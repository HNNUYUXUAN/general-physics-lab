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
    spectrum=np.array([[float(v) for v in row] for row in read_rows(experiment_dir,1)]);observations=read_rows(experiment_dir,2);visibility=np.array([float(row[3]) for row in observations]);first=spectrum[np.abs(spectrum[:,0])==1,1];position=float(np.mean(abs(first)));d=.0006328*150/position;frequency=1/d;x=spectrum[:,0];y=spectrum[:,1];slope=float(np.dot(x-x.mean(),y-y.mean())/np.dot(x-x.mean(),x-x.mean()));intercept=float(y.mean()-slope*x.mean());dfit=.0006328*150/slope
    return {'metrics':{'first_order_mean_abs_mm':metric(position,'mm','正负一级平均绝对位置'),'grating_period_mm':metric(d,'mm','一级位置光栅周期'),'spatial_frequency_per_mm':metric(frequency,'1/mm','基频'),'spectrum_slope_mm':metric(slope,'mm','全级次频谱位置拟合斜率'),'spectrum_intercept_mm':metric(intercept,'mm','频谱位置拟合截距'),'period_fit_mm':metric(dfit,'mm','全级次位置拟合光栅周期'),'visibility_zero_only':metric(visibility[1],'1','仅零级记录可见度'),'visibility_unfiltered':metric(visibility[0],'1','未滤波记录可见度')},'tables':{'table1':table(['衍射级次 $k$',r'频谱位置 $\xi$ / mm'],spectrum.tolist()),'table2':source_table(experiment_dir,2)},'series':{'spectrum-fit':{'x':x.tolist(),'y':y.tolist(),'x_label':'衍射级次 $k$','y_label':r'后焦面位置 $\xi$ / mm','label':'观测值','fit':True},'filter-visibility':{'x':[1,2,3,4,5],'y':visibility.tolist(),'x_label':'滤波方式序号（对应观察表）','y_label':'记录相对可见度','label':'源记录可见度'}},'notes':['可见度只有记录结果，未附最大最小光强，无法复核其计算。','没有频谱复振幅和光阑尺寸，不能从当前记录重建实际二维物像。','遮挡零级后的反相条纹为观测描述，不能仅由通过±1断言普遍反相。']}
