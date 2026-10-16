"""Independent reference validation; writes only requested output artifacts."""
import argparse,csv,hashlib,json,math,subprocess
from pathlib import Path
import numpy as np
def make_cases():
 return [dict(mode=mode,E=E,R0=R0,K=K,X=X)for mode in['current','voltage']for E in[.1,5,12]for R0 in[50,1000,5000]for K in[.1,1,10]for X in[0,.1,.5,.9,1]]

def reference(p):
 load=p['K']*p['R0'];x=p['X']
 if p['mode']=='current':current=float(np.linalg.solve(np.array([[load+x*p['R0']]]),[p['E']])[0]);voltage=current*load
 else:
  if x==0:voltage=0.
  elif x==1:voltage=p['E']
  else:
   upper=(1-x)*p['R0'];lower=x*p['R0'];voltage=float(np.linalg.solve(np.array([[1/upper+1/lower+1/load]]),[p['E']/upper])[0])
  current=voltage/load
 return dict(voltage=voltage,current=current,current_mA=current*1000)


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--output-root',type=Path);ap.add_argument('--model',type=Path);a=ap.parse_args();out=a.output_root or a.repo_root;model=a.model or a.repo_root/'simulations/current-voltage-divider/model.mjs'
 cases=make_cases()
 code="import{readFileSync}from'node:fs';import{pathToFileURL}from'node:url';const m=await import(pathToFileURL(process.argv[1]));const ps=JSON.parse(readFileSync(0,'utf8'));console.log(JSON.stringify(ps.map(p=>m.response(p))));"
 run=subprocess.run(['node','--input-type=module','-e',code,str(model)],input=json.dumps(cases),text=True,capture_output=True,check=True);actual=json.loads(run.stdout);errors={}
 for p,b in zip(cases,actual):
  for key,val in reference(p).items():
   if isinstance(val,(float,int)):
    if not math.isfinite(b[key]):raise AssertionError('nonfinite '+key)
    errors[key]=max(errors.get(key,0),abs(b[key]-val)/max(1.,abs(val)))
 tolerance=1e-10
 if any(v>tolerance for v in errors.values()):raise AssertionError(errors)
 source=a.repo_root/'experiments/course-03/current-voltage-divider/data';tables={};hashes={}
 for file in sorted(source.glob('*.csv')):
  with file.open(encoding='utf-8-sig',newline='')as fh:rows=list(csv.reader(fh))
  tables[file.stem]={'title':file.stem,'headers':rows[0],'rows':rows[1:]};hashes[file.name]=hashlib.sha256(file.read_bytes()).hexdigest()
 dest=out/'simulations/current-voltage-divider/observations.json';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps({'experimentId':'course-03/current-voltage-divider','source':'original-report-observations','tables':tables,'sourceHashes':hashes},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 result={'experimentId':'course-03/current-voltage-divider','status':'passed','method':'independent DC nodal conductance equation','caseCount':len(cases),'maxScaledErrors':errors,'scaling':'abs(error)/max(1,abs(reference))','tolerance':tolerance,'modelSha256':hashlib.sha256(model.read_bytes()).hexdigest(),'numpyVersion':np.__version__}
 dest=out/'docs/simulation/current-voltage-divider-reference.json';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
