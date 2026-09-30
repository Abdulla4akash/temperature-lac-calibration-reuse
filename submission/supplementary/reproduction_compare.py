"""Report exact and numerical reproduction separately, with fixed tolerances."""
import csv
import math
from pathlib import Path
import numpy as np

ARRAY_ATOL = 1e-12
CSV_ATOL = 1e-12
CSV_RTOL = 1e-10
EXACT_COLUMNS = {"name", "procedure", "n", "M", "replications", "total_observations"}


def compare_csv(expected_path, actual_path):
    def read(path):
        with Path(path).open(newline="") as handle:
            reader = csv.DictReader(handle)
            return reader.fieldnames, list(reader)
    fields, expected = read(expected_path)
    actual_fields, actual = read(actual_path)
    report = {"exact": Path(expected_path).read_bytes() == Path(actual_path).read_bytes(),
              "numerical_agreement": False, "changed_cells": 0,
              "max_absolute_difference": 0.0, "failures": []}
    if fields != actual_fields or len(expected) != len(actual):
        report["failures"].append("CSV columns or row counts differ")
        return report
    for index, (left, right) in enumerate(zip(expected, actual)):
        if None in left or None in right or any(v is None for v in (*left.values(), *right.values())):
            report["failures"].append(f"Malformed CSV row {index + 1}")
            continue
        for field in fields:
            a, b = left[field], right[field]
            report["changed_cells"] += int(a != b)
            if field in EXACT_COLUMNS:
                ok = a == b
            else:
                try:
                    x, y = float(a), float(b)
                except ValueError:
                    ok = a == b
                else:
                    finite = math.isfinite(x) and math.isfinite(y)
                    ok = finite and math.isclose(x, y, rel_tol=CSV_RTOL, abs_tol=CSV_ATOL)
                    if finite:
                        report["max_absolute_difference"] = max(report["max_absolute_difference"], abs(x-y))
            if not ok:
                report["failures"].append(f"Row {index + 1}, field {field}")
    report["numerical_agreement"] = not report["failures"]
    return report


def compare_arrays(expected_path, actual_path):
    report = {"exact": False, "numerical_agreement": False, "arrays": {}, "failures": []}
    with np.load(expected_path, allow_pickle=False) as expected, np.load(actual_path, allow_pickle=False) as actual:
        if set(expected.files) != set(actual.files):
            report["failures"].append("Array keys differ")
            return report
        for key in expected.files:
            a, b = expected[key], actual[key]
            if a.shape != b.shape or a.dtype != b.dtype or a.dtype.kind != "f":
                report["failures"].append(f"Array shape or floating dtype differs: {key}")
                continue
            if not (np.isfinite(a).all() and np.isfinite(b).all()):
                report["failures"].append(f"Nonfinite array values: {key}")
                continue
            difference = np.abs(a - b)
            maximum = float(difference.max()) if difference.size else 0.0
            report["arrays"][key] = {"exact": a.tobytes() == b.tobytes(),
                                     "numerical_agreement": maximum <= ARRAY_ATOL,
                                     "max_absolute_difference": maximum,
                                     "changed_entries": int(np.count_nonzero(difference))}
            if maximum > ARRAY_ATOL:
                report["failures"].append(f"Array values differ beyond tolerance: {key}")
    report["numerical_agreement"] = not report["failures"]
    report["exact"] = report["numerical_agreement"] and all(r["exact"] for r in report["arrays"].values())
    return report


def compare_results(expected_dir, actual_dir):
    expected_dir, actual_dir = Path(expected_dir), Path(actual_dir)
    tables = {name: compare_csv(expected_dir/name, actual_dir/name)
              for name in ("coverage_main.csv", "coverage_law_diagnostics.csv")}
    arrays = compare_arrays(expected_dir/"coverage_raw.npz", actual_dir/"coverage_raw.npz")
    checks = [*tables.values(), arrays]
    exact = all(r["exact"] for r in checks)
    numerical = all(r["numerical_agreement"] for r in checks)
    return {"status": "PASS_EXACT" if exact and numerical else "PASS_NUMERICAL" if numerical else "DIFFERENCE",
            "exact": exact, "numerical_agreement": numerical,
            "tolerances": {"array_atol": ARRAY_ATOL, "array_rtol": 0.0, "csv_atol": CSV_ATOL, "csv_rtol": CSV_RTOL},
            "tables": tables, "raw_arrays": arrays}
