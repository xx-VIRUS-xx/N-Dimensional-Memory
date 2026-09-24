from __future__ import annotations
import json, os, re, subprocess, time
from typing import Any

class ClaudeCodeReader:
    def __init__(self, model: str = "sonnet"):
        self.model = model

    def ask(self, prompt: str) -> dict[str, Any]:
        cmd = ["claude", "-p", "--output-format", "json", "--model", self.model, "--no-session-persistence"]
        started = time.perf_counter()
        proc = subprocess.run(cmd, input=prompt, text=True, capture_output=True)
        latency = (time.perf_counter() - started) * 1000
        raw: dict[str, Any] = {}
        try:
            raw = json.loads(proc.stdout)
        except Exception:
            raw = {"stdout": proc.stdout, "stderr": proc.stderr}
        usage = raw.get("usage", {}) if isinstance(raw, dict) else {}
        model_usage = raw.get("modelUsage", {}) if isinstance(raw, dict) else {}
        actual_models = list(model_usage.keys()) if isinstance(model_usage, dict) else []
        actual_model = actual_models[0] if actual_models else None
        if proc.returncode != 0 or raw.get("is_error"):
            msg = raw.get("result") or raw.get("error") or proc.stderr.strip() or "claude process failed"
            text = str(msg)
            low = text.lower()
            status = "CONTEXT_LIMIT" if any(x in low for x in ["context window", "too many tokens", "maximum context", "prompt is too long"]) else ("RATE_LIMIT" if any(x in low for x in ["rate limit", "429", "too many requests"]) else "ERROR")
            return {"status": status, "text": "", "raw_response": raw, "error": text, "latency_ms": latency, "actual_model": actual_model}
        return {
            "status": "SUCCESS", "text": str(raw.get("result", "")), "raw_response": raw,
            "latency_ms": latency, "actual_model": actual_model,
            "estimated_cost_usd": raw.get("total_cost_usd"),
            "usage": usage, "model_usage": model_usage,
            "session_id": raw.get("session_id"),
        }


def extract_choice(text: str) -> str | None:
    matches = re.findall(r"(?:^|\n|\s)(?:answer\s*[:=-]\s*)?\*{0,2}([ABCD])\*{0,2}(?:\s*$|[.\)\s])", text.strip(), re.I)
    if not matches:
        return None
    return matches[-1].upper()
