import json, random, re
from pathlib import Path

OUT=Path(__file__).resolve().parents[1]/'data'
random.seed(7401)

signal=[
("E0007","2026-01-03","Rahul","We discussed PostgreSQL and DynamoDB for billing; no choice was made in that meeting.","billing"),
("E0014","2026-01-05","Rahul","We chose PostgreSQL for billing because auditability mattered more than migration effort.","billing"),
]
# Curated durable events. Additional events are generated as semantically similar noise.
durable=[
("E0014","2026-01-05","Rahul","We chose PostgreSQL for billing because auditability mattered more than migration effort.","billing"),
("E0068","2026-01-19","Rahul","We tried DynamoDB for the billing prototype, but conditional-update semantics did not match the transaction flow and the migration failed.","billing"),
("E0142","2026-02-02","Claude","The DynamoDB migration failure was confirmed after reviewing integration-test output.","billing"),
("E0179","2026-02-09","Rahul","We tested Redis caching to reduce API latency.","redis"),
("E0264","2026-02-21","Rahul","The Redis experiment increased cache invalidation complexity, so we abandoned it.","redis"),
("E0357","2026-03-01","Rahul","The first invoice export attempt timed out after 18 minutes.","invoice"),
("E0402","2026-03-11","Rahul","The webhook migration moved from polling to webhooks after the provider fixed signature verification.","webhook"),
("E0449","2026-03-17","Claude","I inferred that transaction semantics were related to the billing migration failure.","billing"),
("E0450","2026-03-17","Rahul","I confirmed transaction semantics were the reason the DynamoDB migration was abandoned.","billing"),
("E0516","2026-03-22","Arjun","The deployment-window pronoun 'he' remains unresolved between Rahul and Arjun.","ambiguity"),
("E0549","2026-03-29","Rahul","MongoDB was not discussed in the billing migration review; this statement is scoped to that review.","negative"),
("E0623","2026-04-03","Rahul","We switched invoice exports to asynchronous jobs after the timeout.","invoice"),
("E0732","2026-04-25","Rahul","We retried Redis with a narrower cache scope, but the latency improvement was negligible.","redis"),
("E0803","2026-05-02","Copilot","I later read the billing migration notes and preserved the failed DynamoDB attempt and decision history.","provenance"),
("E0888","2026-05-20","Rahul","Webhooks were temporarily disabled because duplicate deliveries caused reconciliation errors.","webhook"),
("E1034","2026-06-01","Rahul","The first full customer invoice batch completed successfully through asynchronous export.","invoice"),
("E1103","2026-06-10","Rahul","A MongoDB proposal appeared in a different project, not the billing migration review.","negative"),
("E1191","2026-06-03","Rahul","Webhooks were re-enabled after idempotency handling was deployed.","webhook"),
]
# Two additional durable-like events make 20, while forcing evaluator to distinguish discussion/decision.
durable += [
("E1200","2026-06-05","Rahul","The billing database decision remains PostgreSQL; no later reversal was made.","billing"),
("E1201","2026-06-06","Rahul","We will document the webhook state history in the migration notes.","webhook"),
]
# 20 gold events, including a few intentionally mundane-but-important statements.
# Normalize IDs to exactly 20.
durable=durable[:20]

def noise(i, ts):
    topic=random.choice(["billing","redis","invoice","webhook","deployment","observability","testing","database"])
    templates={
    "billing":["We discussed billing database options again and compared tradeoffs.","The billing prototype was mentioned during a planning chat.","Someone asked whether billing work was on track.","We reviewed an old billing note without changing the decision.","A billing database migration was discussed as a possibility."],
    "redis":["We discussed whether Redis could help latency in a hypothetical case.","Redis came up during a cache design discussion.","The team reviewed cache metrics without making a new decision.","Someone suggested looking at cache scope later.","Redis was mentioned while reviewing unrelated performance notes."],
    "invoice":["Invoice export work was discussed in standup.","Someone asked about invoice export progress.","We reviewed an invoice export log without changing the process.","The invoice exporter was mentioned as a possible optimization target.","The team discussed export monitoring."],
    "webhook":["Webhook migration progress was discussed without changing the current plan.","The provider integration came up in a routine design review.","We reviewed webhook logs and delivery metrics.","Someone proposed checking webhook behavior later.","Webhook compatibility was discussed with no new decision."],
    "deployment":["Deployment timing was discussed without a committed window.","A possible deployment change was mentioned for later review.","The team checked deployment status.","Deployment notes were reviewed.","Someone asked whether the next deployment needed attention."],
    "observability":["Monitoring dashboards were reviewed.","Latency metrics were discussed without a new action.","The team looked at logs and traces.","Observability improvements were mentioned as future work.","No monitoring decision was made in this discussion."],
    "testing":["Integration tests were reviewed.","A test run was discussed without a new conclusion.","Someone suggested another test.","Test output was mentioned during review.","The team checked test coverage."],
    "database":["Database options were discussed without a decision.","A database migration was mentioned as possible future work.","The team reviewed database documentation.","Someone compared database tradeoffs.","Database reliability was discussed during planning."]}
    text=random.choice(templates[topic])
    return f"E{10000+i}",ts,random.choice(["Rahul","Arjun","Claude","Copilot"]),text,topic

# Build 1180 noise events interleaved with 20 durable events. Ensure no unique lexical marker.
events=[]
by_id={x[0]:x for x in durable}
slots=sorted(random.sample(range(1200),20))
for idx in range(1200):
    if idx in slots:
        ev=durable[slots.index(idx)]
    else:
        day=1+idx//20
        month=1+(day-1)//30
        d=((day-1)%30)+1
        ev=noise(idx, f"2026-{month:02d}-{d:02d}")
    events.append(ev)
# Keep chronological by slot ordering, but durable dates should be monotonic enough for evaluation.
records=[]
for eid,ts,sp,text,topic in events:
    records.append({"event_id":eid,"timestamp":ts,"speaker":sp,"text":text,"topics":[topic],"kind":"signal" if eid in by_id else "distractor"})
with open(OUT/'conversation_v7_4.jsonl','w') as f:
    for r in records:f.write(json.dumps(r)+"\n")
with open(OUT/'conversation_v7_4_unlabeled.jsonl','w') as f:
    for r in records:
        r={k:v for k,v in r.items() if k!="kind"}
        f.write(json.dumps(r)+"\n")
# Evaluator-only gold. Includes durable event IDs and delayed query definitions.
gold={"version":"7.4","corpus_size":1200,"signal_event_ids":[x[0] for x in durable],"cases":[
{"case_id":"V74-HIST-01","query":"Why was PostgreSQL chosen and what happened with DynamoDB?","required_event_ids":["E0014","E0068","E0142"]},
{"case_id":"V74-DEC-01","query":"What happened to Redis from experiment through retry outcome?","required_event_ids":["E0179","E0264","E0732"]},
{"case_id":"V74-ACT-01","query":"What happened to invoice exports from failure through successful batch?","required_event_ids":["E0357","E0623","E1034"]},
{"case_id":"V74-TIME-01","query":"Reconstruct webhook state through the latest known state.","required_event_ids":["E0402","E0888","E1191"]},
{"case_id":"V74-AMB-01","query":"What is known about the deployment-window pronoun ambiguity?","required_event_ids":["E0516"]},
{"case_id":"V74-BELIEF-01","query":"Was transaction semantics only an inference or later confirmed?","required_event_ids":["E0449","E0450"]},
{"case_id":"V74-NEG-01","query":"Was MongoDB discussed in the billing migration review?","required_event_ids":["E0549","E1103"]},
{"case_id":"V74-PROV-01","query":"What is the provenance history of the billing database decision and migration failure?","required_event_ids":["E0068","E0142","E0449","E0450","E0803"]}
]}
with open(OUT/'benchmark_v7_4.json','w') as f:json.dump(gold,f,indent=2)
print('generated',len(records),'events; durable',len(durable),'slots',slots)
