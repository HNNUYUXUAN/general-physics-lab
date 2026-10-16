"""Compare analytic browser modes against an independent discrete eigenproblem."""
from pathlib import Path
import argparse, hashlib, json, platform, shutil, subprocess
import numpy as np
from scipy.linalg import eigh_tridiagonal
import scipy

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def run(repo_root,output_root,model):
    exp=repo_root/'experiments/course-02/string-vibration'
    cfg=json.loads((exp/'experiment.json').read_text(encoding='utf-8'));g=cfg['parameters']['gravity_m_s2'];series={}
    for name in ['tension','frequency']:
        a=np.genfromtxt(exp/f'data/{name}.csv',delimiter=',',names=True)
        series[name]=[{'mass_g':float(r['mass_g']) if name=='tension' else 100.,'frequency_hz':60. if name=='tension' else float(r['frequency_hz']),'length_cm':float(r['length_cm']),'half_waves':int(r['half_waves']),'wavelength_cm':float(2*r['length_cm']/r['half_waves']),'tension_N':float((r['mass_g'] if name=='tension' else 100)*g/1000),'source':'original-observation','conflict':name=='tension' and i==6} for i,r in enumerate(a)]
    cases=[]
    for L in [.2,1.191,2.]:
        for mass in [.02,.1,.3]:
            for mu in [.00005,.0002,.000570,.001]:
                for mode in [1,2,6]:cases.append(dict(length=L,mass=mass,linearDensity=mu,gravity=9.794,mode=mode))
    node=shutil.which('node') or r'C:\Program Files\nodejs\node.exe'
    js=f"import{{properties}}from {json.dumps(model.resolve().as_uri())};const cases={json.dumps(cases)};console.log(JSON.stringify(cases.map(properties)));"
    values=json.loads(subprocess.check_output([node,'--input-type=module','-e',js],text=True))
    comparisons=[];failures=[]
    for p,q in zip(cases,values):
        errors=[]
        for cells in [32,64,128,256]:
            dx=p['length']/cells;diag=np.full(cells-1,2/dx**2);off=np.full(cells-2,-1/dx**2)
            eigenvalue=eigh_tridiagonal(diag,off,select='i',select_range=(p['mode']-1,p['mode']-1),eigvals_only=True)[0]
            frequency=np.sqrt(p['mass']*p['gravity']/p['linearDensity']*eigenvalue)/(2*np.pi)
            errors.append(float(abs(frequency/q['frequency']-1)))
        ratios=[errors[i]/errors[i+1] for i in range(3)]
        if errors[-1]>.00023 or min(ratios)<3.9:failures.append(p)
        comparisons.append({'parameters':p,'analytic_frequency_hz':q['frequency'],'relative_errors':errors,'refinement_ratios':ratios})
    result={'schema_version':1,'experiment':'course-02/string-vibration','model_sha256':sha(model),'validator_sha256':sha(Path(__file__)),'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},'method':'eigh_tridiagonal on fixed-end second-order spatial Laplacian; 32/64/128/256 intervals','tolerances':{'max_finest_relative_frequency_error':.00023,'minimum_refinement_ratio':3.9},'case_count':len(cases),'max_finest_relative_frequency_error':max(c['relative_errors'][-1] for c in comparisons),'minimum_refinement_ratio':min(min(c['refinement_ratios']) for c in comparisons),'status':'passed' if not failures else 'failed','failures':failures,'cases':comparisons}
    sources=[exp/'experiment.json',exp/'data/tension.csv',exp/'data/frequency.csv',exp/'data/provenance.json']
    observed={'schema_version':1,'experiment':'course-02/string-vibration','source_files':[{'path':x.relative_to(repo_root).as_posix(),'sha256':sha(x)}for x in sources],'series':series,'notes':['原报告线密度缺失，网页教学输入不用于改写原始观测。','张力系列第7点L63.30cm,n1推得126.60cm；源报告派生166.60cm冲突保留。']}
    outputs=[(output_root/'docs/simulation/string-vibration-reference.json',result),(output_root/'simulations/string-vibration/observations.json',observed)]
    for path,data in outputs:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k]for k in ['status','case_count','max_finest_relative_frequency_error','minimum_refinement_ratio']},indent=2))
    if failures:raise SystemExit(1)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1]);parser.add_argument('--output-root',type=Path);parser.add_argument('--model',type=Path);args=parser.parse_args();run(args.repo_root,args.output_root or args.repo_root,args.model or args.repo_root/'simulations/string-vibration/model.mjs')
