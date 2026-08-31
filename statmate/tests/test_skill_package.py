from __future__ import annotations

import ast
import json
from pathlib import Path

import yaml


SKILL = Path(__file__).resolve().parents[1]


def _frontmatter() -> dict:
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    assert text.startswith("---\n")
    _, raw, _ = text.split("---", 2)
    return yaml.safe_load(raw)


def test_skill_frontmatter_is_discriminating() -> None:
    frontmatter = _frontmatter()
    assert frontmatter["name"] == "statmate"
    description = frontmatter["description"]
    assert 80 <= len(description) <= 700
    assert "generic business charts" in description


def test_scripts_parse_and_presets_are_complete() -> None:
    for script in sorted((SKILL / "scripts").glob("*.py")):
        ast.parse(script.read_text(encoding="utf-8"), filename=str(script))

    data = json.loads((SKILL / "assets" / "presets.json").read_text(encoding="utf-8"))
    required = {
        "widths_mm", "max_height_mm", "font_family", "font_size_pt",
        "axes_label_pt", "tick_label_pt", "title_pt", "line_width_pt",
        "axes_line_width_pt", "dpi_raster", "dpi_line_art", "export_formats",
        "color_mode", "palette", "panel_label_case",
    }
    assert data["presets"]
    for name, preset in data["presets"].items():
        assert not (required - preset.keys()), name
        assert preset["palette"] in data["palettes"]


def test_package_dependency_profiles_exist() -> None:
    for name in (
        "requirements.txt",
        "requirements-all.txt",
        "requirements-demo.txt",
        "requirements-test.txt",
    ):
        assert (SKILL / name).is_file()
