import json
from pathlib import Path
from .temporal_v4 import build_v4
from .conflict_v43 import build_v43

ROOT = Path(__file__).resolve().parents[1]

CASES = {
    "ordered_evolution": [
        "Rahul started playing football.",
        "Rahul stopped playing football later.",
        "Rahul resumed playing football after that.",
    ],
    "unordered_conflict": [
        "Rahul is playing football.",
        "Rahul is not playing football.",
    ],
    "repeated_same_state": [
        "Rahul is playing football.",
        "Rahul is playing football again.",
    ],
}


def make_points(sentences):
    points = []
    for i, sentence in enumerate(sentences):
        state = "playing" if "playing" in sentence.lower() else "playing"
        value = "inactive" if "not playing" in sentence.lower() or "stopped" in sentence.lower() else "active"
        if "resumed" in sentence.lower() or "started" in sentence.lower():
            value = "active"
        points.extend([
            {"canonical_id": "rahul", "dimensions": {"union": ["actor", "subject"]}, "evidence": [sentence]},
            {"canonical_id": f"playing_{i}", "dimensions": {"union": ["action", "state", "verb"]}, "evidence": [sentence], "surfaces": ["playing"]},
            {"canonical_id": f"state_{i}", "dimensions": {"union": ["state"]}, "evidence": [sentence], "surfaces": [value]},
        ])
    return points


def build_case(name, sentences):
    v4 = build_v4(make_points(sentences))
    # Benchmark normalization: plain present-tense assertions are state observations,
    # not transition verbs, so represent them explicitly for V4.3.
    for event in v4["events"]:
        low = event["source_sentence"].lower()
        if "not playing" in low:
            event["transition_markers"].append({"marker": "state", "state": "inactive"})
        elif "is playing" in low:
            event["transition_markers"].append({"marker": "state", "state": "active"})
    v43 = build_v43(v4)
    return {"case": name, "input": sentences, "v4": v4, "v43": v43}


results = {name: build_case(name, sentences) for name, sentences in CASES.items()}
(ROOT / "results/conversation_01.v43.json").write_text(json.dumps(results, indent=2))

lines = ["# EXP-V4.3 Report", "", "| Case | Evolutions | Potential conflicts | Preserved events |", "|---|---:|---:|---:|"]
for name, r in results.items():
    m = r["v43"]["metrics"]
    lines.append(f"| {name} | {m['evolutions']} | {m['potential_conflicts']} | {m['preserved_observations']} |")
lines += ["", "## Principle", "", "Source sentence order is retained as provenance but is not sufficient to classify opposing states as evolution.", ""]
(ROOT / "results/conversation_01.v43.report.md").write_text("\n".join(lines))
print(json.dumps({name: r["v43"]["metrics"] for name, r in results.items()}, indent=2))
