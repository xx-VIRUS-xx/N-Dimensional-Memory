# Fixed RAG retrieval policy used for this agent's run

Chunking: split each case's `conversation` field on sentence boundaries (`. `), one sentence per chunk.

Retrieval: score each chunk by keyword overlap (case-insensitive token overlap) against the `delayed_query`, keep all chunks with overlap > 0, ordered by score descending, ties broken by original order. If no chunk scores > 0, fall back to returning all chunks (since these benchmark conversations are short and single-topic).

This policy is fixed across all 7 cases and was decided before scoring/retrieving any case, per EXP-V7 §6 (RAG: "Record retrieved chunks and scores").
