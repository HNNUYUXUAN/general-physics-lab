# 单摆测重力加速度

普通物理实验 1 · 缪雨轩 · 2414050120

| 成果 | 文件 |
| --- | --- |
| 完整实验报告 | [report.md](report/report.md) |
| 报告排版阅读 | [report.html](report/report.html) |
| 浏览器交互阅读 | [analysis.html](notebooks/analysis.html) |
| Python 计算与模型探索 | [analysis.ipynb](notebooks/analysis.ipynb) |
| Wolfram 计算与交互探索 | [Pendulum.nb](../../../notebook/paclets/PendulumLab/Notebooks/Pendulum.nb) |
| 双端数值核验 | [verification.json](results/verification.json) |
| 数据来源与校核问题 | [provenance.json](data/provenance.json) |

数据为源实验报告记录的 18 条计时与 6 条摆球直径观测。首次使用源 Paclet 前，运行项目根目录的 `python scripts/pipeline.py prepare`；完整构建使用 `python scripts/pipeline.py all`。

源包保留可编辑 Wolfram 代码；构建产出的安装包位于 `notebook/paclets/PendulumLab/dist/PendulumLab-0.1.0.paclet`。安装后可调用 `Needs["PendulumLab`"]`、`PLNotebookPath[]` 和 `PLOpenNotebook[]`。

实验分析与模型情景分别展示；仪器 B 类不确定度、实际摆幅记录和当地重力参考值的独立标定依据尚未确认。详情见报告的误差分析。

## 交互操作

Jupyter 运行全部单元后，可用菜单筛选重复计时、暂不纳入某组拟合数据、选择摆角与摆长情景；动画支持播放、暂停和时间拖动，摆角扫描支持滑块定位。交互阅读版内嵌绘图库，浏览器可直接打开；公式排版由阅读器提供。GitHub 静态预览显示保留的静态图，完整交互请使用可信的本地 Notebook 或 HTML。

Wolfram Notebook 提供对应的原生菜单和滑块，并能连续调整摆长与摆角、播放时间动画、切换小角度解。输入单元默认折叠，可通过单元括号展开；首次打开请求值全部单元。计算实现位于独立 Paclet 上下文中。

## 成稿规范

三份成稿共用原 DOCX 的七个主章节。Notebook 在实验原理、原始数据记录、数据处理及误差分析中展开符号推导、拟合、数值求解和参数探索。中文使用宋体（SimSun），西文及数字使用 Times New Roman；公式采用 LaTeX／原生数学排版，图表采用黑白线型和点型。重建正式图表需本机安装这两种字体；字体文件不随项目分发。Markdown 的字体由阅读器决定，指定字体的报告预览见 report.html。
