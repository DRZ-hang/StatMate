# Chart Selection — data shape × claim → chart type

Pick the chart from two inputs: **the shape of the data** and **the claim the figure must
make** (stage 2's one-sentence job). Never pick by habit. This guide maps common
situations to good defaults and flags the anti-patterns reviewers punish.

## Table of contents
1. Comparing a quantitative outcome across groups
2. Relationship between two quantitative variables
3. Trends over time / ordered x
4. Counts, proportions, compositions
5. Distributions (shape of one variable)
6. Many variables or many samples (high-dimensional)
7. Effect sizes / meta-analysis / subgroups
8. Time-to-event (survival)
9. Diagnostic, prediction, and agreement
10. Tables vs figures
11. Anti-patterns to avoid

---

## 1. Comparing a quantitative outcome across groups
*Claim: "Group A differs from Group B (…)."*

- **Small/medium n (≤ ~50/group): show every point.** Box + jittered points, violin +
  points, or a **raincloud** (half-violin + box + points). Points let the reader see
  spread, outliers, and bimodality that a bar hides.
- **Paired/repeated design:** connect each subject's points across conditions (paired
  slope plot) — the pairing is the whole point.
- **Large n, well-behaved unimodal data:** bar of mean + error bar is acceptable, but a
  box/violin is usually still better. If you use a bar, define the error bar (SD/SEM/CI)
  in the caption.
- **>2 groups:** same chart types; add the omnibus test result and only mark the pairwise
  comparisons you pre-specified or corrected for.

Avoid the "dynamite plot" (bar + single error whisker) as the *only* view when n is small
— it implies a symmetric distribution you haven't shown.

## 2. Relationship between two quantitative variables
*Claim: "X is associated with Y."*

- **Scatter plot.** Add a fit (linear/LOESS) **with a confidence band** if you claim a
  trend. Report the coefficient/r and p, and the model, in the caption.
- Heavy overplotting → use transparency (alpha), hexbin, 2D density, or contours.
- Want marginals too → joint plot (scatter + marginal histograms/KDE).
- Don't extrapolate the fit line beyond the data range.

## 3. Trends over time / ordered x
*Claim: "Y changes over time / dose / position."*

- **Line plot** with a shaded error band (CI or SEM). One line per group.
- **Repeated measures:** faint per-subject "spaghetti" lines + a bold mean line + band.
- Dose-response → consider log x and a fitted curve (e.g. 4-parameter logistic).
- Connect points with lines only when x is ordered/continuous. For categorical x, don't.

## 4. Counts, proportions, compositions
*Claim: "Category frequencies differ" / "composition is X% A, Y% B."*

- Counts across categories → **bar chart** (sorted by value unless order is meaningful).
- Proportions across a grouping → grouped or **100% stacked bar**; show n per group.
- Part-to-whole at one time → stacked bar (avoid pie charts for >3 slices or close values;
  bars are easier to compare). Many parts changing over time → stacked area.
- Two categorical variables → mosaic plot or grouped bars; report the test (χ²/Fisher).

## 5. Distributions (shape of one variable)
*Claim: "Y is distributed like ___ / is skewed / is bimodal."*

- **Histogram** (state bin width/rule) or **ECDF** (no binning choice, great for comparing
  groups) or **KDE/density**. ECDF is underused and very honest.
- Comparing a few distributions → overlaid ECDFs or ridgeline (joyplot) for many groups.

## 6. Many variables or many samples (high-dimensional)
*Claim: "Samples cluster / features co-vary / there's structure."*

- **Heatmap** (z-scored rows) ± hierarchical clustering dendrograms for expression/feature
  matrices. Always show the color scale with units.
- **PCA / UMAP / t-SNE scatter** colored by group for sample structure — state the method
  and parameters; t-SNE/UMAP distances aren't quantitative.
- Correlation among variables → correlation heatmap (annotate r, use a diverging colormap
  centered at 0).

## 7. Effect sizes / meta-analysis / subgroups
*Claim: "Effect is consistent/heterogeneous across studies or subgroups."*

- **Forest plot:** point estimate + CI per study/subgroup, a summary diamond, and a null
  reference line. Include weights and a heterogeneity statistic (I²) for meta-analysis.

## 8. Time-to-event (survival)
*Claim: "Survival/event timing differs between groups."*

- **Kaplan–Meier curves** with a **numbers-at-risk table** underneath and censoring ticks.
  Report the log-rank p and, if modeling, the hazard ratio (CI). Use `lifelines`.

## 9. Diagnostic, prediction, and agreement
- Diagnostic discrimination → ROC or precision-recall when appropriate; show threshold-specific
  sensitivity/specificity when clinical decisions depend on a cutoff. Do not let AUC stand in for
  calibration.
- Predicted risk → calibration plot plus a distribution/risk-stratification view; report validated
  performance rather than training fit.
- Clinical utility → decision curve only when thresholds and net-benefit assumptions are meaningful
  and clearly explained.
- Continuous method agreement → Bland–Altman plot with bias and limits of agreement; correlation
  scatter alone is insufficient.
- Classification agreement → confusion matrix with denominators and class-specific metrics.

## 10. Tables vs figures
Use a **table** when exact values matter and the reader will look them up: sample
characteristics ("Table 1"), full coefficient lists, per-group summary stats, or test
results across many outcomes. Use a **figure** when the *pattern/comparison* is the point.
If you find yourself describing a trend in a 20-row table, it probably wants to be a plot.

Good table craft: one summary statistic style per column (mean ± SD, median [IQR], n (%)),
consistent decimal places, units in the header, n stated, and a footnote defining every
abbreviation and test.

## 11. Anti-patterns to avoid
- **Truncated / non-zero y-axis on bar charts** — exaggerates differences. Bars must start
  at zero; if you need a zoom, use points/box (which don't imply area) and say so.
- **Bar-of-means hiding the distribution** when n is small.
- **Dual y-axes** — easy to mislead; prefer two panels.
- **Rainbow/jet colormaps** — perceptually non-uniform and colorblind-hostile. Use viridis
  family or ColorBrewer; verify with a colorblind simulation.
- **Encoding the only group difference in red/green.**
- **3D bar/pie** — distorts comparison.
- **Pie charts** for anything but a couple of very different slices.
- **Unlabeled axes / undefined error bars / missing n.**
- **Overplotting** that hides density — fix with alpha/jitter/hexbin/2D-density.
