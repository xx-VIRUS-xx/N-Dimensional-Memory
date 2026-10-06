# ND-Q report: LLM-planned logical query tools vs keyword selection

**Spec:** `EXP-NDQ.md`, frozen 2026-10-06 before any scored run (hashes in `FREEZE.sha256`). **Verdict: ND-Q fails Q1, Q2 and Q3.** Logical tools over the current memory did not beat one-shot retrieval, and did not beat an agent loop that searches raw turns.

## Setup
LoCoMo conv-49 (Evan and Sam), 509 turns, the same 40 ND-3 questions, the same frozen Haiku extraction and engine v0.3 state. Answering model Sonnet, one isolated `claude -p` session per question, at most 10 tool calls. TOOLS = 8 deterministic tools over the engine state (incl. `find_value`). RAGTOOL = same loop, one tool `search_turns` (BM25, top 5 dated turns). RAW, RAG, DEPICT are the ND-3 hand scores, reused. All 80 new answers were hand-scored by the author (C=1, P=0.5, W=0) from a sheet that showed the gold answer and the two answers in shuffled order without arm labels; the key (`results/key.json`) was applied afterwards. Reproduce with `tools/ndq_score.py`.

## Scores (out of 40)
| Arm | Total | Without q17, q25, q30 (/37) | Cat 1 multi-hop (/8) | Cat 2 temporal (/7) | Cat 4 single-hop (/15) | Cat 5 false-premise (/8) |
|---|---|---|---|---|---|---|
| RAW (reused) | 32.5 | 29.5 | 6.0 | 7.0 | 13.5 | 5.0 |
| RAGTOOL | 31.0 | 30.0 | 6.0 | 7.0 | 11.0 | 6.0 |
| RAG (reused) | 28.5 | 28.0 | 4.5 | 6.0 | 10.5 | 6.5 |
| DEPICT (reused) | 28.5 | 28.0 | 3.0 | 7.0 | 10.0 | 7.0 |
| **TOOLS** | **26.5** | **24.5** | 4.5 | 5.0 | 11.5 | 5.0 |

Cat 3 (2 questions): RAW 1.0, RAGTOOL 1.0, RAG 1.0, DEPICT 1.5, TOOLS 0.5.

## Hypotheses
| ID | Criterion | Result | |
|---|---|---|---|
| Q1 | TOOLS >= RAG + 3.0 (>= 31.5) | 26.5 (2.0 below RAG) | FAIL |
| Q2 | TOOLS >= RAGTOOL + 2.0 | 26.5 vs 31.0 (4.5 below) | FAIL |
| Q3 | TOOLS >= 90% of RAW (>= 29.25) | 81.5% | FAIL |
| Q4 | reported | table above | - |
| Q5 | median <= 10 calls and <= 1,500 words | TOOLS 3 calls, 220 words; RAGTOOL 2 calls, 303 words; 0 call errors, 0 over limit in both | PASS |

Pass rule needs Q1 and Q3, so the confirmation set (40 fresh conv-49 questions) was not run.

Per question, RAGTOOL beat TOOLS on 8 (q06, q07, q08, q09, q11, q15, q19, q33) and TOOLS beat RAGTOOL on 2 (q13, q25); exact sign test on 2 vs 8, two-sided p = 0.11. The direction is consistent; with 40 questions it is not conclusive on its own.

## Evidence recall (TOOLS only)
Share of gold evidence turns whose tick appeared in any TOOLS result: mean per question 0.68 (41 of 82 pooled). By category: cat 1 0.42, cat 2 0.86, cat 4 0.80, cat 5 0.62. Questions with every evidence turn seen averaged 0.86 (25 questions); the rest averaged 0.33 (15). RAGTOOL recall was not computed (its traces were not part of the analysis). The spec's reference values (BM25 0.76, depiction 0.69) may use a different aggregate, so no comparison is claimed.

## Why TOOLS lost (from the traces; mechanism, not a controlled test)
1. **Relative time was stored but never shown or resolved.** q06 (gold: first week of June 2023): event t39 holds `Evan.temporal_position = last week`, but `find_value` printed only the matching string (`Evan.action = had health scare ...`), the model never opened the full event, and answered with the day it was said (6 Jun). q15 (gold 5 Jan 2024): t432 holds `Evan.temporal_position = yesterday`, again not shown by `find_value`. The tools also filter dates on the day a turn was said, so a cue like `last month` (q23, t162, said 19 Aug) can never match a July filter. A check of the 41 turns with a regex-detected cue found a stored `temporal_position` at 40 of them, so extraction is not the cause; the tool output and missing date resolution are. (A first version of this report wrongly said the cues had been dropped at extraction; corrected 2026-10-07 after reading the events.)
2. **Free-text values do not share words with the question.** q07 (gold: soda, candy): the model searched "snack", never reached "soda" or "candy". `find_value` is exact lexical matching, so the keyword problem moved inside it.
3. **Zero evidence reached the model on 9 questions** (q04, q07, q12, q17, q20, q23, q33, q34, q36). Most are missing or differently worded values, not wrong tool choices.

The calls per question fell and no tool misuse showed up (0 call errors); the failures sit in what the memory stored, which is the storage-format suspect named in the spec.

## Caveats
- One scorer, one run per question, one conversation, 40 questions, Claude only. The primary 40 are not held out; the confirmation set that would have addressed that was not run.
- The blind sheet was built by an assistant that had read both arms' answers before building it; the scoring itself was done by the author from the sheet only.
- The ND-3 "extraction ceiling" labels (q17, q25, q30) look wrong: TOOLS answered q25 and q30 correctly, so that information was in memory. Both columns are reported.
- `find_value` was added after a 3-question unscored conv-30 pilot, before the freeze (spec amendment). It narrows the gap between TOOLS and keyword search; the result above includes it.
- The pilots (`pilot/`, `pilot2/`) are unscored harness checks on development data.

## What this does and does not show
It shows that, on this memory, deterministic query tools gave an LLM no advantage over searching raw turns, and that the loss traces to what extraction stored (values phrased in free text, pronouns left unresolved) and in what the tools display (stored time cues were not shown or resolved). It does not show that structured queries cannot help; it shows they were limited by the 19-dimension free-text storage they ran on. The next experiment named in the spec is a paper test of the entity-to-entity storage format with one-word values (the 14 ND-3 misses plus 10 correct answers, written in that format and as queries, no LLM), with relative time kept as stored text.
