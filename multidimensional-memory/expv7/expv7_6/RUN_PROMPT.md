# EXP-V7.6 Run Prompt

You are participating in EXP-V7.6, a research benchmark for model-independent persistent conversational memory.

Read:
- README.md
- EXP-V7.6.md
- AGENT_HANDOFF.md

Your task has two phases.

## Phase 1 — clean-room memory writer

Given only the V7.6 conversation corpus and the memory schema, construct a persistent memory artifact that preserves durable information useful for future queries.

You must not inspect:
- gold answers
- gold memory
- another agent's results
- future query files

The memory must preserve historical observations rather than overwriting them.

After writing memory:
1. validate it
2. compute its integrity hash
3. freeze it
4. record the writer/model/configuration

Do not modify the frozen memory during reader evaluation.

## Phase 2 — reader evaluation

Using the post-freeze future query set, evaluate:

1. RAW
2. BM25
3. SEMANTIC_RAG
4. HYBRID_RAG
5. MEMORY
6. MEMORY+RAW

Use the same queries for every condition.

For every case record:
- answer
- correct/incorrect
- unsupported_claim
- evidence_used
- provenance where applicable
- token counts when exposed
- retrieval latency when exposed
- answer latency when exposed
- cost when exposed

Do not guess when evidence is insufficient.

## Important
The purpose is not to make memory win. The purpose is to determine whether the memory hypothesis survives realistic data and stronger baselines.

If a baseline wins a case, record it accurately.
If memory fails, preserve the failure.
