#!/usr/bin/env python3
"""EXP-V7.7-Repaired Phase D: integrity manifest + independent correctness scoring.

Scores every agent's Phase B/C result file against evaluation/data/benchmark_v7_7_gold_repaired.json's
required_event_ids, since not every agent's own output includes a self-reported `correct` field
(Codex's does not; Claude's does). This computes one consistent, independently-derived correctness
score for every agent/condition so comparisons are apples-to-apples, and separately preserves each
agent's own self-reported score where present for comparison.
"""
import json
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _ids_from_one_evidence_dict(ev, evaluator_events, key_to_id, ids):
    if "event_id" in ev and isinstance(ev["event_id"], str) and ev["event_id"] in evaluator_events:
        ids.add(ev["event_id"])
    if "source_event_id" in ev and isinstance(ev["source_event_id"], str):
        _resolve_sid(ev["source_event_id"], evaluator_events, key_to_id, ids)
    for sid in ev.get("source_event_ids", []) or []:
        if isinstance(sid, str):
            _resolve_sid(sid, evaluator_events, key_to_id, ids)


def _resolve_sid(sid, evaluator_events, key_to_id, ids):
    if sid in evaluator_events:
        ids.add(sid)
        return
    sep = "@" if "@" in sid else (":" if ":" in sid else None)
    if not sep:
        return
    conv, ts = sid.split(sep)
    try:
        ts = int(ts)
    except ValueError:
        return
    real = key_to_id.get((conv, ts))
    if real:
        ids.add(real)


def extract_evidence_event_ids(record):
    """Best-effort extraction of real event_ids referenced by one result record's evidence,
    across the different shapes agents used: evidence as a list of dicts (with
    source_event_ids/source_event_id/event_id fields, using 'CONV-XX@ts' or 'CONV-XX:ts'
    or a real event_id string directly), or evidence as a dict of named sub-lists
    (e.g. Codex's MEMORY+RAW shape: {"memory_records": [...], "linked_raw_events": [...]})."""
    evaluator_events = extract_evidence_event_ids._cache
    key_to_id = extract_evidence_event_ids._key_to_id
    ids = set()
    evidence = record.get("evidence", [])
    if isinstance(evidence, dict):
        sub_items = []
        for v in evidence.values():
            if isinstance(v, list):
                sub_items.extend(v)
        evidence = sub_items
    for ev in evidence:
        if isinstance(ev, dict):
            _ids_from_one_evidence_dict(ev, evaluator_events, key_to_id, ids)
        elif isinstance(ev, str):
            _resolve_sid(ev, evaluator_events, key_to_id, ids)
    return ids


def main():
    evaluator_events_list = [json.loads(l) for l in open(DATA / "conversation_v7_7_evaluator.jsonl")]
    evaluator_event_ids = {e["event_id"] for e in evaluator_events_list}
    key_to_id = {(e["conversation_id"], e["timestamp"]): e["event_id"] for e in evaluator_events_list}
    extract_evidence_event_ids._cache = evaluator_event_ids
    extract_evidence_event_ids._key_to_id = key_to_id

    gold = json.loads((DATA / "benchmark_v7_7_gold_repaired.json").read_text())
    required_by_qid = {q["query_id"]: set(q["required_event_ids"]) for q in gold["queries"]}

    manifest = {
        "experiment": "EXP-V7.7-Repaired",
        "phase": "D-integrity",
        "dataset_hash": {
            "corpus_evaluator": sha(DATA / "conversation_v7_7_evaluator.jsonl"),
            "corpus_unlabeled": sha(DATA / "conversation_v7_7_unlabeled.jsonl"),
            "public_queries": sha(DATA / "benchmark_v7_7_public_repaired.json"),
            "gold": sha(DATA / "benchmark_v7_7_gold_repaired.json"),
        },
        "writer_memories": {},
        "phase_b_conditions": {},
        "phase_c_cross_agent": {},
        "integrity_failures": [],
    }

    for agent in ["claude", "codex", "copilot"]:
        frozen_p = ROOT / "frozen" / agent / "memory.json"
        results_p = RESULTS / f"{agent}.memory.json"
        p = frozen_p if frozen_p.exists() else results_p
        if p.exists():
            d = json.loads(p.read_text())
            entry = {
                "path": str(p.relative_to(ROOT)),
                "sha256": sha(p),
                "record_count": len(d.get("records", [])),
                "memory_version": d.get("memory_version"),
            }
            if frozen_p.exists() and results_p.exists():
                entry["results_copy_matches_frozen"] = sha(frozen_p) == sha(results_p)
                if not entry["results_copy_matches_frozen"]:
                    manifest["integrity_failures"].append(f"{agent}: results/{agent}.memory.json diverges from frozen/{agent}/memory.json")
            manifest["writer_memories"][agent] = entry
        else:
            manifest["writer_memories"][agent] = {"status": "MISSING"}
            manifest["integrity_failures"].append(f"{agent}.memory.json missing (checked frozen/ and results/)")

    conditions = ["RAW", "BM25", "DENSE", "HYBRID", "GRAPHRAG", "HIPPORAG2", "RAPTOR", "GRAPHITI", "MEMORY", "MEMORY+RAW"]
    for agent in ["claude", "codex"]:
        manifest["phase_b_conditions"][agent] = {}
        for cond in conditions:
            p = RESULTS / "retrieval" / f"{agent}.{cond}.json"
            if not p.exists():
                manifest["phase_b_conditions"][agent][cond] = {"status": "MISSING"}
                manifest["integrity_failures"].append(f"{agent}.{cond}.json missing")
                continue
            d = json.loads(p.read_text())
            status = d["metadata"]["status"]
            entry = {"path": str(p.relative_to(ROOT)), "sha256": sha(p), "status": status}
            if status == "OK":
                n_scored = 0
                n_correct_independent = 0
                n_correct_self_reported = None
                self_reported_present = all("correct" in r for r in d["results"])
                if self_reported_present:
                    n_correct_self_reported = sum(r["correct"] for r in d["results"])
                for r in d["results"]:
                    required = required_by_qid.get(r["query_id"])
                    if required is None:
                        continue
                    covered = extract_evidence_event_ids(r)
                    n_scored += 1
                    if required.issubset(covered):
                        n_correct_independent += 1
                entry["independently_scored_correct"] = n_correct_independent
                entry["independently_scored_total"] = n_scored
                entry["self_reported_correct"] = n_correct_self_reported
                if n_correct_self_reported is not None and n_correct_self_reported != n_correct_independent:
                    manifest["integrity_failures"].append(
                        f"{agent}.{cond}: self-reported correct ({n_correct_self_reported}) != independently rescored correct ({n_correct_independent})"
                    )
            else:
                entry["reason"] = d["metadata"]["reason"]
            manifest["phase_b_conditions"][agent][cond] = entry

    manifest["phase_b_conditions"]["copilot"] = {
        "status": "NOT_PRODUCED_BY_WRITER",
        "note": "Copilot's session had not produced Phase B retrieval condition files in results/retrieval/ at the time this manifest was generated; only results/copilot.memory.json (Phase A) exists.",
    }

    pairs = [("claude", "codex"), ("claude", "copilot"), ("codex", "claude"), ("codex", "copilot"), ("copilot", "claude"), ("copilot", "codex")]
    for writer, reader in pairs:
        p = RESULTS / "cross_agent" / f"{writer}_to_{reader}.json"
        if not p.exists():
            manifest["integrity_failures"].append(f"{writer}_to_{reader} cross-agent result missing")
            continue
        d = json.loads(p.read_text())
        meta = d.get("metadata", d)
        status = meta.get("status", "OK")

        if status != "OK":
            manifest["phase_c_cross_agent"][f"{writer}_to_{reader}"] = {
                "path": str(p.relative_to(ROOT)),
                "sha256": sha(p),
                "status": status,
                "reason": meta.get("reason"),
            }
            continue

        n_scored = 0
        n_correct = 0
        for r in d["results"]:
            required = required_by_qid.get(r["query_id"])
            if required is None:
                continue
            covered = extract_evidence_event_ids(r)
            n_scored += 1
            if required.issubset(covered):
                n_correct += 1
        actual_hash = manifest["writer_memories"].get(writer, {}).get("sha256")
        referenced_hash = (meta.get("input_files") or {}).get("writer_memory_sha256") or meta.get("writer_memory_sha256")
        entry = {
            "path": str(p.relative_to(ROOT)),
            "sha256": sha(p),
            "status": "OK",
            "independently_scored_correct": n_correct,
            "independently_scored_total": n_scored,
            "writer_memory_sha256_referenced": referenced_hash,
            "writer_memory_sha256_actual": actual_hash,
            "hash_match": referenced_hash == actual_hash,
        }
        if not entry["hash_match"]:
            manifest["integrity_failures"].append(f"{writer}_to_{reader}: memory hash mismatch between cross-agent record and current writer artifact")
        manifest["phase_c_cross_agent"][f"{writer}_to_{reader}"] = entry

    manifest["integrity_status"] = "PASS" if not manifest["integrity_failures"] else "FAIL"

    out_path = RESULTS / "MANIFEST_phase_d_integrity.json"
    out_path.write_text(json.dumps(manifest, indent=2))
    print("Wrote", out_path)
    print("integrity_status:", manifest["integrity_status"])
    for f in manifest["integrity_failures"]:
        print(" -", f)


if __name__ == "__main__":
    main()
