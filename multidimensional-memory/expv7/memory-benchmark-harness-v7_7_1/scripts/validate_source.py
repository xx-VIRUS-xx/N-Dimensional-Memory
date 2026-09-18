import argparse,json,hashlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument("--corpus",default="benchmark/datasets/v7_7_1/corpus.jsonl");a=p.parse_args()
x=Path(a.corpus)
if not x.exists(): raise SystemExit(f"Missing corpus: {x}")
ids=[]
for n,line in enumerate(x.read_text().splitlines(),1):
 o=json.loads(line)
 for k in ("event_id","conversation_id","timestamp","speaker","text"):
  if k not in o: raise SystemExit(f"line {n}: missing {k}")
 ids.append(o["event_id"])
if len(ids)!=len(set(ids)): raise SystemExit("Duplicate event_id")
h=hashlib.sha256(x.read_bytes()).hexdigest()
print(json.dumps({"status":"PASS","events":len(ids),"sha256":h},indent=2))
