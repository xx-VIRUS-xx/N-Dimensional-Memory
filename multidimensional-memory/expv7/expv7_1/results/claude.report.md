# EXP-V7.1 — Claude Code report

## Execution
- agent identity: `claude`
- number of cases: 8 (V71-HIST-01, V71-DEC-01, V71-ACT-01, V71-TIME-01, V71-AMB-01, V71-CONFLICT-01, V71-NEG-01, V71-PROV-01)
- number of conditions: 4 (RAW, RAG, V6, V6+RAW)
- total records: 32 (8 × 4)
- validation result: `python src/validate_v71.py` → `result validation passed`; additionally validated all 32 records directly against `schemas/agent_result_v71.schema.json` via `jsonschema.validate` → all 32 passed. `pytest -q` → 4 passed (after running `generate_v71.py`, `build_rag.py`, `build_v6_memory.py` as instructed; note `pytest` required `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` in this environment due to an unrelated local plugin conflict on the `--browser` CLI flag, not related to this experiment's code).

## Results

Correctness is counted per applicable `correctness.*` field (null fields are not counted, per schema — a case only has non-null fields for the categories its query actually tests).

| Condition | Cases | Applicable checks | Correct | Incorrect | Unsupported claims |
| --------- | ----: | -----------------: | ------: | --------: | ------------------: |
| RAW       |     8 |                  15 |      15 |         0 |                    0 |
| RAG       |     8 |                  16 |      14 |         2 |                    0 |
| V6        |     8 |                  15 |      15 |         0 |                    0 |
| V6+RAW    |     8 |                  16 |      16 |         0 |                    0 |

(RAG and V6+RAW have 16 applicable checks vs. 15 for RAW/V6 because V71-TIME-01 under RAG produced explicit `factual: false, temporal: false` — two failed checks that are still "applicable," whereas under RAW/V6, V71-TIME-01 only used 2 checks (factual, temporal) all correct; the count differs by which fields ended up non-null per my own answer, not by design.)

## Failure analysis

**Case: V71-TIME-01, Condition: RAG.**
- What was missing/incorrect: the deployment/webhook history has 4 signal events (E0233 polling start, E0401 move to webhooks, E0887 webhooks disabled, E1190 webhooks re-enabled). The deterministic RAG retrieval for this case (`data/rag_retrievals_v71.json`, key `V71-TIME-01`) returned chunks `C0033, C0000, C0005, C0011, C0019, C0037`. I checked each returned chunk's `event_ids` list directly against the required IDs: only `E0233` and `E0401` fall inside the retrieved chunks; `E0887` and `E1190` do not appear in any of the 6 retrieved chunks. So the retrieved evidence supports only "polling → webhooks" and cannot support or rule out any state change after 2026-03-11.
- What evidence was actually available: 2 of 4 required events (E0233, E0401), confirmed by directly inspecting `rag_retrievals_v71.json`'s `event_ids` arrays — not inferred.
- Cause: **retrieval-related**, not representation- or reasoning-related. The lexical/deterministic retrieval policy in `src/build_rag.py` did not surface the two chunks containing E0887/E1190 within its top-6 results for this query. This is a retrieval-coverage gap in the fixed policy for this specific case, verified against the actual retrieval log rather than assumed.
- My answer under RAG explicitly reported the evidence as insufficient for "latest known state" rather than asserting webhooks-active (which would have been factually right by luck, not by support) or asserting webhooks-disabled (the last state visible in RAW/V6, which the RAG evidence also can't support). Both `factual` and `temporal` were marked `false` since the RAG condition could not correctly reconstruct the full state history or confidently state the latest state per the benchmark's gold timeline — the answer is honest about the gap but does not fulfill the query.

No other failures occurred in RAW, V6, or V6+RAW for this run.

## Retrieval observations (RAG)

Per case, retrieved chunk IDs (with scores) are recorded verbatim from `data/rag_retrievals_v71.json` in `results/claude.RAG.json`'s `retrieved_chunks` field. Coverage check (required event IDs vs. event IDs contained in retrieved chunks), computed directly from the retrieval log:

| Case | Required events | Retrieved chunks cover | Missing |
|---|---|---|---|
| V71-HIST-01 | E0005, E0067, E0141 | all 3 | none |
| V71-DEC-01 | E0178, E0263, E0731 | all 3 | none |
| V71-ACT-01 | E0356, E0622, E1033 | all 3 | none |
| V71-TIME-01 | E0233, E0401, E0887, E1190 | E0233, E0401 | **E0887, E1190** |
| V71-AMB-01 | E0312, E0515 | all 2 | none |
| V71-CONFLICT-01 | E0448, E0449 | all 2 | none |
| V71-NEG-01 | E0548, E1102 | all 2 | none |
| V71-PROV-01 | E0067, E0141, E0448, E0449, E0802 | all 5 | none |

7 of 8 cases had fully sufficient retrieved evidence for this run's fixed top-6 policy. V71-TIME-01 was the sole retrieval gap.

## Memory observations (V6)

- Memory records used per case are listed in `evidence_used` in `results/claude.V6.json` (e.g. `M-E0005`, plus derived records like `MREL-BILLING-01`, `MSTATE-WEBHOOK`, `MAMB-HE`, `MREL-CONFIRM`, `MNEG-MONGO`, `MPROV-BILLING`).
- Relationship/state-transition records used: `MREL-BILLING-01`/`02` (HIST-01), `MREL-REDIS-01`/`02` (DEC-01), `MSTATE-WEBHOOK` (TIME-01, a 4-entry `state_history` with `valid_from`/`valid_to` and a `current_state` field).
- Ambiguity records used: `MAMB-HE` (AMB-01) — `resolution: null`, `status: unresolved`.
- Provenance/belief-history records used: `MREL-CONFIRM` (CONFLICT-01, inferred→confirmed chain), `MPROV-BILLING` (PROV-01, 5-step chain across Rahul/Claude/Rahul/Copilot with distinct roles: observation, confirmation, inference, confirmation, later_memory_read).
- Negative-knowledge record used: `MNEG-MONGO` (NEG-01) — includes a `qualifier` distinguishing the in-scope negative from the out-of-scope E1102 mention.
- One gap: `V71-ACT-01` has **no** derived relationship/state record in `data/v6_memory.json` — only the 3 raw `observation`-type records (`M-E0356`, `M-E0622`, `M-E1033`) exist under that `case_id`. The V6 answer for this case was reconstructed by ordering these three raw observations by timestamp, not from a pre-derived relationship, since none was supplied.
- Reconstruction did **not** require the raw conversation for any case under the V6-only condition — all 8 cases were answerable from the supplied memory records alone (though ACT-01 required reasoning over raw-observation timestamps rather than a pre-computed state/relationship record).

## Measurements
- input tokens: Not available (manual, non-instrumented interactive run; `null` in all 32 records)
- latency: Not available (manual, non-instrumented interactive run; `null` in all 32 records)

## Note on interpretation
Per the handoff's Step 15/§10 instructions, this report does not claim general superiority of V6 over RAG or vice versa. It reports one specific, verified retrieval-coverage gap in the fixed RAG policy for V71-TIME-01, traced directly to the retrieval log rather than assumed, and notes that V6 (and V6+RAW) answered that same case correctly because its structured `state_history` record was constructed by the benchmark's canonical compiler directly from the full event set rather than by lexical retrieval — this reflects the benchmark's documented "important limitation" that V6 here measures downstream representation utility, not independent LLM extraction quality.
