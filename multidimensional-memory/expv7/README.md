# EXP-V7 — Agent Utility Benchmark

V7 tests whether the persistent relational memory established in V6 improves long-horizon agent continuity.

## Core question
Does an agent perform better on delayed, history-dependent tasks when it consumes V6 memory instead of only raw conversation or similarity-based retrieval?

## Important separation
V7 does not ask agents to design the memory. Agents are the consumers/evaluators. The memory representation and scoring harness remain fixed.

## Conditions
1. RAW — relevant raw conversation/context supplied directly.
2. RAG — retrieved text chunks from the same conversation.
3. V6 — structured persistent relational memory only.
4. V6+RAW — V6 memory plus linked raw evidence.

Use the same agent, same benchmark case, same question, and equivalent evidence budget across conditions where practical.

## Agents
Run the same benchmark independently with:
- Codex
- Claude Code
- GitHub Copilot

The first pass should be single-agent. The second pass is cross-agent: one agent writes memory, another consumes it.

## What V7 measures
- historical recall
- decision continuity
- action/outcome recall
- temporal state reconstruction
- ambiguity handling
- contradiction handling
- negative knowledge
- provenance/evidence use
- answer correctness
- context tokens supplied
- retrieval latency
- answer latency

## Run the deterministic harness
```bash
pytest -q
python -m src.validate_results
```

Agent runs are intentionally manual/provider-neutral. Do not fabricate agent results in the repository.
