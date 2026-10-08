# ND-Q2 dev-set pilot (unscored)

Run 2026-10-09 on the 40 ND-3 questions (dev set), run 6 memory, Sonnet, arms struct, tools2, ragtool2. Nothing was hand-scored for the hypotheses; answers were read against LoCoMo gold only to debug tools. These numbers are not results.

| Arm | calls median (max) | words read median (max) | harness errors | cost | trace evidence recall (mean per question; pooled) |
|---|---|---|---|---|---|
| struct | 2 (7) | 320 (1066) | 0 | $1.58 | 0.739; 38/82 |
| tools2 | 1 (5) | 203 (811) | 0 | $1.45 | 0.744; 37/82 |
| ragtool2 | 2 (12) | 360 (1542) | 0 | $1.49 | 0.766; 39/82 |

Tool use: struct called find 86, values 5, neighbors 4, catalog 3, event 3, count 0. tools2 called search_turns 41, find 14, neighbors 10, event 6, values 3, catalog 0, count 0. The model mostly searches; structure is used for dates and entity filters.

## Defects found and fixed (patch 0035)
1. `find` paging. The 250-word cap cut 40 of 100 find results to 2 to 4 events while the header said "showing 1-10", and the hint "use offset" pointed at offset 10, which would have skipped the cut events. Now the header says what was shown (`showing a-b`), the note gives the exact next offset, and an over-long single event is truncated, never skipped. Tests walk the offsets and check every event is visited once.
2. The 10-call limit was only in the prompt (ragtool2 made 12 calls on q26). The server now refuses call 11 onward with an error that says to answer.
3. The `find` description now says "as many as fit in about 250 words".

## Observations kept on record, no change made
- Recall of all three arms is 0.74 to 0.77, under the R3 line (0.80). Misses are mostly questions that need many events (q09 gift 17 events, q11 7, q13 8, q08 5, q04 4) and questions whose gold sits in words the question does not use (q07 soda and candy vs "unhealthy snacks").
- Time questions (q03, q05, q06, q14, q15, q16) were answered with resolved dates in all three arms; q26 ("9th December") was answered by struct and tools2 through the date filter and failed in ragtool2 after 12 searches.
- Adversarial questions (cat 5): by a quick unscored read, all three arms rejected or corrected the premise on all 8; none accepted a wrong premise.
- `count` and `catalog` are rarely used. They stay: the spec names them and unused tools cost nothing.
