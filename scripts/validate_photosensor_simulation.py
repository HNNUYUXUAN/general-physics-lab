"""Independent nodal KCL linear solves and source circuit consistency."""
import argparse,csv,hashlib,json,platform,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1]);parser.add_argument('--output-root',type=Path);parser.add_argument('--model',type=Path);a=parser.parse_args();repo=a.repo_root.resolve();out=(a.output_root or repo).resolve();model=(a.model or repo/'simulations/photosensor/model.mjs').resolve();exp=repo/'experiments/course-03/photosensor';cases=[]
 for Ee in[0,.5,1]:
  for feedback in[1,50,200]:
   for zero in[-.1,0,.1]:
    p={'irradiance_mw_cm2':Ee,'feedback_kohm':feedback,'zero_current_ua':zero,'wavelength_nm':950,'reverse_bias_v':5,'temperature_c':25,'linear_output_limit_v':4.5};matrix=np.array([[1.,0.],[feedback*1000,1.]]);rhs=np.array([(50*Ee+zero)*1e-6,0.]);current,voltage=np.linalg.solve(matrix,rhs);dark=np.linalg.solve(matrix,np.array([zero*1e-6,0.]))[1];cases.append({'parameters':p,'current_ua':float(current*1e6),'ideal_output_v':float(voltage),'dark_output_v':float(dark),'linear_valid':bool(abs(voltage)<=4.5)})
 script="""import fs from'node:fs';const m=await import(process.argv[1]),d=JSON.parse(fs.readFileSync(0,'utf8'));console.log(JSON.stringify(d.map(c=>{const p=c.parameters,point=m.workingPoint(p),zero=m.zeroCalibration(p);return{point,zero,record:point.linear_valid?m.measurement(p,zero):null};})));""";node=shutil.which('node')or r'C:\Program Files\nodejs\node.exe';result=json.loads(subprocess.run([node,'--input-type=module','-e',script,model.as_uri()],input=json.dumps(cases),text=True,capture_output=True,check=True).stdout);voltage_error=0;current_error=0;invalid=0
 for c,r in zip(cases,result):
  assert c['linear_valid']==r['point']['linear_valid'];voltage_error=max(voltage_error,abs(c['ideal_output_v']-r['point']['ideal_output_v']),abs(c['dark_output_v']-r['zero']['raw']['output_v']))
  if c['linear_valid']:current_error=max(current_error,abs(r['record']['derived']['corrected_photo_current_ua']-50*c['parameters']['irradiance_mw_cm2']))
  else:assert r['point']['output_v']is None;invalid+=1
 assert voltage_error<1e-12 and current_error<1e-10
 with(exp/'data/measurements.csv').open(encoding='utf-8-sig',newline='')as f:raw=list(csv.DictReader(f))
 assert len(raw)==56
 rows=[]
 for r in raw:
  position=int(r['position_cm']);load=float(r['load_kOhm']);voltage=float(r['output_V']);sample=float(r['sample_mV']);current=sample/10;expected=current*.001*(load*1000+10);rows.append({'position_cm':position,'load_kohm':load,'output_v':voltage,'sample_mv':sample,'current_ma':current,'circuit_prediction_v':expected,'circuit_difference_v':voltage-expected})
 analysis={'maximum_circuit_relative_difference_percent':max(abs(r['circuit_difference_v']/r['output_v'])*100 for r in rows)};paths=[exp/'experiment.json',exp/'data/measurements.csv',exp/'data/provenance.json'];hashes={str(p.relative_to(repo)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths};obs={'experiment_id':'course-03/photosensor','source':'original-report','rows':rows,'analysis':analysis,'input_hashes':hashes};record={'experiment_id':obs['experiment_id'],'status':'passed','created_at':datetime.now(timezone.utc).isoformat(),'environment':{'python':platform.python_version(),'numpy':np.__version__},'model_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),'input_hashes':hashes,'device_basis':{'model':'Vishay BPW34','document':'81521 Rev2.1 23-Aug-2011','test_conditions':{'wavelength_nm':950,'reverse_bias_v':5,'temperature_c':25,'irradiance_mw_cm2':1,'typical_current_ua':50}},'methods':['independent nodal KCL linear system for ideal transimpedance stage','independent dark baseline linear solve and subtraction','explicit linear-output-bound invalid-point classification','source10Ohm sample current and circuit voltage recomputation'],'case_count':len(cases),'cases':cases,'overrange_case_count':invalid,'maximum_errors':{'voltage_v':voltage_error,'corrected_current_ua':current_error},'tolerances':{'voltage_v':1e-12,'corrected_current_ua':1e-10},'original_observation_analysis':analysis}
 for rel,data in[('simulations/photosensor/observations.json',obs),('docs/simulation/photosensor-reference.json',record)]:
  path=out/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
 print(json.dumps({'status':'passed','case_count':len(cases),'overrange_cases':invalid,'maximum_errors':record['maximum_errors']}))
if __name__=='__main__':main()
