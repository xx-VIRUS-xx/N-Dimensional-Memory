# EXP-V7.0 Results

## 1. Purpose

EXP-V7.0 tested whether a persistent structured memory substrate could be consumed by multiple coding agents while preserving conversational information that is important for long-horizon continuity.

The benchmark used four conditions:

- **RAW**: agent receives the raw conversation.
- **RAG**: agent receives condition-scoped retrieved evidence.
- **V6**: agent receives the structured persistent V6 memory representation.
- **V6+RAW**: agent receives V6 memory plus linked raw evidence.

Three agents participated: Codex, Claude Sonnet 5, and Copilot.

## 2. Benchmark scope

There were **7 benchmark cases** per condition and **4 conditions**, giving:

- 7 cases × 4 conditions = 28 records per agent.
- 3 agents × 4 conditions × 7 cases = **84 agent-condition-case observations**.

The benchmark categories covered:

1. Historical recall
2. Action/outcome memory
3. Temporal state
4. Ambiguity
5. Contradiction/conflict
6. Negative knowledge
7. Provenance

The benchmark was deliberately designed to test more than simple factual recall. In particular, it tested whether an agent could preserve temporal evolution, unresolved ambiguity, conflicting observations, negative knowledge, and source provenance.

## 3. Results summary

Correctness below is calculated over the **applicable rubric fields**. Non-applicable fields are not counted.

| Agent | RAW | RAG | V6 | V6+RAW |
|---|---:|---:|---:|---:|
| Codex | 16/16 (100%) | 16/16 (100%) | 21/21 (100%) | 21/21 (100%) |
| Claude Sonnet 5 | 11/11 (100%) | 9/11 (81.8%) | 11/11 (100%) | 11/11 (100%) |
| Copilot | 16/16 (100%) | 16/16 (100%) | 21/21 (100%) | 21/21 (100%) |

The differing denominators arise because the applicability of rubric fields varies by case. They are therefore not raw percentages over all JSON fields.

## 4. Codex results

Codex completed all seven cases under all four conditions. Its report marks every applicable category field correct and records **0 unsupported claims across all 28 records**.

RAW, RAG, V6, and V6+RAW all produced correct answers for the applicable fields in the Codex run. fileciteturn18file0L9-L26

Examples from the Codex run:

- Historical recall reconstructed that approach A was tried first, abandoned because latency was too high, and followed by approach B. fileciteturn18file1L49-L63
- Temporal state reconstructed polling in January, webhooks in March, and temporary webhook disablement during migration in May. fileciteturn18file1L81-L95
- Ambiguity preserved the unresolved Rahul/Arjun referent rather than selecting one. fileciteturn18file1L97-L111
- V6 represented the temporal sequence as separate state observations and retained provenance. fileciteturn18file3L327-L341
- V6 represented the Jaipur/Delhi disagreement as disputed rather than silently resolving it. fileciteturn18file3L360-L373
- V6 represented MongoDB as not discussed while retaining the completeness-of-evidence condition. fileciteturn18file3L375-L389
- V6 preserved that Codex originally observed the migration failure and Claude later confirmed it. fileciteturn18file3L391-L405

## 5. Claude Sonnet 5 results

Claude produced 100% applicable-field correctness for RAW, V6, and V6+RAW. The RAG condition was the only observed answer-level failure in the benchmark.

The RAG temporal-state case retrieved only the January polling evidence. It did not surface the March webhook transition or May disablement, so Claude explicitly declined to claim the latest state from the retrieved evidence. The record is marked `factual_correct: false` and `temporal_correct: false`. fileciteturn19file0L42-L56

The same temporal case under V6 reconstructed the complete January → March → May evolution and the latest known state. fileciteturn19file2L288-L302

Claude's V6 condition also preserved:

- unresolved Rahul/Arjun ambiguity, fileciteturn19file2L304-L318
- disputed Jaipur/Delhi deployment observations with provenance, fileciteturn19file2L320-L334
- negative knowledge that MongoDB was not discussed, with complete evidence marked, fileciteturn19file2L336-L350
- provenance linking Codex's original observation to Claude's later confirmation. fileciteturn19file2L352-L366

The V6+RAW run cross-checked the structured memory against the raw conversation and recovered the temporal sequence, ambiguity, conflict, negative knowledge, and provenance correctly. fileciteturn19file3L411-L425 fileciteturn19file3L427-L441 fileciteturn19file3L443-L457

## 6. Copilot results

Copilot achieved 100% applicable-field correctness across RAW, RAG, V6, and V6+RAW.

Its RAG temporal-state result retrieved the full January → March → May sequence, while its ambiguity result preserved the unresolved Rahul/Arjun reference. fileciteturn19file4L502-L507

## 7. What V7.0 demonstrated

V7.0 provides evidence for several properties of the proposed memory substrate:

### 7.1 Cross-agent consumption

The same structured memory representation was successfully consumed by different agent implementations. V6 produced correct applicable-field results for the tested cases across Codex, Claude, and Copilot.

### 7.2 Temporal continuity

The benchmark showed that temporal state can be represented as an evolving sequence rather than only as a single latest value. Codex and Claude's V6 runs reconstructed the polling → webhooks → disabled sequence. fileciteturn18file3L327-L341 fileciteturn19file2L288-L302

### 7.3 Ambiguity preservation

The memory representation can retain an unresolved ambiguity instead of forcing an unsupported answer. The tested case retained Rahul and Arjun as candidates. fileciteturn18file3L343-L357

### 7.4 Conflict preservation

The system can preserve competing observations and represent their status as disputed when overlapping observations lack a temporal explanation. fileciteturn18file3L360-L373

### 7.5 Negative knowledge

The benchmark explicitly tested the distinction between “not discussed” and simply “not found.” V6 represented MongoDB as not discussed with a complete evidence condition. fileciteturn18file3L375-L389

### 7.6 Provenance

The memory representation retained who originally observed a fact and who later confirmed it. fileciteturn18file3L391-L405

### 7.7 Evidence-grounded behavior

Across Codex's 28 records, unsupported claims were zero. fileciteturn18file0L20-L26

## 8. What V7.0 did NOT demonstrate

V7.0 should not be used to claim that V6 is categorically superior to RAG.

The most important limitation is methodological: the Codex report states that V7.0 did **not** provide separately materialized RAG chunks or V6 memory files. Instead, condition-scoped evidence identifiers were derived from benchmark cases. fileciteturn18file0L28-L38

Therefore, V7.0 did not constitute a fully independent end-to-end comparison between:

- a real RAG indexing/retrieval pipeline, and
- a real V6 ingestion/storage/retrieval pipeline.

The Claude RAG temporal failure is still an observed retrieval failure in that run, but the implementations and evidence paths were not sufficiently standardized to interpret the result as a general superiority result.

## 9. Additional limitations

### Small benchmark

The benchmark contains only seven cases. This is sufficient for a proof-of-concept evaluation, but not for broad statistical claims about long-horizon memory performance.

### RAW is an easy baseline

RAW exposes the complete conversation directly to the model. High RAW accuracy therefore mainly establishes that the agents can answer the questions when the relevant source material is available. It does not test retrieval under memory pressure.

### No measured token cost

Codex reported that token counts were unavailable, so `input_tokens` was null. fileciteturn18file0L28-L30

### No measured latency

Codex reported that latency was not measured by the environment, so `latency_ms` was null. fileciteturn18file0L32-L34

### V6 memory was not independently generated from arbitrary conversation

The benchmark primarily evaluates consumption and preservation of the structured representation. It does not establish how reliably an LLM would construct that representation from unconstrained real-world conversations.

### Retrieval difficulty was limited

The benchmark conversations were small enough that relevant evidence could remain relatively accessible. This does not reproduce the severe dilution found in a months-long coding-agent history containing thousands of irrelevant events.

## 10. Interpretation

The strongest defensible interpretation of V7.0 is:

> **V7.0 demonstrates that the proposed persistent relational-memory representation can be consumed by multiple coding agents while preserving the tested historical, temporal, ambiguity, conflict, negative-knowledge, and provenance information. It also exposes a concrete retrieval failure in the Claude RAG run. However, the benchmark is small and the RAG/V6 conditions were not implemented as fully independent end-to-end retrieval pipelines, so V7.0 does not establish superiority of V6 over RAG.**

## 11. Why V7.1 follows naturally

V7.1 addresses the main methodological weakness directly.

It introduces:

- a substantially longer conversation corpus,
- deterministic materialized RAG chunks/indexes,
- bounded top-k retrieval,
- materialized V6 structured memory,
- explicit evidence accounting,
- the same benchmark queries across conditions,
- and a two-agent execution plan using Claude and Copilot because Codex is temporarily rate-limited.

The goal is no longer simply to ask whether agents can read the memory. The next experiment asks whether **structured relational memory can preserve useful long-horizon state when conventional retrieval is forced to operate under a bounded evidence budget**.

## 12. Status

**V7.0: completed.**

**Conclusion:** proof-of-concept support for the memory substrate, with a clear need for a more controlled retrieval-vs-memory experiment.
