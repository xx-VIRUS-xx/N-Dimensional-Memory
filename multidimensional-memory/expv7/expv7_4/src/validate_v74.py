import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
SCHEMAS = ROOT / 'schemas'
RESULTS = ROOT / 'results'

bench = json.loads((DATA / 'benchmark_v7_4.json').read_text())
case_ids = {c['case_id'] for c in bench['cases']}

CONSUMPTION_CONDITIONS = {'RAW', 'RAG', 'V6-GENERATED', 'V6-GENERATED+RAW'}
LEGACY_ALIASES = {'V6', 'V6+RAW'}

condition_warnings = []


def validate_consumption_record(r, source_path):
    assert r['case_id'] in case_ids, f"unknown case_id {r['case_id']!r} in {source_path}"
    cond = r['condition']
    if cond not in CONSUMPTION_CONDITIONS:
        if cond in LEGACY_ALIASES:
            condition_warnings.append(f"{source_path.name}: condition field is {cond!r}, filename implies a V7.4 condition name")
        else:
            raise AssertionError(f"unknown condition {cond!r} in {source_path}")
    assert isinstance(r['unsupported_claims'], int) and r['unsupported_claims'] >= 0
    assert isinstance(r['evidence_used'], list)
    assert 'correctness' in r and isinstance(r['correctness'], dict)


def main():
    consumption_files = sorted(RESULTS.glob('*.RAW.json')) + \
        sorted(RESULTS.glob('*.RAG.json')) + \
        sorted(RESULTS.glob('*.V6-GENERATED.json')) + \
        sorted(RESULTS.glob('*.V6-GENERATED+RAW.json'))

    total = 0
    for p in consumption_files:
        data = json.loads(p.read_text())
        assert isinstance(data, list), f'{p} must be a list'
        assert len(data) == 8, f'{p} must have exactly 8 records, has {len(data)}'
        for r in data:
            validate_consumption_record(r, p)
            total += 1
    print(f'validated_consumption_records={total}')
    if condition_warnings:
        print(f'condition_label_warnings={len(condition_warnings)}')
        for w in sorted(set(condition_warnings)):
            print(f'  WARNING: {w}')

    import jsonschema
    mem_schema = json.loads((SCHEMAS / 'memory_v74.schema.json').read_text())
    memory_files = sorted(RESULTS.glob('*.memory.json'))
    for p in memory_files:
        data = json.loads(p.read_text())
        jsonschema.validate(instance=data, schema=mem_schema)
    print(f'memory_artifacts_found={len(memory_files)} (all schema-valid against memory_v74.schema.json)')

    eval_files = sorted(RESULTS.glob('*.memory_eval.json'))
    print(f'memory_eval_artifacts_found={len(eval_files)}')

    handoff_files = [p for p in [RESULTS / 'claude_to_copilot.json', RESULTS / 'copilot_to_claude.json'] if p.exists()]
    print(f'cross_agent_handoff_artifacts_found={len(handoff_files)}')
    for p in handoff_files:
        d = json.loads(p.read_text())
        status = d.get('status', 'executed' if 'answers' in d or d.get('correct') is not None else 'unknown')
        print(f'  {p.name}: status={status!r}')


if __name__ == '__main__':
    main()
