"""Independent reference validation; writes only requested output artifacts."""
import argparse,csv,hashlib,json,math,subprocess
from pathlib import Path
import numpy as np
def make_cases():
 return [dict(polarity=n,current_mA=I,field_T=B,sensitivity=K,common_mV=.5,currentOdd_mV=.3,fieldOdd_mV=.2,sameParity_mV=same)for n in[1,2,3,4]for I in[.1,3,5]for B in[0,.3,1]for K in[10,100,200]for same in[0,2]]

def reference(p):
 matrix=np.array([[1,1,1,1],[-1,1,1,-1],[1,1,-1,-1],[-1,1,-1,1]],dtype=float)
 H=p['sensitivity']*(p['current_mA']*.001)*p['field_T']*1000
 components=np.array([H+p['sameParity_mV'],p['common_mV'],p['currentOdd_mV'],p['fieldOdd_mV']]);raw=matrix@components;recovered=np.linalg.solve(matrix,raw);n=int(p['polarity'])-1
 return dict(rawVoltage_mV=float(raw[n]),trueHall_mV=H,projectedHall_mV=float(recovered[0]),projectedCommon_mV=float(recovered[1]),projectedCurrentOdd_mV=float(recovered[2]),projectedFieldOdd_mV=float(recovered[3]))


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--output-root',type=Path);ap.add_argument('--model',type=Path);a=ap.parse_args();out=a.output_root or a.repo_root;model=a.model or a.repo_root/'simulations/hall-effect/model.mjs'
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
 source=a.repo_root/'experiments/course-03/hall-effect/data';tables={};hashes={}
 for file in sorted(source.glob('*.csv')):
  with file.open(encoding='utf-8-sig',newline='')as fh:rows=list(csv.reader(fh))
  tables[file.stem]={'title':file.stem,'headers':rows[0],'rows':rows[1:]};hashes[file.name]=hashlib.sha256(file.read_bytes()).hexdigest()
 dest=out/'simulations/hall-effect/observations.json';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps({'experimentId':'course-03/hall-effect','source':'original-report-observations','tables':tables,'sourceHashes':hashes},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 result={'experimentId':'course-03/hall-effect','status':'passed','method':'independent four-polarity linear-system inversion (Hadamard basis)','caseCount':len(cases),'maxScaledErrors':errors,'scaling':'abs(error)/max(1,abs(reference))','tolerance':tolerance,'modelSha256':hashlib.sha256(model.read_bytes()).hexdigest(),'numpyVersion':np.__version__}
 dest=out/'docs/simulation/hall-effect-reference.json';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
