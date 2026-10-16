# Agent 工作指南

本项目整理淮南师范学院四门普通物理实验课程，共 45 个实验。每个实验提供独立 Markdown 报告、Jupyter Notebook、Wolfram Notebook、共同输入和双端计算结果。

## 首次接手

1. 阅读 `llms.txt` 与 `docs/agent-guide.md`，按任务选择实验。
2. 用 `python scripts/agent_catalog.py search "关键词" --json` 检索中英文名称、别名、物理主题和方法。稳定标识形式为 `course-NN/slug`。
3. 用 `python scripts/agent_catalog.py show course-03/rlc-resonance --json` 获取文件路径、指标、数据来源、入口函数与复现命令。
4. 修改前读取目标实验的 `README.md`、`experiment.json`、`data/provenance.json`、计算模块和适用的 `authoring.json`。完整流程见 `docs/agent-reproduction.md`。

## 内容与计算约定

- Markdown 沿主报告 DOCX 的章节顺序和记录表结构组织。Jupyter 与 Wolfram 沿对应章节展开计算物理内容；三稿各自包含理解本实验必需的参数、说明和结论。
- 主输入是实验目录内的 CSV 与 `experiment.json`。数据身份、单位换算、更正和来源定位记录在 `data/`；模型情景与观测读数分别描述。
- 修改物理计算时同时维护 `src/physicslab/experiments/<module>.py` 与对应 Paclet 的计算实现。使用未修约值比较结果，按本实验声明的单位、容差和不确定度定义判断。
- 结果引用附实验标识、指标键、单位、适用条件、文件路径和 Git 提交。完整精度来自 `results/python.json`、`results/wolfram.json`，展示修约来自报告。
- 已有图文 README 单独维护；重建保留其内容，入口图由 `scripts/build_readme_assets.py` 更新。

## 排版

- 默认中文；中文宋体（SimSun），西文与数字 Times New Roman。
- Markdown/Jupyter 使用标准 LaTeX；Wolfram 使用等价原生 BoxData/StandardForm。以 VS Code、Jupyter 和 Wolfram 前端检查数学显示。
- 图表白底黑线、空心观测点、浅灰辅助线，图例和说明避开数据。图题在图下、表题在表上；Wolfram 图表及题注居中。
- 每个交互对应明确的物理模型、参数、单位和范围，保留代表性静态输出。

## 运行与检查

在仓库根目录安装 `python -m pip install -e ".[test]"`；运行 Notebook 另装 JupyterLab。Python 要求 3.11 及以上；正式图表需要 SimSun 和 Times New Roman。完整双端构建还需 WolframScript 与 Wolfram 前端。

```text
python scripts/execute_notebooks.py --experiment course-03/rlc-resonance
python scripts/check_delivery.py --experiment course-03/rlc-resonance
python -m pytest
python scripts/agent_catalog.py build --check
python scripts/check_agent_docs.py
```

完整重建使用 `python scripts/pipeline.py all --experiment course-03/rlc-resonance`。单摆使用 `python scripts/pipeline.py all`，其 Python 结果结构和 Wolfram `PL*` 接口单独定义。`pipeline.py all --all` 构建其余 44 项；`execute_notebooks.py --all` 与 `check_delivery.py --all` 覆盖全部 45 项。

## 文档与索引维护

- 新增或变更实验时同步 `experiments/registry.json`、`docs/experiment-topics.json` 和实验文稿，再运行 `python scripts/agent_catalog.py build` 更新生成入口。
- `docs/experiments.json`、`docs/experiment-index.md`、`llms.txt`、`llm.txt`、`llms-full.txt` 由脚本生成；生成依据及检索字段见 `docs/discovery.md`。
- 代码、报告和数据之间的技术信息放入数据与验证文件；读者文稿直接说明实验内容和物理结论。
- 检查记录区分已有成果的审计、新内核执行、双端数值比较与前端呈现检查。完成后报告实际运行的检查和产物路径。
