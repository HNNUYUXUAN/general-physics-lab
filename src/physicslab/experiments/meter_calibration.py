from pathlib import Path
import csv,json,math

def line(x,y):
    xm=sum(x)/len(x);ym=sum(y)/len(y);a=sum((v-xm)*(w-ym) for v,w in zip(x,y))/sum((v-xm)**2 for v in x);return a,ym-a*xm

def analyze(experiment_dir):
    p=Path(experiment_dir);cfg=json.loads((p/'experiment.json').read_text(encoding='utf-8'));metrics,tables,series={},{},{}
    for kind,unit,fs in [('current','mA',5),('voltage','V',1.5)]:
        with (p/f'data/{kind}.csv').open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
        x=[float(r['indicated']) for r in rows];up=[float(r['standard_up']) for r in rows];down=[float(r['standard_down']) for r in rows];mean=[(a+b)/2 for a,b in zip(up,down)];err=[a-b for a,b in zip(x,mean)];h=[abs(a-b) for a,b in zip(up,down)];slope,intercept=line(x,mean)
        metrics[kind+'_max_error']={'value':max(abs(v) for v in err),'unit':unit,'label':('电流' if kind=='current' else '电压')+' 最大示值误差绝对值'}
        metrics[kind+'_FS_error_percent']={'value':max(abs(v) for v in err)/fs*100,'unit':'%','label':kind+' 相对满量程最大误差'}
        metrics[kind+'_max_hysteresis']={'value':max(h),'unit':unit,'label':kind+' 最大往返读数差'}
        metrics[kind+'_correction_slope']={'value':slope,'unit':'1','label':kind+' 标准均值对改装示值拟合斜率'}
        metrics[kind+'_correction_intercept']={'value':intercept,'unit':unit,'label':kind+' 校准拟合截距'}
        tables[kind+'_observations']={'headers':[f'改装示值 / {unit}',f'标准上行 / {unit}',f'标准下行 / {unit}','源表平均列','源表“误差”列'],'rows':[[x[j],up[j],down[j],cfg['source_calibration_columns'][kind]['means'][j],cfg['source_calibration_columns'][kind]['errors'][j]] for j in range(len(x))]}
        tables[kind+'_calibration']={'headers':[f'改装示值 / {unit}',f'标准均值 / {unit}',f'示值−标准均值 / {unit}',f'往返差绝对值 / {unit}'],'rows':[[x[j],round(mean[j],6),round(err[j],6),round(h[j],6)] for j in range(len(x))]}
        series[kind+'_error']={'x':x,'y':err,'x_label':f'改装示值 / {unit}','y_label':f'示值−标准均值 / {unit}','label':'全部原记录点'}
        series[kind+'_correction']={'x':x,'y':mean,'x_label':f'改装示值 / {unit}','y_label':f'标准均值 / {unit}','label':'全部原记录点','fit':True}
    rg,ig=cfg['design']['Rg_inferred_Ohm'],cfg['design']['Ig_A']
    values={'shunt_resistance':(rg/(5-1),'Ω','5 mA设计分流电阻'),'series_resistance':(1.5/ig-rg,'Ω','1.5 V设计串联电阻'),'original_Rw_at_16':(1.6/ig-rg-1000,'Ω','原限流电阻设计在1.6 V所需调零电阻'),'improved_Rw_at_13':(1.3/ig-rg-1100,'Ω','改进设计在1.3 V所需调零电阻'),'improved_Rw_at_16':(1.6/ig-rg-1100,'Ω','改进设计在1.6 V所需调零电阻')}
    for k,(v,u,l) in values.items():metrics[k]={'value':v,'unit':u,'label':l}
    tables['ohm_record']={'headers':['记录列']+cfg['ohm_headers'],'rows':[['偏转格数']+cfg['ohm_deflections']]}
    tables['zero_design']={'headers':['限流电阻 / Ω','电源1.3 V所需调零电阻 / Ω','电源1.5 V所需调零电阻 / Ω','电源1.6 V所需调零电阻 / Ω','470 Ω电位器是否覆盖'],'rows':[[r3,round(1.3/ig-rg-r3,3),round(1.5/ig-rg-r3,3),round(1.6/ig-rg-r3,3),'否' if r3==1000 else '是（理想模型）'] for r3 in [1000,1100]]}
    xs=[i*15 for i in range(401)];series['ohm_model']={'x':xs,'y':[1.5/(1500+x)/ig for x in xs],'x_label':r'待测电阻 $R_x\,/\,\Omega$','y_label':r'表头偏转 $I/I_g$','label':'E=1.5 V、总内部电阻1500 Ω理想模型','model':True}
    return {'metrics':metrics,'tables':tables,'series':series,'notes':['表头30Ω为设计结论反推值，无独立内阻测量记录。','电压1.25V行保留未改，其参考读数异常需核验。','欧姆表标度对应阻值不全且格数非单调，未反演未知电阻。']}

def explore(key,result):
    if key!='zero-design':raise KeyError(key)
    import plotly.graph_objects as go
    e=[1.3+j*.003 for j in range(101)];f=go.Figure()
    for j,r3 in enumerate([1000,1100]):f.add_trace(go.Scatter(x=e,y=[v/.001-30-r3 for v in e],mode='lines',line={'color':'black'},visible=j==1,showlegend=False))
    f.add_hline(y=470,line_color='#888888',line_dash='dash');f.add_hline(y=0,line_color='#888888',line_dash='dash')
    f.update_layout(width=1000,height=520,paper_bgcolor='white',plot_bgcolor='white',font={'family':'Times New Roman, SimSun','size':18},sliders=[{'active':1,'steps':[{'method':'update','args':[{'visible':[j==0,j==1]}],'label':str(r3)} for j,r3 in enumerate([1000,1100])],'currentvalue':{'prefix':'模型限流电阻 R3 / Ω = '},'pad':{'t':50}}],margin={'l':105,'r':40,'t':30,'b':140});f.update_xaxes(title_text='电源 E / V',showline=True,linecolor='black',gridcolor='#eeeeee');f.update_yaxes(title_text='所需调零电阻 Rw / Ω',showline=True,linecolor='black',gridcolor='#eeeeee')
    return f
