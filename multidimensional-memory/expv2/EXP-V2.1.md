# EXP-V2.1: Canonical Point Identity

## Goal

EXP-V2 established that multiple agents expose a stable semantic core while disagreeing on enrichment. EXP-V2.1 tests the next necessary layer:

> Can we distinguish equivalent points from related-but-different points without using an LLM, embeddings, or a vector database?

## Identity classes

### SAME
Two observations refer to the same canonical point after transparent normalization.

Example:

```text
plays
playing
play
```

### RELATED
Two observations should remain separate because one is more specific, qualified, or granular than the other, but they describe compatible concepts.

Example:

```text
play
play football
```

They should not be collapsed. The relationship itself is useful information.

### DISTINCT
There is not enough deterministic evidence to treat the observations as the same or related.

## Pipeline

```text
Claude / Codex / Copilot
          |
          v
  normalized observations
          |
          v
     point identity
      /    |     \
   SAME RELATED DISTINCT
      \    |     /
          v
 canonical substrate
          |
          v
   candidate relations
```

## Important rule

**Do not optimize for fewer points.** If collapsing two points destroys granularity, the algorithm must keep them separate.

## Run

```bash
cd /mnt/data/expv2
python -m src.run_v21
pytest -q
```

## Expected observation

For the existing Conversation 01 data, the algorithm should preserve `play` and `play football` as related rather than forcing them into a single point. It should also merge morphological variants such as `plays` and `playing` when their normalized surface and dimensions support equivalence.

## EXP-V2.2 trigger

If identity matching behaves correctly across a larger dataset, the next experiment is to derive relationship candidates from canonical points and their temporal evidence.
