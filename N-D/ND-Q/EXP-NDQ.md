# ND-Q: does an LLM-planned logical query beat keyword selection on the memory we already have?

**Status:** DRAFT 2026-10-06. Not frozen. It freezes on approval, before any ND-Q run; after that, any change is a new version and the first version is still reported.

## Why

ND-3 tied retrieval (DEPICT 28.5, BM25 28.5, RAW 32.5). The cause found in the miss analysis: depiction selects by question words, which is BM25 under another name, and the stored values are free text, so only words can be matched. A deterministic NLP query parser (spaCy, WordNet, dateparser) did no better on evidence recall (0.75 vs BM25 0.76); it won multi-hop and lost false-premise and everyday categories.

ND-Q tests a different split of work: **the answering LLM plans the query, a small set of deterministic tools executes it over the engine's memory, and nothing is ranked.** The LLM does the language understanding; the engine does exact, auditable operations on entities, dates, speakers and statuses.

This tests the query mechanism on the memory as it is today (engine v0.3, Haiku extraction run 1). It does not test a new storage format; that is a separate question (see "Not tested here").

## Data

- **LoCoMo conv-49**, 509 turns, same frozen extraction and engine state as ND-3. No re-extraction.
- **Primary set:** the same 40 ND-3 questions, so the ND-3 hand scores can be reused as baselines (RAW 32.5, RAG 28.5, DEPICT 28.5, unchanged and not re-run).
- **Confirmation set (only if the primary passes):** 40 fresh conv-49 questions not used in any analysis so far, seed 11, stratified as in ND-3 where each category has enough left, excluding the primary 40.
- **Pilot (unscored, harness debugging only):** 3 questions from conv-30. conv-49 is not used for debugging.

## Arms (answering model Sonnet, one isolated session per question)

| Arm | What the model can do | Source |
|---|---|---|
| RAW | Reads all 509 turns | ND-3 result, reused |
| RAG | Reads BM25 top turns, ≤ 1,000 words, one shot | ND-3 result, reused |
| DEPICT | Reads depiction v2, ≤ 1,000 words, one shot | ND-3 result, reused |
| **TOOLS** | Calls the logical tools below, up to 10 calls, then answers | New |
| **RAGTOOL** | Same loop and call limit, one tool: `search_turns(query)` = BM25 over raw turns, top 5 dated turns per call | New |

RAGTOOL is the control that matters. An iterative agent can beat one-shot retrieval without any structure, so TOOLS must beat RAGTOOL for the credit to belong to the structure.

## The tools (frozen interface; read-only, deterministic, no LLM)

Every result is capped at 200 words with a "N more" count. Tools return **memory strings** (entity, dimension, value, status, owner, date, speaker), never source turns.

| Tool | Returns |
|---|---|
| `find_entity(name)` | Pegs matching by normalised name (exact, then near matches, near matches proposed and never merged): type, event count, first and last date |
| `trajectory(entity, from?, to?)` | That peg's events in order: tick, date, speaker, its dimension values, status, owner |
| `event(tick)` | One event in full: speaker, listener, date, every entity with its dimension values and statuses |
| `co_occurring(entity_a, entity_b?)` | Events where the pegs appear together (collisions), hub pegs excluded unless named |
| `filter_events(dimension?, status?, owner?, speaker?, from?, to?)` | Matching events: count plus the first 10 |
| `count(entity?, dimension?, status?, owner?, from?, to?)` | Exact number of matching events and of distinct pegs, with their ids |
| `ambiguities(entity?)` | Open buckets with their candidates; no resolution is applied |

The prompt gives the model the dimension dictionary, the date range of the memory, and these rules: answer only from tool results; if the tools return nothing relevant, say it is not in memory; do not accept a premise the memory does not support. The final-answer instructions are the ND-3 text, unchanged.

## Measures

1. **Accuracy:** hand scores, C = 1, P = 0.5, W = 0, against LoCoMo gold, with arm labels hidden when scoring.
2. **Evidence recall of the trace:** share of gold evidence turns whose events appeared in any tool result (no LLM), with the total words returned, for comparison with BM25 0.76 and depiction 0.69.
3. **Cost:** tool calls and words read per question, wall-clock, harness failures.
4. **Extraction ceiling:** questions whose gold evidence never reached memory (q17, q25, q30 from the ND-3 attribution) are reported separately, since no arm can recover them. Scores are given with and without them.

## Hypotheses and verdict

| ID | Hypothesis | Criterion |
|---|---|---|
| Q1 | Logical tools beat one-shot retrieval | TOOLS ≥ RAG + 3.0 points (≥ 31.5 of 40) |
| Q2 | The gain comes from structure, not just from an agent loop | TOOLS ≥ RAGTOOL + 2.0 points |
| Q3 | Close to reading everything | TOOLS ≥ 90% of RAW (≥ 29.25) |
| Q4 | Reported, no threshold | cat 5 false-premise, cat 2 temporal, cat 1 multi-hop counts, abstention behaviour |
| Q5 | Cost is bounded | median ≤ 10 calls and ≤ 1,500 words read; reported either way |

**ND-Q passes if Q1 and Q3 hold, and on the confirmation set the same two hold.** Q2 decides how the pass is worded: if Q2 fails, the win is the agent loop, not NDM's structure, and the report says so.

**If TOOLS ≤ RAG:** logical tools over the current memory do not help, because the stored values are text. The next suspect is the storage format (entity-to-entity relations, one-word dimension values), tested on paper before any code (see below).

## Interpretation limits, stated now

- 40 questions, one conversation, one extraction run, Claude only. A difference of 1–2 questions is noise.
- The primary 40 were read during the ND-3 miss analysis and during the NLP-query prototype. The tool interface here comes from the memory's structure, not from those answers, but the primary set is not held out. That is why the confirmation set is required.
- The answering model is also the query planner, and temperature is not settable on the CLI: each question runs once, so run-to-run variance is not measured.
- A tool result that is empty, or that returns a wrong peg, is scored as the arm's failure, even when the cause is an extraction gap. The ceiling split (measure 4) separates these.

## Implementation intent (not results)

`engine/ndm_tools.py` holds the pure functions; `engine/ndm_mcp.py` wraps them as an MCP stdio server; the runner uses `claude -p` with `--strict-mcp-config`, built-in tools disabled, an empty temp directory and `--max-turns 12`. Every tool call and result is saved per question for audit. Each tool gets a contract test on the frozen state (for example `count` matches a manual count on five known cases) before the first scored run.

## Not tested here

- A new storage format (entities pointing at entities, a one-word `Is`, relations stored once). Its paper test (the 14 ND-3 misses plus 10 correct answers, written in that format and as queries, no LLM usage) is a separate step and can run in parallel.
- LLM-decided writes. Ingestion stays automatic; only reads are planned by the model.
- Other model families, other conversations, Mem0 or Zep.

## Stop rules

On a usage limit, stop, commit what is done and resume one arm at a time. Tool descriptions and the prompt are not edited after the first scored answer. Failures are reported in `REPORT.md` against these criteria.
