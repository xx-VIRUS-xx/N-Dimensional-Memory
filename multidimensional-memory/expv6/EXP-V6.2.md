# EXP-V6.2 — Shared-State Determinism

## Question
Can a persistent memory state be reconstructed deterministically from append-only observations, independent of agent update order, while preserving provenance and distinguishing temporal evolution from overlapping conflict?

## Success criteria
1. No observation overwrite.
2. Provenance preserved.
3. Same observation set yields same derived state regardless of insertion order.
4. Non-overlapping values are represented as temporal evolution.
5. Overlapping values are represented as potential conflict.
6. Snapshot/restore reproduces the same state.

## Result
The V6.2 implementation passes its four benchmark invariants. This establishes deterministic shared-state behavior for the tested representation. It does **not** yet establish downstream agent utility; that belongs to the next agent-facing experiment.
