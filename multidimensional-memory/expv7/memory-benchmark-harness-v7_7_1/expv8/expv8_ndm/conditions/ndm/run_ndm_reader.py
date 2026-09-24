from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ndm.retriever import NDMRetriever, QuerySpec


def load_json(path: Path) -> Any:
    with path.open(
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


def save_json(
    path: Path,
    data: Any,
) -> None:

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False,
        )


def main() -> None:

    parser = argparse.ArgumentParser(
        description="NDM V3.1 deterministic state-aware retriever"
    )

    parser.add_argument(
        "--memory",
        required=True,
    )

    parser.add_argument(
        "--queries",
        required=True,
    )

    parser.add_argument(
        "--output",
        required=True,
    )

    args = parser.parse_args()

    memory_path = Path(args.memory)
    queries_path = Path(args.queries)
    output_path = Path(args.output)

    memory = load_json(
        memory_path
    )

    queries = load_json(
        queries_path
    )

    if not isinstance(
        queries,
        list,
    ):
        raise ValueError(
            "Query file must contain a JSON array."
        )

    retriever = NDMRetriever(
        memory
    )

    results: List[Dict[str, Any]] = []

    for query in queries:

        spec = QuerySpec(
            query_id=str(
                query["query_id"]
            ),
            question=str(
                query["question"]
            ),
            mode=str(
                query.get(
                    "mode",
                    "current",
                )
            ),
            subject=query.get(
                "subject"
            ),
            scope=query.get(
                "scope"
            ),
        )

        result = retriever.retrieve(
            spec
        )

        # Store the full packet in the JSON file.
        results.append(result)

    output = {
        "status": "SUCCESS",
        "version": "ndm-retriever-v3.1",
        "memory_path": str(
            memory_path
        ),
        "query_count": len(results),
        "results": results,
    }

    save_json(
        output_path,
        output,
    )

    # ---------------------------------------------------------
    # COMPACT TERMINAL REPORT
    # ---------------------------------------------------------

    print()
    print("=" * 64)
    print("NDM V2 STATE-AWARE RECONSTRUCTION")
    print("=" * 64)

    print(
        f"Status:   SUCCESS"
    )

    print(
        f"Queries:  {len(results)}"
    )

    print(
        f"Output:   {output_path}"
    )

    print()
    print(
        "-" * 64
    )

    for result in results:

        qid = result[
            "query_id"
        ]

        mode = result[
            "mode"
        ]

        props = ",".join(
            result[
                "selected_proposition_ids"
            ]
        ) or "-"

        events = ",".join(
            result[
                "selected_event_ids"
            ]
        ) or "-"

        relation_count = len(
            result[
                "relationships"
            ]
        )

        belief_count = len(
            result[
                "beliefs"
            ]
        )

        negative_count = len(
            result[
                "negative_knowledge"
            ]
        )

        print(
            f"{qid:<5} "
            f"{mode:<14} "
            f"props=[{props}] "
            f"events=[{events}] "
            f"rel={relation_count} "
            f"belief={belief_count} "
            f"neg={negative_count}"
        )

    print()
    print(
        "=" * 64
    )


if __name__ == "__main__":
    main()