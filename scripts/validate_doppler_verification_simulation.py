"""Numerical wavefront/trajectory intersection independent validation."""
import argparse,csv,hashlib,json,math,subprocess
from pathlib import Path
import numpy as np
import scipy
from scipy.optimize import brentq
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--output-root',type=Path);ap.add_argument('--model',type=Path);a=ap.parse_args();out=a.output_root or a.repo_root;model=a.model or a.repo_root/'simulations/doppler-verification/model.mjs'
 cases=[]
 for temp in[0,23.1,40]:
  for frequency in[20000,40002,60000]:
   for velocity in[-1.5,-.75,0,.46,.88,1.27,1.5]:cases.append(dict(temperature=temp,frequency=frequency,velocity=velocity,distance=.5))
 code="import{readFileSync}from'node:fs';import{pathToFileURL}from'node:url';const m=await import(pathToFileURL(process.argv[1]));const ps=JSON.parse(readFileSync(0,'utf8'));console.log(JSON.stringify(ps.map(p=>({r:m.response(p),arrivals:Array.from({length:6},(_,n)=>m.arrival(p,n))}))));"
 run=subprocess.run(['node','--input-type=module','-e',code,str(model)],input=json.dumps(cases),text=True,capture_output=True,check=True);results=json.loads(run.stdout);errs={'arrival_absolute_s':0.,'frequency_relative':0.}
 for p,r in zip(cases,results):
  c=331.45*math.sqrt(1+p['temperature']/273.15);times=[]
  for n in range(6):
   emission=n/p['frequency'];t=brentq(lambda t:c*(t-emission)-(p['distance']-p['velocity']*t),emission,emission+.1,xtol=1e-15);times.append(t);errs['arrival_absolute_s']=max(errs['arrival_absolute_s'],abs(t-r['arrivals'][n]))
  frequency=1/float(np.mean(np.diff(times)));errs['frequency_relative']=max(errs['frequency_relative'],abs(frequency-r['r']['received'])/frequency)
 source=a.repo_root/'experiments/course-01/doppler-verification/data/observations.csv'
 with source.open(encoding='utf-8-sig',newline='')as fh: rows=[{'velocity':float(r['velocity_m_s']),'frequency':float(r['frequency_hz'])}for r in csv.DictReader(fh)]
 coef=np.linalg.lstsq(np.column_stack([[r['velocity']for r in rows],np.ones(len(rows))]),[r['frequency']for r in rows],rcond=None)[0]
 limits={'arrival_absolute_s':1e-12,'frequency_relative':1e-10}
 if any(errs[k]>limits[k]for k in errs):raise AssertionError(errs)
 obs={'experimentId':'course-01/doppler-verification','source':'original-report-observations','sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'sourceFrequency':40002,'temperature':23.1,'rows':rows,'units':{'velocity':'m/s','frequency':'Hz'}}
 dest=out/'simulations/doppler-verification/observations.json';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(obs,indent=2)+'\n',encoding='utf-8')
 report={'experimentId':'course-01/doppler-verification','status':'passed','method':'Brent intersection of each expanding wavefront with receiver trajectory; mean arrival interval','caseCount':len(cases),'wavefrontsPerCase':6,'maxErrors':errs,'tolerances':limits,'modelSha256':hashlib.sha256(model.read_bytes()).hexdigest(),'scipyVersion':scipy.__version__,'observedFit':{'slope':float(coef[0]),'intercept':float(coef[1]),'soundSpeed':float(40002/coef[0])}}
 dest=out/'docs/simulation/doppler-verification-reference.json';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
