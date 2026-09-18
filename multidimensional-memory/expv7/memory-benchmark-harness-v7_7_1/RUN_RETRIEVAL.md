# RETRIEVAL EXECUTION

Run only after source and gold validation pass.

Conditions:
RAW, BM25, Dense, Hybrid, GraphRAG, Graphiti, HippoRAG2, RAPTOR.

Every condition receives the same canonical corpus, query set, top-k and event-ID namespace.

A missing condition is NOT_EXECUTED or FAILED_SETUP, never a score of zero.

Run:
python scripts/validate_source.py
python scripts/validate_gold.py
then the installed competitor runners.
