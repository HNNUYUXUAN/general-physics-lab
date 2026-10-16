# Agent 复现与维护指南

本仓库按“规范输入 → 独立双端计算 → 报告与 Notebook → 执行及呈现核验”维护 45 个普通物理实验。接手时先确定实验标识，再选择阅读、复算或修改路径。

## 先定位实验和证据

[`experiments/registry.json`](../experiments/registry.json) 是实验标识、课程、Python 模块、Paclet、主 DOCX 与成稿路径的索引。以 `course-03/rlc-resonance` 为例：

|需要了解什么|读取位置|
|---|---|
|实验问题、关键结果与各格式入口|实验的 `README.md`|
|原理、记录、计算与结论|`report/report.md`、源报告 PDF|
|输入读数、单位与参数|`data/*.csv`、`experiment.json`|
|资料来源、单位转换与更正|`data/provenance.json`|
|报告章节、比较指标、Notebook 展开块|`authoring.json`|
|Python 计算|`src/physicslab/experiments/<module>.py`|
|Wolfram 独立计算|`notebook/paclets/<Paclet>/Kernel/analysis.wl`|
|计算输出与双端数值对照|`results/python.json`、`wolfram.json`、`verification.json`|
|执行、视觉、控件与包核验|本实验 `results/` 中相应的 `*-review.json`、`*-validation.json`|

源 DOCX 位于本地 `archive/`，按登记表中的 `source_docx` 定位；仓库中的 [`pdf/verification.json`](../pdf/verification.json) 记录源 PDF 的实验归属、页数与哈希。公开运行的计算输入随实验提供，资料对照使用 PDF。

## 新环境与已有输出

以下命令在仓库根目录的 Windows PowerShell 中执行。Python 要求 3.11 及以上，成稿字体使用 SimSun 与 Times New Roman；Wolfram 完整构建需要内核、WolframScript 和可用前端。现有安装包声明 Wolfram 14.0+，已保存的本地完整运行记录使用 15.0.1。

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test]" jupyterlab
$env:PYTHONUTF8 = "1"
$env:WOLFRAMSCRIPT = "C:/Program Files/Wolfram Research/WolframScript/wolframscript.exe"
$env:PHYSICSLAB_BUILD_ROOT = "D:/physicslab-build"
```

`PHYSICSLAB_BUILD_ROOT` 指向较短的暂存路径，适合 Windows 的 Wolfram 文件接口。macOS/Linux 使用 `.venv/bin/python`，并按本机安装设置环境变量。成稿计算环境的依赖快照见 [`requirements-windows.lock.txt`](../requirements-windows.lock.txt)；当前运行与测试依赖以 [`pyproject.toml`](../pyproject.toml) 为准，`.[test]` 同时安装 pytest 与文档校验所用的 PyYAML。阅读与启动方式见[使用指南](usage.md)。

Notebook 中的保存输出用于直接阅读。检查某本 Jupyter 在当前环境能否从新内核运行：

```powershell
.\.venv\Scripts\python.exe scripts/execute_notebooks.py --experiment course-03/rlc-resonance
.\.venv\Scripts\python.exe scripts/execute_notebooks.py --all
```

结果写到 `.build/notebook-checks/<运行编号>/<实验标识>/analysis.ipynb`，汇总在同次运行的 `execution.json`。该命令执行现有单元、保留正式文件，`--all` 覆盖全部 45 项。修改输入后，采用下节的完整构建同步报告文字中的数值、数表与图表。

## 修改一项实验

1. 从主报告、来源记录与规范输入确认数据粒度、单位、测量批次及模型条件。原始读数和派生量分别维护；讲义示例、源作者补齐值、已报中间量按其来源身份参与分析。
2. 修改相应 Python 模块与独立 Wolfram 计算，更新适用的解析算例、物理极限或参考检查。报告文字修改写入 `report/report.template.md`；计算值使用 `metrics.*`、`tables.*` 或 `replacements.*` 占位符。
3. 在 `authoring.json` 维护本实验 DOCX 的章节顺序、`comparison` 指标及按指标设置的 `tolerances`。Notebook 的讲解、两端调用与题注写入相应 `expansions`，章节名称应与报告匹配。
4. 执行完整构建，再审阅计算、图形、控件和结论，更新与新产物哈希对应的审核记录。

```powershell
.\.venv\Scripts\python.exe scripts/pipeline.py all --experiment course-03/rlc-resonance
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe scripts/check_delivery.py --experiment course-03/rlc-resonance
```

构建从隔离快照执行 Python、新 Jupyter 内核、Wolfram 独立计算、测试、打包和独立安装验证，生成真实输出，再复制到该实验及 Paclet 目录。构建中的源文件变化会使该轮输出保留在暂存区，随后以新快照重试。

构建状态与日志位于 `.build/<实验标识>/<运行编号>/`、`.build/progress.json` 和 `.build/batch-summary.json`；实际暂存项目位于 `PHYSICSLAB_BUILD_ROOT/<实验哈希>/<运行编号>/`。`wolfram-build.log` 与 `wolfram-verify.log` 分别记录计算/打包和独立安装/新内核/前端检查。

## 全量构建与单摆入口

```powershell
.\.venv\Scripts\python.exe scripts/batch.py --list
.\.venv\Scripts\python.exe scripts/pipeline.py all --all
.\.venv\Scripts\python.exe scripts/check_delivery.py --all
```

批量构建选择单摆以外的 **44 项**，按实验依次执行，某项失败后继续其他实验并汇总失败项。恢复工作时选择受影响实验重新运行完整链；现有 CLI 的恢复粒度是实验。

单摆使用独立的既有构建源与结果结构：

```powershell
.\.venv\Scripts\python.exe scripts/pipeline.py all
.\.venv\Scripts\python.exe scripts/pipeline.py compare
.\.venv\Scripts\python.exe scripts/check_delivery.py --experiment course-01/pendulum
```

无选择参数的 `pipeline.py` 命令作用于单摆；其细分阶段为 `prepare`、`python`、`wolfram`、`report`、`notebook`、`compare`。其他实验由 `all --experiment <id>` 构建，比较实现在 `scripts/batch.py` 的 `compare(p,w,a)` 中。`python-only` 也是单摆入口。

|Wolfram 接口|单摆|其余 44 项|
|---|---|---|
|计算|``PendulumLab`PLAnalyze[]``|``<Paclet>`Analyze[]``|
|Notebook 路径|``PendulumLab`PLNotebookPath[]``|``<Paclet>`LabNotebookPath[]``|
|打开 Notebook|``PendulumLab`PLOpenNotebook[]``|``<Paclet>`OpenNotebook[]``|
|Notebook 文件名|`Pendulum.nb`|`<Paclet>.nb`|
|主要编辑源|`Kernel/PendulumLab.wl`、`Support/build.wls`、`scripts/build_notebook.py`|`Kernel/analysis.wl`、报告模板、`authoring.json`|

其他包还提供 `ExecuteBlock[index]`、`ResultsFigure[key]`、`ResultsTable[tableAssociation]` 和适用的 `Explore[key]`；实际探索键从本实验展开块读取。

从新克隆直接安装 `dist/*.paclet` 即可使用自带代码、数据与 Notebook。源目录的 `data/`、`exports/` 是构建生成资源；完整流水线负责复制规范输入、校验哈希并生成它们。源包直接执行 `Support/build.wls` 时需要这些资源已存在。

## 数值、哈希与呈现核验

`check_delivery.py` 是只读检查，默认单摆，`--all` 覆盖 45 项。它检查章节一致、Jupyter 执行计数与错误、必要产物、链接、报告模板同步、当前输入/代码哈希、双端指标和数表，以及审核记录是否对应当前 Notebook、HTML 和模型源。该命令读取正式成稿及已有记录；本机新内核执行另用 `execute_notebooks.py`，完整双端重算使用 `pipeline.py all`。

新实验的指标容差在 `authoring.json/tolerances` 中声明；默认相对容差为 `1e-8`，绝对容差随指标尺度设置。两端数表中的数值单元另用 `rtol=1e-7`、`atol=1e-9` 比较。先排查单位、量纲、输入身份与数值实现，再依据物理和数值方法确定容差。

其余 44 项的 `input_hashes` 包含 `experiment.json` 和 `data/` 顶层文件；Python 的 `code_hashes` 包含实验模块与公共层，Wolfram 记录 `Kernel/analysis.wl`。单摆采用自己的输入清单与单数 `code_hash` 字段。计算结果中的哈希按原文件字节核验；机器检索目录的 `hash_basis` 另声明文本 LF 规范化或原字节规则，见[目录接口](agent-catalog.md)。共享计算或呈现模块变化时，复核全部依赖实验。`.gitattributes` 保留参与字节哈希的文件换行形式。

视觉核验分别查看 Markdown/Jupyter 的 LaTeX、HTML 的 MathJax 与实际 Wolfram 前端。检查中文宋体、西文数字 Times New Roman、公式上下标、单位、图例与图线分离、图题在下、表题在上、图组对齐和 Wolfram 居中。每个实际控件检查默认状态及至少一个参数变化；静态实验复核计算与图表。

README 插图由 `assets/readme-plan.json` 从保存的计算序列选图，题注在 README 中维护：

```powershell
.\.venv\Scripts\python.exe scripts/build_readme_assets.py --experiment course-03/rlc-resonance
```

输出为 `assets/readme-*.svg` 与 `.png`，导出检查记录在 `.build/readme-assets/render-checks.json`。已有 README 作为实验入口文稿维护；计算重建后，按新结果更新关键数值、选图和阅读说明。重绘后查看实际图片与 GitHub 页面，结合缺字、裁切和图例位置检查。

Wolfram 参数响应可在串行内核中调用：

```wolfram
Get["D:/general-physics-lab/scripts/audit_wolfram_interactions.wl"];
InteractionResponseAudit`AuditProject[
  "D:/general-physics-lab", {"course-03/rlc-resonance"},
  "D:/general-physics-lab/.build/rlc-interaction-audit.json"
]
```

该工具求值实际 `Manipulate` 模型体的默认值与合法非默认参数，记录计算及几何响应。前端显示与鼠标操作另外检查。完整安装验证记录和包资源校验见本实验 `results/`，已保存汇总见[验收汇总](delivery-summary.md)与 [`validation-summary.json`](validation-summary.json)。

## 排障顺序

|现象|检查与处理|
|---|---|
|`stale input` 或代码哈希变化|确认来源修改，按实验重建上下游产物；保留现有审核记录用于对照，随后审核新哈希|
|构建成功后呈现审核仍待更新|读取 `presentation-validation.json`，实际查看新 HTML/Notebook，重跑控件并登记对应产物哈希|
|Notebook 新内核找不到模块|在仓库根目录安装包，使用虚拟环境解释器；单元从头运行|
|中文缺字或图例符号异常|确认字体实际可用，查看 PNG/SVG 与前端；根据混排路径检查文本字体和数学字体|
|HTML 原始公式或空白|检查 MathJax 加载与公式语法，用 VS Code/Jupyter 交叉查看标准 LaTeX|
|Wolfram 包或数据缺失|安装对应 `.paclet`；修改源包时先运行完整流水线生成数据资源|
|Windows 包复制或资源访问异常|设置较短的 `PHYSICSLAB_BUILD_ROOT`，查看实际暂存路径与包内文件|
|`Author sources changed during execution`|待本实验源修改完成后重跑，使用新快照|
|实验 `build.lock` 或全局 `wolfram.lock` 已存在|核对锁内 PID 与实际运行进程；进程结束后再清理遗留锁并重试|

Wolfram 构建与安装共享本机资源，流水线使用独占锁。`scripts/batch.py --skip-frontend --experiment <id>` 可用于计算排查；完整验收仍执行前端显示检查。GitHub 工作流在字体齐全时执行 Jupyter，并单独记录运行环境的 Wolfram 状态，见 [Python workflow](../.github/workflows/python.yml)。

[开发规则](development.md) · [数据与方法](data-and-methods.md) · [使用指南](usage.md) · [返回项目首页](../README.md)
