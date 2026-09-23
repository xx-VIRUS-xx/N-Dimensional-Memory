import os
import json
import time
import numpy as np
from sentence_transformers import SentenceTransformer

_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def build(corpus_path, output_dir, config=None):
    os.makedirs(output_dir, exist_ok=True)
    events = []
    texts = []
    
    with open(corpus_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            item = json.loads(line)
            events.append(item)
            text = item.get("text", "") or item.get("content", "") or json.dumps(item)
            texts.append(text)
            
    model = get_model()
    embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
    
    with open(os.path.join(output_dir, "dense_corpus.json"), "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2)
        
    np.save(os.path.join(output_dir, "dense_embeddings.npy"), embeddings)
    
    return {"status": "SUCCESS", "num_events": len(events)}

def retrieve(query, k=5, index_dir=None, config=None):
    start_time = time.time()
    corpus_file = os.path.join(index_dir, "dense_corpus.json")
    emb_file = os.path.join(index_dir, "dense_embeddings.npy")
    
    if not os.path.exists(corpus_file) or not os.path.exists(emb_file):
        return {
            "query_id": config.get("query_id", "Q000") if config else "Q000",
            "condition": "dense",
            "status": "FAILED_SETUP",
            "evidence": [],
            "latency_ms": (time.time() - start_time) * 1000,
            "error": "Dense index files missing."
        }
        
    with open(corpus_file, "r", encoding="utf-8") as f:
        events = json.load(f)
    embeddings = np.load(emb_file)
    
    model = get_model()
    q_emb = model.encode([query], convert_to_numpy=True, normalize_embeddings=True)[0]
    
    scores = np.dot(embeddings, q_emb)
    
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
        "condition": "dense",
        "status": "EXECUTED",
        "evidence": top_k,
        "latency_ms": round(latency, 2)
    }
