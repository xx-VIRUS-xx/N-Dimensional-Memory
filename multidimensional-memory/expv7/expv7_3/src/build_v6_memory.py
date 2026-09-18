import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data'
bench=json.loads((DATA/'benchmark_v7_1.json').read_text())
events={e['event_id']:e for e in [json.loads(x) for x in (DATA/'conversation_v7_1.jsonl').read_text().splitlines()]}
mem=[]
for case in bench['cases']:
    for eid in case['raw_event_ids']:
        e=events[eid]
        mem.append({'memory_id':f'M-{eid}','case_id':case['case_id'],'type':'observation','event_id':eid,'timestamp':e['timestamp'],'speaker':e['speaker'],'content':e['text'],'provenance':{'source_event':eid,'source_agent':e['speaker']},'status':'observed'})
# Derived relational/state records. These are deterministic benchmark annotations, not LLM output.
mem += [
{'memory_id':'MREL-BILLING-01','type':'relationship','case_id':'V71-HIST-01','subject':'PostgreSQL','predicate':'chosen_for','object':'billing_service','basis':['E0005'],'status':'confirmed'},
{'memory_id':'MREL-BILLING-02','type':'relationship','case_id':'V71-HIST-01','subject':'DynamoDB','predicate':'migration_failed_because','object':'transaction_flow_incompatibility','basis':['E0067','E0141'],'status':'confirmed'},
{'memory_id':'MREL-REDIS-01','type':'relationship','case_id':'V71-DEC-01','subject':'Redis','predicate':'abandoned_because','object':'cache_invalidation_complexity','basis':['E0263'],'status':'confirmed'},
{'memory_id':'MREL-REDIS-02','type':'relationship','case_id':'V71-DEC-01','subject':'Redis','predicate':'retry_result','object':'negligible_latency_improvement','basis':['E0731'],'status':'confirmed'},
{'memory_id':'MSTATE-WEBHOOK','type':'state_history','case_id':'V71-TIME-01','subject':'webhook_migration','states':[{'state':'polling','valid_from':'2026-02-17','valid_to':'2026-03-11','basis':['E0233']},{'state':'webhooks_active','valid_from':'2026-03-11','valid_to':'2026-05-20','basis':['E0401']},{'state':'webhooks_disabled','valid_from':'2026-05-20','valid_to':'2026-06-03','basis':['E0887']},{'state':'webhooks_active','valid_from':'2026-06-03','valid_to':None,'basis':['E1190']}],'current_state':'webhooks_active','status':'derived'},
{'memory_id':'MAMB-HE','type':'ambiguity','case_id':'V71-AMB-01','expression':'he','candidates':['Rahul','Arjun'],'resolution':None,'basis':['E0312','E0515'],'status':'unresolved'},
{'memory_id':'MREL-CONFIRM','type':'belief_history','case_id':'V71-CONFLICT-01','proposition':'DynamoDB migration was abandoned because transaction semantics were incompatible','history':[{'status':'inferred','source':'E0448','agent':'Claude'},{'status':'confirmed','source':'E0449','agent':'Rahul'}],'current_status':'confirmed','basis':['E0448','E0449']},
{'memory_id':'MNEG-MONGO','type':'negative_knowledge','case_id':'V71-NEG-01','proposition':'MongoDB was discussed in the billing migration review','status':'not_discussed','completeness':'complete_for_review','basis':['E0548'],'qualifier':'A later MongoDB mention belonged to a different project (E1102)'},
{'memory_id':'MPROV-BILLING','type':'provenance_chain','case_id':'V71-PROV-01','proposition':'DynamoDB migration failure and reason','chain':[{'source':'E0067','agent':'Rahul','role':'observation'},{'source':'E0141','agent':'Claude','role':'confirmation'},{'source':'E0448','agent':'Claude','role':'inference'},{'source':'E0449','agent':'Rahul','role':'confirmation'},{'source':'E0802','agent':'Copilot','role':'later_memory_read'}]}
]
(DATA/'v6_memory.json').write_text(json.dumps({'version':'6.2','memory':mem},indent=2))
print(f'wrote {len(mem)} memory records')
