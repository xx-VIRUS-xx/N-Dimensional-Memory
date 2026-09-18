# EXP-V5.1 — Competing Beliefs and Non-Destructive Resolution

## Question
Can the memory substrate preserve multiple competing beliefs about the same proposition and later resolve their conflict without deleting the observations that created it?

## Design
- Observations remain append-only.
- A proposition is a normalized grouping, not a replacement for observations.
- Opposing propositions create an explicit conflict record.
- Resolution changes the conflict state and records provenance, but does not erase either observation.
- A later confirmed observation may update its own epistemic status while retaining status history.

## Important distinction
Resolution is not deletion. The system remembers that an earlier belief existed, why it was held, and what later evidence changed its standing.

## Benchmark
The benchmark intentionally creates two competing location propositions and then resolves the conflict using an explicit user correction. It also tests repeated support for the same proposition and confirmation history.
