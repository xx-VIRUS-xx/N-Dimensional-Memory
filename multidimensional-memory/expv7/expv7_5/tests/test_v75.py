import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_generate_and_validate():
    subprocess.check_call([sys.executable,str(ROOT/'src/generate_v75_corpus.py')])
    subprocess.check_call([sys.executable,str(ROOT/'src/generate_future_queries.py')])
    subprocess.check_call([sys.executable,str(ROOT/'src/validate_v75.py')])

def test_no_writer_shortcut():
    for p in (ROOT/'data').glob('*_unlabeled.jsonl'):
        for line in p.read_text().splitlines():
            r=json.loads(line)
            assert 'kind' not in r
            assert 'signal' not in r['text'].lower()
            assert 'distractor' not in r['text'].lower()
