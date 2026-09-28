# Reference gold (pilot10)

`pilot10.gold.jsonl` is one annotator's reading (Claude) of the 10 pilot sentences. It is **reference only, not a scoring target**. It is used to design probes and must-haves, and as a diagnostic ceiling for `tools/ndm_math.py`.

## Reading the buckets

- `model_belief` is a hint, never a resolution (CONTRACT C9a). tick 8's `model_belief: "PostgreSQL"` does not resolve "its failover behavior"; MH3 requires that bucket to stay open.
- tick 9 ("the rate-limiting change") lists one candidate, event 6. Under C9 clause (c) the engine may resolve it (one compatible candidate in the window), recorded as `resolved_by: engine` with evidence tick 6. The gold keeps it written as a bucket so the engine's resolution can be checked.
- tick 6 (target: payments platform or separate service) states its alternatives in the sentence, so it stays open (MH2).

## Known limits

- Single annotator; a second human pass is pending.
- Source sentences were reconstructed from the BabyTest extraction (`../../ND-0/data/pilot10.source.jsonl`); replace them with the originals if they differ, and revise this file if that changes any reading.
