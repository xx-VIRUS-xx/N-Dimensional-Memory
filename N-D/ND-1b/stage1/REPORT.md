# ND-1b stage 1: Haiku on LoCoMo conversation 0, sessions 1–3

**Runs:** Haiku runs 1–2 (58 turns each). Probes on Haiku run 1 only (B3); the RAW baseline has Sonnet read the 58 original turns; Sonnet also answers from memory. Engine v0.2.1 (rules frozen). All 50 answers were hand-scored against LoCoMo's gold answers (`m3_review.json`).

## Results against the frozen targets

| Metric | Target | Result | |
|---|---|---|---|
| M1 contract | 0 in every run | Run 1: 0. Run 2: 1 (an entity with no dimensions) | ✗ |
| M2a / M2b | ≥ 0.95 / 0 | 0.968, 0.973 / 0, 0 | ✓ |
| M3 memory vs RAW | ≥ 90% of RAW | **16 / 21 = 76%** | ✗ |
| M5 collision stability (participants excluded) | ≥ 0.8 | **0.221** | ✗ |
| Memory size vs source | reported | 4,030 vs 1,910 words (2.1×) | — |

**Verdict: stage 1 fails. Per B3, stages 2–3 are not run.** The causes are specific and diagnosable, below.

## M3 by question type

| Type | Memory | RAW |
|---|---|---|
| Temporal ("when…?", 7) | **1** | 7 |
| All other questions (18) | **15** | 14 |
| of which adversarial, false premise (5) | **4** | 3 |

**The memory's whole deficit is temporal.** On everything else it matches or beats reading the raw conversation, and it handles swapped-speaker traps better than raw (4 vs 3). This is the attribution property N-D is designed for; small sample, but in the right direction.

## Causes, from the data

1. **Dates never reach memory. This is an implementation gap, not a design failure.** Turn dates were given to the extractor (B1), but engine v0 stores no world time and the depiction shows only ticks. So "yesterday (t2)" can't become 7 May 2023. The two-clock design (CONTRACT C4) is specified but was never built into the engine. Every temporal miss traces to this.
2. **Identity drifts between runs (M5 = 0.22).** The two Haiku runs share only **48%** of their pegs. Much of the gap is mechanical: "that lake sunrise" vs "lake sunrise", "my kids" vs "kids", "adoption agency" vs "adoption agencies". Normalisation strips only "the/a/an", not "that/this/my/our" or plurals. The rest is granularity: one run extracts abstract nouns ("love", "courage", "empathy"), the other doesn't. Both break collisions.
3. **Dialogue meaning spans turns.** "How long have you been married?" → "5 years already!" is one fact split across two turns. A stateless extractor sees only the answer, so the marriage duration was lost (q19). The pilot's narrated sentences never exposed this.
4. **Memory is larger than the source,** mostly label noise, which the depiction layer (ND-3) must fix.

## What this does and doesn't show

- It **does not** show that N-D memory is worse than raw for facts: 15/18 vs 14/18 on non-temporal questions.
- It **does** show that on real dialogue, the engine as built can't answer time questions, and that its geometry is unstable across runs. The pilot's perfect stability came from short, clean, narrated sentences.
- **Limits:** one conversation chunk; probes on one run; one answering model; the gold has known errors (q05).

## Proposed next step (ND-1c)

The spec is to be frozen before it runs, on a **different LoCoMo conversation** so the fixes are tested out of sample:

- **Engine v0.3:** build the second clock (store each turn's date as the event's occurred time, and render it); normalise determiners, possessives and plurals in peg identity.
- **Contract:** give the interpreter the previous turn as read-only context (a decision for the project owner; see below).
