# Journal Specifications — what to look up, how presets work

Journals reject figures for formatting before they read the science: wrong width, fonts
too small at print size, raster where vector is required, RGB where CMYK is wanted. This
file tells you **what to pin down** and how the configurable preset system works. Journal
rules change — when in doubt, fetch the journal's current "Guide for Authors" /
"Artwork/Figure guidelines" and confirm with the user rather than trusting memory.

## The checklist to fill in per target journal

| Spec | Why it matters | Typical values |
|---|---|---|
| **Column widths** (single / 1.5 / double) in **mm** | Figures are sized to the column; design at final print size | single ≈ 85–90 mm, double ≈ 170–183 mm |
| **Max height** | Page limit | ~ 230–247 mm |
| **Min font size** at final size | Readability after scaling | 5–8 pt (often 7 pt) |
| **Font family** | House style; embedding | Arial / Helvetica (sans) most common |
| **File format** | Vector vs raster | PDF/EPS/AI for line art; TIFF/PNG for images |
| **Resolution (raster)** | Print quality | ≥300 dpi (color/halftone), ≥600–1200 dpi (line/combination) |
| **Color mode** | Print pipeline | RGB increasingly accepted; some still want CMYK |
| **Line weight (min)** | Lines vanish when scaled | ≥ 0.25–0.5 pt (~0.75 px) |
| **Panel labels** | Multi-panel convention | bold lowercase **a b c** (Nature) or uppercase **A B C** (Cell/many) |
| **File naming** | Submission system | often `Figure1.tif`, `Fig1`, etc. |

Design **at final size** (set the figure's physical width to the column width in inches),
so 7 pt really is 7 pt on the page. Don't design huge and shrink — text becomes unreadable.

## How presets work (configurable, not hard-coded)

`assets/presets.json` holds named **starting presets**. Each records figure widths (mm), dpi, font
family and sizes, line widths, venue submission formats, color mode, and panel-label style.
`scripts/figstyle.py` validates the preset, applies the matplotlib-compatible settings, preserves
the requested physical canvas size on export, and can verify raster dimensions. Metadata such as
submission color mode and panel-label case still requires an explicit final-delivery check.

For review, `save_figure()` writes one PNG preview and one PDF vector by default, regardless of
venue. Substitute SVG for PDF when requested. Generate TIFF/JPEG/EPS or other submission-specific
formats only after the analysis is approved and the user or current venue guidance requires them.

The user picks the journal (stage 4). Workflow:
1. `python scripts/figstyle.py --list` to see available presets.
2. If the target journal is present, use it.
3. If not — or if you're unsure the bundled numbers are current — look up the journal's
   guidelines, **add a new preset** to `assets/presets.json` (copy an existing block, edit
   the numbers), and confirm with the user. Adding presets is the intended extension point;
   the bundled ones are a starting library, not an authority.

The bundled `generic` preset is a practical review default (300/600 dpi, vector PDF + PNG preview,
Arial preference, colorblind-safe palette) for theses, preprints, or an unknown venue. Example
journal-family presets (`nature`, `science`, `cell`, `ieee`, `elsevier`, `plos`) are convenience
starting points, not certifications of compliance. Verify them against the exact journal's live
guidelines and record the source/date before final submission.

## Common gotchas
- **Fonts not embedded** → text reflows on the editor's machine. Export PDF with fonts
  embedded; for matplotlib set `pdf.fonttype = 42` (TrueType) so text stays editable and
  embeds. (`figstyle.py` does this.)
- **Designed too big** → 12 pt looks fine on screen but the journal scales the figure down
  and it's now 4 pt. Always preview at column width.
- **JPEG for line art** → compression artifacts around text/lines. Use PDF/TIFF/PNG.
- **Rainbow colormaps / red-green encoding** → fail colorblind and grayscale printing.
- **Inconsistent fonts/sizes across figures** in the same paper → use one preset for all.
- **Missing scale bars** on micrographs, **missing axis units**, **panel labels not bold**.
