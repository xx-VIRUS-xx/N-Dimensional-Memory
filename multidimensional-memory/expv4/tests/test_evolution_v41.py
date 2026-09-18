from src.temporal_v4 import build_v4
from src.evolution_v41 import build_v41


def sample():
    return [
        {"canonical_id":"rahul","dimensions":{"union":["actor","subject"]},"evidence":["Rahul started playing football."]},
        {"canonical_id":"start","dimensions":{"union":["action","state","verb"]},"evidence":["Rahul started playing football."]},
        {"canonical_id":"rahul","dimensions":{"union":["actor","subject"]},"evidence":["Rahul stopped playing football during summer."]},
        {"canonical_id":"stop","dimensions":{"union":["action","state","verb"]},"evidence":["Rahul stopped playing football during summer."]},
        {"canonical_id":"rahul","dimensions":{"union":["actor","subject"]},"evidence":["Rahul resumed playing football later."]},
        {"canonical_id":"resume","dimensions":{"union":["action","state","verb"]},"evidence":["Rahul resumed playing football later."]},
    ]

def test_preserves_state_history():
    r = build_v41(build_v4(sample()))
    assert len(r["state_updates"]) == 3
    assert r["policy"]["history_is_append_only"] is True

def test_detects_evolution_without_deleting_previous_state():
    r = build_v41(build_v4(sample()))
    values = [u["value"] for h in r["state_histories"] for u in h["updates"]]
    assert "active" in values and "inactive" in values
    assert len(r["contradictions"]) >= 1

def test_does_not_auto_resolve():
    r = build_v41(build_v4(sample()))
    assert all(c["resolution"] == "preserve_both" for c in r["contradictions"])
