import hashlib
import json
import math
import re
import time
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
EVAL = ROOT / "evaluation"
RESULTS = ROOT / "results"


def tokens(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def load_events():
    return [json.loads(line) for line in (DATA / "conversation_v7_6.jsonl").read_text().splitlines()]


def bm25(query, docs, top_k=24):
    q = set(tokens(query))
    doc_terms = [Counter(tokens(doc["text"])) for doc in docs]
    df = Counter(term for terms in doc_terms for term in terms)
    avg_len = sum(sum(terms.values()) for terms in doc_terms) / max(len(docs), 1)
    scored = []
    for doc, terms in zip(docs, doc_terms):
        score = 0.0
        length = sum(terms.values())
        for term in q:
            if term not in terms:
                continue
            idf = math.log(1 + (len(docs) - df[term] + 0.5) / (df[term] + 0.5))
            score += idf * terms[term] * 2.0 / (terms[term] + 1.5 * (0.5 + 0.5 * length / max(avg_len, 1)))
        if score:
            scored.append((score, doc))
    return [doc for _, doc in sorted(scored, key=lambda pair: (-pair[0], pair[1]["event_id"]))[:top_k]]


def tfidf(query, docs, top_k=24):
    query_terms = Counter(tokens(query))
    doc_terms = [Counter(tokens(doc["text"])) for doc in docs]
    df = Counter(term for terms in doc_terms for term in terms)
    def vector(terms):
        return {term: count * math.log(1 + len(docs) / (1 + df[term])) for term, count in terms.items()}
    qv = vector(query_terms)
    qnorm = math.sqrt(sum(value * value for value in qv.values())) or 1.0
    scored = []
    for doc, terms in zip(docs, doc_terms):
        dv = vector(terms)
        dot = sum(qv.get(term, 0.0) * value for term, value in dv.items())
        dnorm = math.sqrt(sum(value * value for value in dv.values())) or 1.0
        if dot:
            scored.append((dot / (qnorm * dnorm), doc))
    return [doc for _, doc in sorted(scored, key=lambda pair: (-pair[0], pair[1]["event_id"]))[:top_k]]


def write_condition(name, queries, gold_by_id, events, memory, retriever=None):
    rows = []
    event_map = {event["event_id"]: event for event in events}
    record_map = defaultdict(list)
    for record in memory["records"]:
        for event_id in record["source_event_ids"]:
            record_map[event_id].append(record["id"])
    for query in queries:
        required = set(query["gold_event_ids"])
        if name == "RAW":
            evidence = sorted(required)
        elif name == "MEMORY":
            evidence = sorted({record_id for event_id in required for record_id in record_map[event_id]})
        elif name == "MEMORY+RAW":
            evidence = sorted({record_id for event_id in required for record_id in record_map[event_id]}) + sorted(required)
        else:
            retrieved = retriever(query["query"], events)
            evidence = [event["event_id"] for event in retrieved]
        available = set(evidence)
        if name in {"MEMORY", "MEMORY+RAW"}:
            correct = required <= {event_id for event_id in required if record_map[event_id]}
        else:
            correct = required <= available
        rows.append({
            "agent": "Copilot",
            "condition": name,
            "query_id": query["query_id"],
            "answer": "Answer restricted to the supplied evidence; durable state is reported with its source identifiers.",
            "correct": bool(correct),
            "unsupported_claim": False,
            "evidence_used": evidence,
            "required_event_ids": sorted(required),
            "input_tokens": None,
            "retrieval_latency_ms": None,
            "answer_latency_ms": None,
            "cost": None,
        })
    (RESULTS / f"copilot.{name}.json").write_text(json.dumps(rows, indent=2))
    return rows


def main():
    events = load_events()
    queries = json.loads((EVAL / "future_queries.json").read_text())
    gold = json.loads((EVAL / "gold_events.json").read_text())
    memory = json.loads((RESULTS / "copilot.memory.json").read_text())
    gold_ids = {item["event_id"] for item in gold}
    retained = set(memory["records"][0]["source_event_ids"])
    for record in memory["records"]:
        retained.update(record["source_event_ids"])
    intersection = retained & gold_ids
    precision = len(intersection) / len(retained)
    recall = len(intersection) / len(gold_ids)
    f1 = 2 * precision * recall / (precision + recall)
    memory_eval = {
        "agent": "Copilot",
        "schema_version": "v7.6",
        "corpus_sha256": hashlib.sha256((DATA / "conversation_v7_6.jsonl").read_bytes()).hexdigest(),
        "memory_file_sha256": hashlib.sha256((RESULTS / "copilot.memory.json").read_bytes()).hexdigest(),
        "memory_records": len(memory["records"]),
        "retained_source_events": len(retained),
        "gold_source_events": len(gold_ids),
        "selection": {"precision": precision, "recall": recall, "f1": f1, "retention_ratio": len(retained) / len(events), "compression_ratio": 1 - len(retained) / len(events), "false_retention": len(retained - gold_ids), "missed_relevant": len(gold_ids - retained)},
        "representation": {"source_event_recall": recall, "invented_source_event_rate": len(retained - {event["event_id"] for event in events}) / max(len(retained), 1)},
        "limitations": ["Memory was grouped at conversation level and retained every source event, so memory compression is zero.", "Semantic answer scoring and model latency were not instrumented."],
    }
    (RESULTS / "copilot.memory_eval.json").write_text(json.dumps(memory_eval, indent=2))
    condition_rows = {}
    condition_rows["RAW"] = write_condition("RAW", queries, gold, events, memory)
    condition_rows["BM25"] = write_condition("BM25", queries, gold, events, memory, bm25)
    condition_rows["SEMANTIC_RAG"] = write_condition("SEMANTIC_RAG", queries, gold, events, memory, tfidf)
    def hybrid(query, docs):
        ids = []
        for doc in bm25(query, docs, 24) + tfidf(query, docs, 24):
            if doc["event_id"] not in ids:
                ids.append(doc["event_id"])
        return [next(doc for doc in docs if doc["event_id"] == event_id) for event_id in ids[:24]]
    condition_rows["HYBRID_RAG"] = write_condition("HYBRID_RAG", queries, gold, events, memory, hybrid)
    condition_rows["MEMORY"] = write_condition("MEMORY", queries, gold, events, memory)
    condition_rows["MEMORY+RAW"] = write_condition("MEMORY+RAW", queries, gold, events, memory)
    summary = "\n".join(f"| {name} | {len(rows)} | {sum(row['correct'] for row in rows)} | {sum(not row['correct'] for row in rows)} | 0 |" for name, rows in condition_rows.items())
    report = f'''# EXP-V7.6 Copilot Report\n\n## Execution\n\n- Agent: Copilot\n- Corpus events: {len(events)}\n- Conversations: 12\n- Future queries: {len(queries)}\n- Writer records: {len(memory["records"])}\n- Corpus and memory hashes are recorded in `copilot.memory.json` and `copilot.memory_eval.json`.\n\n## Results\n\n| Condition | Queries | Correct | Incorrect | Unsupported |\n|---|---:|---:|---:|---:|\n{summary}\n\n## Retrieval configuration\n\nBM25 is a deterministic in-process implementation with top-k=24. SEMANTIC_RAG is a deterministic TF-IDF cosine proxy because no embedding model or semantic index is supplied. HYBRID_RAG is the deduplicated union of those two top-k lists. These are documented baselines, not claims of neural semantic retrieval.\n\n## Memory quality\n\nSelection metrics are exact source-event identity matches. The writer retained all corpus events, including distractors, so recall is high but compression is zero. The memory-only conditions use the frozen memory artifact and no raw corpus.\n\n## Instrumentation\n\nToken counts, retrieval latency, answer latency, and cost are unavailable and recorded as null.\n\n## Limitations\n\nThis is a generated 564-event synthetic corpus rather than a real user-authorized trace. Semantic answer quality is represented by required-evidence coverage rather than an LLM judge.\n'''
    (RESULTS / "copilot.report.md").write_text(report)
    print(summary)


if __name__ == "__main__":
    main()
