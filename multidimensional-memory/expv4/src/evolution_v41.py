"""EXP-V4.1: append-only evolving state and contradiction detection."""
from collections import defaultdict
import re

STATE_MARKERS = {
    "stopped": ("playing", "inactive"),
    "started": ("playing", "active"),
    "resumed": ("playing", "active"),
    "changed": ("plan", "changed"),
    "bought": ("instrument", "owned"),
    "joined": ("team", "member"),
}

OPPOSITES = {
    ("playing", "active"): ("playing", "inactive"),
    ("playing", "inactive"): ("playing", "active"),
}

def norm(s):
    return re.sub(r"\s+", " ", s.lower().strip())

def event_state_updates(events):
    updates = []
    for e in events:
        for tr in e.get("transition_markers", []):
            marker = tr["marker"]
            state = tr["state"]
            subject = None
            for aid in e.get("actor_ids", []):
                subject = aid
                break
            if not subject:
                continue
            target, value = STATE_MARKERS.get(marker, (marker, state))
            updates.append({
                "event_id": e["event_id"],
                "sequence": e["sequence"],
                "subject_id": subject,
                "target": target,
                "value": value,
                "marker": marker,
                "source": e["source_sentence"],
                "time_anchors": e.get("time_anchors", []),
            })
    return updates

def detect_contradictions(updates):
    contradictions = []
    by_key = defaultdict(list)
    for u in updates:
        by_key[(u["subject_id"], u["target"])].append(u)
    for key, seq in by_key.items():
        for prev, cur in zip(seq, seq[1:]):
            if (prev["target"], prev["value"]) in OPPOSITES and OPPOSITES[(prev["target"], prev["value"])] == (cur["target"], cur["value"]):
                contradictions.append({
                    "subject_id": key[0],
                    "target": key[1],
                    "from": prev["value"],
                    "to": cur["value"],
                    "event_from": prev["event_id"],
                    "event_to": cur["event_id"],
                    "kind": "state_transition",
                    "resolution": "preserve_both",
                    "evidence": [prev["source"], cur["source"]],
                })
    return contradictions

def build_v41(v4_result):
    updates = event_state_updates(v4_result["events"])
    contradictions = detect_contradictions(updates)
    histories = defaultdict(list)
    for u in updates:
        histories[(u["subject_id"], u["target"])].append(u)
    return {
        "experiment": "EXP-V4.1",
        "hypothesis": "An append-only temporal substrate can represent evolving state and detect contradictory state observations without overwriting prior memory.",
        "policy": {
            "history_is_append_only": True,
            "contradictions_are_preserved": True,
            "latest_state_does_not_delete_prior_state": True,
            "contradictions_are_not_auto_resolved": True,
            "no_absolute_dates_invented": True,
        },
        "state_updates": updates,
        "state_histories": [
            {"subject_id": k[0], "target": k[1], "updates": v}
            for k, v in histories.items()
        ],
        "contradictions": contradictions,
        "metrics": {
            "state_updates": len(updates),
            "state_histories": len(histories),
            "contradictions_or_transitions": len(contradictions),
        },
    }
