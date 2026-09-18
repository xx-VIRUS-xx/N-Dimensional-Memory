"""Generate deterministic V7.5 corpora and evaluator-only annotations."""
import json, random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOMAINS = {
    "engineering": [
        "PostgreSQL migration", "Redis retry policy", "DynamoDB migration", "invoice timeout", "webhook delivery",
        "deployment rollback", "cache invalidation", "API rate limit", "CI pipeline", "search index"
    ],
    "planning": [
        "release date", "team ownership", "customer workshop", "budget approval", "hiring plan",
        "travel schedule", "on-call rotation", "documentation deadline", "vendor review", "quarterly goal"
    ],
    "product": [
        "bulk import", "dark mode", "export API", "mobile workflow", "pricing experiment",
        "notification system", "search redesign", "checkout flow", "analytics dashboard", "SSO rollout"
    ],
    "operations": [
        "database outage", "queue backlog", "billing alert", "certificate renewal", "backup failure",
        "support escalation", "latency incident", "storage alert", "worker crash", "dependency outage"
    ]
}
DURABLE_TEMPLATES = [
    "Decision: {topic} was approved after reviewing the alternatives.",
    "Action: the team attempted {topic}; the first attempt failed.",
    "Outcome: {topic} was confirmed successful after the follow-up check.",
    "State: {topic} changed from tentative to confirmed.",
    "Plan: {topic} remains unresolved and no final decision has been confirmed.",
    "Change: {topic} was replaced by a newer approach; the earlier state is obsolete.",
]
DISTRACTOR_TEMPLATES = [
    "The team discussed {topic} and compared several options.",
    "Someone mentioned {topic} during the meeting without making a decision.",
    "A possible future approach involving {topic} was considered.",
    "The team revisited {topic} as background context.",
    "A nearby task mentioned {topic}, but it did not change the current state.",
    "An earlier note about {topic} was repeated for context.",
    "The group asked whether {topic} might matter later.",
]

def write_jsonl(path, rows):
    with path.open("w", encoding="utf-8") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")

def main():
    random.seed(7501)
    data = ROOT / "data"
    all_gold = {}
    all_queries_seed = {}
    for domain, topics in DOMAINS.items():
        events=[]; gold=[]
        # 30 durable events: deterministic but distributed across timeline.
        durable_positions = sorted(random.sample(range(500), 30))
        durable_set=set(durable_positions)
        for i in range(500):
            eid=f"{domain[:3].upper()}-{i:04d}"
            topic=topics[(i*7 + 3) % len(topics)]
            text = (DURABLE_TEMPLATES[i % len(DURABLE_TEMPLATES)].format(topic=topic)
                    if i in durable_set else DISTRACTOR_TEMPLATES[i % len(DISTRACTOR_TEMPLATES)].format(topic=topic))
            # Add semantic noise so no single lexical marker identifies durability.
            if i % 11 == 0: text += " The discussion continued with related operational details."
            if i % 17 == 0: text += " Earlier notes were reviewed before moving on."
            row={"event_id":eid,"timestamp":f"2026-01-{(i%28)+1:02d}T{(i%24):02d}:00:00Z","speaker":["Alex","Sam","Priya"][i%3],"text":text,"topic":topic}
            events.append(row)
            if i in durable_set:
                gold.append({"event_id":eid,"domain":domain,"topic":topic,"durable":True})
        # Shuffle ordering by timestamp to force consumers to use timestamps, while keeping stable chronological data.
        events.sort(key=lambda x:(x["timestamp"],x["event_id"]))
        write_jsonl(data/f"{domain}_unlabeled.jsonl", events)
        write_jsonl(data/f"{domain}_labeled.jsonl", [dict(e, kind=("signal" if e["event_id"] in {g["event_id"] for g in gold} else "distractor")) for e in events])
        all_gold[domain]=gold
        all_queries_seed[domain]=[g["event_id"] for g in gold]
    (data/"gold_annotations.json").write_text(json.dumps(all_gold,indent=2),encoding="utf-8")
    (data/"query_seeds.json").write_text(json.dumps(all_queries_seed,indent=2),encoding="utf-8")

if __name__ == "__main__": main()
