"""Momentum and post-collision velocity ratios with explicit missing-data limits."""
from pathlib import Path
import json
import numpy as np

def collision_velocities(m1,m2,v10,v20,e):
 return ((m1-e*m2)*v10+(1+e)*m2*v20)/(m1+m2),((1+e)*m1*v10+(m2-e*m1)*v20)/(m1+m2)

def analyze(experiment_dir):
 root=Path(experiment_dir);cfg=json.loads((root/'experiment.json').read_text(encoding='utf-8'));p=cfg['parameters'];m1=p['mass1_g']/1000;m2=p['mass2_g']/1000
 ine=np.genfromtxt(root/'data/inelastic.csv',delimiter=',',names=True);ela=np.genfromtxt(root/'data/elastic.csv',delimiter=',',names=True)
 v0=ine['incident_cm_s']/100;vc=ine['common_cm_s']/100;v1=(ela['v1_first_cm_s']+ela['v1_second_cm_s'])/200;v2=ela['v2_cm_s']/100
 if len(ine)!=5 or len(ela)!=5 or np.any(v0<=0) or np.any(v1<=0):raise ValueError('Invalid collision observations.')
 pin=m1*v0;pout=(m1+m2)*vc;eta=100*(pin-pout)/pin;ein=.5*m1*v0**2;eout=.5*(m1+m2)*vc**2;loss=100*(ein-eout)/ein
 theory=2*m1/(m1-m2);ratios=v2/v1;delta=100*(ratios-theory)/theory
 inferred_v0=(m1*v1+m2*v2)/m1;conditional_e=(v2-v1)/inferred_v0
 vals=[('mass_total',m1+m2,'kg','系统总质量'),('mean_momentum_deviation',np.mean(eta),'%','非弹性动量平均相对亏损'),('max_momentum_deviation',np.max(eta),'%','非弹性动量最大相对亏损'),('mean_energy_loss',np.mean(loss),'%','非弹性动能平均损失率'),('theoretical_energy_loss',100*m2/(m1+m2),'%','理想粘合碰撞动能损失率'),('theoretical_velocity_ratio',theory,'1','理想弹性碰撞后速度比'),('mean_velocity_ratio',np.mean(ratios),'1','测得碰后速度比平均'),('mean_absolute_ratio_deviation',np.mean(np.abs(delta)),'%','速度比平均相对差异'),('mean_conditional_restitution',np.mean(conditional_e),'1','假定动量守恒的恢复系数平均')]
 metrics={k:{'value':float(v),'unit':unit,'label':label} for k,v,unit,label in vals}
 tables={'inelastic_observations':{'headers':['序号','$v_{10} / (\\mathrm{cm\\,s^{-1}})$','$v_{\\mathrm{c}} / (\\mathrm{cm\\,s^{-1}})$'],'rows':[[int(row['trial']),float(row['incident_cm_s']),float(row['common_cm_s'])] for row in ine]},'elastic_observations':{'headers':['序号','滑块1速度第一次 / (cm s⁻¹)','滑块2速度 / (cm s⁻¹)','滑块1速度第二次 / (cm s⁻¹)'],'rows':[[int(row['trial']),float(row['v1_first_cm_s']),float(row['v2_cm_s']),float(row['v1_second_cm_s'])] for row in ela]},'momentum':{'headers':['序号','碰前动量 / (kg m s⁻¹)','碰后动量 / (kg m s⁻¹)','动量相对亏损 / %','碰前动能 / J','碰后动能 / J','动能损失 / %'],'rows':[[i+1,*[float(x[i]) for x in (pin,pout,eta,ein,eout,loss)]] for i in range(5)]},'ratios':{'headers':['序号','滑块1均速 / (cm s⁻¹)','滑块2速度 / (cm s⁻¹)','测得速度比','相对理论比值差异 / %','条件恢复系数'],'rows':[[i+1,float(v1[i]*100),float(v2[i]*100),float(ratios[i]),float(delta[i]),float(conditional_e[i])] for i in range(5)]}}
 series={'momentum_deviation':{'x':[1,2,3,4,5],'y':eta.tolist(),'x_label':'测量序号','y_label':'动量相对亏损 / %'},'velocity_ratio':{'x':[1,2,3,4,5],'y':ratios.tolist(),'x_label':'测量序号','y_label':'碰后速度比'}}
 return {'metrics':metrics,'tables':tables,'series':series,'notes':['非弹性数据按重撞轻、轻块初始静止和碰后粘合处理。','弹性组缺碰前速度，无法独立验证动量与动能守恒或直接测e。','条件恢复系数借助假定动量守恒反推初速度，属于模型诊断。']}

def explore(key,result):
 import plotly.graph_objects as go
 if key!='restitution':raise KeyError(key)
 total=result['metrics']['mass_total']['value'];loss=result['metrics']['theoretical_energy_loss']['value']/100;m2=total*loss;m1=total-m2;v0=result['tables']['inelastic_observations']['rows'][0][1]/100
 es=np.linspace(0,1,101);v1,v2=collision_velocities(m1,m2,v0,0,es);a,b=collision_velocities(m1,m2,v0,0,1)
 fig=go.Figure([go.Scatter(x=es,y=v1,mode='lines',line={'color':'black'},name='滑块1'),go.Scatter(x=es,y=v2,mode='lines',line={'color':'#626262','dash':'dash'},name='滑块2'),go.Scatter(x=[1,1],y=[a,b],mode='markers',marker={'color':'black','size':10},name='选定模型')])
 fig.update_layout(template='plotly_white',font={'family':'Times New Roman, SimSun','size':18},width=900,height=580,xaxis_title='恢复系数 e',yaxis_title='碰后速度 / (m s⁻¹)',margin={'l':85,'r':30,'t':25,'b':150},legend={'orientation':'h','y':1.05},sliders=[{'active':100,'currentvalue':{'prefix':'恢复系数：'},'steps':[{'label':f'{e:.2f}','method':'restyle','args':[{'x':[[float(e),float(e)]],'y':[[float(x),float(y)]]},[2]]} for e,x,y in zip(es,v1,v2)]}]);fig.update_xaxes(showline=True,linecolor='black',gridcolor='#e3e3e3');fig.update_yaxes(showline=True,linecolor='black',gridcolor='#e3e3e3')
 return fig
