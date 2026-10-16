from pathlib import Path
import csv,json,math

def project(v):
    a,b,c,d=v;return [(a-b+c-d)/4,(a+b+c+d)/4,(a+b-c-d)/4,(a-b-c+d)/4]
def fit(x,y):
    xm=sum(x)/len(x);ym=sum(y)/len(y);a=sum((v-xm)*(w-ym) for v,w in zip(x,y))/sum((v-xm)**2 for v in x);b=ym-a*xm;res=[w-a*v-b for v,w in zip(x,y)];r2=1-sum(v*v for v in res)/sum((v-ym)**2 for v in y);return a,b,r2

def analyze(experiment_dir):
    p=Path(experiment_dir);cfg=json.loads((p/'experiment.json').read_text(encoding='utf-8'));metrics,tables,series={},{},{}
    values={}
    for key,xlabel in [('working_current',r'工作电流 $I_S\,/\,\mathrm{mA}$'),('magnet_current',r'励磁电流 $I_M\,/\,\mathrm{mA}$'),('position',r'位置 $X\,/\,\mathrm{mm}$')]:
        with (p/f'data/{key}.csv').open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
        x=[float(r['x']) for r in rows];raw=[[float(r['V'+str(i)+'_mV']) for i in range(1,5)] for r in rows];parts=[project(v) for v in raw];y=[v[0] for v in parts];values[key]=y
        tables[key+'_observations']={'headers':['自变量']+[f'$V_{j}/\\mathrm{{mV}}$' for j in range(1,5)]+['源表霍尔列 / mV'],'rows':[[x[j]]+raw[j]+[cfg['source_hall_columns'][key][j]] for j in range(len(x))]}
        tables[key+'_decomposition']={'headers':['自变量','$V_H/\\mathrm{mV}$','共模 / mV','电流奇磁场偶 / mV','磁场奇电流偶 / mV'],'rows':[[x[j]]+[round(v,6) for v in parts[j]] for j in range(len(x))]}
        series[key]={'x':x,'y':y,'x_label':xlabel,'y_label':r'霍尔投影 $V_H\,/\,\mathrm{mV}$','label':'四极性投影','fit':key!='position'}
        metrics[key+'_source_column_max_difference']={'value':max(abs(y[j]-cfg['source_hall_columns'][key][j]) for j in range(len(y))),'unit':'mV','label':key+' 源处理列最大差'}
        if key!='position':
            a,b,r2=fit(x,y)
            for suffix,v,u,label in [('slope',a,'mV/mA','线性拟合斜率'),('intercept',b,'mV','线性拟合截距'),('fit_R2',r2,'1','拟合决定系数')]:metrics[key+'_'+suffix]={'value':v,'unit':u,'label':key+' '+label}
        for j,v in enumerate(raw):
            for n,c in enumerate(v,1):metrics[f'{key}_point{j+1}_channel{n}']={'value':c,'unit':'mV','label':key+f' 点{j+1}通道{n}'}
        # Explicit decomposition stores only ten bounded rows, not fitted replacement observations.
        metrics[key+'_max_current_odd']={'value':max(abs(v[2]) for v in parts),'unit':'mV','label':key+' 最大电流奇分量绝对值'}
    relative=[v/values['position'][0] for v in values['position']]
    series['relative_field']={'x':series['position']['x'],'y':relative,'x_label':r'位置 $X\,/\,\mathrm{mm}$','y_label':r'相对磁场 $B(X)/B(2\,\mathrm{mm})$','label':'固定工作电流和灵敏度条件'}
    ratio=values['working_current'][-1]/values['magnet_current'][-1]
    metrics['same_setting_voltage_ratio']={'value':ratio,'unit':'1','label':'两表同标记设置霍尔投影比值'}
    metrics['field_end_ratio']={'value':relative[-1],'unit':'1','label':'20 mm相对2 mm的场投影比值'}
    metrics['field_inner_spread_percent']={'value':(max(values['position'][:7])-min(values['position'][:7]))/values['position'][0]*100,'unit':'%','label':'2–14 mm记录相对变化范围'}
    tables['fit_summary']={'headers':['系列','斜率 / (mV/mA)','截距 / mV','$r^2$'],'rows':[[{'working_current':'工作电流','magnet_current':'励磁电流'}[k],round(metrics[k+'_slope']['value'],9),round(metrics[k+'_intercept']['value'],6),round(metrics[k+'_fit_R2']['value'],6)] for k in ['working_current','magnet_current']]}
    return {'metrics':metrics,'tables':tables,'series':series,'notes':['两表同Is=3mA、IM=500mA的投影不一致，不能合并为校准。','缺少KH、B与厚度d，未求绝对磁场或载流子浓度。','四极性投影隔离奇B奇I分量，不保证消除具有相同奇偶性的副效应。']}

def explore(key,result):
    if key!='parity':raise KeyError(key)
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    f=make_subplots(rows=1,cols=2,horizontal_spacing=.18);states=[]
    for name in ['working_current','magnet_current','position']:
        for index,row in enumerate(result['tables'][name+'_decomposition']['rows']):
            raw=result['tables'][name+'_observations']['rows'][index][1:5];j=len(states);states.append((name,index))
            f.add_trace(go.Bar(x=['(+B,+I)','(−B,+I)','(−B,−I)','(+B,−I)'],y=raw,marker={'color':'white','line':{'color':'black','width':1.5}},visible=j==0,showlegend=False),row=1,col=1)
            f.add_trace(go.Bar(x=['霍尔投影','共模','电流奇','磁场奇'],y=row[1:],marker={'color':'white','line':{'color':'black','width':1.5}},visible=j==0,showlegend=False),row=1,col=2)
    steps=[]
    for j,(name,index) in enumerate(states):mask=[False]*60;mask[2*j:2*j+2]=[True,True];steps.append({'method':'update','args':[{'visible':mask}],'label':f'{name} #{index+1}'})
    f.update_layout(width=1000,height=550,paper_bgcolor='white',plot_bgcolor='white',font={'family':'Times New Roman, SimSun','size':17},sliders=[{'steps':steps,'active':0,'currentvalue':{'prefix':'原始记录：'},'pad':{'t':60}}],margin={'l':85,'r':40,'t':30,'b':170});f.update_yaxes(title_text='电压 / mV',showline=True,linecolor='black',gridcolor='#eeeeee');f.update_xaxes(showline=True,linecolor='black')
    return f
