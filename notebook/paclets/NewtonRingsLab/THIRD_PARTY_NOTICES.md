# 第三方材料与版权说明

[许可划分](LICENSING.md) · [逐项机器清单](docs/third-party-materials.json) · [源PDF清单](pdf/verification.json)

## 源文稿

源资料共 **57 份 PDF：45 份实验主报告、12 份参考资料，210 页**。逐项清单保留来源DOCX、PDF路径、哈希、页数、正文署名与机构线索。源模板、摘录和嵌入图片继续适用其原权利。

正文中明确署名的报告作者为缪雨轩；这些报告的作者原创贡献适用 CC BY 4.0。其他源文件的作者或许可未在正文明确时，清单相应字段为 `null`，沿用原权利。PDF 的编辑器 `Author` 元数据单独记录，正文署名另列。

|材料组|来源与署名信息|许可范围|
|---|---|---|
|45 份实验主报告|21 份正文署名缪雨轩；24 份正文作者未明确|已确认署名作者的原创贡献按 CC BY 4.0；其他来源内容按清单保留原权利|
|12 份讲义、模板、数据分析与说明书|来源与实验归属逐份登记|原来源材料的权利及许可|
|QJ47 文件名的两份说明书|正文机构为杭州大华仪器制造有限公司；PDF 元数据标题为 DH6101 型电阻元件 V-A 特性实验仪|机构信息作为来源线索，权利人和许可未在正文明确|
|FB716-Ⅲ 设计性装置讲义|正文包含杭州精科仪器有限公司|机构信息作为来源线索，权利人和许可未在正文明确|

## 图像与学校标识

|路径或素材|来源|许可范围|
|---|---|---|
|`docs/assets/hnnu-logo.svg`|学校公共资料提供的“淮南师范学院-01.svg”，与所用源文件 SHA-256 一致|学校官方校徽与校名标识，标识相关权利由淮南师范学院保留|
|`docs/assets/physics-lab-cover.png`|imagegen 生成的单摆、电路与棱镜实验主题封面|项目可许可的封面与编排贡献为 CC BY 4.0|
|同轴电场、光敏器件、电阻伏安法与惠斯通电桥 SVG|依据对应源报告的物理关系重绘；同名副本位于各实验 Paclet|重绘贡献为 CC BY 4.0；源报告图片自身沿用原权利|
|各实验计算图与 README 概览|项目脚本根据规范结果生成|项目图表贡献为 CC BY 4.0|

学校标识、课程讲义和仪器说明书保持各自的来源身份。上述项目许可不向读者授予学校商标或其他第三方材料的再许可。

## HTML 与软件组件

HTML 的图形和公式显示使用以下组件。上游版权、许可及已有源内通知随组件保留；软件依赖由各自发布包提供其许可文本。

|组件|版本|交付方式|原许可|
|---|---|---|
|Plotly.js|4.1.1|embedded|[MIT](https://raw.githubusercontent.com/plotly/plotly.js/v4.1.1/LICENSE)|
|Jupyter nbconvert HTML template|7.17.2|embedded-template-and-css|[BSD-3-Clause](https://raw.githubusercontent.com/jupyter/nbconvert/v7.17.2/LICENSE)|
|RequireJS|2.1.10|HTML-CDN-reference-and-Pages-vendor|[MIT OR BSD-3-Clause](https://raw.githubusercontent.com/requirejs/requirejs/2.1.10/LICENSE)|
|MathJax|2.7.7|HTML-CDN-reference-and-Pages-vendor|[Apache-2.0](https://raw.githubusercontent.com/mathjax/MathJax/2.7.7/LICENSE)|
|Mermaid|11.10.0|conditional-CDN-import|[MIT](https://raw.githubusercontent.com/mermaid-js/mermaid/mermaid@11.10.0/LICENSE)|
|Mermaid ELK layout|0.1.9|conditional-CDN-import|[MIT](https://raw.githubusercontent.com/mermaid-js/mermaid/mermaid@11.10.0/LICENSE)|

原始 HTML 引用 RequireJS 与 MathJax CDN；Pages 将这两个组件作为站内资源提供，同时保留原发行版许可。版本、来源和逐文件哈希见 [vendor 清单](site/vendor/manifest.json)，完整许可位于 [MathJax LICENSE](site/vendor/mathjax-2.7.7/LICENSE) 和 [RequireJS LICENSE](site/vendor/requirejs-2.1.10/LICENSE)。MathJax 原发行字体随同该组件提供。

Mermaid 与 ELK 布局按图示需要加载。Plotly 代码内嵌于适用 Notebook HTML，保留原版权头部。Jupyter 导出模板和样式保留 Jupyter Development Team 的版权标识。

以下保留内嵌组件对应的完整上游许可文本。

### Plotly.js

来源：[Plotly.js 官方许可](https://raw.githubusercontent.com/plotly/plotly.js/v4.1.1/LICENSE)

```text
MIT License

Copyright (c) 2016-2024 Plotly Technologies Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
```

### Jupyter nbconvert HTML template

来源：[Jupyter nbconvert HTML template 官方许可](https://raw.githubusercontent.com/jupyter/nbconvert/v7.17.2/LICENSE)

```text
BSD 3-Clause License

- Copyright (c) 2001-2015, IPython Development Team
- Copyright (c) 2015-, Jupyter Development Team

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
```
