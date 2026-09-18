import json
from temporal_belief_v52 import Observation, BeliefTimeline

t=BeliefTimeline("Rahul.location")
t.add(Observation("o1","Rahul.location","Jaipur",valid_from="2025-01",valid_to="2026-05",status="asserted",source="I live in Jaipur."))
t.add(Observation("o2","Rahul.location","Delhi",valid_from="2026-06",status="confirmed",source="Actually, I moved to Delhi last month."))
result={"experiment":"EXP-V5.2","proposition":t.proposition,"observations":[o.__dict__ for o in t.observations],"relations":t.classify()}
print(json.dumps(result,indent=2))
with open("results/v5.2.temporal_belief.json","w") as f: json.dump(result,f,indent=2)
