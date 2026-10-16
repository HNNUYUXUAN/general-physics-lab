/**
 * Ideal point pendulum, released from rest: theta'' = -(g / L) sin(theta).
 * SI units: length m, gravity m/s², time s, theta rad, omega rad/s.
 * Period: T = 4 sqrt(L/g) K(sin(theta0/2)); K uses the modulus k, not k².
 * Source mapping, model limitations and numerical verification accompany the
 * pendulum simulation in docs/simulation/. No measured noise is synthesized.
 */

export const MODEL_VERSION = '1.0.0';
export const DEFAULT_PARAMETERS = Object.freeze({ length: 1, gravity: 9.81, angleDeg: 20 });
export const PARAMETER_BOUNDS = Object.freeze({
  length: Object.freeze([0.2, 1.2]),
  gravity: Object.freeze([1, 20]),
  angleDeg: Object.freeze([1, 60]),
});

function finite(value, name) {
  if (typeof value !== 'number' || !Number.isFinite(value)) {
    throw new TypeError(`${name} must be a finite number`);
  }
  return value;
}

function positive(value, name) {
  finite(value, name);
  if (value <= 0) throw new RangeError(`${name} must be positive`);
  return value;
}

/** Return a checked copy; omitted fields take the published scenario defaults. */
export function validateParameters(params = DEFAULT_PARAMETERS) {
  if (params === null || typeof params !== 'object' || Array.isArray(params)) {
    throw new TypeError('Parameters must be an object');
  }
  const checked = {};
  for (const [name, [lower, upper]] of Object.entries(PARAMETER_BOUNDS)) {
    const value = Object.hasOwn(params, name) ? params[name] : DEFAULT_PARAMETERS[name];
    finite(value, name);
    if (value < lower || value > upper) {
      throw new RangeError(`${name} must be in [${lower}, ${upper}]`);
    }
    checked[name] = value;
  }
  return checked;
}

export function smallAnglePeriod(params = DEFAULT_PARAMETERS) {
  const { length, gravity } = validateParameters(params);
  return 2 * Math.PI * Math.sqrt(length / gravity);
}

/** Complete elliptic integral K(k) by the arithmetic-geometric mean. */
export function ellipticKAGM(k) {
  finite(k, 'Elliptic modulus');
  if (k < 0 || k >= 1) throw new RangeError('Elliptic modulus must be in [0, 1)');
  let a = 1;
  let b = Math.sqrt((1 - k) * (1 + k));
  for (let i = 0; i < 32; i += 1) {
    const nextA = (a + b) / 2;
    const nextB = Math.sqrt(a * b);
    a = nextA;
    b = nextB;
    if (Math.abs(a - b) <= 4 * Number.EPSILON * a) return Math.PI / (2 * a);
  }
  throw new Error('Arithmetic-geometric mean failed to converge');
}

export function exactPeriod(params = DEFAULT_PARAMETERS) {
  const { length, gravity, angleDeg } = validateParameters(params);
  const k = Math.sin((angleDeg * Math.PI) / 360);
  return 4 * Math.sqrt(length / gravity) * ellipticKAGM(k);
}

function validateState(state) {
  if (!state || typeof state !== 'object') throw new TypeError('State must be an object');
  finite(state.theta, 'theta');
  finite(state.omega, 'omega');
  if (state.t !== undefined) finite(state.t, 't');
}

/** Mechanical energy per unit mass relative to the lowest point, in J/kg. */
export function energy(state, params = DEFAULT_PARAMETERS) {
  validateState(state);
  const { length, gravity } = validateParameters(params);
  return energyUnchecked(state, length, gravity);
}

function energyUnchecked(state, length, gravity) {
  return 0.5 * length ** 2 * state.omega ** 2
    + 2 * gravity * length * Math.sin(state.theta / 2) ** 2;
}

function stepUnchecked(state, dt, length, gravity) {
  const acceleration = theta => -(gravity / length) * Math.sin(theta);
  const k1t = state.omega;
  const k1w = acceleration(state.theta);
  const k2t = state.omega + (dt / 2) * k1w;
  const k2w = acceleration(state.theta + (dt / 2) * k1t);
  const k3t = state.omega + (dt / 2) * k2w;
  const k3w = acceleration(state.theta + (dt / 2) * k2t);
  const k4t = state.omega + dt * k3w;
  const k4w = acceleration(state.theta + dt * k3t);
  return {
    t: (state.t ?? 0) + dt,
    theta: state.theta + (dt / 6) * (k1t + 2 * k2t + 2 * k3t + k4t),
    omega: state.omega + (dt / 6) * (k1w + 2 * k2w + 2 * k3w + k4w),
  };
}

function validateStep(dt) {
  positive(dt, 'dt');
  if (dt > 0.02) throw new RangeError('dt must not exceed 0.02 s');
}

/** Classical fixed-step RK4. Inputs are not mutated. */
export function rk4Step(state, dt, params = DEFAULT_PARAMETERS) {
  validateState(state);
  validateStep(dt);
  const { length, gravity } = validateParameters(params);
  return stepUnchecked(state, dt, length, gravity);
}

/** A reproducible trajectory, including t=0 and the exact requested endpoint. */
export function simulate(params = DEFAULT_PARAMETERS, { duration = 10, dt = 1 / 240 } = {}) {
  const parameters = validateParameters(params);
  const { length, gravity, angleDeg } = parameters;
  finite(duration, 'duration');
  if (duration < 0 || duration > 120) throw new RangeError('duration must be in [0, 120] s');
  validateStep(dt);
  const count = Math.ceil(duration / dt);
  if (count > 100000) throw new RangeError('Simulation requires more than 100000 steps');
  const theta0 = (angleDeg * Math.PI) / 180;
  let state = { t: 0, theta: theta0, omega: 0 };
  const initialEnergy = energyUnchecked(state, length, gravity);
  let maxEnergyDifference = 0;
  const samples = [];
  const record = () => {
    const currentEnergy = energyUnchecked(state, length, gravity);
    maxEnergyDifference = Math.max(maxEnergyDifference, Math.abs(currentEnergy - initialEnergy));
    samples.push({
      ...state,
      energy: currentEnergy,
      linearTheta: theta0 * Math.cos(Math.sqrt(gravity / length) * state.t),
    });
  };
  record();
  for (let i = 1; i <= count; i += 1) {
    const nextTime = Math.min(i * dt, duration);
    state = stepUnchecked(state, nextTime - state.t, length, gravity);
    state.t = nextTime;
    record();
  }
  return {
    parameters,
    samples,
    periodExact: exactPeriod(parameters),
    periodSmallAngle: smallAnglePeriod(parameters),
    relativeEnergyDrift: maxEnergyDifference / initialEnergy,
    dt,
    duration,
  };
}

/** Exact elapsed time for an integer count of full oscillations. */
export function autoMeasurement(params = DEFAULT_PARAMETERS, { oscillations = 20 } = {}) {
  const parameters = validateParameters(params);
  if (!Number.isInteger(oscillations) || oscillations < 1 || oscillations > 100) {
    throw new RangeError('oscillations must be an integer in [1, 100]');
  }
  const period = exactPeriod(parameters);
  return { ...parameters, oscillations, elapsed: oscillations * period, period, source: 'ideal-model' };
}

/**
 * Unweighted OLS of T² = slope L + intercept. Each row is one recorded timing
 * or one supplied period; repeated rows remain repeated observations.
 * gravitySE is propagation of the residual slope standard error only.
 * This is not a full measurement uncertainty budget.
 */
export function fitMeasurements(rows) {
  if (!Array.isArray(rows) || rows.length < 3) throw new RangeError('Fit requires at least three rows');
  const sources = rows.map(row => row?.source ?? null);
  if (sources.some(source => source !== sources[0])) {
    throw new RangeError('Fit requires one common data source for every row');
  }
  if (sources[0] !== null && (typeof sources[0] !== 'string' || sources[0].length === 0)) {
    throw new TypeError('Data source must be a nonempty string when supplied');
  }
  const virtualCount = rows.filter(row => row?.source === 'ideal-model').length;
  if (virtualCount > 0 && virtualCount !== rows.length) {
    throw new RangeError('Ideal-model timings must be fitted separately from other data sources');
  }
  const conditions = {
    dataSource: sources[0] ?? 'supplied-measurements',
    constantGravity: null,
    constantAngleDeg: null,
    angleCorrectionApplied: false,
  };
  for (const [field, key] of [['gravity', 'constantGravity'], ['angleDeg', 'constantAngleDeg']]) {
    if (rows.some(row => row?.[field] !== undefined)) {
      const expected = finite(rows[0]?.[field], `row 1 ${field}`);
      for (let i = 1; i < rows.length; i += 1) {
        finite(rows[i]?.[field], `row ${i + 1} ${field}`);
        if (rows[i][field] !== expected) {
          throw new RangeError(`Fit requires the same ${field} for every row`);
        }
      }
      conditions[key] = expected;
    }
  }
  const pairs = rows.map((row, index) => {
    if (!row || typeof row !== 'object') throw new TypeError(`Invalid row ${index + 1}`);
    const length = positive(row.length, `row ${index + 1} length`);
    let period;
    if (row.elapsed !== undefined || row.oscillations !== undefined) {
      positive(row.elapsed, `row ${index + 1} elapsed`);
      if (!Number.isInteger(row.oscillations) || row.oscillations < 1) {
        throw new RangeError(`row ${index + 1} oscillations must be a positive integer`);
      }
      period = row.elapsed / row.oscillations;
      if (row.period !== undefined) {
        positive(row.period, `row ${index + 1} period`);
        if (Math.abs(row.period - period) > 1e-12 * Math.max(row.period, period)) {
          throw new RangeError(`row ${index + 1} has inconsistent period and elapsed time`);
        }
      }
    } else {
      period = positive(row.period, `row ${index + 1} period`);
    }
    const periodSquared = period ** 2;
    finite(periodSquared, `row ${index + 1} period squared`);
    return { length, period, periodSquared };
  });
  const n = pairs.length;
  const xMean = pairs.reduce((sum, pair) => sum + pair.length, 0) / n;
  const yMean = pairs.reduce((sum, pair) => sum + pair.periodSquared, 0) / n;
  let sxx = 0;
  let sxy = 0;
  let syy = 0;
  for (const pair of pairs) {
    const dx = pair.length - xMean;
    const dy = pair.periodSquared - yMean;
    sxx += dx * dx;
    sxy += dx * dy;
    syy += dy * dy;
  }
  if (!(sxx > 0)) throw new RangeError('Fit requires different lengths');
  const slope = sxy / sxx;
  if (!Number.isFinite(slope) || slope <= 0) throw new RangeError('Fitted slope must be positive');
  const intercept = yMean - slope * xMean;
  const residuals = pairs.map(pair => pair.periodSquared - (slope * pair.length + intercept));
  const sse = residuals.reduce((sum, value) => sum + value ** 2, 0);
  const residualVariance = sse / (n - 2);
  const slopeSE = Math.sqrt(residualVariance / sxx);
  const gravity = (4 * Math.PI ** 2) / slope;
  return {
    slope,
    intercept,
    slopeSE,
    interceptSE: Math.sqrt(residualVariance * (1 / n + xMean ** 2 / sxx)),
    gravity,
    gravitySE: gravity * slopeSE / slope,
    rSquared: syy > 0 ? 1 - sse / syy : null,
    residuals,
    residualVariance,
    pairs,
    count: n,
    degreesOfFreedom: n - 2,
    conditions,
    uncertaintyScope: 'OLS residual standard error; excludes instrument and systematic uncertainty',
  };
}
