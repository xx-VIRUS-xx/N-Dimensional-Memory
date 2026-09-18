# Evaluation Protocol

Selection recall = relevant retained / relevant gold.
Selection precision = relevant retained / all retained.
F1 = harmonic mean of precision and recall.
Retention = retained / total source events.
Compression = 1 - retention.

Consumption correctness must be evaluated against evaluator-only gold answers. Semantic paraphrases count as correct when the underlying state is equivalent.

Unsupported claims are tracked separately and never silently converted to incorrect answers.
