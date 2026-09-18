# EXP-V7.4 Agent Handoff

Read `README.md`, `EXP-V7.4.md`, and `RUN_PROMPT.md`. This file is authoritative only as a concise execution handoff and must not override those documents.

## Objective
Test autonomous importance selection under semantic/lexical adversarial noise.

## Writer input
`data/conversation_v7_4_unlabeled.jsonl` only.

## Hidden evaluator
`data/benchmark_v7_4.json` and `data/v6_memory.json` are forbidden until the writer artifact is frozen.

## Required output
Each agent produces a frozen memory, memory evaluation, four consumption files, report, and both cross-agent handoff statuses/results.

Never fabricate the other model's run.
