"""NumPy FFT2, independent pupil operations, and doubled-grid convergence."""
import argparse,csv,hashlib,json,math,platform,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1]);parser.add_argument('--output-root',type=Path);parser.add_argument('--model',type=Path);a=parser.parse_args();repo=a.repo_root.resolve();out=(a.output_root or repo).resolve();model=(a.model or repo/'simulations/abbe-imaging/model.mjs').resolve();exp=repo/'experiments/course-04/abbe-imaging';cases=[];modes=['open','circle','zero-only','horizontal-slit','vertical-slit','block-zero']
 for cycles in[8,16,32]:
  for wave in[500,632.8,700]:
   for focal in[100,150,200]:
    idx=len(cases);cases.append({'wavelength_nm':wave,'focal_length_mm':focal,'field_length_mm':4,'cycles':cycles,'pupil_radius_mm':[.1,.4,.8][idx%3],'filter':modes[idx%6],'grid_size':128})
 def reference(p):
  n=p['grid_size'];x=(np.arange(n)/n-.5)*4;xx,yy=np.meshgrid(x,x);obj=.5+.2*np.cos(2*np.pi*p['cycles']*xx/4)+.2*np.cos(2*np.pi*p['cycles']*yy/4);freq=np.fft.fftfreq(n,d=4/n);fx,fy=np.meshgrid(freq,freq);xi=fx*p['wavelength_nm']*1e-6*p['focal_length_mm'];eta=fy*p['wavelength_nm']*1e-6*p['focal_length_mm'];r=np.hypot(xi,eta);mode=p['filter'];mask=np.ones_like(r)if mode=='open'else (r<=p['pupil_radius_mm']+1e-12)if mode=='circle'else (r<=.05)if mode=='zero-only'else(np.abs(eta)<=.05)if mode=='horizontal-slit'else(np.abs(xi)<=.05)if mode=='vertical-slit'else(r>.05);return obj,np.fft.ifft2(np.fft.fft2(obj)*mask)
 script="""import fs from'node:fs';const m=await import(process.argv[1]),d=JSON.parse(fs.readFileSync(0,'utf8'));console.log(JSON.stringify(d.map((p,i)=>{const a=m.analyze(p);let fine=null;if([0,13,26].includes(i)){const b=m.analyze({...p,grid_size:256}),re=[],im=[];for(let j=0;j<128;j++)for(let k=0;k<128;k++){re.push(b.image.re[j*2*256+k*2]);im.push(b.image.im[j*2*256+k*2]);}fine={re,im};}return{re:[...a.image.re],im:[...a.image.im],metrics:a.metrics,fine};})));""";node=shutil.which('node')or r'C:\Program Files\nodejs\node.exe';result=json.loads(subprocess.run([node,'--input-type=module','-e',script,model.as_uri()],input=json.dumps(cases),text=True,capture_output=True,check=True).stdout);field_error=0;energy_error=0;convergence_error=0
 for p,r in zip(cases,result):
  obj,image=reference(p);actual=np.array(r['re'])+1j*np.array(r['im']);field_error=max(field_error,float(np.max(np.abs(image.ravel()-actual))));energy=float(np.sum(abs(image)**2)/np.sum(obj**2));energy_error=max(energy_error,abs(energy-r['metrics']['transmitted_energy_fraction']));
  if r['fine'] is not None:convergence_error=max(convergence_error,float(np.max(np.abs(actual-(np.array(r['fine']['re'])+1j*np.array(r['fine']['im']))))))
 assert field_error<1e-10 and energy_error<1e-10 and convergence_error<1e-10
 tables=[]
 for i in[1,2]:
  with(exp/f'data/observations-{i:02d}.csv').open(encoding='utf-8-sig',newline='')as f:raw=list(csv.reader(f))
  tables.append({'headers':raw[0],'rows':raw[1:]})
 spectrum=np.array([[float(v)for v in r]for r in tables[0]['rows']]);position=float(np.mean(abs(spectrum[abs(spectrum[:,0])==1,1])));analysis={'first_order_mean_abs_mm':position,'period_mm':632.8e-6*150/position};paths=[exp/'experiment.json',exp/'data/observations-01.csv',exp/'data/observations-02.csv',exp/'data/provenance.json'];hashes={str(p.relative_to(repo)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths};obs={'experiment_id':'course-04/abbe-imaging','source':'original-report','tables':tables,'analysis':analysis,'input_hashes':hashes};fftpath=model.parent/'fft.mjs';record={'experiment_id':obs['experiment_id'],'status':'passed','created_at':datetime.now(timezone.utc).isoformat(),'environment':{'python':platform.python_version(),'numpy':np.__version__},'model_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),'fft_sha256':hashlib.sha256(fftpath.read_bytes()).hexdigest(),'input_hashes':hashes,'methods':['NumPy complex FFT2 and independently constructed physical Fourier-plane pupil','pointwise full complex-field comparison','128to256 grid-doubling comparison at common sample locations','analytic Fourier coefficients and Parseval checks in Node tests'],'case_count':len(cases),'cases':cases,'maximum_errors':{'complex_field':field_error,'energy_fraction':energy_error,'grid_doubling_complex_field':convergence_error},'tolerances':{'complex_field':1e-10,'energy_fraction':1e-10,'grid_doubling_complex_field':1e-10},'original_observation_analysis':analysis}
 for rel,data in[('simulations/abbe-imaging/observations.json',obs),('docs/simulation/abbe-imaging-reference.json',record)]:
  path=out/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
 print(json.dumps({'status':'passed','case_count':len(cases),'maximum_errors':record['maximum_errors']}))
if __name__=='__main__':main()
