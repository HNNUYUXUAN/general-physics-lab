import test from'node:test';import assert from'node:assert/strict';import{DEFAULTS,forward,measurement,diffractionIntensity}from'../simulations/transmission-grating/model.mjs';
test('green reference wavelength recovered independently',()=>assert.ok(Math.abs(measurement(DEFAULTS).estimate-546.1)<1e-9));
test('interference central maximum and symmetry',()=>{assert.equal(diffractionIntensity(0,DEFAULTS),1);assert.ok(Math.abs(diffractionIntensity(10,DEFAULTS)-diffractionIntensity(-10,DEFAULTS))<1e-12);});
test('finite grating maximum includes single-slit envelope',()=>{const theta=forward(DEFAULTS).theta_deg,beta=Math.PI*DEFAULTS.open_fraction;assert.ok(Math.abs(diffractionIntensity(theta,DEFAULTS)-(Math.sin(beta)/beta)**2)<1e-12);});
test('unavailable order fails explicitly',()=>assert.throws(()=>forward({...DEFAULTS,spacing_um:1,wavelength_nm:700,order:3})));
test('one interference zero independently located',()=>{const sin=DEFAULTS.wavelength_nm/(DEFAULTS.slit_count*DEFAULTS.spacing_um*1e3);assert.ok(diffractionIntensity(Math.asin(sin)*180/Math.PI,DEFAULTS)<1e-25);});
test('opposed verniers cancel across negative positive angular positions',()=>assert.ok(Math.abs(measurement({...DEFAULTS,zero_deg:359.9,eccentricity_arcmin:10}).estimate-546.1)<1e-9));
