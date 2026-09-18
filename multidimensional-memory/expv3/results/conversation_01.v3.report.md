# EXP-V3: Deterministic Relationship Candidates

## Hypothesis

Candidate relationships can be derived from canonical points using dimensions, shared evidence, identity links, and explicit temporal/state markers without another model call.

## Metrics

- **canonical_points:** `12`
- **candidate_relations:** `14`
- **connected_points:** `8`
- **isolated_points:** `4`
- **relation_types:** `{'acts_on': 6, 'granularity_related': 3, 'performs': 4, 'state_transition_began': 1}`
- **high_confidence_relations:** `7`
- **medium_confidence_relations:** `7`

## Candidate relations

- `p_001 -> p_002` **performs** (high) — shared evidence + actor/subject to action/verb — evidence: Rahul loves to play football.
- `p_001 -> p_003` **performs** (high) — shared evidence + actor/subject to action/verb — evidence: Rahul loves to play football.
- `p_001 -> p_012` **performs** (high) — shared evidence + actor/subject to action/verb — evidence: Rahul loves to play football.
- `p_002 -> p_004` **acts_on** (medium) — shared evidence + action to object/target — evidence: Rahul loves to play football.
- `p_002 -> p_012` **acts_on** (medium) — shared evidence + action to object/target — evidence: Rahul loves to play football.
- `p_003 -> p_004` **acts_on** (medium) — shared evidence + action to object/target — evidence: Rahul loves to play football.
- `p_003 -> p_012` **acts_on** (medium) — shared evidence + action to object/target — evidence: Rahul loves to play football.
- `p_003 -> p_012` **granularity_related** (high) — EXP-V2.1 RELATED identity — evidence: identity substrate
- `p_004 -> p_012` **granularity_related** (high) — EXP-V2.1 RELATED identity — evidence: identity substrate
- `p_009 -> p_012` **granularity_related** (high) — EXP-V2.1 RELATED identity — evidence: identity substrate
- `p_010 -> p_011` **acts_on** (medium) — shared evidence + action to object/target — evidence: Rahul started playing again after joining a new team.
- `p_010 -> p_011` **state_transition_began** (medium) — marker 'started' + event/state dimensions — evidence: Rahul started playing again after joining a new team.
- `p_011 -> p_010` **performs** (high) — shared evidence + actor/subject to action/verb — evidence: Rahul started playing again after joining a new team.
- `p_012 -> p_004` **acts_on** (medium) — shared evidence + action to object/target — evidence: Rahul loves to play football.

## Interpretation rule

These are candidate edges, not asserted facts. Human approval or a later policy layer is required before promoting a candidate to a fact.
