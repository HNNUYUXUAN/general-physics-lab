"""Two ultrasonic wavelength datasets read from source DOCX table images."""
from pathlib import Path
import json
import numpy as np
def analyze(experiment_dir):
 root=Path(experiment_dir);cfg=json.loads((root/'experiment.json').read_text(encoding='utf-8'));p=cfg['parameters'];a=np.genfromtxt(root/'data/wavelengths.csv',delimiter=',',names=True);f=p['frequency_hz'];T=p['temperature_c']+273.15;uf=p['frequency_error_limit_hz']/np.sqrt(3);ub=p['wavelength_error_limit_mm']/np.sqrt(3)
 if len(a)!=10:raise ValueError('Expected ten wavelength pairs.')
 metrics={};results=[];unc=[]
 for i,(key,label) in enumerate([('standing','驻波法'),('phase','相位比较法')],1):
  lam=a[f'{key}_mm'];mean=float(lam.mean());sd=float(np.std(lam,ddof=1));ua=sd/np.sqrt(10);ul=np.hypot(ua,ub);v=mean*f/1000;uv=v*np.hypot(ul/mean,uf/f);gamma=p['air_molar_mass_kg_mol']*v*v/(p['gas_constant_j_molk']*T);ugamma=2*gamma*uv/v;err=100*abs(v-p['reference_speed_m_s'])/p['reference_speed_m_s'];errgamma=100*abs(gamma-p['reference_gamma'])/p['reference_gamma']
  for name,val,unit,desc in [('wavelength',mean,'mm','平均波长'),('sample_sd',sd,'mm','波长样本标准差'),('wavelength_uncertainty_a',ua,'mm','波长均值A类不确定度'),('wavelength_uncertainty',ul,'mm','波长条件标准不确定度'),('speed',v,'m/s','声速'),('speed_uncertainty',uv,'m/s','声速条件标准不确定度'),('relative_deviation',err,'%','声速相对参考差异'),('gamma',gamma,'1','空气比热容比'),('gamma_uncertainty',ugamma,'1','比热容比条件标准不确定度'),('gamma_deviation',errgamma,'%','比热容比相对理论差异')]:metrics[f'{key}_{name}']={'value':float(val),'unit':unit,'label':label+desc}
  metrics[f'{key}_speed']['uncertainty']=float(uv);metrics[f'{key}_gamma']['uncertainty']=float(ugamma)
  results.append([label,mean,v,p['reference_speed_m_s'],err,gamma,errgamma]);unc.append([label,sd,ua,ul,uv,ugamma])
 metrics['arithmetic_mean_speed']={'value':float(np.mean([row[2] for row in results])),'unit':'m/s','label':'两法声速算术平均（描述量）'}
 headers=['测量次数',*[str(i) for i in range(1,11)],'平均值 / mm']
 return {'metrics':metrics,'tables':{'standing':{'headers':headers,'rows':[['$\\lambda_1 / \\mathrm{mm}$',*a['standing_mm'].tolist(),float(a['standing_mm'].mean())]]},'phase':{'headers':headers,'rows':[['$\\lambda_2 / \\mathrm{mm}$',*a['phase_mm'].tolist(),float(a['phase_mm'].mean())]]},'results':{'headers':['方法','平均波长 / mm','声速 / (m s⁻¹)','参考声速 / (m s⁻¹)','声速差异 / %','比热容比','比热容比差异 / %'],'rows':results},'uncertainty':{'headers':['方法','波长样本标准差 / mm','波长均值A类 / mm','波长条件合成 / mm','声速标准不确定度 / (m s⁻¹)','比热容比标准不确定度'],'rows':unc}},'series':{'standing_sequence':{'x':list(range(1,11)),'y':a['standing_mm'].tolist(),'x_label':'测量序号','y_label':'驻波法波长 / mm'},'phase_sequence':{'x':list(range(1,11)),'y':a['phase_mm'].tolist(),'x_label':'测量序号','y_label':'相位比较法波长 / mm'}},'notes':['原始位移位置未给出，波长是原记录已转换的观察量。','波长B类限沿用源.005mm；频率B类限.5Hz，均匀分布。','gamma标准不确定度只传播声速，未计温度、摩尔质量和R。','两法共享频率与部分系统因素，算术平均不作独立加权合并估计。']}
def explore(key,result):
 import plotly.graph_objects as go
 if key!='length-scale':raise KeyError(key)
 scale=np.linspace(.98,1.02,101);v1=result['metrics']['standing_speed']['value'];v2=result['metrics']['phase_speed']['value']
 fig=go.Figure([go.Scatter(x=scale,y=v1*scale,mode='lines',line={'color':'black'},name='驻波法'),go.Scatter(x=scale,y=v2*scale,mode='lines',line={'color':'#626262','dash':'dash'},name='相位比较法'),go.Scatter(x=[1,1],y=[v1,v2],mode='markers',marker={'color':'black','size':10},name='选定标度')]);fig.update_layout(template='plotly_white',font={'family':'Times New Roman, SimSun','size':18},width=900,height=580,xaxis_title='假设波长标度因子',yaxis_title='声速 / (m s⁻¹)',margin={'l':90,'r':30,'t':25,'b':150},legend={'orientation':'h','y':1.05},sliders=[{'active':50,'currentvalue':{'prefix':'波长标度因子：'},'steps':[{'label':f'{s:.4f}','method':'restyle','args':[{'x':[[float(s),float(s)]],'y':[[float(v1*s),float(v2*s)]]},[2]]} for s in scale]}]);fig.update_xaxes(showline=True,linecolor='black',gridcolor='#e3e3e3');fig.update_yaxes(showline=True,linecolor='black',gridcolor='#e3e3e3');return fig
