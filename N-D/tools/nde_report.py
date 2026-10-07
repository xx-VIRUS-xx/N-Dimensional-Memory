"""ND-E measures M1-M5 and M8 (EXP-NDE.md) plus a hand-review file, from an extraction jsonl.

Vocabulary (amendment 4): an event is one sentence; its relations are the typed items of its EventRelation list. The spec's
"events" in M2, M3, M6 and M7 mean relations; the thresholds are unchanged. Rows written before amendment 4 say `events`.

  python3 tools/nde_report.py --extraction <run.jsonl> --source <source.jsonl> --out <dir> [--window 50]

Writes <dir>/nde_report.json and <dir>/review.md (per event: the sentence, the extraction, and each slot value marked
LINK or TEXT, so entity-like values that were left as text can be spotted by hand for M3).
M6 and M7 need the evidence oracle and run in Phase 2; they are not computed here.
"""
import argparse
import json
import os
import re
import statistics as st
from collections import Counter

CUE = re.compile(r"\b(yesterday|last (?:week|weekend|month|year|night|summer|winter|spring|fall|monday|tuesday|wednesday|thursday|friday|saturday|sunday)|"
                 r"a few (?:days|weeks|years|months) (?:ago|back)|next (?:week|month|year)|tomorrow|this (?:week|month|weekend))\b", re.I)


def rels(row):
    return row["relations"] if "relations" in row else row["events"]


def measures(rows, turns, window):
    n = len(rows)
    ev = [e for r in rows for e in rels(r)]
    slots = [(e, k, s) for e in ev for k, s in e["slots"].items()]
    linked = sum(1 for _, _, s in slots if s["link"])
    out = {"events": n, "relations": len(ev), "slot_values": len(slots)}
    out["M1_valid_without_retry"] = sum(1 for r in rows if r["attempts"] == 1) / n if n else None
    out["M2_relations_with_type"] = (sum(1 for e in ev if e["type"]) / len(ev)) if ev else None
    out["M3_link_rate_all_slots"] = linked / len(slots) if slots else None
    cnt = Counter(e["type"] for e in ev)
    seen, new_per_window = set(), []
    for w0 in range(0, n, window):
        types = {e["type"] for r in rows[w0:w0 + window] for e in rels(r)}
        new_per_window.append({"events": f"{w0}-{min(w0 + window, n) - 1}", "new_types": len(types - seen)})
        seen |= types
    top10 = sum(c for _, c in cnt.most_common(10))
    out["M4_new_types_per_window"] = new_per_window
    out["M4_top10_type_coverage"] = top10 / len(ev) if ev else None
    out["M4_types"] = [{"type": t, "relations": c, "roles": dict(Counter(k for r in rows for e in rels(r) if e["type"] == t for k in e["slots"]).most_common(8))}
                       for t, c in cnt.most_common(15)]
    cue_events = [i for i, t in enumerate(turns[:n]) if CUE.search(t["text"])]
    kept = 0
    for i in cue_events:
        phrase = CUE.search(turns[i]["text"]).group(0).lower()
        if any(phrase in s["value"].lower() for e in rels(rows[i]) for s in e["slots"].values()):
            kept += 1
    out["M5_time_cue_events"] = len(cue_events)
    out["M5_time_cue_kept"] = (kept / len(cue_events)) if cue_events else None
    out["M8_mean_attempts"] = st.mean(r["attempts"] for r in rows) if rows else None
    out["M8_mean_seconds_per_turn"] = st.mean(r["seconds"] for r in rows) if rows else None
    out["M8_mean_prompt_chars"] = st.mean(r["prompt_chars"] for r in rows) if rows else None
    out["M8_final_registry"] = rows[-1]["registry"] if rows else None
    unlinked = Counter(s["value"].lower() for _, _, s in slots if not s["link"])
    out["unlinked_most_common"] = unlinked.most_common(15)
    return out


def review(rows, turns):
    lines = ["# ND-E review: mark entity-like values that stayed TEXT (M3 hand check). The model saw only the sentence.", ""]
    for r, t in zip(rows, turns):
        lines.append(f"## {r['event_id']}")
        lines.append(f"> {t['text']}")
        lines.append(f"Entities: {r['Entities']}")
        for e in rels(r):
            parts = [f"{k}={s['value']!r} {'LINK' if s['link'] else 'TEXT'}" for k, s in e["slots"].items()]
            lines.append(f"- **{e['type']}**: " + "; ".join(parts))
        lines.append("")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--extraction", required=True)
    ap.add_argument("--source", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--window", type=int, default=50)
    a = ap.parse_args(argv)
    rows = [json.loads(l) for l in open(a.extraction) if l.strip()]
    turns = [json.loads(l) for l in open(a.source) if l.strip()][:len(rows)]
    os.makedirs(a.out, exist_ok=True)
    m = measures(rows, turns, a.window)
    json.dump(m, open(os.path.join(a.out, "nde_report.json"), "w"), indent=1)
    open(os.path.join(a.out, "review.md"), "w").write(review(rows, turns))
    for k, v in m.items():
        if k not in ("M4_types", "unlinked_most_common"):
            print(f"{k}: {v}")
    print("top types:", [(t["type"], t["relations"]) for t in m["M4_types"][:8]])
    print("most common unlinked values:", m["unlinked_most_common"][:8])


if __name__ == "__main__":
    main()
