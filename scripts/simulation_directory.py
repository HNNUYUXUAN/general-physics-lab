"""Generate a searchable, progressively enhanced directory of accepted laboratories."""
from pathlib import Path
import argparse,html,json

ROOT=Path(__file__).resolve().parents[1]
BASE='https://hnnuyuxuan.github.io/general-physics-lab/simulations/'
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def esc(value):return html.escape(str(value),quote=True)

def catalog(root,accepted):
    metadata=read(root/'site/simulation-directory.json')
    science=read(root/'docs/series-scientific-manifest.json')
    annotations={e['id']:e for e in read(root/'docs/experiment-topics.json')['experiments']}
    original=read(root/'experiments/registry.json')['experiments']
    ordering={e['id']:i for i,e in enumerate(original)}
    themes=science['theory_groups'];by_experiment={i:g for g in themes for i in g['experiment_ids']}
    entries=[]
    for e in sorted(accepted,key=lambda e:ordering[e['experiment_id']]):
        identity=e['experiment_id'];topic=by_experiment[identity];a=annotations[identity]
        course=identity.split('/')[0];number=int(course.split('-')[1])
        measurement=metadata['measurements'][e['slug']]
        entries.append({'id':identity,'slug':e['slug'],'title':e['title'],
          'course':course,'course_title':f'普通物理实验 {number}',
          'topic':topic['id'],'topic_title':topic['title'],'measurement':measurement,
          'evidence':'../'+e['resources']['model_evidence'],
          'search':' '.join([identity,e['title'],a['title_en'],measurement,topic['title'],*a['aliases'],*a['topics'],*a['methods']])})
    courses=[{'id':f'course-{i:02}','title':f'普通物理实验 {i}',
      'description':metadata['course_descriptions'][f'course-{i:02}']} for i in range(1,5)]
    themes=[{'id':g['id'],'title':g['title'],'description':metadata['topic_descriptions'][g['id']]} for g in themes]
    return entries,courses,themes

def group_markup(group,entries):
    cards=''.join(card(e) for e in entries)
    return (f'<details class="directory-group" data-group="{esc(group["id"])}">'
      f'<summary><span class="group-heading"><span class="group-title">{esc(group["title"])}</span>'
      f'<span class="group-description">{esc(group["description"])}</span></span>'
      f'<span class="group-count">{len(entries)} 项</span></summary>'
      f'<div class="directory-cards">{cards}</div></details>')

def card(e):
    return (f'<article class="experiment-entry" data-course="{esc(e["course"])}" data-topic="{esc(e["topic"])}" '
      f'data-search="{esc(e["search"])}" data-id="{esc(e["id"])}">'
      f'<p class="entry-subject">{esc(e["topic_title"])} · {esc(e["course_title"])}</p>'
      f'<h3><a href="{esc(e["slug"])}/index.html">{esc(e["title"])}</a></h3>'
      f'<p class="entry-measurement">{esc(e["measurement"])}</p>'
      f'<div class="entry-links"><a href="{esc(e["slug"])}/index.html">进入实验 <span aria-hidden="true">→</span></a>'
      f'<a href="{esc(e["evidence"])}">模型与文献</a></div></article>')

def render(entries,courses,themes):
    def options(groups,key):
        return ''.join(f'<option value="{esc(g["id"])}">{esc(g["title"])}（{sum(e[key]==g["id"] for e in entries)}）</option>' for g in groups)
    settings=json.dumps({'courses':courses,'topics':themes},ensure_ascii=False).replace('<','\\u003c')
    groups=''.join(group_markup(g,[e for e in entries if e['course']==g['id']]) for g in courses if any(e['course']==g['id'] for e in entries))
    return f'''<!doctype html><html lang="zh-CN"><head><link rel="stylesheet" href="../site/assets/simulation-directory.css"><script type="module" src="../site/assets/simulation-directory.mjs"></script></head><body>
<main class="site-content directory-page" data-directory>
<header class="directory-heading"><p class="directory-kicker">普通物理实验 · 在线操作与测量</p><h1>虚拟实验</h1>
<p>从装置操作到读数分析，按课程或物理问题选择实验。</p><p class="directory-total">4 门课程 <span aria-hidden="true">/</span> {len(entries)} 项实验</p></header>
<form class="directory-filters" role="search" aria-label="查找虚拟实验" hidden>
<div class="directory-search"><label for="directory-query">搜索实验</label><input id="directory-query" name="q" type="search" maxlength="160" autocomplete="off" placeholder="实验名称、关键词或方法"></div>
<div class="directory-filter-row"><div class="filter-field"><label for="directory-course">课程</label><select id="directory-course" name="course"><option value="">全部课程</option>{options(courses,'course')}</select></div>
<div class="filter-field"><label for="directory-topic">物理主题</label><select id="directory-topic" name="topic"><option value="">全部主题</option>{options(themes,'topic')}</select></div>
<div class="directory-view" role="group" aria-label="浏览方式"><span>浏览方式</span><button type="button" data-view="course" aria-pressed="true">按课程</button><button type="button" data-view="topic" aria-pressed="false">按主题</button></div>
<button class="directory-reset" type="reset">清除筛选</button></div></form>
<div class="directory-results-bar"><p id="directory-status" role="status" aria-live="polite" aria-atomic="true">共 {len(entries)} 项实验，展开目录进入实验。</p><button type="button" id="directory-expand" hidden>展开全部</button></div>
<section id="directory-groups" aria-label="实验目录">{groups}</section>
<section class="directory-empty" hidden><h2>没有符合条件的实验</h2><p>请调整关键词、课程或物理主题。</p><button type="button" data-clear>清除筛选</button></section>
<script type="application/json" id="directory-settings">{settings}</script>
<footer class="directory-reading"><h2>阅读与复现</h2><p><a href="../docs/experiment-index.md">实验报告与计算目录</a> · <a href="../docs/series-scientific-guide.md">模型与文献总览</a> · <a href="../docs/simulation/series-validation.json">逐项验收记录</a> · <a href="../docs/virtual-lab-agent-guide.md">检索与复现</a></p></footer>
</main></body></html>'''

def markdown(entries,courses,themes):
    lines=['# 虚拟实验','','4门课程，'+str(len(entries))+'项在线虚拟实验。从装置操作到读数分析，按课程或物理问题选择实验。','',
      '[打开在线目录：搜索与筛选]('+BASE+') · [按物理主题浏览]('+BASE+'?group=topic)','','## 按课程进入','']
    for g in courses:
        selected=[e for e in entries if e['course']==g['id']]
        if not selected:continue
        lines += [f'### {g["title"]} · {len(selected)}项', '',g['description']+'。 [在线筛选本课程]('+BASE+'?course='+g['id']+')','']
        for e in selected:lines.append(f'- [{e["title"]}]({BASE}{e["slug"]}/)：{e["measurement"]}。 [模型与文献]({e["evidence"]})')
        lines.append('')
    lines+=['## 按物理主题进入','','|主题|实验数量|在线入口|','|---|---:|---|']
    for g in themes:
        count=sum(e['topic']==g['id'] for e in entries)
        if count:lines.append(f'|{g["title"]}|{count}|[浏览实验]({BASE}?group=topic&topic={g["id"]})|')
    lines+=['','[实验报告与计算目录](../docs/experiment-index.md) · [模型与文献总览](../docs/series-scientific-guide.md) · [逐项验收记录](../docs/simulation/series-validation.json) · [检索与复现](../docs/virtual-lab-agent-guide.md)','']
    return '\n'.join(lines)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--repo-root',type=Path,default=ROOT);parser.add_argument('--check',action='store_true');a=parser.parse_args()
    accepted=[e for e in read(a.repo_root/'simulations/registry.json')['simulations'] if e['status'] in {'validated','published'} and e['evidence_status']=='verified' and e['frontend_status']=='passed']
    text=markdown(*catalog(a.repo_root,accepted));path=a.repo_root/'simulations/README.md'
    if a.check:
        if path.read_text(encoding='utf-8')!=text:raise SystemExit('Simulation directory README is stale; run scripts/simulation_directory.py')
    else:path.write_text(text,encoding='utf-8',newline='\n')
    print(f'{len(accepted)} accepted experiments; directory '+('checked' if a.check else 'generated'))
if __name__=='__main__':main()
