"""Independent temperature and signed environmental-heat ODE integration."""
from pathlib import Path
import argparse,hashlib,json,platform,shutil,subprocess
import numpy as np
from scipy.integrate import solve_ivp
import scipy
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(repo_root,output_root,model):
    exp=repo_root/'experiments/course-01/mechanical-equivalent-heat';a=np.genfromtxt(exp/'data/temperatures.csv',delimiter=',',names=True);times=a['time_min']*60;T=a['temperature_k'];fit=lambda t,y:np.linalg.lstsq(np.column_stack([t,np.ones(len(t))]),y,rcond=None)[0][0];obs={'schema_version':1,'experiment':'course-01/mechanical-equivalent-heat','source_files':[{'path':z.relative_to(repo_root).as_posix(),'sha256':sha(z)}for z in[exp/'experiment.json',exp/'data/temperatures.csv',exp/'data/provenance.json']],'rows':[{'index':i+1,'time_min':float(t),'temperature_K':float(y)}for i,(t,y)in enumerate(zip(a['time_min'],T))],'slope_K_s':float(fit(times,T)),'early_slope_K_s':float(fit(times[:15],T[:15])),'late_slope_K_s':float(fit(times[15:],T[15:])),'latent_equivalent_independent_status':'not_computable_missing_measured_power_and_heat_capacity'}
    cases=[{'equivalent':4.1868,'heatCapacityCal':C,'voltage':U,'current':I,'heatTransfer':H,'ambientTemperature':Ta,'initialTemperature':Ti}for C in[100,300]for U in[5,20]for I in[.1,.5]for H in[0,.05,.1]for Ta in[285,305]for Ti in[285,305]]
    js=f"import{{state}}from {json.dumps(model.resolve().as_uri())};const cases={json.dumps(cases)};console.log(JSON.stringify(cases.map(p=>[true,false].map(heating=>({{heating,samples:[0,60,600,1800].map(t=>state(p,t,heating))}})))));"
    vals=json.loads(subprocess.check_output([shutil.which('node')or r'C:\Program Files\nodejs\node.exe','--input-type=module','-e',js],text=True));checks=[];fail=[]
    for p,phases in zip(cases,vals):
        for phase in phases:
            power=p['voltage']*p['current']if phase['heating']else 0;C=p['equivalent']*p['heatCapacityCal'];H=p['heatTransfer'];Ta=p['ambientTemperature'];rhs=lambda t,y:[(power-H*(y[0]-Ta))/C,H*(y[0]-Ta)];sol=solve_ivp(rhs,[0,1800],[p['initialTemperature'],0],t_eval=[0,60,600,1800],method='DOP853',rtol=5e-13,atol=2e-13);error=max(max(abs(sol.y[0,i]-q['temperature']),abs(sol.y[1,i]-q['heatExchange']))for i,q in enumerate(phase['samples']));checks.append({'parameters':p,'heating':phase['heating'],'max_absolute_error':error})
            if error>2e-8:fail.append({'parameters':p,'heating':phase['heating']})
    report={'schema_version':1,'experiment':'course-01/mechanical-equivalent-heat','model_sha256':sha(model),'validator_sha256':sha(Path(__file__)),'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},'method':'DOP853 integrates temperature and signed environmental heat as separate state variables; heating and independent power-off conditions','case_count':len(checks),'tolerances':{'absolute':2e-8},'max_absolute_error':max(c['max_absolute_error']for c in checks),'status':'passed'if not fail else'failed','failures':fail,'cases':checks}
    for path,data in[(output_root/'simulations/mechanical-equivalent-heat/observations.json',obs),(output_root/'docs/simulation/mechanical-equivalent-heat-reference.json',report)]:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:report[k]for k in['status','case_count','max_absolute_error']}))
    if fail:raise SystemExit(1)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--output-root',type=Path);ap.add_argument('--model',type=Path);a=ap.parse_args();run(a.repo_root,a.output_root or a.repo_root,a.model or a.repo_root/'simulations/mechanical-equivalent-heat/model.mjs')
