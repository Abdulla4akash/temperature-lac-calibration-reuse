"""Exact linear-algebra + Taylor certificates for K=2**m+1 softmax shattering.
The high-precision exponential check is secondary; the rational identities and
an explicit remainder inequality supply the mathematical certificate.
"""
import os
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']: os.environ[key]='1'
import json,time,resource,sys,platform
from pathlib import Path
from fractions import Fraction as F
import sympy as sp
import mpmath as mp
ROOT=Path(__file__).resolve().parents[1]

def sf(x): return F(int(sp.numer(x)),int(sp.denom(x)))
def smp(x): return mp.mpf(x.numerator)/x.denominator

def build(m):
    q=2**m
    nodes=[F(q+2+r,q+1) for r in range(q)]  # 1<t<2, hence 0<log(t)<1
    E=sp.Matrix([[sp.Rational(t.denominator,t.numerator)**(j+1) for j in range(q)] for t in nodes])
    signs=sp.Matrix([[1-2*((r>>i)&1) for i in range(m)] for r in range(q)])
    V=E.inv()*signs
    H=max(F(1),max(abs(sf(x)) for x in V))
    eps=F(1,6*q)/H
    W=[[sf(V[j,i])/H for j in range(q)] for i in range(m)]
    # Full rational verification, independent of the symbolic inverse output.
    for i in range(m):
        for r,t in enumerate(nodes):
            value=sum((W[i][j]*t**(-j-1) for j in range(q)),F(0))
            assert value==F(1-2*((r>>i)&1),1)/H
    assert max(abs(v) for row in W for v in row)<=1
    assert eps<=1 and F(3,2)*q*eps*H==F(1,4)
    observed=[]; margin_ratios=[]; rem_ratios=[]
    for r,t in enumerate(nodes):
        beta=mp.log(smp(t)); linear=smp(eps)*beta/smp(H)
        base=mp.fsum([mp.exp(beta*(-j-1)) for j in range(q)])
        actualmask=0
        for i in range(m):
            pert=mp.fsum([mp.exp(beta*(-j-1+smp(eps*W[i][j]))) for j in range(q)])
            d=pert-base
            s=1-2*((r>>i)&1)
            assert d*s>0
            assert abs(d-s*linear) <= linear/4
            actualmask |= (int(d<0)<<i)
            margin_ratios.append(float(abs(d)/linear))
            rem_ratios.append(float(abs(d-s*linear)/linear))
        assert actualmask==r
        observed.append(actualmask)
    return {'m':m,'K':q+1,'patterns':observed,'nodes_t':[str(t) for t in nodes], 'baseline_exponents':[-j-1 for j in range(q)],'H':str(H),'epsilon':str(eps),'normalized_perturbations':[[str(x) for x in row] for row in W], 'exact_linear_system_verified':True, 'exact_Taylor_ratio_bound':'1/4','all_target_logits_uniquely_top':True,'min_numeric_margin_to_first_order':min(margin_ratios),'max_numeric_relative_remainder':max(rem_ratios),'epsilon_approx':float(eps),'H_approx':float(H),'decimal_precision':mp.mp.dps}

def main():
    conf=json.loads((ROOT/'protocol.json').read_text())['interpolation_validation']
    mp.mp.dps=conf['precision_decimal_digits']
    sw=time.perf_counter(); sc=time.process_time()
    result=[build(m) for m in conf['m_values']]
    out={'entries':result,'CPU_seconds':time.process_time()-sc,'wall_seconds':time.perf_counter()-sw,'max_RSS_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'sympy':sp.__version__,'mpmath':mp.__version__}
    (ROOT/'results/interpolation_certificates.json').write_text(json.dumps(out,indent=2))
    print([(r['m'],r['K'],len(r['patterns']),r['epsilon_approx'],r['min_numeric_margin_to_first_order']) for r in result])
    print('CPU seconds',out['CPU_seconds'])
if __name__=='__main__':main()
