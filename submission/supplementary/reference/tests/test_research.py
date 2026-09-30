import unittest,sys,json,hashlib,math
from pathlib import Path
from fractions import Fraction as F
import numpy as np
import sympy as sp
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'source'))
from verify_integer_witnesses import exact_probabilities
from coverage_embedding import roots_from_u,latent_quantiles_from_softmax,quantile_index,exact_min_beta_mean

class ResearchTests(unittest.TestCase):
    def test_original_protocol_hash(self):
        expected=(ROOT/'PROTOCOL_SHA256.txt').read_text().split()[0]
        self.assertEqual(hashlib.sha256((ROOT/'protocol.json').read_bytes()).hexdigest(),expected)
    def test_extension_protocol_hash(self):
        expected=(ROOT/'COVERAGE_PROTOCOL_SHA256.txt').read_text().split()[0]
        self.assertEqual(hashlib.sha256((ROOT/'coverage_extension_protocol.json').read_bytes()).hexdigest(),expected)
    def test_false_float_witness_preserved(self):
        rows=json.loads((ROOT/'results/exact_integer_audit.json').read_text())['entries']
        k4=next(x for x in rows if x['K']==4)
        self.assertEqual(k4['valid_requested_patterns'],7)
        failure=next(r for r in k4['rows'] if not r['pass'])
        self.assertEqual((failure['mask_requested'],failure['mask_actual']),(5,6))
    def test_integer_certificates_independent_recompute(self):
        for entry in json.loads((ROOT/'results/exact_integer_audit.json').read_text())['entries']:
            for row in entry['rows']:
                ps=exact_probabilities(entry['logits'],F(row['t']));q=F(row['cutoff'])
                actual=sum(int(p>=q)<<i for i,p in enumerate(ps))
                self.assertEqual(actual,row['mask_actual'])
    def test_interpolation_rational_identities(self):
        for entry in json.loads((ROOT/'results/interpolation_certificates.json').read_text())['entries']:
            H=F(entry['H']);q=entry['K']-1;eps=F(entry['epsilon'])
            self.assertEqual(F(3,2)*q*eps*H,F(1,4))
            for i,row in enumerate(entry['normalized_perturbations']):
                ws=list(map(F,row));self.assertLessEqual(max(map(abs,ws)),1)
                for r,t in enumerate(map(F,entry['nodes_t'])):
                    val=sum((ws[j]*t**(-j-1) for j in range(q)),F(0))
                    self.assertEqual(val,F(1-2*((r>>i)&1))/H)
    def test_power_sum_jacobian_exact(self):
        for q in range(1,9):
            w=[sp.Rational(j+1,q+1) for j in range(q)]
            J=sp.Matrix([[(r+1)*w[j]**r for j in range(q)] for r in range(q)])
            expected=sp.factorial(q)
            for i in range(q):
                for j in range(i+1,q): expected*=w[j]-w[i]
            self.assertEqual(J.det(),expected)
            self.assertGreater(expected,0)
    def test_explicit_embedding_exact_corner_bounds(self):
        delta=F(1,100)
        lo=2*F(5,8)-(1+delta)**2;hi=2*(F(5,8)+delta)-1
        self.assertEqual(lo,F(2299,10000));self.assertEqual(hi,F(27,100))
        self.assertGreater(lo,0);self.assertLess(hi,F(1))
        # sqrt(D)<.52, s in[1,1.01] imply roots within(.24,.765).
        self.assertLess(hi,F(52,100)**2)
    def test_explicit_embedding_numerical_corners(self):
        u=np.array([[a,b] for a in [0.,1.] for b in [0.,1.]])
        a,b=roots_from_u(u)
        self.assertTrue(np.all((a>0)&(a<b)&(b<1)))
        np.testing.assert_allclose(a+b,1+.01*u[:,0],rtol=0,atol=1e-15)
        np.testing.assert_allclose(a*a+b*b,.625+.01*u[:,1],rtol=0,atol=1e-15)
    def test_quantile_off_by_one(self):
        for n,k in [(99,90),(49,45),(50,46),(499,450),(1999,1800)]: self.assertEqual(quantile_index(n),k)
    def test_actual_softmax_identity(self):
        u=np.random.default_rng(4).random((30,99,2))
        r,d,err=latent_quantiles_from_softmax(u)
        self.assertLess(err,1e-10)
    def test_grid_NLL_selector_is_beta_two(self):
        u=np.random.default_rng(5).random((10,99,2));a,b=roots_from_u(u)
        loss1=np.log1p(a+b).mean(axis=1);loss2=np.log1p(a*a+b*b).mean(axis=1)
        self.assertTrue(np.all(loss2<loss1))
    def test_beta_single_model_mean(self):
        for n in [99,499,1999]:
            mean,_=exact_min_beta_mean(n,1);self.assertAlmostEqual(mean,.9,places=11)
    def test_raw_main_summary(self):
        data=np.load(ROOT/'results/coverage_raw.npz');out=json.loads((ROOT/'results/coverage_results.json').read_text())
        for row in out['main']:
            x=data[row['name']];self.assertAlmostEqual(x.mean(),row['mean_coverage'],places=14)
            self.assertAlmostEqual(x.std(ddof=1)/np.sqrt(len(x)),row['MC_SE'],places=14)
        x=data['independent']-data['reuse'];self.assertAlmostEqual(x.mean(),out['paired']['mean_coverage'],places=14)
    def test_raw_diagnostics_summary(self):
        data=np.load(ROOT/'results/coverage_raw.npz');out=json.loads((ROOT/'results/coverage_results.json').read_text())
        for row in out['diagnostics']:
            x=data[f"n{row['n']}_M{row['M']}"];self.assertAlmostEqual(x.mean(),row['mean_coverage'],places=14)
    def test_binary_invariance_via_exact_order(self):
        # Compare margins exactly: reciprocal score is 1+t**margin for t>1.
        margins=list(range(-10,11));cal=margins[:17];k=12;threshold=sorted(cal)[k-1]
        for t in [F(101,100),F(2),F(20)]:
            scores=[1+t**a for a in cal];q=sorted(scores)[k-1]
            self.assertEqual([1+t**a<=q for a in margins],[a<=threshold for a in margins])

if __name__=='__main__':unittest.main(verbosity=2)
