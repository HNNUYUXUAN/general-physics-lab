"""One report outline, with computation expansions inserted in both notebooks."""
import re,json
from pathlib import Path
import nbformat as nbf

SETUP='''from pathlib import Path
import sys
start=Path.cwd().resolve()
ROOT=next(p for p in (start,*start.parents) if (p/"pyproject.toml").exists())
sys.path.insert(0,str(ROOT/"src"))
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sympy as sp
from IPython.display import display, Markdown, HTML
from physicslab.experiments.pendulum import load_data, analyze
from physicslab.experiments.interactive import show, measurements, fit_explorer, model_explorer, animation, amplitude_explorer
from physicslab.common.plots import fit_figure, trajectory_figure, scan_figure, apparatus_figure
from physicslab.common.theme import EXPORT_CSS
EXP=ROOT/"experiments/course-01/pendulum"
config,timing,diameters=load_data(EXP)
result=analyze(EXP)
display(HTML(EXPORT_CSS))
'''
# Each expansion contains the same prose and a native implementation per engine.
EXPANSIONS={
"实验原理":[
("符号推导与模型假设",r"""设摆球为质点、摆线无质量，忽略阻尼与驱动力。用符号运算解出 $g(k)$，并由一阶微分得到斜率标准误的传播公式：
$$u_g=\left|\frac{\partial g}{\partial k}\right|u_k=\frac{4\pi^2}{k^2}u_k.$$
这里的 $u_k$ 是回归斜率标准误；仪器误差仍需另行评定。""",
'''k,g,u_k=sp.symbols("k g u_k",positive=True)
g_of_k=sp.solve(sp.Eq(k,4*sp.pi**2/g),g)[0]
display(sp.Eq(g,g_of_k),sp.Eq(sp.Symbol("u_g"),sp.Abs(sp.diff(g_of_k,k))*u_k))''',
'PLSymbolicDerivation[]')],
"原始数据记录":[
("重复计时的离散程度",r"""从原始读数计算各组均值，再绘制 $t_{ij}-\bar t_i$。菜单可以选择测量组；连线只用于辨认同一组的重复读数。""",
'show(measurements(timing),first=True)','PLMeasurementExplorer[]')],
"数据处理":[
("拟合、残差与数据敏感性",r"""用全部六组数据重算斜率、截距及残差。菜单可暂时移去一组观察参数变化；正式估计使用全部六组数据。图中误差条是 $u_A(T^2)$。""",
'show(fit_explorer(result))','PLFitExplorer[]')],
"误差分析":[
("不确定度的数值传播",r"""先计算重复计时均值的 A 类标准不确定度，再依次传播到 $T$ 与 $T^2$。保留未修约数值参与拟合。""",
r'''p=result["processed"]
display(pd.DataFrame([[x["run_id"],x["time_mean_u_a_s"],x["period_u_a_s"],x["period_squared_u_a_s2"]] for x in p],columns=["组号",r"$u_A(\bar t)/\mathrm{s}$",r"$u_A(T)/\mathrm{s}$",r"$u_A(T^2)/\mathrm{s^2}$"]).style.hide(axis="index").format({r"$u_A(\bar t)/\mathrm{s}$":"{:.6f}",r"$u_A(T)/\mathrm{s}$":"{:.7f}",r"$u_A(T^2)/\mathrm{s^2}$":"{:.7f}"}))''',
'PLTable["processed"][[1,2]]'),
("非线性单摆的数值求解",r"""小角度公式的适用性可由完整运动方程检验：
$$\ddot\theta+\frac{g}{L'}\sin\theta=0,\qquad \theta(0)=\theta_0,\qquad \dot\theta(0)=0.$$
探索初始摆角 $5^\circ$、$20^\circ$、$45^\circ$、$60^\circ$ 及不同摆长，比较非线性解与小角度解。默认情景取 $L'=1\,\mathrm m$、$\theta_0=20^\circ$、时长 $10\,\mathrm s$，重力参数使用本次拟合值。实际实验摆幅未记录，这些情景用于说明模型影响。""",
'show(model_explorer(config,result["metrics"]["gravity_fit"]["value"]))\ntrajectory_figure(result)\nplt.show()','PLModelExplorer[]'),
("单摆运动与相空间",r"""播放或选择时间，观察摆球位置与相图中的同一状态。取 $L'=1\,\mathrm m$、$\theta_0=20^\circ$，初始角速度为零；经过平衡位置时角速度的绝对值最大。""",
'show(animation(result))','PLModelView[]'),
("摆角扫描与重力估计偏差",r"""精确周期写为
$$T_{\mathrm{exact}}=4\sqrt{\frac{L'}g}\,K\!\left(\sin^2\frac{\theta_0}{2}\right),\qquad \frac{g_{\mathrm{est}}}{g}=\left(\frac{T_0}{T_{\mathrm{exact}}}\right)^2.$$
其中 $K(m)$ 使用参数 $m$ 的定义，$T_0$ 为小角度周期。滑块选中同一摆角，联动显示周期增量与重力估计偏差；灰带标明 $0^\circ$ 至 $5^\circ$ 的小摆角范围。""",
'show(amplitude_explorer(config,result["metrics"]["gravity_fit"]["value"]))\nscan_figure(result)\nplt.show()','PLAmplitudeExplorer[]'),
("周期与机械能校核",r"""以椭圆积分周期核对常微分方程积分得到的周期，并检查无阻尼模型的机械能守恒：
$$\frac{E}{m}=\frac12(L'\dot\theta)^2+gL'(1-\cos\theta).$$
下列误差用于评估数值计算，不替代实验不确定度。""",
'''s=result["simulation"]
period_error=abs(s["period_ode_s"]/s["period_exact_s"]-1)
assert period_error<1e-7 and s["relative_energy_drift"]<1e-7
display(pd.DataFrame([["数值周期与精确周期相对差",period_error],["机械能相对漂移",s["relative_energy_drift"]]],columns=["检查","数值"]).style.hide(axis="index").format({"数值":"{:.3e}"}))''',
'With[{s=PLAnalyze[]["simulation"]},Grid[{{"数值检查","相对误差"},{"数值周期与精确周期",ScientificForm[Abs[s["period_ode_s"]/s["period_exact_s"]-1],3]},{"机械能相对漂移",ScientificForm[s["relative_energy_drift"],3]}},Frame->All]]')
]}

CAPTIONS={
 "重复计时的离散程度":("figure","图 1　重复计时的离散程度"),
 "拟合、残差与数据敏感性":("figure","图 3　拟合参数与残差的敏感性分析"),
 "不确定度的数值传播":("table","表 5　重复计时不确定度的传播"),
 "非线性单摆的数值求解":("figure","图 4　非线性单摆与小角度近似的比较"),
 "单摆运动与相空间":("figure","图 5　单摆运动与相空间"),
 "摆角扫描与重力估计偏差":("figure","图 6　初始摆角对周期与重力估计的影响"),
 "周期与机械能校核":("table","表 6　周期与机械能的数值校核")}

def blocks(text):
    text=re.sub(r'(\$\$.*?\$\$)',r'\n\n\1\n\n',text,flags=re.S)
    out=[]
    for b in re.split(r'\n\s*\n',text.strip()):
        if b.startswith('#'):
            m=re.match(r'(#+) (.*)',b);out.append(dict(type='heading',level=len(m[1]),text=m[2]))
        elif re.match(r'^[图表] \d+\s',b):out.append(dict(type='caption',text=b))
        elif b.startswith('|'):
            rows=[[x.strip() for x in line.strip().strip('|').split('|')] for line in b.splitlines()]
            out.append(dict(type='table',rows=[rows[0],*rows[2:]]))
        elif b.startswith('!['):out.append(dict(type='figure',text='fit'))
        elif b.startswith('$$'):out.append(dict(type='math',text=b.strip('$').strip()))
        else:out.append(dict(type='text',text=b))
    return out

def narrative(root):
    text=(root/'experiments/course-01/pendulum/report/report.md').read_text(encoding='utf-8').replace('图 1　周期平方与有效摆长的线性拟合及残差','图 2　周期平方与有效摆长的线性拟合及残差')
    chunks=re.split(r'(?=^#{2,3} )',text,flags=re.M)
    entries=[];pending=None
    for chunk in chunks:
        first=chunk.splitlines()[0]
        name=re.sub(r'^#+ ','',first)
        if first.startswith('## '):
            if pending:
                for expansion in EXPANSIONS.get(pending,[]):entries.append(('expansion',expansion))
            pending=name
        entries.append(('report',chunk))
        if name=='误差分析':
            for expansion in EXPANSIONS[name]:entries.append(('expansion',expansion))
    if pending:
        for expansion in EXPANSIONS.get(pending,[]):entries.append(('expansion',expansion))
    return entries

def export_wolfram(root):
    payload=[]
    for kind,value in narrative(root):
        if kind=='report':payload.extend(blocks(value))
        else:
            title,prose,py,wl=value
            payload.extend([dict(type='heading',level=4,text=title),*blocks(prose)])
            cap=CAPTIONS.get(title)
            if cap and cap[0]=='table':payload.append(dict(type='caption',text=cap[1]))
            payload.append(dict(type='compute',text=wl))
            if cap and cap[0]=='figure':payload.append(dict(type='caption',text=cap[1]))
    def runs(text):
        text=re.sub(r'\[([^\]]+)\]\([^)]+\)',r'\1',text).replace('**','')
        return [dict(kind='math' if part.startswith('$') else 'text',text=part.strip('$') if part.startswith('$') else part) for part in re.split(r'(\$[^$]+\$)',text) if part]
    for block in payload:
        if block['type'] in ('text','heading','caption'):block['runs']=runs(block['text'])
        if block['type']=='table':block['runs']=[[runs(cell) for cell in row] for row in block['rows']]
    path=root/'notebook/paclets/PendulumLab/data/report.json' 
    path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')

def build(root):
    root=Path(root);cells=[]
    cells.append(nbf.v4.new_code_cell(SETUP,metadata={"jupyter":{"source_hidden":True},"tags":["setup"]}))
    for kind,value in narrative(root):
        if kind=='report':
            parts=re.split(r'(!\[[^\]]*\]\([^)]+\))',value)
            for part in parts:
                if part.startswith('!['):
                    cells.append(nbf.v4.new_code_cell('fit_figure(result)\nplt.show()',metadata={"jupyter":{"source_hidden":True},"tags":["report-figure"]}))
                elif part.strip():cells.append(nbf.v4.new_markdown_cell(part))
        else:
            title,prose,py,wl=value
            cells.append(nbf.v4.new_markdown_cell('#### '+title+'\n\n'+prose))
            cap=CAPTIONS.get(title)
            if cap and cap[0]=='table':cells.append(nbf.v4.new_markdown_cell(cap[1]))
            cells.append(nbf.v4.new_code_cell(py,metadata={"jupyter":{"source_hidden":True}}))
            if cap and cap[0]=='figure':cells.append(nbf.v4.new_markdown_cell(cap[1]))
    for i,c in enumerate(cells):c['id']=f'pendulum-{i:03}'
    nb=nbf.v4.new_notebook(cells=cells,metadata={"kernelspec":{"name":"python3","display_name":"Python 3","language":"python"},"language_info":{"name":"python"},"physicslab":{"report_outline":"DOCX","chinese_font":"SimSun","latin_font":"Times New Roman"}})
    path=root/'experiments/course-01/pendulum/notebooks/analysis.ipynb'
    nbf.validate(nb);nbf.write(nb,path);return path
