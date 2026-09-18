# Codex V7.7 Repaired Run Report

## Completed

- Phase A writer artifact: `results/codex.memory.json`
- Phase A eval/metadata: `results/codex.memory_eval.json`
- Phase B retrieval outputs: `results/retrieval/codex.<condition>.json`

## Important Filesystem Note

This filesystem is case-insensitive, so `codex.memory.json` and `codex.MEMORY.json` collide. To preserve the writer memory artifact, all Phase B retrieval files are stored in `results/retrieval/`, matching the operator handoff retrieval layout.

## Runnable Conditions

- RAW: full conversation for each public query.
- BM25: local BM25 lexical retrieval, top-k 24.
- MEMORY: frozen Codex memory only.
- MEMORY+RAW: frozen Codex memory plus linked raw events.

## NOT_RUN Conditions

- DENSE: no verified dense embedding backend configured.
- HYBRID: dense backend unavailable.
- GRAPHRAG: no verified GraphRAG backend configured.
- HIPPORAG2: not installed/configured.
- RAPTOR: not installed/configured.

## Integrity

- Corpus SHA-256: `80a32f4f6edde3f65fa3ac74dede2750214b4514b23d8ca1c2bec9f7b7b9fec6`
- Public query SHA-256: `eb18624c78b25af7e927ff77f47878e890f795b2dc68f17f2f9d376d279d11d5`
- Memory SHA-256: `0887d43b4feeb86f0c264ac906b88776a8d651e921c719017054c1352369d715`

## Retrieval Hashes

```json
{
  "results/retrieval/codex.RAW.json": "1731db57c0f815ea7565b28eb95177cf328bfcd7dd97d79b6f4a9456ecb5f4fa",
  "results/retrieval/codex.BM25.json": "fe3073195fcd87398d9016ddc18285aad754f226429e4105f124d8ffcb12ce2d",
  "results/retrieval/codex.DENSE.json": "71c9da2238b680bfdf6347c7eafe962b324a9aafff1b1017ab2f237f2a7c5019",
  "results/retrieval/codex.HYBRID.json": "00806aa4dcdfbc1b48c216622b2e4b6d629db1d896500faaf815cfad6d2b8098",
  "results/retrieval/codex.GRAPHRAG.json": "ca783c4f3d190b464baf38d01681dd42ecb854bef919b4597aeae7b62196937c",
  "results/retrieval/codex.HIPPORAG2.json": "763efbad0264192a9d697b596921b25fed7c4278c245b8f34bb5dd74f362ef12",
  "results/retrieval/codex.RAPTOR.json": "641d483f17311059c7a276f428ff2be870e1ca64c548ad0772ee176adbfe9f48",
  "results/retrieval/codex.MEMORY.json": "a2d763ffa939ffd919a2c82577db88490cd195a4b30fb151382e947158455a04",
  "results/retrieval/codex.MEMORY+RAW.json": "3d3e86a33122842be4ae8a8c2ce089166c366333f4b44540ead9c5f1a6db8428"
}
```

## Limitations

No evaluator gold, relevance labels, other agent outputs, or previous result artifacts were used. The writer-visible corpus lacks explicit `event_id` fields, so source references use `conversation_id:timestamp`. Token counts and latency were unavailable and are recorded as null.
