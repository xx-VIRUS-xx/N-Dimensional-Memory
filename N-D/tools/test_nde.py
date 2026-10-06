"""Tests for the ND-E extractor and report (self-contained fixtures, no model calls).

Run from N-D/:   python3 -m unittest tools.test_nde -v     (or: python3 tools/test_nde.py)
"""
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import extract_events as X  # noqa: E402
import nde_report as R  # noqa: E402

EXAMPLE = {"Entities": ["Bob", "CockroachDB", "multi-region payments", "Alice", "proposal"],
           "EventRelation": [
               {"type": "argument", "arguer": "Bob", "claim_subject": "CockroachDB", "claim": "better", "domain": "multi-region payments"},
               {"type": "acceptance", "acceptor": "Alice", "accepted_object": "proposal"}]}

TURNS = [
    {"sentence_id": "t0", "speaker": "Sam", "listener": "Evan", "date": "1:00 pm on 18 May, 2023", "text": "Hey Evan, how was the trip?"},
    {"sentence_id": "t1", "speaker": "Evan", "listener": "Sam", "date": "1:00 pm on 18 May, 2023", "text": "I got back from a road trip to Jasper last weekend with my family."},
    {"sentence_id": "t2", "speaker": "Sam", "listener": "Evan", "date": "1:01 pm on 18 May, 2023", "text": "That sounds great, I loved it."},
]
RAW = [
    {"Entities": [], "EventRelation": []},
    {"Entities": ["Evan", "Jasper", "family"], "EventRelation": [
        {"type": "trip", "traveler": "Evan", "destination": "Jasper", "companions": "my family", "when": "last weekend"}]},
    {"Entities": ["it"], "EventRelation": [{"type": "state", "subject": "Sam", "state": "loved", "object": "it"}]},
]


class Normalisation(unittest.TestCase):
    def test_snake(self):
        self.assertEqual(X.snake("Claim Subject!"), "claim_subject")
        self.assertEqual(X.snake("  __x--y "), "x_y")

    def test_norm_entity(self):
        self.assertEqual(X.norm_entity("The Prius"), "prius")
        self.assertEqual(X.norm_entity("Evan's new Prius"), "new prius")
        self.assertEqual(X.norm_entity("my family"), "family")
        self.assertEqual(X.norm_entity("snacks"), "snack")
        self.assertEqual(X.norm_entity("glass"), "glass")        # no fold on -ss
        self.assertEqual(X.norm_entity("US"), "us")               # short words are left alone
        self.assertEqual(X.norm_entity("Prius"), "prius")
        self.assertEqual(X.norm_entity("priuses"), "prius")
        self.assertEqual(X.norm_entity("buses"), X.norm_entity("bus"))
        self.assertEqual(X.norm_entity("boxes"), "box")
        self.assertEqual(X.norm_entity("cookies"), "cookie")
        self.assertEqual(X.norm_entity("glasses"), "glass")


class Validation(unittest.TestCase):
    def test_example_is_valid(self):
        self.assertEqual(X.validate(EXAMPLE), [])
        self.assertEqual(X.validate({"Entities": [], "EventRelation": []}), [])

    def test_rejections(self):
        bad = [
            ([], "top level"),
            ({"EventRelation": []}, "Entities"),
            ({"Entities": ["a", ""], "EventRelation": []}, "non-empty string"),
            ({"Entities": []}, "EventRelation"),
            ({"Entities": [], "EventRelation": [{"arguer": "Bob"}]}, "no 'type'"),
            ({"Entities": [], "EventRelation": [{"type": "x", "claim": 3}]}, "text value"),
            ({"Entities": [], "EventRelation": [{"type": "x", "claim": ["a"]}]}, "text value"),
            ({"Entities": [], "EventRelation": ["x"]}, "not an object"),
        ]
        for rec, frag in bad:
            errs = X.validate(rec)
            self.assertTrue(any(frag in e for e in errs), (rec, errs))


class Links(unittest.TestCase):
    def test_example_links(self):
        ev = X.derive(EXAMPLE)
        arg = ev[0]["slots"]
        self.assertEqual(arg["claim_subject"]["link"], "CockroachDB")
        self.assertEqual(arg["domain"]["link"], "multi-region payments")
        self.assertEqual(arg["arguer"]["link"], "Bob")
        self.assertIsNone(arg["claim"]["link"])                       # plain text
        self.assertEqual(ev[1]["slots"]["accepted_object"]["link"], "proposal")

    def test_match_ignores_case_determiner_possessive_plural(self):
        rec = {"Entities": ["Prius", "snack"], "EventRelation": [
            {"type": "ownership", "owner": "Evan", "thing": "the prius", "other": "Evan's Prius", "many": "Snacks"}]}
        s = X.derive(rec)[0]["slots"]
        self.assertEqual((s["thing"]["link"], s["other"]["link"], s["many"]["link"]), ("Prius", "Prius", "snack"))
        self.assertIsNone(s["owner"]["link"])                         # Evan is not in Entities here

    def test_type_and_role_names_are_normalised(self):
        ev = X.derive({"Entities": [], "EventRelation": [{"type": "Road Trip", "Who Went": "Evan"}]})
        self.assertEqual(ev[0]["type"], "road_trip")
        self.assertIn("who_went", ev[0]["slots"])


class RegistryTests(unittest.TestCase):
    def test_counts_and_render(self):
        reg = X.Registry()
        self.assertIn("empty", reg.render(0))
        reg.update(X.derive(EXAMPLE), 0, EXAMPLE["Entities"])
        reg.update(X.derive(EXAMPLE), 1, EXAMPLE["Entities"])
        self.assertEqual(reg.types["argument"]["count"], 2)
        self.assertEqual(reg.types["argument"]["roles"]["arguer"], 2)
        out = reg.render(2)
        self.assertIn("- argument (2):", out)
        self.assertIn("arguer (2)", out)
        self.assertIn('e.g. {"type": "argument"', out)
        self.assertEqual(reg.sizes(), {"types": 2, "roles": 6})

    def test_render_limits(self):
        reg = X.Registry()
        for i in range(60):                                             # 60 types, 3 uses for the first 10, then 1
            for _ in range(3 if i < 10 else 1):
                reg.update([{"type": f"t{i:02d}", "slots": {"r": {"value": "v", "link": None}}}], 0, [])
        out = reg.render(1000)                                          # far later: no type counts as recent
        self.assertEqual(len(out.split("\n")), X.TOP_TYPES)
        self.assertIn("- t00 (3):", out)
        recent = reg.render(10)                                         # last seen at tick 0: all recent within 20
        self.assertEqual(len(recent.split("\n")), 60)

    def test_recent_reuse_keeps_a_rare_type_visible(self):
        reg = X.Registry()
        slot = {"r": {"value": "v", "link": None}}
        for i in range(45):                                             # 45 common types, 3 uses each, last seen at tick 0
            for _ in range(3):
                reg.update([{"type": f"common{i:02d}", "slots": slot}], 0, [])
        reg.update([{"type": "rare", "slots": slot}], 0, [])            # first seen at tick 0 ...
        reg.update([{"type": "rare", "slots": slot}], 100, [])          # ... used again at tick 100 (2 uses: below the top 40)
        self.assertIn("- rare (2):", reg.render(105))                   # visible only through recency
        self.assertNotIn("- rare (2):", reg.render(200))                # later it falls out again

    def test_role_cap(self):
        reg = X.Registry()
        reg.update([{"type": "x", "slots": {f"r{i}": {"value": "v", "link": None} for i in range(12)}}], 0, [])
        self.assertEqual(reg.render(1).count("(1)"), X.MAX_ROLES + 1)   # roles plus the type's own count


class RunAndReport(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.src = os.path.join(self.d, "source.jsonl")
        with open(self.src, "w") as f:
            for t in TURNS:
                f.write(json.dumps(t) + "\n")

    def replay(self, raws):
        p = os.path.join(self.d, "replay.jsonl")
        with open(p, "w") as f:
            for r in raws:
                f.write(json.dumps({"raw": r}) + "\n")
        return p

    def run_main(self, raws, extra=()):
        X.main(["--source", self.src, "--out-dir", os.path.join(self.d, "out"), "--provider", "replay", "--model", "stub",
                "--replay", self.replay(raws), *extra])
        return [json.loads(l) for l in open(os.path.join(self.d, "out", "replay__stub__run1.jsonl"))]

    def test_end_to_end_with_retry(self):
        raws = [RAW[0], {"Entities": ["Evan"], "EventRelation": [{"type": "trip", "when": 3}]}, RAW[1], RAW[2]]   # t1 first answer is bad
        rows = self.run_main(raws)
        self.assertEqual([r["attempts"] for r in rows], [1, 2, 1])
        self.assertEqual(rows[1]["events"][0]["slots"]["destination"]["link"], "Jasper")
        self.assertEqual(rows[1]["events"][0]["slots"]["companions"]["link"], "family")     # "my family" -> family
        self.assertIsNone(rows[1]["events"][0]["slots"]["when"]["link"])
        self.assertEqual(rows[2]["events"][0]["slots"]["object"]["link"], "it")             # pronoun kept as an entity
        self.assertEqual(rows[1]["registry"], {"types": 1, "roles": 4})
        meta = json.load(open(os.path.join(self.d, "out", "replay__stub__run1.meta.json")))
        self.assertEqual(meta["prompt_version"], X.PROMPT_VERSION)
        self.assertEqual(len(meta["prompt_sha256"]), 64)

    def test_registry_reaches_the_next_prompt(self):
        reg = X.Registry()
        reg.update(X.derive(RAW[1]), 1, RAW[1]["Entities"])
        prompt = X.make_prompt(TURNS[2], "t2", reg, 2)
        self.assertIn("- trip (1): ", prompt)
        self.assertIn("speaker Sam, listener Evan", prompt)
        self.assertIn("Turn t2: That sounds great", prompt)
        self.assertNotIn("Jasper last weekend", prompt)                                     # earlier turn text is not leaked

    def test_failure_stops_and_resume_continues(self):
        bad = {"Entities": "x", "EventRelation": []}
        with self.assertRaises(SystemExit):
            self.run_main([RAW[0], bad, bad, bad, bad])
        saved = [json.loads(l) for l in open(os.path.join(self.d, "out", "replay__stub__run1.jsonl"))]
        self.assertEqual(len(saved), 1)
        rows = self.run_main([RAW[1], RAW[2]], ["--resume"])
        self.assertEqual([r["event_id"] for r in rows], ["t0", "t1", "t2"])
        self.assertEqual(rows[2]["registry"]["types"], 2)                                    # registry rebuilt from saved rows

    def test_limit(self):
        rows = self.run_main([RAW[0]], ["--limit", "1"])
        self.assertEqual(len(rows), 1)

    def test_report_numbers(self):
        rows = self.run_main([RAW[0], {"Entities": [], "EventRelation": [{"type": "x", "a": 1}]}, RAW[1], RAW[2]])
        turns = [json.loads(l) for l in open(self.src)]
        m = R.measures(rows, turns, window=2)
        self.assertAlmostEqual(m["M1_valid_without_retry"], 2 / 3)
        self.assertEqual(m["events"], 2)
        self.assertEqual(m["slot_values"], 7)                                  # trip: 4 roles; state: 3 roles
        self.assertAlmostEqual(m["M3_link_rate_all_slots"], 4 / 7)             # Evan, Jasper, family, it
        self.assertEqual(m["M5_time_cue_turns"], 1)
        self.assertEqual(m["M5_time_cue_kept"], 1.0)                           # "last weekend" kept in slot 'when'
        self.assertEqual(m["M4_new_types_per_window"], [{"turns": "0-1", "new_types": 1}, {"turns": "2-2", "new_types": 1}])
        text = R.review(rows, turns)
        self.assertIn("destination='Jasper' LINK", text)
        self.assertIn("when='last weekend' TEXT", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
