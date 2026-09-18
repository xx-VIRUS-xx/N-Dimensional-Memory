# EXP-V7.1 — Experimental Specification

## 1. What V7.0 gave us
V7.0 established that multiple agents could consume the proposed V6 memory representation and answer the tested long-horizon cases. Across Codex, Claude, and Copilot, RAW was 100% applicable correctness; V6 and V6+RAW were also 100% in the completed benchmark. Claude's RAG run had one temporal failure, producing 9/11 applicable checks (81.8%).

However, V7.0 had a major methodological limitation: its RAG and V6 evidence were not independently materialized retrieval/memory pipelines. Codex explicitly reported that evidence was represented by condition-scoped identifiers rather than separate retrieved chunks or generated V6 memory files. The benchmark was also only 7 cases long and RAW exposed too much of the original context.

Therefore V7.0 supports the statement:
> The proposed relational memory representation can be consumed by multiple agents and can preserve the tested temporal, ambiguity, conflict, negative-knowledge, action/outcome, and provenance information.

It does **not** support:
> V6 is superior to RAG.

## 2. V7.1 hypothesis
When historical evidence is diluted inside a long conversation, a structured relational memory representation will allow an agent to reconstruct relevant history from fewer supplied context units than a similarity-only retrieval baseline, while preserving temporal state, ambiguity, conflict, negative knowledge, and provenance.

## 3. Agents
Only:
- Claude Code
- Copilot

Codex is excluded solely because of the current rate limit. Do not interpret the missing Codex arm as a performance result.

## 4. Corpus
The benchmark contains 1,200 chronological conversation events. The corpus is synthetic but deliberately constructed to create lexical distractors and long-horizon dilution.

Each event has:
- event_id
- timestamp
- speaker
- text
- topic tags
- optional canonical signal annotation

The benchmark contains signal events plus distractors. Distractors may reuse names, tools, projects, dates, verbs, and technical terms without carrying the queried proposition.

## 5. Conditions
### RAW
Supply the complete raw evidence window defined by the case. This is an upper-bound evidence condition, not an efficiency baseline.

### RAG
Use `src/build_rag.py` to chunk the corpus and retrieve with the same deterministic lexical policy for every agent. Supply only the returned chunks and scores. Record exactly what was retrieved.

### V6
Use `src/build_v6_memory.py` to construct the canonical persistent memory. Supply only the memory records relevant to the query. The memory contains propositions, relationships, temporal intervals, state transitions, ambiguity, conflict, action/outcome, and provenance.

### V6+RAW
Supply the V6 records plus only the raw events linked to those records.

## 6. Benchmark cases
Cases cover:
1. historical recall
2. decision continuity
3. action → outcome
4. temporal state
5. ambiguity
6. overlapping conflict
7. negative knowledge
8. provenance

Each case has an answer rubric and an evidence-completeness declaration.

## 7. Required agent behavior
- Do not use general knowledge to answer conversation-history questions.
- Do not silently resolve ambiguity.
- Do not select one side of an overlapping conflict.
- Distinguish temporal evolution from simultaneous disagreement.
- Say `not_discussed` only when the supplied evidence is complete enough to establish it.
- Distinguish observed facts from inferred/confirmed state.
- Include evidence IDs in the result.

## 8. Metrics
Primary:
- applicable correctness rate
- category correctness
- unsupported claims
- evidence units supplied
- retrieved chunks for RAG
- V6 records supplied

Secondary where measurable:
- input tokens
- retrieval latency
- answer latency

Do not fabricate unavailable measurements.

## 9. Cross-agent persistence
After the same-agent condition runs, execute writer → reader handoff:
- Claude writes canonical V6 memory from the supplied conversation.
- Copilot reads only that memory and delayed queries.
- Copilot writes canonical V6 memory.
- Claude reads only that memory and delayed queries.

The reader must not receive the original conversation in the V6-only handoff.

## 10. Interpretation
V7.1 can demonstrate utility, context efficiency, and model-independent consumption. It cannot establish universal superiority from two agents and one synthetic benchmark. Any observed difference must be reported with the exact retrieval policy, context budget, and failure cases.
