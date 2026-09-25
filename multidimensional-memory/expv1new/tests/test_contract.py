import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_small_corpus_contract():
    corpus = json.loads((ROOT / "tests/data/small_corpus.json").read_text())
    queries = json.loads((ROOT / "tests/data/small_queries.json").read_text())

    assert len(corpus["events"]) == 6
    assert all(event["event_id"] and event["text"] for event in corpus["events"])

    expected = {q["query_id"]: q["expected_event_ids"] for q in queries["queries"]}
    assert expected["Q001"] == ["E001"]
    assert expected["Q002"] == ["E005"]
    assert expected["Q003"] == ["E001", "E002", "E003", "E005"]
    assert expected["Q004"] == ["E006"]
