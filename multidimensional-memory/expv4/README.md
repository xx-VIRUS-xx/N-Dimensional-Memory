# EXP-V4

Temporal and evolving memory experiments.

## Versions

- **V4**: extracts conservative temporal anchors, events, ordering evidence, and state transitions.
- **V4.1**: preserves append-only state histories and detects opposing state transitions.
- **V4.2**: distinguishes temporal evolution from potentially conflicting observations.
- **V4.3**: introduces a contradiction benchmark and tightens the rule so source sequence alone cannot prove evolution.

## Run V4.3

```bash
cd /mnt/data/expv4
python -m src.run_v43
pytest -q
```

## Principle

```text
observation
    ↓
event
    ↓
temporal evidence
    ↓
state comparison
    ↓
 evolution OR potential conflict
    ↓
preserve all evidence
```
