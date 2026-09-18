from src.temporal_v4 import build_v4, extract_time_anchors

def points():
    return [
      {"canonical_id":"p1","dimensions":{"union":["actor","subject"]},"evidence":["Rahul stopped playing football during the summer."]},
      {"canonical_id":"p2","dimensions":{"union":["action","state","verb"]},"evidence":["Rahul stopped playing football during the summer."]},
      {"canonical_id":"p3","dimensions":{"union":["action","state","verb"]},"evidence":["Rahul started playing again after joining a new team."]},
      {"canonical_id":"p4","dimensions":{"union":["noun","actor","target"]},"evidence":["Rahul started playing again after joining a new team."]},
    ]

def test_extracts_relative_and_seasonal_time():
    a = extract_time_anchors("Rahul stopped playing football during the summer.")
    assert any(x["text"].lower() == "summer" for x in a)

def test_builds_events_and_state_history():
    r = build_v4(points())
    assert len(r["events"]) == 2
    assert r["metrics"]["anchored_events"] == 2
    assert r["state_history"]["p1"][0]["transition"] == "ended"

def test_never_invents_absolute_dates():
    r = build_v4(points())
    blob = str(r)
    assert "2026" not in blob
    assert "date" not in blob.lower() or "absolute_dates_are_never_invented" in blob
