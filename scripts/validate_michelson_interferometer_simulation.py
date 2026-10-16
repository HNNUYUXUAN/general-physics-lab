"""Independent coherent complex-wave sums and numerical fringe cycle roots."""
import argparse,csv,hashlib,json,math,platform,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
import scipy
from scipy.optimize import brentq
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1]);parser.add_argument('--output-root',type=Path);parser.add_argument('--model',type=Path);a=parser.parse_args();repo=a.repo_root.resolve();out=(a.output_root or repo).resolve();model=(a.model or repo/'simulations/michelson-interferometer/model.mjs').resolve();exp=repo/'experiments/course-04/michelson-interferometer';cases=[]
 for wavelength in[400,632.8,700]:
  for tilt in[0,.25,2]:
   for start in[0,.1,1]:
    p={'wavelength_nm':wavelength,'tilt_mrad':tilt};points=[]
    for x in[-2,-1,0,1,2]:
     field=(1+np.exp(1j*2*math.pi*(2*start+2*tilt*x)/(wavelength*.001)))/2;points.append({'position_mm':x,'intensity':float(abs(field)**2)})
    N=100;end=brentq(lambda d:4*math.pi*(d-start)/(wavelength*.001)-2*math.pi*N,start,40,xtol=1e-13);cases.append({'parameters':p,'start_um':start,'fringe_count':N,'end_um':end,'points':points})
 script="""import fs from'node:fs';const m=await import(process.argv[1]),d=JSON.parse(fs.readFileSync(0,'utf8'));console.log(JSON.stringify(d.map(c=>({record:m.autoMeasurement(c.parameters,c.start_um,c.fringe_count),intensities:c.points.map(p=>m.intensity(p.position_mm,c.start_um,c.parameters))}))));""";node=shutil.which('node')or r'C:\Program Files\nodejs\node.exe';result=json.loads(subprocess.run([node,'--input-type=module','-e',script,model.as_uri()],input=json.dumps(cases),text=True,capture_output=True,check=True).stdout);intensity_error=max(abs(p['intensity']-v)for c,r in zip(cases,result)for p,v in zip(c['points'],r['intensities']));end_error=max(abs(c['end_um']-r['record']['mirror_end_um'])for c,r in zip(cases,result));wavelength_error=max(abs(c['parameters']['wavelength_nm']-r['record']['wavelength_estimate_nm'])for c,r in zip(cases,result));assert intensity_error<1e-12 and end_error<1e-10 and wavelength_error<1e-9
 with(exp/'data/observations-01.csv').open(encoding='utf-8-sig',newline='')as f:raw=list(csv.reader(f))[1:]
 rows=[{'trial':int(r[0]),'fringe_count':int(r[1]),'start_mm':float(r[2]),'end_mm':float(r[3]),'wavelength_nm':2*(float(r[3])-float(r[2]))/int(r[1])*1e6}for r in raw];values=np.array([r['wavelength_nm']for r in rows]);analysis={'wavelength_mean_nm':float(values.mean()),'wavelength_type_a_nm':float(values.std(ddof=1)/math.sqrt(len(values)))};paths=[exp/'experiment.json',exp/'data/observations-01.csv',exp/'data/provenance.json'];hashes={str(p.relative_to(repo)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths};obs={'experiment_id':'course-04/michelson-interferometer','source':'original-report','rows':rows,'analysis':analysis,'input_hashes':hashes};phase_step=2*math.pi*2*2*.008/(400*.001);assert phase_step<math.pi;record={'experiment_id':obs['experiment_id'],'status':'passed','created_at':datetime.now(timezone.utc).isoformat(),'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},'model_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),'input_hashes':hashes,'methods':['direct sum of two complex plane waves','brentq root of unwrapped accumulated phase for100fringes','independent source100fringe displacement recalculation'],'case_count':len(cases),'cases':cases,'maximum_errors':{'intensity':intensity_error,'mirror_end_um':end_error,'wavelength_nm':wavelength_error},'tolerances':{'intensity':1e-12,'mirror_end_um':1e-10,'wavelength_nm':1e-9},'sampling':{'pixels_per_axis':501,'extent_mm':2,'maximum_phase_step_rad':phase_step},'original_observation_analysis':analysis}
 for rel,data in[('simulations/michelson-interferometer/observations.json',obs),('docs/simulation/michelson-interferometer-reference.json',record)]:
  path=out/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
 print(json.dumps({'status':'passed','case_count':len(cases),'maximum_errors':record['maximum_errors']}))
if __name__=='__main__':main()
