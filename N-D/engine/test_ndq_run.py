"""Plumbing test for tools/ndq_run.py with a stub `claude` (no model, no usage).
The stub records its arguments, reads the MCP config the runner wrote, starts that server, makes one real tool call, and answers.
Run: python3 -I N-D/engine/test_ndq_run.py"""
import json, os, stat, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ND = os.path.join(HERE, "..")
RUN = os.path.join(ND, "tools", "ndq_run.py")
STATE = os.path.join(ND, "ND-3", "per_run", "claude-cli__haiku__run1.state.json")
FIX = tempfile.mkdtemp(prefix="ndq-fixture-")                  # fixtures are built here: raw LoCoMo data is git-ignored
SRC, PROBES = os.path.join(FIX, "source.jsonl"), os.path.join(FIX, "probes.jsonl")
with open(SRC, "w") as f:
    for i, (who, text) in enumerate([("Sam", "Hey Evan, what is new?"), ("Evan", "I just got back from a trip in my new Prius."),
                                     ("Sam", "Nice! Where did you go?"), ("Evan", "We drove to the Rockies for a hike.")]):
        f.write(json.dumps({"sentence_id": f"t{i}", "dia_id": f"D1:{i + 1}", "speaker": who, "listener": "x", "date": "1:47 pm on 18 May, 2023", "text": text}) + "\n")
with open(PROBES, "w") as f:
    for i in range(3):
        f.write(json.dumps({"id": f"q0{i}", "category": 1, "question": f"What did Evan do with his Prius ({i})?", "evidence": [], "gold_answer": None}) + "\n")

STUB = r'''#!/usr/bin/env python3
import json, os, subprocess, sys
argv = sys.argv[1:]
open(os.environ["STUB_ARGS"], "a").write(json.dumps(argv) + "\n")
if os.environ.get("STUB_FAIL"):
    sys.exit(1)
prompt = sys.stdin.read()
cfg = json.load(open(argv[argv.index("--mcp-config") + 1]))
(name, spec), = cfg["mcpServers"].items()
p = subprocess.Popen([spec["command"], "-I", *spec["args"]] if False else [spec["command"], *spec["args"]], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                     text=True, env=dict(os.environ, **spec["env"]))
def rpc(i, m, params=None):
    p.stdin.write(json.dumps({"jsonrpc": "2.0", "id": i, "method": m, "params": params or {}}) + "\n"); p.stdin.flush(); return json.loads(p.stdout.readline())
rpc(1, "initialize")
tool = rpc(2, "tools/list")["result"]["tools"][0]["name"]
args = {"query": "Prius"} if tool == "search_turns" else {"status": "intent"}
rpc(3, "tools/call", {"name": "count" if tool != "search_turns" else tool, "arguments": args})
p.stdin.close(); p.wait()
print(json.dumps({"result": "stub answer for: " + prompt.strip().splitlines()[-1][:60], "num_turns": 3, "total_cost_usd": 0.01}))
'''


class Runner(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        stub = os.path.join(self.d, "claude")
        open(stub, "w").write(STUB); os.chmod(stub, os.stat(stub).st_mode | stat.S_IEXEC)
        self.env = dict(os.environ, PATH=self.d + os.pathsep + os.environ["PATH"], STUB_ARGS=os.path.join(self.d, "args.jsonl"))
        self.out = os.path.join(self.d, "out")

    def go(self, *extra, env=None):
        return subprocess.run([sys.executable, "-I", RUN, "--probes", PROBES, "--out", self.out, *extra],
                              capture_output=True, text=True, env=env or self.env)

    def test_tools_arm(self):
        r = self.go("--arm", "tools", "--state", STATE, "--ids", "q00,q01")
        self.assertEqual(r.returncode, 0, r.stderr)
        ans = json.load(open(os.path.join(self.out, "tools.answers.json"))); meta = json.load(open(os.path.join(self.out, "tools.meta.json")))
        self.assertEqual(sorted(ans), ["q00", "q01"]); self.assertTrue(ans["q00"].startswith("stub answer"))
        self.assertEqual(meta["q00"]["calls"], 1); self.assertGreater(meta["q00"]["words_returned"], 0); self.assertEqual(meta["q00"]["call_errors"], 0)
        argv = json.loads(open(self.env["STUB_ARGS"]).readline())
        for flag in ("--strict-mcp-config", "--mcp-config", "--allowedTools", "--no-session-persistence"):
            self.assertIn(flag, argv)
        self.assertEqual(argv[argv.index("--tools") + 1], "")                       # built-in tools off
        self.assertEqual(argv[argv.index("--max-turns") + 1], "12")
        self.assertEqual(sorted(a for a in argv if a.startswith("mcp__ndm__")), sorted(f"mcp__ndm__{t}" for t in
                         ["find_entity", "trajectory", "event", "co_occurring", "filter_events", "count", "ambiguities"]))
        trace = [json.loads(l) for l in open(os.path.join(self.out, "tools.traces", "q00.jsonl"))]
        self.assertEqual(trace[0]["tool"], "count")

    def test_ragtool_arm(self):
        r = self.go("--arm", "ragtool", "--source", SRC, "--ids", "q00")
        self.assertEqual(r.returncode, 0, r.stderr)
        meta = json.load(open(os.path.join(self.out, "ragtool.meta.json")))["q00"]
        self.assertEqual(meta["calls"], 1); self.assertGreater(meta["words_returned"], 5)
        argv = json.loads(open(self.env["STUB_ARGS"]).readline())
        self.assertIn("mcp__rag__search_turns", argv)

    def test_stop_and_resume(self):
        r = self.go("--arm", "tools", "--state", STATE, "--ids", "q00,q01,q02", env=dict(self.env, STUB_FAIL="1"))
        self.assertEqual(r.returncode, 1); self.assertIn("STOPPED", r.stderr)
        self.assertFalse(os.path.exists(os.path.join(self.out, "tools.answers.json")))          # nothing half-saved
        self.assertEqual(self.go("--arm", "tools", "--state", STATE, "--ids", "q00,q01,q02").returncode, 0)
        r = self.go("--arm", "tools", "--state", STATE, "--ids", "q00,q01,q02")                  # a rerun answers nothing new
        self.assertIn("3/3 already answered", r.stdout)
        self.assertEqual(len(open(self.env["STUB_ARGS"]).readlines()), 4)                      # 1 failed + 3 answered, none repeated


if __name__ == "__main__":
    unittest.main(verbosity=2)
