"""Independent Jones projections and numerical dark equal-field roots."""
import argparse,csv,hashlib,json,math,platform,re,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
import scipy
from scipy.optimize import brentq
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1]);parser.add_argument('--output-root',type=Path);parser.add_argument('--model',type=Path);a=parser.parse_args();repo=a.repo_root.resolve();out=(a.output_root or repo).resolve();model=(a.model or repo/'simulations/optical-rotation/model.mjs').resolve();exp=repo/'experiments/course-04/optical-rotation';cases=[]
 def fields(theta,phi,epsilon):
  projection=np.array([math.cos(math.radians(theta)),math.sin(math.radians(theta))]);out=[]
  rotation=np.array([[math.cos(phi),-math.sin(phi)],[math.sin(phi),math.cos(phi)]])
  for sign in[1,-1]:
   input=np.array([math.cos(sign*epsilon),math.sin(sign*epsilon)]);out.append(float(abs(projection@rotation@input)**2))
  return out
 for c in[.01,.1,.2]:
  for l in[.5,2,3]:
   for alpha in[60,66.46,70]:
    phi=alpha*l*c;eps=math.radians(5);root=brentq(lambda theta:fields(theta,math.radians(phi),eps)[0]-fields(theta,math.radians(phi),eps)[1],90+phi-2,90+phi+2,xtol=1e-12);points=[{'angle_deg':theta,'intensities':fields(theta,math.radians(phi),eps)}for theta in[0,45,90,root,180]];cases.append({'parameters':{'concentration_g_ml':c,'tube_length_dm':l,'specific_rotation':alpha,'half_angle_deg':5},'root_deg':root,'points':points})
 script="""import fs from'node:fs';const m=await import(process.argv[1]),d=JSON.parse(fs.readFileSync(0,'utf8'));console.log(JSON.stringify(d.map(c=>({rotation:m.rotation(c.parameters),record:m.measurement(c.parameters),fields:c.points.map(p=>m.halfField(p.angle_deg,c.parameters))}))));""";node=shutil.which('node')or r'C:\Program Files\nodejs\node.exe';result=json.loads(subprocess.run([node,'--input-type=module','-e',script,model.as_uri()],input=json.dumps(cases),text=True,capture_output=True,check=True).stdout);angle_error=max(abs(c['root_deg']-90-r['rotation'])for c,r in zip(cases,result));intensity_error=max(abs(point['intensities'][j]-actual[key])for c,r in zip(cases,result)for point,actual in zip(c['points'],r['fields'])for j,key in enumerate(['left','right']));concentration_error=max(abs(c['parameters']['concentration_g_ml']-r['record']['concentration_g_ml'])for c,r in zip(cases,result));assert angle_error<1e-9 and intensity_error<1e-12 and concentration_error<1e-12
 with(exp/'data/observations-01.csv').open(encoding='utf-8-sig',newline='')as f:raw=list(csv.reader(f))
 def angle(text):
  v=[float(x)for x in re.findall(r'\d+(?:\.\d+)?',text)];return v[0]+v[1]/60
 def diff(a,b):return abs(math.degrees(np.angle(np.exp(1j*math.radians(a-b)))))
 values=[]
 for row in raw[1:]:
  v=[angle(x)for x in row[1:5]];values.append((diff(v[2],v[0])+diff(v[3],v[1]))/2)
 analysis={'rotation_magnitude_deg':float(np.mean(values)),'conditional_concentration_g_ml':float(np.mean(values))/(66.46*2),'type_a_arcmin':float(np.std(values,ddof=1)/math.sqrt(len(values))*60)};paths=[exp/'experiment.json',exp/'data/observations-01.csv',exp/'data/provenance.json'];hashes={str(p.relative_to(repo)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths};obs={'experiment_id':'course-04/optical-rotation','source':'original-report','table':{'headers':raw[0],'rows':raw[1:]},'analysis':analysis,'input_hashes':hashes};record={'experiment_id':obs['experiment_id'],'status':'passed','created_at':datetime.now(timezone.utc).isoformat(),'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},'model_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),'input_hashes':hashes,'methods':['matrix rotation of two linear Jones states and projection','brentq search for dim equal-field root','source circular differences via complex phase'],'case_count':len(cases),'cases':cases,'maximum_errors':{'angle_deg':angle_error,'intensity':intensity_error,'concentration_g_ml':concentration_error},'tolerances':{'angle_deg':1e-9,'intensity':1e-12,'concentration_g_ml':1e-12},'original_observation_analysis':analysis}
 for rel,data in[('simulations/optical-rotation/observations.json',obs),('docs/simulation/optical-rotation-reference.json',record)]:
  path=out/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
 print(json.dumps({'status':'passed','case_count':len(cases),'maximum_errors':record['maximum_errors']}))
if __name__=='__main__':main()
