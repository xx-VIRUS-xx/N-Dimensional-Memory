# EXP-V7.1 — Real Retrieval vs Real Persistent Memory

V7.1 is the next controlled step after V7.0. It keeps the same research question but removes the biggest weakness in V7.0: RAG and V6 were represented by condition-scoped evidence identifiers rather than independently materialized retrieval/memory systems.

## Agents
- Claude Code
- Copilot

Codex is intentionally excluded from this run because of the current rate limit. This is a temporary experimental constraint, not a result about Codex.

## Goal
Compare four conditions using the **same long-horizon conversation corpus and delayed queries**:

1. RAW — complete relevant raw transcript supplied.
2. RAG — actual deterministic chunking + retrieval; only retrieved chunks supplied.
3. V6 — structured persistent memory supplied; raw transcript withheld.
4. V6+RAW — structured memory plus the minimum linked raw evidence.

V7.1 is primarily a retrieval/memory-utility experiment. It does not claim that the memory extractor itself is solved.

## Dataset design
- 1,200 synthetic conversation events.
- 20 deliberately relevant signal events distributed across the benchmark cases.
- Hundreds of distractor events sharing vocabulary with the signal events.
- Delayed queries that require history, temporal ordering, state reconstruction, ambiguity preservation, conflict preservation, negative knowledge, action/outcome, decisions, and provenance.
- Deterministic ground truth and deterministic RAG retrieval policy.

## Reproducibility
Run:
```bash
python src/generate_v71.py
python src/build_rag.py
python src/build_v6_memory.py
pytest -q
```

The generated artifacts are deterministic. RAG returns actual chunk IDs and lexical scores. V6 returns actual structured memory records, relationships, state histories, and provenance.

## Important limitation
The V6 condition uses a deterministic benchmark memory compiler from the benchmark's canonical event annotations. Therefore V7.1 measures **downstream utility of the representation/retrieval**, not the quality of an LLM's event extraction. A later experiment should separately measure writer/extraction quality.
