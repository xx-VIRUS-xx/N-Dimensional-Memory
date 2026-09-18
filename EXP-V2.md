# EXP-V2: Canonical Semantic Substrate

## Hypothesis

If Claude, Codex and Copilot independently interpret the same conversation, there should be a model-independent semantic core that can be extracted deterministically from their representations.

## What we are testing

1. **Point stability:** Does the same conceptual point appear across models?
2. **Dimension stability:** Which dimensions survive across all models?
3. **Model-specific enrichment:** Which dimensions appear only in some models?
4. **Uncertainty preservation:** Do disagreements remain visible instead of being silently collapsed?
5. **No information destruction:** Does canonicalization preserve the union of observed information while distinguishing common structure from model-specific observations?

## Baseline rules

- Surface variants such as `play`, `plays`, and `playing` are normalized to a shared surface for this experiment.
- Dimension labels are lower-cased and normalized.
- A dimension is **common** only if every participating model assigned it to the canonical point.
- A dimension appearing in one or more but not all models is retained as **model-specific**.
- Ambiguity is never resolved merely because one model made a stronger inference.
- Relationship inference is intentionally minimal. Full relationship derivation is EXP-V3.

## Expected example

For `football`:

```text
Claude   = noun + object + activity
Codex    = noun + object
Copilot  = noun + object + activity

COMMON   = noun + object
UNION    = noun + object + activity
```

This is exactly the kind of disagreement we want to preserve.

## Success condition

A successful EXP-V2 result is not "all models agree." It is:

> A canonical representation can retain the stable semantic core, retain model-specific observations, and preserve ambiguity without selecting a preferred model.

## Next experiment

EXP-V3 will take the canonical points and derive candidate relationships algorithmically.
