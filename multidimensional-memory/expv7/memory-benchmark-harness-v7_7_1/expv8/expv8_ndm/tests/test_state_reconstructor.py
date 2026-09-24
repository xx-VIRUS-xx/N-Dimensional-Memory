from __future__ import annotations

import json
from pathlib import Path

from ndm.state_reconstructor import ReconstructedState


ROOT = Path(__file__).resolve().parents[1]

MEMORY_PATH = (
    ROOT
    / "results"
    / "ndm"
    / "adversarial_01"
    / "memory.json"
)


def load_memory():
    with MEMORY_PATH.open(
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


def test_memory_loads():
    memory = load_memory()

    state = ReconstructedState(memory)

    assert len(state.entities) == 6
    assert len(state.propositions) == 5
    assert len(state.events) == 5


def test_current_state_excludes_superseded_postgresql():
    memory = load_memory()

    state = ReconstructedState(memory)

    current = state.current_propositions()

    current_ids = {
        proposition["id"]
        for proposition in current
    }

    assert "PROP_001" not in current_ids
    assert "PROP_003" in current_ids


def test_supersession_chain():
    memory = load_memory()

    state = ReconstructedState(memory)

    history = state.proposition_history(
        "PROP_001"
    )

    history_ids = {
        proposition["id"]
        for proposition in history
    }

    assert "PROP_001" in history_ids
    assert "PROP_003" in history_ids


def test_alice_historical_belief():
    memory = load_memory()

    state = ReconstructedState(memory)

    beliefs = state.beliefs_for_proposition(
        "PROP_001"
    )

    assert len(beliefs) >= 1

    assert any(
        belief.get("state") == "confirmed"
        for belief in beliefs
    )


def test_bob_belief_is_preserved():
    memory = load_memory()

    state = ReconstructedState(memory)

    beliefs = state.beliefs_for_proposition(
        "PROP_004"
    )

    assert len(beliefs) == 1

    belief = beliefs[0]

    assert belief.get("holder") == "ENT_BOB"
    assert belief.get("state") == "confirmed"


def test_mongodb_negative_knowledge_preserved():
    memory = load_memory()

    state = ReconstructedState(memory)

    negatives = state.negative_knowledge

    assert len(negatives) >= 1

    assert any(
        "MongoDB" in str(item)
        for item in negatives
    )


def test_temporal_order_is_preserved():
    memory = load_memory()

    state = ReconstructedState(memory)

    timestamps = [
        state.events[event_id].get("timestamp")
        for event_id in [
            "E001",
            "E002",
            "E003",
            "E004",
            "E005",
        ]
    ]

    assert timestamps == sorted(timestamps)


def test_no_false_contradiction_relationship():
    memory = load_memory()

    state = ReconstructedState(memory)

    contradictions = [
        relation
        for relation in state.relationships
        if relation.get("type") == "contradicts"
    ]

    assert contradictions == []


def test_supersession_relationship_exists():
    memory = load_memory()

    state = ReconstructedState(memory)

    supersedes = [
        relation
        for relation in state.relationships
        if relation.get("type") == "supersedes"
    ]

    assert any(
        relation.get("source") == "PROP_003"
        and relation.get("target") == "PROP_001"
        for relation in supersedes
    )


def test_current_packet_prefers_dynamodb():
    memory = load_memory()

    state = ReconstructedState(memory)

    packet = state.build_packet(
        proposition_ids=[
            "PROP_001",
            "PROP_003",
        ],
        event_ids=[
            "E001",
            "E003",
        ],
        include_history=False,
    )

    proposition_ids = {
        proposition["id"]
        for proposition in packet["propositions"]
    }

    assert "PROP_003" in proposition_ids
    assert "PROP_001" not in proposition_ids


def test_historical_packet_contains_both_states():
    memory = load_memory()

    state = ReconstructedState(memory)

    packet = state.build_packet(
        proposition_ids=[
            "PROP_001",
        ],
        event_ids=[
            "E001",
            "E003",
        ],
        include_history=True,
    )

    proposition_ids = {
        proposition["id"]
        for proposition in packet["propositions"]
    }

    assert "PROP_001" in proposition_ids
    assert "PROP_003" in proposition_ids