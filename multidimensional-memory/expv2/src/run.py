import json
from pathlib import Path
from .compare import compare_models, metrics
from .invariants import derive_relations

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "conversation_01"
RESULTS = ROOT / "results"


def main():
    model_docs = {}
    for model in ("claude", "codex", "copilot"):
        path = DATA / f"{model}.json"
        with path.open() as f:
            model_docs[model] = json.load(f)

    canonical, models = compare_models(model_docs)
    result = {
        "conversation_id": model_docs[models[0]].get("conversation_id", "conversation_01"),
        "points": canonical,
        "ambiguities": sorted({
            json.dumps(a, sort_keys=True)
            for doc in model_docs.values()
            for a in doc.get("ambiguities", [])
        }),
        "relations": derive_relations(canonical),
        "metrics": metrics(canonical, models),
    }
    result["ambiguities"] = [json.loads(x) for x in result["ambiguities"]]

    RESULTS.mkdir(exist_ok=True)
    out = RESULTS / "conversation_01.canonical.json"
    out.write_text(json.dumps(result, indent=2) + "\n")

    report = RESULTS / "conversation_01.report.md"
    m = result["metrics"]
    lines = [
        "# EXP-V2 Conversation 01 Report",
        "",
        f"Models compared: {', '.join(models)}",
        "",
        "## Metrics",
        f"- Canonical points: {m['canonical_point_count']}",
        f"- Points present in all models: {m['points_present_in_all_models']}",
        f"- Point coverage: {m['point_coverage']:.2%}",
        f"- Points with at least one common dimension: {m['points_with_at_least_one_common_dimension']}",
        f"- Dimension preservation (intersection / union): {m['dimension_preservation']:.2%}",
        "",
        "## Canonical points",
    ]
    for p in canonical:
        lines.append(f"### `{p['surface']}`")
        lines.append(f"- common: {', '.join(p['dimensions']['common']) or 'none'}")
        lines.append(f"- union: {', '.join(p['dimensions']['union']) or 'none'}")
        for model, dims in p["dimensions"]["model_specific"].items():
            if dims:
                lines.append(f"- {model}-specific: {', '.join(dims)}")
        lines.append("")

    report.write_text("\n".join(lines))
    print(out)
    print(report)
    print(json.dumps(m, indent=2))


if __name__ == "__main__":
    main()
