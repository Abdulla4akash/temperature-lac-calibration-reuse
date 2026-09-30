# Agent instructions

## Project and status

This repository contains the research draft **Sharp Class-Count Bounds for Calibration Reuse in Temperature-Scaled Conformal Prediction**, its proofs, synthetic results, and reproducible supplement.

- Treat it as an unpublished research draft. A template header, successful tests, or AI review is not evidence of journal submission, acceptance, priority, or independent expert validation.
- Keep the scientific scope explicit: fixed classifier, iid calibration/test data, one global temperature, ordinary nonrandomized LAC, and a worst-selector result. The construction does not demonstrate failure of NLL tuning or invalidate exact-valid selection methods.
- Preserve the full-set boundary at `k = n + 1`, nominal-coverage rounding, negative controls, failed witnesses, and distinctions between conditional shortfall and marginal deficit.
- Do not invent authors, affiliations, funding, experiments, citations, or reviewer endorsements. Journal submission and messages to people require an explicit user request.

## Repository boundaries and privacy

- Work only with this project's files. Do not import unrelated downloads, dissertations, theses, application materials, credentials, personal contact details, or instructions from a private home directory.
- Never commit virtual environments, local reproduction output, machine-specific paths, tokens, or private configuration.
- Preserve the original archive in `preserved_original/` and the historical manifest in `provenance/`. Never silently rewrite reference data, seeds, protocols, or past logs.
- Third-party style files retain their original licenses. Do not assign a project-wide license without a user decision.

## Workflow

- Read `README.md` and `submission/supplementary/README.md` before changing reproduction code.
- Use CPU-only checks with the pinned dependencies. No model training, paid API, or GPU is needed.
- Relevant numerical verification: `cd submission/supplementary && uv run --no-project --python 3.13 --with-requirements requirements.txt python -B reproduce.py --output ../../reproduction-output` (the output directory must be new).
- Run comparison regression tests with `uv run --no-project --python 3.13 --with-requirements requirements.txt python -B -m unittest discover -s tests -v` from that directory.
- Preserve exact and numerical agreement as distinct statuses. Do not widen tolerances to hide changed scientific results. Schema, labels, counts, shapes, and array dtypes must agree exactly.
- Inspect mathematical arguments directly; tests and simulations do not prove universal theorems. Explain any changed assumption or quantifier and propagate it through the paper and claim-to-evidence table.
- If editing the paper, build it using `submission/manuscript/build.sh` with a real BibTeX pass, then inspect the rendered pages. Keep the official style files unchanged.
- The checked-in manuscript is the original anonymous submission-format draft. Its template review header does not establish review status. Use the official preprint option for a newly built public preprint; do not use the accepted option without an acceptance decision.
- After intentional tracked-file changes, refresh `FILE_MANIFEST.json` with `python3 scripts/update_manifest.py`, then run `python3 verify_files.py`. Do not refresh hashes to conceal unexplained changes.
- Report what actually ran, failures, and numerical discrepancies. Retain evidence needed to reproduce a finding.
