import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from shared_memory_v61 import Observation, SharedMemory


def obs(i, agent, value, observed, **kwargs):
    return Observation(i, "rahul.location", agent, value, "inferred", observed, **kwargs)


def test_updates_append_without_overwrite():
    store = SharedMemory()
    store.append(obs("a", "A", "Jaipur", "2026-01-01"))
    store.append(obs("b", "B", "Delhi", "2026-01-02"))
    state = store.state("rahul.location")
    assert len(state["observations"]) == 2
    assert state["status"] == "disputed"


def test_provenance_survives():
    store = SharedMemory()
    store.append(obs("a", "Claude", "Jaipur", "2026-01-01"))
    store.append(obs("b", "Codex", "Delhi", "2026-01-02"))
    assert store.state("rahul.location")["agents"] == ["Claude", "Codex"]


def test_order_independence_for_disagreement():
    first = [obs("a", "A", "Jaipur", "2026-01-01"), obs("b", "B", "Delhi", "2026-01-02")]
    second = list(reversed(first))
    states = []
    for updates in (first, second):
        store = SharedMemory()
        for item in updates:
            store.append(item)
        state = store.state("rahul.location")
        states.append((state["status"], sorted(o["value"] for o in state["observations"])))
    assert states[0] == states[1] == ("disputed", ["Delhi", "Jaipur"])


def test_temporally_separated_values_are_not_disputed():
    store = SharedMemory()
    store.append(obs("a", "A", "Jaipur", "2026-01-01", valid_from="2025-01-01", valid_to="2026-05-31"))
    store.append(obs("b", "B", "Delhi", "2026-06-01", valid_from="2026-06-01"))
    assert store.state("rahul.location")["status"] == "consistent"


def test_snapshot_round_trip_preserves_history():
    store = SharedMemory()
    store.append(obs("a", "A", "Jaipur", "2026-01-01"))
    store.append(obs("b", "B", "Delhi", "2026-01-02"))
    restored = SharedMemory.from_snapshot(store.snapshot())
    assert restored.state("rahul.location") == store.state("rahul.location")
