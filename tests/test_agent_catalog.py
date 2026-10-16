"""Exercise discovery against physical questions and source identity."""
from pathlib import Path
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from agent_catalog import compile_catalog, read_json, resource, search, card, SIMULATION_RESOURCES
from check_agent_docs import validate


@pytest.fixture(scope='module')
def catalog():
    return read_json(ROOT / 'docs/experiments.json')


@pytest.mark.parametrize('query,expected', [
    ('重力加速度', 'course-01/pendulum'),
    ('RLC bandwidth', 'course-03/rlc-resonance'),
    ('pycnometer', 'course-01/density'),
    ('弹簧动静态', 'course-01/doppler-application'),
    ('全息照相', 'course-04/holography'),
    ('Newton rings', 'course-04/newton-rings'),
    ('衍射 缝宽', 'course-04/single-slit-diffraction'),
    ('Kelvin bridge', 'course-03/kelvin-bridge'),
    ('diffraction grating', 'course-04/transmission-grating'),
    ('uncertainty propagation', 'course-01/density'),
    ('C02_R1_Q_bandwidth', 'course-03/rlc-resonance'),
])
def test_physics_questions_retrieve_expected_experiment(catalog, query, expected):
    assert expected in [entry['id'] for entry in search(catalog, query)]


def test_search_respects_course_and_all_query_terms(catalog):
    assert search(catalog, 'pendulum', course='course-04') == []
    assert search(catalog, 'RLC不存在的实验名称') == []


def test_english_acronym_is_not_a_substring_of_model_or_diode(catalog):
    found = search(catalog, 'ODE', limit=45)
    assert [entry['id'] for entry in found] == ['course-01/pendulum']


@pytest.mark.parametrize('extension', ['.md', '.mjs', '.css', '.html', '.json', '.bib'])
def test_text_content_identity_survives_checkout_line_endings(tmp_path, extension):
    path = tmp_path / ('guide' + extension)
    path.write_bytes('标题\r\n正文\r\n'.encode('utf-8'))
    windows = resource(path, tmp_path)
    path.write_bytes('标题\n正文\n'.encode('utf-8'))
    assert resource(path, tmp_path) == windows
    assert windows['hash_basis'] == 'utf8-lf'


def test_source_pdf_mismatch_is_rejected(monkeypatch):
    # A corrupted source mapping must fail even when the filename still exists.
    import agent_catalog
    original = agent_catalog.resource
    def altered(path, root=ROOT):
        value = original(path, root)
        if value['path'].endswith('.pdf'):
            value['sha256'] = '0' * 64
        return value
    monkeypatch.setattr(agent_catalog, 'resource', altered)
    with pytest.raises(AssertionError, match='PDF hash'):
        compile_catalog()


def test_discovery_bundle_matches_sources_and_schema():
    assert validate()['experiments'] == 45


def test_registered_simulation_resources_are_discoverable(catalog):
    from agent_catalog import simulation_resources
    registered=simulation_resources()
    for entry in catalog['experiments']:
        expected=registered.get(entry['id'],{})
        assert {key:entry['resources'][key]['path'] for key in expected}==expected
        if expected:
            assert entry['resources']['simulation_html']['online_url'] in card(entry,compact=True)
            for key in ('simulation_model','simulation_controller','simulation_charts','simulation_styles','references_bibtex'):
                assert entry['resources'][key]['hash_basis']=='utf8-lf'
        else:assert 'simulation_html' not in entry['resources']
