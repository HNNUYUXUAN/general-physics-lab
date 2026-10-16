"""Independent mass-spring ODE and retarded acoustic-phase difference."""
from pathlib import Path
import argparse,hashlib,json,platform,shutil,subprocess
import numpy as np
from scipy.integrate import solve_ivp
import scipy
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(repo_root,output_root,model):
    exp=repo_root/'experiments/course-01/doppler-application';a=np.genfromtxt(exp/'data/static.csv',delimiter=',',names=True,dtype=None,encoding='utf8');b=np.genfromtxt(exp/'data/periods.csv',delimiter=',',names=True);T=float(b['period_s'].mean());obs={'schema_version':1,'experiment':'course-01/doppler-application','source_files':[{'path':z.relative_to(repo_root).as_posix(),'sha256':sha(z)}for z in[exp/'experiment.json',exp/'data/static.csv',exp/'data/periods.csv',exp/'data/provenance.json']],'static':[{'trial':int(r['trial']),'mass_g':float(r['mass_g']),'position_cm':float(r['position_cm']),'included':bool(r['included_in_source_mean']),'stiffness':float(r['mass_g']*.001*9.8/((r['position_cm']-24.9)/100))}for r in a],'periods_s':b['period_s'].tolist(),'mean_period_s':T,'dynamic_stiffness':4*np.pi**2*.1032/T**2}
    cases=[]
    for k in[3.,5.2,8.]:
        for M in[.05,.1032,.2]:
            for ms in[0.,.05]:
                for A in[.01,.05]:cases.append({'stiffness':k,'mass':M,'springMass':ms,'amplitude':A,'carrier':20000 if len(cases)%2 else 60000,'soundSpeed':330 if len(cases)%2 else 350,'addedMass':.05,'baselinePosition':.249,'staticOffset':0,'gravity':9.8})
    js=f"import{{properties,motion}}from {json.dumps(model.resolve().as_uri())};const cases={json.dumps(cases)};console.log(JSON.stringify(cases.map(p=>{{const q=properties(p);return{{...q,samples:Array.from({{length:33}},(_,i)=>{{const t=q.period*(.01+1.98*i/32);return{{time:t,...motion(p,t)}}}})}}}})));"
    values=json.loads(subprocess.check_output([shutil.which('node')or r'C:\Program Files\nodejs\node.exe','--input-type=module','-e',js],text=True));checks=[];fail=[]
    for p,q in zip(cases,values):
        mass=p['mass']+p['springMass']/3;rhs=lambda t,y:[y[1],-p['stiffness']/mass*y[0]]
        def event(t,y):return y[1]
        event.direction=-1
        sol=solve_ivp(rhs,[0,3.1*q['period']],[p['amplitude'],0],method='DOP853',events=event,rtol=2e-12,atol=2e-14,dense_output=True);period=float(np.mean(np.diff(sol.t_events[0])));position_error=velocity_error=frequency_error=0.
        for v in q['samples']:
            t=v['time'];x,vel=sol.sol(t);position_error=max(position_error,abs(x-v['position']));velocity_error=max(velocity_error,abs(vel-v['velocity']));h=1e-5*q['period'];phase=lambda s:2*np.pi*p['carrier']*(s-(.5-float(sol.sol(s)[0]))/p['soundSpeed']);frequency=(phase(t+h)-phase(t-h))/(2*h)/(2*np.pi);frequency_error=max(frequency_error,abs(frequency-v['frequency']))
        r={'parameters':p,'reference_period_s':period,'period_error_s':abs(period-q['period']),'max_position_error_m':position_error,'max_velocity_error_m_s':velocity_error,'max_acoustic_frequency_error_Hz':frequency_error};checks.append(r)
        if r['period_error_s']>1e-9 or position_error>1e-10 or velocity_error>1e-9 or frequency_error>5e-5:fail.append(r)
    report={'schema_version':1,'experiment':'course-01/doppler-application','model_sha256':sha(model),'validator_sha256':sha(Path(__file__)),'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},'method':'DOP853 mass-spring trajectory and same-direction velocity-zero events; finite difference of retarded phase from moving receiver distance','case_count':len(checks),'tolerances':{'period_s':1e-9,'position_m':1e-10,'velocity_m_s':1e-9,'frequency_Hz':5e-5},'max_period_error_s':max(r['period_error_s']for r in checks),'max_frequency_error_Hz':max(r['max_acoustic_frequency_error_Hz']for r in checks),'status':'passed'if not fail else'failed','failures':fail,'cases':checks}
    for path,data in[(output_root/'simulations/doppler-application/observations.json',obs),(output_root/'docs/simulation/doppler-application-reference.json',report)]:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:report[k]for k in['status','case_count','max_period_error_s','max_frequency_error_Hz']}))
    if fail:raise SystemExit(1)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--output-root',type=Path);ap.add_argument('--model',type=Path);a=ap.parse_args();run(a.repo_root,a.output_root or a.repo_root,a.model or a.repo_root/'simulations/doppler-application/model.mjs')
