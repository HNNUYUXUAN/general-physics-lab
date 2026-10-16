"""Independent complex acoustic round-trip series and position regression."""
from pathlib import Path
import argparse,hashlib,json,platform,shutil,subprocess
import numpy as np
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(repo_root,output_root,model):
    exp=repo_root/'experiments/course-02/sound-speed';a=np.genfromtxt(exp/'data/wavelengths.csv',delimiter=',',names=True);obs={'schema_version':1,'experiment':'course-02/sound-speed','source_files':[{'path':z.relative_to(repo_root).as_posix(),'sha256':sha(z)}for z in[exp/'experiment.json',exp/'data/wavelengths.csv',exp/'data/provenance.json']],'rows':[{'trial':int(r['trial']),'standing_mm':float(r['standing_mm']),'phase_mm':float(r['phase_mm'])}for r in a],'standing_speed_m_s':float(a['standing_mm'].mean()*36015/1000),'phase_speed_m_s':float(a['phase_mm'].mean()*36015/1000),'identity':'source already-converted wavelengths; raw positions absent'}
    cases=[{'frequency':f,'soundSpeed':c,'position':L,'roundTrip':r,'electronicPhase':phi,'positionScale':scale,'positionOffset':.0005,'temperature':26.5}for f in[34000,36015,40000]for c in[330,347.21,360]for L in[.05,.1,.15]for r in[.3,.9]for phi,scale in[(0,1),(1.,1.02)]]
    js=f"import{{transfer,sweep,fitRecords}}from {json.dumps(model.resolve().as_uri())};const cases={json.dumps(cases)};console.log(JSON.stringify(cases.map(p=>({{standing:transfer(p),phase:transfer(p,'phase'),fitStanding:fitRecords(sweep(p,'standing'),'standing','ideal-model'),fitPhase:fitRecords(sweep(p,'phase'),'phase','ideal-model')}}))));"
    vals=json.loads(subprocess.check_output([shutil.which('node')or r'C:\Program Files\nodejs\node.exe','--input-type=module','-e',js],text=True));checks=[];fail=[]
    for p,q in zip(cases,vals):
        k=2*np.pi*p['frequency']/p['soundSpeed'];n=np.arange(401);cavity=(1-p['roundTrip'])*np.sum(p['roundTrip']**n*np.exp(-1j*k*p['position']*(2*n+1)))*np.exp(1j*p['electronicPhase']);free=np.exp(-1j*k*p['position']+1j*p['electronicPhase']);errors=[abs(cavity-complex(q['standing']['real'],q['standing']['imag'])),abs(free-complex(q['phase']['real'],q['phase']['imag'])),abs(q['fitStanding']['speed']/(p['soundSpeed']*p['positionScale'])-1),abs(q['fitPhase']['speed']/(p['soundSpeed']*p['positionScale'])-1)];error=max(errors);checks.append({'parameters':p,'roundtrip_terms':401,'reference_cavity':[float(cavity.real),float(cavity.imag)],'max_scaled_error':float(error)})
        if error>1e-10:fail.append(p)
    report={'schema_version':1,'experiment':'course-02/sound-speed','model_sha256':sha(model),'validator_sha256':sha(Path(__file__)),'environment':{'python':platform.python_version(),'numpy':np.__version__},'method':'401 complex paths for round-trip cavity compared to closed form; free propagation phasor; independent expected position scale effect in both regressions','case_count':len(cases),'tolerances':{'scaled':1e-10},'max_scaled_error':max(c['max_scaled_error']for c in checks),'status':'passed'if not fail else'failed','failures':fail,'cases':checks}
    for path,data in[(output_root/'simulations/sound-speed/observations.json',obs),(output_root/'docs/simulation/sound-speed-reference.json',report)]:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:report[k]for k in['status','case_count','max_scaled_error']}))
    if fail:raise SystemExit(1)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--output-root',type=Path);ap.add_argument('--model',type=Path);a=ap.parse_args();run(a.repo_root,a.output_root or a.repo_root,a.model or a.repo_root/'simulations/sound-speed/model.mjs')
