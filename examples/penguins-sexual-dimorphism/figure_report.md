# Figure & Table Report / 图表报告
### Worked example: Antarctic penguin morphometrics / 案例:南极企鹅形态学

> Produced by **StatMate（统计同学）** from the raw data of Gorman, Williams &
> Fraser (2014). A gallery covering nine chart families and three academic
> three-line (三线表) tables, each with a bilingual caption, annotations, and an
> in-text citation location.
>
> 由 **StatMate（统计同学）** 基于 Gorman 等 (2014) 原始数据生成。涵盖九类图型与三张
> 学术三线表,每项均含中英双语图注、标注与正文引用位置。

## Manuscript / 稿件
- **Source paper / 来源论文:** Gorman KB, Williams TD, Fraser WR (2014). *PLOS ONE* 9(3): e90081.
- **Preset / 预设:** `generic` high-quality (single/double column as noted)
- **Data / 数据:** `data/penguins_raw.csv` — one row = one penguin / 每行一只企鹅
- **Reproduce / 复现:** run `scripts/make_*.py`; figures → `figures/`; seed = 0.

## Asset index / 图表清单
| # | Chart family 图型 | File 文件 | One-line claim 一句话结论 |
|---|---|---|---|
| Fig 1 | box + points | `Fig1.pdf` | Body size separates the three species. 体型区分三物种。 |
| Fig 2 | grouped box | `Fig2.pdf` | Males heavier than females in every species. 各物种雄性更重。 |
| Fig 3 | scatter + regression | `Fig3.pdf` | Culmen length and depth co-vary within species. 物种内喙长喙深正相关。 |
| Fig 4 | raincloud (violin+box+points) | `Fig4.pdf` | Flipper-length distributions differ by species. 鳍长分布按物种不同。 |
| Fig 5 | histogram + ECDF | `Fig5.pdf` | Gentoo body mass is distinctly higher. 巴布亚体重明显更高。 |
| Fig 6 | grouped bar (counts) | `Fig6.pdf` | Species are unevenly distributed across islands. 物种在各岛分布不均。 |
| Fig 7 | correlation heatmap | `Fig7.pdf` | Flipper length and body mass are tightly correlated. 鳍长与体重高度相关。 |
| Fig 8 | PCA biplot | `Fig8.pdf` | Morphometrics separate species in 2D. 形态空间二维上区分物种。 |
| Fig 9 | forest plot | `Fig9.pdf` | Dimorphism effect size is large in all species. 各物种性二态效应量均大。 |
| Table 1 | three-line table | `Table1.docx` | Morphometrics (mean±SD) by species × sex. 形态指标按物种×性别。 |
| Table 2 | three-line table | `Table2.docx` | Sexual-dimorphism test results. 性二态检验结果。 |
| Table 3 | three-line table | `Table3.docx` | Sample composition by species/island/sex. 样本构成。 |

---

## Figure 1 / 图 1 — Body size among species (box + points) / 物种间体型(箱线+散点)
**File:** `figures/Fig1.pdf` — 180 mm, vector + 600 dpi PNG.
**Claim / 论证:** Flipper length and body mass differ among species; Gentoo largest. / 鳍长与体重存在物种差异,巴布亚最大。

**Caption EN:** **Figure 1.** Body size differs among penguin species. (**A**) Flipper length and
(**B**) body mass for Adélie (n=151), Chinstrap (n=68) and Gentoo (n=123); birds missing the
measurement are excluded. Box = median + IQR; whiskers = 1.5×IQR; points = individual birds.
Kruskal–Wallis (A: H=244.9; B: H=217.6; both p<0.001).
**图注 中文:** **图 1。** 企鹅体型存在物种差异。(**A**)鳍长、(**B**)体重,阿德利(n=151)、帽带(n=68)、
巴布亚(n=123);缺测个体已剔除。箱体=中位数+四分位距,须线=1.5×IQR,散点=个体。Kruskal–Wallis 检验(A:H=244.9;B:H=217.6;p 均<0.001)。

**Annotations / 标注:** x=species, y=measurement+units; non-parametric omnibus test; full distribution shown (no error bars); Okabe–Ito colorblind-safe. / x=物种,y=测量值+单位;非参数总体检验;直接展示分布;色盲安全配色。
**Citation / 引用位置:** Results → body-size paragraph: "Gentoo were largest in flipper length and body mass **(Fig. 1)**."
**Repro:** `scripts/make_fig1_morphometrics.py`

## Figure 2 / 图 2 — Sexual size dimorphism (grouped box) / 性体型二态(分组箱线)
**File:** `figures/Fig2.pdf` — 90 mm.
**Claim:** Within every species, males are heavier than females. / 各物种内雄性体重大于雌性。

**Caption EN:** **Figure 2.** Sexual size dimorphism in body mass. Within each species, males (orange)
exceed females (blue). Box = median + IQR; points = birds. Per-species Welch's t-test; ***p<0.001
(Adélie t=13.1, g=2.16; Chinstrap t=5.2, g=1.25; Gentoo t=14.8, g=2.68).
**图注 中文:** **图 2。** 体重的性体型二态。各物种内雄性(橙)大于雌性(蓝)。箱体=中位数+四分位距,散点=个体。
各物种 Welch t 检验;***p<0.001(阿德利 t=13.1,g=2.16;帽带 t=5.2,g=1.25;巴布亚 t=14.8,g=2.68)。

**Annotations:** blue=female, orange=male; Welch t (unequal variance); Hedges' g large in all; ***p<0.001. / 蓝=雌,橙=雄;Welch t;g 均为大效应。
**Citation:** Results → "Sexual dimorphism": "Males were heavier across all species **(Fig. 2; Table 2)**."
**Repro:** `scripts/make_fig2_dimorphism.py`

## Figure 3 / 图 3 — Culmen shape relationship (scatter + fit) / 喙形关系(散点+回归)
**File:** `figures/Fig3.pdf` — 90 mm.
**Claim:** Culmen length and depth are positively related within each species. / 各物种内喙长与喙深正相关。

**Caption EN:** **Figure 3.** Culmen length versus depth, with per-species ordinary-least-squares fits
(lines) and 95% confidence bands. The relationship is positive within each species, although pooling
all species would reverse the slope (Simpson's paradox) — hence species-specific fits.
**图注 中文:** **图 3。** 喙长与喙深关系,按物种分别拟合最小二乘回归(实线)及 95% 置信带。各物种内呈正相关;
若合并全部物种则斜率反转(辛普森悖论),故采用分物种拟合。

**Annotations:** x=culmen length (mm), y=culmen depth (mm); shaded = 95% CI of fitted mean; points = birds. / x=喙长,y=喙深;阴影=拟合均值 95% 置信带。
**Citation:** Results → trait covariation: "Within species, deeper culmens accompanied longer culmens **(Fig. 3)**."
**Repro:** `scripts/make_fig3_scatter_regression.py`

## Figure 4 / 图 4 — Flipper-length distribution (raincloud) / 鳍长分布(云雨图)
**File:** `figures/Fig4.pdf` — 90 mm.
**Claim:** Flipper-length distributions are well separated across species. / 三物种鳍长分布彼此分离。

**Caption EN:** **Figure 4.** Flipper length by species shown as a raincloud: half-violin (kernel density),
box (median + IQR) and jittered points (individual birds). Gentoo show clearly longer flippers.
**图注 中文:** **图 4。** 各物种鳍长的云雨图:半小提琴(核密度)、箱体(中位数+四分位距)与抖动散点(个体)。
巴布亚企鹅鳍长明显更大。

**Annotations:** density + summary + raw data combined; n = 152/68/124. / 密度、汇总、原始数据三合一。
**Citation:** Results → flipper length: "Flipper-length distributions barely overlapped between Gentoo and the others **(Fig. 4)**."
**Repro:** `scripts/make_fig4_raincloud.py`

## Figure 5 / 图 5 — Body-mass distribution (histogram + ECDF) / 体重分布(直方图+ECDF)
**File:** `figures/Fig5.pdf` — 180 mm.
**Claim:** Body-mass distributions show Gentoo shifted to higher values. / 体重分布中巴布亚整体偏高。

**Caption EN:** **Figure 5.** Body-mass distribution by species. (**A**) Overlaid histograms (22 equal-width bins);
(**B**) empirical cumulative distribution functions. The ECDF (no binning choice) shows Gentoo's distribution
shifted entirely rightward of Adélie and Chinstrap.
**图注 中文:** **图 5。** 各物种体重分布。(**A**)叠加直方图(22 个等宽区间);(**B**)经验累积分布函数。
ECDF(无需选择分箱)显示巴布亚整体右移于阿德利与帽带。

**Annotations:** A: bin width stated; B: ECDF is binning-free and ideal for comparison. / A 注明分箱;B 为无分箱、利于比较。
**Citation:** Results → mass distribution: "Gentoo body mass scarcely overlapped the other species **(Fig. 5)**."
**Repro:** `scripts/make_fig5_distribution.py`

## Figure 6 / 图 6 — Species across islands (grouped bar) / 各岛物种分布(分组柱状)
**File:** `figures/Fig6.pdf` — 90 mm.
**Claim:** Species occupy islands unevenly. / 物种在各岛分布不均。

**Caption EN:** **Figure 6.** Number of penguins sampled per island and species (counts labelled on bars).
Bars start at zero. Species and island are strongly associated (χ²≈300, p<0.001); Gentoo were sampled
only on Biscoe, Chinstrap only on Dream.
**图注 中文:** **图 6。** 各岛、各物种采样的企鹅数量(柱顶标注计数)。柱从零起。物种与岛屿强关联(χ²≈300,p<0.001);
巴布亚仅见于 Biscoe,帽带仅见于 Dream。

**Annotations:** counts (bars from zero); χ² test of association; n labelled. / 计数(柱从零);χ² 关联检验。
**Citation:** Methods/Results → sampling: "Sampling by island and species is shown in **Fig. 6** (see also **Table 3**)."
**Repro:** `scripts/make_fig6_bar_counts.py`

## Figure 7 / 图 7 — Trait correlations (heatmap) / 性状相关(热图)
**File:** `figures/Fig7.pdf` — 90 mm.
**Claim:** Body mass tracks flipper length; culmen depth runs opposite. / 体重随鳍长上升,喙深方向相反。

**Caption EN:** **Figure 7.** Pearson correlations among four morphometric traits (pooled, complete cases).
Diverging colormap centred at r=0; r annotated per cell. Flipper length and body mass are most strongly
correlated (r=0.87); culmen depth correlates negatively with the others.
**图注 中文:** **图 7。** 四项形态性状的 Pearson 相关(合并样本,完整观测)。发散色标以 r=0 为中心,各格标注 r。
鳍长与体重相关最强(r=0.87);喙深与其余性状负相关。

**Annotations:** diverging colormap centred at 0; r in each cell; colorbar labelled. / 发散色标居中于 0;每格标 r;色标带标签。
**Citation:** Results → trait structure: "Flipper length and body mass were tightly coupled **(Fig. 7)**."
**Repro:** `scripts/make_fig7_corr_heatmap.py`

## Figure 8 / 图 8 — Morphometric space (PCA biplot) / 形态空间(PCA 双标图)
**File:** `figures/Fig8.pdf` — 90 mm.
**Claim:** The four traits separate species in two dimensions. / 四性状在二维上区分物种。

**Caption EN:** **Figure 8.** Principal component analysis of four z-scored morphometric traits (complete cases).
Points are birds coloured by species; arrows are trait loadings. PC1 (69% variance) separates Gentoo from
Adélie/Chinstrap; PC2 (19%) reflects culmen depth.
**图注 中文:** **图 8。** 四项标准化形态性状的主成分分析(完整观测)。散点为个体并按物种着色,箭头为性状载荷。
PC1(解释 69% 方差)区分巴布亚与阿德利/帽带;PC2(19%)主要反映喙深。

**Annotations:** traits z-scored before PCA; % variance on axes; loadings as biplot arrows. / PCA 前标准化;轴标注方差占比;载荷以箭头表示。
**Citation:** Results → multivariate: "A PCA of morphometrics cleanly separated the species **(Fig. 8)**."
**Repro:** `scripts/make_fig8_pca.py`

## Figure 9 / 图 9 — Dimorphism effect sizes (forest plot) / 性二态效应量(森林图)
**File:** `figures/Fig9.pdf` — 90 mm.
**Claim:** The male–female body-mass effect is large in every species. / 各物种雌雄体重差均为大效应。

**Caption EN:** **Figure 9.** Standardized male–female body-mass difference (Hedges' g) per species with
95% confidence intervals; dashed line at g=0 (no difference). All intervals lie well above zero
(Adélie 2.16 [1.75, 2.57]; Chinstrap 1.25 [0.73, 1.77]; Gentoo 2.68 [2.19, 3.18]).
**图注 中文:** **图 9。** 各物种雄性减雌性体重的标准化差异(Hedges' g)及 95% 置信区间;虚线为 g=0(无差异)。
所有区间均明显大于零(阿德利 2.16 [1.75, 2.57];帽带 1.25 [0.73, 1.77];巴布亚 2.68 [2.19, 3.18])。

**Annotations:** point = g, line = 95% CI, dashed reference at 0; positive = males larger. / 点=g,线=95% CI,虚线参考 0;正值表示雄性更大。
**Citation:** Discussion → effect magnitude: "Dimorphism was not merely significant but large **(Fig. 9)**."
**Repro:** `scripts/make_fig9_forest.py`

---

## Table 1 / 表 1 — Morphometric summary (three-line) / 形态指标汇总(三线表)
**File:** `figures/Table1.docx` (+ `.csv`, `.md`).
**Caption EN:** **Table 1.** Morphometric measurements (mean ± SD) by species and sex. n = number of penguins. Data: Gorman et al. (2014).
**表注 中文:** **表 1。** 形态测量值(均值 ± 标准差),按物种和性别。n = 企鹅数量。数据:Gorman 等 (2014)。
**Annotations:** one statistic style per cell (mean ± SD); n stated; units in headers. / 每格统一为均值±SD;注明 n;表头含单位。
**Citation:** Results, opening: "Morphometrics by species and sex are summarized in **Table 1**."
**Repro:** `scripts/make_table1_summary.py`

## Table 2 / 表 2 — Sexual dimorphism tests (three-line) / 性二态检验(三线表)
**File:** `figures/Table2.docx` (+ `.csv`).
**Caption EN:** **Table 2.** Sexual dimorphism by species and trait. Female and male mean ± SD, Welch's t,
degrees of freedom, p, and Hedges' g with 95% CI (positive = males larger). Data: Gorman et al. (2014).
**表注 中文:** **表 2。** 各物种、各性状的性二态。雌、雄均值±SD,Welch t,自由度,p,以及带 95% CI 的 Hedges' g
(正值表示雄性更大)。数据:Gorman 等 (2014)。
**Annotations:** Welch t (unequal variance), Welch–Satterthwaite df; effect size + CI per row. / Welch t(不等方差)、Welch–Satterthwaite 自由度;每行含效应量与 CI。
**Citation:** Results → "Sexual dimorphism": cite alongside Fig. 2 for exact statistics. / 与图 2 并列,提供精确统计量。
**Repro:** `scripts/make_table2_dimorphism_stats.py`

## Table 3 / 表 3 — Sample composition (three-line) / 样本构成(三线表)
**File:** `figures/Table3.docx` (+ `.csv`).
**Caption EN:** **Table 3.** Sample composition by species, island and sex (number of penguins).
Unknown = sex not determined. Data: Gorman et al. (2014).
**表注 中文:** **表 3。** 样本构成,按物种、岛屿和性别(企鹅数量)。Unknown = 性别未定。数据:Gorman 等 (2014)。
**Annotations:** raw counts; row totals + grand total; documents the analysed sample. / 原始计数;含行合计与总计;用于说明分析样本。
**Citation:** Methods → study sample: "The analysed sample is detailed in **Table 3**."
**Repro:** `scripts/make_table3_composition.py`
