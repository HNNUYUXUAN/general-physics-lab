"""Shared presentation of independently computed experiment results."""
from pathlib import Path
import re,base64
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display,HTML
from .plots import style
from .theme import FONT

_plotly_loaded=False
_table_captioned=False

def unit_latex(unit):
    if any(ord(c)>=0x2e80 for c in unit):return None
    special={'degC':r'{}^\circ\mathrm{C}','deg':r'{}^\circ','degree':r'{}^\circ','arcmin':r'{}^{\prime}','arcsec':r'{}^{\prime\prime}','%':r'\%','um':r'\mu\mathrm{m}','urad':r'\mu\mathrm{rad}','uF':r'\mu\mathrm{F}','ohm':r'\Omega'}
    if unit in special:return special[unit]
    unit=unit.replace('Ω',r'\Omega ').replace('µ',r'\mu ').replace('μ',r'\mu ').replace('°C',r'{}^\circ C').replace('*',r'\cdot ')
    unit=re.sub(r'\^(-?\d+)',r'^{\1}',unit)
    return r'\mathrm{'+unit.replace(' ',r'\,')+'}'

def number_tex(value,digits=10):
    text=f'{float(value):.{digits}g}'
    if 'e' in text.lower():
        mantissa,exponent=text.lower().split('e')
        return mantissa+r'\times10^{'+str(int(exponent))+'}'
    return text

def axis_label(text):
    """Keep Chinese in SimSun and route every Latin/unit run through Times mathtext."""
    superscripts=str.maketrans('⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺','0123456789-+')
    def roman(match):
        s=match[0]
        if not s.strip():return s
        s=re.sub('[⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺]+',lambda m:'^{'+m[0].translate(superscripts)+'}',s)
        s=s.replace('·',r'\cdot ').replace('°',r'{}^\circ').replace('%',r'\%').replace('_',r'\_')
        s=re.sub(r'\^(-?\d+)',r'^{\1}',s).replace(' ',r'\ ')
        return r'$\mathrm{'+s+'}$'
    return ''.join(p if p.startswith('$') else re.sub(r'[^\u2e80-\u9fff\uff00-\uffef]+',roman,p) for p in re.split(r'(\$[^$]*\$)',text))

def table_markdown(table):
    def cell(value):
        if isinstance(value,float):
            text=number_tex(value,8)
            return '$'+text+'$' if '\\times' in text else text
        text=str(value)
        if re.fullmatch(r'[-+]?\d+(?:\.\d+)?[eE][-+]?\d+',text):return '$'+number_tex(float(text),8)+'$'
        return ''.join(re.sub(r'(?<!\\)\|',r'\\vert ',p) if p.startswith('$') else p.replace('|',r'\|') for p in re.split(r'(\$[^$]*\$)',text))
    headers=table['headers']
    return '\n'.join(['| '+' | '.join(map(cell,headers))+' |','| '+' | '.join(['---']*len(headers))+' |',*['| '+' | '.join(map(cell,r))+' |' for r in table['rows']]])

def table_display(table):
    # Markdown MIME gives Jupyter's native math renderer access to table headers.
    from IPython.display import Markdown
    title='' if _table_captioned else "表　"+table.get("title","计算结果")+"\n\n"
    display(Markdown(title+table_markdown(table)))

def metrics_display(result):
    def unit(v):
        source=v.get('unit','1');tex=unit_latex(source)
        return '$'+tex+'$' if tex else source
    table_display({'headers':['指标','数值','单位'],'rows':[[v.get('label',k),float(v['value']),unit(v)] for k,v in result['metrics'].items()]})

def series_plot(result,key):
    series_figure(result['series'][key]);plt.show()

def display_plotly(fig):
    global _plotly_loaded
    fig.update_layout(paper_bgcolor='white',plot_bgcolor='white',font={'family':FONT,'size':16,'color':'#171717'},title=None)
    fig.update_xaxes(showline=True,linecolor='#222',ticks='inside',showgrid=False,zeroline=False)
    fig.update_yaxes(showline=True,linecolor='#222',ticks='inside',gridcolor='#e3e3e3',zeroline=False)
    display(HTML('<div class="lab-figure">'+fig.to_html(full_html=False,include_plotlyjs=not _plotly_loaded,auto_play=False,config={'responsive':True,'displayModeBar':False,'displaylogo':False})+'</div>'))
    _plotly_loaded=True

def series_figure(series):
    style();x=np.asarray(series['x'],dtype=float);y=np.asarray(series['y'],dtype=float)
    if x.shape!=y.shape or x.size==0 or not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)):
        raise ValueError('Invalid plotted series')
    if series.get('fit') and len(x)>2 and np.ptp(x)>0:
        fig,(ax,residual)=plt.subplots(2,1,figsize=(10.5,8.5),height_ratios=[2,1],layout='constrained')
        slope,intercept=np.polyfit(x,y,1);xx=np.linspace(x.min(),x.max(),200)
        ax.plot(xx,slope*xx+intercept,'-',color='#222',label='线性拟合')
        residual.plot(x,y-(slope*x+intercept),'o',mfc='white',mec='#222')
        residual.axhline(0,color='#888',linestyle='--',linewidth=1)
        unit=series.get('residual_unit')
        if unit is None:unit=series['y_label'].split(' / ',1)[1] if ' / ' in series['y_label'] else '无量纲' if 'log' in series['y_label'].lower() or 'ln' in series['y_label'].lower() else ''
        residual.set(xlabel=axis_label(series['x_label']),ylabel=axis_label('残差'+(' / '+unit if unit else '')))
    else:fig,ax=plt.subplots(figsize=(10.5,6.6),layout='constrained')
    ax.plot(x,y,'-' if series.get('model',False) else 'o-' if series.get('connect',False) else 'o',mfc='white',mec='#222',color='#222',label=series.get('label','模型曲线' if series.get('model') else '观测值'))
    ax.set(xlabel=axis_label(series['x_label']),ylabel=axis_label(series['y_label']));ax.legend()
    if series.get('equal_aspect'):ax.set_aspect('equal',adjustable='box')
    for axis in fig.axes:
        axis.xaxis.label.set_fontfamily('SimSun');axis.yaxis.label.set_fontfamily('SimSun')
    return fig

def inline_images(html,base):
    from bs4 import BeautifulSoup
    soup=BeautifulSoup(html,'html.parser')
    for img in soup.select('img[src]'):
        src=img['src']
        if src.startswith(('http:','https:','data:','attachment:')):continue
        path=(Path(base)/src).resolve()
        if path.is_file() and path.suffix.lower() in ('.svg','.png'):
            mime='image/svg+xml' if path.suffix.lower()=='.svg' else 'image/png'
            img['src']='data:'+mime+';base64,'+base64.b64encode(path.read_bytes()).decode()
    return str(soup)

def sections(text):
    return [re.sub(r'[*：:]','',m).strip() for m in re.findall(r'^## (.+)$',text,re.M)]
