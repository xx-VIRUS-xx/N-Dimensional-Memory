import os
import json
from competitors.graphiti.adapter import retrieve

def run_smoke_test():
    res = retrieve("synthetic query", k=2, index_dir="/tmp/dummy", config={"query_id": "Q_SMOKE_GRAPHITI"})
    assert res["status"] == "FAILED_SETUP", f"Expected FAILED_SETUP status, got {res['status']}"
    print("Graphiti competitor setup state recorded successfully (FAILED_SETUP as required when upstream missing).")

if __name__ == "__main__":
    run_smoke_test()
