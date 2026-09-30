"""Audit exploratory float witnesses with exact rational arithmetic; never round ties."""
from fractions import Fraction as F
from pathlib import Path
import json,time,resource
ROOT=Path(__file__).resolve().parents[1]

def exact_probabilities(logits,t):
    return [1/sum((t**int(z) for z in row),F(0)) for row in logits]

def verify_entry(entry, numerators,denominator):
    rows=[]
    for w in entry['witnesses']:
        t=F(numerators[w['node_index']],denominator)
        ps=exact_probabilities(entry['logits'],t)
        target=w['mask']; inside=[ps[i] for i in range(3) if target>>i&1];outside=[ps[i] for i in range(3) if not(target>>i&1)]
        lo=max(outside) if outside else F(0)
        hi=min(inside) if inside else F(1)
        cutoff=(lo+hi)/2
        actual=sum((int(p>=cutoff)<<i) for i,p in enumerate(ps))
        rows.append({'mask_requested':target,'mask_actual':actual,'pass':actual==target and hi>lo,'t':str(t),'cutoff':str(cutoff),'probabilities':[str(p) for p in ps], 'separation':float(hi-lo)})
    return {'K':entry['K'],'logits':entry['logits'],'patterns_requested':entry['patterns_found'],'valid_requested_patterns':sum(r['pass'] for r in rows),'rows':rows}

def main():
    start=time.process_time(); data=json.loads((ROOT/'results/exploratory_search.json').read_text())
    result=[verify_entry(e,data['t_numerators'],data['t_denominator']) for e in data['results']]
    out={'entries':result,'CPU_seconds':time.process_time()-start,'max_RSS_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    (ROOT/'results/exact_integer_audit.json').write_text(json.dumps(out,indent=2))
    print([(x['K'],x['valid_requested_patterns'],[(r['mask_requested'],r['mask_actual']) for r in x['rows'] if not r['pass']]) for x in result])
if __name__=='__main__':main()
