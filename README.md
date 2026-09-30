# Temperature-scaled conformal calibration reuse

Research materials for **Sharp Class-Count Bounds for Calibration Reuse in Temperature-Scaled Conformal Prediction**.

**Status: unpublished research draft, prepared for author review.** This repository is not evidence of TMLR submission or acceptance. The supplied PDF uses the anonymous TMLR submission template, whose automatic “under review” header does not describe an actual submission. Correctness, originality, and significance remain subject to specialist scrutiny.

## Start here

- [Manuscript PDF](submission/manuscript/main.pdf) — 13 pages including references and complete proof appendices.
- [LaTeX source](submission/manuscript/main.tex) and [bibliography](submission/manuscript/references.bib).
- [Computational supplement](submission/supplementary/README.md) — code, raw results, exact certificates, negative controls, and original execution records.
- [Plain-language author guide](review/AUTHOR_GUIDE.md).
- [Mathematical and novelty assessment](review/MATHEMATICAL_AND_NOVELTY_ASSESSMENT.md) — an AI-assisted assessment, not external peer review.
- [Claim-to-evidence map](submission/CLAIM_EVIDENCE.csv), [revision history](review/CHANGELOG.md), and [submission checklist](review/TMLR_CHECKLIST.md).
- [Agent instructions](AGENTS.md) for future work in this repository.

## Research question

How much coverage can be lost when a global softmax temperature is selected using the same observations that calibrate an ordinary LAC prediction set?

The manuscript gives an explicit class-count-dependent growth bound, a VC dimension asymptotic to `log2(K)`, a fixed-softmax realization of independently varying score coordinates, and a matching uniform worst-selector coverage-deficit rate of `min(1, sqrt(log(K) / n))` in its stated interior-coverage regime.

The lower construction uses an adversarial selector. It does not demonstrate failure of ordinary likelihood tuning. The classifier is fixed independently of calibration, data are iid, prediction sets may be empty, and the construction may require tiny numerical margins. The constants do not provide practical sample-size prescriptions. See the paper for all assumptions and quantile boundary cases.

## Reproduce on a CPU

Python 3.13 and the pinned packages in the supplement are sufficient; no GPU, training, or model API is needed. With `uv` installed, run from the repository root:

```bash
python3 verify_files.py
cd submission/supplementary
uv run --no-project --python 3.13 --with-requirements requirements.txt python -B reproduce.py --output ../../reproduction-output
```

The output directory must be new. A standard virtual-environment alternative is in the [supplement README](submission/supplementary/README.md).

The runner retains the original reference data and reports one of `PASS_EXACT`, `PASS_NUMERICAL`, or `DIFFERENCE`. Numerical agreement allows only documented tiny floating-point differences; original exact-match results remain visible. Use `--strict` to require exact agreement. See [the public repository changes](provenance/PUBLIC_REPOSITORY_CHANGES.md) for tolerances and the macOS reproduction findings.

The original research, mathematical-audit, and boundary suites have 35 named test methods. Additional regression tests exercise the comparison layer. These checks support implementation reliability; they do not prove the manuscript's universal mathematical statements.

## Build the manuscript

With a TeX distribution providing pdfLaTeX, BibTeX, and the required packages:

```bash
bash submission/manuscript/build.sh
```

The supplied build uses the original anonymous submission layout. For a newly generated public preprint, use `\usepackage[preprint]{tmlr}` and review the authorship line. Keep the original style files unchanged. Do not label the paper accepted or submitted without an actual decision or submission record.

## Provenance and integrity

The downloaded revision's research files and review records are preserved here. The earlier complete research archive remains under [preserved_original](preserved_original/); its historical file manifests are retained. [FILE_MANIFEST.json](FILE_MANIFEST.json) describes this repository snapshot, while [the original revision manifest](provenance/ORIGINAL_TMLR_FILE_MANIFEST.json) records the input package.

For intentional repository changes, refresh the current manifest with `python3 scripts/update_manifest.py`, then run `python3 verify_files.py`. Do not alter historical manifests or baseline results to make a comparison pass.

Generative AI assisted the research, code, review, and drafting. The original disclosure is retained. Human authorship and accountability must be settled before any journal submission.

## Licensing

No project-wide license has been selected. Public availability alone does not grant a general reuse license. The bundled TMLR style files retain their existing third-party license terms; see [style attribution](submission/manuscript/THIRD_PARTY_STYLES.md) and [the repository license supplied with those styles](submission/manuscript/STYLE_REPOSITORY_LICENSE.txt).
