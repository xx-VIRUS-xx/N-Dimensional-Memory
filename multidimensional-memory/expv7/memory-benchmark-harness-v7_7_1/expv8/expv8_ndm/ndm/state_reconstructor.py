from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Set


@dataclass
class ReconstructedState:
    """
    Deterministic state view over an NDM memory document.

    This layer does NOT answer questions.
    It only reconstructs and exposes semantic state.
    """

    memory: Dict[str, Any]

    entities: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    propositions: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    events: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    beliefs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    ambiguities: List[Dict[str, Any]] = field(default_factory=list)
    negative_knowledge: List[Dict[str, Any]] = field(default_factory=list)

    superseded_ids: Set[str] = field(default_factory=set)
    superseding_map: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.entities = {
            self._id(item): item
            for item in self.memory.get("entities", [])
            if self._id(item)
        }

        self.propositions = {
            self._id(item): item
            for item in self.memory.get("propositions", [])
            if self._id(item)
        }

        self.events = {
            self._id(item): item
            for item in self.memory.get("events", [])
            if self._id(item)
        }

        self.relationships = list(
            self.memory.get("relationships", [])
        )

        self.beliefs = {
            self._belief_id(item): item
            for item in self.memory.get("beliefs", [])
            if self._belief_id(item)
        }

        self.ambiguities = list(
            self.memory.get("ambiguities", [])
        )

        self.negative_knowledge = list(
            self.memory.get("negative_knowledge", [])
        )

        self._build_lifecycle_indexes()

    @staticmethod
    def _id(item: Dict[str, Any]) -> str | None:
        value = item.get("id")
        return str(value) if value is not None else None

    @staticmethod
    def _belief_id(item: Dict[str, Any]) -> str | None:
        value = item.get("id")
        return str(value) if value is not None else None

    @staticmethod
    def _relation_type(item: Dict[str, Any]) -> str:
        return str(item.get("type", "")).strip().lower()

    @staticmethod
    def _relation_source(item: Dict[str, Any]) -> str | None:
        value = item.get("source")
        if value is None:
            value = item.get("from")
        return str(value) if value is not None else None

    @staticmethod
    def _relation_target(item: Dict[str, Any]) -> str | None:
        value = item.get("target")
        if value is None:
            value = item.get("to")
        return str(value) if value is not None else None

    def _build_lifecycle_indexes(self) -> None:
        """
        Build deterministic supersession indexes.

        Two sources are recognized:
        1. proposition.status == "superseded"
        2. relationship.type == "supersedes"

        The relationship is authoritative for identifying the replacement.
        """

        for proposition_id, proposition in self.propositions.items():
            if proposition.get("status") == "superseded":
                self.superseded_ids.add(proposition_id)

        for relation in self.relationships:
            if self._relation_type(relation) != "supersedes":
                continue

            source = self._relation_source(relation)
            target = self._relation_target(relation)

            if not source or not target:
                continue

            self.superseded_ids.add(target)
            self.superseding_map[target] = source

    # ------------------------------------------------------------------
    # Proposition state
    # ------------------------------------------------------------------

    def current_propositions(self) -> List[Dict[str, Any]]:
        """
        Return propositions that are not superseded.

        Rejected propositions are retained because rejection is semantic
        information, not the same thing as supersession.
        """

        return [
            proposition
            for proposition_id, proposition in self.propositions.items()
            if proposition_id not in self.superseded_ids
        ]

    def historical_propositions(self) -> List[Dict[str, Any]]:
        """
        Return all propositions, including superseded propositions.
        """

        return list(self.propositions.values())

    def proposition_history(self, proposition_id: str) -> List[Dict[str, Any]]:
        """
        Return the lifecycle chain containing a proposition.

        For the current V8 representation this follows supersession links
        in both directions.
        """

        proposition_id = str(proposition_id)

        if proposition_id not in self.propositions:
            return []

        chain_ids: Set[str] = {proposition_id}

        changed = True
        while changed:
            changed = False

            for old_id, new_id in self.superseding_map.items():
                if old_id in chain_ids and new_id not in chain_ids:
                    chain_ids.add(new_id)
                    changed = True

                if new_id in chain_ids and old_id not in chain_ids:
                    chain_ids.add(old_id)
                    changed = True

        propositions = [
            self.propositions[item_id]
            for item_id in chain_ids
            if item_id in self.propositions
        ]

        return sorted(
            propositions,
            key=lambda item: (
                item.get("valid_from") or "",
                item.get("id") or "",
            ),
        )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    def relationships_for(
        self,
        object_ids: Set[str],
    ) -> List[Dict[str, Any]]:
        """
        Return relationships touching any supplied object.
        """

        normalized = {str(value) for value in object_ids}

        result = []

        for relation in self.relationships:
            source = self._relation_source(relation)
            target = self._relation_target(relation)

            if source in normalized or target in normalized:
                result.append(relation)

        return result

    # ------------------------------------------------------------------
    # Beliefs
    # ------------------------------------------------------------------

    def beliefs_for_proposition(
        self,
        proposition_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Find beliefs referring to a proposition.

        Supports both:
        - proposition_id
        - proposition

        This is intentional because the current writer output and original
        schema used different field names.
        """

        proposition_id = str(proposition_id)

        result = []

        for belief in self.beliefs.values():
            referenced = belief.get("proposition_id")

            if referenced is None:
                referenced = belief.get("proposition")

            if str(referenced) == proposition_id:
                result.append(belief)

        return result

    # ------------------------------------------------------------------
    # Evidence packet construction
    # ------------------------------------------------------------------

    def build_packet(
        self,
        proposition_ids: List[str] | None = None,
        event_ids: List[str] | None = None,
        include_history: bool = False,
        include_relationships: bool = True,
        include_beliefs: bool = True,
        include_negative_knowledge: bool = True,
    ) -> Dict[str, Any]:
        """
        Construct a deterministic state/evidence packet.

        This function does not perform semantic question answering.
        """

        proposition_ids = proposition_ids or []
        event_ids = event_ids or []

        selected_propositions: List[Dict[str, Any]] = []

        if include_history:
            for proposition_id in proposition_ids:
                selected_propositions.extend(
                    self.proposition_history(proposition_id)
                )
        else:
            for proposition_id in proposition_ids:
                proposition = self.propositions.get(str(proposition_id))

                if proposition is None:
                    continue

                if str(proposition_id) in self.superseded_ids:
                    replacement_id = self.superseding_map.get(
                        str(proposition_id)
                    )

                    if replacement_id:
                        replacement = self.propositions.get(replacement_id)

                        if replacement:
                            selected_propositions.append(replacement)

                    continue

                selected_propositions.append(proposition)

        # Deduplicate propositions while preserving deterministic order.
        selected_propositions = self._dedupe_by_id(
            selected_propositions
        )

        selected_events = [
            self.events[event_id]
            for event_id in event_ids
            if event_id in self.events
        ]

        object_ids = {
            str(item.get("id"))
            for item in selected_propositions + selected_events
            if item.get("id") is not None
        }

        selected_relationships = []

        if include_relationships:
            selected_relationships = self.relationships_for(object_ids)

        selected_beliefs = []

        if include_beliefs:
            for proposition in selected_propositions:
                proposition_id = proposition.get("id")

                if proposition_id is None:
                    continue

                selected_beliefs.extend(
                    self.beliefs_for_proposition(str(proposition_id))
                )

        selected_negative = []

        if include_negative_knowledge:
            selected_negative = list(self.negative_knowledge)

        return {
            "source": self.memory.get("source"),
            "propositions": selected_propositions,
            "events": selected_events,
            "relationships": selected_relationships,
            "beliefs": selected_beliefs,
            "negative_knowledge": selected_negative,
        }

    @staticmethod
    def _dedupe_by_id(
        items: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        seen: Set[str] = set()
        result = []

        for item in items:
            item_id = item.get("id")

            if item_id is None:
                result.append(item)
                continue

            item_id = str(item_id)

            if item_id in seen:
                continue

            seen.add(item_id)
            result.append(item)

        return result