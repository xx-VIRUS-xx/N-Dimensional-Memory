# ND-E amendment 5 (prompt v4.1), 2026-10-07

EXP-NDE.md and amendments 1 to 4 stay on record. Runs 1 to 4 stay on record. The sentence-only input of amendment 4 is unchanged.

## Phase 1 run 4 (prompt v4.0, 30 events, Haiku, sentence only)
| | Run 3 (v3.2, with metadata) | Run 4 (v4.0) | Target |
|---|---|---|---|
| M1 / M2 | 30/30, 66/66 | 30/30, 94/94 | >=99% / 100% |
| M3, all links (hand read) | about 99% | about 96% | >=90% |
| M3, named entities only | about 95% | about 90% | >=90% |
| M4 new types per 10 events | 4, 5, 3 | 7, 3, 2 (last/first = 29%) | last <=25% of first, decided in Phase 2 |
| M4 top-10 coverage | 97% | 98% | >=60% |
| M5 | 4/4 | 4/4 | >=90% |
| Relations / types / roles | 66 / 12 / 38 | 94 / 12 / 40 | reported |
| Seconds per event | 41 | 45 | reported |

## What worked
No name from the dataset appeared in any row (names occur only where the sentence has them). "we" stayed "we" at t3, t5, t8, so the error that amendment 3 patched is gone without it. The model derived addressees from vocatives ("see you" after "Take it easy, Evan!" became "can't wait to see Evan").

## What went wrong (hand read)
1. **Vocatives were typed `greeting`.** 9 `greeting` relations, about 4 of them not greetings ("Thanks, Evan!", "No worries, Sam!", "That sounds great, Evan!"). The model used `greeting` to record who is addressed.
2. **"I", "you", "we" used as values without being listed** in `Entities` (t4, t19, t22), so they stayed text; t22 lists 11 entities, several unused; "Mine" (t25) and abstractions such as "journey" listed as entities.
3. **"I" dominates the links:** about 39 of 109 links are "I", about 69 of 109 are pronouns. The model uses "I" for the implicit speaker even when the sentence has no "I" (t0, "What's new?"). With no speaker field, "I" means a different person each sentence.
4. **Volume and noise:** 94 relations against 66; `state` is 49% of relations, including social filler ("glad to see Evan", "sorry to hear that"); `exhortation` lumps requests, farewells and advice (8); `question` has `asker` in 10 of 14 and `addressee` in 8 of 14.
5. **Synonym report overfired** (6 of 8 pairs came from shared entities such as Evan or you, which stop being hubs once metadata is gone) and printed a leftover `turn` key.

## Changes
1. **Prompt v4.1** (sha256 `ee9427ff...`, pinned by a test). Pronoun values ("I", "you", "we", "it", ...) must be listed in `Entities`; an entity is listed only if it appears as a role value. A name used to address someone is one relation of type `address` with role `addressee`; `greeting`, `thanks` and `farewell` only when the sentence really is one. The rest of v4.0 is unchanged.
2. **`nde_synonyms.py`:** pronoun links are not counted as shared entities, three shared non-hub entities are needed (was two), and the example key is `event`. On run 4 the report now lists exactly `activity` / `activity_start` and `trip` / `trip_return`.

## Not changed, on purpose
Social-filler states and `exhortation` lumping stay as the model interprets them. Whether "I" is resolved to the speaker, by joining the source `speaker` field on `event_id` at the engine or query layer, is **undecided**. It would keep rows free of dataset fields and keep attribution answerable; without it, M6 and "who said or did X" questions are expected to fail on sentences whose only key is "I".

## Run 5 (same 30 events) and how it is judged
M1 to M5 and M8. By hand: `address` used for vocatives and `greeting` only for greetings; pronoun values all listed in `Entities`; unused entities; any name not in the sentence; "we" resolved to a named person; types and roles after 30 events. Then `nde_synonyms.py`.
