import json
from pathlib import Path
from .relations_v31 import derive_relationships_v31, metrics
ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'data' / 'conversation_01.v21.json'
OUT_JSON = ROOT / 'results' / 'conversation_01.v31.json'
OUT_MD = ROOT / 'results' / 'conversation_01.v31.report.md'

def main():
    substrate=json.loads(INPUT.read_text())
    points=substrate['points']; relations=derive_relationships_v31(points); m=metrics(points, relations)
    result={'experiment':'EXP-V3.1','conversation_id':substrate['conversation_id'],
      'hypothesis':'Relationship candidates become more useful when deterministic rules are constrained by semantic roles, lexical structure, shared evidence, and local transition markers.',
      'policy':{'relationships_are_candidates':True,'no_fact_inference':True,'no_llm':True,'no_embeddings':True,'no_vector_db':True,'no_graph_db':True},'points':points,'relations':relations,'metrics':m}
    OUT_JSON.write_text(json.dumps(result,indent=2)+'\n')
    lines=['# EXP-V3.1: Evidence-Constrained Relationships','','## Hypothesis','',result['hypothesis'],'','## Metrics','']
    lines += [f'- **{k}:** `{v}`' for k,v in m.items()]
    lines += ['', '## Candidate relations','']
    for r in relations:
        ev='; '.join(r['evidence']) if r['evidence'] else 'identity substrate'
        lines.append(f"- `{r['source']} -> {r['target']}` **{r['type']}** ({r['confidence']}) — {r['rule']} — evidence: {ev}")
    lines += ['', '## Key constraint changes','', '- Emotion/feeling/intent-only verbs are not treated as generic object-taking actions.', '- Actor-to-context edges require shared evidence.', '- Transition markers must occur in the event point itself.', '- Lexical containment can raise action-to-object confidence, but does not merge points.']
    OUT_MD.write_text('\n'.join(lines)+'\n')
    print(json.dumps(m,indent=2))
if __name__=='__main__': main()
