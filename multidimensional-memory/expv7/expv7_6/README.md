# EXP-V7.6 — Realistic Conversational Memory Benchmark

V7.6 is the next phase after V7.5. The goal is to test whether the model-independent persistent memory thesis survives more realistic, messy conversational data and stronger retrieval baselines.

## Core question

Can an external structured memory layer preserve long-horizon conversational state more reliably and efficiently than raw-context replay and realistic retrieval systems, while remaining usable across different LLM agents?

## Critical change from V7.5

V7.5 used synthetic/template-generated long conversations. V7.6 should prioritize realistic conversational structure, richer retrieval baselines, autonomous memory construction, and instrumentation.

Do not treat V7.6 as proof of superiority in advance. The experiment is designed to falsify the thesis.

## Conditions

1. RAW — full eligible conversation context.
2. RAG — actual indexed chunks + semantic/hybrid retrieval + reranking where available.
3. MEMORY — agent-generated structured memory only.
4. MEMORY+RAW — structured memory plus bounded raw evidence.
5. Optional ORACLE-MEMORY — gold memory only for diagnostic separation of construction vs consumption quality.

All conditions must use the same future queries and the same reader model per comparison.

## Required instrumentation

Record, where available:
- source context tokens
- retrieved raw tokens
- memory tokens / bytes
- memory construction time
- retrieval time
- answer time
- model/API cost
- number of retained observations
- proposition count
- relationship count
- temporal-state count
- ambiguity/conflict counts
- unsupported claims
- answer correctness
- provenance correctness

If a platform does not expose a metric, record `null`. Never estimate it silently.

## Agent separation

Writer and reader roles must be separated. A writer must not see gold answers, gold memory, or another agent's results before freezing its memory. Cross-agent handoff happens only after both independent writer runs have completed.

## Reproducibility

Freeze:
- corpus hash
- benchmark/query hash
- memory artifact hash
- retrieval configuration
- model name/version when exposed
- prompt version
- timestamp

Every reported result must identify the exact artifact/configuration used.


## Corpus status
The V7.6 corpus is now included at `data/conversation_v7_6.jsonl`. Evaluation-only future queries and gold annotations are under `evaluation/` and must remain hidden from the clean-room writer until memory freeze.
