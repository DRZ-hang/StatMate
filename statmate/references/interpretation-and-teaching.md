# Interpretation and teaching

Write two separate layers for every figure and table. The first helps an author state the result
correctly; the second teaches a non-statistician how to inspect the display.

## Scientific interpretation

Use this order:

1. **What was estimated:** groups/variables, time point, analysis population, model.
2. **Direction and magnitude:** effect estimate in original or interpretable units.
3. **Uncertainty:** confidence interval and, when relevant, exact p-value or adjusted p/q-value.
4. **Data pattern:** overlap, spread, heterogeneity, nonlinearity, outliers, events, or calibration.
5. **Robustness:** diagnostics and sensitivity analyses that agree or disagree.
6. **Scientific relevance:** distinguish statistical evidence from clinical/biological importance.
7. **Boundary:** state design limitations, multiplicity, missingness, residual confounding,
   measurement error, model dependence, or limited precision.
8. **Manuscript wording:** provide a cautious result sentence that includes estimate and interval.

Do not say:

- “no difference” solely because p is above a threshold;
- “the groups are equivalent” without an equivalence/non-inferiority design;
- “X causes Y” from an observational association;
- “clinically important” without a justified threshold/context;
- “perfect prediction” from training-set performance;
- “trend” as a substitute for a non-significant result without a defined trend analysis.

## How to read a figure

Teach in a fixed reading order:

1. Read the title/caption to identify the question and population.
2. Read axes, units, scales, transformations, and group encodings.
3. Identify what each mark represents: participant, specimen, mean, median, model estimate, event,
   censoring mark, or fitted value.
4. Inspect raw distribution or trajectory before summary/error bars.
5. Compare effect size and interval with a meaningful reference/null line.
6. Read n, missingness, test/model, correction, and sensitivity notes.
7. State the pattern in one sentence, then state what cannot be concluded.

Explain display-specific elements:

- **scatter/strip:** each point and possible overplotting/jitter;
- **box:** median, quartiles, whisker rule, and points beyond whiskers;
- **violin/density:** width represents estimated density, not sample size unless scaled so;
- **error bar/band:** SD, SEM, CI, prediction interval, or model uncertainty—name it;
- **regression line:** fitted association within the observed range; band definition;
- **forest plot:** estimate, confidence interval, weight if present, and null/reference line;
- **Kaplan–Meier:** step-down events, censor marks, numbers at risk, and late-curve uncertainty;
- **heatmap:** row/column meaning, normalization, clustering, and color scale;
- **ROC/calibration:** discrimination versus calibration; thresholds and prevalence context.

## How to read a table

Teach the reader to:

1. read title, analysis population, and footnotes;
2. identify denominator and summary convention for each column;
3. compare raw group summaries before the inferential column;
4. read the effect estimate and confidence interval before p-value;
5. confirm reference group, units, adjustment set, model n/events, and multiplicity;
6. distinguish unadjusted, adjusted, primary, exploratory, and sensitivity results;
7. note missing denominators and rows that use different samples.

## Required per-item teaching block

For each asset provide:

- **Purpose:** the question this item answers;
- **Elements:** what every axis/row/column/mark/symbol means;
- **Reading path:** 3–6 ordered steps specific to this item;
- **Observed result:** data-grounded pattern and numerical estimate;
- **Common misreading:** at least one likely error;
- **Takeaway:** one plain-language sentence;
- **Cannot conclude:** one explicit boundary when relevant.

Keep the teaching block concrete to the actual data and display. Do not paste generic textbook
definitions that fail to explain the user's figure.
