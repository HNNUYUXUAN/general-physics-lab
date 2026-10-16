import test from'node:test';import assert from'node:assert/strict';import{DEFAULT_PARAMETERS as P,properties,motion,timeAtDistance,fallInterval,inferViscosity,validateParameters}from'../simulations/liquid-viscosity/model.mjs';const near=(a,b,t=1e-12)=>assert.ok(Math.abs(a-b)<t);
test('initial rest and terminal limit',()=>{const q=properties(P);near(motion(P,0).position,0);near(motion(P,0).velocity,0);near(motion(P,40*q.tau).velocity,q.speed);});
test('force balance at terminal speed',()=>{const q=properties(P);near(3*Math.PI*P.viscosity*P.diameter*q.wall*q.speed,(P.sphereDensity-P.liquidDensity)*P.gravity*Math.PI*P.diameter**3/6);});
test('ODE derivative and distance inversion',()=>{const q=properties(P),t=.5*q.tau,h=q.tau*1e-5;near((motion(P,t+h).velocity-motion(P,t-h).velocity)/(2*h),(q.speed-motion(P,t).velocity)/q.tau,1e-7);for(const x of[0,.01,.2])near(motion(P,timeAtDistance(P,x)).position,x);});
test('terminal interval recovers viscosity',()=>near(inferViscosity(P,fallInterval(P)).viscosity,P.viscosity,1e-10));
test('counting acceleration interval gives positive bias',()=>assert.ok(inferViscosity({...P,entryDistance:0},fallInterval({...P,entryDistance:0})).viscosity>P.viscosity));
test('wall correction slows falling',()=>assert.ok(properties({...P,tubeDiameter:.04}).speed>properties(P).speed));
test('invalid or high Reynolds inputs rejected',()=>{assert.throws(()=>validateParameters({...P,viscosity:.2,diameter:.002}));assert.throws(()=>inferViscosity(P,0));});
