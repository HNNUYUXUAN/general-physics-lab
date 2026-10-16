from pathlib import Path
import numpy as np
from scipy.stats import linregress
from physicslab.experiments.pendulum import analyze,load_data
from physicslab.experiments.interactive import fit_scenarios,model_scenarios,animation
ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/"experiments/course-01/pendulum"

def test_fit_selection_recomputes_each_subset():
    r=analyze(EXP);_,scenarios=fit_scenarios(r)
    assert len(scenarios)==7
    for s in scenarios:
        expected=linregress(s["x"],s["y"])
        assert np.isclose(s["g"],4*np.pi**2/expected.slope,rtol=1e-12)
        assert len(s["residual"])==(6 if s["omit"]==0 else 5)
        assert abs(sum(s["residual"]))<1e-9

def test_model_presets_recompute_period_and_keep_canonical_config():
    c,_,_=load_data(EXP);r=analyze(EXP);scenes=model_scenarios(c,r["metrics"]["gravity_fit"]["value"])
    by_pair={(a,l):s for a,l,s in scenes}
    assert c["simulation"]["initial_angle_deg"]==20
    assert by_pair[60,1.]["period_exact_s"]>by_pair[5,1.]["period_exact_s"]
    assert np.isclose(by_pair[20,1.5]["period_exact_s"]/by_pair[20,.5]["period_exact_s"],np.sqrt(3))
    assert all(s["relative_energy_drift"]<1e-7 for _,_,s in scenes)

def test_animation_tracks_integrated_state_and_preserves_length():
    r=analyze(EXP);f=animation(r);l=r["model_parameters"]["length_m"]
    assert len(f.frames)>50
    for frame in f.frames:
        bob=frame.data[0]
        assert np.isclose(bob.x[1]**2+bob.y[1]**2,l*l)
        index=np.argmin(abs(np.array(r["simulation"]["time_s"])-float(frame.name)))
        assert np.isclose(frame.data[1].x[0],np.rad2deg(r["simulation"]["angle_rad"][index]))

def test_report_follows_docx_outline():
    report=(EXP/"report/report.md").read_text(encoding="utf-8")
    headings=[line[3:] for line in report.splitlines() if line.startswith("## ")]
    assert headings==["实验目的","实验原理","主要仪器设备","实验步骤","原始数据记录","数据处理","实验结果与讨论"]
    assert report.startswith("# 淮南师范学院实验报告")
    assert "| 测量次数 | 1 | 2 | 3 | 4 | 5 | 6 | 平均值 |" in report

