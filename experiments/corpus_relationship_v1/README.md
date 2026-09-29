# NDM Corpus → Entity-Dimension → Mathematical Structure v1

This experiment is the next step after the semantic reconstruction test.

## Research question

Can a real corpus be processed event-by-event into **entity-specific dimensions**, without asking the LLM to build a cross-event relationship graph, and then yield measurable mathematical structure from which candidate entity relationships can be discovered?

The division of responsibility is deliberate:

```
Corpus
  ↓
LLM semantic interpretation
  ↓
event-level entities + dimensions
  ↓
deterministic validation / normalization
  ↓
mathematical representation
  ↓
similarity + structural signals
  ↓
candidate relationship discovery
  ↓
independent validation
```

The LLM is the semantic interpreter. The relationship engine is algorithmic.

## What this experiment must not do

- Do not ask the extraction model to create relationship edges.
- Do not infer a relationship merely because two entities occur in the same event.
- Do not infer chronology or causality across events.
- Do not resolve entity aliases across the corpus during extraction.
- Do not treat vector proximity as proof of a semantic relationship.

The experiment records three different things separately:

1. **Explicit semantic information** contained in the entity dimensions.
2. **Mathematical signals** computed from those dimensions.
3. **Candidate relationships** produced by the algorithm.

## Directory

```
corpus_relationship_v1/
├── README.md
├── requirements.txt
├── setup.sh
├── prompts/
│   └── entity_dimension_extraction.md
├── sample/
│   ├── extracted_entity_dimensions.jsonl
│   └── gold_relationships.jsonl
├── run_pipeline.py
└── evaluate.py
```

Generated experiment output goes under `outputs/<run_name>/`.

## 1. Setup

```bash
cd experiments/corpus_relationship_v1
./setup.sh
source .venv/bin/activate
```

The default semantic model is `sentence-transformers/all-MiniLM-L6-v2`. The first run downloads its weights.

## 2. Prepare the corpus

The intended raw corpus format is JSONL:

```json
{"event_id":"e001","text":"Alice proposed PostgreSQL for the payments platform.","source":"example"}
```

Keep the original events unchanged. The extraction artifact is a separate file.

For the initial experiment, aim for approximately 100–500 events and 20–100 unique entities, with repeated entities across events.

## 3. Extract entities and dimensions with Claude Code

Use `prompts/entity_dimension_extraction.md` with Claude Code.

The output must be JSONL, one object per event:

```json
{
  "event_id": "e001",
  "entities": [
    {
      "name": "Alice",
      "dimensions": [
        {"name": "event_role", "value": "proposer"},
        {"name": "action_performed", "value": "proposed PostgreSQL for the payments platform"}
      ]
    }
  ]
}
```

The extractor may create arbitrary dimension names. Do not impose a fixed ontology.

### Important identity rule

For v1, entity identity is the normalized literal name:

```
"Payments Platform" → "payments platform"
```

This intentionally does **not** perform semantic entity resolution. Keep aliases separate unless a later, independently created alias map merges them.

This prevents entity resolution from silently contaminating the relationship experiment.

## 4. Build the mathematical representation

Run:

```bash
python run_pipeline.py   --input sample/extracted_entity_dimensions.jsonl   --output outputs/sample   --top-k 5
```

For the real corpus:

```bash
python run_pipeline.py   --input /path/to/entity_dimensions.jsonl   --output outputs/corpus_v1   --top-k 10
```

The pipeline creates:

```
outputs/corpus_v1/
├── validation_report.json
├── entities.json
├── dimension_records.jsonl
├── entity_features.npy
├── similarity_matrix.npy
├── pair_signals.jsonl
├── candidate_relationships.json
└── entity_projection.png
```

## 5. Mathematical representation

For each entity, each dimension becomes:

```
dimension_name: dimension_value
```

A sentence-transformer encodes these items. The entity vector is the normalized mean of its dimension vectors.

For entities A and B the baseline computes:

- `semantic_cosine`
- `dimension_name_jaccard`
- `event_jaccard`
- `dimension_text_tfidf_cosine`

The baseline candidate score is:

```
0.60 * semantic_cosine
+ 0.15 * dimension_name_jaccard
+ 0.15 * event_jaccard
+ 0.10 * dimension_text_tfidf_cosine
```

This is an experimental baseline, not a claim about the final NDM algorithm. All component signals are preserved.

No pair is called a verified relationship. The pipeline only produces mathematical candidates.

## 6. Geometry

`entity_projection.png` is generated with PCA.

The plot is diagnostic. Proximity is not proof of a semantic relationship.

## 7. Independent evaluation

When a manually constructed gold set exists:

```bash
python evaluate.py   --candidates outputs/corpus_v1/candidate_relationships.json   --gold sample/gold_relationships.jsonl   --k 5
```

The gold set must be created independently of the candidate-generating algorithm.

This turns the experiment into a falsifiable test rather than a vector-space demo.

## Scientific progression

```
v1: baseline entity-dimension representation
 ↓
v2: alternative aggregation methods
 ↓
v3: dimension-aware / multi-vector representations
 ↓
v4: learned or analytically derived relationship scoring
 ↓
v5: temporal / directional cross-event structure
 ↓
v6: scale and retrieval benchmarks
```

Do not optimize later stages until v1 shows measurable signal.
