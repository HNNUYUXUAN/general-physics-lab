from pathlib import Path
import csv,json,math

def analyze(experiment_dir):
    p=Path(experiment_dir);cfg=json.loads((p/'experiment.json').read_text(encoding='utf-8'))
    with (p/'data/balance.csv').open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
    l=[float(r['length_mm'])/1000 for r in rows];rx=[float(r['S_Ohm'])/float(r['M_Ohm'])*float(r['comparison_Ohm']) for r in rows];diam=cfg['diameter_mm']/1000;area=math.pi*diam**2/4;rho=[r*area/z for r,z in zip(rx,l)];mean=sum(rho)/len(rho);sd=math.sqrt(sum((v-mean)**2 for v in rho)/(len(rho)-1));xm=sum(l)/5;ym=sum(rx)/5;slope=sum((a-xm)*(b-ym) for a,b in zip(l,rx))/sum((a-xm)**2 for a in l);intercept=ym-slope*xm
    values={'cross_section':(area,'m²','导体横截面积'),'rho_mean':(mean,'Ω·m','五长度电阻率均值'),'rho_sd_descriptive':(sd,'Ω·m','五长度电阻率描述性标准差'),'rho_from_slope':(slope*area,'Ω·m','含截距R–L拟合电阻率'),'resistance_slope':(slope,'Ω/m','R–L斜率'),'resistance_intercept':(intercept,'Ω','R–L截距'),'model_matched_contact_shift':(0,'Ω','比率匹配时接触电阻修正项')}
    for j,v in enumerate(rx,1):values[f'R{j}']=(v,'Ω',f'第{j}长度平衡电阻');values[f'rho{j}']=(rho[j-1],'Ω·m',f'第{j}长度电阻率')
    metrics={k:{'value':v,'unit':u,'label':label} for k,(v,u,label) in values.items()}
    tables={'observations':{'headers':['长度 / mm','$S/\\Omega$','$M/\\Omega$','比较臂 / Ω','源原始表Rx列 / Ω','直径 / mm'],'rows':[[float(v['length_mm']),float(v['S_Ohm']),float(v['M_Ohm']),float(v['comparison_Ohm']),cfg['source_raw_Rx'][j],cfg['diameter_mm']] for j,v in enumerate(rows)]},'results':{'headers':['序号','长度 / m','平衡电阻 / Ω','电阻率 / (Ω·m)'],'rows':[[j+1,l[j],rx[j],rho[j]] for j in range(5)]},'summary':{'headers':['指标','数值','单位'],'rows':[[v['label'],v['value'],v['unit']] for v in list(metrics.values())[:6]]}}
    series={'R_length':{'x':l,'y':[v*1000 for v in rx],'x_label':r'长度 $L\,/\,\mathrm{m}$','y_label':r'电阻 $R_x\,/\,\mathrm{m}\Omega$','label':'双臂平衡结果','fit':True},'rho_length':{'x':[v*1000 for v in l],'y':[v*1e8 for v in rho],'x_label':r'长度 $L\,/\,\mathrm{mm}$','y_label':r'$\rho/(10^{-8}\,\Omega\,\mathrm{m})$','label':'逐长度电阻率'}}
    return {'metrics':metrics,'tables':tables,'series':series,'notes':['原始表Rx列比S/M计算值大1000倍，统一按实际比率与比较臂重算。','不同长度得到的rho散布是描述性统计，不代替重复测量A类不确定度。','说明书最低区间等级0.5%，源0.2%及限差公式未沿用。']}

def explore(key,result):
    if key!='diameter':raise KeyError(key)
    import plotly.graph_objects as go
    f=go.Figure();diameters=[3.9,4,4.1];s=result['series']['rho_length']
    for j,d in enumerate(diameters):f.add_trace(go.Scatter(x=s['x'],y=[v*(d/4)**2 for v in s['y']],mode='lines+markers',line={'color':'black'},marker={'color':'white','line':{'color':'black','width':1.5}},visible=j==1,showlegend=False))
    f.update_layout(width=1000,height=520,paper_bgcolor='white',plot_bgcolor='white',font={'family':'Times New Roman, SimSun','size':18},sliders=[{'active':1,'steps':[{'method':'update','args':[{'visible':[i==j for i in range(3)]}],'label':str(d)} for j,d in enumerate(diameters)],'currentvalue':{'prefix':'模型直径 D / mm = '},'pad':{'t':50}}],margin={'l':100,'r':40,'t':30,'b':140});f.update_xaxes(title_text='导体长度 L / mm',showline=True,linecolor='black',gridcolor='#eeeeee');f.update_yaxes(title_text='电阻率 ρ / (10⁻⁸ Ω·m)',showline=True,linecolor='black',gridcolor='#eeeeee')
    return f
