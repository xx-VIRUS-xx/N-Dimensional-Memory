# EXP-V4.3: Explicit Temporal Conflict Benchmark

## Question

Can the memory substrate distinguish genuine temporal evolution from contradictory observations when source order alone is insufficient?

## Change from V4.2

V4.2 allowed source sentence order to classify opposing states as evolution. V4.3 treats source order as provenance only. An evolution classification requires explicit temporal evidence such as `later`, `after`, or another temporal constraint.

## Cases

1. **Ordered evolution**: opposing states with explicit temporal ordering.
2. **Unordered conflict**: opposing states with no temporal ordering evidence.
3. **Repeated state**: same state repeated, which is not a conflict.

## Core invariant

```text
opposing observations
        |
        +-- explicit temporal order --> evolution
        |
        +-- no explicit order -------> potential conflict

both observations are preserved
```

## Constraints

- No winner is selected.
- No observation is deleted.
- Source sequence is not treated as wall-clock truth.
- No absolute dates are invented.
- No LLM, embeddings, vector DB, or graph DB are used.
