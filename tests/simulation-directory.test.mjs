import {test} from 'node:test';import assert from 'node:assert/strict';
import {matches,validState,stateURL} from '../site/assets/simulation-directory.mjs';
const entry={course:'course-03',topic:'circuits',search:'RLC 谐振 电容 capacitor amplitude phase 幅相 扫频'};
test('course, topic and multiple search tokens intersect',()=>{
 assert(matches(entry,{q:'ＲＬＣ 电容',course:'course-03',topic:'circuits'}));
 assert(matches(entry,{q:'CAPACITOR phase'}));
 assert(!matches(entry,{q:'RLC 重力'}));assert(!matches(entry,{q:'',course:'course-04'}));
});
test('empty and punctuation searches are literal',()=>{
 assert(matches(entry,{q:'  '}));assert(!matches(entry,{q:'[.*]'}));assert(!matches(entry,{q:'<script>'}));
});
test('shared URL round trips unicode and preserves the project path',()=>{
 const state={q:'干涉 & wave',course:'course-04',topic:'wave-optics',group:'topic'};
 const url=stateURL(state,'https://example.test/nested/general-physics-lab/simulations/');
 assert.equal(url.pathname,'/nested/general-physics-lab/simulations/');
 assert.deepEqual(validState(Object.fromEntries(url.searchParams),['course-04'],['wave-optics']),state);
 assert.equal(stateURL({q:'',course:'',topic:'',group:'course'},url).search,'');
});
test('unknown filters recover to available choices and bound query length',()=>{
 assert.deepEqual(validState({course:'bad',topic:'bad',group:'bad'},['course-03'],['circuits']),{q:'',course:'',topic:'',group:'course'});
 assert.equal(validState({q:'x'.repeat(200)},[],[]).q.length,160);
});
