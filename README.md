# NDM: N-Dimensional Memory

**An external memory for LLM agents that stores every conversation event exactly, keeps track of who said what and when, and hands the model a short, question-specific view of that history.**

The LLM does one small, checkable job: for each turn, list the entities and their dimensions. A deterministic engine (code and math, no LLM calls) does everything else: identity, time, attribution, ambiguity, relationships, and the view the answering model reads.

Status: research prototype. Tested on the [LoCoMo](https://github.com/snap-research/locomo) long-conversation benchmark. Results so far are reported below, including the failures.

---

## Why

Long conversations break LLMs in predictable ways: facts get attributed to the wrong speaker, dates drift, a model's guess turns into a "fact", and the full history eventually stops fitting in context. Retrieval (RAG) helps with length but returns text fragments with no notion of who said them, when, or whether they were settled.

NDM keeps a structured, auditable record instead, and lets the engine (not the model) decide what is a fact, what is someone's claim, and what is still open.

## How it works

```
conversation turn ──► LLM (stateless, one call per turn) ──► entities + dimensions (validated JSON)
                                                                       │
                                                                       ▼
                                     deterministic engine: ticks, identity, dates, status, buckets
                                                                       │
                                     question ──► depiction (≤ 1,000 words) ──► answering LLM
```

1. **Extraction (LLM).** Each turn is sent in a fresh session with the speaker, date and a dimension dictionary, and nothing else. The output must name every entity with a type and at least one dimension; a parser validates it and retries with feedback when it doesn't.
2. **Engine (code and math).** Every event gets its own tick on the timeline. Entities become fixed **pegs**. The engine builds an incidence matrix *B* (entities × events) and derives everything from it:
   - **Collisions** (*BᵀB*): events that share a peg.
   - **Relationship strength** (*BBᵀ*, Adamic–Adar weighted): how strongly two entities are linked by shared events.
   - **Trajectories**: one entity's events, in time order.
   - **Two clocks**: the order things were said, and the date they happened.

   No relationship is ever stored as an edge; it is computed from shared events.
3. **Epistemic status.** Every event has exactly one status and an owner: fact, claim, speaker belief, model belief, open question, or intent. Unresolved references ("its failover behaviour") become **ambiguity buckets**. A bucket closes only through an explicit statement, the user, or an auditable engine rule (exactly one compatible candidate in the last 3 events). A model's own belief is a hint, never a resolution.
4. **Depiction.** For each question the engine builds a short view: the full trajectory of every entity in the question, then the highest-scoring events, the turn before each, and their neighbours, all dated, with every line labelled "*X* said:" and who each fact is about.

The rules are fixed in a contract with a test for each one: [`N-D/CONTRACT.md`](N-D/CONTRACT.md).

## Results

Every experiment has a spec frozen before it runs; results are reported against that spec, and every answer is hand-scored against the benchmark's gold answers.

| Exp | Data | Question | Result |
|---|---|---|---|
| **ND-0** | 10-sentence pilot | Can free-form extraction support the math? | **No.** Free dimension names break the geometry; extraction must be structured. |
| **ND-1** | Same pilot, engine v0 | Is the engine faithful and stable? | **Conditional pass.** Faithfulness 0.986–1.0; collisions identical across runs (Jaccard 1.0); 14–15 of 15 probes. |
| **ND-1b** | LoCoMo conv-26, 3 sessions | Does memory answer benchmark questions? | **Fail.** 16 vs raw text 21 (76%); temporal 1/7. Causes: missing dates, identity drift, facts split across turns. |
| **ND-2** | LoCoMo conv-30, held out, 33 questions | After fixes, does the depiction keep up with raw text? | **Pass, with a qualifier.** Depiction 24, raw text 26, full memory dump 27. Depiction uses 571 words vs 1,734 (33%). Temporal 5/5. |
| **ND-3** | LoCoMo conv-49, full length (509 turns), 40 questions | Does N-D beat retrieval at the same size? | **Fail.** Depiction 28.5, BM25 retrieval 28.5 (both ~1,000 words), raw text 32.5 (15,014 words): a tie with retrieval, 88% of raw. False premise: depiction 7/8, raw 5/8. Temporal 7/7. |

**What the evidence supports so far**

- **Attribution is the robust result.** On false-premise questions (swapped-speaker traps), owned memory beats reading the raw text on two held-out conversations: ND-2 memory dump 9/9 vs raw 5.5/9; ND-3 depiction 7/8 vs raw 5/8, at 6% of the raw size.
- **Dates work.** Temporal questions went from 1/7 (ND-1b) to 5/5 (ND-2) and 7/7 (ND-3).
- **The engine's memory holds the facts.** In ND-2 the full memory dump matched raw text (27 vs 26). In ND-3, 7 of the depiction's 14 misses were facts present in memory but not selected.
- **Selection is not yet better than retrieval.** At equal size, the depiction ties BM25 (ND-3): it still chooses what to show mostly by question words, and it is weak on questions that gather many turns (multi-hop 3/8 vs raw 6/8).

**Limits.** Small samples (33–40 questions per test), one conversation per test, one extraction run, Claude models only. A difference of 1–2 questions is noise. No comparison with other memory systems (Mem0, Zep) yet.

Full reports: [ND-1b](N-D/ND-1b/stage1/REPORT.md) · [ND-2](N-D/ND-2/REPORT.md) · [ND-3](N-D/ND-3/REPORT.md)

## Repository layout

```
N-D/                         current research track (start here)
  README.md                  thesis and experiment rules
  CONTRACT.md                invariants C1–C12, each with a failure test
  PLAN.md                    experiment sequence
  schema/                    event wire format
  catalog/                   starter dimension catalog
  tools/
    locomo_chunk.py          LoCoMo download check (SHA-256) and chunking
    extract_stateless.py     stateless extractor: anthropic | openai | ollama | claude-cli | replay
    ndm_math.py              incidence-matrix metrics
  engine/
    nd_engine.py             engine stages E1–E6 (no LLM calls)
    depict.py                depiction v1/v2 and the BM25 baseline
    checks.py                contract, faithfulness and must-have checks
    run_batch.py             engine + checks over a folder of extractions
    probe_harness.py         question runs: depict2 | rag | raw | flat, resumable
  ND-0 … ND-3/               one folder per experiment: spec, data notice, results, report

everything else at the root  earlier experiments (V1–V8) and concept documents, kept for history;
                             not used as results or assumptions by N-D
```

## Reproduce

Requirements: Python 3, `numpy`, and either an Anthropic API key or the [Claude Code](https://docs.claude.com/en/docs/claude-code/overview) CLI. Commands run from the `N-D` folder.

```zsh
pip install numpy
git clone https://github.com/snap-research/locomo ~/locomo
cd N-Dimensional-Memory/N-D
```

Build the ND-3 data (the script checks the dataset's SHA-256 first):

```zsh
python3 tools/locomo_chunk.py --locomo ~/locomo/data/locomo10.json --sample 8 --sessions all --probe-sample 40 --seed 7 --out-dir ND-3/data
```

Extract (resumable; rerun the same line to continue):

```zsh
export ANTHROPIC_API_KEY=your-key-here
python3 tools/extract_stateless.py --provider anthropic --model claude-haiku-4-5-20251001 --run 1 --source ND-3/data/source.jsonl --out-dir ND-3/extractions --resume
```

Run the engine and checks (no LLM calls):

```zsh
python3 engine/run_batch.py ND-3 --source ND-3/data/source.jsonl
```

Ask the questions under each condition (each resumable):

```zsh
python3 engine/probe_harness.py depict2 ND-3/per_run ND-3/data/probes.jsonl --model sonnet
python3 engine/probe_harness.py rag ND-3/data/source.jsonl ND-3/data/probes.jsonl ND-3/probes_rag --model sonnet
python3 engine/probe_harness.py raw ND-3/data/source.jsonl ND-3/data/probes.jsonl ND-3/probes_raw --model sonnet
```

The question runs call `claude -p` once per question, from an empty temporary folder. If you keep a personal `~/.claude/CLAUDE.md`, move it aside during runs so it doesn't leak into answers. The built-in scorer is word matching for triage only; reported scores are hand-reviewed (see each experiment's `review.json`).

## Data and license

- **Code:** MIT, see [LICENSE](LICENSE).
- **LoCoMo:** Maharana et al., "Evaluating Very Long-Term Conversational Memory of LLM Agents", ACL 2024, licensed CC BY-NC 4.0. The raw dataset is not committed; `tools/locomo_chunk.py` regenerates it from a verified download. Results derived from it (extractions, engine states, answers) are shared under CC BY-NC 4.0, non-commercial use only. See each experiment's `NOTICE.md`.

## What's next

- Split the engine into inspectable layers, each writing a human-readable view, with a test for every contract rule.
- Fix selection using the engine's structure, not question words: speaker-scoped trajectories, open-bucket candidates, and aggregation for "how many / what kinds" questions; test on fresh held-out data.
- Supersession and contradiction handling, and event-at-a-time ingestion.
- Repeat with a second model family, and compare against existing memory systems (Mem0, Zep).
- Activity memory (tracking intents and tasks over time) and harder ambiguity tests.

## Author

Prabhat Saxena · [github.com/xx-VIRUS-xx](https://github.com/xx-VIRUS-xx)
