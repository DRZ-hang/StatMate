# Study-design intake

Extract the design before proposing a test. Use the manuscript and protocol as evidence; use the
data only to verify implementation. Mark every inferred item as inferred and every unresolved item
as a decision needed.

## Minimum design map

Record:

| Field | Required content |
|---|---|
| Research question | Population, exposure/intervention, comparator, outcome, time horizon |
| Purpose | Descriptive, associational, predictive, diagnostic, prognostic, or causal |
| Design | Randomized, observational cohort, case-control, cross-sectional, laboratory, etc. |
| Sampling/assignment | How units entered groups; randomized/blinded if applicable |
| Analysis population | Inclusion/exclusion and ITT, per-protocol, complete-case, or other set |
| Outcomes | Primary, secondary, exploratory; scale and measurement time |
| Predictors/exposures | Coding, reference level, dose/time structure |
| Covariates | Pre-specified confounders, precision variables, mediators, colliders |
| Analysis unit | One independent participant, animal, specimen, batch, center, etc. |
| Dependence | Pairing, repeated measures, clusters, nests, families, sites, batches |
| Estimand | Difference, ratio, association, odds/risk/hazard ratio, AUC, prediction error, etc. |
| Claim boundary | Strongest wording supported by design |

## Questions that cannot be guessed

Resolve these before formal analysis when relevant:

- What is one independent observation?
- Are measurements paired or repeated on the same unit?
- Were groups assigned, selected, or observed?
- Which outcome and time point are primary?
- Which comparisons were planned before seeing results?
- Which covariates were chosen a priori, and why?
- What do missing values mean?
- Were any participants, wells, fields, images, or batches excluded?
- For longitudinal/survival data, what are time zero, event, censoring, and visit windows?
- For diagnostic studies, what is the reference standard and how were thresholds selected?

## Reconcile manuscript, data dictionary, and data

Create a discrepancy list. Examples:

- manuscript says 120 participants but the file contains 116 unique participant IDs;
- methods describe three visits but a fourth visit code exists;
- outcome units differ between the dictionary and column header;
- technical replicates appear as independent rows;
- randomization or pairing is described but no identifier preserves it.

Do not choose whichever source is convenient. Ask the author to resolve material conflicts and
record the decision.

## Convert aims into analyzable questions

For every aim, write:

1. the scientific question in domain language;
2. the estimand or prediction target;
3. the outcome and its type;
4. the comparison/exposure and reference;
5. the independent unit and dependence structure;
6. the covariate strategy;
7. the time point/window;
8. whether the analysis is confirmatory or exploratory;
9. the maximum defensible conclusion.

Avoid vague aims such as “compare all variables between groups.” Separate primary questions from
supporting descriptions and exploratory discovery.

## Claim boundaries

- **Descriptive:** describe the observed sample; do not generalize beyond the sampling frame without
  justification.
- **Associational:** say “associated with” or “correlated with”; do not imply intervention effects.
- **Predictive:** evaluate out-of-sample performance; coefficients need not be causal.
- **Diagnostic:** report discrimination, calibration, threshold performance, and reference standard.
- **Causal:** require a defensible design and assumptions; name the treatment contrast, time horizon,
  population, and confounding strategy.

## Intake output

Produce a short design map, a data-to-question mapping, a discrepancy list, and a list of only the
decisions that could change the analysis. Do not overwhelm the user with questions already answered
by supplied materials.
