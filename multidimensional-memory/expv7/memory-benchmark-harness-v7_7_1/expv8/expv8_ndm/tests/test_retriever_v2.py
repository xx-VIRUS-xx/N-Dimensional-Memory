from __future__ import annotations

import json
from pathlib import Path

from ndm.retriever import NDMRetriever, QuerySpec


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


def retrieve(
    query_id,
    question,
    mode,
    subject=None,
    scope=None,
):

    retriever = NDMRetriever(
        load_memory()
    )

    return retriever.retrieve(
        QuerySpec(
            query_id=query_id,
            question=question,
            mode=mode,
            subject=subject,
            scope=scope,
        )
    )


def pids(result):
    return set(
        result[
            "selected_proposition_ids"
        ]
    )


def eids(result):
    return set(
        result[
            "selected_event_ids"
        ]
    )


def test_q001_original():

    result = retrieve(
        "Q001",
        "What database did Alice originally decide to use for the billing service?",
        "historical",
        "ENT_ALICE",
        "billing service technology choice",
    )

    assert pids(result) == {
        "PROP_001",
        
    }

    assert eids(result) == {
        "E001",
        
    }


def test_q002_current():

    result = retrieve(
        "Q002",
        "What database did Alice ultimately decide to use for the billing service?",
        "current",
        "ENT_ALICE",
        "billing service technology choice",
    )

    assert pids(result) == {
        "PROP_003"
    }

    assert eids(result) == {
        "E003"
    }


def test_q003_lifecycle():

    result = retrieve(
        "Q003",
        "What happened to Alice's original PostgreSQL decision?",
        "lifecycle",
        "ENT_ALICE",
        "billing service technology choice",
    )

    assert pids(result) == {
        "PROP_001",
        "PROP_003",
    }

    assert eids(result) == {
        "E001",
        "E003",
    }

    assert len(
        result["relationships"]
    ) == 1

    relation = result[
        "relationships"
    ][0]

    assert relation[
        "type"
    ] == "supersedes"

    assert relation[
        "source"
    ] == "PROP_003"

    assert relation[
        "target"
    ] == "PROP_001"


def test_q004_causal():

    result = retrieve(
        "Q004",
        "Why did Alice reconsider PostgreSQL?",
        "causal",
        "ENT_ALICE",
        "operating cost of PostgreSQL for billing service",
    )

    assert pids(result) == {
        "PROP_002"
    }

    assert eids(result) == {
        "E002"
    }

    assert len(
        result["relationships"]
    ) == 1

    assert result[
        "relationships"
    ][0]["type"] == "caused"


def test_q005_belief():

    result = retrieve(
        "Q005",
        "What does Bob believe about PostgreSQL?",
        "belief",
        "ENT_BOB",
        "analytics use case, as believed by Bob",
    )

    assert pids(result) == {
        "PROP_004"
    }

    assert eids(result) == {
        "E004"
    }

    assert {
        (
            belief["holder"],
            belief["proposition"],
        )
        for belief in result[
            "beliefs"
        ]
    } == {
        (
            "ENT_BOB",
            "PROP_004",
        )
    }


def test_q006_scope():

    result = retrieve(
        "Q006",
        "Does Bob's preference mean the billing service currently uses PostgreSQL?",
        "scope",
        scope="billing service technology choice",
    )

    assert pids(result) == {
        "PROP_003"
    }

    assert eids(result) == {
        "E003"
    }


def test_q007_negative():

    result = retrieve(
        "Q007",
        "Which database did Alice explicitly reject for the billing service?",
        "negative",
        "ENT_ALICE",
        "billing service technology choice",
    )

    assert pids(result) == {
        "PROP_005"
    }

    assert eids(result) == {
        "E005"
    }

    assert len(
        result[
            "negative_knowledge"
        ]
    ) == 1


def test_q008_temporal():

    result = retrieve(
        "Q008",
        "What were Alice's billing-service database decisions over time?",
        "temporal",
        "ENT_ALICE",
        "billing service technology choice",
    )

    assert pids(result) == {
    "PROP_001",
    "PROP_003",
    }

    assert eids(result) == {
        "E001",
        "E003",
    }


def test_q009_cross_scope():

    result = retrieve(
        "Q009",
        "Is Bob's belief that PostgreSQL is better for analytics a contradiction of Alice's DynamoDB decision for the billing service?",
        "contradiction",
        scope="billing service technology choice",
    )

    assert pids(result) == {
        "PROP_003",
        "PROP_004",
    }

    assert eids(result) == {
        "E003",
        "E004",
    }

    assert result[
        "relationships"
    ] == []


def test_q010_causal():

    result = retrieve(
        "Q010",
        "What caused Alice to reconsider the PostgreSQL decision?",
        "causal",
        "ENT_ALICE",
        "operating cost of PostgreSQL for billing service",
    )

    assert pids(result) == {
        "PROP_002"
    }

    assert eids(result) == {
        "E002"
    }