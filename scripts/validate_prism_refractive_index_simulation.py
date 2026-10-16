"""Numerical Snell roots and minimum-deviation search independent of browser asin."""
import argparse,csv,hashlib,json,math,platform,re,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
import scipy
from scipy.optimize import brentq,minimize_scalar
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1]);parser.add_argument('--output-root',type=Path);parser.add_argument('--model',type=Path);a=parser.parse_args();repo=a.repo_root.resolve();out=(a.output_root or repo).resolve();model=(a.model or repo/'simulations/prism-refractive-index/model.mjs').resolve();exp=repo/'experiments/course-04/prism-refractive-index'
 def trace(incident,A,n):
  i=math.radians(incident);ar=math.radians(A);r1=brentq(lambda r:n*math.sin(r)-math.sin(i),0,math.pi/2,xtol=1e-15);r2=ar-r1
  if r2<0 or n*math.sin(r2)>=1:return math.inf
  emergence=brentq(lambda e:math.sin(e)-n*math.sin(r2),0,math.pi/2,xtol=1e-15);return incident+math.degrees(emergence)-A
 cases=[];reference_minima=[]
 for apex in[40,60,70]:
  for n in[1.3,1.5,1.7]:
   center=math.degrees(math.asin(n*math.sin(math.radians(apex)/2)));critical=math.asin(1/n);lower=math.degrees(math.asin(max(0,n*math.sin(max(0,math.radians(apex)-critical)))))+1e-7;opt=minimize_scalar(lambda x:trace(x,apex,n),bounds=(lower,85),method='bounded',options={'xatol':1e-10});reference_minima.append({'apex_deg':apex,'n':n,'min_incidence_deg':float(opt.x),'min_deviation_deg':float(opt.fun)})
   for shift in[-2,0,2]:
    p={'apex_deg':apex,'refractive_index':n,'incidence_deg':center+shift,'zero_deg':359.9,'eccentricity_arcmin':10};target=trace(p['incidence_deg'],apex,n);apparent=math.sin(math.radians(apex+target)/2)/math.sin(math.radians(apex)/2);cases.append({'parameters':p,'deviation_deg':target,'apparent_index':apparent,'shift_deg':shift})
 script="""import fs from'node:fs';const m=await import(process.argv[1]),d=JSON.parse(fs.readFileSync(0,'utf8'));console.log(JSON.stringify(d.map(c=>({forward:m.forward(c.parameters),measurement:m.measurement(c.parameters),minimum:m.minimum(c.parameters)}))));""";node=shutil.which('node')or r'C:\Program Files\nodejs\node.exe';result=json.loads(subprocess.run([node,'--input-type=module','-e',script,model.as_uri()],input=json.dumps(cases),text=True,capture_output=True,check=True).stdout);deviation_error=max(abs(c['deviation_deg']-r['forward']['target_deg'])for c,r in zip(cases,result));index_error=max(abs(c['apparent_index']-r['measurement']['estimate'])for c,r in zip(cases,result));min_error=max(abs(ref['min_deviation_deg']-result[i*3]['minimum']['deviation_deg'])for i,ref in enumerate(reference_minima));assert deviation_error<1e-9 and index_error<1e-10 and min_error<1e-8
 with (exp/'data/observations-01.csv').open(encoding='utf-8-sig',newline='')as f:raw=list(csv.reader(f))
 def angle(s):
  q=[float(v)for v in re.findall(r'\d+(?:\.\d+)?',s)];return q[0]+q[1]/60
 def difference(a,b):return abs(math.degrees(np.angle(np.exp(1j*math.radians(a-b)))))
 values=[]
 for row in raw[1:]:
  v=[angle(s)for s in row[1:5]];values.append((difference(v[2],v[0])+difference(v[3],v[1]))/2)
 mean=float(np.mean(values));analysis={'angle_mean_deg':mean,'type_a_arcmin':float(np.std(values,ddof=1)/math.sqrt(len(values))*60),'refractive_index':math.sin(math.radians(60+mean)/2)/math.sin(math.radians(60)/2),'per_trial_deg':values};paths=[exp/'experiment.json',exp/'data/observations-01.csv',exp/'data/provenance.json'];hashes={str(p.relative_to(repo)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths};obs={'experiment_id':'course-04/prism-refractive-index','source':'original-report','tables':[{'headers':raw[0],'rows':raw[1:]}],'analysis':analysis,'input_hashes':hashes};record={'experiment_id':obs['experiment_id'],'status':'passed','created_at':datetime.now(timezone.utc).isoformat(),'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},'model_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),'input_hashes':hashes,'methods':['two Snell equations solved independently with brentq','minimum deviation searched numerically over transmitting incidence interval','unit complex-number phases for source circular readings'],'case_count':len(cases),'cases':cases,'minimum_searches':reference_minima,'maximum_errors':{'deviation_deg':deviation_error,'apparent_index':index_error,'minimum_deviation_deg':min_error},'tolerances':{'deviation_deg':1e-9,'apparent_index':1e-10,'minimum_deviation_deg':1e-8},'original_observation_analysis':analysis}
 for rel,data in[('simulations/prism-refractive-index/observations.json',obs),('docs/simulation/prism-refractive-index-reference.json',record)]:
  path=out/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
 print(json.dumps({'status':'passed','case_count':len(cases),'max_errors':record['maximum_errors']}))
if __name__=='__main__':main()
