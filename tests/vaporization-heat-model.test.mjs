import test from'node:test';import assert from'node:assert/strict';import{DEFAULT_PARAMETERS as P,properties,inferLatent,idealReadings,measurement,validateParameters}from'../simulations/vaporization-heat/model.mjs';const near=(a,b,t=1e-10)=>assert.ok(Math.abs(a-b)/Math.max(1,Math.abs(b))<t);
test('latent sensible absorbed balance',()=>{const q=properties(P);near(q.latent+q.sensible-q.heatLoss,q.absorbed);});
test('ideal calorimetry inverse recovers latent heat',()=>near(inferLatent(P,idealReadings(P)).latentHeat,P.latentHeat));
test('wet steam and heat loss reduce apparent latent heat',()=>{const p={...P,moistureFraction:.1,heatLossFraction:.05};near(inferLatent(p,idealReadings(p)).latentHeat,p.latentHeat*.85);});
test('weighing inventory must match assumption',()=>{const raw=idealReadings(P,true);near(inferLatent(P,raw,true).latentHeat,P.latentHeat);assert.ok(inferLatent(P,raw).latentHeat<P.latentHeat);});
test('more cold water reduces final temperature',()=>assert.ok(properties({...P,waterMass:.2}).finalTemperature<properties(P).finalTemperature));
test('invalid boiling state or readings rejected',()=>{assert.throws(()=>validateParameters({...P,steamMass:.015,waterMass:.08,initialTemperature:30,latentHeat:2.5e6}));assert.throws(()=>measurement(P,{initialMass:0,finalMass:0,initialVoltage:0,finalVoltage:0},'manual-readings'));});
