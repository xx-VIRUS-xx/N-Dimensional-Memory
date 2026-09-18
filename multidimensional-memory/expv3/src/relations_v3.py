"""EXP-V3 deterministic relationship candidate extraction.

The experiment intentionally does NOT decide facts. It produces typed candidate
relations with evidence and confidence tiers from the EXP-V2.1 substrate.
No LLM, embeddings, vector DB, or graph DB is used.
"""
from collections import defaultdict
import re

TEMPORAL_MARKERS = {
    "yesterday": -3, "last week": -3, "last month": -3,
    "today": 0, "now": 0, "currently": 0,
    "tomorrow": 3, "next month": 3, "next week": 3,
    "later": 2, "again": 1,
}

TRANSITION_MARKERS = {
    "stopped": "ended",
    "started": "began",
    "resumed": "resumed",
    "changed": "changed",
    "bought": "acquired",
    "joined": "joined",
}


def _norm(s):
    return re.sub(r"\s+", " ", s.lower().strip())


def _surface_match(surface, sentence):
    s = _norm(surface)
    sent = _norm(sentence)
    if not s:
        return False
    # Ignore punctuation and allow leading determiners/prepositions in observations.
    s = re.sub(r"^(at|in|on|to|with|for|after|before|the|his|her|a|an)\s+", "", s)
    return s in sent


def _point_sentence_index(points):
    index = defaultdict(set)
    for p in points:
        for sentence in p.get("evidence", []):
            index[p["canonical_id"]].add(sentence)
    return index


def _common_sentence_pairs(points):
    idx = _point_sentence_index(points)
    ids = list(idx)
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            shared = sorted(idx[a] & idx[b])
            if shared:
                yield a, b, shared


def _dims(p):
    return set(p.get("dimensions", {}).get("union", []))


def _surface_tokens(s):
    return set(re.findall(r"[a-z0-9]+", _norm(s)))


def _relation(a, b, rel, evidence, confidence, rule):
    return {
        "source": a,
        "target": b,
        "type": rel,
        "confidence": confidence,
        "rule": rule,
        "evidence": evidence,
    }


def derive_relationships(points):
    """Return deterministic candidate relationships from canonical points."""
    by_id = {p["canonical_id"]: p for p in points}
    relations = []

    # 1. Role relations: actor/subject -> action/verb; action -> object/target.
    for a_id, b_id, evidence in _common_sentence_pairs(points):
        a, b = by_id[a_id], by_id[b_id]
        da, db = _dims(a), _dims(b)
        # Subject/actor + action/verb: strong structural candidate.
        if ({"subject", "actor"} & da) and ({"action", "verb"} & db):
            relations.append(_relation(a_id, b_id, "performs", evidence, "high", "shared evidence + actor/subject to action/verb"))
        if ({"subject", "actor"} & db) and ({"action", "verb"} & da):
            relations.append(_relation(b_id, a_id, "performs", evidence, "high", "shared evidence + actor/subject to action/verb"))
        # Action/verb -> object/target/activity/instrument.
        if ({"action", "verb"} & da) and ({"object", "target", "activity", "instrument"} & db):
            relations.append(_relation(a_id, b_id, "acts_on", evidence, "medium", "shared evidence + action to object/target"))
        if ({"action", "verb"} & db) and ({"object", "target", "activity", "instrument"} & da):
            relations.append(_relation(b_id, a_id, "acts_on", evidence, "medium", "shared evidence + action to object/target"))
        # Actor/subject -> place/time gives contextual attachment, not semantic ownership.
        if ({"subject", "actor"} & da) and ({"place", "time"} & db):
            relations.append(_relation(a_id, b_id, "contextualized_by", evidence, "medium", "shared evidence + actor to place/time"))
        if ({"subject", "actor"} & db) and ({"place", "time"} & da):
            relations.append(_relation(b_id, a_id, "contextualized_by", evidence, "medium", "shared evidence + actor to place/time"))

    # 2. RELATED identity edges become explicit structural relations.
    for p in points:
        for rid in p.get("related_point_ids", []):
            if p["canonical_id"] < rid:
                relations.append(_relation(p["canonical_id"], rid, "granularity_related", [], "high", "EXP-V2.1 RELATED identity"))

    # 3. Temporal candidates from temporal dimensions and lexical markers.
    temporal = [p for p in points if "time" in _dims(p)]
    event_like = [p for p in points if ({"action", "verb", "state", "intent"} & _dims(p))]
    for t in temporal:
        for e in event_like:
            if t["canonical_id"] == e["canonical_id"]:
                continue
            evidence = sorted(set(t.get("evidence", [])) & set(e.get("evidence", [])))
            if not evidence:
                continue
            ts = _norm(" ".join(t.get("surfaces", [])))
            direction = None
            for marker, rank in TEMPORAL_MARKERS.items():
                if marker in ts:
                    direction = rank
                    break
            if direction is not None:
                rel = "temporal_context"
                relations.append(_relation(e["canonical_id"], t["canonical_id"], rel, evidence, "medium", f"time marker '{ts}'"))

    # 4. State transition candidates. Only create when the same evidence contains
    # a transition marker and another event/state point.
    for a_id, b_id, evidence in _common_sentence_pairs(points):
        a, b = by_id[a_id], by_id[b_id]
        sa = " ".join(a.get("surfaces", []))
        sb = " ".join(b.get("surfaces", []))
        for p, q, sp, sq in [(a,b,sa,sb),(b,a,sb,sa)]:
            for marker, transition in TRANSITION_MARKERS.items():
                if marker in sp and ({"state", "action", "verb"} & _dims(q)):
                    relations.append(_relation(p["canonical_id"], q["canonical_id"], f"state_transition_{transition}", evidence, "medium", f"marker '{marker}' + event/state dimensions"))

    # Deduplicate exact candidate records.
    unique = {}
    for r in relations:
        key = (r["source"], r["target"], r["type"])
        if key not in unique:
            unique[key] = r
        else:
            unique[key]["evidence"] = sorted(set(unique[key]["evidence"]) | set(r["evidence"]))
    return sorted(unique.values(), key=lambda x: (x["source"], x["target"], x["type"]))


def relation_metrics(points, relations):
    ids = {p["canonical_id"] for p in points}
    typed = defaultdict(int)
    for r in relations:
        typed[r["type"]] += 1
    connected = {x for r in relations for x in (r["source"], r["target"])}
    return {
        "canonical_points": len(points),
        "candidate_relations": len(relations),
        "connected_points": len(connected),
        "isolated_points": len(ids - connected),
        "relation_types": dict(sorted(typed.items())),
        "high_confidence_relations": sum(r["confidence"] == "high" for r in relations),
        "medium_confidence_relations": sum(r["confidence"] == "medium" for r in relations),
    }
