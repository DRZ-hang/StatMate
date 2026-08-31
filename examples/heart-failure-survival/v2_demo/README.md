# StatMate demo — Heart-failure prognosis / 心衰预后分析

This is the repository's reference implementation of the **v2 evidence workflow**. It uses the unchanged public UCI CSV cited by Ahmad et al. (2017) and Chicco & Jurman (2020), runs every statistic through saved Python code, and delivers both the scientific result and a beginner-readable guide to each figure and table.

这是本仓库 **v2 证据工作流**的参考实现。它使用 Ahmad 等（2017）与 Chicco、Jurman（2020）引用的同一份公开 UCI 原始 CSV；所有统计量均由保存的 Python 代码真实计算，并同时交付科研解读与逐图逐表阅读教学。

| Automated QA / 自动 QA | Manifest / 清单 | Scientific review / 科学审查 |
|:---:|:---:|:---:|
| **PASS** | **33/33 verified** | **needs-author-decision** |

## Result at a glance / 核心结果

- Source: 299 patients, 96 observed deaths, median follow-up 115 days; no missing cells or exact duplicate rows.
- Kaplan–Meier curves differed across prespecified EF groups (overall log-rank p<0.001).
- Prespecified adjusted Cox model: EF per +5 percentage points HR 0.79 (95% CI 0.72–0.87); serum creatinine per +1 mg/dL HR 1.36 (95% CI 1.18–1.55); C-index 0.73.
- The EF covariate-level proportional-hazards diagnostic was p=0.025. A global diagnostic and
  graphical residual review remain pending, so the Cox assets and package are explicitly marked
  `needs-author-decision` rather than `final`.
- Exploratory repeated 5-fold CV: full 11-feature logistic model AUC 0.766 (SD 0.061), versus 0.757 (SD 0.063) for creatinine + EF. `time` is excluded to prevent follow-up leakage.
- These are observational associations and internal predictions, not causal or deployment claims.

## Reference-run outputs / 参考运行产物

| Asset | Preview | Vector / table |
|---|---|---|
| Figure 1 — Kaplan–Meier + risk table | [PNG](06_final/figures/Fig1.png) | [PDF](06_final/figures/Fig1.pdf) |
| Figure 2 — adjusted Cox forest | [PNG](06_final/figures/Fig2.png) | [PDF](06_final/figures/Fig2.pdf) |
| Figure 3 — ROC + calibration | [PNG](06_final/figures/Fig3.png) | [PDF](06_final/figures/Fig3.pdf) |
| Table 1 — cohort characteristics | [CSV](06_final/tables/Table1.csv) | [three-line DOCX](06_final/tables/Table1.docx) |
| Table 2 — Cox model + PH diagnostic | [CSV](06_final/tables/Table2.csv) | [three-line DOCX](06_final/tables/Table2.docx) |
| Illustrated teaching handoff | [English DOCX](06_final/Heart_Failure_v2_Report.docx) | [PDF snapshot](06_final/Heart_Failure_v2_Report.pdf)\* |
| QA + provenance | [validation](06_final/validation_report.md) | [manifest](06_final/manifest.json) |

\* The script regenerates the DOCX. The checked-in PDF was re-exported from the current DOCX and
visually reviewed page by page. Because `run_demo.py` does not create that PDF, it remains outside
the automated manifest.

### Figure 1 — Kaplan–Meier + risk table / 生存曲线与风险人数

![](06_final/figures/Fig1.png)

| Figure 2 — Cox model (`needs-author-decision`) | Figure 3 — exploratory internal prediction |
|:---:|:---:|
| ![](06_final/figures/Fig2.png) | ![](06_final/figures/Fig3.png) |

The demo retains stable package paths under `06_final/`; the explicit review state controls
scientific readiness. The current package-level state is `needs-author-decision`, not `final`.

演示为保持路径稳定，仍把产物放在 `06_final/`；真正决定科学审核状态的是显式 review
state。当前整包是 `needs-author-decision`，不是 `final`。

## The auditable path / 可审计路径

```text
v2_demo/
├── 01_intake/study_design.md              # question, estimand, claim boundary
├── 02_audit/                              # source audit JSON/MD + clinical checks
├── 03_plan/analysis_plan.md               # frozen before model execution
├── 04_code/run_demo.py                    # one-command real-data computation
├── 05_results/                            # machine-readable statistics
└── 06_final/                              # reviewed figures, tables, report, QA, manifest
```

The primary analysis respects the time-to-event structure. Binary logistic prediction is retained only as an explicitly exploratory comparison with the source paper, and its unequal-follow-up limitation is repeated in the plan, captions, report, and validation record.

主要分析保留了时间—事件结构。为了与来源论文的核心主张进行演示性比较，另做二分类逻辑回归；但该部分明确标为探索性，并在分析计划、图注、报告和验证记录中反复提示“不等随访被压缩为二分类结局”的局限。

## Reproduce / 复现

From the repository root:

```bash
python -m venv .venv
# Windows: .venv\Scripts\python -m pip install -r statmate/requirements-demo.txt
# macOS/Linux: .venv/bin/python -m pip install -r statmate/requirements-demo.txt
# Windows:
.venv\Scripts\python examples/heart-failure-survival/v2_demo/04_code/run_demo.py
# macOS/Linux:
.venv/bin/python examples/heart-failure-survival/v2_demo/04_code/run_demo.py
```

The demo regenerates and immediately verifies its manifest. To verify it again without rerunning the
analysis:

```bash
python statmate/scripts/analysis_manifest.py verify examples/heart-failure-survival/v2_demo/06_final/manifest.json
```

`statmate/requirements-demo.txt` declares the supported demo dependencies; the adjacent
`requirements-reference.txt` records the direct package versions used for the checked-in reference
run. The raw CSV is never overwritten. Randomized validation uses seed `20260816`.

## Attribution / 署名

- Ahmad T, Munir A, Bhatti SH, Aftab M, Raza MA (2017). *Survival analysis of heart failure patients: A case study.* PLOS ONE 12(7): e0181001. https://doi.org/10.1371/journal.pone.0181001
- Chicco D, Jurman G (2020). *Machine learning can predict survival of patients with heart failure from serum creatinine and ejection fraction alone.* BMC Medical Informatics and Decision Making 20:16. https://doi.org/10.1186/s12911-020-1023-5
- UCI Machine Learning Repository, Heart Failure Clinical Records, DOI 10.24432/C5Z89R, CC BY 4.0.
