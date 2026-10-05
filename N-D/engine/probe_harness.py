"""ND-1 M3: probe accuracy. The answering model sees ONLY the rendered engine
state, never the source text.

1) Build prompts:  python engine/probe_harness.py prompts <state.json> <probes.jsonl> <out_dir>
2) Answer them with any model (one answer per probe id, JSON: {"p01": "...", ...}).
3) Score:          python engine/probe_harness.py score <probes.jsonl> <answers.json>

N-D depiction instead of the flat dump (one depiction per question, built by engine/depict.py):
   python engine/probe_harness.py depict <state_dir> <probes.jsonl> --model sonnet

Or all at once through Claude Code (one fresh, isolated `claude -p` call per probe).
Progress prints per probe; answers are saved after each one, and rerunning the same
command continues where it stopped:
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
        if e.get("occurred_anchor"):
            head = f"[{e['occurred_anchor']}] " + head          # v0.3: the second clock, also in the flat view
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


def batch(state_dir, probes_path, model="sonnet", mode="flat", budget=700):
    if mode == "depict2":
        budget = 1000
    from extract_stateless import call  # isolated claude -p call
    state_dir = state_dir.rstrip("/")
    suffix = "" if mode == "flat" else f"_{mode}"
    out = os.path.join(os.path.dirname(state_dir), "probes_" + os.path.basename(state_dir) + suffix)
    if mode in ("depict", "depict2"):
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from depict import depict, depict_v2
    os.makedirs(out, exist_ok=True)
    probes = [json.loads(l) for l in open(probes_path) if l.strip()]
    summary = {"answering_model": f"claude-cli:{model}", "runs": {}}
    for f in sorted(glob.glob(os.path.join(state_dir, "*.state.json"))):
        name = os.path.basename(f)[:-11]
        state = json.load(open(f))
        flat_ctx = render(state)
        path = os.path.join(out, f"{name}.answers.json")
        answers = json.load(open(path)) if os.path.exists(path) else {}   # resume: keep saved answers
        sizes_path = os.path.join(out, f"{name}.context_words.json")
        sizes = json.load(open(sizes_path)) if os.path.exists(sizes_path) else {}
        print(f"{name} [{mode}]: {len(answers)}/{len(probes)} already answered", flush=True)
        for p in probes:
            if p["id"] in answers:
                continue
            ctx = (depict(state, p["question"], budget) if mode == "depict"
                   else depict_v2(state, p["question"], budget) if mode == "depict2" else flat_ctx)
            sizes[p["id"]] = len(ctx.split())
            prompt = (f"{ctx}\n\nAnswer from the memory above only. If memory does not settle it, "
                      f"say so. Answer in one short sentence.\nQuestion: {p['question']}")
            answers[p["id"]] = call("claude-cli", model, prompt).strip()
            json.dump(answers, open(path, "w"), indent=2)                  # saved after every answer
            json.dump(sizes, open(sizes_path, "w"), indent=2)
            print(f"  {p['id']} done ({len(answers)}/{len(probes)})", flush=True)
        ok, n, misses = score(probes_path, path, quiet=True)
        summary["runs"][name] = {"M3_triage": f"{ok}/{n}", "misses": misses,
                                 "mean_context_words": round(sum(sizes.values()) / max(len(sizes), 1))}
        print(f"{name:40s} M3 triage {ok}/{n}  mean context {summary['runs'][name]['mean_context_words']} words")
    json.dump(summary, open(os.path.join(out, "m3_summary.json"), "w"), indent=2)


def rag_baseline(source_path, probes_path, out_dir, model="sonnet", budget=1000):
    """Retrieval baseline at the depiction's word budget: BM25 over raw turns."""
    from extract_stateless import call
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from depict import bm25_context
    turns = [json.loads(l) for l in open(source_path) if l.strip()]
    os.makedirs(out_dir, exist_ok=True)
    probes = [json.loads(l) for l in open(probes_path) if l.strip()]
    path = os.path.join(out_dir, "rag.answers.json")
    sizes_path = os.path.join(out_dir, "rag.context_words.json")
    answers = json.load(open(path)) if os.path.exists(path) else {}
    sizes = json.load(open(sizes_path)) if os.path.exists(sizes_path) else {}
    print(f"RAG (BM25, {budget} words): {len(answers)}/{len(probes)} already answered", flush=True)
    for p in probes:
        if p["id"] in answers:
            continue
        ctx = bm25_context(turns, p["question"], budget)
        sizes[p["id"]] = len(ctx.split())
        prompt = (f"{ctx}\n\nAnswer from the turns above only. If they do not settle it, "
                  f"say so. Answer in one short sentence.\nQuestion: {p['question']}")
        answers[p["id"]] = call("claude-cli", model, prompt).strip()
        json.dump(answers, open(path, "w"), indent=2)
        json.dump(sizes, open(sizes_path, "w"), indent=2)
        print(f"  {p['id']} done ({len(answers)}/{len(probes)})", flush=True)
    ok, n, misses = score(probes_path, path, quiet=True)
    print(f"RAG baseline  M3 triage {ok}/{n}  mean context {round(sum(sizes.values()) / max(len(sizes), 1))} words")


def raw_baseline(source_path, probes_path, out_dir, model="sonnet"):
    """Baseline: the answering model reads the original turns instead of engine memory."""
    from extract_stateless import call
    turns = [json.loads(l) for l in open(source_path) if l.strip()]
    ctx = "CONVERSATION\n" + "\n".join(
        f"[{t.get('date', '')}] {t.get('speaker', '')}: {t['text']}" for t in turns)
    os.makedirs(out_dir, exist_ok=True)
    probes = [json.loads(l) for l in open(probes_path) if l.strip()]
    path = os.path.join(out_dir, "raw.answers.json")
    answers = json.load(open(path)) if os.path.exists(path) else {}
    print(f"RAW: context {len(ctx.split())} words; {len(answers)}/{len(probes)} already answered", flush=True)
    for p in probes:
        if p["id"] in answers:
            continue
        prompt = (f"{ctx}\n\nAnswer from the conversation above only. If it does not settle it, "
                  f"say so. Answer in one short sentence.\nQuestion: {p['question']}")
        answers[p["id"]] = call("claude-cli", model, prompt).strip()
        json.dump(answers, open(path, "w"), indent=2)
        print(f"  {p['id']} done ({len(answers)}/{len(probes)})", flush=True)
    ok, n, misses = score(probes_path, path, quiet=True)
    print(f"RAW baseline  M3 triage {ok}/{n}  context {len(ctx.split())} words")


if __name__ == "__main__":
    if sys.argv[1] == "prompts":
        build(*sys.argv[2:5])
    elif sys.argv[1] == "raw":
        model = sys.argv[sys.argv.index("--model") + 1] if "--model" in sys.argv else "sonnet"
        raw_baseline(sys.argv[2], sys.argv[3], sys.argv[4], model)
    elif sys.argv[1] in ("batch", "depict", "depict2"):
        model = sys.argv[sys.argv.index("--model") + 1] if "--model" in sys.argv else "sonnet"
        batch(sys.argv[2], sys.argv[3], model, mode={"batch": "flat"}.get(sys.argv[1], sys.argv[1]))
    elif sys.argv[1] == "rag":
        model = sys.argv[sys.argv.index("--model") + 1] if "--model" in sys.argv else "sonnet"
        rag_baseline(sys.argv[2], sys.argv[3], sys.argv[4], model)
    else:
        score(*sys.argv[2:4])
