from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Set


@dataclass
class QuerySpec:
    query_id: str
    question: str
    mode: str = "current"
    subject: Optional[str] = None
    scope: Optional[str] = None


class NDMRetriever:
    """
    NDM V3 deterministic state-aware retriever.

    V3 change:
        Same scope != same lifecycle.

    Lifecycle reconstruction follows explicit semantic edges:
        supersedes

    It does NOT use generic:
        follows

    as a semantic lifecycle edge.

    Therefore:

        PROP_001 --superseded by--> PROP_003

    is a lifecycle chain, while:

        PROP_005

    remains an independent rejected alternative.
    """

    def __init__(self, memory: Dict[str, Any]):

        self.memory = memory

        self.entities = {
            str(x["id"]): x
            for x in memory.get("entities", [])
            if x.get("id") is not None
        }

        self.propositions = {
            str(x["id"]): x
            for x in memory.get("propositions", [])
            if x.get("id") is not None
        }

        self.events = {
            str(x["id"]): x
            for x in memory.get("events", [])
            if x.get("id") is not None
        }

        self.relationships = list(
            memory.get("relationships", [])
        )

        self.beliefs = list(
            memory.get("beliefs", [])
        )

        self.ambiguities = list(
            memory.get("ambiguities", [])
        )

        self.negative_knowledge = list(
            memory.get("negative_knowledge", [])
        )

        self.superseded_by: Dict[str, str] = {}
        self.supersedes: Dict[str, Set[str]] = {}

        self._build_lifecycle_index()

    # ================================================================
    # NORMALIZATION
    # ================================================================

    @staticmethod
    def norm(value: Any) -> str:
        if value is None:
            return ""

        return str(value).strip().lower()

    # ================================================================
    # LIFECYCLE INDEX
    # ================================================================

    def _build_lifecycle_index(self) -> None:

        for relation in self.relationships:

            if relation.get("type") != "supersedes":
                continue

            source = relation.get("source")
            target = relation.get("target")

            if source is None or target is None:
                continue

            source = str(source)
            target = str(target)

            self.superseded_by[target] = source

            self.supersedes.setdefault(
                source,
                set(),
            ).add(target)

    # ================================================================
    # CURRENT STATE
    # ================================================================

    def is_superseded(
        self,
        proposition_id: str,
    ) -> bool:

        return proposition_id in self.superseded_by

    def is_rejected(
        self,
        proposition_id: str,
    ) -> bool:

        proposition = self.propositions.get(
            proposition_id
        )

        if not proposition:
            return False

        return (
            proposition.get("status")
            == "rejected"
        )

    def is_current(
        self,
        proposition_id: str,
    ) -> bool:

        return (
            not self.is_superseded(
                proposition_id
            )
            and not self.is_rejected(
                proposition_id
            )
        )

    # ================================================================
    # BELIEFS
    # ================================================================

    def beliefs_for_proposition(
        self,
        proposition_id: str,
    ) -> List[Dict[str, Any]]:

        return [
            belief
            for belief in self.beliefs
            if str(
                belief.get("proposition")
            ) == proposition_id
        ]

    def holders_for_proposition(
        self,
        proposition_id: str,
    ) -> Set[str]:

        return {
            str(
                belief.get("holder")
            )
            for belief in self.beliefs_for_proposition(
                proposition_id
            )
            if belief.get("holder") is not None
        }

    # ================================================================
    # ENTITY / SUBJECT
    # ================================================================

    def proposition_matches_subject(
    self,
    proposition: Dict[str, Any],
    subject: Optional[str],
    ) -> bool:

        if not subject:
            return True

        subject = self.norm(subject)

        proposition_id = str(
            proposition.get("id")
        )

        if self.norm(proposition.get("subject")) == subject:
            return True

        if self.norm(proposition.get("object")) == subject:
            return True

        if subject in {
            self.norm(x)
            for x in self.holders_for_proposition(
                proposition_id
            )
        }:
            return True

        provenance = proposition.get("provenance")

        if isinstance(provenance, dict):
            event_id = provenance.get("span")
            event = self.events.get(str(event_id))

            if event:
                participants = {
                    self.norm(x)
                    for x in event.get("participants", [])
                }

                if subject in participants:
                    return True

        return False

    # ================================================================
    # SCOPE
    # ================================================================

    def proposition_matches_scope(
        self,
        proposition: Dict[str, Any],
        scope: Optional[str],
    ) -> bool:

        if not scope:
            return True

        proposition_scope = self.norm(
            proposition.get("scope")
        )

        requested_scope = self.norm(
            scope
        )

        if not proposition_scope:
            return False

        return (
            proposition_scope
            == requested_scope
        )

    # ================================================================
    # BASE CANDIDATES
    # ================================================================

    def candidate_propositions(
        self,
        spec: QuerySpec,
    ) -> List[Dict[str, Any]]:

        result = []

        for proposition in self.propositions.values():

            if not self.proposition_matches_subject(
                proposition,
                spec.subject,
            ):
                continue

            if not self.proposition_matches_scope(
                proposition,
                spec.scope,
            ):
                continue

            result.append(
                proposition
            )

        return result

    # ================================================================
    # LIFECYCLE
    # ================================================================

    def lifecycle_chain(
        self,
        proposition_id: str,
    ) -> Set[str]:

        """
        Return the explicit supersession chain connected
        to proposition_id.

        Example:

            PROP_001 <-superseded by- PROP_003

        returns:

            {PROP_001, PROP_003}

        If later:

            PROP_005 supersedes PROP_003

        it becomes:

            {PROP_001, PROP_003, PROP_005}

        No generic temporal/follows edges are traversed.
        """

        result = {
            proposition_id
        }

        queue = [
            proposition_id
        ]

        while queue:

            current = queue.pop()

            # Older state.
            for older in self.supersedes.get(
                current,
                set(),
            ):

                if older not in result:

                    result.add(
                        older
                    )

                    queue.append(
                        older
                    )

            # Newer state.
            newer = self.superseded_by.get(
                current
            )

            if (
                newer is not None
                and newer not in result
            ):

                result.add(
                    newer
                )

                queue.append(
                    newer
                )

        return result

    # ================================================================
    # FIND LIFECYCLE ANCHORS
    # ================================================================

    def find_lifecycle_anchors(
        self,
        candidates: List[Dict[str, Any]],
        spec: QuerySpec,
    ) -> List[str]:

        """
        Select propositions that plausibly anchor the requested
        lifecycle.

        For current decisions:
            choose current proposition(s).

        For historical/lifecycle/temporal queries:
            prefer non-rejected propositions.

        Rejected alternatives are NOT lifecycle anchors unless
        the query explicitly targets rejection.
        """

        candidate_ids = {
            str(
                proposition["id"]
            )
            for proposition in candidates
        }

        non_rejected = [
            proposition
            for proposition in candidates
            if proposition.get("status")
            != "rejected"
        ]

        if not non_rejected:
            return sorted(
                candidate_ids
            )

        current = [
            proposition
            for proposition in non_rejected
            if self.is_current(
                str(proposition["id"])
            )
        ]

        # Current state is the strongest lifecycle anchor.
        if current:
            return [
                str(
                    proposition["id"]
                )
                for proposition in current
            ]

        return [
            str(
                proposition["id"]
            )
            for proposition in non_rejected
        ]

    # ================================================================
    # EVENT RESOLUTION
    # ================================================================

    def event_for_proposition(
        self,
        proposition: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:

        provenance = proposition.get(
            "provenance"
        )

        if not isinstance(
            provenance,
            dict,
        ):
            return None

        event_id = provenance.get(
            "span"
        )

        if event_id is None:
            return None

        return self.events.get(
            str(event_id)
        )

    # ================================================================
    # RELATIONSHIPS
    # ================================================================

    def relationships_for(
        self,
        proposition_ids: Set[str],
        event_ids: Set[str],
        mode: str,
    ) -> List[Dict[str, Any]]:

        selected = (
            proposition_ids
            | event_ids
        )

        if mode in {
            "historical",
            "lifecycle",
            "temporal",
        }:

            allowed = {
                "supersedes"
            }

        elif mode == "current":

            allowed = {
                "supersedes"
            }

        elif mode == "causal":

            allowed = {
                "caused"
            }

        elif mode == "contradiction":

            allowed = {
                "contradicts"
            }

        else:

            allowed = set()

        result = []

        for relation in self.relationships:

            if relation.get(
                "type"
            ) not in allowed:
                continue

            source = str(
                relation.get(
                    "source"
                )
            )

            target = str(
                relation.get(
                    "target"
                )
            )

            if (
                source in selected
                and target in selected
            ):

                result.append(
                    relation
                )

        return result

    # ================================================================
    # BELIEFS
    # ================================================================

    def beliefs_for(
        self,
        proposition_ids: Set[str],
    ) -> List[Dict[str, Any]]:

        return [
            belief
            for belief in self.beliefs
            if str(
                belief.get(
                    "proposition"
                )
            ) in proposition_ids
        ]

    # ================================================================
    # NEGATIVE KNOWLEDGE
    # ================================================================

    def negative_for(
        self,
        proposition_ids: Set[str],
    ) -> List[Dict[str, Any]]:

        return [
            item
            for item in self.negative_knowledge
            if str(
                item.get(
                    "related_proposition"
                )
            ) in proposition_ids
        ]

    # ================================================================
    # CURRENT QUERY
    # ================================================================

    def retrieve_current(
        self,
        candidates: List[Dict[str, Any]],
        spec: QuerySpec,
    ) -> Dict[str, Any]:

        selected = [
            proposition
            for proposition in candidates
            if self.is_current(
                str(
                    proposition["id"]
                )
            )
        ]

        proposition_ids = {
            str(
                proposition["id"]
            )
            for proposition in selected
        }

        return self.build_result(
            spec,
            proposition_ids,
        )

    # ================================================================
    # HISTORICAL / LIFECYCLE / TEMPORAL
    # ================================================================

    def retrieve_lifecycle(
        self,
        candidates: List[Dict[str, Any]],
        spec: QuerySpec,
    ) -> Dict[str, Any]:

        anchors = self.find_lifecycle_anchors(
            candidates,
            spec,
        )

        proposition_ids: Set[str] = set()

        for anchor in anchors:

            proposition_ids.update(
                self.lifecycle_chain(
                    anchor
                )
            )

        # Never pull rejected alternatives merely because
        # they share subject/scope.
        proposition_ids = {
            proposition_id
            for proposition_id in proposition_ids
            if not self.is_rejected(
                proposition_id
            )
        }

        return self.build_result(
            spec,
            proposition_ids,
        )

    # ================================================================
    # CAUSAL
    # ================================================================

    def retrieve_causal(
        self,
        candidates: List[Dict[str, Any]],
        spec: QuerySpec,
    ) -> Dict[str, Any]:

        candidate_ids = {
            str(
                proposition["id"]
            )
            for proposition in candidates
        }

        causal_ids = set()

        for relation in self.relationships:

            if relation.get(
                "type"
            ) != "caused":
                continue

            source = str(
                relation.get(
                    "source"
                )
            )

            if source in candidate_ids:

                causal_ids.add(
                    source
                )

        return self.build_result(
            spec,
            causal_ids,
        )

    # ================================================================
    # BELIEF
    # ================================================================

    def retrieve_belief(
    self,
    candidates: List[Dict[str, Any]],
    spec: QuerySpec,
    ) -> Dict[str, Any]:

        """
        Belief retrieval is belief-first.

        The holder is the primary candidate generator.

        We do NOT require the proposition to match the requested
        subject/scope before discovering the belief.

        Example:

            BELIEF_003
                holder = ENT_BOB
                proposition = PROP_004

        should retrieve PROP_004 even though the proposition's
        subject is ENT_POSTGRESQL rather than ENT_BOB.
        """

        proposition_ids: Set[str] = set()

        # ------------------------------------------------------------
        # Step 1: discover propositions through beliefs
        # ------------------------------------------------------------

        for belief in self.beliefs:

            holder = belief.get(
                "holder"
            )

            proposition_id = belief.get(
                "proposition"
            )

            if proposition_id is None:
                continue

            # If a holder is specified, it is the primary filter.
            if spec.subject:

                if str(holder) != str(
                    spec.subject
                ):
                    continue

            proposition_id = str(
                proposition_id
            )

            proposition = self.propositions.get(
                proposition_id
            )

            if proposition is None:
                continue

            # --------------------------------------------------------
            # Scope is secondary.
            #
            # A belief query should not lose the belief merely because
            # the proposition subject is the same entity being discussed.
            # If scope is supplied, require exact scope match.
            # --------------------------------------------------------

            if spec.scope:

                if not self.proposition_matches_scope(
                    proposition,
                    spec.scope,
                ):
                    continue

            proposition_ids.add(
                proposition_id
            )

        return self.build_result(
            spec,
            proposition_ids,
        )

    # ================================================================
    # NEGATIVE
    # ================================================================

    def retrieve_negative(
        self,
        candidates: List[Dict[str, Any]],
        spec: QuerySpec,
    ) -> Dict[str, Any]:

        ids = {
            str(
                proposition["id"]
            )
            for proposition in candidates
            if proposition.get(
                "status"
            )
            == "rejected"
        }

        return self.build_result(
            spec,
            ids,
        )

    # ================================================================
    # SCOPE QUERY
    # ================================================================

    def retrieve_scope(
        self,
        spec: QuerySpec,
    ) -> Dict[str, Any]:

        # Current state of requested scope.
        current = []

        for proposition in self.propositions.values():

            if not self.proposition_matches_scope(
                proposition,
                spec.scope,
            ):
                continue

            if self.is_current(
                str(
                    proposition["id"]
                )
            ):

                current.append(
                    proposition
                )

        ids = {
            str(
                proposition["id"]
            )
            for proposition in current
        }

        return self.build_result(
            spec,
            ids,
        )

    # ================================================================
    # CROSS-SCOPE CONTRADICTION
    # ================================================================

    def retrieve_contradiction(
        self,
        spec: QuerySpec,
    ) -> Dict[str, Any]:

        """
        Cross-scope comparison retrieval.

        This method retrieves candidate propositions for a
        contradiction/compatibility question.

        It does NOT decide whether the propositions actually
        contradict one another.

        Candidate discovery uses:
            1. current propositions in the requested scope
            2. beliefs associated with entities appearing in
               those propositions
            3. propositions referenced by those beliefs

        No proposition IDs are hardcoded.
        """

        # ------------------------------------------------------------
        # 1. Current propositions in requested scope
        # ------------------------------------------------------------

        scoped = []

        for proposition in self.propositions.values():

            proposition_id = str(
                proposition.get("id")
            )

            if not self.is_current(
                proposition_id
            ):
                continue

            if spec.scope:

                if not self.proposition_matches_scope(
                    proposition,
                    spec.scope,
                ):
                    continue

            scoped.append(
                proposition
            )

        proposition_ids = {
            str(
                proposition["id"]
            )
            for proposition in scoped
        }

        # ------------------------------------------------------------
        # 2. Extract semantic entities from the scoped propositions
        # ------------------------------------------------------------

        relevant_entities: Set[str] = set()

        for proposition in scoped:

            subject = proposition.get(
                "subject"
            )

            object_ = proposition.get(
                "object"
            )

            if subject:
                relevant_entities.add(
                    str(subject)
                )

            if object_:
                relevant_entities.add(
                    str(object_)
                )

        # ------------------------------------------------------------
        # 3. Find beliefs whose proposition refers to one of those
        #    semantic entities.
        #
        #    Example:
        #
        #    PROP_003
        #       object = ENT_DYNAMODB
        #       text mentions PostgreSQL
        #
        #    PROP_004
        #       subject = ENT_POSTGRESQL
        #
        #    We therefore also inspect the proposition text and
        #    entity names for semantic overlap.
        # ------------------------------------------------------------

        relevant_names = set()

        for entity_id in relevant_entities:

            entity = self.entities.get(
                entity_id
            )

            if entity:

                name = entity.get(
                    "name"
                )

                if name:
                    relevant_names.add(
                        self.norm(name)
                    )

        # Also collect entities explicitly mentioned in the
        # proposition text.
        for proposition in scoped:

            text = self.norm(
                proposition.get(
                    "text"
                )
            )

            for entity in self.entities.values():

                name = entity.get(
                    "name"
                )

                if not name:
                    continue

                if self.norm(name) in text:

                    relevant_names.add(
                        self.norm(name)
                    )

        # ------------------------------------------------------------
        # 4. Belief-first expansion.
        #
        #    Any current belief whose proposition refers to one of
        #    the relevant entities becomes a candidate.
        # ------------------------------------------------------------

        for belief in self.beliefs:

            proposition_id = belief.get(
                "proposition"
            )

            if proposition_id is None:
                continue

            proposition_id = str(
                proposition_id
            )

            proposition = self.propositions.get(
                proposition_id
            )

            if proposition is None:
                continue

            if not self.is_current(
                proposition_id
            ):
                continue

            subject = proposition.get(
                "subject"
            )

            object_ = proposition.get(
                "object"
            )

            matches_entity = (
                subject is not None
                and str(subject)
                in relevant_entities
            ) or (
                object_ is not None
                and str(object_)
                in relevant_entities
            )

            text = self.norm(
                proposition.get(
                    "text"
                )
            )

            matches_name = any(
                name in text
                for name in relevant_names
            )

            if matches_entity or matches_name:

                proposition_ids.add(
                    proposition_id
                )

        # ------------------------------------------------------------
        # 5. Build the evidence packet.
        #
        #    No contradiction edge is fabricated here.
        # ------------------------------------------------------------

        return self.build_result(
            spec,
            proposition_ids,
        )

    # ================================================================
    # PUBLIC API
    # ================================================================
    def retrieve_historical(
    self,
    candidates: List[Dict[str, Any]],
    spec: QuerySpec,
    ) -> Dict[str, Any]:

        """
        Historical retrieval asks:

            What was the state at the beginning/original point
            of the requested semantic scope?

        It does NOT expand the entire lifecycle.

        For the current adversarial fixture:

            PROP_001 -> PostgreSQL
            PROP_003 -> DynamoDB

        Q001 therefore returns only PROP_001.

        Lifecycle queries are responsible for returning both.
        """

        valid_candidates = [
            proposition
            for proposition in candidates
            if proposition.get("status")
            != "rejected"
        ]

        if not valid_candidates:
            return self.build_result(
                spec,
                set(),
            )

        # Earliest valid proposition in the requested scope.
        # Use validity first, then provenance/event timestamp
        # as deterministic fallback.
        def sort_key(proposition):

            valid_from = (
                proposition.get(
                    "valid_from"
                )
                or ""
            )

            event = self.event_for_proposition(
                proposition
            )

            timestamp = (
                event.get("timestamp", "")
                if event
                else ""
            )

            return (
                valid_from,
                timestamp,
                str(
                    proposition.get("id")
                ),
            )

        earliest = min(
            valid_candidates,
            key=sort_key,
        )

        return self.build_result(
            spec,
            {
                str(
                    earliest["id"]
                )
            },
        )
    def retrieve_lifecycle(
    self,
    candidates: List[Dict[str, Any]],
    spec: QuerySpec,
    ) -> Dict[str, Any]:

        anchors = self.find_lifecycle_anchors(
            candidates,
            spec,
        )

        proposition_ids: Set[str] = set()

        for anchor in anchors:
            proposition_ids.update(
                self.lifecycle_chain(anchor)
            )

        # Lifecycle means explicit semantic state transitions.
        # Rejected alternatives are not automatically part of the
        # lifecycle unless an explicit supersedes edge connects them.
        proposition_ids = {
            proposition_id
            for proposition_id in proposition_ids
            if not self.is_rejected(proposition_id)
        }

        return self.build_result(
            spec,
            proposition_ids,
        )

        # ================================================================
    # RESULT BUILDER
    # ================================================================

    def build_result(
        self,
        spec: QuerySpec,
        proposition_ids: Set[str],
    ) -> Dict[str, Any]:

        selected_propositions = [
            self.propositions[
                proposition_id
            ]
            for proposition_id in sorted(
                proposition_ids
            )
            if proposition_id in self.propositions
        ]

        # Resolve propositions -> source events through provenance.
        event_ids: Set[str] = set()

        for proposition in selected_propositions:

            event = self.event_for_proposition(
                proposition
            )

            if event is not None:

                event_ids.add(
                    str(
                        event["id"]
                    )
                )

        selected_events = [
            self.events[event_id]
            for event_id in sorted(
                event_ids
            )
            if event_id in self.events
        ]

        # Resolve semantic relationships relevant to this result.
        relationships = self.relationships_for(
            proposition_ids,
            event_ids,
            spec.mode,
        )

        # Resolve beliefs attached to selected propositions.
        beliefs = self.beliefs_for(
            proposition_ids
        )

        # Resolve negative knowledge attached to selected propositions.
        negative_knowledge = self.negative_for(
            proposition_ids
        )

        return {
            "query_id": spec.query_id,
            "question": spec.question,
            "mode": spec.mode,

            "propositions":
                selected_propositions,

            "events":
                selected_events,

            "relationships":
                relationships,

            "beliefs":
                beliefs,

            "negative_knowledge":
                negative_knowledge,

            "selected_proposition_ids":
                sorted(
                    proposition_ids
                ),

            "selected_event_ids":
                sorted(
                    event_ids
                ),
        }
    
    def retrieve(
        self,
        spec: QuerySpec,
    ) -> Dict[str, Any]:

        # ------------------------------------------------------------
        # Special query modes with their own candidate-generation
        # strategy.
        # ------------------------------------------------------------

        if spec.mode == "contradiction":
            return self.retrieve_contradiction(
                spec
            )

        if spec.mode == "scope":
            return self.retrieve_scope(
                spec
            )

        # ------------------------------------------------------------
        # Standard proposition candidate generation.
        # ------------------------------------------------------------

        candidates = self.candidate_propositions(
            spec
        )

        # ------------------------------------------------------------
        # CURRENT
        # ------------------------------------------------------------

        if spec.mode == "current":

            return self.retrieve_current(
                candidates,
                spec,
            )

        # ------------------------------------------------------------
        # HISTORICAL
        #
        # Return the earliest state in the requested scope.
        # Do not expand the entire lifecycle.
        # ------------------------------------------------------------

        if spec.mode == "historical":

            return self.retrieve_historical(
                candidates,
                spec,
            )

        # ------------------------------------------------------------
        # LIFECYCLE
        #
        # Follow explicit supersedes relationships only.
        # ------------------------------------------------------------

        if spec.mode == "lifecycle":

            return self.retrieve_lifecycle(
                candidates,
                spec,
            )

        # ------------------------------------------------------------
        # TEMPORAL
        #
        # For V3.1, temporal reconstruction follows the explicit
        # lifecycle chain.
        # ------------------------------------------------------------

        if spec.mode == "temporal":

            return self.retrieve_lifecycle(
                candidates,
                spec,
            )

        # ------------------------------------------------------------
        # CAUSAL
        # ------------------------------------------------------------

        if spec.mode == "causal":

            return self.retrieve_causal(
                candidates,
                spec,
            )

        # ------------------------------------------------------------
        # BELIEF
        #
        # retrieve_belief() performs belief-first candidate
        # generation internally.
        # ------------------------------------------------------------

        if spec.mode == "belief":

            return self.retrieve_belief(
                candidates,
                spec,
            )

        # ------------------------------------------------------------
        # NEGATIVE KNOWLEDGE
        # ------------------------------------------------------------

        if spec.mode == "negative":

            return self.retrieve_negative(
                candidates,
                spec,
            )

        # ------------------------------------------------------------
        # Unknown mode.
        #
        # Deterministic fallback rather than silently pretending
        # the requested retrieval semantics were understood.
        # ------------------------------------------------------------

        return self.build_result(
            spec,
            {
                str(
                    proposition["id"]
                )
                for proposition in candidates
            },
        )