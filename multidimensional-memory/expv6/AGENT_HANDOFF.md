# EXP-V6 Agent Handoff

## Purpose

This document is the step-by-step protocol for running EXP-V6 with independent coding agents such as Codex, Claude Code, and GitHub Copilot.

The goal is **not** to ask agents to design the memory system. The goal is to test whether independent agents can observe the same conversational evidence and produce observations that can be persisted into one model-agnostic memory state.

> Important: the agents are observers/interpreters. The persistent memory layer owns identity, provenance, history, and state reconstruction.

---

## 1. What V6 is testing

### Research question

Can observations produced independently by different models/agents be merged into one persistent memory state while preserving:

- provenance
- disagreement
- uncertainty
- temporal history
- append-only observations

### Core principle

`shared memory identity != shared interpretation`

Do not force different agents to agree. Agreement is itself an observation.

---

## 2. What each agent must NOT do

Each agent must **not**:

- build the graph
- invent relationships
- assign final truth
- overwrite another agent's observation
- resolve ambiguity merely because another agent resolved it
- use another agent's output as evidence
- modify the benchmark to make its answer fit
- collapse distinct observations into one fact

The agent's job is deliberately smaller: inspect the supplied conversation and report structured observations.

---

## 3. Environment

Use the same benchmark material for every agent.

Recommended agents:

1. Codex
2. Claude Code
3. GitHub Copilot

Each agent should receive the **same input text** and the **same extraction instructions**.

Do not show an agent another agent's output before its own observation is produced.

---

## 4. Step 1 — Give the agent the benchmark

Use the benchmark files in:

```text
data/
  benchmark_v6.json
  benchmark_v6_1.json
```

The benchmark contains the conversational material and expected test scenario.

If your agent cannot directly read the JSON, paste only the relevant conversation content into its task. Keep the wording identical across agents.

---

## 5. Step 2 — Give the agent this extraction prompt

Copy this prompt exactly for every agent:

```text
You are an independent semantic observer in a research experiment.

Analyze ONLY the supplied conversation.

Your task is to extract observations, not to build a knowledge graph and not to decide final truth.

For each meaningful proposition/event, report:

1. proposition_id_candidate
2. subject/entity
3. predicate/action/state
4. object/value, if present
5. temporal information, if present
6. epistemic status: unknown | inferred | confirmed | disputed | rejected
7. ambiguity, if any
8. confidence
9. evidence: quote or concise reference to the source statement

Rules:
- Preserve ambiguity when the conversation does not resolve it.
- Do not invent facts.
- Do not infer temporal order unless the language provides it.
- Distinguish an observation from your interpretation.
- Do not use any other agent's output.
- Do not overwrite or collapse competing observations.
- If two statements appear contradictory, report both observations and mark the relevant proposition as disputed rather than choosing one.
- If a pronoun such as "he" or "they" is ambiguous, preserve the ambiguity.
- Use stable, human-readable proposition IDs where possible.

Return JSON only.
```

---

## 6. Step 3 — Run the same task independently

Run the prompt separately in:

```text
Codex
Claude Code
Copilot
```

Do not let one agent inspect another agent's output first.

Save the raw outputs separately:

```text
results/
  agent_codex.json
  agent_claude.json
  agent_copilot.json
```

The filenames are examples. Keep the agent identity explicit.

---

## 7. Step 4 — Compare observations

Before inserting anything into persistent memory, compare the three outputs.

Look for:

### A. Stable semantic points

Do different agents identify the same underlying entity/action/value even when wording differs?

Example:

```text
Codex: Rahul plays football
Claude: Rahul is associated with playing football
Copilot: Rahul -> play -> football
```

These may refer to the same underlying proposition.

### B. Different granularity

Do not treat different granularity as automatic contradiction.

Example:

```text
Agent A: play
Agent B: play football
```

These may be related while remaining distinct observations.

### C. Interpretation disagreement

Example:

```text
Agent A: "He" = Rahul
Agent B: "He" = unresolved
```

Preserve both interpretations.

### D. Actual contradiction

Example:

```text
Agent A: location = Jaipur
Agent B: location = Delhi
```

Do not select a winner. Persist both observations and let temporal/evidentiary rules determine whether this is evolution, conflict, or unresolved disagreement.

---

## 8. Step 5 — Insert observations into V6

Use the V6 implementation as the persistence/state layer.

Important separation:

```text
Agent
  ↓
Observation
  ↓
Persistent memory
  ↓
Derived state
```

The agent produces observations.

V6 stores observations.

V6 derives state from observations.

The agent does not directly mutate the historical state.

---

## 9. Step 6 — Test insertion-order independence

Take the same observations and apply them in different orders.

Example:

```text
Run A:
Codex → Claude → Copilot

Run B:
Copilot → Codex → Claude

Run C:
Claude → Copilot → Codex
```

Expected result:

```text
same observation set
        ↓
 same derived state
```

The order of agent execution must not determine the resulting memory state.

---

## 10. Step 7 — Test provenance

For every stored observation verify that you can answer:

- Which agent produced it?
- What did that agent observe?
- When was it observed?
- What evidence supported it?
- What epistemic status did it have?

A merged proposition must not erase the individual observations.

---

## 11. Step 8 — Test disagreement preservation

Use the location-disagreement benchmark.

Example conceptual input:

```text
Observation A:
location = Jaipur
valid through May 2026

Observation B:
location = Delhi
valid from June 2026
```

Expected:

```text
Jaipur observation → preserved
Delhi observation  → preserved
Temporal relation  → evolution
```

If two different values overlap in time:

```text
Jaipur: valid 2026-06-01 → 2026-12-01
Delhi:  valid 2026-08-01 → 2026-10-01
```

Expected classification:

```text
potential conflict
```

Do not delete either observation.

---

## 12. Step 9 — Run the automated tests

From the repository root:

```bash
pytest -q
```

The V6 suite should pass the existing V6, V6.1, and V6.2 tests.

The latest V6.2 benchmark currently has:

```text
12 passed
```

This verifies the implementation's existing invariants. It is not evidence that an LLM agent performs better with V6 memory.

---

## 13. Step 10 — Record experimental results

Create an experiment record containing at least:

```text
agent_name
model/version if known
benchmark_id
raw_output_path
number_of_observations
shared_propositions
interpretation_disagreements
ambiguities_preserved
conflicts_preserved
provenance_preserved
insertion_order_test
snapshot_restore_test
notes
```

Do not report a model as "better" merely because it generated more observations.

The research question is whether the underlying semantic substrate remains usable across agents.

---

## 14. What counts as a successful V6 result

V6 succeeds if:

1. Independent agents can produce observations from the same evidence.
2. Shared proposition identity can be established without erasing agent-specific interpretation.
3. Provenance survives persistence.
4. Ambiguity survives persistence.
5. Conflicting observations survive persistence.
6. Temporal evolution is distinguishable from overlapping conflict.
7. State reconstruction is deterministic.
8. Agent insertion order does not change the derived state.
9. Snapshot and restore reproduce the same state.

---

## 15. What V6 does NOT prove

Do not overclaim.

V6 does **not** prove that:

- agents answer questions better using this memory
- the representation beats vector/RAG
- the representation reduces token usage
- the representation reduces latency
- the memory improves long-horizon coding performance
- the representation is superior to existing temporal knowledge graphs

Those require the next experiment.

---

## 16. Final V6 architecture

```text
                    ┌─────────────────┐
                    │ Conversation    │
                    └────────┬────────┘
                             │
             ┌───────────────┼───────────────┐
             ▼               ▼               ▼
          Codex           Claude          Copilot
             │               │               │
             └───────────────┼───────────────┘
                             ▼
                    Agent Observations
                             │
                             ▼
                 ┌──────────────────────┐
                 │ Append-only Memory   │
                 │                      │
                 │ Proposition IDs     │
                 │ Observations        │
                 │ Provenance          │
                 │ Epistemic status    │
                 │ Temporal intervals  │
                 └──────────┬───────────┘
                            ▼
                 Deterministic State
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
          Evolution      Conflict       Current
                                      derived state
```

---

## 17. Handoff to EXP-V7

Once V6 is reproduced, stop modifying the memory semantics just to improve an agent's score.

The next experiment should put the memory in front of an agent and measure downstream utility.

### EXP-V7 — Agent Utility Benchmark

Compare:

```text
Raw conversation
       vs
Vector/RAG
       vs
V6 relational memory
       vs
V6 + raw evidence
```

Use the same delayed questions and the same agent where possible.

Measure:

- historical recall
- decision continuity
- action/outcome recall
- temporal consistency
- ambiguity handling
- negative knowledge
- context tokens
- retrieval latency
- answer latency
- cost

V7 is where the system stops being merely an elegant memory data structure and starts having to justify its existence. Humanity has suffered enough from architectures that were "interesting" but useless.
