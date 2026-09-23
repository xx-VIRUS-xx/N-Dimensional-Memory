def build(corpus_path, output_dir, config=None):
    raise NotImplementedError("GRAPH SYSTEM RULE: Real Microsoft GraphRAG engine is required. Setup incomplete due to missing upstream package / API keys.")

def retrieve(query, k=5, index_dir=None, config=None):
    return {
        "query_id": config.get("query_id", "Q000") if config else "Q000",
        "condition": "graphrag",
        "status": "FAILED_SETUP",
        "evidence": [],
        "latency_ms": 0.0,
        "error": "GRAPH SYSTEM RULE: Real Microsoft GraphRAG engine required."
    }
