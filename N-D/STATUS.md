# N-D status: what exists, what is only planned

Read this before assuming something was built. Updated 2026-10-09 (patch 0035). Status words: **built** (code and tests exist), **run** (a model run produced results), **spec** (written down, no code), **idea** (discussed, not specced), **parked** (decided to leave for later).

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
| Amendment 5: prompt v4.1 (vocative = `address`, pronoun values listed in Entities, no unused entities), synonym report ignores pronouns | built (0031), run (run 5) |
| `nde_synonyms.py`: synonym-candidate report (source hubs, catch-all and overlap rules, role families) | built (0028, fixed in 0031 and 0033), run on runs 1 to 6 |
| `nde_report.py`: M1 to M5 and M8, review.md for the M3 hand check | built, run |
| `nde_evidence.py`: M6 and M7 from the evidence events of the probes (arms slots / +entities, as stored / joined) | built (0032), run on run 5 (8 evidence events covered; meaningless until Phase 2) |
| Decision: "I" = source `speaker`, "you" = source `listener`, joined on `event_id` at the engine/query layer; rows stay sentence-only; extractor and prompt unchanged | decided (amendment 6); join itself not built (the `joined` reading in `nde_evidence.py` simulates it) |
| Prompt v4.1 frozen for Phase 2 | decided (amendment 6) |
| Phase 1 run 3 (30 events, v3.2): M1 to M3 and M5 pass; M4 undecided at 30 events | run (see AMENDMENT-3.md) |
| Phase 1 run 4 (30 events, v4.0, sentence only): M1, M2, M5 pass; M3 about 96% (about 90% on named entities only); M4 29% on 10-event windows; 94 relations, "I" is about 39 of 109 links | run (see AMENDMENT-5.md) |
| Phase 1 run 5 (30 events, v4.1): M1, M2, M3 (about 99%), M5 pass; M4 9/2/3; 97 relations, 14 types; defects listed in AMENDMENT-6.md | run |
| Phase 2 (509 events, prompt v4.1, run 6): M1 to M5 pass; M6 18% and M7 87% fail on the spec arm (11% and 95% with the Entities list); results in AMENDMENT-7.md | run |
| Pronoun resolution over ND-E rows: contract C9 (explicit statement, user, or the single-candidate rule within the last 3 events; otherwise an open bucket with candidates, most recent first) and C12 (backward and forward runs). Spec rule 7 wrongly said the engine resolves nothing (AMENDMENT-4.md). **ND-E rows are not ingested by `nd_engine.py`: not wired** | spec / contract only |
| Attribution (status field) no longer enforced; false-premise questions (category 5) reported separately | spec only |

## Phase 3: query side. Approved 2026-10-09 although M6 and M7 failed on the spec arm (AMENDMENT-7.md). Spec `ND-Q2/EXP-NDQ2.md` frozen 2026-10-09; tools, server, runner and scorer built (0034); dev-set pilot not yet run
| Item | Status |
|---|---|
| `engine/ndq2_tools.py`: catalog, find (types list, entity, role, value, speaker, from/to, offset), count (by type/speaker/month), values, event, neighbors, BM25 `search_turns`; 250-word cap (catalog 700) with exact "n more not shown"; errors as text | built (0034), contract tests with mutation checks |
| Time cues shown as `cue -> range` and resolved in code against the source `date` joined on `event_id` (closed list in `resolve_cue`) | built (0034) |
| "I" = speaker, "you" = listener joined at query time, rows never rewritten | built (0034) |
| `engine/ndq2_mcp.py`: MCP server, arms struct / tools2 / ragtool2 | built (0034), protocol tests |
| `tools/ndq2_run.py`: runner (one isolated `claude -p` per question, 10 calls), prompts draft | built (0034), stub-claude tests; prompts and tool descriptions freeze after the dev-set pilot |
| `tools/ndq2_score.py`: blind sheet (random order, key kept apart), R1 to R5, trace evidence recall, cost | built (0034), tests |
| `tools/locomo_chunk.py --exclude`: disjoint fresh draw | built (0034); draw gives 153 questions left, not the 156 in the spec |
| Dev-set pilot on the 40 ND-3 questions (unscored): ran, found a `find` paging bug and a missing server-side call limit, both fixed (0035); findings in `ND-Q2/PILOT.md` | run (round 1) |
| Pilot round 2 on struct and tools2 to confirm the fixes, then ND-Q2/AMENDMENT-1 freezing descriptions, prompts and the RAGTOOL2 output format | next |
| Test-set draw (seed 11), four arms, blind scoring, report | after the freeze |
| Code-computed "possibly similar types" hints | dropped from ND-Q2 (Phase 2 synonym report was mostly noise before the fix) |

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
- Attribution (who spoke) is not in the rows; the query layer joins it from the source by `event_id` (decided in amendment 6; not built).
- Phase 2: content nouns often sit inside text values (M6, M7 fail on the spec arm); 11 role names stand for the one acting; `state` is 45% of relations; 9 singleton types; social acts 18% of relations; M8 seconds do not match the run's wall-clock (AMENDMENT-7.md).
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
