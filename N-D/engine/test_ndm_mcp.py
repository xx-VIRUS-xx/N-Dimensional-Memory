"""Protocol tests for the ND-Q MCP server: scripted JSON-RPC client over a subprocess, no dependencies.
Run: python3 -I N-D/engine/test_ndm_mcp.py"""
import json, os, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "..", "ND-3", "per_run", "claude-cli__haiku__run1.state.json")
sys.path.insert(0, HERE)
from ndm_tools import load  # noqa: E402

M = load(STATE)


class Client:
    def __init__(self, trace=None):
        env = dict(os.environ, **({"NDQ_TRACE": trace} if trace else {}))
        self.p = subprocess.Popen([sys.executable, "-I", os.path.join(HERE, "ndm_mcp.py"), STATE], stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE, text=True, env=env)
        self.n = 0

    def rpc(self, method, params=None):
        self.n += 1
        self.p.stdin.write(json.dumps({"jsonrpc": "2.0", "id": self.n, "method": method, "params": params or {}}) + "\n")
        self.p.stdin.flush()
        return json.loads(self.p.stdout.readline())

    def notify(self, method):
        self.p.stdin.write(json.dumps({"jsonrpc": "2.0", "method": method}) + "\n"); self.p.stdin.flush()

    def close(self):
        self.p.stdin.close(); self.p.wait(timeout=10)


class Protocol(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mktemp(suffix=".jsonl")
        self.c = Client(self.tmp)
        self.init = self.c.rpc("initialize", {"protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "t", "version": "0"}})
        self.c.notify("notifications/initialized")

    def tearDown(self):
        self.c.close()
        if os.path.exists(self.tmp): os.remove(self.tmp)

    def test_initialize(self):
        r = self.init["result"]
        self.assertEqual(r["protocolVersion"], "2025-03-26"); self.assertIn("tools", r["capabilities"]); self.assertEqual(r["serverInfo"]["name"], "ndm")

    def test_tools_list_matches_spec(self):
        tools = {t["name"]: t for t in self.c.rpc("tools/list")["result"]["tools"]}
        self.assertEqual(set(tools), {"find_entity", "trajectory", "event", "co_occurring", "filter_events", "count", "find_value", "ambiguities"})
        for t in tools.values():
            self.assertEqual(t["inputSchema"]["type"], "object"); self.assertTrue(t["description"])
        self.assertIn("from", tools["count"]["inputSchema"]["properties"])
        self.assertIn("entity", tools["filter_events"]["inputSchema"]["properties"])

    def test_call_equals_direct_function(self):
        for name, args, direct in [("find_entity", {"name": "Prius"}, M.find_entity("Prius")),
                                   ("event", {"tick": 1}, M.event(1)),
                                   ("count", {"status": "open_question", "from": "2023-05", "to": "2023-12"}, M.count(status="open_question", frm="2023-05", to="2023-12")),
                                   ("co_occurring", {"entity_a": "trip"}, M.co_occurring("trip")),
                                   ("find_value", {"word": "hike", "from": "2023-05"}, M.find_value("hike", frm="2023-05")),
                                   ("ambiguities", {"entity": "it"}, M.ambiguities("it"))]:
            r = self.c.rpc("tools/call", {"name": name, "arguments": args})["result"]
            self.assertFalse(r["isError"], name); self.assertEqual(r["content"][0]["text"], direct["text"], name)

    def test_errors_are_results_not_crashes(self):
        cases = [("count", {"from": "May 2023"}, "bad date"), ("nope", {}, "unknown tool"), ("event", {}, "needs ['tick']"),
                 ("find_entity", {"name": "x", "extra": 1}, "does not take"), ("event", {"tick": 9999}, "No event 9999"),
                 ("count", {"entity": "zzyzx"}, "No entity")]
        for name, args, want in cases:
            r = self.c.rpc("tools/call", {"name": name, "arguments": args})["result"]
            self.assertIn(want, r["content"][0]["text"], (name, args))
            self.assertTrue(r["isError"], (name, args))
        self.assertEqual(self.c.rpc("ping")["result"], {})                 # still alive after the bad calls
        self.assertIn("error", self.c.rpc("resources/list"))

    def test_nothing_found_is_not_an_error(self):
        for name, args in [("find_entity", {"name": "zzyzx"}), ("find_value", {"word": "zzyzx"})]:
            r = self.c.rpc("tools/call", {"name": name, "arguments": args})["result"]
            self.assertFalse(r["isError"], name)
        self.assertTrue(self.c.rpc("tools/call", {"name": "find_value", "arguments": {"word": ""}})["result"]["isError"])

    def test_trace_file(self):
        self.c.rpc("tools/call", {"name": "find_entity", "arguments": {"name": "Prius"}})
        self.c.rpc("tools/call", {"name": "count", "arguments": {"status": "intent"}})
        rows = [json.loads(l) for l in open(self.tmp)]
        self.assertEqual([r["tool"] for r in rows], ["find_entity", "count"]); self.assertEqual(rows[0]["args"], {"name": "Prius"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
