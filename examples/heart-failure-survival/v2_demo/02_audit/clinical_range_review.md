# Clinical and structural review checklist

The automated audit is complemented by these design-specific checks in `run_demo.py`:

- expected shape: 299 patients × 13 fields;
- no exact duplicate rows and no missing cells;
- binary coding restricted to 0/1 for anaemia, diabetes, high blood pressure, sex, smoking, and death event;
- positive follow-up time;
- broad plausibility checks: age 18–110 years, ejection fraction 5–90%, serum creatinine 0.1–20 mg/dL, serum sodium 100–180 mEq/L, and positive platelet/CPK values;
- event and censoring counts reconciled against the source papers.

Passing these checks does not prove clinical validity, measurement accuracy, representativeness, or de-identification. It only establishes that the supplied public file is structurally usable for this demo.
