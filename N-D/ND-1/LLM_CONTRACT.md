# What the LLM is asked for (and nothing more)

Per sentence, the LLM returns entities and, for each entity, dimensions with values, in the ND-0 (BabyTest) format:

```json
{"event_id": "s4", "entities": [{"name": "...", "type": "person|org|system|other", "dimensions": {"dimension_name": "value"}}]}
```

Dimension names are chosen from the dimension dictionary supplied with the prompt; a new name is allowed only when none fits. `type` is required: the engine's single-candidate rule (C9c) needs it to decide which pegs are compatible with "he/she", "it" or "the X".

Each call is a fresh, stateless session: the sentence, speaker and time, and the dictionary, with no earlier sentences. The LLM resolves references answered inside the sentence and marks every other reference as unresolved (local ambiguity run, C12). The prompt keeps the BabyTest constraints: no invented information, no relationships just because entities co-occur, no resolving ambiguity the sentence leaves open.

Everything else (ticks, peg identity, value linking, cleaning, dimension canonicalisation, epistemic status, buckets, collisions, trajectories, depiction) is the engine's job, in code and math.
