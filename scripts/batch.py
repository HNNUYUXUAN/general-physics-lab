"""Isolated, resumable three-manuscript builds for registered experiments."""
from pathlib import Path
import argparse,base64,datetime,hashlib,importlib,importlib.metadata,json,os,re,shutil,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from physicslab.common.io import read_json,write_json,sha256
from physicslab.common.manuscripts import table_markdown,series_figure,sections,inline_images,number_tex
from physicslab.common.tex_boxes import tex_boxes,wl_string

def registry():return read_json(ROOT/'experiments/registry.json')['experiments']
def stamp():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d_%H%M%S_%f')
def author(entry):return read_json(ROOT/'experiments'/entry['id']/'authoring.json')
def digest(paths,base):return {p.relative_to(base).as_posix():sha256(p) for p in sorted(paths) if p.is_file()}
def input_hashes(exp):return digest([exp/'experiment.json',*list((exp/'data').glob('*'))],exp)
def write_wl(path,text):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(''.join(c if ord(c)<128 else '\\:'+format(ord(c),'04x') for c in text),encoding='ascii')

def state(entry,phase,**extra):
    path=ROOT/'.build/progress.json';record=read_json(path) if path.exists() else {'experiments':{}}
    record['experiments'][entry['id']]={'phase':phase,'updated_at':datetime.datetime.now().astimezone().isoformat(),**extra}
    write_json(path,record)

def render_report(template,result):
    def replace(m):
        typ,key=m[1].split('.',1)
        if typ=='metrics':
            metric=result['metrics'][key]
            value=metric.get('display',number_tex(metric['value']))
            if '\\times' in value and not any(t.start()<=m.start()<t.end() for t in MATH.finditer(template)):return '$'+value+'$'
            return value
        if typ=='tables':return table_markdown(result['tables'][key])
        if typ=='replacements':return str(result['replacements'][key])
        raise ValueError('Unknown replacement '+m[1])
    out=re.sub(r'\{\{([\w.-]+)\}\}',replace,template)
    if '{{' in out:raise ValueError('Unresolved report replacements')
    out=MATH.sub(lambda m:re.sub(r'(?<!\\)\|',r'\\vert ',m[0]),out)
    out=re.sub(r'(?m)^(\s*\d+)\\\.',r'\1.',out)
    out=re.sub(r'\\\((\d+)\\\)',r'(\1)',out)
    out=re.sub(r'(?m)^([图表]\s*\d+[^\n]*)$',r'\n\n\1\n\n',out)
    return out

MATH=re.compile(r'(\$\$[\s\S]*?\$\$|(?<!\$)\$[^$\n]+\$(?!\$))')
def runs(text):
    return [{'kind':'math' if t.startswith('$') else 'text','text':t.strip('$') if t.startswith('$') else t,'boxes':tex_boxes(t.strip('$')) if t.startswith('$') else ''} for t in MATH.split(text.replace('**','')) if t]
def blocks(text):
    text=re.sub(r'(\$\$.*?\$\$)',r'\n\n\1\n\n',text,flags=re.S);out=[]
    for b in re.split(r'\n\s*\n',text.strip()):
        b=b.strip()
        if not b:continue
        if b.startswith('#'):
            m=re.match(r'(#+)\s+(.*)',b);out.append({'type':'heading','level':len(m[1]),'runs':runs(m[2])})
        elif b.startswith('$$'):out.append({'type':'math','text':b.strip('$'),'boxes':tex_boxes(b.strip('$'))})
        elif b.startswith('|'):
            rows=[[c.strip().replace(r'\|','|') for c in re.split(r'(?<!\\)\|',line.strip().strip('|'))] for line in b.splitlines()]
            out.append({'type':'table','rows':[[runs(c) for c in row] for row in [rows[0],*rows[2:]]]})
        elif b.startswith('!['):
            m=re.match(r'!\[([^\]]*)\]\(([^)]+)\)',b);key=Path(m[2]).stem
            out.append({'type':'figure','key':key})
        else:out.append({'type':'caption' if re.match(r'^[图表]\s*\d+',b) else 'text','runs':runs(b)})
    return out

def chunks(report,a):
    # Insert expansions at the end of their matching main section.
    pieces=re.split(r'(?=^## )',report,flags=re.M)
    for piece in pieces:
        if not piece.strip():continue
        yield ('report',piece)
        match=re.match(r'^## (.+)',piece)
        if match:
            section=re.sub(r'[*：:]','',match[1]).strip()
            for i,e in enumerate(a.get('expansions',[])):
                if re.sub(r'[*：:]','',e['section']).strip()==section:yield ('expansion',(i,e))

def setup_source(entry):
    return f'''from pathlib import Path
import sys
ROOT=next(p for p in (Path.cwd(),*Path.cwd().parents) if (p/'pyproject.toml').exists())
sys.path.insert(0,str(ROOT/'src'))
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display,Markdown,HTML
from physicslab.common.theme import EXPORT_CSS
from physicslab.common.manuscripts import table_display,metrics_display,display_plotly,series_plot
from physicslab.experiments import {entry['module']} as adapter
EXP=ROOT/'experiments/{entry['id']}'
result=adapter.analyze(EXP)
import json
labels=json.loads((EXP/'authoring.json').read_text(encoding='utf-8')).get('metric_labels',{{}})
for key,value in result['metrics'].items():value.setdefault('label',labels.get(key,key))
display(HTML(EXPORT_CSS))
'''

def notebook(work,entry,a,report):
    import nbformat as nbf
    from nbclient import NotebookClient
    cells=[nbf.v4.new_code_cell(setup_source(entry),metadata={'tags':['setup'],'jupyter':{'source_hidden':True}})]
    payload=[]
    for kind,value in chunks(report,a):
        if kind=='report':
            cell=nbf.v4.new_markdown_cell(value)
            def attach(m):
                path=(work/'experiments'/entry['id']/'report'/m[2]).resolve()
                if not path.is_file():raise FileNotFoundError(path)
                name=path.name;mime='image/svg+xml' if path.suffix=='.svg' else 'image/png'
                cell.setdefault('attachments',{})[name]={mime:base64.b64encode(path.read_bytes()).decode()}
                return f'![{m[1]}](attachment:{name})'
            cell.source=re.sub(r'!\[([^\]]*)\]\(([^)]+)\)',attach,value)
            cells.append(cell);payload.extend(blocks(value))
        else:
            i,e=value
            cells.append(nbf.v4.new_markdown_cell('#### '+e['title']+'\n\n'+e.get('prose','')))
            payload.extend(blocks('#### '+e['title']+'\n\n'+e.get('prose','')))
            cap=e.get('caption');before=e.get('caption_position')=='before' or bool(cap and cap.startswith('表'))
            if cap and before:cells.append(nbf.v4.new_markdown_cell(cap));payload.extend(blocks(cap))
            code='import physicslab.common.manuscripts as _presentation\n_presentation._table_captioned='+repr(bool(cap and before))+'\n'+e['python']
            cells.append(nbf.v4.new_code_cell(code,metadata={'jupyter':{'source_hidden':True}}))
            payload.append({'type':'compute','index':i+1})
            if cap and not before:cells.append(nbf.v4.new_markdown_cell(cap));payload.extend(blocks(cap))
    for i,c in enumerate(cells):c['id']=f"{entry['slug']}-{i:03}"
    nb=nbf.v4.new_notebook(cells=cells,metadata={'kernelspec':{'name':'python3','display_name':'Python 3','language':'python'},'language_info':{'name':'python'},'physicslab':{'experiment_id':entry['id'],'chinese_font':'SimSun','latin_font':'Times New Roman'}})
    envdir=work/'.build/jupyter';kernel=envdir/'kernels/physicslab';kernel.mkdir(parents=True)
    write_json(kernel/'kernel.json',{'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],'display_name':'Physics Lab','language':'python'})
    previous=os.environ.get('JUPYTER_PATH');os.environ['JUPYTER_PATH']=str(envdir)+(os.pathsep+previous if previous else '')
    try:NotebookClient(nb,timeout=180,kernel_name='physicslab',resources={'metadata':{'path':str(work)}}).execute()
    finally:
        if previous is None:os.environ.pop('JUPYTER_PATH',None)
        else:os.environ['JUPYTER_PATH']=previous
    nbf.validate(nb)
    exp=work/'experiments'/entry['id'];path=exp/'notebooks/analysis.ipynb';path.parent.mkdir(exist_ok=True)
    nbf.write(nb,path)
    html_export(nb,path.with_suffix('.html'),path.parent)
    return payload,{'status':'passed','code_cells':sum(c.cell_type=='code' for c in cells),'outputs':sum(len(c.get('outputs',[])) for c in nb.cells)}

def html_export(nb,path,base):
    from nbconvert import HTMLExporter
    from physicslab.common.theme import polish_export
    html,_=HTMLExporter(exclude_input=True).from_notebook_node(nb)
    path.write_text(polish_export(inline_images(html,base)),encoding='utf-8')

def compare(p,w,a):
    import math
    checks=[]
    for key in a['comparison']:
        pv=p['metrics'][key];wv=w['metrics'][key]
        if pv['unit']!=wv['unit']:raise ValueError('Unit mismatch '+key)
        settings=a.get('tolerances',{}).get(key,{})
        scale=abs(float(pv['value']))
        ok=math.isclose(float(pv['value']),float(wv['value']),rel_tol=settings.get('rtol',1e-8),abs_tol=settings.get('atol',min(1e-10,scale*1e-10) if scale else 1e-14))
        checks.append({'metric':key,'python':pv['value'],'wolfram':wv['value'],'unit':pv['unit'],'passed':ok})
    if set(p.get('tables',{}))!=set(w.get('tables',{})):raise ValueError('Computed table keys differ between engines')
    for key,table in p.get('tables',{}).items():
        other=w['tables'][key]
        if len(table['rows'])!=len(other['rows']):raise ValueError('Table row count differs '+key)
        for i,(left,right) in enumerate(zip(table['rows'],other['rows'])):
            if len(left)!=len(right):raise ValueError('Table column count differs '+key)
            for j,(pv,wv) in enumerate(zip(left,right)):
                if isinstance(pv,(int,float)) and isinstance(wv,(int,float)):
                    checks.append({'table':key,'row':i,'column':j,'passed':math.isclose(float(pv),float(wv),rel_tol=1e-7,abs_tol=1e-9)})
    if not checks or not all(c['passed'] for c in checks):raise AssertionError([c for c in checks if not c['passed']])
    return {'status':'passed','checks':checks}

def ensure_readme(exp,entry,a):
    """Create an initial entry while preserving an existing experiment guide."""
    path=exp/'README.md'
    if path.exists():return
    readme=f"# {a['title']}\n\n[实验报告](report/report.md) · [报告阅读版](report/report.html) · [Jupyter Notebook](notebooks/analysis.ipynb) · [Notebook 阅读版](notebooks/analysis.html) · [Wolfram Notebook](../../../notebook/paclets/{entry['paclet']}/Notebooks/{entry['paclet']}.nb)\n\n计算使用随项目提供的规范数据。Notebook 可在新内核中依次执行。\n"
    path.write_text(readme,encoding='utf-8')

def build(entry,skip_frontend=False):
    a=author(entry);exp=ROOT/'experiments'/entry['id'];run_id=stamp();run=ROOT/'.build'/entry['id']/run_id
    run.mkdir(parents=True,exist_ok=True)
    # Keep Wolfram's native file APIs below Windows MAX_PATH even when the caller's
    # staging checkout has a long desktop task path.
    work=Path(os.environ.get('PHYSICSLAB_BUILD_ROOT',str(ROOT/'.build/runs')))/hashlib.sha256(entry['id'].encode()).hexdigest()[:8]/run_id
    state(entry,'material_checked',run=str(run))
    lock=ROOT/'.build'/entry['id']/'build.lock';lock.parent.mkdir(parents=True,exist_ok=True)
    with lock.open('x') as f:f.write(str(os.getpid()))
    try:
        source_paths=[exp/'authoring.json',exp/'experiment.json',exp/'report/report.template.md',*list((exp/'data').glob('*')),*list((exp/'assets').glob('*')),ROOT/'src/physicslab/experiments'/(entry['module']+'.py'),ROOT/'notebook/paclets'/entry['paclet']/'Kernel/analysis.wl']
        source_snapshot=digest(source_paths,ROOT)
        shutil.copytree(exp,work/'experiments'/entry['id'],ignore=shutil.ignore_patterns('results','notebooks','report.md','report.html'))
        shutil.copytree(ROOT/'src',work/'src',ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copy2(ROOT/'pyproject.toml',work/'pyproject.toml')
        package=ROOT/'notebook/paclets'/entry['paclet'];paclet=work/'notebook/paclets'/entry['paclet']
        shutil.copytree(package,paclet,ignore=shutil.ignore_patterns('dist','exports','Notebooks','data'))
        tmp=work/'experiments'/entry['id'];results=tmp/'results';results.mkdir()
        observations=input_hashes(tmp)
        module_name='physicslab.experiments.'+entry['module']
        spec=importlib.util.spec_from_file_location(module_name,work/'src/physicslab/experiments'/(entry['module']+'.py'))
        adapter=importlib.util.module_from_spec(spec);sys.modules[module_name]=adapter;spec.loader.exec_module(adapter)
        p=adapter.analyze(tmp)
        for key,value in p['metrics'].items():value.setdefault('label',a.get('metric_labels',{}).get(key,key))
        # JSON serialization also rejects NaN and infinities before manuscript generation.
        dependencies=[work/'src/physicslab/experiments'/(entry['module']+'.py'),*list((work/'src/physicslab/common').glob('*.py'))]
        p.update({'experiment_id':entry['id'],'engine':'python','input_hashes':observations,'code_hashes':digest(dependencies,work),'environment':{'python':sys.version.split()[0],**{name:importlib.metadata.version(name) for name in ('numpy','scipy','matplotlib','nbclient','nbformat','plotly')}}})
        write_json(results/'python.json',p)
        for check in a.get('python_checks',[]):
            namespace={'result':p,'adapter':adapter,'EXP':tmp,'np':__import__('numpy')}
            if check.lstrip().startswith('assert '):exec(check,namespace)
            elif not eval(check,namespace):raise AssertionError(check)
        state(entry,'python_computed',run=str(run),input_hashes=observations)
        figures=results/'figures';figures.mkdir()
        import matplotlib.pyplot as plt
        for key,s in p.get('series',{}).items():
            fig=series_figure(s)
            for suffix in ('svg','png'):fig.savefig(figures/(key+'.'+suffix),dpi=200)
            plt.close(fig)
        print('FIGURES_OK',entry['id'],flush=True)
        report=render_report((tmp/'report/report.template.md').read_text(encoding='utf-8'),p)
        if sections(report)!=[re.sub(r'[*：:]','',s).strip() for s in a['sections']]:raise AssertionError('Report outline differs from declared DOCX outline')
        (tmp/'report/report.md').write_text(report,encoding='utf-8')
        import nbformat
        html_export(nbformat.v4.new_notebook(cells=[nbformat.v4.new_markdown_cell(report)]),tmp/'report/report.html',tmp/'report')
        print('REPORT_OK',entry['id'],flush=True)
        payload,jupyter=notebook(work,entry,a,report)
        print('JUPYTER_OK',entry['id'],flush=True)
        write_json(results/'jupyter-execution.json',jupyter)
        state(entry,'jupyter_executed',run=str(run))
        (paclet/'data').mkdir()
        if (tmp/'assets').is_dir():shutil.copytree(tmp/'assets',paclet/'assets',dirs_exist_ok=True)
        for block in payload:
            if block['type']=='figure' and block['key'] not in p.get('series',{}):
                matches=list((tmp/'assets').glob(block['key']+'.*'))
                if len(matches)!=1:raise ValueError('Missing figure/asset '+block['key'])
                block.update(type='asset',name=matches[0].name)
        shutil.copy2(tmp/'experiment.json',paclet/'data/experiment.json');shutil.copytree(tmp/'data',paclet/'data/data')
        for name,value in [('authoring.json',a),('report.json',payload),('python-reference.json',p),('input-hashes.json',observations)]:write_json(paclet/'data'/name,value)
        from wolfram_batch import generate,execute
        generate(paclet,entry,a)
        execute(paclet,run,skip_frontend)
        w=read_json(paclet/'exports/wolfram.json')
        if w.get('input_hashes')!=observations:raise AssertionError('Wolfram actual input hashes differ')
        w['engine']='wolfram';w['experiment_id']=entry['id']
        write_json(results/'wolfram.json',w)
        verification=compare(p,w,a);verification['input_hashes']=observations;write_json(results/'verification.json',verification)
        visual=read_json(paclet/'exports/validation.json')
        if not visual['passed']:raise AssertionError(visual)
        state(entry,'execution_compared',run=str(run),checks=len(verification['checks']))
        write_json(results/'presentation-validation.json',{'status':'awaiting_visual_review','native':visual,'sections':a['sections'],'formulas':'native box grammar parsed; browser review pending','font_families':['SimSun','Times New Roman'],'limitations':a.get('limitations',[])})
        if digest(source_paths,ROOT)!=source_snapshot:
            raise RuntimeError('Author sources changed during execution; preserving current sources and previous manuscripts for a fresh retry')
        # Publish into rollout staging only. A separately guarded deploy copies reviewed results to project.
        for folder in ('report','notebooks','results'):shutil.copytree(tmp/folder,exp/folder,dirs_exist_ok=True)
        shutil.copytree(paclet,package,dirs_exist_ok=True)
        ensure_readme(exp,entry,a)
        state(entry,'awaiting_visual_review',run=str(run),checks=len(verification['checks']),limitations=a.get('limitations',[]))
        print('BUILD_OK',entry['id'],len(verification['checks']),flush=True)
        return run
    except Exception as exc:
        state(entry,'failed',run=str(run),error=str(exc));raise
    finally:lock.unlink(missing_ok=True)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--experiment');parser.add_argument('--all',action='store_true');parser.add_argument('--skip-frontend',action='store_true');parser.add_argument('--list',action='store_true');args=parser.parse_args()
    entries=registry()
    if args.list:
        for e in entries:print(e['id'],e['title'])
        return
    selected=[e for e in entries if e['id']==args.experiment] if args.experiment else [e for e in entries if e['slug']!='pendulum'] if args.all else []
    if not selected:parser.error('Choose --experiment or --all')
    failures=[]
    for entry in selected:
        if not (ROOT/'experiments'/entry['id']/'authoring.json').exists():failures.append({'id':entry['id'],'error':'not authored'});continue
        try:build(entry,args.skip_frontend)
        except Exception as exc:failures.append({'id':entry['id'],'error':str(exc)});print('BUILD_FAILED',entry['id'],str(exc),flush=True)
    write_json(ROOT/'.build/batch-summary.json',{'selected':len(selected),'failures':failures})
    if failures:raise SystemExit(1)

if __name__=='__main__':main()
