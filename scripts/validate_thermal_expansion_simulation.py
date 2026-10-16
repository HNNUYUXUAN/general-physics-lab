"""Independent heating ODE and spatial strain integration."""
from pathlib import Path
import argparse,csv,hashlib,json,platform,shutil,subprocess
import numpy as np
from scipy.integrate import solve_ivp,quad
import scipy
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(repo_root,output_root,model):
    exp=repo_root/'experiments/course-02/thermal-expansion';cfg=json.loads((exp/'experiment.json').read_text(encoding='utf8'))
    with (exp/'data/observations-02.csv').open(encoding='utf-8-sig',newline='')as f:r=list(csv.reader(f))[1:]
    T=np.array([float(v)for v in r[0][1:]]);S=np.array([float(v)for v in r[1][1:]]);L=cfg['parameters']['nominal_length_mm']*1000;fit=np.linalg.lstsq(np.column_stack([T,np.ones(len(T))]),S,rcond=None)[0]
    obs={'schema_version':1,'experiment':'course-02/thermal-expansion','identity':'report-identical-to-lecture-example','source_files':[{'path':z.relative_to(repo_root).as_posix(),'sha256':sha(z)}for z in[exp/'experiment.json',exp/'data/observations-01.csv',exp/'data/observations-02.csv',exp/'data/provenance.json']],'rows':[{'index':i+1,'temperature_c':float(t),'dial_um':float(s)}for i,(t,s)in enumerate(zip(T,S))],'alpha_fit_per_k':float(fit[0]/L),'alpha_difference_per_k':float(np.mean((S[4:]-S[:4])/(L*(T[4:]-T[:4]))))}
    cases=[{'alpha':alpha,'length':length,'referenceTemperature':20,'targetTemperature':target,'timeConstant':tau,'temperatureBias':bias,'dialGain':gain,'dialOrigin':20e-6}for alpha in[5e-6,17.25e-6,30e-6]for length in[.1,.3]for target in[30,110]for tau in[5,60]for bias,gain in[(0,1),(2,1.05)]]
    js=f"import{{temperature,reading,sweep,fitRecords}}from {json.dumps(model.resolve().as_uri())};const cases={json.dumps(cases)};console.log(JSON.stringify(cases.map(p=>({{samples:[0,.5,1,3,5].map(r=>{{const T=temperature(p,r*p.timeConstant);return{{time:r*p.timeConstant,...reading(p,T)}}}}),fit:fitRecords(sweep(p),'ideal-equilibrium')}}))));"
    vals=json.loads(subprocess.check_output([shutil.which('node')or r'C:\Program Files\nodejs\node.exe','--input-type=module','-e',js],text=True));checks=[];fail=[]
    for p,q in zip(cases,vals):
        times=[v['time']for v in q['samples']];sol=solve_ivp(lambda t,y:[(p['targetTemperature']-y[0])/p['timeConstant']],[0,times[-1]],[20],method='DOP853',t_eval=times,rtol=5e-13,atol=2e-15);errors=[]
        for T,v in zip(sol.y[0],q['samples']):
            extension=quad(lambda x:p['alpha']*(T-20),0,p['length'],epsabs=1e-14)[0];errors.extend([abs(T-v['temperature']),abs(extension-v['extension'])])
        errors.append(abs(q['fit']['alpha']-p['alpha']*p['dialGain']));error=max(errors);checks.append({'parameters':p,'max_absolute_error':error})
        if error>2e-10:fail.append(p)
    report={'schema_version':1,'experiment':'course-02/thermal-expansion','model_sha256':sha(model),'validator_sha256':sha(Path(__file__)),'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},'method':'DOP853 lumped heating trajectory; independent spatial quadrature of thermal strain; linear algebra coefficient recovery','case_count':len(cases),'tolerances':{'absolute':2e-10},'max_absolute_error':max(c['max_absolute_error']for c in checks),'status':'passed'if not fail else'failed','failures':fail,'cases':checks}
    for path,data in[(output_root/'simulations/thermal-expansion/observations.json',obs),(output_root/'docs/simulation/thermal-expansion-reference.json',report)]:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:report[k]for k in['status','case_count','max_absolute_error']}))
    if fail:raise SystemExit(1)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--output-root',type=Path);ap.add_argument('--model',type=Path);a=ap.parse_args();run(a.repo_root,a.output_root or a.repo_root,a.model or a.repo_root/'simulations/thermal-expansion/model.mjs')
