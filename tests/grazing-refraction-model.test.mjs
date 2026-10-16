import test from'node:test';import assert from'node:assert/strict';import{DEFAULTS,forward,measurement,inverse}from'../simulations/grazing-refraction/model.mjs';
test('grazing two-face geometry inverts independent liquid index',()=>assert.ok(Math.abs(measurement(DEFAULTS).estimate-1.33)<1e-10));
test('bounded refractive domain always has exiting beam',()=>{for(const n of[1.25,1.33,1.45])for(const n1 of[1.5,1.5425,1.55]){const p={...DEFAULTS,liquid_index:n,prism_index:n1};assert.ok(forward(p).target_deg>0&&forward(p).target_deg<90);assert.ok(Math.abs(measurement(p).estimate-n)<1e-10);}});
test('larger liquid index gives smaller exit angle',()=>assert.ok(forward({...DEFAULTS,liquid_index:1.4}).target_deg<forward(DEFAULTS).target_deg));
test('invalid material region is rejected',()=>{assert.throws(()=>forward({...DEFAULTS,liquid_index:1.6}));assert.throws(()=>inverse(NaN,DEFAULTS));});
