"""Run registered virtual-laboratory checks in an isolated output directory."""
from __future__ import annotations
import argparse,datetime,hashlib,json,os,shutil,subprocess,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SUCCESS={'passed','pass'}
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def validate(root,entry,output):
    identity=entry['experiment_id'];folder=output/identity;folder.mkdir(parents=True,exist_ok=True)
    result={'experiment_id':identity,'model_version':entry['model_version'],
            'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'status':'not_run','checks':[],'source_files':{}}
    for name,path in entry['resources'].items():
        p=root/path
        if p.is_file():result['source_files'][path]=digest(p)
    validator=root/entry['validator'];tests=[root/p for p in entry['tests']]
    for p in [validator,*tests]:
        if p.is_file():result['source_files'][p.relative_to(root).as_posix()]=digest(p)
    if not validator.is_file() or any(not p.is_file() for p in tests):
        result['reason']='implementation_pending'
    else:
        node=shutil.which('node')
        if not node:raise RuntimeError('Node.js is required for browser model validation')
        runtime=sorted((root/entry['resources']['simulation_model']).parent.glob('*.mjs'))
        parse_script="const c=require('node:child_process'); for(const p of process.argv.slice(1))c.execFileSync(process.execPath,['--check',p],{stdio:'inherit'}); console.log('Parsed '+process.argv.slice(1).length+' runtime modules');"
        commands=[('runtime_syntax',[node,'-e',parse_script,*[str(p) for p in runtime]]),
          ('model_tests',[node,'--test',*[str(p) for p in tests]]),
          ('independent_reference',[sys.executable,str(validator),'--repo-root',str(root),
            '--output-root',str(folder),'--model',str(root/entry['resources']['simulation_model'])])]
        for name,command in commands:
            try:
                proc=subprocess.run(command,cwd=root,capture_output=True,text=True,encoding='utf-8',timeout=240)
                (folder/(name+'.log')).write_text(proc.stdout+'\n'+proc.stderr,encoding='utf-8')
                result['checks'].append({'name':name,'status':'passed' if proc.returncode==0 else 'failed','exit_code':proc.returncode})
            except subprocess.TimeoutExpired:
                result['checks'].append({'name':name,'status':'failed','reason':'timeout'})
        result['status']='passed' if all(c['status']=='passed' for c in result['checks']) else 'failed'
        reference=folder/entry['resources']['simulation_validation']
        if result['status']=='passed' and not reference.is_file():
            result['status']='failed';result['reason']='reference_artifact_missing'
        if reference.is_file():
            result['reference_artifact']=str(reference);result['reference_sha256']=digest(reference)
            artifact=read(reference)
            # The pendulum reference predates this registry and has per-section results.
            if entry['experiment_id']!='course-01/pendulum':
                model_hash=artifact.get('model_sha256',artifact.get('modelSha256'))
                if artifact.get('status') not in SUCCESS or model_hash!=digest(root/entry['resources']['simulation_model']):
                    result['status']='failed';result['reason']='reference_status_or_model_hash_mismatch'
    (folder/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    choice=p.add_mutually_exclusive_group(required=True);choice.add_argument('--experiment');choice.add_argument('--all',action='store_true')
    p.add_argument('--repo-root',type=Path,default=ROOT);p.add_argument('--output-root',type=Path)
    a=p.parse_args();root=a.repo_root.resolve()
    entries=read(root/'simulations/registry.json')['simulations']
    if a.experiment:
        entries=[e for e in entries if e['experiment_id']==a.experiment]
        if not entries:p.error('Unknown experiment: '+a.experiment)
    else:entries=[e for e in entries if e['status'] in {'implemented','validated','published'}]
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    output=(a.output_root or root/'.build/simulation-checks'/stamp).resolve()
    output.mkdir(parents=True,exist_ok=True)
    results=[validate(root,e,output) for e in entries]
    summary={'status':'passed' if results and all(r['status']=='passed' for r in results) else 'failed',
             'selected':len(results),'registered':45,'results':results}
    (output/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':summary['status'],'selected':len(results),'summary':str(output/'summary.json')},ensure_ascii=False))
    return 0 if summary['status']=='passed' else 1
if __name__=='__main__':sys.exit(main())
