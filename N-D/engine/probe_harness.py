"""ND-1 M3: probe accuracy. The answering model sees ONLY the rendered engine
state, never the source text.

1) Build prompts:  python engine/probe_harness.py prompts <state.json> <probes.jsonl> <out_dir>
2) Answer them with any model (one answer per probe id, JSON: {"p01": "...", ...}).
3) Score:          python engine/probe_harness.py score <probes.jsonl> <answers.json>

Or all at once through Claude Code (one fresh, isolated `claude -p` call per probe):
   python engine/probe_harness.py batch <state_dir> <probes.jsonl> --model sonnet
   Answers go to <state_dir>/../probes_<state_dir_name>/<run>.answers.json, plus m3_summary.json.
"""
import glob
import json
import re
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))


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


def score(probes_path, answers_path, quiet=False):
    probes = [json.loads(l) for l in open(probes_path) if l.strip()]
    ans = json.load(open(answers_path))
    ok, misses = 0, []
    for p in probes:
        a = ans.get(p["id"], "").lower()
        also = p.get("accept_also", [])
        # A9: whole-word matching (substring matching let "no" match "not"/"known").
        # Still triage only: it misses paraphrases ("not fully ... unresolved") and cannot
        # catch self-contradicting answers. M3 is the hand-reviewed score.
        def said(x):
            return re.search(rf"(?<![a-z]){re.escape(x.lower())}(?![a-z])", a) is not None
        hit = any(said(x) for x in p["accept"]) and (not also or any(said(y) for y in also))
        ok += hit
        if not hit:
            misses.append({"id": p["id"], "question": p["question"], "answer": ans.get(p["id"], "")})
        if not quiet:
            print(f"{p['id']} {'PASS' if hit else 'MISS'}  {p['question']}  ->  {ans.get(p['id'], '')}")
    if not quiet:
        print(f"M3: {ok}/{len(probes)} (misses need manual review before counting)")
    return ok, len(probes), misses


def batch(state_dir, probes_path, model="sonnet"):
    from extract_stateless import call  # isolated claude -p call
    state_dir = state_dir.rstrip("/")
    out = os.path.join(os.path.dirname(state_dir), "probes_" + os.path.basename(state_dir))
    os.makedirs(out, exist_ok=True)
    probes = [json.loads(l) for l in open(probes_path) if l.strip()]
    summary = {"answering_model": f"claude-cli:{model}", "runs": {}}
    for f in sorted(glob.glob(os.path.join(state_dir, "*.state.json"))):
        name = os.path.basename(f)[:-11]
        ctx = render(json.load(open(f)))
        answers = {}
        for p in probes:
            prompt = (f"{ctx}\n\nAnswer from the memory above only. If memory does not settle it, "
                      f"say so. Answer in one short sentence.\nQuestion: {p['question']}")
            answers[p["id"]] = call("claude-cli", model, prompt).strip()
        path = os.path.join(out, f"{name}.answers.json")
        json.dump(answers, open(path, "w"), indent=2)
        ok, n, misses = score(probes_path, path, quiet=True)
        summary["runs"][name] = {"M3": f"{ok}/{n}", "misses": misses}
        print(f"{name:40s} M3 {ok}/{n}  misses: {[m['id'] for m in misses]}")
    json.dump(summary, open(os.path.join(out, "m3_summary.json"), "w"), indent=2)


def raw_baseline(source_path, probes_path, out_dir, model="sonnet"):
    """Baseline: the answering model reads the original turns instead of engine memory."""
    from extract_stateless import call
    turns = [json.loads(l) for l in open(source_path) if l.strip()]
    ctx = "CONVERSATION\n" + "\n".join(
        f"[{t.get('date', '')}] {t.get('speaker', '')}: {t['text']}" for t in turns)
    os.makedirs(out_dir, exist_ok=True)
    probes = [json.loads(l) for l in open(probes_path) if l.strip()]
    answers = {}
    for p in probes:
        prompt = (f"{ctx}\n\nAnswer from the conversation above only. If it does not settle it, "
                  f"say so. Answer in one short sentence.\nQuestion: {p['question']}")
        answers[p["id"]] = call("claude-cli", model, prompt).strip()
    path = os.path.join(out_dir, "raw.answers.json")
    json.dump(answers, open(path, "w"), indent=2)
    ok, n, misses = score(probes_path, path, quiet=True)
    print(f"RAW baseline  M3 {ok}/{n}  misses: {[m['id'] for m in misses]}")


if __name__ == "__main__":
    if sys.argv[1] == "prompts":
        build(*sys.argv[2:5])
    elif sys.argv[1] == "raw":
        model = sys.argv[sys.argv.index("--model") + 1] if "--model" in sys.argv else "sonnet"
        raw_baseline(sys.argv[2], sys.argv[3], sys.argv[4], model)
    elif sys.argv[1] == "batch":
        model = sys.argv[sys.argv.index("--model") + 1] if "--model" in sys.argv else "sonnet"
        batch(sys.argv[2], sys.argv[3], model)
    else:
        score(*sys.argv[2:4])
