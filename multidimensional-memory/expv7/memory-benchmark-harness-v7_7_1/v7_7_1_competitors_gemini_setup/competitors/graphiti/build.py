from adapter import build,retrieve

# result = build(
#     "/Users/xxvirusxx/PY/BabyAI/N-Dimensional-Memory/multidimensional-memory/expv7/memory-benchmark-harness-v7_7_1/v7_7_1_competitors_gemini_setup/benchmark/smoke/hipporag_smoke.json",
#     "results/graphiti/smoke"
# )

# print(result)
# from competitors.graphiti.adapter import retrieve

result = retrieve(
    "What database does the billing service use after the migration?",
    3,
    "results/graphiti/smoke"
)

print(result)