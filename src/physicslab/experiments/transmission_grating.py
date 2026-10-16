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
    raw=[read_rows(experiment_dir,i) for i in range(1,5)]
    phis=[];uas=[];disagreements=[];tables={}
    for j,rows in enumerate(raw,1):
        a=np.array([[angle(c) for c in row[1:5]] for row in rows]);l=np.array([separation(q[0],q[1]) for q in a]);rr=np.array([separation(q[2],q[3]) for q in a]);phi=(l+rr)/4
        mean,ua=mean_a(phi);phis.append(mean);uas.append(ua);disagreements.extend(abs(l-rr)*60)
        tables['table'+str(j)]=table(['次数','$V_1$',r'$V_1^{\prime}$','$V_2$',r'$V_2^{\prime}$',r'$\varphi_i$ / °'],[[int(row[0]),*[tex(c) for c in row[1:5]],round(float(v),8)] for row,v in zip(rows,phi)])
    rad=np.radians(phis);urad=np.radians(uas);d=546.1/math.sin(rad[1]);ud=abs(546.1*math.cos(rad[1])/math.sin(rad[1])**2*urad[1]);wave=d*np.sin(rad)
    uw=np.hypot(np.sin(rad)*ud,d*np.cos(rad)*urad);uw[1]=0
    names=['紫线','绿线（标定）','黄线1','黄线2'];metrics={'grating_spacing_nm':metric(d,'nm','光栅常数'),'grating_spacing_type_a_nm':metric(ud,'nm','标定角重复性传播分量'),'grating_lines_per_mm':metric(1e6/d,'1/mm','每毫米刻线数')}
    for key,name,v,u in zip(['violet','green','yellow_1','yellow_2'],names,wave,uw):metrics[key+'_wavelength_nm']=metric(v,'nm',name+'波长');metrics[key+'_type_a_nm']=metric(u,'nm',name+'指定重复性传播分量')
    delta=math.radians(phis[3]-phis[2]);metrics.update({'yellow_angle_gap_arcmin':metric((phis[3]-phis[2])*60,'arcmin','双黄线平均角间隔'),'dispersion_empirical_rad_per_nm':metric(delta/2.06,'rad/nm','指定波长差下实验色散'),'dispersion_theoretical_rad_per_nm':metric(1/(d*math.cos((rad[2]+rad[3])/2)),'rad/nm','光栅方程一级局部色散'),'maximum_vernier_gap_arcmin':metric(max(disagreements),'arcmin','两游标测得双侧角差最大不一致')})
    tables['table5']=table(['谱线','平均衍射角 / °','角度均值A类 / ′','波长 / nm','指定A类传播分量 / nm'],[[name,round(phi,8),round(u*60,5),round(float(w),5),round(float(ww),5)] for name,phi,u,w,ww in zip(names,phis,uas,wave,uw)])
    return {'metrics':metrics,'tables':tables,'series':{'grating-angles':{'x':[1,2,3,4],'y':phis,'x_label':'谱线序号（紫、绿、黄1、黄2）','y_label':r'平均衍射角 $\varphi$ / °','label':'一级衍射角'}},'notes':['绿线用作标定，计算回代标准值是恒等关系，不是独立波长验证。','缺标准波长、仪器分度和定位系统误差；传播只包含重复性分量。','部分两游标双侧角差明显不一致，数据保留但限制谱线识别和色散结论。']}
