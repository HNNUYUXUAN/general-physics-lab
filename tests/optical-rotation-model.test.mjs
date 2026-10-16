import test from'node:test';import assert from'node:assert/strict';import{DEFAULTS,rotation,halfField,measurement,difference180}from'../simulations/optical-rotation/model.mjs';
test('conditional concentration independently set and recovered',()=>{assert.ok(Math.abs(rotation(DEFAULTS)-13.292)<1e-10);assert.ok(Math.abs(measurement(DEFAULTS).concentration_g_ml-.1)<1e-10);});
test('blank and sample dim equal field',()=>{for(const[angle,blank]of[[90,true],[103.292,false]]){const f=halfField(angle,DEFAULTS,blank);assert.ok(Math.abs(f.left-f.right)<1e-12);assert.ok(f.left<.01);}});
test('bright equal field is a distinct branch',()=>{const f=halfField(rotation(DEFAULTS),DEFAULTS);assert.ok(Math.abs(f.left-f.right)<1e-12);assert.ok(f.left>.99);});
test('period180 and ambiguity',()=>{assert.ok(Math.abs(difference180(2,178)-4)<1e-10);assert.throws(()=>difference180(90,0));});
test('missing manual angles and invalid material parameters fail',()=>{assert.throws(()=>measurement(DEFAULTS,'manual-equal-field'));assert.throws(()=>rotation({...DEFAULTS,tube_length_dm:0}));});
