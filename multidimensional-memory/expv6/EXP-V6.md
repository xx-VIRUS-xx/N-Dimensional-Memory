# EXP-V6 — Cross-Agent Persistent Memory

## Question
Can observations produced independently by different models/agents be merged into one persistent memory state while preserving provenance, disagreement, uncertainty, and temporal history?

## Hypothesis
A model-agnostic memory layer should not require one model to be authoritative. If multiple agents observe the same underlying conversation, their observations can be attached to a shared proposition/event identity while retaining each agent's original observation and confidence.

## Core principle
`shared memory identity != shared interpretation`

The memory substrate owns persistence and provenance. Agents remain interpretation layers.

## Benchmark
Three agents independently report observations from the same conversational material:
- Claude: Rahul is the actor associated with playing football.
- Codex: Rahul is the actor associated with playing football; "He" is resolved to Rahul with high confidence.
- Copilot: Rahul is the actor associated with playing football; "He" is treated as an ambiguity candidate.

Expected:
- shared proposition identity for Rahul's football activity
- all agent observations preserved
- model-specific interpretations preserved
- disagreement about pronoun resolution remains visible rather than silently collapsed

A second benchmark introduces two agents with opposing location observations to test disagreement preservation.

## Success criteria
1. Shared observations merge under a stable proposition identity.
2. Provenance survives merging.
3. Agreement is distinguishable from interpretation disagreement.
4. Conflicting observations remain open unless explicit evidence resolves them.
5. No source observation is deleted.
