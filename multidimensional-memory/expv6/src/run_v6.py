import json
from pathlib import Path
from memory_v6 import AgentObservation, merge_observations, summarize

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "benchmark_v6.json"
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)

raw = json.loads(DATA.read_text())
all_results = {}
for name, rows in raw["benchmarks"].items():
    observations = [AgentObservation(**row) for row in rows]
    memories = merge_observations(observations)
    all_results[name] = {
        "summary": summarize(memories),
        "memories": [
            {
                "id": m.id,
                "key": m.key,
                "state": m.state,
                "agents": sorted(m.agents()),
                "values": sorted(m.values),
                "interpretations": sorted(m.interpretations()),
                "observations": [o.__dict__ for o in m.observations],
            }
            for m in memories
        ],
    }

output = {"experiment": "EXP-V6", "benchmarks": all_results}
(RESULTS / "v6.cross_agent.json").write_text(json.dumps(output, indent=2))
print(json.dumps({k: v["summary"] for k, v in all_results.items()}, indent=2))
