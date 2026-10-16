"""Hydrostatic and pycnometric density with explicit uncertainty assumptions."""
from pathlib import Path
import json
import numpy as np


def analyze(experiment_dir):
    root = Path(experiment_dir)
    cfg = json.loads((root / 'experiment.json').read_text(encoding='utf-8'))
    solid = np.genfromtxt(root/'data/solid.csv', delimiter=',', names=True)
    liquid = np.genfromtxt(root/'data/liquid.csv', delimiter=',', names=True)
    vectors = [solid['air_mass_g'], solid['submerged_mass_g'], liquid['empty_mass_g'], liquid['water_total_mass_g'], liquid['brine_total_mass_g']]
    if any(len(x) != 3 or not np.isfinite(x).all() for x in vectors):
        raise ValueError('Expected three finite readings for each mass.')
    m, a, e, w, b = [float(np.mean(x)) for x in vectors]
    if not (m > a > 0 and b > e and w > e):
        raise ValueError('Nonphysical mass ordering.')
    rw = float(cfg['parameters']['water_density_g_cm3'])
    limit = float(cfg['parameters']['assumed_mass_error_limit_g'])
    ua = np.array([np.std(x, ddof=1)/np.sqrt(len(x)) for x in vectors])
    ub = limit / np.sqrt(3)
    uc = np.hypot(ua, ub)
    rho_s = rw*m/(m-a)
    rho_l = rw*(b-e)/(w-e)
    ds = np.array([-rw*a/(m-a)**2, rw*m/(m-a)**2])
    dl = np.array([rw*(b-w)/(w-e)**2, -rw*(b-e)/(w-e)**2, rw/(w-e)])
    us_a = float(np.linalg.norm(ds*ua[:2]))
    ul_a = float(np.linalg.norm(dl*ua[2:]))
    us = float(np.linalg.norm(ds*uc[:2]))
    ul = float(np.linalg.norm(dl*uc[2:]))
    metrics = {}
    def metric(k,v,unit,uncertainty=None):
        metrics[k]={'value':float(v),'unit':unit}
        if uncertainty is not None: metrics[k]['uncertainty']=float(uncertainty)
    for key,value in zip(['air_mass','submerged_mass','empty_mass','water_total_mass','brine_total_mass'],[m,a,e,w,b]): metric(key,value,'g')
    metric('solid_density',rho_s,'g/cm^3',us)
    metric('liquid_density',rho_l,'g/cm^3',ul)
    metric('solid_uncertainty_a',us_a,'g/cm^3')
    metric('liquid_uncertainty_a',ul_a,'g/cm^3')
    metric('solid_uncertainty_conditional',us,'g/cm^3')
    metric('liquid_uncertainty_conditional',ul,'g/cm^3')
    metric('solid_relative_uncertainty',100*us/rho_s,'%')
    metric('liquid_relative_uncertainty',100*ul/rho_l,'%')
    metric('solid_volume', (m-a)/rw,'cm^3')
    metric('bottle_volume',(w-e)/rw,'cm^3')
    tables={
        'solid_observations': {'headers':['测量次数','$m / \\mathrm{g}$','$m_{\\mathrm{s}} / \\mathrm{g}$'], 'rows':[[i+1,float(x),float(y)] for i,(x,y) in enumerate(zip(*vectors[:2]))]+[['平均值',m,a]]},
        'liquid_observations': {'headers':['测量次数','$m_0 / \\mathrm{g}$','$m_{\\mathrm{w}} / \\mathrm{g}$','$m_{\\mathrm{b}} / \\mathrm{g}$'], 'rows':[[i+1,*[float(x[i]) for x in vectors[2:]]] for i in range(3)]+[['平均值',e,w,b]]},
        'mass_uncertainty': {'headers':['质量','$u_A / \\mathrm{g}$','$u_B / \\mathrm{g}$','$u_c / \\mathrm{g}$'], 'rows':[[symbol,float(x),float(ub),float(y)] for symbol,x,y in zip(['$m$','$m_{\\mathrm{s}}$','$m_0$','$m_{\\mathrm{w}}$','$m_{\\mathrm{b}}$'],ua,uc)]},
        'density_results': {'headers':['对象','$\\rho / (\\mathrm{g\\,cm^{-3}})$','$u_A(\\rho) / (\\mathrm{g\\,cm^{-3}})$','$u_c(\\rho) / (\\mathrm{g\\,cm^{-3}})$'], 'rows':[['合金块',rho_s,us_a,us],['盐水',rho_l,ul_a,ul]]},
        'sensitivity': {'headers':['输入质量','$\\partial\\rho/\\partial m / \\mathrm{cm^{-3}}$','条件方差贡献占比 / %'], 'rows':[[name,float(d),float(100*(d*u)**2/total**2)] for names,derivs,ucs,total in [(['$m$','$m_{\\mathrm{s}}$'],ds,uc[:2],us),(['$m_0$','$m_{\\mathrm{w}}$','$m_{\\mathrm{b}}$'],dl,uc[2:],ul)] for name,d,u in zip(names,derivs,ucs)]}}
    shifts=np.linspace(-0.05,0.05,101)
    series={
        'solid_repeat': {'x':[1,2,3], 'y':[float(rw*x/(x-y)) for x,y in zip(*vectors[:2])], 'x_label':'测量次数', 'y_label':'合金密度 $\\rho_{\\mathrm{s}}$ / (g cm$^{-3}$)'},
        'liquid_repeat': {'x':[1,2,3], 'y':[float(rw*(bb-ee)/(ww-ee)) for ee,ww,bb in zip(*vectors[2:])], 'x_label':'测量次数', 'y_label':'盐水密度 $\\rho_{\\mathrm{b}}$ / (g cm$^{-3}$)'},
        'apparent_bias': {'x':shifts.tolist(), 'y':(rw*m/(m-(a+shifts))).tolist(), 'x_label':'视质量偏移 $\\delta m_{\\mathrm{s}}$ / g', 'y_label':'合金密度 $\\rho_{\\mathrm{s}}$ / (g cm$^{-3}$)'}}
    labels=['空气中质量','水中视质量','空瓶质量','瓶与水总质量','瓶与盐水总质量','合金密度','盐水密度','合金密度A类不确定度','盐水密度A类不确定度','合金密度条件标准不确定度','盐水密度条件标准不确定度','合金密度条件相对不确定度','盐水密度条件相对不确定度','合金体积','比重瓶容积']
    for entry,label in zip(metrics.values(),labels): entry['label']=label
    return {'metrics':metrics,'tables':tables,'series':series,'notes':['0.01 g 误差限来自读数位数推断，A+B 不确定度为条件结果。','忽略水密度的不确定度；各次称量均值的协方差按零处理，共享空瓶质量通过偏导直接传播。']}


def explore(key, result):
    """Slider scans a hypothetical bias; does not change the measured dataset."""
    import plotly.graph_objects as go
    if key != 'mass-bias': raise KeyError(key)
    m=result['metrics']['air_mass']['value']; a=result['metrics']['submerged_mass']['value']
    rw=result['metrics']['solid_density']['value']*(m-a)/m
    shifts=np.linspace(-.05,.05,101); densities=rw*m/(m-a-shifts)
    fig=go.Figure([go.Scatter(x=shifts,y=densities,mode='lines',line={'color':'black'},name='模型'),go.Scatter(x=[0],y=[rw*m/(m-a)],mode='markers',marker={'color':'black','size':11},name='选定偏移')])
    fig.update_layout(template='plotly_white',font={'family':'Times New Roman, SimSun','size':18},width=900,height=580,xaxis_title='视质量偏移 / g',yaxis_title='合金密度 / (g cm⁻³)',margin={'l':90,'r':35,'t':30,'b':150},showlegend=False,
        sliders=[{'active':50,'currentvalue':{'prefix':'视质量偏移 / g：'},'steps':[{'label':f'{d:.3f}','method':'restyle','args':[{'x':[[float(d)]],'y':[[float(v)]]},[1]]} for d,v in zip(shifts,densities)]}])
    fig.update_xaxes(showline=True,linecolor='black',zeroline=True,zerolinecolor='#aaaaaa')
    fig.update_yaxes(showline=True,linecolor='black',gridcolor='#e3e3e3')
    return fig
