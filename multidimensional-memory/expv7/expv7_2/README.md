# EXP-V7.2 — Memory Construction and Cross-Agent Persistence

V7.2 attacks the remaining methodological gap from V7.1: can an agent **construct** the proposed persistent relational memory from a long conversation, rather than merely consume a benchmark-generated memory?

## Core question

Given the same 1,200-event conversation corpus, can Claude and Copilot independently transform raw conversation into a canonical persistent memory representation that preserves:

- facts and propositions
- semantic relationships
- action → outcome chains
- temporal state and state transitions
- ambiguity
- overlapping conflict
- belief evolution
- negative knowledge / scoped non-discussion
- provenance and source/agent roles

Then, can another model consume that memory without access to the original conversation and answer delayed queries correctly?

## Experimental arms

### A. Writer / extraction quality
Each agent independently builds V6 memory from the complete conversation.

Compare the generated memory against the deterministic gold annotations.

Measure:
- observation coverage
- proposition precision/recall
- relationship precision/recall
- temporal-state accuracy
- ambiguity preservation
- conflict preservation
- negative-knowledge correctness
- provenance preservation
- unsupported/invented memory records

### B. Same-agent consumption
Writer creates memory → same agent receives only generated memory → delayed queries.

### C. Cross-agent consumption
Claude writes → Copilot reads only Claude's memory.
Copilot writes → Claude reads only Copilot's memory.

This is the model-agnostic persistence test.

### D. Reconstruction / round-trip
Writer memory → reader answers → compare against gold.
Also compare the writer artifact itself against gold, so a correct answer cannot hide a bad memory representation.

## Conditions

- `RAW`: full relevant raw evidence, for upper-bound comparison only.
- `RAG`: deterministic retrieval baseline from V7.1.
- `V6-GENERATED`: agent-generated memory only.
- `V6-GENERATED+RAW`: generated memory plus linked raw evidence.

The primary new comparison is `V6-GENERATED` against the gold V6 representation and against the V7.1 deterministic-memory condition.

## Critical anti-cheating rule

The agents must not read the gold V6 memory, benchmark expected answers, or another agent's results while constructing memory. Gold artifacts are evaluation-only.

## Important interpretation

V7.2 does **not** assume the agent's extracted memory is correct. It explicitly measures extraction quality before testing downstream usefulness.
