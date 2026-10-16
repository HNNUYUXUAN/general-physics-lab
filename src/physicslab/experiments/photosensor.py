from pathlib import Path
import csv,json,math

def analyze(experiment_dir):
    p=Path(experiment_dir);cfg=json.loads((p/'experiment.json').read_text(encoding='utf-8'))
    with (p/'data/measurements.csv').open(encoding='utf-8',newline='') as f:records=list(csv.DictReader(f))
    metrics,tables,series={},{},{};summary=[];common=[]
    for position in [0,3,6,9]:
        rows=[v for v in records if int(v['position_cm'])==position];rn=[float(v['load_kOhm']) for v in rows];u=[float(v['output_V']) for v in rows];rs=[float(v['sample_mV']) for v in rows];i=[v/cfg['sample_resistance_Ohm'] for v in rs];expected=[cur*(r*1000+cfg['sample_resistance_Ohm'])/1000 for cur,r in zip(i,rn)];difference=[a-b for a,b in zip(u,expected)];relative=[abs(v)/abs(a)*100 for v,a in zip(difference,u)];key=f'L{position}'
        for part,start,stop in [('a',0,7),('b',7,14)]:
            tables[key+'_'+part]={'headers':['物理量']+[str(j+1) for j in range(start,stop)],'rows':[['$R_n/\\mathrm{k}\\Omega$']+rn[start:stop],['$U_o/\\mathrm{V}$']+u[start:stop],['$U_{R1}/\\mathrm{mV}$']+rs[start:stop],['重算负载电流 / mA']+i[start:stop]]}
        tables[key+'_consistency']={'headers':['负载 / kΩ','负载电流 / mA','记录Uo / V','回路预测Uo / V','记录−回路 / V','相对记录差 / %'],'rows':[[rn[j],i[j],u[j],round(expected[j],6),round(difference[j],6),round(relative[j],3)] for j in range(14)]}
        series[key+'_IV']={'x':u,'y':i,'x_label':r'记录端电压 $U_o\,/\,\mathrm{V}$','y_label':r'取样换算电流 $I\,/\,\mathrm{mA}$','label':f'位置L={position}cm（回路一致性待核）'}
        series[key+'_circuit_difference']={'x':rn,'y':difference,'x_label':r'标记负载 $R_n\,/\,\mathrm{k}\Omega$','y_label':r'$U_o-I(R_n+R_1)\,/\,\mathrm{V}$','label':f'位置L={position}cm'}
        values={'maximum_recorded_current':(max(i),'mA','最大记录负载电流（非短路）'),'minimum_recorded_voltage':(min(u),'V','最小记录端电压'),'maximum_recorded_voltage':(max(u),'V','最大记录端电压（非开路）'),'max_circuit_relative_difference':(max(relative),'%','回路相对差最大值'),'mean_circuit_relative_difference':(sum(relative)/14,'%','回路相对差均值')}
        for k,(v,unit,label) in values.items():metrics[key+'_'+k]={'value':v,'unit':unit,'label':f'L={position}cm '+label}
        summary.append([position,min(rn),max(rn),max(i),min(u),max(u),round(max(relative),3)])
        point=rn.index(1);common.append([position,i[point],u[point]])
    tables['summary']={'headers':['灯杆位置 / cm','最小负载 / kΩ','最大负载 / kΩ','最大负载电流 / mA','最小端电压 / V','最大端电压 / V','最大回路相对差 / %'],'rows':summary}
    tables['common_load']={'headers':['灯杆位置 / cm','1 kΩ负载电流 / mA','1 kΩ端电压 / V'],'rows':common}
    series['current_distance_common_load']={'x':[v[0] for v in common],'y':[v[1] for v in common],'x_label':r'灯杆刻度 $L\,/\,\mathrm{cm}$','y_label':r'$1\,\mathrm{k}\Omega$ 负载电流 / mA','label':'同标记负载比较'}
    xs=[j/400 for j in range(401)]
    for a in [5,10,15]:
        ys=[1-math.expm1(a*v)/math.expm1(a) for v in xs];series[f'ideal_a{a}']={'x':xs,'y':ys,'x_label':r'归一化电压 $V/V_{oc}$','y_label':r'归一化电流 $I/I_{ph}$','label':f'理想单二极管模型a={a}','model':True}
        metrics[f'model_a{a}_midpoint']={'value':1-math.expm1(a*.5)/math.expm1(a),'unit':'1','label':f'理想模型a={a}半开路电压处电流'}
    return {'metrics':metrics,'tables':tables,'series':series,'notes':['取样换算的是负载电流，不把它直接记为光生源电流。','未测短路和开路，未给Isc/Voc或最大功率点。','回路关系不一致，不能将这些曲线作为已核实器件IV特性。','灯杆刻度不等于照度，未作照度校准或反平方拟合。']}

def explore(key,result):
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    if key=='records':
        f=make_subplots(rows=1,cols=2,horizontal_spacing=.18);positions=[0,3,6,9]
        for j,pos in enumerate(positions):
            for col,s in [(1,result['series'][f'L{pos}_IV']),(2,result['series'][f'L{pos}_circuit_difference'])]:f.add_trace(go.Scatter(x=s['x'],y=s['y'],mode='lines+markers',line={'color':'black'},marker={'symbol':'circle-open','color':'black'},visible=j==0,showlegend=False),row=1,col=col)
        steps=[]
        for j,pos in enumerate(positions):mask=[False]*8;mask[2*j:2*j+2]=[True,True];steps.append({'method':'update','args':[{'visible':mask}],'label':str(pos)})
        f.update_layout(sliders=[{'active':0,'steps':steps,'currentvalue':{'prefix':'记录灯杆位置 L / cm = '},'pad':{'t':50}}]);f.update_xaxes(title_text='记录端电压 Uo / V',row=1,col=1);f.update_xaxes(title_text='标记负载 Rn / kΩ',row=1,col=2);f.update_yaxes(title_text='取样换算电流 I / mA',row=1,col=1);f.update_yaxes(title_text='回路电压差 / V',row=1,col=2)
    elif key=='ideal':
        f=go.Figure();factors=[5,10,15]
        for j,a in enumerate(factors):s=result['series'][f'ideal_a{a}'];f.add_trace(go.Scatter(x=s['x'],y=s['y'],mode='lines',line={'color':'black'},visible=j==1,showlegend=False))
        f.update_layout(sliders=[{'active':1,'steps':[{'method':'update','args':[{'visible':[i==j for i in range(3)]}],'label':str(a)} for j,a in enumerate(factors)],'currentvalue':{'prefix':'理想模型指数参数 a = '},'pad':{'t':50}}]);f.update_xaxes(title_text='归一化电压 V / Voc');f.update_yaxes(title_text='归一化电流 I / Iph')
    else:raise KeyError(key)
    f.update_layout(width=1000,height=540,paper_bgcolor='white',plot_bgcolor='white',font={'family':'Times New Roman, SimSun','size':18},margin={'l':105,'r':40,'t':30,'b':150});f.update_xaxes(showline=True,linecolor='black',gridcolor='#eeeeee');f.update_yaxes(showline=True,linecolor='black',gridcolor='#eeeeee')
    return f
