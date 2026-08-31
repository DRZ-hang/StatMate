# Study design map

## Research question

Among adults with advanced heart failure in the supplied 2015 Faisalabad cohort, which baseline clinical features are associated with time to death during observed follow-up, and how much internal predictive discrimination is retained by serum creatinine plus ejection fraction alone?

## Design classification

- Design: single-centre observational follow-up cohort; secondary analysis of a public dataset.
- Analysis unit: one patient per row.
- Time origin: cohort entry as represented in the source dataset.
- Outcome: `DEATH_EVENT` (1 = death during follow-up, 0 = censored).
- Follow-up: `time`, in days.
- Primary estimand: adjusted hazard ratio for death over observed follow-up.
- Secondary descriptive contrast: survival functions across prespecified ejection-fraction categories.
- Exploratory estimand: internal cross-validated discrimination and calibration for two baseline logistic models.

## Prespecified variables

- Main clinical predictors: ejection fraction and serum creatinine.
- Adjustment set: age, serum sodium, anaemia, and high blood pressure.
- Ejection-fraction groups, following the original PLOS ONE analysis: ≤30%, 31–45%, and >45%.
- The exploratory full baseline prediction model uses all 11 baseline variables.
- `time` is never used as a baseline predictor because it is post-baseline follow-up information.

## Claim boundary

This secondary observational analysis can describe associations and internal predictive performance. It cannot establish causality, treatment effects, transportability to other hospitals or populations, or readiness for clinical deployment. No external validation cohort is available.

## Source alignment

- Ahmad et al. (2017) collected the cohort and used Kaplan–Meier and Cox regression.
- Chicco and Jurman (2020) reused the data for machine-learning prediction and highlighted ejection fraction and serum creatinine.
- This demo is a new, code-run analysis designed to exercise the StatMate workflow; it is not a numerical replication of every model in either article.
