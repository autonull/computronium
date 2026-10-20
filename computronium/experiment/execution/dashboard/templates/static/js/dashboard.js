var Up=Object.defineProperty;var Np=(i,e,t)=>e in i?Up(i,e,{enumerable:!0,configurable:!0,writable:!0,value:t}):i[e]=t;var ae=(i,e,t)=>Np(i,typeof e!="symbol"?e+"":e,t);/**
 * @license
 * Copyright 2010-2024 Three.js Authors
 * SPDX-License-Identifier: MIT
 */const Hc="168",Xr={ROTATE:0,DOLLY:1,PAN:2},qr={ROTATE:0,PAN:1,DOLLY_PAN:2,DOLLY_ROTATE:3},Fp=0,Vu=1,Op=2,Vd=1,Gd=2,Ci=3,ir=0,Cn=1,gi=2,Qi=0,_s=1,Gu=2,Wu=3,Xu=4,Bp=5,br=100,zp=101,kp=102,Hp=103,Vp=104,Gp=200,Wp=201,Xp=202,qp=203,ql=204,Yl=205,Yp=206,$p=207,jp=208,Kp=209,Zp=210,Jp=211,Qp=212,em=213,tm=214,nm=0,im=1,rm=2,Mo=3,sm=4,am=5,om=6,lm=7,Wd=0,cm=1,um=2,er=0,hm=1,dm=2,fm=3,Xd=4,pm=5,mm=6,gm=7,qd=300,bs=301,Ts=302,$l=303,jl=304,Io=306,Kl=1e3,Ar=1001,Zl=1002,Xn=1003,_m=1004,Pa=1005,ti=1006,al=1007,Rr=1008,Oi=1009,Yd=1010,$d=1011,ma=1012,Vc=1013,Pr=1014,Li=1015,va=1016,Gc=1017,Wc=1018,ws=1020,jd=35902,Kd=1021,Zd=1022,ri=1023,Jd=1024,Qd=1025,vs=1026,As=1027,ef=1028,Xc=1029,tf=1030,qc=1031,Yc=1033,po=33776,mo=33777,go=33778,_o=33779,Jl=35840,Ql=35841,ec=35842,tc=35843,nc=36196,ic=37492,rc=37496,sc=37808,ac=37809,oc=37810,lc=37811,cc=37812,uc=37813,hc=37814,dc=37815,fc=37816,pc=37817,mc=37818,gc=37819,_c=37820,vc=37821,vo=36492,xc=36494,yc=36495,nf=36283,Mc=36284,Sc=36285,Ec=36286,vm=3200,xm=3201,rf=0,ym=1,Ji="",pi="srgb",lr="srgb-linear",$c="display-p3",Uo="display-p3-linear",So="linear",Nt="srgb",Eo="rec709",bo="p3",Yr=7680,qu=519,Mm=512,Sm=513,Em=514,sf=515,bm=516,Tm=517,wm=518,Am=519,bc=35044,Yu="300 es",Di=2e3,To=2001;let Us=class{addEventListener(e,t){this._listeners===void 0&&(this._listeners={});const n=this._listeners;n[e]===void 0&&(n[e]=[]),n[e].indexOf(t)===-1&&n[e].push(t)}hasEventListener(e,t){if(this._listeners===void 0)return!1;const n=this._listeners;return n[e]!==void 0&&n[e].indexOf(t)!==-1}removeEventListener(e,t){if(this._listeners===void 0)return;const r=this._listeners[e];if(r!==void 0){const s=r.indexOf(t);s!==-1&&r.splice(s,1)}}dispatchEvent(e){if(this._listeners===void 0)return;const n=this._listeners[e.type];if(n!==void 0){e.target=this;const r=n.slice(0);for(let s=0,a=r.length;s<a;s++)r[s].call(this,e);e.target=null}}};const pn=["00","01","02","03","04","05","06","07","08","09","0a","0b","0c","0d","0e","0f","10","11","12","13","14","15","16","17","18","19","1a","1b","1c","1d","1e","1f","20","21","22","23","24","25","26","27","28","29","2a","2b","2c","2d","2e","2f","30","31","32","33","34","35","36","37","38","39","3a","3b","3c","3d","3e","3f","40","41","42","43","44","45","46","47","48","49","4a","4b","4c","4d","4e","4f","50","51","52","53","54","55","56","57","58","59","5a","5b","5c","5d","5e","5f","60","61","62","63","64","65","66","67","68","69","6a","6b","6c","6d","6e","6f","70","71","72","73","74","75","76","77","78","79","7a","7b","7c","7d","7e","7f","80","81","82","83","84","85","86","87","88","89","8a","8b","8c","8d","8e","8f","90","91","92","93","94","95","96","97","98","99","9a","9b","9c","9d","9e","9f","a0","a1","a2","a3","a4","a5","a6","a7","a8","a9","aa","ab","ac","ad","ae","af","b0","b1","b2","b3","b4","b5","b6","b7","b8","b9","ba","bb","bc","bd","be","bf","c0","c1","c2","c3","c4","c5","c6","c7","c8","c9","ca","cb","cc","cd","ce","cf","d0","d1","d2","d3","d4","d5","d6","d7","d8","d9","da","db","dc","dd","de","df","e0","e1","e2","e3","e4","e5","e6","e7","e8","e9","ea","eb","ec","ed","ee","ef","f0","f1","f2","f3","f4","f5","f6","f7","f8","f9","fa","fb","fc","fd","fe","ff"];let $u=1234567;const xs=Math.PI/180,ga=180/Math.PI;function Ui(){const i=Math.random()*4294967295|0,e=Math.random()*4294967295|0,t=Math.random()*4294967295|0,n=Math.random()*4294967295|0;return(pn[i&255]+pn[i>>8&255]+pn[i>>16&255]+pn[i>>24&255]+"-"+pn[e&255]+pn[e>>8&255]+"-"+pn[e>>16&15|64]+pn[e>>24&255]+"-"+pn[t&63|128]+pn[t>>8&255]+"-"+pn[t>>16&255]+pn[t>>24&255]+pn[n&255]+pn[n>>8&255]+pn[n>>16&255]+pn[n>>24&255]).toLowerCase()}function gn(i,e,t){return Math.max(e,Math.min(t,i))}function jc(i,e){return(i%e+e)%e}function Rm(i,e,t,n,r){return n+(i-e)*(r-n)/(t-e)}function Cm(i,e,t){return i!==e?(t-i)/(e-i):0}function ca(i,e,t){return(1-t)*i+t*e}function Pm(i,e,t,n){return ca(i,e,1-Math.exp(-t*n))}function Lm(i,e=1){return e-Math.abs(jc(i,e*2)-e)}function Dm(i,e,t){return i<=e?0:i>=t?1:(i=(i-e)/(t-e),i*i*(3-2*i))}function Im(i,e,t){return i<=e?0:i>=t?1:(i=(i-e)/(t-e),i*i*i*(i*(i*6-15)+10))}function Um(i,e){return i+Math.floor(Math.random()*(e-i+1))}function Nm(i,e){return i+Math.random()*(e-i)}function Fm(i){return i*(.5-Math.random())}function Om(i){i!==void 0&&($u=i);let e=$u+=1831565813;return e=Math.imul(e^e>>>15,e|1),e^=e+Math.imul(e^e>>>7,e|61),((e^e>>>14)>>>0)/4294967296}function Bm(i){return i*xs}function zm(i){return i*ga}function km(i){return(i&i-1)===0&&i!==0}function Hm(i){return Math.pow(2,Math.ceil(Math.log(i)/Math.LN2))}function Vm(i){return Math.pow(2,Math.floor(Math.log(i)/Math.LN2))}function Gm(i,e,t,n,r){const s=Math.cos,a=Math.sin,o=s(t/2),l=a(t/2),c=s((e+n)/2),u=a((e+n)/2),h=s((e-n)/2),d=a((e-n)/2),m=s((n-e)/2),_=a((n-e)/2);switch(r){case"XYX":i.set(o*u,l*h,l*d,o*c);break;case"YZY":i.set(l*d,o*u,l*h,o*c);break;case"ZXZ":i.set(l*h,l*d,o*u,o*c);break;case"XZX":i.set(o*u,l*_,l*m,o*c);break;case"YXY":i.set(l*m,o*u,l*_,o*c);break;case"ZYZ":i.set(l*_,l*m,o*u,o*c);break;default:console.warn("THREE.MathUtils: .setQuaternionFromProperEuler() encountered an unknown order: "+r)}}function ni(i,e){switch(e.constructor){case Float32Array:return i;case Uint32Array:return i/4294967295;case Uint16Array:return i/65535;case Uint8Array:return i/255;case Int32Array:return Math.max(i/2147483647,-1);case Int16Array:return Math.max(i/32767,-1);case Int8Array:return Math.max(i/127,-1);default:throw new Error("Invalid component type.")}}function bt(i,e){switch(e.constructor){case Float32Array:return i;case Uint32Array:return Math.round(i*4294967295);case Uint16Array:return Math.round(i*65535);case Uint8Array:return Math.round(i*255);case Int32Array:return Math.round(i*2147483647);case Int16Array:return Math.round(i*32767);case Int8Array:return Math.round(i*127);default:throw new Error("Invalid component type.")}}const Tc={DEG2RAD:xs,RAD2DEG:ga,generateUUID:Ui,clamp:gn,euclideanModulo:jc,mapLinear:Rm,inverseLerp:Cm,lerp:ca,damp:Pm,pingpong:Lm,smoothstep:Dm,smootherstep:Im,randInt:Um,randFloat:Nm,randFloatSpread:Fm,seededRandom:Om,degToRad:Bm,radToDeg:zm,isPowerOfTwo:km,ceilPowerOfTwo:Hm,floorPowerOfTwo:Vm,setQuaternionFromProperEuler:Gm,normalize:bt,denormalize:ni};class Xe{constructor(e=0,t=0){Xe.prototype.isVector2=!0,this.x=e,this.y=t}get width(){return this.x}set width(e){this.x=e}get height(){return this.y}set height(e){this.y=e}set(e,t){return this.x=e,this.y=t,this}setScalar(e){return this.x=e,this.y=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y)}copy(e){return this.x=e.x,this.y=e.y,this}add(e){return this.x+=e.x,this.y+=e.y,this}addScalar(e){return this.x+=e,this.y+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this}subScalar(e){return this.x-=e,this.y-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this}multiply(e){return this.x*=e.x,this.y*=e.y,this}multiplyScalar(e){return this.x*=e,this.y*=e,this}divide(e){return this.x/=e.x,this.y/=e.y,this}divideScalar(e){return this.multiplyScalar(1/e)}applyMatrix3(e){const t=this.x,n=this.y,r=e.elements;return this.x=r[0]*t+r[3]*n+r[6],this.y=r[1]*t+r[4]*n+r[7],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this}negate(){return this.x=-this.x,this.y=-this.y,this}dot(e){return this.x*e.x+this.y*e.y}cross(e){return this.x*e.y-this.y*e.x}lengthSq(){return this.x*this.x+this.y*this.y}length(){return Math.sqrt(this.x*this.x+this.y*this.y)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)}normalize(){return this.divideScalar(this.length()||1)}angle(){return Math.atan2(-this.y,-this.x)+Math.PI}angleTo(e){const t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;const n=this.dot(e)/t;return Math.acos(gn(n,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){const t=this.x-e.x,n=this.y-e.y;return t*t+n*n}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this}equals(e){return e.x===this.x&&e.y===this.y}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this}rotateAround(e,t){const n=Math.cos(t),r=Math.sin(t),s=this.x-e.x,a=this.y-e.y;return this.x=s*n-a*r+e.x,this.y=s*r+a*n+e.y,this}random(){return this.x=Math.random(),this.y=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y}}class rt{constructor(e,t,n,r,s,a,o,l,c){rt.prototype.isMatrix3=!0,this.elements=[1,0,0,0,1,0,0,0,1],e!==void 0&&this.set(e,t,n,r,s,a,o,l,c)}set(e,t,n,r,s,a,o,l,c){const u=this.elements;return u[0]=e,u[1]=r,u[2]=o,u[3]=t,u[4]=s,u[5]=l,u[6]=n,u[7]=a,u[8]=c,this}identity(){return this.set(1,0,0,0,1,0,0,0,1),this}copy(e){const t=this.elements,n=e.elements;return t[0]=n[0],t[1]=n[1],t[2]=n[2],t[3]=n[3],t[4]=n[4],t[5]=n[5],t[6]=n[6],t[7]=n[7],t[8]=n[8],this}extractBasis(e,t,n){return e.setFromMatrix3Column(this,0),t.setFromMatrix3Column(this,1),n.setFromMatrix3Column(this,2),this}setFromMatrix4(e){const t=e.elements;return this.set(t[0],t[4],t[8],t[1],t[5],t[9],t[2],t[6],t[10]),this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){const n=e.elements,r=t.elements,s=this.elements,a=n[0],o=n[3],l=n[6],c=n[1],u=n[4],h=n[7],d=n[2],m=n[5],_=n[8],v=r[0],p=r[3],f=r[6],E=r[1],S=r[4],T=r[7],z=r[2],R=r[5],L=r[8];return s[0]=a*v+o*E+l*z,s[3]=a*p+o*S+l*R,s[6]=a*f+o*T+l*L,s[1]=c*v+u*E+h*z,s[4]=c*p+u*S+h*R,s[7]=c*f+u*T+h*L,s[2]=d*v+m*E+_*z,s[5]=d*p+m*S+_*R,s[8]=d*f+m*T+_*L,this}multiplyScalar(e){const t=this.elements;return t[0]*=e,t[3]*=e,t[6]*=e,t[1]*=e,t[4]*=e,t[7]*=e,t[2]*=e,t[5]*=e,t[8]*=e,this}determinant(){const e=this.elements,t=e[0],n=e[1],r=e[2],s=e[3],a=e[4],o=e[5],l=e[6],c=e[7],u=e[8];return t*a*u-t*o*c-n*s*u+n*o*l+r*s*c-r*a*l}invert(){const e=this.elements,t=e[0],n=e[1],r=e[2],s=e[3],a=e[4],o=e[5],l=e[6],c=e[7],u=e[8],h=u*a-o*c,d=o*l-u*s,m=c*s-a*l,_=t*h+n*d+r*m;if(_===0)return this.set(0,0,0,0,0,0,0,0,0);const v=1/_;return e[0]=h*v,e[1]=(r*c-u*n)*v,e[2]=(o*n-r*a)*v,e[3]=d*v,e[4]=(u*t-r*l)*v,e[5]=(r*s-o*t)*v,e[6]=m*v,e[7]=(n*l-c*t)*v,e[8]=(a*t-n*s)*v,this}transpose(){let e;const t=this.elements;return e=t[1],t[1]=t[3],t[3]=e,e=t[2],t[2]=t[6],t[6]=e,e=t[5],t[5]=t[7],t[7]=e,this}getNormalMatrix(e){return this.setFromMatrix4(e).invert().transpose()}transposeIntoArray(e){const t=this.elements;return e[0]=t[0],e[1]=t[3],e[2]=t[6],e[3]=t[1],e[4]=t[4],e[5]=t[7],e[6]=t[2],e[7]=t[5],e[8]=t[8],this}setUvTransform(e,t,n,r,s,a,o){const l=Math.cos(s),c=Math.sin(s);return this.set(n*l,n*c,-n*(l*a+c*o)+a+e,-r*c,r*l,-r*(-c*a+l*o)+o+t,0,0,1),this}scale(e,t){return this.premultiply(ol.makeScale(e,t)),this}rotate(e){return this.premultiply(ol.makeRotation(-e)),this}translate(e,t){return this.premultiply(ol.makeTranslation(e,t)),this}makeTranslation(e,t){return e.isVector2?this.set(1,0,e.x,0,1,e.y,0,0,1):this.set(1,0,e,0,1,t,0,0,1),this}makeRotation(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,-n,0,n,t,0,0,0,1),this}makeScale(e,t){return this.set(e,0,0,0,t,0,0,0,1),this}equals(e){const t=this.elements,n=e.elements;for(let r=0;r<9;r++)if(t[r]!==n[r])return!1;return!0}fromArray(e,t=0){for(let n=0;n<9;n++)this.elements[n]=e[n+t];return this}toArray(e=[],t=0){const n=this.elements;return e[t]=n[0],e[t+1]=n[1],e[t+2]=n[2],e[t+3]=n[3],e[t+4]=n[4],e[t+5]=n[5],e[t+6]=n[6],e[t+7]=n[7],e[t+8]=n[8],e}clone(){return new this.constructor().fromArray(this.elements)}}const ol=new rt;function af(i){for(let e=i.length-1;e>=0;--e)if(i[e]>=65535)return!0;return!1}function wo(i){return document.createElementNS("http://www.w3.org/1999/xhtml",i)}function Wm(){const i=wo("canvas");return i.style.display="block",i}const ju={};function ys(i){i in ju||(ju[i]=!0,console.warn(i))}function Xm(i,e,t){return new Promise(function(n,r){function s(){switch(i.clientWaitSync(e,i.SYNC_FLUSH_COMMANDS_BIT,0)){case i.WAIT_FAILED:r();break;case i.TIMEOUT_EXPIRED:setTimeout(s,t);break;default:n()}}setTimeout(s,t)})}const Ku=new rt().set(.8224621,.177538,0,.0331941,.9668058,0,.0170827,.0723974,.9105199),Zu=new rt().set(1.2249401,-.2249404,0,-.0420569,1.0420571,0,-.0196376,-.0786361,1.0982735),Ys={[lr]:{transfer:So,primaries:Eo,luminanceCoefficients:[.2126,.7152,.0722],toReference:i=>i,fromReference:i=>i},[pi]:{transfer:Nt,primaries:Eo,luminanceCoefficients:[.2126,.7152,.0722],toReference:i=>i.convertSRGBToLinear(),fromReference:i=>i.convertLinearToSRGB()},[Uo]:{transfer:So,primaries:bo,luminanceCoefficients:[.2289,.6917,.0793],toReference:i=>i.applyMatrix3(Zu),fromReference:i=>i.applyMatrix3(Ku)},[$c]:{transfer:Nt,primaries:bo,luminanceCoefficients:[.2289,.6917,.0793],toReference:i=>i.convertSRGBToLinear().applyMatrix3(Zu),fromReference:i=>i.applyMatrix3(Ku).convertLinearToSRGB()}},qm=new Set([lr,Uo]),Mt={enabled:!0,_workingColorSpace:lr,get workingColorSpace(){return this._workingColorSpace},set workingColorSpace(i){if(!qm.has(i))throw new Error(`Unsupported working color space, "${i}".`);this._workingColorSpace=i},convert:function(i,e,t){if(this.enabled===!1||e===t||!e||!t)return i;const n=Ys[e].toReference,r=Ys[t].fromReference;return r(n(i))},fromWorkingColorSpace:function(i,e){return this.convert(i,this._workingColorSpace,e)},toWorkingColorSpace:function(i,e){return this.convert(i,e,this._workingColorSpace)},getPrimaries:function(i){return Ys[i].primaries},getTransfer:function(i){return i===Ji?So:Ys[i].transfer},getLuminanceCoefficients:function(i,e=this._workingColorSpace){return i.fromArray(Ys[e].luminanceCoefficients)}};function Ms(i){return i<.04045?i*.0773993808:Math.pow(i*.9478672986+.0521327014,2.4)}function ll(i){return i<.0031308?i*12.92:1.055*Math.pow(i,.41666)-.055}let $r;class Ym{static getDataURL(e){if(/^data:/i.test(e.src)||typeof HTMLCanvasElement>"u")return e.src;let t;if(e instanceof HTMLCanvasElement)t=e;else{$r===void 0&&($r=wo("canvas")),$r.width=e.width,$r.height=e.height;const n=$r.getContext("2d");e instanceof ImageData?n.putImageData(e,0,0):n.drawImage(e,0,0,e.width,e.height),t=$r}return t.width>2048||t.height>2048?(console.warn("THREE.ImageUtils.getDataURL: Image converted to jpg for performance reasons",e),t.toDataURL("image/jpeg",.6)):t.toDataURL("image/png")}static sRGBToLinear(e){if(typeof HTMLImageElement<"u"&&e instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&e instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&e instanceof ImageBitmap){const t=wo("canvas");t.width=e.width,t.height=e.height;const n=t.getContext("2d");n.drawImage(e,0,0,e.width,e.height);const r=n.getImageData(0,0,e.width,e.height),s=r.data;for(let a=0;a<s.length;a++)s[a]=Ms(s[a]/255)*255;return n.putImageData(r,0,0),t}else if(e.data){const t=e.data.slice(0);for(let n=0;n<t.length;n++)t instanceof Uint8Array||t instanceof Uint8ClampedArray?t[n]=Math.floor(Ms(t[n]/255)*255):t[n]=Ms(t[n]);return{data:t,width:e.width,height:e.height}}else return console.warn("THREE.ImageUtils.sRGBToLinear(): Unsupported image type. No color space conversion applied."),e}}let $m=0;class of{constructor(e=null){this.isSource=!0,Object.defineProperty(this,"id",{value:$m++}),this.uuid=Ui(),this.data=e,this.dataReady=!0,this.version=0}set needsUpdate(e){e===!0&&this.version++}toJSON(e){const t=e===void 0||typeof e=="string";if(!t&&e.images[this.uuid]!==void 0)return e.images[this.uuid];const n={uuid:this.uuid,url:""},r=this.data;if(r!==null){let s;if(Array.isArray(r)){s=[];for(let a=0,o=r.length;a<o;a++)r[a].isDataTexture?s.push(cl(r[a].image)):s.push(cl(r[a]))}else s=cl(r);n.url=s}return t||(e.images[this.uuid]=n),n}}function cl(i){return typeof HTMLImageElement<"u"&&i instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&i instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&i instanceof ImageBitmap?Ym.getDataURL(i):i.data?{data:Array.from(i.data),width:i.width,height:i.height,type:i.data.constructor.name}:(console.warn("THREE.Texture: Unable to serialize Texture."),{})}let jm=0;class An extends Us{constructor(e=An.DEFAULT_IMAGE,t=An.DEFAULT_MAPPING,n=Ar,r=Ar,s=ti,a=Rr,o=ri,l=Oi,c=An.DEFAULT_ANISOTROPY,u=Ji){super(),this.isTexture=!0,Object.defineProperty(this,"id",{value:jm++}),this.uuid=Ui(),this.name="",this.source=new of(e),this.mipmaps=[],this.mapping=t,this.channel=0,this.wrapS=n,this.wrapT=r,this.magFilter=s,this.minFilter=a,this.anisotropy=c,this.format=o,this.internalFormat=null,this.type=l,this.offset=new Xe(0,0),this.repeat=new Xe(1,1),this.center=new Xe(0,0),this.rotation=0,this.matrixAutoUpdate=!0,this.matrix=new rt,this.generateMipmaps=!0,this.premultiplyAlpha=!1,this.flipY=!0,this.unpackAlignment=4,this.colorSpace=u,this.userData={},this.version=0,this.onUpdate=null,this.isRenderTargetTexture=!1,this.pmremVersion=0}get image(){return this.source.data}set image(e=null){this.source.data=e}updateMatrix(){this.matrix.setUvTransform(this.offset.x,this.offset.y,this.repeat.x,this.repeat.y,this.rotation,this.center.x,this.center.y)}clone(){return new this.constructor().copy(this)}copy(e){return this.name=e.name,this.source=e.source,this.mipmaps=e.mipmaps.slice(0),this.mapping=e.mapping,this.channel=e.channel,this.wrapS=e.wrapS,this.wrapT=e.wrapT,this.magFilter=e.magFilter,this.minFilter=e.minFilter,this.anisotropy=e.anisotropy,this.format=e.format,this.internalFormat=e.internalFormat,this.type=e.type,this.offset.copy(e.offset),this.repeat.copy(e.repeat),this.center.copy(e.center),this.rotation=e.rotation,this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrix.copy(e.matrix),this.generateMipmaps=e.generateMipmaps,this.premultiplyAlpha=e.premultiplyAlpha,this.flipY=e.flipY,this.unpackAlignment=e.unpackAlignment,this.colorSpace=e.colorSpace,this.userData=JSON.parse(JSON.stringify(e.userData)),this.needsUpdate=!0,this}toJSON(e){const t=e===void 0||typeof e=="string";if(!t&&e.textures[this.uuid]!==void 0)return e.textures[this.uuid];const n={metadata:{version:4.6,type:"Texture",generator:"Texture.toJSON"},uuid:this.uuid,name:this.name,image:this.source.toJSON(e).uuid,mapping:this.mapping,channel:this.channel,repeat:[this.repeat.x,this.repeat.y],offset:[this.offset.x,this.offset.y],center:[this.center.x,this.center.y],rotation:this.rotation,wrap:[this.wrapS,this.wrapT],format:this.format,internalFormat:this.internalFormat,type:this.type,colorSpace:this.colorSpace,minFilter:this.minFilter,magFilter:this.magFilter,anisotropy:this.anisotropy,flipY:this.flipY,generateMipmaps:this.generateMipmaps,premultiplyAlpha:this.premultiplyAlpha,unpackAlignment:this.unpackAlignment};return Object.keys(this.userData).length>0&&(n.userData=this.userData),t||(e.textures[this.uuid]=n),n}dispose(){this.dispatchEvent({type:"dispose"})}transformUv(e){if(this.mapping!==qd)return e;if(e.applyMatrix3(this.matrix),e.x<0||e.x>1)switch(this.wrapS){case Kl:e.x=e.x-Math.floor(e.x);break;case Ar:e.x=e.x<0?0:1;break;case Zl:Math.abs(Math.floor(e.x)%2)===1?e.x=Math.ceil(e.x)-e.x:e.x=e.x-Math.floor(e.x);break}if(e.y<0||e.y>1)switch(this.wrapT){case Kl:e.y=e.y-Math.floor(e.y);break;case Ar:e.y=e.y<0?0:1;break;case Zl:Math.abs(Math.floor(e.y)%2)===1?e.y=Math.ceil(e.y)-e.y:e.y=e.y-Math.floor(e.y);break}return this.flipY&&(e.y=1-e.y),e}set needsUpdate(e){e===!0&&(this.version++,this.source.needsUpdate=!0)}set needsPMREMUpdate(e){e===!0&&this.pmremVersion++}}An.DEFAULT_IMAGE=null;An.DEFAULT_MAPPING=qd;An.DEFAULT_ANISOTROPY=1;class Zt{constructor(e=0,t=0,n=0,r=1){Zt.prototype.isVector4=!0,this.x=e,this.y=t,this.z=n,this.w=r}get width(){return this.z}set width(e){this.z=e}get height(){return this.w}set height(e){this.w=e}set(e,t,n,r){return this.x=e,this.y=t,this.z=n,this.w=r,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this.w=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setW(e){return this.w=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;case 3:this.w=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;case 3:return this.w;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z,this.w)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this.w=e.w!==void 0?e.w:1,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this.w+=e.w,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this.w+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this.w=e.w+t.w,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this.w+=e.w*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this.w-=e.w,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this.w-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this.w=e.w-t.w,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this.w*=e.w,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this.w*=e,this}applyMatrix4(e){const t=this.x,n=this.y,r=this.z,s=this.w,a=e.elements;return this.x=a[0]*t+a[4]*n+a[8]*r+a[12]*s,this.y=a[1]*t+a[5]*n+a[9]*r+a[13]*s,this.z=a[2]*t+a[6]*n+a[10]*r+a[14]*s,this.w=a[3]*t+a[7]*n+a[11]*r+a[15]*s,this}divideScalar(e){return this.multiplyScalar(1/e)}setAxisAngleFromQuaternion(e){this.w=2*Math.acos(e.w);const t=Math.sqrt(1-e.w*e.w);return t<1e-4?(this.x=1,this.y=0,this.z=0):(this.x=e.x/t,this.y=e.y/t,this.z=e.z/t),this}setAxisAngleFromRotationMatrix(e){let t,n,r,s;const l=e.elements,c=l[0],u=l[4],h=l[8],d=l[1],m=l[5],_=l[9],v=l[2],p=l[6],f=l[10];if(Math.abs(u-d)<.01&&Math.abs(h-v)<.01&&Math.abs(_-p)<.01){if(Math.abs(u+d)<.1&&Math.abs(h+v)<.1&&Math.abs(_+p)<.1&&Math.abs(c+m+f-3)<.1)return this.set(1,0,0,0),this;t=Math.PI;const S=(c+1)/2,T=(m+1)/2,z=(f+1)/2,R=(u+d)/4,L=(h+v)/4,O=(_+p)/4;return S>T&&S>z?S<.01?(n=0,r=.707106781,s=.707106781):(n=Math.sqrt(S),r=R/n,s=L/n):T>z?T<.01?(n=.707106781,r=0,s=.707106781):(r=Math.sqrt(T),n=R/r,s=O/r):z<.01?(n=.707106781,r=.707106781,s=0):(s=Math.sqrt(z),n=L/s,r=O/s),this.set(n,r,s,t),this}let E=Math.sqrt((p-_)*(p-_)+(h-v)*(h-v)+(d-u)*(d-u));return Math.abs(E)<.001&&(E=1),this.x=(p-_)/E,this.y=(h-v)/E,this.z=(d-u)/E,this.w=Math.acos((c+m+f-1)/2),this}setFromMatrixPosition(e){const t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this.w=t[15],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this.w=Math.min(this.w,e.w),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this.w=Math.max(this.w,e.w),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this.z=Math.max(e.z,Math.min(t.z,this.z)),this.w=Math.max(e.w,Math.min(t.w,this.w)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this.z=Math.max(e,Math.min(t,this.z)),this.w=Math.max(e,Math.min(t,this.w)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this.w=Math.floor(this.w),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this.w=Math.ceil(this.w),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this.w=Math.round(this.w),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this.w=Math.trunc(this.w),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this.w=-this.w,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z+this.w*e.w}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)+Math.abs(this.w)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this.w+=(e.w-this.w)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this.z=e.z+(t.z-e.z)*n,this.w=e.w+(t.w-e.w)*n,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z&&e.w===this.w}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this.w=e[t+3],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e[t+3]=this.w,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this.w=e.getW(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this.w=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z,yield this.w}}class Km extends Us{constructor(e=1,t=1,n={}){super(),this.isRenderTarget=!0,this.width=e,this.height=t,this.depth=1,this.scissor=new Zt(0,0,e,t),this.scissorTest=!1,this.viewport=new Zt(0,0,e,t);const r={width:e,height:t,depth:1};n=Object.assign({generateMipmaps:!1,internalFormat:null,minFilter:ti,depthBuffer:!0,stencilBuffer:!1,resolveDepthBuffer:!0,resolveStencilBuffer:!0,depthTexture:null,samples:0,count:1},n);const s=new An(r,n.mapping,n.wrapS,n.wrapT,n.magFilter,n.minFilter,n.format,n.type,n.anisotropy,n.colorSpace);s.flipY=!1,s.generateMipmaps=n.generateMipmaps,s.internalFormat=n.internalFormat,this.textures=[];const a=n.count;for(let o=0;o<a;o++)this.textures[o]=s.clone(),this.textures[o].isRenderTargetTexture=!0;this.depthBuffer=n.depthBuffer,this.stencilBuffer=n.stencilBuffer,this.resolveDepthBuffer=n.resolveDepthBuffer,this.resolveStencilBuffer=n.resolveStencilBuffer,this.depthTexture=n.depthTexture,this.samples=n.samples}get texture(){return this.textures[0]}set texture(e){this.textures[0]=e}setSize(e,t,n=1){if(this.width!==e||this.height!==t||this.depth!==n){this.width=e,this.height=t,this.depth=n;for(let r=0,s=this.textures.length;r<s;r++)this.textures[r].image.width=e,this.textures[r].image.height=t,this.textures[r].image.depth=n;this.dispose()}this.viewport.set(0,0,e,t),this.scissor.set(0,0,e,t)}clone(){return new this.constructor().copy(this)}copy(e){this.width=e.width,this.height=e.height,this.depth=e.depth,this.scissor.copy(e.scissor),this.scissorTest=e.scissorTest,this.viewport.copy(e.viewport),this.textures.length=0;for(let n=0,r=e.textures.length;n<r;n++)this.textures[n]=e.textures[n].clone(),this.textures[n].isRenderTargetTexture=!0;const t=Object.assign({},e.texture.image);return this.texture.source=new of(t),this.depthBuffer=e.depthBuffer,this.stencilBuffer=e.stencilBuffer,this.resolveDepthBuffer=e.resolveDepthBuffer,this.resolveStencilBuffer=e.resolveStencilBuffer,e.depthTexture!==null&&(this.depthTexture=e.depthTexture.clone()),this.samples=e.samples,this}dispose(){this.dispatchEvent({type:"dispose"})}}class Lr extends Km{constructor(e=1,t=1,n={}){super(e,t,n),this.isWebGLRenderTarget=!0}}class lf extends An{constructor(e=null,t=1,n=1,r=1){super(null),this.isDataArrayTexture=!0,this.image={data:e,width:t,height:n,depth:r},this.magFilter=Xn,this.minFilter=Xn,this.wrapR=Ar,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1,this.layerUpdates=new Set}addLayerUpdate(e){this.layerUpdates.add(e)}clearLayerUpdates(){this.layerUpdates.clear()}}class Zm extends An{constructor(e=null,t=1,n=1,r=1){super(null),this.isData3DTexture=!0,this.image={data:e,width:t,height:n,depth:r},this.magFilter=Xn,this.minFilter=Xn,this.wrapR=Ar,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}}class Dr{constructor(e=0,t=0,n=0,r=1){this.isQuaternion=!0,this._x=e,this._y=t,this._z=n,this._w=r}static slerpFlat(e,t,n,r,s,a,o){let l=n[r+0],c=n[r+1],u=n[r+2],h=n[r+3];const d=s[a+0],m=s[a+1],_=s[a+2],v=s[a+3];if(o===0){e[t+0]=l,e[t+1]=c,e[t+2]=u,e[t+3]=h;return}if(o===1){e[t+0]=d,e[t+1]=m,e[t+2]=_,e[t+3]=v;return}if(h!==v||l!==d||c!==m||u!==_){let p=1-o;const f=l*d+c*m+u*_+h*v,E=f>=0?1:-1,S=1-f*f;if(S>Number.EPSILON){const z=Math.sqrt(S),R=Math.atan2(z,f*E);p=Math.sin(p*R)/z,o=Math.sin(o*R)/z}const T=o*E;if(l=l*p+d*T,c=c*p+m*T,u=u*p+_*T,h=h*p+v*T,p===1-o){const z=1/Math.sqrt(l*l+c*c+u*u+h*h);l*=z,c*=z,u*=z,h*=z}}e[t]=l,e[t+1]=c,e[t+2]=u,e[t+3]=h}static multiplyQuaternionsFlat(e,t,n,r,s,a){const o=n[r],l=n[r+1],c=n[r+2],u=n[r+3],h=s[a],d=s[a+1],m=s[a+2],_=s[a+3];return e[t]=o*_+u*h+l*m-c*d,e[t+1]=l*_+u*d+c*h-o*m,e[t+2]=c*_+u*m+o*d-l*h,e[t+3]=u*_-o*h-l*d-c*m,e}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get w(){return this._w}set w(e){this._w=e,this._onChangeCallback()}set(e,t,n,r){return this._x=e,this._y=t,this._z=n,this._w=r,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._w)}copy(e){return this._x=e.x,this._y=e.y,this._z=e.z,this._w=e.w,this._onChangeCallback(),this}setFromEuler(e,t=!0){const n=e._x,r=e._y,s=e._z,a=e._order,o=Math.cos,l=Math.sin,c=o(n/2),u=o(r/2),h=o(s/2),d=l(n/2),m=l(r/2),_=l(s/2);switch(a){case"XYZ":this._x=d*u*h+c*m*_,this._y=c*m*h-d*u*_,this._z=c*u*_+d*m*h,this._w=c*u*h-d*m*_;break;case"YXZ":this._x=d*u*h+c*m*_,this._y=c*m*h-d*u*_,this._z=c*u*_-d*m*h,this._w=c*u*h+d*m*_;break;case"ZXY":this._x=d*u*h-c*m*_,this._y=c*m*h+d*u*_,this._z=c*u*_+d*m*h,this._w=c*u*h-d*m*_;break;case"ZYX":this._x=d*u*h-c*m*_,this._y=c*m*h+d*u*_,this._z=c*u*_-d*m*h,this._w=c*u*h+d*m*_;break;case"YZX":this._x=d*u*h+c*m*_,this._y=c*m*h+d*u*_,this._z=c*u*_-d*m*h,this._w=c*u*h-d*m*_;break;case"XZY":this._x=d*u*h-c*m*_,this._y=c*m*h-d*u*_,this._z=c*u*_+d*m*h,this._w=c*u*h+d*m*_;break;default:console.warn("THREE.Quaternion: .setFromEuler() encountered an unknown order: "+a)}return t===!0&&this._onChangeCallback(),this}setFromAxisAngle(e,t){const n=t/2,r=Math.sin(n);return this._x=e.x*r,this._y=e.y*r,this._z=e.z*r,this._w=Math.cos(n),this._onChangeCallback(),this}setFromRotationMatrix(e){const t=e.elements,n=t[0],r=t[4],s=t[8],a=t[1],o=t[5],l=t[9],c=t[2],u=t[6],h=t[10],d=n+o+h;if(d>0){const m=.5/Math.sqrt(d+1);this._w=.25/m,this._x=(u-l)*m,this._y=(s-c)*m,this._z=(a-r)*m}else if(n>o&&n>h){const m=2*Math.sqrt(1+n-o-h);this._w=(u-l)/m,this._x=.25*m,this._y=(r+a)/m,this._z=(s+c)/m}else if(o>h){const m=2*Math.sqrt(1+o-n-h);this._w=(s-c)/m,this._x=(r+a)/m,this._y=.25*m,this._z=(l+u)/m}else{const m=2*Math.sqrt(1+h-n-o);this._w=(a-r)/m,this._x=(s+c)/m,this._y=(l+u)/m,this._z=.25*m}return this._onChangeCallback(),this}setFromUnitVectors(e,t){let n=e.dot(t)+1;return n<Number.EPSILON?(n=0,Math.abs(e.x)>Math.abs(e.z)?(this._x=-e.y,this._y=e.x,this._z=0,this._w=n):(this._x=0,this._y=-e.z,this._z=e.y,this._w=n)):(this._x=e.y*t.z-e.z*t.y,this._y=e.z*t.x-e.x*t.z,this._z=e.x*t.y-e.y*t.x,this._w=n),this.normalize()}angleTo(e){return 2*Math.acos(Math.abs(gn(this.dot(e),-1,1)))}rotateTowards(e,t){const n=this.angleTo(e);if(n===0)return this;const r=Math.min(1,t/n);return this.slerp(e,r),this}identity(){return this.set(0,0,0,1)}invert(){return this.conjugate()}conjugate(){return this._x*=-1,this._y*=-1,this._z*=-1,this._onChangeCallback(),this}dot(e){return this._x*e._x+this._y*e._y+this._z*e._z+this._w*e._w}lengthSq(){return this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w}length(){return Math.sqrt(this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w)}normalize(){let e=this.length();return e===0?(this._x=0,this._y=0,this._z=0,this._w=1):(e=1/e,this._x=this._x*e,this._y=this._y*e,this._z=this._z*e,this._w=this._w*e),this._onChangeCallback(),this}multiply(e){return this.multiplyQuaternions(this,e)}premultiply(e){return this.multiplyQuaternions(e,this)}multiplyQuaternions(e,t){const n=e._x,r=e._y,s=e._z,a=e._w,o=t._x,l=t._y,c=t._z,u=t._w;return this._x=n*u+a*o+r*c-s*l,this._y=r*u+a*l+s*o-n*c,this._z=s*u+a*c+n*l-r*o,this._w=a*u-n*o-r*l-s*c,this._onChangeCallback(),this}slerp(e,t){if(t===0)return this;if(t===1)return this.copy(e);const n=this._x,r=this._y,s=this._z,a=this._w;let o=a*e._w+n*e._x+r*e._y+s*e._z;if(o<0?(this._w=-e._w,this._x=-e._x,this._y=-e._y,this._z=-e._z,o=-o):this.copy(e),o>=1)return this._w=a,this._x=n,this._y=r,this._z=s,this;const l=1-o*o;if(l<=Number.EPSILON){const m=1-t;return this._w=m*a+t*this._w,this._x=m*n+t*this._x,this._y=m*r+t*this._y,this._z=m*s+t*this._z,this.normalize(),this}const c=Math.sqrt(l),u=Math.atan2(c,o),h=Math.sin((1-t)*u)/c,d=Math.sin(t*u)/c;return this._w=a*h+this._w*d,this._x=n*h+this._x*d,this._y=r*h+this._y*d,this._z=s*h+this._z*d,this._onChangeCallback(),this}slerpQuaternions(e,t,n){return this.copy(e).slerp(t,n)}random(){const e=2*Math.PI*Math.random(),t=2*Math.PI*Math.random(),n=Math.random(),r=Math.sqrt(1-n),s=Math.sqrt(n);return this.set(r*Math.sin(e),r*Math.cos(e),s*Math.sin(t),s*Math.cos(t))}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._w===this._w}fromArray(e,t=0){return this._x=e[t],this._y=e[t+1],this._z=e[t+2],this._w=e[t+3],this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._w,e}fromBufferAttribute(e,t){return this._x=e.getX(t),this._y=e.getY(t),this._z=e.getZ(t),this._w=e.getW(t),this._onChangeCallback(),this}toJSON(){return this.toArray()}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._w}}class H{constructor(e=0,t=0,n=0){H.prototype.isVector3=!0,this.x=e,this.y=t,this.z=n}set(e,t,n){return n===void 0&&(n=this.z),this.x=e,this.y=t,this.z=n,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this}multiplyVectors(e,t){return this.x=e.x*t.x,this.y=e.y*t.y,this.z=e.z*t.z,this}applyEuler(e){return this.applyQuaternion(Ju.setFromEuler(e))}applyAxisAngle(e,t){return this.applyQuaternion(Ju.setFromAxisAngle(e,t))}applyMatrix3(e){const t=this.x,n=this.y,r=this.z,s=e.elements;return this.x=s[0]*t+s[3]*n+s[6]*r,this.y=s[1]*t+s[4]*n+s[7]*r,this.z=s[2]*t+s[5]*n+s[8]*r,this}applyNormalMatrix(e){return this.applyMatrix3(e).normalize()}applyMatrix4(e){const t=this.x,n=this.y,r=this.z,s=e.elements,a=1/(s[3]*t+s[7]*n+s[11]*r+s[15]);return this.x=(s[0]*t+s[4]*n+s[8]*r+s[12])*a,this.y=(s[1]*t+s[5]*n+s[9]*r+s[13])*a,this.z=(s[2]*t+s[6]*n+s[10]*r+s[14])*a,this}applyQuaternion(e){const t=this.x,n=this.y,r=this.z,s=e.x,a=e.y,o=e.z,l=e.w,c=2*(a*r-o*n),u=2*(o*t-s*r),h=2*(s*n-a*t);return this.x=t+l*c+a*h-o*u,this.y=n+l*u+o*c-s*h,this.z=r+l*h+s*u-a*c,this}project(e){return this.applyMatrix4(e.matrixWorldInverse).applyMatrix4(e.projectionMatrix)}unproject(e){return this.applyMatrix4(e.projectionMatrixInverse).applyMatrix4(e.matrixWorld)}transformDirection(e){const t=this.x,n=this.y,r=this.z,s=e.elements;return this.x=s[0]*t+s[4]*n+s[8]*r,this.y=s[1]*t+s[5]*n+s[9]*r,this.z=s[2]*t+s[6]*n+s[10]*r,this.normalize()}divide(e){return this.x/=e.x,this.y/=e.y,this.z/=e.z,this}divideScalar(e){return this.multiplyScalar(1/e)}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this.z=Math.max(e.z,Math.min(t.z,this.z)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this.z=Math.max(e,Math.min(t,this.z)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this.z=e.z+(t.z-e.z)*n,this}cross(e){return this.crossVectors(this,e)}crossVectors(e,t){const n=e.x,r=e.y,s=e.z,a=t.x,o=t.y,l=t.z;return this.x=r*l-s*o,this.y=s*a-n*l,this.z=n*o-r*a,this}projectOnVector(e){const t=e.lengthSq();if(t===0)return this.set(0,0,0);const n=e.dot(this)/t;return this.copy(e).multiplyScalar(n)}projectOnPlane(e){return ul.copy(this).projectOnVector(e),this.sub(ul)}reflect(e){return this.sub(ul.copy(e).multiplyScalar(2*this.dot(e)))}angleTo(e){const t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;const n=this.dot(e)/t;return Math.acos(gn(n,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){const t=this.x-e.x,n=this.y-e.y,r=this.z-e.z;return t*t+n*n+r*r}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)+Math.abs(this.z-e.z)}setFromSpherical(e){return this.setFromSphericalCoords(e.radius,e.phi,e.theta)}setFromSphericalCoords(e,t,n){const r=Math.sin(t)*e;return this.x=r*Math.sin(n),this.y=Math.cos(t)*e,this.z=r*Math.cos(n),this}setFromCylindrical(e){return this.setFromCylindricalCoords(e.radius,e.theta,e.y)}setFromCylindricalCoords(e,t,n){return this.x=e*Math.sin(t),this.y=n,this.z=e*Math.cos(t),this}setFromMatrixPosition(e){const t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this}setFromMatrixScale(e){const t=this.setFromMatrixColumn(e,0).length(),n=this.setFromMatrixColumn(e,1).length(),r=this.setFromMatrixColumn(e,2).length();return this.x=t,this.y=n,this.z=r,this}setFromMatrixColumn(e,t){return this.fromArray(e.elements,t*4)}setFromMatrix3Column(e,t){return this.fromArray(e.elements,t*3)}setFromEuler(e){return this.x=e._x,this.y=e._y,this.z=e._z,this}setFromColor(e){return this.x=e.r,this.y=e.g,this.z=e.b,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this}randomDirection(){const e=Math.random()*Math.PI*2,t=Math.random()*2-1,n=Math.sqrt(1-t*t);return this.x=n*Math.cos(e),this.y=t,this.z=n*Math.sin(e),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z}}const ul=new H,Ju=new Dr;class xa{constructor(e=new H(1/0,1/0,1/0),t=new H(-1/0,-1/0,-1/0)){this.isBox3=!0,this.min=e,this.max=t}set(e,t){return this.min.copy(e),this.max.copy(t),this}setFromArray(e){this.makeEmpty();for(let t=0,n=e.length;t<n;t+=3)this.expandByPoint(Kn.fromArray(e,t));return this}setFromBufferAttribute(e){this.makeEmpty();for(let t=0,n=e.count;t<n;t++)this.expandByPoint(Kn.fromBufferAttribute(e,t));return this}setFromPoints(e){this.makeEmpty();for(let t=0,n=e.length;t<n;t++)this.expandByPoint(e[t]);return this}setFromCenterAndSize(e,t){const n=Kn.copy(t).multiplyScalar(.5);return this.min.copy(e).sub(n),this.max.copy(e).add(n),this}setFromObject(e,t=!1){return this.makeEmpty(),this.expandByObject(e,t)}clone(){return new this.constructor().copy(this)}copy(e){return this.min.copy(e.min),this.max.copy(e.max),this}makeEmpty(){return this.min.x=this.min.y=this.min.z=1/0,this.max.x=this.max.y=this.max.z=-1/0,this}isEmpty(){return this.max.x<this.min.x||this.max.y<this.min.y||this.max.z<this.min.z}getCenter(e){return this.isEmpty()?e.set(0,0,0):e.addVectors(this.min,this.max).multiplyScalar(.5)}getSize(e){return this.isEmpty()?e.set(0,0,0):e.subVectors(this.max,this.min)}expandByPoint(e){return this.min.min(e),this.max.max(e),this}expandByVector(e){return this.min.sub(e),this.max.add(e),this}expandByScalar(e){return this.min.addScalar(-e),this.max.addScalar(e),this}expandByObject(e,t=!1){e.updateWorldMatrix(!1,!1);const n=e.geometry;if(n!==void 0){const s=n.getAttribute("position");if(t===!0&&s!==void 0&&e.isInstancedMesh!==!0)for(let a=0,o=s.count;a<o;a++)e.isMesh===!0?e.getVertexPosition(a,Kn):Kn.fromBufferAttribute(s,a),Kn.applyMatrix4(e.matrixWorld),this.expandByPoint(Kn);else e.boundingBox!==void 0?(e.boundingBox===null&&e.computeBoundingBox(),La.copy(e.boundingBox)):(n.boundingBox===null&&n.computeBoundingBox(),La.copy(n.boundingBox)),La.applyMatrix4(e.matrixWorld),this.union(La)}const r=e.children;for(let s=0,a=r.length;s<a;s++)this.expandByObject(r[s],t);return this}containsPoint(e){return e.x>=this.min.x&&e.x<=this.max.x&&e.y>=this.min.y&&e.y<=this.max.y&&e.z>=this.min.z&&e.z<=this.max.z}containsBox(e){return this.min.x<=e.min.x&&e.max.x<=this.max.x&&this.min.y<=e.min.y&&e.max.y<=this.max.y&&this.min.z<=e.min.z&&e.max.z<=this.max.z}getParameter(e,t){return t.set((e.x-this.min.x)/(this.max.x-this.min.x),(e.y-this.min.y)/(this.max.y-this.min.y),(e.z-this.min.z)/(this.max.z-this.min.z))}intersectsBox(e){return e.max.x>=this.min.x&&e.min.x<=this.max.x&&e.max.y>=this.min.y&&e.min.y<=this.max.y&&e.max.z>=this.min.z&&e.min.z<=this.max.z}intersectsSphere(e){return this.clampPoint(e.center,Kn),Kn.distanceToSquared(e.center)<=e.radius*e.radius}intersectsPlane(e){let t,n;return e.normal.x>0?(t=e.normal.x*this.min.x,n=e.normal.x*this.max.x):(t=e.normal.x*this.max.x,n=e.normal.x*this.min.x),e.normal.y>0?(t+=e.normal.y*this.min.y,n+=e.normal.y*this.max.y):(t+=e.normal.y*this.max.y,n+=e.normal.y*this.min.y),e.normal.z>0?(t+=e.normal.z*this.min.z,n+=e.normal.z*this.max.z):(t+=e.normal.z*this.max.z,n+=e.normal.z*this.min.z),t<=-e.constant&&n>=-e.constant}intersectsTriangle(e){if(this.isEmpty())return!1;this.getCenter($s),Da.subVectors(this.max,$s),jr.subVectors(e.a,$s),Kr.subVectors(e.b,$s),Zr.subVectors(e.c,$s),Gi.subVectors(Kr,jr),Wi.subVectors(Zr,Kr),mr.subVectors(jr,Zr);let t=[0,-Gi.z,Gi.y,0,-Wi.z,Wi.y,0,-mr.z,mr.y,Gi.z,0,-Gi.x,Wi.z,0,-Wi.x,mr.z,0,-mr.x,-Gi.y,Gi.x,0,-Wi.y,Wi.x,0,-mr.y,mr.x,0];return!hl(t,jr,Kr,Zr,Da)||(t=[1,0,0,0,1,0,0,0,1],!hl(t,jr,Kr,Zr,Da))?!1:(Ia.crossVectors(Gi,Wi),t=[Ia.x,Ia.y,Ia.z],hl(t,jr,Kr,Zr,Da))}clampPoint(e,t){return t.copy(e).clamp(this.min,this.max)}distanceToPoint(e){return this.clampPoint(e,Kn).distanceTo(e)}getBoundingSphere(e){return this.isEmpty()?e.makeEmpty():(this.getCenter(e.center),e.radius=this.getSize(Kn).length()*.5),e}intersect(e){return this.min.max(e.min),this.max.min(e.max),this.isEmpty()&&this.makeEmpty(),this}union(e){return this.min.min(e.min),this.max.max(e.max),this}applyMatrix4(e){return this.isEmpty()?this:(bi[0].set(this.min.x,this.min.y,this.min.z).applyMatrix4(e),bi[1].set(this.min.x,this.min.y,this.max.z).applyMatrix4(e),bi[2].set(this.min.x,this.max.y,this.min.z).applyMatrix4(e),bi[3].set(this.min.x,this.max.y,this.max.z).applyMatrix4(e),bi[4].set(this.max.x,this.min.y,this.min.z).applyMatrix4(e),bi[5].set(this.max.x,this.min.y,this.max.z).applyMatrix4(e),bi[6].set(this.max.x,this.max.y,this.min.z).applyMatrix4(e),bi[7].set(this.max.x,this.max.y,this.max.z).applyMatrix4(e),this.setFromPoints(bi),this)}translate(e){return this.min.add(e),this.max.add(e),this}equals(e){return e.min.equals(this.min)&&e.max.equals(this.max)}}const bi=[new H,new H,new H,new H,new H,new H,new H,new H],Kn=new H,La=new xa,jr=new H,Kr=new H,Zr=new H,Gi=new H,Wi=new H,mr=new H,$s=new H,Da=new H,Ia=new H,gr=new H;function hl(i,e,t,n,r){for(let s=0,a=i.length-3;s<=a;s+=3){gr.fromArray(i,s);const o=r.x*Math.abs(gr.x)+r.y*Math.abs(gr.y)+r.z*Math.abs(gr.z),l=e.dot(gr),c=t.dot(gr),u=n.dot(gr);if(Math.max(-Math.max(l,c,u),Math.min(l,c,u))>o)return!1}return!0}const Jm=new xa,js=new H,dl=new H;class ya{constructor(e=new H,t=-1){this.isSphere=!0,this.center=e,this.radius=t}set(e,t){return this.center.copy(e),this.radius=t,this}setFromPoints(e,t){const n=this.center;t!==void 0?n.copy(t):Jm.setFromPoints(e).getCenter(n);let r=0;for(let s=0,a=e.length;s<a;s++)r=Math.max(r,n.distanceToSquared(e[s]));return this.radius=Math.sqrt(r),this}copy(e){return this.center.copy(e.center),this.radius=e.radius,this}isEmpty(){return this.radius<0}makeEmpty(){return this.center.set(0,0,0),this.radius=-1,this}containsPoint(e){return e.distanceToSquared(this.center)<=this.radius*this.radius}distanceToPoint(e){return e.distanceTo(this.center)-this.radius}intersectsSphere(e){const t=this.radius+e.radius;return e.center.distanceToSquared(this.center)<=t*t}intersectsBox(e){return e.intersectsSphere(this)}intersectsPlane(e){return Math.abs(e.distanceToPoint(this.center))<=this.radius}clampPoint(e,t){const n=this.center.distanceToSquared(e);return t.copy(e),n>this.radius*this.radius&&(t.sub(this.center).normalize(),t.multiplyScalar(this.radius).add(this.center)),t}getBoundingBox(e){return this.isEmpty()?(e.makeEmpty(),e):(e.set(this.center,this.center),e.expandByScalar(this.radius),e)}applyMatrix4(e){return this.center.applyMatrix4(e),this.radius=this.radius*e.getMaxScaleOnAxis(),this}translate(e){return this.center.add(e),this}expandByPoint(e){if(this.isEmpty())return this.center.copy(e),this.radius=0,this;js.subVectors(e,this.center);const t=js.lengthSq();if(t>this.radius*this.radius){const n=Math.sqrt(t),r=(n-this.radius)*.5;this.center.addScaledVector(js,r/n),this.radius+=r}return this}union(e){return e.isEmpty()?this:this.isEmpty()?(this.copy(e),this):(this.center.equals(e.center)===!0?this.radius=Math.max(this.radius,e.radius):(dl.subVectors(e.center,this.center).setLength(e.radius),this.expandByPoint(js.copy(e.center).add(dl)),this.expandByPoint(js.copy(e.center).sub(dl))),this)}equals(e){return e.center.equals(this.center)&&e.radius===this.radius}clone(){return new this.constructor().copy(this)}}const Ti=new H,fl=new H,Ua=new H,Xi=new H,pl=new H,Na=new H,ml=new H;class Ma{constructor(e=new H,t=new H(0,0,-1)){this.origin=e,this.direction=t}set(e,t){return this.origin.copy(e),this.direction.copy(t),this}copy(e){return this.origin.copy(e.origin),this.direction.copy(e.direction),this}at(e,t){return t.copy(this.origin).addScaledVector(this.direction,e)}lookAt(e){return this.direction.copy(e).sub(this.origin).normalize(),this}recast(e){return this.origin.copy(this.at(e,Ti)),this}closestPointToPoint(e,t){t.subVectors(e,this.origin);const n=t.dot(this.direction);return n<0?t.copy(this.origin):t.copy(this.origin).addScaledVector(this.direction,n)}distanceToPoint(e){return Math.sqrt(this.distanceSqToPoint(e))}distanceSqToPoint(e){const t=Ti.subVectors(e,this.origin).dot(this.direction);return t<0?this.origin.distanceToSquared(e):(Ti.copy(this.origin).addScaledVector(this.direction,t),Ti.distanceToSquared(e))}distanceSqToSegment(e,t,n,r){fl.copy(e).add(t).multiplyScalar(.5),Ua.copy(t).sub(e).normalize(),Xi.copy(this.origin).sub(fl);const s=e.distanceTo(t)*.5,a=-this.direction.dot(Ua),o=Xi.dot(this.direction),l=-Xi.dot(Ua),c=Xi.lengthSq(),u=Math.abs(1-a*a);let h,d,m,_;if(u>0)if(h=a*l-o,d=a*o-l,_=s*u,h>=0)if(d>=-_)if(d<=_){const v=1/u;h*=v,d*=v,m=h*(h+a*d+2*o)+d*(a*h+d+2*l)+c}else d=s,h=Math.max(0,-(a*d+o)),m=-h*h+d*(d+2*l)+c;else d=-s,h=Math.max(0,-(a*d+o)),m=-h*h+d*(d+2*l)+c;else d<=-_?(h=Math.max(0,-(-a*s+o)),d=h>0?-s:Math.min(Math.max(-s,-l),s),m=-h*h+d*(d+2*l)+c):d<=_?(h=0,d=Math.min(Math.max(-s,-l),s),m=d*(d+2*l)+c):(h=Math.max(0,-(a*s+o)),d=h>0?s:Math.min(Math.max(-s,-l),s),m=-h*h+d*(d+2*l)+c);else d=a>0?-s:s,h=Math.max(0,-(a*d+o)),m=-h*h+d*(d+2*l)+c;return n&&n.copy(this.origin).addScaledVector(this.direction,h),r&&r.copy(fl).addScaledVector(Ua,d),m}intersectSphere(e,t){Ti.subVectors(e.center,this.origin);const n=Ti.dot(this.direction),r=Ti.dot(Ti)-n*n,s=e.radius*e.radius;if(r>s)return null;const a=Math.sqrt(s-r),o=n-a,l=n+a;return l<0?null:o<0?this.at(l,t):this.at(o,t)}intersectsSphere(e){return this.distanceSqToPoint(e.center)<=e.radius*e.radius}distanceToPlane(e){const t=e.normal.dot(this.direction);if(t===0)return e.distanceToPoint(this.origin)===0?0:null;const n=-(this.origin.dot(e.normal)+e.constant)/t;return n>=0?n:null}intersectPlane(e,t){const n=this.distanceToPlane(e);return n===null?null:this.at(n,t)}intersectsPlane(e){const t=e.distanceToPoint(this.origin);return t===0||e.normal.dot(this.direction)*t<0}intersectBox(e,t){let n,r,s,a,o,l;const c=1/this.direction.x,u=1/this.direction.y,h=1/this.direction.z,d=this.origin;return c>=0?(n=(e.min.x-d.x)*c,r=(e.max.x-d.x)*c):(n=(e.max.x-d.x)*c,r=(e.min.x-d.x)*c),u>=0?(s=(e.min.y-d.y)*u,a=(e.max.y-d.y)*u):(s=(e.max.y-d.y)*u,a=(e.min.y-d.y)*u),n>a||s>r||((s>n||isNaN(n))&&(n=s),(a<r||isNaN(r))&&(r=a),h>=0?(o=(e.min.z-d.z)*h,l=(e.max.z-d.z)*h):(o=(e.max.z-d.z)*h,l=(e.min.z-d.z)*h),n>l||o>r)||((o>n||n!==n)&&(n=o),(l<r||r!==r)&&(r=l),r<0)?null:this.at(n>=0?n:r,t)}intersectsBox(e){return this.intersectBox(e,Ti)!==null}intersectTriangle(e,t,n,r,s){pl.subVectors(t,e),Na.subVectors(n,e),ml.crossVectors(pl,Na);let a=this.direction.dot(ml),o;if(a>0){if(r)return null;o=1}else if(a<0)o=-1,a=-a;else return null;Xi.subVectors(this.origin,e);const l=o*this.direction.dot(Na.crossVectors(Xi,Na));if(l<0)return null;const c=o*this.direction.dot(pl.cross(Xi));if(c<0||l+c>a)return null;const u=-o*Xi.dot(ml);return u<0?null:this.at(u/a,s)}applyMatrix4(e){return this.origin.applyMatrix4(e),this.direction.transformDirection(e),this}equals(e){return e.origin.equals(this.origin)&&e.direction.equals(this.direction)}clone(){return new this.constructor().copy(this)}}class Ft{constructor(e,t,n,r,s,a,o,l,c,u,h,d,m,_,v,p){Ft.prototype.isMatrix4=!0,this.elements=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],e!==void 0&&this.set(e,t,n,r,s,a,o,l,c,u,h,d,m,_,v,p)}set(e,t,n,r,s,a,o,l,c,u,h,d,m,_,v,p){const f=this.elements;return f[0]=e,f[4]=t,f[8]=n,f[12]=r,f[1]=s,f[5]=a,f[9]=o,f[13]=l,f[2]=c,f[6]=u,f[10]=h,f[14]=d,f[3]=m,f[7]=_,f[11]=v,f[15]=p,this}identity(){return this.set(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1),this}clone(){return new Ft().fromArray(this.elements)}copy(e){const t=this.elements,n=e.elements;return t[0]=n[0],t[1]=n[1],t[2]=n[2],t[3]=n[3],t[4]=n[4],t[5]=n[5],t[6]=n[6],t[7]=n[7],t[8]=n[8],t[9]=n[9],t[10]=n[10],t[11]=n[11],t[12]=n[12],t[13]=n[13],t[14]=n[14],t[15]=n[15],this}copyPosition(e){const t=this.elements,n=e.elements;return t[12]=n[12],t[13]=n[13],t[14]=n[14],this}setFromMatrix3(e){const t=e.elements;return this.set(t[0],t[3],t[6],0,t[1],t[4],t[7],0,t[2],t[5],t[8],0,0,0,0,1),this}extractBasis(e,t,n){return e.setFromMatrixColumn(this,0),t.setFromMatrixColumn(this,1),n.setFromMatrixColumn(this,2),this}makeBasis(e,t,n){return this.set(e.x,t.x,n.x,0,e.y,t.y,n.y,0,e.z,t.z,n.z,0,0,0,0,1),this}extractRotation(e){const t=this.elements,n=e.elements,r=1/Jr.setFromMatrixColumn(e,0).length(),s=1/Jr.setFromMatrixColumn(e,1).length(),a=1/Jr.setFromMatrixColumn(e,2).length();return t[0]=n[0]*r,t[1]=n[1]*r,t[2]=n[2]*r,t[3]=0,t[4]=n[4]*s,t[5]=n[5]*s,t[6]=n[6]*s,t[7]=0,t[8]=n[8]*a,t[9]=n[9]*a,t[10]=n[10]*a,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromEuler(e){const t=this.elements,n=e.x,r=e.y,s=e.z,a=Math.cos(n),o=Math.sin(n),l=Math.cos(r),c=Math.sin(r),u=Math.cos(s),h=Math.sin(s);if(e.order==="XYZ"){const d=a*u,m=a*h,_=o*u,v=o*h;t[0]=l*u,t[4]=-l*h,t[8]=c,t[1]=m+_*c,t[5]=d-v*c,t[9]=-o*l,t[2]=v-d*c,t[6]=_+m*c,t[10]=a*l}else if(e.order==="YXZ"){const d=l*u,m=l*h,_=c*u,v=c*h;t[0]=d+v*o,t[4]=_*o-m,t[8]=a*c,t[1]=a*h,t[5]=a*u,t[9]=-o,t[2]=m*o-_,t[6]=v+d*o,t[10]=a*l}else if(e.order==="ZXY"){const d=l*u,m=l*h,_=c*u,v=c*h;t[0]=d-v*o,t[4]=-a*h,t[8]=_+m*o,t[1]=m+_*o,t[5]=a*u,t[9]=v-d*o,t[2]=-a*c,t[6]=o,t[10]=a*l}else if(e.order==="ZYX"){const d=a*u,m=a*h,_=o*u,v=o*h;t[0]=l*u,t[4]=_*c-m,t[8]=d*c+v,t[1]=l*h,t[5]=v*c+d,t[9]=m*c-_,t[2]=-c,t[6]=o*l,t[10]=a*l}else if(e.order==="YZX"){const d=a*l,m=a*c,_=o*l,v=o*c;t[0]=l*u,t[4]=v-d*h,t[8]=_*h+m,t[1]=h,t[5]=a*u,t[9]=-o*u,t[2]=-c*u,t[6]=m*h+_,t[10]=d-v*h}else if(e.order==="XZY"){const d=a*l,m=a*c,_=o*l,v=o*c;t[0]=l*u,t[4]=-h,t[8]=c*u,t[1]=d*h+v,t[5]=a*u,t[9]=m*h-_,t[2]=_*h-m,t[6]=o*u,t[10]=v*h+d}return t[3]=0,t[7]=0,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromQuaternion(e){return this.compose(Qm,e,eg)}lookAt(e,t,n){const r=this.elements;return In.subVectors(e,t),In.lengthSq()===0&&(In.z=1),In.normalize(),qi.crossVectors(n,In),qi.lengthSq()===0&&(Math.abs(n.z)===1?In.x+=1e-4:In.z+=1e-4,In.normalize(),qi.crossVectors(n,In)),qi.normalize(),Fa.crossVectors(In,qi),r[0]=qi.x,r[4]=Fa.x,r[8]=In.x,r[1]=qi.y,r[5]=Fa.y,r[9]=In.y,r[2]=qi.z,r[6]=Fa.z,r[10]=In.z,this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){const n=e.elements,r=t.elements,s=this.elements,a=n[0],o=n[4],l=n[8],c=n[12],u=n[1],h=n[5],d=n[9],m=n[13],_=n[2],v=n[6],p=n[10],f=n[14],E=n[3],S=n[7],T=n[11],z=n[15],R=r[0],L=r[4],O=r[8],w=r[12],x=r[1],C=r[5],j=r[9],B=r[13],K=r[2],W=r[6],J=r[10],q=r[14],ee=r[3],me=r[7],he=r[11],ve=r[15];return s[0]=a*R+o*x+l*K+c*ee,s[4]=a*L+o*C+l*W+c*me,s[8]=a*O+o*j+l*J+c*he,s[12]=a*w+o*B+l*q+c*ve,s[1]=u*R+h*x+d*K+m*ee,s[5]=u*L+h*C+d*W+m*me,s[9]=u*O+h*j+d*J+m*he,s[13]=u*w+h*B+d*q+m*ve,s[2]=_*R+v*x+p*K+f*ee,s[6]=_*L+v*C+p*W+f*me,s[10]=_*O+v*j+p*J+f*he,s[14]=_*w+v*B+p*q+f*ve,s[3]=E*R+S*x+T*K+z*ee,s[7]=E*L+S*C+T*W+z*me,s[11]=E*O+S*j+T*J+z*he,s[15]=E*w+S*B+T*q+z*ve,this}multiplyScalar(e){const t=this.elements;return t[0]*=e,t[4]*=e,t[8]*=e,t[12]*=e,t[1]*=e,t[5]*=e,t[9]*=e,t[13]*=e,t[2]*=e,t[6]*=e,t[10]*=e,t[14]*=e,t[3]*=e,t[7]*=e,t[11]*=e,t[15]*=e,this}determinant(){const e=this.elements,t=e[0],n=e[4],r=e[8],s=e[12],a=e[1],o=e[5],l=e[9],c=e[13],u=e[2],h=e[6],d=e[10],m=e[14],_=e[3],v=e[7],p=e[11],f=e[15];return _*(+s*l*h-r*c*h-s*o*d+n*c*d+r*o*m-n*l*m)+v*(+t*l*m-t*c*d+s*a*d-r*a*m+r*c*u-s*l*u)+p*(+t*c*h-t*o*m-s*a*h+n*a*m+s*o*u-n*c*u)+f*(-r*o*u-t*l*h+t*o*d+r*a*h-n*a*d+n*l*u)}transpose(){const e=this.elements;let t;return t=e[1],e[1]=e[4],e[4]=t,t=e[2],e[2]=e[8],e[8]=t,t=e[6],e[6]=e[9],e[9]=t,t=e[3],e[3]=e[12],e[12]=t,t=e[7],e[7]=e[13],e[13]=t,t=e[11],e[11]=e[14],e[14]=t,this}setPosition(e,t,n){const r=this.elements;return e.isVector3?(r[12]=e.x,r[13]=e.y,r[14]=e.z):(r[12]=e,r[13]=t,r[14]=n),this}invert(){const e=this.elements,t=e[0],n=e[1],r=e[2],s=e[3],a=e[4],o=e[5],l=e[6],c=e[7],u=e[8],h=e[9],d=e[10],m=e[11],_=e[12],v=e[13],p=e[14],f=e[15],E=h*p*c-v*d*c+v*l*m-o*p*m-h*l*f+o*d*f,S=_*d*c-u*p*c-_*l*m+a*p*m+u*l*f-a*d*f,T=u*v*c-_*h*c+_*o*m-a*v*m-u*o*f+a*h*f,z=_*h*l-u*v*l-_*o*d+a*v*d+u*o*p-a*h*p,R=t*E+n*S+r*T+s*z;if(R===0)return this.set(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);const L=1/R;return e[0]=E*L,e[1]=(v*d*s-h*p*s-v*r*m+n*p*m+h*r*f-n*d*f)*L,e[2]=(o*p*s-v*l*s+v*r*c-n*p*c-o*r*f+n*l*f)*L,e[3]=(h*l*s-o*d*s-h*r*c+n*d*c+o*r*m-n*l*m)*L,e[4]=S*L,e[5]=(u*p*s-_*d*s+_*r*m-t*p*m-u*r*f+t*d*f)*L,e[6]=(_*l*s-a*p*s-_*r*c+t*p*c+a*r*f-t*l*f)*L,e[7]=(a*d*s-u*l*s+u*r*c-t*d*c-a*r*m+t*l*m)*L,e[8]=T*L,e[9]=(_*h*s-u*v*s-_*n*m+t*v*m+u*n*f-t*h*f)*L,e[10]=(a*v*s-_*o*s+_*n*c-t*v*c-a*n*f+t*o*f)*L,e[11]=(u*o*s-a*h*s-u*n*c+t*h*c+a*n*m-t*o*m)*L,e[12]=z*L,e[13]=(u*v*r-_*h*r+_*n*d-t*v*d-u*n*p+t*h*p)*L,e[14]=(_*o*r-a*v*r-_*n*l+t*v*l+a*n*p-t*o*p)*L,e[15]=(a*h*r-u*o*r+u*n*l-t*h*l-a*n*d+t*o*d)*L,this}scale(e){const t=this.elements,n=e.x,r=e.y,s=e.z;return t[0]*=n,t[4]*=r,t[8]*=s,t[1]*=n,t[5]*=r,t[9]*=s,t[2]*=n,t[6]*=r,t[10]*=s,t[3]*=n,t[7]*=r,t[11]*=s,this}getMaxScaleOnAxis(){const e=this.elements,t=e[0]*e[0]+e[1]*e[1]+e[2]*e[2],n=e[4]*e[4]+e[5]*e[5]+e[6]*e[6],r=e[8]*e[8]+e[9]*e[9]+e[10]*e[10];return Math.sqrt(Math.max(t,n,r))}makeTranslation(e,t,n){return e.isVector3?this.set(1,0,0,e.x,0,1,0,e.y,0,0,1,e.z,0,0,0,1):this.set(1,0,0,e,0,1,0,t,0,0,1,n,0,0,0,1),this}makeRotationX(e){const t=Math.cos(e),n=Math.sin(e);return this.set(1,0,0,0,0,t,-n,0,0,n,t,0,0,0,0,1),this}makeRotationY(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,0,n,0,0,1,0,0,-n,0,t,0,0,0,0,1),this}makeRotationZ(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,-n,0,0,n,t,0,0,0,0,1,0,0,0,0,1),this}makeRotationAxis(e,t){const n=Math.cos(t),r=Math.sin(t),s=1-n,a=e.x,o=e.y,l=e.z,c=s*a,u=s*o;return this.set(c*a+n,c*o-r*l,c*l+r*o,0,c*o+r*l,u*o+n,u*l-r*a,0,c*l-r*o,u*l+r*a,s*l*l+n,0,0,0,0,1),this}makeScale(e,t,n){return this.set(e,0,0,0,0,t,0,0,0,0,n,0,0,0,0,1),this}makeShear(e,t,n,r,s,a){return this.set(1,n,s,0,e,1,a,0,t,r,1,0,0,0,0,1),this}compose(e,t,n){const r=this.elements,s=t._x,a=t._y,o=t._z,l=t._w,c=s+s,u=a+a,h=o+o,d=s*c,m=s*u,_=s*h,v=a*u,p=a*h,f=o*h,E=l*c,S=l*u,T=l*h,z=n.x,R=n.y,L=n.z;return r[0]=(1-(v+f))*z,r[1]=(m+T)*z,r[2]=(_-S)*z,r[3]=0,r[4]=(m-T)*R,r[5]=(1-(d+f))*R,r[6]=(p+E)*R,r[7]=0,r[8]=(_+S)*L,r[9]=(p-E)*L,r[10]=(1-(d+v))*L,r[11]=0,r[12]=e.x,r[13]=e.y,r[14]=e.z,r[15]=1,this}decompose(e,t,n){const r=this.elements;let s=Jr.set(r[0],r[1],r[2]).length();const a=Jr.set(r[4],r[5],r[6]).length(),o=Jr.set(r[8],r[9],r[10]).length();this.determinant()<0&&(s=-s),e.x=r[12],e.y=r[13],e.z=r[14],Zn.copy(this);const c=1/s,u=1/a,h=1/o;return Zn.elements[0]*=c,Zn.elements[1]*=c,Zn.elements[2]*=c,Zn.elements[4]*=u,Zn.elements[5]*=u,Zn.elements[6]*=u,Zn.elements[8]*=h,Zn.elements[9]*=h,Zn.elements[10]*=h,t.setFromRotationMatrix(Zn),n.x=s,n.y=a,n.z=o,this}makePerspective(e,t,n,r,s,a,o=Di){const l=this.elements,c=2*s/(t-e),u=2*s/(n-r),h=(t+e)/(t-e),d=(n+r)/(n-r);let m,_;if(o===Di)m=-(a+s)/(a-s),_=-2*a*s/(a-s);else if(o===To)m=-a/(a-s),_=-a*s/(a-s);else throw new Error("THREE.Matrix4.makePerspective(): Invalid coordinate system: "+o);return l[0]=c,l[4]=0,l[8]=h,l[12]=0,l[1]=0,l[5]=u,l[9]=d,l[13]=0,l[2]=0,l[6]=0,l[10]=m,l[14]=_,l[3]=0,l[7]=0,l[11]=-1,l[15]=0,this}makeOrthographic(e,t,n,r,s,a,o=Di){const l=this.elements,c=1/(t-e),u=1/(n-r),h=1/(a-s),d=(t+e)*c,m=(n+r)*u;let _,v;if(o===Di)_=(a+s)*h,v=-2*h;else if(o===To)_=s*h,v=-1*h;else throw new Error("THREE.Matrix4.makeOrthographic(): Invalid coordinate system: "+o);return l[0]=2*c,l[4]=0,l[8]=0,l[12]=-d,l[1]=0,l[5]=2*u,l[9]=0,l[13]=-m,l[2]=0,l[6]=0,l[10]=v,l[14]=-_,l[3]=0,l[7]=0,l[11]=0,l[15]=1,this}equals(e){const t=this.elements,n=e.elements;for(let r=0;r<16;r++)if(t[r]!==n[r])return!1;return!0}fromArray(e,t=0){for(let n=0;n<16;n++)this.elements[n]=e[n+t];return this}toArray(e=[],t=0){const n=this.elements;return e[t]=n[0],e[t+1]=n[1],e[t+2]=n[2],e[t+3]=n[3],e[t+4]=n[4],e[t+5]=n[5],e[t+6]=n[6],e[t+7]=n[7],e[t+8]=n[8],e[t+9]=n[9],e[t+10]=n[10],e[t+11]=n[11],e[t+12]=n[12],e[t+13]=n[13],e[t+14]=n[14],e[t+15]=n[15],e}}const Jr=new H,Zn=new Ft,Qm=new H(0,0,0),eg=new H(1,1,1),qi=new H,Fa=new H,In=new H,Qu=new Ft,eh=new Dr;class _i{constructor(e=0,t=0,n=0,r=_i.DEFAULT_ORDER){this.isEuler=!0,this._x=e,this._y=t,this._z=n,this._order=r}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get order(){return this._order}set order(e){this._order=e,this._onChangeCallback()}set(e,t,n,r=this._order){return this._x=e,this._y=t,this._z=n,this._order=r,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._order)}copy(e){return this._x=e._x,this._y=e._y,this._z=e._z,this._order=e._order,this._onChangeCallback(),this}setFromRotationMatrix(e,t=this._order,n=!0){const r=e.elements,s=r[0],a=r[4],o=r[8],l=r[1],c=r[5],u=r[9],h=r[2],d=r[6],m=r[10];switch(t){case"XYZ":this._y=Math.asin(gn(o,-1,1)),Math.abs(o)<.9999999?(this._x=Math.atan2(-u,m),this._z=Math.atan2(-a,s)):(this._x=Math.atan2(d,c),this._z=0);break;case"YXZ":this._x=Math.asin(-gn(u,-1,1)),Math.abs(u)<.9999999?(this._y=Math.atan2(o,m),this._z=Math.atan2(l,c)):(this._y=Math.atan2(-h,s),this._z=0);break;case"ZXY":this._x=Math.asin(gn(d,-1,1)),Math.abs(d)<.9999999?(this._y=Math.atan2(-h,m),this._z=Math.atan2(-a,c)):(this._y=0,this._z=Math.atan2(l,s));break;case"ZYX":this._y=Math.asin(-gn(h,-1,1)),Math.abs(h)<.9999999?(this._x=Math.atan2(d,m),this._z=Math.atan2(l,s)):(this._x=0,this._z=Math.atan2(-a,c));break;case"YZX":this._z=Math.asin(gn(l,-1,1)),Math.abs(l)<.9999999?(this._x=Math.atan2(-u,c),this._y=Math.atan2(-h,s)):(this._x=0,this._y=Math.atan2(o,m));break;case"XZY":this._z=Math.asin(-gn(a,-1,1)),Math.abs(a)<.9999999?(this._x=Math.atan2(d,c),this._y=Math.atan2(o,s)):(this._x=Math.atan2(-u,m),this._y=0);break;default:console.warn("THREE.Euler: .setFromRotationMatrix() encountered an unknown order: "+t)}return this._order=t,n===!0&&this._onChangeCallback(),this}setFromQuaternion(e,t,n){return Qu.makeRotationFromQuaternion(e),this.setFromRotationMatrix(Qu,t,n)}setFromVector3(e,t=this._order){return this.set(e.x,e.y,e.z,t)}reorder(e){return eh.setFromEuler(this),this.setFromQuaternion(eh,e)}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._order===this._order}fromArray(e){return this._x=e[0],this._y=e[1],this._z=e[2],e[3]!==void 0&&(this._order=e[3]),this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._order,e}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._order}}_i.DEFAULT_ORDER="XYZ";class Kc{constructor(){this.mask=1}set(e){this.mask=(1<<e|0)>>>0}enable(e){this.mask|=1<<e|0}enableAll(){this.mask=-1}toggle(e){this.mask^=1<<e|0}disable(e){this.mask&=~(1<<e|0)}disableAll(){this.mask=0}test(e){return(this.mask&e.mask)!==0}isEnabled(e){return(this.mask&(1<<e|0))!==0}}let tg=0;const th=new H,Qr=new Dr,wi=new Ft,Oa=new H,Ks=new H,ng=new H,ig=new Dr,nh=new H(1,0,0),ih=new H(0,1,0),rh=new H(0,0,1),sh={type:"added"},rg={type:"removed"},es={type:"childadded",child:null},gl={type:"childremoved",child:null};class $t extends Us{constructor(){super(),this.isObject3D=!0,Object.defineProperty(this,"id",{value:tg++}),this.uuid=Ui(),this.name="",this.type="Object3D",this.parent=null,this.children=[],this.up=$t.DEFAULT_UP.clone();const e=new H,t=new _i,n=new Dr,r=new H(1,1,1);function s(){n.setFromEuler(t,!1)}function a(){t.setFromQuaternion(n,void 0,!1)}t._onChange(s),n._onChange(a),Object.defineProperties(this,{position:{configurable:!0,enumerable:!0,value:e},rotation:{configurable:!0,enumerable:!0,value:t},quaternion:{configurable:!0,enumerable:!0,value:n},scale:{configurable:!0,enumerable:!0,value:r},modelViewMatrix:{value:new Ft},normalMatrix:{value:new rt}}),this.matrix=new Ft,this.matrixWorld=new Ft,this.matrixAutoUpdate=$t.DEFAULT_MATRIX_AUTO_UPDATE,this.matrixWorldAutoUpdate=$t.DEFAULT_MATRIX_WORLD_AUTO_UPDATE,this.matrixWorldNeedsUpdate=!1,this.layers=new Kc,this.visible=!0,this.castShadow=!1,this.receiveShadow=!1,this.frustumCulled=!0,this.renderOrder=0,this.animations=[],this.userData={}}onBeforeShadow(){}onAfterShadow(){}onBeforeRender(){}onAfterRender(){}applyMatrix4(e){this.matrixAutoUpdate&&this.updateMatrix(),this.matrix.premultiply(e),this.matrix.decompose(this.position,this.quaternion,this.scale)}applyQuaternion(e){return this.quaternion.premultiply(e),this}setRotationFromAxisAngle(e,t){this.quaternion.setFromAxisAngle(e,t)}setRotationFromEuler(e){this.quaternion.setFromEuler(e,!0)}setRotationFromMatrix(e){this.quaternion.setFromRotationMatrix(e)}setRotationFromQuaternion(e){this.quaternion.copy(e)}rotateOnAxis(e,t){return Qr.setFromAxisAngle(e,t),this.quaternion.multiply(Qr),this}rotateOnWorldAxis(e,t){return Qr.setFromAxisAngle(e,t),this.quaternion.premultiply(Qr),this}rotateX(e){return this.rotateOnAxis(nh,e)}rotateY(e){return this.rotateOnAxis(ih,e)}rotateZ(e){return this.rotateOnAxis(rh,e)}translateOnAxis(e,t){return th.copy(e).applyQuaternion(this.quaternion),this.position.add(th.multiplyScalar(t)),this}translateX(e){return this.translateOnAxis(nh,e)}translateY(e){return this.translateOnAxis(ih,e)}translateZ(e){return this.translateOnAxis(rh,e)}localToWorld(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(this.matrixWorld)}worldToLocal(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(wi.copy(this.matrixWorld).invert())}lookAt(e,t,n){e.isVector3?Oa.copy(e):Oa.set(e,t,n);const r=this.parent;this.updateWorldMatrix(!0,!1),Ks.setFromMatrixPosition(this.matrixWorld),this.isCamera||this.isLight?wi.lookAt(Ks,Oa,this.up):wi.lookAt(Oa,Ks,this.up),this.quaternion.setFromRotationMatrix(wi),r&&(wi.extractRotation(r.matrixWorld),Qr.setFromRotationMatrix(wi),this.quaternion.premultiply(Qr.invert()))}add(e){if(arguments.length>1){for(let t=0;t<arguments.length;t++)this.add(arguments[t]);return this}return e===this?(console.error("THREE.Object3D.add: object can't be added as a child of itself.",e),this):(e&&e.isObject3D?(e.removeFromParent(),e.parent=this,this.children.push(e),e.dispatchEvent(sh),es.child=e,this.dispatchEvent(es),es.child=null):console.error("THREE.Object3D.add: object not an instance of THREE.Object3D.",e),this)}remove(e){if(arguments.length>1){for(let n=0;n<arguments.length;n++)this.remove(arguments[n]);return this}const t=this.children.indexOf(e);return t!==-1&&(e.parent=null,this.children.splice(t,1),e.dispatchEvent(rg),gl.child=e,this.dispatchEvent(gl),gl.child=null),this}removeFromParent(){const e=this.parent;return e!==null&&e.remove(this),this}clear(){return this.remove(...this.children)}attach(e){return this.updateWorldMatrix(!0,!1),wi.copy(this.matrixWorld).invert(),e.parent!==null&&(e.parent.updateWorldMatrix(!0,!1),wi.multiply(e.parent.matrixWorld)),e.applyMatrix4(wi),e.removeFromParent(),e.parent=this,this.children.push(e),e.updateWorldMatrix(!1,!0),e.dispatchEvent(sh),es.child=e,this.dispatchEvent(es),es.child=null,this}getObjectById(e){return this.getObjectByProperty("id",e)}getObjectByName(e){return this.getObjectByProperty("name",e)}getObjectByProperty(e,t){if(this[e]===t)return this;for(let n=0,r=this.children.length;n<r;n++){const a=this.children[n].getObjectByProperty(e,t);if(a!==void 0)return a}}getObjectsByProperty(e,t,n=[]){this[e]===t&&n.push(this);const r=this.children;for(let s=0,a=r.length;s<a;s++)r[s].getObjectsByProperty(e,t,n);return n}getWorldPosition(e){return this.updateWorldMatrix(!0,!1),e.setFromMatrixPosition(this.matrixWorld)}getWorldQuaternion(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(Ks,e,ng),e}getWorldScale(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(Ks,ig,e),e}getWorldDirection(e){this.updateWorldMatrix(!0,!1);const t=this.matrixWorld.elements;return e.set(t[8],t[9],t[10]).normalize()}raycast(){}traverse(e){e(this);const t=this.children;for(let n=0,r=t.length;n<r;n++)t[n].traverse(e)}traverseVisible(e){if(this.visible===!1)return;e(this);const t=this.children;for(let n=0,r=t.length;n<r;n++)t[n].traverseVisible(e)}traverseAncestors(e){const t=this.parent;t!==null&&(e(t),t.traverseAncestors(e))}updateMatrix(){this.matrix.compose(this.position,this.quaternion,this.scale),this.matrixWorldNeedsUpdate=!0}updateMatrixWorld(e){this.matrixAutoUpdate&&this.updateMatrix(),(this.matrixWorldNeedsUpdate||e)&&(this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),this.matrixWorldNeedsUpdate=!1,e=!0);const t=this.children;for(let n=0,r=t.length;n<r;n++)t[n].updateMatrixWorld(e)}updateWorldMatrix(e,t){const n=this.parent;if(e===!0&&n!==null&&n.updateWorldMatrix(!0,!1),this.matrixAutoUpdate&&this.updateMatrix(),this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),t===!0){const r=this.children;for(let s=0,a=r.length;s<a;s++)r[s].updateWorldMatrix(!1,!0)}}toJSON(e){const t=e===void 0||typeof e=="string",n={};t&&(e={geometries:{},materials:{},textures:{},images:{},shapes:{},skeletons:{},animations:{},nodes:{}},n.metadata={version:4.6,type:"Object",generator:"Object3D.toJSON"});const r={};r.uuid=this.uuid,r.type=this.type,this.name!==""&&(r.name=this.name),this.castShadow===!0&&(r.castShadow=!0),this.receiveShadow===!0&&(r.receiveShadow=!0),this.visible===!1&&(r.visible=!1),this.frustumCulled===!1&&(r.frustumCulled=!1),this.renderOrder!==0&&(r.renderOrder=this.renderOrder),Object.keys(this.userData).length>0&&(r.userData=this.userData),r.layers=this.layers.mask,r.matrix=this.matrix.toArray(),r.up=this.up.toArray(),this.matrixAutoUpdate===!1&&(r.matrixAutoUpdate=!1),this.isInstancedMesh&&(r.type="InstancedMesh",r.count=this.count,r.instanceMatrix=this.instanceMatrix.toJSON(),this.instanceColor!==null&&(r.instanceColor=this.instanceColor.toJSON())),this.isBatchedMesh&&(r.type="BatchedMesh",r.perObjectFrustumCulled=this.perObjectFrustumCulled,r.sortObjects=this.sortObjects,r.drawRanges=this._drawRanges,r.reservedRanges=this._reservedRanges,r.visibility=this._visibility,r.active=this._active,r.bounds=this._bounds.map(o=>({boxInitialized:o.boxInitialized,boxMin:o.box.min.toArray(),boxMax:o.box.max.toArray(),sphereInitialized:o.sphereInitialized,sphereRadius:o.sphere.radius,sphereCenter:o.sphere.center.toArray()})),r.maxInstanceCount=this._maxInstanceCount,r.maxVertexCount=this._maxVertexCount,r.maxIndexCount=this._maxIndexCount,r.geometryInitialized=this._geometryInitialized,r.geometryCount=this._geometryCount,r.matricesTexture=this._matricesTexture.toJSON(e),this._colorsTexture!==null&&(r.colorsTexture=this._colorsTexture.toJSON(e)),this.boundingSphere!==null&&(r.boundingSphere={center:r.boundingSphere.center.toArray(),radius:r.boundingSphere.radius}),this.boundingBox!==null&&(r.boundingBox={min:r.boundingBox.min.toArray(),max:r.boundingBox.max.toArray()}));function s(o,l){return o[l.uuid]===void 0&&(o[l.uuid]=l.toJSON(e)),l.uuid}if(this.isScene)this.background&&(this.background.isColor?r.background=this.background.toJSON():this.background.isTexture&&(r.background=this.background.toJSON(e).uuid)),this.environment&&this.environment.isTexture&&this.environment.isRenderTargetTexture!==!0&&(r.environment=this.environment.toJSON(e).uuid);else if(this.isMesh||this.isLine||this.isPoints){r.geometry=s(e.geometries,this.geometry);const o=this.geometry.parameters;if(o!==void 0&&o.shapes!==void 0){const l=o.shapes;if(Array.isArray(l))for(let c=0,u=l.length;c<u;c++){const h=l[c];s(e.shapes,h)}else s(e.shapes,l)}}if(this.isSkinnedMesh&&(r.bindMode=this.bindMode,r.bindMatrix=this.bindMatrix.toArray(),this.skeleton!==void 0&&(s(e.skeletons,this.skeleton),r.skeleton=this.skeleton.uuid)),this.material!==void 0)if(Array.isArray(this.material)){const o=[];for(let l=0,c=this.material.length;l<c;l++)o.push(s(e.materials,this.material[l]));r.material=o}else r.material=s(e.materials,this.material);if(this.children.length>0){r.children=[];for(let o=0;o<this.children.length;o++)r.children.push(this.children[o].toJSON(e).object)}if(this.animations.length>0){r.animations=[];for(let o=0;o<this.animations.length;o++){const l=this.animations[o];r.animations.push(s(e.animations,l))}}if(t){const o=a(e.geometries),l=a(e.materials),c=a(e.textures),u=a(e.images),h=a(e.shapes),d=a(e.skeletons),m=a(e.animations),_=a(e.nodes);o.length>0&&(n.geometries=o),l.length>0&&(n.materials=l),c.length>0&&(n.textures=c),u.length>0&&(n.images=u),h.length>0&&(n.shapes=h),d.length>0&&(n.skeletons=d),m.length>0&&(n.animations=m),_.length>0&&(n.nodes=_)}return n.object=r,n;function a(o){const l=[];for(const c in o){const u=o[c];delete u.metadata,l.push(u)}return l}}clone(e){return new this.constructor().copy(this,e)}copy(e,t=!0){if(this.name=e.name,this.up.copy(e.up),this.position.copy(e.position),this.rotation.order=e.rotation.order,this.quaternion.copy(e.quaternion),this.scale.copy(e.scale),this.matrix.copy(e.matrix),this.matrixWorld.copy(e.matrixWorld),this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrixWorldAutoUpdate=e.matrixWorldAutoUpdate,this.matrixWorldNeedsUpdate=e.matrixWorldNeedsUpdate,this.layers.mask=e.layers.mask,this.visible=e.visible,this.castShadow=e.castShadow,this.receiveShadow=e.receiveShadow,this.frustumCulled=e.frustumCulled,this.renderOrder=e.renderOrder,this.animations=e.animations.slice(),this.userData=JSON.parse(JSON.stringify(e.userData)),t===!0)for(let n=0;n<e.children.length;n++){const r=e.children[n];this.add(r.clone())}return this}}$t.DEFAULT_UP=new H(0,1,0);$t.DEFAULT_MATRIX_AUTO_UPDATE=!0;$t.DEFAULT_MATRIX_WORLD_AUTO_UPDATE=!0;const Jn=new H,Ai=new H,_l=new H,Ri=new H,ts=new H,ns=new H,ah=new H,vl=new H,xl=new H,yl=new H;class Wn{constructor(e=new H,t=new H,n=new H){this.a=e,this.b=t,this.c=n}static getNormal(e,t,n,r){r.subVectors(n,t),Jn.subVectors(e,t),r.cross(Jn);const s=r.lengthSq();return s>0?r.multiplyScalar(1/Math.sqrt(s)):r.set(0,0,0)}static getBarycoord(e,t,n,r,s){Jn.subVectors(r,t),Ai.subVectors(n,t),_l.subVectors(e,t);const a=Jn.dot(Jn),o=Jn.dot(Ai),l=Jn.dot(_l),c=Ai.dot(Ai),u=Ai.dot(_l),h=a*c-o*o;if(h===0)return s.set(0,0,0),null;const d=1/h,m=(c*l-o*u)*d,_=(a*u-o*l)*d;return s.set(1-m-_,_,m)}static containsPoint(e,t,n,r){return this.getBarycoord(e,t,n,r,Ri)===null?!1:Ri.x>=0&&Ri.y>=0&&Ri.x+Ri.y<=1}static getInterpolation(e,t,n,r,s,a,o,l){return this.getBarycoord(e,t,n,r,Ri)===null?(l.x=0,l.y=0,"z"in l&&(l.z=0),"w"in l&&(l.w=0),null):(l.setScalar(0),l.addScaledVector(s,Ri.x),l.addScaledVector(a,Ri.y),l.addScaledVector(o,Ri.z),l)}static isFrontFacing(e,t,n,r){return Jn.subVectors(n,t),Ai.subVectors(e,t),Jn.cross(Ai).dot(r)<0}set(e,t,n){return this.a.copy(e),this.b.copy(t),this.c.copy(n),this}setFromPointsAndIndices(e,t,n,r){return this.a.copy(e[t]),this.b.copy(e[n]),this.c.copy(e[r]),this}setFromAttributeAndIndices(e,t,n,r){return this.a.fromBufferAttribute(e,t),this.b.fromBufferAttribute(e,n),this.c.fromBufferAttribute(e,r),this}clone(){return new this.constructor().copy(this)}copy(e){return this.a.copy(e.a),this.b.copy(e.b),this.c.copy(e.c),this}getArea(){return Jn.subVectors(this.c,this.b),Ai.subVectors(this.a,this.b),Jn.cross(Ai).length()*.5}getMidpoint(e){return e.addVectors(this.a,this.b).add(this.c).multiplyScalar(1/3)}getNormal(e){return Wn.getNormal(this.a,this.b,this.c,e)}getPlane(e){return e.setFromCoplanarPoints(this.a,this.b,this.c)}getBarycoord(e,t){return Wn.getBarycoord(e,this.a,this.b,this.c,t)}getInterpolation(e,t,n,r,s){return Wn.getInterpolation(e,this.a,this.b,this.c,t,n,r,s)}containsPoint(e){return Wn.containsPoint(e,this.a,this.b,this.c)}isFrontFacing(e){return Wn.isFrontFacing(this.a,this.b,this.c,e)}intersectsBox(e){return e.intersectsTriangle(this)}closestPointToPoint(e,t){const n=this.a,r=this.b,s=this.c;let a,o;ts.subVectors(r,n),ns.subVectors(s,n),vl.subVectors(e,n);const l=ts.dot(vl),c=ns.dot(vl);if(l<=0&&c<=0)return t.copy(n);xl.subVectors(e,r);const u=ts.dot(xl),h=ns.dot(xl);if(u>=0&&h<=u)return t.copy(r);const d=l*h-u*c;if(d<=0&&l>=0&&u<=0)return a=l/(l-u),t.copy(n).addScaledVector(ts,a);yl.subVectors(e,s);const m=ts.dot(yl),_=ns.dot(yl);if(_>=0&&m<=_)return t.copy(s);const v=m*c-l*_;if(v<=0&&c>=0&&_<=0)return o=c/(c-_),t.copy(n).addScaledVector(ns,o);const p=u*_-m*h;if(p<=0&&h-u>=0&&m-_>=0)return ah.subVectors(s,r),o=(h-u)/(h-u+(m-_)),t.copy(r).addScaledVector(ah,o);const f=1/(p+v+d);return a=v*f,o=d*f,t.copy(n).addScaledVector(ts,a).addScaledVector(ns,o)}equals(e){return e.a.equals(this.a)&&e.b.equals(this.b)&&e.c.equals(this.c)}}const cf={aliceblue:15792383,antiquewhite:16444375,aqua:65535,aquamarine:8388564,azure:15794175,beige:16119260,bisque:16770244,black:0,blanchedalmond:16772045,blue:255,blueviolet:9055202,brown:10824234,burlywood:14596231,cadetblue:6266528,chartreuse:8388352,chocolate:13789470,coral:16744272,cornflowerblue:6591981,cornsilk:16775388,crimson:14423100,cyan:65535,darkblue:139,darkcyan:35723,darkgoldenrod:12092939,darkgray:11119017,darkgreen:25600,darkgrey:11119017,darkkhaki:12433259,darkmagenta:9109643,darkolivegreen:5597999,darkorange:16747520,darkorchid:10040012,darkred:9109504,darksalmon:15308410,darkseagreen:9419919,darkslateblue:4734347,darkslategray:3100495,darkslategrey:3100495,darkturquoise:52945,darkviolet:9699539,deeppink:16716947,deepskyblue:49151,dimgray:6908265,dimgrey:6908265,dodgerblue:2003199,firebrick:11674146,floralwhite:16775920,forestgreen:2263842,fuchsia:16711935,gainsboro:14474460,ghostwhite:16316671,gold:16766720,goldenrod:14329120,gray:8421504,green:32768,greenyellow:11403055,grey:8421504,honeydew:15794160,hotpink:16738740,indianred:13458524,indigo:4915330,ivory:16777200,khaki:15787660,lavender:15132410,lavenderblush:16773365,lawngreen:8190976,lemonchiffon:16775885,lightblue:11393254,lightcoral:15761536,lightcyan:14745599,lightgoldenrodyellow:16448210,lightgray:13882323,lightgreen:9498256,lightgrey:13882323,lightpink:16758465,lightsalmon:16752762,lightseagreen:2142890,lightskyblue:8900346,lightslategray:7833753,lightslategrey:7833753,lightsteelblue:11584734,lightyellow:16777184,lime:65280,limegreen:3329330,linen:16445670,magenta:16711935,maroon:8388608,mediumaquamarine:6737322,mediumblue:205,mediumorchid:12211667,mediumpurple:9662683,mediumseagreen:3978097,mediumslateblue:8087790,mediumspringgreen:64154,mediumturquoise:4772300,mediumvioletred:13047173,midnightblue:1644912,mintcream:16121850,mistyrose:16770273,moccasin:16770229,navajowhite:16768685,navy:128,oldlace:16643558,olive:8421376,olivedrab:7048739,orange:16753920,orangered:16729344,orchid:14315734,palegoldenrod:15657130,palegreen:10025880,paleturquoise:11529966,palevioletred:14381203,papayawhip:16773077,peachpuff:16767673,peru:13468991,pink:16761035,plum:14524637,powderblue:11591910,purple:8388736,rebeccapurple:6697881,red:16711680,rosybrown:12357519,royalblue:4286945,saddlebrown:9127187,salmon:16416882,sandybrown:16032864,seagreen:3050327,seashell:16774638,sienna:10506797,silver:12632256,skyblue:8900331,slateblue:6970061,slategray:7372944,slategrey:7372944,snow:16775930,springgreen:65407,steelblue:4620980,tan:13808780,teal:32896,thistle:14204888,tomato:16737095,turquoise:4251856,violet:15631086,wheat:16113331,white:16777215,whitesmoke:16119285,yellow:16776960,yellowgreen:10145074},Yi={h:0,s:0,l:0},Ba={h:0,s:0,l:0};function Ml(i,e,t){return t<0&&(t+=1),t>1&&(t-=1),t<1/6?i+(e-i)*6*t:t<1/2?e:t<2/3?i+(e-i)*6*(2/3-t):i}class tt{constructor(e,t,n){return this.isColor=!0,this.r=1,this.g=1,this.b=1,this.set(e,t,n)}set(e,t,n){if(t===void 0&&n===void 0){const r=e;r&&r.isColor?this.copy(r):typeof r=="number"?this.setHex(r):typeof r=="string"&&this.setStyle(r)}else this.setRGB(e,t,n);return this}setScalar(e){return this.r=e,this.g=e,this.b=e,this}setHex(e,t=pi){return e=Math.floor(e),this.r=(e>>16&255)/255,this.g=(e>>8&255)/255,this.b=(e&255)/255,Mt.toWorkingColorSpace(this,t),this}setRGB(e,t,n,r=Mt.workingColorSpace){return this.r=e,this.g=t,this.b=n,Mt.toWorkingColorSpace(this,r),this}setHSL(e,t,n,r=Mt.workingColorSpace){if(e=jc(e,1),t=gn(t,0,1),n=gn(n,0,1),t===0)this.r=this.g=this.b=n;else{const s=n<=.5?n*(1+t):n+t-n*t,a=2*n-s;this.r=Ml(a,s,e+1/3),this.g=Ml(a,s,e),this.b=Ml(a,s,e-1/3)}return Mt.toWorkingColorSpace(this,r),this}setStyle(e,t=pi){function n(s){s!==void 0&&parseFloat(s)<1&&console.warn("THREE.Color: Alpha component of "+e+" will be ignored.")}let r;if(r=/^(\w+)\(([^\)]*)\)/.exec(e)){let s;const a=r[1],o=r[2];switch(a){case"rgb":case"rgba":if(s=/^\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(o))return n(s[4]),this.setRGB(Math.min(255,parseInt(s[1],10))/255,Math.min(255,parseInt(s[2],10))/255,Math.min(255,parseInt(s[3],10))/255,t);if(s=/^\s*(\d+)\%\s*,\s*(\d+)\%\s*,\s*(\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(o))return n(s[4]),this.setRGB(Math.min(100,parseInt(s[1],10))/100,Math.min(100,parseInt(s[2],10))/100,Math.min(100,parseInt(s[3],10))/100,t);break;case"hsl":case"hsla":if(s=/^\s*(\d*\.?\d+)\s*,\s*(\d*\.?\d+)\%\s*,\s*(\d*\.?\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(o))return n(s[4]),this.setHSL(parseFloat(s[1])/360,parseFloat(s[2])/100,parseFloat(s[3])/100,t);break;default:console.warn("THREE.Color: Unknown color model "+e)}}else if(r=/^\#([A-Fa-f\d]+)$/.exec(e)){const s=r[1],a=s.length;if(a===3)return this.setRGB(parseInt(s.charAt(0),16)/15,parseInt(s.charAt(1),16)/15,parseInt(s.charAt(2),16)/15,t);if(a===6)return this.setHex(parseInt(s,16),t);console.warn("THREE.Color: Invalid hex color "+e)}else if(e&&e.length>0)return this.setColorName(e,t);return this}setColorName(e,t=pi){const n=cf[e.toLowerCase()];return n!==void 0?this.setHex(n,t):console.warn("THREE.Color: Unknown color "+e),this}clone(){return new this.constructor(this.r,this.g,this.b)}copy(e){return this.r=e.r,this.g=e.g,this.b=e.b,this}copySRGBToLinear(e){return this.r=Ms(e.r),this.g=Ms(e.g),this.b=Ms(e.b),this}copyLinearToSRGB(e){return this.r=ll(e.r),this.g=ll(e.g),this.b=ll(e.b),this}convertSRGBToLinear(){return this.copySRGBToLinear(this),this}convertLinearToSRGB(){return this.copyLinearToSRGB(this),this}getHex(e=pi){return Mt.fromWorkingColorSpace(mn.copy(this),e),Math.round(gn(mn.r*255,0,255))*65536+Math.round(gn(mn.g*255,0,255))*256+Math.round(gn(mn.b*255,0,255))}getHexString(e=pi){return("000000"+this.getHex(e).toString(16)).slice(-6)}getHSL(e,t=Mt.workingColorSpace){Mt.fromWorkingColorSpace(mn.copy(this),t);const n=mn.r,r=mn.g,s=mn.b,a=Math.max(n,r,s),o=Math.min(n,r,s);let l,c;const u=(o+a)/2;if(o===a)l=0,c=0;else{const h=a-o;switch(c=u<=.5?h/(a+o):h/(2-a-o),a){case n:l=(r-s)/h+(r<s?6:0);break;case r:l=(s-n)/h+2;break;case s:l=(n-r)/h+4;break}l/=6}return e.h=l,e.s=c,e.l=u,e}getRGB(e,t=Mt.workingColorSpace){return Mt.fromWorkingColorSpace(mn.copy(this),t),e.r=mn.r,e.g=mn.g,e.b=mn.b,e}getStyle(e=pi){Mt.fromWorkingColorSpace(mn.copy(this),e);const t=mn.r,n=mn.g,r=mn.b;return e!==pi?`color(${e} ${t.toFixed(3)} ${n.toFixed(3)} ${r.toFixed(3)})`:`rgb(${Math.round(t*255)},${Math.round(n*255)},${Math.round(r*255)})`}offsetHSL(e,t,n){return this.getHSL(Yi),this.setHSL(Yi.h+e,Yi.s+t,Yi.l+n)}add(e){return this.r+=e.r,this.g+=e.g,this.b+=e.b,this}addColors(e,t){return this.r=e.r+t.r,this.g=e.g+t.g,this.b=e.b+t.b,this}addScalar(e){return this.r+=e,this.g+=e,this.b+=e,this}sub(e){return this.r=Math.max(0,this.r-e.r),this.g=Math.max(0,this.g-e.g),this.b=Math.max(0,this.b-e.b),this}multiply(e){return this.r*=e.r,this.g*=e.g,this.b*=e.b,this}multiplyScalar(e){return this.r*=e,this.g*=e,this.b*=e,this}lerp(e,t){return this.r+=(e.r-this.r)*t,this.g+=(e.g-this.g)*t,this.b+=(e.b-this.b)*t,this}lerpColors(e,t,n){return this.r=e.r+(t.r-e.r)*n,this.g=e.g+(t.g-e.g)*n,this.b=e.b+(t.b-e.b)*n,this}lerpHSL(e,t){this.getHSL(Yi),e.getHSL(Ba);const n=ca(Yi.h,Ba.h,t),r=ca(Yi.s,Ba.s,t),s=ca(Yi.l,Ba.l,t);return this.setHSL(n,r,s),this}setFromVector3(e){return this.r=e.x,this.g=e.y,this.b=e.z,this}applyMatrix3(e){const t=this.r,n=this.g,r=this.b,s=e.elements;return this.r=s[0]*t+s[3]*n+s[6]*r,this.g=s[1]*t+s[4]*n+s[7]*r,this.b=s[2]*t+s[5]*n+s[8]*r,this}equals(e){return e.r===this.r&&e.g===this.g&&e.b===this.b}fromArray(e,t=0){return this.r=e[t],this.g=e[t+1],this.b=e[t+2],this}toArray(e=[],t=0){return e[t]=this.r,e[t+1]=this.g,e[t+2]=this.b,e}fromBufferAttribute(e,t){return this.r=e.getX(t),this.g=e.getY(t),this.b=e.getZ(t),this}toJSON(){return this.getHex()}*[Symbol.iterator](){yield this.r,yield this.g,yield this.b}}const mn=new tt;tt.NAMES=cf;let sg=0;class cr extends Us{constructor(){super(),this.isMaterial=!0,Object.defineProperty(this,"id",{value:sg++}),this.uuid=Ui(),this.name="",this.type="Material",this.blending=_s,this.side=ir,this.vertexColors=!1,this.opacity=1,this.transparent=!1,this.alphaHash=!1,this.blendSrc=ql,this.blendDst=Yl,this.blendEquation=br,this.blendSrcAlpha=null,this.blendDstAlpha=null,this.blendEquationAlpha=null,this.blendColor=new tt(0,0,0),this.blendAlpha=0,this.depthFunc=Mo,this.depthTest=!0,this.depthWrite=!0,this.stencilWriteMask=255,this.stencilFunc=qu,this.stencilRef=0,this.stencilFuncMask=255,this.stencilFail=Yr,this.stencilZFail=Yr,this.stencilZPass=Yr,this.stencilWrite=!1,this.clippingPlanes=null,this.clipIntersection=!1,this.clipShadows=!1,this.shadowSide=null,this.colorWrite=!0,this.precision=null,this.polygonOffset=!1,this.polygonOffsetFactor=0,this.polygonOffsetUnits=0,this.dithering=!1,this.alphaToCoverage=!1,this.premultipliedAlpha=!1,this.forceSinglePass=!1,this.visible=!0,this.toneMapped=!0,this.userData={},this.version=0,this._alphaTest=0}get alphaTest(){return this._alphaTest}set alphaTest(e){this._alphaTest>0!=e>0&&this.version++,this._alphaTest=e}onBeforeRender(){}onBeforeCompile(){}customProgramCacheKey(){return this.onBeforeCompile.toString()}setValues(e){if(e!==void 0)for(const t in e){const n=e[t];if(n===void 0){console.warn(`THREE.Material: parameter '${t}' has value of undefined.`);continue}const r=this[t];if(r===void 0){console.warn(`THREE.Material: '${t}' is not a property of THREE.${this.type}.`);continue}r&&r.isColor?r.set(n):r&&r.isVector3&&n&&n.isVector3?r.copy(n):this[t]=n}}toJSON(e){const t=e===void 0||typeof e=="string";t&&(e={textures:{},images:{}});const n={metadata:{version:4.6,type:"Material",generator:"Material.toJSON"}};n.uuid=this.uuid,n.type=this.type,this.name!==""&&(n.name=this.name),this.color&&this.color.isColor&&(n.color=this.color.getHex()),this.roughness!==void 0&&(n.roughness=this.roughness),this.metalness!==void 0&&(n.metalness=this.metalness),this.sheen!==void 0&&(n.sheen=this.sheen),this.sheenColor&&this.sheenColor.isColor&&(n.sheenColor=this.sheenColor.getHex()),this.sheenRoughness!==void 0&&(n.sheenRoughness=this.sheenRoughness),this.emissive&&this.emissive.isColor&&(n.emissive=this.emissive.getHex()),this.emissiveIntensity!==void 0&&this.emissiveIntensity!==1&&(n.emissiveIntensity=this.emissiveIntensity),this.specular&&this.specular.isColor&&(n.specular=this.specular.getHex()),this.specularIntensity!==void 0&&(n.specularIntensity=this.specularIntensity),this.specularColor&&this.specularColor.isColor&&(n.specularColor=this.specularColor.getHex()),this.shininess!==void 0&&(n.shininess=this.shininess),this.clearcoat!==void 0&&(n.clearcoat=this.clearcoat),this.clearcoatRoughness!==void 0&&(n.clearcoatRoughness=this.clearcoatRoughness),this.clearcoatMap&&this.clearcoatMap.isTexture&&(n.clearcoatMap=this.clearcoatMap.toJSON(e).uuid),this.clearcoatRoughnessMap&&this.clearcoatRoughnessMap.isTexture&&(n.clearcoatRoughnessMap=this.clearcoatRoughnessMap.toJSON(e).uuid),this.clearcoatNormalMap&&this.clearcoatNormalMap.isTexture&&(n.clearcoatNormalMap=this.clearcoatNormalMap.toJSON(e).uuid,n.clearcoatNormalScale=this.clearcoatNormalScale.toArray()),this.dispersion!==void 0&&(n.dispersion=this.dispersion),this.iridescence!==void 0&&(n.iridescence=this.iridescence),this.iridescenceIOR!==void 0&&(n.iridescenceIOR=this.iridescenceIOR),this.iridescenceThicknessRange!==void 0&&(n.iridescenceThicknessRange=this.iridescenceThicknessRange),this.iridescenceMap&&this.iridescenceMap.isTexture&&(n.iridescenceMap=this.iridescenceMap.toJSON(e).uuid),this.iridescenceThicknessMap&&this.iridescenceThicknessMap.isTexture&&(n.iridescenceThicknessMap=this.iridescenceThicknessMap.toJSON(e).uuid),this.anisotropy!==void 0&&(n.anisotropy=this.anisotropy),this.anisotropyRotation!==void 0&&(n.anisotropyRotation=this.anisotropyRotation),this.anisotropyMap&&this.anisotropyMap.isTexture&&(n.anisotropyMap=this.anisotropyMap.toJSON(e).uuid),this.map&&this.map.isTexture&&(n.map=this.map.toJSON(e).uuid),this.matcap&&this.matcap.isTexture&&(n.matcap=this.matcap.toJSON(e).uuid),this.alphaMap&&this.alphaMap.isTexture&&(n.alphaMap=this.alphaMap.toJSON(e).uuid),this.lightMap&&this.lightMap.isTexture&&(n.lightMap=this.lightMap.toJSON(e).uuid,n.lightMapIntensity=this.lightMapIntensity),this.aoMap&&this.aoMap.isTexture&&(n.aoMap=this.aoMap.toJSON(e).uuid,n.aoMapIntensity=this.aoMapIntensity),this.bumpMap&&this.bumpMap.isTexture&&(n.bumpMap=this.bumpMap.toJSON(e).uuid,n.bumpScale=this.bumpScale),this.normalMap&&this.normalMap.isTexture&&(n.normalMap=this.normalMap.toJSON(e).uuid,n.normalMapType=this.normalMapType,n.normalScale=this.normalScale.toArray()),this.displacementMap&&this.displacementMap.isTexture&&(n.displacementMap=this.displacementMap.toJSON(e).uuid,n.displacementScale=this.displacementScale,n.displacementBias=this.displacementBias),this.roughnessMap&&this.roughnessMap.isTexture&&(n.roughnessMap=this.roughnessMap.toJSON(e).uuid),this.metalnessMap&&this.metalnessMap.isTexture&&(n.metalnessMap=this.metalnessMap.toJSON(e).uuid),this.emissiveMap&&this.emissiveMap.isTexture&&(n.emissiveMap=this.emissiveMap.toJSON(e).uuid),this.specularMap&&this.specularMap.isTexture&&(n.specularMap=this.specularMap.toJSON(e).uuid),this.specularIntensityMap&&this.specularIntensityMap.isTexture&&(n.specularIntensityMap=this.specularIntensityMap.toJSON(e).uuid),this.specularColorMap&&this.specularColorMap.isTexture&&(n.specularColorMap=this.specularColorMap.toJSON(e).uuid),this.envMap&&this.envMap.isTexture&&(n.envMap=this.envMap.toJSON(e).uuid,this.combine!==void 0&&(n.combine=this.combine)),this.envMapRotation!==void 0&&(n.envMapRotation=this.envMapRotation.toArray()),this.envMapIntensity!==void 0&&(n.envMapIntensity=this.envMapIntensity),this.reflectivity!==void 0&&(n.reflectivity=this.reflectivity),this.refractionRatio!==void 0&&(n.refractionRatio=this.refractionRatio),this.gradientMap&&this.gradientMap.isTexture&&(n.gradientMap=this.gradientMap.toJSON(e).uuid),this.transmission!==void 0&&(n.transmission=this.transmission),this.transmissionMap&&this.transmissionMap.isTexture&&(n.transmissionMap=this.transmissionMap.toJSON(e).uuid),this.thickness!==void 0&&(n.thickness=this.thickness),this.thicknessMap&&this.thicknessMap.isTexture&&(n.thicknessMap=this.thicknessMap.toJSON(e).uuid),this.attenuationDistance!==void 0&&this.attenuationDistance!==1/0&&(n.attenuationDistance=this.attenuationDistance),this.attenuationColor!==void 0&&(n.attenuationColor=this.attenuationColor.getHex()),this.size!==void 0&&(n.size=this.size),this.shadowSide!==null&&(n.shadowSide=this.shadowSide),this.sizeAttenuation!==void 0&&(n.sizeAttenuation=this.sizeAttenuation),this.blending!==_s&&(n.blending=this.blending),this.side!==ir&&(n.side=this.side),this.vertexColors===!0&&(n.vertexColors=!0),this.opacity<1&&(n.opacity=this.opacity),this.transparent===!0&&(n.transparent=!0),this.blendSrc!==ql&&(n.blendSrc=this.blendSrc),this.blendDst!==Yl&&(n.blendDst=this.blendDst),this.blendEquation!==br&&(n.blendEquation=this.blendEquation),this.blendSrcAlpha!==null&&(n.blendSrcAlpha=this.blendSrcAlpha),this.blendDstAlpha!==null&&(n.blendDstAlpha=this.blendDstAlpha),this.blendEquationAlpha!==null&&(n.blendEquationAlpha=this.blendEquationAlpha),this.blendColor&&this.blendColor.isColor&&(n.blendColor=this.blendColor.getHex()),this.blendAlpha!==0&&(n.blendAlpha=this.blendAlpha),this.depthFunc!==Mo&&(n.depthFunc=this.depthFunc),this.depthTest===!1&&(n.depthTest=this.depthTest),this.depthWrite===!1&&(n.depthWrite=this.depthWrite),this.colorWrite===!1&&(n.colorWrite=this.colorWrite),this.stencilWriteMask!==255&&(n.stencilWriteMask=this.stencilWriteMask),this.stencilFunc!==qu&&(n.stencilFunc=this.stencilFunc),this.stencilRef!==0&&(n.stencilRef=this.stencilRef),this.stencilFuncMask!==255&&(n.stencilFuncMask=this.stencilFuncMask),this.stencilFail!==Yr&&(n.stencilFail=this.stencilFail),this.stencilZFail!==Yr&&(n.stencilZFail=this.stencilZFail),this.stencilZPass!==Yr&&(n.stencilZPass=this.stencilZPass),this.stencilWrite===!0&&(n.stencilWrite=this.stencilWrite),this.rotation!==void 0&&this.rotation!==0&&(n.rotation=this.rotation),this.polygonOffset===!0&&(n.polygonOffset=!0),this.polygonOffsetFactor!==0&&(n.polygonOffsetFactor=this.polygonOffsetFactor),this.polygonOffsetUnits!==0&&(n.polygonOffsetUnits=this.polygonOffsetUnits),this.linewidth!==void 0&&this.linewidth!==1&&(n.linewidth=this.linewidth),this.dashSize!==void 0&&(n.dashSize=this.dashSize),this.gapSize!==void 0&&(n.gapSize=this.gapSize),this.scale!==void 0&&(n.scale=this.scale),this.dithering===!0&&(n.dithering=!0),this.alphaTest>0&&(n.alphaTest=this.alphaTest),this.alphaHash===!0&&(n.alphaHash=!0),this.alphaToCoverage===!0&&(n.alphaToCoverage=!0),this.premultipliedAlpha===!0&&(n.premultipliedAlpha=!0),this.forceSinglePass===!0&&(n.forceSinglePass=!0),this.wireframe===!0&&(n.wireframe=!0),this.wireframeLinewidth>1&&(n.wireframeLinewidth=this.wireframeLinewidth),this.wireframeLinecap!=="round"&&(n.wireframeLinecap=this.wireframeLinecap),this.wireframeLinejoin!=="round"&&(n.wireframeLinejoin=this.wireframeLinejoin),this.flatShading===!0&&(n.flatShading=!0),this.visible===!1&&(n.visible=!1),this.toneMapped===!1&&(n.toneMapped=!1),this.fog===!1&&(n.fog=!1),Object.keys(this.userData).length>0&&(n.userData=this.userData);function r(s){const a=[];for(const o in s){const l=s[o];delete l.metadata,a.push(l)}return a}if(t){const s=r(e.textures),a=r(e.images);s.length>0&&(n.textures=s),a.length>0&&(n.images=a)}return n}clone(){return new this.constructor().copy(this)}copy(e){this.name=e.name,this.blending=e.blending,this.side=e.side,this.vertexColors=e.vertexColors,this.opacity=e.opacity,this.transparent=e.transparent,this.blendSrc=e.blendSrc,this.blendDst=e.blendDst,this.blendEquation=e.blendEquation,this.blendSrcAlpha=e.blendSrcAlpha,this.blendDstAlpha=e.blendDstAlpha,this.blendEquationAlpha=e.blendEquationAlpha,this.blendColor.copy(e.blendColor),this.blendAlpha=e.blendAlpha,this.depthFunc=e.depthFunc,this.depthTest=e.depthTest,this.depthWrite=e.depthWrite,this.stencilWriteMask=e.stencilWriteMask,this.stencilFunc=e.stencilFunc,this.stencilRef=e.stencilRef,this.stencilFuncMask=e.stencilFuncMask,this.stencilFail=e.stencilFail,this.stencilZFail=e.stencilZFail,this.stencilZPass=e.stencilZPass,this.stencilWrite=e.stencilWrite;const t=e.clippingPlanes;let n=null;if(t!==null){const r=t.length;n=new Array(r);for(let s=0;s!==r;++s)n[s]=t[s].clone()}return this.clippingPlanes=n,this.clipIntersection=e.clipIntersection,this.clipShadows=e.clipShadows,this.shadowSide=e.shadowSide,this.colorWrite=e.colorWrite,this.precision=e.precision,this.polygonOffset=e.polygonOffset,this.polygonOffsetFactor=e.polygonOffsetFactor,this.polygonOffsetUnits=e.polygonOffsetUnits,this.dithering=e.dithering,this.alphaTest=e.alphaTest,this.alphaHash=e.alphaHash,this.alphaToCoverage=e.alphaToCoverage,this.premultipliedAlpha=e.premultipliedAlpha,this.forceSinglePass=e.forceSinglePass,this.visible=e.visible,this.toneMapped=e.toneMapped,this.userData=JSON.parse(JSON.stringify(e.userData)),this}dispose(){this.dispatchEvent({type:"dispose"})}set needsUpdate(e){e===!0&&this.version++}onBuild(){console.warn("Material: onBuild() has been removed.")}}class ua extends cr{constructor(e){super(),this.isMeshBasicMaterial=!0,this.type="MeshBasicMaterial",this.color=new tt(16777215),this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.specularMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new _i,this.combine=Wd,this.reflectivity=1,this.refractionRatio=.98,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.lightMap=e.lightMap,this.lightMapIntensity=e.lightMapIntensity,this.aoMap=e.aoMap,this.aoMapIntensity=e.aoMapIntensity,this.specularMap=e.specularMap,this.alphaMap=e.alphaMap,this.envMap=e.envMap,this.envMapRotation.copy(e.envMapRotation),this.combine=e.combine,this.reflectivity=e.reflectivity,this.refractionRatio=e.refractionRatio,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.wireframeLinecap=e.wireframeLinecap,this.wireframeLinejoin=e.wireframeLinejoin,this.fog=e.fog,this}}const Xt=new H,za=new Xe;class si{constructor(e,t,n=!1){if(Array.isArray(e))throw new TypeError("THREE.BufferAttribute: array should be a Typed Array.");this.isBufferAttribute=!0,this.name="",this.array=e,this.itemSize=t,this.count=e!==void 0?e.length/t:0,this.normalized=n,this.usage=bc,this._updateRange={offset:0,count:-1},this.updateRanges=[],this.gpuType=Li,this.version=0}onUploadCallback(){}set needsUpdate(e){e===!0&&this.version++}get updateRange(){return ys("THREE.BufferAttribute: updateRange() is deprecated and will be removed in r169. Use addUpdateRange() instead."),this._updateRange}setUsage(e){return this.usage=e,this}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}copy(e){return this.name=e.name,this.array=new e.array.constructor(e.array),this.itemSize=e.itemSize,this.count=e.count,this.normalized=e.normalized,this.usage=e.usage,this.gpuType=e.gpuType,this}copyAt(e,t,n){e*=this.itemSize,n*=t.itemSize;for(let r=0,s=this.itemSize;r<s;r++)this.array[e+r]=t.array[n+r];return this}copyArray(e){return this.array.set(e),this}applyMatrix3(e){if(this.itemSize===2)for(let t=0,n=this.count;t<n;t++)za.fromBufferAttribute(this,t),za.applyMatrix3(e),this.setXY(t,za.x,za.y);else if(this.itemSize===3)for(let t=0,n=this.count;t<n;t++)Xt.fromBufferAttribute(this,t),Xt.applyMatrix3(e),this.setXYZ(t,Xt.x,Xt.y,Xt.z);return this}applyMatrix4(e){for(let t=0,n=this.count;t<n;t++)Xt.fromBufferAttribute(this,t),Xt.applyMatrix4(e),this.setXYZ(t,Xt.x,Xt.y,Xt.z);return this}applyNormalMatrix(e){for(let t=0,n=this.count;t<n;t++)Xt.fromBufferAttribute(this,t),Xt.applyNormalMatrix(e),this.setXYZ(t,Xt.x,Xt.y,Xt.z);return this}transformDirection(e){for(let t=0,n=this.count;t<n;t++)Xt.fromBufferAttribute(this,t),Xt.transformDirection(e),this.setXYZ(t,Xt.x,Xt.y,Xt.z);return this}set(e,t=0){return this.array.set(e,t),this}getComponent(e,t){let n=this.array[e*this.itemSize+t];return this.normalized&&(n=ni(n,this.array)),n}setComponent(e,t,n){return this.normalized&&(n=bt(n,this.array)),this.array[e*this.itemSize+t]=n,this}getX(e){let t=this.array[e*this.itemSize];return this.normalized&&(t=ni(t,this.array)),t}setX(e,t){return this.normalized&&(t=bt(t,this.array)),this.array[e*this.itemSize]=t,this}getY(e){let t=this.array[e*this.itemSize+1];return this.normalized&&(t=ni(t,this.array)),t}setY(e,t){return this.normalized&&(t=bt(t,this.array)),this.array[e*this.itemSize+1]=t,this}getZ(e){let t=this.array[e*this.itemSize+2];return this.normalized&&(t=ni(t,this.array)),t}setZ(e,t){return this.normalized&&(t=bt(t,this.array)),this.array[e*this.itemSize+2]=t,this}getW(e){let t=this.array[e*this.itemSize+3];return this.normalized&&(t=ni(t,this.array)),t}setW(e,t){return this.normalized&&(t=bt(t,this.array)),this.array[e*this.itemSize+3]=t,this}setXY(e,t,n){return e*=this.itemSize,this.normalized&&(t=bt(t,this.array),n=bt(n,this.array)),this.array[e+0]=t,this.array[e+1]=n,this}setXYZ(e,t,n,r){return e*=this.itemSize,this.normalized&&(t=bt(t,this.array),n=bt(n,this.array),r=bt(r,this.array)),this.array[e+0]=t,this.array[e+1]=n,this.array[e+2]=r,this}setXYZW(e,t,n,r,s){return e*=this.itemSize,this.normalized&&(t=bt(t,this.array),n=bt(n,this.array),r=bt(r,this.array),s=bt(s,this.array)),this.array[e+0]=t,this.array[e+1]=n,this.array[e+2]=r,this.array[e+3]=s,this}onUpload(e){return this.onUploadCallback=e,this}clone(){return new this.constructor(this.array,this.itemSize).copy(this)}toJSON(){const e={itemSize:this.itemSize,type:this.array.constructor.name,array:Array.from(this.array),normalized:this.normalized};return this.name!==""&&(e.name=this.name),this.usage!==bc&&(e.usage=this.usage),e}}class uf extends si{constructor(e,t,n){super(new Uint16Array(e),t,n)}}class hf extends si{constructor(e,t,n){super(new Uint32Array(e),t,n)}}class vn extends si{constructor(e,t,n){super(new Float32Array(e),t,n)}}let ag=0;const Hn=new Ft,Sl=new $t,is=new H,Un=new xa,Zs=new xa,on=new H;class ln extends Us{constructor(){super(),this.isBufferGeometry=!0,Object.defineProperty(this,"id",{value:ag++}),this.uuid=Ui(),this.name="",this.type="BufferGeometry",this.index=null,this.attributes={},this.morphAttributes={},this.morphTargetsRelative=!1,this.groups=[],this.boundingBox=null,this.boundingSphere=null,this.drawRange={start:0,count:1/0},this.userData={}}getIndex(){return this.index}setIndex(e){return Array.isArray(e)?this.index=new(af(e)?hf:uf)(e,1):this.index=e,this}getAttribute(e){return this.attributes[e]}setAttribute(e,t){return this.attributes[e]=t,this}deleteAttribute(e){return delete this.attributes[e],this}hasAttribute(e){return this.attributes[e]!==void 0}addGroup(e,t,n=0){this.groups.push({start:e,count:t,materialIndex:n})}clearGroups(){this.groups=[]}setDrawRange(e,t){this.drawRange.start=e,this.drawRange.count=t}applyMatrix4(e){const t=this.attributes.position;t!==void 0&&(t.applyMatrix4(e),t.needsUpdate=!0);const n=this.attributes.normal;if(n!==void 0){const s=new rt().getNormalMatrix(e);n.applyNormalMatrix(s),n.needsUpdate=!0}const r=this.attributes.tangent;return r!==void 0&&(r.transformDirection(e),r.needsUpdate=!0),this.boundingBox!==null&&this.computeBoundingBox(),this.boundingSphere!==null&&this.computeBoundingSphere(),this}applyQuaternion(e){return Hn.makeRotationFromQuaternion(e),this.applyMatrix4(Hn),this}rotateX(e){return Hn.makeRotationX(e),this.applyMatrix4(Hn),this}rotateY(e){return Hn.makeRotationY(e),this.applyMatrix4(Hn),this}rotateZ(e){return Hn.makeRotationZ(e),this.applyMatrix4(Hn),this}translate(e,t,n){return Hn.makeTranslation(e,t,n),this.applyMatrix4(Hn),this}scale(e,t,n){return Hn.makeScale(e,t,n),this.applyMatrix4(Hn),this}lookAt(e){return Sl.lookAt(e),Sl.updateMatrix(),this.applyMatrix4(Sl.matrix),this}center(){return this.computeBoundingBox(),this.boundingBox.getCenter(is).negate(),this.translate(is.x,is.y,is.z),this}setFromPoints(e){const t=[];for(let n=0,r=e.length;n<r;n++){const s=e[n];t.push(s.x,s.y,s.z||0)}return this.setAttribute("position",new vn(t,3)),this}computeBoundingBox(){this.boundingBox===null&&(this.boundingBox=new xa);const e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingBox(): GLBufferAttribute requires a manual bounding box.",this),this.boundingBox.set(new H(-1/0,-1/0,-1/0),new H(1/0,1/0,1/0));return}if(e!==void 0){if(this.boundingBox.setFromBufferAttribute(e),t)for(let n=0,r=t.length;n<r;n++){const s=t[n];Un.setFromBufferAttribute(s),this.morphTargetsRelative?(on.addVectors(this.boundingBox.min,Un.min),this.boundingBox.expandByPoint(on),on.addVectors(this.boundingBox.max,Un.max),this.boundingBox.expandByPoint(on)):(this.boundingBox.expandByPoint(Un.min),this.boundingBox.expandByPoint(Un.max))}}else this.boundingBox.makeEmpty();(isNaN(this.boundingBox.min.x)||isNaN(this.boundingBox.min.y)||isNaN(this.boundingBox.min.z))&&console.error('THREE.BufferGeometry.computeBoundingBox(): Computed min/max have NaN values. The "position" attribute is likely to have NaN values.',this)}computeBoundingSphere(){this.boundingSphere===null&&(this.boundingSphere=new ya);const e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingSphere(): GLBufferAttribute requires a manual bounding sphere.",this),this.boundingSphere.set(new H,1/0);return}if(e){const n=this.boundingSphere.center;if(Un.setFromBufferAttribute(e),t)for(let s=0,a=t.length;s<a;s++){const o=t[s];Zs.setFromBufferAttribute(o),this.morphTargetsRelative?(on.addVectors(Un.min,Zs.min),Un.expandByPoint(on),on.addVectors(Un.max,Zs.max),Un.expandByPoint(on)):(Un.expandByPoint(Zs.min),Un.expandByPoint(Zs.max))}Un.getCenter(n);let r=0;for(let s=0,a=e.count;s<a;s++)on.fromBufferAttribute(e,s),r=Math.max(r,n.distanceToSquared(on));if(t)for(let s=0,a=t.length;s<a;s++){const o=t[s],l=this.morphTargetsRelative;for(let c=0,u=o.count;c<u;c++)on.fromBufferAttribute(o,c),l&&(is.fromBufferAttribute(e,c),on.add(is)),r=Math.max(r,n.distanceToSquared(on))}this.boundingSphere.radius=Math.sqrt(r),isNaN(this.boundingSphere.radius)&&console.error('THREE.BufferGeometry.computeBoundingSphere(): Computed radius is NaN. The "position" attribute is likely to have NaN values.',this)}}computeTangents(){const e=this.index,t=this.attributes;if(e===null||t.position===void 0||t.normal===void 0||t.uv===void 0){console.error("THREE.BufferGeometry: .computeTangents() failed. Missing required attributes (index, position, normal or uv)");return}const n=t.position,r=t.normal,s=t.uv;this.hasAttribute("tangent")===!1&&this.setAttribute("tangent",new si(new Float32Array(4*n.count),4));const a=this.getAttribute("tangent"),o=[],l=[];for(let O=0;O<n.count;O++)o[O]=new H,l[O]=new H;const c=new H,u=new H,h=new H,d=new Xe,m=new Xe,_=new Xe,v=new H,p=new H;function f(O,w,x){c.fromBufferAttribute(n,O),u.fromBufferAttribute(n,w),h.fromBufferAttribute(n,x),d.fromBufferAttribute(s,O),m.fromBufferAttribute(s,w),_.fromBufferAttribute(s,x),u.sub(c),h.sub(c),m.sub(d),_.sub(d);const C=1/(m.x*_.y-_.x*m.y);isFinite(C)&&(v.copy(u).multiplyScalar(_.y).addScaledVector(h,-m.y).multiplyScalar(C),p.copy(h).multiplyScalar(m.x).addScaledVector(u,-_.x).multiplyScalar(C),o[O].add(v),o[w].add(v),o[x].add(v),l[O].add(p),l[w].add(p),l[x].add(p))}let E=this.groups;E.length===0&&(E=[{start:0,count:e.count}]);for(let O=0,w=E.length;O<w;++O){const x=E[O],C=x.start,j=x.count;for(let B=C,K=C+j;B<K;B+=3)f(e.getX(B+0),e.getX(B+1),e.getX(B+2))}const S=new H,T=new H,z=new H,R=new H;function L(O){z.fromBufferAttribute(r,O),R.copy(z);const w=o[O];S.copy(w),S.sub(z.multiplyScalar(z.dot(w))).normalize(),T.crossVectors(R,w);const C=T.dot(l[O])<0?-1:1;a.setXYZW(O,S.x,S.y,S.z,C)}for(let O=0,w=E.length;O<w;++O){const x=E[O],C=x.start,j=x.count;for(let B=C,K=C+j;B<K;B+=3)L(e.getX(B+0)),L(e.getX(B+1)),L(e.getX(B+2))}}computeVertexNormals(){const e=this.index,t=this.getAttribute("position");if(t!==void 0){let n=this.getAttribute("normal");if(n===void 0)n=new si(new Float32Array(t.count*3),3),this.setAttribute("normal",n);else for(let d=0,m=n.count;d<m;d++)n.setXYZ(d,0,0,0);const r=new H,s=new H,a=new H,o=new H,l=new H,c=new H,u=new H,h=new H;if(e)for(let d=0,m=e.count;d<m;d+=3){const _=e.getX(d+0),v=e.getX(d+1),p=e.getX(d+2);r.fromBufferAttribute(t,_),s.fromBufferAttribute(t,v),a.fromBufferAttribute(t,p),u.subVectors(a,s),h.subVectors(r,s),u.cross(h),o.fromBufferAttribute(n,_),l.fromBufferAttribute(n,v),c.fromBufferAttribute(n,p),o.add(u),l.add(u),c.add(u),n.setXYZ(_,o.x,o.y,o.z),n.setXYZ(v,l.x,l.y,l.z),n.setXYZ(p,c.x,c.y,c.z)}else for(let d=0,m=t.count;d<m;d+=3)r.fromBufferAttribute(t,d+0),s.fromBufferAttribute(t,d+1),a.fromBufferAttribute(t,d+2),u.subVectors(a,s),h.subVectors(r,s),u.cross(h),n.setXYZ(d+0,u.x,u.y,u.z),n.setXYZ(d+1,u.x,u.y,u.z),n.setXYZ(d+2,u.x,u.y,u.z);this.normalizeNormals(),n.needsUpdate=!0}}normalizeNormals(){const e=this.attributes.normal;for(let t=0,n=e.count;t<n;t++)on.fromBufferAttribute(e,t),on.normalize(),e.setXYZ(t,on.x,on.y,on.z)}toNonIndexed(){function e(o,l){const c=o.array,u=o.itemSize,h=o.normalized,d=new c.constructor(l.length*u);let m=0,_=0;for(let v=0,p=l.length;v<p;v++){o.isInterleavedBufferAttribute?m=l[v]*o.data.stride+o.offset:m=l[v]*u;for(let f=0;f<u;f++)d[_++]=c[m++]}return new si(d,u,h)}if(this.index===null)return console.warn("THREE.BufferGeometry.toNonIndexed(): BufferGeometry is already non-indexed."),this;const t=new ln,n=this.index.array,r=this.attributes;for(const o in r){const l=r[o],c=e(l,n);t.setAttribute(o,c)}const s=this.morphAttributes;for(const o in s){const l=[],c=s[o];for(let u=0,h=c.length;u<h;u++){const d=c[u],m=e(d,n);l.push(m)}t.morphAttributes[o]=l}t.morphTargetsRelative=this.morphTargetsRelative;const a=this.groups;for(let o=0,l=a.length;o<l;o++){const c=a[o];t.addGroup(c.start,c.count,c.materialIndex)}return t}toJSON(){const e={metadata:{version:4.6,type:"BufferGeometry",generator:"BufferGeometry.toJSON"}};if(e.uuid=this.uuid,e.type=this.type,this.name!==""&&(e.name=this.name),Object.keys(this.userData).length>0&&(e.userData=this.userData),this.parameters!==void 0){const l=this.parameters;for(const c in l)l[c]!==void 0&&(e[c]=l[c]);return e}e.data={attributes:{}};const t=this.index;t!==null&&(e.data.index={type:t.array.constructor.name,array:Array.prototype.slice.call(t.array)});const n=this.attributes;for(const l in n){const c=n[l];e.data.attributes[l]=c.toJSON(e.data)}const r={};let s=!1;for(const l in this.morphAttributes){const c=this.morphAttributes[l],u=[];for(let h=0,d=c.length;h<d;h++){const m=c[h];u.push(m.toJSON(e.data))}u.length>0&&(r[l]=u,s=!0)}s&&(e.data.morphAttributes=r,e.data.morphTargetsRelative=this.morphTargetsRelative);const a=this.groups;a.length>0&&(e.data.groups=JSON.parse(JSON.stringify(a)));const o=this.boundingSphere;return o!==null&&(e.data.boundingSphere={center:o.center.toArray(),radius:o.radius}),e}clone(){return new this.constructor().copy(this)}copy(e){this.index=null,this.attributes={},this.morphAttributes={},this.groups=[],this.boundingBox=null,this.boundingSphere=null;const t={};this.name=e.name;const n=e.index;n!==null&&this.setIndex(n.clone(t));const r=e.attributes;for(const c in r){const u=r[c];this.setAttribute(c,u.clone(t))}const s=e.morphAttributes;for(const c in s){const u=[],h=s[c];for(let d=0,m=h.length;d<m;d++)u.push(h[d].clone(t));this.morphAttributes[c]=u}this.morphTargetsRelative=e.morphTargetsRelative;const a=e.groups;for(let c=0,u=a.length;c<u;c++){const h=a[c];this.addGroup(h.start,h.count,h.materialIndex)}const o=e.boundingBox;o!==null&&(this.boundingBox=o.clone());const l=e.boundingSphere;return l!==null&&(this.boundingSphere=l.clone()),this.drawRange.start=e.drawRange.start,this.drawRange.count=e.drawRange.count,this.userData=e.userData,this}dispose(){this.dispatchEvent({type:"dispose"})}}const oh=new Ft,_r=new Ma,ka=new ya,lh=new H,rs=new H,ss=new H,as=new H,El=new H,Ha=new H,Va=new Xe,Ga=new Xe,Wa=new Xe,ch=new H,uh=new H,hh=new H,Xa=new H,qa=new H;class Tn extends $t{constructor(e=new ln,t=new ua){super(),this.isMesh=!0,this.type="Mesh",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),e.morphTargetInfluences!==void 0&&(this.morphTargetInfluences=e.morphTargetInfluences.slice()),e.morphTargetDictionary!==void 0&&(this.morphTargetDictionary=Object.assign({},e.morphTargetDictionary)),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const r=t[n[0]];if(r!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let s=0,a=r.length;s<a;s++){const o=r[s].name||String(s);this.morphTargetInfluences.push(0),this.morphTargetDictionary[o]=s}}}}getVertexPosition(e,t){const n=this.geometry,r=n.attributes.position,s=n.morphAttributes.position,a=n.morphTargetsRelative;t.fromBufferAttribute(r,e);const o=this.morphTargetInfluences;if(s&&o){Ha.set(0,0,0);for(let l=0,c=s.length;l<c;l++){const u=o[l],h=s[l];u!==0&&(El.fromBufferAttribute(h,e),a?Ha.addScaledVector(El,u):Ha.addScaledVector(El.sub(t),u))}t.add(Ha)}return t}raycast(e,t){const n=this.geometry,r=this.material,s=this.matrixWorld;r!==void 0&&(n.boundingSphere===null&&n.computeBoundingSphere(),ka.copy(n.boundingSphere),ka.applyMatrix4(s),_r.copy(e.ray).recast(e.near),!(ka.containsPoint(_r.origin)===!1&&(_r.intersectSphere(ka,lh)===null||_r.origin.distanceToSquared(lh)>(e.far-e.near)**2))&&(oh.copy(s).invert(),_r.copy(e.ray).applyMatrix4(oh),!(n.boundingBox!==null&&_r.intersectsBox(n.boundingBox)===!1)&&this._computeIntersections(e,t,_r)))}_computeIntersections(e,t,n){let r;const s=this.geometry,a=this.material,o=s.index,l=s.attributes.position,c=s.attributes.uv,u=s.attributes.uv1,h=s.attributes.normal,d=s.groups,m=s.drawRange;if(o!==null)if(Array.isArray(a))for(let _=0,v=d.length;_<v;_++){const p=d[_],f=a[p.materialIndex],E=Math.max(p.start,m.start),S=Math.min(o.count,Math.min(p.start+p.count,m.start+m.count));for(let T=E,z=S;T<z;T+=3){const R=o.getX(T),L=o.getX(T+1),O=o.getX(T+2);r=Ya(this,f,e,n,c,u,h,R,L,O),r&&(r.faceIndex=Math.floor(T/3),r.face.materialIndex=p.materialIndex,t.push(r))}}else{const _=Math.max(0,m.start),v=Math.min(o.count,m.start+m.count);for(let p=_,f=v;p<f;p+=3){const E=o.getX(p),S=o.getX(p+1),T=o.getX(p+2);r=Ya(this,a,e,n,c,u,h,E,S,T),r&&(r.faceIndex=Math.floor(p/3),t.push(r))}}else if(l!==void 0)if(Array.isArray(a))for(let _=0,v=d.length;_<v;_++){const p=d[_],f=a[p.materialIndex],E=Math.max(p.start,m.start),S=Math.min(l.count,Math.min(p.start+p.count,m.start+m.count));for(let T=E,z=S;T<z;T+=3){const R=T,L=T+1,O=T+2;r=Ya(this,f,e,n,c,u,h,R,L,O),r&&(r.faceIndex=Math.floor(T/3),r.face.materialIndex=p.materialIndex,t.push(r))}}else{const _=Math.max(0,m.start),v=Math.min(l.count,m.start+m.count);for(let p=_,f=v;p<f;p+=3){const E=p,S=p+1,T=p+2;r=Ya(this,a,e,n,c,u,h,E,S,T),r&&(r.faceIndex=Math.floor(p/3),t.push(r))}}}}function og(i,e,t,n,r,s,a,o){let l;if(e.side===Cn?l=n.intersectTriangle(a,s,r,!0,o):l=n.intersectTriangle(r,s,a,e.side===ir,o),l===null)return null;qa.copy(o),qa.applyMatrix4(i.matrixWorld);const c=t.ray.origin.distanceTo(qa);return c<t.near||c>t.far?null:{distance:c,point:qa.clone(),object:i}}function Ya(i,e,t,n,r,s,a,o,l,c){i.getVertexPosition(o,rs),i.getVertexPosition(l,ss),i.getVertexPosition(c,as);const u=og(i,e,t,n,rs,ss,as,Xa);if(u){r&&(Va.fromBufferAttribute(r,o),Ga.fromBufferAttribute(r,l),Wa.fromBufferAttribute(r,c),u.uv=Wn.getInterpolation(Xa,rs,ss,as,Va,Ga,Wa,new Xe)),s&&(Va.fromBufferAttribute(s,o),Ga.fromBufferAttribute(s,l),Wa.fromBufferAttribute(s,c),u.uv1=Wn.getInterpolation(Xa,rs,ss,as,Va,Ga,Wa,new Xe)),a&&(ch.fromBufferAttribute(a,o),uh.fromBufferAttribute(a,l),hh.fromBufferAttribute(a,c),u.normal=Wn.getInterpolation(Xa,rs,ss,as,ch,uh,hh,new H),u.normal.dot(n.direction)>0&&u.normal.multiplyScalar(-1));const h={a:o,b:l,c,normal:new H,materialIndex:0};Wn.getNormal(rs,ss,as,h.normal),u.face=h}return u}class Ii extends ln{constructor(e=1,t=1,n=1,r=1,s=1,a=1){super(),this.type="BoxGeometry",this.parameters={width:e,height:t,depth:n,widthSegments:r,heightSegments:s,depthSegments:a};const o=this;r=Math.floor(r),s=Math.floor(s),a=Math.floor(a);const l=[],c=[],u=[],h=[];let d=0,m=0;_("z","y","x",-1,-1,n,t,e,a,s,0),_("z","y","x",1,-1,n,t,-e,a,s,1),_("x","z","y",1,1,e,n,t,r,a,2),_("x","z","y",1,-1,e,n,-t,r,a,3),_("x","y","z",1,-1,e,t,n,r,s,4),_("x","y","z",-1,-1,e,t,-n,r,s,5),this.setIndex(l),this.setAttribute("position",new vn(c,3)),this.setAttribute("normal",new vn(u,3)),this.setAttribute("uv",new vn(h,2));function _(v,p,f,E,S,T,z,R,L,O,w){const x=T/L,C=z/O,j=T/2,B=z/2,K=R/2,W=L+1,J=O+1;let q=0,ee=0;const me=new H;for(let he=0;he<J;he++){const ve=he*C-B;for(let Te=0;Te<W;Te++){const xe=Te*x-j;me[v]=xe*E,me[p]=ve*S,me[f]=K,c.push(me.x,me.y,me.z),me[v]=0,me[p]=0,me[f]=R>0?1:-1,u.push(me.x,me.y,me.z),h.push(Te/L),h.push(1-he/O),q+=1}}for(let he=0;he<O;he++)for(let ve=0;ve<L;ve++){const Te=d+ve+W*he,xe=d+ve+W*(he+1),te=d+(ve+1)+W*(he+1),ce=d+(ve+1)+W*he;l.push(Te,xe,ce),l.push(xe,te,ce),ee+=6}o.addGroup(m,ee,w),m+=ee,d+=q}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Ii(e.width,e.height,e.depth,e.widthSegments,e.heightSegments,e.depthSegments)}}function Rs(i){const e={};for(const t in i){e[t]={};for(const n in i[t]){const r=i[t][n];r&&(r.isColor||r.isMatrix3||r.isMatrix4||r.isVector2||r.isVector3||r.isVector4||r.isTexture||r.isQuaternion)?r.isRenderTargetTexture?(console.warn("UniformsUtils: Textures of render targets cannot be cloned via cloneUniforms() or mergeUniforms()."),e[t][n]=null):e[t][n]=r.clone():Array.isArray(r)?e[t][n]=r.slice():e[t][n]=r}}return e}function bn(i){const e={};for(let t=0;t<i.length;t++){const n=Rs(i[t]);for(const r in n)e[r]=n[r]}return e}function lg(i){const e=[];for(let t=0;t<i.length;t++)e.push(i[t].clone());return e}function df(i){const e=i.getRenderTarget();return e===null?i.outputColorSpace:e.isXRRenderTarget===!0?e.texture.colorSpace:Mt.workingColorSpace}const cg={clone:Rs,merge:bn};var ug=`void main() {
	gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
}`,hg=`void main() {
	gl_FragColor = vec4( 1.0, 0.0, 0.0, 1.0 );
}`;class rr extends cr{constructor(e){super(),this.isShaderMaterial=!0,this.type="ShaderMaterial",this.defines={},this.uniforms={},this.uniformsGroups=[],this.vertexShader=ug,this.fragmentShader=hg,this.linewidth=1,this.wireframe=!1,this.wireframeLinewidth=1,this.fog=!1,this.lights=!1,this.clipping=!1,this.forceSinglePass=!0,this.extensions={clipCullDistance:!1,multiDraw:!1},this.defaultAttributeValues={color:[1,1,1],uv:[0,0],uv1:[0,0]},this.index0AttributeName=void 0,this.uniformsNeedUpdate=!1,this.glslVersion=null,e!==void 0&&this.setValues(e)}copy(e){return super.copy(e),this.fragmentShader=e.fragmentShader,this.vertexShader=e.vertexShader,this.uniforms=Rs(e.uniforms),this.uniformsGroups=lg(e.uniformsGroups),this.defines=Object.assign({},e.defines),this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.fog=e.fog,this.lights=e.lights,this.clipping=e.clipping,this.extensions=Object.assign({},e.extensions),this.glslVersion=e.glslVersion,this}toJSON(e){const t=super.toJSON(e);t.glslVersion=this.glslVersion,t.uniforms={};for(const r in this.uniforms){const a=this.uniforms[r].value;a&&a.isTexture?t.uniforms[r]={type:"t",value:a.toJSON(e).uuid}:a&&a.isColor?t.uniforms[r]={type:"c",value:a.getHex()}:a&&a.isVector2?t.uniforms[r]={type:"v2",value:a.toArray()}:a&&a.isVector3?t.uniforms[r]={type:"v3",value:a.toArray()}:a&&a.isVector4?t.uniforms[r]={type:"v4",value:a.toArray()}:a&&a.isMatrix3?t.uniforms[r]={type:"m3",value:a.toArray()}:a&&a.isMatrix4?t.uniforms[r]={type:"m4",value:a.toArray()}:t.uniforms[r]={value:a}}Object.keys(this.defines).length>0&&(t.defines=this.defines),t.vertexShader=this.vertexShader,t.fragmentShader=this.fragmentShader,t.lights=this.lights,t.clipping=this.clipping;const n={};for(const r in this.extensions)this.extensions[r]===!0&&(n[r]=!0);return Object.keys(n).length>0&&(t.extensions=n),t}}class ff extends $t{constructor(){super(),this.isCamera=!0,this.type="Camera",this.matrixWorldInverse=new Ft,this.projectionMatrix=new Ft,this.projectionMatrixInverse=new Ft,this.coordinateSystem=Di}copy(e,t){return super.copy(e,t),this.matrixWorldInverse.copy(e.matrixWorldInverse),this.projectionMatrix.copy(e.projectionMatrix),this.projectionMatrixInverse.copy(e.projectionMatrixInverse),this.coordinateSystem=e.coordinateSystem,this}getWorldDirection(e){return super.getWorldDirection(e).negate()}updateMatrixWorld(e){super.updateMatrixWorld(e),this.matrixWorldInverse.copy(this.matrixWorld).invert()}updateWorldMatrix(e,t){super.updateWorldMatrix(e,t),this.matrixWorldInverse.copy(this.matrixWorld).invert()}clone(){return new this.constructor().copy(this)}}const $i=new H,dh=new Xe,fh=new Xe;class _n extends ff{constructor(e=50,t=1,n=.1,r=2e3){super(),this.isPerspectiveCamera=!0,this.type="PerspectiveCamera",this.fov=e,this.zoom=1,this.near=n,this.far=r,this.focus=10,this.aspect=t,this.view=null,this.filmGauge=35,this.filmOffset=0,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.fov=e.fov,this.zoom=e.zoom,this.near=e.near,this.far=e.far,this.focus=e.focus,this.aspect=e.aspect,this.view=e.view===null?null:Object.assign({},e.view),this.filmGauge=e.filmGauge,this.filmOffset=e.filmOffset,this}setFocalLength(e){const t=.5*this.getFilmHeight()/e;this.fov=ga*2*Math.atan(t),this.updateProjectionMatrix()}getFocalLength(){const e=Math.tan(xs*.5*this.fov);return .5*this.getFilmHeight()/e}getEffectiveFOV(){return ga*2*Math.atan(Math.tan(xs*.5*this.fov)/this.zoom)}getFilmWidth(){return this.filmGauge*Math.min(this.aspect,1)}getFilmHeight(){return this.filmGauge/Math.max(this.aspect,1)}getViewBounds(e,t,n){$i.set(-1,-1,.5).applyMatrix4(this.projectionMatrixInverse),t.set($i.x,$i.y).multiplyScalar(-e/$i.z),$i.set(1,1,.5).applyMatrix4(this.projectionMatrixInverse),n.set($i.x,$i.y).multiplyScalar(-e/$i.z)}getViewSize(e,t){return this.getViewBounds(e,dh,fh),t.subVectors(fh,dh)}setViewOffset(e,t,n,r,s,a){this.aspect=e/t,this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=n,this.view.offsetY=r,this.view.width=s,this.view.height=a,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const e=this.near;let t=e*Math.tan(xs*.5*this.fov)/this.zoom,n=2*t,r=this.aspect*n,s=-.5*r;const a=this.view;if(this.view!==null&&this.view.enabled){const l=a.fullWidth,c=a.fullHeight;s+=a.offsetX*r/l,t-=a.offsetY*n/c,r*=a.width/l,n*=a.height/c}const o=this.filmOffset;o!==0&&(s+=e*o/this.getFilmWidth()),this.projectionMatrix.makePerspective(s,s+r,t,t-n,e,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){const t=super.toJSON(e);return t.object.fov=this.fov,t.object.zoom=this.zoom,t.object.near=this.near,t.object.far=this.far,t.object.focus=this.focus,t.object.aspect=this.aspect,this.view!==null&&(t.object.view=Object.assign({},this.view)),t.object.filmGauge=this.filmGauge,t.object.filmOffset=this.filmOffset,t}}const os=-90,ls=1;class dg extends $t{constructor(e,t,n){super(),this.type="CubeCamera",this.renderTarget=n,this.coordinateSystem=null,this.activeMipmapLevel=0;const r=new _n(os,ls,e,t);r.layers=this.layers,this.add(r);const s=new _n(os,ls,e,t);s.layers=this.layers,this.add(s);const a=new _n(os,ls,e,t);a.layers=this.layers,this.add(a);const o=new _n(os,ls,e,t);o.layers=this.layers,this.add(o);const l=new _n(os,ls,e,t);l.layers=this.layers,this.add(l);const c=new _n(os,ls,e,t);c.layers=this.layers,this.add(c)}updateCoordinateSystem(){const e=this.coordinateSystem,t=this.children.concat(),[n,r,s,a,o,l]=t;for(const c of t)this.remove(c);if(e===Di)n.up.set(0,1,0),n.lookAt(1,0,0),r.up.set(0,1,0),r.lookAt(-1,0,0),s.up.set(0,0,-1),s.lookAt(0,1,0),a.up.set(0,0,1),a.lookAt(0,-1,0),o.up.set(0,1,0),o.lookAt(0,0,1),l.up.set(0,1,0),l.lookAt(0,0,-1);else if(e===To)n.up.set(0,-1,0),n.lookAt(-1,0,0),r.up.set(0,-1,0),r.lookAt(1,0,0),s.up.set(0,0,1),s.lookAt(0,1,0),a.up.set(0,0,-1),a.lookAt(0,-1,0),o.up.set(0,-1,0),o.lookAt(0,0,1),l.up.set(0,-1,0),l.lookAt(0,0,-1);else throw new Error("THREE.CubeCamera.updateCoordinateSystem(): Invalid coordinate system: "+e);for(const c of t)this.add(c),c.updateMatrixWorld()}update(e,t){this.parent===null&&this.updateMatrixWorld();const{renderTarget:n,activeMipmapLevel:r}=this;this.coordinateSystem!==e.coordinateSystem&&(this.coordinateSystem=e.coordinateSystem,this.updateCoordinateSystem());const[s,a,o,l,c,u]=this.children,h=e.getRenderTarget(),d=e.getActiveCubeFace(),m=e.getActiveMipmapLevel(),_=e.xr.enabled;e.xr.enabled=!1;const v=n.texture.generateMipmaps;n.texture.generateMipmaps=!1,e.setRenderTarget(n,0,r),e.render(t,s),e.setRenderTarget(n,1,r),e.render(t,a),e.setRenderTarget(n,2,r),e.render(t,o),e.setRenderTarget(n,3,r),e.render(t,l),e.setRenderTarget(n,4,r),e.render(t,c),n.texture.generateMipmaps=v,e.setRenderTarget(n,5,r),e.render(t,u),e.setRenderTarget(h,d,m),e.xr.enabled=_,n.texture.needsPMREMUpdate=!0}}class pf extends An{constructor(e,t,n,r,s,a,o,l,c,u){e=e!==void 0?e:[],t=t!==void 0?t:bs,super(e,t,n,r,s,a,o,l,c,u),this.isCubeTexture=!0,this.flipY=!1}get images(){return this.image}set images(e){this.image=e}}class fg extends Lr{constructor(e=1,t={}){super(e,e,t),this.isWebGLCubeRenderTarget=!0;const n={width:e,height:e,depth:1},r=[n,n,n,n,n,n];this.texture=new pf(r,t.mapping,t.wrapS,t.wrapT,t.magFilter,t.minFilter,t.format,t.type,t.anisotropy,t.colorSpace),this.texture.isRenderTargetTexture=!0,this.texture.generateMipmaps=t.generateMipmaps!==void 0?t.generateMipmaps:!1,this.texture.minFilter=t.minFilter!==void 0?t.minFilter:ti}fromEquirectangularTexture(e,t){this.texture.type=t.type,this.texture.colorSpace=t.colorSpace,this.texture.generateMipmaps=t.generateMipmaps,this.texture.minFilter=t.minFilter,this.texture.magFilter=t.magFilter;const n={uniforms:{tEquirect:{value:null}},vertexShader:`

				varying vec3 vWorldDirection;

				vec3 transformDirection( in vec3 dir, in mat4 matrix ) {

					return normalize( ( matrix * vec4( dir, 0.0 ) ).xyz );

				}

				void main() {

					vWorldDirection = transformDirection( position, modelMatrix );

					#include <begin_vertex>
					#include <project_vertex>

				}
			`,fragmentShader:`

				uniform sampler2D tEquirect;

				varying vec3 vWorldDirection;

				#include <common>

				void main() {

					vec3 direction = normalize( vWorldDirection );

					vec2 sampleUV = equirectUv( direction );

					gl_FragColor = texture2D( tEquirect, sampleUV );

				}
			`},r=new Ii(5,5,5),s=new rr({name:"CubemapFromEquirect",uniforms:Rs(n.uniforms),vertexShader:n.vertexShader,fragmentShader:n.fragmentShader,side:Cn,blending:Qi});s.uniforms.tEquirect.value=t;const a=new Tn(r,s),o=t.minFilter;return t.minFilter===Rr&&(t.minFilter=ti),new dg(1,10,this).update(e,a),t.minFilter=o,a.geometry.dispose(),a.material.dispose(),this}clear(e,t,n,r){const s=e.getRenderTarget();for(let a=0;a<6;a++)e.setRenderTarget(this,a),e.clear(t,n,r);e.setRenderTarget(s)}}const bl=new H,pg=new H,mg=new rt;class Ki{constructor(e=new H(1,0,0),t=0){this.isPlane=!0,this.normal=e,this.constant=t}set(e,t){return this.normal.copy(e),this.constant=t,this}setComponents(e,t,n,r){return this.normal.set(e,t,n),this.constant=r,this}setFromNormalAndCoplanarPoint(e,t){return this.normal.copy(e),this.constant=-t.dot(this.normal),this}setFromCoplanarPoints(e,t,n){const r=bl.subVectors(n,t).cross(pg.subVectors(e,t)).normalize();return this.setFromNormalAndCoplanarPoint(r,e),this}copy(e){return this.normal.copy(e.normal),this.constant=e.constant,this}normalize(){const e=1/this.normal.length();return this.normal.multiplyScalar(e),this.constant*=e,this}negate(){return this.constant*=-1,this.normal.negate(),this}distanceToPoint(e){return this.normal.dot(e)+this.constant}distanceToSphere(e){return this.distanceToPoint(e.center)-e.radius}projectPoint(e,t){return t.copy(e).addScaledVector(this.normal,-this.distanceToPoint(e))}intersectLine(e,t){const n=e.delta(bl),r=this.normal.dot(n);if(r===0)return this.distanceToPoint(e.start)===0?t.copy(e.start):null;const s=-(e.start.dot(this.normal)+this.constant)/r;return s<0||s>1?null:t.copy(e.start).addScaledVector(n,s)}intersectsLine(e){const t=this.distanceToPoint(e.start),n=this.distanceToPoint(e.end);return t<0&&n>0||n<0&&t>0}intersectsBox(e){return e.intersectsPlane(this)}intersectsSphere(e){return e.intersectsPlane(this)}coplanarPoint(e){return e.copy(this.normal).multiplyScalar(-this.constant)}applyMatrix4(e,t){const n=t||mg.getNormalMatrix(e),r=this.coplanarPoint(bl).applyMatrix4(e),s=this.normal.applyMatrix3(n).normalize();return this.constant=-r.dot(s),this}translate(e){return this.constant-=e.dot(this.normal),this}equals(e){return e.normal.equals(this.normal)&&e.constant===this.constant}clone(){return new this.constructor().copy(this)}}const vr=new ya,$a=new H;class Zc{constructor(e=new Ki,t=new Ki,n=new Ki,r=new Ki,s=new Ki,a=new Ki){this.planes=[e,t,n,r,s,a]}set(e,t,n,r,s,a){const o=this.planes;return o[0].copy(e),o[1].copy(t),o[2].copy(n),o[3].copy(r),o[4].copy(s),o[5].copy(a),this}copy(e){const t=this.planes;for(let n=0;n<6;n++)t[n].copy(e.planes[n]);return this}setFromProjectionMatrix(e,t=Di){const n=this.planes,r=e.elements,s=r[0],a=r[1],o=r[2],l=r[3],c=r[4],u=r[5],h=r[6],d=r[7],m=r[8],_=r[9],v=r[10],p=r[11],f=r[12],E=r[13],S=r[14],T=r[15];if(n[0].setComponents(l-s,d-c,p-m,T-f).normalize(),n[1].setComponents(l+s,d+c,p+m,T+f).normalize(),n[2].setComponents(l+a,d+u,p+_,T+E).normalize(),n[3].setComponents(l-a,d-u,p-_,T-E).normalize(),n[4].setComponents(l-o,d-h,p-v,T-S).normalize(),t===Di)n[5].setComponents(l+o,d+h,p+v,T+S).normalize();else if(t===To)n[5].setComponents(o,h,v,S).normalize();else throw new Error("THREE.Frustum.setFromProjectionMatrix(): Invalid coordinate system: "+t);return this}intersectsObject(e){if(e.boundingSphere!==void 0)e.boundingSphere===null&&e.computeBoundingSphere(),vr.copy(e.boundingSphere).applyMatrix4(e.matrixWorld);else{const t=e.geometry;t.boundingSphere===null&&t.computeBoundingSphere(),vr.copy(t.boundingSphere).applyMatrix4(e.matrixWorld)}return this.intersectsSphere(vr)}intersectsSprite(e){return vr.center.set(0,0,0),vr.radius=.7071067811865476,vr.applyMatrix4(e.matrixWorld),this.intersectsSphere(vr)}intersectsSphere(e){const t=this.planes,n=e.center,r=-e.radius;for(let s=0;s<6;s++)if(t[s].distanceToPoint(n)<r)return!1;return!0}intersectsBox(e){const t=this.planes;for(let n=0;n<6;n++){const r=t[n];if($a.x=r.normal.x>0?e.max.x:e.min.x,$a.y=r.normal.y>0?e.max.y:e.min.y,$a.z=r.normal.z>0?e.max.z:e.min.z,r.distanceToPoint($a)<0)return!1}return!0}containsPoint(e){const t=this.planes;for(let n=0;n<6;n++)if(t[n].distanceToPoint(e)<0)return!1;return!0}clone(){return new this.constructor().copy(this)}}function mf(){let i=null,e=!1,t=null,n=null;function r(s,a){t(s,a),n=i.requestAnimationFrame(r)}return{start:function(){e!==!0&&t!==null&&(n=i.requestAnimationFrame(r),e=!0)},stop:function(){i.cancelAnimationFrame(n),e=!1},setAnimationLoop:function(s){t=s},setContext:function(s){i=s}}}function gg(i){const e=new WeakMap;function t(o,l){const c=o.array,u=o.usage,h=c.byteLength,d=i.createBuffer();i.bindBuffer(l,d),i.bufferData(l,c,u),o.onUploadCallback();let m;if(c instanceof Float32Array)m=i.FLOAT;else if(c instanceof Uint16Array)o.isFloat16BufferAttribute?m=i.HALF_FLOAT:m=i.UNSIGNED_SHORT;else if(c instanceof Int16Array)m=i.SHORT;else if(c instanceof Uint32Array)m=i.UNSIGNED_INT;else if(c instanceof Int32Array)m=i.INT;else if(c instanceof Int8Array)m=i.BYTE;else if(c instanceof Uint8Array)m=i.UNSIGNED_BYTE;else if(c instanceof Uint8ClampedArray)m=i.UNSIGNED_BYTE;else throw new Error("THREE.WebGLAttributes: Unsupported buffer data format: "+c);return{buffer:d,type:m,bytesPerElement:c.BYTES_PER_ELEMENT,version:o.version,size:h}}function n(o,l,c){const u=l.array,h=l._updateRange,d=l.updateRanges;if(i.bindBuffer(c,o),h.count===-1&&d.length===0&&i.bufferSubData(c,0,u),d.length!==0){for(let m=0,_=d.length;m<_;m++){const v=d[m];i.bufferSubData(c,v.start*u.BYTES_PER_ELEMENT,u,v.start,v.count)}l.clearUpdateRanges()}h.count!==-1&&(i.bufferSubData(c,h.offset*u.BYTES_PER_ELEMENT,u,h.offset,h.count),h.count=-1),l.onUploadCallback()}function r(o){return o.isInterleavedBufferAttribute&&(o=o.data),e.get(o)}function s(o){o.isInterleavedBufferAttribute&&(o=o.data);const l=e.get(o);l&&(i.deleteBuffer(l.buffer),e.delete(o))}function a(o,l){if(o.isInterleavedBufferAttribute&&(o=o.data),o.isGLBufferAttribute){const u=e.get(o);(!u||u.version<o.version)&&e.set(o,{buffer:o.buffer,type:o.type,bytesPerElement:o.elementSize,version:o.version});return}const c=e.get(o);if(c===void 0)e.set(o,t(o,l));else if(c.version<o.version){if(c.size!==o.array.byteLength)throw new Error("THREE.WebGLAttributes: The size of the buffer attribute's array buffer does not match the original size. Resizing buffer attributes is not supported.");n(c.buffer,o,l),c.version=o.version}}return{get:r,remove:s,update:a}}class No extends ln{constructor(e=1,t=1,n=1,r=1){super(),this.type="PlaneGeometry",this.parameters={width:e,height:t,widthSegments:n,heightSegments:r};const s=e/2,a=t/2,o=Math.floor(n),l=Math.floor(r),c=o+1,u=l+1,h=e/o,d=t/l,m=[],_=[],v=[],p=[];for(let f=0;f<u;f++){const E=f*d-a;for(let S=0;S<c;S++){const T=S*h-s;_.push(T,-E,0),v.push(0,0,1),p.push(S/o),p.push(1-f/l)}}for(let f=0;f<l;f++)for(let E=0;E<o;E++){const S=E+c*f,T=E+c*(f+1),z=E+1+c*(f+1),R=E+1+c*f;m.push(S,T,R),m.push(T,z,R)}this.setIndex(m),this.setAttribute("position",new vn(_,3)),this.setAttribute("normal",new vn(v,3)),this.setAttribute("uv",new vn(p,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new No(e.width,e.height,e.widthSegments,e.heightSegments)}}var _g=`#ifdef USE_ALPHAHASH
	if ( diffuseColor.a < getAlphaHashThreshold( vPosition ) ) discard;
#endif`,vg=`#ifdef USE_ALPHAHASH
	const float ALPHA_HASH_SCALE = 0.05;
	float hash2D( vec2 value ) {
		return fract( 1.0e4 * sin( 17.0 * value.x + 0.1 * value.y ) * ( 0.1 + abs( sin( 13.0 * value.y + value.x ) ) ) );
	}
	float hash3D( vec3 value ) {
		return hash2D( vec2( hash2D( value.xy ), value.z ) );
	}
	float getAlphaHashThreshold( vec3 position ) {
		float maxDeriv = max(
			length( dFdx( position.xyz ) ),
			length( dFdy( position.xyz ) )
		);
		float pixScale = 1.0 / ( ALPHA_HASH_SCALE * maxDeriv );
		vec2 pixScales = vec2(
			exp2( floor( log2( pixScale ) ) ),
			exp2( ceil( log2( pixScale ) ) )
		);
		vec2 alpha = vec2(
			hash3D( floor( pixScales.x * position.xyz ) ),
			hash3D( floor( pixScales.y * position.xyz ) )
		);
		float lerpFactor = fract( log2( pixScale ) );
		float x = ( 1.0 - lerpFactor ) * alpha.x + lerpFactor * alpha.y;
		float a = min( lerpFactor, 1.0 - lerpFactor );
		vec3 cases = vec3(
			x * x / ( 2.0 * a * ( 1.0 - a ) ),
			( x - 0.5 * a ) / ( 1.0 - a ),
			1.0 - ( ( 1.0 - x ) * ( 1.0 - x ) / ( 2.0 * a * ( 1.0 - a ) ) )
		);
		float threshold = ( x < ( 1.0 - a ) )
			? ( ( x < a ) ? cases.x : cases.y )
			: cases.z;
		return clamp( threshold , 1.0e-6, 1.0 );
	}
#endif`,xg=`#ifdef USE_ALPHAMAP
	diffuseColor.a *= texture2D( alphaMap, vAlphaMapUv ).g;
#endif`,yg=`#ifdef USE_ALPHAMAP
	uniform sampler2D alphaMap;
#endif`,Mg=`#ifdef USE_ALPHATEST
	#ifdef ALPHA_TO_COVERAGE
	diffuseColor.a = smoothstep( alphaTest, alphaTest + fwidth( diffuseColor.a ), diffuseColor.a );
	if ( diffuseColor.a == 0.0 ) discard;
	#else
	if ( diffuseColor.a < alphaTest ) discard;
	#endif
#endif`,Sg=`#ifdef USE_ALPHATEST
	uniform float alphaTest;
#endif`,Eg=`#ifdef USE_AOMAP
	float ambientOcclusion = ( texture2D( aoMap, vAoMapUv ).r - 1.0 ) * aoMapIntensity + 1.0;
	reflectedLight.indirectDiffuse *= ambientOcclusion;
	#if defined( USE_CLEARCOAT ) 
		clearcoatSpecularIndirect *= ambientOcclusion;
	#endif
	#if defined( USE_SHEEN ) 
		sheenSpecularIndirect *= ambientOcclusion;
	#endif
	#if defined( USE_ENVMAP ) && defined( STANDARD )
		float dotNV = saturate( dot( geometryNormal, geometryViewDir ) );
		reflectedLight.indirectSpecular *= computeSpecularOcclusion( dotNV, ambientOcclusion, material.roughness );
	#endif
#endif`,bg=`#ifdef USE_AOMAP
	uniform sampler2D aoMap;
	uniform float aoMapIntensity;
#endif`,Tg=`#ifdef USE_BATCHING
	#if ! defined( GL_ANGLE_multi_draw )
	#define gl_DrawID _gl_DrawID
	uniform int _gl_DrawID;
	#endif
	uniform highp sampler2D batchingTexture;
	uniform highp usampler2D batchingIdTexture;
	mat4 getBatchingMatrix( const in float i ) {
		int size = textureSize( batchingTexture, 0 ).x;
		int j = int( i ) * 4;
		int x = j % size;
		int y = j / size;
		vec4 v1 = texelFetch( batchingTexture, ivec2( x, y ), 0 );
		vec4 v2 = texelFetch( batchingTexture, ivec2( x + 1, y ), 0 );
		vec4 v3 = texelFetch( batchingTexture, ivec2( x + 2, y ), 0 );
		vec4 v4 = texelFetch( batchingTexture, ivec2( x + 3, y ), 0 );
		return mat4( v1, v2, v3, v4 );
	}
	float getIndirectIndex( const in int i ) {
		int size = textureSize( batchingIdTexture, 0 ).x;
		int x = i % size;
		int y = i / size;
		return float( texelFetch( batchingIdTexture, ivec2( x, y ), 0 ).r );
	}
#endif
#ifdef USE_BATCHING_COLOR
	uniform sampler2D batchingColorTexture;
	vec3 getBatchingColor( const in float i ) {
		int size = textureSize( batchingColorTexture, 0 ).x;
		int j = int( i );
		int x = j % size;
		int y = j / size;
		return texelFetch( batchingColorTexture, ivec2( x, y ), 0 ).rgb;
	}
#endif`,wg=`#ifdef USE_BATCHING
	mat4 batchingMatrix = getBatchingMatrix( getIndirectIndex( gl_DrawID ) );
#endif`,Ag=`vec3 transformed = vec3( position );
#ifdef USE_ALPHAHASH
	vPosition = vec3( position );
#endif`,Rg=`vec3 objectNormal = vec3( normal );
#ifdef USE_TANGENT
	vec3 objectTangent = vec3( tangent.xyz );
#endif`,Cg=`float G_BlinnPhong_Implicit( ) {
	return 0.25;
}
float D_BlinnPhong( const in float shininess, const in float dotNH ) {
	return RECIPROCAL_PI * ( shininess * 0.5 + 1.0 ) * pow( dotNH, shininess );
}
vec3 BRDF_BlinnPhong( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in vec3 specularColor, const in float shininess ) {
	vec3 halfDir = normalize( lightDir + viewDir );
	float dotNH = saturate( dot( normal, halfDir ) );
	float dotVH = saturate( dot( viewDir, halfDir ) );
	vec3 F = F_Schlick( specularColor, 1.0, dotVH );
	float G = G_BlinnPhong_Implicit( );
	float D = D_BlinnPhong( shininess, dotNH );
	return F * ( G * D );
} // validated`,Pg=`#ifdef USE_IRIDESCENCE
	const mat3 XYZ_TO_REC709 = mat3(
		 3.2404542, -0.9692660,  0.0556434,
		-1.5371385,  1.8760108, -0.2040259,
		-0.4985314,  0.0415560,  1.0572252
	);
	vec3 Fresnel0ToIor( vec3 fresnel0 ) {
		vec3 sqrtF0 = sqrt( fresnel0 );
		return ( vec3( 1.0 ) + sqrtF0 ) / ( vec3( 1.0 ) - sqrtF0 );
	}
	vec3 IorToFresnel0( vec3 transmittedIor, float incidentIor ) {
		return pow2( ( transmittedIor - vec3( incidentIor ) ) / ( transmittedIor + vec3( incidentIor ) ) );
	}
	float IorToFresnel0( float transmittedIor, float incidentIor ) {
		return pow2( ( transmittedIor - incidentIor ) / ( transmittedIor + incidentIor ));
	}
	vec3 evalSensitivity( float OPD, vec3 shift ) {
		float phase = 2.0 * PI * OPD * 1.0e-9;
		vec3 val = vec3( 5.4856e-13, 4.4201e-13, 5.2481e-13 );
		vec3 pos = vec3( 1.6810e+06, 1.7953e+06, 2.2084e+06 );
		vec3 var = vec3( 4.3278e+09, 9.3046e+09, 6.6121e+09 );
		vec3 xyz = val * sqrt( 2.0 * PI * var ) * cos( pos * phase + shift ) * exp( - pow2( phase ) * var );
		xyz.x += 9.7470e-14 * sqrt( 2.0 * PI * 4.5282e+09 ) * cos( 2.2399e+06 * phase + shift[ 0 ] ) * exp( - 4.5282e+09 * pow2( phase ) );
		xyz /= 1.0685e-7;
		vec3 rgb = XYZ_TO_REC709 * xyz;
		return rgb;
	}
	vec3 evalIridescence( float outsideIOR, float eta2, float cosTheta1, float thinFilmThickness, vec3 baseF0 ) {
		vec3 I;
		float iridescenceIOR = mix( outsideIOR, eta2, smoothstep( 0.0, 0.03, thinFilmThickness ) );
		float sinTheta2Sq = pow2( outsideIOR / iridescenceIOR ) * ( 1.0 - pow2( cosTheta1 ) );
		float cosTheta2Sq = 1.0 - sinTheta2Sq;
		if ( cosTheta2Sq < 0.0 ) {
			return vec3( 1.0 );
		}
		float cosTheta2 = sqrt( cosTheta2Sq );
		float R0 = IorToFresnel0( iridescenceIOR, outsideIOR );
		float R12 = F_Schlick( R0, 1.0, cosTheta1 );
		float T121 = 1.0 - R12;
		float phi12 = 0.0;
		if ( iridescenceIOR < outsideIOR ) phi12 = PI;
		float phi21 = PI - phi12;
		vec3 baseIOR = Fresnel0ToIor( clamp( baseF0, 0.0, 0.9999 ) );		vec3 R1 = IorToFresnel0( baseIOR, iridescenceIOR );
		vec3 R23 = F_Schlick( R1, 1.0, cosTheta2 );
		vec3 phi23 = vec3( 0.0 );
		if ( baseIOR[ 0 ] < iridescenceIOR ) phi23[ 0 ] = PI;
		if ( baseIOR[ 1 ] < iridescenceIOR ) phi23[ 1 ] = PI;
		if ( baseIOR[ 2 ] < iridescenceIOR ) phi23[ 2 ] = PI;
		float OPD = 2.0 * iridescenceIOR * thinFilmThickness * cosTheta2;
		vec3 phi = vec3( phi21 ) + phi23;
		vec3 R123 = clamp( R12 * R23, 1e-5, 0.9999 );
		vec3 r123 = sqrt( R123 );
		vec3 Rs = pow2( T121 ) * R23 / ( vec3( 1.0 ) - R123 );
		vec3 C0 = R12 + Rs;
		I = C0;
		vec3 Cm = Rs - T121;
		for ( int m = 1; m <= 2; ++ m ) {
			Cm *= r123;
			vec3 Sm = 2.0 * evalSensitivity( float( m ) * OPD, float( m ) * phi );
			I += Cm * Sm;
		}
		return max( I, vec3( 0.0 ) );
	}
#endif`,Lg=`#ifdef USE_BUMPMAP
	uniform sampler2D bumpMap;
	uniform float bumpScale;
	vec2 dHdxy_fwd() {
		vec2 dSTdx = dFdx( vBumpMapUv );
		vec2 dSTdy = dFdy( vBumpMapUv );
		float Hll = bumpScale * texture2D( bumpMap, vBumpMapUv ).x;
		float dBx = bumpScale * texture2D( bumpMap, vBumpMapUv + dSTdx ).x - Hll;
		float dBy = bumpScale * texture2D( bumpMap, vBumpMapUv + dSTdy ).x - Hll;
		return vec2( dBx, dBy );
	}
	vec3 perturbNormalArb( vec3 surf_pos, vec3 surf_norm, vec2 dHdxy, float faceDirection ) {
		vec3 vSigmaX = normalize( dFdx( surf_pos.xyz ) );
		vec3 vSigmaY = normalize( dFdy( surf_pos.xyz ) );
		vec3 vN = surf_norm;
		vec3 R1 = cross( vSigmaY, vN );
		vec3 R2 = cross( vN, vSigmaX );
		float fDet = dot( vSigmaX, R1 ) * faceDirection;
		vec3 vGrad = sign( fDet ) * ( dHdxy.x * R1 + dHdxy.y * R2 );
		return normalize( abs( fDet ) * surf_norm - vGrad );
	}
#endif`,Dg=`#if NUM_CLIPPING_PLANES > 0
	vec4 plane;
	#ifdef ALPHA_TO_COVERAGE
		float distanceToPlane, distanceGradient;
		float clipOpacity = 1.0;
		#pragma unroll_loop_start
		for ( int i = 0; i < UNION_CLIPPING_PLANES; i ++ ) {
			plane = clippingPlanes[ i ];
			distanceToPlane = - dot( vClipPosition, plane.xyz ) + plane.w;
			distanceGradient = fwidth( distanceToPlane ) / 2.0;
			clipOpacity *= smoothstep( - distanceGradient, distanceGradient, distanceToPlane );
			if ( clipOpacity == 0.0 ) discard;
		}
		#pragma unroll_loop_end
		#if UNION_CLIPPING_PLANES < NUM_CLIPPING_PLANES
			float unionClipOpacity = 1.0;
			#pragma unroll_loop_start
			for ( int i = UNION_CLIPPING_PLANES; i < NUM_CLIPPING_PLANES; i ++ ) {
				plane = clippingPlanes[ i ];
				distanceToPlane = - dot( vClipPosition, plane.xyz ) + plane.w;
				distanceGradient = fwidth( distanceToPlane ) / 2.0;
				unionClipOpacity *= 1.0 - smoothstep( - distanceGradient, distanceGradient, distanceToPlane );
			}
			#pragma unroll_loop_end
			clipOpacity *= 1.0 - unionClipOpacity;
		#endif
		diffuseColor.a *= clipOpacity;
		if ( diffuseColor.a == 0.0 ) discard;
	#else
		#pragma unroll_loop_start
		for ( int i = 0; i < UNION_CLIPPING_PLANES; i ++ ) {
			plane = clippingPlanes[ i ];
			if ( dot( vClipPosition, plane.xyz ) > plane.w ) discard;
		}
		#pragma unroll_loop_end
		#if UNION_CLIPPING_PLANES < NUM_CLIPPING_PLANES
			bool clipped = true;
			#pragma unroll_loop_start
			for ( int i = UNION_CLIPPING_PLANES; i < NUM_CLIPPING_PLANES; i ++ ) {
				plane = clippingPlanes[ i ];
				clipped = ( dot( vClipPosition, plane.xyz ) > plane.w ) && clipped;
			}
			#pragma unroll_loop_end
			if ( clipped ) discard;
		#endif
	#endif
#endif`,Ig=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
	uniform vec4 clippingPlanes[ NUM_CLIPPING_PLANES ];
#endif`,Ug=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
#endif`,Ng=`#if NUM_CLIPPING_PLANES > 0
	vClipPosition = - mvPosition.xyz;
#endif`,Fg=`#if defined( USE_COLOR_ALPHA )
	diffuseColor *= vColor;
#elif defined( USE_COLOR )
	diffuseColor.rgb *= vColor;
#endif`,Og=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR )
	varying vec3 vColor;
#endif`,Bg=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR ) || defined( USE_INSTANCING_COLOR ) || defined( USE_BATCHING_COLOR )
	varying vec3 vColor;
#endif`,zg=`#if defined( USE_COLOR_ALPHA )
	vColor = vec4( 1.0 );
#elif defined( USE_COLOR ) || defined( USE_INSTANCING_COLOR ) || defined( USE_BATCHING_COLOR )
	vColor = vec3( 1.0 );
#endif
#ifdef USE_COLOR
	vColor *= color;
#endif
#ifdef USE_INSTANCING_COLOR
	vColor.xyz *= instanceColor.xyz;
#endif
#ifdef USE_BATCHING_COLOR
	vec3 batchingColor = getBatchingColor( getIndirectIndex( gl_DrawID ) );
	vColor.xyz *= batchingColor.xyz;
#endif`,kg=`#define PI 3.141592653589793
#define PI2 6.283185307179586
#define PI_HALF 1.5707963267948966
#define RECIPROCAL_PI 0.3183098861837907
#define RECIPROCAL_PI2 0.15915494309189535
#define EPSILON 1e-6
#ifndef saturate
#define saturate( a ) clamp( a, 0.0, 1.0 )
#endif
#define whiteComplement( a ) ( 1.0 - saturate( a ) )
float pow2( const in float x ) { return x*x; }
vec3 pow2( const in vec3 x ) { return x*x; }
float pow3( const in float x ) { return x*x*x; }
float pow4( const in float x ) { float x2 = x*x; return x2*x2; }
float max3( const in vec3 v ) { return max( max( v.x, v.y ), v.z ); }
float average( const in vec3 v ) { return dot( v, vec3( 0.3333333 ) ); }
highp float rand( const in vec2 uv ) {
	const highp float a = 12.9898, b = 78.233, c = 43758.5453;
	highp float dt = dot( uv.xy, vec2( a,b ) ), sn = mod( dt, PI );
	return fract( sin( sn ) * c );
}
#ifdef HIGH_PRECISION
	float precisionSafeLength( vec3 v ) { return length( v ); }
#else
	float precisionSafeLength( vec3 v ) {
		float maxComponent = max3( abs( v ) );
		return length( v / maxComponent ) * maxComponent;
	}
#endif
struct IncidentLight {
	vec3 color;
	vec3 direction;
	bool visible;
};
struct ReflectedLight {
	vec3 directDiffuse;
	vec3 directSpecular;
	vec3 indirectDiffuse;
	vec3 indirectSpecular;
};
#ifdef USE_ALPHAHASH
	varying vec3 vPosition;
#endif
vec3 transformDirection( in vec3 dir, in mat4 matrix ) {
	return normalize( ( matrix * vec4( dir, 0.0 ) ).xyz );
}
vec3 inverseTransformDirection( in vec3 dir, in mat4 matrix ) {
	return normalize( ( vec4( dir, 0.0 ) * matrix ).xyz );
}
mat3 transposeMat3( const in mat3 m ) {
	mat3 tmp;
	tmp[ 0 ] = vec3( m[ 0 ].x, m[ 1 ].x, m[ 2 ].x );
	tmp[ 1 ] = vec3( m[ 0 ].y, m[ 1 ].y, m[ 2 ].y );
	tmp[ 2 ] = vec3( m[ 0 ].z, m[ 1 ].z, m[ 2 ].z );
	return tmp;
}
bool isPerspectiveMatrix( mat4 m ) {
	return m[ 2 ][ 3 ] == - 1.0;
}
vec2 equirectUv( in vec3 dir ) {
	float u = atan( dir.z, dir.x ) * RECIPROCAL_PI2 + 0.5;
	float v = asin( clamp( dir.y, - 1.0, 1.0 ) ) * RECIPROCAL_PI + 0.5;
	return vec2( u, v );
}
vec3 BRDF_Lambert( const in vec3 diffuseColor ) {
	return RECIPROCAL_PI * diffuseColor;
}
vec3 F_Schlick( const in vec3 f0, const in float f90, const in float dotVH ) {
	float fresnel = exp2( ( - 5.55473 * dotVH - 6.98316 ) * dotVH );
	return f0 * ( 1.0 - fresnel ) + ( f90 * fresnel );
}
float F_Schlick( const in float f0, const in float f90, const in float dotVH ) {
	float fresnel = exp2( ( - 5.55473 * dotVH - 6.98316 ) * dotVH );
	return f0 * ( 1.0 - fresnel ) + ( f90 * fresnel );
} // validated`,Hg=`#ifdef ENVMAP_TYPE_CUBE_UV
	#define cubeUV_minMipLevel 4.0
	#define cubeUV_minTileSize 16.0
	float getFace( vec3 direction ) {
		vec3 absDirection = abs( direction );
		float face = - 1.0;
		if ( absDirection.x > absDirection.z ) {
			if ( absDirection.x > absDirection.y )
				face = direction.x > 0.0 ? 0.0 : 3.0;
			else
				face = direction.y > 0.0 ? 1.0 : 4.0;
		} else {
			if ( absDirection.z > absDirection.y )
				face = direction.z > 0.0 ? 2.0 : 5.0;
			else
				face = direction.y > 0.0 ? 1.0 : 4.0;
		}
		return face;
	}
	vec2 getUV( vec3 direction, float face ) {
		vec2 uv;
		if ( face == 0.0 ) {
			uv = vec2( direction.z, direction.y ) / abs( direction.x );
		} else if ( face == 1.0 ) {
			uv = vec2( - direction.x, - direction.z ) / abs( direction.y );
		} else if ( face == 2.0 ) {
			uv = vec2( - direction.x, direction.y ) / abs( direction.z );
		} else if ( face == 3.0 ) {
			uv = vec2( - direction.z, direction.y ) / abs( direction.x );
		} else if ( face == 4.0 ) {
			uv = vec2( - direction.x, direction.z ) / abs( direction.y );
		} else {
			uv = vec2( direction.x, direction.y ) / abs( direction.z );
		}
		return 0.5 * ( uv + 1.0 );
	}
	vec3 bilinearCubeUV( sampler2D envMap, vec3 direction, float mipInt ) {
		float face = getFace( direction );
		float filterInt = max( cubeUV_minMipLevel - mipInt, 0.0 );
		mipInt = max( mipInt, cubeUV_minMipLevel );
		float faceSize = exp2( mipInt );
		highp vec2 uv = getUV( direction, face ) * ( faceSize - 2.0 ) + 1.0;
		if ( face > 2.0 ) {
			uv.y += faceSize;
			face -= 3.0;
		}
		uv.x += face * faceSize;
		uv.x += filterInt * 3.0 * cubeUV_minTileSize;
		uv.y += 4.0 * ( exp2( CUBEUV_MAX_MIP ) - faceSize );
		uv.x *= CUBEUV_TEXEL_WIDTH;
		uv.y *= CUBEUV_TEXEL_HEIGHT;
		#ifdef texture2DGradEXT
			return texture2DGradEXT( envMap, uv, vec2( 0.0 ), vec2( 0.0 ) ).rgb;
		#else
			return texture2D( envMap, uv ).rgb;
		#endif
	}
	#define cubeUV_r0 1.0
	#define cubeUV_m0 - 2.0
	#define cubeUV_r1 0.8
	#define cubeUV_m1 - 1.0
	#define cubeUV_r4 0.4
	#define cubeUV_m4 2.0
	#define cubeUV_r5 0.305
	#define cubeUV_m5 3.0
	#define cubeUV_r6 0.21
	#define cubeUV_m6 4.0
	float roughnessToMip( float roughness ) {
		float mip = 0.0;
		if ( roughness >= cubeUV_r1 ) {
			mip = ( cubeUV_r0 - roughness ) * ( cubeUV_m1 - cubeUV_m0 ) / ( cubeUV_r0 - cubeUV_r1 ) + cubeUV_m0;
		} else if ( roughness >= cubeUV_r4 ) {
			mip = ( cubeUV_r1 - roughness ) * ( cubeUV_m4 - cubeUV_m1 ) / ( cubeUV_r1 - cubeUV_r4 ) + cubeUV_m1;
		} else if ( roughness >= cubeUV_r5 ) {
			mip = ( cubeUV_r4 - roughness ) * ( cubeUV_m5 - cubeUV_m4 ) / ( cubeUV_r4 - cubeUV_r5 ) + cubeUV_m4;
		} else if ( roughness >= cubeUV_r6 ) {
			mip = ( cubeUV_r5 - roughness ) * ( cubeUV_m6 - cubeUV_m5 ) / ( cubeUV_r5 - cubeUV_r6 ) + cubeUV_m5;
		} else {
			mip = - 2.0 * log2( 1.16 * roughness );		}
		return mip;
	}
	vec4 textureCubeUV( sampler2D envMap, vec3 sampleDir, float roughness ) {
		float mip = clamp( roughnessToMip( roughness ), cubeUV_m0, CUBEUV_MAX_MIP );
		float mipF = fract( mip );
		float mipInt = floor( mip );
		vec3 color0 = bilinearCubeUV( envMap, sampleDir, mipInt );
		if ( mipF == 0.0 ) {
			return vec4( color0, 1.0 );
		} else {
			vec3 color1 = bilinearCubeUV( envMap, sampleDir, mipInt + 1.0 );
			return vec4( mix( color0, color1, mipF ), 1.0 );
		}
	}
#endif`,Vg=`vec3 transformedNormal = objectNormal;
#ifdef USE_TANGENT
	vec3 transformedTangent = objectTangent;
#endif
#ifdef USE_BATCHING
	mat3 bm = mat3( batchingMatrix );
	transformedNormal /= vec3( dot( bm[ 0 ], bm[ 0 ] ), dot( bm[ 1 ], bm[ 1 ] ), dot( bm[ 2 ], bm[ 2 ] ) );
	transformedNormal = bm * transformedNormal;
	#ifdef USE_TANGENT
		transformedTangent = bm * transformedTangent;
	#endif
#endif
#ifdef USE_INSTANCING
	mat3 im = mat3( instanceMatrix );
	transformedNormal /= vec3( dot( im[ 0 ], im[ 0 ] ), dot( im[ 1 ], im[ 1 ] ), dot( im[ 2 ], im[ 2 ] ) );
	transformedNormal = im * transformedNormal;
	#ifdef USE_TANGENT
		transformedTangent = im * transformedTangent;
	#endif
#endif
transformedNormal = normalMatrix * transformedNormal;
#ifdef FLIP_SIDED
	transformedNormal = - transformedNormal;
#endif
#ifdef USE_TANGENT
	transformedTangent = ( modelViewMatrix * vec4( transformedTangent, 0.0 ) ).xyz;
	#ifdef FLIP_SIDED
		transformedTangent = - transformedTangent;
	#endif
#endif`,Gg=`#ifdef USE_DISPLACEMENTMAP
	uniform sampler2D displacementMap;
	uniform float displacementScale;
	uniform float displacementBias;
#endif`,Wg=`#ifdef USE_DISPLACEMENTMAP
	transformed += normalize( objectNormal ) * ( texture2D( displacementMap, vDisplacementMapUv ).x * displacementScale + displacementBias );
#endif`,Xg=`#ifdef USE_EMISSIVEMAP
	vec4 emissiveColor = texture2D( emissiveMap, vEmissiveMapUv );
	totalEmissiveRadiance *= emissiveColor.rgb;
#endif`,qg=`#ifdef USE_EMISSIVEMAP
	uniform sampler2D emissiveMap;
#endif`,Yg="gl_FragColor = linearToOutputTexel( gl_FragColor );",$g=`
const mat3 LINEAR_SRGB_TO_LINEAR_DISPLAY_P3 = mat3(
	vec3( 0.8224621, 0.177538, 0.0 ),
	vec3( 0.0331941, 0.9668058, 0.0 ),
	vec3( 0.0170827, 0.0723974, 0.9105199 )
);
const mat3 LINEAR_DISPLAY_P3_TO_LINEAR_SRGB = mat3(
	vec3( 1.2249401, - 0.2249404, 0.0 ),
	vec3( - 0.0420569, 1.0420571, 0.0 ),
	vec3( - 0.0196376, - 0.0786361, 1.0982735 )
);
vec4 LinearSRGBToLinearDisplayP3( in vec4 value ) {
	return vec4( value.rgb * LINEAR_SRGB_TO_LINEAR_DISPLAY_P3, value.a );
}
vec4 LinearDisplayP3ToLinearSRGB( in vec4 value ) {
	return vec4( value.rgb * LINEAR_DISPLAY_P3_TO_LINEAR_SRGB, value.a );
}
vec4 LinearTransferOETF( in vec4 value ) {
	return value;
}
vec4 sRGBTransferOETF( in vec4 value ) {
	return vec4( mix( pow( value.rgb, vec3( 0.41666 ) ) * 1.055 - vec3( 0.055 ), value.rgb * 12.92, vec3( lessThanEqual( value.rgb, vec3( 0.0031308 ) ) ) ), value.a );
}`,jg=`#ifdef USE_ENVMAP
	#ifdef ENV_WORLDPOS
		vec3 cameraToFrag;
		if ( isOrthographic ) {
			cameraToFrag = normalize( vec3( - viewMatrix[ 0 ][ 2 ], - viewMatrix[ 1 ][ 2 ], - viewMatrix[ 2 ][ 2 ] ) );
		} else {
			cameraToFrag = normalize( vWorldPosition - cameraPosition );
		}
		vec3 worldNormal = inverseTransformDirection( normal, viewMatrix );
		#ifdef ENVMAP_MODE_REFLECTION
			vec3 reflectVec = reflect( cameraToFrag, worldNormal );
		#else
			vec3 reflectVec = refract( cameraToFrag, worldNormal, refractionRatio );
		#endif
	#else
		vec3 reflectVec = vReflect;
	#endif
	#ifdef ENVMAP_TYPE_CUBE
		vec4 envColor = textureCube( envMap, envMapRotation * vec3( flipEnvMap * reflectVec.x, reflectVec.yz ) );
	#else
		vec4 envColor = vec4( 0.0 );
	#endif
	#ifdef ENVMAP_BLENDING_MULTIPLY
		outgoingLight = mix( outgoingLight, outgoingLight * envColor.xyz, specularStrength * reflectivity );
	#elif defined( ENVMAP_BLENDING_MIX )
		outgoingLight = mix( outgoingLight, envColor.xyz, specularStrength * reflectivity );
	#elif defined( ENVMAP_BLENDING_ADD )
		outgoingLight += envColor.xyz * specularStrength * reflectivity;
	#endif
#endif`,Kg=`#ifdef USE_ENVMAP
	uniform float envMapIntensity;
	uniform float flipEnvMap;
	uniform mat3 envMapRotation;
	#ifdef ENVMAP_TYPE_CUBE
		uniform samplerCube envMap;
	#else
		uniform sampler2D envMap;
	#endif
	
#endif`,Zg=`#ifdef USE_ENVMAP
	uniform float reflectivity;
	#if defined( USE_BUMPMAP ) || defined( USE_NORMALMAP ) || defined( PHONG ) || defined( LAMBERT )
		#define ENV_WORLDPOS
	#endif
	#ifdef ENV_WORLDPOS
		varying vec3 vWorldPosition;
		uniform float refractionRatio;
	#else
		varying vec3 vReflect;
	#endif
#endif`,Jg=`#ifdef USE_ENVMAP
	#if defined( USE_BUMPMAP ) || defined( USE_NORMALMAP ) || defined( PHONG ) || defined( LAMBERT )
		#define ENV_WORLDPOS
	#endif
	#ifdef ENV_WORLDPOS
		
		varying vec3 vWorldPosition;
	#else
		varying vec3 vReflect;
		uniform float refractionRatio;
	#endif
#endif`,Qg=`#ifdef USE_ENVMAP
	#ifdef ENV_WORLDPOS
		vWorldPosition = worldPosition.xyz;
	#else
		vec3 cameraToVertex;
		if ( isOrthographic ) {
			cameraToVertex = normalize( vec3( - viewMatrix[ 0 ][ 2 ], - viewMatrix[ 1 ][ 2 ], - viewMatrix[ 2 ][ 2 ] ) );
		} else {
			cameraToVertex = normalize( worldPosition.xyz - cameraPosition );
		}
		vec3 worldNormal = inverseTransformDirection( transformedNormal, viewMatrix );
		#ifdef ENVMAP_MODE_REFLECTION
			vReflect = reflect( cameraToVertex, worldNormal );
		#else
			vReflect = refract( cameraToVertex, worldNormal, refractionRatio );
		#endif
	#endif
#endif`,e_=`#ifdef USE_FOG
	vFogDepth = - mvPosition.z;
#endif`,t_=`#ifdef USE_FOG
	varying float vFogDepth;
#endif`,n_=`#ifdef USE_FOG
	#ifdef FOG_EXP2
		float fogFactor = 1.0 - exp( - fogDensity * fogDensity * vFogDepth * vFogDepth );
	#else
		float fogFactor = smoothstep( fogNear, fogFar, vFogDepth );
	#endif
	gl_FragColor.rgb = mix( gl_FragColor.rgb, fogColor, fogFactor );
#endif`,i_=`#ifdef USE_FOG
	uniform vec3 fogColor;
	varying float vFogDepth;
	#ifdef FOG_EXP2
		uniform float fogDensity;
	#else
		uniform float fogNear;
		uniform float fogFar;
	#endif
#endif`,r_=`#ifdef USE_GRADIENTMAP
	uniform sampler2D gradientMap;
#endif
vec3 getGradientIrradiance( vec3 normal, vec3 lightDirection ) {
	float dotNL = dot( normal, lightDirection );
	vec2 coord = vec2( dotNL * 0.5 + 0.5, 0.0 );
	#ifdef USE_GRADIENTMAP
		return vec3( texture2D( gradientMap, coord ).r );
	#else
		vec2 fw = fwidth( coord ) * 0.5;
		return mix( vec3( 0.7 ), vec3( 1.0 ), smoothstep( 0.7 - fw.x, 0.7 + fw.x, coord.x ) );
	#endif
}`,s_=`#ifdef USE_LIGHTMAP
	uniform sampler2D lightMap;
	uniform float lightMapIntensity;
#endif`,a_=`LambertMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularStrength = specularStrength;`,o_=`varying vec3 vViewPosition;
struct LambertMaterial {
	vec3 diffuseColor;
	float specularStrength;
};
void RE_Direct_Lambert( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in LambertMaterial material, inout ReflectedLight reflectedLight ) {
	float dotNL = saturate( dot( geometryNormal, directLight.direction ) );
	vec3 irradiance = dotNL * directLight.color;
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
void RE_IndirectDiffuse_Lambert( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in LambertMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
#define RE_Direct				RE_Direct_Lambert
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Lambert`,l_=`uniform bool receiveShadow;
uniform vec3 ambientLightColor;
#if defined( USE_LIGHT_PROBES )
	uniform vec3 lightProbe[ 9 ];
#endif
vec3 shGetIrradianceAt( in vec3 normal, in vec3 shCoefficients[ 9 ] ) {
	float x = normal.x, y = normal.y, z = normal.z;
	vec3 result = shCoefficients[ 0 ] * 0.886227;
	result += shCoefficients[ 1 ] * 2.0 * 0.511664 * y;
	result += shCoefficients[ 2 ] * 2.0 * 0.511664 * z;
	result += shCoefficients[ 3 ] * 2.0 * 0.511664 * x;
	result += shCoefficients[ 4 ] * 2.0 * 0.429043 * x * y;
	result += shCoefficients[ 5 ] * 2.0 * 0.429043 * y * z;
	result += shCoefficients[ 6 ] * ( 0.743125 * z * z - 0.247708 );
	result += shCoefficients[ 7 ] * 2.0 * 0.429043 * x * z;
	result += shCoefficients[ 8 ] * 0.429043 * ( x * x - y * y );
	return result;
}
vec3 getLightProbeIrradiance( const in vec3 lightProbe[ 9 ], const in vec3 normal ) {
	vec3 worldNormal = inverseTransformDirection( normal, viewMatrix );
	vec3 irradiance = shGetIrradianceAt( worldNormal, lightProbe );
	return irradiance;
}
vec3 getAmbientLightIrradiance( const in vec3 ambientLightColor ) {
	vec3 irradiance = ambientLightColor;
	return irradiance;
}
float getDistanceAttenuation( const in float lightDistance, const in float cutoffDistance, const in float decayExponent ) {
	float distanceFalloff = 1.0 / max( pow( lightDistance, decayExponent ), 0.01 );
	if ( cutoffDistance > 0.0 ) {
		distanceFalloff *= pow2( saturate( 1.0 - pow4( lightDistance / cutoffDistance ) ) );
	}
	return distanceFalloff;
}
float getSpotAttenuation( const in float coneCosine, const in float penumbraCosine, const in float angleCosine ) {
	return smoothstep( coneCosine, penumbraCosine, angleCosine );
}
#if NUM_DIR_LIGHTS > 0
	struct DirectionalLight {
		vec3 direction;
		vec3 color;
	};
	uniform DirectionalLight directionalLights[ NUM_DIR_LIGHTS ];
	void getDirectionalLightInfo( const in DirectionalLight directionalLight, out IncidentLight light ) {
		light.color = directionalLight.color;
		light.direction = directionalLight.direction;
		light.visible = true;
	}
#endif
#if NUM_POINT_LIGHTS > 0
	struct PointLight {
		vec3 position;
		vec3 color;
		float distance;
		float decay;
	};
	uniform PointLight pointLights[ NUM_POINT_LIGHTS ];
	void getPointLightInfo( const in PointLight pointLight, const in vec3 geometryPosition, out IncidentLight light ) {
		vec3 lVector = pointLight.position - geometryPosition;
		light.direction = normalize( lVector );
		float lightDistance = length( lVector );
		light.color = pointLight.color;
		light.color *= getDistanceAttenuation( lightDistance, pointLight.distance, pointLight.decay );
		light.visible = ( light.color != vec3( 0.0 ) );
	}
#endif
#if NUM_SPOT_LIGHTS > 0
	struct SpotLight {
		vec3 position;
		vec3 direction;
		vec3 color;
		float distance;
		float decay;
		float coneCos;
		float penumbraCos;
	};
	uniform SpotLight spotLights[ NUM_SPOT_LIGHTS ];
	void getSpotLightInfo( const in SpotLight spotLight, const in vec3 geometryPosition, out IncidentLight light ) {
		vec3 lVector = spotLight.position - geometryPosition;
		light.direction = normalize( lVector );
		float angleCos = dot( light.direction, spotLight.direction );
		float spotAttenuation = getSpotAttenuation( spotLight.coneCos, spotLight.penumbraCos, angleCos );
		if ( spotAttenuation > 0.0 ) {
			float lightDistance = length( lVector );
			light.color = spotLight.color * spotAttenuation;
			light.color *= getDistanceAttenuation( lightDistance, spotLight.distance, spotLight.decay );
			light.visible = ( light.color != vec3( 0.0 ) );
		} else {
			light.color = vec3( 0.0 );
			light.visible = false;
		}
	}
#endif
#if NUM_RECT_AREA_LIGHTS > 0
	struct RectAreaLight {
		vec3 color;
		vec3 position;
		vec3 halfWidth;
		vec3 halfHeight;
	};
	uniform sampler2D ltc_1;	uniform sampler2D ltc_2;
	uniform RectAreaLight rectAreaLights[ NUM_RECT_AREA_LIGHTS ];
#endif
#if NUM_HEMI_LIGHTS > 0
	struct HemisphereLight {
		vec3 direction;
		vec3 skyColor;
		vec3 groundColor;
	};
	uniform HemisphereLight hemisphereLights[ NUM_HEMI_LIGHTS ];
	vec3 getHemisphereLightIrradiance( const in HemisphereLight hemiLight, const in vec3 normal ) {
		float dotNL = dot( normal, hemiLight.direction );
		float hemiDiffuseWeight = 0.5 * dotNL + 0.5;
		vec3 irradiance = mix( hemiLight.groundColor, hemiLight.skyColor, hemiDiffuseWeight );
		return irradiance;
	}
#endif`,c_=`#ifdef USE_ENVMAP
	vec3 getIBLIrradiance( const in vec3 normal ) {
		#ifdef ENVMAP_TYPE_CUBE_UV
			vec3 worldNormal = inverseTransformDirection( normal, viewMatrix );
			vec4 envMapColor = textureCubeUV( envMap, envMapRotation * worldNormal, 1.0 );
			return PI * envMapColor.rgb * envMapIntensity;
		#else
			return vec3( 0.0 );
		#endif
	}
	vec3 getIBLRadiance( const in vec3 viewDir, const in vec3 normal, const in float roughness ) {
		#ifdef ENVMAP_TYPE_CUBE_UV
			vec3 reflectVec = reflect( - viewDir, normal );
			reflectVec = normalize( mix( reflectVec, normal, roughness * roughness) );
			reflectVec = inverseTransformDirection( reflectVec, viewMatrix );
			vec4 envMapColor = textureCubeUV( envMap, envMapRotation * reflectVec, roughness );
			return envMapColor.rgb * envMapIntensity;
		#else
			return vec3( 0.0 );
		#endif
	}
	#ifdef USE_ANISOTROPY
		vec3 getIBLAnisotropyRadiance( const in vec3 viewDir, const in vec3 normal, const in float roughness, const in vec3 bitangent, const in float anisotropy ) {
			#ifdef ENVMAP_TYPE_CUBE_UV
				vec3 bentNormal = cross( bitangent, viewDir );
				bentNormal = normalize( cross( bentNormal, bitangent ) );
				bentNormal = normalize( mix( bentNormal, normal, pow2( pow2( 1.0 - anisotropy * ( 1.0 - roughness ) ) ) ) );
				return getIBLRadiance( viewDir, bentNormal, roughness );
			#else
				return vec3( 0.0 );
			#endif
		}
	#endif
#endif`,u_=`ToonMaterial material;
material.diffuseColor = diffuseColor.rgb;`,h_=`varying vec3 vViewPosition;
struct ToonMaterial {
	vec3 diffuseColor;
};
void RE_Direct_Toon( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in ToonMaterial material, inout ReflectedLight reflectedLight ) {
	vec3 irradiance = getGradientIrradiance( geometryNormal, directLight.direction ) * directLight.color;
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
void RE_IndirectDiffuse_Toon( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in ToonMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
#define RE_Direct				RE_Direct_Toon
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Toon`,d_=`BlinnPhongMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularColor = specular;
material.specularShininess = shininess;
material.specularStrength = specularStrength;`,f_=`varying vec3 vViewPosition;
struct BlinnPhongMaterial {
	vec3 diffuseColor;
	vec3 specularColor;
	float specularShininess;
	float specularStrength;
};
void RE_Direct_BlinnPhong( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in BlinnPhongMaterial material, inout ReflectedLight reflectedLight ) {
	float dotNL = saturate( dot( geometryNormal, directLight.direction ) );
	vec3 irradiance = dotNL * directLight.color;
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
	reflectedLight.directSpecular += irradiance * BRDF_BlinnPhong( directLight.direction, geometryViewDir, geometryNormal, material.specularColor, material.specularShininess ) * material.specularStrength;
}
void RE_IndirectDiffuse_BlinnPhong( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in BlinnPhongMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
#define RE_Direct				RE_Direct_BlinnPhong
#define RE_IndirectDiffuse		RE_IndirectDiffuse_BlinnPhong`,p_=`PhysicalMaterial material;
material.diffuseColor = diffuseColor.rgb * ( 1.0 - metalnessFactor );
vec3 dxy = max( abs( dFdx( nonPerturbedNormal ) ), abs( dFdy( nonPerturbedNormal ) ) );
float geometryRoughness = max( max( dxy.x, dxy.y ), dxy.z );
material.roughness = max( roughnessFactor, 0.0525 );material.roughness += geometryRoughness;
material.roughness = min( material.roughness, 1.0 );
#ifdef IOR
	material.ior = ior;
	#ifdef USE_SPECULAR
		float specularIntensityFactor = specularIntensity;
		vec3 specularColorFactor = specularColor;
		#ifdef USE_SPECULAR_COLORMAP
			specularColorFactor *= texture2D( specularColorMap, vSpecularColorMapUv ).rgb;
		#endif
		#ifdef USE_SPECULAR_INTENSITYMAP
			specularIntensityFactor *= texture2D( specularIntensityMap, vSpecularIntensityMapUv ).a;
		#endif
		material.specularF90 = mix( specularIntensityFactor, 1.0, metalnessFactor );
	#else
		float specularIntensityFactor = 1.0;
		vec3 specularColorFactor = vec3( 1.0 );
		material.specularF90 = 1.0;
	#endif
	material.specularColor = mix( min( pow2( ( material.ior - 1.0 ) / ( material.ior + 1.0 ) ) * specularColorFactor, vec3( 1.0 ) ) * specularIntensityFactor, diffuseColor.rgb, metalnessFactor );
#else
	material.specularColor = mix( vec3( 0.04 ), diffuseColor.rgb, metalnessFactor );
	material.specularF90 = 1.0;
#endif
#ifdef USE_CLEARCOAT
	material.clearcoat = clearcoat;
	material.clearcoatRoughness = clearcoatRoughness;
	material.clearcoatF0 = vec3( 0.04 );
	material.clearcoatF90 = 1.0;
	#ifdef USE_CLEARCOATMAP
		material.clearcoat *= texture2D( clearcoatMap, vClearcoatMapUv ).x;
	#endif
	#ifdef USE_CLEARCOAT_ROUGHNESSMAP
		material.clearcoatRoughness *= texture2D( clearcoatRoughnessMap, vClearcoatRoughnessMapUv ).y;
	#endif
	material.clearcoat = saturate( material.clearcoat );	material.clearcoatRoughness = max( material.clearcoatRoughness, 0.0525 );
	material.clearcoatRoughness += geometryRoughness;
	material.clearcoatRoughness = min( material.clearcoatRoughness, 1.0 );
#endif
#ifdef USE_DISPERSION
	material.dispersion = dispersion;
#endif
#ifdef USE_IRIDESCENCE
	material.iridescence = iridescence;
	material.iridescenceIOR = iridescenceIOR;
	#ifdef USE_IRIDESCENCEMAP
		material.iridescence *= texture2D( iridescenceMap, vIridescenceMapUv ).r;
	#endif
	#ifdef USE_IRIDESCENCE_THICKNESSMAP
		material.iridescenceThickness = (iridescenceThicknessMaximum - iridescenceThicknessMinimum) * texture2D( iridescenceThicknessMap, vIridescenceThicknessMapUv ).g + iridescenceThicknessMinimum;
	#else
		material.iridescenceThickness = iridescenceThicknessMaximum;
	#endif
#endif
#ifdef USE_SHEEN
	material.sheenColor = sheenColor;
	#ifdef USE_SHEEN_COLORMAP
		material.sheenColor *= texture2D( sheenColorMap, vSheenColorMapUv ).rgb;
	#endif
	material.sheenRoughness = clamp( sheenRoughness, 0.07, 1.0 );
	#ifdef USE_SHEEN_ROUGHNESSMAP
		material.sheenRoughness *= texture2D( sheenRoughnessMap, vSheenRoughnessMapUv ).a;
	#endif
#endif
#ifdef USE_ANISOTROPY
	#ifdef USE_ANISOTROPYMAP
		mat2 anisotropyMat = mat2( anisotropyVector.x, anisotropyVector.y, - anisotropyVector.y, anisotropyVector.x );
		vec3 anisotropyPolar = texture2D( anisotropyMap, vAnisotropyMapUv ).rgb;
		vec2 anisotropyV = anisotropyMat * normalize( 2.0 * anisotropyPolar.rg - vec2( 1.0 ) ) * anisotropyPolar.b;
	#else
		vec2 anisotropyV = anisotropyVector;
	#endif
	material.anisotropy = length( anisotropyV );
	if( material.anisotropy == 0.0 ) {
		anisotropyV = vec2( 1.0, 0.0 );
	} else {
		anisotropyV /= material.anisotropy;
		material.anisotropy = saturate( material.anisotropy );
	}
	material.alphaT = mix( pow2( material.roughness ), 1.0, pow2( material.anisotropy ) );
	material.anisotropyT = tbn[ 0 ] * anisotropyV.x + tbn[ 1 ] * anisotropyV.y;
	material.anisotropyB = tbn[ 1 ] * anisotropyV.x - tbn[ 0 ] * anisotropyV.y;
#endif`,m_=`struct PhysicalMaterial {
	vec3 diffuseColor;
	float roughness;
	vec3 specularColor;
	float specularF90;
	float dispersion;
	#ifdef USE_CLEARCOAT
		float clearcoat;
		float clearcoatRoughness;
		vec3 clearcoatF0;
		float clearcoatF90;
	#endif
	#ifdef USE_IRIDESCENCE
		float iridescence;
		float iridescenceIOR;
		float iridescenceThickness;
		vec3 iridescenceFresnel;
		vec3 iridescenceF0;
	#endif
	#ifdef USE_SHEEN
		vec3 sheenColor;
		float sheenRoughness;
	#endif
	#ifdef IOR
		float ior;
	#endif
	#ifdef USE_TRANSMISSION
		float transmission;
		float transmissionAlpha;
		float thickness;
		float attenuationDistance;
		vec3 attenuationColor;
	#endif
	#ifdef USE_ANISOTROPY
		float anisotropy;
		float alphaT;
		vec3 anisotropyT;
		vec3 anisotropyB;
	#endif
};
vec3 clearcoatSpecularDirect = vec3( 0.0 );
vec3 clearcoatSpecularIndirect = vec3( 0.0 );
vec3 sheenSpecularDirect = vec3( 0.0 );
vec3 sheenSpecularIndirect = vec3(0.0 );
vec3 Schlick_to_F0( const in vec3 f, const in float f90, const in float dotVH ) {
    float x = clamp( 1.0 - dotVH, 0.0, 1.0 );
    float x2 = x * x;
    float x5 = clamp( x * x2 * x2, 0.0, 0.9999 );
    return ( f - vec3( f90 ) * x5 ) / ( 1.0 - x5 );
}
float V_GGX_SmithCorrelated( const in float alpha, const in float dotNL, const in float dotNV ) {
	float a2 = pow2( alpha );
	float gv = dotNL * sqrt( a2 + ( 1.0 - a2 ) * pow2( dotNV ) );
	float gl = dotNV * sqrt( a2 + ( 1.0 - a2 ) * pow2( dotNL ) );
	return 0.5 / max( gv + gl, EPSILON );
}
float D_GGX( const in float alpha, const in float dotNH ) {
	float a2 = pow2( alpha );
	float denom = pow2( dotNH ) * ( a2 - 1.0 ) + 1.0;
	return RECIPROCAL_PI * a2 / pow2( denom );
}
#ifdef USE_ANISOTROPY
	float V_GGX_SmithCorrelated_Anisotropic( const in float alphaT, const in float alphaB, const in float dotTV, const in float dotBV, const in float dotTL, const in float dotBL, const in float dotNV, const in float dotNL ) {
		float gv = dotNL * length( vec3( alphaT * dotTV, alphaB * dotBV, dotNV ) );
		float gl = dotNV * length( vec3( alphaT * dotTL, alphaB * dotBL, dotNL ) );
		float v = 0.5 / ( gv + gl );
		return saturate(v);
	}
	float D_GGX_Anisotropic( const in float alphaT, const in float alphaB, const in float dotNH, const in float dotTH, const in float dotBH ) {
		float a2 = alphaT * alphaB;
		highp vec3 v = vec3( alphaB * dotTH, alphaT * dotBH, a2 * dotNH );
		highp float v2 = dot( v, v );
		float w2 = a2 / v2;
		return RECIPROCAL_PI * a2 * pow2 ( w2 );
	}
#endif
#ifdef USE_CLEARCOAT
	vec3 BRDF_GGX_Clearcoat( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in PhysicalMaterial material) {
		vec3 f0 = material.clearcoatF0;
		float f90 = material.clearcoatF90;
		float roughness = material.clearcoatRoughness;
		float alpha = pow2( roughness );
		vec3 halfDir = normalize( lightDir + viewDir );
		float dotNL = saturate( dot( normal, lightDir ) );
		float dotNV = saturate( dot( normal, viewDir ) );
		float dotNH = saturate( dot( normal, halfDir ) );
		float dotVH = saturate( dot( viewDir, halfDir ) );
		vec3 F = F_Schlick( f0, f90, dotVH );
		float V = V_GGX_SmithCorrelated( alpha, dotNL, dotNV );
		float D = D_GGX( alpha, dotNH );
		return F * ( V * D );
	}
#endif
vec3 BRDF_GGX( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in PhysicalMaterial material ) {
	vec3 f0 = material.specularColor;
	float f90 = material.specularF90;
	float roughness = material.roughness;
	float alpha = pow2( roughness );
	vec3 halfDir = normalize( lightDir + viewDir );
	float dotNL = saturate( dot( normal, lightDir ) );
	float dotNV = saturate( dot( normal, viewDir ) );
	float dotNH = saturate( dot( normal, halfDir ) );
	float dotVH = saturate( dot( viewDir, halfDir ) );
	vec3 F = F_Schlick( f0, f90, dotVH );
	#ifdef USE_IRIDESCENCE
		F = mix( F, material.iridescenceFresnel, material.iridescence );
	#endif
	#ifdef USE_ANISOTROPY
		float dotTL = dot( material.anisotropyT, lightDir );
		float dotTV = dot( material.anisotropyT, viewDir );
		float dotTH = dot( material.anisotropyT, halfDir );
		float dotBL = dot( material.anisotropyB, lightDir );
		float dotBV = dot( material.anisotropyB, viewDir );
		float dotBH = dot( material.anisotropyB, halfDir );
		float V = V_GGX_SmithCorrelated_Anisotropic( material.alphaT, alpha, dotTV, dotBV, dotTL, dotBL, dotNV, dotNL );
		float D = D_GGX_Anisotropic( material.alphaT, alpha, dotNH, dotTH, dotBH );
	#else
		float V = V_GGX_SmithCorrelated( alpha, dotNL, dotNV );
		float D = D_GGX( alpha, dotNH );
	#endif
	return F * ( V * D );
}
vec2 LTC_Uv( const in vec3 N, const in vec3 V, const in float roughness ) {
	const float LUT_SIZE = 64.0;
	const float LUT_SCALE = ( LUT_SIZE - 1.0 ) / LUT_SIZE;
	const float LUT_BIAS = 0.5 / LUT_SIZE;
	float dotNV = saturate( dot( N, V ) );
	vec2 uv = vec2( roughness, sqrt( 1.0 - dotNV ) );
	uv = uv * LUT_SCALE + LUT_BIAS;
	return uv;
}
float LTC_ClippedSphereFormFactor( const in vec3 f ) {
	float l = length( f );
	return max( ( l * l + f.z ) / ( l + 1.0 ), 0.0 );
}
vec3 LTC_EdgeVectorFormFactor( const in vec3 v1, const in vec3 v2 ) {
	float x = dot( v1, v2 );
	float y = abs( x );
	float a = 0.8543985 + ( 0.4965155 + 0.0145206 * y ) * y;
	float b = 3.4175940 + ( 4.1616724 + y ) * y;
	float v = a / b;
	float theta_sintheta = ( x > 0.0 ) ? v : 0.5 * inversesqrt( max( 1.0 - x * x, 1e-7 ) ) - v;
	return cross( v1, v2 ) * theta_sintheta;
}
vec3 LTC_Evaluate( const in vec3 N, const in vec3 V, const in vec3 P, const in mat3 mInv, const in vec3 rectCoords[ 4 ] ) {
	vec3 v1 = rectCoords[ 1 ] - rectCoords[ 0 ];
	vec3 v2 = rectCoords[ 3 ] - rectCoords[ 0 ];
	vec3 lightNormal = cross( v1, v2 );
	if( dot( lightNormal, P - rectCoords[ 0 ] ) < 0.0 ) return vec3( 0.0 );
	vec3 T1, T2;
	T1 = normalize( V - N * dot( V, N ) );
	T2 = - cross( N, T1 );
	mat3 mat = mInv * transposeMat3( mat3( T1, T2, N ) );
	vec3 coords[ 4 ];
	coords[ 0 ] = mat * ( rectCoords[ 0 ] - P );
	coords[ 1 ] = mat * ( rectCoords[ 1 ] - P );
	coords[ 2 ] = mat * ( rectCoords[ 2 ] - P );
	coords[ 3 ] = mat * ( rectCoords[ 3 ] - P );
	coords[ 0 ] = normalize( coords[ 0 ] );
	coords[ 1 ] = normalize( coords[ 1 ] );
	coords[ 2 ] = normalize( coords[ 2 ] );
	coords[ 3 ] = normalize( coords[ 3 ] );
	vec3 vectorFormFactor = vec3( 0.0 );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 0 ], coords[ 1 ] );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 1 ], coords[ 2 ] );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 2 ], coords[ 3 ] );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 3 ], coords[ 0 ] );
	float result = LTC_ClippedSphereFormFactor( vectorFormFactor );
	return vec3( result );
}
#if defined( USE_SHEEN )
float D_Charlie( float roughness, float dotNH ) {
	float alpha = pow2( roughness );
	float invAlpha = 1.0 / alpha;
	float cos2h = dotNH * dotNH;
	float sin2h = max( 1.0 - cos2h, 0.0078125 );
	return ( 2.0 + invAlpha ) * pow( sin2h, invAlpha * 0.5 ) / ( 2.0 * PI );
}
float V_Neubelt( float dotNV, float dotNL ) {
	return saturate( 1.0 / ( 4.0 * ( dotNL + dotNV - dotNL * dotNV ) ) );
}
vec3 BRDF_Sheen( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, vec3 sheenColor, const in float sheenRoughness ) {
	vec3 halfDir = normalize( lightDir + viewDir );
	float dotNL = saturate( dot( normal, lightDir ) );
	float dotNV = saturate( dot( normal, viewDir ) );
	float dotNH = saturate( dot( normal, halfDir ) );
	float D = D_Charlie( sheenRoughness, dotNH );
	float V = V_Neubelt( dotNV, dotNL );
	return sheenColor * ( D * V );
}
#endif
float IBLSheenBRDF( const in vec3 normal, const in vec3 viewDir, const in float roughness ) {
	float dotNV = saturate( dot( normal, viewDir ) );
	float r2 = roughness * roughness;
	float a = roughness < 0.25 ? -339.2 * r2 + 161.4 * roughness - 25.9 : -8.48 * r2 + 14.3 * roughness - 9.95;
	float b = roughness < 0.25 ? 44.0 * r2 - 23.7 * roughness + 3.26 : 1.97 * r2 - 3.27 * roughness + 0.72;
	float DG = exp( a * dotNV + b ) + ( roughness < 0.25 ? 0.0 : 0.1 * ( roughness - 0.25 ) );
	return saturate( DG * RECIPROCAL_PI );
}
vec2 DFGApprox( const in vec3 normal, const in vec3 viewDir, const in float roughness ) {
	float dotNV = saturate( dot( normal, viewDir ) );
	const vec4 c0 = vec4( - 1, - 0.0275, - 0.572, 0.022 );
	const vec4 c1 = vec4( 1, 0.0425, 1.04, - 0.04 );
	vec4 r = roughness * c0 + c1;
	float a004 = min( r.x * r.x, exp2( - 9.28 * dotNV ) ) * r.x + r.y;
	vec2 fab = vec2( - 1.04, 1.04 ) * a004 + r.zw;
	return fab;
}
vec3 EnvironmentBRDF( const in vec3 normal, const in vec3 viewDir, const in vec3 specularColor, const in float specularF90, const in float roughness ) {
	vec2 fab = DFGApprox( normal, viewDir, roughness );
	return specularColor * fab.x + specularF90 * fab.y;
}
#ifdef USE_IRIDESCENCE
void computeMultiscatteringIridescence( const in vec3 normal, const in vec3 viewDir, const in vec3 specularColor, const in float specularF90, const in float iridescence, const in vec3 iridescenceF0, const in float roughness, inout vec3 singleScatter, inout vec3 multiScatter ) {
#else
void computeMultiscattering( const in vec3 normal, const in vec3 viewDir, const in vec3 specularColor, const in float specularF90, const in float roughness, inout vec3 singleScatter, inout vec3 multiScatter ) {
#endif
	vec2 fab = DFGApprox( normal, viewDir, roughness );
	#ifdef USE_IRIDESCENCE
		vec3 Fr = mix( specularColor, iridescenceF0, iridescence );
	#else
		vec3 Fr = specularColor;
	#endif
	vec3 FssEss = Fr * fab.x + specularF90 * fab.y;
	float Ess = fab.x + fab.y;
	float Ems = 1.0 - Ess;
	vec3 Favg = Fr + ( 1.0 - Fr ) * 0.047619;	vec3 Fms = FssEss * Favg / ( 1.0 - Ems * Favg );
	singleScatter += FssEss;
	multiScatter += Fms * Ems;
}
#if NUM_RECT_AREA_LIGHTS > 0
	void RE_Direct_RectArea_Physical( const in RectAreaLight rectAreaLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight ) {
		vec3 normal = geometryNormal;
		vec3 viewDir = geometryViewDir;
		vec3 position = geometryPosition;
		vec3 lightPos = rectAreaLight.position;
		vec3 halfWidth = rectAreaLight.halfWidth;
		vec3 halfHeight = rectAreaLight.halfHeight;
		vec3 lightColor = rectAreaLight.color;
		float roughness = material.roughness;
		vec3 rectCoords[ 4 ];
		rectCoords[ 0 ] = lightPos + halfWidth - halfHeight;		rectCoords[ 1 ] = lightPos - halfWidth - halfHeight;
		rectCoords[ 2 ] = lightPos - halfWidth + halfHeight;
		rectCoords[ 3 ] = lightPos + halfWidth + halfHeight;
		vec2 uv = LTC_Uv( normal, viewDir, roughness );
		vec4 t1 = texture2D( ltc_1, uv );
		vec4 t2 = texture2D( ltc_2, uv );
		mat3 mInv = mat3(
			vec3( t1.x, 0, t1.y ),
			vec3(    0, 1,    0 ),
			vec3( t1.z, 0, t1.w )
		);
		vec3 fresnel = ( material.specularColor * t2.x + ( vec3( 1.0 ) - material.specularColor ) * t2.y );
		reflectedLight.directSpecular += lightColor * fresnel * LTC_Evaluate( normal, viewDir, position, mInv, rectCoords );
		reflectedLight.directDiffuse += lightColor * material.diffuseColor * LTC_Evaluate( normal, viewDir, position, mat3( 1.0 ), rectCoords );
	}
#endif
void RE_Direct_Physical( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight ) {
	float dotNL = saturate( dot( geometryNormal, directLight.direction ) );
	vec3 irradiance = dotNL * directLight.color;
	#ifdef USE_CLEARCOAT
		float dotNLcc = saturate( dot( geometryClearcoatNormal, directLight.direction ) );
		vec3 ccIrradiance = dotNLcc * directLight.color;
		clearcoatSpecularDirect += ccIrradiance * BRDF_GGX_Clearcoat( directLight.direction, geometryViewDir, geometryClearcoatNormal, material );
	#endif
	#ifdef USE_SHEEN
		sheenSpecularDirect += irradiance * BRDF_Sheen( directLight.direction, geometryViewDir, geometryNormal, material.sheenColor, material.sheenRoughness );
	#endif
	reflectedLight.directSpecular += irradiance * BRDF_GGX( directLight.direction, geometryViewDir, geometryNormal, material );
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
void RE_IndirectDiffuse_Physical( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
void RE_IndirectSpecular_Physical( const in vec3 radiance, const in vec3 irradiance, const in vec3 clearcoatRadiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight) {
	#ifdef USE_CLEARCOAT
		clearcoatSpecularIndirect += clearcoatRadiance * EnvironmentBRDF( geometryClearcoatNormal, geometryViewDir, material.clearcoatF0, material.clearcoatF90, material.clearcoatRoughness );
	#endif
	#ifdef USE_SHEEN
		sheenSpecularIndirect += irradiance * material.sheenColor * IBLSheenBRDF( geometryNormal, geometryViewDir, material.sheenRoughness );
	#endif
	vec3 singleScattering = vec3( 0.0 );
	vec3 multiScattering = vec3( 0.0 );
	vec3 cosineWeightedIrradiance = irradiance * RECIPROCAL_PI;
	#ifdef USE_IRIDESCENCE
		computeMultiscatteringIridescence( geometryNormal, geometryViewDir, material.specularColor, material.specularF90, material.iridescence, material.iridescenceFresnel, material.roughness, singleScattering, multiScattering );
	#else
		computeMultiscattering( geometryNormal, geometryViewDir, material.specularColor, material.specularF90, material.roughness, singleScattering, multiScattering );
	#endif
	vec3 totalScattering = singleScattering + multiScattering;
	vec3 diffuse = material.diffuseColor * ( 1.0 - max( max( totalScattering.r, totalScattering.g ), totalScattering.b ) );
	reflectedLight.indirectSpecular += radiance * singleScattering;
	reflectedLight.indirectSpecular += multiScattering * cosineWeightedIrradiance;
	reflectedLight.indirectDiffuse += diffuse * cosineWeightedIrradiance;
}
#define RE_Direct				RE_Direct_Physical
#define RE_Direct_RectArea		RE_Direct_RectArea_Physical
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Physical
#define RE_IndirectSpecular		RE_IndirectSpecular_Physical
float computeSpecularOcclusion( const in float dotNV, const in float ambientOcclusion, const in float roughness ) {
	return saturate( pow( dotNV + ambientOcclusion, exp2( - 16.0 * roughness - 1.0 ) ) - 1.0 + ambientOcclusion );
}`,g_=`
vec3 geometryPosition = - vViewPosition;
vec3 geometryNormal = normal;
vec3 geometryViewDir = ( isOrthographic ) ? vec3( 0, 0, 1 ) : normalize( vViewPosition );
vec3 geometryClearcoatNormal = vec3( 0.0 );
#ifdef USE_CLEARCOAT
	geometryClearcoatNormal = clearcoatNormal;
#endif
#ifdef USE_IRIDESCENCE
	float dotNVi = saturate( dot( normal, geometryViewDir ) );
	if ( material.iridescenceThickness == 0.0 ) {
		material.iridescence = 0.0;
	} else {
		material.iridescence = saturate( material.iridescence );
	}
	if ( material.iridescence > 0.0 ) {
		material.iridescenceFresnel = evalIridescence( 1.0, material.iridescenceIOR, dotNVi, material.iridescenceThickness, material.specularColor );
		material.iridescenceF0 = Schlick_to_F0( material.iridescenceFresnel, 1.0, dotNVi );
	}
#endif
IncidentLight directLight;
#if ( NUM_POINT_LIGHTS > 0 ) && defined( RE_Direct )
	PointLight pointLight;
	#if defined( USE_SHADOWMAP ) && NUM_POINT_LIGHT_SHADOWS > 0
	PointLightShadow pointLightShadow;
	#endif
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_POINT_LIGHTS; i ++ ) {
		pointLight = pointLights[ i ];
		getPointLightInfo( pointLight, geometryPosition, directLight );
		#if defined( USE_SHADOWMAP ) && ( UNROLLED_LOOP_INDEX < NUM_POINT_LIGHT_SHADOWS )
		pointLightShadow = pointLightShadows[ i ];
		directLight.color *= ( directLight.visible && receiveShadow ) ? getPointShadow( pointShadowMap[ i ], pointLightShadow.shadowMapSize, pointLightShadow.shadowIntensity, pointLightShadow.shadowBias, pointLightShadow.shadowRadius, vPointShadowCoord[ i ], pointLightShadow.shadowCameraNear, pointLightShadow.shadowCameraFar ) : 1.0;
		#endif
		RE_Direct( directLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if ( NUM_SPOT_LIGHTS > 0 ) && defined( RE_Direct )
	SpotLight spotLight;
	vec4 spotColor;
	vec3 spotLightCoord;
	bool inSpotLightMap;
	#if defined( USE_SHADOWMAP ) && NUM_SPOT_LIGHT_SHADOWS > 0
	SpotLightShadow spotLightShadow;
	#endif
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_SPOT_LIGHTS; i ++ ) {
		spotLight = spotLights[ i ];
		getSpotLightInfo( spotLight, geometryPosition, directLight );
		#if ( UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS )
		#define SPOT_LIGHT_MAP_INDEX UNROLLED_LOOP_INDEX
		#elif ( UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS )
		#define SPOT_LIGHT_MAP_INDEX NUM_SPOT_LIGHT_MAPS
		#else
		#define SPOT_LIGHT_MAP_INDEX ( UNROLLED_LOOP_INDEX - NUM_SPOT_LIGHT_SHADOWS + NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS )
		#endif
		#if ( SPOT_LIGHT_MAP_INDEX < NUM_SPOT_LIGHT_MAPS )
			spotLightCoord = vSpotLightCoord[ i ].xyz / vSpotLightCoord[ i ].w;
			inSpotLightMap = all( lessThan( abs( spotLightCoord * 2. - 1. ), vec3( 1.0 ) ) );
			spotColor = texture2D( spotLightMap[ SPOT_LIGHT_MAP_INDEX ], spotLightCoord.xy );
			directLight.color = inSpotLightMap ? directLight.color * spotColor.rgb : directLight.color;
		#endif
		#undef SPOT_LIGHT_MAP_INDEX
		#if defined( USE_SHADOWMAP ) && ( UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS )
		spotLightShadow = spotLightShadows[ i ];
		directLight.color *= ( directLight.visible && receiveShadow ) ? getShadow( spotShadowMap[ i ], spotLightShadow.shadowMapSize, spotLightShadow.shadowIntensity, spotLightShadow.shadowBias, spotLightShadow.shadowRadius, vSpotLightCoord[ i ] ) : 1.0;
		#endif
		RE_Direct( directLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if ( NUM_DIR_LIGHTS > 0 ) && defined( RE_Direct )
	DirectionalLight directionalLight;
	#if defined( USE_SHADOWMAP ) && NUM_DIR_LIGHT_SHADOWS > 0
	DirectionalLightShadow directionalLightShadow;
	#endif
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_DIR_LIGHTS; i ++ ) {
		directionalLight = directionalLights[ i ];
		getDirectionalLightInfo( directionalLight, directLight );
		#if defined( USE_SHADOWMAP ) && ( UNROLLED_LOOP_INDEX < NUM_DIR_LIGHT_SHADOWS )
		directionalLightShadow = directionalLightShadows[ i ];
		directLight.color *= ( directLight.visible && receiveShadow ) ? getShadow( directionalShadowMap[ i ], directionalLightShadow.shadowMapSize, directionalLightShadow.shadowIntensity, directionalLightShadow.shadowBias, directionalLightShadow.shadowRadius, vDirectionalShadowCoord[ i ] ) : 1.0;
		#endif
		RE_Direct( directLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if ( NUM_RECT_AREA_LIGHTS > 0 ) && defined( RE_Direct_RectArea )
	RectAreaLight rectAreaLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_RECT_AREA_LIGHTS; i ++ ) {
		rectAreaLight = rectAreaLights[ i ];
		RE_Direct_RectArea( rectAreaLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if defined( RE_IndirectDiffuse )
	vec3 iblIrradiance = vec3( 0.0 );
	vec3 irradiance = getAmbientLightIrradiance( ambientLightColor );
	#if defined( USE_LIGHT_PROBES )
		irradiance += getLightProbeIrradiance( lightProbe, geometryNormal );
	#endif
	#if ( NUM_HEMI_LIGHTS > 0 )
		#pragma unroll_loop_start
		for ( int i = 0; i < NUM_HEMI_LIGHTS; i ++ ) {
			irradiance += getHemisphereLightIrradiance( hemisphereLights[ i ], geometryNormal );
		}
		#pragma unroll_loop_end
	#endif
#endif
#if defined( RE_IndirectSpecular )
	vec3 radiance = vec3( 0.0 );
	vec3 clearcoatRadiance = vec3( 0.0 );
#endif`,__=`#if defined( RE_IndirectDiffuse )
	#ifdef USE_LIGHTMAP
		vec4 lightMapTexel = texture2D( lightMap, vLightMapUv );
		vec3 lightMapIrradiance = lightMapTexel.rgb * lightMapIntensity;
		irradiance += lightMapIrradiance;
	#endif
	#if defined( USE_ENVMAP ) && defined( STANDARD ) && defined( ENVMAP_TYPE_CUBE_UV )
		iblIrradiance += getIBLIrradiance( geometryNormal );
	#endif
#endif
#if defined( USE_ENVMAP ) && defined( RE_IndirectSpecular )
	#ifdef USE_ANISOTROPY
		radiance += getIBLAnisotropyRadiance( geometryViewDir, geometryNormal, material.roughness, material.anisotropyB, material.anisotropy );
	#else
		radiance += getIBLRadiance( geometryViewDir, geometryNormal, material.roughness );
	#endif
	#ifdef USE_CLEARCOAT
		clearcoatRadiance += getIBLRadiance( geometryViewDir, geometryClearcoatNormal, material.clearcoatRoughness );
	#endif
#endif`,v_=`#if defined( RE_IndirectDiffuse )
	RE_IndirectDiffuse( irradiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif
#if defined( RE_IndirectSpecular )
	RE_IndirectSpecular( radiance, iblIrradiance, clearcoatRadiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif`,x_=`#if defined( USE_LOGDEPTHBUF )
	gl_FragDepth = vIsPerspective == 0.0 ? gl_FragCoord.z : log2( vFragDepth ) * logDepthBufFC * 0.5;
#endif`,y_=`#if defined( USE_LOGDEPTHBUF )
	uniform float logDepthBufFC;
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,M_=`#ifdef USE_LOGDEPTHBUF
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,S_=`#ifdef USE_LOGDEPTHBUF
	vFragDepth = 1.0 + gl_Position.w;
	vIsPerspective = float( isPerspectiveMatrix( projectionMatrix ) );
#endif`,E_=`#ifdef USE_MAP
	vec4 sampledDiffuseColor = texture2D( map, vMapUv );
	#ifdef DECODE_VIDEO_TEXTURE
		sampledDiffuseColor = vec4( mix( pow( sampledDiffuseColor.rgb * 0.9478672986 + vec3( 0.0521327014 ), vec3( 2.4 ) ), sampledDiffuseColor.rgb * 0.0773993808, vec3( lessThanEqual( sampledDiffuseColor.rgb, vec3( 0.04045 ) ) ) ), sampledDiffuseColor.w );
	
	#endif
	diffuseColor *= sampledDiffuseColor;
#endif`,b_=`#ifdef USE_MAP
	uniform sampler2D map;
#endif`,T_=`#if defined( USE_MAP ) || defined( USE_ALPHAMAP )
	#if defined( USE_POINTS_UV )
		vec2 uv = vUv;
	#else
		vec2 uv = ( uvTransform * vec3( gl_PointCoord.x, 1.0 - gl_PointCoord.y, 1 ) ).xy;
	#endif
#endif
#ifdef USE_MAP
	diffuseColor *= texture2D( map, uv );
#endif
#ifdef USE_ALPHAMAP
	diffuseColor.a *= texture2D( alphaMap, uv ).g;
#endif`,w_=`#if defined( USE_POINTS_UV )
	varying vec2 vUv;
#else
	#if defined( USE_MAP ) || defined( USE_ALPHAMAP )
		uniform mat3 uvTransform;
	#endif
#endif
#ifdef USE_MAP
	uniform sampler2D map;
#endif
#ifdef USE_ALPHAMAP
	uniform sampler2D alphaMap;
#endif`,A_=`float metalnessFactor = metalness;
#ifdef USE_METALNESSMAP
	vec4 texelMetalness = texture2D( metalnessMap, vMetalnessMapUv );
	metalnessFactor *= texelMetalness.b;
#endif`,R_=`#ifdef USE_METALNESSMAP
	uniform sampler2D metalnessMap;
#endif`,C_=`#ifdef USE_INSTANCING_MORPH
	float morphTargetInfluences[ MORPHTARGETS_COUNT ];
	float morphTargetBaseInfluence = texelFetch( morphTexture, ivec2( 0, gl_InstanceID ), 0 ).r;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		morphTargetInfluences[i] =  texelFetch( morphTexture, ivec2( i + 1, gl_InstanceID ), 0 ).r;
	}
#endif`,P_=`#if defined( USE_MORPHCOLORS )
	vColor *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		#if defined( USE_COLOR_ALPHA )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ) * morphTargetInfluences[ i ];
		#elif defined( USE_COLOR )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ).rgb * morphTargetInfluences[ i ];
		#endif
	}
#endif`,L_=`#ifdef USE_MORPHNORMALS
	objectNormal *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) objectNormal += getMorph( gl_VertexID, i, 1 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,D_=`#ifdef USE_MORPHTARGETS
	#ifndef USE_INSTANCING_MORPH
		uniform float morphTargetBaseInfluence;
		uniform float morphTargetInfluences[ MORPHTARGETS_COUNT ];
	#endif
	uniform sampler2DArray morphTargetsTexture;
	uniform ivec2 morphTargetsTextureSize;
	vec4 getMorph( const in int vertexIndex, const in int morphTargetIndex, const in int offset ) {
		int texelIndex = vertexIndex * MORPHTARGETS_TEXTURE_STRIDE + offset;
		int y = texelIndex / morphTargetsTextureSize.x;
		int x = texelIndex - y * morphTargetsTextureSize.x;
		ivec3 morphUV = ivec3( x, y, morphTargetIndex );
		return texelFetch( morphTargetsTexture, morphUV, 0 );
	}
#endif`,I_=`#ifdef USE_MORPHTARGETS
	transformed *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) transformed += getMorph( gl_VertexID, i, 0 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,U_=`float faceDirection = gl_FrontFacing ? 1.0 : - 1.0;
#ifdef FLAT_SHADED
	vec3 fdx = dFdx( vViewPosition );
	vec3 fdy = dFdy( vViewPosition );
	vec3 normal = normalize( cross( fdx, fdy ) );
#else
	vec3 normal = normalize( vNormal );
	#ifdef DOUBLE_SIDED
		normal *= faceDirection;
	#endif
#endif
#if defined( USE_NORMALMAP_TANGENTSPACE ) || defined( USE_CLEARCOAT_NORMALMAP ) || defined( USE_ANISOTROPY )
	#ifdef USE_TANGENT
		mat3 tbn = mat3( normalize( vTangent ), normalize( vBitangent ), normal );
	#else
		mat3 tbn = getTangentFrame( - vViewPosition, normal,
		#if defined( USE_NORMALMAP )
			vNormalMapUv
		#elif defined( USE_CLEARCOAT_NORMALMAP )
			vClearcoatNormalMapUv
		#else
			vUv
		#endif
		);
	#endif
	#if defined( DOUBLE_SIDED ) && ! defined( FLAT_SHADED )
		tbn[0] *= faceDirection;
		tbn[1] *= faceDirection;
	#endif
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	#ifdef USE_TANGENT
		mat3 tbn2 = mat3( normalize( vTangent ), normalize( vBitangent ), normal );
	#else
		mat3 tbn2 = getTangentFrame( - vViewPosition, normal, vClearcoatNormalMapUv );
	#endif
	#if defined( DOUBLE_SIDED ) && ! defined( FLAT_SHADED )
		tbn2[0] *= faceDirection;
		tbn2[1] *= faceDirection;
	#endif
#endif
vec3 nonPerturbedNormal = normal;`,N_=`#ifdef USE_NORMALMAP_OBJECTSPACE
	normal = texture2D( normalMap, vNormalMapUv ).xyz * 2.0 - 1.0;
	#ifdef FLIP_SIDED
		normal = - normal;
	#endif
	#ifdef DOUBLE_SIDED
		normal = normal * faceDirection;
	#endif
	normal = normalize( normalMatrix * normal );
#elif defined( USE_NORMALMAP_TANGENTSPACE )
	vec3 mapN = texture2D( normalMap, vNormalMapUv ).xyz * 2.0 - 1.0;
	mapN.xy *= normalScale;
	normal = normalize( tbn * mapN );
#elif defined( USE_BUMPMAP )
	normal = perturbNormalArb( - vViewPosition, normal, dHdxy_fwd(), faceDirection );
#endif`,F_=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,O_=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,B_=`#ifndef FLAT_SHADED
	vNormal = normalize( transformedNormal );
	#ifdef USE_TANGENT
		vTangent = normalize( transformedTangent );
		vBitangent = normalize( cross( vNormal, vTangent ) * tangent.w );
	#endif
#endif`,z_=`#ifdef USE_NORMALMAP
	uniform sampler2D normalMap;
	uniform vec2 normalScale;
#endif
#ifdef USE_NORMALMAP_OBJECTSPACE
	uniform mat3 normalMatrix;
#endif
#if ! defined ( USE_TANGENT ) && ( defined ( USE_NORMALMAP_TANGENTSPACE ) || defined ( USE_CLEARCOAT_NORMALMAP ) || defined( USE_ANISOTROPY ) )
	mat3 getTangentFrame( vec3 eye_pos, vec3 surf_norm, vec2 uv ) {
		vec3 q0 = dFdx( eye_pos.xyz );
		vec3 q1 = dFdy( eye_pos.xyz );
		vec2 st0 = dFdx( uv.st );
		vec2 st1 = dFdy( uv.st );
		vec3 N = surf_norm;
		vec3 q1perp = cross( q1, N );
		vec3 q0perp = cross( N, q0 );
		vec3 T = q1perp * st0.x + q0perp * st1.x;
		vec3 B = q1perp * st0.y + q0perp * st1.y;
		float det = max( dot( T, T ), dot( B, B ) );
		float scale = ( det == 0.0 ) ? 0.0 : inversesqrt( det );
		return mat3( T * scale, B * scale, N );
	}
#endif`,k_=`#ifdef USE_CLEARCOAT
	vec3 clearcoatNormal = nonPerturbedNormal;
#endif`,H_=`#ifdef USE_CLEARCOAT_NORMALMAP
	vec3 clearcoatMapN = texture2D( clearcoatNormalMap, vClearcoatNormalMapUv ).xyz * 2.0 - 1.0;
	clearcoatMapN.xy *= clearcoatNormalScale;
	clearcoatNormal = normalize( tbn2 * clearcoatMapN );
#endif`,V_=`#ifdef USE_CLEARCOATMAP
	uniform sampler2D clearcoatMap;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	uniform sampler2D clearcoatNormalMap;
	uniform vec2 clearcoatNormalScale;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	uniform sampler2D clearcoatRoughnessMap;
#endif`,G_=`#ifdef USE_IRIDESCENCEMAP
	uniform sampler2D iridescenceMap;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	uniform sampler2D iridescenceThicknessMap;
#endif`,W_=`#ifdef OPAQUE
diffuseColor.a = 1.0;
#endif
#ifdef USE_TRANSMISSION
diffuseColor.a *= material.transmissionAlpha;
#endif
gl_FragColor = vec4( outgoingLight, diffuseColor.a );`,X_=`vec3 packNormalToRGB( const in vec3 normal ) {
	return normalize( normal ) * 0.5 + 0.5;
}
vec3 unpackRGBToNormal( const in vec3 rgb ) {
	return 2.0 * rgb.xyz - 1.0;
}
const float PackUpscale = 256. / 255.;const float UnpackDownscale = 255. / 256.;const float ShiftRight8 = 1. / 256.;
const float Inv255 = 1. / 255.;
const vec4 PackFactors = vec4( 1.0, 256.0, 256.0 * 256.0, 256.0 * 256.0 * 256.0 );
const vec2 UnpackFactors2 = vec2( UnpackDownscale, 1.0 / PackFactors.g );
const vec3 UnpackFactors3 = vec3( UnpackDownscale / PackFactors.rg, 1.0 / PackFactors.b );
const vec4 UnpackFactors4 = vec4( UnpackDownscale / PackFactors.rgb, 1.0 / PackFactors.a );
vec4 packDepthToRGBA( const in float v ) {
	if( v <= 0.0 )
		return vec4( 0., 0., 0., 0. );
	if( v >= 1.0 )
		return vec4( 1., 1., 1., 1. );
	float vuf;
	float af = modf( v * PackFactors.a, vuf );
	float bf = modf( vuf * ShiftRight8, vuf );
	float gf = modf( vuf * ShiftRight8, vuf );
	return vec4( vuf * Inv255, gf * PackUpscale, bf * PackUpscale, af );
}
vec3 packDepthToRGB( const in float v ) {
	if( v <= 0.0 )
		return vec3( 0., 0., 0. );
	if( v >= 1.0 )
		return vec3( 1., 1., 1. );
	float vuf;
	float bf = modf( v * PackFactors.b, vuf );
	float gf = modf( vuf * ShiftRight8, vuf );
	return vec3( vuf * Inv255, gf * PackUpscale, bf );
}
vec2 packDepthToRG( const in float v ) {
	if( v <= 0.0 )
		return vec2( 0., 0. );
	if( v >= 1.0 )
		return vec2( 1., 1. );
	float vuf;
	float gf = modf( v * 256., vuf );
	return vec2( vuf * Inv255, gf );
}
float unpackRGBAToDepth( const in vec4 v ) {
	return dot( v, UnpackFactors4 );
}
float unpackRGBToDepth( const in vec3 v ) {
	return dot( v, UnpackFactors3 );
}
float unpackRGToDepth( const in vec2 v ) {
	return v.r * UnpackFactors2.r + v.g * UnpackFactors2.g;
}
vec4 pack2HalfToRGBA( const in vec2 v ) {
	vec4 r = vec4( v.x, fract( v.x * 255.0 ), v.y, fract( v.y * 255.0 ) );
	return vec4( r.x - r.y / 255.0, r.y, r.z - r.w / 255.0, r.w );
}
vec2 unpackRGBATo2Half( const in vec4 v ) {
	return vec2( v.x + ( v.y / 255.0 ), v.z + ( v.w / 255.0 ) );
}
float viewZToOrthographicDepth( const in float viewZ, const in float near, const in float far ) {
	return ( viewZ + near ) / ( near - far );
}
float orthographicDepthToViewZ( const in float depth, const in float near, const in float far ) {
	return depth * ( near - far ) - near;
}
float viewZToPerspectiveDepth( const in float viewZ, const in float near, const in float far ) {
	return ( ( near + viewZ ) * far ) / ( ( far - near ) * viewZ );
}
float perspectiveDepthToViewZ( const in float depth, const in float near, const in float far ) {
	return ( near * far ) / ( ( far - near ) * depth - far );
}`,q_=`#ifdef PREMULTIPLIED_ALPHA
	gl_FragColor.rgb *= gl_FragColor.a;
#endif`,Y_=`vec4 mvPosition = vec4( transformed, 1.0 );
#ifdef USE_BATCHING
	mvPosition = batchingMatrix * mvPosition;
#endif
#ifdef USE_INSTANCING
	mvPosition = instanceMatrix * mvPosition;
#endif
mvPosition = modelViewMatrix * mvPosition;
gl_Position = projectionMatrix * mvPosition;`,$_=`#ifdef DITHERING
	gl_FragColor.rgb = dithering( gl_FragColor.rgb );
#endif`,j_=`#ifdef DITHERING
	vec3 dithering( vec3 color ) {
		float grid_position = rand( gl_FragCoord.xy );
		vec3 dither_shift_RGB = vec3( 0.25 / 255.0, -0.25 / 255.0, 0.25 / 255.0 );
		dither_shift_RGB = mix( 2.0 * dither_shift_RGB, -2.0 * dither_shift_RGB, grid_position );
		return color + dither_shift_RGB;
	}
#endif`,K_=`float roughnessFactor = roughness;
#ifdef USE_ROUGHNESSMAP
	vec4 texelRoughness = texture2D( roughnessMap, vRoughnessMapUv );
	roughnessFactor *= texelRoughness.g;
#endif`,Z_=`#ifdef USE_ROUGHNESSMAP
	uniform sampler2D roughnessMap;
#endif`,J_=`#if NUM_SPOT_LIGHT_COORDS > 0
	varying vec4 vSpotLightCoord[ NUM_SPOT_LIGHT_COORDS ];
#endif
#if NUM_SPOT_LIGHT_MAPS > 0
	uniform sampler2D spotLightMap[ NUM_SPOT_LIGHT_MAPS ];
#endif
#ifdef USE_SHADOWMAP
	#if NUM_DIR_LIGHT_SHADOWS > 0
		uniform sampler2D directionalShadowMap[ NUM_DIR_LIGHT_SHADOWS ];
		varying vec4 vDirectionalShadowCoord[ NUM_DIR_LIGHT_SHADOWS ];
		struct DirectionalLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform DirectionalLightShadow directionalLightShadows[ NUM_DIR_LIGHT_SHADOWS ];
	#endif
	#if NUM_SPOT_LIGHT_SHADOWS > 0
		uniform sampler2D spotShadowMap[ NUM_SPOT_LIGHT_SHADOWS ];
		struct SpotLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform SpotLightShadow spotLightShadows[ NUM_SPOT_LIGHT_SHADOWS ];
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
		uniform sampler2D pointShadowMap[ NUM_POINT_LIGHT_SHADOWS ];
		varying vec4 vPointShadowCoord[ NUM_POINT_LIGHT_SHADOWS ];
		struct PointLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
			float shadowCameraNear;
			float shadowCameraFar;
		};
		uniform PointLightShadow pointLightShadows[ NUM_POINT_LIGHT_SHADOWS ];
	#endif
	float texture2DCompare( sampler2D depths, vec2 uv, float compare ) {
		return step( compare, unpackRGBAToDepth( texture2D( depths, uv ) ) );
	}
	vec2 texture2DDistribution( sampler2D shadow, vec2 uv ) {
		return unpackRGBATo2Half( texture2D( shadow, uv ) );
	}
	float VSMShadow (sampler2D shadow, vec2 uv, float compare ){
		float occlusion = 1.0;
		vec2 distribution = texture2DDistribution( shadow, uv );
		float hard_shadow = step( compare , distribution.x );
		if (hard_shadow != 1.0 ) {
			float distance = compare - distribution.x ;
			float variance = max( 0.00000, distribution.y * distribution.y );
			float softness_probability = variance / (variance + distance * distance );			softness_probability = clamp( ( softness_probability - 0.3 ) / ( 0.95 - 0.3 ), 0.0, 1.0 );			occlusion = clamp( max( hard_shadow, softness_probability ), 0.0, 1.0 );
		}
		return occlusion;
	}
	float getShadow( sampler2D shadowMap, vec2 shadowMapSize, float shadowIntensity, float shadowBias, float shadowRadius, vec4 shadowCoord ) {
		float shadow = 1.0;
		shadowCoord.xyz /= shadowCoord.w;
		shadowCoord.z += shadowBias;
		bool inFrustum = shadowCoord.x >= 0.0 && shadowCoord.x <= 1.0 && shadowCoord.y >= 0.0 && shadowCoord.y <= 1.0;
		bool frustumTest = inFrustum && shadowCoord.z <= 1.0;
		if ( frustumTest ) {
		#if defined( SHADOWMAP_TYPE_PCF )
			vec2 texelSize = vec2( 1.0 ) / shadowMapSize;
			float dx0 = - texelSize.x * shadowRadius;
			float dy0 = - texelSize.y * shadowRadius;
			float dx1 = + texelSize.x * shadowRadius;
			float dy1 = + texelSize.y * shadowRadius;
			float dx2 = dx0 / 2.0;
			float dy2 = dy0 / 2.0;
			float dx3 = dx1 / 2.0;
			float dy3 = dy1 / 2.0;
			shadow = (
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx0, dy0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( 0.0, dy0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx1, dy0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx2, dy2 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( 0.0, dy2 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx3, dy2 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx0, 0.0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx2, 0.0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy, shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx3, 0.0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx1, 0.0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx2, dy3 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( 0.0, dy3 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx3, dy3 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx0, dy1 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( 0.0, dy1 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx1, dy1 ), shadowCoord.z )
			) * ( 1.0 / 17.0 );
		#elif defined( SHADOWMAP_TYPE_PCF_SOFT )
			vec2 texelSize = vec2( 1.0 ) / shadowMapSize;
			float dx = texelSize.x;
			float dy = texelSize.y;
			vec2 uv = shadowCoord.xy;
			vec2 f = fract( uv * shadowMapSize + 0.5 );
			uv -= f * texelSize;
			shadow = (
				texture2DCompare( shadowMap, uv, shadowCoord.z ) +
				texture2DCompare( shadowMap, uv + vec2( dx, 0.0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, uv + vec2( 0.0, dy ), shadowCoord.z ) +
				texture2DCompare( shadowMap, uv + texelSize, shadowCoord.z ) +
				mix( texture2DCompare( shadowMap, uv + vec2( -dx, 0.0 ), shadowCoord.z ),
					 texture2DCompare( shadowMap, uv + vec2( 2.0 * dx, 0.0 ), shadowCoord.z ),
					 f.x ) +
				mix( texture2DCompare( shadowMap, uv + vec2( -dx, dy ), shadowCoord.z ),
					 texture2DCompare( shadowMap, uv + vec2( 2.0 * dx, dy ), shadowCoord.z ),
					 f.x ) +
				mix( texture2DCompare( shadowMap, uv + vec2( 0.0, -dy ), shadowCoord.z ),
					 texture2DCompare( shadowMap, uv + vec2( 0.0, 2.0 * dy ), shadowCoord.z ),
					 f.y ) +
				mix( texture2DCompare( shadowMap, uv + vec2( dx, -dy ), shadowCoord.z ),
					 texture2DCompare( shadowMap, uv + vec2( dx, 2.0 * dy ), shadowCoord.z ),
					 f.y ) +
				mix( mix( texture2DCompare( shadowMap, uv + vec2( -dx, -dy ), shadowCoord.z ),
						  texture2DCompare( shadowMap, uv + vec2( 2.0 * dx, -dy ), shadowCoord.z ),
						  f.x ),
					 mix( texture2DCompare( shadowMap, uv + vec2( -dx, 2.0 * dy ), shadowCoord.z ),
						  texture2DCompare( shadowMap, uv + vec2( 2.0 * dx, 2.0 * dy ), shadowCoord.z ),
						  f.x ),
					 f.y )
			) * ( 1.0 / 9.0 );
		#elif defined( SHADOWMAP_TYPE_VSM )
			shadow = VSMShadow( shadowMap, shadowCoord.xy, shadowCoord.z );
		#else
			shadow = texture2DCompare( shadowMap, shadowCoord.xy, shadowCoord.z );
		#endif
		}
		return mix( 1.0, shadow, shadowIntensity );
	}
	vec2 cubeToUV( vec3 v, float texelSizeY ) {
		vec3 absV = abs( v );
		float scaleToCube = 1.0 / max( absV.x, max( absV.y, absV.z ) );
		absV *= scaleToCube;
		v *= scaleToCube * ( 1.0 - 2.0 * texelSizeY );
		vec2 planar = v.xy;
		float almostATexel = 1.5 * texelSizeY;
		float almostOne = 1.0 - almostATexel;
		if ( absV.z >= almostOne ) {
			if ( v.z > 0.0 )
				planar.x = 4.0 - v.x;
		} else if ( absV.x >= almostOne ) {
			float signX = sign( v.x );
			planar.x = v.z * signX + 2.0 * signX;
		} else if ( absV.y >= almostOne ) {
			float signY = sign( v.y );
			planar.x = v.x + 2.0 * signY + 2.0;
			planar.y = v.z * signY - 2.0;
		}
		return vec2( 0.125, 0.25 ) * planar + vec2( 0.375, 0.75 );
	}
	float getPointShadow( sampler2D shadowMap, vec2 shadowMapSize, float shadowIntensity, float shadowBias, float shadowRadius, vec4 shadowCoord, float shadowCameraNear, float shadowCameraFar ) {
		float shadow = 1.0;
		vec3 lightToPosition = shadowCoord.xyz;
		
		float lightToPositionLength = length( lightToPosition );
		if ( lightToPositionLength - shadowCameraFar <= 0.0 && lightToPositionLength - shadowCameraNear >= 0.0 ) {
			float dp = ( lightToPositionLength - shadowCameraNear ) / ( shadowCameraFar - shadowCameraNear );			dp += shadowBias;
			vec3 bd3D = normalize( lightToPosition );
			vec2 texelSize = vec2( 1.0 ) / ( shadowMapSize * vec2( 4.0, 2.0 ) );
			#if defined( SHADOWMAP_TYPE_PCF ) || defined( SHADOWMAP_TYPE_PCF_SOFT ) || defined( SHADOWMAP_TYPE_VSM )
				vec2 offset = vec2( - 1, 1 ) * shadowRadius * texelSize.y;
				shadow = (
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.xyy, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.yyy, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.xyx, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.yyx, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.xxy, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.yxy, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.xxx, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.yxx, texelSize.y ), dp )
				) * ( 1.0 / 9.0 );
			#else
				shadow = texture2DCompare( shadowMap, cubeToUV( bd3D, texelSize.y ), dp );
			#endif
		}
		return mix( 1.0, shadow, shadowIntensity );
	}
#endif`,Q_=`#if NUM_SPOT_LIGHT_COORDS > 0
	uniform mat4 spotLightMatrix[ NUM_SPOT_LIGHT_COORDS ];
	varying vec4 vSpotLightCoord[ NUM_SPOT_LIGHT_COORDS ];
#endif
#ifdef USE_SHADOWMAP
	#if NUM_DIR_LIGHT_SHADOWS > 0
		uniform mat4 directionalShadowMatrix[ NUM_DIR_LIGHT_SHADOWS ];
		varying vec4 vDirectionalShadowCoord[ NUM_DIR_LIGHT_SHADOWS ];
		struct DirectionalLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform DirectionalLightShadow directionalLightShadows[ NUM_DIR_LIGHT_SHADOWS ];
	#endif
	#if NUM_SPOT_LIGHT_SHADOWS > 0
		struct SpotLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform SpotLightShadow spotLightShadows[ NUM_SPOT_LIGHT_SHADOWS ];
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
		uniform mat4 pointShadowMatrix[ NUM_POINT_LIGHT_SHADOWS ];
		varying vec4 vPointShadowCoord[ NUM_POINT_LIGHT_SHADOWS ];
		struct PointLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
			float shadowCameraNear;
			float shadowCameraFar;
		};
		uniform PointLightShadow pointLightShadows[ NUM_POINT_LIGHT_SHADOWS ];
	#endif
#endif`,e0=`#if ( defined( USE_SHADOWMAP ) && ( NUM_DIR_LIGHT_SHADOWS > 0 || NUM_POINT_LIGHT_SHADOWS > 0 ) ) || ( NUM_SPOT_LIGHT_COORDS > 0 )
	vec3 shadowWorldNormal = inverseTransformDirection( transformedNormal, viewMatrix );
	vec4 shadowWorldPosition;
#endif
#if defined( USE_SHADOWMAP )
	#if NUM_DIR_LIGHT_SHADOWS > 0
		#pragma unroll_loop_start
		for ( int i = 0; i < NUM_DIR_LIGHT_SHADOWS; i ++ ) {
			shadowWorldPosition = worldPosition + vec4( shadowWorldNormal * directionalLightShadows[ i ].shadowNormalBias, 0 );
			vDirectionalShadowCoord[ i ] = directionalShadowMatrix[ i ] * shadowWorldPosition;
		}
		#pragma unroll_loop_end
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
		#pragma unroll_loop_start
		for ( int i = 0; i < NUM_POINT_LIGHT_SHADOWS; i ++ ) {
			shadowWorldPosition = worldPosition + vec4( shadowWorldNormal * pointLightShadows[ i ].shadowNormalBias, 0 );
			vPointShadowCoord[ i ] = pointShadowMatrix[ i ] * shadowWorldPosition;
		}
		#pragma unroll_loop_end
	#endif
#endif
#if NUM_SPOT_LIGHT_COORDS > 0
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_SPOT_LIGHT_COORDS; i ++ ) {
		shadowWorldPosition = worldPosition;
		#if ( defined( USE_SHADOWMAP ) && UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS )
			shadowWorldPosition.xyz += shadowWorldNormal * spotLightShadows[ i ].shadowNormalBias;
		#endif
		vSpotLightCoord[ i ] = spotLightMatrix[ i ] * shadowWorldPosition;
	}
	#pragma unroll_loop_end
#endif`,t0=`float getShadowMask() {
	float shadow = 1.0;
	#ifdef USE_SHADOWMAP
	#if NUM_DIR_LIGHT_SHADOWS > 0
	DirectionalLightShadow directionalLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_DIR_LIGHT_SHADOWS; i ++ ) {
		directionalLight = directionalLightShadows[ i ];
		shadow *= receiveShadow ? getShadow( directionalShadowMap[ i ], directionalLight.shadowMapSize, directionalLight.shadowIntensity, directionalLight.shadowBias, directionalLight.shadowRadius, vDirectionalShadowCoord[ i ] ) : 1.0;
	}
	#pragma unroll_loop_end
	#endif
	#if NUM_SPOT_LIGHT_SHADOWS > 0
	SpotLightShadow spotLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_SPOT_LIGHT_SHADOWS; i ++ ) {
		spotLight = spotLightShadows[ i ];
		shadow *= receiveShadow ? getShadow( spotShadowMap[ i ], spotLight.shadowMapSize, spotLight.shadowIntensity, spotLight.shadowBias, spotLight.shadowRadius, vSpotLightCoord[ i ] ) : 1.0;
	}
	#pragma unroll_loop_end
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
	PointLightShadow pointLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_POINT_LIGHT_SHADOWS; i ++ ) {
		pointLight = pointLightShadows[ i ];
		shadow *= receiveShadow ? getPointShadow( pointShadowMap[ i ], pointLight.shadowMapSize, pointLight.shadowIntensity, pointLight.shadowBias, pointLight.shadowRadius, vPointShadowCoord[ i ], pointLight.shadowCameraNear, pointLight.shadowCameraFar ) : 1.0;
	}
	#pragma unroll_loop_end
	#endif
	#endif
	return shadow;
}`,n0=`#ifdef USE_SKINNING
	mat4 boneMatX = getBoneMatrix( skinIndex.x );
	mat4 boneMatY = getBoneMatrix( skinIndex.y );
	mat4 boneMatZ = getBoneMatrix( skinIndex.z );
	mat4 boneMatW = getBoneMatrix( skinIndex.w );
#endif`,i0=`#ifdef USE_SKINNING
	uniform mat4 bindMatrix;
	uniform mat4 bindMatrixInverse;
	uniform highp sampler2D boneTexture;
	mat4 getBoneMatrix( const in float i ) {
		int size = textureSize( boneTexture, 0 ).x;
		int j = int( i ) * 4;
		int x = j % size;
		int y = j / size;
		vec4 v1 = texelFetch( boneTexture, ivec2( x, y ), 0 );
		vec4 v2 = texelFetch( boneTexture, ivec2( x + 1, y ), 0 );
		vec4 v3 = texelFetch( boneTexture, ivec2( x + 2, y ), 0 );
		vec4 v4 = texelFetch( boneTexture, ivec2( x + 3, y ), 0 );
		return mat4( v1, v2, v3, v4 );
	}
#endif`,r0=`#ifdef USE_SKINNING
	vec4 skinVertex = bindMatrix * vec4( transformed, 1.0 );
	vec4 skinned = vec4( 0.0 );
	skinned += boneMatX * skinVertex * skinWeight.x;
	skinned += boneMatY * skinVertex * skinWeight.y;
	skinned += boneMatZ * skinVertex * skinWeight.z;
	skinned += boneMatW * skinVertex * skinWeight.w;
	transformed = ( bindMatrixInverse * skinned ).xyz;
#endif`,s0=`#ifdef USE_SKINNING
	mat4 skinMatrix = mat4( 0.0 );
	skinMatrix += skinWeight.x * boneMatX;
	skinMatrix += skinWeight.y * boneMatY;
	skinMatrix += skinWeight.z * boneMatZ;
	skinMatrix += skinWeight.w * boneMatW;
	skinMatrix = bindMatrixInverse * skinMatrix * bindMatrix;
	objectNormal = vec4( skinMatrix * vec4( objectNormal, 0.0 ) ).xyz;
	#ifdef USE_TANGENT
		objectTangent = vec4( skinMatrix * vec4( objectTangent, 0.0 ) ).xyz;
	#endif
#endif`,a0=`float specularStrength;
#ifdef USE_SPECULARMAP
	vec4 texelSpecular = texture2D( specularMap, vSpecularMapUv );
	specularStrength = texelSpecular.r;
#else
	specularStrength = 1.0;
#endif`,o0=`#ifdef USE_SPECULARMAP
	uniform sampler2D specularMap;
#endif`,l0=`#if defined( TONE_MAPPING )
	gl_FragColor.rgb = toneMapping( gl_FragColor.rgb );
#endif`,c0=`#ifndef saturate
#define saturate( a ) clamp( a, 0.0, 1.0 )
#endif
uniform float toneMappingExposure;
vec3 LinearToneMapping( vec3 color ) {
	return saturate( toneMappingExposure * color );
}
vec3 ReinhardToneMapping( vec3 color ) {
	color *= toneMappingExposure;
	return saturate( color / ( vec3( 1.0 ) + color ) );
}
vec3 CineonToneMapping( vec3 color ) {
	color *= toneMappingExposure;
	color = max( vec3( 0.0 ), color - 0.004 );
	return pow( ( color * ( 6.2 * color + 0.5 ) ) / ( color * ( 6.2 * color + 1.7 ) + 0.06 ), vec3( 2.2 ) );
}
vec3 RRTAndODTFit( vec3 v ) {
	vec3 a = v * ( v + 0.0245786 ) - 0.000090537;
	vec3 b = v * ( 0.983729 * v + 0.4329510 ) + 0.238081;
	return a / b;
}
vec3 ACESFilmicToneMapping( vec3 color ) {
	const mat3 ACESInputMat = mat3(
		vec3( 0.59719, 0.07600, 0.02840 ),		vec3( 0.35458, 0.90834, 0.13383 ),
		vec3( 0.04823, 0.01566, 0.83777 )
	);
	const mat3 ACESOutputMat = mat3(
		vec3(  1.60475, -0.10208, -0.00327 ),		vec3( -0.53108,  1.10813, -0.07276 ),
		vec3( -0.07367, -0.00605,  1.07602 )
	);
	color *= toneMappingExposure / 0.6;
	color = ACESInputMat * color;
	color = RRTAndODTFit( color );
	color = ACESOutputMat * color;
	return saturate( color );
}
const mat3 LINEAR_REC2020_TO_LINEAR_SRGB = mat3(
	vec3( 1.6605, - 0.1246, - 0.0182 ),
	vec3( - 0.5876, 1.1329, - 0.1006 ),
	vec3( - 0.0728, - 0.0083, 1.1187 )
);
const mat3 LINEAR_SRGB_TO_LINEAR_REC2020 = mat3(
	vec3( 0.6274, 0.0691, 0.0164 ),
	vec3( 0.3293, 0.9195, 0.0880 ),
	vec3( 0.0433, 0.0113, 0.8956 )
);
vec3 agxDefaultContrastApprox( vec3 x ) {
	vec3 x2 = x * x;
	vec3 x4 = x2 * x2;
	return + 15.5 * x4 * x2
		- 40.14 * x4 * x
		+ 31.96 * x4
		- 6.868 * x2 * x
		+ 0.4298 * x2
		+ 0.1191 * x
		- 0.00232;
}
vec3 AgXToneMapping( vec3 color ) {
	const mat3 AgXInsetMatrix = mat3(
		vec3( 0.856627153315983, 0.137318972929847, 0.11189821299995 ),
		vec3( 0.0951212405381588, 0.761241990602591, 0.0767994186031903 ),
		vec3( 0.0482516061458583, 0.101439036467562, 0.811302368396859 )
	);
	const mat3 AgXOutsetMatrix = mat3(
		vec3( 1.1271005818144368, - 0.1413297634984383, - 0.14132976349843826 ),
		vec3( - 0.11060664309660323, 1.157823702216272, - 0.11060664309660294 ),
		vec3( - 0.016493938717834573, - 0.016493938717834257, 1.2519364065950405 )
	);
	const float AgxMinEv = - 12.47393;	const float AgxMaxEv = 4.026069;
	color *= toneMappingExposure;
	color = LINEAR_SRGB_TO_LINEAR_REC2020 * color;
	color = AgXInsetMatrix * color;
	color = max( color, 1e-10 );	color = log2( color );
	color = ( color - AgxMinEv ) / ( AgxMaxEv - AgxMinEv );
	color = clamp( color, 0.0, 1.0 );
	color = agxDefaultContrastApprox( color );
	color = AgXOutsetMatrix * color;
	color = pow( max( vec3( 0.0 ), color ), vec3( 2.2 ) );
	color = LINEAR_REC2020_TO_LINEAR_SRGB * color;
	color = clamp( color, 0.0, 1.0 );
	return color;
}
vec3 NeutralToneMapping( vec3 color ) {
	const float StartCompression = 0.8 - 0.04;
	const float Desaturation = 0.15;
	color *= toneMappingExposure;
	float x = min( color.r, min( color.g, color.b ) );
	float offset = x < 0.08 ? x - 6.25 * x * x : 0.04;
	color -= offset;
	float peak = max( color.r, max( color.g, color.b ) );
	if ( peak < StartCompression ) return color;
	float d = 1. - StartCompression;
	float newPeak = 1. - d * d / ( peak + d - StartCompression );
	color *= newPeak / peak;
	float g = 1. - 1. / ( Desaturation * ( peak - newPeak ) + 1. );
	return mix( color, vec3( newPeak ), g );
}
vec3 CustomToneMapping( vec3 color ) { return color; }`,u0=`#ifdef USE_TRANSMISSION
	material.transmission = transmission;
	material.transmissionAlpha = 1.0;
	material.thickness = thickness;
	material.attenuationDistance = attenuationDistance;
	material.attenuationColor = attenuationColor;
	#ifdef USE_TRANSMISSIONMAP
		material.transmission *= texture2D( transmissionMap, vTransmissionMapUv ).r;
	#endif
	#ifdef USE_THICKNESSMAP
		material.thickness *= texture2D( thicknessMap, vThicknessMapUv ).g;
	#endif
	vec3 pos = vWorldPosition;
	vec3 v = normalize( cameraPosition - pos );
	vec3 n = inverseTransformDirection( normal, viewMatrix );
	vec4 transmitted = getIBLVolumeRefraction(
		n, v, material.roughness, material.diffuseColor, material.specularColor, material.specularF90,
		pos, modelMatrix, viewMatrix, projectionMatrix, material.dispersion, material.ior, material.thickness,
		material.attenuationColor, material.attenuationDistance );
	material.transmissionAlpha = mix( material.transmissionAlpha, transmitted.a, material.transmission );
	totalDiffuse = mix( totalDiffuse, transmitted.rgb, material.transmission );
#endif`,h0=`#ifdef USE_TRANSMISSION
	uniform float transmission;
	uniform float thickness;
	uniform float attenuationDistance;
	uniform vec3 attenuationColor;
	#ifdef USE_TRANSMISSIONMAP
		uniform sampler2D transmissionMap;
	#endif
	#ifdef USE_THICKNESSMAP
		uniform sampler2D thicknessMap;
	#endif
	uniform vec2 transmissionSamplerSize;
	uniform sampler2D transmissionSamplerMap;
	uniform mat4 modelMatrix;
	uniform mat4 projectionMatrix;
	varying vec3 vWorldPosition;
	float w0( float a ) {
		return ( 1.0 / 6.0 ) * ( a * ( a * ( - a + 3.0 ) - 3.0 ) + 1.0 );
	}
	float w1( float a ) {
		return ( 1.0 / 6.0 ) * ( a *  a * ( 3.0 * a - 6.0 ) + 4.0 );
	}
	float w2( float a ){
		return ( 1.0 / 6.0 ) * ( a * ( a * ( - 3.0 * a + 3.0 ) + 3.0 ) + 1.0 );
	}
	float w3( float a ) {
		return ( 1.0 / 6.0 ) * ( a * a * a );
	}
	float g0( float a ) {
		return w0( a ) + w1( a );
	}
	float g1( float a ) {
		return w2( a ) + w3( a );
	}
	float h0( float a ) {
		return - 1.0 + w1( a ) / ( w0( a ) + w1( a ) );
	}
	float h1( float a ) {
		return 1.0 + w3( a ) / ( w2( a ) + w3( a ) );
	}
	vec4 bicubic( sampler2D tex, vec2 uv, vec4 texelSize, float lod ) {
		uv = uv * texelSize.zw + 0.5;
		vec2 iuv = floor( uv );
		vec2 fuv = fract( uv );
		float g0x = g0( fuv.x );
		float g1x = g1( fuv.x );
		float h0x = h0( fuv.x );
		float h1x = h1( fuv.x );
		float h0y = h0( fuv.y );
		float h1y = h1( fuv.y );
		vec2 p0 = ( vec2( iuv.x + h0x, iuv.y + h0y ) - 0.5 ) * texelSize.xy;
		vec2 p1 = ( vec2( iuv.x + h1x, iuv.y + h0y ) - 0.5 ) * texelSize.xy;
		vec2 p2 = ( vec2( iuv.x + h0x, iuv.y + h1y ) - 0.5 ) * texelSize.xy;
		vec2 p3 = ( vec2( iuv.x + h1x, iuv.y + h1y ) - 0.5 ) * texelSize.xy;
		return g0( fuv.y ) * ( g0x * textureLod( tex, p0, lod ) + g1x * textureLod( tex, p1, lod ) ) +
			g1( fuv.y ) * ( g0x * textureLod( tex, p2, lod ) + g1x * textureLod( tex, p3, lod ) );
	}
	vec4 textureBicubic( sampler2D sampler, vec2 uv, float lod ) {
		vec2 fLodSize = vec2( textureSize( sampler, int( lod ) ) );
		vec2 cLodSize = vec2( textureSize( sampler, int( lod + 1.0 ) ) );
		vec2 fLodSizeInv = 1.0 / fLodSize;
		vec2 cLodSizeInv = 1.0 / cLodSize;
		vec4 fSample = bicubic( sampler, uv, vec4( fLodSizeInv, fLodSize ), floor( lod ) );
		vec4 cSample = bicubic( sampler, uv, vec4( cLodSizeInv, cLodSize ), ceil( lod ) );
		return mix( fSample, cSample, fract( lod ) );
	}
	vec3 getVolumeTransmissionRay( const in vec3 n, const in vec3 v, const in float thickness, const in float ior, const in mat4 modelMatrix ) {
		vec3 refractionVector = refract( - v, normalize( n ), 1.0 / ior );
		vec3 modelScale;
		modelScale.x = length( vec3( modelMatrix[ 0 ].xyz ) );
		modelScale.y = length( vec3( modelMatrix[ 1 ].xyz ) );
		modelScale.z = length( vec3( modelMatrix[ 2 ].xyz ) );
		return normalize( refractionVector ) * thickness * modelScale;
	}
	float applyIorToRoughness( const in float roughness, const in float ior ) {
		return roughness * clamp( ior * 2.0 - 2.0, 0.0, 1.0 );
	}
	vec4 getTransmissionSample( const in vec2 fragCoord, const in float roughness, const in float ior ) {
		float lod = log2( transmissionSamplerSize.x ) * applyIorToRoughness( roughness, ior );
		return textureBicubic( transmissionSamplerMap, fragCoord.xy, lod );
	}
	vec3 volumeAttenuation( const in float transmissionDistance, const in vec3 attenuationColor, const in float attenuationDistance ) {
		if ( isinf( attenuationDistance ) ) {
			return vec3( 1.0 );
		} else {
			vec3 attenuationCoefficient = -log( attenuationColor ) / attenuationDistance;
			vec3 transmittance = exp( - attenuationCoefficient * transmissionDistance );			return transmittance;
		}
	}
	vec4 getIBLVolumeRefraction( const in vec3 n, const in vec3 v, const in float roughness, const in vec3 diffuseColor,
		const in vec3 specularColor, const in float specularF90, const in vec3 position, const in mat4 modelMatrix,
		const in mat4 viewMatrix, const in mat4 projMatrix, const in float dispersion, const in float ior, const in float thickness,
		const in vec3 attenuationColor, const in float attenuationDistance ) {
		vec4 transmittedLight;
		vec3 transmittance;
		#ifdef USE_DISPERSION
			float halfSpread = ( ior - 1.0 ) * 0.025 * dispersion;
			vec3 iors = vec3( ior - halfSpread, ior, ior + halfSpread );
			for ( int i = 0; i < 3; i ++ ) {
				vec3 transmissionRay = getVolumeTransmissionRay( n, v, thickness, iors[ i ], modelMatrix );
				vec3 refractedRayExit = position + transmissionRay;
		
				vec4 ndcPos = projMatrix * viewMatrix * vec4( refractedRayExit, 1.0 );
				vec2 refractionCoords = ndcPos.xy / ndcPos.w;
				refractionCoords += 1.0;
				refractionCoords /= 2.0;
		
				vec4 transmissionSample = getTransmissionSample( refractionCoords, roughness, iors[ i ] );
				transmittedLight[ i ] = transmissionSample[ i ];
				transmittedLight.a += transmissionSample.a;
				transmittance[ i ] = diffuseColor[ i ] * volumeAttenuation( length( transmissionRay ), attenuationColor, attenuationDistance )[ i ];
			}
			transmittedLight.a /= 3.0;
		
		#else
		
			vec3 transmissionRay = getVolumeTransmissionRay( n, v, thickness, ior, modelMatrix );
			vec3 refractedRayExit = position + transmissionRay;
			vec4 ndcPos = projMatrix * viewMatrix * vec4( refractedRayExit, 1.0 );
			vec2 refractionCoords = ndcPos.xy / ndcPos.w;
			refractionCoords += 1.0;
			refractionCoords /= 2.0;
			transmittedLight = getTransmissionSample( refractionCoords, roughness, ior );
			transmittance = diffuseColor * volumeAttenuation( length( transmissionRay ), attenuationColor, attenuationDistance );
		
		#endif
		vec3 attenuatedColor = transmittance * transmittedLight.rgb;
		vec3 F = EnvironmentBRDF( n, v, specularColor, specularF90, roughness );
		float transmittanceFactor = ( transmittance.r + transmittance.g + transmittance.b ) / 3.0;
		return vec4( ( 1.0 - F ) * attenuatedColor, 1.0 - ( 1.0 - transmittedLight.a ) * transmittanceFactor );
	}
#endif`,d0=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
	varying vec2 vUv;
#endif
#ifdef USE_MAP
	varying vec2 vMapUv;
#endif
#ifdef USE_ALPHAMAP
	varying vec2 vAlphaMapUv;
#endif
#ifdef USE_LIGHTMAP
	varying vec2 vLightMapUv;
#endif
#ifdef USE_AOMAP
	varying vec2 vAoMapUv;
#endif
#ifdef USE_BUMPMAP
	varying vec2 vBumpMapUv;
#endif
#ifdef USE_NORMALMAP
	varying vec2 vNormalMapUv;
#endif
#ifdef USE_EMISSIVEMAP
	varying vec2 vEmissiveMapUv;
#endif
#ifdef USE_METALNESSMAP
	varying vec2 vMetalnessMapUv;
#endif
#ifdef USE_ROUGHNESSMAP
	varying vec2 vRoughnessMapUv;
#endif
#ifdef USE_ANISOTROPYMAP
	varying vec2 vAnisotropyMapUv;
#endif
#ifdef USE_CLEARCOATMAP
	varying vec2 vClearcoatMapUv;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	varying vec2 vClearcoatNormalMapUv;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	varying vec2 vClearcoatRoughnessMapUv;
#endif
#ifdef USE_IRIDESCENCEMAP
	varying vec2 vIridescenceMapUv;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	varying vec2 vIridescenceThicknessMapUv;
#endif
#ifdef USE_SHEEN_COLORMAP
	varying vec2 vSheenColorMapUv;
#endif
#ifdef USE_SHEEN_ROUGHNESSMAP
	varying vec2 vSheenRoughnessMapUv;
#endif
#ifdef USE_SPECULARMAP
	varying vec2 vSpecularMapUv;
#endif
#ifdef USE_SPECULAR_COLORMAP
	varying vec2 vSpecularColorMapUv;
#endif
#ifdef USE_SPECULAR_INTENSITYMAP
	varying vec2 vSpecularIntensityMapUv;
#endif
#ifdef USE_TRANSMISSIONMAP
	uniform mat3 transmissionMapTransform;
	varying vec2 vTransmissionMapUv;
#endif
#ifdef USE_THICKNESSMAP
	uniform mat3 thicknessMapTransform;
	varying vec2 vThicknessMapUv;
#endif`,f0=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
	varying vec2 vUv;
#endif
#ifdef USE_MAP
	uniform mat3 mapTransform;
	varying vec2 vMapUv;
#endif
#ifdef USE_ALPHAMAP
	uniform mat3 alphaMapTransform;
	varying vec2 vAlphaMapUv;
#endif
#ifdef USE_LIGHTMAP
	uniform mat3 lightMapTransform;
	varying vec2 vLightMapUv;
#endif
#ifdef USE_AOMAP
	uniform mat3 aoMapTransform;
	varying vec2 vAoMapUv;
#endif
#ifdef USE_BUMPMAP
	uniform mat3 bumpMapTransform;
	varying vec2 vBumpMapUv;
#endif
#ifdef USE_NORMALMAP
	uniform mat3 normalMapTransform;
	varying vec2 vNormalMapUv;
#endif
#ifdef USE_DISPLACEMENTMAP
	uniform mat3 displacementMapTransform;
	varying vec2 vDisplacementMapUv;
#endif
#ifdef USE_EMISSIVEMAP
	uniform mat3 emissiveMapTransform;
	varying vec2 vEmissiveMapUv;
#endif
#ifdef USE_METALNESSMAP
	uniform mat3 metalnessMapTransform;
	varying vec2 vMetalnessMapUv;
#endif
#ifdef USE_ROUGHNESSMAP
	uniform mat3 roughnessMapTransform;
	varying vec2 vRoughnessMapUv;
#endif
#ifdef USE_ANISOTROPYMAP
	uniform mat3 anisotropyMapTransform;
	varying vec2 vAnisotropyMapUv;
#endif
#ifdef USE_CLEARCOATMAP
	uniform mat3 clearcoatMapTransform;
	varying vec2 vClearcoatMapUv;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	uniform mat3 clearcoatNormalMapTransform;
	varying vec2 vClearcoatNormalMapUv;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	uniform mat3 clearcoatRoughnessMapTransform;
	varying vec2 vClearcoatRoughnessMapUv;
#endif
#ifdef USE_SHEEN_COLORMAP
	uniform mat3 sheenColorMapTransform;
	varying vec2 vSheenColorMapUv;
#endif
#ifdef USE_SHEEN_ROUGHNESSMAP
	uniform mat3 sheenRoughnessMapTransform;
	varying vec2 vSheenRoughnessMapUv;
#endif
#ifdef USE_IRIDESCENCEMAP
	uniform mat3 iridescenceMapTransform;
	varying vec2 vIridescenceMapUv;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	uniform mat3 iridescenceThicknessMapTransform;
	varying vec2 vIridescenceThicknessMapUv;
#endif
#ifdef USE_SPECULARMAP
	uniform mat3 specularMapTransform;
	varying vec2 vSpecularMapUv;
#endif
#ifdef USE_SPECULAR_COLORMAP
	uniform mat3 specularColorMapTransform;
	varying vec2 vSpecularColorMapUv;
#endif
#ifdef USE_SPECULAR_INTENSITYMAP
	uniform mat3 specularIntensityMapTransform;
	varying vec2 vSpecularIntensityMapUv;
#endif
#ifdef USE_TRANSMISSIONMAP
	uniform mat3 transmissionMapTransform;
	varying vec2 vTransmissionMapUv;
#endif
#ifdef USE_THICKNESSMAP
	uniform mat3 thicknessMapTransform;
	varying vec2 vThicknessMapUv;
#endif`,p0=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
	vUv = vec3( uv, 1 ).xy;
#endif
#ifdef USE_MAP
	vMapUv = ( mapTransform * vec3( MAP_UV, 1 ) ).xy;
#endif
#ifdef USE_ALPHAMAP
	vAlphaMapUv = ( alphaMapTransform * vec3( ALPHAMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_LIGHTMAP
	vLightMapUv = ( lightMapTransform * vec3( LIGHTMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_AOMAP
	vAoMapUv = ( aoMapTransform * vec3( AOMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_BUMPMAP
	vBumpMapUv = ( bumpMapTransform * vec3( BUMPMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_NORMALMAP
	vNormalMapUv = ( normalMapTransform * vec3( NORMALMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_DISPLACEMENTMAP
	vDisplacementMapUv = ( displacementMapTransform * vec3( DISPLACEMENTMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_EMISSIVEMAP
	vEmissiveMapUv = ( emissiveMapTransform * vec3( EMISSIVEMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_METALNESSMAP
	vMetalnessMapUv = ( metalnessMapTransform * vec3( METALNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_ROUGHNESSMAP
	vRoughnessMapUv = ( roughnessMapTransform * vec3( ROUGHNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_ANISOTROPYMAP
	vAnisotropyMapUv = ( anisotropyMapTransform * vec3( ANISOTROPYMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_CLEARCOATMAP
	vClearcoatMapUv = ( clearcoatMapTransform * vec3( CLEARCOATMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	vClearcoatNormalMapUv = ( clearcoatNormalMapTransform * vec3( CLEARCOAT_NORMALMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	vClearcoatRoughnessMapUv = ( clearcoatRoughnessMapTransform * vec3( CLEARCOAT_ROUGHNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_IRIDESCENCEMAP
	vIridescenceMapUv = ( iridescenceMapTransform * vec3( IRIDESCENCEMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	vIridescenceThicknessMapUv = ( iridescenceThicknessMapTransform * vec3( IRIDESCENCE_THICKNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SHEEN_COLORMAP
	vSheenColorMapUv = ( sheenColorMapTransform * vec3( SHEEN_COLORMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SHEEN_ROUGHNESSMAP
	vSheenRoughnessMapUv = ( sheenRoughnessMapTransform * vec3( SHEEN_ROUGHNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SPECULARMAP
	vSpecularMapUv = ( specularMapTransform * vec3( SPECULARMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SPECULAR_COLORMAP
	vSpecularColorMapUv = ( specularColorMapTransform * vec3( SPECULAR_COLORMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SPECULAR_INTENSITYMAP
	vSpecularIntensityMapUv = ( specularIntensityMapTransform * vec3( SPECULAR_INTENSITYMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_TRANSMISSIONMAP
	vTransmissionMapUv = ( transmissionMapTransform * vec3( TRANSMISSIONMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_THICKNESSMAP
	vThicknessMapUv = ( thicknessMapTransform * vec3( THICKNESSMAP_UV, 1 ) ).xy;
#endif`,m0=`#if defined( USE_ENVMAP ) || defined( DISTANCE ) || defined ( USE_SHADOWMAP ) || defined ( USE_TRANSMISSION ) || NUM_SPOT_LIGHT_COORDS > 0
	vec4 worldPosition = vec4( transformed, 1.0 );
	#ifdef USE_BATCHING
		worldPosition = batchingMatrix * worldPosition;
	#endif
	#ifdef USE_INSTANCING
		worldPosition = instanceMatrix * worldPosition;
	#endif
	worldPosition = modelMatrix * worldPosition;
#endif`;const g0=`varying vec2 vUv;
uniform mat3 uvTransform;
void main() {
	vUv = ( uvTransform * vec3( uv, 1 ) ).xy;
	gl_Position = vec4( position.xy, 1.0, 1.0 );
}`,_0=`uniform sampler2D t2D;
uniform float backgroundIntensity;
varying vec2 vUv;
void main() {
	vec4 texColor = texture2D( t2D, vUv );
	#ifdef DECODE_VIDEO_TEXTURE
		texColor = vec4( mix( pow( texColor.rgb * 0.9478672986 + vec3( 0.0521327014 ), vec3( 2.4 ) ), texColor.rgb * 0.0773993808, vec3( lessThanEqual( texColor.rgb, vec3( 0.04045 ) ) ) ), texColor.w );
	#endif
	texColor.rgb *= backgroundIntensity;
	gl_FragColor = texColor;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,v0=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,x0=`#ifdef ENVMAP_TYPE_CUBE
	uniform samplerCube envMap;
#elif defined( ENVMAP_TYPE_CUBE_UV )
	uniform sampler2D envMap;
#endif
uniform float flipEnvMap;
uniform float backgroundBlurriness;
uniform float backgroundIntensity;
uniform mat3 backgroundRotation;
varying vec3 vWorldDirection;
#include <cube_uv_reflection_fragment>
void main() {
	#ifdef ENVMAP_TYPE_CUBE
		vec4 texColor = textureCube( envMap, backgroundRotation * vec3( flipEnvMap * vWorldDirection.x, vWorldDirection.yz ) );
	#elif defined( ENVMAP_TYPE_CUBE_UV )
		vec4 texColor = textureCubeUV( envMap, backgroundRotation * vWorldDirection, backgroundBlurriness );
	#else
		vec4 texColor = vec4( 0.0, 0.0, 0.0, 1.0 );
	#endif
	texColor.rgb *= backgroundIntensity;
	gl_FragColor = texColor;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,y0=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,M0=`uniform samplerCube tCube;
uniform float tFlip;
uniform float opacity;
varying vec3 vWorldDirection;
void main() {
	vec4 texColor = textureCube( tCube, vec3( tFlip * vWorldDirection.x, vWorldDirection.yz ) );
	gl_FragColor = texColor;
	gl_FragColor.a *= opacity;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,S0=`#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
varying vec2 vHighPrecisionZW;
void main() {
	#include <uv_vertex>
	#include <batching_vertex>
	#include <skinbase_vertex>
	#include <morphinstance_vertex>
	#ifdef USE_DISPLACEMENTMAP
		#include <beginnormal_vertex>
		#include <morphnormal_vertex>
		#include <skinnormal_vertex>
	#endif
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vHighPrecisionZW = gl_Position.zw;
}`,E0=`#if DEPTH_PACKING == 3200
	uniform float opacity;
#endif
#include <common>
#include <packing>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
varying vec2 vHighPrecisionZW;
void main() {
	vec4 diffuseColor = vec4( 1.0 );
	#include <clipping_planes_fragment>
	#if DEPTH_PACKING == 3200
		diffuseColor.a = opacity;
	#endif
	#include <map_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <logdepthbuf_fragment>
	float fragCoordZ = 0.5 * vHighPrecisionZW[0] / vHighPrecisionZW[1] + 0.5;
	#if DEPTH_PACKING == 3200
		gl_FragColor = vec4( vec3( 1.0 - fragCoordZ ), opacity );
	#elif DEPTH_PACKING == 3201
		gl_FragColor = packDepthToRGBA( fragCoordZ );
	#elif DEPTH_PACKING == 3202
		gl_FragColor = vec4( packDepthToRGB( fragCoordZ ), 1.0 );
	#elif DEPTH_PACKING == 3203
		gl_FragColor = vec4( packDepthToRG( fragCoordZ ), 0.0, 1.0 );
	#endif
}`,b0=`#define DISTANCE
varying vec3 vWorldPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <batching_vertex>
	#include <skinbase_vertex>
	#include <morphinstance_vertex>
	#ifdef USE_DISPLACEMENTMAP
		#include <beginnormal_vertex>
		#include <morphnormal_vertex>
		#include <skinnormal_vertex>
	#endif
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <worldpos_vertex>
	#include <clipping_planes_vertex>
	vWorldPosition = worldPosition.xyz;
}`,T0=`#define DISTANCE
uniform vec3 referencePosition;
uniform float nearDistance;
uniform float farDistance;
varying vec3 vWorldPosition;
#include <common>
#include <packing>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <clipping_planes_pars_fragment>
void main () {
	vec4 diffuseColor = vec4( 1.0 );
	#include <clipping_planes_fragment>
	#include <map_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	float dist = length( vWorldPosition - referencePosition );
	dist = ( dist - nearDistance ) / ( farDistance - nearDistance );
	dist = saturate( dist );
	gl_FragColor = packDepthToRGBA( dist );
}`,w0=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
}`,A0=`uniform sampler2D tEquirect;
varying vec3 vWorldDirection;
#include <common>
void main() {
	vec3 direction = normalize( vWorldDirection );
	vec2 sampleUV = equirectUv( direction );
	gl_FragColor = texture2D( tEquirect, sampleUV );
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,R0=`uniform float scale;
attribute float lineDistance;
varying float vLineDistance;
#include <common>
#include <uv_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	vLineDistance = scale * lineDistance;
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <fog_vertex>
}`,C0=`uniform vec3 diffuse;
uniform float opacity;
uniform float dashSize;
uniform float totalSize;
varying float vLineDistance;
#include <common>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <fog_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	if ( mod( vLineDistance, totalSize ) > dashSize ) {
		discard;
	}
	vec3 outgoingLight = vec3( 0.0 );
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	outgoingLight = diffuseColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
}`,P0=`#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <envmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#if defined ( USE_ENVMAP ) || defined ( USE_SKINNING )
		#include <beginnormal_vertex>
		#include <morphnormal_vertex>
		#include <skinbase_vertex>
		#include <skinnormal_vertex>
		#include <defaultnormal_vertex>
	#endif
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <worldpos_vertex>
	#include <envmap_vertex>
	#include <fog_vertex>
}`,L0=`uniform vec3 diffuse;
uniform float opacity;
#ifndef FLAT_SHADED
	varying vec3 vNormal;
#endif
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_pars_fragment>
#include <fog_pars_fragment>
#include <specularmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <specularmap_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	#ifdef USE_LIGHTMAP
		vec4 lightMapTexel = texture2D( lightMap, vLightMapUv );
		reflectedLight.indirectDiffuse += lightMapTexel.rgb * lightMapIntensity * RECIPROCAL_PI;
	#else
		reflectedLight.indirectDiffuse += vec3( 1.0 );
	#endif
	#include <aomap_fragment>
	reflectedLight.indirectDiffuse *= diffuseColor.rgb;
	vec3 outgoingLight = reflectedLight.indirectDiffuse;
	#include <envmap_fragment>
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,D0=`#define LAMBERT
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <envmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <envmap_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,I0=`#define LAMBERT
uniform vec3 diffuse;
uniform vec3 emissive;
uniform float opacity;
#include <common>
#include <packing>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_pars_fragment>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_lambert_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <specularmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <specularmap_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_lambert_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + totalEmissiveRadiance;
	#include <envmap_fragment>
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,U0=`#define MATCAP
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <color_pars_vertex>
#include <displacementmap_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <fog_vertex>
	vViewPosition = - mvPosition.xyz;
}`,N0=`#define MATCAP
uniform vec3 diffuse;
uniform float opacity;
uniform sampler2D matcap;
varying vec3 vViewPosition;
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <fog_pars_fragment>
#include <normal_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	vec3 viewDir = normalize( vViewPosition );
	vec3 x = normalize( vec3( viewDir.z, 0.0, - viewDir.x ) );
	vec3 y = cross( viewDir, x );
	vec2 uv = vec2( dot( x, normal ), dot( y, normal ) ) * 0.495 + 0.5;
	#ifdef USE_MATCAP
		vec4 matcapColor = texture2D( matcap, uv );
	#else
		vec4 matcapColor = vec4( vec3( mix( 0.2, 0.8, uv.y ) ), 1.0 );
	#endif
	vec3 outgoingLight = diffuseColor.rgb * matcapColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,F0=`#define NORMAL
#if defined( FLAT_SHADED ) || defined( USE_BUMPMAP ) || defined( USE_NORMALMAP_TANGENTSPACE )
	varying vec3 vViewPosition;
#endif
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphinstance_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
#if defined( FLAT_SHADED ) || defined( USE_BUMPMAP ) || defined( USE_NORMALMAP_TANGENTSPACE )
	vViewPosition = - mvPosition.xyz;
#endif
}`,O0=`#define NORMAL
uniform float opacity;
#if defined( FLAT_SHADED ) || defined( USE_BUMPMAP ) || defined( USE_NORMALMAP_TANGENTSPACE )
	varying vec3 vViewPosition;
#endif
#include <packing>
#include <uv_pars_fragment>
#include <normal_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( 0.0, 0.0, 0.0, opacity );
	#include <clipping_planes_fragment>
	#include <logdepthbuf_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	gl_FragColor = vec4( packNormalToRGB( normal ), diffuseColor.a );
	#ifdef OPAQUE
		gl_FragColor.a = 1.0;
	#endif
}`,B0=`#define PHONG
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <envmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphinstance_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <envmap_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,z0=`#define PHONG
uniform vec3 diffuse;
uniform vec3 emissive;
uniform vec3 specular;
uniform float shininess;
uniform float opacity;
#include <common>
#include <packing>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_pars_fragment>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_phong_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <specularmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <specularmap_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_phong_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + reflectedLight.directSpecular + reflectedLight.indirectSpecular + totalEmissiveRadiance;
	#include <envmap_fragment>
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,k0=`#define STANDARD
varying vec3 vViewPosition;
#ifdef USE_TRANSMISSION
	varying vec3 vWorldPosition;
#endif
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
#ifdef USE_TRANSMISSION
	vWorldPosition = worldPosition.xyz;
#endif
}`,H0=`#define STANDARD
#ifdef PHYSICAL
	#define IOR
	#define USE_SPECULAR
#endif
uniform vec3 diffuse;
uniform vec3 emissive;
uniform float roughness;
uniform float metalness;
uniform float opacity;
#ifdef IOR
	uniform float ior;
#endif
#ifdef USE_SPECULAR
	uniform float specularIntensity;
	uniform vec3 specularColor;
	#ifdef USE_SPECULAR_COLORMAP
		uniform sampler2D specularColorMap;
	#endif
	#ifdef USE_SPECULAR_INTENSITYMAP
		uniform sampler2D specularIntensityMap;
	#endif
#endif
#ifdef USE_CLEARCOAT
	uniform float clearcoat;
	uniform float clearcoatRoughness;
#endif
#ifdef USE_DISPERSION
	uniform float dispersion;
#endif
#ifdef USE_IRIDESCENCE
	uniform float iridescence;
	uniform float iridescenceIOR;
	uniform float iridescenceThicknessMinimum;
	uniform float iridescenceThicknessMaximum;
#endif
#ifdef USE_SHEEN
	uniform vec3 sheenColor;
	uniform float sheenRoughness;
	#ifdef USE_SHEEN_COLORMAP
		uniform sampler2D sheenColorMap;
	#endif
	#ifdef USE_SHEEN_ROUGHNESSMAP
		uniform sampler2D sheenRoughnessMap;
	#endif
#endif
#ifdef USE_ANISOTROPY
	uniform vec2 anisotropyVector;
	#ifdef USE_ANISOTROPYMAP
		uniform sampler2D anisotropyMap;
	#endif
#endif
varying vec3 vViewPosition;
#include <common>
#include <packing>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <iridescence_fragment>
#include <cube_uv_reflection_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_physical_pars_fragment>
#include <fog_pars_fragment>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_physical_pars_fragment>
#include <transmission_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <clearcoat_pars_fragment>
#include <iridescence_pars_fragment>
#include <roughnessmap_pars_fragment>
#include <metalnessmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <roughnessmap_fragment>
	#include <metalnessmap_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <clearcoat_normal_fragment_begin>
	#include <clearcoat_normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_physical_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 totalDiffuse = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse;
	vec3 totalSpecular = reflectedLight.directSpecular + reflectedLight.indirectSpecular;
	#include <transmission_fragment>
	vec3 outgoingLight = totalDiffuse + totalSpecular + totalEmissiveRadiance;
	#ifdef USE_SHEEN
		float sheenEnergyComp = 1.0 - 0.157 * max3( material.sheenColor );
		outgoingLight = outgoingLight * sheenEnergyComp + sheenSpecularDirect + sheenSpecularIndirect;
	#endif
	#ifdef USE_CLEARCOAT
		float dotNVcc = saturate( dot( geometryClearcoatNormal, geometryViewDir ) );
		vec3 Fcc = F_Schlick( material.clearcoatF0, material.clearcoatF90, dotNVcc );
		outgoingLight = outgoingLight * ( 1.0 - material.clearcoat * Fcc ) + ( clearcoatSpecularDirect + clearcoatSpecularIndirect ) * material.clearcoat;
	#endif
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,V0=`#define TOON
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,G0=`#define TOON
uniform vec3 diffuse;
uniform vec3 emissive;
uniform float opacity;
#include <common>
#include <packing>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <gradientmap_pars_fragment>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_toon_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_toon_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + totalEmissiveRadiance;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,W0=`uniform float size;
uniform float scale;
#include <common>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
#ifdef USE_POINTS_UV
	varying vec2 vUv;
	uniform mat3 uvTransform;
#endif
void main() {
	#ifdef USE_POINTS_UV
		vUv = ( uvTransform * vec3( uv, 1 ) ).xy;
	#endif
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <project_vertex>
	gl_PointSize = size;
	#ifdef USE_SIZEATTENUATION
		bool isPerspective = isPerspectiveMatrix( projectionMatrix );
		if ( isPerspective ) gl_PointSize *= ( scale / - mvPosition.z );
	#endif
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <worldpos_vertex>
	#include <fog_vertex>
}`,X0=`uniform vec3 diffuse;
uniform float opacity;
#include <common>
#include <color_pars_fragment>
#include <map_particle_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <fog_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	vec3 outgoingLight = vec3( 0.0 );
	#include <logdepthbuf_fragment>
	#include <map_particle_fragment>
	#include <color_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	outgoingLight = diffuseColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
}`,q0=`#include <common>
#include <batching_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <shadowmap_pars_vertex>
void main() {
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphinstance_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <worldpos_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,Y0=`uniform vec3 color;
uniform float opacity;
#include <common>
#include <packing>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <logdepthbuf_pars_fragment>
#include <shadowmap_pars_fragment>
#include <shadowmask_pars_fragment>
void main() {
	#include <logdepthbuf_fragment>
	gl_FragColor = vec4( color, opacity * ( 1.0 - getShadowMask() ) );
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
}`,$0=`uniform float rotation;
uniform vec2 center;
#include <common>
#include <uv_pars_vertex>
#include <fog_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	vec4 mvPosition = modelViewMatrix * vec4( 0.0, 0.0, 0.0, 1.0 );
	vec2 scale;
	scale.x = length( vec3( modelMatrix[ 0 ].x, modelMatrix[ 0 ].y, modelMatrix[ 0 ].z ) );
	scale.y = length( vec3( modelMatrix[ 1 ].x, modelMatrix[ 1 ].y, modelMatrix[ 1 ].z ) );
	#ifndef USE_SIZEATTENUATION
		bool isPerspective = isPerspectiveMatrix( projectionMatrix );
		if ( isPerspective ) scale *= - mvPosition.z;
	#endif
	vec2 alignedPosition = ( position.xy - ( center - vec2( 0.5 ) ) ) * scale;
	vec2 rotatedPosition;
	rotatedPosition.x = cos( rotation ) * alignedPosition.x - sin( rotation ) * alignedPosition.y;
	rotatedPosition.y = sin( rotation ) * alignedPosition.x + cos( rotation ) * alignedPosition.y;
	mvPosition.xy += rotatedPosition;
	gl_Position = projectionMatrix * mvPosition;
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <fog_vertex>
}`,j0=`uniform vec3 diffuse;
uniform float opacity;
#include <common>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <fog_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	vec3 outgoingLight = vec3( 0.0 );
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	outgoingLight = diffuseColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
}`,it={alphahash_fragment:_g,alphahash_pars_fragment:vg,alphamap_fragment:xg,alphamap_pars_fragment:yg,alphatest_fragment:Mg,alphatest_pars_fragment:Sg,aomap_fragment:Eg,aomap_pars_fragment:bg,batching_pars_vertex:Tg,batching_vertex:wg,begin_vertex:Ag,beginnormal_vertex:Rg,bsdfs:Cg,iridescence_fragment:Pg,bumpmap_pars_fragment:Lg,clipping_planes_fragment:Dg,clipping_planes_pars_fragment:Ig,clipping_planes_pars_vertex:Ug,clipping_planes_vertex:Ng,color_fragment:Fg,color_pars_fragment:Og,color_pars_vertex:Bg,color_vertex:zg,common:kg,cube_uv_reflection_fragment:Hg,defaultnormal_vertex:Vg,displacementmap_pars_vertex:Gg,displacementmap_vertex:Wg,emissivemap_fragment:Xg,emissivemap_pars_fragment:qg,colorspace_fragment:Yg,colorspace_pars_fragment:$g,envmap_fragment:jg,envmap_common_pars_fragment:Kg,envmap_pars_fragment:Zg,envmap_pars_vertex:Jg,envmap_physical_pars_fragment:c_,envmap_vertex:Qg,fog_vertex:e_,fog_pars_vertex:t_,fog_fragment:n_,fog_pars_fragment:i_,gradientmap_pars_fragment:r_,lightmap_pars_fragment:s_,lights_lambert_fragment:a_,lights_lambert_pars_fragment:o_,lights_pars_begin:l_,lights_toon_fragment:u_,lights_toon_pars_fragment:h_,lights_phong_fragment:d_,lights_phong_pars_fragment:f_,lights_physical_fragment:p_,lights_physical_pars_fragment:m_,lights_fragment_begin:g_,lights_fragment_maps:__,lights_fragment_end:v_,logdepthbuf_fragment:x_,logdepthbuf_pars_fragment:y_,logdepthbuf_pars_vertex:M_,logdepthbuf_vertex:S_,map_fragment:E_,map_pars_fragment:b_,map_particle_fragment:T_,map_particle_pars_fragment:w_,metalnessmap_fragment:A_,metalnessmap_pars_fragment:R_,morphinstance_vertex:C_,morphcolor_vertex:P_,morphnormal_vertex:L_,morphtarget_pars_vertex:D_,morphtarget_vertex:I_,normal_fragment_begin:U_,normal_fragment_maps:N_,normal_pars_fragment:F_,normal_pars_vertex:O_,normal_vertex:B_,normalmap_pars_fragment:z_,clearcoat_normal_fragment_begin:k_,clearcoat_normal_fragment_maps:H_,clearcoat_pars_fragment:V_,iridescence_pars_fragment:G_,opaque_fragment:W_,packing:X_,premultiplied_alpha_fragment:q_,project_vertex:Y_,dithering_fragment:$_,dithering_pars_fragment:j_,roughnessmap_fragment:K_,roughnessmap_pars_fragment:Z_,shadowmap_pars_fragment:J_,shadowmap_pars_vertex:Q_,shadowmap_vertex:e0,shadowmask_pars_fragment:t0,skinbase_vertex:n0,skinning_pars_vertex:i0,skinning_vertex:r0,skinnormal_vertex:s0,specularmap_fragment:a0,specularmap_pars_fragment:o0,tonemapping_fragment:l0,tonemapping_pars_fragment:c0,transmission_fragment:u0,transmission_pars_fragment:h0,uv_pars_fragment:d0,uv_pars_vertex:f0,uv_vertex:p0,worldpos_vertex:m0,background_vert:g0,background_frag:_0,backgroundCube_vert:v0,backgroundCube_frag:x0,cube_vert:y0,cube_frag:M0,depth_vert:S0,depth_frag:E0,distanceRGBA_vert:b0,distanceRGBA_frag:T0,equirect_vert:w0,equirect_frag:A0,linedashed_vert:R0,linedashed_frag:C0,meshbasic_vert:P0,meshbasic_frag:L0,meshlambert_vert:D0,meshlambert_frag:I0,meshmatcap_vert:U0,meshmatcap_frag:N0,meshnormal_vert:F0,meshnormal_frag:O0,meshphong_vert:B0,meshphong_frag:z0,meshphysical_vert:k0,meshphysical_frag:H0,meshtoon_vert:V0,meshtoon_frag:G0,points_vert:W0,points_frag:X0,shadow_vert:q0,shadow_frag:Y0,sprite_vert:$0,sprite_frag:j0},Re={common:{diffuse:{value:new tt(16777215)},opacity:{value:1},map:{value:null},mapTransform:{value:new rt},alphaMap:{value:null},alphaMapTransform:{value:new rt},alphaTest:{value:0}},specularmap:{specularMap:{value:null},specularMapTransform:{value:new rt}},envmap:{envMap:{value:null},envMapRotation:{value:new rt},flipEnvMap:{value:-1},reflectivity:{value:1},ior:{value:1.5},refractionRatio:{value:.98}},aomap:{aoMap:{value:null},aoMapIntensity:{value:1},aoMapTransform:{value:new rt}},lightmap:{lightMap:{value:null},lightMapIntensity:{value:1},lightMapTransform:{value:new rt}},bumpmap:{bumpMap:{value:null},bumpMapTransform:{value:new rt},bumpScale:{value:1}},normalmap:{normalMap:{value:null},normalMapTransform:{value:new rt},normalScale:{value:new Xe(1,1)}},displacementmap:{displacementMap:{value:null},displacementMapTransform:{value:new rt},displacementScale:{value:1},displacementBias:{value:0}},emissivemap:{emissiveMap:{value:null},emissiveMapTransform:{value:new rt}},metalnessmap:{metalnessMap:{value:null},metalnessMapTransform:{value:new rt}},roughnessmap:{roughnessMap:{value:null},roughnessMapTransform:{value:new rt}},gradientmap:{gradientMap:{value:null}},fog:{fogDensity:{value:25e-5},fogNear:{value:1},fogFar:{value:2e3},fogColor:{value:new tt(16777215)}},lights:{ambientLightColor:{value:[]},lightProbe:{value:[]},directionalLights:{value:[],properties:{direction:{},color:{}}},directionalLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},directionalShadowMap:{value:[]},directionalShadowMatrix:{value:[]},spotLights:{value:[],properties:{color:{},position:{},direction:{},distance:{},coneCos:{},penumbraCos:{},decay:{}}},spotLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},spotLightMap:{value:[]},spotShadowMap:{value:[]},spotLightMatrix:{value:[]},pointLights:{value:[],properties:{color:{},position:{},decay:{},distance:{}}},pointLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{},shadowCameraNear:{},shadowCameraFar:{}}},pointShadowMap:{value:[]},pointShadowMatrix:{value:[]},hemisphereLights:{value:[],properties:{direction:{},skyColor:{},groundColor:{}}},rectAreaLights:{value:[],properties:{color:{},position:{},width:{},height:{}}},ltc_1:{value:null},ltc_2:{value:null}},points:{diffuse:{value:new tt(16777215)},opacity:{value:1},size:{value:1},scale:{value:1},map:{value:null},alphaMap:{value:null},alphaMapTransform:{value:new rt},alphaTest:{value:0},uvTransform:{value:new rt}},sprite:{diffuse:{value:new tt(16777215)},opacity:{value:1},center:{value:new Xe(.5,.5)},rotation:{value:0},map:{value:null},mapTransform:{value:new rt},alphaMap:{value:null},alphaMapTransform:{value:new rt},alphaTest:{value:0}}},mi={basic:{uniforms:bn([Re.common,Re.specularmap,Re.envmap,Re.aomap,Re.lightmap,Re.fog]),vertexShader:it.meshbasic_vert,fragmentShader:it.meshbasic_frag},lambert:{uniforms:bn([Re.common,Re.specularmap,Re.envmap,Re.aomap,Re.lightmap,Re.emissivemap,Re.bumpmap,Re.normalmap,Re.displacementmap,Re.fog,Re.lights,{emissive:{value:new tt(0)}}]),vertexShader:it.meshlambert_vert,fragmentShader:it.meshlambert_frag},phong:{uniforms:bn([Re.common,Re.specularmap,Re.envmap,Re.aomap,Re.lightmap,Re.emissivemap,Re.bumpmap,Re.normalmap,Re.displacementmap,Re.fog,Re.lights,{emissive:{value:new tt(0)},specular:{value:new tt(1118481)},shininess:{value:30}}]),vertexShader:it.meshphong_vert,fragmentShader:it.meshphong_frag},standard:{uniforms:bn([Re.common,Re.envmap,Re.aomap,Re.lightmap,Re.emissivemap,Re.bumpmap,Re.normalmap,Re.displacementmap,Re.roughnessmap,Re.metalnessmap,Re.fog,Re.lights,{emissive:{value:new tt(0)},roughness:{value:1},metalness:{value:0},envMapIntensity:{value:1}}]),vertexShader:it.meshphysical_vert,fragmentShader:it.meshphysical_frag},toon:{uniforms:bn([Re.common,Re.aomap,Re.lightmap,Re.emissivemap,Re.bumpmap,Re.normalmap,Re.displacementmap,Re.gradientmap,Re.fog,Re.lights,{emissive:{value:new tt(0)}}]),vertexShader:it.meshtoon_vert,fragmentShader:it.meshtoon_frag},matcap:{uniforms:bn([Re.common,Re.bumpmap,Re.normalmap,Re.displacementmap,Re.fog,{matcap:{value:null}}]),vertexShader:it.meshmatcap_vert,fragmentShader:it.meshmatcap_frag},points:{uniforms:bn([Re.points,Re.fog]),vertexShader:it.points_vert,fragmentShader:it.points_frag},dashed:{uniforms:bn([Re.common,Re.fog,{scale:{value:1},dashSize:{value:1},totalSize:{value:2}}]),vertexShader:it.linedashed_vert,fragmentShader:it.linedashed_frag},depth:{uniforms:bn([Re.common,Re.displacementmap]),vertexShader:it.depth_vert,fragmentShader:it.depth_frag},normal:{uniforms:bn([Re.common,Re.bumpmap,Re.normalmap,Re.displacementmap,{opacity:{value:1}}]),vertexShader:it.meshnormal_vert,fragmentShader:it.meshnormal_frag},sprite:{uniforms:bn([Re.sprite,Re.fog]),vertexShader:it.sprite_vert,fragmentShader:it.sprite_frag},background:{uniforms:{uvTransform:{value:new rt},t2D:{value:null},backgroundIntensity:{value:1}},vertexShader:it.background_vert,fragmentShader:it.background_frag},backgroundCube:{uniforms:{envMap:{value:null},flipEnvMap:{value:-1},backgroundBlurriness:{value:0},backgroundIntensity:{value:1},backgroundRotation:{value:new rt}},vertexShader:it.backgroundCube_vert,fragmentShader:it.backgroundCube_frag},cube:{uniforms:{tCube:{value:null},tFlip:{value:-1},opacity:{value:1}},vertexShader:it.cube_vert,fragmentShader:it.cube_frag},equirect:{uniforms:{tEquirect:{value:null}},vertexShader:it.equirect_vert,fragmentShader:it.equirect_frag},distanceRGBA:{uniforms:bn([Re.common,Re.displacementmap,{referencePosition:{value:new H},nearDistance:{value:1},farDistance:{value:1e3}}]),vertexShader:it.distanceRGBA_vert,fragmentShader:it.distanceRGBA_frag},shadow:{uniforms:bn([Re.lights,Re.fog,{color:{value:new tt(0)},opacity:{value:1}}]),vertexShader:it.shadow_vert,fragmentShader:it.shadow_frag}};mi.physical={uniforms:bn([mi.standard.uniforms,{clearcoat:{value:0},clearcoatMap:{value:null},clearcoatMapTransform:{value:new rt},clearcoatNormalMap:{value:null},clearcoatNormalMapTransform:{value:new rt},clearcoatNormalScale:{value:new Xe(1,1)},clearcoatRoughness:{value:0},clearcoatRoughnessMap:{value:null},clearcoatRoughnessMapTransform:{value:new rt},dispersion:{value:0},iridescence:{value:0},iridescenceMap:{value:null},iridescenceMapTransform:{value:new rt},iridescenceIOR:{value:1.3},iridescenceThicknessMinimum:{value:100},iridescenceThicknessMaximum:{value:400},iridescenceThicknessMap:{value:null},iridescenceThicknessMapTransform:{value:new rt},sheen:{value:0},sheenColor:{value:new tt(0)},sheenColorMap:{value:null},sheenColorMapTransform:{value:new rt},sheenRoughness:{value:1},sheenRoughnessMap:{value:null},sheenRoughnessMapTransform:{value:new rt},transmission:{value:0},transmissionMap:{value:null},transmissionMapTransform:{value:new rt},transmissionSamplerSize:{value:new Xe},transmissionSamplerMap:{value:null},thickness:{value:0},thicknessMap:{value:null},thicknessMapTransform:{value:new rt},attenuationDistance:{value:0},attenuationColor:{value:new tt(0)},specularColor:{value:new tt(1,1,1)},specularColorMap:{value:null},specularColorMapTransform:{value:new rt},specularIntensity:{value:1},specularIntensityMap:{value:null},specularIntensityMapTransform:{value:new rt},anisotropyVector:{value:new Xe},anisotropyMap:{value:null},anisotropyMapTransform:{value:new rt}}]),vertexShader:it.meshphysical_vert,fragmentShader:it.meshphysical_frag};const ja={r:0,b:0,g:0},xr=new _i,K0=new Ft;function Z0(i,e,t,n,r,s,a){const o=new tt(0);let l=s===!0?0:1,c,u,h=null,d=0,m=null;function _(E){let S=E.isScene===!0?E.background:null;return S&&S.isTexture&&(S=(E.backgroundBlurriness>0?t:e).get(S)),S}function v(E){let S=!1;const T=_(E);T===null?f(o,l):T&&T.isColor&&(f(T,1),S=!0);const z=i.xr.getEnvironmentBlendMode();z==="additive"?n.buffers.color.setClear(0,0,0,1,a):z==="alpha-blend"&&n.buffers.color.setClear(0,0,0,0,a),(i.autoClear||S)&&(n.buffers.depth.setTest(!0),n.buffers.depth.setMask(!0),n.buffers.color.setMask(!0),i.clear(i.autoClearColor,i.autoClearDepth,i.autoClearStencil))}function p(E,S){const T=_(S);T&&(T.isCubeTexture||T.mapping===Io)?(u===void 0&&(u=new Tn(new Ii(1,1,1),new rr({name:"BackgroundCubeMaterial",uniforms:Rs(mi.backgroundCube.uniforms),vertexShader:mi.backgroundCube.vertexShader,fragmentShader:mi.backgroundCube.fragmentShader,side:Cn,depthTest:!1,depthWrite:!1,fog:!1})),u.geometry.deleteAttribute("normal"),u.geometry.deleteAttribute("uv"),u.onBeforeRender=function(z,R,L){this.matrixWorld.copyPosition(L.matrixWorld)},Object.defineProperty(u.material,"envMap",{get:function(){return this.uniforms.envMap.value}}),r.update(u)),xr.copy(S.backgroundRotation),xr.x*=-1,xr.y*=-1,xr.z*=-1,T.isCubeTexture&&T.isRenderTargetTexture===!1&&(xr.y*=-1,xr.z*=-1),u.material.uniforms.envMap.value=T,u.material.uniforms.flipEnvMap.value=T.isCubeTexture&&T.isRenderTargetTexture===!1?-1:1,u.material.uniforms.backgroundBlurriness.value=S.backgroundBlurriness,u.material.uniforms.backgroundIntensity.value=S.backgroundIntensity,u.material.uniforms.backgroundRotation.value.setFromMatrix4(K0.makeRotationFromEuler(xr)),u.material.toneMapped=Mt.getTransfer(T.colorSpace)!==Nt,(h!==T||d!==T.version||m!==i.toneMapping)&&(u.material.needsUpdate=!0,h=T,d=T.version,m=i.toneMapping),u.layers.enableAll(),E.unshift(u,u.geometry,u.material,0,0,null)):T&&T.isTexture&&(c===void 0&&(c=new Tn(new No(2,2),new rr({name:"BackgroundMaterial",uniforms:Rs(mi.background.uniforms),vertexShader:mi.background.vertexShader,fragmentShader:mi.background.fragmentShader,side:ir,depthTest:!1,depthWrite:!1,fog:!1})),c.geometry.deleteAttribute("normal"),Object.defineProperty(c.material,"map",{get:function(){return this.uniforms.t2D.value}}),r.update(c)),c.material.uniforms.t2D.value=T,c.material.uniforms.backgroundIntensity.value=S.backgroundIntensity,c.material.toneMapped=Mt.getTransfer(T.colorSpace)!==Nt,T.matrixAutoUpdate===!0&&T.updateMatrix(),c.material.uniforms.uvTransform.value.copy(T.matrix),(h!==T||d!==T.version||m!==i.toneMapping)&&(c.material.needsUpdate=!0,h=T,d=T.version,m=i.toneMapping),c.layers.enableAll(),E.unshift(c,c.geometry,c.material,0,0,null))}function f(E,S){E.getRGB(ja,df(i)),n.buffers.color.setClear(ja.r,ja.g,ja.b,S,a)}return{getClearColor:function(){return o},setClearColor:function(E,S=1){o.set(E),l=S,f(o,l)},getClearAlpha:function(){return l},setClearAlpha:function(E){l=E,f(o,l)},render:v,addToRenderList:p}}function J0(i,e){const t=i.getParameter(i.MAX_VERTEX_ATTRIBS),n={},r=d(null);let s=r,a=!1;function o(x,C,j,B,K){let W=!1;const J=h(B,j,C);s!==J&&(s=J,c(s.object)),W=m(x,B,j,K),W&&_(x,B,j,K),K!==null&&e.update(K,i.ELEMENT_ARRAY_BUFFER),(W||a)&&(a=!1,T(x,C,j,B),K!==null&&i.bindBuffer(i.ELEMENT_ARRAY_BUFFER,e.get(K).buffer))}function l(){return i.createVertexArray()}function c(x){return i.bindVertexArray(x)}function u(x){return i.deleteVertexArray(x)}function h(x,C,j){const B=j.wireframe===!0;let K=n[x.id];K===void 0&&(K={},n[x.id]=K);let W=K[C.id];W===void 0&&(W={},K[C.id]=W);let J=W[B];return J===void 0&&(J=d(l()),W[B]=J),J}function d(x){const C=[],j=[],B=[];for(let K=0;K<t;K++)C[K]=0,j[K]=0,B[K]=0;return{geometry:null,program:null,wireframe:!1,newAttributes:C,enabledAttributes:j,attributeDivisors:B,object:x,attributes:{},index:null}}function m(x,C,j,B){const K=s.attributes,W=C.attributes;let J=0;const q=j.getAttributes();for(const ee in q)if(q[ee].location>=0){const he=K[ee];let ve=W[ee];if(ve===void 0&&(ee==="instanceMatrix"&&x.instanceMatrix&&(ve=x.instanceMatrix),ee==="instanceColor"&&x.instanceColor&&(ve=x.instanceColor)),he===void 0||he.attribute!==ve||ve&&he.data!==ve.data)return!0;J++}return s.attributesNum!==J||s.index!==B}function _(x,C,j,B){const K={},W=C.attributes;let J=0;const q=j.getAttributes();for(const ee in q)if(q[ee].location>=0){let he=W[ee];he===void 0&&(ee==="instanceMatrix"&&x.instanceMatrix&&(he=x.instanceMatrix),ee==="instanceColor"&&x.instanceColor&&(he=x.instanceColor));const ve={};ve.attribute=he,he&&he.data&&(ve.data=he.data),K[ee]=ve,J++}s.attributes=K,s.attributesNum=J,s.index=B}function v(){const x=s.newAttributes;for(let C=0,j=x.length;C<j;C++)x[C]=0}function p(x){f(x,0)}function f(x,C){const j=s.newAttributes,B=s.enabledAttributes,K=s.attributeDivisors;j[x]=1,B[x]===0&&(i.enableVertexAttribArray(x),B[x]=1),K[x]!==C&&(i.vertexAttribDivisor(x,C),K[x]=C)}function E(){const x=s.newAttributes,C=s.enabledAttributes;for(let j=0,B=C.length;j<B;j++)C[j]!==x[j]&&(i.disableVertexAttribArray(j),C[j]=0)}function S(x,C,j,B,K,W,J){J===!0?i.vertexAttribIPointer(x,C,j,K,W):i.vertexAttribPointer(x,C,j,B,K,W)}function T(x,C,j,B){v();const K=B.attributes,W=j.getAttributes(),J=C.defaultAttributeValues;for(const q in W){const ee=W[q];if(ee.location>=0){let me=K[q];if(me===void 0&&(q==="instanceMatrix"&&x.instanceMatrix&&(me=x.instanceMatrix),q==="instanceColor"&&x.instanceColor&&(me=x.instanceColor)),me!==void 0){const he=me.normalized,ve=me.itemSize,Te=e.get(me);if(Te===void 0)continue;const xe=Te.buffer,te=Te.type,ce=Te.bytesPerElement,ye=te===i.INT||te===i.UNSIGNED_INT||me.gpuType===Vc;if(me.isInterleavedBufferAttribute){const de=me.data,Be=de.stride,Ve=me.offset;if(de.isInstancedInterleavedBuffer){for(let Ne=0;Ne<ee.locationSize;Ne++)f(ee.location+Ne,de.meshPerAttribute);x.isInstancedMesh!==!0&&B._maxInstanceCount===void 0&&(B._maxInstanceCount=de.meshPerAttribute*de.count)}else for(let Ne=0;Ne<ee.locationSize;Ne++)p(ee.location+Ne);i.bindBuffer(i.ARRAY_BUFFER,xe);for(let Ne=0;Ne<ee.locationSize;Ne++)S(ee.location+Ne,ve/ee.locationSize,te,he,Be*ce,(Ve+ve/ee.locationSize*Ne)*ce,ye)}else{if(me.isInstancedBufferAttribute){for(let de=0;de<ee.locationSize;de++)f(ee.location+de,me.meshPerAttribute);x.isInstancedMesh!==!0&&B._maxInstanceCount===void 0&&(B._maxInstanceCount=me.meshPerAttribute*me.count)}else for(let de=0;de<ee.locationSize;de++)p(ee.location+de);i.bindBuffer(i.ARRAY_BUFFER,xe);for(let de=0;de<ee.locationSize;de++)S(ee.location+de,ve/ee.locationSize,te,he,ve*ce,ve/ee.locationSize*de*ce,ye)}}else if(J!==void 0){const he=J[q];if(he!==void 0)switch(he.length){case 2:i.vertexAttrib2fv(ee.location,he);break;case 3:i.vertexAttrib3fv(ee.location,he);break;case 4:i.vertexAttrib4fv(ee.location,he);break;default:i.vertexAttrib1fv(ee.location,he)}}}}E()}function z(){O();for(const x in n){const C=n[x];for(const j in C){const B=C[j];for(const K in B)u(B[K].object),delete B[K];delete C[j]}delete n[x]}}function R(x){if(n[x.id]===void 0)return;const C=n[x.id];for(const j in C){const B=C[j];for(const K in B)u(B[K].object),delete B[K];delete C[j]}delete n[x.id]}function L(x){for(const C in n){const j=n[C];if(j[x.id]===void 0)continue;const B=j[x.id];for(const K in B)u(B[K].object),delete B[K];delete j[x.id]}}function O(){w(),a=!0,s!==r&&(s=r,c(s.object))}function w(){r.geometry=null,r.program=null,r.wireframe=!1}return{setup:o,reset:O,resetDefaultState:w,dispose:z,releaseStatesOfGeometry:R,releaseStatesOfProgram:L,initAttributes:v,enableAttribute:p,disableUnusedAttributes:E}}function Q0(i,e,t){let n;function r(c){n=c}function s(c,u){i.drawArrays(n,c,u),t.update(u,n,1)}function a(c,u,h){h!==0&&(i.drawArraysInstanced(n,c,u,h),t.update(u,n,h))}function o(c,u,h){if(h===0)return;e.get("WEBGL_multi_draw").multiDrawArraysWEBGL(n,c,0,u,0,h);let m=0;for(let _=0;_<h;_++)m+=u[_];t.update(m,n,1)}function l(c,u,h,d){if(h===0)return;const m=e.get("WEBGL_multi_draw");if(m===null)for(let _=0;_<c.length;_++)a(c[_],u[_],d[_]);else{m.multiDrawArraysInstancedWEBGL(n,c,0,u,0,d,0,h);let _=0;for(let v=0;v<h;v++)_+=u[v];for(let v=0;v<d.length;v++)t.update(_,n,d[v])}}this.setMode=r,this.render=s,this.renderInstances=a,this.renderMultiDraw=o,this.renderMultiDrawInstances=l}function ev(i,e,t,n){let r;function s(){if(r!==void 0)return r;if(e.has("EXT_texture_filter_anisotropic")===!0){const R=e.get("EXT_texture_filter_anisotropic");r=i.getParameter(R.MAX_TEXTURE_MAX_ANISOTROPY_EXT)}else r=0;return r}function a(R){return!(R!==ri&&n.convert(R)!==i.getParameter(i.IMPLEMENTATION_COLOR_READ_FORMAT))}function o(R){const L=R===va&&(e.has("EXT_color_buffer_half_float")||e.has("EXT_color_buffer_float"));return!(R!==Oi&&n.convert(R)!==i.getParameter(i.IMPLEMENTATION_COLOR_READ_TYPE)&&R!==Li&&!L)}function l(R){if(R==="highp"){if(i.getShaderPrecisionFormat(i.VERTEX_SHADER,i.HIGH_FLOAT).precision>0&&i.getShaderPrecisionFormat(i.FRAGMENT_SHADER,i.HIGH_FLOAT).precision>0)return"highp";R="mediump"}return R==="mediump"&&i.getShaderPrecisionFormat(i.VERTEX_SHADER,i.MEDIUM_FLOAT).precision>0&&i.getShaderPrecisionFormat(i.FRAGMENT_SHADER,i.MEDIUM_FLOAT).precision>0?"mediump":"lowp"}let c=t.precision!==void 0?t.precision:"highp";const u=l(c);u!==c&&(console.warn("THREE.WebGLRenderer:",c,"not supported, using",u,"instead."),c=u);const h=t.logarithmicDepthBuffer===!0,d=i.getParameter(i.MAX_TEXTURE_IMAGE_UNITS),m=i.getParameter(i.MAX_VERTEX_TEXTURE_IMAGE_UNITS),_=i.getParameter(i.MAX_TEXTURE_SIZE),v=i.getParameter(i.MAX_CUBE_MAP_TEXTURE_SIZE),p=i.getParameter(i.MAX_VERTEX_ATTRIBS),f=i.getParameter(i.MAX_VERTEX_UNIFORM_VECTORS),E=i.getParameter(i.MAX_VARYING_VECTORS),S=i.getParameter(i.MAX_FRAGMENT_UNIFORM_VECTORS),T=m>0,z=i.getParameter(i.MAX_SAMPLES);return{isWebGL2:!0,getMaxAnisotropy:s,getMaxPrecision:l,textureFormatReadable:a,textureTypeReadable:o,precision:c,logarithmicDepthBuffer:h,maxTextures:d,maxVertexTextures:m,maxTextureSize:_,maxCubemapSize:v,maxAttributes:p,maxVertexUniforms:f,maxVaryings:E,maxFragmentUniforms:S,vertexTextures:T,maxSamples:z}}function tv(i){const e=this;let t=null,n=0,r=!1,s=!1;const a=new Ki,o=new rt,l={value:null,needsUpdate:!1};this.uniform=l,this.numPlanes=0,this.numIntersection=0,this.init=function(h,d){const m=h.length!==0||d||n!==0||r;return r=d,n=h.length,m},this.beginShadows=function(){s=!0,u(null)},this.endShadows=function(){s=!1},this.setGlobalState=function(h,d){t=u(h,d,0)},this.setState=function(h,d,m){const _=h.clippingPlanes,v=h.clipIntersection,p=h.clipShadows,f=i.get(h);if(!r||_===null||_.length===0||s&&!p)s?u(null):c();else{const E=s?0:n,S=E*4;let T=f.clippingState||null;l.value=T,T=u(_,d,S,m);for(let z=0;z!==S;++z)T[z]=t[z];f.clippingState=T,this.numIntersection=v?this.numPlanes:0,this.numPlanes+=E}};function c(){l.value!==t&&(l.value=t,l.needsUpdate=n>0),e.numPlanes=n,e.numIntersection=0}function u(h,d,m,_){const v=h!==null?h.length:0;let p=null;if(v!==0){if(p=l.value,_!==!0||p===null){const f=m+v*4,E=d.matrixWorldInverse;o.getNormalMatrix(E),(p===null||p.length<f)&&(p=new Float32Array(f));for(let S=0,T=m;S!==v;++S,T+=4)a.copy(h[S]).applyMatrix4(E,o),a.normal.toArray(p,T),p[T+3]=a.constant}l.value=p,l.needsUpdate=!0}return e.numPlanes=v,e.numIntersection=0,p}}function nv(i){let e=new WeakMap;function t(a,o){return o===$l?a.mapping=bs:o===jl&&(a.mapping=Ts),a}function n(a){if(a&&a.isTexture){const o=a.mapping;if(o===$l||o===jl)if(e.has(a)){const l=e.get(a).texture;return t(l,a.mapping)}else{const l=a.image;if(l&&l.height>0){const c=new fg(l.height);return c.fromEquirectangularTexture(i,a),e.set(a,c),a.addEventListener("dispose",r),t(c.texture,a.mapping)}else return null}}return a}function r(a){const o=a.target;o.removeEventListener("dispose",r);const l=e.get(o);l!==void 0&&(e.delete(o),l.dispose())}function s(){e=new WeakMap}return{get:n,dispose:s}}class Ss extends ff{constructor(e=-1,t=1,n=1,r=-1,s=.1,a=2e3){super(),this.isOrthographicCamera=!0,this.type="OrthographicCamera",this.zoom=1,this.view=null,this.left=e,this.right=t,this.top=n,this.bottom=r,this.near=s,this.far=a,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.left=e.left,this.right=e.right,this.top=e.top,this.bottom=e.bottom,this.near=e.near,this.far=e.far,this.zoom=e.zoom,this.view=e.view===null?null:Object.assign({},e.view),this}setViewOffset(e,t,n,r,s,a){this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=n,this.view.offsetY=r,this.view.width=s,this.view.height=a,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const e=(this.right-this.left)/(2*this.zoom),t=(this.top-this.bottom)/(2*this.zoom),n=(this.right+this.left)/2,r=(this.top+this.bottom)/2;let s=n-e,a=n+e,o=r+t,l=r-t;if(this.view!==null&&this.view.enabled){const c=(this.right-this.left)/this.view.fullWidth/this.zoom,u=(this.top-this.bottom)/this.view.fullHeight/this.zoom;s+=c*this.view.offsetX,a=s+c*this.view.width,o-=u*this.view.offsetY,l=o-u*this.view.height}this.projectionMatrix.makeOrthographic(s,a,o,l,this.near,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){const t=super.toJSON(e);return t.object.zoom=this.zoom,t.object.left=this.left,t.object.right=this.right,t.object.top=this.top,t.object.bottom=this.bottom,t.object.near=this.near,t.object.far=this.far,this.view!==null&&(t.object.view=Object.assign({},this.view)),t}}const gs=4,ph=[.125,.215,.35,.446,.526,.582],Tr=20,Tl=new Ss,mh=new tt;let wl=null,Al=0,Rl=0,Cl=!1;const Mr=(1+Math.sqrt(5))/2,cs=1/Mr,gh=[new H(-Mr,cs,0),new H(Mr,cs,0),new H(-cs,0,Mr),new H(cs,0,Mr),new H(0,Mr,-cs),new H(0,Mr,cs),new H(-1,1,-1),new H(1,1,-1),new H(-1,1,1),new H(1,1,1)];class _h{constructor(e){this._renderer=e,this._pingPongRenderTarget=null,this._lodMax=0,this._cubeSize=0,this._lodPlanes=[],this._sizeLods=[],this._sigmas=[],this._blurMaterial=null,this._cubemapMaterial=null,this._equirectMaterial=null,this._compileMaterial(this._blurMaterial)}fromScene(e,t=0,n=.1,r=100){wl=this._renderer.getRenderTarget(),Al=this._renderer.getActiveCubeFace(),Rl=this._renderer.getActiveMipmapLevel(),Cl=this._renderer.xr.enabled,this._renderer.xr.enabled=!1,this._setSize(256);const s=this._allocateTargets();return s.depthBuffer=!0,this._sceneToCubeUV(e,n,r,s),t>0&&this._blur(s,0,0,t),this._applyPMREM(s),this._cleanup(s),s}fromEquirectangular(e,t=null){return this._fromTexture(e,t)}fromCubemap(e,t=null){return this._fromTexture(e,t)}compileCubemapShader(){this._cubemapMaterial===null&&(this._cubemapMaterial=yh(),this._compileMaterial(this._cubemapMaterial))}compileEquirectangularShader(){this._equirectMaterial===null&&(this._equirectMaterial=xh(),this._compileMaterial(this._equirectMaterial))}dispose(){this._dispose(),this._cubemapMaterial!==null&&this._cubemapMaterial.dispose(),this._equirectMaterial!==null&&this._equirectMaterial.dispose()}_setSize(e){this._lodMax=Math.floor(Math.log2(e)),this._cubeSize=Math.pow(2,this._lodMax)}_dispose(){this._blurMaterial!==null&&this._blurMaterial.dispose(),this._pingPongRenderTarget!==null&&this._pingPongRenderTarget.dispose();for(let e=0;e<this._lodPlanes.length;e++)this._lodPlanes[e].dispose()}_cleanup(e){this._renderer.setRenderTarget(wl,Al,Rl),this._renderer.xr.enabled=Cl,e.scissorTest=!1,Ka(e,0,0,e.width,e.height)}_fromTexture(e,t){e.mapping===bs||e.mapping===Ts?this._setSize(e.image.length===0?16:e.image[0].width||e.image[0].image.width):this._setSize(e.image.width/4),wl=this._renderer.getRenderTarget(),Al=this._renderer.getActiveCubeFace(),Rl=this._renderer.getActiveMipmapLevel(),Cl=this._renderer.xr.enabled,this._renderer.xr.enabled=!1;const n=t||this._allocateTargets();return this._textureToCubeUV(e,n),this._applyPMREM(n),this._cleanup(n),n}_allocateTargets(){const e=3*Math.max(this._cubeSize,112),t=4*this._cubeSize,n={magFilter:ti,minFilter:ti,generateMipmaps:!1,type:va,format:ri,colorSpace:lr,depthBuffer:!1},r=vh(e,t,n);if(this._pingPongRenderTarget===null||this._pingPongRenderTarget.width!==e||this._pingPongRenderTarget.height!==t){this._pingPongRenderTarget!==null&&this._dispose(),this._pingPongRenderTarget=vh(e,t,n);const{_lodMax:s}=this;({sizeLods:this._sizeLods,lodPlanes:this._lodPlanes,sigmas:this._sigmas}=iv(s)),this._blurMaterial=rv(s,e,t)}return r}_compileMaterial(e){const t=new Tn(this._lodPlanes[0],e);this._renderer.compile(t,Tl)}_sceneToCubeUV(e,t,n,r){const o=new _n(90,1,t,n),l=[1,-1,1,1,1,1],c=[1,1,1,-1,-1,-1],u=this._renderer,h=u.autoClear,d=u.toneMapping;u.getClearColor(mh),u.toneMapping=er,u.autoClear=!1;const m=new ua({name:"PMREM.Background",side:Cn,depthWrite:!1,depthTest:!1}),_=new Tn(new Ii,m);let v=!1;const p=e.background;p?p.isColor&&(m.color.copy(p),e.background=null,v=!0):(m.color.copy(mh),v=!0);for(let f=0;f<6;f++){const E=f%3;E===0?(o.up.set(0,l[f],0),o.lookAt(c[f],0,0)):E===1?(o.up.set(0,0,l[f]),o.lookAt(0,c[f],0)):(o.up.set(0,l[f],0),o.lookAt(0,0,c[f]));const S=this._cubeSize;Ka(r,E*S,f>2?S:0,S,S),u.setRenderTarget(r),v&&u.render(_,o),u.render(e,o)}_.geometry.dispose(),_.material.dispose(),u.toneMapping=d,u.autoClear=h,e.background=p}_textureToCubeUV(e,t){const n=this._renderer,r=e.mapping===bs||e.mapping===Ts;r?(this._cubemapMaterial===null&&(this._cubemapMaterial=yh()),this._cubemapMaterial.uniforms.flipEnvMap.value=e.isRenderTargetTexture===!1?-1:1):this._equirectMaterial===null&&(this._equirectMaterial=xh());const s=r?this._cubemapMaterial:this._equirectMaterial,a=new Tn(this._lodPlanes[0],s),o=s.uniforms;o.envMap.value=e;const l=this._cubeSize;Ka(t,0,0,3*l,2*l),n.setRenderTarget(t),n.render(a,Tl)}_applyPMREM(e){const t=this._renderer,n=t.autoClear;t.autoClear=!1;const r=this._lodPlanes.length;for(let s=1;s<r;s++){const a=Math.sqrt(this._sigmas[s]*this._sigmas[s]-this._sigmas[s-1]*this._sigmas[s-1]),o=gh[(r-s-1)%gh.length];this._blur(e,s-1,s,a,o)}t.autoClear=n}_blur(e,t,n,r,s){const a=this._pingPongRenderTarget;this._halfBlur(e,a,t,n,r,"latitudinal",s),this._halfBlur(a,e,n,n,r,"longitudinal",s)}_halfBlur(e,t,n,r,s,a,o){const l=this._renderer,c=this._blurMaterial;a!=="latitudinal"&&a!=="longitudinal"&&console.error("blur direction must be either latitudinal or longitudinal!");const u=3,h=new Tn(this._lodPlanes[r],c),d=c.uniforms,m=this._sizeLods[n]-1,_=isFinite(s)?Math.PI/(2*m):2*Math.PI/(2*Tr-1),v=s/_,p=isFinite(s)?1+Math.floor(u*v):Tr;p>Tr&&console.warn(`sigmaRadians, ${s}, is too large and will clip, as it requested ${p} samples when the maximum is set to ${Tr}`);const f=[];let E=0;for(let L=0;L<Tr;++L){const O=L/v,w=Math.exp(-O*O/2);f.push(w),L===0?E+=w:L<p&&(E+=2*w)}for(let L=0;L<f.length;L++)f[L]=f[L]/E;d.envMap.value=e.texture,d.samples.value=p,d.weights.value=f,d.latitudinal.value=a==="latitudinal",o&&(d.poleAxis.value=o);const{_lodMax:S}=this;d.dTheta.value=_,d.mipInt.value=S-n;const T=this._sizeLods[r],z=3*T*(r>S-gs?r-S+gs:0),R=4*(this._cubeSize-T);Ka(t,z,R,3*T,2*T),l.setRenderTarget(t),l.render(h,Tl)}}function iv(i){const e=[],t=[],n=[];let r=i;const s=i-gs+1+ph.length;for(let a=0;a<s;a++){const o=Math.pow(2,r);t.push(o);let l=1/o;a>i-gs?l=ph[a-i+gs-1]:a===0&&(l=0),n.push(l);const c=1/(o-2),u=-c,h=1+c,d=[u,u,h,u,h,h,u,u,h,h,u,h],m=6,_=6,v=3,p=2,f=1,E=new Float32Array(v*_*m),S=new Float32Array(p*_*m),T=new Float32Array(f*_*m);for(let R=0;R<m;R++){const L=R%3*2/3-1,O=R>2?0:-1,w=[L,O,0,L+2/3,O,0,L+2/3,O+1,0,L,O,0,L+2/3,O+1,0,L,O+1,0];E.set(w,v*_*R),S.set(d,p*_*R);const x=[R,R,R,R,R,R];T.set(x,f*_*R)}const z=new ln;z.setAttribute("position",new si(E,v)),z.setAttribute("uv",new si(S,p)),z.setAttribute("faceIndex",new si(T,f)),e.push(z),r>gs&&r--}return{lodPlanes:e,sizeLods:t,sigmas:n}}function vh(i,e,t){const n=new Lr(i,e,t);return n.texture.mapping=Io,n.texture.name="PMREM.cubeUv",n.scissorTest=!0,n}function Ka(i,e,t,n,r){i.viewport.set(e,t,n,r),i.scissor.set(e,t,n,r)}function rv(i,e,t){const n=new Float32Array(Tr),r=new H(0,1,0);return new rr({name:"SphericalGaussianBlur",defines:{n:Tr,CUBEUV_TEXEL_WIDTH:1/e,CUBEUV_TEXEL_HEIGHT:1/t,CUBEUV_MAX_MIP:`${i}.0`},uniforms:{envMap:{value:null},samples:{value:1},weights:{value:n},latitudinal:{value:!1},dTheta:{value:0},mipInt:{value:0},poleAxis:{value:r}},vertexShader:Jc(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			varying vec3 vOutputDirection;

			uniform sampler2D envMap;
			uniform int samples;
			uniform float weights[ n ];
			uniform bool latitudinal;
			uniform float dTheta;
			uniform float mipInt;
			uniform vec3 poleAxis;

			#define ENVMAP_TYPE_CUBE_UV
			#include <cube_uv_reflection_fragment>

			vec3 getSample( float theta, vec3 axis ) {

				float cosTheta = cos( theta );
				// Rodrigues' axis-angle rotation
				vec3 sampleDirection = vOutputDirection * cosTheta
					+ cross( axis, vOutputDirection ) * sin( theta )
					+ axis * dot( axis, vOutputDirection ) * ( 1.0 - cosTheta );

				return bilinearCubeUV( envMap, sampleDirection, mipInt );

			}

			void main() {

				vec3 axis = latitudinal ? poleAxis : cross( poleAxis, vOutputDirection );

				if ( all( equal( axis, vec3( 0.0 ) ) ) ) {

					axis = vec3( vOutputDirection.z, 0.0, - vOutputDirection.x );

				}

				axis = normalize( axis );

				gl_FragColor = vec4( 0.0, 0.0, 0.0, 1.0 );
				gl_FragColor.rgb += weights[ 0 ] * getSample( 0.0, axis );

				for ( int i = 1; i < n; i++ ) {

					if ( i >= samples ) {

						break;

					}

					float theta = dTheta * float( i );
					gl_FragColor.rgb += weights[ i ] * getSample( -1.0 * theta, axis );
					gl_FragColor.rgb += weights[ i ] * getSample( theta, axis );

				}

			}
		`,blending:Qi,depthTest:!1,depthWrite:!1})}function xh(){return new rr({name:"EquirectangularToCubeUV",uniforms:{envMap:{value:null}},vertexShader:Jc(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			varying vec3 vOutputDirection;

			uniform sampler2D envMap;

			#include <common>

			void main() {

				vec3 outputDirection = normalize( vOutputDirection );
				vec2 uv = equirectUv( outputDirection );

				gl_FragColor = vec4( texture2D ( envMap, uv ).rgb, 1.0 );

			}
		`,blending:Qi,depthTest:!1,depthWrite:!1})}function yh(){return new rr({name:"CubemapToCubeUV",uniforms:{envMap:{value:null},flipEnvMap:{value:-1}},vertexShader:Jc(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			uniform float flipEnvMap;

			varying vec3 vOutputDirection;

			uniform samplerCube envMap;

			void main() {

				gl_FragColor = textureCube( envMap, vec3( flipEnvMap * vOutputDirection.x, vOutputDirection.yz ) );

			}
		`,blending:Qi,depthTest:!1,depthWrite:!1})}function Jc(){return`

		precision mediump float;
		precision mediump int;

		attribute float faceIndex;

		varying vec3 vOutputDirection;

		// RH coordinate system; PMREM face-indexing convention
		vec3 getDirection( vec2 uv, float face ) {

			uv = 2.0 * uv - 1.0;

			vec3 direction = vec3( uv, 1.0 );

			if ( face == 0.0 ) {

				direction = direction.zyx; // ( 1, v, u ) pos x

			} else if ( face == 1.0 ) {

				direction = direction.xzy;
				direction.xz *= -1.0; // ( -u, 1, -v ) pos y

			} else if ( face == 2.0 ) {

				direction.x *= -1.0; // ( -u, v, 1 ) pos z

			} else if ( face == 3.0 ) {

				direction = direction.zyx;
				direction.xz *= -1.0; // ( -1, v, -u ) neg x

			} else if ( face == 4.0 ) {

				direction = direction.xzy;
				direction.xy *= -1.0; // ( -u, -1, v ) neg y

			} else if ( face == 5.0 ) {

				direction.z *= -1.0; // ( u, v, -1 ) neg z

			}

			return direction;

		}

		void main() {

			vOutputDirection = getDirection( uv, faceIndex );
			gl_Position = vec4( position, 1.0 );

		}
	`}function sv(i){let e=new WeakMap,t=null;function n(o){if(o&&o.isTexture){const l=o.mapping,c=l===$l||l===jl,u=l===bs||l===Ts;if(c||u){let h=e.get(o);const d=h!==void 0?h.texture.pmremVersion:0;if(o.isRenderTargetTexture&&o.pmremVersion!==d)return t===null&&(t=new _h(i)),h=c?t.fromEquirectangular(o,h):t.fromCubemap(o,h),h.texture.pmremVersion=o.pmremVersion,e.set(o,h),h.texture;if(h!==void 0)return h.texture;{const m=o.image;return c&&m&&m.height>0||u&&m&&r(m)?(t===null&&(t=new _h(i)),h=c?t.fromEquirectangular(o):t.fromCubemap(o),h.texture.pmremVersion=o.pmremVersion,e.set(o,h),o.addEventListener("dispose",s),h.texture):null}}}return o}function r(o){let l=0;const c=6;for(let u=0;u<c;u++)o[u]!==void 0&&l++;return l===c}function s(o){const l=o.target;l.removeEventListener("dispose",s);const c=e.get(l);c!==void 0&&(e.delete(l),c.dispose())}function a(){e=new WeakMap,t!==null&&(t.dispose(),t=null)}return{get:n,dispose:a}}function av(i){const e={};function t(n){if(e[n]!==void 0)return e[n];let r;switch(n){case"WEBGL_depth_texture":r=i.getExtension("WEBGL_depth_texture")||i.getExtension("MOZ_WEBGL_depth_texture")||i.getExtension("WEBKIT_WEBGL_depth_texture");break;case"EXT_texture_filter_anisotropic":r=i.getExtension("EXT_texture_filter_anisotropic")||i.getExtension("MOZ_EXT_texture_filter_anisotropic")||i.getExtension("WEBKIT_EXT_texture_filter_anisotropic");break;case"WEBGL_compressed_texture_s3tc":r=i.getExtension("WEBGL_compressed_texture_s3tc")||i.getExtension("MOZ_WEBGL_compressed_texture_s3tc")||i.getExtension("WEBKIT_WEBGL_compressed_texture_s3tc");break;case"WEBGL_compressed_texture_pvrtc":r=i.getExtension("WEBGL_compressed_texture_pvrtc")||i.getExtension("WEBKIT_WEBGL_compressed_texture_pvrtc");break;default:r=i.getExtension(n)}return e[n]=r,r}return{has:function(n){return t(n)!==null},init:function(){t("EXT_color_buffer_float"),t("WEBGL_clip_cull_distance"),t("OES_texture_float_linear"),t("EXT_color_buffer_half_float"),t("WEBGL_multisampled_render_to_texture"),t("WEBGL_render_shared_exponent")},get:function(n){const r=t(n);return r===null&&ys("THREE.WebGLRenderer: "+n+" extension not supported."),r}}}function ov(i,e,t,n){const r={},s=new WeakMap;function a(h){const d=h.target;d.index!==null&&e.remove(d.index);for(const _ in d.attributes)e.remove(d.attributes[_]);for(const _ in d.morphAttributes){const v=d.morphAttributes[_];for(let p=0,f=v.length;p<f;p++)e.remove(v[p])}d.removeEventListener("dispose",a),delete r[d.id];const m=s.get(d);m&&(e.remove(m),s.delete(d)),n.releaseStatesOfGeometry(d),d.isInstancedBufferGeometry===!0&&delete d._maxInstanceCount,t.memory.geometries--}function o(h,d){return r[d.id]===!0||(d.addEventListener("dispose",a),r[d.id]=!0,t.memory.geometries++),d}function l(h){const d=h.attributes;for(const _ in d)e.update(d[_],i.ARRAY_BUFFER);const m=h.morphAttributes;for(const _ in m){const v=m[_];for(let p=0,f=v.length;p<f;p++)e.update(v[p],i.ARRAY_BUFFER)}}function c(h){const d=[],m=h.index,_=h.attributes.position;let v=0;if(m!==null){const E=m.array;v=m.version;for(let S=0,T=E.length;S<T;S+=3){const z=E[S+0],R=E[S+1],L=E[S+2];d.push(z,R,R,L,L,z)}}else if(_!==void 0){const E=_.array;v=_.version;for(let S=0,T=E.length/3-1;S<T;S+=3){const z=S+0,R=S+1,L=S+2;d.push(z,R,R,L,L,z)}}else return;const p=new(af(d)?hf:uf)(d,1);p.version=v;const f=s.get(h);f&&e.remove(f),s.set(h,p)}function u(h){const d=s.get(h);if(d){const m=h.index;m!==null&&d.version<m.version&&c(h)}else c(h);return s.get(h)}return{get:o,update:l,getWireframeAttribute:u}}function lv(i,e,t){let n;function r(d){n=d}let s,a;function o(d){s=d.type,a=d.bytesPerElement}function l(d,m){i.drawElements(n,m,s,d*a),t.update(m,n,1)}function c(d,m,_){_!==0&&(i.drawElementsInstanced(n,m,s,d*a,_),t.update(m,n,_))}function u(d,m,_){if(_===0)return;e.get("WEBGL_multi_draw").multiDrawElementsWEBGL(n,m,0,s,d,0,_);let p=0;for(let f=0;f<_;f++)p+=m[f];t.update(p,n,1)}function h(d,m,_,v){if(_===0)return;const p=e.get("WEBGL_multi_draw");if(p===null)for(let f=0;f<d.length;f++)c(d[f]/a,m[f],v[f]);else{p.multiDrawElementsInstancedWEBGL(n,m,0,s,d,0,v,0,_);let f=0;for(let E=0;E<_;E++)f+=m[E];for(let E=0;E<v.length;E++)t.update(f,n,v[E])}}this.setMode=r,this.setIndex=o,this.render=l,this.renderInstances=c,this.renderMultiDraw=u,this.renderMultiDrawInstances=h}function cv(i){const e={geometries:0,textures:0},t={frame:0,calls:0,triangles:0,points:0,lines:0};function n(s,a,o){switch(t.calls++,a){case i.TRIANGLES:t.triangles+=o*(s/3);break;case i.LINES:t.lines+=o*(s/2);break;case i.LINE_STRIP:t.lines+=o*(s-1);break;case i.LINE_LOOP:t.lines+=o*s;break;case i.POINTS:t.points+=o*s;break;default:console.error("THREE.WebGLInfo: Unknown draw mode:",a);break}}function r(){t.calls=0,t.triangles=0,t.points=0,t.lines=0}return{memory:e,render:t,programs:null,autoReset:!0,reset:r,update:n}}function uv(i,e,t){const n=new WeakMap,r=new Zt;function s(a,o,l){const c=a.morphTargetInfluences,u=o.morphAttributes.position||o.morphAttributes.normal||o.morphAttributes.color,h=u!==void 0?u.length:0;let d=n.get(o);if(d===void 0||d.count!==h){let x=function(){O.dispose(),n.delete(o),o.removeEventListener("dispose",x)};var m=x;d!==void 0&&d.texture.dispose();const _=o.morphAttributes.position!==void 0,v=o.morphAttributes.normal!==void 0,p=o.morphAttributes.color!==void 0,f=o.morphAttributes.position||[],E=o.morphAttributes.normal||[],S=o.morphAttributes.color||[];let T=0;_===!0&&(T=1),v===!0&&(T=2),p===!0&&(T=3);let z=o.attributes.position.count*T,R=1;z>e.maxTextureSize&&(R=Math.ceil(z/e.maxTextureSize),z=e.maxTextureSize);const L=new Float32Array(z*R*4*h),O=new lf(L,z,R,h);O.type=Li,O.needsUpdate=!0;const w=T*4;for(let C=0;C<h;C++){const j=f[C],B=E[C],K=S[C],W=z*R*4*C;for(let J=0;J<j.count;J++){const q=J*w;_===!0&&(r.fromBufferAttribute(j,J),L[W+q+0]=r.x,L[W+q+1]=r.y,L[W+q+2]=r.z,L[W+q+3]=0),v===!0&&(r.fromBufferAttribute(B,J),L[W+q+4]=r.x,L[W+q+5]=r.y,L[W+q+6]=r.z,L[W+q+7]=0),p===!0&&(r.fromBufferAttribute(K,J),L[W+q+8]=r.x,L[W+q+9]=r.y,L[W+q+10]=r.z,L[W+q+11]=K.itemSize===4?r.w:1)}}d={count:h,texture:O,size:new Xe(z,R)},n.set(o,d),o.addEventListener("dispose",x)}if(a.isInstancedMesh===!0&&a.morphTexture!==null)l.getUniforms().setValue(i,"morphTexture",a.morphTexture,t);else{let _=0;for(let p=0;p<c.length;p++)_+=c[p];const v=o.morphTargetsRelative?1:1-_;l.getUniforms().setValue(i,"morphTargetBaseInfluence",v),l.getUniforms().setValue(i,"morphTargetInfluences",c)}l.getUniforms().setValue(i,"morphTargetsTexture",d.texture,t),l.getUniforms().setValue(i,"morphTargetsTextureSize",d.size)}return{update:s}}function hv(i,e,t,n){let r=new WeakMap;function s(l){const c=n.render.frame,u=l.geometry,h=e.get(l,u);if(r.get(h)!==c&&(e.update(h),r.set(h,c)),l.isInstancedMesh&&(l.hasEventListener("dispose",o)===!1&&l.addEventListener("dispose",o),r.get(l)!==c&&(t.update(l.instanceMatrix,i.ARRAY_BUFFER),l.instanceColor!==null&&t.update(l.instanceColor,i.ARRAY_BUFFER),r.set(l,c))),l.isSkinnedMesh){const d=l.skeleton;r.get(d)!==c&&(d.update(),r.set(d,c))}return h}function a(){r=new WeakMap}function o(l){const c=l.target;c.removeEventListener("dispose",o),t.remove(c.instanceMatrix),c.instanceColor!==null&&t.remove(c.instanceColor)}return{update:s,dispose:a}}class gf extends An{constructor(e,t,n,r,s,a,o,l,c,u=vs){if(u!==vs&&u!==As)throw new Error("DepthTexture format must be either THREE.DepthFormat or THREE.DepthStencilFormat");n===void 0&&u===vs&&(n=Pr),n===void 0&&u===As&&(n=ws),super(null,r,s,a,o,l,u,n,c),this.isDepthTexture=!0,this.image={width:e,height:t},this.magFilter=o!==void 0?o:Xn,this.minFilter=l!==void 0?l:Xn,this.flipY=!1,this.generateMipmaps=!1,this.compareFunction=null}copy(e){return super.copy(e),this.compareFunction=e.compareFunction,this}toJSON(e){const t=super.toJSON(e);return this.compareFunction!==null&&(t.compareFunction=this.compareFunction),t}}const _f=new An,Mh=new gf(1,1),vf=new lf,xf=new Zm,yf=new pf,Sh=[],Eh=[],bh=new Float32Array(16),Th=new Float32Array(9),wh=new Float32Array(4);function Ns(i,e,t){const n=i[0];if(n<=0||n>0)return i;const r=e*t;let s=Sh[r];if(s===void 0&&(s=new Float32Array(r),Sh[r]=s),e!==0){n.toArray(s,0);for(let a=1,o=0;a!==e;++a)o+=t,i[a].toArray(s,o)}return s}function Jt(i,e){if(i.length!==e.length)return!1;for(let t=0,n=i.length;t<n;t++)if(i[t]!==e[t])return!1;return!0}function Qt(i,e){for(let t=0,n=e.length;t<n;t++)i[t]=e[t]}function Fo(i,e){let t=Eh[e];t===void 0&&(t=new Int32Array(e),Eh[e]=t);for(let n=0;n!==e;++n)t[n]=i.allocateTextureUnit();return t}function dv(i,e){const t=this.cache;t[0]!==e&&(i.uniform1f(this.addr,e),t[0]=e)}function fv(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(i.uniform2f(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(Jt(t,e))return;i.uniform2fv(this.addr,e),Qt(t,e)}}function pv(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(i.uniform3f(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else if(e.r!==void 0)(t[0]!==e.r||t[1]!==e.g||t[2]!==e.b)&&(i.uniform3f(this.addr,e.r,e.g,e.b),t[0]=e.r,t[1]=e.g,t[2]=e.b);else{if(Jt(t,e))return;i.uniform3fv(this.addr,e),Qt(t,e)}}function mv(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(i.uniform4f(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(Jt(t,e))return;i.uniform4fv(this.addr,e),Qt(t,e)}}function gv(i,e){const t=this.cache,n=e.elements;if(n===void 0){if(Jt(t,e))return;i.uniformMatrix2fv(this.addr,!1,e),Qt(t,e)}else{if(Jt(t,n))return;wh.set(n),i.uniformMatrix2fv(this.addr,!1,wh),Qt(t,n)}}function _v(i,e){const t=this.cache,n=e.elements;if(n===void 0){if(Jt(t,e))return;i.uniformMatrix3fv(this.addr,!1,e),Qt(t,e)}else{if(Jt(t,n))return;Th.set(n),i.uniformMatrix3fv(this.addr,!1,Th),Qt(t,n)}}function vv(i,e){const t=this.cache,n=e.elements;if(n===void 0){if(Jt(t,e))return;i.uniformMatrix4fv(this.addr,!1,e),Qt(t,e)}else{if(Jt(t,n))return;bh.set(n),i.uniformMatrix4fv(this.addr,!1,bh),Qt(t,n)}}function xv(i,e){const t=this.cache;t[0]!==e&&(i.uniform1i(this.addr,e),t[0]=e)}function yv(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(i.uniform2i(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(Jt(t,e))return;i.uniform2iv(this.addr,e),Qt(t,e)}}function Mv(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(i.uniform3i(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(Jt(t,e))return;i.uniform3iv(this.addr,e),Qt(t,e)}}function Sv(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(i.uniform4i(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(Jt(t,e))return;i.uniform4iv(this.addr,e),Qt(t,e)}}function Ev(i,e){const t=this.cache;t[0]!==e&&(i.uniform1ui(this.addr,e),t[0]=e)}function bv(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(i.uniform2ui(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(Jt(t,e))return;i.uniform2uiv(this.addr,e),Qt(t,e)}}function Tv(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(i.uniform3ui(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(Jt(t,e))return;i.uniform3uiv(this.addr,e),Qt(t,e)}}function wv(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(i.uniform4ui(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(Jt(t,e))return;i.uniform4uiv(this.addr,e),Qt(t,e)}}function Av(i,e,t){const n=this.cache,r=t.allocateTextureUnit();n[0]!==r&&(i.uniform1i(this.addr,r),n[0]=r);let s;this.type===i.SAMPLER_2D_SHADOW?(Mh.compareFunction=sf,s=Mh):s=_f,t.setTexture2D(e||s,r)}function Rv(i,e,t){const n=this.cache,r=t.allocateTextureUnit();n[0]!==r&&(i.uniform1i(this.addr,r),n[0]=r),t.setTexture3D(e||xf,r)}function Cv(i,e,t){const n=this.cache,r=t.allocateTextureUnit();n[0]!==r&&(i.uniform1i(this.addr,r),n[0]=r),t.setTextureCube(e||yf,r)}function Pv(i,e,t){const n=this.cache,r=t.allocateTextureUnit();n[0]!==r&&(i.uniform1i(this.addr,r),n[0]=r),t.setTexture2DArray(e||vf,r)}function Lv(i){switch(i){case 5126:return dv;case 35664:return fv;case 35665:return pv;case 35666:return mv;case 35674:return gv;case 35675:return _v;case 35676:return vv;case 5124:case 35670:return xv;case 35667:case 35671:return yv;case 35668:case 35672:return Mv;case 35669:case 35673:return Sv;case 5125:return Ev;case 36294:return bv;case 36295:return Tv;case 36296:return wv;case 35678:case 36198:case 36298:case 36306:case 35682:return Av;case 35679:case 36299:case 36307:return Rv;case 35680:case 36300:case 36308:case 36293:return Cv;case 36289:case 36303:case 36311:case 36292:return Pv}}function Dv(i,e){i.uniform1fv(this.addr,e)}function Iv(i,e){const t=Ns(e,this.size,2);i.uniform2fv(this.addr,t)}function Uv(i,e){const t=Ns(e,this.size,3);i.uniform3fv(this.addr,t)}function Nv(i,e){const t=Ns(e,this.size,4);i.uniform4fv(this.addr,t)}function Fv(i,e){const t=Ns(e,this.size,4);i.uniformMatrix2fv(this.addr,!1,t)}function Ov(i,e){const t=Ns(e,this.size,9);i.uniformMatrix3fv(this.addr,!1,t)}function Bv(i,e){const t=Ns(e,this.size,16);i.uniformMatrix4fv(this.addr,!1,t)}function zv(i,e){i.uniform1iv(this.addr,e)}function kv(i,e){i.uniform2iv(this.addr,e)}function Hv(i,e){i.uniform3iv(this.addr,e)}function Vv(i,e){i.uniform4iv(this.addr,e)}function Gv(i,e){i.uniform1uiv(this.addr,e)}function Wv(i,e){i.uniform2uiv(this.addr,e)}function Xv(i,e){i.uniform3uiv(this.addr,e)}function qv(i,e){i.uniform4uiv(this.addr,e)}function Yv(i,e,t){const n=this.cache,r=e.length,s=Fo(t,r);Jt(n,s)||(i.uniform1iv(this.addr,s),Qt(n,s));for(let a=0;a!==r;++a)t.setTexture2D(e[a]||_f,s[a])}function $v(i,e,t){const n=this.cache,r=e.length,s=Fo(t,r);Jt(n,s)||(i.uniform1iv(this.addr,s),Qt(n,s));for(let a=0;a!==r;++a)t.setTexture3D(e[a]||xf,s[a])}function jv(i,e,t){const n=this.cache,r=e.length,s=Fo(t,r);Jt(n,s)||(i.uniform1iv(this.addr,s),Qt(n,s));for(let a=0;a!==r;++a)t.setTextureCube(e[a]||yf,s[a])}function Kv(i,e,t){const n=this.cache,r=e.length,s=Fo(t,r);Jt(n,s)||(i.uniform1iv(this.addr,s),Qt(n,s));for(let a=0;a!==r;++a)t.setTexture2DArray(e[a]||vf,s[a])}function Zv(i){switch(i){case 5126:return Dv;case 35664:return Iv;case 35665:return Uv;case 35666:return Nv;case 35674:return Fv;case 35675:return Ov;case 35676:return Bv;case 5124:case 35670:return zv;case 35667:case 35671:return kv;case 35668:case 35672:return Hv;case 35669:case 35673:return Vv;case 5125:return Gv;case 36294:return Wv;case 36295:return Xv;case 36296:return qv;case 35678:case 36198:case 36298:case 36306:case 35682:return Yv;case 35679:case 36299:case 36307:return $v;case 35680:case 36300:case 36308:case 36293:return jv;case 36289:case 36303:case 36311:case 36292:return Kv}}class Jv{constructor(e,t,n){this.id=e,this.addr=n,this.cache=[],this.type=t.type,this.setValue=Lv(t.type)}}class Qv{constructor(e,t,n){this.id=e,this.addr=n,this.cache=[],this.type=t.type,this.size=t.size,this.setValue=Zv(t.type)}}class ex{constructor(e){this.id=e,this.seq=[],this.map={}}setValue(e,t,n){const r=this.seq;for(let s=0,a=r.length;s!==a;++s){const o=r[s];o.setValue(e,t[o.id],n)}}}const Pl=/(\w+)(\])?(\[|\.)?/g;function Ah(i,e){i.seq.push(e),i.map[e.id]=e}function tx(i,e,t){const n=i.name,r=n.length;for(Pl.lastIndex=0;;){const s=Pl.exec(n),a=Pl.lastIndex;let o=s[1];const l=s[2]==="]",c=s[3];if(l&&(o=o|0),c===void 0||c==="["&&a+2===r){Ah(t,c===void 0?new Jv(o,i,e):new Qv(o,i,e));break}else{let h=t.map[o];h===void 0&&(h=new ex(o),Ah(t,h)),t=h}}}class xo{constructor(e,t){this.seq=[],this.map={};const n=e.getProgramParameter(t,e.ACTIVE_UNIFORMS);for(let r=0;r<n;++r){const s=e.getActiveUniform(t,r),a=e.getUniformLocation(t,s.name);tx(s,a,this)}}setValue(e,t,n,r){const s=this.map[t];s!==void 0&&s.setValue(e,n,r)}setOptional(e,t,n){const r=t[n];r!==void 0&&this.setValue(e,n,r)}static upload(e,t,n,r){for(let s=0,a=t.length;s!==a;++s){const o=t[s],l=n[o.id];l.needsUpdate!==!1&&o.setValue(e,l.value,r)}}static seqWithValue(e,t){const n=[];for(let r=0,s=e.length;r!==s;++r){const a=e[r];a.id in t&&n.push(a)}return n}}function Rh(i,e,t){const n=i.createShader(e);return i.shaderSource(n,t),i.compileShader(n),n}const nx=37297;let ix=0;function rx(i,e){const t=i.split(`
`),n=[],r=Math.max(e-6,0),s=Math.min(e+6,t.length);for(let a=r;a<s;a++){const o=a+1;n.push(`${o===e?">":" "} ${o}: ${t[a]}`)}return n.join(`
`)}function sx(i){const e=Mt.getPrimaries(Mt.workingColorSpace),t=Mt.getPrimaries(i);let n;switch(e===t?n="":e===bo&&t===Eo?n="LinearDisplayP3ToLinearSRGB":e===Eo&&t===bo&&(n="LinearSRGBToLinearDisplayP3"),i){case lr:case Uo:return[n,"LinearTransferOETF"];case pi:case $c:return[n,"sRGBTransferOETF"];default:return console.warn("THREE.WebGLProgram: Unsupported color space:",i),[n,"LinearTransferOETF"]}}function Ch(i,e,t){const n=i.getShaderParameter(e,i.COMPILE_STATUS),r=i.getShaderInfoLog(e).trim();if(n&&r==="")return"";const s=/ERROR: 0:(\d+)/.exec(r);if(s){const a=parseInt(s[1]);return t.toUpperCase()+`

`+r+`

`+rx(i.getShaderSource(e),a)}else return r}function ax(i,e){const t=sx(e);return`vec4 ${i}( vec4 value ) { return ${t[0]}( ${t[1]}( value ) ); }`}function ox(i,e){let t;switch(e){case hm:t="Linear";break;case dm:t="Reinhard";break;case fm:t="Cineon";break;case Xd:t="ACESFilmic";break;case mm:t="AgX";break;case gm:t="Neutral";break;case pm:t="Custom";break;default:console.warn("THREE.WebGLProgram: Unsupported toneMapping:",e),t="Linear"}return"vec3 "+i+"( vec3 color ) { return "+t+"ToneMapping( color ); }"}const Za=new H;function lx(){Mt.getLuminanceCoefficients(Za);const i=Za.x.toFixed(4),e=Za.y.toFixed(4),t=Za.z.toFixed(4);return["float luminance( const in vec3 rgb ) {",`	const vec3 weights = vec3( ${i}, ${e}, ${t} );`,"	return dot( weights, rgb );","}"].join(`
`)}function cx(i){return[i.extensionClipCullDistance?"#extension GL_ANGLE_clip_cull_distance : require":"",i.extensionMultiDraw?"#extension GL_ANGLE_multi_draw : require":""].filter(sa).join(`
`)}function ux(i){const e=[];for(const t in i){const n=i[t];n!==!1&&e.push("#define "+t+" "+n)}return e.join(`
`)}function hx(i,e){const t={},n=i.getProgramParameter(e,i.ACTIVE_ATTRIBUTES);for(let r=0;r<n;r++){const s=i.getActiveAttrib(e,r),a=s.name;let o=1;s.type===i.FLOAT_MAT2&&(o=2),s.type===i.FLOAT_MAT3&&(o=3),s.type===i.FLOAT_MAT4&&(o=4),t[a]={type:s.type,location:i.getAttribLocation(e,a),locationSize:o}}return t}function sa(i){return i!==""}function Ph(i,e){const t=e.numSpotLightShadows+e.numSpotLightMaps-e.numSpotLightShadowsWithMaps;return i.replace(/NUM_DIR_LIGHTS/g,e.numDirLights).replace(/NUM_SPOT_LIGHTS/g,e.numSpotLights).replace(/NUM_SPOT_LIGHT_MAPS/g,e.numSpotLightMaps).replace(/NUM_SPOT_LIGHT_COORDS/g,t).replace(/NUM_RECT_AREA_LIGHTS/g,e.numRectAreaLights).replace(/NUM_POINT_LIGHTS/g,e.numPointLights).replace(/NUM_HEMI_LIGHTS/g,e.numHemiLights).replace(/NUM_DIR_LIGHT_SHADOWS/g,e.numDirLightShadows).replace(/NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS/g,e.numSpotLightShadowsWithMaps).replace(/NUM_SPOT_LIGHT_SHADOWS/g,e.numSpotLightShadows).replace(/NUM_POINT_LIGHT_SHADOWS/g,e.numPointLightShadows)}function Lh(i,e){return i.replace(/NUM_CLIPPING_PLANES/g,e.numClippingPlanes).replace(/UNION_CLIPPING_PLANES/g,e.numClippingPlanes-e.numClipIntersection)}const dx=/^[ \t]*#include +<([\w\d./]+)>/gm;function wc(i){return i.replace(dx,px)}const fx=new Map;function px(i,e){let t=it[e];if(t===void 0){const n=fx.get(e);if(n!==void 0)t=it[n],console.warn('THREE.WebGLRenderer: Shader chunk "%s" has been deprecated. Use "%s" instead.',e,n);else throw new Error("Can not resolve #include <"+e+">")}return wc(t)}const mx=/#pragma unroll_loop_start\s+for\s*\(\s*int\s+i\s*=\s*(\d+)\s*;\s*i\s*<\s*(\d+)\s*;\s*i\s*\+\+\s*\)\s*{([\s\S]+?)}\s+#pragma unroll_loop_end/g;function Dh(i){return i.replace(mx,gx)}function gx(i,e,t,n){let r="";for(let s=parseInt(e);s<parseInt(t);s++)r+=n.replace(/\[\s*i\s*\]/g,"[ "+s+" ]").replace(/UNROLLED_LOOP_INDEX/g,s);return r}function Ih(i){let e=`precision ${i.precision} float;
	precision ${i.precision} int;
	precision ${i.precision} sampler2D;
	precision ${i.precision} samplerCube;
	precision ${i.precision} sampler3D;
	precision ${i.precision} sampler2DArray;
	precision ${i.precision} sampler2DShadow;
	precision ${i.precision} samplerCubeShadow;
	precision ${i.precision} sampler2DArrayShadow;
	precision ${i.precision} isampler2D;
	precision ${i.precision} isampler3D;
	precision ${i.precision} isamplerCube;
	precision ${i.precision} isampler2DArray;
	precision ${i.precision} usampler2D;
	precision ${i.precision} usampler3D;
	precision ${i.precision} usamplerCube;
	precision ${i.precision} usampler2DArray;
	`;return i.precision==="highp"?e+=`
#define HIGH_PRECISION`:i.precision==="mediump"?e+=`
#define MEDIUM_PRECISION`:i.precision==="lowp"&&(e+=`
#define LOW_PRECISION`),e}function _x(i){let e="SHADOWMAP_TYPE_BASIC";return i.shadowMapType===Vd?e="SHADOWMAP_TYPE_PCF":i.shadowMapType===Gd?e="SHADOWMAP_TYPE_PCF_SOFT":i.shadowMapType===Ci&&(e="SHADOWMAP_TYPE_VSM"),e}function vx(i){let e="ENVMAP_TYPE_CUBE";if(i.envMap)switch(i.envMapMode){case bs:case Ts:e="ENVMAP_TYPE_CUBE";break;case Io:e="ENVMAP_TYPE_CUBE_UV";break}return e}function xx(i){let e="ENVMAP_MODE_REFLECTION";if(i.envMap)switch(i.envMapMode){case Ts:e="ENVMAP_MODE_REFRACTION";break}return e}function yx(i){let e="ENVMAP_BLENDING_NONE";if(i.envMap)switch(i.combine){case Wd:e="ENVMAP_BLENDING_MULTIPLY";break;case cm:e="ENVMAP_BLENDING_MIX";break;case um:e="ENVMAP_BLENDING_ADD";break}return e}function Mx(i){const e=i.envMapCubeUVHeight;if(e===null)return null;const t=Math.log2(e)-2,n=1/e;return{texelWidth:1/(3*Math.max(Math.pow(2,t),7*16)),texelHeight:n,maxMip:t}}function Sx(i,e,t,n){const r=i.getContext(),s=t.defines;let a=t.vertexShader,o=t.fragmentShader;const l=_x(t),c=vx(t),u=xx(t),h=yx(t),d=Mx(t),m=cx(t),_=ux(s),v=r.createProgram();let p,f,E=t.glslVersion?"#version "+t.glslVersion+`
`:"";t.isRawShaderMaterial?(p=["#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,_].filter(sa).join(`
`),p.length>0&&(p+=`
`),f=["#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,_].filter(sa).join(`
`),f.length>0&&(f+=`
`)):(p=[Ih(t),"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,_,t.extensionClipCullDistance?"#define USE_CLIP_DISTANCE":"",t.batching?"#define USE_BATCHING":"",t.batchingColor?"#define USE_BATCHING_COLOR":"",t.instancing?"#define USE_INSTANCING":"",t.instancingColor?"#define USE_INSTANCING_COLOR":"",t.instancingMorph?"#define USE_INSTANCING_MORPH":"",t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.map?"#define USE_MAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+u:"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",t.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",t.displacementMap?"#define USE_DISPLACEMENTMAP":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.anisotropy?"#define USE_ANISOTROPY":"",t.anisotropyMap?"#define USE_ANISOTROPYMAP":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",t.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaHash?"#define USE_ALPHAHASH":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",t.mapUv?"#define MAP_UV "+t.mapUv:"",t.alphaMapUv?"#define ALPHAMAP_UV "+t.alphaMapUv:"",t.lightMapUv?"#define LIGHTMAP_UV "+t.lightMapUv:"",t.aoMapUv?"#define AOMAP_UV "+t.aoMapUv:"",t.emissiveMapUv?"#define EMISSIVEMAP_UV "+t.emissiveMapUv:"",t.bumpMapUv?"#define BUMPMAP_UV "+t.bumpMapUv:"",t.normalMapUv?"#define NORMALMAP_UV "+t.normalMapUv:"",t.displacementMapUv?"#define DISPLACEMENTMAP_UV "+t.displacementMapUv:"",t.metalnessMapUv?"#define METALNESSMAP_UV "+t.metalnessMapUv:"",t.roughnessMapUv?"#define ROUGHNESSMAP_UV "+t.roughnessMapUv:"",t.anisotropyMapUv?"#define ANISOTROPYMAP_UV "+t.anisotropyMapUv:"",t.clearcoatMapUv?"#define CLEARCOATMAP_UV "+t.clearcoatMapUv:"",t.clearcoatNormalMapUv?"#define CLEARCOAT_NORMALMAP_UV "+t.clearcoatNormalMapUv:"",t.clearcoatRoughnessMapUv?"#define CLEARCOAT_ROUGHNESSMAP_UV "+t.clearcoatRoughnessMapUv:"",t.iridescenceMapUv?"#define IRIDESCENCEMAP_UV "+t.iridescenceMapUv:"",t.iridescenceThicknessMapUv?"#define IRIDESCENCE_THICKNESSMAP_UV "+t.iridescenceThicknessMapUv:"",t.sheenColorMapUv?"#define SHEEN_COLORMAP_UV "+t.sheenColorMapUv:"",t.sheenRoughnessMapUv?"#define SHEEN_ROUGHNESSMAP_UV "+t.sheenRoughnessMapUv:"",t.specularMapUv?"#define SPECULARMAP_UV "+t.specularMapUv:"",t.specularColorMapUv?"#define SPECULAR_COLORMAP_UV "+t.specularColorMapUv:"",t.specularIntensityMapUv?"#define SPECULAR_INTENSITYMAP_UV "+t.specularIntensityMapUv:"",t.transmissionMapUv?"#define TRANSMISSIONMAP_UV "+t.transmissionMapUv:"",t.thicknessMapUv?"#define THICKNESSMAP_UV "+t.thicknessMapUv:"",t.vertexTangents&&t.flatShading===!1?"#define USE_TANGENT":"",t.vertexColors?"#define USE_COLOR":"",t.vertexAlphas?"#define USE_COLOR_ALPHA":"",t.vertexUv1s?"#define USE_UV1":"",t.vertexUv2s?"#define USE_UV2":"",t.vertexUv3s?"#define USE_UV3":"",t.pointsUvs?"#define USE_POINTS_UV":"",t.flatShading?"#define FLAT_SHADED":"",t.skinning?"#define USE_SKINNING":"",t.morphTargets?"#define USE_MORPHTARGETS":"",t.morphNormals&&t.flatShading===!1?"#define USE_MORPHNORMALS":"",t.morphColors?"#define USE_MORPHCOLORS":"",t.morphTargetsCount>0?"#define MORPHTARGETS_TEXTURE_STRIDE "+t.morphTextureStride:"",t.morphTargetsCount>0?"#define MORPHTARGETS_COUNT "+t.morphTargetsCount:"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+l:"",t.sizeAttenuation?"#define USE_SIZEATTENUATION":"",t.numLightProbes>0?"#define USE_LIGHT_PROBES":"",t.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"","uniform mat4 modelMatrix;","uniform mat4 modelViewMatrix;","uniform mat4 projectionMatrix;","uniform mat4 viewMatrix;","uniform mat3 normalMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;","#ifdef USE_INSTANCING","	attribute mat4 instanceMatrix;","#endif","#ifdef USE_INSTANCING_COLOR","	attribute vec3 instanceColor;","#endif","#ifdef USE_INSTANCING_MORPH","	uniform sampler2D morphTexture;","#endif","attribute vec3 position;","attribute vec3 normal;","attribute vec2 uv;","#ifdef USE_UV1","	attribute vec2 uv1;","#endif","#ifdef USE_UV2","	attribute vec2 uv2;","#endif","#ifdef USE_UV3","	attribute vec2 uv3;","#endif","#ifdef USE_TANGENT","	attribute vec4 tangent;","#endif","#if defined( USE_COLOR_ALPHA )","	attribute vec4 color;","#elif defined( USE_COLOR )","	attribute vec3 color;","#endif","#ifdef USE_SKINNING","	attribute vec4 skinIndex;","	attribute vec4 skinWeight;","#endif",`
`].filter(sa).join(`
`),f=[Ih(t),"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,_,t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.alphaToCoverage?"#define ALPHA_TO_COVERAGE":"",t.map?"#define USE_MAP":"",t.matcap?"#define USE_MATCAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+c:"",t.envMap?"#define "+u:"",t.envMap?"#define "+h:"",d?"#define CUBEUV_TEXEL_WIDTH "+d.texelWidth:"",d?"#define CUBEUV_TEXEL_HEIGHT "+d.texelHeight:"",d?"#define CUBEUV_MAX_MIP "+d.maxMip+".0":"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",t.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.anisotropy?"#define USE_ANISOTROPY":"",t.anisotropyMap?"#define USE_ANISOTROPYMAP":"",t.clearcoat?"#define USE_CLEARCOAT":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.dispersion?"#define USE_DISPERSION":"",t.iridescence?"#define USE_IRIDESCENCE":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",t.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaTest?"#define USE_ALPHATEST":"",t.alphaHash?"#define USE_ALPHAHASH":"",t.sheen?"#define USE_SHEEN":"",t.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.vertexTangents&&t.flatShading===!1?"#define USE_TANGENT":"",t.vertexColors||t.instancingColor||t.batchingColor?"#define USE_COLOR":"",t.vertexAlphas?"#define USE_COLOR_ALPHA":"",t.vertexUv1s?"#define USE_UV1":"",t.vertexUv2s?"#define USE_UV2":"",t.vertexUv3s?"#define USE_UV3":"",t.pointsUvs?"#define USE_POINTS_UV":"",t.gradientMap?"#define USE_GRADIENTMAP":"",t.flatShading?"#define FLAT_SHADED":"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+l:"",t.premultipliedAlpha?"#define PREMULTIPLIED_ALPHA":"",t.numLightProbes>0?"#define USE_LIGHT_PROBES":"",t.decodeVideoTexture?"#define DECODE_VIDEO_TEXTURE":"",t.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"","uniform mat4 viewMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;",t.toneMapping!==er?"#define TONE_MAPPING":"",t.toneMapping!==er?it.tonemapping_pars_fragment:"",t.toneMapping!==er?ox("toneMapping",t.toneMapping):"",t.dithering?"#define DITHERING":"",t.opaque?"#define OPAQUE":"",it.colorspace_pars_fragment,ax("linearToOutputTexel",t.outputColorSpace),lx(),t.useDepthPacking?"#define DEPTH_PACKING "+t.depthPacking:"",`
`].filter(sa).join(`
`)),a=wc(a),a=Ph(a,t),a=Lh(a,t),o=wc(o),o=Ph(o,t),o=Lh(o,t),a=Dh(a),o=Dh(o),t.isRawShaderMaterial!==!0&&(E=`#version 300 es
`,p=[m,"#define attribute in","#define varying out","#define texture2D texture"].join(`
`)+`
`+p,f=["#define varying in",t.glslVersion===Yu?"":"layout(location = 0) out highp vec4 pc_fragColor;",t.glslVersion===Yu?"":"#define gl_FragColor pc_fragColor","#define gl_FragDepthEXT gl_FragDepth","#define texture2D texture","#define textureCube texture","#define texture2DProj textureProj","#define texture2DLodEXT textureLod","#define texture2DProjLodEXT textureProjLod","#define textureCubeLodEXT textureLod","#define texture2DGradEXT textureGrad","#define texture2DProjGradEXT textureProjGrad","#define textureCubeGradEXT textureGrad"].join(`
`)+`
`+f);const S=E+p+a,T=E+f+o,z=Rh(r,r.VERTEX_SHADER,S),R=Rh(r,r.FRAGMENT_SHADER,T);r.attachShader(v,z),r.attachShader(v,R),t.index0AttributeName!==void 0?r.bindAttribLocation(v,0,t.index0AttributeName):t.morphTargets===!0&&r.bindAttribLocation(v,0,"position"),r.linkProgram(v);function L(C){if(i.debug.checkShaderErrors){const j=r.getProgramInfoLog(v).trim(),B=r.getShaderInfoLog(z).trim(),K=r.getShaderInfoLog(R).trim();let W=!0,J=!0;if(r.getProgramParameter(v,r.LINK_STATUS)===!1)if(W=!1,typeof i.debug.onShaderError=="function")i.debug.onShaderError(r,v,z,R);else{const q=Ch(r,z,"vertex"),ee=Ch(r,R,"fragment");console.error("THREE.WebGLProgram: Shader Error "+r.getError()+" - VALIDATE_STATUS "+r.getProgramParameter(v,r.VALIDATE_STATUS)+`

Material Name: `+C.name+`
Material Type: `+C.type+`

Program Info Log: `+j+`
`+q+`
`+ee)}else j!==""?console.warn("THREE.WebGLProgram: Program Info Log:",j):(B===""||K==="")&&(J=!1);J&&(C.diagnostics={runnable:W,programLog:j,vertexShader:{log:B,prefix:p},fragmentShader:{log:K,prefix:f}})}r.deleteShader(z),r.deleteShader(R),O=new xo(r,v),w=hx(r,v)}let O;this.getUniforms=function(){return O===void 0&&L(this),O};let w;this.getAttributes=function(){return w===void 0&&L(this),w};let x=t.rendererExtensionParallelShaderCompile===!1;return this.isReady=function(){return x===!1&&(x=r.getProgramParameter(v,nx)),x},this.destroy=function(){n.releaseStatesOfProgram(this),r.deleteProgram(v),this.program=void 0},this.type=t.shaderType,this.name=t.shaderName,this.id=ix++,this.cacheKey=e,this.usedTimes=1,this.program=v,this.vertexShader=z,this.fragmentShader=R,this}let Ex=0;class bx{constructor(){this.shaderCache=new Map,this.materialCache=new Map}update(e){const t=e.vertexShader,n=e.fragmentShader,r=this._getShaderStage(t),s=this._getShaderStage(n),a=this._getShaderCacheForMaterial(e);return a.has(r)===!1&&(a.add(r),r.usedTimes++),a.has(s)===!1&&(a.add(s),s.usedTimes++),this}remove(e){const t=this.materialCache.get(e);for(const n of t)n.usedTimes--,n.usedTimes===0&&this.shaderCache.delete(n.code);return this.materialCache.delete(e),this}getVertexShaderID(e){return this._getShaderStage(e.vertexShader).id}getFragmentShaderID(e){return this._getShaderStage(e.fragmentShader).id}dispose(){this.shaderCache.clear(),this.materialCache.clear()}_getShaderCacheForMaterial(e){const t=this.materialCache;let n=t.get(e);return n===void 0&&(n=new Set,t.set(e,n)),n}_getShaderStage(e){const t=this.shaderCache;let n=t.get(e);return n===void 0&&(n=new Tx(e),t.set(e,n)),n}}class Tx{constructor(e){this.id=Ex++,this.code=e,this.usedTimes=0}}function wx(i,e,t,n,r,s,a){const o=new Kc,l=new bx,c=new Set,u=[],h=r.logarithmicDepthBuffer,d=r.vertexTextures;let m=r.precision;const _={MeshDepthMaterial:"depth",MeshDistanceMaterial:"distanceRGBA",MeshNormalMaterial:"normal",MeshBasicMaterial:"basic",MeshLambertMaterial:"lambert",MeshPhongMaterial:"phong",MeshToonMaterial:"toon",MeshStandardMaterial:"physical",MeshPhysicalMaterial:"physical",MeshMatcapMaterial:"matcap",LineBasicMaterial:"basic",LineDashedMaterial:"dashed",PointsMaterial:"points",ShadowMaterial:"shadow",SpriteMaterial:"sprite"};function v(w){return c.add(w),w===0?"uv":`uv${w}`}function p(w,x,C,j,B){const K=j.fog,W=B.geometry,J=w.isMeshStandardMaterial?j.environment:null,q=(w.isMeshStandardMaterial?t:e).get(w.envMap||J),ee=q&&q.mapping===Io?q.image.height:null,me=_[w.type];w.precision!==null&&(m=r.getMaxPrecision(w.precision),m!==w.precision&&console.warn("THREE.WebGLProgram.getParameters:",w.precision,"not supported, using",m,"instead."));const he=W.morphAttributes.position||W.morphAttributes.normal||W.morphAttributes.color,ve=he!==void 0?he.length:0;let Te=0;W.morphAttributes.position!==void 0&&(Te=1),W.morphAttributes.normal!==void 0&&(Te=2),W.morphAttributes.color!==void 0&&(Te=3);let xe,te,ce,ye;if(me){const at=mi[me];xe=at.vertexShader,te=at.fragmentShader}else xe=w.vertexShader,te=w.fragmentShader,l.update(w),ce=l.getVertexShaderID(w),ye=l.getFragmentShaderID(w);const de=i.getRenderTarget(),Be=B.isInstancedMesh===!0,Ve=B.isBatchedMesh===!0,Ne=!!w.map,dt=!!w.matcap,U=!!q,ut=!!w.aoMap,nt=!!w.lightMap,ot=!!w.bumpMap,Fe=!!w.normalMap,St=!!w.displacementMap,qe=!!w.emissiveMap,We=!!w.metalnessMap,D=!!w.roughnessMap,M=w.anisotropy>0,Z=w.clearcoat>0,oe=w.dispersion>0,Q=w.iridescence>0,G=w.sheen>0,Ee=w.transmission>0,ge=M&&!!w.anisotropyMap,Ae=Z&&!!w.clearcoatMap,je=Z&&!!w.clearcoatNormalMap,pe=Z&&!!w.clearcoatRoughnessMap,we=Q&&!!w.iridescenceMap,Ke=Q&&!!w.iridescenceThicknessMap,ze=G&&!!w.sheenColorMap,Se=G&&!!w.sheenRoughnessMap,ke=!!w.specularMap,N=!!w.specularColorMap,le=!!w.specularIntensityMap,I=Ee&&!!w.transmissionMap,re=Ee&&!!w.thicknessMap,ne=!!w.gradientMap,ie=!!w.alphaMap,_e=w.alphaTest>0,$e=!!w.alphaHash,st=!!w.extensions;let mt=er;w.toneMapped&&(de===null||de.isXRRenderTarget===!0)&&(mt=i.toneMapping);const Et={shaderID:me,shaderType:w.type,shaderName:w.name,vertexShader:xe,fragmentShader:te,defines:w.defines,customVertexShaderID:ce,customFragmentShaderID:ye,isRawShaderMaterial:w.isRawShaderMaterial===!0,glslVersion:w.glslVersion,precision:m,batching:Ve,batchingColor:Ve&&B._colorsTexture!==null,instancing:Be,instancingColor:Be&&B.instanceColor!==null,instancingMorph:Be&&B.morphTexture!==null,supportsVertexTextures:d,outputColorSpace:de===null?i.outputColorSpace:de.isXRRenderTarget===!0?de.texture.colorSpace:lr,alphaToCoverage:!!w.alphaToCoverage,map:Ne,matcap:dt,envMap:U,envMapMode:U&&q.mapping,envMapCubeUVHeight:ee,aoMap:ut,lightMap:nt,bumpMap:ot,normalMap:Fe,displacementMap:d&&St,emissiveMap:qe,normalMapObjectSpace:Fe&&w.normalMapType===ym,normalMapTangentSpace:Fe&&w.normalMapType===rf,metalnessMap:We,roughnessMap:D,anisotropy:M,anisotropyMap:ge,clearcoat:Z,clearcoatMap:Ae,clearcoatNormalMap:je,clearcoatRoughnessMap:pe,dispersion:oe,iridescence:Q,iridescenceMap:we,iridescenceThicknessMap:Ke,sheen:G,sheenColorMap:ze,sheenRoughnessMap:Se,specularMap:ke,specularColorMap:N,specularIntensityMap:le,transmission:Ee,transmissionMap:I,thicknessMap:re,gradientMap:ne,opaque:w.transparent===!1&&w.blending===_s&&w.alphaToCoverage===!1,alphaMap:ie,alphaTest:_e,alphaHash:$e,combine:w.combine,mapUv:Ne&&v(w.map.channel),aoMapUv:ut&&v(w.aoMap.channel),lightMapUv:nt&&v(w.lightMap.channel),bumpMapUv:ot&&v(w.bumpMap.channel),normalMapUv:Fe&&v(w.normalMap.channel),displacementMapUv:St&&v(w.displacementMap.channel),emissiveMapUv:qe&&v(w.emissiveMap.channel),metalnessMapUv:We&&v(w.metalnessMap.channel),roughnessMapUv:D&&v(w.roughnessMap.channel),anisotropyMapUv:ge&&v(w.anisotropyMap.channel),clearcoatMapUv:Ae&&v(w.clearcoatMap.channel),clearcoatNormalMapUv:je&&v(w.clearcoatNormalMap.channel),clearcoatRoughnessMapUv:pe&&v(w.clearcoatRoughnessMap.channel),iridescenceMapUv:we&&v(w.iridescenceMap.channel),iridescenceThicknessMapUv:Ke&&v(w.iridescenceThicknessMap.channel),sheenColorMapUv:ze&&v(w.sheenColorMap.channel),sheenRoughnessMapUv:Se&&v(w.sheenRoughnessMap.channel),specularMapUv:ke&&v(w.specularMap.channel),specularColorMapUv:N&&v(w.specularColorMap.channel),specularIntensityMapUv:le&&v(w.specularIntensityMap.channel),transmissionMapUv:I&&v(w.transmissionMap.channel),thicknessMapUv:re&&v(w.thicknessMap.channel),alphaMapUv:ie&&v(w.alphaMap.channel),vertexTangents:!!W.attributes.tangent&&(Fe||M),vertexColors:w.vertexColors,vertexAlphas:w.vertexColors===!0&&!!W.attributes.color&&W.attributes.color.itemSize===4,pointsUvs:B.isPoints===!0&&!!W.attributes.uv&&(Ne||ie),fog:!!K,useFog:w.fog===!0,fogExp2:!!K&&K.isFogExp2,flatShading:w.flatShading===!0,sizeAttenuation:w.sizeAttenuation===!0,logarithmicDepthBuffer:h,skinning:B.isSkinnedMesh===!0,morphTargets:W.morphAttributes.position!==void 0,morphNormals:W.morphAttributes.normal!==void 0,morphColors:W.morphAttributes.color!==void 0,morphTargetsCount:ve,morphTextureStride:Te,numDirLights:x.directional.length,numPointLights:x.point.length,numSpotLights:x.spot.length,numSpotLightMaps:x.spotLightMap.length,numRectAreaLights:x.rectArea.length,numHemiLights:x.hemi.length,numDirLightShadows:x.directionalShadowMap.length,numPointLightShadows:x.pointShadowMap.length,numSpotLightShadows:x.spotShadowMap.length,numSpotLightShadowsWithMaps:x.numSpotLightShadowsWithMaps,numLightProbes:x.numLightProbes,numClippingPlanes:a.numPlanes,numClipIntersection:a.numIntersection,dithering:w.dithering,shadowMapEnabled:i.shadowMap.enabled&&C.length>0,shadowMapType:i.shadowMap.type,toneMapping:mt,decodeVideoTexture:Ne&&w.map.isVideoTexture===!0&&Mt.getTransfer(w.map.colorSpace)===Nt,premultipliedAlpha:w.premultipliedAlpha,doubleSided:w.side===gi,flipSided:w.side===Cn,useDepthPacking:w.depthPacking>=0,depthPacking:w.depthPacking||0,index0AttributeName:w.index0AttributeName,extensionClipCullDistance:st&&w.extensions.clipCullDistance===!0&&n.has("WEBGL_clip_cull_distance"),extensionMultiDraw:(st&&w.extensions.multiDraw===!0||Ve)&&n.has("WEBGL_multi_draw"),rendererExtensionParallelShaderCompile:n.has("KHR_parallel_shader_compile"),customProgramCacheKey:w.customProgramCacheKey()};return Et.vertexUv1s=c.has(1),Et.vertexUv2s=c.has(2),Et.vertexUv3s=c.has(3),c.clear(),Et}function f(w){const x=[];if(w.shaderID?x.push(w.shaderID):(x.push(w.customVertexShaderID),x.push(w.customFragmentShaderID)),w.defines!==void 0)for(const C in w.defines)x.push(C),x.push(w.defines[C]);return w.isRawShaderMaterial===!1&&(E(x,w),S(x,w),x.push(i.outputColorSpace)),x.push(w.customProgramCacheKey),x.join()}function E(w,x){w.push(x.precision),w.push(x.outputColorSpace),w.push(x.envMapMode),w.push(x.envMapCubeUVHeight),w.push(x.mapUv),w.push(x.alphaMapUv),w.push(x.lightMapUv),w.push(x.aoMapUv),w.push(x.bumpMapUv),w.push(x.normalMapUv),w.push(x.displacementMapUv),w.push(x.emissiveMapUv),w.push(x.metalnessMapUv),w.push(x.roughnessMapUv),w.push(x.anisotropyMapUv),w.push(x.clearcoatMapUv),w.push(x.clearcoatNormalMapUv),w.push(x.clearcoatRoughnessMapUv),w.push(x.iridescenceMapUv),w.push(x.iridescenceThicknessMapUv),w.push(x.sheenColorMapUv),w.push(x.sheenRoughnessMapUv),w.push(x.specularMapUv),w.push(x.specularColorMapUv),w.push(x.specularIntensityMapUv),w.push(x.transmissionMapUv),w.push(x.thicknessMapUv),w.push(x.combine),w.push(x.fogExp2),w.push(x.sizeAttenuation),w.push(x.morphTargetsCount),w.push(x.morphAttributeCount),w.push(x.numDirLights),w.push(x.numPointLights),w.push(x.numSpotLights),w.push(x.numSpotLightMaps),w.push(x.numHemiLights),w.push(x.numRectAreaLights),w.push(x.numDirLightShadows),w.push(x.numPointLightShadows),w.push(x.numSpotLightShadows),w.push(x.numSpotLightShadowsWithMaps),w.push(x.numLightProbes),w.push(x.shadowMapType),w.push(x.toneMapping),w.push(x.numClippingPlanes),w.push(x.numClipIntersection),w.push(x.depthPacking)}function S(w,x){o.disableAll(),x.supportsVertexTextures&&o.enable(0),x.instancing&&o.enable(1),x.instancingColor&&o.enable(2),x.instancingMorph&&o.enable(3),x.matcap&&o.enable(4),x.envMap&&o.enable(5),x.normalMapObjectSpace&&o.enable(6),x.normalMapTangentSpace&&o.enable(7),x.clearcoat&&o.enable(8),x.iridescence&&o.enable(9),x.alphaTest&&o.enable(10),x.vertexColors&&o.enable(11),x.vertexAlphas&&o.enable(12),x.vertexUv1s&&o.enable(13),x.vertexUv2s&&o.enable(14),x.vertexUv3s&&o.enable(15),x.vertexTangents&&o.enable(16),x.anisotropy&&o.enable(17),x.alphaHash&&o.enable(18),x.batching&&o.enable(19),x.dispersion&&o.enable(20),x.batchingColor&&o.enable(21),w.push(o.mask),o.disableAll(),x.fog&&o.enable(0),x.useFog&&o.enable(1),x.flatShading&&o.enable(2),x.logarithmicDepthBuffer&&o.enable(3),x.skinning&&o.enable(4),x.morphTargets&&o.enable(5),x.morphNormals&&o.enable(6),x.morphColors&&o.enable(7),x.premultipliedAlpha&&o.enable(8),x.shadowMapEnabled&&o.enable(9),x.doubleSided&&o.enable(10),x.flipSided&&o.enable(11),x.useDepthPacking&&o.enable(12),x.dithering&&o.enable(13),x.transmission&&o.enable(14),x.sheen&&o.enable(15),x.opaque&&o.enable(16),x.pointsUvs&&o.enable(17),x.decodeVideoTexture&&o.enable(18),x.alphaToCoverage&&o.enable(19),w.push(o.mask)}function T(w){const x=_[w.type];let C;if(x){const j=mi[x];C=cg.clone(j.uniforms)}else C=w.uniforms;return C}function z(w,x){let C;for(let j=0,B=u.length;j<B;j++){const K=u[j];if(K.cacheKey===x){C=K,++C.usedTimes;break}}return C===void 0&&(C=new Sx(i,x,w,s),u.push(C)),C}function R(w){if(--w.usedTimes===0){const x=u.indexOf(w);u[x]=u[u.length-1],u.pop(),w.destroy()}}function L(w){l.remove(w)}function O(){l.dispose()}return{getParameters:p,getProgramCacheKey:f,getUniforms:T,acquireProgram:z,releaseProgram:R,releaseShaderCache:L,programs:u,dispose:O}}function Ax(){let i=new WeakMap;function e(a){return i.has(a)}function t(a){let o=i.get(a);return o===void 0&&(o={},i.set(a,o)),o}function n(a){i.delete(a)}function r(a,o,l){i.get(a)[o]=l}function s(){i=new WeakMap}return{has:e,get:t,remove:n,update:r,dispose:s}}function Rx(i,e){return i.groupOrder!==e.groupOrder?i.groupOrder-e.groupOrder:i.renderOrder!==e.renderOrder?i.renderOrder-e.renderOrder:i.material.id!==e.material.id?i.material.id-e.material.id:i.z!==e.z?i.z-e.z:i.id-e.id}function Uh(i,e){return i.groupOrder!==e.groupOrder?i.groupOrder-e.groupOrder:i.renderOrder!==e.renderOrder?i.renderOrder-e.renderOrder:i.z!==e.z?e.z-i.z:i.id-e.id}function Nh(){const i=[];let e=0;const t=[],n=[],r=[];function s(){e=0,t.length=0,n.length=0,r.length=0}function a(h,d,m,_,v,p){let f=i[e];return f===void 0?(f={id:h.id,object:h,geometry:d,material:m,groupOrder:_,renderOrder:h.renderOrder,z:v,group:p},i[e]=f):(f.id=h.id,f.object=h,f.geometry=d,f.material=m,f.groupOrder=_,f.renderOrder=h.renderOrder,f.z=v,f.group=p),e++,f}function o(h,d,m,_,v,p){const f=a(h,d,m,_,v,p);m.transmission>0?n.push(f):m.transparent===!0?r.push(f):t.push(f)}function l(h,d,m,_,v,p){const f=a(h,d,m,_,v,p);m.transmission>0?n.unshift(f):m.transparent===!0?r.unshift(f):t.unshift(f)}function c(h,d){t.length>1&&t.sort(h||Rx),n.length>1&&n.sort(d||Uh),r.length>1&&r.sort(d||Uh)}function u(){for(let h=e,d=i.length;h<d;h++){const m=i[h];if(m.id===null)break;m.id=null,m.object=null,m.geometry=null,m.material=null,m.group=null}}return{opaque:t,transmissive:n,transparent:r,init:s,push:o,unshift:l,finish:u,sort:c}}function Cx(){let i=new WeakMap;function e(n,r){const s=i.get(n);let a;return s===void 0?(a=new Nh,i.set(n,[a])):r>=s.length?(a=new Nh,s.push(a)):a=s[r],a}function t(){i=new WeakMap}return{get:e,dispose:t}}function Px(){const i={};return{get:function(e){if(i[e.id]!==void 0)return i[e.id];let t;switch(e.type){case"DirectionalLight":t={direction:new H,color:new tt};break;case"SpotLight":t={position:new H,direction:new H,color:new tt,distance:0,coneCos:0,penumbraCos:0,decay:0};break;case"PointLight":t={position:new H,color:new tt,distance:0,decay:0};break;case"HemisphereLight":t={direction:new H,skyColor:new tt,groundColor:new tt};break;case"RectAreaLight":t={color:new tt,position:new H,halfWidth:new H,halfHeight:new H};break}return i[e.id]=t,t}}}function Lx(){const i={};return{get:function(e){if(i[e.id]!==void 0)return i[e.id];let t;switch(e.type){case"DirectionalLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new Xe};break;case"SpotLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new Xe};break;case"PointLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new Xe,shadowCameraNear:1,shadowCameraFar:1e3};break}return i[e.id]=t,t}}}let Dx=0;function Ix(i,e){return(e.castShadow?2:0)-(i.castShadow?2:0)+(e.map?1:0)-(i.map?1:0)}function Ux(i){const e=new Px,t=Lx(),n={version:0,hash:{directionalLength:-1,pointLength:-1,spotLength:-1,rectAreaLength:-1,hemiLength:-1,numDirectionalShadows:-1,numPointShadows:-1,numSpotShadows:-1,numSpotMaps:-1,numLightProbes:-1},ambient:[0,0,0],probe:[],directional:[],directionalShadow:[],directionalShadowMap:[],directionalShadowMatrix:[],spot:[],spotLightMap:[],spotShadow:[],spotShadowMap:[],spotLightMatrix:[],rectArea:[],rectAreaLTC1:null,rectAreaLTC2:null,point:[],pointShadow:[],pointShadowMap:[],pointShadowMatrix:[],hemi:[],numSpotLightShadowsWithMaps:0,numLightProbes:0};for(let c=0;c<9;c++)n.probe.push(new H);const r=new H,s=new Ft,a=new Ft;function o(c){let u=0,h=0,d=0;for(let w=0;w<9;w++)n.probe[w].set(0,0,0);let m=0,_=0,v=0,p=0,f=0,E=0,S=0,T=0,z=0,R=0,L=0;c.sort(Ix);for(let w=0,x=c.length;w<x;w++){const C=c[w],j=C.color,B=C.intensity,K=C.distance,W=C.shadow&&C.shadow.map?C.shadow.map.texture:null;if(C.isAmbientLight)u+=j.r*B,h+=j.g*B,d+=j.b*B;else if(C.isLightProbe){for(let J=0;J<9;J++)n.probe[J].addScaledVector(C.sh.coefficients[J],B);L++}else if(C.isDirectionalLight){const J=e.get(C);if(J.color.copy(C.color).multiplyScalar(C.intensity),C.castShadow){const q=C.shadow,ee=t.get(C);ee.shadowIntensity=q.intensity,ee.shadowBias=q.bias,ee.shadowNormalBias=q.normalBias,ee.shadowRadius=q.radius,ee.shadowMapSize=q.mapSize,n.directionalShadow[m]=ee,n.directionalShadowMap[m]=W,n.directionalShadowMatrix[m]=C.shadow.matrix,E++}n.directional[m]=J,m++}else if(C.isSpotLight){const J=e.get(C);J.position.setFromMatrixPosition(C.matrixWorld),J.color.copy(j).multiplyScalar(B),J.distance=K,J.coneCos=Math.cos(C.angle),J.penumbraCos=Math.cos(C.angle*(1-C.penumbra)),J.decay=C.decay,n.spot[v]=J;const q=C.shadow;if(C.map&&(n.spotLightMap[z]=C.map,z++,q.updateMatrices(C),C.castShadow&&R++),n.spotLightMatrix[v]=q.matrix,C.castShadow){const ee=t.get(C);ee.shadowIntensity=q.intensity,ee.shadowBias=q.bias,ee.shadowNormalBias=q.normalBias,ee.shadowRadius=q.radius,ee.shadowMapSize=q.mapSize,n.spotShadow[v]=ee,n.spotShadowMap[v]=W,T++}v++}else if(C.isRectAreaLight){const J=e.get(C);J.color.copy(j).multiplyScalar(B),J.halfWidth.set(C.width*.5,0,0),J.halfHeight.set(0,C.height*.5,0),n.rectArea[p]=J,p++}else if(C.isPointLight){const J=e.get(C);if(J.color.copy(C.color).multiplyScalar(C.intensity),J.distance=C.distance,J.decay=C.decay,C.castShadow){const q=C.shadow,ee=t.get(C);ee.shadowIntensity=q.intensity,ee.shadowBias=q.bias,ee.shadowNormalBias=q.normalBias,ee.shadowRadius=q.radius,ee.shadowMapSize=q.mapSize,ee.shadowCameraNear=q.camera.near,ee.shadowCameraFar=q.camera.far,n.pointShadow[_]=ee,n.pointShadowMap[_]=W,n.pointShadowMatrix[_]=C.shadow.matrix,S++}n.point[_]=J,_++}else if(C.isHemisphereLight){const J=e.get(C);J.skyColor.copy(C.color).multiplyScalar(B),J.groundColor.copy(C.groundColor).multiplyScalar(B),n.hemi[f]=J,f++}}p>0&&(i.has("OES_texture_float_linear")===!0?(n.rectAreaLTC1=Re.LTC_FLOAT_1,n.rectAreaLTC2=Re.LTC_FLOAT_2):(n.rectAreaLTC1=Re.LTC_HALF_1,n.rectAreaLTC2=Re.LTC_HALF_2)),n.ambient[0]=u,n.ambient[1]=h,n.ambient[2]=d;const O=n.hash;(O.directionalLength!==m||O.pointLength!==_||O.spotLength!==v||O.rectAreaLength!==p||O.hemiLength!==f||O.numDirectionalShadows!==E||O.numPointShadows!==S||O.numSpotShadows!==T||O.numSpotMaps!==z||O.numLightProbes!==L)&&(n.directional.length=m,n.spot.length=v,n.rectArea.length=p,n.point.length=_,n.hemi.length=f,n.directionalShadow.length=E,n.directionalShadowMap.length=E,n.pointShadow.length=S,n.pointShadowMap.length=S,n.spotShadow.length=T,n.spotShadowMap.length=T,n.directionalShadowMatrix.length=E,n.pointShadowMatrix.length=S,n.spotLightMatrix.length=T+z-R,n.spotLightMap.length=z,n.numSpotLightShadowsWithMaps=R,n.numLightProbes=L,O.directionalLength=m,O.pointLength=_,O.spotLength=v,O.rectAreaLength=p,O.hemiLength=f,O.numDirectionalShadows=E,O.numPointShadows=S,O.numSpotShadows=T,O.numSpotMaps=z,O.numLightProbes=L,n.version=Dx++)}function l(c,u){let h=0,d=0,m=0,_=0,v=0;const p=u.matrixWorldInverse;for(let f=0,E=c.length;f<E;f++){const S=c[f];if(S.isDirectionalLight){const T=n.directional[h];T.direction.setFromMatrixPosition(S.matrixWorld),r.setFromMatrixPosition(S.target.matrixWorld),T.direction.sub(r),T.direction.transformDirection(p),h++}else if(S.isSpotLight){const T=n.spot[m];T.position.setFromMatrixPosition(S.matrixWorld),T.position.applyMatrix4(p),T.direction.setFromMatrixPosition(S.matrixWorld),r.setFromMatrixPosition(S.target.matrixWorld),T.direction.sub(r),T.direction.transformDirection(p),m++}else if(S.isRectAreaLight){const T=n.rectArea[_];T.position.setFromMatrixPosition(S.matrixWorld),T.position.applyMatrix4(p),a.identity(),s.copy(S.matrixWorld),s.premultiply(p),a.extractRotation(s),T.halfWidth.set(S.width*.5,0,0),T.halfHeight.set(0,S.height*.5,0),T.halfWidth.applyMatrix4(a),T.halfHeight.applyMatrix4(a),_++}else if(S.isPointLight){const T=n.point[d];T.position.setFromMatrixPosition(S.matrixWorld),T.position.applyMatrix4(p),d++}else if(S.isHemisphereLight){const T=n.hemi[v];T.direction.setFromMatrixPosition(S.matrixWorld),T.direction.transformDirection(p),v++}}}return{setup:o,setupView:l,state:n}}function Fh(i){const e=new Ux(i),t=[],n=[];function r(u){c.camera=u,t.length=0,n.length=0}function s(u){t.push(u)}function a(u){n.push(u)}function o(){e.setup(t)}function l(u){e.setupView(t,u)}const c={lightsArray:t,shadowsArray:n,camera:null,lights:e,transmissionRenderTarget:{}};return{init:r,state:c,setupLights:o,setupLightsView:l,pushLight:s,pushShadow:a}}function Nx(i){let e=new WeakMap;function t(r,s=0){const a=e.get(r);let o;return a===void 0?(o=new Fh(i),e.set(r,[o])):s>=a.length?(o=new Fh(i),a.push(o)):o=a[s],o}function n(){e=new WeakMap}return{get:t,dispose:n}}class Fx extends cr{constructor(e){super(),this.isMeshDepthMaterial=!0,this.type="MeshDepthMaterial",this.depthPacking=vm,this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.wireframe=!1,this.wireframeLinewidth=1,this.setValues(e)}copy(e){return super.copy(e),this.depthPacking=e.depthPacking,this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this}}class Ox extends cr{constructor(e){super(),this.isMeshDistanceMaterial=!0,this.type="MeshDistanceMaterial",this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.setValues(e)}copy(e){return super.copy(e),this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this}}const Bx=`void main() {
	gl_Position = vec4( position, 1.0 );
}`,zx=`uniform sampler2D shadow_pass;
uniform vec2 resolution;
uniform float radius;
#include <packing>
void main() {
	const float samples = float( VSM_SAMPLES );
	float mean = 0.0;
	float squared_mean = 0.0;
	float uvStride = samples <= 1.0 ? 0.0 : 2.0 / ( samples - 1.0 );
	float uvStart = samples <= 1.0 ? 0.0 : - 1.0;
	for ( float i = 0.0; i < samples; i ++ ) {
		float uvOffset = uvStart + i * uvStride;
		#ifdef HORIZONTAL_PASS
			vec2 distribution = unpackRGBATo2Half( texture2D( shadow_pass, ( gl_FragCoord.xy + vec2( uvOffset, 0.0 ) * radius ) / resolution ) );
			mean += distribution.x;
			squared_mean += distribution.y * distribution.y + distribution.x * distribution.x;
		#else
			float depth = unpackRGBAToDepth( texture2D( shadow_pass, ( gl_FragCoord.xy + vec2( 0.0, uvOffset ) * radius ) / resolution ) );
			mean += depth;
			squared_mean += depth * depth;
		#endif
	}
	mean = mean / samples;
	squared_mean = squared_mean / samples;
	float std_dev = sqrt( squared_mean - mean * mean );
	gl_FragColor = pack2HalfToRGBA( vec2( mean, std_dev ) );
}`;function kx(i,e,t){let n=new Zc;const r=new Xe,s=new Xe,a=new Zt,o=new Fx({depthPacking:xm}),l=new Ox,c={},u=t.maxTextureSize,h={[ir]:Cn,[Cn]:ir,[gi]:gi},d=new rr({defines:{VSM_SAMPLES:8},uniforms:{shadow_pass:{value:null},resolution:{value:new Xe},radius:{value:4}},vertexShader:Bx,fragmentShader:zx}),m=d.clone();m.defines.HORIZONTAL_PASS=1;const _=new ln;_.setAttribute("position",new si(new Float32Array([-1,-1,.5,3,-1,.5,-1,3,.5]),3));const v=new Tn(_,d),p=this;this.enabled=!1,this.autoUpdate=!0,this.needsUpdate=!1,this.type=Vd;let f=this.type;this.render=function(R,L,O){if(p.enabled===!1||p.autoUpdate===!1&&p.needsUpdate===!1||R.length===0)return;const w=i.getRenderTarget(),x=i.getActiveCubeFace(),C=i.getActiveMipmapLevel(),j=i.state;j.setBlending(Qi),j.buffers.color.setClear(1,1,1,1),j.buffers.depth.setTest(!0),j.setScissorTest(!1);const B=f!==Ci&&this.type===Ci,K=f===Ci&&this.type!==Ci;for(let W=0,J=R.length;W<J;W++){const q=R[W],ee=q.shadow;if(ee===void 0){console.warn("THREE.WebGLShadowMap:",q,"has no shadow.");continue}if(ee.autoUpdate===!1&&ee.needsUpdate===!1)continue;r.copy(ee.mapSize);const me=ee.getFrameExtents();if(r.multiply(me),s.copy(ee.mapSize),(r.x>u||r.y>u)&&(r.x>u&&(s.x=Math.floor(u/me.x),r.x=s.x*me.x,ee.mapSize.x=s.x),r.y>u&&(s.y=Math.floor(u/me.y),r.y=s.y*me.y,ee.mapSize.y=s.y)),ee.map===null||B===!0||K===!0){const ve=this.type!==Ci?{minFilter:Xn,magFilter:Xn}:{};ee.map!==null&&ee.map.dispose(),ee.map=new Lr(r.x,r.y,ve),ee.map.texture.name=q.name+".shadowMap",ee.camera.updateProjectionMatrix()}i.setRenderTarget(ee.map),i.clear();const he=ee.getViewportCount();for(let ve=0;ve<he;ve++){const Te=ee.getViewport(ve);a.set(s.x*Te.x,s.y*Te.y,s.x*Te.z,s.y*Te.w),j.viewport(a),ee.updateMatrices(q,ve),n=ee.getFrustum(),T(L,O,ee.camera,q,this.type)}ee.isPointLightShadow!==!0&&this.type===Ci&&E(ee,O),ee.needsUpdate=!1}f=this.type,p.needsUpdate=!1,i.setRenderTarget(w,x,C)};function E(R,L){const O=e.update(v);d.defines.VSM_SAMPLES!==R.blurSamples&&(d.defines.VSM_SAMPLES=R.blurSamples,m.defines.VSM_SAMPLES=R.blurSamples,d.needsUpdate=!0,m.needsUpdate=!0),R.mapPass===null&&(R.mapPass=new Lr(r.x,r.y)),d.uniforms.shadow_pass.value=R.map.texture,d.uniforms.resolution.value=R.mapSize,d.uniforms.radius.value=R.radius,i.setRenderTarget(R.mapPass),i.clear(),i.renderBufferDirect(L,null,O,d,v,null),m.uniforms.shadow_pass.value=R.mapPass.texture,m.uniforms.resolution.value=R.mapSize,m.uniforms.radius.value=R.radius,i.setRenderTarget(R.map),i.clear(),i.renderBufferDirect(L,null,O,m,v,null)}function S(R,L,O,w){let x=null;const C=O.isPointLight===!0?R.customDistanceMaterial:R.customDepthMaterial;if(C!==void 0)x=C;else if(x=O.isPointLight===!0?l:o,i.localClippingEnabled&&L.clipShadows===!0&&Array.isArray(L.clippingPlanes)&&L.clippingPlanes.length!==0||L.displacementMap&&L.displacementScale!==0||L.alphaMap&&L.alphaTest>0||L.map&&L.alphaTest>0){const j=x.uuid,B=L.uuid;let K=c[j];K===void 0&&(K={},c[j]=K);let W=K[B];W===void 0&&(W=x.clone(),K[B]=W,L.addEventListener("dispose",z)),x=W}if(x.visible=L.visible,x.wireframe=L.wireframe,w===Ci?x.side=L.shadowSide!==null?L.shadowSide:L.side:x.side=L.shadowSide!==null?L.shadowSide:h[L.side],x.alphaMap=L.alphaMap,x.alphaTest=L.alphaTest,x.map=L.map,x.clipShadows=L.clipShadows,x.clippingPlanes=L.clippingPlanes,x.clipIntersection=L.clipIntersection,x.displacementMap=L.displacementMap,x.displacementScale=L.displacementScale,x.displacementBias=L.displacementBias,x.wireframeLinewidth=L.wireframeLinewidth,x.linewidth=L.linewidth,O.isPointLight===!0&&x.isMeshDistanceMaterial===!0){const j=i.properties.get(x);j.light=O}return x}function T(R,L,O,w,x){if(R.visible===!1)return;if(R.layers.test(L.layers)&&(R.isMesh||R.isLine||R.isPoints)&&(R.castShadow||R.receiveShadow&&x===Ci)&&(!R.frustumCulled||n.intersectsObject(R))){R.modelViewMatrix.multiplyMatrices(O.matrixWorldInverse,R.matrixWorld);const B=e.update(R),K=R.material;if(Array.isArray(K)){const W=B.groups;for(let J=0,q=W.length;J<q;J++){const ee=W[J],me=K[ee.materialIndex];if(me&&me.visible){const he=S(R,me,w,x);R.onBeforeShadow(i,R,L,O,B,he,ee),i.renderBufferDirect(O,null,B,he,R,ee),R.onAfterShadow(i,R,L,O,B,he,ee)}}}else if(K.visible){const W=S(R,K,w,x);R.onBeforeShadow(i,R,L,O,B,W,null),i.renderBufferDirect(O,null,B,W,R,null),R.onAfterShadow(i,R,L,O,B,W,null)}}const j=R.children;for(let B=0,K=j.length;B<K;B++)T(j[B],L,O,w,x)}function z(R){R.target.removeEventListener("dispose",z);for(const O in c){const w=c[O],x=R.target.uuid;x in w&&(w[x].dispose(),delete w[x])}}}function Hx(i){function e(){let I=!1;const re=new Zt;let ne=null;const ie=new Zt(0,0,0,0);return{setMask:function(_e){ne!==_e&&!I&&(i.colorMask(_e,_e,_e,_e),ne=_e)},setLocked:function(_e){I=_e},setClear:function(_e,$e,st,mt,Et){Et===!0&&(_e*=mt,$e*=mt,st*=mt),re.set(_e,$e,st,mt),ie.equals(re)===!1&&(i.clearColor(_e,$e,st,mt),ie.copy(re))},reset:function(){I=!1,ne=null,ie.set(-1,0,0,0)}}}function t(){let I=!1,re=null,ne=null,ie=null;return{setTest:function(_e){_e?ye(i.DEPTH_TEST):de(i.DEPTH_TEST)},setMask:function(_e){re!==_e&&!I&&(i.depthMask(_e),re=_e)},setFunc:function(_e){if(ne!==_e){switch(_e){case nm:i.depthFunc(i.NEVER);break;case im:i.depthFunc(i.ALWAYS);break;case rm:i.depthFunc(i.LESS);break;case Mo:i.depthFunc(i.LEQUAL);break;case sm:i.depthFunc(i.EQUAL);break;case am:i.depthFunc(i.GEQUAL);break;case om:i.depthFunc(i.GREATER);break;case lm:i.depthFunc(i.NOTEQUAL);break;default:i.depthFunc(i.LEQUAL)}ne=_e}},setLocked:function(_e){I=_e},setClear:function(_e){ie!==_e&&(i.clearDepth(_e),ie=_e)},reset:function(){I=!1,re=null,ne=null,ie=null}}}function n(){let I=!1,re=null,ne=null,ie=null,_e=null,$e=null,st=null,mt=null,Et=null;return{setTest:function(at){I||(at?ye(i.STENCIL_TEST):de(i.STENCIL_TEST))},setMask:function(at){re!==at&&!I&&(i.stencilMask(at),re=at)},setFunc:function(at,un,Ot){(ne!==at||ie!==un||_e!==Ot)&&(i.stencilFunc(at,un,Ot),ne=at,ie=un,_e=Ot)},setOp:function(at,un,Ot){($e!==at||st!==un||mt!==Ot)&&(i.stencilOp(at,un,Ot),$e=at,st=un,mt=Ot)},setLocked:function(at){I=at},setClear:function(at){Et!==at&&(i.clearStencil(at),Et=at)},reset:function(){I=!1,re=null,ne=null,ie=null,_e=null,$e=null,st=null,mt=null,Et=null}}}const r=new e,s=new t,a=new n,o=new WeakMap,l=new WeakMap;let c={},u={},h=new WeakMap,d=[],m=null,_=!1,v=null,p=null,f=null,E=null,S=null,T=null,z=null,R=new tt(0,0,0),L=0,O=!1,w=null,x=null,C=null,j=null,B=null;const K=i.getParameter(i.MAX_COMBINED_TEXTURE_IMAGE_UNITS);let W=!1,J=0;const q=i.getParameter(i.VERSION);q.indexOf("WebGL")!==-1?(J=parseFloat(/^WebGL (\d)/.exec(q)[1]),W=J>=1):q.indexOf("OpenGL ES")!==-1&&(J=parseFloat(/^OpenGL ES (\d)/.exec(q)[1]),W=J>=2);let ee=null,me={};const he=i.getParameter(i.SCISSOR_BOX),ve=i.getParameter(i.VIEWPORT),Te=new Zt().fromArray(he),xe=new Zt().fromArray(ve);function te(I,re,ne,ie){const _e=new Uint8Array(4),$e=i.createTexture();i.bindTexture(I,$e),i.texParameteri(I,i.TEXTURE_MIN_FILTER,i.NEAREST),i.texParameteri(I,i.TEXTURE_MAG_FILTER,i.NEAREST);for(let st=0;st<ne;st++)I===i.TEXTURE_3D||I===i.TEXTURE_2D_ARRAY?i.texImage3D(re,0,i.RGBA,1,1,ie,0,i.RGBA,i.UNSIGNED_BYTE,_e):i.texImage2D(re+st,0,i.RGBA,1,1,0,i.RGBA,i.UNSIGNED_BYTE,_e);return $e}const ce={};ce[i.TEXTURE_2D]=te(i.TEXTURE_2D,i.TEXTURE_2D,1),ce[i.TEXTURE_CUBE_MAP]=te(i.TEXTURE_CUBE_MAP,i.TEXTURE_CUBE_MAP_POSITIVE_X,6),ce[i.TEXTURE_2D_ARRAY]=te(i.TEXTURE_2D_ARRAY,i.TEXTURE_2D_ARRAY,1,1),ce[i.TEXTURE_3D]=te(i.TEXTURE_3D,i.TEXTURE_3D,1,1),r.setClear(0,0,0,1),s.setClear(1),a.setClear(0),ye(i.DEPTH_TEST),s.setFunc(Mo),ot(!1),Fe(Vu),ye(i.CULL_FACE),ut(Qi);function ye(I){c[I]!==!0&&(i.enable(I),c[I]=!0)}function de(I){c[I]!==!1&&(i.disable(I),c[I]=!1)}function Be(I,re){return u[I]!==re?(i.bindFramebuffer(I,re),u[I]=re,I===i.DRAW_FRAMEBUFFER&&(u[i.FRAMEBUFFER]=re),I===i.FRAMEBUFFER&&(u[i.DRAW_FRAMEBUFFER]=re),!0):!1}function Ve(I,re){let ne=d,ie=!1;if(I){ne=h.get(re),ne===void 0&&(ne=[],h.set(re,ne));const _e=I.textures;if(ne.length!==_e.length||ne[0]!==i.COLOR_ATTACHMENT0){for(let $e=0,st=_e.length;$e<st;$e++)ne[$e]=i.COLOR_ATTACHMENT0+$e;ne.length=_e.length,ie=!0}}else ne[0]!==i.BACK&&(ne[0]=i.BACK,ie=!0);ie&&i.drawBuffers(ne)}function Ne(I){return m!==I?(i.useProgram(I),m=I,!0):!1}const dt={[br]:i.FUNC_ADD,[zp]:i.FUNC_SUBTRACT,[kp]:i.FUNC_REVERSE_SUBTRACT};dt[Hp]=i.MIN,dt[Vp]=i.MAX;const U={[Gp]:i.ZERO,[Wp]:i.ONE,[Xp]:i.SRC_COLOR,[ql]:i.SRC_ALPHA,[Zp]:i.SRC_ALPHA_SATURATE,[jp]:i.DST_COLOR,[Yp]:i.DST_ALPHA,[qp]:i.ONE_MINUS_SRC_COLOR,[Yl]:i.ONE_MINUS_SRC_ALPHA,[Kp]:i.ONE_MINUS_DST_COLOR,[$p]:i.ONE_MINUS_DST_ALPHA,[Jp]:i.CONSTANT_COLOR,[Qp]:i.ONE_MINUS_CONSTANT_COLOR,[em]:i.CONSTANT_ALPHA,[tm]:i.ONE_MINUS_CONSTANT_ALPHA};function ut(I,re,ne,ie,_e,$e,st,mt,Et,at){if(I===Qi){_===!0&&(de(i.BLEND),_=!1);return}if(_===!1&&(ye(i.BLEND),_=!0),I!==Bp){if(I!==v||at!==O){if((p!==br||S!==br)&&(i.blendEquation(i.FUNC_ADD),p=br,S=br),at)switch(I){case _s:i.blendFuncSeparate(i.ONE,i.ONE_MINUS_SRC_ALPHA,i.ONE,i.ONE_MINUS_SRC_ALPHA);break;case Gu:i.blendFunc(i.ONE,i.ONE);break;case Wu:i.blendFuncSeparate(i.ZERO,i.ONE_MINUS_SRC_COLOR,i.ZERO,i.ONE);break;case Xu:i.blendFuncSeparate(i.ZERO,i.SRC_COLOR,i.ZERO,i.SRC_ALPHA);break;default:console.error("THREE.WebGLState: Invalid blending: ",I);break}else switch(I){case _s:i.blendFuncSeparate(i.SRC_ALPHA,i.ONE_MINUS_SRC_ALPHA,i.ONE,i.ONE_MINUS_SRC_ALPHA);break;case Gu:i.blendFunc(i.SRC_ALPHA,i.ONE);break;case Wu:i.blendFuncSeparate(i.ZERO,i.ONE_MINUS_SRC_COLOR,i.ZERO,i.ONE);break;case Xu:i.blendFunc(i.ZERO,i.SRC_COLOR);break;default:console.error("THREE.WebGLState: Invalid blending: ",I);break}f=null,E=null,T=null,z=null,R.set(0,0,0),L=0,v=I,O=at}return}_e=_e||re,$e=$e||ne,st=st||ie,(re!==p||_e!==S)&&(i.blendEquationSeparate(dt[re],dt[_e]),p=re,S=_e),(ne!==f||ie!==E||$e!==T||st!==z)&&(i.blendFuncSeparate(U[ne],U[ie],U[$e],U[st]),f=ne,E=ie,T=$e,z=st),(mt.equals(R)===!1||Et!==L)&&(i.blendColor(mt.r,mt.g,mt.b,Et),R.copy(mt),L=Et),v=I,O=!1}function nt(I,re){I.side===gi?de(i.CULL_FACE):ye(i.CULL_FACE);let ne=I.side===Cn;re&&(ne=!ne),ot(ne),I.blending===_s&&I.transparent===!1?ut(Qi):ut(I.blending,I.blendEquation,I.blendSrc,I.blendDst,I.blendEquationAlpha,I.blendSrcAlpha,I.blendDstAlpha,I.blendColor,I.blendAlpha,I.premultipliedAlpha),s.setFunc(I.depthFunc),s.setTest(I.depthTest),s.setMask(I.depthWrite),r.setMask(I.colorWrite);const ie=I.stencilWrite;a.setTest(ie),ie&&(a.setMask(I.stencilWriteMask),a.setFunc(I.stencilFunc,I.stencilRef,I.stencilFuncMask),a.setOp(I.stencilFail,I.stencilZFail,I.stencilZPass)),qe(I.polygonOffset,I.polygonOffsetFactor,I.polygonOffsetUnits),I.alphaToCoverage===!0?ye(i.SAMPLE_ALPHA_TO_COVERAGE):de(i.SAMPLE_ALPHA_TO_COVERAGE)}function ot(I){w!==I&&(I?i.frontFace(i.CW):i.frontFace(i.CCW),w=I)}function Fe(I){I!==Fp?(ye(i.CULL_FACE),I!==x&&(I===Vu?i.cullFace(i.BACK):I===Op?i.cullFace(i.FRONT):i.cullFace(i.FRONT_AND_BACK))):de(i.CULL_FACE),x=I}function St(I){I!==C&&(W&&i.lineWidth(I),C=I)}function qe(I,re,ne){I?(ye(i.POLYGON_OFFSET_FILL),(j!==re||B!==ne)&&(i.polygonOffset(re,ne),j=re,B=ne)):de(i.POLYGON_OFFSET_FILL)}function We(I){I?ye(i.SCISSOR_TEST):de(i.SCISSOR_TEST)}function D(I){I===void 0&&(I=i.TEXTURE0+K-1),ee!==I&&(i.activeTexture(I),ee=I)}function M(I,re,ne){ne===void 0&&(ee===null?ne=i.TEXTURE0+K-1:ne=ee);let ie=me[ne];ie===void 0&&(ie={type:void 0,texture:void 0},me[ne]=ie),(ie.type!==I||ie.texture!==re)&&(ee!==ne&&(i.activeTexture(ne),ee=ne),i.bindTexture(I,re||ce[I]),ie.type=I,ie.texture=re)}function Z(){const I=me[ee];I!==void 0&&I.type!==void 0&&(i.bindTexture(I.type,null),I.type=void 0,I.texture=void 0)}function oe(){try{i.compressedTexImage2D.apply(i,arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function Q(){try{i.compressedTexImage3D.apply(i,arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function G(){try{i.texSubImage2D.apply(i,arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function Ee(){try{i.texSubImage3D.apply(i,arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function ge(){try{i.compressedTexSubImage2D.apply(i,arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function Ae(){try{i.compressedTexSubImage3D.apply(i,arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function je(){try{i.texStorage2D.apply(i,arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function pe(){try{i.texStorage3D.apply(i,arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function we(){try{i.texImage2D.apply(i,arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function Ke(){try{i.texImage3D.apply(i,arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function ze(I){Te.equals(I)===!1&&(i.scissor(I.x,I.y,I.z,I.w),Te.copy(I))}function Se(I){xe.equals(I)===!1&&(i.viewport(I.x,I.y,I.z,I.w),xe.copy(I))}function ke(I,re){let ne=l.get(re);ne===void 0&&(ne=new WeakMap,l.set(re,ne));let ie=ne.get(I);ie===void 0&&(ie=i.getUniformBlockIndex(re,I.name),ne.set(I,ie))}function N(I,re){const ie=l.get(re).get(I);o.get(re)!==ie&&(i.uniformBlockBinding(re,ie,I.__bindingPointIndex),o.set(re,ie))}function le(){i.disable(i.BLEND),i.disable(i.CULL_FACE),i.disable(i.DEPTH_TEST),i.disable(i.POLYGON_OFFSET_FILL),i.disable(i.SCISSOR_TEST),i.disable(i.STENCIL_TEST),i.disable(i.SAMPLE_ALPHA_TO_COVERAGE),i.blendEquation(i.FUNC_ADD),i.blendFunc(i.ONE,i.ZERO),i.blendFuncSeparate(i.ONE,i.ZERO,i.ONE,i.ZERO),i.blendColor(0,0,0,0),i.colorMask(!0,!0,!0,!0),i.clearColor(0,0,0,0),i.depthMask(!0),i.depthFunc(i.LESS),i.clearDepth(1),i.stencilMask(4294967295),i.stencilFunc(i.ALWAYS,0,4294967295),i.stencilOp(i.KEEP,i.KEEP,i.KEEP),i.clearStencil(0),i.cullFace(i.BACK),i.frontFace(i.CCW),i.polygonOffset(0,0),i.activeTexture(i.TEXTURE0),i.bindFramebuffer(i.FRAMEBUFFER,null),i.bindFramebuffer(i.DRAW_FRAMEBUFFER,null),i.bindFramebuffer(i.READ_FRAMEBUFFER,null),i.useProgram(null),i.lineWidth(1),i.scissor(0,0,i.canvas.width,i.canvas.height),i.viewport(0,0,i.canvas.width,i.canvas.height),c={},ee=null,me={},u={},h=new WeakMap,d=[],m=null,_=!1,v=null,p=null,f=null,E=null,S=null,T=null,z=null,R=new tt(0,0,0),L=0,O=!1,w=null,x=null,C=null,j=null,B=null,Te.set(0,0,i.canvas.width,i.canvas.height),xe.set(0,0,i.canvas.width,i.canvas.height),r.reset(),s.reset(),a.reset()}return{buffers:{color:r,depth:s,stencil:a},enable:ye,disable:de,bindFramebuffer:Be,drawBuffers:Ve,useProgram:Ne,setBlending:ut,setMaterial:nt,setFlipSided:ot,setCullFace:Fe,setLineWidth:St,setPolygonOffset:qe,setScissorTest:We,activeTexture:D,bindTexture:M,unbindTexture:Z,compressedTexImage2D:oe,compressedTexImage3D:Q,texImage2D:we,texImage3D:Ke,updateUBOMapping:ke,uniformBlockBinding:N,texStorage2D:je,texStorage3D:pe,texSubImage2D:G,texSubImage3D:Ee,compressedTexSubImage2D:ge,compressedTexSubImage3D:Ae,scissor:ze,viewport:Se,reset:le}}function Oh(i,e,t,n){const r=Vx(n);switch(t){case Kd:return i*e;case Jd:return i*e;case Qd:return i*e*2;case ef:return i*e/r.components*r.byteLength;case Xc:return i*e/r.components*r.byteLength;case tf:return i*e*2/r.components*r.byteLength;case qc:return i*e*2/r.components*r.byteLength;case Zd:return i*e*3/r.components*r.byteLength;case ri:return i*e*4/r.components*r.byteLength;case Yc:return i*e*4/r.components*r.byteLength;case po:case mo:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*8;case go:case _o:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*16;case Ql:case tc:return Math.max(i,16)*Math.max(e,8)/4;case Jl:case ec:return Math.max(i,8)*Math.max(e,8)/2;case nc:case ic:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*8;case rc:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*16;case sc:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*16;case ac:return Math.floor((i+4)/5)*Math.floor((e+3)/4)*16;case oc:return Math.floor((i+4)/5)*Math.floor((e+4)/5)*16;case lc:return Math.floor((i+5)/6)*Math.floor((e+4)/5)*16;case cc:return Math.floor((i+5)/6)*Math.floor((e+5)/6)*16;case uc:return Math.floor((i+7)/8)*Math.floor((e+4)/5)*16;case hc:return Math.floor((i+7)/8)*Math.floor((e+5)/6)*16;case dc:return Math.floor((i+7)/8)*Math.floor((e+7)/8)*16;case fc:return Math.floor((i+9)/10)*Math.floor((e+4)/5)*16;case pc:return Math.floor((i+9)/10)*Math.floor((e+5)/6)*16;case mc:return Math.floor((i+9)/10)*Math.floor((e+7)/8)*16;case gc:return Math.floor((i+9)/10)*Math.floor((e+9)/10)*16;case _c:return Math.floor((i+11)/12)*Math.floor((e+9)/10)*16;case vc:return Math.floor((i+11)/12)*Math.floor((e+11)/12)*16;case vo:case xc:case yc:return Math.ceil(i/4)*Math.ceil(e/4)*16;case nf:case Mc:return Math.ceil(i/4)*Math.ceil(e/4)*8;case Sc:case Ec:return Math.ceil(i/4)*Math.ceil(e/4)*16}throw new Error(`Unable to determine texture byte length for ${t} format.`)}function Vx(i){switch(i){case Oi:case Yd:return{byteLength:1,components:1};case ma:case $d:case va:return{byteLength:2,components:1};case Gc:case Wc:return{byteLength:2,components:4};case Pr:case Vc:case Li:return{byteLength:4,components:1};case jd:return{byteLength:4,components:3}}throw new Error(`Unknown texture type ${i}.`)}function Gx(i,e,t,n,r,s,a){const o=e.has("WEBGL_multisampled_render_to_texture")?e.get("WEBGL_multisampled_render_to_texture"):null,l=typeof navigator>"u"?!1:/OculusBrowser/g.test(navigator.userAgent),c=new Xe,u=new WeakMap;let h;const d=new WeakMap;let m=!1;try{m=typeof OffscreenCanvas<"u"&&new OffscreenCanvas(1,1).getContext("2d")!==null}catch{}function _(D,M){return m?new OffscreenCanvas(D,M):wo("canvas")}function v(D,M,Z){let oe=1;const Q=We(D);if((Q.width>Z||Q.height>Z)&&(oe=Z/Math.max(Q.width,Q.height)),oe<1)if(typeof HTMLImageElement<"u"&&D instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&D instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&D instanceof ImageBitmap||typeof VideoFrame<"u"&&D instanceof VideoFrame){const G=Math.floor(oe*Q.width),Ee=Math.floor(oe*Q.height);h===void 0&&(h=_(G,Ee));const ge=M?_(G,Ee):h;return ge.width=G,ge.height=Ee,ge.getContext("2d").drawImage(D,0,0,G,Ee),console.warn("THREE.WebGLRenderer: Texture has been resized from ("+Q.width+"x"+Q.height+") to ("+G+"x"+Ee+")."),ge}else return"data"in D&&console.warn("THREE.WebGLRenderer: Image in DataTexture is too big ("+Q.width+"x"+Q.height+")."),D;return D}function p(D){return D.generateMipmaps&&D.minFilter!==Xn&&D.minFilter!==ti}function f(D){i.generateMipmap(D)}function E(D,M,Z,oe,Q=!1){if(D!==null){if(i[D]!==void 0)return i[D];console.warn("THREE.WebGLRenderer: Attempt to use non-existing WebGL internal format '"+D+"'")}let G=M;if(M===i.RED&&(Z===i.FLOAT&&(G=i.R32F),Z===i.HALF_FLOAT&&(G=i.R16F),Z===i.UNSIGNED_BYTE&&(G=i.R8)),M===i.RED_INTEGER&&(Z===i.UNSIGNED_BYTE&&(G=i.R8UI),Z===i.UNSIGNED_SHORT&&(G=i.R16UI),Z===i.UNSIGNED_INT&&(G=i.R32UI),Z===i.BYTE&&(G=i.R8I),Z===i.SHORT&&(G=i.R16I),Z===i.INT&&(G=i.R32I)),M===i.RG&&(Z===i.FLOAT&&(G=i.RG32F),Z===i.HALF_FLOAT&&(G=i.RG16F),Z===i.UNSIGNED_BYTE&&(G=i.RG8)),M===i.RG_INTEGER&&(Z===i.UNSIGNED_BYTE&&(G=i.RG8UI),Z===i.UNSIGNED_SHORT&&(G=i.RG16UI),Z===i.UNSIGNED_INT&&(G=i.RG32UI),Z===i.BYTE&&(G=i.RG8I),Z===i.SHORT&&(G=i.RG16I),Z===i.INT&&(G=i.RG32I)),M===i.RGB&&Z===i.UNSIGNED_INT_5_9_9_9_REV&&(G=i.RGB9_E5),M===i.RGBA){const Ee=Q?So:Mt.getTransfer(oe);Z===i.FLOAT&&(G=i.RGBA32F),Z===i.HALF_FLOAT&&(G=i.RGBA16F),Z===i.UNSIGNED_BYTE&&(G=Ee===Nt?i.SRGB8_ALPHA8:i.RGBA8),Z===i.UNSIGNED_SHORT_4_4_4_4&&(G=i.RGBA4),Z===i.UNSIGNED_SHORT_5_5_5_1&&(G=i.RGB5_A1)}return(G===i.R16F||G===i.R32F||G===i.RG16F||G===i.RG32F||G===i.RGBA16F||G===i.RGBA32F)&&e.get("EXT_color_buffer_float"),G}function S(D,M){let Z;return D?M===null||M===Pr||M===ws?Z=i.DEPTH24_STENCIL8:M===Li?Z=i.DEPTH32F_STENCIL8:M===ma&&(Z=i.DEPTH24_STENCIL8,console.warn("DepthTexture: 16 bit depth attachment is not supported with stencil. Using 24-bit attachment.")):M===null||M===Pr||M===ws?Z=i.DEPTH_COMPONENT24:M===Li?Z=i.DEPTH_COMPONENT32F:M===ma&&(Z=i.DEPTH_COMPONENT16),Z}function T(D,M){return p(D)===!0||D.isFramebufferTexture&&D.minFilter!==Xn&&D.minFilter!==ti?Math.log2(Math.max(M.width,M.height))+1:D.mipmaps!==void 0&&D.mipmaps.length>0?D.mipmaps.length:D.isCompressedTexture&&Array.isArray(D.image)?M.mipmaps.length:1}function z(D){const M=D.target;M.removeEventListener("dispose",z),L(M),M.isVideoTexture&&u.delete(M)}function R(D){const M=D.target;M.removeEventListener("dispose",R),w(M)}function L(D){const M=n.get(D);if(M.__webglInit===void 0)return;const Z=D.source,oe=d.get(Z);if(oe){const Q=oe[M.__cacheKey];Q.usedTimes--,Q.usedTimes===0&&O(D),Object.keys(oe).length===0&&d.delete(Z)}n.remove(D)}function O(D){const M=n.get(D);i.deleteTexture(M.__webglTexture);const Z=D.source,oe=d.get(Z);delete oe[M.__cacheKey],a.memory.textures--}function w(D){const M=n.get(D);if(D.depthTexture&&D.depthTexture.dispose(),D.isWebGLCubeRenderTarget)for(let oe=0;oe<6;oe++){if(Array.isArray(M.__webglFramebuffer[oe]))for(let Q=0;Q<M.__webglFramebuffer[oe].length;Q++)i.deleteFramebuffer(M.__webglFramebuffer[oe][Q]);else i.deleteFramebuffer(M.__webglFramebuffer[oe]);M.__webglDepthbuffer&&i.deleteRenderbuffer(M.__webglDepthbuffer[oe])}else{if(Array.isArray(M.__webglFramebuffer))for(let oe=0;oe<M.__webglFramebuffer.length;oe++)i.deleteFramebuffer(M.__webglFramebuffer[oe]);else i.deleteFramebuffer(M.__webglFramebuffer);if(M.__webglDepthbuffer&&i.deleteRenderbuffer(M.__webglDepthbuffer),M.__webglMultisampledFramebuffer&&i.deleteFramebuffer(M.__webglMultisampledFramebuffer),M.__webglColorRenderbuffer)for(let oe=0;oe<M.__webglColorRenderbuffer.length;oe++)M.__webglColorRenderbuffer[oe]&&i.deleteRenderbuffer(M.__webglColorRenderbuffer[oe]);M.__webglDepthRenderbuffer&&i.deleteRenderbuffer(M.__webglDepthRenderbuffer)}const Z=D.textures;for(let oe=0,Q=Z.length;oe<Q;oe++){const G=n.get(Z[oe]);G.__webglTexture&&(i.deleteTexture(G.__webglTexture),a.memory.textures--),n.remove(Z[oe])}n.remove(D)}let x=0;function C(){x=0}function j(){const D=x;return D>=r.maxTextures&&console.warn("THREE.WebGLTextures: Trying to use "+D+" texture units while this GPU supports only "+r.maxTextures),x+=1,D}function B(D){const M=[];return M.push(D.wrapS),M.push(D.wrapT),M.push(D.wrapR||0),M.push(D.magFilter),M.push(D.minFilter),M.push(D.anisotropy),M.push(D.internalFormat),M.push(D.format),M.push(D.type),M.push(D.generateMipmaps),M.push(D.premultiplyAlpha),M.push(D.flipY),M.push(D.unpackAlignment),M.push(D.colorSpace),M.join()}function K(D,M){const Z=n.get(D);if(D.isVideoTexture&&St(D),D.isRenderTargetTexture===!1&&D.version>0&&Z.__version!==D.version){const oe=D.image;if(oe===null)console.warn("THREE.WebGLRenderer: Texture marked for update but no image data found.");else if(oe.complete===!1)console.warn("THREE.WebGLRenderer: Texture marked for update but image is incomplete");else{xe(Z,D,M);return}}t.bindTexture(i.TEXTURE_2D,Z.__webglTexture,i.TEXTURE0+M)}function W(D,M){const Z=n.get(D);if(D.version>0&&Z.__version!==D.version){xe(Z,D,M);return}t.bindTexture(i.TEXTURE_2D_ARRAY,Z.__webglTexture,i.TEXTURE0+M)}function J(D,M){const Z=n.get(D);if(D.version>0&&Z.__version!==D.version){xe(Z,D,M);return}t.bindTexture(i.TEXTURE_3D,Z.__webglTexture,i.TEXTURE0+M)}function q(D,M){const Z=n.get(D);if(D.version>0&&Z.__version!==D.version){te(Z,D,M);return}t.bindTexture(i.TEXTURE_CUBE_MAP,Z.__webglTexture,i.TEXTURE0+M)}const ee={[Kl]:i.REPEAT,[Ar]:i.CLAMP_TO_EDGE,[Zl]:i.MIRRORED_REPEAT},me={[Xn]:i.NEAREST,[_m]:i.NEAREST_MIPMAP_NEAREST,[Pa]:i.NEAREST_MIPMAP_LINEAR,[ti]:i.LINEAR,[al]:i.LINEAR_MIPMAP_NEAREST,[Rr]:i.LINEAR_MIPMAP_LINEAR},he={[Mm]:i.NEVER,[Am]:i.ALWAYS,[Sm]:i.LESS,[sf]:i.LEQUAL,[Em]:i.EQUAL,[wm]:i.GEQUAL,[bm]:i.GREATER,[Tm]:i.NOTEQUAL};function ve(D,M){if(M.type===Li&&e.has("OES_texture_float_linear")===!1&&(M.magFilter===ti||M.magFilter===al||M.magFilter===Pa||M.magFilter===Rr||M.minFilter===ti||M.minFilter===al||M.minFilter===Pa||M.minFilter===Rr)&&console.warn("THREE.WebGLRenderer: Unable to use linear filtering with floating point textures. OES_texture_float_linear not supported on this device."),i.texParameteri(D,i.TEXTURE_WRAP_S,ee[M.wrapS]),i.texParameteri(D,i.TEXTURE_WRAP_T,ee[M.wrapT]),(D===i.TEXTURE_3D||D===i.TEXTURE_2D_ARRAY)&&i.texParameteri(D,i.TEXTURE_WRAP_R,ee[M.wrapR]),i.texParameteri(D,i.TEXTURE_MAG_FILTER,me[M.magFilter]),i.texParameteri(D,i.TEXTURE_MIN_FILTER,me[M.minFilter]),M.compareFunction&&(i.texParameteri(D,i.TEXTURE_COMPARE_MODE,i.COMPARE_REF_TO_TEXTURE),i.texParameteri(D,i.TEXTURE_COMPARE_FUNC,he[M.compareFunction])),e.has("EXT_texture_filter_anisotropic")===!0){if(M.magFilter===Xn||M.minFilter!==Pa&&M.minFilter!==Rr||M.type===Li&&e.has("OES_texture_float_linear")===!1)return;if(M.anisotropy>1||n.get(M).__currentAnisotropy){const Z=e.get("EXT_texture_filter_anisotropic");i.texParameterf(D,Z.TEXTURE_MAX_ANISOTROPY_EXT,Math.min(M.anisotropy,r.getMaxAnisotropy())),n.get(M).__currentAnisotropy=M.anisotropy}}}function Te(D,M){let Z=!1;D.__webglInit===void 0&&(D.__webglInit=!0,M.addEventListener("dispose",z));const oe=M.source;let Q=d.get(oe);Q===void 0&&(Q={},d.set(oe,Q));const G=B(M);if(G!==D.__cacheKey){Q[G]===void 0&&(Q[G]={texture:i.createTexture(),usedTimes:0},a.memory.textures++,Z=!0),Q[G].usedTimes++;const Ee=Q[D.__cacheKey];Ee!==void 0&&(Q[D.__cacheKey].usedTimes--,Ee.usedTimes===0&&O(M)),D.__cacheKey=G,D.__webglTexture=Q[G].texture}return Z}function xe(D,M,Z){let oe=i.TEXTURE_2D;(M.isDataArrayTexture||M.isCompressedArrayTexture)&&(oe=i.TEXTURE_2D_ARRAY),M.isData3DTexture&&(oe=i.TEXTURE_3D);const Q=Te(D,M),G=M.source;t.bindTexture(oe,D.__webglTexture,i.TEXTURE0+Z);const Ee=n.get(G);if(G.version!==Ee.__version||Q===!0){t.activeTexture(i.TEXTURE0+Z);const ge=Mt.getPrimaries(Mt.workingColorSpace),Ae=M.colorSpace===Ji?null:Mt.getPrimaries(M.colorSpace),je=M.colorSpace===Ji||ge===Ae?i.NONE:i.BROWSER_DEFAULT_WEBGL;i.pixelStorei(i.UNPACK_FLIP_Y_WEBGL,M.flipY),i.pixelStorei(i.UNPACK_PREMULTIPLY_ALPHA_WEBGL,M.premultiplyAlpha),i.pixelStorei(i.UNPACK_ALIGNMENT,M.unpackAlignment),i.pixelStorei(i.UNPACK_COLORSPACE_CONVERSION_WEBGL,je);let pe=v(M.image,!1,r.maxTextureSize);pe=qe(M,pe);const we=s.convert(M.format,M.colorSpace),Ke=s.convert(M.type);let ze=E(M.internalFormat,we,Ke,M.colorSpace,M.isVideoTexture);ve(oe,M);let Se;const ke=M.mipmaps,N=M.isVideoTexture!==!0,le=Ee.__version===void 0||Q===!0,I=G.dataReady,re=T(M,pe);if(M.isDepthTexture)ze=S(M.format===As,M.type),le&&(N?t.texStorage2D(i.TEXTURE_2D,1,ze,pe.width,pe.height):t.texImage2D(i.TEXTURE_2D,0,ze,pe.width,pe.height,0,we,Ke,null));else if(M.isDataTexture)if(ke.length>0){N&&le&&t.texStorage2D(i.TEXTURE_2D,re,ze,ke[0].width,ke[0].height);for(let ne=0,ie=ke.length;ne<ie;ne++)Se=ke[ne],N?I&&t.texSubImage2D(i.TEXTURE_2D,ne,0,0,Se.width,Se.height,we,Ke,Se.data):t.texImage2D(i.TEXTURE_2D,ne,ze,Se.width,Se.height,0,we,Ke,Se.data);M.generateMipmaps=!1}else N?(le&&t.texStorage2D(i.TEXTURE_2D,re,ze,pe.width,pe.height),I&&t.texSubImage2D(i.TEXTURE_2D,0,0,0,pe.width,pe.height,we,Ke,pe.data)):t.texImage2D(i.TEXTURE_2D,0,ze,pe.width,pe.height,0,we,Ke,pe.data);else if(M.isCompressedTexture)if(M.isCompressedArrayTexture){N&&le&&t.texStorage3D(i.TEXTURE_2D_ARRAY,re,ze,ke[0].width,ke[0].height,pe.depth);for(let ne=0,ie=ke.length;ne<ie;ne++)if(Se=ke[ne],M.format!==ri)if(we!==null)if(N){if(I)if(M.layerUpdates.size>0){const _e=Oh(Se.width,Se.height,M.format,M.type);for(const $e of M.layerUpdates){const st=Se.data.subarray($e*_e/Se.data.BYTES_PER_ELEMENT,($e+1)*_e/Se.data.BYTES_PER_ELEMENT);t.compressedTexSubImage3D(i.TEXTURE_2D_ARRAY,ne,0,0,$e,Se.width,Se.height,1,we,st,0,0)}M.clearLayerUpdates()}else t.compressedTexSubImage3D(i.TEXTURE_2D_ARRAY,ne,0,0,0,Se.width,Se.height,pe.depth,we,Se.data,0,0)}else t.compressedTexImage3D(i.TEXTURE_2D_ARRAY,ne,ze,Se.width,Se.height,pe.depth,0,Se.data,0,0);else console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()");else N?I&&t.texSubImage3D(i.TEXTURE_2D_ARRAY,ne,0,0,0,Se.width,Se.height,pe.depth,we,Ke,Se.data):t.texImage3D(i.TEXTURE_2D_ARRAY,ne,ze,Se.width,Se.height,pe.depth,0,we,Ke,Se.data)}else{N&&le&&t.texStorage2D(i.TEXTURE_2D,re,ze,ke[0].width,ke[0].height);for(let ne=0,ie=ke.length;ne<ie;ne++)Se=ke[ne],M.format!==ri?we!==null?N?I&&t.compressedTexSubImage2D(i.TEXTURE_2D,ne,0,0,Se.width,Se.height,we,Se.data):t.compressedTexImage2D(i.TEXTURE_2D,ne,ze,Se.width,Se.height,0,Se.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()"):N?I&&t.texSubImage2D(i.TEXTURE_2D,ne,0,0,Se.width,Se.height,we,Ke,Se.data):t.texImage2D(i.TEXTURE_2D,ne,ze,Se.width,Se.height,0,we,Ke,Se.data)}else if(M.isDataArrayTexture)if(N){if(le&&t.texStorage3D(i.TEXTURE_2D_ARRAY,re,ze,pe.width,pe.height,pe.depth),I)if(M.layerUpdates.size>0){const ne=Oh(pe.width,pe.height,M.format,M.type);for(const ie of M.layerUpdates){const _e=pe.data.subarray(ie*ne/pe.data.BYTES_PER_ELEMENT,(ie+1)*ne/pe.data.BYTES_PER_ELEMENT);t.texSubImage3D(i.TEXTURE_2D_ARRAY,0,0,0,ie,pe.width,pe.height,1,we,Ke,_e)}M.clearLayerUpdates()}else t.texSubImage3D(i.TEXTURE_2D_ARRAY,0,0,0,0,pe.width,pe.height,pe.depth,we,Ke,pe.data)}else t.texImage3D(i.TEXTURE_2D_ARRAY,0,ze,pe.width,pe.height,pe.depth,0,we,Ke,pe.data);else if(M.isData3DTexture)N?(le&&t.texStorage3D(i.TEXTURE_3D,re,ze,pe.width,pe.height,pe.depth),I&&t.texSubImage3D(i.TEXTURE_3D,0,0,0,0,pe.width,pe.height,pe.depth,we,Ke,pe.data)):t.texImage3D(i.TEXTURE_3D,0,ze,pe.width,pe.height,pe.depth,0,we,Ke,pe.data);else if(M.isFramebufferTexture){if(le)if(N)t.texStorage2D(i.TEXTURE_2D,re,ze,pe.width,pe.height);else{let ne=pe.width,ie=pe.height;for(let _e=0;_e<re;_e++)t.texImage2D(i.TEXTURE_2D,_e,ze,ne,ie,0,we,Ke,null),ne>>=1,ie>>=1}}else if(ke.length>0){if(N&&le){const ne=We(ke[0]);t.texStorage2D(i.TEXTURE_2D,re,ze,ne.width,ne.height)}for(let ne=0,ie=ke.length;ne<ie;ne++)Se=ke[ne],N?I&&t.texSubImage2D(i.TEXTURE_2D,ne,0,0,we,Ke,Se):t.texImage2D(i.TEXTURE_2D,ne,ze,we,Ke,Se);M.generateMipmaps=!1}else if(N){if(le){const ne=We(pe);t.texStorage2D(i.TEXTURE_2D,re,ze,ne.width,ne.height)}I&&t.texSubImage2D(i.TEXTURE_2D,0,0,0,we,Ke,pe)}else t.texImage2D(i.TEXTURE_2D,0,ze,we,Ke,pe);p(M)&&f(oe),Ee.__version=G.version,M.onUpdate&&M.onUpdate(M)}D.__version=M.version}function te(D,M,Z){if(M.image.length!==6)return;const oe=Te(D,M),Q=M.source;t.bindTexture(i.TEXTURE_CUBE_MAP,D.__webglTexture,i.TEXTURE0+Z);const G=n.get(Q);if(Q.version!==G.__version||oe===!0){t.activeTexture(i.TEXTURE0+Z);const Ee=Mt.getPrimaries(Mt.workingColorSpace),ge=M.colorSpace===Ji?null:Mt.getPrimaries(M.colorSpace),Ae=M.colorSpace===Ji||Ee===ge?i.NONE:i.BROWSER_DEFAULT_WEBGL;i.pixelStorei(i.UNPACK_FLIP_Y_WEBGL,M.flipY),i.pixelStorei(i.UNPACK_PREMULTIPLY_ALPHA_WEBGL,M.premultiplyAlpha),i.pixelStorei(i.UNPACK_ALIGNMENT,M.unpackAlignment),i.pixelStorei(i.UNPACK_COLORSPACE_CONVERSION_WEBGL,Ae);const je=M.isCompressedTexture||M.image[0].isCompressedTexture,pe=M.image[0]&&M.image[0].isDataTexture,we=[];for(let ie=0;ie<6;ie++)!je&&!pe?we[ie]=v(M.image[ie],!0,r.maxCubemapSize):we[ie]=pe?M.image[ie].image:M.image[ie],we[ie]=qe(M,we[ie]);const Ke=we[0],ze=s.convert(M.format,M.colorSpace),Se=s.convert(M.type),ke=E(M.internalFormat,ze,Se,M.colorSpace),N=M.isVideoTexture!==!0,le=G.__version===void 0||oe===!0,I=Q.dataReady;let re=T(M,Ke);ve(i.TEXTURE_CUBE_MAP,M);let ne;if(je){N&&le&&t.texStorage2D(i.TEXTURE_CUBE_MAP,re,ke,Ke.width,Ke.height);for(let ie=0;ie<6;ie++){ne=we[ie].mipmaps;for(let _e=0;_e<ne.length;_e++){const $e=ne[_e];M.format!==ri?ze!==null?N?I&&t.compressedTexSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+ie,_e,0,0,$e.width,$e.height,ze,$e.data):t.compressedTexImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+ie,_e,ke,$e.width,$e.height,0,$e.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .setTextureCube()"):N?I&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+ie,_e,0,0,$e.width,$e.height,ze,Se,$e.data):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+ie,_e,ke,$e.width,$e.height,0,ze,Se,$e.data)}}}else{if(ne=M.mipmaps,N&&le){ne.length>0&&re++;const ie=We(we[0]);t.texStorage2D(i.TEXTURE_CUBE_MAP,re,ke,ie.width,ie.height)}for(let ie=0;ie<6;ie++)if(pe){N?I&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+ie,0,0,0,we[ie].width,we[ie].height,ze,Se,we[ie].data):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+ie,0,ke,we[ie].width,we[ie].height,0,ze,Se,we[ie].data);for(let _e=0;_e<ne.length;_e++){const st=ne[_e].image[ie].image;N?I&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+ie,_e+1,0,0,st.width,st.height,ze,Se,st.data):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+ie,_e+1,ke,st.width,st.height,0,ze,Se,st.data)}}else{N?I&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+ie,0,0,0,ze,Se,we[ie]):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+ie,0,ke,ze,Se,we[ie]);for(let _e=0;_e<ne.length;_e++){const $e=ne[_e];N?I&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+ie,_e+1,0,0,ze,Se,$e.image[ie]):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+ie,_e+1,ke,ze,Se,$e.image[ie])}}}p(M)&&f(i.TEXTURE_CUBE_MAP),G.__version=Q.version,M.onUpdate&&M.onUpdate(M)}D.__version=M.version}function ce(D,M,Z,oe,Q,G){const Ee=s.convert(Z.format,Z.colorSpace),ge=s.convert(Z.type),Ae=E(Z.internalFormat,Ee,ge,Z.colorSpace);if(!n.get(M).__hasExternalTextures){const pe=Math.max(1,M.width>>G),we=Math.max(1,M.height>>G);Q===i.TEXTURE_3D||Q===i.TEXTURE_2D_ARRAY?t.texImage3D(Q,G,Ae,pe,we,M.depth,0,Ee,ge,null):t.texImage2D(Q,G,Ae,pe,we,0,Ee,ge,null)}t.bindFramebuffer(i.FRAMEBUFFER,D),Fe(M)?o.framebufferTexture2DMultisampleEXT(i.FRAMEBUFFER,oe,Q,n.get(Z).__webglTexture,0,ot(M)):(Q===i.TEXTURE_2D||Q>=i.TEXTURE_CUBE_MAP_POSITIVE_X&&Q<=i.TEXTURE_CUBE_MAP_NEGATIVE_Z)&&i.framebufferTexture2D(i.FRAMEBUFFER,oe,Q,n.get(Z).__webglTexture,G),t.bindFramebuffer(i.FRAMEBUFFER,null)}function ye(D,M,Z){if(i.bindRenderbuffer(i.RENDERBUFFER,D),M.depthBuffer){const oe=M.depthTexture,Q=oe&&oe.isDepthTexture?oe.type:null,G=S(M.stencilBuffer,Q),Ee=M.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,ge=ot(M);Fe(M)?o.renderbufferStorageMultisampleEXT(i.RENDERBUFFER,ge,G,M.width,M.height):Z?i.renderbufferStorageMultisample(i.RENDERBUFFER,ge,G,M.width,M.height):i.renderbufferStorage(i.RENDERBUFFER,G,M.width,M.height),i.framebufferRenderbuffer(i.FRAMEBUFFER,Ee,i.RENDERBUFFER,D)}else{const oe=M.textures;for(let Q=0;Q<oe.length;Q++){const G=oe[Q],Ee=s.convert(G.format,G.colorSpace),ge=s.convert(G.type),Ae=E(G.internalFormat,Ee,ge,G.colorSpace),je=ot(M);Z&&Fe(M)===!1?i.renderbufferStorageMultisample(i.RENDERBUFFER,je,Ae,M.width,M.height):Fe(M)?o.renderbufferStorageMultisampleEXT(i.RENDERBUFFER,je,Ae,M.width,M.height):i.renderbufferStorage(i.RENDERBUFFER,Ae,M.width,M.height)}}i.bindRenderbuffer(i.RENDERBUFFER,null)}function de(D,M){if(M&&M.isWebGLCubeRenderTarget)throw new Error("Depth Texture with cube render targets is not supported");if(t.bindFramebuffer(i.FRAMEBUFFER,D),!(M.depthTexture&&M.depthTexture.isDepthTexture))throw new Error("renderTarget.depthTexture must be an instance of THREE.DepthTexture");(!n.get(M.depthTexture).__webglTexture||M.depthTexture.image.width!==M.width||M.depthTexture.image.height!==M.height)&&(M.depthTexture.image.width=M.width,M.depthTexture.image.height=M.height,M.depthTexture.needsUpdate=!0),K(M.depthTexture,0);const oe=n.get(M.depthTexture).__webglTexture,Q=ot(M);if(M.depthTexture.format===vs)Fe(M)?o.framebufferTexture2DMultisampleEXT(i.FRAMEBUFFER,i.DEPTH_ATTACHMENT,i.TEXTURE_2D,oe,0,Q):i.framebufferTexture2D(i.FRAMEBUFFER,i.DEPTH_ATTACHMENT,i.TEXTURE_2D,oe,0);else if(M.depthTexture.format===As)Fe(M)?o.framebufferTexture2DMultisampleEXT(i.FRAMEBUFFER,i.DEPTH_STENCIL_ATTACHMENT,i.TEXTURE_2D,oe,0,Q):i.framebufferTexture2D(i.FRAMEBUFFER,i.DEPTH_STENCIL_ATTACHMENT,i.TEXTURE_2D,oe,0);else throw new Error("Unknown depthTexture format")}function Be(D){const M=n.get(D),Z=D.isWebGLCubeRenderTarget===!0;if(M.__boundDepthTexture!==D.depthTexture){const oe=D.depthTexture;if(M.__depthDisposeCallback&&M.__depthDisposeCallback(),oe){const Q=()=>{delete M.__boundDepthTexture,delete M.__depthDisposeCallback,oe.removeEventListener("dispose",Q)};oe.addEventListener("dispose",Q),M.__depthDisposeCallback=Q}M.__boundDepthTexture=oe}if(D.depthTexture&&!M.__autoAllocateDepthBuffer){if(Z)throw new Error("target.depthTexture not supported in Cube render targets");de(M.__webglFramebuffer,D)}else if(Z){M.__webglDepthbuffer=[];for(let oe=0;oe<6;oe++)if(t.bindFramebuffer(i.FRAMEBUFFER,M.__webglFramebuffer[oe]),M.__webglDepthbuffer[oe]===void 0)M.__webglDepthbuffer[oe]=i.createRenderbuffer(),ye(M.__webglDepthbuffer[oe],D,!1);else{const Q=D.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,G=M.__webglDepthbuffer[oe];i.bindRenderbuffer(i.RENDERBUFFER,G),i.framebufferRenderbuffer(i.FRAMEBUFFER,Q,i.RENDERBUFFER,G)}}else if(t.bindFramebuffer(i.FRAMEBUFFER,M.__webglFramebuffer),M.__webglDepthbuffer===void 0)M.__webglDepthbuffer=i.createRenderbuffer(),ye(M.__webglDepthbuffer,D,!1);else{const oe=D.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,Q=M.__webglDepthbuffer;i.bindRenderbuffer(i.RENDERBUFFER,Q),i.framebufferRenderbuffer(i.FRAMEBUFFER,oe,i.RENDERBUFFER,Q)}t.bindFramebuffer(i.FRAMEBUFFER,null)}function Ve(D,M,Z){const oe=n.get(D);M!==void 0&&ce(oe.__webglFramebuffer,D,D.texture,i.COLOR_ATTACHMENT0,i.TEXTURE_2D,0),Z!==void 0&&Be(D)}function Ne(D){const M=D.texture,Z=n.get(D),oe=n.get(M);D.addEventListener("dispose",R);const Q=D.textures,G=D.isWebGLCubeRenderTarget===!0,Ee=Q.length>1;if(Ee||(oe.__webglTexture===void 0&&(oe.__webglTexture=i.createTexture()),oe.__version=M.version,a.memory.textures++),G){Z.__webglFramebuffer=[];for(let ge=0;ge<6;ge++)if(M.mipmaps&&M.mipmaps.length>0){Z.__webglFramebuffer[ge]=[];for(let Ae=0;Ae<M.mipmaps.length;Ae++)Z.__webglFramebuffer[ge][Ae]=i.createFramebuffer()}else Z.__webglFramebuffer[ge]=i.createFramebuffer()}else{if(M.mipmaps&&M.mipmaps.length>0){Z.__webglFramebuffer=[];for(let ge=0;ge<M.mipmaps.length;ge++)Z.__webglFramebuffer[ge]=i.createFramebuffer()}else Z.__webglFramebuffer=i.createFramebuffer();if(Ee)for(let ge=0,Ae=Q.length;ge<Ae;ge++){const je=n.get(Q[ge]);je.__webglTexture===void 0&&(je.__webglTexture=i.createTexture(),a.memory.textures++)}if(D.samples>0&&Fe(D)===!1){Z.__webglMultisampledFramebuffer=i.createFramebuffer(),Z.__webglColorRenderbuffer=[],t.bindFramebuffer(i.FRAMEBUFFER,Z.__webglMultisampledFramebuffer);for(let ge=0;ge<Q.length;ge++){const Ae=Q[ge];Z.__webglColorRenderbuffer[ge]=i.createRenderbuffer(),i.bindRenderbuffer(i.RENDERBUFFER,Z.__webglColorRenderbuffer[ge]);const je=s.convert(Ae.format,Ae.colorSpace),pe=s.convert(Ae.type),we=E(Ae.internalFormat,je,pe,Ae.colorSpace,D.isXRRenderTarget===!0),Ke=ot(D);i.renderbufferStorageMultisample(i.RENDERBUFFER,Ke,we,D.width,D.height),i.framebufferRenderbuffer(i.FRAMEBUFFER,i.COLOR_ATTACHMENT0+ge,i.RENDERBUFFER,Z.__webglColorRenderbuffer[ge])}i.bindRenderbuffer(i.RENDERBUFFER,null),D.depthBuffer&&(Z.__webglDepthRenderbuffer=i.createRenderbuffer(),ye(Z.__webglDepthRenderbuffer,D,!0)),t.bindFramebuffer(i.FRAMEBUFFER,null)}}if(G){t.bindTexture(i.TEXTURE_CUBE_MAP,oe.__webglTexture),ve(i.TEXTURE_CUBE_MAP,M);for(let ge=0;ge<6;ge++)if(M.mipmaps&&M.mipmaps.length>0)for(let Ae=0;Ae<M.mipmaps.length;Ae++)ce(Z.__webglFramebuffer[ge][Ae],D,M,i.COLOR_ATTACHMENT0,i.TEXTURE_CUBE_MAP_POSITIVE_X+ge,Ae);else ce(Z.__webglFramebuffer[ge],D,M,i.COLOR_ATTACHMENT0,i.TEXTURE_CUBE_MAP_POSITIVE_X+ge,0);p(M)&&f(i.TEXTURE_CUBE_MAP),t.unbindTexture()}else if(Ee){for(let ge=0,Ae=Q.length;ge<Ae;ge++){const je=Q[ge],pe=n.get(je);t.bindTexture(i.TEXTURE_2D,pe.__webglTexture),ve(i.TEXTURE_2D,je),ce(Z.__webglFramebuffer,D,je,i.COLOR_ATTACHMENT0+ge,i.TEXTURE_2D,0),p(je)&&f(i.TEXTURE_2D)}t.unbindTexture()}else{let ge=i.TEXTURE_2D;if((D.isWebGL3DRenderTarget||D.isWebGLArrayRenderTarget)&&(ge=D.isWebGL3DRenderTarget?i.TEXTURE_3D:i.TEXTURE_2D_ARRAY),t.bindTexture(ge,oe.__webglTexture),ve(ge,M),M.mipmaps&&M.mipmaps.length>0)for(let Ae=0;Ae<M.mipmaps.length;Ae++)ce(Z.__webglFramebuffer[Ae],D,M,i.COLOR_ATTACHMENT0,ge,Ae);else ce(Z.__webglFramebuffer,D,M,i.COLOR_ATTACHMENT0,ge,0);p(M)&&f(ge),t.unbindTexture()}D.depthBuffer&&Be(D)}function dt(D){const M=D.textures;for(let Z=0,oe=M.length;Z<oe;Z++){const Q=M[Z];if(p(Q)){const G=D.isWebGLCubeRenderTarget?i.TEXTURE_CUBE_MAP:i.TEXTURE_2D,Ee=n.get(Q).__webglTexture;t.bindTexture(G,Ee),f(G),t.unbindTexture()}}}const U=[],ut=[];function nt(D){if(D.samples>0){if(Fe(D)===!1){const M=D.textures,Z=D.width,oe=D.height;let Q=i.COLOR_BUFFER_BIT;const G=D.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,Ee=n.get(D),ge=M.length>1;if(ge)for(let Ae=0;Ae<M.length;Ae++)t.bindFramebuffer(i.FRAMEBUFFER,Ee.__webglMultisampledFramebuffer),i.framebufferRenderbuffer(i.FRAMEBUFFER,i.COLOR_ATTACHMENT0+Ae,i.RENDERBUFFER,null),t.bindFramebuffer(i.FRAMEBUFFER,Ee.__webglFramebuffer),i.framebufferTexture2D(i.DRAW_FRAMEBUFFER,i.COLOR_ATTACHMENT0+Ae,i.TEXTURE_2D,null,0);t.bindFramebuffer(i.READ_FRAMEBUFFER,Ee.__webglMultisampledFramebuffer),t.bindFramebuffer(i.DRAW_FRAMEBUFFER,Ee.__webglFramebuffer);for(let Ae=0;Ae<M.length;Ae++){if(D.resolveDepthBuffer&&(D.depthBuffer&&(Q|=i.DEPTH_BUFFER_BIT),D.stencilBuffer&&D.resolveStencilBuffer&&(Q|=i.STENCIL_BUFFER_BIT)),ge){i.framebufferRenderbuffer(i.READ_FRAMEBUFFER,i.COLOR_ATTACHMENT0,i.RENDERBUFFER,Ee.__webglColorRenderbuffer[Ae]);const je=n.get(M[Ae]).__webglTexture;i.framebufferTexture2D(i.DRAW_FRAMEBUFFER,i.COLOR_ATTACHMENT0,i.TEXTURE_2D,je,0)}i.blitFramebuffer(0,0,Z,oe,0,0,Z,oe,Q,i.NEAREST),l===!0&&(U.length=0,ut.length=0,U.push(i.COLOR_ATTACHMENT0+Ae),D.depthBuffer&&D.resolveDepthBuffer===!1&&(U.push(G),ut.push(G),i.invalidateFramebuffer(i.DRAW_FRAMEBUFFER,ut)),i.invalidateFramebuffer(i.READ_FRAMEBUFFER,U))}if(t.bindFramebuffer(i.READ_FRAMEBUFFER,null),t.bindFramebuffer(i.DRAW_FRAMEBUFFER,null),ge)for(let Ae=0;Ae<M.length;Ae++){t.bindFramebuffer(i.FRAMEBUFFER,Ee.__webglMultisampledFramebuffer),i.framebufferRenderbuffer(i.FRAMEBUFFER,i.COLOR_ATTACHMENT0+Ae,i.RENDERBUFFER,Ee.__webglColorRenderbuffer[Ae]);const je=n.get(M[Ae]).__webglTexture;t.bindFramebuffer(i.FRAMEBUFFER,Ee.__webglFramebuffer),i.framebufferTexture2D(i.DRAW_FRAMEBUFFER,i.COLOR_ATTACHMENT0+Ae,i.TEXTURE_2D,je,0)}t.bindFramebuffer(i.DRAW_FRAMEBUFFER,Ee.__webglMultisampledFramebuffer)}else if(D.depthBuffer&&D.resolveDepthBuffer===!1&&l){const M=D.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT;i.invalidateFramebuffer(i.DRAW_FRAMEBUFFER,[M])}}}function ot(D){return Math.min(r.maxSamples,D.samples)}function Fe(D){const M=n.get(D);return D.samples>0&&e.has("WEBGL_multisampled_render_to_texture")===!0&&M.__useRenderToTexture!==!1}function St(D){const M=a.render.frame;u.get(D)!==M&&(u.set(D,M),D.update())}function qe(D,M){const Z=D.colorSpace,oe=D.format,Q=D.type;return D.isCompressedTexture===!0||D.isVideoTexture===!0||Z!==lr&&Z!==Ji&&(Mt.getTransfer(Z)===Nt?(oe!==ri||Q!==Oi)&&console.warn("THREE.WebGLTextures: sRGB encoded textures have to use RGBAFormat and UnsignedByteType."):console.error("THREE.WebGLTextures: Unsupported texture color space:",Z)),M}function We(D){return typeof HTMLImageElement<"u"&&D instanceof HTMLImageElement?(c.width=D.naturalWidth||D.width,c.height=D.naturalHeight||D.height):typeof VideoFrame<"u"&&D instanceof VideoFrame?(c.width=D.displayWidth,c.height=D.displayHeight):(c.width=D.width,c.height=D.height),c}this.allocateTextureUnit=j,this.resetTextureUnits=C,this.setTexture2D=K,this.setTexture2DArray=W,this.setTexture3D=J,this.setTextureCube=q,this.rebindTextures=Ve,this.setupRenderTarget=Ne,this.updateRenderTargetMipmap=dt,this.updateMultisampleRenderTarget=nt,this.setupDepthRenderbuffer=Be,this.setupFrameBufferTexture=ce,this.useMultisampledRTT=Fe}function Wx(i,e){function t(n,r=Ji){let s;const a=Mt.getTransfer(r);if(n===Oi)return i.UNSIGNED_BYTE;if(n===Gc)return i.UNSIGNED_SHORT_4_4_4_4;if(n===Wc)return i.UNSIGNED_SHORT_5_5_5_1;if(n===jd)return i.UNSIGNED_INT_5_9_9_9_REV;if(n===Yd)return i.BYTE;if(n===$d)return i.SHORT;if(n===ma)return i.UNSIGNED_SHORT;if(n===Vc)return i.INT;if(n===Pr)return i.UNSIGNED_INT;if(n===Li)return i.FLOAT;if(n===va)return i.HALF_FLOAT;if(n===Kd)return i.ALPHA;if(n===Zd)return i.RGB;if(n===ri)return i.RGBA;if(n===Jd)return i.LUMINANCE;if(n===Qd)return i.LUMINANCE_ALPHA;if(n===vs)return i.DEPTH_COMPONENT;if(n===As)return i.DEPTH_STENCIL;if(n===ef)return i.RED;if(n===Xc)return i.RED_INTEGER;if(n===tf)return i.RG;if(n===qc)return i.RG_INTEGER;if(n===Yc)return i.RGBA_INTEGER;if(n===po||n===mo||n===go||n===_o)if(a===Nt)if(s=e.get("WEBGL_compressed_texture_s3tc_srgb"),s!==null){if(n===po)return s.COMPRESSED_SRGB_S3TC_DXT1_EXT;if(n===mo)return s.COMPRESSED_SRGB_ALPHA_S3TC_DXT1_EXT;if(n===go)return s.COMPRESSED_SRGB_ALPHA_S3TC_DXT3_EXT;if(n===_o)return s.COMPRESSED_SRGB_ALPHA_S3TC_DXT5_EXT}else return null;else if(s=e.get("WEBGL_compressed_texture_s3tc"),s!==null){if(n===po)return s.COMPRESSED_RGB_S3TC_DXT1_EXT;if(n===mo)return s.COMPRESSED_RGBA_S3TC_DXT1_EXT;if(n===go)return s.COMPRESSED_RGBA_S3TC_DXT3_EXT;if(n===_o)return s.COMPRESSED_RGBA_S3TC_DXT5_EXT}else return null;if(n===Jl||n===Ql||n===ec||n===tc)if(s=e.get("WEBGL_compressed_texture_pvrtc"),s!==null){if(n===Jl)return s.COMPRESSED_RGB_PVRTC_4BPPV1_IMG;if(n===Ql)return s.COMPRESSED_RGB_PVRTC_2BPPV1_IMG;if(n===ec)return s.COMPRESSED_RGBA_PVRTC_4BPPV1_IMG;if(n===tc)return s.COMPRESSED_RGBA_PVRTC_2BPPV1_IMG}else return null;if(n===nc||n===ic||n===rc)if(s=e.get("WEBGL_compressed_texture_etc"),s!==null){if(n===nc||n===ic)return a===Nt?s.COMPRESSED_SRGB8_ETC2:s.COMPRESSED_RGB8_ETC2;if(n===rc)return a===Nt?s.COMPRESSED_SRGB8_ALPHA8_ETC2_EAC:s.COMPRESSED_RGBA8_ETC2_EAC}else return null;if(n===sc||n===ac||n===oc||n===lc||n===cc||n===uc||n===hc||n===dc||n===fc||n===pc||n===mc||n===gc||n===_c||n===vc)if(s=e.get("WEBGL_compressed_texture_astc"),s!==null){if(n===sc)return a===Nt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_4x4_KHR:s.COMPRESSED_RGBA_ASTC_4x4_KHR;if(n===ac)return a===Nt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_5x4_KHR:s.COMPRESSED_RGBA_ASTC_5x4_KHR;if(n===oc)return a===Nt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_5x5_KHR:s.COMPRESSED_RGBA_ASTC_5x5_KHR;if(n===lc)return a===Nt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_6x5_KHR:s.COMPRESSED_RGBA_ASTC_6x5_KHR;if(n===cc)return a===Nt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_6x6_KHR:s.COMPRESSED_RGBA_ASTC_6x6_KHR;if(n===uc)return a===Nt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_8x5_KHR:s.COMPRESSED_RGBA_ASTC_8x5_KHR;if(n===hc)return a===Nt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_8x6_KHR:s.COMPRESSED_RGBA_ASTC_8x6_KHR;if(n===dc)return a===Nt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_8x8_KHR:s.COMPRESSED_RGBA_ASTC_8x8_KHR;if(n===fc)return a===Nt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_10x5_KHR:s.COMPRESSED_RGBA_ASTC_10x5_KHR;if(n===pc)return a===Nt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_10x6_KHR:s.COMPRESSED_RGBA_ASTC_10x6_KHR;if(n===mc)return a===Nt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_10x8_KHR:s.COMPRESSED_RGBA_ASTC_10x8_KHR;if(n===gc)return a===Nt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_10x10_KHR:s.COMPRESSED_RGBA_ASTC_10x10_KHR;if(n===_c)return a===Nt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_12x10_KHR:s.COMPRESSED_RGBA_ASTC_12x10_KHR;if(n===vc)return a===Nt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_12x12_KHR:s.COMPRESSED_RGBA_ASTC_12x12_KHR}else return null;if(n===vo||n===xc||n===yc)if(s=e.get("EXT_texture_compression_bptc"),s!==null){if(n===vo)return a===Nt?s.COMPRESSED_SRGB_ALPHA_BPTC_UNORM_EXT:s.COMPRESSED_RGBA_BPTC_UNORM_EXT;if(n===xc)return s.COMPRESSED_RGB_BPTC_SIGNED_FLOAT_EXT;if(n===yc)return s.COMPRESSED_RGB_BPTC_UNSIGNED_FLOAT_EXT}else return null;if(n===nf||n===Mc||n===Sc||n===Ec)if(s=e.get("EXT_texture_compression_rgtc"),s!==null){if(n===vo)return s.COMPRESSED_RED_RGTC1_EXT;if(n===Mc)return s.COMPRESSED_SIGNED_RED_RGTC1_EXT;if(n===Sc)return s.COMPRESSED_RED_GREEN_RGTC2_EXT;if(n===Ec)return s.COMPRESSED_SIGNED_RED_GREEN_RGTC2_EXT}else return null;return n===ws?i.UNSIGNED_INT_24_8:i[n]!==void 0?i[n]:null}return{convert:t}}class Xx extends _n{constructor(e=[]){super(),this.isArrayCamera=!0,this.cameras=e}}class Ja extends $t{constructor(){super(),this.isGroup=!0,this.type="Group"}}const qx={type:"move"};class Ll{constructor(){this._targetRay=null,this._grip=null,this._hand=null}getHandSpace(){return this._hand===null&&(this._hand=new Ja,this._hand.matrixAutoUpdate=!1,this._hand.visible=!1,this._hand.joints={},this._hand.inputState={pinching:!1}),this._hand}getTargetRaySpace(){return this._targetRay===null&&(this._targetRay=new Ja,this._targetRay.matrixAutoUpdate=!1,this._targetRay.visible=!1,this._targetRay.hasLinearVelocity=!1,this._targetRay.linearVelocity=new H,this._targetRay.hasAngularVelocity=!1,this._targetRay.angularVelocity=new H),this._targetRay}getGripSpace(){return this._grip===null&&(this._grip=new Ja,this._grip.matrixAutoUpdate=!1,this._grip.visible=!1,this._grip.hasLinearVelocity=!1,this._grip.linearVelocity=new H,this._grip.hasAngularVelocity=!1,this._grip.angularVelocity=new H),this._grip}dispatchEvent(e){return this._targetRay!==null&&this._targetRay.dispatchEvent(e),this._grip!==null&&this._grip.dispatchEvent(e),this._hand!==null&&this._hand.dispatchEvent(e),this}connect(e){if(e&&e.hand){const t=this._hand;if(t)for(const n of e.hand.values())this._getHandJoint(t,n)}return this.dispatchEvent({type:"connected",data:e}),this}disconnect(e){return this.dispatchEvent({type:"disconnected",data:e}),this._targetRay!==null&&(this._targetRay.visible=!1),this._grip!==null&&(this._grip.visible=!1),this._hand!==null&&(this._hand.visible=!1),this}update(e,t,n){let r=null,s=null,a=null;const o=this._targetRay,l=this._grip,c=this._hand;if(e&&t.session.visibilityState!=="visible-blurred"){if(c&&e.hand){a=!0;for(const v of e.hand.values()){const p=t.getJointPose(v,n),f=this._getHandJoint(c,v);p!==null&&(f.matrix.fromArray(p.transform.matrix),f.matrix.decompose(f.position,f.rotation,f.scale),f.matrixWorldNeedsUpdate=!0,f.jointRadius=p.radius),f.visible=p!==null}const u=c.joints["index-finger-tip"],h=c.joints["thumb-tip"],d=u.position.distanceTo(h.position),m=.02,_=.005;c.inputState.pinching&&d>m+_?(c.inputState.pinching=!1,this.dispatchEvent({type:"pinchend",handedness:e.handedness,target:this})):!c.inputState.pinching&&d<=m-_&&(c.inputState.pinching=!0,this.dispatchEvent({type:"pinchstart",handedness:e.handedness,target:this}))}else l!==null&&e.gripSpace&&(s=t.getPose(e.gripSpace,n),s!==null&&(l.matrix.fromArray(s.transform.matrix),l.matrix.decompose(l.position,l.rotation,l.scale),l.matrixWorldNeedsUpdate=!0,s.linearVelocity?(l.hasLinearVelocity=!0,l.linearVelocity.copy(s.linearVelocity)):l.hasLinearVelocity=!1,s.angularVelocity?(l.hasAngularVelocity=!0,l.angularVelocity.copy(s.angularVelocity)):l.hasAngularVelocity=!1));o!==null&&(r=t.getPose(e.targetRaySpace,n),r===null&&s!==null&&(r=s),r!==null&&(o.matrix.fromArray(r.transform.matrix),o.matrix.decompose(o.position,o.rotation,o.scale),o.matrixWorldNeedsUpdate=!0,r.linearVelocity?(o.hasLinearVelocity=!0,o.linearVelocity.copy(r.linearVelocity)):o.hasLinearVelocity=!1,r.angularVelocity?(o.hasAngularVelocity=!0,o.angularVelocity.copy(r.angularVelocity)):o.hasAngularVelocity=!1,this.dispatchEvent(qx)))}return o!==null&&(o.visible=r!==null),l!==null&&(l.visible=s!==null),c!==null&&(c.visible=a!==null),this}_getHandJoint(e,t){if(e.joints[t.jointName]===void 0){const n=new Ja;n.matrixAutoUpdate=!1,n.visible=!1,e.joints[t.jointName]=n,e.add(n)}return e.joints[t.jointName]}}const Yx=`
void main() {

	gl_Position = vec4( position, 1.0 );

}`,$x=`
uniform sampler2DArray depthColor;
uniform float depthWidth;
uniform float depthHeight;

void main() {

	vec2 coord = vec2( gl_FragCoord.x / depthWidth, gl_FragCoord.y / depthHeight );

	if ( coord.x >= 1.0 ) {

		gl_FragDepth = texture( depthColor, vec3( coord.x - 1.0, coord.y, 1 ) ).r;

	} else {

		gl_FragDepth = texture( depthColor, vec3( coord.x, coord.y, 0 ) ).r;

	}

}`;class jx{constructor(){this.texture=null,this.mesh=null,this.depthNear=0,this.depthFar=0}init(e,t,n){if(this.texture===null){const r=new An,s=e.properties.get(r);s.__webglTexture=t.texture,(t.depthNear!=n.depthNear||t.depthFar!=n.depthFar)&&(this.depthNear=t.depthNear,this.depthFar=t.depthFar),this.texture=r}}getMesh(e){if(this.texture!==null&&this.mesh===null){const t=e.cameras[0].viewport,n=new rr({vertexShader:Yx,fragmentShader:$x,uniforms:{depthColor:{value:this.texture},depthWidth:{value:t.z},depthHeight:{value:t.w}}});this.mesh=new Tn(new No(20,20),n)}return this.mesh}reset(){this.texture=null,this.mesh=null}getDepthTexture(){return this.texture}}class Kx extends Us{constructor(e,t){super();const n=this;let r=null,s=1,a=null,o="local-floor",l=1,c=null,u=null,h=null,d=null,m=null,_=null;const v=new jx,p=t.getContextAttributes();let f=null,E=null;const S=[],T=[],z=new Xe;let R=null;const L=new _n;L.layers.enable(1),L.viewport=new Zt;const O=new _n;O.layers.enable(2),O.viewport=new Zt;const w=[L,O],x=new Xx;x.layers.enable(1),x.layers.enable(2);let C=null,j=null;this.cameraAutoUpdate=!0,this.enabled=!1,this.isPresenting=!1,this.getController=function(te){let ce=S[te];return ce===void 0&&(ce=new Ll,S[te]=ce),ce.getTargetRaySpace()},this.getControllerGrip=function(te){let ce=S[te];return ce===void 0&&(ce=new Ll,S[te]=ce),ce.getGripSpace()},this.getHand=function(te){let ce=S[te];return ce===void 0&&(ce=new Ll,S[te]=ce),ce.getHandSpace()};function B(te){const ce=T.indexOf(te.inputSource);if(ce===-1)return;const ye=S[ce];ye!==void 0&&(ye.update(te.inputSource,te.frame,c||a),ye.dispatchEvent({type:te.type,data:te.inputSource}))}function K(){r.removeEventListener("select",B),r.removeEventListener("selectstart",B),r.removeEventListener("selectend",B),r.removeEventListener("squeeze",B),r.removeEventListener("squeezestart",B),r.removeEventListener("squeezeend",B),r.removeEventListener("end",K),r.removeEventListener("inputsourceschange",W);for(let te=0;te<S.length;te++){const ce=T[te];ce!==null&&(T[te]=null,S[te].disconnect(ce))}C=null,j=null,v.reset(),e.setRenderTarget(f),m=null,d=null,h=null,r=null,E=null,xe.stop(),n.isPresenting=!1,e.setPixelRatio(R),e.setSize(z.width,z.height,!1),n.dispatchEvent({type:"sessionend"})}this.setFramebufferScaleFactor=function(te){s=te,n.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change framebuffer scale while presenting.")},this.setReferenceSpaceType=function(te){o=te,n.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change reference space type while presenting.")},this.getReferenceSpace=function(){return c||a},this.setReferenceSpace=function(te){c=te},this.getBaseLayer=function(){return d!==null?d:m},this.getBinding=function(){return h},this.getFrame=function(){return _},this.getSession=function(){return r},this.setSession=async function(te){if(r=te,r!==null){if(f=e.getRenderTarget(),r.addEventListener("select",B),r.addEventListener("selectstart",B),r.addEventListener("selectend",B),r.addEventListener("squeeze",B),r.addEventListener("squeezestart",B),r.addEventListener("squeezeend",B),r.addEventListener("end",K),r.addEventListener("inputsourceschange",W),p.xrCompatible!==!0&&await t.makeXRCompatible(),R=e.getPixelRatio(),e.getSize(z),r.renderState.layers===void 0){const ce={antialias:p.antialias,alpha:!0,depth:p.depth,stencil:p.stencil,framebufferScaleFactor:s};m=new XRWebGLLayer(r,t,ce),r.updateRenderState({baseLayer:m}),e.setPixelRatio(1),e.setSize(m.framebufferWidth,m.framebufferHeight,!1),E=new Lr(m.framebufferWidth,m.framebufferHeight,{format:ri,type:Oi,colorSpace:e.outputColorSpace,stencilBuffer:p.stencil})}else{let ce=null,ye=null,de=null;p.depth&&(de=p.stencil?t.DEPTH24_STENCIL8:t.DEPTH_COMPONENT24,ce=p.stencil?As:vs,ye=p.stencil?ws:Pr);const Be={colorFormat:t.RGBA8,depthFormat:de,scaleFactor:s};h=new XRWebGLBinding(r,t),d=h.createProjectionLayer(Be),r.updateRenderState({layers:[d]}),e.setPixelRatio(1),e.setSize(d.textureWidth,d.textureHeight,!1),E=new Lr(d.textureWidth,d.textureHeight,{format:ri,type:Oi,depthTexture:new gf(d.textureWidth,d.textureHeight,ye,void 0,void 0,void 0,void 0,void 0,void 0,ce),stencilBuffer:p.stencil,colorSpace:e.outputColorSpace,samples:p.antialias?4:0,resolveDepthBuffer:d.ignoreDepthValues===!1})}E.isXRRenderTarget=!0,this.setFoveation(l),c=null,a=await r.requestReferenceSpace(o),xe.setContext(r),xe.start(),n.isPresenting=!0,n.dispatchEvent({type:"sessionstart"})}},this.getEnvironmentBlendMode=function(){if(r!==null)return r.environmentBlendMode},this.getDepthTexture=function(){return v.getDepthTexture()};function W(te){for(let ce=0;ce<te.removed.length;ce++){const ye=te.removed[ce],de=T.indexOf(ye);de>=0&&(T[de]=null,S[de].disconnect(ye))}for(let ce=0;ce<te.added.length;ce++){const ye=te.added[ce];let de=T.indexOf(ye);if(de===-1){for(let Ve=0;Ve<S.length;Ve++)if(Ve>=T.length){T.push(ye),de=Ve;break}else if(T[Ve]===null){T[Ve]=ye,de=Ve;break}if(de===-1)break}const Be=S[de];Be&&Be.connect(ye)}}const J=new H,q=new H;function ee(te,ce,ye){J.setFromMatrixPosition(ce.matrixWorld),q.setFromMatrixPosition(ye.matrixWorld);const de=J.distanceTo(q),Be=ce.projectionMatrix.elements,Ve=ye.projectionMatrix.elements,Ne=Be[14]/(Be[10]-1),dt=Be[14]/(Be[10]+1),U=(Be[9]+1)/Be[5],ut=(Be[9]-1)/Be[5],nt=(Be[8]-1)/Be[0],ot=(Ve[8]+1)/Ve[0],Fe=Ne*nt,St=Ne*ot,qe=de/(-nt+ot),We=qe*-nt;if(ce.matrixWorld.decompose(te.position,te.quaternion,te.scale),te.translateX(We),te.translateZ(qe),te.matrixWorld.compose(te.position,te.quaternion,te.scale),te.matrixWorldInverse.copy(te.matrixWorld).invert(),Be[10]===-1)te.projectionMatrix.copy(ce.projectionMatrix),te.projectionMatrixInverse.copy(ce.projectionMatrixInverse);else{const D=Ne+qe,M=dt+qe,Z=Fe-We,oe=St+(de-We),Q=U*dt/M*D,G=ut*dt/M*D;te.projectionMatrix.makePerspective(Z,oe,Q,G,D,M),te.projectionMatrixInverse.copy(te.projectionMatrix).invert()}}function me(te,ce){ce===null?te.matrixWorld.copy(te.matrix):te.matrixWorld.multiplyMatrices(ce.matrixWorld,te.matrix),te.matrixWorldInverse.copy(te.matrixWorld).invert()}this.updateCamera=function(te){if(r===null)return;let ce=te.near,ye=te.far;v.texture!==null&&(v.depthNear>0&&(ce=v.depthNear),v.depthFar>0&&(ye=v.depthFar)),x.near=O.near=L.near=ce,x.far=O.far=L.far=ye,(C!==x.near||j!==x.far)&&(r.updateRenderState({depthNear:x.near,depthFar:x.far}),C=x.near,j=x.far);const de=te.parent,Be=x.cameras;me(x,de);for(let Ve=0;Ve<Be.length;Ve++)me(Be[Ve],de);Be.length===2?ee(x,L,O):x.projectionMatrix.copy(L.projectionMatrix),he(te,x,de)};function he(te,ce,ye){ye===null?te.matrix.copy(ce.matrixWorld):(te.matrix.copy(ye.matrixWorld),te.matrix.invert(),te.matrix.multiply(ce.matrixWorld)),te.matrix.decompose(te.position,te.quaternion,te.scale),te.updateMatrixWorld(!0),te.projectionMatrix.copy(ce.projectionMatrix),te.projectionMatrixInverse.copy(ce.projectionMatrixInverse),te.isPerspectiveCamera&&(te.fov=ga*2*Math.atan(1/te.projectionMatrix.elements[5]),te.zoom=1)}this.getCamera=function(){return x},this.getFoveation=function(){if(!(d===null&&m===null))return l},this.setFoveation=function(te){l=te,d!==null&&(d.fixedFoveation=te),m!==null&&m.fixedFoveation!==void 0&&(m.fixedFoveation=te)},this.hasDepthSensing=function(){return v.texture!==null},this.getDepthSensingMesh=function(){return v.getMesh(x)};let ve=null;function Te(te,ce){if(u=ce.getViewerPose(c||a),_=ce,u!==null){const ye=u.views;m!==null&&(e.setRenderTargetFramebuffer(E,m.framebuffer),e.setRenderTarget(E));let de=!1;ye.length!==x.cameras.length&&(x.cameras.length=0,de=!0);for(let Ve=0;Ve<ye.length;Ve++){const Ne=ye[Ve];let dt=null;if(m!==null)dt=m.getViewport(Ne);else{const ut=h.getViewSubImage(d,Ne);dt=ut.viewport,Ve===0&&(e.setRenderTargetTextures(E,ut.colorTexture,d.ignoreDepthValues?void 0:ut.depthStencilTexture),e.setRenderTarget(E))}let U=w[Ve];U===void 0&&(U=new _n,U.layers.enable(Ve),U.viewport=new Zt,w[Ve]=U),U.matrix.fromArray(Ne.transform.matrix),U.matrix.decompose(U.position,U.quaternion,U.scale),U.projectionMatrix.fromArray(Ne.projectionMatrix),U.projectionMatrixInverse.copy(U.projectionMatrix).invert(),U.viewport.set(dt.x,dt.y,dt.width,dt.height),Ve===0&&(x.matrix.copy(U.matrix),x.matrix.decompose(x.position,x.quaternion,x.scale)),de===!0&&x.cameras.push(U)}const Be=r.enabledFeatures;if(Be&&Be.includes("depth-sensing")){const Ve=h.getDepthInformation(ye[0]);Ve&&Ve.isValid&&Ve.texture&&v.init(e,Ve,r.renderState)}}for(let ye=0;ye<S.length;ye++){const de=T[ye],Be=S[ye];de!==null&&Be!==void 0&&Be.update(de,ce,c||a)}ve&&ve(te,ce),ce.detectedPlanes&&n.dispatchEvent({type:"planesdetected",data:ce}),_=null}const xe=new mf;xe.setAnimationLoop(Te),this.setAnimationLoop=function(te){ve=te},this.dispose=function(){}}}const yr=new _i,Zx=new Ft;function Jx(i,e){function t(p,f){p.matrixAutoUpdate===!0&&p.updateMatrix(),f.value.copy(p.matrix)}function n(p,f){f.color.getRGB(p.fogColor.value,df(i)),f.isFog?(p.fogNear.value=f.near,p.fogFar.value=f.far):f.isFogExp2&&(p.fogDensity.value=f.density)}function r(p,f,E,S,T){f.isMeshBasicMaterial||f.isMeshLambertMaterial?s(p,f):f.isMeshToonMaterial?(s(p,f),h(p,f)):f.isMeshPhongMaterial?(s(p,f),u(p,f)):f.isMeshStandardMaterial?(s(p,f),d(p,f),f.isMeshPhysicalMaterial&&m(p,f,T)):f.isMeshMatcapMaterial?(s(p,f),_(p,f)):f.isMeshDepthMaterial?s(p,f):f.isMeshDistanceMaterial?(s(p,f),v(p,f)):f.isMeshNormalMaterial?s(p,f):f.isLineBasicMaterial?(a(p,f),f.isLineDashedMaterial&&o(p,f)):f.isPointsMaterial?l(p,f,E,S):f.isSpriteMaterial?c(p,f):f.isShadowMaterial?(p.color.value.copy(f.color),p.opacity.value=f.opacity):f.isShaderMaterial&&(f.uniformsNeedUpdate=!1)}function s(p,f){p.opacity.value=f.opacity,f.color&&p.diffuse.value.copy(f.color),f.emissive&&p.emissive.value.copy(f.emissive).multiplyScalar(f.emissiveIntensity),f.map&&(p.map.value=f.map,t(f.map,p.mapTransform)),f.alphaMap&&(p.alphaMap.value=f.alphaMap,t(f.alphaMap,p.alphaMapTransform)),f.bumpMap&&(p.bumpMap.value=f.bumpMap,t(f.bumpMap,p.bumpMapTransform),p.bumpScale.value=f.bumpScale,f.side===Cn&&(p.bumpScale.value*=-1)),f.normalMap&&(p.normalMap.value=f.normalMap,t(f.normalMap,p.normalMapTransform),p.normalScale.value.copy(f.normalScale),f.side===Cn&&p.normalScale.value.negate()),f.displacementMap&&(p.displacementMap.value=f.displacementMap,t(f.displacementMap,p.displacementMapTransform),p.displacementScale.value=f.displacementScale,p.displacementBias.value=f.displacementBias),f.emissiveMap&&(p.emissiveMap.value=f.emissiveMap,t(f.emissiveMap,p.emissiveMapTransform)),f.specularMap&&(p.specularMap.value=f.specularMap,t(f.specularMap,p.specularMapTransform)),f.alphaTest>0&&(p.alphaTest.value=f.alphaTest);const E=e.get(f),S=E.envMap,T=E.envMapRotation;S&&(p.envMap.value=S,yr.copy(T),yr.x*=-1,yr.y*=-1,yr.z*=-1,S.isCubeTexture&&S.isRenderTargetTexture===!1&&(yr.y*=-1,yr.z*=-1),p.envMapRotation.value.setFromMatrix4(Zx.makeRotationFromEuler(yr)),p.flipEnvMap.value=S.isCubeTexture&&S.isRenderTargetTexture===!1?-1:1,p.reflectivity.value=f.reflectivity,p.ior.value=f.ior,p.refractionRatio.value=f.refractionRatio),f.lightMap&&(p.lightMap.value=f.lightMap,p.lightMapIntensity.value=f.lightMapIntensity,t(f.lightMap,p.lightMapTransform)),f.aoMap&&(p.aoMap.value=f.aoMap,p.aoMapIntensity.value=f.aoMapIntensity,t(f.aoMap,p.aoMapTransform))}function a(p,f){p.diffuse.value.copy(f.color),p.opacity.value=f.opacity,f.map&&(p.map.value=f.map,t(f.map,p.mapTransform))}function o(p,f){p.dashSize.value=f.dashSize,p.totalSize.value=f.dashSize+f.gapSize,p.scale.value=f.scale}function l(p,f,E,S){p.diffuse.value.copy(f.color),p.opacity.value=f.opacity,p.size.value=f.size*E,p.scale.value=S*.5,f.map&&(p.map.value=f.map,t(f.map,p.uvTransform)),f.alphaMap&&(p.alphaMap.value=f.alphaMap,t(f.alphaMap,p.alphaMapTransform)),f.alphaTest>0&&(p.alphaTest.value=f.alphaTest)}function c(p,f){p.diffuse.value.copy(f.color),p.opacity.value=f.opacity,p.rotation.value=f.rotation,f.map&&(p.map.value=f.map,t(f.map,p.mapTransform)),f.alphaMap&&(p.alphaMap.value=f.alphaMap,t(f.alphaMap,p.alphaMapTransform)),f.alphaTest>0&&(p.alphaTest.value=f.alphaTest)}function u(p,f){p.specular.value.copy(f.specular),p.shininess.value=Math.max(f.shininess,1e-4)}function h(p,f){f.gradientMap&&(p.gradientMap.value=f.gradientMap)}function d(p,f){p.metalness.value=f.metalness,f.metalnessMap&&(p.metalnessMap.value=f.metalnessMap,t(f.metalnessMap,p.metalnessMapTransform)),p.roughness.value=f.roughness,f.roughnessMap&&(p.roughnessMap.value=f.roughnessMap,t(f.roughnessMap,p.roughnessMapTransform)),f.envMap&&(p.envMapIntensity.value=f.envMapIntensity)}function m(p,f,E){p.ior.value=f.ior,f.sheen>0&&(p.sheenColor.value.copy(f.sheenColor).multiplyScalar(f.sheen),p.sheenRoughness.value=f.sheenRoughness,f.sheenColorMap&&(p.sheenColorMap.value=f.sheenColorMap,t(f.sheenColorMap,p.sheenColorMapTransform)),f.sheenRoughnessMap&&(p.sheenRoughnessMap.value=f.sheenRoughnessMap,t(f.sheenRoughnessMap,p.sheenRoughnessMapTransform))),f.clearcoat>0&&(p.clearcoat.value=f.clearcoat,p.clearcoatRoughness.value=f.clearcoatRoughness,f.clearcoatMap&&(p.clearcoatMap.value=f.clearcoatMap,t(f.clearcoatMap,p.clearcoatMapTransform)),f.clearcoatRoughnessMap&&(p.clearcoatRoughnessMap.value=f.clearcoatRoughnessMap,t(f.clearcoatRoughnessMap,p.clearcoatRoughnessMapTransform)),f.clearcoatNormalMap&&(p.clearcoatNormalMap.value=f.clearcoatNormalMap,t(f.clearcoatNormalMap,p.clearcoatNormalMapTransform),p.clearcoatNormalScale.value.copy(f.clearcoatNormalScale),f.side===Cn&&p.clearcoatNormalScale.value.negate())),f.dispersion>0&&(p.dispersion.value=f.dispersion),f.iridescence>0&&(p.iridescence.value=f.iridescence,p.iridescenceIOR.value=f.iridescenceIOR,p.iridescenceThicknessMinimum.value=f.iridescenceThicknessRange[0],p.iridescenceThicknessMaximum.value=f.iridescenceThicknessRange[1],f.iridescenceMap&&(p.iridescenceMap.value=f.iridescenceMap,t(f.iridescenceMap,p.iridescenceMapTransform)),f.iridescenceThicknessMap&&(p.iridescenceThicknessMap.value=f.iridescenceThicknessMap,t(f.iridescenceThicknessMap,p.iridescenceThicknessMapTransform))),f.transmission>0&&(p.transmission.value=f.transmission,p.transmissionSamplerMap.value=E.texture,p.transmissionSamplerSize.value.set(E.width,E.height),f.transmissionMap&&(p.transmissionMap.value=f.transmissionMap,t(f.transmissionMap,p.transmissionMapTransform)),p.thickness.value=f.thickness,f.thicknessMap&&(p.thicknessMap.value=f.thicknessMap,t(f.thicknessMap,p.thicknessMapTransform)),p.attenuationDistance.value=f.attenuationDistance,p.attenuationColor.value.copy(f.attenuationColor)),f.anisotropy>0&&(p.anisotropyVector.value.set(f.anisotropy*Math.cos(f.anisotropyRotation),f.anisotropy*Math.sin(f.anisotropyRotation)),f.anisotropyMap&&(p.anisotropyMap.value=f.anisotropyMap,t(f.anisotropyMap,p.anisotropyMapTransform))),p.specularIntensity.value=f.specularIntensity,p.specularColor.value.copy(f.specularColor),f.specularColorMap&&(p.specularColorMap.value=f.specularColorMap,t(f.specularColorMap,p.specularColorMapTransform)),f.specularIntensityMap&&(p.specularIntensityMap.value=f.specularIntensityMap,t(f.specularIntensityMap,p.specularIntensityMapTransform))}function _(p,f){f.matcap&&(p.matcap.value=f.matcap)}function v(p,f){const E=e.get(f).light;p.referencePosition.value.setFromMatrixPosition(E.matrixWorld),p.nearDistance.value=E.shadow.camera.near,p.farDistance.value=E.shadow.camera.far}return{refreshFogUniforms:n,refreshMaterialUniforms:r}}function Qx(i,e,t,n){let r={},s={},a=[];const o=i.getParameter(i.MAX_UNIFORM_BUFFER_BINDINGS);function l(E,S){const T=S.program;n.uniformBlockBinding(E,T)}function c(E,S){let T=r[E.id];T===void 0&&(_(E),T=u(E),r[E.id]=T,E.addEventListener("dispose",p));const z=S.program;n.updateUBOMapping(E,z);const R=e.render.frame;s[E.id]!==R&&(d(E),s[E.id]=R)}function u(E){const S=h();E.__bindingPointIndex=S;const T=i.createBuffer(),z=E.__size,R=E.usage;return i.bindBuffer(i.UNIFORM_BUFFER,T),i.bufferData(i.UNIFORM_BUFFER,z,R),i.bindBuffer(i.UNIFORM_BUFFER,null),i.bindBufferBase(i.UNIFORM_BUFFER,S,T),T}function h(){for(let E=0;E<o;E++)if(a.indexOf(E)===-1)return a.push(E),E;return console.error("THREE.WebGLRenderer: Maximum number of simultaneously usable uniforms groups reached."),0}function d(E){const S=r[E.id],T=E.uniforms,z=E.__cache;i.bindBuffer(i.UNIFORM_BUFFER,S);for(let R=0,L=T.length;R<L;R++){const O=Array.isArray(T[R])?T[R]:[T[R]];for(let w=0,x=O.length;w<x;w++){const C=O[w];if(m(C,R,w,z)===!0){const j=C.__offset,B=Array.isArray(C.value)?C.value:[C.value];let K=0;for(let W=0;W<B.length;W++){const J=B[W],q=v(J);typeof J=="number"||typeof J=="boolean"?(C.__data[0]=J,i.bufferSubData(i.UNIFORM_BUFFER,j+K,C.__data)):J.isMatrix3?(C.__data[0]=J.elements[0],C.__data[1]=J.elements[1],C.__data[2]=J.elements[2],C.__data[3]=0,C.__data[4]=J.elements[3],C.__data[5]=J.elements[4],C.__data[6]=J.elements[5],C.__data[7]=0,C.__data[8]=J.elements[6],C.__data[9]=J.elements[7],C.__data[10]=J.elements[8],C.__data[11]=0):(J.toArray(C.__data,K),K+=q.storage/Float32Array.BYTES_PER_ELEMENT)}i.bufferSubData(i.UNIFORM_BUFFER,j,C.__data)}}}i.bindBuffer(i.UNIFORM_BUFFER,null)}function m(E,S,T,z){const R=E.value,L=S+"_"+T;if(z[L]===void 0)return typeof R=="number"||typeof R=="boolean"?z[L]=R:z[L]=R.clone(),!0;{const O=z[L];if(typeof R=="number"||typeof R=="boolean"){if(O!==R)return z[L]=R,!0}else if(O.equals(R)===!1)return O.copy(R),!0}return!1}function _(E){const S=E.uniforms;let T=0;const z=16;for(let L=0,O=S.length;L<O;L++){const w=Array.isArray(S[L])?S[L]:[S[L]];for(let x=0,C=w.length;x<C;x++){const j=w[x],B=Array.isArray(j.value)?j.value:[j.value];for(let K=0,W=B.length;K<W;K++){const J=B[K],q=v(J),ee=T%z,me=ee%q.boundary,he=ee+me;T+=me,he!==0&&z-he<q.storage&&(T+=z-he),j.__data=new Float32Array(q.storage/Float32Array.BYTES_PER_ELEMENT),j.__offset=T,T+=q.storage}}}const R=T%z;return R>0&&(T+=z-R),E.__size=T,E.__cache={},this}function v(E){const S={boundary:0,storage:0};return typeof E=="number"||typeof E=="boolean"?(S.boundary=4,S.storage=4):E.isVector2?(S.boundary=8,S.storage=8):E.isVector3||E.isColor?(S.boundary=16,S.storage=12):E.isVector4?(S.boundary=16,S.storage=16):E.isMatrix3?(S.boundary=48,S.storage=48):E.isMatrix4?(S.boundary=64,S.storage=64):E.isTexture?console.warn("THREE.WebGLRenderer: Texture samplers can not be part of an uniforms group."):console.warn("THREE.WebGLRenderer: Unsupported uniform value type.",E),S}function p(E){const S=E.target;S.removeEventListener("dispose",p);const T=a.indexOf(S.__bindingPointIndex);a.splice(T,1),i.deleteBuffer(r[S.id]),delete r[S.id],delete s[S.id]}function f(){for(const E in r)i.deleteBuffer(r[E]);a=[],r={},s={}}return{bind:l,update:c,dispose:f}}class Mf{constructor(e={}){const{canvas:t=Wm(),context:n=null,depth:r=!0,stencil:s=!1,alpha:a=!1,antialias:o=!1,premultipliedAlpha:l=!0,preserveDrawingBuffer:c=!1,powerPreference:u="default",failIfMajorPerformanceCaveat:h=!1}=e;this.isWebGLRenderer=!0;let d;if(n!==null){if(typeof WebGLRenderingContext<"u"&&n instanceof WebGLRenderingContext)throw new Error("THREE.WebGLRenderer: WebGL 1 is not supported since r163.");d=n.getContextAttributes().alpha}else d=a;const m=new Uint32Array(4),_=new Int32Array(4);let v=null,p=null;const f=[],E=[];this.domElement=t,this.debug={checkShaderErrors:!0,onShaderError:null},this.autoClear=!0,this.autoClearColor=!0,this.autoClearDepth=!0,this.autoClearStencil=!0,this.sortObjects=!0,this.clippingPlanes=[],this.localClippingEnabled=!1,this._outputColorSpace=pi,this.toneMapping=er,this.toneMappingExposure=1;const S=this;let T=!1,z=0,R=0,L=null,O=-1,w=null;const x=new Zt,C=new Zt;let j=null;const B=new tt(0);let K=0,W=t.width,J=t.height,q=1,ee=null,me=null;const he=new Zt(0,0,W,J),ve=new Zt(0,0,W,J);let Te=!1;const xe=new Zc;let te=!1,ce=!1;const ye=new Ft,de=new H,Be=new Zt,Ve={background:null,fog:null,environment:null,overrideMaterial:null,isScene:!0};let Ne=!1;function dt(){return L===null?q:1}let U=n;function ut(b,V){return t.getContext(b,V)}try{const b={alpha:!0,depth:r,stencil:s,antialias:o,premultipliedAlpha:l,preserveDrawingBuffer:c,powerPreference:u,failIfMajorPerformanceCaveat:h};if("setAttribute"in t&&t.setAttribute("data-engine",`three.js r${Hc}`),t.addEventListener("webglcontextlost",ne,!1),t.addEventListener("webglcontextrestored",ie,!1),t.addEventListener("webglcontextcreationerror",_e,!1),U===null){const V="webgl2";if(U=ut(V,b),U===null)throw ut(V)?new Error("Error creating WebGL context with your selected attributes."):new Error("Error creating WebGL context.")}}catch(b){throw console.error("THREE.WebGLRenderer: "+b.message),b}let nt,ot,Fe,St,qe,We,D,M,Z,oe,Q,G,Ee,ge,Ae,je,pe,we,Ke,ze,Se,ke,N,le;function I(){nt=new av(U),nt.init(),ke=new Wx(U,nt),ot=new ev(U,nt,e,ke),Fe=new Hx(U),St=new cv(U),qe=new Ax,We=new Gx(U,nt,Fe,qe,ot,ke,St),D=new nv(S),M=new sv(S),Z=new gg(U),N=new J0(U,Z),oe=new ov(U,Z,St,N),Q=new hv(U,oe,Z,St),Ke=new uv(U,ot,We),je=new tv(qe),G=new wx(S,D,M,nt,ot,N,je),Ee=new Jx(S,qe),ge=new Cx,Ae=new Nx(nt),we=new Z0(S,D,M,Fe,Q,d,l),pe=new kx(S,Q,ot),le=new Qx(U,St,ot,Fe),ze=new Q0(U,nt,St),Se=new lv(U,nt,St),St.programs=G.programs,S.capabilities=ot,S.extensions=nt,S.properties=qe,S.renderLists=ge,S.shadowMap=pe,S.state=Fe,S.info=St}I();const re=new Kx(S,U);this.xr=re,this.getContext=function(){return U},this.getContextAttributes=function(){return U.getContextAttributes()},this.forceContextLoss=function(){const b=nt.get("WEBGL_lose_context");b&&b.loseContext()},this.forceContextRestore=function(){const b=nt.get("WEBGL_lose_context");b&&b.restoreContext()},this.getPixelRatio=function(){return q},this.setPixelRatio=function(b){b!==void 0&&(q=b,this.setSize(W,J,!1))},this.getSize=function(b){return b.set(W,J)},this.setSize=function(b,V,$=!0){if(re.isPresenting){console.warn("THREE.WebGLRenderer: Can't change size while VR device is presenting.");return}W=b,J=V,t.width=Math.floor(b*q),t.height=Math.floor(V*q),$===!0&&(t.style.width=b+"px",t.style.height=V+"px"),this.setViewport(0,0,b,V)},this.getDrawingBufferSize=function(b){return b.set(W*q,J*q).floor()},this.setDrawingBufferSize=function(b,V,$){W=b,J=V,q=$,t.width=Math.floor(b*$),t.height=Math.floor(V*$),this.setViewport(0,0,b,V)},this.getCurrentViewport=function(b){return b.copy(x)},this.getViewport=function(b){return b.copy(he)},this.setViewport=function(b,V,$,X){b.isVector4?he.set(b.x,b.y,b.z,b.w):he.set(b,V,$,X),Fe.viewport(x.copy(he).multiplyScalar(q).round())},this.getScissor=function(b){return b.copy(ve)},this.setScissor=function(b,V,$,X){b.isVector4?ve.set(b.x,b.y,b.z,b.w):ve.set(b,V,$,X),Fe.scissor(C.copy(ve).multiplyScalar(q).round())},this.getScissorTest=function(){return Te},this.setScissorTest=function(b){Fe.setScissorTest(Te=b)},this.setOpaqueSort=function(b){ee=b},this.setTransparentSort=function(b){me=b},this.getClearColor=function(b){return b.copy(we.getClearColor())},this.setClearColor=function(){we.setClearColor.apply(we,arguments)},this.getClearAlpha=function(){return we.getClearAlpha()},this.setClearAlpha=function(){we.setClearAlpha.apply(we,arguments)},this.clear=function(b=!0,V=!0,$=!0){let X=0;if(b){let k=!1;if(L!==null){const ue=L.texture.format;k=ue===Yc||ue===qc||ue===Xc}if(k){const ue=L.texture.type,Ce=ue===Oi||ue===Pr||ue===ma||ue===ws||ue===Gc||ue===Wc,Pe=we.getClearColor(),Ie=we.getClearAlpha(),Ze=Pe.r,Je=Pe.g,Oe=Pe.b;Ce?(m[0]=Ze,m[1]=Je,m[2]=Oe,m[3]=Ie,U.clearBufferuiv(U.COLOR,0,m)):(_[0]=Ze,_[1]=Je,_[2]=Oe,_[3]=Ie,U.clearBufferiv(U.COLOR,0,_))}else X|=U.COLOR_BUFFER_BIT}V&&(X|=U.DEPTH_BUFFER_BIT),$&&(X|=U.STENCIL_BUFFER_BIT,this.state.buffers.stencil.setMask(4294967295)),U.clear(X)},this.clearColor=function(){this.clear(!0,!1,!1)},this.clearDepth=function(){this.clear(!1,!0,!1)},this.clearStencil=function(){this.clear(!1,!1,!0)},this.dispose=function(){t.removeEventListener("webglcontextlost",ne,!1),t.removeEventListener("webglcontextrestored",ie,!1),t.removeEventListener("webglcontextcreationerror",_e,!1),ge.dispose(),Ae.dispose(),qe.dispose(),D.dispose(),M.dispose(),Q.dispose(),N.dispose(),le.dispose(),G.dispose(),re.dispose(),re.removeEventListener("sessionstart",Ot),re.removeEventListener("sessionend",Bt),tn.stop()};function ne(b){b.preventDefault(),console.log("THREE.WebGLRenderer: Context Lost."),T=!0}function ie(){console.log("THREE.WebGLRenderer: Context Restored."),T=!1;const b=St.autoReset,V=pe.enabled,$=pe.autoUpdate,X=pe.needsUpdate,k=pe.type;I(),St.autoReset=b,pe.enabled=V,pe.autoUpdate=$,pe.needsUpdate=X,pe.type=k}function _e(b){console.error("THREE.WebGLRenderer: A WebGL context could not be created. Reason: ",b.statusMessage)}function $e(b){const V=b.target;V.removeEventListener("dispose",$e),st(V)}function st(b){mt(b),qe.remove(b)}function mt(b){const V=qe.get(b).programs;V!==void 0&&(V.forEach(function($){G.releaseProgram($)}),b.isShaderMaterial&&G.releaseShaderCache(b))}this.renderBufferDirect=function(b,V,$,X,k,ue){V===null&&(V=Ve);const Ce=k.isMesh&&k.matrixWorld.determinant()<0,Pe=qo(b,V,$,X,k);Fe.setMaterial(X,Ce);let Ie=$.index,Ze=1;if(X.wireframe===!0){if(Ie=oe.getWireframeAttribute($),Ie===void 0)return;Ze=2}const Je=$.drawRange,Oe=$.attributes.position;let lt=Je.start*Ze,Rt=(Je.start+Je.count)*Ze;ue!==null&&(lt=Math.max(lt,ue.start*Ze),Rt=Math.min(Rt,(ue.start+ue.count)*Ze)),Ie!==null?(lt=Math.max(lt,0),Rt=Math.min(Rt,Ie.count)):Oe!=null&&(lt=Math.max(lt,0),Rt=Math.min(Rt,Oe.count));const Ct=Rt-lt;if(Ct<0||Ct===1/0)return;N.setup(k,X,Pe,$,Ie);let hn,ft=ze;if(Ie!==null&&(hn=Z.get(Ie),ft=Se,ft.setIndex(hn)),k.isMesh)X.wireframe===!0?(Fe.setLineWidth(X.wireframeLinewidth*dt()),ft.setMode(U.LINES)):ft.setMode(U.TRIANGLES);else if(k.isLine){let He=X.linewidth;He===void 0&&(He=1),Fe.setLineWidth(He*dt()),k.isLineSegments?ft.setMode(U.LINES):k.isLineLoop?ft.setMode(U.LINE_LOOP):ft.setMode(U.LINE_STRIP)}else k.isPoints?ft.setMode(U.POINTS):k.isSprite&&ft.setMode(U.TRIANGLES);if(k.isBatchedMesh)if(k._multiDrawInstances!==null)ft.renderMultiDrawInstances(k._multiDrawStarts,k._multiDrawCounts,k._multiDrawCount,k._multiDrawInstances);else if(nt.get("WEBGL_multi_draw"))ft.renderMultiDraw(k._multiDrawStarts,k._multiDrawCounts,k._multiDrawCount);else{const He=k._multiDrawStarts,Gt=k._multiDrawCounts,pt=k._multiDrawCount,Pt=Ie?Z.get(Ie).bytesPerElement:1,Si=qe.get(X).currentProgram.getUniforms();for(let fn=0;fn<pt;fn++)Si.setValue(U,"_gl_DrawID",fn),ft.render(He[fn]/Pt,Gt[fn])}else if(k.isInstancedMesh)ft.renderInstances(lt,Ct,k.count);else if($.isInstancedBufferGeometry){const He=$._maxInstanceCount!==void 0?$._maxInstanceCount:1/0,Gt=Math.min($.instanceCount,He);ft.renderInstances(lt,Ct,Gt)}else ft.render(lt,Ct)};function Et(b,V,$){b.transparent===!0&&b.side===gi&&b.forceSinglePass===!1?(b.side=Cn,b.needsUpdate=!0,ur(b,V,$),b.side=ir,b.needsUpdate=!0,ur(b,V,$),b.side=gi):ur(b,V,$)}this.compile=function(b,V,$=null){$===null&&($=b),p=Ae.get($),p.init(V),E.push(p),$.traverseVisible(function(k){k.isLight&&k.layers.test(V.layers)&&(p.pushLight(k),k.castShadow&&p.pushShadow(k))}),b!==$&&b.traverseVisible(function(k){k.isLight&&k.layers.test(V.layers)&&(p.pushLight(k),k.castShadow&&p.pushShadow(k))}),p.setupLights();const X=new Set;return b.traverse(function(k){const ue=k.material;if(ue)if(Array.isArray(ue))for(let Ce=0;Ce<ue.length;Ce++){const Pe=ue[Ce];Et(Pe,$,k),X.add(Pe)}else Et(ue,$,k),X.add(ue)}),E.pop(),p=null,X},this.compileAsync=function(b,V,$=null){const X=this.compile(b,V,$);return new Promise(k=>{function ue(){if(X.forEach(function(Ce){qe.get(Ce).currentProgram.isReady()&&X.delete(Ce)}),X.size===0){k(b);return}setTimeout(ue,10)}nt.get("KHR_parallel_shader_compile")!==null?ue():setTimeout(ue,10)})};let at=null;function un(b){at&&at(b)}function Ot(){tn.stop()}function Bt(){tn.start()}const tn=new mf;tn.setAnimationLoop(un),typeof self<"u"&&tn.setContext(self),this.setAnimationLoop=function(b){at=b,re.setAnimationLoop(b),b===null?tn.stop():tn.start()},re.addEventListener("sessionstart",Ot),re.addEventListener("sessionend",Bt),this.render=function(b,V){if(V!==void 0&&V.isCamera!==!0){console.error("THREE.WebGLRenderer.render: camera is not an instance of THREE.Camera.");return}if(T===!0)return;if(b.matrixWorldAutoUpdate===!0&&b.updateMatrixWorld(),V.parent===null&&V.matrixWorldAutoUpdate===!0&&V.updateMatrixWorld(),re.enabled===!0&&re.isPresenting===!0&&(re.cameraAutoUpdate===!0&&re.updateCamera(V),V=re.getCamera()),b.isScene===!0&&b.onBeforeRender(S,b,V,L),p=Ae.get(b,E.length),p.init(V),E.push(p),ye.multiplyMatrices(V.projectionMatrix,V.matrixWorldInverse),xe.setFromProjectionMatrix(ye),ce=this.localClippingEnabled,te=je.init(this.clippingPlanes,ce),v=ge.get(b,f.length),v.init(),f.push(v),re.enabled===!0&&re.isPresenting===!0){const ue=S.xr.getDepthSensingMesh();ue!==null&&oi(ue,V,-1/0,S.sortObjects)}oi(b,V,0,S.sortObjects),v.finish(),S.sortObjects===!0&&v.sort(ee,me),Ne=re.enabled===!1||re.isPresenting===!1||re.hasDepthSensing()===!1,Ne&&we.addToRenderList(v,b),this.info.render.frame++,te===!0&&je.beginShadows();const $=p.state.shadowsArray;pe.render($,b,V),te===!0&&je.endShadows(),this.info.autoReset===!0&&this.info.reset();const X=v.opaque,k=v.transmissive;if(p.setupLights(),V.isArrayCamera){const ue=V.cameras;if(k.length>0)for(let Ce=0,Pe=ue.length;Ce<Pe;Ce++){const Ie=ue[Ce];xn(X,k,b,Ie)}Ne&&we.render(b);for(let Ce=0,Pe=ue.length;Ce<Pe;Ce++){const Ie=ue[Ce];xi(v,b,Ie,Ie.viewport)}}else k.length>0&&xn(X,k,b,V),Ne&&we.render(b),xi(v,b,V);L!==null&&(We.updateMultisampleRenderTarget(L),We.updateRenderTargetMipmap(L)),b.isScene===!0&&b.onAfterRender(S,b,V),N.resetDefaultState(),O=-1,w=null,E.pop(),E.length>0?(p=E[E.length-1],te===!0&&je.setGlobalState(S.clippingPlanes,p.state.camera)):p=null,f.pop(),f.length>0?v=f[f.length-1]:v=null};function oi(b,V,$,X){if(b.visible===!1)return;if(b.layers.test(V.layers)){if(b.isGroup)$=b.renderOrder;else if(b.isLOD)b.autoUpdate===!0&&b.update(V);else if(b.isLight)p.pushLight(b),b.castShadow&&p.pushShadow(b);else if(b.isSprite){if(!b.frustumCulled||xe.intersectsSprite(b)){X&&Be.setFromMatrixPosition(b.matrixWorld).applyMatrix4(ye);const Ce=Q.update(b),Pe=b.material;Pe.visible&&v.push(b,Ce,Pe,$,Be.z,null)}}else if((b.isMesh||b.isLine||b.isPoints)&&(!b.frustumCulled||xe.intersectsObject(b))){const Ce=Q.update(b),Pe=b.material;if(X&&(b.boundingSphere!==void 0?(b.boundingSphere===null&&b.computeBoundingSphere(),Be.copy(b.boundingSphere.center)):(Ce.boundingSphere===null&&Ce.computeBoundingSphere(),Be.copy(Ce.boundingSphere.center)),Be.applyMatrix4(b.matrixWorld).applyMatrix4(ye)),Array.isArray(Pe)){const Ie=Ce.groups;for(let Ze=0,Je=Ie.length;Ze<Je;Ze++){const Oe=Ie[Ze],lt=Pe[Oe.materialIndex];lt&&lt.visible&&v.push(b,Ce,lt,$,Be.z,Oe)}}else Pe.visible&&v.push(b,Ce,Pe,$,Be.z,null)}}const ue=b.children;for(let Ce=0,Pe=ue.length;Ce<Pe;Ce++)oi(ue[Ce],V,$,X)}function xi(b,V,$,X){const k=b.opaque,ue=b.transmissive,Ce=b.transparent;p.setupLightsView($),te===!0&&je.setGlobalState(S.clippingPlanes,$),X&&Fe.viewport(x.copy(X)),k.length>0&&Yn(k,V,$),ue.length>0&&Yn(ue,V,$),Ce.length>0&&Yn(Ce,V,$),Fe.buffers.depth.setTest(!0),Fe.buffers.depth.setMask(!0),Fe.buffers.color.setMask(!0),Fe.setPolygonOffset(!1)}function xn(b,V,$,X){if(($.isScene===!0?$.overrideMaterial:null)!==null)return;p.state.transmissionRenderTarget[X.id]===void 0&&(p.state.transmissionRenderTarget[X.id]=new Lr(1,1,{generateMipmaps:!0,type:nt.has("EXT_color_buffer_half_float")||nt.has("EXT_color_buffer_float")?va:Oi,minFilter:Rr,samples:4,stencilBuffer:s,resolveDepthBuffer:!1,resolveStencilBuffer:!1,colorSpace:Mt.workingColorSpace}));const ue=p.state.transmissionRenderTarget[X.id],Ce=X.viewport||x;ue.setSize(Ce.z,Ce.w);const Pe=S.getRenderTarget();S.setRenderTarget(ue),S.getClearColor(B),K=S.getClearAlpha(),K<1&&S.setClearColor(16777215,.5),S.clear(),Ne&&we.render($);const Ie=S.toneMapping;S.toneMapping=er;const Ze=X.viewport;if(X.viewport!==void 0&&(X.viewport=void 0),p.setupLightsView(X),te===!0&&je.setGlobalState(S.clippingPlanes,X),Yn(b,$,X),We.updateMultisampleRenderTarget(ue),We.updateRenderTargetMipmap(ue),nt.has("WEBGL_multisampled_render_to_texture")===!1){let Je=!1;for(let Oe=0,lt=V.length;Oe<lt;Oe++){const Rt=V[Oe],Ct=Rt.object,hn=Rt.geometry,ft=Rt.material,He=Rt.group;if(ft.side===gi&&Ct.layers.test(X.layers)){const Gt=ft.side;ft.side=Cn,ft.needsUpdate=!0,yi(Ct,$,X,hn,ft,He),ft.side=Gt,ft.needsUpdate=!0,Je=!0}}Je===!0&&(We.updateMultisampleRenderTarget(ue),We.updateRenderTargetMipmap(ue))}S.setRenderTarget(Pe),S.setClearColor(B,K),Ze!==void 0&&(X.viewport=Ze),S.toneMapping=Ie}function Yn(b,V,$){const X=V.isScene===!0?V.overrideMaterial:null;for(let k=0,ue=b.length;k<ue;k++){const Ce=b[k],Pe=Ce.object,Ie=Ce.geometry,Ze=X===null?Ce.material:X,Je=Ce.group;Pe.layers.test($.layers)&&yi(Pe,V,$,Ie,Ze,Je)}}function yi(b,V,$,X,k,ue){b.onBeforeRender(S,V,$,X,k,ue),b.modelViewMatrix.multiplyMatrices($.matrixWorldInverse,b.matrixWorld),b.normalMatrix.getNormalMatrix(b.modelViewMatrix),k.onBeforeRender(S,V,$,X,b,ue),k.transparent===!0&&k.side===gi&&k.forceSinglePass===!1?(k.side=Cn,k.needsUpdate=!0,S.renderBufferDirect($,V,X,k,b,ue),k.side=ir,k.needsUpdate=!0,S.renderBufferDirect($,V,X,k,b,ue),k.side=gi):S.renderBufferDirect($,V,X,k,b,ue),b.onAfterRender(S,V,$,X,k,ue)}function ur(b,V,$){V.isScene!==!0&&(V=Ve);const X=qe.get(b),k=p.state.lights,ue=p.state.shadowsArray,Ce=k.state.version,Pe=G.getParameters(b,k.state,ue,V,$),Ie=G.getProgramCacheKey(Pe);let Ze=X.programs;X.environment=b.isMeshStandardMaterial?V.environment:null,X.fog=V.fog,X.envMap=(b.isMeshStandardMaterial?M:D).get(b.envMap||X.environment),X.envMapRotation=X.environment!==null&&b.envMap===null?V.environmentRotation:b.envMapRotation,Ze===void 0&&(b.addEventListener("dispose",$e),Ze=new Map,X.programs=Ze);let Je=Ze.get(Ie);if(Je!==void 0){if(X.currentProgram===Je&&X.lightsStateVersion===Ce)return Sa(b,Pe),Je}else Pe.uniforms=G.getUniforms(b),b.onBeforeCompile(Pe,S),Je=G.acquireProgram(Pe,Ie),Ze.set(Ie,Je),X.uniforms=Pe.uniforms;const Oe=X.uniforms;return(!b.isShaderMaterial&&!b.isRawShaderMaterial||b.clipping===!0)&&(Oe.clippingPlanes=je.uniform),Sa(b,Pe),X.needsLights=Yo(b),X.lightsStateVersion=Ce,X.needsLights&&(Oe.ambientLightColor.value=k.state.ambient,Oe.lightProbe.value=k.state.probe,Oe.directionalLights.value=k.state.directional,Oe.directionalLightShadows.value=k.state.directionalShadow,Oe.spotLights.value=k.state.spot,Oe.spotLightShadows.value=k.state.spotShadow,Oe.rectAreaLights.value=k.state.rectArea,Oe.ltc_1.value=k.state.rectAreaLTC1,Oe.ltc_2.value=k.state.rectAreaLTC2,Oe.pointLights.value=k.state.point,Oe.pointLightShadows.value=k.state.pointShadow,Oe.hemisphereLights.value=k.state.hemi,Oe.directionalShadowMap.value=k.state.directionalShadowMap,Oe.directionalShadowMatrix.value=k.state.directionalShadowMatrix,Oe.spotShadowMap.value=k.state.spotShadowMap,Oe.spotLightMatrix.value=k.state.spotLightMatrix,Oe.spotLightMap.value=k.state.spotLightMap,Oe.pointShadowMap.value=k.state.pointShadowMap,Oe.pointShadowMatrix.value=k.state.pointShadowMatrix),X.currentProgram=Je,X.uniformsList=null,Je}function ks(b){if(b.uniformsList===null){const V=b.currentProgram.getUniforms();b.uniformsList=xo.seqWithValue(V.seq,b.uniforms)}return b.uniformsList}function Sa(b,V){const $=qe.get(b);$.outputColorSpace=V.outputColorSpace,$.batching=V.batching,$.batchingColor=V.batchingColor,$.instancing=V.instancing,$.instancingColor=V.instancingColor,$.instancingMorph=V.instancingMorph,$.skinning=V.skinning,$.morphTargets=V.morphTargets,$.morphNormals=V.morphNormals,$.morphColors=V.morphColors,$.morphTargetsCount=V.morphTargetsCount,$.numClippingPlanes=V.numClippingPlanes,$.numIntersection=V.numClipIntersection,$.vertexAlphas=V.vertexAlphas,$.vertexTangents=V.vertexTangents,$.toneMapping=V.toneMapping}function qo(b,V,$,X,k){V.isScene!==!0&&(V=Ve),We.resetTextureUnits();const ue=V.fog,Ce=X.isMeshStandardMaterial?V.environment:null,Pe=L===null?S.outputColorSpace:L.isXRRenderTarget===!0?L.texture.colorSpace:lr,Ie=(X.isMeshStandardMaterial?M:D).get(X.envMap||Ce),Ze=X.vertexColors===!0&&!!$.attributes.color&&$.attributes.color.itemSize===4,Je=!!$.attributes.tangent&&(!!X.normalMap||X.anisotropy>0),Oe=!!$.morphAttributes.position,lt=!!$.morphAttributes.normal,Rt=!!$.morphAttributes.color;let Ct=er;X.toneMapped&&(L===null||L.isXRRenderTarget===!0)&&(Ct=S.toneMapping);const hn=$.morphAttributes.position||$.morphAttributes.normal||$.morphAttributes.color,ft=hn!==void 0?hn.length:0,He=qe.get(X),Gt=p.state.lights;if(te===!0&&(ce===!0||b!==w)){const Rn=b===w&&X.id===O;je.setState(X,b,Rn)}let pt=!1;X.version===He.__version?(He.needsLights&&He.lightsStateVersion!==Gt.state.version||He.outputColorSpace!==Pe||k.isBatchedMesh&&He.batching===!1||!k.isBatchedMesh&&He.batching===!0||k.isBatchedMesh&&He.batchingColor===!0&&k.colorTexture===null||k.isBatchedMesh&&He.batchingColor===!1&&k.colorTexture!==null||k.isInstancedMesh&&He.instancing===!1||!k.isInstancedMesh&&He.instancing===!0||k.isSkinnedMesh&&He.skinning===!1||!k.isSkinnedMesh&&He.skinning===!0||k.isInstancedMesh&&He.instancingColor===!0&&k.instanceColor===null||k.isInstancedMesh&&He.instancingColor===!1&&k.instanceColor!==null||k.isInstancedMesh&&He.instancingMorph===!0&&k.morphTexture===null||k.isInstancedMesh&&He.instancingMorph===!1&&k.morphTexture!==null||He.envMap!==Ie||X.fog===!0&&He.fog!==ue||He.numClippingPlanes!==void 0&&(He.numClippingPlanes!==je.numPlanes||He.numIntersection!==je.numIntersection)||He.vertexAlphas!==Ze||He.vertexTangents!==Je||He.morphTargets!==Oe||He.morphNormals!==lt||He.morphColors!==Rt||He.toneMapping!==Ct||He.morphTargetsCount!==ft)&&(pt=!0):(pt=!0,He.__version=X.version);let Pt=He.currentProgram;pt===!0&&(Pt=ur(X,V,k));let Si=!1,fn=!1,hr=!1;const kt=Pt.getUniforms(),li=He.uniforms;if(Fe.useProgram(Pt.program)&&(Si=!0,fn=!0,hr=!0),X.id!==O&&(O=X.id,fn=!0),Si||w!==b){kt.setValue(U,"projectionMatrix",b.projectionMatrix),kt.setValue(U,"viewMatrix",b.matrixWorldInverse);const Rn=kt.map.cameraPosition;Rn!==void 0&&Rn.setValue(U,de.setFromMatrixPosition(b.matrixWorld)),ot.logarithmicDepthBuffer&&kt.setValue(U,"logDepthBufFC",2/(Math.log(b.far+1)/Math.LN2)),(X.isMeshPhongMaterial||X.isMeshToonMaterial||X.isMeshLambertMaterial||X.isMeshBasicMaterial||X.isMeshStandardMaterial||X.isShaderMaterial)&&kt.setValue(U,"isOrthographic",b.isOrthographicCamera===!0),w!==b&&(w=b,fn=!0,hr=!0)}if(k.isSkinnedMesh){kt.setOptional(U,k,"bindMatrix"),kt.setOptional(U,k,"bindMatrixInverse");const Rn=k.skeleton;Rn&&(Rn.boneTexture===null&&Rn.computeBoneTexture(),kt.setValue(U,"boneTexture",Rn.boneTexture,We))}k.isBatchedMesh&&(kt.setOptional(U,k,"batchingTexture"),kt.setValue(U,"batchingTexture",k._matricesTexture,We),kt.setOptional(U,k,"batchingIdTexture"),kt.setValue(U,"batchingIdTexture",k._indirectTexture,We),kt.setOptional(U,k,"batchingColorTexture"),k._colorsTexture!==null&&kt.setValue(U,"batchingColorTexture",k._colorsTexture,We));const Hs=$.morphAttributes;if((Hs.position!==void 0||Hs.normal!==void 0||Hs.color!==void 0)&&Ke.update(k,$,Pt),(fn||He.receiveShadow!==k.receiveShadow)&&(He.receiveShadow=k.receiveShadow,kt.setValue(U,"receiveShadow",k.receiveShadow)),X.isMeshGouraudMaterial&&X.envMap!==null&&(li.envMap.value=Ie,li.flipEnvMap.value=Ie.isCubeTexture&&Ie.isRenderTargetTexture===!1?-1:1),X.isMeshStandardMaterial&&X.envMap===null&&V.environment!==null&&(li.envMapIntensity.value=V.environmentIntensity),fn&&(kt.setValue(U,"toneMappingExposure",S.toneMappingExposure),He.needsLights&&Mi(li,hr),ue&&X.fog===!0&&Ee.refreshFogUniforms(li,ue),Ee.refreshMaterialUniforms(li,X,q,J,p.state.transmissionRenderTarget[b.id]),xo.upload(U,ks(He),li,We)),X.isShaderMaterial&&X.uniformsNeedUpdate===!0&&(xo.upload(U,ks(He),li,We),X.uniformsNeedUpdate=!1),X.isSpriteMaterial&&kt.setValue(U,"center",k.center),kt.setValue(U,"modelViewMatrix",k.modelViewMatrix),kt.setValue(U,"normalMatrix",k.normalMatrix),kt.setValue(U,"modelMatrix",k.matrixWorld),X.isShaderMaterial||X.isRawShaderMaterial){const Rn=X.uniformsGroups;for(let Nr=0,Ea=Rn.length;Nr<Ea;Nr++){const ba=Rn[Nr];le.update(ba,Pt),le.bind(ba,Pt)}}return Pt}function Mi(b,V){b.ambientLightColor.needsUpdate=V,b.lightProbe.needsUpdate=V,b.directionalLights.needsUpdate=V,b.directionalLightShadows.needsUpdate=V,b.pointLights.needsUpdate=V,b.pointLightShadows.needsUpdate=V,b.spotLights.needsUpdate=V,b.spotLightShadows.needsUpdate=V,b.rectAreaLights.needsUpdate=V,b.hemisphereLights.needsUpdate=V}function Yo(b){return b.isMeshLambertMaterial||b.isMeshToonMaterial||b.isMeshPhongMaterial||b.isMeshStandardMaterial||b.isShadowMaterial||b.isShaderMaterial&&b.lights===!0}this.getActiveCubeFace=function(){return z},this.getActiveMipmapLevel=function(){return R},this.getRenderTarget=function(){return L},this.setRenderTargetTextures=function(b,V,$){qe.get(b.texture).__webglTexture=V,qe.get(b.depthTexture).__webglTexture=$;const X=qe.get(b);X.__hasExternalTextures=!0,X.__autoAllocateDepthBuffer=$===void 0,X.__autoAllocateDepthBuffer||nt.has("WEBGL_multisampled_render_to_texture")===!0&&(console.warn("THREE.WebGLRenderer: Render-to-texture extension was disabled because an external texture was provided"),X.__useRenderToTexture=!1)},this.setRenderTargetFramebuffer=function(b,V){const $=qe.get(b);$.__webglFramebuffer=V,$.__useDefaultFramebuffer=V===void 0},this.setRenderTarget=function(b,V=0,$=0){L=b,z=V,R=$;let X=!0,k=null,ue=!1,Ce=!1;if(b){const Ie=qe.get(b);if(Ie.__useDefaultFramebuffer!==void 0)Fe.bindFramebuffer(U.FRAMEBUFFER,null),X=!1;else if(Ie.__webglFramebuffer===void 0)We.setupRenderTarget(b);else if(Ie.__hasExternalTextures)We.rebindTextures(b,qe.get(b.texture).__webglTexture,qe.get(b.depthTexture).__webglTexture);else if(b.depthBuffer){const Oe=b.depthTexture;if(Ie.__boundDepthTexture!==Oe){if(Oe!==null&&qe.has(Oe)&&(b.width!==Oe.image.width||b.height!==Oe.image.height))throw new Error("WebGLRenderTarget: Attached DepthTexture is initialized to the incorrect size.");We.setupDepthRenderbuffer(b)}}const Ze=b.texture;(Ze.isData3DTexture||Ze.isDataArrayTexture||Ze.isCompressedArrayTexture)&&(Ce=!0);const Je=qe.get(b).__webglFramebuffer;b.isWebGLCubeRenderTarget?(Array.isArray(Je[V])?k=Je[V][$]:k=Je[V],ue=!0):b.samples>0&&We.useMultisampledRTT(b)===!1?k=qe.get(b).__webglMultisampledFramebuffer:Array.isArray(Je)?k=Je[$]:k=Je,x.copy(b.viewport),C.copy(b.scissor),j=b.scissorTest}else x.copy(he).multiplyScalar(q).floor(),C.copy(ve).multiplyScalar(q).floor(),j=Te;if(Fe.bindFramebuffer(U.FRAMEBUFFER,k)&&X&&Fe.drawBuffers(b,k),Fe.viewport(x),Fe.scissor(C),Fe.setScissorTest(j),ue){const Ie=qe.get(b.texture);U.framebufferTexture2D(U.FRAMEBUFFER,U.COLOR_ATTACHMENT0,U.TEXTURE_CUBE_MAP_POSITIVE_X+V,Ie.__webglTexture,$)}else if(Ce){const Ie=qe.get(b.texture),Ze=V||0;U.framebufferTextureLayer(U.FRAMEBUFFER,U.COLOR_ATTACHMENT0,Ie.__webglTexture,$||0,Ze)}O=-1},this.readRenderTargetPixels=function(b,V,$,X,k,ue,Ce){if(!(b&&b.isWebGLRenderTarget)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");return}let Pe=qe.get(b).__webglFramebuffer;if(b.isWebGLCubeRenderTarget&&Ce!==void 0&&(Pe=Pe[Ce]),Pe){Fe.bindFramebuffer(U.FRAMEBUFFER,Pe);try{const Ie=b.texture,Ze=Ie.format,Je=Ie.type;if(!ot.textureFormatReadable(Ze)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in RGBA or implementation defined format.");return}if(!ot.textureTypeReadable(Je)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in UnsignedByteType or implementation defined type.");return}V>=0&&V<=b.width-X&&$>=0&&$<=b.height-k&&U.readPixels(V,$,X,k,ke.convert(Ze),ke.convert(Je),ue)}finally{const Ie=L!==null?qe.get(L).__webglFramebuffer:null;Fe.bindFramebuffer(U.FRAMEBUFFER,Ie)}}},this.readRenderTargetPixelsAsync=async function(b,V,$,X,k,ue,Ce){if(!(b&&b.isWebGLRenderTarget))throw new Error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");let Pe=qe.get(b).__webglFramebuffer;if(b.isWebGLCubeRenderTarget&&Ce!==void 0&&(Pe=Pe[Ce]),Pe){Fe.bindFramebuffer(U.FRAMEBUFFER,Pe);try{const Ie=b.texture,Ze=Ie.format,Je=Ie.type;if(!ot.textureFormatReadable(Ze))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in RGBA or implementation defined format.");if(!ot.textureTypeReadable(Je))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in UnsignedByteType or implementation defined type.");if(V>=0&&V<=b.width-X&&$>=0&&$<=b.height-k){const Oe=U.createBuffer();U.bindBuffer(U.PIXEL_PACK_BUFFER,Oe),U.bufferData(U.PIXEL_PACK_BUFFER,ue.byteLength,U.STREAM_READ),U.readPixels(V,$,X,k,ke.convert(Ze),ke.convert(Je),0),U.flush();const lt=U.fenceSync(U.SYNC_GPU_COMMANDS_COMPLETE,0);await Xm(U,lt,4);try{U.bindBuffer(U.PIXEL_PACK_BUFFER,Oe),U.getBufferSubData(U.PIXEL_PACK_BUFFER,0,ue)}finally{U.deleteBuffer(Oe),U.deleteSync(lt)}return ue}}finally{const Ie=L!==null?qe.get(L).__webglFramebuffer:null;Fe.bindFramebuffer(U.FRAMEBUFFER,Ie)}}},this.copyFramebufferToTexture=function(b,V=null,$=0){b.isTexture!==!0&&(ys("WebGLRenderer: copyFramebufferToTexture function signature has changed."),V=arguments[0]||null,b=arguments[1]);const X=Math.pow(2,-$),k=Math.floor(b.image.width*X),ue=Math.floor(b.image.height*X),Ce=V!==null?V.x:0,Pe=V!==null?V.y:0;We.setTexture2D(b,0),U.copyTexSubImage2D(U.TEXTURE_2D,$,0,0,Ce,Pe,k,ue),Fe.unbindTexture()},this.copyTextureToTexture=function(b,V,$=null,X=null,k=0){b.isTexture!==!0&&(ys("WebGLRenderer: copyTextureToTexture function signature has changed."),X=arguments[0]||null,b=arguments[1],V=arguments[2],k=arguments[3]||0,$=null);let ue,Ce,Pe,Ie,Ze,Je;$!==null?(ue=$.max.x-$.min.x,Ce=$.max.y-$.min.y,Pe=$.min.x,Ie=$.min.y):(ue=b.image.width,Ce=b.image.height,Pe=0,Ie=0),X!==null?(Ze=X.x,Je=X.y):(Ze=0,Je=0);const Oe=ke.convert(V.format),lt=ke.convert(V.type);We.setTexture2D(V,0),U.pixelStorei(U.UNPACK_FLIP_Y_WEBGL,V.flipY),U.pixelStorei(U.UNPACK_PREMULTIPLY_ALPHA_WEBGL,V.premultiplyAlpha),U.pixelStorei(U.UNPACK_ALIGNMENT,V.unpackAlignment);const Rt=U.getParameter(U.UNPACK_ROW_LENGTH),Ct=U.getParameter(U.UNPACK_IMAGE_HEIGHT),hn=U.getParameter(U.UNPACK_SKIP_PIXELS),ft=U.getParameter(U.UNPACK_SKIP_ROWS),He=U.getParameter(U.UNPACK_SKIP_IMAGES),Gt=b.isCompressedTexture?b.mipmaps[k]:b.image;U.pixelStorei(U.UNPACK_ROW_LENGTH,Gt.width),U.pixelStorei(U.UNPACK_IMAGE_HEIGHT,Gt.height),U.pixelStorei(U.UNPACK_SKIP_PIXELS,Pe),U.pixelStorei(U.UNPACK_SKIP_ROWS,Ie),b.isDataTexture?U.texSubImage2D(U.TEXTURE_2D,k,Ze,Je,ue,Ce,Oe,lt,Gt.data):b.isCompressedTexture?U.compressedTexSubImage2D(U.TEXTURE_2D,k,Ze,Je,Gt.width,Gt.height,Oe,Gt.data):U.texSubImage2D(U.TEXTURE_2D,k,Ze,Je,ue,Ce,Oe,lt,Gt),U.pixelStorei(U.UNPACK_ROW_LENGTH,Rt),U.pixelStorei(U.UNPACK_IMAGE_HEIGHT,Ct),U.pixelStorei(U.UNPACK_SKIP_PIXELS,hn),U.pixelStorei(U.UNPACK_SKIP_ROWS,ft),U.pixelStorei(U.UNPACK_SKIP_IMAGES,He),k===0&&V.generateMipmaps&&U.generateMipmap(U.TEXTURE_2D),Fe.unbindTexture()},this.copyTextureToTexture3D=function(b,V,$=null,X=null,k=0){b.isTexture!==!0&&(ys("WebGLRenderer: copyTextureToTexture3D function signature has changed."),$=arguments[0]||null,X=arguments[1]||null,b=arguments[2],V=arguments[3],k=arguments[4]||0);let ue,Ce,Pe,Ie,Ze,Je,Oe,lt,Rt;const Ct=b.isCompressedTexture?b.mipmaps[k]:b.image;$!==null?(ue=$.max.x-$.min.x,Ce=$.max.y-$.min.y,Pe=$.max.z-$.min.z,Ie=$.min.x,Ze=$.min.y,Je=$.min.z):(ue=Ct.width,Ce=Ct.height,Pe=Ct.depth,Ie=0,Ze=0,Je=0),X!==null?(Oe=X.x,lt=X.y,Rt=X.z):(Oe=0,lt=0,Rt=0);const hn=ke.convert(V.format),ft=ke.convert(V.type);let He;if(V.isData3DTexture)We.setTexture3D(V,0),He=U.TEXTURE_3D;else if(V.isDataArrayTexture||V.isCompressedArrayTexture)We.setTexture2DArray(V,0),He=U.TEXTURE_2D_ARRAY;else{console.warn("THREE.WebGLRenderer.copyTextureToTexture3D: only supports THREE.DataTexture3D and THREE.DataTexture2DArray.");return}U.pixelStorei(U.UNPACK_FLIP_Y_WEBGL,V.flipY),U.pixelStorei(U.UNPACK_PREMULTIPLY_ALPHA_WEBGL,V.premultiplyAlpha),U.pixelStorei(U.UNPACK_ALIGNMENT,V.unpackAlignment);const Gt=U.getParameter(U.UNPACK_ROW_LENGTH),pt=U.getParameter(U.UNPACK_IMAGE_HEIGHT),Pt=U.getParameter(U.UNPACK_SKIP_PIXELS),Si=U.getParameter(U.UNPACK_SKIP_ROWS),fn=U.getParameter(U.UNPACK_SKIP_IMAGES);U.pixelStorei(U.UNPACK_ROW_LENGTH,Ct.width),U.pixelStorei(U.UNPACK_IMAGE_HEIGHT,Ct.height),U.pixelStorei(U.UNPACK_SKIP_PIXELS,Ie),U.pixelStorei(U.UNPACK_SKIP_ROWS,Ze),U.pixelStorei(U.UNPACK_SKIP_IMAGES,Je),b.isDataTexture||b.isData3DTexture?U.texSubImage3D(He,k,Oe,lt,Rt,ue,Ce,Pe,hn,ft,Ct.data):V.isCompressedArrayTexture?U.compressedTexSubImage3D(He,k,Oe,lt,Rt,ue,Ce,Pe,hn,Ct.data):U.texSubImage3D(He,k,Oe,lt,Rt,ue,Ce,Pe,hn,ft,Ct),U.pixelStorei(U.UNPACK_ROW_LENGTH,Gt),U.pixelStorei(U.UNPACK_IMAGE_HEIGHT,pt),U.pixelStorei(U.UNPACK_SKIP_PIXELS,Pt),U.pixelStorei(U.UNPACK_SKIP_ROWS,Si),U.pixelStorei(U.UNPACK_SKIP_IMAGES,fn),k===0&&V.generateMipmaps&&U.generateMipmap(He),Fe.unbindTexture()},this.initRenderTarget=function(b){qe.get(b).__webglFramebuffer===void 0&&We.setupRenderTarget(b)},this.initTexture=function(b){b.isCubeTexture?We.setTextureCube(b,0):b.isData3DTexture?We.setTexture3D(b,0):b.isDataArrayTexture||b.isCompressedArrayTexture?We.setTexture2DArray(b,0):We.setTexture2D(b,0),Fe.unbindTexture()},this.resetState=function(){z=0,R=0,L=null,Fe.reset(),N.reset()},typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}get coordinateSystem(){return Di}get outputColorSpace(){return this._outputColorSpace}set outputColorSpace(e){this._outputColorSpace=e;const t=this.getContext();t.drawingBufferColorSpace=e===$c?"display-p3":"srgb",t.unpackColorSpace=Mt.workingColorSpace===Uo?"display-p3":"srgb"}}class Qc{constructor(e,t=25e-5){this.isFogExp2=!0,this.name="",this.color=new tt(e),this.density=t}clone(){return new Qc(this.color,this.density)}toJSON(){return{type:"FogExp2",name:this.name,color:this.color.getHex(),density:this.density}}}class eu extends $t{constructor(){super(),this.isScene=!0,this.type="Scene",this.background=null,this.environment=null,this.fog=null,this.backgroundBlurriness=0,this.backgroundIntensity=1,this.backgroundRotation=new _i,this.environmentIntensity=1,this.environmentRotation=new _i,this.overrideMaterial=null,typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}copy(e,t){return super.copy(e,t),e.background!==null&&(this.background=e.background.clone()),e.environment!==null&&(this.environment=e.environment.clone()),e.fog!==null&&(this.fog=e.fog.clone()),this.backgroundBlurriness=e.backgroundBlurriness,this.backgroundIntensity=e.backgroundIntensity,this.backgroundRotation.copy(e.backgroundRotation),this.environmentIntensity=e.environmentIntensity,this.environmentRotation.copy(e.environmentRotation),e.overrideMaterial!==null&&(this.overrideMaterial=e.overrideMaterial.clone()),this.matrixAutoUpdate=e.matrixAutoUpdate,this}toJSON(e){const t=super.toJSON(e);return this.fog!==null&&(t.object.fog=this.fog.toJSON()),this.backgroundBlurriness>0&&(t.object.backgroundBlurriness=this.backgroundBlurriness),this.backgroundIntensity!==1&&(t.object.backgroundIntensity=this.backgroundIntensity),t.object.backgroundRotation=this.backgroundRotation.toArray(),this.environmentIntensity!==1&&(t.object.environmentIntensity=this.environmentIntensity),t.object.environmentRotation=this.environmentRotation.toArray(),t}}class ey{constructor(e,t){this.isInterleavedBuffer=!0,this.array=e,this.stride=t,this.count=e!==void 0?e.length/t:0,this.usage=bc,this._updateRange={offset:0,count:-1},this.updateRanges=[],this.version=0,this.uuid=Ui()}onUploadCallback(){}set needsUpdate(e){e===!0&&this.version++}get updateRange(){return ys("THREE.InterleavedBuffer: updateRange() is deprecated and will be removed in r169. Use addUpdateRange() instead."),this._updateRange}setUsage(e){return this.usage=e,this}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}copy(e){return this.array=new e.array.constructor(e.array),this.count=e.count,this.stride=e.stride,this.usage=e.usage,this}copyAt(e,t,n){e*=this.stride,n*=t.stride;for(let r=0,s=this.stride;r<s;r++)this.array[e+r]=t.array[n+r];return this}set(e,t=0){return this.array.set(e,t),this}clone(e){e.arrayBuffers===void 0&&(e.arrayBuffers={}),this.array.buffer._uuid===void 0&&(this.array.buffer._uuid=Ui()),e.arrayBuffers[this.array.buffer._uuid]===void 0&&(e.arrayBuffers[this.array.buffer._uuid]=this.array.slice(0).buffer);const t=new this.array.constructor(e.arrayBuffers[this.array.buffer._uuid]),n=new this.constructor(t,this.stride);return n.setUsage(this.usage),n}onUpload(e){return this.onUploadCallback=e,this}toJSON(e){return e.arrayBuffers===void 0&&(e.arrayBuffers={}),this.array.buffer._uuid===void 0&&(this.array.buffer._uuid=Ui()),e.arrayBuffers[this.array.buffer._uuid]===void 0&&(e.arrayBuffers[this.array.buffer._uuid]=Array.from(new Uint32Array(this.array.buffer))),{uuid:this.uuid,buffer:this.array.buffer._uuid,type:this.array.constructor.name,stride:this.stride}}}const En=new H;class Ao{constructor(e,t,n,r=!1){this.isInterleavedBufferAttribute=!0,this.name="",this.data=e,this.itemSize=t,this.offset=n,this.normalized=r}get count(){return this.data.count}get array(){return this.data.array}set needsUpdate(e){this.data.needsUpdate=e}applyMatrix4(e){for(let t=0,n=this.data.count;t<n;t++)En.fromBufferAttribute(this,t),En.applyMatrix4(e),this.setXYZ(t,En.x,En.y,En.z);return this}applyNormalMatrix(e){for(let t=0,n=this.count;t<n;t++)En.fromBufferAttribute(this,t),En.applyNormalMatrix(e),this.setXYZ(t,En.x,En.y,En.z);return this}transformDirection(e){for(let t=0,n=this.count;t<n;t++)En.fromBufferAttribute(this,t),En.transformDirection(e),this.setXYZ(t,En.x,En.y,En.z);return this}getComponent(e,t){let n=this.array[e*this.data.stride+this.offset+t];return this.normalized&&(n=ni(n,this.array)),n}setComponent(e,t,n){return this.normalized&&(n=bt(n,this.array)),this.data.array[e*this.data.stride+this.offset+t]=n,this}setX(e,t){return this.normalized&&(t=bt(t,this.array)),this.data.array[e*this.data.stride+this.offset]=t,this}setY(e,t){return this.normalized&&(t=bt(t,this.array)),this.data.array[e*this.data.stride+this.offset+1]=t,this}setZ(e,t){return this.normalized&&(t=bt(t,this.array)),this.data.array[e*this.data.stride+this.offset+2]=t,this}setW(e,t){return this.normalized&&(t=bt(t,this.array)),this.data.array[e*this.data.stride+this.offset+3]=t,this}getX(e){let t=this.data.array[e*this.data.stride+this.offset];return this.normalized&&(t=ni(t,this.array)),t}getY(e){let t=this.data.array[e*this.data.stride+this.offset+1];return this.normalized&&(t=ni(t,this.array)),t}getZ(e){let t=this.data.array[e*this.data.stride+this.offset+2];return this.normalized&&(t=ni(t,this.array)),t}getW(e){let t=this.data.array[e*this.data.stride+this.offset+3];return this.normalized&&(t=ni(t,this.array)),t}setXY(e,t,n){return e=e*this.data.stride+this.offset,this.normalized&&(t=bt(t,this.array),n=bt(n,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this}setXYZ(e,t,n,r){return e=e*this.data.stride+this.offset,this.normalized&&(t=bt(t,this.array),n=bt(n,this.array),r=bt(r,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this.data.array[e+2]=r,this}setXYZW(e,t,n,r,s){return e=e*this.data.stride+this.offset,this.normalized&&(t=bt(t,this.array),n=bt(n,this.array),r=bt(r,this.array),s=bt(s,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this.data.array[e+2]=r,this.data.array[e+3]=s,this}clone(e){if(e===void 0){console.log("THREE.InterleavedBufferAttribute.clone(): Cloning an interleaved buffer attribute will de-interleave buffer data.");const t=[];for(let n=0;n<this.count;n++){const r=n*this.data.stride+this.offset;for(let s=0;s<this.itemSize;s++)t.push(this.data.array[r+s])}return new si(new this.array.constructor(t),this.itemSize,this.normalized)}else return e.interleavedBuffers===void 0&&(e.interleavedBuffers={}),e.interleavedBuffers[this.data.uuid]===void 0&&(e.interleavedBuffers[this.data.uuid]=this.data.clone(e)),new Ao(e.interleavedBuffers[this.data.uuid],this.itemSize,this.offset,this.normalized)}toJSON(e){if(e===void 0){console.log("THREE.InterleavedBufferAttribute.toJSON(): Serializing an interleaved buffer attribute will de-interleave buffer data.");const t=[];for(let n=0;n<this.count;n++){const r=n*this.data.stride+this.offset;for(let s=0;s<this.itemSize;s++)t.push(this.data.array[r+s])}return{itemSize:this.itemSize,type:this.array.constructor.name,array:t,normalized:this.normalized}}else return e.interleavedBuffers===void 0&&(e.interleavedBuffers={}),e.interleavedBuffers[this.data.uuid]===void 0&&(e.interleavedBuffers[this.data.uuid]=this.data.toJSON(e)),{isInterleavedBufferAttribute:!0,itemSize:this.itemSize,data:this.data.uuid,offset:this.offset,normalized:this.normalized}}}class Ac extends cr{constructor(e){super(),this.isSpriteMaterial=!0,this.type="SpriteMaterial",this.color=new tt(16777215),this.map=null,this.alphaMap=null,this.rotation=0,this.sizeAttenuation=!0,this.transparent=!0,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.alphaMap=e.alphaMap,this.rotation=e.rotation,this.sizeAttenuation=e.sizeAttenuation,this.fog=e.fog,this}}let us;const Js=new H,hs=new H,ds=new H,fs=new Xe,Qs=new Xe,Sf=new Ft,Qa=new H,ea=new H,eo=new H,Bh=new Xe,Dl=new Xe,zh=new Xe;class ty extends $t{constructor(e=new Ac){if(super(),this.isSprite=!0,this.type="Sprite",us===void 0){us=new ln;const t=new Float32Array([-.5,-.5,0,0,0,.5,-.5,0,1,0,.5,.5,0,1,1,-.5,.5,0,0,1]),n=new ey(t,5);us.setIndex([0,1,2,0,2,3]),us.setAttribute("position",new Ao(n,3,0,!1)),us.setAttribute("uv",new Ao(n,2,3,!1))}this.geometry=us,this.material=e,this.center=new Xe(.5,.5)}raycast(e,t){e.camera===null&&console.error('THREE.Sprite: "Raycaster.camera" needs to be set in order to raycast against sprites.'),hs.setFromMatrixScale(this.matrixWorld),Sf.copy(e.camera.matrixWorld),this.modelViewMatrix.multiplyMatrices(e.camera.matrixWorldInverse,this.matrixWorld),ds.setFromMatrixPosition(this.modelViewMatrix),e.camera.isPerspectiveCamera&&this.material.sizeAttenuation===!1&&hs.multiplyScalar(-ds.z);const n=this.material.rotation;let r,s;n!==0&&(s=Math.cos(n),r=Math.sin(n));const a=this.center;to(Qa.set(-.5,-.5,0),ds,a,hs,r,s),to(ea.set(.5,-.5,0),ds,a,hs,r,s),to(eo.set(.5,.5,0),ds,a,hs,r,s),Bh.set(0,0),Dl.set(1,0),zh.set(1,1);let o=e.ray.intersectTriangle(Qa,ea,eo,!1,Js);if(o===null&&(to(ea.set(-.5,.5,0),ds,a,hs,r,s),Dl.set(0,1),o=e.ray.intersectTriangle(Qa,eo,ea,!1,Js),o===null))return;const l=e.ray.origin.distanceTo(Js);l<e.near||l>e.far||t.push({distance:l,point:Js.clone(),uv:Wn.getInterpolation(Js,Qa,ea,eo,Bh,Dl,zh,new Xe),face:null,object:this})}copy(e,t){return super.copy(e,t),e.center!==void 0&&this.center.copy(e.center),this.material=e.material,this}}function to(i,e,t,n,r,s){fs.subVectors(i,t).addScalar(.5).multiply(n),r!==void 0?(Qs.x=s*fs.x-r*fs.y,Qs.y=r*fs.x+s*fs.y):Qs.copy(fs),i.copy(e),i.x+=Qs.x,i.y+=Qs.y,i.applyMatrix4(Sf)}class tr extends cr{constructor(e){super(),this.isLineBasicMaterial=!0,this.type="LineBasicMaterial",this.color=new tt(16777215),this.map=null,this.linewidth=1,this.linecap="round",this.linejoin="round",this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.linewidth=e.linewidth,this.linecap=e.linecap,this.linejoin=e.linejoin,this.fog=e.fog,this}}const Ro=new H,Co=new H,kh=new Ft,ta=new Ma,no=new ya,Il=new H,Hh=new H;class Rc extends $t{constructor(e=new ln,t=new tr){super(),this.isLine=!0,this.type="Line",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}computeLineDistances(){const e=this.geometry;if(e.index===null){const t=e.attributes.position,n=[0];for(let r=1,s=t.count;r<s;r++)Ro.fromBufferAttribute(t,r-1),Co.fromBufferAttribute(t,r),n[r]=n[r-1],n[r]+=Ro.distanceTo(Co);e.setAttribute("lineDistance",new vn(n,1))}else console.warn("THREE.Line.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.");return this}raycast(e,t){const n=this.geometry,r=this.matrixWorld,s=e.params.Line.threshold,a=n.drawRange;if(n.boundingSphere===null&&n.computeBoundingSphere(),no.copy(n.boundingSphere),no.applyMatrix4(r),no.radius+=s,e.ray.intersectsSphere(no)===!1)return;kh.copy(r).invert(),ta.copy(e.ray).applyMatrix4(kh);const o=s/((this.scale.x+this.scale.y+this.scale.z)/3),l=o*o,c=this.isLineSegments?2:1,u=n.index,d=n.attributes.position;if(u!==null){const m=Math.max(0,a.start),_=Math.min(u.count,a.start+a.count);for(let v=m,p=_-1;v<p;v+=c){const f=u.getX(v),E=u.getX(v+1),S=io(this,e,ta,l,f,E);S&&t.push(S)}if(this.isLineLoop){const v=u.getX(_-1),p=u.getX(m),f=io(this,e,ta,l,v,p);f&&t.push(f)}}else{const m=Math.max(0,a.start),_=Math.min(d.count,a.start+a.count);for(let v=m,p=_-1;v<p;v+=c){const f=io(this,e,ta,l,v,v+1);f&&t.push(f)}if(this.isLineLoop){const v=io(this,e,ta,l,_-1,m);v&&t.push(v)}}}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const r=t[n[0]];if(r!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let s=0,a=r.length;s<a;s++){const o=r[s].name||String(s);this.morphTargetInfluences.push(0),this.morphTargetDictionary[o]=s}}}}}function io(i,e,t,n,r,s){const a=i.geometry.attributes.position;if(Ro.fromBufferAttribute(a,r),Co.fromBufferAttribute(a,s),t.distanceSqToSegment(Ro,Co,Il,Hh)>n)return;Il.applyMatrix4(i.matrixWorld);const l=e.ray.origin.distanceTo(Il);if(!(l<e.near||l>e.far))return{distance:l,point:Hh.clone().applyMatrix4(i.matrixWorld),index:r,face:null,faceIndex:null,object:i}}const Vh=new H,Gh=new H;class ha extends Rc{constructor(e,t){super(e,t),this.isLineSegments=!0,this.type="LineSegments"}computeLineDistances(){const e=this.geometry;if(e.index===null){const t=e.attributes.position,n=[];for(let r=0,s=t.count;r<s;r+=2)Vh.fromBufferAttribute(t,r),Gh.fromBufferAttribute(t,r+1),n[r]=r===0?0:n[r-1],n[r+1]=n[r]+Vh.distanceTo(Gh);e.setAttribute("lineDistance",new vn(n,1))}else console.warn("THREE.LineSegments.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.");return this}}class Ef extends cr{constructor(e){super(),this.isPointsMaterial=!0,this.type="PointsMaterial",this.color=new tt(16777215),this.map=null,this.alphaMap=null,this.size=1,this.sizeAttenuation=!0,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.alphaMap=e.alphaMap,this.size=e.size,this.sizeAttenuation=e.sizeAttenuation,this.fog=e.fog,this}}const Wh=new Ft,Cc=new Ma,ro=new ya,so=new H;class ny extends $t{constructor(e=new ln,t=new Ef){super(),this.isPoints=!0,this.type="Points",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}raycast(e,t){const n=this.geometry,r=this.matrixWorld,s=e.params.Points.threshold,a=n.drawRange;if(n.boundingSphere===null&&n.computeBoundingSphere(),ro.copy(n.boundingSphere),ro.applyMatrix4(r),ro.radius+=s,e.ray.intersectsSphere(ro)===!1)return;Wh.copy(r).invert(),Cc.copy(e.ray).applyMatrix4(Wh);const o=s/((this.scale.x+this.scale.y+this.scale.z)/3),l=o*o,c=n.index,h=n.attributes.position;if(c!==null){const d=Math.max(0,a.start),m=Math.min(c.count,a.start+a.count);for(let _=d,v=m;_<v;_++){const p=c.getX(_);so.fromBufferAttribute(h,p),Xh(so,p,l,r,e,t,this)}}else{const d=Math.max(0,a.start),m=Math.min(h.count,a.start+a.count);for(let _=d,v=m;_<v;_++)so.fromBufferAttribute(h,_),Xh(so,_,l,r,e,t,this)}}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const r=t[n[0]];if(r!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let s=0,a=r.length;s<a;s++){const o=r[s].name||String(s);this.morphTargetInfluences.push(0),this.morphTargetDictionary[o]=s}}}}}function Xh(i,e,t,n,r,s,a){const o=Cc.distanceSqToPoint(i);if(o<t){const l=new H;Cc.closestPointToPoint(i,l),l.applyMatrix4(n);const c=r.ray.origin.distanceTo(l);if(c<r.near||c>r.far)return;s.push({distance:c,distanceToRay:Math.sqrt(o),point:l,index:e,face:null,object:a})}}class iy extends An{constructor(e,t,n,r,s,a,o,l,c){super(e,t,n,r,s,a,o,l,c),this.isCanvasTexture=!0,this.needsUpdate=!0}}const ao=new H,oo=new H,Ul=new H,lo=new Wn;class ry extends ln{constructor(e=null,t=1){if(super(),this.type="EdgesGeometry",this.parameters={geometry:e,thresholdAngle:t},e!==null){const r=Math.pow(10,4),s=Math.cos(xs*t),a=e.getIndex(),o=e.getAttribute("position"),l=a?a.count:o.count,c=[0,0,0],u=["a","b","c"],h=new Array(3),d={},m=[];for(let _=0;_<l;_+=3){a?(c[0]=a.getX(_),c[1]=a.getX(_+1),c[2]=a.getX(_+2)):(c[0]=_,c[1]=_+1,c[2]=_+2);const{a:v,b:p,c:f}=lo;if(v.fromBufferAttribute(o,c[0]),p.fromBufferAttribute(o,c[1]),f.fromBufferAttribute(o,c[2]),lo.getNormal(Ul),h[0]=`${Math.round(v.x*r)},${Math.round(v.y*r)},${Math.round(v.z*r)}`,h[1]=`${Math.round(p.x*r)},${Math.round(p.y*r)},${Math.round(p.z*r)}`,h[2]=`${Math.round(f.x*r)},${Math.round(f.y*r)},${Math.round(f.z*r)}`,!(h[0]===h[1]||h[1]===h[2]||h[2]===h[0]))for(let E=0;E<3;E++){const S=(E+1)%3,T=h[E],z=h[S],R=lo[u[E]],L=lo[u[S]],O=`${T}_${z}`,w=`${z}_${T}`;w in d&&d[w]?(Ul.dot(d[w].normal)<=s&&(m.push(R.x,R.y,R.z),m.push(L.x,L.y,L.z)),d[w]=null):O in d||(d[O]={index0:c[E],index1:c[S],normal:Ul.clone()})}}for(const _ in d)if(d[_]){const{index0:v,index1:p}=d[_];ao.fromBufferAttribute(o,v),oo.fromBufferAttribute(o,p),m.push(ao.x,ao.y,ao.z),m.push(oo.x,oo.y,oo.z)}this.setAttribute("position",new vn(m,3))}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}}class tu extends ln{constructor(e=.5,t=1,n=32,r=1,s=0,a=Math.PI*2){super(),this.type="RingGeometry",this.parameters={innerRadius:e,outerRadius:t,thetaSegments:n,phiSegments:r,thetaStart:s,thetaLength:a},n=Math.max(3,n),r=Math.max(1,r);const o=[],l=[],c=[],u=[];let h=e;const d=(t-e)/r,m=new H,_=new Xe;for(let v=0;v<=r;v++){for(let p=0;p<=n;p++){const f=s+p/n*a;m.x=h*Math.cos(f),m.y=h*Math.sin(f),l.push(m.x,m.y,m.z),c.push(0,0,1),_.x=(m.x/t+1)/2,_.y=(m.y/t+1)/2,u.push(_.x,_.y)}h+=d}for(let v=0;v<r;v++){const p=v*(n+1);for(let f=0;f<n;f++){const E=f+p,S=E,T=E+n+1,z=E+n+2,R=E+1;o.push(S,T,R),o.push(T,z,R)}}this.setIndex(o),this.setAttribute("position",new vn(l,3)),this.setAttribute("normal",new vn(c,3)),this.setAttribute("uv",new vn(u,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new tu(e.innerRadius,e.outerRadius,e.thetaSegments,e.phiSegments,e.thetaStart,e.thetaLength)}}class Nl extends cr{constructor(e){super(),this.isMeshStandardMaterial=!0,this.defines={STANDARD:""},this.type="MeshStandardMaterial",this.color=new tt(16777215),this.roughness=1,this.metalness=0,this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.emissive=new tt(0),this.emissiveIntensity=1,this.emissiveMap=null,this.bumpMap=null,this.bumpScale=1,this.normalMap=null,this.normalMapType=rf,this.normalScale=new Xe(1,1),this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.roughnessMap=null,this.metalnessMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new _i,this.envMapIntensity=1,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.flatShading=!1,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.defines={STANDARD:""},this.color.copy(e.color),this.roughness=e.roughness,this.metalness=e.metalness,this.map=e.map,this.lightMap=e.lightMap,this.lightMapIntensity=e.lightMapIntensity,this.aoMap=e.aoMap,this.aoMapIntensity=e.aoMapIntensity,this.emissive.copy(e.emissive),this.emissiveMap=e.emissiveMap,this.emissiveIntensity=e.emissiveIntensity,this.bumpMap=e.bumpMap,this.bumpScale=e.bumpScale,this.normalMap=e.normalMap,this.normalMapType=e.normalMapType,this.normalScale.copy(e.normalScale),this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this.roughnessMap=e.roughnessMap,this.metalnessMap=e.metalnessMap,this.alphaMap=e.alphaMap,this.envMap=e.envMap,this.envMapRotation.copy(e.envMapRotation),this.envMapIntensity=e.envMapIntensity,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.wireframeLinecap=e.wireframeLinecap,this.wireframeLinejoin=e.wireframeLinejoin,this.flatShading=e.flatShading,this.fog=e.fog,this}}class sy extends tr{constructor(e){super(),this.isLineDashedMaterial=!0,this.type="LineDashedMaterial",this.scale=1,this.dashSize=3,this.gapSize=1,this.setValues(e)}copy(e){return super.copy(e),this.scale=e.scale,this.dashSize=e.dashSize,this.gapSize=e.gapSize,this}}class nu extends $t{constructor(e,t=1){super(),this.isLight=!0,this.type="Light",this.color=new tt(e),this.intensity=t}dispose(){}copy(e,t){return super.copy(e,t),this.color.copy(e.color),this.intensity=e.intensity,this}toJSON(e){const t=super.toJSON(e);return t.object.color=this.color.getHex(),t.object.intensity=this.intensity,this.groundColor!==void 0&&(t.object.groundColor=this.groundColor.getHex()),this.distance!==void 0&&(t.object.distance=this.distance),this.angle!==void 0&&(t.object.angle=this.angle),this.decay!==void 0&&(t.object.decay=this.decay),this.penumbra!==void 0&&(t.object.penumbra=this.penumbra),this.shadow!==void 0&&(t.object.shadow=this.shadow.toJSON()),this.target!==void 0&&(t.object.target=this.target.uuid),t}}class ay extends nu{constructor(e,t,n){super(e,n),this.isHemisphereLight=!0,this.type="HemisphereLight",this.position.copy($t.DEFAULT_UP),this.updateMatrix(),this.groundColor=new tt(t)}copy(e,t){return super.copy(e,t),this.groundColor.copy(e.groundColor),this}}const Fl=new Ft,qh=new H,Yh=new H;class oy{constructor(e){this.camera=e,this.intensity=1,this.bias=0,this.normalBias=0,this.radius=1,this.blurSamples=8,this.mapSize=new Xe(512,512),this.map=null,this.mapPass=null,this.matrix=new Ft,this.autoUpdate=!0,this.needsUpdate=!1,this._frustum=new Zc,this._frameExtents=new Xe(1,1),this._viewportCount=1,this._viewports=[new Zt(0,0,1,1)]}getViewportCount(){return this._viewportCount}getFrustum(){return this._frustum}updateMatrices(e){const t=this.camera,n=this.matrix;qh.setFromMatrixPosition(e.matrixWorld),t.position.copy(qh),Yh.setFromMatrixPosition(e.target.matrixWorld),t.lookAt(Yh),t.updateMatrixWorld(),Fl.multiplyMatrices(t.projectionMatrix,t.matrixWorldInverse),this._frustum.setFromProjectionMatrix(Fl),n.set(.5,0,0,.5,0,.5,0,.5,0,0,.5,.5,0,0,0,1),n.multiply(Fl)}getViewport(e){return this._viewports[e]}getFrameExtents(){return this._frameExtents}dispose(){this.map&&this.map.dispose(),this.mapPass&&this.mapPass.dispose()}copy(e){return this.camera=e.camera.clone(),this.intensity=e.intensity,this.bias=e.bias,this.radius=e.radius,this.mapSize.copy(e.mapSize),this}clone(){return new this.constructor().copy(this)}toJSON(){const e={};return this.intensity!==1&&(e.intensity=this.intensity),this.bias!==0&&(e.bias=this.bias),this.normalBias!==0&&(e.normalBias=this.normalBias),this.radius!==1&&(e.radius=this.radius),(this.mapSize.x!==512||this.mapSize.y!==512)&&(e.mapSize=this.mapSize.toArray()),e.camera=this.camera.toJSON(!1).object,delete e.camera.matrix,e}}class ly extends oy{constructor(){super(new Ss(-5,5,5,-5,.5,500)),this.isDirectionalLightShadow=!0}}class cy extends nu{constructor(e,t){super(e,t),this.isDirectionalLight=!0,this.type="DirectionalLight",this.position.copy($t.DEFAULT_UP),this.updateMatrix(),this.target=new $t,this.shadow=new ly}dispose(){this.shadow.dispose()}copy(e){return super.copy(e),this.target=e.target.clone(),this.shadow=e.shadow.clone(),this}}class uy extends nu{constructor(e,t){super(e,t),this.isAmbientLight=!0,this.type="AmbientLight"}}const $h=new Ft;class hy{constructor(e,t,n=0,r=1/0){this.ray=new Ma(e,t),this.near=n,this.far=r,this.camera=null,this.layers=new Kc,this.params={Mesh:{},Line:{threshold:1},LOD:{},Points:{threshold:1},Sprite:{}}}set(e,t){this.ray.set(e,t)}setFromCamera(e,t){t.isPerspectiveCamera?(this.ray.origin.setFromMatrixPosition(t.matrixWorld),this.ray.direction.set(e.x,e.y,.5).unproject(t).sub(this.ray.origin).normalize(),this.camera=t):t.isOrthographicCamera?(this.ray.origin.set(e.x,e.y,(t.near+t.far)/(t.near-t.far)).unproject(t),this.ray.direction.set(0,0,-1).transformDirection(t.matrixWorld),this.camera=t):console.error("THREE.Raycaster: Unsupported camera type: "+t.type)}setFromXRController(e){return $h.identity().extractRotation(e.matrixWorld),this.ray.origin.setFromMatrixPosition(e.matrixWorld),this.ray.direction.set(0,0,-1).applyMatrix4($h),this}intersectObject(e,t=!0,n=[]){return Pc(e,this,n,t),n.sort(jh),n}intersectObjects(e,t=!0,n=[]){for(let r=0,s=e.length;r<s;r++)Pc(e[r],this,n,t);return n.sort(jh),n}}function jh(i,e){return i.distance-e.distance}function Pc(i,e,t,n){let r=!0;if(i.layers.test(e.layers)&&i.raycast(e,t)===!1&&(r=!1),r===!0&&n===!0){const s=i.children;for(let a=0,o=s.length;a<o;a++)Pc(s[a],e,t,!0)}}class Kh{constructor(e=1,t=0,n=0){return this.radius=e,this.phi=t,this.theta=n,this}set(e,t,n){return this.radius=e,this.phi=t,this.theta=n,this}copy(e){return this.radius=e.radius,this.phi=e.phi,this.theta=e.theta,this}makeSafe(){return this.phi=Math.max(1e-6,Math.min(Math.PI-1e-6,this.phi)),this}setFromVector3(e){return this.setFromCartesianCoords(e.x,e.y,e.z)}setFromCartesianCoords(e,t,n){return this.radius=Math.sqrt(e*e+t*t+n*n),this.radius===0?(this.theta=0,this.phi=0):(this.theta=Math.atan2(e,n),this.phi=Math.acos(gn(t/this.radius,-1,1))),this}clone(){return new this.constructor().copy(this)}}class dy extends ha{constructor(e=10,t=10,n=4473924,r=8947848){n=new tt(n),r=new tt(r);const s=t/2,a=e/t,o=e/2,l=[],c=[];for(let d=0,m=0,_=-o;d<=t;d++,_+=a){l.push(-o,0,_,o,0,_),l.push(_,0,-o,_,0,o);const v=d===s?n:r;v.toArray(c,m),m+=3,v.toArray(c,m),m+=3,v.toArray(c,m),m+=3,v.toArray(c,m),m+=3}const u=new ln;u.setAttribute("position",new vn(l,3)),u.setAttribute("color",new vn(c,3));const h=new tr({vertexColors:!0,toneMapped:!1});super(u,h),this.type="GridHelper"}dispose(){this.geometry.dispose(),this.material.dispose()}}typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("register",{detail:{revision:Hc}}));typeof window<"u"&&(window.__THREE__?console.warn("WARNING: Multiple instances of Three.js being imported."):window.__THREE__=Hc);var fy=Object.defineProperty,py=(i,e,t)=>e in i?fy(i,e,{enumerable:!0,configurable:!0,writable:!0,value:t}):i[e]=t,my=(i,e,t)=>(py(i,e+"",t),t);class gy{constructor(){my(this,"_listeners")}addEventListener(e,t){this._listeners===void 0&&(this._listeners={});const n=this._listeners;n[e]===void 0&&(n[e]=[]),n[e].indexOf(t)===-1&&n[e].push(t)}hasEventListener(e,t){if(this._listeners===void 0)return!1;const n=this._listeners;return n[e]!==void 0&&n[e].indexOf(t)!==-1}removeEventListener(e,t){if(this._listeners===void 0)return;const r=this._listeners[e];if(r!==void 0){const s=r.indexOf(t);s!==-1&&r.splice(s,1)}}dispatchEvent(e){if(this._listeners===void 0)return;const n=this._listeners[e.type];if(n!==void 0){e.target=this;const r=n.slice(0);for(let s=0,a=r.length;s<a;s++)r[s].call(this,e);e.target=null}}}var _y=Object.defineProperty,vy=(i,e,t)=>e in i?_y(i,e,{enumerable:!0,configurable:!0,writable:!0,value:t}):i[e]=t,Ye=(i,e,t)=>(vy(i,typeof e!="symbol"?e+"":e,t),t);const co=new Ma,Zh=new Ki,xy=Math.cos(70*(Math.PI/180)),Jh=(i,e)=>(i%e+e)%e;class yy extends gy{constructor(e,t){super(),Ye(this,"object"),Ye(this,"domElement"),Ye(this,"enabled",!0),Ye(this,"target",new H),Ye(this,"minDistance",0),Ye(this,"maxDistance",1/0),Ye(this,"minZoom",0),Ye(this,"maxZoom",1/0),Ye(this,"minPolarAngle",0),Ye(this,"maxPolarAngle",Math.PI),Ye(this,"minAzimuthAngle",-1/0),Ye(this,"maxAzimuthAngle",1/0),Ye(this,"enableDamping",!1),Ye(this,"dampingFactor",.05),Ye(this,"enableZoom",!0),Ye(this,"zoomSpeed",1),Ye(this,"enableRotate",!0),Ye(this,"rotateSpeed",1),Ye(this,"enablePan",!0),Ye(this,"panSpeed",1),Ye(this,"screenSpacePanning",!0),Ye(this,"keyPanSpeed",7),Ye(this,"zoomToCursor",!1),Ye(this,"autoRotate",!1),Ye(this,"autoRotateSpeed",2),Ye(this,"reverseOrbit",!1),Ye(this,"reverseHorizontalOrbit",!1),Ye(this,"reverseVerticalOrbit",!1),Ye(this,"keys",{LEFT:"ArrowLeft",UP:"ArrowUp",RIGHT:"ArrowRight",BOTTOM:"ArrowDown"}),Ye(this,"mouseButtons",{LEFT:Xr.ROTATE,MIDDLE:Xr.DOLLY,RIGHT:Xr.PAN}),Ye(this,"touches",{ONE:qr.ROTATE,TWO:qr.DOLLY_PAN}),Ye(this,"target0"),Ye(this,"position0"),Ye(this,"zoom0"),Ye(this,"_domElementKeyEvents",null),Ye(this,"getPolarAngle"),Ye(this,"getAzimuthalAngle"),Ye(this,"setPolarAngle"),Ye(this,"setAzimuthalAngle"),Ye(this,"getDistance"),Ye(this,"getZoomScale"),Ye(this,"listenToKeyEvents"),Ye(this,"stopListenToKeyEvents"),Ye(this,"saveState"),Ye(this,"reset"),Ye(this,"update"),Ye(this,"connect"),Ye(this,"dispose"),Ye(this,"dollyIn"),Ye(this,"dollyOut"),Ye(this,"getScale"),Ye(this,"setScale"),this.object=e,this.domElement=t,this.target0=this.target.clone(),this.position0=this.object.position.clone(),this.zoom0=this.object.zoom,this.getPolarAngle=()=>u.phi,this.getAzimuthalAngle=()=>u.theta,this.setPolarAngle=N=>{let le=Jh(N,2*Math.PI),I=u.phi;I<0&&(I+=2*Math.PI),le<0&&(le+=2*Math.PI);let re=Math.abs(le-I);2*Math.PI-re<re&&(le<I?le+=2*Math.PI:I+=2*Math.PI),h.phi=le-I,n.update()},this.setAzimuthalAngle=N=>{let le=Jh(N,2*Math.PI),I=u.theta;I<0&&(I+=2*Math.PI),le<0&&(le+=2*Math.PI);let re=Math.abs(le-I);2*Math.PI-re<re&&(le<I?le+=2*Math.PI:I+=2*Math.PI),h.theta=le-I,n.update()},this.getDistance=()=>n.object.position.distanceTo(n.target),this.listenToKeyEvents=N=>{N.addEventListener("keydown",Ae),this._domElementKeyEvents=N},this.stopListenToKeyEvents=()=>{this._domElementKeyEvents.removeEventListener("keydown",Ae),this._domElementKeyEvents=null},this.saveState=()=>{n.target0.copy(n.target),n.position0.copy(n.object.position),n.zoom0=n.object.zoom},this.reset=()=>{n.target.copy(n.target0),n.object.position.copy(n.position0),n.object.zoom=n.zoom0,n.object.updateProjectionMatrix(),n.dispatchEvent(r),n.update(),l=o.NONE},this.update=(()=>{const N=new H,le=new H(0,1,0),I=new Dr().setFromUnitVectors(e.up,le),re=I.clone().invert(),ne=new H,ie=new Dr,_e=2*Math.PI;return function(){const st=n.object.position;I.setFromUnitVectors(e.up,le),re.copy(I).invert(),N.copy(st).sub(n.target),N.applyQuaternion(I),u.setFromVector3(N),n.autoRotate&&l===o.NONE&&K(j()),n.enableDamping?(u.theta+=h.theta*n.dampingFactor,u.phi+=h.phi*n.dampingFactor):(u.theta+=h.theta,u.phi+=h.phi);let mt=n.minAzimuthAngle,Et=n.maxAzimuthAngle;isFinite(mt)&&isFinite(Et)&&(mt<-Math.PI?mt+=_e:mt>Math.PI&&(mt-=_e),Et<-Math.PI?Et+=_e:Et>Math.PI&&(Et-=_e),mt<=Et?u.theta=Math.max(mt,Math.min(Et,u.theta)):u.theta=u.theta>(mt+Et)/2?Math.max(mt,u.theta):Math.min(Et,u.theta)),u.phi=Math.max(n.minPolarAngle,Math.min(n.maxPolarAngle,u.phi)),u.makeSafe(),n.enableDamping===!0?n.target.addScaledVector(m,n.dampingFactor):n.target.add(m),n.zoomToCursor&&w||n.object.isOrthographicCamera?u.radius=xe(u.radius):u.radius=xe(u.radius*d),N.setFromSpherical(u),N.applyQuaternion(re),st.copy(n.target).add(N),n.object.matrixAutoUpdate||n.object.updateMatrix(),n.object.lookAt(n.target),n.enableDamping===!0?(h.theta*=1-n.dampingFactor,h.phi*=1-n.dampingFactor,m.multiplyScalar(1-n.dampingFactor)):(h.set(0,0,0),m.set(0,0,0));let at=!1;if(n.zoomToCursor&&w){let un=null;if(n.object instanceof _n&&n.object.isPerspectiveCamera){const Ot=N.length();un=xe(Ot*d);const Bt=Ot-un;n.object.position.addScaledVector(L,Bt),n.object.updateMatrixWorld()}else if(n.object.isOrthographicCamera){const Ot=new H(O.x,O.y,0);Ot.unproject(n.object),n.object.zoom=Math.max(n.minZoom,Math.min(n.maxZoom,n.object.zoom/d)),n.object.updateProjectionMatrix(),at=!0;const Bt=new H(O.x,O.y,0);Bt.unproject(n.object),n.object.position.sub(Bt).add(Ot),n.object.updateMatrixWorld(),un=N.length()}else console.warn("WARNING: OrbitControls.js encountered an unknown camera type - zoom to cursor disabled."),n.zoomToCursor=!1;un!==null&&(n.screenSpacePanning?n.target.set(0,0,-1).transformDirection(n.object.matrix).multiplyScalar(un).add(n.object.position):(co.origin.copy(n.object.position),co.direction.set(0,0,-1).transformDirection(n.object.matrix),Math.abs(n.object.up.dot(co.direction))<xy?e.lookAt(n.target):(Zh.setFromNormalAndCoplanarPoint(n.object.up,n.target),co.intersectPlane(Zh,n.target))))}else n.object instanceof Ss&&n.object.isOrthographicCamera&&(at=d!==1,at&&(n.object.zoom=Math.max(n.minZoom,Math.min(n.maxZoom,n.object.zoom/d)),n.object.updateProjectionMatrix()));return d=1,w=!1,at||ne.distanceToSquared(n.object.position)>c||8*(1-ie.dot(n.object.quaternion))>c?(n.dispatchEvent(r),ne.copy(n.object.position),ie.copy(n.object.quaternion),at=!1,!0):!1}})(),this.connect=N=>{n.domElement=N,n.domElement.style.touchAction="none",n.domElement.addEventListener("contextmenu",we),n.domElement.addEventListener("pointerdown",Z),n.domElement.addEventListener("pointercancel",Q),n.domElement.addEventListener("wheel",ge)},this.dispose=()=>{var N,le,I,re,ne,ie;n.domElement&&(n.domElement.style.touchAction="auto"),(N=n.domElement)==null||N.removeEventListener("contextmenu",we),(le=n.domElement)==null||le.removeEventListener("pointerdown",Z),(I=n.domElement)==null||I.removeEventListener("pointercancel",Q),(re=n.domElement)==null||re.removeEventListener("wheel",ge),(ne=n.domElement)==null||ne.ownerDocument.removeEventListener("pointermove",oe),(ie=n.domElement)==null||ie.ownerDocument.removeEventListener("pointerup",Q),n._domElementKeyEvents!==null&&n._domElementKeyEvents.removeEventListener("keydown",Ae)};const n=this,r={type:"change"},s={type:"start"},a={type:"end"},o={NONE:-1,ROTATE:0,DOLLY:1,PAN:2,TOUCH_ROTATE:3,TOUCH_PAN:4,TOUCH_DOLLY_PAN:5,TOUCH_DOLLY_ROTATE:6};let l=o.NONE;const c=1e-6,u=new Kh,h=new Kh;let d=1;const m=new H,_=new Xe,v=new Xe,p=new Xe,f=new Xe,E=new Xe,S=new Xe,T=new Xe,z=new Xe,R=new Xe,L=new H,O=new Xe;let w=!1;const x=[],C={};function j(){return 2*Math.PI/60/60*n.autoRotateSpeed}function B(){return Math.pow(.95,n.zoomSpeed)}function K(N){n.reverseOrbit||n.reverseHorizontalOrbit?h.theta+=N:h.theta-=N}function W(N){n.reverseOrbit||n.reverseVerticalOrbit?h.phi+=N:h.phi-=N}const J=(()=>{const N=new H;return function(I,re){N.setFromMatrixColumn(re,0),N.multiplyScalar(-I),m.add(N)}})(),q=(()=>{const N=new H;return function(I,re){n.screenSpacePanning===!0?N.setFromMatrixColumn(re,1):(N.setFromMatrixColumn(re,0),N.crossVectors(n.object.up,N)),N.multiplyScalar(I),m.add(N)}})(),ee=(()=>{const N=new H;return function(I,re){const ne=n.domElement;if(ne&&n.object instanceof _n&&n.object.isPerspectiveCamera){const ie=n.object.position;N.copy(ie).sub(n.target);let _e=N.length();_e*=Math.tan(n.object.fov/2*Math.PI/180),J(2*I*_e/ne.clientHeight,n.object.matrix),q(2*re*_e/ne.clientHeight,n.object.matrix)}else ne&&n.object instanceof Ss&&n.object.isOrthographicCamera?(J(I*(n.object.right-n.object.left)/n.object.zoom/ne.clientWidth,n.object.matrix),q(re*(n.object.top-n.object.bottom)/n.object.zoom/ne.clientHeight,n.object.matrix)):(console.warn("WARNING: OrbitControls.js encountered an unknown camera type - pan disabled."),n.enablePan=!1)}})();function me(N){n.object instanceof _n&&n.object.isPerspectiveCamera||n.object instanceof Ss&&n.object.isOrthographicCamera?d=N:(console.warn("WARNING: OrbitControls.js encountered an unknown camera type - dolly/zoom disabled."),n.enableZoom=!1)}function he(N){me(d/N)}function ve(N){me(d*N)}function Te(N){if(!n.zoomToCursor||!n.domElement)return;w=!0;const le=n.domElement.getBoundingClientRect(),I=N.clientX-le.left,re=N.clientY-le.top,ne=le.width,ie=le.height;O.x=I/ne*2-1,O.y=-(re/ie)*2+1,L.set(O.x,O.y,1).unproject(n.object).sub(n.object.position).normalize()}function xe(N){return Math.max(n.minDistance,Math.min(n.maxDistance,N))}function te(N){_.set(N.clientX,N.clientY)}function ce(N){Te(N),T.set(N.clientX,N.clientY)}function ye(N){f.set(N.clientX,N.clientY)}function de(N){v.set(N.clientX,N.clientY),p.subVectors(v,_).multiplyScalar(n.rotateSpeed);const le=n.domElement;le&&(K(2*Math.PI*p.x/le.clientHeight),W(2*Math.PI*p.y/le.clientHeight)),_.copy(v),n.update()}function Be(N){z.set(N.clientX,N.clientY),R.subVectors(z,T),R.y>0?he(B()):R.y<0&&ve(B()),T.copy(z),n.update()}function Ve(N){E.set(N.clientX,N.clientY),S.subVectors(E,f).multiplyScalar(n.panSpeed),ee(S.x,S.y),f.copy(E),n.update()}function Ne(N){Te(N),N.deltaY<0?ve(B()):N.deltaY>0&&he(B()),n.update()}function dt(N){let le=!1;switch(N.code){case n.keys.UP:ee(0,n.keyPanSpeed),le=!0;break;case n.keys.BOTTOM:ee(0,-n.keyPanSpeed),le=!0;break;case n.keys.LEFT:ee(n.keyPanSpeed,0),le=!0;break;case n.keys.RIGHT:ee(-n.keyPanSpeed,0),le=!0;break}le&&(N.preventDefault(),n.update())}function U(){if(x.length==1)_.set(x[0].pageX,x[0].pageY);else{const N=.5*(x[0].pageX+x[1].pageX),le=.5*(x[0].pageY+x[1].pageY);_.set(N,le)}}function ut(){if(x.length==1)f.set(x[0].pageX,x[0].pageY);else{const N=.5*(x[0].pageX+x[1].pageX),le=.5*(x[0].pageY+x[1].pageY);f.set(N,le)}}function nt(){const N=x[0].pageX-x[1].pageX,le=x[0].pageY-x[1].pageY,I=Math.sqrt(N*N+le*le);T.set(0,I)}function ot(){n.enableZoom&&nt(),n.enablePan&&ut()}function Fe(){n.enableZoom&&nt(),n.enableRotate&&U()}function St(N){if(x.length==1)v.set(N.pageX,N.pageY);else{const I=ke(N),re=.5*(N.pageX+I.x),ne=.5*(N.pageY+I.y);v.set(re,ne)}p.subVectors(v,_).multiplyScalar(n.rotateSpeed);const le=n.domElement;le&&(K(2*Math.PI*p.x/le.clientHeight),W(2*Math.PI*p.y/le.clientHeight)),_.copy(v)}function qe(N){if(x.length==1)E.set(N.pageX,N.pageY);else{const le=ke(N),I=.5*(N.pageX+le.x),re=.5*(N.pageY+le.y);E.set(I,re)}S.subVectors(E,f).multiplyScalar(n.panSpeed),ee(S.x,S.y),f.copy(E)}function We(N){const le=ke(N),I=N.pageX-le.x,re=N.pageY-le.y,ne=Math.sqrt(I*I+re*re);z.set(0,ne),R.set(0,Math.pow(z.y/T.y,n.zoomSpeed)),he(R.y),T.copy(z)}function D(N){n.enableZoom&&We(N),n.enablePan&&qe(N)}function M(N){n.enableZoom&&We(N),n.enableRotate&&St(N)}function Z(N){var le,I;n.enabled!==!1&&(x.length===0&&((le=n.domElement)==null||le.ownerDocument.addEventListener("pointermove",oe),(I=n.domElement)==null||I.ownerDocument.addEventListener("pointerup",Q)),Ke(N),N.pointerType==="touch"?je(N):G(N))}function oe(N){n.enabled!==!1&&(N.pointerType==="touch"?pe(N):Ee(N))}function Q(N){var le,I,re;ze(N),x.length===0&&((le=n.domElement)==null||le.releasePointerCapture(N.pointerId),(I=n.domElement)==null||I.ownerDocument.removeEventListener("pointermove",oe),(re=n.domElement)==null||re.ownerDocument.removeEventListener("pointerup",Q)),n.dispatchEvent(a),l=o.NONE}function G(N){let le;switch(N.button){case 0:le=n.mouseButtons.LEFT;break;case 1:le=n.mouseButtons.MIDDLE;break;case 2:le=n.mouseButtons.RIGHT;break;default:le=-1}switch(le){case Xr.DOLLY:if(n.enableZoom===!1)return;ce(N),l=o.DOLLY;break;case Xr.ROTATE:if(N.ctrlKey||N.metaKey||N.shiftKey){if(n.enablePan===!1)return;ye(N),l=o.PAN}else{if(n.enableRotate===!1)return;te(N),l=o.ROTATE}break;case Xr.PAN:if(N.ctrlKey||N.metaKey||N.shiftKey){if(n.enableRotate===!1)return;te(N),l=o.ROTATE}else{if(n.enablePan===!1)return;ye(N),l=o.PAN}break;default:l=o.NONE}l!==o.NONE&&n.dispatchEvent(s)}function Ee(N){if(n.enabled!==!1)switch(l){case o.ROTATE:if(n.enableRotate===!1)return;de(N);break;case o.DOLLY:if(n.enableZoom===!1)return;Be(N);break;case o.PAN:if(n.enablePan===!1)return;Ve(N);break}}function ge(N){n.enabled===!1||n.enableZoom===!1||l!==o.NONE&&l!==o.ROTATE||(N.preventDefault(),n.dispatchEvent(s),Ne(N),n.dispatchEvent(a))}function Ae(N){n.enabled===!1||n.enablePan===!1||dt(N)}function je(N){switch(Se(N),x.length){case 1:switch(n.touches.ONE){case qr.ROTATE:if(n.enableRotate===!1)return;U(),l=o.TOUCH_ROTATE;break;case qr.PAN:if(n.enablePan===!1)return;ut(),l=o.TOUCH_PAN;break;default:l=o.NONE}break;case 2:switch(n.touches.TWO){case qr.DOLLY_PAN:if(n.enableZoom===!1&&n.enablePan===!1)return;ot(),l=o.TOUCH_DOLLY_PAN;break;case qr.DOLLY_ROTATE:if(n.enableZoom===!1&&n.enableRotate===!1)return;Fe(),l=o.TOUCH_DOLLY_ROTATE;break;default:l=o.NONE}break;default:l=o.NONE}l!==o.NONE&&n.dispatchEvent(s)}function pe(N){switch(Se(N),l){case o.TOUCH_ROTATE:if(n.enableRotate===!1)return;St(N),n.update();break;case o.TOUCH_PAN:if(n.enablePan===!1)return;qe(N),n.update();break;case o.TOUCH_DOLLY_PAN:if(n.enableZoom===!1&&n.enablePan===!1)return;D(N),n.update();break;case o.TOUCH_DOLLY_ROTATE:if(n.enableZoom===!1&&n.enableRotate===!1)return;M(N),n.update();break;default:l=o.NONE}}function we(N){n.enabled!==!1&&N.preventDefault()}function Ke(N){x.push(N)}function ze(N){delete C[N.pointerId];for(let le=0;le<x.length;le++)if(x[le].pointerId==N.pointerId){x.splice(le,1);return}}function Se(N){let le=C[N.pointerId];le===void 0&&(le=new Xe,C[N.pointerId]=le),le.set(N.pageX,N.pageY)}function ke(N){const le=N.pointerId===x[0].pointerId?x[1]:x[0];return C[le.pointerId]}this.dollyIn=(N=B())=>{ve(N),n.update()},this.dollyOut=(N=B())=>{he(N),n.update()},this.getScale=()=>d,this.setScale=N=>{me(N),n.update()},this.getZoomScale=()=>B(),t!==void 0&&this.connect(t),this.update()}}class My{constructor(){ae(this,"handlers",new Map);ae(this,"onceHandlers",new Map);ae(this,"messageBuffer",new Map)}register(e,t){if(!this.handlers.has(e)){this.handlers.set(e,new Set);const n=this.messageBuffer.get(e);n&&(n.forEach(r=>Promise.resolve(t(r))),this.messageBuffer.delete(e))}return this.handlers.get(e).add(t),()=>this.unregister(e,t)}once(e,t){return this.onceHandlers.has(e)||this.onceHandlers.set(e,new Set),this.onceHandlers.get(e).add(t),()=>this.unregisterOnce(e,t)}unregister(e,t){var n;(n=this.handlers.get(e))==null||n.delete(t)}unregisterOnce(e,t){var n;(n=this.onceHandlers.get(e))==null||n.delete(t)}buffer(e){const{type:t}=e;this.messageBuffer.has(t)||this.messageBuffer.set(t,[]),this.messageBuffer.get(t).push(e)}async dispatch(e){const{type:t,...n}=e,r=this.handlers.get(t);if(r&&r.size>0){await Promise.all(Array.from(r).map(a=>Promise.resolve(a(n))));return}const s=this.onceHandlers.get(t);if(s&&s.size>0){await Promise.all(Array.from(s).map(a=>Promise.resolve(a(n)))),this.onceHandlers.delete(t);return}this.buffer(e)}clear(){this.handlers.clear(),this.onceHandlers.clear(),this.messageBuffer.clear()}getBuffered(e){return this.messageBuffer.get(e)??[]}hasHandlers(e){var t;return(((t=this.handlers.get(e))==null?void 0:t.size)??0)>0}}class Sy{constructor(e,t){ae(this,"ws",null);ae(this,"url");ae(this,"router");ae(this,"reconnectDelay",1e3);ae(this,"maxReconnectDelay",3e4);ae(this,"reconnectAttempts",0);ae(this,"shouldReconnect",!0);ae(this,"state","disconnected");ae(this,"stateListeners",new Set);ae(this,"messageQueue",[]);this.url=e,this.router=t}get connectionState(){return this.state}onStateChange(e){return this.stateListeners.add(e),e(this.state),()=>this.stateListeners.delete(e)}setState(e){this.state!==e&&(this.state=e,this.stateListeners.forEach(t=>t(e)))}connect(){var n;if(((n=this.ws)==null?void 0:n.readyState)===WebSocket.OPEN||this.state==="connecting")return;this.setState("connecting");const t=`${window.location.protocol==="https:"?"wss:":"ws:"}//${window.location.host}${this.url}`;this.ws=new WebSocket(t),this.ws.binaryType="arraybuffer",this.ws.onopen=()=>{console.log("[WS] Connected"),this.reconnectAttempts=0,this.reconnectDelay=1e3,this.setState("connected"),this.flushQueue()},this.ws.onmessage=async r=>{try{const s=JSON.parse(r.data);await this.router.dispatch(s)}catch(s){console.error("[WS] Failed to parse message:",s)}},this.ws.onclose=()=>{console.log("[WS] Disconnected"),this.setState("disconnected"),this.shouldReconnect&&this.scheduleReconnect()},this.ws.onerror=r=>{console.error("[WS] Error:",r)}}scheduleReconnect(){if(this.state==="reconnecting")return;this.setState("reconnecting");const e=Math.min(this.reconnectDelay*Math.pow(1.5,this.reconnectAttempts),this.maxReconnectDelay);this.reconnectAttempts++,console.log(`[WS] Reconnecting in ${e}ms (attempt ${this.reconnectAttempts})`),setTimeout(()=>this.connect(),e)}send(e){var t;((t=this.ws)==null?void 0:t.readyState)===WebSocket.OPEN?this.ws.send(JSON.stringify(e)):this.messageQueue.push(e)}flushQueue(){var e;for(;this.messageQueue.length>0&&((e=this.ws)==null?void 0:e.readyState)===WebSocket.OPEN;){const t=this.messageQueue.shift();this.ws.send(JSON.stringify(t))}}disconnect(){var e;this.shouldReconnect=!1,(e=this.ws)==null||e.close(),this.ws=null,this.setState("disconnected")}async waitForConnection(e=1e4){return this.state==="connected"?!0:new Promise(t=>{const n=setTimeout(()=>{r(),t(!1)},e),r=this.onStateChange(s=>{s==="connected"&&(clearTimeout(n),r(),t(!0))})})}get isConnected(){var e;return((e=this.ws)==null?void 0:e.readyState)===WebSocket.OPEN}}const Yt=new My,Cs=new Sy("/ws",Yt);let bf=null;function Ey(i){bf=i}function Qh(){return bf}class by{constructor(){ae(this,"components",new Map);ae(this,"initialized",!1)}register(e){const t=e.name||e.constructor.name;this.components.has(t)&&console.warn(`[ComponentRegistry] Component "${t}" already registered, replacing`),this.components.set(t,e),this.initialized&&e.init().catch(console.error)}unregister(e){const t=this.components.get(e);t&&(t.destroy().catch(console.error),this.components.delete(e))}async initAll(){this.initialized=!0;for(const[e,t]of this.components)try{await t.init(),console.log(`[ComponentRegistry] Initialized: ${e}`)}catch(n){console.error(`[ComponentRegistry] Failed to initialize ${e}:`,n)}}async destroyAll(){for(const[e,t]of this.components)try{await t.destroy(),console.log(`[ComponentRegistry] Destroyed: ${e}`)}catch(n){console.error(`[ComponentRegistry] Failed to destroy ${e}:`,n)}this.components.clear(),this.initialized=!1}get(e){return this.components.get(e)}list(){return Array.from(this.components.keys())}}const sr=new by;typeof window<"u"&&(document.addEventListener("DOMContentLoaded",()=>{sr.initAll().catch(console.error)}),window.addEventListener("beforeunload",()=>{sr.destroyAll().catch(console.error)}));const nr={gradient:"#58a6ff",pepita:"#d4a843",random_projections:"#f78166",local_goodness:"#a371f7",thermodynamic_contrast:"#3fb950",contrastive:"#ff7b72",hebbian:"#79c0ff",predictive:"#d2a8ff"},be={bg:"#0a0e14",border:"#2a3a4a",text_primary:"#e8ecf0",text_secondary:"#8b98a8",text_muted:"#5a6a7a",gradient:"#58a6ff",measured:"#d4a843",legal_unmeasured:"#58a6ff",void:"#f85149",pareto:"#e8ecf0",chance_line:"#f85149",gpu:"#58a6ff",cpu:"#3fb950",memory:"#d29922",ok:"#3fb950",warn:"#d29922",error:"#f85149",passed:"#3fb950",insufficient:"#d29922",rejected:"#f85149",promoted:"#a371f7"};class Ty{constructor(){ae(this,"metricsByRun",new Map);ae(this,"selectedRunId",null);ae(this,"chosenByReader",!1);ae(this,"listeners",[])}observe(e,t){this.metricsByRun.set(e,t),this.chosenByReader||(this.selectedRunId=this.newestRunId()),this.notify()}select(e){this.chosenByReader=!0,this.selectedRunId=e,this.notify()}get selectedId(){return this.selectedRunId}get selected(){return this.selectedRunId?this.metricsByRun.get(this.selectedRunId)??null:null}get runs(){return Array.from(this.metricsByRun.entries())}onChange(e){this.listeners.push(e)}notify(){this.listeners.forEach(e=>e(this.selectedRunId,this.selected))}newestRunId(){let e=null,t=-1/0;if(this.metricsByRun.forEach((r,s)=>{var l;const a=(l=r.run)==null?void 0:l.started_at,o=a?Date.parse(a):Number.NaN;Number.isNaN(o)||o>=t&&(t=o,e=s)}),e)return e;const n=this.metricsByRun.keys().next();return n.done?null:n.value}}const Fn=new Ty,wy={substrate:{display_name:"Substrate",description:"Physical or computational substrate",primitives:[{name:"digital",summary:"Digital substrate: exact arithmetic, full precision",available:!0},{name:"analog",summary:"Analog substrate: continuous-valued physical state",available:!0},{name:"memristive",summary:"Memristive substrate: conductance, IR-drop, noise",available:!0},{name:"neuromorphic",summary:"Neuromorphic substrate: asynchronous spike events",available:!0},{name:"optical",summary:"Photonic substrate: phase/amplitude modulation",available:!0},{name:"quantum",summary:"Quantum substrate: unitary gate simulation",available:!0},{name:"complex",summary:"Complex-valued substrate",available:!0},{name:"sparse",summary:"Sparse substrate: sparsity-masked state",available:!0},{name:"ternary",summary:"Ternary substrate: weights in {-alpha, 0, +alpha}",available:!0}]},geometry:{display_name:"Geometry",description:"Network architecture and connectivity",primitives:[{name:"feedforward",summary:"Feedforward DAG (MLP/CNN)",available:!0},{name:"recurrent",summary:"Recurrent attractor (Hopfield/EqProp)",available:!0},{name:"causal_transformer",summary:"Causal transformer with KV cache",available:!0},{name:"tile",summary:"TileNet modular tile mesh",available:!0},{name:"tile_mesh",summary:"TileNet mesh topology",available:!0},{name:"conv",summary:"Convolutional geometry",available:!0},{name:"graph",summary:"Arbitrary node-edge fabric (FabricPC)",available:!0},{name:"attention",summary:"Attention geometry",available:!0},{name:"spatial_lattice",summary:"3-D spatial lattice (neural_cube)",available:!0},{name:"nca",summary:"Neural cellular automaton fabric",available:!0},{name:"ntm",summary:"Neural Turing Machine tape",available:!0}]},dynamics:{display_name:"Dynamics",description:"State evolution and settling",primitives:[{name:"energy_minimization",summary:"Equilibrium propagation energy minimization",available:!0},{name:"predictive_settling",summary:"Predictive coding settling",available:!0},{name:"error_predictive_coding",summary:"Error predictive coding",available:!0},{name:"spike_integration",summary:"LIF/Izhikevich spike integration",available:!0},{name:"instantaneous",summary:"Instantaneous pass (FF/Backprop)",available:!0},{name:"diffusion",summary:"Continuous-time diffusion settling",available:!0},{name:"lazy",summary:"Lazy/on-demand state dynamics",available:!0},{name:"pc_alm",summary:"Augmented Lagrangian predictive coding",available:!0}]},plasticity:{display_name:"Plasticity",description:"Local learning and adaptation",primitives:[{name:"null",summary:"Null plasticity (5-D slice)",available:!0},{name:"routing",summary:"Routing plasticity: state-dependent gating",available:!0},{name:"fast_weights",summary:"Fast-weight episode-local memory",available:!0},{name:"substrate_coupled",summary:"Physical substrate-coupled plasticity",available:!0},{name:"rule_state",summary:"Rule-state plasticity (Z3)",available:!0},{name:"temporal_psi",summary:"Trace-decayed supervised psi",available:!0},{name:"conflict_adaptive",summary:"Conflict-adaptive psi",available:!0}]},credit:{display_name:"Credit Assignment",description:"How learning signals reach parameters",primitives:[{name:"thermodynamic_contrast",summary:"EqProp free/nudged contrast (Scellier-Bengio)",available:!0},{name:"random_projections",summary:"Fixed random feedback (FA/DFA)",available:!0},{name:"local_goodness",summary:"Forward-Forward / PEPITA goodness",available:!0},{name:"local_contrastive",summary:"Local contrastive credit",available:!0},{name:"temporal_trace",summary:"Hebbian/STDP temporal trace",available:!0},{name:"target_inversion",summary:"Target propagation inversion",available:!0},{name:"homeostatic",summary:"Autonomous Lipschitz scaling",available:!0},{name:"pepita",summary:"PEPITA input-modulation credit",available:!0},{name:"gradient",summary:"Backprop gradient credit (ruler reference)",available:!0},{name:"pc_alm",summary:"PC-ALM primal-dual credit",available:!0}]},update:{display_name:"Update Rule",description:"How parameters are updated",primitives:[{name:"euclidean",summary:"SGD/Adam Euclidean update",available:!0},{name:"adam",summary:"Adam adaptive moment",available:!0},{name:"local_adam",summary:"Local Adam",available:!0},{name:"ortho_adam",summary:"Orthogonal Adam",available:!0},{name:"riemannian_orthogonal",summary:"Riemannian orthogonal update (Muon-family)",available:!0},{name:"muon",summary:"Muon update",available:!0},{name:"lion",summary:"Lion optimizer",available:!0},{name:"spectral_constrained",summary:"Spectral-norm constrained update",available:!0},{name:"mean_norm",summary:"Mean-norm update",available:!0},{name:"elastic_consolidation",summary:"EWC elastic consolidation",available:!0},{name:"natural_gradient",summary:"Natural gradient (Fisher)",available:!0},{name:"role_split",summary:"Role-split update",available:!0}]}},Ay={axes:wy},na=["credit","geometry","dynamics","substrate","plasticity","update"],ed=Ay.axes,Ry={measured:"Measured — the run has evidence here",legal:"Legal — a gap nobody has measured",void:"Void — the system refuses this cell"};function da(i){return i.length===0?0:i.reduce((e,t)=>e+t,0)/i.length}function Cy(i){if(i.length<2)return 0;const e=da(i),t=i.reduce((n,r)=>n+(r-e)**2,0)/(i.length-1);return Math.sqrt(t)}function Py(i){const e=new Map;for(const t of i)for(const n of t){const r=e.get(n.epoch)??[];r.push(n.val_acc),e.set(n.epoch,r)}return Array.from(e.entries()).sort((t,n)=>t[0]-n[0]).map(([t,n])=>({epoch:t,val_acc:da(n)}))}function Ly(i,e=10){if(i.length<=e)return[i];const t=[];let n="";for(const r of i.split("_")){const s=n?`${n}_${r}`:r;s.length>e&&n?(t.push(n),n=r):n=s}return n&&t.push(n),t}const Dy=.72,Iy=.86;class Uy{constructor(){ae(this,"name","DiscoveryMap");ae(this,"scene",new eu);ae(this,"camera",new _n);ae(this,"renderer",null);ae(this,"cells",new Map);ae(this,"cellDataMap",new Map);ae(this,"cellHeights",new Map);ae(this,"axes",{x:"credit",y:"geometry",z:"dynamics"});ae(this,"xValues",[]);ae(this,"yValues",[]);ae(this,"zValues",[]);ae(this,"space",null);ae(this,"spaceCells",new Map);ae(this,"measuredValues",{credit:[],geometry:[],dynamics:[],substrate:[],plasticity:[],update:[]});ae(this,"spaceRequest","");ae(this,"cellSize",.8);ae(this,"spacing",1.1);ae(this,"raycaster",new hy);ae(this,"mouse",new Xe);ae(this,"selectedCell",null);ae(this,"hoveredCell",null);ae(this,"legendElement",null);ae(this,"readoutElement",null);ae(this,"pointerX",0);ae(this,"pointerY",0);ae(this,"axisLabelMeshes",[]);ae(this,"voidMesh",null);ae(this,"chance",.1);ae(this,"requiredSeeds",0);ae(this,"runId");ae(this,"lastMetrics",null);ae(this,"onQueueUpdate",e=>{});ae(this,"onCampaignMetrics",e=>{var r;const t=e==null?void 0:e.data;if(!((r=t==null?void 0:t.records)!=null&&r.length))return;const n=typeof(e==null?void 0:e.campaign_id)=="string"?e.campaign_id:null;n&&Fn.observe(n,t)});Yt.register("queue_update",this.onQueueUpdate),Yt.register("campaign_metrics",this.onCampaignMetrics)}async init(){const e=Qh();e&&(this.scene=e.scene,this.camera=e.camera,this.renderer=e.renderer),this.setupInteraction(),this.createLegend(),this.createReadout(),this.buildGrid(),console.log("[DiscoveryMap] Initialized")}async destroy(){var e,t;Yt.unregister("queue_update",this.onQueueUpdate),Yt.unregister("campaign_metrics",this.onCampaignMetrics),this.clearGrid(),(e=this.legendElement)==null||e.remove(),(t=this.readoutElement)==null||t.remove()}setupInteraction(){var t;const e=(t=this.renderer)==null?void 0:t.domElement;e&&(this.raycaster.params.Line.threshold=this.cellSize*.2,e.addEventListener("mousemove",n=>{const r=e.getBoundingClientRect();this.mouse.x=(n.clientX-r.left)/r.width*2-1,this.mouse.y=-((n.clientY-r.top)/r.height)*2+1,this.pointerX=n.clientX,this.pointerY=n.clientY}),e.addEventListener("mouseleave",()=>{this.hideReadout()}),e.addEventListener("click",()=>{this.hoveredCell&&this.selectCell(this.hoveredCell)}))}createReadout(){const e=document.getElementById("ui-overlay");e&&(this.readoutElement=document.createElement("div"),this.readoutElement.id="cell-readout",this.readoutElement.style.cssText=`
      position: fixed;
      pointer-events: none;
      background: var(--bg-secondary);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 8px 10px;
      font-size: 11px;
      line-height: 1.5;
      z-index: 300;
      display: none;
      max-width: 340px;
    `,e.appendChild(this.readoutElement))}showReadout(e){const t=this.readoutElement;if(!t)return;const n=document.createElement("div");n.style.color="var(--text-secondary)",n.textContent=Object.entries(e.coordinate).filter(([,l])=>l).map(([l,c])=>`${l}=${c}`).join("  "),t.replaceChildren(n);const r=document.createElement("div");if(r.style.marginTop="4px",r.style.fontWeight="600",r.style.color=e.status==="void"?be.void:e.status==="measured"?be.measured:be.legal_unmeasured,r.textContent=Ry[e.status],t.appendChild(r),e.voidReason){const l=document.createElement("div");l.style.marginTop="4px",l.style.color="var(--text-secondary)",l.textContent=e.voidReason,t.appendChild(l)}t.style.display="block";const s=t.getBoundingClientRect(),a=Math.min(this.pointerX+16,window.innerWidth-s.width-8),o=Math.min(this.pointerY+16,window.innerHeight-s.height-8);t.style.left=`${Math.max(8,a)}px`,t.style.top=`${Math.max(8,o)}px`}hideReadout(){this.readoutElement&&(this.readoutElement.style.display="none")}createLegend(){const e=document.getElementById("ui-overlay");e&&(this.legendElement=document.createElement("div"),this.legendElement.id="discovery-legend",this.legendElement.style.cssText=`
      position: fixed;
      bottom: 140px;
      left: 20px;
      background: var(--bg-secondary);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px;
      font-size: 12px;
      z-index: 100;
      min-width: 220px;
      max-width: 340px;
    `,this.legendElement.innerHTML=`
      <div style="font-weight: 600; margin-bottom: 12px; color: var(--text-primary);">Discovery Map</div>
      <div style="display: flex; flex-direction: column; gap: 8px;">
        <div class="legend-item" style="display: flex; align-items: center; gap: 8px;">
          <div style="width: 16px; height: 16px; background: var(--measured); border-radius: 3px; box-shadow: 0 0 8px var(--measured);"></div>
          <span>Measured (glowing pillar)</span>
        </div>
        <div class="legend-item" style="display: flex; align-items: center; gap: 8px;">
          <div style="width: 16px; height: 16px; background: transparent; border: 2px solid var(--legal-unmeasured); border-radius: 3px;"></div>
          <span>Legal / unmeasured — a gap</span>
        </div>
        <div class="legend-item" style="display: flex; align-items: center; gap: 8px;">
          <svg width="16" height="16" viewBox="0 0 16 16"><line x1="3" y1="3" x2="13" y2="13" stroke="var(--void)" stroke-width="2"/><line x1="13" y1="3" x2="3" y2="13" stroke="var(--void)" stroke-width="2"/></svg>
          <span>Void (the system refuses it)</span>
        </div>
      </div>
      <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--border);">
        <div style="font-weight: 600; margin-bottom: 8px;">Arms</div>
        <div id="legend-arms" style="display: flex; flex-wrap: wrap; gap: 6px;"></div>
      </div>
      <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--border);">
        <div style="font-weight: 600; margin-bottom: 8px;">Run</div>
        <select id="legend-run-picker" style="
          width: 100%;
          background: var(--bg-tertiary);
          color: var(--text-primary);
          border: 1px solid var(--border);
          border-radius: 4px;
          font-size: 11px;
          padding: 2px 4px;
        "></select>
        <div id="legend-run" style="font-size: 11px; color: var(--text-secondary); margin-top: 8px;"></div>
      </div>
      <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--border);">
        <div style="font-weight: 600; margin-bottom: 8px;">Axes</div>
        <div id="legend-axis-picker" style="display: flex; flex-direction: column; gap: 6px;"></div>
        <div id="legend-axes" style="font-size: 11px; color: var(--text-secondary); margin-top: 8px;"></div>
      </div>
    `,e.appendChild(this.legendElement),this.createRunPicker(),this.createAxisPicker(),this.updateLegendArms(),this.updateLegendAxes())}createRunPicker(){var t;const e=(t=this.legendElement)==null?void 0:t.querySelector("#legend-run-picker");e&&(e.addEventListener("change",()=>{Fn.select(e.value||null)}),Fn.onChange(()=>this.refresh()))}updateRunPicker(){var a,o,l;const e=(a=this.legendElement)==null?void 0:a.querySelector("#legend-run-picker"),t=(o=this.legendElement)==null?void 0:o.querySelector("#legend-run");if(!e)return;const n=Fn.runs;if(e.innerHTML="",n.forEach(([c,u])=>{var _,v;const h=document.createElement("option"),d=((_=u==null?void 0:u.run)==null?void 0:_.profile)??"run",m=((v=u==null?void 0:u.records)==null?void 0:v.length)??0;h.value=c,h.textContent=`${c.slice(0,8)} · ${d} · ${m}`,h.selected=c===Fn.selectedId,e.appendChild(h)}),n.length===0){e.disabled=!0,t&&(t.textContent="No run has reported yet.");return}e.disabled=!1;const r=Fn.selected;if(!t)return;if(!r){t.textContent="";return}const s=r.run??{};t.textContent=[`run ${(Fn.selectedId??"").slice(0,8)}`,s.mode,`${((l=r.records)==null?void 0:l.length)??0} records`].filter(Boolean).join(" · ")}createAxisPicker(){var n;const e=(n=this.legendElement)==null?void 0:n.querySelector("#legend-axis-picker");if(!e)return;["x","y","z"].forEach(r=>{const s=document.createElement("div");s.style.cssText="display: flex; align-items: center; gap: 6px; font-size: 11px;";const a=document.createElement("span");a.textContent=r.toUpperCase(),a.style.cssText="color: var(--text-secondary); width: 12px;";const o=document.createElement("select");o.dataset.dimension=r,o.style.cssText=`
        flex: 1;
        background: var(--bg-tertiary);
        color: var(--text-primary);
        border: 1px solid var(--border);
        border-radius: 4px;
        font-size: 11px;
        padding: 2px 4px;
      `,o.addEventListener("change",()=>{this.axes={...this.axes,[r]:o.value},this.syncSpace()}),s.appendChild(a),s.appendChild(o),e.appendChild(s)}),this.refreshAxisOptions()}refreshAxisOptions(){var t;const e=(t=this.legendElement)==null?void 0:t.querySelectorAll("#legend-axis-picker select");e&&e.forEach(n=>{const r=n.dataset.dimension,s=new Set(["x","y","z"].filter(a=>a!==r).map(a=>this.axes[a]));n.innerHTML="",na.forEach(a=>{var l;const o=document.createElement("option");o.value=a,o.textContent=((l=ed[a])==null?void 0:l.display_name)??a,o.disabled=s.has(a),o.selected=this.axes[r]===a,n.appendChild(o)})})}updateLegendArms(){var n;const e=(n=this.legendElement)==null?void 0:n.querySelector("#legend-arms");if(!e)return;const t=this.measuredValues.credit;if(t.length===0){e.innerHTML='<span style="color: var(--text-muted); font-size: 11px;">No arm measured yet.</span>';return}e.innerHTML=t.map(r=>{const s=nr[r]||be.gradient;return`<span style="display: inline-flex; align-items: center; gap: 4px; padding: 2px 8px; background: ${s}22; border: 1px solid ${s}88; border-radius: 12px; color: ${s}; font-size: 11px;">${r}</span>`}).join("")}updateLegendAxes(){var l;const e=(l=this.legendElement)==null?void 0:l.querySelector("#legend-axes");if(!e)return;const t=this.space;if(!t){e.textContent="Waiting for the run's declared space — the axes come from the ontology.";return}const n=(c,u)=>{var _;const h=t.available[c]??u.length,d=h>u.length?` (${u.length} of ${h})`:"";return`${((_=ed[c])==null?void 0:_.display_name)??c}${d}`},r=Object.entries(t.held).map(([c,u])=>`${c}=${u}`),s={measured:0,legal:0,void:0};this.cellDataMap.forEach(c=>{s[c.status]+=1});const a=t.cells.length,o=Object.entries(t.void_rules??{}).sort((c,u)=>u[1]-c[1]).slice(0,2).map(([c,u])=>`${c.replace(/_/g," ")} (${u})`);e.innerHTML=[`<div>X: ${n(this.axes.x,t.values[this.axes.x]??[])}</div>`,`<div>Y: ${n(this.axes.y,t.values[this.axes.y]??[])}</div>`,`<div>Z: ${n(this.axes.z,t.values[this.axes.z]??[])}</div>`,`<div style="margin-top: 6px;">held: ${r.join(" · ")||"—"}</div>`,`<div style="margin-top: 6px;">${s.measured} measured · ${s.legal} legal · ${s.void} void (of ${a})</div>`,o.length>0?`<div style="margin-top: 6px;">refused by: ${o.join(", ")}</div>`:""].join("")}applyAxes(){const e=this.space;this.xValues=(e==null?void 0:e.values[this.axes.x])??[],this.yValues=(e==null?void 0:e.values[this.axes.y])??[],this.zValues=(e==null?void 0:e.values[this.axes.z])??[],this.buildGrid(),this.refreshAxisOptions(),this.updateLegendArms(),this.updateLegendAxes()}buildGrid(){this.clearGrid(),this.createAxisLabels();const e=[];this.yValues.forEach((t,n)=>{this.zValues.forEach((r,s)=>{this.xValues.forEach((a,o)=>{const l=this.cellKey(a,t,r),c=this.spaceCells.get(l),u=(c==null?void 0:c.status)??"legal",h={coordinate:this.coordinateFor(a,t,r),status:u,chance:this.chance,requiredSeeds:this.requiredSeeds,runId:this.runId,voidReason:c==null?void 0:c.reason,inDeclaration:c==null?void 0:c.in_declaration};if(this.cellDataMap.set(l,h),u==="void"){e.push(...this.voidMarkerPositions(o,n,s));return}this.createCell(l,h,o,n,s)})})}),e.length>0&&this.createVoidMarkers(e),this.frameGrid()}coordinateFor(e,t,n){const r={credit:"",geometry:"",dynamics:"",substrate:"",plasticity:"",update:""};return r[this.axes.x]=e,r[this.axes.y]=t,r[this.axes.z]=n,na.forEach(s=>{var o,l;if(r[s])return;const a=(l=(o=this.space)==null?void 0:o.held)==null?void 0:l[s];a&&(r[s]=a)}),r}cellKey(e,t,n){return`${e}|${t}|${n}`}createAxisLabels(){this.axisLabelMeshes.forEach(u=>this.scene.remove(u)),this.axisLabelMeshes=[];const e=new Ac({color:9148584,sizeAttenuation:!0}),t=new Ac({color:13227232,sizeAttenuation:!0}),n=(this.xValues.length-1)*this.spacing,s=(this.zValues.length-1)*this.spacing/2+1.2,a=-.45;this.xValues.forEach((u,h)=>{const d=(h-(this.xValues.length-1)/2)*this.spacing,m=this.createTextSprite(u,.3,e,this.spacing*.95);m.position.set(d,a,s),this.scene.add(m),this.axisLabelMeshes.push(m)});const o=this.createTextSprite(this.axes.x,.3,t);o.position.set(n/2+1.15,a,s),this.scene.add(o),this.axisLabelMeshes.push(o);const l=this.createTextSprite(this.axes.z,.3,t);l.position.set(0,a,s+1.1),this.scene.add(l),this.axisLabelMeshes.push(l);const c=this.createTextSprite(this.axes.y,.3,t);c.position.set(-(n/2)-1.5,1.3,0),this.scene.add(c),this.axisLabelMeshes.push(c)}createTextSprite(e,t,n,r){const s=Ly(e),a=document.createElement("canvas"),o=a.getContext("2d"),l=64,c=72;o.font=`bold ${l}px "JetBrains Mono", monospace`;const u=Math.max(...s.map(p=>o.measureText(p).width))+16;a.width=Math.max(64,Math.ceil(u)),a.height=s.length*c+16,o.font=`bold ${l}px "JetBrains Mono", monospace`,o.fillStyle="#ffffff",o.textAlign="center",o.textBaseline="middle",s.forEach((p,f)=>{o.fillText(p,a.width/2,c*f+c/2+8)});const h=new iy(a);h.needsUpdate=!0;const d=n.clone();d.map=h,d.transparent=!0;const m=new ty(d),_=a.width/a.height;let v=t*s.length;return r!==void 0&&(v=Math.min(v,r/_)),m.scale.set(v*_,v,1),m}createCell(e,t,n,r,s){const a=(n-(this.xValues.length-1)/2)*this.spacing,o=r*this.spacing,l=(s-(this.zValues.length-1)/2)*this.spacing,c=t.status==="measured"?this.createMeasuredCell(t):this.createLegalCell();c.position.set(a,o,l),c.userData={...c.userData,cellKey:e},this.scene.add(c),this.cells.set(e,c)}createMeasuredCell(e){const t=this.pillarHeight(e),n=nr[e.coordinate.credit]||be.gradient,r=new Ii(this.cellSize,t,this.cellSize);r.translate(0,t/2,0);const s=new Nl({color:new tt(n),emissive:new tt(n),emissiveIntensity:.5,transparent:!0,opacity:.9,metalness:.3,roughness:.4}),a=new Tn(r,s);a.castShadow=!0,a.receiveShadow=!0;const o=new Ii(this.cellSize*1.1,t*1.1,this.cellSize*1.1);o.translate(0,t/2,0);const l=new ua({color:new tt(n),transparent:!0,opacity:.15,depthWrite:!1}),c=new Tn(o,l);return a.add(c),a.userData.glow=c,a}createLegalCell(){const e=new Ii(this.cellSize,this.cellSize,this.cellSize),t=new ry(e);t.translate(0,this.cellSize/2,0);const n=new tr({color:be.legal_unmeasured,transparent:!0,opacity:.55}),r=new ha(t,n),s=new Tn(new Ii(this.cellSize,this.cellSize,this.cellSize),new ua);return s.position.y=this.cellSize/2,s.visible=!1,r.add(s),r}disposeMesh(e){e.traverse(t=>{const n=t.geometry;n&&n.dispose();const r=t.material;Array.isArray(r)?r.forEach(s=>s.dispose()):r&&r.dispose()})}voidMarkerPositions(e,t,n){const r=(e-(this.xValues.length-1)/2)*this.spacing,s=t*this.spacing,a=(n-(this.zValues.length-1)/2)*this.spacing,o=this.cellSize*.6,l=.1;return[r-o,s+l,a-o,r+o,s+l,a+o,r+o,s+l,a-o,r-o,s+l,a+o]}createVoidMarkers(e){const t=new ln;t.setAttribute("position",new vn(e,3));const n=new tr({color:be.void,transparent:!0,opacity:.32});this.voidMesh=new ha(t,n),this.scene.add(this.voidMesh)}frameGrid(){const e=Qh();if(!(e!=null&&e.controls)||this.xValues.length===0||this.zValues.length===0)return;const t=(this.xValues.length-1)*this.spacing/2+this.cellSize,n=(this.zValues.length-1)*this.spacing/2+this.cellSize,r=(this.yValues.length-1)*this.spacing+this.cellSize,s=n+1.8,a=-.8,o=new H(0,r/2,0),l=this.camera.position.clone().sub(e.controls.target);l.lengthSq()===0&&l.set(.4,.5,.8),l.normalize();const c=l.clone().negate(),u=new H().crossVectors(c,new H(0,1,0)).normalize(),h=new H().crossVectors(u,c).normalize(),d=Math.tan((this.camera.fov??60)*Math.PI/360),m=d*(this.camera.aspect||1),_=d*Iy,v=m*Dy;let p=0;[-1,1].forEach(f=>{[a,r].forEach(E=>{[-n,s].forEach(S=>{const T=new H(f*t,E,S),z=Math.max(Math.abs(T.dot(u))/v,Math.abs(T.dot(h))/_)+T.dot(l);p=Math.max(p,z)})})}),p*=1.06,o.add(u.clone().multiplyScalar(.28*m*p)).add(h.clone().multiplyScalar(-.14*d*p)),e.controls.target.copy(o),this.camera.position.copy(o).add(l.clone().multiplyScalar(p)),e.controls.update()}clearGrid(){this.cells.forEach(e=>{this.scene.remove(e),this.disposeMesh(e)}),this.cells.clear(),this.cellDataMap.clear(),this.cellHeights.clear(),this.voidMesh&&(this.scene.remove(this.voidMesh),this.voidMesh.geometry.dispose(),Array.isArray(this.voidMesh.material)?this.voidMesh.material.forEach(e=>e.dispose()):this.voidMesh.material.dispose(),this.voidMesh=null)}refresh(){const e=Fn.selectedId,t=Fn.selected;this.lastMetrics=t??null,this.runId=e??void 0,t&&(typeof t.chance=="number"&&(this.chance=t.chance),typeof t.required_seeds=="number"&&(this.requiredSeeds=t.required_seeds),this.absorbMeasuredValues(t.records??[])),this.updateRunPicker(),this.syncSpace()}async syncSpace(){if(!this.runId){this.applyAggregates(this.aggregate(this.lastMetrics));return}const e=[this.runId,this.axes.x,this.axes.y,this.axes.z,...na.map(t=>this.measuredValues[t].join(","))].join("|");if(e!==this.spaceRequest){const t=await this.fetchSpace();if(!t)return;this.spaceRequest=e,this.space=t,this.spaceCells=this.indexSpaceCells(t),this.applyAxes()}this.applyAggregates(this.aggregate(this.lastMetrics))}async fetchSpace(){try{const e=await fetch(`/api/cells/${this.runId}/space`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({axes:[this.axes.x,this.axes.y,this.axes.z]})});return e.ok?await e.json():(console.warn("[DiscoveryMap] The space was refused",e.status),null)}catch(e){return console.warn("[DiscoveryMap] The space could not be read",e),null}}indexSpaceCells(e){const t=new Map;return e.cells.forEach(n=>{const r=this.cellKey(n.coordinate[this.axes.x],n.coordinate[this.axes.y],n.coordinate[this.axes.z]);t.set(r,n)}),t}applyAggregates(e){e.forEach((t,n)=>{const r=this.cellDataMap.get(n);r&&(r.status="measured",r.coordinate={...t.coordinate},r.metrics={val_acc:da(t.acc),val_acc_std:Cy(t.acc),walltime_s:da(t.walltime),param_count:da(t.params),n_seeds:t.acc.length},r.curve=Py(t.curves),r.pareto=t.pareto,r.chance=this.chance,r.requiredSeeds=this.requiredSeeds,r.runId=this.runId,this.updateCellVisual(n,r,t.pareto))}),this.updateLegendAxes()}aggregate(e){const t=new Map;return e!=null&&e.records&&e.records.forEach((n,r)=>{var c;const s=n.coordinate;if(!s)return;const a=this.cellKey(s[this.axes.x],s[this.axes.y],s[this.axes.z]);let o=t.get(a);o||(o={acc:[],walltime:[],params:[],curves:[],pareto:!1,coordinate:{...s}},t.set(a,o));const l=n.payload??{};if(typeof l.val_acc=="number"&&o.acc.push(l.val_acc),typeof l.walltime_s=="number"&&o.walltime.push(l.walltime_s),typeof l.param_count=="number"&&o.params.push(l.param_count),Array.isArray(l.convergence_curve)){const u=l.convergence_curve.filter(h=>typeof(h==null?void 0:h.epoch)=="number"&&typeof(h==null?void 0:h.val_acc)=="number").map(h=>({epoch:h.epoch,val_acc:h.val_acc}));u.length>0&&o.curves.push(u)}(c=e.pareto)!=null&&c[r]&&(o.pareto=!0)}),t}absorbMeasuredValues(e){const t={credit:new Set,geometry:new Set,dynamics:new Set,substrate:new Set,plasticity:new Set,update:new Set};e.forEach(n=>{const r=n==null?void 0:n.coordinate;r&&na.forEach(s=>{const a=r[s];typeof a=="string"&&a.length>0&&t[s].add(a)})}),na.forEach(n=>{this.measuredValues[n]=Array.from(t[n]).sort()})}pillarHeight(e){var t;return Tc.lerp(.4,3.4,((t=e.metrics)==null?void 0:t.val_acc)??0)}updateCellVisual(e,t,n){const r=this.cells.get(e);if(!r)return;const s=r.position.clone(),a=r.userData.glow;a&&r.remove(a),this.scene.remove(r),this.disposeMesh(r);const o=this.createMeasuredCell(t);o.position.copy(s),o.userData.cellKey=e;const l=this.pillarHeight(t),c=this.cellHeights.get(e)??0;if(this.cellHeights.set(e,l),o.scale.y=l>0?Math.min(1,Math.max(c/l,.001)):1,n){const u=new tu(this.cellSize*.6,this.cellSize*.8,32),h=new ua({color:be.pareto,side:gi,transparent:!0,opacity:.6}),d=new Tn(u,h);d.rotation.x=-Math.PI/2,d.position.y=.05,o.add(d),o.userData.paretoRing=d}this.scene.add(o),this.cells.set(e,o)}selectCell(e){this.selectedCell=e;const t=this.cellDataMap.get(e);t&&window.dispatchEvent(new CustomEvent("cell-selected",{detail:t}))}update(e){const t=1-Math.exp(-e*8);this.cells.forEach((a,o)=>{const l=this.cellDataMap.get(o);if((l==null?void 0:l.status)==="measured"&&a instanceof Tn&&a.material instanceof Nl){a.scale.y<1&&(a.scale.y=Math.min(1,a.scale.y+(1-a.scale.y)*t));const c=a.userData.glow;c&&(c.material.opacity=.1+.1*Math.sin(Date.now()*.003));const u=a.userData.paretoRing;u&&(u.material.opacity=.4+.2*Math.sin(Date.now()*.005))}}),this.raycaster.setFromCamera(this.mouse,this.camera);const n=this.raycaster.intersectObjects(Array.from(this.cells.values()),!0);let r=null;n.length>0&&(r=this.pickCell(n)),r||(r=this.voidCellUnderCursor()),r!==this.hoveredCell&&(this.hoveredCell&&this.highlightCell(this.hoveredCell,!1),this.hoveredCell=r,r&&this.highlightCell(r,!0));const s=r?this.cellDataMap.get(r):void 0;s?this.showReadout(s):this.hideReadout()}pickCell(e){var n,r;let t=null;for(const s of e){const a=s.object.userData.cellKey||((n=s.object.parent)==null?void 0:n.userData.cellKey);if(a&&(t??(t=a),((r=this.cellDataMap.get(a))==null?void 0:r.status)==="measured"))return a}return t}voidCellUnderCursor(){if(!this.voidMesh)return null;const e=this.raycaster.params.Line.threshold;this.raycaster.params.Line.threshold=this.cellSize*.3;try{const t=this.raycaster.intersectObject(this.voidMesh,!1);return t.length===0?null:this.cellAt(t[0].point)}finally{this.raycaster.params.Line.threshold=e}}cellAt(e){const t=Math.round(e.x/this.spacing+(this.xValues.length-1)/2),n=Math.round(e.y/this.spacing),r=Math.round(e.z/this.spacing+(this.zValues.length-1)/2);return t<0||t>=this.xValues.length||n<0||n>=this.yValues.length||r<0||r>=this.zValues.length?null:this.cellKey(this.xValues[t],this.yValues[n],this.zValues[r])}highlightCell(e,t){const n=this.cells.get(e);if(n){if(n instanceof Tn&&n.material instanceof Nl){t?(n.userData.originalEmissive=n.material.emissiveIntensity,n.material.emissiveIntensity=(n.userData.originalEmissive||.5)+.5):n.userData.originalEmissive!==void 0&&(n.material.emissiveIntensity=n.userData.originalEmissive);return}n instanceof ha&&n.material instanceof tr&&(t?(n.userData.originalOpacity=n.material.opacity,n.material.opacity=.95):n.userData.originalOpacity!==void 0&&(n.material.opacity=n.userData.originalOpacity))}}}const iu=new Uy;sr.register(iu);class Ny{constructor(){ae(this,"name","CellDrawer");ae(this,"panel",null);ae(this,"content",null);ae(this,"sparklineScene",null);ae(this,"sparklineRenderer",null);ae(this,"sparklineCamera",null);ae(this,"sparklineAnimationId",null);ae(this,"currentData",null);ae(this,"onKeyDown",e=>{e.key==="Escape"&&this.currentData&&this.hide()});ae(this,"onCellSelected",e=>{this.show(e.detail)})}async init(){this.createPanel(),this.setupEvents(),console.log("[CellDrawer] Initialized")}async destroy(){var e;this.stopSparkline(),(e=this.panel)==null||e.remove(),window.removeEventListener("cell-selected",this.onCellSelected),window.removeEventListener("keydown",this.onKeyDown)}createPanel(){const e=document.getElementById("ui-overlay");e&&(this.panel=document.createElement("div"),this.panel.id="cell-drawer",this.panel.style.cssText=`
      position: fixed;
      top: 0;
      right: 0;
      width: 380px;
      height: 100%;
      background: var(--bg-secondary);
      border-left: 1px solid var(--border);
      transform: translateX(100%);
      transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      z-index: 200;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    `,this.panel.innerHTML=`
      <div id="drawer-header" style="
        padding: 16px;
        border-bottom: 1px solid var(--border);
        display: flex;
        align-items: center;
        justify-content: space-between;
      ">
        <h3 style="margin: 0; font-size: 14px; font-weight: 600;">Cell Details</h3>
        <button id="drawer-close" style="
          background: none;
          border: none;
          color: var(--text-secondary);
          font-size: 20px;
          cursor: pointer;
          padding: 4px;
          line-height: 1;
        ">&times;</button>
      </div>
      <div id="drawer-content" style="
        flex: 1;
        overflow-y: auto;
        padding: 16px;
      "></div>
    `,e.appendChild(this.panel),this.content=this.panel.querySelector("#drawer-content"),this.panel.querySelector("#drawer-close").addEventListener("click",()=>this.hide()))}setupEvents(){window.addEventListener("cell-selected",this.onCellSelected),window.addEventListener("keydown",this.onKeyDown)}shiftPanels(e){const t=e?400:20;["hud","plotter"].forEach(n=>{var r;(r=document.getElementById(n))==null||r.style.setProperty("right",`${t}px`)})}show(e){this.currentData=e,this.renderContent(e),this.panel.style.transform="translateX(0)",this.shiftPanels(!0),this.startSparkline(e)}hide(){this.panel.style.transform="translateX(100%)",this.shiftPanels(!1),this.stopSparkline(),this.currentData=null}renderContent(e){if(!this.content)return;const{coordinate:t,metrics:n,status:r}=e,s=nr[t.credit]||be.gradient,a=(n==null?void 0:n.val_acc)??0,o=(n==null?void 0:n.n_seeds)??0,l=e.chance??.1,c=e.requiredSeeds??0;let u="UNMEASURED",h=be.legal_unmeasured;r==="void"&&(u="VOID",h=be.void),r==="measured"&&(a<=l?(u="REJECTED",h=be.rejected):c>0&&o<c?(u="INSUFFICIENT",h=be.insufficient):a>l+.1?(u="PASSED",h=be.passed):(u="INSUFFICIENT",h=be.insufficient));const d=r==="measured"&&c>0?Math.max(0,c-o):"N/A";this.content.innerHTML=`
      <div style="margin-bottom: 20px;">
        <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px;">
          ${Object.entries(t).filter(([,_])=>_).map(([_,v])=>`
              <span style="
                padding: 4px 10px;
                background: ${_==="credit"?s+"22":"var(--bg-tertiary)"};
                border: 1px solid ${_==="credit"?s+"88":"var(--border)"};
                border-radius: 12px;
                font-size: 11px;
                color: ${_==="credit"?s:"var(--text-primary)"};
              ">
                ${_}=${v}
              </span>
            `).join("")}
        </div>
      </div>

      ${n?`
        <div style="margin-bottom: 20px;">
          <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 4px;">VALIDATION ACCURACY</div>
          <div style="
            font-size: 42px;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
            color: var(--text-primary);
            line-height: 1;
          ">${a.toFixed(3)}</div>
          <div style="font-size: 11px; color: var(--text-secondary); margin-top: 4px;">
            ± ${(n.val_acc_std??0).toFixed(3)} (n=${o})
          </div>
        </div>
      `:""}

      <div style="margin-bottom: 20px; padding: 12px; background: var(--bg-tertiary); border-radius: 6px;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
          <span style="
            padding: 4px 10px;
            background: ${h}22;
            border: 1px solid ${h}88;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            color: ${h};
            text-transform: uppercase;
          ">${u}</span>
          <span style="font-size: 12px; color: var(--text-secondary);">Chance level: ${l}</span>
        </div>
        ${e.voidReason?`<div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 8px;">${e.voidReason}</div>`:""}
        <div style="height: 4px; background: var(--bg); border-radius: 2px; overflow: hidden;">
          <div style="
            width: ${Math.min(100,a/(l*2)*100)}%;
            height: 100%;
            background: linear-gradient(90deg, ${be.rejected}, ${be.insufficient}, ${be.passed});
            border-radius: 2px;
          "></div>
        </div>
      </div>

      ${r==="measured"?`
        <div style="margin-bottom: 20px;">
          <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 8px;">SEEDS TO CLAIM</div>
          <div style="font-size: 24px; font-weight: 700; font-family: 'JetBrains Mono', monospace; color: ${be.insufficient};">
            ${d}
          </div>
          <div style="font-size: 11px; color: var(--text-secondary);">(d=0.5, α=0.05)</div>
        </div>
      `:""}

      ${n!=null&&n.walltime_s?`
        <div style="margin-bottom: 20px; padding: 12px; background: var(--bg-tertiary); border-radius: 6px;">
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; font-size: 12px;">
            <div>
              <div style="color: var(--text-secondary);">Wall Time</div>
              <div style="font-family: 'JetBrains Mono', monospace; font-weight: 600;">${n.walltime_s.toFixed(1)}s</div>
            </div>
            <div>
              <div style="color: var(--text-secondary);">Parameters</div>
              <div style="font-family: 'JetBrains Mono', monospace; font-weight: 600;">${((n.param_count??0)/1e3).toFixed(1)}K</div>
            </div>
          </div>
        </div>
      `:""}

      <!-- Mini 3D Sparkline Container -->
      <div style="margin-bottom: 20px;">
        <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 8px;">TRAINING CURVE</div>
        <div id="sparkline-container" style="
          width: 100%;
          height: 120px;
          background: var(--bg);
          border: 1px solid var(--border);
          border-radius: 6px;
          overflow: hidden;
        "></div>
      </div>

      <!-- Actions -->
      <div style="
        display: flex;
        flex-direction: column;
        gap: 8px;
        padding-top: 16px;
        border-top: 1px solid var(--border);
      ">
        <div id="drawer-action-note" style="font-size: 11px; color: var(--text-secondary); line-height: 1.5;">
        </div>
        <div style="display: flex; gap: 8px;">
          <button class="drawer-btn" data-action="replicate" style="flex: 1;">Queue Rest</button>
          <button class="drawer-btn" data-action="preregister" style="flex: 1;">Preregister</button>
          <button class="drawer-btn" data-action="quest" style="flex: 1;">Adopt as Quest</button>
        </div>
        <input id="drawer-threshold" class="drawer-input" type="number" step="0.001"
          placeholder="material effect (auto)" />
        <div id="drawer-status" style="font-size: 11px; color: var(--text-secondary); line-height: 1.5;"></div>
      </div>
    `;const m=document.createElement("style");m.textContent=`
      .drawer-btn {
        padding: 10px;
        background: var(--bg-tertiary);
        border: 1px solid var(--border);
        border-radius: 6px;
        color: var(--text-secondary);
        font-size: 11px;
        cursor: not-allowed;
        transition: all 0.15s;
      }
      .drawer-btn:not(:disabled):hover {
        background: var(--border);
        color: var(--text-primary);
        border-color: var(--border-bright);
      }
      .drawer-btn:not(:disabled) {
        cursor: pointer;
        color: var(--text-primary);
      }
      .drawer-btn:disabled {
        opacity: 0.45;
      }
      .drawer-input {
        padding: 8px 10px;
        background: var(--bg-tertiary);
        border: 1px solid var(--border);
        border-radius: 6px;
        color: var(--text-primary);
        font-size: 11px;
        font-family: 'JetBrains Mono', monospace;
      }
    `,this.content.appendChild(m),this.wireActions(e)}actionStates(e){var a;if(e.status==="void")return{replicate:!1,preregister:!1,quest:!1};const t=e.status==="measured",n=((a=e.metrics)==null?void 0:a.n_seeds)??0,r=e.requiredSeeds??0;return{replicate:(r>0?Math.max(0,r-n):0)>0||!t,preregister:t,quest:!t}}wireActions(e){const t=this.content;if(!t)return;const n=this.actionStates(e);t.querySelectorAll(".drawer-btn[data-action]").forEach(o=>{const l=o.dataset.action??"",c=n[l]===!0;o.disabled=!c,o.addEventListener("click",()=>{this.runAction(l,e)})});const s=t.querySelector('.drawer-btn[data-action="replicate"]');s&&(s.textContent=e.status==="measured"?"Queue Rest":"Queue");const a=t.querySelector("#drawer-action-note");a&&(a.textContent=this.actionNote(e))}actionNote(e){var r;if(!e.runId)return"This cell belongs to no run yet, so there is nothing to queue or register.";if(e.status==="void")return`The system refuses this cell, so nothing can be measured here.${e.voidReason?` ${e.voidReason}.`:""}`;if(e.status==="measured"){const s=((r=e.metrics)==null?void 0:r.n_seeds)??0,a=e.requiredSeeds??0;return`Queue Rest measures the ${Math.max(0,a-s)} seeds this cell still owes. Preregister writes down the protocol a confirming run must meet.`}const t=e.inDeclaration===!1?" It lies outside this run's declaration, so the run did not set out to measure it.":"";return`The system would measure this cell and nobody has. Queue measures it (${e.requiredSeeds??0} seeds). Adopt as Quest writes the question down first and then queues the run that would answer it — a new run, because a threshold written now cannot confirm a run that has already begun.${t}`}setStatus(e,t=!1){var r;const n=(r=this.content)==null?void 0:r.querySelector("#drawer-status");n&&(n.textContent=e,n.style.color=t?be.rejected:be.text_secondary)}async runAction(e,t){var o,l;if(!t.runId){this.setStatus("This cell belongs to no run yet.",!0);return}const n=Array.from(((o=this.content)==null?void 0:o.querySelectorAll(".drawer-btn"))??[]);n.forEach(c=>{c.disabled=!0}),this.setStatus("Working…");const r=(l=this.content)==null?void 0:l.querySelector("#drawer-threshold"),s=r!=null&&r.value?Number(r.value):null,a={coordinate:t.coordinate};s!==null&&Number.isFinite(s)&&(a.threshold=s);try{const c=await fetch(`/api/cells/${t.runId}/${e}`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(a)}),u=await c.json();if(!c.ok){this.setStatus((u==null?void 0:u.error)??"The action failed.",!0);return}this.setStatus(this.actionSummary(e,u))}catch(c){this.setStatus(`The action failed: ${String(c)}`,!0)}finally{n.forEach(c=>{c.disabled=!1})}}actionSummary(e,t){if(e==="replicate")return`Queued campaign ${t.campaign_id}: ${t.measurements} measurements in a plan of ${t.plan}.`;const r=`${t.written?"Registered":"Already registered"} ${t.path} — commit it; the run that follows it can be confirmatory.`;return e!=="quest"?r:t.campaign_id?`${r} Queued campaign ${t.campaign_id}: ${t.measurements} measurements in a plan of ${t.plan}, in a new run.`:`${r} No campaign queue is attached, so nothing is scheduled.`}startSparkline(e){const t=document.getElementById("sparkline-container");if(!t)return;this.stopSparkline();const n=e.curve??[];if(n.length===0){t.innerHTML=`
        <div style="
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 11px;
          color: var(--text-muted);
          text-align: center;
          padding: 0 12px;
        ">No convergence curve recorded for this cell.</div>
      `;return}this.sparklineScene=new eu,this.sparklineCamera=new Ss(-1,1,1,-1,.1,10),this.sparklineCamera.position.z=2,this.sparklineRenderer=new Mf({alpha:!0,antialias:!0}),this.sparklineRenderer.setSize(t.clientWidth,t.clientHeight),this.sparklineRenderer.setPixelRatio(Math.min(window.devicePixelRatio,2)),t.appendChild(this.sparklineRenderer.domElement);const r=e.chance??.1,s=n.map(L=>L.val_acc),a=Math.min(r,...s),l=Math.max(...s,r)-a||1,c=L=>Tc.lerp(-.7,.7,(L-a)/l),u=n.map((L,O)=>{const w=Tc.lerp(-.9,.9,O/(n.length-1||1));return new H(w,c(L.val_acc),0)}),h=new ln().setFromPoints(u),d=new tr({color:nr[e.coordinate.credit]||be.gradient,linewidth:2}),m=new Rc(h,d);this.sparklineScene.add(m);const _=new ny(new ln().setFromPoints(u),new Ef({color:nr[e.coordinate.credit]||be.gradient,size:6,sizeAttenuation:!1}));this.sparklineScene.add(_);const v=c(r),p=new ln().setFromPoints([new H(-.9,v,0),new H(.9,v,0)]),f=new sy({color:be.chance_line,dashSize:.05,gapSize:.03,linewidth:1}),E=new Rc(p,f);E.computeLineDistances(),this.sparklineScene.add(E);const S=new ln().setFromPoints([new H(-.9,-.7,0),new H(.9,-.7,0),new H(-.9,-.7,0),new H(-.9,.7,0)]),T=new tr({color:be.border,linewidth:1}),z=new ha(S,T);this.sparklineScene.add(z);const R=()=>{!this.sparklineRenderer||!this.sparklineScene||!this.sparklineCamera||(this.sparklineRenderer.render(this.sparklineScene,this.sparklineCamera),this.sparklineAnimationId=requestAnimationFrame(R))};R()}stopSparkline(){this.sparklineAnimationId&&(cancelAnimationFrame(this.sparklineAnimationId),this.sparklineAnimationId=null),this.sparklineRenderer&&(this.sparklineRenderer.dispose(),this.sparklineRenderer=null),this.sparklineScene=null,this.sparklineCamera=null}}const Tf=new Ny;sr.register(Tf);const Fy=!0,en="u-",Oy="uplot",By=en+"hz",zy=en+"vt",ky=en+"title",Hy=en+"wrap",Vy=en+"under",Gy=en+"over",Wy=en+"axis",wr=en+"off",Xy=en+"select",qy=en+"cursor-x",Yy=en+"cursor-y",$y=en+"cursor-pt",jy=en+"legend",Ky=en+"live",Zy=en+"inline",Jy=en+"series",Qy=en+"marker",td=en+"label",eM=en+"value",aa="width",oa="height",ia="top",nd="bottom",ps="left",Ol="right",ru="#000",id=ru+"0",Bl="mousemove",rd="mousedown",zl="mouseup",sd="mouseenter",ad="mouseleave",od="dblclick",tM="resize",nM="scroll",ld="change",Po="dppxchange",su="--",Fs=typeof window<"u",Lc=Fs?document:null,Es=Fs?window:null,iM=Fs?navigator:null;let xt,uo;function Dc(){let i=devicePixelRatio;xt!=i&&(xt=i,uo&&Uc(ld,uo,Dc),uo=matchMedia(`(min-resolution: ${xt-.001}dppx) and (max-resolution: ${xt+.001}dppx)`),Cr(ld,uo,Dc),Es.dispatchEvent(new CustomEvent(Po)))}function Nn(i,e){if(e!=null){let t=i.classList;!t.contains(e)&&t.add(e)}}function Ic(i,e){let t=i.classList;t.contains(e)&&t.remove(e)}function Ut(i,e,t){i.style[e]=t+"px"}function Qn(i,e,t,n){let r=Lc.createElement(i);return e!=null&&Nn(r,e),t!=null&&t.insertBefore(r,n),r}function Vn(i,e){return Qn("div",i,e)}const cd=new WeakMap;function fi(i,e,t,n,r){let s="translate("+e+"px,"+t+"px)",a=cd.get(i);s!=a&&(i.style.transform=s,cd.set(i,s),e<0||t<0||e>n||t>r?Nn(i,wr):Ic(i,wr))}const ud=new WeakMap;function hd(i,e,t){let n=e+t,r=ud.get(i);n!=r&&(ud.set(i,n),i.style.background=e,i.style.borderColor=t)}const dd=new WeakMap;function fd(i,e,t,n){let r=e+""+t,s=dd.get(i);r!=s&&(dd.set(i,r),i.style.height=t+"px",i.style.width=e+"px",i.style.marginLeft=n?-e/2+"px":0,i.style.marginTop=n?-t/2+"px":0)}const au={passive:!0},rM={...au,capture:!0};function Cr(i,e,t,n){e.addEventListener(i,t,n?rM:au)}function Uc(i,e,t,n){e.removeEventListener(i,t,au)}Fs&&Dc();function ei(i,e,t,n){let r;t=t||0,n=n||e.length-1;let s=n<=2147483647;for(;n-t>1;)r=s?t+n>>1:On((t+n)/2),e[r]<i?t=r:n=r;return i-e[t]<=e[n]-i?t:n}function wf(i){return(t,n,r)=>{let s=-1,a=-1;for(let o=n;o<=r;o++)if(i(t[o])){s=o;break}for(let o=r;o>=n;o--)if(i(t[o])){a=o;break}return[s,a]}}const Af=i=>i!=null,Rf=i=>i!=null&&i>0,Oo=wf(Af),sM=wf(Rf);function aM(i,e,t,n=0,r=!1){let s=r?sM:Oo,a=r?Rf:Af;[e,t]=s(i,e,t);let o=i[e],l=i[e];if(e>-1)if(n==1)o=i[e],l=i[t];else if(n==-1)o=i[t],l=i[e];else for(let c=e;c<=t;c++){let u=i[c];a(u)&&(u<o?o=u:u>l&&(l=u))}return[o??wt,l??-wt]}function Bo(i,e,t,n){let r=gd(i),s=gd(e);i==e&&(r==-1?(i*=t,e/=t):(i/=t,e*=t));let a=t==10?Ni:Cf,o=r==1?On:Gn,l=s==1?Gn:On,c=o(a(Kt(i))),u=l(a(Kt(e))),h=Ps(t,c),d=Ps(t,u);return t==10&&(c<0&&(h=At(h,-c)),u<0&&(d=At(d,-u))),n||t==2?(i=h*r,e=d*s):(i=If(i,h),e=zo(e,d)),[i,e]}function ou(i,e,t,n){let r=Bo(i,e,t,n);return i==0&&(r[0]=0),e==0&&(r[1]=0),r}const lu=.1,pd={mode:3,pad:lu},fa={pad:0,soft:null,mode:0},oM={min:fa,max:fa};function Lo(i,e,t,n){return ko(t)?md(i,e,t):(fa.pad=t,fa.soft=n?0:null,fa.mode=n?3:0,md(i,e,oM))}function _t(i,e){return i??e}function lM(i,e,t){for(e=_t(e,0),t=_t(t,i.length-1);e<=t;){if(i[e]!=null)return!0;e++}return!1}function md(i,e,t){let n=t.min,r=t.max,s=_t(n.pad,0),a=_t(r.pad,0),o=_t(n.hard,-wt),l=_t(r.hard,wt),c=_t(n.soft,wt),u=_t(r.soft,-wt),h=_t(n.mode,0),d=_t(r.mode,0),m=e-i,_=Ni(m),v=wn(Kt(i),Kt(e)),p=Ni(v),f=Kt(p-_);(m<1e-24||f>10)&&(m=0,(i==0||e==0)&&(m=1e-24,h==2&&c!=wt&&(s=0),d==2&&u!=-wt&&(a=0)));let E=m||v||1e3,S=Ni(E),T=Ps(10,On(S)),z=E*(m==0?i==0?.1:1:s),R=At(If(i-z,T/10),24),L=i>=c&&(h==1||h==3&&R<=c||h==2&&R>=c)?c:wt,O=wn(o,R<L&&i>=L?L:ii(L,R)),w=E*(m==0?e==0?.1:1:a),x=At(zo(e+w,T/10),24),C=e<=u&&(d==1||d==3&&x>=u||d==2&&x<=u)?u:-wt,j=ii(l,x>C&&e<=C?C:wn(C,x));return O==j&&O==0&&(j=100),[O,j]}const cM=new Intl.NumberFormat(Fs?iM.language:"en-US"),cu=i=>cM.format(i),Bn=Math,yo=Bn.PI,Kt=Bn.abs,On=Bn.floor,jt=Bn.round,Gn=Bn.ceil,ii=Bn.min,wn=Bn.max,Ps=Bn.pow,gd=Bn.sign,Ni=Bn.log10,Cf=Bn.log2,uM=(i,e=1)=>Bn.sinh(i)*e,kl=(i,e=1)=>Bn.asinh(i/e),wt=1/0;function _d(i){return(Ni((i^i>>31)-(i>>31))|0)+1}function Nc(i,e,t){return ii(wn(i,e),t)}function Pf(i){return typeof i=="function"}function ht(i){return Pf(i)?i:()=>i}const hM=()=>{},Lf=i=>i,Df=(i,e)=>e,dM=i=>null,vd=i=>!0,xd=(i,e)=>i==e,fM=/\.\d*?(?=9{6,}|0{6,})/gm,Ir=i=>{if(Nf(i)||ar.has(i))return i;const e=`${i}`,t=e.match(fM);if(t==null)return i;let n=t[0].length-1;if(e.indexOf("e-")!=-1){let[r,s]=e.split("e");return+`${Ir(r)}e${s}`}return At(i,n)};function Sr(i,e){return Ir(At(Ir(i/e))*e)}function zo(i,e){return Ir(Gn(Ir(i/e))*e)}function If(i,e){return Ir(On(Ir(i/e))*e)}function At(i,e=0){if(Nf(i))return i;let t=10**e,n=i*t*(1+Number.EPSILON);return jt(n)/t}const ar=new Map;function Uf(i){return((""+i).split(".")[1]||"").length}function _a(i,e,t,n){let r=[],s=n.map(Uf);for(let a=e;a<t;a++){let o=Kt(a),l=At(Ps(i,a),o);for(let c=0;c<n.length;c++){let u=i==10?+`${n[c]}e${a}`:n[c]*l,h=(a>=0?0:o)+(a>=s[c]?0:s[c]),d=i==10?u:At(u,h);r.push(d),ar.set(d,h)}}return r}const pa={},uu=[],Ls=[null,null],Zi=Array.isArray,Nf=Number.isInteger,pM=i=>i===void 0;function yd(i){return typeof i=="string"}function ko(i){let e=!1;if(i!=null){let t=i.constructor;e=t==null||t==Object}return e}function mM(i){return i!=null&&typeof i=="object"}const gM=Object.getPrototypeOf(Uint8Array),Ff="__proto__";function Ds(i,e=ko){let t;if(Zi(i)){let n=i.find(r=>r!=null);if(Zi(n)||e(n)){t=Array(i.length);for(let r=0;r<i.length;r++)t[r]=Ds(i[r],e)}else t=i.slice()}else if(i instanceof gM)t=i.slice();else if(e(i)){t={};for(let n in i)n!=Ff&&(t[n]=Ds(i[n],e))}else t=i;return t}function qt(i){let e=arguments;for(let t=1;t<e.length;t++){let n=e[t];for(let r in n)r!=Ff&&(ko(i[r])?qt(i[r],Ds(n[r])):i[r]=Ds(n[r]))}return i}const _M=0,vM=1,xM=2;function yM(i,e,t){for(let n=0,r,s=-1;n<e.length;n++){let a=e[n];if(a>s){for(r=a-1;r>=0&&i[r]==null;)i[r--]=null;for(r=a+1;r<t&&i[r]==null;)i[s=r++]=null}}}function MM(i,e){if(bM(i)){let a=i[0].slice();for(let o=1;o<i.length;o++)a.push(...i[o].slice(1));return TM(a[0])||(a=EM(a)),a}let t=new Set;for(let a=0;a<i.length;a++){let l=i[a][0],c=l.length;for(let u=0;u<c;u++)t.add(l[u])}let n=[Array.from(t).sort((a,o)=>a-o)],r=n[0].length,s=new Map;for(let a=0;a<r;a++)s.set(n[0][a],a);for(let a=0;a<i.length;a++){let o=i[a],l=o[0];for(let c=1;c<o.length;c++){let u=o[c],h=Array(r).fill(void 0),d=e?e[a][c]:vM,m=[];for(let _=0;_<u.length;_++){let v=u[_],p=s.get(l[_]);v===null?d!=_M&&(h[p]=v,d==xM&&m.push(p)):h[p]=v}yM(h,m,r),n.push(h)}}return n}const SM=typeof queueMicrotask>"u"?i=>Promise.resolve().then(i):queueMicrotask;function EM(i){let e=i[0],t=e.length,n=Array(t);for(let s=0;s<n.length;s++)n[s]=s;n.sort((s,a)=>e[s]-e[a]);let r=[];for(let s=0;s<i.length;s++){let a=i[s],o=Array(t);for(let l=0;l<t;l++)o[l]=a[n[l]];r.push(o)}return r}function bM(i){let e=i[0][0],t=e.length;for(let n=1;n<i.length;n++){let r=i[n][0];if(r.length!=t)return!1;if(r!=e){for(let s=0;s<t;s++)if(r[s]!=e[s])return!1}}return!0}function TM(i,e=100){const t=i.length;if(t<=1)return!0;let n=0,r=t-1;for(;n<=r&&i[n]==null;)n++;for(;r>=n&&i[r]==null;)r--;if(r<=n)return!0;const s=wn(1,On((r-n+1)/e));for(let a=i[n],o=n+s;o<=r;o+=s){const l=i[o];if(l!=null){if(l<=a)return!1;a=l}}return!0}const Of=["January","February","March","April","May","June","July","August","September","October","November","December"],Bf=["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];function zf(i){return i.slice(0,3)}const wM=Bf.map(zf),AM=Of.map(zf),RM={MMMM:Of,MMM:AM,WWWW:Bf,WWW:wM};function ra(i){return(i<10?"0":"")+i}function CM(i){return(i<10?"00":i<100?"0":"")+i}const PM={YYYY:i=>i.getFullYear(),YY:i=>(i.getFullYear()+"").slice(2),MMMM:(i,e)=>e.MMMM[i.getMonth()],MMM:(i,e)=>e.MMM[i.getMonth()],MM:i=>ra(i.getMonth()+1),M:i=>i.getMonth()+1,DD:i=>ra(i.getDate()),D:i=>i.getDate(),WWWW:(i,e)=>e.WWWW[i.getDay()],WWW:(i,e)=>e.WWW[i.getDay()],HH:i=>ra(i.getHours()),H:i=>i.getHours(),h:i=>{let e=i.getHours();return e==0?12:e>12?e-12:e},AA:i=>i.getHours()>=12?"PM":"AM",aa:i=>i.getHours()>=12?"pm":"am",a:i=>i.getHours()>=12?"p":"a",mm:i=>ra(i.getMinutes()),m:i=>i.getMinutes(),ss:i=>ra(i.getSeconds()),s:i=>i.getSeconds(),fff:i=>CM(i.getMilliseconds())};function hu(i,e){e=e||RM;let t=[],n=/\{([a-z]+)\}|[^{]+/gi,r;for(;r=n.exec(i);)t.push(r[0][0]=="{"?PM[r[1]]:r[0]);return s=>{let a="";for(let o=0;o<t.length;o++)a+=typeof t[o]=="string"?t[o]:t[o](s,e);return a}}const LM=new Intl.DateTimeFormat().resolvedOptions().timeZone;function DM(i,e){let t;return e=="UTC"||e=="Etc/UTC"?t=new Date(+i+i.getTimezoneOffset()*6e4):e==LM?t=i:(t=new Date(i.toLocaleString("en-US",{timeZone:e})),t.setMilliseconds(i.getMilliseconds())),t}const kf=i=>i%1==0,Do=[1,2,2.5,5],IM=_a(10,-32,0,Do),Hf=_a(10,0,32,Do),UM=Hf.filter(kf),Er=IM.concat(Hf),du=`
`,Vf="{YYYY}",Md=du+Vf,Gf="{M}/{D}",la=du+Gf,ho=la+"/{YY}",Wf="{aa}",NM="{h}:{mm}",ms=NM+Wf,Sd=du+ms,Ed=":{ss}",yt=null;function Xf(i){let e=i*1e3,t=e*60,n=t*60,r=n*24,s=r*30,a=r*365,l=(i==1?_a(10,0,3,Do).filter(kf):_a(10,-3,0,Do)).concat([e,e*5,e*10,e*15,e*30,t,t*5,t*10,t*15,t*30,n,n*2,n*3,n*4,n*6,n*8,n*12,r,r*2,r*3,r*4,r*5,r*6,r*7,r*8,r*9,r*10,r*15,s,s*2,s*3,s*4,s*6,a,a*2,a*5,a*10,a*25,a*50,a*100]);const c=[[a,Vf,yt,yt,yt,yt,yt,yt,1],[r*28,"{MMM}",Md,yt,yt,yt,yt,yt,1],[r,Gf,Md,yt,yt,yt,yt,yt,1],[n,"{h}"+Wf,ho,yt,la,yt,yt,yt,1],[t,ms,ho,yt,la,yt,yt,yt,1],[e,Ed,ho+" "+ms,yt,la+" "+ms,yt,Sd,yt,1],[i,Ed+".{fff}",ho+" "+ms,yt,la+" "+ms,yt,Sd,yt,1]];function u(h){return(d,m,_,v,p,f)=>{let E=[],S=p>=a,T=p>=s&&p<a,z=h(_),R=At(z*i,3),L=Hl(z.getFullYear(),S?0:z.getMonth(),T||S?1:z.getDate()),O=At(L*i,3);if(T||S){let w=T?p/s:0,x=S?p/a:0,C=R==O?R:At(Hl(L.getFullYear()+x,L.getMonth()+w,1)*i,3),j=new Date(jt(C/i)),B=j.getFullYear(),K=j.getMonth();for(let W=0;C<=v;W++){let J=Hl(B+x*W,K+w*W,1),q=J-h(At(J*i,3));C=At((+J+q)*i,3),C<=v&&E.push(C)}}else{let w=p>=r?r:p,x=On(_)-On(R),C=O+x+zo(R-O,w);E.push(C);let j=h(C),B=j.getHours()+j.getMinutes()/t+j.getSeconds()/n,K=p/n,W=d.axes[m]._space,J=f/W;for(;C=At(C+p,i==1?0:3),!(C>v);)if(K>1){let q=On(At(B+K,6))%24,he=h(C).getHours()-q;he>1&&(he=-1),C-=he*n,B=(B+K)%24;let ve=E[E.length-1];At((C-ve)/p,3)*J>=.7&&E.push(C)}else E.push(C)}return E}}return[l,c,u]}const[FM,OM,BM]=Xf(1),[zM,kM,HM]=Xf(.001);_a(2,-53,53,[1]);function bd(i,e){return i.map(t=>t.map((n,r)=>r==0||r==8||n==null?n:e(r==1||t[8]==0?n:t[1]+n)))}function Td(i,e){return(t,n,r,s,a)=>{let o=e.find(_=>a>=_[0])||e[e.length-1],l,c,u,h,d,m;return n.map(_=>{let v=i(_),p=v.getFullYear(),f=v.getMonth(),E=v.getDate(),S=v.getHours(),T=v.getMinutes(),z=v.getSeconds(),R=p!=l&&o[2]||f!=c&&o[3]||E!=u&&o[4]||S!=h&&o[5]||T!=d&&o[6]||z!=m&&o[7]||o[1];return l=p,c=f,u=E,h=S,d=T,m=z,R(v)})}}function VM(i,e){let t=hu(e);return(n,r,s,a,o)=>r.map(l=>t(i(l)))}function Hl(i,e,t){return new Date(i,e,t)}function wd(i,e){return e(i)}const GM="{YYYY}-{MM}-{DD} {h}:{mm}{aa}";function Ad(i,e){return(t,n,r,s)=>s==null?su:e(i(n))}function WM(i,e){let t=i.series[e];return t.width?t.stroke(i,e):t.points.width?t.points.stroke(i,e):null}function XM(i,e){return i.series[e].fill(i,e)}const qM={show:!0,live:!0,isolate:!1,mount:hM,markers:{show:!0,width:2,stroke:WM,fill:XM,dash:"solid"},idx:null,idxs:null,values:[]};function YM(i,e){let t=i.cursor.points,n=Vn(),r=t.size(i,e);Ut(n,aa,r),Ut(n,oa,r);let s=r/-2;Ut(n,"marginLeft",s),Ut(n,"marginTop",s);let a=t.width(i,e,r);return a&&Ut(n,"borderWidth",a),n}function $M(i,e){let t=i.series[e].points;return t._fill||t._stroke}function jM(i,e){let t=i.series[e].points;return t._stroke||t._fill}function KM(i,e){return i.series[e].points.size}const Vl=[0,0];function ZM(i,e,t){return Vl[0]=e,Vl[1]=t,Vl}function fo(i,e,t,n=!0){return r=>{r.button==0&&(!n||r.target==e)&&t(r)}}function Gl(i,e,t,n=!0){return r=>{(!n||r.target==e)&&t(r)}}const JM={show:!0,x:!0,y:!0,lock:!1,move:ZM,points:{one:!1,show:YM,size:KM,width:0,stroke:jM,fill:$M},bind:{mousedown:fo,mouseup:fo,click:fo,dblclick:fo,mousemove:Gl,mouseleave:Gl,mouseenter:Gl},drag:{setScale:!0,x:!0,y:!1,dist:0,uni:null,click:(i,e)=>{e.stopPropagation(),e.stopImmediatePropagation()},_x:!1,_y:!1},focus:{dist:(i,e,t,n,r)=>n-r,prox:-1,bias:0},hover:{skip:[void 0],prox:null,bias:0},left:-10,top:-10,idx:null,dataIdx:null,idxs:null,event:null},qf={show:!0,stroke:"rgba(0,0,0,0.07)",width:2},fu=qt({},qf,{filter:Df}),Yf=qt({},fu,{size:10}),$f=qt({},qf,{show:!1}),pu='12px system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji"',jf="bold "+pu,Kf=1.5,Rd={show:!0,scale:"x",stroke:ru,space:50,gap:5,alignTo:1,size:50,labelGap:0,labelSize:30,labelFont:jf,side:2,grid:fu,ticks:Yf,border:$f,font:pu,lineGap:Kf,rotate:0},QM="Value",eS="Time",Cd={show:!0,scale:"x",auto:!1,sorted:1,min:wt,max:-wt,idxs:[]};function tS(i,e,t,n,r){return e.map(s=>s==null?"":cu(s))}function nS(i,e,t,n,r,s,a){let o=[],l=ar.get(r)||0;t=a?t:At(zo(t,r),l);for(let c=t;c<=n;c=At(c+r,l))o.push(Object.is(c,-0)?0:c);return o}function Fc(i,e,t,n,r,s,a){const o=[],l=i.scales[i.axes[e].scale].log,c=l==10?Ni:Cf,u=On(c(t));r=Ps(l,u),l==10&&(r=Er[ei(r,Er)]);let h=t,d=r*l;l==10&&(d=Er[ei(d,Er)]);do o.push(h),h=h+r,l==10&&!ar.has(h)&&(h=At(h,ar.get(r))),h>=d&&(r=h,d=r*l,l==10&&(d=Er[ei(d,Er)]));while(h<=n);return o}function iS(i,e,t,n,r,s,a){let l=i.scales[i.axes[e].scale].asinh,c=n>l?Fc(i,e,wn(l,t),n,r):[l],u=n>=0&&t<=0?[0]:[];return(t<-l?Fc(i,e,wn(l,-n),-t,r):[l]).reverse().map(d=>-d).concat(u,c)}const Zf=/./,rS=/[12357]/,sS=/[125]/,Pd=/1/,Oc=(i,e,t,n)=>i.map((r,s)=>e==4&&r==0||s%n==0&&t.test(r.toExponential()[r<0?1:0])?r:null);function aS(i,e,t,n,r){let s=i.axes[t],a=s.scale,o=i.scales[a],l=i.valToPos,c=s._space,u=l(10,a),h=l(9,a)-u>=c?Zf:l(7,a)-u>=c?rS:l(5,a)-u>=c?sS:Pd;if(h==Pd){let d=Kt(l(1,a)-u);if(d<c)return Oc(e.slice().reverse(),o.distr,h,Gn(c/d)).reverse()}return Oc(e,o.distr,h,1)}function oS(i,e,t,n,r){let s=i.axes[t],a=s.scale,o=s._space,l=i.valToPos,c=Kt(l(1,a)-l(2,a));return c<o?Oc(e.slice().reverse(),3,Zf,Gn(o/c)).reverse():e}function lS(i,e,t,n){return n==null?su:e==null?"":cu(e)}const Ld={show:!0,scale:"y",stroke:ru,space:30,gap:5,alignTo:1,size:50,labelGap:0,labelSize:30,labelFont:jf,side:3,grid:fu,ticks:Yf,border:$f,font:pu,lineGap:Kf,rotate:0};function cS(i,e){let t=3+(i||1)*2;return At(t*e,3)}function uS(i,e){let{scale:t,idxs:n}=i.series[0],r=i._data[0],s=i.valToPos(r[n[0]],t,!0),a=i.valToPos(r[n[1]],t,!0),o=Kt(a-s),l=i.series[e],c=o/(l.points.space*xt);return n[1]-n[0]<=c}const Dd={scale:null,auto:!0,sorted:0,min:wt,max:-wt},Jf=(i,e,t,n,r)=>r,Id={show:!0,auto:!0,sorted:0,gaps:Jf,alpha:1,facets:[qt({},Dd,{scale:"x"}),qt({},Dd,{scale:"y"})]},Ud={scale:"y",auto:!0,sorted:0,show:!0,spanGaps:!1,gaps:Jf,alpha:1,points:{show:uS,filter:null},values:null,min:wt,max:-wt,idxs:[],path:null,clip:null};function hS(i,e,t,n,r){return t/10}const Qf={time:Fy,auto:!0,distr:1,log:10,asinh:1,min:null,max:null,dir:1,ori:0},dS=qt({},Qf,{time:!1,ori:1}),Nd={};function ep(i,e){let t=Nd[i];return t||(t={key:i,plots:[],sub(n){t.plots.push(n)},unsub(n){t.plots=t.plots.filter(r=>r!=n)},pub(n,r,s,a,o,l,c){for(let u=0;u<t.plots.length;u++)t.plots[u]!=r&&t.plots[u].pub(n,r,s,a,o,l,c)}},i!=null&&(Nd[i]=t)),t}const Is=1,Bc=2;function Ur(i,e,t){const n=i.mode,r=i.series[e],s=n==2?i._data[e]:i._data,a=i.scales,o=i.bbox;let l=s[0],c=n==2?s[1]:s[e],u=n==2?a[r.facets[0].scale]:a[i.series[0].scale],h=n==2?a[r.facets[1].scale]:a[r.scale],d=o.left,m=o.top,_=o.width,v=o.height,p=i.valToPosH,f=i.valToPosV;return u.ori==0?t(r,l,c,u,h,p,f,d,m,_,v,Vo,Os,Wo,np,rp):t(r,l,c,u,h,f,p,m,d,v,_,Go,Bs,_u,ip,sp)}function mu(i,e){let t=0,n=0,r=_t(i.bands,uu);for(let s=0;s<r.length;s++){let a=r[s];a.series[0]==e?t=a.dir:a.series[1]==e&&(a.dir==1?n|=1:n|=2)}return[t,n==1?-1:n==2?1:n==3?2:0]}function fS(i,e,t,n,r){let s=i.mode,a=i.series[e],o=s==2?a.facets[1].scale:a.scale,l=i.scales[o];return r==-1?l.min:r==1?l.max:l.distr==3?l.dir==1?l.min:l.max:0}function Fi(i,e,t,n,r,s){return Ur(i,e,(a,o,l,c,u,h,d,m,_,v,p)=>{let f=a.pxRound;const E=c.dir*(c.ori==0?1:-1),S=c.ori==0?Os:Bs;let T,z;E==1?(T=t,z=n):(T=n,z=t);let R=f(h(o[T],c,v,m)),L=f(d(l[T],u,p,_)),O=f(h(o[z],c,v,m)),w=f(d(s==1?u.max:u.min,u,p,_)),x=new Path2D(r);return S(x,O,w),S(x,R,w),S(x,R,L),x})}function Ho(i,e,t,n,r,s){let a=null;if(i.length>0){a=new Path2D;const o=e==0?Wo:_u;let l=t;for(let h=0;h<i.length;h++){let d=i[h];if(d[1]>d[0]){let m=d[0]-l;m>0&&o(a,l,n,m,n+s),l=d[1]}}let c=t+r-l,u=10;c>0&&o(a,l,n-u/2,c,n+s+u)}return a}function pS(i,e,t){let n=i[i.length-1];n&&n[0]==e?n[1]=t:i.push([e,t])}function gu(i,e,t,n,r,s,a){let o=[],l=i.length;for(let c=r==1?t:n;c>=t&&c<=n;c+=r)if(e[c]===null){let h=c,d=c;if(r==1)for(;++c<=n&&e[c]===null;)d=c;else for(;--c>=t&&e[c]===null;)d=c;let m=s(i[h]),_=d==h?m:s(i[d]),v=h-r;m=a<=0&&v>=0&&v<l?s(i[v]):m;let f=d+r;_=a>=0&&f>=0&&f<l?s(i[f]):_,_>=m&&o.push([m,_])}return o}function Fd(i){return i==0?Lf:i==1?jt:e=>Sr(e,i)}function tp(i){let e=i==0?Vo:Go,t=i==0?(r,s,a,o,l,c)=>{r.arcTo(s,a,o,l,c)}:(r,s,a,o,l,c)=>{r.arcTo(a,s,l,o,c)},n=i==0?(r,s,a,o,l)=>{r.rect(s,a,o,l)}:(r,s,a,o,l)=>{r.rect(a,s,l,o)};return(r,s,a,o,l,c=0,u=0)=>{c==0&&u==0?n(r,s,a,o,l):(c=ii(c,o/2,l/2),u=ii(u,o/2,l/2),e(r,s+c,a),t(r,s+o,a,s+o,a+l,c),t(r,s+o,a+l,s,a+l,u),t(r,s,a+l,s,a,u),t(r,s,a,s+o,a,c),r.closePath())}}const Vo=(i,e,t)=>{i.moveTo(e,t)},Go=(i,e,t)=>{i.moveTo(t,e)},Os=(i,e,t)=>{i.lineTo(e,t)},Bs=(i,e,t)=>{i.lineTo(t,e)},Wo=tp(0),_u=tp(1),np=(i,e,t,n,r,s)=>{i.arc(e,t,n,r,s)},ip=(i,e,t,n,r,s)=>{i.arc(t,e,n,r,s)},rp=(i,e,t,n,r,s,a)=>{i.bezierCurveTo(e,t,n,r,s,a)},sp=(i,e,t,n,r,s,a)=>{i.bezierCurveTo(t,e,r,n,a,s)};function ap(i){return(e,t,n,r,s)=>Ur(e,t,(a,o,l,c,u,h,d,m,_,v,p)=>{let{pxRound:f,points:E}=a,S,T;c.ori==0?(S=Vo,T=np):(S=Go,T=ip);const z=At(E.width*xt,3);let R=(E.size-E.width)/2*xt,L=At(R*2,3),O=new Path2D,w=new Path2D,{left:x,top:C,width:j,height:B}=e.bbox;Wo(w,x-L,C-L,j+L*2,B+L*2);const K=W=>{if(l[W]!=null){let J=f(h(o[W],c,v,m)),q=f(d(l[W],u,p,_));S(O,J+R,q),T(O,J,q,R,0,yo*2)}};if(s)s.forEach(K);else for(let W=n;W<=r;W++)K(W);return{stroke:z>0?O:null,fill:O,clip:w,flags:Is|Bc}})}function op(i){return(e,t,n,r,s,a)=>{n!=r&&(s!=n&&a!=n&&i(e,t,n),s!=r&&a!=r&&i(e,t,r),i(e,t,a))}}const mS=op(Os),gS=op(Bs);function lp(i){const e=_t(i==null?void 0:i.alignGaps,0);return(t,n,r,s)=>Ur(t,n,(a,o,l,c,u,h,d,m,_,v,p)=>{[r,s]=Oo(l,r,s);let f=a.pxRound,E=B=>f(h(B,c,v,m)),S=B=>f(d(B,u,p,_)),T,z;c.ori==0?(T=Os,z=mS):(T=Bs,z=gS);const R=c.dir*(c.ori==0?1:-1),L={stroke:new Path2D,fill:null,clip:null,band:null,gaps:null,flags:Is},O=L.stroke;let w=!1;if(s-r>=v*4){let B=xe=>t.posToVal(xe,c.key,!0),K=null,W=null,J,q,ee,me=E(o[R==1?r:s]),he=E(o[r]),ve=E(o[s]),Te=B(R==1?he+1:ve-1);for(let xe=R==1?r:s;xe>=r&&xe<=s;xe+=R){let te=o[xe],ye=(R==1?te<Te:te>Te)?me:E(te),de=l[xe];ye==me?de!=null?(q=de,K==null?(T(O,ye,S(q)),J=K=W=q):q<K?K=q:q>W&&(W=q)):de===null&&(w=!0):(K!=null&&z(O,me,S(K),S(W),S(J),S(q)),de!=null?(q=de,T(O,ye,S(q)),K=W=J=q):(K=W=null,de===null&&(w=!0)),me=ye,Te=B(me+R))}K!=null&&K!=W&&ee!=me&&z(O,me,S(K),S(W),S(J),S(q))}else for(let B=R==1?r:s;B>=r&&B<=s;B+=R){let K=l[B];K===null?w=!0:K!=null&&T(O,E(o[B]),S(K))}let[C,j]=mu(t,n);if(a.fill!=null||C!=0){let B=L.fill=new Path2D(O),K=a.fillTo(t,n,a.min,a.max,C),W=S(K),J=E(o[r]),q=E(o[s]);R==-1&&([q,J]=[J,q]),T(B,q,W),T(B,J,W)}if(!a.spanGaps){let B=[];w&&B.push(...gu(o,l,r,s,R,E,e)),L.gaps=B=a.gaps(t,n,r,s,B),L.clip=Ho(B,c.ori,m,_,v,p)}return j!=0&&(L.band=j==2?[Fi(t,n,r,s,O,-1),Fi(t,n,r,s,O,1)]:Fi(t,n,r,s,O,j)),L})}function _S(i){const e=_t(i.align,1),t=_t(i.ascDesc,!1),n=_t(i.alignGaps,0),r=_t(i.extend,!1);return(s,a,o,l)=>Ur(s,a,(c,u,h,d,m,_,v,p,f,E,S)=>{[o,l]=Oo(h,o,l);let T=c.pxRound,{left:z,width:R}=s.bbox,L=he=>T(_(he,d,E,p)),O=he=>T(v(he,m,S,f)),w=d.ori==0?Os:Bs;const x={stroke:new Path2D,fill:null,clip:null,band:null,gaps:null,flags:Is},C=x.stroke,j=d.dir*(d.ori==0?1:-1);let B=O(h[j==1?o:l]),K=L(u[j==1?o:l]),W=K,J=K;r&&e==-1&&(J=z,w(C,J,B)),w(C,K,B);for(let he=j==1?o:l;he>=o&&he<=l;he+=j){let ve=h[he];if(ve==null)continue;let Te=L(u[he]),xe=O(ve);e==1?w(C,Te,B):w(C,W,xe),w(C,Te,xe),B=xe,W=Te}let q=W;r&&e==1&&(q=z+R,w(C,q,B));let[ee,me]=mu(s,a);if(c.fill!=null||ee!=0){let he=x.fill=new Path2D(C),ve=c.fillTo(s,a,c.min,c.max,ee),Te=O(ve);w(he,q,Te),w(he,J,Te)}if(!c.spanGaps){let he=[];he.push(...gu(u,h,o,l,j,L,n));let ve=c.width*xt/2,Te=t||e==1?ve:-ve,xe=t||e==-1?-ve:ve;he.forEach(te=>{te[0]+=Te,te[1]+=xe}),x.gaps=he=c.gaps(s,a,o,l,he),x.clip=Ho(he,d.ori,p,f,E,S)}return me!=0&&(x.band=me==2?[Fi(s,a,o,l,C,-1),Fi(s,a,o,l,C,1)]:Fi(s,a,o,l,C,me)),x})}function Od(i,e,t,n,r,s,a=wt){if(i.length>1){let o=null;for(let l=0,c=1/0;l<i.length;l++)if(e[l]!==void 0){if(o!=null){let u=Kt(i[l]-i[o]);u<c&&(c=u,a=Kt(t(i[l],n,r,s)-t(i[o],n,r,s)))}o=l}}return a}function vS(i){i=i||pa;const e=_t(i.size,[.6,wt,1]),t=i.align||0,n=i.gap||0;let r=i.radius;r=r==null?[0,0]:typeof r=="number"?[r,0]:r;const s=ht(r),a=1-e[0],o=_t(e[1],wt),l=_t(e[2],1),c=_t(i.disp,pa),u=_t(i.each,m=>{}),{fill:h,stroke:d}=c;return(m,_,v,p)=>Ur(m,_,(f,E,S,T,z,R,L,O,w,x,C)=>{let j=f.pxRound,B=t,K=n*xt,W=o*xt,J=l*xt,q,ee;T.ori==0?[q,ee]=s(m,_):[ee,q]=s(m,_);const me=T.dir*(T.ori==0?1:-1);let he=T.ori==0?Wo:_u,ve=T.ori==0?u:(G,Ee,ge,Ae,je,pe,we)=>{u(G,Ee,ge,je,Ae,we,pe)},Te=_t(m.bands,uu).find(G=>G.series[0]==_),xe=Te!=null?Te.dir:0,te=f.fillTo(m,_,f.min,f.max,xe),ce=j(L(te,z,C,w)),ye,de,Be,Ve=x,Ne=j(f.width*xt),dt=!1,U=null,ut=null,nt=null,ot=null;h!=null&&(Ne==0||d!=null)&&(dt=!0,U=h.values(m,_,v,p),ut=new Map,new Set(U).forEach(G=>{G!=null&&ut.set(G,new Path2D)}),Ne>0&&(nt=d.values(m,_,v,p),ot=new Map,new Set(nt).forEach(G=>{G!=null&&ot.set(G,new Path2D)})));let{x0:Fe,size:St}=c;if(Fe!=null&&St!=null){B=1,E=Fe.values(m,_,v,p),Fe.unit==2&&(E=E.map(ge=>m.posToVal(O+ge*x,T.key,!0)));let G=St.values(m,_,v,p);St.unit==2?de=G[0]*x:de=R(G[0],T,x,O)-R(0,T,x,O),Ve=Od(E,S,R,T,x,O,Ve),Be=Ve-de+K}else Ve=Od(E,S,R,T,x,O,Ve),Be=Ve*a+K,de=Ve-Be;Be<1&&(Be=0),Ne>=de/2&&(Ne=0),Be<5&&(j=Lf);let qe=Be>0,We=Ve-Be-(qe?Ne:0);de=j(Nc(We,J,W)),ye=(B==0?de/2:B==me?0:de)-B*me*((B==0?K/2:0)+(qe?Ne/2:0));const D={stroke:null,fill:null,clip:null,band:null,gaps:null,flags:0},M=dt?null:new Path2D;let Z=null;if(Te!=null)Z=m.data[Te.series[1]];else{let{y0:G,y1:Ee}=c;G!=null&&Ee!=null&&(S=Ee.values(m,_,v,p),Z=G.values(m,_,v,p))}let oe=q*de,Q=ee*de;for(let G=me==1?v:p;G>=v&&G<=p;G+=me){let Ee=S[G];if(Ee==null)continue;if(Z!=null){let Se=Z[G]??0;if(Ee-Se==0)continue;ce=L(Se,z,C,w)}let ge=T.distr!=2||c!=null?E[G]:G,Ae=R(ge,T,x,O),je=L(_t(Ee,te),z,C,w),pe=j(Ae-ye),we=j(wn(je,ce)),Ke=j(ii(je,ce)),ze=we-Ke;if(Ee!=null){let Se=Ee<0?Q:oe,ke=Ee<0?oe:Q;dt?(Ne>0&&nt[G]!=null&&he(ot.get(nt[G]),pe,Ke+On(Ne/2),de,wn(0,ze-Ne),Se,ke),U[G]!=null&&he(ut.get(U[G]),pe,Ke+On(Ne/2),de,wn(0,ze-Ne),Se,ke)):he(M,pe,Ke+On(Ne/2),de,wn(0,ze-Ne),Se,ke),ve(m,_,G,pe-Ne/2,Ke,de+Ne,ze)}}return Ne>0?D.stroke=dt?ot:M:dt||(D._fill=f.width==0?f._fill:f._stroke??f._fill,D.width=0),D.fill=dt?ut:M,D})}function xS(i,e){const t=_t(e==null?void 0:e.alignGaps,0);return(n,r,s,a)=>Ur(n,r,(o,l,c,u,h,d,m,_,v,p,f)=>{[s,a]=Oo(c,s,a);let E=o.pxRound,S=q=>E(d(q,u,p,_)),T=q=>E(m(q,h,f,v)),z,R,L;u.ori==0?(z=Vo,L=Os,R=rp):(z=Go,L=Bs,R=sp);const O=u.dir*(u.ori==0?1:-1);let w=S(l[O==1?s:a]),x=w,C=[],j=[];for(let q=O==1?s:a;q>=s&&q<=a;q+=O)if(c[q]!=null){let me=l[q],he=S(me);C.push(x=he),j.push(T(c[q]))}const B={stroke:i(C,j,z,L,R,E),fill:null,clip:null,band:null,gaps:null,flags:Is},K=B.stroke;let[W,J]=mu(n,r);if(o.fill!=null||W!=0){let q=B.fill=new Path2D(K),ee=o.fillTo(n,r,o.min,o.max,W),me=T(ee);L(q,x,me),L(q,w,me)}if(!o.spanGaps){let q=[];q.push(...gu(l,c,s,a,O,S,t)),B.gaps=q=o.gaps(n,r,s,a,q),B.clip=Ho(q,u.ori,_,v,p,f)}return J!=0&&(B.band=J==2?[Fi(n,r,s,a,K,-1),Fi(n,r,s,a,K,1)]:Fi(n,r,s,a,K,J)),B})}function yS(i){return xS(MS,i)}function MS(i,e,t,n,r,s){const a=i.length;if(a<2)return null;const o=new Path2D;if(t(o,i[0],e[0]),a==2)n(o,i[1],e[1]);else{let l=Array(a),c=Array(a-1),u=Array(a-1),h=Array(a-1);for(let d=0;d<a-1;d++)u[d]=e[d+1]-e[d],h[d]=i[d+1]-i[d],c[d]=u[d]/h[d];l[0]=c[0];for(let d=1;d<a-1;d++)c[d]===0||c[d-1]===0||c[d-1]>0!=c[d]>0?l[d]=0:(l[d]=3*(h[d-1]+h[d])/((2*h[d]+h[d-1])/c[d-1]+(h[d]+2*h[d-1])/c[d]),isFinite(l[d])||(l[d]=0));l[a-1]=c[a-2];for(let d=0;d<a-1;d++)r(o,i[d]+h[d]/3,e[d]+l[d]*h[d]/3,i[d+1]-h[d]/3,e[d+1]-l[d+1]*h[d]/3,i[d+1],e[d+1])}return o}const zc=new Set;function Bd(){for(let i of zc)i.syncRect(!0)}Fs&&(Cr(tM,Es,Bd),Cr(nM,Es,Bd,!0),Cr(Po,Es,()=>{cn.pxRatio=xt}));const SS=lp(),ES=ap();function zd(i,e,t,n){return(n?[i[0],i[1]].concat(i.slice(2)):[i[0]].concat(i.slice(1))).map((s,a)=>kc(s,a,e,t))}function bS(i,e){return i.map((t,n)=>n==0?{}:qt({},e,t))}function kc(i,e,t,n){return qt({},e==0?t:n,i)}function cp(i,e,t){return e==null?Ls:[e,t]}const TS=cp;function wS(i,e,t){return e==null?Ls:Lo(e,t,lu,!0)}function up(i,e,t,n){return e==null?Ls:Bo(e,t,i.scales[n].log,!1)}const AS=up;function hp(i,e,t,n){return e==null?Ls:ou(e,t,i.scales[n].log,!1)}const RS=hp;function CS(i,e,t,n,r){let s=wn(_d(i),_d(e)),a=e-i,o=ei(r/n*a,t);do{let l=t[o],c=n*l/a;if(c>=r&&s+(l<5?ar.get(l):0)<=17)return[l,c]}while(++o<t.length);return[0,0]}function kd(i){let e,t;return i=i.replace(/(\d+)px/,(n,r)=>(e=jt((t=+r)*xt))+"px"),[i,e,t]}function PS(i){i.show&&[i.font,i.labelFont].forEach(e=>{let t=At(e[2]*xt,1);e[0]=e[0].replace(/[0-9.]+px/,t+"px"),e[1]=t})}function cn(i,e,t){const n={mode:_t(i.mode,1)},r=n.mode;function s(g,y,A,P){let F=y.valToPct(g);return P+A*(y.dir==-1?1-F:F)}function a(g,y,A,P){let F=y.valToPct(g);return P+A*(y.dir==-1?F:1-F)}function o(g,y,A,P){return y.ori==0?s(g,y,A,P):a(g,y,A,P)}n.valToPosH=s,n.valToPosV=a;let l=!1;n.status=0;const c=n.root=Vn(Oy);if(i.id!=null&&(c.id=i.id),Nn(c,i.class),i.title){let g=Vn(ky,c);g.textContent=i.title}const u=Qn("canvas"),h=n.ctx=u.getContext("2d"),d=Vn(Hy,c);Cr("click",d,g=>{g.target===_&&(Lt!=kr||zt!=Hr)&&dn.click(n,g)},!0);const m=n.under=Vn(Vy,d);d.appendChild(u);const _=n.over=Vn(Gy,d);i=Ds(i);const v=+_t(i.pxAlign,1),p=Fd(v);(i.plugins||[]).forEach(g=>{g.opts&&(i=g.opts(n,i)||i)});const f=i.ms||.001,E=n.series=r==1?zd(i.series||[],Cd,Ud,!1):bS(i.series||[null],Id),S=n.axes=zd(i.axes||[],Rd,Ld,!0),T=n.scales={},z=n.bands=i.bands||[];z.forEach(g=>{g.fill=ht(g.fill||null),g.dir=_t(g.dir,-1)});const R=r==2?E[1].facets[0].scale:E[0].scale,L={axes:xp,series:Rn},O=(i.drawOrder||["axes","series"]).map(g=>L[g]);function w(g){const y=g.distr==3?A=>Ni(A>0?A:g.clamp(n,A,g.min,g.max,g.key)):g.distr==4?A=>kl(A,g.asinh):g.distr==100?A=>g.fwd(A):A=>A;return A=>{let P=y(A),{_min:F,_max:Y}=g,se=Y-F;return(P-F)/se}}function x(g){let y=T[g];if(y==null){let A=(i.scales||pa)[g]||pa;if(A.from!=null){x(A.from);let P=qt({},T[A.from],A,{key:g});P.valToPct=w(P),T[g]=P}else{y=T[g]=qt({},g==R?Qf:dS,A),y.key=g;let P=y.time,F=y.range,Y=Zi(F);if((g!=R||r==2&&!P)&&(Y&&(F[0]==null||F[1]==null)&&(F={min:F[0]==null?pd:{mode:1,hard:F[0],soft:F[0]},max:F[1]==null?pd:{mode:1,hard:F[1],soft:F[1]}},Y=!1),!Y&&ko(F))){let se=F;F=(fe,Me,Le)=>Me==null?Ls:Lo(Me,Le,se)}y.range=ht(F||(P?TS:g==R?y.distr==3?AS:y.distr==4?RS:cp:y.distr==3?up:y.distr==4?hp:wS)),y.auto=ht(Y?!1:y.auto),y.clamp=ht(y.clamp||hS),y._min=y._max=null,y.valToPct=w(y)}}}x("x"),x("y"),r==1&&E.forEach(g=>{x(g.scale)}),S.forEach(g=>{x(g.scale)});for(let g in i.scales)x(g);const C=T[R],j=C.distr;let B,K;C.ori==0?(Nn(c,By),B=s,K=a):(Nn(c,zy),B=a,K=s);const W={};for(let g in T){let y=T[g];(y.min!=null||y.max!=null)&&(W[g]={min:y.min,max:y.max},y.min=y.max=null)}const J=i.tzDate||(g=>new Date(jt(g/f))),q=i.fmtDate||hu,ee=f==1?BM(J):HM(J),me=Td(J,bd(f==1?OM:kM,q)),he=Ad(J,wd(GM,q)),ve=[],Te=n.legend=qt({},qM,i.legend),xe=n.cursor=qt({},JM,{drag:{y:r==2}},i.cursor),te=Te.show,ce=xe.show,ye=Te.markers;Te.idxs=ve,ye.width=ht(ye.width),ye.dash=ht(ye.dash),ye.stroke=ht(ye.stroke),ye.fill=ht(ye.fill);let de,Be,Ve,Ne=[],dt=[],U,ut=!1,nt={};if(Te.live){const g=E[1]?E[1].values:null;ut=g!=null,U=ut?g(n,1,0):{_:0};for(let y in U)nt[y]=su}if(te)if(de=Qn("table",jy,c),Ve=Qn("tbody",null,de),Te.mount(n,de),ut){Be=Qn("thead",null,de,Ve);let g=Qn("tr",null,Be);Qn("th",null,g);for(var ot in U)Qn("th",td,g).textContent=ot}else Nn(de,Zy),Te.live&&Nn(de,Ky);const Fe={show:!0},St={show:!1};function qe(g,y){if(y==0&&(ut||!Te.live||r==2))return Ls;let A=[],P=Qn("tr",Jy,Ve,Ve.childNodes[y]);Nn(P,g.class),g.show||Nn(P,wr);let F=Qn("th",null,P);if(ye.show){let fe=Vn(Qy,F);if(y>0){let Me=ye.width(n,y);Me&&(fe.style.border=Me+"px "+ye.dash(n,y)+" "+ye.stroke(n,y)),fe.style.background=ye.fill(n,y)}}let Y=Vn(td,F);g.label instanceof HTMLElement?Y.appendChild(g.label):Y.textContent=g.label,y>0&&(ye.show||(Y.style.color=g.width>0?ye.stroke(n,y):ye.fill(n,y)),D("click",F,fe=>{if(xe._lock)return;Ot(fe);let Me=E.indexOf(g);if((fe.ctrlKey||fe.metaKey)!=Te.isolate){let Le=E.some((De,Ue)=>Ue>0&&Ue!=Me&&De.show);E.forEach((De,Ue)=>{Ue>0&&ci(Ue,Le?Ue==Me?Fe:St:Fe,!0,Wt.setSeries)})}else ci(Me,{show:!g.show},!0,Wt.setSeries)},!1),oi&&D(sd,F,fe=>{xe._lock||(Ot(fe),ci(E.indexOf(g),Gr,!0,Wt.setSeries))},!1));for(var se in U){let fe=Qn("td",eM,P);fe.textContent="--",A.push(fe)}return[P,A]}const We=new Map;function D(g,y,A,P=!0){const F=We.get(y)||{},Y=xe.bind[g](n,y,A,P);Y&&(Cr(g,y,F[g]=Y),We.set(y,F))}function M(g,y,A){const P=We.get(y)||{};for(let F in P)(g==null||F==g)&&(Uc(F,y,P[F]),delete P[F]);g==null&&We.delete(y)}let Z=0,oe=0,Q=0,G=0,Ee=0,ge=0,Ae=Ee,je=ge,pe=Q,we=G,Ke=0,ze=0,Se=0,ke=0;n.bbox={};let N=!1,le=!1,I=!1,re=!1,ne=!1,ie=!1;function _e(g,y,A){(A||g!=n.width||y!=n.height)&&$e(g,y),Fr(!1),I=!0,le=!0,Or()}function $e(g,y){n.width=Z=Q=g,n.height=oe=G=y,Ee=ge=0,at(),un();let A=n.bbox;Ke=A.left=Sr(Ee*xt,.5),ze=A.top=Sr(ge*xt,.5),Se=A.width=Sr(Q*xt,.5),ke=A.height=Sr(G*xt,.5)}const st=3;function mt(){let g=!1,y=0;for(;!g;){y++;let A=_p(y),P=vp(y);g=y==st||A&&P,g||($e(n.width,n.height),le=!0)}}function Et({width:g,height:y}){_e(g,y)}n.setSize=Et;function at(){let g=!1,y=!1,A=!1,P=!1;S.forEach((F,Y)=>{if(F.show&&F._show){let{side:se,_size:fe}=F,Me=se%2,Le=F.label!=null?F.labelSize:0,De=fe+Le;De>0&&(Me?(Q-=De,se==3?(Ee+=De,P=!0):A=!0):(G-=De,se==0?(ge+=De,g=!0):y=!0))}}),Mi[0]=g,Mi[1]=A,Mi[2]=y,Mi[3]=P,Q-=$[1]+$[3],Ee+=$[3],G-=$[2]+$[0],ge+=$[0]}function un(){let g=Ee+Q,y=ge+G,A=Ee,P=ge;function F(Y,se){switch(Y){case 1:return g+=se,g-se;case 2:return y+=se,y-se;case 3:return A-=se,A+se;case 0:return P-=se,P+se}}S.forEach((Y,se)=>{if(Y.show&&Y._show){let fe=Y.side;Y._pos=F(fe,Y._size),Y.label!=null&&(Y._lpos=F(fe,Y.labelSize))}})}if(xe.dataIdx==null){let g=xe.hover,y=g.skip=new Set(g.skip??[]);y.add(void 0);let A=g.prox=ht(g.prox),P=g.bias??(g.bias=0);xe.dataIdx=(F,Y,se,fe)=>{if(Y==0)return se;let Me=se,Le=A(F,Y,se,fe)??wt,De=Le>=0&&Le<wt,Ue=C.ori==0?Q:G,et=xe.left,vt=e[0],gt=e[Y];if(y.has(gt[se])){Me=null;let ct=null,Qe=null,Ge;if(P==0||P==-1)for(Ge=se;ct==null&&Ge-- >0;)y.has(gt[Ge])||(ct=Ge);if(P==0||P==1)for(Ge=se;Qe==null&&Ge++<gt.length;)y.has(gt[Ge])||(Qe=Ge);if(ct!=null||Qe!=null)if(De){let It=ct==null?-1/0:B(vt[ct],C,Ue,0),Ht=Qe==null?1/0:B(vt[Qe],C,Ue,0),an=et-It,Tt=Ht-et;an<=Tt?an<=Le&&(Me=ct):Tt<=Le&&(Me=Qe)}else Me=Qe==null?ct:ct==null?Qe:se-ct<=Qe-se?ct:Qe}else De&&Kt(et-B(vt[se],C,Ue,0))>Le&&(Me=null);return Me}}const Ot=g=>{xe.event=g};xe.idxs=ve,xe._lock=!1;let Bt=xe.points;Bt.show=ht(Bt.show),Bt.size=ht(Bt.size),Bt.stroke=ht(Bt.stroke),Bt.width=ht(Bt.width),Bt.fill=ht(Bt.fill);const tn=n.focus=qt({},i.focus||{alpha:.3},xe.focus),oi=tn.prox>=0,xi=oi&&Bt.one;let xn=[],Yn=[],yi=[];function ur(g,y){let A=Bt.show(n,y);if(A instanceof HTMLElement)return Nn(A,$y),Nn(A,g.class),fi(A,-10,-10,Q,G),_.insertBefore(A,xn[y]),A}function ks(g,y){if(r==1||y>0){let A=r==1&&T[g.scale].time,P=g.value;g.value=A?yd(P)?Ad(J,wd(P,q)):P||he:P||lS,g.label=g.label||(A?eS:QM)}if(xi||y>0){g.width=g.width==null?1:g.width,g.paths=g.paths||SS||dM,g.fillTo=ht(g.fillTo||fS),g.pxAlign=+_t(g.pxAlign,v),g.pxRound=Fd(g.pxAlign),g.stroke=ht(g.stroke||null),g.fill=ht(g.fill||null),g._stroke=g._fill=g._paths=g._focus=null;let A=cS(wn(1,g.width),1),P=g.points=qt({},{size:A,width:wn(1,A*.2),stroke:g.stroke,space:A*2,paths:ES,_stroke:null,_fill:null},g.points);P.show=ht(P.show),P.filter=ht(P.filter),P.fill=ht(P.fill),P.stroke=ht(P.stroke),P.paths=ht(P.paths),P.pxAlign=g.pxAlign}if(te){let A=qe(g,y);Ne.splice(y,0,A[0]),dt.splice(y,0,A[1]),Te.values.push(null)}if(ce){ve.splice(y,0,null);let A=null;xi?y==0&&(A=ur(g,y)):y>0&&(A=ur(g,y)),xn.splice(y,0,A),Yn.splice(y,0,0),yi.splice(y,0,0)}sn("addSeries",y)}function Sa(g,y){y=y??E.length,g=r==1?kc(g,y,Cd,Ud):kc(g,y,{},Id),E.splice(y,0,g),ks(E[y],y)}n.addSeries=Sa;function qo(g){if(E.splice(g,1),te){Te.values.splice(g,1),dt.splice(g,1);let y=Ne.splice(g,1)[0];M(null,y.firstChild),y.remove()}ce&&(ve.splice(g,1),xn.splice(g,1)[0].remove(),Yn.splice(g,1),yi.splice(g,1)),sn("delSeries",g)}n.delSeries=qo;const Mi=[!1,!1,!1,!1];function Yo(g,y){if(g._show=g.show,g.show){let A=g.side%2,P=T[g.scale];P==null&&(g.scale=A?E[1].scale:R,P=T[g.scale]);let F=P.time;g.size=ht(g.size),g.space=ht(g.space),g.rotate=ht(g.rotate),Zi(g.incrs)&&g.incrs.forEach(se=>{!ar.has(se)&&ar.set(se,Uf(se))}),g.incrs=ht(g.incrs||(P.distr==2?UM:F?f==1?FM:zM:Er)),g.splits=ht(g.splits||(F&&P.distr==1?ee:P.distr==3?Fc:P.distr==4?iS:nS)),g.stroke=ht(g.stroke),g.grid.stroke=ht(g.grid.stroke),g.ticks.stroke=ht(g.ticks.stroke),g.border.stroke=ht(g.border.stroke);let Y=g.values;g.values=Zi(Y)&&!Zi(Y[0])?ht(Y):F?Zi(Y)?Td(J,bd(Y,q)):yd(Y)?VM(J,Y):Y||me:Y||tS,g.filter=ht(g.filter||(P.distr>=3&&P.log==10?aS:P.distr==3&&P.log==2?oS:Df)),g.font=kd(g.font),g.labelFont=kd(g.labelFont),g._size=g.size(n,null,y,0),g._space=g._rotate=g._incrs=g._found=g._splits=g._values=null,g._size>0&&(Mi[y]=!0,g._el=Vn(Wy,d))}}function b(g,y,A,P){let[F,Y,se,fe]=A,Me=y%2,Le=0;return Me==0&&(fe||Y)&&(Le=y==0&&!F||y==2&&!se?jt(Rd.size/3):0),Me==1&&(F||se)&&(Le=y==1&&!Y||y==3&&!fe?jt(Ld.size/2):0),Le}const V=n.padding=(i.padding||[b,b,b,b]).map(g=>ht(_t(g,b))),$=n._padding=V.map((g,y)=>g(n,y,Mi,0));let X,k=null,ue=null;const Ce=r==1?E[0].idxs:null;let Pe=null,Ie=!1;function Ze(g,y){if(e=g??[],n.data=n._data=e,r==2){X=0;for(let A=1;A<E.length;A++)X+=e[A][0].length}else{e.length==0&&(n.data=n._data=e=[[]]),Pe=e[0],X=Pe.length;let A=e;if(j==2){A=e.slice();let P=A[0]=Array(X);for(let F=0;F<X;F++)P[F]=F}n._data=e=A}if(Fr(!0),sn("setData"),j==2&&(I=!0),y!==!1){let A=C;A.auto(n,Ie)?Je():ki(R,A.min,A.max),re=re||xe.left>=0,ie=!0,Or()}}n.setData=Ze;function Je(){Ie=!0;let g,y;r==1&&(X>0?(k=Ce[0]=0,ue=Ce[1]=X-1,g=e[0][k],y=e[0][ue],j==2?(g=k,y=ue):g==y&&(j==3?[g,y]=Bo(g,g,C.log,!1):j==4?[g,y]=ou(g,g,C.log,!1):C.time?y=g+jt(86400/f):[g,y]=Lo(g,y,lu,!0))):(k=Ce[0]=g=null,ue=Ce[1]=y=null)),ki(R,g,y)}let Oe,lt,Rt,Ct,hn,ft,He,Gt,pt,Pt;function Si(g,y,A,P,F,Y){g??(g=id),A??(A=uu),P??(P="butt"),F??(F=id),Y??(Y="round"),g!=Oe&&(h.strokeStyle=Oe=g),F!=lt&&(h.fillStyle=lt=F),y!=Rt&&(h.lineWidth=Rt=y),Y!=hn&&(h.lineJoin=hn=Y),P!=ft&&(h.lineCap=ft=P),A!=Ct&&h.setLineDash(Ct=A)}function fn(g,y,A,P){y!=lt&&(h.fillStyle=lt=y),g!=He&&(h.font=He=g),A!=Gt&&(h.textAlign=Gt=A),P!=pt&&(h.textBaseline=pt=P)}function hr(g,y,A,P,F=0){if(P.length>0&&g.auto(n,Ie)&&(y==null||y.min==null)){let Y=_t(k,0),se=_t(ue,P.length-1),fe=A.min==null?aM(P,Y,se,F,g.distr==3):[A.min,A.max];g.min=ii(g.min,A.min=fe[0]),g.max=wn(g.max,A.max=fe[1])}}const kt={min:null,max:null};function li(){for(let P in T){let F=T[P];W[P]==null&&(F.min==null||W[R]!=null&&F.auto(n,Ie))&&(W[P]=kt)}for(let P in T){let F=T[P];W[P]==null&&F.from!=null&&W[F.from]!=null&&(W[P]=kt)}W[R]!=null&&Fr(!0);let g={};for(let P in W){let F=W[P];if(F!=null){let Y=g[P]=Ds(T[P],mM);if(F.min!=null)qt(Y,F);else if(P!=R||r==2)if(X==0&&Y.from==null){let se=Y.range(n,null,null,P);Y.min=se[0],Y.max=se[1]}else Y.min=wt,Y.max=-wt}}if(X>0){E.forEach((P,F)=>{if(r==1){let Y=P.scale,se=W[Y];if(se==null)return;let fe=g[Y];if(F==0){let Me=fe.range(n,fe.min,fe.max,Y);fe.min=Me[0],fe.max=Me[1],k=ei(fe.min,e[0]),ue=ei(fe.max,e[0]),ue-k>1&&(e[0][k]<fe.min&&k++,e[0][ue]>fe.max&&ue--),P.min=Pe[k],P.max=Pe[ue]}else P.show&&P.auto&&hr(fe,se,P,e[F],P.sorted);P.idxs[0]=k,P.idxs[1]=ue}else if(F>0&&P.show&&P.auto){let[Y,se]=P.facets,fe=Y.scale,Me=se.scale,[Le,De]=e[F],Ue=g[fe],et=g[Me];Ue!=null&&hr(Ue,W[fe],Y,Le,Y.sorted),et!=null&&hr(et,W[Me],se,De,se.sorted),P.min=se.min,P.max=se.max}});for(let P in g){let F=g[P],Y=W[P];if(F.from==null&&(Y==null||Y.min==null)){let se=F.range(n,F.min==wt?null:F.min,F.max==-wt?null:F.max,P);F.min=se[0],F.max=se[1]}}}for(let P in g){let F=g[P];if(F.from!=null){let Y=g[F.from];if(Y.min==null)F.min=F.max=null;else{let se=F.range(n,Y.min,Y.max,P);F.min=se[0],F.max=se[1]}}}let y={},A=!1;for(let P in g){let F=g[P],Y=T[P];if(Y.min!=F.min||Y.max!=F.max){Y.min=F.min,Y.max=F.max;let se=Y.distr;Y._min=se==3?Ni(Y.min):se==4?kl(Y.min,Y.asinh):se==100?Y.fwd(Y.min):Y.min,Y._max=se==3?Ni(Y.max):se==4?kl(Y.max,Y.asinh):se==100?Y.fwd(Y.max):Y.max,y[P]=A=!0}}if(A){E.forEach((P,F)=>{r==2?F>0&&y.y&&(P._paths=null):y[P.scale]&&(P._paths=null)});for(let P in y)I=!0,sn("setScale",P);ce&&xe.left>=0&&(re=ie=!0)}for(let P in W)W[P]=null}function Hs(g){let y=Nc(k-1,0,X-1),A=Nc(ue+1,0,X-1);for(;g[y]==null&&y>0;)y--;for(;g[A]==null&&A<X-1;)A++;return[y,A]}function Rn(){if(X>0){let g=E.some(y=>y._focus)&&Pt!=tn.alpha;g&&(h.globalAlpha=Pt=tn.alpha),E.forEach((y,A)=>{if(A>0&&y.show&&(Nr(A,!1),Nr(A,!0),y._paths==null)){let P=Pt;Pt!=y.alpha&&(h.globalAlpha=Pt=y.alpha);let F=r==2?[0,e[A][0].length-1]:Hs(e[A]);y._paths=y.paths(n,A,F[0],F[1]),Pt!=P&&(h.globalAlpha=Pt=P)}}),E.forEach((y,A)=>{if(A>0&&y.show){let P=Pt;Pt!=y.alpha&&(h.globalAlpha=Pt=y.alpha),y._paths!=null&&Ea(A,!1);{let F=y._paths!=null?y._paths.gaps:null,Y=y.points.show(n,A,k,ue,F),se=y.points.filter(n,A,Y,F);(Y||se)&&(y.points._paths=y.points.paths(n,A,k,ue,se),Ea(A,!0))}Pt!=P&&(h.globalAlpha=Pt=P),sn("drawSeries",A)}}),g&&(h.globalAlpha=Pt=1)}}function Nr(g,y){let A=y?E[g].points:E[g];A._stroke=A.stroke(n,g),A._fill=A.fill(n,g)}function Ea(g,y){let A=y?E[g].points:E[g],{stroke:P,fill:F,clip:Y,flags:se,_stroke:fe=A._stroke,_fill:Me=A._fill,_width:Le=A.width}=A._paths;Le=At(Le*xt,3);let De=null,Ue=Le%2/2;y&&Me==null&&(Me=Le>0?"#fff":fe);let et=A.pxAlign==1&&Ue>0;if(et&&h.translate(Ue,Ue),!y){let vt=Ke-Le/2,gt=ze-Le/2,ct=Se+Le,Qe=ke+Le;De=new Path2D,De.rect(vt,gt,ct,Qe)}y?$o(fe,Le,A.dash,A.cap,Me,P,F,se,Y):ba(g,fe,Le,A.dash,A.cap,Me,P,F,se,De,Y),et&&h.translate(-Ue,-Ue)}function ba(g,y,A,P,F,Y,se,fe,Me,Le,De){let Ue=!1;Me!=0&&z.forEach((et,vt)=>{if(et.series[0]==g){let gt=E[et.series[1]],ct=e[et.series[1]],Qe=(gt._paths||pa).band;Zi(Qe)&&(Qe=et.dir==1?Qe[0]:Qe[1]);let Ge,It=null;gt.show&&Qe&&lM(ct,k,ue)?(It=et.fill(n,vt)||Y,Ge=gt._paths.clip):Qe=null,$o(y,A,P,F,It,se,fe,Me,Le,De,Ge,Qe),Ue=!0}}),Ue||$o(y,A,P,F,Y,se,fe,Me,Le,De)}const Su=Is|Bc;function $o(g,y,A,P,F,Y,se,fe,Me,Le,De,Ue){Si(g,y,A,P,F),(Me||Le||Ue)&&(h.save(),Me&&h.clip(Me),Le&&h.clip(Le)),Ue?(fe&Su)==Su?(h.clip(Ue),De&&h.clip(De),wa(F,se),Ta(g,Y,y)):fe&Bc?(wa(F,se),h.clip(Ue),Ta(g,Y,y)):fe&Is&&(h.save(),h.clip(Ue),De&&h.clip(De),wa(F,se),h.restore(),Ta(g,Y,y)):(wa(F,se),Ta(g,Y,y)),(Me||Le||Ue)&&h.restore()}function Ta(g,y,A){A>0&&(y instanceof Map?y.forEach((P,F)=>{h.strokeStyle=Oe=F,h.stroke(P)}):y!=null&&g&&h.stroke(y))}function wa(g,y){y instanceof Map?y.forEach((A,P)=>{h.fillStyle=lt=P,h.fill(A)}):y!=null&&g&&h.fill(y)}function gp(g,y,A,P){let F=S[g],Y;if(P<=0)Y=[0,0];else{let se=F._space=F.space(n,g,y,A,P),fe=F._incrs=F.incrs(n,g,y,A,P,se);Y=CS(y,A,fe,P,se)}return F._found=Y}function jo(g,y,A,P,F,Y,se,fe,Me,Le){let De=se%2/2;v==1&&h.translate(De,De),Si(fe,se,Me,Le,fe),h.beginPath();let Ue,et,vt,gt,ct=F+(P==0||P==3?-Y:Y);A==0?(et=F,gt=ct):(Ue=F,vt=ct);for(let Qe=0;Qe<g.length;Qe++)y[Qe]!=null&&(A==0?Ue=vt=g[Qe]:et=gt=g[Qe],h.moveTo(Ue,et),h.lineTo(vt,gt));h.stroke(),v==1&&h.translate(-De,-De)}function _p(g){let y=!0;return S.forEach((A,P)=>{if(!A.show)return;let F=T[A.scale];if(F.min==null){A._show&&(y=!1,A._show=!1,Fr(!1));return}else A._show||(y=!1,A._show=!0,Fr(!1));let Y=A.side,se=Y%2,{min:fe,max:Me}=F,[Le,De]=gp(P,fe,Me,se==0?Q:G);if(De==0)return;let Ue=F.distr==2,et=A._splits=A.splits(n,P,fe,Me,Le,De,Ue),vt=F.distr==2?et.map(Ge=>Pe[Ge]):et,gt=F.distr==2?Pe[et[1]]-Pe[et[0]]:Le,ct=A._values=A.values(n,A.filter(n,vt,P,De,gt),P,De,gt);A._rotate=Y==2?A.rotate(n,ct,P,De):0;let Qe=A._size;A._size=Gn(A.size(n,ct,P,g)),Qe!=null&&A._size!=Qe&&(y=!1)}),y}function vp(g){let y=!0;return V.forEach((A,P)=>{let F=A(n,P,Mi,g);F!=$[P]&&(y=!1),$[P]=F}),y}function xp(){for(let g=0;g<S.length;g++){let y=S[g];if(!y.show||!y._show)continue;let A=y.side,P=A%2,F,Y,se=y.stroke(n,g),fe=A==0||A==3?-1:1,[Me,Le]=y._found;if(y.label!=null){let Mn=y.labelGap*fe,Dn=jt((y._lpos+Mn)*xt);fn(y.labelFont[0],se,"center",A==2?ia:nd),h.save(),P==1?(F=Y=0,h.translate(Dn,jt(ze+ke/2)),h.rotate((A==3?-yo:yo)/2)):(F=jt(Ke+Se/2),Y=Dn);let pr=Pf(y.label)?y.label(n,g,Me,Le):y.label;h.fillText(pr,F,Y),h.restore()}if(Le==0)continue;let De=T[y.scale],Ue=P==0?Se:ke,et=P==0?Ke:ze,vt=y._splits,gt=De.distr==2?vt.map(Mn=>Pe[Mn]):vt,ct=De.distr==2?Pe[vt[1]]-Pe[vt[0]]:Me,Qe=y.ticks,Ge=y.border,It=Qe.show?Qe.size:0,Ht=jt(It*xt),an=jt((y.alignTo==2?y._size-It-y.gap:y.gap)*xt),Tt=y._rotate*-yo/180,Vt=p(y._pos*xt),Pn=(Ht+an)*fe,yn=Vt+Pn;Y=P==0?yn:0,F=P==1?yn:0;let zn=y.font[0],$n=y.align==1?ps:y.align==2?Ol:Tt>0?ps:Tt<0?Ol:P==0?"center":A==3?Ol:ps,hi=Tt||P==1?"middle":A==2?ia:nd;fn(zn,se,$n,hi);let Ln=y.font[1]*y.lineGap,kn=vt.map(Mn=>p(o(Mn,De,Ue,et))),jn=y._values;for(let Mn=0;Mn<jn.length;Mn++){let Dn=jn[Mn];if(Dn!=null){P==0?F=kn[Mn]:Y=kn[Mn],Dn=""+Dn;let pr=Dn.indexOf(`
`)==-1?[Dn]:Dn.split(/\n/gm);for(let Sn=0;Sn<pr.length;Sn++){let Hu=pr[Sn];Tt?(h.save(),h.translate(F,Y+Sn*Ln),h.rotate(Tt),h.fillText(Hu,0,0),h.restore()):h.fillText(Hu,F,Y+Sn*Ln)}}}Qe.show&&jo(kn,Qe.filter(n,gt,g,Le,ct),P,A,Vt,Ht,At(Qe.width*xt,3),Qe.stroke(n,g),Qe.dash,Qe.cap);let di=y.grid;di.show&&jo(kn,di.filter(n,gt,g,Le,ct),P,P==0?2:1,P==0?ze:Ke,P==0?ke:Se,At(di.width*xt,3),di.stroke(n,g),di.dash,di.cap),Ge.show&&jo([Vt],[1],P==0?1:0,P==0?1:2,P==1?ze:Ke,P==1?ke:Se,At(Ge.width*xt,3),Ge.stroke(n,g),Ge.dash,Ge.cap)}sn("drawAxes")}function Fr(g){E.forEach((y,A)=>{A>0&&(y._paths=null,g&&(r==1?(y.min=null,y.max=null):y.facets.forEach(P=>{P.min=null,P.max=null})))})}let Aa=!1,Ko=!1,Vs=[];function yp(){Ko=!1;for(let g=0;g<Vs.length;g++)sn(...Vs[g]);Vs.length=0}function Or(){Aa||(SM(Eu),Aa=!0)}function Mp(g,y=!1){Aa=!0,Ko=y,g(n),Eu(),y&&Vs.length>0&&queueMicrotask(yp)}n.batch=Mp;function Eu(){if(N&&(li(),N=!1),I&&(mt(),I=!1),le){if(Ut(m,ps,Ee),Ut(m,ia,ge),Ut(m,aa,Q),Ut(m,oa,G),Ut(_,ps,Ee),Ut(_,ia,ge),Ut(_,aa,Q),Ut(_,oa,G),Ut(d,aa,Z),Ut(d,oa,oe),u.width=jt(Z*xt),u.height=jt(oe*xt),S.forEach(({_el:g,_show:y,_size:A,_pos:P,side:F})=>{if(g!=null)if(y){let Y=F===3||F===0?A:0,se=F%2==1;Ut(g,se?"left":"top",P-Y),Ut(g,se?"width":"height",A),Ut(g,se?"top":"left",se?ge:Ee),Ut(g,se?"height":"width",se?G:Q),Ic(g,wr)}else Nn(g,wr)}),Oe=lt=Rt=hn=ft=He=Gt=pt=Ct=null,Pt=1,Xs(!0),Ee!=Ae||ge!=je||Q!=pe||G!=we){Fr(!1);let g=Q/pe,y=G/we;if(ce&&!re&&xe.left>=0){xe.left*=g,xe.top*=y,Br&&fi(Br,jt(xe.left),0,Q,G),zr&&fi(zr,0,jt(xe.top),Q,G);for(let A=0;A<xn.length;A++){let P=xn[A];P!=null&&(Yn[A]*=g,yi[A]*=y,fi(P,Gn(Yn[A]),Gn(yi[A]),Q,G))}}if(Dt.show&&!ne&&Dt.left>=0&&Dt.width>0){Dt.left*=g,Dt.width*=g,Dt.top*=y,Dt.height*=y;for(let A in nl)Ut(Vr,A,Dt[A])}Ae=Ee,je=ge,pe=Q,we=G}sn("setSize"),le=!1}Z>0&&oe>0&&(h.clearRect(0,0,u.width,u.height),sn("drawClear"),O.forEach(g=>g()),sn("draw")),Dt.show&&ne&&(Ra(Dt),ne=!1),ce&&re&&(fr(null,!0,!1),re=!1),Te.show&&Te.live&&ie&&(el(),ie=!1),l||(l=!0,n.status=1,sn("ready")),Ie=!1,Aa=!1}n.redraw=(g,y)=>{I=y||!1,g!==!1?ki(R,C.min,C.max):Or()};function Zo(g,y){let A=T[g];if(A.from==null){if(X==0){let P=A.range(n,y.min,y.max,g);y.min=P[0],y.max=P[1]}if(y.min>y.max){let P=y.min;y.min=y.max,y.max=P}if(X>1&&y.min!=null&&y.max!=null&&y.max-y.min<1e-16)return;g==R&&A.distr==2&&X>0&&(y.min=ei(y.min,e[0]),y.max=ei(y.max,e[0]),y.min==y.max&&y.max++),W[g]=y,N=!0,Or()}}n.setScale=Zo;let Jo,Qo,Br,zr,bu,Tu,kr,Hr,wu,Au,Lt,zt,zi=!1;const dn=xe.drag;let nn=dn.x,rn=dn.y;ce&&(xe.x&&(Jo=Vn(qy,_)),xe.y&&(Qo=Vn(Yy,_)),C.ori==0?(Br=Jo,zr=Qo):(Br=Qo,zr=Jo),Lt=xe.left,zt=xe.top);const Dt=n.select=qt({show:!0,over:!0,left:0,width:0,top:0,height:0},i.select),Vr=Dt.show?Vn(Xy,Dt.over?_:m):null;function Ra(g,y){if(Dt.show){for(let A in g)Dt[A]=g[A],A in nl&&Ut(Vr,A,g[A]);y!==!1&&sn("setSelect")}}n.setSelect=Ra;function Sp(g){if(E[g].show)te&&Ic(Ne[g],wr);else if(te&&Nn(Ne[g],wr),ce){let A=xi?xn[0]:xn[g];A!=null&&fi(A,-10,-10,Q,G)}}function ki(g,y,A){Zo(g,{min:y,max:A})}function ci(g,y,A,P){y.focus!=null&&Ap(g),y.show!=null&&E.forEach((F,Y)=>{Y>0&&(g==Y||g==null)&&(F.show=y.show,Sp(Y),r==2?(ki(F.facets[0].scale,null,null),ki(F.facets[1].scale,null,null)):ki(F.scale,null,null),Or())}),A!==!1&&sn("setSeries",g,y),P&&qs("setSeries",n,g,y)}n.setSeries=ci;function Ep(g,y){qt(z[g],y)}function bp(g,y){g.fill=ht(g.fill||null),g.dir=_t(g.dir,-1),y=y??z.length,z.splice(y,0,g)}function Tp(g){g==null?z.length=0:z.splice(g,1)}n.addBand=bp,n.setBand=Ep,n.delBand=Tp;function wp(g,y){E[g].alpha=y,ce&&xn[g]!=null&&(xn[g].style.opacity=y),te&&Ne[g]&&(Ne[g].style.opacity=y)}let Ei,Hi,dr;const Gr={focus:!0};function Ap(g){if(g!=dr){let y=g==null,A=tn.alpha!=1;E.forEach((P,F)=>{if(r==1||F>0){let Y=y||F==0||F==g;P._focus=y?null:Y,A&&wp(F,Y?1:tn.alpha)}}),dr=g,A&&Or()}}te&&oi&&D(ad,de,g=>{xe._lock||(Ot(g),dr!=null&&ci(null,Gr,!0,Wt.setSeries))});function ui(g,y,A){let P=T[y];A&&(g=g/xt-(P.ori==1?ge:Ee));let F=Q;P.ori==1&&(F=G,g=F-g),P.dir==-1&&(g=F-g);let Y=P._min,se=P._max,fe=g/F,Me=Y+(se-Y)*fe,Le=P.distr;return Le==3?Ps(10,Me):Le==4?uM(Me,P.asinh):Le==100?P.bwd(Me):Me}function Rp(g,y){let A=ui(g,R,y);return ei(A,e[0],k,ue)}n.valToIdx=g=>ei(g,e[0]),n.posToIdx=Rp,n.posToVal=ui,n.valToPos=(g,y,A)=>T[y].ori==0?s(g,T[y],A?Se:Q,A?Ke:0):a(g,T[y],A?ke:G,A?ze:0),n.setCursor=(g,y,A)=>{Lt=g.left,zt=g.top,fr(null,y,A)};function Ru(g,y){Ut(Vr,ps,Dt.left=g),Ut(Vr,aa,Dt.width=y)}function Cu(g,y){Ut(Vr,ia,Dt.top=g),Ut(Vr,oa,Dt.height=y)}let Gs=C.ori==0?Ru:Cu,Ws=C.ori==1?Ru:Cu;function Cp(){if(te&&Te.live)for(let g=r==2?1:0;g<E.length;g++){if(g==0&&ut)continue;let y=Te.values[g],A=0;for(let P in y)dt[g][A++].firstChild.nodeValue=y[P]}}function el(g,y){if(g!=null&&(g.idxs?g.idxs.forEach((A,P)=>{ve[P]=A}):pM(g.idx)||ve.fill(g.idx),Te.idx=ve[0]),te&&Te.live){for(let A=0;A<E.length;A++)(A>0||r==1&&!ut)&&Pp(A,ve[A]);Cp()}ie=!1,y!==!1&&sn("setLegend")}n.setLegend=el;function Pp(g,y){let A=E[g],P=g==0&&j==2?Pe:e[g],F;ut?F=A.values(n,g,y)??nt:(F=A.value(n,y==null?null:P[y],g,y),F=F==null?nt:{_:F}),Te.values[g]=F}function fr(g,y,A){wu=Lt,Au=zt,[Lt,zt]=xe.move(n,Lt,zt),xe.left=Lt,xe.top=zt,ce&&(Br&&fi(Br,jt(Lt),0,Q,G),zr&&fi(zr,0,jt(zt),Q,G));let P,F=k>ue;Ei=wt,Hi=null;let Y=C.ori==0?Q:G,se=C.ori==1?Q:G;if(Lt<0||X==0||F){P=xe.idx=null;for(let fe=0;fe<E.length;fe++){let Me=xn[fe];Me!=null&&fi(Me,-10,-10,Q,G)}oi&&ci(null,Gr,!0,g==null&&Wt.setSeries),Te.live&&(ve.fill(P),ie=!0)}else{let fe,Me,Le;r==1&&(fe=C.ori==0?Lt:zt,Me=ui(fe,R),P=xe.idx=ei(Me,e[0],k,ue),Le=B(e[0][P],C,Y,0));let De=-10,Ue=-10,et=0,vt=0,gt=!0,ct="",Qe="";for(let Ge=r==2?1:0;Ge<E.length;Ge++){let It=E[Ge],Ht=ve[Ge],an=Ht==null?null:r==1?e[Ge][Ht]:e[Ge][1][Ht],Tt=xe.dataIdx(n,Ge,P,Me),Vt=Tt==null?null:r==1?e[Ge][Tt]:e[Ge][1][Tt];if(ie=ie||Vt!=an||Tt!=Ht,ve[Ge]=Tt,Ge>0&&It.show){let Pn=Tt==null?-10:Tt==P?Le:B(r==1?e[0][Tt]:e[Ge][0][Tt],C,Y,0),yn=Vt==null?-10:K(Vt,r==1?T[It.scale]:T[It.facets[1].scale],se,0);if(oi&&Vt!=null){let zn=C.ori==1?Lt:zt,$n=Kt(tn.dist(n,Ge,Tt,yn,zn));if($n<Ei){let hi=tn.bias;if(hi!=0){let Ln=ui(zn,It.scale),kn=Vt>=0?1:-1,jn=Ln>=0?1:-1;jn==kn&&(jn==1?hi==1?Vt>=Ln:Vt<=Ln:hi==1?Vt<=Ln:Vt>=Ln)&&(Ei=$n,Hi=Ge)}else Ei=$n,Hi=Ge}}if(ie||xi){let zn,$n;C.ori==0?(zn=Pn,$n=yn):(zn=yn,$n=Pn);let hi,Ln,kn,jn,di,Mn,Dn=!0,pr=Bt.bbox;if(pr!=null){Dn=!1;let Sn=pr(n,Ge);kn=Sn.left,jn=Sn.top,hi=Sn.width,Ln=Sn.height}else kn=zn,jn=$n,hi=Ln=Bt.size(n,Ge);if(Mn=Bt.fill(n,Ge),di=Bt.stroke(n,Ge),xi)Ge==Hi&&Ei<=tn.prox&&(De=kn,Ue=jn,et=hi,vt=Ln,gt=Dn,ct=Mn,Qe=di);else{let Sn=xn[Ge];Sn!=null&&(Yn[Ge]=kn,yi[Ge]=jn,fd(Sn,hi,Ln,Dn),hd(Sn,Mn,di),fi(Sn,Gn(kn),Gn(jn),Q,G))}}}}if(xi){let Ge=tn.prox,It=dr==null?Ei<=Ge:Ei>Ge||Hi!=dr;if(ie||It){let Ht=xn[0];Ht!=null&&(Yn[0]=De,yi[0]=Ue,fd(Ht,et,vt,gt),hd(Ht,ct,Qe),fi(Ht,Gn(De),Gn(Ue),Q,G))}}}if(Dt.show&&zi)if(g!=null){let[fe,Me]=Wt.scales,[Le,De]=Wt.match,[Ue,et]=g.cursor.sync.scales,vt=g.cursor.drag;if(nn=vt._x,rn=vt._y,nn||rn){let{left:gt,top:ct,width:Qe,height:Ge}=g.select,It=g.scales[Ue].ori,Ht=g.posToVal,an,Tt,Vt,Pn,yn,zn=fe!=null&&Le(fe,Ue),$n=Me!=null&&De(Me,et);zn&&nn?(It==0?(an=gt,Tt=Qe):(an=ct,Tt=Ge),Vt=T[fe],Pn=B(Ht(an,Ue),Vt,Y,0),yn=B(Ht(an+Tt,Ue),Vt,Y,0),Gs(ii(Pn,yn),Kt(yn-Pn))):Gs(0,Y),$n&&rn?(It==1?(an=gt,Tt=Qe):(an=ct,Tt=Ge),Vt=T[Me],Pn=K(Ht(an,et),Vt,se,0),yn=K(Ht(an+Tt,et),Vt,se,0),Ws(ii(Pn,yn),Kt(yn-Pn))):Ws(0,se)}else il()}else{let fe=Kt(wu-bu),Me=Kt(Au-Tu);if(C.ori==1){let et=fe;fe=Me,Me=et}nn=dn.x&&fe>=dn.dist,rn=dn.y&&Me>=dn.dist;let Le=dn.uni;Le!=null?nn&&rn&&(nn=fe>=Le,rn=Me>=Le,!nn&&!rn&&(Me>fe?rn=!0:nn=!0)):dn.x&&dn.y&&(nn||rn)&&(nn=rn=!0);let De,Ue;nn&&(C.ori==0?(De=kr,Ue=Lt):(De=Hr,Ue=zt),Gs(ii(De,Ue),Kt(Ue-De)),rn||Ws(0,se)),rn&&(C.ori==1?(De=kr,Ue=Lt):(De=Hr,Ue=zt),Ws(ii(De,Ue),Kt(Ue-De)),nn||Gs(0,Y)),!nn&&!rn&&(Gs(0,0),Ws(0,0))}if(dn._x=nn,dn._y=rn,g==null){if(A){if(ku!=null){let[fe,Me]=Wt.scales;Wt.values[0]=fe!=null?ui(C.ori==0?Lt:zt,fe):null,Wt.values[1]=Me!=null?ui(C.ori==1?Lt:zt,Me):null}qs(Bl,n,Lt,zt,Q,G,P)}if(oi){let fe=A&&Wt.setSeries,Me=tn.prox;dr==null?Ei<=Me&&ci(Hi,Gr,!0,fe):Ei>Me?ci(null,Gr,!0,fe):Hi!=dr&&ci(Hi,Gr,!0,fe)}}ie&&(Te.idx=P,el()),y!==!1&&sn("setCursor")}let Vi=null;Object.defineProperty(n,"rect",{get(){return Vi==null&&Xs(!1),Vi}});function Xs(g=!1){g?Vi=null:(Vi=_.getBoundingClientRect(),sn("syncRect",Vi))}function Pu(g,y,A,P,F,Y,se){xe._lock||zi&&g!=null&&g.movementX==0&&g.movementY==0||(tl(g,y,A,P,F,Y,se,!1,g!=null),g!=null?fr(null,!0,!0):fr(y,!0,!1))}function tl(g,y,A,P,F,Y,se,fe,Me){if(Vi==null&&Xs(!1),Ot(g),g!=null)A=g.clientX-Vi.left,P=g.clientY-Vi.top;else{if(A<0||P<0){Lt=-10,zt=-10;return}let[Le,De]=Wt.scales,Ue=y.cursor.sync,[et,vt]=Ue.values,[gt,ct]=Ue.scales,[Qe,Ge]=Wt.match,It=y.axes[0].side%2==1,Ht=C.ori==0?Q:G,an=C.ori==1?Q:G,Tt=It?Y:F,Vt=It?F:Y,Pn=It?P:A,yn=It?A:P;if(gt!=null?A=Qe(Le,gt)?o(et,T[Le],Ht,0):-10:A=Ht*(Pn/Tt),ct!=null?P=Ge(De,ct)?o(vt,T[De],an,0):-10:P=an*(yn/Vt),C.ori==1){let zn=A;A=P,P=zn}}Me&&(y==null||y.cursor.event.type==Bl)&&((A<=1||A>=Q-1)&&(A=Sr(A,Q)),(P<=1||P>=G-1)&&(P=Sr(P,G))),fe?(bu=A,Tu=P,[kr,Hr]=xe.move(n,A,P)):(Lt=A,zt=P)}const nl={width:0,height:0,left:0,top:0};function il(){Ra(nl,!1)}let Lu,Du,Iu,Uu;function Nu(g,y,A,P,F,Y,se){zi=!0,nn=rn=dn._x=dn._y=!1,tl(g,y,A,P,F,Y,se,!0,!1),g!=null&&(D(zl,Lc,Fu,!1),qs(rd,n,kr,Hr,Q,G,null));let{left:fe,top:Me,width:Le,height:De}=Dt;Lu=fe,Du=Me,Iu=Le,Uu=De}function Fu(g,y,A,P,F,Y,se){zi=dn._x=dn._y=!1,tl(g,y,A,P,F,Y,se,!1,!0);let{left:fe,top:Me,width:Le,height:De}=Dt,Ue=Le>0||De>0,et=Lu!=fe||Du!=Me||Iu!=Le||Uu!=De;if(Ue&&et&&Ra(Dt),dn.setScale&&Ue&&et){let vt=fe,gt=Le,ct=Me,Qe=De;if(C.ori==1&&(vt=Me,gt=De,ct=fe,Qe=Le),nn&&ki(R,ui(vt,R),ui(vt+gt,R)),rn)for(let Ge in T){let It=T[Ge];Ge!=R&&It.from==null&&It.min!=wt&&ki(Ge,ui(ct+Qe,Ge),ui(ct,Ge))}il()}else xe.lock&&(xe._lock=!xe._lock,fr(y,!0,g!=null));g!=null&&(M(zl,Lc),qs(zl,n,Lt,zt,Q,G,null))}function Lp(g,y,A,P,F,Y,se){if(xe._lock)return;Ot(g);let fe=zi;if(zi){let Me=!0,Le=!0,De=10,Ue,et;C.ori==0?(Ue=nn,et=rn):(Ue=rn,et=nn),Ue&&et&&(Me=Lt<=De||Lt>=Q-De,Le=zt<=De||zt>=G-De),Ue&&Me&&(Lt=Lt<kr?0:Q),et&&Le&&(zt=zt<Hr?0:G),fr(null,!0,!0),zi=!1}Lt=-10,zt=-10,ve.fill(null),fr(null,!0,!0),fe&&(zi=fe)}function Ou(g,y,A,P,F,Y,se){xe._lock||(Ot(g),Je(),il(),g!=null&&qs(od,n,Lt,zt,Q,G,null))}function Bu(){S.forEach(PS),_e(n.width,n.height,!0)}Cr(Po,Es,Bu);const Wr={};Wr.mousedown=Nu,Wr.mousemove=Pu,Wr.mouseup=Fu,Wr.dblclick=Ou,Wr.setSeries=(g,y,A,P)=>{let F=Wt.match[2];A=F(n,y,A),A!=-1&&ci(A,P,!0,!1)},ce&&(D(rd,_,Nu),D(Bl,_,Pu),D(sd,_,g=>{Ot(g),Xs(!1)}),D(ad,_,Lp),D(od,_,Ou),zc.add(n),n.syncRect=Xs);const Ca=n.hooks=i.hooks||{};function sn(g,y,A){Ko?Vs.push([g,y,A]):g in Ca&&Ca[g].forEach(P=>{P.call(null,n,y,A)})}(i.plugins||[]).forEach(g=>{for(let y in g.hooks)Ca[y]=(Ca[y]||[]).concat(g.hooks[y])});const zu=(g,y,A)=>A,Wt=qt({key:null,setSeries:!1,filters:{pub:vd,sub:vd},scales:[R,E[1]?E[1].scale:null],match:[xd,xd,zu],values:[null,null]},xe.sync);Wt.match.length==2&&Wt.match.push(zu),xe.sync=Wt;const ku=Wt.key,rl=ep(ku);function qs(g,y,A,P,F,Y,se){Wt.filters.pub(g,y,A,P,F,Y,se)&&rl.pub(g,y,A,P,F,Y,se)}rl.sub(n);function Dp(g,y,A,P,F,Y,se){Wt.filters.sub(g,y,A,P,F,Y,se)&&Wr[g](null,y,A,P,F,Y,se)}n.pub=Dp;function Ip(){rl.unsub(n),zc.delete(n),We.clear(),Uc(Po,Es,Bu),c.remove(),de==null||de.remove(),sn("destroy")}n.destroy=Ip;function sl(){sn("init",i,e),Ze(e||i.data,!1),W[R]?Zo(R,W[R]):Je(),ne=Dt.show&&(Dt.width>0||Dt.height>0),re=ie=!0,_e(i.width,i.height)}return E.forEach(ks),S.forEach(Yo),t?t instanceof HTMLElement?(t.appendChild(c),sl()):t(n,sl):sl(),n}cn.assign=qt;cn.fmtNum=cu;cn.rangeNum=Lo;cn.rangeLog=Bo;cn.rangeAsinh=ou;cn.orient=Ur;cn.pxRatio=xt;cn.join=MM;cn.fmtDate=hu,cn.tzDate=DM;cn.sync=ep;{cn.addGap=pS,cn.clipGaps=Ho;let i=cn.paths={points:ap};i.linear=lp,i.stepped=_S,i.bars=vS,i.spline=yS}function Wl(i){return Math.max(120,i.clientHeight-30)}class LS{constructor(){ae(this,"name","Plotter");ae(this,"container",null);ae(this,"tabsContainer",null);ae(this,"contentContainer",null);ae(this,"tooltip",null);ae(this,"paretoPlot",null);ae(this,"ablationPlot",null);ae(this,"variabilityPlot",null);ae(this,"currentTab","pareto");ae(this,"records",[]);ae(this,"ablationGroups",[]);ae(this,"paretoFlags",[]);ae(this,"chance",.1);ae(this,"paretoRecordIndices",[]);ae(this,"paretoXData",[]);ae(this,"paretoYData",[]);ae(this,"categoryLabels",[]);ae(this,"ablationFixedAxes","");ae(this,"onCampaignMetrics",e=>{const{data:t}=e;t!=null&&t.records&&Fn.observe(e==null?void 0:e.campaign_id,t)});ae(this,"onRunChanged",(e,t)=>{t&&(this.records=t.records??[],this.paretoFlags=t.pareto??[],this.ablationGroups=t.ablation_groups??[],typeof t.chance=="number"&&(this.chance=t.chance),this.updatePlots(),this.updateStatus())});Yt.register("campaign_metrics",this.onCampaignMetrics),Fn.onChange(this.onRunChanged)}async init(){this.createUI(),console.log("[Plotter] Initialized")}async destroy(){var e,t,n,r;Yt.unregister("campaign_metrics",this.onCampaignMetrics),(e=this.paretoPlot)==null||e.destroy(),(t=this.ablationPlot)==null||t.destroy(),(n=this.variabilityPlot)==null||n.destroy(),(r=this.container)==null||r.remove()}createUI(){const e=document.getElementById("ui-overlay");e&&(this.container=document.createElement("div"),this.container.id="plotter",this.container.style.cssText=`
      position: fixed;
      bottom: 140px;
      right: 20px;
      width: 520px;
      height: 430px;
      background: var(--bg-secondary);
      border: 1px solid var(--border);
      border-radius: 8px;
      display: flex;
      flex-direction: column;
      z-index: 150;
      box-shadow: 0 8px 32px rgba(0,0,0,0.4);
      transition: right 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    `,this.container.innerHTML=`
      <div id="plotter-tabs" style="
        display: flex;
        border-bottom: 1px solid var(--border);
        background: var(--bg-tertiary);
        border-radius: 8px 8px 0 0;
      ">
        <button class="plotter-tab active" data-tab="pareto" style="flex: 1;">Pareto</button>
        <button class="plotter-tab" data-tab="ablation" style="flex: 1;">Ablation</button>
        <button class="plotter-tab" data-tab="variability" style="flex: 1;">Variability</button>
      </div>
      <div id="plotter-content" style="flex: 1; position: relative; overflow: hidden;">
        <div id="plotter-pareto" style="width: 100%; height: 100%; display: block;"></div>
        <div id="plotter-ablation" style="width: 100%; height: 100%; display: none;"></div>
        <div id="plotter-variability" style="width: 100%; height: 100%; display: none;"></div>
      </div>
      <div id="plotter-toolbar" style="
        padding: 8px 12px;
        border-top: 1px solid var(--border);
        display: flex;
        gap: 8px;
        align-items: center;
        font-size: 11px;
        color: var(--text-secondary);
      ">
        <span id="plotter-status" style="
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        ">No data</span>
        <div style="flex: 1;"></div>
        <button id="plotter-download" style="
          padding: 4px 10px;
          background: var(--bg-tertiary);
          border: 1px solid var(--border);
          border-radius: 4px;
          color: var(--text-primary);
          font-size: 11px;
          cursor: pointer;
        ">Download PNG</button>
      </div>
    `,e.appendChild(this.container),this.tabsContainer=this.container.querySelector("#plotter-tabs"),this.contentContainer=this.container.querySelector("#plotter-content"),this.tooltip=document.createElement("div"),this.tooltip.id="plotter-tooltip",this.tooltip.style.cssText=`
      position: absolute;
      display: none;
      pointer-events: none;
      padding: 6px 10px;
      background: var(--bg-secondary);
      border: 1px solid var(--border-bright);
      border-radius: 6px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      color: var(--text-primary);
      white-space: nowrap;
      z-index: 10;
      box-shadow: 0 4px 16px rgba(0,0,0,0.5);
    `,this.container.appendChild(this.tooltip),this.tabsContainer.querySelectorAll(".plotter-tab").forEach(t=>{t.addEventListener("click",()=>this.switchTab(t.getAttribute("data-tab")))}),this.container.querySelector("#plotter-download").addEventListener("click",()=>this.downloadCurrent()),this.switchTab(this.currentTab))}showTab(e){e!==this.currentTab&&this.switchTab(e)}switchTab(e){this.currentTab=e,this.tabsContainer.querySelectorAll(".plotter-tab").forEach(n=>{n.classList.toggle("active",n.getAttribute("data-tab")===e)}),Object.entries({pareto:"plotter-pareto",ablation:"plotter-ablation",variability:"plotter-variability"}).forEach(([n,r])=>{const s=document.getElementById(r);s&&(s.style.display=n===e?"block":"none")}),e==="pareto"&&!this.paretoPlot&&this.initParetoPlot(),e==="ablation"&&!this.ablationPlot&&this.initAblationPlot(),e==="variability"&&!this.variabilityPlot&&this.initVariabilityPlot(),this.updatePlots()}updateStatus(){var r;const e=(r=this.container)==null?void 0:r.querySelector("#plotter-status");if(!e)return;const t=`${this.records.length} records | ${this.paretoFlags.filter(s=>s).length} Pareto`,n=this.ablationFixedAxes?` | fixed: ${this.ablationFixedAxes}`:"";e.textContent=t+n,e.title=e.textContent}updatePlots(){this.currentTab==="pareto"&&this.paretoPlot&&this.updateParetoPlot(),this.currentTab==="ablation"&&this.ablationPlot&&this.updateAblationPlot(),this.currentTab==="variability"&&this.variabilityPlot&&this.updateVariabilityPlot()}initParetoPlot(){const e=document.getElementById("plotter-pareto");if(!e)return;const t={width:e.clientWidth,height:Wl(e),title:"Pareto Frontier: validation accuracy vs speed",axes:[{label:"1 / walltime_s   (faster →)",grid:{stroke:be.border}},{label:"accuracy",grid:{stroke:be.border},side:1}],scales:{x:{time:!1},y:{time:!1}},series:[{},{label:"val_acc",stroke:be.gradient,width:0,points:{show:!0,size:8,stroke:"white",width:1,fill:(n,r)=>{var o;const s=this.paretoRecordIndices[r],a=s===void 0?void 0:this.records[s];return a&&nr[(o=a.coordinate)==null?void 0:o.credit]||be.gradient}}}],hooks:{draw:[n=>{const r=n.ctx;if(this.paretoFlags.some(a=>a)){const a=[];this.records.forEach((o,l)=>{this.paretoFlags[l]&&o.payload.walltime_s&&o.payload.val_acc&&a.push([1/o.payload.walltime_s,o.payload.val_acc])}),a.sort((o,l)=>o[0]-l[0]),a.length>1&&(r.beginPath(),r.strokeStyle=be.pareto,r.lineWidth=2,r.setLineDash([5,5]),a.forEach((o,l)=>{const c=n.valToPos(o[0],"x"),u=n.valToPos(o[1],"y");l===0?r.moveTo(c,u):r.lineTo(c,u)}),r.stroke(),r.setLineDash([])),a.forEach(o=>{const l=n.valToPos(o[0],"x"),c=n.valToPos(o[1],"y");r.beginPath(),r.arc(l,c,7,0,Math.PI*2),r.strokeStyle=be.pareto,r.lineWidth=1.5,r.stroke()})}const s=n.valToPos(this.chance,"y");r.strokeStyle=be.chance_line,r.lineWidth=1.5,r.setLineDash([4,4]),r.beginPath(),r.moveTo(n.bbox.left,s),r.lineTo(n.bbox.width,s),r.stroke(),r.setLineDash([])}],setCursor:[n=>{this.showScatterTooltip(n)}]},cursor:{show:!0,drag:{setScale:!0},focus:{prox:16}}};this.paretoPlot=new cn(t,[[],[]],e)}recordAt(e){const t=this.paretoRecordIndices[e];return t===void 0?void 0:this.records[t]}updateParetoPlot(){if(!this.paretoPlot||this.records.length===0)return;const e=[],t=[];this.paretoRecordIndices=[],this.records.forEach((s,a)=>{const o=s.payload.walltime_s,l=s.payload.val_acc;this.paretoRecordIndices.push(a),o&&l?(e.push(1/o),t.push(l)):(e.push(NaN),t.push(NaN))}),this.paretoPlot.setData([e,t]),this.paretoXData=e,this.paretoYData=t;const n=e.filter(Number.isFinite),r=t.filter(Number.isFinite);n.length>0&&this.fitScale(this.paretoPlot,"x",Math.min(...n),Math.max(...n)),r.length>0&&this.fitScale(this.paretoPlot,"y",Math.min(Math.min(...r),this.chance),Math.max(...r))}fitScale(e,t,n,r){if(!Number.isFinite(n)||!Number.isFinite(r))return;n===r&&(n-=.01,r+=.01);const s=(r-n)*.05;e.setScale(t,{min:n-s,max:r+s})}initAblationPlot(){const e=document.getElementById("plotter-ablation");if(!e)return;const t={width:e.clientWidth,height:Wl(e),title:"Ablation: credit arm → validation accuracy",axes:[{label:"credit arm",splits:()=>this.categoryIndices(),values:(n,r)=>r.map(s=>this.categoryLabels[s]??String(s)),grid:{stroke:be.border}},{label:"accuracy",grid:{stroke:be.border},side:1}],scales:{x:{time:!1},y:{time:!1}},series:[{},{label:"val_acc",width:0,points:{show:!1}}],hooks:{draw:[n=>{if(!this.ablationGroups.length)return;const r=n.ctx,s=this.ablationGroups.find(u=>u.axis==="credit");if(!s)return;const a=s.metrics.find(u=>u.metric==="val_acc");if(!a)return;const o=a.arms,l=n.bbox.width/(o.length*1.5);n.bbox.left,o.forEach((u,h)=>{const d=n.valToPos(h,"x"),m=n.valToPos(0,"y"),_=n.valToPos(u.mean,"y"),v=m-_;if(r.fillStyle=nr[u.value]||be.gradient,r.fillRect(d-l/2,_,l,v),u.std>0){const p=n.valToPos(u.mean+u.std,"y");r.strokeStyle=be.text_muted,r.lineWidth=1,r.beginPath(),r.moveTo(d,p),r.lineTo(d,m),r.stroke(),r.moveTo(d-3,p),r.lineTo(d+3,p),r.stroke()}});const c=n.valToPos(this.chance,"y");r.strokeStyle=be.chance_line,r.lineWidth=2,r.setLineDash([5,5]),r.beginPath(),r.moveTo(n.bbox.left,c),r.lineTo(n.bbox.width,c),r.stroke(),r.setLineDash([])}],setCursor:[n=>{this.showCategoryTooltip(n,"ablation")}]},cursor:{show:!0,drag:{setScale:!0}}};this.ablationPlot=new cn(t,[[],[]],e)}updateAblationPlot(){if(!this.ablationPlot||!this.ablationGroups.length)return;const e=this.ablationGroups.find(o=>o.axis==="credit");if(!e)return;const t=e.metrics.find(o=>o.metric==="val_acc");if(!t)return;const n=t.arms.map((o,l)=>l),r=t.arms.map(o=>o.mean);this.categoryLabels=t.arms.map(o=>o.value),this.ablationFixedAxes=e.fixed_axes.split(",").map(o=>o.split("=").pop()??o).join(", "),this.ablationPlot.setData([n,r]),this.fitScale(this.ablationPlot,"x",-.5,Math.max(n.length-.5,.5));const s=t.arms.flatMap(o=>[o.mean-o.std,o.mean+o.std]);s.length>0&&this.fitScale(this.ablationPlot,"y",Math.min(Math.min(...s),this.chance),Math.max(...s));const a=this.ablationPlot.root.querySelector(".u-title");a&&(a.textContent=`Ablation: ${e.axis} vs val_acc`)}initVariabilityPlot(){const e=document.getElementById("plotter-variability");if(!e)return;const t={width:e.clientWidth,height:Wl(e),title:"Seed variability: validation accuracy per arm",axes:[{label:"credit arm",splits:()=>this.categoryIndices(),values:(n,r)=>r.map(s=>this.categoryLabels[s]??String(s)),grid:{stroke:be.border}},{label:"accuracy",grid:{stroke:be.border},side:1}],scales:{x:{time:!1},y:{time:!1}},series:[{},{label:"val_acc",width:0,points:{show:!1}}],hooks:{draw:[n=>{if(!this.records.length)return;const r=n.ctx,s={};this.records.forEach(c=>{const u=c.coordinate.credit,h=c.payload.val_acc;h!==void 0&&(s[u]||(s[u]=[])).push(h)});const a=Object.keys(s).sort(),o=n.bbox.width/(a.length*2);a.forEach((c,u)=>{const h=s[c].sort((x,C)=>x-C),d=h.length;if(d===0)return;const m=h[Math.floor(d*.25)],_=h[Math.floor(d*.5)],v=h[Math.floor(d*.75)],p=v-m,f=Math.max(h[0],m-1.5*p),E=Math.min(h[d-1],v+1.5*p),S=n.valToPos(u,"x"),T=n.valToPos(f,"y"),z=n.valToPos(m,"y"),R=n.valToPos(_,"y"),L=n.valToPos(v,"y"),O=n.valToPos(E,"y"),w=nr[c]||be.gradient;r.strokeStyle=w,r.lineWidth=1.5,r.beginPath(),r.moveTo(S,T),r.lineTo(S,z),r.moveTo(S,L),r.lineTo(S,O),r.stroke(),r.fillStyle=w+"44",r.strokeStyle=w,r.lineWidth=1.5,r.fillRect(S-o/2,L,o,z-L),r.strokeRect(S-o/2,L,o,z-L),r.strokeStyle="white",r.lineWidth=2,r.beginPath(),r.moveTo(S-o/2,R),r.lineTo(S+o/2,R),r.stroke(),h.forEach(x=>{if(x<f||x>E){const C=n.valToPos(x,"y");r.fillStyle=w,r.beginPath(),r.arc(S,C,2,0,Math.PI*2),r.fill()}})});const l=n.valToPos(this.chance,"y");r.strokeStyle=be.chance_line,r.lineWidth=2,r.setLineDash([5,5]),r.beginPath(),r.moveTo(n.bbox.left,l),r.lineTo(n.bbox.width,l),r.stroke(),r.setLineDash([])}],setCursor:[n=>{this.showCategoryTooltip(n,"variability")}]},cursor:{show:!0,drag:{setScale:!0}}};this.variabilityPlot=new cn(t,[[],[]],e)}updateVariabilityPlot(){if(!this.variabilityPlot||!this.records.length)return;const e=Array.from(new Set(this.records.map(s=>s.coordinate.credit))).sort(),t=e.map((s,a)=>a),n=e.map(()=>0);this.categoryLabels=e,this.variabilityPlot.setData([t,n]),this.fitScale(this.variabilityPlot,"x",-.5,Math.max(e.length-.5,.5));const r=this.records.map(s=>s.payload.val_acc).filter(s=>typeof s=="number");r.length>0&&this.fitScale(this.variabilityPlot,"y",Math.min(Math.min(...r),this.chance),Math.max(...r))}categoryIndices(){return this.categoryLabels.map((e,t)=>t)}showTooltip(e,t){if(!this.tooltip||!this.container)return;const n=e.cursor;if(!n||n.left==null||n.top==null){this.hideTooltip();return}const r=e.ctx.canvas.getBoundingClientRect(),s=this.container.getBoundingClientRect();this.tooltip.innerHTML=t,this.tooltip.style.display="block",this.tooltip.style.left=`${r.left-s.left+e.bbox.left+n.left+14}px`,this.tooltip.style.top=`${r.top-s.top+e.bbox.top+n.top+14}px`}hideTooltip(){this.tooltip&&(this.tooltip.style.display="none")}showScatterTooltip(e){var d,m;const t=e.cursor;if(!t||t.left==null||t.top==null){this.hideTooltip();return}let n=-1,r=1/0;if(this.paretoXData.forEach((_,v)=>{const p=this.paretoYData[v];if(!Number.isFinite(_)||!Number.isFinite(p))return;const f=e.valToPos(_,"x"),E=e.valToPos(p,"y");if(!Number.isFinite(f)||!Number.isFinite(E))return;const S=(f-t.left)**2+(E-t.top)**2;S<r&&(r=S,n=v)}),n<0||r>400){this.hideTooltip();return}const s=this.recordAt(n);if(!s){this.hideTooltip();return}const a=this.paretoRecordIndices[n],o=((d=s.coordinate)==null?void 0:d.credit)??"?",l=s.payload.val_acc??0,c=s.payload.walltime_s??0,u=((m=s.schedule)==null?void 0:m.seed)??"?",h=this.paretoFlags[a]?" · PARETO":"";this.showTooltip(e,`${o} · val_acc ${l.toFixed(3)} · ${c.toFixed(1)}s · seed ${u}${h}`)}showCategoryTooltip(e,t){const n=e.cursor;if(!n||n.left==null||n.top==null){this.hideTooltip();return}const r=Math.round(e.posToVal(n.left,"x"));if(r<0||r>=this.categoryLabels.length){this.hideTooltip();return}const s=this.categoryLabels[r];if(t==="ablation"){const u=this.ablationGroups.find(m=>m.axis==="credit"),h=u==null?void 0:u.metrics.find(m=>m.metric==="val_acc"),d=h==null?void 0:h.arms[r];if(!d){this.hideTooltip();return}this.showTooltip(e,`${s} · ${d.mean.toFixed(3)} ± ${d.std.toFixed(3)} (n=${d.count})${d.at_chance?" · at chance":""}`);return}const a=this.records.filter(u=>u.coordinate.credit===s).map(u=>u.payload.val_acc).filter(u=>typeof u=="number").sort((u,h)=>u-h);if(a.length===0){this.hideTooltip();return}const o=a[Math.floor(a.length*.5)],l=a[Math.floor(a.length*.25)],c=a[Math.floor(a.length*.75)];this.showTooltip(e,`${s} · median ${o.toFixed(3)} · IQR ${(c-l).toFixed(3)} · n=${a.length}`)}downloadCurrent(){const t={pareto:this.paretoPlot,ablation:this.ablationPlot,variability:this.variabilityPlot}[this.currentTab];if(!t)return;const n=document.createElement("a");n.download=`computronium-${this.currentTab}-${Date.now()}.png`,n.href=this.exportImage(t),n.click()}exportImage(e){const t=Array.from(e.root.querySelectorAll("canvas")),n=e.root.getBoundingClientRect(),r=Math.max(...t.map(l=>l.width),1),s=Math.max(...t.map(l=>l.height),1),a=document.createElement("canvas");a.width=r,a.height=s;const o=a.getContext("2d");return o?(o.fillStyle=be.bg,o.fillRect(0,0,r,s),t.forEach(l=>{const c=l.getBoundingClientRect();if(c.width===0||c.height===0)return;const u=l.width/c.width;o.drawImage(l,(c.left-n.left)*u,(c.top-n.top)*u,l.width,l.height)}),a.toDataURL("image/png")):e.ctx.canvas.toDataURL("image/png")}}const vu=new LS;sr.register(vu);class DS{constructor(){ae(this,"name","LiveRail");ae(this,"container",null);ae(this,"logContainer",null);ae(this,"events",[]);ae(this,"maxEvents",50);ae(this,"onPipelineEvent",e=>{this.events.unshift(e),this.events.length>this.maxEvents&&this.events.pop(),this.render()});ae(this,"onStatusUpdate",e=>{var s,a,o;const t=((s=e==null?void 0:e.data)==null?void 0:s.running_campaigns)??0,n=((a=e==null?void 0:e.data)==null?void 0:a.queued_campaigns)??0,r=(o=this.container)==null?void 0:o.querySelector("#rail-queue");r&&(r.textContent=`${t} running · ${n} queued`)});Yt.register("pipeline_event",this.onPipelineEvent),Yt.register("status_update",this.onStatusUpdate)}async init(){this.createUI(),Cs.onStateChange(e=>this.setConnected(e==="connected")),console.log("[LiveRail] Initialized")}async destroy(){var e;Yt.unregister("pipeline_event",this.onPipelineEvent),Yt.unregister("status_update",this.onStatusUpdate),(e=this.container)==null||e.remove()}createUI(){const e=document.getElementById("ui-overlay");e&&(this.container=document.createElement("div"),this.container.id="live-rail",this.container.style.cssText=`
      position: fixed;
      bottom: 0;
      left: 0;
      right: 0;
      height: 120px;
      background: linear-gradient(to top, var(--bg), transparent);
      border-top: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      z-index: 100;
      pointer-events: none;
    `,this.container.innerHTML=`
      <div style="
        padding: 8px 16px;
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 11px;
        color: var(--text-secondary);
        border-bottom: 1px solid var(--border);
        background: var(--bg-secondary);
      ">
        <span style="font-weight: 600; color: var(--text-primary);">LIVE RAIL</span>
        <span id="rail-connection" style="
          display: inline-flex;
          align-items: center;
          gap: 4px;
          padding: 2px 8px;
          border-radius: 12px;
          background: var(--error)22;
          border: 1px solid var(--error)88;
          color: var(--error);
        ">
          <span class="dot" style="width: 6px; height: 6px; border-radius: 50%; background: var(--error);"></span>
          <span class="rail-label">Disconnected</span>
        </span>
        <div style="flex: 1;"></div>
        <span id="rail-queue" style="color: var(--text-secondary);">0 running · 0 queued</span>
        <span id="rail-count">0 events</span>
      </div>
      <div id="rail-log" style="
        flex: 1;
        overflow-x: auto;
        overflow-y: hidden;
        display: flex;
        gap: 24px;
        padding: 8px 16px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        white-space: nowrap;
      "></div>
    `,e.appendChild(this.container),this.logContainer=this.container.querySelector("#rail-log"))}toggle(){this.container&&(this.container.style.display=this.container.style.display==="none"?"":"none")}setConnected(e){var a;const t=(a=this.container)==null?void 0:a.querySelector("#rail-connection");if(!t)return;const n=t.querySelector(".dot"),r=t.querySelector(".rail-label");if(!n||!r)return;const s=e?be.ok:be.error;n.style.background=s,t.style.background=s+"22",t.style.borderColor=s+"88",t.style.color=s,r.textContent=e?"Connected":"Disconnected"}render(){var t;if(!this.logContainer)return;this.logContainer.innerHTML=this.events.map(n=>{const r=new Date(n.timestamp).toLocaleTimeString(),a={ok:be.ok,warn:be.warn,error:be.error}[n.level]||be.text_secondary,o=n.level==="ok"?"✓":n.level==="warn"?"⚠":"✗";return`
          <span style="
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 12px;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 16px;
            color: var(--text-primary);
          ">
            <span style="color: var(--text-secondary);">${r}</span>
            <span style="color: ${a};">${o}</span>
            <span style="color: var(--text-muted);">[${n.stage}]</span>
            <span>${n.message}</span>
          </span>
        `}).join("");const e=(t=this.container)==null?void 0:t.querySelector("#rail-count");e&&(e.textContent=`${this.events.length} events`),this.logContainer.scrollLeft=0}}const xu=new DS;sr.register(xu);const IS=4e3,US={ok:be.text_primary,warn:be.warn,error:be.error};class NS{constructor(){ae(this,"name","Caption");ae(this,"container",null);ae(this,"headline",null);ae(this,"context",null);ae(this,"state",[]);ae(this,"spoken",null);ae(this,"last",null);ae(this,"holdTimer",null);ae(this,"onNarration",e=>{this.state=(e==null?void 0:e.state)??[],this.render()});ae(this,"onEvent",e=>{e!=null&&e.sentence&&this.say(e.sentence,e.level??"ok")});Yt.register("narration",this.onNarration),Yt.register("pipeline_event",this.onEvent)}async init(){this.createUI(),this.render()}async destroy(){var e;Yt.unregister("narration",this.onNarration),Yt.unregister("pipeline_event",this.onEvent),this.holdTimer!==null&&window.clearTimeout(this.holdTimer),(e=this.container)==null||e.remove()}toggle(){this.container&&(this.container.style.display=this.container.style.display==="none"?"":"none")}say(e,t="ok"){e&&(this.spoken={text:e,level:t},this.last={text:e,level:t},this.render(),this.holdTimer!==null&&window.clearTimeout(this.holdTimer),this.holdTimer=window.setTimeout(()=>{this.spoken=null,this.holdTimer=null,this.render()},IS))}createUI(){const e=document.getElementById("ui-overlay");e&&(this.container=document.createElement("div"),this.container.id="caption",this.container.style.cssText=`
      position: fixed;
      bottom: 132px;
      left: 50%;
      transform: translateX(-50%);
      width: 820px;
      max-width: calc(100vw - 80px);
      padding: 12px 20px;
      background: rgba(10, 14, 20, 0.82);
      border: 1px solid var(--border);
      border-radius: 10px;
      text-align: center;
      z-index: 160;
      pointer-events: none;
      box-shadow: 0 8px 32px rgba(0,0,0,0.45);
    `,this.container.innerHTML=`
      <div id="caption-headline" style="
        font-size: 22px;
        line-height: 1.3;
        color: var(--text-primary);
        text-shadow: 0 2px 6px rgba(0,0,0,0.8);
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
      ">The dashboard is starting.</div>
      <div id="caption-context" style="
        margin-top: 6px;
        font-size: 14px;
        line-height: 1.35;
        color: var(--text-secondary);
      "></div>
    `,e.appendChild(this.container),this.headline=this.container.querySelector("#caption-headline"),this.context=this.container.querySelector("#caption-context"))}render(){if(!(!this.headline||!this.context)){if(this.spoken){this.headline.textContent=this.spoken.text,this.headline.style.color=this.colorOf(this.spoken.level),this.context.textContent=this.state.join(" ");return}if(this.state.length>0){this.headline.textContent=this.state[0],this.headline.style.color=be.text_primary,this.context.textContent=this.state.slice(1).join(" ");return}if(this.last){this.headline.textContent=this.last.text,this.headline.style.color=this.colorOf(this.last.level),this.context.textContent="";return}this.headline.textContent="The dashboard is starting.",this.headline.style.color=be.text_primary,this.context.textContent=""}}colorOf(e){return US[e]??be.text_primary}}const yu=new NS;sr.register(yu);class FS{constructor(){ae(this,"name","HUD");ae(this,"panel",null);ae(this,"modeChip",null);ae(this,"connectionPill",null);ae(this,"rows",new Map);ae(this,"rowElements",new Map);ae(this,"claimValue",null);ae(this,"sourceValue",null);ae(this,"statusData",{});ae(this,"resources",{});ae(this,"requiredSeeds",0);ae(this,"measuredSeeds",0);ae(this,"connected",!1);ae(this,"animationTime",0);ae(this,"onStatusUpdate",e=>{const t=(e==null?void 0:e.data)??e;t&&(this.statusData=t,this.updateQueueRows())});ae(this,"onCampaignMetrics",e=>{const t=e==null?void 0:e.data;t&&Fn.observe(e==null?void 0:e.campaign_id,t)});ae(this,"onRunChanged",(e,t)=>{var n;t&&(this.resources=t.resources??{},typeof t.required_seeds=="number"&&(this.requiredSeeds=t.required_seeds),this.measuredSeeds=this.resources.seeds_per_arm??((n=t.records)==null?void 0:n.length)??0,this.updateModeChip(t.run),this.updateSource(t.store),this.updateResourceRows(),this.updateClaim())});Yt.register("status_update",this.onStatusUpdate),Yt.register("campaign_metrics",this.onCampaignMetrics),Fn.onChange(this.onRunChanged)}async init(){this.createPanel(),this.createModeChip(),Cs.onStateChange(e=>{this.connected=e==="connected",this.updateConnection()}),console.log("[HUD] Initialized")}async destroy(){var e,t;Yt.unregister("status_update",this.onStatusUpdate),Yt.unregister("campaign_metrics",this.onCampaignMetrics),(e=this.panel)==null||e.remove(),(t=this.modeChip)==null||t.remove()}createPanel(){const e=document.getElementById("ui-overlay");if(!e)return;this.panel=document.createElement("div"),this.panel.id="hud",this.panel.style.cssText=`
      position: fixed;
      top: 20px;
      right: 20px;
      width: 260px;
      background: var(--bg-secondary);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 14px 16px;
      font-size: 11px;
      z-index: 150;
      box-shadow: 0 8px 32px rgba(0,0,0,0.4);
      transition: right 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    `,this.panel.innerHTML=`
      <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
        <span style="font-weight: 600; color: var(--text-primary); letter-spacing: 0.08em;">MISSION CONTROL</span>
        <div style="flex: 1;"></div>
        <span id="hud-connection" style="
          display: inline-flex;
          align-items: center;
          gap: 4px;
          padding: 2px 8px;
          border-radius: 12px;
          background: var(--error)22;
          border: 1px solid var(--error)88;
          color: var(--error);
        ">
          <span class="dot" style="width: 6px; height: 6px; border-radius: 50%; background: var(--error);"></span>
          <span>offline</span>
        </span>
      </div>
      <div id="hud-meters" style="display: flex; flex-direction: column; gap: 9px;"></div>
      <div style="margin-top: 12px; padding-top: 10px; border-top: 1px solid var(--border); display: flex; justify-content: space-between; align-items: baseline;">
        <span style="color: var(--text-secondary);">PICTURE</span>
        <span id="hud-source" style="font-weight: 600; color: ${be.text_secondary};">—</span>
      </div>
      <div style="margin-top: 12px; padding-top: 10px; border-top: 1px solid var(--border); display: flex; justify-content: space-between; align-items: baseline;">
        <span style="color: var(--text-secondary);">SEEDS TO CLAIM</span>
        <span id="hud-claim" style="font-weight: 700; color: ${be.insufficient};">—</span>
      </div>
    `,e.appendChild(this.panel);const t=this.panel.querySelector("#hud-meters");this.addMeter(t,"device","DEVICE",be.gradient),this.addMeter(t,"memory","MEMORY",be.memory),this.addMeter(t,"walltime","WALLTIME",be.cpu),this.addMeter(t,"gpu","GPU",be.gpu),this.addMeter(t,"cpu","CPU",be.cpu),this.addMeter(t,"records","RECORDS",be.promoted),this.claimValue=this.panel.querySelector("#hud-claim"),this.connectionPill=this.panel.querySelector("#hud-connection"),this.sourceValue=this.panel.querySelector("#hud-source")}addMeter(e,t,n,r){const s=document.createElement("div");s.style.cssText="display: flex; flex-direction: column; gap: 3px;",s.innerHTML=`
      <div style="display: flex; justify-content: space-between;">
        <span style="color: var(--text-secondary);">${n}</span>
        <span class="hud-value" style="color: var(--text-primary);">—</span>
      </div>
      <div style="height: 4px; background: var(--bg); border-radius: 2px; overflow: hidden;">
        <div class="hud-fill" style="height: 100%; width: 0%; background: ${r}; border-radius: 2px; transition: width 0.4s ease;"></div>
      </div>
    `,e.appendChild(s),this.rows.set(t,{key:t,label:n,value:"",fraction:0,color:r}),this.rowElements.set(t,{fill:s.querySelector(".hud-fill"),value:s.querySelector(".hud-value")})}createModeChip(){const e=document.getElementById("ui-overlay");e&&(this.modeChip=document.createElement("div"),this.modeChip.id="mode-chip",this.modeChip.style.cssText=`
      position: fixed;
      top: 20px;
      left: 20px;
      padding: 6px 14px;
      border-radius: 16px;
      background: ${be.text_muted}22;
      border: 1px solid ${be.text_muted}88;
      color: ${be.text_muted};
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 0.1em;
      z-index: 150;
      line-height: 1.5;
    `,this.modeChip.innerHTML=`
      <div class="mode-label">NO RUN</div>
      <div class="mode-detail" style="
        font-weight: 400;
        letter-spacing: 0.02em;
        font-size: 10px;
        opacity: 0.8;
      "></div>
    `,e.appendChild(this.modeChip))}updateModeChip(e){if(!this.modeChip)return;const t=(e==null?void 0:e.mode)??"NO RUN",n=t==="PREREGISTERED"?be.passed:t==="EXPLORATORY"?be.insufficient:be.text_muted;this.modeChip.style.background=`${n}22`,this.modeChip.style.borderColor=`${n}88`,this.modeChip.style.color=n;const r=this.modeChip.querySelector(".mode-label");r&&(r.textContent=t);const s=this.modeChip.querySelector(".mode-detail");s&&(s.textContent=[e==null?void 0:e.profile,((e==null?void 0:e.tasks)??[]).join(", "),e==null?void 0:e.fidelity].filter(Boolean).join(" · ")),this.modeChip.title=e?`run ${e.run_id??"?"} · objectives: ${(e.objectives??[]).join(", ")||"none"}`:"No run has reported yet"}setMeter(e,t,n){const r=this.rows.get(e),s=this.rowElements.get(e);!r||!s||(r.value=t,r.fraction=Math.max(0,Math.min(1,n)),s.value.textContent=t,s.fill.style.width=`${(r.fraction*100).toFixed(1)}%`)}updateSource(e){if(!this.sourceValue)return;const t=e==null?void 0:e.source;if(!t){this.sourceValue.textContent="—",this.sourceValue.style.color=be.text_secondary;return}if(t==="snapshot"){const n=e!=null&&e.published_at?new Date(e.published_at).toLocaleTimeString():"";this.sourceValue.textContent=n?`snapshot ${n}`:"snapshot",this.sourceValue.style.color=be.insufficient,this.sourceValue.title="The writer published this copy; it is as fresh as its last publish.";return}this.sourceValue.textContent="live",this.sourceValue.style.color=be.passed,this.sourceValue.title="The store itself, read as it is written."}updateQueueRows(){const e=this.statusData;this.setMeter("gpu",e.max_gpus?`${e.used_gpus??0} / ${e.max_gpus}`:"—",e.max_gpus?(e.used_gpus??0)/e.max_gpus:0),this.setMeter("cpu",e.max_cpus?`${e.used_cpus??0} / ${e.max_cpus}`:"—",e.max_cpus?(e.used_cpus??0)/e.max_cpus:0)}updateResourceRows(){const e=this.resources;this.setMeter("device",e.device??"—",e.device?1:0),this.setMeter("memory",e.memory_mb!==void 0?`${e.memory_mb.toFixed(1)} MB`:"—",e.memory_mb!==void 0?Math.min(1,e.memory_mb/2048):0),this.setMeter("walltime",e.walltime_s!==void 0?`${e.walltime_s.toFixed(1)} s`:"—",e.walltime_s!==void 0?Math.min(1,e.walltime_s/120):0),this.setMeter("records",e.records!==void 0?`${e.records}`:"—",e.records!==void 0?Math.min(1,e.records/20):0)}updateClaim(){if(!this.claimValue)return;if(this.requiredSeeds<=0){this.claimValue.textContent="—";return}const e=Math.max(0,this.requiredSeeds-this.measuredSeeds);this.claimValue.textContent=`${e} more (${this.requiredSeeds} needed)`}updateConnection(){if(!this.connectionPill)return;const e=this.connectionPill.querySelector(".dot"),t=this.connectionPill.querySelector("span:last-child"),n=this.connected?be.ok:be.error;e.style.background=n,this.connectionPill.style.background=`${n}22`,this.connectionPill.style.borderColor=`${n}88`,this.connectionPill.style.color=n,t.textContent=this.connected?"live":"offline"}toggle(){this.panel&&(this.panel.style.display=this.panel.style.display==="none"?"":"none")}update(e){var n;this.animationTime+=e;const t=.5+.5*Math.sin(this.animationTime*2);(n=this.connectionPill)==null||n.style.setProperty("opacity",`${.75+.25*t}`)}}const Xo=new FS;sr.register(Xo);const OS=/swiftshader|llvmpipe|software|basic render/i;function BS(){const i=zS();return{software:i,fps:i?12:60,shadows:!i,antialias:!i}}function zS(){try{const i=document.createElement("canvas"),e=i.getContext("webgl2")??i.getContext("webgl");if(!e)return!0;const t=e.getExtension("WEBGL_debug_renderer_info"),n=String(t?e.getParameter(t.UNMASKED_RENDERER_WEBGL):e.getParameter(e.RENDERER));return OS.test(n)}catch{return!0}}window.addEventListener("error",i=>{var e;console.error("[Global Error]",i.error),fp(((e=i.error)==null?void 0:e.message)||"Unknown error")});window.addEventListener("unhandledrejection",i=>{var e;console.error("[Unhandled Rejection]",i.reason),fp(((e=i.reason)==null?void 0:e.message)||"Unhandled promise rejection")});let Pi=null,ji=null;function dp(i="Initializing dashboard..."){const e=document.getElementById("ui-overlay");e&&(Pi=document.createElement("div"),Pi.id="global-loading",Pi.style.cssText=`
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 32px 48px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
    z-index: 1000;
    box-shadow: 0 16px 48px rgba(0,0,0,0.5);
  `,Pi.innerHTML=`
    <div style="
      width: 48px;
      height: 48px;
      border: 3px solid var(--border);
      border-top-color: ${be.gradient};
      border-radius: 50%;
      animation: spin 1s linear infinite;
    "></div>
    <div style="font-size: 14px; color: var(--text-primary);">${i}</div>
    <style>
      @keyframes spin { to { transform: rotate(360deg); } }
    </style>
  `,e.appendChild(Pi))}function Hd(){Pi==null||Pi.remove(),Pi=null}function fp(i){const e=document.getElementById("ui-overlay");e&&(ji=document.createElement("div"),ji.id="global-error",ji.style.cssText=`
    position: fixed;
    top: 20px;
    right: 20px;
    background: ${be.error}22;
    border: 1px solid ${be.error}88;
    border-radius: 8px;
    padding: 16px 24px;
    color: ${be.error};
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    z-index: 1000;
    max-width: 400px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    display: flex;
    align-items: center;
    gap: 12px;
  `,ji.innerHTML=`
    <span>✗</span>
    <span>${i}</span>
    <button onclick="this.parentElement.remove()" style="
      background: none;
      border: none;
      color: ${be.error};
      font-size: 18px;
      cursor: pointer;
      line-height: 1;
      padding: 0 4px;
    ">&times;</button>
  `,e.appendChild(ji),setTimeout(()=>ji==null?void 0:ji.remove(),1e4))}Cs.connect();dp("Connecting to dashboard...");Cs.waitForConnection(15e3).then(i=>{i?Hd():(dp("Connection timeout — retrying..."),Cs.onStateChange(e=>{e==="connected"&&Hd()}))});const kS={1:"pareto",2:"ablation",3:"variability"};window.addEventListener("keydown",i=>{if(i.metaKey||i.ctrlKey||i.altKey)return;const e=kS[i.key];if(e){vu.showTab(e);return}const t=i.key.toLowerCase();t==="h"&&Xo.toggle(),t==="l"&&xu.toggle(),t==="c"&&yu.toggle()});const HS=document.getElementById("dashboard-canvas"),zs=BS(),qn=new Mf({canvas:HS,antialias:zs.antialias,alpha:!0,powerPreference:"high-performance"});qn.setSize(window.innerWidth,window.innerHeight);qn.setPixelRatio(zs.software?1:Math.min(window.devicePixelRatio,2));qn.shadowMap.enabled=zs.shadows;qn.shadowMap.type=Gd;qn.toneMapping=Xd;qn.toneMappingExposure=1.2;const Bi=new eu;Bi.background=new tt(658964);Bi.fog=new Qc(658964,.015);const or=new _n(60,window.innerWidth/window.innerHeight,.1,200);or.position.set(3.3,4.4,8.8);or.lookAt(0,1,.1);const vi=new yy(or,qn.domElement);vi.target.set(0,1,.1);vi.enableDamping=!0;vi.dampingFactor=.05;vi.enablePan=!0;vi.minDistance=5;vi.maxDistance=80;vi.maxPolarAngle=Math.PI/2-.05;Ey({scene:Bi,camera:or,renderer:qn,controls:vi});const VS=new uy(4473958,.6);Bi.add(VS);const ai=new cy(16777215,1.2);ai.position.set(10,20,10);ai.castShadow=zs.shadows;ai.shadow.mapSize.width=2048;ai.shadow.mapSize.height=2048;ai.shadow.camera.near=1;ai.shadow.camera.far=50;ai.shadow.camera.left=-20;ai.shadow.camera.right=20;ai.shadow.camera.top=20;ai.shadow.camera.bottom=-20;Bi.add(ai);const GS=new ay(8956671,2236979,.5);Bi.add(GS);const Mu=new dy(8,8,2371648,1449256);Mu.position.y=-.01;const pp=Mu.material;pp.transparent=!0;pp.opacity=.35;Bi.add(Mu);function WS(){or.aspect=window.innerWidth/window.innerHeight,or.updateProjectionMatrix(),qn.setSize(window.innerWidth,window.innerHeight),qn.setPixelRatio(zs.software?1:Math.min(window.devicePixelRatio,2))}window.addEventListener("resize",WS);const XS=1e3/zs.fps;let Xl=0;function mp(i){if(requestAnimationFrame(mp),i-Xl<XS)return;const e=(i-Xl)/1e3;Xl=i,vi.update(),iu.update(e),Xo.update(e),qn.render(Bi,or)}requestAnimationFrame(mp);window.__DASHBOARD__={scene:Bi,camera:or,renderer:qn,controls:vi,discoveryMap:iu,cellDrawer:Tf,plotter:vu,liveRail:xu,caption:yu,hud:Xo,wsClient:Cs,router:Yt};console.log("🚀 Computronium Dashboard initialized");
//# sourceMappingURL=dashboard.js.map
