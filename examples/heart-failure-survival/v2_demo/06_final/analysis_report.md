# Heart-failure v2 statistical handoff

## Executive result

**Package review state: `needs-author-decision`.** This code-run secondary analysis used all 299 patients and 96 observed deaths. Lower baseline ejection fraction and higher serum creatinine were associated with a higher observed mortality hazard after the prespecified adjustment set. The two-feature exploratory classifier retained similar internal discrimination to the 11-feature model, but neither model has external validation and neither is ready for clinical use. Because one prespecified proportional-hazards diagnostic is below 0.05, the constant-HR Cox interpretation requires an author-selected sensitivity strategy before it can be called final.

## Figure 1 — Kaplan–Meier survival

![Kaplan–Meier survival by ejection-fraction group](figures/Fig1.png)

**Result.** The three prespecified ejection-fraction groups had different observed survival functions (overall log-rank p <0.001).

**Visual key.** The orange-red curve is EF ≤30%, the gold curve is EF 31–45%, and the green curve is EF >45%. A downward step marks an observed death; a horizontal segment means that no death was observed between event times. Small plus signs are censored observations, not deaths. Translucent bands are 95% confidence intervals. The color-matched rows below the plot report how many patients remain under observation and event-free immediately before each displayed time.

**Reading path.** First read follow-up days on the horizontal axis and estimated survival probability on the vertical axis. Then compare when the colored curves begin to fall and how far apart they become. Next, judge uncertainty from the shaded bands. Finally, check the numbers at risk before interpreting late curve segments: estimates become unstable when few patients remain.

**Interpretation.** The lower-EF group falls sooner and farther, supporting an unadjusted prognostic association.

**Common misreading.** Separation does not prove that low EF caused death, and the log-rank p-value does not measure effect size.

## Figure 2 and Table 2 — adjusted Cox model

![Adjusted Cox proportional-hazards model](figures/Fig2.png)

**Result.** The model concordance index was 0.730. Ejection fraction HR per 5 percentage points was 0.79 (95% CI 0.72–0.87); serum creatinine HR per 1 mg/dL was 1.36 (95% CI 1.18–1.55).

**Visual key.** Each row is one covariate. The square is its adjusted hazard ratio (HR), and the horizontal whisker is the 95% confidence interval. The vertical dashed line at HR=1 is the no-association reference. Orange symbols indicate p<0.05 in this display; gray symbols do not. Color is a statistical highlighting rule, not a statement of causality or clinical importance. The printed values on the right repeat the HR and interval.

**Reading path.** Locate the square, then read the entire confidence interval before the p-value. Values left of 1 indicate lower hazard and values right of 1 higher hazard, conditional on the adjustment set. The horizontal axis is logarithmic, so equal visual distances represent equal multiplicative changes. Read each row's unit: EF is scaled per +5 percentage points and creatinine per +1 mg/dL. Finally, inspect the PH diagnostic before treating an HR as constant over follow-up.

**Interpretation.** Within this cohort and adjustment set, higher creatinine was associated with higher hazard and higher EF with lower hazard.

**Diagnostic boundary.** Covariate-level PH-test p<0.05 for ejection fraction. A global PH diagnostic has not been completed. Graphical scaled-Schoenfeld-residual review remains an author task.

**Common misreading.** Hazard is not the same as absolute risk, and adjustment does not convert an observational association into a causal effect.

## Figure 3 — exploratory internal prediction

![Cross-validated discrimination and calibration](figures/Fig3.png)

**Result.** Across 100 repeated validation folds, the full model AUC was 0.766 (0.061) and the two-feature model AUC was 0.757 (0.063). The corresponding Brier summaries were 0.177 (0.023) and 0.181 (0.019).

**Visual key.** Blue is the 11-feature baseline model and orange is the two-feature creatinine + EF model in both panels. In panel A, each position along an ROC curve corresponds to a different classification threshold; the gray dashed diagonal is chance-level ranking. In panel B, each colored point represents a quantile group of patients, not an individual patient. Connecting lines are visual guides. The gray dashed diagonal is perfect agreement between mean predicted risk and observed event proportion.

**Reading path.** In panel A, compare how closely the curves approach the upper-left corner and then read AUC in the legend. In panel B, compare the colored points with the identity line: points above it indicate underprediction and points below it overprediction for that risk group. Read the Brier score in the legend; lower values mean smaller overall probability error. Use both panels because discrimination and calibration answer different questions.

**Interpretation.** The simpler model retained similar internal ranking performance, consistent with the source paper's qualitative headline.

**Common misreading.** These are internal estimates for a binary endpoint with unequal follow-up. They do not demonstrate transportability, clinical benefit, a safe decision threshold, or equivalence between models.

## Table 1 — cohort description

Continuous values are median [Q1, Q3]; binary values are n (%). Standardized mean differences
describe the magnitude and direction of observed-group imbalance without using Table 1 as a
hypothesis-test screen.

## Provenance and limits

- Raw CSV SHA-256: `9c73cea7468ff5d517801ec050fe9993da5912fce4b56f296f8df3b38dd75912`
- No rows were created, imputed, or deleted.
- `time` was excluded from baseline prediction to avoid follow-up leakage.
- The demo is a new analysis of the cited public data, not an exact numeric replication of every source-paper model.
