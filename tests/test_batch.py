import copy,json,sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import batch
from physicslab.common.tex_boxes import tex_boxes

def test_tiny_physical_quantity_disagreement_rejected():
    p={'metrics':{'rho':{'value':1e-12,'unit':'ohm m'}},'tables':{}}
    w=copy.deepcopy(p);w['metrics']['rho']['value']=2e-12
    with pytest.raises(AssertionError):batch.compare(p,w,{'comparison':['rho']})

def test_computed_table_corruption_rejected():
    p={'metrics':{'x':{'value':1.,'unit':'1'}},'tables':{'t':{'headers':['x'],'rows':[[2.]]}}}
    w=copy.deepcopy(p);w['tables']['t']['rows'][0][0]=3.
    with pytest.raises(AssertionError):batch.compare(p,w,{'comparison':['x']})

def test_unit_disagreement_rejected():
    p={'metrics':{'x':{'value':1.,'unit':'m'}},'tables':{}};w=copy.deepcopy(p);w['metrics']['x']['unit']='cm'
    with pytest.raises(ValueError,match='Unit mismatch'):batch.compare(p,w,{'comparison':['x']})

def test_bare_tex_fraction_preserves_two_arguments():
    boxes=tex_boxes(r'\frac12 m v^2')
    assert 'FractionBox["1","2"]' in boxes and '"12"' not in boxes

def test_formula_parentheses_have_local_box_group():
    boxes=tex_boxes(r'u_A(\bar h)=\sqrt{v}')
    assert 'RowBox[{"(",OverscriptBox["h","_"],")"}]' in boxes

def test_registry_has_unique_independent_targets():
    entries=batch.registry();assert len(entries)==45
    for key in ('id','paclet','module'):assert len({e[key] for e in entries})==45
    assert len({e['source_docx'] for e in entries})==45
    assert [sum(e['course']==f'course-{i:02}' for e in entries) for i in range(1,5)]==[8,10,13,14]

@pytest.mark.parametrize('entry',[e for e in batch.registry() if e['slug']!='pendulum'],ids=lambda e:e['id'])
def test_experiment_reference_checks_and_relocated_inputs(entry,tmp_path):
    import importlib,numpy as np,shutil
    adapter=importlib.import_module('physicslab.experiments.'+entry['module']);exp=ROOT/'experiments'/entry['id']
    result=adapter.analyze(exp);a=batch.author(entry)
    json.dumps(result,allow_nan=False)
    for check in a.get('python_checks',[]):
        scope={'result':result,'adapter':adapter,'EXP':exp,'np':np}
        if check.lstrip().startswith('assert '):exec(check,scope)
        else:assert eval(check,scope),check
    copy=tmp_path/'relocated';copy.mkdir();shutil.copy2(exp/'experiment.json',copy/'experiment.json');shutil.copytree(exp/'data',copy/'data')
    moved=adapter.analyze(copy)
    assert moved['metrics']==result['metrics'] and moved['tables']==result['tables']
