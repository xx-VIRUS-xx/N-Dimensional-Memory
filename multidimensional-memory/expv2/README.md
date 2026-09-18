# EXP-V2: Canonical Semantic Substrate

EXP-V2 tests the next hypothesis after EXP-V1:

> Different models can produce different surface representations of the same conversation, while a stable semantic substrate can be extracted without choosing one model as the authority.

This experiment deliberately does **not** use embeddings, vector search, graph databases, or another LLM for canonicalization.

## Pipeline

```text
Claude / Codex / Copilot representations
                |
                v
        normalization layer
                |
                v
       cross-model comparison
                |
        +-------+--------+
        |                |
        v                v
 semantic invariants  model-specific signals
        |
        v
 canonical substrate
```

## Run

```bash
python -m src.run
pytest -q
```

The runner reads the three model representations under `data/conversation_01/` and writes `results/conversation_01.canonical.json` plus a human-readable report.

## Important constraint

The canonicalizer is intentionally conservative. A dimension appearing in only one model is **not promoted to a fact**. It remains a model-specific observation.

The first implementation uses exact normalized labels and simple intersection/union logic. This is a baseline, not the final algorithm.
