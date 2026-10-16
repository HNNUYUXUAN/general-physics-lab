"""Standing-wave geometry and log-log power laws, recomputed from L and n."""
from pathlib import Path
import json
import numpy as np
def fit_power(x,y):
 xc=x-x.mean();yc=y-y.mean();k=float(xc@yc/(xc@xc));b=float(y.mean()-k*x.mean());r=float(xc@yc/np.sqrt((xc@xc)*(yc@yc)));res=y-k*x-b;u=float(np.sqrt((res@res)/(len(x)-2)/(xc@xc)));return k,b,r,u
def analyze(experiment_dir):
 root=Path(experiment_dir);cfg=json.loads((root/'experiment.json').read_text(encoding='utf-8'));p=cfg['parameters'];a=np.genfromtxt(root/'data/tension.csv',delimiter=',',names=True);b=np.genfromtxt(root/'data/frequency.csv',delimiter=',',names=True)
 if len(a)!=7 or len(b)!=7 or np.any(a['half_waves']<=0) or np.any(b['half_waves']<=0):raise ValueError('Invalid standing-wave observations.')
 la=2*a['length_cm']/a['half_waves'];lb=2*b['length_cm']/b['half_waves'];F=a['mass_g']*p['gravity_m_s2']/1000;xf=np.log10(F);yf=np.log10(la);xn=np.log10(b['frequency_hz']);yn=np.log10(lb);k1,b1,r1,u1=fit_power(xf,yf);k2,b2,r2,u2=fit_power(xn,yn)
 vals=[('tension_exponent',k1,'1','张力幂指数'),('tension_intercept',b1,'1','张力双对数截距'),('tension_correlation',r1,'1','张力双对数相关系数'),('tension_slope_uncertainty',u1,'1','张力指数回归标准误差'),('tension_exponent_deviation',100*abs(k1-.5)/.5,'%','张力指数相对理论差异'),('frequency_exponent',k2,'1','频率幂指数'),('frequency_intercept',b2,'1','频率双对数截距'),('frequency_correlation',r2,'1','频率双对数相关系数'),('frequency_slope_uncertainty',u2,'1','频率指数回归标准误差'),('frequency_exponent_deviation',100*abs(k2+1),'%','频率指数相对理论差异'),('last_tension_wavelength',la[-1],'cm','最后张力点由弦长与半波数复算波长'),('baseline_wave_speed',la[0]/100*p['fixed_frequency_hz'],'m/s','第一驻波记录推算传播速度')]
 metrics={key:{'value':float(val),'unit':unit,'label':label} for key,val,unit,label in vals};metrics['tension_exponent']['uncertainty']=u1;metrics['frequency_exponent']['uncertainty']=u2
 headers=['物理量','1','2','3','4','5','6','7']
 tables={'tension':{'headers':headers,'rows':[['质量 / g',*a['mass_g'].tolist()],['弦长 / cm',*a['length_cm'].tolist()],['半波数',*a['half_waves'].astype(int).tolist()],['复算波长 / cm',*la.tolist()],['张力 / N',*F.tolist()],['波长常用对数',*yf.tolist()],['张力常用对数',*xf.tolist()]]},'frequency':{'headers':headers,'rows':[['频率 / Hz',*b['frequency_hz'].tolist()],['弦长 / cm',*b['length_cm'].tolist()],['半波数',*b['half_waves'].astype(int).tolist()],['复算波长 / cm',*lb.tolist()],['波长常用对数',*yn.tolist()],['频率常用对数',*xn.tolist()]]},'fit_results':{'headers':['关系','斜率','标准误差','相关系数','相对理论差异 / %'],'rows':[['波长—张力',k1,u1,r1,100*abs(k1-.5)/.5],['波长—频率',k2,u2,r2,100*abs(k2+1)]]}}
 return {'metrics':metrics,'tables':tables,'series':{'tension_log':{'x':xf.tolist(),'y':yf.tolist(),'x_label':'张力常用对数（N）','y_label':'波长常用对数（cm）','fit':True},'frequency_log':{'x':xn.tolist(),'y':yn.tolist(),'x_label':'频率常用对数（Hz）','y_label':'波长常用对数（cm）','fit':True}},'notes':['张力表最后L63.30cm,n1应得126.60cm，源派生166.60cm不采用。','对数均按物理量相对1N、1Hz、1cm的无量纲数值计算。','未给弦线密度、张力和长度仪器误差，指数标准误差仅为回归条件量。']}
def explore(key,result):
 import plotly.graph_objects as go
 if key!='standing-mode':raise KeyError(key)
 L=result['tables']['tension']['rows'][1][1]/100;v=result['metrics']['baseline_wave_speed']['value'];x=np.linspace(0,L,401);waves=[np.sin(n*np.pi*x/L) for n in range(1,5)]
 fig=go.Figure(go.Scatter(x=x,y=waves[1],mode='lines',line={'color':'black'}));fig.update_layout(template='plotly_white',font={'family':'Times New Roman, SimSun','size':18},width=900,height=580,xaxis_title='弦上位置 / m',yaxis_title=r'$\text{归一化位移}\;y/A$',margin={'l':90,'r':30,'t':80,'b':130},updatemenus=[{'active':1,'buttons':[{'label':f'n={n}，f={n*v/(2*L):.1f} Hz','method':'restyle','args':[{'y':[wave.tolist()]}]} for n,wave in enumerate(waves,1)],'x':.5,'y':1.15,'xanchor':'center','yanchor':'top'}]);fig.update_xaxes(showline=True,linecolor='black',gridcolor='#e3e3e3');fig.update_yaxes(showline=True,linecolor='black',gridcolor='#e3e3e3',range=[-1.1,1.1]);return fig
