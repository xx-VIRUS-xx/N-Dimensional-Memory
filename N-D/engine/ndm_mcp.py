"""ND-Q: the seven tools (ndm_tools.py) as a dependency-free MCP stdio server.

Usage:   python3 ndm_mcp.py <engine state.json>
Trace:   set NDQ_TRACE=<file.jsonl> to append every call and result (for audit).

Newline-delimited JSON-RPC 2.0 on stdin/stdout: initialize, ping, tools/list, tools/call.
Tool names, parameters and descriptions below are part of the pre-registered ND-Q spec (EXP-NDQ.md).
"""
import json
import os
import sys
import time
from os.path import dirname

sys.path.insert(0, dirname(os.path.abspath(__file__)))
from ndm_tools import load  # noqa: E402

DATES = "Dates are the day a turn was said, as YYYY-MM-DD or YYYY-MM."
S = {"type": "string"}


def _tool(name, desc, props, required=()):
    return {"name": name, "description": desc,
            "inputSchema": {"type": "object", "properties": props, "required": list(required), "additionalProperties": False}}


TOOLS = [
    _tool("find_entity", "Find entities (pegs) in memory by name. Names are matched after normalisation (determiners dropped, plurals singularised). "
          "Exact matches and proposed near matches are listed separately; near matches are never merged. Returns type, event count and first and last date.",
          {"name": S}, ["name"]),
    _tool("trajectory", "List one entity's events in time order: tick, date, who said it, and what was recorded about the entity (dimension = value, with status and owner when not a plain statement by the speaker). "
          "The header counts events where the entity was present but nothing was recorded about it. " + DATES,
          {"entity": S, "from": S, "to": S}, ["entity"]),
    _tool("event", "Show one event in full by its tick number: speaker, listener, date and every entity with its recorded dimensions.",
          {"tick": {"type": "integer"}}, ["tick"]),
    _tool("co_occurring", "With two entities: the events where both appear. With one entity: the other entities that appear in the same events, with counts (speakers and listeners excluded).",
          {"entity_a": S, "entity_b": S}, ["entity_a"]),
    _tool("filter_events", "List events (count plus the first 10) matching all given conditions: a dimension name, a status (claim, speaker_belief, open_question, intent), "
          "an owner (who the statement belongs to), the speaker of the turn, an entity, and a date range. " + DATES,
          {"dimension": S, "status": S, "owner": S, "speaker": S, "entity": S, "from": S, "to": S}),
    _tool("count", "Exact count of events matching all given conditions, with their tick numbers and the distinct entities among them. "
          "An event counts once however many strings match. An unknown entity name returns an error; use find_entity first. " + DATES,
          {"entity": S, "dimension": S, "status": S, "owner": S, "from": S, "to": S}),
    _tool("ambiguities", "List unresolved references (pronouns and definite phrases such as 'it', 'that', 'the old one') with their candidate referents. "
          "Nothing is resolved for you; candidates are options, not answers.",
          {"entity": S}),
]


def dispatch(mem, name, a):
    if name == "find_entity":
        return mem.find_entity(a["name"])
    if name == "trajectory":
        return mem.trajectory(a["entity"], a.get("from"), a.get("to"))
    if name == "event":
        return mem.event(int(a["tick"]))
    if name == "co_occurring":
        return mem.co_occurring(a["entity_a"], a.get("entity_b"))
    if name == "filter_events":
        return mem.filter_events(a.get("dimension"), a.get("status"), a.get("owner"), a.get("speaker"), a.get("entity"), a.get("from"), a.get("to"))
    if name == "count":
        return mem.count(a.get("entity"), a.get("dimension"), a.get("status"), a.get("owner"), a.get("from"), a.get("to"))
    if name == "ambiguities":
        return mem.ambiguities(a.get("entity"))
    raise KeyError(name)


def call(mem, name, args):
    spec = next((t for t in TOOLS if t["name"] == name), None)
    if spec is None:
        return f"Error: unknown tool '{name}'.", True
    props, req = spec["inputSchema"]["properties"], spec["inputSchema"]["required"]
    bad = [k for k in args if k not in props]
    miss = [k for k in req if k not in args]
    if bad or miss:
        return f"Error: {name} " + (f"does not take {bad}. " if bad else "") + (f"needs {miss}. " if miss else "") + f"Parameters: {list(props)}.", True
    try:
        res = dispatch(mem, name, args)
        text = res["text"]
        return text, res["data"] is None or text.startswith(("Error", "No entity", "No event"))
    except (ValueError, TypeError) as e:
        return f"Error: {e}", True


def main():
    mem = load(sys.argv[1])
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
        if mid is None:                                  # notification: no reply
            continue
        if method == "initialize":
            res = {"protocolVersion": params.get("protocolVersion", "2024-11-05"), "capabilities": {"tools": {}},
                   "serverInfo": {"name": "ndm", "version": "0.1"}}
        elif method == "ping":
            res = {}
        elif method == "tools/list":
            res = {"tools": TOOLS}
        elif method == "tools/call":
            name, args = params.get("name"), params.get("arguments") or {}
            text, is_err = call(mem, name, args)
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
