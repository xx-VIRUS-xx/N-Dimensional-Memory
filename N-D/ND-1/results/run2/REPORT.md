# ND-1 run 2: stateless extractions through Claude Code

**Date:** 2026-09-29. **Extractor:** Claude Code 2.1.281, print mode, one fresh empty-folder session per sentence; Sonnet × 3 runs and Opus × 3 runs. `~/.claude/CLAUDE.md` was absent in all 6 runs (`.meta.json`). **Prompt:** LLM contract v1, unchanged. **Engine:** v0.1 as committed (primary results), then v0.2 (diagnostic rescoring, below).

## Primary results (engine v0.1, as frozen before the runs)

| Run | M1 | M2a | M2b | M4 | Failed |
|---|---|---|---|---|---|
| Opus 1 | ok | 0.987 | 0 | 7/7 | none |
| Opus 2 | ok | 0.986 | 0 | 7/7 | none |
| Opus 3 | ok | 1.000 | 0 | 7/7 | none |
| Sonnet 1 | ok | 1.000 | 0 | 5/7 | MH2, MH3 |
| Sonnet 2 | ok | 1.000 | 0 | 5/7 | MH2, MH3 |
| Sonnet 3 | ok | 1.000 | 0 | 5/7 | MH2, MH3 |

M5: collision Jaccard (minimum over all pairs) **1.0**; bucket-outcome Jaccard (minimum) **0.091**. M3 not yet run.

## What the runs show

1. **Stateless extraction is far more faithful.** M2a is 0.986–1.000 against 0.934 for the BabyTest extraction; M2b is 0 in every run (no invented pegs). The PostgreSQL insertion seen in run 1 is gone.
2. **The collision geometry is identical across all 6 runs.** 23 colliding event pairs, the same pairs, for both models and every run. The structure N-D relies on does not depend on which Claude model extracts or on run-to-run noise.
3. **Ambiguity handling is unstable, for four distinct reasons.** Each was traced by reading the extractions:

| # | What the extraction did | Attribution |
|---|---|---|
| a | Sonnet wrote "its failover behavior" as a single unresolved entity; v0.1 only recognised a bare pronoun | Engine miss: the information was present |
| b | Sonnet expressed "payments platform or a separate service" as two unresolved entities marked `unclear`, instead of one "A or B" value | Engine miss: the information was present, in a shape v0.1 didn't read |
| c | Opus marked first mentions ("the architecture document", "the team") as unresolved; v0.1 turned each into an `unknown_referent` bucket | Engine: noise, not error; these are new entities |
| d | Opus run 2 marked "they" as unresolved; v0.1 allowed only persons for "they", excluding "the payments platform team" | Engine bug |
| e | Sonnet never marked "the rate-limiting change" as unresolved (it kept "the" in the name) | Extraction under-marking that the engine can compensate for |
| f | **Sonnet run 3 silently resolved "its" to the benchmark** (`owner: the peak-load benchmark`) | **Extraction violation** of contract rule 5. MH3 is right to fail it. |

## Diagnostic rescoring (engine v0.2)

Engine v0.2 adds rules A7a–A7g and scopes the MH3 check (A8); both are logged in `EXP-ND1.md`. The same extractions, rescored (`per_run_engine_v0.2/`, `summary_engine_v0.2.json`):

| Run | M4 | Buckets |
|---|---|---|
| Opus 1, 3 | 7/7 | t4 open, t5 "its" open, t5 "the peak-load benchmark" resolved → t2, t6 resolved → t4 |
| Opus 2 | 7/7 | same, plus t7 "they" open |
| Sonnet 1, 2 | 7/7 | same as Opus 1 |
| Sonnet 3 | 6/7 (MH3) | t5 "its" absent: silently resolved by the extractor (row f) |

M5 under v0.2: collision Jaccard 1.0, bucket-outcome Jaccard 0.6. The remaining bucket differences are Opus 2's extra "they" bucket (the sentence resolves it, but it was marked unresolved) and Sonnet 3's missing "its".

**This rescoring is not evidence that v0.2 works.** v0.2 was designed by reading these exact failures, so it is fitted to them. It counts only after ND-1b: new conversations, extracted fresh, scored with v0.2 frozen.

## Honest limits

- **Claude-only (amendment A6).** Stability is shown within one model family. Cross-family stability is untested, and shared training could hide shared blind spots.
- **No temperature control** through the CLI. Sonnet's three runs were nearly identical anyway; Opus varied more.

## Decisions

1. Freeze engine v0.2 and prompt v1 for ND-1b.
2. Prompt v1 stays unchanged. Row f is an extraction violation that engine rules must not paper over; it stays visible as an MH3 failure.
3. M3 is done (below).
4. Next: ND-1b, three new 30-sentence conversations, never seen by the engine rules.

## M3: probe accuracy (added 2026-09-30)

The answering model is Claude Sonnet via `claude -p`, one isolated call per probe. It sees only the rendered engine memory. All 180 answers were read by hand (`m3_review.json`).

| Run | Engine v0.1 | Engine v0.2 |
|---|---|---|
| Opus 1 / 2 / 3 | 15 / 15 / 15 | 15 / 15 / 15 |
| Sonnet 1 | 14 (p10) | 15 |
| Sonnet 2 | **14** (p10; automatic score was 15) | 15 |
| Sonnet 3 | 14 (p10) | 14 (p10) |

Every run clears the ≥ 13/15 target. The only probe ever missed is p10, "whose failover behaviour is uncertain?", and every miss names an owner for an unresolved "its". The misses land exactly where the must-haves predicted.

**Caveats:**

- **No string scorer is reliable here.** Substring matching let "no" match inside "not" and "known". Whole-word matching (A9) fixes that, but creates a new false miss (Opus 1: "Not fully — … unresolved"), and neither catches a self-contradicting answer ("No — … it's PostgreSQL's"). The automatic score is triage only; **hand review of every answer on the discriminating probes (p08, p10, p13) is mandatory**, and run 2's M3 is the hand-reviewed number.
- **Most probes are easy.** Any faithful extraction answers probes such as "who proposed Redis?". Only p08, p10 and p13 discriminate. M3 shows that memory keeps the facts; it does not show that the N-D depiction helps. That is ND-3's question.
- **The answering model is from the same family as the extractor** (Claude-only, A6).
- **The depiction shows raw extractor labels.** Opus answers to p05 hedged because the memory still displayed `reference_status = unresolved` for "the team", although the engine had classified it as a first mention. The renderer should show engine decisions, not the labels those decisions replaced. This belongs in the depiction layer (ND-3).

## ND-1 verdict

| Gate criterion (PLAN.md) | Result |
|---|---|
| M1 = 0 | ✓ all runs |
| M2a ≥ 95%, M2b = 0 | ✓ all runs |
| M3 ≥ 13/15 | ✓ all runs (hand-reviewed) |
| M4 = 7/7 | Opus ✓. Sonnet 5/7 under v0.1; 7/7, 7/7, 6/7 under v0.2 (fitted) |
| M5 stable | Geometry ✓ (collision Jaccard 1.0). Ambiguity ✗ (0.091 under v0.1, 0.6 under v0.2) |

**Conditional pass.** Faithfulness, the contract, retention and the collision geometry hold across models and runs. Ambiguity handling does not yet: the v0.2 fixes exist but are unvalidated. **ND-1b decides:** new conversations, engine v0.2 and prompt v1 frozen, whole-word probe scoring.
