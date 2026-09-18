# EXP-V1 Agent Instruction

You are participating in an experiment on multidimensional conversational memory.

Read the supplied conversation.

Your task is to represent the conversation as a multidimensional semantic state.

This is NOT a conventional knowledge graph.

This is NOT a summary.

Do NOT create relationships merely because they seem plausible.

Do NOT invent facts.

Preserve the original evidence.

## Dimensions

Initially use:

- noun
- verb
- action
- subject
- object
- time
- place
- emotion
- feeling
- intent
- state
- actor
- target

A token or phrase may exist in multiple dimensions.

For example:

"Rahul"

may simultaneously be:

- noun
- subject
- actor

"loves"

may be:

- verb
- emotion
- feeling

"play"

may be:

- verb
- action

"football"

may be:

- noun
- object
- activity

Do not force a token into a dimension if the evidence does not support it.

## Temporal information

Preserve changes over time.

For example:

playing
→ stopped playing
→ started playing again

should not become a single static fact.

## Ambiguity

If something is ambiguous, preserve the ambiguity.

Example:

"He plays football."

If it is unclear who "He" refers to, create an unresolved ambiguity instead of silently assuming the answer.

## Evidence

Every interpretation must retain its source sentence.

## Output

Return JSON using this structure:

{
  "conversation_id": "...",

  "points": [
    {
      "point_id": "...",
      "surface": "...",
      "dimensions": [],
      "interpretations": [],
      "source_sentences": [],
      "confidence": 0.0
    }
  ],

  "temporal_states": [],

  "ambiguities": [],

  "explicit_facts": []
}

Do not generate inferred relationships.

Do not generate coordinates.

Do not generate embeddings.

Do not generate graph edges.

The purpose of this experiment is to determine whether the conversation can first be represented as reusable multidimensional points.
