"""Blind sheet and report for ND-Q2 (EXP-NDQ2.md).

  sheet:  python3 tools/ndq2_score.py sheet --probes P --answers raw=A.json ragtool=B.json struct=C.json tools2=D.json --out-dir DIR [--seed 5]
          writes DIR/sheet.md (question, gold, answers in a random order labelled A-D; arm names never shown), DIR/key.json (the secret order),
          DIR/scores.json (empty template: {"q00A": "", ...}); fill each with C, P or W.
  report: python3 tools/ndq2_score.py report --scores S --key K --probes P --source SRC --traces struct=DIR tools2=DIR ragtool2=DIR --meta tools2=M.json ...
          accuracy per arm and category, R1 to R5, trace evidence recall, cost. The RAW arm has no traces or meta.
"""
import argparse, json, os, random, re, statistics as st
from collections import defaultdict

VAL = {"C": 1.0, "P": 0.5, "W": 0.0}
ARM_NAMES = {"raw": "RAW", "ragtool": "RAGTOOL", "struct": "STRUCT", "tools2": "TOOLS2"}
LABELS = "ABCD"


def load_probes(path):
    return [json.loads(l) for l in open(path) if l.strip()]


def pairs(items):
    return dict(i.split("=", 1) for i in items)


def build_sheet(probes, answers, seed):
    """answers: {arm: {id: text}}. Returns (markdown, key, template). Every arm must have an answer for every question."""
    for arm, a in answers.items():
        missing = [p["id"] for p in probes if p["id"] not in a]
        if missing:
            raise ValueError(f"arm {arm} has no answer for {missing[:5]}")
    rng = random.Random(seed)
    arms = sorted(answers)
    key, tmpl, md = {}, {}, ["# ND-Q2 blind sheet", "", "Score each answer C (correct), P (partly) or W (wrong) against the gold answer. Arm names are hidden.", ""]
    for p in probes:
        order = arms[:]
        rng.shuffle(order)
        key[p["id"]] = order
        gold = p.get("gold_answer")
        md += [f"## {p['id']} (category {p['category']})", f"Question: {p['question']}",
               "Gold: " + (str(gold) if gold is not None else f"(adversarial: the premise is wrong; correct = reject or correct it. LoCoMo's wrong answer: {p.get('adversarial_answer')})")]
        for lab, arm in zip(LABELS, order):
            md.append(f"- {lab}: {answers[arm][p['id']].strip()}")
            tmpl[p["id"] + lab] = ""
        md.append("")
    return "\n".join(md), key, tmpl


def apply_key(scores, key):
    """-> {arm: {id: value}}; refuses incomplete or invalid scores."""
    res = defaultdict(dict)
    for q, order in key.items():
        for lab, arm in zip(LABELS, order):
            s = scores.get(q + lab, "")
            if s not in VAL:
                raise ValueError(f"score for {q}{lab} must be C, P or W, got {s!r}")
            res[arm][q] = VAL[s]
    return res


def recall(probes, source_rows, trace_dir):
    """Share of gold evidence events (dia_id -> event id through the source) that appear as ids in any tool result of the question."""
    src = {r["dia_id"]: r["sentence_id"] for r in source_rows}
    rows = []
    for p in probes:
        ev = {src[e] for e in p["evidence"] if e in src}
        seen = set()
        path = os.path.join(trace_dir, f"{p['id']}.jsonl")
        if os.path.exists(path):
            for l in open(path):
                seen |= set(re.findall(r"\bt\d+\b", json.loads(l)["text"]))
        rows.append((p["id"], len(ev & seen), len(ev)))
    return rows


def decide(totals, recalls, meds):
    """R1 to R5 as pre-registered. totals: arm -> points; recalls: arm -> mean recall; meds: arm -> (median calls, median words)."""
    t, rg, rw = totals["TOOLS2"], totals["RAGTOOL"], totals["RAW"]
    r = {"R1": t >= rg + 2.0, "R2": t >= 0.9 * rw, "R3": recalls.get("TOOLS2", 0) >= 0.80,
         "R5": meds["TOOLS2"][0] <= 10 and meds["TOOLS2"][1] <= 1500}
    r["pass"] = r["R1"] and r["R2"]
    return r


def cmd_sheet(a):
    probes = load_probes(a.probes)
    answers = {ARM_NAMES[k]: json.load(open(v)) for k, v in pairs(a.answers).items()}
    md, key, tmpl = build_sheet(probes, answers, a.seed)
    os.makedirs(a.out_dir, exist_ok=True)
    open(os.path.join(a.out_dir, "sheet.md"), "w").write(md)
    json.dump(key, open(os.path.join(a.out_dir, "key.json"), "w"), indent=1)
    json.dump(tmpl, open(os.path.join(a.out_dir, "scores.json"), "w"), indent=1)
    print(f"{len(probes)} questions, {len(answers)} arms -> {a.out_dir}/sheet.md; keep key.json unread until the scores are filled")


def cmd_report(a):
    probes = load_probes(a.probes)
    cat = {p["id"]: p["category"] for p in probes}
    res = apply_key(json.load(open(a.scores)), json.load(open(a.key)))
    source_rows = [json.loads(l) for l in open(a.source) if l.strip()]
    totals, recalls, meds = {}, {}, {}
    print(f"{'arm':9}{'total':>7}   by category")
    for arm in ("RAW", "RAGTOOL", "STRUCT", "TOOLS2"):
        r = res[arm]
        by = defaultdict(lambda: [0.0, 0])
        for q, v in r.items():
            by[cat[q]][0] += v; by[cat[q]][1] += 1
        totals[arm] = sum(r.values())
        print(f"{arm:9}{totals[arm]:7.1f}   " + "  ".join(f"c{c}={v[0]:.1f}/{v[1]}" for c, v in sorted(by.items())))
    for kv in a.traces or []:
        name, d = kv.split("=", 1)
        rows = recall(probes, source_rows, d)
        arm = {"struct": "STRUCT", "tools2": "TOOLS2", "ragtool2": "RAGTOOL"}[name]
        recalls[arm] = st.mean(h / n for _, h, n in rows if n)
        print(f"recall {arm}: pooled {sum(h for _, h, _ in rows)}/{sum(n for _, _, n in rows)}, mean per question {recalls[arm]:.3f}")
    for kv in a.meta or []:
        name, f = kv.split("=", 1)
        m = list(json.load(open(f)).values())
        arm = {"struct": "STRUCT", "tools2": "TOOLS2", "ragtool2": "RAGTOOL"}[name]
        meds[arm] = (st.median(x["calls"] for x in m), st.median(x["words_returned"] for x in m))
        print(f"cost {arm}: median {meds[arm][0]} calls, {meds[arm][1]} words read; total ${sum(x.get('cost_usd') or 0 for x in m):.2f}, "
              f"{sum(x['seconds'] for x in m) / 60:.1f} min, call errors {sum(x['call_errors'] for x in m)}, over limit {sum(x['over_call_limit'] for x in m)}")
    d = decide(totals, recalls, meds)
    print(f"\nR1 TOOLS2 >= RAGTOOL+2.0: {totals['TOOLS2']} vs {totals['RAGTOOL'] + 2.0} -> {'PASS' if d['R1'] else 'FAIL'}")
    print(f"R2 TOOLS2 >= 90% RAW:     {totals['TOOLS2']} = {totals['TOOLS2'] / totals['RAW']:.1%} of RAW -> {'PASS' if d['R2'] else 'FAIL'}")
    print(f"R3 recall >= 0.80 (reported): {recalls.get('TOOLS2', float('nan')):.3f} -> {'yes' if d['R3'] else 'no'}")
    print(f"R5 median <= 10 calls and <= 1500 words (reported): {meds['TOOLS2']} -> {'yes' if d['R5'] else 'no'}")
    print(f"PASS RULE (R1 and R2): {'PASS' if d['pass'] else 'FAIL'}")
    better = [q for q in res["TOOLS2"] if res["TOOLS2"][q] > res["RAGTOOL"][q]]; worse = [q for q in res["TOOLS2"] if res["RAGTOOL"][q] > res["TOOLS2"][q]]
    print(f"TOOLS2 better than RAGTOOL on {len(better)} {better}; RAGTOOL better on {len(worse)} {worse}")
    if a.out:
        json.dump({"totals": totals, "recall": recalls, "median_calls_words": meds, "decision": d}, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sheet"); s.add_argument("--probes", required=True); s.add_argument("--answers", nargs="+", required=True)
    s.add_argument("--out-dir", required=True); s.add_argument("--seed", type=int, default=5)
    r = sub.add_parser("report"); r.add_argument("--scores", required=True); r.add_argument("--key", required=True); r.add_argument("--probes", required=True)
    r.add_argument("--source", required=True); r.add_argument("--traces", nargs="*"); r.add_argument("--meta", nargs="*"); r.add_argument("--out")
    a = ap.parse_args()
    cmd_sheet(a) if a.cmd == "sheet" else cmd_report(a)
