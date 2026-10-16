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


def parse_time(text):
    numbers=[float(v) for v in re.findall(r'\d+(?:\.\d+)?',text)]
    return numbers[0] if len(numbers)==1 else numbers[0]*60+numbers[1]+numbers[2]/100
def analyze(experiment_dir):
    original=read_rows(experiment_dir,2)[0][1:];apparent=np.array([float(v)*10 for v in original]);diameters=apparent-.005;d=float(diameters.mean())*.001;ud=.005*.001/math.sqrt(3);raw_times=read_rows(experiment_dir,3)[0][1:];times=np.array([parse_time(v) for v in raw_times]);i=np.arange(1,7);x=i-i.mean();t=float(np.dot(x,times-times.mean())/np.dot(x,x));b=float(times.mean()-t*i.mean());res=times-(t*i+b);ua=math.sqrt(float(np.dot(res,res))/4/float(np.dot(x,x)));ub=.01/math.sqrt(3);ut=math.hypot(ua,ub);pair=(times[3:]-times[:3])/3;single=np.diff(np.r_[0,times]);wall=1+2.4*d/.020;eta=(7800-950)*9.8*d*d*t/(18*.200*wall);relative=math.hypot((2*.020+2.4*d)/(.020+2.4*d)*ud/d,ut/t);ueta=eta*relative;v=.200/t;reynolds=950*v*d/eta
    metrics={'diameter_corrected_mm':metric(d*1000,'mm','正零差修正直径均值'),'diameter_type_b_mm':metric(ud*1000,'mm','给定示值误差限B类分量'),'fall_time_fit_s':metric(t,'s','累计时间斜率'),'fall_time_pair_s':metric(float(pair.mean()),'s','三间隔逐差平均时间'),'time_fit_residual_se_s':metric(ua,'s','斜率残差标准误'),'time_specified_combined_s':metric(ut,'s','残差与指定秒表限值合成'),'time_intercept_s':metric(b,'s','累计时间拟合截距'),'terminal_speed_m_s':metric(v,'m/s','测量区间平均速度'),'wall_factor':metric(wall,'1','管壁修正因子'),'viscosity_pa_s':metric(eta,'Pa s','有限管径修正黏度'),'specified_viscosity_uncertainty_pa_s':metric(ueta,'Pa s','仅直径和时间指定分量传播'),'reynolds_number':metric(reynolds,'1','按当前估计计算的雷诺数')}
    tables={'table1':source_table(experiment_dir,1),'table2':table(['测量次数',1,2,3,4,5,6],[['原始读数 / cm',*original],['直径视值 / mm',*apparent.tolist()],['修正直径 / mm',*diameters.tolist()]]),'table3':table(['测量次数',1,2,3,4,5,6],[['原始累计读数',*raw_times],['累计时间 / s',*times.tolist()],['单次差 / s',*np.round(single,8).tolist()]]),'table4':table(['i',1,2,3],[['三间隔累计差 / s',*np.round(times[3:]-times[:3],8).tolist()],['单次平均 / s',*np.round(pair,8).tolist()]])}
    return {'metrics':metrics,'tables':tables,'series':{'cumulative-fit':{'x':i.tolist(),'y':times.tolist(),'x_label':'小球序号 $i$','y_label':'累计时间 $T_i$ / s','label':'主报告计时组','fit':True},'single-time':{'x':i.tolist(),'y':single.tolist(),'x_label':'小球序号 $i$','y_label':'相邻累计时间差 / s','label':'主报告累计时间差分'}},'notes':['只使用主报告31.28..189.60s累计计时，照片另外两组不拼接。','六个直径相同只使记录A类分量为零，不代表实际小球完全一致。','传播只含给定直径和时间分量，密度、温度、长度和壁修正模型误差未给。','连续计时拟合以累计值代表同一测量区间的累计下落耗时为前提，未另附投放空档记录。']}
