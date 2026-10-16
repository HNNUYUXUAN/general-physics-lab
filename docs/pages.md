# 网页阅读与交互

站点地址为 **https://hnnuyuxuan.github.io/general-physics-lab/**。首页、课程和实验入口沿仓库 README 组织，报告与计算 HTML 可以直接打开；滑块、菜单、曲线提示和缩放保留在计算阅读版中。

|内容|站点路径|
|---|---|
|首页|`/general-physics-lab/`|
|课程目录|`/general-physics-lab/experiments/index.html`|
|实验入口|`/general-physics-lab/experiments/course-NN/slug/index.html`|
|计算与交互|`/general-physics-lab/experiments/course-NN/slug/notebooks/analysis.html`|
|完整报告|`/general-physics-lab/experiments/course-NN/slug/report/report.html`|
|源 PDF|`/general-physics-lab/pdf/` 下的原目录与文件名|
|许可与来源|`/general-physics-lab/licensing.html`、`third-party-notices.html`|
|Agent 导览|`/general-physics-lab/llms.txt`、`llms-full.txt`、`docs/experiments.json`|

例如 [RLC 计算阅读版](https://hnnuyuxuan.github.io/general-physics-lab/experiments/course-03/rlc-resonance/notebooks/analysis.html) 可切换电容和品质因数，同时观察幅频与相频响应。需要编辑 Python 或 Wolfram 计算时，从实验入口下载对应 Notebook 或 Paclet；下载链接指向 GitHub 中的正式文件。

## 构建与本地核验

在仓库根目录安装项目依赖后运行：

```powershell
.\.venv\Scripts\python.exe scripts/build_pages.py
.\.venv\Scripts\python.exe scripts/check_pages.py --report .build/pages/verification.json
```

输出为 `.build/pages/site/`，保存构建清单 `build-manifest.json`。构建读取正式成稿，生成带导航和许可入口的网页副本；实验报告、Notebook 及其保存输出保留各自源文件。

本地按 GitHub 项目子路径预览，可在 `.build/pages/preview/` 下创建 `general-physics-lab` 指向站点输出的目录链接，或将站点复制到同名子目录，然后从预览根启动：

```powershell
python -m http.server 8000 --bind 127.0.0.1 --directory .build/pages/preview
```

打开 `http://127.0.0.1:8000/general-physics-lab/`，检查首页导航、实验图表、公式和控件。输出路径可通过 `--output` 指定，站点基址可通过 `--base-url` 指定；`.build/pages/` 中带生成标记的站点目录可以重复构建，其他输出目录需为空。

## 浏览器资源与检查

站内固定使用 MathJax **2.7.7** 与 RequireJS **2.1.10**，运行资源和许可证位于 `site/vendor/`。MathJax 使用 packed 发行目录、完整配置和扩展、jax、语言资源与现代字体，页面配置为 `TeX-AMS_CHTML-full,Safe`；运行清单见 `manifest.json`。构建逐文件核对来源版本、字节数和 SHA-256，随后复制到站点的 `vendor/`。MathJax 的字体随其发行版提供；宋体和 Times New Roman 由阅读设备使用本机字体。

计算 HTML 已内嵌 Plotly，构建保留现有交互初始化，仅将 MathJax 与 RequireJS 的 CDN 入口替换为本站资源。首页和各文档使用同一数学运行时。导航、规范 URL、`sitemap.xml` 和 `robots.txt` 由站点构建生成。

图内数学标题由构建逐页登记。弦振动的归一化位移轴使用 `site/assets/plot-math.js` 调用本地 MathJax 2 的 SVG 输出，保留正文 CommonHTML；菜单切换与窗口调整后重新定位数学标题。原始 HTML 与 Notebook 保留正式成稿，发布副本的标题转换和运行资源记录在构建清单中。

`check_pages.py` 核对 45 个实验入口、45 份报告、45 份计算 HTML、57 份 PDF、全部本地链接、站点子路径、数学运行时、许可证、资源哈希、Plotly 初始化数量以及总大小。站点输出采用明确的资源白名单；Notebook 和 Paclet 下载由 GitHub 提供。

## GitHub Pages 工作流

[Pages workflow](../.github/workflows/pages.yml) 在 `main` 更新或手动触发时执行：安装依赖 → 测试与文档同步检查 → 构建 → 站点检查 → 上传 Pages 产物 → 部署。仓库 Settings → Pages 的构建来源设为 **GitHub Actions**。

构建失败在对应步骤报告错误并返回非零状态。核验记录作为 `pages-validation` 工作流产物保存，部署地址由 `github-pages` 环境记录。Python/Wolfram 的完整重算流程见[复现指南](agent-reproduction.md)。
