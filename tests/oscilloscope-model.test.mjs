import test from'node:test';import assert from'node:assert/strict';import{DEFAULTS,response,wave}from'../simulations/oscilloscope/model.mjs';const close=(a,b)=>assert.ok(Math.abs(a-b)<1e-10);
test('default cursor readings match input',()=>{const r=response(DEFAULTS);close(r.measuredVpp,1);close(r.measuredFrequency,1000);close(r.trueRMS,1/Math.sqrt(8));});
test('waveform RMS factors',()=>{close(response({...DEFAULTS,waveform:'triangle'}).trueRMS,.5/Math.sqrt(3));close(response({...DEFAULTS,waveform:'square'}).trueRMS,.5);});
test('cursors independent of input',()=>{assert.notEqual(response({...DEFAULTS,x2:5}).measuredFrequency,1000);assert.equal(response({...DEFAULTS,x2:1}).measuredFrequency,null);});
test('screen clipping explicit',()=>assert.equal(response({...DEFAULTS,amplitude:2}).clipped,true));
test('periodic wave and invalid scale',()=>{close(wave('sine',0),0);close(wave('triangle',.25),1);assert.throws(()=>response({...DEFAULTS,voltsPerDiv:0}));});

import * as BoundaryModel from '../simulations/oscilloscope/model.mjs';import{readFileSync as readBoundaryConfig}from'node:fs';
test('all declared control boundaries produce finite physical plots',()=>{const c=JSON.parse(readBoundaryConfig(new URL('../simulations/oscilloscope/ui-config.json',import.meta.url),'utf8'));for(const f of c.controls){const values=f.type==='select'?f.options.map(x=>x.value):[f.min,f.max];for(const v of values){const p={...BoundaryModel.DEFAULTS,[f.key]:v};for(const plot of BoundaryModel.plots(p))for(const curve of plot.curves){assert.ok(curve.points.length>=2);assert.ok(curve.points.every(row=>row.every(Number.isFinite)));}}}});
