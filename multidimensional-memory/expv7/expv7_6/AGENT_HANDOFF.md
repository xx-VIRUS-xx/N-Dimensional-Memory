# EXP-V7.6 Agent Handoff

## Mission
Run EXP-V7.6 as a falsification-oriented benchmark of model-independent persistent conversational memory.

## Before running
1. Read `README.md` and `EXP-V7.6.md`.
2. Use only the supplied V7.6 corpus/data and frozen schema.
3. Do not inspect other agents' results.
4. Do not use gold answers or gold memory during writer construction.
5. Freeze and hash your memory before consuming future queries.

## Writer phase
Build structured memory from the conversation only.

Preserve:
- observations
- propositions
- relationships
- temporal histories
- decisions
- actions/outcomes
- ambiguity
- conflicts
- negative knowledge
- provenance

Do not collapse history into only the latest state.

## Reader phase
Evaluate every condition using the same future query set:
- RAW
- BM25
- SEMANTIC_RAG
- HYBRID_RAG
- MEMORY
- MEMORY+RAW

Record actual evidence used. If a condition does not provide enough evidence, say so. Do not guess.

## Instrumentation
Record actual:
- tokens
- bytes
- latency
- cost

Use `null` when unavailable.

## Cross-agent
Do not attempt cross-agent handoff while the other writer is still running. Both writers finish first. A separate post-run phase performs:
- Claude memory → Copilot reader
- Copilot memory → Claude reader

## Integrity
Do not rewrite a frozen memory artifact after evaluation. If a repair is unavoidable, create a new version and explicitly disclose the change.

## Required outputs
Write all artifacts under `results/` using the exact names defined in `EXP-V7.6.md`.
