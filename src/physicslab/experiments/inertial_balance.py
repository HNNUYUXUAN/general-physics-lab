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
    raw=read_rows(experiment_dir,1);m=np.array([float(v) for v in raw[0][1:9]])*.001;period=np.array([float(v) for v in raw[1][1:9]]);tx=float(raw[1][9]);sq=period**2;x=m-m.mean();A=float(np.dot(x,sq-sq.mean())/np.dot(x,x));B=float(sq.mean()-A*m.mean());res=sq-(A*m+B);variance=float(np.dot(res,res))/6;va=variance/float(np.dot(x,x));vb=variance*(1/8+float(m.mean())**2/float(np.dot(x,x)));cov=-float(m.mean())*va;ua=math.sqrt(va);mx=(tx*tx-B)/A;k=4*math.pi**2/A;m0=B/A;uk=k*ua/A;umx=math.sqrt((mx*mx*va+vb+2*mx*cov)/(A*A));um0=math.sqrt((m0*m0*va+vb-2*m0*cov)/(A*A));pair=(sq[4:]-sq[:4])/(m[4:]-m[:4]);r2=1-float(np.dot(res,res)/np.dot(sq-sq.mean(),sq-sq.mean()))
    metrics={'slope_s2_kg':metric(A,'s^2/kg','定标斜率'),'slope_residual_se_s2_kg':metric(ua,'s^2/kg','残差斜率标准误'),'intercept_s2':metric(B,'s^2','定标截距'),'difference_slope_s2_kg':metric(float(pair.mean()),'s^2/kg','逐差平均斜率'),'calibration_r_squared':metric(r2,'1','定标决定系数'),'unknown_mass_g':metric(mx*1000,'g','圆柱体反推惯性质量'),'unknown_calibration_component_g':metric(umx*1000,'g','仅定标参数协方差传播分量'),'relative_nominal_difference_percent':metric(abs(mx*1000-190.5)/190.5*100,'%','相对标称190.5g差异'),'effective_stiffness_n_m':metric(k,'N/m','等效劲度系数'),'stiffness_residual_component_n_m':metric(uk,'N/m','斜率残差传播劲度分量'),'empty_effective_mass_g':metric(m0*1000,'g','空载等效质量'),'empty_mass_covariance_component_g':metric(um0*1000,'g','定标协方差空载质量分量')}
    rows=[['样品',*(['标准质量片']*8),'圆柱体'],['质量 / g',*(m*1000).tolist(),'190.5（标称，不定标）'],['周期 / s',*period.tolist(),tx],['周期平方 / s²',*sq.tolist(),tx*tx],['隔四组平方差 / s²',*np.round(sq[4:]-sq[:4],9).tolist(),*(['—']*5)],['隔四组质量差 / g',100,100,100,100,*(['—']*5)]]
    return {'metrics':metrics,'tables':{'table1':table(['次数',1,2,3,4,5,6,7,8,9],rows)},'series':{'balance-calibration':{'x':m.tolist(),'y':sq.tolist(),'x_label':'标准附加质量 $m$ / kg','y_label':'周期平方 $T^2$ / s$^2$','label':'仅前8组标准质量','fit':True}},'notes':['圆柱体190.5g只作为标称比较值，不进入定标。','周期平方由未修约周期重新计算，不用源表已修约平方求拟合。','斜率截距协方差在质量传播中保留，未含圆柱体周期和标准质量误差。']}
