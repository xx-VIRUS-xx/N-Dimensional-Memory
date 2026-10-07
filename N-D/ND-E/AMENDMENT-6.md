# ND-E amendment 6 (speaker join decided, M6/M7 script, prompt frozen), 2026-10-07

EXP-NDE.md and amendments 1 to 5 stay on record.

## Phase 1 run 5 (prompt v4.1, same 30 events, Haiku, sentence only)
| | Run 4 (v4.0) | Run 5 (v4.1) | Target |
|---|---|---|---|
| M1 / M2 | 100% / 100% | 100% / 100% | >=99% / 100% |
| M3, entity-like values (hand read) | about 96% | about 99% | >=90% |
| M4 new types per 10 events | 7, 3, 2 | 9, 2, 3 (33%) | <=25%, decided in Phase 2 |
| M4 top-10 coverage | 98% | 96% | >=60% |
| M5 | 4/4 | 4/4 | >=90% |
| Relations / types / roles | 94 / 12 / 40 | 97 / 14 / 39 | reported |
| `state` share | 49% | 41% | reported |
| Seconds per event / prompt chars | 45 / 4575 | 48 / 5165 | reported |

Types across the five runs on the same 30 events: 11, 20, 12, 12, 14. One sample per prompt cannot separate a prompt effect from sampling noise, so M4 on 30 events says nothing about v4.1.

Fixed by v4.1: vocatives are `address` (6); no mistyped `greeting` found (t23 arguable); every pronoun value is listed in Entities; no invented names; "we" stays "we" (t0, t3, t5, t8, t22); no invented "I" at t0; `inquiry` has `asked_to` in 14 of 15.

Still wrong, recorded and not patched: about 20 listed entities are never a role value (abstract nouns inside text); "I" still inferred in imperatives and ellipsis (t3, t19, t21, t22, t23); duplicated social acts (t24 address+thanks, t27 thanks+appreciation); t3 "Glad you asked" typed `thanks`; role `subject` means the topic in `inquiry` and the described thing in `state`; `travel` / `activity` / `return` overlap for the same kind of event (hikes, trips); the synonym report finds 0 pairs and so misses that overlap, because the types share only pronouns.

## Decisions
1. **The prompt is frozen at v4.1** (sha256 `ee9427ff...`). No further prompt amendment before Phase 2. The defects above are inputs to the Phase 4 consolidation and to the join below, not reasons to retune on 30 events.
2. **"I" and "you" are resolved by a join, not by the extractor.** At the engine or query layer, "I" is the source `speaker` and "you" the source `listener` of the row with the same `event_id`. Stored rows stay sentence-only and are never rewritten. "we", "us", "they" and other pronouns are not joined. Nothing in the extractor or its prompt changes.
3. **M6 and M7 are computed by `tools/nde_evidence.py`**, with the arms below. The thresholds of the frozen spec apply to the `slots` arm; the other arms are reported beside it.

## M6 / M7 definitions as implemented
- Evidence events: dia_ids of the probes in categories 1 to 4, mapped to event ids through the source. The spec says 74; that is the number of dia_id mentions, and 55 of them are distinct events. The script uses the 55 distinct events as the denominator and reports it.
- Hub names: the speakers and listeners of the source (Evan, Sam). Pronouns: the list in `nde_synonyms.py`.
- Entity key: a linked slot value that is not a hub name and not a pronoun. Role key: (type, role, linked value), hub names and joined pronouns included.
- M6: evidence events with no entity key. M7: among evidence events with at least one key, the share whose smallest candidate set (events in the whole run sharing that key) is 10 or fewer; also reported over all covered evidence events.
- Arms: `slots` (spec) and `+entities` (the event's own Entities list also gives entity keys, amendment 2); each read `as stored` and `joined`.
- The join cannot change M6, because a joined "I" becomes a hub name, which is not an entity key. It can change M7 and attribution questions ("who said or did X"); the `joined` readings show by how much.
- Events missing from the extraction are not covered. On the 30-event run only 8 evidence events are covered, so those numbers mean nothing; the measures are read on Phase 2.

## Phase 2 (all 509 events)
Prompt v4.1, Haiku, one run, same source. Reported: M1 to M8 as in the spec, M6 and M7 from the script, the synonym report. Hand work: the M3 100-value sample from `review.md` (labels hidden), the synonym pairs marked same / parent-child / different.
