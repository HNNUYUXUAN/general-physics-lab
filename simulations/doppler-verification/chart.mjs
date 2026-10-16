import {response,arrival,position} from './model.mjs';
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

export function apparatus(svg,p,time){
 const small=window.matchMedia('(max-width:650px)').matches,W=small?400:700,H=small?300:340,origin=small?40:65,scale=small?320:580,cy=small?135:162.5;
 svg.setAttribute('viewBox','0 0 '+W+' '+H);reset(svg,'静止声源在左，接收器沿水平轴匀速运动；灰线代表瞬时波前');svg.setAttribute('font-size',small?18:16);
 const r=response(p),pos=origin+position(p,time)*scale;add(svg,'line',{x1:origin,x2:origin+scale,y1:cy+75,y2:cy+75,stroke:'#777'});const phase=(time*p.frequency)%1;
 for(let i=0;i<200;i++){const x=(i+phase)*r.wavelength;if(x>1)break;add(svg,'line',{x1:origin+x*scale,x2:origin+x*scale,y1:cy-48,y2:cy+48,stroke:'#ddd'});}
 add(svg,'rect',{x:origin-17.5,y:cy-32.5,width:35,height:65,fill:'white',stroke:'#222','stroke-width':2});add(svg,'rect',{x:pos-13,y:cy-32.5,width:26,height:65,fill:'white',stroke:'#222','stroke-width':2});
 add(svg,'text',{x:origin,y:cy-68,'text-anchor':'middle'},'固定声源');add(svg,'text',{x:pos,y:cy-68,'text-anchor':'middle'},'接收器');
 add(svg,'text',{x:W/2,y:small?250:285,'text-anchor':'middle'},'x = '+position(p,time).toFixed(4)+' m    v = '+p.velocity.toFixed(2)+' m/s');add(svg,'text',{x:W/2,y:small?280:315,'text-anchor':'middle'},'波长 λ = '+(r.wavelength*1000).toFixed(4)+' mm');
}
export function scan(svg,p){const r=response(p),a=axes(svg,{xd:[-1.5,1.5],yd:[-p.frequency*1.7/r.speed,p.frequency*1.7/r.speed],xLabel:'接近速度 v / (m/s)',yLabel:'频移 Δf / Hz',title:'固定声源运动接收器的频移'});line(svg,[[-1.5,-p.frequency*1.5/r.speed],[1.5,p.frequency*1.5/r.speed]],a);point(svg,p.velocity,r.shift,a,'#222');}
export function arrivals(svg,p){const values=Array.from({length:6},(_,n)=>[n,arrival(p,n)*1000]),t0=values[0][1],t1=values.at(-1)[1],a=axes(svg,{xd:[0,5],yd:[t0-(t1-t0)*.12,t1+(t1-t0)*.12],xLabel:'波前序号 n',yLabel:'到达时间 tₙ / ms',title:'波前与接收器轨迹相交的时刻'});line(svg,values,a);values.forEach(([x,y])=>point(svg,x,y,a));add(svg,'text',{x:a.left,y:20},'连续波稳态：每个波前相邻到达');}
export function fitChart(svg,rows,f,sourceFrequency){const xs=rows.map(r=>r.velocity),ys=rows.map(r=>r.frequency-sourceFrequency),xmin=Math.min(-.1,...xs),xmax=Math.max(.1,...xs),ymin=Math.min(-5,...ys),ymax=Math.max(5,...ys),pad=(ymax-ymin)*.1,a=axes(svg,{xd:[xmin,xmax],yd:[ymin-pad,ymax+pad],xLabel:'接近速度 v / (m/s)',yLabel:'频移 Δf / Hz',title:'频率速度数据拟合，纵轴减去声源频率'});rows.forEach(r=>point(svg,r.velocity,r.frequency-sourceFrequency,a));if(f)line(svg,[[xmin,f.slope*xmin+f.intercept-sourceFrequency],[xmax,f.slope*xmax+f.intercept-sourceFrequency]],a);add(svg,'text',{x:a.left,y:20},'空心点：记录　实线：含截距拟合');}
