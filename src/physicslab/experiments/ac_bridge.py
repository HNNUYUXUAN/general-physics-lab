from pathlib import Path
import csv,json,math,cmath

def analyze(experiment_dir):
    p=Path(experiment_dir);cfg=json.loads((p/'experiment.json').read_text(encoding='utf-8'))
    with (p/'data/balance.csv').open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
    w=2*math.pi*cfg['frequency_Hz'];metrics,tables,series={},{},{};raw=[];processed=[];rs=[];cs=[];ds=[]
    for j,row in enumerate(rows,1):
        rn,cn,r3,r4=map(float,[row['Rn_Ohm'],row['Cn_uF'],row['R3_Ohm'],row['R4_Ohm']]);cn*=1e-6;rx=r4/r3*rn;cx=r3/r4*cn;loss=w*cn*rn;delta=math.atan(loss)*180/math.pi;xc=1/(w*cx);z=complex(rx,-xc);rs.append(rx);cs.append(cx);ds.append(loss)
        raw.append([j,rn,cn*1e6,r3,r4,int(float(row['null_gain']))]);processed.append([j,r3,r4,rn,round(rx,6),round(cx*1e6,9),round(loss,9),round(delta,6),round(abs(z),6)])
        for key,val,unit,label in [('Rx',rx,'Ω','串联损耗电阻'),('Cx',cx,'F','电容量'),('loss_factor',loss,'1','损耗因数'),('loss_angle',delta,'degree','损耗角'),('reactance',xc,'Ω','容抗幅值'),('impedance_magnitude',abs(z),'Ω','串联阻抗幅值'),('loss_identity_residual',w*rx*cx-loss,'1','两种损耗公式差')]:metrics[f'group{j}_{key}']={'value':val,'unit':unit,'label':f'第{j}组 '+label}
    for key,vals,unit,label in [('Rx_mean',rs,'Ω','损耗电阻均值'),('Cx_mean',cs,'F','电容量均值'),('loss_mean',ds,'1','损耗因数均值')]:metrics[key]={'value':sum(vals)/3,'unit':unit,'label':label}
    metrics['capacitance_spread_percent']={'value':(max(cs)-min(cs))/(sum(cs)/3)*100,'unit':'%','label':'电容量极差相对均值'};metrics['resistance_spread_percent']={'value':(max(rs)-min(rs))/(sum(rs)/3)*100,'unit':'%','label':'损耗电阻极差相对均值'}
    tables['observations']={'headers':['组号','$R_n/\\Omega$','$C_n/\\mu\\mathrm{F}$','$R_3/\\Omega$','$R_4/\\Omega$','指零仪增益'],'rows':raw};tables['results']={'headers':['组号','$R_3/\\Omega$','$R_4/\\Omega$','$R_n/\\Omega$','$R_x/\\Omega$','$C_x/\\mu\\mathrm{F}$','$\\tan\\delta$','损耗角 / °','$|Z_x|/\\Omega$'],'rows':processed}
    tables['summary']={'headers':['参数','均值','单位'],'rows':[['电容量',sum(cs)/3*1e6,'μF'],['损耗电阻',sum(rs)/3,'Ω'],['损耗因数',sum(ds)/3,'1']]}
    series['capacitance']={'x':[1,2,3],'y':[v*1e6 for v in cs],'x_label':'组号','y_label':r'电容量 $C_x\,/\,\mu\mathrm{F}$','label':'三组平衡结果'};series['loss_resistance']={'x':[1,2,3],'y':rs,'x_label':'组号','y_label':r'损耗电阻 $R_x\,/\,\Omega$','label':'三组平衡结果'}
    return {'metrics':metrics,'tables':tables,'series':series,'notes':['三组改变比率臂并非重复相同设置；散布不能直接代表准确度。','指零仪增益只记录为观察条件，不作为物理放大系数进入元件计算。','模平衡和相平衡均需满足；参数稳定不代表已知绝对误差。']}

def explore(key,result):
    if key!='complex-balance':raise KeyError(key)
    import plotly.graph_objects as go
    f=go.Figure();w=2*math.pi*1000;z1=complex(result['metrics']['group1_Rx']['value'],-1/(w*result['metrics']['group1_Cx']['value']));rns=[100+i for i in range(201)];scales=[.95,1,1.05]
    for j,scale in enumerate(scales):
        errors=[complex(rn,-1/(w*.1e-6))/(z1+complex(rn,-1/(w*.1e-6)))-10000/(9720*scale+10000) for rn in rns]
        f.add_trace(go.Scatter(x=[z.real for z in errors],y=[z.imag for z in errors],mode='lines',line={'color':'black'},visible=j==1,showlegend=False,customdata=rns,hovertemplate='Re=%{x:.6f}<br>Im=%{y:.6f}<br>Rn=%{customdata}Ω<extra></extra>'))
    f.add_hline(y=0,line_color='#888888',line_dash='dash');f.add_vline(x=0,line_color='#888888',line_dash='dash');f.update_layout(width=1000,height=580,paper_bgcolor='white',plot_bgcolor='white',font={'family':'Times New Roman, SimSun','size':18},sliders=[{'active':1,'steps':[{'method':'update','args':[{'visible':[i==j for i in range(3)]}],'label':str(scale)} for j,scale in enumerate(scales)],'currentvalue':{'prefix':'模型R4 / 第一组平衡R4 = '},'pad':{'t':50}}],margin={'l':110,'r':40,'t':30,'b':140});f.update_xaxes(title_text='桥输出 / E 的实部',showline=True,linecolor='black',gridcolor='#eeeeee');f.update_yaxes(title_text='桥输出 / E 的虚部',showline=True,linecolor='black',gridcolor='#eeeeee',scaleanchor='x',scaleratio=1)
    return f
