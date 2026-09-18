# EXP-V7 Agent Handoff

## Purpose
You are participating as an evaluator/consumer of a persistent memory system. Do **not** redesign V6, invent missing memory, or optimize the benchmark for yourself.

Your task is to run the same benchmark under controlled memory conditions and produce reproducible results.

## Rule 0 — independence
Do not read another agent's output before completing your own run.
Do not modify the benchmark cases or expected-answer rubric.
Do not use hidden knowledge from previous runs.

## Step 1 — inspect the workspace
Run:
```bash
find . -maxdepth 3 -type f | sort
pytest -q
```
Read:
- `README.md`
- `EXP-V7.md`
- `data/benchmark_v7.json`
- `schemas/agent_result.schema.json`

## Step 2 — understand the four conditions
You will run each benchmark case under:
- `RAW`
- `RAG`
- `V6`
- `V6+RAW`

Do not change the underlying conversation between conditions.

## Step 3 — execute the agent task
For each case:
1. Load only the evidence specified by the condition.
2. Read the delayed query.
3. Answer it.
4. State uncertainty where evidence is insufficient.
5. Preserve conflicting observations when present.
6. Use provenance identifiers when supplied.

Do not answer from general world knowledge when the benchmark asks about conversation history.

## Step 4 — record the result
Create one JSON record per case using:
`schemas/agent_result.schema.json`

Required fields include:
- agent_id
- condition
- case_id
- query_category
- answer
- correctness fields
- unsupported_claims
- evidence_used
- input_tokens when measurable
- latency_ms when measurable

If a measurement is unavailable, use `null`. Never invent a measurement.

## Step 5 — same-agent pass
Complete all cases for your assigned agent before comparing with anyone else.

## Step 6 — cross-agent pass
A separate agent may act as the memory writer. You act only as the reader.
You receive the V6 memory produced by the writer plus the delayed query.
Do not request the original transcript unless the condition explicitly permits V6+RAW.

## Step 7 — special behaviors to test
### Ambiguity
If the memory says a reference is unresolved, do not choose an interpretation merely because one sounds plausible.

### Conflict
If two overlapping observations disagree, preserve the disagreement and provenance.

### Temporal evolution
If observations are non-overlapping in time, reconstruct the state sequence rather than calling it a contradiction.

### Negative knowledge
Only claim "never discussed" when the supplied benchmark evidence is complete enough to support that statement.

### Provenance
Distinguish an agent observation from a derived/confirmed state.

## Step 8 — final report
Produce:
`results/<agent_id>.<condition>.json`

Then produce a short markdown report containing:
- number of cases
- category-level correctness
- unsupported claims
- context/evidence size
- latency
- notable failure modes

Do not rank agents.

## What success means
The experiment succeeds if it can compare conditions reproducibly and determine whether V6 memory preserves useful long-horizon information for downstream agents.

It is acceptable for V6 to fail. A clean failure is more valuable than a benchmark quietly massaged into a victory.
