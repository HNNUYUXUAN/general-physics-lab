"""Independent reference validation; writes only requested output artifacts."""
import argparse,csv,hashlib,json,math,subprocess
from pathlib import Path
import numpy as np
def make_cases():
 return [dict(coils=coils,current_mA=I,radius_cm=R,spacingRatio=d,positionRatio=x)for coils in['single','double']for I in[100,300,800]for R in[8,10.5,15]for d in[.5,1,1.5]for x in[-2,-1,0,1,2]]

def reference(p):
 from scipy.integrate import quad_vec
 R=p['radius_cm']*.01;I=p['current_mA']*.001;x=p['positionRatio']*R;centers=[0]if p['coils']=='single'else[-p['spacingRatio']*R/2,p['spacingRatio']*R/2]
 def field(x):
  total=np.zeros(3)
  for center in centers:
   def integrand(phi):
    dl=np.array([-R*math.sin(phi),R*math.cos(phi),0]);delta=np.array([-R*math.cos(phi),-R*math.sin(phi),x-center]);return np.cross(dl,delta)/np.linalg.norm(delta)**3
   total+=quad_vec(integrand,0,2*math.pi,epsabs=1e-10,epsrel=1e-11)[0]*1e-7*500*I
  return float(total[2]*1000)
 B=field(x);B0=field(0)
 return dict(position_mm=x*1000,field_mT=B,normalized=B/B0,relativeDeviationPercent=(B/B0-1)*100,centerField_mT=B0)


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--output-root',type=Path);ap.add_argument('--model',type=Path);a=ap.parse_args();out=a.output_root or a.repo_root;model=a.model or a.repo_root/'simulations/magnetic-field/model.mjs'
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
 source=a.repo_root/'experiments/course-03/magnetic-field/data';tables={};hashes={}
 for file in sorted(source.glob('*.csv')):
  with file.open(encoding='utf-8-sig',newline='')as fh:rows=list(csv.reader(fh))
  tables[file.stem]={'title':file.stem,'headers':rows[0],'rows':rows[1:]};hashes[file.name]=hashlib.sha256(file.read_bytes()).hexdigest()
 dest=out/'simulations/magnetic-field/observations.json';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps({'experimentId':'course-03/magnetic-field','source':'original-report-observations','tables':tables,'sourceHashes':hashes},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 result={'experimentId':'course-03/magnetic-field','status':'passed','method':'independent vector Biot-Savart line quadrature around each circular loop','caseCount':len(cases),'maxScaledErrors':errors,'scaling':'abs(error)/max(1,abs(reference))','tolerance':tolerance,'modelSha256':hashlib.sha256(model.read_bytes()).hexdigest(),'numpyVersion':np.__version__}
 dest=out/'docs/simulation/magnetic-field-reference.json';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
