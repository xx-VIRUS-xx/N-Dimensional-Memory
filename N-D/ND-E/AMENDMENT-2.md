# ND-E amendment 2 (prompt v3.2), 2026-10-07

EXP-NDE.md and AMENDMENT-1.md are unchanged. Runs 1 and 2 stay on record.

## Phase 1 run 2 (prompt v3.1, 30 turns, Haiku)
| | Run 1 (v3.0) | Run 2 (v3.1) | Target |
|---|---|---|---|
| M1 / M2 | 30/30, 59/59 | 30/30, 72/72 | >=99% / 100% |
| M3 (hand read of review.md) | about 60% | about 98% | >=90% |
| M4 new types per 10-turn window | 5, 4, 2 | 7, 4, 9 | last <=25% of first (decided only in Phase 2) |
| M4 top-10 coverage | 98% | 86% | >=60% |
| M5 | 4/4 | 4/4 | >=90% |
| Seconds per turn | 33 | 45 | reported |
| Registry at turn 30 | 11 types, 35 roles | 20 types, 59 roles | reported |

M3 caveats: 13 of the 95 links are pronouns (ambiguous by design) and 3 are phrases the model listed as entities at t0 ("since we last met" and two others). Without them, about 79 of 81. Run 2 is one sample; Haiku varies run to run.

## What went wrong in run 2 (hand read)
1. "we" with no antecedent was resolved to the listener (t8: the hike was Sam with his dad, stored as companion=Evan). Run 1 made the same mistake.
2. The Bob/Alice format example leaked its generic types: `argument` and `acceptance` at t25 (2 of 72 events).
3. v3.1's "every named role value must be in Entities" made the model list phrases and a time cue as entities (t0).
4. Of the 20 types, about 15 are genuinely new acts at first appearance. The real overlaps: `travel` / `travel_return` (same trip), `breakdown` (a `state` event under its own type), and `thanks` stored as `greeting` at t18. Not caused by synonyms: about 35% of events are social acts or questions (greeting, farewell, thanks, commiseration, offer_help, question). Left unchanged on purpose: they sit in their own types and can be filtered out by type later.

## Changes
1. **Prompt v3.2.** Entities: a phrase, a time expression, a feeling or a question is never an entity. Rule 4 now names we, us, they, he, she, there and says "we", "us" and "they" do not automatically mean the listener. The format example uses domain-specific types (`database_recommendation`, `proposal_acceptance`) and says they belong to the example only.
2. **`tools/nde_synonyms.py` (report only).** Lists type pairs that share a name token, two or more specific role names, or two or more non-hub linked entities, plus role-name variants inside one type. Generic roles (used by a fifth of all types) and hub entities (linked in 30% of events) are ignored. It merges and changes nothing. On run 2 it finds `travel` / `travel_return` and the role pair `claim` / `claim_subject`; on run 1 it finds nothing. It cannot find `breakdown` vs `state` or a misfiled `thanks`; those need a hand read of the review file.
3. **Measurement rule for M6 and M7 (Phase 2).** Each turn's own `Entities` list is also a key for its events, because an entity inside a text value ("how you got into watercolor painting") is not a link. M6 and M7 are reported twice: with slot links only, and with slot links plus the turn's `Entities`. The thresholds apply to the slot-links-only number; the second number is reported beside it.

## Rerun (same 30 turns, run 3) and how it is judged
M1 to M5 and M8 as in the spec, M3 by hand with the same entity-like definition, plus: any `we`, `us`, `they` resolved to a named person; any event typed `argument` or `acceptance`; entities listed that are phrases. Then run `nde_synonyms.py` on runs 2 and 3. Phase 2 is not started, and its prompt hash is not fixed, until this is read.

## Not part of this amendment
The query-side design and the consolidation pass are planned, not built. See `N-D/STATUS.md`, which lists every planned item and whether it exists.
