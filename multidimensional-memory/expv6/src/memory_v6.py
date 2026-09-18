from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class AgentObservation:
    id: str
    agent: str
    proposition_key: str
    value: str
    interpretation: str
    confidence: float
    source: str
    temporal_from: Optional[str] = None
    temporal_to: Optional[str] = None


@dataclass
class PropositionMemory:
    id: str
    key: str
    observations: List[AgentObservation] = field(default_factory=list)

    def add(self, observation: AgentObservation) -> None:
        if observation.proposition_key != self.key:
            raise ValueError("observation proposition key does not match memory key")
        self.observations.append(observation)

    @property
    def values(self) -> set[str]:
        return {o.value for o in self.observations}

    @property
    def state(self) -> str:
        if len(self.values) > 1:
            return "disputed"
        if not self.observations:
            return "unresolved"
        return "supported"

    def agents(self) -> set[str]:
        return {o.agent for o in self.observations}

    def interpretations(self) -> set[str]:
        return {o.interpretation for o in self.observations}


def merge_observations(observations: List[AgentObservation]) -> List[PropositionMemory]:
    grouped: dict[str, PropositionMemory] = {}
    for obs in observations:
        memory = grouped.setdefault(obs.proposition_key, PropositionMemory(
            id=f"pm_{len(grouped)+1:03d}", key=obs.proposition_key
        ))
        memory.add(obs)
    return list(grouped.values())


def summarize(memories: List[PropositionMemory]) -> dict:
    return {
        "propositions": len(memories),
        "observations": sum(len(m.observations) for m in memories),
        "multi_agent_propositions": sum(len(m.agents()) >= 2 for m in memories),
        "disputed_propositions": sum(m.state == "disputed" for m in memories),
        "interpretation_variants": sum(len(m.interpretations()) > 1 for m in memories),
        "provenance_preserved": all(bool(o.agent and o.source) for m in memories for o in m.observations),
    }
