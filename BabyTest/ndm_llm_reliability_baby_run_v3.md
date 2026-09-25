## Hypothesis
Current general-purpose LLMs are sufficiently capable of identifying entities and relevant semantic dimensions from natural-language events that a lightweight extraction interface may be sufficient for constructing an N-dimensional memory representation, without requiring the model to directly generate the complete NDM storage structure.

## Test 001
Single Event

### Input
Bob argued that CockroachDB was better for multi-region payments, and Alice accepted the proposal.

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

Bob argued that CockroachDB was better for multi-region payments, and Alice accepted the proposal.

### Raw Output
{
"entities": [
{
"name": "Bob",
"dimensions": {
"role": "arguer / proposer",
"action": "argued that CockroachDB was better for multi-region payments",
"advocated_choice": "CockroachDB",
"outcome": "had proposal accepted by Alice"
}
},
{
"name": "CockroachDB",
"dimensions": {
"entity_type": "database system / technology",
"role_in_argument": "subject of comparison and recommendation",
"asserted_attribute": "better for multi-region payments"
}
},
{
"name": "multi-region payments",
"dimensions": {
"entity_type": "use case / operational domain",
"context": "functional requirement against which CockroachDB was evaluated"
}
},
{
"name": "Alice",
"dimensions": {
"role": "evaluator / recipient of the proposal",
"action": "accepted the proposal",
"decision_state": "in agreement"
}
},
{
"name": "proposal",
"dimensions": {
"entity_type": "proposition / technical recommendation",
"originator": "Bob",
"content": "using CockroachDB for multi-region payments",
"resolution_status": "accepted by Alice"
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

## Test 002
Single Event

### Input
Bob argued that CockroachDB was better for multi-region payments, and Alice accepted the proposal.

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

Bob argued that CockroachDB was better for multi-region payments, and Alice accepted the proposal.

### Raw Output
```json
{
  "entities": [
    {
      "name": "Bob",
      "dimensions": {
        "action": "argued",
        "argument_position": "CockroachDB was better for multi-region payments",
        "role_in_event": "advocate"
      }
    },
    {
      "name": "CockroachDB",
      "dimensions": {
        "role_in_event": "subject of Bob's argument",
        "claimed_quality": "better",
        "claimed_suitability_context": "multi-region payments",
        "comparison_baseline": "unspecified",
        "claim_source": "Bob"
      }
    },
    {
      "name": "multi-region payments",
      "dimensions": {
        "role_in_event": "use-case context for the evaluation of CockroachDB"
      }
    },
    {
      "name": "Alice",
      "dimensions": {
        "action": "accepted",
        "object_of_action": "the proposal",
        "role_in_event": "decision-maker or respondent"
      }
    },
    {
      "name": "the proposal",
      "dimensions": {
        "status": "accepted",
        "accepted_by": "Alice",
        "proposer": "unspecified",
        "content": "unspecified",
        "relation_to_bob_argument": "ambiguous; not explicitly stated"
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
Bob argued that CockroachDB was better for multi-region payments, and Alice accepted the proposal.

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

Bob argued that CockroachDB was better for multi-region payments, and Alice accepted the proposal.

### Raw Output
{
  "entities": [
    {
      "name": "Bob",
      "dimensions": {
        "action": "argued that CockroachDB was better for multi-region payments",
        "role": "proposer"
      }
    },
    {
      "name": "CockroachDB",
      "dimensions": {
        "claimed_advantage": "better for multi-region payments",
        "claimed_by": "Bob"
      }
    },
    {
      "name": "multi-region payments",
      "dimensions": {
        "context": "use case for which CockroachDB was argued to be better"
      }
    },
    {
      "name": "Alice",
      "dimensions": {
        "action": "accepted the proposal"
      }
    },
    {
      "name": "proposal",
      "dimensions": {
        "content": "CockroachDB was better for multi-region payments",
        "status": "accepted",
        "accepted_by": "Alice",
        "origin": "Bob's argument"
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
Bob argued that CockroachDB was better for multi-region payments, and Alice accepted the proposal.

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

Bob argued that CockroachDB was better for multi-region payments, and Alice accepted the proposal.

### Raw Output
{
"entities": [
{
"name": "Bob",
"dimensions": {
"role": "arguer",
"action": "argued that CockroachDB was better for multi-region payments",
"belief": "CockroachDB was better for multi-region payments"
}
},
{
"name": "CockroachDB",
"dimensions": {
"role": "proposed technology",
"comparative_assessment": "better for multi-region payments",
"context": "multi-region payments"
}
},
{
"name": "multi-region payments",
"dimensions": {
"context": "use case for which CockroachDB was argued to be better"
}
},
{
"name": "Alice",
"dimensions": {
"role": "proposal recipient",
"action": "accepted the proposal",
"status": "accepted"
}
},
{
"name": "proposal",
"dimensions": {
"content": "use CockroachDB for multi-region payments",
"status": "accepted by Alice"
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