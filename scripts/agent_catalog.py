"""Build and query the source-backed experiment discovery catalog."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import quote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
REPO = 'https://github.com/HNNUYUXUAN/general-physics-lab'
RAW = 'https://raw.githubusercontent.com/HNNUYUXUAN/general-physics-lab/main/'
PAGES = 'https://hnnuyuxuan.github.io/general-physics-lab/'
GENERATED = ('docs/experiments.json', 'docs/experiment-index.md',
             'llms.txt', 'llm.txt', 'llms-full.txt')


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def json_text(value):
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n'


def resource(path, root=ROOT):
    path = Path(path)
    if not path.is_absolute():
        path = root / path
    relative = path.resolve().relative_to(root.resolve()).as_posix()
    content = path.read_bytes()
    text_resource = path.suffix.lower() in {'.md', '.json', '.csv', '.py', '.wl', '.ipynb', '.html'}
    if text_resource:
        content = content.decode('utf-8').replace('\r\n', '\n').encode('utf-8')
    descriptor = {'path': relative, 'url': REPO + '/blob/main/' + quote(relative, safe='/'),
            'raw_url': RAW + quote(relative, safe='/'),
            'sha256': hashlib.sha256(content).hexdigest(), 'bytes': len(content),
            'hash_basis': 'utf8-lf' if text_resource else 'raw-bytes'}
    if relative.endswith('.html') or relative.startswith('pdf/') and relative.endswith('.pdf'):
        descriptor['online_url'] = PAGES + quote(relative, safe='/')
    return descriptor


def compile_catalog(root=ROOT):
    entries = read_json(root / 'experiments/registry.json')['experiments']
    annotations = read_json(root / 'docs/experiment-topics.json')['experiments']
    topics = {item['id']: item for item in annotations}
    assert len(topics) == len(annotations), 'Duplicate topic IDs'
    assert set(topics) == {entry['id'] for entry in entries}, 'Topic coverage differs from registry'
    with (root / 'pdf/manifest.csv').open(encoding='utf-8-sig', newline='') as stream:
        pdfs = [row for row in csv.DictReader(stream) if row['role'] == 'main_report']
    main_pdfs = {row['experiment_id']: row for row in pdfs}
    assert len(main_pdfs) == len(pdfs) == len(entries), 'Main PDF correspondence differs'
    experiments = []
    for entry in entries:
        identity = entry['id']
        base = root / 'experiments' / identity
        package = root / 'notebook/paclets' / entry['paclet']
        pendulum = entry['slug'] == 'pendulum'
        result = read_json(base / 'results/python.json')
        verification = read_json(base / 'results/verification.json')
        assert result['experiment_id'] == identity, identity
        pdf = main_pdfs[identity]
        assert pdf['source'] == entry['source_docx'], (identity, 'PDF source identity')
        assert pdf['sha256'] == entry['source_sha256'], (identity, 'DOCX source hash')
        pdf_resource = resource('pdf/' + pdf['pdf_file'], root)
        assert pdf_resource['sha256'] == pdf['pdf_sha256'], (identity, 'PDF hash')
        paths = {
            'readme': base / 'README.md', 'report': root / entry['report'],
            'report_html': base / 'report/report.html',
            'jupyter_notebook': root / entry['jupyter_notebook'],
            'notebook_html': base / 'notebooks/analysis.html',
            'wolfram_notebook': root / entry['wolfram_notebook'],
            'paclet_archive': root / entry['paclet_archive'],
            'config': root / entry['canonical_input'],
            'provenance': base / 'data/provenance.json',
            'python_module': root / entry['python_module'],
            'wolfram_module': package / 'Kernel' / ('PendulumLab.wl' if pendulum else 'analysis.wl'),
            'python_results': base / 'results/python.json',
            'wolfram_results': base / 'results/wolfram.json',
            'verification': base / 'results/verification.json',
            'report_template': base / 'report/report.template.md',
        }
        for name in ('authoring.json',):
            if (base / name).exists():
                paths['authoring'] = base / name
        for name in ('jupyter-execution', 'native-review', 'browser-review',
                     'native-interaction-review', 'presentation-validation', 'wolfram-tests'):
            candidate = base / 'results' / (name + '.json')
            if candidate.exists():
                paths[name.replace('-', '_')] = candidate
        resources = {key: resource(path, root) for key, path in paths.items()}
        resources['source_pdf'] = pdf_resource
        data_files = []
        for path in sorted((base / 'data').glob('*.csv')):
            with path.open(encoding='utf-8-sig', newline='') as stream:
                rows = list(csv.reader(stream))
            assert rows, (identity, 'Empty CSV', path.name)
            data_files.append({'resource': resource(path, root), 'columns': rows[0],
                               'row_count': len(rows) - 1})
        if pendulum:
            keys = ['gravity_fit', 'slope', 'intercept']
        else:
            plan = read_json(base / 'assets/readme-plan.json')
            keys = list(dict.fromkeys(item['metric'] for item in plan['result_checks']))
        meanings = topics[identity].get('metric_descriptions', {})
        assert set(meanings) <= set(result['metrics']), (identity, 'Unknown described metric')
        key_results = [{'key': key, **result['metrics'][key], 'result_pointer': '/metrics/' + key,
                        **({'description': meanings[key]} if key in meanings else {})} for key in keys]
        build = 'python scripts/pipeline.py all' + ('' if pendulum else ' --experiment ' + identity)
        experiments.append({
            'id': identity, 'course': entry['course'], 'title': entry['title'],
            **{key: topics[identity][key] for key in
               ('title_en', 'aliases', 'topics', 'methods', 'summary_zh')},
            'sections': entry['sections'], 'resources': resources, 'data_files': data_files,
            'metric_catalog': [{'key': key, 'label': metric.get('label', key), 'unit': metric['unit'],
                                **({'description': meanings[key]} if key in meanings else {})}
                               for key, metric in result['metrics'].items()],
            'key_results': key_results,
            'python_interface': {'module': 'physicslab.experiments.' + entry['module'],
                                 'analyze': 'analyze(experiment_directory)'},
            'wolfram_interface': {'context': entry['paclet'] + '`',
                                  'analyze': 'PLAnalyze[]' if pendulum else 'Analyze[]',
                                  'notebook_path': 'PLNotebookPath[]' if pendulum else 'LabNotebookPath[]',
                                  'open_notebook': 'PLOpenNotebook[]' if pendulum else 'OpenNotebook[]'},
            'commands': {'audit': 'python scripts/check_delivery.py --experiment ' + identity,
                         'execute_notebook': 'python scripts/execute_notebooks.py --experiment ' + identity,
                         'rebuild': build,
                         'readme_figures': 'python scripts/build_readme_assets.py --experiment ' + identity},
            'verification': {'recorded_status': verification['status'],
                             'comparison_count': len(verification['checks']),
                             'path': resources['verification']['path']},
            'source_identity': {'docx_archive_path': 'archive/' + entry['source_docx'],
                                'docx_sha256': entry['source_sha256'],
                                'pdf_path': pdf_resource['path'], 'pdf_sha256': pdf_resource['sha256'],
                                'pdf_pages': int(pdf['pages'])},
        })
    return {'schema_version': 1, 'repository_url': REPO, 'raw_base_url': RAW, 'site_base_url': PAGES,
            'path_base': 'repository_root', 'experiment_count': len(experiments),
            'courses': [{'id': f'course-{number:02}', 'title': f'普通物理实验 {number}',
                         'experiment_count': sum(e['course'] == f'course-{number:02}' for e in experiments)}
                        for number in range(1, 5)],
            'experiments': experiments}


def link(label, path):
    return f'[{label}]({RAW}{quote(path, safe="/")})'


def card(experiment, compact=False):
    e = experiment
    text = [f"### {e['title']} · {e['title_en']}", '', f"标识：`{e['id']}`。{e['summary_zh']}", '',
            '别名：' + '；'.join(e['aliases']) + '。', '',
            '主题：' + '；'.join(e['topics']) + '。方法：' + '；'.join(e['methods']) + '。', '']
    navigation = [('实验入口', 'readme'), ('报告', 'report'), ('Jupyter', 'jupyter_notebook'),
                  ('Wolfram', 'wolfram_notebook'), ('源PDF', 'source_pdf')]
    text += [' · '.join(link(label, e['resources'][key]['path']) for label, key in navigation), '']
    if not compact:
        text += ['章节：' + ' → '.join(e['sections']) + '。', '',
                 ' | '.join(link(label, e['resources'][key]['path']) for label, key in
                            [('参数', 'config'), ('来源', 'provenance'), ('Python计算', 'python_module'),
                             ('Wolfram计算', 'wolfram_module'), ('完整结果', 'python_results'),
                             ('双端对照', 'verification'), ('Paclet', 'paclet_archive')]), '',
                 '观测表：' + '；'.join(link(Path(d['resource']['path']).name, d['resource']['path']) +
                                    f"（{d['row_count']}行；字段：" + ', '.join(d['columns']) + '）'
                                    for d in e['data_files']) + '。', '',
                 '|指标键|数值|单位|', '|---|---:|---|']
        for metric in e['key_results']:
            text.append(f"|`{metric['key']}`|{metric['value']:.12g}|{metric['unit']}|")
        text += ['', '上述为完整结果的选摘；不确定度定义与模型条件见参数、报告和结果文件。', '',
                 f"Python：`{e['python_interface']['module']}.analyze(experiment_directory)`。",
                 f"Wolfram：``{e['wolfram_interface']['context']}{e['wolfram_interface']['analyze']}``；"
                 f"打开：``{e['wolfram_interface']['context']}{e['wolfram_interface']['open_notebook']}``。", '',
                 '```text', e['commands']['execute_notebook'], e['commands']['audit'], '```', '']
    return '\n'.join(text)


def absolute_links(text, source):
    def replace(match):
        target = match['target']
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc:
            return match[0]
        path = (source.parent / parsed.path).resolve() if parsed.path else source
        relative = path.relative_to(ROOT).as_posix()
        return (match['label'] + '(' + RAW + quote(relative, safe='/') +
                (('#' + quote(parsed.fragment)) if parsed.fragment else '') + ')')
    return re.sub(r'(?P<label>!?\[[^\]]*\])\((?P<target>[^\s)]+)\)', replace, text)


def documents(catalog, root=ROOT):
    entries = catalog['experiments']
    llms = ['# 普通物理实验 · General Physics Lab', '',
            '> 淮南师范学院四门普通物理实验课程的45个实验：Markdown报告、Python/Jupyter与Wolfram计算笔记本、共享CSV/JSON数据、源PDF、双端数值对照与独立Paclet。', '',
            'Reproducible general physics laboratory experiments in mechanics, thermodynamics, electromagnetism and optics. Primary language: Chinese (zh-CN); English aliases support topic lookup.', '',
            '按任务检索一个实验，先读其README与报告，再取参数、CSV及完整结果。引用数值时附实验标识、指标键、单位、适用条件与提交SHA。Python要求3.11及以上；Wolfram复算使用本机Wolfram环境。', '',
            '## 阅读与接手', '',
            '- [在线实验站点](' + PAGES + '): 45项实验报告与浏览器交互，Notebook和Paclet提供下载复算。',
            '- ' + link('Agent阅读指南 / Reading guide', 'docs/agent-guide.md') + ': 定位实验、读取证据和引用结果。',
            '- ' + link('Agent复现指南 / Reproduction', 'docs/agent-reproduction.md') + ': 新内核执行、双端重建、Paclet与验收。',
            '- ' + link('仓库工作约定 / AGENTS.md', 'AGENTS.md') + ': 修改范围、数据和排版规则。',
            '- ' + link('运行环境 / Setup', 'docs/usage.md') + ': Python、Wolfram、字体与HTML阅读。', '',
            '## 检索目录', '',
            '- ' + link('45项实验检索目录 / Experiment index', 'docs/experiment-index.md') + ': 中英文名、常用别名、主题、方法和三稿入口。',
            '- ' + link('机器目录 / Machine catalog', 'docs/experiments.json') + ': 路径、raw URL、哈希、数据表、指标和实际接口。',
            '- ' + link('目录接口 / Catalog API', 'docs/agent-catalog.md') + ': 标准库检索CLI与字段说明。', '',
            '## 按课程阅读', '']
    for course in catalog['courses']:
        llms.append('- ' + link(course['title'], 'experiments/' + course['id'] + '/README.md') +
                    f": {course['experiment_count']}个实验。")
    llms += ['', '## 数据、方法与引用', '',
             '- ' + link('数据与方法', 'docs/data-and-methods.md') + ': 单位、模型、统计与结果定义。',
             '- ' + link('验证汇总', 'docs/delivery-summary.md') + ': 实验验证记录与资料条件。',
             '- ' + link('源资料PDF', 'pdf/README.md') + ': 45份主报告和12份参考资料。',
             '- ' + link('引用信息 / Citation', 'CITATION.cff') + ': 作者与项目身份；具体结果附提交与路径。', '',
             '- ' + link('许可范围 / Licensing', 'LICENSING.md') + ': 代码MIT，原创文稿及数据整理贡献CC BY 4.0，第三方材料保留各自权利。', '',
             '## Optional', '',
             '- ' + link('完整导览 / Expanded guide', 'llms-full.txt') + ': 接手文档与全部实验卡片。',
             '- ' + link('软件元数据 / CodeMeta', 'codemeta.json') + ': 软件、语言与学科描述。',
             '- ' + link('开发与构建', 'docs/development.md') + ': 成稿组织与构建接口。',
             '- ' + link('索引维护', 'docs/discovery.md') + ': 生成依据、版本链接和同步检查。', '']
    index = ['# 实验检索目录 · Experiment Index', '',
             '[项目首页](../README.md) · [Agent阅读指南](agent-guide.md) · [机器目录](experiments.json) · [目录接口](agent-catalog.md)', '',
             '45项实验按课程组织；可检索中文名称、英文名称、常用别名、物理主题和分析方法。每项链接进入实际文稿或数据文件。', '']
    full = ['# 普通物理实验 · 完整 Agent 导览', '',
            '> General Physics Lab: reading, reproduction and 45 experiment cards.', '',
            '本文件汇集阅读与复现说明及全部实验卡片。报告、原始读数和完整精度结果通过各卡片链接按需读取。', '',
            '项目：' + REPO, '', link('简短导览', 'llms.txt') + ' · ' + link('机器目录', 'docs/experiments.json'), '']
    for source_name in ('docs/agent-guide.md', 'docs/agent-reproduction.md', 'docs/agent-catalog.md'):
        source = root / source_name
        text = absolute_links(source.read_text(encoding='utf-8'), source)
        # Keep a single H1 in the assembled guide and preserve the inner hierarchy.
        text = re.sub(r'^(#{1,5}) ', r'#\1 ', text, flags=re.M)
        full += ['---', '', '来源：' + link(source.name, source_name), '', text.strip(), '']
    for course in catalog['courses']:
        heading = f"## {course['title']} · {course['experiment_count']}项"
        index += [heading, '']
        full += [heading, '']
        for entry in entries:
            if entry['course'] == course['id']:
                index += [card(entry, compact=True), '']
                full += [card(entry), '']
    return {'docs/experiments.json': json_text(catalog),
            'docs/experiment-index.md': '\n'.join(index).rstrip() + '\n',
            'llms.txt': '\n'.join(llms),
            'llm.txt': '# 普通物理实验 · General Physics Lab\n\n> Agent 阅读与复现入口。\n\n## 导览\n\n- ' +
                       link('llms.txt', 'llms.txt') + ': 规范导览与实验检索入口。\n',
            'llms-full.txt': '\n'.join(full).rstrip() + '\n'}


def search(catalog, query, course=None, limit=10):
    terms = query.casefold().split()
    if not terms:
        return []
    ranked = []
    for e in catalog['experiments']:
        if course and e['course'] != course:
            continue
        fields = [(e['id'], 8), (e['title'], 6), (e['title_en'], 5),
                  (' '.join(e['aliases']), 4), (' '.join(e['topics']), 3),
                  (' '.join(e['methods']), 2), (e['summary_zh'], 1),
                  (' '.join(m['key'] + ' ' + m['label'] + ' ' + m.get('description', '')
                            for m in e['metric_catalog']), 1)]
        def matches(term, text):
            text = text.casefold()
            if re.fullmatch(r'[a-z0-9_-]+', term):
                return re.search(r'(?<![a-z0-9_])' + re.escape(term) + r'(?![a-z0-9_])', text) is not None
            return term in text
        field_scores = [max((weight for text, weight in fields if matches(term, text)), default=0)
                        for term in terms]
        if all(field_scores):
            ranked.append((sum(field_scores), e))
    ranked.sort(key=lambda pair: (-pair[0], pair[1]['id']))
    return [{'id': e['id'], 'title': e['title'], 'title_en': e['title_en'],
             'summary_zh': e['summary_zh'], 'readme': e['resources']['readme'],
             'report': e['resources']['report']} for _, e in ranked[:limit]]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    build = commands.add_parser('build', help='Generate discovery files')
    build.add_argument('--check', action='store_true', help='Check without writing files')
    find = commands.add_parser('search', help='Find experiments by bilingual topic')
    find.add_argument('query'); find.add_argument('--course'); find.add_argument('--limit', type=int, default=10)
    find.add_argument('--json', action='store_true')
    show = commands.add_parser('show', help='Read one experiment record')
    show.add_argument('experiment'); show.add_argument('--json', action='store_true')
    args = parser.parse_args()
    if args.command == 'build':
        changed = []
        for relative, text in documents(compile_catalog()).items():
            path = ROOT / relative
            if not path.exists() or path.read_text(encoding='utf-8') != text:
                changed.append(relative)
                if not args.check:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(text, encoding='utf-8', newline='\n')
        if args.check and changed:
            parser.exit(1, 'Discovery files need an update:\n' + '\n'.join(changed) + '\n')
        print(('Checked' if args.check else 'Generated') + f' {len(GENERATED)} discovery files; 45 experiments')
        return
    catalog = read_json(ROOT / 'docs/experiments.json')
    if args.command == 'search':
        if args.limit < 1:
            parser.error('--limit must be positive')
        if args.course and args.course not in {c['id'] for c in catalog['courses']}:
            parser.error('Unknown course: ' + args.course)
        found = search(catalog, args.query, args.course, args.limit)
        if args.json:
            print(json_text(found), end='')
        else:
            for e in found:
                print(f"{e['id']}\t{e['title']}\n  {e['summary_zh']}\n  {e['readme']['path']}")
            if not found:
                print('No matching experiments')
    else:
        entry = next((e for e in catalog['experiments'] if e['id'] == args.experiment), None)
        if entry is None:
            parser.error('Unknown experiment: ' + args.experiment)
        print(json_text(entry) if args.json else card(entry), end='')


if __name__ == '__main__':
    main()
