from __future__ import annotations
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "ndm-v0.1"


def empty_memory(source_id: str, conversation_id: str | None = None) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "source": {"source_id": source_id, "conversation_id": conversation_id, "created_at": None},
        "entities": [],
        "propositions": [],
        "events": [],
        "relationships": [],
        "ambiguities": [],
        "beliefs": [],
        "negative_knowledge": [],
    }


def validate_memory(memory: dict[str, Any]) -> list[str]:
    required = ["schema_version", "source", "entities", "propositions", "events", "relationships", "ambiguities", "beliefs", "negative_knowledge"]
    return [f"missing:{k}" for k in required if k not in memory]


def load_memory(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save_memory(path: str | Path, memory: dict[str, Any]) -> None:
    Path(path).write_text(json.dumps(memory, ensure_ascii=False, indent=2), encoding="utf-8")
