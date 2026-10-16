"""Independent aperture-integral references for browser single-slit diffraction."""
import argparse,csv,hashlib,json,math,platform,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
import scipy
from scipy.integrate import quad
from scipy.optimize import minimize_scalar
def main():
 p=argparse.ArgumentParser();p.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--output-root',type=Path);p.add_argument('--model',type=Path);a=p.parse_args();repo=a.repo_root.resolve();out=(a.output_root or repo).resolve();model=(a.model or repo/'simulations/single-slit-diffraction/model.mjs').resolve();exp=repo/'experiments/course-04/single-slit-diffraction'
 def read(path):
  with path.open(encoding='utf-8-sig',newline='')as f:return list(csv.reader(f))[1:]
 obs={'experiment_id':'course-04/single-slit-diffraction','source':'original-report','wavelength_nm':632.8,'distance_mm':800,'scan':[{'position_mm':float(r[0]),'normalized_intensity':float(r[1])}for r in read(exp/'data/observations-01.csv')],'dark':[{'order':int(r[0]),'position_mm':float(r[1])}for r in read(exp/'data/observations-02.csv')]}
 cases=[]
 for width in[.05,.1,.2]:
  for distance in[800,1400,2000]:
   for wave in[500,632.8,700]:
    parameters={'width_mm':width,'distance_mm':distance,'wavelength_nm':wave};points=[]
    for x in[-15,-8,-2.5,-.1,0,.1,2.5,8,15]:
     q=2*math.pi*width*x/(math.hypot(distance,x)*wave*1e-6);real=quad(lambda u:math.cos(q*u),-.5,.5,epsabs=1e-12)[0];imag=quad(lambda u:math.sin(q*u),-.5,.5,epsabs=1e-12)[0];points.append({'position_mm':x,'intensity':real*real+imag*imag})
    cases.append({'parameters':parameters,'points':points})
 script="""import fs from'node:fs';const m=await import(process.argv[1]),d=JSON.parse(fs.readFileSync(0,'utf8'));console.log(JSON.stringify(d.map(c=>({intensities:c.points.map(r=>m.intensity(r.position_mm,c.parameters)),dark:[1,2,3,4].map(k=>m.darkPosition(k,c.parameters)),fit:m.fitDark([1,2,3,4].map(k=>m.measurement(k,c.parameters)))}))));"""
 node=shutil.which('node')or r'C:\Program Files\nodejs\node.exe';actual=json.loads(subprocess.run([node,'--input-type=module','-e',script,model.as_uri()],input=json.dumps(cases),text=True,capture_output=True,check=True).stdout);err=0;dark_error=0;width_error=0
 for case,result in zip(cases,actual):
  pp=case['parameters'];err=max(err,*[abs(r['intensity']-v)for r,v in zip(case['points'],result['intensities'])]);width_error=max(width_error,abs(result['fit']['width_mm']-pp['width_mm']))
  for order,x in enumerate(result['dark'],1):
   q=2*math.pi*pp['width_mm']*x/(math.hypot(pp['distance_mm'],x)*pp['wavelength_nm']*1e-6);amp=quad(lambda u:math.cos(q*u),-.5,.5,epsabs=1e-12)[0];dark_error=max(dark_error,amp**2)
 assert err<1e-10 and dark_error<1e-20 and width_error<1e-10
 hashes={str(path.relative_to(repo)).replace('\\','/'):hashlib.sha256(path.read_bytes()).hexdigest()for path in[exp/'experiment.json',exp/'data/observations-01.csv',exp/'data/observations-02.csv',exp/'data/provenance.json']};obs['input_hashes']=hashes
 reference={'experiment_id':obs['experiment_id'],'status':'passed','created_at':datetime.now(timezone.utc).isoformat(),'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},'model_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),'input_hashes':hashes,'methods':['SciPy quadrature of complex uniform-aperture amplitude','angular dark-fringe condition and independent quadrature zero','synthetic full-precision angular least-squares recovery'],'case_count':len(cases),'point_count':sum(len(c['points'])for c in cases),'cases':cases,'maximum_errors':{'intensity':err,'dark_intensity':dark_error,'width_mm':width_error},'tolerances':{'intensity':1e-10,'dark_intensity':1e-20,'width_mm':1e-10},'sampling':{'curve_dx_mm':.025,'minimum_dark_spacing_mm':2.,'minimum_samples_per_spacing':80},'original_observation_summary':{'near_axis_width_mean_mm':float(np.mean([r['order']*632.8e-6*800/r['position_mm']for r in obs['dark']]))}}
 for rel,data in[('simulations/single-slit-diffraction/observations.json',obs),('docs/simulation/single-slit-diffraction-reference.json',reference)]:
  path=out/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
 print(json.dumps({'status':'passed','case_count':len(cases),'maximum_errors':reference['maximum_errors']}))
if __name__=='__main__':main()
