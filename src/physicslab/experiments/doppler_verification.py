"""Moving-receiver Doppler shift and acoustic speed estimation."""
from pathlib import Path
import json
import numpy as np

def analyze(experiment_dir):
    root=Path(experiment_dir);cfg=json.loads((root/'experiment.json').read_text(encoding='utf-8'))
    data=np.genfromtxt(root/'data/observations.csv',delimiter=',',names=True)
    x=data['velocity_m_s'];y=data['frequency_hz'];p=cfg['parameters'];f0=p['source_frequency_hz'];temp=p['temperature_c']
    if len(x)!=5 or not np.isfinite(x).all() or not np.isfinite(y).all():raise ValueError('Expected five finite Doppler records.')
    xc=x-x.mean();yc=y-y.mean();k=float(xc@yc/(xc@xc));b=float(y.mean()-k*x.mean());res=y-k*x-b
    r=float(xc@yc/np.sqrt((xc@xc)*(yc@yc)));sy=np.sqrt(res@res/(len(x)-2));uk=float(sy/np.sqrt(xc@xc));ub=float(sy*np.sqrt(1/len(x)+x.mean()**2/(xc@xc)))
    u=f0/k;theory=331.45*np.sqrt(1+temp/273.15); uu=f0*uk/k**2
    vals=[('slope',k,'Hz/(m/s)','频率速度拟合斜率',uk),('intercept',b,'Hz','拟合截距',ub),('correlation',r,'1','相关系数',None),('sound_speed',u,'m/s','实验声速',uu),('theoretical_speed',theory,'m/s','温度模型声速',None),('relative_deviation',100*abs(u-theory)/theory,'%','声速相对差异',None),('intercept_offset',b-f0,'Hz','截距与声源频率差',None)]
    metrics={key:dict(value=float(value),unit=unit,label=label,**({'uncertainty':float(unc)} if unc is not None else {})) for key,value,unit,label,unc in vals}
    tables={'observations':{'headers':['序号','$v / (\\mathrm{m\\,s^{-1}})$','$f / \\mathrm{Hz}$'],'rows':[[i+1,float(v),float(f)] for i,(v,f) in enumerate(zip(x,y))]},'processed':{'headers':['序号','模型预测频率 / Hz','拟合残差 / Hz','温度模型预测频率 / Hz'],'rows':[[i+1,float(k*v+b),float(e),float(f0*(1+v/theory))] for i,(v,e) in enumerate(zip(x,res))]}}
    return {'metrics':metrics,'tables':tables,'series':{'doppler_fit':{'x':x.tolist(),'y':y.tolist(),'x_label':'接收器速度 / (m s⁻¹)','y_label':'接收频率 / Hz','fit':True}},'notes':['声源固定，接收器向声源运动为正。','声速不确定度只传播回归斜率标准误差，未计声源频率、测速和温度仪器误差。']}

def explore(key,result):
    import plotly.graph_objects as go
    if key!='receiver-speed':raise KeyError(key)
    u=result['metrics']['theoretical_speed']['value']; f0=result['metrics']['intercept']['value']-result['metrics']['intercept_offset']['value'];v=np.linspace(-1.5,1.5,101)
    fig=go.Figure([go.Scatter(x=v,y=f0*(1+v/u),line={'color':'black'},mode='lines',name='静止声源模型'),go.Scatter(x=[0],y=[f0],mode='markers',marker={'color':'black','size':11},name='选定速度')])
    fig.update_layout(template='plotly_white',font={'family':'Times New Roman, SimSun','size':18},width=900,height=580,xaxis_title='接收器速度 / (m s⁻¹)',yaxis_title='接收频率 / Hz',margin={'l':90,'r':30,'t':25,'b':150},showlegend=False,sliders=[{'active':50,'currentvalue':{'prefix':'接收器速度 / (m/s)：'},'steps':[{'label':f'{vel:.2f}','method':'restyle','args':[{'x':[[float(vel)]],'y':[[float(f0*(1+vel/u))]]},[1]]} for vel in v]}])
    fig.update_xaxes(showline=True,linecolor='black',gridcolor='#e3e3e3');fig.update_yaxes(showline=True,linecolor='black',gridcolor='#e3e3e3')
    return fig
