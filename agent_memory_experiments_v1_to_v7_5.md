# Persistent Model-Agnostic Agent Memory

## Experimental Progress Summary: EXP-V1 → EXP-V7.5

**Status:** Research milestone summary before EXP-V7.6\
**Scope:** Model-agnostic persistent conversational memory for
long-running coding agents and assistants

------------------------------------------------------------------------

## 1. Research Thesis

The project investigates whether long-running agents can maintain
useful, model-independent memory by representing conversation as a
persistent semantic/relational state rather than relying primarily on
raw conversation replay, model-specific summaries, or similarity-based
retrieval.

The working thesis is:

> Persistent agent memory should be represented as a model-independent,
> temporally evolving epistemic state that preserves observations,
> relationships, actions, outcomes, uncertainty, conflict, negative
> knowledge, and provenance, rather than as retrieved conversational
> text or model-specific summaries.

The system is intended to allow different agents/models to read and
update the same underlying memory substrate.

Conceptually:

``` text
Conversation / External Events / Agent Actions
                    |
                    v
             Smart / Memory Layer
                    |
                    v
      Persistent Relational Memory
                    |
       +------------+-------------+
       |            |             |
  observations   beliefs      relationships
       |            |             |
       +------------+-------------+
                    |
                    v
          Context / Retrieval Builder
                    |
                    v
              Any LLM / Agent
```

The key research question is not simply:

> "Can an LLM remember?"

It is:

> "Can memory be externalized into a model-independent representation
> that preserves what happened, what was believed, what changed, what is
> uncertain, what was never discussed, and why the system believes
> something, while remaining usable by different models?"

------------------------------------------------------------------------

# 2. Experimental Progress at a Glance

  --------------------------------------------------------------------------------------
  Experiment        Primary question       Main comparison / test Main result
  ----------------- ---------------------- ---------------------- ----------------------
  V1                Do different coding    Claude Code vs Codex   Strong semantic
                    agents derive a        vs Copilot             convergence
                    similar semantic                              
                    substrate?                                    

  V2                Can that substrate be  Multi-model semantic   \~75% all-model point
                    canonicalized          outputs vs canonical   support; \~71.43%
                    deterministically?     representation         dimension
                                                                  intersection/union

  V2.1              Can point identity be  SAME / RELATED /       12 canonical points;
                    deterministic and      DISTINCT rules         91.67% supported by ≥2
                    model-independent?                            models

  V3                Can relationships be   Algorithmic relation   14 → 12 candidate
                    inferred without       inference over         relations after
                    letting the LLM invent canonical points       tightening; false
                    the graph?                                    broad relation removed

  V4.x              Can memory represent   Temporal order vs      Correctly
                    time, evolution,       state change vs        distinguishes
                    contradiction and      conflict               evolution from
                    state history?                                overlapping conflict

  V5.x              Can memory represent   Belief lifecycle +     Preserves
                    uncertainty, ambiguity later evidence +       unresolved/competing
                    and competing beliefs? temporal validity      beliefs and later
                                                                  resolution

  V6.x              Can different agents   Claude/Codex/Copilot   Deterministic
                    share and reconstruct  observations over      reconstruction;
                    the same memory?       append-only substrate  update-order
                                                                  independence;
                                                                  provenance preserved

  V7.0              Does structured memory RAW vs RAG vs V6 vs    Initial evidence that
                    help an agent answer   V6+RAW                 structured memory can
                    delayed questions?                            preserve harder
                                                                  historical state

  V7.1              Does this survive      1,200-event corpus;    RAG missed temporal
                    long-horizon           deterministic RAG vs   evidence; V6 answered
                    distractors?           structured memory      all tested cases

  V7.2              Can agents construct   Agent-generated memory Strong memory
                    memory rather than     vs RAW/RAG             construction and
                    consume                                       consumption results
                    benchmark-generated                           
                    memory?                                       

  V7.3              Can writers select     Unlabeled 1,200-event  20/20 selection, but
                    durable information    corpus                 corpus had a
                    without exposed signal                        lexical/template tell
                    labels?                                       

  V7.4              Can selection survive  1,200-event dense      Both writers selected
                    adversarial semantic   distractor corpus      20/20; RAG degraded
                    distractors?                                  substantially

  V7.5              Can the system operate 2,000 events, 4        40/40 memory
                    across                 domains, independent   consumption and 40/40
                    distribution-shifted   writers, bidirectional cross-agent in both
                    long conversations and handoff                directions; RAG 12/40
                    across agents?                                
  --------------------------------------------------------------------------------------

------------------------------------------------------------------------

# 3. EXP-V1: Cross-Model Semantic Convergence

## Question

If the memory system is intended to be model-agnostic, can different LLM
coding agents independently derive a sufficiently similar semantic
representation from the same conversation?

## Models Tested

-   Claude Code
-   Codex
-   GitHub Copilot

## Experimental design

The same conversations were given to each model.

The agents were asked to identify semantic dimensions for concepts.

Example:

> "Rahul loves to play football."

Expected semantic decomposition included:

``` text
Rahul
  noun
  subject
  actor
  person

loves
  verb
  emotion
  feeling
  relationship/state

play
  verb
  action/activity

football
  noun
  object
  activity
  sport
```

Temporal, spatial and reference information was also evaluated.

Examples included:

-   Sunday → time
-   park → place
-   "He" → potentially Rahul, but ambiguous
-   "They" → potentially Rahul + another actor
-   "The plan" → potentially ambiguous
-   "stopped" → state/action transition
-   "started playing again" → resumed state

## Result

There was strong convergence between models on the semantic core.

Importantly, model disagreement was not treated as an error to be
silently corrected. Model-specific interpretations were preserved when
appropriate.

## What V1 established

V1 provided the initial evidence that:

> A model-independent semantic substrate may be feasible even when the
> models use different wording or assign different secondary dimensions.

This became the foundation for deterministic canonicalization.

------------------------------------------------------------------------

# 4. EXP-V2: Canonical Semantic Substrate

## Question

Can the semantic output from different models be converted into a
deterministic representation without making another LLM authoritative?

## Rules

The canonicalization baseline:

1.  Normalize surface variants.
2.  Normalize dimension names.
3.  Use a common dimension only when supported by every participating
    model.
4.  Preserve model-specific dimensions rather than deleting them.
5.  Do not resolve ambiguity simply because one model appears more
    confident.
6.  Defer relationship inference to a separate stage.

## Result

Approximate measured metrics:

-   Point coverage: **\~75%**
-   Dimension preservation: **\~71.43%**

This demonstrated that a canonical substrate could be constructed from
independent model interpretations without using embeddings or another
model to arbitrate every difference.

------------------------------------------------------------------------

# 5. EXP-V2.1: Deterministic Point Identity

## Question

Can semantic point identity be determined using explicit rules instead
of embeddings or another LLM?

## Identity classes

### SAME

Normalized surface-equivalent concepts.

Example:

``` text
plays ≈ playing ≈ play
```

### RELATED

Compatible concepts with different granularity or qualifiers.

Examples:

``` text
play ↔ play football
team ↔ new team
```

### DISTINCT

Insufficient evidence to establish a relationship.

Example:

``` text
Rahul ≠ football
```

## Result

``` text
canonical_points: 12
points_supported_by_2_or_more_models: 11
points_supported_by_all_models: 9

multi_model_support_rate: 0.9167
all_model_support_rate: 0.75

related_point_edges: 3
dimension_intersection_union_ratio: 0.7143

tests: 8 passed
```

## Significance

This separated:

> semantic identity

from:

> semantic relatedness

without relying on vector similarity.

That distinction became important later for relationship inference and
temporal reasoning.

------------------------------------------------------------------------

# 6. EXP-V3: Algorithmic Relationship Inference

## Question

Can relationships be inferred from the canonical substrate without
allowing the model to directly invent the graph?

## Input

The algorithm operated on the canonical points produced by V2/V2.1.

It used signals such as:

-   semantic role
-   shared evidence
-   lexical structure
-   local transition evidence
-   compatible dimensions

## Initial result

``` text
canonical points: 12
candidate relations: 14
connected points: 8
isolated points: 4
high confidence: 7
medium confidence: 7
```

A false positive was detected:

``` text
love → acts_on → football
```

This arose from overly broad dimension overlap.

## V3.1

Relationship constraints were tightened.

The revised system removed the false relation.

``` text
candidate relations: 12
connected points: 7
isolated points: 5
high confidence: 9
medium confidence: 3
tests: 8 passed
```

## Significance

The important result was methodological:

> Relationship inference can be separated from semantic extraction and
> constrained algorithmically.

The LLM provides semantic observations. The memory system decides which
relationships are sufficiently supported.

------------------------------------------------------------------------

# 7. EXP-V4: Temporal and Evolving Memory

V4 introduced time as a first-class component.

## Question

Can the memory system distinguish:

-   a temporal anchor
-   temporal ordering
-   a state change
-   an evolving fact
-   a contradiction?

## Example

``` text
Rahul stopped playing football during summer.

Rahul started playing again after joining a new team.
```

The system represented:

``` text
Rahul
  state: playing
      ↓
  state: inactive
      ↓
  state: active
```

The important principle was:

> Current state is not the same thing as memory of previous states.

Historical observations are not overwritten merely because a newer state
exists.

------------------------------------------------------------------------

## V4.1: State History

State transitions were explicitly preserved:

``` text
playing → inactive → active
```

Tests passed: **6**

------------------------------------------------------------------------

## V4.2: Temporal Conflict Resolution

The system distinguished:

``` text
A happened before B
```

from:

``` text
A and B overlap and disagree
```

The first is an evolution.

The second is a potential conflict.

------------------------------------------------------------------------

## V4.3: Deliberate Contradiction Benchmark

Three cases were tested:

### Ordered evolution

``` text
evolution: 2
conflict: 0
observations: 3
```

### Unordered / overlapping conflict

``` text
evolution: 0
conflict: 1
observations: 2
```

### Repeated same state

``` text
evolution: 0
conflict: 0
observations: 2
```

Tests passed: **12**

## Core rule established

> Explicit temporal order → evolution.

> No temporal ordering / overlapping incompatible states → potential
> conflict.

> Preserve both observations.

This prevented the memory system from collapsing history into a single
"latest truth."

------------------------------------------------------------------------

# 8. EXP-V5: Ambiguity and Belief State

## Question

What happens when the system does not know something, or when different
observations support competing propositions?

Traditional memory systems often encourage producing a single answer.

This experiment explicitly tested whether memory can represent
uncertainty.

## Belief lifecycle

``` text
unknown
   ↓
inferred
   ↓
confirmed
   ↓
disputed
   ↓
rejected
```

The states are historical, not destructive.

An inferred belief that later becomes confirmed retains its earlier
inference history.

## Ambiguity bucket

Unresolved questions are stored explicitly.

Example:

``` text
"He" → Rahul OR Arjun
```

The system does not force a choice simply to produce a fluent answer.

## Initial V5 result

``` text
observations: 2
ambiguity buckets: 1
resolved ambiguities: 1
confirmed: 1
unknown: 1
inferred/disputed/rejected: 0
tests: 5 passed
```

------------------------------------------------------------------------

# 9. EXP-V5.1: Competing Beliefs

Multiple observations of the same proposition were allowed to coexist.

The system preserved:

-   observation
-   provenance
-   status
-   belief history
-   conflict state

Instead of:

``` text
new observation → overwrite old observation
```

the model became:

``` text
observation A
observation B
      ↓
comparison
      ↓
derived belief state
```

Tests passed: **10**

------------------------------------------------------------------------

# 10. EXP-V5.2: Temporal Belief History

Example:

``` text
"I live in Jaipur."
valid until May 2026

"Actually, I moved to Delhi."
valid from June 2026
```

The system treats this as temporal evolution rather than contradiction.

Both observations remain available.

This establishes another key distinction:

> A proposition's current validity is different from the historical
> record of what was previously believed or observed.

Tests passed: **3**

------------------------------------------------------------------------

# 11. EXP-V6: Cross-Agent Persistent Memory

## Question

Can different models share the same persistent memory without one model
becoming authoritative?

Agents:

-   Claude
-   Codex
-   Copilot

## Test cases

The V6 benchmark included:

### Shared activity

Multiple agents independently observed the same proposition.

### Location disagreement

One agent observed:

``` text
Jaipur
2025-01 → 2026-05
```

Another observed:

``` text
Delhi
from 2026-06
```

The persistent memory preserved both observations and derived the
appropriate temporal/disagreement state.

------------------------------------------------------------------------

# 12. EXP-V6.1: Shared Memory Read/Update Protocol

The protocol introduced:

1.  Stable proposition identity
2.  Agent-local observations
3.  Persistent derived state
4.  Immutable provenance/history

The observation store is append-only.

This means an update does not destroy what came before it.

------------------------------------------------------------------------

# 13. EXP-V6.2: Deterministic Reconstruction

## Main question

Can the same memory state be reconstructed from the same append-only
observation set regardless of insertion/update order?

## Required properties

1.  No observation overwrite
2.  Provenance preserved
3.  Same observation set → same derived state
4.  Non-overlapping values → temporal evolution
5.  Overlapping values → potential conflict
6.  Snapshot/restore → same state

## Result

The V6 suite passed **12 tests**.

## Significance

This is an important architectural property.

Memory is not dependent on:

``` text
which agent wrote last
```

or:

``` text
which model was considered authoritative
```

Instead:

``` text
append-only observations
        ↓
deterministic state reconstruction
```

This is the foundation for model interoperability.

------------------------------------------------------------------------

# 14. EXP-V7.0: Memory Consumption by Actual Agents

V7 was the first stage where memory was consumed by agents to answer
delayed questions.

## Conditions

Every agent evaluated the same benchmark under:

``` text
RAW
RAG
V6
V6 + RAW
```

Agents:

-   Codex
-   Claude
-   Copilot

## Case categories

The benchmark included:

1.  Historical recall
2.  Decision continuity
3.  Action/outcome
4.  Temporal state
5.  Ambiguity
6.  Conflict
7.  Negative knowledge
8.  Provenance

The initial V7 benchmark used 7 cases.

## V7.0 results

### Codex

``` text
RAW:       16/16
RAG:       16/16
V6:        21/21
V6+RAW:    21/21
```

### Claude

``` text
RAW:       11/11
RAG:         9/11
V6:        11/11
V6+RAW:    11/11
```

### Copilot

``` text
RAW:       16/16
RAG:       16/16
V6:        21/21
V6+RAW:    21/21
```

## Important limitation

The V7.0 RAG and V6 conditions were not yet equally mature
implementations.

Codex's condition evidence was represented using condition-scoped
identifiers rather than independently materialized retrieval/memory
pipelines.

Therefore V7.0 was evidence of the direction, not a clean universal
comparison between RAG and V6.

------------------------------------------------------------------------

# 15. EXP-V7.1: Long-Horizon Distractor Test

## Purpose

V7.1 made the problem substantially harder.

Instead of a small conversation, the benchmark contained:

-   **1,200 chronological events**
-   8 benchmark cases
-   only a small subset relevant to each query
-   many distractors
-   deterministic RAG chunks
-   deterministic top-6 retrieval

The structured memory contained **33 records** derived from benchmark
annotations.

Important limitation:

> V7.1 tested whether structured memory is useful when the structured
> memory already exists. It did not yet fully test whether an LLM can
> reliably construct that memory from raw conversation.

## Results

### Claude

``` text
RAW:       15/15
RAG:       14/16
V6:        15/15
V6+RAW:    16/16
```

### Copilot

``` text
RAW:        8/8
RAG:        7/8
V6:         8/8
V6+RAW:     8/8
```

Both RAG failures involved the temporal-state case.

The lexical top-6 retrieval did not surface all required historical
events.

## Significance

The experiment demonstrated a failure mode of retrieval:

> Relevant information distributed across a long history may not be
> jointly retrieved even when every individual fact exists in the source
> conversation.

Structured memory explicitly represented the state history.

------------------------------------------------------------------------

# 16. EXP-V7.2: Agent-Generated Memory

V7.2 moved the important question upstream.

Instead of giving the evaluator a benchmark-generated memory, a writer
agent had to construct the memory.

## Writer process

``` text
1,200 events
     ↓
writer agent
     ↓
V6 memory
     ↓
freeze
     ↓
future queries
     ↓
reader agent
```

The writer had:

-   full conversation
-   schema
-   design rules

The writer did NOT have:

-   gold memory
-   gold answers
-   other agents' results

## Required memory features

-   immutable observations
-   stable proposition IDs
-   relationships
-   temporal state histories
-   ambiguity
-   conflict/belief state
-   negative knowledge
-   provenance
-   source IDs
-   confidence/status

## Results

### Copilot

``` text
memory source-event selection: 20/20
selection precision: 1.0
selection recall: 1.0

RAW:              8/8
RAG:              7/8
V6-GENERATED:     8/8
V6-GENERATED+RAW: 8/8

Claude → Copilot: 8/8
```

### Claude

The memory contained:

``` text
50 records
20 source events
```

Exact observation precision/recall was 1.0.

Representation results included:

-   state history: 4/4
-   ambiguity: exact
-   conflict: preserved as a superset
-   negative knowledge: exact scoped representation
-   provenance: 5/5
-   invented records: 0

Consumption:

``` text
V6-GENERATED:     8/8
V6-GENERATED+RAW: 8/8
RAG:              7/8
```

Cross-agent handoff also produced **8/8** in the executed direction.

## Important limitation

The benchmark still exposed too much structural information through the
synthetic corpus and retained selection scaffolding.

This motivated V7.3.

------------------------------------------------------------------------

# 17. EXP-V7.3: Unlabeled Selection

## Goal

Prevent the memory writer from being told which events were important.

Changes:

-   no signal/distractor labels
-   no benchmark raw event IDs
-   no case IDs
-   no explicit relevance hints

## Result

Both Claude and Copilot selected:

``` text
20 / 20 durable events
```

Retention:

``` text
1.67%
```

Compression:

``` text
98.33%
```

## Problem discovered

The corpus had a weakness:

**1,180 distractors shared exact boilerplate such as "routine progress
and no final decision."**

This gave the writer an unintended exclusion signal.

Therefore the impressive selection score was not yet strong evidence of
general autonomous importance detection.

This is a useful negative result.

It demonstrated that benchmark construction itself had become part of
the problem.

------------------------------------------------------------------------

# 18. EXP-V7.4: Adversarial Semantic Distractors

V7.4 attempted to remove the obvious lexical tell.

## Design

-   1,200 events
-   20 durable events
-   1,180 distractors
-   hidden gold durable IDs
-   writer sees unlabeled corpus
-   distractors use semantically close topic vocabulary
-   no single shared lexical discriminator

## Claude

Selection:

``` text
20/20
precision: 1.0
recall: 1.0
F1: 1.0
retention: 1.67%
```

Memory:

``` text
20 durable events covered
0 invented event IDs
all 8 cases covered
```

Consumption:

``` text
RAW:              15/15
RAG:               5/15
V6-GENERATED:     18/18
V6-GENERATED+RAW: 18/18
```

The deterministic RAG baseline failed on **6 of 8 case categories**.

It missed distributed evidence for examples involving:

-   historical state
-   decision continuity
-   action/outcome
-   temporal evolution
-   belief
-   provenance

Ambiguity and negative knowledge were among the cases that were fully
retrieved.

## Copilot

Selection:

``` text
20/20
precision: 1.0
recall: 1.0
F1: 1.0
retention: 1.67%
```

Consumption:

``` text
RAW:              8/8
RAG:              3/8
V6-GENERATED:     8/8
V6-GENERATED+RAW: 8/8
```

## Cross-agent

A Copilot → Claude artifact later demonstrated:

``` text
8/8
```

## Significance

V7.4 strengthened the observation that structured memory can preserve
information that a simple lexical retrieval strategy fails to jointly
retrieve.

However, it remained a synthetic benchmark.

------------------------------------------------------------------------

# 19. EXP-V7.5: Distribution Shift + Cross-Agent Persistence

V7.5 was the strongest experiment completed so far.

## Corpus

-   **2,000 conversational events**
-   **120 durable events**
-   4 domains:
    -   engineering
    -   planning
    -   operations
    -   product
-   dense distractors
-   future queries generated after memory freeze
-   independent clean-room memory writers

The benchmark deliberately moved away from the exact structure of V7.4.

------------------------------------------------------------------------

# 20. V7.5 Memory Construction

## Claude

Claude's memory contained:

``` text
85 records
120 retained source events
4 domains
```

Representation:

``` text
31 state_transition
26 action_outcome
14 decision
10 belief_state
 2 negative_knowledge
 1 ambiguity
 1 provenance_note
```

Selection:

``` text
120 / 120
precision: 1.0
recall: 1.0
F1: 1.0
retention: 6%
compression: 94%
invented event rate: 0
```

The memory preserved at least **9 non-monotonic/conflicting topics**
across four domains rather than collapsing each topic into one current
fact.

Examples included:

-   team ownership
-   PostgreSQL/DynamoDB migration states
-   export API evolution
-   failures followed by later resolution
-   tentative → confirmed beliefs

One disclosed structural exception existed:

> A corpus-structure meta-observation had empty source_event_ids. It was
> not a conversational fact.

------------------------------------------------------------------------

## Copilot

Copilot retained:

``` text
120 / 120 durable events
```

Selection:

``` text
precision: 1.0
recall: 1.0
F1: 1.0
retention: 6%
compression: 94%
```

Source ID precision/recall:

``` text
1.0 / 1.0
```

Invented record rate:

``` text
0
```

## Hash caveat

Copilot reported a cryptographic hash that did not independently
reproduce exactly.

The content remained schema-valid and internally consistent, and the
discrepancy was disclosed.

Therefore:

> Content correctness was preserved, but cryptographic freeze integrity
> for the original reported hash cannot be independently claimed.

------------------------------------------------------------------------

# 21. V7.5 Consumption Results

## Claude

``` text
RAW:              40/40
RAG:              12/40
V6-GENERATED:     40/40
V6-GENERATED+RAW: 40/40
```

## Copilot

``` text
RAW:              40/40
RAG:              12/40
V6-GENERATED:     40/40
V6-GENERATED+RAW: 40/40
```

So the measured result was:

  Condition                     Claude   Copilot
  --------------------------- -------- ---------
  RAW                            40/40     40/40
  Deterministic lexical RAG      12/40     12/40
  V6-generated memory            40/40     40/40
  V6-generated + RAW             40/40     40/40

Unsupported claims:

``` text
0
```

for the reported conditions.

------------------------------------------------------------------------

# 22. V7.5 RAG Failure Pattern

The RAG implementation was a deterministic top-six lexical retrieval
baseline.

Claude's RAG breakdown:

``` text
direct:       2/8
paraphrase:   0/4
indirect:     2/4
temporal:     2/4
causal:       1/4
multi-hop:    0/4
negative:     1/4
ambiguity:    2/4
compositional:2/4
```

The key observation is not that "RAG is bad."

The tested baseline was deliberately narrow.

The observation is:

> Lexical top-k retrieval can fail to retrieve the collection of events
> needed to reconstruct a distributed historical state.

This is precisely the class of problem the relational memory
representation is intended to address.

No claim should be made that V6 universally outperforms modern
hybrid/semantic/graph retrieval systems based on this benchmark.

------------------------------------------------------------------------

# 23. V7.5 Cross-Agent Persistence

This is one of the strongest results.

The system tested:

``` text
Claude memory → Copilot
Copilot memory → Claude
```

Both directions produced:

``` text
40/40 correct
```

Therefore:

> Memory produced by one model remained usable by a different model
> without requiring the original model to be present.

The cross-agent artifacts were executed after both memory writers
completed, avoiding the earlier parallel-run race condition.

This is materially stronger than simply demonstrating that one model can
read its own memory.

------------------------------------------------------------------------

# 24. What the Seven Experimental Stages Have Actually Demonstrated

The work has progressively established several properties.

## Property 1: Semantic substrate convergence

Different models can independently identify a common semantic core.

Established through:

``` text
V1 → V2 → V2.1
```

------------------------------------------------------------------------

## Property 2: Deterministic canonicalization

Surface variation can be normalized without embeddings or an
authoritative LLM.

Established through:

``` text
V2.1
```

------------------------------------------------------------------------

## Property 3: Explicit relationship inference

Relationships can be derived algorithmically from structured semantic
evidence rather than being blindly generated by the LLM.

Established through:

``` text
V3 / V3.1
```

------------------------------------------------------------------------

## Property 4: Temporal memory is not just "latest value"

Historical states can be preserved and reconstructed.

Established through:

``` text
V4.x
```

------------------------------------------------------------------------

## Property 5: Contradiction is not necessarily error

Two incompatible observations may represent:

-   temporal evolution
-   overlapping disagreement
-   unresolved uncertainty

The system preserves the observations instead of overwriting one.

Established through:

``` text
V4.2 / V4.3 / V5.x
```

------------------------------------------------------------------------

## Property 6: Belief and uncertainty can be first-class memory

The memory can explicitly represent:

``` text
unknown
inferred
confirmed
disputed
rejected
ambiguous
```

Established through:

``` text
V5.x
```

------------------------------------------------------------------------

## Property 7: Memory can be reconstructed independently of writer order

The persistent state is derived from an append-only observation set.

Established through:

``` text
V6.x
```

------------------------------------------------------------------------

## Property 8: Different agents can share the same memory substrate

Claude and Copilot were able to consume each other's memory successfully
in V7.5.

Established through:

``` text
V6 → V7.5
```

with the strongest bidirectional result:

``` text
Claude → Copilot: 40/40
Copilot → Claude: 40/40
```

------------------------------------------------------------------------

## Property 9: Structured memory can preserve information that retrieval misses

Across V7.1--V7.5, the deterministic lexical RAG baseline repeatedly
missed distributed temporal/causal/multi-hop evidence while structured
memory retained the relevant state.

The strongest V7.5 comparison was:

``` text
RAG:             12/40
V6-generated:    40/40
V6 + RAW:        40/40
```

for both tested reader agents.

------------------------------------------------------------------------

## Property 10: Memory construction itself is feasible

V7.2--V7.5 moved from benchmark-generated memory toward independent
clean-room writer agents.

V7.5 produced:

``` text
Claude: 120/120 selection
Copilot: 120/120 selection
```

with no invented source events in the reported evaluation.

This is promising, but the synthetic nature of the corpus prevents
treating this as proof of real-world autonomous memory extraction.

------------------------------------------------------------------------

# 25. What We Have NOT Proven

This section is deliberately important.

## Not proven: Universal superiority over RAG

The tested RAG baseline is deterministic lexical top-k retrieval.

Modern RAG can use:

-   semantic retrieval
-   hybrid lexical + vector retrieval
-   reranking
-   graph retrieval
-   query expansion
-   multi-hop retrieval

Therefore:

> V7.5 does not prove V6 is universally better than RAG.

------------------------------------------------------------------------

## Not proven: Real-world generalization

The corpora are synthetic/template-generated.

Even V7.5, while substantially stronger, is still not equivalent to
months of messy human-agent interaction.

------------------------------------------------------------------------

## Not proven: Perfect autonomous memory construction

The 120/120 selection result is extremely encouraging inside the
benchmark.

It does not prove that an agent can always decide:

> "This information will matter six months from now."

That remains an open problem.

------------------------------------------------------------------------

## Not proven: Efficiency superiority

Actual:

-   token counts
-   retrieval latency
-   memory construction latency
-   answer latency
-   monetary cost

were not available in the V7.5 runs.

Therefore no efficiency superiority claim should be made yet.

------------------------------------------------------------------------

## Not proven: Final research novelty

The work uses mechanisms that overlap with existing research:

-   temporal knowledge graphs
-   provenance
-   persistent memory
-   belief/state tracking
-   graph-based retrieval
-   agent memory

The potential novelty lies in the **combination and framing**:

> a model-independent persistent epistemic memory substrate intended to
> survive model replacement and support cross-agent cognitive
> continuity.

That claim still needs systematic prior-art comparison.

------------------------------------------------------------------------

# 26. Current Architectural Model

The experiments now support the following architecture:

``` text
                 ┌─────────────────────────┐
                 │ Conversation / Events   │
                 └────────────┬────────────┘
                              │
                              v
                 ┌─────────────────────────┐
                 │ Semantic Interpretation │
                 │                         │
                 │ points                  │
                 │ dimensions              │
                 │ roles                   │
                 │ temporal signals        │
                 │ ambiguity               │
                 └────────────┬────────────┘
                              │
                              v
                 ┌─────────────────────────┐
                 │ Canonical Memory Layer  │
                 │                         │
                 │ observations            │
                 │ propositions            │
                 │ relationships           │
                 │ states                  │
                 │ beliefs                 │
                 │ conflicts               │
                 │ provenance              │
                 │ negative knowledge      │
                 └────────────┬────────────┘
                              │
                              v
                 ┌─────────────────────────┐
                 │ Persistent Memory Store │
                 │                         │
                 │ append-only evidence    │
                 │ deterministic state     │
                 │ version/history         │
                 └────────────┬────────────┘
                              │
                              v
                 ┌─────────────────────────┐
                 │ Context / Query Planner │
                 └────────────┬────────────┘
                              │
               ┌──────────────┼──────────────┐
               v              v              v
            Claude          Codex         Copilot
```

The LLM is therefore not the permanent memory itself.

The LLM is an interchangeable intelligence layer interacting with
persistent memory.

------------------------------------------------------------------------

# 27. The Most Important Conceptual Shift

The project began with:

> "Can we make AI remember conversations better?"

The experiments have refined that into:

> "Can memory be represented independently from the intelligence model
> that interprets and consumes it?"

This changes the unit of memory from:

``` text
text chunk
```

toward:

``` text
observation
+ proposition
+ relationship
+ state
+ temporal validity
+ uncertainty
+ provenance
+ outcome
```

The model can change.

The memory remains.

That is the architectural idea worth investigating further.

------------------------------------------------------------------------

# 28. Current Research Position

As of V7.5, the project has evidence for:

``` text
semantic convergence             ✓
canonicalization                 ✓
relationship inference           ✓
temporal state history           ✓
conflict preservation            ✓
belief/ambiguity representation  ✓
append-only reconstruction       ✓
cross-agent sharing              ✓
long-horizon structured memory   ✓
agent-generated memory           ✓
bidirectional cross-agent use    ✓
```

But:

``` text
real conversational generalization      ?
strong RAG comparison                   ?
real-world memory selection             ?
token/latency/cost advantage             ?
large-scale long-term degradation        ?
formal novelty vs prior art              ?
```

remain open.

------------------------------------------------------------------------

# 29. Why EXP-V7.6 Is the Correct Next Step

The benchmark should now become more realistic rather than merely more
complicated.

V7.6 should move toward:

``` text
realistic messy conversation
          ↓
autonomous memory construction
          ↓
memory freeze/version
          ↓
long delayed queries
          ↓
different reader models
```

and instrument the complete pipeline.

## Required measurements

### Memory construction

-   source context tokens
-   memory tokens
-   memory bytes
-   construction time
-   number of observations retained
-   number of propositions
-   relationship count
-   invented-record rate
-   missed durable information

### Retrieval / consumption

-   retrieved memory records
-   retrieved raw chunks
-   retrieval latency
-   context tokens
-   answer latency
-   answer cost
-   unsupported claims

### Semantic correctness

-   historical recall
-   decision continuity
-   action → outcome
-   temporal reconstruction
-   ambiguity handling
-   conflict handling
-   negative knowledge
-   provenance
-   cross-agent handoff

------------------------------------------------------------------------

# 30. Final Status Before V7.6

V7.5 is the strongest milestone so far.

The result is **not**:

> "We have proven a universally superior memory architecture."

The result is:

> **We have built and experimentally validated a coherent
> model-independent memory substrate across seven increasingly demanding
> experimental stages, and the latest experiments show that
> independently generated structured memory can preserve and transfer
> long-horizon conversational state across different LLM agents while a
> simple lexical retrieval baseline frequently fails to recover the same
> distributed evidence.**

That is enough evidence to justify moving beyond toy architecture
experiments.

The next phase should focus on falsification:

> **Take the memory system out of synthetic conditions and see whether
> the observed advantage survives realistic conversation, stronger
> retrieval baselines, autonomous memory construction, and real
> efficiency measurements.**

If it survives that, the project will have moved from a promising
architecture hypothesis toward a defensible research contribution.
