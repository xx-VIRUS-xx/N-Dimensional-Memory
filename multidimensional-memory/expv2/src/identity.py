"""Deterministic point-identity and granularity matching for EXP-V2.1.

No embeddings or LLM calls. The goal is to distinguish:
- SAME: surface variants / equivalent normalized points
- RELATED: one point is a more specific formulation of another
- DISTINCT: insufficient evidence to merge
"""
from .normalizer import canonical_surface, normalize_dimensions, load_points

# Dimensions that describe broad lexical/semantic roles and can safely support
# a granularity relation when shared.
ROLE_DIMS = {"noun", "verb", "subject", "actor", "object", "target", "action", "activity", "state", "intent", "emotion", "feeling", "time", "place", "instrument"}


def _tokens(surface):
    return set(canonical_surface(surface).split())


def _compatible(a, b):
    da = normalize_dimensions(a.get("dimensions", []))
    db = normalize_dimensions(b.get("dimensions", []))
    # A contradictory lexical class is a strong reason not to relate points.
    if "noun" in da and "verb" in db and not ({"action", "intent", "state"} & (da | db)):
        return False
    if "verb" in da and "noun" in db and not ({"action", "intent", "state"} & (da | db)):
        return False
    return bool((da & db) & ROLE_DIMS)


def classify_identity(a, b):
    """Return SAME, RELATED, or DISTINCT for two model points."""
    sa, sb = canonical_surface(a.get("surface", "")), canonical_surface(b.get("surface", ""))
    if sa == sb:
        return "SAME"
    if not _compatible(a, b):
        return "DISTINCT"

    ta, tb = _tokens(sa), _tokens(sb)
    if not ta or not tb:
        return "DISTINCT"

    # Containment captures granularity such as "play" -> "play football".
    if ta < tb or tb < ta:
        return "RELATED"

    # Same lexical head with different qualifiers, e.g. "new team" vs "team".
    if ta & tb:
        shared = len(ta & tb) / max(1, min(len(ta), len(tb)))
        if shared >= 0.5:
            return "RELATED"

    return "DISTINCT"


def build_identity_groups(model_docs):
    """Group points across models while preserving RELATED granularity."""
    models = sorted(model_docs)
    nodes = []
    for model in models:
        for p in load_points(model_docs[model]):
            p = dict(p)
            p["model"] = model
            nodes.append(p)

    groups = []
    for node in nodes:
        same_group = None
        for group in groups:
            if any(classify_identity(node, member) == "SAME" for member in group["members"]):
                same_group = group
                break
        if same_group is None:
            groups.append({"members": [node], "related_to": []})
        else:
            same_group["members"].append(node)

    # Compute cross-group RELATED links without merging them.
    for i, g in enumerate(groups):
        for j in range(i + 1, len(groups)):
            if any(classify_identity(a, b) == "RELATED" for a in g["members"] for b in groups[j]["members"]):
                g["related_to"].append(j)
                groups[j]["related_to"].append(i)

    return groups, models
