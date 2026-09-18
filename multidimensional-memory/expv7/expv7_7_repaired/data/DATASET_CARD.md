# V7.7 Repaired Dataset Card

- 12 conversations
- 1,200 source events
- 216 curated durable events
- 96 future queries
- 8 query categories × 12 conversations

## Repair
The prior V7.7 gold query evidence lists were inconsistent with the durable-event set and pointed at generic filler events. This repaired version rebuilds every query evidence set from canonical durable event IDs and validates answerability.

## Writer visibility
Writers receive `conversation_v7_7_unlabeled.jsonl` and public query/schema/design materials only. Evaluator gold is kept separate.

## Caveat
The corpus remains synthetic/template-generated and should not be treated as evidence of real-world conversational generalization.
