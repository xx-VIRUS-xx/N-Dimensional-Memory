# Visualization Agent Prompt

You are the visualization stage of the Spherical NDM v1 experiment.

Read these artifacts before implementing anything:

- `corpus/raw_events.jsonl`
- `extraction/entity_dimensions.jsonl`
- `space/reference_dimensions.json`
- `space/space_definition.md`

## Representation rules

1. An entity is a point.
2. An entity appearing at different events is represented as a different point P(entity,event).
3. `conversationByTime` is the reference dimension and orders events from t0 to tN.
4. LLM-extracted dimensions are semantic information associated with the point.
5. Do not create relationship edges unless they are explicitly present in the supplied data.
6. Do not invent mathematical formulas and present them as NDM theory.
7. Preserve ambiguity when the extraction result contains it.

## Visualization requirements

Create an interactive visualization that allows the researcher to rotate, zoom, pan, move through conversationByTime, select an entity point, inspect its event, inspect its dimensions, filter entities, filter dimensions, and reveal repeated occurrences of the same entity across time.

The visualization is a diagnostic instrument. Geometric proximity must not be presented as proof of a semantic relationship.

## Deliverables

Create a self-contained runnable visualization using the technologies available in the environment. Include a short README explaining how to run it and exactly which input files were consumed.

Do not modify the source extraction artifacts, the raw events, or the space definition.
Do not add relationship inference algorithms.

The purpose of this stage is to let the research team inspect the actual entity-point/dimension structure before defining the mathematics.
