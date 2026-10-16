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
    rows=read_rows(experiment_dir,2);t=np.array([float(v) for v in rows[0][1:]]);s=np.array([float(v) for v in rows[1][1:]]);L=150000.;x=t-t.mean();k=float(np.dot(x,s-s.mean())/np.dot(x,x));a=float(s.mean()-k*t.mean());e=s-(a+k*t);uk=math.sqrt(float(np.dot(e,e))/6/float(np.dot(x,x)));dif=s[4:]-s[:4];alpha_pair=dif/(L*(t[4:]-t[:4]));alpha=k/L;u=uk/L;r2=1-float(np.dot(e,e)/np.dot(s-s.mean(),s-s.mean()));reference=17.25e-6
    metrics={'alpha_difference_per_k':metric(float(alpha_pair.mean()),'1/K','逐差平均线胀系数'),'alpha_fit_per_k':metric(alpha,'1/K','最小二乘线胀系数'),'alpha_fit_residual_se_per_k':metric(u,'1/K','拟合残差传播分量'),'slope_um_per_k':metric(k,'μm/K','温度读数拟合斜率'),'slope_standard_error_um_per_k':metric(uk,'μm/K','残差斜率标准误'),'intercept_um':metric(a,'um','拟合截距'),'fit_r_squared':metric(r2,'1','拟合决定系数'),'reference_difference_percent':metric(abs(alpha-reference)/reference*100,'%','相对指定参考中值偏差')}
    tables={'table1':source_table(experiment_dir,1),'table2':source_table(experiment_dir,2),'table3':table(['配对',r'$t_i$ / °C',r'$t_{i+4}$ / °C',r'$S_i$ / μm',r'$S_{i+4}$ / μm',r'$\Delta S_i$ / μm',r'$\alpha_i$ / K$^{-1}$'],[[f'{i+1}–{i+5}',t[i],t[i+4],s[i],s[i+4],round(float(dif[i]),8),float(alpha_pair[i])] for i in range(4)]),'table4':table(['序号','温度 $t$ / °C','读数 $S$ / μm',r'$t^2$ / °C$^2$',r'$tS$ / (°C·μm)'],[[i+1,float(tt),float(ss),float(tt*tt),float(tt*ss)] for i,(tt,ss) in enumerate(zip(t,s))]+[['合计',float(sum(t)),float(sum(s)),float(sum(t*t)),float(np.dot(t,s))]]),'table5':table(['项目','计算结果'],[['斜率 / (μm/K)',k],['残差斜率标准误 / (μm/K)',uk],['线胀系数 / K⁻¹',alpha],['仅残差传播分量 / K⁻¹',u],['相对残差分量 / %',u/alpha*100]])}
    return {'metrics':metrics,'tables':tables,'series':{'expansion-fit':{'x':t.tolist(),'y':s.tolist(),'x_label':r'温度 $t / {}^\circ\mathrm{C}$','y_label':r'千分表读数 $S / \mu\mathrm{m}$','residual_unit':r'$\mu\mathrm{m}$','label':'报告与讲义相同的示例数据','fit':True}},'notes':['八组读数与配套讲义B示例完全一致，不能认定为独立新增观测。','150mm是标称长度；拟合标准误未包含有效长度、温度与千分表系统误差。']}
