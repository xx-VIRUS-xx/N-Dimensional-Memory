# N-D — N-Dimensional Memory, fresh track

> **Closed 2026-10-09 as a negative result on a 509-turn conversation.** Read `CLOSEOUT.md` first, then `STATUS.md`.

N-D restarts NDM from first principles. Earlier experiments (EXP-V1 … EXP-V8) are not carried forward as results or assumptions. Their *setup* (harnesses, adapters, retrieval baselines, competitor Docker files) may be reused when an N-D experiment needs it, and every reuse is named in that experiment's spec.

## Thesis

An LLM is a capable reasoner but cannot retain everything or check itself against what it was told. N-D is an external memory that stores every event exactly, tracks change over time, and depicts that history to the LLM so it can reconstruct context.

## Division of labour

The LLM supplies only entities and dimensions per event. The engine (code and math) builds everything else: ticks, peg identity, value linking, epistemic status, buckets, collisions, trajectories, depiction.

## Model in one paragraph

Entities, dimensions and values are fixed pegs. Each event is a star of role strings pinned to its own tick. Relationships are never stored: they come from **collisions** (events sharing a peg) and **trajectories** (a peg's events in order). Relations a source explicitly states (A happened *because* of B) are events themselves. Every event has one epistemic status with an owner: fact, claim, speaker belief, model belief, open question, or intent. Unresolved references are ambiguity buckets, closed only by an explicit statement or the user.

## Layout

```
CONTRACT.md                 invariants every N-D experiment must preserve
PLAN.md                     experiment sequence and week-by-week schedule
schema/event.schema.json    the event-star wire format (v0)
catalog/dimensions_v0.json  starter dimension and kind catalog
tools/ndm_math.py           incidence math and metrics (both formats)
ND-0/                       baseline: free-dimension extraction, measured
ND-1/                       engine v0: code + math, judged by probes, must-haves and stability
```

## Rules for every experiment

1. A spec (`EXP-NDx.md`) is written and frozen before any run: question, data, protocol, metrics, success and falsification criteria.
2. Results are reported against the frozen spec, including failures.
3. LLM output is never scored against a handwritten structure. It is judged by contract rules, faithfulness to the source, probe questions, must-have checks and stability across models. Probes are written before runs and never shown to the extractor.
4. Anything reused from V1–V8 is listed with its path and what was changed.
