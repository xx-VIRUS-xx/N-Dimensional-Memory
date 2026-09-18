# EXP-V4: Temporal & Evolving Memory

## Question

> Can the canonical substrate preserve temporal context and evolving state without inventing absolute dates or collapsing uncertainty?

## Why V4

V3/V3.1 established deterministic relationship candidates. V4 adds a temporal layer while keeping the same conservative policy: observations and state changes are appended, relative time stays relative, and source order is treated as weak evidence unless the text explicitly says `after` or `before`.

## Design

```text
canonical substrate
       ↓
source evidence
       ↓
temporal anchors
       ↓
events
       ↓
ordering constraints
       ↓
append-only state history
```

### Rules

1. No absolute date is invented.
2. `yesterday`, `tomorrow`, `next month`, `summer`, etc. remain relative/seasonal anchors.
3. Conversation/source order is weak temporal evidence, not a wall-clock assertion.
4. Explicit `after`/`before` creates a stronger local ordering constraint.
5. State transitions are preserved as history, never overwritten.
6. Relationships remain evidence-backed; V4 does not turn candidates into facts.
7. No LLM, embeddings, vector database, or graph database is used.

## Run

```bash
cd /mnt/data/expv4
python -m src.run_v4
pytest -q
```
