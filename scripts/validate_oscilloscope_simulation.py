"""Independent reference validation; writes only requested output artifacts."""
import argparse,csv,hashlib,json,math,subprocess
from pathlib import Path
import numpy as np
def make_cases():
 return [dict(waveform=w,amplitude=A,frequency=f,voltsPerDiv=.2,msPerDiv=.2,y1=-2.5,y2=2.5,x1=1,x2=6,phase=45,ratio=1)for w in['sine','triangle','square']for A in[.1,.5,2]for f in[250,1000,2000]]

def reference(p):
 from scipy.integrate import quad
 A=p['amplitude'];kind=p['waveform']
 def wave(t):
  if kind=='sine':return A*math.sin(2*math.pi*t)
  if kind=='square':return A if t<.5 else -A
  return A*(4*t if t<.25 else 2-4*t if t<.75 else 4*t-4)
 rms=math.sqrt(quad(lambda t:wave(t)**2,0,1,points=[.25,.5,.75],epsabs=1e-12)[0]);vpp=abs(p['y2']-p['y1'])*p['voltsPerDiv'];Tms=abs(p['x2']-p['x1'])*p['msPerDiv'];factor=math.sqrt(2)if kind=='sine'else math.sqrt(3)if kind=='triangle'else 1
 return dict(trueRMS=rms,measuredVpp=vpp,measuredPeriodMs=Tms,measuredFrequency=1000/Tms,measuredRMS=vpp/(2*factor))


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--output-root',type=Path);ap.add_argument('--model',type=Path);a=ap.parse_args();out=a.output_root or a.repo_root;model=a.model or a.repo_root/'simulations/oscilloscope/model.mjs'
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
 source=a.repo_root/'experiments/course-03/oscilloscope/data';tables={};hashes={}
 for file in sorted(source.glob('*.csv')):
  with file.open(encoding='utf-8-sig',newline='')as fh:rows=list(csv.reader(fh))
  tables[file.stem]={'title':file.stem,'headers':rows[0],'rows':rows[1:]};hashes[file.name]=hashlib.sha256(file.read_bytes()).hexdigest()
 dest=out/'simulations/oscilloscope/observations.json';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps({'experimentId':'course-03/oscilloscope','source':'original-report-observations','tables':tables,'sourceHashes':hashes},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 result={'experimentId':'course-03/oscilloscope','status':'passed','method':'independent numerical waveform energy quadrature and cursor scale conversion','caseCount':len(cases),'maxScaledErrors':errors,'scaling':'abs(error)/max(1,abs(reference))','tolerance':tolerance,'modelSha256':hashlib.sha256(model.read_bytes()).hexdigest(),'numpyVersion':np.__version__}
 dest=out/'docs/simulation/oscilloscope-reference.json';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
