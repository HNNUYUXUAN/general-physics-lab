import test from'node:test';import assert from'node:assert/strict';import{DEFAULTS,forward,measurement,readVerniers}from'../simulations/prism-apex/model.mjs';
test('two reflected directions give twice the apex',()=>{assert.equal(forward(DEFAULTS).target_deg,120);assert.ok(Math.abs(measurement(DEFAULTS).estimate-60)<1e-10);});
test('opposed verniers cancel error before dividing by two',()=>{for(const zero of[0,179.9,359.9])for(const ecc of[0,10])assert.ok(Math.abs(measurement({...DEFAULTS,zero_deg:zero,eccentricity_arcmin:ecc}).estimate-60)<1e-10);});
test('manual readings recover actual telescope separation divided by two',()=>{const r=measurement(DEFAULTS,'manual-telescope',readVerniers(20,DEFAULTS),readVerniers(140,DEFAULTS));assert.ok(Math.abs(r.estimate-60)<1e-10);});
test('invalid apex and missing manual readings fail',()=>{assert.throws(()=>measurement({...DEFAULTS,apex_deg:90}));assert.throws(()=>measurement(DEFAULTS,'manual-telescope'));});
