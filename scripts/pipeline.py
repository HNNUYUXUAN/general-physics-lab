"""Project workflow: prepare, compute, execute, compare, render and validate."""
from pathlib import Path
import argparse, csv, hashlib, json, os, shutil, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from physicslab.common.io import read_json,write_json,input_hashes,sha256
EXP=ROOT/'experiments/course-01/pendulum'
PACLET=ROOT/'notebook/paclets/PendulumLab'
RESULTS=EXP/'results'

def prepare():
    for name in ('experiment.json','data/measurements.csv','data/diameters.csv','data/provenance.json'):
        target=PACLET/'data'/name;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(EXP/name,target)
        if sha256(target)!=sha256(EXP/name): raise RuntimeError('Paclet input copy mismatch')
    RESULTS.mkdir(parents=True,exist_ok=True)
    print('PREPARE_OK')

def python_compute():
    from physicslab.experiments.pendulum import analyze
    from physicslab.common.plots import export_figures
    result=analyze(EXP)
    write_json(RESULTS/'python.json',result)
    export_figures(result,RESULTS/'figures')
    print('PYTHON_OK',result['metrics']['gravity_fit'])

def wolfram():
    executable=os.environ.get('WOLFRAMSCRIPT') or shutil.which('wolframscript')
    if not executable:
        candidate=Path('C:/Program Files/Wolfram Research/WolframScript/wolframscript.exe')
        if candidate.exists(): executable=str(candidate)
    if not executable: raise RuntimeError('WolframScript unavailable; set WOLFRAMSCRIPT. Wolfram validation remains unverified.')
    subprocess.run([executable,'-file',str(PACLET/'Support/build.wls')],cwd=ROOT,check=True)
    shutil.copyfile(PACLET/'exports/wolfram.json',RESULTS/'wolfram.json')
    shutil.copyfile(PACLET/'exports/tests.json',RESULTS/'wolfram-tests.json')

def compare():
    import numpy as np
    p=read_json(RESULTS/'python.json');w=read_json(RESULTS/'wolfram.json');c=read_json(EXP/'experiment.json');tol=c['comparison']
    if p['input_hashes']!=input_hashes(EXP) or w['input_hashes']!=input_hashes(EXP): raise ValueError('Stale input hashes')
    if p['code_hash']!=sha256(ROOT/'src/physicslab/experiments/pendulum.py') or w['code_hash']!=sha256(PACLET/'Kernel/PendulumLab.wl'): raise ValueError('Stale computation code hashes')
    if p['model_parameters']!=c['simulation'] or w['model_parameters']!=c['simulation']: raise ValueError('Model parameters differ')
    checks=[]
    def check(name,a,b,simulation=False):
        rtol=tol['simulation_rtol' if simulation else 'metrics_rtol']; atol=tol['simulation_atol' if simulation else 'metrics_atol']
        aa=np.asarray(a,dtype=float);bb=np.asarray(b,dtype=float)
        ok=aa.shape==bb.shape and np.all(np.isfinite(aa)) and np.all(np.isfinite(bb)) and np.allclose(aa,bb,rtol=rtol,atol=atol)
        checks.append({'name':name,'passed':bool(ok),'max_absolute_difference':float(np.max(np.abs(aa-bb))) if aa.shape==bb.shape else None,'rtol':rtol,'atol':atol})
    if set(p['metrics'])!=set(w['metrics']): raise ValueError('Metric keys differ')
    for key,value in p['metrics'].items():
        if value['unit']!=w['metrics'][key]['unit']: raise ValueError('Metric units differ')
        check('metrics.'+key,value['value'],w['metrics'][key]['value'])
    for collection in ('processed','amplitude_scan'):
        if len(p[collection])!=len(w[collection]): raise ValueError('Result row counts differ')
        for key in p[collection][0]: check(collection+'.'+key,[r[key] for r in p[collection]],[r[key] for r in w[collection]])
    check('residuals',p['residuals_s2'],w['residuals_s2'])
    for key in ('time_s','angle_rad','angular_velocity_rad_s','linear_angle_rad','period_ode_s','period_exact_s'):
        check('simulation.'+key,p['simulation'][key],w['simulation'][key],True)
    for engine,result in [('python',p),('wolfram',w)]:
        s=result['simulation']
        checks.append({'name':engine+'.energy_conservation','passed':s['relative_energy_drift']<1e-7,'max_relative_drift':s['relative_energy_drift']})
        checks.append({'name':engine+'.period_reference','passed':abs(s['period_ode_s']/s['period_exact_s']-1)<1e-7})
    passed=all(item['passed'] for item in checks)
    record={'status':'passed' if passed else 'failed','input_hashes':p['input_hashes'],'code_hashes':{'python':p['code_hash'],'wolfram':w['code_hash']},'engines':{'python':p['environment'],'wolfram':w['environment']},'checks':checks}
    write_json(RESULTS/'verification.json',record)
    if not passed: raise AssertionError([x for x in checks if not x['passed']])
    print('CROSS_LANGUAGE_OK',len(checks))
    return record

def table(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(map(str,row))+' |' for row in rows])

def render_report(validate=True):
    from physicslab.experiments.pendulum import load_data
    if validate: compare()
    r=read_json(RESULTS/'python.json'); c,t,d=load_data(EXP); m=r['metrics']; s=r['simulation']
    value=lambda key:m[key]['value']
    replacements={
     'diameter_cm':f"{value('diameter_mean')*100:.3f}",'radius_cm':f"{value('diameter_mean')*50:.3f}",
     'diameter_horizontal':table(['测量次数',*[str(i) for i in range(1,len(d)+1)],'平均值'],[['直径 / cm',*[f"{float(x['diameter_cm']):.3f}" for x in d],f"{value('diameter_mean')*100:.3f}"]]),
     'source_measurement_table':table(['组号','摆线长 $L/\\mathrm{cm}$','$t_1/\\mathrm{s}$','$t_2/\\mathrm{s}$','$t_3/\\mathrm{s}$','平均 $\\bar t/\\mathrm{s}$','周期 $T/\\mathrm{s}$','$T^2/\\mathrm{s^2}$'],[[p['run_id'],f"{p['string_length_m']*100:.2f}",*[f"{float(q['elapsed_time_s']):.2f}" for q in t if int(q['run_id'])==p['run_id']],f"{p['mean_time_s']:.5f}",f"{p['period_s']:.6f}",f"{p['period_squared_s2']:.6f}"] for p in r['processed']]),
     'individual_calculations':table(['组号','有效摆长 $L^\\prime/\\mathrm{m}$','$T^2/\\mathrm{s^2}$','$g_i/(\\mathrm{m/s^2})$'],[[p['run_id'],f"{p['effective_length_m']:.4f}",f"{p['period_squared_s2']:.6f}",f"{p['gravity_individual_m_s2']:.6f}"] for p in r['processed']]),
     'fit_points':table(['$x_i/\\mathrm{m}$','$y_i/\\mathrm{s^2}$'],[[f"{p['effective_length_m']:.4f}",f"{p['period_squared_s2']:.6f}"] for p in r['processed']]),
     'individual_mean':f"{value('gravity_individual_mean'):.6f}",
     'x_mean':f"{sum(p['effective_length_m'] for p in r['processed'])/len(r['processed']):.7f}",
     'y_mean':f"{sum(p['period_squared_s2'] for p in r['processed'])/len(r['processed']):.7f}",
     'slope':f"{value('slope'):.8f}",'intercept':f"{value('intercept'):.8f}",
     'reference_abs_difference':f"{abs(value('reference_relative_difference_pct')):.4f}",
     'data_version':c['data_version'],'model_length':f"{c['simulation']['length_m']:g}",'model_angle':f"{c['simulation']['initial_angle_deg']:g}",'model_omega':f"{c['simulation']['initial_angular_velocity_rad_s']:g}",
     'diameter_table':table(['重复序号','直径 / cm'],[[x['repeat_id'],x['diameter_cm']] for x in d]),
     'observation_table':table(['组号','摆线长 / cm','全振动次数','$t_1/\\mathrm{s}$','$t_2/\\mathrm{s}$','$t_3/\\mathrm{s}$'],[[run,rows[0]['string_length_cm'],c['oscillations'],*[q['elapsed_time_s'] for q in rows]] for run in range(1,7) for rows in [[q for q in t if int(q['run_id'])==run]]]),
     'processed_table':table(['组号','有效摆长 / m','平均计时 / s','周期 / s','周期平方 / s²','u_A(T) / s','逐组 g / (m/s²)'],[[x['run_id'],f"{x['effective_length_m']:.5f}",f"{x['mean_time_s']:.6f}",f"{x['period_s']:.7f}",f"{x['period_squared_s2']:.8f}",f"{x['period_u_a_s']:.7f}",f"{x['gravity_individual_m_s2']:.6f}"] for x in r['processed']]),
     'metrics_table':table(['指标','数值','单位'],[[label,f'{value(key):.9g}',m[key]['unit']] for key,label in [('slope','拟合斜率'),('intercept','拟合截距'),('r_squared','决定系数'),('gravity_fit','重力加速度'),('gravity_regression_standard_error','重力回归标准误'),('gravity_individual_mean','逐组重力平均值')]]),
     'source_comparison':table(['指标','源报告','重新计算'],[['斜率 / (s²/m)',c['source_report_values']['slope_s2_m'],f"{value('slope'):.8f}"],['g / (m/s²)',c['source_report_values']['gravity_m_s2'],f"{value('gravity_fit'):.8f}"]]),
     'scan_table':table(['初始摆角 / °','非线性周期 / s','周期增量 / %','重力估计偏差 / %'],[[x['angle_deg'],f"{x['period_s']:.7f}",f"{x['period_excess_pct']:.5f}",f"{x['gravity_bias_pct']:.5f}"] for x in r['amplitude_scan']]),
     'diameter_mean':f"{value('diameter_mean'):.6f}",'diameter_u':f"{value('diameter_mean_u_a'):.3g}",
     'gravity':f"{value('gravity_fit'):.6f}",'gravity_se':f"{value('gravity_regression_standard_error'):.6f}",
     'reference_difference':f"{value('reference_relative_difference_pct'):.4f}",
     'period_ode':f"{s['period_ode_s']:.8f}",'period_exact':f"{s['period_exact_s']:.8f}",'energy_drift':f"{s['relative_energy_drift']:.3g}",
     'input_digest':hashlib.sha256(json.dumps(r['input_hashes'],sort_keys=True).encode()).hexdigest()}
    template=(EXP/'report/report.template.md').read_text(encoding='utf-8')
    for key,value_ in replacements.items(): template=template.replace('{{'+key+'}}',str(value_))
    if '{{' in template: raise ValueError('Unresolved report placeholders')
    (EXP/'report/report.md').write_text(template,encoding='utf-8')
    from build_notebook import export_wolfram
    export_wolfram(ROOT)
    import nbformat
    from nbconvert import HTMLExporter
    from physicslab.common.theme import polish_export
    import base64,re
    html,_=HTMLExporter(exclude_input=True).from_notebook_node(nbformat.v4.new_notebook(cells=[nbformat.v4.new_markdown_cell(template)]))
    def inline_image(match):
        name=match.group(1)
        path=(EXP/'report'/name).resolve()
        if path.suffix=='.svg' and path.is_file():
            return 'src="data:image/svg+xml;base64,'+base64.b64encode(path.read_bytes()).decode()+'"'
        return match.group(0)
    html=re.sub(r'src="([^"]+)"',inline_image,html)
    (EXP/'report/report.html').write_text(polish_export(html),encoding='utf-8')
    print('REPORT_OK' if validate else 'REPORT_DRAFT_READY')

def notebook():
    import nbformat
    from nbclient import NotebookClient
    from nbconvert import HTMLExporter
    from build_notebook import build
    path=build(ROOT)
    # An isolated kernel specification binds execution to this exact Python environment.
    kernelbase=ROOT/'.build/jupyter'; kernel=kernelbase/'kernels/physicslab';kernel.mkdir(parents=True,exist_ok=True)
    write_json(kernel/'kernel.json',{'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],'display_name':'Physics Lab','language':'python'})
    old=os.environ.get('JUPYTER_PATH');os.environ['JUPYTER_PATH']=str(kernelbase)+(os.pathsep+old if old else '')
    nb=nbformat.read(path,as_version=4)
    NotebookClient(nb,timeout=180,kernel_name='physicslab',resources={'metadata':{'path':str(ROOT)}}).execute()
    # Remove machine-specific kernel name while retaining all real outputs.
    nb.metadata.kernelspec={'name':'python3','display_name':'Python 3','language':'python'}
    nbformat.validate(nb);nbformat.write(nb,path)
    html,_=HTMLExporter(exclude_input=True).from_notebook_node(nb)
    from physicslab.common.theme import polish_export
    html=polish_export(html)
    preview=ROOT/'.build/preview';preview.mkdir(parents=True,exist_ok=True)
    (preview/'analysis.html').write_text(html,encoding='utf-8')
    (path.parent/'analysis.html').write_text(html,encoding='utf-8')
    write_json(RESULTS/'jupyter-execution.json',{'status':'passed','code_cells':sum(x.cell_type=='code' for x in nb.cells),'output_cells':sum(bool(x.get('outputs')) for x in nb.cells),'input_hashes':input_hashes(EXP),'python':sys.version.split()[0]})
    print('NOTEBOOK_OK')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['prepare','python','wolfram','compare','report','notebook','all','python-only'])
    parser.add_argument('--experiment');parser.add_argument('--all',action='store_true')
    args=parser.parse_args();cmd=args.command
    if args.all or (args.experiment and args.experiment!='course-01/pendulum'):
        if cmd!='all':parser.error('Registered experiment builds use: all --experiment <id> or all --all; all stages run in isolation before publishing.')
        import batch
        sys.argv=[sys.argv[0],*(['--all'] if args.all else ['--experiment',args.experiment])]
        return batch.main()
    steps={'prepare':prepare,'python':python_compute,'wolfram':wolfram,'compare':compare,'report':render_report,'notebook':notebook}
    if cmd=='all':
        for action in (prepare,python_compute,lambda:render_report(False),wolfram,render_report,notebook):action()
    elif cmd=='python-only':
        python_compute();notebook()
        write_json(ROOT/'.build/ci-status.json',{'python':'executed','wolfram':'not_run','cross_language':'not_run'})
    else:steps[cmd]()

if __name__=='__main__':main()
