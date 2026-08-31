# Statistical analysis plan

Write the plan before running inferential analyses. Keep it proportional: a single well-specified
comparison may need one page; a multi-endpoint longitudinal study needs a fuller plan.

## Required decision table

Create one row per research question/outcome with these fields:

| Field | What to state |
|---|---|
| Question/status | Primary, secondary, exploratory, sensitivity |
| Estimand/target | Difference, ratio, coefficient, AUC, risk, prediction error, etc. |
| Variables | Outcome, exposure/group, covariates, time, cluster/subject ID |
| Analysis set/unit | Included units and what counts as independent n |
| Descriptive summary | Mean/SD, median/IQR, n/%, rate/person-time, etc. |
| Main method | Named test/model and parameterization |
| Assumptions | Design and model assumptions that matter |
| Diagnostics | How each check will be assessed |
| Effect/uncertainty | Effect size, interval level, tails |
| Multiplicity | Family of tests and adjustment method |
| Missing data | Rule, analysis n, imputation/model strategy |
| Sensitivity | Pre-specified alternative or robustness check |
| Output | Figure/table and essential annotations |
| Claim boundary | Wording supported if result is positive or null |

Before approval, add a feasibility line: required design cells, independent units/events, outcome
variation, planned parameter count, and whether the proposed effect is identifiable from the
available data.

## Method rationale

Explain every main method twice:

- **Technical rationale:** outcome distribution, dependence, link/function, adjustment, estimand,
  assumptions, and diagnostic plan.
- **Plain-language rationale:** what comparison the method makes and why it respects how the data
  were collected.

Mention plausible alternatives when they encode a genuinely different assumption or estimand.
Do not list every possible test.

## Approval gate

Require an author decision before computation when any of these is unresolved:

- primary outcome/time point or endpoint hierarchy;
- paired versus independent structure;
- analysis unit or cluster ID;
- inclusion/exclusion rule;
- covariate set that materially affects interpretation;
- handling of missing data, censoring, limits of detection, or competing events;
- multiplicity family;
- threshold selected using the same outcome data;
- confirmatory versus exploratory status.
- sparse/empty design cells or insufficient independent units/events for the proposed model.

Record approval, date, plan version, and any deviations. When the user explicitly requests an
exploratory quick look, label it exploratory and avoid converting it into an unqualified
confirmatory claim later.

## Descriptive analysis

Describe the sample before inference. Use summaries that match variable type and distribution.
State denominators for every percentage and n for every model. For baseline tables, do not
automatically treat p-values as a test of successful randomization; emphasize clinically meaningful
imbalance and pre-specified adjustment.

## Multiplicity

Define the family of hypotheses, not merely the correction name. Separate:

- a small set of planned confirmatory comparisons;
- many exploratory outcomes/features;
- post-hoc pairwise tests after an omnibus model;
- repeated subgroup, time-point, or threshold searches.

Use Holm/Bonferroni for controlled small families when appropriate; use false-discovery-rate
methods for discovery-scale testing. Report adjusted values and the family definition.

## Sensitivity and robustness

Choose sensitivity analyses because an assumption or decision is plausible, not because the primary
result is inconvenient. Common examples include:

- complete-case versus principled missing-data handling;
- adjusted versus minimally adjusted model;
- alternative distribution/link or robust standard errors;
- participant-level aggregation versus hierarchical model for replicate data;
- influential observation included versus documented exclusion;
- alternative event/censoring definition;
- continuous predictor versus pre-specified categories;
- internal validation or resampling for prediction.

Label post-hoc analyses and preserve all relevant results.

## Reporting contract

Specify decimal precision, confidence level, exact p-value policy, reference categories, units,
effect direction, model n/events, correction, and error-bar meaning before formatting.

The plan is not proof that the method is valid. After fitting, diagnose the actual model and update
the report with deviations, failures, and limitations.
