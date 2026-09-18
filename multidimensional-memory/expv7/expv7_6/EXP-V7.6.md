# EXP-V7.6 — Realistic Conversational Memory Benchmark

## 1. Research objective

V7.6 moves the project from progressively elaborate synthetic benchmarks toward realistic long-running conversations.

The hypothesis under test is:

> A model-independent persistent memory substrate can preserve useful long-horizon conversational state, including history, decisions, actions/outcomes, temporal evolution, ambiguity, conflict, negative knowledge, and provenance, while allowing different LLMs to consume the same memory.

The experiment must be capable of disproving this hypothesis.

---

## 2. Questions

### Q1 — Memory construction
Can an agent identify durable information in realistic conversations without being given gold relevance labels?

### Q2 — Representation
Does structured memory preserve information that matters for future queries better than compressed text summaries?

### Q3 — Retrieval
Does structured memory remain useful when compared against a stronger retrieval stack than V7.5's deterministic lexical top-k baseline?

### Q4 — Long-horizon continuity
Can the system reconstruct decisions, state transitions, failed attempts, revisions, and outcomes after substantial conversational distance?

### Q5 — Uncertainty
Can it correctly say that something is unknown, ambiguous, disputed, or never discussed rather than inventing an answer?

### Q6 — Cross-agent persistence
Can memory written by one model be consumed by a different model without the original conversation?

### Q7 — Efficiency
Does the memory representation reduce the amount of context required to answer correctly?

---

## 3. Data design

Prefer realistic conversational traces rather than templated event streams.

Candidate sources:
- real user-agent conversations with permission and sensitive information removed
- public conversational datasets with suitable licenses
- realistic manually authored conversations designed to contain natural messiness
- long coding/debugging sessions
- project planning threads
- research discussions
- multi-session assistant interactions

Do not include private user data without appropriate authorization.

### Required properties

Conversations should contain natural examples of:
- corrections
- changing requirements
- decisions followed by reversals
- partial completion
- failed approaches
- successful outcomes
- references such as "that", "the earlier approach", "it"
- delayed dependencies
- uncertainty
- contradictory statements
- information that is deliberately absent
- irrelevant side discussions
- repeated topics with changed context
- multiple participants where possible

### Long-horizon structure

Target several sessions per conversation/project rather than one monolithic prompt.

Suggested initial scale:
- 20–50 conversations
- 5–20 sessions per conversation
- enough text to create meaningful retrieval dilution
- 100+ future queries across the benchmark

Do not force these numbers if the available realistic data is smaller. Report the actual scale.

---

## 4. Query categories

At minimum:

1. Historical recall
2. Decision continuity
3. Action → outcome
4. Temporal state
5. Revision / supersession
6. Ambiguity
7. Conflict / competing beliefs
8. Negative knowledge
9. Provenance
10. Multi-hop relationship
11. Cross-session reference
12. Compositional query requiring multiple memories

Queries must be written after the relevant conversation has been frozen. The writer must not see the future query set.

---

## 5. Memory representation

The memory schema should support:

```text
Observation
  source_event_id(s)
  agent/model
  timestamp
  content
  provenance

Proposition
  stable_id
  semantic content
  status
  confidence

Relationship
  source
  relation
  target
  evidence
  confidence

Temporal state
  proposition
  valid_from
  valid_until
  transition

Belief state
  unknown
  inferred
  confirmed
  disputed
  rejected

Ambiguity
  unresolved references/questions

Negative knowledge
  proposition
  scope
  evidence completeness

Outcome
  action
  result
  timestamp
```

Observations are append-only. Derived state may be recomputed from observations.

---

## 6. Retrieval baselines

V7.5's lexical top-six baseline is insufficient as the only comparison.

V7.6 should implement or use at least:

### Baseline A — RAW
Full eligible context, subject to the model's context limit.

### Baseline B — lexical RAG
BM25 or equivalent.

### Baseline C — semantic RAG
Embedding retrieval with fixed top-k.

### Baseline D — hybrid RAG
Lexical + semantic retrieval, followed by a deterministic or documented reranker.

### Baseline E — structured memory
V7-style memory representation.

### Baseline F — structured memory + bounded evidence
Memory plus only the raw evidence needed to ground the answer.

Keep implementations deterministic where possible and freeze configuration before evaluation.

---

## 7. Writer protocol

For each conversation:

```text
conversation
    ↓
clean-room memory writer
    ↓
structured memory artifact
    ↓
freeze + hash
    ↓
future queries generated separately
```

Writer restrictions:
- no gold memory
- no gold answers
- no future queries
- no other model's memory
- no benchmark relevance labels

The writer should record source IDs so memory construction can be evaluated independently from memory consumption.

---

## 8. Reader protocol

Each reader receives exactly one condition at a time.

The same query set is used across conditions.

The reader must return:
- answer
- evidence used
- confidence/status if applicable
- unsupported-claim flag
- provenance references

When evidence is insufficient, the correct behavior is to state uncertainty or lack of discussion rather than infer a plausible answer.

---

## 9. Cross-agent protocol

Run independently:

```text
Claude writer → Copilot reader
Copilot writer → Claude reader
```

Optionally include Codex when execution access is available.

The reader must receive:
- frozen memory
- query
- schema/protocol

It must not receive:
- original conversation
- gold answers
- writer report
- other conditions' results

Cross-agent evaluation happens only after both writer artifacts have been frozen.

---

## 10. Metrics

### Memory construction

- observation precision
- observation recall
- observation F1
- proposition precision/recall
- relationship precision/recall
- temporal transition accuracy
- ambiguity accuracy
- conflict accuracy
- negative-knowledge accuracy
- provenance accuracy
- invented-record rate
- retained bytes/tokens
- compression ratio

### Answer quality

- overall correctness
- historical recall
- decision continuity
- action/outcome
- temporal consistency
- ambiguity handling
- conflict handling
- negative knowledge
- provenance
- multi-hop correctness
- unsupported claim rate

### Efficiency

Measure actual values where exposed:

```text
input tokens
retrieved tokens
memory tokens
memory bytes
memory build time
retrieval latency
answer latency
API/model cost
```

Do not substitute token estimates for measured counts without labeling them explicitly.

---

## 11. Statistical reporting

Avoid presenting a single aggregate score as the entire conclusion.

Report:
- per-query results
- category-level results
- per-agent results
- per-condition results
- confidence intervals or bootstrap intervals where sample size permits
- failure examples
- retrieval evidence coverage

For paired condition comparisons, use the same queries and report paired differences.

---

## 12. Falsification criteria

The thesis should be considered weakened if any of the following occur consistently across realistic datasets:

1. Strong RAG matches or exceeds memory on long-horizon state reconstruction.
2. Memory construction loses important information at rates that erase its consumption advantage.
3. Memory requires substantially more context than expected to remain reliable.
4. Cross-agent memory transfer degrades materially.
5. Structured representation causes more unsupported claims than retrieval baselines.
6. Gains disappear outside synthetic/template-like conversations.

A null result is valuable. Do not tune the benchmark after seeing results merely to recover the expected outcome.

---

## 13. Success interpretation

A successful V7.6 result would not prove universal superiority.

It would provide stronger evidence that:

> structured, model-independent memory is a useful abstraction for long-horizon conversational continuity under realistic conditions.

The strongest result would show a combination of:

```text
high memory fidelity
+ high answer fidelity
+ lower context requirements
+ acceptable latency/cost
+ cross-agent transfer
+ strong uncertainty/provenance behavior
```

---

## 14. V7.5 → V7.6 changes

| Dimension | V7.5 | V7.6 |
|---|---|---|
| Corpus | synthetic/template-generated | realistic conversational traces |
| Scale | 2,000 events | multi-session conversations |
| RAG | deterministic lexical top-6 | lexical + semantic + hybrid baselines |
| Writer | clean-room autonomous | clean-room autonomous |
| Queries | future queries | future queries, broader categories |
| Instrumentation | mostly unavailable | explicit token/latency/cost capture |
| Cross-agent | bidirectional | bidirectional, post-freeze |
| Goal | strengthen structural evidence | test real-world robustness and efficiency |

---

## 15. Deliverables

Each agent run should produce:

```text
results/<agent>.memory.json
results/<agent>.memory_eval.json
results/<agent>.RAW.json
results/<agent>.BM25.json
results/<agent>.SEMANTIC_RAG.json
results/<agent>.HYBRID_RAG.json
results/<agent>.MEMORY.json
results/<agent>.MEMORY+RAW.json
results/<agent>.report.md
```

Cross-agent:

```text
results/<writer>_to_<reader>.json
```

All artifacts must include hashes/configuration identifiers where possible.
