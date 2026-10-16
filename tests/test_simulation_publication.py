"""Keep the virtual experiment executable under a GitHub Pages project prefix."""
import importlib.util
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

from bs4 import BeautifulSoup
import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('simulation_pages_builder', ROOT / 'scripts/build_pages.py')
PAGES = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PAGES)


def _fixture(root):
    (root / 'experiments').mkdir()
    (root / 'experiments/registry.json').write_text(json.dumps({
        'experiments': [{'id': 'course-01/pendulum', 'title': '单摆测重力加速度'}]
    }), encoding='utf-8')
    folder = root / PAGES.SIMULATION
    folder.mkdir(parents=True)
    (folder / 'index.html').write_text('''<!doctype html><html><head>
<link rel="stylesheet" href="./styles.css"></head><body><main>
<h1>单摆虚拟实验</h1><p>$T_0=2\\pi\\sqrt{L/g}$</p>
<script type="module" src="./app.mjs"></script></main></body></html>''', encoding='utf-8')
    (folder / 'app.mjs').write_text("import {period} from './model.mjs';\nfetch(new URL('./scenario.json', import.meta.url));\n", encoding='utf-8')
    (folder / 'model.mjs').write_text('export const period = (length, gravity) => 2 * Math.PI * Math.sqrt(length / gravity);\n', encoding='utf-8')
    (folder / 'styles.css').write_text('body {font-family: "Times New Roman", SimSun, serif;}\n', encoding='utf-8')
    (folder / 'scenario.json').write_text('{"length_m":1,"gravity_m_s2":9.81}\n', encoding='utf-8')
    (folder / 'references.json').write_text('{"references":[]}\n', encoding='utf-8')
    (folder / 'model.test.mjs').write_text('throw new Error("test fixture");', encoding='utf-8')
    (folder / 'research-download.pdf').write_bytes(b'%PDF-local-research')
    (folder / 'README.md').write_text('# Source notes\n', encoding='utf-8')
    return folder


@pytest.mark.parametrize('prefix', ['/general-physics-lab', '/preview/nested', ''])
def test_module_page_uses_project_prefix_and_preserves_runtime_bytes(tmp_path, prefix):
    root = tmp_path / 'root'
    root.mkdir()
    folder = _fixture(root)
    output = tmp_path / 'published'
    builder = PAGES.Builder(root, output, 'https://example.test' + prefix)
    builder.register_simulation()
    builder.build_simulation()
    published = output / PAGES.SIMULATION
    soup = BeautifulSoup((published / 'index.html').read_text(encoding='utf-8'), 'html.parser')
    route = prefix + '/' + PAGES.SIMULATION + '/'
    assert soup.select_one('script[type="module"]')['src'] == route + 'app.mjs'
    assert soup.select_one('link[rel="stylesheet"]')['href'] == route + 'styles.css'
    assert soup.select_one('link[rel="canonical"]')['href'] == 'https://example.test' + route + 'index.html'
    assert soup.select_one('nav.site-nav') and soup.select_one('footer.site-footer')
    assert any(a.get_text() == '虚拟实验' and a['href'] == route + 'index.html' for a in soup.select('nav a'))
    assert len(soup.select('script[src*="/vendor/mathjax-2.7.7/MathJax.js?"]')) == 1
    assert builder.pages == [PAGES.SIMULATION + '/index.html']
    assert builder.source_html == [{'path': PAGES.SIMULATION + '/index.html', 'sha256': PAGES.sha(folder / 'index.html')}]
    for name in ('app.mjs', 'model.mjs', 'styles.css', 'scenario.json', 'references.json'):
        assert (published / name).read_bytes() == (folder / name).read_bytes()
        assert builder.copied[PAGES.SIMULATION + '/' + name] == PAGES.sha(folder / name)
    for name in ('model.test.mjs', 'research-download.pdf', 'README.md'):
        assert not (published / name).exists()
    assert builder.reference('../../../simulations/pendulum/index.html', root / 'experiments/course-01/pendulum/README.md') == route + 'index.html'


def _module_references(text):
    # Imports, literal fetches, and module-relative assets used by the browser runtime.
    patterns = (
        r'''\b(?:import|export)\s+(?:[^;\n]*?\s+from\s*)?["']([^"']+)["']''',
        r'''\bimport\s*\(\s*["']([^"']+)["']''',
        r'''\bfetch\s*\(\s*["']([^"']+)["']''',
        r'''\bnew\s+URL\s*\(\s*["']([^"']+)["']\s*,\s*import\.meta\.url''',
    )
    return {match for pattern in patterns for match in re.findall(pattern, text)}


def test_pendulum_runtime_imports_and_data_assets_are_published(tmp_path):
    builder = PAGES.Builder(ROOT, tmp_path / 'published', 'https://example.test/general-physics-lab')
    builder.register_simulation()
    runtime = [path for path in builder.simulation_files if path.suffix == '.mjs']
    assert runtime, 'The simulation must provide an executable browser module'
    source_folder = (ROOT / 'simulations').resolve()
    for path in builder.simulation_files:
        if path.name != 'index.html':
            builder.copy(path)
    for path in runtime:
        for reference in _module_references(path.read_text(encoding='utf-8')):
            parsed = urlsplit(reference)
            assert not parsed.scheme and not parsed.netloc, (path.name, 'external module/asset', reference)
            assert reference.startswith(('./','../')), (path.name, 'asset must be module relative', reference)
            target = (path.parent / unquote(parsed.path)).resolve()
            assert target.is_relative_to(source_folder), (path.name, 'asset escapes module', reference)
            relative = target.relative_to(ROOT).as_posix()
            assert relative in builder.mapping, (path.name, 'unpublished module asset', reference)
            assert (builder.output / relative).is_file(), (path.name, 'missing published module asset', reference)
            assert (builder.output / relative).read_bytes() == target.read_bytes()


def test_registry_covers_existing_experiments_once():
    registry=json.loads((ROOT/'simulations/registry.json').read_text(encoding='utf-8'))
    original=json.loads((ROOT/'experiments/registry.json').read_text(encoding='utf-8'))
    entries=registry['simulations']
    assert len(entries)==registry['experiment_count']==45
    assert len({e['experiment_id'] for e in entries})==45
    assert {e['experiment_id'] for e in entries}=={e['id'] for e in original['experiments']}
    assert len({e['resources']['simulation_html'] for e in entries})==45
    assert [sum(e['group']==g for e in entries) for g in range(8)]==[1,3,8,8,8,7,7,3]
    for e in entries:
        assert e['status'] in {'queued','research','implemented','validated','published'}
        for rel in [*e['resources'].values(),e['validator'],*e['tests']]:
            assert not Path(rel).is_absolute() and '..' not in Path(rel).parts

def test_acceptance_gate_and_multiple_simulation_routes(tmp_path):
    root=tmp_path/'root';root.mkdir();_fixture(root)
    (root/'simulations/registry.json').write_text(json.dumps({'simulations':[
        {'experiment_id':'course-01/pendulum','title':'单摆','status':'published',
         'evidence_status':'pending','frontend_status':'passed',
         'resources':{'simulation_html':PAGES.SIMULATION+'/index.html'}}]}),encoding='utf-8')
    builder=PAGES.Builder(root,tmp_path/'site','https://example.test/project')
    with pytest.raises(ValueError,match='acceptance'):builder.register_simulation()


def test_frontend_acceptance_rejects_changed_runtime(tmp_path):
    root=tmp_path/'root';root.mkdir();folder=_fixture(root)
    runtime=folder/'app.mjs'
    evidence=root/'docs/frontend.json';evidence.parent.mkdir()
    evidence.write_text(json.dumps({'status':'passed','source_hashes':{runtime.relative_to(root).as_posix():PAGES.sha(runtime)}}),encoding='utf-8')
    (root/'simulations/registry.json').write_text(json.dumps({'simulations':[
      {'experiment_id':'course-01/pendulum','title':'单摆','status':'validated',
       'evidence_status':'verified','frontend_status':'passed','frontend_validation':'docs/frontend.json',
       'resources':{'simulation_html':PAGES.SIMULATION+'/index.html'}}]}),encoding='utf-8')
    runtime.write_text('throw new Error("changed runtime");',encoding='utf-8')
    builder=PAGES.Builder(root,tmp_path/'site','https://example.test/project')
    with pytest.raises(ValueError,match='Frontend acceptance is stale'):builder.register_simulation()
