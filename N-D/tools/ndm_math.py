"""N-D incidence math: metrics over an extracted corpus.

Reads either the BabyTest entity-centric format or the N-D event-star format
(schema/event.schema.json) and reports shape, geometry and epistemic metrics.
Usage: python tools/ndm_math.py <file.jsonl> [--json out.json]
"""
import itertools, json, math, re, sys, collections
import numpy as np

ABSENCE = re.compile(r"not stated|unspecified|unknown|not recorded|not specified", re.I)
INFERENCE = re.compile(r"suggests|implying|implied|indicates", re.I)
STORYLINES = [("Alice", "PostgreSQL"), ("Carol", "Redis")]


def load(path):
    rows = [json.loads(l) for l in open(path) if l.strip()]
    return ("star" if "roles" in rows[0] else "babytest"), rows


def strings_babytest(rows):
    """-> list of (event_id, peg_or_None, dimension, value_text, participants)"""
    out, inc = [], []
    names = {x["name"] for r in rows for x in r["entities"]}
    for r in rows:
        inc.append({x["name"] for x in r["entities"]})
        for x in r["entities"]:
            for d, v in x["dimensions"].items():
                out.append({"ev": r["event_id"], "peg": x["name"], "dim": d, "val": str(v),
                            "val_is_peg": str(v) in names, "bucket": bool(re.search(r"\bambiguous\b|candidate_scopes", f"{d} {v}"))})
    return out, inc


def strings_star(rows):
    out, inc = [], []
    for r in rows:
        parts = set()
        spk = r["source"].get("speaker")
        if spk: parts.add(spk)
        own = r["status"].get("owner")
        if own: parts.add(own)
        for d, f in r["roles"].items():
            if "peg" in f:
                parts.add(f["peg"]); out.append({"ev": r["tick"], "dim": d, "val": f["peg"], "val_is_peg": True, "bucket": False})
            elif "pegs" in f:
                parts.update(f["pegs"])
                for p in f["pegs"]: out.append({"ev": r["tick"], "dim": d, "val": p, "val_is_peg": True, "bucket": False})
            elif "lit" in f:
                out.append({"ev": r["tick"], "dim": d, "val": f["lit"], "val_is_peg": False, "bucket": False})
            elif "event" in f:
                out.append({"ev": r["tick"], "dim": d, "val": f"event:{f['event']}", "val_is_peg": True, "bucket": False})
            elif "bucket" in f:
                out.append({"ev": r["tick"], "dim": d, "val": json.dumps(f["bucket"]["candidates"]), "val_is_peg": False, "bucket": True})
        inc.append(parts)
    return out, inc


def analyse(path):
    fmt, rows = load(path)
    s, inc = (strings_star if fmt == "star" else strings_babytest)(rows)
    ids = [r.get("tick", r.get("event_id")) for r in rows]
    pegs = sorted(set().union(*inc)); P = {p: i for i, p in enumerate(pegs)}
    B = np.zeros((len(pegs), len(rows)), int)
    for k, parts in enumerate(inc):
        for p in parts: B[P[p], k] = 1
    size = B.sum(0); deg = B.sum(1)
    aa = collections.Counter()
    for k in range(len(rows)):
        idx = np.nonzero(B[:, k])[0]
        for i, j in itertools.combinations(idx, 2):
            aa[tuple(sorted((pegs[i], pegs[j])))] += 1 / math.log(1 + size[k])
    ranking = [p for p, _ in aa.most_common()]
    dims = collections.Counter(x["dim"] for x in s)
    D = B.T @ B
    colliding = sum(1 for k, l in itertools.combinations(range(len(rows)), 2) if D[k, l] > 0)
    iso = [ids[k] for k in range(len(rows)) if D[k].sum() - D[k, k] == 0]
    m = {
        "format": fmt, "events": len(rows), "pegs": len(pegs), "role_strings": len(s),
        "distinct_dimensions": len(dims),
        "singleton_dimension_rate": round(sum(1 for c in dims.values() if c == 1) / len(dims), 3),
        "value_is_peg_rate": round(sum(x["val_is_peg"] for x in s) / len(s), 3),
        "mean_words_per_value": round(float(np.mean([len(x["val"].split()) for x in s if not x["bucket"]])), 2),
        "single_event_peg_rate": round(float((deg == 1).mean()), 3),
        "colliding_event_pairs": colliding, "isolated_events": iso,
        "storyline_ranks": {f"{a}~{b}": (ranking.index(tuple(sorted((a, b)))) + 1 if tuple(sorted((a, b))) in aa else None) for a, b in STORYLINES},
        "top_pairs": [[a, b, round(w, 2)] for (a, b), w in aa.most_common(6)],
        "buckets": sum(x["bucket"] for x in s),
        "stored_absences": sum(bool(ABSENCE.search(x["val"])) for x in s),
        "inference_markers": sum(bool(INFERENCE.search(f"{x['dim']} {x['val']}")) for x in s),
        "trajectories": {p: [ids[k] for k in np.nonzero(B[P[p]])[0]] for p in pegs if deg[P[p]] >= 2},
    }
    if fmt == "star":
        m["status_counts"] = dict(collections.Counter(r["status"]["type"] for r in rows))
    return m


if __name__ == "__main__":
    m = analyse(sys.argv[1])
    if "--json" in sys.argv:
        json.dump(m, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=2)
    for k, v in m.items():
        print(f"{k:26s} {v}")
