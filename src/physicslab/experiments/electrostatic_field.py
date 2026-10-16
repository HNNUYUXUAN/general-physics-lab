from pathlib import Path
import csv,json,math

def analyze(experiment_dir):
    p=Path(experiment_dir);cfg=json.loads((p/'experiment.json').read_text(encoding='utf-8'))
    with (p/'data/reported_radii.csv').open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
    a,b,u0=cfg['inner_radius_cm'],cfg['outer_radius_cm'],cfg['inner_voltage_V'];den=math.log(b/a)
    u=[float(r['voltage_V']) for r in rows];r=[float(v['radius_cm']) for v in rows];interior=list(range(8));x=[u[j]/u0 for j in interior];y=[math.log(r[j]) for j in interior]
    xm=sum(x)/8;ym=sum(y)/8;slope=sum((v-xm)*(w-ym) for v,w in zip(x,y))/sum((v-xm)**2 for v in x);intercept=ym-slope*xm
    residual=[w-slope*v-intercept for v,w in zip(x,y)];r2=1-sum(v*v for v in residual)/sum((v-ym)**2 for v in y)
    pred=[u0*math.log(b/v)/den for v in r];errors=[pred[j]-u[j] for j in interior]
    metrics={}
    for key,value,unit,label in [('lnr_slope',slope,'1','内点线性化斜率'),('lnr_intercept',intercept,'1','内点线性化截距'),('fit_R2',r2,'1','线性化决定系数'),('theory_slope',-den,'1','同轴理论斜率'),('theory_intercept',math.log(b),'1','同轴理论截距'),('max_voltage_difference',max(abs(v) for v in errors),'V','八内点最大电压差绝对值'),('voltage_rmse',math.sqrt(sum(v*v for v in errors)/8),'V','八内点电压均方根差'),('inner_field',u0/((a/100)*den),'V/m','内边界理想电场'),('outer_field',u0/((b/100)*den),'V/m','外边界理想电场')]:metrics[key]={'value':value,'unit':unit,'label':label}
    source=cfg['source_summary']
    tables={'source_summary':{'headers':['$U/\\mathrm{V}$','$U/U_0$','源表对数列','$r/\\mathrm{cm}$','$D/\\mathrm{mm}$'],'rows':source},'recalculated':{'headers':['$U/\\mathrm{V}$','$r/\\mathrm{cm}$','$\\ln[r/(1\\,\\mathrm{cm})]$','$U_{\\mathrm{th}}/\\mathrm{V}$','理论−记录 / V'],'rows':[[u[j],r[j],round(math.log(r[j]),6),round(pred[j],6),round(pred[j]-u[j],6)] for j in range(len(u))]},'fit':{'headers':['指标','数值'],'rows':[[v['label'],round(v['value'],6)] for v in list(metrics.values())[:7]]}}
    series={'linearized':{'x':x,'y':y,'x_label':r'归一化电压 $U/U_0$','y_label':r'$\ln[r/(1\,\mathrm{cm})]$','label':'八个内点汇总半径','fit':True},'voltage_difference':{'x':r[:8],'y':errors,'x_label':r'半径 $r\,/\,\mathrm{cm}$','y_label':'理论电压−记录电压 / V','label':'八个内点'}}
    radii=[a+(b-a)*j/400 for j in range(401)]
    series['potential_profile']={'x':radii,'y':[u0*math.log(b/z)/den for z in radii],'x_label':r'半径 $r\,/\,\mathrm{cm}$','y_label':r'电势 $\varphi\,/\,\mathrm{V}$','label':'理想同轴模型','model':True}
    series['field_profile']={'x':radii,'y':[u0/(z/100*den) for z in radii],'x_label':r'半径 $r\,/\,\mathrm{cm}$','y_label':r'电场强度 $E_r\,/\,(\mathrm{V}/\mathrm{m})$','label':'理想同轴模型','model':True}
    return {'metrics':metrics,'tables':tables,'series':series,'notes':['输入来自报告汇总半径，不含逐方向点坐标或重复尺寸。','对数列和直径列不作为独立观测参与拟合。','线性拟合仅使用八个内点，边界用于理论定义。']}

def explore(key,result):
    if key!='coaxial':raise KeyError(key)
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    a,b=1.05,6.94;den=math.log(b/a);r=[a+(b-a)*j/400 for j in range(401)];f=make_subplots(rows=1,cols=2,horizontal_spacing=.16)
    for j,u in enumerate([5,10,15]):
        for y,col in [([u*math.log(b/z)/den for z in r],1),([u/(z/100*den) for z in r],2)]:f.add_trace(go.Scatter(x=r,y=y,mode='lines',line={'color':'black'},visible=j==1,showlegend=False),row=1,col=col)
    steps=[]
    for j,u in enumerate([5,10,15]):mask=[False]*6;mask[2*j:2*j+2]=[True,True];steps.append({'method':'update','args':[{'visible':mask}],'label':str(u)})
    f.update_layout(width=1000,height=520,paper_bgcolor='white',plot_bgcolor='white',font={'family':'Times New Roman, SimSun','size':18},sliders=[{'steps':steps,'active':1,'currentvalue':{'prefix':'模型内电极电压 / V = '},'pad':{'t':50}}],margin={'l':90,'r':40,'t':30,'b':140});f.update_xaxes(title_text='半径 r / cm',showline=True,linecolor='black',gridcolor='#eeeeee');f.update_yaxes(title_text='电势 φ / V',row=1,col=1,showline=True,linecolor='black',gridcolor='#eeeeee');f.update_yaxes(title_text='径向电场 Er / (V/m)',row=1,col=2,showline=True,linecolor='black',gridcolor='#eeeeee')
    return f
