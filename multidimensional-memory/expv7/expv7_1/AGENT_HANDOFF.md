# V7.1 Agent Handoff

## Current agents
Run only:
- Claude Code
- Copilot

Do NOT wait for or invoke Codex. It is excluded because of the current rate limit until 12:19 AM.

## Independence rule
Complete your own full run before inspecting another agent's results. Do not modify the benchmark, expected answers, or retrieval code to improve your own result.

## Step 1 — setup
```bash
cd /mnt/data/expv7_1
python src/generate_v71.py
python src/build_rag.py
python src/build_v6_memory.py
pytest -q
```

Read:
- `README.md`
- `EXP-V7.1.md`
- `data/benchmark_v7_1.json`
- `data/conversation_v7_1.jsonl`
- `data/rag_index.json`
- `data/v6_memory.json`
- `schemas/agent_result_v71.schema.json`

## Step 2 — run all four conditions
For every benchmark case run:
- RAW
- RAG
- V6
- V6+RAW

Do not substitute summaries for the supplied condition evidence.

### RAW
Use the exact raw event IDs specified by the case.

### RAG
Run the deterministic retriever. Record the exact retrieved chunk IDs and scores. Do not manually add a missing chunk.

### V6
Use only the V6 records selected for the case. Do not inspect raw transcript text while answering.

### V6+RAW
Use V6 plus only the linked raw evidence.

## Step 3 — answer protocol
For each case:
1. Read the delayed query.
2. Answer only from the supplied condition evidence.
3. Preserve uncertainty.
4. Preserve overlapping conflict.
5. Reconstruct temporal state in order.
6. Distinguish `not_discussed` from `not_retrieved`.
7. Record all evidence IDs actually used.

## Step 4 — results
Create:
- `results/<agent_id>.RAW.json`
- `results/<agent_id>.RAG.json`
- `results/<agent_id>.V6.json`
- `results/<agent_id>.V6+RAW.json`
- `results/<agent_id>.report.md`

Validate each JSON against `schemas/agent_result_v71.schema.json`.

## Step 5 — cross-agent handoff
Do this only after the independent four-condition run.

### Handoff A
Claude acts as writer. Claude produces a V6 memory file from the corpus using the benchmark memory schema. Copilot receives that memory file plus the delayed queries, with no raw conversation. Copilot answers and records results.

### Handoff B
Copilot acts as writer. Copilot produces a V6 memory file from the corpus. Claude receives only that memory file plus delayed queries and answers.

Record:
- writer agent
- reader agent
- memory artifact hash if available
- cases correct
- unsupported claims
- evidence IDs

## Do not do
- Do not fabricate token counts or latency.
- Do not inspect another agent's results before your own run.
- Do not change expected answers.
- Do not claim V6 wins.
- Do not call a RAG miss a memory failure without checking the retrieval log.
