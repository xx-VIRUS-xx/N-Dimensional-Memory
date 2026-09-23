import os
import json
import time

def build(corpus_path, output_dir, config=None):
    """
    Build raw corpus index (simple copy / metadata mapping for raw pass-through).
    """
    os.makedirs(output_dir, exist_ok=True)
    with open(corpus_path, "r", encoding="utf-8") as f:
        events = [json.loads(line) for line in f if line.strip()]
    
    index_file = os.path.join(output_dir, "raw_corpus.json")
    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2)
    
    return {"status": "SUCCESS", "num_events": len(events)}

def retrieve(query, k=5, index_dir=None, config=None):
    """
    Retrieve top-k events based on raw text scan.
    Returns normalized output schema.
    """
    start_time = time.time()
    index_file = os.path.join(index_dir, "raw_corpus.json")
    if not os.path.exists(index_file):
        return {
            "query_id": config.get("query_id", "Q_UNKNOWN") if config else "Q_UNKNOWN",
            "condition": "raw",
            "status": "FAILED_SETUP",
            "evidence": [],
            "latency_ms": (time.time() - start_time) * 1000,
            "error": "Index file not found."
        }
    
    with open(index_file, "r", encoding="utf-8") as f:
        events = json.load(f)
    
    scored_events = []
    query_terms = set(query.lower().split())
    for ev in events:
        text = ev.get("text", "") or ev.get("content", "") or json.dumps(ev)
        text_lower = text.lower()
        score = sum(1.0 for term in query_terms if term in text_lower)
        event_id = ev.get("event_id") or ev.get("id")
        if event_id:
            scored_events.append({"event_id": str(event_id), "score": float(score)})
            
    scored_events.sort(key=lambda x: x["score"], reverse=True)
    top_k = scored_events[:k]
    
    latency = (time.time() - start_time) * 1000
    return {
        "query_id": config.get("query_id", "Q000") if config else "Q000",
        "condition": "raw",
        "status": "EXECUTED",
        "evidence": top_k,
        "latency_ms": round(latency, 2)
    }
