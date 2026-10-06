"""ND-Q control arm RAGTOOL: one MCP tool, search_turns(query) = BM25 over the raw turns, top 5, dated.

Usage: python3 rag_mcp.py <source.jsonl>      Trace: NDQ_TRACE=<file.jsonl>
Same protocol and BM25 scoring as the ND-3 RAG baseline (depict.bm25_context), so the only difference
between RAG and RAGTOOL is that the model can query repeatedly.
"""
import json, math, os, sys, time
from collections import Counter
from os.path import dirname

sys.path.insert(0, dirname(os.path.abspath(__file__)))
from nd_engine import STOP, ident            # noqa: E402
from depict import QUESTION_WORDS            # noqa: E402

TOP = 5
TOOLS = [{"name": "search_turns",
          "description": "Keyword search over the conversation turns. Returns the 5 best-matching turns, each with its date and speaker, in time order.",
          "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"], "additionalProperties": False}}]


class Index:
    def __init__(self, turns, k1=1.5, b=0.75):
        self.turns, self.k1, self.b = turns, k1, b
        self.docs = [[t for t in ident(x["text"]).split() if t not in STOP] for x in turns]
        self.avg = sum(map(len, self.docs)) / len(self.docs)
        self.df = Counter(t for d in self.docs for t in set(d))

    def search(self, query):
        n = len(self.docs)
        q = [t for t in ident(query).split() if t not in STOP and t not in QUESTION_WORDS]
        def score(d):
            tf = Counter(d)
            return sum(math.log(1 + (n - self.df[t] + 0.5) / (self.df[t] + 0.5)) * tf[t] * (self.k1 + 1)
                       / (tf[t] + self.k1 * (1 - self.b + self.b * len(d) / self.avg)) for t in q if t in tf)
        ranked = sorted(range(n), key=lambda i: (-score(self.docs[i]), i))[:TOP]
        ranked = [i for i in ranked if score(self.docs[i]) > 0]
        if not ranked:
            return "No turns match."
        return "\n".join(f"[{self.turns[i].get('date', '')}] {self.turns[i].get('speaker', '')}: {self.turns[i]['text']}" for i in sorted(ranked))


def main():
    idx = Index([json.loads(l) for l in open(sys.argv[1]) if l.strip()])
    trace = os.environ.get("NDQ_TRACE")
    for line in sys.stdin:
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        mid, method, params = msg.get("id"), msg.get("method"), msg.get("params") or {}
        if mid is None:
            continue
        if method == "initialize":
            res = {"protocolVersion": params.get("protocolVersion", "2024-11-05"), "capabilities": {"tools": {}}, "serverInfo": {"name": "rag", "version": "0.1"}}
        elif method == "ping":
            res = {}
        elif method == "tools/list":
            res = {"tools": TOOLS}
        elif method == "tools/call":
            a = params.get("arguments") or {}
            if params.get("name") != "search_turns" or not isinstance(a.get("query"), str):
                text, err = "Error: search_turns needs a string 'query'.", True
            else:
                text, err = idx.search(a["query"]), False
            res = {"content": [{"type": "text", "text": text}], "isError": err}
            if trace:
                with open(trace, "a") as f:
                    f.write(json.dumps({"ts": time.time(), "tool": params.get("name"), "args": a, "error": err, "text": text}) + "\n")
        else:
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": "method not found"}}) + "\n"); sys.stdout.flush()
            continue
        sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": mid, "result": res}) + "\n"); sys.stdout.flush()


if __name__ == "__main__":
    main()
