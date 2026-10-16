"""ODE and matrix-fit independent validation of inertial balance model."""
import argparse,csv,hashlib,json,math,subprocess
from pathlib import Path
import numpy as np
import scipy
from scipy.integrate import solve_ivp

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--output-root',type=Path);ap.add_argument('--model',type=Path);args=ap.parse_args();out=args.output_root or args.repo_root;model=args.model or args.repo_root/'simulations/inertial-balance/model.mjs'
 source=args.repo_root/'experiments/course-02/inertial-balance/data/observations-01.csv'
 with source.open(encoding='utf-8-sig',newline='')as f: raw=list(csv.reader(f))
 rows=[dict(mass=float(m)*.001,period=float(t))for m,t in zip(raw[1][1:9],raw[2][1:9])];unknown=dict(nominalMass=.1905,period=float(raw[2][9]));x=np.array([r['mass']for r in rows]);y=np.array([r['period']**2 for r in rows]);design=np.column_stack([x,np.ones(len(x))]);coef=np.linalg.lstsq(design,y,rcond=None)[0];res=y-design@coef;cov=np.linalg.inv(design.T@design)*float(res@res)/(len(x)-2)
 calibration=dict(slope=float(coef[0]),intercept=float(coef[1]),stiffness=float(4*math.pi**2/coef[0]),emptyMass=float(coef[1]/coef[0]))
 cases=[]
 for mass in [0,.1,.25]:
  for k in [10,calibration['stiffness'],40]:
   for amp in [.001,.01]:
    p=dict(mass=mass,emptyMass=calibration['emptyMass'],stiffness=k,amplitude=amp,cycles=20);T=2*math.pi*math.sqrt((mass+p['emptyMass'])/k);times=np.linspace(0,4*T,65)
    def ode(t,s):return[s[1],-k*s[0]/(mass+p['emptyMass'])]
    sol=solve_ivp(ode,[0,4*T],[amp,0],t_eval=times,rtol=2e-12,atol=1e-14,method='DOP853');cases.append(dict(parameters=p,times=times.tolist(),reference=sol.y.T.tolist()))
 code="import{readFileSync}from'node:fs';import{pathToFileURL}from'node:url';const m=await import(pathToFileURL(process.argv[1]));const c=JSON.parse(readFileSync(0,'utf8'));console.log(JSON.stringify({fit:m.calibration(c.rows),cases:c.cases.map(x=>({period:m.period(x.parameters),states:x.times.map(t=>m.state(x.parameters,t))}))}));"
 run=subprocess.run(['node','--input-type=module','-e',code,str(model)],input=json.dumps(dict(rows=rows,cases=cases)),text=True,capture_output=True,check=True);browser=json.loads(run.stdout)
 errors={'ode_position_absolute_m':0.,'ode_velocity_absolute_m_s':0.,'fit_slope_absolute':abs(browser['fit']['slope']-calibration['slope']),'fit_intercept_absolute':abs(browser['fit']['intercept']-calibration['intercept'])}
 for ref,b in zip(cases,browser['cases']):
  for a,s in zip(ref['reference'],b['states']):errors['ode_position_absolute_m']=max(errors['ode_position_absolute_m'],abs(a[0]-s['x']));errors['ode_velocity_absolute_m_s']=max(errors['ode_velocity_absolute_m_s'],abs(a[1]-s['velocity']))
 limits={'ode_position_absolute_m':1e-10,'ode_velocity_absolute_m_s':1e-9,'fit_slope_absolute':1e-12,'fit_intercept_absolute':1e-12}
 if any(errors[k]>limits[k]for k in errors):raise AssertionError(errors)
 observation={'experimentId':'course-02/inertial-balance','source':'original-report-observations','sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'calibration':rows,'unknown':unknown,'calibrationScenario':calibration,'scenarioIdentity':'fitted-from-original-calibration; not independent validation of observed apparatus'}
 dest=out/'simulations/inertial-balance/observations.json';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(observation,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 report={'experimentId':'course-02/inertial-balance','status':'passed','method':'DOP853 oscillator integration and matrix least squares independent of browser implementation','caseCount':len(cases),'samplesPerCase':65,'maxErrors':errors,'tolerances':limits,'modelSha256':hashlib.sha256(model.read_bytes()).hexdigest(),'scipyVersion':scipy.__version__,'calibration':calibration}
 dest=out/'docs/simulation/inertial-balance-reference.json';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
