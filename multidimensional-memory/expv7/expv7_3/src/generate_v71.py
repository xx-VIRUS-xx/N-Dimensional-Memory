import json, random
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'; DATA.mkdir(exist_ok=True)
rng=random.Random(7101)

# Deliberate long-horizon signal events. These are the canonical facts the V6 compiler will preserve.
signals = [
(5,'2026-01-04','Rahul','We chose PostgreSQL for the billing service because auditability mattered more than the lower migration effort of DynamoDB.'),
(67,'2026-01-19','Rahul','We tried DynamoDB for the billing prototype, but the migration failed because conditional update semantics did not match the existing transaction flow.'),
(141,'2026-02-02','Claude','The failed DynamoDB migration was confirmed after reviewing the integration test output.'),
(233,'2026-02-17','Rahul','We started a webhook migration using polling as the temporary compatibility path.'),
(401,'2026-03-11','Rahul','The webhook migration moved from polling to webhooks after the provider fixed signature verification.'),
(887,'2026-05-20','Rahul','Webhooks were disabled temporarily because duplicate deliveries caused reconciliation errors.'),
(1190,'2026-06-03','Rahul','Webhooks were re-enabled after idempotency handling was deployed.'),
(312,'2026-02-25','Rahul','Rahul said he would ask Arjun about the deployment window, but the conversation did not establish whether "he" meant Rahul or Arjun.'),
(515,'2026-03-22','Arjun','The team discussed the deployment window, but no speaker-reference resolution for "he" was recorded.'),
(178,'2026-02-09','Rahul','We tested Redis caching to reduce API latency.'),
(263,'2026-02-21','Rahul','The Redis experiment increased cache invalidation complexity, so we abandoned it.'),
(731,'2026-04-18','Rahul','We retried Redis with a narrower cache scope, but the latency improvement was negligible.'),
(356,'2026-03-01','Rahul','The first invoice export attempt timed out after 18 minutes.'),
(622,'2026-04-03','Rahul','We switched invoice exports to asynchronous jobs after the timeout.'),
(1033,'2026-05-31','Rahul','The asynchronous invoice export completed successfully for the first full customer batch.'),
(448,'2026-03-17','Claude','Claude inferred that the billing migration failure was related to transaction semantics.'),
(449,'2026-03-17','Rahul','Rahul confirmed that transaction semantics were the reason the DynamoDB migration was abandoned.'),
(548,'2026-03-29','Rahul','We explicitly recorded that MongoDB had not been discussed in the billing migration review.'),
(802,'2026-04-29','Copilot','Copilot later read the billing migration notes and preserved the PostgreSQL decision and the failed DynamoDB attempt.'),
(1102,'2026-05-08','Rahul','A proposal to use MongoDB for billing was mentioned in a different project, not in the billing migration review.'),
]
signal_by_id={i:{'event_id':f'E{i:04d}','timestamp':ts,'speaker':sp,'text':txt} for i,ts,sp,txt in signals}

names=['Rahul','Arjun','Meera','Neha','Vikram']
topics=['billing','webhook','deployment','API','database','observability','cache','invoice','CI','testing','auth','search','frontend','mobile']
verbs=['reviewed','discussed','tested','planned','measured','updated','documented','checked','deployed','refactored']
objects=['latency','logs','tests','schema','dashboard','retry policy','API contract','release notes','metrics','alerts']

events=[]
for i in range(1,1201):
    if i in signal_by_id:
        e=signal_by_id[i].copy(); e['kind']='signal'; e['topics']=[]
        events.append(e); continue
    speaker=rng.choice(names)
    topic=rng.choice(topics)
    text=f'{speaker} {rng.choice(verbs)} {rng.choice(objects)} for the {topic} workstream; the note recorded routine progress and no final decision.'
    events.append({'event_id':f'E{i:04d}','timestamp':f'2026-{1+(i-1)//300:02d}-{1+(i-1)%28:02d}','speaker':speaker,'text':text,'kind':'distractor','topics':[topic]})

cases=[
{'case_id':'V71-HIST-01','query_category':'historical_recall','query':'Why was PostgreSQL chosen for the billing service, and what happened when DynamoDB was tried?','raw_event_ids':['E0005','E0067','E0141'],'gold':{'facts':['PostgreSQL was chosen because auditability mattered more than lower migration effort','DynamoDB migration failed due to conditional-update/transaction-flow incompatibility','Claude later confirmed the failure after reviewing integration-test output'],'required':['E0005','E0067','E0141']}},
{'case_id':'V71-DEC-01','query_category':'decision_continuity','query':'Why was Redis caching abandoned, and what happened when it was retried?','raw_event_ids':['E0178','E0263','E0731'],'gold':{'facts':['initial Redis test increased cache invalidation complexity','it was abandoned','a narrower retry produced negligible latency improvement'],'required':['E0178','E0263','E0731']}},
{'case_id':'V71-ACT-01','query_category':'action_outcome','query':'What happened with invoice exports from the first failed attempt through the later full customer batch?','raw_event_ids':['E0356','E0622','E1033'],'gold':{'facts':['first export timed out after 18 minutes','exports were switched to asynchronous jobs','first full customer batch completed successfully'],'required':['E0356','E0622','E1033']}},
{'case_id':'V71-TIME-01','query_category':'temporal_state','query':'Reconstruct the webhook state from the initial migration through the latest known state.','raw_event_ids':['E0233','E0401','E0887','E1190'],'gold':{'timeline':['polling temporary compatibility path','moved to webhooks','webhooks disabled temporarily due duplicate deliveries/reconciliation errors','webhooks re-enabled after idempotency handling'],'latest':'webhooks re-enabled','required':['E0233','E0401','E0887','E1190']}},
{'case_id':'V71-AMB-01','query_category':'ambiguity','query':'Who did "he" refer to in the deployment-window discussion?','raw_event_ids':['E0312','E0515'],'gold':{'answer':'unresolved between Rahul and Arjun','required':['E0312','E0515']}},
{'case_id':'V71-CONFLICT-01','query_category':'conflict','query':'Was the reason for abandoning DynamoDB merely an inference, or was it later confirmed? Preserve the provenance.','raw_event_ids':['E0448','E0449'],'gold':{'observations':['Claude inferred transaction semantics were involved','Rahul later confirmed transaction semantics were the reason'],'status':'confirmed_after_inference','required':['E0448','E0449']}},
{'case_id':'V71-NEG-01','query_category':'negative_knowledge','query':'Was MongoDB discussed as a billing-migration option in the billing migration review?','raw_event_ids':['E0548','E1102'],'gold':{'answer':'not_discussed_in_that_review; E1102 was a different project','required':['E0548','E1102']}},
{'case_id':'V71-PROV-01','query_category':'provenance','query':'Which agent observed or confirmed the DynamoDB migration failure, and what is the history of that belief?','raw_event_ids':['E0067','E0141','E0448','E0449','E0802'],'gold':{'history':['Rahul observed the failed migration','Claude confirmed it after reviewing integration-test output','Claude later inferred transaction semantics','Rahul explicitly confirmed transaction semantics'],'required':['E0067','E0141','E0448','E0449','E0802']}},
]

# case relevance index used by the actual condition builders
case_ids={c['case_id']:c for c in cases}
with (DATA/'conversation_v7_1.jsonl').open('w') as f:
    for e in events:
        f.write(json.dumps(e,ensure_ascii=False)+'\n')
with (DATA/'benchmark_v7_1.json').open('w') as f:
    json.dump({'version':'7.1','event_count':len(events),'cases':cases},f,indent=2)
print(f'generated {len(events)} events and {len(cases)} cases')
