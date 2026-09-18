import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from memory_v62 import Observation, SharedMemoryV62

def o(i,a,v,t,vf=None,vt=None): return Observation(i,'p',a,v,'asserted',t,vf,vt,'e')

def test_append_only_and_provenance():
 m=SharedMemoryV62(); m.append(o('a','A','Jaipur','2026-01')); m.append(o('b','B','Delhi','2026-02'))
 s=m.state('p'); assert len(s['observations'])==2 and s['agents']==['A','B']

def test_order_independent_conflict():
 x=[o('a','A','Jaipur','2026-01'),o('b','B','Delhi','2026-02')]
 out=[]
 for seq in (x,x[::-1]):
  m=SharedMemoryV62(); [m.append(z) for z in seq]; s=m.state('p'); out.append((s['status'],sorted(v['value'] for v in s['observations'])))
 assert out[0]==out[1]==('disputed',['Delhi','Jaipur'])

def test_temporal_evolution_not_conflict():
 m=SharedMemoryV62(); m.append(o('a','A','Jaipur','2026-01','2025-01','2026-05')); m.append(o('b','B','Delhi','2026-06','2026-06',None)); s=m.state('p')
 assert s['status']=='consistent' and s['relations']==[{'type':'temporal_evolution','from':'a','to':'b'}]

def test_snapshot_reconstructs_same_state():
 m=SharedMemoryV62(); m.append(o('a','A','Jaipur','2026-01')); m.append(o('b','B','Delhi','2026-02')); r=SharedMemoryV62.from_snapshot(m.snapshot()); assert r.state('p')==m.state('p')
