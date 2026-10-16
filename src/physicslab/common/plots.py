from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager

def style():
    for name in ('Times New Roman','SimSun'):
        font_manager.findfont(name,fallback_to_default=False)
    plt.rcParams.update({'font.family':['Times New Roman','SimSun'],'font.size':16,
      'mathtext.fontset':'custom','mathtext.rm':'Times New Roman','mathtext.it':'Times New Roman:italic',
      'mathtext.bf':'Times New Roman:bold','axes.unicode_minus':True,'axes.spines.top':False,
      'axes.spines.right':False,'axes.spines.left':True,'axes.spines.bottom':True,
      'axes.edgecolor':'black','axes.labelcolor':'black','axes.linewidth':1.1,
      'axes.labelpad':12,'axes.titlelocation':'left','axes.titlesize':22,'axes.titleweight':'normal','axes.titlepad':20,
      'xtick.direction':'in','ytick.direction':'in','xtick.color':'black','ytick.color':'black',
      'figure.facecolor':'white','savefig.facecolor':'white','lines.linewidth':1.8,
      'lines.markersize':6,'legend.frameon':False,'legend.fontsize':13,'axes.grid':True,
      'figure.constrained_layout.w_pad':.25,'figure.constrained_layout.h_pad':.20,
      'figure.constrained_layout.hspace':.08,'axes.grid.axis':'y','grid.color':'#e3e3e3','grid.linewidth':.8,'svg.fonttype':'path'})

def fit_figure(result):
    style();p=result['processed'];m=result['metrics'];x=np.array([r['effective_length_m'] for r in p]);y=np.array([r['period_squared_s2'] for r in p]);u=np.array([r['period_squared_u_a_s2'] for r in p])
    fig,(ax,ar)=plt.subplots(2,1,figsize=(10.5,10),gridspec_kw={'height_ratios':[1.5,1]},layout='constrained')
    ax.errorbar(x,y,yerr=u,fmt='o',mfc='white',mec='#222',color='#222',capsize=3,label='观测值及 A 类标准不确定度',zorder=4)
    xx=np.linspace(x.min()-.02,x.max()+.02,100)
    ax.plot(xx,m['slope']['value']*xx+m['intercept']['value'],color='#222',label='含截距线性拟合')
    ax.set(xlabel=r"有效摆长 $L'\,/\,\mathrm{m}$",ylabel=r'$T^2\,/\,\mathrm{s}^2$')
    ax.legend(loc='upper left')
    ax.text(.42,.12,rf'$g={m["gravity_fit"]["value"]:.6f}\ \mathrm{{m/s^2}}$',transform=ax.transAxes,fontsize=18)
    ar.errorbar(x,np.array(result['residuals_s2'])*1000,yerr=u*1000,fmt='o',mfc='white',mec='#222',color='#222',capsize=4)
    ar.axhline(0,color='#888',lw=1,ls='--')
    ar.set(xlabel=r"有效摆长 $L'\,/\,\mathrm{m}$",ylabel=r'残差 $/\,(10^{-3}\,\mathrm{s}^2)$')
    for axis in (ax,ar):axis.set_xlim(.48,1.05)
    for axis in fig.axes:
        axis.xaxis.label.set_fontfamily("SimSun");axis.yaxis.label.set_fontfamily("SimSun")
    return fig

def trajectory_figure(result):
    style();s=result['simulation'];t=np.array(s['time_s'])
    fig,axes=plt.subplots(2,1,figsize=(10.5,8.5),layout='constrained')
    axes[0].plot(t,np.rad2deg(s['angle_rad']),color='#171717',label='非线性数值解')
    axes[0].plot(t,np.rad2deg(s['linear_angle_rad']),color='#666',ls='--',label='小角度解析解')
    axes[0].set(xlabel=r'时间 $t\,/\,\mathrm{s}$',ylabel=r'摆角 $\theta\,/\,{}^\circ$');axes[0].legend(loc='upper right')
    axes[1].plot(t,s['angular_velocity_rad_s'],color='#171717')
    axes[1].set(xlabel=r'时间 $t\,/\,\mathrm{s}$',ylabel=r'角速度 $\omega\,/\,(\mathrm{rad/s})$')
    for axis in fig.axes:
        axis.xaxis.label.set_fontfamily("SimSun");axis.yaxis.label.set_fontfamily("SimSun")
    return fig

def scan_figure(result):
    style();scan=result['amplitude_scan'];a=np.array([r['angle_deg'] for r in scan]);fig,axes=plt.subplots(2,1,figsize=(10.5,9),layout='constrained')
    for ax,key,title,ylabel in [(axes[0],'period_excess_pct','图 5  初始摆角与周期增量',r'周期增量 $/\,\%$'),(axes[1],'gravity_bias_pct','图 6  小角度近似对重力估计的影响',r'重力估计偏差 $/\,\%$')]:
        yy=np.array([r[key] for r in scan]);ax.plot(a,yy,'o-',color='#222',mfc='white',mec='#222')
        ax.axvspan(0,5,color='#eeeeee');ax.axvline(5,color='#999',ls='--',lw=1)
        ax.set(xlabel=r'初始摆角 $\theta_0\,/\,{}^\circ$',ylabel=ylabel,xlim=(0,62))
        ax.text(.10,.85,'灰带：小摆角实验条件',transform=ax.transAxes,fontsize=14)
    for axis in fig.axes:
        axis.xaxis.label.set_fontfamily("SimSun");axis.yaxis.label.set_fontfamily("SimSun")
    return fig

def apparatus_figure():
    from matplotlib.patches import Circle,Arc,Rectangle
    style();fig,ax=plt.subplots(figsize=(9,5));ax.set_aspect('equal');ax.axis('off')
    ax.set(xlim=(-.8,1.6),ylim=(-1.35,.4));a=np.deg2rad(24);end=np.array([np.sin(a),-np.cos(a)])
    ax.add_patch(Rectangle((-.23,.02),.46,.045,fc='#bbb',ec='#222',lw=1))
    for x in np.linspace(-.23,.18,9):ax.plot([x,x+.05],[.065,.13],color='#888',lw=.8)
    ax.plot([0,0],[0,-1.12],ls='--',color='#999',lw=1)
    ax.plot([0,end[0]],[0,end[1]],color='#222',lw=1.8)
    ax.add_patch(Circle(end,.075,fc='white',ec='#222',lw=1.6));ax.plot(0,0,'o',color='black',ms=4)
    ax.add_patch(Arc((0,0),.6,.6,theta1=-90,theta2=-66,color='#444',lw=1));ax.text(.06,-.42,r'$\theta$',fontsize=19)
    offset=np.array([-.24,-.11]);ax.annotate('',end+offset,offset,arrowprops={'arrowstyle':'|-|','color':'#555','lw':1})
    ax.text(-.18,-.61,r"$L' = L+d/2$",rotation=-66,ha='center',fontsize=15)
    ax.text(0,.2,r'悬点 $O$',ha='center',fontfamily='SimSun');ax.text(0,-1.24,'平衡位置',ha='center',fontsize=14)
    ax.annotate('',end+[0,-.29],end+[0,-.075],arrowprops={'arrowstyle':'->','color':'black','lw':1.2});ax.text(end[0]+.05,end[1]-.23,r'$mg$')
    ax.text(.85,-.25,r'$T=2\pi\sqrt{L^\prime/g}$',fontsize=25)
    ax.text(.8,-.55,'小角度近似\n质点摆球、无质量摆线',fontsize=15,linespacing=1.8)
    fig.tight_layout();return fig

def export_figures(result,directory):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    for name,make in [('fit',fit_figure),('trajectory',trajectory_figure),('amplitude-scan',scan_figure)]:
        fig=make(result)
        for ext in ('svg','png'):fig.savefig(directory/f'{name}.{ext}',dpi=220)
        plt.close(fig)
