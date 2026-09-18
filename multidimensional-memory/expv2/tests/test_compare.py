from src.compare import compare_models, metrics


def docs():
    return {
        "claude": {"conversation_id": "x", "points": [
            {"surface": "Rahul", "dimensions": ["noun", "subject", "actor"]},
            {"surface": "football", "dimensions": ["noun", "object", "activity"]},
        ]},
        "codex": {"conversation_id": "x", "points": [
            {"surface": "Rahul", "dimensions": ["noun", "subject", "actor"]},
            {"surface": "football", "dimensions": ["noun", "object"]},
        ]},
        "copilot": {"conversation_id": "x", "points": [
            {"surface": "Rahul", "dimensions": ["noun", "subject", "actor"]},
            {"surface": "football", "dimensions": ["noun", "object", "activity"]},
        ]},
    }


def test_common_dimensions():
    canonical, models = compare_models(docs())
    rahul = next(x for x in canonical if x["surface"] == "rahul")
    football = next(x for x in canonical if x["surface"] == "football")
    assert set(rahul["dimensions"]["common"]) == {"noun", "subject", "actor"}
    assert set(football["dimensions"]["common"]) == {"noun", "object"}


def test_metrics():
    canonical, models = compare_models(docs())
    m = metrics(canonical, models)
    assert m["point_coverage"] == 1.0
