import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
SCHEMAS = ROOT / 'schemas'

bench = json.loads((DATA / 'benchmark_v7_1.json').read_text())
case_ids = {c['case_id'] for c in bench['cases']}

CONSUMPTION_CONDITIONS = {'RAW', 'RAG', 'V6-GENERATED', 'V6-GENERATED+RAW'}
# V7.2-era condition strings some agents' runs still emit for the two generated-memory
# conditions; accepted here (with a warning) rather than rejected, since crashing on this
# is less useful than surfacing it as a documented cross-agent labeling inconsistency.
LEGACY_ALIASES = {'V6', 'V6+RAW'}

condition_warnings = []


def validate_consumption_record(r, source_path, source_condition_from_filename):
    assert r['case_id'] in case_ids, f"unknown case_id {r['case_id']!r}"
    cond = r['condition']
    if cond not in CONSUMPTION_CONDITIONS:
        if cond in LEGACY_ALIASES:
            condition_warnings.append(
                f"{source_path.name}: record condition field is {cond!r} but filename implies "
                f"{source_condition_from_filename!r} (V7.2-era label used instead of the V7.3 "
                f"condition name required by EXP-V7.3.md section 7)"
            )
        else:
            raise AssertionError(f"unknown condition {cond!r} in {source_path}")
    assert isinstance(r['unsupported_claims'], int) and r['unsupported_claims'] >= 0
    assert isinstance(r['evidence_used'], list)
    assert 'correctness' in r and isinstance(r['correctness'], dict)


def main():
    result_dir = ROOT / 'results'
    consumption_files = sorted(result_dir.glob('*.RAW.json')) + \
        sorted(result_dir.glob('*.RAG.json')) + \
        sorted(result_dir.glob('*.V6-GENERATED.json')) + \
        sorted(result_dir.glob('*.V6-GENERATED+RAW.json'))

    total = 0
    for p in consumption_files:
        data = json.loads(p.read_text())
        assert isinstance(data, list), f'{p} must be a list'
        assert len(data) == 8, f'{p} must have exactly 8 records, has {len(data)}'
        implied_condition = p.stem.split('.', 1)[1] if '.' in p.stem else None
        for r in data:
            validate_consumption_record(r, p, implied_condition)
            total += 1
    print(f'validated_consumption_records={total}')
    if condition_warnings:
        print(f'condition_label_warnings={len(condition_warnings)}')
        for w in condition_warnings:
            print(f'  WARNING: {w}')

    memory_files = sorted(result_dir.glob('*.memory.json'))
    memory_key_warnings = []
    for p in memory_files:
        data = json.loads(p.read_text())
        if 'memory' in data:
            pass
        elif 'records' in data:
            memory_key_warnings.append(
                f"{p.name}: top-level memory-list key is 'records', not the 'memory' key used "
                f"elsewhere in this experiment series (e.g. claude.memory.json) -- same cross-agent "
                f"naming inconsistency pattern as the condition-label warnings above"
            )
        else:
            raise AssertionError(f'{p} has neither a "memory" nor a "records" top-level key')
    print(f'memory_artifacts_found={len(memory_files)}')
    for w in memory_key_warnings:
        print(f'  WARNING: {w}')

    eval_files = sorted(result_dir.glob('*.memory_eval.json'))
    print(f'memory_eval_artifacts_found={len(eval_files)}')

    handoff_files = [p for p in [result_dir / 'claude_to_copilot.json', result_dir / 'copilot_to_claude.json'] if p.exists()]
    print(f'cross_agent_handoff_artifacts_found={len(handoff_files)}')

    if total == 0 and not memory_files:
        print('No agent result files yet. This is expected before manual agent runs.')


if __name__ == '__main__':
    main()
