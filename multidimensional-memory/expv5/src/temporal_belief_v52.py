from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Observation:
    id: str
    proposition: str
    value: str
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None
    status: str = "asserted"
    source: str = ""

@dataclass
class BeliefTimeline:
    proposition: str
    observations: List[Observation] = field(default_factory=list)

    def add(self, obs: Observation):
        self.observations.append(obs)
        self.observations.sort(key=lambda x: (x.valid_from is None, x.valid_from or ""))

    def classify(self):
        events=[]
        for i,a in enumerate(self.observations):
            for b in self.observations[i+1:]:
                if a.value == b.value:
                    events.append({"type":"same_state","from":a.id,"to":b.id})
                    continue
                ordered = a.valid_from is not None and b.valid_from is not None and a.valid_from < b.valid_from
                overlap = False
                if a.valid_to and b.valid_from:
                    overlap = a.valid_to >= b.valid_from
                if ordered and not overlap:
                    events.append({"type":"temporal_evolution","from":a.id,"to":b.id})
                else:
                    events.append({"type":"potential_conflict","from":a.id,"to":b.id})
        return events
