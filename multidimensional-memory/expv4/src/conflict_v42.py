"""EXP-V4.2: temporal conflict resolution without destructive resolution."""
from collections import defaultdict
from .evolution_v41 import event_state_updates, norm

# Explicitly opposite values. Extend only when evidence semantics justify it.
OPPOSITES = {
    ("playing", "active"): ("playing", "inactive"),
    ("playing", "inactive"): ("playing", "active"),
    ("plan", "changed"): ("plan", "unchanged"),
}


def _index_events(v4_result):
    return {e["event_id"]: e for e in v4_result.get("events", [])}


def _explicit_order(a, b, constraints):
    for c in constraints:
        if c["before"] == a["event_id"] and c["after"] == b["event_id"]:
            return c["type"], c["confidence"]
    return None, None


def classify_updates(v4_result):
    updates = event_state_updates(v4_result.get("events", []))
    by_key = defaultdict(list)
    for u in updates:
        by_key[(u["subject_id"], u["target"])].append(u)

    events = _index_events(v4_result)
    constraints = v4_result.get("temporal_constraints", [])
    observations = []

    for key, seq in by_key.items():
        for prev, cur in zip(seq, seq[1:]):
            opposite = OPPOSITES.get((prev["target"], prev["value"]))
            if not opposite or opposite != (cur["target"], cur["value"]):
                continue

            # Ordered opposite states are evolution, not contradiction.
            order_type, order_conf = _explicit_order(prev, cur, constraints)
            if order_type:
                kind = "evolution"
                reason = "opposing states have explicit temporal order"
            elif cur["sequence"] > prev["sequence"]:
                kind = "evolution"
                reason = "opposing states occur in source sequence; ordering is weak"
            else:
                kind = "potential_conflict"
                reason = "opposing observations lack temporal ordering evidence"

            observations.append({
                "subject_id": key[0],
                "target": key[1],
                "from": prev["value"],
                "to": cur["value"],
                "event_from": prev["event_id"],
                "event_to": cur["event_id"],
                "kind": kind,
                "reason": reason,
                "ordering": {
                    "type": order_type or "source_sequence",
                    "confidence": order_conf or "medium",
                },
                "resolution": "preserve_both",
                "evidence": [prev["source"], cur["source"]],
            })

    return observations


def build_v42(v4_result):
    observations = classify_updates(v4_result)
    histories = v4_result.get("state_history", {})
    return {
        "experiment": "EXP-V4.2",
        "hypothesis": "Temporal ordering can distinguish legitimate state evolution from potentially conflicting observations while preserving every observation.",
        "policy": {
            "history_is_append_only": True,
            "preserve_both": True,
            "evolution_is_not_conflict": True,
            "potential_conflict_is_not_auto_resolved": True,
            "no_winner_selected": True,
            "absolute_dates_never_invented": True,
        },
        "state_histories": histories,
        "state_relationships": observations,
        "metrics": {
            "state_relationships": len(observations),
            "evolutions": sum(x["kind"] == "evolution" for x in observations),
            "potential_conflicts": sum(x["kind"] == "potential_conflict" for x in observations),
            "preserved_observations": len(v4_result.get("events", [])),
        },
    }
