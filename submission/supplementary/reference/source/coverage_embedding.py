"""Real softmax/quantile validation plus separately labelled exact-law diagnostics."""
import os
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']: os.environ[key]='1'
import json,time,resource,csv,sys,platform
from pathlib import Path
import numpy as np
import scipy
from scipy.integrate import quad
from scipy.special import betaincc,logsumexp
ROOT=Path(__file__).resolve().parents[1]

def quantile_index(n,c=.9):
    # Avoid roundoff in the specifically prescribed rational 9/10 target.
    if c==.9: return (9*(n+1)+9)//10
    return int(np.ceil((n+1)*c))

def roots_from_u(u,delta=.01):
    s=1+delta*u[...,0]; v=.625+delta*u[...,1]
    D=2*v-s*s
    a=(s-np.sqrt(D))/2; b=(s+np.sqrt(D))/2
    return a,b

def latent_quantiles_from_softmax(u,delta=.01):
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
    k=quantile_index(n)
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
