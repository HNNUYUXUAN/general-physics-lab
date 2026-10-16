"""Validate discovery metadata, local links and catalog/source consistency."""
import json
import hashlib
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

import markdown
from bs4 import BeautifulSoup
from jsonschema import Draft202012Validator, FormatChecker
from markdown.extensions.toc import slugify_unicode
import yaml

from agent_catalog import ROOT, REPO, RAW, GENERATED, compile_catalog, documents, read_json, resource

MANUAL = ('AGENTS.md', 'docs/agent-guide.md', 'docs/agent-reproduction.md',
          'docs/agent-catalog.md', 'docs/discovery.md', 'docs/virtual-lab-development.md',
          'docs/virtual-lab-agent-guide.md', 'docs/pendulum-model-evidence.md')


def target_for_url(url, source):
    parsed = urlsplit(url)
    for prefix in (RAW, REPO + '/blob/main/', REPO + '/tree/main/'):
        if url.startswith(prefix):
            return ROOT / unquote(urlsplit(url[len(prefix):]).path), unquote(parsed.fragment)
    if parsed.scheme or parsed.netloc:
        return None, ''
    return ((source.parent / unquote(parsed.path)).resolve() if parsed.path else source), unquote(parsed.fragment)


def check_links(path):
    text = path.read_text(encoding='utf-8')
    assert not re.search(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', text), (path, 'Control character')
    assert text.count('```') % 2 == 0, (path, 'Unbalanced code fence')
    soup = BeautifulSoup(markdown.markdown(text, extensions=['tables', 'fenced_code']), 'html.parser')
    count = 0
    for element in soup.select('a[href],img[src]'):
        url = element.get('href', element.get('src'))
        target, anchor = target_for_url(url, path)
        if target is None:
            continue
        assert target.resolve().is_relative_to(ROOT.resolve()), (path, 'Outside repository', url)
        assert target.exists(), (path, 'Missing linked target', url)
        if anchor and target.suffix in ('.md', '.txt'):
            headings = re.findall(r'^#{1,6}\s+(.+)$', target.read_text(encoding='utf-8'), re.M)
            assert anchor in {slugify_unicode(h, '-') for h in headings}, (path, 'Missing anchor', url)
        count += 1
    return count


def validate():
    catalog = read_json(ROOT / 'docs/experiments.json')
    schema = read_json(ROOT / 'docs/schemas/experiments.schema.json')
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(catalog)
    expected = documents(compile_catalog())
    for relative, text in expected.items():
        assert (ROOT / relative).read_text(encoding='utf-8') == text, ('Stale discovery file', relative)
    ids = [e['id'] for e in catalog['experiments']]
    assert len(ids) == len(set(ids)) == catalog['experiment_count']
    resources = metrics = 0
    for entry in catalog['experiments']:
        for item in [*entry['resources'].values(), *(d['resource'] for d in entry['data_files'])]:
            assert resource(item['path']) == item, ('Stale resource', item['path'])
            resources += 1
        result = read_json(ROOT / entry['resources']['python_results']['path'])
        for metric in entry['key_results']:
            assert {key: value for key, value in metric.items() if key not in ('key', 'result_pointer', 'description')} == result['metrics'][metric['key']]
            metrics += 1
        if 'simulation_validation' in entry['resources']:
            reference = read_json(ROOT / entry['resources']['simulation_validation']['path'])
            identity=reference.get('experiment_id',reference.get('experimentId',reference.get('experiment')))
            assert identity == entry['id'], ('Simulation reference identity', entry['id'])
            if 'simulation_model' in entry['resources']:
                model = ROOT / entry['resources']['simulation_model']['path']
                expected_hash=reference.get('model_sha256',reference.get('modelSha256',reference.get('browser_verification',{}).get('model_sha256')))
                assert hashlib.sha256(model.read_bytes()).hexdigest() == expected_hash, ('Stale simulation model verification', model)
        if 'simulation_observations' in entry['resources']:
            observations = read_json(ROOT / entry['resources']['simulation_observations']['path'])
            identity=observations.get('experiment_id',observations.get('experimentId',observations.get('experiment')))
            assert identity == entry['id'], ('Simulation observation identity', entry['id'])
            sources=observations.get('source_files',observations.get('sourceFiles',observations.get('provenance',{}).get('input_hashes')))
            assert sources, ('Observation source hashes missing',entry['id'])
            if isinstance(sources,dict):sources=[{'path':key,'sha256':value} for key,value in sources.items()]
            for source in sources:
                candidates=[ROOT/source['path'],ROOT/'experiments'/entry['id']/'data'/source['path'],ROOT/'experiments'/entry['id']/source['path']]
                source_path=next((p for p in candidates if p.is_file()),None)
                assert source_path and hashlib.sha256(source_path.read_bytes()).hexdigest() == source['sha256'], ('Stale simulation observation source', source['path'])
    citation = yaml.safe_load((ROOT / 'CITATION.cff').read_text(encoding='utf-8'))
    assert citation['cff-version'] == '1.2.0' and citation['type'] == 'software'
    assert citation['repository-code'] == REPO and citation['url'] == REPO
    assert citation['authors'] and all(a['family-names'] and a['given-names'] for a in citation['authors'])
    meta = read_json(ROOT / 'codemeta.json')
    assert meta['@type'] == 'SoftwareSourceCode' and meta['codeRepository'] == REPO
    assert meta['name'] == citation['title']
    assert meta['author'][0]['name'] == citation['authors'][0]['family-names'] + citation['authors'][0]['given-names']
    assert set(meta['keywords']) == set(citation['keywords'])
    links = sum(check_links(ROOT / name) for name in (*MANUAL, 'README.md', *(p for p in GENERATED if not p.endswith('.json'))))
    return {'status': 'passed', 'experiments': len(ids), 'resources': resources,
            'key_results': metrics, 'local_links': links, 'generated_files': len(GENERATED)}


if __name__ == '__main__':
    try:
        print(json.dumps(validate(), ensure_ascii=False, indent=2))
    except Exception as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1)
