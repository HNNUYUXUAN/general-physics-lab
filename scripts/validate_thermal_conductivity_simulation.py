"""Independent Fourier-series solution and 20/40/80-cell convergence."""
from pathlib import Path
import argparse,csv,hashlib,json,platform,shutil,subprocess
import numpy as np
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(repo_root,output_root,model):
    exp=repo_root/'experiments/course-02/thermal-conductivity'
    with (exp/'data/observations-02.csv').open(encoding='utf-8-sig',newline='')as f:a=np.array([[float(v)for v in r]for r in list(csv.reader(f))[1:]])
    difference=a[:,3]-a[:,2];area=.85*.09*.09;q=18.02**2/(2*area*110);obs={'schema_version':1,'experiment':'course-02/thermal-conductivity','source_files':[{'path':z.relative_to(repo_root).as_posix(),'sha256':sha(z)}for z in[exp/'experiment.json',exp/'data/observations-01.csv',exp/'data/observations-02.csv',exp/'data/provenance.json']],'rows':[{'time_min':float(r[1]),'center_uV':float(r[2]),'heater_uV':float(r[3]),'difference_uV':float(d)}for r,d in zip(a,difference)],'conductivity_endpoint_W_mK':float(q*.01/(2*difference[-1]/40)),'conductivity_mean_W_mK':float(q*.01/(2*difference.mean()/40)),'difference_drift_percent':float((difference[-1]/difference[0]-1)*100)}
    cases=[{'conductivity':k,'specificHeat':c,'density':1124,'thickness':R,'voltage':18.02,'resistance':110,'area':area,'thermocouple':40,'initialTemperature':20}for k in[.1,.2,.4]for c in[1000,1500,2000]for R in[.005,.01,.015]]
    js=f"import{{properties,simulate}}from {json.dumps(model.resolve().as_uri())};const cases={json.dumps(cases)};console.log(JSON.stringify(cases.flatMap(p=>[.02,.1,.25].map(Fo=>{{const duration=Fo*p.thickness**2/properties(p).diffusivity;return{{parameters:p,Fo,time:duration,meshes:[20,40,80].map(cells=>({{cells,frame:simulate(p,{{cells,duration,outputStep:duration}}).frames.at(-1)}}))}}}}))));"
    values=json.loads(subprocess.check_output([shutil.which('node')or r'C:\Program Files\nodejs\node.exe','--input-type=module','-e',js],text=True));records=[];fail=[]
    for r in values:
        p=r['parameters'];Fo=r['Fo'];R=p['thickness'];k=p['conductivity'];q=p['voltage']**2/(2*p['area']*p['resistance']);rate=q/(p['density']*p['specificHeat']*R);mean=20+rate*r['time'];errs=[];energies=[]
        for mesh in r['meshes']:
            frame=mesh['frame'];x=np.array(frame['positions']);u=x/R;n=np.arange(1,201,dtype=float);series=np.sum(((-1)**n/n**2*np.exp(-n*n*np.pi*np.pi*Fo))[:,None]*np.cos(n[:,None]*np.pi*u[None,:]),axis=0);reference=mean+q*R/(2*k)*(u*u-1/3)-2*q*R/(k*np.pi*np.pi)*series;errs.append(float(np.max(abs(np.array(frame['temperatures'])-reference))/(q*R/k)));energies.append(abs(frame['mean']-mean))
        ratios=[errs[i]/errs[i+1]for i in range(2)];record={'parameters':p,'fourier_number':Fo,'time_s':r['time'],'scaled_profile_errors':errs,'refinement_ratios':ratios,'mean_energy_errors_K':energies};records.append(record)
        if errs[-1]>5e-5 or min(ratios)<3.7 or max(energies)>5e-8:fail.append(record)
    report={'schema_version':1,'experiment':'course-02/thermal-conductivity','model_sha256':sha(model),'validator_sha256':sha(Path(__file__)),'environment':{'python':platform.python_version(),'numpy':np.__version__},'method':'independent 200-term Neumann constant-flux Fourier series; 20/40/80 finite-volume CN cell-center profile convergence and mean-energy identity','case_count':len(records),'mesh_runs':len(records)*3,'tolerances':{'finest_profile_scaled':5e-5,'minimum_refinement_ratio':3.7,'mean_energy_absolute_K':5e-8},'max_finest_scaled_error':max(r['scaled_profile_errors'][-1]for r in records),'minimum_refinement_ratio':min(min(r['refinement_ratios'])for r in records),'max_mean_energy_error_K':max(max(r['mean_energy_errors_K'])for r in records),'status':'passed'if not fail else'failed','failures':fail,'cases':records}
    for path,data in[(output_root/'simulations/thermal-conductivity/observations.json',obs),(output_root/'docs/simulation/thermal-conductivity-reference.json',report)]:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:report[k]for k in['status','case_count','mesh_runs','max_finest_scaled_error','minimum_refinement_ratio','max_mean_energy_error_K']}))
    if fail:raise SystemExit(1)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--output-root',type=Path);ap.add_argument('--model',type=Path);a=ap.parse_args();run(a.repo_root,a.output_root or a.repo_root,a.model or a.repo_root/'simulations/thermal-conductivity/model.mjs')
