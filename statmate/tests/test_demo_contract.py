from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[2]
DEMO_SCRIPT = (
    REPO
    / "examples"
    / "heart-failure-survival"
    / "v2_demo"
    / "04_code"
    / "run_demo.py"
)
SPEC = importlib.util.spec_from_file_location("statmate_v2_demo", DEMO_SCRIPT)
assert SPEC is not None and SPEC.loader is not None
run_demo = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(run_demo)


def test_zero_variance_smd_is_not_silently_reported_as_no_difference() -> None:
    equal = run_demo.standardized_mean_difference(
        pd.Series([1.0, 1.0]), pd.Series([1.0, 1.0])
    )
    separated = run_demo.standardized_mean_difference(
        pd.Series([1.0, 1.0]), pd.Series([2.0, 2.0])
    )
    binary_separated = run_demo.standardized_mean_difference(
        pd.Series([0, 0]), pd.Series([1, 1]), binary=True
    )
    assert equal == 0.0
    assert separated is None
    assert binary_separated is None
    assert run_demo.format_smd(separated) == "not estimable"


def test_ph_gate_requires_finite_covariate_global_and_graphical_review() -> None:
    clean = pd.DataFrame({"p": [0.2, 0.8]}, index=["age_10y", "ef_5pct"])
    pending = run_demo.assess_ph_diagnostics(clean)
    assert pending["status"] == "needs-author-decision"
    assert any("global" in reason.lower() for reason in pending["review_reasons"])
    assert any("graphical" in reason.lower() for reason in pending["review_reasons"])

    complete = run_demo.assess_ph_diagnostics(
        clean, global_test_p=0.5, graphical_review_completed=True
    )
    assert complete["status"] == "final"
    assert complete["review_reasons"] == []

    nonfinite = run_demo.assess_ph_diagnostics(
        pd.DataFrame({"p": [np.nan]}, index=["ef_5pct"]),
        global_test_p=0.5,
        graphical_review_completed=True,
    )
    assert nonfinite["status"] == "needs-author-decision"
    assert nonfinite["nonfinite_covariates"] == ["ef_5pct"]


def test_demo_table1_is_descriptive_and_has_no_hypothesis_test_column() -> None:
    frame = pd.DataFrame(
        {
            "death_event": [0, 0, 1, 1],
            **{name: [1.0, 2.0, 3.0, 4.0] for name, _ in run_demo.CONTINUOUS},
            **{name: [0, 1, 0, 1] for name, _ in run_demo.BINARY},
        }
    )
    table = run_demo.build_table1(frame)
    assert "SMD (Died − Censored)" in table.columns
    assert not any("p-value" in column.lower() for column in table.columns)
