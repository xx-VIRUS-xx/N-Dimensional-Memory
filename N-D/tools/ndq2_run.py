"""ND-Q2 runner (EXP-NDQ2.md): answer each question with an agent that can only call tools.

  python3 tools/ndq2_run.py --arm struct|tools2|ragtool2 --extraction <run.jsonl> --source <source.jsonl> --probes <probes.jsonl> --out <dir> [--model sonnet] [--ids q01,q02] [--limit N]

Same isolation, limits, outputs and resume behaviour as tools/ndq_run.py (which it imports and does not change): one `claude -p` session per
question in an empty temp dir, built-in tools off, only this arm's MCP server (engine/ndq2_mcp.py), at most 10 tool calls.
Writes <out>/<arm>.answers.json, <arm>.meta.json and <arm>.traces/<id>.jsonl. A `claude` failure stops the run and keeps what is saved.
The prompts below are frozen after the dev-set pilot, with their hash, before the test set is drawn.
"""
import argparse, json, os, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(os.path.dirname(HERE), "engine")
sys.path.insert(0, HERE)
import ndq_run as V1  # noqa: E402

MAX_CALLS = V1.MAX_CALLS

STRUCT_PROMPT = """You answer a question about a conversation between {a} and {b} (turns dated {first} to {last}) using memory tools. The memory was built from the conversation: every turn is an event with its sentence and the relations found in it, written type(role=value). You cannot see the conversation itself; use the tools to look things up, then answer.

Rules:
- Answer from what the tools return only. If the tools do not settle it, say it is not in memory.
- Do not accept a premise the memory does not support. Say who actually said or did something, or that the memory does not show it. In an event line the arrow shows who spoke to whom, and a value like "I (Name)" means the speaker of that turn.
- The date on an event is the day the turn was said, not necessarily when the thing happened. Where a relation carries a time cue, "cue -> range" is the day or period it refers to, computed from the cue; "vague" means it could not be pinned down.
- catalog lists the relation types, their roles and the most linked entities; start there unless you already know what to look for. Related types can be searched together with types=[...]. Details are often in the sentence and not in a role, so use value= when an entity name finds nothing.
- You may call tools several times, at most {calls} calls in total.

Answer in one short sentence.
Question: {q}"""

TOOLS2_PROMPT = STRUCT_PROMPT.replace(
    "- You may call tools several times,",
    "- search_turns finds turns by keyword; the ids it returns work with event and neighbors.\n- You may call tools several times,")

RAGTOOL2_PROMPT = """You answer a question about a conversation between {a} and {b} (turns dated {first} to {last}). You cannot see the conversation itself; use the search tool to find turns, then answer.

Rules:
- Answer from the turns the tool returns only. If they do not settle it, say so.
- Do not accept a premise the turns do not support. Say who actually said or did something, or that the turns do not show it. Each turn shows its id, date and who spoke to whom.
- A date on a turn is the day it was said, not necessarily when the thing happened ("last week" is relative to that day).
- You may search several times, at most {calls} searches in total.

Answer in one short sentence.
Question: {q}"""

PROMPTS = {"struct": STRUCT_PROMPT, "tools2": TOOLS2_PROMPT, "ragtool2": RAGTOOL2_PROMPT}
ARMS = {"struct": ("ndq2", ["catalog", "find", "count", "values", "event", "neighbors"]),
        "tools2": ("ndq2", ["catalog", "find", "count", "values", "event", "neighbors", "search_turns"]),
        "ragtool2": ("ndq2", ["search_turns"])}


def run(args):
    probes = [json.loads(l) for l in open(args.probes) if l.strip()]
    if args.ids:
        want = set(args.ids.split(","))
        probes = [p for p in probes if p["id"] in want]
    if args.limit:
        probes = probes[:args.limit]
    server, tool_names = ARMS[args.arm]
    template = PROMPTS[args.arm]
    turns = [json.loads(l) for l in open(args.source) if l.strip()]
    facts = V1.facts_from_source(turns)
    cmd = [sys.executable, os.path.join(ENGINE, "ndq2_mcp.py"), os.path.abspath(args.extraction), os.path.abspath(args.source), args.arm]
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
            os.remove(trace)
        cfg = {"mcpServers": {server: {"command": cmd[0], "args": cmd[1:], "env": {"NDQ_TRACE": os.path.abspath(trace)}}}}
        prompt = template.format(calls=MAX_CALLS, q=p["question"], **facts)
        with tempfile.TemporaryDirectory(prefix="ndq2-") as tmp:
            cfg_path = os.path.join(tmp, "mcp.json")
            json.dump(cfg, open(cfg_path, "w"))
            t0 = time.time()
            out = V1.call_claude(prompt, cfg_path, server, tool_names, args.model, tmp)
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
    ap.add_argument("--extraction", required=True); ap.add_argument("--source", required=True)
    ap.add_argument("--probes", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="sonnet"); ap.add_argument("--ids"); ap.add_argument("--limit", type=int)
    a = ap.parse_args()
    try:
        run(a)
    except RuntimeError as e:
        print(f"STOPPED: {e}\nEverything answered so far is saved; rerun the same command to continue.", file=sys.stderr)
        sys.exit(1)
