# Plotting Stacks — publication-quality idioms

Four stacks, one job: a clean, honest, print-ready figure reproducible from raw data. Pick
the one that fits the figure and the user.

- **matplotlib** — the foundation. Maximum control over size, dpi, fonts, vector export.
  Everything else builds on it. Use directly for fine-tuned print figures and multi-panel
  layouts.
- **seaborn** — statistical charts on top of matplotlib with far less code (box, violin,
  strip, swarm, regression, heatmap, faceting). Default for most static statistical figures.
  Returns matplotlib objects, so you still apply the journal preset and fine-tune.
- **plotnine** — grammar of graphics (ggplot2 syntax) in Python. Use when the user thinks
  in ggplot / layered aesthetics, or for clean faceted/multi-layer figures.
- **plotly** — interactive HTML. Use for supplementary interactive figures, dashboards, or
  when the deliverable is a web page — not for print (print = matplotlib/seaborn/plotnine).

Apply the journal preset first via `scripts/figstyle.py` (it configures matplotlib rcParams,
which seaborn and plotnine's matplotlib backend inherit), then plot.

---

## matplotlib — the print workhorse
```python
import matplotlib.pyplot as plt
from figstyle import apply_preset, save_figure   # bundled helper

apply_preset("nature", column="single")          # sets size, dpi, fonts, line widths
fig, ax = plt.subplots()                          # size comes from the preset
ax.bar(x, means, yerr=sem, capsize=2)
ax.set_xlabel("Condition"); ax.set_ylabel("Expression (a.u.)")
ax.spines[["top", "right"]].set_visible(False)    # de-clutter
save_figure(fig, number="1", preset="nature")     # writes Fig1.png + Fig1.pdf
```
Tips: design at final width; keep `ax.spines` minimal; use constrained layout or explicit subplot
margins to avoid clipping without changing the exported canvas size; annotate significance with
`ax.plot` brackets + `ax.text`; embed fonts (`pdf.fonttype=42`, set by the preset).

## seaborn — statistical charts, less code
```python
import seaborn as sns
from figstyle import apply_preset, save_figure
apply_preset("generic")
ax = sns.boxplot(data=df, x="group", y="value", showfliers=False, width=0.5)
sns.stripplot(data=df, x="group", y="value", color="black", size=2, jitter=0.15, ax=ax)
# add stats annotations with the `statannotations` package if installed
save_figure(ax.figure, number="2", preset="generic")
```
Good defaults: `boxplot/violinplot` + `stripplot`/`swarmplot` overlay to show points;
`sns.set_palette` to a colorblind-safe palette; `sns.relplot`/`catplot` for faceting;
`sns.heatmap`/`clustermap` with a labeled colorbar. For significance brackets use the
`statannotations` library (`Annotator`) — it computes/positions tests for you.

## plotnine — grammar of graphics
```python
from plotnine import *
(ggplot(df, aes("group", "value", fill="group"))
 + geom_violin()
 + geom_jitter(width=0.15, size=0.6)
 + labs(x="Group", y="Value (units)")
 + theme_classic()
 + theme(figure_size=(3.46, 2.6), text=element_text(family="Arial", size=7))
).save("Fig3.pdf", dpi=300)
```
Use when layered aesthetics or faceting (`facet_wrap`/`facet_grid`) express the figure
naturally. Mirror the preset's size/font in `theme()`.

## plotly — interactive supplements
```python
import plotly.express as px
fig = px.scatter(df, x="x", y="y", color="group", trendline="ols")
fig.write_html("FigS1_interactive.html")
fig.write_image("FigS1.pdf", width=900, height=600, scale=2)  # needs kaleido
```
For print export from plotly you need `kaleido`. Prefer matplotlib/seaborn for the
print version and offer plotly only as an interactive extra.

---

## Cross-cutting quality rules
- **Colorblind-safe palettes** by default (viridis/cividis for sequential; ColorBrewer
  "Set2"/Okabe-Ito for categorical). Avoid jet/rainbow and red-green pairs.
- **Vector for line art** (PDF/SVG/EPS), high-dpi raster for images. Set ≥300 dpi.
- **Two review assets by default:** one directly viewable PNG and one vector PDF. Substitute SVG
  for PDF or request other formats only when the user/venue needs them.
- **Embed fonts**; keep text as text (don't outline) so editors can adjust.
- **Direct-label** lines/points instead of a far-off legend when it reduces eye travel.
- **Consistent style across all figures** in a paper — one preset, applied everywhere.
- **Set a random seed** before any jitter/sampling/embedding so the figure is reproducible.
- **Save the script**; record library versions (e.g. `pip freeze > figs/requirements.lock`).
