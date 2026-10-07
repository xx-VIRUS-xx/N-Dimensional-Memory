# ND-E amendment 1 (prompt v3.1), 2026-10-07

EXP-NDE.md is unchanged and its hash in FREEZE.sha256 still holds. This file records what changed after the Phase 1 pilot (30 turns, Haiku, prompt v3.0). The v3.0 results are kept and still reported.

## Phase 1 result that triggered it (v3.0, run 1)
M1 30/30, M2 59/59, M5 4/4, M4 top-10 coverage 98%. M3 (hand read of review.md): about 54 linked of 89 entity-like values, about 60%, against 90%. The cause was one thing: the model left the speaker and the listener out of `Entities` when they appeared as plain names (27 of the unlinked values were Sam or Evan; when listed they linked every time). Another 8 were joint values ("Evan and family", "Sam and dad"), and some listed entities were used by no event.

## Changes
1. **Code:** `derive()` also treats the speaker and the listener as known entities. They are metadata supplied by code (spec rule 5), so this adds no model dependence. A name the model lists itself still wins. The stored `Entities` field remains exactly what the model returned.
2. **Prompt (v3.0 to v3.1):** Entities are the things the events point at; every role value that names one must also be listed; nothing is listed that no event uses; speaker and listener need not be listed. New rule 7: one entity or one short phrase per role value, never joined with "and" or a comma; use one event each or a second role (`participant`, `participant_2`).

## Offline check before any new model call
Re-deriving the 150 slot values of v3.0 run 1 with change 1 alone gives 81 linked instead of 54 (81 of about 89 entity-like values, about 91%). Change 2 is untested until the rerun.

## Rerun (same 30 turns, run 2) and how it is judged
M1 to M5 and M8 as in the spec, plus M3 re-scored by hand on the same entity-like definition for both runs. Phase 2 is not started until this is read. If M3 on v3.1 is below 90%, the next change is made the same way, as amendment 2.
