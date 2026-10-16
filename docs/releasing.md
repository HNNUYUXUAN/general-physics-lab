# 版本发布与维护

[在线实验](https://hnnuyuxuan.github.io/general-physics-lab/) · [GitHub Releases](https://github.com/HNNUYUXUAN/general-physics-lab/releases) · [许可范围](../LICENSING.md)

版本号在 `pyproject.toml`、引用信息和 Paclet 元数据中保持一致。发布对应一个 Git 标签，下载包的完整内容与 SHA-256 在 `release-manifest.json` 和 `SHA256SUMS.txt` 中记录。

## 发布内容

|下载文件|用途|
|---|---|
|`*-reading.zip`|完整在线阅读站点副本，附本机预览启动器、公式脚本和57份源PDF|
|`*-paclets.zip`|45个独立安装包与许可说明|
|`*-data.zip`|45项规范输入、参数、来源记录和实验机器目录|
|`release-manifest.json`|源码提交、资源哈希、已有交付记录及本次安装核验|
|`SHA256SUMS.txt`|校验下载文件的SHA-256|

完整源码与Jupyter、Wolfram Notebook可从同一Release的源码归档或对应标签获取。阅读包解压后运行 `python serve.py`，打开打印的本机地址；计算环境安装见[使用指南](usage.md)。

## 检查与打包

在仓库根目录执行：

```text
python scripts/package_release.py --license-paclets
python scripts/agent_catalog.py build
python -m pytest
python scripts/check_delivery.py --all
python scripts/execute_notebooks.py --all
wolframscript -file scripts/verify_release_paclets.wls
python scripts/build_pages.py
python scripts/check_pages.py
```

许可封装保留Paclet中现有计算代码、数据和Notebook字节，添加组成许可与第三方说明，并保存逐包核验记录。安装检查在新的WolframScript会话中逐包独立安装、核对输入和数值、读取Notebook并运行包测试。

README、许可、数据或安装包变化后，重新生成机器目录和网站。Pages构建将正式成稿复制到独立目录，再接入站内脚本和导航；站点检查验证链接、部署子路径及资源覆盖。前端检查包含数学显示、默认图形和控件改变后的响应。

提交经检查的源文件后，生成版本下载包：

```text
python scripts/package_release.py --version 0.1.0
```

输出位于 `.build/release/v0.1.0/`。发布说明列明实验数量、在线入口、许可与下载方式；标签指向清单记录的源码提交。GitHub Pages工作流从 `main` 的检查通过版本部署。
