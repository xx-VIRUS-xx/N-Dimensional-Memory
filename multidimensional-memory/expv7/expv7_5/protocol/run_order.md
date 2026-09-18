# V7.5 Run Order

1. Generate corpora.
2. Run Claude writer and Copilot writer in parallel.
3. Freeze both memory artifacts and record hashes.
4. Generate future queries only after both freezes.
5. Run each model's RAW/RAG/MEMORY/MEMORY+RAW conditions.
6. Run cross-agent readers as a separate post-run barrier.
7. Aggregate metrics.

Never add a wait-for-other-agent barrier inside Phase 1.
