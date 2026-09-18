import json, re
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'


def toks(s):
    return re.findall(r'[a-z0-9]+', s.lower())


events = [json.loads(x) for x in (DATA / 'conversation_v7_4.jsonl').read_text().splitlines()]
chunk_size = 12
chunks = []
for start in range(0, len(events), chunk_size):
    es = events[start:start + chunk_size]
    chunks.append({
        'chunk_id': f'C{start // chunk_size:04d}',
        'event_ids': [e['event_id'] for e in es],
        'text': '\n'.join(e['text'] for e in es),
    })

bench = json.loads((DATA / 'benchmark_v7_4.json').read_text())
index = []
for c in chunks:
    index.append({
        'chunk_id': c['chunk_id'],
        'event_ids': c['event_ids'],
        'text': c['text'],
        'terms': dict(Counter(toks(c['text']))),
    })
(DATA / 'rag_index_v74.json').write_text(json.dumps({'chunk_size': chunk_size, 'chunks': index}, indent=2))


def retrieve(query, top_k=6):
    q = set(toks(query))
    out = []
    for c in index:
        ct = set(c['terms'])
        overlap = len(q & ct)
        if overlap:
            score = overlap / (len(q) ** 0.5)
            out.append((score, c['chunk_id'], c['event_ids'], c['text']))
    out.sort(key=lambda x: (-x[0], x[1]))
    return [{'chunk_id': cid, 'score': round(score, 6), 'event_ids': ids, 'text': text} for score, cid, ids, text in out[:top_k]]


retrieved = {c['case_id']: retrieve(c['query']) for c in bench['cases']}
(DATA / 'rag_retrievals_v74.json').write_text(json.dumps(retrieved, indent=2))
for cid, rs in retrieved.items():
    print(cid, [(r['chunk_id'], r['score']) for r in rs])
