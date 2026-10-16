"""Independent impulse-equation linear solve for one-dimensional impacts."""
from pathlib import Path
import argparse,hashlib,json,platform,shutil,subprocess
import numpy as np
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(repo_root,output_root,model):
    exp=repo_root/'experiments/course-01/collisions';cfg=json.loads((exp/'experiment.json').read_text(encoding='utf-8'));m1=cfg['parameters']['mass1_g']/1000;m2=cfg['parameters']['mass2_g']/1000;a=np.genfromtxt(exp/'data/inelastic.csv',delimiter=',',names=True);b=np.genfromtxt(exp/'data/elastic.csv',delimiter=',',names=True)
    obs={'schema_version':1,'experiment':'course-01/collisions','source_files':[{'path':p.relative_to(repo_root).as_posix(),'sha256':sha(p)}for p in[exp/'experiment.json',exp/'data/inelastic.csv',exp/'data/elastic.csv',exp/'data/provenance.json']],'mass1_kg':m1,'mass2_kg':m2,'inelastic':[{'trial':int(r['trial']),'incident_cm_s':float(r['incident_cm_s']),'common_cm_s':float(r['common_cm_s']),'momentum_difference':float((m1+m2)*r['common_cm_s']/100-m1*r['incident_cm_s']/100),'energy_loss':float(.5*m1*(r['incident_cm_s']/100)**2-.5*(m1+m2)*(r['common_cm_s']/100)**2)}for r in a],'elastic':[{'trial':int(r['trial']),'v1_first_cm_s':float(r['v1_first_cm_s']),'v2_cm_s':float(r['v2_cm_s']),'v1_second_cm_s':float(r['v1_second_cm_s']),'velocity_ratio':float(2*r['v2_cm_s']/(r['v1_first_cm_s']+r['v1_second_cm_s']))}for r in b],'notes':['弹性组缺碰前速度，不进行该组动量能量独立验证。','原始观测未包含轻撞重；网页质量交换是独立教学情景。']}
    cases=[{'mass1':x,'mass2':y,'incident':u,'restitution':e,'flagLength':.02}for x in[.05,.34175,1.]for y in[.05,.15449,1.]for u in[.1,.7102,1.5]for e in[0.,.4,1.]]
    js=f"import{{solve,gateReadings,fromGate}}from {json.dumps(model.resolve().as_uri())};const cases={json.dumps(cases)};console.log(JSON.stringify(cases.map(p=>({{result:solve(p),gate:fromGate(p,gateReadings(p))}}))));"
    values=json.loads(subprocess.check_output([shutil.which('node')or r'C:\Program Files\nodejs\node.exe','--input-type=module','-e',js],text=True));records=[];fail=[]
    for p,v in zip(cases,values):
        m1,m2,u,e=p['mass1'],p['mass2'],p['incident'],p['restitution'];matrix=np.array([[m1,0.,1.],[0.,m2,-1.],[-1.,1.,0.]]);v1,v2,J=np.linalg.solve(matrix,[m1*u,0.,e*u]);ref_loss=.5*m1*m2/(m1+m2)*(1-e**2)*u**2
        error=max(abs(v['result']['v1']-v1),abs(v['result']['v2']-v2),abs(v['result']['energyLoss']-ref_loss),abs(v['result']['momentumDifference']),abs(v['gate']['v1']-v1),abs(v['gate']['v2']-v2));records.append({'parameters':p,'reference_v1':v1,'reference_v2':v2,'impulse_N_s':J,'max_absolute_error':error})
        if error>1e-12:fail.append(p)
    report={'schema_version':1,'experiment':'course-01/collisions','model_sha256':sha(model),'validator_sha256':sha(Path(__file__)),'environment':{'python':platform.python_version(),'numpy':np.__version__},'method':'independent 3×3 linear solve of two impulse equations and relative separation condition; reduced-mass energy loss identity; photogate roundtrip','case_count':len(cases),'tolerances':{'absolute':1e-12},'max_absolute_error':max(r['max_absolute_error']for r in records),'status':'passed'if not fail else'failed','failures':fail,'cases':records}
    for path,data in[(output_root/'simulations/collisions/observations.json',obs),(output_root/'docs/simulation/collisions-reference.json',report)]:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k]for k in['status','case_count','max_absolute_error']}))
    if fail:raise SystemExit(1)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--output-root',type=Path);ap.add_argument('--model',type=Path);a=ap.parse_args();run(a.repo_root,a.output_root or a.repo_root,a.model or a.repo_root/'simulations/collisions/model.mjs')
