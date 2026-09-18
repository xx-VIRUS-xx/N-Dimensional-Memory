# Copilot EXP-V7 Conditions

Independent run based only on `data/benchmark_v7.json`, `EXP-V7.md`, and the schema.

Each case was answered under all four fixed conditions without changing the delayed query:

- `RAW`: the case conversation supplied directly.
- `RAG`: one retrieved chunk containing the case conversation; no unrelated case was supplied.
- `V6`: only the corresponding structured observations in `v6_memory.json`, including provenance and status.
- `V6+RAW`: the corresponding structured observations plus the case conversation as linked verification evidence.

No token or latency measurement was available for this manual provider-neutral run, so those fields are `null` in every result. No other agent output was consulted.
