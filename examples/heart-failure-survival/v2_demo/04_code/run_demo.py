#!/usr/bin/env python3
"""Run the StatMate heart-failure demonstration from the public raw CSV.

The script performs structural validation, freezes all modelling choices in code,
creates real result tables, exports PNG/PDF figure pairs, writes three-line Word
tables, and assembles an English interpretation/teaching report.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from lifelines import CoxPHFitter, KaplanMeierFitter
from lifelines.statistics import multivariate_logrank_test, proportional_hazard_test
from sklearn.calibration import calibration_curve
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score, roc_curve
from sklearn.model_selection import RepeatedStratifiedKFold, StratifiedKFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

HERE = Path(__file__).resolve().parent
DEMO = HERE.parent
EXAMPLE = DEMO.parent
REPO = EXAMPLE.parents[1]
SKILL_SCRIPTS = REPO / "statmate" / "scripts"
sys.path.insert(0, str(SKILL_SCRIPTS))

from docx_tables import three_line_table  # noqa: E402
from analysis_manifest import build_manifest, verify_manifest  # noqa: E402
from figstyle import (  # noqa: E402
    apply_preset,
    get_preset,
    save_figure,
    validate_png_export,
)
from report_docx import build_report  # noqa: E402

SEED = 20260816
DATA = EXAMPLE / "data" / "heart_failure_clinical_records.csv"
RESULTS = DEMO / "05_results"
FINAL = DEMO / "06_final"
FIGURES = FINAL / "figures"
TABLES = FINAL / "tables"
MANIFEST = FINAL / "manifest.json"

FIGURE_ASPECTS = {"Fig1": 0.65, "Fig2": 0.62, "Fig3": 0.52}
FIGURE_PRESET = "generic"
FIGURE_COLUMN = "double"

CONTINUOUS = [
    ("age", "Age, years"),
    ("ejection_fraction", "Ejection fraction, %"),
    ("serum_creatinine", "Serum creatinine, mg/dL"),
    ("serum_sodium", "Serum sodium, mEq/L"),
    ("platelets", "Platelets, ×10³/µL"),
    ("creatinine_phosphokinase", "Creatine phosphokinase, mcg/L"),
]
BINARY = [
    ("sex", "Male sex"),
    ("anaemia", "Anaemia"),
    ("diabetes", "Diabetes"),
    ("high_blood_pressure", "High blood pressure"),
    ("smoking", "Current smoking"),
]
EXPECTED = [
    "age", "anaemia", "creatinine_phosphokinase", "diabetes",
    "ejection_fraction", "high_blood_pressure", "platelets",
    "serum_creatinine", "serum_sodium", "sex", "smoking", "time",
    "DEATH_EVENT",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def json_ready(value):
    if isinstance(value, dict):
        return {str(k): json_ready(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_ready(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, (np.floating,)):
        return None if not np.isfinite(value) else float(value)
    return value


def portable_manifest_verification(verification: dict) -> dict:
    """Return a commit-safe verification snapshot without machine-local paths."""
    portable = json_ready(verification)
    portable["manifest"] = MANIFEST.relative_to(DEMO).as_posix()
    portable["base_directory"] = "."
    for item in portable.get("files", []):
        item["package_path"] = item.get("path", "")
        item.pop("resolved_path", None)
    return portable


def format_p(p: float) -> str:
    if p < 0.001:
        return "<0.001"
    return f"{p:.3f}"


def standardized_mean_difference(
    censored: pd.Series,
    died: pd.Series,
    *,
    binary: bool = False,
) -> float | None:
    """Return Died-minus-Censored SMD, or None when pooled variation is zero.

    Equal constants have zero standardized difference. Different constants have
    no finite standardization denominator and must not be mislabeled as SMD=0.
    """
    if binary:
        p0, p1 = float(censored.mean()), float(died.mean())
        difference = p1 - p0
        denominator = math.sqrt((p0 * (1 - p0) + p1 * (1 - p1)) / 2.0)
    else:
        difference = float(died.mean() - censored.mean())
        denominator = math.sqrt((censored.var(ddof=1) + died.var(ddof=1)) / 2.0)
    if not np.isfinite(denominator) or denominator == 0:
        return 0.0 if difference == 0 else None
    return difference / denominator


def format_smd(value: float | None) -> str:
    return "not estimable" if value is None else f"{value:+.2f}"


def assess_ph_diagnostics(
    ph: pd.DataFrame,
    *,
    global_test_p: float | None = None,
    graphical_review_completed: bool = False,
) -> dict:
    """Convert proportional-hazards diagnostics into an explicit review gate."""
    labels = {
        "age_10y": "age",
        "ef_5pct": "ejection fraction",
        "creatinine_1": "serum creatinine",
        "sodium_5": "serum sodium",
        "anaemia": "anaemia",
        "high_blood_pressure": "high blood pressure",
    }
    values = pd.to_numeric(ph["p"], errors="coerce")
    finite = pd.Series(np.isfinite(values.to_numpy(dtype=float)), index=values.index)
    flagged = [str(name) for name in values.index[finite & values.lt(0.05)]]
    nonfinite = [str(name) for name in values.index[~finite]]
    reasons = []
    if flagged:
        reasons.append(
            "Covariate-level PH-test p<0.05 for "
            + ", ".join(labels.get(name, name) for name in flagged)
            + "."
        )
    if nonfinite:
        reasons.append(
            "Non-finite covariate-level PH-test result for "
            + ", ".join(labels.get(name, name) for name in nonfinite)
            + "."
        )
    if global_test_p is None or not np.isfinite(global_test_p):
        reasons.append("A global PH diagnostic has not been completed.")
    elif global_test_p < 0.05:
        reasons.append(f"Global PH-test p={global_test_p:.3f}.")
    if not graphical_review_completed:
        reasons.append("Graphical scaled-Schoenfeld-residual review remains an author task.")
    return {
        "status": "needs-author-decision" if reasons else "final",
        "covariate_test_p": {str(key): float(value) if np.isfinite(value) else None for key, value in values.items()},
        "flagged_covariates": flagged,
        "nonfinite_covariates": nonfinite,
        "global_test_p": global_test_p,
        "graphical_review_completed": graphical_review_completed,
        "review_reasons": reasons,
    }


def load_and_validate() -> tuple[pd.DataFrame, dict]:
    raw = pd.read_csv(DATA)
    checks = {
        "source_sha256": sha256(DATA),
        "shape": list(raw.shape),
        "expected_columns_exact": list(raw.columns) == EXPECTED,
        "duplicate_rows_n": int(raw.duplicated().sum()),
        "missing_cells_n": int(raw.isna().sum().sum()),
    }
    if raw.shape != (299, 13) or not checks["expected_columns_exact"]:
        raise ValueError(f"Unexpected source schema: {raw.shape}, {list(raw.columns)}")
    if checks["duplicate_rows_n"] or checks["missing_cells_n"]:
        raise ValueError("Source contains duplicates or missing cells; stop for author review.")

    for column in ["anaemia", "diabetes", "high_blood_pressure", "sex", "smoking", "DEATH_EVENT"]:
        values = set(raw[column].unique())
        checks[f"{column}_binary"] = values <= {0, 1}
        if not checks[f"{column}_binary"]:
            raise ValueError(f"{column} is not binary: {values}")

    ranges = {
        "age": raw["age"].between(18, 110).all(),
        "ejection_fraction": raw["ejection_fraction"].between(5, 90).all(),
        "serum_creatinine": raw["serum_creatinine"].between(0.1, 20).all(),
        "serum_sodium": raw["serum_sodium"].between(100, 180).all(),
        "platelets": raw["platelets"].gt(0).all(),
        "creatinine_phosphokinase": raw["creatinine_phosphokinase"].gt(0).all(),
        "time": raw["time"].gt(0).all(),
    }
    checks["broad_range_checks"] = {k: bool(v) for k, v in ranges.items()}
    if not all(ranges.values()):
        raise ValueError("A broad clinical-range check failed; stop for author review.")

    df = raw.rename(columns={"DEATH_EVENT": "death_event"}).copy()
    df["platelets"] = df["platelets"] / 1000.0
    df["outcome"] = np.where(df["death_event"].eq(1), "Died", "Censored")
    df["ef_group"] = pd.cut(
        df["ejection_fraction"],
        bins=[-np.inf, 30, 45, np.inf],
        labels=["≤30%", "31–45%", ">45%"],
        right=True,
    )
    checks.update({
        "patients_n": len(df),
        "deaths_n": int(df["death_event"].sum()),
        "censored_n": int((1 - df["death_event"]).sum()),
        "follow_up_median_days": float(df["time"].median()),
        "follow_up_range_days": [int(df["time"].min()), int(df["time"].max())],
        "ef_group_counts": df["ef_group"].value_counts(sort=False).to_dict(),
    })
    return df, checks


def build_table1(df: pd.DataFrame) -> pd.DataFrame:
    """Describe observed-outcome groups without turning Table 1 into a test screen."""

    rows = []
    groups = [df, df[df.death_event.eq(0)], df[df.death_event.eq(1)]]
    for variable, label in CONTINUOUS:
        values = []
        for group in groups:
            q = group[variable].quantile([0.25, 0.5, 0.75])
            values.append(f"{q.loc[0.5]:.1f} [{q.loc[0.25]:.1f}, {q.loc[0.75]:.1f}]")
        smd = standardized_mean_difference(groups[1][variable], groups[2][variable])
        rows.append([label, *values, format_smd(smd)])

    for variable, label in BINARY:
        values = [f"{int(g[variable].sum())} ({100*g[variable].mean():.1f}%)" for g in groups]
        smd = standardized_mean_difference(
            groups[1][variable], groups[2][variable], binary=True
        )
        rows.append([label, *values, format_smd(smd)])

    return pd.DataFrame(
        rows,
        columns=["Characteristic", f"Overall (n={len(df)})", f"Censored (n={(df.death_event==0).sum()})", f"Died (n={df.death_event.sum()})", "SMD (Died − Censored)"],
    )


def fit_cox(df: pd.DataFrame) -> tuple[CoxPHFitter, pd.DataFrame, pd.DataFrame]:
    model = pd.DataFrame({
        "time": df["time"],
        "death_event": df["death_event"],
        "age_10y": df["age"] / 10.0,
        "ef_5pct": df["ejection_fraction"] / 5.0,
        "creatinine_1": df["serum_creatinine"],
        "sodium_5": df["serum_sodium"] / 5.0,
        "anaemia": df["anaemia"],
        "high_blood_pressure": df["high_blood_pressure"],
    })
    cph = CoxPHFitter()
    cph.fit(model, duration_col="time", event_col="death_event")
    ph = proportional_hazard_test(cph, model, time_transform="rank").summary
    labels = {
        "age_10y": "Age, per 10 years",
        "ef_5pct": "Ejection fraction, per 5%",
        "creatinine_1": "Serum creatinine, per 1 mg/dL",
        "sodium_5": "Serum sodium, per 5 mEq/L",
        "anaemia": "Anaemia, yes vs no",
        "high_blood_pressure": "High blood pressure, yes vs no",
    }
    order = list(labels)
    summary = cph.summary.loc[order]
    table = pd.DataFrame({
        "Covariate": [labels[x] for x in order],
        "Hazard ratio": np.exp(summary["coef"]).map(lambda x: f"{x:.2f}"),
        "95% CI": [f"{math.exp(lo):.2f}–{math.exp(hi):.2f}" for lo, hi in zip(summary["coef lower 95%"], summary["coef upper 95%"])],
        "p-value": summary["p"].map(format_p),
        "PH-test p": ph.loc[order, "p"].map(format_p).values,
    })
    return cph, table, ph


def plot_km(df: pd.DataFrame) -> tuple[float, dict]:
    apply_preset(FIGURE_PRESET, column=FIGURE_COLUMN, aspect=FIGURE_ASPECTS["Fig1"])
    palette = get_preset(FIGURE_PRESET)["palette_colors"]
    colors = [palette[6], palette[1], palette[3]]
    fig = plt.figure(layout="constrained")
    gs = fig.add_gridspec(2, 1, height_ratios=[4.2, 1.15])
    ax = fig.add_subplot(gs[0])
    risk_ax = fig.add_subplot(gs[1], sharex=ax)
    groups = ["≤30%", "31–45%", ">45%"]
    times = np.array([0, 60, 120, 180, 240])
    risks = {}
    for label, color in zip(groups, colors):
        sub = df[df.ef_group.astype(str).eq(label)]
        km = KaplanMeierFitter(label=f"EF {label} (n={len(sub)})")
        km.fit(sub.time, event_observed=sub.death_event)
        km.plot_survival_function(ax=ax, ci_show=True, ci_alpha=0.12, show_censors=True, censor_styles={"ms": 3}, color=color, linewidth=1.6)
        risks[label] = [int((sub.time >= t).sum()) for t in times]

    logrank = multivariate_logrank_test(df.time, df.ef_group, df.death_event)
    # Reserve real canvas space before day 0 so row labels cannot collide with the first count.
    ax.set(xlabel="", ylabel="Survival probability", xlim=(-20, 285), ylim=(0, 1.02))
    ax.set_title(f"Survival by baseline ejection fraction · log-rank p {format_p(logrank.p_value)}", loc="left")
    ax.legend(frameon=False, loc="lower left", ncol=1)
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.5)
    ax.tick_params(labelbottom=False)

    risk_ax.set_ylim(-0.6, 2.7)
    risk_ax.set_xlim(-20, 285)
    risk_ax.set_yticks([2, 1, 0], labels=[f"EF {g}" for g in groups])
    risk_ax.set_xticks(times)
    risk_ax.set_xlabel("Follow-up (days)")
    risk_ax.set_title("Number at risk", loc="left", fontsize=8)
    for y, label, color in zip([2, 1, 0], groups, colors):
        for x, n in zip(times, risks[label]):
            risk_ax.text(x, y, str(n), ha="center", va="center", color=color, fontsize=7)
    risk_ax.set_yticklabels([f"EF {g}" for g in groups], fontsize=7)
    risk_ax.spines[["top", "right", "left"]].set_visible(False)
    risk_ax.tick_params(axis="y", length=0)
    save_figure(fig, "1", preset=FIGURE_PRESET, outdir=str(FIGURES), kind="line")
    plt.close(fig)
    return float(logrank.p_value), risks


def plot_cox(cph: CoxPHFitter, ph: pd.DataFrame) -> None:
    apply_preset(FIGURE_PRESET, column=FIGURE_COLUMN, aspect=FIGURE_ASPECTS["Fig2"])
    palette = get_preset(FIGURE_PRESET)["palette_colors"]
    labels = {
        "age_10y": "Age (per 10 years)",
        "ef_5pct": "Ejection fraction (per 5%)",
        "creatinine_1": "Serum creatinine (per 1 mg/dL)",
        "sodium_5": "Serum sodium (per 5 mEq/L)",
        "anaemia": "Anaemia (yes vs no)",
        "high_blood_pressure": "High blood pressure (yes vs no)",
    }
    order = list(labels)
    s = cph.summary.loc[order]
    hr = np.exp(s["coef"]).to_numpy()
    lo = np.exp(s["coef lower 95%"]).to_numpy()
    hi = np.exp(s["coef upper 95%"]).to_numpy()
    y = np.arange(len(order))[::-1]
    fig, ax = plt.subplots()
    for yi, estimate, lower, upper, p in zip(y, hr, lo, hi, s["p"]):
        color = palette[6] if p < 0.05 else "#777777"
        ax.errorbar(estimate, yi, xerr=[[estimate-lower], [upper-estimate]], fmt="s", color=color, capsize=2.5, markersize=5)
        ax.text(8.7, yi, f"{estimate:.2f} [{lower:.2f}, {upper:.2f}]", va="center", fontsize=7.5)
    ax.axvline(1, color="#777777", linestyle="--", linewidth=0.8)
    ax.set_xscale("log")
    ax.set_xlim(0.35, 15)
    ax.set_xticks([0.5, 1, 2, 4, 8], labels=["0.5", "1", "2", "4", "8"])
    ax.set_yticks(y, labels=[labels[x] for x in order])
    ax.set_xlabel("Adjusted hazard ratio (95% CI; log scale)")
    flagged = int((ph["p"] < 0.05).sum())
    ax.set_title(f"Prespecified Cox model · C-index {cph.concordance_index_:.2f} · PH flags {flagged}/6", loc="left")
    ax.grid(axis="x", color="#D9D9D9", linewidth=0.5)
    save_figure(fig, "2", preset=FIGURE_PRESET, outdir=str(FIGURES), kind="line")
    plt.close(fig)


def prediction_analysis(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    all_features = [c for c, _ in CONTINUOUS] + [c for c, _ in BINARY]
    feature_sets = {
        "All 11 baseline features": all_features,
        "Creatinine + ejection fraction": ["serum_creatinine", "ejection_fraction"],
    }
    y = df.death_event.to_numpy()
    repeated = RepeatedStratifiedKFold(n_splits=5, n_repeats=20, random_state=SEED)
    fold_metrics = []
    splits = list(repeated.split(df, y))
    for model_name, features in feature_sets.items():
        X = df[features].to_numpy()
        for fold, (train, test) in enumerate(splits, 1):
            model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, random_state=SEED))
            model.fit(X[train], y[train])
            p = model.predict_proba(X[test])[:, 1]
            fold_metrics.append({
                "Model": model_name,
                "Fold": fold,
                "AUC": roc_auc_score(y[test], p),
                "Brier score": brier_score_loss(y[test], p),
            })
    fold_df = pd.DataFrame(fold_metrics)
    summary_rows = []
    for model_name, group in fold_df.groupby("Model", sort=False):
        summary_rows.append({
            "Model": model_name,
            "AUC, mean (SD)": f"{group['AUC'].mean():.3f} ({group['AUC'].std():.3f})",
            "Brier, mean (SD)": f"{group['Brier score'].mean():.3f} ({group['Brier score'].std():.3f})",
            "Repeated folds": len(group),
        })
    summary = pd.DataFrame(summary_rows)

    fixed_cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    oof = {}
    for model_name, features in feature_sets.items():
        model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, random_state=SEED))
        oof[model_name] = cross_val_predict(model, df[features].to_numpy(), y, cv=fixed_cv, method="predict_proba")[:, 1]

    apply_preset(FIGURE_PRESET, column=FIGURE_COLUMN, aspect=FIGURE_ASPECTS["Fig3"])
    palette = get_preset(FIGURE_PRESET)["palette_colors"]
    fig, axes = plt.subplots(1, 2)
    colors = [palette[5], palette[6]]
    metrics = {}
    for (model_name, probs), color in zip(oof.items(), colors):
        fpr, tpr, _ = roc_curve(y, probs)
        auc = roc_auc_score(y, probs)
        brier = brier_score_loss(y, probs)
        metrics[model_name] = {"fixed_5fold_auc": auc, "fixed_5fold_brier": brier}
        axes[0].plot(fpr, tpr, color=color, linewidth=1.5, label=f"{model_name}\nAUC {auc:.2f}")
        obs, pred = calibration_curve(y, probs, n_bins=6, strategy="quantile")
        axes[1].plot(pred, obs, marker="o", markersize=4, color=color, linewidth=1.3, label=f"{model_name}\nBrier {brier:.2f}")
    axes[0].plot([0, 1], [0, 1], "--", color="#888888", linewidth=0.7)
    axes[0].set(xlabel="False-positive rate", ylabel="True-positive rate", xlim=(0, 1), ylim=(0, 1.02), title="A  Discrimination")
    axes[1].plot([0, 1], [0, 1], "--", color="#888888", linewidth=0.7)
    axes[1].set(xlabel="Mean predicted risk", ylabel="Observed event proportion", xlim=(0, 0.85), ylim=(0, 0.85), title="B  Calibration")
    axes[0].legend(frameon=False, fontsize=6.5, loc="lower right")
    # The lowest-risk calibration point sits in the upper-left; keep the legend
    # in the empty lower-right region so it never hides observed data.
    axes[1].legend(frameon=False, fontsize=6.5, loc="lower right")
    for ax in axes:
        ax.grid(color="#E1E1E1", linewidth=0.45)
    fig.suptitle("Exploratory internal validation · baseline variables only · 5-fold out-of-fold", x=0.02, ha="left", fontsize=9)
    save_figure(fig, "3", preset=FIGURE_PRESET, outdir=str(FIGURES), kind="line")
    plt.close(fig)
    return summary, {
        "fold_metrics": fold_df.to_dict(orient="records"),
        "fixed_oof": metrics,
        "feature_sets": feature_sets,
    }


def write_markdown_report(results: dict) -> Path:
    cox = results["cox"]
    pred = results["prediction"]
    text = f"""# Heart-failure v2 statistical handoff

## Executive result

**Package review state: `{results['overall_status']}`.** This code-run secondary analysis used all {results['validation']['patients_n']} patients and {results['validation']['deaths_n']} observed deaths. Lower baseline ejection fraction and higher serum creatinine were associated with a higher observed mortality hazard after the prespecified adjustment set. The two-feature exploratory classifier retained similar internal discrimination to the 11-feature model, but neither model has external validation and neither is ready for clinical use. Because one prespecified proportional-hazards diagnostic is below 0.05, the constant-HR Cox interpretation requires an author-selected sensitivity strategy before it can be called final.

## Figure 1 — Kaplan–Meier survival

![Kaplan–Meier survival by ejection-fraction group](figures/Fig1.png)

**Result.** The three prespecified ejection-fraction groups had different observed survival functions (overall log-rank p {format_p(results['logrank_p'])}).

**Visual key.** The orange-red curve is EF ≤30%, the gold curve is EF 31–45%, and the green curve is EF >45%. A downward step marks an observed death; a horizontal segment means that no death was observed between event times. Small plus signs are censored observations, not deaths. Translucent bands are 95% confidence intervals. The color-matched rows below the plot report how many patients remain under observation and event-free immediately before each displayed time.

**Reading path.** First read follow-up days on the horizontal axis and estimated survival probability on the vertical axis. Then compare when the colored curves begin to fall and how far apart they become. Next, judge uncertainty from the shaded bands. Finally, check the numbers at risk before interpreting late curve segments: estimates become unstable when few patients remain.

**Interpretation.** The lower-EF group falls sooner and farther, supporting an unadjusted prognostic association.

**Common misreading.** Separation does not prove that low EF caused death, and the log-rank p-value does not measure effect size.

## Figure 2 and Table 2 — adjusted Cox model

![Adjusted Cox proportional-hazards model](figures/Fig2.png)

**Result.** The model concordance index was {cox['c_index']:.3f}. Ejection fraction HR per 5 percentage points was {cox['ef_hr']:.2f} (95% CI {cox['ef_lo']:.2f}–{cox['ef_hi']:.2f}); serum creatinine HR per 1 mg/dL was {cox['cr_hr']:.2f} (95% CI {cox['cr_lo']:.2f}–{cox['cr_hi']:.2f}).

**Visual key.** Each row is one covariate. The square is its adjusted hazard ratio (HR), and the horizontal whisker is the 95% confidence interval. The vertical dashed line at HR=1 is the no-association reference. Orange symbols indicate p<0.05 in this display; gray symbols do not. Color is a statistical highlighting rule, not a statement of causality or clinical importance. The printed values on the right repeat the HR and interval.

**Reading path.** Locate the square, then read the entire confidence interval before the p-value. Values left of 1 indicate lower hazard and values right of 1 higher hazard, conditional on the adjustment set. The horizontal axis is logarithmic, so equal visual distances represent equal multiplicative changes. Read each row's unit: EF is scaled per +5 percentage points and creatinine per +1 mg/dL. Finally, inspect the PH diagnostic before treating an HR as constant over follow-up.

**Interpretation.** Within this cohort and adjustment set, higher creatinine was associated with higher hazard and higher EF with lower hazard.

**Diagnostic boundary.** {cox['ph_message']}

**Common misreading.** Hazard is not the same as absolute risk, and adjustment does not convert an observational association into a causal effect.

## Figure 3 — exploratory internal prediction

![Cross-validated discrimination and calibration](figures/Fig3.png)

**Result.** Across 100 repeated validation folds, the full model AUC was {pred['full_auc']} and the two-feature model AUC was {pred['two_auc']}. The corresponding Brier summaries were {pred['full_brier']} and {pred['two_brier']}.

**Visual key.** Blue is the 11-feature baseline model and orange is the two-feature creatinine + EF model in both panels. In panel A, each position along an ROC curve corresponds to a different classification threshold; the gray dashed diagonal is chance-level ranking. In panel B, each colored point represents a quantile group of patients, not an individual patient. Connecting lines are visual guides. The gray dashed diagonal is perfect agreement between mean predicted risk and observed event proportion.

**Reading path.** In panel A, compare how closely the curves approach the upper-left corner and then read AUC in the legend. In panel B, compare the colored points with the identity line: points above it indicate underprediction and points below it overprediction for that risk group. Read the Brier score in the legend; lower values mean smaller overall probability error. Use both panels because discrimination and calibration answer different questions.

**Interpretation.** The simpler model retained similar internal ranking performance, consistent with the source paper's qualitative headline.

**Common misreading.** These are internal estimates for a binary endpoint with unequal follow-up. They do not demonstrate transportability, clinical benefit, a safe decision threshold, or equivalence between models.

## Table 1 — cohort description

Continuous values are median [Q1, Q3]; binary values are n (%). Standardized mean differences
describe the magnitude and direction of observed-group imbalance without using Table 1 as a
hypothesis-test screen.

## Provenance and limits

- Raw CSV SHA-256: `{results['validation']['source_sha256']}`
- No rows were created, imputed, or deleted.
- `time` was excluded from baseline prediction to avoid follow-up leakage.
- The demo is a new analysis of the cited public data, not an exact numeric replication of every source-paper model.
"""
    path = FINAL / "analysis_report.md"
    path.write_text(text, encoding="utf-8")
    return path


def build_word_report(results: dict) -> Path:
    cox = results["cox"]
    pred = results["prediction"]
    cox_status = results["overall_status"]
    items = [
        {
            "kind": "figure", "number": "1", "title": {"en": "Kaplan–Meier survival", "zh": "Kaplan–Meier 生存曲线"},
            "image": "06_final/figures/Fig1.png", "width_in": 4.7, "image_after_caption": True, "page_break_before": True, "status": "final",
            "claim": {"en": "Observed survival differs across prespecified ejection-fraction groups.", "zh": "预设射血分数组别的观察生存曲线存在差异。"},
            "method_rationale": {"en": "Time-to-event outcome with censoring requires Kaplan–Meier estimation; the overall log-rank test compares the three curves.", "zh": "结局包含随访时间与删失，采用 Kaplan–Meier 估计；整体 log-rank 检验比较三条曲线。"},
            "result": {"en": f"Overall log-rank p {format_p(results['logrank_p'])}.", "zh": f"整体 log-rank p {format_p(results['logrank_p'])}。"},
            "interpretation": {"en": "Lower baseline EF is associated with poorer observed survival.", "zh": "较低的基线 EF 与较差的观察生存相关。"},
            "how_to_read": {"en": [
                "Axes — follow-up days are on the horizontal axis; the vertical axis is the estimated probability of remaining alive.",
                "Colors — orange-red is EF ≤30%, gold is EF 31–45%, and green is EF >45%.",
                "Steps and lines — each downward step is an observed death; a horizontal segment means no death was observed between event times.",
                "Plus signs — these are censored patients, not deaths; follow-up ended without a recorded death at that time.",
                "Shaded bands — these are 95% confidence intervals around each survival estimate.",
                "Numbers at risk — the color-matched rows show how many patients remain under observation and event-free just before each time point.",
                "Reading order — compare when curves fall, how far they separate, how wide the bands are, and how many patients remain at risk.",
                "Late follow-up — treat tail separation cautiously when the risk rows contain only a few patients.",
            ], "zh": []},
            "common_misreading": {"en": "Curve separation is not causal evidence.", "zh": "曲线分离并不构成因果证据。"},
            "cannot_conclude": {"en": "A treatment effect or a clinically optimal EF threshold.", "zh": "不能据此得出治疗效应或临床最佳 EF 阈值。"},
            "caption": {"en": "Kaplan–Meier survival by prespecified baseline ejection-fraction group, with 95% confidence bands, censoring marks, and numbers at risk.", "zh": "按预设基线射血分数组别绘制的 Kaplan–Meier 生存曲线，含 95% 置信带、删失标记和风险人数。"},
            "citation": "Results — survival analysis", "repro": "v2_demo/04_code/run_demo.py",
        },
        {
            "kind": "figure", "number": "2", "title": {"en": "Adjusted Cox model", "zh": "校正后的 Cox 模型"},
            "image": "06_final/figures/Fig2.png", "width_in": 4.7, "image_after_caption": True, "page_break_before": True, "status": cox_status,
            "claim": {"en": "EF and serum creatinine retain prognostic associations after prespecified adjustment.", "zh": "在预设校正后，EF 与血清肌酐仍保持预后关联。"},
            "method_rationale": {"en": "Cox regression estimates covariate-adjusted hazard ratios while retaining censoring information.", "zh": "Cox 回归在保留删失信息的同时估计协变量校正后的风险比。"},
            "result": {"en": f"C-index {cox['c_index']:.2f}; EF HR {cox['ef_hr']:.2f}; creatinine HR {cox['cr_hr']:.2f}.", "zh": f"C-index {cox['c_index']:.2f}；EF HR {cox['ef_hr']:.2f}；肌酐 HR {cox['cr_hr']:.2f}。"},
            "interpretation": {"en": "Higher EF is associated with lower hazard; higher creatinine with higher hazard.", "zh": "较高 EF 与较低风险相关，较高肌酐与较高风险相关。"},
            "how_to_read": {"en": [
                "Rows — each row is one covariate in the same adjusted Cox model.",
                "Squares — the square marks the adjusted hazard ratio (HR); the horizontal whisker is its 95% confidence interval.",
                "Dashed line — HR=1 is the no-association reference. Intervals crossing 1 are compatible with no association at the 0.05 level.",
                "Direction — estimates left of 1 indicate lower hazard and estimates right of 1 higher hazard, conditional on the adjustment set.",
                "Scale — the horizontal axis is logarithmic, so equal distances represent equal multiplicative changes rather than equal absolute changes.",
                "Colors — orange denotes p<0.05 in this figure and gray denotes p≥0.05; color does not establish causality or clinical importance.",
                "Units — EF is reported per +5 percentage points and creatinine per +1 mg/dL; other rows use the unit printed in the label.",
                "Diagnostics — read the C-index as model discrimination and inspect the PH flag before assuming an HR is constant over follow-up.",
            ], "zh": []},
            "common_misreading": {"en": "A hazard ratio is not an absolute risk ratio.", "zh": "风险比并不等于绝对风险比。"},
            "cannot_conclude": {"en": "Causality, treatment benefit, or external validity.", "zh": "不能据此得出因果关系、治疗获益或外部有效性。"},
            "caption": {"en": "Prespecified multivariable Cox model. Continuous effects use clinically interpretable increments; horizontal lines are 95% confidence intervals.", "zh": "预设多变量 Cox 模型。连续变量按临床可解释增量报告，横线为 95% 置信区间。"},
            "citation": "Results — adjusted associations", "repro": "v2_demo/04_code/run_demo.py",
        },
        {
            "kind": "figure", "number": "3", "title": {"en": "Exploratory internal prediction", "zh": "探索性内部预测"},
            "image": "06_final/figures/Fig3.png", "width_in": 4.7, "image_after_caption": True, "page_break_before": True, "status": "final",
            "claim": {"en": "The two-feature model retains similar internal discrimination to the full baseline model.", "zh": "双变量模型保留了与完整基线模型相近的内部区分度。"},
            "method_rationale": {"en": "Out-of-fold probabilities avoid evaluating each patient with a model trained on that patient; follow-up time is excluded.", "zh": "折外预测避免用包含该患者的训练模型评价该患者，并排除随访时间。"},
            "result": {"en": f"Repeated-CV AUC: full {pred['full_auc']}; two-feature {pred['two_auc']}.", "zh": f"重复交叉验证 AUC：完整模型 {pred['full_auc']}；双变量模型 {pred['two_auc']}。"},
            "interpretation": {"en": "The compact model may be useful for hypothesis generation, not deployment.", "zh": "精简模型可用于提出假设，但不能直接部署。"},
            "how_to_read": {"en": [
                "Colors — blue is the full 11-feature model and orange is the two-feature creatinine + EF model in both panels.",
                "ROC panel — false-positive rate is on the horizontal axis and true-positive rate on the vertical axis; each curve position corresponds to a different threshold.",
                "ROC reference — the gray dashed diagonal is chance-level ranking; curves nearer the upper-left discriminate outcomes better.",
                "AUC — read the value in the legend as an overall ranking summary, not as accuracy at a selected threshold.",
                "Calibration points — each point is a quantile group of patients, not one patient; connecting lines are visual guides only.",
                "Calibration reference — the gray dashed identity line is perfect agreement. Points above it indicate underprediction and points below it overprediction for that group.",
                "Brier score — read the value in the legend as overall probability error; lower is better.",
                "Reading order — assess ROC discrimination and calibration separately, then compare both models without declaring equivalence from similar curves.",
            ], "zh": []},
            "common_misreading": {"en": "Similar AUC is not proof of model equivalence.", "zh": "AUC 相近并不能证明模型等效。"},
            "cannot_conclude": {"en": "Transportability, net clinical benefit, or a safe decision threshold.", "zh": "不能据此得出可迁移性、临床净获益或安全决策阈值。"},
            "caption": {"en": "Five-fold out-of-fold ROC and quantile-binned calibration for baseline logistic models. This secondary endpoint ignores unequal follow-up and is exploratory.", "zh": "基线逻辑回归模型的五折折外 ROC 与分位数分箱校准。本二分类终点忽略不等随访，属于探索性分析。"},
            "citation": "Results — exploratory prediction", "repro": "v2_demo/04_code/run_demo.py",
        },
        {
            "kind": "table", "number": "1", "title": {"en": "Cohort characteristics", "zh": "队列特征"},
            "csv": "06_final/tables/Table1.csv", "status": "final", "page_break_before": True,
            "table_title": {"en": "Table 1. Baseline characteristics by observed outcome", "zh": "表 1. 按观察结局分组的基线特征"},
            "table_note": {"en": "Continuous: median [Q1, Q3]; binary: n (%). SMD direction is Died minus Censored.", "zh": "连续变量：中位数 [Q1, Q3]；二分类变量：n (%)。SMD 方向为死亡组减删失组。"},
            "claim": {"en": "The table describes, rather than balances, outcome groups.", "zh": "该表用于描述结局组，而不是证明组间平衡。"},
            "method_rationale": {"en": "Distribution summaries and standardized differences describe observed groups without p-value-driven screening.", "zh": "分布汇总与标准化差异用于描述观察组，避免由 p 值驱动的筛选。"},
            "how_to_read": {"en": ["Compare medians and IQRs for continuous rows.", "For binary rows, read numerator and percentage together.", "Use SMD magnitude and direction as a descriptive imbalance measure, not as a causal effect."], "zh": ["连续变量先比较中位数和四分位距。", "二分类行应同时阅读人数与百分比。", "SMD 的大小和方向只描述组间差异，不是因果效应。"]},
            "common_misreading": {"en": "Outcome-group imbalance is not an independent prognostic effect.", "zh": "结局组间差异并不等于独立预后效应。"},
            "cannot_conclude": {"en": "Independent effects or causal risk factors.", "zh": "不能据此得出独立效应或因果危险因素。"},
            "caption": {"en": "Baseline characteristics of the public heart-failure cohort.", "zh": "公开心衰队列的基线特征。"},
            "citation": "Methods and Results — cohort", "repro": "v2_demo/04_code/run_demo.py",
        },
        {
            "kind": "table", "number": "2", "title": {"en": "Prespecified Cox model", "zh": "预设 Cox 模型"},
            "csv": "06_final/tables/Table2.csv", "status": cox_status, "page_break_before": True,
            "table_title": {"en": "Table 2. Multivariable Cox proportional-hazards model", "zh": "表 2. 多变量 Cox 比例风险模型"},
            "table_note": {"en": "Covariate-level PH-test p uses rank-transformed time. A global diagnostic and graphical residual review remain pending; inspect any p<0.05 flag.", "zh": "协变量级 PH 检验采用秩变换时间。整体诊断与残差图形审查尚待完成；任何 p<0.05 均需审查。"},
            "claim": {"en": "The table reports effect size, uncertainty, and diagnostics together.", "zh": "该表同时报告效应量、不确定性和诊断。"},
            "method_rationale": {"en": "Prespecified adjustment prevents p-value-driven variable selection.", "zh": "预设校正集可避免由 p 值驱动的变量筛选。"},
            "how_to_read": {"en": ["Read HR with its 95% CI, not p-value alone.", "Check the PH-test column before treating the HR as constant over follow-up."], "zh": ["HR 必须与 95% CI 一起阅读，不能只看 p 值。", "将 HR 视为随访期恒定前，应先检查 PH 检验列。"]},
            "common_misreading": {"en": "Statistical adjustment does not remove unmeasured confounding.", "zh": "统计校正无法消除未测量混杂。"},
            "cannot_conclude": {"en": "A mechanistic or causal relationship.", "zh": "不能据此得出机制性或因果关系。"},
            "caption": {"en": "Adjusted hazard ratios and proportional-hazards diagnostics.", "zh": "校正风险比及比例风险诊断。"},
            "citation": "Results — adjusted associations", "repro": "v2_demo/04_code/run_demo.py",
        },
    ]
    output = FINAL / "Heart_Failure_v2_Report.docx"
    build_report(
        output,
        title={"en": "Heart-failure v2 statistical handoff", "zh": ""},
        subtitle={"en": "Real-data demo · analysis, interpretation, and figure-reading guide", "zh": ""},
        meta=[
            ({"en": "Dataset", "zh": "数据集"}, "UCI Heart Failure Clinical Records (n=299)"),
            ({"en": "Design", "zh": "设计"}, {"en": "Observational follow-up cohort; secondary analysis", "zh": "观察性随访队列；二次分析"}),
            ({"en": "Primary outcome", "zh": "主要结局"}, {"en": "Time to death with censoring", "zh": "含删失的死亡时间"}),
            ({"en": "Review state", "zh": "审核状态"}, {"en": results["overall_status"], "zh": results["overall_status"]}),
        ],
        items=items,
        base_dir=DEMO,
        lang="en",
        body_font="Arial",
        body_pt=9,
    )
    return output


def write_validation(results: dict, generated: list[Path]) -> Path:
    checks = []
    for path in generated:
        checks.append({"check": f"exists:{path.relative_to(DEMO).as_posix()}", "pass": path.is_file() and path.stat().st_size > 0})
    preset = get_preset(FIGURE_PRESET)
    width_in = float(preset["widths_mm"][FIGURE_COLUMN]) / 25.4
    for figure_name, aspect in FIGURE_ASPECTS.items():
        png = FIGURES / f"{figure_name}.png"
        export = validate_png_export(
            png,
            expected_size_inches=(width_in, width_in * aspect),
            expected_dpi=preset["dpi_line_art"],
        )
        checks.append({
            "check": f"png_canvas_and_dpi:{png.name}",
            "pass": export["valid"],
            "detail": (
                f"{export['width_px']}×{export['height_px']} px; "
                f"{export['width_mm']:.2f}×{export['height_mm']:.2f} mm; "
                f"{export['dpi_x']:.2f} dpi"
            ),
        })
    checks.extend([
        {"check": "source_shape_299x13", "pass": results["validation"]["shape"] == [299, 13]},
        {"check": "no_missing_cells", "pass": results["validation"]["missing_cells_n"] == 0},
        {"check": "no_duplicate_rows", "pass": results["validation"]["duplicate_rows_n"] == 0},
        {
            "check": "prediction_excludes_followup_time",
            "pass": all("time" not in features for features in results["prediction"]["feature_sets"].values()),
            "detail": str(results["prediction"]["feature_sets"]),
        },
        {
            "check": "cox_fit_completed_and_finite",
            "pass": bool(results["cox"]["fit_completed"] and np.isfinite(results["cox"]["c_index"])),
        },
        {
            "check": "cox_covariate_ph_tests_finite",
            "pass": not results["cox"]["ph_diagnostics"]["nonfinite_covariates"],
            "detail": str(results["cox"]["ph_diagnostics"]["nonfinite_covariates"]),
        },
        {
            "check": "review_state_matches_ph_gate",
            "pass": results["overall_status"] == results["cox"]["ph_diagnostics"]["status"],
        },
    ])
    passed = all(item["pass"] for item in checks)
    automated_status = "pass" if passed else "fail"
    payload = {"status": automated_status, "automated_status": automated_status, "review_state": results["overall_status"], "checks": checks, "limitations": [
        "Single-centre, small observational cohort.",
        "No external validation cohort.",
        "Binary exploratory prediction collapses unequal follow-up.",
        "Automated checks do not establish clinical correctness or causal validity.",
    ]}
    (RESULTS / "validation_checks.json").write_text(json.dumps(json_ready(payload), indent=2), encoding="utf-8")
    lines = [
        "# Validation report",
        "",
        f"Automated check status: **{payload['automated_status'].upper()}**",
        f"Scientific review state: **{payload['review_state']}**",
        "",
        "A technical PASS does not override an unresolved statistical diagnostic.",
        "",
        "## Automated checks",
        "",
    ]
    lines.extend([f"- {'PASS' if c['pass'] else 'FAIL'} — {c['check']}" + (f" ({c['detail']})" if c.get('detail') else "") for c in checks])
    lines.extend(["", "## Limitations", ""] + [f"- {x}" for x in payload["limitations"]] + [""])
    path = FINAL / "validation_report.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    if not passed:
        raise RuntimeError("One or more validation checks failed; inspect validation_checks.json")
    return path


def build_and_verify_manifest(results: dict, final_assets: list[Path]) -> tuple[Path, dict]:
    """Hash the complete generated handoff and verify it immediately."""
    source_files = [
        DATA,
        DEMO / "requirements-reference.txt",
        DEMO / "01_intake" / "study_design.md",
        DEMO / "02_audit" / "clinical_range_review.md",
        DEMO / "02_audit" / "heart_failure_source_audit.json",
        DEMO / "02_audit" / "heart_failure_source_audit.md",
        DEMO / "03_plan" / "analysis_plan.md",
    ]
    script_files = [
        Path(__file__),
        SKILL_SCRIPTS / "analysis_manifest.py",
        SKILL_SCRIPTS / "docx_tables.py",
        SKILL_SCRIPTS / "figstyle.py",
        SKILL_SCRIPTS / "report_docx.py",
        REPO / "statmate" / "requirements-demo.txt",
    ]
    result_files = [
        RESULTS / "data_validation.json",
        RESULTS / "table1_baseline.csv",
        RESULTS / "table2_cox.csv",
        RESULTS / "model_metrics.csv",
        RESULTS / "prediction_fold_metrics.csv",
        RESULTS / "analysis_results.json",
        RESULTS / "validation_checks.json",
    ]
    groups = {
        "inputs": source_files,
        "scripts": script_files,
        "results": result_files,
        "assets": sorted(final_assets),
    }
    if results["overall_status"] == "needs-author-decision":
        review_reasons = " ".join(results["cox"]["ph_diagnostics"]["review_reasons"])
        note = (
            "Automated artifact checks passed, but scientific review remains open: "
            + review_reasons
            + " The manually converted PDF report snapshot is outside this generated asset set."
        )
    else:
        note = "Automated artifact checks passed; the manually converted PDF report snapshot is outside this generated asset set."
    manifest = build_manifest(
        DEMO,
        groups,
        status=results["overall_status"],
        note=note,
        manifest_path=MANIFEST,
    )
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    verification = verify_manifest(MANIFEST)
    verification_path = RESULTS / "manifest_verification.json"
    verification_path.write_text(
        json.dumps(portable_manifest_verification(verification), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    if not verification["ok"]:
        raise RuntimeError(f"Manifest verification failed; inspect {verification_path}")
    return MANIFEST, verification


def main() -> None:
    for directory in [RESULTS, FIGURES, TABLES]:
        directory.mkdir(parents=True, exist_ok=True)
    df, validation = load_and_validate()
    (RESULTS / "data_validation.json").write_text(json.dumps(json_ready(validation), indent=2), encoding="utf-8")

    table1 = build_table1(df)
    cph, table2, ph = fit_cox(df)
    logrank_p, risk_counts = plot_km(df)
    plot_cox(cph, ph)
    model_metrics, prediction_details = prediction_analysis(df)

    table1.to_csv(RESULTS / "table1_baseline.csv", index=False, encoding="utf-8-sig")
    table2.to_csv(RESULTS / "table2_cox.csv", index=False, encoding="utf-8-sig")
    model_metrics.to_csv(RESULTS / "model_metrics.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(prediction_details["fold_metrics"]).to_csv(RESULTS / "prediction_fold_metrics.csv", index=False, encoding="utf-8-sig")
    table1.to_csv(TABLES / "Table1.csv", index=False, encoding="utf-8-sig")
    table2.to_csv(TABLES / "Table2.csv", index=False, encoding="utf-8-sig")
    three_line_table(table1, TABLES / "Table1.docx", title="Table 1. Baseline characteristics by observed outcome", note="Continuous: median [Q1, Q3]; binary: n (%). SMD direction is Died minus Censored.", size_pt=8)
    three_line_table(table2, TABLES / "Table2.docx", title="Table 2. Prespecified multivariable Cox model", note="Covariate-level PH-test p is based on scaled Schoenfeld residuals with rank-transformed time; global and graphical PH review remain pending.", size_pt=9)

    s = cph.summary
    full = model_metrics[model_metrics.Model.eq("All 11 baseline features")].iloc[0]
    two = model_metrics[model_metrics.Model.eq("Creatinine + ejection fraction")].iloc[0]
    ph_diagnostics = assess_ph_diagnostics(ph)
    ph_message = " ".join(ph_diagnostics["review_reasons"])
    overall_status = ph_diagnostics["status"]
    results = {
        "validation": validation,
        "logrank_p": logrank_p,
        "risk_counts": risk_counts,
        "cox": {
            "c_index": float(cph.concordance_index_),
            "ef_hr": float(np.exp(s.loc["ef_5pct", "coef"])),
            "ef_lo": float(np.exp(s.loc["ef_5pct", "coef lower 95%"])),
            "ef_hi": float(np.exp(s.loc["ef_5pct", "coef upper 95%"])),
            "cr_hr": float(np.exp(s.loc["creatinine_1", "coef"])),
            "cr_lo": float(np.exp(s.loc["creatinine_1", "coef lower 95%"])),
            "cr_hi": float(np.exp(s.loc["creatinine_1", "coef upper 95%"])),
            "ph_test_p": ph["p"].to_dict(),
            "ph_diagnostics": ph_diagnostics,
            "ph_message": ph_message,
            "fit_completed": True,
        },
        "prediction": {
            "full_auc": full["AUC, mean (SD)"],
            "two_auc": two["AUC, mean (SD)"],
            "full_brier": full["Brier, mean (SD)"],
            "two_brier": two["Brier, mean (SD)"],
            "fixed_oof": prediction_details["fixed_oof"],
            "feature_sets": prediction_details["feature_sets"],
        },
        "overall_status": overall_status,
    }
    (RESULTS / "analysis_results.json").write_text(json.dumps(json_ready(results), indent=2, ensure_ascii=False), encoding="utf-8")
    report_md = write_markdown_report(results)
    report_docx = build_word_report(results)
    generated = [
        *(FIGURES / f"Fig{number}.{extension}" for number in (1, 2, 3) for extension in ("png", "pdf")),
        TABLES / "Table1.csv",
        TABLES / "Table1.docx",
        TABLES / "Table2.csv",
        TABLES / "Table2.docx",
        report_md,
        report_docx,
    ]
    validation_md = write_validation(results, generated)
    manifest_path, manifest_verification = build_and_verify_manifest(results, generated + [validation_md])
    print(json.dumps(json_ready({
        "run_status": "ok",
        "review_state": results["overall_status"],
        "report": str(report_docx),
        "validation": str(validation_md),
        "manifest": str(manifest_path),
        "manifest_verified": manifest_verification["ok"],
        "results": results,
    }), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
