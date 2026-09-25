#!/usr/bin/env python3
"""Evaluate top-k candidate pairs against an independently prepared gold set."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def canonical_pair(a: str, b: str) -> tuple[str, str]:
    a, b = a.strip().lower(), b.strip().lower()
    return (a, b) if a <= b else (b, a)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", required=True, type=Path)
    parser.add_argument("--gold", required=True, type=Path)
    parser.add_argument("--k", type=int, default=5)
    args = parser.parse_args()

    candidate_obj = json.loads(args.candidates.read_text(encoding="utf-8"))
    gold_rows = load_jsonl(args.gold)
    gold = {canonical_pair(row["entity_a"], row["entity_b"]) for row in gold_rows}

    topk: set[tuple[str, str]] = set()
    for entity, rows in candidate_obj["top_k_per_entity"].items():
        for row in rows[: args.k]:
            topk.add(canonical_pair(entity, row["other_entity"]))

    tp = len(topk & gold)
    precision = tp / len(topk) if topk else 0.0
    recall = tp / len(gold) if gold else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if precision + recall else 0.0

    result = {
        "k_per_entity": args.k,
        "gold_pairs": len(gold),
        "candidate_pairs_considered": len(topk),
        "true_positive_pairs": tp,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "matched_pairs": sorted(topk & gold),
        "unmatched_gold_pairs": sorted(gold - topk),
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
