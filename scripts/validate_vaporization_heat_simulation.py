"""Independent energy residual root and raw weighing-inventory comparison."""
from pathlib import Path
import argparse,csv,hashlib,json,platform,shutil,subprocess
import numpy as np
from scipy.optimize import brentq
import scipy
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(repo_root,output_root,model):
    exp=repo_root/'experiments/course-01/vaporization-heat';cfg=json.loads((exp/'experiment.json').read_text(encoding='utf8'));p=cfg['parameters']
    with (exp/'data/observations.csv').open(encoding='utf-8-sig',newline='')as f:raw=list(csv.DictReader(f))
    v={r['quantity']:float(r['value'])for r in raw};mw=v['initial_total_mass']-v['inner_mass'];ms=v['final_total_mass']-v['initial_total_mass'];C=mw*p['water_specific_heat_j_gk']+v['inner_mass']*p['inner_specific_heat_j_gk']+v['stirrer_mass']*p['stirrer_specific_heat_j_gk'];T1=v['initial_voltage']-273.15;T2=v['final_voltage']-273.15;latent=lambda mass:(C*(T2-T1)/mass-p['water_specific_heat_j_gk']*(100-T2))*1000
    obs={'schema_version':1,'experiment':'course-01/vaporization-heat','source_files':[{'path':z.relative_to(repo_root).as_posix(),'sha256':sha(z)}for z in[exp/'experiment.json',exp/'data/observations.csv',exp/'data/provenance.json']],'rows':[{'quantity':r['quantity'],'value':float(r['value']),'unit':r['unit'],'note':r['note']}for r in raw],'latent_same_J_kg':latent(ms),'latent_extra_J_kg':latent(ms-v['stirrer_mass'])}
    cases=[]
    for L in[2e6,2.25e6,2.5e6]:
        for mw in[.08,.2]:
            for M in[.001,.0078,.015]:
                for T in[0.,30.]:
                    for z,q in[(0.,0.),(.1,.1)]:
                        p={'latentHeat':L,'waterMass':mw,'steamMass':M,'initialTemperature':T,'steamTemperature':100,'innerMass':.02952,'stirrerMass':.00384,'waterHeat':4180,'innerHeat':897,'stirrerHeat':390,'moistureFraction':z,'heatLossFraction':q};C=mw*4180+.02952*897+.00384*390;Tf=(C*T+M*((1-z-q)*L+4180*100))/(C+M*4180)
                        if Tf<99:cases.append(p)
    js=f"import{{properties,idealReadings,inferLatent}}from {json.dumps(model.resolve().as_uri())};const cases={json.dumps(cases)};console.log(JSON.stringify(cases.map(p=>({{...properties(p),inverse:inferLatent(p,idealReadings(p)),inverseExtra:inferLatent(p,idealReadings(p,true),true)}}))));"
    vals=json.loads(subprocess.check_output([shutil.which('node')or r'C:\Program Files\nodejs\node.exe','--input-type=module','-e',js],text=True));checks=[];fail=[]
    for p,q in zip(cases,vals):
        C=p['waterMass']*4180+p['innerMass']*897+p['stirrerMass']*390;M=p['steamMass'];L=p['latentHeat'];res=lambda Tf:C*(Tf-p['initialTemperature'])-M*((1-p['moistureFraction'])*L+4180*(100-Tf))+M*p['heatLossFraction']*L;Tf=brentq(res,-50,100,xtol=1e-12);expected=(1-p['moistureFraction']-p['heatLossFraction'])*L;error=max(abs(Tf-q['finalTemperature']),abs(res(q['finalTemperature']))/max(1,C),abs(q['inverse']['latentHeat']-expected)/max(1,expected),abs(q['inverseExtra']['latentHeat']-expected)/max(1,expected));checks.append({'parameters':p,'reference_final_temperature_C':Tf,'reference_apparent_latent_heat_J_kg':expected,'max_scaled_error':error})
        if error>1e-10:fail.append(p)
    report={'schema_version':1,'experiment':'course-01/vaporization-heat','model_sha256':sha(model),'validator_sha256':sha(Path(__file__)),'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},'method':'brentq energy residual root plus independent wet-steam/heat-loss apparent-heat identity; same/extra-stirrer matched inventory inversion','case_count':len(cases),'tolerances':{'scaled':1e-10},'max_scaled_error':max(c['max_scaled_error']for c in checks),'status':'passed'if not fail else'failed','failures':fail,'cases':checks}
    for path,data in[(output_root/'simulations/vaporization-heat/observations.json',obs),(output_root/'docs/simulation/vaporization-heat-reference.json',report)]:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:report[k]for k in['status','case_count','max_scaled_error']}))
    if fail:raise SystemExit(1)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--output-root',type=Path);ap.add_argument('--model',type=Path);a=ap.parse_args();run(a.repo_root,a.output_root or a.repo_root,a.model or a.repo_root/'simulations/vaporization-heat/model.mjs')
