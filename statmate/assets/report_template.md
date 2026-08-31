# Figure & Table Report / 图表报告

> Markdown fallback for the figure report (the default deliverable is a Word `.docx` built by
> `scripts/report_docx.py`). **Match the report's language to the user's choice** — keep only
> the English caption for an English-only report, only the Chinese for 全中文, or both for a
> bilingual report. This template shows the bilingual form; drop one language as needed.
>
> Fill one block per figure and table, in numbered order. The "Citation location" tells the
> author exactly where to cite each item in the manuscript. Delete these instruction lines in
> the final report.
>
> 每个图/表填写一个区块,按编号顺序排列。图注与标注中英双语。"引用位置"指明在正文中
> 何处引用。完成后删除本说明行。

---

## Manuscript / 稿件
- **Title / 标题:**
- **Target journal / 目标期刊:**
- **Preset used / 使用的预设:** (e.g. `nature`, single column)
- **Date / 日期:**

## Asset index / 图表清单
| # | Type 类型 | File 文件 | One-line claim 一句话结论 |
|---|---|---|---|
| Fig 1 | figure | Fig1.pdf | |
| Fig 2 | figure | Fig2.pdf | |
| Table 1 | table | Table1.docx | |

---

## Figure 1 / 图 1 — <short title / 简短标题>

**File / 文件:** `Fig1.pdf` (+ `Fig1.png` preview) — <format>, <dpi>, <width> mm

**Claim / 论证:** This figure shows that … / 本图表明……

**Review status / 审核状态:** draft | needs-author-decision | approved | final

**Method rationale / 方法依据:** <Why the method matches the design, outcome, analysis unit,
assumptions, and estimand. / 方法为何适配研究设计、结局、分析单位、假设和目标估计量。>

### Caption / 图注
**EN:** Figure 1. <Full caption: what is plotted, groups, what each element means.>
Data are <mean ± SEM / median [IQR]>; n = <n, unit of analysis>. <Test> was used;
*p < 0.05, **p < 0.01, ***p < 0.001; ns, not significant.

**中文:** 图 1。<完整图注:绘制了什么、分组、各元素含义。>数据为<均值 ± 标准误 /
中位数 [四分位距]>;n = <样本量,分析单位>。采用<统计检验>;*p < 0.05,**p < 0.01,
***p < 0.001;ns 表示无显著性差异。

### Annotations / 标注说明
- **Panels / 分图:** A = …, B = … / A = ……,B = ……
- **Axes / 坐标轴:** x = … (units), y = … (units)
- **Error bars / 误差棒:** <SD | SEM | 95% CI> — define explicitly / 明确定义
- **n / 样本量:** <n per group, what one observation is>
- **Statistics / 统计:** <test, paired/unpaired, correction, effect size + CI>
- **Significance markers / 显著性标记:** <which comparisons, convention>
- **Color / 颜色:** <palette; colorblind-safe? grayscale-safe?>
- **Scale choices / 标度:** <log axis? broken axis? — note if it affects interpretation>

### Scientific interpretation / 科研结果解读
- **Result / 结果:** <effect direction, magnitude, CI, adjusted p/q if relevant>
- **Robustness / 稳健性:** <diagnostics and sensitivity analyses>
- **Relevance / 意义:** <scientific/clinical importance distinct from significance>
- **Limitations / 局限:** <design, missingness, multiplicity, precision, model dependence>
- **Manuscript wording / 论文表述:** <one cautious result sentence>

### How to read / 如何阅读
1. <Read the axes/units or table title/denominators.>
2. <Identify what every point/line/box/error bar or row/column represents.>
3. <Inspect the raw pattern, then the estimate and interval.>
4. <Read n, model/test, correction, and footnotes.>
- **Common misreading / 常见误读:** <likely mistake>
- **Plain-language takeaway / 通俗结论:** <one sentence>
- **Cannot conclude / 不能据此得出:** <explicit boundary>

### Citation location / 引用位置
- **Section / 章节:** Results → <subsection> / 结果 → <小节>
- **Sentence / 句子:** "…the effect was significant **(Fig. 1A)**." Insert after this
  sentence. / 在该句后引用。

### Reproducibility / 可复现性
- **Data source / 数据来源:** `<path/to/data.csv>` (sheet/columns: …)
- **Script / 脚本:** `<path/to/make_fig1.py>` (seed = …)
- **Key libraries / 主要依赖:** matplotlib x.y, seaborn x.y, scipy x.y

---

## Table 1 / 表 1 — <short title / 简短标题>

**File / 文件:** `Table1.docx` / `Table1.csv`

> Choose final table format only after content approval: Word three-line table by default;
> add Excel, CSV, or LaTeX only when requested.

**Review status / 审核状态:** draft | needs-author-decision | approved | final

**Method rationale / 方法依据:** <Why these summaries/models answer the table's question.>

### Caption / 表注
**EN:** Table 1. <What the table summarizes; per-cell statistic; n; test footnotes.>
**中文:** 表 1。<表格汇总内容;每格统计量;样本量;检验脚注。>

### Annotations / 标注说明
- **Columns / 列:** <column = meaning, units, statistic shown>
- **Summary statistic / 汇总统计:** <mean ± SD | median [IQR] | n (%)>
- **Tests / 检验:** <test per row/column; correction>
- **Abbreviations / 缩写:** <define every abbreviation>

### Scientific interpretation / 科研结果解读
- **Result / 结果:** <main estimate and uncertainty>
- **Limitations / 局限:** <sample, missingness, adjustment, multiplicity>

### How to read / 如何阅读
1. <Read title, analysis population, and footnotes.>
2. <Confirm each denominator and summary convention.>
3. <Read effect estimate and CI before the p-value.>
4. <Check reference group, adjustment set, model n/events, and correction.>
- **Common misreading / 常见误读:** <likely mistake>
- **Cannot conclude / 不能据此得出:** <explicit boundary>

### Citation location / 引用位置
- **Section / 章节:** <e.g. Results, baseline characteristics / 结果,基线特征>
- **Sentence / 句子:** "Baseline characteristics are summarized in **Table 1**." 

### Reproducibility / 可复现性
- **Data source / 数据来源:** `<path/to/data.csv>`
- **Script / 脚本:** `<path/to/make_table1.py>`

---

<!-- Duplicate the Figure/Table blocks above for every additional asset, in order. -->
<!-- 为每个后续图表复制上述区块,按顺序排列。 -->
