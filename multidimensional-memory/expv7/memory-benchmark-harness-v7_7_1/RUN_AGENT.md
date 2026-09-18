# AGENT EXPERIMENT PROTOCOL

Fresh session.

PHASE A: MEMORY WRITER
Allowed: public/unlabeled corpus + schema + writer instructions.
Forbidden: evaluator gold, other agents, competitor results.
Produce frozen memory preserving decisions, outcomes, temporal state, supersession, ambiguity/conflict, negative knowledge, provenance, and multi-hop dependencies.

PHASE B: MEMORY READER
Allowed: frozen memory + future queries + reader schema.
Forbidden: evaluator gold and other systems' outputs.
Return answers plus exact evidence IDs.

ANTIGRAVITY is the third independent agent for this cycle, replacing Copilot.
Use a fresh session for writer and another fresh session for reader.
