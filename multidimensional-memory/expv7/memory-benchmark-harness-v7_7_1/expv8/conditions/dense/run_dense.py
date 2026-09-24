import os
import json
import time
from pathlib import Path

import faiss
import numpy as np
from datasets import load_from_disk
from sentence_transformers import SentenceTransformer
from google import genai


# ============================================================
# CONFIG
# ============================================================

DATASET_PATH = Path("datasets/longbench_v2")

OUTPUT_PATH = Path(
    "results/dense/longbench_v2_dense.jsonl"
)

SUMMARY_PATH = Path(
    "results/dense/summary.json"
)

TOP_K = 12
CHUNK_WORDS = 800
CHUNK_OVERLAP = 100

EMBEDDING_MODEL = os.getenv(
    "DENSE_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2",
)

READER_MODEL = os.getenv(
    "RAW_MODEL",
    "gemini-2.5-flash-lite",
)

API_KEY = os.getenv("GEMINI_API_KEY")


# ============================================================
# VALIDATION
# ============================================================

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY environment variable is not set."
    )


OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)


# ============================================================
# CLIENTS
# ============================================================

print(f"Loading embedding model: {EMBEDDING_MODEL}")

embedder = SentenceTransformer(EMBEDDING_MODEL)

client = genai.Client(api_key=API_KEY)


# ============================================================
# DATASET
# ============================================================

print(f"Loading dataset from: {DATASET_PATH}")

dataset = load_from_disk(str(DATASET_PATH))

if hasattr(dataset, "keys"):
    split_name = "train" if "train" in dataset else list(dataset.keys())[0]
    dataset = dataset[split_name]

print(f"Questions: {len(dataset)}")


# ============================================================
# CHUNKING
# ============================================================

def chunk_text(text, chunk_words=CHUNK_WORDS, overlap=CHUNK_OVERLAP):
    words = text.split()

    if not words:
        return []

    chunks = []

    step = chunk_words - overlap

    for start in range(0, len(words), step):
        end = min(start + chunk_words, len(words))

        chunk = " ".join(words[start:end]).strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(words):
            break

    return chunks


# ============================================================
# DENSE RETRIEVAL
# ============================================================

def dense_retrieve(context, query, top_k=TOP_K):
    chunks = chunk_text(context)

    if not chunks:
        return []

    # Encode corpus chunks
    chunk_embeddings = embedder.encode(
        chunks,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    # FAISS inner-product over normalized vectors = cosine similarity
    dimension = chunk_embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)

    index.add(
        chunk_embeddings.astype(np.float32)
    )

    # Encode query
    query_embedding = embedder.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    k = min(top_k, len(chunks))

    scores, indices = index.search(
        query_embedding.astype(np.float32),
        k,
    )

    results = []

    for rank, (idx, score) in enumerate(
        zip(indices[0], scores[0]),
        start=1,
    ):
        if idx < 0:
            continue

        results.append(
            {
                "rank": rank,
                "chunk_id": int(idx),
                "score": float(score),
                "text": chunks[idx],
            }
        )

    return results


# ============================================================
# GEMINI READER
# ============================================================

def build_prompt(question, choices, evidence):
    evidence_text = "\n\n".join(
        f"[Evidence {item['rank']}]\n{item['text']}"
        for item in evidence
    )

    return f"""
You are answering a multiple-choice question.

Use ONLY the supplied evidence.

Return ONLY the letter of the correct answer:
A
B
C
or
D

Do not provide an explanation.

QUESTION:
{question}

CHOICES:
A. {choices['A']}
B. {choices['B']}
C. {choices['C']}
D. {choices['D']}

EVIDENCE:
{evidence_text}

ANSWER:
""".strip()


def normalize_answer(text):
    if not text:
        return None

    text = text.strip().upper()

    # Exact answer
    if text in {"A", "B", "C", "D"}:
        return text

    # Handle common model formatting
    for letter in ["A", "B", "C", "D"]:
        if text.startswith(f"{letter}."):
            return letter

        if text.startswith(f"{letter})"):
            return letter

        if text.startswith(f"({letter})"):
            return letter

    # Last-resort extraction from very short outputs
    tokens = text.replace(".", " ").replace(")", " ").split()

    for token in tokens[:3]:
        if token in {"A", "B", "C", "D"}:
            return token

    return None


# ============================================================
# MAIN LOOP
# ============================================================

results = []

correct = 0
answered = 0
errors = 0

start_total = time.time()

for i, item in enumerate(dataset):

    question_id = item.get("_id", str(i))

    question = item["question"]

    choices = {
        "A": item["choice_A"],
        "B": item["choice_B"],
        "C": item["choice_C"],
        "D": item["choice_D"],
    }

    gold = item["answer"]

    question_start = time.time()

    record = {
        "question_id": question_id,
        "index": i,
        "condition": "DENSE",
        "retrieval": {
            "model": EMBEDDING_MODEL,
            "top_k": TOP_K,
            "chunk_words": CHUNK_WORDS,
            "chunk_overlap": CHUNK_OVERLAP,
        },
        "reader": READER_MODEL,
        "status": "SUCCESS",
    }

    try:

        # ----------------------------------------------------
        # Retrieval
        # ----------------------------------------------------

        evidence = dense_retrieve(
            context=item["context"],
            query=question,
            top_k=TOP_K,
        )

        record["evidence"] = [
            {
                "rank": e["rank"],
                "chunk_id": e["chunk_id"],
                "score": e["score"],
                "text": e["text"],
            }
            for e in evidence
        ]

        # ----------------------------------------------------
        # Reader
        # ----------------------------------------------------

        prompt = build_prompt(
            question=question,
            choices=choices,
            evidence=evidence,
        )

        response = client.models.generate_content(
            model=READER_MODEL,
            contents=prompt,
        )

        raw_answer = response.text.strip()

        predicted = normalize_answer(raw_answer)

        record["raw_answer"] = raw_answer
        record["predicted_answer"] = predicted
        record["gold_answer"] = gold

        record["correct"] = (
            predicted == gold
            if predicted is not None
            else False
        )

        if predicted is not None:
            answered += 1

            if predicted == gold:
                correct += 1

        # ----------------------------------------------------
        # Token usage
        # ----------------------------------------------------

        usage = getattr(response, "usage_metadata", None)

        if usage:

            record["usage"] = {
                "prompt_tokens": getattr(
                    usage,
                    "prompt_token_count",
                    None,
                ),
                "output_tokens": getattr(
                    usage,
                    "candidates_token_count",
                    None,
                ),
                "total_tokens": getattr(
                    usage,
                    "total_token_count",
                    None,
                ),
            }

    except Exception as exc:

        errors += 1

        record["status"] = "ERROR"

        record["error"] = {
            "type": type(exc).__name__,
            "message": str(exc),
        }

    record["latency_seconds"] = (
        time.time() - question_start
    )

    results.append(record)

    # --------------------------------------------------------
    # Append immediately
    # --------------------------------------------------------

    with OUTPUT_PATH.open(
        "a",
        encoding="utf-8",
    ) as f:

        f.write(
            json.dumps(
                record,
                ensure_ascii=False,
            )
            + "\n"
        )

    # --------------------------------------------------------
    # Progress
    # --------------------------------------------------------

    completed = i + 1

    accuracy = (
        correct / answered
        if answered
        else 0.0
    )

    print(
        f"[{completed}/{len(dataset)}] "
        f"{question_id} | "
        f"status={record['status']} | "
        f"pred={record.get('predicted_answer')} | "
        f"gold={gold} | "
        f"accuracy={accuracy:.4f}"
    )


# ============================================================
# SUMMARY
# ============================================================

total_time = time.time() - start_total

summary = {
    "condition": "DENSE",
    "dataset": "LongBench-v2",
    "dataset_path": str(DATASET_PATH),

    "questions": len(dataset),

    "answered": answered,
    "correct": correct,

    "accuracy": (
        correct / answered
        if answered
        else 0.0
    ),

    "errors": errors,

    "embedding_model": EMBEDDING_MODEL,
    "reader_model": READER_MODEL,

    "top_k": TOP_K,
    "chunk_words": CHUNK_WORDS,
    "chunk_overlap": CHUNK_OVERLAP,

    "total_runtime_seconds": total_time,

    "output": str(OUTPUT_PATH),
}


with SUMMARY_PATH.open(
    "w",
    encoding="utf-8",
) as f:

    json.dump(
        summary,
        f,
        indent=2,
    )


print("\n" + "=" * 60)
print("DENSE RUN COMPLETE")
print("=" * 60)
print(json.dumps(summary, indent=2))