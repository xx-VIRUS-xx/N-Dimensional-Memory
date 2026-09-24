# EXP-V8 NDM Adapter

Initial implementation for testing N-Dimensional Memory before competitor comparison.

## Principle

`source context -> NDM writer -> frozen multidimensional state -> query retrieval/reconstruction -> common reader`

The writer must not receive the future question, answer key, or evaluator data.

## Current state

- NDM schema v0.1
- Writer adapter using Claude Code CLI
- Frozen JSON memory per source
- Deterministic semantic evidence retrieval
- Current-state eligibility penalty for superseded/rejected/disputed records
- Canonical provenance fields
- Reader adapter scaffold
- Explicit statuses for context-limit, rate-limit, writer schema failure

## Deliberate limitation

The first retrieval implementation is deterministic lexical candidate generation over NDM records. It is a harness/debugging slice, not the final NDM retrieval algorithm. The research loop is: expose failure -> classify -> modify NDM -> freeze a version -> evaluate.

## Next

1. Run 1-3 small clean-room source contexts.
2. Inspect memory records manually.
3. Add adversarial NDM tests for temporal state, supersession, ambiguity, belief conflict, causality, provenance and negative knowledge.
4. Implement NDM query reconstruction.
5. Run a small LongBench-v2 slice.
6. Only after NDM is stable, compare GraphRAG/HippoRAG2.
