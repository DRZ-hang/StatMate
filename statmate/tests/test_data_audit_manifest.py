from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import analysis_manifest  # noqa: E402
import data_audit  # noqa: E402


def _source_file(tmp_path: Path, df: pd.DataFrame, name: str = "source.csv") -> Path:
    source = tmp_path / name
    df.to_csv(source, index=False)
    return source


def _warning_codes(audit: dict) -> set[str]:
    return {warning["code"] for warning in audit["warnings"]}


def test_explicit_visit_role_builds_discrete_cross_tabs(tmp_path: Path) -> None:
    df = pd.DataFrame(
        {
            "unit_id": ["a1", "a1", "a2", "a2", "b1", "b1", "b2", "b2"],
            "group": ["A", "A", "A", "A", "B", "B", "B", "B"],
            "visit": ["baseline", "week4"] * 4,
        }
    )
    audit = data_audit.audit_dataframe(
        df,
        _source_file(tmp_path, df),
        id_column="unit_id",
        group_column="group",
        visit_column="visit",
    )

    assert audit["visit_column"] == {
        "name": "visit",
        "source": "visit_column",
        "missing_n": 0,
        "unique_n": 2,
    }
    assert audit["group_visit_row_counts"]["A"] == {"baseline": 2, "week4": 2}
    assert audit["group_visit_unique_unit_counts"]["B"] == {
        "baseline": 2,
        "week4": 2,
    }
    assert "empty_group_visit_cells" not in _warning_codes(audit)


def test_legacy_high_cardinality_time_is_not_cross_tabulated(tmp_path: Path) -> None:
    df = pd.DataFrame(
        {
            "group": ["A"] * 6 + ["B"] * 6,
            "followup_days": list(range(1, 13)),
        }
    )
    audit = data_audit.audit_dataframe(
        df,
        _source_file(tmp_path, df),
        group_column="group",
        time_column="followup_days",
    )

    assert audit["legacy_time_column"]["treated_as_visit"] is False
    assert "group_time_row_counts" not in audit
    assert "group_visit_row_counts" not in audit
    codes = _warning_codes(audit)
    assert "legacy_time_column_not_treated_as_visit" in codes
    assert "empty_group_time_cells" not in codes


def test_legacy_low_cardinality_time_keeps_compatible_outputs(tmp_path: Path) -> None:
    df = pd.DataFrame(
        {
            "group": ["A", "A", "B", "B"],
            "time": [0, 1, 0, 1],
        }
    )
    audit = data_audit.audit_dataframe(
        df,
        _source_file(tmp_path, df),
        group_column="group",
        time_column="time",
    )

    assert audit["legacy_time_column"]["treated_as_visit"] is True
    assert audit["group_time_row_counts"] == audit["group_visit_row_counts"]
    assert audit["visit_column"]["source"] == "legacy_time_column"


def test_survival_roles_report_validity_and_paired_counts(tmp_path: Path) -> None:
    df = pd.DataFrame(
        {
            "duration": [10, 0, -2, None, "bad", np.inf, 5, 7],
            "event": [1, 0, 1, None, 2, np.inf, "bad", 0],
        }
    )
    audit = data_audit.audit_dataframe(
        df,
        _source_file(tmp_path, df),
        time_column="duration",
        duration_column="duration",
        event_column="event",
    )

    duration = audit["survival"]["duration"]
    assert duration["valid_nonnegative_n"] == 4
    assert duration["missing_n"] == 1
    assert duration["non_numeric_n"] == 1
    assert duration["non_finite_n"] == 1
    assert duration["negative_n"] == 1
    assert duration["zero_n"] == 1

    event = audit["survival"]["event"]
    assert event["valid_binary_n"] == 4
    assert event["event_n"] == 2
    assert event["censored_n"] == 2
    assert event["missing_n"] == 1
    assert event["non_numeric_n"] == 1
    assert event["non_finite_n"] == 1
    assert event["invalid_code_n"] == 1

    assert audit["survival"]["paired_counts"] == {
        "valid_pair_n": 3,
        "excluded_pair_n": 5,
        "event_n": 1,
        "censored_n": 2,
    }
    assert "visit_column" not in audit
    codes = _warning_codes(audit)
    assert {
        "legacy_time_column_ignored_for_survival_duration",
        "negative_duration_values",
        "non_numeric_duration_values",
        "non_finite_duration_values",
        "invalid_event_codes",
        "non_numeric_event_values",
        "non_finite_event_values",
    } <= codes
    markdown = data_audit.audit_to_markdown(audit)
    assert "Valid duration/event pairs: 3" in markdown


def test_survival_pair_gate_uses_jointly_valid_rows(tmp_path: Path) -> None:
    no_joint_events = pd.DataFrame(
        {
            "duration": [1, 2, -1],
            "event": [0, 0, 1],
        }
    )
    audit = data_audit.audit_dataframe(
        no_joint_events,
        _source_file(tmp_path, no_joint_events, "no-joint-events.csv"),
        duration_column="duration",
        event_column="event",
    )
    assert audit["survival"]["paired_counts"]["event_n"] == 0
    assert "no_observed_events_in_valid_survival_pairs" in _warning_codes(audit)

    no_pairs = pd.DataFrame({"duration": [None, "bad"], "event": [1, 0]})
    empty = data_audit.audit_dataframe(
        no_pairs,
        _source_file(tmp_path, no_pairs, "no-pairs.csv"),
        duration_column="duration",
        event_column="event",
    )
    assert empty["survival"]["paired_counts"]["valid_pair_n"] == 0
    assert "no_valid_survival_pairs" in _warning_codes(empty)


def test_data_audit_cli_keeps_legacy_time_and_accepts_survival_roles(
    tmp_path: Path,
) -> None:
    df = pd.DataFrame(
        {
            "group": ["A", "A", "B", "B"],
            "visit": [0, 1, 0, 1],
            "duration": [2, 4, 3, 5],
            "event": [0, 1, 1, 0],
        }
    )
    source = _source_file(tmp_path, df)
    outdir = tmp_path / "audit"
    script = SCRIPT_DIR / "data_audit.py"
    completed = subprocess.run(
        [
            sys.executable,
            str(script),
            str(source),
            "--group-column",
            "group",
            "--time-column",
            "visit",
            "--duration-column",
            "duration",
            "--event-column",
            "event",
            "--outdir",
            str(outdir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    audit = json.loads((outdir / "source_audit.json").read_text(encoding="utf-8"))
    assert audit["legacy_time_column"]["treated_as_visit"] is True
    assert audit["group_time_row_counts"] == audit["group_visit_row_counts"]
    assert audit["survival"]["paired_counts"]["valid_pair_n"] == 4


def test_manifest_base_is_relative_to_manifest_and_verify_detects_changes(
    tmp_path: Path,
) -> None:
    base = tmp_path / "analysis"
    base.mkdir()
    result = base / "result.csv"
    result.write_bytes(b"abc")
    manifest_path = tmp_path / "handoff" / "manifest.json"
    manifest_path.parent.mkdir()

    manifest = analysis_manifest.build_manifest(
        base,
        {"results": [result]},
        status="draft",
        manifest_path=manifest_path,
    )
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    expected_base = Path(os.path.relpath(base.resolve(), manifest_path.parent.resolve())).as_posix()
    assert manifest["base_directory"] == expected_base
    assert analysis_manifest.resolve_base_directory(manifest_path, manifest) == base.resolve()

    verified = analysis_manifest.verify_manifest(manifest_path)
    assert verified["ok"] is True
    assert verified["summary"] == {
        "total": 1,
        "ok": 1,
        "missing": 0,
        "size_mismatch": 0,
        "sha256_mismatch": 0,
        "invalid_entry": 0,
    }

    result.write_bytes(b"xyz")
    changed = analysis_manifest.verify_manifest(manifest_path)
    assert changed["ok"] is False
    assert changed["summary"]["size_mismatch"] == 0
    assert changed["summary"]["sha256_mismatch"] == 1

    result.unlink()
    missing = analysis_manifest.verify_manifest(manifest_path)
    assert missing["summary"]["missing"] == 1


def test_manifest_text_metrics_are_stable_across_line_endings_and_detect_edits(
    tmp_path: Path,
) -> None:
    base = tmp_path / "analysis"
    base.mkdir()
    result = base / "result.csv"
    result.write_bytes(b"name,value\nalpha,1\nbeta,2\n")
    manifest_path = tmp_path / "manifest.json"

    manifest = analysis_manifest.build_manifest(
        base,
        {"results": [result]},
        status="draft",
        manifest_path=manifest_path,
    )
    entry = manifest["files"]["results"][0]
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    assert manifest["manifest_version"] == 3
    assert entry["size_mode"] == analysis_manifest.TEXT_LF_MODE
    assert entry["hash_mode"] == analysis_manifest.TEXT_LF_MODE
    assert entry["size_bytes"] == len(b"name,value\nalpha,1\nbeta,2\n")

    result.write_bytes(b"name,value\r\nalpha,1\r\nbeta,2\r\n")
    crlf = analysis_manifest.verify_manifest(manifest_path)
    assert crlf["ok"] is True
    assert crlf["summary"]["ok"] == 1

    result.write_bytes(b"name,value\ralpha,1\rbeta,2\r")
    cr_only = analysis_manifest.verify_manifest(manifest_path)
    assert cr_only["ok"] is True

    result.write_bytes(b"name,value\r\nalpha,1\r\nbeta,3\r\n")
    changed = analysis_manifest.verify_manifest(manifest_path)
    assert changed["ok"] is False
    assert changed["summary"]["size_mismatch"] == 0
    assert changed["summary"]["sha256_mismatch"] == 1


def test_manifest_binary_metrics_remain_raw_and_byte_exact(tmp_path: Path) -> None:
    base = tmp_path / "analysis"
    base.mkdir()
    asset = base / "asset.bin"
    asset.write_bytes(b"a\nb\n")
    manifest_path = tmp_path / "manifest.json"

    manifest = analysis_manifest.build_manifest(
        base,
        {"assets": [asset]},
        status="draft",
        manifest_path=manifest_path,
    )
    entry = manifest["files"]["assets"][0]
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    assert entry["size_mode"] == analysis_manifest.RAW_BYTES_MODE
    assert entry["hash_mode"] == analysis_manifest.RAW_BYTES_MODE
    assert entry["size_bytes"] == 4

    asset.write_bytes(b"a\r\nb\r\n")
    changed = analysis_manifest.verify_manifest(manifest_path)
    assert changed["ok"] is False
    assert changed["summary"]["size_mismatch"] == 1
    assert changed["summary"]["sha256_mismatch"] == 1


def test_manifest_entries_without_modes_keep_legacy_raw_verification(
    tmp_path: Path,
) -> None:
    base = tmp_path / "analysis"
    base.mkdir()
    result = base / "legacy.txt"
    result.write_bytes(b"a\nb\n")
    manifest_path = tmp_path / "manifest.json"

    manifest = analysis_manifest.build_manifest(
        base,
        {"results": [result]},
        status="draft",
        manifest_path=manifest_path,
    )
    manifest["manifest_version"] = 2
    entry = manifest["files"]["results"][0]
    entry["size_bytes"] = result.stat().st_size
    entry["sha256"] = analysis_manifest.sha256_file(result)
    entry.pop("size_mode")
    entry.pop("hash_mode")
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    unchanged = analysis_manifest.verify_manifest(manifest_path)
    assert unchanged["ok"] is True
    assert unchanged["files"][0]["size_mode"] == analysis_manifest.RAW_BYTES_MODE
    assert unchanged["files"][0]["hash_mode"] == analysis_manifest.RAW_BYTES_MODE

    result.write_bytes(b"a\r\nb\r\n")
    changed = analysis_manifest.verify_manifest(manifest_path)
    assert changed["ok"] is False
    assert changed["summary"]["size_mismatch"] == 1
    assert changed["summary"]["sha256_mismatch"] == 1


def test_text_metric_normalization_handles_chunk_boundary_crlf(tmp_path: Path) -> None:
    text = tmp_path / "boundary.txt"
    text.write_bytes(b"a\r\nb\r\nc\r")

    size, digest = analysis_manifest.file_metrics(
        text,
        mode=analysis_manifest.TEXT_LF_MODE,
        chunk_size=2,
    )
    canonical = b"a\nb\nc\n"
    assert size == len(canonical)
    assert digest == hashlib.sha256(canonical).hexdigest()


def test_manifest_cli_supports_legacy_build_and_verify_subcommand(tmp_path: Path) -> None:
    base = tmp_path / "analysis"
    base.mkdir()
    source = base / "source.csv"
    source.write_text("x\n1\n", encoding="utf-8")
    manifest_path = tmp_path / "package" / "manifest.json"
    script = SCRIPT_DIR / "analysis_manifest.py"

    built = subprocess.run(
        [
            sys.executable,
            str(script),
            "--base",
            str(base),
            "--input",
            str(source),
            "--output",
            str(manifest_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert built.returncode == 0, built.stderr
    assert manifest_path.is_file()

    verified = subprocess.run(
        [sys.executable, str(script), "verify", str(manifest_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert verified.returncode == 0, verified.stderr
    assert json.loads(verified.stdout)["ok"] is True
