"""ND-E extractor (EXP-NDE.md, amendment 4): one sentence (an event) in, entities plus typed relations out, with an accumulating type/role registry.

  python3 tools/extract_events.py --source <source.jsonl> --out-dir <dir> [--model haiku] [--limit 30] [--resume]
  python3 tools/extract_events.py --source S --out-dir D --provider replay --replay canned.jsonl      # offline test

Vocabulary: an EVENT is one sentence of the conversation. Its EventRelation list holds RELATIONS (type plus role slots).
The model sees the sentence text and the registry and nothing else: no speaker, listener, date or neighbouring sentences,
even though the source file may carry them. Each call is a fresh `claude -p` session (empty temp dir, no tools).
Sentences run in order because the registry accumulates. Code, not the model, decides which slot values are links to
entities (norm_entity match against `Entities`). The stored row has no speaker, listener or date.
Output: <out-dir>/<provider>__<model>__run<k>.jsonl (one record per event) and a .meta.json beside it. Standard library only.
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

PROMPT_VERSION = "v4.1"

PROMPT = """You extract entities and relations from ONE sentence of a conversation. The sentence is all you have: you are not told who speaks, who is addressed, or when, and you have no other context.

Return JSON only, no prose, no code fences:
{{"Entities": ["..."], "EventRelation": [{{"type": "...", "<role>": "<value>"}}]}}

What to record
- Entities: the people, things, places, tools, organisations and topics that your relations point at. Every role value that names one of these must also be in Entities, written the same way; this includes "I", "you", "we", "it" and any other pronoun you use as a value. List an entity only if it appears as a role value in one of your relations. Name things as the sentence names them. Do not list actions, feelings or plain adjectives as entities. A phrase, a time expression, a feeling or a question is never an entity.
- EventRelation: one object per thing that happens, is claimed, is asked, is intended, or is the case. Every object has "type" (a short snake_case name for the kind of relation) plus role keys of your choice. A role value either names an entity from your Entities list (exactly as written there) or is short text (a claim, a reason, a quantity).
- Use type "state" for how someone or something is: a subject and the state.
- A name used to address someone ("Hey Priya", "Thanks, Priya") is recorded as one relation of type "address" with the role "addressee", so a reader can tell who is addressed. Use type "greeting", "thanks" or "farewell" only when the sentence really greets, thanks or says goodbye.
- Record any time expression exactly as written ("last week", "yesterday", "in July") under a role of your choice.
- Record who claims, believes, asks or intends something through the roles of the relation (for example who argued, asked or plans), never by guessing.

Rules
1. Use only what the sentence states. Never invent entities, facts or relations. A role you cannot fill is left out. A relation you cannot describe is left out.
2. Reuse an existing type and its role names from the registry below whenever they fit. Create a new type or role name only when none fits.
3. You are not told who "I", "me", "my", "you" or "your" are. Use a name for them only when the sentence itself supplies it (for example "Hey Priya" addresses Priya; "I'm Marcus" names the speaker). Otherwise put the word in Entities as written ("I", "you") and use it as the value.
4. If a pronoun or phrase (it, that, this, there, they, he, she, we, us, the X) has no antecedent inside this sentence, put it in Entities as written (for example "it") and use it as the value. Never guess what it refers to; in particular "we", "us" and "they" do not automatically include the person addressed.
5. Keep values short, in the sentence's own words.
6. A sentence with no relation (a greeting) returns {{"Entities": [], "EventRelation": []}}.
7. One entity or one short phrase per role value. Never join two with "and" or a comma. For several people or things in the same role, write one relation each, or use a second role (for example participant and participant_2).

Format example only (unrelated to this conversation; its type and role names belong to the example, use them only if a sentence really is that). Sentence: "Bob recommended CockroachDB for multi-region payments, and Alice accepted the proposal."
{{"Entities": ["Bob", "CockroachDB", "multi-region payments", "Alice", "proposal"], "EventRelation": [{{"type": "database_recommendation", "recommender": "Bob", "recommended": "CockroachDB", "reason": "better", "domain": "multi-region payments"}}, {{"type": "proposal_acceptance", "acceptor": "Alice", "accepted_object": "proposal"}}]}}

Registry of types seen so far (type (uses): role names (uses); e.g. one example):
{registry}

Sentence {sid}: {text}
"""

TOP_TYPES = 40
MAX_ROLES = 8
RECENT_TURNS = 20
MAX_EXAMPLE_CHARS = 220


def snake(s):
    return re.sub(r"[^a-z0-9]+", "_", str(s).lower()).strip("_")


_DET = re.compile(r"^(the|a|an|my|your|his|her|their|our|its|this|that|these|those)\s+", re.I)
_POSS = re.compile(r"^[a-z0-9]+['’]s\s+", re.I)


def norm_entity(s):
    """Match key for links: case folded, leading determiner or possessive dropped, simple plural folded."""
    t = re.sub(r"\s+", " ", str(s).strip().lower())
    for _ in range(2):
        t = _DET.sub("", t)
        t = _POSS.sub("", t)
    if len(t) > 4 and re.search(r"(ses|xes|zes|ches|shes)$", t):
        t = t[:-2]                                   # buses -> bus, boxes -> box, priuses -> prius
    elif len(t) > 3 and t.endswith("s") and not re.search(r"(ss|us|is)$", t):
        t = t[:-1]                                   # snacks -> snack, cookies -> cookie; prius, glass, analysis stay
    return t


def validate(rec):
    """Problems found in one model output; an empty list means it meets the contract."""
    if not isinstance(rec, dict):
        return ["top level is not a JSON object"]
    errs = []
    ents, evs = rec.get("Entities"), rec.get("EventRelation")
    if not isinstance(ents, list):
        errs.append("'Entities' is missing or not a list")
    elif any(not isinstance(e, str) or not e.strip() for e in ents):
        errs.append("every item of 'Entities' must be a non-empty string")
    if not isinstance(evs, list):
        errs.append("'EventRelation' is missing or not a list")
        return errs
    for i, ev in enumerate(evs):
        if not isinstance(ev, dict):
            errs.append(f"relation {i} is not an object")
            continue
        if not isinstance(ev.get("type"), str) or not snake(ev.get("type")):
            errs.append(f"relation {i} has no 'type'")
        for k, v in ev.items():
            if not isinstance(k, str) or not snake(k):
                errs.append(f"relation {i} has an empty key")
            elif k != "type" and (not isinstance(v, str) or not v.strip()):
                errs.append(f"relation {i} role '{k}' must have a non-empty text value (omit the role if unknown)")
    return errs


def derive(rec):
    """Code decides links: a slot value whose norm_entity matches an entity in Entities is a link.
    Returns the relations of one event: [{"type": ..., "slots": {role: {"value": ..., "link": entity or None}}}]."""
    index = {}
    for e in rec["Entities"]:
        index.setdefault(norm_entity(e), e.strip())
    out = []
    for ev in rec["EventRelation"]:
        slots = {}
        for k, v in ev.items():
            if k == "type":
                continue
            slots[snake(k)] = {"value": v.strip(), "link": index.get(norm_entity(v))}
        out.append({"type": snake(ev["type"]), "slots": slots})
    return out


class Registry:
    def __init__(self):
        self.types = {}

    def update(self, relations, tick, entities):
        for ev in relations:
            t = self.types.setdefault(ev["type"], {"count": 0, "roles": {}, "example": None, "last": tick})
            t["count"] += 1
            t["last"] = tick
            for r in ev["slots"]:
                t["roles"][r] = t["roles"].get(r, 0) + 1
            if t["example"] is None:
                ex = json.dumps({"type": ev["type"], **{r: s["value"] for r, s in ev["slots"].items()}}, ensure_ascii=False)
                t["example"] = ex if len(ex) <= MAX_EXAMPLE_CHARS else None

    def render(self, tick):
        if not self.types:
            return "(empty: no types yet. Create the types you need.)"
        ranked = sorted(self.types.items(), key=lambda kv: (-kv[1]["count"], kv[0]))
        keep = {n for n, _ in ranked[:TOP_TYPES]} | {n for n, t in self.types.items() if tick - t["last"] <= RECENT_TURNS}
        lines = []
        for n, t in ranked:
            if n not in keep:
                continue
            roles = sorted(t["roles"].items(), key=lambda kv: (-kv[1], kv[0]))[:MAX_ROLES]
            line = f"- {n} ({t['count']}): " + ", ".join(f"{r} ({c})" for r, c in roles)
            if t["example"]:
                line += f"; e.g. {t['example']}"
            lines.append(line)
        return "\n".join(lines)

    def sizes(self):
        return {"types": len(self.types), "roles": sum(len(t["roles"]) for t in self.types.values())}


def parse(text):
    t = re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.M).strip()
    start, end = t.find("{"), t.rfind("}")
    return json.loads(t[start:end + 1])


def call_claude(prompt, model):
    with tempfile.TemporaryDirectory(prefix="nde-") as empty:
        cmd = ["claude", "-p", "--output-format", "json", "--max-turns", "1", "--tools", "", "--no-session-persistence"]
        if model != "default":
            cmd += ["--model", model]
        proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True, cwd=empty, timeout=300)
    if proc.returncode != 0:
        raise RuntimeError(f"claude exited {proc.returncode}: {proc.stderr.strip()[:300]}")
    try:
        return json.loads(proc.stdout)["result"]
    except (ValueError, KeyError):
        return proc.stdout


def rels(row):
    """The relations of a stored row (rows written before amendment 4 call them `events`)."""
    return row["relations"] if "relations" in row else row["events"]


def make_prompt(event, sid, registry, tick):
    """The model sees the sentence text and the registry. Nothing else from the source record is used."""
    return PROMPT.format(sid=sid, text=event["text"], registry=registry.render(tick))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--provider", default="claude-cli", choices=["claude-cli", "replay"])
    ap.add_argument("--model", default="haiku")
    ap.add_argument("--replay", help="jsonl of raw model outputs, one per attempt in order (replay provider only)")
    ap.add_argument("--run", type=int, default=1)
    ap.add_argument("--limit", type=int)
    ap.add_argument("--resume", action="store_true")
    a = ap.parse_args(argv)
    events = [json.loads(l) for l in open(a.source) if l.strip()]
    if a.limit:
        events = events[:a.limit]
    os.makedirs(a.out_dir, exist_ok=True)
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", a.model)
    out_path = os.path.join(a.out_dir, f"{a.provider}__{safe}__run{a.run}.jsonl")
    if a.provider == "claude-cli" and not shutil.which("claude"):
        sys.exit("claude-cli: the `claude` command was not found on PATH")
    replay = [json.loads(l)["raw"] for l in open(a.replay)] if a.provider == "replay" else None
    reg, done = Registry(), []
    if a.resume and os.path.exists(out_path):
        for line in open(out_path):
            if line.strip():
                try:
                    done.append(json.loads(line))
                except ValueError:
                    break
        done = [r for i, r in enumerate(done) if r.get("event_id") == f"t{i}"][:len(events)]
        for r in done:
            reg.update(rels(r), r["tick"], r["Entities"])
        print(f"resuming at t{len(done)} ({len(done)} of {len(events)} done)")
    meta = {"provider": a.provider, "model": a.model, "run": a.run, "prompt_version": PROMPT_VERSION,
            "prompt_sha256": hashlib.sha256(PROMPT.encode()).hexdigest(), "source": os.path.basename(a.source),
            "events": len(events), "model_input": "sentence text and registry only", "started": datetime.datetime.now().isoformat(timespec="seconds"),
            "isolation": "fresh empty temp dir per call, no tools" if a.provider == "claude-cli" else "replay"}
    if a.provider == "claude-cli":
        meta["claude_version"] = subprocess.run(["claude", "--version"], capture_output=True, text=True).stdout.strip()
        if os.path.exists(os.path.expanduser("~/.claude/CLAUDE.md")):
            print("WARNING: ~/.claude/CLAUDE.md exists and is loaded into every call; move it aside for a clean run.")
    cursor = 0
    with open(out_path, "w") as out:
        for r in done:
            out.write(json.dumps(r) + "\n")
        out.flush()
        for tick, event in enumerate(events):
            if tick < len(done):
                continue
            sid = f"t{tick}"
            base = make_prompt(event, sid, reg, tick)
            prompt, rec, errs, attempt = base, None, [], 0
            t0 = time.time()
            for attempt in range(1, 5):
                try:
                    if replay is not None:
                        raw = replay[cursor]
                        cursor += 1
                    else:
                        raw = call_claude(prompt, a.model)
                    cand = parse(raw) if isinstance(raw, str) else raw
                    errs = validate(cand)
                except Exception as e:
                    cand, errs = None, [f"call or JSON error: {e}"]
                    if "claude exited" in str(e):
                        time.sleep(2 * attempt)
                if not errs:
                    rec = cand
                    break
                prompt = base + "\n\nYOUR PREVIOUS OUTPUT WAS REJECTED BY THE PARSER:\n- " + "\n- ".join(errs[:8]) + "\nReturn the corrected JSON only."
            if rec is None:
                sys.exit(f"{sid}: failed validation after 4 attempts: {errs[:3]}\nProgress is saved; rerun the same command with --resume.")
            relations = derive(rec)
            reg.update(relations, tick, rec["Entities"])
            row = {"event_id": sid, "tick": tick,
                   "Entities": [e.strip() for e in rec["Entities"]], "EventRelation": rec["EventRelation"], "relations": relations,
                   "attempts": attempt, "seconds": round(time.time() - t0, 1), "prompt_chars": len(base), "registry": reg.sizes()}
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
            out.flush()
            print(f"{sid}: {len(rec['Entities'])} entities, {len(relations)} relations, registry {reg.sizes()['types']} types")
    meta["finished"] = datetime.datetime.now().isoformat(timespec="seconds")
    json.dump(meta, open(out_path[:-6] + ".meta.json", "w"), indent=2)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
