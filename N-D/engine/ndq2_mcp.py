"""ND-Q2: the tools of ndq2_tools.py as a dependency-free MCP stdio server.

Usage:   python3 ndq2_mcp.py <extraction.jsonl> <source.jsonl> <arm>      arm = struct | tools2 | ragtool2
Trace:   set NDQ_TRACE=<file.jsonl> to append every call and result (for audit).

Arms (EXP-NDQ2.md): struct = catalog, find, count, values, event, neighbors; tools2 = struct plus search_turns;
ragtool2 = search_turns only. search_turns is the same BM25 search in tools2 and ragtool2.
Newline-delimited JSON-RPC 2.0: initialize, ping, tools/list, tools/call.
Tool names, parameters and behaviour are frozen by the spec; the description strings are frozen after the dev-set pilot.
"""
import json
import os
import sys
import time
from os.path import dirname

sys.path.insert(0, dirname(os.path.abspath(__file__)))
from ndq2_tools import load, TurnIndex  # noqa: E402

S = {"type": "string"}
DATES = "Dates are YYYY-MM-DD or YYYY-MM. The date shown on an event is the day the turn was said."


def _tool(name, desc, props, required=()):
    return {"name": name, "description": desc,
            "inputSchema": {"type": "object", "properties": props, "required": list(required), "additionalProperties": False}}


FILTERS = {"types": {"type": "array", "items": S}, "entity": S, "role": S, "value": S, "speaker": S, "from": S, "to": S}

TOOLS = {
    "catalog": _tool("catalog", "List every relation type in memory with its count, its main role names and one example, then the most linked entities "
                     "and the date range. Read it first to choose types and entities.", {}),
    "find": _tool("find", "List events (the exact count, then up to 10 in time order, as many as fit in about 250 words; the result says which offset continues) matching all given filters. Each event shows the dated sentence and its relations "
                  "as type(role=value). 'types' is a list: give several related types together. 'entity' matches any slot or entity of the event; "
                  "\"I\" counts as the speaker and \"you\" as the listener of that turn. 'role' keeps events that have that slot name. "
                  "'value' keeps events whose slot values or sentence contain every word given (plural, -ing and -ed endings ignored; no synonyms; not ranked). "
                  "'speaker' is who said the turn. 'from'/'to' filter on when the thing happened if the turn says (\"last week\" is resolved, shown as cue -> range), "
                  "otherwise on the day the turn was said. At least one filter is required. 'offset' pages. " + DATES,
                  {**FILTERS, "offset": {"type": "integer"}}),
    "count": _tool("count", "Exact number of events matching the same filters as find, plus the number of distinct entities in them and their ids. "
                   "'by' = type, speaker or month gives a breakdown. " + DATES, {**FILTERS, "by": S}),
    "values": _tool("values", "For the relations that link an entity, list the distinct values of a slot (every slot if 'role' is omitted), grouped by relation type, "
                    "with event ids. Use it to see what is recorded about an entity.", {"entity": S, "role": S}, ["entity"]),
    "event": _tool("event", "Show one event by id (for example t42): dated sentence and relations.", {"id": S}, ["id"]),
    "neighbors": _tool("neighbors", "Show the k events before and after an event (k 1 to 3, default 3): the event in full, the others as sentences.",
                       {"id": S, "k": {"type": "integer"}}, ["id"]),
    "search_turns": _tool("search_turns", "Keyword search over the conversation turns. Returns the 5 best-matching turns, each with its id, date and speaker, in time order.",
                          {"query": S}, ["query"]),
}
ARMS = {"struct": ["catalog", "find", "count", "values", "event", "neighbors"],
        "tools2": ["catalog", "find", "count", "values", "event", "neighbors", "search_turns"],
        "ragtool2": ["search_turns"]}


MAX_CALLS = 10


def call(mem, idx, arm, name, args):
    if name not in ARMS[arm]:
        return f"Error: unknown tool '{name}'.", True
    spec = TOOLS[name]
    props, req = spec["inputSchema"]["properties"], spec["inputSchema"]["required"]
    bad = [k for k in args if k not in props]
    miss = [k for k in req if k not in args]
    if bad or miss:
        return f"Error: {name} " + (f"does not take {bad}. " if bad else "") + (f"needs {miss}. " if miss else "") + f"Parameters: {list(props)}.", True
    try:
        if name == "catalog":
            text = mem.catalog()
        elif name == "find":
            text = mem.find(args.get("types"), args.get("entity"), args.get("role"), args.get("value"), args.get("speaker"),
                            args.get("from"), args.get("to"), args.get("offset", 0))
        elif name == "count":
            text = mem.count(args.get("types"), args.get("entity"), args.get("role"), args.get("value"), args.get("speaker"),
                             args.get("from"), args.get("to"), args.get("by"))
        elif name == "values":
            text = mem.values(args["entity"], args.get("role"))
        elif name == "event":
            text = mem.event(args["id"])
        elif name == "neighbors":
            text = mem.neighbors(args["id"], args.get("k", 3))
        else:
            text = idx.search(args["query"])
        return text, text.startswith(("No event", "Error"))
    except (ValueError, TypeError) as e:
        return f"Error: {e}", True


def main():
    ext, src, arm = sys.argv[1], sys.argv[2], sys.argv[3]
    mem = load(ext, src)
    idx = TurnIndex(mem)
    tools = [TOOLS[n] for n in ARMS[arm]]
    used = 0
    trace = os.environ.get("NDQ_TRACE")
    out = sys.stdout
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        mid, method, params = msg.get("id"), msg.get("method"), msg.get("params") or {}
        if mid is None:
            continue
        if method == "initialize":
            res = {"protocolVersion": params.get("protocolVersion", "2024-11-05"), "capabilities": {"tools": {}},
                   "serverInfo": {"name": "ndq2", "version": "0.1"}}
        elif method == "ping":
            res = {}
        elif method == "tools/list":
            res = {"tools": tools}
        elif method == "tools/call":
            name, args = params.get("name"), params.get("arguments") or {}
            used += 1
            if used > MAX_CALLS:
                text, is_err = f"Error: the limit of {MAX_CALLS} tool calls is used up. Answer now from what you have, or say it is not in memory.", True
            else:
                text, is_err = call(mem, idx, arm, name, args)
            res = {"content": [{"type": "text", "text": text}], "isError": is_err}
            if trace:
                with open(trace, "a") as f:
                    f.write(json.dumps({"ts": time.time(), "tool": name, "args": args, "error": is_err, "text": text}) + "\n")
        else:
            out.write(json.dumps({"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"method not found: {method}"}}) + "\n")
            out.flush()
            continue
        out.write(json.dumps({"jsonrpc": "2.0", "id": mid, "result": res}) + "\n")
        out.flush()


if __name__ == "__main__":
    main()
