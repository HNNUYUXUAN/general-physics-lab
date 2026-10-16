import test from'node:test';import assert from'node:assert/strict';import{DEFAULTS,minimum,deviationAt,measurement,forward}from'../simulations/prism-refractive-index/model.mjs';
test('symmetric minimum recovers independently set refractive index',()=>{assert.ok(Math.abs(measurement(DEFAULTS).estimate-1.5)<1e-10);});
test('minimum increases on both sides of optimum',()=>{const m=minimum(DEFAULTS);assert.ok(deviationAt(m.incidence_deg-2,DEFAULTS)>m.deviation_deg);assert.ok(deviationAt(m.incidence_deg+2,DEFAULTS)>m.deviation_deg);});
test('non-minimum apparent index is not silently calibrated',()=>{const r=measurement({...DEFAULTS,incidence_deg:60});assert.equal(r.at_minimum,false);assert.ok(r.estimate>1.5);});
test('total internal reflection returns an explicit failure',()=>{assert.throws(()=>forward({...DEFAULTS,incidence_deg:0}));});
test('symmetric min exists throughout bounded material domain',()=>{for(const A of[40,60,70])for(const n of[1.3,1.5,1.7]){const p={...DEFAULTS,apex_deg:A,refractive_index:n};p.incidence_deg=minimum(p).incidence_deg;assert.ok(Math.abs(measurement(p).estimate-n)<1e-10);}});
