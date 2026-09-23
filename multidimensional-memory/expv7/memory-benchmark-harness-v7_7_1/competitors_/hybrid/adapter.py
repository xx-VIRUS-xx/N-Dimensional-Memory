import os
import json
import time
from competitors.bm25 import adapter as bm25_adapter
from competitors.dense import adapter as dense_adapter

def build(corpus_path, output_dir, config=None):
    os.makedirs(output_dir, exist_ok=True)
    bm25_dir = os.path.join(output_dir, "bm25_idx")
    dense_dir = os.path.join(output_dir, "dense_idx")
    
    res_b = bm25_adapter.build(corpus_path, bm25_dir, config)
    res_d = dense_adapter.build(corpus_path, dense_dir, config)
    
    if res_b["status"] == "SUCCESS" and res_d["status"] == "SUCCESS":
        return {"status": "SUCCESS", "num_events": res_b["num_events"]}
    return {"status": "FAILED", "error": f"BM25: {res_b}, Dense: {res_d}"}

def retrieve(query, k=5, index_dir=None, config=None):
    start_time = time.time()
    bm25_dir = os.path.join(index_dir, "bm25_idx")
    dense_dir = os.path.join(index_dir, "dense_idx")
    
    bm25_res = bm25_adapter.retrieve(query, k=k*2, index_dir=bm25_dir, config=config)
    dense_res = dense_adapter.retrieve(query, k=k*2, index_dir=dense_dir, config=config)
    
    if bm25_res["status"] != "EXECUTED" or dense_res["status"] != "EXECUTED":
        return {
            "query_id": config.get("query_id", "Q000") if config else "Q000",
            "condition": "hybrid",
            "status": "FAILED_SETUP",
            "evidence": [],
            "latency_ms": (time.time() - start_time) * 1000,
            "error": f"Sub-retriever failed. BM25: {bm25_res.get('error')}, Dense: {dense_res.get('error')}"
        }
        
    bm25_scores = {ev["event_id"]: ev["score"] for ev in bm25_res["evidence"]}
    dense_scores = {ev["event_id"]: ev["score"] for ev in dense_res["evidence"]}
    
    # Reciprocal Rank Fusion (RRF)
    all_event_ids = set(bm25_scores.keys()).union(set(dense_scores.keys()))
    bm25_ranks = {ev["event_id"]: r + 1 for r, ev in enumerate(bm25_res["evidence"])}
    dense_ranks = {ev["event_id"]: r + 1 for r, ev in enumerate(dense_res["evidence"])}
    
    rrf_k = 60
    hybrid_scores = []
    for event_id in all_event_ids:
        r_b = bm25_ranks.get(event_id, 9999)
        r_d = dense_ranks.get(event_id, 9999)
        score = (1.0 / (rrf_k + r_b)) + (1.0 / (rrf_k + r_d))
        hybrid_scores.append({"event_id": str(event_id), "score": float(score)})
        
    hybrid_scores.sort(key=lambda x: x["score"], reverse=True)
    top_k = hybrid_scores[:k]
    
    latency = (time.time() - start_time) * 1000
    return {
        "query_id": config.get("query_id", "Q000") if config else "Q000",
        "condition": "hybrid",
        "status": "EXECUTED",
        "evidence": top_k,
        "latency_ms": round(latency, 2)
    }
