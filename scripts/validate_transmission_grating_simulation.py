"""Independent finite complex aperture sums and spectral angle calculations."""
import argparse,csv,hashlib,json,math,platform,re,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
import scipy
from scipy.integrate import quad
from scipy.optimize import brentq
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1]);parser.add_argument('--output-root',type=Path);parser.add_argument('--model',type=Path);a=parser.parse_args();repo=a.repo_root.resolve();out=(a.output_root or repo).resolve();model=(a.model or repo/'simulations/transmission-grating/model.mjs').resolve();exp=repo/'experiments/course-04/transmission-grating';cases=[]
 for d in[1,2,4]:
  for wave in[400,546.1,700]:
   for N in[10,20,50]:
    for order in[1,2,3]:
     if order*wave>=d*1000:continue
     theta=brentq(lambda x:d*1000*math.sin(x)-order*wave,0,math.pi/2,xtol=1e-15);points=[]
     for angle in[-70,-20,-1,0,1,20,70,math.degrees(theta)]:
      q=2*math.pi*d*1000*math.sin(math.radians(angle))/wave;aperture=quad(lambda u:math.cos(.25*q*u),-.5,.5,epsabs=1e-12)[0];field=np.sum(np.exp(1j*q*np.arange(N)))/N;points.append({'angle_deg':angle,'intensity':float(abs(field*aperture)**2)})
     cases.append({'parameters':{'spacing_um':d,'wavelength_nm':wave,'order':order,'slit_count':N,'open_fraction':.25,'zero_deg':359.9,'eccentricity_arcmin':10},'theta_deg':math.degrees(theta),'points':points})
 script="""import fs from'node:fs';const m=await import(process.argv[1]),d=JSON.parse(fs.readFileSync(0,'utf8'));console.log(JSON.stringify(d.map(c=>({forward:m.forward(c.parameters),measurement:m.measurement(c.parameters),intensities:c.points.map(p=>m.diffractionIntensity(p.angle_deg,c.parameters))}))));""";node=shutil.which('node')or r'C:\Program Files\nodejs\node.exe';result=json.loads(subprocess.run([node,'--input-type=module','-e',script,model.as_uri()],input=json.dumps(cases),text=True,capture_output=True,check=True).stdout);angle_error=max(abs(c['theta_deg']-r['forward']['theta_deg'])for c,r in zip(cases,result));wavelength_error=max(abs(c['parameters']['wavelength_nm']-r['measurement']['estimate'])for c,r in zip(cases,result));intensity_error=max(abs(p['intensity']-v)for c,r in zip(cases,result)for p,v in zip(c['points'],r['intensities']));assert angle_error<1e-9 and wavelength_error<1e-8 and intensity_error<1e-10
 def angle(s):
  q=[float(v)for v in re.findall(r'\d+(?:\.\d+)?',s)];return q[0]+q[1]/60
 def diff(a,b):return abs(math.degrees(np.angle(np.exp(1j*math.radians(a-b)))))
 tables=[];phis=[]
 for idx in[1,2,3,4]:
  with(exp/f'data/observations-{idx:02d}.csv').open(encoding='utf-8-sig',newline='')as f:raw=list(csv.reader(f))
  values=[]
  for row in raw[1:]:
   v=[angle(s)for s in row[1:5]];values.append((diff(v[0],v[1])+diff(v[2],v[3]))/4)
  phis.append(float(np.mean(values)));tables.append({'headers':raw[0],'rows':raw[1:]})
 spacing=546.1/math.sin(math.radians(phis[1]));analysis={'angle_means_deg':phis,'spacing_nm':spacing,'wavelengths_nm':[spacing*math.sin(math.radians(v))for v in phis]};paths=[exp/'experiment.json',exp/'data/provenance.json',*[exp/f'data/observations-{i:02d}.csv'for i in[1,2,3,4]]];hashes={str(p.relative_to(repo)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths};obs={'experiment_id':'course-04/transmission-grating','source':'original-report','tables':tables,'analysis':analysis,'input_hashes':hashes};phase_step=2*math.pi*50*4e3/400*math.radians(.02);assert phase_step<math.pi;record={'experiment_id':obs['experiment_id'],'status':'passed','created_at':datetime.now(timezone.utc).isoformat(),'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},'model_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),'input_hashes':hashes,'methods':['direct finite complex sum over individual apertures','numerical quadrature of rectangular-slit envelope','brentq direction equation root','unit complex phases for raw dual-vernier readings'],'case_count':len(cases),'cases':cases,'maximum_errors':{'angle_deg':angle_error,'wavelength_nm':wavelength_error,'intensity':intensity_error},'tolerances':{'angle_deg':1e-9,'wavelength_nm':1e-8,'intensity':1e-10},'sampling':{'angular_step_deg':.02,'maximum_intensity_phase_step_rad':phase_step},'original_observation_analysis':analysis}
 for rel,data in[('simulations/transmission-grating/observations.json',obs),('docs/simulation/transmission-grating-reference.json',record)]:
  path=out/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
 print(json.dumps({'status':'passed','case_count':len(cases),'maximum_errors':record['maximum_errors']}))
if __name__=='__main__':main()
