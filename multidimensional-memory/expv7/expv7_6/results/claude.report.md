# EXP-V7.6 — Claude Code report

agent: `claude`

## 0. Incident disclosure (read first — affects how to weigh everything below)

This run suffered **two accidental data-loss incidents**, both caused by the same bug in my own tooling, not by any writer defect:

- A script I wrote saved consumption-condition results to `results/claude.MEMORY.json`. On this session's macOS filesystem (case-insensitive), that path is **the same file** as `results/claude.memory.json` — the frozen writer artifact. Writing the condition file silently overwrote and destroyed the frozen memory artifact. This happened **twice**, the second time despite me explicitly knowing about the bug from the first occurrence, because I repeated the exact same filename pattern.
- Each time, the destroyed artifact had already been independently verified (schema-valid, SHA-256-matched, perfect 216/216 selection) before being destroyed. Neither loss was recoverable from any other file (the `memory_eval.json` summaries do not contain full record content).
- After the second incident I stopped and asked the user how to proceed rather than attempting a third silent fix. The user asked me to re-run the writer once more and disclose both incidents prominently, which this section does.
- **The current `results/claude.memory.json` is the third independent writer run.** It is backed up at `results/claude.memory.FROZEN_BACKUP.json` as insurance. To avoid a third collision, the MEMORY consumption-condition file for this run is saved as `results/claude.MEMORY_condition.json` rather than `results/claude.MEMORY.json`, a deliberate deviation from EXP-V7.6.md §15's exact filename list, made to protect data integrity over strict naming compliance. This is flagged as a tooling defect this session introduced and does not reflect anything in the provided EXP-V7.6 workspace.
- **Cross-run consistency, as a partial silver lining**: all three independent clean-room writer runs (destroyed run 1, destroyed run 2, and this surviving run 3) each independently cited **exactly 216 distinct source events** — matching `data/DATASET_CARD.md`'s stated `durable_annotated_events: 216` in all three cases, with no writer ever having access to gold data. This is meaningful evidence the selection result is stable across independent runs, not a fluke of one particular execution, even though only the third run's actual record content survives for detailed evaluation.

## 1. Memory construction

Writer: clean-room subagent (3rd run), restricted to exactly 5 files (`README.md`, `EXP-V7.6.md`, `schemas/memory_v76.schema.json`, `data/DATASET_CARD.md`, `data/conversation_v7_6.jsonl`). Confirmed no access to `evaluation/`, `results/`, or any prior-round content.

Artifact: `results/claude.memory.json` — 240 records: action_outcome 60, state_transition 36, ambiguity 24, decision 24, negative_knowledge 24, provenance_note 24, observation 12, proposition 12, relationship 12, belief_state 12. `memory_hash` (SHA-256 over `json.dumps(records, sort_keys=True)`): `80dc642af2b1e02c7f5b4db60d780171c04a4ba03785b5a24bc0f9d484a64bd1`, independently recomputed and confirmed matching. Schema-valid against `schemas/memory_v76.schema.json`.

## 2. Selection quality

Full detail in `results/claude.memory_eval.json`.

| | Gold | Retained | Missed | False-retained | Recall | Precision | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Overall (12 conversations)** | 216 | 216 | 0 | 0 | 1.0 | 1.0 | 1.0 |

All 12 conversations (atlas, mercury, northstar, orion, harbor, cinder, lumen, quartz, maple, vertex, echo, apollo) independently scored 18/18. Retention ratio 38.3% (216/564) — much higher than V7.1-V7.5's typical 1.7-6%, because this corpus's per-conversation signal density is higher (18 durable / ~47 total events ≈ 38%), not because selection was less strict.

**Corpus realism caveat, disclosed rather than glossed over**: all three independent writer runs, unprompted, flagged that the 12 conversations share one fixed narrative template and near-identical event/session counts, differing only in substituted technology/project nouns. This was independently verified in evaluation (`evaluation/gold_events.json`'s `key` field follows an identical dot-path pattern across all 12 conversations). The corpus is a real improvement over V7.1-V7.5's raw sentence-template generation (natural, varied prose; no repeated boilerplate substring), but it is a **parameterized template repeated 12 times**, not 12 independently-varied realistic conversations. Perfect selection here demonstrates robust, repeatable execution of one hard extraction pattern, not demonstrated generalization across genuinely varied conversational structures — this is the single most important caveat for interpreting this round's results.

## 3. Representation quality

Every conversation's reversal arc (tentative tech-1 lean → explicit supersession by tech-2 after cost review) was captured with the superseded state marked, not deleted, satisfying EXP-V7.6.md's explicit "do not collapse history into only the latest state" requirement. Two ambiguities per conversation (24 total) were recorded as genuinely unresolved at the point raised, then linked to their later within-conversation resolution. 24 negative-knowledge records correctly grounded explicit denials (not retrieval absence) in two flavors per conversation: one time-bound (a cutover-approval status later superseded) and one permanent (an unrelated technology explicitly denied ever being discussed). 24 provenance-note records preserved original-reporter vs. later-confirmer role distinctions. Invented-event rate: 0.

## 4. Retrieval quality (BM25 / SEMANTIC_RAG / HYBRID_RAG)

All three retrieval baselines were built fresh for this workspace (`src/build_retrievers_v76.py`) since none was provided: BM25 via `rank_bm25`, SEMANTIC_RAG via TF-IDF + cosine similarity (scikit-learn) — **disclosed explicitly: this is a lexical-vector proxy, not a neural embedding model**, since this environment has no API/network access for real embeddings. HYBRID_RAG is a 50/50 normalized-score blend of the two.

Because each query's gold requirement is a set of ~12 specific events (not just "any relevant chunk"), correctness was scored strictly: a condition is "correct" only if its evidence set is a superset of the query's full `gold_event_ids`. Under this strict standard, **all three retrieval baselines scored 0/96** — none ever retrieved the complete required evidence set for any query within a top-12 budget. This is reported plainly, per EXP-V7.6.md's explicit instruction: "If a baseline wins a case, record it accurately. If memory fails, preserve the failure" (the symmetric case — here, retrieval failing outright — is preserved with equal honesty).

Because a binary 0/96 score would obscure genuine near-misses, every condition file also records an `evidence_coverage_fraction` (fraction of required events actually retrieved), which is more informative:

| Retriever | Overall avg. coverage | decision | temporal | revision | action_outcome | provenance | ambiguity | multi_hop | negative |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BM25 | 0.438 | 0.722 | 0.583 | 0.576 | 0.438 | 0.403 | 0.417 | 0.292 | 0.076 |
| SEMANTIC (TF-IDF) | 0.467 | 0.722 | 0.569 | 0.576 | 0.500 | 0.472 | 0.465 | 0.319 | 0.111 |
| HYBRID | 0.438 | 0.722 | 0.576 | 0.576 | 0.438 | 0.403 | 0.424 | 0.292 | 0.076 |

**Negative-knowledge queries are the hardest category for all three retrievers by a wide margin (7-11% coverage)** — a query like "was Cassandra ever discussed?" has almost no lexical/semantic overlap with the sparse, brief denial sentence that answers it, and that sentence is easily outranked by dozens of topically-similar but irrelevant chunks. Multi-hop queries are the second-hardest (29-32%). Decision queries fare best (72% for all three, identical because the top few chunks are dominated by the decision language itself, which both BM25 and TF-IDF weight similarly here).

## 5. Reader quality (MEMORY / MEMORY+RAW)

Both: 96/96 correct, 0 unsupported claims, `evidence_coverage_fraction` 1.0 throughout. Every query — across all 8 categories including negative-knowledge and multi-hop, the two hardest for retrieval — was answerable from the frozen memory alone, since 216/216 selection recall guaranteed every query's required events had a covering memory record. MEMORY+RAW additionally cross-checked every answer against its own linked raw evidence with no discrepancies.

## 6. Cross-agent quality

Copilot's own independent run (`results/copilot.*`) was already present in the workspace when this run reached Phase 3/4, having used the same strict binary correctness standard (its BM25 file also scored 0/96, its MEMORY+RAW scored 96/96) — a useful cross-agent consistency check on methodology, though this session did not itself execute a cross-agent reader handoff in either direction this round (no `claude_to_copilot.json`/`copilot_to_claude.json` was produced by this session; that would require a further post-freeze phase this report does not claim to have completed).

## 7. Efficiency

Memory: 240 records over 564 source events (61.7% compression by event count). Token/latency/cost instrumentation: **not measured** — this is a manual, non-instrumented interactive session; all such fields are `null` throughout, per instruction, never estimated.

## Falsification-criteria check (EXP-V7.6.md §12)

1. *"Strong RAG matches or exceeds memory on long-horizon state reconstruction"* — **not observed this round**: all three RAG baselines scored 0/96 under strict full-coverage correctness; memory scored 96/96. This is the opposite of falsifying evidence, but see the corpus-realism caveat below for why this shouldn't be over-read.
2. *"Memory construction loses important information at rates that erase its consumption advantage"* — not observed; 0% invented-event rate, 100% selection recall/precision.
3. *"Gains disappear outside synthetic/template-like conversations"* — **this criterion is the load-bearing caveat for this round.** The corpus, despite being written in natural prose, is structurally a repeated template across all 12 conversations (confirmed independently by three separate writer runs and by direct inspection of gold_events.json's key patterns). This result should be read as evidence the pipeline mechanics work correctly at this realistic-prose-but-templated-structure level, not as evidence the memory hypothesis survives genuinely varied real-world conversation structure, which EXP-V7.6.md's stated goal actually requires.

## Limitations

- Two data-loss incidents this session caused (§0) mean this round's writer artifact is a third, not first, execution; the destroyed runs' exact record content cannot be independently audited, only their aggregate statistics (matching this run's) are known.
- SEMANTIC_RAG is a TF-IDF/cosine proxy, not a real embedding model, due to no API access in this environment — explicitly disclosed, not silently substituted.
- No cross-agent reader handoff was executed by this session this round.
- The corpus's 12-conversation structural regularity is the primary reason to treat this round's strong results cautiously rather than as confirmation of the memory hypothesis under genuinely realistic conditions.
