#!/usr/bin/env python3
"""Export an approved result table to only the formats requested by the user."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from docx_tables import three_line_table

SUPPORTED = {"docx", "xlsx", "csv", "tex"}


def _safe_stem(stem: str) -> str:
    """Require one filename stem so --outdir remains the sole destination."""
    if not isinstance(stem, str) or not stem.strip():
        raise ValueError("Output stem must be a non-empty filename stem.")
    cleaned = stem.strip()
    if cleaned in {".", ".."} or Path(cleaned).name != cleaned or any(
        separator in cleaned for separator in ("/", "\\")
    ):
        raise ValueError("Output stem must not contain a directory or path traversal.")
    return cleaned


def load_table(path: Path, sheet: str | int = 0) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix in {".tsv", ".txt"}:
        return pd.read_csv(path, sep="\t")
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path, sheet_name=sheet)
    raise ValueError(f"Unsupported input table: {suffix}")


def export_table(
    df: pd.DataFrame,
    outdir: Path,
    stem: str,
    formats: list[str],
    *,
    approved: bool,
    title: str | None = None,
    note: str | None = None,
) -> list[Path]:
    if not approved:
        raise PermissionError(
            "Final table export requires approved=True after content/statistical review."
        )
    stem = _safe_stem(stem)
    if not all(isinstance(fmt, str) for fmt in formats):
        raise ValueError("Every requested format must be a string.")
    requested = [fmt.lower().lstrip(".") for fmt in formats]
    unsupported = sorted(set(requested) - SUPPORTED)
    if unsupported:
        raise ValueError(f"Unsupported formats {unsupported}; choose from {sorted(SUPPORTED)}")
    if not requested:
        raise ValueError("Choose at least one output format.")

    outdir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for fmt in dict.fromkeys(requested):
        path = outdir / f"{stem}.{fmt}"
        if fmt == "docx":
            three_line_table(df, path, title=title, note=note)
        elif fmt == "xlsx":
            df.to_excel(path, index=False)
        elif fmt == "csv":
            df.to_csv(path, index=False, encoding="utf-8-sig")
        elif fmt == "tex":
            path.write_text(
                df.to_latex(index=False, caption=title, label=None, escape=True),
                encoding="utf-8",
            )
        written.append(path)
        print(path)
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Reviewed CSV/TSV/Excel result table")
    parser.add_argument("--sheet", default=0, help="Excel sheet name or zero-based index")
    parser.add_argument("--outdir", type=Path, default=Path("final"))
    parser.add_argument("--stem", help="Output filename stem; defaults to input stem")
    parser.add_argument(
        "--formats",
        nargs="+",
        default=["docx"],
        choices=sorted(SUPPORTED),
        help="Generate only these final formats",
    )
    parser.add_argument("--title")
    parser.add_argument("--note")
    parser.add_argument(
        "--approved",
        action="store_true",
        help="Confirm that statistical content and table structure were reviewed",
    )
    args = parser.parse_args()

    sheet: str | int = args.sheet
    if isinstance(sheet, str) and sheet.isdigit():
        sheet = int(sheet)
    df = load_table(args.input, sheet=sheet)
    export_table(
        df,
        args.outdir,
        args.stem or args.input.stem,
        args.formats,
        approved=args.approved,
        title=args.title,
        note=args.note,
    )


if __name__ == "__main__":
    main()
