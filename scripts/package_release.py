"""Package versioned reading, data and Paclet downloads with license notices."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tomllib
import zipfile

ROOT = Path(__file__).resolve().parents[1]
LICENSE_PATHS = ('LICENSE', 'LICENSING.md', 'THIRD_PARTY_NOTICES.md')


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def license_files():
    return [ROOT / path for path in LICENSE_PATHS] + sorted((ROOT / 'LICENSES').glob('*.txt'))


def license_paclets():
    """Add notices without changing the original scientific package members."""
    entries = json.loads((ROOT / 'experiments/registry.json').read_text(encoding='utf-8'))['experiments']
    records = []
    licenses = license_files()
    assert licenses and all(path.is_file() for path in licenses)
    for entry in entries:
        archive = ROOT / entry['paclet_archive']
        package = ROOT / 'notebook/paclets' / entry['paclet']
        for source in licenses:
            relative = source.relative_to(ROOT)
            target = package / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        with zipfile.ZipFile(archive) as source_zip:
            infos = source_zip.infolist()
            members = {info.filename: source_zip.read(info.filename) for info in infos}
        prefix = next(name.rsplit('/', 1)[0] + '/' for name in members if name.endswith('/PacletInfo.wl'))
        additions = {prefix + path.relative_to(ROOT).as_posix(): path.read_bytes() for path in licenses}
        temporary = archive.with_suffix('.paclet.tmp')
        try:
            with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_DEFLATED) as target_zip:
                for info in infos:
                    if info.filename not in additions:
                        target_zip.writestr(info, members[info.filename])
                for name, content in additions.items():
                    info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    target_zip.writestr(info, content)
            with zipfile.ZipFile(temporary) as check:
                assert check.testzip() is None, archive
                assert len(check.namelist()) == len(set(check.namelist())), archive
                for name, content in members.items():
                    if name not in additions:
                        assert check.read(name) == content, (archive, name)
                for name, content in additions.items():
                    assert check.read(name) == content, (archive, name)
            temporary.replace(archive)
        finally:
            temporary.unlink(missing_ok=True)
        records.append({'experiment_id': entry['id'], 'archive': entry['paclet_archive'],
                        'sha256': sha256(archive), 'scientific_members_preserved': True,
                        'license_files': sorted(additions)})
    path = ROOT / '.build/release/paclet-licensing.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Licensed {len(records)} standalone Paclets')
    return records


def zip_paths(target, paths, prefix, base=ROOT, extras=None):
    """Use fixed ordering and timestamps for deterministic release archives."""
    selected = sorted(set(Path(path) for path in paths))
    with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in selected:
            assert path.is_file() and path.resolve().is_relative_to(base.resolve()), path
            relative = path.relative_to(base).as_posix()
            info = zipfile.ZipInfo(prefix + '/' + relative, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, path.read_bytes())
        for name, content in sorted((extras or {}).items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, content)
    with zipfile.ZipFile(target) as archive:
        assert archive.testzip() is None, target


def build(version, site):
    project = tomllib.loads((ROOT / 'pyproject.toml').read_text(encoding='utf-8'))['project']
    assert version == project['version'], 'Release version differs from pyproject.toml'
    tag = 'v' + version
    output = ROOT / '.build/release' / tag
    output.mkdir(parents=True, exist_ok=True)
    entries = json.loads((ROOT / 'experiments/registry.json').read_text(encoding='utf-8'))['experiments']
    licenses = license_files()
    zip_paths(output / f'general-physics-lab-{tag}-paclets.zip',
              [*(ROOT / entry['paclet_archive'] for entry in entries), *licenses],
              f'general-physics-lab-{tag}')
    data = [ROOT / 'experiments/registry.json', ROOT / 'docs/experiments.json',
            ROOT / 'docs/agent-catalog.md', ROOT / 'CITATION.cff', ROOT / 'codemeta.json', *licenses]
    for entry in entries:
        base = ROOT / 'experiments' / entry['id']
        data += [base / 'experiment.json', base / 'README.md', *sorted((base / 'data').glob('*'))]
    zip_paths(output / f'general-physics-lab-{tag}-data.zip', data, f'general-physics-lab-{tag}')
    assert (site / 'index.html').is_file() and (site / 'llms.txt').is_file(), 'Build Pages first'
    reading_root = f'general-physics-lab-{tag}'
    launcher = '''"""Preview the bundled reading site on localhost."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--port", type=int, default=8000)
args = parser.parse_args()
root = Path(__file__).resolve().parent
server = ThreadingHTTPServer(("127.0.0.1", args.port), partial(SimpleHTTPRequestHandler, directory=str(root)))
print(f"Open http://127.0.0.1:{server.server_port}/general-physics-lab/", flush=True)
try:
    server.serve_forever()
except KeyboardInterrupt:
    pass
finally:
    server.server_close()
'''
    instructions = ('# 普通物理实验 · 离线阅读包\n\n'
                    '在本目录运行 `python serve.py`，然后打开 '
                    '`http://127.0.0.1:8000/general-physics-lab/`。\n\n'
                    '需要更换端口时运行 `python serve.py --port 8001`。服务绑定本机，按 Ctrl+C 结束。'
                    '站内包含公式脚本、图表、45份计算阅读版和45份报告阅读版。'
                    'Python、Wolfram重算入口链接到项目源码和安装包。\n\n'
                    '代码MIT；原创文稿和数据整理贡献CC BY 4.0。许可范围见 LICENSING.md。\n')
    extras = {reading_root + '/serve.py': launcher.encode('utf-8'),
              reading_root + '/README.md': instructions.encode('utf-8'),
              **{reading_root + '/' + path.relative_to(ROOT).as_posix(): path.read_bytes() for path in licenses}}
    zip_paths(output / f'general-physics-lab-{tag}-reading.zip',
              [path for path in site.rglob('*') if path.is_file()], reading_root + '/general-physics-lab', site, extras)
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    checks = json.loads((ROOT / 'docs/validation-summary.json').read_text(encoding='utf-8'))
    record = {'version': version, 'tag': tag, 'source_commit': commit,
              'experiments': len(entries), 'licenses': {'code': 'MIT', 'content_and_data': 'CC-BY-4.0'},
              'recorded_delivery_summary': checks,
              'assets': [{'name': path.name, 'sha256': sha256(path), 'bytes': path.stat().st_size}
                         for path in sorted(output.glob('*.zip'))]}
    for name in ('paclet-licensing.json', 'paclet-installation.json'):
        path = ROOT / '.build/release' / name
        if path.exists():
            record[name.removesuffix('.json').replace('-', '_')] = json.loads(path.read_text(encoding='utf-8'))
    installation = record.get('paclet_installation', {}).get('packages', [])
    assert len(installation) == len(entries) and all(item['status'] == 'passed' for item in installation), 'Complete installed Paclet validation first'
    notebook_runs = sorted((ROOT / '.build/notebook-checks').glob('*/execution.json'))
    assert notebook_runs, 'Execute notebooks before release packaging'
    notebook_run = notebook_runs[-1]
    execution = json.loads(notebook_run.read_text(encoding='utf-8'))
    assert {item['id'] for item in execution} == {item['id'] for item in entries} and all(item['status'] == 'passed' for item in execution), 'Complete all 45 notebook executions before packaging'
    record['notebook_execution'] = {'run': notebook_run.parent.name, 'experiments': execution}
    pages_check = ROOT / '.build/pages/verification.json'
    record['pages_validation'] = json.loads(pages_check.read_text(encoding='utf-8'))
    assert record['pages_validation']['status'] == 'passed', 'Validate the reading site before packaging'
    record['browser_validation'] = {
        'coverage': 'All 45 experiments; each supplied interactive control changed and checked',
        'navigation': 'Desktop and mobile layouts, PDF and download entries checked',
        'pendulum_animation': 'Play, pause and time selection checked after interruption handling repair',
        'records': []}
    for relative in ('browser-course01-02.json', 'browser-course03.json',
                     'review-optics/browser-validation.json', 'browser-navigation.json', 'browser-animation.json',
                     'browser-plot-math.json'):
        path = ROOT / '.build/pages' / relative
        assert path.is_file(), 'Complete browser validation: ' + relative
        record['browser_validation']['records'].append({'name': relative, 'sha256': sha256(path)})
    qa_root = json.loads((ROOT / '.build/pages/browser-course01-02.json').read_text(encoding='utf-8'))
    qa_electric = json.loads((ROOT / '.build/pages/browser-course03.json').read_text(encoding='utf-8'))
    qa_optics = json.loads((ROOT / '.build/pages/review-optics/browser-validation.json').read_text(encoding='utf-8'))
    browser_pages = [*qa_root['pages'], *(page for experiment in qa_electric['experiments'] for page in experiment['pages'])]
    assert all(page['sources'] == page['rendered'] for page in browser_pages)
    assert all(page['expected'] == page['frames'] for page in qa_optics['pages'])
    count = len(browser_pages) + len(qa_optics['pages'])
    assert count == len(entries) * 2, 'Complete every report and computation page browser check'
    record['browser_validation']['experiment_report_and_notebook_pages'] = count
    plot_math = json.loads((ROOT / '.build/pages/browser-plot-math.json').read_text(encoding='utf-8'))
    assert plot_math['status'] == 'passed', 'Complete mathematical plot label rendering checks'
    site_manifest = json.loads((site / 'build-manifest.json').read_text(encoding='utf-8'))
    record['browser_validation']['rendered_body_formulas'] = sum(page['rendered'] for page in browser_pages) + sum(page['frames'] for page in qa_optics['pages'])
    record['browser_validation']['rendered_plot_math_labels'] = len(site_manifest['plot_math_labels'])
    record['browser_validation']['rendered_formulas'] = record['browser_validation']['rendered_body_formulas'] + record['browser_validation']['rendered_plot_math_labels']
    manifest = output / 'release-manifest.json'
    manifest.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    files = [*sorted(output.glob('*.zip')), manifest]
    (output / 'SHA256SUMS.txt').write_text(''.join(f'{sha256(path)}  {path.name}\n' for path in files), encoding='utf-8')
    print(json.dumps({'output': str(output), 'assets': record['assets']}, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--license-paclets', action='store_true')
    parser.add_argument('--version', default='0.1.0')
    parser.add_argument('--site', type=Path, default=ROOT / '.build/pages/site')
    args = parser.parse_args()
    if args.license_paclets:
        license_paclets()
    else:
        build(args.version, args.site.resolve())


if __name__ == '__main__':
    main()
