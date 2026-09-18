"""Minimal V7.6 artifact sanity checks.

This intentionally does not score semantic correctness. The benchmark evaluator
must compare results against a separately frozen gold annotation set.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def validate_memory(path: Path):
    obj = json.loads(path.read_text())
    assert obj.get("schema_version") == "v7.6"
    assert isinstance(obj.get("records"), list)
    ids = [r.get("id") for r in obj["records"]]
    assert all(ids)
    assert len(ids) == len(set(ids))
    for r in obj["records"]:
        assert r.get("type") in {
            "observation", "proposition", "relationship", "state_transition",
            "decision", "action_outcome", "belief_state", "ambiguity",
            "negative_knowledge", "provenance_note"
        }
        assert isinstance(r.get("source_event_ids"), list)


if __name__ == "__main__":
    for p in (ROOT / "results").glob("*.memory.json"):
        validate_memory(p)
        print(f"VALID {p.name}")
