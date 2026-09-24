from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .schema import save_memory, validate_memory
from .writer_prompt import build_writer_prompt
from harness.claude_code_reader import ClaudeCodeReader


def parse_json_response(raw_text: str) -> dict[str, Any]:
    """
    Parse JSON returned by the LLM.

    Accepts:
      - plain JSON
      - ```json ... ```
      - ``` ... ```
      - JSON surrounded by incidental prose
    """
    text = raw_text.strip()

    # Remove Markdown code fence.
    if text.startswith("```"):
        lines = text.splitlines()

        # Remove opening ``` or ```json
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]

        # Remove closing ```
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

    # If the model added prose before the JSON object,
    # start at the first object delimiter.
    if not text.startswith("{"):
        start = text.find("{")
        if start >= 0:
            text = text[start:]

    # If incidental text follows the JSON object,
    # stop at the final closing brace.
    if not text.endswith("}"):
        end = text.rfind("}")
        if end >= 0:
            text = text[: end + 1]

    return json.loads(text)


class NDMAdapter:
    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

        self.writer_model = self.config.get(
            "writer_model",
            "sonnet",
        )

        self.reader = ClaudeCodeReader(self.writer_model)

    def build_one(
        self,
        source_id: str,
        context: str,
        output_dir: Path,
        conversation_id: str | None = None,
    ) -> dict[str, Any]:

        output_dir.mkdir(parents=True, exist_ok=True)

        prompt = build_writer_prompt(
            source_id,
            context,
        )

        result = self.reader.ask(prompt)

        if result.get("status") != "SUCCESS":
            return {
                "source_id": source_id,
                "status": "ERROR",
                "latency_ms": result.get("latency_ms"),
                "estimated_cost_usd": result.get("cost_usd"),
                "actual_model": result.get("actual_model"),
                "usage": result.get("usage"),
                "model_usage": result.get("model_usage"),
                "error": result.get("error")
                or "Claude reader returned non-success status",
                "memory_path": None,
            }

        raw_text = result.get("text", "")

        try:
            memory = parse_json_response(raw_text)
        except Exception as exc:
            return {
                "source_id": source_id,
                "status": "WRITER_SCHEMA_ERROR",
                "error": str(exc),
                "raw_text": raw_text,
                "latency_ms": result.get("latency_ms"),
                "estimated_cost_usd": result.get("cost_usd"),
                "actual_model": result.get("actual_model"),
                "usage": result.get("usage"),
                "model_usage": result.get("model_usage"),
            }

        # Ensure core source metadata is present.
        memory.setdefault("schema_version", "ndm-v0.1")
        memory.setdefault("source", {})
        memory["source"].setdefault("source_id", source_id)

        if conversation_id is not None:
            memory["source"].setdefault(
                "conversation_id",
                conversation_id,
            )

        errors = validate_memory(memory)

        if errors:
            return {
                "source_id": source_id,
                "status": "WRITER_SCHEMA_ERROR",
                "error": "Memory validation failed",
                "validation_errors": errors,
                "memory": memory,
                "latency_ms": result.get("latency_ms"),
                "estimated_cost_usd": result.get("cost_usd"),
                "actual_model": result.get("actual_model"),
                "usage": result.get("usage"),
                "model_usage": result.get("model_usage"),
            }

        memory_path = output_dir / "memory.json"

        save_memory(
            memory_path,
            memory,
        )

        return {
            "source_id": source_id,
            "status": "SUCCESS",
            "latency_ms": result.get("latency_ms"),
            "estimated_cost_usd": result.get("cost_usd"),
            "actual_model": result.get("actual_model"),
            "usage": result.get("usage"),
            "model_usage": result.get("model_usage"),
            "memory_path": str(memory_path),
            "record_counts": {
                "entities": len(memory.get("entities", [])),
                "propositions": len(memory.get("propositions", [])),
                "events": len(memory.get("events", [])),
                "relationships": len(memory.get("relationships", [])),
                "ambiguities": len(memory.get("ambiguities", [])),
                "beliefs": len(memory.get("beliefs", [])),
                "negative_knowledge": len(
                    memory.get("negative_knowledge", [])
                ),
            },
        }

    def retrieve(
        self,
        query: str,
        memory_path: str | Path,
        k: int = 12,
    ) -> dict[str, Any]:

        from .schema import load_memory
        from .retriever import retrieve, pack

        memory = load_memory(memory_path)

        evidence = retrieve(
            memory,
            query,
            k=k,
        )

        return {
            "query": query,
            "k": k,
            "evidence": evidence,
            "packed_context": pack(
                memory,
                evidence,
            ),
        }