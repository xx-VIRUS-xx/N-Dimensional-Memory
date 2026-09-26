# Extraction

Each event is processed independently through Claude Code.

`run_extraction.py` starts a new non-interactive Claude process for every event and gives it only the extraction prompt template and the current event.

No previous event result is passed into the next invocation.

The output of this phase is the entity-and-dimension representation. No embedding, relationship scoring, graph construction, or normalization is performed here.
