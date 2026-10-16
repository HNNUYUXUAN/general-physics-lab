import test from'node:test';import assert from'node:assert/strict';import{DEFAULTS,response}from'../simulations/resistor-iv/model.mjs';const close=(a,b)=>assert.ok(Math.abs(a-b)<1e-9*Math.max(1,Math.abs(b)));
test('internal apparent resistance includes ammeter',()=>close(response(DEFAULTS).apparentResistance,1001));
test('external loading underestimates true resistance',()=>{const r=response({...DEFAULTS,mode:'external'});close(r.apparentResistance,1000e6/(1000+1e6));assert.ok(r.errorPercent<0);});
test('current scales with voltage',()=>close(response({...DEFAULTS,U:2}).current_mA,2*response(DEFAULTS).current_mA));
test('meter resistance controls error direction',()=>{assert.ok(response({...DEFAULTS,RA:100}).errorPercent>response(DEFAULTS).errorPercent);assert.throws(()=>response({...DEFAULTS,RV:0}));});

import * as BoundaryModel from '../simulations/resistor-iv/model.mjs';import{readFileSync as readBoundaryConfig}from'node:fs';
test('all declared control boundaries produce finite physical plots',()=>{const c=JSON.parse(readBoundaryConfig(new URL('../simulations/resistor-iv/ui-config.json',import.meta.url),'utf8'));for(const f of c.controls){const values=f.type==='select'?f.options.map(x=>x.value):[f.min,f.max];for(const v of values){const p={...BoundaryModel.DEFAULTS,[f.key]:v};for(const plot of BoundaryModel.plots(p))for(const curve of plot.curves){assert.ok(curve.points.length>=2);assert.ok(curve.points.every(row=>row.every(Number.isFinite)));}}}});
