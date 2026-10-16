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
    rows=read_rows(experiment_dir,1);a=np.array([[angle(v) for v in row[1:5]] for row in rows]);left=np.array([separation(q[0],q[2]) for q in a]);right=np.array([separation(q[1],q[3]) for q in a]);phi=(left+right)/2;mean,ua=mean_a(phi);concentration=mean/(66.46*2);uc=ua/(66.46*2)
    return {'metrics':{'rotation_magnitude_deg':metric(mean,'deg','旋光角绝对值均值'),'rotation_type_a_arcmin':metric(ua*60,'arcmin','旋光角均值A类'),'conditional_concentration_g_ml':metric(concentration,'g/mL','指定蔗糖比旋光率及管长下浓度'),'concentration_type_a_g_ml':metric(uc,'g/mL','只传播旋光角重复性分量'),'maximum_vernier_disagreement_arcmin':metric(max(abs(left-right))*60,'arcmin','双游标旋光角最大不一致')},'tables':{'table1':source_table(experiment_dir,1),'table2':table(['次数','左游标角差 / °','右游标角差 / °','旋光角绝对值 / °'],[[int(row[0]),round(float(l),8),round(float(rr),8),round(float(p),8)] for row,l,rr,p in zip(rows,left,right,phi)])},'series':{'rotation-repeat':{'x':[1,2,3,4,5],'y':phi.tolist(),'x_label':'测量次数','y_label':r'旋光角绝对值 $|\varphi|$ / °','label':'双游标平均'}},'notes':['液柱长度2.00dm由源作者按常用样品管取值，不是独立实测记录。','温度、溶液身份、比旋光率和管长误差未记录，浓度是给定假设下的反推。','角差取绝对值，不能由此独立判定旋光方向。']}
