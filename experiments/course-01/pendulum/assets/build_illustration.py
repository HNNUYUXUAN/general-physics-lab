"""Draw the README geometry and analysis overview with print typography."""
from pathlib import Path
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Arc
from matplotlib.font_manager import FontProperties, findfont

for family in ('SimSun','Times New Roman'):
    findfont(family,fallback_to_default=False)
plt.rcParams.update({'font.family':'Times New Roman','mathtext.fontset':'custom',
    'mathtext.rm':'Times New Roman','mathtext.it':'Times New Roman:italic',
    'mathtext.bf':'Times New Roman:bold','svg.fonttype':'path','savefig.facecolor':'white'})
zh=FontProperties(family='SimSun')
fig,ax=plt.subplots(figsize=(10.8,4.2));fig.subplots_adjust(0,0,1,1)
ax.set(xlim=(0,10.8),ylim=(0,4.2));ax.set_aspect('equal');ax.axis('off')
p=(1.65,3.63);angle=math.radians(20);v=(math.sin(angle),-math.cos(angle));length=2.5;radius=.23
c=tuple(p[i]+length*v[i] for i in (0,1));top=tuple(c[i]-radius*v[i] for i in (0,1))
ax.plot([.9,2.45],[3.73,3.73],color='#171717',lw=2)
ax.plot([p[0],p[0]],[.7,p[1]],color='#aaa',ls=(0,(4,4)),lw=1)
ax.plot([p[0],top[0]],[p[1],top[1]],color='#171717',lw=1.7)
ax.add_patch(Circle(c,radius,facecolor='#f2f2f2',edgecolor='#171717',lw=1.6))
ax.plot(*p,'o',color='#171717',ms=4);ax.plot(*c,'o',color='#171717',ms=3)
ax.add_patch(Arc(p,1.5,1.5,theta1=-90,theta2=-70,color='#777',lw=1))
ax.text(1.75,2.67,r'$\theta$',fontsize=18)
normal=(-math.cos(angle),-math.sin(angle));offset=.56
a=tuple(p[i]+offset*normal[i] for i in (0,1));b=tuple(c[i]+offset*normal[i] for i in (0,1))
ax.annotate('',b,a,arrowprops={'arrowstyle':'<->','color':'#444','lw':1.1})
for end,original in [(a,p),(b,c)]:ax.plot([end[0]-.08,original[0]],[end[1],original[1]],color='#bbb',lw=.8)
ax.text(.45,2.13,'有效摆长',fontproperties=zh,fontsize=16)
ax.text(.8,1.8,r"$L'$",fontsize=21)
ax.annotate('摆线长',xy=((p[0]+top[0])/2,(p[1]+top[1])/2),xytext=(2.6,2.7),
    fontproperties=zh,fontsize=16,arrowprops={'arrowstyle':'-','color':'#777','lw':.9})
ax.text(3.5,2.67,r'$L$',fontsize=19)
ax.annotate('',(c[0]+radius,c[1]),(c[0]-radius,c[1]),arrowprops={'arrowstyle':'<->','color':'#444','lw':1})
ax.text(c[0],c[1]-.58,r'$\bar d$',ha='center',fontsize=18)
ax.text(1.4,.3,'摆球球心到悬点的距离',fontproperties=zh,fontsize=14,color='#444')
ax.plot([4.15,4.15],[.35,3.75],color='#ddd',lw=1)
for num,y,label,formula in [('01',3.28,'测量有效摆长',r"$L'=L+\bar d/2$"),('02',2.13,'连续计时求周期',r'$T=\bar t/20$'),('03',.98,'拟合周期平方与摆长',r"$T^2=kL'+b$")]:
    ax.text(4.58,y,num,fontsize=25,color='#999',va='center')
    ax.text(5.33,y+.11,label,fontproperties=zh,fontsize=17,va='center')
    ax.text(5.33,y-.32,formula,fontsize=20,va='center')
ax.text(8.35,.65,r'$g=4\pi^2/k$',fontsize=22)
out=Path(__file__).parent
fig.savefig(out/'pendulum-overview.svg',metadata={'Date':None})
fig.savefig(out/'pendulum-overview.png',dpi=180)
plt.close(fig)
