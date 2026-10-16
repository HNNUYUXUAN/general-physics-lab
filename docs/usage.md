# 阅读与运行指南

[返回项目首页](../README.md) · [课程 1](../experiments/course-01/README.md) · [课程 2](../experiments/course-02/README.md) · [课程 3](../experiments/course-03/README.md) · [课程 4](../experiments/course-04/README.md)

## 先找到一个实验

从首页课程表进入课程目录，再点击实验名称查看完整入口。目录也提供报告、Jupyter、Wolfram 与源报告 PDF 的直达链接。

|文件|用途|打开方式|
|---|---|---|
|`report/report.md`|整理后的完整实验报告|GitHub、VS Code 的 Markdown 预览|
|`report/report.html`|排版后的报告阅读版|本地浏览器|
|`notebooks/analysis.html`|包含已保存图表及适用交互的计算阅读版|本地浏览器|
|`notebooks/analysis.ipynb`|可修改并重算的 Python 笔记本|JupyterLab、VS Code|
|Paclet 中的 `.nb`|可修改并重算的 Wolfram 笔记本|本机 Wolfram 前端|
|Paclet 中的 `.paclet`|包含代码、数据和 Notebook 的独立安装包|Wolfram 的 `PacletInstall`|
|`pdf/` 中的 `.pdf`|由原始 DOCX 转换的源资料|GitHub PDF 预览或本地 PDF 阅读器|

源报告 PDF 用于对照原始资料；重新整理和核算的报告位于各实验的 `report/`。源资料的文件名保留原样，实验归属以课程目录和 PDF 清单为准。

## 在浏览器中查看 HTML

GitHub 仓库页面显示 HTML 文件源码。要查看完整页面，可克隆或下载仓库后，在浏览器中打开实验的 `analysis.html`；保留完整仓库可同时使用报告引用的相对路径图片。

在仓库根目录启动本地预览服务：

```powershell
python -m http.server 8000 --bind 127.0.0.1
```

然后打开：

```text
http://127.0.0.1:8000/experiments/course-01/pendulum/notebooks/analysis.html
```

其中 `course-01/pendulum` 可替换为其他实验标识。查看报告阅读版则将后半段改为 `report/report.html`。结束时在启动服务的终端按 `Ctrl+C`。

HTML 中的滑块、菜单、曲线提示与缩放在浏览器中执行。数学公式由 MathJax 排版。

## 运行 Jupyter Notebook

以下命令在 Windows PowerShell 中执行。已有本地仓库时直接进入仓库根目录。

```powershell
git clone https://github.com/HNNUYUXUAN/general-physics-lab.git
cd general-physics-lab
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test]" jupyterlab
.\.venv\Scripts\python.exe -m ipykernel install --user --name general-physics-lab --display-name "General Physics Lab"
.\.venv\Scripts\python.exe -m jupyterlab
```

Python 要求 3.11 及以上。macOS／Linux 的虚拟环境解释器路径为 `.venv/bin/python`；按本机环境调整命令。

在 JupyterLab 打开一个实验的 `notebooks/analysis.ipynb`，选择 **General Physics Lab** 内核，重启内核并运行所有单元。Notebook 自带执行输出；GitHub 静态预览可用于阅读，较大的文件可下载到本机查看。

成稿图表使用宋体（SimSun）与 Times New Roman。运行前安装这两种字体。Markdown／Jupyter 的数学公式使用标准 LaTeX，可在 VS Code 或 Jupyter 中查看。

只想重新检查某个已保存 Notebook 的执行情况：

```powershell
.\.venv\Scripts\python.exe scripts/execute_notebooks.py --experiment course-03/rlc-resonance
```

执行结果保存在 `.build/notebook-checks/`。使用 `--all` 可检查全部 45 个实验。

## 打开 Wolfram Notebook

每个实验提供独立 Paclet。推荐使用实验入口中的安装包，这样代码、数据和 Notebook 可一起加载。

下面以物质密度实验为例，在 Wolfram Notebook 中运行。将 `root` 改为本机仓库路径：

```wolfram
root = "D:/general-physics-lab";
PacletInstall[FileNameJoin[{
  root, "notebook", "paclets", "DensityLab", "dist",
  "DensityLab-0.1.0.paclet"
}]];
Needs["DensityLab`"];
DensityLab`OpenNotebook[]
```

打开后，从新内核依次求值。安装包自带规范数据，可以独立于本仓库使用。单摆使用 `PendulumLab` 包，其打开入口为 ``PendulumLab`PLOpenNotebook[]``；其他实验的包名见课程目录及 [`experiments/registry.json`](../experiments/registry.json)。

直接阅读 `.nb` 的已保存输出也需要 Wolfram 前端。若要重新生成安装包或完整三稿，还需可调用的 WolframScript、指定字体和可用前端。

## 修改数据与重新构建

先阅读[数据与方法](data-and-methods.md)。规范读数位于实验的 `data/`，参数与单位位于 `experiment.json`。修改后运行该实验的完整双端流程：

```powershell
.\.venv\Scripts\python.exe scripts/pipeline.py all --experiment course-03/rlc-resonance
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe scripts/check_delivery.py --experiment course-03/rlc-resonance
```

通过 `WOLFRAMSCRIPT` 指定本机 WolframScript 路径；Windows 可用 `PHYSICSLAB_BUILD_ROOT` 设置较短的暂存目录。构建、呈现检查和结果发布流程见[开发文档](development.md)。

`--all` 批量构建单摆以外的 44 个实验。单摆使用 `scripts/pipeline.py all` 重建。

## 计算记录与问题定位

每个实验的 `results/verification.json` 记录双端数值对照；执行、呈现和交互核验分别保存在本实验的 `results/` 中。[验收汇总](delivery-summary.md)集中列出资料限制。

|现象|优先检查|
|---|---|
|HTML 在 GitHub 上显示为源码|下载后用浏览器打开，或使用本地 HTTP 预览|
|HTML 公式空白或显示原始符号|MathJax 资源能否加载；可改用 VS Code／Jupyter 查看|
|图表中文乱码或字体检查失败|本机是否安装 SimSun 与 Times New Roman|
|Python 找不到 `physicslab`|是否在仓库根目录安装依赖，且选中了虚拟环境内核|
|直接求值 Wolfram Notebook 找不到包或数据|先安装对应 `.paclet`，再使用包的 Notebook 入口|
|CI 没有重新执行 Notebook 或 Wolfram|查看工作流摘要；公共运行器的字体和 Wolfram 状态会单独记录|
