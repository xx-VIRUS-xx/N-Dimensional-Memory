# ND-0 — Baseline: free-dimension extraction under the N-D math

**Status:** complete (2026-09-28).

## Question

If an LLM extracts entities and invents its own dimension names per event (the free-dimension style), does the result support the N-D geometry: collisions, trajectories, state interactions?

## Data

- `data/pilot10.source.jsonl`: 10 sentences from a design discussion (PostgreSQL, Redis, three speakers). **Reconstructed from the extraction; replace with the original sentences if they differ.**
- `data/pilot10.babytest.jsonl`: the free-dimension extraction of those sentences (entity → free dimension → free-text value).

Reference point: `../ND-1/gold/pilot10.gold.jsonl`, 16 hand-built event-star events for the same sentences (the gold ceiling).

## Method

`python tools/ndm_math.py <file>` builds the peg-by-event incidence matrix B and reports shape, geometry and epistemic metrics. Nothing else is computed.

## Results

| Metric | Free-dimension baseline | Event-star gold (ceiling) |
|---|---:|---:|
| Events | 10 | 16 (compound sentences split) |
| Role strings | 180 | 48 |
| Distinct dimensions | 102 | 25 (all from catalog) |
| Values that are pegs | 16.1% | 81.2% |
| Mean words per value | 3.9 | 1.5 |
| Single-event pegs | 76.9% | 50.0% |
| Colliding event pairs | 24 | 49 |
| Storyline ranks (Alice~PostgreSQL, Carol~Redis) | 1, 2 | 1, 2 |
| Referent buckets | 4 flagged (2 real, 1 absence, 1 duplicate) | 3 (t4 scope, t5 "its", t6 "the change") |
| Stored absences | 21 | 0 |
| Inference markers inside facts | 4 | 0 |

## Findings

1. **Entity identification is good enough.** Both formats recover the two storylines at ranks 1 and 2 by weighted collision alone.
2. **Free dimensions break the rest.** Values are sentences (16% pegs), so values never collide; 21 stored absences and 4 inferences are noise the contract forbids.
3. **Dimension count per role string is not the right metric at this size.** Gold still has 25 dimensions for 48 strings; the difference is that gold's are catalog names that will repeat as the corpus grows. ND-1 therefore measures catalog compliance, not singleton rate.
4. **The free-dimension extractor missed one bucket** (t6 "the rate-limiting change") and asserted one false conflict (Bob vs Carol "different preferences", no shared dimension).

## Decision

Free-dimension extraction is rejected as the N-D write format. ND-1 tests whether LLMs can produce the event-star shape directly, scored against the gold.
