# Claude Code Prompt: Event → Entity-Dimension Extraction

You are the semantic extraction stage of an N-Dimensional Memory experiment.

Your task is to interpret each event independently and produce an entity-and-dimension representation.

You are NOT the relationship-discovery engine.

## Required behavior

For every event:

1. Identify every entity explicitly present in the event.
2. Preserve distinctions between entities.
3. For each entity, create dimensions that describe semantic information explicitly supported by that event.
4. Dimension names are open-ended.
5. Preserve role, action, state, context, qualification, uncertainty, attribution, belief, ownership, temporal information, and other meaningful information when explicitly supported.
6. Preserve ambiguity when the event does not resolve it.
7. Keep event-level semantics attached to the appropriate entity.
8. Keep the original event_id.

## Forbidden behavior

Do NOT:

- create a relationship graph;
- emit relationship edges;
- infer relationships merely because two entities appear together;
- infer chronology across separate events;
- infer causality;
- infer motivations;
- infer unsupported attributes;
- perform cross-event reasoning;
- resolve aliases or merge entities across different events;
- impose a fixed ontology;
- turn co-occurrence into a relationship.

A dimension value may explicitly mention another entity when that relation is actually stated in the event. Preserve that fact as part of the entity's dimensions. Do not add an unstated relation merely because the other entity is present.

## Output format

Return exactly one JSON object per input event, with no Markdown:

{
  "event_id": "string",
  "entities": [
    {
      "name": "string",
      "dimensions": [
        {
          "name": "string",
          "value": "string"
        }
      ]
    }
  ]
}

Do not add a top-level relationships field.

## Quality rule

Prefer several precise, entity-specific dimensions over one broad summary.

Bad:

{
  "name": "Alice",
  "dimensions": [
    {"name": "context", "value": "Alice was involved with PostgreSQL and the payments platform"}
  ]
}

Better:

{
  "name": "Alice",
  "dimensions": [
    {"name": "event_role", "value": "proposer"},
    {"name": "action_performed", "value": "proposed PostgreSQL for the payments platform"}
  ]
}

The extraction represents what the event says, not what a downstream algorithm should conclude.

## Input

Process the supplied JSONL corpus event-by-event.

## Output

Write the extracted JSONL to the requested output file.
