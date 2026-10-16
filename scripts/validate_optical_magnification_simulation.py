"""Independent ABCD ray-transfer matrix image formation and calibration."""
import argparse,csv,hashlib,json,math,platform,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
import scipy
from scipy.optimize import brentq
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1]);parser.add_argument('--output-root',type=Path);parser.add_argument('--model',type=Path);a=parser.parse_args();repo=a.repo_root.resolve();out=(a.output_root or repo).resolve();model=(a.model or repo/'simulations/optical-magnification/model.mjs').resolve();exp=repo/'experiments/course-04/optical-magnification';cases=[]
 propagation=lambda d:np.array([[1.,d],[0.,1.]])
 lens=lambda f:np.array([[1.,0.],[-1/f,1.]])
 for f in[10,20,30]:
  for ratio in[1.1,1.2,1.5]:
   for pitch in[.05,.1,.2]:
    u=f*ratio;v=brentq(lambda d:(propagation(d)@lens(f)@propagation(u))[0,1],0,10000,xtol=1e-12);M=abs((propagation(v)@lens(f)@propagation(u))[0,0]);cases.append({'parameters':{'focal_mm':f,'object_ratio':ratio,'eyepiece_pitch_mm':pitch,'wire_width_mm':.05,'telescope_objective_mm':200,'telescope_eyepiece_mm':40},'image_distance_mm':v,'magnification':float(M),'scale_mm_div':pitch/M})
 telescopes=[]
 for fo in[100,200,300]:
  for fe in[20,40,50]:
   matrix=lens(fe)@propagation(fo+fe)@lens(fo);assert abs(matrix[1,0])<1e-12;telescopes.append({'parameters':{**cases[0]['parameters'],'telescope_objective_mm':fo,'telescope_eyepiece_mm':fe},'angular_magnification':float(matrix[1,1])})
 script="""import fs from'node:fs';const m=await import(process.argv[1]),d=JSON.parse(fs.readFileSync(0,'utf8'));console.log(JSON.stringify({cases:d.cases.map(c=>{const cal=m.measurement('calibration',c.parameters),scale=m.calibrationScale([cal],c.parameters,'ideal-model');return{optics:m.optics(c.parameters),cal,wire:m.measurement('wire',c.parameters,'ideal-model',null,null,scale)};}),telescopes:d.telescopes.map(c=>m.optics(c.parameters).telescope_magnification)}));""";node=shutil.which('node')or r'C:\Program Files\nodejs\node.exe';result=json.loads(subprocess.run([node,'--input-type=module','-e',script,model.as_uri()],input=json.dumps({'cases':cases,'telescopes':telescopes}),text=True,capture_output=True,check=True).stdout);v_error=max(abs(c['image_distance_mm']-r['optics']['image_distance_mm'])for c,r in zip(cases,result['cases']));scale_error=max(abs(c['scale_mm_div']-r['cal']['scale_mm_div'])for c,r in zip(cases,result['cases']));wire_error=max(abs(c['parameters']['wire_width_mm']-r['wire']['diameter_mm'])for c,r in zip(cases,result['cases']));telescope_error=max(abs(c['angular_magnification']-v)for c,v in zip(telescopes,result['telescopes']));assert v_error<1e-8 and scale_error<1e-10 and wire_error<1e-10 and telescope_error<1e-12
 tables=[];numbers=[]
 for i in[1,2,3,4]:
  with(exp/f'data/observations-{i:02d}.csv').open(encoding='utf-8-sig',newline='')as file:raw=list(csv.reader(file))
  tables.append({'headers':raw[0],'rows':raw[1:]});numbers.append(np.array([[float(v)for v in r]for r in raw[1:]]))
 microscope=numbers[0][:,2]/numbers[0][:,1];telescope=numbers[1][:,1]/numbers[1][:,2];scale=numbers[2][:,1]/numbers[2][:,2];wire=numbers[3][:,1]*np.mean(scale);analysis={'microscope_magnification':float(np.mean(microscope)),'telescope_magnification':float(np.mean(telescope)),'eyepiece_scale_mm_div':float(np.mean(scale)),'wire_diameter_um':float(np.mean(wire)*1000)};paths=[exp/'experiment.json',exp/'data/provenance.json',*[exp/f'data/observations-{i:02d}.csv'for i in[1,2,3,4]]];hashes={str(p.relative_to(repo)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths};obs={'experiment_id':'course-04/optical-magnification','source':'original-report','tables':tables,'analysis':analysis,'input_hashes':hashes};record={'experiment_id':obs['experiment_id'],'status':'passed','created_at':datetime.now(timezone.utc).isoformat(),'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},'model_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),'input_hashes':hashes,'methods':['ABCD ray-transfer matrix B=0 solved by brentq','image magnification from independent ABCD A element','afocal two-lens telescope angular magnification from ABCD D element','original L/S calibration followed by common mean scale propagation'],'case_count':len(cases)+len(telescopes),'cases':cases,'telescopes':telescopes,'maximum_errors':{'image_distance_mm':v_error,'scale_mm_div':scale_error,'wire_diameter_mm':wire_error,'telescope_magnification':telescope_error},'tolerances':{'image_distance_mm':1e-8,'scale_mm_div':1e-10,'wire_diameter_mm':1e-10,'telescope_magnification':1e-12},'original_observation_analysis':analysis}
 for rel,data in[('simulations/optical-magnification/observations.json',obs),('docs/simulation/optical-magnification-reference.json',record)]:
  path=out/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
 print(json.dumps({'status':'passed','case_count':record['case_count'],'maximum_errors':record['maximum_errors']}))
if __name__=='__main__':main()
