# EXP-V7.5 — Claude Code report

agent: `claude`

## 1. Memory construction

Delegated Phase 1 to a fresh clean-room subagent (this session had prior exposure to gold data and prior V7.x reports; per RUN_PROMPT.md, direct execution would have invalidated the anti-cheating rule). The subagent was restricted to exactly 8 files: `README.md`, `EXP-V7.5.md`, `protocol/writer_protocol.md`, `schemas/memory_v75.schema.json`, and the 4 `*_unlabeled.jsonl` corpora. It confirmed reading only those 8 files and no forbidden content.

Artifact: `results/claude.memory.json` — 85 records across 4 domains (engineering 22, planning 23, operations 21, product 19), citing 120 distinct source events (30 per domain). `frozen_sha256` was computed by the writer as SHA-256 over `json.dumps({agent, version, records, source_event_ids}, sort_keys=True)`; I independently recomputed this hash after the fact and it matched exactly (`cfbbdf35aa9142d56dfe88fffb3ee4b8791dc2a850a390f7acf7e5be171eb5bb`). Schema-valid against `schemas/memory_v75.schema.json`.

## 2. Selection quality

Full detail in `results/claude.memory_eval.json`.

| Domain | Gold | Retained | Missed | False-retained | Recall | Precision | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| engineering | 30 | 30 | 0 | 0 | 1.0 | 1.0 | 1.0 |
| planning | 30 | 30 | 0 | 0 | 1.0 | 1.0 | 1.0 |
| product | 30 | 30 | 0 | 0 | 1.0 | 1.0 | 1.0 |
| operations | 30 | 30 | 0 | 0 | 1.0 | 1.0 | 1.0 |
| **overall** | **120** | **120** | **0** | **0** | **1.0** | **1.0** | **1.0** |

Retention ratio 6% (120/2,000), compression 94%.

This is the fourth consecutive perfect-selection result for this agent across V7.2-V7.5, but on a materially different and arguably harder basis: 4 independent domains, no query knowledge at write time, and (verified in post-freeze evaluation) durable/distractor separation governed by 6 vs. 7 template families sharing overlapping topic vocabulary rather than any single lexical marker. The writer's own report describes explicitly checking corpus structure across all 2,000 events before finalizing selections. A perfect score across four domains built from the same generator family is meaningful evidence of consistency, but should not be read as proof this generalizes to non-templated, real-world noisy conversation.

## 3. Representation quality

85 records: 31 state_transition, 26 action_outcome, 14 decision, 10 belief_state, 2 negative_knowledge, 1 ambiguity, 1 provenance_note. Invented-event rate: 0 (spot-checked 15 records across all 4 domains against source text).

**Strongest finding of this round**: the writer discovered and explicitly preserved genuine non-monotonic/conflicting durable state within single topics — e.g. `PLA-MEM-025` (team ownership: one outcome-confirmed event followed by three separate "remains unresolved" events for the same topic) and `PRO-MEM-084` (export API: 8 source events forming a non-monotonic history of 4 failed attempts, 2 obsolescence markers, and 2 tentative-to-confirmed transitions with no order resolvable from timestamps alone). At least 9 such conflicting-topic cases were found across the 4 domains and recorded as `belief_state`/`ambiguity` rather than silently resolved to a single "current" fact — a materially richer form of ambiguity/conflict preservation than V7.1-V7.4, which typically involved one explicit unresolved-pronoun statement per experiment.

**One disclosed self-consistency gap**: record `OPE-MEM-085` (`provenance_note`, a meta-observation about the corpus's own template structure) has an empty `source_event_ids` array, diverging from the general principle that every record cites real source events. The writer's own report flagged this transparently as a corpus-structure observation rather than a conversational fact.

## 4. Retrieval quality (RAG condition)

**Severe degradation, the worst RAG result across the V7.1-V7.5 series.** Of 40 queries, only 12 (30%) had their gold-relevant event present anywhere in the deterministic retriever's top-k chunks (verified directly against `data/rag_retrievals_v75.json`'s per-query `event_ids` lists — not assumed).

Breakdown by query kind:

| Kind | Correct | Total |
|---|---:|---:|
| direct | 2 | 8 |
| paraphrase | 0 | 4 |
| indirect | 2 | 4 |
| temporal | 2 | 4 |
| causal | 1 | 4 |
| multi_hop | 0 | 4 |
| negative | 1 | 4 |
| ambiguity | 2 | 4 |
| compositional | 2 | 4 |

Paraphrase and multi-hop queries failed completely (0/4 each) — the two query kinds furthest from the corpus's exact wording, consistent with a pure lexical-overlap retriever's known weakness. This is a genuine, verified effect of dense per-domain distractor volume (470 near-identical-template distractors per domain sharing the same topic vocabulary as the 30 durable events), not a retriever implementation bug (spot-checked, e.g. the query "What was ultimately decided about PostgreSQL migration?" shares almost no exploitable lexical signal against "Change: PostgreSQL migration was replaced by a newer approach" once diluted across hundreds of same-topic distractor mentions).

Every RAG miss was reported as an explicit evidence gap, never guessed or backfilled from the full corpus.

## 5. Reader quality (V6-GENERATED / V6-GENERATED+RAW)

Both conditions: 40/40 correct, 0 unsupported claims. Every one of the 40 future queries — including paraphrase, indirect, causal, multi-hop, negative-knowledge, ambiguity, and compositional kinds the writer never saw — was answerable from the frozen memory alone, because the 120/120 selection recall guaranteed every query's gold event had a covering record. V6-GENERATED+RAW additionally cross-checked each answer against the linked raw event text with no discrepancies found, and in the RAG-failed cases confirmed those gaps were retrieval-policy artifacts, not memory-content gaps.

## 6. Cross-agent quality

- **Claude → Copilot**: executed by Copilot's own session (`results/claude_to_copilot.json`, pre-existing when I reached this phase) against my genuinely frozen `claude.memory.json`. Result: 40/40 correct.
- **Copilot → Claude**: executed by this session. Read only `results/copilot.memory.json` (120 records, one per source event, types: action_outcome 25, belief_confirmation 25, decision 20, unresolved_plan 20, obsolete_state 17, confirmed_outcome 13) plus the 40 future queries and schema — no original corpus, no gold, no Copilot report. Result: **40/40 correct**.
- **Genuine defect found and disclosed, not silently patched or ignored**: Copilot's `frozen_sha256` field does not verify. I independently recomputed SHA-256 over `{agent, version, records, source_event_ids}` using `json.dumps(obj, sort_keys=True)` — the identical method my own writer subagent used and I independently confirmed — and it did not match under that canonicalization nor three others tried (compact separators, `indent=2`, default `json.dumps` with no `sort_keys`). This means Copilot's memory artifact's self-reported hash cannot currently be used to prove the file wasn't altered after its stated freeze point. I proceeded to read and use the memory content anyway (the freeze rule's purpose is preventing post-freeze editing to improve query performance, not gating reader access on hash reproducibility, and the record content itself is internally consistent and schema-valid), but this is recorded in `results/copilot_to_claude.json`'s `writer_memory_hash_verification_note` field for the consolidated report to address.

## 7. Efficiency

- Memory bytes: `claude.memory.json` is a compact 85-record artifact over 2,000 source events (94% compression by event count).
- Input tokens / retrieval latency / answer latency / memory-build time: **not measured** — this is a manual, non-instrumented interactive session. All such fields are omitted or `null` rather than fabricated, per instruction.
- No cost or latency claims are made anywhere in this report.

## Tooling/specification defects disclosed this round

1. Copilot's `frozen_sha256` does not reproduce under standard canonical-JSON hashing (see section 6) — a genuine integrity-verification gap in Copilot's freeze process, not something I could or should silently correct.
2. `schemas/consumption_v75.schema.json` requires only `agent/condition/query_id/correct` plus optional `unsupported_claim` — no `evidence_used`/`answer` fields are schema-mandated this round (unlike V7.1-V7.4's schemas). I included them anyway in all 160 of my own records for auditability, since the protocol's general spirit (and prior rounds' explicit requirement) favors traceable answers even where this round's schema doesn't strictly enforce it.
3. No other tooling defects found this round — `src/generate_v75_corpus.py`, `src/generate_future_queries.py`, and `src/validate_v75.py` all worked correctly for this workspace (unlike V7.4's stale `build_rag.py`/`validate_v71.py`, which were leftovers from an earlier round).

## Limitations

- RAG's severe failure this round is specific to the fixed deterministic lexical retriever used throughout this experiment series under this specific dense-distractor corpus design; per EXP-V7.5.md's own scientific rule, this is not a general claim about retrieval-augmented generation.
- This remains a synthetic, template-generated corpus across all 4 domains; strong within-experiment generalization (4 domains, no query leakage) is not the same claim as generalization to arbitrary real-world conversation.
- The Copilot→Claude cross-agent read used memory content whose self-reported integrity hash could not be verified (see section 6) — the content was still used and scored, but this caveat should travel with the 40/40 result in any consolidated cross-round comparison.
