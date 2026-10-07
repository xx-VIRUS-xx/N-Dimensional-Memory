# ND-E amendment 4 (prompt v4.0): sentence only, relations, contract correction, 2026-10-07

EXP-NDE.md and amendments 1 to 3 stay on record. This amendment changes the extractor input, the stored row, the vocabulary and one wrong sentence in the spec. No Phase 2 data exists yet (the run was stopped before any row was written).

## Why
1. **Source purity (Prabhat Saxena).** Not all real conversation has a known speaker and listener, and the extractor must not be bound to, or polluted by, fields of this dataset. The source is the sentence.
2. **Vocabulary.** An **event** is one sentence. The `EventRelation` list is part of the event, and each item in it is a **relation** (a type plus role slots). Until now the code, the reports and my messages called the relations "events".
3. **Contract correction.** Spec rule 7 says the engine "resolves nothing". CONTRACT.md C9 says otherwise: a pronoun bucket closes only by an explicit statement, by the user, or by the engine's single-candidate rule (exactly one type-compatible candidate within the last 3 events or the current speaker turn, recorded as `resolved_by: engine` with its evidence ticks); with two or more candidates it stays open and shows the candidate list, most recent first; C12 adds a backward and a forward pass. Rule 7 should read "resolves only by C9". The frozen spec is not edited; this note is the correction.

## Glossary (from here on)
| Term | Meaning |
|---|---|
| event | one sentence of the conversation (`event_id` t0, t1, ...; what earlier files and messages called a turn) |
| EventRelation | the model's JSON list for that event |
| relation | one item of that list: `type` plus role slots (what earlier files called an "event") |
| slot | one role and its value; a value is a link (matched to `Entities` in code) or text |
In EXP-NDE.md the words "events" in M2, M3, M6 and M7 mean relations. Thresholds are unchanged.

## Changes
1. **Prompt v4.0** (sha256 `d17fe36e...`, pinned by a test). The model sees the sentence and the registry. It is not told who speaks, who is addressed, or when. Rule 3: "I", "me", "my", "you", "your" get a name only when the sentence itself supplies it (a vocative such as "Hey Priya", or "I'm Marcus"); otherwise they are put in `Entities` as written and used as the value, like any other pronoun without an antecedent. The example names are neutral on purpose, so no name from the dataset is in the prompt. Amendment 2's prompt rules are kept.
2. **Stored row** has no speaker, listener or date: `event_id`, `tick`, `Entities`, `EventRelation`, `relations`, `attempts`, `seconds`, `prompt_chars`, `registry`. The meta file records `"model_input": "sentence text and registry only"`. The source file still carries those fields; the extractor ignores them.
3. **Removed (they depended on dataset metadata):** amendment 1's linking of speaker and listener as known entities, and amendment 3's listener grounding check. Nothing else in the extractor reads speaker, listener or date.
4. **Renames:** stored key `events` becomes `relations`; report keys `M2_events_with_type` becomes `M2_relations_with_type`, `turns` becomes `events`, per-type counts say `relations`, `M5_time_cue_turns` becomes `M5_time_cue_events`. Readers accept old rows (`events` key). `nde_report.py` changed in names and in the review header only (it prints the sentence, with no speaker or date, because the model did not see them); the measure definitions are unchanged. Its hash in `FREEZE.sha256` is updated (old: `7b216a1aa302646a...`).

## What I expect, to be checked on run 4 (these are predictions, not results)
- "I" and "you" will be ambiguous entities in most relations. They link to an entity literally named "I" or "you", so M3 can stay high while meaning less; the hand read must count them separately.
- Names appear only where the sentence has them, so the Sam and Evan hubs shrink. M6 and M7 (not yet built) will measure a different thing than they would have with metadata.
- Attribution ("who said or did this") is no longer in the rows. The engine can resolve some of it through C9 and neighbors, but the single-candidate rule has nothing to work with when no sentence names anyone.
- The model might invent a name that is not in the sentence. Any such name is a leak or a hallucination and is counted.

## Not decided here
How the query layer learns who spoke and when: joining the source record by `event_id` is possible, but it is a separate decision, as is where time-cue resolution gets its reference date. The pronoun resolver of C9 and C12 over ND-E rows is not wired (nothing ingests ND-E rows into `nd_engine.py`).

## Run 4 (same 30 sentences) and how it is judged
M1 to M5 and M8 as in the spec. By hand: entity-like values left as text; count of "I"/"you" values; any name in a row that the sentence does not contain; "we", "us", "they" resolved to a named person; types and roles after 30 events. Then `nde_synonyms.py`. Phase 2 starts only after this is read, with the v4.0 hash recorded.
