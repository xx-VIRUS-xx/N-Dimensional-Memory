from collections import Counter
from .identity import build_identity_groups
from .normalizer import normalize_dimensions


def canonicalize_v21(model_docs):
    groups, models = build_identity_groups(model_docs)
    points = []
    for idx, group in enumerate(groups, 1):
        per_model = {m: [] for m in models}
        for member in group["members"]:
            per_model[member["model"]].append(member)

        dim_sets = {
            m: set(d for p in ps for d in normalize_dimensions(p.get("dimensions", [])))
            for m, ps in per_model.items() if ps
        }
        common = set.intersection(*dim_sets.values()) if dim_sets else set()
        union = set.union(*dim_sets.values()) if dim_sets else set()
        surfaces = sorted({p["surface"] for p in group["members"]})
        points.append({
            "canonical_id": f"p_{idx:03d}",
            "surfaces": surfaces,
            "dimensions": {
                "common": sorted(common),
                "union": sorted(union),
                "model_specific": {m: sorted(dim_sets.get(m, set()) - common) for m in models},
            },
            "model_support": {m: bool(per_model[m]) for m in models},
            "evidence": sorted({s for p in group["members"] for s in p.get("source_sentences", [])}),
            "raw_observations": [
                {"model": p["model"], "surface": p["raw_surface"], "dimensions": sorted(normalize_dimensions(p.get("dimensions", []))), "confidence": p.get("confidence")}
                for p in group["members"]
            ],
            "related_point_ids": [f"p_{j+1:03d}" for j in group["related_to"]],
        })
    return points, models


def metrics_v21(points, models):
    all_models = len(models)
    same_groups = sum(1 for p in points if sum(p["model_support"].values()) >= 2)
    all_model_groups = sum(1 for p in points if all(p["model_support"].values()))
    related_edges = sum(len(p["related_point_ids"]) for p in points) // 2
    common_dims = sum(len(p["dimensions"]["common"]) for p in points)
    union_dims = sum(len(p["dimensions"]["union"]) for p in points)
    return {
        "models": models,
        "canonical_points": len(points),
        "points_supported_by_2_or_more_models": same_groups,
        "points_supported_by_all_models": all_model_groups,
        "multi_model_support_rate": round(same_groups / len(points), 4) if points else 0,
        "all_model_support_rate": round(all_model_groups / len(points), 4) if points else 0,
        "related_point_edges": related_edges,
        "dimension_intersection_union_ratio": round(common_dims / union_dims, 4) if union_dims else 0,
    }
