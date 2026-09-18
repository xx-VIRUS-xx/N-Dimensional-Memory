import json
from pathlib import Path
from shared_memory_v61 import SharedMemory, Observation

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "benchmark_v6_1.json"
OUT = ROOT / "results" / "v6.1.shared_memory.json"


def run():
    benchmark = json.loads(DATA.read_text())
    store = SharedMemory()
    for item in benchmark["updates"]:
        store.append(Observation(**item))

    result = {
        "benchmark": benchmark["name"],
        "state": store.state(benchmark["proposition_id"]),
        "snapshot_round_trip": SharedMemory.from_snapshot(store.snapshot()).state(
            benchmark["proposition_id"]
        ),
    }
    OUT.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    run()
