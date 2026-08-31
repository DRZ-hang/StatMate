# Data audit

- Source: examples/heart-failure-survival/data/heart_failure_clinical_records.csv
- Sheet: n/a
- SHA-256: 9c73cea7468ff5d517801ec050fe9993da5912fce4b56f296f8df3b38dd75912
- Shape: 299 rows × 13 columns
- Exact duplicate rows: 0

## Columns

| Column | dtype | Missing | Unique | Constant | Identifier flag |
|---|---:|---:|---:|---:|---:|
| age | float64 | 0 (0.000%) | 47 | no | no |
| anaemia | int64 | 0 (0.000%) | 2 | no | no |
| creatinine_phosphokinase | int64 | 0 (0.000%) | 208 | no | no |
| diabetes | int64 | 0 (0.000%) | 2 | no | no |
| ejection_fraction | int64 | 0 (0.000%) | 17 | no | no |
| high_blood_pressure | int64 | 0 (0.000%) | 2 | no | no |
| platelets | float64 | 0 (0.000%) | 176 | no | no |
| serum_creatinine | float64 | 0 (0.000%) | 40 | no | no |
| serum_sodium | int64 | 0 (0.000%) | 27 | no | no |
| sex | int64 | 0 (0.000%) | 2 | no | no |
| smoking | int64 | 0 (0.000%) | 2 | no | no |
| time | int64 | 0 (0.000%) | 148 | no | no |
| DEATH_EVENT | int64 | 0 (0.000%) | 2 | no | no |

## Findings

- No automated structural warnings. Design-specific review is still required.

> This automated audit does not establish the analysis unit, validate clinical ranges,
> define missingness, or prove de-identification. Reconcile it with the protocol and
> data dictionary before analysis.
