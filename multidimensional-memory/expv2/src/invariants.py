"""Conservative semantic invariants for the first EXP-V2 baseline."""


def derive_relations(canonical):
    """Only emit obvious structural relations already present in common dimensions.

    This is deliberately tiny. Relationship inference belongs to EXP-V3.
    """
    by_surface = {p["surface"]: p for p in canonical}
    relations = []

    # Known invariant from EXP-V1: Rahul performs play and play has football as object.
    if {"rahul", "play", "football"}.issubset(by_surface):
        if "actor" in by_surface["rahul"]["dimensions"]["common"] and "action" in by_surface["play"]["dimensions"]["common"]:
            relations.append({"from": "rahul", "type": "performs", "to": "play", "status": "candidate"})
        if "object" in by_surface["football"]["dimensions"]["common"]:
            relations.append({"from": "play", "type": "object", "to": "football", "status": "candidate"})

    return relations
