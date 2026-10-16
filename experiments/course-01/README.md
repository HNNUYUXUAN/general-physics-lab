# 普通物理实验 1

[项目首页](../../README.md) · [阅读与运行指南](../../docs/usage.md) · [源资料 PDF 总目录](../../pdf/README.md)

本课程整理 **8 个实验**。围绕运动规律、碰撞、密度与热量测量展开，从原始读数进入拟合、误差分析和物理模型。

点击实验名称进入完整入口，可选择报告阅读版、HTML 计算阅读版、规范数据和独立 Paclet 安装包。下表提供常用文件直达链接。

## 实验索引

|实验入口|阅读与对照|计算笔记本|
|---|---|---|
|[单摆测重力加速度](pendulum/README.md)|[报告](pendulum/report/report.md) · [源 PDF](../../pdf/course-01/%E5%8D%95%E6%91%86%E6%B5%8B%E9%87%8D%E5%8A%9B%E5%8A%A0%E9%80%9F%E5%BA%A6/%E7%89%9B%E9%A1%BF%E7%AC%AC%E4%BA%8C%E8%BF%90%E5%8A%A8%E5%AE%9A%E5%BE%8B%E6%B5%8B%E9%87%8D%E5%8A%9B%E5%8A%A0%E9%80%9F%E5%BA%A6%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A.pdf)|[Python](pendulum/notebooks/analysis.ipynb) · [Wolfram](../../notebook/paclets/PendulumLab/Notebooks/Pendulum.nb)|
|[多普勒效应的验证](doppler-verification/README.md)|[报告](doppler-verification/report/report.md) · [源 PDF](../../pdf/course-01/%E5%A4%9A%E6%99%AE%E5%8B%92%E6%95%88%E5%BA%94%E7%9A%84%E9%AA%8C%E8%AF%81/%E5%A4%9A%E6%99%AE%E5%8B%92%E6%95%88%E5%BA%94%E9%AA%8C%E8%AF%81%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A.pdf)|[Python](doppler-verification/notebooks/analysis.ipynb) · [Wolfram](../../notebook/paclets/DopplerVerificationLab/Notebooks/DopplerVerificationLab.nb)|
|[多普勒效应的应用](doppler-application/README.md)|[报告](doppler-application/report/report.md) · [源 PDF](../../pdf/course-01/%E5%A4%9A%E6%99%AE%E5%8B%92%E6%95%88%E5%BA%94%E7%9A%84%E5%BA%94%E7%94%A8/%E5%A4%9A%E6%99%AE%E5%8B%92%E6%95%88%E5%BA%94%E7%9A%84%E5%BA%94%E7%94%A8-%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A.pdf)|[Python](doppler-application/notebooks/analysis.ipynb) · [Wolfram](../../notebook/paclets/DopplerApplicationLab/Notebooks/DopplerApplicationLab.nb)|
|[牛顿第二定律的验证](newton-second-law/README.md)|[报告](newton-second-law/report/report.md) · [源 PDF](../../pdf/course-01/%E7%89%9B%E9%A1%BF%E7%AC%AC%E4%BA%8C%E5%AE%9A%E5%BE%8B%E7%9A%84%E9%AA%8C%E8%AF%81/%E7%89%9B%E9%A1%BF%E7%AC%AC%E4%BA%8C%E8%BF%90%E5%8A%A8%E5%AE%9A%E5%BE%8B%E9%AA%8C%E8%AF%81%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A.pdf)|[Python](newton-second-law/notebooks/analysis.ipynb) · [Wolfram](../../notebook/paclets/NewtonSecondLawLab/Notebooks/NewtonSecondLawLab.nb)|
|[碰撞规律的研究](collisions/README.md)|[报告](collisions/report/report.md) · [源 PDF](../../pdf/course-01/%E7%A2%B0%E6%92%9E%E8%A7%84%E5%BE%8B%E7%9A%84%E7%A0%94%E7%A9%B6/%E7%A2%B0%E6%92%9E%E8%A7%84%E5%BE%8B%E7%A0%94%E7%A9%B6%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A.pdf)|[Python](collisions/notebooks/analysis.ipynb) · [Wolfram](../../notebook/paclets/CollisionsLab/Notebooks/CollisionsLab.nb)|
|[热功当量的测量](mechanical-equivalent-heat/README.md)|[报告](mechanical-equivalent-heat/report/report.md) · [源 PDF](../../pdf/course-01/%E7%83%AD%E5%8A%9F%E5%BD%93%E9%87%8F%E7%9A%84%E6%B5%8B%E9%87%8F/%E7%83%AD%E5%8A%9F%E5%BD%93%E9%87%8F%E7%9A%84%E6%B5%8B%E9%87%8F%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A.pdf)|[Python](mechanical-equivalent-heat/notebooks/analysis.ipynb) · [Wolfram](../../notebook/paclets/MechanicalEquivalentHeatLab/Notebooks/MechanicalEquivalentHeatLab.nb)|
|[物质密度的测量](density/README.md)|[报告](density/report/report.md) · [源 PDF](../../pdf/course-01/%E7%89%A9%E8%B4%A8%E5%AF%86%E5%BA%A6%E7%9A%84%E6%B5%8B%E9%87%8F/%E7%89%A9%E8%B4%A8%E5%AF%86%E5%BA%A6%E6%B5%8B%E9%87%8F%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A.pdf)|[Python](density/notebooks/analysis.ipynb) · [Wolfram](../../notebook/paclets/DensityLab/Notebooks/DensityLab.nb)|
|[液体比汽化热的测量](vaporization-heat/README.md)|[报告](vaporization-heat/report/report.md) · [源 PDF](../../pdf/course-01/%E6%B6%B2%E4%BD%93%E6%AF%94%E6%B1%BD%E5%8C%96%E7%83%AD%E7%9A%84%E6%B5%8B%E9%87%8F/%E6%B6%B2%E4%BD%93%E6%AF%94%E6%B1%BD%E5%8C%96%E7%83%AD%E6%B5%8B%E9%87%8F%E5%AE%9E%E9%AA%8C%E6%8A%A5%E5%91%8A.pdf)|[Python](vaporization-heat/notebooks/analysis.ipynb) · [Wolfram](../../notebook/paclets/VaporizationHeatLab/Notebooks/VaporizationHeatLab.nb)|

报告和源 PDF 可直接在 GitHub 阅读。HTML 阅读版下载后在浏览器打开；重新计算需要对应的 Python 或 Wolfram 环境。
