# ND-Q2 report: does an LLM-planned query over the ND-E memory beat searching raw turns?

Run 2026-10-09, spec `EXP-NDQ2.md` + `AMENDMENT-1.md` (frozen before the draw). Memory: ND-E run 6 (509 events, 1822 relations, 39 types) joined to the source for speaker, listener and date. Test set: 40 fresh conv-49 questions (seed 11, disjoint from the 40 dev questions; 15 / 8 / 8 / 7 / 2 by category 4 / 1 / 5 / 2 / 3). Sonnet answered, one isolated session per question. Hand scores C = 1, P = 0.5, W = 0 against LoCoMo gold, arm labels hidden by a code-built random order; scores read from the author's marks in `sheet.md` and applied through `key.json` in code (`results/`).

## Result: the pass rule FAILS (R1 and R2 both short)

| Arm | Points /40 | Cat 1 /8 | Cat 2 /7 | Cat 3 /2 | Cat 4 /15 | Cat 5 /8 |
|---|---|---|---|---|---|---|
| RAW (all 509 turns, ~11.5k words) | 32.5 | 6.0 | 4.5 | 2.0 | 12.0 | 8.0 |
| RAGTOOL (search_turns only) | 29.5 | 5.5 | 3.5 | 1.0 | 11.5 | 8.0 |
| STRUCT (structured tools, no text search) | 29.0 | 6.0 | 3.0 | 2.0 | 10.0 | 8.0 |
| TOOLS2 (structured tools + search_turns) | 29.0 | 4.0 | 5.0 | 1.0 | 11.0 | 8.0 |

| Rule | Threshold | Observed | Verdict |
|---|---|---|---|
| R1 TOOLS2 >= RAGTOOL + 2.0 | 31.5 | 29.0 | FAIL |
| R2 TOOLS2 >= 90% of RAW | 29.25 | 29.0 (89.2%) | FAIL |
| R3 trace recall >= 0.80 (reported) | 0.80 | TOOLS2 0.617, RAGTOOL 0.599, STRUCT 0.492 | no |
| R5 median <= 10 calls and <= 1,500 words (reported) | | TOOLS2 2 calls, 192 words | yes |

Uncertainty: 40 questions. Bootstrap 95% interval for TOOLS2 minus RAGTOOL: -0.5 points [-4.5, +3.5]; TOOLS2 minus RAW: -3.5 [-9.0, +1.5]. The test cannot rule out a gain of up to 3.5 points, nor a loss of 4.5. It does show that no gain of the size set in R1 appeared. Dev-set pilot rounds showed that trace recall moves by up to 6 events of 82 between identical runs.

Sensitivity: q04 (gold "every three months") is marked C for all four arms although each answer says the frequency is not in memory. Scoring those four as W gives RAW 28.5, RAGTOOL 25.5, STRUCT 25.0, TOOLS2 25.0; R1 (25.0 vs 27.5) and R2 (87.7%) still fail.

## What the data says
1. **Structure did not beat search.** TOOLS2 beat RAGTOOL on 2 questions (q01, q11) and lost on 4 (q05, q13, q16, q19). STRUCT and TOOLS2 tie (3 questions each way). The combination is not better than either part.
2. **Where structure helped: time.** TOOLS2 is the best arm on category 2 (5.0 of 7; RAW 4.5, RAGTOOL 3.5, STRUCT 3.0). Resolved time cues and the from/to filter did what they were built for.
3. **Where it hurt: multi-event questions (category 1).** TOOLS2 scored 4.0 of 8 against RAW 6.0. These need several events; one tool result is capped at 250 words and the model usually stops after 2 to 3 calls.
4. **Failures are mostly retrieval, not reasoning.** Of the 12 categories 1 to 4 answers TOOLS2 did not get fully right, 9 missed part of the gold evidence in every tool result (STRUCT 11 of 12, RAGTOOL 11 of 13). Three TOOLS2 answers had the evidence in view and still failed (q09, q21, q25). Recall of the structured arms is no better than BM25 on turns (0.62 against 0.60; STRUCT 0.49).
5. **The model mostly searches.** TOOLS2 called search_turns 50 times, find 30, neighbors 13, values 3, event 3, catalog 2, count 0. STRUCT, without search, called find 104 times and recall fell to 0.49.
6. **Adversarial questions (category 5): all four arms 8 of 8.**
7. **Cost.** Per question: TOOLS2 2.5 calls, 341 words read, $0.039, 9 s; RAGTOOL 2.7 calls, 377 words, $0.036, 8 s; STRUCT 3.0 calls, 388 words, $0.041, 10 s. RAW reads about 11,450 words every time. At this corpus size reading everything is cheap, which is why the retrieval arms cannot win on cost here; this test does not probe the case where the corpus no longer fits in context.

## Deviations and notes (none changes the verdict)
- The author scored in `sheet.md` (letters at the end of each answer); the uploaded `scores.json` was the empty template. The scores were parsed by code (160 of 160 valid).
- The author annotated gold answers for the category 5 questions and q30 in the sheet (for example "No painting with bird mentioned"); the same annotated gold applied to every arm.
- TOOLS2 on q12 made an 11th call; the server refused it with the call-limit error, as designed (one `over_call_limit` flag in `tools2.meta.json`).
- Trace recall was computed after scoring from a local redraw of the test set (same seed and exclude file; question text checked equal to the sheet), because `probes.jsonl` was not sent.
- ND-Q (v1) numbers (TOOLS 26.5, RAGTOOL 31.0, RAW 32.5 on the 40 ND-3 questions) are on a different question set and are not compared with these.

## Reading
On this memory, with these tools, an LLM that plans queries over the ND-E extraction did about as well as an LLM that searches the raw turns (29.0 against 29.5) and did not reach 90% of reading everything (89.2%). The structured layer earned its keep on dated questions and lost on questions that need many events or words the question does not use. The extraction itself (Phase 2) did not make retrieval better than BM25.

Not supported by this experiment: that the structured memory improves answers over raw-turn search on a 509-turn conversation. Not tested: behaviour on corpora too large to read whole, and any consolidation or alias layer (Phase 4).

## Options (not decided)
1. Stop here and write ND up as a negative result with the measured wins (time questions, adversarial handling, cheap per-question reads) and the failure analysis above.
2. A targeted follow-up on the two failure modes (multi-event questions, vocabulary mismatch), pre-registered, on questions not yet used (113 conv-49 questions remain; the 40 test questions are now spent for tuning).
3. A scale test: a much longer conversation set where RAW no longer fits, which is the case the structure was meant for.
