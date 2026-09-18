# EXP-V7.7 — Modern Long-Horizon Memory Benchmark

V7.7 is the first comparative benchmark in this series designed to test the proposed model-agnostic persistent memory architecture against stronger retrieval and memory baselines, not only lexical RAG.

## Agents
- Claude
- Copilot
- Codex

## Core arms
1. RAW — full conversation/context
2. BM25 — lexical retrieval baseline
3. DENSE — embedding retrieval baseline
4. HYBRID — dense + lexical retrieval
5. GRAPHRAG — graph-based retrieval
6. HIPPORAG2 — associative graph-memory retrieval
7. RAPTOR — hierarchical retrieval/summarization
8. MEMORY — generated structured persistent memory
9. MEMORY+RAW — generated memory plus raw evidence

External systems may be substituted only if documented in the run report. The benchmark does not treat any implementation as ground truth.

## Important
The benchmark intentionally separates:
- memory construction quality
- retrieval quality
- answer quality
- cross-agent persistence
- efficiency

Do not use evaluator gold files during writer construction.
