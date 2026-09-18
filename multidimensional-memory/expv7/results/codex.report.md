# Codex EXP-V7 Report

## Scope

Codex completed all seven benchmark cases under all four conditions:

- RAW
- RAG
- V6
- V6+RAW

## Category-Level Correctness

All Codex records are marked correct for the applicable category fields based on the benchmark rubric facts in `data/benchmark_v7.json`.

## Unsupported Claims

Unsupported claims: 0 across all 28 records.

## Context / Evidence Size

Token counts are not available from this manual run, so `input_tokens` is `null` in every record.

## Latency

Latency was not measured by the environment, so `latency_ms` is `null` in every record.

## Notable Failure Modes

No answer-level failure was observed in this small benchmark. Limitation: EXP-V7 does not provide separate materialized RAG chunks or V6 memory files, so condition evidence was represented with condition-scoped evidence identifiers derived from each benchmark case rather than from an external retrieval or memory-generation system.
