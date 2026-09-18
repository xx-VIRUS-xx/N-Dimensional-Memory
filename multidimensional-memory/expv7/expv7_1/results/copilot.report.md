# EXP-V7.1 Copilot Report

## Execution

- Agent identity: `copilot`
- Cases: 8
- Conditions: 4 (`RAW`, `RAG`, `V6`, `V6+RAW`)
- Total records: 32
- Validation: passed for the four Copilot result files

## Results

| Condition | Cases | Correct | Incorrect | Unsupported |
|---|---:|---:|---:|---:|
| RAW | 8 | 8 | 0 | 0 |
| RAG | 8 | 7 | 1 | 0 |
| V6 | 8 | 8 | 0 | 0 |
| V6+RAW | 8 | 8 | 0 | 0 |

Correctness is based on the applicable benchmark correctness fields for each case. All records have `unsupported_claims: 0`.

## Failure analysis

One failure was observed in `RAG` for `V71-TIME-01`. The retrieved chunks contained the early polling and webhooks events (`E0233`, `E0401`) but missed the later disablement and re-enablement events (`E0887`, `E1190`). The answer correctly reported the evidence boundary and did not invent the latest state, but it could not satisfy the full temporal rubric. This is a retrieval-related failure, not a V6 representation failure.

## Retrieval observations

The deterministic RAG retrieval returned six chunks per case. Required signal coverage was present for every case in the actual retrieval log:

- `V71-HIST-01`: `C0000`, `C0005`, `C0011` contained `E0005`, `E0067`, `E0141`.
- `V71-DEC-01`: `C0021`, `C0060`, `C0014` contained `E0178`, `E0263`, `E0731`.
- `V71-ACT-01`: `C0086`, `C0066`, `C0029` contained `E0356`, `E0622`, `E1033`.
- `V71-TIME-01`: `C0033` and `C0019` contained `E0233` and `E0401`; `E0887` and `E1190` were missed by the bounded retrieval.
- `V71-AMB-01`: `C0025` and `C0042` contained `E0312` and `E0515`.
- `V71-CONFLICT-01`: `C0037` contained `E0448` and `E0449`.
- `V71-NEG-01`: `C0045` and `C0091` contained `E0548` and `E1102`.
- `V71-PROV-01`: `C0037`, `C0011`, `C0000`, `C0005`, and `C0066` contained the required provenance events.

RAG retrieval was lexical and included distractor events. No missing chunk was manually added, and no full-corpus fallback was used. The exact chunk IDs and scores are recorded in `copilot.RAG.json`.

## Memory observations

V6 used only case-selected records from the generated `data/v6_memory.json`:

- Historical, decision, and action cases used observation records plus relationship records where materialized.
- The temporal case used four observations and `MSTATE-WEBHOOK`, preserving all state transitions and current state.
- The ambiguity case used `MAMB-HE`, with candidates Rahul and Arjun and `resolution: null`.
- The conflict case used `MREL-CONFIRM`, preserving Claude's inference and Rahul's later confirmation.
- The negative-knowledge case used `MNEG-MONGO`, including `complete_for_review` and the different-project qualifier for `E1102`.
- The provenance case used `MPROV-BILLING`, preserving the ordered source and agent roles.

No V6 answer required raw conversation. V6+RAW included the same memory IDs plus only the case-linked raw event IDs.

## Measurements

Input-token counts, retrieval latency, and answer latency were not exposed by this manual provider-neutral run. All JSON measurement fields are therefore `null`; no measurements were invented.
