# Claude Code (Sonnet 5) — EXP-V7 run

agent_id: `claude-sonnet-5`

This folder contains this agent's independent run artifacts per `AGENT_HANDOFF.md`:

- `v6_memory.json` — V6-style structured memory built from each benchmark case's conversation, following the EXP-V6 principles (proposition identity, provenance, append-only observations, disagreement preserved). No pre-existing V6 memory file was found in the repo at run time, so this agent constructed it directly from `data/benchmark_v7.json` conversations, per case, before running any condition. This construction step itself was done once, prior to answering any delayed query, and was not adjusted afterward.
- `conditions/` — the exact evidence supplied to the agent under each condition, per case.
- `answers.md` — the natural-language answers per case/condition.
- Result records were written to `../../results/claude-sonnet-5.<condition>.json` per the handoff's required output location.

## Rule 0 compliance
This run was completed without reading any other agent's output directory (`agents/codex` was empty at the time of this run). The benchmark cases and rubric in `data/benchmark_v7.json` and `schemas/agent_result.schema.json` were not modified.

## Notes on token/latency fields
This is a manual, non-API run inside an interactive coding session — there is no token-metering or wall-clock latency instrumentation available for the "answer" step itself. Per the handoff ("If a measurement is unavailable, use `null`. Never invent a measurement."), `input_tokens` and `latency_ms` are reported as `null` throughout rather than estimated.
