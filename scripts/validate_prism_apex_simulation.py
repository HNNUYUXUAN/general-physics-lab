"""Independent complex-circle angular differences and source data recomputation."""
import argparse,csv,hashlib,json,math,platform,re,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1]);parser.add_argument('--output-root',type=Path);parser.add_argument('--model',type=Path);a=parser.parse_args();repo=a.repo_root.resolve();out=(a.output_root or repo).resolve();model=(a.model or repo/'simulations/prism-apex/model.mjs').resolve();exp=repo/'experiments/course-04/prism-apex'
 def load(path):
  with path.open(encoding='utf-8-sig',newline='')as f:return list(csv.reader(f))
 tables=[]
 for i in[1]:
  raw=load(exp/f'data/observations-{i:02d}.csv');tables.append({'headers':raw[0],'rows':raw[1:]})
 def angle(s):
  q=[float(v)for v in re.findall(r'\d+(?:\.\d+)?',s)];return q[0]+q[1]/60
 def diff(a,b):return math.degrees(np.angle(np.exp(1j*math.radians(a))/np.exp(1j*math.radians(b))))
 values=[]
 for row in tables[0]['rows']:
  x=[angle(c)for c in row[1:5]];values.append((abs(diff(x[2],x[0]))+abs(diff(x[3],x[1])))/4)
 cases=[]
 for delta in[40,60,80]:
  for zero in[0,180,359.9]:
   for ecc in[0,5,10]:cases.append({'apex_deg':delta,'zero_deg':zero,'eccentricity_arcmin':ecc})
 script="""import fs from'node:fs';const m=await import(process.argv[1]),d=JSON.parse(fs.readFileSync(0,'utf8'));console.log(JSON.stringify(d.map(p=>m.measurement(p))));""";node=shutil.which('node')or r'C:\Program Files\nodejs\node.exe';result=json.loads(subprocess.run([node,'--input-type=module','-e',script,model.as_uri()],input=json.dumps(cases),text=True,capture_output=True,check=True).stdout);error=0
 for p,r in zip(cases,result):
  ds=[diff(r['end'][k],r['start'][k])for k in['left_deg','right_deg']];ref=abs(sum(ds)/4);error=max(error,abs(ref-r['estimate']),abs(r['estimate']-p['apex_deg']))
 # Independent vector mirror reflections: normals separated by apex angle.
 for p,r in zip(cases,result):
  a=math.radians(p['apex_deg']);incoming=np.array([0.,-1.]);n1=np.array([1.,0.]);n2=np.array([math.cos(a),math.sin(a)]);v1=incoming-2*np.dot(incoming,n1)*n1;v2=incoming-2*np.dot(incoming,n2)*n2;physical_angle=math.degrees(math.acos(float(np.clip(np.dot(v1,v2),-1,1))))/2;error=max(error,abs(physical_angle-r['estimate']))
 assert error<1e-9
 paths=[exp/'experiment.json',exp/'data/observations-01.csv',exp/'data/provenance.json'];hashes={str(path.relative_to(repo)).replace('\\','/'):hashlib.sha256(path.read_bytes()).hexdigest()for path in paths};analysis={'angle_mean_deg':float(np.mean(values)),'type_a_arcmin':float(np.std(values,ddof=1)/math.sqrt(len(values))*60),'per_trial_deg':values}
 obs={'experiment_id':'course-04/prism-apex','source':'original-report','tables':tables,'analysis':analysis,'input_hashes':hashes};record={'experiment_id':obs['experiment_id'],'status':'passed','created_at':datetime.now(timezone.utc).isoformat(),'environment':{'python':platform.python_version(),'numpy':np.__version__},'model_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),'input_hashes':hashes,'method':'independent mirror-normal vector reflection, and unit complex-number quotient phase','case_count':len(cases),'cases':cases,'maximum_error_deg':error,'tolerance_deg':1e-9,'original_observation_analysis':analysis}
 for rel,data in[('simulations/prism-apex/observations.json',obs),('docs/simulation/prism-apex-reference.json',record)]:
  path=out/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
 print(json.dumps({'status':'passed','case_count':len(cases),'max_error_deg':error}))
if __name__=='__main__':main()
