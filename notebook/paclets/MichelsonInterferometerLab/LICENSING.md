# 许可与署名

《普通物理实验 · General Physics Lab》采用分组成许可：**代码 MIT，原创文稿、数据整理与计算图表 CC BY 4.0**。作者与维护者：缪雨轩，2026。

|组成|适用许可|范围|
|---|---|---|
|Python、Wolfram 与构建代码|[MIT](LICENSE)|`src/`、`scripts/`、`tests/`、工作流和包配置中的项目代码；Paclet 的 `Kernel/`、`Tests/`、`Support/`；Notebook 可执行代码单元|
|实验报告、说明与 Notebook 叙述|[CC BY 4.0](LICENSES/CC-BY-4.0.txt)|项目原创的 Markdown、报告模板、HTML 正文、README、开发文档及 Notebook 文字、公式说明和原创输出|
|规范数据与计算图表|[CC BY 4.0](LICENSES/CC-BY-4.0.txt)|项目的 CSV/JSON 整理贡献、计算结果、程序绘制图表和示意图；适用的数据库权利随同许可|
|源报告 PDF|按逐份登记的范围|作者原创部分适用 CC BY 4.0；原模板、插图、摘录及其他来源内容沿用原权利|
|课程讲义、说明书与其他参考资料|原权利与原许可|逐份来源和可见署名见第三方清单|
|学校校徽与校名标识|学校标识权利|淮南师范学院官方标识，来源为学校标识素材；商标及标识使用权由相应权利人保留|
|第三方 JavaScript、CSS 与模板|各组件原许可|Plotly、MathJax、RequireJS、Mermaid 和 Jupyter 组件的版权与许可分别保留|

CC BY 4.0 允许在保留署名、许可链接并标注修改的条件下分享和改编，包括商业用途。完整条款以本目录 `LICENSES/CC-BY-4.0.txt` 中的[官方法律文本](https://creativecommons.org/licenses/by/4.0/legalcode)为准。MIT 完整条款保存在同目录 `LICENSE`。

## 复用与署名

文稿、数据整理或图表可使用如下署名，补充具体实验、路径和版本即可：

> 缪雨轩，《普通物理实验 · General Physics Lab》，实验名称或文件路径，版本或 Git 提交，https://github.com/HNNUYUXUAN/general-physics-lab ，CC BY 4.0。修改说明：……

代码复用保留 MIT 版权和许可文本。引用计算结果时一并注明实验、数据版本、单位与适用条件，便于重新计算。

## 来源材料与混合文件

源 PDF、学校标识和材料中引用的第三方表达适用其原有权利。项目的 CC BY 4.0 许可覆盖可许可的原创贡献；第三方内容的再利用范围按其自身许可判断。已明确的作者、署名机构、来源路径及许可分别列于[第三方说明](https://github.com/HNNUYUXUAN/general-physics-lab/blob/main/THIRD_PARTY_NOTICES.md)和[逐项清单](https://github.com/HNNUYUXUAN/general-physics-lab/blob/main/docs/third-party-materials.json)。清单中 `null` 表示现有材料未明确该项。

Jupyter 和 Wolfram Notebook 是混合文件：代码单元适用 MIT，项目原创的文字、推导说明、计算表和图形输出适用 CC BY 4.0；所引用的第三方内容保留相应标识与条款。HTML 内嵌或加载的第三方代码保持组件原许可。

## 独立 Paclet

每个独立 Paclet 同目录携带 `LICENSE`、`LICENSES/CC-BY-4.0.txt` 与本说明。包内 `Kernel/`、`Tests/`、`Support/` 的项目代码和 Notebook 代码单元适用 MIT；Notebook 原创叙述、计算输出、`data/` 整理贡献与项目图表适用 CC BY 4.0。`assets/` 内素材根据上述来源清单保留第三方例外。

源目录与可安装 `.paclet` 使用相同组成划分。项目地址及版本记录用于追溯包内数据和图表的来源。
