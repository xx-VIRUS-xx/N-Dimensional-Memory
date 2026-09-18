# Evaluator-only materials

`benchmark_v7_7_gold_repaired.json` is evaluator-only. Do not expose it to writer or reader agents before their relevant phase is frozen. The repaired benchmark validates that every required evidence ID exists, is durable, belongs to the query conversation, and is not generic filler.
