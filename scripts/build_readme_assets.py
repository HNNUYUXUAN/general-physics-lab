"""Render experiment guide illustrations from saved canonical calculation results."""
from pathlib import Path
import argparse, hashlib, json, re, sys, textwrap
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import warnings
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Patch
from matplotlib.text import Text

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from physicslab.common.plots import style,fit_figure,trajectory_figure,scan_figure
from physicslab.common.manuscripts import axis_label
plt.rcParams['mathtext.fallback']='stix'
warnings.filterwarnings('error',message=r'Glyph.*missing from font')

def read(path):return json.loads(path.read_text(encoding='utf-8'))

def guide_label(text):
    return re.sub(r'\\circ([A-Za-z])',r'\\circ \1',axis_label(text))

def outside_legend(ax):
    handles,labels=ax.get_legend_handles_labels()
    if handles:ax.legend(handles,[guide_label(s) for s in labels],loc='lower left',bbox_to_anchor=(0,1.015),borderaxespad=0,ncol=1,frameon=False,prop={'family':'SimSun','size':13})

def save(fig,path):
    fig.canvas.draw();renderer=fig.canvas.get_renderer();bounds=fig.bbox
    clipped=[];legends=[];hidden_ticks=set()
    for ax in fig.axes:
        for axis in (ax.xaxis,ax.yaxis):
            low,high=sorted(axis.get_view_interval())
            for tick in axis.get_major_ticks():
                if not low<=tick.get_loc()<=high:hidden_ticks.update((id(tick.label1),id(tick.label2)))
    for text in fig.findobj(Text):
        if id(text) in hidden_ticks or not text.get_visible() or not text.get_text().strip():continue
        box=text.get_window_extent(renderer)
        if box.x0<bounds.x0-3 or box.y0<bounds.y0-3 or box.x1>bounds.x1+3 or box.y1>bounds.y1+3:
            clipped.append(text.get_text())
    for ax in fig.axes:
        legend=ax.get_legend()
        if legend:
            box=legend.get_window_extent(renderer);area=ax.get_window_extent(renderer)
            assert box.y0>=area.y1-2,('legend overlaps plotting area',str(path))
            legends.append(True)
    assert not clipped,('clipped text',str(path),clipped)
    path.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(path.with_suffix('.png'),dpi=180)
    fig.savefig(path.with_suffix('.svg'),metadata={'Date':None})
    plt.close(fig)
    return {'file':path.relative_to(ROOT).as_posix(),'legend_outside_axes':legends,'text_clipping':clipped}

def overview(steps):
    assert len(steps)==3
    style();fig,ax=plt.subplots(figsize=(12,3.5));fig.subplots_adjust(0,0,1,1)
    ax.set(xlim=(0,12),ylim=(0,3.5));ax.axis('off')
    font=FontProperties(family='SimSun')
    for i,s in enumerate(steps):
        x=i*4+.4
        ax.text(x,2.95,f'{i+1:02}',fontsize=25,color='#999',va='center')
        label='\n'.join(guide_label(t) for t in textwrap.wrap(s['label'],width=13))
        ax.text(x,2.28,label,fontproperties=font,fontsize=18,va='center',linespacing=1.5)
        formula=s.get('formula','').strip('$')
        t=ax.text(x,1.45,'$'+formula+'$' if formula else '',fontsize=19,va='center')
        fig.canvas.draw()
        while t.get_window_extent().width>fig.bbox.width*.265 and t.get_fontsize()>14:
            t.set_fontsize(t.get_fontsize()-1);fig.canvas.draw()
        assert t.get_window_extent().width<=fig.bbox.width*.28,('overview formula too long',formula)
        detail='\n'.join(guide_label(t) for t in textwrap.wrap(s.get('detail',''),width=22))
        ax.text(x,.5,detail,fontproperties=font,fontsize=13,color='#444',va='center',linespacing=1.5)
        if i<2:ax.plot([4*(i+1)-.08]*2,[.25,3.22],color='#ddd',lw=1)
    return fig

def chart(s):
    style();x=np.array(s['x'],dtype=float);y=np.array(s['y'],dtype=float)
    assert x.shape==y.shape and x.size and np.isfinite(x).all() and np.isfinite(y).all()
    if s.get('fit') and x.size>2 and np.ptp(x)>0:
        fig,(ax,res)=plt.subplots(2,1,figsize=(10.5,8.5),height_ratios=[2,1],layout='constrained')
        k,b=np.polyfit(x,y,1);xx=np.linspace(x.min(),x.max(),200)
        ax.plot(xx,k*xx+b,color='#222',label='含截距线性拟合')
        res.plot(x,y-(k*x+b),'o',mfc='white',mec='#222',color='#222')
        res.axhline(0,color='#888',ls='--',lw=1)
        unit=s.get('residual_unit')
        if unit is None:unit=s['y_label'].split(' / ',1)[1] if ' / ' in s['y_label'] else ''
        res.set(xlabel=guide_label(s['x_label']),ylabel=guide_label('残差'+(' / '+unit if unit else '')))
    else:fig,ax=plt.subplots(figsize=(10.5,6.6),layout='constrained')
    model=s.get('model',False)
    ax.plot(x,y,'-' if model else 'o-' if s.get('connect',False) else 'o',
        mfc='white',mec='#222',color='#222',label=s.get('label','理论模型' if model else '观测值'))
    ax.set(xlabel=guide_label(s['x_label']),ylabel=guide_label(s['y_label']))
    if s.get('equal_aspect'):ax.set_aspect('equal',adjustable='box')
    outside_legend(ax)
    for a in fig.axes:
        a.xaxis.label.set_fontfamily('SimSun');a.yaxis.label.set_fontfamily('SimSun')
    return fig

def build(entry):
    exp=ROOT/'experiments'/entry['id'];result=read(exp/'results/python.json');assets=exp/'assets';checks=[]
    if entry['slug']=='pendulum':
        for key,factory in [('fit',fit_figure),('trajectory',trajectory_figure),('amplitude-scan',scan_figure)]:
            fig=factory(result)
            if key=='fit':
                for t in list(fig.axes[0].texts):t.remove()
            if key=='amplitude-scan':
                for ax in fig.axes:
                    for t in list(ax.texts):t.remove()
                    ax.legend(handles=[Patch(facecolor='#eee',edgecolor='#aaa',label='小摆角范围：0—5°')],
                        loc='lower left',bbox_to_anchor=(0,1.015),borderaxespad=0,frameon=False,prop={'family':'SimSun','size':13})
            else:
                for ax in fig.axes:outside_legend(ax)
            for ax in fig.axes:
                ax.xaxis.label.set_fontfamily('SimSun')
                ax.yaxis.label.set_fontfamily('SimSun')
            checks.append(save(fig,assets/('readme-'+key)))
    else:
        plan=read(assets/'readme-plan.json');checks.append(save(overview(plan['overview']),assets/'readme-overview'))
        for item in plan['figures']:
            key=item['key'];assert re.fullmatch(r'[a-zA-Z0-9_.-]+',key),key
            series=dict(result['series'][key])
            series.update({k:item[k] for k in ('model','label','connect') if k in item})
            checks.append(save(chart(series),assets/('readme-'+key)))
    return {'id':entry['id'],'figures':checks}

def main():
    p=argparse.ArgumentParser();p.add_argument('--all',action='store_true');p.add_argument('--experiment');a=p.parse_args()
    entries=read(ROOT/'experiments/registry.json')['experiments']
    selected=entries if a.all else [e for e in entries if e['id']==(a.experiment or 'course-01/pendulum')]
    assert selected,'Unknown experiment'
    records=[]
    for entry in selected:
        try:
            records.append(build(entry));print(entry['id'],len(records[-1]['figures']),flush=True)
        except Exception as error:
            plt.close('all');records.append({'id':entry['id'],'error':str(error)})
            print(entry['id'],'FAILED',str(error),flush=True)
    output=ROOT/'.build/readme-assets';output.mkdir(parents=True,exist_ok=True)
    (output/'render-checks.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
    if any('error' in r for r in records):raise SystemExit(1)

if __name__=='__main__':main()
