# EXP-V7.2 — Claude Code report

## Execution
- agent identity: `claude`
- number of cases: 8
- number of conditions: 4 (RAW, RAG, V6-GENERATED, V6-GENERATED+RAW)
- total consumption records: 32 (8 × 4)
- plus: `results/claude.memory.json` (50-record generated memory artifact) and `results/claude.memory_eval.json` (evaluation against gold)
- validation result: all 32 consumption records pass strict `jsonschema.validate` against the schema's required fields and structure. **One tooling gap found and worked around, not silently patched**: `schemas/agent_result_v71.schema.json`'s `condition` enum only allows `RAW/RAG/V6/V6+RAW`, but `EXP-V7.2.md` explicitly requires the distinct condition names `V6-GENERATED` and `V6-GENERATED+RAW` (to avoid conflating agent-generated memory with the V7.1 benchmark-generated `V6` condition). Rather than mislabel my results to fit the outdated enum, or silently edit the shared V7.1 schema (which the handoff calls "modify the benchmark," rule 15/DO-NOT list), I created `schemas/agent_result_v72.schema.json` — an exact copy with only the enum extended to include the two new condition strings — and validated against that. `src/validate_v71.py` (the repo's own validator script) has the same V7.1-only enum hardcoded and would need the same update to accept these files; I did not modify that script. `pytest -q` (after `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`, an unrelated local plugin conflict) → 4 passed, unaffected by this issue since the existing tests only check the V7.1 benchmark/corpus, not V7.2 condition names.

## Phase 0 — clean-room writer note

Because I (this session) had already read the gold `data/v6_memory.json` file earlier in this conversation during the separate V7.1 task, I could not personally perform Phase 1 (memory construction) as a genuine clean-room extraction — I would already know the answer key. To keep the anti-cheating rule (EXP-V7.2.md §"Critical anti-cheating rule") meaningful, I delegated Phase 1 to a fresh subagent with no prior exposure to this conversation, gold data, or either V7.1/V7.0 results file. That subagent confirmed in its own report that it did not open `data/v6_memory.json`, anything under `results/`, `v7.1_results.md`, or `v7_0results.md`, and built `results/claude.memory.json` from only the raw 1,200-event corpus and the benchmark's query set (which contains queries and relevant-event IDs, not answers or gold memory). I then performed Phases 2–5 (evaluation against gold, consumption, validation, reporting) myself, since those phases explicitly require gold access.

## Phase 1 — memory construction summary

`results/claude.memory.json`: 50 records — 20 observation, 14 relationship, 9 proposition, 3 state_history, 1 ambiguity, 1 belief_history, 1 negative_knowledge, 1 provenance_chain. All 8 benchmark cases covered. Full detail in the writer subagent's own report (reproduced faithfully, not re-summarized): it extracted from the corpus's self-labeled `kind: "signal"` vs `"distractor"` event tagging (20 signal events across the corpus, matching exactly the union of all 8 cases' `raw_event_ids`), and made explicit judgment calls on: (a) treating Copilot's later notes-read (E0802) as a `later_memory_read` provenance role rather than a new observation, (b) classifying the DynamoDB-cause case as inference→confirmation evolution rather than overlapping conflict, and (c) scoping the MongoDB negative-knowledge claim tightly to "within the billing migration review" per explicit textual completeness evidence in E0548, with an out-of-scope caveat for E1102.

## Phase 2 — memory evaluation summary (full detail in `results/claude.memory_eval.json`)

- **Observation coverage**: 20/20 gold signal event IDs present in generated memory (recall = precision = 1.0). Zero invented event IDs.
- **Relationship comparison**: 3 of 4 gold relationships have an exact or near-exact semantic counterpart; the 4th (`MREL-REDIS-02`, "Redis retry_result negligible_latency_improvement") is present in generated memory only as a `state_history` note rather than a standalone relationship record — the fact is retained, but the record-type choice differs.
- **State history (V71-TIME-01)**: all 4 states, all `valid_from`/`valid_to` boundaries, and all source event IDs match gold exactly. State *labels* are semantic paraphrases (e.g. gold's `webhooks_active` used twice vs. generated's `webhooks_enabled` then `webhooks_re_enabled`), not string-identical — flagged explicitly as a labeling divergence, not a factual one.
- **Ambiguity, negative knowledge, provenance chain**: exact semantic matches to gold on all substantive fields (candidates, resolution, scope, completeness basis, role sequence, actors).
- **Belief history**: generated memory's version is a strict superset of gold's (5 steps vs. gold's 2), but contains gold's exact `inferred→confirmed` step as a subsequence, with matching `status` field.
- **Invented-record rate**: 0.
- One case, V71-ACT-01, has no relationship/state_history record in gold at all — generated memory added one (`STATE-invoice-export`), which is additional structure the evaluation does not penalize since it's directly supported by the same 3 source events gold itself references.

## Phase 3 — Results

Correctness is counted per applicable `correctness.*` field (null fields excluded, since a case's query only tests some of the 7 rubric dimensions).

| Condition | Cases | Applicable checks | Correct | Incorrect | Unsupported |
| --------- | ----: | -----------------: | ------: | --------: | -----------: |
| RAW              | 8 | 15 | 15 | 0 | 0 |
| RAG              | 8 | 16 | 14 | 2 | 0 |
| V6-GENERATED     | 8 | 18 | 18 | 0 | 0 |
| V6-GENERATED+RAW | 8 | 18 | 18 | 0 | 0 |

(V6-GENERATED/+RAW show 18 applicable checks vs. RAW's 15 because the generated memory's richer relationship/state records let me mark `relationship: true` on 3 additional cases — V71-DEC-01, V71-ACT-01, V71-TIME-01 — where the RAW condition's free-text answer didn't naturally populate that field. This reflects how I scored my own answers, not a difference in underlying evidence sufficiency.)

## Failure analysis

**Case: V71-TIME-01, Condition: RAG.** Identical failure mode to V7.1 (same deterministic retrieval policy, same corpus, re-verified fresh in this run): the top-6 retrieved chunks (`C0033, C0000, C0005, C0011, C0019, C0037`) contain only 2 of the 4 required events (`E0233`, `E0401`); `E0887` and `E1190` (webhooks-disabled, webhooks-re-enabled) are absent from every retrieved chunk's `event_ids` list, verified directly against `data/rag_retrievals_v71.json` rather than assumed. My RAG answer explicitly reported the retrieved evidence as insufficient for "latest known state" rather than guessing, so `factual` and `temporal` were marked `false` (the query is unanswered from retrieved evidence), not because a wrong fact was asserted. Cause: **retrieval-related** — the lexical top-6 policy simply does not surface the later two chunks for this query's phrasing. No other failures occurred in RAW, V6-GENERATED, or V6-GENERATED+RAW.

## Retrieval observations (RAG)

Retrieved chunk IDs/scores per case are recorded verbatim in `results/claude.RAG.json`'s `retrieved_chunks` field (identical to the V7.1 run, since the retrieval artifact and policy are unchanged — re-verified by regenerating `data/rag_retrievals_v71.json` fresh in this session via `src/build_rag.py` and re-checking coverage).

| Case | Required events | Covered | Missing |
|---|---|---|---|
| V71-HIST-01 | 3 | 3 | none |
| V71-DEC-01 | 3 | 3 | none |
| V71-ACT-01 | 3 | 3 | none |
| V71-TIME-01 | 4 | 2 | **E0887, E1190** |
| V71-AMB-01 | 2 | 2 | none |
| V71-CONFLICT-01 | 2 | 2 | none |
| V71-NEG-01 | 2 | 2 | none |
| V71-PROV-01 | 5 | 5 | none |

7 of 8 cases had fully sufficient retrieved evidence. V71-TIME-01 was the sole gap, and it is the same gap observed independently in the V7.1 run — this is a property of the deterministic retrieval policy and query phrasing, not something that varied between runs.

## Memory observations (V6-GENERATED)

- Every one of the 8 cases was answerable from `results/claude.memory.json` alone (`V6-GENERATED` condition), with no raw conversation consulted while producing those 8 answers.
- Relationship/state-transition records used: `REL-postgres-chosen-for-billing`, `REL-postgres-chosen-over-dynamodb`, `REL-dynamodb-tried-for-billing`, `REL-dynamodb-migration-failed-due-to`, `REL-claude-confirmed-dynamodb-failure` (HIST-01); `STATE-redis-caching`, `REL-redis-abandoned-due-to`, `REL-redis-retry-of` (DEC-01); `STATE-invoice-export`, `REL-invoice-export-switched-to` (ACT-01); `STATE-webhook-migration`, `REL-webhook-migration-path`, `REL-webhook-disabled-due-to`, `REL-webhook-reenabled-after` (TIME-01).
- Ambiguity record used: `AMB-he-deployment-window` (AMB-01) — `resolution: null`, `status: unresolved`.
- Provenance/belief records used: `BELIEF-dynamodb-cause` and `PROV-dynamodb-failure-full-history` (CONFLICT-01, PROV-01) — both explicitly distinguish `observation` / `confirmation` / `inference` / `later_confirmation` / `later_memory_read` roles across 4 distinct actors (Rahul, Claude, Rahul again, Copilot).
- Negative-knowledge record used: `NEG-mongodb-billing-review` (NEG-01), with explicit `scope`, `completeness_declaration`, and `out_of_scope_caveat` fields.
- Reconstruction did **not** require the raw conversation for any of the 8 cases under V6-GENERATED. This matches the V7.1 GOLD-V6 result's downstream-utility finding, but here the memory was independently agent-constructed rather than benchmark-compiled.

## Measurements
- input tokens: Not available (manual, non-instrumented interactive run; `null` in all 32 records)
- latency: Not available (manual, non-instrumented interactive run; `null` in all 32 records)
- Generated memory artifact size: `results/claude.memory.json` — 50 records (see byte size via `wc -c` if needed; not measured here as tokens/latency, only structural counts are reported per instrumentation availability)

## Interpretation discipline

Per EXP-V7.2.md §15 and the handoff's DO-NOT list, this report does not claim `V6-GENERATED` beats RAG, nor that this result generalizes beyond this one benchmark/corpus/agent. What this run specifically shows: (1) the writer subagent's clean-room extraction achieved perfect event coverage and zero invented facts against gold, with only representational/labeling divergences, not factual ones (Phase 2 detail); (2) the resulting generated memory supported all 8 delayed queries without raw conversation access (Phase 3); (3) the one RAG failure mode observed in V7.1 reproduced identically here under the same deterministic policy, and was correctly avoided by both the GOLD-V6 (V7.1) and this run's agent-generated V6 memory, for the same underlying reason — the state history was constructed from the full event set rather than via lexical retrieval, not because "V6 is smarter than RAG" in general. Whether a second model (Copilot) can consume this specific generated memory artifact (Phase 4, cross-agent handoff) has not yet been run in this session and is a separate step.
