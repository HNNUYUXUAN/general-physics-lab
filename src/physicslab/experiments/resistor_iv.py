"""Ammeter/voltmeter loading and nonlinear forward diode observations."""
from pathlib import Path
import csv,json,math


def fit_line(x,y):
    n=len(x);xm=sum(x)/n;ym=sum(y)/n
    slope=sum((a-xm)*(b-ym) for a,b in zip(x,y))/sum((a-xm)**2 for a in x)
    intercept=ym-slope*xm
    residual=[b-slope*a-intercept for a,b in zip(x,y)]
    sse=sum(v*v for v in residual);sst=sum((b-ym)**2 for b in y)
    return slope,intercept,1-sse/sst if sst else 1,math.sqrt(sse/n)


def analyze(experiment_dir):
    base=Path(experiment_dir)
    cfg=json.loads((base/'experiment.json').read_text(encoding='utf-8'))
    with (base/'data/resistors.csv').open(encoding='utf-8',newline='') as fh:data=list(csv.DictReader(fh))
    with (base/'data/diode.csv').open(encoding='utf-8',newline='') as fh:diode=list(csv.DictReader(fh))
    metrics,tables,series={},{},{}
    def add(k,v,u,label):metrics[k]={'value':float(v),'unit':u,'label':label}
    original=[];derived=[];fitrows=[]
    for connection in ['internal','external']:
        for resistor in ['R1','R2']:
            key=f'{connection}_{resistor}';items=[r for r in data if r['connection']==connection and r['resistor']==resistor]
            u=[float(r['voltage_V']) for r in items];i=[float(r['current_mA'])*1e-3 for r in items]
            if len(items)!=7 or any(v<=0 for v in i):raise ValueError('Expected seven positive current observations')
            resistance=[a/b for a,b in zip(u,i)]
            avg=sum(resistance)/len(resistance);origin=sum(a*b for a,b in zip(i,u))/sum(a*a for a in i)
            slope,intercept,r2,rmse=fit_line(i,u)
            for k,v,unit,label in [('R_mean',avg,'Ω','逐点电阻均值'),('R_origin',origin,'Ω','过原点拟合电阻'),('R_slope',slope,'Ω','含截距拟合电阻'),('U_intercept',intercept,'V','电压拟合截距'),('fit_R2',r2,'1','拟合决定系数'),('fit_rmse',rmse,'V','电压拟合均方根残差')]:add(key+'_'+k,v,unit,('内接' if connection=='internal' else '外接')+' '+resistor+' '+label)
            title='内接法' if connection=='internal' else '外接法'
            original.append([title,resistor,'$U/\\mathrm{V}$']+u+['2 V'])
            original.append(['','','$I/\\mathrm{mA}$']+[v*1e3 for v in i]+[cfg['current_ranges_mA'][resistor]])
            derived.append([title,resistor]+[round(v,3) for v in resistance]+[round(avg,3)])
            fitrows.append([title,resistor,round(avg,3),round(origin,3),round(slope,3),round(intercept,6),round(r2,6)])
            series[key]={'x':[v*1e3 for v in i],'y':u,'x_label':r'电流 $I\,/\,\mathrm{mA}$','y_label':r'电压 $U\,/\,\mathrm{V}$','label':title+' '+resistor,'fit':True}
    u=[float(r['voltage_V']) for r in diode];i=[float(r['current_mA']) for r in diode]
    if any(b<=a for a,b in zip(u,u[1:])) or any(x<=0 for x in i):raise ValueError('Invalid diode record')
    add('diode_current_06',i[5],'mA','0.60 V时记录电流')
    add('diode_current_065',i[6],'mA','0.65 V时记录电流（量程待核）')
    add('diode_gain_04_06',i[5]/i[2],'1','0.40–0.60 V电流增大倍数')
    beta,lnis,diode_r2,rmse=fit_line(u[2:6],[math.log(v) for v in i[2:6]])
    add('diode_log_slope_04_06',beta,'1/V','0.40–0.60 V半对数斜率')
    add('diode_log_R2_04_06',diode_r2,'1','0.40–0.60 V半对数决定系数')
    series['diode_forward']={'x':u,'y':i,'x_label':r'正向电压 $U\,/\,\mathrm{V}$','y_label':r'正向电流 $I\,/\,\mathrm{mA}$','label':'二极管正向记录（最高点量程待核）'}
    series['diode_log']={'x':u[2:6],'y':[math.log(v) for v in i[2:6]],'x_label':r'正向电压 $U\,/\,\mathrm{V}$','y_label':r'$\ln[I/(1\,\mathrm{mA})]$','label':'0.40–0.60 V 半对数分析','fit':True}
    tables['observations']={'headers':['接法','元件','物理量']+[str(j) for j in range(1,8)]+['量程'],'rows':original}
    tables['point_resistance']={'headers':['接法','元件']+[f'$R_{j}/\\Omega$' for j in range(1,8)]+['均值 / Ω'],'rows':derived}
    tables['fits']={'headers':['接法','元件','均值 / Ω','过原点拟合 / Ω','含截距斜率 / Ω','截距 / V','$r^2$'],'rows':fitrows}
    tables['diode']={'headers':['物理量']+[str(j) for j in range(1,8)]+['量程'],'rows':[['$U/\\mathrm{V}$']+u+['2 V'],['$I/\\mathrm{mA}$']+i+['2 mA（最高点超出，待核）'],['反向特性']+['未测']*7+['—']]}
    # Loading-error model uses explicit dimensionless model parameters.
    for k in cfg['model']['voltmeter_ammeter_ratios']:
        x=[10**(-1+j/80) for j in range(561)]
        series[f'loading_k{k}']={'x':[math.log10(v) for v in x],'y':[100*v/(v+k) for v in x],'x_label':r'$\log_{10}(R_x/R_A)$','y_label':'外接法相对误差绝对值 / %','label':f'模型 RV/RA={k}','model':True}
        add(f'model_k{k}_crossover',(math.sqrt(1+4*k)+1)/2,'1','等相对误差时的模型Rx/RA')
    return {'metrics':metrics,'tables':tables,'series':series,'notes':['R2低电流记录只有0.001 mA步进，均值与拟合的差异不能忽略。','二极管4.511 mA高于表内2 mA量程，保留记录但未用于半对数拟合。','未测反向特性，不能据此实验验证单向导电性。']}


def explore(key,result):
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    if key=='fit':
        fig=make_subplots(rows=1,cols=2,horizontal_spacing=.16)
        states=[]
        for name in ['internal_R1','external_R1','internal_R2','external_R2']:
            s=result['series'][name];x=s['x'];y=s['y']
            for start in [0,3]:
                a,b,_,_=fit_line(x[start:],y[start:]);yp=[a*v+b for v in x]
                index=len(states);states.append((name,start))
                for trace,col in [(go.Scatter(x=x,y=y,mode='markers',marker={'color':'black','symbol':'circle-open','size':8}),1),(go.Scatter(x=x,y=yp,mode='lines',line={'color':'black'}),1),(go.Scatter(x=x,y=[v-w for v,w in zip(y,yp)],mode='markers+lines',marker={'color':'black','symbol':'circle-open'},line={'color':'black'}),2)]:
                    trace.visible=index==0;trace.showlegend=False;fig.add_trace(trace,row=1,col=col)
        steps=[]
        for j,(name,start) in enumerate(states):
            mask=[False]*(len(states)*3);mask[j*3:j*3+3]=[True]*3
            steps.append({'method':'update','args':[{'visible':mask}],'label':name.replace('internal','内接').replace('external','外接')+(' 全部7点' if start==0 else '高电压4点')})
        fig.update_layout(sliders=[{'steps':steps,'active':0,'pad':{'t':50},'currentvalue':{'prefix':'拟合选择：'}}])
        fig.update_xaxes(title_text='电流 I / mA');fig.update_yaxes(title_text='电压 U / V',row=1,col=1);fig.update_yaxes(title_text='电压残差 / V',row=1,col=2)
    elif key=='loading':
        fig=go.Figure();xs=[10**(-1+j/80) for j in range(561)];ks=[1000,10000,1000000]
        for j,k in enumerate(ks):
            fig.add_trace(go.Scatter(x=xs,y=[100/x for x in xs],mode='lines',line={'color':'black'},name='内接法',visible=j==1))
            fig.add_trace(go.Scatter(x=xs,y=[100*x/(x+k) for x in xs],mode='lines',line={'color':'black','dash':'dash'},name='外接法',visible=j==1))
        steps=[]
        for j,k in enumerate(ks):
            mask=[False]*6;mask[j*2:j*2+2]=[True]*2;steps.append({'method':'update','args':[{'visible':mask}],'label':f'RV/RA={k}'})
        fig.update_layout(sliders=[{'steps':steps,'active':1,'pad':{'t':50},'currentvalue':{'prefix':'模型仪表内阻比：'}}])
        fig.update_xaxes(type='log',title_text='电阻比 Rx / RA');fig.update_yaxes(type='log',title_text='相对加载误差绝对值 / %')
    else:raise KeyError(key)
    fig.update_layout(height=530,width=1000,paper_bgcolor='white',plot_bgcolor='white',font={'family':'Times New Roman, SimSun','size':18},margin={'l':95,'r':40,'t':30,'b':160})
    fig.update_xaxes(showline=True,linecolor='black',gridcolor='#eeeeee',ticks='inside');fig.update_yaxes(showline=True,linecolor='black',gridcolor='#eeeeee',ticks='inside')
    return fig
