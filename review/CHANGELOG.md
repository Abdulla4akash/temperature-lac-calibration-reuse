# Change log — TMLR preparation, 30 September 2026

All edits are separate from the supplied archive. No result in the original archive was replaced.

## Essential clarifications and repairs completed

1. Made the probability space explicit (standard Borel inputs and Borel logits) and retained the pointwise-separability proof. Defined positive-part notation, inverse temperature and each coverage target. Conditional shortfall, marginal deficit and the motivating paper's absolute-gap tuning bias are not interchangeable.
2. Retained and checked the full-set k=n+1 branch in every theorem. Fixed a helper implementation that previously attempted an ordinary order statistic at that boundary; added validation and eight deterministic boundary tests. The published n=99 results remain identical.
3. Specified the NLL row as an analytically determined grid control. The code does not run an NLL optimizer; no optimizer performance is now implied.
4. Expanded the VC asymptotic step and retained simultaneous-intersection, coincident-curve and equality-threshold arguments. No numerical test substitutes for those arguments.
5. Checked the Beta-density constants, integer-shape Stirling bounds, interior range, capped t and event independence. The uniform finite-sample theorem is retained without a rate change. Nominal rounding and the binary boundary remain explicit.
6. Added the original symmetric-chain reference and the LAC source, checked the primary Haussler packing theorem, and removed an unnecessary book pinpoint whose cited edition could not be retrieved. The empirical-process argument remains supported by primary sources and the supplied entropy derivation.

## Scientific editing completed

- Changed the title to “Sharp Class-Count Bounds for Calibration Reuse in Temperature-Scaled Conformal Prediction”.
- Rewrote the abstract and introduction around the softmax-specific question and matched worst-selector rate. The motivating correction is proportionate related work, not the headline.
- Kept all complete proofs. Moved audit history, protocols, resource bookkeeping and reproduction details out of the main exposition into supplementary and author-facing files.
- Distinguished known fixed-formula quadratic growth, finite-family selection penalties and Beta-tail theory from the proposed structural advance.
- Retained every consequential limitation and negative control: adversarial selection; no NLL failure; empty sets; iid data; independently fixed classifier; potentially tiny margins; no finite-precision or operational-constant promise.
- Added a factual generative-AI assistance disclosure without inventing human authorship, funding, ethics clearance or external validation.

## Format and build

Used the current official, unmodified anonymous 10-point TMLR style and bibliography style. Removed the earlier generic article layout. The build script now requires an actual BibTeX invocation and cannot silently reuse a stale bibliography. Author metadata is empty; no identities or acknowledgments were invented. The standard template's review header does not mean a submission occurred.

## Reproduction

Original full suite: all 20 raw arrays and both coverage CSVs matched. Revised default suite: the same numerical match, 35 named tests passed, and exact certificates regenerated. The failed floating-point witness and non-covering Monte Carlo interval were not removed. No new random experiment was introduced.

## Not changed or claimed

The primary theorem's rate, exact coverage law, numerical conclusions and negative controls are unchanged. There is no new deployment algorithm, real-data experiment, proof of NLL failure, reviewer endorsement or priority certification. No journal submission or correspondence occurred.
