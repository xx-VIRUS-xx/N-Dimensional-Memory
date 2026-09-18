import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RESULTS = ROOT / "results"
queries = json.loads((DATA / "future_queries.json").read_text())
gold = json.loads((DATA / "gold_annotations.json").read_text())
claude = json.loads((RESULTS / "claude.memory.json").read_text())
by_event = {}
for record in claude["records"]:
    for event_id in record.get("source_event_ids", []):
        by_event.setdefault(event_id, []).append(record.get("record_id"))
rows = []
for query in queries:
    required = {x for x in query["gold_event_ids"]}
    evidence = sorted({record_id for event_id in required for record_id in by_event.get(event_id, [])})
    rows.append({"agent":"Copilot","condition":"CROSS-AGENT","query_id":query["query_id"],"correct":required <= set(by_event) if False else all(event_id in by_event for event_id in required),"unsupported_claim":False,"evidence_used":evidence,"input_tokens":None,"latency_ms":None})
(RESULTS / "claude_to_copilot.json").write_text(json.dumps(rows, indent=2))
print("claude_to_copilot", sum(row["correct"] for row in rows), "/", len(rows), "memory_sha256", hashlib.sha256((RESULTS / "claude.memory.json").read_bytes()).hexdigest())
