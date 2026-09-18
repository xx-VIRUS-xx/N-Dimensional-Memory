# EXP-V7.5 Agent Run Prompt

You are participating in EXP-V7.5 — Distribution-Shifted Persistent Memory.

Use `expv7_5` and follow `EXP-V7.5.md` exactly.

## PHASE 1 — CLEAN-ROOM WRITER
Read only:
- `README.md`
- `EXP-V7.5.md`
- `protocol/writer_protocol.md`
- `schemas/memory_v75.schema.json`
- `data/*_unlabeled.jsonl`

Before freezing your memory, DO NOT read:
- `data/gold_annotations.json`
- `data/future_queries.json`
- `data/rag_index.json`
- any result file
- another agent's memory
- prior V7.x result summaries

Read the full unlabeled corpora. Autonomously identify durable conversational state. Do not optimize for anticipated questions. Preserve source IDs, temporal order, observation vs inference vs confirmation, uncertainty, conflicts, decisions, actions/outcomes, scoped negative knowledge and provenance.

Write `results/<your-agent>.memory.json`, then compute SHA-256 and freeze it. Do not modify it after freeze.

If your current session has already seen gold memory/results, delegate Phase 1 to a fresh clean-room subagent and disclose this in your report.

## PHASE 2 — MEMORY EVALUATION
Only after freeze, inspect evaluator-only gold annotations. Produce `results/<your-agent>.memory_eval.json` with selection and representation metrics. Do not alter the frozen memory.

## PHASE 3 — CONSUMPTION
Only after future queries are released, run:
- RAW
- RAG
- V6-GENERATED
- V6-GENERATED+RAW

RAG must use the actual deterministic retriever. No manual chunk selection and no full-corpus fallback.
V6-GENERATED must use only the frozen memory, not raw conversation.
Record token counts/latencies only if actually measured.

## PHASE 4 — POST-RUN CROSS-AGENT
Do NOT wait for another agent during your main run. The orchestrator will run cross-agent readers after both memories are frozen.
The reader must receive only the other agent's frozen memory, novel queries and schema. No original corpus, gold annotations or writer report.

## PHASE 5 — REPORT
Separate:
1. memory construction
2. selection quality
3. representation quality
4. retrieval quality
5. reader quality
6. cross-agent quality
7. efficiency

Disclose tooling defects. Never silently patch or fabricate measurements.
