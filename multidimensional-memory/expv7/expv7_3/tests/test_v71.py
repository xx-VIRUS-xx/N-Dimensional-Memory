import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data'

def test_corpus_size():
    assert sum(1 for _ in (DATA/'conversation_v7_1.jsonl').open()) == 1200

def test_cases():
    b=json.loads((DATA/'benchmark_v7_1.json').read_text())
    assert len(b['cases']) == 8
    assert all(len(c['raw_event_ids']) >= 2 for c in b['cases'])

def test_rag_and_memory_materialized():
    assert (DATA/'rag_index.json').exists()
    assert (DATA/'rag_retrievals_v71.json').exists()
    m=json.loads((DATA/'v6_memory.json').read_text())
    assert len(m['memory']) > 20
    assert any(x['type']=='state_history' for x in m['memory'])

def test_rag_budget_is_bounded():
    r=json.loads((DATA/'rag_retrievals_v71.json').read_text())
    assert all(len(v) <= 6 for v in r.values())
