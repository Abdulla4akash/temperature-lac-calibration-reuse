# Supplementary material: temperature-scaled LAC calibration reuse

## What this archive supports

This is an anonymous computational supplement to **Sharp Class-Count Bounds for Calibration Reuse in Temperature-Scaled Conformal Prediction**. Complete universal proofs are in the manuscript; passing tests is not a proof. The supplement supplies exact finite certificates, the existing synthetic illustration, negative results, protocols and runnable CPU-only code. There are no real-data results, trained models or model API calls.

## Reproduce

From this directory, in Python 3.13 with the pinned dependencies installed:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python reproduce.py --output ../reproduction_output
```

The final command is offline; dependency installation requires the packages to be available. The output directory must not already exist and must be outside this supplement. The runner refuses to overwrite reference inputs, checks their hashes, constrains numerical thread counts, runs the experiment and tests, and compares all 20 raw arrays and both coverage CSVs. Pinning packages does not guarantee identical last-bit arithmetic on every operating system and CPU.

The public repository's runner distinguishes `PASS_EXACT`, `PASS_NUMERICAL`, and `DIFFERENCE`. Raw floating-point arrays permit absolute differences up to `1e-12`, with zero relative tolerance. CSV numerical summaries use absolute tolerance `1e-12` and relative tolerance `1e-10`, covering accumulated rounding in standardized diagnostics. Array keys, shapes, dtypes, table schemas, row counts, labels, and integer metadata must match exactly. Nonfinite numbers and substantive differences fail. Every comparison is saved in `comparison.json`; nothing rewrites reference results. Add `--strict` to require exact agreement and fail even on tolerated numerical differences.

Eight comparison regression tests are run in addition to the 35 original research/audit/boundary tests. They check that tiny rounding differences are reported separately while altered scientific values or output structure are rejected. See [the public repository changes](../../provenance/PUBLIC_REPOSITORY_CHANGES.md) for the observed platform differences and change history.

To repeat the preserved exploratory search as well:

```bash
python reproduce.py --full-search --output ../full_reproduction_output
```

The exploratory search is not needed to prove any theorem. It is provided to preserve unsuccessful as well as successful attempts.

## File map and evidence types

`reference/source/` and `reference/tests/` retain the original scripts and tests. `reference/results/coverage_raw.npz` contains the saved per-replication results. `coverage_main.csv` reports five procedures at n=99, with 10,000 independent calibration samples. Each calibrated softmax set has its fresh-test coverage integrated analytically. `coverage_law_diagnostics.csv` uses the derived Beta law directly and is not a collection of additional softmax experiments.

`code/coverage_embedding.py` is the reviewed implementation; the runner copies it into a fresh work tree. Its full-set branch handles k=n+1 explicitly, and input validation rejects invalid ranks, class counts and score-domain inputs. These repairs do not change the saved n=99 experiment. `code/boundary_tests.py` adds eight named tests. The original 15 tests and the earlier 12 audit tests are also retained: 35 named test methods total.

`code/audit_checks.py` uses exact rational arithmetic to integrate the primary coverage law and check delicate crossings, alongside clearly separated numerical checks. `code/chain_certificate.py` constructs exact rational linear identities and analytic Taylor remainder bounds for the K=4 and K=7 shattering witnesses. Arbitrary-precision evaluation is secondary corroboration. `expected/` stores their outputs and the existing 48-cell deterministic Beta integration grid. The grid is an illustration, not a universal lower-bound proof.

The integer-witness verification and search/certificate records in `reference/results/` retain the rejected floating-point candidate. It is distinct from the valid Taylor-certified four-class witness. No claim relies on the rejected candidate.

## Protocol and negative controls

The original local analysis protocol and its later coverage extension are both retained with their hash locks. They were local records, not externally timestamped preregistrations. No seed, grid or success criterion was changed during this submission preparation. The mathematical law was known before its simulation; the experiment checks an implementation, not a blind prediction of a discovery.

NLL tuning is an **analytic grid control**: on this construction, every observation has true class as unique argmax and increasing inverse temperature improves likelihood, so the grid choice is always beta=2. No optimizer was run. This valid negative control must not be described as a demonstrated NLL failure. Adding the argmax label to every set also eliminates the particular example's failures. Ordinary LAC is allowed to return empty sets.

One paired Monte Carlo interval in the existing results misses its expectation by 2.26 standard errors. It is preserved. No seed was rerun to make every interval contain its target.

## Resource measurements from this review

The original full reproduction used 31.98 CPU seconds (32.01 seconds elapsed; 155664 KiB peak RSS). The revised default runner, including all 35 named tests and regenerated certificates, used 20.48 CPU seconds (20.58 seconds elapsed; 155672 KiB peak RSS). Together these two externally timed suite invocations used 52.46 CPU seconds and at most 152.024 MiB. This includes repeated work, not just the core simulation.

Host: Intel Xeon Platinum 8370C @ 2.80 GHz, Linux x86_64; Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0, SymPy 1.14.0, mpmath 1.3.0. Numerical thread counts were set to one. These are hosted CPU measurements, not laptop timings. Literature retrieval, writing, proof work, rendering, setup, packaging and uninstrumented commands are excluded. No GPU, training, model API or separately provisioned paid compute was used.

`records/` contains the actual logs, including non-identifying hosted filesystem paths. The runner records per-command time on each new machine. It uses POSIX `resource`; run on Linux/macOS, or WSL on Windows. Reading these logs does not imply independent human proof validation.
