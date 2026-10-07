"""M6 and M7 of ND-E: what narrowing the stored relations would allow for the evidence events of the probe questions.

  python3 tools/nde_evidence.py --extraction <run.jsonl> --source <source.jsonl> --probes <probes.jsonl> --out <dir>

The evidence events (dia_ids of the probes in categories 1 to 4, mapped to event ids through the source) are an oracle for what
narrowing is possible, not an answer check. Two arms, both reported:
  slots      keys come from linked slot values only (the spec rule; thresholds apply)
  +entities  keys also come from the event's own Entities list (amendment 2, reported beside)
Two readings of "I" and "you":
  as stored  pronouns stay as the model wrote them
  joined     "I" is the source speaker and "you" the source listener of that event, joined on event_id here, never in the rows
Keys: an entity key is a linked value that is not a hub name (the speakers of the source) and not a pronoun. A role key is
(type, role, value) for a linked value, hub names included (joined pronouns become hub names). M6: evidence events with no entity key.
M7: for evidence events with at least one key, the size of the smallest candidate set (events in the whole run sharing that key);
the share of those events with a smallest set <= 10. Events missing from the extraction are counted as not covered.
Writes <dir>/nde_evidence.json and .md. Standard library only.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_events import norm_entity  # noqa: E402
from nde_synonyms import PRONOUNS, rels  # noqa: E402


def load(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def evidence_events(probes, source, categories=(1, 2, 3, 4)):
    by_dia = {s["dia_id"]: s["sentence_id"] for s in source}
    ids, missing = [], []
    for q in probes:
        if q.get("category") not in categories:
            continue
        for d in q.get("evidence", []):
            if d in by_dia:
                if by_dia[d] not in ids:
                    ids.append(by_dia[d])
            else:
                missing.append(d)
    return ids, missing


def hubs_of(source):
    return {norm_entity(s[k]) for s in source for k in ("speaker", "listener") if s.get(k)}


def keys_of(row, who, hubs, join, with_entities):
    """Returns (entity_keys, role_keys) of one stored event. who = (speaker, listener) of the source row."""
    ent, role = set(), set()

    def val(v):
        n = norm_entity(v)
        if join and n == "i" and who[0]:
            return norm_entity(who[0])
        if join and n == "you" and who[1]:
            return norm_entity(who[1])
        return n

    for r in rels(row):
        for rname, slot in r["slots"].items():
            if slot.get("link") is None:
                continue
            v = val(slot["link"])
            role.add((r["type"], rname, v))
            if v not in hubs and v not in PRONOUNS:
                ent.add(v)
    if with_entities:
        for e in row.get("Entities", []):
            v = val(e)
            if v not in hubs and v not in PRONOUNS:
                ent.add(v)
    return ent, role


def measure(rows, source, evidence, join, with_entities):
    hubs = hubs_of(source)
    who = {s["sentence_id"]: (s.get("speaker"), s.get("listener")) for s in source}
    keyed = {r["event_id"]: keys_of(r, who.get(r["event_id"], (None, None)), hubs, join, with_entities) for r in rows}
    count = {}
    for ent, role in keyed.values():
        for k in ent:
            count[("e", k)] = count.get(("e", k), 0) + 1
        for k in role:
            count[("r", k)] = count.get(("r", k), 0) + 1
    covered = [e for e in evidence if e in keyed]
    no_entity_key, sizes, detail = 0, [], []
    for e in covered:
        ent, role = keyed[e]
        if not ent:
            no_entity_key += 1
        cand = [count[("e", k)] for k in ent] + [count[("r", k)] for k in role]
        best = min(cand) if cand else None
        if best is not None:
            sizes.append(best)
        detail.append({"event": e, "entity_keys": sorted(ent), "smallest_candidate_set": best})
    n = len(covered)
    return {
        "evidence_events": len(evidence), "covered": n,
        "M6_no_entity_key": no_entity_key, "M6_share": (no_entity_key / n) if n else None,
        "M7_events_with_key": len(sizes), "M7_le10": sum(1 for s in sizes if s <= 10),
        "M7_share_le10": (sum(1 for s in sizes if s <= 10) / len(sizes)) if sizes else None,
        "M7_overall_share_le10": (sum(1 for s in sizes if s <= 10) / n) if n else None,
        "detail": detail,
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--extraction", required=True)
    ap.add_argument("--source", required=True)
    ap.add_argument("--probes", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    rows, source, probes = load(a.extraction), load(a.source), load(a.probes)
    evidence, missing = evidence_events(probes, source)
    out = {"events_in_run": len(rows), "unmapped_dia_ids": missing, "arms": {}}
    for arm, we in (("slots", False), ("+entities", True)):
        for reading, join in (("as stored", False), ("joined", True)):
            out["arms"][f"{arm} / {reading}"] = measure(rows, source, evidence, join, we)
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "nde_evidence.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    lines = ["# ND-E M6 / M7 (evidence oracle)", "",
             f"Events in run: {out['events_in_run']}. Evidence events (categories 1 to 4, unique): {len(evidence)}. Unmapped dia_ids: {len(missing)}.", "",
             "| arm / reading of I, you | covered | M6 no entity key (<=10%) | M7 smallest set <=10, events with a key (>=90%) | M7 over all covered |", "|---|---|---|---|---|"]
    for k, m in out["arms"].items():
        def pct(x):
            return "n/a" if x is None else f"{100 * x:.0f}%"
        lines.append(f"| {k} | {m['covered']} | {m['M6_no_entity_key']} ({pct(m['M6_share'])}) | {m['M7_le10']}/{m['M7_events_with_key']} ({pct(m['M7_share_le10'])}) | {pct(m['M7_overall_share_le10'])} |")
    with open(os.path.join(a.out, "nde_evidence.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
