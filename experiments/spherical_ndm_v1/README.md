# Spherical NDM v1

This experiment is the next step after the entity-and-dimension reliability work in `ndm_llm_reliability_baby_run_v2.md`.

## Core representation

The primitive object is:

```text
Entity = Point
```

An entity appearing in event t is a distinct point:

```text
P(entity, event)
```

The first reference dimension is `conversationByTime`, which orders the ten events as t0 through t9.

The LLM-extracted dimensions are semantic information associated with each entity point. We do not mean-pool an entity into one global embedding in this experiment.

## Experiment flow

```text
10 raw events
    ↓
run_extraction.py
    ↓
10 independent Claude Code invocations
    ↓
entity_dimensions.jsonl
    ↓
visualization agent
    ↓
interactive spatial inspection
    ↓
mathematical brainstorming
    ↓
query model
```

## Extraction isolation

Every event is sent to a fresh Claude Code print-mode process.

The runner uses `--bare`, `--no-session-persistence`, `--tools ""`, `--max-turns 1`, and `CLAUDE_CODE_SKIP_PROMPT_HISTORY=1` so the extraction stage does not carry conversation history or automatically load project memory/instructions.

The semantic input for each invocation is only the prompt template plus the current event.

## Phase 1

Run from `experiments/spherical_ndm_v1`:

```bash
python extraction/run_extraction.py
```

Optional:

```bash
python extraction/run_extraction.py --model sonnet --overwrite
```

Outputs are written under `extraction/` and are intentionally ignored by git.

## Phase 2

Give the visualization agent these artifacts:

- `corpus/raw_events.jsonl`
- `extraction/entity_dimensions.jsonl`
- `space/reference_dimensions.json`
- `space/space_definition.md`
- `visualization/agent_prompt.md`

The visualization stage must observe the representation, not invent the mathematics.

## Not implemented yet

This experiment intentionally does not define embeddings, distance, similarity, correlation, collapse, relationship scoring, graph edges, or ambiguity formulas.

Those are to be developed after the first interactive visualization is inspected.
