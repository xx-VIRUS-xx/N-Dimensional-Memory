# Codex V7.7 Memory Writer Report

## Files

- `results/codex.memory.json`
- `results/codex.memory_eval.json`
- `results/codex.report.md`

## Construction

Built from `data/conversation_v7_7_unlabeled.jsonl` only. I did not read evaluator gold, relevance labels, or other agent outputs while constructing the memory.

## Coverage Shape

- Source conversations: 12
- Source events: 1200
- Memory records: 252
- Unique retained source events: 240
- Source reference check: passed

The memory preserves durable decisions, replacement/supersession, failure observations, actions, validation outcomes, rollout state transitions, unresolved ambiguity, negative MongoDB knowledge scoped by service, provenance confirmation, and multi-hop failure-to-rollout dependencies.

## Integrity

- Memory SHA-256: `a8c23a518e53cf3959eb7d98dbf7bbf5bea37adedc35366be10d1eec043a6a87`
- Source corpus SHA-256: `80a32f4f6edde3f65fa3ac74dede2750214b4514b23d8ca1c2bec9f7b7b9fec6`

## Limitations

- The public schema is intentionally loose; record semantics are encoded in `record_type`, `content`, timestamps, status, and source IDs.
- Gold-based precision/recall and query-answer metrics are not computed here because the writer phase must not inspect evaluator files.
- Token counts and latency were not measured in this manual construction pass.
