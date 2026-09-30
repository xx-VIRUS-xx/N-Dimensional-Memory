"""Stateless extraction for ND-1 run 2 (LLM contract v1).

Each sentence goes to a FRESH session: the sentence, its id, and the fixed
dimension dictionary. No earlier sentences, no earlier outputs.

Usage:
  python tools/extract_stateless.py --provider anthropic --model <model-id> --run 1
  python tools/extract_stateless.py --provider openai    --model <model-id> --run 1
  python tools/extract_stateless.py --provider ollama    --model <model-name> --run 1
  python tools/extract_stateless.py --provider claude-cli --model sonnet    --run 1   # uses Claude Code login
  python tools/extract_stateless.py --provider replay    --model babytest   --run 1   # offline smoke test

Keys: ANTHROPIC_API_KEY or OPENAI_API_KEY in the environment. Ollama: local server at
http://localhost:11434 (override with OLLAMA_URL). claude-cli: the installed `claude`
command in print mode (-p), logged in with your Claude Code account; each call runs in
a new empty temporary folder so no project files or project CLAUDE.md are visible.
User-level ~/.claude/CLAUDE.md is still loaded by Claude Code; move it aside for runs.
Output:
  ND-1/results/run2/extractions/<provider>__<model>__run<k>.jsonl
Standard library only.
"""
import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, "ND-0", "data", "pilot10.source.jsonl")
DICT = os.path.join(ROOT, "ND-1", "dimension_dictionary_v1.json")
OUT_DIR = os.path.join(ROOT, "ND-1", "results", "run2", "extractions")

PROMPT = """You extract entities and dimensions from ONE sentence. You have no other context.

Return JSON only, no prose, no code fences:
{{"event_id": "{sid}", "entities": [{{"name": "...", "type": "person|org|system|other", "dimensions": {{"dimension_name": "value"}}}}]}}

Rules:
1. Use only what the sentence states. Do not add entities, facts or relationships it does not state.
2. Name entities as the sentence names them.
3. Choose dimension names from the dictionary below; invent a new snake_case name only if none fits.
4. Keep values short and in the sentence's own words where possible.
5. Resolve a reference (he, she, it, its, they, the X) only if this sentence itself says what it refers to.
   Otherwise add an entity named exactly as written (for example "its" or "the rate-limiting change")
   with the dimension "reference_status": "unresolved". Never guess.
6. If the sentence states alternatives ("unclear whether A or B"), keep both; do not choose.
7. Record who said or reported something (epistemic_source) and any hedging (epistemic_stance).
8. Do not record what the sentence does not say (no "not stated", "unknown", "unspecified" values).

Dimension dictionary:
{dictionary}

{metadata}Sentence ({sid}): {text}
"""

METADATA = """Turn metadata (given, not part of the sentence):
- Speaker: {speaker}. "I", "me", "my" in the sentence refer to {speaker}; resolve them to {speaker}.
- Listener: {listener}. "you", "your" refer to {listener}; resolve them to {listener}.
- Date of this turn: {date}. Relative times ("last Sunday", "yesterday") may be recorded as written, with this date as context.
- Include {speaker} as an entity with role_in_event "speaker".

"""


def call(provider, model, prompt):
    if provider == "anthropic":
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=json.dumps({"model": model, "max_tokens": 2000, "temperature": 0,
                             "messages": [{"role": "user", "content": prompt}]}).encode(),
            headers={"x-api-key": os.environ["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01",
                     "content-type": "application/json"})
        body = json.load(urllib.request.urlopen(req, timeout=120))
        return "".join(b.get("text", "") for b in body["content"])
    if provider == "openai":
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps({"model": model, "temperature": 0,
                             "messages": [{"role": "user", "content": prompt}]}).encode(),
            headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}", "content-type": "application/json"})
        return json.load(urllib.request.urlopen(req, timeout=120))["choices"][0]["message"]["content"]
    if provider == "ollama":
        url = os.environ.get("OLLAMA_URL", "http://localhost:11434") + "/api/chat"
        req = urllib.request.Request(url, data=json.dumps({
            "model": model, "stream": False, "options": {"temperature": 0},
            "messages": [{"role": "user", "content": prompt}]}).encode(), headers={"content-type": "application/json"})
        return json.load(urllib.request.urlopen(req, timeout=300))["message"]["content"]
    if provider == "claude-cli":
        # Fresh session per call: empty temp dir as cwd, one turn, no tools needed.
        with tempfile.TemporaryDirectory(prefix="nd-stateless-") as empty:
            cmd = ["claude", "-p", "--output-format", "json", "--max-turns", "1"]
            if model != "default":
                cmd += ["--model", model]
            proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True, cwd=empty, timeout=300)
        if proc.returncode != 0:
            raise RuntimeError(f"claude exited {proc.returncode}: {proc.stderr.strip()[:300]}")
        try:
            return json.loads(proc.stdout)["result"]
        except (ValueError, KeyError):
            return proc.stdout
    raise ValueError(provider)


def parse(text):
    t = re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.M).strip()
    start, end = t.find("{"), t.rfind("}")
    return json.loads(t[start:end + 1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", required=True, choices=["anthropic", "openai", "ollama", "claude-cli", "replay"])
    ap.add_argument("--model", required=True)
    ap.add_argument("--run", type=int, default=1)
    ap.add_argument("--source", default=SOURCE, help="jsonl of sentences (default: the pilot)")
    ap.add_argument("--out-dir", default=OUT_DIR)
    a = ap.parse_args()
    sentences = [json.loads(l) for l in open(a.source) if l.strip()]
    dictionary = json.dumps(json.load(open(DICT))["dimensions"], indent=1)
    os.makedirs(a.out_dir, exist_ok=True)
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", a.model)
    out_path = os.path.join(a.out_dir, f"{a.provider}__{safe}__run{a.run}.jsonl")
    if a.provider == "claude-cli" and not shutil.which("claude"):
        sys.exit("claude-cli: the `claude` command was not found on PATH")
    meta = {"provider": a.provider, "model": a.model, "run": a.run, "source": os.path.relpath(a.source, ROOT),
            "started": datetime.datetime.now().isoformat(timespec="seconds"),
            "temperature": "0" if a.provider in ("anthropic", "openai", "ollama") else "not settable (CLI default)",
            "isolation": "fresh empty temp dir per call" if a.provider == "claude-cli" else "stateless API call"}
    if a.provider == "claude-cli":
        v = subprocess.run(["claude", "--version"], capture_output=True, text=True)
        meta["claude_version"] = v.stdout.strip()
        meta["user_claude_md_present"] = os.path.exists(os.path.expanduser("~/.claude/CLAUDE.md"))
        if meta["user_claude_md_present"]:
            print("WARNING: ~/.claude/CLAUDE.md exists and will be loaded into every call. "
                  "Move it aside for a clean run (see instructions).")
    replay = None
    if a.provider == "replay":
        replay = [json.loads(l) for l in open(os.path.join(ROOT, "ND-0", "data", "pilot10.babytest.jsonl"))]
    with open(out_path, "w") as out:
        for i, s in enumerate(sentences):
            sid = f"t{i}"
            if replay:
                rec = replay[i]
            else:
                md = METADATA.format(**s) if "speaker" in s else ""
                prompt = PROMPT.format(sid=sid, text=s["text"], dictionary=dictionary, metadata=md)
                for attempt in range(3):
                    try:
                        rec = parse(call(a.provider, a.model, prompt))
                        break
                    except Exception as e:  # network or JSON errors: retry, then fail loudly
                        if attempt == 2:
                            sys.exit(f"{sid}: failed after 3 attempts: {e}")
                        time.sleep(2 * (attempt + 1))
                rec["event_id"] = sid
            out.write(json.dumps(rec) + "\n")
            print(f"{sid}: {len(rec.get('entities', []))} entities")
    meta["finished"] = datetime.datetime.now().isoformat(timespec="seconds")
    json.dump(meta, open(out_path[:-6] + ".meta.json", "w"), indent=2)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
