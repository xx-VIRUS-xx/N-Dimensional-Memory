# ND-E amendment 3 (listener grounding check, code only), 2026-10-07

EXP-NDE.md, AMENDMENT-1.md and AMENDMENT-2.md are unchanged. **The extraction prompt is unchanged: v3.2, sha256 starting 6844bb51**, which is the prompt Phase 2 will run (a test pins this).

## Phase 1 run 3 (prompt v3.2, 30 turns, Haiku)
| | Run 1 (v3.0) | Run 2 (v3.1) | Run 3 (v3.2) | Target |
|---|---|---|---|---|
| M1 / M2 | 30/30, 59/59 | 30/30, 72/72 | 30/30, 66/66 | >=99% / 100% |
| M3 (hand read) | about 60% | about 98% | about 99% | >=90% |
| M4 new types per 10-turn window | 5, 4, 2 | 7, 4, 9 | 4, 5, 3 | last <=25% of first (decided only in Phase 2) |
| M4 top-10 coverage | 98% | 86% | 97% | >=60% |
| M5 | 4/4 | 4/4 | 4/4 | >=90% |
| Types / roles at turn 30 | 11 / 35 | 20 / 59 | 12 / 38 | reported |
| Seconds per turn | 33 | 45 | 41 | reported |

Amendment 2's fixes held: no `argument` / `acceptance`, no phrase-entities at t0, no synonym pairs. Types varied 11, 20, 12 across three prompts on the same 30 turns, so prompt effects cannot be separated from run-to-run variation with one sample each.

## Still wrong in run 3 (hand read)
1. "we" resolved to a named person: t3 (`companions=Sam`, text "we went to Rockies") and t8 (`companions=Evan`, text "We hiked a good distance", really Sam with his dad). At t5 the model kept "we all" as written. Run 1 and run 2 had the same t8 error.
2. Phrases listed as entities and linked: "good distance", "great memory", "tips for breaking old habits".
3. Fewer types, less precision: `decision` holds "start doing this" and "keep Evan posted"; `advice_giving` holds "take it easy" and "have a good one".
4. About ten entities listed but used by no event (for example "Icefields Parkway" at t22). The turn-level `Entities` key (amendment 2) covers retrieval of these.
5. Social acts and questions are still about 35% of events. Left as is: they sit in their own types and can be filtered by type.

## Change (code only)
`validate(rec, turn)` rejects an output in which a slot value equals the listener's name (case-insensitive) while the turn contains neither that name (whole word) nor a word for "you" (you, your, yours, yourself, you're, you'll, you've, you'd, y'all). The existing retry quotes the complaint and tells the model to keep "we", "they" or "us" as written and not guess who it includes, or to omit the role. The speaker is never checked, since the speaker is present by speaking. "we" does not ground the listener.

## Offline check before any new model call (51 listener-valued slots in runs 1 to 3, turn text from review.md)
Run 1: 21 slots, 0 flagged (its t8 slipped through as the compound "Sam and Evan"). Run 2: 16 slots, 1 flagged, t8. Run 3: 14 slots, 1 flagged, t8. No false positive in these slots. It cannot catch t3, because the text says "Glad you asked". It may wrongly flag a turn such as "we should catch up" where the listener really is included; the retry message lets the model keep "we", and the cost is one extra call.

## Not changed
Items 2 to 5 above. Nothing is rerun for this amendment: the prompt is the same text, and the check only fires on outputs that would have carried the error. Phase 2 reports how often the check fires (M8: attempts per turn) so its false-positive rate can be read from `review.md`.
