"""Heating-curve analysis; missing heat capacity prevents independent J estimate."""
from pathlib import Path
import json
import numpy as np

def regression(x,y):
 x=np.asarray(x);y=np.asarray(y);xc=x-x.mean();yc=y-y.mean();a=float(xc@yc/(xc@xc));b=float(y.mean()-a*x.mean());r=float(xc@yc/np.sqrt((xc@xc)*(yc@yc)));res=y-a*x-b;sy=np.sqrt(res@res/(len(x)-2));ua=float(sy/np.sqrt(xc@xc));ub=float(sy*np.sqrt(1/len(x)+x.mean()**2/(xc@xc)))
 return a,b,r,ua,ub

def analyze(experiment_dir):
 root=Path(experiment_dir);cfg=json.loads((root/'experiment.json').read_text(encoding='utf-8'));data=np.genfromtxt(root/'data/temperatures.csv',delimiter=',',names=True)
 t=data['time_min']*60;T=data['temperature_k']
 if len(t)!=30 or not np.isfinite(T).all() or not np.all(np.diff(t)>0):raise ValueError('Expected 30 ordered temperatures.')
 a,b,r,ua,ub=regression(t,T);early=regression(t[:15],T[:15])[0];late=regression(t[15:],T[15:])[0];endpoint=(T[-1]-T[0])/(t[-1]-t[0])
 vals=[('heating_slope',a,'K/s','全区间温升拟合斜率',ua),('temperature_intercept',b,'K','拟合初温截距',ub),('correlation',r,'1','相关系数',None),('endpoint_slope',endpoint,'K/s','首尾温升速率',None),('early_slope',early,'K/s','前15点拟合斜率',None),('late_slope',late,'K/s','后15点拟合斜率',None),('total_temperature_rise',T[-1]-T[0],'K','首尾温升',None),('source_slope_difference',100*(a-cfg['source_reported']['slope_k_s'])/cfg['source_reported']['slope_k_s'],'%','相对源仪器斜率差异',None)]
 metrics={key:dict(value=float(val),unit=unit,label=label,**({'uncertainty':float(u)} if u is not None else {})) for key,val,unit,label,u in vals}
 rows=[[i+1,float(data['time_min'][i]),float(T[i]),i+16,float(data['time_min'][i+15]),float(T[i+15])] for i in range(15)]
 return {'metrics':metrics,'tables':{'observations':{'headers':['序号','$t / \\mathrm{min}$','$T / \\mathrm{K}$','序号','$t / \\mathrm{min}$','$T / \\mathrm{K}$'],'rows':rows},'fit_values':{'headers':['时间 / min','温度 / K','拟合温度 / K','残差 / K'],'rows':[[float(tt/60),float(temp),float(a*tt+b),float(temp-a*tt-b)] for tt,temp in zip(t,T)]}},'series':{'heating_curve':{'x':t.tolist(),'y':T.tolist(),'x_label':'加热时间 / s','y_label':'水温 / K','fit':True}},'notes':['J=4.21J/cal为源报告记录结果，缺少实际电压/电流及总热容，无法独立重算。','电压20V、电流.495A仅为操作设定近似值，未视为实际测量。','线性回归不会自动完成散热修正。']}

def explore(key,result):
 import plotly.graph_objects as go
 if key!='fit-window':raise KeyError(key)
 data=result['series']['heating_curve'];x=np.array(data['x']);y=np.array(data['y']);windows=[slice(None),slice(0,15),slice(15,30),slice(5,25)];labels=['全部30点','前15点','后15点','中间20点'];curves=[]
 for win in windows:
  a,b,*_=regression(x[win],y[win]);curves.append(a*x+b)
 fig=go.Figure([go.Scatter(x=x,y=y,mode='markers',marker={'color':'black','size':8,'symbol':'circle-open'},name='记录温度'),go.Scatter(x=x,y=curves[0],mode='lines',line={'color':'black'},name='选定区间拟合')])
 fig.update_layout(template='plotly_white',font={'family':'Times New Roman, SimSun','size':18},width=900,height=580,xaxis_title='加热时间 / s',yaxis_title='水温 / K',margin={'l':85,'r':30,'t':80,'b':130},showlegend=False,updatemenus=[{'buttons':[{'label':label,'method':'restyle','args':[{'y':[curve.tolist()]},[1]]} for label,curve in zip(labels,curves)],'direction':'down','x':.5,'y':1.15,'xanchor':'center','yanchor':'top'}]);fig.update_xaxes(showline=True,linecolor='black',gridcolor='#e3e3e3');fig.update_yaxes(showline=True,linecolor='black',gridcolor='#e3e3e3')
 return fig
