# Prompt to give Claude Code or Copilot

You are participating in EXP-V7.2, a controlled research experiment on model-agnostic persistent conversational memory.

Your task is to independently execute the full V7.2 protocol in `/mnt/data/expv7_2`.

Read `README.md`, `EXP-V7.2.md`, and `AGENT_HANDOFF.md` first. Run the setup/tests. Then construct your own persistent V6 memory from the 1,200-event conversation corpus before consulting the gold memory or any expected answers.

Your memory must preserve immutable observations, canonical propositions, relationships, temporal state histories, ambiguity, overlapping conflict, belief evolution, scoped negative knowledge, provenance, and source event IDs. Do not overwrite history merely because a newer state exists.

Freeze your generated artifact as `results/<your-agent>.memory.json`. Only after freezing it may you inspect `data/v6_memory.json` for deterministic evaluation.

Then run the four consumption conditions:
- RAW
- RAG
- V6-GENERATED
- V6-GENERATED+RAW

For RAG, use the actual deterministic retrieval artifacts and record exactly what was retrieved. Do not manually add chunks or fall back to the whole corpus.

For V6-GENERATED, use only your generated memory. The original conversation must be unavailable to the answering step.

For V6-GENERATED+RAW, use generated memory plus only linked raw events.

After your independent run, perform both cross-agent handoffs:
- Claude memory → Copilot reader
- Copilot memory → Claude reader

The reader must receive only the writer's generated memory, delayed queries, and schema. Do not provide the original conversation, gold memory, gold answers, or the writer's report.

Produce all required result files and a concise report. Validate everything. Never fabricate token counts, latency, or measurements. If unavailable, use null.

Most importantly: this experiment is about separating **memory construction quality** from **memory consumption quality**. Do not make a superiority claim. Report exactly what happened, including failures, missing records, unsupported claims, and retrieval gaps.
