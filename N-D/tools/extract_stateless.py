"""Stateless extraction for ND-1 run 2 (LLM contract v1).

Each sentence goes to a FRESH session: the sentence, its id, and the fixed
dimension dictionary. No earlier sentences, no earlier outputs.

Usage:
  python tools/extract_stateless.py --provider anthropic --model <model-id> --run 1
  python tools/extract_stateless.py --provider openai    --model <model-id> --run 1
  python tools/extract_stateless.py --provider ollama    --model <model-name> --run 1
  python tools/extract_stateless.py --provider claude-cli --model sonnet    --run 1   # uses Claude Code login
  python tools/extract_stateless.py --provider replay    --model babytest   --run 1   # offline smoke test
  add --resume to continue an interrupted run from the first missing sentence

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

Output requirements (your output is validated by a parser and rejected if any fails):
- The top level has "event_id" and a non-empty "entities" list.
- EVERY entity has all three keys: "name" (non-empty text), "type" (one of person, org, system, other),
  and "dimensions" (an object with AT LEAST ONE dimension). Never output an entity without dimensions;
  if you cannot give it a dimension, leave that entity out.
{speaker_rule}
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


VALID_TYPES = {"person", "org", "system", "other"}


def validate(rec, sid, speaker=None):
    """Return a list of problems; empty means the record meets the contract."""
    errs = []
    if not isinstance(rec, dict):
        return ["top level is not a JSON object"]
    ents = rec.get("entities")
    if not isinstance(ents, list) or not ents:
        return ["'entities' is missing or empty"]
    for i, e in enumerate(ents):
        if not isinstance(e, dict):
            errs.append(f"entity {i} is not an object")
            continue
        name = e.get("name")
        if not isinstance(name, str) or not name.strip():
            errs.append(f"entity {i} has no 'name'")
        if e.get("type") not in VALID_TYPES:
            errs.append(f"entity {i} ({name}) has type {e.get('type')!r}; use one of {sorted(VALID_TYPES)}")
        d = e.get("dimensions")
        if not isinstance(d, dict) or not d:
            errs.append(f"entity {i} ({name}) has no 'dimensions' (needs at least one)")
        elif any(not isinstance(k, str) or isinstance(v, (dict, list)) for k, v in d.items()):
            errs.append(f"entity {i} ({name}) has a nested or non-text dimension value; use flat text values")
    if speaker and not any(isinstance(e, dict) and str(e.get("name", "")).strip().lower() == speaker.lower() for e in ents):
        errs.append(f"the speaker {speaker} is missing as an entity")
    return errs


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
    ap.add_argument("--resume", action="store_true",
                    help="keep sentences already extracted in this run's file and continue from the first missing one")
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
    done = []
    if a.resume and os.path.exists(out_path):
        for line in open(out_path):
            if line.strip():
                try:
                    done.append(json.loads(line))
                except ValueError:
                    break  # a torn last line is dropped and redone
        done = [r for i, r in enumerate(done) if r.get("event_id") == f"t{i}"][:len(sentences)]
        meta["resumed_from_turn"] = len(done)
        print(f"resuming {os.path.basename(out_path)} at t{len(done)} ({len(done)} of {len(sentences)} already done)")
    retries = {}
    replay = None
    if a.provider == "replay":
        replay = [json.loads(l) for l in open(os.path.join(ROOT, "ND-0", "data", "pilot10.babytest.jsonl"))]
    with open(out_path, "w") as out:
        for r in done:
            out.write(json.dumps(r) + "\n")
        out.flush()
        for i, s in enumerate(sentences):
            if i < len(done):
                continue
            sid = f"t{i}"
            if replay:
                rec = replay[i]
            else:
                md = METADATA.format(**s) if "speaker" in s else ""
                md = METADATA.format(**s) if "speaker" in s else ""
                spk_rule = (f'- There must be an entity named exactly "{s["speaker"]}" (the speaker).\n'
                            if "speaker" in s else "")
                base = PROMPT.format(sid=sid, text=s["text"], dictionary=dictionary, metadata=md,
                                     speaker_rule=spk_rule)
                prompt, rec, errs = base, None, []
                for attempt in range(1, 5):          # 1 try + up to 3 retries with the parser's feedback
                    try:
                        cand = parse(call(a.provider, a.model, prompt))
                        errs = validate(cand, sid, s.get("speaker"))
                    except Exception as e:           # network, CLI or JSON errors
                        cand, errs = None, [f"call or JSON error: {e}"]
                        if "claude exited" in str(e) or "HTTP" in str(e):
                            time.sleep(2 * attempt)
                    if not errs:
                        rec = cand
                        break
                    retries[sid] = attempt
                    prompt = (base + "\n\nYOUR PREVIOUS OUTPUT WAS REJECTED BY THE PARSER:\n- "
                              + "\n- ".join(errs[:8]) + "\nReturn the corrected JSON only.")
                if rec is None:
                    sys.exit(f"{sid}: failed validation after 4 attempts: {errs[:3]}\n"
                             f"Progress is saved. Continue later with the same command plus --resume.")
                rec["event_id"] = sid
            out.write(json.dumps(rec) + "\n")
            out.flush()
            print(f"{sid}: {len(rec.get('entities', []))} entities")
    meta["finished"] = datetime.datetime.now().isoformat(timespec="seconds")
    meta["prompt_version"] = "v2 (validated: name, type, dimensions on every entity; speaker required)"
    meta["turns_needing_retries"] = retries
    json.dump(meta, open(out_path[:-6] + ".meta.json", "w"), indent=2)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
