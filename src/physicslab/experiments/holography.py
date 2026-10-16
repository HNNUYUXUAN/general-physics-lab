import csv,json,math,re
from pathlib import Path
import numpy as np
def read_rows(root,index):
    with (Path(root)/'data'/f'observations-{index:02d}.csv').open(encoding='utf-8-sig',newline='') as f:return list(csv.reader(f))[1:]
def angle(value):
    parts=[float(x) for x in re.findall(r'-?\d+(?:\.\d+)?',value)]
    return parts[0]+(parts[1]/60 if len(parts)>1 else 0)+(parts[2]/3600 if len(parts)>2 else 0)
def separation(a,b):return abs((a-b+180)%360-180)
def mean_a(v):return float(np.mean(v)),float(np.std(v,ddof=1)/math.sqrt(len(v)))
def metric(v,unit,label):return {'value':float(v),'unit':unit,'label':label}
def table(h,r):return {'headers':h,'rows':r}
def tex(s):
    s=str(s)
    if '°' in s:
        v=re.findall(r'\d+(?:\.\d+)?',s)
        if len(v)>=2:return '$'+v[0]+r'^{\circ}'+v[1]+r"^{\prime}"+'$'
    pairs={'Δx_p':r'$\Delta x_p$','Δx_i':r'$\Delta x_i$','z_p':r'$z_p$','z_i':r'$z_i$','θ₁':r'$\theta_1$','θ₂':r'$\theta_2$','θ₃':r'$\theta_3$','θ₄':r'$\theta_4$','θ':'$\\theta$','δᵢ':r'$\delta_i$','δmin,i':r'$\delta_{\min,i}$','φᵢ':r'$\varphi_i$','Aᵢ':'$A_i$'}
    for a,b in pairs.items():s=s.replace(a,b)
    return s
def source_table(root,index):
    with (Path(root)/'data'/f'observations-{index:02d}.csv').open(encoding='utf-8-sig',newline='') as f:r=list(csv.reader(f))
    return table([tex(s) for s in r[0]],[[tex(s) for s in row] for row in r[1:]])


def analyze(experiment_dir):
    setup=np.array([[float(v) for v in row] for row in read_rows(experiment_dir,1)]);image=np.array([[float(v) for v in row] for row in read_rows(experiment_dir,2)]);ratio=setup[:,5]/setup[:,4];spacing=.6328/(2*np.sin(np.radians(setup[:,3])/2));mag=image[:,4]/image[:,3];km,ku=mean_a(ratio);mm,mu=mean_a(mag);visibility=2*np.sqrt(ratio)/(1+ratio);exposure=(setup[:,4]+setup[:,5])*setup[:,6];difference=abs(setup[:,2]-setup[:,1]);
    return {'metrics':{'fringe_spacing_um':metric(float(spacing.mean()),'um','理想平面波干涉条纹间距'),'mean_intensity_ratio':metric(km,'1','参考光与物光光强比均值'),'intensity_ratio_type_a':metric(ku,'1','光强比均值A类'),'mean_magnification':metric(mm,'1','再现横向放大率均值'),'magnification_type_a':metric(mu,'1','放大率均值A类'),'ideal_visibility_mean':metric(float(visibility.mean()),'1','等偏振完全相干理论可见度均值'),'mean_total_exposure_mj_cm2':metric(float(exposure.mean()),'mJ/cm^2','两束平均光强的曝光量均值'),'maximum_path_difference_cm':metric(float(difference.max()),'cm','最大记录光路差')},'tables':{'table1':source_table(experiment_dir,1),'table2':source_table(experiment_dir,2),'table3':table(['次数','$I_r/I_o$'],[[int(row[0]),round(float(k),8)] for row,k in zip(setup,ratio)]),'table4':table(['次数',r'$\Delta x_i/\Delta x_p$'],[[int(row[0]),round(float(v),8)] for row,v in zip(image,mag)])},'series':{'hologram-ratio':{'x':[1,2,3],'y':ratio.tolist(),'x_label':'测量次数','y_label':'光强比 $K=I_r/I_o$','label':'记录光强计算'},'hologram-magnification':{'x':[1,2,3],'y':mag.tolist(),'x_label':'测量次数','y_label':'横向放大率 $M$','label':'记录物像尺寸计算'}},'notes':['理论可见度假定相同偏振、完全相干、等波前稳定性，未作为实测条纹对比度。','相干长度和干板响应未记录，不能由光路差单独保证相干或曝光最佳。','只有三次重复，仪器、物像定位和干板处理误差未给。']}
def explore(key,result):
    import plotly.graph_objects as go
    ratio=result['metrics']['mean_intensity_ratio']['value'];x=np.linspace(0,6,1001);fig=go.Figure();steps=[]
    if key=='intensity-ratio':values=np.round(np.arange(.25,2.001,.05),2);default=1.;prefix='光强比 / 记录均值 = '
    elif key=='beam-angle':values=np.arange(10,61,5);default=30;prefix='两束平面波夹角 / ° = '
    else:raise KeyError(key)
    for i,value in enumerate(values):
        k=ratio*value if key=='intensity-ratio' else ratio;angle=value if key=='beam-angle' else 30.;spacing=.6328/(2*math.sin(math.radians(angle)/2));contrast=2*math.sqrt(k)/(1+k);intensity=1+contrast*np.cos(2*np.pi*x/spacing)
        fig.add_trace(go.Scatter(x=x,y=intensity,mode='lines',visible=value==default,line=dict(color='black',width=1.5),showlegend=False));mask=[False]*len(values);mask[i]=True;steps.append(dict(method='update',label=f'{value:g}',args=[{'visible':mask},{'annotations':[dict(text=f'K={k:.3f}；Λ={spacing:.4f} μm；理论可见度={contrast:.4f}',x=.01,y=1.13,xref='paper',yref='paper',showarrow=False,xanchor='left')]}]))
    active=list(values).index(default);fig.update_layout(template='plotly_white',font=dict(family='Times New Roman, SimSun',size=18),height=530,margin=dict(l=80,r=30,t=55,b=110),xaxis_title='干板横向位置 x / μm',yaxis_title='强度 I / (Io+Ir)',yaxis_range=[0,2.05],sliders=[dict(active=active,steps=steps,currentvalue=dict(prefix=prefix))],annotations=steps[active]['args'][1]['annotations']);return fig
