"""Shared data loading for the Palmer Penguins example (StatMate skill demo).

Loads the raw Gorman et al. (2014) penguin morphometrics, makes figstyle.py
importable, and exposes tidy column names so every figure/table script starts
from the same clean frame.
"""
from pathlib import Path
import sys

import pandas as pd

# Print Unicode (±, ρ…) safely even on a GBK/cp1252 console.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# --- make the skill's figstyle helper importable ---------------------------
_HERE = Path(__file__).resolve().parent
_SKILL_SCRIPTS = _HERE.parents[2] / "statmate" / "scripts"
sys.path.insert(0, str(_SKILL_SCRIPTS))

from docx_tables import three_line_table  # noqa: E402  (re-exported for table scripts)

DATA = _HERE.parent / "data" / "penguins_raw.csv"
FIGDIR = _HERE.parent / "figures"

# Short species labels (raw values are e.g. "Adelie Penguin (Pygoscelis adeliae)")
SPECIES_ORDER = ["Adelie", "Chinstrap", "Gentoo"]


def load_clean() -> pd.DataFrame:
    """Return a tidy frame with the columns the figures use.

    One row = one measured penguin (the unit of analysis). Rows missing the
    morphometric or sex used by a given figure are dropped *in that figure*,
    not here, so each script can report its own n.
    """
    df = pd.read_csv(DATA)
    df = df.rename(
        columns={
            "Culmen Length (mm)": "culmen_length_mm",
            "Culmen Depth (mm)": "culmen_depth_mm",
            "Flipper Length (mm)": "flipper_length_mm",
            "Body Mass (g)": "body_mass_g",
        }
    )
    df["species"] = df["Species"].str.split().str[0]  # first word -> Adelie/Chinstrap/Gentoo
    df["sex"] = df["Sex"].str.title()  # MALE/FEMALE -> Male/Female
    df.loc[~df["sex"].isin(["Male", "Female"]), "sex"] = pd.NA  # drop '.' / NA codes
    df["species"] = pd.Categorical(df["species"], categories=SPECIES_ORDER, ordered=True)
    return df


if __name__ == "__main__":
    d = load_clean()
    print("rows:", len(d))
    print(d.groupby(["species", "sex"], observed=True).size())
