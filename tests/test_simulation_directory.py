"""Exercise the directory's publication, accessibility and search contracts."""
from pathlib import Path
import importlib.util,json,subprocess,shutil,sys
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from simulation_directory import catalog,render,markdown
from build_pages import Builder

def accepted():
    return [e for e in json.loads((ROOT/'simulations/registry.json').read_text(encoding='utf-8'))['simulations'] if e['status'] in {'validated','published'}]

def test_every_accepted_experiment_has_one_searchable_entry_and_course():
    entries,courses,themes=catalog(ROOT,accepted())
    assert len(entries)==45 and len({e['id'] for e in entries})==45
    assert [sum(e['course']==c['id'] for e in entries) for c in courses]==[8,10,13,14]
    assert sum(sum(e['topic']==t['id'] for e in entries) for t in themes)==45
    assert all(e['measurement'] and e['search'] and e['evidence'] for e in entries)

def test_static_directory_works_without_javascript():
    entries,courses,themes=catalog(ROOT,accepted());soup=BeautifulSoup(render(entries,courses,themes),'html.parser')
    assert len(soup.select('details.directory-group'))==4
    assert len(soup.select('article.experiment-entry'))==45
    assert all(d.select_one('summary') and d.select('a[href]') for d in soup.select('details'))
    assert soup.select_one('form[role=search][hidden]') and soup.select_one('[aria-live=polite]')
    assert {n['for'] for n in soup.select('label')}=={'directory-query','directory-course','directory-topic'}

def test_directory_escapes_source_text():
    entries,courses,themes=catalog(ROOT,accepted());entries[0]={**entries[0],'title':'<img src=x onerror=alert(1)>','search':'</script><script>unsafe</script>'}
    soup=BeautifulSoup(render(entries,courses,themes),'html.parser')
    assert soup.select_one('article h3').get_text()=='<img src=x onerror=alert(1)>'
    assert not soup.select('img') and len(soup.select('script'))==2

def test_built_directory_keeps_nested_project_prefix(tmp_path):
    builder=Builder(ROOT,tmp_path/'site','https://example.test/preview/general-physics-lab')
    builder.mapping={e['resources']['model_evidence']:e['resources']['model_evidence'].replace('.md','.html') for e in accepted()}
    builder.register_simulation();builder.markdown_page(ROOT/'simulations/README.md','simulations/index.html')
    soup=BeautifulSoup((builder.output/'simulations/index.html').read_text(encoding='utf-8'),'html.parser')
    styles=[link['href'] for link in soup.select('link[rel=stylesheet]')]
    assert styles.index('/preview/general-physics-lab/assets/site.css')<styles.index('/preview/general-physics-lab/assets/simulation-directory.css')
    assert soup.select_one('script[type=module]')['src']=='/preview/general-physics-lab/assets/simulation-directory.mjs'
    for card in soup.select('.experiment-entry'):
        assert card.select_one('h3 a')['href'].startswith('/preview/general-physics-lab/simulations/')
        assert card.select_one('.entry-links a:last-child')['href'].startswith('/preview/general-physics-lab/docs/')

def test_readme_is_current_and_groups_courses():
    expected=markdown(*catalog(ROOT,accepted()))
    assert (ROOT/'simulations/README.md').read_text(encoding='utf-8')==expected
    assert expected.count('### 普通物理实验 ')==4 and '|课程|实验|' not in expected

def test_search_and_shared_state_in_node():
    node=shutil.which('node');assert node,'Node.js is required for virtual laboratories'
    result=subprocess.run([node,'--test',str(ROOT/'tests/simulation-directory.test.mjs')],capture_output=True,text=True,encoding='utf-8')
    assert result.returncode==0,result.stdout+result.stderr
