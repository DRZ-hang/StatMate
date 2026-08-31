# Data audit and provenance

Audit the data without changing the source. A clean-looking spreadsheet is not evidence that the
analysis unit, coding, or missingness is correct.

## Preserve and identify sources

- Keep source files read-only in practice; write derived files elsewhere.
- Record absolute or project-relative path, sheet/table, byte size, modified time, and SHA-256.
- Identify the data dictionary/version and manuscript/protocol version used.
- Record every join key and expected join cardinality.
- Never overwrite the only copy of source data.

Run `scripts/data_audit.py` on supported CSV/TSV/Excel/flat-JSON files for a first pass. Use
`--visit-column` only for discrete scheduled/repeated visits; use `--duration-column` plus
`--event-column` for survival follow-up. The legacy `--time-column` remains an alias for a visit
column and should not be used for continuous survival duration. Treat identifier flags and type
inference as prompts for review, not proof.

## Structural checks

- row and column count;
- exact and key-based duplicate rows;
- unique counts and constant/near-constant fields;
- inferred type versus declared type;
- impossible or out-of-range values;
- inconsistent categorical coding, capitalization, whitespace, and sentinel values;
- date order and time-window violations;
- group and stratum sizes;
- empty group-by-time/outcome cells and independent-unit/event counts per planned contrast;
- repeated IDs, visit counts, cluster sizes, and unbalanced follow-up;
- join losses, one-to-many explosions, and orphan records.

## Missingness

Report missing count and percentage by variable and relevant group/time point. Distinguish true
missingness from “not applicable,” “not measured,” “below detection,” structural zeros, and censoring.

Never silently replace sentinel codes such as -9, 999, NA, or blank. Map them only with documented
evidence. State the analysis population for each model because different variables can produce
different complete-case n.

Choose deletion, single imputation, multiple imputation, likelihood-based modeling, or another
approach from the missingness mechanism, estimand, and design. A convenience fill with mean/zero is
not a neutral choice. Add a sensitivity analysis when plausible missing-data assumptions matter.

## Outliers and transformations

An extreme value is not automatically an error. First check units, decimal placement, duplication,
measurement limits, and source records. Keep legitimate extremes unless a pre-specified rule says
otherwise.

For every exclusion, winsorization, normalization, log transform, batch correction, or aggregation,
record:

- rule and rationale;
- variables and rows/units affected;
- count before and after;
- whether chosen before viewing outcomes;
- primary and sensitivity results if the choice can affect conclusions.

## Analysis unit and pseudoreplication

Count independent experimental or participant units, not rows. Cells within animals, technical
replicates within samples, bilateral organs, repeated images, fields within slides, and visits
within patients create dependence. Aggregate only when scientifically justified; otherwise model
the hierarchy.

## Estimability and information

Before fitting, verify that each planned contrast has observations in every required design cell,
that the outcome varies, and that the reference categories exist. Count independent units—not rows—
per group and count events for event models. Flag separation, sparse cells, too few clusters,
too few repeated units, more parameters than the data can support, and outcomes with no variation.
Do not treat a model that technically returns coefficients as evidence that it is stable or valid.

## Privacy checks for biomedical data

Flag direct identifiers and likely identifiers: names, medical record numbers, phone/email/address,
government IDs, free-text notes, exact dates, small geographic units, and unusually identifying
combinations. Do not reproduce them in logs, screenshots, plots, or reports. Do not alter/delete
the source without authorization. Prefer coded IDs in derived analysis data.

## Audit output

Create:

1. machine-readable JSON audit;
2. concise Markdown audit;
3. discrepancy/decision table;
4. transformation and exclusion log;
5. source-to-derived lineage entries for the manifest.

Classify findings as:

- **blocking:** method or sample cannot be determined safely;
- **material:** analysis may proceed only after a documented decision;
- **warning:** proceed with explicit caveat or sensitivity check;
- **informational:** useful context with no immediate action.
