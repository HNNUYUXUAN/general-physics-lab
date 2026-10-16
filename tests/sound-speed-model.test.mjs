import test from'node:test';import assert from'node:assert/strict';import{DEFAULT_PARAMETERS as P,transfer,featurePosition,nextFeature,sweep,fitRecords,validateParameters}from'../simulations/sound-speed/model.mjs';const near=(a,b,t=1e-10)=>assert.ok(Math.abs(a-b)<t);
test('standing maxima spaced half wavelength',()=>{const x=featurePosition(P,'standing',12),a=transfer({...P,position:x}),b=transfer({...P,position:x+P.soundSpeed/(2*P.frequency)});near(a.amplitude,1);near(b.amplitude,1);});
test('phase repeats at full wavelength',()=>{const a=transfer(P,'phase'),b=transfer({...P,position:P.position+P.soundSpeed/P.frequency},'phase');near(a.real,b.real);near(a.imag,b.imag);});
test('both position regressions recover speed',()=>{for(const mode of['standing','phase'])near(fitRecords(sweep(P,mode),mode,'ideal-model').speed,P.soundSpeed);});
test('scale factor biases speed and constant zero cancels',()=>{const p={...P,positionScale:1.02,positionOffset:.0005};near(fitRecords(sweep(p,'phase'),'phase','ideal-model').speed,P.soundSpeed*1.02);});
test('electronic phase cancels same-phase spacing',()=>{const p={...P,electronicPhase:1};near(fitRecords(sweep(p,'phase'),'phase','ideal-model').speed,P.soundSpeed);});
test('next feature and range rejection',()=>assert.ok(nextFeature(P,'standing').position>P.position));
test('invalid values and mixed conditions rejected',()=>{assert.throws(()=>validateParameters({...P,roundTrip:1}));const a=sweep(P,'phase');a[0].parameters.frequency=37000;assert.throws(()=>fitRecords(a,'phase','ideal-model'));});
