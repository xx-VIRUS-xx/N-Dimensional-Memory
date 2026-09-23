#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
set -a
source .env
set +a
mkdir -p results/setup

echo "== Gemini API =="
curl -fsS "${GEMINI_BASE_URL}models" \
  -H "Authorization: Bearer ${GEMINI_API_KEY}" \
  > results/setup/gemini_models.json
echo "Gemini API: PASS"

echo "== GraphRAG =="
source competitors/graphrag/.venv/bin/activate
python3 -c "import graphrag; print('GraphRAG import: PASS')"
deactivate

echo "== Graphiti =="
source competitors/graphiti/.venv/bin/activate
python3 -c "import graphiti_core; print('Graphiti import: PASS')"
deactivate


echo "== Neo4j =="
docker compose -f docker/graphiti/docker-compose.yml ps
echo "Basic smoke tests passed."
