from src.temporal_belief_v52 import Observation, BeliefTimeline

def test_temporal_evolution():
    t=BeliefTimeline("location")
    t.add(Observation("o1","location","Jaipur",valid_from="2026-01",valid_to="2026-05"))
    t.add(Observation("o2","location","Delhi",valid_from="2026-06"))
    assert t.classify()==[{"type":"temporal_evolution","from":"o1","to":"o2"}]

def test_unordered_conflict():
    t=BeliefTimeline("location")
    t.add(Observation("o1","location","Jaipur"))
    t.add(Observation("o2","location","Delhi"))
    assert t.classify()[0]["type"]=="potential_conflict"

def test_same_state():
    t=BeliefTimeline("location")
    t.add(Observation("o1","location","Jaipur",valid_from="2026-01"))
    t.add(Observation("o2","location","Jaipur",valid_from="2026-02"))
    assert t.classify()[0]["type"]=="same_state"
