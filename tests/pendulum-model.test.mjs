import test from 'node:test';
import assert from 'node:assert/strict';
import {
  DEFAULT_PARAMETERS, validateParameters, smallAnglePeriod, exactPeriod,
  ellipticKAGM, rk4Step, simulate, energy, autoMeasurement, fitMeasurements,
} from '../simulations/pendulum/model.mjs';

function close(actual, expected, tolerance, message = '') {
  assert.ok(Math.abs(actual - expected) <= tolerance,
    `${message}: ${actual} differs from ${expected} by ${Math.abs(actual - expected)} > ${tolerance}`);
}

test('parameter defaults and strict numeric/range validation', () => {
  assert.deepEqual(validateParameters(), DEFAULT_PARAMETERS);
  assert.deepEqual(validateParameters({ length: 0.2 }), { ...DEFAULT_PARAMETERS, length: 0.2 });
  for (const parameters of [
    null, [], { length: NaN }, { length: '1' }, { length: 0.19 }, { length: 1.21 },
    { gravity: 0 }, { gravity: Infinity }, { gravity: 20.1 }, { angleDeg: 0 }, { angleDeg: 61 },
  ]) assert.throws(() => validateParameters(parameters));
});

test('elliptic AGM agrees with zero modulus and independently known special value', () => {
  close(ellipticKAGM(0), Math.PI / 2, 1e-15);
  // K(1/sqrt(2)) = Gamma(1/4)^2 / (4 sqrt(pi)).
  close(ellipticKAGM(Math.SQRT1_2), 1.8540746773013719184, 1e-14);
  for (const invalid of [-0.1, 1, Infinity, NaN]) assert.throws(() => ellipticKAGM(invalid));
});

test('small-angle period and finite-amplitude series agree at one degree', () => {
  const p = { length: 1, gravity: 9.81, angleDeg: 1 };
  close(smallAnglePeriod(p), 2.0060666807106475, 1e-14);
  const angle = Math.PI / 180;
  const series = 1 + angle ** 2 / 16 + 11 * angle ** 4 / 3072;
  close(exactPeriod(p) / smallAnglePeriod(p), series, 1e-14);
});

test('finite-amplitude period increases, scales as sqrt(L/g), and differs at 60 degrees', () => {
  let previous = 0;
  for (const angleDeg of [1, 5, 10, 20, 30, 45, 60]) {
    const p = { ...DEFAULT_PARAMETERS, angleDeg };
    assert.ok(exactPeriod(p) > previous);
    previous = exactPeriod(p);
  }
  const p = { length: 0.2, gravity: 9.81, angleDeg: 60 };
  close(exactPeriod(p) / smallAnglePeriod(p), 1.0731820071493644, 1e-14);
  close(exactPeriod({ ...p, length: 0.8 }) / exactPeriod(p), 2, 1e-14);
  close(exactPeriod({ ...p, gravity: 9.81 / 4 }) / exactPeriod(p), 2, 1e-14);
});

test('RK4 keeps input immutable and accelerates towards equilibrium', () => {
  const state = Object.freeze({ theta: 0.2, omega: 0, t: 0 });
  const next = rk4Step(state, 0.001);
  assert.ok(next.theta < state.theta);
  assert.ok(next.omega < 0);
  close(next.t, 0.001, 0);
  close(energy(state), 9.81 * (1 - Math.cos(0.2)), 1e-14);
  for (const invalid of [0, -1, 0.03, NaN]) assert.throws(() => rk4Step(state, invalid));
  assert.throws(() => rk4Step({ theta: NaN, omega: 0 }, 0.001));
});

test('trajectory endpoints, sampling and initial conditions are reproducible', () => {
  const p = { length: 1, gravity: 9.81, angleDeg: 20 };
  const result = simulate(p, { duration: 1.001, dt: 0.01 });
  assert.equal(result.samples.length, 102);
  assert.equal(result.samples[0].t, 0);
  assert.equal(result.samples.at(-1).t, 1.001);
  close(result.samples[0].theta, Math.PI / 9, 1e-15);
  assert.equal(result.samples[0].omega, 0);
  assert.deepEqual(result, simulate(p, { duration: 1.001, dt: 0.01 }));
  assert.equal(simulate(p, { duration: 0 }).samples.length, 1);
  for (const options of [{ duration: -1 }, { duration: 121 }, { dt: 0 }, { dt: 1e-8 }]) {
    assert.throws(() => simulate(p, options));
  }
});

test('RK4 conserves energy across the permitted extremes at the production step', () => {
  for (const length of [0.2, 1.2]) for (const gravity of [1, 20]) for (const angleDeg of [1, 60]) {
    const result = simulate({ length, gravity, angleDeg }, { duration: 20 });
    assert.ok(result.relativeEnergyDrift < 1e-6,
      `energy drift ${result.relativeEnergyDrift}, L=${length}, g=${gravity}, theta=${angleDeg}`);
  }
});

test('quarter-period trajectory reaches equilibrium and fourth-order convergence is observed', () => {
  const p = { length: 0.2, gravity: 20, angleDeg: 60 };
  const duration = exactPeriod(p) / 4;
  const errors = [0.01, 0.005, 0.0025].map(dt =>
    Math.abs(simulate(p, { duration, dt }).samples.at(-1).theta));
  assert.ok(errors[0] / errors[1] > 12, `coarse/medium convergence ratio ${errors[0] / errors[1]}`);
  assert.ok(errors[1] / errors[2] > 12, `medium/fine convergence ratio ${errors[1] / errors[2]}`);
  assert.ok(errors[2] < 1e-8);
  const final = simulate(p, { duration: exactPeriod(p), dt: 1 / 240 }).samples.at(-1);
  close(final.theta, Math.PI / 3, 1e-8);
  close(final.omega, 0, 2e-6);
});

test('automatic timing represents exact deterministic full periods', () => {
  const one = autoMeasurement(DEFAULT_PARAMETERS, { oscillations: 20 });
  const two = autoMeasurement(DEFAULT_PARAMETERS, { oscillations: 20 });
  assert.equal(one.source, 'ideal-model');
  assert.deepEqual(one, two);
  assert.equal(one.elapsed, 20 * exactPeriod(DEFAULT_PARAMETERS));
  for (const n of [0, -1, 1.5, 101, NaN]) assert.throws(() => autoMeasurement({}, { oscillations: n }));
});

test('OLS recovers analytic known gravity and intercept with residual-only standard error', () => {
  const slope = 4 * Math.PI ** 2 / 9.81;
  const rows = [0.2, 0.4, 0.6, 0.8, 1].map(length => ({ length, period: Math.sqrt(slope * length + 0.02) }));
  const fit = fitMeasurements(rows);
  close(fit.gravity, 9.81, 1e-12);
  close(fit.intercept, 0.02, 1e-14);
  close(fit.slope, slope, 1e-14);
  assert.ok(fit.gravitySE < 1e-12);
  assert.equal(fit.degreesOfFreedom, 3);
  close(fit.rSquared, 1, 1e-15);
  const timings = rows.map(row => ({ length: row.length, elapsed: 20 * row.period, oscillations: 20 }));
  close(fitMeasurements(timings).gravity, fit.gravity, 1e-12);
});

test('OLS slope SE matches a hand-checkable symmetric residual construction', () => {
  // x = 1..5, slope 2, intercept 1, residuals [1,-2,2,-2,1].
  // sum e = sum x*e = 0, SSE=14, Sxx=10, df=3.
  const residuals = [1, -2, 2, -2, 1];
  const rows = [1, 2, 3, 4, 5].map((length, i) => ({ length, period: Math.sqrt(2 * length + 1 + residuals[i]) }));
  const fit = fitMeasurements(rows);
  close(fit.slope, 2, 1e-14);
  close(fit.intercept, 1, 1e-14);
  close(fit.slopeSE, Math.sqrt(14 / 30), 1e-14);
  close(fit.gravitySE, fit.gravity * Math.sqrt(14 / 30) / 2, 1e-13);
});

test('finite-angle synthetic timings reveal the expected small-angle gravity bias', () => {
  const rows = [0.2, 0.4, 0.6, 0.8, 1].map(length => autoMeasurement({ length, gravity: 9.81, angleDeg: 60 }));
  const fit = fitMeasurements(rows);
  const ratio = exactPeriod({ angleDeg: 60 }) / smallAnglePeriod();
  close(fit.gravity, 9.81 / ratio ** 2, 1e-12);
  assert.ok(fit.gravity < 9.81);
  assert.deepEqual(fit.conditions, {
    dataSource: 'ideal-model', constantGravity: 9.81,
    constantAngleDeg: 60, angleCorrectionApplied: false,
  });
});

test('fit separates data identity and requires common model conditions', () => {
  const rows = [0.2, 0.4, 0.6].map(length => autoMeasurement({ length, gravity: 9.81, angleDeg: 20 }));
  assert.throws(() => fitMeasurements([rows[0], rows[1], autoMeasurement({ length: 0.6, gravity: 10, angleDeg: 20 })]));
  assert.throws(() => fitMeasurements([rows[0], rows[1], autoMeasurement({ length: 0.6, gravity: 9.81, angleDeg: 30 })]));
  assert.throws(() => fitMeasurements([rows[0], rows[1], { length: 0.6, period: 2 }]));
  assert.throws(() => fitMeasurements(rows.map((row, i) => i ? row : { ...row, gravity: undefined })));
  const manualRows = rows.map(row => ({ ...row, source: 'manual-timing' }));
  assert.equal(fitMeasurements(manualRows).conditions.dataSource, 'manual-timing');
  assert.throws(() => fitMeasurements(manualRows.map((row, i) => i ? row : { ...row, source: 'source-report' })));
  assert.throws(() => fitMeasurements(manualRows.map((row, i) => i ? row : { ...row, source: undefined })));
  assert.throws(() => fitMeasurements(manualRows.map(row => ({ ...row, source: '' }))));
});

test('regression rejects insufficient, nonfinite, inconsistent and nonphysical inputs', () => {
  const valid = [0.2, 0.4, 0.6].map(length => ({ length, period: Math.sqrt(4 * length) }));
  for (const rows of [
    [], valid.slice(0, 2), valid.map(row => ({ ...row, length: 1 })),
    valid.map(row => ({ ...row, period: 1 })),
    [{ length: 1, period: 3 }, { length: 2, period: 2 }, { length: 3, period: 1 }],
    [{ length: 0, period: 1 }, ...valid],
    [{ length: 0.2, period: NaN }, ...valid],
    [{ length: 0.2, period: 2, elapsed: 20, oscillations: 20 }, ...valid],
    [{ length: 0.2, elapsed: 20, oscillations: 0 }, ...valid],
  ]) assert.throws(() => fitMeasurements(rows));
});
