#!/usr/bin/env python3
"""New exact Taylor certificates for symmetric-chain softmax witnesses.

The rational linear identities and rational remainder inequality certify order.
High-precision exponential evaluation is a secondary, non-proof check.
"""
from __future__ import annotations
import json, math, os, time
from fractions import Fraction as F
from pathlib import Path
import mpmath as mp
import sympy as sp
ROOT=Path(__file__).resolve().parents[1]
OUT=Path(os.environ.get('LAC_AUDIT_OUTPUT',str(ROOT/'results')))


def chains(m: int) -> list[list[int]]:
    if m<0: raise ValueError('m must be nonnegative')
    if m==0: return [[0]]
    bit=1<<(m-1)
    ans=[]
    for chain in chains(m-1):
        ans.append(chain+[chain[-1]|bit])
        if len(chain)>1: ans.append([a|bit for a in chain[:-1]])
    return ans


def permutation(chain: list[int],m:int) -> list[int]:
    ans=[i for i in range(m) if chain[0]>>i&1]
    for a,b in zip(chain,chain[1:]):
        added=b^a
        assert added and (added&(added-1))==0
        ans.append(added.bit_length()-1)
    ans += [i for i in range(m) if not chain[-1]>>i&1]
    assert sorted(ans)==list(range(m))
    return ans


def rational(x): return F(int(sp.numer(x)),int(sp.denom(x)))
def decimal(x:F): return mp.mpf(x.numerator)/x.denominator


def certificate(m: int) -> dict:
    decomp=chains(m);q=len(decomp)
    assert q==math.comb(m,m//2)
    flatten=[a for c in decomp for a in c]
    assert sorted(flatten)==list(range(2**m))
    for c in decomp:
        assert c[0].bit_count()+c[-1].bit_count()==m
        assert all(a&b==a and b.bit_count()==a.bit_count()+1 for a,b in zip(c,c[1:]))
    perms=[permutation(c,m) for c in decomp]
    nodes=[F(q+2+r,q+1) for r in range(q)]
    E=sp.Matrix([[sp.Rational(t.denominator,t.numerator)**(j+1) for j in range(q)] for t in nodes])
    targets=sp.Matrix([[perm.index(i) for i in range(m)] for perm in perms])
    V=E.inv()*targets
    H=max(F(1),max(abs(rational(v)) for v in V))
    eps=F(1,12*q)/H
    W=[[rational(V[j,i])/H for j in range(q)] for i in range(m)]
    assert max(abs(v) for row in W for v in row)<=1
    for i in range(m):
        for r,t in enumerate(nodes):
            assert sum((W[i][j]*t**(-j-1) for j in range(q)),F(0))==F(perms[r].index(i))/H
    # |R_i|/(beta*eps/H) <= (3/2)*q*eps*H = 1/8.
    ratio=F(3,2)*q*eps*H
    assert ratio==F(1,8)
    masks=set(); measured_ratios=[]; max_remainder=0.
    for r,t in enumerate(nodes):
        b=mp.log(decimal(t)); step=b*decimal(eps)/decimal(H)
        base=1+mp.fsum(mp.exp(-b*(j+1)) for j in range(q))
        A=[]
        for i in range(m):
            ai=1+mp.fsum(mp.exp(b*(-j-1+decimal(eps*W[i][j]))) for j in range(q))
            A.append(ai)
            rem=abs(ai-base-step*perms[r].index(i))/step
            assert rem<=mp.mpf(1)/8
            max_remainder=max(max_remainder,float(rem))
        observed=sorted(range(m),key=lambda i:A[i])
        assert observed==perms[r]
        for left,right in zip(observed,observed[1:]):
            measured_ratios.append(float((A[right]-A[left])/step))
        current=0;masks.add(current)
        for i in observed:
            current|=1<<i;masks.add(current)
    assert masks==set(range(2**m))
    return dict(m=m,K=q+1,temperature_count=q,permutations=perms,
                exp_beta_nodes=[str(t) for t in nodes],H=str(H),epsilon=str(eps),
                logits=[["0"]+[str(F(-j-1)+eps*W[i][j]) for j in range(q)] for i in range(m)],
                normalized_perturbations=[[str(w) for w in row] for row in W],
                exact_remainder_to_adjacent_step_bound=str(ratio),
                certified_patterns=sorted(masks),certificate_type='Rational interpolation and rigorous exponential Taylor inequality',
                secondary_numeric_precision=mp.mp.dps,secondary_min_adjacent_step_ratio=min(measured_ratios),
                secondary_max_relative_remainder=max_remainder)


def main():
    OUT.mkdir(parents=True,exist_ok=True); mp.mp.dps=160
    start=time.process_time()
    # Exhaustively check only a bounded finite range; induction in manuscript is the proof.
    for m in range(10):
        c=chains(m)
        assert sorted(a for row in c for a in row)==list(range(2**m))
        assert len(c)==math.comb(m,m//2)
    result=[certificate(m) for m in (3,4)]
    info={'entries':result,'cpu_seconds_internal':time.process_time()-start,
          'finite_chain_checks_m':list(range(10)),'status':'PASS'}
    (OUT/'chain_certificates.json').write_text(json.dumps(info,indent=2)+'\n')
    print([(r['m'],r['K'],len(r['certified_patterns'])) for r in result])
if __name__=='__main__':main()
