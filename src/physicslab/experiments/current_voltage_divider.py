from pathlib import Path
import csv,json,math

def shape(kind,k,x):return 1/(k+x) if kind=='current' else k*x/(k+x*(1-x))

def analyze(experiment_dir):
    p=Path(experiment_dir);metrics,tables,series={},{},{}
    with (p/'data/observations.csv').open(encoding='utf-8',newline='') as f:records=list(csv.DictReader(f))
    summary=[]
    for kind in ['current','voltage']:
        original=[]
        for k in [.1,.5,1.]:
            rows=[r for r in records if r['kind']==kind and float(r['K'])==k];x=[float(r['X']) for r in rows];y=[float(r['reading']) for r in rows]
            w=[shape(kind,k,a) for a in x];amp=sum(a*b for a,b in zip(w,y))/sum(a*a for a in w);pred=[amp*a for a in w]
            residual=[b-a for a,b in zip(pred,y)];rmse=math.sqrt(sum(v*v for v in residual)/len(y));maxrel=max(abs(a)/b*100 for a,b in zip(residual,y))
            key=f'{kind}_K{str(k).replace(".","p")}';unit='原记录电流单位' if kind=='current' else '原记录电压单位'
            for suffix,v,u,label in [('amplitude',amp,unit,'物理模型幅度估计'),('rmse',rmse,unit,'模型均方根残差'),('max_relative_residual',maxrel,'%','最大相对读数残差')]:metrics[key+'_'+suffix]={'value':v,'unit':u,'label':kind+f' K={k} '+label}
            original.append([k]+y);summary.append(["制流" if kind=="current" else "分压",k,round(amp,6),round(rmse,6),round(maxrel,3)])
            series[key]={'x':x,'y':y,'x_label':r'滑块位置 $X=R_{AC}/R_0$','y_label':'电流 / 原记录单位' if kind=='current' else '电压 / 原记录单位','label':f'K={k}'}
            series[key+'_residual']={'x':x,'y':residual,'x_label':r'滑块位置 $X$','y_label':'观测−物理模型 / 原记录单位','label':f'K={k}'}
        tables[kind+'_observations']={'headers':['$K$']+[f'$X={j/10:g}$' for j in range(1,11)],'rows':original}
    tables['model_fit']={'headers':['接法','参数 $K$','模型幅度（原记录单位）','均方根残差（原记录单位）','最大相对残差 / %'],'rows':summary}
    x=[j/400 for j in range(401)]
    for k in [.1,.5,1.,2.,10.]:
        stem=str(k).replace('.','p')
        for kind in ['current','voltage']:
            y=[k/(k+a) if kind=='current' else shape(kind,k,a) for a in x]
            series[f'model_{kind}_K{stem}']={'x':x,'y':y,'x_label':r'滑块位置 $X$','y_label':r'$I/I_{\max}$' if kind=='current' else r'$U/E$','label':f'理想模型 K={k}','model':True}
        metrics[f'model_K{stem}_current_end']={'value':k/(k+1),'unit':'1','label':f'K={k} 制流末端归一化电流'}
        metrics[f'model_K{stem}_voltage_mid']={'value':shape('voltage',k,.5),'unit':'1','label':f'K={k} 分压中点归一化电压'}
    return {'metrics':metrics,'tables':tables,'series':series,'notes':['原表未注明I、U读数单位；未推定mA或V。','电源E、R0、负载实际阻值未记录；A和E来自各曲线物理模型幅度估计。','观测不覆盖X=0；端点零电压为模型性质，非实测记录。']}

def explore(key,result):
    if key!='divider':raise KeyError(key)
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    fig=make_subplots(rows=1,cols=2,horizontal_spacing=.15);ks=[.1,.5,1.,2.,10.];x=[j/400 for j in range(401)]
    for j,k in enumerate(ks):
        for kind,col in [('current',1),('voltage',2)]:
            y=[k/(k+a) if kind=='current' else shape(kind,k,a) for a in x];fig.add_trace(go.Scatter(x=x,y=y,mode='lines',line={'color':'black'},showlegend=False,visible=j==2),row=1,col=col)
    steps=[]
    for j,k in enumerate(ks):mask=[False]*10;mask[j*2:j*2+2]=[True,True];steps.append({'method':'update','args':[{'visible':mask}],'label':str(k)})
    fig.update_layout(width=1000,height=520,paper_bgcolor='white',plot_bgcolor='white',font={'family':'Times New Roman, SimSun','size':18},sliders=[{'steps':steps,'active':2,'currentvalue':{'prefix':'模型参数 K = '},'pad':{'t':50}}],margin={'l':85,'r':30,'t':30,'b':140})
    fig.update_xaxes(title_text='滑块位置 X',range=[0,1],showline=True,linecolor='black',gridcolor='#eeeeee');fig.update_yaxes(title_text='归一化电流 I / Imax',row=1,col=1,range=[0,1.05],showline=True,linecolor='black',gridcolor='#eeeeee');fig.update_yaxes(title_text='归一化电压 U / E',row=1,col=2,range=[0,1.05],showline=True,linecolor='black',gridcolor='#eeeeee')
    return fig
