# 实验目录接口

[`experiments.json`](experiments.json) 是45项实验的机器可读目录，[JSON Schema](schemas/experiments.schema.json)定义字段。所有 `path` 相对仓库根目录；`url` 指向 GitHub 阅读页，`raw_url` 指向原文件。

每个资源记录 SHA-256、字节数与 `hash_basis`。`utf8-lf` 表示先将 UTF-8 文本的 CRLF 换为 LF，再计算哈希和字节数，便于跨平台识别同一内容；PDF、Paclet 使用 `raw-bytes`，直接计算原字节。计算结果内的 `input_hashes` 和 `code_hashes` 按各实验原有的原字节规则核验。

## 检索命令

在仓库根目录运行，检索本身只依赖 Python 标准库：

```text
python scripts/agent_catalog.py search "重力加速度"
python scripts/agent_catalog.py search "RLC bandwidth" --json
python scripts/agent_catalog.py search "interference" --course course-04 --json
python scripts/agent_catalog.py show course-03/rlc-resonance --json
```

搜索使用标题、英文标题、别名、主题、方法、摘要和指标键/标签，多词查询要求所有词出现；默认返回最多10项，可通过 `--limit` 调整。`search --json` 返回命中列表；`show --json` 返回一个完整实验对象。实验标识保持稳定，展示名称和别名可以更新。

英文词与缩写按词边界匹配，中文按短语匹配，大小写等价。例如 `ODE` 检索常微分方程方法，`C02_R1_Q_bandwidth` 检索完整指标键。

## 主要字段

|字段|含义|
|---|---|
|`id`、`course`、`title`、`title_en`|稳定标识、课程、中文和英文名称|
|`aliases`、`topics`、`methods`、`summary_zh`|人工核对的检索词与实验摘要|
|`sections`|本实验报告的章节顺序|
|`resources`|README、报告、Notebook、源PDF、参数、数据来源、代码、结果及验证文件|
|`data_files`|数据目录中的CSV文件、原表头、首行以外的记录行数和资源描述|
|`metric_catalog`|结果中全部指标的键、标签和单位|
|`key_results`|代表性结果摘录；44项按README选图计划，单摆选拟合重力、斜率与截距；以对应 `results/python.json` 为计算依据|
|`key_results[].result_pointer`|数值在结果JSON中的指针，例如 `/metrics/C02_R1_Q_bandwidth`|
|`python_interface`、`wolfram_interface`|实际模块、分析函数、包上下文及Notebook打开函数|
|`commands`|单实验审计、新内核执行、双端重建与入口图更新命令|
|`verification`|已有记录的状态、双端检查数量及原记录路径|
|`source_identity`|主DOCX归档身份及对应PDF的路径、页数和哈希|

`verification` 描述随仓库保存的记录。重新执行产生的新记录按[复现指南](agent-reproduction.md)处理。模型条件、不确定度定义与来源细节分别读取 `experiment.json`、原始结果及 `data/provenance.json`。

CSV表头按位置原样列出，同名和空白列保留原表结构；参与计算的表和列由计算模块确定。指标的 `label` 沿用保存结果；提供 `description` 的指标附有检索释义，结合指标键与单位阅读。

## 更新目录

```text
python scripts/agent_catalog.py build
python scripts/agent_catalog.py build --check
```

`build` 更新机器目录、Markdown检索目录、短导览和完整导览。`build --check` 只比较生成内容，发生来源变化时以非零状态退出并列出待更新文件。生成文件使用固定排序与UTF-8，保持相同输入对应相同输出。
