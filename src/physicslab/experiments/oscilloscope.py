from pathlib import Path
import csv,json,math

def wave(kind,t):
    phase=(t*1000)%1
    if kind=='sine':return .5*math.sin(2*math.pi*phase)
    if kind=='triangle':return .5*(1-4*abs(phase-.5))
    return .5 if phase<.5 else -.5

def analyze(experiment_dir):
    p=Path(experiment_dir);cfg=json.loads((p/'experiment.json').read_text(encoding='utf-8'))
    with (p/'data/waveforms.csv').open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
    with (p/'data/lissajous.csv').open(encoding='utf-8',newline='') as f:liss=list(csv.DictReader(f))
    metrics,tables,series={},{},{};volrows=[];timerows=[]
    for r in rows:
        k=r['waveform'];upp=float(r['volts_per_div'])*float(r['vertical_div']);up=upp/2;rms=up/({'sine':math.sqrt(2),'triangle':math.sqrt(3),'square':1}[k]);meter=float(r['meter_rms_V']);T=float(r['ms_per_div'])*float(r['horizontal_div'])*1e-3;freq=1/T;deviation=(meter-rms)/rms*100
        for suffix,v,u,label in [('U_pp',upp,'V','峰峰值'),('U_peak',up,'V','峰值'),('U_rms',rms,'V','几何波形有效值'),('meter_deviation_percent',deviation,'%','毫伏表与波形有效值偏差'),('period',T,'s','周期'),('frequency',freq,'Hz','周期法频率')]:metrics[k+'_'+suffix]={'value':v,'unit':u,'label':r['label']+' '+label}
        volrows.append([r['label'],float(r['volts_per_div']),float(r['vertical_div']),upp,cfg['source_rms'][k],round(rms,6),meter,round(deviation,3)])
        timerows.append([r['label'],float(r['ms_per_div']),float(r['horizontal_div']),T,freq,float(r['source_Hz'])])
        ts=[j*2e-6 for j in range(1001)];series[k+'_wave']={'x':[t*1e3 for t in ts],'y':[wave(k,t) for t in ts],'x_label':r'时间 $t\,/\,\mathrm{ms}$','y_label':r'电压 $u\,/\,\mathrm{V}$','label':'理想'+r['label']+'（示意）','model':True}
    inferred=[];lissrows=[]
    for j,r in enumerate(liss,1):
        fx=float(r['standard_Hz']);nx=int(r['horizontal_count']);ny=int(r['vertical_count']);fy=fx*nx/ny;inferred.append(fy)
        metrics[f'lissajous_{j}_frequency']={'value':fy,'unit':'Hz','label':f'李萨如第{j}组频率'}
        lissrows.append([fx,nx,ny,fy])
        # 250 Hz is the common fundamental of all supplied frequency pairs.
        ts=[v*4e-6 for v in range(1001)];series[f'lissajous_{j}']={'x':[math.sin(2*math.pi*fx*t) for t in ts],'y':[math.sin(2*math.pi*fy*t+math.pi/4) for t in ts],'x_label':r'归一化水平电压 $u_x/A_x$','y_label':r'归一化垂直电压 $u_y/A_y$','label':f'理想频率比 {fy:g}:{fx:g}，相位π/4','model':True,'equal_aspect':True}
    metrics['lissajous_mean_frequency']={'value':sum(inferred)/len(inferred),'unit':'Hz','label':'李萨如频率均值'}
    tables['voltage']={'headers':['波形','$k_V/(\\mathrm{V/div})$','$y/\\mathrm{div}$','$U_{pp}/\\mathrm{V}$','源有效值 / V','重算有效值 / V','毫伏表 / V','相对重算值偏差 / %'],'rows':volrows}
    tables['period']={'headers':['波形','扫描 / (ms/div)','水平长度 / div','周期 / s','重算频率 / Hz','信号源 / Hz'],'rows':timerows}
    tables['lissajous']={'headers':['标准频率 / Hz','$N_x$','$N_y$','重算频率 / Hz'],'rows':lissrows}
    return {'metrics':metrics,'tables':tables,'series':series,'notes':['源正弦有效值0.5V为处理错误，原几何读数不变。','李萨如模拟相位π/4为展示参数，非截图相位测量。','缺少读格和仪器限差，未把读数吻合表述为精确频率真值。']}

def explore(key,result):
    import plotly.graph_objects as go
    if key=='waveforms':
        f=go.Figure();names=['sine','triangle','square']
        for j,k in enumerate(names):s=result['series'][k+'_wave'];f.add_trace(go.Scatter(x=s['x'],y=s['y'],mode='lines',line={'color':'black'},visible=j==0,showlegend=False))
        steps=[{'method':'update','args':[{'visible':[i==j for i in range(3)]}],'label':['正弦','三角','方波'][j]} for j in range(3)];xlabel='时间 t / ms';ylabel='电压 u / V';active=0
    elif key=='lissajous':
        f=go.Figure();pairs=[(fx,phase) for fx in [250,500,1000,1500,2000] for phase in [0,math.pi/4,math.pi/2]]
        for j,(fx,phase) in enumerate(pairs):ts=[v*4e-6 for v in range(1001)];f.add_trace(go.Scatter(x=[math.sin(2*math.pi*fx*t) for t in ts],y=[math.sin(2*math.pi*1000*t+phase) for t in ts],mode='lines',line={'color':'black'},visible=j==1,showlegend=False))
        steps=[{'method':'update','args':[{'visible':[i==j for i in range(15)]}],'label':f'fx={fx}Hz / φ={phase/math.pi:.2g}π'} for j,(fx,phase) in enumerate(pairs)];xlabel='归一化水平电压 ux / Ax';ylabel='归一化垂直电压 uy / Ay';active=1;f.update_yaxes(scaleanchor='x',scaleratio=1)
    else:raise KeyError(key)
    f.update_layout(width=1000,height=580,paper_bgcolor='white',plot_bgcolor='white',font={'family':'Times New Roman, SimSun','size':18},sliders=[{'active':active,'steps':steps,'currentvalue':{'prefix':'模型选择：'},'pad':{'t':55}}],margin={'l':100,'r':40,'t':30,'b':160});f.update_xaxes(title_text=xlabel,showline=True,linecolor='black',gridcolor='#eeeeee');f.update_yaxes(title_text=ylabel,showline=True,linecolor='black',gridcolor='#eeeeee')
    return f
