/** Linear steady-state series RLC. All voltages are RMS; R is total series loss. */
export const MODEL_VERSION='1.0.0';
export const EXPERIMENT_ID='course-03/rlc-resonance';
export const DEFAULTS=Object.freeze({inductance:0.1,capacitance:0.2e-6,resistance:88.38834764831844,sourceVoltage:1});
export function validateParameters(p){
 for(const [key,lo,hi] of [['inductance',.05,.2],['capacitance',.1e-6,.2e-6],['resistance',20,400],['sourceVoltage',.1,5]])
  if(!Number.isFinite(p[key])||p[key]<lo||p[key]>hi) throw new RangeError(`${key} out of range`);
 return {...p};
}
export function characteristics(parameters){
 const p=validateParameters(parameters),{inductance:L,capacitance:C,resistance:R}=p;
 const omega0=1/Math.sqrt(L*C), delta=R/L, root=Math.hypot(delta,2*omega0);
 const low=2*omega0*omega0/(root+delta)/(2*Math.PI),high=(root+delta)/(4*Math.PI);
 return {f0:omega0/(2*Math.PI),quality:omega0*L/R,bandwidth:delta/(2*Math.PI),low,high,halfVoltage:p.sourceVoltage/Math.sqrt(2)};
}
export function response(parameters,frequency){
 const p=validateParameters(parameters);
 if(!Number.isFinite(frequency)||frequency<=0) throw new RangeError('frequency must be positive');
 const w=2*Math.PI*frequency,x=w*p.inductance-1/(w*p.capacitance),z=Math.hypot(p.resistance,x),current=p.sourceVoltage/z;
 return {frequency,current,voltageR:current*p.resistance,voltageL:current*w*p.inductance,voltageC:current/(w*p.capacitance),phase:-Math.atan2(x,p.resistance),normalized:p.resistance/z,power:current*current*p.resistance,reactance:x};
}
export function sweep(parameters,count=601){
 if(!Number.isInteger(count)||count<3||count>10001) throw new RangeError('invalid sample count');
 const {f0}=characteristics(parameters);
 return Array.from({length:count},(_,i)=>response(parameters,f0*(.2+2.3*i/(count-1))));
}
export function inferHalfPower(rows){
 const selected=['low','peak','high'].map(role=>rows.filter(r=>r.role===role).at(-1));
 if(selected.some(r=>!r)) return null;
 const [low,peak,high]=selected;
 if(!selected.every(r=>r.group===peak.group&&r.source===peak.source)) throw new RangeError('incompatible parameter or source groups');
 if(!(low.frequency<peak.frequency&&peak.frequency<high.frequency)) throw new RangeError('half-power order invalid');
 const bandwidth=high.frequency-low.frequency,f0=Math.sqrt(low.frequency*high.frequency);
 const lowRatio=low.voltageR/peak.voltageR,highRatio=high.voltageR/peak.voltageR,peakRatio=peak.voltageR/peak.parameters.sourceVoltage;
 return {f0,peakFrequency:peak.frequency,bandwidth,quality:f0/bandwidth,lowRatio,highRatio,peakRatio,lowConditionResidual:lowRatio-Math.SQRT1_2,highConditionResidual:highRatio-Math.SQRT1_2,peakConditionResidual:peakRatio-1};
}
export function parameterKey(p){validateParameters(p);return [p.inductance,p.capacitance,p.resistance,p.sourceVoltage].join('|');}
/** Parameter edits invalidate prior automatic localization; repeated reads do not. */
export function selectionAfterParameterChange(previous,next,selection){return parameterKey(previous)===parameterKey(next)?{...selection}:{source:'user-frequency-selection',role:'sample'};}
export function makeRecord(p,frequency,role='sample',source='automatic-steady-state-model'){
 if(!['sample','low','peak','high'].includes(role)) throw new RangeError('invalid record role');
 if(!['automatic-steady-state-model','user-frequency-selection'].includes(source))throw new RangeError('invalid source');
 return {experimentId:EXPERIMENT_ID,modelVersion:MODEL_VERSION,source,role,group:parameterKey(p),parameters:{...p},units:{frequency:'Hz',voltageR:'V',current:'A',phase:'rad'},...response(p,frequency)};
}
/** Linear interpolation of independently observed voltages; no model-generated samples inserted. */
export function observedHalfPower(rows){
 if(rows.length<3||rows.some((r,i)=>!Number.isFinite(r.frequency)||!Number.isFinite(r.voltage)||r.voltage<=0||(i&&r.frequency<=rows[i-1].frequency))) throw new RangeError('invalid observations');
 const peak=rows.reduce((a,b)=>b.voltage>a.voltage?b:a),k=rows.indexOf(peak),level=peak.voltage/Math.sqrt(2);
 const cross=(a,b)=>a.frequency+(level-a.voltage)*(b.frequency-a.frequency)/(b.voltage-a.voltage);
 let low=null,high=null;
 for(let i=k-1;i>=0;i--) if(rows[i].voltage<=level&&rows[i+1].voltage>=level){low=cross(rows[i],rows[i+1]);break;}
 for(let i=k;i<rows.length-1;i++) if(rows[i].voltage>=level&&rows[i+1].voltage<=level){high=cross(rows[i],rows[i+1]);break;}
 if(low===null||high===null) return null;
 return {peakFrequency:peak.frequency,peakVoltage:peak.voltage,low,high,bandwidth:high-low,quality:peak.frequency/(high-low)};
}
