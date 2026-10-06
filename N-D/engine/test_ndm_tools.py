"""Contract tests for the ND-Q tools (EXP-NDQ.md) on the frozen ND-3 state.

Every expected value is computed here, straight from the raw state JSON, with code that does not use
ndm_tools. Run from N-D/:   python3 -m unittest engine.test_ndm_tools -v   (or run this file directly)
"""
import json, os, re, sys, unittest
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ndm_tools import load, CAP_WORDS  # noqa: E402

STATE = os.path.join(HERE, "..", "ND-3", "per_run", "claude-cli__haiku__run1.state.json")
S = json.load(open(STATE))
M = load(STATE)
HIDDEN = {"role", "role_in_event", "type", "reference_status", "epistemic_source"}
HUBS = {"sam", "evan"}
EV = {e["tick"]: e for e in S["events"]}


def said_in(tick, month_word, year):
    return re.search(rf"\b{month_word},? {year}\b", EV[tick]["occurred_anchor"]) is not None


def words(t):
    return len(t.split())


class FindEntity(unittest.TestCase):
    def test_exact_and_near(self):
        r = M.find_entity("Prius")["data"]
        self.assertIn(("prius", "exact"), [(x["peg"], x["match"]) for x in r])
        self.assertTrue(any(x["peg"] == "Evan's new Prius" and x["match"].startswith("near") for x in r))

    def test_event_count_matches_raw(self):
        ticks = {x["tick"] for x in S["strings"] if x["peg"] == "prius"} | {e["tick"] for e in S["events"] if "prius" in e["participants"]}
        row = [x for x in M.find_entity("prius")["data"] if x["peg"] == "prius"][0]
        self.assertEqual(row["events"], len(ticks))

    def test_unknown(self):
        r = M.find_entity("zzyzx")
        self.assertEqual(r["data"], [])
        self.assertIn("No entity", r["text"])


class Trajectory(unittest.TestCase):
    def test_rockies(self):
        want = sorted({x["tick"] for x in S["strings"] if x["peg"] == "Rockies" and x["dim"] not in HIDDEN})
        self.assertEqual(M.trajectory("Rockies")["data"], want)

    def test_date_window(self):
        want = sorted({x["tick"] for x in S["strings"] if x["peg"] == "Evan" and x["dim"] not in HIDDEN and said_in(x["tick"], "May", 2023)})
        got = M.trajectory("Evan", "2023-05", "2023-05")["data"]
        self.assertEqual(got, want)
        self.assertEqual(got, sorted(got))

    def test_bad_date_is_a_message(self):
        r = M.trajectory("Evan", "May 2023")
        self.assertIsNone(r["data"]); self.assertTrue(r["text"].startswith("Error"))


class Event(unittest.TestCase):
    def test_t1(self):
        r = M.event(1)
        self.assertEqual((r["data"]["speaker"], r["data"]["listener"], r["data"]["day"]), ("Evan", "Sam", "2023-05-18"))
        self.assertIn("Prius", r["text"])

    def test_out_of_range(self):
        for bad in (-1, 509, "x"):
            self.assertIsNone(M.event(bad)["data"]); self.assertIn("No event", M.event(bad)["text"])


class CoOccurring(unittest.TestCase):
    def test_pairs_match_raw(self):
        def ticks_of(name):                       # only pegs whose name is unique under normalisation
            return {x["tick"] for x in S["strings"] if x["peg"] == name} | {e["tick"] for e in S["events"] if name in e["participants"]}
        names = [p for p, _ in Counter(q for e in S["events"] for q in e["participants"] if q.lower() not in HUBS).most_common(6)]
        checked = 0
        for a in names:
            for b in names:
                if a < b and len(M.resolve(a)[0]) == 1 and len(M.resolve(b)[0]) == 1:
                    self.assertEqual(M.co_occurring(a, b)["data"], sorted(ticks_of(a) & ticks_of(b)), (a, b)); checked += 1
        self.assertGreater(checked, 3)

    def test_partners_exclude_hubs_and_count_events(self):
        a = "trip"
        want = Counter(p for e in S["events"] if a in e["participants"] for p in e["participants"] if p != a and p.lower() not in HUBS)
        got = dict(M.co_occurring(a)["data"])
        self.assertEqual(got, dict(want))
        self.assertFalse({"Sam", "Evan"} & set(got))


class FilterAndCount(unittest.TestCase):
    def test_status(self):
        want = sorted({x["tick"] for x in S["strings"] if x["status"] == "open_question"})
        self.assertEqual(M.count(status="open_question")["data"]["events"], want)

    def test_speaker(self):
        self.assertEqual(M.filter_events(speaker="Sam")["data"], [e["tick"] for e in S["events"] if e["source_speaker"] == "Sam"])

    def test_dimension_and_owner(self):
        want = sorted({x["tick"] for x in S["strings"] if x["dim"] == "action" and x["owner"] == "Evan"})
        self.assertEqual(M.count(dimension="action", owner="Evan")["data"]["events"], want)

    def test_month(self):
        want = [e["tick"] for e in S["events"] if said_in(e["tick"], "May", 2023)]
        self.assertEqual(M.count(frm="2023-05", to="2023-05")["data"]["events"], want)
        self.assertGreater(len(want), 0)

    def test_entity_and_status(self):
        want = sorted({x["tick"] for x in S["strings"] if x["peg"] == "Evan" and x["status"] == "intent"})
        self.assertEqual(M.count(entity="Evan", status="intent")["data"]["events"], want)

    def test_distinct_pegs(self):
        want = sorted({x["peg"] for x in S["strings"] if x["dim"] == "action"})
        self.assertEqual(M.count(dimension="action")["data"]["pegs"], want)

    def test_unknown_entity_is_a_message(self):
        self.assertIn("No entity", M.count(entity="zzyzx")["text"])

    def test_filter_total_is_exact_beyond_ten(self):
        r = M.filter_events(status="open_question")
        self.assertTrue(r["text"].startswith(f"{len(r['data'])} matching events"))
        self.assertGreater(len(r["data"]), 10)


class Ambiguities(unittest.TestCase):
    def test_all_unresolved(self):
        want = [b["id"] for b in S["buckets"] if b["state"] != "resolved"]
        self.assertEqual(M.ambiguities()["data"], want)

    def test_entity_filter_it(self):
        want = [b["id"] for b in S["buckets"] if b["state"] != "resolved"
                and (b["peg"].lower() == "it" or any(str(c).lower() == "it" for c in b["candidates"]))]
        got = M.ambiguities("it")["data"]
        self.assertTrue(set(want) <= set(got))                 # near-normalised forms may add a few, never drop one
        self.assertLessEqual(len(got), len(want) + 5)


class Properties(unittest.TestCase):
    def test_word_cap_everywhere(self):
        limit = CAP_WORDS + 10                                  # header plus "(N more)" footer
        texts = []
        for p in S["pegs"]:
            texts += [M.find_entity(p)["text"], M.trajectory(p)["text"], M.co_occurring(p)["text"]]
        texts += [M.event(t)["text"] for t in range(0, 509, 7)] + [M.ambiguities(p)["text"] for p in list(S["pegs"])[:60]]
        texts += [M.count()["text"], M.filter_events()["text"], M.filter_events(speaker="Evan")["text"]]
        over = [t[:60] for t in texts if words(t) > limit]
        self.assertEqual(over, [])

    def test_deterministic(self):
        calls = [lambda: M.find_entity("Prius"), lambda: M.trajectory("Evan", "2023-05", "2023-06"),
                 lambda: M.co_occurring("trip"), lambda: M.count(status="intent"), lambda: M.ambiguities("it"), lambda: M.event(22)]
        for c in calls:
            self.assertEqual(c(), c())

    def test_state_only_no_source_text(self):
        src = open(os.path.join(HERE, "ndm_tools.py")).read()
        self.assertNotIn("source.jsonl", src)
        self.assertFalse(any("text" in e for e in S["events"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
