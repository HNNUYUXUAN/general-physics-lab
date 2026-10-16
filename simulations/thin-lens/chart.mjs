import{conjugates,bessel}from'./model.mjs';
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

export function rays(svg,p,method){reset(svg,'近轴薄透镜光路，实线表示光线，虚线表示反向延长线');const f=p.focalLength,D=f*p.screenRatio,u=method==='conjugates'?f*p.objectRatio:D*p.lensFraction,c=conjugates(f,u),maxX=method==='bessel'?D:Math.max(5*f,u+(c.v>0?Math.min(c.v,6*f):2*f)),x=v=>50+v/maxX*590,y=v=>170-v/.04*120;add(svg,'line',{x1:30,x2:665,y1:170,y2:170,stroke:'#bbb'});const defs=add(svg,'defs'),cp=add(defs,'clipPath',{id:'rayclip'});add(cp,'rect',{x:25,y:50,width:650,height:235});const g=add(svg,'g',{'clip-path':'url(#rayclip)'});const path=(pairs,dash=false)=>add(g,'path',{d:pairs.map(([xx,yy],i)=>`${i?'L':'M'}${x(xx)},${y(yy)}`).join(' '),stroke:dash?'#999':'#222',fill:'none','stroke-width':1.7,...(dash?{'stroke-dasharray':'5 5'}:{})});add(svg,'line',{x1:x(u),x2:x(u),y1:65,y2:278,stroke:'#222','stroke-width':2});add(svg,'text',{x:x(u),y:40,'text-anchor':'middle'},'薄透镜');path([[0,0],[0,p.height]]);add(svg,'text',{x:x(0),y:300,'text-anchor':'middle'},'物');const end=method==='bessel'?D:maxX;path([[0,p.height],[u,p.height],[end,p.height-(end-u)*p.height/f]]);path([[0,p.height],[u,0],[end,-(end-u)*p.height/u]]);if(c.v<0){path([[u,p.height],[u+c.v,c.magnification*p.height]],true);path([[u,0],[u+c.v,c.magnification*p.height]],true);}if(c.v!==null&&u+c.v>=0&&u+c.v<=maxX&&Math.abs(c.magnification*p.height)<.04){path([[u+c.v,0],[u+c.v,c.magnification*p.height]]);add(svg,'text',{x:x(u+c.v),y:300,'text-anchor':'middle'},c.type==='real'?'实像':'虚像');}if(method==='bessel'){add(svg,'line',{x1:x(D),x2:x(D),y1:75,y2:270,stroke:'#777','stroke-width':3});add(svg,'text',{x:x(D),y:40,'text-anchor':'middle'},'光屏');}for(const z of[u-f,u+f])if(z>0&&z<maxX){add(svg,'circle',{cx:x(z),cy:170,r:3,fill:'#222'});add(svg,'text',{x:x(z),y:195,'text-anchor':'middle'},'F');}add(svg,'text',{x:350,y:333,'text-anchor':'middle'},`横轴：物到光具座位置　　物高 ${(p.height*1000).toFixed(1)} mm`);}
export function conjugateChart(svg,p){const a=axes(svg,{xd:[1,4],yd:[0,12],xLabel:'物距比 u / f',yLabel:'像距比 v / f',title:'实像的共轭距离关系'});line(svg,Array.from({length:301},(_,i)=>{const q=1.1+2.9*i/300;return[q,Math.min(12,q/(q-1))];}),a);if(p.objectRatio>1.1)point(svg,p.objectRatio,p.objectRatio/(p.objectRatio-1),a);add(svg,'text',{x:a.left,y:20},'u/f → 1⁺ 时像距发散');}
export function besselChart(svg,p){const a=axes(svg,{xd:[3,8],yd:[0,8],xLabel:'物屏距离比 D / f',yLabel:'透镜位置比 u / f',title:'Bessel二次成像位置与临界条件'});for(const sign of[-1,1])line(svg,Array.from({length:201},(_,i)=>{const q=4+i/50;return[q,(q+sign*Math.sqrt(q*q-4*q))/2];}),a,sign>0?{'stroke-dasharray':'6 4'}:{});const b=bessel(1,p.screenRatio);b.positions.forEach(v=>point(svg,p.screenRatio,v,a));add(svg,'text',{x:a.left,y:20},'D/f < 4 无实成像位置');}
