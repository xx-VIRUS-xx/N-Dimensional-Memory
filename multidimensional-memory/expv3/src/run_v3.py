import json
from pathlib import Path
from .relations_v3 import derive_relationships, relation_metrics

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "conversation_01.v21.json"
OUT_JSON = ROOT / "results" / "conversation_01.v3.json"
OUT_MD = ROOT / "results" / "conversation_01.v3.report.md"


def main():
    substrate = json.loads(INPUT.read_text())
    points = substrate["points"]
    relations = derive_relationships(points)
    metrics = relation_metrics(points, relations)
    result = {
        "experiment": "EXP-V3",
        "conversation_id": substrate["conversation_id"],
        "hypothesis": "Candidate relationships can be derived from canonical points using dimensions, shared evidence, identity links, and explicit temporal/state markers without another model call.",
        "policy": {
            "relationships_are_candidates": True,
            "no_fact_inference": True,
            "no_llm": True,
            "no_embeddings": True,
            "no_vector_db": True,
            "no_graph_db": True,
        },
        "points": points,
        "relations": relations,
        "metrics": metrics,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2) + "\n")
    lines = [
        "# EXP-V3: Deterministic Relationship Candidates", "",
        "## Hypothesis", "",
        result["hypothesis"], "",
        "## Metrics", "",
    ]
    for k, v in metrics.items():
        lines.append(f"- **{k}:** `{v}`")
    lines += ["", "## Candidate relations", ""]
    for r in relations:
        ev = "; ".join(r["evidence"]) if r["evidence"] else "identity substrate"
        lines.append(f"- `{r['source']} -> {r['target']}` **{r['type']}** ({r['confidence']}) — {r['rule']} — evidence: {ev}")
    lines += ["", "## Interpretation rule", "", "These are candidate edges, not asserted facts. Human approval or a later policy layer is required before promoting a candidate to a fact."]
    OUT_MD.write_text("\n".join(lines) + "\n")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
