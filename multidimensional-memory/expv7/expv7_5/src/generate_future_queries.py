"""Generate evaluator-only queries AFTER memory freeze."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    gold=json.loads((ROOT/"data/gold_annotations.json").read_text())
    queries=[]
    kinds=["direct","paraphrase","indirect","temporal","causal","multi_hop","negative","ambiguity","compositional"]
    for domain, rows in gold.items():
        for idx,g in enumerate(rows[:10]):
            topic=g["topic"]
            q=[
                f"What was ultimately decided about {topic}?",
                f"Did the team ever settle the question involving {topic}?",
                f"What changed over time regarding {topic}?",
                f"What was the eventual outcome associated with {topic}?",
                f"Why did the later state of {topic} differ from the earlier discussion?",
                f"Trace the discussion, action, and outcome for {topic}.",
                f"Was {topic} ever confirmed, or was it left unresolved?",
                f"What do we know and what remains uncertain about {topic}?",
                f"How does {topic} relate to the surrounding decision and later outcome?",
            ][idx%9]
            queries.append({"query_id":f"{domain.upper()}-Q{idx:03d}","domain":domain,"kind":kinds[idx%len(kinds)],"gold_event_ids":[g["event_id"]],"question":q})
    (ROOT/"data/future_queries.json").write_text(json.dumps(queries,indent=2),encoding="utf-8")
if __name__ == "__main__": main()
