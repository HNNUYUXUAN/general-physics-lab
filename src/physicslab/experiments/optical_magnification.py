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
    rows=[read_rows(experiment_dir,i) for i in range(1,5)];q=[np.array([[float(c) for c in row] for row in t]) for t in rows]
    microscope=q[0][:,2]/q[0][:,1];telescope=q[1][:,1]/q[1][:,2];calibration=q[2][:,1]/q[2][:,2];k,uk=mean_a(calibration);width=q[3][:,1];s,us=mean_a(width);diameters=k*width;d,udrepeat=mean_a(diameters);ud=math.hypot(s*uk,k*us)
    mm,um=mean_a(microscope);mt,ut=mean_a(telescope)
    metrics={'microscope_magnification':metric(mm,'1','显微镜投影放大率'),'microscope_type_a':metric(um,'1','显微镜放大率均值A类'),'telescope_magnification':metric(mt,'1','望远镜放大率绝对值'),'telescope_type_a':metric(ut,'1','望远镜放大率均值A类'),'eyepiece_scale_mm':metric(k,'mm/div','测微目镜每格值'),'eyepiece_scale_type_a_mm':metric(uk,'mm/div','每格值均值A类'),'wire_diameter_um':metric(d*1000,'um','细丝直径均值'),'wire_repeat_type_a_um':metric(udrepeat*1000,'um','固定标定下细丝均值A类'),'wire_random_combined_um':metric(ud*1000,'um','标定与宽度重复性传播分量')}
    tables={}
    for i,(raw,v,headers) in enumerate(zip(q[:3],[microscope,telescope,calibration],[['次数','$l_0$ / mm','$l$ / mm','$M_m$'],['次数','$l_1$ / mm','$l_2$ / mm','$|M_t|$'],['次数','$L$ / mm','$S$ / 格','$k$ / (mm/格)']]),1):tables['table'+str(i)]=table(headers,[[int(row[0]),row[1],row[2],round(float(value),8)] for row,value in zip(raw,v)])
    tables['table4']=table(['次数','宽度 $s$ / 格','直径 $d$ / mm'],[[int(row[0]),row[1],round(float(value),8)] for row,value in zip(q[3],diameters)])
    return {'metrics':metrics,'tables':tables,'series':{'wire-repeat':{'x':[1,2,3,4,5],'y':(diameters*1000).tolist(),'x_label':'测量次数','y_label':'细丝直径 $d$ / μm','label':'共用标定均值'}},'notes':['标定均值是所有细丝读数共享的乘法因子，其分量不能再次随细丝重复次数缩小。','未给标尺、投影距离和对焦系统误差；重复性不等于准确度。']}
