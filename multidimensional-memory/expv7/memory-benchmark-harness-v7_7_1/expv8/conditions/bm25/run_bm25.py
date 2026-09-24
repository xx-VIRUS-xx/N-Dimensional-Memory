import json
import os
import re
import time
from pathlib import Path

from datasets import load_from_disk
from rank_bm25 import BM25Okapi
from google import genai


DATASET_PATH = Path("datasets/longbench_v2")
OUTPUT_PATH = Path("results/bm25/longbench_v2_bm25.jsonl")
SUMMARY_PATH = Path("results/bm25/summary.json")

TOP_K = int(os.getenv("BM25_TOP_K", "12"))
CHUNK_WORDS = int(os.getenv("BM25_CHUNK_WORDS", "800"))
CHUNK_OVERLAP = int(os.getenv("BM25_CHUNK_OVERLAP", "100"))

MODEL = os.getenv("RAW_MODEL", "gemini-2.5-flash-lite")

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)


def tokenize(text):
    return re.findall(r"\b\w+\b", text.lower())


def chunk_text(text):
    words = text.split()

    chunks = []
    start = 0

    while start < len(words):
        end = min(start + CHUNK_WORDS, len(words))

        chunk = " ".join(words[start:end])

        chunks.append({
            "chunk_id": len(chunks),
            "text": chunk,
            "start_word": start,
            "end_word": end,
        })

        if end >= len(words):
            break

        start = max(end - CHUNK_OVERLAP, start + 1)

    return chunks


def build_prompt(row, retrieved_chunks):
    evidence = "\n\n".join(
        f"[CHUNK {c['chunk_id']}]\n{c['text']}"
        for c in retrieved_chunks
    )

    return f"""You are answering a multiple-choice question.

Use ONLY the retrieved evidence below.

Return ONLY one letter:
A
B
C
D

Retrieved evidence:
{evidence}

Question:
{row["question"]}

A. {row["choice_A"]}
B. {row["choice_B"]}
C. {row["choice_C"]}
D. {row["choice_D"]}

Answer with exactly one letter.
"""


def normalize_answer(value):
    if value is None:
        return None

    value = str(value).strip().upper()

    match = re.search(r"\b([ABCD])\b", value)

    if match:
        return match.group(1)

    if value in {"A", "B", "C", "D"}:
        return value

    return None


def run_reader(prompt):
    start = time.perf_counter()

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
    )

    latency_ms = (time.perf_counter() - start) * 1000

    text = response.text or ""

    usage = getattr(response, "usage_metadata", None)

    input_tokens = None
    output_tokens = None

    if usage:
        input_tokens = getattr(
            usage,
            "prompt_token_count",
            None,
        )

        output_tokens = getattr(
            usage,
            "candidates_token_count",
            None,
        )

    return {
        "raw_response": text,
        "predicted_answer": normalize_answer(text),
        "latency_ms": latency_ms,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
    }


def main():
    ds = load_from_disk(str(DATASET_PATH))["train"]

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    results = []

    total_correct = 0
    total_invalid = 0
    total_errors = 0

    print(f"LongBench-v2 questions: {len(ds)}")
    print(f"Condition: BM25")
    print(f"Model: {MODEL}")
    print(f"Top-k: {TOP_K}")
    print(f"Chunk size: {CHUNK_WORDS}")
    print(f"Overlap: {CHUNK_OVERLAP}")

    for i, row in enumerate(ds):

        print(
            f"[{i + 1}/{len(ds)}] "
            f"{row['_id']}",
            flush=True,
        )

        chunks = chunk_text(row["context"])

        tokenized_chunks = [
            tokenize(c["text"])
            for c in chunks
        ]

        bm25 = BM25Okapi(tokenized_chunks)

        query_tokens = tokenize(row["question"])

        scores = bm25.get_scores(query_tokens)

        ranked_indices = sorted(
            range(len(chunks)),
            key=lambda x: scores[x],
            reverse=True,
        )[:TOP_K]

        retrieved_chunks = [
            chunks[idx]
            for idx in ranked_indices
        ]

        retrieved_scores = [
            float(scores[idx])
            for idx in ranked_indices
        ]

        prompt = build_prompt(
            row,
            retrieved_chunks,
        )

        result = {
            "condition": "BM25",
            "dataset": "LongBench-v2",
            "split": "train",
            "index": i,
            "question_id": row["_id"],
            "domain": row["domain"],
            "sub_domain": row["sub_domain"],
            "difficulty": row["difficulty"],
            "length": row["length"],
            "gold_answer": row["answer"],
            "top_k": TOP_K,
            "chunk_words": CHUNK_WORDS,
            "chunk_overlap": CHUNK_OVERLAP,
            "retrieved_chunks": [
                {
                    "chunk_id": c["chunk_id"],
                    "score": score,
                    "start_word": c["start_word"],
                    "end_word": c["end_word"],
                }
                for c, score in zip(
                    retrieved_chunks,
                    retrieved_scores,
                )
            ],
            "status": "ERROR",
            "predicted_answer": None,
            "correct": None,
            "latency_ms": None,
            "input_tokens": None,
            "output_tokens": None,
            "error": None,
        }

        try:
            reader_result = run_reader(prompt)

            result.update({
                "status": "SUCCESS"
                if reader_result["predicted_answer"]
                else "INVALID_OUTPUT",
                "predicted_answer":
                    reader_result["predicted_answer"],
                "raw_response":
                    reader_result["raw_response"],
                "latency_ms":
                    reader_result["latency_ms"],
                "input_tokens":
                    reader_result["input_tokens"],
                "output_tokens":
                    reader_result["output_tokens"],
            })

            if reader_result["predicted_answer"]:
                result["correct"] = (
                    reader_result["predicted_answer"]
                    == row["answer"]
                )

                if result["correct"]:
                    total_correct += 1
            else:
                total_invalid += 1

        except Exception as exc:
            result["error"] = repr(exc)
            total_errors += 1

        results.append(result)

        with OUTPUT_PATH.open("a") as f:
            f.write(
                json.dumps(
                    result,
                    ensure_ascii=False,
                )
                + "\n"
            )

    completed = len(results)

    summary = {
        "dataset": "LongBench-v2",
        "condition": "BM25",
        "model": MODEL,
        "questions": completed,
        "correct": total_correct,
        "accuracy": (
            total_correct / completed
            if completed
            else None
        ),
        "invalid_output": total_invalid,
        "errors": total_errors,
        "top_k": TOP_K,
        "chunk_words": CHUNK_WORDS,
        "chunk_overlap": CHUNK_OVERLAP,
    }

    SUMMARY_PATH.write_text(
        json.dumps(
            summary,
            indent=2,
        )
        + "\n"
    )

    print("\n==============================")
    print("BM25 COMPLETE")
    print("==============================")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()