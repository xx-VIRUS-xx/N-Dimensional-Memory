# ND-3: does N-D help at full conversation length?

**Status:** spec frozen 2026-10-01, before any ND-3 run. Engine v0.3, depiction v2 and prompt v2 are frozen.

## Why

ND-2 showed parity with the raw text at a third of the size, on a 1,734-word chunk short enough for the answering model to read directly. N-D's accuracy claim belongs to long histories, where raw text is long and retrieval has to choose. ND-3 runs at full conversation length and adds the standard alternative, **retrieval at the same word budget**.

## Data

- **LoCoMo conv-49**, all 25 sessions: **509 turns, about 11,450 words**. Never used in development; its questions were not read when designing depiction v2.
- **Questions:** 40 of its 196, stratified by LoCoMo category, seeded (`--probe-sample 40 --seed 7`): 15 × cat 4, 8 × cat 1, 8 × cat 5 (adversarial), 7 × cat 2 (temporal), 2 × cat 3. Hand-scored against LoCoMo gold.
- **Extraction:** one Haiku run, prompt v2 (validated, with retries).

## Conditions (answering model: Sonnet, one isolated `claude -p` call per question)

| Condition | What the model reads | Size |
|---|---|---|
| RAW | All 509 turns, dated | ~15k words (11.5k of dialogue plus dates and speakers) |
| RAG | BM25 top turns, dated, in time order | ≤ 1,000 words |
| DEPICT | N-D depiction v2 | ≤ 1,000 words |
| FLAT (optional) | Whole engine memory, dated | Large; run only if usage allows |

## Depiction v2 (changes from v1, each aimed at a measured ND-2 miss)

1. **Selection:** the full trajectory of every non-speaker entity named in the question first; then scored events; then the preceding turn of each; then collision neighbours.
2. **Attribution:** each line reads "*X* said:", and each fact is labelled with whom it is about, e.g. "(themself)" or "(another person)". The header forbids moving facts between speakers.
3. The unverified "related to" line is removed.
4. Budget: 1,000 words, the same as RAG.

These were designed after reading ND-2's conv-30 answers. conv-30 is therefore development data now; conv-49 is the only held-out data.

## Hypotheses and verdict (hand scores: C = 1, P = 0.5, W = 0)

| ID | Hypothesis | Criterion |
|---|---|---|
| H1 | N-D structure beats standard retrieval at equal size | DEPICT > RAG |
| H2 | N-D stays close to reading everything | DEPICT ≥ 90% of RAW |
| H3 | Attribution: false-premise questions (cat 5, n = 8) | DEPICT ≥ RAW (reported) |
| H4 | Temporal questions (cat 2, n = 7) | Reported for all conditions |

**ND-3 passes if H1 and H2 both hold.** If DEPICT = RAG, H1 fails: equal-size retrieval would do the same job with no engine. Every DEPICT miss is attributed to extraction, selection, presentation, or gold.

**Interpretation limits, stated now:**

- 40 questions, one conversation, one extraction run, Claude-only.
- A difference of 1–2 questions is noise.
- RAW at ~15k words still fits the answering model comfortably. LoCoMo is long, but not long enough to break raw reading. If RAW wins, that is expected at this length, and the comparison that matters is H1.
