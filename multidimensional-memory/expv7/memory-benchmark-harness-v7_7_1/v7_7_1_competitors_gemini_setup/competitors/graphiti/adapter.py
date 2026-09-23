from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from graphiti_core import Graphiti
from graphiti_core.cross_encoder.gemini_reranker_client import GeminiRerankerClient
from graphiti_core.driver.falkordb_driver import FalkorDriver
from graphiti_core.embedder.gemini import GeminiEmbedder, GeminiEmbedderConfig
from graphiti_core.llm_client.gemini_client import GeminiClient, LLMConfig
from graphiti_core.nodes import EpisodeType

COMPETITOR = "graphiti"
DEFAULT_LLM_MODEL = "gemini-2.5-flash-lite"
DEFAULT_RERANKER_MODEL = "gemini-2.5-flash-lite"
DEFAULT_EMBEDDING_MODEL = "gemini-embedding-001"
DEFAULT_GROUP_ID = "v771-smoke"
DEFAULT_FALKORDB_HOST = "localhost"
DEFAULT_FALKORDB_PORT = 6379
DEFAULT_FALKORDB_DATABASE = "v771_graphiti"


def _config() -> dict[str, Any]:
    return {
        "llm_model": os.getenv("GRAPHITI_LLM_MODEL", DEFAULT_LLM_MODEL),
        "reranker_model": os.getenv(
            "GRAPHITI_RERANKER_MODEL", DEFAULT_RERANKER_MODEL
        ),
        "embedding_model": os.getenv(
            "GRAPHITI_EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL
        ),
        "falkordb_host": os.getenv(
            "GRAPHITI_FALKORDB_HOST", DEFAULT_FALKORDB_HOST
        ),
        "falkordb_port": int(
            os.getenv("GRAPHITI_FALKORDB_PORT", str(DEFAULT_FALKORDB_PORT))
        ),
        "falkordb_database": os.getenv(
            "GRAPHITI_FALKORDB_DATABASE", DEFAULT_FALKORDB_DATABASE
        ),
        "group_id": os.getenv("GRAPHITI_GROUP_ID", DEFAULT_GROUP_ID),
    }


def _make_graphiti() -> Graphiti:
    api_key = os.environ["GEMINI_API_KEY"]
    cfg = _config()

    driver = FalkorDriver(
        host=cfg["falkordb_host"],
        port=cfg["falkordb_port"],
        database=cfg["falkordb_database"],
    )

    return Graphiti(
        graph_driver=driver,
        llm_client=GeminiClient(
            config=LLMConfig(
                api_key=api_key,
                model=cfg["llm_model"],
            )
        ),
        embedder=GeminiEmbedder(
            config=GeminiEmbedderConfig(
                api_key=api_key,
                embedding_model=cfg["embedding_model"],
            )
        ),
        cross_encoder=GeminiRerankerClient(
            config=LLMConfig(
                api_key=api_key,
                model=cfg["reranker_model"],
            )
        ),
    )


def _parse_reference_time(value: str) -> datetime:
    # Benchmark timestamps are ISO-8601. Normalize trailing Z for fromisoformat().
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


async def _build_async(
    corpus_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    graphiti = _make_graphiti()
    cfg = _config()
    output_dir.mkdir(parents=True, exist_ok=True)

    provenance: dict[str, str] = {}
    event_count = 0

    try:
        await graphiti.build_indices_and_constraints()

        with corpus_path.open("r", encoding="utf-8") as f:
            corpus = json.load(f)

        for event in corpus:
            event_id = event["event_id"]

            episode_body = json.dumps(
                {
                    "event_id": event_id,
                    "conversation_id": event["conversation_id"],
                    "timestamp": event["timestamp"],
                    "text": event["text"],
                    **({"speaker": event["speaker"]} if "speaker" in event else {}),
                },
                ensure_ascii=False,
            )

            result = await graphiti.add_episode(
                name=event_id,
                episode_body=episode_body,
                source=EpisodeType.json,
                source_description="V7.7.1 benchmark event",
                reference_time=_parse_reference_time(event["timestamp"]),
                group_id=cfg["group_id"],
            )

            # Persist Graphiti's internal episode UUID -> benchmark event ID.
            provenance[result.episode.uuid] = event_id
            event_count += 1

        provenance_path = output_dir / "provenance.json"
        provenance_path.write_text(
            json.dumps(provenance, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        metadata = {
            "competitor": COMPETITOR,
            "status": "SUCCESS",
            "events_indexed": event_count,
            "graphiti_version": "0.30.2",
            "backend": "falkordb",
            "group_id": cfg["group_id"],
            "database": cfg["falkordb_database"],
            "llm_model": cfg["llm_model"],
            "embedding_model": cfg["embedding_model"],
            "reranker_model": cfg["reranker_model"],
            "provenance_file": str(provenance_path),
        }

        (output_dir / "build_metadata.json").write_text(
            json.dumps(metadata, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return metadata
    finally:
        await graphiti.close()


async def _retrieve_async(
    query: str,
    k: int,
    index_dir: Path,
) -> dict[str, Any]:
    graphiti = _make_graphiti()
    cfg = _config()

    try:
        provenance_path = index_dir / "provenance.json"
        if not provenance_path.exists():
            raise FileNotFoundError(
                f"Graphiti provenance map not found: {provenance_path}"
            )

        provenance = json.loads(
            provenance_path.read_text(encoding="utf-8")
        )

        results = await graphiti.search(
            query=query,
            group_ids=[cfg["group_id"]],
            num_results=k,
        )

        evidence: list[dict[str, Any]] = []

        for rank, result in enumerate(results, start=1):
            event_ids = [
                provenance[episode_uuid]
                for episode_uuid in (getattr(result, "episodes", None) or [])
                if episode_uuid in provenance
            ]

            # One Graphiti fact can be supported by multiple source episodes.
            # Preserve all source IDs instead of inventing a single provenance.
            for event_id in event_ids:
                evidence.append(
                    {
                        "event_id": event_id,
                        "rank": rank,
                        "score": None,
                    }
                )

        return {
            "query": query,
            "condition": COMPETITOR,
            "status": "SUCCESS",
            "evidence": evidence,
            "metadata": {
                "k": k,
                "graphiti_version": "0.30.2",
                "backend": "falkordb",
                "group_id": cfg["group_id"],
                "database": cfg["falkordb_database"],
                "llm_model": cfg["llm_model"],
                "embedding_model": cfg["embedding_model"],
                "reranker_model": cfg["reranker_model"],
            },
        }
    finally:
        await graphiti.close()


def build(
    corpus_path: str | Path,
    output_dir: str | Path,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    del config
    return asyncio.run(
        _build_async(
            Path(corpus_path).resolve(),
            Path(output_dir).resolve(),
        )
    )


def retrieve(
    query: str,
    k: int,
    index_dir: str | Path,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    del config
    return asyncio.run(
        _retrieve_async(
            query,
            k,
            Path(index_dir).resolve(),
        )
    )
