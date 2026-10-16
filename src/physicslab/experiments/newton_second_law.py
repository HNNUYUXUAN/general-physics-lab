"""Constant-total-mass force–acceleration experiment."""
from pathlib import Path
import json
import numpy as np

def fit_line(x,y):
    x=np.asarray(x,dtype=float);y=np.asarray(y,dtype=float)
    xc=x-x.mean(); slope=float(np.dot(xc,y-y.mean())/np.dot(xc,xc)); intercept=float(y.mean()-slope*x.mean())
    residual=y-(slope*x+intercept); sse=float(residual@residual)
    r=float(np.corrcoef(x,y)[0,1]); sy=np.sqrt(sse/(len(x)-2)); u_slope=float(sy/np.sqrt(xc@xc)); u_intercept=float(sy*np.sqrt(1/len(x)+x.mean()**2/(xc@xc)))
    return slope,intercept,r,sse,u_slope,u_intercept,residual

def analyze(experiment_dir):
    root=Path(experiment_dir); cfg=json.loads((root/'experiment.json').read_text(encoding='utf-8'))
    a=np.genfromtxt(root/'data/observations.csv',delimiter=',',names=True,dtype=None,encoding='utf-8')
    s=cfg['parameters']['gate_spacing_m'];g=cfg['parameters']['gravity_m_s2']
    masses=[];averages=[];uas=[];processed=[];raw=[]
    for group in range(1,6):
        block=a[a['group']==group]
        if len(block)!=5:raise ValueError('Each force group must contain five trials.')
        vals=[]
        for row in block:
            if row['mode']=='direct': acc=float(row['reported_acceleration_cm_s2'])
            else: acc=(float(row['v2_cm_s'])**2-float(row['v1_cm_s'])**2)/(200*s)
            if not np.isfinite(acc) or acc<=0:raise ValueError('Acceleration must be finite and positive.')
            vals.append(acc)
            raw.append([group,float(row['hanging_mass_g']),int(row['trial']),float(row['reported_acceleration_cm_s2']) if row['mode']=='direct' else float(row['v1_cm_s']),'—' if row['mode']=='direct' else float(row['v2_cm_s']),float(row['reported_acceleration_cm_s2'])])
            processed.append([group,int(row['trial']),acc,acc-float(row['reported_acceleration_cm_s2'])])
        masses.append(float(block['hanging_mass_g'][0]));averages.append(float(np.mean(vals)));uas.append(float(np.std(vals,ddof=1)/np.sqrt(5)))
    k,c,r,sse,uk,uc,residual=fit_line(averages,masses)
    metrics={}
    def add(key,val,unit,label,u=None):
        metrics[key]={'value':float(val),'unit':unit,'label':label}
        if u is not None:metrics[key]['uncertainty']=float(u)
    for i,(av,ua) in enumerate(zip(averages,uas),1):add(f'acceleration_{i}',av,'cm/s^2',f'第{i}组平均加速度',ua)
    add('slope',k,'g/(cm/s^2)','质量—加速度拟合斜率',uk)
    add('intercept',c,'g','拟合截距',uc)
    add('correlation',r,'1','相关系数');add('r_squared',r*r,'1','决定系数')
    add('inferred_system_mass',k*g*100,'g','斜率推算系统质量',uk*g*100)
    add('equivalent_resistance',c*g/1000,'N','截距等效阻力',uc*g/1000)
    add('sse',sse,'g^2','拟合残差平方和')
    k2,c2,r2,*_=fit_line(averages[1:],masses[1:])
    add('slope_without_group1',k2,'g/(cm/s^2)','去掉第一组后的斜率')
    add('intercept_without_group1',c2,'g','去掉第一组后的截距')
    add('correlation_without_group1',r2,'1','去掉第一组后的相关系数')
    tables={'observations':{'headers':['组别','$m_0 / \\mathrm{g}$','次数','数据1（速度或加速度）','数据2速度 / (cm s⁻¹)','记录加速度 / (cm s⁻²)'],'rows':raw},
      'recalculation':{'headers':['组别','次数','采用加速度 / (cm s⁻²)','相对记录列差值 / (cm s⁻²)'],'rows':processed},
      'summary':{'headers':['组别','$m_0 / \\mathrm{g}$','$F / \\mathrm{N}$','$\\bar a / (\\mathrm{cm\\,s^{-2}})$','$u_A(\\bar a) / (\\mathrm{cm\\,s^{-2}})$','质量拟合残差 / g'],'rows':[[i+1,m,m*g/1000,av,ua,float(res)] for i,(m,av,ua,res) in enumerate(zip(masses,averages,uas,residual))]}}
    series={'force_acceleration':{'x':averages,'y':masses,'x_label':'平均加速度 / (cm s⁻²)','y_label':'悬挂质量 / g','fit':True},'force_residual':{'x':averages,'y':residual.tolist(),'x_label':'平均加速度 / (cm s⁻²)','y_label':'质量拟合残差 / g'}}
    return {'metrics':metrics,'tables':tables,'series':series,'notes':['F1为直接加速度；F2-F5由原始速度及0.500m间距重算。','回归为等权普通最小二乘；斜率与截距不确定度只表示回归残差估计。','没有系统独立称量值及仪器精度，不能声称完成完整不确定度评估或严格比例验证。']}

def explore(key,result):
    import plotly.graph_objects as go
    if key!='fit-selection':raise KeyError(key)
    data=result['series']['force_acceleration'];x=np.array(data['x']);y=np.array(data['y']);domain=np.linspace(min(x)-5,max(x)+5,101)
    selections=[np.arange(5)]+[np.delete(np.arange(5),i) for i in range(5)]
    labels=['全部五组']+[f'省略第{i}组' for i in range(1,6)]
    lines=[]
    for selection in selections:
        k,c,*_=fit_line(x[selection],y[selection]);lines.append(k*domain+c)
    fig=go.Figure([go.Scatter(x=x,y=y,mode='markers',marker={'color':'black','size':10,'symbol':'circle-open'},name='五组观测'),go.Scatter(x=domain,y=lines[0],mode='lines',line={'color':'black'},name='拟合')])
    fig.update_layout(template='plotly_white',font={'family':'Times New Roman, SimSun','size':18},width=900,height=580,xaxis_title=data['x_label'],yaxis_title=data['y_label'],margin={'l':80,'r':30,'t':80,'b':130},showlegend=False,updatemenus=[{'buttons':[{'label':label,'method':'restyle','args':[{'y':[line.tolist()]},[1]]} for label,line in zip(labels,lines)],'direction':'down','x':.5,'y':1.15,'xanchor':'center','yanchor':'top'}])
    fig.update_xaxes(showline=True,linecolor='black',gridcolor='#e3e3e3');fig.update_yaxes(showline=True,linecolor='black',gridcolor='#e3e3e3')
    return fig
