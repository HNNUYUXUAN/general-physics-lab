"""Series RLC measurements; bandwidth estimates use observed peak amplitudes."""
from pathlib import Path
import csv
import json
import math


def half_power(frequencies, voltages):
    """Two crossings around the unique sampled maximum, by linear interpolation."""
    peak = max(range(len(voltages)), key=voltages.__getitem__)
    level = voltages[peak] / math.sqrt(2)
    def crossing(a, b):
        return frequencies[a] + (level-voltages[a])*(frequencies[b]-frequencies[a])/(voltages[b]-voltages[a])
    left = next(crossing(i, i+1) for i in range(peak-1, -1, -1) if voltages[i] <= level <= voltages[i+1])
    right = next(crossing(i, i+1) for i in range(peak, len(voltages)-1) if voltages[i+1] <= level <= voltages[i])
    return frequencies[peak], voltages[peak], left, right


def analyze(experiment_dir):
    base = Path(experiment_dir)
    config = json.loads((base/'experiment.json').read_text(encoding='utf-8'))
    with (base/'data/response.csv').open(encoding='utf-8', newline='') as fh:
        observations = list(csv.DictReader(fh))
    with (base/'data/resonance_voltages.csv').open(encoding='utf-8', newline='') as fh:
        resonance = list(csv.DictReader(fh))
    metrics, tables, series = {}, {}, {}
    estimates, voltage_rows, frequency_rows = [], [], []
    def add(key, value, unit):
        names={'f_theory':'理论谐振频率','f_peak':'观测峰值频率','U_peak':'观测峰值电压','f_low':'低频半功率交点','f_high':'高频半功率交点','bandwidth':'半功率带宽','Q_bandwidth':'带宽法品质因数','relative_error_percent':'峰值频率相对偏差','Q_voltage':'条件电压比品质因数','voltage_asymmetry_percent':'电感电容电压相对差','response_09':'频率比0.9时模型幅值','peak':'模型归一化峰值'}
        suffix=next((s for s in names if key.endswith('_'+s)),key)
        metrics[key] = {'value': float(value), 'unit': unit,'label':key[:-len(suffix)-1]+' '+names.get(suffix,suffix)}
    for group in config['groups']:
        gid, capacitance = group['id'], group['capacitance_F']
        data = [r for r in observations if r['group'] == gid]
        f = [float(r['frequency_Hz']) for r in data]
        if len(set(f)) != len(f) or any(b <= a for a,b in zip(f,f[1:])):
            raise ValueError('Frequencies must be unique and increasing')
        theory = 1/(2*math.pi*math.sqrt(config['inductance_H']*capacitance))
        add(f'{gid}_f_theory', theory, 'Hz')
        for resistor in ['R1', 'R2']:
            v = [float(r[f'U_{resistor}_V']) for r in data]
            if not all(math.isfinite(x) and x > 0 for x in v):
                raise ValueError('Voltage observations must be finite and positive')
            peak, vmax, f1, f2 = half_power(f,v)
            band, q = f2-f1, peak/(f2-f1)
            stem = f'{gid}_{resistor}'
            for key,value,unit in [('f_peak',peak,'Hz'),('U_peak',vmax,'V'),('f_low',f1,'Hz'),('f_high',f2,'Hz'),('bandwidth',band,'Hz'),('Q_bandwidth',q,'1')]:
                add(f'{stem}_{key}',value,unit)
            estimates.append([gid,resistor,peak,round(vmax,3),round(f1,3),round(f2,3),round(band,3),round(q,3)])
            series[stem] = {'x':f,'y':v,'x_label':r'频率 $f\,/\,\mathrm{Hz}$','y_label':rf'电阻电压 $U_{{{resistor}}}\,/\,\mathrm{{V}}$','label':f'{gid} / {resistor}'}
            series[f'{stem}_normalized'] = {'x':f,'y':[x/vmax for x in v],'x_label':r'频率 $f\,/\,\mathrm{Hz}$','y_label':r'归一化电压 $U_R/U_{R,\max}$','label':f'{gid} / {resistor}'}
        frequency = metrics[f'{gid}_R1_f_peak']['value']
        relative = (frequency-theory)/theory*100
        add(f'{gid}_relative_error_percent',relative,'%')
        frequency_rows.append([gid,capacitance*1e6,round(theory,3),frequency,round(relative,3)])
        for part,start,stop in [('a',0,10),('b',10,20)] if gid == 'C02' else [('a',0,len(f))]:
            rows=[['$f/\\mathrm{Hz}$']+f[start:stop]]
            for resistor in ['R1','R2']:
                rows.append([rf'$U_{{{resistor}}}/\mathrm{{V}}$']+[float(r[f'U_{resistor}_V']) for r in data[start:stop]])
            tables[f'{gid}_{part}']={'headers':['物理量']+[str(i+1+start) for i in range(len(f[start:stop]))], 'rows':rows}
    for row in resonance:
        gid, resistor = row['group'], row['resistor']
        ul,uc = float(row['U_L_V']),float(row['U_C_V'])
        q = (ul+uc)/(2*config['source_voltage_nominal_V'])
        add(f'{gid}_{resistor}_Q_voltage',q,'1')
        asymmetry = abs(ul-uc)/((ul+uc)/2)*100
        add(f'{gid}_{resistor}_voltage_asymmetry_percent',asymmetry,'%')
        voltage_rows.append([gid,resistor,ul,uc,round(q,3),round(asymmetry,3)])
    tables['frequencies']={'headers':['组别','$C/\\mu\\mathrm{F}$','$f_{0,\\mathrm{th}}/\\mathrm{Hz}$','$f_{\\mathrm{peak}}/\\mathrm{Hz}$','相对偏差 / %'],'rows':frequency_rows}
    tables['bandwidth']={'headers':['组别','电阻设置','$f_{\\mathrm{peak}}/\\mathrm{Hz}$','$U_{R,\\max}/\\mathrm{V}$','$f_1/\\mathrm{Hz}$','$f_2/\\mathrm{Hz}$','$B/\\mathrm{Hz}$','$Q_B$'],'rows':estimates}
    tables['voltage_ratio']={'headers':['组别','电阻设置','$U_L/\\mathrm{V}$','$U_C/\\mathrm{V}$','$Q_U$','两电压相对差 / %'],'rows':voltage_rows}
    # Dimensionless steady-state comparison: parameters fixed in experiment.json.
    q_values=config['model']['quality_factors']
    xs=[0.5+i/400 for i in range(401)]
    for q in q_values:
        series[f'model_Q{q}']={'x':xs,'y':[1/math.sqrt(1+q*q*(x-1/x)**2) for x in xs],'x_label':r'频率比 $f/f_0$','y_label':r'归一化电流 $I/I_{\max}$','label':f'理想模型 Q = {q}','model':True}
        add(f'model_Q{q}_response_09',1/math.sqrt(1+q*q*(.9-1/.9)**2),'1')
        add(f'model_Q{q}_peak',1,'1')
    return {'metrics':metrics,'tables':tables,'series':series,'notes':['半功率频率由相邻观测点线性插值，未拟合或补造观测。','电压比品质因数以源电压约 1 V 为条件；与带宽法的差异未归因于未经测量的内阻。']}


def explore(key, result):
    """Self-contained Plotly physical-parameter selection for HTML and notebook."""
    if key != 'resonance':
        raise KeyError(key)
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    x=[.5+i/600 for i in range(601)]
    fig=make_subplots(rows=1,cols=2,horizontal_spacing=.16)
    parameters=[(c,q) for c in [.2e-6,.1e-6] for q in [2,5,8,15,25]]
    for i,(c,q) in enumerate(parameters):
        f0=1/(2*math.pi*math.sqrt(.1*c))
        fig.add_trace(go.Scatter(x=[f0*a for a in x],y=[1/math.sqrt(1+q*q*(a-1/a)**2) for a in x],mode='lines',line={'color':'black','width':2},visible=i==2,showlegend=False),row=1,col=1)
        fig.add_trace(go.Scatter(x=[f0*a for a in x],y=[-math.atan(q*(a-1/a))*180/math.pi for a in x],mode='lines',line={'color':'black','width':2},visible=i==2,showlegend=False),row=1,col=2)
    steps=[]
    for i,(c,q) in enumerate(parameters):
        mask=[False]*(2*len(parameters));mask[2*i]=mask[2*i+1]=True
        steps.append({'method':'update','args':[{'visible':mask}],'label':f'C={c*1e6:.1f} μF / Q={q}'})
    fig.update_layout(height=510,width=1000,paper_bgcolor='white',plot_bgcolor='white',font={'family':'Times New Roman, SimSun','size':18},sliders=[{'active':2,'steps':steps,'currentvalue':{'prefix':'模型参数：'},'pad':{'t':55}}],margin={'l':85,'r':35,'t':30,'b':170})
    fig.update_xaxes(title_text='频率 f / Hz',showline=True,linecolor='black',gridcolor='#eeeeee',ticks='inside')
    fig.update_yaxes(title_text='归一化电流 I / Imax',range=[0,1.05],row=1,col=1,showline=True,linecolor='black',gridcolor='#eeeeee')
    fig.update_yaxes(title_text='电流相位 φ / °',range=[-90,90],row=1,col=2,showline=True,linecolor='black',gridcolor='#eeeeee')
    return fig


