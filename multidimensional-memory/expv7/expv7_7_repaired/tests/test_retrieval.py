import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def test_retrieval_runner_conditions():
    for c in ('raw','bm25','semantic','hybrid'):
        p=subprocess.run([sys.executable,str(ROOT/'run_retrieval.py'),'--condition',c,'--top-k','24'],cwd=ROOT,capture_output=True,text=True)
        assert p.returncode==0,p.stderr
        out=ROOT/'results'/'retrieval'/f'{c}.json'; assert out.exists()
        d=json.loads(out.read_text()); assert d['query_count']==96; assert len(d['results'])==96
        assert all(row['retrieved'] for row in d['results'])
