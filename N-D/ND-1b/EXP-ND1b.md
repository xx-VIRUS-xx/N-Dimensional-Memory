# ND-1b: does the frozen engine hold on external dialogue?

**Status:** spec frozen 2026-09-30, before any run.

## Question

With engine v0.2 and prompt v1 frozen (plus dialogue metadata, B1), do faithfulness, the contract, fact retention and collision stability from ND-1 hold on external, naturally written dialogue that neither the engine rules nor the probes were written for?

## Data (Part A)

- **LoCoMo** (Maharana et al., ACL 2024), `snap-research/locomo` at commit `3eb6f2c5`, `data/locomo10.json`, SHA-256 `79fa87e9…ea698ff4`. CC BY-NC 4.0.
- **Chunk:** conversation 0 (`conv-26`, Caroline and Melanie), sessions 1–3: **58 turns**. Cut with `tools/locomo_chunk.py`, which verifies the SHA-256. The raw chunk is **not committed**; regenerate it with the script.
- **Probes:** the **25 LoCoMo questions** whose evidence turns all lie inside the chunk, with LoCoMo's gold answers. By LoCoMo category: 9 × cat 4, 7 × cat 2 (temporal), 5 × cat 5 (adversarial), 3 × cat 1, 1 × cat 3. Only cat 2 (temporal, "When did…") and cat 5 (adversarial, with `adversarial_answer`) are labelled here from inspection; other category names are not asserted. An independent audit reports errors in LoCoMo gold answers, so disputed items are checked by hand.

**Part B (ambiguity stability) is deferred.** LoCoMo is casual chat with few unresolved references or stated alternatives, so ND-1b does **not** settle the ambiguity question that ND-1 left open. That needs its own slice (TANGLE or items written before extraction).

## Protocol

| Item | Setting |
|---|---|
| Engine | v0.2, frozen (no rule changes during ND-1b) |
| Prompt | v1 plus B1 turn metadata: speaker, listener and date are given; "I" resolves to the speaker, "you" to the listener |
| Extractors | Claude Code `claude -p`: **Haiku × 3, Sonnet × 2** (290 calls; trimmed for usage limits; A6 applies: Claude-only) |
| Answering model | Sonnet, one isolated call per probe |
| Baseline | **RAW**: the same answering model reads the 58 original turns instead of engine memory |

## Metrics and targets

| ID | Metric | Target (from ND-1, "hold within 10%") |
|---|---|---|
| M1 | Contract violations | 0 |
| M2a / M2b | Content traceability; label-introduced pegs | ≥ 0.95; 0 (names and dates from turn metadata count as traceable, B1) |
| M3 | Probe accuracy, **hand-reviewed**, per run and per LoCoMo category | N-D memory ≥ 90% of the RAW baseline's hand-reviewed score |
| M5 | Collision stability (minimum pairwise Jaccard) **excluding the two participants as hub pegs** (B2) | ≥ 0.8 |
| M5b | Bucket-outcome stability | Reported only (Part B deferred) |
| — | Memory size vs source (words) | Reported |

**Adversarial probes (cat 5)** are correct when the answer rejects or corrects the false premise (usually a swapped speaker), not when it repeats `adversarial_answer`. These probes directly test attribution.

## Amendments made before any run

- **B1: Dialogue metadata.** Each turn's speaker, listener and date are passed to the stateless extractor. The metadata is part of the input, so names and dates from it count as traceable in M2.
- **B2: Hub pegs.** In a two-person dialogue both participants touch nearly every event (the pipeline test found 1,418 of 1,653 pairs colliding), so raw collision stability is trivially 1.0. M5 therefore excludes participants' pegs.

- **B3: Staged runs (usage limits, before any scoring).** Stage 1: Haiku runs 1–2, with probes on Haiku run 1 plus the RAW baseline. Stage 2: Haiku run 3, no probes. Stage 3: Sonnet × 1, with probes. Probes run on one extraction per model, because stability (M5) is measured from collision structure and needs no probes, and ND-1 showed M3 varies by at most one question across runs. If Stage 1 fails the M3 target, stages 2–3 are not run.
- **B4: Engine v0.2.1.** Input validation only. Malformed extractor output (an entity without a name or without dimensions) is recorded as an M1 contract violation instead of crashing the engine. No rules changed; the pilot results reproduce exactly.

## Falsification

ND-1b **fails** if any of these holds:

- M2a < 0.95 or M1 > 0 in any run
- N-D memory's M3 < 90% of RAW
- M5 < 0.8

A failure is attributed to extraction or engine per item, as in ND-1.
