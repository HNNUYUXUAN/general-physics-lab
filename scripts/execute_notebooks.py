"""Execute saved notebooks in fresh kernels without replacing formal manuscripts."""
from pathlib import Path
import argparse,datetime,json,os,sys
import nbformat
from nbclient import NotebookClient
ROOT=Path(__file__).resolve().parents[1]

def main():
    args=argparse.ArgumentParser();args.add_argument('--all',action='store_true');args.add_argument('--experiment');opt=args.parse_args()
    entries=json.loads((ROOT/'experiments/registry.json').read_text(encoding='utf-8'))['experiments']
    selected=entries if opt.all else [e for e in entries if e['id']==(opt.experiment or 'course-01/pendulum')]
    assert selected,'unknown experiment'
    run=ROOT/'.build/notebook-checks'/datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f');kernel=run/'kernels/physicslab';kernel.mkdir(parents=True)
    (kernel/'kernel.json').write_text(json.dumps({'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],'display_name':'Physics Lab','language':'python'}),encoding='utf-8')
    os.environ['JUPYTER_PATH']=str(run)+os.pathsep+os.environ.get('JUPYTER_PATH','')
    records=[]
    for e in selected:
        try:
            nb=nbformat.read(ROOT/'experiments'/e['id']/'notebooks/analysis.ipynb',as_version=4)
            NotebookClient(nb,timeout=180,kernel_name='physicslab',resources={'metadata':{'path':str(ROOT)}}).execute()
            target=run/e['id']/'analysis.ipynb';target.parent.mkdir(parents=True,exist_ok=True);nbformat.write(nb,target)
            records.append({'id':e['id'],'status':'passed','code_cells':sum(c.cell_type=='code' for c in nb.cells)})
        except Exception as ex:records.append({'id':e['id'],'status':'failed','error':str(ex)})
        print(e['id'],records[-1]['status'],flush=True)
    (run/'execution.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
    if any(r['status']=='failed' for r in records):raise SystemExit(1)
if __name__=='__main__':main()
