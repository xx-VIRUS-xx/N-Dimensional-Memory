import json
from pathlib import Path

from ndm.query_reconstructor import NDMQueryReconstructor
from ndm.retriever import QuerySpec


ROOT = Path(__file__).resolve().parents[1]
QUERIES_PATH = ROOT / "tests" / "data" / "adversarial_03_queries.json"


def _memory():
    def p(pid, text, scope, valid_from, entities, status="observed"):
        return {
            "id": pid,
            "text": text,
            "scope": scope,
            "valid_from": valid_from,
            "entities": entities,
            "status": status,
            "provenance": {"span": "E" + pid[1:]},
        }

    props = [
        p("P301", "Alice proposed PostgreSQL for the payments platform.", "payments platform database choice", "2026-03-01", ["ENT_ALICE_PLATFORM", "ENT_PAYMENTS", "ENT_POSTGRESQL"]),
        p("P302", "Bob argued that CockroachDB was better for multi-region payments.", "payments platform database choice", "2026-03-02", ["ENT_BOB", "ENT_PAYMENTS", "ENT_COCKROACHDB"]),
        p("P303", "Alice accepted CockroachDB after Bob's argument.", "payments platform database choice", "2026-03-03", ["ENT_ALICE_PLATFORM", "ENT_PAYMENTS", "ENT_COCKROACHDB"]),
        p("P304", "The compliance requirement ruled out CockroachDB.", "payments platform database choice", "2026-03-04", ["ENT_CAROL", "ENT_COMPLIANCE", "ENT_COCKROACHDB"]),
        p("P305", "Alice reversed the decision and selected PostgreSQL because of the compliance requirement.", "payments platform database choice", "2026-03-05", ["ENT_ALICE_PLATFORM", "ENT_PAYMENTS", "ENT_POSTGRESQL"]),
        p("P306", "The team discovered that the compliance document had been misinterpreted.", "payments platform compliance correction", "2026-03-06", ["ENT_COMPLIANCE", "ENT_COMPLIANCE_DOC"]),
        p("P307", "Alice corrected the decision and selected CockroachDB again.", "payments platform database choice", "2026-03-07", ["ENT_ALICE_PLATFORM", "ENT_PAYMENTS", "ENT_COCKROACHDB"]),
        p("P308", "Bob claimed that the original CockroachDB decision had always been the intended architecture.", "payments platform architecture belief", "2026-03-08", ["ENT_BOB", "ENT_COCKROACHDB", "ENT_PAYMENTS"]),
        p("P309", "Alice explicitly rejected Bob's interpretation and said CockroachDB was not the original decision.", "payments platform architecture belief", "2026-03-09", ["ENT_ALICE_PLATFORM", "ENT_BOB", "ENT_COCKROACHDB"]),
        p("P310", "Another Alice from the security team discussed a security architecture unrelated to payments.", "security architecture", "2026-03-10", ["ENT_ALICE_SECURITY", "ENT_SECURITY"]),
        p("P311", "The payments Alice clarified that she was Alice from the platform team.", "payments platform identity", "2026-03-11", ["ENT_ALICE_PLATFORM", "ENT_ALICE_SECURITY"]),
        p("P312", "The payments platform deployment completed successfully.", "payments platform deployment", "2026-03-12", ["ENT_PAYMENTS", "ENT_DEPLOYMENT"]),
        p("P313", "Alice stated that deployment happened after the migration work and did not cause the architectural decision.", "payments platform deployment", "2026-03-13", ["ENT_ALICE_PLATFORM", "ENT_MIGRATION", "ENT_PAYMENTS"]),
    ]

    events = [
        {"id": "E" + x["id"][1:], "text": x["text"], "timestamp": x["valid_from"], "participants": x["entities"]}
        for x in props
    ]

    relationships = [
        {"type": "supports", "source": "P302", "target": "P303"},
        {"type": "supersedes", "source": "P303", "target": "P301"},
        {"type": "caused", "source": "P304", "target": "P305"},
        {"type": "supersedes", "source": "P305", "target": "P303"},
        {"type": "corrects", "source": "P306", "target": "P304"},
        {"type": "corrects", "source": "P306", "target": "P305"},
        {"type": "supersedes", "source": "P307", "target": "P305"},
        {"type": "contradicts", "source": "P309", "target": "P308"},
        {"type": "follows", "source": "P312", "target": "P313"}
    ]

    beliefs = [
        {"id": "BELIEF_301", "holder": "ENT_BOB", "proposition_id": "P308", "state": "confirmed"},
        {"id": "BELIEF_302", "holder": "ENT_ALICE_PLATFORM", "proposition_id": "P309", "state": "confirmed"}
    ]

    ambiguities = [
        {
            "id": "AMB301",
            "mention": "Alice",
            "candidate_set": ["ENT_ALICE_PLATFORM", "ENT_ALICE_SECURITY"],
            "resolved_by": "P311",
            "resolution": "Alice in the payments context is the platform-team Alice."
        }
    ]

    negative = [
        {
            "id": "NK301",
            "text": "Deployment did not cause the architectural decision; deployment only followed the migration work.",
            "related_propositions": ["P312", "P313"]
        }
    ]

    return {
        "source": "adversarial_03",
        "entities": [],
        "propositions": props,
        "events": events,
        "relationships": relationships,
        "beliefs": beliefs,
        "ambiguities": ambiguities,
        "negative_knowledge": negative,
    }


with open(QUERIES_PATH, "r", encoding="utf-8") as f:
    QUERIES = json.load(f)


def test_adv03_query_contract():
    resolver = NDMQueryReconstructor(_memory())
    for query in QUERIES:
        spec = QuerySpec(
            query_id=query["query_id"],
            question=query["question"],
            mode=query["mode"],
            subject=query.get("subject"),
            scope=query.get("scope"),
        )
        result = resolver.resolve(spec)
        assert result["selected_event_ids"] == query["expected_evidence"], query["query_id"]


def test_adv03_dimensions_are_present():
    memory = _memory()
    assert len(memory["relationships"]) >= 1
    assert len(memory["beliefs"]) == 2
    assert len(memory["ambiguities"]) == 1
    assert len(memory["negative_knowledge"]) == 1
