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
## Prompt
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

# Event

Alice proposed PostgreSQL for the payments platform.

---
## Test001

# Input
{
  "entities": [
    {
      "name": "Alice",
      "dimensions": {
        "event_role": "proposer",
        "action_performed": "proposed PostgreSQL for the payments platform"
      }
    },
    {
      "name": "PostgreSQL",
      "dimensions": {
        "event_role": "proposed_technology",
        "proposal_target": "payments platform",
        "proposer": "Alice"
      }
    },
    {
      "name": "payments platform",
      "dimensions": {
        "event_role": "target_system",
        "candidate_technology": "PostgreSQL"
      }
    }
  ]
}
# Interpreter Model
Gemini Flash 3.8

# Reconstructor Model A Output
Gemini Flash 3.8
The context establishes three distinct entities and their explicit semantic dimensions within a proposal event:

* **Alice**
* **Role:** Operates in the event role of "proposer."
* **Action:** Performed the action of proposing PostgreSQL for the payments platform.


* **PostgreSQL**
* **Role:** Operates in the event role of "proposed_technology."
* **Relationships & Attribution:** Identified as having Alice as its "proposer" and the payments platform as its "proposal_target."


* **Payments platform**
* **Role:** Operates in the event role of "target_system."
* **Status/Association:** Associated with PostgreSQL as its "candidate_technology."

# Reconstructor Model B Output
Claude Opus 5.5
The context describes a single proposal event from three consistent perspectives, with each entity explicitly referencing the others.

**Alice** is a participant who acted as the proposer: she proposed PostgreSQL for the payments platform. Nothing else about Alice is stated, including her position, affiliation, authority, reasons, or any outcome of her proposal.

**PostgreSQL** is a technology that was proposed. Its target is the payments platform, and its proposer is Alice. Its status is only "proposed." The context does not say it was accepted, rejected, adopted, evaluated, compared with alternatives, or already in use.

**The payments platform** is the system the proposal is directed at, and PostgreSQL is described as a candidate technology for it. "Candidate" means a possibility under consideration, not a decision. The context does not say what role PostgreSQL would play, such as primary database or specific component, whether the platform exists yet or is being planned, or whether other candidates exist.

The context leaves several things unstated:
- No timing, sequence, or decision-maker is given.
- No motivation or justification is given.
- No other participants are mentioned.
- No causal claims are made. The proposal is not linked to any problem, requirement, or consequence.
- Whether the proposal is still open, resolved, or superseded is unknown.

# Reconstructor Model C Output
Grok
There is an entity named Alice.  
Associated with Alice is the event role of proposer.  
Associated with Alice is the action performed of proposed PostgreSQL for the payments platform.

There is an entity named PostgreSQL.  
Associated with PostgreSQL is the event role of proposed_technology.  
Associated with PostgreSQL is the proposal target of payments platform.  
Associated with PostgreSQL is the proposer of Alice.

There is an entity named payments platform.  
Associated with payments platform is the event role of target_system.  
Associated with payments platform is the candidate technology of PostgreSQL.

# Reconstructor Model D Output
ChatGPT
Alice is an entity that acted as the proposer in the represented event. Alice proposed PostgreSQL for the payments platform.

PostgreSQL is an entity represented as the technology that was proposed. The proposal concerns the payments platform, and Alice is identified as the proposer.

The payments platform is an entity represented as the target system of the proposal. PostgreSQL is represented as the candidate technology for that system.

The representation does not establish whether PostgreSQL was ultimately selected or used, whether the proposal was accepted or rejected, or any causal relationship between the entities beyond the explicitly represented proposal.

---
# Input
{
  "entities": [
    {
      "name": "Alice",
      "dimensions": {
        "role_in_event": "proposer",
        "action": "proposed",
        "proposal_subject": "PostgreSQL",
        "proposal_target": "payments platform",
        "temporal_position": "past"
      }
    },
    {
      "name": "PostgreSQL",
      "dimensions": {
        "role_in_event": "proposed option",
        "proposal_status": "proposed",
        "proposed_by": "Alice",
        "proposed_for": "payments platform",
        "adoption_status": "unresolved"
      }
    },
    {
      "name": "payments platform",
      "dimensions": {
        "role_in_event": "target of proposal",
        "proposed_technology": "PostgreSQL",
        "decision_status": "unresolved"
      }
    }
  ]
}
# Interpreter Model
Claude Opus 5.5
# Reconstructor Model A Output
Gemini Flash 3.8
The provided context specifies three distinct entities and the semantic facts explicitly associated with each:

* **Alice**
* **Role and Action:** Alice participated as a proposer who performed the action of proposing.
* **Proposal Subject:** The subject of Alice's proposal was PostgreSQL.
* **Proposal Target:** The target of Alice's proposal was the payments platform.
* **Temporal State:** This action is positioned in the past.


* **PostgreSQL**
* **Role and Status:** PostgreSQL served in the role of a proposed option, holding the status of being proposed.
* **Attribution:** The proposal of PostgreSQL was made by Alice.
* **Intended Target:** PostgreSQL was proposed for the payments platform.
* **Resolution State:** The adoption status of PostgreSQL is unresolved.


* **Payments platform**
* **Role:** The payments platform served in the role of the target of a proposal.
* **Associated Technology:** The proposed technology associated with this platform was PostgreSQL.
* **Decision State:** The decision status regarding this target remains unresolved.
# Reconstructor Model B Output
Claude Opus 5.5
**Semantic representation**

**Entity: Alice**
Alice is a participant in a proposal event, in the role of proposer. She performed the action of proposing. The thing she proposed is PostgreSQL, and she proposed it for the payments platform. The proposing action is placed in the past. The source does not say when in the past, to whom the proposal was made, why it was made, or what Alice's role is outside this event.

**Entity: PostgreSQL**
PostgreSQL is the option being proposed in this event. Its proposal status is "proposed," meaning it has been put forward, with nothing further stated. Alice proposed it, and it was proposed for the payments platform. Its adoption status is unresolved. The source does not say whether it will be, is being, or has been adopted or rejected. No competing or alternative options are mentioned. PostgreSQL appears only as a proposed option, and the source says nothing about its properties or whether it suits the platform.

**Entity: payments platform**
The payments platform is the target of the proposal, the thing PostgreSQL was proposed for. The technology proposed for it is PostgreSQL. Its decision status is unresolved. The source attaches this status to the platform without saying explicitly what the decision concerns. The most direct reading is that it concerns the PostgreSQL proposal, but the source does not state this outright. It also does not say who holds decision authority, whether a formal decision process exists, or what technology the platform currently uses, if any.

**Cross-entity notes**

The three entities describe a single proposal event from three perspectives (proposer, proposed option, and target). They should not be read as three separate events.

The relationships that are explicitly supported are: Alice proposed PostgreSQL; PostgreSQL was proposed for the payments platform; and Alice's proposal targeted the payments platform.

Two statuses are open. The adoption of PostgreSQL is unresolved, and the platform's decision status is unresolved. These are recorded separately, and the source does not state whether they refer to the same pending outcome.

The only explicit temporal marker is "past," on Alice's action. The current state of the unresolved statuses is implied rather than given a time, and no sequence beyond the proposal having occurred is stated.

Nothing indicates causality, motivation, endorsement, opposition, or outcome.
# Reconstructor Model C Output
Grok
Alice is the proposer. Alice performed the action of proposing. The subject of the proposal by Alice is PostgreSQL. The target of the proposal by Alice is the payments platform. The temporal position of this is past.

PostgreSQL has the role of proposed option. The proposal status of PostgreSQL is proposed. PostgreSQL was proposed by Alice. PostgreSQL was proposed for the payments platform. The adoption status of PostgreSQL is unresolved.

The payments platform has the role of target of proposal. The proposed technology for the payments platform is PostgreSQL. The decision status of the payments platform is unresolved.
# Reconstructor Model D Output
ChatGPT
Alice is represented as the proposer of a past proposal. The proposal concerned PostgreSQL as an option for the payments platform.

PostgreSQL is represented as the technology option that was proposed by Alice for the payments platform. Its status is that of a proposal, while whether it was adopted remains unresolved.

The payments platform is represented as the target for the proposal. PostgreSQL is identified as the technology proposed for it, while the platform's decision regarding the proposal remains unresolved.

The representation does not establish that PostgreSQL was adopted, rejected, or implemented, nor does it establish why the proposal was made.


---
# Input
{
  "entities": [
    {
      "name": "Alice",
      "dimensions": {
        "action": "proposed",
        "proposed_item": "PostgreSQL",
        "proposed_for": "payments platform"
      }
    },
    {
      "name": "PostgreSQL",
      "dimensions": {
        "status": "proposed",
        "proposed_by": "Alice",
        "proposed_for": "payments platform"
      }
    },
    {
      "name": "payments platform",
      "dimensions": {
        "role": "target of proposal",
        "proposed_technology": "PostgreSQL",
        "proposed_by": "Alice"
      }
    }
  ]
}
# Interpreter Model
Grok
# Reconstructor Model A Output
Gemini Flash 3.8
The context defines three distinct entities and the explicit semantic facts and dimensions attributed to each:

* **Alice**: An entity whose associated action is "proposed." The entity or item proposed by Alice is "PostgreSQL," and the target or purpose for which it is proposed is "payments platform."
* **PostgreSQL**: An entity with the status of "proposed." It is explicitly characterized as having been proposed by the entity "Alice" for the "payments platform."
* **payments platform**: An entity whose role is specified as "target of proposal." It is associated with a proposed technology, which is "PostgreSQL," and the proposal is attributed to "Alice."
# Reconstructor Model B Output
Claude Opus 5.5
The context describes a single proposal event, recorded redundantly from the perspective of each of three participating entities. All three records agree and add no facts beyond that one event.

**The event:** Alice proposed PostgreSQL for the payments platform.

**Alice** is the agent of the proposal. The only thing attributed to her is the act of proposing: she put forward PostgreSQL, and the proposal concerned the payments platform. The context says nothing about her role, her authority, her reasons, or her relationship to the platform or its team.

**PostgreSQL** is the item proposed. Its status is "proposed," meaning it has been put forward but nothing indicates it was accepted, rejected, evaluated, or adopted. The context attributes the proposal to Alice and ties it to the payments platform. It does not say what role PostgreSQL would play (for example, primary datastore or something else), though "proposed for" implies some intended use in connection with the platform.

**The payments platform** is the target of the proposal, meaning it is the thing the proposal concerns. PostgreSQL was proposed for it, by Alice. The context does not say whether the platform already exists or is planned, what it currently uses, or whether the proposal is being considered by anyone.

**What remains unspecified:** when the proposal happened, whether any decision followed, the motivation for the proposal, whether alternatives were considered, and who, if anyone, received or will evaluate it. These points should stay open rather than be filled in.
# Reconstructor Model C Output
Grok
Alice has the action of having proposed. The item that Alice proposed is PostgreSQL. The thing for which Alice proposed that item is the payments platform.

PostgreSQL has the status of being proposed. The entity by which PostgreSQL was proposed is Alice. The thing for which PostgreSQL was proposed is the payments platform.

The payments platform has the role of being the target of a proposal. The technology proposed for the payments platform is PostgreSQL. The entity by which that technology was proposed for the payments platform is Alice.
# Reconstructor Model D Output
ChatGPT
Alice is an entity associated with an action of proposing PostgreSQL. The proposal concerns using PostgreSQL for the payments platform. The representation does not specify whether the proposal was accepted, rejected, implemented, or merely discussed.

PostgreSQL is an entity whose status is represented as proposed. Alice is identified as the proposer, and the payments platform is identified as the target for which PostgreSQL was proposed.

The payments platform is an entity serving as the target of the proposal. PostgreSQL is identified as the technology proposed for it, and Alice is identified as the person who made the proposal.

The representation establishes a proposal relationship between Alice, PostgreSQL, and the payments platform. It does not establish that PostgreSQL is actually being used by the payments platform, nor does it establish that Alice has any role in operating or developing the platform.

---
# Input
{
"entities": [
{
"name": "Alice",
"dimensions": {
"role": "proposer",
"action": "proposed"
}
},
{
"name": "PostgreSQL",
"dimensions": {
"role": "proposed technology"
}
},
{
"name": "payments platform",
"dimensions": {
"context": "intended platform"
}
}
]
}
# Interpreter Model
ChatGPT
# Reconstructor Model A Output
Gemini Flash 3.8
The provided context explicitly supports the following distinct entities and their associated semantic dimensions:

* **Alice**
* **Role:** Proposer
* **Action:** Proposed
* *Semantic description:* Alice is identified as an entity fulfilling the role of a proposer and is associated with the explicit action of having proposed. The context does not explicitly specify the direct grammatical target of her action, nor does it explicitly link her action to other entities beyond these dimensional labels.


* **PostgreSQL**
* **Role:** Proposed technology
* *Semantic description:* PostgreSQL is identified as an entity fulfilling the role of a proposed technology. The context does not state who proposed it, when it was proposed, or what specific system it was proposed for, leaving those links unasserted.


* **Payments platform**
* **Context:** Intended platform
* *Semantic description:* The payments platform is identified as an entity characterized within the context dimension as an "intended platform." The context does not define what technology is intended for it, who intends it, or its operational state.
# Reconstructor Model B Output
Claude Opus 5.5
**Alice** is an entity characterized as a proposer, and she performed the action of proposing (past tense, "proposed"). The context does not state what she proposed, to whom, when, or with what outcome.

**PostgreSQL** is an entity whose role is "proposed technology," meaning it has the status of a technology that was put forward as a proposal. The context does not say who proposed it, for what purpose, or whether the proposal was accepted, rejected, or is still pending.

**Payments platform** is an entity described contextually as an "intended platform." It is framed as a platform that something is intended for, but the context does not say what is intended for it, by whom, or whether it currently exists or is planned.

**Unresolved relations.** The three entities appear together, and their descriptors fit a reading in which Alice proposed PostgreSQL for the payments platform. That reading is not explicitly asserted. No stated relation links Alice to PostgreSQL as the object of her proposal, and none links PostgreSQL or the proposal to the payments platform as its target. The following are all absent: the decision status, the rationale, the timing, the alternatives, and any other participants. These links should stay open unless additional context supports them.
# Reconstructor Model C Output
Grok
There is an entity named Alice. Associated with this entity is the role of proposer. Associated with this entity is the action of proposed.

There is an entity named PostgreSQL. Associated with this entity is the role of proposed technology.

There is an entity named payments platform. Associated with this entity is the context of intended platform.
# Reconstructor Model D Output
ChatGPT
Alice is represented as the proposer and is associated with the action of proposing.

PostgreSQL is represented as a proposed technology.

The payments platform is represented as the intended platform.

The representation does not explicitly specify what Alice proposed, whether PostgreSQL was proposed by Alice, or what relationship exists between PostgreSQL and the payments platform.

---

## Conclusion

The experiment provides preliminary evidence that an LLM-generated entity-and-dimension representation contains sufficient semantic information for another LLM to interpret the represented context in natural language. This supports using entity-dimension representations as a semantic intermediate representation. It does not yet establish that the representation is lossless, nor that downstream NDM algorithms will successfully recover all cross-event relationships or chronology.
# Next Experiment: Corpus → Entity-Dimension Structure → Mathematical Relationship Discovery

## Objective

The next phase is to move from a controlled semantic reconstruction test to a corpus-based experiment.

The purpose is to deliberately generate entity-and-dimension representations from a real corpus using Claude Code, while keeping relationship discovery outside the LLM extraction step.

The central question is:

> Can independently extracted entity-and-dimension representations contain enough structure for mathematical and algorithmic methods to discover meaningful relationships between entities, even when those relationships were not explicitly stored as relationship edges?

## Stage 1: Corpus Extraction

A corpus will be processed event-by-event.

For each event:

```text
Event
  ↓
LLM semantic interpretation
  ↓
Entities
  ↓
Entity-specific dimensions
```

The extraction step must not perform cross-event relationship discovery.

It must not infer relationships merely because entities occur together.

It must not infer chronology or causality across separate events.

It must produce semantic information associated with each entity within the individual event.

The LLM therefore acts as a semantic interpreter, not as the relationship engine.

## Stage 2: Corpus-Level NDM Representation

The independently extracted event-level records will be accumulated into a corpus-level representation.

Conceptually:

```text
Event E1
  ├── Entity A
  │     ├── Dimension
  │     └── Dimension
  └── Entity B
        └── Dimension

Event E2
  ├── Entity A
  │     └── Dimension
  └── Entity C
        ├── Dimension
        └── Dimension
```

The same entity may therefore appear across many events with different dimensions and different semantic states.

No explicit relationship graph is required at ingestion time.

## Stage 3: Mathematical Representation

The entity-dimensional structure will then be converted into mathematical representations suitable for analysis.

The first experiments should investigate multiple signals rather than assuming that a single embedding is sufficient.

Potential signals include:

- semantic similarity between dimensions
- dimension overlap
- dimension compatibility
- repeated appearance of entity pairs under compatible dimensions
- directional or role information
- state information
- temporal information where explicitly available
- recurrence and distribution across the corpus

For an entity `E`, its representation can be considered as a function of the dimensions associated with that entity:

```text
E = f(D1, D2, ..., Dn)
```

Similarity between entities can then be measured mathematically:

```text
sim(E1, E2)
```

The similarity itself should initially be treated as a mathematical signal, not automatically as a semantic relationship.

## Stage 4: Candidate Relationship Discovery

The algorithmic layer will search for structure in the mathematical representation.

A candidate relationship may depend on a combination of signals such as:

```text
R(A, B) = f(
    semantic similarity,
    dimension overlap,
    dimension compatibility,
    recurrence,
    directionality,
    state compatibility,
    temporal structure
)
```

This is a candidate mathematical formulation, not a fixed final algorithm.

The experiment should determine which signals actually contribute useful structure.

## Stage 5: Entity Geometry / Plotting

Entities will be projected into a lower-dimensional space for inspection and analysis.

The visualization is a diagnostic tool rather than proof of a relationship.

The goal is to determine whether entities with meaningful semantic connections form measurable structure in the resulting representation.

For example:

```text
            Entity Space

       ● Entity A
                    ● Entity B

                          ● Entity C
        ● Entity D
```

The plot should help identify clustering, proximity, separation, and other geometric structure that can later be tested quantitatively.

## Critical Constraint

The system must not confuse mathematical proximity with a verified semantic relationship.

The intended pipeline is:

```text
mathematical proximity
        ↓
candidate relationship
        ↓
algorithmic validation
        ↓
relationship hypothesis
```

The experiment should therefore distinguish between:

- information explicitly present in the extracted dimensions
- structure discovered mathematically
- relationships validated by independent evidence

## Initial Corpus Scale

The first corpus experiment should remain small enough to inspect manually and debug:

```text
100–500 events
20–100 unique entities
multiple dimensions per entity
```

The scale can increase after the representation and relationship-discovery pipeline is stable.

## Expected Outputs

The experiment should produce artifacts such as:

```text
entities.json
entity_dimensions.json
entity_features.npy
similarity_matrix.npy
candidate_relationships.json
entity_projection.png
```

The exact formats can change during experimentation.

## What This Experiment Is Intended to Establish

This experiment is not intended to prove the complete NDM system.

It is intended to determine whether:

1. a real corpus can be converted into useful event-level entity-dimensional representations;
2. those representations preserve enough structure for mathematical processing;
3. meaningful entity structure appears without explicitly encoding a relationship graph;
4. algorithmic methods can discover candidate relationships from that structure.

If this works, the next stage is to refine the mathematical representation and relationship-discovery algorithms rather than expanding the LLM's role.
