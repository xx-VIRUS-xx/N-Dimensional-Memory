# EXP-V7.4 — Adversarial Autonomous Memory Formation

V7.4 removes the accidental lexical shortcut exposed by V7.3.

**Core question:** Can an agent identify durable information worth remembering when important and unimportant events are semantically and lexically similar?

## Pipeline

1. 1,200-event noisy conversation corpus
2. Writer sees an unlabeled corpus only
3. Agent autonomously selects durable memory
4. Agent builds persistent V6-style memory
5. Selection quality is evaluated against hidden gold
6. Generated memory is consumed without raw conversation
7. Cross-agent handoff is evaluated

## V7.4 changes

- No signal/distractor labels in writer view
- No benchmark case IDs or relevant-event IDs
- No repeated boilerplate discriminator
- Semantic distractors and near-duplicates
- Obsolete/current-state sequences
- Discussion vs decision contrasts
- Tentative vs confirmed claims
- Repeated observations and paraphrases
- Delayed consequences separated by distractors

## Agents

Claude and Copilot. Codex remains excluded because of the previously disclosed rate limit.

## Important distinction

V7.4 measures selection, representation, consumption, and interoperability separately. A high score is not evidence of universal superiority over RAG.
