# Biomedical statistical methods

Use this guide only after establishing the design and estimand. It routes common biomedical
questions; it is not an automatic test selector.

## Longitudinal and repeated measurements

- Use paired analyses only for one paired contrast.
- For multiple visits, unequal follow-up, covariate adjustment, or clustered trajectories, prefer a
  mixed-effects model or a suitable generalized mixed model/GEE.
- Include subject-level dependence and justify random-effects/correlation structure.
- Model time as categorical when trajectory shape is not safely assumed; include group-by-time
  interaction when the scientific question concerns differential change.
- Report estimated contrasts with intervals, not only the interaction p-value.

## Clustered, nested, and replicate data

Model sites, families, animals, specimens, batches, wells, fields, or images according to the actual
hierarchy. Technical replicates do not automatically increase biological n. Use participant-level
aggregation only when it matches the estimand and does not discard essential structure.

## Binary, ordinal, count, and rate outcomes

- Binary outcome: logistic/binomial model; report risk or prevalence measures when more
  interpretable, not odds ratios by habit.
- Ordinal outcome: proportional-odds or other ordinal model; check the proportional-odds
  assumption.
- Counts: Poisson only when mean/variance assumptions fit; consider negative binomial,
  zero-inflated/hurdle structures, or robust alternatives when justified.
- Rates: include person-time/exposure as an offset and report rate ratios with intervals.
- Common outcomes: odds ratios may exaggerate intuitive risk differences; provide absolute risk
  when scientifically useful.

## Time-to-event

Define time zero, event, censoring, competing events, and follow-up window. Plot Kaplan–Meier curves
with numbers at risk for simple survival descriptions. Use Cox models for adjusted relative hazards
only after checking proportional hazards. Consider time-varying effects or alternative models when
it fails. For competing risks, distinguish cause-specific hazards from cumulative-incidence
estimands and use the method matching the question.

## Diagnostic accuracy

Define the index test, reference standard, target condition, sampling design, and whether threshold
selection was pre-specified. Report sensitivity and specificity with intervals at meaningful
thresholds; include predictive values only with the relevant prevalence context. Report ROC AUC
with interval, but do not let AUC replace calibration or clinically relevant threshold performance.
Avoid choosing and evaluating a “best” cutoff on the same data without validation.

## Prediction and prognosis

Separate explanation from prediction. Prevent leakage by placing preprocessing, feature selection,
and tuning inside resampling. Prefer internal validation by bootstrap or repeated/nested
cross-validation over a single random split for modest datasets. Report discrimination,
calibration, and clinically relevant error/utility; provide uncertainty. Do not interpret selected
predictor coefficients causally.

## Agreement and method comparison

Correlation is not agreement. For continuous measurements, consider Bland–Altman analysis and
limits of agreement; address repeated measurements if present. For categorical ratings, use an
appropriate kappa/weighted kappa while noting prevalence effects. For reliability, select the ICC
form that matches raters, consistency/absolute agreement, and single/average measurement.

## Repeated tests, omics, and high-dimensional data

Predefine filtering and normalization. Control false discovery rate across the relevant family.
Separate discovery from validation. Treat PCA/UMAP/t-SNE as exploratory structure views; do not
claim formal group separation from a visual alone. Record parameters and seeds.

## Dose-response and laboratory assays

Respect plate, batch, animal, specimen, and technical-replicate structure. For calibration or
dose-response curves, fit a scientifically appropriate response function, inspect residuals and
range, and avoid extrapolation. Handle values below detection limits explicitly rather than
replacing them silently.

## Subgroups

Test interaction when asking whether effects differ between subgroups. A significant result in one
subgroup and a non-significant result in another does not prove subgroup difference. Limit
subgroups, correct or clearly label exploration, and show effect estimates with intervals in a
forest plot.

## Sample-size and power statements

Do not use observed post-hoc power as an interpretation of a completed result. For planning, base
sample size on the primary estimand, plausible effect, variability/event rate, allocation,
clustering/attrition, and chosen error rates. For completed studies, emphasize estimate precision
and interval width.
