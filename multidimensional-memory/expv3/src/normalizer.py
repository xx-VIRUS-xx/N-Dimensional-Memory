"""Deterministic normalization for EXP-V2.

This intentionally avoids an LLM. The point is to discover what can be
preserved with a transparent algorithm after model interpretation.
"""

import re
from collections import defaultdict

DIMENSION_ALIASES = {
    "verb": "verb",
    "noun": "noun",
    "subject": "subject",
    "actor": "actor",
    "object": "object",
    "target": "target",
    "action": "action",
    "activity": "activity",
    "state": "state",
    "emotion": "emotion",
    "feeling": "feeling",
    "intent": "intent",
    "time": "time",
    "place": "place",
    "instrument": "instrument",
}


def canonical_surface(surface: str) -> str:
    s = surface.lower().strip()
    s = re.sub(r"\s+", " ", s)
    # Remove shallow function-word variation without doing semantic resolution.
    s = re.sub(r"^(at|in|on|during|for|after) ", "", s)
    s = re.sub(r"^(the|a|an) ", "", s)
    s = re.sub(r"^his ", "", s)
    s = s.replace("every sunday", "sunday")
    # Treat simple inflections as the same conceptual surface for this baseline.
    if s in {"play", "plays", "playing", "play / plays / playing"}:
        return "play"
    if s in {"love", "loves"}:
        return "love"
    return s


def normalize_dimensions(dimensions):
    out = set()
    for d in dimensions or []:
        key = str(d).lower().strip()
        out.add(DIMENSION_ALIASES.get(key, key))
    return out


def load_points(doc):
    points = []
    for p in doc.get("points", []):
        points.append({
            "surface": canonical_surface(p.get("surface", "")),
            "raw_surface": p.get("surface", ""),
            "dimensions": normalize_dimensions(p.get("dimensions", [])),
            "confidence": p.get("confidence"),
            "source_sentences": p.get("source_sentences", []),
            "interpretations": p.get("interpretations", []),
        })
    return points


def index_by_surface(model_docs):
    index = defaultdict(dict)
    for model, doc in model_docs.items():
        for point in load_points(doc):
            index[point["surface"]][model] = point
    return index
