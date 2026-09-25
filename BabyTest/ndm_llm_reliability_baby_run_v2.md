## Hypothesis
Current general-purpose LLMs are sufficiently capable of identifying entities and relevant semantic dimensions from natural-language events that a lightweight extraction interface may be sufficient for constructing an N-dimensional memory representation, without requiring the model to directly generate the complete NDM storage structure.

## Test 001
Single Event

### Input
Alice proposed PostgreSQL for the payments platform.

### Model
Gemini Flash 3.8

### Prompt
Analyze the event below.

First identify every entity explicitly present in the event.

For each entity, determine the semantic dimensions that are relevant
to understanding that entity within this specific event.

A dimension should describe something meaningful about the entity,
such as its role, state, action, relationship, context, ownership,
status, temporal position, belief, or other relevant characteristic.

Do not use a fixed dimension vocabulary.
Create dimension names that best describe the information present.

Do not invent information that is not supported by the event.
Do not infer relationships merely because two entities appear together.
Do not resolve ambiguity that the event itself does not resolve.

Return ONLY valid JSON in this structure:

{
  "entities": [
    {
      "name": "...",
      "dimensions": {
        "dimension_name": "value"
      }
    }
  ]
}

Event:

Alice proposed PostgreSQL for the payments platform.

### Raw Output
```json
{
  "entities": [
    {
      "name": "Alice",
      "dimensions": {
        "event_role": "proposer",
        "action_performed": "proposed PostgreSQL for the payments platform"
      }
    },
    {
      "name": "PostgreSQL",
      "dimensions": {
        "event_role": "proposed_technology",
        "proposal_target": "payments platform",
        "proposer": "Alice"
      }
    },
    {
      "name": "payments platform",
      "dimensions": {
        "event_role": "target_system",
        "candidate_technology": "PostgreSQL"
      }
    }
  ]
}

```
### Parsed Output
...

### Expected Entities
...

### Expected Dimensions
...

### Observations
...

### Errors
...

### Output Format
STRUCTURED

### Parseable
YES 

### Semantic Accuracy
...

### Missing Dimensions
...

### Hallucinated Entities
...

### Hallucinated Relationships
...

### Notes
...

## Test 002
Single Event

### Input
Alice proposed PostgreSQL for the payments platform.

### Model
Claude Opus 5.5

### Prompt
Analyze the event below.

First identify every entity explicitly present in the event.

For each entity, determine the semantic dimensions that are relevant
to understanding that entity within this specific event.

A dimension should describe something meaningful about the entity,
such as its role, state, action, relationship, context, ownership,
status, temporal position, belief, or other relevant characteristic.

Do not use a fixed dimension vocabulary.
Create dimension names that best describe the information present.

Do not invent information that is not supported by the event.
Do not infer relationships merely because two entities appear together.
Do not resolve ambiguity that the event itself does not resolve.

Return ONLY valid JSON in this structure:

{
  "entities": [
    {
      "name": "...",
      "dimensions": {
        "dimension_name": "value"
      }
    }
  ]
}

Event:

Alice proposed PostgreSQL for the payments platform.

### Raw Output
```json
{
  "entities": [
    {
      "name": "Alice",
      "dimensions": {
        "role_in_event": "proposer",
        "action": "proposed",
        "proposal_subject": "PostgreSQL",
        "proposal_target": "payments platform",
        "temporal_position": "past"
      }
    },
    {
      "name": "PostgreSQL",
      "dimensions": {
        "role_in_event": "proposed option",
        "proposal_status": "proposed",
        "proposed_by": "Alice",
        "proposed_for": "payments platform",
        "adoption_status": "unresolved"
      }
    },
    {
      "name": "payments platform",
      "dimensions": {
        "role_in_event": "target of proposal",
        "proposed_technology": "PostgreSQL",
        "decision_status": "unresolved"
      }
    }
  ]
}
```
### Parsed Output
...

### Expected Entities
...

### Expected Dimensions
...

### Observations
...

### Errors
...

### Output Format
STRUCTURED

### Parseable
YES 

### Semantic Accuracy
...

### Missing Dimensions
...

### Hallucinated Entities
...

### Hallucinated Relationships
...

### Notes
...

## Test 003
Single Event

### Input
Alice proposed PostgreSQL for the payments platform.

### Model
Grok

### Prompt
Analyze the event below.

First identify every entity explicitly present in the event.

For each entity, determine the semantic dimensions that are relevant
to understanding that entity within this specific event.

A dimension should describe something meaningful about the entity,
such as its role, state, action, relationship, context, ownership,
status, temporal position, belief, or other relevant characteristic.

Do not use a fixed dimension vocabulary.
Create dimension names that best describe the information present.

Do not invent information that is not supported by the event.
Do not infer relationships merely because two entities appear together.
Do not resolve ambiguity that the event itself does not resolve.

Return ONLY valid JSON in this structure:

{
  "entities": [
    {
      "name": "...",
      "dimensions": {
        "dimension_name": "value"
      }
    }
  ]
}

Event:

Alice proposed PostgreSQL for the payments platform.

### Raw Output
{
  "entities": [
    {
      "name": "Alice",
      "dimensions": {
        "action": "proposed",
        "proposed_item": "PostgreSQL",
        "proposed_for": "payments platform"
      }
    },
    {
      "name": "PostgreSQL",
      "dimensions": {
        "status": "proposed",
        "proposed_by": "Alice",
        "proposed_for": "payments platform"
      }
    },
    {
      "name": "payments platform",
      "dimensions": {
        "role": "target of proposal",
        "proposed_technology": "PostgreSQL",
        "proposed_by": "Alice"
      }
    }
  ]
}
### Parsed Output
...

### Expected Entities
...

### Expected Dimensions
...

### Observations
...

### Errors
...

### Output Format
STRUCTURED

### Parseable
YES 

### Semantic Accuracy
...

### Missing Dimensions
...

### Hallucinated Entities
...

### Hallucinated Relationships
...

### Notes
...

## Test 004
Single Event

### Input
Alice proposed PostgreSQL for the payments platform.

### Model
ChatGPT

### Prompt
Analyze the event below.

First identify every entity explicitly present in the event.

For each entity, determine the semantic dimensions that are relevant
to understanding that entity within this specific event.

A dimension should describe something meaningful about the entity,
such as its role, state, action, relationship, context, ownership,
status, temporal position, belief, or other relevant characteristic.

Do not use a fixed dimension vocabulary.
Create dimension names that best describe the information present.

Do not invent information that is not supported by the event.
Do not infer relationships merely because two entities appear together.
Do not resolve ambiguity that the event itself does not resolve.

Return ONLY valid JSON in this structure:

{
  "entities": [
    {
      "name": "...",
      "dimensions": {
        "dimension_name": "value"
      }
    }
  ]
}

Event:

Alice proposed PostgreSQL for the payments platform.

### Raw Output
{
"entities": [
{
"name": "Alice",
"dimensions": {
"role": "proposer",
"action": "proposed"
}
},
{
"name": "PostgreSQL",
"dimensions": {
"role": "proposed technology"
}
},
{
"name": "payments platform",
"dimensions": {
"context": "intended platform"
}
}
]
}

### Parsed Output
...

### Expected Entities
...

### Expected Dimensions
...

### Observations
...

### Errors
...

### Output Format
STRUCTURED

### Parseable
YES 

### Semantic Accuracy
...

### Missing Dimensions
...

### Hallucinated Entities
...

### Hallucinated Relationships
...

### Notes
...