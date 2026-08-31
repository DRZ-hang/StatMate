from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest
from docx import Document


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from docx_tables import three_line_table  # noqa: E402
from table_export import export_table  # noqa: E402


def test_final_export_requires_approval_and_writes_only_requested_formats(tmp_path: Path) -> None:
    frame = pd.DataFrame({"Measure": ["A"], "Estimate": [1.2]})
    with pytest.raises(PermissionError, match="approved=True"):
        export_table(frame, tmp_path, "Table1", ["csv"], approved=False)

    written = export_table(frame, tmp_path, "Table1", ["csv", ".CSV"], approved=True)
    assert written == [tmp_path / "Table1.csv"]
    assert sorted(path.name for path in tmp_path.iterdir()) == ["Table1.csv"]


@pytest.mark.parametrize("stem", ["", ".", "..", "../escape", r"nested\escape", "/absolute"])
def test_export_rejects_unsafe_output_stems(tmp_path: Path, stem: str) -> None:
    with pytest.raises(ValueError, match="stem|directory|traversal"):
        export_table(pd.DataFrame({"x": [1]}), tmp_path, stem, ["csv"], approved=True)


def test_standalone_docx_table_creates_parent_and_keeps_title_note(tmp_path: Path) -> None:
    output = tmp_path / "nested" / "Table1.docx"
    returned = three_line_table(
        pd.DataFrame({"Characteristic": ["Age"], "Value": ["50 [40, 60]"]}),
        output,
        title="Table 1. Cohort",
        note="Values are median [Q1, Q3].",
    )
    assert returned == output
    document = Document(output)
    visible = "\n".join(paragraph.text for paragraph in document.paragraphs)
    assert "Table 1. Cohort" in visible
    assert "Values are median [Q1, Q3]." in visible
