# N-D status: what exists, what is only planned

Read this before assuming something was built. Updated 2026-10-07 (patch 0031). Status words: **built** (code and tests exist), **run** (a model run produced results), **spec** (written down, no code), **idea** (discussed, not specced), **parked** (decided to leave for later).

## Words
**event** = one sentence of the conversation (earlier files called it a turn). **EventRelation** = the model's list for that event. **relation** = one item of that list (type plus role slots; earlier files and messages called it an "event"). The extractor sees the sentence text only: no speaker, listener, date or neighbouring sentences, and stored rows carry none of them (amendment 4).

## ND-Q (query tools over the engine memory): finished, failed
| Item | Status |
|---|---|
| EXP-NDQ.md frozen spec, 8 query tools, MCP servers, runner, blind scoring | built, run |
| Result: TOOLS 26.5 vs RAGTOOL 31.0, RAG 28.5, RAW 32.5 (REPORT.md) | reported |
| Cause: what is stored and shown, not tool misuse | reported |

## ND-E (store typed events with role slots): in progress
| Item | Status |
|---|---|
| EXP-NDE.md frozen spec; M1 to M8 defined | spec, frozen |
| `extract_events.py` (registry, validation, retries, resume, links decided in code) | built, run (runs 1 and 2) |
| Amendment 1: speaker and listener linked in code, prompt v3.1 | built, run (run 2); **mechanism removed in amendment 4** |
| Amendment 2: prompt rules (we/us/they, no phrases as entities, example types), turn-level Entities counted for M6/M7 | built, run (run 3); rules kept in v4.0 |
| Amendment 3: listener grounding check | built, **removed in amendment 4** (it needed the listener field) |
| Amendment 4: prompt v4.0 (sentence only, "I"/"you" ambiguous unless the sentence names them), relations vocabulary, no speaker/listener/date in rows, C9 correction | built (0030), **not run yet (run 4 pending)** |
| Amendment 5: prompt v4.1 (vocative = `address`, pronoun values listed in Entities, no unused entities), synonym report ignores pronouns | built (0031), **not run yet (run 5 pending)** |
| `nde_synonyms.py`: synonym-candidate report | built (0028, fixed in 0031), run on runs 1 to 4 |
| `nde_report.py`: M1 to M5 and M8, review.md for the M3 hand check | built, run |
| **M6 and M7 computation** (evidence oracle: `probes.jsonl` lists `dia_id`s per question and `source.jsonl` maps `dia_id` to `event_id`, so it is buildable) | **not built** |
| **Decision: resolve "I" and attribution by joining the source `speaker` field on `event_id` at the engine/query layer (rows stay pure)** | **undecided**; recommended; without it M6 and "who said X" questions are expected to fail |
| Phase 1 run 3 (30 events, v3.2): M1 to M3 and M5 pass; M4 undecided at 30 events | run (see AMENDMENT-3.md) |
| Phase 1 run 4 (30 events, v4.0, sentence only): M1, M2, M5 pass; M3 about 96% (about 90% on named entities only); M4 29% on 10-event windows; 94 relations, "I" is about 39 of 109 links | run (see AMENDMENT-5.md) |
| Phase 1 run 5 (30 events, v4.1) | pending your run |
| Phase 2: all 509 events, M1 to M8, prompt hash fixed beforehand (the v4.x prompt of the last Phase 1 run). Stopped before any data was written. About 45 s per turn, so about 6.4 hours sequential; registry is sequential by design | **not run** |
| Pronoun resolution over ND-E rows: contract C9 (explicit statement, user, or the single-candidate rule within the last 3 events; otherwise an open bucket with candidates, most recent first) and C12 (backward and forward runs). Spec rule 7 wrongly said the engine resolves nothing (AMENDMENT-4.md). **ND-E rows are not ingested by `nd_engine.py`: not wired** | spec / contract only |
| Attribution (status field) no longer enforced; false-premise questions (category 5) reported separately | spec only |

## Phase 3 (only if Phase 2 passes): query side. Nothing here is built
| Item | Status |
|---|---|
| `catalog` view: every type with count, role names, one example; top entities with counts | idea |
| Multi-type filter `types=[...]`; the model maps a question to a set of related types, entities, roles | idea |
| Count first, narrow, then fetch (narrow-or-count); facets; `describe` | idea |
| Entity-first route (events where any slot links to X), type as secondary filter | idea |
| Text-search fallback over slot values; optional BM25 rank inside a filtered set | idea |
| `offset` paging; `neighbors(tick, +-3)` (C9's window of 3 events); `values(entity, role)` | idea |
| Time cues shown and resolved in code against the day the turn was said | idea |
| Code-computed "possibly similar types" hints (from nde_synonyms signals) | idea |
| New frozen ND-Q v2 spec scored on the 40 fresh conv-49 questions (seed 11), RAGTOOL control again | not drafted |

## Phase 4 (optional): memory consolidation. Nothing here is built
| Item | Status |
|---|---|
| Alias layer: mapping of type, role and entity names to canonical ones; stored events untouched; reversible | idea |
| Code proposes candidate clusters, an LLM judges merge, keep separate, or parent/child, with real examples | idea |
| Prefer hierarchy (`travel` over `travel_return`) to hard merges; entity surface-form merging too | idea |
| Canonical names shown in the extraction prompt afterwards, so drift slows at the source | idea |
| Checks: event and slot counts identical before and after; M7 not worse; hand-checked merge precision with arm labels hidden; frozen decision log | idea |
| Trigger: only if Phase 2 shows the catalog outgrowing what can be shown, or many real duplicates in the synonym report | idea |

## Known problems found, not fixed
- "we" resolved to a person at t3 (Sam) and t8 (Evan) in runs 1 to 3 (with speaker/listener given); v4.0 gives no names, so this should change; run 4 checks.
- Attribution (who spoke) is not in the rows; how the query layer gets it is undecided (AMENDMENT-4.md).
- Phrases listed as entities and linked ("good distance", "great memory"); fewer types in run 3 meant coarser types (`decision`, `advice_giving` hold unrelated acts).
- About 35% of run-2 events are social acts or questions. Left as is; filterable by type.
- `breakdown` filed apart from `state`, and `thanks` filed as `greeting`: not detectable by the synonym tool; hand read only.
- An entity inside a text value is not a link; the turn-level Entities list is the fallback key.
- Run-to-run variation of Haiku is unmeasured (one sample per prompt so far).
- Source quirk at t21: speaker Evan, text addressed to Evan.

## Parked
ND-P paper test; layered engine; Postgres ledger (ND-4); updating the paper doc's ND-3 row; cross-family replication; RAGTOOL evidence recall (traces now exist).

## Process rules
Commit and push once, never amend after pushing. Do not commit `ND-E/phase1/` or `ND-E/phase1_v31/` until told. Spec, freeze hashes and amendments: a frozen spec is never edited; changes go in numbered amendments with their own hash in `ND-E/FREEZE.sha256`.
