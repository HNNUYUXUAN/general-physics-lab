"""Reanalysis of reported angular accelerations and independently known geometry."""
from pathlib import Path
import json,csv
import numpy as np
def analyze(experiment_dir):
 root=Path(experiment_dir);cfg=json.loads((root/'experiment.json').read_text(encoding='utf-8'));src=cfg['source_intermediates'];reported=cfg['source_reported_inertia_kg_m2']
 with (root/'data/geometry.csv').open(encoding='utf-8') as f:geom={row['quantity']:float(row['value']) for row in csv.DictReader(f)}
 beta=np.array(src['angular_accelerations_rad_s2'],dtype=float)
 if beta.shape!=(6,4) or not np.isfinite(beta).all():raise ValueError('Expected six four-value reported intermediate sets.')
 means=beta.mean(axis=1);jr=.5*geom['ring_mass_kg']*(geom['ring_outer_radius_m']**2+geom['ring_inner_radius_m']**2);jc0=.5*geom['cylinder_mass_kg']*geom['cylinder_radius_m']**2;jc=jc0+geom['cylinder_mass_kg']*geom['offset_m']**2
 ring=reported['platform_ring']-reported['platform'];cylinder=(reported['platform_two_cylinders']-reported['platform'])/2
 metrics={f'beta_mean_{i+1}':{'value':float(mean),'unit':'rad/s^2','label':f'第{i+1}组已报角加速度平均'} for i,mean in enumerate(means)}
 vals=[('ring_inertia_from_reported_totals',ring,'kg m^2','已报总惯量之差所得圆环惯量'),('cylinder_inertia_from_reported_totals',cylinder,'kg m^2','已报总惯量之差所得单柱惯量'),('ring_inertia_theory',jr,'kg m^2','几何模型圆环惯量'),('cylinder_center_inertia',jc0,'kg m^2','几何模型单柱中心轴惯量'),('cylinder_offset_inertia_theory',jc,'kg m^2','几何模型单柱偏轴惯量'),('ring_relative_deviation',100*(ring-jr)/jr,'%','圆环已报结果相对几何差异'),('cylinder_relative_deviation',100*(cylinder-jc)/jc,'%','单柱已报结果相对几何差异'),('parallel_axis_contribution',geom['cylinder_mass_kg']*geom['offset_m']**2,'kg m^2','单柱平行轴附加项')]
 for key,val,unit,label in vals:metrics[key]={'value':float(val),'unit':unit,'label':label}
 names=['空载物台','空载物台','载物台与圆环','载物台与圆环','载物台与两圆柱','载物台与两圆柱'];states=['匀减速','匀加速']*3
 tables={'geometry':{'headers':['物理量','数值','单位'],'rows':[['圆环质量',geom['ring_mass_kg'],'kg'],['圆环外半径',geom['ring_outer_radius_m'],'m'],['圆环内半径',geom['ring_inner_radius_m'],'m'],['单柱质量',geom['cylinder_mass_kg'],'kg'],['单柱半径',geom['cylinder_radius_m'],'m'],['偏轴距离',geom['offset_m'],'m'],['塔轮标称半径',geom['tower_radius_m'],'m']]},'beta':{'headers':['对象','状态','逐差1','逐差2','逐差3','逐差4','复算平均 / (rad s⁻²)'],'rows':[[name,state,*row.tolist(),float(mean)] for name,state,row,mean in zip(names,states,beta,means)]},'reported_totals':{'headers':['项目','已报总惯量 / (kg m²)'],'rows':[['空载物台',reported['platform']],['载物台与圆环',reported['platform_ring']],['载物台与两圆柱',reported['platform_two_cylinders']]]},'comparison':{'headers':['对象','由已报总惯量相减 / (kg m²)','几何理论 / (kg m²)','相对差异 / %'],'rows':[['圆环',ring,jr,100*(ring-jr)/jr],['单个偏轴圆柱',cylinder,jc,100*(cylinder-jc)/jc]]}}
 offset=np.linspace(0,.15,151)
 return {'metrics':metrics,'tables':tables,'series':{'parallel_axis':{'x':offset.tolist(),'y':(jc0+geom['cylinder_mass_kg']*offset**2).tolist(),'x_label':'理论偏轴距离 / m','y_label':'单柱转动惯量 / (kg m²)'}},'notes':['源原始记录段误插导热参数和热电势表，未用这些无关数据建立转动实验输入。','缺k-t原始计时和悬挂质量，β为已报派生量，实验J仅对已报总惯量作差，未声称独立测得。','只有一个偏轴位置，不能据此定量验证J随d²变化规律。']}
def explore(key,result):
 import plotly.graph_objects as go
 if key!='parallel-axis':raise KeyError(key)
 data=result['series']['parallel_axis'];x=np.array(data['x']);y=np.array(data['y']);default=.1;J=result['metrics']['cylinder_offset_inertia_theory']['value']
 fig=go.Figure([go.Scatter(x=x,y=y,mode='lines',line={'color':'black'}),go.Scatter(x=[default],y=[J],mode='markers',marker={'color':'black','size':11})]);fig.update_layout(template='plotly_white',font={'family':'Times New Roman, SimSun','size':18},width=900,height=580,xaxis_title='理论偏轴距离 / m',yaxis_title='单柱转动惯量 / (kg m²)',margin={'l':100,'r':30,'t':25,'b':150},showlegend=False,sliders=[{'active':100,'currentvalue':{'prefix':'理论偏轴距离 / m：'},'steps':[{'label':f'{d:.3f}','method':'restyle','args':[{'x':[[float(d)]],'y':[[float(j)]]},[1]]} for d,j in zip(x,y)]}]);fig.update_xaxes(showline=True,linecolor='black',gridcolor='#e3e3e3');fig.update_yaxes(showline=True,linecolor='black',gridcolor='#e3e3e3');return fig
