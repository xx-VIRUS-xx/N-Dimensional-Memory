# ND-E: event-relation extraction with an accumulating type/role registry

**Status:** DRAFT 2026-10-07. Not frozen. Thresholds below are proposals for approval; they freeze before the first extraction run, and any later change is a new version.

## Why
ND-Q (REPORT.md) showed the query tools were limited by what the memory stores and shows. Measured on the ND-3 memory: 96% of `action` values are unique (492 of 512), values average 4.2 words, relations live inside free-text values (a single announcement is stored three times, once per entity), 7% of strings sit on pronoun pegs, and 23 of 74 evidence events (31%) have no entity to key on except Evan, Sam or a pronoun (Evan and Sam are in 86% of events). The tools can narrow only on what is categorical, and almost nothing is.

ND-E tests a different thing to store: per turn, a list of entities plus a list of typed events whose role slots point at those entities.

## Target output (one JSON object per turn)
```
{"Entities": ["Bob", "CockroachDB", "multi-region payments", "Alice", "proposal"],
 "EventRelation": [
   {"type": "argument", "arguer": "Bob", "claim_subject": "CockroachDB", "claim": "better", "domain": "multi-region payments"},
   {"type": "acceptance", "acceptor": "Alice", "accepted_object": "proposal"}]}
```

## Rules (these go into the prompt; the model interprets, the code enforces)
1. **Only `type` is structural.** Every other key is a role name the model chooses. No fixed dimension list; the model is told what to record (time expressions, who claims or believes, states) and does so by itself.
2. **Registry.** After each turn, code adds new types and role names to a registry (snake_case, lowercase, exact-duplicate merge only, no synonym merging). The next prompt shows the registry: types by frequency with counts, each type's role names with counts, one example each (top 40 types, up to 8 roles each, plus every type seen in the last 20 turns). The model reuses a name when one fits, and may create a new type or role when none does. Extraction is therefore sequential by tick, like the ND-3 dimension dictionary.
3. **Entity or literal is decided in code.** A slot value that matches a name in `Entities` (case-insensitive, leading determiners and possessives dropped, plural folded, as `find_entity` does) is a link; anything else is text. The prompt only says what belongs in `Entities`: things, people, places, tools and topics that can come up again.
4. **States are events**: type `state` with a subject and the state.
5. **Time:** a time expression in the turn is recorded verbatim in a role the model names. Code resolves it against the day the turn was said (it never trusts the model's arithmetic). Speaker, listener, day said and tick are metadata supplied by code from the source, never extracted.
6. **Empty is allowed.** A slot the model cannot fill is omitted. Nothing is invented. Omissions count as extraction failures in the measures below.
7. **Pronouns and missing subjects:** the pronoun is recorded as an ambiguous entity (`it`, `that`, ...); its candidates go to the ambiguity bucket and the engine resolves nothing (C9, C9a). Where several unrelated candidates exist they are displayed most recent first, and a user's correction is recorded as a user resolution. Display order only.
8. **Attribution** (whose claim or belief) is carried by the event's own roles (arguer, believer, ...) plus the speaker metadata. The ND-3 status field (fact, claim, speaker_belief, open_question, intent) is no longer enforced. Known risk: false-premise questions (category 5) relied on it, so they are reported separately.

## Measures (structural; no handwritten gold, nothing graded against it)
| ID | Measure | Proposed threshold |
|---|---|---|
| M1 | Turns with valid JSON (no repair) | >= 99% |
| M2 | Events with a `type` | 100% |
| M3 | Slot values that are links (matched to `Entities`) among entity-like values, on a 100-value hand-checked sample | >= 90% |
| M4 | Registry health: new types in turns 460-509 vs turns 1-50 | <= 25% of the first window; top 10 types cover >= 60% of events |
| M5 | Turns with a time expression (41 found by regex) whose event keeps it | >= 90% |
| M6 | Evidence events (74, categories 1-4 of the 40 ND-3 questions) with no key other than Evan, Sam or a pronoun | <= 10% (current memory: 31%) |
| M7 | Candidate-set size after narrowing by the best key, over events that have one (type plus a role value counts as a key) | <= 10 events in >= 90% (current memory: 100% where a key exists, 69% overall) |
| M8 | Cost: tokens and seconds per turn, registry size per turn | reported |

M6 and M7 use the evidence turns as an oracle (what narrowing would be possible), not as an answer check. A gold-word overlap measure was tried and dropped: it scores 12/23 on both the current memory and the raw text, so it cannot tell memories apart.

## Phases
0. This spec, reviewed and approved (no model calls).
1. Prototype on 30 turns with Haiku; read the output by hand; check M1-M3.
2. Extract all 509 turns; compute M1-M8; compare with the current memory.
3. Only if Phase 2 passes: drill-down tools over type, role and entity (`describe`, facets, role sets, narrow-or-count, `neighbors`, resolved time), then a new frozen ND-Q v2 spec scored on the 40 fresh conv-49 questions.

## Not tested here
Whether answers improve (that is ND-Q v2), other models, other conversations, cross-turn coreference, any change to the engine's ambiguity rules.
