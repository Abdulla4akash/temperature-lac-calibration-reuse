"""Exploratory finite witness search. Exact certificates are produced separately."""
import os
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:
    os.environ[key]='1'
import json,time,resource,platform,sys
from pathlib import Path
import numpy as np
from scipy.special import logsumexp
ROOT=Path(__file__).resolve().parents[1]
conf=json.loads((ROOT/'protocol.json').read_text())['exploratory_search']
resource.setrlimit(resource.RLIMIT_CPU,(180,185))
rng=np.random.default_rng(conf['seed'])
# beta=log(t); these rational t nodes can later be verified exactly for integer logits.
t_num=np.unique(np.rint(np.geomspace(1001,1000000,conf['grid_points'])).astype(int))
t_den=1000
beta=np.log(t_num/t_den)
startw=time.perf_counter(); startc=time.process_time()
results=[]
for K in conf['classes']:
    best=0; saved=None
    for trial in range(conf['max_trials_each']):
        gaps=rng.integers(conf['logit_integer_min'],conf['logit_integer_max']+1,size=(3,K-1))
        # Include the target logit 0. Scores inverse probabilities have the same ascending ordering.
        logits=np.concatenate([np.zeros((3,1),dtype=int),gaps],axis=1)
        values=logsumexp(beta[:,None,None]*logits[None,:,:],axis=2)
        order=np.argsort(values,axis=1,kind='stable')
        masks=np.cumsum(1<<order,axis=1)
        uniq=np.unique(masks)
        count=len(uniq)+1
        if count>best:
            best=count
            witnesses=[]
            for mask in [0]+uniq.tolist():
                if mask==0:
                    witnesses.append({'mask':0,'node_index':0,'prefix':0})
                else:
                    ids=np.argwhere(masks==mask)
                    # Choose largest log-denominator gap among possibilities.
                    bestgap=-1; chosen=None
                    for r,p in ids:
                        if p==2: gap=1.
                        else: gap=values[r,order[r,p+1]]-values[r,order[r,p]]
                        if gap>bestgap:
                            bestgap=gap;chosen=(int(r),int(p+1))
                    witnesses.append({'mask':int(mask),'node_index':chosen[0],'prefix':chosen[1]})
            saved={'K':K,'trial_found':trial,'patterns_found':count,'logits':logits.tolist(),'witnesses':witnesses}
        if best==8: break
    saved['trials_run']=trial+1
    results.append(saved)
    print(K,trial+1,best,flush=True)
output={'results':results,'t_numerators':t_num.tolist(),'t_denominator':t_den,'CPU_seconds':time.process_time()-startc,'wall_seconds':time.perf_counter()-startw,'max_RSS_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'python':sys.version,'platform':platform.platform(),'seed':conf['seed']}
(ROOT/'results/exploratory_search.json').write_text(json.dumps(output,indent=2))
print('CPU',output['CPU_seconds'])
