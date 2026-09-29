# ND-1 run 2: stateless extractions

Fill `extractions/` with `tools/extract_stateless.py` (2–3 models × 3 runs; `--provider claude-cli` uses Claude Code instead of an API key), then run `python engine/run_batch.py ND-1/results/run2`. The runner writes `per_run/` and `summary.json`; the report goes in `REPORT.md`.

`--provider replay` reproduces the ND-0 BabyTest extraction and is a smoke test only. Do not count it as a run 2 result.

Each extraction has a `.meta.json` sidecar (provider, model, times, temperature, isolation, CLI version). Commit it with the results.
