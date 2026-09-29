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
    return re.sub(r"(ly|ing|ed|es|s)$", "", re.sub(r"fully$", "ful", t))


# Amendment 1 (EXP-ND1.md): annotation-label dimensions describe the sentence
# (role, time, status, source) rather than quote it. They are exempt from lexical
# traceability (M2a) but must not introduce pegs absent from the sentence (M2b).
LABEL_DIM = re.compile(r"^(role|role_in_event|temporal_\w*|\w*_status|status|epistemic_\w*|type|"
                       r"specificity|persistence|qualifier|certainty\w*|reference_status)$")


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

    # M2 faithfulness. run-1 definition kept for comparability; amended M2a/M2b decide pass.
    pron = {"he", "she", "him", "her", "his", "they", "them", "their", "it", "its", "this", "that"}
    names = [(e["tick"], p) for e in E for p in e["participants"] if norm(p) not in pron]
    bad_names = [f"{t}:{p}" for t, p in names if traceable(p, src[t]) < 1.0]
    vals = [(s["tick"], s["peg"], s["dim"], s["value"]) for s in S]
    bad_all = [f"{t}:{p}.{d} = {v}" for t, p, d, v in vals if traceable(v, src[t]) < 0.5]
    content = [v for v in vals if not LABEL_DIM.match(v[2])]
    labels = [s for s in S if LABEL_DIM.match(s["dim"])]
    bad_content = [f"{t}:{p}.{d} = {v}" for t, p, d, v in content if traceable(v, src[t]) < 0.5]
    label_new_pegs = sorted({f"{s['tick']}:{l}" for s in labels for l in s["links"]
                             if traceable(l, src[s["tick"]]) < 1.0})
    n_a = len(names) + len(content)
    r["M2"] = {"run1_definition_rate": round(1 - (len(bad_names) + len(bad_all)) / (len(names) + len(vals)), 3),
               "M2a_content_traceable_rate": round(1 - (len(bad_names) + len(bad_content)) / n_a, 3),
               "M2b_label_introduced_pegs": label_new_pegs,
               "untraceable_names": bad_names, "untraceable_content_values": bad_content}
    r["M2"]["traceable_rate"] = r["M2"]["M2a_content_traceable_rate"]
    r["M2"]["pass"] = r["M2"]["M2a_content_traceable_rate"] >= 0.95 and not label_new_pegs

    # M4 must-haves. Names are compared normalised so different valid spellings pass.
    def at(t):
        return [s for s in S if s["tick"] == t]
    def has(names, want):
        return any(norm(want) == norm(n) or norm(want) in norm(n).split(" ") for n in names)
    parts = {e["tick"]: [norm(p) for p in e["participants"]] for e in E}
    b_at = {}
    for b in B:
        b_at.setdefault(b["tick"], []).append(b)
    def cand_text(b):
        return " | ".join(norm(str(c)) for c in b["candidates"])
    mh = {}
    bob4 = [s for s in at(4) if norm(s["peg"]) == "bob" and re.search(r"propos", s["value"] + s["dim"])
            and ("redis" in norm(s["value"]) or any(norm(l) == "redis" for l in s["links"]))]
    mh["MH1"] = bool(bob4) and "alice" not in parts[4]
    b4 = [b for b in b_at.get(4, []) if b["state"] == "open"]
    mh["MH2"] = any("payments platform" in cand_text(b) and "separate service" in cand_text(b) for b in b4)
    b5 = [b for b in b_at.get(5, [])]
    mh["MH3"] = bool(b5) and all(b["state"] == "open" and b.get("model_belief") is None
                                 and not any(x["bucket"] == b["id"] for x in state["resolutions"]) for b in b5)
    res5 = [s for s in at(5) if re.search(r"success|passed", s["value"]) and not LABEL_DIM.match(s["dim"])]
    mh["MH4"] = bool(res5) and all(s["status"] == "claim" and norm(s["owner"] or "") == "alice" for s in res5)
    might6 = [s for s in at(6) if re.search(r"\bmight\b", s["value"])]
    mh["MH5"] = bool(might6) and all(s["status"] == "speaker_belief" and s["modality"] == "possible"
                                     and norm(s["owner"] or "") == "bob" for s in might6)
    mh["MH6"] = not any(re.search(r"stance_relative|different preference|disagree", f"{s['dim']} {s['value']}")
                        and s["status"] in ("fact", "claim") for s in at(9))
    mh["MH7"] = all(x in parts[0] for x in ("alice", "postgresql")) and all(x in parts[8] for x in ("alice", "postgresql"))
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
    print("M2a content traceable:", out["M2"]["M2a_content_traceable_rate"], "| M2b label-introduced pegs",
          len(out["M2"]["M2b_label_introduced_pegs"]), "| pass", out["M2"]["pass"],
          "| (run-1 definition:", out["M2"]["run1_definition_rate"], ")")
    print("M4 must-haves:", out["M4"]["passed"], "/", out["M4"]["of"], out["M4"]["checks"])
    print("diagnostics:", json.dumps(out["diagnostics"], indent=1))
