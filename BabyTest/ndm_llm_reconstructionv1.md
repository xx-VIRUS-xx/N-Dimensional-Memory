# NDM LLM Reconstruction Experiment v1

## Purpose

Test whether an LLM can interpret source context into a semantic representation and whether another LLM can reconstruct entity-specific semantic dimensions from that interpreted context.

This experiment is intentionally separate from NDM storage, relationship discovery, chronology, retrieval, and mathematical processing.

The LLM is being tested only as a semantic interpreter.

---

## Core Hypothesis

An interpreted natural-language representation can preserve enough semantic information that a second LLM can reconstruct the entities and entity-specific dimensions without receiving the original source context.

The important question is semantic recoverability, not textual similarity.

---

## Experimental Pipeline

```text
Original Source
      |
      v
LLM A: Semantic Interpretation
      |
      v
Interpreted Context
      |
      v
LLM B: Reconstruction
      |
      v
Entities + Entity-Specific Dimensions
```

The original source MUST NOT be provided to LLM B.

LLM B receives only the interpreted context produced by LLM A.

---

## Separation of Responsibilities

### LLM A

LLM A interprets the source.

It may express:

- entities
- actions
- states
- roles
- claims
- beliefs
- context
- qualifications
- uncertainty
- explicit temporal information
- other semantic information supported by the source

LLM A does not build the NDM storage structure.

### LLM B

LLM B reconstructs:

- entities
- entity-specific semantic dimensions
- dimension values supported by the interpreted context

LLM B must not recover information from the original source because it never receives it.

### NDM Algorithms

The following are OUTSIDE this experiment:

- cross-event relationships
- chronology construction
- causality
- entity resolution across events
- mathematical similarity
- retrieval
- state transitions across events
- graph construction
- memory compression
- query reconstruction

Those belong to the later computational layer.

---

# Test 001

## Source

`BabyTest/2601.14952v2.pdf`

The source is the CorpusQA paper used in the previous reliability experiment.

The previous experiment established that general-purpose LLMs can extract entities and entity-specific dimensions from this source. This experiment asks a different question: whether those semantics can first be expressed as interpreted context and then reconstructed.

---

## Stage A: Direct Semantic Interpretation

### Model

`MODEL A`

### Source Input

```text
PASTE SOURCE EVENT OR SELECTED SOURCE PASSAGE
```

### Interpretation Prompt

```text
Interpret the context below as a semantic representation.

Do not summarize it for a human reader.

Preserve the semantic information explicitly supported by the context.

Identify the entities and describe the meaningful semantic facts associated
with them in natural language.

Preserve distinctions between entities.

Preserve ambiguity, uncertainty, qualification, attribution, belief,
state, action, role, context, and other semantic information when present.

Do not invent information.

Do not infer relationships merely because entities appear together.

Do not infer causality or temporal relationships unless explicitly supported.

Do not resolve ambiguity that the source does not resolve.

Do not create a fixed ontology.

Do not produce the final entity-dimension JSON.

Return an interpreted semantic representation in natural language.

Context:

{{SOURCE}}
```

### Raw Interpretation

```text
PASTE LLM A OUTPUT
```

### Interpretation Notes

```text
-
-
-
```

---

# Stage B: Reconstruction

## Model

`MODEL B`

## Input

The ONLY input available to Model B is the interpreted context produced by Model A.

```text
PASTE STAGE A INTERPRETED CONTEXT
```

## Reconstruction Prompt

Use:

`BabyTest/ndm_reconstruction_prompt_v1.md`

### Raw Reconstruction

```text
PASTE LLM B OUTPUT
```

### Parsed Reconstruction

```json
PASTE PARSED JSON
```

---

# Stage C: Independent Direct Extraction Reference

This stage is NOT provided to Model B.

It exists only for post-hoc analysis.

The direct extraction result from the previous reliability experiment may be used as one reference point.

## Direct Extraction Model

`MODEL`

## Direct Extraction Output

```json
PASTE PREVIOUS DIRECT ENTITY-DIMENSION OUTPUT
```

---

# Reconstruction Analysis

## Entity Recovery

| Entity | Present in Source | Present in Interpretation | Present in Reconstruction |
|---|---|---|---|
| | | | |
| | | | |

### Missing Entities

```text
-
```

### Added Entities

```text
-
```

---

## Dimension Recovery

Dimensions are compared by meaning, not by exact dimension-name matching.

| Entity | Source Semantic Information | Interpretation | Reconstruction | Preserved |
|---|---|---|---|---|
| | | | | |
| | | | | |

---

## Semantic Loss

Information present in the source or interpretation but absent from the reconstruction.

```text
-
-
-
```

---

## Semantic Addition

Information introduced by the reconstruction that was not supported by the interpreted context.

```text
-
-
-
```

---

## Semantic Drift

Meaning changed during:

```text
Source → Interpretation
```

or:

```text
Interpretation → Reconstruction
```

### Observed Drift

```text
-
-
-
```

### First Stage Where Drift Appeared

`SOURCE / INTERPRETATION / RECONSTRUCTION`

---

## Ambiguity Preservation

### Source Ambiguity

```text
-
```

### Interpretation

```text
-
```

### Reconstruction

```text
-
```

### Preserved?

`YES / PARTIAL / NO`

---

## Unsupported Inference

Did the reconstruction introduce information that was not represented in the interpreted context?

`YES / NO`

### Details

```text
-
-
-
```

---

# Key Measurement

## Semantic Recoverability

`HIGH / MEDIUM / LOW`

### Reason

```text
-
-
-
```

---

## Reconstruction Result

`SUCCESS / PARTIAL / FAILURE`

### Why

```text
-
-
-
```

---

# Chain Extension

If Stage B succeeds, the same reconstructed representation can optionally be passed to another LLM.

```text
Source
  |
  v
Interpretation A
  |
  v
Reconstruction B
  |
  v
Reinterpretation C
  |
  v
Reconstruction D
```

The original source must remain unavailable to later stages.

---

# Extended Chain Results

| Stage | Model | Input Type | Entities Preserved | Semantic Loss | Unsupported Addition |
|---|---|---|---:|---|---|
| A | | Source | | | |
| B | | Interpretation | | | |
| C | | Reconstruction | | | |
| D | | Reconstruction | | | |

---

# Final Findings

## What Survived

```text
-
-
-
```

## What Was Lost

```text
-
-
-
```

## What Was Invented

```text
-
-
-
```

## What Became Ambiguous

```text
-
-
-
```

## Most Important Observation

```text
-
```

---

# Experiment Conclusion

### Hypothesis Status

`SUPPORTED / PARTIALLY SUPPORTED / NOT SUPPORTED`

### Conclusion

```text
-
-
-
```

---

# Important Constraint

This experiment does NOT establish that the reconstructed representation is a correct NDM implementation.

It only tests whether semantic information can survive the transformation:

```text
source context
    ↓
semantic interpretation
    ↓
entity + dimension reconstruction
```

The later NDM system is responsible for computational treatment of the resulting observations.
