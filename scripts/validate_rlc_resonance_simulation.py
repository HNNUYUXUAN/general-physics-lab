"""Independent nodal linear-system validation of the browser RLC model."""
import argparse,csv,hashlib,json,math,subprocess
from pathlib import Path
import numpy as np

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--output-root',type=Path);ap.add_argument('--model',type=Path);args=ap.parse_args()
 root=args.repo_root;out=args.output_root or root;model=args.model or root/'simulations/rlc-resonance/model.mjs'
 cases=[]
 for L in [.05,.1,.2]:
  for C in [.1e-6,.2e-6]:
   for R in [20,88.38834764831844,400]:
    for U in [.1,1,5]:
     p=dict(inductance=L,capacitance=C,resistance=R,sourceVoltage=U);f0=1/(2*math.pi*math.sqrt(L*C))
     for ratio in [.2,.5,1,1.5,2.5]:cases.append(dict(parameters=p,frequency=f0*ratio))
 launcher=model.parents[2]/'validation/export_reference_cases.mjs'
 # The script is packaged beside the validator when integrated into scripts/.
 if not launcher.exists(): launcher=Path(__file__).with_name('export_rlc_reference_cases.mjs')
 run=subprocess.run(['node',str(launcher),str(model)],input=json.dumps(cases),text=True,capture_output=True,check=True)
 browser=json.loads(run.stdout);errors={k:0.0 for k in ['current_relative','phase_absolute','voltage_relative','half_power_residual']}
 for case,b in zip(cases,browser):
  p=case['parameters'];w=2*math.pi*case['frequency'];yr=1/p['resistance'];yl=1/(1j*w*p['inductance']);yc=1j*w*p['capacitance']
  # Independent nodal voltages between source-R-L-C-ground.
  v1,v2=np.linalg.solve(np.array([[yr+yl,-yl],[-yl,yl+yc]],dtype=complex),np.array([yr*p['sourceVoltage'],0],dtype=complex))
  current=(p['sourceVoltage']-v1)*yr
  errors['current_relative']=max(errors['current_relative'],abs(abs(current)-b['current'])/abs(current))
  errors['phase_absolute']=max(errors['phase_absolute'],abs(np.angle(current)-b['phase']))
  errors['voltage_relative']=max(errors['voltage_relative'],abs(abs(p['sourceVoltage']-v1)-b['voltageR'])/max(b['voltageR'],1e-12))
  for f in [b['characteristics']['low'],b['characteristics']['high']]:
   ww=2*math.pi*f;normalized=p['resistance']/abs(p['resistance']+1j*(ww*p['inductance']-1/(ww*p['capacitance'])))
   errors['half_power_residual']=max(errors['half_power_residual'],abs(normalized-1/math.sqrt(2)))
 tolerances={'current_relative':2e-12,'phase_absolute':2e-12,'voltage_relative':2e-12,'half_power_residual':2e-12}
 if any(errors[k]>tolerances[k] for k in errors):raise AssertionError(errors)
 source=root/'experiments/course-03/rlc-resonance'
 curves={}
 with (source/'data/response.csv').open(encoding='utf-8',newline='') as fh:
  for row in csv.DictReader(fh):
   for r in ['R1','R2']:curves.setdefault(f"{row['group']}_{r}",[]).append({'frequency':float(row['frequency_Hz']),'voltage':float(row[f'U_{r}_V'])})
 observation={'experimentId':'course-03/rlc-resonance','source':'original-report-observations','sourceFiles':{'response.csv':hashlib.sha256((source/'data/response.csv').read_bytes()).hexdigest()},'units':{'frequency':'Hz','voltage':'V'},'curves':curves}
 obsfile=out/'simulations/rlc-resonance/observations.json';obsfile.parent.mkdir(parents=True,exist_ok=True);obsfile.write_text(json.dumps(observation,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 report={'experimentId':'course-03/rlc-resonance','status':'passed','method':'independent complex nodal linear system (NumPy solve), exact half-power identities','caseCount':len(cases),'modelSha256':hashlib.sha256(model.read_bytes()).hexdigest(),'maxErrors':errors,'tolerances':tolerances,'parameterGrid':{'inductance_H':[.05,.1,.2],'capacitance_F':[.1e-6,.2e-6],'resistance_ohm':[20,88.38834764831844,400],'sourceVoltage_V':[.1,1,5],'frequency_ratio':[.2,.5,1,1.5,2.5]},'numpyVersion':np.__version__}
 dest=out/'docs/simulation/rlc-resonance-reference.json';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
