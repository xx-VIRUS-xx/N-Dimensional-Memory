# EXP-V3.1: Evidence-Constrained Relationships

## Question

> Can deterministic relationship candidates be made more precise by enforcing semantic-role constraints and requiring local evidence, without another model call?

## Changes from EXP-V3

EXP-V3 exposed false positives caused by broad dimension co-occurrence. EXP-V3.1 adds conservative constraints:

1. Emotion/feeling/intent-only verbs are not generic actions.
2. Actor -> time/place requires shared evidence.
3. Transition markers must occur in the event surface itself.
4. Lexical containment may strengthen an action -> object candidate, but never merges points.
5. Every candidate retains provenance and remains a candidate, never a fact.

## Run

```bash
cd /mnt/data/expv3
python -m src.run_v31
pytest -q
```
