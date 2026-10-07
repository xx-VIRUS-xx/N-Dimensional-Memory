"""Synonym candidates among the types and role names of an ND-E extraction (report only; nothing is merged or changed).

  python3 tools/nde_synonyms.py --extraction <run.jsonl> --out <dir>

Writes <dir>/synonym_candidates.json and .md. Code proposes pairs; a person (or, in a later consolidation pass, an LLM
shown these examples) decides. Signals per pair of types: shared specific role names, shared non-hub linked entities,
shared name tokens (travel / travel_return). Generic roles (used by a fifth of all types, like time) and hub entities
(linked in 30% of relations, like the two speakers) are ignored. A role pair inside one type is reported when the names share a stem
(companion / companions) or a token. Standard library only.
"""
import argparse
import json
import os
import re


def rels(row):
    return row["relations"] if "relations" in row else row["events"]


def tokens(name):
    return {t for t in name.split("_") if t}


def stem(t):
    return re.sub(r"(ing|ed|es|s)$", "", t) if len(t) > 4 else t


def jaccard(a, b):
    return len(a & b) / len(a | b) if (a | b) else 0.0


def profile(rows):
    types = {}
    for r in rows:
        for ev in rels(r):
            p = types.setdefault(ev["type"], {"count": 0, "roles": {}, "entities": set(), "ent_counts": {}, "example": None, "turns": []})
            p["count"] += 1
            p["turns"].append(r["event_id"])
            for role, s in ev["slots"].items():
                p["roles"][role] = p["roles"].get(role, 0) + 1
                if s["link"]:
                    e = s["link"].lower()
                    p["entities"].add(e)
                    p["ent_counts"][e] = p["ent_counts"].get(e, 0) + 1
            if p["example"] is None:
                p["example"] = {"turn": r["event_id"], **{k: v["value"] for k, v in ev["slots"].items()}}
    return types


def generic_roles(types, share=0.2):
    """Roles used by at least `share` of all types (time, recipient, ...) say nothing about two types being alike."""
    n = max(len(types), 1)
    count = {}
    for p in types.values():
        for r in p["roles"]:
            count[r] = count.get(r, 0) + 1
    return {r for r, c in count.items() if c / n >= share and c > 1}


def hub_entities(types, rows_total, share=0.3):
    """Entities linked in at least `share` of all relations are hubs (the speakers); sharing them proves nothing."""
    count, total = {}, 0
    for p in types.values():
        total += p["count"]
        for e, c in p["ent_counts"].items():
            count[e] = count.get(e, 0) + c
    return {e for e, c in count.items() if total and c / total >= share}


def candidates(types, min_shared_roles=2, min_shared_entities=2):
    names, out = sorted(types), []
    gen, hubs = generic_roles(types), hub_entities(types, None)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            pa, pb = types[a], types[b]
            roles = sorted((set(pa["roles"]) & set(pb["roles"])) - gen)
            ents = sorted((pa["entities"] & pb["entities"]) - hubs)
            ta = {stem(t) for t in tokens(a)}
            tb = {stem(t) for t in tokens(b)}
            shared = sorted(ta & tb)
            reasons = []
            if len(roles) >= min_shared_roles:
                reasons.append("share specific role names " + "/".join(roles))
            if len(ents) >= min_shared_entities:
                reasons.append("share linked entities " + "/".join(ents))
            if shared:
                reasons.append("share name token " + "/".join(shared))
            if reasons:
                out.append({"a": a, "b": b, "reasons": reasons, "counts": [pa["count"], pb["count"]],
                            "examples": [pa["example"], pb["example"]]})
    out.sort(key=lambda c: (-len(c["reasons"]), c["a"], c["b"]))
    return out


def role_variants(types):
    out = []
    for t, p in sorted(types.items()):
        rs = sorted(p["roles"])
        for i, a in enumerate(rs):
            for b in rs[i + 1:]:
                if {stem(x) for x in tokens(a)} & {stem(x) for x in tokens(b)}:
                    out.append({"type": t, "a": a, "b": b, "counts": [p["roles"][a], p["roles"][b]]})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--extraction", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    rows = [json.loads(l) for l in open(a.extraction) if l.strip()]
    types = profile(rows)
    cands, rvars = candidates(types), role_variants(types)
    os.makedirs(a.out, exist_ok=True)
    json.dump({"types": len(types), "type_pairs": cands, "role_variants": rvars},
              open(os.path.join(a.out, "synonym_candidates.json"), "w"), indent=1, ensure_ascii=False)
    lines = [f"# Synonym candidates ({len(types)} types, {len(cands)} pairs, {len(rvars)} role variants)", "",
             "Report only. Mark each pair: same / parent-child / different.", ""]
    for c in cands:
        lines += [f"## {c['a']} ({c['counts'][0]}) vs {c['b']} ({c['counts'][1]})", "- " + "; ".join(c["reasons"]),
                  f"- {c['a']}: {json.dumps(c['examples'][0], ensure_ascii=False)}",
                  f"- {c['b']}: {json.dumps(c['examples'][1], ensure_ascii=False)}", "- verdict: ", ""]
    if rvars:
        lines += ["## Role name variants within a type", ""]
        lines += [f"- {v['type']}: {v['a']} ({v['counts'][0]}) / {v['b']} ({v['counts'][1]})" for v in rvars]
    open(os.path.join(a.out, "synonym_candidates.md"), "w").write("\n".join(lines) + "\n")
    print(f"{len(types)} types, {len(cands)} candidate pairs, {len(rvars)} role variants -> {a.out}")


if __name__ == "__main__":
    main()
