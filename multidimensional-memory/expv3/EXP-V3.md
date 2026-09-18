# EXP-V3: Deterministic Relationship Candidates

## Question

> Can canonical points from EXP-V2.1 produce useful relationship candidates using only their dimensions, evidence, identity links, and explicit temporal/state markers?

## Why this experiment

EXP-V2.1 established point identity while deliberately deferring relationships. EXP-V3 tests the next layer without allowing another model to invent the graph.

```text
Claude / Codex / Copilot
          |
          v
     EXP-V2.1 points
          |
          v
 deterministic rules
          |
          v
 candidate relations
```

## Candidate relation types

- `performs`: actor/subject -> action/verb in shared evidence
- `acts_on`: action/verb -> object/target/activity/instrument in shared evidence
- `contextualized_by`: actor/subject -> place/time in shared evidence
- `granularity_related`: inherited from EXP-V2.1 RELATED identity
- `temporal_context`: event/state -> explicit time point
- `state_transition_*`: transition marker -> event/state candidate

## Non-goals

This experiment does not:

- assert that a candidate relation is a fact
- resolve ambiguity
- use an LLM
- use embeddings
- use a vector database
- use a graph database

## Run

```bash
cd /mnt/data/expv3
python -m src.run_v3
pytest -q
```

## Success criterion

The system should create explainable candidate edges from canonical points while preserving provenance and avoiding unsupported edges when evidence is absent.
