# Author guide: understanding and defending the paper

## What the paper says in plain language

A classifier can return a set of plausible labels rather than one label. Calibration chooses a cutoff so that this set contains the true label at a specified long-run rate. A temperature changes the classifier's probabilities. When the temperature is chosen using the same observations that set the cutoff, the two steps can select a misleadingly favorable pattern.

The familiar part is that adaptive selection can overfit. Your paper asks the more specific question: how much freedom does the actual one-temperature softmax family have, and how does the number of classes affect it?

Its answer has two sides. The family is restricted enough that its worst possible coverage loss has an upper bound. Yet it is flexible enough to attain a matching order of loss. In the stated interior regime, the worst loss scales like the square root of log(class count) divided by calibration sample size, until it reaches a constant order. This is a worst-case rate with unspecified/conservative constants, not a forecast that a particular model will lose that much coverage.

The central construction keeps the classifier fixed before calibration. Different temperatures reveal different coordinates of its inputs. A selector can then choose whichever coordinate had the smallest calibration cutoff. Fresh observations do not inherit that unusually small cutoff, which produces the exact minimum-of-Beta coverage law.

The paper is not saying ordinary NLL temperature tuning fails. In the explicit example, it does not. It is not saying exact-valid reuse is impossible: existing methods change the calibration procedure or restrict selection. It is not a practical algorithm proposal.

## The four ideas to understand first

**Order statistics.** Sort n calibration scores. The kth smallest is an order statistic. For independent uniform scores, its distribution is Beta(k,n+1−k). Its mean is k/(n+1). The k=n+1 case is not an ordinary order statistic: conformal prediction uses a full set instead.

**VC dimension.** This measures how many arbitrary include/exclude decisions a threshold family can express on a finite collection of examples. It is not the number of adjustable scalar parameters. Here the threshold and temperature jointly define the class, whose capacity grows asymptotically like log2 K.

**Local invertibility.** If a smooth map has an invertible Jacobian at one point, small changes in its outputs can be realized by small changes in its inputs. The paper proves that invertibility for a particular exponential-sum map. That is how multiple score coordinates are realized without modifying the classifier after calibration.

**Conditional versus marginal coverage.** Conditional coverage describes the future success rate after fixing one calibration sample. Marginal coverage averages over calibration samples. A valid fixed-score method can fluctuate around its target conditionally while maintaining the marginal guarantee.

## Questions you should be able to answer

### 1. What is the new result, rather than the known overfitting observation?

Explain the explicit K-dependent growth bound, the fixed-softmax coordinate realization, and the matched uniform worst-selector rate. Credit the classical VC inequality, finite-family penalty, inverse-function theorem, symmetric chains and Beta-tail behavior. Fixed-K quadratic growth is already implied by definability results.

### 2. What exactly does “one temperature” mean?

There is one global beta=1/T applied to all class logits for every example. It may be selected from calibration data. There is no vector scaling, input-dependent temperature, retraining or test-label-based tuning. The conformal cutoff is also data-dependent, as it is in ordinary calibration.

### 3. Why does beta=0 matter even though allowable beta is positive?

Every reciprocal true-label probability equals K at beta=0. Each nonidentical pair difference therefore already spends one of its possible real zeros there. Subtracting it reduces the maximum positive intersections to 2K−4. This is a boundary fact about the curves, not an allowed tuning value.

### 4. How are ties and coincident curves handled?

Coincident curves cannot label their points independently. Merge them for the upper bound. When a cutoff equals several curve values, move the reciprocal cutoff slightly upward without crossing an excluded value. That reproduces the same binary pattern in an open face. Tangencies and simultaneous crossings do not invalidate the overcounting upper bound.

### 5. Is the constructed classifier really fixed before calibration?

Yes. Choose temperatures, baseline logits, local inverse and perturbation radius first. These define one deterministic smooth map u to z(u). Then draw the iid calibration inputs. The temperature selector changes only which coordinate is exposed; it never changes the model. The construction may depend on K and the allowed ranges but not on the realized sample.

### 6. What does the symmetric-chain argument contribute?

A score coordinate gives one ordering of the sample points, and its cutoffs give prefixes of that ordering. A classical partition of all subsets into symmetric chains shows that central-binomially many such orderings suffice to represent every subset. This is stronger than allocating one coordinate to every binary pattern. The combinatorial decomposition itself dates to 1951.

### 7. Why does the upper bound apply to any measurable temperature selector?

Whichever temperature is chosen, its calibrated set includes at least k of the n calibration observations. The gap between empirical and fresh coverage is no larger than the largest discrepancy across the entire threshold class. A VC bound controls that common discrepancy, so it does not need to inspect the selector's objective. Measurability is established with a countable pointwise approximation.

### 8. Where does independence enter the lower proof?

Each observation has independent uniform coordinates and observations are independent. Hence complete columns of calibration coordinates are independent, and so are their kth order statistics. Once the calibration sample and selected coordinate are fixed, the fresh coordinate is still uniform. It would be wrong to assume independent cutoffs for arbitrary real model predictions.

### 9. Is the rate theorem uniform or only asymptotic?

The central finite-sample theorem holds simultaneously for all K≥3 and n+1≥16/eta² with k/(n+1) in [eta,1−eta]. Its constants depend only on eta. The proof caps its tail displacement, covering the saturation regime. The separate Gaussian-maximum argument takes n to infinity with M fixed and then M to infinity; it is not the proof of uniformity.

### 10. What changes at k=n+1, K=2, or nominal coverage c?

At k=n+1 the prediction set is full, so coverage is one. At K=2 positive temperature preserves all score ordering and the calibrated sets themselves, so marginal deficit is zero. For nominal c, the finite-rank p=ceil((n+1)c)/(n+1) can be slightly larger than c; the lower nominal deficit subtracts at most 1/(n+1). Conditional fluctuations need not vanish in the binary case.

### 11. What did the experiment actually run?

It repeated 10,000 n=99 calibration samples for the existing three-class construction, computing logits, softmax scores and cutoffs, then integrating fresh-test coverage analytically. The exact expected adversarial coverage is about 88.3287%, and the reproduced mean is 88.2848%. The NLL row uses its analytically known grid choice beta=2, not a numerical optimizer. Other grids sample the Beta law or perform deterministic integration and must not be described as real-data or additional classifier experiments.

### 12. What can a reviewer reasonably object to?

The selector is adversarial; the realization may need tiny margins; possible empty sets drive the explicit example; and the constants are not practical correction factors. Answer by limiting the claim to a structural worst-case characterization, not by implying these concerns are experimentally refuted. A reviewer may also identify specialized prior art. Compare its actual quantifiers, K dependence and realized family before arguing priority.

## What not to say

Do not claim to have invented parameter-count counterexamples, VC theory, the inverse-function theorem, symmetric chains or Beta extreme-value behavior. Do not call the experiments independent external verification, the protocol externally preregistered, the new witnesses exact finite-K VC dimensions, or NLL tuning unsafe on this evidence. Do not describe the worst-selector result as minimax impossibility for all valid conformal procedures.

## Before approving submission

Read the manuscript and proofs until you can explain the above without relying on an AI verdict. Reproduce the code and understand what its assertions do and do not check. Confirm that the AI-use disclosure is accurate and complete; it cannot certify your personal contribution. Determine genuine authorship, affiliations, contributions, funding, conflicts and submission eligibility. No author identities or declarations have been invented in the draft.

TMLR permits assistive language-model use but holds human authors responsible for correctness and all policy compliance. It does not allow a language model to be an author. Its authorship and accountability criteria must be satisfied by the actual human authors. See the official editorial policies in TMLR_CHECKLIST.md. An anonymous draft is not an exemption from those obligations.
