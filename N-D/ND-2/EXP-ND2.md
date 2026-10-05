# ND-2: does the N-D depiction beat a flat memory dump and match the raw conversation?

**Status:** spec frozen 2026-10-01, before any ND-2 run. **Result: pass** (D1 92%, D2 33%), with the qualifier that FLAT scored highest; see `REPORT.md`.

## Why

Everything tested until now was ingestion plus a **flat dump** of memory. ND-1b stage 1 showed that dump losing to the raw conversation on time questions (1/7 vs 7/7), while matching it on facts (15/18 vs 14/18). The dump is also 2.1× larger than the source. The core N-D claim is about the **depiction**: selected, dated, linked, compact. ND-2 tests that claim directly.

## Conditions (same answering model: Sonnet via `claude -p`, one isolated call per question)

| Condition | What the model reads |
|---|---|
| RAW | The original turns, with dates and speakers |
| FLAT | The whole engine memory, v0.3, dated (`probe_harness batch`) |
| DEPICT | The N-D depiction for that question (`probe_harness depict`; `engine/depict.py`, budget 700 words) |

## Data

- **Development (not decisive):** LoCoMo conv-26, sessions 1–3; the existing Haiku run 1 extraction (prompt v1), re-scored with engine v0.3. RAW is reused from ND-1b stage 1. This data informed the v0.3 fixes, so its result is reported but **not used for the verdict**.
- **Held-out (decisive):** LoCoMo **conv-30** (Jon and Gina), sessions 1–3: 58 turns and its benchmark questions whose evidence lies in those sessions. Never looked at during development. **One fresh Haiku extraction** with prompt v2 (below).

## Changes since ND-1b (all made before ND-2)

- **Prompt v2 and parser:** every entity must have `name`, `type` and at least one dimension, and the speaker must be present. Invalid output is rejected and retried with the parser's error list, up to 3 retries. Retries are recorded per turn in `.meta.json`.
- **Engine v0.3:**
  - each event carries the date its turn was said (the second clock, CONTRACT C4)
  - peg identity ignores case, punctuation, plain determiners ("the", "that") and plurals
  - "my/our" resolve to the speaker and "your" to the listener, so "my family" (Melanie's) ≠ "a family"
  - the pilot results are unchanged
- **Depiction v1:**
  - seeds from the question
  - event scoring
  - the preceding turn of each selected turn (dialogue adjacency; this keeps extraction stateless)
  - collision neighbours
  - related entities
  - open buckets and non-fact statuses
  - labels hidden
  - a 700-word budget

## Metrics (hand-scored against LoCoMo gold: C = 1, P = 0.5, W = 0)

| ID | Metric | Target (held-out) |
|---|---|---|
| D1 | DEPICT accuracy vs RAW | ≥ 90% of RAW |
| D2 | DEPICT mean context size vs RAW | ≤ 50% of RAW's words |
| D3 | DEPICT vs FLAT | Reported (expected: DEPICT ≥ FLAT) |
| D4 | Temporal subset (LoCoMo category 2), DEPICT vs RAW | Reported |
| D5 | Adversarial subset (category 5), DEPICT vs RAW | Reported |
| — | Extraction contract (M1), traceability (M2a/M2b), parser retries | Reported |

## Verdict rule

ND-2 **passes** if D1 and D2 both hold on the held-out conversation. If D1 fails, each DEPICT miss is attributed to one of four causes:

- **extraction:** the fact isn't in memory
- **selection:** the fact is in memory but not in the depiction
- **presentation:** the fact is in the depiction but misread
- **gold:** the benchmark answer is wrong

Selection and presentation misses are depiction work; extraction misses are contract work.

## Cost

Held-out: 58 extraction calls (plus retries), then RAW, FLAT and DEPICT at about 33 questions each. Development: FLAT and DEPICT at 25 each. About 250 calls in total.
