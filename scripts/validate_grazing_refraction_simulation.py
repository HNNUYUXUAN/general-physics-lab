"""Independent two-interface grazing Snell root calculations."""
import argparse,csv,hashlib,json,math,platform,re,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
import scipy
from scipy.optimize import brentq
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1]);parser.add_argument('--output-root',type=Path);parser.add_argument('--model',type=Path);a=parser.parse_args();repo=a.repo_root.resolve();out=(a.output_root or repo).resolve();model=(a.model or repo/'simulations/grazing-refraction/model.mjs').resolve();exp=repo/'experiments/course-04/grazing-refraction';cases=[]
 for n in[1.25,1.33,1.45]:
  for n1 in[1.5,1.5425,1.55]:
   for zero in[0,180,359.9]:
    beta=brentq(lambda b:n1*math.sin(b)-n,0,math.pi/2,xtol=1e-15);gamma=math.pi/2-beta;phi=brentq(lambda f:math.sin(f)-n1*math.sin(gamma),0,math.pi/2,xtol=1e-15);cases.append({'parameters':{'liquid_index':n,'prism_index':n1,'zero_deg':zero,'eccentricity_arcmin':10},'exit_angle_deg':math.degrees(phi)})
 script="""import fs from'node:fs';const m=await import(process.argv[1]),d=JSON.parse(fs.readFileSync(0,'utf8'));console.log(JSON.stringify(d.map(c=>({forward:m.forward(c.parameters),measurement:m.measurement(c.parameters)}))));""";node=shutil.which('node')or r'C:\Program Files\nodejs\node.exe';result=json.loads(subprocess.run([node,'--input-type=module','-e',script,model.as_uri()],input=json.dumps(cases),text=True,capture_output=True,check=True).stdout);angle_error=max(abs(c['exit_angle_deg']-r['forward']['target_deg'])for c,r in zip(cases,result));index_error=max(abs(c['parameters']['liquid_index']-r['measurement']['estimate'])for c,r in zip(cases,result));assert angle_error<1e-9 and index_error<1e-10
 with(exp/'data/observations-01.csv').open(encoding='utf-8-sig',newline='')as f:raw=list(csv.reader(f))
 def angle(s):
  q=[float(v)for v in re.findall(r'\d+(?:\.\d+)?',s)];return q[0]+q[1]/60
 def difference(a,b):return abs(math.degrees(np.angle(np.exp(1j*math.radians(a-b)))))
 values=[]
 for row in raw[1:]:
  v=[angle(s)for s in row[1:5]];values.append((difference(v[2],v[0])+difference(v[3],v[1]))/2)
 mean=float(np.mean(values));analysis={'angle_mean_deg':mean,'type_a_arcmin':float(np.std(values,ddof=1)/math.sqrt(len(values))*60),'liquid_index':math.sqrt(1.5425**2-math.sin(math.radians(mean))**2),'per_trial_deg':values};paths=[exp/'experiment.json',exp/'data/observations-01.csv',exp/'data/provenance.json'];hashes={str(p.relative_to(repo)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths};obs={'experiment_id':'course-04/grazing-refraction','source':'original-report','tables':[{'headers':raw[0],'rows':raw[1:]}],'analysis':analysis,'input_hashes':hashes};record={'experiment_id':obs['experiment_id'],'status':'passed','created_at':datetime.now(timezone.utc).isoformat(),'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},'model_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),'input_hashes':hashes,'methods':['two-interface grazing incidence Snell equations solved by brentq','unit complex-number phase source circular differences'],'case_count':len(cases),'cases':cases,'maximum_errors':{'exit_angle_deg':angle_error,'liquid_index':index_error},'tolerances':{'exit_angle_deg':1e-9,'liquid_index':1e-10},'original_observation_analysis':analysis}
 for rel,data in[('simulations/grazing-refraction/observations.json',obs),('docs/simulation/grazing-refraction-reference.json',record)]:
  path=out/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
 print(json.dumps({'status':'passed','case_count':len(cases),'maximum_errors':record['maximum_errors']}))
if __name__=='__main__':main()
