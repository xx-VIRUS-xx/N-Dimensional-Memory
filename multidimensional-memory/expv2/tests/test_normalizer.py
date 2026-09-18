from src.normalizer import canonical_surface, normalize_dimensions


def test_play_inflections_merge():
    assert canonical_surface("plays") == "play"
    assert canonical_surface("playing") == "play"


def test_dimensions_are_case_normalized():
    assert normalize_dimensions(["Noun", "Subject", "Actor"]) == {"noun", "subject", "actor"}
