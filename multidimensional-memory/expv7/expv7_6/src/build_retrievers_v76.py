"""V7.6 retrieval baselines over the real 564-event corpus.

Honesty note (EXP-V7.6.md instrumentation rules): this environment has no
network/API access, so SEMANTIC_RAG here is TF-IDF + cosine similarity
(scikit-learn), not a neural embedding model. Disclosed explicitly in every
output file's retriever_note and in the report.
"""
import json
import re
from pathlib import Path

from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def tok(s):
    return re.findall(r"[a-z0-9]+", s.lower())


def main():
    events = [json.loads(line) for line in open(DATA / "conversation_v7_6.jsonl")]
    queries = json.load(open(ROOT / "evaluation" / "future_queries.json"))
    texts = [e["text"] for e in events]
    ids = [e["event_id"] for e in events]
    conv_by_id = {e["event_id"]: e["conversation_id"] for e in events}

    tokenized = [tok(t) for t in texts]
    bm25 = BM25Okapi(tokenized)

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(texts)

    TOP_K = 12  # matched to typical gold_event_ids set size (~12) for a fair evidence budget

    bm25_results, semantic_results, hybrid_results = {}, {}, {}

    for q in queries:
        qid = q["query_id"]
        question = q["query"]
        conv_id = q["conversation_id"]
        idxs = [i for i, e in enumerate(events) if e["conversation_id"] == conv_id]

        qtok = tok(question)
        scores = bm25.get_scores(qtok)
        bm25_ranked = sorted([(scores[i], ids[i]) for i in idxs], key=lambda x: (-x[0], x[1]))[:TOP_K]
        bm25_results[qid] = [{"event_id": eid, "score": round(float(sc), 6)} for sc, eid in bm25_ranked]

        qvec = vectorizer.transform([question])
        sims = cosine_similarity(qvec, tfidf_matrix)[0]
        sem_ranked = sorted([(sims[i], ids[i]) for i in idxs], key=lambda x: (-x[0], x[1]))[:TOP_K]
        semantic_results[qid] = [{"event_id": eid, "score": round(float(sc), 6)} for sc, eid in sem_ranked]

        bm25_by_id = {eid: sc for sc, eid in bm25_ranked}
        sem_by_id = {eid: sc for sc, eid in sem_ranked}
        all_ids = set(bm25_by_id) | set(sem_by_id)
        max_bm25 = max([abs(v) for v in bm25_by_id.values()] + [1e-9])
        max_sem = max([abs(v) for v in sem_by_id.values()] + [1e-9])
        hybrid_scored = [(0.5 * bm25_by_id.get(eid, 0) / max_bm25 + 0.5 * sem_by_id.get(eid, 0) / max_sem, eid) for eid in all_ids]
        hybrid_ranked = sorted(hybrid_scored, key=lambda x: (-x[0], x[1]))[:TOP_K]
        hybrid_results[qid] = [{"event_id": eid, "score": round(float(sc), 6)} for sc, eid in hybrid_ranked]

    json.dump(bm25_results, open(DATA / "retrieval_bm25.json", "w"), indent=2)
    json.dump(semantic_results, open(DATA / "retrieval_semantic.json", "w"), indent=2)
    json.dump(hybrid_results, open(DATA / "retrieval_hybrid.json", "w"), indent=2)
    print("wrote retrieval_bm25.json, retrieval_semantic.json, retrieval_hybrid.json")

    for name, results in [("BM25", bm25_results), ("SEMANTIC (TF-IDF)", semantic_results), ("HYBRID", hybrid_results)]:
        full_cov = 0
        partial_cov = 0
        for q in queries:
            qid = q["query_id"]
            retrieved_ids = {r["event_id"] for r in results[qid]}
            required = set(q["gold_event_ids"])
            if required.issubset(retrieved_ids):
                full_cov += 1
            elif retrieved_ids & required:
                partial_cov += 1
        print(f"{name}: {full_cov}/{len(queries)} queries fully covered, {partial_cov}/{len(queries)} partially covered")


if __name__ == "__main__":
    main()
