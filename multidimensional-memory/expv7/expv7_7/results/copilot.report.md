# EXP-V7.7 Copilot Report

## Execution

- Agent: Copilot
- Writer phase: delegated to a fresh clean-room subagent.
- Public writer corpus: 1,200 events across 12 conversations.
- Frozen memory: `results/copilot.memory.json`
- Frozen artifact SHA-256: `4932ba0fb82cd64ec4fbaa89cff687a2d32d6f6af70682be81a4abf84a9986e8`
- Memory records: 12
- Retained source-event IDs: 216

## Memory construction

The artifact is schema-valid and compact at 12 conversation-level records. It preserves decisions, revisions, actions/outcomes, temporal state, ambiguity, conflicts, negative knowledge, provenance, and source IDs.

## Selection evaluation

Exact source-event matching failed because the writer used IDs such as `CONV-01:100002`, while the evaluator gold uses IDs such as `C01E003`. Therefore the exact metrics are:

| Metric | Value |
|---|---:|
| Precision | 0.000 |
| Recall | 0.000 |
| F1 | 0.000 |
| Retention | 216 / 1,200 = 18.0% |
| Compression | 82.0% |
| False-retained IDs under exact matching | 216 |
| Missed gold IDs under exact matching | 216 |

This is an identifier/provenance compatibility failure. No post-freeze normalization was applied and no semantic equivalence was claimed.

## Retrieval and consumption

BM25, DENSE, HYBRID, GRAPHRAG, HIPPORAG2, RAPTOR, RAW, MEMORY, and MEMORY+RAW result files were not generated. The V7.7 workspace contains no retrieval indexes, future-query file, reader schema, or runnable baseline adapters. The adapters README explicitly requires real implementations and forbids silently replacing advanced systems with proxies.

## Tooling limitations

- `pytest -q` reports no tests ran because `tests/test_benchmark.py` contains top-level assertions rather than pytest test functions.
- Running the assertion file directly passed the public benchmark checks.
- The evaluator folder exposes gold material only after writer freeze, but no runnable evaluator/reader pipeline is supplied.
- The writer/evaluator source-event ID namespaces are incompatible, preventing exact provenance scoring.

## Status

Only the clean-room memory artifact and its explicit evaluation report are complete. No retrieval or answer-quality result is claimed.
