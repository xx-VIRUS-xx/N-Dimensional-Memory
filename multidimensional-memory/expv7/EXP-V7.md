# EXP-V7 — Agent Utility Benchmark

## 1. Hypothesis
A persistent relational memory layer that preserves relationships, temporal state, actions, outcomes, ambiguity, disagreement, and provenance should improve long-horizon agent continuity compared with raw-context-only or similarity-only retrieval, while reducing the amount of historical context that must be supplied to the model.

## 2. Experimental question
When an agent receives a delayed query about an earlier interaction, does V6 memory allow it to reconstruct the relevant history and answer correctly without the original conversation being present?

## 3. Independent variables
- Memory condition: RAW, RAG, V6, V6+RAW
- Agent/provider: Codex, Claude Code, Copilot
- Query category
- Cross-agent vs same-agent memory writer/reader

## 4. Controlled variables
Keep constant:
- benchmark conversation
- delayed query
- expected answer rubric
- system/developer instructions used for the benchmark
- temperature/model settings where the provider exposes them
- maximum evidence/context budget where measurable
- evaluator rubric

Do not let one agent inspect another agent's answer before completing its own run.

## 5. Benchmark categories
### Historical recall
What approach/decision/event happened previously?

### Decision continuity
Why was a previous option abandoned or changed?

### Action → outcome
What did we try, and what happened afterward?

### Temporal state
What is the latest known state after multiple changes?

### Ambiguity
What did an ambiguous reference refer to? If unresolved, the correct answer may be that it remains ambiguous.

### Contradiction
Two observations conflict or overlap. The agent must preserve the disagreement rather than silently selecting a winner.

### Negative knowledge
Ask whether a topic was ever discussed. Correct behavior is to distinguish "not found in retrieved evidence" from "never discussed"; only the benchmark's complete observation set can justify the latter.

### Provenance
Ask which agent/source established a remembered claim and whether it was confirmed or merely inferred.

## 6. Conditions
### RAW
Provide the relevant raw transcript window directly.

### RAG
Index the same transcript into chunks. Retrieve using a fixed retrieval policy. Record retrieved chunks and scores.

### V6
Provide only the structured V6-derived memory required by the query. Include provenance and status fields. Do not silently add raw transcript text.

### V6+RAW
Provide V6 memory plus the minimum linked raw evidence required to verify claims.

## 7. Agent protocol
1. Read the benchmark case.
2. Read the condition-specific evidence.
3. Answer only the delayed query.
4. Cite memory/provenance identifiers when available.
5. Explicitly mark uncertainty instead of guessing.
6. Do not infer a relationship that is absent from the supplied memory.
7. Return a machine-readable result plus a short natural-language answer.

## 8. Scoring
Each case receives a rubric score from the benchmark evaluator, not an overall model ranking.

Recommended fields:
- factual correctness
- temporal correctness
- relationship correctness
- ambiguity correctness
- conflict preservation
- provenance correctness
- unsupported-claim count
- evidence sufficiency

Report aggregate metrics per condition and per query category. Do not collapse them into a "best agent" score.

## 9. Context efficiency
Record:
- input tokens/evidence tokens
- retrieved evidence count
- V6 memory nodes/edges supplied
- latency
- estimated cost when available

The primary efficiency comparison is correctness at a given evidence/context budget.

## 10. Cross-agent test
Writer agent A processes the conversation and writes V6 memory.
Reader agent B receives only the resulting V6 memory and delayed query.
Repeat across agent pairs. The purpose is to test model independence, not model superiority.

## 11. Interpretation
A successful V7 result would show that V6 memory is useful to an agent downstream. It would not by itself prove universal superiority over every RAG implementation or every model. Those claims require broader benchmarks.
