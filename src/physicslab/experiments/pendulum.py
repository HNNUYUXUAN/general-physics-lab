"""Measured-data analysis and undamped nonlinear pendulum model.

Source observations, regression uncertainty, and model scenarios remain distinct.
"""
from pathlib import Path
import csv
import platform
import numpy as np
import scipy
from scipy.integrate import solve_ivp
from scipy.special import ellipk
from physicslab.common.io import read_json, input_hashes, sha256

def load_data(experiment):
    experiment=Path(experiment); config=read_json(experiment/'experiment.json')
    def rows(name):
        with (experiment/'data'/name).open(encoding='utf-8-sig',newline='') as f:
            return list(csv.DictReader(f))
    times=rows('measurements.csv'); diameters=rows('diameters.csv')
    if len(times)!=config['expected_runs']*config['repeats_per_run'] or len(diameters)!=config['diameter_repeats']:
        raise ValueError('Unexpected observation count')
    keys=[(r['run_id'],r['repeat_id']) for r in times]
    if len(set(keys))!=len(keys): raise ValueError('Duplicate timing observation identifier')
    if len({r['repeat_id'] for r in diameters})!=len(diameters): raise ValueError('Duplicate diameter identifier')
    values=[]
    for r in times:
        values.extend([float(r['string_length_cm']),float(r['elapsed_time_s'])])
        if int(r['oscillations'])!=config['oscillations']: raise ValueError('Oscillation count mismatch')
    values.extend(float(r['diameter_cm']) for r in diameters)
    if not np.all(np.isfinite(values)) or np.any(np.array(values)<=0): raise ValueError('Measurements must be finite and positive')
    ids=sorted({int(r['run_id']) for r in times})
    if ids!=list(range(1,config['expected_runs']+1)): raise ValueError('Unexpected run identifiers')
    for run in ids:
        group=[r for r in times if int(r['run_id'])==run]
        if len(group)!=config['repeats_per_run'] or len({r['string_length_cm'] for r in group})!=1:
            raise ValueError('Inconsistent repeats or length within a run')
        if sorted(int(r['repeat_id']) for r in group)!=list(range(1,config['repeats_per_run']+1)):
            raise ValueError('Unexpected repeat identifiers')
    return config,times,diameters

def fit_line(x,y):
    x=np.asarray(x,dtype=float); y=np.asarray(y,dtype=float)
    if x.shape!=y.shape or x.ndim!=1 or len(x)<3 or not np.all(np.isfinite([x,y])):
        raise ValueError('Fit requires at least three finite pairs')
    dx=x-x.mean(); sxx=dx@dx
    if sxx<=0: raise ValueError('Fit requires different lengths')
    slope=(dx@(y-y.mean()))/sxx
    intercept=y.mean()-slope*x.mean(); residuals=y-(slope*x+intercept)
    sse=residuals@residuals; se=np.sqrt(sse/(len(x)-2)/sxx)
    total=(y-y.mean())@(y-y.mean())
    return {'slope':float(slope),'intercept':float(intercept),'slope_se':float(se),
            'r_squared':float(1-sse/total) if total>0 else 1.0,'residuals':residuals.tolist()}

def period_exact(angle_rad,length,gravity):
    if not (0<=abs(angle_rad)<np.pi and length>0 and gravity>0): raise ValueError('Libration requires |angle| < pi, positive length and gravity')
    # scipy and Wolfram both use the parameter m=k^2 for the complete elliptic integral.
    return float(4*np.sqrt(length/gravity)*ellipk(np.sin(angle_rad/2)**2))

def simulate(config,gravity,angle_deg=None):
    cfg=config['simulation']; length=cfg['length_m']; angle=cfg['initial_angle_deg'] if angle_deg is None else angle_deg
    theta0=np.deg2rad(angle); omega0=cfg['initial_angular_velocity_rad_s']
    if not 0<abs(theta0)<np.pi or length<=0 or gravity<=0: raise ValueError('Invalid model parameters')
    if omega0!=0: raise ValueError('The period comparison assumes release from rest')
    def rhs(t,y): return [y[1],-gravity/length*np.sin(y[0])]
    def crossing(t,y): return y[0]
    crossing.direction=-np.sign(theta0); crossing.terminal=False
    time=np.linspace(0,cfg['duration_s'],cfg['samples'])
    solution=solve_ivp(rhs,[0,time[-1]],[theta0,omega0],t_eval=time,events=crossing,
                       method='DOP853',rtol=cfg['relative_tolerance'],atol=cfg['absolute_tolerance'],max_step=0.04)
    if not solution.success or not len(solution.t_events[0]): raise RuntimeError('Pendulum integration failed')
    theta,omega=solution.y
    energy=0.5*length**2*omega**2+gravity*length*(1-np.cos(theta))
    linear=theta0*np.cos(np.sqrt(gravity/length)*time)
    return {'time_s':time.tolist(),'angle_rad':theta.tolist(),'angular_velocity_rad_s':omega.tolist(),
            'linear_angle_rad':linear.tolist(),'period_ode_s':float(4*solution.t_events[0][0]),
            'period_exact_s':period_exact(theta0,length,gravity),
            'relative_energy_drift':float(np.max(np.abs(energy-energy[0]))/energy[0])}

def analyze(experiment):
    experiment=Path(experiment); config,times,diameters=load_data(experiment)
    d=np.array([float(r['diameter_cm'])/100 for r in diameters]); dm=float(d.mean()); du=float(d.std(ddof=1)/np.sqrt(len(d)))
    processed=[]
    for run in range(1,config['expected_runs']+1):
        records=sorted((r for r in times if int(r['run_id'])==run),key=lambda r:int(r['repeat_id']))
        t=np.array([float(r['elapsed_time_s']) for r in records]); length=float(records[0]['string_length_cm'])/100
        mean=float(t.mean()); u=float(t.std(ddof=1)/np.sqrt(len(t))); period=mean/config['oscillations']; pu=u/config['oscillations']
        effective=length+dm/2
        processed.append({'run_id':run,'string_length_m':length,'effective_length_m':effective,
          'mean_time_s':mean,'time_mean_u_a_s':u,'period_s':period,'period_u_a_s':pu,
          'period_squared_s2':period**2,'period_squared_u_a_s2':2*period*pu,
          'gravity_individual_m_s2':4*np.pi**2*effective/period**2})
    fit=fit_line([r['effective_length_m'] for r in processed],[r['period_squared_s2'] for r in processed])
    if fit['slope']<=0: raise ValueError('Fitted slope must be positive')
    g=float(4*np.pi**2/fit['slope']); gu=g*fit['slope_se']/fit['slope']
    def metric(value,unit): return {'value':float(value),'unit':unit}
    metrics={
      'diameter_mean':metric(dm,'m'),'diameter_mean_u_a':metric(du,'m'),
      'slope':metric(fit['slope'],'s^2/m'),'intercept':metric(fit['intercept'],'s^2'),
      'slope_standard_error':metric(fit['slope_se'],'s^2/m'),
      'gravity_fit':metric(g,'m/s^2'),'gravity_regression_standard_error':metric(gu,'m/s^2'),
      'gravity_individual_mean':metric(np.mean([r['gravity_individual_m_s2'] for r in processed]),'m/s^2'),
      'r_squared':metric(fit['r_squared'],'1'),
      'reference_relative_difference_pct':metric(100*(g/config['reference_gravity_m_s2']-1),'%')}
    length=config['simulation']['length_m']; t0=2*np.pi*np.sqrt(length/g)
    scan=[]
    for angle in config['simulation']['scan_angles_deg']:
        exact=period_exact(np.deg2rad(angle),length,g)
        scan.append({'angle_deg':angle,'period_s':exact,'linear_period_s':float(t0),
                     'period_excess_pct':float(100*(exact/t0-1)), 'gravity_bias_pct':float(100*((t0/exact)**2-1))})
    return {'schema_version':1,'experiment_id':config['experiment_id'],'engine':'python',
      'input_hashes':input_hashes(experiment),'code_hash':sha256(__file__),
      'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},
      'uncertainty_scope':config['analysis']['uncertainty_scope'],'model_parameters':config['simulation'],
      'metrics':metrics,'processed':processed,'residuals_s2':fit['residuals'],
      'simulation':simulate(config,g),'amplitude_scan':scan}
