import json
from pathlib import Path
from src.temporal_v4 import build_v4
from src.evolution_v41 import build_v41

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "data/conversation_01.v31.json").read_text())
v4 = build_v4(data["points"])
v41 = build_v41(v4)
( ROOT / "results/conversation_01.v41.json").write_text(json.dumps(v41, indent=2))
report = [
    "# EXP-V4.1 Report", "", 
    f"State updates: {v41['metrics']['state_updates']}",
    f"State histories: {v41['metrics']['state_histories']}",
    f"Detected transitions: {v41['metrics']['contradictions_or_transitions']}", "",
]
for c in v41["contradictions"]:
    report.append(f"- {c['subject_id']} / {c['target']}: {c['from']} -> {c['to']} ({c['resolution']})")
(ROOT / "results/conversation_01.v41.report.md").write_text("\n".join(report) + "\n")
print(json.dumps(v41["metrics"], indent=2))
