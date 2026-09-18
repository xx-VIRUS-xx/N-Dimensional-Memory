# EXP-V3.1: Evidence-Constrained Relationships

## Hypothesis

Relationship candidates become more useful when deterministic rules are constrained by semantic roles, lexical structure, shared evidence, and local transition markers.

## Metrics

- **canonical_points:** `12`
- **candidate_relations:** `12`
- **connected_points:** `7`
- **isolated_points:** `5`
- **relation_types:** `{'acts_on': 4, 'granularity_related': 3, 'performs': 3, 'state_transition_began': 1, 'state_transition_ended': 1}`
- **high_confidence_relations:** `9`
- **medium_confidence_relations:** `3`

## Candidate relations

- `p_001 -> p_003` **performs** (high) — shared evidence + actor/subject -> action/verb — evidence: Rahul loves to play football.
- `p_001 -> p_012` **performs** (high) — shared evidence + actor/subject -> action/verb — evidence: Rahul loves to play football.
- `p_003 -> p_004` **acts_on** (medium) — shared evidence + action -> object/target — evidence: Rahul loves to play football.
- `p_003 -> p_012` **acts_on** (high) — compound/lexical containment + action -> object — evidence: Rahul loves to play football.
- `p_003 -> p_012` **granularity_related** (high) — EXP-V2.1 RELATED identity — evidence: identity substrate
- `p_004 -> p_012` **granularity_related** (high) — EXP-V2.1 RELATED identity — evidence: identity substrate
- `p_009 -> p_009` **state_transition_ended** (high) — transition marker 'stopped' in event surface — evidence: Rahul stopped playing football during the summer.
- `p_009 -> p_012` **granularity_related** (high) — EXP-V2.1 RELATED identity — evidence: identity substrate
- `p_010 -> p_010` **state_transition_began** (high) — transition marker 'started' in event surface — evidence: Rahul started playing again after joining a new team.
- `p_010 -> p_011` **acts_on** (medium) — shared evidence + action -> object/target — evidence: Rahul started playing again after joining a new team.
- `p_011 -> p_010` **performs** (high) — shared evidence + actor/subject -> action/verb — evidence: Rahul started playing again after joining a new team.
- `p_012 -> p_004` **acts_on** (medium) — shared evidence + action -> object/target — evidence: Rahul loves to play football.

## Key constraint changes

- Emotion/feeling/intent-only verbs are not treated as generic object-taking actions.
- Actor-to-context edges require shared evidence.
- Transition markers must occur in the event point itself.
- Lexical containment can raise action-to-object confidence, but does not merge points.
