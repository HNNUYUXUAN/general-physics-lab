import {
  MODEL_VERSION, DEFAULT_PARAMETERS, validateParameters, exactPeriod, smallAnglePeriod,
  rk4Step, simulate, autoMeasurement, fitMeasurements,
} from './model.mjs';
import { renderPendulum, renderTrajectory, renderFit, renderScan } from './chart.mjs';

const $ = id => document.getElementById(id);
const STORAGE_KEY = 'physicslab.pendulum.simulation.v1';
const STORAGE_SCHEMA = 1;
const MAX_RECORDS = 100;
const MAX_TIME = 60;
const DT = 1 / 240;
const SOURCE_LABELS = { 'ideal-model': '理想模型计时', 'manual-timing': '手动计时' };
const ids = ['length', 'length-value', 'angle', 'angle-value', 'gravity', 'cycles',
  'play', 'reset', 'record', 'source-gravity', 'clock', 'status', 'pendulum', 'trajectory',
  'fit-chart', 'scan-chart', 'summary', 'records', 'clear', 'export-csv', 'export-json',
  'compare-linear', 'record-count', 'fit-result', 'source-table', 'source-fit',
  'timer-start', 'timer-stop', 'timer-record', 'timer-value', 'timer-status', 'fit-source'];
for (const id of ids) if (!$(id)) throw new Error(`Missing simulation element: #${id}`);

let params = { ...DEFAULT_PARAMETERS };
let records = [];
let state = initialState();
let running = false;
let frameId = null;
let lastWallTime = null;
let accumulator = 0;
let updateApparatus = () => {};
let updateCursor = () => {};
let trajectory = null;
let timer = null;
let sourceData = null;
let nextRecordId = 1;
let storageAvailable = true;
let gravityRejected = false;

function initialState() {
  return { t: 0, theta: params.angleDeg * Math.PI / 180, omega: 0 };
}

function say(message) { $('status').textContent = message; }

function element(name, text, className) {
  const node = document.createElement(name);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}

function format(value, digits = 6) {
  if (Math.abs(value) < 1e-14) return '0';
  return Number(value.toPrecision(digits)).toString();
}

function readCycles() {
  const count = Number($('cycles').value);
  if (!Number.isInteger(count) || count < 1 || count > 100) throw new Error('全振动次数请填 1–100 的整数。');
  return count;
}

function currentSource() { return $('fit-source').value === 'manual-timing' ? 'manual-timing' : 'ideal-model'; }

function checkedStoredRecord(row) {
  if (!row || !Object.hasOwn(SOURCE_LABELS, row.source)) return null;
  try {
    const p = validateParameters({ length: row.length, gravity: row.gravity, angleDeg: row.angleDeg });
    if (!Number.isInteger(row.oscillations) || row.oscillations < 1 || row.oscillations > 100
      || !Number.isFinite(row.elapsed) || row.elapsed <= 0) return null;
    if (row.source === 'ideal-model') {
      const expected = exactPeriod(p) * row.oscillations;
      if (Math.abs(row.elapsed - expected) > 1e-10 * expected) return null;
    } else if (row.elapsed > MAX_TIME) return null;
    const saved = { ...p, oscillations: row.oscillations, elapsed: row.elapsed,
      period: row.elapsed / row.oscillations, source: row.source };
    if (row.source === 'manual-timing') {
      if (!Number.isFinite(row.startTime) || !Number.isFinite(row.endTime)
        || row.startTime < 0 || row.endTime > MAX_TIME || row.endTime <= row.startTime
        || Math.abs(row.endTime - row.startTime - row.elapsed) > 1e-10) return null;
      saved.startTime = row.startTime; saved.endTime = row.endTime;
    }
    saved.createdAt = typeof row.createdAt === 'string' && Number.isFinite(Date.parse(row.createdAt))
      ? new Date(row.createdAt).toISOString() : null;
    saved.id = nextRecordId++;
    return saved;
  } catch { return null; }
}

function restore() {
  try {
    const text = localStorage.getItem(STORAGE_KEY);
    if (!text || text.length > 250000) return;
    const saved = JSON.parse(text);
    if (saved?.schemaVersion !== STORAGE_SCHEMA || saved?.modelVersion !== MODEL_VERSION) return;
    try { params = validateParameters(saved.settings?.parameters); } catch { params = { ...DEFAULT_PARAMETERS }; }
    if (Number.isInteger(saved.settings?.oscillations) && saved.settings.oscillations >= 1
      && saved.settings.oscillations <= 100) $('cycles').value = saved.settings.oscillations;
    if (typeof saved.settings?.compareLinear === 'boolean') $('compare-linear').checked = saved.settings.compareLinear;
    if (Object.hasOwn(SOURCE_LABELS, saved.settings?.fitSource)) $('fit-source').value = saved.settings.fitSource;
    if (Array.isArray(saved.records)) records = saved.records.slice(0, MAX_RECORDS).map(checkedStoredRecord).filter(Boolean);
  } catch { storageAvailable = false; }
}

function settings() {
  return { parameters: { ...params }, oscillations: Number($('cycles').value),
    compareLinear: $('compare-linear').checked, fitSource: currentSource() };
}

function persist() {
  if (!storageAvailable) return;
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ schemaVersion: STORAGE_SCHEMA,
      modelVersion: MODEL_VERSION, settings: settings(), records }));
  } catch {
    storageAvailable = false;
    say('浏览器本地保存不可用；当前记录仍可导出为 CSV 或 JSON。');
  }
}

function syncControls() {
  $('length').value = params.length;
  $('angle').value = params.angleDeg;
  $('gravity').value = params.gravity;
  $('length-value').textContent = `${params.length.toFixed(2)} m`;
  $('angle-value').textContent = `${params.angleDeg}°`;
  syncRecordButton();
}

function syncRecordButton() {
  const count = Number($('cycles').value);
  $('record').textContent = Number.isInteger(count) && count >= 1 && count <= 100
    ? `记录 ${count} 个周期` : '记录周期';
}

function updateSummary() {
  const period = exactPeriod(params);
  const base = smallAnglePeriod(params);
  const ratio = period / base;
  const entries = [
    ['非线性周期 T', `${period.toFixed(6)} s`],
    ['小角度周期 T₀', `${base.toFixed(6)} s`],
    ['周期增量', `${(100 * (ratio - 1)).toFixed(3)}%`],
    ['小角度公式的 g 偏差', `${(100 * (ratio ** -2 - 1)).toFixed(3)}%`],
  ];
  $('summary').replaceChildren(...entries.map(([label, value]) => {
    const block = element('div', undefined, 'metric');
    block.append(element('span', label, 'metric-label'), element('strong', value, 'metric-value'));
    return block;
  }));
}

function refreshPlots() {
  updateApparatus = renderPendulum($('pendulum'), params);
  const duration = Math.min(30, Math.max(8, 4 * exactPeriod(params)));
  trajectory = simulate(params, { duration, dt: DT });
  updateCursor = renderTrajectory($('trajectory'), trajectory, $('compare-linear').checked);
  renderScan($('scan-chart'), params);
  updateSummary();
  drawFrame();
}

function drawFrame() {
  updateApparatus(state, $('compare-linear').checked);
  updateCursor(state.t);
  $('clock').textContent = state.t.toFixed(2);
  $('play').disabled = state.t >= MAX_TIME;
  updateTimer();
}

function pause(message) {
  running = false;
  if (frameId !== null) cancelAnimationFrame(frameId);
  frameId = null; lastWallTime = null; accumulator = 0;
  $('play').textContent = '开始';
  $('play').setAttribute('aria-pressed', 'false');
  if (message) say(message);
}

function animate(timestamp) {
  if (!running) return;
  if (lastWallTime !== null) accumulator += Math.min((timestamp - lastWallTime) / 1000, 0.1);
  lastWallTime = timestamp;
  while (accumulator >= DT && state.t < MAX_TIME) {
    state = rk4Step(state, Math.min(DT, MAX_TIME - state.t), params);
    accumulator -= DT;
  }
  if (state.t >= MAX_TIME - 1e-10) {
    state.t = MAX_TIME;
    if (timer && timer.endTime === null) {
      timer.endTime = MAX_TIME;
      timer.interrupted = true;
      $('timer-status').textContent = '本轮已到 60 s，计时已中断。请复位后重新计时，选择能够在 60 s 内完成的周期数。';
    }
    pause('仿真已运行 60 s，请复位后继续实验。');
  }
  drawFrame();
  if (running) frameId = requestAnimationFrame(animate);
}

function start() {
  if (state.t >= MAX_TIME) {
    say('当前仿真已达到 60 s，请先复位。'); return;
  }
  running = true; lastWallTime = null;
  $('play').textContent = '暂停';
  $('play').setAttribute('aria-pressed', 'true');
  say('运动进行中；秒表使用仿真时间。');
  frameId = requestAnimationFrame(animate);
}

function cancelTimer(message = '点击开始计时，在同向经过标记位置时开始并结束计时。') {
  timer = null;
  $('timer-status').textContent = message;
  updateTimer();
}

function updateTimer() {
  const elapsed = timer ? (timer.endTime ?? state.t) - timer.startTime : 0;
  $('timer-value').textContent = `${Math.max(0, elapsed).toFixed(3)} s`;
  $('timer-start').disabled = state.t >= MAX_TIME || Boolean(timer && timer.endTime === null);
  $('timer-stop').disabled = !timer || timer.endTime !== null;
  $('timer-record').disabled = !timer || timer.endTime === null || elapsed <= 0 || timer.saved || timer.interrupted;
}

function restart(message) {
  pause(); state = initialState(); cancelTimer(); drawFrame(); say(message);
}

function updateParameters(next) {
  try {
    params = validateParameters(next);
  } catch {
    say('请填写范围内的数值：摆长 0.20–1.20 m，初始摆角 1–60°，重力加速度 1–20 m/s²。');
    syncControls(); return;
  }
  gravityRejected = false;
  pause(); state = initialState();
  cancelTimer('参数已更新，秒表已复位。请在当前条件下重新计时。');
  syncControls(); refreshPlots(); renderRecords(); persist();
  say('参数已更新。运动从静止释放，已有记录按原条件保留。');
}

/** Commit completed numeric editing before any calculation or new timing. */
function commitGravityInput(forAction = false) {
  const field = $('gravity');
  if (forAction && gravityRejected && Number(field.value) === params.gravity) {
    gravityRejected = false;
    say('刚才的重力输入超出范围，已恢复当前参数。请核对后再次操作。');
    return false;
  }
  let checked;
  try {
    if (field.value.trim() === '') throw new RangeError('Empty gravity');
    checked = validateParameters({ ...params, gravity: Number(field.value) });
  } catch {
    field.value = params.gravity;
    gravityRejected = true;
    say('重力加速度请填写 1–20 m/s² 的有效数值，输入框已恢复当前参数。');
    return false;
  }
  if (checked.gravity !== params.gravity) updateParameters(checked);
  return true;
}

function selectedRecords() {
  return records.filter(row => row.source === currentSource()
    && row.gravity === params.gravity && row.angleDeg === params.angleDeg);
}

function renderRecords() {
  const fragment = document.createDocumentFragment();
  if (!records.length) {
    const tr = element('tr'); const td = element('td', '尚无虚拟记录。选择摆长后记录计时，再改变摆长重复测量。');
    td.colSpan = 8; td.className = 'empty-state'; tr.append(td); fragment.append(tr);
  }
  records.forEach((row, index) => {
    const tr = element('tr');
    const active = row.source === currentSource() && row.gravity === params.gravity && row.angleDeg === params.angleDeg;
    tr.classList.toggle('record-selected', active);
    const columns = [row.source === 'ideal-model' ? '自动' : '手动', row.length.toFixed(2), row.angleDeg,
      format(row.gravity, 9), row.oscillations, row.elapsed.toFixed(6), row.period.toFixed(6)];
    columns.forEach(value => tr.append(element('td', String(value))));
    tr.firstElementChild.title = SOURCE_LABELS[row.source];
    const action = element('td');
    const remove = element('button', '移除', 'text-button');
    remove.type = 'button'; remove.setAttribute('aria-label', `移除第 ${index + 1} 条虚拟记录`);
    remove.addEventListener('click', () => {
      records = records.filter(candidate => candidate.id !== row.id);
      renderRecords(); persist(); say('已移除所选虚拟记录。');
    });
    action.append(remove); tr.append(action); fragment.append(tr);
  });
  $('records').replaceChildren(fragment);
  $('record-count').textContent = String(records.length);
  const selected = selectedRecords();
  let fit = null;
  let message;
  const context = `${SOURCE_LABELS[currentSource()]}；g = ${format(params.gravity, 9)} m/s²，θ₀ = ${params.angleDeg}°。`;
  if (selected.length < 3) {
    message = `${context}当前有 ${selected.length} 条符合条件的记录；至少记录 3 条、包含不同摆长后进行拟合。`;
  } else if (new Set(selected.map(row => row.length)).size < 2) {
    message = `${context}请改变摆长补充记录，才能确定 T² 对 L 的斜率。`;
  } else {
    try {
      fit = fitMeasurements(selected);
      const interceptText = format(Math.abs(fit.intercept));
      const interceptSign = interceptText === '0' ? '+' : fit.intercept < 0 ? '−' : '+';
      message = `${context}T² = ${format(fit.slope)} L ${interceptSign} ${interceptText}；`
        + `斜率单位 s²/m，截距单位 s²。小角度公式估计 g = ${format(fit.gravity, 8)} m/s²，`
        + `回归标准误 ${format(fit.gravitySE, 4)} m/s²，R² = ${format(fit.rSquared, 8)}。`
        + '标准误仅来自拟合残差；有限摆角会产生模型偏差。';
    } catch {
      message = `${context}当前数据未形成正斜率。请核对全振动次数，以及开始和结束计时所选的位置与方向。`;
    }
  }
  $('fit-result').textContent = message;
  renderFit($('fit-chart'), selected, fit);
  $('clear').disabled = !records.length;
  $('export-csv').disabled = !records.length;
  $('export-json').disabled = !records.length;
}

function appendRecord(row) {
  if (records.length >= MAX_RECORDS) {
    say('已保存 100 条记录。请先导出，再清空或移除部分记录。'); return false;
  }
  records.push({ ...row, id: nextRecordId++, createdAt: new Date().toISOString() });
  $('fit-source').value = row.source;
  renderRecords(); persist(); return true;
}

function download(filename, text, type) {
  const blob = new Blob([text], { type });
  const url = URL.createObjectURL(blob);
  const anchor = element('a');
  anchor.href = url; anchor.download = filename; anchor.hidden = true;
  document.body.append(anchor); anchor.click(); anchor.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function stamp() { return new Date().toISOString().replace(/[:.]/g, '-'); }

function csvCell(value) {
  const text = value === null || value === undefined ? '' : String(value);
  return /[",\r\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}

async function loadSourceObservations() {
  $('source-gravity').disabled = true;
  try {
    const response = await fetch(new URL('./observations.json', import.meta.url));
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    if (data.experiment_id !== 'course-01/pendulum' || !Array.isArray(data.raw?.measurements)
      || !Array.isArray(data.derived?.groups) || !Number.isFinite(data.derived?.fit?.gravity_m_s2)) {
      throw new Error('Invalid observation schema');
    }
    sourceData = data;
    const fragment = document.createDocumentFragment();
    for (const group of data.derived.groups) {
      const raw = data.raw.measurements.filter(row => row.run_id === group.run_id).sort((a, b) => a.repeat_id - b.repeat_id);
      const tr = element('tr');
      const columns = [group.run_id, group.effective_length_m.toFixed(4),
        ...raw.map(row => row.as_recorded.elapsed_time_s), group.period_s.toFixed(6), group.period_squared_s2.toFixed(6)];
      columns.forEach(value => tr.append(element('td', String(value)))); fragment.append(tr);
    }
    $('source-table').replaceChildren(fragment);
    const fit = data.derived.fit;
    $('source-fit').textContent = `源报告共有 6 组摆长，每组 3 次计时，每次 20 次全振动。平均球直径为 `
      + `${(data.derived.diameter.mean_m * 100).toFixed(3)} cm；有效摆长等于摆线长度加平均半径。`
      + `含截距拟合得到 g = ${fit.gravity_m_s2.toFixed(6)} m/s²，回归标准误为 `
      + `${fit.gravity_regression_standard_error_m_s2.toFixed(6)} m/s²。原始摆角及仪器误差限未记录，`
      + '该结果用于数据对照和模型情景，不作为当地重力的独立标定值。';
    $('source-gravity').disabled = false;
  } catch {
    $('source-fit').textContent = '源报告数据未能载入，请刷新页面重试。当前虚拟实验可以继续使用。';
    $('source-table').replaceChildren();
  }
}

restore(); syncControls(); state = initialState();
if (!$('cycles').value) $('cycles').value = '20';
$('play').type = 'button';
for (const id of ['reset', 'record', 'source-gravity', 'clear', 'export-csv', 'export-json', 'timer-start', 'timer-stop', 'timer-record']) $(id).type = 'button';

for (const [id, field] of [['length', 'length'], ['angle', 'angleDeg']]) {
  $(id).addEventListener('input', () => {
    const value = Number($(id).value);
    if (commitGravityInput(true)) updateParameters({ ...params, [field]: value });
    else $(id).value = params[field];
  });
}
$('gravity').addEventListener('input', () => {
  gravityRejected = false;
  if (running && ($('gravity').value.trim() === '' || Number($('gravity').value) !== params.gravity)) {
    pause('重力参数正在编辑，完成输入后可重新开始运动。');
  }
});
$('gravity').addEventListener('change', () => commitGravityInput());
$('gravity').addEventListener('blur', () => commitGravityInput());
$('cycles').addEventListener('change', () => {
  try {
    readCycles(); cancelTimer('全振动次数已更新，请重新开始计时。'); syncRecordButton(); persist();
  } catch (error) { $('cycles').value = 20; syncRecordButton(); cancelTimer(); say(error.message); }
});
$('cycles').addEventListener('input', syncRecordButton);
$('play').addEventListener('click', () => {
  if (running) pause('运动已暂停；仿真时间和秒表同步暂停。');
  else if (commitGravityInput(true)) start();
});
$('reset').addEventListener('click', () => {
  if (commitGravityInput(true)) restart('运动与秒表已复位，参数和已保存记录保持不变。');
});
$('compare-linear').addEventListener('change', () => {
  updateCursor = renderTrajectory($('trajectory'), trajectory, $('compare-linear').checked);
  drawFrame(); persist();
});
$('record').addEventListener('click', () => {
  try {
    if (!commitGravityInput(true)) return;
    const row = autoMeasurement(params, { oscillations: readCycles() });
    if (appendRecord(row)) say(`已记录理想模型 ${row.oscillations} 次全振动的精确时长。改变摆长可以继续记录。`);
  } catch (error) { say(error.message); }
});
$('source-gravity').addEventListener('click', () => {
  if (sourceData) {
    updateParameters({ ...params, gravity: sourceData.derived.fit.gravity_m_s2 });
    say('当前重力参数采用源报告拟合值，作为仿真情景。');
  }
});
$('timer-start').addEventListener('click', () => {
  try {
    if (!commitGravityInput(true)) return;
    if (state.t >= MAX_TIME) { say('请先复位运动，再开始新的手动计时。'); return; }
    timer = { parameters: { ...params }, oscillations: readCycles(), startTime: state.t, endTime: null, saved: false };
    $('timer-status').textContent = `秒表已开始，目标为 ${timer.oscillations} 次全振动；在同一位置、同一方向经过时停止。`
      + (running ? '' : '点击运动的“开始”按钮推进仿真时间。')
      + (timer.oscillations * exactPeriod(params) > MAX_TIME - state.t
        ? `本轮剩余 ${(MAX_TIME - state.t).toFixed(1)} s，少于目标周期总时长。可减小 N 并重新计时。` : '');
    updateTimer();
  } catch (error) { say(error.message); }
});
$('timer-stop').addEventListener('click', () => {
  if (!timer || timer.endTime !== null) return;
  timer.endTime = state.t;
  $('timer-status').textContent = timer.endTime > timer.startTime
    ? '秒表已停止。确认全振动次数后，将这次手动计时加入记录。'
    : '本次计时时间为零，请启动运动后重新计时。';
  updateTimer();
});
$('timer-record').addEventListener('click', () => {
  if (!commitGravityInput(true)) return;
  if (!timer || timer.endTime === null || timer.saved || timer.interrupted || timer.endTime <= timer.startTime) return;
  const elapsed = timer.endTime - timer.startTime;
  if (appendRecord({ ...timer.parameters, oscillations: timer.oscillations, elapsed,
    period: elapsed / timer.oscillations, source: 'manual-timing', startTime: timer.startTime, endTime: timer.endTime })) {
    timer.saved = true; updateTimer();
    $('timer-status').textContent = '本次手动计时已记录，可在“手动计时”分组中拟合或导出。';
    say('已添加手动计时记录。拟合只使用同一重力、初始角度及所选计时来源的记录。');
  }
});
$('fit-source').addEventListener('change', () => { renderRecords(); persist(); });
$('clear').addEventListener('click', () => {
  records = []; renderRecords(); persist(); say('虚拟实验记录已清空。');
});
$('export-csv').addEventListener('click', () => {
  const columns = ['source', 'length_m', 'gravity_m_s2', 'initial_angle_deg', 'oscillations',
    'elapsed_time_s', 'period_s', 'period_squared_s2', 'timer_start_s', 'timer_end_s', 'created_at', 'model_version'];
  const rows = records.map(row => [row.source, row.length, row.gravity, row.angleDeg, row.oscillations,
    row.elapsed, row.period, row.period ** 2, row.startTime, row.endTime, row.createdAt, MODEL_VERSION]);
  download(`pendulum-records-${stamp()}.csv`, '\uFEFF' + [columns, ...rows].map(row => row.map(csvCell).join(',')).join('\r\n'), 'text/csv;charset=utf-8');
  say('已导出完整精度 CSV，来源和每条记录的模型参数保留在独立列中。');
});
$('export-json').addEventListener('click', () => {
  const payload = { schemaVersion: STORAGE_SCHEMA, modelVersion: MODEL_VERSION,
    experimentId: 'course-01/pendulum', exportedAt: new Date().toISOString(), settings: settings(),
    model: { equation: 'theta_ddot = -(g/L) sin(theta)', initialAngularVelocity: 0,
      integrator: 'RK4', integrationStep_s: DT, periodMethod: 'complete elliptic integral via AGM',
      assumptions: ['point mass', 'massless inextensible string', 'fixed pivot', 'uniform gravity', 'no damping or drive'],
      randomNoise: null },
    units: { length: 'm', gravity: 'm/s^2', angleDeg: 'degree', elapsed: 's', period: 's' },
    dataIdentity: { 'ideal-model': 'N times the exact ideal-model period',
      'manual-timing': 'User-selected start and stop in simulation time' },
    records };
  download(`pendulum-records-${stamp()}.json`, JSON.stringify(payload, null, 2) + '\n', 'application/json');
  say('已导出 JSON，包含模型版本、假设、参数与完整精度记录。');
});
document.addEventListener('visibilitychange', () => {
  if (document.hidden && running) { pause('页面切换后运动已暂停，返回时可以继续。'); drawFrame(); }
});

refreshPlots(); renderRecords(); cancelTimer();
say(records.length ? `已恢复 ${records.length} 条本地虚拟实验记录。` : '设置摆长与初始摆角，开始观察运动或记录计时。');
void loadSourceObservations();
