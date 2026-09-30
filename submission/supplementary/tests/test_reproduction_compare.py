"""Reject scientific/structural changes while reporting rounding separately."""
from pathlib import Path
import sys
import tempfile
import unittest
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from reproduction_compare import compare_results


class ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.expected = Path(self.tmp.name)/"expected"
        self.actual = Path(self.tmp.name)/"actual"
        for path in (self.expected, self.actual):
            path.mkdir()
            np.savez(path/"coverage_raw.npz", reuse=np.array([.1, .9], dtype=np.float64))
            for name in ("coverage_main.csv", "coverage_law_diagnostics.csv"):
                (path/name).write_text("name,n,mean_coverage,z_from_exact\nexample,99,0.9,2.0\n")

    def compare(self):
        return compare_results(self.expected, self.actual)

    def test_identical_outputs_are_exact(self):
        self.assertEqual(self.compare()["status"], "PASS_EXACT")

    def test_last_bit_differences_are_reported_separately(self):
        np.savez(self.actual/"coverage_raw.npz", reuse=np.array([.1, .9+3e-16]))
        p = self.actual/"coverage_law_diagnostics.csv"
        p.write_text(p.read_text().replace("2.0", "2.0000000000028"))
        result = self.compare()
        self.assertEqual(result["status"], "PASS_NUMERICAL")
        self.assertFalse(result["exact"])

    def test_material_array_difference_fails(self):
        np.savez(self.actual/"coverage_raw.npz", reuse=np.array([.1, .9001]))
        self.assertEqual(self.compare()["status"], "DIFFERENCE")

    def test_material_summary_difference_fails(self):
        p = self.actual/"coverage_main.csv"
        p.write_text(p.read_text().replace("0.9", "0.901"))
        self.assertEqual(self.compare()["status"], "DIFFERENCE")

    def test_extra_or_missing_array_keys_fail(self):
        for values in ({"other": np.array([.1, .9])}, {"reuse": np.array([.1, .9]), "extra": np.array([.1])}):
            with self.subTest(keys=list(values)):
                np.savez(self.actual/"coverage_raw.npz", **values)
                self.assertEqual(self.compare()["status"], "DIFFERENCE")

    def test_shape_dtype_and_nonfinite_changes_fail(self):
        for values in (np.array([[.1, .9]]), np.array([.1, .9], dtype=np.float32), np.array([np.nan, .9]), np.array([np.inf, .9])):
            with self.subTest(values=values):
                np.savez(self.actual/"coverage_raw.npz", reuse=values)
                self.assertEqual(self.compare()["status"], "DIFFERENCE")

    def test_schema_labels_counts_and_nonfinite_summaries_fail(self):
        p = self.actual/"coverage_main.csv"
        baseline = p.read_text()
        for text in (baseline.replace("mean_coverage", "other"), baseline.replace("example", "changed"),
                     baseline.replace(",99,", ",100,"), baseline.replace("0.9", "nan"), baseline+"example,99,0.9,2.0\n"):
            with self.subTest(text=text):
                p.write_text(text)
                self.assertEqual(self.compare()["status"], "DIFFERENCE")

    def test_reordered_or_malformed_rows_fail(self):
        p = self.actual/"coverage_main.csv"
        p.write_text("name,n,mean_coverage,z_from_exact\nexample,99,0.9,2.0,unexpected\n")
        self.assertEqual(self.compare()["status"], "DIFFERENCE")
        baseline = "name,n,mean_coverage,z_from_exact\na,99,0.9,2.0\nb,99,0.8,1.0\n"
        (self.expected/p.name).write_text(baseline)
        lines = baseline.splitlines()
        p.write_text("\n".join([lines[0], lines[2], lines[1]])+"\n")
        self.assertEqual(self.compare()["status"], "DIFFERENCE")


if __name__ == "__main__":
    unittest.main(verbosity=2)
