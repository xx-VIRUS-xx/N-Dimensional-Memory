# EXP-V7 Copilot Report

## Run

- Agent: `copilot`
- Cases: 7
- Conditions: `RAW`, `RAG`, `V6`, `V6+RAW`
- Records: 28
- Other agent outputs read before completion: none
- Benchmark cases and rubric modified: no

## Correctness

All seven cases were answered correctly in all four conditions under the supplied evidence. Category-level result: 1/1 for historical recall, action/outcome, temporal state, ambiguity, contradiction, negative knowledge, and provenance in each condition.

## Unsupported claims

Unsupported claims: 0 in every record. Ambiguous pronoun resolution was explicitly left unresolved. Conflicting deployment targets were preserved with both source identities. The negative-knowledge answer relied on the case's explicit claim that its conversation was complete.

## Evidence and context

- `RAW`: one complete case conversation supplied directly.
- `RAG`: one retrieved case chunk supplied.
- `V6`: structured case observations only, with observation IDs, provenance, status, and temporal fields where applicable.
- `V6+RAW`: the corresponding V6 observations plus linked raw case evidence.
- Input token counts: unavailable, recorded as `null`.
- Retrieval count: one chunk for each RAG case; no retrieval latency was exposed.
- V6 memory: 21 observations across seven isolated case records, including derived conflict status only where explicitly supported by two observations.

## Latency

Answer latency and retrieval latency were unavailable in this manual provider-neutral run and are recorded as `null`; no measurements were invented.

## Notable behavior

The run preserved unresolved ambiguity in `V7-AMB-01`, retained both overlapping deployment claims in `V7-CONFLICT-01`, reconstructed the full January-to-May service sequence in `V7-TIME-01`, and distinguished Codex's observation from Claude's later confirmation in `V7-PROV-01`.
