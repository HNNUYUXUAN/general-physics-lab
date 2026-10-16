"""Independent reference validation; writes only requested output artifacts."""
import argparse,csv,hashlib,json,math,subprocess
from pathlib import Path
import numpy as np
def make_cases():
 return [dict(mode='voltage',voltage=E,sourceResistance=Rs,voltageRange=20,Rx=Rx,multiplier=1,battery=Eb,zeroFactor=1)for E in[1.5,10,20]for Rs in[1,1000,1000000]for Rx in[0,1500,100000]for Eb in[.8,1.5,1.6]]

def reference(p):
 rs=p['sourceResistance'];E=p['voltage'];rv=1e7;va=float(np.linalg.solve(np.array([[1/rs+1/rv]]),[E/rs])[0]);analogrv=20000*p['voltageRange'];vb=float(np.linalg.solve(np.array([[1/rs+1/analogrv]]),[E/rs])[0]);base=1500*p['multiplier'];ig=1.5/base;current=float(np.linalg.solve(np.array([[base*p['zeroFactor']+p['Rx']]]),[p['battery']])[0]);fraction=current/ig;digits=round(va/(p['voltageRange']/2000))*(p['voltageRange']/2000)
 return dict(digitalVoltage=digits,analogVoltage=vb,fraction=fraction,indicatedResistance=base*(1/fraction-1),inputLoadedVoltage=va)


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--output-root',type=Path);ap.add_argument('--model',type=Path);a=ap.parse_args();out=a.output_root or a.repo_root;model=a.model or a.repo_root/'simulations/multimeter/model.mjs'
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
 source=a.repo_root/'experiments/course-03/multimeter/data';tables={};hashes={}
 for file in sorted(source.glob('*.csv')):
  with file.open(encoding='utf-8-sig',newline='')as fh:rows=list(csv.reader(fh))
  tables[file.stem]={'title':file.stem,'headers':rows[0],'rows':rows[1:]};hashes[file.name]=hashlib.sha256(file.read_bytes()).hexdigest()
 dest=out/'simulations/multimeter/observations.json';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps({'experimentId':'course-03/multimeter','source':'original-report-observations','tables':tables,'sourceHashes':hashes},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 result={'experimentId':'course-03/multimeter','status':'passed','method':'independent voltage nodal loading and ohmmeter loop solve','caseCount':len(cases),'maxScaledErrors':errors,'scaling':'abs(error)/max(1,abs(reference))','tolerance':tolerance,'modelSha256':hashlib.sha256(model.read_bytes()).hexdigest(),'numpyVersion':np.__version__}
 dest=out/'docs/simulation/multimeter-reference.json';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
