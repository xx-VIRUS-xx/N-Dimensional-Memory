#!/usr/bin/env python3
import argparse,json,time
from pathlib import Path
from .common import load_queries, RESULTS

def load_memory(path):
    d=json.loads(Path(path).read_text())
    if isinstance(d,list): return d
    for k in ('records','memory','items'):
        if isinstance(d.get(k),list): return d[k]
    raise ValueError('Memory JSON must contain a list or records/memory/items')

def source_ids(r):
    out=[]
    for k in ('source_event_ids','source_ids','event_ids','source_event_id'):
        v=r.get(k)
        if isinstance(v,str): out.append(v)
        elif isinstance(v,list): out.extend(x for x in v if isinstance(x,str))
    return set(out)

def main():
    p=argparse.ArgumentParser(); p.add_argument('--memory',required=True); a=p.parse_args()
    mem=load_memory(a.memory); results=[]
    for q in load_queries():
        t=time.perf_counter(); relevant=[r for r in mem if q['conversation_id'] in str(r.get('conversation_id',r.get('conversation_ids','')))] or mem
        ev=sorted({x for r in relevant for x in source_ids(r)})
        results.append({'query_id':q['query_id'],'conversation_id':q['conversation_id'],'category':q['category'],'question':q['question'],'memory_records_available':len(relevant),'evidence_event_ids':ev,'retrieval_latency_ms':(time.perf_counter()-t)*1000})
    RESULTS.mkdir(parents=True,exist_ok=True); out={'benchmark':'EXP-V7.7-Repaired','condition':'MEMORY','memory_path':str(Path(a.memory).resolve()),'query_count':len(results),'results':results}; path=RESULTS/'memory.json'; path.write_text(json.dumps(out,indent=2)); print(f'Wrote {path}')
if __name__=='__main__': main()
