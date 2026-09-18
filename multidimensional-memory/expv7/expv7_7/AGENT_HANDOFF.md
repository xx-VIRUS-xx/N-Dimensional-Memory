# V7.7 Agent Handoff

## Phase A — parallel clean-room writers
Run Claude, Copilot and Codex independently.

Produce:
- results/<agent>.memory.json
- results/<agent>.memory_eval.json
- results/<agent>.report.md

Do not wait for another agent. Do not read another agent's files.

## Phase B — baseline retrieval
Run the same 96 future queries through every retrieval baseline that is available.
Materialize actual evidence sets.

Required result files:
- <agent>.RAW.json
- <agent>.BM25.json
- <agent>.DENSE.json
- <agent>.HYBRID.json
- <agent>.GRAPHRAG.json
- <agent>.HIPPORAG2.json
- <agent>.RAPTOR.json
- <agent>.MEMORY.json
- <agent>.MEMORY+RAW.json

## Phase C — cross-agent
After ALL three memories are frozen, run six directed writer→reader evaluations.

## Phase D — integrity
Record SHA-256 of frozen memory artifacts and manifests. A hash mismatch is a reported integrity failure, not a repair to hide.
