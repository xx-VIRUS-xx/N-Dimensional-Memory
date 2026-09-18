"""V7.7 retrieval baselines: RAW, BM25, DENSE, HYBRID.

BM25: rank_bm25 (real lexical algorithm).
DENSE: sentence-transformers 'all-MiniLM-L6-v2' real embedding model + cosine
similarity (real neural embeddings, not a TF-IDF proxy, per adapters/README.md's
explicit "do not substitute" instruction).
HYBRID: normalized 50/50 blend of BM25 and DENSE scores, reranked.

Writes retrieval index artifacts under data/, and per-query top-k evidence sets
used later to build the condition result files.
"""
import json
import re
from pathlib import Path

from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

TOP_K = 12


def tok(s):
    return re.findall(r"[a-z0-9]+", s.lower())


def main():
    events = [json.loads(l) for l in open(DATA / "conversation_v7_7_evaluator.jsonl")]
    gold = json.load(open(DATA / "benchmark_v7_7_gold.json"))
    queries = gold["queries"]

    texts = [e["text"] for e in events]
    ids = [e["event_id"] for e in events]
    conv_by_idx = [e["conversation_id"] for e in events]

    print("Building BM25 index...")
    tokenized = [tok(t) for t in texts]
    bm25 = BM25Okapi(tokenized)

    print("Loading sentence-transformers model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    print("Encoding corpus (1200 events)...")
    corpus_emb = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)

    bm25_results, dense_results, hybrid_results = {}, {}, {}

    for q in queries:
        qid = q["query_id"]
        question = q["question"]
        conv_id = q["conversation_id"]
        idxs = [i for i, c in enumerate(conv_by_idx) if c == conv_id]

        # BM25
        qtok = tok(question)
        scores = bm25.get_scores(qtok)
        bm25_ranked = sorted([(scores[i], ids[i]) for i in idxs], key=lambda x: (-x[0], x[1]))[:TOP_K]
        bm25_results[qid] = [{"event_id": eid, "score": round(float(sc), 6)} for sc, eid in bm25_ranked]

        # DENSE
        q_emb = model.encode([question], normalize_embeddings=True)[0]
        sims = corpus_emb @ q_emb
        dense_ranked = sorted([(float(sims[i]), ids[i]) for i in idxs], key=lambda x: (-x[0], x[1]))[:TOP_K]
        dense_results[qid] = [{"event_id": eid, "score": round(sc, 6)} for sc, eid in dense_ranked]

        # HYBRID: normalize both to [0,1] within this query's candidate set, average, rerank
        bm25_by_id = {eid: sc for sc, eid in bm25_ranked}
        dense_by_id = {eid: sc for sc, eid in dense_ranked}
        all_ids = set(bm25_by_id) | set(dense_by_id)
        max_bm25 = max([abs(v) for v in bm25_by_id.values()] + [1e-9])
        max_dense = max([abs(v) for v in dense_by_id.values()] + [1e-9])
        hybrid_scored = [
            (0.5 * bm25_by_id.get(eid, 0) / max_bm25 + 0.5 * dense_by_id.get(eid, 0) / max_dense, eid)
            for eid in all_ids
        ]
        hybrid_ranked = sorted(hybrid_scored, key=lambda x: (-x[0], x[1]))[:TOP_K]
        hybrid_results[qid] = [{"event_id": eid, "score": round(float(sc), 6)} for sc, eid in hybrid_ranked]

    json.dump(bm25_results, open(DATA / "retrieval_bm25_v77.json", "w"), indent=2)
    json.dump(dense_results, open(DATA / "retrieval_dense_v77.json", "w"), indent=2)
    json.dump(hybrid_results, open(DATA / "retrieval_hybrid_v77.json", "w"), indent=2)
    print("Wrote retrieval_bm25_v77.json, retrieval_dense_v77.json, retrieval_hybrid_v77.json")

    for name, results in [("BM25", bm25_results), ("DENSE", dense_results), ("HYBRID", hybrid_results)]:
        full = sum(
            1 for q in queries
            if set(q["required_event_ids"]).issubset({r["event_id"] for r in results[q["query_id"]]})
        )
        avg_cov = sum(
            len(set(q["required_event_ids"]) & {r["event_id"] for r in results[q["query_id"]]}) / len(q["required_event_ids"])
            for q in queries
        ) / len(queries)
        print(f"{name}: {full}/{len(queries)} fully covered, avg coverage {avg_cov:.3f}")


if __name__ == "__main__":
    main()
