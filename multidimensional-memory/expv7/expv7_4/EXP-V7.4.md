# EXP-V7.4 — Adversarial Autonomous Memory Formation

## 1. Objective

V7.3 showed perfect autonomous selection, but the synthetic corpus contained a near-perfect lexical tell: distractors shared one boilerplate phrase. V7.4 removes that shortcut.

The experiment asks whether a coding agent can decide what deserves persistent memory when durable and non-durable events overlap in vocabulary, topic, and apparent importance.

## 2. Corpus design

The corpus contains exactly 1,200 chronological events. The writer view must expose only:
- event_id
- timestamp
- speaker
- text
- ordinary topic metadata if present

The writer view MUST NOT expose:
- signal/distractor labels
- benchmark case IDs
- gold memory
- relevant event IDs
- delayed-query relevance hints
- expected answers
- prior experiment results

The hidden evaluator retains gold labels.

### Adversarial event families

The generator intentionally includes:
- discussion vs actual decision
- tentative proposal vs confirmed choice
- action vs mere intention
- successful vs failed outcome
- current state vs obsolete state
- repeated/paraphrased observations
- semantically similar distractors
- important events surrounded by topical noise
- delayed consequences of earlier decisions
- scoped negative knowledge
- unresolved ambiguity
- inference followed by confirmation

There must be no single substring or formatting feature that separates gold signal from distractor.

## 3. Writer task

The writer reads all 1,200 events before finalizing memory. It decides what deserves durable persistence.

It should preserve:
- durable decisions and rationale
- meaningful actions and outcomes
- evolving state histories
- uncertainty and ambiguity
- belief/inference/confirmation history
- conflicts and temporal evolution
- scoped negative knowledge
- provenance
- enough source evidence to reconstruct why a memory exists

It should avoid:
- routine chatter
- repeated copies of the same fact
- unresolved discussion presented as decision
- obsolete state presented as current
- unsupported inference
- unrelated topical mentions

Every retained record must cite real source event IDs.

## 4. Evaluation

### Selection
- precision
- recall
- F1
- retention ratio
- compression ratio
- false-retained events
- missed relevant events

### Memory representation
- observation coverage
- invented event rate
- proposition precision/recall
- relationship semantic precision/recall
- temporal transition/state coverage
- ambiguity preservation
- belief/conflict preservation
- action/outcome preservation
- negative knowledge scope/completeness
- provenance completeness
- duplicate/compression quality

### Consumption
Conditions:
- RAW
- deterministic RAG
- V6-GENERATED
- V6-GENERATED+RAW

Generated-memory arms must use only the frozen writer memory, except +RAW which may use explicitly linked source events.

### Cross-agent
Run both directions:
- Claude memory → Copilot reader
- Copilot memory → Claude reader

Reader gets generated memory + delayed queries + schema/design rules only.

## 5. Scientific rules

Do not fabricate token counts, latency, retrieval scores, or missing runs.
Do not modify prior V7.3 files to hide defects.
Do not use gold or query knowledge during writer formation.
If clean-room execution is impossible, delegate to a fresh subagent and disclose it.

## 6. Success interpretation

V7.4 is informative if agents retain high-value events despite semantic distractors, preserve the relational/temporal memory semantics, and remain interoperable across models.

A failure is also useful: selection errors will reveal which kinds of importance judgment remain difficult.
