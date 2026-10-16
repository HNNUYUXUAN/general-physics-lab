/** Circular readings and the first-harmonic opposed-vernier teaching model. */
export function wrap(angle){if(!Number.isFinite(angle))throw new RangeError('角度须为有限数');return((angle%360)+360)%360;}
export function signedDifference(a,b){const delta=wrap(a-b+180)-180;if(Math.abs(delta+180)<1e-10)throw new RangeError('180°角差方向不唯一');return delta;}
export function separation(a,b){return Math.abs(signedDifference(a,b));}
export function readVerniers(physical_deg,{zero_deg,eccentricity_arcmin}){if(!Number.isFinite(zero_deg)||zero_deg<0||zero_deg>360||!Number.isFinite(eccentricity_arcmin)||eccentricity_arcmin<0||eccentricity_arcmin>10)throw new RangeError('零点0–360°，一阶偏心幅度0–10角分');const theta=wrap(physical_deg+zero_deg),perturb=eccentricity_arcmin/60*Math.cos(theta*Math.PI/180);return {left_deg:wrap(theta+perturb),right_deg:wrap(theta+180-perturb),physical_deg:wrap(physical_deg)};}
export function dualDifference(start,end){const left=signedDifference(end.left_deg,start.left_deg),right=signedDifference(end.right_deg,start.right_deg);if(left*right<0&&Math.abs(left-right)>1)throw new RangeError('两游标角差方向不一致');return{left_difference_deg:left,right_difference_deg:right,average_difference_deg:(left+right)/2};}
export function formatAngle(angle){const totalMinutes=wrap(angle)*60,degrees=Math.floor(totalMinutes/60),minutes=totalMinutes-degrees*60;return`${degrees}° ${minutes.toFixed(2)}′`;}
