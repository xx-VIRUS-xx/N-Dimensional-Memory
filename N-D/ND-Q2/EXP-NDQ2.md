# ND-Q2: does an LLM-planned query over the ND-E memory beat searching raw turns?

**Status: FROZEN 2026-10-09, approved by Prabhat Saxena ("Approve", after reading the draft; the items marked [A] are approved as written).** Freeze is staged, as in ND-Q: this file (data, arms, hypotheses, pass rule, tool names and behaviour) is frozen now and listed in `ND-Q2/FREEZE.sha256`. The exact tool descriptions and the prompt text may change during the dev-set pilot and are frozen, with their hashes in an amendment, before the test set is drawn; after the first scored answer nothing is edited. Later changes are numbered amendments and this file stays as it is.

## Why
ND-Q (v1) failed on the old memory: TOOLS 26.5, RAGTOOL 31.0, RAW 32.5 (Q1, Q2, Q3 failed). Its traces named three causes: relative time was stored but never shown or resolved; free-text values did not share words with the question; nine questions had no evidence in any tool result. ND-E changes what is stored: one event per sentence, open relation types with linked entities, a per-event `Entities` list, time cues kept verbatim, no speaker or date in the rows. Phase 2 (amendment 7) passed M1 to M5 and failed M6 and M7 on the spec arm because content nouns often sit inside text values. This experiment tests the query side on that memory as it is: no re-extraction.

## Data
- **Memory:** LoCoMo conv-49, 509 events, run 6 (prompt v4.1, sha256 `ee9427ff...`). Speaker, listener and date come from the source row with the same `event_id`, joined by code at query time; the rows are not changed.
- **Dev set (tool debugging, unscored for the hypotheses):** the 40 ND-3 questions (`probes.jsonl`). They are development data now: their evidence map was used for M6 and M7. **[A]**
- **Test set:** 40 conv-49 questions not in the dev set, drawn with seed 11 and the ND-3 quotas (15 x cat 4, 8 x cat 1, 8 x cat 5, 7 x cat 2, 2 x cat 3) from the 156 left. The draw happens after the freeze; `tools/locomo_chunk.py` gets an `--exclude` option for it. The author does not read the test questions until the blind sheet.
- **Answering model:** Sonnet, one isolated `claude -p` session per question, empty temp dir, built-in tools off, only that arm's MCP server, at most 10 tool calls (as ND-Q).

## Arms
| Arm | What the model can do |
|---|---|
| RAW | Reads all 509 dated turns with speakers (run again on the test set) |
| RAGTOOL | Only `search_turns(query)`: BM25, top 5 dated turns per call (`engine/rag_mcp.py`) |
| STRUCT | The structured tools below, no text search **[A]** |
| TOOLS2 | The structured tools plus the same `search_turns` as RAGTOOL |

TOOLS2 vs RAGTOOL isolates what the structure adds to the same search. STRUCT vs RAGTOOL shows whether structure alone is enough.

## Tools (interface fixed at the freeze; read-only, deterministic, no LLM)
Every call returns at most 250 words (`catalog` 700), with an exact "N more" count and an `offset` for paging. Each event is shown as `[t123 | 2023-05-18 | Sam -> Evan] "the sentence" | type(role=value; ...) | type(...)`. **The source sentence is shown with its relations [A]**: in v1 only memory strings were returned, and the model could not recover what the strings dropped. RAGTOOL returns the same dated sentences, so both arms read the same kind of evidence and differ in how they find it.

| Tool | Returns |
|---|---|
| `catalog()` | Every relation type with its count, its role names and one example; the 30 most linked entities with counts; the date range. The model reads it to choose types and entities |
| `find(types?, entity?, role?, value?, speaker?, from?, to?, offset?)` | Count plus a page of 10 events in time order. `types` is a list (related types together). `entity` matches any slot or the `Entities` list by normalised name; "Evan" also matches "I" in Evan's turns and "you" in turns addressed to him. `value` matches words in slot values and in the sentence (stems: plural, -ing, -ed; no synonyms; not ranked) |
| `count(...same filters..., by?)` | Exact number of events and of distinct entities; `by` = type, speaker or month gives the breakdown |
| `values(entity, role?)` | In the relations that link `entity` (after the pronoun join), the distinct values of slot `role` (every role if omitted), grouped by relation type, with event ids |
| `event(id)` | One event in full |
| `neighbors(id, k)` | The k events before and after (k up to 3, the C9 window) |
| `search_turns(query)` | BM25 top 5 dated turns (TOOLS2 only) |

**Pronouns:** in display and in `entity` matching, "I" is the speaker and "you" the listener of that event. "we", "us", "they", "it", "that" are shown as stored and never joined.

**Time cues:** a closed list is resolved in code against the date of the turn: yesterday, today, tonight, tomorrow, last/next week, weekend, month, year, "last <weekday>", "N days/weeks/months/years ago", "in <month>", "<month> <year>". The event shows `cue -> resolved range`. Vague cues ("recently", "lately", "a few years back", "soon") are shown with the turn date and marked vague. `from` and `to` filter on the resolved range when there is one, otherwise on the turn date. Anything else is left unresolved and shown verbatim.

**Not included, on purpose:** code-computed "possibly similar types" hints (the Phase 2 synonym report was about 95% noise before the fix), role aliasing (Phase 4), any ranking inside the structured tools.

## Prompt
The ND-Q prompt text, unchanged except for the tool list: answer only from tool results; if nothing relevant is returned, say it is not in memory; do not accept a premise the memory does not support; the ND-3 final-answer instructions. The file is hashed into `FREEZE.sha256` with the tool descriptions.

## Measures
1. Accuracy: hand scores C = 1, P = 0.5, W = 0 against LoCoMo gold, arm labels hidden. The blind sheet is built by code with a random arm order per question, before anyone reads the answers.
2. Evidence recall of the trace: share of gold evidence events (dia_id mapped through the source) that appeared in any tool result; no LLM.
3. Cost: tool calls, words read, wall-clock, harness failures.
4. Failure notes per question: empty result, wrong entity, time cue unresolved, evidence only in text.

## Hypotheses and verdict
| ID | Hypothesis | Criterion |
|---|---|---|
| R1 | Structure adds to the same search | TOOLS2 >= RAGTOOL + 2.0 points |
| R2 | Close to reading everything | TOOLS2 >= 90% of RAW |
| R3 | Trace recall | TOOLS2 recall >= 0.80 (v1 TOOLS 0.68; BM25 0.76) |
| R4 | Reported, no threshold | STRUCT vs RAGTOOL; categories 1, 2 and 5; abstention; failure notes |
| R5 | Cost bounded | median <= 10 calls and <= 1,500 words read |

**Pass: R1 and R2.** R3 and R5 are reported either way. If R1 fails, the structure did not help on this memory and the report says so. If TOOLS2 beats RAGTOOL but STRUCT does not, the win is the combination, and the report words it that way. Thresholds **[A]**.

## Interpretation limits, stated now
- 40 questions, one conversation, one extraction run, one run per question, Claude only. A difference of 2 points is five questions of one category; treat 1 to 2 questions as noise.
- Phase 2 failed M6 and M7 on the spec arm. This experiment may fail for that reason, and the failure notes will say so. It is not a test of the extractor's best case.
- The answering model is also the query planner; temperature cannot be set on the CLI.
- Role names are fragmented (11 names for the one acting); `find(entity=...)` does not depend on role names, `values(entity, role)` does.
- The test set is read by the author at scoring time, after the freeze.

## Build order (after the freeze)
1. `engine/ndq2_tools.py` and tests against run 6 and the source (contract tests, time-cue grammar tests, pronoun join tests).
2. MCP server `engine/ndq2_mcp.py`, arm runner reuse (`tools/ndq_run.py` gets `--arm struct|tools2`).
3. Dev-set pilot (primary 40, unscored); fix tools and prompt; freeze hashes.
4. Draw the test set, run the four arms, blind sheet, hand scores, report.
