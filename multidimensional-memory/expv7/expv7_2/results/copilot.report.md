# EXP-V7.2 Copilot Report

## Execution

- Agent: `copilot`
- Corpus: 1,200 events
- Writer artifact: `results/copilot.memory.json`
- Writer records: 31
- Writer SHA-256: `d924ded34a6027a8afcc772c46c4d3fa0e7f1e7607505d0551b11d20567791b0`
- Conditions: RAW, RAG, V6-GENERATED, V6-GENERATED+RAW
- Consumption records: 32
- Independent result schema validation: passed

## Results

| Condition | Cases | Correct | Incorrect | Unsupported |
|---|---:|---:|---:|---:|
| RAW | 8 | 8 | 0 | 0 |
| RAG | 8 | 7 | 1 | 0 |
| V6-GENERATED | 8 | 8 | 0 | 0 |
| V6-GENERATED+RAW | 8 | 8 | 0 | 0 |

The result schema supplied by the workspace only permits `V6`, not `V6-GENERATED`; generated-memory result records therefore use the schema-compatible condition value `V6` in the two generated-memory files. The filenames and this report identify those arms as V7.2 generated memory.

## Memory construction

The writer selected the 20 substantive signal events from the corpus and preserved all 20 unique source event IDs. The artifact contains immutable observations plus propositions, relationships, a four-state webhook history, unresolved ambiguity, inferred-to-confirmed belief history, scoped negative knowledge, and an ordered provenance chain. No source event IDs were invented or missing in the deterministic evaluation.

Memory evaluation: 20/20 unique observation source events matched the gold memory observations, with deterministic source-event precision 1.0 and recall 1.0. All required derived dimensions were present. Free-text semantic equivalence was not independently scored.

## Failure analysis

The only failure was `V71-TIME-01` under RAG. The actual bounded retrieval returned chunks containing `E0233` and `E0401`, but missed later events `E0887` (temporary disablement) and `E1190` (re-enablement). The answer therefore reported the evidence boundary and did not claim a latest state. This is retrieval-related; it is not evidence of a generated-memory failure.

No failures occurred in RAW, V6-GENERATED, or V6-GENERATED+RAW. Ambiguity remained unresolved, belief evolution preserved inference and confirmation, and scoped negative knowledge distinguished the billing review from the different project.

## Retrieval observations

RAG used the actual six-chunk deterministic retrieval for each case. Exact chunk IDs and scores are in `copilot.RAG.json`. Required temporal events missed: `E0887`, `E1190`. No chunks were manually added and no whole-corpus fallback was used.

## Generated-memory observations

V6-GENERATED used only Copilot's frozen memory artifact. V6-GENERATED+RAW added only the linked raw event IDs. The temporal state record `S-WEBHOOK`, ambiguity record `A-HE`, belief record `B-TRANSACTION`, negative record `N-MONGODB`, and provenance record `PROV-DYNAMO` were used directly. No generated-memory answer required raw evidence.

## Cross-agent handoff

Claude → Copilot was completed after the independent run: Claude memory record count 50, SHA-256 `d5a71e9ce6aedddc0c4ce8e17e48a11388088547e2839842e9be6ceb2abfcf0b`, reader correctness 8/8, unsupported claims 0. The handoff record is `results/claude_to_copilot.json`.

Copilot → Claude was not executed by this agent because it requires a Claude reader execution; no result is fabricated.

## Measurements and validation

Input tokens, retrieval latency, and answer latency were unavailable and remain `null` in JSON. Local artifact byte size and SHA-256 were measurable and recorded.

Custom schema validation passed for all 32 Copilot result records. The supplied `src/validate_v71.py` is V7.1-only, scans all result JSON files, and rejects a V7.2 condition/artifact; it was not modified. Baseline tests passed: `4 passed` with third-party pytest plugin autoload disabled.
