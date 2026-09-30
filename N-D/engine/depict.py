"""N-D depiction v1: what the engine hands the answering model for ONE question.

Deterministic; no LLM. Built only from the engine state (never from source text).

1. Seed    : pegs named in the question (identity keys, same normalisation as the engine).
2. Score   : each event by seed pegs it contains and question words in its content.
3. Select  : top events, plus the turn just before each (dialogue adjacency: a question
             and its answer are one fact split across two turns), plus collision
             neighbours sharing a non-hub peg with the top events.
4. Order   : chronologically, each event with the date its turn was said (second clock).
5. Link    : related entities (collision partners of the seeds), open buckets, and
             statuses other than plain fact/claim (belief, open question, intent).
6. Budget  : lowest-scored events are dropped until the depiction fits the word budget.
Descriptive labels (role_in_event, type, reference_status, epistemic_source) are not
shown; their information is carried by the speaker and status tags instead.
"""
import re
from collections import Counter

from nd_engine import STOP, ident, norm

QUESTION_WORDS = {"what", "when", "where", "who", "whom", "which", "why", "how", "does", "did", "do",
                  "is", "are", "was", "were", "has", "have", "had", "can", "could", "would", "will",
                  "about", "long", "much", "many", "kind", "type"}
HIDDEN_DIMS = re.compile(r"^(role|role_in_event|type|reference_status|epistemic_source)$")
TOP_EVENTS = 8
NEIGHBOURS = 4


def _tokens(text):
    return {t for t in ident(text).split() if t not in STOP and t not in QUESTION_WORDS and len(t) > 2}


def depict(state, question, budget_words=700):
    events = state["events"]
    hubs = {norm(e.get("source_speaker") or "") for e in events} | {norm(e.get("source_listener") or "") for e in events}
    hubs.discard("")
    q = _tokens(question)
    peg_keys = {p: ident(p) for p in state["pegs"]}
    seeds = {p for p, k in peg_keys.items() if k and set(k.split()) <= q}
    by_tick = {}
    for s in state["strings"]:
        by_tick.setdefault(s["tick"], []).append(s)

    def event_tokens(e):
        toks = set()
        for s in by_tick.get(e["tick"], []):
            toks |= _tokens(s["value"]) | _tokens(s["peg"])
        return toks

    scores = {}
    for e in events:
        parts = set(e["participants"])
        non_hub_seeds = {p for p in parts & seeds if norm(p) not in hubs}
        hub_seeds = {p for p in parts & seeds if norm(p) in hubs}
        overlap = len(q & event_tokens(e))
        score = 3 * len(non_hub_seeds) + overlap + 0.5 * len(hub_seeds)
        if non_hub_seeds or overlap:
            scores[e["tick"]] = score
    top = [t for t, _ in sorted(scores.items(), key=lambda x: (-x[1], x[0]))[:TOP_EVENTS]]

    chosen = dict((t, scores[t]) for t in top)
    for t in top:                                   # dialogue adjacency
        if t - 1 >= 0 and t - 1 not in chosen:
            chosen[t - 1] = scores.get(t - 1, 0) + 0.1
    top_pegs = Counter(p for t in top[:3] for p in events[t]["participants"] if norm(p) not in hubs)
    added = 0
    for e in events:                                # collision neighbours
        if added >= NEIGHBOURS:
            break
        if e["tick"] not in chosen and set(e["participants"]) & set(top_pegs):
            chosen[e["tick"]] = scores.get(e["tick"], 0) + 0.05
            added += 1

    related = Counter()
    for e in events:
        if set(e["participants"]) & seeds:
            for p in e["participants"]:
                if p not in seeds and norm(p) not in hubs:
                    related[p] += 1

    open_b = {}
    for b in state["buckets"]:
        if b["state"] == "open":
            open_b.setdefault(b["tick"], []).append(b)

    def render_event(t):
        e = events[t]
        who = e.get("source_speaker") or e.get("speaker") or ""
        when = e.get("occurred_anchor") or ""
        facts = []
        for s in by_tick.get(t, []):
            if HIDDEN_DIMS.match(s["dim"]):
                continue
            tag = ""
            if s["status"] in ("speaker_belief", "open_question", "intent"):
                tag = f" [{s['status'].replace('_', ' ')}{', ' + s['modality'] if s['modality'] != 'certain' else ''}]"
            facts.append(f"{s['peg']} {s['dim'].replace('_', ' ')}: {s['value']}{tag}")
        line = f"[{when}] t{t} {who}: " + "; ".join(facts)
        for b in open_b.get(t, []):
            line += f"\n    OPEN: {b['query']} candidates {b['candidates'][:6]}"
        return line

    order = sorted(chosen, key=lambda t: -chosen[t])      # drop lowest scores first when over budget
    keep = list(order)
    header = ("N-D MEMORY for this question. Selected events in time order. The date is when each turn was said; "
              "relative times ('yesterday', 'last week') are relative to that date. OPEN items are unresolved.")
    rel = ("Related to " + ", ".join(sorted(seeds)) + ": " + ", ".join(p for p, _ in related.most_common(8))) if seeds and related else ""

    def assemble(ticks):
        body = "\n".join(render_event(t) for t in sorted(ticks))
        return "\n".join(x for x in (header, rel, body) if x)

    text = assemble(keep)
    while len(text.split()) > budget_words and len(keep) > 1:
        keep.pop()                                      # lowest-scored event
        text = assemble(keep)
    return text
