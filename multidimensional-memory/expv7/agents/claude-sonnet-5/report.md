# EXP-V7 — Claude Code (Sonnet 5) report

agent_id: `claude-sonnet-5`

## Number of cases
7 benchmark cases, run across all 4 conditions (RAW, RAG, V6, V6+RAW) = 28 records total, all validated against `schemas/agent_result.schema.json` (`python -m src.validate_results` — 0 errors for this agent's 4 files).

## Category-level correctness
(Self-assessed by this agent against the benchmark's `expected_facts`; not an external rubric score.)

| Category | RAW | RAG | V6 | V6+RAW |
|---|---|---|---|---|
| historical_recall | correct | correct | correct | correct |
| action_outcome | correct | correct | correct | correct |
| temporal_state | correct | **incorrect** (see below) | correct | correct |
| ambiguity | correct (unresolved reported) | correct (unresolved reported) | correct (unresolved reported) | correct (unresolved reported) |
| contradiction | correct (disputed preserved) | correct (disputed preserved) | correct (disputed preserved) | correct (disputed preserved) |
| negative_knowledge | correct | correct | correct | correct |
| provenance | correct | correct | correct | correct |

## Unsupported claims
0 across all 28 records. No answer asserted a fact absent from the evidence supplied under that condition.

## Context/evidence size
- RAW: full conversation per case (2–4 sentences each).
- RAG: fixed keyword-overlap retrieval policy (see `agents/claude-sonnet-5/conditions/RAG_policy.md`), sentence-level chunks. For 2 of 7 cases (V7-HIST-01, V7-ACT-01) no chunk scored above zero against the query, so the policy fell back to returning all chunks. For V7-TIME-01, only 1 of 3 chunks was retrieved.
- V6: structured memory only (propositions/observations/ambiguity/conflict/negative-knowledge records), no raw text.
- V6+RAW: V6 memory plus full raw conversation for verification.
- Exact token counts are unavailable in this manual run and are reported as `null` per the handoff's instruction not to fabricate measurements.

## Latency
Not measurable in this manual/interactive run; reported as `null` throughout, per instruction.

## Notable failure modes

**RAG under-retrieval on V7-TIME-01 (temporal_state).** The fixed keyword-overlap retrieval policy retrieved only the January/polling sentence for the query "What is the latest known service state, and how did it evolve?" — the query's keywords ("latest," "state," "evolve") don't lexically overlap with the March/May sentences, which are phrased around "changed to webhooks" and "disabled webhooks temporarily." This caused RAG to produce a factually incomplete and temporally wrong answer (reporting January/polling as if final), while V6 — which stores an explicit ordered/superseding sequence rather than relying on lexical similarity — preserved the full state history and produced the correct answer. This is the single clearest condition-level divergence in this run and is directly relevant to V7's core question: it demonstrates a concrete mechanism (retrieval-policy blindness to paraphrase/reference, not just "RAG is worse in general") by which V6-style structured memory outperformed similarity retrieval on a downstream task.

**No V6 failure modes observed in this run.** V6 answers matched RAW/V6+RAW answers in substance for all 7 cases. This run cannot rule out V6 failure on harder or longer-horizon cases than this benchmark contains; the benchmark's conversations are short (2–4 sentences), which limits how hard the RAG condition's retrieval problem actually is and how much stress is placed on V6's merge/provenance logic.

**No V6 memory file pre-existed in the repository at run time.** This agent had to construct the V6-format memory itself from the raw conversations, guided by the EXP-V6/V6.1/V6.2 design docs, rather than consuming a memory artifact written independently by a "writer" agent. This run is therefore a same-agent (single-agent) pass per Step 5, not yet the cross-agent pass described in Step 6 — a true cross-agent test requires a separate writer agent's V6 output as input, which was not available.

## What this run does and does not show
This run shows that, for this benchmark's 7 short cases, V6-style structured memory reproduced RAW-condition correctness while supplying substantially less/no raw text, and it avoided a retrieval-completeness failure that a simple fixed-policy RAG condition exhibited on the temporal_state case. It does not show cross-agent robustness (no independent writer agent's memory was consumed), does not show performance on longer or noisier conversations, and does not constitute a ranking of agents.
