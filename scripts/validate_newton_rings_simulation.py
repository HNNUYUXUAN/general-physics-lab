"""Compare browser Newton-ring calculations with independent SciPy references."""
from __future__ import annotations
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import platform
import shutil
import subprocess
import numpy as np
import scipy
from scipy.optimize import minimize_scalar
from scipy.stats import linregress

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')

def rows(path):
    with path.open(encoding='utf-8-sig', newline='') as file:
        return [{k:float(v) for k,v in row.items()} for row in csv.DictReader(file)]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output-root', type=Path)
    parser.add_argument('--model', type=Path)
    args=parser.parse_args()
    repo=args.repo_root.resolve(); out=(args.output_root or repo).resolve()
    model=(args.model or repo/'simulations/newton-rings/model.mjs').resolve()
    exp=repo/'experiments/course-04/newton-rings'
    config=json.loads((exp/'experiment.json').read_text(encoding='utf-8-sig'))
    rings=rows(exp/'data/rings.csv'); wedge=rows(exp/'data/wedge.csv')
    assert len(rings)==6 and len(wedge)==5
    assert len({r['order'] for r in rings})==6
    rings=[{**r,'order':int(r['order'])} for r in rings]
    wave=config['parameters']['wavelength_nm']
    obs={'experiment_id':'course-04/newton-rings','source':'original-report','data_version':config['data_version'],'wavelength_nm':wave,'rings':rings,'wedge':[{'trial':int(r['trial']),'intervals':int(r['fringe_intervals']),'fringe_length_mm':r['fringe_length_mm'],'wedge_length_mm':r['wedge_length_mm']} for r in wedge],'provenance':{'primary_source':config['source_docx'],'input_hashes':{str(p.relative_to(repo)).replace('\\','/'):sha(p) for p in [exp/'experiment.json',exp/'data/rings.csv',exp/'data/wedge.csv',exp/'data/provenance.json']}}}
    cases=[]
    # Independent minima are found in optical phase, not by using darkRadius.
    for radius in [300,800,1500]:
        for wavelength in [400,589.3,700]:
            for gap in [0,.1,.25,.5]:
                orders=[2,5,10,15,20,25,30]
                reference=[]
                for order in orders:
                    phase=minimize_scalar(lambda q:math.sin(math.pi*q)**2,bounds=(order-.45,order+.45),method='bounded',options={'xatol':1e-12}).x
                    rad=math.sqrt(radius*wavelength*1e-6*(phase-2*gap))
                    reference.append({'order':order,'radius_mm':rad})
                p={'radius_mm':radius,'wavelength_nm':wavelength,'gap_fraction':gap,'center_mm':25}
                cases.append({'parameters':p,'rings':reference})
    payload={'cases':cases,'observations':obs}
    script="""import fs from 'node:fs'; const m=await import(process.argv[1]);const d=JSON.parse(fs.readFileSync(0,'utf8'));console.log(JSON.stringify({cases:d.cases.map(c=>{const rows=c.rings.map(r=>m.measurement(r.order,c.parameters));return {radii:c.rings.map(r=>m.darkRadius(r.order,c.parameters)),intensities:c.rings.map(r=>m.intensity(r.radius_mm,0,c.parameters)),fit:m.fitMeasurements(rows,c.parameters.wavelength_nm),pairs:m.pairDifferences(rows,10,c.parameters.wavelength_nm)};}),observed:m.fitMeasurements(d.observations.rings,d.observations.wavelength_nm),wedge:d.observations.wedge.map(r=>m.wedgeThickness(r,d.observations.wavelength_nm))}));"""
    node=shutil.which('node') or r'C:\Program Files\nodejs\node.exe'
    result=json.loads(subprocess.run([node,'--input-type=module','-e',script,model.as_uri()],input=json.dumps(payload),text=True,capture_output=True,check=True).stdout)
    maxima={'radius_absolute_mm':0.,'dark_intensity':0.,'fit_radius_absolute_mm':0.,'fit_gap_absolute_nm':0.,'pair_radius_absolute_mm':0.,'sphere_thickness_relative':0.}
    for c,b in zip(cases,result['cases']):
        p=c['parameters']
        for ref,actual,value in zip(c['rings'],b['radii'],b['intensities']):
            maxima['radius_absolute_mm']=max(maxima['radius_absolute_mm'],abs(ref['radius_mm']-actual))
            maxima['dark_intensity']=max(maxima['dark_intensity'],value)
        maxima['fit_radius_absolute_mm']=max(maxima['fit_radius_absolute_mm'],abs(b['fit']['radius_mm']-p['radius_mm']))
        maxima['fit_gap_absolute_nm']=max(maxima['fit_gap_absolute_nm'],abs(b['fit']['gap_from_intercept_nm']-p['gap_fraction']*p['wavelength_nm']))
        for pair in b['pairs']:
            maxima['pair_radius_absolute_mm']=max(maxima['pair_radius_absolute_mm'],abs(pair['radius_mm']-p['radius_mm']))
        r2=50.; exact=r2/(p['radius_mm']+math.sqrt(p['radius_mm']**2-r2)); paraxial=r2/(2*p['radius_mm'])
        maxima['sphere_thickness_relative']=max(maxima['sphere_thickness_relative'],(exact-paraxial)/exact)
    # SciPy least squares on actual readings, independent of browser implementation.
    orders=np.array([r['order'] for r in rings]); diameter=np.array([r['right_mm']-r['left_mm'] for r in rings]); fit=linregress(orders,diameter**2)
    reference_radius=fit.slope/(4*wave*1e-6)
    assert abs(result['observed']['radius_mm']-reference_radius)<1e-9
    assert abs(result['observed']['radius_residual_se_mm']-fit.stderr/(4*wave*1e-6))<1e-8
    thickness=np.array([r['fringe_intervals']*wave*1e-6*r['wedge_length_mm']/(2*r['fringe_length_mm']) for r in wedge])
    assert np.max(np.abs(thickness-np.array(result['wedge'])))<1e-15
    tolerances={'radius_absolute_mm':1e-6,'dark_intensity':1e-12,'fit_radius_absolute_mm':1e-8,'fit_gap_absolute_nm':1e-8,'pair_radius_absolute_mm':1e-8,'sphere_thickness_relative':1.4e-4}
    for k,v in maxima.items():
        assert v<tolerances[k],f'{k}: {v} exceeds {tolerances[k]}'
    # Grid step .005 mm: each coordinate phase increment stays below Nyquist.
    maximum_axis_phase_step=4*math.pi*5*.005/(300*400e-6)
    assert maximum_axis_phase_step<math.pi
    record={'experiment_id':'course-04/newton-rings','status':'passed','created_at':datetime.now(timezone.utc).isoformat(),'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},'model_sha256':sha(model),'input_hashes':obs['provenance']['input_hashes'],'reference_methods':['SciPy bounded minimization of reflected intensity in optical phase','SciPy linregress on original left/right readings','exact spherical sag compared with paraxial film thickness'],'cases':cases,'case_count':len(cases),'dark_ring_count':sum(len(c['rings']) for c in cases),'max_errors':maxima,'tolerances':tolerances,'grid':{'size':2001,'extent_mm':5,'maximum_axis_phase_step_rad':maximum_axis_phase_step,'nyquist_rad':math.pi},'original_observation_fit':{'radius_mm':reference_radius,'radius_residual_se_mm':fit.stderr/(4*wave*1e-6),'intercept_mm2':fit.intercept},'wedge':{'mean_um':float(thickness.mean()*1000),'type_a_mean_um':float(thickness.std(ddof=1)/math.sqrt(len(thickness))*1000)}}
    write(out/'simulations/newton-rings/observations.json',obs);write(out/'docs/simulation/newton-rings-reference.json',record)
    print(json.dumps({'status':'passed','case_count':len(cases),'dark_ring_count':record['dark_ring_count'],'max_errors':maxima},ensure_ascii=False))

if __name__=='__main__': main()
