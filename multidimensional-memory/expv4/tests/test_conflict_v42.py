from src.temporal_v4 import build_v4
from src.conflict_v42 import build_v42


def points(sentences):
    out = []
    for i, sentence in enumerate(sentences):
        out.extend([
            {"canonical_id": "rahul", "dimensions": {"union": ["actor", "subject"]}, "evidence": [sentence]},
            {"canonical_id": f"state_{i}", "dimensions": {"union": ["action", "state", "verb"]}, "evidence": [sentence]},
        ])
    return out


def test_ordered_opposites_are_evolution():
    r = build_v42(build_v4(points([
        "Rahul started playing football.",
        "Rahul stopped playing football during summer.",
        "Rahul resumed playing football later.",
    ])))
    assert r["metrics"]["evolutions"] >= 2
    assert r["metrics"]["potential_conflicts"] == 0


def test_history_is_preserved_and_not_resolved():
    r = build_v42(build_v4(points([
        "Rahul started playing football.",
        "Rahul stopped playing football.",
    ])))
    assert r["policy"]["preserve_both"] is True
    assert r["policy"]["no_winner_selected"] is True
    values = [u["transition"] for h in r["state_histories"].values() for u in h]
    assert "began" in values and "ended" in values


def test_same_state_is_not_a_conflict():
    r = build_v42(build_v4(points([
        "Rahul started playing football.",
        "Rahul started playing football again.",
    ])))
    assert r["metrics"]["potential_conflicts"] == 0
