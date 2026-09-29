# ND-1 — Engine v0: from entity-dimension output to N-D geometry

**Status:** spec frozen. Run 1 complete (M3 and M5 pending); see `results/run1/REPORT.md`.

## Question

Given only the LLM's entity-dimension output (ND-0 format), can deterministic engine code and math build a geometry that answers questions about the source correctly, never breaks the contract, keeps the must-haves, and stays stable across models?

## Division of labour

| Layer | Does | Does not |
|---|---|---|
| LLM | Entities and free dimensions per sentence (`LLM_CONTRACT.md`) | Ticks, schema, statuses, buckets, relations |
| Engine (code + math) | Everything below | Call an LLM, except where a stage is marked "confirm" |

## Engine v0 stages

| # | Stage | Method (deterministic) |
|---|---|---|
| E1 | Ticks | One tick per input event, in order |
| E2 | Peg identity | Normalise names (case, punctuation, hyphens); exact and alias matches merge; near-matches ("peak load" / "peak-load benchmark") become proposals for confirmation, never auto-merged |
| E3 | Value linking | Find known peg names inside value strings, so "proposed PostgreSQL" links to the PostgreSQL peg; the value text is kept as a literal |
| E4 | Cleaning | Drop absence values ("not stated", "unspecified"); flag inference-marked dimensions ("implied_*", "suggests") as model-belief candidates, not facts |
| E5 | Epistemic tagging | Map the LLM's own cue dimensions and phrases (e.g. epistemic_source, "according to", "as reported", "might", "questioned whether", "planned") to statuses and owners, with a fixed rule table |
| E6 | Buckets | Values marked ambiguous/unclear become buckets; candidates come from the text and from collisions on the same dimension in earlier events |
| E7 | Dimension canonicalisation | Footprints over the corpus; propose equivalent, inverse, broader or related; apply only confirmed mappings |
| E8 | Geometry | Incidence matrix B, collision levels, trajectories, weighted relationship strength (tools/ndm_math.py) |

## Data

- Input: `../ND-0/data/pilot10.babytest.jsonl`, the existing LLM output. Run it as-is first; then on fresh stateless extractions from 2 more models, 3 runs each.
- Source text: `../ND-0/data/pilot10.source.jsonl`.
- Probes: `probes/pilot10.probes.jsonl` (15 questions with accepted answers). Must-haves: `probes/must_haves.jsonl` (7 checks).
- Reference only: `gold/pilot10.gold.jsonl` (one annotator's reading). **Not a scoring target.** It is used to design probes and must-haves, and as a ceiling for diagnostics.

## Evaluation principle

The LLM's reading is not compared to a handwritten structure. Many extractions of the same sentence are equally valid, so scoring is by what the extraction lets the system do: rules it must never break, faithfulness to the source, questions it must answer, and stability across models.

## Metrics

| ID | Metric | How | Target |
|---|---|---|---|
| M1 | Contract violations after engine stages | Schema; stored absences (C6); unflagged inferences (C7) | 0 |
| M2 | Faithfulness | Every entity name and every value's content words traceable to the source sentence (automatic lexical check, misses reviewed by hand) | ≥ 95% traceable; every untraceable item listed |
| M3 | Probe accuracy | An answering LLM receives only the engine output (no source text) and answers the 15 probes; answers are string-matched to accepted answers, misses reviewed | ≥ 13/15 |
| M4 | Must-haves | Each of the 7 checks passes or fails on the engine output | 7/7 |
| M5 | Stability | Across models and runs: storyline ranks, colliding event pairs (Jaccard), open buckets, probe answers | Storyline ranks identical; collision Jaccard ≥ 0.8; probe answers agree ≥ 90% |
| M6 | Extra-but-correct | Items the LLM extracted that the reference gold lacks but the source supports | Counted in the LLM's favour; listed |
| M7 | Stage attribution | For every M1–M4 failure: extraction miss (information absent from LLM output) or engine miss (present but lost or misused) | Reported per item |

**Diagnostics, not targets:** values that are pegs, single-event pegs, and colliding pairs versus the reference ceiling (`results/gold_ceiling.metrics.json`), from `tools/ndm_math.py`.

## Falsification

If must-haves MH4–MH5 and the attribution and belief probes fail as extraction misses (M7), the LLM output lacks the information: code cannot recover who said what or how certain it was. The minimal fix to test is adding one optional field per entity, `"said_by"`, to the LLM contract, and no more.

## Known limits

- Code can only recover what the LLM's output contains. If a speaker or hedge is missing from the output, no rule can restore it; M7 records these cases as extraction misses, not engine misses.
- Probes and must-haves were written by one author (Claude) and need a human pass; they are less subjective than a full gold structure, but not free of judgement.

## Amendments (logged before run 2; run 1 numbers are unchanged)

**A1: M2 split (after run 1).** Run 1 showed that 58 of 65 untraceable values were annotation labels (role, time, status, epistemic source) that describe the sentence rather than quote it. From run 2:

- **M2a:** entity names and *content* values must be lexically traceable to the source, at ≥ 95%.
- **M2b:** annotation labels are exempt from traceability but must not introduce pegs that the sentence does not contain. The target is 0.
- The run-1 definition is still computed and reported, for comparability.

**A2: Measurement fix.** The stemmer now handles "-ly" and "-fully" ("successfully" vs "successful" was a false miss in run 1).

**A3: Engine rule-table fix.** E4's parenthetical absence rule now includes "not recorded" (the single M1 failure in run 1).

**A4: Run 2 protocol.** LLM contract v1: stateless sessions, one sentence per session, the fixed dictionary `dimension_dictionary_v1.json`, a required entity `type`, and unresolved references marked `reference_status: unresolved`. The script is `tools/extract_stateless.py`; the batch runner is `engine/run_batch.py`. Must-haves compare names after normalisation, so valid spellings ("a separate service") pass.

**Known limit found while building run 2:** pronoun candidates are every type-compatible peg in the window, including the entity the pronoun modifies. The candidate lists for "its" are therefore noisy but always open, which is the safe direction. Not tuned on the pilot.
