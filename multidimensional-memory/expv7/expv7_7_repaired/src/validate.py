import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "data/conversation_v7_7_evaluator.jsonl"
GOLD = ROOT / "data/benchmark_v7_7_gold_repaired.json"

def load_corpus():
    rows=[json.loads(x) for x in CORPUS.read_text().splitlines() if x.strip()]
    return {r["event_id"]: r for r in rows}

def main():
    events=load_corpus(); gold=json.loads(GOLD.read_text())
    assert len(events)==1200, len(events)
    convs={e["conversation_id"] for e in events.values()}
    assert len(convs)==12, len(convs)
    durable=set(gold["gold_durable_event_ids"])
    assert len(durable)==216, len(durable)
    assert all(i in events for i in durable)
    assert len(gold["queries"])==96
    for q in gold["queries"]:
        assert q["required_event_ids"]
        assert q["conversation_id"] in convs
        for eid in q["required_event_ids"]:
            assert eid in events, (q["query_id"], eid)
            assert eid in durable, (q["query_id"], eid)
            assert events[eid]["conversation_id"] == q["conversation_id"], (q["query_id"],eid)
            assert "routine progress" not in events[eid]["text"].lower(), (q["query_id"],eid)
    print("V7.7 REPAIRED DATASET: PASS")
    print(f"events={len(events)} conversations={len(convs)} durable={len(durable)} queries={len(gold['queries'])}")

if __name__ == "__main__": main()
