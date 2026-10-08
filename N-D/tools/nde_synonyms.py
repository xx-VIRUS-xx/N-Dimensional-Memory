"""Synonym candidates among the types and role names of an ND-E extraction (report only; nothing is merged or changed).

  python3 tools/nde_synonyms.py --extraction <run.jsonl> --out <dir>

Writes <dir>/synonym_candidates.json and .md. Code proposes pairs; a person (or, in a later consolidation pass, an LLM
shown these examples) decides. Signals per pair of types: shared specific role names, shared non-hub, non-pronoun linked entities,
shared name tokens (travel / travel_return). Generic roles (used by a fifth of all types, like time) and hub entities
(linked in 30% of relations, like the two speakers) are ignored. A role pair inside one type is reported when the names share a stem
(companion / companions) or a token. Standard library only.
"""
import argparse
import json
import os
import re


PRONOUNS = {"i", "me", "my", "mine", "myself", "you", "your", "yours", "yourself", "we", "us", "our", "ours", "ourselves", "it", "its",
            "that", "this", "there", "they", "them", "their", "he", "him", "his", "she", "her", "hers"}


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
            p = types.setdefault(ev["type"], {"count": 0, "roles": {}, "entities": set(), "ent_counts": {}, "example": None, "events": []})
            p["count"] += 1
            p["events"].append(r["event_id"])
            for role, s in ev["slots"].items():
                p["roles"][role] = p["roles"].get(role, 0) + 1
                if s["link"]:
                    e = s["link"].lower()
                    if e in PRONOUNS:
                        continue                                   # pronouns say nothing about two types being alike
                    p["entities"].add(e)
                    p["ent_counts"][e] = p["ent_counts"].get(e, 0) + 1
            if p["example"] is None:
                p["example"] = {"event": r["event_id"], **{k: v["value"] for k, v in ev["slots"].items()}}
    return types


def _base(role):
    """object_2 and object are one role name for comparing types; the numbered copy only records a second value."""
    return re.sub(r"_\d+$", "", role)


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


def candidates(types, min_shared_roles=2, min_shared_entities=3, min_entity_overlap=0.3, hub_names=()):
    names, out = sorted(types), []
    gen = generic_roles(types)
    total = sum(p["count"] for p in types.values()) or 1
    catch_all = {t for t, p in types.items() if p["count"] / total >= 0.25}   # a type that holds a quarter of everything (state) shares entities with all
    hubs = hub_entities(types, None) | {h.lower() for h in hub_names}
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            pa, pb = types[a], types[b]
            roles = sorted(({_base(x) for x in pa["roles"]} & {_base(x) for x in pb["roles"]}) - gen)
            ents = sorted((pa["entities"] & pb["entities"]) - hubs)
            ta = {stem(t) for t in tokens(a)}
            tb = {stem(t) for t in tokens(b)}
            shared = sorted(ta & tb)
            reasons = []
            if len(roles) >= min_shared_roles:
                reasons.append("share specific role names " + "/".join(roles))
            smaller = min(len(pa["entities"] - hubs), len(pb["entities"] - hubs)) or 1
            if a not in catch_all and b not in catch_all and len(ents) >= min_shared_entities and len(ents) / smaller >= min_entity_overlap:
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


def role_families(rows, min_uses=10, share=0.5):
    """Role names of different types whose linked values are mostly the same speaker pronoun (thanker, hoper, promiser: all "I").
    Report only: these are candidates for one actor role, which the stored rows keep apart."""
    uses = {}
    for r in rows:
        for ev in rels(r):
            for role, s in ev["slots"].items():
                if s["link"]:
                    u = uses.setdefault(role, {"n": 0, "pron": {}, "types": set()})
                    u["n"] += 1
                    u["types"].add(ev["type"])
                    e = s["link"].lower()
                    if e in PRONOUNS:
                        u["pron"][e] = u["pron"].get(e, 0) + 1
    fam = {}
    for role, u in uses.items():
        if u["n"] >= min_uses and u["pron"]:
            top, c = max(u["pron"].items(), key=lambda kv: kv[1])
            if c / u["n"] >= share:
                fam.setdefault(top, []).append({"role": role, "uses": u["n"], "share": round(c / u["n"], 2), "types": sorted(u["types"])})
    return {k: sorted(v, key=lambda x: -x["uses"]) for k, v in fam.items() if len(v) > 1}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--extraction", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--source", help="source jsonl; its speaker and listener names are treated as hubs")
    a = ap.parse_args(argv)
    rows = [json.loads(l) for l in open(a.extraction) if l.strip()]
    hub_names = set()
    if a.source:
        for line in open(a.source):
            if line.strip():
                d = json.loads(line)
                hub_names |= {d[k] for k in ("speaker", "listener") if d.get(k)}
    types = profile(rows)
    cands, rvars, fams = candidates(types, hub_names=hub_names), role_variants(types), role_families(rows)
    os.makedirs(a.out, exist_ok=True)
    json.dump({"types": len(types), "type_pairs": cands, "role_variants": rvars, "role_families": fams},
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
    if fams:
        lines += ["", "## Role families (different types, linked values mostly the same pronoun)", ""]
        for pron, items in sorted(fams.items()):
            lines.append(f"- {pron}: " + ", ".join(f"{i['role']} ({i['uses']})" for i in items))
    open(os.path.join(a.out, "synonym_candidates.md"), "w").write("\n".join(lines) + "\n")
    print(f"{len(types)} types, {len(cands)} candidate pairs, {len(rvars)} role variants -> {a.out}")


if __name__ == "__main__":
    main()
