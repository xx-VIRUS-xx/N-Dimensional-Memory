# EXP-V7.2 — Experimental Specification

## 1. Motivation
V7.1 showed that benchmark-generated structured memory could support long-horizon queries and that bounded lexical retrieval could miss later temporal events. Its remaining limitation was that the V6 memory was compiled from canonical annotations.

V7.2 removes that assumption.

## 2. Hypotheses

H1. An agent can construct a model-agnostic semantic/relational memory from long conversation without needing the final query at extraction time.

H2. The generated memory can preserve temporal evolution, ambiguity, conflict, provenance, action/outcome, and scoped negative knowledge.

H3. A second model can consume the generated memory without raw conversation and reconstruct delayed history.

H4. Extraction errors and consumption errors can be measured separately.

## 3. Agents
Only Claude Code and Copilot.

Codex is excluded because of the current rate-limit constraint. Missing Codex is not a result.

## 4. Corpus
Use the exact V7.1 corpus:
- 1,200 chronological events
- same eight benchmark cases
- same gold annotations
- same delayed queries
- same distractors

Do not modify the corpus or gold labels.

## 5. New writer protocol
Each writer receives:
- full conversation corpus
- V6 memory schema
- memory design principles
- no gold V6 memory
- no expected answers
- no other agent results

The writer must produce a canonical memory artifact containing at minimum:

1. immutable observations
2. stable proposition identities
3. relationship records
4. temporal state histories
5. ambiguity records
6. conflict/belief histories
7. negative-knowledge records with scope/completeness
8. provenance records
9. source event IDs
10. confidence/status where applicable

The writer must not delete observations merely because a later state supersedes them.

## 6. Evaluation of generated memory
Compare generated memory to gold annotations using deterministic matching where possible.

Primary metrics:
- observation recall
- observation precision
- proposition recall/precision
- relation recall/precision
- temporal transition recall/precision
- ambiguity preservation rate
- conflict preservation rate
- negative-knowledge correctness
- provenance completeness
- invented-record rate

If exact deterministic matching is not possible, preserve raw artifacts and report the matching method explicitly. Do not invent a metric.

## 7. Consumer protocol
After writer artifact is frozen:

### Same-agent
Writer → generated memory → writer answers delayed queries.

### Cross-agent
Claude → memory → Copilot → delayed queries.
Copilot → memory → Claude → delayed queries.

Reader receives:
- generated memory artifact
- query set
- schema

Reader does NOT receive:
- original conversation
- gold memory
- gold answers
- writer's private reasoning

## 8. Comparison arms
Run V7.1 baselines where possible:
- RAW
- deterministic RAG
- generated V6 memory
- generated V6 + linked raw

Also retain the V7.1 gold-memory V6 result as a reference, clearly labeled `GOLD-V6`, not as an agent-generated condition.

## 9. Answer correctness
Use the existing V7.1 benchmark rubric. Null fields are not scored.

Additionally report:
- unsupported claims
- evidence IDs
- whether answer depended on raw evidence
- whether memory was sufficient

## 10. Provenance requirements
Every generated memory record should point to source event IDs where possible. Preserve role distinctions such as:
- observation
- confirmation
- inference
- later confirmation
- later memory read

## 11. Negative knowledge
Do not infer global absence from retrieval absence.
A `not_discussed` record requires explicit scope and sufficient completeness evidence.

## 12. Temporal reasoning
Do not collapse:
- state history
- temporal ordering
- overlapping disagreement
- current state

Non-overlapping states may form an evolution. Overlapping incompatible observations remain conflict/dispute unless later evidence resolves them.

## 13. Required artifacts
Each agent must create:

- `results/<agent>.memory.json`
- `results/<agent>.memory_eval.json`
- `results/<agent>.RAW.json`
- `results/<agent>.RAG.json`
- `results/<agent>.V6-GENERATED.json`
- `results/<agent>.V6-GENERATED+RAW.json`
- `results/<agent>.report.md`

Cross-agent:
- `results/claude_to_copilot.json`
- `results/copilot_to_claude.json`

## 14. Instrumentation
Record actual token counts and latency only if the environment exposes them. Otherwise use null.
Record artifact byte size and record counts if measurable locally.

## 15. Interpretation
Do not claim universal superiority. The key outputs are:
1. Can agents build the memory correctly?
2. What information is lost or distorted during construction?
3. Can another model consume the resulting artifact?
4. Which memory dimensions are robust versus fragile?
5. Does generated memory retain the downstream benefits observed with GOLD-V6?
