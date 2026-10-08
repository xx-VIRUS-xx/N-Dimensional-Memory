"""ND-Q2 tools (EXP-NDQ2.md): read-only, deterministic queries over an ND-E extraction. No LLM.

Memory(extraction rows, source rows). The rows are never changed. Speaker, listener and date come from the source row with the
same event id, joined here: "I" is the speaker and "you" the listener of that event. Relative time cues in slot values are
resolved in code against the date of the turn (closed list in `resolve_cue`).

Every tool returns text of at most CAP words (CATALOG_CAP for the catalog) with an exact count of what was cut.
Bad input returns an error message, never an exception.
"""
import datetime as dt
import json
import math
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "tools"))
from extract_events import norm_entity  # noqa: E402
from nd_engine import STOP, ident        # noqa: E402
from depict import QUESTION_WORDS        # noqa: E402

CAP = 250
CATALOG_CAP = 700
PAGE = 10
FIND_RESERVE = 25                  # words kept free in a find result for the header and the continuation note
TOP_BM25 = 5
MAX_K = 3
MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
NUMBER_WORDS = {"a": 1, "an": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
                "eleven": 11, "twelve": 12}
VAGUE = re.compile(r"^(recently|lately|soon|a while (ago|back)|(a few|a couple of|a couple|several|some|many) (days|weeks|months|years|hours) (ago|back)|"
                   r"(a few|several) (days|weeks|months|years)|back then|ages|these days|nowadays|for a while|earlier|later|before|now|just|always|sometimes|"
                   r"right away|a long time ago|long ago|not long ago)$")


# ---------------------------------------------------------------- small helpers

def _words(s):
    return len(s.split())


def _cap(header, lines, cap=CAP, hint=""):
    """Join lines under the word cap, the "n more not shown" notice included, and say how many were cut. A single over-long first line is truncated."""
    used = _words(header)
    if used + sum(_words(ln) for ln in lines) <= cap:
        return "\n".join(([header] if header else []) + list(lines))
    room, out = cap - used - 8, []                                 # 8 words reserved for the notice
    for i, ln in enumerate(lines):
        if _words(ln) > room:
            if not out and room > 0:
                out.append(" ".join(ln.split()[:room]) + " ...(truncated)")
                i += 1
            out.append(f"({len(lines) - i} more not shown{hint})")
            break
        out.append(ln)
        room -= _words(ln)
    return "\n".join(([header] if header else []) + out)


def _stem(w):
    for suf in ("ing", "ed", "es", "s", "e"):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            return w[:-len(suf)]
    return w


def _stems(text):
    return {_stem(w) for w in re.findall(r"[a-z0-9]+", re.sub(r"['’]s\b", "", str(text).lower()))}


def parse_date(s):
    """'1:47 pm on 18 May, 2023' -> date."""
    m = re.search(r"(\d{1,2}) (\w+),? (\d{4})", s or "")
    if not m:
        raise ValueError(f"cannot read a date from {s!r}")
    return dt.datetime.strptime(" ".join(m.groups()), "%d %B %Y").date()


def _bound(s, end):
    """YYYY-MM-DD or YYYY-MM -> date (the first or last day of a month when only the month is given)."""
    m = re.fullmatch(r"(\d{4})-(\d{2})(?:-(\d{2}))?", str(s).strip())
    if not m:
        raise ValueError(f"date must be YYYY-MM-DD or YYYY-MM, got {s!r}")
    y, mo, d = int(m.group(1)), int(m.group(2)), m.group(3)
    try:
        if d:
            return dt.date(y, mo, int(d))
        return _month_end(y, mo) if end else dt.date(y, mo, 1)
    except ValueError:
        raise ValueError(f"not a calendar date: {s!r}")


def _month_end(y, m):
    return (dt.date(y + (m == 12), m % 12 + 1, 1) - dt.timedelta(days=1))


def _add_months(d, n):
    m0 = d.year * 12 + d.month - 1 + n
    return m0 // 12, m0 % 12 + 1


def _iso_week_start(d):
    return d - dt.timedelta(days=d.weekday())


# ---------------------------------------------------------------- time cues (closed list, EXP-NDQ2.md)

def resolve_cue(text, d):
    """Resolve a relative time cue against the date `d` of the turn.

    Returns (start, end) for a cue in the closed list, "vague" for a vague cue, None for anything else.
    Closed list: yesterday, today, tonight, tomorrow; last/next week, weekend, month, year; last <weekday>;
    N days/weeks/months/years ago; in <month>; <month> <year>; in <year>.
    Weeks run Monday to Sunday. "last weekend" is Saturday and Sunday of the week before the week of d;
    "next weekend" the same of the week after. "N days ago" and "N weeks ago" are one day; "N months ago" and "N years ago" the calendar month
    or year containing that date. "in <month>" is that month of d's year, or of the year before if that month starts after d."""
    t = re.sub(r"\s+", " ", str(text).strip().lower().rstrip(".!,"))
    if t.startswith("in ") and re.fullmatch(r"in (" + "|".join(MONTHS) + r"|\d{4}|(" + "|".join(MONTHS) + r") \d{4})", t):
        t = t[3:]
    if t == "yesterday":
        return d - dt.timedelta(days=1), d - dt.timedelta(days=1)
    if t in ("today", "tonight", "this morning", "this evening", "this afternoon"):
        return d, d
    if t == "tomorrow":
        return d + dt.timedelta(days=1), d + dt.timedelta(days=1)
    ws = _iso_week_start(d)
    if t in ("last week", "this past week", "the week before"):
        return ws - dt.timedelta(days=7), ws - dt.timedelta(days=1)
    if t == "next week":
        return ws + dt.timedelta(days=7), ws + dt.timedelta(days=13)
    if t == "last weekend":
        return ws - dt.timedelta(days=2), ws - dt.timedelta(days=1)
    if t == "next weekend":
        return ws + dt.timedelta(days=12), ws + dt.timedelta(days=13)
    if t == "last month":
        y, m = _add_months(d, -1)
        return dt.date(y, m, 1), _month_end(y, m)
    if t == "next month":
        y, m = _add_months(d, 1)
        return dt.date(y, m, 1), _month_end(y, m)
    if t == "last year":
        return dt.date(d.year - 1, 1, 1), dt.date(d.year - 1, 12, 31)
    if t == "next year":
        return dt.date(d.year + 1, 1, 1), dt.date(d.year + 1, 12, 31)
    m = re.fullmatch(r"last (" + "|".join(WEEKDAYS) + ")", t)
    if m:
        back = (d.weekday() - WEEKDAYS.index(m.group(1))) % 7 or 7
        x = d - dt.timedelta(days=back)
        return x, x
    m = re.fullmatch(r"(\d+|" + "|".join(NUMBER_WORDS) + r") (day|week|month|year)s? ago", t)
    if m and not VAGUE.match(t):
        n = int(m.group(1)) if m.group(1).isdigit() else NUMBER_WORDS[m.group(1)]
        unit = m.group(2)
        if unit == "day":
            x = d - dt.timedelta(days=n)
            return x, x
        if unit == "week":
            x = d - dt.timedelta(days=7 * n)
            return x, x
        if unit == "month":
            y, mo = _add_months(d, -n)
            return dt.date(y, mo, 1), _month_end(y, mo)
        return dt.date(d.year - n, 1, 1), dt.date(d.year - n, 12, 31)
    m = re.fullmatch(r"(" + "|".join(MONTHS) + r")(?: (\d{4}))?", t)
    if m:
        mo = MONTHS.index(m.group(1)) + 1
        y = int(m.group(2)) if m.group(2) else d.year
        if not m.group(2) and dt.date(y, mo, 1) > d:
            y -= 1
        return dt.date(y, mo, 1), _month_end(y, mo)
    if re.fullmatch(r"\d{4}", t):
        return dt.date(int(t), 1, 1), dt.date(int(t), 12, 31)
    if VAGUE.match(t):
        return "vague"
    return None


def _fmt_range(a, b):
    return a.isoformat() if a == b else f"{a.isoformat()}..{b.isoformat()}"


# ---------------------------------------------------------------- the memory

class Memory:
    def __init__(self, rows, source):
        src = {s["sentence_id"]: s for s in source}
        self.events, self.by_id = [], {}
        for r in rows:
            s = src[r["event_id"]]
            d = parse_date(s.get("date"))
            ev = {"id": r["event_id"], "tick": len(self.events), "date": d, "speaker": s.get("speaker") or "", "listener": s.get("listener") or "",
                  "text": s["text"].strip(), "entities": list(r.get("Entities", [])), "relations": []}
            for rel in (r["relations"] if "relations" in r else r["events"]):
                slots = {k: (v["value"], v["link"]) for k, v in rel["slots"].items()}
                ev["relations"].append({"type": rel["type"], "slots": slots})
            ev["cues"] = self._cues(ev)
            ev["when"] = next(((a, b) for (_, _, rg) in ev["cues"] if rg != "vague" for (a, b) in [rg]), (d, d))
            ev["_ent"] = self._entity_keys(ev)
            ev["_stems"] = set()
            for rel in ev["relations"]:
                for v, _ in rel["slots"].values():
                    ev["_stems"] |= _stems(v)
            ev["_stems"] |= _stems(ev["text"])
            self.by_id[ev["id"]] = ev
            self.events.append(ev)
        self.first, self.last = min(e["date"] for e in self.events), max(e["date"] for e in self.events)
        self.names = sorted({e["speaker"] for e in self.events if e["speaker"]})

    # ---- joins
    @staticmethod
    def join(value, ev):
        """'I' is the speaker, 'you' the listener of that event; everything else is as stored."""
        v = str(value).strip().lower()
        if v == "i" and ev["speaker"]:
            return ev["speaker"]
        if v == "you" and ev["listener"]:
            return ev["listener"]
        return value

    def _entity_keys(self, ev):
        keys = set()
        for rel in ev["relations"]:
            for _, link in rel["slots"].values():
                if link:
                    keys.add(norm_entity(self.join(link, ev)))
        for e in ev["entities"]:
            keys.add(norm_entity(self.join(e, ev)))
        return keys

    def _cues(self, ev):
        out = []
        for ri, rel in enumerate(ev["relations"]):
            for role, (v, _) in rel["slots"].items():
                rg = resolve_cue(v, ev["date"])
                if rg is not None:
                    out.append(((ri, role), v, rg))
        return out

    # ---- display
    def _slot_text(self, ev, value):
        v = self.join(value, ev)
        return f"{value} ({v})" if v != value else str(value)

    def _cue_text(self, ev, ri, role, value):
        for (k, v, rg) in ev["cues"]:
            if k == (ri, role):
                return f"{value} -> " + ("vague, said " + ev["date"].isoformat() if rg == "vague" else _fmt_range(*rg))
        return None

    def line(self, ev, with_relations=True):
        head = f"[{ev['id']} | {ev['date'].isoformat()} | {ev['speaker'] or '?'} -> {ev['listener'] or '?'}] \"{ev['text']}\""
        if not with_relations:
            return head
        parts = []
        for ri, rel in enumerate(ev["relations"]):
            slots = []
            for role, (v, _) in rel["slots"].items():
                slots.append(f"{role}={self._cue_text(ev, ri, role, v) or self._slot_text(ev, v)}")
            parts.append(f"{rel['type']}({'; '.join(slots)})")
        return head + (" | " + " | ".join(parts) if parts else "")

    # ---- filtering
    def _filter(self, types=None, entity=None, role=None, value=None, speaker=None, frm=None, to=None):
        lo = _bound(frm, False) if frm else None
        hi = _bound(to, True) if to else None
        types = [t.strip().lower() for t in types] if types else None
        key = norm_entity(entity) if entity else None
        vs = _stems(value) if value else None
        if value and not vs:
            raise ValueError("value has no searchable words")
        spk = speaker.strip().lower() if speaker else None
        out = []
        for ev in self.events:
            if spk and ev["speaker"].lower() != spk:
                continue
            a, b = ev["when"]
            if lo and b < lo:
                continue
            if hi and a > hi:
                continue
            if key and key not in ev["_ent"]:
                continue
            if vs and not vs <= ev["_stems"]:
                continue
            rels = ev["relations"]
            if types:
                rels = [r for r in rels if r["type"].lower() in types]
                if not rels:
                    continue
            if role:
                rels = [r for r in rels if role in r["slots"]]
                if not rels:
                    continue
            out.append(ev)
        return out

    @staticmethod
    def _need_filter(**kw):
        if not any(v for v in kw.values()):
            raise ValueError("give at least one filter (types, entity, role, value, speaker, from or to)")

    # ---- tools
    def catalog(self):
        tc, roles, ex = Counter(), {}, {}
        for ev in self.events:
            for rel in ev["relations"]:
                tc[rel["type"]] += 1
                for r in rel["slots"]:
                    roles.setdefault(rel["type"], Counter())[r] += 1
                if rel["type"] not in ex:
                    ex[rel["type"]] = rel["slots"]
        multi = [t for t, c in tc.most_common() if c > 1]
        once = [t for t, c in tc.most_common() if c == 1]
        lines = []
        for t in multi:
            rs = ", ".join(r for r, _ in roles[t].most_common(5))
            exs = "; ".join(f"{r}={v[0]}" for r, v in list(ex[t].items())[:2])
            lines.append(f"{t} ({tc[t]}): {rs} | e.g. {exs}")
        if once:
            lines.append("once each: " + ", ".join(once))
        ec = Counter()
        for ev in self.events:
            for k in ev["_ent"]:
                ec[k] += 1
        top = ", ".join(f"{k} ({c})" for k, c in ec.most_common(30))
        lines.append("most linked entities: " + top)
        head = (f"{len(self.events)} events, {sum(tc.values())} relations, {len(tc)} relation types; turns dated {self.first.isoformat()} to "
                f"{self.last.isoformat()}; speakers {' and '.join(self.names)}. Types with count, main roles, example:")
        return _cap(head, lines, CATALOG_CAP)

    def find(self, types=None, entity=None, role=None, value=None, speaker=None, frm=None, to=None, offset=0):
        self._need_filter(types=types, entity=entity, role=role, value=value, speaker=speaker, frm=frm, to=to)
        offset = int(offset or 0)
        if offset < 0:
            raise ValueError("offset must be 0 or more")
        hit = self._filter(types, entity, role, value, speaker, frm, to)
        page = hit[offset:offset + PAGE]
        if not page:
            return f"{len(hit)} events match" + ("" if not hit else f" (offset {offset} is past the last match)")
        lines = [self.line(e) for e in page]
        n, used = 0, FIND_RESERVE                                  # header and continuation note are reserved
        for ln in lines:
            if used + _words(ln) > CAP:
                break
            used += _words(ln)
            n += 1
        if n == 0:                                                 # a single over-long event: cut its text, never skip it
            lines[0] = " ".join(lines[0].split()[:CAP - FIND_RESERVE]) + " ...(truncated)"
            n = 1
        left = len(hit) - (offset + n)
        out = [f"{len(hit)} events match; showing {offset + 1}-{offset + n}"] + lines[:n]
        if left:
            out.append(f"({left} more; the next one is at offset={offset + n})")
        return "\n".join(out)

    def count(self, types=None, entity=None, role=None, value=None, speaker=None, frm=None, to=None, by=None):
        self._need_filter(types=types, entity=entity, role=role, value=value, speaker=speaker, frm=frm, to=to)
        hit = self._filter(types, entity, role, value, speaker, frm, to)
        ents = {k for e in hit for k in e["_ent"]} - {norm_entity(n) for n in self.names}
        head = f"{len(hit)} events; {len(ents)} distinct entities"
        lines = []
        if by:
            if by == "type":
                c = Counter(r["type"] for e in hit for r in e["relations"] if not types or r["type"].lower() in [t.lower() for t in types])
            elif by == "speaker":
                c = Counter(e["speaker"] for e in hit)
            elif by == "month":
                c = Counter(e["date"].strftime("%Y-%m") for e in hit)
            else:
                raise ValueError("by must be type, speaker or month")
            lines.append(f"by {by}: " + ", ".join(f"{k} {v}" for k, v in sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))))
        ids = [e["id"] for e in hit]
        lines.append("events: " + ", ".join(ids[:40]) + (f" ... ({len(ids) - 40} more)" if len(ids) > 40 else ""))
        return _cap(head, lines)

    def values(self, entity, role=None):
        if not entity or not str(entity).strip():
            raise ValueError("entity is required")
        key = norm_entity(entity)
        groups = {}
        for ev in self.events:
            for rel in ev["relations"]:
                linked = {norm_entity(self.join(l, ev)) for _, l in rel["slots"].values() if l}
                if key not in linked:
                    continue
                for r, (v, l) in rel["slots"].items():
                    if role and r != role:
                        continue
                    if l and norm_entity(self.join(l, ev)) == key:
                        continue                                           # the entity itself is not a value of its own relation
                    groups.setdefault((rel["type"], r), {}).setdefault(self._slot_text(ev, v), []).append(ev["id"])
        if not groups:
            return f"No relation links '{entity}'" + (f" with a slot named '{role}'" if role else "") + ". Use find with value= to search the words."
        lines = []
        for (t, r), vals in sorted(groups.items()):
            lines.append(f"{t}.{r}: " + "; ".join(f"{v} [{', '.join(ids[:3])}{'...' if len(ids) > 3 else ''}]" for v, ids in list(vals.items())[:12]))
        return _cap(f"Values around '{entity}':", lines)

    def event(self, id):
        ev = self.by_id.get(str(id).strip())
        if not ev:
            return f"No event '{id}'. Events are named t0 to t{len(self.events) - 1}."
        return self.line(ev)

    def neighbors(self, id, k=3):
        ev = self.by_id.get(str(id).strip())
        if not ev:
            return f"No event '{id}'."
        k = int(k)
        if not 1 <= k <= MAX_K:
            raise ValueError(f"k must be 1 to {MAX_K}")
        lo, hi = max(0, ev["tick"] - k), min(len(self.events), ev["tick"] + k + 1)
        lines = [("> " + self.line(e)) if e["id"] == ev["id"] else self.line(e, with_relations=False) for e in self.events[lo:hi]]
        return _cap(f"Events around {ev['id']} (+-{k}):", lines)


# ---------------------------------------------------------------- search_turns (BM25, same scoring as the ND-3 RAG baseline)

class TurnIndex:
    def __init__(self, memory, k1=1.5, b=0.75):
        self.m, self.k1, self.b = memory, k1, b
        self.docs = [[t for t in ident(e["text"]).split() if t not in STOP] for e in memory.events]
        self.avg = sum(map(len, self.docs)) / len(self.docs)
        self.df = Counter(t for d in self.docs for t in set(d))

    def search(self, query):
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string")
        n = len(self.docs)
        q = [t for t in ident(query).split() if t not in STOP and t not in QUESTION_WORDS]

        def score(d):
            tf = Counter(d)
            return sum(math.log(1 + (n - self.df[t] + 0.5) / (self.df[t] + 0.5)) * tf[t] * (self.k1 + 1)
                       / (tf[t] + self.k1 * (1 - self.b + self.b * len(d) / self.avg)) for t in q if t in tf)
        ranked = sorted(range(n), key=lambda i: (-score(self.docs[i]), i))[:TOP_BM25]
        ranked = [i for i in ranked if score(self.docs[i]) > 0]
        if not ranked:
            return "No turns match."
        return _cap("", [self.m.line(self.m.events[i], with_relations=False) for i in sorted(ranked)])


def load(extraction_path, source_path):
    rows = [json.loads(l) for l in open(extraction_path, encoding="utf-8") if l.strip()]
    source = [json.loads(l) for l in open(source_path, encoding="utf-8") if l.strip()]
    return Memory(rows, source)
