# Mathematical and novelty assessment

**Paper:** Sharp Class-Count Bounds for Calibration Reuse in Temperature-Scaled Conformal Prediction  
**Review date:** 30 September 2026  
**Verdict:** **Submission-ready after author review.** No substantive unresolved proof gap was identified in the stated central results. The contribution supports a standalone theory submission; a new algorithm or real-data experiment is not an essential missing component. This is an AI-assisted critical assessment, not independent external validation or a prediction of acceptance.

## 1. Central mathematics

The review independently followed the logical arguments rather than treating tests or the previous audit as proof. Let N=n+1 and p=k/N. The model is a Borel map from a standard Borel input space to finite K-dimensional logits, fixed independently of calibration. Observations are iid; the selector is measurable and uses calibration observations only. All lower constructions are fixed before the sample, although they may depend on K and the allowed temperature/logit ranges.

| Claim | Verdict | Argument checked and boundary handling | Effect on manuscript |
|---|---|---|---|
| Growth function at most min(2^m, m+1+(K−2)m(m−1)) | Verified argument | An r-term nonzero exponential sum has at most r−1 distinct real zeros by induction and Rolle. Pair differences have at most 2(K−1) terms and always vanish at beta=0, leaving at most 2K−4 positive intersections. Coincident curves merge. Inserting a graph adds at most one face per connected arc. Pair counting overestimates simultaneous intersections and tangencies. Moving a tied reciprocal cutoff upward slightly preserves all included equalities without adding an excluded point. | Retained, with explicit degeneracies. It is an upper bound, not an exact growth formula. |
| Local realization of K−1 coordinates | Verified argument | The Jacobian beta_r exp(beta_r c_j) is nonsingular: a nonzero null vector would produce an M-term exponential sum with M distinct zeros. An inverse-function neighborhood contains a common translated cube with positive radius delta. All coordinates use one fixed smooth logit map; nothing is fitted after calibration. | Retained. Any prescribed distinct positive temperatures and any B>0 are allowed; delta can depend on them and need not be numerically useful. |
| Symmetric-chain VC lower bound and class-count asymptotic | Verified argument | Each classical symmetric chain extends to prefixes of a permutation. A realized coordinate implements each permutation, so a cutoff obtains every subset. Stirling estimates for the central binomial coefficient give log2 K + 0.5 log2 log2 K + O(1) below; the growth inequality gives log2 K + 2 log2 log2 K + O(1) above. | Retained. Leading coefficient is sharp; second-order terms and all exact finite-K dimensions are not. d2=1 and d3=2 were separately checked. |
| VC-to-coverage transfer | Verified argument | P_n h_D ≥ k/n ≥ p, so conditional shortfall is bounded by the uniform empirical discrepancy. Symmetrization and the VC entropy integral give C sqrt(d/n). Rational parameter approximations with larger positive cutoff slack establish pointwise separability including ties. | Retained. Expected conditional shortfall upper-bounds marginal deficit, not vice versa. Neither is automatically the earlier paper's absolute-gap tuning bias. |
| Exact minimum-of-Beta coverage law | Verified argument | Product-uniform inputs give independent coordinate columns; their kth order statistics are iid Beta(k,N−k). Each candidate score is a strictly increasing transform of its coordinate. The normalized-cutoff selector chooses the smallest order statistic. Conditional fresh-test coverage is exactly that minimum. | Retained for k≤n. At k=N the set is full and coverage is one; Beta(k,0) is never invoked. |
| Uniform finite-sample lower bound | Verified argument | Integer-shape Stirling bounds give a density lower envelope. Independent events B1≥p and min(B2,…,BM)≤p−t produce a nonnegative loss of at least t. The capped t makes the proof valid in the saturation regime without exchanging n and M limits. Explicit constants and their dependencies were checked. | Retained without a changed rate. Constants establish existence and are very conservative. |
| Quantile rounding and small cases | Verified, implementation repaired | c≤ceil(Nc)/N<c+1/N; nominal loss subtracts at most 1/N. Binary scores have identical cross-example order at every positive temperature, so calibrated sets are unchanged. The full-set cutoff is +infinity. | No theorem change. One helper lacked the full-set branch; it and input validation were repaired. The n=99 results are unchanged. |

### Lower-bound constants and quantifiers

For 0<eta≤1/2, N≥16/eta², p in [eta,1−eta], and M≥2, the appendix defines

A_eta = exp(−1/6) sqrt(eta(1−eta)/(2 pi)), B_eta=4/eta,
r_eta=A_eta exp(−B_eta), q_eta=A_eta exp(−2 B_eta),
L_eta=(eta/4) r_eta [1−exp(−q_eta/sqrt(2))].

All are strictly positive and depend only on eta. On [eta/2,1−eta/2], the density satisfies f(x)≥A_eta sqrt(N) exp(−B_eta N(x−p)²). With h=N^−1/2 and t=(eta/4) min(1,sqrt(log(M)/N)), both integration intervals stay in that domain. The lower-tail probability is at least q_eta M^−1/2 even when log(M)≥N. Independence and (M−1)/sqrt(M)≥1/sqrt(2) give

p−E min_r B_r ≥ L_eta min(1,sqrt(log(M)/N)).

Putting M=K−1, using log(K−1)≥0.5 log K and N≤2n, gives the stated constant a_eta=L_eta/2 in the K-rate. The constants do not depend on the allowed nonempty open temperature interval or B>0. The realization radius does, so no finite-precision conclusion follows. The result is uniform over n,K in the stated regime. The separate fixed-M CLT uses a uniform second-moment bound M/4 to justify expectation convergence; it is not substituted for this finite-sample argument.

The supremum defining the risk is over classifiers, distributions and selectors. A poor selector can attain the lower rate; this is not a lower bound for every selector, an NLL theorem, or an impossibility statement for methods that change calibration to preserve validity.

## 2. Specific novelty comparison

References below are primary sources. Versions are recorded because theorem numbering may change.

| Prior result and inspected source | Assumptions and conclusion already established | Exact overlap and addition here |
|---|---|---|
| Aschenbrenner et al., Theorem 1.1, [arXiv:1109.5438v1](https://arxiv.org/html/1109.5438v1) | A fixed definable formula in a weakly o-minimal theory has VC density no larger than its parameter count. In the real exponential structure, two parameters imply O_K(m²) growth. | Fixed-K quadratic growth is already known. The formula-dependent constant is not an explicit K-dependent coefficient, leading VC asymptotic, or coordinate realization. The proposed advance is quantitative dependence across K and its coverage consequence. |
| Karpinski–Macintyre, Theorem 2 and exponential-polynomial example, [author PDF](https://theory.cs.uni-bonn.de/marek/publications/poly_bounds_for_vc_dim.pdf) | Bounds VC dimension using a uniform connected-component bound B, number of atomic predicates s and parameters l: at most 2 log2 B +(16+2 log2 s)l. General Pfaffian specializations yield broader polynomial upper bounds. | The parameter-space geometry approach is prior art. Its general component bound does not supply this sharp coefficient or fixed-model realization without a new specialized argument. |
| Yang–Kuchibhotla, Theorem 1, [arXiv:2104.13871v3](https://arxiv.org/html/2104.13871v3) | Fixed finite family of nested scores, independent training and iid calibration: selection costs O(sqrt(log J/n)); split-again procedures are also studied. | The logarithmic selection penalty is known. This paper bounds the continuum and realizes J=K−1 independent coordinates inside one global-temperature classifier. It does not introduce the finite-family penalty. |
| Zeng et al., Lemmas D.3–D.6 and D.8, [arXiv:2502.03023v2](https://arxiv.org/html/2502.03023v2), [ICML record](https://proceedings.mlr.press/v267/zeng25e.html) | Valid empirical-process/VC transfer and binary order preservation; inspected version also uses a continuity/boundedness parameter-count implication. | Transfer and binary invariance are credited. The specific softmax class is analyzed directly, avoiding that implication. The paper does not claim their practical experiments are false. |
| Zhang–Zhou, Theorem 8, [arXiv:1810.09006v3](https://arxiv.org/html/1810.09006v3) | Nonasymptotic Beta upper/lower tails with shape parameters at least one; extreme-value arguments follow from these tails. | The probability mechanism is established. The appendix gives explicit conservative constants for the exact uniform regime needed here, not a new standalone probability theorem. |
| Liang–Zhu–Barber, Theorems 3.1 and 3.3, [arXiv:2408.07066v4](https://arxiv.org/html/2408.07066v4) | Exchangeability and suitable full-conformal symmetry give exact-valid selection procedures without another split. | Different procedure. Their validity does not conflict with the lower bound for unmodified same-data LAC; no superiority over them is claimed. |
| Hegazy et al., stable-selector guarantee, [arXiv:2506.20173v1](https://arxiv.org/html/2506.20173v1); Wang–Wang, Theorem 1, [arXiv:2602.19284v1](https://arxiv.org/html/2602.19284v1) | Stability restrictions or localized symmetric construction protect post-selection coverage. | These are existing positive reuse routes. The unrestricted worst-selector result cannot be marketed as ruling them out. |
| Dabah–Tirer, [ICML 2025](https://proceedings.mlr.press/v267/dabah25a.html); Mattei–Loureiro, Proposition 1, [arXiv:2602.14862v2](https://arxiv.org/html/2602.14862v2) | Temperature-dependent conformal efficiency/coverage trade-offs and softmax/NLL structure. | Temperature effects and within-example order preservation are not new. The contribution concerns cross-example true-label threshold orderings and their worst-selector consequence. |

The symmetric-chain theorem is explicitly credited to [de Bruijn et al. (1951), Theorem 2](https://pure.tue.nl/ws/files/4373475/597494.pdf). The original theorem and inductive construction were read. [Haussler's packing theorem](https://www.cs.columbia.edu/~djhsu/coms4995-s20/haussler-packing.pdf) supports the VC entropy step. These are tools, not discoveries claimed by this work. Theorem 1 and Corollary 53 of [Combinatorial Bounds in Distal Structures](https://arxiv.org/html/2104.07769v2) were also inspected: their fixed-formula density/incidence conclusions do not supply an equivalent K-uniform softmax realization.

**Defensible novelty statement:** the explicit class-count analysis, local fixed-softmax realization at prescribed temperatures, and their combination into a matching uniform worst-selector coverage rate. The inspected sources do not subsume this combination. The proof's use of classical tools does not make the combination automatically old. Conversely, an unsuccessful search is not evidence of priority.

### Access and search limitations

Searches covered temperature/LAC, selection and stability, softmax/exponential/Pfaffian VC and pseudodimension, weakly o-minimal/distal arrangements, local interpolation, symmetric chains, and Beta/order-statistic minima. Some searches returned irrelevant results and were not counted as evidence of absence. Author/preprint primary sources were used when publisher pages failed.

The motivating paper's OpenReview discussion returned a browser challenge; the official proceedings PDF could not be byte-compared with the inspected arXiv v2. Hence the motivating criticism remains version-specific and the absence of a correction is not asserted. The full publisher text for Yang–Kuchibhotla and some journal metadata pages was inaccessible; the cited arXiv theorem versions were read. An inaccessible book-edition pinpoint was removed as unnecessary; the primary entropy support remains. Priority is provisional in the normal sense of a literature-based scholarly claim, not externally certified.

## 3. Significance and readiness

The scientific contribution is a quantitative boundary for a common score family. It shows that bounded logits, a compact temperature search range and one scalar parameter do not force a class-count-independent reuse rate. It also gives a continuum upper bound rather than only a counterexample. Researchers developing selector-specific guarantees or evaluating conformal tuning can use this as a worst-case reference and as an explicit stress-test family.

The adversarial selector and small margins materially limit deployment advice, but they do not invalidate a structural worst-case theorem. The empty-set mechanism narrows this example further; a forced-argmax variant is outside scope. No claim of widespread failure, NLL failure, improved set size, or a recommended algorithm is needed for the theory contribution. The results do not determine every finite-K VC dimension or match second-order terms.

[Official TMLR criteria](https://jmlr.org/tmlr/acceptance-criteria.html) center on supported claims and interest to some ML researchers; they do not automatically require a new algorithm or real-data result. This manuscript has a coherent theory claim worth submitting under those criteria. Whether reviewers judge the advance sufficiently informative remains an editorial decision, not something an audit can guarantee.

**Essential technical fixes are complete.** No additional theorem or experiment is specified as a submission prerequisite. Remaining actions are author review and responsibility, accurate authorship/affiliation/funding/conflict information, policy and eligibility checks, and final anonymous-file inspection. None was fabricated or performed on the author's behalf. Ordinary likelihood tuning, finite precision and sharper second-order VC terms are optional future work, not new blockers.

A subsequently identified equivalent prior theorem could remove the originality claim; an independently found proof error could require revision. Neither is currently an identified unresolved mathematical gap. Repeated AI review is not independent expert endorsement. Nothing was submitted or sent to anyone.
