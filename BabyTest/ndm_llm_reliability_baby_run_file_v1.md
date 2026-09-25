## Hypothesis
Current general-purpose LLMs are sufficiently capable of identifying entities and relevant semantic dimensions from natural-language events that a lightweight extraction interface may be sufficient for constructing an N-dimensional memory representation, without requiring the model to directly generate the complete NDM storage structure.

## Test 001
Single Event

### Input
/Users/xxvirusxx/PY/BabyAI/N-Dimensional-Memory/BabyTest/2601.14952v2.pdf

### Model
Gemini Flash 3.8

### Prompt
Analyze the event below.

First identify every entity explicitly present in the event.

For each entity, determine the semantic dimensions that are relevant
to understanding that entity within this specific event.

A dimension should describe something meaningful about the entity,
such as its role, state, action, relationship, context, ownership,
status, temporal position, belief, or other relevant characteristic.

Do not use a fixed dimension vocabulary.
Create dimension names that best describe the information present.

Do not invent information that is not supported by the event.
Do not infer relationships merely because two entities appear together.
Do not resolve ambiguity that the event itself does not resolve.

Return ONLY valid JSON in this structure:

{
  "entities": [
    {
      "name": "...",
      "dimensions": {
        "dimension_name": "value"
      }
    }
  ]
}

Event:

/Users/xxvirusxx/PY/BabyAI/N-Dimensional-Memory/BabyTest/2601.14952v2.pdf

### Raw Output
```json
{
  "entities": [
    {
      "name": "Zhiyuan Lu",
      "dimensions": {
        "entity_type": "Person / Researcher",
        "affiliation": "Tongyi Lab, Alibaba Group",
        "author_order": "First author",
        "role": "Corresponding author",
        "contact_email": "zylu734@gmail.com"
      }
    },
    {
      "name": "Chenliang Li",
      "dimensions": {
        "entity_type": "Person / Researcher",
        "affiliation": "Tongyi Lab, Alibaba Group",
        "role": "Co-author"
      }
    },
    {
      "name": "Yingcheng Shi",
      "dimensions": {
        "entity_type": "Person / Researcher",
        "affiliation": "Tongyi Lab, Alibaba Group",
        "role": "Co-author"
      }
    },
    {
      "name": "Weizhou Shen",
      "dimensions": {
        "entity_type": "Person / Researcher",
        "affiliation": "Tongyi Lab, Alibaba Group",
        "role": "Co-author"
      }
    },
    {
      "name": "Ming Yan",
      "dimensions": {
        "entity_type": "Person / Researcher",
        "affiliation": "Tongyi Lab, Alibaba Group",
        "role": "Corresponding author and co-author",
        "contact_email": "ym119608@alibaba-inc.com"
      }
    },
    {
      "name": "Fei Huang",
      "dimensions": {
        "entity_type": "Person / Researcher",
        "affiliation": "Tongyi Lab, Alibaba Group",
        "role": "Co-author"
      }
    },
    {
      "name": "Tongyi Lab",
      "dimensions": {
        "entity_type": "Research Laboratory / Organization",
        "parent_organization": "Alibaba Group",
        "role": "Author institutional affiliation"
      }
    },
    {
      "name": "Alibaba Group",
      "dimensions": {
        "entity_type": "Company / Enterprise",
        "role": "Parent organization of Tongyi Lab"
      }
    },
    {
      "name": "CorpusQA",
      "dimensions": {
        "entity_type": "Benchmark dataset and framework",
        "purpose": "Evaluating corpus-level analysis and long-context reasoning",
        "token_scale": "Up to 10 million tokens",
        "evaluation_settings": "Set1 (128K), Set2 (1M), Set3 (4M), Set4 (10M)",
        "domains_covered": "Financial (zh, en), Education (en), Real Estate (en)",
        "difficulty_levels": "Easy, Medium, Hard",
        "methodology": "Decoupling reasoning from textual representation via schema extraction, query templates, data table aggregation, and NL2SQL execution",
        "status": "Introduced in the paper"
      }
    },
    {
      "name": "InfiniteBench",
      "dimensions": {
        "entity_type": "Long-context benchmark",
        "token_limit": "Does not reach 10M",
        "reasoning_intensive": "No (marked as X)",
        "controllable_context": "No (marked as X)",
        "evidence_dispersion": "No high dispersion (marked as X)",
        "role": "Baseline / Prior work compared in Table 1 and Section 2.2"
      }
    },
    {
      "name": "LongBench v2",
      "dimensions": {
        "entity_type": "Long-context benchmark",
        "token_limit": "Does not reach 10M",
        "reasoning_intensive": "Reasoning-intensive (marked as checkmark)",
        "controllable_context": "No (marked as X)",
        "evidence_dispersion": "No high dispersion (marked as X)",
        "role": "Baseline / Prior work evaluated for out-of-domain transfer"
      }
    },
    {
      "name": "Loong",
      "dimensions": {
        "entity_type": "Multi-document QA benchmark",
        "role": "Prior work compared in Table 1 and Section 2.2",
        "context_scale": "Operates at smaller scale (<10M tokens)"
      }
    },
    {
      "name": "FanOutQA",
      "dimensions": {
        "entity_type": "Multi-document QA benchmark",
        "role": "Prior work compared in Table 1 and Section 2.2",
        "context_scale": "Operates at smaller scale (<10M tokens)"
      }
    },
    {
      "name": "FRAMES",
      "dimensions": {
        "entity_type": "RAG benchmark",
        "reasoning_intensive": "Reasoning-intensive (marked as checkmark)",
        "role": "Prior work compared in Table 1 and evaluated for out-of-domain generalization"
      }
    },
    {
      "name": "CRAG",
      "dimensions": {
        "entity_type": "RAG benchmark",
        "role": "Prior work compared in Table 1 and Section 2.1"
      }
    },
    {
      "name": "Gemini 2.5 Pro",
      "dimensions": {
        "entity_type": "Large Language Model",
        "access_type": "Closed-source model",
        "role_in_pipeline": "Model used in multi-model voting for schema extraction; base model for memory agent and direct testing",
        "performance": "80.19% overall at 128K; 50.73% overall at 1M"
      }
    },
    {
      "name": "GPT-4.1",
      "dimensions": {
        "entity_type": "Large Language Model",
        "developer": "OpenAI",
        "role_in_pipeline": "Model used in multi-model voting ensemble for schema extraction (Step 2)"
      }
    },
    {
      "name": "Qwen-Max",
      "dimensions": {
        "entity_type": "Large Language Model",
        "developer": "Alibaba (Qwen Team)",
        "role_in_pipeline": "Model used in multi-model voting ensemble for schema extraction (Step 2)"
      }
    },
    {
      "name": "Gemini-2.5-Flash",
      "dimensions": {
        "entity_type": "Large Language Model",
        "access_type": "Closed-source model",
        "performance": "77.81% overall at 128K; 37.31% overall at 1M"
      }
    },
    {
      "name": "GPT-5",
      "dimensions": {
        "entity_type": "Large Language Model",
        "access_type": "Closed-source model",
        "version_tag": "GPT-5-2025-08-07",
        "performance": "82.02% overall at 128K"
      }
    },
    {
      "name": "GPT-5-Mini",
      "dimensions": {
        "entity_type": "Large Language Model",
        "access_type": "Closed-source model",
        "version_tag": "GPT-5-Mini-2025-08-07",
        "performance": "79.88% overall at 128K"
      }
    },
    {
      "name": "Qwen3-235B-A22B-Thinking",
      "dimensions": {
        "entity_type": "Large Language Model",
        "access_type": "Open-source reasoning model",
        "performance": "78.08% overall at 128K"
      }
    },
    {
      "name": "Qwen3-30B-A3B-Thinking",
      "dimensions": {
        "entity_type": "Large Language Model",
        "access_type": "Open-source reasoning model",
        "performance": "69.59% overall at 128K; 66.7% in human vs AI study (128K)"
      }
    },
    {
      "name": "Qwen3-235B-Instruct",
      "dimensions": {
        "entity_type": "Large Language Model",
        "alignment_type": "Instruction-tuned model",
        "performance": "61.41% overall at 128K"
      }
    },
    {
      "name": "Qwen3-30B-Instruct",
      "dimensions": {
        "entity_type": "Large Language Model",
        "alignment_type": "Instruction-tuned model",
        "role": "Comparative baseline against Qwen3-30B-Thinking in Figure 4"
      }
    },
    {
      "name": "DeepSeek-R1-0528",
      "dimensions": {
        "entity_type": "Large Language Model",
        "access_type": "Open-source model",
        "performance": "74.72% overall at 128K"
      }
    },
    {
      "name": "MiniMax-M1-80k",
      "dimensions": {
        "entity_type": "Large Language Model",
        "access_type": "Open-source model",
        "performance": "71.02% overall at 128K; 11.63% overall at 1M"
      }
    },
    {
      "name": "DeepSeek-V3",
      "dimensions": {
        "entity_type": "Large Language Model",
        "role": "Judge model in LLM-as-a-Judge evaluation framework"
      }
    },
    {
      "name": "Qwen3-4B-Thinking",
      "dimensions": {
        "entity_type": "Large Language Model",
        "access_type": "Open-source model",
        "role": "Target model for fine-tuning experiment via GRPO on synthesized CorpusQA data"
      }
    },
    {
      "name": "MemAgent-14B",
      "dimensions": {
        "entity_type": "Specialist agent model",
        "role": "Memory agent architecture implementation evaluated on ultra-long contexts"
      }
    },
    {
      "name": "Apple Inc.",
      "dimensions": {
        "entity_type": "Commercial company / Enterprise",
        "role": "Subject entity in example question ('What is the revenue of Apple Inc.?') in Figure 1"
      }
    },
    {
      "name": "NETFLIX INC",
      "dimensions": {
        "entity_type": "Commercial company / Enterprise",
        "role": "Example entity value in answer format template (Appendix C)"
      }
    },
    {
      "name": "H&R BLOCK INC",
      "dimensions": {
        "entity_type": "Commercial company / Enterprise",
        "role": "Example entity value in answer format template (Appendix C)"
      }
    }
  ]
}

```
### Parsed Output
...

### Expected Entities
...

### Expected Dimensions
...

### Observations
...

### Errors
...

### Output Format
STRUCTURED

### Parseable
YES 

### Semantic Accuracy
...

### Missing Dimensions
...

### Hallucinated Entities
...

### Hallucinated Relationships
...

### Notes
...

## Test 002
Single Event

### Input
/Users/xxvirusxx/PY/BabyAI/N-Dimensional-Memory/BabyTest/2601.14952v2.pdf

### Model
Claude Opus 5.5

### Prompt
Analyze the event below.

First identify every entity explicitly present in the event.

For each entity, determine the semantic dimensions that are relevant
to understanding that entity within this specific event.

A dimension should describe something meaningful about the entity,
such as its role, state, action, relationship, context, ownership,
status, temporal position, belief, or other relevant characteristic.

Do not use a fixed dimension vocabulary.
Create dimension names that best describe the information present.

Do not invent information that is not supported by the event.
Do not infer relationships merely because two entities appear together.
Do not resolve ambiguity that the event itself does not resolve.

Return ONLY valid JSON in this structure:

{
  "entities": [
    {
      "name": "...",
      "dimensions": {
        "dimension_name": "value"
      }
    }
  ]
}

Event:

/Users/xxvirusxx/PY/BabyAI/N-Dimensional-Memory/BabyTest/2601.14952v2.pdf

### Raw Output
```json
{
  "entities": [
    {
      "name": "CorpusQA",
      "dimensions": {
        "type": "benchmark for corpus-level analysis and reasoning",
        "max_scale": "up to 10 million tokens",
        "creators": "Zhiyuan Lu, Chenliang Li, Yingcheng Shi, Weizhou Shen, Ming Yan, Fei Huang (Tongyi Lab, Alibaba Group)",
        "publication": "arXiv:2601.14952v2 [cs.CL], 25 Apr 2026",
        "core_design_principles": "unprecedented scale and complexity; high information dispersion; guaranteed factual grounding",
        "claimed_novelty": "first benchmark designed for large-scale corpus-level analysis",
        "domains": "Financial (ZH, EN; 664 instances; avg 2.71M tokens), Education (EN; 328; avg 3.12M), Real Estate (EN; 324; avg 3.59M)",
        "length_sets": "Set1 128K (avg 92.5K), Set2 1M (avg 905K), Set3 4M (avg 3.71M), Set4 10M (avg 7.84M); 329 instances each",
        "difficulty_distribution": "Easy 296, Medium 648, Hard 372",
        "instance_structure": "triplet of concatenated document corpus, natural language query, programmatically derived ground-truth answer",
        "answer_formats": "list of strings, single short string, number (2 decimals), percentage (2 decimals), date as YYYY-MM",
        "conflict_rule_in_prompt": "use value from the latest file when files conflict",
        "evaluation_metric": "accuracy judged by LLM-as-a-Judge (DeepSeek-V3)",
        "stated_limitations": "LLM-as-a-Judge less deterministic than rule-based; deep-research agentic architectures not evaluated",
        "comparison_claim": "only benchmark in Table 1 checking all of: 10M length, reasoning intensive, controllable context, high evidence dispersion, multilingual"
      }
    },
    {
      "name": "CorpusQA data synthesis framework",
      "dimensions": {
        "role": "pipeline generating CorpusQA questions and verifiable answers",
        "core_mechanism": "decouples reasoning from textual representation by structuring information, computing answers programmatically, then re-presenting original unstructured documents",
        "stages": "1 document collection, 2 schema extraction, 3 query generation, 4 data table aggregation, 5 NL2SQL execution, 6 long-context QA pair assembly",
        "claimed_accuracy": "100% factual accuracy and logical consistency of ground truth",
        "secondary_use": "generating training data that improves long-context reasoning"
      }
    },
    {
      "name": "Document Collection (Step 1)",
      "dimensions": {
        "source_material": "real-world PDF documents from domains such as finance and academia",
        "processing": "PDFs parsed into Markdown",
        "filter_1": "discard documents with fewer than 10,240 tokens",
        "filter_2": "retain only documents with rich statistical tables and numerical data"
      }
    },
    {
      "name": "Schema Extraction (Step 2)",
      "dimensions": {
        "method": "multi-model voting; each model queried multiple times per target field",
        "ensemble_models": "Gemini 2.5 Pro, GPT-4.1, Qwen-Max",
        "validity_rule": "value valid only if clear majority across all extraction results",
        "failure_handling": "documents failing consensus on any field are discarded",
        "output": "validated key-value pairs in consistent JSON-based schema",
        "verification_sample": "1,000 schemas per domain for education_en and financial_zh",
        "human_consistency": "94.13% education_en; 98.97% financial_zh",
        "disagreement_resolution": "secondary human review found LLM extraction correct in every disagreement",
        "exempt_domains": "financial_en and real_estate_en, derived from structured sources"
      }
    },
    {
      "name": "Query Generation (Step 3)",
      "dimensions": {
        "method": "manually authored templates expanded and paraphrased by an LLM",
        "reasoning_patterns": "comparison, ranking, conditional filtering, multi-step calculations",
        "example_template": "List the companies where their basic earnings per share is higher than their diluted earnings per share.",
        "purpose_of_paraphrasing": "increase linguistic diversity and prevent overfitting to phrasings",
        "difficulty_categorization": "Easy, Medium, Hard by logical and computational complexity"
      }
    },
    {
      "name": "Data Table Aggregation (Step 4)",
      "dimensions": {
        "input": "structured JSON objects from every document in a corpus",
        "output": "single global data table; rows are entities, columns are schema attributes",
        "role": "canonical structured knowledge base for the document set"
      }
    },
    {
      "name": "NL2SQL Execution (Step 5)",
      "dimensions": {
        "method": "LLM translates natural language query into SQL executed against aggregated table",
        "example_sql": "SELECT company_name FROM financials WHERE basic_eps > diluted_eps;",
        "role": "programmatic ground-truth generation"
      }
    },
    {
      "name": "Long Context QA Pair (Step 6)",
      "dimensions": {
        "method": "full-text Markdown documents concatenated in entirety as context",
        "prompt_format": "# Document N: sections, then # Question, then output requirements; final answer as 'The answer is: xxx'"
      }
    },
    {
      "name": "Easy difficulty level",
      "dimensions": {
        "definition": "basic aggregation and single-dimension analysis",
        "subtypes": "simple aggregation, single-condition filtering, basic ranking",
        "example": "List the top 5 universities with the highest total enrollment."
      }
    },
    {
      "name": "Medium difficulty level",
      "dimensions": {
        "definition": "numerical calculation and multi-condition analysis",
        "subtypes": "ratio calculation, multi-condition combination, simple custom metrics, grouped comparison",
        "example": "Which universities have a graduation rate above 90% and fewer than 5,000 undergraduate students?"
      }
    },
    {
      "name": "Hard difficulty level",
      "dimensions": {
        "definition": "custom metrics and multi-step reasoning",
        "subtypes": "multi-step calculation, complex business logic, advanced metric construction",
        "example": "Identify companies where (X1×1.2 + X2×1.4 + X3×3.3) < 1.8 with X1, X2, X3 defined as balance-sheet ratios"
      }
    },
    {
      "name": "Corpus-Level Analysis",
      "dimensions": {
        "definition": "reasoning over a collection of hundreds or thousands of documents to uncover insights visible only at corpus level",
        "defining_characteristic": "high dispersion of evidence across the repository",
        "requirements": "holistic processing of complete ultra-long context, complex reasoning, statistical aggregation, precise computation",
        "example_domains": "finance, law, scientific research",
        "example_task": "How many companies generated more net cash from financing activities than from operating activities?"
      }
    },
    {
      "name": "Sparse retrieval assumption",
      "dimensions": {
        "definition": "answers can be derived from a few relevant chunks",
        "held_by": "existing RAG benchmarks such as FRAMES and CRAG",
        "status_in_paper": "claimed invalid for corpus-level analysis"
      }
    },
    {
      "name": "Retrieval-Augmented Generation (RAG) - Gemini-2.5-Pro",
      "dimensions": {
        "role": "system-level baseline for ultra-long contexts",
        "mechanism": "segment corpus into chunks, retrieve small subset, generate from retrieved evidence and query",
        "accuracy_by_scale": "128K 55.85; 1M 17.38; 4M 2.43; 10M 1.20",
        "failure_note": "several 4M/10M cases retrieved fewer chunks than documents, making accurate answers impossible",
        "paper_characterization": "collapses catastrophically; cannot gather globally distributed evidence"
      }
    },
    {
      "name": "Memory Agent - Gemini-2.5-Pro",
      "dimensions": {
        "role": "memory-augmented agentic system evaluated on CorpusQA",
        "framework_source": "Memory Agent framework by Yu et al. (2025)",
        "mechanism": "processes document in chunks, iteratively updates fixed-size memory buffer, answers solely from consolidated memory",
        "tuning": "general-purpose LLM instructed to follow workflow without task-specific tuning",
        "accuracy_by_scale": "128K 67.58; 1M 44.95; 4M 22.14; 10M 11.13",
        "paper_characterization": "more resilient than RAG but far from solving the task"
      }
    },
    {
      "name": "MemAgent-14B",
      "dimensions": {
        "role": "specialist model fine-tuned for the Memory Agent workflow by Yu et al. (2025)",
        "evaluation_status": "listed as evaluated implementation; results not reported in provided tables"
      }
    },
    {
      "name": "Memory Agent - Qwen3-30B-A3B-Thinking",
      "dimensions": {
        "role": "AI system in human-performance comparison",
        "accuracy_by_scale": "128K 50.0; 1M 33.3; 4M 25.0; 10M 16.7",
        "avg_time_minutes": "128K 1.4; 1M 69.7; 4M 323.5; 10M 789.3",
        "timeout_rate": "0% at all scales",
        "paper_characterization": "only viable approach at 4M and 10M in the human study"
      }
    },
    {
      "name": "Human expert",
      "dimensions": {
        "role": "human baseline in difficulty study",
        "sample": "12 QA pairs per scale",
        "time_limit": "90 minutes per task",
        "accuracy_by_scale": "128K 75.0; 1M 50.0; 4M 0.0; 10M 0.0",
        "avg_time_minutes": "128K 17.8; 1M 31.9",
        "timeout_rate": "128K 6.6%; 1M 33.3%; 4M 100%; 10M 100%"
      }
    },
    {
      "name": "Gemini-2.5-Pro",
      "dimensions": {
        "developer_reference": "Comanici et al. (2025)",
        "source_type": "closed-source",
        "roles": "evaluated base LLM; schema extraction ensemble member; backbone of Memory Agent and RAG systems",
        "accuracy_128k": "80.19 overall (Fin-zh 89.16, Fin-en 80.72, Edu-en 76.83, RE-en 74.07)",
        "accuracy_1m": "50.73 overall (Fin-zh 50.60, Fin-en 48.19, Edu-en 65.85, RE-en 38.27)",
        "paper_characterization": "shows partial resilience at million-token scale"
      }
    },
    {
      "name": "Gemini-2.5-Flash",
      "dimensions": {
        "source_type": "closed-source",
        "accuracy_128k": "77.81 overall",
        "accuracy_1m": "37.31 overall"
      }
    },
    {
      "name": "GPT-5",
      "dimensions": {
        "version": "GPT-5-2025-08-07",
        "source_type": "closed-source",
        "accuracy_128k": "82.02 overall (highest at 128K)",
        "tested_at_1m": "no"
      }
    },
    {
      "name": "GPT-5-Mini",
      "dimensions": {
        "version": "GPT-5-Mini-2025-08-07",
        "source_type": "closed-source",
        "accuracy_128k": "79.88 overall"
      }
    },
    {
      "name": "Qwen3-235B-A22B-Thinking",
      "dimensions": {
        "source_type": "open-source",
        "accuracy_128k": "78.08 overall",
        "comparison": "outperforms Qwen3-235B-Instruct (61.41) at 128K"
      }
    },
    {
      "name": "Qwen3-235B-Instruct",
      "dimensions": {
        "source_type": "open-source",
        "model_type": "instruction-tuned",
        "accuracy_128k": "61.41 overall (Fin-zh 62.6, Fin-en 62.6, Edu-en 53.7, RE-en 66.7)"
      }
    },
    {
      "name": "Qwen3-30B-A3B-Thinking",
      "dimensions": {
        "source_type": "open-source",
        "accuracy_128k": "69.59 overall",
        "roles": "evaluated base LLM; base LLM and Memory Agent backbone in human study",
        "human_study_base_llm_results": "128K 66.7% in 2.1 min; 1M 20.0% in 120.7 min; 4M/10M context limit exceeded"
      }
    },
    {
      "name": "Qwen3-30B Instruct",
      "dimensions": {
        "model_type": "instruction-tuned",
        "accuracy_128k_figure4": "Fin-zh 14.5, Fin-en 21.7, Edu-en 20.7, RE-en 53.1"
      }
    },
    {
      "name": "DeepSeek-R1-0528",
      "dimensions": {
        "source_type": "open-source",
        "accuracy_128k": "74.72 overall"
      }
    },
    {
      "name": "MiniMax-M1-80k",
      "dimensions": {
        "source_type": "open-source",
        "accuracy_128k": "71.02 overall",
        "accuracy_1m": "11.63 overall",
        "paper_characterization": "collapses at 1M"
      }
    },
    {
      "name": "Qwen3-4B-Thinking",
      "dimensions": {
        "role": "model fine-tuned in pilot training experiment",
        "training_data": "480 samples synthesized by CorpusQA framework",
        "training_method": "GRPO for 25 steps",
        "longbench_v2": "39.36 → 42.35",
        "frames": "63.23 → 65.53",
        "corpusqa": "55.00 → 60.31",
        "paper_characterization": "gains generalize to out-of-domain long-context benchmarks"
      }
    },
    {
      "name": "Group Relative Policy Optimization (GRPO)",
      "dimensions": {
        "role": "fine-tuning algorithm used in pilot experiment",
        "reference": "Shao et al. (2024)"
      }
    },
    {
      "name": "DeepSeek-V3",
      "dimensions": {
        "role": "LLM-as-a-Judge model",
        "judging_criterion": "semantic equivalence between prediction and ground truth, output [[YES]] or [[NO]]"
      }
    },
    {
      "name": "GPT-4.1",
      "dimensions": {
        "role": "schema extraction ensemble member"
      }
    },
    {
      "name": "Qwen-Max",
      "dimensions": {
        "role": "schema extraction ensemble member",
        "version": "snapshot 2025-01-25"
      }
    },
    {
      "name": "LongBench v2",
      "dimensions": {
        "role": "prior benchmark compared against; out-of-domain eval in training experiment",
        "category": "single concatenated long-text evaluation",
        "table1_features": "reasoning intensive, multilingual; not 10M, not controllable, not high dispersion"
      }
    },
    {
      "name": "InfiniteBench",
      "dimensions": {
        "role": "prior benchmark compared against",
        "category": "single concatenated long-text evaluation",
        "table1_features": "multilingual only"
      }
    },
    {
      "name": "Loong",
      "dimensions": {
        "role": "prior multi-document QA benchmark",
        "limitation_stated": "typically fewer than a dozen documents; fits within modern LLM context",
        "table1_features": "controllable context, high dispersion, multilingual"
      }
    },
    {
      "name": "FanOutQA",
      "dimensions": {
        "role": "prior multi-document QA benchmark",
        "limitation_stated": "typically fewer than a dozen documents",
        "table1_features": "controllable context, high dispersion; not multilingual"
      }
    },
    {
      "name": "FRAMES",
      "dimensions": {
        "role": "prior RAG benchmark; out-of-domain eval in training experiment",
        "focus": "multi-hop reasoning over structured and unstructured knowledge bases",
        "table1_features": "reasoning intensive only"
      }
    },
    {
      "name": "CRAG",
      "dimensions": {
        "role": "prior RAG benchmark",
        "focus": "dynamic RAG evaluation including self-correction and web search",
        "table1_features": "none of the five features"
      }
    },
    {
      "name": "Tongyi Lab, Alibaba Group",
      "dimensions": {
        "role": "authoring institution"
      }
    }
  ]
}
```
### Parsed Output
...

### Expected Entities
...

### Expected Dimensions
...

### Observations
...

### Errors
...

### Output Format
STRUCTURED

### Parseable
YES 

### Semantic Accuracy
...

### Missing Dimensions
...

### Hallucinated Entities
...

### Hallucinated Relationships
...

### Notes
...

## Test 003
Single Event

### Input
/Users/xxvirusxx/PY/BabyAI/N-Dimensional-Memory/BabyTest/2601.14952v2.pdf

### Model
Grok

### Prompt
Analyze the event below.

First identify every entity explicitly present in the event.

For each entity, determine the semantic dimensions that are relevant
to understanding that entity within this specific event.

A dimension should describe something meaningful about the entity,
such as its role, state, action, relationship, context, ownership,
status, temporal position, belief, or other relevant characteristic.

Do not use a fixed dimension vocabulary.
Create dimension names that best describe the information present.

Do not invent information that is not supported by the event.
Do not infer relationships merely because two entities appear together.
Do not resolve ambiguity that the event itself does not resolve.

Return ONLY valid JSON in this structure:

{
  "entities": [
    {
      "name": "...",
      "dimensions": {
        "dimension_name": "value"
      }
    }
  ]
}

Event:

/Users/xxvirusxx/PY/BabyAI/N-Dimensional-Memory/BabyTest/2601.14952v2.pdf

### Raw Output
{
  "entities": [
    {
      "name": "CorpusQA",
      "dimensions": {
        "type": "benchmark",
        "scale": "up to 10 million tokens",
        "purpose": "corpus-level analysis and reasoning",
        "key_features": "high evidence dispersion, reasoning intensive, controllable context, multilingual",
        "generation_method": "novel data synthesis framework with programmatic ground-truth answers"
      }
    },
    {
      "name": "Zhiyuan Lu",
      "dimensions": {
        "role": "author",
        "affiliation": "Tongyi Lab, Alibaba Group",
        "contact": "zylu734@gmail.com"
      }
    },
    {
      "name": "Chenliang Li",
      "dimensions": {
        "role": "author",
        "affiliation": "Tongyi Lab, Alibaba Group"
      }
    },
    {
      "name": "Yingcheng Shi",
      "dimensions": {
        "role": "author",
        "affiliation": "Tongyi Lab, Alibaba Group"
      }
    },
    {
      "name": "Weizhou Shen",
      "dimensions": {
        "role": "author",
        "affiliation": "Tongyi Lab, Alibaba Group"
      }
    },
    {
      "name": "Ming Yan",
      "dimensions": {
        "role": "author",
        "affiliation": "Tongyi Lab, Alibaba Group",
        "contact": "ym119608@alibaba-inc.com"
      }
    },
    {
      "name": "Fei Huang",
      "dimensions": {
        "role": "author",
        "affiliation": "Tongyi Lab, Alibaba Group"
      }
    },
    {
      "name": "Tongyi Lab",
      "dimensions": {
        "type": "organization",
        "parent": "Alibaba Group"
      }
    },
    {
      "name": "Alibaba Group",
      "dimensions": {
        "type": "organization"
      }
    },
    {
      "name": "InfiniteBench",
      "dimensions": {
        "type": "benchmark",
        "comparison": "lacks high evidence dispersion and controllable context relative to CorpusQA"
      }
    },
    {
      "name": "LongBench v2",
      "dimensions": {
        "type": "benchmark",
        "comparison": "lacks up to 10M length and high evidence dispersion relative to CorpusQA"
      }
    },
    {
      "name": "Loong",
      "dimensions": {
        "type": "benchmark",
        "comparison": "lacks up to 10M length relative to CorpusQA"
      }
    },
    {
      "name": "FanOutQA",
      "dimensions": {
        "type": "benchmark",
        "comparison": "lacks up to 10M length and multilingual support relative to CorpusQA"
      }
    },
    {
      "name": "FRAMES",
      "dimensions": {
        "type": "benchmark",
        "comparison": "lacks up to 10M length, controllable context, and high evidence dispersion relative to CorpusQA"
      }
    },
    {
      "name": "CRAG",
      "dimensions": {
        "type": "benchmark",
        "comparison": "lacks up to 10M length, reasoning intensive, controllable context, and high evidence dispersion relative to CorpusQA"
      }
    },
    {
      "name": "Gemini-2.5-Pro",
      "dimensions": {
        "type": "large language model",
        "performance_128K": "80.19 overall accuracy",
        "performance_1M": "50.73 overall accuracy",
        "used_in": "base LLM evaluation, Memory Agent, RAG"
      }
    },
    {
      "name": "Gemini-2.5-Flash",
      "dimensions": {
        "type": "large language model",
        "performance_128K": "77.81 overall accuracy",
        "performance_1M": "37.31 overall accuracy"
      }
    },
    {
      "name": "GPT-5",
      "dimensions": {
        "type": "large language model",
        "performance_128K": "82.02 overall accuracy"
      }
    },
    {
      "name": "GPT-5-Mini",
      "dimensions": {
        "type": "large language model",
        "performance_128K": "79.88 overall accuracy"
      }
    },
    {
      "name": "Qwen3-235B-A22B-Thinking",
      "dimensions": {
        "type": "large language model",
        "performance_128K": "78.08 overall accuracy"
      }
    },
    {
      "name": "Qwen3-30B-A3B-Thinking",
      "dimensions": {
        "type": "large language model",
        "performance_128K": "69.59 overall accuracy"
      }
    },
    {
      "name": "DeepSeek-R1-0528",
      "dimensions": {
        "type": "large language model",
        "performance_128K": "74.72 overall accuracy"
      }
    },
    {
      "name": "MiniMax-M1-80k",
      "dimensions": {
        "type": "large language model",
        "performance_128K": "71.02 overall accuracy",
        "performance_1M": "11.63 overall accuracy"
      }
    },
    {
      "name": "Memory Agent",
      "dimensions": {
        "type": "system architecture",
        "base_model": "Gemini-2.5-Pro",
        "performance_128K": "67.58 overall accuracy",
        "performance_1M": "44.95 overall accuracy",
        "performance_4M": "22.14 overall accuracy",
        "performance_10M": "11.13 overall accuracy",
        "characteristic": "more resilient than RAG on high evidence dispersion tasks"
      }
    },
    {
      "name": "RAG",
      "dimensions": {
        "type": "system architecture",
        "base_model": "Gemini-2.5-Pro",
        "performance_128K": "55.85 overall accuracy",
        "performance_1M": "17.38 overall accuracy",
        "performance_4M": "2.43 overall accuracy",
        "performance_10M": "1.20 overall accuracy",
        "characteristic": "collapses on high evidence dispersion tasks"
      }
    },
    {
      "name": "Financial domain",
      "dimensions": {
        "average_tokens": "2.71M",
        "languages": "ZH, EN",
        "instances": "664"
      }
    },
    {
      "name": "Education domain",
      "dimensions": {
        "average_tokens": "3.12M",
        "language": "EN",
        "instances": "328"
      }
    },
    {
      "name": "Real Estate domain",
      "dimensions": {
        "average_tokens": "3.59M",
        "language": "EN",
        "instances": "324"
      }
    },
    {
      "name": "Set1 (128K)",
      "dimensions": {
        "average_tokens": "92.5K",
        "languages": "EN, ZH",
        "instances": "329"
      }
    },
    {
      "name": "Set2 (1M)",
      "dimensions": {
        "average_tokens": "905K",
        "languages": "EN, ZH",
        "instances": "329"
      }
    },
    {
      "name": "Set3 (4M)",
      "dimensions": {
        "average_tokens": "3.71M",
        "languages": "EN, ZH",
        "instances": "329"
      }
    },
    {
      "name": "Set4 (10M)",
      "dimensions": {
        "average_tokens": "7.84M",
        "languages": "EN, ZH",
        "instances": "329"
      }
    },
    {
      "name": "Qwen3-4B-Thinking",
      "dimensions": {
        "type": "large language model",
        "role": "fine-tuned with synthesized data from CorpusQA framework",
        "training": "25 steps with GRPO on 480 samples"
      }
    },
    {
      "name": "DeepSeek-V3",
      "dimensions": {
        "type": "large language model",
        "role": "LLM-as-a-Judge for evaluation"
      }
    }
  ]
}
### Parsed Output
...

### Expected Entities
...

### Expected Dimensions
...

### Observations
...

### Errors
...

### Output Format
STRUCTURED

### Parseable
YES 

### Semantic Accuracy
...

### Missing Dimensions
...

### Hallucinated Entities
...

### Hallucinated Relationships
...

### Notes
...

## Test 004
Single Event

### Input
/Users/xxvirusxx/PY/BabyAI/N-Dimensional-Memory/BabyTest/2601.14952v2.pdf

### Model
ChatGPT

### Prompt
Analyze the event below.

First identify every entity explicitly present in the event.

For each entity, determine the semantic dimensions that are relevant
to understanding that entity within this specific event.

A dimension should describe something meaningful about the entity,
such as its role, state, action, relationship, context, ownership,
status, temporal position, belief, or other relevant characteristic.

Do not use a fixed dimension vocabulary.
Create dimension names that best describe the information present.

Do not invent information that is not supported by the event.
Do not infer relationships merely because two entities appear together.
Do not resolve ambiguity that the event itself does not resolve.

Return ONLY valid JSON in this structure:

{
  "entities": [
    {
      "name": "...",
      "dimensions": {
        "dimension_name": "value"
      }
    }
  ]
}

Event:

/Users/xxvirusxx/PY/BabyAI/N-Dimensional-Memory/BabyTest/2601.14952v2.pdf

### Raw Output
{
"entities": [
{
"name": "CorpusQA",
"dimensions": {
"entity_type": "benchmark",
"purpose": "evaluates corpus-level analysis and reasoning",
"maximum_scale": "10 million tokens",
"evidence_characteristic": "highly dispersed across documents",
"reasoning_requirement": "global integration, comparison, statistical aggregation, and computation",
"data_generation": "programmatically synthesized",
"ground_truth": "programmatically generated and verifiable",
"language_coverage": "English and Chinese",
"domains": "financial, education, and real estate",
"context_lengths": "128K, 1M, 4M, and 10M tokens",
"difficulty_levels": "Easy, Medium, Hard"
}
},
{
"name": "Zhiyuan Lu",
"dimensions": {
"role": "author",
"affiliation": "Tongyi Lab, Alibaba Group"
}
},
{
"name": "Chenliang Li",
"dimensions": {
"role": "author",
"affiliation": "Tongyi Lab, Alibaba Group"
}
},
{
"name": "Yingcheng Shi",
"dimensions": {
"role": "author",
"affiliation": "Tongyi Lab, Alibaba Group"
}
},
{
"name": "Weizhou Shen",
"dimensions": {
"role": "author",
"affiliation": "Tongyi Lab, Alibaba Group"
}
},
{
"name": "Ming Yan",
"dimensions": {
"role": "author",
"affiliation": "Tongyi Lab, Alibaba Group"
}
},
{
"name": "Fei Huang",
"dimensions": {
"role": "author",
"affiliation": "Tongyi Lab, Alibaba Group"
}
},
{
"name": "Tongyi Lab",
"dimensions": {
"entity_type": "research laboratory",
"affiliation": "Alibaba Group"
}
},
{
"name": "Alibaba Group",
"dimensions": {
"entity_type": "organization",
"affiliation_context": "Tongyi Lab"
}
},
{
"name": "Corpus-Level Analysis",
"dimensions": {
"entity_type": "analysis paradigm",
"scope": "entire document repositories",
"evidence_distribution": "highly dispersed",
"processing_requirement": "holistic processing of complete context",
"reasoning_requirement": "complex reasoning and statistical aggregation"
}
},
{
"name": "Retrieval-Augmented Generation",
"dimensions": {
"entity_type": "system paradigm",
"abbreviation": "RAG",
"retrieval_assumption": "answers can be synthesized from a small number of relevant chunks",
"limitation_described": "insufficient for highly dispersed corpus-level evidence"
}
},
{
"name": "Large Language Models",
"dimensions": {
"entity_type": "model class",
"capability_context": "long-context processing and reasoning",
"evaluated_contexts": "128K and 1M tokens",
"observed_behavior": "performance degrades as context scale increases"
}
},
{
"name": "Memory Agents",
"dimensions": {
"entity_type": "agent architecture",
"purpose": "processing ultra-long text",
"memory_mechanism": "iteratively updates a fixed-size memory buffer",
"output_basis": "information consolidated in memory",
"evaluation_scope": "128K to 10M tokens"
}
},
{
"name": "InfiniteBench",
"dimensions": {
"entity_type": "long-context benchmark",
"context_focus": "single or concatenated long text",
"CorpusQA_comparison": "does not provide the same corpus-level scale and evidence dispersion"
}
},
{
"name": "LongBench v2",
"dimensions": {
"entity_type": "long-context benchmark",
"evaluation_focus": "long-context multitask reasoning",
"external_evaluation_use": "used to measure generalization of CorpusQA training"
}
},
{
"name": "Loong",
"dimensions": {
"entity_type": "multi-document benchmark",
"evaluation_focus": "reasoning across multiple documents",
"scale_characteristic": "smaller than CorpusQA"
}
},
{
"name": "FanOutQA",
"dimensions": {
"entity_type": "multi-hop multi-document QA benchmark",
"evaluation_focus": "reasoning across multiple documents",
"scale_characteristic": "typically fewer than a dozen documents"
}
},
{
"name": "FRAMES",
"dimensions": {
"entity_type": "RAG evaluation benchmark",
"evaluation_focus": "multi-hop reasoning over structured and unstructured knowledge",
"external_evaluation_use": "used to measure generalization of CorpusQA training"
}
},
{
"name": "CRAG",
"dimensions": {
"entity_type": "RAG benchmark",
"evaluation_focus": "dynamic RAG evaluation",
"capabilities_included": "self-correction and web search"
}
},
{
"name": "Gemini-2.5-Pro",
"dimensions": {
"entity_type": "language model",
"provider_context": "Google",
"evaluated_contexts": "128K and 1M tokens",
"role_in_experiments": "base LLM, Memory Agent foundation, and RAG foundation",
"128K_overall_accuracy": "80.19%",
"1M_overall_accuracy": "50.73%"
}
},
{
"name": "Gemini-2.5-Flash",
"dimensions": {
"entity_type": "language model",
"evaluated_contexts": "128K and 1M tokens",
"128K_overall_accuracy": "77.81%",
"1M_overall_accuracy": "37.31%"
}
},
{
"name": "GPT-5",
"dimensions": {
"entity_type": "language model",
"evaluated_context": "128K tokens",
"128K_overall_accuracy": "82.02%"
}
},
{
"name": "GPT-5-Mini",
"dimensions": {
"entity_type": "language model",
"evaluated_context": "128K tokens",
"128K_overall_accuracy": "79.88%"
}
},
{
"name": "Qwen3-235B-A22B-Thinking",
"dimensions": {
"entity_type": "language model",
"model_family": "Qwen3",
"reasoning_orientation": "Thinking",
"evaluated_context": "128K tokens",
"128K_overall_accuracy": "78.08%"
}
},
{
"name": "Qwen3-30B-A3B-Thinking",
"dimensions": {
"entity_type": "language model",
"model_family": "Qwen3",
"reasoning_orientation": "Thinking",
"evaluated_context": "128K tokens",
"128K_overall_accuracy": "69.59%"
}
},
{
"name": "DeepSeek-R1-0528",
"dimensions": {
"entity_type": "language model",
"evaluated_context": "128K tokens",
"128K_overall_accuracy": "74.72%"
}
},
{
"name": "MiniMax-M1-80k",
"dimensions": {
"entity_type": "language model",
"evaluated_contexts": "128K and 1M tokens",
"128K_overall_accuracy": "71.02%",
"1M_overall_accuracy": "11.63%"
}
},
{
"name": "Qwen3-4B-Thinking",
"dimensions": {
"entity_type": "language model",
"training_experiment": "fine-tuned using synthesized CorpusQA data",
"training_steps": "25",
"training_method": "Group Relative Policy Optimization",
"training_set_size": "480 samples",
"evaluation_targets": "CorpusQA, LongBenchV2, and FRAMES"
}
},
{
"name": "MemAgent-14B",
"dimensions": {
"entity_type": "memory-agent implementation",
"model_type": "specialist model",
"training_context": "fine-tuned for ultra-long text processing"
}
},
{
"name": "DeepSeek-V3",
"dimensions": {
"entity_type": "language model",
"experimental_role": "LLM-as-a-Judge",
"evaluation_function": "assesses semantic equivalence between generated answers and ground truth"
}
},
{
"name": "Qwen-Max",
"dimensions": {
"entity_type": "language model",
"schema_extraction_role": "one of three models used in multi-model voting"
}
},
{
"name": "GPT-4.1",
"dimensions": {
"entity_type": "language model",
"schema_extraction_role": "one of three models used in multi-model voting"
}
},
{
"name": "Schema Extraction",
"dimensions": {
"entity_type": "pipeline stage",
"input": "source documents",
"output": "validated key-value pairs",
"validation_method": "multi-model voting",
"acceptance_condition": "clear majority across extraction results"
}
},
{
"name": "Document Collection",
"dimensions": {
"entity_type": "pipeline stage",
"source_type": "real-world PDF documents",
"domain_scope": "finance and academia among other domains",
"minimum_length": "10,240 tokens",
"content_requirement": "rich statistical tables and numerical data"
}
},
{
"name": "Query Generation",
"dimensions": {
"entity_type": "pipeline stage",
"construction_method": "manual templates combined with LLM paraphrasing and expansion",
"reasoning_patterns": "comparison, ranking, conditional filtering, and multi-step calculations",
"difficulty_categories": "Easy, Medium, Hard"
}
},
{
"name": "Data Table Aggregation",
"dimensions": {
"entity_type": "pipeline stage",
"input": "structured JSON objects extracted from documents",
"output": "single global data table",
"row_semantics": "typically represents an entity",
"column_semantics": "schema attributes"
}
},
{
"name": "NL2SQL Execution",
"dimensions": {
"entity_type": "pipeline stage",
"input": "natural language query",
"transformation": "natural language to executable SQL",
"execution_target": "aggregated data table",
"purpose": "programmatic ground-truth generation"
}
},
{
"name": "Long Context QA Pair",
"dimensions": {
"entity_type": "benchmark instance",
"components": "concatenated document corpus, natural language query, programmatically derived ground truth answer"
}
},
{
"name": "Ground Truth Answer",
"dimensions": {
"entity_type": "evaluation reference",
"generation_method": "programmatic execution",
"source": "aggregated structured data",
"verification_basis": "logical derivation from complete source data"
}
},
{
"name": "LLM-as-a-Judge",
"dimensions": {
"entity_type": "evaluation method",
"purpose": "semantic equivalence assessment",
"input": "problem, model answer, and ground-truth answer",
"output": "equivalence judgment"
},
{
"name": "Financial Domain",
"dimensions": {
"entity_type": "dataset domain",
"average_tokens": "2.71M",
"languages": "Chinese and English",
"instances": "664"
}
},
{
"name": "Education Domain",
"dimensions": {
"entity_type": "dataset domain",
"average_tokens": "3.12M",
"language": "English",
"instances": "328"
}
},
{
"name": "Real Estate Domain",
"dimensions": {
"entity_type": "dataset domain",
"average_tokens": "3.59M",
"language": "English",
"instances": "324"
}
},
{
"name": "128K Context Set",
"dimensions": {
"entity_type": "dataset scale",
"token_length": "128K",
"average_tokens": "92.5K",
"languages": "English and Chinese",
"instances": "329"
}
},
{
"name": "1M Context Set",
"dimensions": {
"entity_type": "dataset scale",
"token_length": "1M",
"average_tokens": "905K",
"languages": "English and Chinese",
"instances": "329"
}
},
{
"name": "4M Context Set",
"dimensions": {
"entity_type": "dataset scale",
"token_length": "4M",
"average_tokens": "3.71M",
"languages": "English and Chinese",
"instances": "329"
}
},
{
"name": "10M Context Set",
"dimensions": {
"entity_type": "dataset scale",
"token_length": "10M",
"average_tokens": "7.84M",
"languages": "English and Chinese",
"instances": "329"
}
},
{
"name": "Easy Difficulty",
"dimensions": {
"entity_type": "query difficulty level",
"reasoning_characteristic": "basic aggregation and single-dimension analysis",
"operations": "retrieval, filtering, and sorting"
}
},
{
"name": "Medium Difficulty",
"dimensions": {
"entity_type": "query difficulty level",
"reasoning_characteristic": "numerical calculation and multi-condition analysis",
"operations": "ratio calculation and multi-condition combination"
}
},
{
"name": "Hard Difficulty",
"dimensions": {
"entity_type": "query difficulty level",
"reasoning_characteristic": "custom metrics and multi-step reasoning",
"operations": "multi-step calculation, custom business logic, and advanced metric construction"
}
},
{
"name": "Human Expert",
"dimensions": {
"entity_type": "evaluation participant",
"evaluation_scales": "128K, 1M, 4M, and 10M tokens",
"time_limit": "90 minutes per task",
"accuracy_at_128K": "75.0%",
"accuracy_at_1M": "50.0%",
"accuracy_at_4M": "0.0%",
"accuracy_at_10M": "0.0%"
}
},
{
"name": "Base LLM",
"dimensions": {
"entity_type": "evaluation system",
"model_used_in_human_study": "Qwen3-30B-A3B-Thinking",
"accuracy_at_128K": "66.7%",
"accuracy_at_1M": "20.0%",
"large_context_behavior": "context limit exceeded at 4M and 10M"
}
},
{
"name": "CorpusQA Data Synthesis Framework",
"dimensions": {
"entity_type": "data generation framework",
"reasoning_separation": "decouples complex reasoning from unstructured text",
"structured_representation": "created before query and ground-truth generation",
"ground_truth_generation": "programmatic",
"training_use": "generates data for long-context model training"
}
}
]
]
}


### Parsed Output
...

### Expected Entities
...

### Expected Dimensions
...

### Observations
...

### Errors
...

### Output Format
STRUCTURED

### Parseable
YES 

### Semantic Accuracy
...

### Missing Dimensions
...

### Hallucinated Entities
...

### Hallucinated Relationships
...

### Notes
...