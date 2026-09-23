# V7.7.1 Competitor Setup Bundle

Prepares the four missing competitors:
- Microsoft GraphRAG
- Graphiti
- HippoRAG2
- official RAPTOR (parthsarthi03/raptor)

You only need to add your Gemini API key to `.env`.

This bundle does not include virtual environments, upstream repositories,
model weights, benchmark data, evaluator gold, generated indexes, or secrets.
Those are created locally by the setup script.

## Setup

    cp .env.example .env
    # edit .env and put your Gemini key

    ./scripts/setup_all.sh
    ./scripts/smoke_all.sh

All commands use `python3`, `python3.10`, or `python3.11`, never `python`.

## Python isolation

- GraphRAG: Python 3.11/3.12 preferred, within upstream 3.10-3.12 support.
- Graphiti: Python 3.11 preferred.
- HippoRAG2: Python 3.10.
- RAPTOR: Python 3.10 because its upstream dependency pins are old.

## Gemini

Gemini is used as the hosted LLM layer. Google documents the OpenAI-compatible
endpoint at https://generativelanguage.googleapis.com/v1beta/openai/.

Some upstream packages expect OPENAI_API_KEY or GOOGLE_API_KEY as variable names.
Those are compatibility aliases containing the same Gemini key. Requests still go
to Google's Gemini endpoint.

## Graphiti

Neo4j is the only service started in Docker. Gemini remains on the host.

## RAPTOR

The official parthsarthi03/raptor repository is used. The setup script does not
substitute another project called RAPTOR.

## Important

Successful package installation/import is only an environment smoke test.
It does not mean the V7.7.1 benchmark adapter is READY. The actual benchmark
must still pass the canonical-ID mapping and clean-room checks.
