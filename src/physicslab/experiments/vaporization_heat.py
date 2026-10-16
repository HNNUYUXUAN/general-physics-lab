"""Steam mixing calorimetry with explicit weighing-composition ambiguity."""
from pathlib import Path
import json,csv
import numpy as np

def analyze(experiment_dir):
 root=Path(experiment_dir);cfg=json.loads((root/'experiment.json').read_text(encoding='utf-8'));p=cfg['parameters']
 with (root/'data/observations.csv').open(encoding='utf-8') as f:rows=list(csv.DictReader(f))
 v={row['quantity']:float(row['value']) for row in rows};m1=v['inner_mass'];m2=v['stirrer_mass'];mi=v['initial_total_mass'];mf=v['final_total_mass'];water=mi-m1;steam=mf-mi
 if water<=0 or steam<=m2:raise ValueError('Invalid calorimetry masses.')
 t1=v['initial_voltage']-p['kelvin_offset'];t2=v['final_voltage']-p['kelvin_offset'];t3=p['steam_temperature_c'];cw=p['water_specific_heat_j_gk'];c1=p['inner_specific_heat_j_gk'];c2=p['stirrer_specific_heat_j_gk']
 C=water*cw+m1*c1+m2*c2;Q=C*(t2-t1);sensible=steam*cw*(t3-t2);latent=Q-sensible;L=latent/steam*1000;ref=p['reference_latent_heat_j_kg'];alternative_steam=steam-m2;alternative_L=(Q/alternative_steam-cw*(t3-t2))*1000;derivative=(C/steam+cw)*1000
 vals=[('water_mass',water,'g','冷水质量'),('steam_mass',steam,'g','默认同构成称量的凝结质量'),('initial_temperature',t1,'degC','初温'),('final_temperature',t2,'degC','末温'),('temperature_rise',t2-t1,'K','冷水温升'),('steam_temperature_drop',t3-t2,'K','凝结水温降'),('system_heat_capacity',C,'J/K','系统热容'),('absorbed_heat',Q,'J','系统吸热'),('sensible_heat',sensible,'J','凝结水显热'),('latent_heat_total',latent,'J','凝结潜热总量'),('latent_heat',L,'J/kg','默认构成条件比汽化热'),('relative_deviation',100*abs(L-ref)/ref,'%','相对参考值差异'),('alternative_steam_mass',alternative_steam,'g','末态额外计搅拌器时凝结质量'),('alternative_latent_heat',alternative_L,'J/kg','末态额外计搅拌器时比汽化热'),('final_temperature_sensitivity',derivative,'J/(kg K)','末温灵敏系数')]
 metrics={k:{'value':float(val),'unit':unit,'label':label} for k,val,unit,label in vals}
 labels={'inner_mass':'量热器内筒质量','stirrer_mass':'搅拌器质量','initial_total_mass':'初态筒与水质量','final_total_mass':'末态总质量','initial_voltage':'初温电压','final_voltage':'末温电压','steam_voltage':'蒸汽理论温度电压'}
 symbols={'inner_mass':'$m_1$','stirrer_mass':'$m_2$','initial_total_mass':'$m_{\\mathrm{i}}$','final_total_mass':'$m_{\\mathrm{f}}$','initial_voltage':'$U_1$','final_voltage':'$U_2$','steam_voltage':'$U_3$'}
 tables={'observations':{'headers':['物理量','符号','数值','单位','备注'],'rows':[[labels[row['quantity']],symbols[row['quantity']],float(row['value']),row['unit'],row['note'] or '—'] for row in rows]},'energy':{'headers':['能量项','数值 / J'],'rows':[['系统吸热',Q],['凝结水显热',sensible],['凝结潜热',latent]]},'composition':{'headers':['称量构成假设','凝结质量 / g','比汽化热 / (J kg⁻¹)'],'rows':[['初末均不含搅拌器（沿用源公式）',steam,L],['仅末态额外计入搅拌器',alternative_steam,alternative_L]]}}
 shifts=np.linspace(-2,2,101)
 return {'metrics':metrics,'tables':tables,'series':{'temperature_sensitivity':{'x':shifts.tolist(),'y':(L+derivative*shifts).tolist(),'x_label':'假设末温偏移 / K','y_label':'比汽化热 / (J kg⁻¹)'}},'notes':['初态备注未计搅拌器；末态构成未明确，主结果条件采用相同称量构成，另列末态额外包含搅拌器情形。','U3=373.2mV是理论圆整电压，蒸汽温度按明确的100℃而非反算100.05℃。','无仪器误差限、气压和热交换记录，不提供完整合成不确定度。']}

def explore(key,result):
 import plotly.graph_objects as go
 if key!='temperature-shift':raise KeyError(key)
 L=result['metrics']['latent_heat']['value'];d=result['metrics']['final_temperature_sensitivity']['value'];x=np.linspace(-2,2,101);y=L+d*x
 fig=go.Figure([go.Scatter(x=x,y=y,mode='lines',line={'color':'black'},name='混合热平衡模型'),go.Scatter(x=[0],y=[L],mode='markers',marker={'color':'black','size':11},name='选定末温偏移')]);fig.update_layout(template='plotly_white',font={'family':'Times New Roman, SimSun','size':18},width=900,height=580,xaxis_title='假设末温偏移 / K',yaxis_title='比汽化热 / (J kg⁻¹)',margin={'l':100,'r':30,'t':25,'b':150},showlegend=False,sliders=[{'active':50,'currentvalue':{'prefix':'假设末温偏移 / K：'},'steps':[{'label':f'{shift:.2f}','method':'restyle','args':[{'x':[[float(shift)]],'y':[[float(val)]]},[1]]} for shift,val in zip(x,y)]}]);fig.update_xaxes(showline=True,linecolor='black',gridcolor='#e3e3e3');fig.update_yaxes(showline=True,linecolor='black',gridcolor='#e3e3e3')
 return fig
