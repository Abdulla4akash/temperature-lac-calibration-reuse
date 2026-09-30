"""Real softmax/quantile validation plus separately labelled exact-law diagnostics."""
import os
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']: os.environ[key]='1'
import json,time,resource,csv,sys,platform
from fractions import Fraction
from numbers import Integral
from pathlib import Path
import numpy as np
import scipy
from scipy.integrate import quad
from scipy.special import betaincc,logsumexp
ROOT=Path(__file__).resolve().parents[1]

def quantile_index(n, c=.9):
    """Exact decimal-rational conformal rank, including n+1 (the full set)."""
    if isinstance(n, bool) or not isinstance(n, Integral) or n < 1:
        raise ValueError("n must be a positive integer")
    try:
        value = c if isinstance(c, Fraction) else Fraction(str(c))
    except (ValueError, TypeError, ZeroDivisionError) as error:
        raise ValueError("coverage must be a finite number in (0,1)") from error
    if not 0 < value < 1:
        raise ValueError("coverage must lie strictly between zero and one")
    rank = (int(n) + 1) * value
    return (rank.numerator + rank.denominator - 1) // rank.denominator

def roots_from_u(u,delta=.01):
    s=1+delta*u[...,0]; v=.625+delta*u[...,1]
    D=2*v-s*s
    a=(s-np.sqrt(D))/2; b=(s+np.sqrt(D))/2
    return a,b

def latent_quantiles_from_softmax(u,delta=.01):
    """Return integrated coordinate cutoffs for a batch of fixed-model samples.

    The numerical model is restricted to 0<delta<=.01 and [batch,n,2]
    observations in the unit square. At rank n+1, q=+infinity means the
    full set; return coordinate coverage one without constructing Beta(k,0).
    """
    u=np.asarray(u)
    if u.ndim != 3 or u.shape[0] < 1 or u.shape[1] < 1 or u.shape[2] != 2:
        raise ValueError("u must have shape [positive batch, positive n, 2]")
    if not np.all(np.isfinite(u)) or np.any((u<0)|(u>1)):
        raise ValueError("coordinates must be finite and lie in [0,1]")
    if not np.isfinite(delta) or not 0 < delta <= .01:
        raise ValueError("the certified numerical model requires 0<delta<=.01")
    if quantile_index(u.shape[1]) == u.shape[1]+1:
        full=np.ones((u.shape[0],2),dtype=float)
        return full,full.copy(),0.0
    a,b=roots_from_u(u,delta)
    assert np.all((a>0)&(a<b)&(b<1))
    z=np.stack([np.zeros_like(a),np.log(a),np.log(b)],axis=-1)
    probabilities=np.exp(-logsumexp(z[...,None,:]*np.array([1.,2.])[None,None,:,None],axis=-1))
    scores=1-probabilities
    k=quantile_index(u.shape[1]); cutoff=np.partition(scores,k-1,axis=1)[:,k-1,:]
    recovered=(1/(1-cutoff)-np.array([2.,1.625]))/delta
    direct=np.partition(u,k-1,axis=1)[:,k-1,:]
    return recovered,direct,float(np.max(np.abs(recovered-direct)))

def exact_min_beta_mean(n,M):
    # Historical function name: this returns numerical quadrature, NOT an
    # exact arithmetic certificate. code/audit_checks.py:exact_mean is exact.
    if isinstance(M,bool) or not isinstance(M,Integral) or M<1:
        raise ValueError("M must be a positive integer")
    k=quantile_index(n)
    if k==n+1:
        return 1.0,0.0
    f=lambda t: float(betaincc(k,n+1-k,t))**M
    val,err=quad(f,0,1,epsabs=2e-12,epsrel=2e-12,limit=250)
    return val,err

def summarize(name,x,expected):
    se=float(np.std(x,ddof=1)/np.sqrt(len(x)));mean=float(np.mean(x))
    return {'name':name,'replications':len(x),'mean_coverage':mean,'exact_expectation':expected,'MC_SE':se,'CI95_low':mean-1.96*se,'CI95_high':mean+1.96*se,'z_from_exact':(mean-expected)/se if se else 0.}

def main():
    conf=json.loads((ROOT/'coverage_extension_protocol.json').read_text());main=conf['main'];diag=conf['diagnostics']
    sc=time.process_time(); sw=time.perf_counter();rng=np.random.default_rng(main['seed'])
    R=main['replications'];n=main['n'];delta=main['delta']
    outputs={name:[] for name in ['reuse','fixed','independent','same_total_split','NLL_grid_control']}; errors=[]
    # Batching bounds memory even when reproducing on small laptops.
    for start in range(0,R,250):
        batch=min(250,R-start)
        u=rng.random((batch,n,2));r,d,e=latent_quantiles_from_softmax(u,delta);errors.append(e)
        chosen=np.argmin(r,axis=1); idx=np.arange(batch)
        outputs['reuse'].append(d[idx,chosen]);outputs['fixed'].append(d[:,0]);outputs['NLL_grid_control'].append(d[:,1])
        ind=rng.random((batch,n,2));ri,di,ei=latent_quantiles_from_softmax(ind,delta);errors.append(ei)
        outputs['independent'].append(di[idx,chosen])
        # Same total n=99: 50 tune, 49 calibrate.
        tune=u[:,:50,:];cal=u[:,50:,:]
        rt,dt,et=latent_quantiles_from_softmax(tune,delta);rc,dc,ec=latent_quantiles_from_softmax(cal,delta);errors.extend([et,ec])
        outputs['same_total_split'].append(dc[idx,np.argmin(rt,axis=1)])
    outputs={k:np.concatenate(v) for k,v in outputs.items()}
    expected_reuse,quaderr=exact_min_beta_mean(n,2)
    rows=[summarize(k,v,expected_reuse if k=='reuse' else .9) for k,v in outputs.items()]
    paired=outputs['independent']-outputs['reuse']
    pairsummary=summarize('paired_independent_minus_reuse',paired,.9-expected_reuse)
    rdiag=np.random.default_rng(diag['seed']);dr=[];raw_diag={}
    for nn in diag['n_values']:
        k=quantile_index(nn)
        for M in diag['M_values']:
            draws=rdiag.beta(k,nn+1-k,size=(diag['replications'],M)).min(axis=1)
            expectation,qe=exact_min_beta_mean(nn,M)
            row=summarize(f'beta_law_n{nn}_M{M}',draws,expectation);row.update(n=nn,M=M,quadrature_error_estimate=qe)
            dr.append(row);raw_diag[f'n{nn}_M{M}']=draws
    # Boundary discriminant: for delta=1/100, 2299/10000 <= D <= 27/100.
    maxerr=max(errors)
    gates={'softmax_identity_maxerror_below_1e-10':maxerr<1e-10,'main_and_controls_within_5_MC_SE':all(abs(r['z_from_exact'])<=5 for r in rows),'diagnostic_rows_within_5_MC_SE':all(abs(r['z_from_exact'])<=5 for r in dr)}
    report={'main':rows,'paired':pairsummary,'identity_max_abs_error':maxerr,'main_quadrature_error_estimate':quaderr,'gates':gates,'diagnostics':dr,'CPU_seconds':time.process_time()-sc,'wall_seconds':time.perf_counter()-sw,'max_RSS_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'versions':{'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__},'platform':platform.platform()}
    np.savez_compressed(ROOT/'results/coverage_raw.npz',**outputs,**raw_diag)
    (ROOT/'results/coverage_results.json').write_text(json.dumps(report,indent=2))
    for filename,records in [('coverage_main.csv',rows+[pairsummary]),('coverage_law_diagnostics.csv',dr)]:
        with (ROOT/'results'/filename).open('w',newline='') as f:
            wr=csv.DictWriter(f,fieldnames=list(records[0]));wr.writeheader();wr.writerows(records)
    print(json.dumps({k:report[k] for k in ['main','paired','identity_max_abs_error','gates','CPU_seconds','max_RSS_KiB']},indent=2))
if __name__=='__main__':main()
