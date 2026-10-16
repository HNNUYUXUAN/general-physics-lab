const NS='http://www.w3.org/2000/svg';
function add(svg,name,attrs={},text){const e=document.createElementNS(NS,name);for(const[k,v]of Object.entries(attrs))e.setAttribute(k,v);if(text!==undefined)e.textContent=text;svg.append(e);return e;}
function reset(svg,title){svg.replaceChildren();add(svg,'title',{},title);svg.setAttribute('aria-label',title);svg.setAttribute('font-size','16');}
const fmt=n=>String(Number(n.toPrecision(4)));
function axes(svg,{xd,yd,xLabel,yLabel,title}){
 reset(svg,title);const left=82,right=536,top=35,bottom=262,x=v=>left+(v-xd[0])/(xd[1]-xd[0])*(right-left),y=v=>bottom-(v-yd[0])/(yd[1]-yd[0])*(bottom-top);
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
export function renderSweep(svg,rows,current,half,p){const a=axes(svg,{xd:[rows[0].frequency,rows.at(-1).frequency],yd:[0,p.sourceVoltage*1.12],xLabel:'频率 f / Hz',yLabel:'电阻电压 Uᵣ / V',title:'稳态幅频响应与当前频率'});line(svg,rows.map(r=>[r.frequency,r.voltageR]),a);line(svg,[[rows[0].frequency,half.halfVoltage],[rows.at(-1).frequency,half.halfVoltage]],a,{stroke:'#999','stroke-dasharray':'5 5'});point(svg,current.frequency,current.voltageR,a,'#222');add(svg,'text',{x:a.left,y:20},'实线：理想电路　虚线：半功率电压');}
export function renderPhase(svg,rows,current){const a=axes(svg,{xd:[rows[0].frequency,rows.at(-1).frequency],yd:[-90,90],xLabel:'频率 f / Hz',yLabel:'电流相位 φ / °',title:'电流相对电源的相位响应'});line(svg,rows.map(r=>[r.frequency,r.phase*180/Math.PI]),a);point(svg,current.frequency,current.phase*180/Math.PI,a,'#222');add(svg,'text',{x:a.left,y:20},'正值：电流超前　负值：电流滞后');}
export function renderWaveform(svg,p,r){const a=axes(svg,{xd:[0,2],yd:[-1.15,1.15],xLabel:'归一化时间 ft',yLabel:'归一化瞬时值',title:'电源电压与电流的相位比较'});const ts=Array.from({length:401},(_,i)=>2*i/400);line(svg,ts.map(t=>[t,Math.sin(2*Math.PI*t)]),a,{stroke:'#999','stroke-dasharray':'6 4'});line(svg,ts.map(t=>[t,r.normalized*Math.sin(2*Math.PI*t+r.phase)]),a);add(svg,'text',{x:a.left,y:20},'实线：i / (√2 U/R)　虚线：u / (√2 U)');}
export function renderObservation(svg,rows){const ymax=Math.max(...rows.map(r=>r.voltage))*1.15;const a=axes(svg,{xd:[rows[0].frequency,rows.at(-1).frequency],yd:[0,ymax],xLabel:'频率 f / Hz',yLabel:'观测电阻电压 Uᵣ / V',title:'原报告频率扫描观测'});line(svg,rows.map(r=>[r.frequency,r.voltage]),a);rows.forEach(r=>point(svg,r.frequency,r.voltage,a));add(svg,'text',{x:a.left,y:20},'空心点：原始观测　连线：读数引导');}
export function renderCircuit(svg,p,r){if(window.innerWidth<=650)return compactCircuit(svg,p,r);svg.setAttribute('viewBox','0 0 700 340');reset(svg,'串联RLC稳态电路；R为总串联损耗，电表读取其等效电压');
 const wire=d=>add(svg,'path',{d,stroke:'#222',fill:'none','stroke-width':2});
 wire('M90 122V75H210 M300 75H345 M465 75H520V122 M520 178V245H90V178');
 add(svg,'circle',{cx:90,cy:150,r:28,fill:'white',stroke:'#222','stroke-width':2});
 wire('M70 150Q80 128 90 150T110 150');
 add(svg,'rect',{x:210,y:62,width:90,height:26,stroke:'#222',fill:'white','stroke-width':2});
 wire('M345 75C345 42 369 42 369 75C369 42 393 42 393 75C393 42 417 42 417 75C417 42 441 42 441 75H465');
 wire('M520 122V145 M499 145H541 M499 155H541 M520 155V178');
 for(const[x,y,t]of[[255,43,`R = ${fmt(p.resistance)} Ω`],[405,32,`L = ${fmt(p.inductance*1000)} mH`],[595,153,`C = ${fmt(p.capacitance*1e6)} μF`],[30,155,'正弦源'],[310,286,`U = ${fmt(p.sourceVoltage)} V（有效值）`],[310,315,`f = ${r.frequency.toFixed(2)} Hz`]])add(svg,'text',{x,y,'text-anchor':'middle'},t);
 add(svg,'text',{x:310,y:211,'text-anchor':'middle','font-size':20},`I = ${(r.current*1000).toFixed(3)} mA　　Uᵣ = ${r.voltageR.toFixed(4)} V`);
}
function compactCircuit(svg,p,r){svg.setAttribute('viewBox','0 0 400 330');reset(svg,'串联RLC紧凑电路，参数和读数分行显示');const wire=d=>add(svg,'path',{d,stroke:'#222',fill:'none','stroke-width':2});wire('M50 119V70H120 M200 70H235 M323 70H350V130 M350 170V235H50V163');add(svg,'circle',{cx:50,cy:141,r:22,fill:'white',stroke:'#222','stroke-width':2});wire('M35 141Q42.5 127 50 141T65 141');add(svg,'rect',{x:120,y:58,width:80,height:24,stroke:'#222',fill:'white','stroke-width':2});wire('M235 70C235 43 257 43 257 70C257 43 279 43 279 70C279 43 301 43 301 70C301 43 323 43 323 70');wire('M350 130V145 M333 145H367 M333 155H367 M350 155V170');for(const[x,y,t]of[[160,36,'R = '+fmt(p.resistance)+' Ω'],[282,22,'L = '+fmt(p.inductance*1000)+' mH'],[240,195,'C = '+fmt(p.capacitance*1e6)+' μF'],[200,270,'U = '+fmt(p.sourceVoltage)+' V　f = '+r.frequency.toFixed(1)+' Hz'],[200,303,'I = '+(r.current*1000).toFixed(3)+' mA　Uᵣ = '+r.voltageR.toFixed(4)+' V']])add(svg,'text',{x,y,'text-anchor':'middle','font-size':16},t);}
