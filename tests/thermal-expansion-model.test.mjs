import test from'node:test';import assert from'node:assert/strict';import{DEFAULT_PARAMETERS as P,temperature,reading,sweep,fitRecords,validateParameters,measurement}from'../simulations/thermal-expansion/model.mjs';const near=(a,b,t=1e-12)=>assert.ok(Math.abs(a-b)<t);
test('lumped heating initial and asymptotic conditions',()=>{near(temperature(P,0),20);near(temperature(P,15),100-80/Math.E);assert.ok(Math.abs(temperature(P,300)-100)<1e-6);});
test('heating ODE derivative',()=>{const t=7,h=1e-4;near((temperature(P,t+h)-temperature(P,t-h))/(2*h),(P.targetTemperature-temperature(P,t))/P.timeConstant,1e-8);});
test('reference temperature zero extension',()=>near(reading(P,20).extension,0));
test('doubling length doubles extension',()=>near(reading({...P,length:.3},80).extension,2*reading(P,80).extension));
test('constant temperature offset and dial zero cancel slope',()=>{const p={...P,temperatureBias:2,dialOrigin:40e-6};near(fitRecords(sweep(p),'ideal-equilibrium').alpha,p.alpha);});
test('dial gain scales inferred expansion coefficient',()=>{const p={...P,dialGain:1.05};near(fitRecords(sweep(p),'ideal-equilibrium').alpha,1.05*p.alpha);});
test('invalid values and mixed geometry rejected',()=>{assert.throws(()=>validateParameters({...P,timeConstant:0}));assert.throws(()=>measurement(P,200,0,'manual-readings'));const a=sweep(P);a[0].parameters.length=.2;assert.throws(()=>fitRecords(a,'ideal-equilibrium'));});
