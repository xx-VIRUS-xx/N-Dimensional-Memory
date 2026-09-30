"""N-D engine v0: stages E1-E6 (EXP-ND1.md).

Input : LLM entity-dimension output, one JSON object per event (ND-0 format).
Output: engine state (JSON) with pegs, role strings, statuses, buckets, proposals.

Deterministic: no LLM calls. Every rule lives in a table below so it can be
reviewed and replaced; nothing is inferred outside these tables.

Known v0 limits (reported, not hidden):
- One event per input record. The engine cannot split compound sentences; that
  is the interpreter's job.
- Rule tables are lexical. They are the specified E4/E5/E6 rules for v0, not
  general language understanding, and ND-1 measures where they fail.
- Entity `type` (LLM contract v1) is used for pronoun candidates; pegs without a
  type (e.g. the older BabyTest output) are treated as compatible with any pronoun.
"""
import json
import re
import sys
from collections import defaultdict

# ---------------------------------------------------------------- rule tables
STOP = {"the", "a", "an", "of", "for", "to", "in", "on", "and", "or", "by", "with",
        "is", "was", "be", "as", "at", "its", "it", "that", "this", "under"}

# E4: absence. A value (or a parenthetical inside it) that only says something is
# missing is not a fact (C6). Stated absences with content ("no final adoption
# decision recorded") are kept.
ABSENCE_WHOLE = re.compile(
    r"^\s*(not stated|unspecified|unknown|not specified|not recorded|none stated)"
    r"(\b.*)?$", re.I)
ABSENCE_PAREN = re.compile(r"\(([^)]*(not stated|unspecified|unknown|not specified|not recorded)[^)]*)\)", re.I)
ABSENCE_TAIL = re.compile(r"[;,]\s*[^;,]*\b(is|are|was|were)? ?not (stated|specified)\b.*$", re.I)

# E4: inference. Dimensions or values that express the extractor's own
# conclusion become model-belief candidates, never facts (C7).
INFERENCE_DIM = re.compile(r"^(implied_|inferred_|stance_relative_to_)", re.I)
INFERENCE_VAL = re.compile(r"\b(suggests|implying|implies|indicates)\b", re.I)

# E5: epistemic cues, checked in order; first match wins for a role string.
SPEAKER_ROLE = re.compile(r"\b(reporter|speaker|said|reported|stated|requester)\b", re.I)
# E5: when nobody speaks, the owner of a non-fact string is the event's actor.
ACTOR_ROLE = re.compile(r"\b(questioner|proposer|requester|reviewer|holder|advocate)\b", re.I)
STATUS_RULES = [
    ("open_question", None, re.compile(r"\b(questioned|question|whether|uncertain|uncertainty|unresolved|pending|being decided|undecided|ambiguous|unclear)\b", re.I)),
    ("speaker_belief", "possible", re.compile(r"\b(might|may|possibly|possible|tentative|hypothetical|doubt)\b", re.I)),
    ("speaker_belief", "certain", re.compile(r"\b(favou?red|prefers?|preference|position)\b", re.I)),
    ("intent", None, re.compile(r"\b(planned|plans?|asked|requested|request|to be kept)\b", re.I)),
]

# E6: local ambiguity cues in a value.
AMBIGUITY = re.compile(r"\b(ambiguous|unclear|either)\b", re.I)
# E6: references the interpreter left unresolved. Stateless extractions mark them
# with reference_status = unresolved (LLM contract v1); the older BabyTest output
# used the phrase "definite reference".
DEFINITE_CUE = re.compile(r"definite reference", re.I)
PRONOUN_PERSON = {"he", "she", "him", "her", "his", "hers"}
PRONOUN_GROUP = {"they", "them", "their", "theirs"}      # persons or orgs (A7b)
PRONOUN_THING = {"it", "its", "this", "that"}
PRONOUNS = PRONOUN_PERSON | PRONOUN_GROUP | PRONOUN_THING
ALTERNATIVE_CUE = re.compile(r"\b(unclear|ambiguous|either|or)\b", re.I)
# E6 forward: an event that explicitly answers an open bucket.
RESOLUTION_CUE = re.compile(r"\b(meant|clarified|confirmed that|specifically)\b", re.I)
WINDOW = 3  # C9(c): last 3 events


# ---------------------------------------------------------------- helpers
def norm(name):
    s = name.lower().replace("-", " ").replace("_", " ")
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = re.sub(r"^(the|a|an) ", "", s.strip())
    return re.sub(r"\s+", " ", s).strip()


def content_tokens(text):
    return [t for t in norm(text).split() if t not in STOP]


def contains_peg(text, peg_norm):
    return re.search(rf"(?<![a-z0-9]){re.escape(peg_norm)}(?![a-z0-9])", norm(text)) is not None


# ---------------------------------------------------------------- engine
def _sanitise(tick, rec, issues):
    """Input validation (v0.2.1): malformed extractor output is recorded as a contract
    violation instead of crashing the engine. No extraction content is invented."""
    ents = []
    for ent in rec.get("entities") or []:
        if not isinstance(ent, dict) or not str(ent.get("name", "")).strip():
            issues.append({"tick": tick, "issue": "entity without a name", "raw": str(ent)[:120]})
            continue
        dims = ent.get("dimensions")
        if not isinstance(dims, dict):
            issues.append({"tick": tick, "entity": ent["name"], "issue": "entity without dimensions"})
            dims = {}
        ents.append({**ent, "dimensions": dims})
    return {**rec, "entities": ents}


def run(records):
    issues = []
    records = [_sanitise(t, r, issues) for t, r in enumerate(records)]
    state = {"input_issues": issues, "engine_version": "v0.2.1", "events": [], "pegs": {}, "strings": [], "proposals": [], "buckets": [], "first_mentions": [],
             "dropped_absences": [], "model_belief_candidates": [], "resolutions": []}
    peg_of = {}            # normalised name -> peg id (display name of first mention)

    for tick, rec in enumerate(records):                      # E1 ticks
        known_before = set(peg_of)                             # pegs that existed before this event
        ev = {"tick": tick, "input_id": rec["event_id"], "participants": [], "speaker": None}

        # E2 peg identity: exact normalised match merges; near matches are proposals.
        for ent in rec["entities"]:
            n = norm(ent["name"])
            if n not in peg_of:
                for other_n, other in peg_of.items():
                    a, b = set(n.split()), set(other_n.split())
                    if (a < b or b < a or len(a & b) / len(a | b) >= 0.5) and a & b - STOP:
                        state["proposals"].append({"tick": tick, "new": ent["name"], "existing": other,
                                                   "rule": "token overlap", "status": "needs confirmation"})
                peg_of[n] = ent["name"]
                state["pegs"][ent["name"]] = {"first_tick": tick, "type": ent.get("type")}
            ev["participants"].append(peg_of[n])

        # E5 speaker: an entity whose role/action marks it as the speaker.
        for ent in rec["entities"]:
            d = ent["dimensions"]
            cue = " ".join(str(d.get(k, "")) for k in ("role_in_event", "role", "action", "communicative_action"))
            if SPEAKER_ROLE.search(cue):
                ev["speaker"] = peg_of[norm(ent["name"])]
                break
        ev["actor"] = None
        for ent in rec["entities"]:
            d = ent["dimensions"]
            cue = " ".join(str(d.get(k, "")) for k in ("role_in_event", "role"))
            if ACTOR_ROLE.search(cue) and not ev["speaker"]:
                ev["actor"] = peg_of[norm(ent["name"])]
                break
        state["events"].append(ev)

        for ent in rec["entities"]:
            peg = peg_of[norm(ent["name"])]
            for dim, raw in ent["dimensions"].items():
                val = str(raw)

                # E4 cleaning: strip absence parentheticals/tails; drop pure absences.
                cleaned = ABSENCE_PAREN.sub("", val)
                cleaned = ABSENCE_TAIL.sub("", cleaned).strip(" ;,")
                if not cleaned or ABSENCE_WHOLE.match(cleaned):
                    state["dropped_absences"].append({"tick": tick, "peg": peg, "dim": dim, "value": val})
                    continue
                if INFERENCE_DIM.search(dim) or INFERENCE_VAL.search(cleaned):
                    state["model_belief_candidates"].append({"tick": tick, "peg": peg, "dim": dim, "value": cleaned,
                                                             "note": "extractor inference; not a fact (C7)"})
                    continue

                # E3 value linking: known pegs (seen up to now) named inside the value.
                links = sorted({p for n, p in peg_of.items() if p != peg and contains_peg(cleaned, n)})

                # E5 status per role string.
                status, modality = ("claim", "certain") if ev["speaker"] else ("fact", "certain")
                for st, mod, rx in STATUS_RULES:
                    if rx.search(f"{dim} {cleaned}"):
                        status, modality = st, (mod or "certain")
                        break
                owner = None if status == "fact" else (ev["speaker"] or ev["actor"] or peg)
                if status == "intent" and dim in ("plan", "planned_status") and not ev["speaker"]:
                    owner = peg

                s = {"tick": tick, "peg": peg, "dim": dim, "value": cleaned, "links": links,
                     "status": status, "modality": modality, "owner": owner}
                state["strings"].append(s)

                # E6 local ambiguity: the interpreter marked alternatives.
                if AMBIGUITY.search(cleaned):
                    # Candidates must be pegs, or short noun phrases (<= 4 words) split on "or".
                    cands = list(links) or [c.strip(" .;,()'") for c in re.split(r"\bor\b", cleaned.split(":", 1)[-1])
                                            if 0 < len(c.split()) <= 4]
                    # head-noun match for "the benchmark" style mentions
                    for n, p in peg_of.items():
                        head = n.split()[-1]
                        if p not in cands and re.search(rf"\bthe {re.escape(head)}\b", val.lower()):
                            cands.append(p)
                    if len(set(cands)) < 2:
                        # Not a referent ambiguity (no alternative pegs): it stays an open-question string.
                        continue
                    state["buckets"].append({"id": f"b{len(state['buckets'])}", "tick": tick, "peg": peg, "dim": dim,
                                             "query": f"{peg}.{dim}", "candidates": sorted(set(cands)),
                                             "model_belief": None, "state": "open", "origin": "local"})

        # E6 global, backward: references the interpreter left open.
        refs = []
        for ent in rec["entities"]:
            dims = " ".join(f"{k} {v}" for k, v in ent["dimensions"].items())
            unresolved = str(ent["dimensions"].get("reference_status", "")).lower() == "unresolved"
            n = norm(ent["name"])
            # A7f: every "the X" phrase that is not an already-known peg is checked,
            # whether or not the interpreter marked it (unmatched ones become first mentions).
            definite = ent["name"].strip().lower().startswith("the ") and n not in known_before
            if unresolved or definite or DEFINITE_CUE.search(dims):
                refs.append(ent)

        # A7d: two or more unresolved non-pronoun entities in one event, marked unclear,
        # are sentence-stated alternatives (one local bucket), not separate references.
        alts = [e for e in refs if norm(e["name"]).split(" ")[0] not in PRONOUNS
                and ALTERNATIVE_CUE.search(str(e["dimensions"].get("epistemic_stance", "")))]
        if len(alts) >= 2:
            state["buckets"].append({"id": f"b{len(state['buckets'])}", "tick": tick, "peg": alts[0]["name"],
                                     "dim": "alternatives", "query": "which of the stated alternatives?",
                                     "candidates": sorted(e["name"] for e in alts), "model_belief": None,
                                     "state": "open", "origin": "local-alternatives"})
            refs = [e for e in refs if e not in alts]
        # A7g: a phrase naming a peg that already existed is identity, not a reference.
        refs = [e for e in refs if not (norm(e["name"]) in known_before and norm(e["name"]).split(" ")[0] not in PRONOUNS)]

        for ent in refs:
            ref = ent["name"]
            ref_n = norm(ref)
            first = ref_n.split(" ")[0] if ref_n else ""
            window = [e for e in state["events"] if tick - WINDOW <= e["tick"] < tick]
            # A7e: never offer the entity the pronoun modifies ("its failover behavior",
            # or an entity whose value is the pronoun) as its own referent.
            modified = {norm(e["name"]) for e in rec["entities"]
                        if any(norm(str(v)) == ref_n for v in e["dimensions"].values())}
            if first in PRONOUNS:
                head = ref_n[len(first):].strip()
                if head:
                    modified.add(head)
            here_pegs = [p for p in ev["participants"] if norm(p) != ref_n and norm(p) not in modified]
            if first in PRONOUNS:
                # A7a: pronoun, bare or possessive ("its failover behavior").
                def compatible(t):
                    if t is None:
                        return True
                    if first in PRONOUN_PERSON:
                        return t == "person"
                    if first in PRONOUN_GROUP:
                        return t in ("person", "org")
                    return t != "person"
                pool = []
                for p in here_pegs + [p for e in window for p in e["participants"]]:
                    if (compatible(state["pegs"].get(p, {}).get("type")) and p not in pool
                            and norm(p).split(" ")[0] not in PRONOUNS and norm(p) not in modified):
                        pool.append(p)
                cands = pool
            else:
                # Definite noun phrase: earlier events whose pegs or values contain its content words.
                key = [t for t in content_tokens(ref) if t not in {"change", "changes", "thing", "one"}]
                cands = []
                for e in window:
                    texts = e["participants"] + [s["value"] for s in state["strings"] if s["tick"] == e["tick"]]
                    if key and any(all(k in norm(t).split() for k in key) for t in texts):
                        cands.append(e["tick"])
                if not cands:
                    # A7c: a definite phrase with no earlier match is a first mention, not an ambiguity.
                    state.setdefault("first_mentions", []).append({"tick": tick, "name": ref})
                    continue
            b = {"id": f"b{len(state['buckets'])}", "tick": tick, "peg": peg_of[norm(ref)], "dim": "reference",
                 "query": f"what does '{ref}' refer to?", "candidates": cands, "model_belief": None,
                 "origin": "global-backward"}
            if len(cands) == 1:
                b.update(state="resolved", resolved_by="engine", evidence_ticks=cands if isinstance(cands[0], int) else [])
                state["resolutions"].append({"bucket": b["id"], "by": "engine", "rule": "C9 clause (c): single candidate",
                                             "value": cands[0], "evidence_ticks": b["evidence_ticks"], "at_tick": tick})
            elif not cands:
                b.update(state="unknown_referent")
            else:
                b.update(state="open")
            state["buckets"].append(b)

        # E6 global, forward: does this event explicitly answer an open bucket?
        here = [s for s in state["strings"] if s["tick"] == tick]
        for b in state["buckets"]:
            if b["state"] != "open" or b["tick"] == tick:
                continue
            for s in here:
                hit = [c for c in b["candidates"] if isinstance(c, str) and contains_peg(s["value"], norm(c))]
                if len(hit) == 1 and RESOLUTION_CUE.search(s["value"]):
                    b.update(state="resolved", resolved_by="explicit statement", evidence_ticks=[tick])
                    state["resolutions"].append({"bucket": b["id"], "by": "explicit statement", "value": hit[0],
                                                 "evidence_ticks": [tick], "at_tick": tick})
    return state


if __name__ == "__main__":
    recs = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
    out = run(recs)
    json.dump(out, open(sys.argv[2], "w"), indent=2)
    print(f"events={len(out['events'])} pegs={len(out['pegs'])} strings={len(out['strings'])} "
          f"buckets={len(out['buckets'])} proposals={len(out['proposals'])} "
          f"dropped_absences={len(out['dropped_absences'])} model_belief_candidates={len(out['model_belief_candidates'])}")
