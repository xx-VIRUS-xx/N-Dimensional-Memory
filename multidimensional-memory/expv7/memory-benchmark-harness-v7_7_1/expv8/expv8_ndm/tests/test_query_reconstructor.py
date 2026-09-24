import pytest

from ndm.query_reconstructor import NDMQueryReconstructor
from ndm.retriever import QuerySpec


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
        p("P101", "Alice decided billing should use PostgreSQL.", "billing service technology choice", "2026-02-01", ["ENT_ALICE", "ENT_BILLING", "ENT_POSTGRESQL"]),
        p("P102", "PostgreSQL was becoming too expensive to operate.", "billing service technology choice", "2026-02-02", ["ENT_ALICE", "ENT_POSTGRESQL"]),
        p("P103", "Alice switched billing to DynamoDB because of operating cost.", "billing service technology choice", "2026-02-03", ["ENT_ALICE", "ENT_BILLING", "ENT_DYNAMODB"]),
        p("P104", "Bob believed PostgreSQL was still better for analytics workloads.", "analytics pipeline", "2026-02-04", ["ENT_BOB", "ENT_POSTGRESQL"]),
        p("P105", "Alice temporarily used Redis for a caching layer in billing.", "billing service technology choice", "2026-02-05", ["ENT_ALICE", "ENT_BILLING", "ENT_REDIS"]),
        p("P106", "Alice decided billing should use CockroachDB instead of DynamoDB.", "billing service technology choice", "2026-02-06", ["ENT_ALICE", "ENT_BILLING", "ENT_COCKROACH"]),
        p("P107", "The analytics pipeline continued using PostgreSQL.", "analytics pipeline", "2026-02-07", ["ENT_POSTGRESQL", "ENT_ANALYTICS"]),
        p("P108", "Alice explicitly rejected MongoDB for billing.", "billing service technology choice", "2026-02-08", ["ENT_ALICE", "ENT_BILLING", "ENT_MONGODB"], "rejected"),
        p("P109", "Alice reconsidered MongoDB after a new compliance requirement.", "billing service technology choice", "2026-02-09", ["ENT_ALICE", "ENT_BILLING", "ENT_MONGODB"]),
        p("P110", "Alice decided to use MongoDB for billing after compliance review.", "billing service technology choice", "2026-02-10", ["ENT_ALICE", "ENT_BILLING", "ENT_MONGODB"]),
        p("P111", "The reporting team was considering Cassandra and DynamoDB, but no decision had been made.", "reporting service database choice", "2026-02-11", ["ENT_CAROL", "ENT_REPORTING"]),
        p("P112", "The reporting team discussed Cassandra again, but still had not selected a database.", "reporting service database choice", "2026-02-12", ["ENT_REPORTING", "ENT_CASSANDRA"]),
        p("P113", "The billing service deployment completed successfully.", "billing service migration and deployment", "2026-02-13", ["ENT_BILLING", "ENT_DEPLOYMENT"]),
        p("P114", "Alice said deployment completed after migration work, but did not say deployment caused migration.", "billing service migration and deployment", "2026-02-14", ["ENT_ALICE", "ENT_BILLING", "ENT_MIGRATION"]),
        p("P115", "Alex approved the reporting architecture.", "reporting architecture", "2026-02-15", ["ENT_ALEX_PLATFORM", "ENT_REPORTING_ARCH"]),
        p("P116", "Another Alex from analytics rejected the reporting architecture.", "reporting architecture", "2026-02-16", ["ENT_ALEX_ANALYTICS", "ENT_REPORTING_ARCH"]),
        p("P117", "The first Alex clarified that they were Alex from the platform team.", "reporting architecture", "2026-02-17", ["ENT_ALEX_PLATFORM", "ENT_ALEX_ANALYTICS"]),
    ]

    events = [
        {"id": "E" + x["id"][1:], "text": x["text"], "participants": x["entities"]}
        for x in props
    ]

    relationships = [
        {"type": "caused", "source": "P102", "target": "P103"},
        {"type": "supersedes", "source": "P103", "target": "P101"},
        {"type": "supersedes", "source": "P106", "target": "P103"},
        {"type": "supersedes", "source": "P110", "target": "P106"},
        {"type": "supersedes", "source": "P110", "target": "P108"},
        {"type": "caused", "source": "ENT_COMPLIANCE", "target": "P109"},
        {"type": "supports", "source": "P109", "target": "P110"},
        {"type": "follows", "source": "P113", "target": "ENT_MIGRATION"},
    ]

    negative = [
        {"id": "NK4", "text": "Deployment did not cause the migration; it only followed the migration work.", "related_propositions": ["P113", "P114"]}
    ]

    return {
        "source": "adversarial_02",
        "entities": [],
        "propositions": props,
        "events": events,
        "relationships": relationships,
        "beliefs": [],
        "ambiguities": [],
        "negative_knowledge": negative,
    }


QUERIES = [
    ("Q201", "What database did Alice originally choose for the billing service?", "historical", "ENT_ALICE", "billing service technology choice", ["E101"]),
    ("Q202", "What database does the billing service currently use after all of Alice's changes?", "current", "ENT_ALICE", "billing service technology choice", ["E110"]),
    ("Q203", "How did Alice's billing-service database decision evolve over time?", "temporal", "ENT_ALICE", "billing service technology choice", ["E101", "E103", "E106", "E110"]),
    ("Q204", "Does Bob's preference for PostgreSQL mean the analytics pipeline or billing service uses PostgreSQL?", "scope", None, "billing service technology choice", ["E104", "E106", "E107"]),
    ("Q205", "What happened to Alice's rejection of MongoDB?", "lifecycle", "ENT_ALICE", "billing service technology choice", ["E108", "E109", "E110"]),
    ("Q206", "What database had the reporting team selected?", "belief", None, "reporting service database choice", ["E111", "E112"]),
    ("Q207", "Did the deployment cause the migration?", "causal", None, "billing service migration and deployment", ["E113", "E114"]),
    ("Q208", "Which Alex approved the reporting architecture?", "belief", None, "reporting architecture", ["E115", "E116", "E117"]),
]


@pytest.mark.parametrize("qid,question,mode,subject,scope,expected", QUERIES)
def test_adv02_query_contract(qid, question, mode, subject, scope, expected):
    resolver = NDMQueryReconstructor(_memory())
    spec = QuerySpec(qid, question, mode, subject, scope)
    result = resolver.resolve(spec)
    assert result["selected_event_ids"] == expected


def test_adv02_v8_actual_shape_contract():
    memory = _memory()

    scope_aliases = {
        "billing service technology choice": "billing_service",
        "billing service migration and deployment": "billing_service",
        "reporting service database choice": "reporting_service",
        "reporting architecture": "reporting_service",
        "analytics pipeline": "analytics_pipeline",
    }
    for proposition in memory["propositions"]:
        proposition["scope"] = scope_aliases[proposition["scope"]]

    memory["relationships"] = [
        {
            **{k: v for k, v in rel.items() if k not in {"source", "target"}},
            "from": rel["source"],
            "to": rel["target"],
        }
        for rel in memory["relationships"]
    ]

    resolver = NDMQueryReconstructor(memory)

    expected = {
        "Q201": ["E101"],
        "Q202": ["E110"],
        "Q203": ["E101", "E103", "E106", "E110"],
        "Q204": ["E104", "E106", "E107"],
        "Q205": ["E108", "E109", "E110"],
        "Q206": ["E111", "E112"],
        "Q207": ["E113", "E114"],
        "Q208": ["E115", "E116", "E117"],
    }

    for qid, question, mode, subject, scope, _ in QUERIES:
        spec = QuerySpec(qid, question, mode, subject, scope)
        result = resolver.resolve(spec)
        assert result["selected_event_ids"] == expected[qid]
