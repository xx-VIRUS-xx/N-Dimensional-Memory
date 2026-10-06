# ND-3 report: N-D depiction vs retrieval vs raw text, at full conversation length

**Held-out data:** LoCoMo conv-49 (Evan and Sam), all 25 sessions: 509 turns, 40 benchmark questions (stratified, seed 7). **Extraction:** one Haiku run, prompt v2: 509/509 turns, 0 parser retries, M1 pass, M2a 0.954. **Engine** v0.3, **depiction** v2, both frozen before the run. **Answering model:** Sonnet, one isolated `claude -p` call per question. All 120 answers were hand-scored against LoCoMo gold (`review.json`; C = 1, P = 0.5, W = 0). RAW finished all 40 questions, so every condition is compared on the same 40.

## Results

| Condition | Score (of 40) | Mean context (words) |
|---|---|---|
| RAW conversation | **32.5** | 15,014 |
| RAG (BM25, dated turns) | 28.5 | 983 |
| N-D DEPICTION v2 | 28.5 | **908** |

| Pre-registered criterion | Result | |
|---|---|---|
| H1: DEPICT > RAG | 28.5 vs 28.5, **tie** | ✗ |
| H2: DEPICT ≥ 90% of RAW | 28.5 / 32.5 = **87.7%** | ✗ |
| H3: false premise (cat 5), DEPICT ≥ RAW | **7 vs 5** of 8 | ✓ |
| H4: temporal (cat 2), reported | DEPICT 7, RAG 6, RAW 7 of 7 | — |

| LoCoMo category | n | DEPICT | RAG | RAW |
|---|---|---|---|---|
| 1 multi-hop | 8 | 3.0 | 4.5 | **6.0** |
| 2 temporal | 7 | **7.0** | 6.0 | **7.0** |
| 3 inference | 2 | 1.5 | 1.0 | 1.0 |
| 4 single-hop | 15 | 10.0 | 10.5 | **13.5** |
| 5 false premise | 8 | **7.0** | 6.5 | 5.0 |

Two gold answers are questionable (q23, q29; see below). Without them: DEPICT 28.5, RAG 28.5, RAW 32 of 38, so DEPICT reaches 89% of RAW. The verdict does not change.

## Verdict: fail by the pre-registered rule

**ND-3 fails.** At equal size, the depiction scores exactly what BM25 retrieval scores (H1), and it falls just short of 90% of reading the whole conversation (H2). On plain recall, the engine's structure did not beat a search index.

**What held:** attribution and time.

- **False premise (cat 5): DEPICT 7/8, RAW 5/8.** Reading all 15,000 words, the model accepted "Evan's supermarket issue" and "Evan's high-impact exercise suggestions". The depiction rejected both, naming the right owner ("belongs to Sam, not Evan"). This repeats ND-2's attribution result on a second held-out conversation, at 6% of the raw size.
- **Temporal (cat 2): DEPICT 7/7**, equal to RAW, at 6% of the size.

**What failed:** questions that need facts gathered from many turns. On multi-hop (cat 1), DEPICT scored 3/8 against RAW's 6/8.

## Why the depiction missed (14 questions, 11.5 points)

| Cause | Questions | Points lost |
|---|---|---|
| **Selection:** the fact is in memory, but the depiction did not pick it | q01, q07, q08, q11, q13, q25, q30 | 6.5 |
| **Unresolved reference:** the fact sits on an "it/this" peg, so the question's entity never reaches it | q02, q17, q20 | 1.5 |
| Gold questionable | q23, q29 | 2.0 |
| Presentation: right facts shown, model answered a different question | q37 | 1.0 |
| Judgement (cat 3, open-ended) | q09 | 0.5 |

**No miss came from dates, and none from extraction alone.** Two selection misses also lost detail in extraction (q25 kept "frustrated with new phone" but dropped "navigation app"; q30 kept "apologized to partner" but dropped the reason).

**Selection is the bottleneck.** In 7 of 14 misses, the answer is in the engine's memory and the depiction did not select it. Depiction v2 seeds on entities named in the question and skips the two speakers (hub pegs), so the seeds were weak in two ways:

- **Only speakers named** (q01 "How many road trips did Evan take", q30 "Why did Evan apologize"): no non-speaker seed exists, so selection falls back to word overlap, which is the same signal BM25 uses.
- **A generic peg matched instead of the fact's peg** (q08 seeded "the suggestion", q07 "unhealthy snacks", q13 "hobbies"): the answers sit on other pegs ("flavored seltzer" t66, "soda and candy" t42, "skiing" t166), which no seed reaches.

Either way, selection ends up close to keyword matching, which is why DEPICT and RAG tie.

**Unresolved references cost recall, not just ambiguity.** In t24, Evan describes the Jasper trip as "fresh air, peacefulness and a cozy cabin", but the extractor attached it to the peg "it". The engine correctly left "it" open (C9), yet nothing connected that open bucket to Jasper when a question asked about Jasper. Buckets are recorded, but no step uses their candidates at query time.

## Gold notes

- **q14:** gold "Thursday before 17 Dec"; the source (D20:3) says "last Tuesday". All three conditions followed the source and were scored correct.
- **q23:** the evidence turn (D8:26) says Evan "drove somewhere fun"; gold says skiing. All conditions scored 0.
- **q29:** the text says the camping photo shows a sunset; the gold "a kayak" comes from the image, which no condition sees.

## What this means for N-D

1. **Retrieval is not where N-D adds value yet.** Selection by question words is BM25 under another name. The engine's structure (trajectories, collisions, statuses) is not yet used to choose what to show.
2. **Attribution is the robust result.** Two held-out conversations, two sizes, same direction: owned, attributed memory rejects swapped-speaker premises that raw reading accepts.
3. **Next fixes, each aimed at a measured miss:**
   - *Speaker-scoped selection:* when the question names a speaker, select that speaker's own trajectory filtered by topic, instead of dropping hub pegs (q07, q08, q13, q30).
   - *Bucket-aware selection:* a question that seeds an entity also pulls events where that entity is a candidate in an open bucket, shown as OPEN (q02, q17, q20).
   - *Aggregation:* for "how many / what kinds" questions, list every matching event on the trajectory before the budget cuts (q01, q11, q13).

   These need a new frozen spec and fresh held-out data. conv-49 is now development data.

## Limits

40 questions, one conversation, one extraction run, one scorer, Claude models only. A difference of 1–2 questions is noise; H1 is a tie, and H2 missed by 2.3 points. At ~15k words, LoCoMo still fits comfortably in the answering model's context, so RAW is expected to be strong here.
