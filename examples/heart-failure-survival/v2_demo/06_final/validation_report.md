# Validation report

Automated check status: **PASS**
Scientific review state: **needs-author-decision**

A technical PASS does not override an unresolved statistical diagnostic.

## Automated checks

- PASS — exists:06_final/figures/Fig1.png
- PASS — exists:06_final/figures/Fig1.pdf
- PASS — exists:06_final/figures/Fig2.png
- PASS — exists:06_final/figures/Fig2.pdf
- PASS — exists:06_final/figures/Fig3.png
- PASS — exists:06_final/figures/Fig3.pdf
- PASS — exists:06_final/tables/Table1.csv
- PASS — exists:06_final/tables/Table1.docx
- PASS — exists:06_final/tables/Table2.csv
- PASS — exists:06_final/tables/Table2.docx
- PASS — exists:06_final/analysis_report.md
- PASS — exists:06_final/Heart_Failure_v2_Report.docx
- PASS — png_canvas_and_dpi:Fig1.png (4251×2763 px; 179.96×116.97 mm; 600.00 dpi)
- PASS — png_canvas_and_dpi:Fig2.png (4251×2636 px; 179.96×111.59 mm; 600.00 dpi)
- PASS — png_canvas_and_dpi:Fig3.png (4251×2211 px; 179.96×93.60 mm; 600.00 dpi)
- PASS — source_shape_299x13
- PASS — no_missing_cells
- PASS — no_duplicate_rows
- PASS — prediction_excludes_followup_time ({'All 11 baseline features': ['age', 'ejection_fraction', 'serum_creatinine', 'serum_sodium', 'platelets', 'creatinine_phosphokinase', 'sex', 'anaemia', 'diabetes', 'high_blood_pressure', 'smoking'], 'Creatinine + ejection fraction': ['serum_creatinine', 'ejection_fraction']})
- PASS — cox_fit_completed_and_finite
- PASS — cox_covariate_ph_tests_finite ([])
- PASS — review_state_matches_ph_gate

## Limitations

- Single-centre, small observational cohort.
- No external validation cohort.
- Binary exploratory prediction collapses unequal follow-up.
- Automated checks do not establish clinical correctness or causal validity.
