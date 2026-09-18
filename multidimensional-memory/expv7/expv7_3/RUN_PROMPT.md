# EXP-V7.3 Agent Run Prompt

You are participating in EXP-V7.3 — Autonomous Memory Formation.

Execute the complete protocol in `expv7_3`.

## Agents
Use Claude and Copilot only. Codex is excluded from this round.

## Critical change from V7.2
This is a clean-room memory-formation test. The writer must receive the full 1,200-event chronological corpus but MUST NOT receive signal/distractor labels, benchmark case IDs, relevant-event IDs, delayed-query relevance hints, gold memory, expected answers, or prior V7.1/V7.2 results.

The writer must autonomously decide what is worth persistent memory.

## Phase 1 — Writer
1. Read `EXP-V7.3.md` and the workspace memory design rules.
2. Read the full unlabeled conversation corpus.
3. Construct your own persistent memory.
4. Preserve durable events, decisions, actions/outcomes, temporal state, ambiguity, belief evolution, scoped negative knowledge, and provenance when supported.
5. Preserve source event IDs for retained observations.
6. Do not invent source events or resolve ambiguity by guessing.
7. Do not inspect `data/v6_memory.json`, any `results/` artifact, V7.1/V7.2 result files, or expected answers.
8. Freeze `results/<your-agent>.memory.json`.

If your current session has previously seen the gold memory or prior results, delegate Phase 1 to a fresh clean-room subagent and disclose that in the report.

## Phase 2 — Memory evaluation
Only after the writer artifact is frozen, compare it to the gold memory/annotations.
Produce:
`results/<your-agent>.memory_eval.json`

Measure selection precision/recall/F1, retention/compression, observation precision/recall, relation/state/proposition quality, ambiguity, belief/conflict, negative knowledge, provenance, and invented-record rate.

## Phase 3 — Consumption
Run all four conditions:
- `RAW`
- `RAG`
- `V6-GENERATED`
- `V6-GENERATED+RAW`

Produce:
`results/<agent>.RAW.json`
`results/<agent>.RAG.json`
`results/<agent>.V6-GENERATED.json`
`results/<agent>.V6-GENERATED+RAW.json`

Use actual deterministic retrieval for RAG. Do not manually add chunks or fall back to the full corpus.
V6-GENERATED must use only the frozen generated memory, not the raw conversation.
Do not fabricate token or latency measurements.

## Phase 4 — Cross-agent handoff
After both writer artifacts are frozen, perform:
- Claude memory → Copilot reader
- Copilot memory → Claude reader

Reader receives generated memory + delayed queries + schema/design rules only. No original conversation, gold memory, expected answers, or writer report.

Produce:
`results/claude_to_copilot.json`
`results/copilot_to_claude.json`

## Phase 5 — Report
Produce `results/<your-agent>.report.md` containing:
- execution provenance
- writer methodology
- selection metrics
- memory metrics
- consumption metrics
- cross-agent result
- failures and retrieval gaps
- tooling/specification defects
- limitations

Do not silently patch prior V7.1/V7.2 artifacts. If a validator is version-specific, create/use a V7.3 validator or schema and disclose the difference.

## Final validation
Run the available tests and the correct V7.3 validator. Ensure all required artifacts exist and are internally consistent.
