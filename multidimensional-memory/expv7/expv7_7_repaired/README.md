# EXP-V7.7 Repaired — Long-Horizon Persistent Memory Benchmark

This is the repaired V7.7 package. The previous gold query evidence mapping was invalid because required evidence IDs pointed to generic filler and did not overlap the durable-event set. This version rebuilds and validates the evaluator gold.

## Research questions
1. Can an agent construct compact persistent memory from long-running conversation?
2. Can that memory answer delayed long-horizon questions with evidence and temporal consistency?
3. Can another model family consume the frozen memory without the original conversation?
4. Does the proposed representation provide utility beyond established retrieval and temporal-graph memory systems such as Graphiti?

## Conditions
RAW, BM25, DENSE, HYBRID, GraphRAG, HippoRAG2, RAPTOR, Graphiti, MEMORY, MEMORY+RAW, plus six directed cross-agent handoffs.

## Critical rule
Graphiti and other external systems must consume the raw conversation, not our generated memory. If an implementation cannot genuinely run, mark `NOT_RUN`; never substitute a weaker proxy silently.

## Operator guide
Read `OPERATOR_HANDOFF.md` before running anything. Run `pytest -q` and `python src/validate.py` before exposing the corpus to agents.

## Data
- 1,200 events
- 12 conversations
- 216 curated durable events
- 96 future queries
- 8 categories × 12 conversations

The corpus is synthetic/template-generated and is a controlled benchmark, not a claim of real-world generalization.

## Executable retrieval runners

After writer memories are frozen:

```bash
python run_retrieval.py --condition raw
python run_retrieval.py --condition bm25 --top-k 24
python run_retrieval.py --condition semantic --top-k 24
python run_retrieval.py --condition hybrid --top-k 24
```

Results are written to `results/retrieval/`.

The semantic condition is a deterministic TF-IDF cosine baseline, not a neural embedding system. Graphiti remains a separate real-system run.
