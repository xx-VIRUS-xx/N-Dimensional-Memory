"""EXP-V4: conservative temporal/evolving-memory layer over EXP-V3.1."""
from collections import defaultdict
import re

ACTION_DIMS = {"action", "verb", "intent"}
STATE_DIMS = {"state"}
ACTOR_DIMS = {"actor", "subject"}
TIME_PATTERNS = [
    (re.compile(r"\bevery\s+(sunday|monday|tuesday|wednesday|thursday|friday|saturday)\b", re.I), "recurring_weekly"),
    (re.compile(r"\b(yesterday|today|tomorrow)\b", re.I), "relative_day"),
    (re.compile(r"\b(next\s+month|next\s+week|next\s+year)\b", re.I), "relative_future"),
    (re.compile(r"\b(last\s+month|last\s+week|last\s+year)\b", re.I), "relative_past"),
    (re.compile(r"\b(summer|winter|spring|autumn|fall)\b", re.I), "seasonal"),
    (re.compile(r"\b(later|after|before|again)\b", re.I), "relative_order"),
]
TRANSITIONS = {
    "stopped": "ended",
    "started": "began",
    "resumed": "resumed",
    "changed": "changed",
    "bought": "acquired",
    "joined": "joined",
}

def norm(s):
    return re.sub(r"\s+", " ", s.lower().strip())

def dims(p):
    return set(p.get("dimensions", {}).get("union", []))

def evidence_points(points):
    out = defaultdict(list)
    for p in points:
        for e in p.get("evidence", []):
            out[e].append(p)
    return out

def extract_time_anchors(text):
    found = []
    for pat, kind in TIME_PATTERNS:
        for m in pat.finditer(text):
            found.append({"text": m.group(0), "kind": kind, "explicit": kind not in {"relative_order"}})
    # preserve source order and deduplicate
    seen = set(); result = []
    for x in sorted(found, key=lambda z: text.lower().find(z["text"].lower())):
        k = (norm(x["text"]), x["kind"])
        if k not in seen:
            seen.add(k); result.append(x)
    return result

def event_points(points):
    return [p for p in points if dims(p) & ACTION_DIMS or dims(p) & STATE_DIMS]

def make_events(points):
    events = []
    by_ev = evidence_points(points)
    # One event per source evidence sentence, with action/state points as its semantic payload.
    for idx, (sentence, ps) in enumerate(by_ev.items(), 1):
        payload = [p["canonical_id"] for p in ps if dims(p) & (ACTION_DIMS | STATE_DIMS)]
        if not payload:
            continue
        actors = [p["canonical_id"] for p in ps if dims(p) & ACTOR_DIMS]
        # Bind an actor point to later evidence when its canonical surface is explicitly present.
        low_sentence = norm(sentence)
        known_actor_points = [p for p in points if dims(p) & ACTOR_DIMS]
        for ap in known_actor_points:
            surfaces = [norm(x) for x in ap.get("surfaces", [])]
            if any(re.search(rf"\b{re.escape(x)}\b", low_sentence) for x in surfaces if x):
                actors.append(ap["canonical_id"])
        anchors = extract_time_anchors(sentence)
        transitions = []
        low = norm(sentence)
        for marker, state in TRANSITIONS.items():
            if re.search(rf"\b{re.escape(marker)}\b", low):
                transitions.append({"marker": marker, "state": state})
        if re.search(r"\bnot\s+playing\b", low):
            transitions.append({"marker": "stopped", "state": "ended"})
        events.append({
            "event_id": f"e_{idx:03d}",
            "sequence": idx,
            "source_sentence": sentence,
            "point_ids": sorted(set(payload)),
            "actor_ids": sorted(set(actors)),
            "time_anchors": anchors,
            "transition_markers": transitions,
            "temporal_status": "anchored" if anchors else "unanchored",
            "ordering_evidence": "source_sentence_order",
        })
    return events

def temporal_constraints(events):
    constraints = []
    # Source order is weak narrative evidence, not a claim about wall-clock time.
    for a, b in zip(events, events[1:]):
        constraints.append({"before": a["event_id"], "after": b["event_id"], "type": "sequence", "confidence": "medium", "evidence": "source_sentence_order"})
    # Explicit after/before markers upgrade only the local ordering claim.
    for i, e in enumerate(events):
        text = norm(e["source_sentence"])
        if ("after" in text or "later" in text) and i > 0:
            constraints.append({"before": events[i-1]["event_id"], "after": e["event_id"], "type": "explicit_after", "confidence": "high", "evidence": e["source_sentence"]})
        if "before" in text and i > 0:
            constraints.append({"before": e["event_id"], "after": events[i-1]["event_id"], "type": "explicit_before", "confidence": "high", "evidence": e["source_sentence"]})
    # Deduplicate
    seen = set(); out = []
    for c in constraints:
        k = (c["before"], c["after"], c["type"])
        if k not in seen:
            seen.add(k); out.append(c)
    return out

def state_history(events):
    history = defaultdict(list)
    for e in events:
        for actor in e["actor_ids"]:
            for tr in e["transition_markers"]:
                history[actor].append({
                    "event_id": e["event_id"],
                    "transition": tr["state"],
                    "marker": tr["marker"],
                    "source": e["source_sentence"],
                })
    return dict(history)

def build_v4(points):
    events = make_events(points)
    return {
        "experiment": "EXP-V4",
        "hypothesis": "A persistent semantic substrate can preserve evolving temporal state without collapsing uncertain or relative time into invented absolute dates.",
        "policy": {
            "temporal_claims_are_conservative": True,
            "absolute_dates_are_never_invented": True,
            "sequence_is_weak_unless_explicit": True,
            "state_history_is_append_only": True,
            "no_llm": True,
            "no_embeddings": True,
            "no_vector_db": True,
            "no_graph_db": True,
        },
        "events": events,
        "temporal_constraints": temporal_constraints(events),
        "state_history": state_history(events),
        "metrics": {
            "events": len(events),
            "anchored_events": sum(e["temporal_status"] == "anchored" for e in events),
            "unanchored_events": sum(e["temporal_status"] == "unanchored" for e in events),
            "temporal_constraints": len(temporal_constraints(events)),
            "state_transition_events": sum(bool(e["transition_markers"]) for e in events),
        },
    }
