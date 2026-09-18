import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_corpus_size_and_views():
    rows=[json.loads(x) for x in open(ROOT/'data/conversation_v7_4.jsonl')]
    unl=[json.loads(x) for x in open(ROOT/'data/conversation_v7_4_unlabeled.jsonl')]
    assert len(rows)==1200 and len(unl)==1200
    assert all('kind' in x for x in rows)
    assert all('kind' not in x for x in unl)
def test_gold_signal_count():
    g=json.load(open(ROOT/'data/benchmark_v7_4.json'))
    assert len(g['signal_event_ids'])==20
    assert len(set(g['signal_event_ids']))==20
def test_no_simple_boilerplate_tell():
    rows=[json.loads(x) for x in open(ROOT/'data/conversation_v7_4.jsonl')]
    phrases={}
    for r in rows:
        for phrase in ['routine progress and no final decision','no final decision','routine progress']:
            phrases.setdefault(phrase,[0,0]); phrases[phrase][r['kind']=='signal']+=1
    assert all(v[0] and v[1] for v in phrases.values())
