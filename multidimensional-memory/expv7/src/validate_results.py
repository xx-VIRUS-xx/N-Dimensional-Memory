import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / 'schemas' / 'agent_result.schema.json').read_text())
ALLOWED = set(SCHEMA['properties']['condition']['enum'])
REQUIRED = set(SCHEMA['required'])


def validate_record(r):
    missing = REQUIRED - r.keys()
    assert not missing, f'missing fields: {sorted(missing)}'
    assert r['condition'] in ALLOWED
    assert isinstance(r['unsupported_claims'], int) and r['unsupported_claims'] >= 0
    assert isinstance(r['evidence_used'], list)


def main():
    result_dir = ROOT / 'results'
    files = sorted(result_dir.glob('*.json'))
    records = []
    for path in files:
        payload = json.loads(path.read_text())
        rows = payload if isinstance(payload, list) else [payload]
        for row in rows:
            validate_record(row)
            records.append(row)
    print(f'validated_records={len(records)}')
    if not records:
        print('No agent result files yet. This is expected before manual agent runs.')


if __name__ == '__main__':
    main()
