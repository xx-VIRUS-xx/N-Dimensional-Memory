#!/usr/bin/env python3
"""Run one stateless Claude Code extraction process per corpus event."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, 1):
            if not line.strip():
                continue
            obj = json.loads(line)
            if not isinstance(obj, dict):
                raise ValueError(f"Expected object at {path}:{line_no}")
            rows.append(obj)
    return rows

def parse_json_response(text: str) -> dict[str, Any]:
    value = text.strip()
    if value.startswith("```"):
        lines = value.splitlines()
        lines = lines[1:] if lines and lines[0].startswith("```") else lines
        lines = lines[:-1] if lines and lines[-1].strip() == "```" else lines
        value = "\n".join(lines).strip()
        if value.lower().startswith("json"):
            value = value[4:].lstrip()
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        start = value.find("{")
        end = value.rfind("}")
        if start < 0 or end <= start:
            raise ValueError("Claude response did not contain a JSON object")
        parsed = json.loads(value[start : end + 1])
    if not isinstance(parsed, dict):
        raise ValueError("Claude response must be a JSON object")
    if not isinstance(parsed.get("entities"), list):
        raise ValueError("Claude JSON must contain an entities array")
    return parsed

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def run_claude(prompt: str, model: str | None) -> subprocess.CompletedProcess[str]:
    if shutil.which("claude") is None:
        raise RuntimeError("Claude Code CLI was not found on PATH.")
    command = [
        "claude", "-p", "--bare", "--no-session-persistence",
        "--tools", "", "--max-turns", "1",
    ]
    if model:
        command.extend(["--model", model])
    command.append(prompt)
    env = os.environ.copy()
    env["CLAUDE_CODE_SKIP_PROMPT_HISTORY"] = "1"
    return subprocess.run(command, text=True, capture_output=True, env=env, check=False)

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=Path(__file__).parents[1] / "corpus" / "raw_events.jsonl")
    parser.add_argument("--prompt", type=Path, default=Path(__file__).with_name("prompt.md"))
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("entity_dimensions.jsonl"))
    parser.add_argument("--log", type=Path, default=Path(__file__).with_name("extraction_log.jsonl"))
    parser.add_argument("--raw-dir", type=Path, default=Path(__file__).with_name("raw_responses"))
    parser.add_argument("--model", default=None)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    if args.output.exists() and not args.overwrite:
        raise SystemExit(f"{args.output} already exists. Use --overwrite to regenerate.")

    events = load_jsonl(args.corpus)
    template = args.prompt.read_text(encoding="utf-8")
    for index, event in enumerate(events):
        if not isinstance(event.get("event_id"), str):
            raise SystemExit(f"Event row {index + 1} has no string event_id.")
        if not isinstance(event.get("text"), str):
            raise SystemExit("Event has no string text: " + str(event.get("event_id")))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.log.parent.mkdir(parents=True, exist_ok=True)
    args.raw_dir.mkdir(parents=True, exist_ok=True)
    if args.overwrite:
        args.output.unlink(missing_ok=True)
        args.log.unlink(missing_ok=True)

    with args.output.open("a", encoding="utf-8") as output_fh, args.log.open("a", encoding="utf-8") as log_fh:
        for index, event in enumerate(events):
            event_id = event["event_id"]
            prompt = template.replace("{{EVENT}}", event["text"])
            log: dict[str, Any] = {
                "event_id": event_id,
                "event_index": index,
                "started_at": now(),
                "model": args.model or "configured-default",
                "input_hash": digest(prompt),
                "memory_isolation": {
                    "bare": True,
                    "no_session_persistence": True,
                    "skip_prompt_history": True,
                    "tools_disabled": True,
                    "max_turns": 1,
                },
            }
            print(f"[{index + 1}/{len(events)}] {event_id}: fresh Claude process", flush=True)
            result = run_claude(prompt, args.model)
            raw_path = args.raw_dir / f"{event_id}.txt"
            raw_path.write_text(result.stdout, encoding="utf-8")
            log["completed_at"] = now()
            log["return_code"] = result.returncode
            log["raw_response_hash"] = digest(result.stdout)
            if result.returncode != 0:
                log["status"] = "error"
                log["stderr"] = result.stderr[-4000:]
                log_fh.write(json.dumps(log, ensure_ascii=False) + "\n")
                log_fh.flush()
                raise RuntimeError(f"Claude failed for {event_id}: {result.stderr.strip()}")
            try:
                parsed = parse_json_response(result.stdout)
            except Exception as exc:
                log["status"] = "invalid_json"
                log["parse_error"] = str(exc)
                log_fh.write(json.dumps(log, ensure_ascii=False) + "\n")
                log_fh.flush()
                raise RuntimeError(f"Invalid Claude JSON for {event_id}: {exc}") from exc
            output_fh.write(json.dumps({"event_id": event_id, "entities": parsed["entities"]}, ensure_ascii=False) + "\n")
            output_fh.flush()
            log["status"] = "success"
            log["entity_count"] = len(parsed["entities"])
            log_fh.write(json.dumps(log, ensure_ascii=False) + "\n")
            log_fh.flush()
    print(f"Completed {len(events)} independent extractions.")
    print(f"Results: {args.output}")
    print(f"Logs: {args.log}")
    print(f"Raw responses: {args.raw_dir}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
