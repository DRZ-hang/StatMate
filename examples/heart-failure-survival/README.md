# Example — Survival of Heart-Failure Patients / 案例:心力衰竭患者生存分析

A **statistics-heavy** worked example of **StatMate（统计同学）**, run end-to-end on a
real, openly licensed clinical dataset. Where the [penguin example](../penguins-sexual-dimorphism/)
shows chart *variety*, this one shows statistical *depth*: survival analysis, regression
modelling, and predictive evaluation. / 这是 **StatMate（统计同学）** 的**统计较重**完整案例，
基于真实、开放许可的临床数据集端到端运行。企鹅案例展示图型**多样性**,本案例展示统计**深度**:
生存分析、回归建模与预测评估。

> **New v2 reference demo / 全新 v2 参考演示:** [open the audited workflow](v2_demo/) — study-design map, raw-data audit, frozen plan, real computation, diagnostics, PNG/PDF pairs, reviewed three-line tables, bilingual teaching report, validation record, and file-hash manifest. / [进入带完整审计链的 v2 演示](v2_demo/)。

## What this shows / 演示内容

Following the skill's workflow on 299 heart-failure patients (96 deaths over a median 115-day
follow-up): read the data → frame each figure → pick the right statistics → render → self-check
→ export → bilingual report. / 在 299 例心衰患者(随访中位 115 天、96 例死亡)上遵循技能工作流。

| Asset | File | Chart family / Statistics |
|---|---|---|
| **Fig 1** | [`Fig1.png`](figures/Fig1.png) | histogram + box — cohort & follow-up overview |
| **Fig 2** | [`Fig2.png`](figures/Fig2.png) | **Kaplan–Meier** + at-risk table, log-rank test |
| **Fig 3** | [`Fig3.png`](figures/Fig3.png) | grouped box — predictors by outcome (Mann–Whitney U) |
| **Fig 4** | [`Fig4.png`](figures/Fig4.png) | **Cox proportional-hazards** forest plot (HR, 95% CI) |
| **Fig 5** | [`Fig5.png`](figures/Fig5.png) | Spearman correlation heatmap |
| **Fig 6** | [`Fig6.png`](figures/Fig6.png) | **logistic ROC**, 5-fold cross-validated AUC |
| **Table 1** | [`Table1.docx`](figures/Table1.docx) | three-line (三线表) — baseline characteristics by outcome |
| **Table 2** | [`Table2.docx`](figures/Table2.docx) | three-line — multivariable Cox model |
| **Report — English** | [`Figure_Report_EN.docx`](Figure_Report_EN.docx) | figures embedded, English-only |
| **Report — bilingual** | [`Figure_Report.docx`](Figure_Report.docx) | figures embedded, 中文 + English |
| **Report — 中文** | [`Figure_Report_ZH.docx`](Figure_Report_ZH.docx) | figures embedded, Chinese-only / 全中文 |
| **Report (md)** | [`figure_report.md`](figure_report.md) | Markdown version (bilingual) |

| | | |
|:---:|:---:|:---:|
| ![Fig2](figures/Fig2.png) | ![Fig4](figures/Fig4.png) | ![Fig6](figures/Fig6.png) |
| Kaplan–Meier survival | Cox hazard ratios | cross-validated ROC |

**The statistical story / 统计叙事:** lower ejection fraction predicts worse survival
(Fig 2); the deceased had lower EF and higher creatinine (Fig 3); both are independent
hazards after adjustment (Fig 4, Table 2); and those same two features predict death almost
as well as the full clinical panel (Fig 6) — reproducing the source paper's headline finding.

## Reproduce it / 复现

```bash
pip install -r ../../statmate/requirements-demo.txt   # includes lifelines, scikit-learn, python-docx
cd scripts
for f in make_fig*.py; do python "$f"; done
for f in make_table*.py; do python "$f"; done
python make_report.py                    # writes the report in EN, bilingual, and 中文
# or pick one language:
STATMATE_LANG=en python make_report.py   # en | zh | bilingual
```

Outputs are written to `figures/`. Random seeds are fixed (cross-validation, jitter) for
reproducibility. / 输出写入 `figures/`,交叉验证与抖动均固定随机种子。

## Files / 文件

```
heart-failure-survival/
├── data/heart_failure_clinical_records.csv   # raw data (see attribution below)
├── scripts/
│   ├── _common.py                            # load + label data; re-exports the three-line helper
│   ├── make_fig1_cohort_overview.py
│   ├── make_fig2_kaplan_meier.py             # lifelines KM + log-rank
│   ├── make_fig3_predictors_boxplot.py
│   ├── make_fig4_cox_forest.py               # lifelines Cox PH
│   ├── make_fig5_correlation.py
│   ├── make_fig6_roc.py                       # scikit-learn logistic + CV ROC
│   ├── make_table1_baseline.py
│   ├── make_table2_cox.py
│   └── make_report.py                         # assemble the Word report (en / zh / bilingual)
├── figures/                                   # generated Fig1–6 + Table1–2
├── Figure_Report_EN.docx                      # ★ Word report — English only
├── Figure_Report.docx                         # ★ Word report — bilingual
├── Figure_Report_ZH.docx                      # ★ Word report — 中文
└── figure_report.md                           # report in Markdown (bilingual)
```

---

## Source & attribution / 来源与署名

Please keep this attribution if you reuse the example. / 转用时请保留以下署名。

**Paper / 论文** (open access, **CC BY 4.0**):

> Chicco D, Jurman G (2020). Machine learning can predict survival of patients with heart
> failure from serum creatinine and ejection fraction alone. *BMC Medical Informatics and
> Decision Making* 20, 16. https://doi.org/10.1186/s12911-020-1023-5

**Original data collection / 原始数据采集:**

> Ahmad T, Munir A, Bhatti SH, Aftab M, Raza MA (2017). Survival analysis of heart failure
> patients: A case study. *PLOS ONE* 12(7): e0181001. https://doi.org/10.1371/journal.pone.0181001

**Dataset distribution / 数据分发** — UCI Machine Learning Repository, "Heart failure clinical
records" (dataset 519), licensed **CC BY 4.0**:
https://archive.ics.uci.edu/dataset/519/heart+failure+clinical+records

`data/heart_failure_clinical_records.csv` is the unmodified UCI file (299 patients, 13 fields;
`platelets` is rescaled to ×10³/µL only at analysis time, not in the stored file). The figures,
models and analysis here are our own work built from that raw data. / 存储文件为 UCI 原始文件未经
修改;血小板仅在分析时换算为 ×10³/µL。图表与建模为基于原始数据的再创作。

### License note / 许可说明
Both the paper and the dataset are **CC BY 4.0** → free to reuse and redistribute with credit
(given above). This example's **code** follows the repository's MIT license.
论文与数据均为 CC BY 4.0,署名即可再分发;本案例代码遵循仓库 MIT 许可。
