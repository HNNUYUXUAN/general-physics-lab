"""Newton rings and air-wedge analysis; all observed inputs are in CSV."""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path
import numpy as np


def _rows(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        return [{k: float(v) for k, v in row.items()} for row in csv.DictReader(stream)]


def analyze(experiment_dir):
    directory = Path(experiment_dir)
    config = json.loads((directory / "experiment.json").read_text(encoding="utf-8"))
    wavelength = config["parameters"]["wavelength_nm"] * 1e-6
    separation = config["parameters"]["order_separation"]
    rings = _rows(directory / "data" / "rings.csv")
    wedge = _rows(directory / "data" / "wedge.csv")
    orders = np.array([r["order"] for r in rings])
    diameters = np.array([r["right_mm"] - r["left_mm"] for r in rings])
    if len(set(orders)) != len(orders) or len(rings) < 3:
        raise ValueError("Ring orders must be unique and contain at least three observations")
    if np.any(diameters <= 0) or any(r["fringe_intervals"] <= 0 or r["fringe_length_mm"] <= 0 or r["wedge_length_mm"] <= 0 for r in wedge):
        raise ValueError("All measured lengths and counted intervals must be positive")
    squared = diameters**2
    slope = float(np.dot(orders - orders.mean(), squared - squared.mean()) / np.dot(orders - orders.mean(), orders - orders.mean()))
    intercept = float(squared.mean() - slope * orders.mean())
    residuals = squared - slope * orders - intercept
    slope_uncertainty = float(math.sqrt(float(np.dot(residuals, residuals)) / (len(orders) - 2) / float(np.dot(orders-orders.mean(), orders-orders.mean()))))
    lookup = {int(m): (float(d), float(d2)) for m, d, d2 in zip(orders, diameters, squared)}
    pairs = []
    for m in sorted(lookup):
        if m + separation in lookup:
            d, d2 = lookup[m]
            other, other2 = lookup[m + separation]
            pairs.append([m, m + separation, d, other, (other2-d2)/(4*separation*wavelength)])
    if not pairs:
        raise ValueError("No ring pair exists for the specified order separation")
    radii = np.array([p[-1] for p in pairs])
    thicknesses = np.array([r["fringe_intervals"]*wavelength*r["wedge_length_mm"]/(2*r["fringe_length_mm"]) for r in wedge])
    mean_h = float(thicknesses.mean())
    mean_h_a = float(thicknesses.std(ddof=1)/math.sqrt(len(thicknesses)))
    metric = lambda value, unit, **extra: {"value": float(value), "unit": unit, **extra}
    return {
        "metrics": {
            "wavelength_nm": metric(wavelength*1e6, "nm"),
            "radius_pair_mean_mm": metric(radii.mean(), "mm"),
            "radius_pair_sd_mm": metric(radii.std(ddof=1), "mm"),
            "radius_fit_mm": metric(slope/(4*wavelength), "mm"),
            "radius_fit_standard_error_mm": metric(slope_uncertainty/(4*wavelength), "mm"),
            "diameter_squared_slope_mm2": metric(slope, "mm^2"),
            "diameter_squared_intercept_mm2": metric(intercept, "mm^2"),
            "fit_r_squared": metric(1-float(np.dot(residuals,residuals))/float(np.dot(squared-squared.mean(), squared-squared.mean())), "1"),
            "wire_diameter_um": metric(mean_h*1000, "um"),
            "wire_diameter_type_a_um": metric(mean_h_a*1000, "um"),
            "wedge_angle_urad": metric(float(np.mean([r["fringe_intervals"]*wavelength/(2*r["fringe_length_mm"]) for r in wedge]))*1e6, "urad"),
        },
        "tables": {
            "rings": {"headers": ["暗环级数 $m$", "左读数 / mm", "右读数 / mm", "$D_m$ / mm"], "rows": [[int(r["order"]),r["left_mm"],r["right_mm"],round(float(d),3)] for r,d in zip(rings,diameters)]},
            "wedge": {"headers": ["次数", "条纹间隔数 $N$", "$l_N$ / mm", "$L$ / mm"], "rows": [[int(r["trial"]),int(r["fringe_intervals"]),r["fringe_length_mm"],r["wedge_length_mm"]] for r in wedge]},
            "pairs": {"headers": ["$m$", "$m+p$", "$D_m$ / mm", "$D_{m+p}$ / mm", "$R$ / mm"], "rows": [[*p[:2],round(p[2],3),round(p[3],3),round(p[4],3)] for p in pairs]},
            "thickness": {"headers": ["次数", "$l_N$ / mm", "$h$ / mm"], "rows": [[int(r["trial"]),r["fringe_length_mm"],round(float(h),8)] for r,h in zip(wedge,thicknesses)]},
            "fit": {"headers": ["$m$", "$D_m^2$ / mm$^2$", "拟合值 / mm$^2$", "残差 / mm$^2$"], "rows": [[int(m),round(float(d2),6),round(float(slope*m+intercept),6),round(float(e),6)] for m,d2,e in zip(orders,squared,residuals)]},
        },
        "series": {
            "ring-fit": {"x":orders.tolist(),"y":squared.tolist(),"x_label":"暗环级数 $m$","y_label":"直径平方 $D_m^2$ / mm$^2$","label":"观测值","fit":True},
            "wire-repeat": {"x":[int(r["trial"]) for r in wedge],"y":(thicknesses*1000).tolist(),"x_label":"测量次数","y_label":"细丝直径 $h$ / μm","label":"五次重复测量"},
        },
        "notes": ["隔级差的四个估计共享暗环读数，彼此相关；其标准差仅表征结果离散，不作为均值标准不确定度。", "拟合标准误差只来自残差，未包含显微镜、波长与模型系统分量。", "细丝直径 A 类不确定度只表示五次重复测量均值的随机分量。", "N 按记录的 20 个条纹间隔使用，条纹端点计数约定未另附记录。"],
    }


def radius_sensitivity(result):
    """Leave-one-ring-out fits; the all-data estimate remains the formal result."""
    import plotly.graph_objects as go
    series = result["series"]["ring-fit"]
    x, y = np.array(series["x"]), np.array(series["y"])
    wavelength = result["metrics"]["wavelength_nm"]["value"]*1e-6
    fig = go.Figure()
    steps = []
    for index in range(-1,len(x)):
        keep = np.ones(len(x),dtype=bool)
        if index >= 0:
            keep[index] = False
        slope, intercept = np.polyfit(x[keep], y[keep], 1)
        visible = index == -1
        fig.add_trace(go.Scatter(x=x[keep],y=y[keep],mode="markers",name="采用读数",visible=visible,marker=dict(symbol="circle-open",size=10,color="black",line=dict(width=1.5))))
        fig.add_trace(go.Scatter(x=[5,30],y=[slope*5+intercept,slope*30+intercept],mode="lines",name="线性拟合",visible=visible,line=dict(color="black",width=1.5)))
        choice = "全部六组" if index < 0 else f"暂排除第 {int(x[index])} 级"
        mask = [False]*((len(x)+1)*2)
        mask[(index+1)*2:(index+1)*2+2] = [True,True]
        steps.append(dict(method="update",label=choice,args=[{"visible":mask},{"annotations":[dict(text=f"R = {slope/(4*wavelength):.3f} mm",x=.02,y=.98,xref="paper",yref="paper",showarrow=False,xanchor="left",yanchor="top")]}]))
    fig.update_layout(template="plotly_white",font=dict(family="Times New Roman, SimSun",size=18),height=520,margin=dict(l=85,r=30,t=30,b=120),xaxis_title="暗环级数 m",yaxis_title="直径平方 D² / mm²",sliders=[dict(active=0,steps=steps,currentvalue=dict(prefix="数据选择："))],annotations=steps[0]["args"][1]["annotations"])
    fig.update_xaxes(showline=True,linecolor="black",gridcolor="#eeeeee")
    fig.update_yaxes(showline=True,linecolor="black",gridcolor="#eeeeee")
    return fig


def contact_gap_view(result):
    """Ideal reflected intensity, controlled contact gap, equal beam amplitudes."""
    import plotly.graph_objects as go
    radius = result["metrics"]["radius_fit_mm"]["value"]
    wavelength = result["metrics"]["wavelength_nm"]["value"]*1e-6
    x = np.linspace(-4,4,601)
    xx, yy = np.meshgrid(x,x)
    fig = go.Figure()
    steps = []
    for index, fraction in enumerate(np.linspace(0,.5,11)):
        gap = fraction*wavelength
        intensity = (1-np.cos(4*np.pi*(gap+(xx*xx+yy*yy)/(2*radius))/wavelength))/2
        fig.add_trace(go.Heatmap(x=x,y=x,z=intensity.astype(np.float32),visible=index==0,colorscale=[[0,"black"],[1,"white"]],zmin=0,zmax=1,colorbar=dict(title="I / Imax"),hovertemplate="x=%{x:.2f} mm<br>y=%{y:.2f} mm<br>I/Imax=%{z:.3f}<extra></extra>"))
        visible = [False]*11
        visible[index] = True
        steps.append(dict(method="update",label=f"{fraction:.2f}",args=[{"visible":visible}]))
    fig.update_layout(template="plotly_white",font=dict(family="Times New Roman, SimSun",size=18),height=620,margin=dict(l=85,r=80,t=30,b=120),xaxis_title="横向位置 x / mm",yaxis_title="纵向位置 y / mm",sliders=[dict(steps=steps,currentvalue=dict(prefix="中心间隙 t₀ / λ = "))])
    fig.update_xaxes(showline=True,linecolor="black",gridcolor="#eeeeee")
    fig.update_yaxes(showline=True,linecolor="black",gridcolor="#eeeeee",scaleanchor="x",scaleratio=1)
    return fig


def explore(key, result):
    return {"ring-selection":radius_sensitivity,"contact-gap":contact_gap_view}[key](result)
