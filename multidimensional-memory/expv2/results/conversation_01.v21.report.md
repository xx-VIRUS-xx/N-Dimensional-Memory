# EXP-V2.1 Identity Report

## Metrics
- models: ['claude', 'codex', 'copilot']
- canonical_points: 12
- points_supported_by_2_or_more_models: 11
- points_supported_by_all_models: 9
- multi_model_support_rate: 0.9167
- all_model_support_rate: 0.75
- related_point_edges: 3
- dimension_intersection_union_ratio: 0.7143

## Canonical points
### `rahul` (p_001)
- common dimensions: actor, noun, subject
- union dimensions: actor, noun, subject
- related points: none
- claude: `Rahul` -> actor, noun, subject
- codex: `Rahul` -> actor, noun, subject
- copilot: `Rahul` -> actor, noun, subject

### `love` (p_002)
- common dimensions: emotion, feeling, verb
- union dimensions: emotion, feeling, verb
- related points: none
- claude: `loves` -> emotion, feeling, verb
- codex: `loves` -> emotion, feeling, verb
- copilot: `loves` -> emotion, feeling, verb

### `play` (p_003)
- common dimensions: action, verb
- union dimensions: action, verb
- related points: p_012
- claude: `play / plays / playing` -> action, verb
- copilot: `play` -> action, verb

### `football` (p_004)
- common dimensions: noun, object
- union dimensions: activity, noun, object
- related points: p_012
- claude: `football` -> activity, noun, object
- codex: `football` -> noun, object
- copilot: `football` -> activity, noun, object

### `sunday` (p_005)
- common dimensions: time
- union dimensions: time
- related points: none
- claude: `every Sunday` -> time
- codex: `every Sunday` -> time
- copilot: `every Sunday` -> time

### `park` (p_006)
- common dimensions: place
- union dimensions: noun, place
- related points: none
- claude: `park` -> noun, place
- codex: `at the park` -> place
- copilot: `park` -> place

### `he` (p_007)
- common dimensions: actor, subject
- union dimensions: actor, noun, subject
- related points: none
- claude: `He` -> actor, noun, subject
- codex: `He` -> actor, subject

### `friends` (p_008)
- common dimensions: noun
- union dimensions: actor, noun, object, target
- related points: none
- claude: `friends` -> noun, object, target
- codex: `his friends` -> actor, noun, target
- copilot: `friends` -> actor, noun

### `stopped playing football` (p_009)
- common dimensions: action, state, verb
- union dimensions: action, state, verb
- related points: p_012
- claude: `stopped playing football` -> action, state, verb
- codex: `stopped playing football` -> action, state, verb
- copilot: `stopped playing football` -> action, state, verb

### `started playing again` (p_010)
- common dimensions: action, state, verb
- union dimensions: action, state, verb
- related points: none
- claude: `started playing again` -> action, state, verb
- codex: `started playing again` -> action, state, verb
- copilot: `started playing again` -> action, state, verb

### `new team` (p_011)
- common dimensions: noun
- union dimensions: actor, noun, object, state, target
- related points: none
- claude: `new team` -> noun, object
- codex: `new team` -> noun, object, target
- copilot: `new team` -> actor, noun, state

### `play football` (p_012)
- common dimensions: action, object, verb
- union dimensions: action, object, verb
- related points: p_003, p_004, p_009
- codex: `play football` -> action, object, verb
