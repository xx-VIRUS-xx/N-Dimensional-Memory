"""ND-1 M3: probe accuracy. The answering model sees ONLY the rendered engine
state, never the source text.

1) Build prompts:  python engine/probe_harness.py prompts <state.json> <probes.jsonl> <out_dir>
2) Answer them with any model (one answer per probe id, JSON: {"p01": "...", ...}).
3) Score:          python engine/probe_harness.py score <probes.jsonl> <answers.json>
"""
import json
import os
import sys


def render(state):
    lines = ["MEMORY (engine output). Statuses: fact, claim (owner said it), speaker_belief, "
             "open_question, intent. OPEN buckets are unresolved; do not pick a candidate yourself.", ""]
    for e in state["events"]:
        head = f"t{e['tick']}"
        if e["speaker"]:
            head += f" (speaker: {e['speaker']})"
        lines.append(head)
        for s in (x for x in state["strings"] if x["tick"] == e["tick"]):
            tag = s["status"] if s["status"] == "fact" else f"{s['status']}, owner {s['owner']}"
            if s["modality"] != "certain":
                tag += f", {s['modality']}"
            lines.append(f"  {s['peg']}.{s['dim']} = {s['value']}  [{tag}]")
        for b in (x for x in state["buckets"] if x["tick"] == e["tick"]):
            if b["state"] == "open":
                lines.append(f"  OPEN BUCKET {b['id']}: {b['query']} candidates {b['candidates']}")
            elif b["state"] == "resolved":
                lines.append(f"  RESOLVED {b['id']}: {b['query']} -> t{b['candidates'][0]} "
                             f"(by {b['resolved_by']}, evidence {b['evidence_ticks']})")
    return "\n".join(lines)


def build(state_path, probes_path, out_dir):
    state = json.load(open(state_path))
    ctx = render(state)
    os.makedirs(out_dir, exist_ok=True)
    open(os.path.join(out_dir, "context.txt"), "w").write(ctx)
    probes = [json.loads(l) for l in open(probes_path) if l.strip()]
    with open(os.path.join(out_dir, "prompts.jsonl"), "w") as f:
        for p in probes:
            prompt = (f"{ctx}\n\nAnswer from the memory above only. If memory does not settle it, "
                      f"say so. Answer in one short sentence.\nQuestion: {p['question']}")
            f.write(json.dumps({"id": p["id"], "prompt": prompt}) + "\n")
    print(f"wrote {len(probes)} prompts and context ({len(ctx.split())} words) to {out_dir}")


def score(probes_path, answers_path):
    probes = [json.loads(l) for l in open(probes_path) if l.strip()]
    ans = json.load(open(answers_path))
    ok = 0
    for p in probes:
        a = ans.get(p["id"], "").lower()
        also = p.get("accept_also", [])
        hit = any(x.lower() in a for x in p["accept"]) and (not also or any(y.lower() in a for y in also))
        ok += hit
        print(f"{p['id']} {'PASS' if hit else 'MISS'}  {p['question']}  ->  {ans.get(p['id'], '')}")
    print(f"M3: {ok}/{len(probes)} (misses need manual review before counting)")


if __name__ == "__main__":
    if sys.argv[1] == "prompts":
        build(*sys.argv[2:5])
    else:
        score(*sys.argv[2:4])
