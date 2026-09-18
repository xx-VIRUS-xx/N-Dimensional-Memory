"""EXP-V3.1: evidence-constrained deterministic relationship candidates."""
from collections import defaultdict
import re

ACTION_DIMS = {"action", "verb"}
ACTOR_DIMS = {"actor", "subject"}
OBJECT_DIMS = {"object", "target", "activity", "instrument"}
TIME_DIMS = {"time"}
PLACE_DIMS = {"place"}
STATE_DIMS = {"state"}

PREP_OBJECTS = {"with", "to", "for", "on", "at", "in", "from", "into", "after", "before"}
NON_ACTION_VERB_DIMS = {"emotion", "feeling", "intent"}

def norm(s):
    return re.sub(r"\s+", " ", s.lower().strip())

def tokens(s):
    return re.findall(r"[a-z0-9]+", norm(s))

def dims(p):
    return set(p.get("dimensions", {}).get("union", []))

def evidence_map(points):
    out = defaultdict(set)
    for p in points:
        for e in p.get("evidence", []):
            out[e].add(p["canonical_id"])
    return out

def relation(source, target, typ, evidence, confidence, rule):
    return {"source": source, "target": target, "type": typ,
            "confidence": confidence, "rule": rule,
            "evidence": sorted(set(evidence))}

def shared(a, b):
    return sorted(set(a.get("evidence", [])) & set(b.get("evidence", [])))

def _is_lexically_contained(container, item):
    ct, it = tokens(container), tokens(item)
    return bool(it) and it < ct

def derive_relationships_v31(points):
    by_id = {p["canonical_id"]: p for p in points}
    rs = []

    # 1. Actor -> action. Require a genuine action dimension, excluding
    # verbs whose only semantic role is emotion/feeling/intent.
    for a in points:
        for b in points:
            if a is b: continue
            ev = shared(a, b)
            if not ev: continue
            da, db = dims(a), dims(b)
            if ACTOR_DIMS & da and ACTION_DIMS & db:
                if not ((NON_ACTION_VERB_DIMS & db) and not ("action" in db)):
                    rs.append(relation(a["canonical_id"], b["canonical_id"], "performs", ev, "high", "shared evidence + actor/subject -> action/verb"))

    # 2. Action -> object. Prefer explicit lexical/compound evidence. A plain
    # action/object co-occurrence is medium only when the action is not an
    # emotion/intent-only verb.
    for a in points:
        da = dims(a)
        if not (ACTION_DIMS & da) or (NON_ACTION_VERB_DIMS & da and "action" not in da):
            continue
        for b in points:
            if a is b: continue
            db = dims(b)
            if not (OBJECT_DIMS & db): continue
            ev = shared(a, b)
            if not ev: continue
            confidence = "medium"
            rule = "shared evidence + action -> object/target"
            if _is_lexically_contained(b.get("surfaces", [""])[0], a.get("surfaces", [""])[0]):
                confidence = "high"
                rule = "compound/lexical containment + action -> object"
            rs.append(relation(a["canonical_id"], b["canonical_id"], "acts_on", ev, confidence, rule))

    # 3. Context belongs to an actor only when actor and context share evidence.
    for a in points:
        if not (ACTOR_DIMS & dims(a)): continue
        for b in points:
            if a is b: continue
            if not (TIME_DIMS | PLACE_DIMS) & dims(b): continue
            ev = shared(a, b)
            if ev:
                rs.append(relation(a["canonical_id"], b["canonical_id"], "contextualized_by", ev, "medium", "shared evidence + actor -> time/place"))

    # 4. Preserve V2.1 RELATED identity without pretending it is semantic truth.
    for p in points:
        for rid in p.get("related_point_ids", []):
            if p["canonical_id"] < rid:
                rs.append(relation(p["canonical_id"], rid, "granularity_related", [], "high", "EXP-V2.1 RELATED identity"))

    # 5. Temporal context: event -> explicit time point in the same evidence.
    for t in points:
        if "time" not in dims(t): continue
        for e in points:
            if e is t or not (ACTION_DIMS | STATE_DIMS | {"intent"}) & dims(e): continue
            ev = shared(t, e)
            if ev:
                rs.append(relation(e["canonical_id"], t["canonical_id"], "temporal_context", ev, "medium", "shared evidence + explicit time dimension"))

    # 6. State transitions: only when the transition marker is itself in the
    # event surface. This avoids manufacturing transitions from unrelated words.
    transition_words = {"stopped": "ended", "started": "began", "resumed": "resumed", "changed": "changed", "bought": "acquired", "joined": "joined"}
    for p in points:
        s = norm(" ".join(p.get("surfaces", [])))
        for marker, transition in transition_words.items():
            if marker in s and (ACTION_DIMS | STATE_DIMS) & dims(p):
                rs.append(relation(p["canonical_id"], p["canonical_id"], f"state_transition_{transition}", p.get("evidence", []), "high", f"transition marker '{marker}' in event surface"))

    # Deduplicate. Self-transition is retained because it describes the point's
    # own state semantics, not a relationship to another point.
    unique = {}
    for r in rs:
        key = (r["source"], r["target"], r["type"])
        if key not in unique:
            unique[key] = r
        else:
            unique[key]["evidence"] = sorted(set(unique[key]["evidence"]) | set(r["evidence"]))
    return sorted(unique.values(), key=lambda r: (r["source"], r["target"], r["type"]))

def metrics(points, relations):
    ids = {p["canonical_id"] for p in points}
    connected = {x for r in relations for x in (r["source"], r["target"])}
    typed = defaultdict(int)
    for r in relations: typed[r["type"]] += 1
    return {
        "canonical_points": len(points),
        "candidate_relations": len(relations),
        "connected_points": len(connected),
        "isolated_points": len(ids - connected),
        "relation_types": dict(sorted(typed.items())),
        "high_confidence_relations": sum(r["confidence"] == "high" for r in relations),
        "medium_confidence_relations": sum(r["confidence"] == "medium" for r in relations),
    }
