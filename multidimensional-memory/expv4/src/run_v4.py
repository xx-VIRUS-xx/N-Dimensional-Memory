import json
from pathlib import Path
from .temporal_v4 import build_v4

ROOT = Path(__file__).resolve().parents[1]
src = ROOT / "data" / "conversation_01.v31.json"
out = ROOT / "results" / "conversation_01.v4.json"
report = ROOT / "results" / "conversation_01.v4.report.md"

def main():
    data = json.loads(src.read_text())
    result = build_v4(data["points"])
    out.write_text(json.dumps(result, indent=2))
    m = result["metrics"]
    report.write_text(f'''# EXP-V4 Result\n\n## Metrics\n\n- Events: {m["events"]}\n- Anchored events: {m["anchored_events"]}\n- Unanchored events: {m["unanchored_events"]}\n- Temporal constraints: {m["temporal_constraints"]}\n- State-transition events: {m["state_transition_events"]}\n\n## Interpretation\n\nV4 preserves relative and explicit temporal evidence without inventing absolute dates. Source sentence order is recorded as weak ordering evidence, while explicit `after`/`before` markers receive stronger local ordering evidence. State transitions remain append-only.\n''')
    print(json.dumps(m, indent=2))

if __name__ == "__main__": main()
