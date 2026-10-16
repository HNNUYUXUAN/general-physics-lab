export const normalize = value => String(value ?? '').normalize('NFKC').toLowerCase().trim();
export function validState(state, courses, topics) {
  return {q:String(state.q ?? '').slice(0,160),course:courses.includes(state.course)?state.course:'',
    topic:topics.includes(state.topic)?state.topic:'',group:state.group==='topic'?'topic':'course'};
}
export function matches(entry, state) {
  return (!state.course || entry.course===state.course) && (!state.topic || entry.topic===state.topic)
    && normalize(state.q).split(/\s+/u).filter(Boolean).every(token=>normalize(entry.search).includes(token));
}
export function stateURL(state, href) {
  const url=new URL(href);
  for(const key of ['q','course','topic','group']) {
    const value=key==='q'?state.q.trim():state[key];
    if(value && !(key==='group' && value==='course'))url.searchParams.set(key,value);else url.searchParams.delete(key);
  }
  return url;
}

export function initializeDirectory(root) {
  const page=root.querySelector('[data-directory]');if(!page)return;
  const settings=JSON.parse(page.querySelector('#directory-settings').textContent);
  const form=page.querySelector('form'),query=page.querySelector('#directory-query');
  const course=page.querySelector('#directory-course'),topic=page.querySelector('#directory-topic');
  const container=page.querySelector('#directory-groups'),status=page.querySelector('#directory-status');
  const empty=page.querySelector('.directory-empty'),expand=page.querySelector('#directory-expand');
  const cards=[...container.querySelectorAll('.experiment-entry')];
  const courses=settings.courses.map(g=>g.id),topics=settings.topics.map(g=>g.id);
  const stateFromURL=()=>validState(Object.fromEntries(new URL(location.href).searchParams),courses,topics);
  let state=stateFromURL();
  function sync() {
    query.value=state.q;course.value=state.course;topic.value=state.topic;
    for(const button of page.querySelectorAll('[data-view]'))button.setAttribute('aria-pressed',String(button.dataset.view===state.group));
  }
  function render(updateURL=true) {
    const selected=cards.filter(card=>matches(card.dataset,state));
    const groups=state.group==='topic'?settings.topics:settings.courses;
    const active=Boolean(state.q.trim()||state.course||state.topic);
    const previous=new Map([...container.querySelectorAll('details')].map(d=>[d.dataset.group,d.open]));
    container.replaceChildren();
    for(const group of groups) {
      const members=selected.filter(card=>card.dataset[state.group]===group.id);if(!members.length)continue;
      const detail=root.createElement('details');detail.className='directory-group';detail.dataset.group=group.id;
      detail.open=active||previous.get(group.id)===true;
      const summary=root.createElement('summary'),heading=root.createElement('span');heading.className='group-heading';
      for(const [className,text] of [['group-title',group.title],['group-description',group.description]]) {
        const span=root.createElement('span');span.className=className;span.textContent=text;heading.append(span);
      }
      const count=root.createElement('span');count.className='group-count';count.textContent=members.length+' 项';
      summary.append(heading,count);const grid=root.createElement('div');grid.className='directory-cards';grid.append(...members);
      detail.append(summary,grid);container.append(detail);
    }
    empty.hidden=selected.length!==0;container.hidden=selected.length===0;expand.hidden=selected.length===0;
    expand.textContent=[...container.querySelectorAll('details')].every(d=>d.open)?'收起全部':'展开全部';
    status.textContent='显示 '+selected.length+' / '+cards.length+' 项实验'+(active?'':'，展开目录进入实验')+'。';
    if(updateURL)history.replaceState(null,'',stateURL(state,location.href));
  }
  function reset() {
    state={q:'',course:'',topic:'',group:'course'};container.replaceChildren();sync();render();query.focus();
  }
  form.addEventListener('submit',e=>e.preventDefault());
  query.addEventListener('input',()=>{state.q=query.value;render();});
  course.addEventListener('change',()=>{state.course=course.value;render();});
  topic.addEventListener('change',()=>{state.topic=topic.value;render();});
  for(const button of page.querySelectorAll('[data-view]'))button.addEventListener('click',()=>{state.group=button.dataset.view;sync();render();});
  form.addEventListener('reset',e=>{e.preventDefault();reset();});page.querySelector('[data-clear]').addEventListener('click',reset);
  expand.addEventListener('click',()=>{const details=[...container.querySelectorAll('details')],open=details.some(d=>!d.open);for(const d of details)d.open=open;expand.textContent=open?'收起全部':'展开全部';});
  container.addEventListener('toggle',()=>{expand.textContent=[...container.querySelectorAll('details')].every(d=>d.open)?'收起全部':'展开全部';},true);
  window.addEventListener('popstate',()=>{state=stateFromURL();sync();render(false);});
  sync();render(false);form.hidden=false;
}
if(typeof document!=='undefined')initializeDirectory(document);
