"""Independent ODE gate arrivals and least-squares force inversion."""
from pathlib import Path
import argparse,hashlib,json,platform,shutil,subprocess
import numpy as np
from scipy.integrate import solve_ivp
import scipy
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(repo_root,output_root,model):
    exp=repo_root/'experiments/course-01/newton-second-law';cfg=json.loads((exp/'experiment.json').read_text(encoding='utf-8'));a=np.genfromtxt(exp/'data/observations.csv',delimiter=',',names=True,dtype=None,encoding='utf8');raw=[];groups=[]
    for group in range(1,6):
        vals=[];block=a[a['group']==group]
        for r in block:
            direct=r['mode']=='direct';v1=None if direct else float(r['v1_cm_s']);v2=None if direct else float(r['v2_cm_s']);acc=float(r['reported_acceleration_cm_s2'])if direct else(v2*v2-v1*v1)/(200*cfg['parameters']['gate_spacing_m']);vals.append(acc);raw.append({'group':group,'trial':int(r['trial']),'mode':str(r['mode']),'v1_cm_s':v1,'v2_cm_s':v2,'reported_acceleration_cm_s2':float(r['reported_acceleration_cm_s2']),'acceleration_cm_s2':acc})
        groups.append({'group':group,'hanging_mass_g':float(block['hanging_mass_g'][0]),'mean_acceleration_cm_s2':float(np.mean(vals)),'count':len(vals)})
    obs={'schema_version':1,'experiment':'course-01/newton-second-law','source_files':[{'path':p.relative_to(repo_root).as_posix(),'sha256':sha(p)}for p in[exp/'experiment.json',exp/'data/observations.csv',exp/'data/provenance.json']],'raw':raw,'groups':groups}
    cases=[{'totalMass':M,'hangingMass':m,'resistance':f,'gravity':9.8,'gateSpacing':S,'initialSpeed':u,'flagLength':d}for M in[.08,.18,.5]for m in[.005,.025]for f in[0.,.04]for S in[.2,.6]for u in[.2,.5]for d in[.001,.005]]
    js=f"import{{dynamics,gateReadings,sweep,fitRecords}}from {json.dumps(model.resolve().as_uri())};const cases={json.dumps(cases)};console.log(JSON.stringify(cases.map(p=>({{dynamics:dynamics(p),gates:gateReadings(p),fit:fitRecords(sweep(p),'ideal-dynamics')}}))));"
    vals=json.loads(subprocess.check_output([shutil.which('node')or r'C:\Program Files\nodejs\node.exe','--input-type=module','-e',js],text=True));checks=[];fail=[]
    for p,v in zip(cases,vals):
        M,m,f,g,S,u,d=[p[k]for k in['totalMass','hangingMass','resistance','gravity','gateSpacing','initialSpeed','flagLength']];acc=(m*g-f)/M
        def rhs(t,y):return[y[1],(m*g-f)/M]
        def arrival(t,y):return y[0]-S
        arrival.terminal=True;arrival.direction=1
        sol=solve_ivp(rhs,[0,20],[0,u],method='DOP853',events=arrival,rtol=5e-13,atol=2e-15,dense_output=True)
        t=float(sol.t_events[0][0]);speed=float(sol.y_events[0][0,1]);duration=[]
        for center in[0.,S]:
            speeds=[np.sqrt(u*u+2*acc*(center+shift))for shift in[-d/2,d/2]];duration.append(float((speeds[1]-speeds[0])/acc))
        expected_gate_a=((d/duration[1])**2-(d/duration[0])**2)/(2*S)
        release_distance=u*u/(2*acc);paper_bias=(np.sqrt((release_distance+S)**2-d*d/4)-np.sqrt(release_distance**2-d*d/4))/(2*S)-.5
        bias_error=abs((v['gates']['acceleration']/acc-1)-paper_bias)
        error=max(bias_error,abs(t-v['dynamics']['travelTime']),abs(speed-v['dynamics']['finalSpeed']),abs(duration[0]-v['gates']['time1']),abs(duration[1]-v['gates']['time2']),abs(expected_gate_a-v['gates']['acceleration']),abs(M-v['fit']['inferredMass']),abs(f-v['fit']['equivalentResistance']));checks.append({'parameters':p,'reference_arrival_s':t,'reference_final_speed_m_s':speed,'reference_gate_durations_s':duration,'paper_relative_bias':float(paper_bias),'paper_bias_error':float(bias_error),'max_absolute_error':error})
        if error>2e-10:fail.append(p)
    report={'schema_version':1,'experiment':'course-01/newton-second-law','model_sha256':sha(model),'validator_sha256':sha(Path(__file__)),'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},'method':'DOP853 dynamics with second-gate event; edge velocities give independent finite-width times; five-force least squares recovers inertial mass and resistance; Shao2025 p246 eq23 independent relative-bias check','case_count':len(cases),'tolerances':{'absolute':2e-10},'max_absolute_error':max(c['max_absolute_error']for c in checks),'status':'passed'if not fail else'failed','failures':fail,'cases':checks}
    for path,data in[(output_root/'simulations/newton-second-law/observations.json',obs),(output_root/'docs/simulation/newton-second-law-reference.json',report)]:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:report[k]for k in['status','case_count','max_absolute_error']}))
    if fail:raise SystemExit(1)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--output-root',type=Path);ap.add_argument('--model',type=Path);a=ap.parse_args();run(a.repo_root,a.output_root or a.repo_root,a.model or a.repo_root/'simulations/newton-second-law/model.mjs')
