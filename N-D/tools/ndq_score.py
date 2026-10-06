"""Apply the blind key to hand scores and report ND-Q results (EXP-NDQ.md).

  python3 tools/ndq_score.py --scores ND-Q/results/scores.json --key ND-Q/results/key.json --review ND-3/review.json
         [--probes P --source S --traces ND-Q/run1/tools.traces]     # adds TOOLS evidence recall
"""
import argparse, json, re, statistics as st
from collections import defaultdict

V = {"C": 1, "P": .5, "W": 0}
CEIL = {"q17", "q25", "q30"}

ap = argparse.ArgumentParser()
ap.add_argument("--scores", required=True); ap.add_argument("--key", required=True); ap.add_argument("--review", required=True)
ap.add_argument("--probes"); ap.add_argument("--source"); ap.add_argument("--traces"); ap.add_argument("--out")
a = ap.parse_args()
sc, key = json.load(open(a.scores)), json.load(open(a.key))
items = {i["id"]: i for i in json.load(open(a.review))["items"]}
assert len(sc) == 2 * len(key), "not all answers scored"
res = defaultdict(dict)
for q, order in key.items():
    for slot, arm in zip("AB", order):
        res[arm][q] = V[sc[q + slot]]
for arm in ("RAW", "RAG", "DEPICT"):
    res[arm] = {q: items[q][arm] for q in items}
out = {"arms": {}}
print(f"{'arm':8}{'total':>7}{'no-ceil/37':>12}   by category")
for arm in ("RAW", "RAGTOOL", "RAG", "DEPICT", "TOOLS"):
    r = res[arm]; cats = defaultdict(lambda: [0, 0])
    for q, v in r.items():
        cats[items[q]["category"]][0] += v; cats[items[q]["category"]][1] += 1
    tot, nc = sum(r.values()), sum(v for q, v in r.items() if q not in CEIL)
    out["arms"][arm] = {"total": tot, "no_ceiling": nc, "by_category": {c: v[0] for c, v in sorted(cats.items())}}
    print(f"{arm:8}{tot:7.1f}{nc:12.1f}   " + "  ".join(f"c{c}={v[0]:.1f}/{v[1]}" for c, v in sorted(cats.items())))
T, R = res["TOOLS"], res["RAGTOOL"]
t, rg, rw, ra = sum(T.values()), sum(R.values()), sum(res["RAW"].values()), sum(res["RAG"].values())
print(f"\nQ1 TOOLS >= RAG+3.0 (>=31.5): {t} vs {ra + 3.0} -> {'PASS' if t >= ra + 3 else 'FAIL'}")
print(f"Q2 TOOLS >= RAGTOOL+2.0:      {t} vs {rg + 2.0} -> {'PASS' if t >= rg + 2 else 'FAIL'}")
print(f"Q3 TOOLS >= 90% RAW (>=29.25): {t} = {t / rw:.1%} of RAW -> {'PASS' if t >= .9 * rw else 'FAIL'}")
tb = [q for q in T if T[q] > R[q]]; rb = [q for q in T if R[q] > T[q]]
print(f"TOOLS better on {len(tb)} {tb}; RAGTOOL better on {len(rb)} {rb}")
if a.probes and a.source and a.traces:
    src = {json.loads(l)["dia_id"]: int(json.loads(l)["sentence_id"][1:]) for l in open(a.source)}
    rows = []
    for p in map(json.loads, open(a.probes)):
        ev = {src[e] for e in p["evidence"] if e in src}; seen = set()
        for l in open(f"{a.traces}/{p['id']}.jsonl"):
            seen |= {int(x) for x in re.findall(r"\bt(\d+)\b", json.loads(l)["text"])}
        rows.append((p["id"], len(ev & seen), len(ev)))
    print(f"\nTOOLS evidence recall: pooled {sum(h for _, h, _ in rows)}/{sum(n for _, _, n in rows)}, mean per question {st.mean(h / n for _, h, n in rows):.3f}")
    out["tools_recall_mean"] = st.mean(h / n for _, h, n in rows)
if a.out:
    json.dump(out, open(a.out, "w"), indent=1)
