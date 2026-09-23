import os
import json
import tempfile
from competitors.hybrid.adapter import build, retrieve

def run_smoke_test():
    synthetic_corpus = [
        {"event_id": "C01E001", "text": "The solar panel energy output was recorded yesterday."},
        {"event_id": "C01E002", "text": "Synthetic test event for BM25 and Dense hybrid search integration."},
        {"event_id": "C01E003", "text": "Unrelated chocolate birthday cake recipe."}
    ]
    
    with tempfile.TemporaryDirectory() as tmpdir:
        corpus_path = os.path.join(tmpdir, "synthetic_corpus.jsonl")
        index_dir = os.path.join(tmpdir, "index")
        
        with open(corpus_path, "w", encoding="utf-8") as f:
            for item in synthetic_corpus:
                f.write(json.dumps(item) + "\n")
                
        build_res = build(corpus_path, index_dir)
        assert build_res["status"] == "SUCCESS", f"Build failed: {build_res}"
        
        res = retrieve("hybrid search integration", k=2, index_dir=index_dir, config={"query_id": "Q_SMOKE_HYBRID"})
        assert res["status"] == "EXECUTED", f"Retrieve status expected EXECUTED, got {res['status']}"
        assert len(res["evidence"]) > 0, "Expected evidence items"
        assert res["evidence"][0]["event_id"] == "C01E002"
        print("Hybrid competitor smoke test PASSED.")

if __name__ == "__main__":
    run_smoke_test()
