# 虚拟实验：检索、接手与复现

从[虚拟实验目录](../simulations/README.md)选择实验。机器入口为 [`simulations/registry.json`](../simulations/registry.json)：使用稳定的 `experiment_id` 定位课程，再由 `resources` 读取页面、物理模型、观测、文献和验证记录。各实验的模型函数及测量规则保存在独立模块中。

## 按问题定位

表 1　文件入口与核对内容

|任务|入口|核对内容|
|---|---|---|
|解释模型|`resources.model_evidence`|方程、假设、初始与边界条件、适用范围|
|追溯文献|`resources.references_json`、`references_bibtex`|书目信息、DOI、正文定位、全文哈希和用途|
|读取参数|`resources.simulation_model`，以及实验提供的 `model-spec.json`|默认值、开放范围、单位、原记录或教学场景身份|
|核对观测|`resources.simulation_observations`|原字符、规范数值、派生量及规范输入哈希|
|检查算法|登记项的 `tests` 与 `validator`|解析算例、极限、独立算法、收敛性及容差|
|检查实际运行|`resources.simulation_validation`、`frontend_validation`|模型与资源哈希、运行环境、数值结果、交互和截图|
|维护页面|`simulation_html`、`simulation_controller`、绘图模块与样式|控件、状态恢复、图轴、题注、公式和窄屏|
|维护发布与检索|[`build_pages.py`](../scripts/build_pages.py)、[`agent_catalog.py`](../scripts/agent_catalog.py)|登记状态、资源白名单、项目子路径和生成目录|

仿真入口见各实验 README。模型使用的单位、方向约定与数据结构按实验声明；例如光学输入常用纳米或毫米，内部传播统一换算后计算。先检查这些约定，再比较跨语言的未修约结果。

## 文献检索与证据

公共理论按振动波动、电路、电磁场、几何光学、波动光学和力热测量组织；具体实验核对自己的装置关系、修正项与材料参数。复用文献时为本实验另建方程及参数映射。

1. 在 Chrome 延续维护者已登录的两校 WebVPN 会话，交叉检索同一目标全文，记录检索式、数据库、日期与获取状态。
2. 核对题名、作者、年卷期页码和 DOI，下载原文到本地 `archive/literature/`，计算 SHA-256。
3. 实际阅读正文，定位页码、章节或公式号；数学页同时核看原页，区分排印与文本提取问题。
4. 分别记录模型依据、参数来源、适用范围和验证方法。发现公式问题时保存原式、推导及核查算例。
5. 两校均未取得目标全文时使用读秀文献传递，记录申请、接收与核读状态，收到文件后补充哈希。

公开书目提供稳定 DOI 或出版机构入口、研究摘要和证据定位。本地归档保存全文与访问记录，`archive/` 由 Git 忽略。数据库会话地址及账号信息保留在浏览器会话中。

## 数据身份与测量解释

表 2　数据类别

|类别|用途|分析规则|
|---|---|---|
|原报告观测|复算既有实验记录|沿用原批次、单位和已知测量条件|
|文献或校准参数|建立具体装置或材料关系|保存来源、温度、波长与适用条件|
|独立教学参数|探索可验证的物理关系|在模型证据中声明数值、范围与教学身份|
|自动模型记录|检验确定性前向计算及反演|保留完整参数、版本与生成方式|
|用户操作读数|练习定位、计时、调零与采样|保存操作条件、原始读数及来源类别|

按实验规定筛选可比较的记录，保持拟合所需条件一致。用于确定参数的数据与独立验证数据分别标记。回归标准误、仪器分辨率和系统不确定度分别解释；缺少仪器信息时保留分析边界。

## 执行独立验证

从仓库根目录准备 Python 项目依赖与 Node.js，按稳定标识运行：

```text
python scripts/validate_simulations.py --experiment course-03/rlc-resonance
python scripts/validate_simulations.py --all
python -m pytest
```

总验证器执行运行模块语法检查、Node 模型测试及各实验的 Python 独立参考计算，结果保存在 `.build/simulation-checks/<运行编号>/`。单项原命令继续有效，例如：

```text
node --test tests/pendulum-model.test.mjs
python scripts/validate_pendulum_simulation.py
```

单摆周期的椭圆积分以模数 $k=\sin(\theta_0/2)$ 表示，SciPy `ellipk` 使用参数 $m=k^2$。其他实验分别采用节点方程、数值求根、独立积分、几何或复振幅计算作为参考；方法与容差写入本实验验证记录。

核验一次运行时同时检查执行状态、退出码、失败项、参数组、容差、输入与代码哈希。只生成参考值的运行按脚本约定保留 `not_run` 等浏览器对照状态。

## 前端与发布

使用 HTTP 预览构建后的站点，保留 `/general-physics-lab/` 项目子路径。数学资源由构建注入本地 MathJax，源页面维护标准 LaTeX。

表 3　实际浏览器验收

|对象|核验行为|
|---|---|
|参数与操作|默认、边界、非法输入、操作次序及读数变化|
|时间演化|播放、暂停、复位、实际标签切换后的计时与恢复|
|记录与反演|采样、分组条件、拟合、已知关系和操作读数|
|保存与导出|刷新恢复、清空、真实 CSV/JSON 文件、单位及模型版本|
|公式与视觉|宋体、Times New Roman、上下标、轴标、图下题与表上题、桌面及窄屏|
|资源|实际 HTTP 返回、模块和源文件 SHA、引用与数据链接|

数值验证与浏览器验收分别记录。源码或页面变化后，更新受影响阶段及下游记录；共同资源变更触发已上线实验回归。前端记录的 `source_hashes` 绑定当时实际验收的资源版本。

```text
python scripts/build_simulation_scientific_index.py --require-all-ready
python scripts/build_simulation_scientific_index.py --check
python scripts/agent_catalog.py build
python scripts/agent_catalog.py build --check
python scripts/check_agent_docs.py
python scripts/build_pages.py
python scripts/check_pages.py --report .build/pages/verification.json
```

登记表中通过科学与前端验收的页面进入正式站点。目录、README 在线入口及 `llms.txt` 系列随登记结果同步。

## 原成稿回归

在独立运行目录保存原报告、Jupyter、Wolfram、规范数据、代码及结果的 SHA-256 基线。平台构建后按同一路径集合复核；README 导航与新增网页资源单独审阅。原实验科学内容修订按双端计算与三稿验收流程建立新基线。

接手时先读登记状态、最新验证记录和模型证据中的待核事项，再处理对应实验。引用计算结果时附实验标识、模型版本、参数及单位、适用条件和 Git 提交。
