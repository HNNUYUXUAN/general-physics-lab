"""Build independent SciPy references and check the browser pendulum solver.

Run from a repository checkout, or pass --repo-root and --output-root when
working in a staging directory. Existing reports and notebooks are read only.
The reference calculation uses scipy.special.ellipk and DOP853, independently
of the browser implementation's AGM elliptic integral and fixed-step RK4.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess
import sys

import numpy as np
import scipy
from scipy.integrate import solve_ivp
from scipy.special import ellipk
from scipy.stats import linregress


EXPERIMENT = Path("experiments/course-01/pendulum")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def observations(repo: Path) -> dict:
    experiment = repo / EXPERIMENT
    config = read_json(experiment / "experiment.json")
    provenance = read_json(experiment / "data/provenance.json")
    saved = read_json(experiment / "results/python.json")
    raw_diameters = read_csv(experiment / "data/diameters.csv")
    raw_measurements = read_csv(experiment / "data/measurements.csv")
    if len(raw_diameters) != 6 or len(raw_measurements) != 18:
        raise ValueError("Expected the approved dataset of 6 diameters and 18 timing readings")
    identifiers = {(r["run_id"], r["repeat_id"]) for r in raw_measurements}
    if len(identifiers) != len(raw_measurements):
        raise ValueError("Duplicate source reading identifiers")
    diameters = [{"repeat_id": int(r["repeat_id"]), "diameter_cm": float(r["diameter_cm"]),
                  "as_recorded": r} for r in raw_diameters]
    measurements = [{"run_id": int(r["run_id"]), "repeat_id": int(r["repeat_id"]),
                     "string_length_cm": float(r["string_length_cm"]),
                     "oscillations": int(r["oscillations"]),
                     "elapsed_time_s": float(r["elapsed_time_s"]), "as_recorded": r}
                    for r in raw_measurements]
    diameters_m = np.array([r["diameter_cm"] / 100 for r in diameters])
    mean_diameter = float(diameters_m.mean())
    diameter_u = float(diameters_m.std(ddof=1) / math.sqrt(len(diameters_m)))
    groups = []
    for run in range(1, 7):
        records = [r for r in measurements if r["run_id"] == run]
        if len(records) != 3 or len({r["string_length_cm"] for r in records}) != 1:
            raise ValueError(f"Source run {run} has inconsistent repeats")
        if any(r["oscillations"] != config["oscillations"] for r in records):
            raise ValueError("Timing count mismatch")
        times = np.array([r["elapsed_time_s"] for r in records])
        mean = float(times.mean())
        mean_u = float(times.std(ddof=1) / math.sqrt(len(times)))
        period = mean / config["oscillations"]
        period_u = mean_u / config["oscillations"]
        string_length = records[0]["string_length_cm"] / 100
        length = string_length + mean_diameter / 2
        groups.append({"run_id": run, "source_repeat_ids": [r["repeat_id"] for r in records],
                       "string_length_m": string_length, "effective_length_m": length,
                       "mean_elapsed_time_s": mean, "time_mean_u_a_s": mean_u,
                       "period_s": period, "period_u_a_s": period_u,
                       "period_squared_s2": period ** 2,
                       "period_squared_u_a_s2": 2 * period * period_u,
                       "gravity_individual_m_s2": 4 * math.pi ** 2 * length / period ** 2})
    x = np.array([r["effective_length_m"] for r in groups])
    y = np.array([r["period_squared_s2"] for r in groups])
    regression = linregress(x, y)
    gravity = float(4 * math.pi ** 2 / regression.slope)
    gravity_se = float(gravity * regression.stderr / regression.slope)
    if not math.isclose(gravity, saved["metrics"]["gravity_fit"]["value"], rel_tol=1e-12):
        raise AssertionError("Independent source-data fit differs from approved saved result")
    residuals = y - (regression.slope * x + regression.intercept)
    for group, residual in zip(groups, residuals, strict=True):
        group["residual_s2"] = float(residual)
    source_paths = [EXPERIMENT / "experiment.json", EXPERIMENT / "data/diameters.csv",
                    EXPERIMENT / "data/measurements.csv", EXPERIMENT / "data/provenance.json",
                    EXPERIMENT / "results/python.json", Path("src/physicslab/experiments/pendulum.py")]
    return {
        "schema_version": 1, "experiment_id": "course-01/pendulum",
        "source_identity": {"label": "源实验报告观测记录", "data_version": config["data_version"],
                            "measurement_date": config["measurement_date"], "nature": config["data_nature"],
                            "primary_document": provenance["sources"][0],
                            "pdf_url": "../../pdf/course-01/单摆测重力加速度/牛顿第二运动定律测重力加速度实验报告.pdf"},
        "source_files": [{"path": p.as_posix(), "sha256": sha256(repo / p)} for p in source_paths],
        "parameters": {"oscillations_per_reading": config["oscillations"],
                       "units": config["units"], "length_definition": config["analysis"]["length_definition"],
                       "reference_gravity_m_s2": config["reference_gravity_m_s2"],
                       "reference_gravity_status": config["reference_gravity_status"],
                       "measured_initial_angle_deg": None, "instrument_error_limits": config["instruments"],
                       "uncertainty_scope": config["analysis"]["uncertainty_scope"]},
        "raw": {"diameters": diameters, "measurements": measurements},
        "derived": {"method": "原始读数转换为 SI 单位，重复计时取均值；含截距普通最小二乘拟合 T² 对有效摆长。",
                    "diameter": {"mean_m": mean_diameter, "mean_u_a_m": diameter_u}, "groups": groups,
                    "fit": {"method": "ordinary_least_squares_with_intercept", "slope_s2_m": float(regression.slope),
                            "intercept_s2": float(regression.intercept), "slope_standard_error_s2_m": float(regression.stderr),
                            "r_squared": float(regression.rvalue ** 2), "gravity_m_s2": gravity,
                            "gravity_regression_standard_error_m_s2": gravity_se,
                            "gravity_individual_mean_m_s2": float(np.mean([r["gravity_individual_m_s2"] for r in groups])),
                            "uncertainty_definition": "OLS 残差估计的回归标准误，不包含仪器与完整系统误差预算。"}},
        "provenance": provenance,
    }


def reference_case(length: float, gravity: float, angle_deg: float, gravity_source: str) -> dict:
    theta0 = math.radians(angle_deg)
    parameter_m = math.sin(theta0 / 2) ** 2
    exact = float(4 * math.sqrt(length / gravity) * ellipk(parameter_m))
    linear = 2 * math.pi * math.sqrt(length / gravity)
    duration = 4 * exact
    times = np.linspace(0, duration, 65)

    def rhs(_time, state):
        return [state[1], -gravity / length * math.sin(state[0])]

    def downward_crossing(_time, state):
        return state[0]

    downward_crossing.direction = -1
    solution = solve_ivp(rhs, (0, duration), [theta0, 0], method="DOP853", t_eval=times,
                         events=downward_crossing, rtol=5e-13, atol=2e-15, max_step=exact / 80)
    if not solution.success or len(solution.t_events[0]) < 4:
        raise RuntimeError(solution.message)
    theta, omega = solution.y
    energy = 0.5 * length ** 2 * omega ** 2 + 2 * gravity * length * np.sin(theta / 2) ** 2
    drift = float(np.max(np.abs(energy / energy[0] - 1)))
    event_period = float(4 * solution.t_events[0][0])
    event_error = abs(event_period / exact - 1)
    if drift > 1e-10 or event_error > 1e-10:
        raise AssertionError("DOP853 reference failed its elliptic-period or energy cross-check")
    return {"id": f"{gravity_source}-L{length:g}-a{angle_deg:g}",
            "parameters": {"length": length, "gravity": gravity, "angleDeg": angle_deg},
            "parameter_units": {"length": "m", "gravity": "m/s^2", "angleDeg": "degree"},
            "initial_angular_velocity_rad_s": 0, "gravity_source": gravity_source,
            "elliptic_parameter_m": parameter_m, "period_exact_s": exact, "period_small_angle_s": linear,
            "period_from_ode_zero_crossing_s": event_period, "ode_period_relative_error": event_error,
            "period_excess_pct": 100 * (exact / linear - 1),
            "small_angle_inferred_gravity_m_s2": 4 * math.pi ** 2 * length / exact ** 2,
            "small_angle_inferred_gravity_bias_pct": 100 * ((linear / exact) ** 2 - 1),
            "duration_s": duration, "initial_energy_per_mass_J_kg": float(energy[0]),
            "reference_relative_energy_drift": drift,
            "trajectory": [{"t": float(t), "theta": float(a), "omega": float(w), "energy": float(e)}
                           for t, a, w, e in zip(times, theta, omega, energy, strict=True)]}


NODE_CHECK = r"""
import fs from 'node:fs';
const payload = JSON.parse(fs.readFileSync(0, 'utf8'));
const model = await import(payload.modelUrl);
const required = ['exactPeriod', 'smallAnglePeriod', 'rk4Step', 'energy', 'simulate'];
for (const symbol of required) if (typeof model[symbol] !== 'function') throw new Error(`Missing export ${symbol}`);
function trajectoryError(c, dt) {
  let state = {theta: c.parameters.angleDeg * Math.PI / 180, omega: 0, t: 0};
  let angleError = 0, omegaError = 0, drift = 0;
  for (const reference of c.trajectory) {
    while (state.t < reference.t - 1e-13) {
      const step = Math.min(dt, reference.t - state.t);
      state = model.rk4Step(state, step, c.parameters);
    }
    angleError = Math.max(angleError, Math.abs(state.theta - reference.theta));
    omegaError = Math.max(omegaError, Math.abs(state.omega - reference.omega));
    drift = Math.max(drift, Math.abs(model.energy(state, c.parameters) / c.initial_energy_per_mass_J_kg - 1));
  }
  return {max_angle_error_rad: angleError, max_angular_velocity_error_rad_s: omegaError, relative_energy_drift: drift};
}
const rows = payload.cases.map(c => {
  const standard = trajectoryError(c, 1 / 240);
  const coarseDt = Math.min(0.02, c.period_exact_s / 80);
  const coarse = trajectoryError(c, coarseDt);
  const fine = trajectoryError(c, coarseDt / 2);
  const sim = model.simulate(c.parameters, {duration: c.duration_s, dt: 1 / 240});
  return {case_id: c.id, period_relative_error: Math.abs(model.exactPeriod(c.parameters) / c.period_exact_s - 1),
    small_angle_period_relative_error: Math.abs(model.smallAnglePeriod(c.parameters) / c.period_small_angle_s - 1),
    ...standard, production_simulation_energy_drift: sim.relativeEnergyDrift, convergence_coarse_dt_s: coarseDt,
    convergence_angle_error_ratio: coarse.max_angle_error_rad / fine.max_angle_error_rad,
    convergence_omega_error_ratio: coarse.max_angular_velocity_error_rad_s / fine.max_angular_velocity_error_rad_s};
});
console.log(JSON.stringify({engine: process.version, cases: rows}));
"""


def verify_browser(model: Path, cases: list[dict]) -> dict:
    process = subprocess.run(["node", "--input-type=module", "-e", NODE_CHECK],
                             input=json.dumps({"modelUrl": model.as_uri(), "cases": cases}),
                             capture_output=True, text=True, encoding="utf-8", timeout=120)
    if process.returncode:
        raise RuntimeError(f"Browser model verification failed:\n{process.stderr}")
    result = json.loads(process.stdout)
    tolerances = {"period_relative_error_max": 1e-12, "small_angle_period_relative_error_max": 1e-12,
                  "max_angle_error_rad_max": 2e-6, "max_angular_velocity_error_rad_s_max": 2e-5,
                  "relative_energy_drift_max": 1e-7, "production_simulation_energy_drift_max": 1e-7,
                  "convergence_angle_error_ratio_min": 10, "convergence_omega_error_ratio_min": 10}
    failures = []
    for case in result["cases"]:
        for constraint, limit in tolerances.items():
            name, direction = constraint.rsplit("_", 1)
            value = case[name]
            if not math.isfinite(value) or (value > limit if direction == "max" else value < limit):
                failures.append({"case_id": case["case_id"], "metric": name, "value": value, "constraint": constraint, "limit": limit})
    return {"status": "passed" if not failures else "failed", "node_version": result["engine"],
            "model_sha256": sha256(model), "tolerances": tolerances,
            "algorithm": "AGM 周期与 SciPy ellipk 比较；固定步长 RK4 与 DOP853 比较；步长 min(0.02 s,T/80) 与其一半的误差比检验四阶收敛。",
            "production_dt_s": 1 / 240, "cases": result["cases"], "failures": failures}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output-root", type=Path, help="Defaults to --repo-root")
    parser.add_argument("--simulation-dir", type=Path, default=Path("simulations/pendulum"), help="Relative output directory for the browser module")
    parser.add_argument("--model", type=Path, help="Defaults to output-root/simulation-dir/model.mjs")
    parser.add_argument("--references-only", action="store_true", help="Generate fixtures without checking browser implementation")
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    output = (args.output_root or repo).resolve()
    observation_data = observations(repo)
    fitted_gravity = observation_data["derived"]["fit"]["gravity_m_s2"]
    cases = [reference_case(length, gravity, angle, source)
             for source, gravity in [("report-reference", 9.81), ("source-data-fit", fitted_gravity),
                                     ("scenario-lower-bound", 1.0), ("scenario-upper-bound", 20.0)]
             for length in [0.2, 0.6, 1.2] for angle in [1, 5, 20, 60]]
    fixture = {"schema_version": 1, "experiment_id": "course-01/pendulum", "model_id": "ideal-undamped-point-pendulum",
               "generated_at_utc": datetime.now(timezone.utc).isoformat(),
               "environment": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
                               "platform": platform.platform()},
               "generator_sha256": sha256(Path(__file__)), "source_files": observation_data["source_files"],
               "reference_method": {"period": "4 sqrt(L/g) scipy.special.ellipk(sin(theta0/2)^2)",
                                    "elliptic_convention": "m = k^2 = sin(theta0/2)^2", "trajectory": "scipy.integrate.solve_ivp DOP853",
                                    "rtol": 5e-13, "atol": 2e-15, "max_step": "T_exact/80", "duration": "4 T_exact",
                                    "sample_count": 65, "energy_per_mass": "L^2 omega^2/2 + 2 g L sin(theta/2)^2",
                                    "assumptions": ["质点摆球", "无质量刚性摆线", "无阻尼", "无驱动力", "从静止释放"]},
               "data_check": {"status": "passed", "diameter_readings": 6, "timing_readings": 18, "length_groups": 6,
                              "independent_fit_method": "scipy.stats.linregress", "fitted_gravity_m_s2": fitted_gravity,
                              "saved_gravity_match_rtol": 1e-12}, "case_count": len(cases), "cases": cases}
    model = (args.model or output / args.simulation_dir / "model.mjs").resolve()
    if args.references_only:
        fixture["browser_verification"] = {"status": "not_run", "reason": "--references-only"}
    else:
        if not model.is_file():
            raise FileNotFoundError(f"Browser model not found: {model}; use --references-only to generate references alone")
        fixture["browser_verification"] = verify_browser(model, cases)
    fixture_path = output / "docs/simulation/pendulum-reference.json"
    observation_path = output / args.simulation_dir / "observations.json"
    write_json(fixture_path, fixture)
    write_json(observation_path, observation_data)
    print(json.dumps({"reference_file": str(fixture_path), "observation_file": str(observation_path),
                      "cases": len(cases), "fitted_gravity_m_s2": fitted_gravity,
                      "browser_verification": fixture["browser_verification"]["status"],
                      "max_reference_energy_drift": max(c["reference_relative_energy_drift"] for c in cases)}, ensure_ascii=False))
    return 1 if fixture["browser_verification"]["status"] == "failed" else 0


if __name__ == "__main__":
    sys.exit(main())
