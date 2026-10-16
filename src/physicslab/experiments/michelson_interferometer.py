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
    rows=np.array([[float(c) for c in row] for row in read_rows(experiment_dir,1)]);shift=rows[:,3]-rows[:,2]
    if np.any(shift<=0) or np.any(rows[:,1]<=0):raise ValueError('Positive motion and fringe counts required')
    wavelength=2*shift/rows[:,1]*1e6;mean,ua=mean_a(wavelength)
    metrics={'wavelength_mean_nm':metric(mean,'nm','激光波长均值'),'wavelength_type_a_nm':metric(ua,'nm','波长均值A类分量'),'relative_reference_difference_percent':metric(abs(mean-632.8)/632.8*100,'%','相对指定632.8nm的差异')}
    return {'metrics':metrics,'tables':{'table1':table(['次数','条纹数 $N$','$d_1$ / mm','$d_2$ / mm',r'$\Delta d$ / mm'],[[int(row[0]),int(row[1]),row[2],row[3],round(float(v),8)] for row,v in zip(rows,shift)]),'table2':table(['次数',r'$\Delta d$ / mm',r'$\lambda$ / nm'],[[int(row[0]),round(float(v),8),round(float(w),6)] for row,v,w in zip(rows,shift,wavelength)])},'series':{'wavelength-repeat':{'x':rows[:,0].tolist(),'y':wavelength.tolist(),'x_label':'测量次数','y_label':r'激光波长 $\lambda$ / nm','label':'五次100条纹计数'}},'notes':['632.8nm是指定常用参考值，未附本激光器校准证书。','只有重复性A类分量，缺仪器与计数系统误差。']}
