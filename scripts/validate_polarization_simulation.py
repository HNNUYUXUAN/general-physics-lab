"""Independent NumPy Jones matrices and Fresnel boundary solutions."""
import argparse,csv,hashlib,json,math,platform,re,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
import scipy
from scipy.stats import linregress
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1]);parser.add_argument('--output-root',type=Path);parser.add_argument('--model',type=Path);a=parser.parse_args();repo=a.repo_root.resolve();out=(a.output_root or repo).resolve();model=(a.model or repo/'simulations/polarization/model.mjs').resolve();exp=repo/'experiments/course-04/polarization'
 def read(path):
  with path.open(encoding='utf-8-sig',newline='')as f:return list(csv.reader(f))[1:]
 def angle(text):
  nums=[float(v)for v in re.findall(r'\d+(?:\.\d+)?',text)];return nums[0]+nums[1]/60
 obs={'experiment_id':'course-04/polarization','source':'original-report','brewster':[{'trial':int(r[0]),'as_recorded':r[1],'angle_deg':angle(r[1])}for r in read(exp/'data/observations-01.csv')],'malus':[{'angle_deg':float(r[0]),'current_ma':float(r[1])}for r in read(exp/'data/observations-02.csv')]}
 defaults={'amplitude_ma':1.2,'background_ma':.02,'plate_axis_deg':45,'retardance_deg':0,'refractive_index':1.5};cases=[]
 for amp in[.1,1.2,2]:
  for axis in[0,22.5,45,90]:
   for retard in[0,90]:
    p={**defaults,'amplitude_ma':amp,'plate_axis_deg':axis,'retardance_deg':retard};phi=math.radians(axis);rot=np.array([[math.cos(phi),-math.sin(phi)],[math.sin(phi),math.cos(phi)]]);field=rot@np.diag([1,np.exp(1j*math.radians(retard))])@rot.T@np.array([1,0]);points=[]
    for theta in[0,20,45,90,135,180]:
     analyzer=np.array([math.cos(math.radians(theta)),math.sin(math.radians(theta))]);current=amp*abs(analyzer@field)**2+.02;points.append({'angle_deg':theta,'current_ma':float(current)})
    cases.append({'parameters':p,'points':points})
 reflections=[]
 for n in[1.2,1.5,1.8]:
  for alpha in[0,20,math.degrees(math.atan(n)),85]:
   ai=math.radians(alpha);bt=math.asin(math.sin(ai)/n);ci=math.cos(ai);ct=math.cos(bt);rs,t=np.linalg.solve(np.array([[1,-1],[ci,n*ct]]),np.array([-1,ci]));rp2=((n-1)/(n+1))**2 if alpha==0 else (math.tan(ai-bt)/math.tan(ai+bt))**2;reflections.append({'parameters':{**defaults,'refractive_index':n},'angle_deg':alpha,'rs':float(rs*rs),'rp':rp2})
 script="""import fs from'node:fs';const m=await import(process.argv[1]),d=JSON.parse(fs.readFileSync(0,'utf8'));console.log(JSON.stringify({cases:d.cases.map(c=>c.points.map(r=>m.transmission(r.angle_deg,c.parameters))),reflections:d.reflections.map(r=>m.reflection(r.angle_deg,r.parameters)),fit:m.fitMalus(d.obs.malus.map(r=>({...r,source:'original-report',kind:'transmission',parameters:d.defaults})))}));"""
 node=shutil.which('node')or r'C:\Program Files\nodejs\node.exe';actual=json.loads(subprocess.run([node,'--input-type=module','-e',script,model.as_uri()],input=json.dumps({'cases':cases,'reflections':reflections,'obs':obs,'defaults':defaults}),text=True,capture_output=True,check=True).stdout);current_error=max(abs(point['current_ma']-value)for case,values in zip(cases,actual['cases'])for point,value in zip(case['points'],values));reflection_error=max(abs(case[k]-result[k])for case,result in zip(reflections,actual['reflections'])for k in['rs','rp']);fit=linregress([math.cos(math.radians(r['angle_deg']))**2 for r in obs['malus']],[r['current_ma']for r in obs['malus']]);assert current_error<1e-12 and reflection_error<1e-12;assert abs(actual['fit']['amplitude_ma']-fit.slope)<1e-12 and abs(actual['fit']['background_ma']-fit.intercept)<1e-12
 paths=[exp/'experiment.json',exp/'data/observations-01.csv',exp/'data/observations-02.csv',exp/'data/provenance.json'];hashes={str(p.relative_to(repo)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths};obs['input_hashes']=hashes;mean=np.mean([r['angle_deg']for r in obs['brewster']]);record={'experiment_id':obs['experiment_id'],'status':'passed','created_at':datetime.now(timezone.utc).isoformat(),'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},'model_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),'input_hashes':hashes,'methods':['NumPy complex rotation/retarder matrix and projection','independent s-polarized boundary linear system','independent p Fresnel trigonometric form','SciPy linregress on original photodetector records'],'case_count':len(cases)+len(reflections),'jones_cases':cases,'reflection_cases':reflections,'maximum_errors':{'current_ma':current_error,'reflectance':reflection_error},'tolerances':{'current_ma':1e-12,'reflectance':1e-12},'original_observation_fit':{'amplitude_ma':fit.slope,'background_ma':fit.intercept,'brewster_mean_deg':float(mean),'refractive_index':math.tan(math.radians(mean))}}
 for rel,data in[('simulations/polarization/observations.json',obs),('docs/simulation/polarization-reference.json',record)]:
  path=out/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
 print(json.dumps({'status':'passed','case_count':record['case_count'],'maximum_errors':record['maximum_errors']}))
if __name__=='__main__':main()
