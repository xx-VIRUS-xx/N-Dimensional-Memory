# EXP-V7.3 Copilot Report

## Execution provenance

- Agent: `copilot`
- Corpus: 1,200 events
- Writer phase: delegated to a fresh clean-room subagent because the main session had previously seen gold memory and prior V7.1/V7.2 results.
- Frozen writer artifact: `results/copilot.memory.json`
- Artifact SHA-256: `71aa87c544aa5dc8633344d40eb0f21af279dca6399000b2b888115f691d395f`
- Writer records: 19
- Retained unique source events: 20

## Writer methodology and selection

The writer selected durable decisions, actions/outcomes, state transitions, ambiguity, belief changes, scoped negative knowledge, and provenance-bearing events. It preserved source event IDs and represented the webhook evolution, unresolved `he` reference, Claude inference followed by Rahul confirmation, scoped MongoDB non-discussion, and invoice/Redis outcomes.

Using exact source-event matching against the evaluator's 20 relevant events:

| Metric | Value |
|---|---:|
| Selection precision | 1.000 |
| Selection recall | 1.000 |
| Selection F1 | 1.000 |
| Retention | 20 / 1,200 = 1.667% |
| Compression | 98.333% |
| False retained relevant IDs | 0 |
| Missed relevant IDs | 0 |

Observation precision and recall were both 1.0 under source-event matching. Required memory dimensions were present: propositions, relationships, temporal states, ambiguity, belief history, action/outcome, scoped negative knowledge, and provenance. Free-text semantic equivalence was not scored by an independent matcher.

## Consumption results

| Condition | Cases | Correct | Incorrect | Unsupported |
|---|---:|---:|---:|---:|
| RAW | 8 | 8 | 0 | 0 |
| RAG | 8 | 7 | 1 | 0 |
| V6-GENERATED | 8 | 8 | 0 | 0 |
| V6-GENERATED+RAW | 8 | 8 | 0 | 0 |

The supplied legacy schema only permits `V6`, not `V6-GENERATED`; the two generated-memory result files use schema-compatible `condition: V6`, while their filenames and this report identify the V7.3 generated arms.

## Failure and retrieval gap

The only consumption failure was `V71-TIME-01` under RAG. The deterministic top-six retrieval contained the polling and initial webhook events but missed the later disablement and re-enablement events. The answer reported that the latest state could not be established rather than inventing it. This is retrieval-related.

No failures occurred in RAW or either generated-memory arm. The generated artifact retained all four webhook source events and the full state sequence.

## Cross-agent handoff

Neither cross-agent direction was executable in this session because no Claude V7.3 writer artifact or Claude reader execution was available. Both required status files were created with `not_executed`; no correctness or unsupported-claim values were fabricated.

- Claude → Copilot: not executed; no Claude memory artifact present.
- Copilot → Claude: not executed; no Claude reader available.

## Tooling and specification defects

1. `AGENT_HANDOFF.md` is stale V7.2 text rather than V7.3 instructions. The attached `RUN_PROMPT.md` and `EXP-V7.3.md` were treated as controlling.
2. `data/conversation_v7_1.jsonl` still exposes `kind: signal/distractor` labels. Therefore the workspace does not actually provide the unlabeled writer corpus promised by V7.3. The fresh writer was explicitly instructed not to use those labels, but label exposure remains a methodological limitation.
3. The existing `agent_result_v71.schema.json` does not permit `V6-GENERATED`; generated-arm records use `V6` for schema compatibility. A V7.3-specific validator was added at `src/validate_v73.py` and was used instead of modifying the legacy validator.

## Measurements and validation

Token counts, retrieval latency, and answer latency were unavailable and remain `null`. The V7.3 validator passed: 19 memory records, 20 unique source events, and four result files with eight records each. Baseline tests passed: `4 passed` with third-party pytest plugin autoload disabled.
