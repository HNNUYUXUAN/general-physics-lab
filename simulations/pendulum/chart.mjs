import { exactPeriod, smallAnglePeriod } from './model.mjs';

const NS = 'http://www.w3.org/2000/svg';
const FONT = '"Times New Roman", SimSun, serif';
const INK = '#202020';
const GRAY = '#777777';

function element(name, attributes = {}, text) {
  const node = document.createElementNS(NS, name);
  for (const [key, value] of Object.entries(attributes)) node.setAttribute(key, String(value));
  if (text !== undefined) node.textContent = text;
  return node;
}

function add(parent, name, attributes, text) {
  const node = element(name, attributes, text);
  parent.append(node);
  return node;
}

function reset(svg, description) {
  svg.replaceChildren();
  svg.setAttribute('font-family', FONT);
  svg.setAttribute('font-size', '16');
  svg.setAttribute('fill', INK);
  svg.setAttribute('role', 'img');
  svg.setAttribute('aria-label', description);
  add(svg, 'title', {}, description);
}

function number(value) {
  if (Math.abs(value) < 1e-12) return '0';
  if (Math.abs(value) >= 10000 || Math.abs(value) < 0.001) return value.toExponential(1);
  return String(Number(value.toPrecision(4)));
}

function plot(svg, { xDomain, yDomain, xLabel, yLabel, description }) {
  reset(svg, description);
  const [, , width, height] = svg.getAttribute('viewBox').split(/\s+/).map(Number);
  const box = { left: 78, top: 35, right: width - 24, bottom: height - 52 };
  const x = value => box.left + ((value - xDomain[0]) / (xDomain[1] - xDomain[0])) * (box.right - box.left);
  const y = value => box.bottom - ((value - yDomain[0]) / (yDomain[1] - yDomain[0])) * (box.bottom - box.top);
  for (let i = 0; i <= 4; i += 1) {
    const yValue = yDomain[0] + (i / 4) * (yDomain[1] - yDomain[0]);
    const py = y(yValue);
    add(svg, 'line', { x1: box.left, x2: box.right, y1: py, y2: py, stroke: '#e6e6e6', 'stroke-width': 1 });
    add(svg, 'line', { x1: box.left, x2: box.left + 5, y1: py, y2: py, stroke: INK });
    add(svg, 'text', { x: box.left - 10, y: py + 5, 'text-anchor': 'end', 'font-size': 16 }, number(yValue));
    const xValue = xDomain[0] + (i / 4) * (xDomain[1] - xDomain[0]);
    const px = x(xValue);
    add(svg, 'line', { x1: px, x2: px, y1: box.bottom, y2: box.bottom - 5, stroke: INK });
    add(svg, 'text', { x: px, y: box.bottom + 23, 'text-anchor': 'middle', 'font-size': 16 }, number(xValue));
  }
  add(svg, 'path', {
    d: `M${box.left},${box.top} V${box.bottom} H${box.right}`,
    stroke: INK, 'stroke-width': 1.4, fill: 'none',
  });
  add(svg, 'text', { x: (box.left + box.right) / 2, y: height - 9, 'text-anchor': 'middle', 'font-size': 17 }, xLabel);
  const yMid = (box.top + box.bottom) / 2;
  add(svg, 'text', { x: 20, y: yMid, 'text-anchor': 'middle', 'font-size': 17, transform: `rotate(-90 20 ${yMid})` }, yLabel);
  const clipId = `${svg.id}-data-clip`;
  const definitions = add(svg, 'defs');
  const clip = add(definitions, 'clipPath', { id: clipId });
  add(clip, 'rect', { x: box.left, y: box.top, width: box.right - box.left, height: box.bottom - box.top });
  const dataLayer = add(svg, 'g', { 'clip-path': `url(#${clipId})` });
  return { x, y, box, width, height, dataLayer };
}

function path(parent, pairs, x, y, attributes = {}) {
  if (!pairs.length) return;
  const d = pairs.map(([px, py], i) => `${i ? 'L' : 'M'}${x(px).toFixed(3)},${y(py).toFixed(3)}`).join(' ');
  return add(parent, 'path', { d, fill: 'none', stroke: INK, 'stroke-width': 1.8, ...attributes });
}

function legend(svg, x, y, text, { dashed = false, marker = false } = {}) {
  add(svg, 'line', { x1: x, x2: x + 28, y1: y - 4, y2: y - 4, stroke: dashed ? GRAY : INK,
    'stroke-width': 1.8, ...(dashed ? { 'stroke-dasharray': '6 4' } : {}) });
  if (marker) add(svg, 'circle', { cx: x + 14, cy: y - 4, r: 3.5, fill: 'white', stroke: INK, 'stroke-width': 1.6 });
  add(svg, 'text', { x: x + 36, y, 'font-size': 17 }, text);
}

/** Build a fixed-scale apparatus and return a cheap frame updater. */
export function renderPendulum(svg, params) {
  reset(svg, '理想单摆装置：实线显示非线性模型，虚线显示小角度近似；长度按固定比例显示。');
  const pivot = { x: 350, y: 48 };
  const pixelsPerMetre = 215;
  const length = pixelsPerMetre * params.length;
  add(svg, 'line', { x1: 290, x2: 410, y1: pivot.y - 8, y2: pivot.y - 8, stroke: INK, 'stroke-width': 3 });
  for (let x = 295; x < 410; x += 12) add(svg, 'line', { x1: x, x2: x + 8, y1: pivot.y - 8, y2: pivot.y - 18, stroke: GRAY });
  add(svg, 'line', { x1: pivot.x, x2: pivot.x, y1: pivot.y, y2: 314, stroke: '#aaaaaa', 'stroke-dasharray': '4 5' });
  const initialAngle = params.angleDeg * Math.PI / 180;
  const ghost = { x: pivot.x + length * Math.sin(initialAngle), y: pivot.y + length * Math.cos(initialAngle) };
  add(svg, 'line', { x1: pivot.x, y1: pivot.y, x2: ghost.x, y2: ghost.y, stroke: '#cccccc', 'stroke-dasharray': '2 5' });
  add(svg, 'circle', { cx: ghost.x, cy: ghost.y, r: 11, stroke: '#cccccc', fill: 'white', 'stroke-dasharray': '2 3' });
  const linearRod = add(svg, 'line', { x1: pivot.x, y1: pivot.y, stroke: GRAY, 'stroke-width': 1.4, 'stroke-dasharray': '6 5' });
  const linearBob = add(svg, 'circle', { r: 10, fill: 'white', stroke: GRAY, 'stroke-width': 1.4, 'stroke-dasharray': '4 3' });
  const rod = add(svg, 'line', { x1: pivot.x, y1: pivot.y, stroke: INK, 'stroke-width': 2 });
  const bob = add(svg, 'circle', { r: 11, fill: 'white', stroke: INK, 'stroke-width': 2.2 });
  add(svg, 'circle', { cx: pivot.x, cy: pivot.y, r: 4, fill: INK });
  const arc = add(svg, 'path', { stroke: GRAY, 'stroke-width': 1.1, fill: 'none' });
  const thetaLabel = add(svg, 'text', { x: 20, y: 66 }, '');
  const omegaLabel = add(svg, 'text', { x: 20, y: 94 }, '');
  add(svg, 'text', { x: 20, y: 335, 'font-size': 14 }, `L = ${params.length.toFixed(2)} m`);
  add(svg, 'text', { x: 180, y: 335, 'font-size': 14 }, `θ₀ = ${params.angleDeg}°`);
  add(svg, 'text', { x: 350, y: 335, 'font-size': 14 }, `g = ${Number(params.gravity.toPrecision(7))} m/s²`);
  add(svg, 'text', { x: 680, y: 335, 'text-anchor': 'end', 'font-size': 14, fill: GRAY }, '从静止释放');
  return (state, compareLinear = true) => {
    const x = pivot.x + length * Math.sin(state.theta);
    const y = pivot.y + length * Math.cos(state.theta);
    rod.setAttribute('x2', x); rod.setAttribute('y2', y);
    bob.setAttribute('cx', x); bob.setAttribute('cy', y);
    const radius = Math.min(42, length * 0.5);
    const arcX = pivot.x + radius * Math.sin(state.theta);
    const arcY = pivot.y + radius * Math.cos(state.theta);
    arc.setAttribute('d', `M${pivot.x},${pivot.y + radius} A${radius},${radius} 0 0 ${state.theta > 0 ? 0 : 1} ${arcX},${arcY}`);
    const linearTheta = initialAngle * Math.cos(Math.sqrt(params.gravity / params.length) * state.t);
    linearRod.setAttribute('x2', pivot.x + length * Math.sin(linearTheta));
    linearRod.setAttribute('y2', pivot.y + length * Math.cos(linearTheta));
    linearBob.setAttribute('cx', pivot.x + length * Math.sin(linearTheta));
    linearBob.setAttribute('cy', pivot.y + length * Math.cos(linearTheta));
    linearRod.style.display = compareLinear ? '' : 'none';
    linearBob.style.display = compareLinear ? '' : 'none';
    thetaLabel.textContent = `θ = ${(state.theta * 180 / Math.PI).toFixed(2)}°`;
    omegaLabel.textContent = `ω = ${state.omega.toFixed(3)} rad/s`;
  };
}

/** Curves are prepared once; the returned function moves only the time cursor. */
export function renderTrajectory(svg, simulation, compareLinear = true) {
  const amplitude = simulation.parameters.angleDeg;
  const { x, y, box } = plot(svg, {
    xDomain: [0, simulation.duration], yDomain: [-amplitude * 1.12, amplitude * 1.12],
    xLabel: '时间 t / s', yLabel: '摆角 θ / °', description: '非线性单摆与小角度近似的摆角随时间变化',
  });
  const stride = Math.max(1, Math.ceil(simulation.samples.length / 1000));
  const samples = simulation.samples.filter((_, i) => i % stride === 0 || i === simulation.samples.length - 1);
  if (compareLinear) path(svg, samples.map(row => [row.t, row.linearTheta * 180 / Math.PI]), x, y,
    { stroke: GRAY, 'stroke-dasharray': '6 4', 'stroke-width': 1.4 });
  path(svg, samples.map(row => [row.t, row.theta * 180 / Math.PI]), x, y);
  legend(svg, box.left, 19, '非线性单摆');
  if (compareLinear) legend(svg, box.left + 200, 19, '小角度近似', { dashed: true });
  const cursor = add(svg, 'line', { x1: x(0), x2: x(0), y1: box.top, y2: box.bottom, stroke: '#999999', 'stroke-width': 1, 'stroke-dasharray': '3 5' });
  return time => {
    cursor.style.display = time <= simulation.duration ? '' : 'none';
    cursor.setAttribute('x1', x(time)); cursor.setAttribute('x2', x(time));
  };
}

export function renderFit(svg, rows, fit = null) {
  const points = rows.map(row => [row.length, (row.elapsed / row.oscillations) ** 2]);
  let xMin = 0.2; let xMax = 1.2; let yMin = 0; let yMax = 6;
  if (points.length) {
    const xs = points.map(point => point[0]); const ys = points.map(point => point[1]);
    xMin = Math.max(0, Math.min(...xs) - 0.06); xMax = Math.max(...xs) + 0.06;
    if (fit) ys.push(fit.slope * xMin + fit.intercept, fit.slope * xMax + fit.intercept);
    const pad = Math.max(0.05, (Math.max(...ys) - Math.min(...ys)) * 0.12);
    yMin = Math.max(0, Math.min(...ys) - pad); yMax = Math.max(...ys) + pad;
  }
  const { x, y, box, dataLayer } = plot(svg, { xDomain: [xMin, xMax], yDomain: [yMin, yMax],
    xLabel: '有效摆长 L / m', yLabel: '周期平方 T² / s²', description: '所选来源与当前模型条件下的周期平方对摆长拟合' });
  if (!points.length) {
    add(svg, 'text', { x: (box.left + box.right) / 2, y: (box.top + box.bottom) / 2,
      'text-anchor': 'middle', 'font-size': 16, fill: GRAY }, '改变摆长并记录，建立本组数据');
    return;
  }
  if (fit) path(dataLayer, [[xMin, fit.slope * xMin + fit.intercept], [xMax, fit.slope * xMax + fit.intercept]], x, y);
  points.forEach(([length, squared], i) => {
    const marker = add(dataLayer, 'circle', { cx: x(length), cy: y(squared), r: 4.5, fill: 'white', stroke: INK, 'stroke-width': 1.6 });
    add(marker, 'title', {}, `第 ${i + 1} 条：L=${length} m，T²=${squared} s²`);
  });
  legend(svg, box.left, 19, fit ? '记录与含截距拟合' : '当前记录', { marker: true });
}

export function renderScan(svg, params) {
  const base = smallAnglePeriod(params);
  const values = [[0, 0], ...Array.from({ length: 60 }, (_, i) => {
    const angle = i + 1;
    return [angle, 100 * (exactPeriod({ ...params, angleDeg: angle }) / base - 1)];
  })];
  const { x, y, box } = plot(svg, { xDomain: [0, 60], yDomain: [0, 8],
    xLabel: '初始摆角 θ₀ / °', yLabel: '周期增量 ΔT / T₀ / %', description: '初始摆角对精确周期相对小角度周期增量的影响' });
  path(svg, values, x, y);
  const selected = 100 * (exactPeriod(params) / base - 1);
  add(svg, 'line', { x1: x(params.angleDeg), x2: x(params.angleDeg), y1: y(selected), y2: box.bottom,
    stroke: GRAY, 'stroke-dasharray': '4 5' });
  add(svg, 'circle', { cx: x(params.angleDeg), cy: y(selected), r: 5, fill: 'white', stroke: INK, 'stroke-width': 2 });
  add(svg, 'text', { x: box.left, y: 19, 'font-size': 17 }, `当前 ${params.angleDeg}°：周期增加 ${selected.toFixed(3)}%`);
}
