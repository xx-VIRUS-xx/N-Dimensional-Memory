import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from memory_v6 import AgentObservation, merge_observations


def test_same_proposition_merges_across_agents_without_losing_observations():
    obs = [
        AgentObservation("a", "claude", "p", "Rahul plays football", "resolved", 1.0, "c1"),
        AgentObservation("b", "codex", "p", "Rahul plays football", "resolved", 0.9, "c1"),
    ]
    memories = merge_observations(obs)
    assert len(memories) == 1
    assert len(memories[0].observations) == 2
    assert memories[0].agents() == {"claude", "codex"}


def test_interpretation_disagreement_does_not_create_value_conflict():
    obs = [
        AgentObservation("a", "claude", "p", "Rahul plays football", "He=Rahul", 1.0, "c1"),
        AgentObservation("b", "copilot", "p", "Rahul plays football", "He=ambiguous", 0.6, "c1"),
    ]
    memory = merge_observations(obs)[0]
    assert memory.state == "supported"
    assert len(memory.interpretations()) == 2


def test_opposing_values_remain_disputed():
    obs = [
        AgentObservation("a", "claude", "Rahul.location", "Jaipur", "asserted", 0.8, "c1", "2025-01", "2026-05"),
        AgentObservation("b", "codex", "Rahul.location", "Delhi", "asserted", 1.0, "c2", "2026-06", None),
    ]
    memory = merge_observations(obs)[0]
    assert memory.state == "disputed"
    assert len(memory.observations) == 2
