"""ABCD matrix and independent ray intersection verification."""
import argparse,csv,hashlib,json,math,subprocess
from pathlib import Path
import numpy as np
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--output-root',type=Path);ap.add_argument('--model',type=Path);a=ap.parse_args();out=a.output_root or a.repo_root;model=a.model or a.repo_root/'simulations/thin-lens/model.mjs'
 cases=[{'f':f,'u':f*q,'D':f*d}for f in[.05,.10008427569062277,.2]for q in[.5,.99,1,1.01,2,4]for d in[3,4,4.0001,5,8]]
 code="import{readFileSync}from'node:fs';import{pathToFileURL}from'node:url';const m=await import(pathToFileURL(process.argv[1]));const cs=JSON.parse(readFileSync(0,'utf8'));console.log(JSON.stringify(cs.map(c=>({c:m.conjugates(c.f,c.u),b:m.bessel(c.f,c.D)}))));"
 run=subprocess.run(['node','--input-type=module','-e',code,str(model)],input=json.dumps(cases),text=True,capture_output=True,check=True);bs=json.loads(run.stdout);errs={'ABCD_B_absolute_m':0.,'image_magnification_absolute':0.,'bessel_focus_B_absolute_m':0.};counts={'real':0,'virtual':0,'collimated':0,'bessel_none':0,'bessel_single':0,'bessel_two':0}
 P=lambda d:np.array([[1.,d],[0.,1.]])
 for case,b in zip(cases,bs):
  f,u,D=case['f'],case['u'],case['D'];lens=np.array([[1.,0],[-1/f,1.]])
  if b['c']['v'] is None:
   # Equal input object height, distinct incident angles: output angles identical at u=f.
   out_matrix=lens@P(u);assert abs(out_matrix[1,1])<1e-12;counts['collimated']+=1
  else:
   v=b['c']['v'];matrix=P(v)@lens@P(u);errs['ABCD_B_absolute_m']=max(errs['ABCD_B_absolute_m'],abs(float(matrix[0,1])));errs['image_magnification_absolute']=max(errs['image_magnification_absolute'],abs(float(matrix[0,0])-b['c']['magnification']));counts[b['c']['type']]+=1
  if D<4*f:assert not b['b']['positions'];counts['bessel_none']+=1
  else:
   counts['bessel_single'if D==4*f else'bessel_two']+=1
   for pos in b['b']['positions']:errs['bessel_focus_B_absolute_m']=max(errs['bessel_focus_B_absolute_m'],abs(float((P(D-pos)@lens@P(pos))[0,1])))
 limits={k:1e-11 for k in errs}
 if any(errs[k]>limits[k]for k in errs):raise AssertionError(errs)
 data=a.repo_root/'experiments/course-04/thin-lens/data';methods={};hashes={}
 for name in['autocollimation','conjugates','bessel','concave']:
  file=data/f'{name}.csv';hashes[file.name]=hashlib.sha256(file.read_bytes()).hexdigest()
  with file.open(encoding='utf-8-sig',newline='')as fh:rows=[[float(v)for v in row.values()]for row in csv.DictReader(fh)]
  fs=[];processed=[]
  for row in rows:
   if name=='autocollimation':f=row[1];processed.append(row)
   elif name=='conjugates':f=row[1]*row[2]/(row[1]+row[2]);processed.append(row+[f])
   elif name=='bessel':f=(row[1]**2-row[2]**2)/(4*row[1]);processed.append(row+[f])
   else:f=-row[1]*row[2]/(row[2]-row[1]);processed.append(row+[f])
   fs.append(f)
  headers={'autocollimation':['组次','f / cm'],'conjugates':['组次','u / cm','v / cm','f / cm'],'bessel':['组次','D / cm','d / cm','f / cm'],'concave':['组次','a / cm','b / cm','f / cm']}[name]
  methods[name]={'headers':headers,'rows':processed,'mean_cm':float(np.mean(fs)),'type_a_cm':float(np.std(fs,ddof=1)/math.sqrt(len(fs)))}
 obs={'experimentId':'course-04/thin-lens','source':'original-report-observations','sourceHashes':hashes,'methods':methods,'units':'cm'};dest=out/'simulations/thin-lens/observations.json';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(obs,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 report={'experimentId':'course-04/thin-lens','status':'passed','method':'independent NumPy ABCD ray transfer matrices','caseCount':len(cases),'scenarios':counts,'maxErrors':errs,'tolerances':limits,'modelSha256':hashlib.sha256(model.read_bytes()).hexdigest(),'numpyVersion':np.__version__};dest=out/'docs/simulation/thin-lens-reference.json';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
