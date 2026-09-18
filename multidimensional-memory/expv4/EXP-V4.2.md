# EXP-V4.2: Temporal Evolution vs Potential Conflict

## Question

Can temporal ordering distinguish a legitimate state transition from potentially conflicting observations without deleting either observation?

## Core principle

Opposing states are not automatically contradictions. If evidence establishes that one state precedes another, the pair represents evolution.

```text
active --[stopped]--> inactive --[resumed]--> active
```

A conflict candidate is different:

```text
observation A: state = X
observation B: state = not-X

no temporal ordering evidence
        ↓
potential_conflict
        ↓
preserve_both
```

## Rules

1. State history remains append-only.
2. Opposing observations are retained.
3. Explicit temporal ordering takes precedence over naive contradiction detection.
4. Source sequence is weak ordering evidence, not wall-clock truth.
5. A potential conflict is never automatically resolved.
6. No winner is selected.
7. Absolute dates are never invented.
8. No LLM, embeddings, vector DB, or graph DB is used.

## Expected distinction

- `active -> inactive -> active` = evolution.
- `active` and `inactive` with no ordering evidence = potential conflict.
- `active` and `active` = repeated observation, not conflict.

## Run

```bash
cd /mnt/data/expv4
python -m src.run_v42
pytest -q
```
