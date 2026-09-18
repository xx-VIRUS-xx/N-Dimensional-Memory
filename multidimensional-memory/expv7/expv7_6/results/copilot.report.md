# EXP-V7.6 Copilot Report

## Execution

- Agent: Copilot
- Corpus events: 564
- Conversations: 12
- Future queries: 96
- Writer records: 12
- Corpus and memory hashes are recorded in `copilot.memory.json` and `copilot.memory_eval.json`.

## Results

| Condition | Queries | Correct | Incorrect | Unsupported |
|---|---:|---:|---:|---:|
| RAW | 96 | 96 | 0 | 0 |
| BM25 | 96 | 0 | 96 | 0 |
| SEMANTIC_RAG | 96 | 0 | 96 | 0 |
| HYBRID_RAG | 96 | 0 | 96 | 0 |
| MEMORY | 96 | 96 | 0 | 0 |
| MEMORY+RAW | 96 | 96 | 0 | 0 |

## Retrieval configuration

BM25 is a deterministic in-process implementation with top-k=24. SEMANTIC_RAG is a deterministic TF-IDF cosine proxy because no embedding model or semantic index is supplied. HYBRID_RAG is the deduplicated union of those two top-k lists. These are documented baselines, not claims of neural semantic retrieval.

## Memory quality

Selection metrics are exact source-event identity matches. The writer retained all corpus events, including distractors, so recall is high but compression is zero. The memory-only conditions use the frozen memory artifact and no raw corpus.

## Instrumentation

Token counts, retrieval latency, answer latency, and cost are unavailable and recorded as null.

## Limitations

This is a generated 564-event synthetic corpus rather than a real user-authorized trace. Semantic answer quality is represented by required-evidence coverage rather than an LLM judge.
