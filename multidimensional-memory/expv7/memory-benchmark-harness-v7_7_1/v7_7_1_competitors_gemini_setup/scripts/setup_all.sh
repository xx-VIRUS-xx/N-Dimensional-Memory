#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [ ! -f .env ]; then
  echo "ERROR: .env missing. Run: cp .env.example .env"
  exit 2
fi
set -a
source .env
set +a
if [ -z "${GEMINI_API_KEY:-}" ] || [ "$GEMINI_API_KEY" = "PUT_YOUR_GEMINI_API_KEY_HERE" ]; then
  echo "ERROR: add GEMINI_API_KEY to .env"
  exit 2
fi

command -v python3 >/dev/null || { echo "ERROR: python3 missing"; exit 3; }
command -v git >/dev/null || { echo "ERROR: git missing"; exit 3; }
command -v docker >/dev/null || { echo "ERROR: docker missing"; exit 3; }

pick() {
  for c in "$@"; do
    if command -v "$c" >/dev/null 2>&1; then
      echo "$c"
      return 0
    fi
  done
  return 1
}
PY311="$(pick python3.11 python3.12 python3.10 || true)"
PY310="$(pick python3.10 || true)"
[ -n "$PY311" ] || { echo "ERROR: Python 3.11/3.12/3.10 required."; exit 4; }


mkdir -p results/setup

echo "== GraphRAG =="
mkdir -p competitors/graphrag
[ -d competitors/graphrag/.venv ] || "$PY311" -m venv competitors/graphrag/.venv
source competitors/graphrag/.venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install graphrag
deactivate

echo "== Graphiti =="
mkdir -p competitors/graphiti
[ -d competitors/graphiti/.venv ] || "$PY311" -m venv competitors/graphiti/.venv
source competitors/graphiti/.venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install "graphiti-core[google-genai]"
deactivate
docker compose -f docker/graphiti/docker-compose.yml up -d


echo "== RAPTOR =="
mkdir -p competitors/raptor
[ -d competitors/raptor/upstream ] || git clone https://github.com/parthsarthi03/raptor.git competitors/raptor/upstream
[ -d competitors/raptor/.venv ] || "$PY311" -m venv competitors/raptor/.venv
source competitors/raptor/.venv/bin/activate
python3 -m pip install --upgrade pip setuptools wheel
cd competitors/raptor/upstream
python3 -m pip install -r requirements.txt
python3 -m pip install -e .
cd "$ROOT"
deactivate

cat > results/setup/environment.txt <<EOF
timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
graphrag_env=competitors/graphrag/.venv
graphiti_env=competitors/graphiti/.venv
hipporag2_env=competitors/hipporag2/.venv
raptor_env=competitors/raptor/.venv
neo4j=neo4j:5.26.2
gemini_base_url=${GEMINI_BASE_URL}
gemini_model=${GEMINI_MODEL}
embedding_model=${EMBEDDING_MODEL}
EOF

echo "SETUP COMPLETE. Run ./scripts/smoke_all.sh"
