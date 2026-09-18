from src.conflict_v43 import build_v43


def event(event_id, seq, value, sentence):
    return {
        "event_id": event_id,
        "sequence": seq,
        "actor_ids": ["rahul"],
        "source_sentence": sentence,
        "transition_markers": [{"marker": "state", "state": value}],
    }


def result(events, constraints=None):
    return build_v43({"events": events, "temporal_constraints": constraints or []})


def test_explicit_temporal_order_is_evolution():
    r = result(
        [event("e1", 1, "started", "Rahul started playing."), event("e2", 2, "stopped", "Rahul stopped playing later.")],
        [{"before": "e1", "after": "e2", "type": "explicit_after", "confidence": "high"}],
    )
    # event_state_updates maps began/ended to active/inactive.
    assert r["metrics"]["evolutions"] == 1
    assert r["metrics"]["potential_conflicts"] == 0


def test_unordered_opposites_are_potential_conflict():
    r = result(
        [event("e1", 1, "started", "Rahul started playing."), event("e2", 2, "stopped", "Rahul stopped playing.")]
    )
    assert r["metrics"]["potential_conflicts"] == 1
    assert r["metrics"]["evolutions"] == 0
    assert r["policy"]["preserve_both"] is True


def test_source_sequence_alone_does_not_prove_evolution():
    r = result(
        [event("e1", 1, "started", "Rahul started playing."), event("e2", 2, "stopped", "Rahul stopped playing.")],
        [{"before": "e1", "after": "e2", "type": "sequence", "confidence": "medium"}],
    )
    assert r["metrics"]["potential_conflicts"] == 1
    assert r["metrics"]["evolutions"] == 0
