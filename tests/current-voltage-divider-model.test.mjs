import test from'node:test';import assert from'node:assert/strict';import{DEFAULTS,response,validateParameters}from'../simulations/current-voltage-divider/model.mjs';const close=(a,b)=>assert.ok(Math.abs(a-b)<1e-12);
test('loaded divider endpoints',()=>{close(response({...DEFAULTS,X:0}).voltage,0);close(response({...DEFAULTS,X:1}).voltage,5);});
test('loaded midpoint is below unloaded half voltage',()=>{assert.ok(response(DEFAULTS).voltage<2.5);close(response(DEFAULTS).voltage,2);});
test('series load limits and monotonic current',()=>{close(response({...DEFAULTS,mode:'current',X:0}).current,.005);assert.ok(response({...DEFAULTS,mode:'current',X:1}).current<response({...DEFAULTS,mode:'current',X:0}).current);});
test('invalid inputs rejected',()=>{assert.throws(()=>validateParameters({...DEFAULTS,K:0}));assert.throws(()=>response({...DEFAULTS,E:NaN}));});

import * as BoundaryModel from '../simulations/current-voltage-divider/model.mjs';import{readFileSync as readBoundaryConfig}from'node:fs';
test('all declared control boundaries produce finite physical plots',()=>{const c=JSON.parse(readBoundaryConfig(new URL('../simulations/current-voltage-divider/ui-config.json',import.meta.url),'utf8'));for(const f of c.controls){const values=f.type==='select'?f.options.map(x=>x.value):[f.min,f.max];for(const v of values){const p={...BoundaryModel.DEFAULTS,[f.key]:v};for(const plot of BoundaryModel.plots(p))for(const curve of plot.curves){assert.ok(curve.points.length>=2);assert.ok(curve.points.every(row=>row.every(Number.isFinite)));}}}});
