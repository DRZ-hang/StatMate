#!/usr/bin/env python3
"""Create privacy-conscious JSON and Markdown audits for flat research data.

The audit never changes the source and deliberately avoids printing example cell values.
Identifier flags are heuristic prompts for author review, not a de-identification decision.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

_IDENTIFIER_RE = re.compile(
    r"(^|_)(id|name|patient|subject|participant|mrn|email|phone|address|passport|"
    r"ssn|national|dob|birth|note|record)($|_)",
    re.IGNORECASE,
)


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_table(path: Path, sheet: str | int | None = None) -> tuple[pd.DataFrame, str | None]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path), None
    if suffix in {".tsv", ".txt"}:
        return pd.read_csv(path, sep="\t"), None
    if suffix in {".xlsx", ".xls"}:
        selected = 0 if sheet is None else sheet
        return pd.read_excel(path, sheet_name=selected), str(selected)
    if suffix == ".json":
        return pd.read_json(path), None
    raise ValueError(f"Unsupported input format: {suffix}")


def _finite_or_none(value):
    if value is None or pd.isna(value):
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        return float(value) if np.isfinite(value) else None
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    return str(value)


def _column_audit(series: pd.Series, position: int | None = None) -> dict:
    rows = len(series)
    missing = int(series.isna().sum())
    non_missing = rows - missing
    unique = int(series.nunique(dropna=True))
    name = str(series.name)
    item = {
        "name": name,
        "position": position,
        "dtype": str(series.dtype),
        "missing_n": missing,
        "missing_pct": round(100.0 * missing / rows, 3) if rows else 0.0,
        "unique_n": unique,
        "constant": bool(non_missing > 0 and unique <= 1),
        "all_missing": bool(non_missing == 0),
        "suspected_identifier": bool(_IDENTIFIER_RE.search(name)),
    }
    if pd.api.types.is_numeric_dtype(series):
        numeric = pd.to_numeric(series, errors="coerce")
        item["numeric"] = {
            "min": _finite_or_none(numeric.min()),
            "q1": _finite_or_none(numeric.quantile(0.25)),
            "median": _finite_or_none(numeric.median()),
            "q3": _finite_or_none(numeric.quantile(0.75)),
            "max": _finite_or_none(numeric.max()),
            "mean": _finite_or_none(numeric.mean()),
            "sd": _finite_or_none(numeric.std()),
            "zero_n": int((numeric == 0).sum()),
            "negative_n": int((numeric < 0).sum()),
        }
    else:
        text_lengths = series.dropna().astype(str).str.len()
        item["text"] = {
            "max_length": int(text_lengths.max()) if not text_lengths.empty else 0,
            "blank_n": int(series.fillna("").astype(str).str.strip().eq("").sum()),
        }
    return item


def _is_likely_discrete_visit(series: pd.Series) -> bool:
    """Conservatively identify a legacy time column as a discrete visit field.

    ``--time-column`` predates the explicit visit and survival roles.  A high-cardinality
    numeric or text column is therefore treated as continuous/ambiguous instead of being
    expanded into a group-by-time cross-tab.  Users can opt in to discrete handling with
    ``--visit-column``.
    """
    non_missing = series.dropna()
    if non_missing.empty:
        return True
    unique = int(non_missing.nunique(dropna=True))
    if unique <= 1:
        return True
    return unique <= 20 and unique / len(non_missing) <= 0.5


def _finite_numeric(series: pd.Series) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Return parsed numeric values, a finite mask, and a non-numeric mask."""
    numeric = pd.to_numeric(series, errors="coerce")
    supplied = series.notna()
    finite = pd.Series(
        np.isfinite(numeric.to_numpy(dtype=float, na_value=np.nan)),
        index=series.index,
    )
    non_numeric = supplied & numeric.isna()
    return numeric, finite, non_numeric


def _duration_audit(series: pd.Series) -> tuple[dict, pd.Series]:
    numeric, finite, non_numeric = _finite_numeric(series)
    supplied = series.notna()
    non_finite = supplied & numeric.notna() & ~finite
    negative = finite & numeric.lt(0)
    valid = finite & numeric.ge(0)
    finite_values = numeric[finite]
    return (
        {
            "name": str(series.name),
            "missing_n": int(series.isna().sum()),
            "non_missing_n": int(supplied.sum()),
            "non_numeric_n": int(non_numeric.sum()),
            "non_finite_n": int(non_finite.sum()),
            "negative_n": int(negative.sum()),
            "zero_n": int((finite & numeric.eq(0)).sum()),
            "positive_n": int((finite & numeric.gt(0)).sum()),
            "valid_nonnegative_n": int(valid.sum()),
            "min": _finite_or_none(finite_values.min()),
            "max": _finite_or_none(finite_values.max()),
        },
        valid,
    )


def _event_audit(series: pd.Series) -> tuple[dict, pd.Series, pd.Series]:
    numeric, finite, non_numeric = _finite_numeric(series)
    supplied = series.notna()
    non_finite = supplied & numeric.notna() & ~finite
    binary = finite & numeric.isin((0, 1))
    invalid_code = finite & ~numeric.isin((0, 1))
    event = binary & numeric.eq(1)
    return (
        {
            "name": str(series.name),
            "missing_n": int(series.isna().sum()),
            "non_missing_n": int(supplied.sum()),
            "non_numeric_n": int(non_numeric.sum()),
            "non_finite_n": int(non_finite.sum()),
            "invalid_code_n": int(invalid_code.sum()),
            "valid_binary_n": int(binary.sum()),
            "event_n": int(event.sum()),
            "censored_n": int((binary & numeric.eq(0)).sum()),
        },
        binary,
        event,
    )


def audit_dataframe(
    df: pd.DataFrame,
    source: Path,
    sheet: str | None = None,
    id_column: str | None = None,
    group_column: str | None = None,
    time_column: str | None = None,
    visit_column: str | None = None,
    duration_column: str | None = None,
    event_column: str | None = None,
) -> dict:
    audit = {
        "audit_version": 2,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source": {
            "path": source.as_posix(),
            "sheet": sheet,
            "size_bytes": source.stat().st_size,
            "modified_utc": datetime.fromtimestamp(
                source.stat().st_mtime, timezone.utc
            ).isoformat(),
            "sha256": sha256_file(source),
        },
        "shape": {"rows": int(df.shape[0]), "columns": int(df.shape[1])},
        "duplicate_rows_n": int(df.duplicated().sum()),
        "columns": [
            _column_audit(df.iloc[:, position].rename(str(column)), position=position)
            for position, column in enumerate(df.columns)
        ],
        "warnings": [],
    }

    duplicate_names = pd.Index(df.columns)[pd.Index(df.columns).duplicated()].tolist()
    if duplicate_names:
        audit["warnings"].append(
            {"severity": "material", "code": "duplicate_column_names", "columns": duplicate_names}
        )

    identifier_columns = [
        item["name"] for item in audit["columns"] if item["suspected_identifier"]
    ]
    if identifier_columns:
        audit["warnings"].append(
            {
                "severity": "warning",
                "code": "suspected_identifier_columns",
                "columns": identifier_columns,
                "message": "Review before reproducing values in reports or plots.",
            }
        )

    if id_column:
        if id_column not in df.columns:
            audit["warnings"].append(
                {"severity": "blocking", "code": "id_column_missing", "column": id_column}
            )
        else:
            ids = df[id_column]
            audit["id_column"] = {
                "name": id_column,
                "missing_n": int(ids.isna().sum()),
                "unique_n": int(ids.nunique(dropna=True)),
                "repeated_row_n": int(ids.duplicated(keep=False).sum()),
            }

    if group_column and group_column not in df.columns:
        audit["warnings"].append(
            {"severity": "blocking", "code": "group_column_missing", "column": group_column}
        )

    effective_visit: str | None = None
    visit_source: str | None = None
    if visit_column:
        if visit_column not in df.columns:
            audit["warnings"].append(
                {
                    "severity": "blocking",
                    "code": "visit_column_missing",
                    "column": visit_column,
                }
            )
        else:
            effective_visit = visit_column
            visit_source = "visit_column"
        if time_column and time_column != visit_column:
            audit["warnings"].append(
                {
                    "severity": "warning",
                    "code": "legacy_time_column_ignored",
                    "column": time_column,
                    "message": "--visit-column takes precedence over legacy --time-column.",
                }
            )
    elif time_column:
        if time_column not in df.columns:
            audit["warnings"].append(
                {
                    "severity": "blocking",
                    "code": "time_column_missing",
                    "column": time_column,
                }
            )
        else:
            time_series = df[time_column]
            matches_duration = bool(duration_column and time_column == duration_column)
            likely_discrete = (
                False if matches_duration else _is_likely_discrete_visit(time_series)
            )
            audit["legacy_time_column"] = {
                "name": time_column,
                "missing_n": int(time_series.isna().sum()),
                "unique_n": int(time_series.nunique(dropna=True)),
                "treated_as_visit": likely_discrete,
            }
            if likely_discrete:
                effective_visit = time_column
                visit_source = "legacy_time_column"
            elif matches_duration:
                audit["warnings"].append(
                    {
                        "severity": "warning",
                        "code": "legacy_time_column_ignored_for_survival_duration",
                        "column": time_column,
                        "message": (
                            "The same column was explicitly assigned as survival duration and "
                            "was not treated as a discrete visit."
                        ),
                    }
                )
            else:
                audit["warnings"].append(
                    {
                        "severity": "warning",
                        "code": "legacy_time_column_not_treated_as_visit",
                        "column": time_column,
                        "message": (
                            "The legacy time column is high-cardinality and was not cross-tabulated. "
                            "Use --visit-column for discrete visits or --duration-column with "
                            "--event-column for survival follow-up."
                        ),
                    }
                )

    for role, column in (("duration", duration_column), ("event", event_column)):
        if column and column not in df.columns:
            audit["warnings"].append(
                {
                    "severity": "blocking",
                    "code": f"{role}_column_missing",
                    "column": column,
                }
            )

    if bool(duration_column) != bool(event_column):
        audit["warnings"].append(
            {
                "severity": "blocking",
                "code": "survival_role_incomplete",
                "message": "Specify both duration and event columns for a survival endpoint.",
            }
        )
    if duration_column and event_column and duration_column == event_column:
        audit["warnings"].append(
            {
                "severity": "blocking",
                "code": "survival_columns_identical",
                "column": duration_column,
            }
        )
    if visit_column and duration_column and visit_column == duration_column:
        audit["warnings"].append(
            {
                "severity": "blocking",
                "code": "visit_duration_columns_identical",
                "column": visit_column,
                "message": "Discrete visit and continuous survival duration require distinct roles.",
            }
        )

    if group_column in df.columns:
        group_counts = df[group_column].fillna("<missing>").astype(str).value_counts(dropna=False)
        audit["group_counts"] = {str(key): int(value) for key, value in group_counts.items()}

    if effective_visit is not None:
        visits = df[effective_visit]
        audit["visit_column"] = {
            "name": effective_visit,
            "source": visit_source,
            "missing_n": int(visits.isna().sum()),
            "unique_n": int(visits.nunique(dropna=True)),
        }
        visit_counts = visits.fillna("<missing>").astype(str).value_counts(dropna=False)
        audit["visit_counts"] = {
            str(key): int(value) for key, value in visit_counts.items()
        }

    if group_column in df.columns and effective_visit is not None:
        cross = pd.crosstab(df[group_column], df[effective_visit], dropna=False)
        group_visit_counts = {
            str(group): {str(visit): int(count) for visit, count in row.items()}
            for group, row in cross.iterrows()
        }
        audit["group_visit_row_counts"] = group_visit_counts
        if visit_source == "legacy_time_column":
            # Preserve the old result key for consumers of --time-column.
            audit["group_time_row_counts"] = group_visit_counts
        empty_cells = [
            {"group": str(group), "visit": str(visit)}
            for group in cross.index
            for visit in cross.columns
            if int(cross.loc[group, visit]) == 0
        ]
        if empty_cells:
            audit["warnings"].append(
                {
                    "severity": "blocking",
                    "code": (
                        "empty_group_time_cells"
                        if visit_source == "legacy_time_column"
                        else "empty_group_visit_cells"
                    ),
                    "cells": empty_cells,
                    "message": "The intended group-by-visit contrast may not be estimable.",
                }
            )
        if id_column in df.columns:
            unique_cross = pd.crosstab(
                df[group_column],
                df[effective_visit],
                values=df[id_column],
                aggfunc=lambda values: values.nunique(),
                dropna=False,
            ).fillna(0)
            group_visit_units = {
                str(group): {str(visit): int(count) for visit, count in row.items()}
                for group, row in unique_cross.iterrows()
            }
            audit["group_visit_unique_unit_counts"] = group_visit_units
            if visit_source == "legacy_time_column":
                audit["group_time_unique_unit_counts"] = group_visit_units

    survival: dict = {}
    duration_valid: pd.Series | None = None
    event_valid: pd.Series | None = None
    event_observed: pd.Series | None = None
    if duration_column in df.columns:
        duration_summary, duration_valid = _duration_audit(df[duration_column])
        survival["duration"] = duration_summary
        for code, severity, count_key in (
            ("missing_duration_values", "material", "missing_n"),
            ("non_numeric_duration_values", "blocking", "non_numeric_n"),
            ("non_finite_duration_values", "blocking", "non_finite_n"),
            ("negative_duration_values", "blocking", "negative_n"),
            ("zero_duration_values", "warning", "zero_n"),
        ):
            count = duration_summary[count_key]
            if count:
                audit["warnings"].append(
                    {
                        "severity": severity,
                        "code": code,
                        "column": duration_column,
                        "n": count,
                    }
                )

    if event_column in df.columns:
        event_summary, event_valid, event_observed = _event_audit(df[event_column])
        survival["event"] = event_summary
        for code, severity, count_key in (
            ("missing_event_values", "material", "missing_n"),
            ("non_numeric_event_values", "blocking", "non_numeric_n"),
            ("non_finite_event_values", "blocking", "non_finite_n"),
            ("invalid_event_codes", "blocking", "invalid_code_n"),
        ):
            count = event_summary[count_key]
            if count:
                audit["warnings"].append(
                    {
                        "severity": severity,
                        "code": code,
                        "column": event_column,
                        "n": count,
                    }
                )
        if event_summary["valid_binary_n"] and event_summary["event_n"] == 0:
            audit["warnings"].append(
                {
                    "severity": "blocking",
                    "code": "no_observed_events",
                    "column": event_column,
                }
            )
        if event_summary["valid_binary_n"] and event_summary["censored_n"] == 0:
            audit["warnings"].append(
                {
                    "severity": "warning",
                    "code": "no_censored_observations",
                    "column": event_column,
                }
            )

    if duration_valid is not None and event_valid is not None and event_observed is not None:
        valid_pair = duration_valid & event_valid
        paired_counts = {
            "valid_pair_n": int(valid_pair.sum()),
            "excluded_pair_n": int((~valid_pair).sum()),
            "event_n": int((valid_pair & event_observed).sum()),
            "censored_n": int((valid_pair & ~event_observed).sum()),
        }
        survival["paired_counts"] = paired_counts
        if paired_counts["valid_pair_n"] == 0:
            audit["warnings"].append(
                {
                    "severity": "blocking",
                    "code": "no_valid_survival_pairs",
                    "message": "No row has both a valid duration and a valid event indicator.",
                }
            )
        elif paired_counts["event_n"] == 0:
            audit["warnings"].append(
                {
                    "severity": "blocking",
                    "code": "no_observed_events_in_valid_survival_pairs",
                    "message": (
                        "Valid duration/event pairs contain no observed events; the requested "
                        "survival effect is not estimable."
                    ),
                }
            )
        if paired_counts["valid_pair_n"] and paired_counts["censored_n"] == 0:
            audit["warnings"].append(
                {
                    "severity": "warning",
                    "code": "no_censored_observations_in_valid_survival_pairs",
                    "message": "Valid duration/event pairs contain no censored observations.",
                }
            )
    if survival:
        audit["survival"] = survival

    return audit


def audit_to_markdown(audit: dict) -> str:
    source = audit["source"]
    shape = audit["shape"]
    lines = [
        "# Data audit",
        "",
        f"- Source: {source['path']}",
        f"- Sheet: {source['sheet'] if source['sheet'] is not None else 'n/a'}",
        f"- SHA-256: {source['sha256']}",
        f"- Shape: {shape['rows']} rows × {shape['columns']} columns",
        f"- Exact duplicate rows: {audit['duplicate_rows_n']}",
        "",
        "## Columns",
        "",
        "| Column | dtype | Missing | Unique | Constant | Identifier flag |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for item in audit["columns"]:
        lines.append(
            f"| {item['name']} | {item['dtype']} | "
            f"{item['missing_n']} ({item['missing_pct']:.3f}%) | {item['unique_n']} | "
            f"{'yes' if item['constant'] else 'no'} | "
            f"{'review' if item['suspected_identifier'] else 'no'} |"
        )

    if "visit_column" in audit:
        visit = audit["visit_column"]
        lines.extend(
            [
                "",
                "## Visit role",
                "",
                f"- Column: {visit['name']}",
                f"- Source: {visit['source']}",
                f"- Distinct visits: {visit['unique_n']}",
                f"- Missing visits: {visit['missing_n']}",
            ]
        )

    if "survival" in audit:
        survival = audit["survival"]
        lines.extend(["", "## Survival roles", ""])
        if "duration" in survival:
            duration = survival["duration"]
            lines.append(
                f"- Duration `{duration['name']}`: {duration['valid_nonnegative_n']} valid "
                f"non-negative values; {duration['missing_n']} missing; "
                f"{duration['negative_n']} negative; {duration['non_numeric_n']} non-numeric."
            )
        if "event" in survival:
            event = survival["event"]
            lines.append(
                f"- Event `{event['name']}`: {event['event_n']} events; "
                f"{event['censored_n']} censored; {event['missing_n']} missing; "
                f"{event['invalid_code_n']} invalid binary codes."
            )
        if "paired_counts" in survival:
            paired = survival["paired_counts"]
            lines.append(
                f"- Valid duration/event pairs: {paired['valid_pair_n']}; "
                f"excluded pairs: {paired['excluded_pair_n']}."
            )

    lines.extend(["", "## Findings", ""])
    if audit["warnings"]:
        for warning in audit["warnings"]:
            detail = warning.get("columns") or warning.get("column") or warning.get("message", "")
            lines.append(
                f"- **{warning['severity']}** — {warning['code']}: {detail}"
            )
    else:
        lines.append("- No automated structural warnings. Design-specific review is still required.")
    lines.extend(
        [
            "",
            "> This automated audit does not establish the analysis unit, validate clinical ranges,",
            "> define missingness, or prove de-identification. Reconcile it with the protocol and",
            "> data dictionary before analysis.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--sheet", help="Excel sheet name or zero-based index")
    parser.add_argument("--id-column", help="Optional participant/experimental-unit ID column")
    parser.add_argument("--group-column", help="Optional treatment/exposure/group column")
    parser.add_argument(
        "--visit-column",
        help="Optional discrete visit/time-point column for repeated-measures checks",
    )
    parser.add_argument(
        "--duration-column",
        help="Optional non-negative survival follow-up/duration column; use with --event-column",
    )
    parser.add_argument(
        "--event-column",
        help="Optional binary survival event column coded 0=censored and 1=event",
    )
    parser.add_argument(
        "--time-column",
        help=(
            "Legacy visit/time option. Low-cardinality fields are treated as visits; "
            "prefer --visit-column or --duration-column."
        ),
    )
    parser.add_argument("--outdir", type=Path, default=Path("audit"))
    parser.add_argument("--prefix", help="Output stem; defaults to the input file stem")
    args = parser.parse_args()

    sheet: str | int | None = args.sheet
    if isinstance(sheet, str) and sheet.isdigit():
        sheet = int(sheet)
    df, loaded_sheet = load_table(args.input, sheet=sheet)
    audit = audit_dataframe(
        df,
        args.input,
        sheet=loaded_sheet,
        id_column=args.id_column,
        group_column=args.group_column,
        time_column=args.time_column,
        visit_column=args.visit_column,
        duration_column=args.duration_column,
        event_column=args.event_column,
    )

    args.outdir.mkdir(parents=True, exist_ok=True)
    stem = args.prefix or args.input.stem
    json_path = args.outdir / f"{stem}_audit.json"
    md_path = args.outdir / f"{stem}_audit.md"
    json_path.write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(audit_to_markdown(audit), encoding="utf-8")
    print(json_path)
    print(md_path)


if __name__ == "__main__":
    main()
