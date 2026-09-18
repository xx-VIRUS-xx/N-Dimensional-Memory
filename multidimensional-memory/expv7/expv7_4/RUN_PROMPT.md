# EXP-V7.4 Agent Run Prompt

You are participating in EXP-V7.4. Execute the full protocol in `expv7_4` independently.

Agents allowed: Claude and Copilot. Codex is excluded.

## Phase 0 — read rules

Read `README.md` and `EXP-V7.4.md` first.

## Phase 1 — clean-room writer

Use ONLY the unlabeled writer corpus `data/conversation_v7_4_unlabeled.jsonl` plus the V7.4 design rules.

You must NOT read:
- `data/benchmark_v7_4.json`
- `data/v6_memory.json`
- any `results/`
- prior V7.0/V7.1/V7.2/V7.3 results
- any file exposing signal/distractor labels
- delayed queries before memory is frozen

Read the entire 1,200-event corpus. Autonomously decide what deserves durable memory. Do not rely on a lexical blacklist or whitelist. In particular, do not classify events by a repeated phrase or metadata shortcut.

Freeze:
`results/<your-agent>.memory.json`

## Phase 2 — memory evaluation

Only after the writer artifact is frozen may you inspect hidden gold/evaluator files.
Produce:
`results/<your-agent>.memory_eval.json`

Report selection precision/recall/F1, retention/compression, false retention, missed relevant events, representation metrics, and invented-record rate.

## Phase 3 — consumption

Run all four conditions for all delayed queries:
- RAW
- RAG
- V6-GENERATED
- V6-GENERATED+RAW

RAG must use actual deterministic retrieval over the corpus. Do not manually select chunks or fall back to the full corpus.

V6-GENERATED must use only your frozen generated memory.

V6-GENERATED+RAW may additionally use only source events explicitly linked by generated memory.

Write:
- `results/<agent>.RAW.json`
- `results/<agent>.RAG.json`
- `results/<agent>.V6-GENERATED.json`
- `results/<agent>.V6-GENERATED+RAW.json`

## Phase 4 — cross-agent

Execute both genuine directions:
- Claude memory → Copilot reader
- Copilot memory → Claude reader

Reader receives only the other agent's frozen memory, delayed queries, and schema/design rules. No original conversation, gold memory, gold answers, or writer report.

Write:
- `results/claude_to_copilot.json`
- `results/copilot_to_claude.json`

If the other agent artifact is unavailable, write `not_executed`; never impersonate another model.

## Phase 5 — report

Write `results/<agent>.report.md`.
Separate:
1. selection quality
2. memory construction quality
3. consumption quality
4. cross-agent quality
5. retrieval failures
6. tooling/specification defects
7. limitations

Do not fabricate token counts or latency. Preserve every discovered defect explicitly.
