"""Contract tests for ndq2_tools.py, ndq2_mcp.py and tools/ndq2_run.py (stub claude, no model, no usage).
Run: python3 -I N-D/engine/test_ndq2.py"""
import datetime as dt, json, os, stat, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ndq2_tools as T  # noqa: E402
import ndq2_mcp as M    # noqa: E402

RUN = os.path.join(HERE, "..", "tools", "ndq2_run.py")
MCP = os.path.join(HERE, "ndq2_mcp.py")
D = dt.date(2023, 5, 18)                                        # a Thursday


def slot(v, link=None):
    return {"value": v, "link": link}


TURNS = [  # (speaker, listener, date text, sentence, Entities, relations)
    ("Sam", "Evan", "1:47 pm on 18 May, 2023", "Hey Evan, how was your weekend?", [], []),
    ("Evan", "Sam", "1:48 pm on 18 May, 2023", "Last weekend I went hiking in the Rockies.", ["Rockies"],
     [{"type": "hike", "slots": {"agent": slot("I", "I"), "place": slot("the Rockies", "Rockies"), "when": slot("Last weekend")}}]),
    ("Sam", "Evan", "1:49 pm on 18 May, 2023", "You should bring a camera next time.", [],
     [{"type": "advice", "slots": {"giver": slot("I", "I"), "receiver": slot("You", "you"), "content": slot("bring a camera")}}]),
    ("Evan", "Sam", "2:00 pm on 20 May, 2023", "I bought a new Prius yesterday.", ["Prius"],
     [{"type": "purchase", "slots": {"buyer": slot("I", "I"), "item": slot("a new Prius", "Prius"), "when": slot("yesterday")}}]),
    ("Sam", "Evan", "2:01 pm on 20 May, 2023", "Congrats! Cars are expensive these days.", [], []),
    ("Evan", "Sam", "3:00 pm on 3 June, 2023", "We hike again soon, maybe in the Rockies, and I will paint it.", ["Rockies"],
     [{"type": "hike", "slots": {"agent": slot("We"), "place": slot("the Rockies", "Rockies"), "when": slot("soon")}},
      {"type": "paint", "slots": {"agent": slot("I", "I"), "object": slot("it")}}]),
    ("Sam", "Evan", "3:01 pm on 3 June, 2023", "Hiking sounds fun, I hiked there in 2019.", ["Rockies"],
     [{"type": "hike", "slots": {"agent": slot("I", "I"), "when": slot("2019")}}]),
]


def fixture():
    src, rows = [], []
    for i, (spk, lis, date, text, ents, rels) in enumerate(TURNS):
        src.append({"sentence_id": f"t{i}", "dia_id": f"D1:{i + 1}", "speaker": spk, "listener": lis, "date": date, "text": text})
        rows.append({"event_id": f"t{i}", "Entities": ents, "relations": rels})
    return rows, src


FIX = tempfile.mkdtemp(prefix="ndq2-fixture-")
ROWS, SRC = fixture()
EXT_P, SRC_P, PROBES_P = (os.path.join(FIX, n) for n in ("ext.jsonl", "source.jsonl", "probes.jsonl"))
for path, data in ((EXT_P, ROWS), (SRC_P, SRC), (PROBES_P, [{"id": f"q0{i}", "category": 1, "question": f"Where did Evan hike ({i})?"} for i in range(3)])):
    with open(path, "w") as f:
        f.writelines(json.dumps(x) + "\n" for x in data)


class Cues(unittest.TestCase):
    def r(self, text, d=D):
        x = T.resolve_cue(text, d)
        return x if isinstance(x, str) or x is None else tuple(a.isoformat() for a in x)

    def test_days(self):
        self.assertEqual(self.r("yesterday"), ("2023-05-17",) * 2)
        self.assertEqual(self.r("Tomorrow."), ("2023-05-19",) * 2)
        self.assertEqual(self.r("tonight"), ("2023-05-18",) * 2)

    def test_weeks_run_monday_to_sunday(self):
        self.assertEqual(self.r("last week"), ("2023-05-08", "2023-05-14"))
        self.assertEqual(self.r("next week"), ("2023-05-22", "2023-05-28"))
        self.assertEqual(self.r("last weekend"), ("2023-05-13", "2023-05-14"))
        self.assertEqual(self.r("next weekend"), ("2023-05-27", "2023-05-28"))
        self.assertEqual(self.r("last weekend", dt.date(2023, 5, 21)), ("2023-05-13", "2023-05-14"))   # a Sunday: week of the 15th

    def test_months_years(self):
        self.assertEqual(self.r("last month"), ("2023-04-01", "2023-04-30"))
        self.assertEqual(self.r("next month", dt.date(2023, 12, 5)), ("2024-01-01", "2024-01-31"))
        self.assertEqual(self.r("last year"), ("2022-01-01", "2022-12-31"))
        self.assertEqual(self.r("in March"), ("2023-03-01", "2023-03-31"))
        self.assertEqual(self.r("November"), ("2022-11-01", "2022-11-30"))      # later than d: the year before
        self.assertEqual(self.r("February 2021"), ("2021-02-01", "2021-02-28"))
        self.assertEqual(self.r("2019"), ("2019-01-01", "2019-12-31"))

    def test_last_weekday_and_ago(self):
        self.assertEqual(self.r("last Thursday"), ("2023-05-11",) * 2)           # same weekday: a week back, never today
        self.assertEqual(self.r("last Monday"), ("2023-05-15",) * 2)
        self.assertEqual(self.r("3 days ago"), ("2023-05-15",) * 2)
        self.assertEqual(self.r("two weeks ago"), ("2023-05-04",) * 2)
        self.assertEqual(self.r("2 months ago"), ("2023-03-01", "2023-03-31"))
        self.assertEqual(self.r("5 years ago"), ("2018-01-01", "2018-12-31"))

    def test_vague_and_unknown(self):
        for t in ("soon", "recently", "a few days ago", "a couple of weeks ago", "a while back"):
            self.assertEqual(self.r(t), "vague", t)
        for t in ("the Rockies", "bring a camera", "", "every Friday", "on my birthday"):
            self.assertIsNone(self.r(t), t)

    def test_bad_inputs(self):
        self.assertEqual(T._bound("2023-02", True).isoformat(), "2023-02-28")
        self.assertEqual(T._bound("2024-02", True).isoformat(), "2024-02-29")
        for bad in ("2023", "May 2023", "2023-13", "2023-02-30"):
            with self.assertRaises(ValueError):
                T._bound(bad, False)


class Tools(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = T.Memory(ROWS, SRC)

    def ids(self, text):
        return [w.strip("[]") for w in text.replace("|", " ").split() if w.startswith("[t")]

    def test_join_i_and_you(self):
        t = self.m.find(entity="Evan")
        self.assertEqual(self.ids(t), ["t1", "t2", "t3", "t5"])                     # t2: "you" is Evan (the listener); t6: "I" is Sam
        self.assertEqual(self.ids(self.m.find(entity="Sam")), ["t2", "t6"])         # t2: "I" is Sam, t6: "I" is Sam
        self.assertNotIn("t6", t)                                                   # t6: "I" is Sam
        self.assertIn("I (Evan)", self.m.event("t1")); self.assertIn("You (Evan)", self.m.event("t2"))
        self.assertEqual(self.m.event("t1").count("Sam"), 1)                        # only in the arrow

    def test_rows_not_rewritten(self):
        self.assertEqual(ROWS[1]["relations"][0]["slots"]["agent"], slot("I", "I"))

    def test_find_filters(self):
        self.assertEqual(self.ids(self.m.find(types=["hike"])), ["t1", "t5", "t6"])
        self.assertEqual(self.ids(self.m.find(types=["HIKE", "purchase"])), ["t1", "t3", "t5", "t6"])
        self.assertEqual(self.ids(self.m.find(types=["hike"], entity="Sam")), ["t6"])
        self.assertEqual(self.ids(self.m.find(role="item")), ["t3"])
        self.assertEqual(self.ids(self.m.find(speaker="sam", types=["hike"])), ["t6"])
        self.assertEqual(self.ids(self.m.find(value="hiking Rockies")), ["t1", "t5"])      # hike/hiking share a stem; every word is needed (t6 has no Rockies)
        self.assertEqual(self.ids(self.m.find(value="hikes")), ["t1", "t5", "t6"])   # "hike", "hiking", "hiked" share a stem; t5 is "hike"
        self.assertIn("0 events match", self.m.find(entity="Nobody"))

    def test_time_filter_uses_resolved_range(self):
        # t1 is said 18 May and means 13-14 May; t3 is said 20 May and means 19 May
        self.assertEqual(self.ids(self.m.find(frm="2023-05-13", to="2023-05-14")), ["t1"])
        self.assertEqual(self.ids(self.m.find(frm="2023-05-19", to="2023-05-19")), ["t3"])
        self.assertEqual(self.ids(self.m.find(frm="2023-05", to="2023-05")), ["t0", "t1", "t2", "t3", "t4"])
        self.assertEqual(self.ids(self.m.find(frm="2023-06")), ["t5"])                  # t6 says 2019: its meaning is not June 2023
        self.assertEqual(self.ids(self.m.find(to="2019-12-31")), ["t6"])             # "2019" resolved: meaning, not the day said
        self.assertIn("t5", self.m.find(frm="2023-06", to="2023-06"))                # vague cue: falls back to the day said

    def test_cue_display(self):
        self.assertIn("when=Last weekend -> 2023-05-13..2023-05-14", self.m.event("t1"))
        self.assertIn("when=yesterday -> 2023-05-19", self.m.event("t3"))
        self.assertIn("when=soon -> vague, said 2023-06-03", self.m.event("t5"))

    def test_find_needs_a_filter_and_pages(self):
        with self.assertRaises(ValueError):
            self.m.find()
        with self.assertRaises(ValueError):
            self.m.find(types=["hike"], offset=-1)
        with self.assertRaises(ValueError):
            self.m.find(frm="May 2023")
        with self.assertRaises(ValueError):
            self.m.find(value="!!")
        t = self.m.find(types=["hike"], offset=2)
        self.assertEqual(self.ids(t), ["t6"]); self.assertIn("showing 3-3", t); self.assertNotIn("more", t)
        self.assertIn("past the last match", self.m.find(types=["hike"], offset=9))

    def test_count(self):
        t = self.m.count(types=["hike"])
        self.assertTrue(t.startswith("3 events;")); self.assertIn("t1, t5, t6", t)
        self.assertIn("distinct entities", t)
        self.assertIn("by speaker: Evan 2, Sam 1", self.m.count(types=["hike"], by="speaker"))
        self.assertIn("by month: 2023-06 2, 2023-05 1", self.m.count(types=["hike"], by="month"))
        self.assertIn("by type: hike 3", self.m.count(types=["hike"], by="type"))
        with self.assertRaises(ValueError):
            self.m.count(types=["hike"], by="colour")
        with self.assertRaises(ValueError):
            self.m.count()

    def test_count_entities_exclude_speakers(self):
        t = self.m.count(types=["hike"])
        self.assertIn("1 distinct entities", t)                                      # only Rockies; Evan and Sam are hubs

    def test_values(self):
        t = self.m.values("Rockies", "when")
        self.assertIn("hike.when:", t); self.assertIn("Last weekend [t1]", t); self.assertIn("soon [t5]", t)
        self.assertIn("I (Evan) [t1]", self.m.values("Rockies", "agent"))
        self.assertNotIn("the Rockies", self.m.values("Rockies", "place"))           # the entity is not its own value
        self.assertTrue(self.m.values("Nothing").startswith("No relation links"))
        with self.assertRaises(ValueError):
            self.m.values("  ")

    def test_event_and_neighbors(self):
        self.assertTrue(self.m.event("zzz").startswith("No event"))
        t = self.m.neighbors("t3", 1)
        self.assertEqual(self.ids(t), ["t2", "t3", "t4"])
        lines = t.splitlines()
        self.assertTrue(lines[2].startswith("> ") and "purchase(" in lines[2])       # center in full
        self.assertNotIn("advice(", t)                                              # others sentence only
        self.assertEqual(self.ids(self.m.neighbors("t0", 3)), ["t0", "t1", "t2", "t3"])
        with self.assertRaises(ValueError):
            self.m.neighbors("t3", 4)
        with self.assertRaises(ValueError):
            self.m.neighbors("t3", 0)

    def test_catalog(self):
        t = self.m.catalog()
        for s in ("7 events", "2023-05-18 to 2023-06-03", "hike (3)", "once each:", "most linked entities:", "Evan and Sam"):
            self.assertIn(s, t)
        self.assertLessEqual(len(t.split()), T.CATALOG_CAP)

    def test_caps(self):
        words = " ".join(["alpha"] * 40)
        rows, src = [], []
        for i in range(30):
            src.append({"sentence_id": f"t{i}", "dia_id": f"D1:{i}", "speaker": "A", "listener": "B", "date": "1:00 pm on 1 May, 2023", "text": f"{words} {i}"})
            rows.append({"event_id": f"t{i}", "Entities": [], "relations": [{"type": "talk", "slots": {"x": slot("v")}}]})
        m = T.Memory(rows, src)
        t = m.find(types=["talk"])
        self.assertLessEqual(len(t.split()), T.CAP)
        n = len(self.ids(t))
        self.assertIn(f"showing 1-{n}", t); self.assertIn(f"offset={n})", t); self.assertLess(n, T.PAGE)   # the header and the offset say what was shown
        self.assertTrue(t.startswith("30 events match"))                              # the count is exact even when the page is cut
        seen, off = [], 0
        while off < 30:                                                               # following the offsets visits every event once, in order
            page = m.find(types=["talk"], offset=off); got = self.ids(page); self.assertTrue(got); seen += got; off += len(got)
        self.assertEqual(seen, [f"t{i}" for i in range(30)])
        one = T.Memory([{**rows[0]}], [{**src[0], "text": " ".join(["w"] * 400)}]).find(types=["talk"])
        self.assertLessEqual(len(one.split()), T.CAP); self.assertIn("truncated", one); self.assertIn("showing 1-1", one)
        self.assertLessEqual(len(m.neighbors("t10", 3).split()), T.CAP)
        self.assertLessEqual(len(T.TurnIndex(m).search("alpha").split()), T.CAP)
        big = T._cap("h", [" ".join(["w"] * 400)], 250)
        self.assertLessEqual(len(big.split()), 250); self.assertIn("truncated", big)

    def test_search_turns(self):
        idx = T.TurnIndex(self.m)
        t = idx.search("Where did Evan buy the Prius?")
        self.assertIn("t3", self.ids(t))
        self.assertNotIn("purchase(", t)                                            # turns only, no relations
        self.assertEqual(idx.search("zebra"), "No turns match.")
        self.assertLessEqual(len(self.ids(idx.search("hike hiking Rockies Evan"))), T.TOP_BM25)
        order = self.ids(idx.search("hike Rockies"))
        self.assertEqual(order, sorted(order, key=lambda s: int(s[1:])))            # time order
        with self.assertRaises(ValueError):
            idx.search("  ")


class Server(unittest.TestCase):
    def session(self, arm, calls):
        p = subprocess.Popen([sys.executable, "-I", MCP, EXT_P, SRC_P, arm], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        out = []
        for i, (method, params) in enumerate([("initialize", {}), ("tools/list", {})] + calls, 1):
            p.stdin.write(json.dumps({"jsonrpc": "2.0", "id": i, "method": method, "params": params}) + "\n"); p.stdin.flush()
            out.append(json.loads(p.stdout.readline()))
        p.stdin.close(); p.wait(timeout=10); p.stdout.close()
        return out

    def test_tool_lists_per_arm(self):
        want = {"struct": ["catalog", "find", "count", "values", "event", "neighbors"],
                "tools2": ["catalog", "find", "count", "values", "event", "neighbors", "search_turns"], "ragtool2": ["search_turns"]}
        for arm, names in want.items():
            tools = self.session(arm, [])[1]["result"]["tools"]
            self.assertEqual([t["name"] for t in tools], names, arm)
            for t in tools:
                self.assertEqual(t["inputSchema"]["type"], "object"); self.assertFalse(t["inputSchema"]["additionalProperties"])

    def test_calls_and_errors_are_text_not_crashes(self):
        c = lambda n, a: ("tools/call", {"name": n, "arguments": a})
        r = self.session("tools2", [c("find", {"types": ["hike"]}), c("find", {}), c("find", {"bogus": 1}), c("values", {}), c("count", {"types": ["hike"], "by": "x"}),
                                     c("neighbors", {"id": "t1", "k": "many"}), c("search_turns", {"query": "Prius"}), c("nope", {}), c("find", {"from": "May"}),
                                     ("bogus/method", {}), ("ping", {})])
        res = [x.get("result") for x in r[2:]]
        self.assertFalse(res[0]["isError"]); self.assertIn("3 events match", res[0]["content"][0]["text"])
        for i in range(1, 6):
            self.assertTrue(res[i]["isError"], i); self.assertTrue(res[i]["content"][0]["text"].startswith("Error"), res[i])
        self.assertFalse(res[6]["isError"]); self.assertIn("t3", res[6]["content"][0]["text"])
        self.assertTrue(res[7]["isError"]); self.assertIn("unknown tool", res[7]["content"][0]["text"])
        self.assertTrue(res[8]["isError"])
        self.assertEqual(r[-2]["error"]["code"], -32601); self.assertEqual(r[-1]["result"], {})

    def test_arm_restricts_tools(self):
        r = self.session("ragtool2", [("tools/call", {"name": "find", "arguments": {"types": ["hike"]}})])
        self.assertTrue(r[2]["result"]["isError"])
        r = self.session("struct", [("tools/call", {"name": "search_turns", "arguments": {"query": "Prius"}})])
        self.assertTrue(r[2]["result"]["isError"])

    def test_call_limit_is_enforced_by_the_server(self):
        c = ("tools/call", {"name": "find", "arguments": {"types": ["hike"]}})
        r = self.session("tools2", [c] * 12)
        res = [x["result"] for x in r[2:]]
        self.assertFalse(any(x["isError"] for x in res[:10]))
        for x in res[10:]:
            self.assertTrue(x["isError"]); self.assertIn("limit of 10", x["content"][0]["text"])

    def test_event_not_found_is_flagged_but_no_matches_is_data(self):
        r = self.session("struct", [("tools/call", {"name": "event", "arguments": {"id": "t99"}}), ("tools/call", {"name": "find", "arguments": {"entity": "Zed"}})])
        self.assertTrue(r[2]["result"]["isError"]); self.assertFalse(r[3]["result"]["isError"])


STUB = r'''#!/usr/bin/env python3
import json, os, subprocess, sys
argv = sys.argv[1:]
open(os.environ["STUB_ARGS"], "a").write(json.dumps(argv) + "\n")
if os.environ.get("STUB_FAIL"):
    sys.exit(1)
prompt = sys.stdin.read()
open(os.environ["STUB_ARGS"] + ".prompt", "a").write(prompt + "\n=====\n")
cfg = json.load(open(argv[argv.index("--mcp-config") + 1]))
(name, spec), = cfg["mcpServers"].items()
p = subprocess.Popen([spec["command"], *spec["args"]], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, env=dict(os.environ, **spec["env"]))
def rpc(i, m, params=None):
    p.stdin.write(json.dumps({"jsonrpc": "2.0", "id": i, "method": m, "params": params or {}}) + "\n"); p.stdin.flush(); return json.loads(p.stdout.readline())
rpc(1, "initialize")
tools = [t["name"] for t in rpc(2, "tools/list")["result"]["tools"]]
rpc(3, "tools/call", {"name": "search_turns", "arguments": {"query": "Prius"}} if tools == ["search_turns"] else {"name": "find", "arguments": {"types": ["hike"]}})
p.stdin.close(); p.wait()
print(json.dumps({"result": "stub answer", "num_turns": 3, "total_cost_usd": 0.01}))
'''


class Runner(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        stub = os.path.join(self.d, "claude")
        open(stub, "w").write(STUB); os.chmod(stub, os.stat(stub).st_mode | stat.S_IEXEC)
        self.env = dict(os.environ, PATH=self.d + os.pathsep + os.environ["PATH"], STUB_ARGS=os.path.join(self.d, "args.jsonl"))
        self.out = os.path.join(self.d, "out")

    def go(self, arm, *extra, env=None):
        return subprocess.run([sys.executable, "-I", RUN, "--arm", arm, "--extraction", EXT_P, "--source", SRC_P, "--probes", PROBES_P, "--out", self.out, *extra],
                              capture_output=True, text=True, env=env or self.env)

    def test_arms_flags_and_prompts(self):
        want = {"struct": ["catalog", "find", "count", "values", "event", "neighbors"], "tools2": ["catalog", "find", "count", "values", "event", "neighbors", "search_turns"],
                "ragtool2": ["search_turns"]}
        for arm, names in want.items():
            r = self.go(arm, "--ids", "q00")
            self.assertEqual(r.returncode, 0, r.stderr)
            meta = json.load(open(os.path.join(self.out, f"{arm}.meta.json")))["q00"]
            self.assertEqual(meta["calls"], 1); self.assertGreater(meta["words_returned"], 3); self.assertEqual(meta["call_errors"], 0)
            argv = json.loads(open(self.env["STUB_ARGS"]).readlines()[-1])
            self.assertEqual(sorted(a for a in argv if a.startswith("mcp__")), sorted(f"mcp__ndq2__{n}" for n in names), arm)
            self.assertEqual(argv[argv.index("--tools") + 1], "")
            for flag in ("--strict-mcp-config", "--no-session-persistence"):
                self.assertIn(flag, argv)
            self.assertEqual(argv[argv.index("--max-turns") + 1], "12")
        prompts = open(self.env["STUB_ARGS"] + ".prompt").read().split("=====\n")
        self.assertIn("catalog", prompts[0]); self.assertNotIn("search_turns", prompts[0])          # struct
        self.assertIn("search_turns", prompts[1]); self.assertIn("catalog", prompts[1])              # tools2
        self.assertNotIn("catalog", prompts[2]); self.assertIn("at most 10 searches", prompts[2])    # ragtool2
        for p in prompts[:3]:
            self.assertIn("Sam", p); self.assertIn("2023-05-18 to 2023-06-03", p); self.assertIn("Where did Evan hike (0)?", p)

    def test_stop_and_resume(self):
        r = self.go("tools2", "--ids", "q00,q01,q02", env=dict(self.env, STUB_FAIL="1"))
        self.assertEqual(r.returncode, 1); self.assertIn("STOPPED", r.stderr)
        self.assertFalse(os.path.exists(os.path.join(self.out, "tools2.answers.json")))
        self.assertEqual(self.go("tools2", "--ids", "q00,q01,q02").returncode, 0)
        self.assertIn("3/3 already answered", self.go("tools2", "--ids", "q00,q01,q02").stdout)
        self.assertEqual(len(open(self.env["STUB_ARGS"]).readlines()), 4)


sys.path.insert(0, os.path.join(HERE, "..", "tools"))
import ndq2_score as S  # noqa: E402


class Blind(unittest.TestCase):
    probes = [{"id": f"q0{i}", "category": 1 + i % 2, "question": f"Q{i}?", "gold_answer": f"g{i}", "evidence": [f"D1:{i + 2}"]} for i in range(4)]
    answers = {a: {f"q0{i}": f"{a}-answer-{i}" for i in range(4)} for a in ("RAW", "RAGTOOL", "STRUCT", "TOOLS2")}

    def test_sheet_hides_arms_and_is_reproducible(self):
        md, key, tmpl = S.build_sheet(self.probes, self.answers, 5)
        for q, order in key.items():
            self.assertEqual(sorted(order), sorted(self.answers))
        self.assertEqual(len(tmpl), 16); self.assertEqual(S.build_sheet(self.probes, self.answers, 5)[1], key)
        self.assertNotEqual(S.build_sheet(self.probes, self.answers, 6)[1], key)
        self.assertGreater(len({tuple(o) for o in key.values()}), 1)                    # order varies per question
        first = key["q00"][0]
        self.assertIn(f"- A: {first}-answer-0", md)                                      # label A is the first arm of the key
        self.assertFalse([l for l in md.splitlines() if not l.startswith("- ") and any(a.lower() in l.lower() for a in self.answers)])    # only answer lines carry text from the arms
        self.assertEqual(md.count("- A:"), 4); self.assertIn("Gold: g0", md)

    def test_missing_answer_refused(self):
        a = {k: dict(v) for k, v in self.answers.items()}; del a["TOOLS2"]["q03"]
        with self.assertRaises(ValueError):
            S.build_sheet(self.probes, a, 5)

    def test_key_applied_and_scores_validated(self):
        key = {"q00": ["TOOLS2", "RAW", "STRUCT", "RAGTOOL"]}
        res = S.apply_key({"q00A": "C", "q00B": "P", "q00C": "W", "q00D": "C"}, key)
        self.assertEqual((res["TOOLS2"]["q00"], res["RAW"]["q00"], res["STRUCT"]["q00"], res["RAGTOOL"]["q00"]), (1.0, 0.5, 0.0, 1.0))
        for bad in ({"q00A": "C", "q00B": "P", "q00C": "W"}, {"q00A": "C", "q00B": "P", "q00C": "W", "q00D": "X"}, {"q00A": "C", "q00B": "P", "q00C": "W", "q00D": ""}):
            with self.assertRaises(ValueError):
                S.apply_key(bad, key)

    def test_decision_rule(self):
        base = {"RAW": 30.0, "RAGTOOL": 28.0, "STRUCT": 25.0, "TOOLS2": 30.0}
        med = {"TOOLS2": (6, 900)}
        self.assertTrue(S.decide(base, {"TOOLS2": .8}, med)["pass"])
        self.assertFalse(S.decide({**base, "TOOLS2": 29.5}, {}, med)["R1"])                # boundary: 30 passes, 29.5 fails
        self.assertTrue(S.decide({**base, "TOOLS2": 30.0}, {}, med)["R1"])
        self.assertFalse(S.decide({**base, "RAW": 34.0, "TOOLS2": 30.0}, {}, med)["R2"])   # 30 < 30.6
        self.assertTrue(S.decide({**base, "RAW": 33.0, "TOOLS2": 29.7}, {}, med)["R2"])    # exactly 90%
        self.assertFalse(S.decide(base, {"TOOLS2": .79}, med)["R3"]); self.assertFalse(S.decide(base, {}, {"TOOLS2": (11, 900)})["R5"])
        self.assertFalse(S.decide(base, {}, {"TOOLS2": (6, 1501)})["R5"])
        self.assertFalse(S.decide({**base, "TOOLS2": 28.0}, {}, med)["pass"])

    def test_recall_from_traces(self):
        d = tempfile.mkdtemp()
        with open(os.path.join(d, "q00.jsonl"), "w") as f:
            f.write(json.dumps({"text": "[t0 | x] a\n[t12 | y] b"}) + "\n")
        with open(os.path.join(d, "q01.jsonl"), "w") as f:
            f.write(json.dumps({"text": "[t4 | x] only, in part1 of the plan"}) + "\n")
        src = [{"dia_id": f"D1:{i + 1}", "sentence_id": f"t{i}"} for i in range(8)]
        rows = S.recall([{"id": "q00", "evidence": ["D1:1", "D1:2"]}, {"id": "q01", "evidence": ["D1:5", "D1:2"]}, {"id": "q02", "evidence": ["D1:3"]}], src, d)
        self.assertEqual(rows, [("q00", 1, 2), ("q01", 1, 2), ("q02", 0, 1)])           # t12 is not t1: ids match whole


class Exclude(unittest.TestCase):
    def test_disjoint_draw(self):
        chunk = os.path.join(HERE, "..", "tools", "locomo_chunk.py")
        data = os.environ.get("LOCOMO_JSON", "/tmp/locomo10.json")
        if not os.path.exists(data):
            self.skipTest("locomo10.json not available")
        d = tempfile.mkdtemp()
        run = lambda *x: subprocess.run([sys.executable, "-I", chunk, "--locomo", data, "--sample", "8", "--sessions", "all", *x], capture_output=True, text=True)
        self.assertEqual(run("--probe-sample", "40", "--seed", "11", "--out-dir", d + "/a").returncode, 0)
        a = [json.loads(l) for l in open(d + "/a/probes.jsonl")]
        self.assertEqual(run("--probe-sample", "40", "--seed", "11", "--exclude", d + "/a/probes.jsonl", "--out-dir", d + "/b").returncode, 0)
        b = [json.loads(l) for l in open(d + "/b/probes.jsonl")]
        self.assertEqual(len(b), 40); self.assertFalse({p["locomo_index"] for p in a} & {p["locomo_index"] for p in b})
        self.assertEqual(json.load(open(d + "/b/chunk_meta.json"))["excluded"], 40)
        self.assertEqual([p["id"] for p in b], [f"q{i:02d}" for i in range(40)])


if __name__ == "__main__":
    unittest.main(verbosity=2)
