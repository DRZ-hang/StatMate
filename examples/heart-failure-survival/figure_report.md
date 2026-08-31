# Figure & Table Report / 图表报告
### Worked example: Survival of heart-failure patients / 案例:心力衰竭患者生存分析

> Produced by **StatMate（统计同学）** from the raw clinical records used in
> Chicco & Jurman (2020). A statistics-heavy walk-through: Kaplan–Meier survival,
> log-rank, multivariable Cox regression, non-parametric group tests, correlation,
> and cross-validated logistic ROC — six figures and two three-line (三线表) tables,
> each with a bilingual caption, annotations, and an in-text citation location.
>
> 由 **StatMate（统计同学）** 基于 Chicco & Jurman (2020) 的原始临床数据生成。统计较重的
> 完整演示:Kaplan–Meier 生存曲线、log-rank、多因素 Cox 回归、非参数组间检验、相关分析、
> 交叉验证 Logistic ROC——六图两表(三线表),均含中英双语图注、标注与正文引用位置。

## Manuscript / 稿件
- **Source paper / 来源论文:** Chicco D, Jurman G (2020). *BMC Med Inform Decis Mak* 20: 16.
- **Cohort / 队列:** 299 heart-failure patients; 96 deaths (32%); follow-up median 115 days (range 4–285). / 299 例心衰患者;96 例死亡(32%);随访中位 115 天(范围 4–285)。
- **Preset / 预设:** `generic` (single/double column as noted).
- **Data / 数据:** `data/heart_failure_clinical_records.csv` — one row = one patient; `time` = follow-up days; `death_event` = 1 if died (else censored). / 每行一例患者;`time` 为随访天数;`death_event`=1 为死亡(否则删失)。

## Asset index / 图表清单
| # | Chart family 图型 | File 文件 | One-line claim 一句话结论 |
|---|---|---|---|
| Fig 1 | hist + box (overview) | `Fig1.pdf` | Events accrue over variable follow-up → use survival analysis. 事件随不等随访累积→需生存分析。 |
| Fig 2 | Kaplan–Meier + risk table | `Fig2.pdf` | Lower ejection fraction → worse survival. 射血分数越低生存越差。 |
| Fig 3 | grouped box | `Fig3.pdf` | Deceased had lower EF, higher creatinine. 死亡者 EF 更低、肌酐更高。 |
| Fig 4 | Cox forest | `Fig4.pdf` | Independent hazards: age, EF, creatinine… 独立风险:年龄、EF、肌酐等。 |
| Fig 5 | correlation heatmap | `Fig5.pdf` | Predictors are weakly correlated (little collinearity). 预测因子相关弱(共线性低)。 |
| Fig 6 | ROC (cross-validated) | `Fig6.pdf` | Two features ≈ full model for predicting death. 两特征≈全模型。 |
| Table 1 | three-line | `Table1.docx` | Baseline characteristics by survival status. 按结局的基线特征。 |
| Table 2 | three-line | `Table2.docx` | Multivariable Cox model (HR [95% CI]). 多因素 Cox 模型。 |

---

## Figure 1 / 图 1 — Cohort overview / 队列概览
**File:** `figures/Fig1.pdf` — 180 mm.
**Claim:** Deaths occur throughout a variable-length follow-up, so survival (time-to-event) methods are required rather than a simple death-rate comparison. / 死亡发生于长短不一的随访期内,故需时间-事件(生存)分析而非简单比较死亡率。

**Caption EN:** **Figure 1.** Study cohort (n = 299; 96 deaths). (**A**) Age distribution by outcome.
(**B**) Follow-up time by outcome (box = median + IQR; points = patients). Patients who survived were
censored at longer follow-up times than the times at which deaths occurred, motivating time-to-event analysis.
**图注 中文:** **图 1。** 研究队列(n = 299;96 例死亡)。(**A**)年龄分布按结局。(**B**)随访时间按结局
(箱体=中位数+四分位距,散点=患者)。生存者在更长随访时点被删失,死亡则分布于随访全程,故采用时间-事件分析。

**Annotations:** A: overlaid histograms; B: box + points; outcome colour = blue (survived) / orange (died). / A 叠加直方图;B 箱+散点;蓝=生存,橙=死亡。
**Citation:** Methods/Results → cohort description: "Of 299 patients, 96 (32%) died over a median follow-up of 115 days **(Fig. 1)**."
**Repro:** `scripts/make_fig1_cohort_overview.py`

## Figure 2 / 图 2 — Survival by ejection fraction (Kaplan–Meier) / 按射血分数的生存(KM)
**File:** `figures/Fig2.pdf` — 90 mm.
**Claim:** Patients with reduced ejection fraction have markedly worse survival. / 射血分数降低者生存明显更差。

**Caption EN:** **Figure 2.** Kaplan–Meier survival by ejection-fraction category — reduced (<30%, n=59),
mid-range (30–45%, n=160), preserved (≥45%, n=80) — with 95% confidence bands and numbers at risk,
censored and events below. Survival differed across groups (log-rank p < 0.001).
**图注 中文:** **图 2。** 按射血分数分组的 Kaplan–Meier 生存曲线——降低(<30%,n=59)、中间(30–45%,n=160)、
保留(≥45%,n=80)——含 95% 置信带,下方为风险人数、删失数与事件数。组间生存差异显著(log-rank p < 0.001)。

**Annotations:** EF groups clinically defined; CI bands shown; at-risk/censored/events table; log-rank across 3 groups. / EF 按临床界值分组;含置信带与风险表;3 组 log-rank 检验。
**Citation:** Results → survival: "Reduced ejection fraction was associated with substantially lower survival **(Fig. 2)**."
**Repro:** `scripts/make_fig2_kaplan_meier.py`

## Figure 3 / 图 3 — Key predictors by outcome / 关键预测因子按结局
**File:** `figures/Fig3.pdf` — 180 mm.
**Claim:** The deceased had lower ejection fraction and higher serum creatinine. / 死亡者射血分数更低、血清肌酐更高。

**Caption EN:** **Figure 3.** The two headline predictors by outcome. (**A**) Ejection fraction and
(**B**) serum creatinine in patients who survived versus died. Box = median + IQR; points = patients.
Mann–Whitney U test; ***p < 0.001.
**图注 中文:** **图 3。** 两个核心预测因子按结局。(**A**)射血分数、(**B**)血清肌酐,生存者与死亡者对比。
箱体=中位数+四分位距,散点=患者。Mann–Whitney U 检验;***p < 0.001。

**Annotations:** non-parametric test (creatinine right-skewed); points shown; ***p<0.001. / 非参数检验(肌酐右偏);展示散点。
**Citation:** Results → univariable: "Ejection fraction was lower and creatinine higher among those who died **(Fig. 3; Table 1)**."
**Repro:** `scripts/make_fig3_predictors_boxplot.py`

## Figure 4 / 图 4 — Multivariable Cox model (forest plot) / 多因素 Cox 模型(森林图)
**File:** `figures/Fig4.pdf` — 90 mm.
**Claim:** Adjusting for all covariates, age, low EF and high creatinine independently raise mortality hazard. / 校正全部协变量后,年龄、低 EF、高肌酐独立升高死亡风险。

**Caption EN:** **Figure 4.** Hazard ratios (95% CI) from a multivariable Cox proportional-hazards model
(log scale; reference HR = 1, dashed). Continuous predictors are standardized (HR per 1 SD). Coloured =
significant at p < 0.05. Higher age (HR 1.74), serum creatinine (1.39) and CPK (1.24), and lower ejection
fraction (0.56) independently predicted mortality; anaemia (1.58) and hypertension (1.61) also contributed.
Model concordance index = 0.74.
**图注 中文:** **图 4。** 多因素 Cox 比例风险模型的风险比(95% CI;对数坐标,虚线为参考 HR = 1)。连续变量已标准化
(HR 为每 1 个标准差)。彩色表示 p < 0.05 显著。年龄(HR 1.74)、肌酐(1.39)、CPK(1.24)升高及射血分数降低
(0.56)独立预测死亡;贫血(1.58)与高血压(1.61)亦有贡献。模型一致性指数 = 0.74。

**Annotations:** log-scale HR; continuous per-SD; reference at 1; significant highlighted; C-index reported. / 对数 HR;连续变量按 SD;参考线 1;显著项高亮;报告 C-index。
**Citation:** Results → adjusted analysis: "In the multivariable Cox model, EF, creatinine and age were independent predictors **(Fig. 4; Table 2)**."
**Repro:** `scripts/make_fig4_cox_forest.py`

## Figure 5 / 图 5 — Correlations among predictors / 预测因子间相关
**File:** `figures/Fig5.pdf` — 90 mm.
**Claim:** Continuous predictors are only weakly correlated, so collinearity is not a concern for the model. / 连续预测因子间相关较弱,模型无明显共线性问题。

**Caption EN:** **Figure 5.** Spearman correlations among continuous clinical variables (diverging colormap
centred at ρ = 0; ρ annotated per cell). Correlations are weak (|ρ| ≤ 0.30; strongest: serum sodium–creatinine
ρ = −0.30), indicating little collinearity among the Cox predictors.
**图注 中文:** **图 5。** 连续临床变量间的 Spearman 相关(发散色标以 ρ = 0 为中心,每格标注 ρ)。相关普遍较弱
(|ρ| ≤ 0.30;最强为血清钠–肌酐 ρ = −0.30),表明 Cox 预测因子间共线性很低。

**Annotations:** Spearman (robust to skew); diverging colormap centred at 0; labelled colorbar. / Spearman(抗偏态);发散色标居中于 0。
**Citation:** Results → model diagnostics: "Predictors were weakly correlated, arguing against collinearity **(Fig. 5)**."
**Repro:** `scripts/make_fig5_correlation.py`

## Figure 6 / 图 6 — Two features vs. the full set (ROC) / 两特征 vs 全特征(ROC)
**File:** `figures/Fig6.pdf` — 90 mm.
**Claim:** Serum creatinine + ejection fraction predict in-study death almost as well as all clinical features. / 血清肌酐+射血分数预测院内死亡几乎与全部临床特征一样好。

**Caption EN:** **Figure 6.** Receiver-operating-characteristic curves for predicting in-study death with
logistic regression, using 5-fold cross-validated predicted probabilities. A model with only serum creatinine
and ejection fraction (AUC = 0.75) nearly matched the full clinical-feature model (AUC = 0.76). Follow-up time
was excluded as a predictor to avoid outcome leakage.
**图注 中文:** **图 6。** Logistic 回归预测院内死亡的 ROC 曲线,采用 5 折交叉验证的预测概率。仅用血清肌酐与
射血分数的模型(AUC = 0.75)几乎与全部临床特征模型(AUC = 0.76)持平。随访时间已排除以避免结局泄漏。

**Annotations:** cross-validated (not in-sample) AUC; `time` excluded (leakage); chance diagonal shown. / 交叉验证 AUC(非样本内);排除 `time`(防泄漏);含随机对角线。
**Citation:** Discussion → parsimony: "Two features reproduced most of the full model's discrimination **(Fig. 6)**."
**Repro:** `scripts/make_fig6_roc.py`

---

## Table 1 / 表 1 — Baseline characteristics (three-line) / 基线特征(三线表)
**File:** `figures/Table1.docx` (+ `.csv`).
**Caption EN:** **Table 1.** Baseline characteristics by survival status. Continuous: median [IQR], Mann–Whitney U;
binary: n (%), chi-square. Data: Chicco & Jurman (2020).
**表注 中文:** **表 1。** 按生存状态的基线特征。连续变量:中位数 [四分位距],Mann–Whitney U;二分类:n (%),卡方检验。
数据:Chicco & Jurman (2020)。
**Annotations:** one statistic per row type; n stated per group; p flags univariable differences (unadjusted for follow-up — see Table 2). / 每类一种统计量;注明各组 n;p 为单因素差异(未校正随访,见表 2)。
**Citation:** Results, opening: "Baseline characteristics are summarized in **Table 1**."
**Repro:** `scripts/make_table1_baseline.py`

## Table 2 / 表 2 — Multivariable Cox model (three-line) / 多因素 Cox 模型(三线表)
**File:** `figures/Table2.docx` (+ `.csv`).
**Caption EN:** **Table 2.** Multivariable Cox proportional-hazards model for mortality. HR with 95% CI;
continuous predictors standardized (HR per 1 SD). Concordance index = 0.74; n = 299, events = 96.
Data: Chicco & Jurman (2020).
**表注 中文:** **表 2。** 死亡的多因素 Cox 比例风险模型。HR 及 95% CI;连续变量标准化(HR 为每 1 个标准差)。
一致性指数 = 0.74;n = 299,事件 = 96。数据:Chicco & Jurman (2020)。
**Annotations:** adjusted HRs (all covariates in one model); per-SD continuous; C-index reported. / 校正后 HR(同一模型纳入全部协变量);连续变量按 SD;报告 C-index。
**Citation:** Results → adjusted analysis: exact HRs cited alongside Fig. 4. / 与图 4 并列,提供精确 HR。
**Repro:** `scripts/make_table2_cox.py`
