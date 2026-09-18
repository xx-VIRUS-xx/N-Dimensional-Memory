from src.relations_v31 import derive_relationships_v31

def p(cid, surface, dims, evidence=("S",), related=()):
    return {"canonical_id": cid, "surfaces": [surface], "dimensions": {"union": list(dims)}, "evidence": list(evidence), "related_point_ids": list(related)}

def types(rs): return {(r['source'], r['target'], r['type']) for r in rs}

def test_emotion_verb_does_not_act_on_object():
    rs = derive_relationships_v31([
        p('rahul','Rahul',['actor','subject']),
        p('love','love',['verb','emotion','feeling']),
        p('football','football',['noun','object'])])
    assert ('love','football','acts_on') not in types(rs)

def test_action_to_compound_object_is_high_confidence():
    rs = derive_relationships_v31([
        p('play','play',['verb','action']),
        p('pf','play football',['verb','action','object'])])
    # Compound point is action-like too, so relationship is preserved via identity in V2.1;
    # direct action->object requires the target's object role.
    assert ('play','pf','acts_on') in types(rs)
    assert next(r for r in rs if r['source']=='play' and r['target']=='pf' and r['type']=='acts_on')['confidence'] == 'high'

def test_temporal_context_requires_shared_evidence():
    rs = derive_relationships_v31([
        p('event','practice',['action']),
        p('time','yesterday',['time'], evidence=('OTHER',))])
    assert not any(r['type']=='temporal_context' for r in rs)

def test_transition_marker_is_local_to_event():
    rs = derive_relationships_v31([p('x','started playing again',['action','state'])])
    assert ('x','x','state_transition_began') in types(rs)
