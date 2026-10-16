import test from'node:test';import assert from'node:assert/strict';import{DEFAULT_PARAMETERS as P,properties,inferSurface,calibrationSweep,calibrate,validateParameters,pullRecord}from'../simulations/surface-tension/model.mjs';const near=(a,b,t=1e-12)=>assert.ok(Math.abs(a-b)<t);
test('wetted ring force and inverse',()=>{const q=properties(P);near(q.surfaceForce,P.surfaceTension*Math.PI*(P.innerDiameter+P.outerDiameter));near(inferSurface(P,q.before,q.after,P.conversion),P.surfaceTension);});
test('inner and outer perimeters both included',()=>{const q=properties({...P,innerDiameter:P.innerDiameter*.8});assert.ok(q.surfaceForce<properties(P).surfaceForce);});
test('contact angle halves force at60degrees',()=>near(properties({...P,contactAngle:60}).surfaceForce,properties(P).surfaceForce/2));
test('film weight adds predictable apparent tension',()=>{const p={...P,filmMass:.0001},q=properties(p);near(inferSurface(p,q.before,q.after,p.conversion)-p.surfaceTension,p.filmMass*p.gravity/q.contactLength);});
test('sensor offset cancels and calibration recovers slope',()=>{const p={...P,baseline:100},q=properties(p);near(q.difference,properties(P).difference);near(calibrate(calibrationSweep(p),p,'ideal-model').slope,p.conversion);});
test('calibration rejects sensor mixture',()=>{const a=calibrationSweep(P);a[0].parameters.conversion=.0004;assert.throws(()=>calibrate(a,P,'ideal-model'));});
test('invalid geometry or voltage difference rejected',()=>{assert.throws(()=>validateParameters({...P,outerDiameter:.03}));assert.throws(()=>pullRecord(P,1,2,'ideal-model'));});
