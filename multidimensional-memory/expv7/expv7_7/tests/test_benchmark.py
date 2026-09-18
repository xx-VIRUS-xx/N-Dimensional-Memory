import json
from pathlib import Path
root=Path(__file__).parents[1]
public=json.load(open(root/'data/benchmark_v7_7_public.json'))
gold=json.load(open(root/'data/benchmark_v7_7_gold.json'))
assert public['event_count']==1200
assert public['conversation_count']==12
assert public['query_count']==96
assert len(gold['gold_durable_event_ids'])==216
assert len(gold['queries'])==96
print('V7.7 benchmark checks passed')
