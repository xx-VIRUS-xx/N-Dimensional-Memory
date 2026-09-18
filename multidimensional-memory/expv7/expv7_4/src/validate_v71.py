import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data'
bench=json.loads((DATA/'benchmark_v7_1.json').read_text())
case_ids={c['case_id'] for c in bench['cases']}
for p in sorted((ROOT/'results').glob('*.json')):
    data=json.loads(p.read_text())
    assert isinstance(data,list), f'{p} must be a list'
    for r in data:
        assert r['case_id'] in case_ids
        assert r['condition'] in {'RAW','RAG','V6','V6+RAW'}
        assert isinstance(r['unsupported_claims'],int) and r['unsupported_claims']>=0
        assert isinstance(r['evidence_used'],list)
print('result validation passed')
