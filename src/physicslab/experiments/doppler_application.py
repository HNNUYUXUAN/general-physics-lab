"""Static/dynamic spring stiffness using recorded Doppler periods."""
from pathlib import Path
import json
import numpy as np

def analyze(experiment_dir):
 root=Path(experiment_dir);cfg=json.loads((root/'experiment.json').read_text(encoding='utf-8'));p=cfg['parameters']
 stat=np.genfromtxt(root/'data/static.csv',delimiter=',',names=True,dtype=None,encoding='utf-8');dyn=np.genfromtxt(root/'data/periods.csv',delimiter=',',names=True)
 dx=(stat['position_cm']-p['initial_position_cm'])/100;force=stat['mass_g']*p['gravity_m_s2']/1000;ks=force/dx
 if len(ks)!=5 or len(dyn)!=13 or np.any(dx<=0):raise ValueError('Invalid spring observations.')
 mask=stat['included_in_source_mean'].astype(bool);kstat=float(np.mean(ks[mask]));T=float(np.mean(dyn['period_s']));ut=float(np.std(dyn['period_s'],ddof=1)/np.sqrt(13));kd=4*np.pi**2*(p['oscillator_mass_g']/1000)/T**2;uk=2*kd*ut/T
 x=dx[mask];y=force[mask];xc=x-x.mean();slope=float(xc@(y-y.mean())/(xc@xc));intercept=float(y.mean()-slope*x.mean())
 values=[('static_stiffness',kstat,'N/m','静态逐组劲度系数平均',None),('static_stiffness_all',float(np.mean(ks)),'N/m','全部五组静态比值平均',None),('static_fit_slope',slope,'N/m','源保留组静态拟合斜率',None),('static_fit_intercept',intercept,'N','源保留组静态拟合截距',None),('mean_period',T,'s','平均周期',ut),('period_sum',float(sum(dyn['period_s'])),'s','周期总和',None),('dynamic_stiffness',kd,'N/m','动态劲度系数',uk),('relative_difference',100*abs(kd-kstat)/kstat,'%','动静态相对差异',None)]
 metrics={key:dict(value=float(val),unit=unit,label=label,**({'uncertainty':float(u)} if u is not None else {})) for key,val,unit,label,u in values}
 return {'metrics':metrics,'tables':{'static':{'headers':['序号','组合','$m / \\mathrm{g}$','$x / \\mathrm{cm}$','$\\Delta x / \\mathrm{m}$','$F / \\mathrm{N}$','$k / (\\mathrm{N\\,m^{-1}})$','源报告平均值选用'],'rows':[[int(row['trial']),'$'+str(row['combination']).replace('m1','m_1').replace('m2','m_2').replace('m3','m_3')+'$',float(row['mass_g']),float(row['position_cm']),float(d),float(f),float(k),'保留' if keep else '剔除'] for row,d,f,k,keep in zip(stat,dx,force,ks,mask)]},'periods':{'headers':['序号','1','2','3','4','5','6','7'],'rows':[['$T / \\mathrm{s}$',*[float(v) for v in dyn['period_s'][:7]]],['序号',8,9,10,11,12,13,'—'],['$T / \\mathrm{s}$',*[float(v) for v in dyn['period_s'][7:]],'—']]}},'series':{'static_force':{'x':dx.tolist(),'y':force.tolist(),'x_label':'伸长量 / m','y_label':'载荷重力 / N','fit':True},'period_sequence':{'x':dyn['trial'].tolist(),'y':dyn['period_s'].tolist(),'x_label':'测量序号','y_label':'周期 / s'}},'notes':['静态主结果沿用源报告明确剔除第1组的选择，但保留该观测及全组平均作敏感性比较。','动态公式未计弹簧质量；周期A类及动态k不确定度未含质量和计时器系统误差。','静态散点图的全五组拟合仅供残差诊断；源保留组拟合参数另行计算。']}

def explore(key,result):
 import plotly.graph_objects as go
 if key!='spring-mass':raise KeyError(key)
 T=result['metrics']['mean_period']['value'];k=result['metrics']['dynamic_stiffness']['value'];ms=np.arange(51);curve=k+4*np.pi**2*(ms/3000)/T**2
 fig=go.Figure([go.Scatter(x=ms,y=curve,mode='lines',line={'color':'black'},name='有效质量模型'),go.Scatter(x=[0],y=[k],mode='markers',marker={'color':'black','size':11},name='选定弹簧质量')])
 fig.update_layout(template='plotly_white',font={'family':'Times New Roman, SimSun','size':18},width=900,height=580,xaxis_title='假设弹簧质量 / g',yaxis_title='固定周期所需劲度系数 / (N m⁻¹)',margin={'l':90,'r':30,'t':25,'b':150},showlegend=False,sliders=[{'active':0,'currentvalue':{'prefix':'假设弹簧质量 / g：'},'steps':[{'label':str(int(m)),'method':'restyle','args':[{'x':[[float(m)]],'y':[[float(v)]]},[1]]} for m,v in zip(ms,curve)]}]);fig.update_xaxes(showline=True,linecolor='black',gridcolor='#e3e3e3');fig.update_yaxes(showline=True,linecolor='black',gridcolor='#e3e3e3')
 return fig
