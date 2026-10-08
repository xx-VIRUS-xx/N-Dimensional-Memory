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
import nde_synonyms as S  # noqa: E402
import nde_evidence as E  # noqa: E402

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


class PromptContract(unittest.TestCase):
    def test_rules_present(self):
        for frag in ("ONE sentence of a conversation",
                     "you are not told who speaks, who is addressed, or when",
                     'You are not told who "I", "me", "my", "you" or "your" are',
                     "Otherwise put the word in Entities as written",
                     "do not automatically include the person addressed",
                     "Every role value that names one of these must also be in Entities",
                     "List an entity only if it appears as a role value in one of your relations",
                     "this includes \"I\", \"you\", \"we\", \"it\" and any other pronoun you use as a value",
                     'is recorded as one relation of type "address" with the role "addressee"',
                     'Use type "greeting", "thanks" or "farewell" only when the sentence really greets, thanks or says goodbye',
                     'Never join two with "and" or a comma',
                     "A phrase, a time expression, a feeling or a question is never an entity",
                     "belong to the example"):
            self.assertIn(frag, X.PROMPT)

    def test_no_dataset_metadata_in_the_prompt_template(self):
        for gone in ("{speaker}", "{listener}", "{date}", "listener", "metadata", "Turn ", "Sam", "Evan"):
            self.assertNotIn(gone, X.PROMPT)                                                  # no placeholders, no dataset names
            self.assertNotIn(gone, X.PROMPT)
        for gone in ('"argument"', '"acceptance"'):
            self.assertNotIn(gone, X.PROMPT)                                                  # example types must not be generic

    def test_prompt_text_is_the_one_frozen_for_phase_2(self):
        import hashlib
        self.assertEqual(X.PROMPT_VERSION, "v4.1")
        self.assertEqual(hashlib.sha256(X.PROMPT.encode()).hexdigest()[:8], "ee9427ff")


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
        self.assertEqual(rows[1]["relations"][0]["slots"]["destination"]["link"], "Jasper")
        self.assertEqual(rows[1]["relations"][0]["slots"]["companions"]["link"], "family")     # "my family" -> family
        self.assertIsNone(rows[1]["relations"][0]["slots"]["when"]["link"])
        self.assertEqual(rows[2]["relations"][0]["slots"]["object"]["link"], "it")             # pronoun kept as an entity
        self.assertEqual(rows[1]["registry"], {"types": 1, "roles": 4})
        meta = json.load(open(os.path.join(self.d, "out", "replay__stub__run1.meta.json")))
        self.assertEqual(meta["prompt_version"], X.PROMPT_VERSION)
        self.assertEqual(len(meta["prompt_sha256"]), 64)

    def test_registry_reaches_the_next_prompt(self):
        reg = X.Registry()
        reg.update(X.derive(RAW[1]), 1, RAW[1]["Entities"])
        prompt = X.make_prompt(TURNS[2], "t2", reg, 2)
        self.assertIn("- trip (1): ", prompt)
        self.assertIn("Sentence t2: That sounds great", prompt)
        self.assertNotIn("Jasper last weekend", prompt)                                     # earlier sentence text is not leaked

    def test_model_sees_only_the_sentence_and_the_registry(self):
        prompt = X.make_prompt(TURNS[1], "t1", X.Registry(), 1)
        for leaked in ("1:00 pm", "18 May", "Sam", "Evan", "{speaker}", "{listener}", "{date}"):
            self.assertNotIn(leaked, prompt)
        self.assertIn("I got back from a road trip to Jasper", prompt)

    def test_rows_carry_no_speaker_listener_or_date_and_call_relations_relations(self):
        rows = self.run_main([RAW[0], RAW[1], RAW[2]])
        for r in rows:
            self.assertFalse({"speaker", "listener", "date", "events"} & set(r), r.keys())
            self.assertIn("relations", r)
        meta = json.load(open(os.path.join(self.d, "out", "replay__stub__run1.meta.json")))
        self.assertEqual(meta["model_input"], "sentence text and registry only")
        self.assertEqual(meta["events"], 3)

    def test_first_person_stays_ambiguous_because_nothing_names_the_speaker(self):
        raw = {"Entities": ["I", "Jasper"], "EventRelation": [{"type": "trip", "traveler": "I", "destination": "Jasper"}]}
        rows = self.run_main([raw, RAW[1], RAW[2]])
        s = rows[0]["relations"][0]["slots"]
        self.assertEqual((s["traveler"]["link"], s["destination"]["link"]), ("I", "Jasper"))   # "I" is an ambiguous entity, not Sam or Evan

    def test_old_rows_with_events_key_are_still_read(self):
        self.assertEqual(X.rels({"events": [1]}), [1])
        self.assertEqual(X.rels({"relations": [2], "events": [1]}), [2])

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
        self.assertEqual(m["events"], 3)
        self.assertEqual(m["relations"], 2)
        self.assertEqual(m["slot_values"], 7)                                  # trip: 4 roles; state: 3 roles
        self.assertAlmostEqual(m["M3_link_rate_all_slots"], 4 / 7)             # Evan, Jasper, family, it; Sam is not in Entities, so it stays TEXT (nothing supplies it)
        self.assertEqual(m["M5_time_cue_events"], 1)
        self.assertEqual(m["M5_time_cue_kept"], 1.0)                           # "last weekend" kept in slot 'when'
        self.assertEqual(m["M4_new_types_per_window"], [{"events": "0-1", "new_types": 1}, {"events": "2-2", "new_types": 1}])
        text = R.review(rows, turns)
        self.assertIn("destination='Jasper' LINK", text)
        self.assertIn("when='last weekend' TEXT", text)


class EvidenceOracle(unittest.TestCase):
    def _fixture(self, n=16):
        src = [{"sentence_id": f"t{i}", "dia_id": f"D1:{i + 1}", "speaker": "Sam" if i % 2 == 0 else "Evan",
                "listener": "Evan" if i % 2 == 0 else "Sam", "text": "x"} for i in range(n)]
        rows = []
        for i in range(n):
            ev = [("state", {"subject": ("I", "I"), "state": ("fine", None)})]
            if i == 5:
                ev.append(("trip", {"destination": ("Rockies", "Rockies")}))
            rows.append(dict(_row(f"t{i}", *ev), Entities=["I"] + (["Rockies"] if i == 5 else []) + (["lake"] if i == 7 else [])))
        return src, rows

    def test_evidence_mapping_and_categories(self):
        src, _ = self._fixture(4)
        probes = [{"category": 1, "evidence": ["D1:1", "D1:3", "D9:9"]}, {"category": 5, "evidence": ["D1:2"]},
                  {"category": 2, "evidence": ["D1:1"]}]
        ids, missing = E.evidence_events(probes, src)
        self.assertEqual(ids, ["t0", "t2"])
        self.assertEqual(missing, ["D9:9"])

    def test_hubs_are_the_speakers_of_the_source(self):
        src, _ = self._fixture(4)
        self.assertEqual(E.hubs_of(src), {"sam", "evan"})

    def test_pronoun_only_event_has_no_entity_key_and_join_cannot_create_one(self):
        src, rows = self._fixture()
        for join in (False, True):
            m = E.measure(rows, src, ["t0"], join, False)
            self.assertEqual((m["covered"], m["M6_no_entity_key"]), (1, 1))

    def test_join_shrinks_the_candidate_set_for_i(self):
        src, rows = self._fixture()
        stored = E.measure(rows, src, ["t0"], False, False)
        joined = E.measure(rows, src, ["t0"], True, False)
        self.assertEqual(stored["detail"][0]["smallest_candidate_set"], 16)
        self.assertEqual(joined["detail"][0]["smallest_candidate_set"], 8)
        self.assertEqual((stored["M7_le10"], joined["M7_le10"]), (0, 1))

    def test_entity_key_counts_and_entities_list_is_a_second_arm(self):
        src, rows = self._fixture()
        slots = E.measure(rows, src, ["t5", "t7"], False, False)
        both = E.measure(rows, src, ["t5", "t7"], False, True)
        self.assertEqual(slots["M6_no_entity_key"], 1)
        self.assertEqual(both["M6_no_entity_key"], 0)
        self.assertEqual(slots["detail"][0]["smallest_candidate_set"], 1)

    def test_events_missing_from_the_run_are_not_covered(self):
        src, rows = self._fixture(4)
        m = E.measure(rows[:2], src, ["t0", "t3"], False, False)
        self.assertEqual((m["evidence_events"], m["covered"]), (2, 1))

    def test_cli_writes_both_files(self):
        src, rows = self._fixture()
        with tempfile.TemporaryDirectory() as d:
            for name, data in (("s.jsonl", src), ("r.jsonl", rows), ("p.jsonl", [{"category": 1, "evidence": ["D1:1"]}])):
                with open(os.path.join(d, name), "w") as f:
                    f.write("\n".join(json.dumps(x) for x in data) + "\n")
            E.main(["--extraction", os.path.join(d, "r.jsonl"), "--source", os.path.join(d, "s.jsonl"),
                    "--probes", os.path.join(d, "p.jsonl"), "--out", os.path.join(d, "o")])
            out = json.load(open(os.path.join(d, "o", "nde_evidence.json")))
            self.assertEqual(set(out["arms"]), {"slots / as stored", "slots / joined", "+entities / as stored", "+entities / joined"})
            self.assertIn("M6", open(os.path.join(d, "o", "nde_evidence.md")).read())


class SynonymAtScale(unittest.TestCase):
    NAMES = ("alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel", "india", "juliet")

    def filler(self):
        return [_row(f"f{i}", (self.NAMES[i], {f"own_role_{i}": ("v", None)})) for i in range(10)]

    def pair_rows(self, shared=("park", "gift", "lake")):
        a = {f"r{i}": (e, e) for i, e in enumerate(shared)}
        b = {f"s{i}": (e, e) for i, e in enumerate(shared)}
        return [_row("t0", ("x_one", a)), _row("t1", ("y_two", b))] + self.filler()

    def test_three_shared_entities_make_a_pair_until_they_are_named_hubs(self):
        rows = self.pair_rows()
        self.assertEqual(len(S.candidates(S.profile(rows))), 1)
        self.assertEqual(S.candidates(S.profile(rows), hub_names=("Park", "gift")), [])      # source speakers are hubs, case ignored

    def test_overlap_must_be_a_share_of_the_smaller_type(self):
        big = {f"r{i}": (f"e{i}", f"e{i}") for i in range(12)}
        small = {f"s{i}": (f"e{i}", f"e{i}") for i in range(3)}
        rows = [_row("t0", ("x_one", big)), _row("t1", ("y_two", small))] + self.filler()
        self.assertEqual(len(S.candidates(S.profile(rows))), 1)                              # 3 of 3 shared: all of the smaller type
        small2 = {f"s{i}": (f"e{i}" if i < 3 else f"z{i}", f"e{i}" if i < 3 else f"z{i}") for i in range(12)}
        rows = [_row("t0", ("x_one", big)), _row("t1", ("y_two", small2))] + self.filler()
        self.assertEqual(S.candidates(S.profile(rows)), [])                                  # 3 of 12: below 0.3

    def test_catch_all_type_is_not_paired_by_shared_entities(self):
        rows = self.pair_rows() + [_row(f"c{i}", ("x_one", {"q": ("v", "park")})) for i in range(40)]
        self.assertEqual(S.candidates(S.profile(rows)), [])                                  # x_one holds over a quarter of all relations

    def test_numbered_role_copies_do_not_count_as_shared_roles(self):
        rows = [_row("t0", ("x_one", {"object": ("a", None), "reason": ("b", None)})),
                _row("t1", ("y_two", {"object_2": ("a", None), "reason_2": ("b", None)}))] + self.filler()
        self.assertEqual(len(S.candidates(S.profile(rows))), 1)                              # object_2 and object are one role name for comparing types
        rows = [_row("t0", ("x_one", {"other": ("a", None)})), _row("t1", ("y_two", {"object_2": ("a", None), "reason_2": ("b", None)}))] + self.filler()
        self.assertEqual(S.candidates(S.profile(rows)), [])

    def test_role_families_group_roles_whose_links_are_the_same_pronoun(self):
        rows = [_row(f"t{i}", ("thanks", {"thanker": ("I", "I")})) for i in range(12)] + \
               [_row(f"u{i}", ("hope", {"hoper": ("I", "I")})) for i in range(12)] + \
               [_row(f"v{i}", ("trip", {"destination": ("Rockies", "Rockies")})) for i in range(12)]
        fam = S.role_families(rows)
        self.assertEqual(sorted(x["role"] for x in fam["i"]), ["hoper", "thanker"])
        self.assertNotIn("destination", str(fam))
        self.assertEqual(S.role_families(rows[:12]), {})                                      # one role is not a family
        mixed = [_row(f"m{i}", (t, {"mixed": (p, p)})) for t in ("p_type", "q_type") for i, p in enumerate(("I", "you", "we", "it") * 3)]
        self.assertNotIn("mixed", str(S.role_families(rows + mixed)))                         # no single pronoun reaches half of its links

    def test_cli_reads_hub_names_from_the_source(self):
        rows = self.pair_rows(("sam", "gift", "lake"))
        with tempfile.TemporaryDirectory() as d:
            ext, srcp = os.path.join(d, "r.jsonl"), os.path.join(d, "s.jsonl")
            open(ext, "w").write("\n".join(json.dumps(r) for r in rows) + "\n")
            open(srcp, "w").write(json.dumps({"sentence_id": "t0", "speaker": "Sam", "listener": "Evan", "text": "x"}) + "\n")
            S.main(["--extraction", ext, "--out", os.path.join(d, "a")])
            S.main(["--extraction", ext, "--source", srcp, "--out", os.path.join(d, "b")])
            self.assertEqual(len(json.load(open(os.path.join(d, "a", "synonym_candidates.json")))["type_pairs"]), 1)
            self.assertEqual(len(json.load(open(os.path.join(d, "b", "synonym_candidates.json")))["type_pairs"]), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)


def _row(tid, *events):
    return {"event_id": tid, "relations": [{"type": ty, "slots": {r: {"value": v, "link": l} for r, (v, l) in sl.items()}} for ty, sl in events]}


class SynonymCandidates(unittest.TestCase):
    def rows(self):
        hubs = lambda n: {"actor": (n, n)}
        return [
            _row("t0", ("travel", {"traveler": ("Evan", "Evan"), "destination": ("Rockies", "Rockies"), "time": ("last week", None)})),
            _row("t1", ("travel_return", {"traveler": ("Evan", "Evan"), "companions": ("family", "family"), "time": ("just", None)})),
            _row("t2", ("thanks", {"thanker": ("Sam", "Sam"), "recipient": ("Evan", "Evan"), "time": ("now", None)})),
            _row("t3", ("farewell", {"fareweller": ("Sam", "Sam"), "target": ("Evan", "Evan"), "time": ("soon", None)})),
            _row("t4", ("outing", {"participants": ("Evan", "Evan"), "companion": ("dad", "dad"), "companions": ("family", "family")})),
        ]

    def test_finds_name_token_pair_and_ignores_hubs_and_generic_roles(self):
        types = S.profile(self.rows())
        pairs = {(c["a"], c["b"]) for c in S.candidates(types)}
        self.assertIn(("travel", "travel_return"), pairs)
        self.assertNotIn(("farewell", "thanks"), pairs)                  # share only hub entities Sam and Evan and the generic role time
        self.assertNotIn(("outing", "thanks"), pairs)

    def test_role_variants_within_a_type(self):
        v = S.role_variants(S.profile(self.rows()))
        self.assertEqual([(x["type"], x["a"], x["b"]) for x in v], [("outing", "companion", "companions")])

    def test_shared_specific_roles_and_entities_count(self):
        rows = [_row("t0", ("a_one", {"giver": ("x", "x"), "gift": ("g", "gift"), "place": ("p", "park"), "when": ("w", "noon")})),
                _row("t1", ("b_two", {"giver": ("x", "x"), "gift": ("g", "gift"), "place": ("p", "park"), "other": ("o", "o")})),
                *[_row(f"f{i}", (("alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel", "india", "juliet")[i], {f"own_role_{i}": ("v", None)})) for i in range(10)]]            # enough types that shared roles are not "generic"
        pairs = [(c["a"], c["b"], c["reasons"]) for c in S.candidates(S.profile(rows))]
        self.assertEqual(len(pairs), 1)
        self.assertEqual(pairs[0][:2], ("a_one", "b_two"))
        self.assertEqual(len(pairs[0][2]), 2)                            # specific roles and entities, each a reason

    def test_generic_role_alone_does_not_make_a_pair(self):
        names = ("alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel", "india", "juliet")
        rows = [_row("t0", ("x_one", {"giver": ("g", None), "time": ("now", None)})),
                _row("t1", ("y_two", {"giver": ("g", None), "time": ("now", None)})),
                _row("t2", ("z_three", {"time": ("now", None)})),
                *[_row(f"f{i}", (names[i], {f"own_role_{i}": ("v", None)})) for i in range(10)]]
        types = S.profile(rows)
        self.assertIn("time", S.generic_roles(types))
        self.assertNotIn("giver", S.generic_roles(types))
        self.assertEqual(S.candidates(types), [])                        # only one specific shared role (giver); time is generic

    def test_pronouns_do_not_make_a_pair(self):
        names = ("alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel", "india", "juliet")
        rows = [_row("t0", ("x_one", {"a": ("i", "I"), "b": ("y", "you"), "c": ("w", "we"), "d": ("t", "it")})),
                _row("t1", ("y_two", {"e": ("i", "I"), "f": ("y", "you"), "g": ("w", "we"), "h": ("t", "it")})),
                *[_row(f"f{i}", (names[i], {f"own_role_{i}": ("v", None)})) for i in range(10)]]
        types = S.profile(rows)
        self.assertEqual(types["x_one"]["entities"], set())               # pronoun links are not recorded as entities
        self.assertEqual(S.candidates(types), [])

    def test_two_shared_entities_are_not_enough_three_are(self):
        names = ("alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel", "india", "juliet")
        filler = [_row(f"f{i}", (names[i], {f"own_role_{i}": ("v", None)})) for i in range(10)]
        two = [_row("t0", ("x_one", {"a": ("1", "park"), "b": ("2", "gift")})), _row("t1", ("y_two", {"c": ("1", "park"), "d": ("2", "gift")}))]
        self.assertEqual(S.candidates(S.profile(two + filler)), [])
        three = [_row("t0", ("x_one", {"a": ("1", "park"), "b": ("2", "gift"), "z": ("3", "noon")})),
                 _row("t1", ("y_two", {"c": ("1", "park"), "d": ("2", "gift"), "y": ("3", "noon")}))]
        self.assertEqual([(c["a"], c["b"]) for c in S.candidates(S.profile(three + filler))], [("x_one", "y_two")])

    def test_cli_writes_report_and_changes_nothing(self):
        d = tempfile.mkdtemp()
        src = os.path.join(d, "run.jsonl")
        with open(src, "w") as f:
            for r in self.rows():
                f.write(json.dumps(r) + "\n")
        before = open(src).read()
        S.main(["--extraction", src, "--out", os.path.join(d, "o")])
        self.assertEqual(open(src).read(), before)
        md = open(os.path.join(d, "o", "synonym_candidates.md")).read()
        self.assertIn("travel (1) vs travel_return (1)", md)
        self.assertIn('"event": "t0"', md)
        self.assertNotIn('"turn"', md)
        self.assertEqual(json.load(open(os.path.join(d, "o", "synonym_candidates.json")))["types"], 5)
