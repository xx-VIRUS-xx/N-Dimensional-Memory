from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any


COMPETITOR = "graphrag"


def _run(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )


def build(
    corpus_path: str | Path,
    output_dir: str | Path,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Build a GraphRAG index.

    corpus_path:
        JSON/JSONL corpus containing canonical event IDs.

    output_dir:
        Dedicated GraphRAG project/index directory.

    config:
        Optional configuration overrides.
    """
    corpus_path = Path(corpus_path).resolve()
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    api_key = os.environ["GEMINI_API_KEY"]
    completion_model = os.getenv(
        "GRAPHRAG_COMPLETION_MODEL",
        "gemini-2.5-flash-lite",
    )
    embedding_model = os.getenv(
        "GRAPHRAG_EMBEDDING_MODEL",
        "gemini-embedding-001",
    )

    # GraphRAG expects an input directory.
    input_dir = output_dir / "input"
    input_dir.mkdir(exist_ok=True)

    # Keep the original corpus untouched.
    target = input_dir / corpus_path.name
    if not target.exists():
        target.write_bytes(corpus_path.read_bytes())

    settings = output_dir / "settings.yaml"

    settings.write_text(
        f"""
completion_models:
  default_completion_model:
    model_provider: gemini
    model: {completion_model}
    auth_method: api_key
    api_key: ${{GEMINI_API_KEY}}

embedding_models:
  default_embedding_model:
    model_provider: gemini
    model: {embedding_model}
    auth_method: api_key
    api_key: ${{GEMINI_API_KEY}}

input:
  type: file
  file_pattern: ".*\\\\.json$"

""".strip()
        + "\n",
        encoding="utf-8",
    )

    env = os.environ.copy()
    env["GEMINI_API_KEY"] = api_key

    _run(
        ["graphrag", "index", "--root", str(output_dir)],
        env=env,
    )

    return {
        "competitor": COMPETITOR,
        "status": "SUCCESS",
        "index_dir": str(output_dir),
        "completion_model": completion_model,
        "embedding_model": embedding_model,
    }


def retrieve(
    query: str,
    k: int,
    index_dir: str | Path,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Retrieve GraphRAG context.

    NOTE:
    GraphRAG's normal query interface returns textual/contextual results,
    not necessarily canonical benchmark event IDs.

    Therefore this adapter expects a benchmark-side mapping file produced
    during indexing:

        index_dir/event_id_map.json

    Format:
        {
            "chunk/node identifier": ["C01E003", ...]
        }

    This prevents evaluator-side gold leakage.
    """
    index_dir = Path(index_dir).resolve()

    env = os.environ.copy()
    env["GEMINI_API_KEY"] = os.environ["GEMINI_API_KEY"]

    result = _run(
        [
            "graphrag",
            "query",
            "--root",
            str(index_dir),
            "--method",
            "local",
            "--query",
            query,
        ],
        env=env,
    )

    text = result.stdout.strip()

    mapping_path = index_dir / "event_id_map.json"

    if not mapping_path.exists():
        raise RuntimeError(
            "GraphRAG index does not contain event_id_map.json. "
            "Canonical evidence mapping must be generated during build."
        )

    mapping = json.loads(mapping_path.read_text(encoding="utf-8"))

    evidence: list[dict[str, Any]] = []

    # The exact GraphRAG textual result format can vary by version.
    # We intentionally do not fabricate event IDs from the query.
    for node_id, event_ids in mapping.items():
        if node_id in text:
            for event_id in event_ids:
                evidence.append(
                    {
                        "event_id": event_id,
                        "score": None,
                    }
                )

    evidence = evidence[:k]

    return {
        "query": query,
        "condition": COMPETITOR,
        "status": "SUCCESS",
        "evidence": [
            {
                "event_id": item["event_id"],
                "rank": rank,
                "score": item["score"],
            }
            for rank, item in enumerate(evidence, start=1)
        ],
        "metadata": {
            "model": os.getenv(
                "GRAPHRAG_COMPLETION_MODEL",
                "gemini-2.5-flash-lite",
            ),
            "embedding_model": os.getenv(
                "GRAPHRAG_EMBEDDING_MODEL",
                "gemini-embedding-001",
            ),
        },
    }