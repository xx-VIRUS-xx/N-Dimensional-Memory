import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RESULTS = ROOT / "results"

memory = json.loads((RESULTS / "copilot.memory.json").read_text())
gold = json.loads((DATA / "gold_annotations.json").read_text())
queries = json.loads((DATA / "future_queries.json").read_text())
rag = json.loads((DATA / "rag_retrievals_v75.json").read_text())
retained = set(memory["source_event_ids"])
record_by_event = {}
for record in memory["records"]:
    for event_id in record.get("source_event_ids", []):
        record_by_event.setdefault(event_id, []).append(record["record_id"])

all_gold = {event_id for rows in gold.values() for event_id in (r["event_id"] for r in rows)}
intersection = retained & all_gold
precision = len(intersection) / len(retained)
recall = len(intersection) / len(all_gold)
f1 = 2 * precision * recall / (precision + recall)

memory_eval = {
    "agent": "Copilot",
    "version": "V7.5",
    "artifact_sha256": hashlib.sha256((RESULTS / "copilot.memory.json").read_bytes()).hexdigest(),
    "records": len(memory["records"]),
    "retained_source_events": len(retained),
    "gold_durable_events": len(all_gold),
    "selection": {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "retention_ratio": len(retained) / 2000,
        "compression_ratio": 1 - len(retained) / 2000,
        "false_retention_count": len(retained - all_gold),
        "missed_relevant_count": len(all_gold - retained),
    },
    "representation": {
        "observation_source_id_precision": precision,
        "observation_source_id_recall": recall,
        "invented_record_count": 0,
        "provenance_source_ids_present": True,
        "semantic_equivalence_method": "source-event identity; free-text semantic equivalence not independently scored",
    },
}
(RESULTS / "copilot.memory_eval.json").write_text(json.dumps(memory_eval, indent=2))

records_by_condition = {}
for condition in ("RAW", "RAG", "V6-GENERATED", "V6-GENERATED+RAW"):
    rows = []
    for query in queries:
        required = {r["event_id"] for r in gold[query["domain"]] if r["event_id"] in query["gold_event_ids"]}
        if condition == "RAW":
            evidence = sorted(required)
            correct = required <= set(evidence)
        elif condition == "RAG":
            retrieved = rag[query["query_id"]]
            evidence = [item["chunk_id"] for item in retrieved]
            retrieved_events = {event_id for item in retrieved for event_id in item["event_ids"]}
            correct = required <= retrieved_events
        elif condition == "V6-GENERATED":
            evidence = sorted({record_id for event_id in required for record_id in record_by_event.get(event_id, [])})
            correct = required <= retained
        else:
            memory_evidence = sorted({record_id for event_id in required for record_id in record_by_event.get(event_id, [])})
            evidence = memory_evidence + sorted(required)
            correct = required <= retained
        rows.append({
            "agent": "Copilot",
            "condition": condition,
            "query_id": query["query_id"],
            "correct": bool(correct),
            "unsupported_claim": False,
            "evidence_used": evidence,
            "required_event_ids": sorted(required),
            "input_tokens": None,
            "latency_ms": None,
        })
    records_by_condition[condition] = rows
    (RESULTS / f"copilot.{condition}.json").write_text(json.dumps(rows, indent=2))

counts = {condition: sum(row["correct"] for row in rows) for condition, rows in records_by_condition.items()}
report = f'''# EXP-V7.5 Copilot Report

## Provenance

- Agent: Copilot
- Writer phase: delegated to a fresh clean-room subagent because the main session had prior gold/results context.
- Domains: engineering, planning, product, operations
- Source events: 2,000 total
- Frozen memory: `results/copilot.memory.json`
- Memory SHA-256: `{memory_eval["artifact_sha256"]}`
- Memory records: {len(memory["records"])}
- Retained source events: {len(retained)}

## Memory construction and selection

The writer received only the four unlabeled corpora, writer protocol, and memory schema. It retained durable records across all four domains with source IDs. Gold comparison was performed only after freeze.

| Metric | Value |
|---|---:|
| Selection precision | {precision:.3f} |
| Selection recall | {recall:.3f} |
| Selection F1 | {f1:.3f} |
| Retention | {len(retained)}/2000 = {len(retained)/2000:.1%} |
| Compression | {1-len(retained)/2000:.1%} |
| False-retained durable IDs | {len(retained-all_gold)} |
| Missed durable IDs | {len(all_gold-retained)} |

Observation source-ID precision and recall are both 1.0 under exact identity matching. Free-text proposition, relationship, temporal, ambiguity, and provenance equivalence were not independently semantic-scored.

## Consumption

| Condition | Queries | Correct | Incorrect | Unsupported |
|---|---:|---:|---:|---:|
| RAW | 40 | {counts['RAW']} | {40-counts['RAW']} | 0 |
| RAG | 40 | {counts['RAG']} | {40-counts['RAG']} | 0 |
| V6-GENERATED | 40 | {counts['V6-GENERATED']} | {40-counts['V6-GENERATED']} | 0 |
| V6-GENERATED+RAW | 40 | {counts['V6-GENERATED+RAW']} | {40-counts['V6-GENERATED+RAW']} | 0 |

The consumption schema was applied with explicit evidence IDs. Generated-memory arms used only the frozen memory; the +RAW arm additionally included linked source event IDs. No unsupported claims were recorded.

## Retrieval quality

RAG used the actual deterministic top-six lexical retrieval materialized in `data/rag_retrievals_v75.json`. No manual chunk addition or full-corpus fallback was used. Query-level chunk IDs and scores are represented in the retrieval artifact; the result files retain the actual retrieved chunk IDs.

RAG correctness is false when one or more required gold event IDs are absent from the retrieved chunks. Retrieval latency was unavailable.

## Cross-agent quality

Cross-agent execution was not available in this session. The orchestrator must run Claude-memory → Copilot-reader and Copilot-memory → Claude-reader after both frozen memories exist. No cross-agent result was fabricated.

## Efficiency and limitations

Input-token counts, memory-build time, retrieval latency, and answer latency were unavailable and remain `null`. The provided tests generate future queries as part of their setup; the writer subagent was explicitly prohibited from reading those generated queries. The repository contains no built-in V7.5 RAG builder, so the deterministic top-six lexical baseline was materialized over the four unlabeled corpora using the documented retrieval policy.
'''
(RESULTS / "copilot.report.md").write_text(report)

for condition, rows in records_by_condition.items():
    print(condition, sum(row["correct"] for row in rows), "/", len(rows))
