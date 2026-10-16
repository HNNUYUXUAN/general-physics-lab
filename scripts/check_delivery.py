"""Read-only delivery audit; default remains the approved pendulum."""
from pathlib import Path
import argparse,hashlib,json,re,sys
import nbformat
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from physicslab.common.io import read_json,sha256
from batch import input_hashes,compare,sections,render_report

def audit(entry):
    exp=ROOT/'experiments'/entry['id'];package=ROOT/'notebook/paclets'/entry['paclet']
    report=(exp/'report/report.md').read_text(encoding='utf-8')
    assert '{{' not in report, 'unresolved report values'
    nb=nbformat.read(exp/'notebooks/analysis.ipynb',as_version=4);nbformat.validate(nb)
    code=[c for c in nb.cells if c.cell_type=='code']
    assert code and all(c.execution_count is not None for c in code), 'unexecuted notebook'
    assert not [o for c in code for o in c.outputs if o.output_type=='error']
    assert sections(report)==sections('\n'.join(c.source for c in nb.cells if c.cell_type=='markdown')), 'notebook outline differs'
    assert nb.metadata.physicslab.chinese_font=='SimSun' and nb.metadata.physicslab.latin_font=='Times New Roman'
    notebook_name='Pendulum.nb' if entry['slug']=='pendulum' else f"{entry['paclet']}.nb"
    required=[exp/'README.md',exp/'report/report.html',exp/'notebooks/analysis.html',package/'Notebooks'/notebook_name,package/'dist'/f"{entry['paclet']}-0.1.0.paclet"]
    assert all(x.is_file() and x.stat().st_size for x in required), 'missing deliverable'
    links=0
    for path in [exp/'README.md',exp/'report/report.md']:
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
            if re.match(r'^[a-zA-Z]+:',target) or target.startswith('#'):continue
            assert (path.parent/target.split('#')[0]).exists(), (path,target)
            links+=1
    v=read_json(exp/'results/verification.json');assert v['status']=='passed'
    record={'id':entry['id'],'status':'passed','code_cells':len(code),'cross_language_checks':len(v['checks']),'links_checked':links}
    if entry['slug']!='pendulum':
        a=read_json(exp/'authoring.json');py=read_json(exp/'results/python.json');wl=read_json(exp/'results/wolfram.json')
        assert report==render_report((exp/'report/report.template.md').read_text(encoding='utf-8'),py), 'report is not synchronized'
        assert py['input_hashes']==wl['input_hashes']==input_hashes(exp), 'stale input'
        for rel,digest in py['code_hashes'].items():assert sha256(ROOT/rel)==digest, 'stale Python code '+rel
        for rel,digest in wl['code_hashes'].items():assert sha256(package/rel)==digest, 'stale Wolfram code '+rel
        compare(py,wl,a)
        native=read_json(exp/'results/native-review.json');assert native['status']=='passed', 'native review pending'
        native_hash=native['notebook']['sha256'] if isinstance(native['notebook'],dict) else native['notebook_sha256']
        assert native_hash==sha256(required[3]), 'stale native review'
        html=read_json(exp/'results/browser-review.json');assert html['status']=='passed', 'browser review pending'
        for key,rel in [('report','report/report.html'),('notebook','notebooks/analysis.html')]:
            assert html[key]['sha256']==sha256(exp/rel), 'stale browser review'
            assert not html[key]['errors'] and not html[key]['raw_formula'] and not html[key]['overflow']
            assert html[key]['math_sources']==html[key]['math_rendered'], 'incomplete math rendering'
        assert html['controls_status']=='passed', 'browser controls pending'
        controls=read_json(exp/'results/native-interaction-review.json')
        assert controls['status'] in ('passed','not_applicable_static'), 'native parameter responses pending'
        if controls['status']=='passed':
            assert controls['source_hashes']['analysis.wl']==sha256(package/'Kernel/analysis.wl'), 'stale native interaction review'
            assert controls['input_hashes']==py['input_hashes'], 'stale native interaction inputs'
        assert sections(report)==[re.sub(r'[*：:]','',s).strip() for s in a['sections']]
        record['limitations']=a.get('limitations',[])
    return record

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--all',action='store_true');parser.add_argument('--experiment');args=parser.parse_args()
    entries=read_json(ROOT/'experiments/registry.json')['experiments']
    selected=entries if args.all else [e for e in entries if e['id']==(args.experiment or 'course-01/pendulum')]
    assert selected,'unknown experiment'
    results=[]
    for e in selected:
        try:results.append(audit(e))
        except Exception as ex:results.append({'id':e['id'],'status':'failed','error':str(ex)})
    print(json.dumps(results,ensure_ascii=False,indent=2))
    if any(r['status']!='passed' for r in results):raise SystemExit(1)
if __name__=='__main__':main()
