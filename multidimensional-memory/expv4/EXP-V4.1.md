# EXP-V4.1: Evolving State & Contradiction Preservation

## Question

> Can the temporal substrate preserve an entity's entire state history and detect opposing state observations without overwriting or automatically resolving them?

## Principle

A memory system should not mutate history merely because a later observation differs from an earlier one.

```text
state A
  ↓
state B
  ↓
state C
```

All three remain evidence. A contradiction may actually be a legitimate transition.

## Rules

1. State history is append-only.
2. Opposing states are retained rather than overwritten.
3. A later observation does not automatically invalidate an earlier observation.
4. Contradiction detection is deterministic and evidence-backed.
5. The system records `preserve_both` rather than selecting a winner.
6. Absolute dates are never invented.
7. No LLM, embeddings, vector database, or graph database is used.

## Example

```text
Rahul started playing football.
        ↓
playing = active

Rahul stopped playing football.
        ↓
playing = inactive

Rahul resumed playing football.
        ↓
playing = active
```

The resulting memory is a history, not a single mutable value.

## Run

```bash
cd /mnt/data/expv4
python -m src.run_v41
pytest -q
```
