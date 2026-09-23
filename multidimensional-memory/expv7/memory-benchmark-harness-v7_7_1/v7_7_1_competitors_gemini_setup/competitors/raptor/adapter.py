from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any


COMPETITOR = "raptor"


def _compose_file() -> Path:
    return Path(
        os.getenv(
            "V771_LEGACY_COMPOSE",
            "v7_7_1_competitors_gemini_setup/"
            "docker/legacy-baselines.compose.yml",
        )
    ).resolve()


def _run_container(
    script: str,
    *,
    mounts: dict[Path, str],
) -> str:

    compose_file = _compose_file()

    cmd = [
        "docker",
        "compose",
        "-f",
        str(compose_file),
        "run",
        "--rm",
    ]

    for host, container in mounts.items():
        cmd.extend(
            [
                "-v",
                f"{host}:{container}",
            ]
        )

    cmd.extend(
        [
            "raptor",
            "python",
            "-c",
            script,
        ]
    )

    result = subprocess.run(
        cmd,
        text=True,
        capture_output=True,
        check=True,
    )

    return result.stdout


def build(
    corpus_path: str | Path,
    output_dir: str | Path,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:

    corpus_path = Path(corpus_path).resolve()
    output_dir = Path(output_dir).resolve()

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    mounts = {
        corpus_path.parent: "/workspace/input",
        output_dir: "/workspace/results",
    }

    script = r"""
import json
import os
from pathlib import Path

from raptor import RetrievalAugmentation
from raptor import RetrievalAugmentationConfig


corpus_path = Path("/workspace/input") / os.environ["CORPUS_FILE"]
output_dir = Path("/workspace/results")

with corpus_path.open("r", encoding="utf-8") as f:
    events = json.load(f)

documents = [
    event["text"]
    for event in events
]

# RAPTOR supports custom summarization, QA and embedding
# implementations through its Base*Model interfaces.
#
# Gemini implementations must be supplied here before the
# benchmark is considered runnable.

raise RuntimeError(
    "RAPTOR container is installed, but the Gemini model "
    "adapters and canonical event-ID preservation are not "
    "yet wired into the upstream implementation."
)
"""

    env = os.environ.copy()
    env["CORPUS_FILE"] = corpus_path.name

    try:
        _run_container(
            script,
            mounts=mounts,
        )
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            "RAPTOR Docker environment is reachable, but the "
            "upstream benchmark integration is not yet wired."
        ) from exc

    return {
        "competitor": COMPETITOR,
        "status": "SUCCESS",
        "index_dir": str(output_dir),
    }


def retrieve(
    query: str,
    k: int,
    index_dir: str | Path,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:

    raise RuntimeError(
        "RAPTOR retrieval adapter is intentionally blocked until "
        "Gemini model adapters and canonical source-ID retrieval "
        "are implemented."
    )