const NS='http://www.w3.org/2000/svg';
function add(svg,name,attrs={},text){const e=document.createElementNS(NS,name);for(const[k,v]of Object.entries(attrs))e.setAttribute(k,v);if(text!==undefined)e.textContent=text;svg.append(e);return e;}
function reset(svg,title){svg.replaceChildren();add(svg,'title',{},title);svg.setAttribute('aria-label',title);svg.setAttribute('font-size','16');}
const fmt=n=>String(Number(n.toPrecision(4)));
function axes(svg,{xd,yd,xLabel,yLabel,title}){
 reset(svg,title);const left=window.matchMedia('(max-width:650px)').matches?135:82,right=window.matchMedia('(max-width:650px)').matches?506:536,top=35,bottom=262,x=v=>left+(v-xd[0])/(xd[1]-xd[0])*(right-left),y=v=>bottom-(v-yd[0])/(yd[1]-yd[0])*(bottom-top);
 for(let i=0;i<=4;i++){
 const xv=xd[0]+i/4*(xd[1]-xd[0]),yv=yd[0]+i/4*(yd[1]-yd[0]);
 add(svg,'line',{x1:left,x2:right,y1:y(yv),y2:y(yv),stroke:'#e6e6e6'});
 add(svg,'text',{x:left-10,y:y(yv)+5,'text-anchor':'end'},fmt(yv));
 add(svg,'text',{x:x(xv),y:bottom+24,'text-anchor':'middle'},fmt(xv));}
 add(svg,'path',{d:`M${left},${top}V${bottom}H${right}`,stroke:'#222',fill:'none','stroke-width':1.5});
 add(svg,'text',{x:(left+right)/2,y:310,'text-anchor':'middle'},xLabel);
 add(svg,'text',{x:22,y:148,transform:'rotate(-90 22 148)','text-anchor':'middle'},yLabel);
 return{x,y,left,right,top,bottom};
}
function line(svg,points,a,style={}){add(svg,'path',{d:points.map(([x,y],i)=>`${i?'L':'M'}${a.x(x)},${a.y(y)}`).join(' '),stroke:'#222',fill:'none','stroke-width':1.8,...style});}
function point(svg,x,y,a,fill='white'){add(svg,'circle',{cx:a.x(x),cy:a.y(y),r:4,fill,stroke:'#222','stroke-width':1.7});}

export function renderPlot(svg,p){const points=p.curves.flatMap(c=>c.points),xs=points.map(x=>x[0]),ys=points.map(x=>x[1]);let lo=Math.min(...ys),hi=Math.max(...ys);if(p.yd){[lo,hi]=p.yd;}else{const pad=Math.max(1e-9,(hi-lo)*.1);lo-=pad;hi+=pad;}const a=axes(svg,{xd:p.xd||[Math.min(...xs),Math.max(...xs)],yd:[lo,hi],xLabel:p.xLabel,yLabel:p.yLabel,title:p.caption});p.curves.forEach((c,i)=>{line(svg,c.points,a,i?{stroke:'#777','stroke-dasharray':'6 4'}:{});if(c.markers)c.points.forEach(([x,y])=>point(svg,x,y,a));});if(p.selected)point(svg,p.selected[0],p.selected[1],a,'#222');add(svg,'text',{x:a.left,y:20,'font-size':15},p.legend||'实线：理想模型');}
