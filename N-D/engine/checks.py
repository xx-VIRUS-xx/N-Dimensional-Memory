"""ND-1 scoring for metrics that need no LLM: M1 contract, M2 faithfulness,
M4 must-haves, plus diagnostics. Probe accuracy (M3) is in probe_harness.py.

Usage: python engine/checks.py <state.json> <source.jsonl> <out.json>
"""
import itertools
import json
import re
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from nd_engine import content_tokens, norm  # noqa: E402

# Measurement patterns (same literal families as ND-0 so numbers are comparable).
ABSENCE = re.compile(r"not stated|unspecified|unknown|not recorded|not specified", re.I)
INFERENCE = re.compile(r"suggests|implying|implied|indicates", re.I)


def stem(t):
    return re.sub(r"(ing|ed|es|s)$", "", t)


def traceable(text, source):
    toks = content_tokens(text)
    if not toks:
        return 1.0
    src = {stem(t) for t in content_tokens(source)}
    return sum(stem(t) in src for t in toks) / len(toks)


def score(state, sources):
    src = {i: s["text"] for i, s in enumerate(sources)}
    S, B, E = state["strings"], state["buckets"], state["events"]
    r = {}

    # M1 contract violations remaining after E4
    r["M1"] = {"stored_absences": [f"{s['tick']}:{s['peg']}.{s['dim']}" for s in S if ABSENCE.search(s["value"])],
               "unflagged_inferences": [f"{s['tick']}:{s['peg']}.{s['dim']}" for s in S
                                        if INFERENCE.search(f"{s['dim']} {s['value']}")]}
    r["M1"]["pass"] = not r["M1"]["stored_absences"] and not r["M1"]["unflagged_inferences"]

    # M2 faithfulness: entity names fully traceable; values >= 50% content words traceable
    names = [(e["tick"], p) for e in E for p in e["participants"]]
    bad_names = [f"{t}:{p}" for t, p in names if traceable(p, src[t]) < 1.0]
    vals = [(s["tick"], s["peg"], s["dim"], s["value"]) for s in S]
    bad_vals = [f"{t}:{p}.{d} = {v}" for t, p, d, v in vals if traceable(v, src[t]) < 0.5]
    total = len(names) + len(vals)
    r["M2"] = {"traceable_rate": round(1 - (len(bad_names) + len(bad_vals)) / total, 3),
               "untraceable_names": bad_names, "untraceable_values": bad_vals}
    r["M2"]["pass"] = r["M2"]["traceable_rate"] >= 0.95

    # M4 must-haves
    def at(t):
        return [s for s in S if s["tick"] == t]
    parts = {e["tick"]: set(e["participants"]) for e in E}
    b_at = {b["tick"]: b for b in B}
    mh = {}
    bob4 = [s for s in at(4) if s["peg"] == "Bob" and re.search(r"propos", s["value"]) and "Redis" in s["links"]]
    mh["MH1"] = bool(bob4) and "Alice" not in parts[4]
    b4 = b_at.get(4)
    mh["MH2"] = bool(b4) and b4["state"] == "open" and {"payments platform", "separate service"} <= set(b4["candidates"])
    b5 = b_at.get(5)
    mh["MH3"] = bool(b5) and b5["state"] == "open" and b5.get("model_belief") is None \
        and not any(x["bucket"] == b5["id"] for x in state["resolutions"])
    res5 = [s for s in at(5) if re.search(r"success", s["value"])]
    mh["MH4"] = bool(res5) and all(s["status"] == "claim" and s["owner"] == "Alice" for s in res5)
    might6 = [s for s in at(6) if re.search(r"\bmight\b", s["value"])]
    mh["MH5"] = bool(might6) and all(s["status"] == "speaker_belief" and s["modality"] == "possible"
                                     and s["owner"] == "Bob" for s in might6)
    mh["MH6"] = not any(re.search(r"stance_relative|different preference", f"{s['dim']} {s['value']}") for s in at(9))
    mh["MH7"] = {"Alice", "PostgreSQL"} <= parts[0] and {"Alice", "PostgreSQL"} <= parts[8]
    r["M4"] = {"checks": mh, "passed": sum(mh.values()), "of": len(mh)}

    # Diagnostics
    colliding = sum(1 for a, b in itertools.combinations(E, 2) if set(a["participants"]) & set(b["participants"]))
    deg = {}
    for e in E:
        for p in e["participants"]:
            deg[p] = deg.get(p, 0) + 1
    r["diagnostics"] = {
        "strings_with_peg_links": round(sum(bool(s["links"]) for s in S) / len(S), 3),
        "single_event_pegs": round(sum(v == 1 for v in deg.values()) / len(deg), 3),
        "colliding_event_pairs": colliding,
        "buckets": [{k: b[k] for k in ("id", "tick", "state", "candidates") if k in b} | {"resolved_by": b.get("resolved_by")} for b in B],
        "identity_proposals_pending": len(state["proposals"]),
        "dropped_absences": len(state["dropped_absences"]),
        "model_belief_candidates": len(state["model_belief_candidates"]),
        "status_counts": {k: sum(s["status"] == k for s in S) for k in
                          ("fact", "claim", "speaker_belief", "open_question", "intent")},
    }
    return r


if __name__ == "__main__":
    st = json.load(open(sys.argv[1]))
    srcs = [json.loads(l) for l in open(sys.argv[2]) if l.strip()]
    out = score(st, srcs)
    json.dump(out, open(sys.argv[3], "w"), indent=2)
    print("M1 pass:", out["M1"]["pass"], "| absences", len(out["M1"]["stored_absences"]),
          "| inferences", len(out["M1"]["unflagged_inferences"]))
    print("M2 traceable:", out["M2"]["traceable_rate"], "| pass", out["M2"]["pass"],
          "| bad names", len(out["M2"]["untraceable_names"]), "| bad values", len(out["M2"]["untraceable_values"]))
    print("M4 must-haves:", out["M4"]["passed"], "/", out["M4"]["of"], out["M4"]["checks"])
    print("diagnostics:", json.dumps(out["diagnostics"], indent=1))
