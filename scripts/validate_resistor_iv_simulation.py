"""Independent reference validation; writes only requested output artifacts."""
import argparse,csv,hashlib,json,math,subprocess
from pathlib import Path
import numpy as np
def make_cases():
 return [dict(mode=mode,U=U,R=R,RA=RA,RV=RV)for mode in['internal','external']for U in[.05,1,2]for R in[10,1000,1000000]for RA in[.1,1,100]for RV in[10000,1000000,100000000]]

def reference(p):
 U,R,RA,RV=p['U'],p['R'],p['RA'],p['RV']
 if p['mode']=='internal':
  v=float(np.linalg.solve(np.array([[1/R+1/RA]]),[U/R])[0]);current=v/RA
 else:
  branch=np.linalg.solve(np.diag([R,RV]),[U,U]);current=float(branch.sum())
 apparent=U/current
 return dict(voltage=U,current_mA=current*1000,apparentResistance=apparent,errorPercent=(apparent-R)/R*100)


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--output-root',type=Path);ap.add_argument('--model',type=Path);a=ap.parse_args();out=a.output_root or a.repo_root;model=a.model or a.repo_root/'simulations/resistor-iv/model.mjs'
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
 source=a.repo_root/'experiments/course-03/resistor-iv/data';tables={};hashes={}
 for file in sorted(source.glob('*.csv')):
  with file.open(encoding='utf-8-sig',newline='')as fh:rows=list(csv.reader(fh))
  tables[file.stem]={'title':file.stem,'headers':rows[0],'rows':rows[1:]};hashes[file.name]=hashlib.sha256(file.read_bytes()).hexdigest()
 dest=out/'simulations/resistor-iv/observations.json';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps({'experimentId':'course-03/resistor-iv','source':'original-report-observations','tables':tables,'sourceHashes':hashes},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 result={'experimentId':'course-03/resistor-iv','status':'passed','method':'independent resistor branch nodal matrix including meter loading','caseCount':len(cases),'maxScaledErrors':errors,'scaling':'abs(error)/max(1,abs(reference))','tolerance':tolerance,'modelSha256':hashlib.sha256(model.read_bytes()).hexdigest(),'numpyVersion':np.__version__}
 dest=out/'docs/simulation/resistor-iv-reference.json';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
