# ANTIGRAVITY: SETUP ONLY

You are an infrastructure/setup agent, NOT an experiment runner.

STRICTLY DO NOT:
- run the full benchmark
- construct agent memory
- answer benchmark queries
- inspect evaluator gold
- inspect other agents' outputs
- generate benchmark scores
- use gold to tune retrieval
- substitute a proxy for GraphRAG, Graphiti, HippoRAG2, or RAPTOR

You MAY:
- install dependencies
- build/pull Docker images
- verify package versions
- run --help/version commands
- run import checks
- run tiny synthetic smoke tests containing NO benchmark data

SET UP:
RAW
BM25
Dense
Hybrid
Microsoft GraphRAG
official Graphiti
upstream HippoRAG2
upstream RAPTOR

Create:
competitors/<name>/adapter.py
competitors/<name>/runner.py
competitors/<name>/README.md
competitors/<name>/requirements.txt or environment spec
competitors/<name>/smoke_test.py

Every adapter must expose:
build(corpus_path, output_dir, config)
retrieve(query, k, index_dir, config)

Canonical event IDs must be preserved exactly, e.g. C01E003.

Normalized result:
{
  "query_id":"Q001",
  "condition":"bm25",
  "status":"EXECUTED",
  "evidence":[{"event_id":"C01E003","score":0.91}],
  "latency_ms":12.3
}

GRAPH SYSTEM RULE:
Use the real upstream implementation. Never call a proxy GraphRAG/Graphiti/HippoRAG2/RAPTOR.

If setup fails, record FAILED_SETUP and exact error. Do not fabricate a result.

GRAPHITI:
Prefer Docker + Neo4j/FalkorDB. Pin verified versions. Smoke-test only with synthetic data.

GRAPHRAG:
Use the actual Microsoft GraphRAG implementation. Record package version/commit and model/config dependencies.

HIPPORAG2/RAPTOR:
Use upstream implementations. If dependency/API drift prevents setup, document it rather than substituting another system.

ISOLATION:
Evaluator gold must never be mounted into agent or competitor containers.

STOP after infrastructure setup and synthetic smoke tests.

Write results/antigravity_setup_report.json with:
- full_benchmark_executed: false
- readiness status for every competitor
- versions/commits
- exact setup failures if any
