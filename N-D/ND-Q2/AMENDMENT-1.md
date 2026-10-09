# ND-Q2 amendment 1: pilot done, tools and prompts frozen

Date: 2026-10-09. Amends `EXP-NDQ2.md` (frozen, unchanged). Written after the dev-set pilot (`PILOT.md`, two rounds) and before the test set is drawn.

## Pilot outcome
Round 1 found two defects (find paging after the word cap; call limit only in the prompt), fixed in patch 0035. Round 2 (struct and tools2 on the 40 dev questions, ragtool2 on q23 and q26): no harness errors, no call over 10, 8 of 120 find calls used `offset`, continuation notes appeared in 45 of 115 struct find calls (the cap cuts long result pages, as designed).

Round 2 trace recall on the dev set: struct 32/82 (round 1: 38), tools2 40/82 (round 1: 37). Same tools and prompt, so a swing of up to 6 events in 82 is run-to-run model variation. Differences of that size between arms on the test set are not evidence. The recall figure on the test set is reported with this caveat.

No tool or prompt was tuned to dev answers beyond the two defects above.

## Frozen now
| Item | SHA-256 |
|---|---|
| Tool names, descriptions and parameter schemas (`TOOLS` in `engine/ndq2_mcp.py`, JSON with sorted keys) | `935f4b19e861ff5bc58e771e8e3125e1a2a963f4d4a36ad2d36d9c24ec3b59fd` |
| STRUCT prompt (`tools/ndq2_run.py`) | `883e79bf83cf7e5dbcd3c5b3c41757dd5ba6b647dfe5f6a0283fc52e01992ff5` |
| TOOLS2 prompt | `60b34c3e43d6d9cfa7969cabe3209c36de466addedadef17b65426c3f94d4411` |
| RAGTOOL2 prompt | `35721ae0b5ebe93cc928807ad4132babcaadc33c17a33a0195890e8e733b0d29` |

The code files `engine/ndq2_tools.py`, `engine/ndq2_mcp.py`, `tools/ndq2_run.py`, `tools/ndq2_score.py`, `tools/locomo_chunk.py` and this amendment are listed in `FREEZE.sha256`. From here to the report nothing in that list changes. A bug found later is reported as a deviation, with its effect, not silently fixed.

## Decisions recorded
1. **RAGTOOL2 output format.** The RAGTOOL arm on the test set is `ragtool2`: `search_turns` only, BM25 with the scoring of the ND-3 RAG baseline, top 5 turns in time order, each shown as `[t123 | 2023-05-18 | Evan -> Sam] "sentence"` (id, ISO date of the turn, speaker to listener). It is the same function and the same format as `search_turns` inside TOOLS2, so the R1 comparison differs only by the structured tools. The ND-Q (v1) `rag_mcp.py` format is not used.
2. **Question count.** The spec says 156 questions are left after removing the dev set. The data gives 153 (193 conv-49 questions with evidence inside the chunk, minus 40). The draw is 40 from 153 with seed 11; the category quotas (15, 8, 8, 7, 2) are unchanged.
3. **Call limit.** 10 tool calls per question, enforced by the server (calls 11 onward return an error that says to answer). The prompts say the same.
4. **Word cap.** 250 words per tool result (catalog 700). `find` shows as many of the page's 10 events as fit and gives the offset that continues.
5. **Cue resolution** covers every slot value of every relation (as built), not only roles named time or when.
6. **`neighbors`** shows the centre event in full and the other events as sentences only.
7. **Reuse.** RAW is run again on the test set with `probe_harness.py raw`. Nothing from ND-Q (v1) or from the dev set is reused for scoring.

## Order from here
1. Draw the test set (seed 11, `--exclude` the dev probes). Record only the file hash and the category counts; nobody reads the questions.
2. Run RAW, ragtool2, struct, tools2 on it.
3. Build the blind sheet (random arm order per question, key kept apart), score by hand, run `tools/ndq2_score.py report`.
4. Report against R1 to R5 as written in `EXP-NDQ2.md`; pass is R1 and R2.
