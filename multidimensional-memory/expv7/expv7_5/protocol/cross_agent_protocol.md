# Cross-Agent Protocol

This phase starts only after both frozen memory artifacts exist.

Claude → Copilot:
Copilot receives Claude's frozen memory, novel queries, and memory schema.

Copilot → Claude:
Claude receives Copilot's frozen memory, novel queries, and memory schema.

Neither reader receives the original corpus, gold annotations, writer report, or the other agent's reasoning.

Record memory SHA-256 and input artifact hash. The reader must answer from the supplied memory only.
