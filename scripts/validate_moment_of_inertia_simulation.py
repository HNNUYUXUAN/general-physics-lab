"""Independent constrained-force solve and ODE half-turn event reference."""
from pathlib import Path
import argparse,hashlib,json,platform,shutil,subprocess
import numpy as np
import scipy
from scipy.integrate import solve_ivp,quad
from scipy.optimize import brentq

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(repo_root,output_root,model):
    exp=repo_root/'experiments/course-02/moment-of-inertia';cfg=json.loads((exp/'experiment.json').read_text(encoding='utf8'));reported=cfg['source_reported_inertia_kg_m2'];labels=['平台减速','平台加速','平台＋环减速','平台＋环加速','平台＋两柱减速','平台＋两柱加速']
    obs={'schema_version':1,'experiment':cfg['id'],'source_files':[{'path':z.relative_to(repo_root).as_posix(),'sha256':sha(z)}for z in[exp/'experiment.json',exp/'data/geometry.csv',exp/'data/provenance.json']],'beta_rows':[{'label':label,'values':a,'mean':float(np.mean(a))}for label,a in zip(labels,cfg['source_intermediates']['angular_accelerations_rad_s2'])],'ring_from_reported':reported['platform_ring']-reported['platform'],'ring_geometry':.5*.436*(.12**2+.105**2),'cylinder_from_reported':(reported['platform_two_cylinders']-reported['platform'])/2,'cylinder_geometry':.166*(.1**2+.5*.015**2),'identity':'source intermediate beta and reported total inertia; raw timestamps and hanging mass absent'}
    cases=[{'platformInertia':J,'ringMass':.436,'ringOuter':.12,'ringInner':.105,'cylinderMass':.166,'cylinderRadius':.015,'offset':d,'hangingMass':m,'towerRadius':r,'frictionTorque':tau,'initialOmega':w,'gravity':9.8}for J in[.003,.008]for d in[0,.1,.15]for m,r,tau,w in[(.02,.015,.0002,5),(.05,.025,.0005,7),(.1,.03,.001,10)]]
    js=f"import{{inertia,accelerations,gateTimes,estimateBeta,inferInertia}}from {json.dumps(model.resolve().as_uri())};const c={json.dumps(cases)};console.log(JSON.stringify(c.map(p=>['platform','ring','cylinders'].map(m=>{{const a=accelerations(p,m),f=gateTimes(p,m,'free'),d=gateTimes(p,m,'driven');return{{inertia:inertia(p,m),a,f,d,bf:estimateBeta(f).beta,bd:estimateBeta(d).beta,inverse:inferInertia(p,estimateBeta(f).beta,estimateBeta(d).beta)}}}}))));"
    values=json.loads(subprocess.check_output([shutil.which('node')or r'C:\Program Files\nodejs\node.exe','--input-type=module','-e',js],text=True));checks=[];fail=[]
    for p,result in zip(cases,values):
        ring=quad(lambda r:2*p['ringMass']*r**3/(p['ringOuter']**2-p['ringInner']**2),p['ringInner'],p['ringOuter'],epsabs=1e-14)[0]
        cylinder=quad(lambda r:2*p['cylinderMass']*r*(r*r+p['offset']**2)/p['cylinderRadius']**2,0,p['cylinderRadius'],epsabs=1e-14)[0]
        for mount,q in zip(['platform','ring','cylinders'],result):
            J=p['platformInertia']+(ring if mount=='ring'else 2*cylinder if mount=='cylinders'else 0);r=p['towerRadius'];m=p['hangingMass'];tau=p['frictionTorque'];drive=np.linalg.solve([[J,0,-r],[0,m,1],[-r,1,0]],[-tau,m*p['gravity'],0])[0];free=-tau/J;errors=[abs(J-q['inertia']['total']),abs(J-q['inverse']),abs(free-q['bf']),abs(drive-q['bd'])];time_error=0
            for beta,ts in[(free,q['f']),(drive,q['d'])]:
                def event(t,y):return y[0]-8*np.pi
                event.terminal=True;event.direction=1
                sol=solve_ivp(lambda t,y:[y[1],beta],[0,30],[0,p['initialOmega']],events=event,dense_output=True,method='DOP853',rtol=2e-12,atol=1e-13)
                end=sol.t_events[0][0];ref=[brentq(lambda t:sol.sol(t)[0]-(k+1)*np.pi,0,end+1e-11,xtol=1e-13)for k in range(8)];time_error=max(time_error,float(np.max(np.abs(np.array(ref)-ts))))
            error=max(errors);checks.append({'parameters':p,'mount':mount,'reference_inertia':J,'max_absolute_error':float(error),'max_gate_time_error_s':time_error})
            if error>1e-10 or time_error>1e-9:fail.append(checks[-1])
    report={'schema_version':1,'experiment':cfg['id'],'model_sha256':sha(model),'validator_sha256':sha(Path(__file__)),'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},'method':'radial mass quadrature; independent constrained 3x3 force/torque solve; DOP853 angular trajectory and half-turn root events; paired inversion','case_count':len(checks),'tolerances':{'absolute':1e-10,'gate_time_s':1e-9},'max_absolute_error':max(c['max_absolute_error']for c in checks),'max_gate_time_error_s':max(c['max_gate_time_error_s']for c in checks),'status':'passed'if not fail else'failed','failures':fail,'cases':checks}
    for path,data in[(output_root/'simulations/moment-of-inertia/observations.json',obs),(output_root/'docs/simulation/moment-of-inertia-reference.json',report)]:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:report[k]for k in['status','case_count','max_absolute_error','max_gate_time_error_s']}))
    if fail:raise SystemExit(1)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--output-root',type=Path);ap.add_argument('--model',type=Path);a=ap.parse_args();run(a.repo_root,a.output_root or a.repo_root,a.model or a.repo_root/'simulations/moment-of-inertia/model.mjs')
