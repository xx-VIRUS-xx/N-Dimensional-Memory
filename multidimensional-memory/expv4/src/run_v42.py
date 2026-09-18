import json
from pathlib import Path
from .temporal_v4 import build_v4
from .conflict_v42 import build_v42

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "data/conversation_01.v31.json").read_text())
v4 = build_v4(data["points"])
v42 = build_v42(v4)
(ROOT / "results/conversation_01.v42.json").write_text(json.dumps(v42, indent=2))
report = [
    "# EXP-V4.2 Report", "",
    f"State relationships: {v42['metrics']['state_relationships']}",
    f"Evolutions: {v42['metrics']['evolutions']}",
    f"Potential conflicts: {v42['metrics']['potential_conflicts']}",
    f"Preserved observations: {v42['metrics']['preserved_observations']}", "",
]
for x in v42["state_relationships"]:
    report.append(f"- {x['subject_id']} / {x['target']}: {x['from']} -> {x['to']} [{x['kind']}] ({x['reason']})")
(ROOT / "results/conversation_01.v42.report.md").write_text("\n".join(report) + "\n")
print(json.dumps(v42["metrics"], indent=2))
