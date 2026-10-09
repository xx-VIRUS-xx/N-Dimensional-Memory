# N-D closeout (2026-10-09)

**Status: closed as a negative result on a 509-turn conversation.** Phase 4 (consolidation) is not built and will not be. The scale test below is the only experiment that could reopen it.

## The question
Does an external memory made of typed, linked events (N-Dimensional Memory) answer questions about a long conversation better than searching the raw turns, and nearly as well as reading all of them?

## What was measured
All on LoCoMo conv-49 (Evan and Sam, 509 turns, about 11.5k to 15k words), Sonnet answering, author scoring by hand with arm labels hidden, specs and thresholds frozen before each run.

| Experiment | Memory | Result (of 40) | Verdict |
|---|---|---|---|
| ND-3 | engine v0.3 depiction in the prompt | DEPICT 28.5, RAG 28.5, RAW 32.5 | fail: tie with BM25, 87.7% of RAW |
| ND-Q | query tools over the same memory | TOOLS 26.5, RAGTOOL 31.0, RAG 28.5, RAW 32.5 | fail |
| ND-E | new extraction: one event per sentence, open relation types, links decided in code (509/509 parsed, 39 types) | M1 to M5 pass; M6 18% and M7 87% fail | store works; its keys do not separate evidence well |
| ND-Q2 | query tools over ND-E + time-cue resolver, fresh 40 questions | TOOLS2 29.0, RAGTOOL 29.5, STRUCT 29.0, RAW 32.5 | fail: R1 29.0 vs 31.5, R2 89.2% vs 90% |

## What held across all of them
- Structure never beat BM25 over the turns, and never reached 90% of reading everything. Three designs, same shape of result.
- It helped on dated questions (ND-3 temporal 7/7; ND-Q2 category 2 best arm, 5.0 of 7) and on false-premise questions in ND-3 (7 vs RAW 5 of 8). In ND-Q2 all four arms were perfect on premise questions, so that edge did not replicate.
- It hurt on questions that need many events or words the question does not use. Most misses were retrieval misses (9 of 12 for TOOLS2), not reasoning errors.
- Cost per question was low (about $0.04, 2 to 3 calls, 340 words read), but reading all 11.5k words is cheap enough that cost does not decide this size.

## Limits of the evidence
One conversation, one extractor model (Haiku), one answering model (Sonnet), 40 questions per test (bootstrap interval for TOOLS2 minus RAGTOOL: -4.5 to +3.5), one scorer, no replication. Trace recall moved by up to 6 of 82 events between identical runs.

## What this does not show
Nothing here tests the setting the design is for: conversations or corpora too large to read whole. At 11.5k words RAW wins by default. The result says the layer does not help at this size; it does not say it fails at 500k words.

## What would reopen it
A pre-registered scale test (ND-Q2 harness and scorer reused as they are): a set of conversations long enough that RAW no longer fits, fresh questions, same frozen arms, same pass rule. Only if that shows TOOLS2 above RAGTOOL by the R1 margin would Phase 4 (alias layer, role-family unification) be worth building.

## What is reusable
- `tools/extract_events.py`: sequential per-sentence extraction with registry, strict validation, retries, resume.
- `engine/ndq2_tools.py` and `ndq2_mcp.py`: deterministic query tools and an MCP server, including a closed-grammar relative-time resolver (tested, with mutation checks).
- `tools/ndq2_run.py`, `tools/ndq2_score.py`: isolated per-question runs, call-limit enforcement, code-built blind sheet, pre-registered decision rule, trace evidence recall.
- The method: freeze spec and hashes first, hand-score blind, report failed pass rules as failed, keep deviations on record.

## Pointers
`ND-Q2/REPORT.md` (latest result and failure analysis), `ND-3/REPORT.md`, `ND-Q/REPORT.md`, `ND-E/AMENDMENT-1.md` to `AMENDMENT-7.md`, `ND-Q2/AMENDMENT-1.md`, `STATUS.md`.
