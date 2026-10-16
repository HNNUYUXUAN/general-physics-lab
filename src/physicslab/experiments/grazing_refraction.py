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
    pairs={'θ₁':r'$\theta_1$','θ₂':r'$\theta_2$','θ₃':r'$\theta_3$','θ₄':r'$\theta_4$','θ':'$\\theta$','δᵢ':r'$\delta_i$','δmin,i':r'$\delta_{\min,i}$','φᵢ':r'$\varphi_i$','Aᵢ':'$A_i$'}
    for a,b in pairs.items():s=s.replace(a,b)
    return s
def source_table(root,index):
    with (Path(root)/'data'/f'observations-{index:02d}.csv').open(encoding='utf-8-sig',newline='') as f:r=list(csv.reader(f))
    return table([tex(s) for s in r[0]],[[tex(s) for s in row] for row in r[1:]])


def analyze(experiment_dir):
    cfg=json.loads((Path(experiment_dir)/'experiment.json').read_text(encoding='utf-8'))
    rows=read_rows(experiment_dir,1)
    angles=np.array([[angle(c) for c in row[1:5]] for row in rows])
    left=np.array([separation(a,c) for a,b,c,d in angles]);right=np.array([separation(b,d) for a,b,c,d in angles])
    values=(left+right)/2
    mean,ua=mean_a(values);ub=cfg['parameters']['angle_error_bound_arcmin']/60/math.sqrt(3);uc=math.hypot(ua,ub)
    metrics={'angle_mean_deg':metric(mean,'deg','出射角均值'),'angle_type_a_arcmin':metric(ua*60,'arcmin','角度均值A类分量'),'angle_type_b_arcmin':metric(ub*60,'arcmin','指定误差限B类分量'),'angle_combined_arcmin':metric(uc*60,'arcmin','两分量合成标准不确定度')}
    tables={f'table{i}':source_table(experiment_dir,i) for i in [1]}
    tables['table2']=table(['次数','左游标角差 / °','右游标角差 / °','出射角 / °'],[[int(row[0]),round(float(l),8),round(float(rr),8),round(float(v),8)] for row,l,rr,v in zip(rows,left,right,values)])
    n1=cfg['parameters']['prism_refractive_index'];u1=cfg['parameters']['prism_standard_uncertainty'];phi=math.radians(mean)
    n=math.sqrt(n1*n1-math.sin(phi)**2)
    un=math.hypot(n1/n*u1,math.sin(phi)*math.cos(phi)/n*uc*math.pi/180)
    metrics.update({'liquid_refractive_index':metric(n,'1','透明液体折射率'),'liquid_standard_uncertainty':metric(un,'1','指定分量传播不确定度')})
    return {'metrics':metrics,'tables':tables,'series':{'angle-repeat':{'x':list(range(1,len(rows)+1)),'y':values.tolist(),'x_label':'测量次数','y_label':'出射角 / °','label':'双游标结果'}},'notes':['圆周最短角差处理跨零读数。', '误差限1角分按最终角度估计的均匀分布限值采用；未含全部校准系统分量。']}
