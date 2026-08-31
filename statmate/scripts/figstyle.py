#!/usr/bin/env python3
"""Apply a validated journal preset and export full-size matplotlib figures.

The helper deliberately exports the complete figure canvas. In particular, it
does not use ``bbox_inches="tight"`` because tight bounding boxes change the
physical dimensions declared by the selected journal preset.

Quick use inside a plotting script
-----------------------------------
    from figstyle import apply_preset, save_figure
    apply_preset("nature", column="single")
    fig, ax = plt.subplots()
    ...
    save_figure(fig, number="1", preset="nature")  # Fig1.png + Fig1.pdf

CLI
---
    python figstyle.py --list
    python figstyle.py --show nature

Presets live in ../assets/presets.json. Bundled values are starting points;
verify them against the journal's current author guidance before submission.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import struct
from pathlib import Path

MM_PER_INCH = 25.4
_PRESETS_PATH = Path(__file__).resolve().parent.parent / "assets" / "presets.json"

SUPPORTED_COLUMNS = ("single", "onehalf", "double")
SUPPORTED_KINDS = ("raster", "line")
RASTER_FORMATS = frozenset(
    {"jpeg", "jpg", "png", "raw", "rgba", "tif", "tiff", "webp"}
)
VECTOR_FORMATS = frozenset({"eps", "pdf", "pgf", "ps", "svg", "svgz"})
SUPPORTED_FORMATS = RASTER_FORMATS | VECTOR_FORMATS

_REQUIRED_PRESET_FIELDS = frozenset(
    {
        "label",
        "widths_mm",
        "max_height_mm",
        "font_family",
        "font_size_pt",
        "axes_label_pt",
        "tick_label_pt",
        "title_pt",
        "line_width_pt",
        "axes_line_width_pt",
        "dpi_raster",
        "dpi_line_art",
        "export_formats",
        "color_mode",
        "palette",
        "panel_label_case",
    }
)
_POSITIVE_NUMBER_FIELDS = (
    "max_height_mm",
    "font_size_pt",
    "axes_label_pt",
    "tick_label_pt",
    "title_pt",
    "line_width_pt",
    "axes_line_width_pt",
)
_HEX_COLOR = re.compile(r"^#[0-9A-Fa-f]{6}(?:[0-9A-Fa-f]{2})?$")
_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _positive_number(value, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be a positive number; got {value!r}.")
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise ValueError(f"{field} must be a positive finite number; got {value!r}.")
    return number


def _normalise_format(value, field: str = "format") -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty format name.")
    fmt = value.strip().lower().lstrip(".")
    if fmt not in SUPPORTED_FORMATS:
        choices = ", ".join(sorted(SUPPORTED_FORMATS))
        raise ValueError(f"Unsupported {field} '{value}'. Supported formats: {choices}.")
    return fmt


def _validate_palette(name: str, colors) -> None:
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Palette names must be non-empty strings.")
    if not isinstance(colors, list) or not colors:
        raise ValueError(f"Palette '{name}' must contain at least one color.")
    invalid = [
        color
        for color in colors
        if not isinstance(color, str) or not _HEX_COLOR.fullmatch(color)
    ]
    if invalid:
        raise ValueError(
            f"Palette '{name}' contains invalid colors {invalid!r}; use #RRGGBB or #RRGGBBAA."
        )


def _validate_preset(name: str, spec, palettes: dict) -> None:
    if not isinstance(spec, dict):
        raise ValueError(f"Preset '{name}' must be a JSON object.")

    missing = sorted(_REQUIRED_PRESET_FIELDS - set(spec))
    if missing:
        raise ValueError(f"Preset '{name}' is missing required fields: {', '.join(missing)}.")

    for field in ("label", "font_family"):
        if not isinstance(spec[field], str) or not spec[field].strip():
            raise ValueError(f"Preset '{name}' field '{field}' must be a non-empty string.")

    widths = spec["widths_mm"]
    if not isinstance(widths, dict):
        raise ValueError(f"Preset '{name}' field 'widths_mm' must be an object.")
    missing_columns = [column for column in SUPPORTED_COLUMNS if column not in widths]
    if missing_columns:
        raise ValueError(
            f"Preset '{name}' is missing widths for: {', '.join(missing_columns)}."
        )
    unknown_columns = sorted(set(widths) - set(SUPPORTED_COLUMNS))
    if unknown_columns:
        raise ValueError(
            f"Preset '{name}' has unsupported width columns: {', '.join(unknown_columns)}."
        )
    for column in SUPPORTED_COLUMNS:
        _positive_number(widths[column], f"Preset '{name}' widths_mm.{column}")

    for field in _POSITIVE_NUMBER_FIELDS:
        _positive_number(spec[field], f"Preset '{name}' {field}")

    for field in ("dpi_raster", "dpi_line_art"):
        value = spec[field]
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(f"Preset '{name}' field '{field}' must be a positive integer.")

    export_formats = spec["export_formats"]
    if not isinstance(export_formats, list) or not export_formats:
        raise ValueError(f"Preset '{name}' field 'export_formats' must be a non-empty list.")
    for index, fmt in enumerate(export_formats):
        _normalise_format(fmt, f"preset '{name}' export_formats[{index}]")

    if spec["color_mode"] != "RGB":
        raise ValueError(
            f"Preset '{name}' color_mode must be 'RGB'; this matplotlib helper does not "
            "perform CMYK or grayscale conversion."
        )
    if spec["panel_label_case"] not in {"lower", "upper"}:
        raise ValueError(
            f"Preset '{name}' panel_label_case must be 'lower' or 'upper'."
        )

    palette = spec["palette"]
    if not isinstance(palette, str) or not palette.strip():
        raise ValueError(f"Preset '{name}' field 'palette' must name a palette.")
    if palette not in palettes:
        raise ValueError(
            f"Preset '{name}' references unknown palette '{palette}'. "
            f"Available palettes: {', '.join(sorted(palettes)) or '(none)'}."
        )


def _validate_data(data) -> None:
    if not isinstance(data, dict):
        raise ValueError("presets.json must contain a JSON object.")
    presets = data.get("presets")
    palettes = data.get("palettes")
    if not isinstance(presets, dict) or not presets:
        raise ValueError("presets.json must contain a non-empty 'presets' object.")
    if not isinstance(palettes, dict) or not palettes:
        raise ValueError("presets.json must contain a non-empty 'palettes' object.")

    for palette_name, colors in palettes.items():
        _validate_palette(palette_name, colors)
    for preset_name, spec in presets.items():
        if not isinstance(preset_name, str) or not preset_name.strip():
            raise ValueError("Preset names must be non-empty strings.")
        _validate_preset(preset_name, spec, palettes)


def _load() -> dict:
    with open(_PRESETS_PATH, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    _validate_data(data)
    return data


def list_presets() -> dict:
    """Return ``{name: label}`` for every validated preset."""
    data = _load()
    return {name: spec["label"] for name, spec in data["presets"].items()}


def get_preset(name: str) -> dict:
    """Return one validated preset with its named palette resolved."""
    data = _load()
    presets = data["presets"]
    if name not in presets:
        raise KeyError(
            f"Unknown preset '{name}'. Available: {', '.join(presets)}. "
            f"Add it to {_PRESETS_PATH}."
        )
    spec = dict(presets[name])
    spec["palette_colors"] = list(data["palettes"][spec["palette"]])
    return spec


def _validate_column(column: str) -> str:
    if column not in SUPPORTED_COLUMNS:
        raise ValueError(
            f"Unknown column '{column}'. Choose one of: {', '.join(SUPPORTED_COLUMNS)}."
        )
    return column


def _validate_height(height_mm: float, spec: dict, preset: str) -> None:
    maximum = float(spec["max_height_mm"])
    if height_mm > maximum + 1e-9:
        raise ValueError(
            f"Figure height {height_mm:.2f} mm exceeds preset '{preset}' maximum "
            f"of {maximum:.2f} mm. Reduce the aspect ratio or figure height."
        )


def apply_preset(name: str = "generic", column: str = "single", aspect: float = 0.72):
    """Configure matplotlib from a validated journal preset and return its spec.

    ``column`` must be ``single``, ``onehalf`` or ``double``. ``aspect`` is the
    default height/width ratio. The resulting height may not exceed the preset's
    ``max_height_mm``. A caller can still pass an explicit ``figsize`` later;
    :func:`save_figure` checks that explicit height before export.
    """
    import matplotlib as mpl
    import matplotlib.pyplot as plt  # noqa: F401  (ensures backend init)

    _validate_column(column)
    aspect_value = _positive_number(aspect, "aspect")
    spec = get_preset(name)
    width_mm = float(spec["widths_mm"][column])
    height_mm = width_mm * aspect_value
    _validate_height(height_mm, spec, name)
    width_in = width_mm / MM_PER_INCH
    height_in = height_mm / MM_PER_INCH

    rc = {
        "figure.figsize": (width_in, height_in),
        "figure.dpi": 150,
        "savefig.dpi": spec["dpi_raster"],
        # Preserve the complete canvas and therefore the declared physical size.
        "savefig.bbox": None,
        "savefig.pad_inches": 0.0,
        "font.family": spec["font_family"],
        "font.size": spec["font_size_pt"],
        "axes.labelsize": spec["axes_label_pt"],
        "axes.titlesize": spec["title_pt"],
        "xtick.labelsize": spec["tick_label_pt"],
        "ytick.labelsize": spec["tick_label_pt"],
        "legend.fontsize": spec["tick_label_pt"],
        "lines.linewidth": spec["line_width_pt"],
        "axes.linewidth": spec["axes_line_width_pt"],
        "xtick.major.width": spec["axes_line_width_pt"],
        "ytick.major.width": spec["axes_line_width_pt"],
        "axes.spines.top": False,
        "axes.spines.right": False,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
        "figure.constrained_layout.use": True,
    }
    mpl.rcParams.update(rc)

    colors = spec["palette_colors"]
    mpl.rcParams["axes.prop_cycle"] = mpl.cycler(color=colors)
    return spec


def inspect_png_export(path) -> dict:
    """Read PNG pixel, DPI and physical dimensions without optional libraries."""
    png_path = Path(path)
    width_px = height_px = None
    pixels_per_metre_x = pixels_per_metre_y = None

    with png_path.open("rb") as fh:
        if fh.read(8) != _PNG_SIGNATURE:
            raise ValueError(f"'{png_path}' is not a valid PNG file.")
        while True:
            raw_length = fh.read(4)
            if not raw_length:
                break
            if len(raw_length) != 4:
                raise ValueError(f"PNG '{png_path}' has a truncated chunk header.")
            length = struct.unpack(">I", raw_length)[0]
            chunk_type = fh.read(4)
            payload = fh.read(length)
            checksum = fh.read(4)
            if len(chunk_type) != 4 or len(payload) != length or len(checksum) != 4:
                raise ValueError(f"PNG '{png_path}' contains a truncated chunk.")
            if chunk_type == b"IHDR":
                if length < 8:
                    raise ValueError(f"PNG '{png_path}' contains an invalid IHDR chunk.")
                width_px, height_px = struct.unpack(">II", payload[:8])
            elif chunk_type == b"pHYs" and length == 9:
                ppm_x, ppm_y, unit = struct.unpack(">IIB", payload)
                if unit == 1 and ppm_x and ppm_y:
                    pixels_per_metre_x = ppm_x
                    pixels_per_metre_y = ppm_y
            elif chunk_type == b"IEND":
                break

    if width_px is None or height_px is None:
        raise ValueError(f"PNG '{png_path}' does not contain a valid IHDR chunk.")

    dpi_x = pixels_per_metre_x * 0.0254 if pixels_per_metre_x else None
    dpi_y = pixels_per_metre_y * 0.0254 if pixels_per_metre_y else None
    width_in = width_px / dpi_x if dpi_x else None
    height_in = height_px / dpi_y if dpi_y else None
    return {
        "path": str(png_path),
        "format": "png",
        "width_px": width_px,
        "height_px": height_px,
        "dpi_x": dpi_x,
        "dpi_y": dpi_y,
        "width_in": width_in,
        "height_in": height_in,
        "width_mm": width_in * MM_PER_INCH if width_in is not None else None,
        "height_mm": height_in * MM_PER_INCH if height_in is not None else None,
    }


def validate_png_export(
    path,
    *,
    expected_size_inches=None,
    expected_dpi=None,
    tolerance_pixels: float = 1.0,
    tolerance_mm: float = 0.1,
    tolerance_dpi: float = 0.1,
    raise_on_error: bool = False,
) -> dict:
    """Validate PNG pixels and encoded physical size, returning audit information.

    ``expected_size_inches`` is ``(width, height)``. Supplying it with
    ``expected_dpi`` verifies both the full-canvas pixel dimensions and the PNG
    pHYs metadata. The returned dict contains ``valid`` and ``errors`` alongside
    the observed dimensions. Set ``raise_on_error=True`` for an export gate.
    """
    for value, label in (
        (tolerance_pixels, "tolerance_pixels"),
        (tolerance_mm, "tolerance_mm"),
        (tolerance_dpi, "tolerance_dpi"),
    ):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
            raise ValueError(f"{label} must be a non-negative number.")

    info = inspect_png_export(path)
    errors = []

    size = None
    if expected_size_inches is not None:
        try:
            if len(expected_size_inches) != 2:
                raise ValueError
            size = tuple(
                _positive_number(value, f"expected_size_inches[{index}]")
                for index, value in enumerate(expected_size_inches)
            )
        except TypeError as exc:
            raise ValueError("expected_size_inches must be a (width, height) pair.") from exc
        except ValueError as exc:
            if "expected_size_inches[" in str(exc):
                raise
            raise ValueError("expected_size_inches must be a (width, height) pair.") from exc

    dpi_pair = None
    if expected_dpi is not None:
        if isinstance(expected_dpi, (tuple, list)):
            if len(expected_dpi) != 2:
                raise ValueError("expected_dpi must be a number or an (x, y) pair.")
            dpi_pair = tuple(
                _positive_number(value, f"expected_dpi[{index}]")
                for index, value in enumerate(expected_dpi)
            )
        else:
            dpi_value = _positive_number(expected_dpi, "expected_dpi")
            dpi_pair = (dpi_value, dpi_value)

    if dpi_pair is not None:
        if info["dpi_x"] is None or info["dpi_y"] is None:
            errors.append("PNG has no physical-resolution (pHYs) metadata.")
        else:
            for axis, observed, expected in (
                ("x", info["dpi_x"], dpi_pair[0]),
                ("y", info["dpi_y"], dpi_pair[1]),
            ):
                if abs(observed - expected) > tolerance_dpi:
                    errors.append(
                        f"PNG {axis}-DPI is {observed:.4f}; expected {expected:.4f}."
                    )

    if size is not None:
        expected_mm = (size[0] * MM_PER_INCH, size[1] * MM_PER_INCH)
        info["expected_width_in"] = size[0]
        info["expected_height_in"] = size[1]
        info["expected_width_mm"] = expected_mm[0]
        info["expected_height_mm"] = expected_mm[1]

        if info["width_mm"] is None or info["height_mm"] is None:
            errors.append("PNG physical dimensions cannot be verified without pHYs metadata.")
        else:
            for axis, observed, expected in (
                ("width", info["width_mm"], expected_mm[0]),
                ("height", info["height_mm"], expected_mm[1]),
            ):
                if abs(observed - expected) > tolerance_mm:
                    errors.append(
                        f"PNG physical {axis} is {observed:.3f} mm; expected {expected:.3f} mm."
                    )

        if dpi_pair is not None:
            expected_pixels = (size[0] * dpi_pair[0], size[1] * dpi_pair[1])
            info["expected_width_px"] = expected_pixels[0]
            info["expected_height_px"] = expected_pixels[1]
            for axis, observed, expected in (
                ("width", info["width_px"], expected_pixels[0]),
                ("height", info["height_px"], expected_pixels[1]),
            ):
                if abs(observed - expected) > tolerance_pixels:
                    errors.append(
                        f"PNG pixel {axis} is {observed}; expected {expected:.3f} (±{tolerance_pixels})."
                    )

    info["valid"] = not errors
    info["errors"] = errors
    if errors and raise_on_error:
        raise ValueError(f"PNG export validation failed for '{path}': " + " ".join(errors))
    return info


def save_figure(
    fig,
    number,
    preset: str = "generic",
    outdir: str = "figures",
    kind: str = "raster",
    formats=None,
    prefix: str = "Fig",
    preview_format: str = "png",
    vector_format: str = "pdf",
):
    """Save a full-canvas raster/vector pair with consistent naming.

    Valid existing calls retain the same interface and return a list of written
    paths. By default the function writes PNG + PDF, independent of a venue's
    final-submission ``export_formats``. Pass ``formats`` to override the pair.
    """
    import matplotlib as mpl

    spec = get_preset(preset)
    if not isinstance(kind, str) or kind.lower() not in SUPPORTED_KINDS:
        raise ValueError(f"Unknown kind '{kind}'. Choose one of: {', '.join(SUPPORTED_KINDS)}.")
    kind = kind.lower()

    if formats is None:
        preview = _normalise_format(preview_format, "preview_format")
        vector = _normalise_format(vector_format, "vector_format")
        if preview not in RASTER_FORMATS:
            raise ValueError(f"preview_format '{preview}' must be a raster format.")
        if vector not in VECTOR_FORMATS:
            raise ValueError(f"vector_format '{vector}' must be a vector format.")
        requested_formats = [preview, vector]
    else:
        requested_formats = [formats] if isinstance(formats, str) else list(formats)
    fmts = list(
        dict.fromkeys(
            _normalise_format(fmt, f"formats[{index}]")
            for index, fmt in enumerate(requested_formats)
        )
    )
    if not fmts:
        raise ValueError("Choose at least one output format.")

    backend_formats = set(fig.canvas.get_supported_filetypes())
    unavailable = [fmt for fmt in fmts if fmt not in backend_formats]
    if unavailable:
        raise ValueError(
            "The active matplotlib backend cannot export: " + ", ".join(unavailable) + "."
        )

    figure_size_inches = tuple(float(value) for value in fig.get_size_inches())
    if len(figure_size_inches) != 2 or any(
        not math.isfinite(value) or value <= 0 for value in figure_size_inches
    ):
        raise ValueError(f"Figure size must be positive and finite; got {figure_size_inches!r}.")
    _validate_height(figure_size_inches[1] * MM_PER_INCH, spec, preset)

    Path(outdir).mkdir(parents=True, exist_ok=True)
    dpi = spec["dpi_line_art"] if kind == "line" else spec["dpi_raster"]
    written = []
    base = f"{prefix}{number}"
    for fmt in fmts:
        path = os.path.join(outdir, f"{base}.{fmt}")
        save_dpi = dpi if fmt in RASTER_FORMATS else None
        # An rc_context makes full-canvas export reliable even if another library
        # globally set savefig.bbox='tight' after apply_preset().
        with mpl.rc_context({"savefig.bbox": None, "savefig.pad_inches": 0.0}):
            fig.savefig(path, dpi=save_dpi, bbox_inches=None, pad_inches=0.0)
        if tuple(float(value) for value in fig.get_size_inches()) != figure_size_inches:
            raise RuntimeError("matplotlib changed the figure size during export.")
        if fmt == "png":
            validate_png_export(
                path,
                expected_size_inches=figure_size_inches,
                expected_dpi=save_dpi,
                raise_on_error=True,
            )
        written.append(path)
        print(
            f"[figstyle] wrote {path}"
            + (f" @ {save_dpi} dpi (full canvas)" if save_dpi else " (vector, full canvas)")
        )
    return written


def _cli():
    parser = argparse.ArgumentParser(description="Inspect validated StatMate journal presets.")
    parser.add_argument("--list", action="store_true", help="list available presets")
    parser.add_argument("--show", metavar="NAME", help="print one preset's settings")
    args = parser.parse_args()

    if args.show:
        print(json.dumps(get_preset(args.show), indent=2, ensure_ascii=False))
    else:
        print("Available presets (edit assets/presets.json to add/modify):\n")
        for name, label in list_presets().items():
            print(f"  {name:<10} {label}")
        print("\nUse: apply_preset('<name>', column='single'|'onehalf'|'double')")


if __name__ == "__main__":
    _cli()
