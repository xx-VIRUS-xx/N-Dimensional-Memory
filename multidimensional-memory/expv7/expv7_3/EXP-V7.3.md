# EXP-V7.3 — Autonomous Memory Formation

## 1. Research question
Can a general-purpose coding agent transform a long, noisy conversation into persistent model-agnostic memory without being told which events are important?

## 2. Hypotheses
- H1: agents can identify high-value events without explicit signal/distractor labels.
- H2: generated memory preserves the important temporal, relational, ambiguous, belief, negative-knowledge, action/outcome, and provenance semantics established in V7.2.
- H3: generated memory remains consumable by another model without the original conversation.
- H4: importance selection introduces measurable recall/precision tradeoffs that were hidden by V7.2 scaffolding.

## 3. Corpus
Use the same 1,200-event chronological corpus from V7.1/V7.2, but expose an **unlabeled writer view**. The writer must not see:
- signal/distractor labels
- benchmark case IDs
- raw_event_ids associated with cases
- expected answers
- gold memory
- V7.1/V7.2 results
- relevance hints derived from delayed queries

The evaluator may use the gold annotations after the writer artifact is frozen.

## 4. Writer task
The writer receives the full chronological conversation and the memory design rules. It must decide what deserves persistence.

Required principles:
- retain durable decisions, actions, outcomes, state transitions, unresolved ambiguity, belief evolution, conflicts, negative knowledge with scope, and provenance when supported;
- preserve source event IDs for retained observations;
- never invent source events;
- distinguish observation from inference and confirmation;
- preserve uncertainty rather than resolving it by guess;
- retain enough context to reconstruct important history;
- do not store every event merely because it is available;
- do not use the delayed queries as a selection oracle.

Freeze `results/<agent>.memory.json` before evaluator access to gold artifacts.

## 5. Selection evaluation
Compare the set of source event IDs retained by the writer against the gold set of semantically relevant signal events.

Metrics:
- selection recall = relevant retained / relevant gold
- selection precision = relevant retained / all retained
- F1
- retention ratio = all retained / 1,200
- compression ratio = 1 - retention ratio
- false-retention count
- missed-relevant count

Because the writer is not told the gold signal set, this is the first experiment where importance selection itself is measured.

## 6. Memory evaluation
Evaluate generated memory against gold for:
- observation coverage
- invented record rate
- proposition recall/precision
- relationship semantic recall/precision
- temporal transition/state recall
- ambiguity preservation
- belief/conflict preservation
- action/outcome preservation
- scoped negative knowledge
- provenance completeness

Semantic equivalence is preferred over exact labels or record IDs.

## 7. Consumption
Run:
- RAW
- deterministic RAG
- V6-GENERATED
- V6-GENERATED+RAW

The reader must not see gold memory, expected answers, or the writer report.

V6-GENERATED receives only generated memory + delayed query set.
V6-GENERATED+RAW receives generated memory + linked raw evidence permitted by the protocol.

## 8. Cross-agent handoff
Run both directions:
- Claude writer → Copilot reader
- Copilot writer → Claude reader

Reader gets only the frozen generated memory, query set, and schema/design rules.

## 9. Anti-cheating rules
The writer must not inspect:
- `data/v6_memory.json`
- `results/`
- V7.1/V7.2 result files
- `v7.1_results.md`
- V7.2 result summaries
- gold annotations or expected answers

If the environment makes clean-room execution impossible, delegate the writer phase to a fresh subagent and disclose that fact.

## 10. Reporting discipline
Do not fabricate token counts, latency, or cost. Use null when unavailable.
Do not claim universal superiority of one memory mechanism.
Separate selection quality, representation quality, retrieval quality, and reader quality.
Document tooling/specification defects instead of silently changing prior benchmark artifacts.
