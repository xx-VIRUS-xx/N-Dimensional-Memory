from __future__ import annotations
import json, math, re, time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVAL_CORPUS = ROOT / 'data' / 'conversation_v7_7_evaluator.jsonl'
PUBLIC_BENCH = ROOT / 'data' / 'benchmark_v7_7_public_repaired.json'
RESULTS = ROOT / 'results' / 'retrieval'
TOKEN_RE = re.compile(r'[A-Za-z0-9_+#.-]+')

def load_events():
    return [json.loads(x) for x in EVAL_CORPUS.read_text().splitlines() if x.strip()]

def load_queries():
    return json.loads(PUBLIC_BENCH.read_text())['queries']

def tokenize(text):
    return [t.lower() for t in TOKEN_RE.findall(text)]

def bm25_scores(query, docs, k1=1.5, b=0.75):
    qset = set(tokenize(query)); N = len(docs)
    df = Counter(); doc_terms=[]; lengths=[]
    for d in docs:
        terms=tokenize(d['text']); c=Counter(terms); doc_terms.append(c); lengths.append(len(terms))
        df.update(c.keys())
    avgdl=sum(lengths)/max(1,N); scores=[]
    for i,c in enumerate(doc_terms):
        dl=lengths[i]; s=0.0
        for term in qset:
            if term not in c: continue
            idf=math.log(1+(N-df[term]+0.5)/(df[term]+0.5)); tf=c[term]
            s += idf*(tf*(k1+1))/(tf+k1*(1-b+b*dl/max(avgdl,1e-9)))
        scores.append(s)
    return scores

def tfidf_scores(query, docs):
    q=Counter(tokenize(query)); ds=[Counter(tokenize(d['text'])) for d in docs]; N=len(docs)
    df=Counter()
    for c in ds: df.update(c.keys())
    def vec(c):
        return {t:tf*(math.log((N+1)/(df[t]+1))+1) for t,tf in c.items()}
    qv=vec(q); qn=math.sqrt(sum(v*v for v in qv.values())) or 1.0; out=[]
    for c in ds:
        dv=vec(c); dot=sum(qv.get(t,0.0)*v for t,v in dv.items()); dn=math.sqrt(sum(v*v for v in dv.values())) or 1.0
        out.append(dot/(qn*dn))
    return out

def normalize(scores):
    if not scores: return scores
    lo,hi=min(scores),max(scores)
    return [0.0]*len(scores) if hi==lo else [(x-lo)/(hi-lo) for x in scores]

def rank_events(query, events, condition, top_k=24):
    docs=[e for e in events if e['conversation_id']==query['conversation_id']]
    if condition=='raw': raw=[0.0]*len(docs); top_k=len(docs)
    elif condition=='bm25': raw=bm25_scores(query['question'],docs)
    elif condition=='semantic': raw=tfidf_scores(query['question'],docs)
    elif condition=='hybrid':
        a=normalize(bm25_scores(query['question'],docs)); b=normalize(tfidf_scores(query['question'],docs)); raw=[(x+y)/2 for x,y in zip(a,b)]
    else: raise ValueError(condition)
    ranked=sorted(zip(docs,raw), key=lambda x:(-x[1],x[0]['timestamp']))
    return [{**{k:d[k] for k in ('event_id','conversation_id','timestamp','speaker','text')},'score':float(s)} for d,s in ranked[:top_k]]

def run(condition, top_k=24):
    events=load_events(); queries=load_queries(); results=[]
    for q in queries:
        t=time.perf_counter(); retrieved=rank_events(q,events,condition,top_k)
        results.append({'query_id':q['query_id'],'conversation_id':q['conversation_id'],'category':q['category'],'question':q['question'],'retrieved':retrieved,'retrieval_latency_ms':(time.perf_counter()-t)*1000})
    return {'benchmark':'EXP-V7.7-Repaired','condition':condition.upper(),'top_k':top_k,'query_count':len(queries),'implementation':{'raw':'complete conversation, no retrieval','bm25':'in-process BM25','semantic':'TF-IDF cosine proxy (not neural embeddings)','hybrid':'50/50 normalized BM25 + TF-IDF cosine'}[condition],'results':results}

def write_result(condition, top_k=24):
    RESULTS.mkdir(parents=True,exist_ok=True); out=run(condition,top_k); path=RESULTS/f'{condition}.json'; path.write_text(json.dumps(out,indent=2)); print(f'Wrote {path}'); print(f'Queries: {len(out["results"])}'); return path
