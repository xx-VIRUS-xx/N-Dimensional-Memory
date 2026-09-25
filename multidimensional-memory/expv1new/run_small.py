from __future__ import annotations

import json
import subprocess
from pathlib import Path

from ndm.writer_prompt import build_prompt


ROOT = Path(__file__).resolve().parent
CORPUS = ROOT / "tests/data/small_corpus.json"
OUT = ROOT / "results/small_corpus_01/memory.json"


def ask_claude(prompt: str) -> dict:
    proc = subprocess.run(
        [
            "claude",
            "-p",
            "--output-format",
            "json",
            "--model",
            "sonnet",
            "--no-session-persistence",
        ],
        input=prompt,
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip())

    response = json.loads(proc.stdout)
    if response.get("is_error"):
        raise RuntimeError(str(response.get("result") or response))

    raw_result = response.get("result", "")
    try:
        return json.loads(raw_result)
    except json.JSONDecodeError as exc:
        # Keep the experiment strict, but preserve the exact model output so
        # protocol failures can be diagnosed without guessing or silently
        # repairing the interpretation.
        raise ValueError(
            "Claude returned a non-JSON interpretation. "
            f"JSON error: {exc}. Raw result:\n{raw_result!r}\n"
            f"stderr:\n{proc.stderr!r}"
        ) from exc


def main() -> None:
    corpus = json.loads(CORPUS.read_text())
    interpreted = []

    for event in corpus["events"]:
        record = ask_claude(build_prompt(event, interpreted))
        interpreted.append(record)

        print(
            f'{event["event_id"]}: '
            f'actors={len(record.get("actors", []))} '
            f'entities={len(record.get("entities", []))} '
            f'propositions={len(record.get("propositions", []))} '
            f'relations={len(record.get("relationships", []))} '
            f'ambiguities={len(record.get("ambiguities", []))}'
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(
            {
                "schema_version": "ndm-v1-experimental",
                "source_id": corpus["source_id"],
                "events": interpreted,
            },
            indent=2,
            ensure_ascii=False,
        )
    )

    print(f"\nWrote {OUT}")


if __name__ == "__main__":
    main()
