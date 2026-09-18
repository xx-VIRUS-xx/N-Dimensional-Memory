# Memory Benchmark Harness V7.7.1

This is the reproducible harness for the persistent conversational-memory benchmark.

Separation:
- agent environment: public corpus/schema/instructions only
- competitor environment: corpus/query inputs, never gold
- evaluator environment: gold/scoring only
- frozen memory: never silently rebuilt downstream

Conditions:
RAW, BM25, Dense, Hybrid, Memory, Memory+RAW, GraphRAG, Graphiti, HippoRAG2, RAPTOR.

Statuses:
EXECUTED / NOT_EXECUTED / FAILED_SETUP / FAILED_RUNTIME / INVALID_RESULT / INCOMPLETE

Never interpret NOT_EXECUTED as zero.

V7.7.1 specifically guards against the V7.7 canonical-ID mismatch and broken query-evidence key.
