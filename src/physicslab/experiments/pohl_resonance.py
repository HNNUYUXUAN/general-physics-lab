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
    cfg=json.loads((Path(experiment_dir)/'experiment.json').read_text(encoding='utf-8'));free=np.array([[float(v) for v in row] for row in read_rows(experiment_dir,1)]).reshape(-1,2);damp=np.array([[float(v) for v in row] for row in read_rows(experiment_dir,2)]);index=np.r_[damp[:,0],damp[:,3]];amplitude=np.r_[damp[:,1],damp[:,4]];period=np.r_[damp[:,2],damp[:,5]];time=np.r_[0,np.cumsum(period[:-1])];log=np.log(np.radians(amplitude));x=time-time.mean();slope=float(np.dot(x,log-log.mean())/np.dot(x,x));intercept=float(log.mean()-slope*time.mean());res=log-(intercept+slope*time);beta=-slope;ub=math.sqrt(float(np.dot(res,res))/8/float(np.dot(x,x)));bpair=float(np.mean(np.log(amplitude[:5]/amplitude[5:])))/(5*float(period.mean()));r2=1-float(np.dot(res,res)/np.dot(log-log.mean(),log-log.mean()));forced=np.array([[float(v) for v in row] for row in read_rows(experiment_dir,3)]);t0=np.array(cfg['parameters']['forced_reference_periods_s']);omega=2*np.pi/forced[:,0];omega0=2*np.pi/t0;ratio=t0/forced[:,0];phase=np.degrees(np.arctan2(-2*beta*omega,omega0**2-omega**2));phase_rmse=float(np.sqrt(np.mean((forced[:,2]-phase)**2)));free_mean=float(free[:,1].mean());w0=2*math.pi/free_mean;peak_ratio=math.sqrt(1-2*(beta/w0)**2);peak=int(np.argmax(forced[:,1]));outside=int(np.sum((forced[:,1]<min(free[:,0]))|(forced[:,1]>max(free[:,0]))))
    metrics={'damping_fit_per_s':metric(beta,'1/s','振幅包络衰减率'),'damping_residual_se_per_s':metric(ub,'1/s','衰减率残差标准误'),'damping_difference_per_s':metric(bpair,'1/s','五周期逐差衰减率'),'decay_intercept':metric(intercept,'1','弧度振幅对数截距'),'decay_r_squared':metric(r2,'1','对数衰减拟合决定系数'),'free_period_mean_s':metric(free_mean,'s','自由表周期均值'),'forced_peak_ratio':metric(ratio[peak],'1','已测幅度最大点频率比'),'forced_peak_amplitude_deg':metric(forced[peak,1],'deg','已测最大幅度'),'linear_model_peak_ratio':metric(peak_ratio,'1','按自由平均周期及衰减率的理论峰频比'),'phase_model_rmse_deg':metric(phase_rmse,'deg','指定参考周期下相位模型均方根差'),'out_of_free_amplitude_range_count':metric(outside,'1','超出自由周期表幅度范围的受迫点数')}
    tables={'table1':table([r'$\theta$ / °',r'$T_0$ / s',r'$\theta$ / °',r'$T_0$ / s',r'$\theta$ / °',r'$T_0$ / s'],free.reshape(4,6).tolist()),'table2':table(['$i$',r'$\theta_i$ / °','$T_i$ / s','$i+5$',r'$\theta_{i+5}$ / °','$T_{i+5}$ / s',r'$\ln(\theta_i/\theta_{i+5})$'],[[*row.tolist(),round(float(v),8)] for row,v in zip(damp,np.log(amplitude[:5]/amplitude[5:]))]),'table3':table(['受迫周期 / s','幅度 / °','指定参考周期 / s','实测相位 / °','重算理论相位 / °',r'$\omega/\omega_0$'],[[float(row[0]),float(row[1]),float(t),float(row[2]),round(float(ph),8),round(float(q),8)] for row,t,ph,q in zip(forced,t0,phase,ratio)])}
    return {'metrics':metrics,'tables':tables,'series':{'free-period':{'x':free[:,0].tolist(),'y':free[:,1].tolist(),'x_label':'自由振荡角幅度 / °','y_label':'周期 $T_0$ / s','label':'阻尼档0'},'decay-fit':{'x':time.tolist(),'y':log.tolist(),'x_label':'首记录后的累计时间 / s','y_label':r'$\ln(\theta/\mathrm{rad})$','label':'阻尼档2','fit':True},'forced-amplitude':{'x':ratio.tolist(),'y':forced[:,1].tolist(),'x_label':r'频率比 $\omega/\omega_0$','y_label':'稳态角幅度 / °','label':'阻尼档2'},'forced-phase':{'x':ratio.tolist(),'y':forced[:,2].tolist(),'x_label':r'频率比 $\omega/\omega_0$','y_label':'实测相位差 / °','label':'主记录平均相位'},'phase-theory':{'x':ratio.tolist(),'y':phase.tolist(),'x_label':r'频率比 $\omega/\omega_0$','y_label':'理论相位差 / °','label':'指定逐点参考周期'}},'notes':['衰减率beta量纲是s^-1，不是rad/s；角频率omega才以rad/s表示。','逐点参考周期采用源记录给定值作为模型参数，原始自由表外3点不能按普通内插验证。','相位实测列是原记录两次稳定读数的平均，未附单次读数，不重构原始重复。','观测峰与理论弱阻尼峰位置不同，稀疏测点和幅度依赖会影响定位，不能仅以阻尼解释。']}
def explore(key,result):
    if key!='damping-response':raise KeyError(key)
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    beta=result['metrics']['damping_fit_per_s']['value'];w0=2*math.pi/result['metrics']['free_period_mean_s']['value'];q=np.linspace(.85,1.15,1201);fig=make_subplots(rows=2,cols=1,shared_xaxes=True,vertical_spacing=.12);factors=np.round(np.arange(.5,2.001,.1),1);steps=[]
    for i,factor in enumerate(factors):
        b=beta*factor;response=1/np.sqrt((1-q*q)**2+(2*b*q/w0)**2);phase=np.degrees(np.arctan2(-2*b*q/w0,1-q*q))
        fig.add_trace(go.Scatter(x=q,y=response,mode='lines',visible=factor==1,line=dict(color='black',width=1.5),showlegend=False),row=1,col=1);fig.add_trace(go.Scatter(x=q,y=phase,mode='lines',visible=factor==1,line=dict(color='black',width=1.5),showlegend=False),row=2,col=1);mask=[False]*(len(factors)*2);mask[2*i:2*i+2]=[True,True];steps.append(dict(method='update',label=str(factor),args=[{'visible':mask}]))
    fig.update_layout(template='plotly_white',font=dict(family='Times New Roman, SimSun',size=18),height=720,margin=dict(l=95,r=30,t=30,b=110),sliders=[dict(active=5,steps=steps,currentvalue=dict(prefix='衰减率 / 实测拟合值 = '))]);fig.update_yaxes(title_text='相对静态位移的稳态幅度',row=1,col=1);fig.update_yaxes(title_text='理论相位 / °',range=[-180,0],row=2,col=1);fig.update_xaxes(title_text='频率比 ω / ω₀',row=2,col=1);return fig
