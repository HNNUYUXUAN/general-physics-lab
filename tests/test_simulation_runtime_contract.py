"""Registry/agent/provenance contracts for real runtime dependencies.

PHYSICSLAB_REPO_ROOT allows running these contracts
proposal against the public checkout without editing that checkout.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
from types import SimpleNamespace
from urllib.parse import unquote, urlsplit

ROOT=Path(os.environ.get('PHYSICSLAB_REPO_ROOT',Path(__file__).resolve().parents[1]))

def load_script(name):
    spec=importlib.util.spec_from_file_location('contract_'+name,ROOT/'scripts'/f'{name}.py')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

def registry():
    return json.loads((ROOT/'simulations/registry.json').read_text(encoding='utf-8'))['simulations']

def dependencies(entry):
    folder=(ROOT/entry['resources']['simulation_html']).parent
    patterns=(r'''\b(?:import|export)\s+(?:[^;\n]*?\s+from\s*)?["']([^"']+)["']''',
              r'''\bimport\s*\(\s*["']([^"']+)["']''',
              r'''\bfetch\s*\(\s*["']([^"']+)["']''',
              r'''\bnew\s+URL\s*\(\s*["']([^"']+)["']\s*,\s*import\.meta\.url''')
    result=set()
    for module in folder.glob('*.mjs'):
        if module.name.endswith('.test.mjs'):continue
        text=module.read_text(encoding='utf-8')
        for value in {v for pattern in patterns for v in re.findall(pattern,text)}:
            parsed=urlsplit(value)
            assert not parsed.scheme and not parsed.netloc,(entry['slug'],'external dependency',value)
            assert value.startswith(('./','../')),(entry['slug'],'non-relative dependency',value)
            target=(module.parent/unquote(parsed.path)).resolve()
            assert target.is_relative_to(ROOT/'simulations'),(entry['slug'],'dependency escapes simulations',value)
            assert target.is_file(),(entry['slug'],'dependency missing',value)
            result.add(target.relative_to(ROOT).as_posix())
    return result

def test_actual_runtime_dependencies_are_registered():
    for entry in registry():
        if entry['status'] not in {'implemented','validated','published'}:continue
        declared=set(entry['resources'].values())|set(entry.get('public_assets',[]))
        assert dependencies(entry)<=declared,(entry['slug'],'unregistered runtime dependencies',sorted(dependencies(entry)-declared))

def test_agents_can_retrieve_auxiliary_runtime_and_frontend_evidence():
    indexed=load_script('agent_catalog').simulation_resources(ROOT)
    for entry in registry():
        if entry['status'] not in {'validated','published'}:continue
        paths=set(indexed[entry['experiment_id']].values())
        assert dependencies(entry)<=paths,(entry['slug'],'Agent catalog omits runtime dependency',sorted(dependencies(entry)-paths))
        if entry.get('frontend_validation'):
            assert entry['frontend_validation'] in paths,(entry['slug'],'Agent catalog omits frontend evidence')

def test_frontend_hashes_cover_accepted_runtime_dependencies():
    for entry in registry():
        if entry['status']not in {'validated','published'}:continue
        # The approved original pendulum has a separate legacy frontend record.
        if entry['experiment_id']=='course-01/pendulum' and not entry.get('frontend_validation'):continue
        assert entry.get('frontend_validation'),(entry['slug'],'frontend evidence is required')
        record=json.loads((ROOT/entry['frontend_validation']).read_text(encoding='utf-8'))
        values=record['source_hashes']
        required=dependencies(entry)|{entry['resources']['simulation_html']}
        assert required<=values.keys(),(entry['slug'],'frontend hashes omit dependency',sorted(required-values.keys()))
        for path in required:
            assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==values[path],(entry['slug'],'stale frontend dependency',path)

def test_numerical_provenance_binds_changed_helper_even_if_model_is_unchanged(tmp_path,monkeypatch):
    mod=load_script('validate_simulations');root=tmp_path/'root';output=tmp_path/'checks'
    paths={'simulation_model':'simulations/fixture/model.mjs','simulation_controller':'simulations/fixture/app.mjs',
           'simulation_fft':'simulations/fixture/fft.mjs','simulation_validation':'docs/simulation/fixture-reference.json'}
    for path,text in [(paths['simulation_model'],"import {factor} from './fft.mjs'; export const f=()=>factor;"),
                      (paths['simulation_controller'],"import {f} from './model.mjs';"),
                      (paths['simulation_fft'],'export const factor=1;'),
                      ('scripts/validate_fixture.py','# fixture only'),('tests/fixture.test.mjs','// fixture only')]:
        p=root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')
    entry=dict(experiment_id='course-01/fixture',model_version='1.0.0',resources=paths,
               validator='scripts/validate_fixture.py',tests=['tests/fixture.test.mjs'])
    def fake_process(command,**kwargs):
        if '--output-root'in command:
            p=Path(command[command.index('--output-root')+1])/paths['simulation_validation'];p.parent.mkdir(parents=True,exist_ok=True)
            p.write_text(json.dumps({'status':'passed','model_sha256':mod.digest(root/paths['simulation_model'])}),encoding='utf-8')
        return SimpleNamespace(returncode=0,stdout='fixture execution',stderr='')
    monkeypatch.setattr(mod.subprocess,'run',fake_process);monkeypatch.setattr(mod.shutil,'which',lambda _:'node')
    result=mod.validate(root,entry,output)
    assert result['status']=='passed'
    model_before=result['source_files'][paths['simulation_model']]
    helper_before=result['source_files'][paths['simulation_fft']]
    (root/paths['simulation_fft']).write_text('export const factor=2;',encoding='utf-8')
    assert mod.digest(root/paths['simulation_model'])==model_before
    assert mod.digest(root/paths['simulation_fft'])!=helper_before
