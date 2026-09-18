# EXP-V5: Ambiguity + Belief State

## Question
Can persistent memory preserve what is known, inferred, uncertain, confirmed, disputed, or explicitly rejected without silently resolving uncertainty or rewriting history?

## Principles
- Unknown is a valid state.
- Ambiguity is stored as first-class data.
- Inference is never promoted to fact by confidence alone.
- Human confirmation can promote a hypothesis to confirmed.
- Later evidence can supersede a belief without deleting prior observations.
- If no supporting memory exists, the substrate can return `no_prior_event`.
- Every belief retains provenance and status history.

## Belief lifecycle
`unknown -> inferred -> confirmed`
`inferred -> disputed`
`confirmed -> disputed`
`inferred/confirmed -> rejected`

These are state transitions of the memory representation, not claims about objective truth.

## Ambiguity
An unresolved reference is represented as a bucket containing candidates, evidence, and resolution status. A later event can resolve the bucket, but the original ambiguity remains in provenance.
