import json
from pathlib import Path
from .compare_v21 import canonicalize_v21, metrics_v21

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "conversation_01"
RESULTS = ROOT / "results"


def main():
    model_docs = {}
    for model in ("claude", "codex", "copilot"):
        with (DATA / f"{model}.json").open() as f:
            model_docs[model] = json.load(f)

    points, models = canonicalize_v21(model_docs)
    result = {
        "experiment": "EXP-V2.1",
        "conversation_id": "conversation_01",
        "identity_policy": {
            "SAME": "normalized surface equivalent",
            "RELATED": "compatible points with different granularity/qualifier",
            "DISTINCT": "insufficient evidence to relate",
        },
        "points": points,
        "metrics": metrics_v21(points, models),
    }
    out = RESULTS / "conversation_01.v21.json"
    out.write_text(json.dumps(result, indent=2) + "\n")

    lines = ["# EXP-V2.1 Identity Report", "", "## Metrics"]
    for k, v in result["metrics"].items():
        lines.append(f"- {k}: {v}")
    lines += ["", "## Canonical points"]
    for p in points:
        lines.append(f"### `{', '.join(p['surfaces'])}` ({p['canonical_id']})")
        lines.append(f"- common dimensions: {', '.join(p['dimensions']['common']) or 'none'}")
        lines.append(f"- union dimensions: {', '.join(p['dimensions']['union']) or 'none'}")
        lines.append(f"- related points: {', '.join(p['related_point_ids']) or 'none'}")
        for obs in p["raw_observations"]:
            lines.append(f"- {obs['model']}: `{obs['surface']}` -> {', '.join(obs['dimensions'])}")
        lines.append("")
    (RESULTS / "conversation_01.v21.report.md").write_text("\n".join(lines))
    print(json.dumps(result["metrics"], indent=2))


if __name__ == "__main__":
    main()
