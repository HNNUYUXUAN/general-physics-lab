import test from'node:test';import assert from'node:assert/strict';import{DEFAULTS,optics,measurement,calibrationScale}from'../simulations/optical-magnification/model.mjs';const close=(a,b)=>assert.ok(Math.abs(a-b)<1e-10);
test('thin lens known geometry and calibrated scale',()=>{const o=optics(DEFAULTS);close(o.object_distance_mm,12);close(o.image_distance_mm,60);close(o.magnification,5);close(o.scale_mm_div,.02);});
test('independent calibration precedes wire inference',()=>{const cal=measurement('calibration',DEFAULTS),scale=calibrationScale([cal],DEFAULTS,'ideal-model'),wire=measurement('wire',DEFAULTS,'ideal-model',null,null,scale);close(wire.diameter_mm,.05);assert.throws(()=>measurement('wire',DEFAULTS));});
test('optical change requires new calibration',()=>{const cal=measurement('calibration',DEFAULTS);assert.throws(()=>calibrationScale([cal],{...DEFAULTS,object_ratio:1.3},'ideal-model'));});
test('manual and ideal calibration cannot silently mix',()=>{const cal=measurement('calibration',DEFAULTS);assert.throws(()=>calibrationScale([cal],DEFAULTS,'manual-reticle'));});
test('afocal telescope inverted angular magnification',()=>close(optics(DEFAULTS).telescope_magnification,-5));
test('invalid focus region and reversed edges fail',()=>{assert.throws(()=>optics({...DEFAULTS,object_ratio:1}));assert.throws(()=>measurement('calibration',DEFAULTS,'manual-reticle',5,1));});
