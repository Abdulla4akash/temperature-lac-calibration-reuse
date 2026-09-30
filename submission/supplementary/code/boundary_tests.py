"""Finite implementation tests, not proof of the manuscript theorems."""
from fractions import Fraction
import unittest
import numpy as np
import coverage_embedding as c

class SubmissionBoundaryTests(unittest.TestCase):
    def test_full_set_all_small_samples(self):
        for n in range(1,9):
            u=np.full((3,n,2),.4)
            recovered,direct,err=c.latent_quantiles_from_softmax(u)
            np.testing.assert_array_equal(recovered,np.ones((3,2)))
            np.testing.assert_array_equal(direct,recovered)
            self.assertEqual(err,0.)
            self.assertEqual(c.exact_min_beta_mean(n,100),(1.,0.))
    def test_full_to_finite_boundary(self):
        self.assertEqual(c.quantile_index(8),9)
        self.assertEqual(c.quantile_index(9),9)
        self.assertAlmostEqual(c.exact_min_beta_mean(9,1)[0],.9,places=12)
    def test_decimal_and_rational_rank(self):
        for n in range(1,25):
            for coverage in (Fraction(1,10),Fraction(1,2),Fraction(9,10)):
                v=(n+1)*coverage
                expected=(v.numerator+v.denominator-1)//v.denominator
                self.assertEqual(c.quantile_index(n,coverage),expected)
                self.assertEqual(c.quantile_index(n,float(coverage)),expected)
    def test_rank_validation(self):
        for n in (0,-1,True,1.5):
            with self.assertRaises(ValueError):c.quantile_index(n)
        for cov in (0,1,-.1,float('nan'),float('inf')):
            with self.assertRaises(ValueError):c.quantile_index(5,cov)
    def test_ties(self):
        u=np.full((2,99,2),.5)
        r,d,e=c.latent_quantiles_from_softmax(u)
        np.testing.assert_array_equal(d,np.full((2,2),.5))
        self.assertLess(e,1e-10)
    def test_input_domains(self):
        for u in (np.zeros((3,2)),np.zeros((2,0,2)),np.zeros((1,5,3)),np.full((1,9,2),2.)):
            with self.assertRaises(ValueError):c.latent_quantiles_from_softmax(u)
        for delta in (0,-1,.02,float('nan')):
            with self.assertRaises(ValueError):c.latent_quantiles_from_softmax(np.zeros((1,9,2)),delta)
    def test_finite_softmax_identity(self):
        # Deterministic grid: no new random seed or experiment.
        u=np.linspace(0,1,2*99*2).reshape(2,99,2)
        r,d,e=c.latent_quantiles_from_softmax(u)
        self.assertLess(e,1e-10)
    def test_invalid_family_size(self):
        for m in (0,-1,True,1.5):
            with self.assertRaises(ValueError):c.exact_min_beta_mean(99,m)

if __name__=='__main__':unittest.main(verbosity=2)
