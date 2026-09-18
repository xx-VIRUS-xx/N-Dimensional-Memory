# EXP-V7.7 Protocol

## Research question
Can a model-agnostic structured persistent memory layer preserve and transfer long-horizon conversational state more reliably and efficiently than modern retrieval and memory architectures?

## Hypotheses
H1. Structured memory improves retrieval of temporal, multi-hop, supersession, ambiguity, provenance and negative-knowledge queries.
H2. Generated memory can be consumed by a different model family without requiring the original model.
H3. Any advantage must survive comparison with modern graph/hierarchical/embedding retrieval, not only BM25.
H4. Memory construction quality is an independent bottleneck and must be scored separately.

## Agent protocol
Each writer gets only:
- unlabeled conversation corpus
- public schema
- public design rules
- public benchmark instructions

Writer must not inspect:
- evaluator gold
- expected answers
- relevance labels
- other agent outputs
- other condition outputs

Freeze memory before reading any evaluation results.

## Evaluation categories
- historical recall
- decision continuity
- action → outcome
- temporal state/revision
- ambiguity
- conflict/belief evolution
- negative knowledge
- provenance
- multi-hop
- compositional retrieval

## Metrics
### Memory construction
- source-event precision/recall/F1
- invented-record rate
- proposition/relationship coverage
- temporal transition coverage
- ambiguity coverage
- conflict preservation
- negative-knowledge coverage
- provenance coverage
- memory bytes / source bytes
- compression ratio

### Retrieval
- required-evidence recall
- required-evidence precision
- answer correctness
- abstention correctness
- retrieval latency
- index/build cost

### Consumption
- answer correctness
- unsupported claim rate
- context/input tokens
- answer tokens
- end-to-end latency
- provenance correctness
- temporal correctness

### Cross-agent
Run all six directed pairs:
Claude→Copilot, Copilot→Claude, Claude→Codex, Codex→Claude, Copilot→Codex, Codex→Copilot.
The reader receives the frozen writer memory and future queries, not the original conversation.

## Fairness
All retrieval systems must use the same corpus and query set. Record actual retrieved chunks/records. Do not report a method as successful merely because the final answer happened to be correct without evidence coverage.

## Strong baselines
Use official/public implementations where practical. HippoRAG 2 explicitly targets associative/multi-hop retrieval; GraphRAG and RAPTOR are included as structural alternatives. Record exact version/configuration.

## Failure rule
If an implementation cannot run, mark it NOT_RUN and report why. Never replace it silently with a weaker proxy.
