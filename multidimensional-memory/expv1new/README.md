# N-Dimensional Memory - EXP-V1NEW

Clean-room implementation of the NDM idea.

## Goal

Build a persistent, loss-aware memory layer for agents that preserves historical context across multiple semantic dimensions instead of collapsing a conversation into a single current-state summary.

The JSON representation is an experimental wire format. The intended product is an agent plugin and eventually a database/storage layer.

## Core rule

Each source event is interpreted independently by an LLM at ingestion time.

The interpreter may extract:
- entities and identity
- actor / participant roles
- propositions and state
- belief and stance
- temporal information
- scope
- references to earlier context
- causality only when supported by the source
- contradiction, correction, supersession
- ambiguity and unresolved candidates
- negative knowledge
- provenance

Chronological order alone must never become causality.

Unresolved ambiguity is preserved and may be resolved later by subsequent evidence or explicit human intervention.

## Experiment path

1. Small clean-room corpus.
2. Inspect the interpreted memory manually.
3. Run reconstruction queries against the stored dimensions.
4. Add adversarial cases only when the representation exposes a real missing dimension.
5. Run a small LongBench slice.
6. Scale toward LongBench evaluation.

## Separation

The ingestion interpreter and reconstruction/query layer are separate.

The query layer must not reverse-engineer missing semantics from raw event prose when those semantics should have been captured during ingestion.

source events -> LLM interpretation -> persistent NDM -> reconstruction -> agent context
