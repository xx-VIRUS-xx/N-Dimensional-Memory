import argparse,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument("--corpus",default="benchmark/datasets/v7_7_1/corpus.jsonl");p.add_argument("--gold",default="benchmark/datasets/v7_7_1/gold_query_evidence.json");a=p.parse_args()
corpus={json.loads(x)["event_id"] for x in Path(a.corpus).read_text().splitlines() if x.strip()}
gold=json.loads(Path(a.gold).read_text())
errors=[]
for q in gold:
 ids=q.get("required_event_ids",[])
 missing=[i for i in ids if i not in corpus]
 if not ids or missing: errors.append({"query_id":q.get("query_id"),"missing":missing,"empty":not ids})
if errors:
 print(json.dumps({"status":"FAIL","errors":errors},indent=2)); raise SystemExit(2)
print(json.dumps({"status":"PASS","queries":len(gold)},indent=2))
