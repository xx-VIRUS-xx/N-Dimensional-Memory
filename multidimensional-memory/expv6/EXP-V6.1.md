# EXP-V6.1 — Shared Memory Read/Update Protocol

## Question
Can multiple independent agents read and update the same persistent memory state without one agent becoming authoritative, while preserving provenance, disagreement, temporal history, and append-only observations?

## Hypothesis
A shared memory protocol can separate four concerns:
1. stable proposition identity,
2. agent-local observations,
3. persistent state derived from those observations,
4. immutable provenance/history.

An agent may append an observation and request a state recomputation, but cannot overwrite another agent's observation.

## Experiment
Two agents perform sequential updates against the same in-memory store:
- Agent A records an inferred location: Jaipur.
- Agent B records a confirmed location: Delhi.
- Agent A reads the state after B's update.
- A later observation can explicitly supersede the earlier state only when temporal/evidentiary rules justify it.

The benchmark also tests concurrent-style independent updates by applying observations in both orders. The resulting memory must retain both observations and expose the disagreement regardless of update order.

## Success criteria
1. Both agents read the same persistent proposition identity.
2. Updates append observations rather than overwrite them.
3. Every observation retains agent/source provenance.
4. Disagreement remains visible and order-independent.
5. Derived current status can change without deleting historical observations.
6. A fresh reader can reconstruct the state from the persisted observation log.
