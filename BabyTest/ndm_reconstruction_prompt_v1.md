# NDM Reconstruction Prompt v1

You are performing a reconstruction experiment for an N-dimensional memory system.

You are given an **interpreted context** produced by another LLM from an original source event or passage.

Your task is to reconstruct the **entities and entity-specific semantic dimensions** that are supported by that interpreted context.

This is NOT a summarization task.
This is NOT a request to reproduce the original wording.
This is NOT a request to improve or correct the interpretation.
This is NOT a request to infer relationships across events.

## Rules

1. Treat the interpreted context as the only source of information.
2. Do not use the original source event, source document, outside knowledge, or assumptions.
3. Identify every entity explicitly represented in the interpreted context.
4. For each entity, identify the semantic dimensions that are supported by the interpreted context.
5. Dimensions must belong to the entity they describe.
6. Preserve distinctions between entities.
7. Preserve distinctions between different semantic aspects of the same entity.
8. Preserve explicit uncertainty, ambiguity, qualification, and unresolved information.
9. Do not resolve ambiguity.
10. Do not infer causality, chronology, ownership, intent, belief, state transition, or relationships unless explicitly represented in the interpreted context.
11. Do not add dimensions merely because they would normally be useful for that type of entity.
12. Do not invent values.
13. Do not merge entities because they appear related.
14. Do not split one entity into multiple entities unless the interpreted context explicitly distinguishes them.
15. Dimension names do not need to match any previous vocabulary. Semantic equivalence matters more than wording.
16. Do not explain your reasoning.
17. Return ONLY valid JSON.

## Output Format

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

## Reconstruction Objective

The output should contain the maximum amount of semantic information that can be reconstructed from the interpreted context without introducing unsupported information.

Do not attempt to reconstruct the original source text.

## Interpreted Context

{{INTERPRETED_CONTEXT}}
