"""Independent force-equilibrium inversion and finite-difference sensitivities."""
from pathlib import Path
import argparse,hashlib,json,platform,shutil,subprocess
import numpy as np
from scipy.optimize import root
import scipy
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(repo_root,output_root,model):
    exp=repo_root/'experiments/course-01/density';cfg=json.loads((exp/'experiment.json').read_text(encoding='utf-8'));rw=cfg['parameters']['water_density_g_cm3'];s=np.genfromtxt(exp/'data/solid.csv',delimiter=',',names=True);l=np.genfromtxt(exp/'data/liquid.csv',delimiter=',',names=True)
    groups=[('air',s['air_mass_g']),('submerged',s['submerged_mass_g']),('empty',l['empty_mass_g']),('water',l['water_total_mass_g']),('liquid',l['brine_total_mass_g'])];means={k:float(np.mean(v)) for k,v in groups}
    observed={'schema_version':1,'experiment':'course-01/density','source_files':[{'path':p.relative_to(repo_root).as_posix(),'sha256':sha(p)}for p in [exp/'experiment.json',exp/'data/solid.csv',exp/'data/liquid.csv',exp/'data/provenance.json']],'water_density_g_cm3':rw,'temperature_c':cfg['parameters']['temperature_c'],'mass_groups':[{'object':k,'readings':v.tolist(),'mean':means[k]}for k,v in groups],'derived':{'solid_density':rw*means['air']/(means['air']-means['submerged']),'liquid_density':rw*(means['liquid']-means['empty'])/(means['water']-means['empty'])},'notes':['0.01 g记录位数不代表已核实天平准确度。','忽略空气浮力、吊丝排水和温度漂移；水密度采用原报告值。']}
    cases=[]
    for rho in [1.1,7.9,12.]:
        for volume in [1.,5.67,20.]:
            for water in [.99,.99779,1.005]:
                mass=rho*volume;apparent=mass-water*volume;cases.append({'kind':'solid','inputs':[mass,apparent,water],'truth':[rho,volume]})
    for rho in [.5,1.08,1.5]:
        for volume in [5.,16.,50.]:
            for tare in [5.,31.63,100.]:cases.append({'kind':'liquid','inputs':[tare,tare+.99779*volume,tare+rho*volume,.99779],'truth':[rho,volume]})
    js=f"import{{inferSolid,inferLiquid,sensitivitySolid,sensitivityLiquid}}from {json.dumps(model.resolve().as_uri())};const cases={json.dumps(cases)};console.log(JSON.stringify(cases.map(c=>({{result:(c.kind==='solid'?inferSolid:inferLiquid)(...c.inputs),sensitivity:(c.kind==='solid'?sensitivitySolid:sensitivityLiquid)(...c.inputs)}}))));"
    browser=json.loads(subprocess.check_output([shutil.which('node')or r'C:\Program Files\nodejs\node.exe','--input-type=module','-e',js],text=True));checks=[];failures=[]
    for c,b in zip(cases,browser):
        if c['kind']=='solid':
            m,a,w=c['inputs'];solution=root(lambda z:[z[0]*z[1]-m,(z[0]-w)*z[1]-a],[3.,5.],tol=1e-11)
            if not solution.success and np.linalg.norm(solution.fun)>1e-8:raise RuntimeError('independent inverse failed')
            reference=solution.x
            def density(x):
                m,a,w=x;return np.linalg.solve(np.array([[1.,0.],[1.,-w]]),[m,a])[0]/np.linalg.solve(np.array([[1.,0.],[1.,-w]]),[m,a])[1]
            names=['air','submerged','waterDensity']
        else:
            e,w,bm,rw2=c['inputs'];reference=np.array([np.linalg.solve(np.array([[rw2]]),[w-e])[0],bm-e]);reference=np.array([reference[1]/reference[0],reference[0]])
            def density(x):
                e,w,bm,rw2=x;v=np.linalg.solve(np.array([[rw2]]),[w-e])[0];return(bm-e)/v
            names=['empty','water','liquid','waterDensity']
        errors=[]
        for i,name in enumerate(names):
            x=np.array(c['inputs']);h=1e-5*max(1.,abs(x[i]));plus=x.copy();minus=x.copy();plus[i]+=h;minus[i]-=h;num=(density(plus)-density(minus))/(2*h);errors.append(abs(num-b['sensitivity'][name])/max(1.,abs(num)))
        rel=max(abs(np.array([b['result']['density'],b['result']['volume']])-reference)/np.maximum(1.,abs(reference)));der=max(errors)
        if rel>1e-9 or der>5e-7:failures.append(c)
        checks.append({'kind':c['kind'],'inputs':c['inputs'],'reference_density_volume':reference.tolist(),'max_inverse_relative_error':float(rel),'max_derivative_scaled_error':float(der)})
    report={'schema_version':1,'experiment':'course-01/density','model_sha256':sha(model),'validator_sha256':sha(Path(__file__)),'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},'method':'solid: solve force-equilibrium nonlinear equations; liquid: independent volume linear solve; derivatives: symmetric finite differences','tolerances':{'inverse_relative':1e-9,'derivative_scaled':5e-7},'case_count':len(cases),'status':'passed' if not failures else 'failed','failures':failures,'cases':checks}
    for path,data in [(output_root/'simulations/density/observations.json',observed),(output_root/'docs/simulation/density-reference.json',report)]:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':report['status'],'case_count':len(cases),'max_inverse_relative_error':max(c['max_inverse_relative_error']for c in checks),'max_derivative_scaled_error':max(c['max_derivative_scaled_error']for c in checks)}))
    if failures:raise SystemExit(1)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--output-root',type=Path);ap.add_argument('--model',type=Path);a=ap.parse_args();run(a.repo_root,a.output_root or a.repo_root,a.model or a.repo_root/'simulations/density/model.mjs')
