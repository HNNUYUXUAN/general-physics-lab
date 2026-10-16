"""Independent bar finite-element displacement and reflected-ray construction."""
from pathlib import Path
import argparse,hashlib,json,platform,shutil,subprocess
import numpy as np
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(repo_root,output_root,model):
    exp=repo_root/'experiments/course-02/young-modulus';cfg=json.loads((exp/'experiment.json').read_text(encoding='utf8'));p=cfg['parameters'];d=np.genfromtxt(exp/'data/diameters.csv',delimiter=',',names=True);load=np.genfromtxt(exp/'data/loading.csv',delimiter=',',names=True);diam=float(d['apparent_mm'].mean()-p['zero_offset_mm']);x=(load['loading_mm']+load['unloading_mm'])/2;mass=load['mass_kg'];fit=np.linalg.lstsq(np.column_stack([mass,np.ones(len(mass))]),x,rcond=None)[0];factor=8*p['gravity_m_s2']*(p['wire_length_mm']/1000)*(p['mirror_distance_mm']/1000)/(np.pi*(diam/1000)**2*(p['lever_constant_mm']/1000));delta=float(np.mean(x[5:]-x[:5]));obs={'schema_version':1,'experiment':'course-02/young-modulus','source_files':[{'path':z.relative_to(repo_root).as_posix(),'sha256':sha(z)}for z in[exp/'experiment.json',exp/'data/diameters.csv',exp/'data/loading.csv',exp/'data/provenance.json']],'diameter_readings_mm':d['apparent_mm'].tolist(),'corrected_mean_diameter_mm':diam,'loading':[{'index':i+1,'mass_kg':float(r['mass_kg']),'loading_mm':float(r['loading_mm']),'unloading_mm':float(r['unloading_mm']),'mean_mm':float(x[i])}for i,r in enumerate(load)],'young_difference_Pa':factor*5/(delta/1000),'young_regression_Pa':factor/(fit[0]/1000)}
    cases=[]
    for E in[1e11,2e11,2.5e11]:
        for m in[1.,5.,10.]:
            for diameter in[.0004,.00052,.0008]:
                for L,H,D in[(.5,.5,.03),(.72,.69,.03526),(1.,1.5,.05)]:
                    strain=m*9.8/(E*np.pi*diameter**2/4)
                    if strain<=.003 and strain*L/D<=.1:cases.append({'youngModulus':E,'wireLength':L,'wireDiameter':diameter,'mirrorDistance':H,'leverArm':D,'mass':m,'gravity':9.8,'scaleOrigin':.032,'trueZero':.000062,'assumedZero':.000062})
    js=f"import{{properties,inferYoung}}from {json.dumps(model.resolve().as_uri())};const cases={json.dumps(cases)};console.log(JSON.stringify(cases.map(p=>{{const q=properties(p);return{{...q,inverse:inferYoung(p,q.scaleShift,'geometric')}}}})));"
    vals=json.loads(subprocess.check_output([shutil.which('node')or r'C:\Program Files\nodejs\node.exe','--input-type=module','-e',js],text=True));checks=[];fail=[]
    for p,q in zip(cases,vals):
        E,L,d,H,D,m=[p[k]for k in['youngModulus','wireLength','wireDiameter','mirrorDistance','leverArm','mass']];N=8;stiff=E*np.pi*d*d/4/(L/N);K=np.zeros((N+1,N+1))
        for i in range(N):K[i:i+2,i:i+2]+=stiff*np.array([[1.,-1.],[-1.,1.]])
        force=np.zeros(N);force[-1]=m*9.8;u=np.linalg.solve(K[1:,1:],force);extension=u[-1];theta=np.arcsin(extension/D);normal=np.array([np.cos(theta),np.sin(theta)]);incident=np.array([-1.,0.]);reflected=incident-2*np.dot(incident,normal)*normal;shift=H*reflected[1]/reflected[0]
        error=max(abs(extension-q['extension'])/max(1e-12,abs(extension)),abs(shift-q['scaleShift'])/max(1e-12,abs(shift)),abs(q['inverse']/E-1));checks.append({'parameters':p,'bar_elements':N,'reference_extension_m':extension,'reference_scale_shift_m':shift,'max_relative_error':error})
        if error>1e-10:fail.append(p)
    report={'schema_version':1,'experiment':'course-02/young-modulus','model_sha256':sha(model),'validator_sha256':sha(Path(__file__)),'environment':{'python':platform.python_version(),'numpy':np.__version__},'method':'8-element axial bar stiffness solve plus vector reflection at rotated mirror; inverse geometric modulus check','case_count':len(cases),'tolerances':{'relative':1e-10},'max_relative_error':max(c['max_relative_error']for c in checks),'status':'passed'if not fail else'failed','failures':fail,'cases':checks}
    for path,data in[(output_root/'simulations/young-modulus/observations.json',obs),(output_root/'docs/simulation/young-modulus-reference.json',report)]:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:report[k]for k in['status','case_count','max_relative_error']}))
    if fail:raise SystemExit(1)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--output-root',type=Path);ap.add_argument('--model',type=Path);a=ap.parse_args();run(a.repo_root,a.output_root or a.repo_root,a.model or a.repo_root/'simulations/young-modulus/model.mjs')
