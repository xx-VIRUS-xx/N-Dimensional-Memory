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

class SharedMemoryV62:
    """Deterministic, append-only shared memory with conflict/evolution derivation."""
    def __init__(self): self._obs: Dict[str, Observation] = {}
    def append(self, o: Observation):
        if o.observation_id in self._obs: raise ValueError(f"duplicate observation_id: {o.observation_id}")
        self._obs[o.observation_id] = o
    def snapshot(self): return {"observations":[asdict(o) for o in self._obs.values()]}
    @classmethod
    def from_snapshot(cls, s):
        m=cls()
        for x in s.get("observations",[]): m.append(Observation(**x))
        return m
    def observations_for(self, pid): return [deepcopy(o) for o in self._obs.values() if o.proposition_id==pid]
    def state(self,pid):
        obs=self.observations_for(pid)
        if not obs: return {"proposition_id":pid,"status":"unknown","observations":[],"agents":[],"relations":[]}
        relations=[]
        for i,a in enumerate(obs):
            for b in obs[i+1:]:
                if a.value==b.value: continue
                if _overlap(a,b): relations.append({"type":"potential_conflict","from":a.observation_id,"to":b.observation_id})
                elif _ordered(a,b): relations.append({"type":"temporal_evolution","from":a.observation_id,"to":b.observation_id})
                elif _ordered(b,a): relations.append({"type":"temporal_evolution","from":b.observation_id,"to":a.observation_id})
        status="disputed" if any(r["type"]=="potential_conflict" for r in relations) else "consistent"
        latest=max(obs,key=lambda o:(o.observed_at,o.observation_id))
        return {"proposition_id":pid,"status":status,"current_value":latest.value,"current_observation_id":latest.observation_id,"observations":[asdict(o) for o in obs],"agents":sorted({o.agent_id for o in obs}),"relations":relations}

def _overlap(a,b):
    a0=a.valid_from or ""; b0=b.valid_from or ""; a1=a.valid_to or "9999-12-31T23:59:59"; b1=b.valid_to or "9999-12-31T23:59:59"
    return a0<=b1 and b0<=a1

def _ordered(a,b):
    return bool(a.valid_to and b.valid_from and a.valid_to < b.valid_from)
