from __future__ import annotations

from dataclasses import dataclass, asdict
from copy import deepcopy
from typing import Dict, List, Optional


@dataclass(frozen=True)
class Observation:
    observation_id: str
    proposition_id: str
    agent_id: str
    value: str
    epistemic_status: str
    observed_at: str
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None
    evidence: str = ""


class SharedMemory:
    """Append-only observation store with deterministic derived state."""

    def __init__(self) -> None:
        self._observations: Dict[str, Observation] = {}

    def append(self, observation: Observation) -> None:
        if observation.observation_id in self._observations:
            raise ValueError(f"duplicate observation_id: {observation.observation_id}")
        self._observations[observation.observation_id] = observation

    def observations_for(self, proposition_id: str) -> List[Observation]:
        return [
            deepcopy(o)
            for o in self._observations.values()
            if o.proposition_id == proposition_id
        ]

    def state(self, proposition_id: str) -> dict:
        observations = self.observations_for(proposition_id)
        values = {o.value for o in observations}
        if not observations:
            return {
                "proposition_id": proposition_id,
                "status": "unknown",
                "observations": [],
                "agents": [],
            }

        # Multiple distinct values are disputed unless temporal validity
        # clearly separates them.
        disputed = False
        if len(values) > 1:
            pairs_overlap = False
            for i, left in enumerate(observations):
                for right in observations[i + 1 :]:
                    if left.value == right.value:
                        continue
                    if _intervals_overlap(left, right):
                        pairs_overlap = True
                        break
                if pairs_overlap:
                    break
            disputed = pairs_overlap

        status = "disputed" if disputed else "consistent"
        latest = max(observations, key=lambda o: (o.observed_at, o.observation_id))
        return {
            "proposition_id": proposition_id,
            "status": status,
            "current_value": latest.value,
            "current_observation_id": latest.observation_id,
            "observations": [asdict(o) for o in observations],
            "agents": sorted({o.agent_id for o in observations}),
        }

    def snapshot(self) -> dict:
        return {
            "observations": [asdict(o) for o in self._observations.values()]
        }

    @classmethod
    def from_snapshot(cls, snapshot: dict) -> "SharedMemory":
        store = cls()
        for raw in snapshot.get("observations", []):
            store.append(Observation(**raw))
        return store


def _intervals_overlap(a: Observation, b: Observation) -> bool:
    # Missing bounds mean the observation is open-ended and therefore overlaps
    # unless the other interval is explicitly outside it.
    a_start = a.valid_from or ""
    b_start = b.valid_from or ""
    a_end = a.valid_to or "9999-12-31T23:59:59"
    b_end = b.valid_to or "9999-12-31T23:59:59"
    return a_start <= b_end and b_start <= a_end
