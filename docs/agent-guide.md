# Agent 检索与复现指南

[项目首页](../README.md) · [实验检索目录](experiment-index.md) · [目录接口](agent-catalog.md) · [计算复现指南](agent-reproduction.md)

本指南面向接手实验问答、数据核对、计算复现和文档维护的 agent。先读仓库 [AGENTS.md](../AGENTS.md)，以稳定实验标识 `course-NN/slug` 定位材料，再沿“原始记录 → 规范输入 → 计算结果 → 物理解释”读取证据。

## 按任务找到文件

首次查找实验可使用[中英文检索目录](experiment-index.md)；程序读取使用 [`docs/experiments.json`](experiments.json)。机器目录包含名称与别名、主题与方法、资源路径、主报告 PDF、指标目录、实际接口和复现命令；字段、哈希规则及命令说明见[目录接口](agent-catalog.md)。

从仓库根目录先检索，再查看完整实验对象：

```powershell
python scripts/agent_catalog.py search "物质密度" --json
python scripts/agent_catalog.py search "RLC bandwidth" --course course-03 --json
python scripts/agent_catalog.py show course-01/pendulum --json
```

前两条分别定位 `course-01/density` 与 `course-03/rlc-resonance`；第三条返回单摆的路径、指标及专用接口。搜索多词时要求所有词出现，`--course` 限定课程，`--limit` 调整返回数量。取得标识后，用 `show <id> --json` 的 `resources` 打开文件，按 `metric_catalog` 与 `result_pointer` 读取数值。

[`experiments/registry.json`](../experiments/registry.json) 是构建登记表，记录中文名称 `title`、标识 `id`、Python 模块、Wolfram Paclet、三稿及安装包路径。中文题名适合语义检索；`id`、`module`、`paclet` 适合精确检索。

|任务 / Search intent|首先读取|继续核对|
|---|---|---|
|找实验入口 / experiment lookup|实验 `README.md`|课程目录、登记表中的三稿路径|
|回答实验原理 / physical model|`report/report.md`|`experiment.json` 的参数与模型、计算实现|
|查读数与来源 / observations, provenance|`data/*.csv`、`data/provenance.json`|源报告 PDF、来源映射和整理记录|
|引用结果 / metric, uncertainty|`results/python.json`|`results/wolfram.json`、`results/verification.json`、报告的条件说明|
|复跑计算 / reproduce, execute|`notebooks/analysis.ipynb`|本实验 Python 模块、Paclet 内核与执行记录|
|找真实交互 / model exploration|`authoring.json` 的 `expansions`|展开块调用的 `explore`、包的 `Explore` 和控件验证记录|
|维护入口图片 / README figures|`assets/readme-plan.json`|所选 `series`、图题和观测/模型标签|

需要直接检查原文或代码时，补充全文检索：

```powershell
rg -n '共振|resonance' experiments/registry.json
rg -n 'surface_tension|条件标准不确定度' experiments/course-02/surface-tension src/physicslab/experiments/surface_tension.py
python scripts/batch.py --list
```

逐实验路径统一从登记表取得。例如 Python 中定位密度实验：

```python
from pathlib import Path
import json

root = Path.cwd()  # 仓库根目录
registry = json.loads((root / "experiments/registry.json").read_text(encoding="utf-8"))
entry = next(e for e in registry["experiments"] if e["id"] == "course-01/density")
exp = root / "experiments" / entry["id"]
print(entry["report"], entry["python_module"], entry["wolfram_notebook"])
```

## 沿证据链读取一个实验

1. **读入口与报告。** 确定实验对象、方法、章节顺序、单位和结论；README 提供阅读路线，报告给出完整推导与记录表。
2. **读规范输入。** CSV 保存本实验的记录，`experiment.json` 保存参数、模型与条件。查看列名和说明后，再判断哪些列是原始读数、源表派生值或模型参数。
3. **读来源映射。** `data/provenance.json` 定位源表、列和转换说明。各实验还可能有更正记录或核对文件，按实际文件读取。
4. **读计算输出。** `results/python.json` 和 `results/wolfram.json` 保存各端结果；`results/verification.json` 保存对照状态与逐项检查。执行与呈现记录位于同一 `results/` 目录。
5. **按问题打开实现。** Python 算法在登记表的 `python_module`，Wolfram 算法在对应 Paclet 的 `Kernel/analysis.wl`；单摆实现见下节。Notebook 展开块在 `authoring.json`，用于定位推导、表格和交互。

源 DOCX 的标识与哈希保存在登记表和来源记录中。源报告 PDF 的对应关系以 [`pdf/verification.json`](../pdf/verification.json) 中 `role = "main_report"`、`experiment_id` 和 `pdf_file` 为准，可用它定位原页进行表格核对。文件名与实验标题有差别时，沿该映射查找。

## 数值引用与数据边界

引用一个指标时同时记录 **实验标识、指标键、数值、单位、处理方法和适用条件**。例如密度实验的 `metrics.solid_density.value` 是由质量均值计算的合金密度，`metrics.solid_density.uncertainty` 对应条件标准不确定度；重复性分量另见 `solid_uncertainty_a`。

- 用未修约的 `value` 进行比较和后续运算，在回答、表格或图题中按所需有效数字显示。
- 单位读取本指标的 `unit`。标准不确定度、回归标准误、相对差和均方根差分别按其定义解释。
- 数字配上指向本实验报告或结果 JSON 的链接与对应 Git 提交；引用源读数时链接 CSV 或源 PDF，并注明表格或测量组。
- 检查输入与代码哈希是否对应当前文件。`check_delivery.py` 会核对这些关系以及已保存执行、对照和呈现记录。
- 保持主报告的测量批次。讲义示例、源作者补齐值、模型扫描与实际观测各按记录身份使用。
- 空值与待核读数沿用来源说明；已有分量按其范围报告，仪器指标、相关性或系统修正齐全后再扩展预算。
- 交互参数表示模型情景；从 `authoring.json` 和实际 `explore` 调用确认控件、范围及默认值。静态实验可通过改输入、重跑计算来研究敏感性。

新实验结果通常包含 `metrics`、`tables`、`series` 和 `notes`。单摆还使用 `processed`、`simulation`、`amplitude_scan` 等专用结构；按实际键名读取。

## 三个具体任务示例

### 任务一：回答“合金和盐水的密度是多少，误差如何解释？”

定位 `course-01/density`，读取 [报告](../experiments/course-01/density/report/report.md)、[两张称量表的来源映射](../experiments/course-01/density/data/provenance.json)和[结果 JSON](../experiments/course-01/density/results/python.json)。以下代码只读取保存结果：

```python
from pathlib import Path
import json

exp = Path("experiments/course-01/density")
result = json.loads((exp / "results/python.json").read_text(encoding="utf-8"))
verification = json.loads((exp / "results/verification.json").read_text(encoding="utf-8"))
print("双端对照：", verification["status"])
for key in ("solid_density", "liquid_density", "solid_uncertainty_a", "liquid_uncertainty_a"):
    metric = result["metrics"][key]
    print(key, metric["value"], metric["unit"], metric.get("uncertainty"))
print(result["notes"])
```

报告的水密度输入为 0.99779 g/cm³；合金与盐水的估值分别约为 7.90123 和 1.083849 g/cm³。解释误差时，分开描述质量重复性，以及采用 0.01 g 假设误差限的条件预算；共享空瓶质量的传播由三个原始称量变量求导。

### 任务二：在新内核复跑 RLC 谐振 Notebook

先按[使用指南](usage.md)安装 Python 依赖、SimSun 和 Times New Roman。以下命令从仓库根目录运行：

```powershell
.\.venv\Scripts\python.exe scripts/execute_notebooks.py --experiment course-03/rlc-resonance
.\.venv\Scripts\python.exe scripts/check_delivery.py --experiment course-03/rlc-resonance
```

第一条命令使用当前 Python 环境创建新内核，执行结果写入 `.build/notebook-checks/<运行编号>/course-03/rlc-resonance/analysis.ipynb`，同次 `execution.json` 记录状态。第二条检查正式成稿、链接、哈希与既有双端及呈现记录。两项输出分别回答“本环境重跑是否成功”和“正式交付是否对应当前输入与实现”。

若需要检查已有交互的物理关系，接着读取该实验的 `authoring.json` 和 `src/physicslab/experiments/rlc_resonance.py`，定位实际展开块与参数控件。

### 任务三：比较单摆的数值周期与解析周期

单摆标识为 `course-01/pendulum`。其 Python 接口同样接受实验目录，但结果结构包含专用模型输出：

```python
from pathlib import Path
from physicslab.experiments.pendulum import analyze

result = analyze(Path("experiments/course-01/pendulum"))
model = result["simulation"]
print("拟合重力：", result["metrics"]["gravity_fit"])
print("ODE 周期 / s：", model["period_ode_s"])
print("椭圆积分周期 / s：", model["period_exact_s"])
print("相对能量漂移：", model["relative_energy_drift"])
```

初始摆角、有效摆长、角速度和时长读自 `experiment.json` 的 `simulation`。ODE 周期取首次过平衡位置时刻的四倍；解析周期使用完整椭圆积分。将两者与相对能量漂移一起检查，连接模型假设与数值精度。

Wolfram 单摆采用 `PL` 前缀的接口与 `Pendulum.nb` 文件名：

```wolfram
root = "D:/general-physics-lab";
PacletInstall[FileNameJoin[{root, "notebook", "paclets", "PendulumLab", "dist", "PendulumLab-0.1.0.paclet"}]];
Needs["PendulumLab`"];
PendulumLab`PLAnalyze[]
PendulumLab`PLOpenNotebook[]
```

其他实验使用登记表中的包名，例如 ``DensityLab`Analyze[]``、``DensityLab`LabNotebookPath[]``、``DensityLab`OpenNotebook[]``、``DensityLab`ResultsFigure["solid_repeat"]``。图和探索的键从对应结果及 `authoring.json` 获取。

## 修改输入或展示后怎样复现

科学输入或算法修改时，同步更新来源说明及计算实现，然后运行实验的双端完整流程。以密度实验为例：

```powershell
.\.venv\Scripts\python.exe scripts/pipeline.py all --experiment course-01/density
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe scripts/check_delivery.py --experiment course-01/density
```

完整流程需要 WolframScript、Wolfram 前端及指定字体。`WOLFRAMSCRIPT` 可指定可执行文件；Windows 的 `PHYSICSLAB_BUILD_ROOT` 可指定较短的暂存目录。构建后核对报告结论、默认与改变参数后的图形状态，并更新相应呈现记录。

命令的批量范围如下：

|命令|范围与产物|
|---|---|
|`python scripts/pipeline.py all --all`|构建单摆以外的 44 个实验|
|`python scripts/pipeline.py all`|构建单摆|
|`python scripts/pipeline.py compare`|核对单摆当前输入、代码及两端结果|
|`python scripts/execute_notebooks.py --all`|在新内核执行全部 45 个 Notebook，保存到独立检查目录|
|`python scripts/check_delivery.py --all`|读取并检查全部 45 项正式交付|
|`python scripts/build_readme_assets.py --experiment course-01/density`|按入口选图计划生成密度实验的概览与结果图片|

仅维护入口文案或选图时，修改实验 `README.md` 与 `assets/readme-plan.json`，按需执行最后一条图片命令。核对图题位于图下、表题位于表上、公式显示、相对链接与观测/模型标识；科学报告和计算改动则按完整复现流程验收。
