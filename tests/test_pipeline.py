from pathlib import Path
import shutil,sys,json
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import pipeline

@pytest.fixture
def comparison_copy(tmp_path,monkeypatch):
    exp=tmp_path/'experiment'
    shutil.copytree(ROOT/'experiments/course-01/pendulum',exp)
    monkeypatch.setattr(pipeline,'EXP',exp)
    monkeypatch.setattr(pipeline,'RESULTS',exp/'results')
    return exp

def test_stale_data_prevents_report(comparison_copy):
    path=comparison_copy/'data/measurements.csv'
    path.write_text(path.read_text(encoding='utf-8').replace('28.78','28.79'),encoding='utf-8')
    original=(comparison_copy/'report/report.md').read_bytes()
    with pytest.raises(ValueError,match='Stale input'):pipeline.render_report()
    assert (comparison_copy/'report/report.md').read_bytes()==original

def test_unit_mismatch_rejected(comparison_copy):
    path=comparison_copy/'results/wolfram.json'
    data=json.loads(path.read_text(encoding='utf-8-sig'));data['metrics']['gravity_fit']['unit']='cm/s^2'
    path.write_text(json.dumps(data),encoding='utf-8')
    with pytest.raises(ValueError,match='units'):pipeline.compare()

def test_numerical_disagreement_rejected(comparison_copy):
    path=comparison_copy/'results/wolfram.json'
    data=json.loads(path.read_text(encoding='utf-8-sig'));data['metrics']['gravity_fit']['value']+=.1
    path.write_text(json.dumps(data),encoding='utf-8')
    with pytest.raises(AssertionError):pipeline.compare()
    assert json.loads((comparison_copy/'results/verification.json').read_text(encoding='utf-8'))['status']=='failed'
