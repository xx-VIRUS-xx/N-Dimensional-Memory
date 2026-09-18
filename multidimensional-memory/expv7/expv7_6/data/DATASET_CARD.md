# V7.6 Dataset Card

{
  "events": 564,
  "conversations": 12,
  "sessions_per_conversation": 6,
  "future_queries": 96,
  "durable_annotated_events": 216,
  "generator_seed": 7601,
  "note": "Synthetic but manually structured realistic conversational traces. No private user data."
}

The corpus is synthetic, but conversations are written as messy multi-session project discussions rather than templated event labels. Durable annotations and future queries are separated from the writer-visible corpus. The writer must not inspect `evaluation/` until its memory artifact is frozen.
