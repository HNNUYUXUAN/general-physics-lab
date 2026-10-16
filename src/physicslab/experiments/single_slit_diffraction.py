import csv,json,math,re
from pathlib import Path
import numpy as np
def read_rows(root,index):
    with (Path(root)/'data'/f'observations-{index:02d}.csv').open(encoding='utf-8-sig',newline='') as f:return list(csv.reader(f))[1:]
def angle(value):
    parts=[float(x) for x in re.findall(r'-?\d+(?:\.\d+)?',value)]
    return parts[0]+(parts[1]/60 if len(parts)>1 else 0)+(parts[2]/3600 if len(parts)>2 else 0)
def separation(a,b):return abs((a-b+180)%360-180)
def mean_a(v):return float(np.mean(v)),float(np.std(v,ddof=1)/math.sqrt(len(v)))
def metric(v,unit,label):return {'value':float(v),'unit':unit,'label':label}
def table(h,r):return {'headers':h,'rows':r}
def tex(s):
    s=str(s)
    if '°' in s:
        v=re.findall(r'\d+(?:\.\d+)?',s)
        if len(v)>=2:return '$'+v[0]+r'^{\circ}'+v[1]+r"^{\prime}"+'$'
    pairs={'θ₁':r'$\theta_1$','θ₂':r'$\theta_2$','θ₃':r'$\theta_3$','θ₄':r'$\theta_4$','θ':'$\\theta$','δᵢ':r'$\delta_i$','δmin,i':r'$\delta_{\min,i}$','φᵢ':r'$\varphi_i$','Aᵢ':'$A_i$'}
    for a,b in pairs.items():s=s.replace(a,b)
    return s
def source_table(root,index):
    with (Path(root)/'data'/f'observations-{index:02d}.csv').open(encoding='utf-8-sig',newline='') as f:r=list(csv.reader(f))
    return table([tex(s) for s in r[0]],[[tex(s) for s in row] for row in r[1:]])


def analyze(experiment_dir):
    scan=np.array([[float(v) for v in row] for row in read_rows(experiment_dir,1)]);dark=np.array([[float(v) for v in row] for row in read_rows(experiment_dir,2)]);wave=.0006328;distance=800.;width=dark[:,0]*wave*distance/dark[:,1];mean,spread=mean_a(width)
    slope=float(np.dot(dark[:,0],dark[:,1])/np.dot(dark[:,0],dark[:,0]));fitwidth=wave*distance/slope
    exact=dark[:,0]*wave*np.sqrt(distance**2+dark[:,1]**2)/dark[:,1]
    x=np.linspace(-10.5,10.5,1201);model=np.sinc(mean*x/(wave*distance))**2
    pred=np.sinc(mean*scan[:,0]/(wave*distance))**2;rmse=float(np.sqrt(np.mean((scan[:,1]-pred)**2)))
    return {'metrics':{'slit_width_mean_mm':metric(mean,'mm','各暗纹级次缝宽均值'),'slit_width_spread_sem_mm':metric(spread,'mm','级次估计均值的形式标准误'),'slit_width_origin_fit_mm':metric(fitwidth,'mm','暗纹位置过原点拟合缝宽'),'maximum_small_angle_correction_mm':metric(max(exact-width),'mm','使用精确sin几何的最大缝宽修正'),'scan_model_rmse':metric(rmse,'1','扫描与固定理论曲线均方根差')},'tables':{'table1':table(['位置 $x$ / mm','归一化光强 $I/I_0$'],scan.tolist()),'table2':table(['暗纹级数 $k$','中心距 $|x_k|$ / mm'],dark.tolist()),'table3':table(['$k$','$|x_k|$ / mm','$d$ / mm'],[[int(k),float(xx),round(float(d),8)] for (k,xx),d in zip(dark,width)])},'series':{'dark-fit':{'x':dark[:,0].tolist(),'y':dark[:,1].tolist(),'x_label':'暗纹级数 $k$','y_label':'暗纹中心距 $|x_k|$ / mm','label':'观测值','fit':True},'scan-observed':{'x':scan[:,0].tolist(),'y':scan[:,1].tolist(),'x_label':'扫描位置 $x$ / mm','y_label':'归一化光强 $I/I_0$','label':'记录中的归一化扫描'},'scan-model':{'model':True,'connect':True,'x':x.tolist(),'y':model.tolist(),'x_label':'屏上位置 $x$ / mm','y_label':'归一化强度 $I/I_0$','label':'暗纹测量均值缝宽的理论模型'}},'notes':['四级暗纹不是同一条件下的独立重复，形式标准误仅描述跨级离散，不作为完整不确定度。','源表只有归一化扫描，没有原始电流与暗电流，不能重新校核扣背景过程。','距离与波长不确定度未给；不将归一化模型拟合当额外测量。']}
def explore(key,result):
    if key!='slit-width':raise KeyError(key)
    import plotly.graph_objects as go
    d=result['metrics']['slit_width_mean_mm']['value'];obs=result['tables']['table1']['rows'];x=np.linspace(-10.5,10.5,1201);fig=go.Figure(go.Scatter(x=[r[0] for r in obs],y=[r[1] for r in obs],mode='markers',name='归一化扫描',marker=dict(color='black',symbol='circle-open',size=9)));steps=[]
    for i,factor in enumerate(np.round(np.arange(.5,1.501,.05),2)):
        fig.add_trace(go.Scatter(x=x,y=np.sinc(factor*d*x/(.0006328*800))**2,mode='lines',name='理想模型',visible=factor==1,line=dict(color='black',width=1.5)))
        mask=[True]+[False]*21;mask[i+1]=True;steps.append(dict(method='update',label=f'{factor:.2f}',args=[{'visible':mask}]))
    fig.update_layout(template='plotly_white',font=dict(family='Times New Roman, SimSun',size=18),height=540,margin=dict(l=80,r=30,t=30,b=110),xaxis_title='位置 x / mm',yaxis_title='归一化强度 I / I₀',sliders=[dict(active=10,steps=steps,currentvalue=dict(prefix='模型缝宽 / 暗纹估计均值 = '))]);return fig
