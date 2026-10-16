"""Independent driven-torsion ODE, complex solve, energy and free-peak reference."""
from pathlib import Path
import argparse,csv,hashlib,json,platform,shutil,subprocess
import numpy as np
import scipy
from scipy.integrate import solve_ivp

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(repo_root,output_root,model):
    exp=repo_root/'experiments/course-02/pohl-resonance';cfg=json.loads((exp/'experiment.json').read_text(encoding='utf8'));tables=[]
    for i in range(1,4):
        with (exp/f'data/observations-{i:02d}.csv').open(encoding='utf-8-sig')as f:tables.append(np.array(list(csv.reader(f))[1:],float))
    free=tables[0].reshape(-1,2);d=tables[1];amp=np.r_[d[:,1],d[:,4]];period=np.r_[d[:,2],d[:,5]];t=np.r_[0,np.cumsum(period[:-1])];beta=-np.polyfit(t,np.log(np.radians(amp)),1)[0]
    obs={'schema_version':1,'experiment':cfg['id'],'source_files':[{'path':z.relative_to(repo_root).as_posix(),'sha256':sha(z)}for z in[exp/'experiment.json',exp/'data/provenance.json',*[exp/f'data/observations-{i:02d}.csv'for i in range(1,4)]]],'free':[{'amplitude_deg':float(a),'period':float(b)}for a,b in free],'decay':[{'time':float(a),'amplitude_deg':float(b),'period':float(c)}for a,b,c in zip(t,amp,period)],'forced':[{'period':float(row[0]),'amplitude_deg':float(row[1]),'phase_deg':float(row[2]),'reference_period':float(ref)}for row,ref in zip(tables[2],cfg['parameters']['forced_reference_periods_s'])],'decay_beta':float(beta),'free_period_min':float(free[:,1].min()),'free_period_max':float(free[:,1].max()),'forced_peak_deg':float(tables[2][:,1].max()),'identity':'source large-amplitude records; no small-angle material calibration inferred'}
    cases=[{'period':T,'beta':b,'forcing':a,'ratio':r,'initialAngle':np.radians(2)}for T in[1.5,1.8]for b in[.05,.12,.4]for a in[.005,.02]for r in[.8,1,1.2]]
    js=f"import{{motion,response,decayPeaks,fitDecay,measurement}}from {json.dumps(model.resolve().as_uri())};const c={json.dumps(cases)};console.log(JSON.stringify(c.map(p=>{{const times=Array.from({{length:121}},(_,i)=>i*8/p.beta/120),peaks=decayPeaks(p);return{{times,response:response(p),peaks,beta:fitDecay(peaks.map(q=>measurement(p,'decay',q)),p,'ideal-model').beta,forced:times.map(t=>motion(p,t)),free:times.map(t=>motion(p,t,'free'))}}}})));"
    vals=json.loads(subprocess.check_output([shutil.which('node')or r'C:\Program Files\nodejs\node.exe','--input-type=module','-e',js],text=True));checks=[];fail=[]
    for p,q in zip(cases,vals):
        w0=2*np.pi/p['period'];w=w0*p['ratio'];matrix=np.array([[w0*w0-w*w,-2*p['beta']*w],[2*p['beta']*w,w0*w0-w*w]]);re,im=np.linalg.solve(matrix,[p['forcing'],0]);complex_error=max(abs(np.hypot(re,im)-q['response']['amplitude']),abs(np.arctan2(im,re)-q['response']['phase']));state_error=0;energy_error=0
        for mode in['free','forced']:
            def rhs(t,y):
                force=p['forcing']*np.cos(w*t)if mode=='forced'else 0
                return[y[1],force-2*p['beta']*y[1]-w0*w0*y[0],force*y[1],2*p['beta']*y[1]*y[1]]
            sol=solve_ivp(rhs,[0,q['times'][-1]],[p['initialAngle'],0,0,0],t_eval=q['times'],method='DOP853',rtol=2e-11,atol=1e-13);ref=np.array([[r['theta'],r['velocity']]for r in q[mode]]).T;state_error=max(state_error,float(np.max(np.abs(ref-sol.y[:2]))));energy=.5*(sol.y[1]**2+w0*w0*sol.y[0]**2);balance=energy-energy[0]-sol.y[2]+sol.y[3];energy_error=max(energy_error,float(np.max(np.abs(balance))))
        decay_error=abs(p['beta']-q['beta']);checks.append({'parameters':p,'max_state_absolute_error':state_error,'complex_response_error':float(complex_error),'energy_balance_error':energy_error,'decay_beta_error':float(decay_error)})
        if max(state_error,complex_error,energy_error,decay_error)>1e-8:fail.append(checks[-1])
    report={'schema_version':1,'experiment':cfg['id'],'model_sha256':sha(model),'validator_sha256':sha(Path(__file__)),'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},'method':'DOP853 angle/velocity plus independent input-work and dissipated-energy states; complex two-real-equation response; exact free extrema logarithmic slope','case_count':len(cases),'tolerances':{'absolute':1e-8},'max_state_absolute_error':max(c['max_state_absolute_error']for c in checks),'max_energy_balance_error':max(c['energy_balance_error']for c in checks),'status':'passed'if not fail else'failed','failures':fail,'cases':checks}
    for path,data in[(output_root/'simulations/pohl-resonance/observations.json',obs),(output_root/'docs/simulation/pohl-resonance-reference.json',report)]:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:report[k]for k in['status','case_count','max_state_absolute_error','max_energy_balance_error']}))
    if fail:raise SystemExit(1)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--output-root',type=Path);ap.add_argument('--model',type=Path);a=ap.parse_args();run(a.repo_root,a.output_root or a.repo_root,a.model or a.repo_root/'simulations/pohl-resonance/model.mjs')
