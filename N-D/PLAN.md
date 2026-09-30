# N-D plan

Each step has a go/no-go. Steps 0–2 need no engine code.

| Week | Experiment | Question | Gate |
|---|---|---|---|
| 0 | ND-0 ✅ | Does free-dimension extraction support the math? | Done: no; event-star adopted |
| 1 | ND-1 ✅ conditional | Engine v0: can code + math turn entity-dimension output into a geometry that answers probes and keeps the must-haves? (pilot 10) | M1 = 0; M3 ≥ 13/15; M4 = 7/7; M5 stable |
| 2 | ND-1b ❌ stage 1 | Frozen engine on external dialogue (Haiku × 3, Sonnet × 2): LoCoMo conv 0, sessions 1–3 (58 turns, 25 benchmark questions); ambiguity part deferred | M1 = 0; M2a ≥ 0.95; M3 ≥ 90% of RAW baseline; M5 (hubs excluded) ≥ 0.8 |
| 3 | ND-2 | Dimension geometry: footprints on the ~100-sentence corpus; propose collapse, inverse, broader, related | Precision ≥ 0.9 on hand-labelled dimension pairs |
| 4–5 | ND-3 | Depiction, facts held constant: flat facts vs N-D depiction, same LLM, 40–60 questions (change, sequence, history, conflict, ambiguity) | Depiction beats flat facts on change and conflict |
| 6 | ND-4 | Engine on Postgres: ledger + stages E1–E8 + depiction renderer | ND-3 results reproduce from the engine |
| 7–8 | ND-5 | TANGLE oracle track, then pipeline track | Oracle vs pipeline gap smaller than published memory systems' |

A failed gate stops the sequence until the cause is understood. Failures are reported in the experiment's results.
