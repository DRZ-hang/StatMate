<div align="center">

[English](README.md) · **中文**

# 📊 StatMate（统计同学）

### 面向科研 Agent 的证据优先统计工作流。

[![Agent Skill](https://img.shields.io/badge/Agent-Skill-8A2BE2)](statmate/SKILL.md)
[![StatMate tests](https://github.com/DRZ-hang/paper-figures/actions/workflows/statmate-tests.yml/badge.svg)](https://github.com/DRZ-hang/paper-figures/actions/workflows/statmate-tests.yml)
[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

![StatMate：证据优先的科研统计工作流](.github/assets/statmate-hero.svg)

<p align="center">
  <a href="DEMO.zh-CN.md"><strong>▶ 打开 60 秒 Demo</strong></a>
  · <a href="examples/heart-failure-survival/v2_demo/">查看完整审计链</a>
  · <a href="statmate/SKILL.md">阅读 Skill</a>
</p>

> **参考 Demo 状态：** 自动 QA **PASS** · Manifest **33/33 验证通过** · 科学审查
> **needs-author-decision（需要作者决定）**

**StatMate（统计同学）**（原 paper-figures）是一个面向生物医学并可用于其他定量领域的
**Agent Skill**。它把论文、方案、数据字典和真实数据整理成研究设计地图、数据审计与可审阅的
统计分析计划；实质性决策解决后，再通过保存的代码完成计算、模型诊断、图表与教学报告。工作流
要求每个报告数值都能追溯到源数据、机器可读结果和生成脚本。

---

## ✨ 亮点

- 🛡️ **真实计算,而非生成图像** — 图表由对原始数据的统计分析与绘图代码产生,全程没有生成式图像模型参与;结果可溯源、可复现,始终不触及 AI 生图红线。
- 🔬 **数据优先、表达明确** — 柱状图使用诚实的零基线，变换坐标必须标注；样本量、
  不确定性定义和真实计算的 p 值保持可见。
- 🧭 **研究设计先于检验** — 先确认研究问题、分析单位、配对/重复/聚类结构、结局、协变量和目标估计量，再选择方法。
- 🔎 **数据审计 + 分析审批门槛** — 检查缺失、重复、异常编码、伪重复、空设计单元和模型可估计性；关键选择确认后才正式计算。
- 📈 **图型与方法决策支持** — 综合数据形态、研究设计、目标估计量和论证目标给出可辩护的选项，最终选择仍由作者审核。
- 🎓 **期刊风格起始预设** — 提供 Nature / Science / Cell / IEEE / Elsevier / PLOS 与通用预设的栏宽、字体、dpi 和色盲安全配色；投稿前必须按具体期刊最新指南复核。
- 🧬 **实用的默认图像对** — 默认一张 PNG 审阅图 + 一张偏矢量的 PDF；SVG 或期刊特殊格式按需生成。
- 📐 **审核后按需导出表格** — 默认 Word 三线表，可选 Excel、CSV 或 LaTeX，不提前制造多余文件。
- 🧑‍🏫 **结果解释 + 阅读教学** — 说明结果、效应、不确定性和结论边界，并逐项教用户阅读点、线、误差棒、区间、表格列和脚注。
- 🌏 **用你习惯的语言交流** — StatMate 默认用你对话时使用的语言回复；除非你明确要求翻译或本地化，否则稿件语言保持不变。
- 🧰 **核心与可选工具栈分层** — 核心依赖包含 matplotlib 与 seaborn；plotnine、plotly、
  lifelines 和 scikit-learn 通过可选依赖配置安装。
- ♻️ **可审计复现** — 固定随机种子、保留脚本与机器结果、记录版本和文件哈希，并在交付前验证 manifest。

---

## 🖼 实际演示

仓库包含一套**可审计参考工作流**和一个**科研图型画廊**，都使用开放许可的真实研究
数据。下面科研图中的数据标记没有经过生成式图像模型重绘。

### 🫀 可审计参考工作流 — 心衰预后分析

**研究设计地图 · 数据审计 · 冻结计划 · Kaplan–Meier · Cox 诊断 · 内部预测 · 教学报告 ·
验证清单**

[▶ 60 秒导览](DEMO.zh-CN.md) ·
[完整审计链](examples/heart-failure-survival/v2_demo/) ·
[图文 DOCX](examples/heart-failure-survival/v2_demo/06_final/Heart_Failure_v2_Report.docx) ·
[逐页检查的 PDF](examples/heart-failure-survival/v2_demo/06_final/Heart_Failure_v2_Report.pdf)

![含置信带与风险人数的 Kaplan-Meier 生存曲线](examples/heart-failure-survival/v2_demo/06_final/figures/Fig1.png)

| 校正 Cox 模型 — 尚待作者决定 | 探索性折外预测 |
|:---:|:---:|
| ![](examples/heart-failure-survival/v2_demo/06_final/figures/Fig2.png) | ![](examples/heart-failure-survival/v2_demo/06_final/figures/Fig3.png) |

> 自动检查通过，清单 33/33 验证一致；但 EF 的比例风险诊断被标记，整体与图形诊断仍待
> 完成，所以整包保持 `needs-author-decision`。

### 🐧 科研图型画廊 — 南极企鹅

**9 类图型 9 张图 + 3 张三线表** ·
[查看画廊](examples/penguins-sexual-dimorphism/) ·
[打开报告](examples/penguins-sexual-dimorphism/Figure_Report.docx)

| 散点 + 回归 | 云雨图 | PCA 双标图 |
|:---:|:---:|:---:|
| ![](examples/penguins-sexual-dimorphism/figures/Fig3.png) | ![](examples/penguins-sexual-dimorphism/figures/Fig4.png) | ![](examples/penguins-sexual-dimorphism/figures/Fig8.png) |
| **相关热图** | **直方图 + ECDF** | **森林图** |
| ![](examples/penguins-sexual-dimorphism/figures/Fig7.png) | ![](examples/penguins-sexual-dimorphism/figures/Fig5.png) | ![](examples/penguins-sexual-dimorphism/figures/Fig9.png) |

---

## 🎯 九阶段工作流

这是一套有纪律的工作流,而非一次性提示——就是一位严谨分析者会走的路径。

| | 阶段 | 做什么 |
|---|---|---|
| 1️⃣ | **研究设计地图** | 从稿件/方案识别问题、分析单位、结局、时间和结论边界。 |
| 2️⃣ | **数据与溯源审计** | 核查结构、缺失、重复、隐私、设计单元和源文件哈希。 |
| 3️⃣ | **统计分析计划** | 给出方法决策表、假设、诊断、效应量、校正和备选方案。 |
| 4️⃣ | **审批门槛** | 让作者确认会实质影响分析的设计与数据决策。 |
| 5️⃣ | **代码计算** | 保存并运行代码，先输出机器可读统计结果。 |
| 6️⃣ | **诊断与敏感性分析** | 检查模型、稳健性和多重比较，不挑选“好看”的结果。 |
| 7️⃣ | **图表制作与自检** | 生成 PNG + PDF，制作表格预览并逐项核对。 |
| 8️⃣ | **解读与教学** | 分开写科研解读、论文表述和逐图逐表阅读指南。 |
| 9️⃣ | **审核后最终导出** | 只输出用户需要的最终表格格式、报告与追溯清单。 |

---

## 💪 从临时出图到证据工作流

| 层级 | 临时出图 | **StatMate 工作流** |
|---|---|---|
| 起点 | 一张指定图 | **研究设计、目标估计量与真实数据** |
| 方法选择 | 作图时临时决定 | **先写成可审阅的分析计划** |
| 计算 | 结果可能只留在笔记本 | **保存代码 + 机器可读结果** |
| 诊断 | 分散或缺失 | **模型假设与敏感性检查紧邻结果** |
| 视觉 QA | 只看外观 | **外观检查 + 画布、DPI 与文件自动检查** |
| 科学状态 | 隐含 | **draft / needs-author-decision / approved / final** |
| 交付 | 图像文件 | **审阅包 + 按需导出 + 报告 + 验证清单** |

---

## 🌐 语言

直接使用你最习惯的语言和 StatMate 对话，它默认会用同一种语言回复。这个规则只影响交流：稿件和投稿材料默认保持原语言（例如英文稿仍保留英文），只有你明确提出时，StatMate 才会把它们翻译或调整为当地语言期刊版本。

仓库中的全英、全中和中英双语报告只是输出示例，并不代表 StatMate 只能使用这几种语言。

可对比心衰案例的同一份报告:
[英文版](examples/heart-failure-survival/Figure_Report_EN.docx)、
[双语版](examples/heart-failure-survival/Figure_Report.docx)、
[中文版](examples/heart-failure-survival/Figure_Report_ZH.docx)。

---

## 🚀 安装与多平台部署

`statmate/` 被设计成可携带的文件夹式 **Agent Skill**：`SKILL.md`、Python 辅助脚本、
参考资料与资源放在一起。不同 Agent 的安装位置与触发约定并不相同，请以目标 Agent 的最新文档为准。

**1. 获取技能:**

```bash
git clone https://github.com/DRZ-hang/paper-figures.git
```

**2. 把 `statmate/` 文件夹放到你所用 agent 的 skills 目录：**

- **Claude Code** — `~/.claude/skills/`(所有项目)或某项目的 `.claude/skills/`:
  ```bash
  cp -r paper-figures/statmate ~/.claude/skills/statmate
  # Windows PowerShell:
  # Copy-Item -Recurse paper-figures\statmate $env:USERPROFILE\.claude\skills\statmate
  ```
- **OpenAI Codex** — 把该文件夹复制进 Codex 的 skills 目录(具体路径见你所用 Codex 的 skills 文档)。
- **其他支持 skills 的 agent（如小龙虾等）** — 同样把 `statmate/` 文件夹放进该 agent 的 skills 位置即可。技能本质就是 `SKILL.md` + 脚本，一个文件夹各处通用，只是目标目录因 agent 而异。

**3. 安装 Python 依赖:**

```bash
pip install -r statmate/requirements.txt       # 核心辅助脚本
pip install -r statmate/requirements-all.txt   # 可选完整绘图/统计栈
```

安装后可用 `$statmate` 显式调用；当你请求研究统计、图表、结果解释或读图教学时也可自动触发。

> 运行 `python statmate/scripts/figstyle.py --list` 可查看内置期刊预设。

---

## 📝 用法

直接把任务描述给你的 agent,并提供稿件和数据:

> - *"这是我的稿件和 `results.xlsx`,帮我画结果部分的图,按 Nature 规范,图注用英文。"*
> - *"为这篇论文的实验数据画一张分组比较图,目标期刊是 IEEE 双栏,图注用中文。"*
> - *"把 `cohort.csv` 做成 Kaplan–Meier 图和一张基线特征三线表,出中英双语报告。"*
> - *"这是研究方案、数据字典和 `results.xlsx`，先判断统计方法并解释理由；我确认后再正式分析。"*

你的 agent 会先建立研究设计地图并审计数据，交付统计分析计划供确认；随后运行代码、诊断模型、
生成图表和结果解读。最终表格格式在审核通过后按需选择。

---

## 📦 仓库结构

```
statmate/                           ← 技能本体（安装这个文件夹）
├── SKILL.md                       ← agent 遵循的工作流
├── requirements.txt              ·  核心工具与常用分析依赖
├── requirements-demo.txt         ·  参考案例依赖
├── requirements-all.txt          ·  可选完整绘图/统计栈
├── requirements-test.txt         ·  CI 与开发检查依赖
├── references/                    ← 按需加载的决策指南
│   ├── study-design-intake.md     ·  研究问题与设计地图
│   ├── data-audit-and-provenance.md · 数据质量、隐私与溯源
│   ├── analysis-plan.md           ·  统计分析计划与审批门槛
│   ├── statistical-methods.md     ·  通用统计方法
│   ├── biomedical-methods.md      ·  生物医学分析路由
│   ├── chart-selection.md         ·  数据形态 × 论证目标 → 图型
│   ├── interpretation-and-teaching.md · 结果解读与阅读教学
│   ├── journal-specs.md           ·  期刊规范 + 预设系统
│   └── plotting-stacks.md         ·  绘图库的发表级写法
├── scripts/
│   ├── data_audit.py              ·  JSON + Markdown 数据审计
│   ├── analysis_manifest.py       ·  文件哈希与复现清单
│   ├── figstyle.py                ·  PNG 预览 + PDF/SVG 矢量图
│   ├── table_export.py            ·  审核后按需导出表格
│   ├── docx_tables.py             ·  三线表 Word 表格
│   └── report_docx.py             ·  生成报告(lang = en / zh / bilingual)
└── assets/
    ├── presets.json               ·  可编辑的期刊预设
    └── report_template.md         ·  Markdown 报告备用模板

statmate/tests/                     ← 单元与集成回归测试

examples/                          ← 两个完整案例(数据 + 脚本 + 图 + 报告)
├── penguins-sexual-dimorphism/    ·  9 类图型,3 张表
└── heart-failure-survival/        ·  v2 审计型生存 / Cox / 预测演示 + 旧版展示
```

---

## 🔬 可复现

仓库中所有图表均由保存的代码生成。心衰演示记录了参考运行使用的直接依赖版本，并在每次生成后
立即验证所有产物。相同环境可复现机器可读结果和位图资产，但字体、数值库以及 PDF/DOCX 元数据可能
随系统变化。每次运行后应检查内容并刷新 manifest，不应假定跨环境字节完全相同。

```bash
cd examples/penguins-sexual-dimorphism/scripts
for f in make_*.py; do python "$f"; done   # 重新生成全部图、表与报告

# 为心衰案例选择报告语言:
cd ../../heart-failure-survival/scripts
STATMATE_LANG=zh python make_report.py      # 或 en / bilingual；仍兼容 PAPERFIG_LANG

# 或运行完整 v2 证据工作流:
cd ..
python v2_demo/04_code/run_demo.py

# 传输或后续审核后，可独立验证全部哈希:
cd ../..
python statmate/scripts/analysis_manifest.py verify examples/heart-failure-survival/v2_demo/06_final/manifest.json
```

---

## ⚠️ 免责声明

StatMate（统计同学）是辅助你从数据出发完成分析与图表制作的工具，不能替代科研判断。科研发表要求严谨，
论文作者对成果负全部责任。在使用或投稿任何图表之前,请由作者本人对其统计方法、图型选择、底层
数值以及每条图注的措辞进行专业、准确性的审核。请把输出视为一份需要核验的高质量草稿,通过专业
审核后再定稿使用。

---

## 📄 许可与数据署名

本项目**代码**以 [MIT 许可](LICENSE)发布。

两个案例完全基于**他人已发表、开放许可的数据**构建,数据著作权归下列原作者所有,转用请保留署名。

### 🐧 案例 1 — 南极企鹅
> **论文(CC BY 4.0):** Gorman KB, Williams TD, Fraser WR (2014). *Ecological Sexual Dimorphism
> and Environmental Variability within a Community of Antarctic Penguins (Genus Pygoscelis).*
> **PLOS ONE** 9(3): e90081. https://doi.org/10.1371/journal.pone.0090081
>
> **数据(CC0):** 由 Kristen Gorman 博士与帕尔默站南极长期生态研究项目(PAL-LTER)采集;
> 经 `palmerpenguins` R 包分发 —— Horst AM, Hill AP, Gorman KB (2020)。
> https://allisonhorst.github.io/palmerpenguins/ · doi:10.5281/zenodo.3960218

### 🫀 案例 2 — 心衰生存分析
> **论文(CC BY 4.0):** Chicco D, Jurman G (2020). *Machine learning can predict survival of
> patients with heart failure from serum creatinine and ejection fraction alone.* **BMC Medical
> Informatics and Decision Making** 20: 16. https://doi.org/10.1186/s12911-020-1023-5
>
> **原始数据采集:** Ahmad T, Munir A, Bhatti SH, Aftab M, Raza MA (2017). *Survival analysis of
> heart failure patients: A case study.* **PLOS ONE** 12(7): e0181001.
> https://doi.org/10.1371/journal.pone.0181001
>
> **数据集(CC BY 4.0):** UCI 机器学习库,*Heart failure clinical records*(数据集 519)。
> https://archive.ics.uci.edu/dataset/519/heart+failure+clinical+records

各案例的详细说明与许可:[企鹅](examples/penguins-sexual-dimorphism/README.md#source--attribution--来源与署名)
· [心衰](examples/heart-failure-survival/README.md#source--attribution--来源与署名)。

<div align="center">

**面向 OpenAI Codex、Claude Code 与其他文件夹式 Skill 工作流设计。** 等仓库公开后，
如果它帮到了你的研究，欢迎点亮 ⭐。

</div>
