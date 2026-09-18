from src.relations_v3 import derive_relationships


def p(cid, surface, dims, evidence=("S",), related=()):
    return {
        "canonical_id": cid,
        "surfaces": [surface],
        "dimensions": {"union": list(dims)},
        "evidence": list(evidence),
        "related_point_ids": list(related),
    }


def test_actor_performs_action():
    rs = derive_relationships([
        p("p1", "Rahul", ["actor", "subject"]),
        p("p2", "plays", ["verb", "action"]),
    ])
    assert any(r["type"] == "performs" and r["source"] == "p1" and r["target"] == "p2" for r in rs)


def test_action_acts_on_object():
    rs = derive_relationships([
        p("p1", "play", ["verb", "action"]),
        p("p2", "football", ["noun", "object"]),
    ])
    assert any(r["type"] == "acts_on" for r in rs)


def test_related_edge_is_preserved():
    rs = derive_relationships([
        p("p1", "play", ["verb", "action"], related=("p2",)),
        p("p2", "play football", ["verb", "action", "object"]),
    ])
    assert any(r["type"] == "granularity_related" for r in rs)


def test_no_relation_without_shared_evidence():
    rs = derive_relationships([
        p("p1", "Rahul", ["actor", "subject"], evidence=("A",)),
        p("p2", "plays", ["verb", "action"], evidence=("B",)),
    ])
    assert not rs
