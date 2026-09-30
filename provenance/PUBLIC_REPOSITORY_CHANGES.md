# Public repository preparation

The input was the downloaded `temperature_lac_TMLR_revision.zip`. The manuscript PDF, LaTeX, bibliography, original research code, reference results, protocols, exact-certificate scripts, and historical review records are preserved. The earlier research archive remains byte-for-byte intact in `preserved_original/`.

## Repository documentation

Added a public README, project-specific `AGENTS.md`, a `.gitignore`, and a current-manifest refresh script. The input README and file manifest were moved into this provenance directory. They are historical records, not the current repository manifest. The PDF's TMLR template review header is explicitly explained as formatting, not evidence of an actual journal submission. No author list, project-wide license, acceptance, or independent expert endorsement was added.

## Reproduction portability

The original runner required exact equality for every saved array and CSV. On the reviewed macOS ARM64 machine, Python 3.13.5 and the same pinned numerical packages reproduced all five main raw arrays and the main coverage CSV exactly. The 15 additional Beta-law diagnostic arrays differed by at most `3.3306690738754696e-16`. Derived diagnostic CSV cells differed by at most approximately `2.783e-12`. All 35 supplied test methods passed. These last-bit differences made the original runner exit with `DIFFERENCE`.

The public runner adds a comparison layer that retains exact-match information and reports:

- `PASS_EXACT`: exact array values and CSV bytes, with valid structure and finite numerical data.
- `PASS_NUMERICAL`: only differences within the fixed, documented tolerances.
- `DIFFERENCE`: altered structure, nonfinite values, or differences beyond tolerance.

Raw floating-point probability arrays use absolute tolerance `1e-12`, with zero relative tolerance. This allows tiny arithmetic differences while rejecting changed scientific values. CSV floating-point summaries use absolute tolerance `1e-12` and relative tolerance `1e-10` because standardization can amplify last-bit differences in means and standard errors. These allowances are far smaller than the reported Monte Carlo uncertainty. Keys, shapes, dtypes, column/row structure, labels, and integer metadata must match exactly.

The new `--strict` option retains exact-only exit behavior. Reference outputs, seeds, protocols, and historical logs are unchanged; comparisons never rewrite them. Eight new regression tests distinguish tolerated rounding from altered values, missing/extra arrays, shape/dtype changes, nonfinite results, and table-structure changes.

The complete public runner passed all **43 test methods** (35 inherited plus eight comparison tests) and returned `PASS_NUMERICAL`. Machine-path-free comparison details and a summary are stored alongside this note. No new stochastic research experiment or mathematical claim was introduced by the repository changes. The original 52.46 CPU-second measurement describes the earlier hosted runs, not this local verification.

## File integrity and public scope

The current `FILE_MANIFEST.json` is separate from `ORIGINAL_TMLR_FILE_MANIFEST.json`. It covers the tracked public research materials and new repository files. Private local reproduction directories and Git metadata are excluded. A recursive scan of the original nested archives and current public files found no credentials, private contact details, private user-machine paths, or unrelated thesis/application material in the initial copied publication set. Checks of tracked files were repeated before publication.

Public availability does not establish peer-review acceptance, scientific priority, or permission under an unspecified project-wide license. Third-party style licenses remain in force.
