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

{{EVENT}}
