from pathlib import Path
import csv,json,math

def theory(x_mm,current_A,coils,R=.105,N=500,d=.105):
    x=x_mm/1000;centers=[-d/2] if coils=='single' else [-d/2,d/2]
    return sum(4*math.pi*1e-7*N*current_A*R*R/(2*(R*R+(x-c)**2)**1.5) for c in centers)*1000

def analyze(experiment_dir):
    p=Path(experiment_dir);cfg=json.loads((p/'experiment.json').read_text(encoding='utf-8'));metrics,tables,series={},{},{}
    with (p/'data/readings.csv').open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
    original=[];comparison=[];groups={}
    for coils in ['single','double']:
        for current in [300,500]:
            key=f'{coils}_{current}';items=[r for r in rows if r['coils']==coils and int(r['current_mA'])==current];x=[float(r['position_mm']) for r in items];y=[float(r['reading']) for r in items];th=[theory(z,current/1000,coils,cfg['radius_m'],cfg['turns'],cfg['spacing_m']) for z in x];groups[key]=y
            original.append(["单线圈" if coils=="single" else "双线圈",current]+y);comparison.extend([["单线圈" if coils=="single" else "双线圈",current,x[j],y[j],cfg['source_theory'][key][j],round(th[j],6)] for j in range(len(x))])
            series[key]={'x':x,'y':y,'x_label':r'轴向位置 $x\,/\,\mathrm{mm}$','y_label':'磁场读数 / 原记录单位','label':f'{"单线圈" if coils=="single" else "双线圈"} / {current} mA'}
            series[key+'_theory']={'x':x,'y':th,'x_label':r'轴向位置 $x\,/\,\mathrm{mm}$','y_label':r'理论磁场 $B\,/\,\mathrm{mT}$','label':f'理想{"单线圈" if coils=="single" else "双线圈"} / {current} mA','model':True}
            series[key+'_normalized']={'x':x,'y':[v/y[3] for v in y],'x_label':r'轴向位置 $x\,/\,\mathrm{mm}$','y_label':r'$B(x)/B(-52\,\mathrm{mm})$','label':'同一读数标度归一化'}
            metrics[key+'_peak_position']={'value':x[max(range(len(y)),key=y.__getitem__)],'unit':'mm','label':key+' 记录峰值位置'}
            metrics[key+'_theory_at_minus52']={'value':th[3],'unit':'mT','label':key+' −52mm理论场'}
        ratios=[b/a for a,b in zip(groups[f'{coils}_300'],groups[f'{coils}_500'])]
        maxdev=max(abs(r/(5/3)-1)*100 for r in ratios)
        metrics[coils+'_current_ratio_max_deviation']={'value':maxdev,'unit':'%','label':coils+' 500/300mA响应比例相对偏差最大值'}
    tables['observations']={'headers':['线圈','电流 / mA']+[str(x) for x in [-82,-72,-62,-52,-42,-32,-22]],'rows':original}
    tables['comparison']={'headers':['线圈','电流 / mA','位置 / mm','记录值（单位未注明）','源理论列（单位未注明）','重算理论 / mT'],'rows':comparison}
    modelx=[-2+j/100 for j in range(401)]
    for d in [.5,1,1.5]:
        name=str(d).replace('.','p');f=lambda z:(1+(z-d/2)**2)**-1.5+(1+(z+d/2)**2)**-1.5
        series['spacing_'+name]={'x':modelx,'y':[f(z)/f(0) for z in modelx],'x_label':r'归一化轴向位置 $x/R$','y_label':r'$B(x)/B(0)$','label':f'模型 d/R={d}','model':True}
        metrics['spacing_'+name+'_curvature']={'value':3*(d*d-1)/(1+d*d/4)**2,'unit':'1','label':f'间距比{d}的中心归一化二阶导数'}
    return {'metrics':metrics,'tables':tables,'series':series,'notes':['磁场读数单位缺失，理论以mT独立列示，不直接认定绝对误差。','双线圈记录峰值位置与报告坐标约定的理论形状不符。','μ0=4π×10^-7 H/m采用本实验经典近似值，未作为现代SI精确定义值。']}

def explore(key,result):
    if key!='spacing':raise KeyError(key)
    import plotly.graph_objects as go
    f=go.Figure()
    for j,d in enumerate([.5,1,1.5]):
        s=result['series']['spacing_'+str(d).replace('.','p')];f.add_trace(go.Scatter(x=s['x'],y=s['y'],mode='lines',line={'color':'black'},visible=j==1,showlegend=False))
    f.update_layout(width=1000,height=520,paper_bgcolor='white',plot_bgcolor='white',font={'family':'Times New Roman, SimSun','size':18},sliders=[{'active':1,'steps':[{'method':'update','args':[{'visible':[i==j for i in range(3)]}],'label':str(d)} for j,d in enumerate([.5,1,1.5])],'currentvalue':{'prefix':'模型线圈间距比 d/R = '},'pad':{'t':50}}],margin={'l':100,'r':40,'t':30,'b':140});f.update_xaxes(title_text='轴向位置 x / R',showline=True,linecolor='black',gridcolor='#eeeeee');f.update_yaxes(title_text='归一化磁场 B(x) / B(0)',showline=True,linecolor='black',gridcolor='#eeeeee')
    return f
