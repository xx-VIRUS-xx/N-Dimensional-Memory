# Spherical NDM v1: Space Definition

## Primitive

An entity is a point.

For an entity E appearing in event t:

```text
P(E, t)
```

is a distinct point in the NDM space.

## Reference dimension

The first reference dimension is:

```text
conversationByTime
```

The initial corpus uses:

```text
t0, t1, ..., t9
```

as the ordered event positions.

The extracted dimensions from the LLM are semantic information associated with P(E,t).

## Not defined yet

This experiment deliberately does not define:

- distance
- similarity
- correlation
- entity collapse
- dimension collapse
- event relation
- ambiguity score
- relationship edges

Those are research questions to be developed after visual inspection.
