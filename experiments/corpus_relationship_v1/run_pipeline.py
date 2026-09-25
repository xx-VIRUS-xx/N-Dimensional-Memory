#!/usr/bin/env python3
"""Build entity representations and mathematical candidate relationships for NDM v1."""

from __future__ import annotations

import argparse
import itertools
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


EPS = 1e-12


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, 1):
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON at {path}:{line_no}: {exc}") from exc
            if not isinstance(obj, dict):
                raise ValueError(f"Expected object at {path}:{line_no}")
            rows.append(obj)
    return rows


def normalize_name(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def validate_input(events: list[dict[str, Any]]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    event_ids: set[str] = set()
    entity_names_by_key: dict[str, set[str]] = defaultdict(set)
    entity_count = 0
    dimension_count = 0

    for idx, event in enumerate(events, 1):
        event_id = event.get("event_id")
        entities = event.get("entities")
        if not isinstance(event_id, str) or not event_id.strip():
            errors.append(f"row {idx}: event_id must be a non-empty string")
            continue
        if event_id in event_ids:
            errors.append(f"row {idx}: duplicate event_id={event_id!r}")
        event_ids.add(event_id)
        if not isinstance(entities, list):
            errors.append(f"event {event_id!r}: entities must be a list")
            continue
        for entity_idx, entity in enumerate(entities, 1):
            if not isinstance(entity, dict):
                errors.append(f"event {event_id!r}: entity {entity_idx} must be an object")
                continue
            name = entity.get("name")
            dimensions = entity.get("dimensions")
            if not isinstance(name, str) or not name.strip():
                errors.append(f"event {event_id!r}: entity {entity_idx} has invalid name")
                continue
            if not isinstance(dimensions, list):
                errors.append(f"event {event_id!r}: entity {name!r} dimensions must be a list")
                continue
            entity_count += 1
            entity_names_by_key[normalize_name(name)].add(name.strip())
            for dim_idx, dim in enumerate(dimensions, 1):
                if not isinstance(dim, dict):
                    errors.append(f"event {event_id!r}, entity {name!r}, dimension {dim_idx}: must be an object")
                    continue
                dname = dim.get("name")
                dvalue = dim.get("value")
                if not isinstance(dname, str) or not dname.strip():
                    errors.append(f"event {event_id!r}, entity {name!r}, dimension {dim_idx}: invalid name")
                if not isinstance(dvalue, str) or not dvalue.strip():
                    errors.append(f"event {event_id!r}, entity {name!r}, dimension {dim_idx}: invalid value")
                dimension_count += 1

    for key, originals in entity_names_by_key.items():
        if len(originals) > 1:
            warnings.append(f"entity normalization merges spellings {sorted(originals)!r} into {key!r}")

    if not event_ids:
        errors.append("input contains no events")

    return {
        "events": len(events),
        "entity_records": entity_count,
        "dimension_records": dimension_count,
        "unique_normalized_entities": len(entity_names_by_key),
        "errors": errors,
        "warnings": warnings,
        "valid": not errors,
    }


def build_dimension_records(events: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    records: list[dict[str, Any]] = []
    entities: dict[str, dict[str, Any]] = {}
    for event in events:
        event_id = event["event_id"]
        for entity in event["entities"]:
            name = entity["name"].strip()
            key = normalize_name(name)
            entity_meta = entities.setdefault(
                key,
                {"entity_id": key, "display_name": name, "events": set(), "dimension_count": 0},
            )
            entity_meta["events"].add(event_id)
            entity_meta["dimension_count"] += len(entity["dimensions"])
            for dimension in entity["dimensions"]:
                records.append({
                    "event_id": event_id,
                    "entity_id": key,
                    "entity_name": name,
                    "dimension_name": dimension["name"].strip(),
                    "dimension_value": dimension["value"].strip(),
                    "text": f"{dimension['name'].strip()}: {dimension['value'].strip()}",
                })
    return records, entities


def l2_normalize(matrix: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    return matrix / np.maximum(norms, EPS)


def aggregate_entity_vectors(
    entity_ids: list[str], records: list[dict[str, Any]], dimension_embeddings: np.ndarray
) -> np.ndarray:
    positions: dict[str, list[int]] = defaultdict(list)
    for idx, record in enumerate(records):
        positions[record["entity_id"]].append(idx)
    vectors = []
    for entity_id in entity_ids:
        idxs = positions[entity_id]
        vectors.append(dimension_embeddings[idxs].mean(axis=0))
    return l2_normalize(np.vstack(vectors))


def pair_signals(
    entity_ids: list[str],
    records: list[dict[str, Any]],
    entity_vectors: np.ndarray,
) -> list[dict[str, Any]]:
    names_by_entity: dict[str, set[str]] = defaultdict(set)
    text_by_entity: dict[str, list[str]] = defaultdict(list)
    events_by_entity: dict[str, set[str]] = defaultdict(set)
    for record in records:
        names_by_entity[record["entity_id"]].add(record["dimension_name"].strip().lower())
        text_by_entity[record["entity_id"]].append(record["text"])
        events_by_entity[record["entity_id"]].add(record["event_id"])

    tfidf_docs = [" ".join(text_by_entity[eid]) for eid in entity_ids]
    tfidf = TfidfVectorizer(lowercase=True, ngram_range=(1, 2)).fit_transform(tfidf_docs)
    tfidf_sim = cosine_similarity(tfidf)
    semantic_sim = entity_vectors @ entity_vectors.T

    results: list[dict[str, Any]] = []
    for i, j in itertools.combinations(range(len(entity_ids)), 2):
        a, b = entity_ids[i], entity_ids[j]
        names_a, names_b = names_by_entity[a], names_by_entity[b]
        union_names = len(names_a | names_b)
        dim_name_jaccard = len(names_a & names_b) / union_names if union_names else 0.0

        events_a, events_b = events_by_entity[a], events_by_entity[b]
        event_union = events_a | events_b
        event_jaccard = len(events_a & events_b) / len(event_union) if event_union else 0.0

        semantic_cosine = float(np.clip(semantic_sim[i, j], -1.0, 1.0))
        tfidf_cosine = float(np.clip(tfidf_sim[i, j], 0.0, 1.0))
        candidate_score = (
            0.60 * max(0.0, semantic_cosine)
            + 0.15 * dim_name_jaccard
            + 0.15 * event_jaccard
            + 0.10 * tfidf_cosine
        )
        results.append({
            "entity_a": a,
            "entity_b": b,
            "semantic_cosine": semantic_cosine,
            "dimension_name_jaccard": dim_name_jaccard,
            "event_jaccard": event_jaccard,
            "shared_event_count": len(events_a & events_b),
            "dimension_text_tfidf_cosine": tfidf_cosine,
            "candidate_score": candidate_score,
        })
    return results


def top_k_candidates(pair_rows: list[dict[str, Any]], entity_ids: list[str], k: int) -> dict[str, list[dict[str, Any]]]:
    by_entity: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in pair_rows:
        by_entity[row["entity_a"]].append({**row, "other_entity": row["entity_b"]})
        by_entity[row["entity_b"]].append({**row, "other_entity": row["entity_a"]})
    output: dict[str, list[dict[str, Any]]] = {}
    for entity_id in entity_ids:
        rows = sorted(by_entity[entity_id], key=lambda r: r["candidate_score"], reverse=True)
        output[entity_id] = rows[:k]
    return output


def save_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Entity-dimension JSONL")
    parser.add_argument("--output", required=True, type=Path, help="Output directory")
    parser.add_argument("--model", default="sentence-transformers/all-MiniLM-L6-v2")
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args()
    if args.top_k < 1:
        parser.error("--top-k must be >= 1")

    args.output.mkdir(parents=True, exist_ok=True)
    events = load_jsonl(args.input)
    report = validate_input(events)
    save_json(args.output / "validation_report.json", report)
    if not report["valid"]:
        raise SystemExit("Input validation failed. See validation_report.json")

    records, entities_meta = build_dimension_records(events)
    entity_ids = sorted(entities_meta)
    save_json(
        args.output / "entities.json",
        [{**entities_meta[eid], "events": sorted(entities_meta[eid]["events"])} for eid in entity_ids],
    )
    with (args.output / "dimension_records.jsonl").open("w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"Encoding {len(records)} dimensions for {len(entity_ids)} entities with {args.model} ...")
    model = SentenceTransformer(args.model)
    dimension_embeddings = model.encode(
        [record["text"] for record in records],
        batch_size=args.batch_size,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=False,
    )
    entity_vectors = aggregate_entity_vectors(entity_ids, records, dimension_embeddings)
    similarity = entity_vectors @ entity_vectors.T
    np.save(args.output / "entity_features.npy", entity_vectors)
    np.save(args.output / "similarity_matrix.npy", similarity)

    pair_rows = sorted(
        pair_signals(entity_ids, records, entity_vectors),
        key=lambda row: row["candidate_score"],
        reverse=True,
    )
    with (args.output / "pair_signals.jsonl").open("w", encoding="utf-8") as fh:
        for row in pair_rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    candidates = top_k_candidates(pair_rows, entity_ids, args.top_k)
    save_json(
        args.output / "candidate_relationships.json",
        {
            "score_definition": "0.60 semantic + 0.15 dimension-name-overlap + 0.15 event-overlap + 0.10 lexical",
            "note": "Candidate ranking only; not a verified semantic relationship graph.",
            "top_k_per_entity": candidates,
        },
    )

    if len(entity_ids) >= 2:
        projection = PCA(n_components=2, random_state=0).fit_transform(entity_vectors)
        fig, ax = plt.subplots(figsize=(11, 8))
        ax.scatter(projection[:, 0], projection[:, 1], s=36)
        if len(entity_ids) <= 100:
            for idx, entity_id in enumerate(entity_ids):
                ax.annotate(entity_id, (projection[idx, 0], projection[idx, 1]), fontsize=8, xytext=(4, 4), textcoords="offset points")
        ax.set_title("NDM Entity Projection (PCA)")
        ax.set_xlabel("PC1")
        ax.set_ylabel("PC2")
        fig.tight_layout()
        fig.savefig(args.output / "entity_projection.png", dpi=180)
        plt.close(fig)

    summary = {
        "events": len(events),
        "entities": len(entity_ids),
        "dimensions": len(records),
        "pair_count": len(pair_rows),
        "top_pair": pair_rows[0] if pair_rows else None,
        "model": args.model,
        "top_k": args.top_k,
    }
    save_json(args.output / "run_summary.json", summary)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
