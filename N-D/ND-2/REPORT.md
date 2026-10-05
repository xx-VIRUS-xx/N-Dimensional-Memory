# ND-2 report: N-D depiction vs flat memory vs raw conversation

**Held-out data:** LoCoMo conv-30 (Jon and Gina), sessions 1–3: 58 turns, 33 benchmark questions, never seen during development. **Extraction:** one Haiku run, prompt v2: 0 parser retries, M1 ok, M2a 0.955, M2b 0. **Engine** v0.3, **depiction** v1, both frozen. **Answering model:** Sonnet, one isolated call per question. All 99 answers were hand-scored against LoCoMo gold (`heldout/review.json`). The development run on conv-26 was skipped (optional; not part of the verdict).

## Results

| Condition | Score (of 33) | Mean context (words) |
|---|---|---|
| RAW conversation | 26.0 | 1,734 |
| FLAT memory dump | **27.0** | 4,080 |
| N-D DEPICTION | 24.0 | **571** |

| Pre-registered criterion | Result | |
|---|---|---|
| D1: DEPICT ≥ 90% of RAW accuracy | 24 / 26 = **92%** | ✓ |
| D2: DEPICT context ≤ 50% of RAW | 571 / 1,734 = **33%** | ✓ |
| D3: DEPICT vs FLAT (reported) | 24 vs 27; **DEPICT is worse** | — |

| Subset | DEPICT | RAW | FLAT |
|---|---|---|---|
| Temporal (5) | **5.0** | 4.5 | 4.5 |
| Adversarial, false premise (9) | 6.0 | 5.5 | **9.0** |
| Other (19) | 13.0 | 16.0 | 13.5 |

## Verdict: pass by the pre-registered rule, with an important qualifier

**The depiction keeps 92% of the raw conversation's accuracy using a third of the words.** By the rule frozen before the run, ND-2 passes.

**But the depiction is not the best memory view.** The flat dump of the same memory scored highest of all (27, against RAW's 26), at 2.4× the raw size and 7× the depiction's. So **the engine's memory itself is now as good as the raw conversation, or better.** What the depiction adds is compression, not accuracy; it currently loses about 3 questions doing so.

## What the results show

1. **The time fix works.** With dates on every event (engine v0.3), memory answers every temporal question (DEPICT 5/5). In ND-1b, before the fix, it answered 1/7.
2. **Memory beats raw on false-premise questions.** FLAT got 9/9; RAW got 5.5. Raw reading fell for swapped-speaker traps ("Jon's team performed Finding Freedom", "Jon chose the furniture"); attributed memory did not. This is the attribution property N-D is built for, now shown on held-out data. The sample is small, but the gap is large.
3. **The depiction's losses are fixable.** Of its 7 misses:
   - **2 are selection:** the fact is in memory but wasn't selected.
   - **3 are presentation:** false premises were accepted because the depiction obscured whose event it was.
   - **1 is an unresolved reference.**
   - **1 is a questionable gold answer.**
   No miss came from dates.
4. **Extraction is now clean:** no parser retries were needed, no contract violations, and 95.5% content traceability.

## Limits

- One conversation, one extraction run, one answering model (Claude-only). Differences of 2–3 questions out of 33 are within noise. The claims here are parity and compression, not superiority.
- The depiction design was frozen before this run but was built by someone who had seen conv-26. conv-30 was unseen.

## Next

**Depiction v2,** targeting the two measured weaknesses:

- **Selection:** include the full trajectory of each seed entity before neighbours.
- **Attribution:** lead every line with *who it is about and who said it*, especially for possessions and activities ("Jon's studio: Marley flooring").

Test it frozen, on a **new** held-out conversation, against FLAT as well as RAW, because FLAT is now the bar to beat.
