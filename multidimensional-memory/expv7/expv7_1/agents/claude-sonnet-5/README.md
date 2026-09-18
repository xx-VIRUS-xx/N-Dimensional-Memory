# Claude Code (Sonnet 5) — EXP-V7.1 run

Result agent_id used in `results/`: `claude` (per AGENT_HANDOFF.md's required filenames/identity).

This folder holds this agent's working artifacts for the independent same-agent run:

- `conditions/RAW.json` — the exact raw events supplied per case (from `case.raw_event_ids`).
- `conditions/RAG.json` — the exact materialized retrieval output per case, copied verbatim from `data/rag_retrievals_v71.json` (chunk IDs, scores, event_ids, text).
- `conditions/V6.json` — the exact V6 memory records selected per case (grouped by `case_id`, copied verbatim from `data/v6_memory.json`).
- `conditions/V6+RAW.json` — V6 records plus only the raw events linked via each record's `basis`/`event_id`/`source_event`/chain fields; verified this always equals the benchmark's `gold.required` list per case.
- `answers.md` — natural-language answers per case × condition.

The machine-readable required outputs were written to `../../results/claude.{RAW,RAG,V6,V6+RAW}.json` and `../../results/claude.report.md`, per the handoff's required output location (not inside this folder), since the handoff specifies exact filenames under `results/`.

## Rule/independence compliance
- `results/` and `agents/` were confirmed empty before this run started (no Copilot output existed yet).
- Setup commands (`generate_v71.py`, `build_rag.py`, `build_v6_memory.py`, `pytest -q`) were run first, per Step 1.
- RAG condition used only the actual materialized retrieval log (`data/rag_retrievals_v71.json`) — no manual addition of missing chunks. The V71-TIME-01 retrieval gap (missing E0887/E1190) is reported as-is; the RAG answer for that case explicitly states the evidence is insufficient rather than fabricating or backfilling the missing state transitions.
- V6 condition used only the supplied memory records; raw conversation text was not consulted while producing the V6-only answers (verified by working from `conditions/V6.json` alone when drafting those answers).
- No token/latency measurements were fabricated; all `input_tokens`/`latency_ms` fields are `null`.
- Cross-agent handoff (Step 5 / AGENT_HANDOFF.md Handoff A/B) was not performed in this pass — it requires Copilot's independent participation and is explicitly a separate step after both agents complete their own four-condition runs.
