"""Four thin-lens focal-length methods from observed lengths in centimetres."""
import csv
import math
from pathlib import Path
import numpy as np


def _read(exp, name):
    with (Path(exp)/"data"/name).open(encoding="utf-8-sig",newline="") as f:
        return np.array([[float(v) for v in row.values()] for row in csv.DictReader(f)])


def analyze(experiment_dir):
    auto,uv,bessel,concave=[_read(experiment_dir,n) for n in ["autocollimation.csv","conjugates.csv","bessel.csv","concave.csv"]]
    for rows in [auto,uv,bessel,concave]:
        if len(rows)<2 or np.any(rows[:,1:]<=0):raise ValueError("Each method requires positive lengths and at least two repeats")
    if np.any(concave[:,2]<=concave[:,1]) or np.any(bessel[:,2]>=bessel[:,1]):raise ValueError("Concave b>a and Bessel D>d are required")
    f1=auto[:,1]
    f2=uv[:,1]*uv[:,2]/(uv[:,1]+uv[:,2])
    f3=(bessel[:,1]**2-bessel[:,2]**2)/(4*bessel[:,1])
    f4=-concave[:,1]*concave[:,2]/(concave[:,2]-concave[:,1])
    fs=[f1,f2,f3,f4]
    means=[float(np.mean(f)) for f in fs]
    errors=[float(np.std(f,ddof=1)/math.sqrt(len(f))) for f in fs]
    names=["自准直法","物距像距法","二次成像法","辅助成像法（凹透镜）"]
    metric=lambda value,label:{"value":float(value),"unit":"cm","label":label}
    metrics={}
    for name,label,mean,error in zip(["autocollimation","conjugates","bessel","concave"],names,means,errors):
        metrics[name+"_mean_cm"]=metric(mean,label+"焦距均值")
        metrics[name+"_type_a_cm"]=metric(error,label+"均值A类分量")
    metrics["convex_method_average_cm"]=metric(np.mean(means[:3]),"三种凸透镜方法等权平均")
    table=lambda headers,rows:{"headers":headers,"rows":rows}
    derived=lambda raw,values:[[int(row[0]),*map(float,row[1:]),round(float(f),6)] for row,f in zip(raw,values)]
    return {"metrics":metrics,"tables":{
        "autocollimation":table(["次数","$f$ / cm"],[[int(row[0]),row[1]] for row in auto]),
        "conjugates":table(["次数","$u$ / cm","$v$ / cm"],[[int(row[0]),*row[1:]] for row in uv]),
        "bessel":table(["次数","$D$ / cm","$d$ / cm"],[[int(row[0]),*row[1:]] for row in bessel]),
        "concave":table(["次数","$a$ / cm","$b$ / cm"],[[int(row[0]),*row[1:]] for row in concave]),
        "conjugates_f":table(["次数","$u$ / cm","$v$ / cm","$f$ / cm"],derived(uv,f2)),
        "bessel_f":table(["次数","$D$ / cm","$d$ / cm","$f$ / cm"],derived(bessel,f3)),
        "concave_f":table(["次数","$a$ / cm","$b$ / cm","$f$ / cm"],derived(concave,f4)),
        "summary":table(["方法","焦距均值 / cm","均值A类分量 / cm"],[[name,round(mean,6),round(error,6)] for name,mean,error in zip(names,means,errors)]),
    },"series":{
        "conjugates-repeat":{"x":uv[:,0].tolist(),"y":f2.tolist(),"x_label":"测量次数","y_label":"焦距 $f$ / cm","label":"物距像距法"},
        "concave-repeat":{"x":concave[:,0].tolist(),"y":f4.tolist(),"x_label":"测量次数","y_label":"凹透镜焦距 $f$ / cm","label":"辅助成像法"},
    },"notes":["A类分量仅由各方法五次重复值估计，缺少仪器、位置判定和模型误差，不能合成为完整不确定度。","三种凸透镜方法等权平均为描述统计，未进行精度加权；共享样品和标尺，不作为独立重复测量估计不确定度。","无透镜标称值或校准值，不据方法间接近判断准确度。"]}


def _style(fig,xlabel,ylabel,height=520):
    fig.update_layout(template="plotly_white",font=dict(family="Times New Roman, SimSun",size=18),height=height,margin=dict(l=80,r=30,t=35,b=110),xaxis_title=xlabel,yaxis_title=ylabel)
    fig.update_xaxes(showline=True,linecolor="black",zerolinecolor="#bbbbbb",gridcolor="#eeeeee")
    fig.update_yaxes(showline=True,linecolor="black",zerolinecolor="#bbbbbb",gridcolor="#eeeeee")
    return fig


def explore(key,result):
    import plotly.graph_objects as go
    focal=result["metrics"]["conjugates_mean_cm"]["value"]
    fig=go.Figure()
    if key=="ray-geometry":
        ratios=np.round(np.linspace(1.2,4,15),2)
        ratios=np.unique(np.append(ratios,2.0))
        steps=[]
        for index,ratio in enumerate(ratios):
            u=ratio*focal;v=focal*u/(u-focal);mag=-v/u
            # Three exact paraxial rays and object/image arrows; transverse scale is arbitrary.
            traces=[([-u,0,v],[1,1,mag]),([-u,0,v],[1,0,mag]),([-u,0,v],[1,mag,mag]),([-u,-u],[0,1]),([v,v],[0,mag]),([0,0],[-3.5,3.5])]
            for j,(x,y) in enumerate(traces):
                fig.add_trace(go.Scatter(x=x,y=y,mode="lines",visible=ratio==2,name=["平行入射光线","过光心光线","过物方焦点光线","物","像","透镜"][j],line=dict(color="black",width=1.5 if j<3 else 2,dash=["solid","dash","dot","solid","solid","dash"][j]),showlegend=j<3))
            mask=[False]*(len(ratios)*6);mask[index*6:index*6+6]=[True]*6
            steps.append(dict(method="update",label=f"{ratio:g}",args=[{"visible":mask},{"annotations":[dict(text=f"u = {u:.2f} cm；v = {v:.2f} cm；放大率 = {mag:.3f}",x=.02,y=.99,xref="paper",yref="paper",showarrow=False,xanchor="left")]}]))
        active=list(ratios).index(2.0)
        fig.update_layout(sliders=[dict(active=active,steps=steps,currentvalue=dict(prefix="物距 u/f = "))],annotations=steps[active]["args"][1]["annotations"],xaxis_range=[-4.2*focal,6.3*focal],yaxis_range=[-5.5,2],legend=dict(orientation="h",y=1.12))
        return _style(fig,"沿光轴位置 x / cm","横向高度 / 任意单位",560)
    if key=="bessel-branches":
        ratio=np.linspace(4,8,201)
        d=ratio*focal
        separation=np.sqrt(d*d-4*d*focal)
        left=(d-separation)/2;right=(d+separation)/2
        fig.add_trace(go.Scatter(x=ratio,y=left,mode="lines",name="第一透镜位置",line=dict(color="black",width=1.5)))
        fig.add_trace(go.Scatter(x=ratio,y=right,mode="lines",name="第二透镜位置",line=dict(color="black",width=1.5,dash="dash")))
        fig.add_trace(go.Scatter(x=[5,5],y=[(5-math.sqrt(5))*focal/2,(5+math.sqrt(5))*focal/2],mode="markers",name="选定物屏距离",marker=dict(color="black",symbol="circle-open",size=11)))
        steps=[]
        for q in np.round(np.arange(4,8.01,.2),1):
            D=q*focal;gap=math.sqrt(max(0,D*D-4*D*focal));positions=[(D-gap)/2,(D+gap)/2]
            steps.append(dict(method="restyle",label=f"{q:g}",args=[{"x":[[q,q]],"y":[positions]},[2]]))
        fig.update_layout(sliders=[dict(active=5,steps=steps,currentvalue=dict(prefix="物屏距离 D/f = "))])
        return _style(fig,"物屏距离 D / f","距物的透镜位置 / cm")
    raise KeyError(key)
