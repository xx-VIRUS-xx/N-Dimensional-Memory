import json
import os
import time
from pathlib import Path
import sys
PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from datasets import load_from_disk
from harness.reader.claude_code_reader import ClaudeCodeReader, normalize_answer

DATASET_PATH = Path("datasets/longbench_v2")
OUTPUT_PATH = Path("results/raw/longbench_v2_raw.jsonl")
SUMMARY_PATH = Path("results/raw/summary.json")
READER_MODEL = os.getenv("CLAUDE_MODEL", "sonnet")


def build_prompt(row):
    return f"""You are answering a multiple-choice question.

Read the context carefully and answer the question using ONLY the information in the context.

Return ONLY one of:
A
B
C
D

Context:
{row["context"]}

Question:
{row["question"]}

A. {row["choice_A"]}
B. {row["choice_B"]}
C. {row["choice_C"]}
D. {row["choice_D"]}

Answer with exactly one letter.
"""


def load_existing_successes():
    existing = {}
    if not OUTPUT_PATH.exists():
        return existing
    print(f"Existing output found: {OUTPUT_PATH}")
    with OUTPUT_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if record.get("status") == "SUCCESS" and record.get("question_id") is not None:
                existing[record["question_id"]] = record
    print(f"Existing successful records: {len(existing)}")
    return existing


def extract_reader_fields(reader_result):
    raw = reader_result.get("raw_response") or {}
    usage = reader_result.get("usage") or raw.get("usage") or {}
    model_usage = (
        reader_result.get("model_usage")
        or reader_result.get("modelUsage")
        or raw.get("modelUsage")
        or {}
    )
    cost = reader_result.get("cost_usd")
    if cost is None:
        cost = raw.get("total_cost_usd")
    return {
        "reader_status": reader_result.get("status"),
        "session_id": reader_result.get("session_id"),
        "reader_text": reader_result.get("text"),
        "latency_ms": reader_result.get("latency_ms"),
        "estimated_cost_usd": cost,
        "input_tokens": usage.get("input_tokens"),
        "output_tokens": usage.get("output_tokens"),
        "cache_read_input_tokens": usage.get("cache_read_input_tokens"),
        "cache_creation_input_tokens": usage.get("cache_creation_input_tokens"),
        "model_usage": model_usage,
        "permission_denials": reader_result.get("permission_denials") or raw.get("permission_denials"),
        "terminal_reason": reader_result.get("terminal_reason") or raw.get("terminal_reason"),
    }


def is_rate_limit(reader_result):
    status = str(reader_result.get("status", "")).upper()
    if status in {"RATE_LIMIT", "QUOTA", "RESOURCE_EXHAUSTED"}:
        return True
    raw = reader_result.get("raw_response") or {}
    text = json.dumps({"status": reader_result.get("status"), "text": reader_result.get("text"), "raw": raw}).lower()
    return any(marker in text for marker in ("rate limit", "rate_limit", "resource exhausted", "quota exceeded", "too many requests", "429"))


def atomic_checkpoint(temp_path):
    if temp_path.exists():
        temp_path.replace(OUTPUT_PATH)


def main():
    ds = load_from_disk(str(DATASET_PATH))["train"]
    print(f"Loaded LongBench-v2: {len(ds)} questions")
    print(f"Reader: Claude Code (requested model={READER_MODEL})")
    print(f"Output: {OUTPUT_PATH}")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    reader = ClaudeCodeReader()
    existing_successes = load_existing_successes()
    temp_path = OUTPUT_PATH.with_suffix(".tmp.jsonl")
    if temp_path.exists():
        temp_path.unlink()

    correct = sum(1 for r in existing_successes.values() if r.get("correct") is True)
    answered = len(existing_successes)
    errors = 0
    rate_limits = 0
    estimated_cost_total = sum(float(r.get("estimated_cost_usd") or 0.0) for r in existing_successes.values())
    total_input_tokens = sum(int(r.get("input_tokens") or 0) for r in existing_successes.values())
    total_output_tokens = sum(int(r.get("output_tokens") or 0) for r in existing_successes.values())
    total_cache_read_tokens = sum(int(r.get("cache_read_input_tokens") or 0) for r in existing_successes.values())
    total_cache_creation_tokens = sum(int(r.get("cache_creation_input_tokens") or 0) for r in existing_successes.values())
    start_total = time.time()
    interrupted = False

    try:
        with temp_path.open("w", encoding="utf-8") as output:
            for i, row in enumerate(ds):
                question_id = row["_id"]
                if question_id in existing_successes:
                    output.write(json.dumps(existing_successes[question_id], ensure_ascii=False) + "\n")
                    print(f"[{i + 1}/{len(ds)}] {question_id} | SKIP existing SUCCESS")
                    continue

                prompt = build_prompt(row)
                started = time.time()
                record = {
                    "condition": "RAW", "dataset": "LongBench-v2", "split": "train", "index": i,
                    "question_id": question_id, "domain": row["domain"], "sub_domain": row["sub_domain"],
                    "difficulty": row["difficulty"], "length": row["length"], "gold_answer": row["answer"],
                    "prompt_chars": len(prompt), "reader": "claude_code", "reader_model_requested": READER_MODEL,
                    "status": "RUNNING", "predicted_answer": None, "correct": None, "raw_answer": None,
                    "latency_ms": None, "estimated_cost_usd": None, "input_tokens": None, "output_tokens": None,
                    "cache_read_input_tokens": None, "cache_creation_input_tokens": None, "model_usage": None,
                    "permission_denials": None, "terminal_reason": None, "error": None,
                }
                reader_result = None
                try:
                    reader_result = reader.ask(prompt)
                    fields = extract_reader_fields(reader_result)
                    record.update({
                        "reader_status": fields["reader_status"], "session_id": fields["session_id"],
                        "latency_ms": fields["latency_ms"], "estimated_cost_usd": fields["estimated_cost_usd"],
                        "input_tokens": fields["input_tokens"], "output_tokens": fields["output_tokens"],
                        "cache_read_input_tokens": fields["cache_read_input_tokens"],
                        "cache_creation_input_tokens": fields["cache_creation_input_tokens"],
                        "model_usage": fields["model_usage"], "permission_denials": fields["permission_denials"],
                        "terminal_reason": fields["terminal_reason"],
                    })
                    raw_answer = (fields["reader_text"] or "").strip()
                    predicted = normalize_answer(raw_answer)
                    record["raw_answer"] = raw_answer
                    record["predicted_answer"] = predicted
                    if str(fields["reader_status"] or "").upper() != "SUCCESS":
                        record["status"] = fields["reader_status"] or "ERROR"
                        record["error"] = {"type": "ReaderError", "message": f"Claude reader returned status={fields['reader_status']}"}
                        errors += 1
                    else:
                        record["status"] = "SUCCESS"
                        record["correct"] = predicted == row["answer"] if predicted is not None else False
                        answered += 1
                        correct += int(record["correct"])
                        estimated_cost_total += float(fields["estimated_cost_usd"] or 0.0)
                        total_input_tokens += int(fields["input_tokens"] or 0)
                        total_output_tokens += int(fields["output_tokens"] or 0)
                        total_cache_read_tokens += int(fields["cache_read_input_tokens"] or 0)
                        total_cache_creation_tokens += int(fields["cache_creation_input_tokens"] or 0)
                except Exception as exc:
                    record["status"] = "ERROR"
                    record["error"] = {"type": type(exc).__name__, "message": str(exc)}
                    errors += 1

                if record["latency_ms"] is None:
                    record["latency_ms"] = round((time.time() - started) * 1000, 2)
                output.write(json.dumps(record, ensure_ascii=False) + "\n")
                output.flush()

                accuracy = correct / answered if answered else 0.0
                print(
                    f"[{i + 1}/{len(ds)}] {question_id} | status={record['status']} | "
                    f"pred={record.get('predicted_answer')} | gold={row['answer']} | "
                    f"accuracy={accuracy:.4f} | latency={record.get('latency_ms')}ms | "
                    f"est_cost=${record.get('estimated_cost_usd')}"
                )

                if reader_result is not None and is_rate_limit(reader_result):
                    rate_limits += 1
                    print("\nRATE LIMIT DETECTED. Checkpointing completed records and stopping.")
                    break

        atomic_checkpoint(temp_path)
    except KeyboardInterrupt:
        interrupted = True
        print("\nInterrupted. Checkpointing completed records...")
        atomic_checkpoint(temp_path)
    except Exception:
        atomic_checkpoint(temp_path)
        raise

    total_time = time.time() - start_total
    summary = {
        "condition": "RAW", "dataset": "LongBench-v2", "split": "train", "questions": len(ds),
        "answered": answered, "correct": correct, "accuracy": correct / answered if answered else 0.0,
        "errors": errors, "rate_limits": rate_limits, "interrupted": interrupted,
        "reader": "claude_code", "reader_model_requested": READER_MODEL,
        "estimated_cost_usd": round(estimated_cost_total, 8), "input_tokens": total_input_tokens,
        "output_tokens": total_output_tokens, "cache_read_input_tokens": total_cache_read_tokens,
        "cache_creation_input_tokens": total_cache_creation_tokens, "total_runtime_seconds": round(total_time, 2),
        "output": str(OUTPUT_PATH),
    }
    with SUMMARY_PATH.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print("\n" + "=" * 60)
    print("RAW RUN FINISHED / CHECKPOINTED")
    print("=" * 60)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
