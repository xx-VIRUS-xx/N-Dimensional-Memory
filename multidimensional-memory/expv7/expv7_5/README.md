# EXP-V7.5 — Distribution-Shifted Persistent Memory

V7.5 tests whether model-agnostic persistent memory remains useful when both the conversation domain and the eventual query distribution change.

## Core question
Can an agent build durable relational memory from a long conversation **without seeing future queries**, and can another model reconstruct unseen, paraphrased, multi-hop questions from that frozen memory alone?

## Design
- 4 independent domains, 500 events each
- 30 durable events per domain, 470 distractors
- Writer sees only unlabeled chronological conversations + memory schema/rules
- Future queries are generated **after memory freeze** from hidden gold annotations
- Query wording and composition are intentionally novel to the writer
- Conditions: RAW, deterministic RAG, V6-GENERATED, V6-GENERATED+RAW
- Mandatory post-run cross-agent phase after both memories exist
- Token, byte, retrieval-latency and answer-latency instrumentation where available

## Domains
1. Engineering / infrastructure
2. Work planning
3. Product development
4. Operations / support

## Scientific rule
This is not a leaderboard and does not establish that structured memory universally beats RAG. It tests the stated distribution-shift hypothesis against a fixed lexical-RAG baseline.

Run tests with:
```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q
```
