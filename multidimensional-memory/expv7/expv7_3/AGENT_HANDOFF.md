# V7.2 Agent Handoff

## Agents
Run only Claude Code and Copilot.

Do not inspect another agent's output until your own independent writer + consumer run is complete.

## Phase 0 — reset / reproduce
```bash
cd /mnt/data/expv7_2
python src/generate_v71.py
python src/build_rag.py
python src/build_v6_memory.py
pytest -q
```

Read:
- README.md
- EXP-V7.2.md
- data/benchmark_v7_1.json
- data/conversation_v7_1.jsonl
- data/rag_index.json
- schemas/agent_result_v71.schema.json

You may inspect the schema and corpus. Do NOT open `data/v6_memory.json` until your writer artifact is frozen and memory evaluation begins. Treat it as gold/evaluation data.

## Phase 1 — BUILD MEMORY
Using only the conversation and schema/design rules, build your own V6 memory.

Output:
`results/<agent>.memory.json`

Requirements:
- append-only observations
- canonical propositions
- relationships
- temporal state histories
- ambiguity
- conflict/belief history
- negative knowledge with scope/completeness
- provenance
- source event IDs
- no invented facts
- preserve superseded observations

Do not use the delayed queries to selectively construct memory. Build memory from the corpus before reading query-specific gold answers.

## Phase 2 — MEMORY EVALUATION
Only after your memory artifact is frozen, compare it against `data/v6_memory.json` and benchmark annotations.

Create:
`results/<agent>.memory_eval.json`

Report precision/recall or exact counts only when the matching method is deterministic and documented. Otherwise report raw mismatches.

## Phase 3 — CONSUMPTION
Run delayed queries under:
1. RAW
2. RAG
3. V6-GENERATED
4. V6-GENERATED+RAW

For V6-GENERATED, use ONLY your generated memory. No raw transcript.
For V6-GENERATED+RAW, use generated memory plus only linked raw events.
For RAG, use actual deterministic retrieval and exact retrieved chunks. Never add missing chunks manually.

Output:
- results/<agent>.RAW.json
- results/<agent>.RAG.json
- results/<agent>.V6-GENERATED.json
- results/<agent>.V6-GENERATED+RAW.json
- results/<agent>.report.md

## Phase 4 — CROSS-AGENT HANDOFF
Only after your independent run is complete.

### Claude → Copilot
Claude freezes `claude.memory.json`.
Copilot receives only that memory + delayed queries + schema.
No raw conversation. No gold memory. No Claude result report.

### Copilot → Claude
Copilot freezes `copilot.memory.json`.
Claude receives only that memory + delayed queries + schema.
No raw conversation. No gold memory. No Copilot result report.

Record:
- writer
- reader
- memory record count
- memory artifact SHA-256
- reader correctness
- unsupported claims
- evidence IDs
- missing/ambiguous records encountered

## Phase 5 — VALIDATION
Validate JSON against schema where applicable.
Run:
```bash
pytest -q
python src/validate_v71.py
```

Do not fabricate token or latency numbers.

## DO NOT
- inspect another agent before your own run
- use gold memory while writing
- use benchmark answers while writing
- modify the benchmark
- change the retrieval policy
- resolve ambiguity without evidence
- collapse conflicting observations
- treat retrieval absence as negative knowledge
- delete old temporal states
- claim V6 wins
