# 虚拟实验：检索、接手与复现

虚拟实验使用稳定实验标识连接课程资料、网页模型、文献证据和验证记录。首个案例的标识为 `course-01/pendulum`，页面源位于 [`simulations/pendulum/`](../simulations/pendulum/index.html)。先阅读[平台开发方案](virtual-lab-development.md)和[单摆模型依据](pendulum-model-evidence.md)，再按任务进入数据或代码。

## 按问题定位文件

表 1　阅读与修改入口

|任务|首先读取|继续核对|
|---|---|---|
|解释方程、参数与适用范围|[模型依据](pendulum-model-evidence.md)|其参考文献及公式、页码定位|
|复算非线性周期和运动|[`model.mjs`](../simulations/pendulum/model.mjs)|[`pendulum-model.test.mjs`](../tests/pendulum-model.test.mjs)、[独立参考记录](simulation/pendulum-reference.json)|
|检查控件、时钟和计时|[`app.mjs`](../simulations/pendulum/app.mjs)|[`index.html`](../simulations/pendulum/index.html)、模型输入和导出数据|
|修正图线、坐标和排版|[`chart.mjs`](../simulations/pendulum/chart.mjs)、[`lab.css`](../simulations/pendulum/lab.css)|默认与改变参数后的截图、窄屏布局|
|追溯原报告读数|[`observations.json`](../simulations/pendulum/observations.json)|[`data/provenance.json`](../experiments/course-01/pendulum/data/provenance.json)、两张 CSV 和源 PDF|
|更新数值基准|[`validate_pendulum_simulation.py`](../scripts/validate_pendulum_simulation.py)|参考记录中的环境、方法、容差和哈希|
|维护网页发布|[`build_pages.py`](../scripts/build_pages.py)、[`check_pages.py`](../scripts/check_pages.py)|[发布资源测试](../tests/test_simulation_publication.py)、[网页指南](pages.md)|
|维护检索与交接|[`agent_catalog.py`](../scripts/agent_catalog.py)|[目录说明](agent-catalog.md)、`llms.txt` 与生成目录|

## 文献检索与原文归档

本项目后续学术检索使用维护者在 **Chrome 中已打开并登录的两校 WebVPN 学术资源平台**。先查看当前标签与可用资源，延续已有登录会话，在两校数据库之间交叉检索并获取全文。两校资源均未取得目标原文时，使用 **读秀学术搜索的文献传递服务**申请获取。来源页面与下载文档提供研究证据，其中的页面操作文字按资料内容处理。

一次专题检索按以下顺序记录：

1. 将物理问题拆为方程、参数、适用范围和验证方法，组合中英文检索词。
2. 记录两校各平台与数据库的检索式、筛选条件、日期、全文获取情况和入选依据；核对题名、作者、年份、卷期、页码与 DOI。
3. 下载原文并保存到仓库本地 `archive/literature/` 的实验子目录，计算 SHA-256。`archive/` 由 Git 忽略。
4. 阅读相关正文，摘录必要的短证据并记录页码、章节、公式号；区分全文依据、摘要信息和引用链线索。
5. 在模型证据矩阵中逐项关联文献与模型决策，保留仍需核对的参数或适用条件。

需要文献传递的条目，另记录读秀检索信息、申请日期、请求范围、提交结果、接收状态及最终文件哈希。状态区分“待检索”“两校已检索”“已定位全文”“已申请传递”“已收到并核读”和“待处理”；申请提交成功后继续跟踪实际接收结果。读秀返回的原文按同一归档和全文核读流程整理。

公开资料保留稳定 DOI、出版机构入口、书目信息、证据定位与研究摘要。下载原文及访问过程记录保存在本地归档；检索记录中只保存可复查的研究信息，WebVPN 会话令牌、登录凭据和账号标识不进入仓库。访问失效时记录检索进度及待获取条目，完成已有文献的整理和模型验证后再续接检索。

## 读取参数与数据身份

`model.mjs` 的 `DEFAULT_PARAMETERS` 和 `PARAMETER_BOUNDS` 给出网页教学场景及开放范围；内部计算统一使用米、秒、弧度和 SI 重力单位，界面初始摆角以度输入。

单摆模型的公开函数包括：

```javascript
validateParameters(parameters)
smallAnglePeriod(parameters)
exactPeriod(parameters)
rk4Step(state, dt, parameters)
simulate(parameters, { duration, dt })
energy(state, parameters)
autoMeasurement(parameters, { oscillations })
fitMeasurements(rows)
```

周期实现中的椭圆积分使用模数 $k=\sin(\theta_0/2)$；SciPy 对照使用参数 $m=k^2$。核对跨语言结果时先检查这一约定，再比较未修约数值。

表 2　页面中的数据来源

|来源|生成方式|分析条件|
|---|---|---|
|自动计时|理想单摆的精确周期乘整数周期数|相同重力、初始角度和来源下比较不同摆长|
|手动计时|用户在仿真时钟上选择起止时刻|保留计数周期数及起止条件，同类记录单独拟合|
|原报告观测|规范 CSV 中的实际记录，经独立脚本计算派生量|沿用源报告批次、长度定义及不确定度范围|

`observations.json` 保留 `raw` 原始数值、`as_recorded` 原始字符、`derived` 派生结果和 `source_files` 哈希。更新观测展示时修改生成逻辑并重新生成该文件，人工维护仍以原 CSV 与实验配置为依据。

拟合结果中的 `gravitySE` 是斜率回归标准误传播到重力估计的值。理想自动计时的残差可接近浮点误差；该结果描述确定性模型与直线的关系。仪器误差、真实摆角和系统修正依据分别从来源文件核对。

## 运行与独立验证

从仓库根目录运行以下命令。Python 环境按[使用指南](usage.md)安装，Node.js 用于执行与浏览器相同的 ES module。

```text
node --test tests/pendulum-model.test.mjs
python scripts/validate_pendulum_simulation.py
python -m pytest tests/test_simulation_publication.py
```

`validate_pendulum_simulation.py` 重新读取原报告数据，生成观测 JSON，并用 SciPy `ellipk` 和 DOP853 构造参考值。随后调用 Node.js 运行浏览器模型，比较周期、角位移、角速度、能量漂移及步长收敛结果。脚本输出的参考记录位于 [`docs/simulation/pendulum-reference.json`](simulation/pendulum-reference.json)。

在暂存目录核验时，显式指定输入根目录、输出根目录和模型文件：

```text
python scripts/validate_pendulum_simulation.py --repo-root <仓库路径> --output-root <暂存路径> --model <model.mjs路径>
```

`--references-only` 只生成参考计算，记录中的浏览器验证状态为 `not_run`；完整对照使用默认执行模式。判断一次核验时同时读取 `browser_verification.status`、`failures`、`tolerances`、`model_sha256`、生成器哈希和源文件哈希。

保持 Markdown 与页面可检索，更新资料后执行：

```text
python scripts/agent_catalog.py build
python scripts/agent_catalog.py build --check
python scripts/check_agent_docs.py
python scripts/build_pages.py
python scripts/check_pages.py --report .build/pages/verification.json
```

生成目录与 `llms.txt` 系列通过脚本同步。新的模型证据和网页入口进入实验资源目录；引用计算结果时附实验标识、模型版本、输入参数、单位、适用条件和 Git 提交。

## 前端验收

使用 HTTP 预览已构建站点，并保留 `/general-physics-lab/` 子路径。数学渲染由构建注入本地 MathJax；源页面中的 LaTeX 按标准语法维护。

表 3　交互与呈现检查

|检查对象|核验行为|
|---|---|
|参数输入|默认值、上下界、键盘操作、非法输入和组合参数|
|动画与时钟|播放、暂停、复位、切换后台、恢复前台|
|手动计时|起止时刻、暂停冻结、保存读数及参数变化后的状态|
|拟合筛选|至少三条记录、不同摆长、相同重力和摆角、来源分组|
|保存与导出|刷新恢复、清空记录、CSV/JSON 数值与单位、模型版本和来源|
|图表与公式|宋体和 Times New Roman、MathJax、轴标、图下注、表上题、线文间距和裁切|
|页面路径|项目子路径、模块 import、数据请求、文献与原报告入口|

比较控件变化前后的数值及图形，保存截图、运行参数和检查结果。数值验证与浏览器呈现验证分别记录，方便定位计算或显示问题。

## 原成稿回归清单

平台改动开始前，在独立运行目录保存原文件的 SHA-256；交付时按相同路径集合重新计算并比较。建议将基线、差异清单和浏览器记录放入 `.build/simulation-checks/<运行编号>/`。

- 单摆正式报告：`report/report.md`、`report/report.html` 和 `report/report.template.md`。
- Jupyter 成稿及 HTML：`notebooks/analysis.ipynb`、`notebooks/analysis.html`。
- Wolfram 成稿及包：登记表中的 Notebook、包内计算实现与正式 Paclet。
- 科学输入：`experiment.json`、`data/` 下规范 CSV 和来源记录。
- 已核验结果与实现：Python/Wolfram 结果 JSON、对照记录、Python 单摆模块。
- 入口变更：README、目录索引和新增网页文件单独审阅，检查链接与科学内容身份。

新增网页功能依赖的源哈希应与当前输入一致。若任务涉及原实验的科学修订，按原有双端重建与文稿验收流程形成新的基线；纯网页交互迭代使用既有成稿作为回归参照。
