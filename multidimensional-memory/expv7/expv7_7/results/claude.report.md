# EXP-V7.7 — Claude report

agent: `claude`

## 0. Headline finding: the benchmark's gold answer key is broken

Before any retrieval/consumption result can be interpreted, this needs to be stated plainly: **`data/benchmark_v7_7_gold.json` contains two mutually inconsistent gold-label sets, and the per-query one used for scoring every condition is broken.**

- `gold_durable_event_ids` (216 events, used to score memory *selection*) correctly identifies durable content — e.g. `C01E003`, "Team discussed whether PostgreSQL should remain the primary technology for billing," is flagged durable, correctly.
- `queries[].required_event_ids` (union of 156 events across 96 queries, used to score every *consumption/retrieval* condition) is **completely disjoint from `gold_durable_event_ids` — zero overlap** — and every single one of the 96 queries' required events, across all 8 categories, points to **generic routine filler text** (verified by direct inspection, not sampling): e.g. Q01-01 ("What was the original technology preference for billing, and what ultimately replaced it?") requires `C01E013`/`C01E031`/`C01E079`, whose actual text is "Routine progress was discussed for billing; no final decision was made" and "A status update mentioned the billing service and ordinary maintenance tasks" — none of which mention a technology, a preference, or a replacement. This pattern repeats identically for all 12 conversations and all 8 query categories.

**Consequence**: every retrieval and memory-consumption condition scores at or near zero below, not because any retrieval system or the memory representation failed to find/preserve the right information, but because the answer key itself does not point at information that could answer its own questions. This was verified directly against corpus text, not inferred from low scores alone. Per EXP-V7.7.md's failure rule ("never replace it silently with a weaker proxy") and this session's explicit instruction to disclose rather than paper over defects, all condition scores below are reported exactly as computed against the gold file as supplied, with this defect as the headline context for interpreting every number that follows.

## 1. Memory construction

Writer: clean-room subagent, restricted to 6 files (`RUN_PROMPT.md`, `README.md`, `EXP-V7.7.md`, `schemas/memory_v77.schema.json`, `data/benchmark_v7_7_public.json`, `data/conversation_v7_7_unlabeled.jsonl`). Confirmed no access to gold files, evaluator corpus, `results/`, or other agents' output (Copilot and Codex writer artifacts already existed in `results/` at the time; the writer confirmed it only `ls`'d the directory, did not read contents).

The writer-visible corpus has no `event_id` field by design (only `conversation_id`/`timestamp`/`speaker`/`text`); the writer correctly self-constructed stable `"CONV-XX@timestamp"` keys, later losslessly mapped to canonical event_ids via `data/conversation_v7_7_evaluator.jsonl` for evaluation (216/216 keys mapped, 0 unmapped).

Artifact: `results/claude.memory.json` — 169 records: action_outcome 48, ambiguity 36, decision 24, state_transition 24, belief_conflict 12, provenance 12, negative_knowledge 12, observation 1. Schema-valid.

## 2. Selection quality (against `gold_durable_event_ids`, the correctly-behaving gold set)

| | Gold | Retained | Missed | False-retained | Recall | Precision | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Overall (12 conversations)** | 216 | 216 | 12 | 12 | 0.9444 | 0.9444 | 0.9444 |

First non-perfect selection score in this agent's V7.1-V7.7 series. The error is **one precisely systematic off-by-position mistake, replicated identically across all 12 conversations**: the writer cited event index 0 (`C0XE001`, routine filler — "Routine progress was discussed... no final decision was made") in every conversation instead of index 2 (`C0XE003`, the genuine tentative-preference statement), a consistent off-by-two slip in an otherwise correctly-instantiated 12x-repeated template, not 12 independent misjudgments. Full detail, including the exact missed/extra event lists, in `results/claude.memory_eval.json`.

## 3. Representation quality

Reversal/supersession arcs, belief conflicts, ambiguity (including correctly distinguishing "genuinely unresolved" from "resolved later"), negative-knowledge statements with scope, and provenance role-splitting were all captured consistently across all 12 conversations, matching the qualitative bar of V7.6's equivalent findings. Invented-event rate: 0. Full detail in `results/claude.memory_eval.json`.

## 4. Retrieval and consumption quality (against `required_event_ids`, the broken gold set)

| Condition | Correct/96 | Avg. evidence coverage | Implementation |
|---|---:|---:|---|
| RAW | 96 | 1.000 | Full raw conversation always available (trivially correct — required events, however defined, are always inside the full transcript) |
| BM25 | 0 | 0.062 | `rank_bm25.BM25Okapi`, real lexical algorithm, top-12 |
| DENSE | 1 | 0.095 | `sentence-transformers` `all-MiniLM-L6-v2`, real neural embeddings + cosine similarity, top-12 |
| HYBRID | 1 | 0.095 | 50/50 normalized blend of BM25 + DENSE scores, reranked |
| GRAPHRAG | 0 | 0.000 | **CUSTOM/DISCLOSED** — no official `graphrag` package available in this environment (`pip show` confirms not installed, no network install attempted); heuristic capitalized-entity co-occurrence graph + shortest-path traversal within the query's conversation |
| HIPPORAG2 | 0 | 0.000 | **CUSTOM/DISCLOSED** — no official `hipporag` package available; same heuristic entity graph, ranked via `networkx` personalized PageRank seeded on query-matched entities, approximating HippoRAG 2's associative-memory mechanism without its real OpenIE/LLM entity extraction |
| RAPTOR | 0 | 0.062 | **CUSTOM/DISCLOSED** — no official `raptor` package available; 2-level structural approximation (10-event contiguous "summary" windows via plain concatenation, no LLM summarization call available offline, + leaf-level BM25), not RAPTOR's real recursive clustering/LLM-summarization tree |
| MEMORY | 0 | 0.000 | `results/claude.memory.json` records only, no raw conversation |
| MEMORY+RAW | 0 | 0.000 | Memory records + their own linked raw evidence |

**Every condition scores near-zero, including MEMORY.** Given §0's finding, this is not evidence that structured memory failed to help, nor that any retrieval baseline is weak — it is a direct consequence of the required-evidence gold set not pointing at answerable content for any of the 96 queries under any evidence source, including the full raw conversation's own topically-relevant sentences elsewhere in the same conversation. (RAW scores 96/96 only because "the full transcript contains these three specific — if generically-worded — events" is trivially true regardless of whether those events answer the question.)

**Disclosed implementation weakness, independent of the gold-data defect**: only 388/1200 corpus events (32%) and only 24/96 queries (25%) contain any capitalized entity my heuristic extractor could anchor on, which alone would have suppressed GRAPHRAG/HIPPORAG2 scores even with a correct gold set — a real limitation of this custom lightweight entity extractor (not full NER/OpenIE), disclosed rather than hidden behind the gold-data defect as an excuse.

## 5. Cross-agent quality

Not executed this round. Both Copilot and Codex writer artifacts (`copilot.memory.json`, `codex.memory.json`) already existed when this session reached this phase, but neither had yet produced Phase B condition files at the time of this run, and this session did not perform the Phase C cross-agent handoffs (Claude→Copilot, Copilot→Claude, Claude→Codex, Codex→Claude, Copilot→Codex, Codex→Copilot) — those require a further phase this report does not claim to have completed, and doing so meaningfully is moot until the gold-data defect in §0 is fixed, since a reader's correctness would be scored against the same broken `required_event_ids`.

## 6. Efficiency

Not instrumented — manual, non-API session; all `input_tokens`/`retrieved_tokens`/`memory_tokens`/latency/cost fields are `null` throughout, never estimated.

## Tooling notes from this session

- This session's own scripting caused two accidental destructions of the frozen memory artifact in the *previous* round (V7.6), both from writing `results/claude.MEMORY.json` on this Mac's case-insensitive filesystem, which silently collides with `results/claude.memory.json`. To prevent a third occurrence, this round's MEMORY condition file is deliberately saved as `results/claude.MEMORY_condition.json` instead of the exact spec'd `results/claude.MEMORY.json` — a disclosed deviation from EXP-V7.7's exact filename list (`AGENT_HANDOFF.md` Phase B), prioritizing artifact integrity over strict naming compliance. `results/claude.memory.json` was additionally backed up immediately after freeze as `results/claude.memory.FROZEN_BACKUP.json`.
- All three GRAPHRAG/HIPPORAG2/RAPTOR condition files carry an explicit `provenance` field per-record disclosing they are custom approximations, not the official packages, per `adapters/README.md`'s explicit instruction not to substitute silently.

## Limitations

- The single most important limitation this round is external to this agent's own work: the benchmark's gold answer key (`required_event_ids`) does not point at answerable evidence for any of its 96 queries, making every non-trivial consumption/retrieval condition score near-zero regardless of the underlying system's actual quality. This should be fixed before any comparative conclusion is drawn from this round's Phase B numbers.
- The writer's one systematic selection slip (94.4% vs. prior rounds' 100%) is real but small and precisely characterized, not a broad quality regression.
- Custom GRAPHRAG/HIPPORAG2/RAPTOR implementations are documented approximations, not the official systems, and carry their own independent (entity-extraction-driven) weakness on top of the gold-data defect.
- No cross-agent handoff was executed this round.
