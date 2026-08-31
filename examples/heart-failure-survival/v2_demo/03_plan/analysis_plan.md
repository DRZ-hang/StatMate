# Frozen analysis plan

Status: frozen before model execution
Demo seed: `20260816`

## Gate 1 — data readiness

1. Verify 299 rows and 13 expected columns.
2. Confirm one row per patient, no exact duplicate rows, no missing values, and binary coding for the six indicator variables and death event.
3. Check clinically plausible broad ranges without deleting observations solely because they are extreme.
4. Preserve the source CSV unchanged and record its SHA-256 hash.

## Gate 2 — primary survival analysis

### Figure 1: Kaplan–Meier curves

- Groups: ejection fraction ≤30%, 31–45%, >45%.
- Display: survival probability, 95% confidence bands, censoring marks, numbers at risk at 0, 60, 120, 180, and 240 days.
- Overall comparison: multivariable log-rank test.
- Interpretation: unadjusted survival differences only.

### Figure 2 and Table 2: Cox proportional-hazards model

- Covariates, fixed in advance: age (per 10 years), ejection fraction (per 5 percentage points), serum creatinine (per 1 mg/dL), serum sodium (per 5 mEq/L), anaemia, and high blood pressure.
- Report: hazard ratio, 95% confidence interval, two-sided Wald p-value.
- Diagnostics: concordance index and covariate-level Schoenfeld-residual proportional-hazards
  tests. A global test and graphical scaled-Schoenfeld-residual review are explicit author-review
  tasks; until recorded, the Cox asset cannot be promoted automatically to `final`.
- No automated variable selection or data-derived cut points.

## Gate 3 — descriptive table

### Table 1

- Continuous variables: median [Q1, Q3].
- Binary variables: n (%).
- Add standardized mean differences (SMD; Died minus Censored) as descriptive
  magnitude-and-direction summaries. Do not use Table 1 as a hypothesis-test screen and do not use
  these observed-outcome differences to select the Cox model.

## Gate 4 — exploratory prediction

### Figure 3 and model metrics

- Outcome: death observed during the available, variable-length follow-up.
- Models: logistic regression with (a) all 11 baseline variables and (b) serum creatinine plus ejection fraction.
- Explicit leakage control: exclude `time`.
- Processing: standardization inside each training fold.
- Internal validation: repeated stratified 5-fold cross-validation (20 repeats) for AUC and Brier score; a fixed 5-fold out-of-fold pass supplies ROC and calibration curves.
- This analysis is exploratory because the binary endpoint collapses variable follow-up and there is no external validation.

## Multiplicity, missingness, and sensitivity

- No multiplicity-adjusted confirmatory hypothesis family is declared; exact p-values and confidence intervals are shown with descriptive language.
- The public file contains no missing values; therefore no imputation is planned.
- No observations are removed for being statistically extreme.
- If proportional hazards appear materially violated, the affected Cox estimate, its figure/table,
  the report, and the package manifest will be marked `needs-author-decision` rather than silently
  treated as definitive. A time-varying effect, stratified model, RMST-based summary, or another
  scientifically justified sensitivity analysis must be selected before that result can become
  `final`.

## Output contract

- Figures: one immediately viewable PNG plus one vector PDF per figure.
- Tables: reviewed CSV plus three-line DOCX for this public demo. LaTeX/XLSX are intentionally not generated.
- Narrative: result, interpretation, how-to-read guidance, common misreading, and claim boundary for each asset.
- Reproducibility: source hash, code, result files, environment versions, and asset hashes in
  `manifest.json`; run manifest verification after every regeneration.
