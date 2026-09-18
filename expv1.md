# EXP-V1: Agent-Based Multidimensional Memory Representation

## 0. Objective

The first experiment should use **coding agents as the model layer**, not a manually built model API.

Available agents:

- Codex
- Claude Code
- GitHub Copilot

The experiment asks:

> Can an agent transform raw conversational history into a multidimensional representation that preserves reusable semantic points, temporal changes, actions, states, and ambiguity?

We are **not** testing which agent is smartest.

We are testing whether the proposed representation is stable enough to become a model-independent memory substrate.

---

# 1. Core experiment

The pipeline is:

```text
                 RAW CONVERSATION
                        │
                        ▼
              ┌──────────────────┐
              │      AGENT        │
              │                  │
              │ Codex / Claude / │
              │ Copilot          │
              └────────┬─────────┘
                       │
                       ▼
          MULTIDIMENSIONAL STATE
                       │
                       ▼
              NORMALIZED POINTS
                       │
                       ▼
                 COMPARISON
```

For EXP-V1, the agent is responsible for:

- semantic interpretation
- dimensional projection
- identifying repeated concepts
- preserving ambiguity
- identifying temporal information

The agent is **not** responsible for:

- building relationships
- deciding graph topology
- calculating coordinates
- embeddings
- retrieval
- compression
- memory storage

Those are later experiments.

---

# 2. Why use agents?

We already have access to capable coding agents.

Instead of building an API integration first, use the agents directly.

This gives us three independent interpreters:

```text
Codex
Claude Code
Copilot
```

If the same underlying representation appears across them, that is more interesting than proving one particular model can produce it.

The first experiment should therefore test:

```text
Model-specific wording
        vs
Model-independent structure
```

---

# 3. Experiment directory

Create:

```bash
mkdir -p multidimensional-memory/expv1
cd multidimensional-memory/expv1

mkdir -p input
mkdir -p prompts
mkdir -p outputs/codex
mkdir -p outputs/claude
mkdir -p outputs/copilot
mkdir -p analysis
```

Expected structure:

```text
expv1/
│
├── input/
│   └── conversation_01.md
│
├── prompts/
│   └── dimensional_representation.md
│
├── outputs/
│   ├── codex/
│   ├── claude/
│   └── copilot/
│
└── analysis/
    ├── comparison.md
    └── result.md
```

---

# 4. Create the first conversation

Create:

```bash
cat > input/conversation_01.md <<'EOF'
# Conversation 01

User: Rahul loves to play football.

Assistant: That sounds like something he enjoys regularly.

User: Rahul plays football every Sunday at the park.

Assistant: So football seems to be part of his weekly routine.

User: He usually plays with his friends.

Assistant: That suggests football is also a social activity for him.

User: Rahul stopped playing football during the summer.

Assistant: So there was a period when he wasn't playing.

User: Rahul started playing again after joining a new team.

Assistant: His football activity resumed after joining the new team.
EOF
```

---

# 5. Define the dimensional representation

Create:

```bash
cat > prompts/dimensional_representation.md <<'EOF'
# EXP-V1 Agent Instruction

You are participating in an experiment on multidimensional conversational memory.

Read the supplied conversation.

Your task is to represent the conversation as a multidimensional semantic state.

This is NOT a conventional knowledge graph.

This is NOT a summary.

Do NOT create relationships merely because they seem plausible.

Do NOT invent facts.

Preserve the original evidence.

## Dimensions

Initially use:

- noun
- verb
- action
- subject
- object
- time
- place
- emotion
- feeling
- intent
- state
- actor
- target

A token or phrase may exist in multiple dimensions.

For example:

"Rahul"

may simultaneously be:

- noun
- subject
- actor

"loves"

may be:

- verb
- emotion
- feeling

"play"

may be:

- verb
- action

"football"

may be:

- noun
- object
- activity

Do not force a token into a dimension if the evidence does not support it.

## Temporal information

Preserve changes over time.

For example:

playing
→ stopped playing
→ started playing again

should not become a single static fact.

## Ambiguity

If something is ambiguous, preserve the ambiguity.

Example:

"He plays football."

If it is unclear who "He" refers to, create an unresolved ambiguity instead of silently assuming the answer.

## Evidence

Every interpretation must retain its source sentence.

## Output

Return JSON using this structure:

{
  "conversation_id": "...",

  "points": [
    {
      "point_id": "...",
      "surface": "...",
      "dimensions": [],
      "interpretations": [],
      "source_sentences": [],
      "confidence": 0.0
    }
  ],

  "temporal_states": [],

  "ambiguities": [],

  "explicit_facts": []
}

Do not generate inferred relationships.

Do not generate coordinates.

Do not generate embeddings.

Do not generate graph edges.

The purpose of this experiment is to determine whether the conversation can first be represented as reusable multidimensional points.
EOF
```

---

# 6. Establish the same experimental conditions

This is important.

All three agents must receive:

1. The exact same conversation.
2. The exact same instruction.
3. The exact same output requirements.

Do not modify the prompt for individual agents.

Otherwise we are comparing prompt engineering rather than representations.

---

# 7. Run with Codex

Start Codex:

```bash
codex
```

Give it:

```text
Read these two files:

input/conversation_01.md
prompts/dimensional_representation.md

Perform EXP-V1 exactly according to the instruction.

Write ONLY the resulting JSON to:

outputs/codex/representation.json

Do not modify the input or prompt.
Do not create additional interpretations outside the requested JSON.
```

Verify:

```bash
cat outputs/codex/representation.json
```

---

# 8. Run with Claude Code

Start Claude Code:

```bash
claude
```

Give it:

```text
Read these two files:

input/conversation_01.md
prompts/dimensional_representation.md

Perform EXP-V1 exactly according to the instruction.

Write ONLY the resulting JSON to:

outputs/claude/representation.json

Do not modify the input or prompt.
Do not create additional interpretations outside the requested JSON.
```

Verify:

```bash
cat outputs/claude/representation.json
```

---

# 9. Run with Copilot

Use Copilot in the same repository/context.

Give it:

```text
Read these two files:

input/conversation_01.md
prompts/dimensional_representation.md

Perform EXP-V1 exactly according to the instruction.

Write ONLY the resulting JSON to:

outputs/copilot/representation.json

Do not modify the input or prompt.
Do not create additional interpretations outside the requested JSON.
```

Verify:

```bash
cat outputs/copilot/representation.json
```

---

# 10. First comparison

Now we have:

```text
outputs/
├── codex/
│   └── representation.json
├── claude/
│   └── representation.json
└── copilot/
    └── representation.json
```

Do NOT ask:

> Which output is best?

Instead ask:

> What structure survives across all three outputs?

This distinction is critical.

---

# 11. Normalize the outputs manually first

Before writing a normalization algorithm, inspect the three outputs.

Create:

```bash
touch analysis/comparison.md
```

Use:

```markdown
# EXP-V1 Comparison

## Shared Points

| Concept | Codex | Claude | Copilot |
|---|---|---|---|
| Rahul | | | |
| football | | | |
| play | | | |
| friends | | | |
| Sunday | | | |
| park | | | |
| summer | | | |
| team | | | |

## Dimension Membership

### Rahul

Codex:
-

Claude:
-

Copilot:
-

### football

Codex:
-

Claude:
-

Copilot:
-

### play

Codex:
-

Claude:
-

Copilot:
-

## Temporal State

Codex:
-

Claude:
-

Copilot:
-

## Ambiguity

Codex:
-

Claude:
-

Copilot:
-

## Information Lost

Codex:
-

Claude:
-

Copilot:
-

## Model-Specific Differences

Codex:
-

Claude:
-

Copilot:
-

## Model-Independent Structure

-

## Unexpected Findings

-

## Questions Raised

-
```

---

# 12. The first thing we are looking for

Suppose the three agents produce:

```text
Codex:

Rahul
  noun
  subject
  actor

Claude:

Rahul
  noun
  subject
  person

Copilot:

Rahul
  noun
  subject
  actor
```

The words differ.

The underlying structure is similar.

That is what matters.

We should potentially normalize:

```text
Rahul
→
{
    dimensions: {
        noun,
        subject,
        actor/person
    }
}
```

The representation becomes independent of the exact model vocabulary.

---

# 13. The important test

Look for **cross-dimensional points**.

Example:

```text
Rahul
├── noun
├── subject
└── actor
```

```text
play
├── verb
└── action
```

```text
football
├── noun
├── object
└── activity
```

This is more important than a conventional:

```text
Rahul --plays--> football
```

edge.

The edge is something we may derive later.

The multidimensional points are the raw substrate.

---

# 14. Temporal test

The conversation contains:

```text
Rahul plays football.
        ↓
Rahul stopped playing football.
        ↓
Rahul started playing again.
```

The representation should preserve these as changing states.

We want to avoid:

```text
Rahul = football player
```

as a permanent static fact.

Instead we want something closer to:

```text
STATE

football participation
        │
        ├── active
        │
        ├── stopped
        │
        └── resumed
```

The actual structure will be determined in later experiments.

---

# 15. Ambiguity test

The sentence:

```text
He usually plays with his friends.
```

contains:

```text
He
```

The previous context strongly suggests Rahul.

But EXP-V1 should distinguish:

```text
explicit evidence
```

from:

```text
contextual interpretation
```

If the agent resolves it, record:

```text
resolved_from_context
```

If it does not:

```text
unresolved
```

Do not penalize either behavior yet.

We are studying how the agents interpret the raw conversation.

---

# 16. Add one deliberately ambiguous conversation

Create:

```bash
cat > input/conversation_02.md <<'EOF'
# Conversation 02

User: Rahul spoke to Arjun about football.

User: He said he might join the team next month.

User: They discussed meeting at the park.

User: The plan changed later.
EOF
```

Run the same prompt through all three agents.

Store:

```text
outputs/codex/conversation_02.json
outputs/claude/conversation_02.json
outputs/copilot/conversation_02.json
```

The key question:

```text
Who does "He" refer to?
Who does "They" refer to?
```

More importantly:

> Does the representation preserve the uncertainty when the agent cannot establish the answer?

---

# 17. Do not solve ambiguity yet

Do NOT build an entity-resolution system.

Do NOT add an LLM judge.

Do NOT vote:

```text
Codex says Rahul
Claude says Arjun
Copilot says Rahul

therefore Rahul
```

That would contaminate the experiment.

Instead record:

```text
Candidate interpretations
+
evidence
+
confidence
+
unresolved state
```

The ambiguity bucket belongs to the representation itself.

---

# 18. Test repeated evidence

Add:

```bash
cat > input/conversation_03.md <<'EOF'
# Conversation 03

User: I want to learn guitar.

Assistant: We can start with basic chords.

User: I bought a guitar yesterday.

Assistant: That gives you an instrument to practice with.

User: I practiced chords for thirty minutes.

Assistant: Consistent practice should help.

User: I want to practice again tomorrow.
EOF
```

Now inspect whether the agents expose:

```text
guitar
├── object
├── noun
└── instrument

practice
├── verb
├── action
└── activity

tomorrow
└── time

want
├── verb
└── intent
```

The important part is repeated semantic participation.

---

# 19. EXP-V1 evaluation

Score each representation on these dimensions.

Do not create a single overall score.

Use observations instead.

## Representation stability

Can the same conceptual point be identified across agents?

## Dimensional richness

Does a concept participate in multiple meaningful dimensions?

## Temporal preservation

Are state changes retained?

## Evidence preservation

Can every interpretation be traced back to source text?

## Ambiguity preservation

Can uncertainty exist without forcing a conclusion?

## Cross-model consistency

Does the underlying structure survive changes in the agent?

---

# 20. What would make EXP-V1 interesting?

A strong result would look like:

```text
Different agents
       ↓
Different wording
       ↓
Different local interpretations
       ↓
Similar underlying points
       ↓
Similar dimensional membership
       ↓
Similar temporal states
```

That would support the idea that:

> A model-independent memory representation may exist beneath model-specific language.

A weak result would look like:

```text
Codex → completely different structure
Claude → completely different structure
Copilot → completely different structure
```

That does not kill the idea.

It means the dimensional system needs stronger formal constraints.

---

# 21. What we are NOT proving

EXP-V1 does NOT prove:

```text
✓ that relationships can be automatically generated
✓ that a graph is the correct implementation
✓ that this is better than vector memory
✓ that this improves agent performance
✓ that this reduces tokens
✓ that this creates reliable long-term memory
✓ that this solves multi-agent memory
```

Those require separate experiments.

EXP-V1 only tests the representation layer.

---

# 22. The architectural hypothesis

The current hypothesis is:

```text
                 AGENT
                   │
                   │ interpretation
                   ▼
          ┌──────────────────┐
          │ Multidimensional │
          │ Representation   │
          └────────┬─────────┘
                   │
                   │ structure
                   ▼
          ┌──────────────────┐
          │ Algorithmic      │
          │ Relationship     │
          │ Layer            │
          └────────┬─────────┘
                   │
                   ▼
             Memory State
                   │
                   ▼
             Context Builder
                   │
                   ▼
                 AGENT
```

This creates a clean separation:

```text
Agent:
"What does this mean?"

Algorithm:
"What structural relationship follows?"

Memory:
"What persists?"

Agent:
"What should I retrieve and use?"
```

---

# 23. EXP-V2 trigger

Proceed to EXP-V2 only if EXP-V1 gives us evidence that:

```text
1. Concepts can be represented as reusable points.

2. Points can occupy multiple dimensions.

3. The representation preserves temporal state.

4. Ambiguity can be represented explicitly.

5. Similar underlying structure appears across agents.
```

Then EXP-V2 becomes:

# Can relationships emerge algorithmically?

The pipeline becomes:

```text
Raw Conversation
       ↓
Codex / Claude / Copilot
       ↓
Multidimensional Points
       ↓
       ┌─────────────────────────┐
       │ Algorithmic Experiments │
       │                         │
       │ co-occurrence           │
       │ intersections           │
       │ temporal proximity      │
       │ repeated evidence       │
       │ dimensional overlap    │
       │ state transitions       │
       └────────────┬────────────┘
                    ↓
             Candidate Relations
```

That is the point where the experiment stops being "can an LLM make JSON?" and starts testing the actual idea.

---

# 24. Final command checklist

```bash
mkdir -p multidimensional-memory/expv1
cd multidimensional-memory/expv1

mkdir -p input prompts
mkdir -p outputs/codex
mkdir -p outputs/claude
mkdir -p outputs/copilot
mkdir -p analysis

# Create the three input conversations
# Create the dimensional prompt

# Run through Codex
codex

# Run through Claude Code
claude

# Run through Copilot

# Inspect outputs
cat outputs/codex/representation.json
cat outputs/claude/representation.json
cat outputs/copilot/representation.json

# Record comparison
nano analysis/comparison.md

# Record conclusion
nano analysis/result.md
```

---

# EXP-V1 Deliverable

At the end:

```text
expv1/
│
├── input/
│   ├── conversation_01.md
│   ├── conversation_02.md
│   └── conversation_03.md
│
├── prompts/
│   └── dimensional_representation.md
│
├── outputs/
│   ├── codex/
│   ├── claude/
│   └── copilot/
│
└── analysis/
    ├── comparison.md
    └── result.md
```

The most valuable artifact is not the JSON.

It is the answer to:

> **What semantic structure remains stable when three different coding agents interpret the same conversation?**

That becomes the foundation for EXP-V2.
