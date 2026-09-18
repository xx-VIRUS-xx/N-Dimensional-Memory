import json,sys
p=sys.argv[1]
d=json.load(open(p))
assert isinstance(d.get('records'),list)
ids=set()
for r in d['records']:
    assert r['memory_id'] not in ids; ids.add(r['memory_id'])
    assert isinstance(r['source_event_ids'],list)
print(f'valid records={len(ids)}')
