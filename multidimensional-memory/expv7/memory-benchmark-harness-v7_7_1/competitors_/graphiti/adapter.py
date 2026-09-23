def build(corpus_path, output_dir, config=None):
    raise NotImplementedError("GRAPH SYSTEM RULE: Official Graphiti Docker + Neo4j/FalkorDB engine is required. Setup incomplete due to missing container service / upstream dependencies.")

def retrieve(query, k=5, index_dir=None, config=None):
    return {
        "query_id": config.get("query_id", "Q000") if config else "Q000",
        "condition": "graphiti",
        "status": "FAILED_SETUP",
        "evidence": [],
        "latency_ms": 0.0,
        "error": "GRAPH SYSTEM RULE: Official Graphiti container service required."
    }
