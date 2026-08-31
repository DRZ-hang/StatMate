# Statistical Methods — choosing, justifying, reporting

The figure's statistics must match the **study design**, not the chart you'd like to draw.
Compute every statistic in code (scipy / statsmodels / pingouin / lifelines); never write a
p-value or CI you didn't calculate. This file helps you pick the right test, check its
assumptions, correct for multiplicity, and report it honestly in the caption.

## Table of contents
1. First, classify the design
2. Comparing groups (the common case)
3. Associations & regression
4. Categorical data
5. Survival / time-to-event
6. Models for non-continuous outcomes
7. Covariates, confounding, and interactions
8. Assumptions and diagnostics
9. Multiple comparisons
10. Error bars: SD vs SEM vs CI
11. Effect sizes and reporting
12. p-value hygiene

---

## 1. First, classify the design
Answer these before choosing a test:
- **Outcome type:** continuous, count, proportion, ordinal, time-to-event?
- **Number of groups/conditions:** 1, 2, or >2?
- **Paired or independent?** Repeated measures on the same unit → paired/within-subject.
- **Unit of analysis / n:** what is one independent observation? Pseudoreplication (treating
  technical replicates as independent) inflates n and is a top reviewer complaint.
- **Covariates** to adjust for?

## 2. Comparing groups (continuous or ordinal outcome)
Name the estimand first: mean difference, median/quantile difference, stochastic ordering, or a
broader distributional contrast. These are not interchangeable.

- **2 independent groups, mean difference:** Welch's t-test or an equivalent linear model is a
  useful default when independent observations and a meaningful mean are defensible. Inspect the
  distribution and influential observations; moderate non-normality alone does not automatically
  invalidate mean-based inference. For very small, heavy-tailed, or contaminated samples, consider
  a justified robust, permutation, or bootstrap analysis that still targets the intended effect.
- **Mann–Whitney U:** use when a rank/distribution estimand is scientifically meaningful. It is not
  automatically a test of medians; a median-shift interpretation needs additional shape/location
  assumptions. Small sample size by itself is not a reason to switch tests.
- **2 paired conditions:** use a paired mean-difference analysis when that estimand fits. A
  Wilcoxon signed-rank analysis concerns the distribution of paired differences and relies on a
  symmetry assumption; a sign or permutation procedure may fit a different estimand.
- **>2 independent groups:** use a linear model/ANOVA family for planned mean contrasts, with
  heteroscedastic methods when needed. Use rank-based methods only when their distributional
  estimand is intended. Match post-hoc contrasts and multiplicity control to the primary model.
- **>2 repeated conditions:** use a repeated-measures or mixed model when trajectories, missing
  visits, covariates, or unequal spacing matter. Friedman is a narrow rank-based option for a
  complete simple block design, not a universal non-parametric replacement.
- **Two or more factors:** use a model with planned main effects/interactions and report estimated
  contrasts with intervals, rather than choosing separate tests from each plotted panel.
- **Nested/clustered data (cells within animals, repeated patients):** use a model or design-based
  analysis that represents the hierarchy. A random-intercept mixed model is one option, not an
  automatic fix for every clustered design.

## 3. Associations & regression
- Linear association, continuous, ~normal → **Pearson r**; monotonic/non-normal/ordinal →
  **Spearman ρ**. Report r/ρ, CI, p, and n.
- Predicting a continuous outcome → linear regression; report coefficients, CI, R².
- Always plot the data behind a correlation (Anscombe's quartet: same r, wildly different
  data). Don't report r without the scatter.

## 4. Categorical data
- 2×2 or R×C counts → use a χ² analysis when its approximation is adequate. For sparse tables,
  choose an exact or Monte-Carlo procedure appropriate to the table and sampling design; the
  common “expected count <5” rule is a warning, not a universal switch. Fisher's exact test is a
  standard 2×2 option but answers a conditional question.
- Paired proportions → McNemar.
- Report counts and proportions, the test, and an effect measure (odds/risk ratio with CI).

## 5. Survival / time-to-event
- Kaplan–Meier estimate + **log-rank** test for group differences.
- Adjusted analysis → Cox proportional-hazards; report HR with CI and check the
  proportional-hazards assumption using global and covariate-level evidence plus graphical
  assessment. If a scientifically important violation remains material, use a justified
  time-varying/stratified model, alternative estimand such as restricted mean survival time, or
  clearly downgrade the result from final. Use `lifelines` where appropriate.

## 6. Models for non-continuous outcomes
- Binary outcome → binomial/logistic model; report a clearly defined odds, risk, or
  prevalence contrast with CI. Do not interpret an odds ratio as a risk ratio.
- Count outcome → Poisson only when its mean/variance structure is plausible; otherwise
  consider negative-binomial or other justified count models. Use an exposure offset for rates.
- Ordinal outcome → ordinal model rather than silently treating categories as equally spaced;
  check the model's ordering/proportional-odds assumption.
- Proportion with a known denominator → binomial model when individual Bernoulli trials or
  numerator/denominator counts are available; avoid ordinary linear regression by habit.
- Clustered or repeated non-continuous outcomes → GEE or a suitable generalized mixed model.

## 7. Covariates, confounding, and interactions
- Choose covariates from the design, prior knowledge, and estimand—not automated p-value screening.
- Distinguish confounders, precision variables, mediators, and colliders. Adjusting for a mediator
  or collider can change the question or introduce bias.
- Preserve continuous predictors when possible. Categorizing at a data-derived cutoff discards
  information and can inflate false-positive findings.
- Check functional form and clinically plausible nonlinearity; use splines or transformations when
  justified and report them.
- Test an interaction when claiming effects differ across subgroups. “Significant here but not
  there” is not itself evidence of interaction.
- Report both unadjusted and planned adjusted estimates when they answer useful distinct questions.

## 8. Assumptions and diagnostics
- **Normality:** look at the distribution (histogram/QQ) more than Shapiro p-values; small
  n makes normality tests useless, large n makes them over-sensitive.
- **Equal variance:** Levene's test / just use Welch by default.
- **Independence:** the design tells you, not a test. Clustered data → mixed model.
- **Linear/regression models:** inspect residual structure, functional form, influential
  observations, collinearity, and heteroscedasticity.
- **Generalized models:** inspect calibration/fit, separation, overdispersion, and influential
  observations as relevant.
- **Mixed models:** check convergence, singular fits, and whether the random-effects structure is
  supported by the design and data.
- If an assumption fails, choose a method that matches the estimand and data-generating structure;
  a non-parametric test is not an automatic universal fix.

## 9. Multiple comparisons
If you run many tests (multiple pairwise comparisons, many outcomes, omics), **correct**:
- Few planned comparisons → Bonferroni/Holm.
- Many tests, discovery setting → Benjamini–Hochberg FDR (report adjusted p-values or the specific
  q-value procedure actually used).
State the correction in the caption. Marking 15 uncorrected pairwise stars is misleading.

## 10. Error bars: SD vs SEM vs CI
Pick deliberately and **always define it in the caption** — this is the single most common
caption omission.
- **SD** describes the spread of the data (how variable individuals are).
- **SEM** describes the precision of the mean estimate (≈ SD/√n) — it shrinks with n and is
  *not* a description of data spread; don't use it to imply small variability.
- **95% CI** is usually the most interpretable for inference.
Whatever you choose, write "error bars = mean ± SEM (n = …)" etc.

## 11. Effect sizes and reporting
p-values alone are not enough. Report an **effect size** with CI: Cohen's d / Hedges' g
(group means), r/ρ (correlation), odds/risk ratio, hazard ratio, η²/partial-η² (ANOVA).
A figure caption should let the reader judge *how big* the effect is, not just whether
p<0.05.

## 12. p-value hygiene
- Report exact p (e.g. p = 0.013), not "p < 0.05", until very small (then "p < 0.001").
- Significance markers convention (state it): ns, * p<0.05, ** p<0.01, *** p<0.001.
- Don't imply causation from an association.
- State the test, the n, the tails, and any correction for every reported statistic.
- Pre-specified vs exploratory: label exploratory comparisons as such.
- Do not interpret p > 0.05 as proof of no effect or equivalence. Use an equivalence or
  non-inferiority design when that is the scientific question.
- Do not report observed post-hoc power as evidence about a completed result; report the estimate
  and confidence interval precision.
