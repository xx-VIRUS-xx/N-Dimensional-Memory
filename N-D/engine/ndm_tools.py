"""ND-Q tools: seven read-only, deterministic queries over the engine state (EXP-NDQ.md).

No LLM, no ranking, no source text: the only input is the engine state JSON.
Each tool returns {"text": <what the model reads, capped at 200 words>, "data": <structure for tests>}.

Dates are the day the turn was SAID (the second clock), not necessarily when the thing happened.
Hub pegs (speakers and listeners) are kept but never listed as partners.
Entity names are matched by the engine's own normalisation (ident): determiners dropped, plurals singularised.
"""
import datetime
import json
import re
import sys
from collections import Counter, defaultdict
from os.path import dirname

sys.path.insert(0, dirname(__file__))
from nd_engine import ident, norm  # noqa: E402

CAP_WORDS = 200
HIDDEN = re.compile(r"^(role|role_in_event|type|reference_status|epistemic_source)$")
MAX_NEAR = 8


def _words(s):
    return len(s.split())


def _cap(header, lines, cap=CAP_WORDS):
    """Join lines under the word cap; say how many were cut. A single over-long line is truncated."""
    out, used = [], _words(header)
    for i, ln in enumerate(lines):
        room = cap - used
        if _words(ln) > room:
            if not out and room > 0:                  # nothing shown yet: cut this line to fit
                out.append(" ".join(ln.split()[:room]) + " ...(truncated)")
                i += 1
            if len(lines) - i > 0:
                out.append(f"({len(lines) - i} more not shown)")
            break
        out.append(ln); used += _words(ln)
    return "\n".join(([header] if header else []) + out)


def _safe(fn):
    """Bad input becomes an error message the model can read, never an exception."""
    def wrapped(self, *a, **k):
        try:
            return fn(self, *a, **k)
        except ValueError as e:
            return {"text": f"Error: {e}", "data": None}
    wrapped.__name__, wrapped.__doc__ = fn.__name__, fn.__doc__
    return wrapped


_SUFFIXES = ("ing", "ed", "es", "s", "e")


def _stem(w):
    """Drop a plural, -ing, -ed or final -e ending, so dance/dances/danced/dancing meet. Nothing fuzzier than that."""
    for suf in _SUFFIXES:
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            return w[:-len(suf)]
    return w


def _stems(text):
    return {_stem(w) for w in re.findall(r"[a-z0-9]+", re.sub(r"['\u2019]s\b", "", str(text).lower()))}


def _day(anchor):
    m = re.search(r"(\d{1,2}) (\w+),? (\d{4})", anchor or "")
    return datetime.datetime.strptime(" ".join(m.groups()), "%d %B %Y").date() if m else None


def _parse_bound(s, end):
    """'2023-05-01' or '2023-05' -> date; for a bare month, the first or last day of it."""
    if not s:
        return None
    m = re.fullmatch(r"(\d{4})-(\d{2})(?:-(\d{2}))?", s.strip())
    if not m:
        raise ValueError(f"bad date '{s}': use YYYY-MM-DD or YYYY-MM")
    y, mo, d = int(m.group(1)), int(m.group(2)), m.group(3)
    if d:
        return datetime.date(y, mo, int(d))
    first = datetime.date(y, mo, 1)
    return (first.replace(year=y + (mo == 12), month=mo % 12 + 1) - datetime.timedelta(days=1)) if end else first


def _fmt_day(d):
    return f"{d.day} {d.strftime('%b %Y')}" if d else "undated"


class Memory:
    def __init__(self, state):
        self.s = state
        self.events = state["events"]
        self.day = {e["tick"]: _day(e.get("occurred_anchor")) for e in self.events}
        self.by_tick = defaultdict(list)
        for x in state["strings"]:
            self.by_tick[x["tick"]].append(x)
        self.peg_ticks = defaultdict(set)
        for x in state["strings"]:
            self.peg_ticks[x["peg"]].add(x["tick"])
        for e in self.events:
            for p in e["participants"]:
                self.peg_ticks[p].add(e["tick"])
        self.keys = {p: ident(p) for p in state["pegs"]}
        self.alias_keys = {p: {ident(a) for a in v.get("aliases", [])} for p, v in state["pegs"].items()}
        self.hubs = {norm(e.get("source_speaker") or "") for e in self.events} | {norm(e.get("source_listener") or "") for e in self.events}
        self.hubs.discard("")

    # ------------------------------------------------------------ helpers
    def resolve(self, name):
        """Exact pegs (by normalised name or alias) and near pegs (token subset either way); near are only proposed."""
        key = ident(name)
        toks = set(key.split())
        exact, near = [], []
        for p, pk in self.keys.items():
            if not pk:
                continue
            if pk == key or key in self.alias_keys[p]:
                exact.append(p)
            elif toks and (toks <= set(pk.split()) or set(pk.split()) <= toks):
                near.append(p)
        by_n = lambda p: (-len(self.peg_ticks[p]), p)
        return sorted(exact, key=by_n), sorted(near, key=by_n)

    def _line(self, tick, strings=None, show_all=False):
        e = self.events[tick]
        who = e.get("source_speaker") or "someone"
        parts = []
        for x in (strings if strings is not None else self.by_tick[tick]):
            if HIDDEN.match(x["dim"]) and not show_all:
                continue
            tag = ""
            if x["status"] != "claim" or norm(x["owner"] or "") != norm(who):
                tag = f" ({x['status'].replace('_', ' ')}; owner {x['owner']})"
            parts.append(f"{x['peg']}.{x['dim']} = {x['value']}{tag}")
        return f"t{tick} [{_fmt_day(self.day[tick])}] {who} said: " + ("; ".join(parts) if parts else "(nothing recorded)")

    def _in_window(self, tick, lo, hi):
        d = self.day[tick]
        return d is not None and (lo is None or d >= lo) and (hi is None or d <= hi)

    # ------------------------------------------------------------ 1. find_entity
    def find_entity(self, name):
        exact, near = self.resolve(name)
        rows = []
        for kind, group in (("exact", exact), ("near (proposed, not merged)", near)):
            for p in group:
                ts = sorted(self.peg_ticks[p])
                rows.append({"peg": p, "match": kind, "type": self.s["pegs"][p].get("type"), "events": len(ts),
                             "first": _fmt_day(self.day[ts[0]]), "last": _fmt_day(self.day[ts[-1]])})
        rows = rows[:MAX_NEAR]
        if not rows:
            return {"text": f"No entity matches '{name}'.", "data": []}
        lines = [f"{r['peg']} | {r['match']} | type {r['type']} | {r['events']} events | {r['first']} to {r['last']}" for r in rows]
        return {"text": _cap(f"Entities matching '{name}':", lines), "data": rows}

    # ------------------------------------------------------------ 2. trajectory
    @_safe
    def trajectory(self, entity, frm=None, to=None):
        exact, _ = self.resolve(entity)
        if not exact:
            return {"text": f"No entity '{entity}'. Use find_entity first.", "data": []}
        lo, hi = _parse_bound(frm, False), _parse_bound(to, True)
        ticks = sorted({t for p in exact for t in self.peg_ticks[p] if self._in_window(t, lo, hi)})
        shown, silent = [], 0                      # events where the peg only listened: nothing is recorded about it
        for t in ticks:
            own = [x for x in self.by_tick[t] if x["peg"] in exact and not HIDDEN.match(x["dim"])]
            if own:
                shown.append((t, own))
            else:
                silent += 1
        lines = [self._line(t, own) for t, own in shown]
        head = (f"{'/'.join(exact)}: {len(shown)} events with something recorded about it"
                + (f" ({silent} more where it was present but nothing was recorded about it)" if silent else "")
                + (f", between {frm or 'start'} and {to or 'end'}" if lo or hi else ""))
        return {"text": _cap(head, lines), "data": [t for t, _ in shown]}

    # ------------------------------------------------------------ 3. event
    def event(self, tick):
        if not isinstance(tick, int) or not 0 <= tick < len(self.events):
            return {"text": f"No event {tick}; ticks run 0 to {len(self.events) - 1}.", "data": None}
        e = self.events[tick]
        head = f"Event t{tick}: said by {e.get('source_speaker')} to {e.get('source_listener')}, {_fmt_day(self.day[tick])}."
        lines = [self._line(tick, show_all=True)]
        return {"text": _cap(head, lines), "data": {"tick": tick, "speaker": e.get("source_speaker"),
                                                    "listener": e.get("source_listener"), "day": str(self.day[tick])}}

    # ------------------------------------------------------------ 4. co_occurring
    def co_occurring(self, entity_a, entity_b=None):
        a, _ = self.resolve(entity_a)
        if not a:
            return {"text": f"No entity '{entity_a}'. Use find_entity first.", "data": []}
        ta = {t for p in a for t in self.peg_ticks[p]}
        if entity_b:
            b, _ = self.resolve(entity_b)
            if not b:
                return {"text": f"No entity '{entity_b}'. Use find_entity first.", "data": []}
            ticks = sorted(ta & {t for p in b for t in self.peg_ticks[p]})
            lines = [self._line(t) for t in ticks]
            return {"text": _cap(f"{'/'.join(a)} together with {'/'.join(b)}: {len(ticks)} events", lines), "data": ticks}
        cnt, first = Counter(), {}
        for t in ta:
            for p in self.events[t]["participants"]:
                if p in a or norm(p) in self.hubs:
                    continue
                cnt[p] += 1; first[p] = min(first.get(p, t), t)
        rows = sorted(cnt.items(), key=lambda kv: (-kv[1], first[kv[0]], kv[0]))
        lines = [f"{p}: {n} shared events, first t{first[p]}" for p, n in rows]
        return {"text": _cap(f"Partners of {'/'.join(a)} (speakers and listeners excluded): {len(rows)}", lines),
                "data": [(p, n) for p, n in rows]}

    # ------------------------------------------------------------ 5/6. filter_events, count
    def _match(self, dimension, status, owner, speaker, entity, frm, to):
        lo, hi = _parse_bound(frm, False), _parse_bound(to, True)
        pegs = None
        if entity:
            pegs, _ = self.resolve(entity)
            if not pegs:
                return None, f"No entity '{entity}'. Use find_entity first."
        dim = (dimension or "").strip().lower().replace(" ", "_")
        hit, hit_pegs = {}, set()
        for e in self.events:
            t = e["tick"]
            if not self._in_window(t, lo, hi) and (lo or hi):
                continue
            if speaker and norm(e.get("source_speaker") or "") != norm(speaker):
                continue
            sel = [x for x in self.by_tick[t]
                   if (not dim or x["dim"].lower() == dim) and (not status or x["status"] == status)
                   and (not owner or norm(x["owner"] or "") == norm(owner)) and (not pegs or x["peg"] in pegs)]
            string_level = dim or status or owner or pegs
            if string_level and not sel:
                continue
            hit[t] = sel
            hit_pegs |= {x["peg"] for x in sel}
        return (hit, hit_pegs), None

    @_safe
    def filter_events(self, dimension=None, status=None, owner=None, speaker=None, entity=None, frm=None, to=None):
        res, err = self._match(dimension, status, owner, speaker, entity, frm, to)
        if err:
            return {"text": err, "data": []}
        hit, _ = res
        ticks = sorted(hit)
        lines = [self._line(t, hit[t] or None, show_all=bool(dimension)) for t in ticks[:10]]
        more = f"({len(ticks) - 10} more events not listed; use count for the exact total)" if len(ticks) > 10 else None
        return {"text": _cap(f"{len(ticks)} matching events:", lines + ([more] if more else [])), "data": ticks}

    @_safe
    def count(self, entity=None, dimension=None, status=None, owner=None, frm=None, to=None):
        res, err = self._match(dimension, status, owner, None, entity, frm, to)
        if err:
            return {"text": err, "data": None}
        hit, pegs = res
        ticks = sorted(hit)
        listed = ", ".join(f"t{t}" for t in ticks[:40]) + (" ..." if len(ticks) > 40 else "")
        txt = f"events: {len(ticks)} ({listed}); distinct entities among the matches: {len(pegs)}"
        if pegs and len(pegs) <= 25:
            txt += " (" + ", ".join(sorted(pegs)) + ")"
        return {"text": _cap("", [txt]), "data": {"events": ticks, "pegs": sorted(pegs)}}

    # ------------------------------------------------------------ 8. find_value
    @_safe
    def find_value(self, word, speaker=None, entity=None, frm=None, to=None):
        """Events whose recorded values or entity names contain every word given (exact after _stem). Unranked, time order."""
        q = _stems(word)
        if not q:
            return {"text": "Error: give at least one word to look for.", "data": None}
        lo, hi = _parse_bound(frm, False), _parse_bound(to, True)
        pegs = None
        if entity:
            pegs, _ = self.resolve(entity)
            if not pegs:
                return {"text": f"No entity '{entity}'. Use find_entity first.", "data": None}
        hits = defaultdict(list)
        for x in self.s["strings"]:
            t = x["tick"]
            if (lo or hi) and not self._in_window(t, lo, hi):
                continue
            if speaker and norm(self.events[t].get("source_speaker") or "") != norm(speaker):
                continue
            if pegs and x["peg"] not in pegs:
                continue
            if q <= (_stems(x["value"]) | _stems(x["peg"])):
                hits[t].append(x)
        ticks = sorted(hits)
        if not ticks:
            return {"text": f"No recorded value or entity name contains '{word}' (matched after dropping plural, -ing and -ed endings).", "data": []}
        lines = [self._line(t, hits[t], show_all=True) for t in ticks[:10]]
        if len(ticks) > 10:
            lines.append(f"({len(ticks) - 10} more events not listed; narrow with entity, speaker, from or to)")
        return {"text": _cap(f"{len(ticks)} events whose recorded values or entity names contain '{word}':", lines), "data": ticks}

    # ------------------------------------------------------------ 7. ambiguities
    def ambiguities(self, entity=None):
        key = ident(entity) if entity else None
        rows = []
        for b in self.s["buckets"]:
            if b["state"] == "resolved":
                continue
            if key and key != ident(b["peg"]) and key not in {ident(str(c)) for c in b["candidates"]}:
                continue
            rows.append(b)
        resolved = sum(1 for b in self.s["buckets"] if b["state"] == "resolved")
        lines = [f"{b['id']} t{b['tick']}: {b['query']} candidates: {', '.join(str(c) for c in b['candidates']) or 'none'} [{b['state']}]" for b in rows[:25]]
        head = f"{len(rows)} unresolved reference buckets" + (f" for '{entity}'" if entity else "") + f" ({resolved} others were resolved by the engine's single-candidate rule and are not shown)"
        return {"text": _cap(head, lines), "data": [b["id"] for b in rows]}


def load(path):
    return Memory(json.load(open(path)))


if __name__ == "__main__":
    m = load(sys.argv[1])
    fn, args = sys.argv[2], sys.argv[3:]
    print(getattr(m, fn)(*[int(a) if a.isdigit() else a for a in args])["text"])
