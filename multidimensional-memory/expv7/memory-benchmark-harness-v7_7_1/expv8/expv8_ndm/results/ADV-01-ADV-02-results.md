# N-Dimensional Memory: ADV-01 and ADV-02 Results

## Status

The NDM V8 query reconstruction layer has passed the ADV-02 evidence contract.

Version:

`ndm-query-reconstructor-v8`

## ADV-01

ADV-01 established the foundational semantic contract:

- historical state
- current state
- lifecycle / supersession
- temporal evolution
- causality
- beliefs
- scope
- negative knowledge
- contradiction

A key finding was that a query subject is not necessarily the proposition subject. An actor such as Alice can be connected to a proposition through event participation and/or belief ownership.

## ADV-02

ADV-02 extends the memory model with:

- successive state changes
- rejected decisions and later reversal
- multiple scopes
- ambiguous entity identity
- identity clarification
- causal and non-causal temporal relationships
- negative knowledge
- provenance
- temporal validity

## Final Evidence Reconstruction

| Query | Evidence |
|---|---|
| Q201 | E101 |
| Q202 | E110 |
| Q203 | E101, E103, E106, E110 |
| Q204 | E104, E106, E107 |
| Q205 | E108, E109, E110 |
| Q206 | E111, E112 |
| Q207 | E113, E114 |
| Q208 | E115, E116, E117 |

All eight ADV-02 query evidence contracts are satisfied.

## Architectural Result

V8 uses a dedicated reconstruction path rather than modifying the V3.1 retriever:

```
NDM V8 memory
    ↓
Reconstructed state
    ↓
NDM query reconstructor
    ↓
Evidence packet
```

The resolver now handles canonical entity identity across identifier casing and actor-scoped queries through proposition entities, event participants, and belief holders.

## Interpretation

The current experiments demonstrate that NDM can reconstruct relevant conversational state across temporal, lifecycle, belief, scope, causal, negative-knowledge, and identity dimensions.

These experiments establish evidence reconstruction. They do not yet establish large-scale performance, noisy extraction robustness, or answer-generation quality from reconstructed evidence.
