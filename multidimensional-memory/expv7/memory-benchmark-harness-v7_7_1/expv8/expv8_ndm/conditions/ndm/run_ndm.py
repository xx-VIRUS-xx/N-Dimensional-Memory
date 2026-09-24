from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))

from ndm.adapter import NDMAdapter

# First milestone: controlled NDM writer smoke test. It intentionally does not
# consume question/gold fields. The question is only used later by retrieval.

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--source", required=True, help="JSON file containing {source_id, context[, conversation_id]}")
    p.add_argument("--output", default="results/ndm/memory")
    p.add_argument("--writer-model", default="sonnet")
    args = p.parse_args()
    src = json.loads(Path(args.source).read_text(encoding="utf-8"))
    out = Path(args.output); out.mkdir(parents=True, exist_ok=True)
    adapter = NDMAdapter({"writer_model": args.writer_model})
    result = adapter.build_one(src["source_id"], src["context"], out, src.get("conversation_id"))
    print(json.dumps(result, indent=2, ensure_ascii=False))
