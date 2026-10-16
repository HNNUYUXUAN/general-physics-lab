from pathlib import Path
import csv, json, shutil
import numpy as np
import pytest
from physicslab.experiments.pendulum import analyze,load_data,fit_line,period_exact,simulate
from physicslab.common.io import input_hashes

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/'experiments/course-01/pendulum'

@pytest.fixture(scope='module')
def result(): return analyze(EXP)

def test_exact_linear_fixture():
    fit=fit_line([1,2,3,4],[3,5,7,9])
    assert fit['slope']==2 and fit['intercept']==1 and fit['slope_se']==0

def test_degenerate_fit_rejected():
    with pytest.raises(ValueError): fit_line([1,1,1],[1,2,3])

def test_units_and_repeated_observations(result):
    assert result['metrics']['diameter_mean']['value']==pytest.approx(.02)
    first=result['processed'][0]
    assert first['effective_length_m']==pytest.approx(.515)
    assert first['period_s']==pytest.approx((28.78+28.74+28.76)/3/20)
    assert first['period_u_a_s']==pytest.approx(.02/np.sqrt(3)/20)

def test_intercept_invariance_to_shared_radius():
    x=np.array([.5,.6,.7,.8]);y=[2.1,2.4,2.8,3.3]
    assert fit_line(x,y)['slope']==pytest.approx(fit_line(x+.01,y)['slope'])

def test_small_angle_limit():
    assert period_exact(0,1,9.81)==pytest.approx(2*np.pi/np.sqrt(9.81))

@pytest.mark.parametrize('angle,length,gravity',[(np.pi,1,9.81),(0,0,9.81),(0,1,-1)])
def test_period_domain(angle,length,gravity):
    with pytest.raises(ValueError):period_exact(angle,length,gravity)

def test_energy_and_period(result):
    s=result['simulation']
    assert s['relative_energy_drift']<1e-7
    assert s['period_ode_s']==pytest.approx(s['period_exact_s'],rel=1e-7)

def test_amplitude_effect(result):
    rows=result['amplitude_scan']
    assert np.all(np.diff([r['period_s'] for r in rows])>0)
    assert all(r['gravity_bias_pct']<0 for r in rows)

def test_negative_initial_angle_symmetry(result):
    config,_,_=load_data(EXP)
    negative=simulate(config,result['metrics']['gravity_fit']['value'],angle_deg=-20)
    assert negative['period_ode_s']==pytest.approx(result['simulation']['period_ode_s'],rel=1e-8)

def test_reference_fit_uses_raw_times(result):
    # scipy's independent linear-regression implementation checks the local centered formula.
    from scipy.stats import linregress
    rows=result['processed']; fit=linregress([r['effective_length_m'] for r in rows],[r['period_squared_s2'] for r in rows])
    assert result['metrics']['slope']['value']==pytest.approx(fit.slope,rel=1e-12)
    assert result['metrics']['slope_standard_error']['value']==pytest.approx(fit.stderr,rel=1e-8)

def test_input_hashes_cover_provenance(result):
    assert result['input_hashes']==input_hashes(EXP)
    assert 'data/provenance.json' in result['input_hashes']

@pytest.mark.parametrize('problem',['duplicate','missing','negative','length','oscillations','nan'])
def test_invalid_observations(tmp_path,problem):
    copy=tmp_path/'experiment';shutil.copytree(EXP,copy,ignore=shutil.ignore_patterns('results','notebooks','report'))
    path=copy/'data/measurements.csv'
    with path.open(encoding='utf-8',newline='') as f:r=list(csv.DictReader(f))
    columns=list(r[0])
    if problem=='duplicate':r[1]=dict(r[0])
    if problem=='missing':r[0]['elapsed_time_s']=''
    if problem=='negative':r[0]['elapsed_time_s']='-1'
    if problem=='length':r[1]['string_length_cm']='99'
    if problem=='oscillations':r[0]['oscillations']='10'
    if problem=='nan':r[0]['elapsed_time_s']='nan'
    with path.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=columns);w.writeheader();w.writerows(r)
    with pytest.raises(ValueError):load_data(copy)

def test_relocated_data(tmp_path,result):
    destination=tmp_path/'renamed experiment';shutil.copytree(EXP,destination,ignore=shutil.ignore_patterns('results','notebooks','report'))
    moved=analyze(destination)
    assert moved['input_hashes']==result['input_hashes']
    assert moved['metrics']==result['metrics']
