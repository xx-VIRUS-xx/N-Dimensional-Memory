# N-Dimensional Memory

## V1–V6 Core Invariants for EXP-V8

### Purpose

EXP-V8 does not replace EXP-V1 through EXP-V6.

V1–V6 established the representational properties of N-Dimensional Memory. EXP-V8 tests whether those properties provide measurable downstream utility for agent reasoning and memory consumption.

The V1–V6 invariants therefore form the **core contract** that the V8 implementation must preserve.

---

# 1. Semantic Preservation

### Origin

EXP-V1

### Invariant

NDM must preserve information that has durable semantic value rather than reducing a conversation to surface-level textual similarity.

A memory representation must retain meaningful:

* facts
* decisions
* actions
* preferences
* states
* changes
* relationships
* uncertainty

### Required property

Equivalent source meaning should remain recoverable from the NDM representation even when the original conversational wording is discarded.

### Failure condition

A fact or semantic state present in the source is lost solely because it was not lexically prominent.

---

# 2. Canonical Semantic Representation

### Origin

EXP-V2

### Invariant

Repeated references to the same semantic object should resolve to a stable representation rather than producing independent duplicated facts.

NDM should distinguish:

```text
surface wording
```

from:

```text
canonical semantic identity
```

### Required property

Different textual expressions referring to the same entity or proposition should be capable of resolving to the same canonical identity.

### Failure condition

The system creates duplicate semantic objects solely because the wording changed.

---

# 3. Relationship Preservation

### Origin

EXP-V3

### Invariant

NDM must preserve meaningful relationships between semantic objects.

Relationships may include:

* caused
* depends_on
* supports
* contradicts
* supersedes
* follows

Relationships are part of memory state, not optional decoration.

### Required property

If the source establishes a meaningful relationship, the relationship should remain recoverable from NDM.

### Failure condition

The individual facts survive but the relationship connecting them is lost.

Example:

```text
PostgreSQL became expensive
        ↓
Alice reconsidered the decision
```

must not become two unrelated facts.

---

# 4. Temporal State Preservation

### Origin

EXP-V4

### Invariant

NDM must preserve the evolution of semantic state over time.

A later state must not erase the historical state that preceded it.

Example:

```text
January:
PostgreSQL

March:
DynamoDB
```

must remain representable as:

```text
historical state:
PostgreSQL

current state:
DynamoDB
```

### Required property

NDM must distinguish:

* historical truth
* current truth
* validity intervals
* state transitions
* supersession

### Failure condition

The system retains only the latest value and loses the historical state.

---

# 5. Belief State Separation

### Origin

EXP-V5

### Invariant

A proposition and a person's belief about that proposition are separate dimensions.

The system must distinguish:

```text
WHAT IS REPRESENTED
```

from:

```text
WHO BELIEVES IT
```

Example:

```text
Alice believes X
Bob believes Y
```

must not collapse into:

```text
X and Y are contradictory global facts
```

### Required property

NDM must be able to represent:

* unknown
* inferred
* confirmed
* disputed
* rejected

belief states.

### Additional requirement

Belief state must remain distinct from proposition lifecycle.

For example:

```text
proposition:
superseded

historical belief:
confirmed
```

is valid.

`superseded` is not a belief state.

### Failure condition

The system converts a person's belief into objective truth or confuses proposition lifecycle with epistemic belief.

---

# 6. Ambiguity Preservation

### Origin

EXP-V5

### Invariant

NDM must preserve unresolved uncertainty rather than silently resolving it.

Supported ambiguity states:

```text
unresolved
candidate_set
resolved
```

### Required property

When the source does not provide enough evidence to resolve an entity, reference, or interpretation, NDM must retain that uncertainty.

When later evidence resolves the ambiguity, the resolution should be representable.

### Failure condition

The system selects one interpretation without sufficient evidence and discards the alternatives.

---

# 7. Provenance Preservation

### Origin

EXP-V6

### Invariant

Memory should retain a trace from derived semantic state back to the source observation.

At minimum, memory should be able to identify:

```text
source
source_id
source span / event / turn
```

### Required property

A proposition, event, relationship, or other derived memory item should be traceable to the source evidence whenever such evidence exists.

### Failure condition

The system produces a semantic claim that cannot be traced back to the source despite source evidence being available.

---

# 8. Supersession Preservation

### Origin

EXP-V4–V6

### Invariant

When a later proposition replaces an earlier proposition, the earlier proposition must remain recoverable as historical state.

Example:

```text
P1:
billing service → PostgreSQL

P2:
billing service → DynamoDB

P2 supersedes P1
```

The correct memory is not:

```text
billing service → DynamoDB
```

alone.

It is:

```text
historical:
billing service → PostgreSQL

current:
billing service → DynamoDB

relationship:
P2 supersedes P1
```

### Failure condition

The system deletes or irreversibly overwrites the earlier proposition.

---

# 9. Append-Only Observation History

### Origin

EXP-V6

### Invariant

Raw observations should remain immutable.

Derived memory state may evolve, but the underlying observations must remain available for reconstruction and audit.

Conceptually:

```text
Observation 1
Observation 2
Observation 3
       ↓
Derived NDM state
```

rather than:

```text
Observation 1
     ↓
overwrite
     ↓
Observation 2
     ↓
overwrite
```

### Required property

The same observation set should be capable of producing the same derived state independent of insertion order where the semantics are order-independent.

### Failure condition

A later write destroys the information required to reconstruct previous state.

---

# 10. Deterministic State Reconstruction

### Origin

EXP-V6

### Invariant

Given the same observation set and the same NDM rules, state reconstruction should be deterministic.

Conceptually:

```text
Observations A + B + C
        ↓
    NDM state X
```

and:

```text
Observations C + A + B
        ↓
    NDM state X
```

when insertion order has no semantic significance.

### Required property

State reconstruction should not depend arbitrarily on the order in which observations were inserted.

### Failure condition

Equivalent observation sets produce materially different memory states solely because they were processed in different orders.

---

# 11. V1–V6 Composite Contract

The complete NDM representation should therefore preserve:

```text
                    NDM STATE
                       │
       ┌───────────────┼────────────────┐
       │               │                │
    SEMANTIC        TEMPORAL         RELATIONAL
       │               │                │
    entities        validity         relationships
    propositions    evolution        causality
    events          supersession     dependencies
       │               │                │
       └───────────────┼────────────────┘
                       │
                 EPISTEMIC STATE
                       │
              ┌────────┼────────┐
              │        │        │
           belief   ambiguity  negative
              │        │        │
              └────────┼────────┘
                       │
                   PROVENANCE
                       │
                 source evidence
                       │
                       ▼
               DETERMINISTIC
              PERSISTENT STATE
```

The representation is considered V1–V6 compliant only when these dimensions can coexist without one dimension incorrectly collapsing into another.

---

# 12. EXP-V8 Must Not Change These Invariants

EXP-V8 may change:

* storage implementation
* retrieval implementation
* indexing
* packing
* reader architecture
* model
* performance optimizations
* serialization details

EXP-V8 must not silently redefine:

* what constitutes a proposition
* temporal state
* belief state
* ambiguity
* provenance
* supersession
* persistent observation history
* deterministic reconstruction

Any change to those concepts constitutes a **new NDM version**, not an implementation tweak.

---

# 13. EXP-V8 Research Question

V1–V6 established the representational hypothesis.

V8 asks the downstream question:

> Does preserving multidimensional conversational state improve an agent's ability to answer questions correctly from long-running conversational histories?

The comparison should therefore separate:

### Representation

```text
Conversation
    ↓
NDM
```

from:

### Consumption

```text
NDM
 ↓
Retriever / State Reconstructor
 ↓
Reader Agent
 ↓
Answer
```

The representation and consumption layers must be evaluated separately.

---

# 14. EXP-V8 Conditions

Initial controlled comparison:

```text
RAW
RAW conversation → reader → answer

NDM
conversation → NDM → state reconstruction → reader → answer
```

Later comparison:

```text
RAW
NDM
RAW + NDM
GraphRAG
HippoRAG2
```

RAPTOR is excluded from the experiment.

---

# 15. EXP-V8 Success Criteria

NDM should not be considered successful merely because it produces valid JSON.

The experiment must establish whether NDM improves one or more measurable properties:

* answer correctness
* evidence completeness
* temporal correctness
* belief/scope correctness
* contradiction handling
* historical-state reconstruction
* current-state reconstruction
* hallucination resistance
* context compression
* reader token consumption
* latency
* total cost
* cross-agent portability

A representation that is richer but produces no downstream improvement remains an interesting research result, but not evidence that the representation provides practical utility.

---

# 16. Immediate Development Sequence

The V8 implementation should proceed in this order:

```text
V1–V6 invariants
       ↓
NDM schema freeze
       ↓
writer validation
       ↓
semantic audit
       ↓
deterministic state reconstruction
       ↓
adversarial query suite
       ↓
RAW vs NDM
       ↓
NDM adversarial stress testing
       ↓
large-scale corpus
       ↓
RAW + NDM
       ↓
GraphRAG / HippoRAG2
       ↓
cross-agent portability
       ↓
LoCoMo / LongMemEval
```

The critical principle is:

> **Do not optimize retrieval until it has been demonstrated that the underlying representation preserves the required state.**

V1–V6 established the representation hypothesis.

V8 tests whether that hypothesis actually matters.
