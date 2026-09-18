# EXP-V7.4 Copilot Report

## Execution provenance

- Agent: `copilot`
- Corpus: 1,200 events
- Writer phase: delegated to a fresh clean-room subagent because the main session had prior experiment context.
- Writer input: `data/conversation_v7_4_unlabeled.jsonl` and V7.4 design/schema only.
- Frozen memory: `results/copilot.memory.json`
- SHA-256: `a7a44a01d5e8de94ffccce2d5e277d16960d7751dd40f3e48f2648d8148ac702`

## Selection quality

The writer produced 6 records retaining 20 unique source events. Against the hidden 20-event gold set, exact source-event matching yielded:

| Metric | Value |
|---|---:|
| Precision | 1.000 |
| Recall | 1.000 |
| F1 | 1.000 |
| Retention | 20 / 1,200 = 1.667% |
| Compression | 98.333% |
| False-retained events | 0 |
| Missed relevant events | 0 |

## Memory construction quality

The artifact includes durable billing and Redis decisions, invoice action/outcome history, webhook state transitions, unresolved deployment ambiguity, belief evolution, scoped MongoDB negative knowledge, and provenance. All 20 retained IDs are real and match the hidden gold IDs. Free-text semantic equivalence and relation quality were not independently scored by an automated matcher; the compact six-record grouping is disclosed for audit.

## Consumption quality

| Condition | Cases | Correct | Incorrect | Unsupported |
|---|---:|---:|---:|---:|
| RAW | 8 | 8 | 0 | 0 |
| RAG | 8 | 3 | 5 | 0 |
| V6-GENERATED | 8 | 8 | 0 | 0 |
| V6-GENERATED+RAW | 8 | 8 | 0 | 0 |

The legacy V7.1 schema only permits `V6`, so the two generated-memory files use `condition: V6` for schema compatibility while their filenames identify the V7.4 generated arms.

## RAG failures

The actual deterministic top-six retrieval was used without manual chunk additions:

- `V74-HIST-01`: retrieved `E0014` and `E0068`, missed `E0142`.
- `V74-DEC-01`: retrieved `E0179` and `E0264`, missed `E0732`.
- `V74-ACT-01`: retrieved `E0623` and `E1034`, missed `E0357`.
- `V74-TIME-01`: missed all required events `E0402`, `E0888`, `E1191`.
- `V74-AMB-01`: retrieved `E0516`.
- `V74-BELIEF-01`: retrieved `E0450`, missed `E0449`.
- `V74-NEG-01`: retrieved `E0549` and `E1103`.
- `V74-PROV-01`: retrieved `E0449` and `E0803`, missed `E0068`, `E0142`, and `E0450`.

Exact chunk IDs and scores are recorded in `copilot.RAG.json`. These failures are retrieval-related; no fallback search was used.

## Cross-agent quality

Claude memory → Copilot and Copilot memory → Claude were both marked `not_executed` because no Claude V7.4 writer artifact or reader execution was available. No other model was impersonated and no correctness values were fabricated.

## Tooling/specification defects

1. The inherited `src/build_rag.py` expects `conversation_v7_1.jsonl` and `benchmark_v7_1.json`, which are absent from the V7.4 workspace. RAG was materialized with the same deterministic lexical/top-six policy against the V7.4 unlabeled corpus and benchmark query set.
2. The inherited `src/validate_v71.py` is V7.1-specific and was not used as the V7.4 validator. A V7.4-specific `src/validate_v74.py` was added.
3. The schema remains the V7.1 result schema and does not include `V6-GENERATED`; generated result files retain schema-compatible `V6` values.

## Measurements and validation

Token counts, retrieval latency, and answer latency were unavailable and remain `null`. V7.4 validation passed: 6 memory records, 20 source events, and four result files with 8 records each. The available tests passed when run separately with plugin autoload disabled: `4 passed`. The combined generator plus inherited RAG setup command failed before tests because of the stale V7.1 filename dependency; this is recorded above.
