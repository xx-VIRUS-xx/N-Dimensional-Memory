from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def test_required_files_exist():
    for name in ["README.md", "EXP-V7.6.md", "AGENT_HANDOFF.md", "RUN_PROMPT.md"]:
        assert (ROOT / name).exists()


def test_schema_is_valid_json():
    data = json.loads((ROOT / "schemas/memory_v76.schema.json").read_text())
    assert data["properties"]["schema_version"]["const"] == "v7.6"
