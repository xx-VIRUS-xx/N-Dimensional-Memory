# ND-1 run 1: engine v0 on the existing BabyTest extraction

**Date:** 2026-09-28. **Input:** `ND-0/data/pilot10.babytest.jsonl` (the only extraction available; not stateless, no entity `type`). **Engine:** `engine/nd_engine.py` v0, stages E1–E6. **Spec:** `EXP-ND1.md`, as frozen. No metric was changed after seeing results.

Reproduce:

```
python engine/nd_engine.py ND-0/data/pilot10.babytest.jsonl ND-1/results/run1/engine_state.json
python engine/checks.py ND-1/results/run1/engine_state.json ND-0/data/pilot10.source.jsonl ND-1/results/run1/checks.json
python engine/probe_harness.py prompts ND-1/results/run1/engine_state.json ND-1/probes/pilot10.probes.jsonl ND-1/results/run1/probes
```

## Results against the frozen metrics

| ID | Metric | Target | Result | Pass |
|---|---|---|---|---|
| M1 | Contract violations after E4 | 0 | 1 stored absence (t8 `final adoption decision.existence`: "…may have been made but not recorded"); 0 unflagged inferences | ✗ |
| M2 | Faithfulness (traceable items) | ≥ 95% | 67.3% (2 names, 65 values untraceable) | ✗ |
| M3 | Probe accuracy | ≥ 13/15 | **Not run:** needs an answering model. Prompts are in `probes/prompts.jsonl` | — |
| M4 | Must-haves | 7/7 | **7/7** | ✓ |
| M5 | Stability across models and runs | see spec | Not run: only one extraction exists | — |
| M6 | Extra-but-correct | listed | Not assessed in this run | — |
| M7 | Stage attribution | per failure | Below | ✓ |

## What worked

- **Ambiguity handling matches the design exactly.** t4 (payments platform or separate service) is open; t5 ("its failover": PostgreSQL or benchmark) is open; t6 ("the rate-limiting change") is resolved by the engine under C9(c): one candidate in the window (t4), recorded with its evidence tick. That is 3 of 3, including the one the BabyTest extraction itself never flagged.
- **All 7 must-haves hold:** role direction, both open buckets, `model_belief` never used, Alice owning the peak-load claim, Bob's hedge kept as a possibility, no invented Bob–Carol conflict, and Alice's two proposals colliding.
- **Cleaning:** 13 of 14 stored absences dropped; 6 extractor inferences moved to model-belief candidates, none left inside facts.
- **Value linking:** 55.9% of role strings now link to a peg (the baseline had 16.1% of values that were pegs).
- **Identity:** 7 near-match proposals raised, none auto-merged. They include one correct rejection case: "payments platform team" ~ "payments platform" (a team is not a platform), which shows why confirmation is required.

## Failures and attribution (M7)

| Failure | Cause | Attribution |
|---|---|---|
| M1: one absence kept (t8 existence) | E4 parenthetical rule lists "not stated/unspecified/unknown/not specified" but not "not recorded" | Engine (rule table gap) |
| M2: 58 of 65 untraceable values are annotation labels (`role_in_event = proposer`, `temporal_position = past`, `*_status`, `epistemic_*`) | The BabyTest prompt asks the LLM to describe roles, time and status. These labels describe the sentence rather than quote it, so lexical traceability cannot judge them | Metric–contract mismatch (see decision 2) |
| M2: `PostgreSQL` at t5 (as participant and `target_system`) | s5 never names PostgreSQL; the extractor added it from earlier context. A real faithfulness miss, and it is also why PostgreSQL appears as a t5 bucket candidate | Extraction (not stateless) |
| M2: `the proposal` at t4 | The extractor turned the event itself into an entity | Extraction |
| M2: 5 paraphrases (e.g. "uncertain, only possible" for "might") and 1 artefact ("successful" vs "successfully", stemmer gap) | Paraphrase is expected from a free-dimension prompt; the stemmer is a measurement bug | Extraction / measurement |
| Single-event pegs unchanged (76.9%) | By design: identity proposals await confirmation | Expected; confirmation step not built |

## Other findings

- **Memory is larger than the source.** The rendered engine state is 1,459 words for a 155-word source (9.4×), almost all of it annotation labels. The depiction layer's zoom and budget (ND-3) is not optional polish; without it the LLM reads more memory than it would have read conversation.
- **Per-string status is noisy but must-have-safe.** Speech-act strings ("Carol said…") and label strings sometimes get intent or open-question statuses from cue words. That's acceptable for v0 because every must-have holds, but it is visible in the probe context.

## Decisions for run 2

1. Add "not recorded" to the E4 absence rule table. This is a rule-table fix, applied to run 2, not retroactively to run 1.
2. **Amend M2 before run 2 (spec change, logged in `EXP-ND1.md`):** split role strings into *content* (checked by lexical traceability) and *annotation labels* (role, time, status, epistemic source). Labels are checked for validity against a closed label vocabulary, not for traceability. Otherwise, alternatively, drop annotation labels from the LLM contract.
3. Run 2 input: fresh **stateless** extractions (one sentence per session, dimension dictionary, entity `type`) from 2–3 models, 3 runs each. This tests the contract as designed and makes M5 possible. The t5 PostgreSQL insertion should disappear, and the global backward run must then supply PostgreSQL as a candidate.
4. Run M3 with an answering model on run 1's prompts, to get a first probe number before run 2.
