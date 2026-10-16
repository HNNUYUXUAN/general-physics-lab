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
    pairs={'αB':r'$\alpha_B$','θ₁':r'$\theta_1$','θ₂':r'$\theta_2$','θ₃':r'$\theta_3$','θ₄':r'$\theta_4$','θ':'$\\theta$','δᵢ':r'$\delta_i$','δmin,i':r'$\delta_{\min,i}$','φᵢ':r'$\varphi_i$','Aᵢ':'$A_i$'}
    for a,b in pairs.items():s=s.replace(a,b)
    return s
def source_table(root,index):
    with (Path(root)/'data'/f'observations-{index:02d}.csv').open(encoding='utf-8-sig',newline='') as f:r=list(csv.reader(f))
    return table([tex(s) for s in r[0]],[[tex(s) for s in row] for row in r[1:]])


def analyze(experiment_dir):
    brew=np.array([angle(row[1]) for row in read_rows(experiment_dir,1)]);angles=np.array([[float(v) for v in row] for row in read_rows(experiment_dir,2)]);mean,ua=mean_a(brew);n=math.tan(math.radians(mean));un=(1+n*n)*math.radians(ua)
    x=np.cos(np.radians(angles[:,0]))**2;y=angles[:,1];xc=x-x.mean();slope=float(np.dot(xc,y-y.mean())/np.dot(xc,xc));background=float(y.mean()-slope*x.mean());prediction=slope*x+background;res=y-prediction;r2=1-float(np.dot(res,res)/np.dot(y-y.mean(),y-y.mean()))
    metrics={'brewster_angle_deg':metric(mean,'deg','布儒斯特角均值'),'brewster_type_a_arcmin':metric(ua*60,'arcmin','布儒斯特角均值A类'),'glass_refractive_index':metric(n,'1','玻璃折射率'),'glass_index_type_a':metric(un,'1','角度重复性传播分量'),'malus_amplitude_ma':metric(slope,'mA','马吕斯拟合幅度'),'malus_background_ma':metric(background,'mA','拟合背景'),'malus_r_squared':metric(r2,'1','马吕斯拟合决定系数')}
    return {'metrics':metrics,'tables':{'table1':source_table(experiment_dir,1),'table2':table([r'检偏器角 $\theta$ / °','光电流 $I$ / mA'],angles.tolist()),'table3':table([r'$\theta$ / °',r'$\cos^2\theta$','实测 $I$ / mA','拟合 $I$ / mA'],[[float(a),round(float(xx),8),float(yy),round(float(pp),8)] for (a,yy),xx,pp in zip(angles,x,prediction)])},'series':{'malus-fit':{'x':x.tolist(),'y':y.tolist(),'x_label':r'$\cos^2\theta$','y_label':'光电流 $I$ / mA','label':'观测值','fit':True}},'notes':['布儒斯特角只传播重复性；未含零点、仪器、玻璃表面分量。','马吕斯等权拟合没有光电流和角度逐点误差，不给完整参数不确定度。','波片插入后的状态没有定量记录，不据此重建实测偏振椭圆。']}
def explore(key,result):
    if key!='malus-offset':raise KeyError(key)
    import plotly.graph_objects as go
    a=result['metrics']['malus_amplitude_ma']['value'];b=result['metrics']['malus_background_ma']['value'];obs=result['tables']['table2']['rows'];x=np.linspace(0,90,361);fig=go.Figure(go.Scatter(x=[r[0] for r in obs],y=[r[1] for r in obs],mode='markers',name='观测值',marker=dict(color='black',symbol='circle-open',size=9)))
    steps=[]
    for i,offset in enumerate(range(-10,11)):
        fig.add_trace(go.Scatter(x=x,y=a*np.cos(np.radians(x-offset))**2+b,mode='lines',name='模型',visible=offset==0,line=dict(color='black',width=1.5)))
        mask=[True]+[False]*21;mask[i+1]=True;steps.append(dict(method='update',label=str(offset),args=[{'visible':mask}]))
    fig.update_layout(template='plotly_white',font=dict(family='Times New Roman, SimSun',size=18),height=530,margin=dict(l=80,r=30,t=30,b=110),xaxis_title='检偏器角 θ / °',yaxis_title='光电流 I / mA',sliders=[dict(active=10,steps=steps,currentvalue=dict(prefix='模型零点偏移 θ₀ / ° = '))]);return fig
