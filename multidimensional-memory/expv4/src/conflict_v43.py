"""EXP-V4.3: explicit temporal conflict benchmark.

V4.3 tightens V4.2: source order alone is not enough to declare evolution.
Explicit temporal evidence is required for an evolution classification.
Unordered opposing observations remain potential conflicts.
"""
from collections import defaultdict


def _state_updates(events):
    """Normalize V4 events and test fixtures into comparable state updates."""
    updates = []
    for event in events:
        subject_ids = event.get("actor_ids", [])
        for marker in event.get("transition_markers", []):
            name = marker.get("marker")
            state = marker.get("state")
            if not subject_ids or state is None:
                continue

            # V4 transition markers use semantic transition names; the benchmark
            # fixtures may use marker='state' with state='started'/'stopped'.
            if name == "state":
                mapped = {
                    "started": ("playing", "active"),
                    "resumed": ("playing", "active"),
                    "stopped": ("playing", "inactive"),
                    "active": ("playing", "active"),
                    "inactive": ("playing", "inactive"),
                }.get(state)
                if mapped is None:
                    continue
                target, value = mapped
            else:
                mapped = {
                    "started": ("playing", "active"),
                    "resumed": ("playing", "active"),
                    "stopped": ("playing", "inactive"),
                }.get(name)
                if mapped is None:
                    continue
                target, value = mapped

            updates.append({
                "event_id": event["event_id"],
                "sequence": event.get("sequence", 0),
                "subject_id": subject_ids[0],
                "target": target,
                "value": value,
                "source": event.get("source_sentence", ""),
            })
    return updates


def _explicit_order(a, b, constraints):
    for constraint in constraints:
        if constraint.get("before") == a["event_id"] and constraint.get("after") == b["event_id"]:
            if constraint.get("type") in {"explicit_after", "explicit_before"}:
                return constraint["type"], constraint.get("confidence", "high")
    return None, None


def classify_updates(v4_result):
    updates = _state_updates(v4_result.get("events", []))
    by_key = defaultdict(list)
    for update in updates:
        by_key[(update["subject_id"], update["target"])].append(update)

    opposites = {
        ("playing", "active"): ("playing", "inactive"),
        ("playing", "inactive"): ("playing", "active"),
    }

    relationships = []
    for key, sequence in by_key.items():
        sequence = sorted(sequence, key=lambda x: x["sequence"])
        for a, b in zip(sequence, sequence[1:]):
            if opposites.get((a["target"], a["value"])) != (b["target"], b["value"]):
                continue

            order_type, order_conf = _explicit_order(
                a, b, v4_result.get("temporal_constraints", [])
            )
            if order_type:
                kind = "evolution"
                reason = "opposing states have explicit temporal ordering evidence"
            else:
                kind = "potential_conflict"
                reason = "opposing observations have no explicit temporal ordering evidence"

            relationships.append({
                "subject_id": key[0],
                "target": key[1],
                "from": a["value"],
                "to": b["value"],
                "event_from": a["event_id"],
                "event_to": b["event_id"],
                "kind": kind,
                "reason": reason,
                "ordering": {
                    "type": order_type or "none",
                    "confidence": order_conf or "none",
                },
                "source_sequence": [a["sequence"], b["sequence"]],
                "resolution": "preserve_both",
                "evidence": [a["source"], b["source"]],
            })
    return relationships


def build_v43(v4_result):
    relationships = classify_updates(v4_result)
    return {
        "experiment": "EXP-V4.3",
        "hypothesis": "Opposing observations can be classified as evolution only when explicit temporal evidence orders them; otherwise they remain potential conflicts.",
        "policy": {
            "history_is_append_only": True,
            "preserve_both": True,
            "explicit_order_required_for_evolution": True,
            "source_sequence_is_not_sufficient_for_evolution": True,
            "potential_conflict_is_not_auto_resolved": True,
            "no_winner_selected": True,
        },
        "state_relationships": relationships,
        "metrics": {
            "state_relationships": len(relationships),
            "evolutions": sum(x["kind"] == "evolution" for x in relationships),
            "potential_conflicts": sum(x["kind"] == "potential_conflict" for x in relationships),
            "preserved_observations": len(v4_result.get("events", [])),
        },
    }
