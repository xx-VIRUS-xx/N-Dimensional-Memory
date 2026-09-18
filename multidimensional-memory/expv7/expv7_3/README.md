# EXP-V7.3 — Autonomous Memory Formation

V7.3 removes the benchmark scaffolding that made V7.2 memory construction easier.

## Core question
Can an agent autonomously decide what deserves persistent memory from a long, noisy conversation, construct model-agnostic structured memory, and hand that memory to another agent without the original conversation?

## What changes from V7.2
- No `kind: signal/distractor` labels exposed to the writer.
- No benchmark `raw_event_ids` exposed to the writer.
- No delayed-query relevance hints exposed to the writer.
- Writer sees only the unlabeled chronological conversation corpus and V6 memory schema/design rules.
- Gold annotations remain evaluator-only.
- Importance selection is now part of the measured task.

## Evaluation layers
1. **Selection quality:** did the writer retain the events that matter and avoid distractors?
2. **Memory construction quality:** are observations, propositions, relations, states, ambiguity, beliefs, negative knowledge, and provenance correct?
3. **Compression quality:** how much of the corpus was retained, and what useful information was lost?
4. **Consumption quality:** can the same or another agent answer delayed queries from generated memory alone?
5. **Cross-agent persistence:** can Claude consume Copilot memory and Copilot consume Claude memory?

V7.3 is deliberately not a leaderboard. It is a controlled experiment about autonomous memory formation.
