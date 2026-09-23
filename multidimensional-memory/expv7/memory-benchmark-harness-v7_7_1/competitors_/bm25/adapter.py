import os
import sys
import json
import re
import time
from rank_bm25 import BM25Okapi

def _tokenize(text):
    return re.findall(r'\w+', text.lower())

def build(corpus_path, output_dir, config=None):
    os.makedirs(output_dir, exist_ok=True)
    events = []
    
    with open(corpus_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            item = json.loads(line)
            events.append(item)
            
    with open(os.path.join(output_dir, "bm25_corpus.json"), "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2)
        
    return {"status": "SUCCESS", "num_events": len(events)}

def retrieve(query, k=5, index_dir=None, config=None):
    start_time = time.time()
    corpus_file = os.path.join(index_dir, "bm25_corpus.json")
    if not os.path.exists(corpus_file):
        return {
            "query_id": config.get("query_id", "Q000") if config else "Q000",
            "condition": "bm25",
            "status": "FAILED_SETUP",
            "evidence": [],
            "latency_ms": (time.time() - start_time) * 1000,
            "error": "BM25 corpus file missing."
        }
        
    with open(corpus_file, "r", encoding="utf-8") as f:
        events = json.load(f)
        
    corpus_tokens = [_tokenize(ev.get("text", "") or ev.get("content", "") or json.dumps(ev)) for ev in events]
    bm25 = BM25Okapi(corpus_tokens)
    
    tokenized_query = _tokenize(query)
    scores = bm25.get_scores(tokenized_query)
    
    scored_events = []
    for idx, score in enumerate(scores):
        event_id = events[idx].get("event_id") or events[idx].get("id")
        if event_id:
            scored_events.append({"event_id": str(event_id), "score": float(score)})
            
    scored_events.sort(key=lambda x: x["score"], reverse=True)
    top_k = scored_events[:k]
    
    latency = (time.time() - start_time) * 1000
    return {
        "query_id": config.get("query_id", "Q000") if config else "Q000",
        "condition": "bm25",
        "status": "EXECUTED",
        "evidence": top_k,
        "latency_ms": round(latency, 2)
    }
