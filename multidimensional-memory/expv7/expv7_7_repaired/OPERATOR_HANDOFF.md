# V7.7 Repaired — Operator Handoff

## Your role
You are the experiment operator and chain-of-custody controller. Do not help an agent answer the benchmark. Preserve isolation, freeze artifacts, run validators, and record failures.

## Phase 0 — dataset validation
1. Work from a clean checkout of this package.
2. Run `pytest -q`.
3. Run `python src/validate.py`.
4. Do not proceed if validation fails.

The validator must confirm: 1,200 events, 12 conversations, 216 durable events, 96 queries, every required evidence ID exists, every required ID is durable, every required ID belongs to the query conversation, and no required evidence is generic filler.

## Phase 1 — clean-room writers
Run Claude, Codex, and Copilot independently and in parallel. Give each only the writer-visible corpus, public schema, experiment protocol, and `RUN_PROMPT.md`. Never provide evaluator gold, expected evidence IDs, other agents' outputs, or previous results.

Expected writer artifacts:
- `results/<agent>.memory.json`
- `results/<agent>.memory_eval.json`
- `results/<agent>.report.md`

## Phase 2 — freeze
After each writer finishes, copy its memory to a unique frozen path and compute SHA-256. Do not edit or overwrite a frozen artifact. If an artifact changes, record an integrity failure and create a new run ID.

Recommended layout:
```
frozen/<agent>/memory.json
frozen/<agent>/report.md
frozen/<agent>/manifest.json
```

## Phase 3 — retrieval
Run the same 96 queries with fixed parameters for RAW, BM25, DENSE, HYBRID, GraphRAG, HippoRAG2, RAPTOR, Graphiti, MEMORY, and MEMORY+RAW where executable. Capture actual retrieved evidence. If a system cannot run, write `NOT_RUN` and the reason. Never substitute a proxy silently.

### Graphiti
Graphiti must ingest the raw conversation, not our generated memory. Record Graphiti version, backend, LLM provider, retrieval configuration, and actual evidence returned. If the required backend/API/dependency is unavailable, mark `NOT_RUN`.

## Phase 4 — reader
For MEMORY, the reader receives only the frozen memory plus the future query and reader instructions. It does not receive the original conversation.

## Phase 5 — cross-agent
Only after all three writer memories are frozen, run all six directed handoffs:
- Claude → Codex
- Claude → Copilot
- Codex → Claude
- Codex → Copilot
- Copilot → Claude
- Copilot → Codex

Run these as a separate phase so no agent has to wait on another writer during construction.

## Phase 6 — result integrity
Validate every result file. Record dataset hash, prompt hash, memory hash, tool/version, start/end time, and status. Do not estimate missing token, latency, or cost data. Use null/NOT_RUN.

## Stop conditions
- dataset validation failure
- writer sees evaluator files
- frozen artifact modified
- missing source references
- benchmark/query mismatch
- retrieval implementation cannot be verified
- result file overwritten

## Reruns
Never overwrite a previous run. Use a new run ID, e.g. `V77-R01`, `V77-R02`.

## RETRIEVAL EXECUTION

After all writer memories are frozen:

```bash
python run_retrieval.py --condition raw
python run_retrieval.py --condition bm25 --top-k 24
python run_retrieval.py --condition semantic --top-k 24
python run_retrieval.py --condition hybrid --top-k 24
```

For a frozen generated memory:

```bash
python run_memory_retrieval.py --memory /absolute/path/to/frozen/memory.json
```

Results go to `results/retrieval/`. Do not change top-k after seeing results. A configuration change is a new run.

Graphiti must consume raw conversation and run through the real Graphiti implementation/backend. If unavailable, record `NOT_RUN` and the reason. Never substitute a custom graph implementation.
