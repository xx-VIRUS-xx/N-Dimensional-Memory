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

Identify:

1. All entities explicitly present in the event.
2. All semantic dimensions that are relevant for understanding the event.

For each entity, provide only its name.

For each dimension, provide only the dimension name.

Do not infer relationships that are not explicitly supported by the event.
Do not add information that is not present.
Do not resolve ambiguity that the event itself does not resolve.

Return ONLY this JSON structure:

{
  "entities": [],
  "dimensions": []
}

Event:
Alice proposed PostgreSQL for the payments platform.

### Raw Output
```json
{
  "entities": [
    "Alice",
    "PostgreSQL",
    "payments platform"
  ],
  "dimensions": [
    "Agent",
    "Action",
    "Proposed Technology",
    "Target System"
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

Identify:

1. All entities explicitly present in the event.
2. All semantic dimensions that are relevant for understanding the event.

For each entity, provide only its name.

For each dimension, provide only the dimension name.

Do not infer relationships that are not explicitly supported by the event.
Do not add information that is not present.
Do not resolve ambiguity that the event itself does not resolve.

Return ONLY this JSON structure:

{
  "entities": [],
  "dimensions": []
}

Event:
Alice proposed PostgreSQL for the payments platform.

### Raw Output
```json
{
  "entities": ["Alice", "PostgreSQL", "payments platform"],
  "dimensions": ["actor", "action", "proposed_technology", "target_system", "decision_status", "tense"]
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

Identify:

1. All entities explicitly present in the event.
2. All semantic dimensions that are relevant for understanding the event.

For each entity, provide only its name.

For each dimension, provide only the dimension name.

Do not infer relationships that are not explicitly supported by the event.
Do not add information that is not present.
Do not resolve ambiguity that the event itself does not resolve.

Return ONLY this JSON structure:

{
  "entities": [],
  "dimensions": []
}

Event:
Alice proposed PostgreSQL for the payments platform.

### Raw Output
{
  "entities": ["Alice", "PostgreSQL", "payments platform"],
  "dimensions": ["agent", "technology", "application", "action"]
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

Identify:

1. All entities explicitly present in the event.
2. All semantic dimensions that are relevant for understanding the event.

For each entity, provide only its name.

For each dimension, provide only the dimension name.

Do not infer relationships that are not explicitly supported by the event.
Do not add information that is not present.
Do not resolve ambiguity that the event itself does not resolve.

Return ONLY this JSON structure:

{
  "entities": [],
  "dimensions": []
}

Event:
Alice proposed PostgreSQL for the payments platform.

### Raw Output
{
"entities": ["Alice", "PostgreSQL", "payments platform"],
"dimensions": ["proposer", "proposal", "technology", "platform", "purpose"]
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