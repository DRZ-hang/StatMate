"""Shared data loading for the Heart-Failure survival example (StatMate demo).

Loads the Chicco & Jurman (2020) heart-failure clinical records, makes the skill's
figstyle/docx helpers importable, and labels the categorical codes so figures and
tables read cleanly.

One row = one patient. `time` is follow-up in days; `death_event` = 1 if the patient
died during follow-up, else 0 (censored).
"""
from pathlib import Path
import sys

import pandas as pd

# Print Unicode (en-dash, ±, ρ…) safely even on a GBK/cp1252 console.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

_HERE = Path(__file__).resolve().parent
_SKILL_SCRIPTS = _HERE.parents[2] / "statmate" / "scripts"
sys.path.insert(0, str(_SKILL_SCRIPTS))

from docx_tables import three_line_table  # noqa: E402  (re-exported for table scripts)

DATA = _HERE.parent / "data" / "heart_failure_clinical_records.csv"
FIGDIR = _HERE.parent / "figures"

# continuous clinical variables (with display labels and rounding)
CONTINUOUS = [
    ("age", "Age (years)", 0),
    ("ejection_fraction", "Ejection fraction (%)", 0),
    ("serum_creatinine", "Serum creatinine (mg/dL)", 2),
    ("serum_sodium", "Serum sodium (mEq/L)", 0),
    ("platelets", "Platelets (×10³/µL)", 0),
    ("creatinine_phosphokinase", "CPK (mcg/L)", 0),
]
BINARY = [
    ("sex", "Male sex"),
    ("anaemia", "Anaemia"),
    ("diabetes", "Diabetes"),
    ("high_blood_pressure", "Hypertension"),
    ("smoking", "Smoking"),
]


def load_clean() -> pd.DataFrame:
    df = pd.read_csv(DATA)
    df = df.rename(columns={"DEATH_EVENT": "death_event"})
    df["platelets"] = df["platelets"] / 1000.0  # ×10^3 per µL for readability
    df["outcome"] = df["death_event"].map({0: "Survived", 1: "Died"})
    return df


if __name__ == "__main__":
    d = load_clean()
    print("patients:", len(d), "| deaths:", int(d.death_event.sum()),
          f"({d.death_event.mean()*100:.0f}%)")
    print("follow-up days: median", int(d.time.median()), "range", int(d.time.min()), "-", int(d.time.max()))
    print(d[["age", "ejection_fraction", "serum_creatinine", "time", "death_event"]].describe().round(1))
