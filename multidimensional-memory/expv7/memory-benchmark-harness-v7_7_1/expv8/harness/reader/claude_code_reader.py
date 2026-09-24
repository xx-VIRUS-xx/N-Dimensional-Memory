import json
import os
import subprocess
import time
from pathlib import Path


CLAUDE_BIN = os.getenv("CLAUDE_BIN", "claude")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "sonnet")
CLAUDE_TIMEOUT = int(
    os.getenv("CLAUDE_TIMEOUT", "300")
)


class ClaudeCodeReader:
    """
    Thin adapter around Claude Code's non-interactive mode.

    The adapter deliberately does not know anything about:
    RAW, BM25, Dense, Hybrid, NDM, etc.

    It only receives a prompt and returns the model response.
    """

    def __init__(
        self,
        model=CLAUDE_MODEL,
        timeout=CLAUDE_TIMEOUT,
    ):
        self.model = model
        self.timeout = timeout

    def smoke_test(self):
        result = self._invoke(
            "Return exactly the single letter A."
        )

        answer = result.get("text", "").strip()

        return {
            "ok": answer.upper().startswith("A"),
            "response": answer,
            "raw": result,
        }

    def ask(self, prompt):
        return self._invoke(prompt)

    def _invoke(self, prompt):

        started = time.time()

        command = [
            CLAUDE_BIN,
            "-p",
            "--output-format",
            "json",
            "--model",
            self.model,
            "--no-session-persistence",
        ]

        try:

            process = subprocess.run(
                command,
                input=prompt,
                text=True,
                capture_output=True,
                timeout=self.timeout,
            )

        except subprocess.TimeoutExpired as exc:

            return {
                "status": "TIMEOUT",
                "text": "",
                "error": str(exc),
                "latency_ms": round(
                    (time.time() - started) * 1000,
                    2,
                ),
            }

        latency_ms = round(
            (time.time() - started) * 1000,
            2,
        )

        stdout = process.stdout.strip()
        stderr = process.stderr.strip()

        if process.returncode != 0:

            return {
                "status": "ERROR",
                "text": "",
                "error": stderr or stdout,
                "returncode": process.returncode,
                "latency_ms": latency_ms,
            }

        try:
            payload = json.loads(stdout)

        except json.JSONDecodeError:

            return {
                "status": "INVALID_JSON",
                "text": stdout,
                "error": stderr,
                "latency_ms": latency_ms,
            }

        text = payload.get(
            "result",
            "",
        )

        return {
            "status": "SUCCESS",
            "text": text,
            "session_id": payload.get(
                "session_id"
            ),
            "usage": {
                "input_tokens": payload.get(
                    "input_tokens"
                ),
                "output_tokens": payload.get(
                    "output_tokens"
                ),
                "cache_read_input_tokens": payload.get(
                    "cache_read_input_tokens"
                ),
                "cache_creation_input_tokens": payload.get(
                    "cache_creation_input_tokens"
                ),
            },
            "cost_usd": payload.get(
                "total_cost_usd"
            ),
            "latency_ms": latency_ms,
            "raw_response": payload,
        }


def normalize_answer(text):
    if not text:
        return None

    text = text.strip().upper()

    if text in {"A", "B", "C", "D"}:
        return text

    for letter in ("A", "B", "C", "D"):

        if text.startswith(f"{letter}."):
            return letter

        if text.startswith(f"{letter})"):
            return letter

        if text.startswith(f"({letter})"):
            return letter

    tokens = (
        text
        .replace(".", " ")
        .replace(")", " ")
        .split()
    )

    for token in tokens[:3]:

        if token in {"A", "B", "C", "D"}:
            return token

    return None