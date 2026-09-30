#!/usr/bin/env python3
"""Independent finite checks for temperature-scaled LAC theory.

No fitting, inference service, or GPU. Exact certificates use Python Fraction.
The finite checks corroborate implementations; they do not prove theorems.
"""
from __future__ import annotations
import csv
import json
import math
import os
import platform
import sys
import time
import unittest
from fractions import Fraction
from pathlib import Path
from typing import Dict

import numpy as np
import scipy
from scipy.integrate import quad
from scipy.stats import beta

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(os.environ.get("LAC_AUDIT_OUTPUT", str(ROOT / "results")))
Poly = Dict[int, Fraction]


def rank_index(n: int, coverage: Fraction | str | float) -> int:
    if not isinstance(n, int) or n < 1:
        raise ValueError("n must be a positive integer")
    c = coverage if isinstance(coverage, Fraction) else Fraction(str(coverage))
    if not 0 < c < 1:
        raise ValueError("coverage must lie strictly between zero and one")
    v = (n + 1) * c
    return (v.numerator + v.denominator - 1) // v.denominator


def validate(n: int, k: int, models: int) -> None:
    if not all(isinstance(v, int) for v in (n, k, models)):
        raise TypeError("n, k, models must be integers")
    if n < 1 or models < 1 or not 1 <= k <= n + 1:
        raise ValueError("require n>=1, models>=1, 1<=k<=n+1")


def multiply(a: Poly, b: Poly) -> Poly:
    result: Poly = {}
    for i, x in a.items():
        for j, y in b.items():
            result[i + j] = result.get(i + j, Fraction(0)) + x * y
    return {i: x for i, x in result.items() if x}


def survival_polynomial(n: int, k: int) -> Poly:
    """Survival of Beta(k,n+1-k); full-set boundary handled by callers."""
    validate(n, k, 1)
    if k == n + 1:
        raise ValueError("k=n+1 is a full-set boundary, not a Beta distribution")
    b = n + 1 - k
    coefficient = Fraction(math.factorial(n), math.factorial(k-1)*math.factorial(b-1))
    result: Poly = {0: Fraction(1)}
    for j in range(b):
        result[k+j] = -coefficient * ((-1)**j) * math.comb(b-1, j) / (k+j)
    return {i: x for i, x in result.items() if x}


def exact_mean(n: int, k: int, models: int) -> Fraction:
    validate(n, k, models)
    if k == n + 1:
        return Fraction(1)
    if n * models > 5000:
        raise ValueError("exact polynomial operation intentionally bounded to degree 5000")
    base = survival_polynomial(n, k)
    result: Poly = {0: Fraction(1)}
    power = models
    while power:
        if power & 1:
            result = multiply(result, base)
        power >>= 1
        if power:
            base = multiply(base, base)
    return sum((coef / (degree+1) for degree, coef in result.items()), Fraction(0))


def numerical_mean(n: int, k: int, models: int) -> tuple[float, float]:
    validate(n, k, models)
    if k == n + 1:
        return 1.0, 0.0
    dist = beta(k, n+1-k)
    # Supply knots around the minimum's transition, not only around the Beta mean.
    qs = np.array([1e-6, 1e-3, .01, .1, .5, .9, .99, .999999]) / models
    points = sorted(set(float(x) for x in dist.ppf(qs) if np.isfinite(x) and 0 < x < 1))
    def integrand(x: float) -> float:
        return float(np.exp(models * dist.logsf(x)))
    value, error = quad(integrand, 0., 1., points=points, epsabs=2e-11,
                        epsrel=2e-11, limit=300)
    return value, error


def lower_constant(eta: float) -> float:
    if not 0 < eta <= .5:
        raise ValueError("0 < eta <= 1/2 required")
    A = math.exp(-1/6) * math.sqrt(eta*(1-eta)/(2*math.pi))
    B = 4/eta
    r = A*math.exp(-B)
    q = A*math.exp(-2*B)
    s = -math.expm1(-q/math.sqrt(2))
    return eta*r*s/4


def rational_denominator(base: Fraction, gaps: tuple[int, ...]) -> Fraction:
    return Fraction(1) + sum((base**g for g in gaps), Fraction(0))


class AuditChecks(unittest.TestCase):
    def test_rank_primary(self):
        self.assertEqual(rank_index(99, '.9'), 90)
        self.assertEqual(rank_index(49, Fraction(9,10)), 45)
    def test_boundary_rank(self):
        self.assertEqual(rank_index(1, '.9'), 2)
        self.assertEqual(rank_index(8, '.9'), 9)
        self.assertEqual(rank_index(9, '.9'), 9)
    def test_full_set(self):
        for n in (1, 8, 99):
            for m in (1, 2, 500):
                self.assertEqual(exact_mean(n, n+1, m), Fraction(1))
                self.assertEqual(numerical_mean(n, n+1, m), (1.,0.))
    def test_invalid_inputs(self):
        for n,c in ((0,.9),(1,0),(1,1)):
            with self.assertRaises(ValueError): rank_index(n,c)
        with self.assertRaises(ValueError): exact_mean(3,5,2)
        with self.assertRaises(ValueError): survival_polynomial(3,4)
    def test_uniform_minimum(self):
        for m in (1,2,3,9):
            self.assertEqual(exact_mean(1,1,m), Fraction(1,m+1))
    def test_single_coordinate(self):
        for n in range(1,9):
            for k in range(1,n+1):
                self.assertEqual(exact_mean(n,k,1), Fraction(k,n+1))
    def test_rational_vs_quadrature(self):
        for n,k,m in ((3,2,3),(6,5,4),(8,3,2),(99,90,2)):
            exact = exact_mean(n,k,m)
            numeric, error = numerical_mean(n,k,m)
            self.assertLess(abs(float(exact)-numeric), max(1e-12, 4*error))
    def test_k3_witness(self):
        gaps_a, gaps_b = (-1,-10), (-4,-4)
        low = rational_denominator(Fraction(11,10),gaps_a)-rational_denominator(Fraction(11,10),gaps_b)
        high = rational_denominator(Fraction(2),gaps_a)-rational_denominator(Fraction(2),gaps_b)
        self.assertLess(low,0)
        self.assertGreater(high,0)
    def test_primary_algebra(self):
        # Symbolic identities in the explicit two-coordinate construction,
        # checked on a rational grid before any transcendental softmax calls.
        for u in (Fraction(0), Fraction(1,3), Fraction(1)):
            for v in (Fraction(0), Fraction(2,3), Fraction(1)):
                s=1+u/100; q=Fraction(5,8)+v/100
                disc=2*q-s*s
                self.assertGreater(disc,0)
                self.assertGreater(s*s-disc,0)
                self.assertLess(s+Fraction(3,5),2)  # sqrt(disc)<3/5 below
                self.assertLess(disc,Fraction(9,25))
    def test_lower_constant_positive(self):
        for e in (.05,.1,.2,.4,.5):
            self.assertGreater(lower_constant(e),0)
            self.assertLess(lower_constant(e),e/4)
    def test_density_envelope_grid(self):
        checked=0
        for eta in (.05,.1,.2,.4):
            N=max(100,math.ceil(16/eta**2))
            for ptarget in (eta,.5,1-eta):
                k=math.ceil(N*ptarget)
                p=k/N
                if not eta <= p <= 1-eta: continue
                A=math.exp(-1/6)*math.sqrt(eta*(1-eta)/(2*math.pi))
                B=4/eta
                for x in np.linspace(eta/2,1-eta/2,101):
                    lhs=float(beta.logpdf(x,k,N-k))
                    rhs=math.log(A)+.5*math.log(N)-B*N*(x-p)**2
                    self.assertGreaterEqual(lhs+1e-8,rhs)
                    checked+=1
        self.assertGreater(checked,500)
    def test_difference_identity_exact(self):
        # Deterministic finite enumeration corroborates the cancellation-free identity.
        import itertools
        values=(Fraction(1,5),Fraction(2,5),Fraction(4,5))
        rows=list(itertools.product(values,repeat=3))
        left=sum((r[0]-min(r) for r in rows),Fraction(0))/len(rows)
        right=sum((max(Fraction(0),r[0]-min(r[1:])) for r in rows),Fraction(0))/len(rows)
        self.assertEqual(left,right)


def run() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    started=time.perf_counter(); cpu=time.process_time()
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(AuditChecks)
    with (OUT/'independent_tests.txt').open('w') as handle:
        result=unittest.TextTestRunner(stream=handle,verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise RuntimeError('Independent audit tests failed; see output file')
    exact=exact_mean(99,90,2)
    numeric,error=numerical_mean(99,90,2)
    witness=[]
    for base in (Fraction(11,10),Fraction(2)):
        vals=[rational_denominator(base,gaps) for gaps in ((-1,-10),(-4,-4))]
        witness.append({'exp_beta':str(base),'denominators':[str(v) for v in vals],
                        'difference':str(vals[0]-vals[1])})
    certificate={'n':99,'k':90,'M':2,'coverage_fraction':str(exact),
                 'coverage_decimal':float(exact),'quadrature':numeric,'quad_error_estimate':error,
                 'absolute_discrepancy':abs(float(exact)-numeric),'K3_exact_witness':witness,
                 'type':'Exact rational polynomial integration; decimal is a rounded display'}
    (OUT/'exact_certificates.json').write_text(json.dumps(certificate,indent=2)+'\n')
    rows=[]
    for n in (19,99,499,1999):
        for c in ('.5','.9'):
            k=rank_index(n,c); p=k/(n+1)
            for m in (2,4,16,64,256,4096):
                mu,err=numerical_mean(n,k,m)
                rate=min(1.,math.sqrt(math.log(m)/(n+1)))
                rows.append(dict(n=n,k=k,c=c,M=m,mean_min=mu,quad_error_estimate=err,
                                 rank_coverage=p,loss=p-mu,rate=rate,loss_over_rate=(p-mu)/rate))
    with (OUT/'uniform_law_grid.csv').open('w',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    cpu_model=next((l.split(':',1)[1].strip() for l in Path('/proc/cpuinfo').read_text().splitlines()
                    if l.startswith('model name')),'unknown') if Path('/proc/cpuinfo').exists() else 'unknown'
    info={'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,
          'platform':platform.platform(),'cpu_model':cpu_model,
          'logical_cpus_visible':os.cpu_count(),'main_numerical_grid_cells':len(rows),
          'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
          'cpu_seconds_internal':time.process_time()-cpu,'wall_seconds_internal':time.perf_counter()-started,
          'new_random_seeds':[],'analysis_kind':'deterministic exact checks and numerical integration',
          'thread_environment':{k:os.environ.get(k) for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS')}}
    (OUT/'independent_environment.json').write_text(json.dumps(info,indent=2)+'\n')
    print(json.dumps({'status':'PASS','tests':result.testsRun,'new_diagnostic_cells':len(rows),
                      'primary_exact_coverage':float(exact)},indent=2))

if __name__=='__main__': run()
