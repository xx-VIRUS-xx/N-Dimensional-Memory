import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_benchmark_has_cases_and_categories():
    cases = json.loads((ROOT / 'data' / 'benchmark_v7.json').read_text())
    assert len(cases) >= 7
    categories = {c['category'] for c in cases}
    assert {'historical_recall', 'action_outcome', 'temporal_state', 'ambiguity', 'contradiction', 'negative_knowledge', 'provenance'} <= categories


def test_conditions_are_fixed():
    conditions = {'RAW', 'RAG', 'V6', 'V6+RAW'}
    assert len(conditions) == 4
