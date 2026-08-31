"""Regression tests for StatMate's physical-size figure export."""
from __future__ import annotations

import copy
import json
import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("MPLBACKEND", "Agg")

STATMATE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STATMATE_ROOT / "scripts"))

import figstyle  # noqa: E402


@pytest.fixture(autouse=True)
def _restore_matplotlib_defaults():
    import matplotlib as mpl
    import matplotlib.pyplot as plt

    original = mpl.rcParams.copy()
    yield
    plt.close("all")
    mpl.rcParams.update(original)


def test_bundled_presets_are_valid_and_palette_is_resolved():
    presets = figstyle.list_presets()
    assert "generic" in presets
    spec = figstyle.get_preset("generic")
    assert spec["palette_colors"]
    assert spec["widths_mm"]["single"] == 90


def test_apply_preset_rejects_unknown_column_and_excess_height():
    with pytest.raises(ValueError, match="Unknown column"):
        figstyle.apply_preset("generic", column="quarter")

    with pytest.raises(ValueError, match="exceeds.*maximum"):
        figstyle.apply_preset("generic", column="double", aspect=2.0)


def test_preset_schema_rejects_missing_field_unknown_palette_and_bad_format():
    data = json.loads((STATMATE_ROOT / "assets" / "presets.json").read_text(encoding="utf-8"))

    missing = copy.deepcopy(data)
    del missing["presets"]["generic"]["max_height_mm"]
    with pytest.raises(ValueError, match="missing required fields: max_height_mm"):
        figstyle._validate_data(missing)

    unknown_palette = copy.deepcopy(data)
    unknown_palette["presets"]["generic"]["palette"] = "not-installed"
    with pytest.raises(ValueError, match="unknown palette"):
        figstyle._validate_data(unknown_palette)

    bad_format = copy.deepcopy(data)
    bad_format["presets"]["generic"]["export_formats"] = ["png", "docx"]
    with pytest.raises(ValueError, match="Unsupported.*export_formats"):
        figstyle._validate_data(bad_format)


def test_default_export_preserves_canvas_pixels_and_physical_size(tmp_path):
    import matplotlib as mpl
    import matplotlib.pyplot as plt

    spec = figstyle.apply_preset("generic", column="single", aspect=0.5)
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    expected_size = tuple(float(value) for value in fig.get_size_inches())

    # A third-party style may set this after apply_preset(); save_figure must
    # still export the complete canvas rather than silently crop it.
    mpl.rcParams["savefig.bbox"] = "tight"
    paths = figstyle.save_figure(fig, number="1", preset="generic", outdir=tmp_path)

    assert [Path(path).suffix for path in paths] == [".png", ".pdf"]
    assert all(Path(path).is_file() for path in paths)
    assert tuple(float(value) for value in fig.get_size_inches()) == expected_size

    info = figstyle.validate_png_export(
        tmp_path / "Fig1.png",
        expected_size_inches=expected_size,
        expected_dpi=spec["dpi_raster"],
    )
    assert info["valid"], info["errors"]
    assert info["width_px"] == pytest.approx(expected_size[0] * spec["dpi_raster"], abs=1)
    assert info["height_px"] == pytest.approx(expected_size[1] * spec["dpi_raster"], abs=1)
    assert info["width_mm"] == pytest.approx(90.0, abs=0.1)
    assert info["height_mm"] == pytest.approx(45.0, abs=0.1)


def test_save_rejects_bad_kind_format_and_too_tall_figure(tmp_path):
    import matplotlib.pyplot as plt

    fig = plt.figure(figsize=(2, 2))
    with pytest.raises(ValueError, match="Unknown kind"):
        figstyle.save_figure(fig, 1, outdir=tmp_path, kind="photo")
    with pytest.raises(ValueError, match="Unsupported.*formats"):
        figstyle.save_figure(fig, 1, outdir=tmp_path, formats=["docx"])

    tall = plt.figure(figsize=(2, 10))
    with pytest.raises(ValueError, match="exceeds.*maximum"):
        figstyle.save_figure(tall, 2, outdir=tmp_path)


def test_explicit_single_format_remains_supported(tmp_path):
    import matplotlib.pyplot as plt

    figstyle.apply_preset("generic", aspect=0.5)
    fig, _ = plt.subplots()
    paths = figstyle.save_figure(fig, "S1", outdir=tmp_path, formats="png")
    assert paths == [os.path.join(tmp_path, "FigS1.png")]


def test_explicit_figsize_is_validated_as_actual_canvas_not_forced_to_preset_width(tmp_path):
    import matplotlib.pyplot as plt

    spec = figstyle.apply_preset("generic", column="double", aspect=0.5)
    # 7.1 in is intentionally a little wider than the 180 mm preset (7.087 in).
    fig = plt.figure(figsize=(7.1, 3.0))
    figstyle.save_figure(fig, "wide", outdir=tmp_path, formats=["png"])

    info = figstyle.validate_png_export(
        tmp_path / "Figwide.png",
        expected_size_inches=(7.1, 3.0),
        expected_dpi=spec["dpi_raster"],
    )
    assert info["valid"], info["errors"]
    assert info["width_px"] == pytest.approx(7.1 * spec["dpi_raster"], abs=1)
