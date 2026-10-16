from pathlib import Path
import csv,json,math

def analyze(experiment_dir):
    p=Path(experiment_dir);cfg=json.loads((p/'experiment.json').read_text(encoding='utf-8'))
    with (p/'data/balance.csv').open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
    metrics,tables,series={},{},{};raw=[];derived=[]
    for j,r in enumerate(rows,1):
        nominal,m,comparison=map(float,[r['nominal_Ohm'],r['ratio_M'],r['comparison_Ohm']]);rx=m*comparison;dev=(rx-nominal)/nominal*100
        grade=None if rx<10 else .05 if rx<=10000 else .1 if rx<=100000 else .2
        raw.append([nominal,r['ratio_label'],comparison,cfg['source_Rx'][j-1]])
        derived.append([nominal,m,rx,round(dev,6),'<10 Ω，超单桥有效范围' if grade is None else f'${grade:g}\\%$（参考条件下）'])
        metrics[f'R{j}_measured']={'value':rx,'unit':'Ω','label':f'标称{nominal:g}Ω的平衡结果'}
        metrics[f'R{j}_nominal_deviation']={'value':dev,'unit':'%','label':f'标称{nominal:g}Ω的相对偏差'}
    metrics['source_example_limit_arithmetic']={'value':.0005*(100/10+3.066),'unit':'Ω','label':'源示例参数代入的限差算术值（非已确认适用）'}
    tables['balance']={'headers':['标称 / Ω','比率设定','比较臂 / Ω','源处理结果 / Ω'],'rows':raw}
    tables['results']={'headers':['标称 / Ω','$M$','重算电阻 / Ω','标称偏差 / %','说明书等级条件'],'rows':derived}
    tables['source_limits']={'headers':['标称 / Ω','源报告限差表达（待核适用条件）'],'rows':[[r['nominal_Ohm'],v] for r,v in zip(rows,cfg['source_limits'])]}
    xs=[.8+j/1000 for j in range(401)]
    for m in [.1,1,10,100]:
        # normalized comparative arm R=1 and ratio arms Ra=M,Rb=1.
        ys=[1/(m+1)-1/(m*q+1) for q in xs];series[f'balance_M{str(m).replace(".","p")}']={'x':xs,'y':ys,'x_label':r'电阻相对平衡值 $R_x/(MR)$','y_label':r'开路桥电压 $(V_B-V_D)/E$','label':f'理想比率臂M={m}','model':True}
        metrics[f'model_M{str(m).replace(".","p")}_balance']={'value':1/(m+1)-1/(m+1),'unit':'1','label':f'M={m}平衡桥电压'}
    return {'metrics':metrics,'tables':tables,'series':series,'notes':['3Ω结果低于单电桥说明书有效范围下限10Ω。','20kΩ所在档等级指数为0.1%，不能统一0.05%。','源限差条件不完整，未将限差视为标准不确定度。']}

def explore(key,result):
    if key!='balance':raise KeyError(key)
    import plotly.graph_objects as go
    f=go.Figure();ms=[.1,1,10,100]
    for j,m in enumerate(ms):s=result['series']['balance_M'+str(m).replace('.','p')];f.add_trace(go.Scatter(x=s['x'],y=s['y'],mode='lines',line={'color':'black'},visible=j==1,showlegend=False))
    f.add_hline(y=0,line_color='#888888',line_dash='dash');f.update_layout(width=1000,height=520,paper_bgcolor='white',plot_bgcolor='white',font={'family':'Times New Roman, SimSun','size':18},sliders=[{'active':1,'steps':[{'method':'update','args':[{'visible':[i==j for i in range(4)]}],'label':str(m)} for j,m in enumerate(ms)],'currentvalue':{'prefix':'理想比率臂 M = '},'pad':{'t':50}}],margin={'l':110,'r':40,'t':30,'b':140});f.update_xaxes(title_text='电阻相对平衡值 Rx / (MR)',showline=True,linecolor='black',gridcolor='#eeeeee');f.update_yaxes(title_text='归一化开路桥电压 (VB−VD) / E',showline=True,linecolor='black',gridcolor='#eeeeee')
    return f
