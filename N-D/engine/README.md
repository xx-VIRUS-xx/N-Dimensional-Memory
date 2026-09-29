# N-D engine v0

Deterministic stages E1–E6 over the LLM's entity-dimension output. No LLM calls.

| File | Purpose |
|---|---|
| `nd_engine.py` | E1 ticks, E2 peg identity (merge exact, propose near), E3 value linking, E4 cleaning, E5 epistemic tagging, E6 buckets (local + global backward/forward). All rules are in tables at the top of the file. |
| `checks.py` | ND-1 metrics that need no LLM: M1 contract, M2 faithfulness, M4 must-haves, diagnostics |
| `run_batch.py` | Run 2: engine + checks on every extraction in a folder, M5 stability summary |
| `probe_harness.py` | M3: renders engine state (the only context the answering model sees), builds prompts, scores answers |

v0 limits: one event per input record (no sentence splitting); lexical rule tables; entity `type` unused until extractions include it.
