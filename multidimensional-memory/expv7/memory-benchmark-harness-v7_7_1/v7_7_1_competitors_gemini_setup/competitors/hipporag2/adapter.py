from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any


COMPETITOR = "hipporag2"


# def _compose_file() -> Path:
#     return Path(
#         os.getenv(
#             "V771_LEGACY_COMPOSE",
#             "v7_7_1_competitors_gemini_setup/"
#             "docker/legacy-baselines.compose.yml",
#         )
#     ).resolve()

def _compose_file() -> Path:
    configured = os.getenv("V771_LEGACY_COMPOSE")

    if configured:
        path = Path(configured).expanduser().resolve()
        if not path.exists():
            raise RuntimeError(
                f"V771_LEGACY_COMPOSE points to a missing file: {path}"
            )
        return path

    # adapter.py:
    # v7_7_1_competitors_gemini_setup/
    #   competitors/hipporag2/adapter.py
    #   docker/legacy-baselines.compose.yml
    adapter_root = Path(__file__).resolve().parents[2]
    compose_file = (
        adapter_root
        / "docker"
        / "legacy-baselines.compose.yml"
    )

    if not compose_file.exists():
        raise RuntimeError(
            f"HippoRAG Compose file not found: {compose_file}"
        )

    return compose_file

def _run_container(
    service: str,
    script: str,
    *,
    mounts: dict[Path, str],
    env: dict[str, str] | None = None,
) -> str:
    compose_file = _compose_file()

    if not compose_file.exists():
        raise RuntimeError(f"Compose file not found: {compose_file}")

    cmd = [
        "docker",
        "compose",
        "-f",
        str(compose_file),
        "run",
        "--rm",
    ]

    # Docker Compose run options MUST come before the service name.
    for host, container in mounts.items():
        cmd.extend([
            "-v",
            f"{Path(host).resolve()}:{container}",
        ])

    if env:
        for key, value in env.items():
            cmd.extend([
                "-e",
                f"{key}={value}",
            ])

    # Service name comes after all `docker compose run` options.
    cmd.extend([
        service,
        "python",
        "-c",
        script,
    ])

    child_env = os.environ.copy()
    if env:
        child_env.update(env)

    result = subprocess.run(
        cmd,
        text=True,
        capture_output=True,
        env=child_env,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "HippoRAG2 container execution failed.\n"
            f"command: {' '.join(cmd)}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )

    return result.stdout


def _write_config(
    config: dict[str, Any] | None,
    output_dir: Path,
) -> Path:
    cfg = dict(config or {})

    cfg.setdefault("llm_name", "gemini-2.5-flash")
    cfg.setdefault(
        "llm_base_url",
        "https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    cfg.setdefault("embedding_provider", "openai")
    cfg.setdefault("embedding_model_name", "gemini-embedding-001")
    cfg.setdefault(
        "embedding_base_url",
        "https://generativelanguage.googleapis.com/v1beta/openai/",
    )

    path = output_dir / "hipporag.config.json"
    path.write_text(
        json.dumps(cfg, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return path


def build(
    corpus_path: str | Path,
    output_dir: str | Path,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    corpus_path = Path(corpus_path).resolve()
    output_dir = Path(output_dir).resolve()

    if not corpus_path.is_file():
        raise FileNotFoundError(f"Corpus not found: {corpus_path}")

    output_dir.mkdir(parents=True, exist_ok=True)
    config_path = _write_config(config, output_dir)

    mounts = {
        corpus_path.parent: "/workspace/input",
        output_dir: "/workspace/results",
    }

    script = r"""
import json
import os
from pathlib import Path

from hipporag import HippoRAG
from hipporag.utils.config_utils import BaseConfig
from hipporag.utils.misc_utils import Chunk

corpus_path = Path("/workspace/input") / os.environ["CORPUS_FILE"]
output_dir = Path("/workspace/results")
config_path = output_dir / "hipporag.config.json"

with corpus_path.open("r", encoding="utf-8") as f:
    events = json.load(f)

if not isinstance(events, list):
    raise ValueError("Corpus must be a JSON array of event objects.")

docs = []
seen_ids = set()

for event in events:
    required = ("event_id", "conversation_id", "timestamp", "text")
    missing = [key for key in required if key not in event]
    if missing:
        raise ValueError(
            f"Event missing required fields: {missing}; event={event!r}"
        )

    event_id = event["event_id"]
    if event_id in seen_ids:
        raise ValueError(f"Duplicate canonical event_id: {event_id}")
    seen_ids.add(event_id)

    docs.append(
        Chunk(
            content=event["text"],
            source_id=event_id,
            metadata={
                "event_id": event_id,
                "conversation_id": event["conversation_id"],
                "timestamp": event["timestamp"],
            },
        )
    )

cfg = json.loads(config_path.read_text(encoding="utf-8"))

hippo_config = BaseConfig(
    llm_name=cfg["llm_name"],
    llm_base_url=cfg.get("llm_base_url"),
    embedding_provider=cfg.get("embedding_provider", "openai"),
    embedding_model_name=cfg["embedding_model_name"],
    embedding_base_url=cfg.get("embedding_base_url"),
    save_dir=str(output_dir),
)

rag = HippoRAG(
    global_config=hippo_config,
    save_dir=str(output_dir),
)

rag.index(docs)

manifest = {
    "competitor": "hipporag2",
    "status": "SUCCESS",
    "num_events": len(events),
    "num_indexed_documents": len(docs),
    "event_ids": sorted(seen_ids),
    "config": cfg,
}

(output_dir / "build_manifest.json").write_text(
    json.dumps(manifest, indent=2, sort_keys=True),
    encoding="utf-8",
)

print(json.dumps(manifest, sort_keys=True))
"""

    _run_container(
        "hipporag2",
        script,
        mounts=mounts,
        env={"CORPUS_FILE": corpus_path.name},
    )

    return {
        "competitor": COMPETITOR,
        "status": "SUCCESS",
        "index_dir": str(output_dir),
        "config_path": str(config_path),
    }


def retrieve(
    query: str,
    k: int,
    index_dir: str | Path,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not query or not query.strip():
        raise ValueError("query must be a non-empty string")
    if k <= 0:
        raise ValueError("k must be > 0")

    index_dir = Path(index_dir).resolve()
    if not index_dir.is_dir():
        raise FileNotFoundError(
            f"HippoRAG index directory not found: {index_dir}"
        )

    query_dir = index_dir / ".adapter_runtime"
    query_dir.mkdir(parents=True, exist_ok=True)

    _write_config(config, index_dir)

    query_path = query_dir / "query.json"
    query_path.write_text(
        json.dumps({"query": query, "k": k}, ensure_ascii=False),
        encoding="utf-8",
    )

    mounts = {
        index_dir: "/workspace/results",
    }

    script = r"""
import json
from pathlib import Path

from hipporag import HippoRAG
from hipporag.utils.config_utils import BaseConfig

output_dir = Path("/workspace/results")
config_path = output_dir / "hipporag.config.json"
query_path = output_dir / ".adapter_runtime" / "query.json"

cfg = json.loads(config_path.read_text(encoding="utf-8"))
request = json.loads(query_path.read_text(encoding="utf-8"))

hippo_config = BaseConfig(
    llm_name=cfg["llm_name"],
    llm_base_url=cfg.get("llm_base_url"),
    embedding_provider=cfg.get("embedding_provider", "openai"),
    embedding_model_name=cfg["embedding_model_name"],
    embedding_base_url=cfg.get("embedding_base_url"),
    save_dir=str(output_dir),
)

rag = HippoRAG(
    global_config=hippo_config,
    save_dir=str(output_dir),
)

# Never pass gold_docs. That would leak evaluator information.
solutions = rag.retrieve(
    [request["query"]],
    num_to_retrieve=request["k"],
)

if not solutions:
    raise RuntimeError("HippoRAG returned no QuerySolution.")

solution = solutions[0]

print(
    "HIPPO_RETRIEVAL_DEBUG:",
    {
        "doc_metadata_type": type(solution.doc_metadata).__name__,
        "doc_scores_type": type(solution.doc_scores).__name__,
        "num_docs": len(solution.doc_metadata)
        if solution.doc_metadata is not None
        else 0,
    },
)
metadata_raw = solution.doc_metadata
scores_raw = solution.doc_scores

if metadata_raw is None:
    metadata = []
else:
    metadata = list(metadata_raw)

if scores_raw is None:
    scores = []
else:
    scores = list(scores_raw)

evidence = []

for rank, md in enumerate(metadata, start=1):
    item = dict(md) if isinstance(md, dict) else {}

    event_id = item.get("event_id") or item.get("source_id")
    if not event_id:
        raise RuntimeError(
            "HippoRAG returned retrieval metadata without canonical "
            f"event_id/source_id at rank {rank}: {item!r}"
        )

    score = None
    if rank - 1 < len(scores):
        try:
            score = float(scores[rank - 1])
        except (TypeError, ValueError):
            pass

    evidence.append(
        {
            "event_id": event_id,
            "rank": rank,
            "score": score,
        }
    )

result = {
    "condition": "hipporag2",
    "query": request["query"],
    "k": request["k"],
    "evidence": evidence,
    "status": "PASS",
    "qa_answer": None,
}

print(json.dumps(result, ensure_ascii=False, sort_keys=True))
"""

    stdout = _run_container(
        "hipporag2",
        script,
        mounts=mounts,
    )

    result_obj: dict[str, Any] | None = None

    for line in reversed(stdout.splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            candidate = json.loads(line)
        except json.JSONDecodeError:
            continue
        if (
            isinstance(candidate, dict)
            and candidate.get("condition") == COMPETITOR
        ):
            result_obj = candidate
            break

    if result_obj is None:
        raise RuntimeError(
            "HippoRAG retrieval completed without a normalized retrieval "
            f"result. Raw stdout:\n{stdout}"
        )

    return result_obj
