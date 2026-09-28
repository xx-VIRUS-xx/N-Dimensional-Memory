# N-D Contract v0

Invariants every N-D implementation and experiment must preserve. Each has a test that would catch a violation.

| ID | Invariant | Violation test |
|---|---|---|
| C1 | **One event per tick.** Ticks are unique and monotonic; two events never share one. | Any duplicate tick in a committed corpus. |
| C2 | **Event shape.** One happening per event; 1–6 roles; roles are catalog dimensions; fillers are a peg, a list of pegs, a short literal (≤40 chars), an event reference, or a bucket. | Schema validation failure; role not in catalog. |
| C3 | **Append-only.** Nothing is updated or deleted; retraction is a new record pointing at a specific event. | Any mutation of a committed event. |
| C4 | **Two clocks.** Tick = order learned and identity; `occurred` = world time. Questions about "what was true when" use `occurred`. | A late-learned past event changes the answer to a replay query before its tick. |
| C5 | **No stored inferred edges.** Structural relationships come only from collisions and trajectories. Only source-stated relations are stored, as events. | A relation present in memory with no stating event. |
| C6 | **No stored absences.** Absence is no record. A *stated* absence ("no decision was recorded") is a negative-polarity fact. | Filler text such as "not stated" / "unspecified". |
| C7 | **No inference inside a fact.** Conclusions are separate model-belief events. | Fact or claim containing "implies/suggests"-type content. |
| C8 | **Owned status.** Every event has exactly one status (fact, claim, speaker_belief, model_belief, open_question, intent) and an owner (null only for narrated facts). | Missing or multiple statuses. |
| C9 | **Resolution authority.** A bucket closes only by (a) an explicit statement, (b) the user, or (c) the engine's single-candidate rule: exactly one type-compatible candidate within the last 3 events or the current speaker turn. (c) is recorded as `resolved_by: engine` with its evidence ticks, and a later explicit statement or the user supersedes it. | A bucket closed any other way; an engine resolution with two or more compatible candidates or without evidence ticks. |
| C9a | **`model_belief` is a hint, never a resolution.** It does not close a bucket, does not remove candidates, is not input to the single-candidate rule, and is always shown labelled as the model's belief. | Any state, depiction or probe answer that equals an open bucket's `model_belief` with no resolution record. |
| C10 | **No self-confirmation.** A model belief never counts as evidence for itself; repetition by the same speaker is not corroboration. | Support count increases on a same-owner restatement. |
| C11 | **Exactness scope.** Memory is exact relative to extracted events, not the source text; extraction quality is always measured. | An experiment that reports memory accuracy without extraction accuracy. |
| C12 | **Two ambiguity runs.** Local: the stateless interpreter resolves only references answered inside the same sentence and marks the rest unresolved. Global: on every new event, the engine runs backward (fill or open buckets for the new event's references) and forward (close old buckets the new event explicitly answers). | An unresolved reference in an event with no bucket, engine resolution or unknown-referent record; an old bucket still open after an event that explicitly answers it. |
