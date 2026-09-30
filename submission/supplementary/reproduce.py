#!/usr/bin/env python3
"""Reproduce the temperature-LAC manuscript into a NEW output directory.

The input reference directory is never modified. No network is used.
Full exploratory search is optional: it is not part of the theorem evidence.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import resource
from reproduction_compare import compare_results

ROOT=Path(__file__).resolve().parent

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--full-search',action='store_true')
    parser.add_argument('--strict',action='store_true',help='Require exact equality, including cross-platform rounding.')
    args=parser.parse_args()
    out=args.output.resolve()
    if out.exists():raise SystemExit(f'Refusing to overwrite {out}')
    if ROOT==out or ROOT in out.parents:
        raise SystemExit('Choose an output directory outside the supplementary source tree.')
    manifest=json.loads((ROOT/'reference_manifest.json').read_text())
    for name,expected in manifest.items():
        if hashlib.sha256((ROOT/'reference'/name).read_bytes()).hexdigest()!=expected:
            raise SystemExit(f'Reference hash mismatch: {name}')
    out.mkdir(parents=True)
    work=out/'work';shutil.copytree(ROOT/'reference',work)
    shutil.copy2(ROOT/'code/coverage_embedding.py',work/'source/coverage_embedding.py')
    env=os.environ.copy()
    env.update(PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',
               MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1',LAC_AUDIT_OUTPUT=str(out/'certificates'))
    commands=[]
    if args.full_search:commands.append((work,[sys.executable,'source/search_witness.py']))
    commands.extend([
        (work,[sys.executable,'source/verify_integer_witnesses.py']),
        (work,[sys.executable,'source/interpolation_certificate.py']),
        (work,[sys.executable,'source/coverage_embedding.py']),
        (work,[sys.executable,'tests/test_research.py']),
        (ROOT,[sys.executable,str(ROOT/'code/audit_checks.py')]),
        (ROOT,[sys.executable,str(ROOT/'code/chain_certificate.py')]),
        (ROOT,[sys.executable,str(ROOT/'code/boundary_tests.py')]),
        (ROOT,[sys.executable,'-m','unittest','discover','-s',str(ROOT/'tests'),'-v'])])
    logs=[]
    for index,(cwd,command) in enumerate(commands,1):
        before=resource.getrusage(resource.RUSAGE_CHILDREN);start=time.perf_counter()
        log=out/f'command_{index:02d}.txt'
        with log.open('w') as handle:
            result=subprocess.run(command,cwd=cwd,env=env,stdout=handle,stderr=subprocess.STDOUT)
        after=resource.getrusage(resource.RUSAGE_CHILDREN)
        logs.append({'command':command,'cwd':str(cwd),'returncode':result.returncode,'log':log.name,
                     'wall_seconds':time.perf_counter()-start,
                     'child_cpu_seconds':after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime})
        (out/'execution.json').write_text(json.dumps(logs,indent=2)+'\n')
        if result.returncode:raise SystemExit(f'Command failed; see {log}')
    compare=compare_results(ROOT/'reference/results',work/'results')
    compare['strict_match_required']=args.strict
    ok=compare['numerical_agreement'] and (compare['exact'] or not args.strict)
    (out/'comparison.json').write_text(json.dumps(compare,indent=2)+'\n')
    print(json.dumps({'status':compare['status'],'strict_match_required':args.strict,
                      'raw_arrays':len(compare['raw_arrays']['arrays']),
                      'research_test_methods':35,'comparison_test_methods':8,'output':str(out)},indent=2))
    if not ok:raise SystemExit('Comparison requirement failed; differences retained. Do not overwrite reference data.')
if __name__=='__main__':main()
