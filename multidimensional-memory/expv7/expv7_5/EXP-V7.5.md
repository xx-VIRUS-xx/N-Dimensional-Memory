# EXP-V7.5 — Distribution-Shifted Persistent Memory

## Objective
V7.4 showed strong memory formation on adversarially constructed conversations. V7.5 removes another possible shortcut: the writer must build memory before the evaluation queries exist, and the evaluation spans four independently generated domains.

## Hypotheses
- H1: durable-event selection generalizes across domains.
- H2: the memory substrate preserves observations, actions/outcomes, temporal state, belief evolution, ambiguity, scoped negative knowledge and provenance under distribution shift.
- H3: novel paraphrased and compositional queries can be answered from memory alone.
- H4: a different model can consume the frozen memory without the source conversation.
- H5: structured memory reduces the context needed for historical reconstruction, measured with actual instrumentation where available.

## Corpus
Four domains × 500 events = 2,000 events. Each domain contains 30 hidden durable events and 470 distractors. Distractors include lexical overlap, semantic similarity, temporal proximity, tentative statements, obsolete states, repeated paraphrases, unrelated-but-plausible events and delayed consequences.

The writer view contains no `kind`, relevance labels, benchmark case IDs, gold memory, raw-event relevance IDs, future queries or expected answers.

## Future-query protocol
After both writer artifacts are frozen, query generation uses evaluator-only gold annotations. Each domain receives direct, paraphrased, indirect, temporal, causal, multi-hop, negative-knowledge, ambiguity and compositional queries. Queries are not shown to writers before freeze.

## Conditions
1. RAW: source conversation available.
2. RAG: deterministic top-k lexical retrieval from the source conversation.
3. V6-GENERATED: only the frozen writer memory.
4. V6-GENERATED+RAW: frozen memory plus linked raw evidence.
5. CROSS-AGENT: reader receives only the other agent's frozen memory + novel queries.

## Metrics
### Selection
precision, recall, F1, retention ratio, compression ratio, false retention, missed durable events.

### Memory quality
observation precision/recall, proposition precision/recall, relationship semantic recall/precision, temporal transition recall, ambiguity preservation, belief/conflict preservation, action/outcome preservation, scoped negative knowledge, provenance completeness, invented-record rate.

### Consumption
answer correctness, temporal consistency, ambiguity handling, negative-knowledge correctness, provenance correctness, unsupported claims, multi-hop correctness.

### Efficiency
memory bytes, raw/context tokens, retrieval latency, memory-build time, answer latency, where tooling permits measurement. Never fabricate unavailable measurements.

## Interpretation
A strong result is convergence across domains and novel queries, especially when memory-only readers reconstruct multi-hop and temporal state. A failure under query shift is equally informative: it identifies a representation or retrieval boundary.

Do not claim universal superiority over RAG. The baseline is a specific deterministic lexical retriever.
