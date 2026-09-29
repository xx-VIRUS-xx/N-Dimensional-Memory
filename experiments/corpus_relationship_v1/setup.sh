#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="python3"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Python 3 is required."
  exit 1
fi

"$PYTHON_BIN" -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt

mkdir -p outputs data

echo "NDM corpus relationship experiment is ready."
echo "Activate with: source .venv/bin/activate"
echo "Run the sample with:"
echo "  python run_pipeline.py --input sample/extracted_entity_dimensions.jsonl --output outputs/sample --top-k 5"
