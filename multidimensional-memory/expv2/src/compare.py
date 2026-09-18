from collections import Counter
from .normalizer import index_by_surface


def compare_models(model_docs):
    models = sorted(model_docs)
    index = index_by_surface(model_docs)
    canonical = []
    dimension_counts = Counter()

    for surface, observations in sorted(index.items()):
        per_model_dims = {m: observations[m]["dimensions"] for m in observations}
        common = set.intersection(*per_model_dims.values()) if per_model_dims else set()
        union = set.union(*per_model_dims.values()) if per_model_dims else set()

        for d in common:
            dimension_counts[d] += 1

        certainty = "common" if len(observations) == len(models) and common else "model_specific"
        canonical.append({
            "canonical_id": f"p_{len(canonical)+1:03d}",
            "surface": surface,
            "dimensions": {
                "common": sorted(common),
                "union": sorted(union),
                "model_specific": {
                    m: sorted(per_model_dims[m] - common) for m in models if m in per_model_dims
                },
            },
            "model_support": {m: m in observations for m in models},
            "certainty": certainty,
            "source_evidence": sorted({
                s for p in observations.values() for s in p["source_sentences"]
            }),
        })

    return canonical, models


def metrics(canonical, models):
    all_points = len(canonical)
    present_all = sum(1 for p in canonical if all(p["model_support"].values()))
    common_dims = sum(1 for p in canonical if p["dimensions"]["common"])
    total_dim_observations = sum(len(p["dimensions"]["union"]) for p in canonical)
    common_dim_observations = sum(len(p["dimensions"]["common"]) for p in canonical)

    return {
        "models": models,
        "canonical_point_count": all_points,
        "points_present_in_all_models": present_all,
        "point_coverage": round(present_all / all_points, 4) if all_points else 0,
        "points_with_at_least_one_common_dimension": common_dims,
        "dimension_preservation": round(common_dim_observations / total_dim_observations, 4) if total_dim_observations else 0,
    }
