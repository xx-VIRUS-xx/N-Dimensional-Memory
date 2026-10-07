# N-D status: what exists, what is only planned

Read this before assuming something was built. Updated 2026-10-07 (patch 0028). Status words: **built** (code and tests exist), **run** (a model run produced results), **spec** (written down, no code), **idea** (discussed, not specced), **parked** (decided to leave for later).

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
| Amendment 1: speaker and listener linked in code, prompt v3.1 | built, run (run 2) |
| Amendment 2: prompt v3.2 (we/us/they, no phrases as entities, example types), turn-level Entities counted for M6/M7 | built (0028), **not run yet** |
| `nde_synonyms.py`: synonym-candidate report | built (0028), run on runs 1 and 2 |
| `nde_report.py`: M1 to M5 and M8, review.md for the M3 hand check | built, run |
| **M6 and M7 computation** (needs the evidence oracle: map the 74 evidence events of the 40 ND-3 questions to turns) | **not built** |
| Phase 1 rerun, run 3 (30 turns, v3.2) | pending your run |
| Phase 2: all 509 turns, M1 to M8, prompt hash fixed beforehand. About 45 s per turn, so about 6.4 hours sequential; registry is sequential by design | **not run** |
| Pronoun rule at display time (most recent candidate first, user correction recorded) | spec only (rule 7); no engine change |
| Attribution (status field) no longer enforced; false-premise questions (category 5) reported separately | spec only |

## Phase 3 (only if Phase 2 passes): query side. Nothing here is built
| Item | Status |
|---|---|
| `catalog` view: every type with count, role names, one example; top entities with counts | idea |
| Multi-type filter `types=[...]`; the model maps a question to a set of related types, entities, roles | idea |
| Count first, narrow, then fetch (narrow-or-count); facets; `describe` | idea |
| Entity-first route (events where any slot links to X), type as secondary filter | idea |
| Text-search fallback over slot values; optional BM25 rank inside a filtered set | idea |
| `offset` paging; `neighbors(tick, +-2)`; `values(entity, role)` | idea |
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
- About 35% of run-2 events are social acts or questions. Left as is; filterable by type.
- `breakdown` filed apart from `state`, and `thanks` filed as `greeting`: not detectable by the synonym tool; hand read only.
- An entity inside a text value is not a link; the turn-level Entities list is the fallback key.
- Run-to-run variation of Haiku is unmeasured (one sample per prompt so far).
- Source quirk at t21: speaker Evan, text addressed to Evan.

## Parked
ND-P paper test; layered engine; Postgres ledger (ND-4); updating the paper doc's ND-3 row; cross-family replication; RAGTOOL evidence recall (traces now exist).

## Process rules
Commit and push once, never amend after pushing. Do not commit `ND-E/phase1/` or `ND-E/phase1_v31/` until told. Spec, freeze hashes and amendments: a frozen spec is never edited; changes go in numbered amendments with their own hash in `ND-E/FREEZE.sha256`.
