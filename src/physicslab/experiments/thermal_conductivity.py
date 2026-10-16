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
    pairs={'z_T':'$z_T$','θ₁':r'$\theta_1$','θ₂':r'$\theta_2$','θ₃':r'$\theta_3$','θ₄':r'$\theta_4$','θ':'$\\theta$','δᵢ':r'$\delta_i$','δmin,i':r'$\delta_{\min,i}$','φᵢ':r'$\varphi_i$','Aᵢ':'$A_i$'}
    for a,b in pairs.items():s=s.replace(a,b)
    return s
def source_table(root,index):
    with (Path(root)/'data'/f'observations-{index:02d}.csv').open(encoding='utf-8-sig',newline='') as f:r=list(csv.reader(f))
    return table([tex(s) for s in r[0]],[[tex(s) for s in row] for row in r[1:]])


def analyze(experiment_dir):
    rows=np.array([[float(v) for v in row] for row in read_rows(experiment_dir,2)]);time=rows[:,1];center=rows[:,2];heater=rows[:,3];difference=heater-center;area=.85*.09*.09;flux=18.02**2/(2*area*110);dt=difference/40;end_conductivity=flux*.010/(2*dt[-1]);mean_conductivity=flux*.010/(2*float(dt.mean()));x=time-time.mean();k=float(np.dot(x,center-center.mean())/np.dot(x,x));a=float(center.mean()-k*time.mean());res=center-(a+k*time);uk=math.sqrt(float(np.dot(res,res))/(len(time)-2)/float(np.dot(x,x)));rate=k/(40*60);ur=uk/(40*60);diff8=center[8:]-center[:8];rate_pair=float(np.mean(diff8))/(40*8*60);heat=flux/(1124*.010*rate);r2=1-float(np.dot(res,res)/np.dot(center-center.mean(),center-center.mean()))
    metrics={'effective_area_m2':metric(area,'m^2','修正面积'),'heat_flux_w_m2':metric(flux,'W/m^2','给定电阻下热流密度'),'temperature_difference_endpoint_k':metric(dt[-1],'K','末端两面温差'),'thermal_conductivity_endpoint':metric(end_conductivity,'W/(m K)','末端温差下导热系数'),'thermal_conductivity_mean_delta':metric(mean_conductivity,'W/(m K)','平均温差下导热系数'),'rise_rate_fit_k_s':metric(rate,'K/s','中心面拟合温升速率'),'rise_rate_residual_se_k_s':metric(ur,'K/s','残差温升速率标准误'),'rise_rate_difference_k_s':metric(rate_pair,'K/s','8分钟逐差温升速率'),'specific_heat_j_kg_k':metric(heat,'J/(kg K)','给定参数下比热容'),'center_slope_uv_min':metric(k,'uV/min','中心面热电势拟合斜率'),'center_intercept_uv':metric(a,'uV','中心面热电势拟合截距'),'center_fit_r_squared':metric(r2,'1','中心面拟合决定系数'),'delta_drift_percent':metric((difference[-1]-difference[0])/difference[0]*100,'%','两面热电势差相对增加')}
    tables={'table1':source_table(experiment_dir,1),'table2':table(['序号','时间 / min','中心面 / μV','加热面 / μV','两面差 / μV','每分钟中心增量 / μV','每8分钟中心增量 / μV'],[[int(row[0]),row[1],row[2],row[3],float(dd),float(center[i+1]-center[i]) if i<len(center)-1 else '—',float(diff8[i]) if i<8 else '—'] for i,(row,dd) in enumerate(zip(rows,difference))]),'table3':table(['物理量','结果','说明'],[['热流密度 / (W/m²)',flux,'电阻110Ω为近似输入'],['末端温差 / K',float(dt[-1]),'40μV/K换算'],['末端导热系数 / (W/(m·K))',end_conductivity,'温差尚缓慢漂移'],['逐差温升速率 / (K/s)',rate_pair,'8分钟隔距'],['拟合温升速率 / (K/s)',rate,'残差分量另列'],['比热容 / (J/(kg·K))',heat,'未含系统分量']])}
    return {'metrics':metrics,'tables':tables,'series':{'center-fit':{'x':time.tolist(),'y':center.tolist(),'x_label':'时间 $t$ / min','y_label':'中心面热电势 $V_c$ / μV','label':'主记录13..28min','fit':True},'heater-time':{'x':time.tolist(),'y':heater.tolist(),'x_label':'时间 $t$ / min','y_label':'加热面热电势 $V_h$ / μV','label':'主记录13..28min'},'thermal-difference':{'x':time.tolist(),'y':difference.tolist(),'x_label':'时间 $t$ / min','y_label':'两面热电势差 $V_h-V_c$ / μV','label':'差值重算'}},'notes':['仅使用主报告13..28min的16组微伏读数，未与照片中的其他时间序列拼接。','0.04mV/K=40μV/K；分钟斜率先除以60再转换K/s。','110Ω、密度、厚度与面积修正为给定近似参数，未确认实测电阻。','两面差在15分钟内增长约11.5%，并非严格准稳态；结果依赖选定端点。']}
