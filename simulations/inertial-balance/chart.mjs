import {state,period} from './model.mjs';
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

export function renderApparatus(svg,p){
 const small=window.matchMedia('(max-width:650px)').matches;
 const q=small?{w:400,h:300,wall:28,ground:370,base:205,block:195,bw:115,bh:80,by:105,cy:145,scale:3500,ky:65,kx:125,ly:35,lx:240,sy:270,fs:18}:{w:700,h:340,wall:70,ground:630,base:260,block:350,bw:130,bh:95,by:120,cy:165,scale:6000,ky:85,kx:210,ly:95,lx:500,sy:310,fs:16};
 svg.setAttribute('viewBox','0 0 '+q.w+' '+q.h);reset(svg,'水平惯性秤等效装置，质块由线性弹性部件连接固定端');svg.setAttribute('font-size',q.fs);
 add(svg,'rect',{x:q.wall,y:75,width:20,height:q.base-75,fill:'#ddd',stroke:'#222'});add(svg,'line',{x1:q.wall,x2:q.ground,y1:q.base,y2:q.base,stroke:'#aaa'});
 const spring=add(svg,'path',{stroke:'#222',fill:'none','stroke-width':2}),block=add(svg,'rect',{x:q.block,y:q.by,width:q.bw,height:q.bh,fill:'white',stroke:'#222','stroke-width':2});
 const text=add(svg,'text',{x:q.block+q.bw/2,y:q.cy+5,'text-anchor':'middle'},'m = '+(p.mass*1000).toFixed(0)+' g');const label=add(svg,'text',{x:q.w/2,y:q.sy,'text-anchor':'middle'},'');
 add(svg,'text',{x:q.kx,y:q.ky,'text-anchor':'middle'},'k = '+p.stiffness.toFixed(4)+' N/m');add(svg,'text',{x:q.lx,y:q.ly,'text-anchor':'middle'},small?'附加质量与空载等效质量':'附加质量与空载等效质量');
 return st=>{const dx=st.x*q.scale;block.setAttribute('x',q.block+dx);text.setAttribute('x',q.block+q.bw/2+dx);const stop=q.block+dx,start=q.wall+20,step=(stop-start)/12;spring.setAttribute('d','M'+start+','+q.cy+' '+Array.from({length:13},(_,i)=>'L'+(start+i*step)+','+(i===0||i===12?q.cy:q.cy+(i%2?14:-14))).join(' '));label.textContent='x = '+(st.x*1000).toFixed(3)+' mm    v = '+(st.velocity*1000).toFixed(3)+' mm/s';};
}
export function renderMotion(svg,p){const T=period(p),a=axes(svg,{xd:[0,4*T],yd:[-p.amplitude*1100,p.amplitude*1100],xLabel:'时间 t / s',yLabel:'位移 x / mm',title:'理想惯性秤的四周期振动'});line(svg,Array.from({length:501},(_,i)=>{const t=4*T*i/500;return[t,state(p,t).x*1000];}),a);}
export function renderCalibration(svg,rows,fit){const xmax=Math.max(.25,...rows.map(r=>r.mass)),ymax=Math.max(.7,...rows.map(r=>r.period*r.period))*1.1,a=axes(svg,{xd:[0,xmax],yd:[0,ymax],xLabel:'附加质量 m / kg',yLabel:'周期平方 T² / s²',title:'虚拟读数的周期平方定标'});rows.forEach(r=>point(svg,r.mass,r.period*r.period,a));if(fit)line(svg,[[0,fit.intercept],[xmax,fit.slope*xmax+fit.intercept]],a);add(svg,'text',{x:a.left,y:20},rows.length?'空心点：当前同组记录':'改变加载质量后记录周期');}
