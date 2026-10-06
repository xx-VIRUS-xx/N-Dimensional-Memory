"""ND-Q runner (EXP-NDQ.md): answer each question with an agent that can only call tools.

  python3 tools/ndq_run.py --arm tools    --state <state.json> --probes <probes.jsonl> --out <dir> [--model sonnet] [--ids q01,q02] [--limit N]
  python3 tools/ndq_run.py --arm ragtool  --source <source.jsonl> --probes <probes.jsonl> --out <dir>

Writes <out>/<arm>.answers.json (id -> answer, same shape as the ND-3 arms, ready for hand scoring),
<out>/<arm>.meta.json (calls, words returned, turns, cost, seconds per question) and <out>/<arm>.traces/<id>.jsonl
(every tool call and result). Rerunning continues where it stopped; any `claude` failure stops the run
(usage limit shows as "claude exited 1") and keeps everything already saved.

One isolated `claude -p` session per question: empty temp dir, built-in tools disabled, only this arm's MCP server.
"""
import argparse, json, os, subprocess, sys, tempfile, time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(os.path.dirname(HERE), "engine")
MAX_CALLS = 10
MAX_TURNS = 12                      # calls plus the final answer, with slack

TOOLS_PROMPT = """You answer a question about a conversation between {a} and {b} (dates {first} to {last}) using memory tools. The memory was extracted from the conversation. You cannot see the conversation itself; use the tools to look things up, then answer.

Rules:
- Answer from what the tools return only. If the tools do not settle it, say it is not in memory.
- Do not accept a premise the memory does not support. Say who actually said or did something, or that the memory does not show it.
- A date in memory is the day a turn was said, not necessarily when the thing happened ("last week" is relative to that day).
- Facts are recorded as values under entities. If what you need is a concept or detail rather than an entity name, look for its words with find_value.
- You may call tools several times, at most {calls} calls in total.
- Dimension names that exist in memory: {dims}. Statuses: claim, speaker_belief, open_question, intent.

Answer in one short sentence.
Question: {q}"""

RAGTOOL_PROMPT = """You answer a question about a conversation between {a} and {b} (dates {first} to {last}). You cannot see the conversation itself; use the search tool to find turns, then answer.

Rules:
- Answer from the turns the tool returns only. If they do not settle it, say so.
- Do not accept a premise the turns do not support. Say who actually said or did something, or that the turns do not show it.
- A date on a turn is the day it was said, not necessarily when the thing happened ("last week" is relative to that day).
- You may search several times, at most {calls} searches in total.

Answer in one short sentence.
Question: {q}"""

ARMS = {"tools": ("ndm", ["find_entity", "trajectory", "event", "co_occurring", "filter_events", "count", "find_value", "ambiguities"]),
        "ragtool": ("rag", ["search_turns"])}


def facts_from_state(state):
    ev = state["events"]
    dims = Counter(x["dim"] for x in state["strings"])
    days = [e["occurred_anchor"] for e in ev if e.get("occurred_anchor")]
    import re, datetime
    def d(a):
        m = re.search(r"(\d{1,2}) (\w+),? (\d{4})", a)
        return datetime.datetime.strptime(" ".join(m.groups()), "%d %B %Y").date()
    ds = sorted(d(a) for a in days)
    spk = sorted({e["source_speaker"] for e in ev if e.get("source_speaker")})
    return {"a": spk[0], "b": spk[1] if len(spk) > 1 else "the other person", "first": str(ds[0]), "last": str(ds[-1]),
            "dims": ", ".join(k for k, _ in dims.most_common())}


def facts_from_source(turns):
    import re, datetime
    spk = sorted({t["speaker"] for t in turns})
    ds = sorted(datetime.datetime.strptime(" ".join(re.search(r"(\d{1,2}) (\w+),? (\d{4})", t["date"]).groups()), "%d %B %Y").date() for t in turns)
    return {"a": spk[0], "b": spk[1], "first": str(ds[0]), "last": str(ds[-1])}


def call_claude(prompt, cfg_path, server, tool_names, model, cwd):
    cmd = ["claude", "-p", "--output-format", "json", "--max-turns", str(MAX_TURNS), "--model", model,
           "--mcp-config", cfg_path, "--strict-mcp-config", "--tools", "", "--no-session-persistence",
           "--allowedTools", *[f"mcp__{server}__{t}" for t in tool_names]]
    proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True, cwd=cwd, timeout=900)
    if proc.returncode != 0:
        raise RuntimeError(f"claude exited {proc.returncode}: {proc.stderr.strip()[:300]}")
    try:
        return json.loads(proc.stdout)
    except ValueError:
        return {"result": proc.stdout}


def run(args):
    probes = [json.loads(l) for l in open(args.probes) if l.strip()]
    if args.ids:
        want = set(args.ids.split(","))
        probes = [p for p in probes if p["id"] in want]
    if args.limit:
        probes = probes[:args.limit]
    server, tool_names = ARMS[args.arm]
    if args.arm == "tools":
        state = json.load(open(args.state))
        facts, template = facts_from_state(state), TOOLS_PROMPT
        cmd = [sys.executable, os.path.join(ENGINE, "ndm_mcp.py"), os.path.abspath(args.state)]
    else:
        turns = [json.loads(l) for l in open(args.source) if l.strip()]
        facts, template = facts_from_source(turns), RAGTOOL_PROMPT
        cmd = [sys.executable, os.path.join(ENGINE, "rag_mcp.py"), os.path.abspath(args.source)]
    os.makedirs(args.out, exist_ok=True)
    trace_dir = os.path.join(args.out, f"{args.arm}.traces")
    os.makedirs(trace_dir, exist_ok=True)
    ans_path, meta_path = (os.path.join(args.out, f"{args.arm}.{x}.json") for x in ("answers", "meta"))
    answers = json.load(open(ans_path)) if os.path.exists(ans_path) else {}
    meta = json.load(open(meta_path)) if os.path.exists(meta_path) else {}
    print(f"{args.arm}: {len(answers)}/{len(probes)} already answered", flush=True)
    for p in probes:
        if p["id"] in answers:
            continue
        trace = os.path.join(trace_dir, f"{p['id']}.jsonl")
        if os.path.exists(trace):
            os.remove(trace)                                   # a stopped question restarts clean
        cfg = {"mcpServers": {server: {"command": cmd[0], "args": cmd[1:], "env": {"NDQ_TRACE": os.path.abspath(trace)}}}}
        prompt = template.format(calls=MAX_CALLS, q=p["question"], **facts)
        with tempfile.TemporaryDirectory(prefix="ndq-") as tmp:
            cfg_path = os.path.join(tmp, "mcp.json")
            json.dump(cfg, open(cfg_path, "w"))
            t0 = time.time()
            out = call_claude(prompt, cfg_path, server, tool_names, args.model, tmp)
        rows = [json.loads(l) for l in open(trace)] if os.path.exists(trace) else []
        answers[p["id"]] = (out.get("result") or "").strip()
        meta[p["id"]] = {"calls": len(rows), "call_errors": sum(r["error"] for r in rows),
                         "words_returned": sum(len(r["text"].split()) for r in rows), "num_turns": out.get("num_turns"),
                         "cost_usd": out.get("total_cost_usd"), "seconds": round(time.time() - t0, 1),
                         "is_error": bool(out.get("is_error")), "over_call_limit": len(rows) > MAX_CALLS}
        json.dump(answers, open(ans_path, "w"), indent=2)
        json.dump(meta, open(meta_path, "w"), indent=2)
        m = meta[p["id"]]
        print(f"  {p['id']} done ({len(answers)}/{len(probes)}): {m['calls']} calls, {m['words_returned']} words, {m['seconds']}s", flush=True)
    done = [meta[p["id"]] for p in probes if p["id"] in meta]
    if done:
        w = sorted(m["words_returned"] for m in done); c = sorted(m["calls"] for m in done)
        print(f"{args.arm}: median {c[len(c) // 2]} calls, {w[len(w) // 2]} words read; call errors {sum(m['call_errors'] for m in done)}; "
              f"over limit {sum(m['over_call_limit'] for m in done)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=ARMS, required=True)
    ap.add_argument("--state"); ap.add_argument("--source"); ap.add_argument("--probes", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="sonnet"); ap.add_argument("--ids"); ap.add_argument("--limit", type=int)
    a = ap.parse_args()
    if (a.arm == "tools" and not a.state) or (a.arm == "ragtool" and not a.source):
        ap.error("tools needs --state; ragtool needs --source")
    try:
        run(a)
    except RuntimeError as e:
        print(f"STOPPED: {e}\nEverything answered so far is saved; rerun the same command to continue.", file=sys.stderr)
        sys.exit(1)
