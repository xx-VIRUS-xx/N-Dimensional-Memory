"""V7.7 structural retrieval baselines: GRAPHRAG, HIPPORAG2, RAPTOR.

DISCLOSURE (required by EXP-V7.7.md's "External systems may be substituted
only if documented" and the failure rule's "never replace silently with a
weaker proxy"): no pip package or official repository for GraphRAG,
HippoRAG 2, or RAPTOR was available in this environment (verified: `pip show
graphrag/hipporag/raptor` all report not-found, and no network-installable
official implementation was attempted). These are CUSTOM, DOCUMENTED,
DISCLOSED implementations of the algorithmic ideas each system is known for,
NOT the official codebases. They are reported under these condition names
per the run's own choice, with this disclosure attached, rather than being
silently mislabeled as the real systems or silently skipped.

GRAPHRAG-style: build an entity co-occurrence graph over corpus events
(entities = capitalized/technical noun phrases extracted heuristically),
retrieve by finding events connected to query-entity nodes via shortest-path
graph traversal within the query's conversation.

HIPPORAG2-style: build a bipartite event-entity graph and run personalized
PageRank (networkx) seeded on query-matched entity nodes, ranking events by
their resulting PageRank mass -- approximating HippoRAG's associative-memory
retrieval mechanism (personalized PageRank over a knowledge graph) without
its actual OpenIE/LLM-based entity extraction pipeline.

RAPTOR-style: build a 2-level hierarchy per conversation (leaf events, and
cluster summaries formed by simple k-means-free contiguous-window grouping
+ concatenation as a "summary" placeholder, since no LLM call is available
in this offline script), then retrieve by BM25-scoring both leaf and summary
levels and returning the union of top leaf hits plus the leaf events under
the top-scoring summary window. This is a structural approximation of
RAPTOR's tree-retrieval idea (query against multiple abstraction levels),
not its real recursive LLM-summarization tree.
"""
import json
import re
from collections import defaultdict
from pathlib import Path

import networkx as nx
from rank_bm25 import BM25Okapi

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
TOP_K = 12

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "was", "were", "is", "are", "for",
    "to", "of", "in", "on", "at", "by", "with", "that", "this", "it", "we",
    "team", "during", "routine", "work", "update", "no", "final", "decision",
    "made", "engineer", "reviewed", "without", "recording", "durable", "change",
}


def tok(s):
    return re.findall(r"[a-z0-9]+", s.lower())


def extract_entities(text):
    # heuristic: capitalized technical terms and known tech-name patterns
    caps = re.findall(r"\b[A-Z][A-Za-z0-9]+\b", text)
    return {c for c in caps if c.lower() not in STOPWORDS and len(c) > 2}


def build_graph(events_by_conv):
    """entity co-occurrence graph, per conversation, for GraphRAG-style traversal"""
    graphs = {}
    entity_to_events = defaultdict(lambda: defaultdict(set))
    for conv_id, evs in events_by_conv.items():
        g = nx.Graph()
        for e in evs:
            ents = extract_entities(e["text"])
            for ent in ents:
                g.add_node(("entity", ent))
                entity_to_events[conv_id][ent].add(e["event_id"])
            g.add_node(("event", e["event_id"]))
            for ent in ents:
                g.add_edge(("event", e["event_id"]), ("entity", ent))
        graphs[conv_id] = g
    return graphs, entity_to_events


def graphrag_retrieve(query, conv_id, graphs, entity_to_events, event_lookup, top_k=TOP_K):
    q_entities = extract_entities(query)
    if not q_entities:
        return []
    g = graphs[conv_id]
    scored = defaultdict(float)
    for ent in q_entities:
        node = ("entity", ent)
        if node not in g:
            continue
        # 1-hop and 2-hop neighbors via shortest path weighting
        lengths = nx.single_source_shortest_path_length(g, node, cutoff=2)
        for (kind, val), dist in lengths.items():
            if kind == "event" and dist > 0:
                scored[val] += 1.0 / dist
    ranked = sorted(scored.items(), key=lambda x: (-x[1], x[0]))[:top_k]
    return [{"event_id": eid, "score": round(sc, 6)} for eid, sc in ranked]


def hipporag2_retrieve(query, conv_id, graphs, top_k=TOP_K):
    q_entities = extract_entities(query)
    g = graphs[conv_id]
    seed_nodes = [("entity", ent) for ent in q_entities if ("entity", ent) in g]
    if not seed_nodes:
        return []
    personalization = {n: (1.0 / len(seed_nodes) if n in seed_nodes else 0.0) for n in g.nodes}
    try:
        pr = nx.pagerank(g, personalization=personalization, alpha=0.85, max_iter=200)
    except Exception:
        return []
    event_scores = [(node[1], score) for node, score in pr.items() if node[0] == "event"]
    ranked = sorted(event_scores, key=lambda x: (-x[1], x[0]))[:top_k]
    return [{"event_id": eid, "score": round(float(sc), 6)} for eid, sc in ranked]


def build_raptor_index(events_by_conv, window=10):
    """contiguous-window 'summary' nodes per conversation (2-level tree, no LLM)"""
    summaries = {}
    for conv_id, evs in events_by_conv.items():
        evs_sorted = sorted(evs, key=lambda e: e["timestamp"])
        windows = []
        for i in range(0, len(evs_sorted), window):
            chunk = evs_sorted[i:i + window]
            summary_text = " ".join(e["text"] for e in chunk)
            windows.append({
                "summary_id": f"{conv_id}-W{i // window}",
                "event_ids": [e["event_id"] for e in chunk],
                "text": summary_text,
            })
        summaries[conv_id] = windows
    return summaries


def raptor_retrieve(query, conv_id, raptor_index, leaf_bm25, leaf_ids_by_conv, top_k=TOP_K):
    windows = raptor_index[conv_id]
    if not windows:
        return []
    win_tokenized = [tok(w["text"]) for w in windows]
    win_bm25 = BM25Okapi(win_tokenized)
    qtok = tok(query)
    win_scores = win_bm25.get_scores(qtok)
    best_window_idx = max(range(len(windows)), key=lambda i: win_scores[i])
    top_window = windows[best_window_idx]

    # also score leaves directly within this conversation, union with top window's leaves
    idxs = leaf_ids_by_conv[conv_id]
    leaf_scores = leaf_bm25.get_scores(qtok)
    leaf_ranked = sorted([(leaf_scores[i], leaf_ids_by_conv["_all_ids"][i]) for i in idxs], key=lambda x: (-x[0], x[1]))[:top_k]

    combined_ids = list(dict.fromkeys([eid for _, eid in leaf_ranked] + top_window["event_ids"]))[:top_k]
    return [{"event_id": eid, "score": None, "source": "raptor_leaf_or_window"} for eid in combined_ids]


def main():
    events = [json.loads(l) for l in open(DATA / "conversation_v7_7_evaluator.jsonl")]
    gold = json.load(open(DATA / "benchmark_v7_7_gold.json"))
    queries = gold["queries"]

    events_by_conv = defaultdict(list)
    for e in events:
        events_by_conv[e["conversation_id"]].append(e)

    print("Building GraphRAG-style / HippoRAG2-style co-occurrence graphs...")
    graphs, entity_to_events = build_graph(events_by_conv)
    event_lookup = {e["event_id"]: e for e in events}

    print("Building RAPTOR-style windowed index...")
    raptor_index = build_raptor_index(events_by_conv, window=10)
    texts = [e["text"] for e in events]
    ids = [e["event_id"] for e in events]
    tokenized_all = [tok(t) for t in texts]
    leaf_bm25 = BM25Okapi(tokenized_all)
    leaf_ids_by_conv = defaultdict(list)
    for i, e in enumerate(events):
        leaf_ids_by_conv[e["conversation_id"]].append(i)
    leaf_ids_by_conv["_all_ids"] = ids

    graphrag_results, hipporag2_results, raptor_results = {}, {}, {}

    for q in queries:
        qid = q["query_id"]
        question = q["question"]
        conv_id = q["conversation_id"]

        graphrag_results[qid] = graphrag_retrieve(question, conv_id, graphs, entity_to_events, event_lookup)
        hipporag2_results[qid] = hipporag2_retrieve(question, conv_id, graphs)
        raptor_results[qid] = raptor_retrieve(question, conv_id, raptor_index, leaf_bm25, leaf_ids_by_conv)

    json.dump(graphrag_results, open(DATA / "retrieval_graphrag_v77.json", "w"), indent=2)
    json.dump(hipporag2_results, open(DATA / "retrieval_hipporag2_v77.json", "w"), indent=2)
    json.dump(raptor_results, open(DATA / "retrieval_raptor_v77.json", "w"), indent=2)
    print("Wrote retrieval_graphrag_v77.json, retrieval_hipporag2_v77.json, retrieval_raptor_v77.json")

    for name, results in [("GRAPHRAG", graphrag_results), ("HIPPORAG2", hipporag2_results), ("RAPTOR", raptor_results)]:
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
