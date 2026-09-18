# EXP-V2 Conversation 01 Report

Models compared: claude, codex, copilot

## Metrics
- Canonical points: 12
- Points present in all models: 9
- Point coverage: 75.00%
- Points with at least one common dimension: 12
- Dimension preservation (intersection / union): 71.43%

## Canonical points
### `football`
- common: noun, object
- union: activity, noun, object
- claude-specific: activity
- copilot-specific: activity

### `friends`
- common: noun
- union: actor, noun, object, target
- claude-specific: object, target
- codex-specific: actor, target
- copilot-specific: actor

### `he`
- common: actor, subject
- union: actor, noun, subject
- claude-specific: noun

### `love`
- common: emotion, feeling, verb
- union: emotion, feeling, verb

### `new team`
- common: noun
- union: actor, noun, object, state, target
- claude-specific: object
- codex-specific: object, target
- copilot-specific: actor, state

### `park`
- common: place
- union: noun, place
- claude-specific: noun

### `play`
- common: action, verb
- union: action, verb

### `play football`
- common: action, object, verb
- union: action, object, verb

### `rahul`
- common: actor, noun, subject
- union: actor, noun, subject

### `started playing again`
- common: action, state, verb
- union: action, state, verb

### `stopped playing football`
- common: action, state, verb
- union: action, state, verb

### `sunday`
- common: time
- union: time
