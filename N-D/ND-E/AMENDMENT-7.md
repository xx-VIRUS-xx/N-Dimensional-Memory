# ND-E amendment 7 (Phase 2 results, Phase 3 approved), 2026-10-09

EXP-NDE.md and amendments 1 to 6 stay on record. Prompt v4.1 (sha256 `ee9427ff...`) was not changed. Run 6 is the Phase 2 run: all 509 events, Haiku, one run, one fresh `claude -p` call per event, registry sequential.

## Results against the frozen thresholds
| Measure | Result | Threshold | Verdict |
|---|---|---|---|
| M1 valid JSON without retry | 509/509 | >=99% | pass |
| M2 relations with a type | 1822/1822 | 100% | pass |
| M3 entity-like values linked | 59/61 (97%); names and nouns only 25/27 | >=90% | pass, small sample |
| M4 new types, events 460-509 vs 1-50 | 1 vs 17 (6%) | <=25% | pass |
| M4 top-10 types' share of relations | 90% | >=60% | pass |
| M5 time cues kept | 41/42 (98%) | >=90% | pass |
| M6 evidence events with no entity key (55 distinct) | 10 (18%) | <=10% | **fail** |
| M7 smallest candidate set <=10 (55 events) | 48 (87%) | >=90% | **fail** |
| M6 / M7 with the event's `Entities` list (amendment 2, reported beside) | 6 (11%) / 52 (95%) | same | marginal fail / pass |
| M8 | 7,808 prompt chars on average; 39 types; 154 type-role pairs | reported | n/a |

M3 method: a random 100 slot values (seed 11) were labelled entity-like or not from the value text alone, link status hidden; 61 were entity-like, 59 linked (misses: `hope.object` "painting", "luck with keys"). The spec asks for 100 entity-like values; this sample is short of that and the 95% interval is roughly 89% to 99%. M5: the report found 42 cue events, the spec's regex 41. M6 and M7 use the 55 distinct evidence events; the spec's 74 counts dia_id mentions. The `joined` readings (amendment 6) are 18% / 85% on the spec arm and 11% / 93% beside it: joining "I" to the speaker merges explicit-name and first-person links, so some candidate sets grow (t40: 7 to 17). M7 rewards small sets, not complete ones, so it cannot show the value of the join.

## Why M6 and M7 failed
Seven of the 10 events without an entity key keep their content nouns inside a text value ("enjoying soda and candy", "concerned about health", "awesome hike", "is the sauce a family secret") while the nouns sit in `Entities`. The `Entities` list rescues six. Three events fail on both readings: t24 and t137 (social filler) and t125 ("what did you put in it", the referent is in the previous sentence).

## Other findings, recorded and not patched
- Name checks: no capitalised name or name value absent from its sentence (0 of 509 events); 4 of about 2,700 pronoun values left as text; 13% of listed entities unused (272 of 2054).
- Vocatives: `address` 157, `greeting` 31; a greeting without a greeting word once (t19).
- Role names: 11 names stand for the one acting (`asker` 151, `thanker` 106, `requester` 81, `agent` 81, `decider` 79, `hoper` 73, `giver` 67, `promiser` 57, `sympathizer`, `apologizer`, `claimer`); 36 distinct role names in all. Entity-first lookup is not affected; role-keyed lookup is.
- Types: `state` is 45% of relations; 16 types have 3 uses or fewer, 9 are singletons (`watched`, `captures`, `pushing`, ...); `address`, `greeting`, `farewell`, `thanks` are 18% of relations and carry only an addressee.
- "I" is 905 of 2,700 links (34%), "you" 297, "we" 68.
- M8 seconds: per-event `seconds` sum to 6.9 h, but the meta file spans 00:43 to 02:07 (84 minutes). Run 5 agreed with its own timestamps. Unexplained; M8 seconds are not used until it is.
- The synonym report listed 42 type pairs, about 40 of them noise (Evan and Sam stopped counting as hubs once they were under 30% of relations; nicknames "ev" and "bud"; `state` shares entities with everything).

## Decisions
1. The v4.1 extraction stands. No re-extraction and no v4.2 prompt.
2. **Phase 3 is approved by Prabhat Saxena ("phase3", 2026-10-09) although M6 and M7 failed on the spec arm.** The record keeps both facts: the Phase 2 gate in `STATUS.md` ("only if Phase 2 passes") was overridden by decision, not met. Phase 3 is designed to cover the failure: entity-first lookup with a text-search fallback.
3. The reference date for time cues is the `date` of the source row with the same `event_id`, joined at the query layer. Rows stay sentence-only. This closes the open item in `STATUS.md`.
4. The speaker/listener join of amendment 6 stays: "I" is the speaker, "you" the listener of that event, at the query layer.

## Tool change in this patch
`tools/nde_synonyms.py`: `--source` takes hub names from the speakers and listeners of the source; a type holding a quarter of all relations is not paired by shared entities; shared entities must be at least 0.3 of the smaller type's entities; numbered copies (`object_2`) compare as their base name; new section "role families" lists roles of different types whose links are mostly the same pronoun. On run 6 the type pairs fall from 42 to 2 (`promise` / `request`, `trip` / `trip_return`); 13 role variants and one role family (`asker`, `thanker`, `requester`, `agent`, `decider`, `hoper`, `giver`, `promiser`, `sympathizer`, `participant`, all "I") remain. Tests: 43 (6 new for this change, 7 for amendment 6), each new rule checked by a mutation.

## Phase 3
Draft spec: `ND-Q2/EXP-NDQ2.md`, status DRAFT. Nothing in it is built or frozen.
