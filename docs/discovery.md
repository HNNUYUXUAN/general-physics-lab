# 检索、引用与 agent 接手

本项目以稳定实验标识连接实验叙述、观测数据、两种计算实现和验证记录。中英文名称、常见别名与计算方法共同构成检索入口，检索结果可以直接定位到可阅读和可复算的文件。

## 按目的选入口

|目的|文件|内容|
|---|---|---|
|让 agent 快速了解项目|[`llms.txt`](../llms.txt)|简短背景、阅读顺序、课程和方法入口|
|一次读取完整导览|[`llms-full.txt`](../llms-full.txt)|接手说明、复现流程与45项实验卡片|
|按中英文主题找实验|[实验检索目录](experiment-index.md)|别名、物理问题、分析方法、三稿和数据链接|
|程序读取和过滤|[`experiments.json`](experiments.json)|稳定标识、相对路径、raw URL、资源哈希、指标与接口|
|了解机器字段|[目录接口](agent-catalog.md) · [JSON Schema](schemas/experiments.schema.json)|字段定义与检索命令|
|定位读数和结果|[Agent 阅读指南](agent-guide.md)|任务示例、证据链、数值引用|
|继续计算和维护|[Agent 复现指南](agent-reproduction.md) · [`AGENTS.md`](../AGENTS.md)|输入、执行、重建、检查与排障|
|引用整个项目|[`CITATION.cff`](../CITATION.cff) · [`codemeta.json`](../codemeta.json)|作者、项目身份、软件与学科元数据|

规范导览文件名为 `llms.txt`；`llm.txt` 提供相同入口的短链接。项目 raw 入口为：

```text
https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/llms.txt
https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/docs/experiments.json
```

需要锁定引用版本时，用实际 Git 提交 SHA 替换 URL 中的 `main`。阅读器沿 GitHub 文件链接浏览；获取纯文本时使用目录中的 `raw_url`。HTML 交互阅读方式见[使用指南](usage.md#在浏览器中查看-html)。

## 从问题进入证据

例如检索“半功率带宽”会定位 RLC 谐振实验。先读实验 README 的测量与计算主线，再读报告的带宽定义；由 `results/python.json` 的 `C02_R1_Q_bandwidth` 获取完整精度，由 `results/verification.json` 核对双端结果，最后追溯到频率扫描 CSV 和参数文件。

引用一个结果时同时保留实验标识、指标键、数值、单位、适用条件、来源路径与提交 SHA。引用观测时注明数据表和行标识；引用模型时注明参数与模型假设。项目整体引用信息见 `CITATION.cff`。

## 维护检索内容

人工维护实验登记、主题别名和正文；脚本从真实文件读取结果、入口、CSV 表头、数据来源与验证状态，生成目录和导览。

```text
python scripts/agent_catalog.py build
python scripts/agent_catalog.py build --check
python scripts/check_agent_docs.py
```

主题资料保存在 [`experiment-topics.json`](experiment-topics.json)，资源路径来自 [`experiments/registry.json`](../experiments/registry.json)，源 PDF 对应关系来自 [`pdf/manifest.csv`](../pdf/manifest.csv)。生成过程校验实验覆盖、文件存在、来源对应关系与 SHA-256。自动检查验证生成文件与当前来源同步。

`llms.txt` 采用 Markdown 导览格式，供 agent 按需取用；其结构依据 [llms.txt 提议](https://llmstxt.org/)。[Google 的 AI 搜索说明](https://developers.google.com/search/docs/appearance/ai-features)强调可抓取、可索引、文本可读和常规搜索基础。本项目据此维护清晰入口、具体内容、真实证据链接与可复现路径。CFF 与 CodeMeta 分别按[引用格式](https://citation-file-format.github.io/)和[软件元数据术语](https://codemeta.github.io/terms/)组织。
