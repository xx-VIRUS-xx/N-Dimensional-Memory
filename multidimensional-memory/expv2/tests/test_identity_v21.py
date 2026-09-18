from src.identity import classify_identity


def p(surface, dims):
    return {"surface": surface, "dimensions": dims}


def test_inflection_is_same():
    assert classify_identity(p("plays", ["verb", "action"]), p("playing", ["verb", "action"])) == "SAME"


def test_specific_phrase_is_related_not_same():
    assert classify_identity(p("play", ["verb", "action"]), p("play football", ["verb", "action", "object"])) == "RELATED"


def test_unrelated_points_are_distinct():
    assert classify_identity(p("Rahul", ["noun", "actor"]), p("football", ["noun", "object", "activity"])) == "DISTINCT"


def test_qualifier_creates_related_point():
    assert classify_identity(p("team", ["noun", "object"]), p("new team", ["noun", "object", "target"])) == "RELATED"
