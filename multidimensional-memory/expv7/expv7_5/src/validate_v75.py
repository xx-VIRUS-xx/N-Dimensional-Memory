import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    for p in (ROOT/"data").glob("*_unlabeled.jsonl"):
        rows=[json.loads(x) for x in p.read_text().splitlines() if x.strip()]
        assert len(rows)==500, (p,len(rows))
        assert all("kind" not in r for r in rows)
    gold=json.loads((ROOT/"data/gold_annotations.json").read_text())
    assert sum(len(v) for v in gold.values())==120
    queries=json.loads((ROOT/"data/future_queries.json").read_text())
    assert queries
    print("V7.5 validation passed")
if __name__ == "__main__": main()
