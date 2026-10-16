# 开发与复现

## 成稿组织

Markdown 报告以归档 DOCX 为内容与结构依据，保留各自已有的抬头、学生信息、章节与内容顺序。原始记录表沿用 DOCX 的列序；公式及计算结果使用已核对的表达和重新计算的数值。模板中只维护叙述，数据与结果占位符由构建流程替换。

两份 Notebook 沿对应 Markdown 报告和本实验 DOCX 的章节顺序组织，在相应章节补充可执行计算、推导及有依据的探索。每个实验使用独立 Python 模块和 Wolfram Paclet；具有明确模型和参数的实验提供原生交互，其他实验保留完整静态计算。HTML 阅读版由执行后的 Jupyter 生成，内嵌 Plotly；公式渲染需要阅读器支持 LaTeX 或加载 MathJax。Markdown/Jupyter 以 VS Code、Jupyter 的标准数学显示为兼容基准。菜单筛选用于探索，正式报告使用主数据集的已验证结果。

## 多实验构建

`experiments/registry.json` 登记四门课程的45个实验。每个实验的 `authoring.json` 指定自己的章节、计算模块、对照指标和 Notebook 展开块，规范观测与来源记录保存在本实验 `data/` 中。

```text
python scripts/pipeline.py all --experiment course-01/density
python scripts/pipeline.py all --all
python scripts/batch.py --list
```

单摆原有无参数命令保持兼容。新实验的单次构建执行完整依赖链，使用按实验与运行编号隔离的暂存项目；通过计算、执行和双端对照后生成成稿，呈现检查独立记录。批处理失败不会覆盖该实验上一版成稿，其他实验继续运行，失败项在汇总中保持明确状态。公共构建使用独占锁串行访问 Wolfram 环境。

每个新 Paclet 公开 `Analyze[]`、`LabNotebookPath[]`、`OpenNotebook[]`、`ResultsTable[]`、`ResultsFigure[]` 和适用的 `Explore[]`；计算函数及其内部符号均位于该包的私有上下文。WolframScript 的输出通道使用文本格式，因此新内核验证重跑输入而不替换原生数学输出；保存的 Output 单元由构建内核实际求值生成。

## 单摆兼容命令

在项目根目录使用虚拟环境的 Python：

| 命令 | 行为 |
| --- | --- |
| `python scripts/pipeline.py prepare` | 将统一输入复制到 Paclet 并验证 SHA-256 |
| `python scripts/pipeline.py python` | 计算 Python 结果、生成 SVG/PNG 图表 |
| `python scripts/pipeline.py wolfram` | Wolfram 独立计算、生成 Notebook、测试与打包 |
| `python scripts/pipeline.py notebook` | 从可编辑源生成 Jupyter，启动新内核执行并保留输出 |
| `python scripts/pipeline.py compare` | 检查输入及代码哈希，逐项对照两端结果 |
| `python scripts/pipeline.py report` | 重新对照后用模板生成报告 |
| `python scripts/pipeline.py all` | 按完整依赖顺序运行上述流程 |
| `python -m pytest` | Python 数据、解析算例、模型与路径迁移测试 |

单摆的 `scripts/build_notebook.py` 是 Jupyter 的可编辑叙述源，计算函数在 Python 包内。Wolfram Notebook 由包内 `Support/build.wls` 生成。修改这两份构建源后重新构建，保留 Notebook 中真实执行得到的结果。

源 Paclet 的数据副本由 prepare 自动生成。构建程序仅将 Kernel、Notebooks、data、Tests 和 PacletInfo 封入安装包；安装包可脱离本仓库运行。单摆使用 `PendulumLab` 上下文；其他包各用登记表中的独立包名作为公开上下文，内部使用对应 Private 子上下文。

## 自动检查与发布记录

CI 执行 Python 数值测试。Notebook 执行还需要宋体（SimSun）和 Times New Roman；字体检查与运行状态记录在 `ci-status.json`。Wolfram 计算与双端流程在配置了字体、内核和前端的环境中执行。计算执行与视觉检查分别记录。

数据或方法修改时，依次更新来源说明、重算双端、审阅残差与结论、重新生成报告。代码环境由 `pyproject.toml` 定义，Windows 环境的精确依赖清单保存在 `requirements-windows.lock.txt`。

独立安装验证使用 `wolframscript -file notebook/paclets/PendulumLab/Support/verify-installed.wls`，会将生成的包安装到用户 Paclet 仓库，核对自带数据，并在新内核中重新执行 Notebook。该验证记录保存在实验的 `results/wolfram-installed-validation.json`；实际前端渲染保存在本地 `.build/wolfram-visual/`。

`.gitattributes` 对参与 SHA-256 校验的输入和计算实现保留原始字节，避免 Git 在跨系统检出时转换换行符而使已核验结果失效。其余文档可按通常方式编辑。

## 全量验收

`--all` 批量构建单摆以外的 44 个实验；单摆使用无参数命令重建。`python scripts/check_delivery.py --all` 检查 45 项成稿的入口、执行输出、输入与代码哈希、双端数值和章节。`python scripts/execute_notebooks.py --all` 在新内核中逐本重跑，结果写入独立的检查目录。

Wolfram 控件验证包括默认状态的前端显示检查，以及参数变化后的计算与几何响应检查。`scripts/audit_wolfram_interactions.wl` 从 `Manipulate` 提取模型与控件，逐个代入合法非默认值；记录保存在各实验的 `results/native-interaction-review.json`。

构建会在暂存目录运行；若源文件在执行过程中变化，拒绝发布该轮输出并保留当前源和上一份成稿，待新快照重试。长期构建的检查点及日志放在 .build/，审核记录同时保留产物哈希。
