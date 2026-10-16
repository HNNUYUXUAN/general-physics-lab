"""Radau integration of Stokes force balance and gate-position events."""
from pathlib import Path
import argparse,csv,hashlib,json,platform,re,shutil,subprocess
import numpy as np
from scipy.integrate import solve_ivp
import scipy
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(repo_root,output_root,model):
    exp=repo_root/'experiments/course-02/liquid-viscosity';cfg=json.loads((exp/'experiment.json').read_text(encoding='utf8'));p=cfg['parameters']
    def table(i):
        with (exp/f'data/observations-{i:02d}.csv').open(encoding='utf-8-sig',newline='')as f:return list(csv.reader(f))[1:]
    raw=table(3)[0][1:];times=[]
    for s in raw:
        n=[float(v)for v in re.findall(r'\d+(?:\.\d+)?',s)];times.append(n[0]if len(n)==1 else n[0]*60+n[1]+n[2]/100)
    diam=(np.mean([float(v)*10 for v in table(2)[0][1:]])-p['micrometer_zero_mm'])/1000;t=np.linalg.lstsq(np.column_stack([np.arange(1,7),np.ones(6)]),times,rcond=None)[0][0];wall=1+2.4*diam/p['tube_diameter_m'];eta=(p['sphere_density_kg_m3']-p['liquid_density_kg_m3'])*p['gravity_m_s2']*diam**2*t/(18*p['distance_m']*wall);obs={'schema_version':1,'experiment':'course-02/liquid-viscosity','source_files':[{'path':z.relative_to(repo_root).as_posix(),'sha256':sha(z)}for z in[exp/'experiment.json',exp/'data/observations-01.csv',exp/'data/observations-02.csv',exp/'data/observations-03.csv',exp/'data/provenance.json']],'rows':[{'index':i+1,'as_recorded':s,'cumulative_s':times[i],'increment_s':times[i]-(times[i-1]if i else 0)}for i,s in enumerate(raw)],'fall_time_fit_s':float(t),'corrected_diameter_m':float(diam),'viscosity_pa_s':float(eta),'reynolds':float(p['liquid_density_kg_m3']*p['distance_m']/t*diam/eta)}
    cases=[]
    for eta in[.2,.5,1.2]:
        for d in[.0005,.000990,.002]:
            for D in[.02,.04]:
                for distance in[.1,.3]:
                    speed=(7800-950)*9.8*d*d/(18*eta*(1+2.4*d/D));Re=950*speed*d/eta
                    if Re<=.1:cases.append({'viscosity':eta,'diameter':d,'tubeDiameter':D,'distance':distance,'entryDistance':.02,'sphereDensity':7800,'liquidDensity':950,'gravity':9.8})
    js=f"import{{properties,motion,fallInterval,timeAtDistance}}from {json.dumps(model.resolve().as_uri())};const cases={json.dumps(cases)};console.log(JSON.stringify(cases.map(p=>({{...properties(p),interval:fallInterval(p),arrival:timeAtDistance(p,p.entryDistance+p.distance),samples:[0,1,3,5].map(r=>motion(p,r*properties(p).tau))}}))));"
    vals=json.loads(subprocess.check_output([shutil.which('node')or r'C:\Program Files\nodejs\node.exe','--input-type=module','-e',js],text=True));checks=[];fail=[]
    for p,q in zip(cases,vals):
        d,eta,D=p['diameter'],p['viscosity'],p['tubeDiameter'];volume=np.pi*d**3/6;mass=7800*volume;buoyant_force=(7800-950)*volume*9.8;drag=3*np.pi*eta*d*(1+2.4*d/D)
        def rhs(t,y):return[y[1],(buoyant_force-drag*y[1])/mass]
        def gate1(t,y):return y[0]-p['entryDistance']
        def gate2(t,y):return y[0]-p['entryDistance']-p['distance']
        gate1.direction=gate2.direction=1;gate2.terminal=True
        sol=solve_ivp(rhs,[0,q['arrival']*1.1+1],[0,0],method='Radau',events=[gate1,gate2],dense_output=True,rtol=2e-11,atol=1e-14);interval=float(sol.t_events[1][0]-sol.t_events[0][0]);samples=sol.sol(np.array([0,1,3,5])*q['tau']);error=max(abs(interval-q['interval']),abs(float(sol.t_events[1][0])-q['arrival']),max(abs(samples[0,i]-v['position'])for i,v in enumerate(q['samples'])),max(abs(samples[1,i]-v['velocity'])for i,v in enumerate(q['samples'])));checks.append({'parameters':p,'reference_interval_s':interval,'max_absolute_error':error})
        if error>2e-8:fail.append(p)
    report={'schema_version':1,'experiment':'course-02/liquid-viscosity','model_sha256':sha(model),'validator_sha256':sha(Path(__file__)),'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},'method':'Radau integration of buoyancy-minus-linear-drag ODE with both measuring-mark events; compare transient positions/velocities','case_count':len(cases),'tolerances':{'absolute':2e-8},'max_absolute_error':max(c['max_absolute_error']for c in checks),'status':'passed'if not fail else'failed','failures':fail,'cases':checks}
    for path,data in[(output_root/'simulations/liquid-viscosity/observations.json',obs),(output_root/'docs/simulation/liquid-viscosity-reference.json',report)]:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:report[k]for k in['status','case_count','max_absolute_error']}))
    if fail:raise SystemExit(1)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--output-root',type=Path);ap.add_argument('--model',type=Path);a=ap.parse_args();run(a.repo_root,a.output_root or a.repo_root,a.model or a.repo_root/'simulations/liquid-viscosity/model.mjs')
