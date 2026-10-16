"""Native notebook visualizations with embedded, offline Plotly controls."""
from copy import deepcopy
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from IPython.display import HTML, display
from .pendulum import fit_line, simulate, period_exact

from physicslab.common.theme import INK,TEAL,COPPER,MUTED,GRID
BLUE=TEAL;GOLD=COPPER
PALETTE=["#666666","#666666","#666666","#666666","#666666","#666666"]
def style(fig,title,height=500):
    fig.update_layout(template="plotly_white",title=dict(text=title,x=.035,xanchor="left",y=.965,yanchor="top",font=dict(size=22)),
      height=height,paper_bgcolor="white",plot_bgcolor="white",
      font=dict(family="Times New Roman, SimSun, serif",size=16,color=INK),
      margin=dict(l=78,r=34,t=136,b=92),colorway=PALETTE,
      legend=dict(orientation="h",y=-.18,x=0,font=dict(size=14,color=MUTED),tracegroupgap=12),
      hovermode="closest",hoverlabel=dict(bgcolor="white",bordercolor="#eeeeee",font_size=12))
    fig.update_xaxes(showgrid=False,showline=True,linecolor="#222222",linewidth=1,gridcolor=GRID,zeroline=False,
      ticks="inside",tickcolor="#222222",ticklen=4,tickfont=dict(size=14,color=MUTED),title_font=dict(size=16,color=MUTED),title_standoff=14)
    fig.update_yaxes(ticks="inside",ticklen=5,showline=True,gridcolor=GRID,zeroline=False,tickfont=dict(size=14,color=MUTED),
      title_font=dict(size=16,color=MUTED),title_standoff=14)
    for menu in fig.layout.updatemenus:
        menu.update(bgcolor="#eeeeee",bordercolor="#eeeeee",borderwidth=1,font=dict(size=16,color=INK),
          pad=dict(l=0,r=0,t=0,b=0))
        if menu.type!="buttons":menu.update(y=1.22,yanchor="top",x=1,xanchor="right")
    for slider in fig.layout.sliders:
        slider.update(bgcolor=TEAL,activebgcolor=TEAL,bordercolor=TEAL,tickcolor="#222222",
          ticklen=3,font=dict(size=10,color=MUTED),currentvalue=dict(font=dict(size=16,color=INK)))
    for ann in fig.layout.annotations:
        ann.update(font=dict(size=13,color=INK))
    for tr in fig.data:
        if tr.type=="scatter" and tr.mode and "markers" in tr.mode and tr.name not in ("当前状态","摆线与摆球"):
            tr.marker.update(color="white",line=dict(color="#222",width=1.6))
            tr.error_y.update(color="#222",thickness=1,width=3)
    return fig

def show(fig,first=False):
    # Captions belong to manuscript cells below each figure. Keep only live parameter readouts here.
    def readout(text):return text.split('<br>',1)[1] if text and '<br>' in text else ''
    fig.layout.title.text=readout(fig.layout.title.text)
    for menu in fig.layout.updatemenus:
        for button in menu.buttons:
            if button.args and len(button.args)>1 and isinstance(button.args[1],dict) and 'title.text' in button.args[1]:
                button.args[1]['title.text']=readout(button.args[1]['title.text'])
    fig.layout.annotations=tuple(a for a in fig.layout.annotations if not (a.xref=='paper' and a.yref=='paper' and a.showarrow is False and a.text in ('摆角随时间变化','相图','角速度随时间变化','动能与势能（单位质量）','单摆装置','相空间 · 当前运动状态','周期延长','小角度公式反推 g 的偏差')))
    body=fig.to_html(full_html=False,auto_play=False,include_plotlyjs=True if first else False,
        config={"responsive":True,"displaylogo":False,"displayModeBar":False,"scrollZoom":False,
                "modeBarButtonsToRemove":["select2d","lasso2d","sendDataToCloud"]})
    display(HTML('<div class="lab-figure">'+body+'</div>'))

def summary(result):
    m=result["metrics"]
    cards=[("拟合重力加速度",f'{m["gravity_fit"]["value"]:.6f}',"m/s²"),
           ("回归标准误",f'{m["gravity_regression_standard_error"]["value"]:.6f}',"m/s²"),
           ("观测设计","6 × 3","组长度 × 重复计时"),
           ("拟合决定系数",f'{m["r_squared"]["value"]:.8f}',"含截距 OLS")]
    css='<style>.lab-summary{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:18px;margin:24px 0;padding:24px 0;border-top:1px solid #eeeeee;border-bottom:1px solid #eeeeee}.lab-metric-label,.lab-metric-unit{font-size:14px;color:#666666}.lab-metric-value{font-size:26px;color:#666666;padding:8px 0;font-variant-numeric:tabular-nums}.lab-figure{margin:10px 0 24px}</style>'
    return HTML(css+'<div class="lab-summary">'+''.join(
      f'<div class="lab-metric"><div class="lab-metric-label">{label}</div>'
      f'<div class="lab-metric-value">{value}</div><div class="lab-metric-unit">{unit}</div></div>'
      for label,value,unit in cards)+'</div>')

def measurements(timing):
    fig=go.Figure()
    for run in range(1,7):
        rows=[r for r in timing if int(r["run_id"])==run]
        t=np.array([float(r["elapsed_time_s"]) for r in rows])
        fig.add_trace(go.Scatter(x=[1,2,3],y=(t-t.mean())*1000,mode="lines+markers",name=f"第 {run} 组",
          customdata=np.column_stack([t,np.full(3,float(rows[0]["string_length_cm"]))]),
          hovertemplate="第 %{x} 次<br>计时 %{customdata[0]:.2f} s<br>摆线长 %{customdata[1]:.2f} cm<br>偏离均值 %{y:.2f} ms<extra>%{fullData.name}</extra>",
          marker=dict(size=8,symbol=["circle","square","diamond","triangle-up","triangle-down","cross"][run-1],line=dict(width=1.5,color="#222")),line=dict(width=1.8,dash=["solid","dash","dot","dashdot","longdash","longdashdot"][run-1])))
    fig.add_hline(y=0,line_dash="dot",line_color="#666666")
    buttons=[dict(label="全部六组",method="update",args=[{"visible":[True]*6}])]
    buttons += [dict(label=f"第 {i+1} 组",method="update",args=[{"visible":[j==i for j in range(6)]}]) for i in range(6)]
    fig.update_layout(updatemenus=[dict(buttons=buttons,x=1,y=1.2,xanchor="right")])
    fig.update_xaxes(title="重复测量序号",tickvals=[1,2,3])
    fig.update_yaxes(title="计时减去本组均值 / ms")
    return style(fig,"重复计时的离散程度")

def fit_scenarios(result):
    p=result["processed"]; x=np.array([r["effective_length_m"] for r in p]);y=np.array([r["period_squared_s2"] for r in p])
    scenarios=[]
    for omit in range(7):
        keep=np.arange(6)!=omit-1 if omit else np.ones(6,dtype=bool)
        f=fit_line(x[keep],y[keep]);g=4*np.pi**2/f["slope"]
        scenarios.append(dict(omit=omit,x=x[keep],y=y[keep],line=f["slope"]*x+f["intercept"],
          residual=(y[keep]-(f["slope"]*x[keep]+f["intercept"]))*1000,
          uncertainty=np.array([r["period_squared_u_a_s2"] for r in p])[keep]*1000,
          g=g,slope=f["slope"],intercept=f["intercept"]))
    return x,scenarios

def fit_explorer(result):
    x,scenarios=fit_scenarios(result)
    fig=make_subplots(rows=2,cols=1,shared_xaxes=True,row_heights=[.68,.32],vertical_spacing=.14)
    buttons=[]
    for i,s in enumerate(scenarios):
        visible=i==0
        fig.add_trace(go.Scatter(x=s["x"],y=s["y"],mode="markers",name="观测值",
          marker=dict(size=9,color=BLUE,line=dict(width=1.5,color="white")),error_y=dict(array=s["uncertainty"]/1000),visible=visible),row=1,col=1)
        fig.add_trace(go.Scatter(x=x,y=s["line"],mode="lines",name="含截距拟合",line=dict(color=GOLD),visible=visible),row=1,col=1)
        fig.add_trace(go.Scatter(x=s["x"],y=s["residual"],mode="markers",name="残差 ± u<sub>A</sub>(T<sup>2</sup>)",
          marker=dict(size=8,color=BLUE,line=dict(width=1,color="white")),error_y=dict(array=s["uncertainty"]),visible=visible),row=2,col=1)
        label="全部数据" if i==0 else f"暂不纳入第 {i} 组"
        title=f'周期平方与有效摆长<br><span style="font-size:14px;color:#666666">{label}　g = {s["g"]:.6f} m/s²　k = {s["slope"]:.6f} s²/m</span>'
        buttons.append(dict(label=label,method="update",args=[{"visible":[j//3==i for j in range(21)]},{"title.text":title}]))
    fig.add_hline(y=0,line_dash="dot",row=2,col=1)
    fig.update_xaxes(title="有效摆长 L′ / m",row=2,col=1)
    fig.update_yaxes(title="周期平方 T<sup>2</sup> / s<sup>2</sup>",row=1,col=1)
    fig.update_yaxes(title="残差 / (0.001 s²)",row=2,col=1)
    fig.update_layout(updatemenus=[dict(buttons=buttons,x=1,y=1.19,xanchor="right")])
    return style(fig,buttons[0]["args"][1]["title.text"],650)

def model_scenarios(config,gravity):
    values=[]
    # Initial preset matches the canonical model, followed by deliberate scenarios.
    pairs=[(config["simulation"]["initial_angle_deg"],config["simulation"]["length_m"])]
    pairs += [(a,l) for a in (5,20,45,60) for l in (.5,1.,1.5) if (a,l) not in pairs]
    for a,l in pairs:
        c=deepcopy(config);c["simulation"].update(initial_angle_deg=a,length_m=l)
        s=simulate(c,gravity);values.append((a,l,s))
    return values

def model_explorer(config,gravity):
    fig=make_subplots(rows=2,cols=2,subplot_titles=["摆角随时间变化","相图","角速度随时间变化","动能与势能（单位质量）"],
      vertical_spacing=.23,horizontal_spacing=.20)
    scenes=model_scenarios(config,gravity);buttons=[]
    for index,(a,l,s) in enumerate(scenes):
        t=s["time_s"];angle=np.rad2deg(s["angle_rad"]);omega=np.array(s["angular_velocity_rad_s"])
        kinetic=.5*l*l*omega**2;potential=gravity*l*(1-np.cos(s["angle_rad"]))
        specs=[(t,angle,"非线性",1,1,BLUE,None),(t,np.rad2deg(s["linear_angle_rad"]),"小角度",1,1,GOLD,"dash"),
          (angle,omega,"相轨迹",1,2,BLUE,None),(t,omega,"角速度",2,1,BLUE,None),
          (t,kinetic,"动能",2,2,BLUE,None),(t,potential,"势能",2,2,GOLD,"dash")]
        for xx,yy,name,row,col,color,dash in specs:
            fig.add_trace(go.Scatter(x=xx,y=yy,mode="lines",name=name,visible=index==0,
              line=dict(color=color,dash=dash,width=2.2),showlegend=name not in ("相轨迹","角速度")),row=row,col=col)
        title=f'非线性单摆 · 四个观察视角<br><span style="font-size:14px;color:#666666">初始摆角 {a:g}°　摆长 {l:g} m　非线性周期 {s["period_exact_s"]:.5f} s</span>'
        buttons.append(dict(label=f"{a:g}° / {l:g} m",method="update",
          args=[{"visible":[j//6==index for j in range(6*len(scenes))]},{"title.text":title}]))
    for row,col in [(1,1),(2,1),(2,2)]:fig.update_xaxes(title="时间 / s",row=row,col=col)
    fig.update_xaxes(title="摆角 / °",row=1,col=2)
    for row,col,title in [(1,1,"摆角 / °"),(1,2,"角速度 / (rad/s)"),(2,1,"角速度 / (rad/s)"),(2,2,"能量 / (J/kg)")]:
        fig.update_yaxes(title=title,row=row,col=col)
    fig.update_layout(updatemenus=[dict(buttons=buttons,x=1,y=1.2,xanchor="right")])
    return style(fig,buttons[0]["args"][1]["title.text"],820)

def animation(result):
    s=result["simulation"];l=result["model_parameters"]["length_m"]
    t=np.array(s["time_s"]);a=np.array(s["angle_rad"]);v=np.array(s["angular_velocity_rad_s"])
    fig=make_subplots(rows=1,cols=2,subplot_titles=["单摆装置","相空间 · 当前运动状态"],horizontal_spacing=.17,column_widths=[.47,.53])
    fig.add_trace(go.Scatter(x=[0,l*np.sin(a[0])],y=[0,-l*np.cos(a[0])],mode="lines+markers",
      marker=dict(size=[9,28],color=[INK,TEAL],line=dict(width=2,color="white")),
      line=dict(width=2.5,color=INK),name="摆线与摆球",hoverinfo="skip"),1,1)
    fig.add_trace(go.Scatter(x=np.rad2deg(a),y=v,mode="lines",line=dict(color="#666666",width=2),name="完整相轨迹",hoverinfo="skip"),1,2)
    fig.add_trace(go.Scatter(x=[np.rad2deg(a[0])],y=[v[0]],mode="markers",
      marker=dict(size=13,color=COPPER,line=dict(width=2,color="white")),name="当前状态",
      hovertemplate="摆角 %{x:.2f}°<br>角速度 %{y:.3f} rad/s<extra></extra>"),1,2)
    # A fixed support, the equilibrium line and a physical length reference.
    fig.add_shape(type="rect",x0=-.23*l,x1=.23*l,y0=.015*l,y1=.07*l,
      line=dict(width=0),fillcolor="#666666",row=1,col=1)
    for xx in np.linspace(-.23,.19,8):
        fig.add_shape(type="line",x0=xx*l,x1=(xx+.04)*l,y0=.07*l,y1=.12*l,line=dict(color="#666666",width=1),row=1,col=1)
    fig.add_shape(type="line",x0=0,x1=0,y0=0,y1=-1.08*l,line=dict(color="#666666",width=1.2,dash="dot"),row=1,col=1)
    fig.add_shape(type="line",x0=-.57*l,x1=-.57*l,y0=0,y1=-l,line=dict(color="#666666",width=1),row=1,col=1)
    for yy in (0,-l):
        fig.add_shape(type="line",x0=-.62*l,x1=-.52*l,y0=yy,y1=yy,line=dict(color="#666666",width=1),row=1,col=1)
    arc=np.linspace(-max(abs(a)),max(abs(a)),80)
    fig.add_trace(go.Scatter(x=l*np.sin(arc),y=-l*np.cos(arc),mode="lines",line=dict(color="#eeeeee",width=1,dash="dot"),hoverinfo="skip",showlegend=False),1,1)
    fig.add_annotation(x=-.65*l,y=-.5*l,text=f"ℓ = {l:g} m",showarrow=False,textangle=-90,font=dict(color=MUTED,size=12),row=1,col=1)
    fig.add_annotation(x=0,y=.19*l,text="悬点 O",showarrow=False,font=dict(color=MUTED,size=12),row=1,col=1)
    fig.add_annotation(x=0,y=-1.15*l,text="平衡位置",showarrow=False,font=dict(color=MUTED,size=11),row=1,col=1)
    fig.frames=[go.Frame(name=f"{t[i]:.2f}",traces=[0,2],data=[
        go.Scatter(x=[0,l*np.sin(a[i])],y=[0,-l*np.cos(a[i])]),
        go.Scatter(x=[np.rad2deg(a[i])],y=[v[i]])]) for i in range(0,len(t),5)]
    fig.update_xaxes(range=[-.82*l,.82*l],row=1,col=1)
    fig.update_yaxes(range=[-1.25*l,.28*l],scaleanchor="x",scaleratio=1,row=1,col=1)
    fig.update_xaxes(title="摆角 θ / °",range=[-1.18*max(np.rad2deg(a)),1.18*max(np.rad2deg(a))],row=1,col=2)
    fig.update_yaxes(title="角速度 ω / (rad/s)",range=[-1.18*max(abs(v)),1.18*max(abs(v))],row=1,col=2)
    opts={"frame":{"duration":70,"redraw":False},"transition":{"duration":0},"fromcurrent":True}
    fig.update_layout(updatemenus=[dict(type="buttons",direction="right",x=0,y=-.24,xanchor="left",yanchor="top",buttons=[
      dict(label="▶  播放",method="animate",args=[None,opts]),
      dict(label="Ⅱ  暂停",method="animate",args=[[None],{"mode":"immediate","frame":{"duration":0,"redraw":False}}])])],
      sliders=[dict(active=0,x=.27,len=.73,y=-.24,pad=dict(t=0),currentvalue=dict(prefix="时间  ",suffix=" s"),
       steps=[dict(label=f.name,method="animate",args=[[f.name],{"mode":"immediate","frame":{"duration":0,"redraw":False},"transition":{"duration":0}}]) for f in fig.frames])])
    style(fig,f'单摆运动与相图<br><span style="font-size:14px;color:#666666">初始摆角 {result["model_parameters"]["initial_angle_deg"]:g}°　摆长 {l:g} m　无阻尼模型</span>',620)
    fig.update_layout(margin=dict(l=60,r=35,t=128,b=135),showlegend=False)
    fig.update_xaxes(visible=False,row=1,col=1);fig.update_yaxes(visible=False,row=1,col=1)
    return fig

def amplitude_explorer(config,gravity):
    angles=np.arange(1,61);l=config["simulation"]["length_m"];t0=2*np.pi*np.sqrt(l/gravity)
    periods=np.array([period_exact(np.deg2rad(a),l,gravity) for a in angles])
    excess=100*(periods/t0-1);bias=100*((t0/periods)**2-1)
    fig=make_subplots(rows=1,cols=2,subplot_titles=["周期延长","小角度公式反推 g 的偏差"],horizontal_spacing=.17)
    for col,y,name,color in [(1,excess,"周期增量",BLUE),(2,bias,"重力偏差",GOLD)]:
        fig.add_trace(go.Scatter(x=angles,y=y,name=name,line=dict(color=color)),1,col)
        fig.add_trace(go.Scatter(x=[20],y=[y[19]],mode="markers",marker=dict(size=13,color=color),showlegend=False),1,col)
        fig.update_xaxes(title="初始摆角 / °",row=1,col=col);fig.update_yaxes(title=name+" / %",row=1,col=col)
    for col in (1,2):
        fig.add_vrect(x0=0,x1=5,fillcolor="#eee",opacity=.6,line_width=0,row=1,col=col)
        fig.add_vline(x=5,line_dash="dash",line_color="#999",row=1,col=col)
    fig.update_layout(sliders=[dict(active=19,currentvalue=dict(prefix="初始摆角 / °："),steps=[
      dict(label=str(a),method="restyle",args=[{"x":[[int(a)],[int(a)]],"y":[[float(excess[a-1])],[float(bias[a-1])]]},[1,3]]) for a in angles])])
    style(fig,"摆角与模型偏差",570)
    fig.update_layout(showlegend=False,margin=dict(l=78,r=34,t=120,b=130))
    fig.layout.sliders[0].update(y=-.23,pad=dict(t=12),tickwidth=0)
    return fig

