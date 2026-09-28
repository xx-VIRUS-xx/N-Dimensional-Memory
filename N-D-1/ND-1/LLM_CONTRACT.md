# What the LLM is asked for (and nothing more)

Per sentence, the LLM returns entities and, for each entity, dimensions with values, in the ND-0 (BabyTest) format:

```json
{"event_id": "s4", "entities": [{"name": "...", "dimensions": {"dimension_name": "value"}}]}
```

Free dimension names are allowed. The prompt keeps the BabyTest constraints: no invented information, no relationships just because entities co-occur, no resolving ambiguity the sentence leaves open.

Everything else (ticks, peg identity, value linking, cleaning, dimension canonicalisation, epistemic status, buckets, collisions, trajectories, depiction) is the engine's job, in code and math.
