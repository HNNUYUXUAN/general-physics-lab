import test from'node:test';import assert from'node:assert/strict';import{DEFAULTS,response}from'../simulations/multimeter/model.mjs';const close=(a,b)=>assert.ok(Math.abs(a-b)<1e-8);
test('ohm center and short limits',()=>{close(response(DEFAULTS).fraction,.5);close(response({...DEFAULTS,Rx:0}).fraction,1);close(response(DEFAULTS).indicatedResistance,1500);});
test('voltage loading and overrange',()=>{assert.ok(response(DEFAULTS).analogVoltage<1.5);assert.equal(response({...DEFAULTS,voltage:10}).overrange,true);});
test('battery zero adjustment restores short but shifts middle',()=>{close(response({...DEFAULTS,battery:1.2,zeroFactor:.8,Rx:0}).fraction,1);assert.notEqual(response({...DEFAULTS,battery:1.2,zeroFactor:.8}).indicatedResistance,1500);});
test('invalid settings rejected',()=>assert.throws(()=>response({...DEFAULTS,battery:0})));

import * as BoundaryModel from '../simulations/multimeter/model.mjs';import{readFileSync as readBoundaryConfig}from'node:fs';
test('all declared control boundaries produce finite physical plots',()=>{const c=JSON.parse(readBoundaryConfig(new URL('../simulations/multimeter/ui-config.json',import.meta.url),'utf8'));for(const f of c.controls){const values=f.type==='select'?f.options.map(x=>x.value):[f.min,f.max];for(const v of values){const p={...BoundaryModel.DEFAULTS,[f.key]:v};for(const plot of BoundaryModel.plots(p))for(const curve of plot.curves){assert.ok(curve.points.length>=2);assert.ok(curve.points.every(row=>row.every(Number.isFinite)));}}}});
