"""Independent reference validation; writes only requested output artifacts."""
import argparse,csv,hashlib,json,math,subprocess
from pathlib import Path
import numpy as np
def make_cases():
 return [dict(mode=mode,currentRange_mA=5,voltageRange=1.5,inputFraction=q,trim=trim,direction='up',R3=1100)for mode in['current','voltage']for q in[0,.5,1,1.2]for trim in[.8,1,1.2]]

def reference(p):
 ig=.001;rg=30
 if p['mode']=='current':
  full=p['currentRange_mA']*.001;reference=full*p['inputFraction'];design=rg/(full/ig-1);shunt=design*p['trim'];v=float(np.linalg.solve(np.array([[1/rg+1/shunt]]),[reference])[0]);head=v/rg;indicated=head/ig*full*1000;reference*=1000
 else:
  full=p['voltageRange'];reference=full*p['inputFraction'];design=full/ig-rg;head=float(np.linalg.solve(np.array([[rg+design*p['trim']]]),[reference])[0]);indicated=head/ig*full
 return dict(reference=reference,indicated=indicated,error=indicated-reference,designResistance=design,actualResistance=design*p['trim'],headCurrent=head)


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--output-root',type=Path);ap.add_argument('--model',type=Path);a=ap.parse_args();out=a.output_root or a.repo_root;model=a.model or a.repo_root/'simulations/meter-calibration/model.mjs'
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
 source=a.repo_root/'experiments/course-03/meter-calibration/data';tables={};hashes={}
 for file in sorted(source.glob('*.csv')):
  with file.open(encoding='utf-8-sig',newline='')as fh:rows=list(csv.reader(fh))
  tables[file.stem]={'title':file.stem,'headers':rows[0],'rows':rows[1:]};hashes[file.name]=hashlib.sha256(file.read_bytes()).hexdigest()
 dest=out/'simulations/meter-calibration/observations.json';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps({'experimentId':'course-03/meter-calibration','source':'original-report-observations','tables':tables,'sourceHashes':hashes},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 result={'experimentId':'course-03/meter-calibration','status':'passed','method':'independent ammeter conductance node and voltmeter series-loop matrix','caseCount':len(cases),'maxScaledErrors':errors,'scaling':'abs(error)/max(1,abs(reference))','tolerance':tolerance,'modelSha256':hashlib.sha256(model.read_bytes()).hexdigest(),'numpyVersion':np.__version__}
 dest=out/'docs/simulation/meter-calibration-reference.json';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
