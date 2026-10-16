"""Independent reference validation; writes only requested output artifacts."""
import argparse,csv,hashlib,json,math,subprocess
from pathlib import Path
import numpy as np
def make_cases():
 return [dict(unknown_mOhm=Rx,standard_mOhm=Rs,ratio=M,contact_mOhm=r,mismatch=e,sourceVoltage=.01)for Rx in[1,2,10]for Rs in[1,2,10]for M in[.1,1,10]for r in[0,10,100]for e in[-.1,0,.1]]

def reference(a):
 rx=a['unknown_mOhm']*.001;rs=a['standard_mOhm']*.001;r=a['contact_mOhm']*.001;M=a['ratio'];q=100;p=M*q*(1+a['mismatch']);E=a['sourceVoltage'];P=M*1000;Q=1000
 v1=float(np.linalg.solve(np.array([[1/P+1/Q]]),[E/P])[0])
 if r==0:
  v2=float(np.linalg.solve(np.array([[1/rx+1/rs]]),[E/rx])[0]);main=E/(rx+rs)
 else:
  mat=np.array([[1/rx+1/r+1/p,-1/r,-1/p],[-1/r,1/r+1/rs+1/q,-1/q],[-1/p,-1/q,1/p+1/q]])
  vb,vc,v2=np.linalg.solve(mat,[E/rx,0,0]);main=(E-vb)/rx
 return dict(bridge_uV=(v1-v2)*1e6,uncorrected_mOhm=M*a['standard_mOhm'],mainCurrent=float(main))


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--output-root',type=Path);ap.add_argument('--model',type=Path);a=ap.parse_args();out=a.output_root or a.repo_root;model=a.model or a.repo_root/'simulations/kelvin-bridge/model.mjs'
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
 source=a.repo_root/'experiments/course-03/kelvin-bridge/data';tables={};hashes={}
 for file in sorted(source.glob('*.csv')):
  with file.open(encoding='utf-8-sig',newline='')as fh:rows=list(csv.reader(fh))
  tables[file.stem]={'title':file.stem,'headers':rows[0],'rows':rows[1:]};hashes[file.name]=hashlib.sha256(file.read_bytes()).hexdigest()
 dest=out/'simulations/kelvin-bridge/observations.json';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps({'experimentId':'course-03/kelvin-bridge','source':'original-report-observations','tables':tables,'sourceHashes':hashes},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 result={'experimentId':'course-03/kelvin-bridge','status':'passed','method':'independent four-node Kelvin bridge with actual secondary shunt of contact link','caseCount':len(cases),'maxScaledErrors':errors,'scaling':'abs(error)/max(1,abs(reference))','tolerance':tolerance,'modelSha256':hashlib.sha256(model.read_bytes()).hexdigest(),'numpyVersion':np.__version__}
 dest=out/'docs/simulation/kelvin-bridge-reference.json';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
