# EXP-V7.5 Copilot Report

## Provenance

- Agent: Copilot
- Writer phase: delegated to a fresh clean-room subagent because the main session had prior gold/results context.
- Domains: engineering, planning, product, operations
- Source events: 2,000 total
- Frozen memory: `results/copilot.memory.json`
- Memory file SHA-256: `e9b0c3be817cca8980be7fbab0fb600d19a1c629b786f14950758ec3daef7822`
- Embedded canonical SHA-256: `d0b1cc8e5fb25d584af2ef18d6cd5403fa34b9b82993b3a89276f51b263354a0`
- Memory records: 120
- Retained source events: 120

## Memory construction and selection

The writer received only the four unlabeled corpora, writer protocol, and memory schema. It retained durable records across all four domains with source IDs. Gold comparison was performed only after freeze.

| Metric | Value |
|---|---:|
| Selection precision | 1.000 |
| Selection recall | 1.000 |
| Selection F1 | 1.000 |
| Retention | 120/2000 = 6.0% |
| Compression | 94.0% |
| False-retained durable IDs | 0 |
| Missed durable IDs | 0 |

Observation source-ID precision and recall are both 1.0 under exact identity matching. Free-text proposition, relationship, temporal, ambiguity, and provenance equivalence were not independently semantic-scored.

The writer initially embedded a non-matching self-referential byte hash. The only post-freeze repair changed the hash field to a canonical hash computed with that field blank; records and source IDs were not changed. This repair is disclosed rather than treated as writer instrumentation.

## Consumption

| Condition | Queries | Correct | Incorrect | Unsupported |
|---|---:|---:|---:|---:|
| RAW | 40 | 40 | 0 | 0 |
| RAG | 40 | 12 | 28 | 0 |
| V6-GENERATED | 40 | 40 | 0 | 0 |
| V6-GENERATED+RAW | 40 | 40 | 0 | 0 |

The consumption schema was applied with explicit evidence IDs. Generated-memory arms used only the frozen memory; the +RAW arm additionally included linked source event IDs. No unsupported claims were recorded.

## Retrieval quality

RAG used the actual deterministic top-six lexical retrieval materialized in `data/rag_retrievals_v75.json`. No manual chunk addition or full-corpus fallback was used. Query-level chunk IDs and scores are represented in the retrieval artifact; the result files retain the actual retrieved chunk IDs.

RAG correctness is false when one or more required gold event IDs are absent from the retrieved chunks. Retrieval latency was unavailable.

## Cross-agent quality

Claude-memory → Copilot-reader was executed using only Claude's frozen memory, the novel queries, and the consumption schema. Claude's memory contained 85 records and 120 unique durable source IDs; the actual frozen-file SHA-256 was `6ac0b3ce63d8ceae1359a5c81634f721c7277fef802cd9e9dfbefe1c6753b473`. Copilot answered `40/40` queries with zero unsupported claims; evidence IDs are recorded in `results/claude_to_copilot.json`.

Copilot-memory → Claude-reader is now present in `results/copilot_to_claude.json` and was independently validated as an executed reader artifact: 40/40 queries correct, zero unsupported claims, and 40 evidence references resolving to Copilot memory record IDs. The artifact also discloses its writer-hash verification note; the stated memory hash does not match the reader's recomputation, so that integrity gap remains visible rather than silently corrected.

## Efficiency and limitations

Input-token counts, memory-build time, retrieval latency, and answer latency were unavailable and remain `null`. The provided tests generate future queries as part of their setup; the writer subagent was explicitly prohibited from reading those generated queries. The repository contains no built-in V7.5 RAG builder, so the deterministic top-six lexical baseline was materialized over the four unlabeled corpora using the documented retrieval policy. The writer initially embedded a hash that did not match final bytes; the memory contents were unchanged and the hash field was repaired to a canonical blank-field hash, disclosed above in the artifact metadata.
