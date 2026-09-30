"""Cut an ND-1b chunk out of LoCoMo (snap-research/locomo, CC BY-NC 4.0).

The dataset is not stored in this repo. Download it, verify it, cut a chunk:
  git clone --depth 1 https://github.com/snap-research/locomo.git ~/locomo
  python tools/locomo_chunk.py --locomo ~/locomo/data/locomo10.json --sample 0 --sessions 1-3

Writes (git-ignored, regenerate any time):
  ND-1b/data/source.jsonl   one turn per line: sentence_id, dia_id, speaker, listener, date, text
  ND-1b/data/probes.jsonl   LoCoMo QA whose evidence lies inside the chunk
Standard library only.
"""
import argparse
import hashlib
import json
import os

EXPECTED_SHA256 = "79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--locomo", required=True)
    ap.add_argument("--sample", type=int, default=0)
    ap.add_argument("--sessions", default="1-3")
    ap.add_argument("--out-dir", default=None, help="default: ND-1b/data")
    a = ap.parse_args()
    raw = open(a.locomo, "rb").read()
    sha = hashlib.sha256(raw).hexdigest()
    if sha != EXPECTED_SHA256:
        raise SystemExit(f"locomo10.json SHA-256 mismatch: {sha} (expected {EXPECTED_SHA256})")
    lo, hi = (int(x) for x in a.sessions.split("-"))
    conv = json.loads(raw)[a.sample]
    c = conv["conversation"]
    who = {c["speaker_a"]: c["speaker_b"], c["speaker_b"]: c["speaker_a"]}
    turns = []
    for s in range(lo, hi + 1):
        for t in c[f"session_{s}"]:
            turns.append({"sentence_id": f"t{len(turns)}", "dia_id": t["dia_id"], "speaker": t["speaker"],
                          "listener": who[t["speaker"]], "date": c[f"session_{s}_date_time"], "text": t["text"]})
    in_chunk = {t["dia_id"] for t in turns}
    probes = []
    for i, q in enumerate(conv["qa"]):
        ev = q.get("evidence") or []
        if not ev or not all(e in in_chunk for e in ev):
            continue
        p = {"id": f"q{len(probes):02d}", "locomo_index": i, "category": q["category"],
             "question": q["question"], "evidence": ev}
        if q["category"] == 5:
            p["adversarial_answer"] = q.get("adversarial_answer")
            p["accept"] = ["not", "no", "unknown", "doesn't", "does not", "never"]
            p["note"] = "adversarial: the premise is wrong (usually attributes to the wrong speaker); correct = reject or correct the premise"
        else:
            p["gold_answer"] = str(q["answer"])
            p["accept"] = [str(q["answer"])]
        probes.append(p)
    out = os.path.abspath(a.out_dir) if a.out_dir else os.path.join(ROOT, "ND-1b", "data")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "source.jsonl"), "w") as f:
        for t in turns:
            f.write(json.dumps(t) + "\n")
    with open(os.path.join(out, "probes.jsonl"), "w") as f:
        for p in probes:
            f.write(json.dumps(p) + "\n")
    meta = {"dataset": "snap-research/locomo data/locomo10.json", "sha256": sha, "sample": a.sample,
            "sample_id": conv.get("sample_id"), "sessions": a.sessions, "turns": len(turns), "probes": len(probes),
            "license": "CC BY-NC 4.0 (derived data; non-commercial use with attribution)"}
    json.dump(meta, open(os.path.join(out, "chunk_meta.json"), "w"), indent=2)
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
