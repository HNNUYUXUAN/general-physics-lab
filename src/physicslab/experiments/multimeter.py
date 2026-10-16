"""Nominal-value comparisons and explicitly conditional analog-meter estimates."""
from pathlib import Path
import csv,json,math

def analyze(experiment_dir):
    p=Path(experiment_dir);cfg=json.loads((p/'experiment.json').read_text(encoding='utf-8'))
    metrics,tables,series={},{},{}
    for kind,unit in [('voltage','V'),('resistance','Ω')]:
        with (p/f'data/{kind}.csv').open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
        original=[];derived=[]
        for j,row in enumerate(rows,1):
            n,d,a=map(float,[row['nominal'],row['digital'],row['analog']]);bound=cfg['one_division_bounds'][kind][j-1]
            de=abs(d-n)/n*100;ae=abs(a-n)/n*100;ub=bound/math.sqrt(3)
            original.append([row['label'],n,row['digital_range'],d,row['analog_range'],a])
            values=[row['label'],round(de,3),round(ae,3),bound,round(ub,6)]
            for suffix,v,u,label in [('digital_deviation',de,'%','数字表与标称偏差'),('analog_deviation',ae,'%','指针表与标称偏差'),('analog_one_division_uB',ub,unit,'假定±一分度的标准不确定度')]:
                metrics[f'{kind}_{j}_{suffix}']={'value':v,'unit':u,'label':row['label']+' '+label}
            if kind=='voltage':
                fs=float(row['analog_range']);limit=.03*fs;values+=[limit]
                metrics[f'voltage_{j}_conditional_limit']={'value':limit,'unit':'V','label':row['label']+' 假定3%FS示值限差'}
            derived.append(values)
        tables[kind+'_observations']={'headers':['待测量',f'标称值 / {unit}','数字表量程',f'数字表读数 / {unit}','指针表量程',f'指针表读数 / {unit}'],'rows':original}
        tables[kind+'_analysis']={'headers':['待测量','数字表标称偏差 / %','指针表标称偏差 / %',f'一分度假定界限 / {unit}',f'条件标准不确定度 / {unit}']+(['假定 $3\\%\\mathrm{FS}$ 界限 / V'] if kind=='voltage' else []),'rows':derived}
        for name,col in [('digital',1),('analog',2)]:
            series[kind+'_'+name+'_deviation']={'x':list(range(1,len(rows)+1)),'y':[v[col] for v in derived],'x_label':'待测量编号','y_label':'相对标称偏差绝对值 / %','label':('数字式' if name=='digital' else '指针式')+'万用表'}
    xs=[j/100 for j in range(2001)]
    series['ohm_scale']={'x':xs,'y':[1/(1+x) for x in xs],'x_label':r'归一化电阻 $R_x/R_{\mathrm{int}}$','y_label':r'归一化偏转 $I/I_0$','label':'理想串联式欧姆表刻度','model':True}
    metrics['ohm_scale_midpoint']={'value':.5,'unit':'1','label':'等内阻时的归一化指针偏转'}
    return {'metrics':metrics,'tables':tables,'series':series,'notes':['标称偏差不是以校准标准为依据的测量误差。','一分度和3%FS估计沿用报告假定，不代表仪表检定规格。','未测量电流；本次无充分重复性样本。']}

def explore(key,result):
    if key!='ohm-scale':raise KeyError(key)
    import plotly.graph_objects as go
    xs=result['series']['ohm_scale']['x'];ys=result['series']['ohm_scale']['y']
    f=go.Figure(go.Scatter(x=xs,y=ys,mode='lines',line={'color':'black'},showlegend=False))
    ratios=[.1,.5,1,2,5,10,20]
    for j,x in enumerate(ratios):f.add_trace(go.Scatter(x=[x],y=[1/(1+x)],mode='markers',marker={'color':'black','size':11},visible=j==2,showlegend=False))
    steps=[]
    for j,x in enumerate(ratios):steps.append({'method':'update','args':[{'visible':[True]+[i==j for i in range(len(ratios))]}],'label':str(x)})
    f.update_layout(width=1000,height=520,paper_bgcolor='white',plot_bgcolor='white',font={'family':'Times New Roman, SimSun','size':18},sliders=[{'active':2,'steps':steps,'currentvalue':{'prefix':'模型电阻比 Rx/Rint = '},'pad':{'t':50}}],margin={'l':100,'r':40,'t':30,'b':140})
    f.update_xaxes(title_text='归一化电阻 Rx / Rint',showline=True,linecolor='black',gridcolor='#eeeeee');f.update_yaxes(title_text='归一化指针偏转 I / I0',range=[0,1.05],showline=True,linecolor='black',gridcolor='#eeeeee')
    return f
