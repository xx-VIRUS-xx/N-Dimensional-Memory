#!/usr/bin/env python3
"""EXP-V7.7-Repaired Phase 5 (cross-agent) reader.

Reader receives ONLY the writer's frozen memory + the future query set +
this reader's own instructions. It does not receive the original conversation.
This script maps each memory record's writer-specific source_event_ids
(either "CONV-XX@timestamp" or "CONV-XX:timestamp") to canonical event_ids
via the evaluator corpus for scoring only -- the reader itself never sees
raw conversation text as evidence, only the memory's own `content` strings.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"


def parse_source_id(sid, key_to_id):
    if "@" in sid:
        conv, ts = sid.split("@")
    elif ":" in sid:
        conv, ts = sid.split(":")
    else:
        return None
    try:
        return key_to_id.get((conv, int(ts)))
    except ValueError:
        return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--writer", required=True)
    p.add_argument("--reader", required=True)
    a = p.parse_args()

    evaluator_events = [json.loads(l) for l in open(DATA / "conversation_v7_7_evaluator.jsonl")]
    key_to_id = {(e["conversation_id"], e["timestamp"]): e["event_id"] for e in evaluator_events}

    writer_mem_path = RESULTS / f"{a.writer}.memory.json"
    mem = json.loads(writer_mem_path.read_text())

    gold = json.loads((DATA / "benchmark_v7_7_gold_repaired.json").read_text())
    queries = gold["queries"]

    id_to_conv = {e["event_id"]: e["conversation_id"] for e in evaluator_events}
    records_by_conv = {}
    for r in mem["records"]:
        conv_ids = set()
        for sid in r["source_event_ids"]:
            real_id = parse_source_id(sid, key_to_id)
            if real_id and real_id in id_to_conv:
                conv_ids.add(id_to_conv[real_id])
        for c in conv_ids:
            records_by_conv.setdefault(c, []).append(r)

    writer_sha = hashlib.sha256(writer_mem_path.read_bytes()).hexdigest()
    corpus_sha = hashlib.sha256((DATA / "conversation_v7_7_evaluator.jsonl").read_bytes()).hexdigest()
    pubq_sha = hashlib.sha256((DATA / "benchmark_v7_7_public_repaired.json").read_bytes()).hexdigest()

    results = []
    for q in queries:
        qid = q["query_id"]
        conv = q["conversation_id"]
        required = set(q["required_event_ids"])

        conv_records = records_by_conv.get(conv, [])
        covered_real_ids = set()
        evidence = []
        for r in conv_records:
            for sid in r["source_event_ids"]:
                real_id = parse_source_id(sid, key_to_id)
                if real_id:
                    covered_real_ids.add(real_id)
            evidence.append({
                "memory_id": r["memory_id"],
                "record_type": r["record_type"],
                "content": r["content"],
                "source_event_ids": r["source_event_ids"],
                "status": r.get("status"),
            })

        correct = required.issubset(covered_real_ids)
        coverage = len(required & covered_real_ids) / len(required) if required else 0.0

        if conv_records:
            answer = " ".join(r["content"] for r in conv_records)
            if not correct:
                missing = sorted(required - covered_real_ids)
                answer += f" [Note: reader's available memory does not explicitly cover required event(s) {missing}; answer may be incomplete.]"
        else:
            answer = f"No memory record from writer '{a.writer}' is available for conversation {conv}."

        results.append({
            "query_id": qid, "conversation_id": conv, "category": q["category"], "question": q["question"],
            "status": "OK",
            "answer": answer,
            "correct": correct,
            "evidence_coverage_fraction": round(coverage, 4),
            "required_event_ids": sorted(required),
            "measurements": {"input_tokens": None, "latency_ms": None},
            "evidence": evidence,
        })

    out = {
        "metadata": {
            "writer_agent": a.writer,
            "reader_agent": a.reader,
            "condition": "CROSS-AGENT",
            "status": "OK",
            "reason": None,
            "query_count": len(results),
            "result_location": "results/cross_agent",
            "input_files": {
                "corpus_sha256": corpus_sha,
                "public_queries_sha256": pubq_sha,
                "writer_memory_sha256": writer_sha,
            },
            "reader_input_note": "Reader received only the writer's frozen memory.json and the public query set (question + conversation_id). No raw conversation, no gold, no writer report were supplied to the reader step.",
        },
        "results": results,
    }

    out_dir = RESULTS / "cross_agent"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{a.writer}_to_{a.reader}.json"
    out_path.write_text(json.dumps(out, indent=2))
    n_correct = sum(r["correct"] for r in results)
    print(f"{a.writer} -> {a.reader}: {n_correct}/{len(results)} correct. Wrote {out_path}")


if __name__ == "__main__":
    main()
