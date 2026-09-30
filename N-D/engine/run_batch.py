"""ND-1 run 2: engine + checks on every extraction, then M5 stability.

Usage: python engine/run_batch.py ND-1/results/run2 [tag] [--source path.jsonl]
With --source (a non-pilot corpus), the pilot must-haves (M4) are skipped.
Reads  <dir>/extractions/*.jsonl; writes <dir>/per_run[_<tag>]/<name>.{state,checks}.json
and <dir>/summary[_<tag>].json, and prints a table. Use a tag to rescore the same
extractions with a newer engine without overwriting earlier results.
"""
import glob
import itertools
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from checks import score  # noqa: E402
from nd_engine import norm, run  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def collisions(state, hubs=frozenset()):
    """Event pairs sharing a peg, ignoring hub pegs (dialogue participants, B2)."""
    E = state["events"]
    pegs = [{norm(p) for p in e["participants"]} - hubs for e in E]
    return {(E[i]["tick"], E[j]["tick"]) for i, j in itertools.combinations(range(len(E)), 2) if pegs[i] & pegs[j]}


def bucket_outcomes(state):
    return {(b["tick"], b["state"]) for b in state["buckets"]}


def jacc(a, b):
    return 1.0 if not a and not b else len(a & b) / len(a | b)


def main(d, tag=None, source=None):
    per = "per_run" + (f"_{tag}" if tag else "")
    summ = "summary" + (f"_{tag}" if tag else "") + ".json"
    pilot = os.path.join(ROOT, "ND-0", "data", "pilot10.source.jsonl")
    sources = [json.loads(l) for l in open(source or pilot)]
    musthaves = source is None
    hubs = frozenset(norm(x) for t in sources for x in (t.get("speaker"), t.get("listener")) if x)
    os.makedirs(os.path.join(d, per), exist_ok=True)
    rows, states = [], {}
    skipped = []
    for f in sorted(glob.glob(os.path.join(d, "extractions", "*.jsonl"))):
        name = os.path.basename(f)[:-6]
        n_lines = sum(1 for l in open(f) if l.strip())
        if not os.path.exists(f[:-6] + ".meta.json") or n_lines != len(sources):
            skipped.append(f"{name} ({n_lines}/{len(sources)} turns)")
            continue  # incomplete run: finish it with --resume before scoring
        st = run([json.loads(l) for l in open(f) if l.strip()])
        sc = score(st, sources, musthaves)
        json.dump(st, open(os.path.join(d, per, f"{name}.state.json"), "w"), indent=2)
        json.dump(sc, open(os.path.join(d, per, f"{name}.checks.json"), "w"), indent=2)
        states[name] = st
        rows.append({"run": name, "M1_pass": sc["M1"]["pass"], "input_issues": len(sc["M1"]["input_issues"]), "M2a": sc["M2"]["M2a_content_traceable_rate"],
                     "M2b_new_pegs": len(sc["M2"]["M2b_label_introduced_pegs"]), "M2_pass": sc["M2"]["pass"],
                     "M4": f"{sc['M4']['passed']}/{sc['M4']['of']}",
                     "M4_failed": [k for k, v in sc["M4"]["checks"].items() if not v],
                     "buckets": sorted(bucket_outcomes(st)), "colliding_pairs": len(collisions(st, hubs))})
    pairs = list(itertools.combinations(states, 2))
    m5 = {"hub_pegs_excluded": sorted(hubs),
          "collision_jaccard_min": round(min((jacc(collisions(states[a], hubs), collisions(states[b], hubs)) for a, b in pairs), default=1.0), 3),
          "bucket_outcome_jaccard_min": round(min((jacc(bucket_outcomes(states[a]), bucket_outcomes(states[b])) for a, b in pairs), default=1.0), 3),
          "runs": len(states)}
    json.dump({"runs": rows, "M5": m5}, open(os.path.join(d, summ), "w"), indent=2, default=list)
    for r in rows:
        print(f"{r['run']:45s} M1 {'ok' if r['M1_pass'] else 'FAIL'}{' (' + str(r['input_issues']) + ' input issues)' if r['input_issues'] else ''}  M2a {r['M2a']:.3f}  M2b {r['M2b_new_pegs']}  "
              f"M4 {r['M4']} {r['M4_failed'] or ''}  pairs {r['colliding_pairs']}  buckets {r['buckets']}")
    print("M5:", m5)
    if skipped:
        print("SKIPPED incomplete runs (finish with --resume):", ", ".join(skipped))


if __name__ == "__main__":
    args = sys.argv[1:]
    src = None
    if "--source" in args:
        i = args.index("--source"); src = args[i + 1]; del args[i:i + 2]
    main(args[0], args[1] if len(args) > 1 else None, src)
