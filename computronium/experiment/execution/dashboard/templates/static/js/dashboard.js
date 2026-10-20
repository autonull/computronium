var Sp=Object.defineProperty;var yp=(i,e,t)=>e in i?Sp(i,e,{enumerable:!0,configurable:!0,writable:!0,value:t}):i[e]=t;var ye=(i,e,t)=>yp(i,typeof e!="symbol"?e+"":e,t);/**
 * @license
 * Copyright 2010-2024 Three.js Authors
 * SPDX-License-Identifier: MIT
 */const Pc="168",Wr={ROTATE:0,DOLLY:1,PAN:2},Xr={ROTATE:0,PAN:1,DOLLY_PAN:2,DOLLY_ROTATE:3},Ep=0,Lu=1,bp=2,Rd=1,Cd=2,Ai=3,er=0,Cn=1,mi=2,Zi=0,gs=1,Du=2,Iu=3,Uu=4,Tp=5,xr=100,wp=101,Ap=102,Rp=103,Cp=104,Pp=200,Lp=201,Dp=202,Ip=203,zl=204,kl=205,Up=206,Np=207,Fp=208,Op=209,Bp=210,zp=211,kp=212,Hp=213,Vp=214,Gp=0,Wp=1,Xp=2,ho=3,Yp=4,qp=5,$p=6,jp=7,Pd=0,Kp=1,Zp=2,Ji=0,Jp=1,Qp=2,em=3,Ld=4,tm=5,nm=6,im=7,Dd=300,Es=301,bs=302,Hl=303,Vl=304,Ao=306,Gl=1e3,yr=1001,Wl=1002,Wn=1003,rm=1004,Sa=1005,ti=1006,tl=1007,Er=1008,Ui=1009,Id=1010,Ud=1011,la=1012,Lc=1013,wr=1014,Ci=1015,ha=1016,Dc=1017,Ic=1018,Ts=1020,Nd=35902,Fd=1021,Od=1022,ri=1023,Bd=1024,zd=1025,_s=1026,ws=1027,kd=1028,Uc=1029,Hd=1030,Nc=1031,Fc=1033,no=33776,io=33777,ro=33778,so=33779,Xl=35840,Yl=35841,ql=35842,$l=35843,jl=36196,Kl=37492,Zl=37496,Jl=37808,Ql=37809,ec=37810,tc=37811,nc=37812,ic=37813,rc=37814,sc=37815,ac=37816,oc=37817,lc=37818,cc=37819,uc=37820,hc=37821,ao=36492,dc=36494,fc=36495,Vd=36283,pc=36284,mc=36285,gc=36286,sm=3200,am=3201,Gd=0,om=1,Ki="",fi="srgb",rr="srgb-linear",Oc="display-p3",Ro="display-p3-linear",fo="linear",Nt="srgb",po="rec709",mo="p3",Yr=7680,Nu=519,lm=512,cm=513,um=514,Wd=515,hm=516,dm=517,fm=518,pm=519,_c=35044,Fu="300 es",Pi=2e3,go=2001;let Ds=class{addEventListener(e,t){this._listeners===void 0&&(this._listeners={});const n=this._listeners;n[e]===void 0&&(n[e]=[]),n[e].indexOf(t)===-1&&n[e].push(t)}hasEventListener(e,t){if(this._listeners===void 0)return!1;const n=this._listeners;return n[e]!==void 0&&n[e].indexOf(t)!==-1}removeEventListener(e,t){if(this._listeners===void 0)return;const r=this._listeners[e];if(r!==void 0){const s=r.indexOf(t);s!==-1&&r.splice(s,1)}}dispatchEvent(e){if(this._listeners===void 0)return;const n=this._listeners[e.type];if(n!==void 0){e.target=this;const r=n.slice(0);for(let s=0,a=r.length;s<a;s++)r[s].call(this,e);e.target=null}}};const dn=["00","01","02","03","04","05","06","07","08","09","0a","0b","0c","0d","0e","0f","10","11","12","13","14","15","16","17","18","19","1a","1b","1c","1d","1e","1f","20","21","22","23","24","25","26","27","28","29","2a","2b","2c","2d","2e","2f","30","31","32","33","34","35","36","37","38","39","3a","3b","3c","3d","3e","3f","40","41","42","43","44","45","46","47","48","49","4a","4b","4c","4d","4e","4f","50","51","52","53","54","55","56","57","58","59","5a","5b","5c","5d","5e","5f","60","61","62","63","64","65","66","67","68","69","6a","6b","6c","6d","6e","6f","70","71","72","73","74","75","76","77","78","79","7a","7b","7c","7d","7e","7f","80","81","82","83","84","85","86","87","88","89","8a","8b","8c","8d","8e","8f","90","91","92","93","94","95","96","97","98","99","9a","9b","9c","9d","9e","9f","a0","a1","a2","a3","a4","a5","a6","a7","a8","a9","aa","ab","ac","ad","ae","af","b0","b1","b2","b3","b4","b5","b6","b7","b8","b9","ba","bb","bc","bd","be","bf","c0","c1","c2","c3","c4","c5","c6","c7","c8","c9","ca","cb","cc","cd","ce","cf","d0","d1","d2","d3","d4","d5","d6","d7","d8","d9","da","db","dc","dd","de","df","e0","e1","e2","e3","e4","e5","e6","e7","e8","e9","ea","eb","ec","ed","ee","ef","f0","f1","f2","f3","f4","f5","f6","f7","f8","f9","fa","fb","fc","fd","fe","ff"];let Ou=1234567;const vs=Math.PI/180,ca=180/Math.PI;function Li(){const i=Math.random()*4294967295|0,e=Math.random()*4294967295|0,t=Math.random()*4294967295|0,n=Math.random()*4294967295|0;return(dn[i&255]+dn[i>>8&255]+dn[i>>16&255]+dn[i>>24&255]+"-"+dn[e&255]+dn[e>>8&255]+"-"+dn[e>>16&15|64]+dn[e>>24&255]+"-"+dn[t&63|128]+dn[t>>8&255]+"-"+dn[t>>16&255]+dn[t>>24&255]+dn[n&255]+dn[n>>8&255]+dn[n>>16&255]+dn[n>>24&255]).toLowerCase()}function pn(i,e,t){return Math.max(e,Math.min(t,i))}function Bc(i,e){return(i%e+e)%e}function mm(i,e,t,n,r){return n+(i-e)*(r-n)/(t-e)}function gm(i,e,t){return i!==e?(t-i)/(e-i):0}function sa(i,e,t){return(1-t)*i+t*e}function _m(i,e,t,n){return sa(i,e,1-Math.exp(-t*n))}function vm(i,e=1){return e-Math.abs(Bc(i,e*2)-e)}function xm(i,e,t){return i<=e?0:i>=t?1:(i=(i-e)/(t-e),i*i*(3-2*i))}function Mm(i,e,t){return i<=e?0:i>=t?1:(i=(i-e)/(t-e),i*i*i*(i*(i*6-15)+10))}function Sm(i,e){return i+Math.floor(Math.random()*(e-i+1))}function ym(i,e){return i+Math.random()*(e-i)}function Em(i){return i*(.5-Math.random())}function bm(i){i!==void 0&&(Ou=i);let e=Ou+=1831565813;return e=Math.imul(e^e>>>15,e|1),e^=e+Math.imul(e^e>>>7,e|61),((e^e>>>14)>>>0)/4294967296}function Tm(i){return i*vs}function wm(i){return i*ca}function Am(i){return(i&i-1)===0&&i!==0}function Rm(i){return Math.pow(2,Math.ceil(Math.log(i)/Math.LN2))}function Cm(i){return Math.pow(2,Math.floor(Math.log(i)/Math.LN2))}function Pm(i,e,t,n,r){const s=Math.cos,a=Math.sin,o=s(t/2),l=a(t/2),c=s((e+n)/2),u=a((e+n)/2),h=s((e-n)/2),d=a((e-n)/2),m=s((n-e)/2),_=a((n-e)/2);switch(r){case"XYX":i.set(o*u,l*h,l*d,o*c);break;case"YZY":i.set(l*d,o*u,l*h,o*c);break;case"ZXZ":i.set(l*h,l*d,o*u,o*c);break;case"XZX":i.set(o*u,l*_,l*m,o*c);break;case"YXY":i.set(l*m,o*u,l*_,o*c);break;case"ZYZ":i.set(l*_,l*m,o*u,o*c);break;default:console.warn("THREE.MathUtils: .setQuaternionFromProperEuler() encountered an unknown order: "+r)}}function ni(i,e){switch(e.constructor){case Float32Array:return i;case Uint32Array:return i/4294967295;case Uint16Array:return i/65535;case Uint8Array:return i/255;case Int32Array:return Math.max(i/2147483647,-1);case Int16Array:return Math.max(i/32767,-1);case Int8Array:return Math.max(i/127,-1);default:throw new Error("Invalid component type.")}}function bt(i,e){switch(e.constructor){case Float32Array:return i;case Uint32Array:return Math.round(i*4294967295);case Uint16Array:return Math.round(i*65535);case Uint8Array:return Math.round(i*255);case Int32Array:return Math.round(i*2147483647);case Int16Array:return Math.round(i*32767);case Int8Array:return Math.round(i*127);default:throw new Error("Invalid component type.")}}const oo={DEG2RAD:vs,RAD2DEG:ca,generateUUID:Li,clamp:pn,euclideanModulo:Bc,mapLinear:mm,inverseLerp:gm,lerp:sa,damp:_m,pingpong:vm,smoothstep:xm,smootherstep:Mm,randInt:Sm,randFloat:ym,randFloatSpread:Em,seededRandom:bm,degToRad:Tm,radToDeg:wm,isPowerOfTwo:Am,ceilPowerOfTwo:Rm,floorPowerOfTwo:Cm,setQuaternionFromProperEuler:Pm,normalize:bt,denormalize:ni};class Xe{constructor(e=0,t=0){Xe.prototype.isVector2=!0,this.x=e,this.y=t}get width(){return this.x}set width(e){this.x=e}get height(){return this.y}set height(e){this.y=e}set(e,t){return this.x=e,this.y=t,this}setScalar(e){return this.x=e,this.y=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y)}copy(e){return this.x=e.x,this.y=e.y,this}add(e){return this.x+=e.x,this.y+=e.y,this}addScalar(e){return this.x+=e,this.y+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this}subScalar(e){return this.x-=e,this.y-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this}multiply(e){return this.x*=e.x,this.y*=e.y,this}multiplyScalar(e){return this.x*=e,this.y*=e,this}divide(e){return this.x/=e.x,this.y/=e.y,this}divideScalar(e){return this.multiplyScalar(1/e)}applyMatrix3(e){const t=this.x,n=this.y,r=e.elements;return this.x=r[0]*t+r[3]*n+r[6],this.y=r[1]*t+r[4]*n+r[7],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this}negate(){return this.x=-this.x,this.y=-this.y,this}dot(e){return this.x*e.x+this.y*e.y}cross(e){return this.x*e.y-this.y*e.x}lengthSq(){return this.x*this.x+this.y*this.y}length(){return Math.sqrt(this.x*this.x+this.y*this.y)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)}normalize(){return this.divideScalar(this.length()||1)}angle(){return Math.atan2(-this.y,-this.x)+Math.PI}angleTo(e){const t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;const n=this.dot(e)/t;return Math.acos(pn(n,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){const t=this.x-e.x,n=this.y-e.y;return t*t+n*n}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this}equals(e){return e.x===this.x&&e.y===this.y}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this}rotateAround(e,t){const n=Math.cos(t),r=Math.sin(t),s=this.x-e.x,a=this.y-e.y;return this.x=s*n-a*r+e.x,this.y=s*r+a*n+e.y,this}random(){return this.x=Math.random(),this.y=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y}}class rt{constructor(e,t,n,r,s,a,o,l,c){rt.prototype.isMatrix3=!0,this.elements=[1,0,0,0,1,0,0,0,1],e!==void 0&&this.set(e,t,n,r,s,a,o,l,c)}set(e,t,n,r,s,a,o,l,c){const u=this.elements;return u[0]=e,u[1]=r,u[2]=o,u[3]=t,u[4]=s,u[5]=l,u[6]=n,u[7]=a,u[8]=c,this}identity(){return this.set(1,0,0,0,1,0,0,0,1),this}copy(e){const t=this.elements,n=e.elements;return t[0]=n[0],t[1]=n[1],t[2]=n[2],t[3]=n[3],t[4]=n[4],t[5]=n[5],t[6]=n[6],t[7]=n[7],t[8]=n[8],this}extractBasis(e,t,n){return e.setFromMatrix3Column(this,0),t.setFromMatrix3Column(this,1),n.setFromMatrix3Column(this,2),this}setFromMatrix4(e){const t=e.elements;return this.set(t[0],t[4],t[8],t[1],t[5],t[9],t[2],t[6],t[10]),this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){const n=e.elements,r=t.elements,s=this.elements,a=n[0],o=n[3],l=n[6],c=n[1],u=n[4],h=n[7],d=n[2],m=n[5],_=n[8],v=r[0],p=r[3],f=r[6],E=r[1],y=r[4],T=r[7],z=r[2],C=r[5],D=r[8];return s[0]=a*v+o*E+l*z,s[3]=a*p+o*y+l*C,s[6]=a*f+o*T+l*D,s[1]=c*v+u*E+h*z,s[4]=c*p+u*y+h*C,s[7]=c*f+u*T+h*D,s[2]=d*v+m*E+_*z,s[5]=d*p+m*y+_*C,s[8]=d*f+m*T+_*D,this}multiplyScalar(e){const t=this.elements;return t[0]*=e,t[3]*=e,t[6]*=e,t[1]*=e,t[4]*=e,t[7]*=e,t[2]*=e,t[5]*=e,t[8]*=e,this}determinant(){const e=this.elements,t=e[0],n=e[1],r=e[2],s=e[3],a=e[4],o=e[5],l=e[6],c=e[7],u=e[8];return t*a*u-t*o*c-n*s*u+n*o*l+r*s*c-r*a*l}invert(){const e=this.elements,t=e[0],n=e[1],r=e[2],s=e[3],a=e[4],o=e[5],l=e[6],c=e[7],u=e[8],h=u*a-o*c,d=o*l-u*s,m=c*s-a*l,_=t*h+n*d+r*m;if(_===0)return this.set(0,0,0,0,0,0,0,0,0);const v=1/_;return e[0]=h*v,e[1]=(r*c-u*n)*v,e[2]=(o*n-r*a)*v,e[3]=d*v,e[4]=(u*t-r*l)*v,e[5]=(r*s-o*t)*v,e[6]=m*v,e[7]=(n*l-c*t)*v,e[8]=(a*t-n*s)*v,this}transpose(){let e;const t=this.elements;return e=t[1],t[1]=t[3],t[3]=e,e=t[2],t[2]=t[6],t[6]=e,e=t[5],t[5]=t[7],t[7]=e,this}getNormalMatrix(e){return this.setFromMatrix4(e).invert().transpose()}transposeIntoArray(e){const t=this.elements;return e[0]=t[0],e[1]=t[3],e[2]=t[6],e[3]=t[1],e[4]=t[4],e[5]=t[7],e[6]=t[2],e[7]=t[5],e[8]=t[8],this}setUvTransform(e,t,n,r,s,a,o){const l=Math.cos(s),c=Math.sin(s);return this.set(n*l,n*c,-n*(l*a+c*o)+a+e,-r*c,r*l,-r*(-c*a+l*o)+o+t,0,0,1),this}scale(e,t){return this.premultiply(nl.makeScale(e,t)),this}rotate(e){return this.premultiply(nl.makeRotation(-e)),this}translate(e,t){return this.premultiply(nl.makeTranslation(e,t)),this}makeTranslation(e,t){return e.isVector2?this.set(1,0,e.x,0,1,e.y,0,0,1):this.set(1,0,e,0,1,t,0,0,1),this}makeRotation(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,-n,0,n,t,0,0,0,1),this}makeScale(e,t){return this.set(e,0,0,0,t,0,0,0,1),this}equals(e){const t=this.elements,n=e.elements;for(let r=0;r<9;r++)if(t[r]!==n[r])return!1;return!0}fromArray(e,t=0){for(let n=0;n<9;n++)this.elements[n]=e[n+t];return this}toArray(e=[],t=0){const n=this.elements;return e[t]=n[0],e[t+1]=n[1],e[t+2]=n[2],e[t+3]=n[3],e[t+4]=n[4],e[t+5]=n[5],e[t+6]=n[6],e[t+7]=n[7],e[t+8]=n[8],e}clone(){return new this.constructor().fromArray(this.elements)}}const nl=new rt;function Xd(i){for(let e=i.length-1;e>=0;--e)if(i[e]>=65535)return!0;return!1}function _o(i){return document.createElementNS("http://www.w3.org/1999/xhtml",i)}function Lm(){const i=_o("canvas");return i.style.display="block",i}const Bu={};function xs(i){i in Bu||(Bu[i]=!0,console.warn(i))}function Dm(i,e,t){return new Promise(function(n,r){function s(){switch(i.clientWaitSync(e,i.SYNC_FLUSH_COMMANDS_BIT,0)){case i.WAIT_FAILED:r();break;case i.TIMEOUT_EXPIRED:setTimeout(s,t);break;default:n()}}setTimeout(s,t)})}const zu=new rt().set(.8224621,.177538,0,.0331941,.9668058,0,.0170827,.0723974,.9105199),ku=new rt().set(1.2249401,-.2249404,0,-.0420569,1.0420571,0,-.0196376,-.0786361,1.0982735),Ws={[rr]:{transfer:fo,primaries:po,luminanceCoefficients:[.2126,.7152,.0722],toReference:i=>i,fromReference:i=>i},[fi]:{transfer:Nt,primaries:po,luminanceCoefficients:[.2126,.7152,.0722],toReference:i=>i.convertSRGBToLinear(),fromReference:i=>i.convertLinearToSRGB()},[Ro]:{transfer:fo,primaries:mo,luminanceCoefficients:[.2289,.6917,.0793],toReference:i=>i.applyMatrix3(ku),fromReference:i=>i.applyMatrix3(zu)},[Oc]:{transfer:Nt,primaries:mo,luminanceCoefficients:[.2289,.6917,.0793],toReference:i=>i.convertSRGBToLinear().applyMatrix3(ku),fromReference:i=>i.applyMatrix3(zu).convertLinearToSRGB()}},Im=new Set([rr,Ro]),St={enabled:!0,_workingColorSpace:rr,get workingColorSpace(){return this._workingColorSpace},set workingColorSpace(i){if(!Im.has(i))throw new Error(`Unsupported working color space, "${i}".`);this._workingColorSpace=i},convert:function(i,e,t){if(this.enabled===!1||e===t||!e||!t)return i;const n=Ws[e].toReference,r=Ws[t].fromReference;return r(n(i))},fromWorkingColorSpace:function(i,e){return this.convert(i,this._workingColorSpace,e)},toWorkingColorSpace:function(i,e){return this.convert(i,e,this._workingColorSpace)},getPrimaries:function(i){return Ws[i].primaries},getTransfer:function(i){return i===Ki?fo:Ws[i].transfer},getLuminanceCoefficients:function(i,e=this._workingColorSpace){return i.fromArray(Ws[e].luminanceCoefficients)}};function Ms(i){return i<.04045?i*.0773993808:Math.pow(i*.9478672986+.0521327014,2.4)}function il(i){return i<.0031308?i*12.92:1.055*Math.pow(i,.41666)-.055}let qr;class Um{static getDataURL(e){if(/^data:/i.test(e.src)||typeof HTMLCanvasElement>"u")return e.src;let t;if(e instanceof HTMLCanvasElement)t=e;else{qr===void 0&&(qr=_o("canvas")),qr.width=e.width,qr.height=e.height;const n=qr.getContext("2d");e instanceof ImageData?n.putImageData(e,0,0):n.drawImage(e,0,0,e.width,e.height),t=qr}return t.width>2048||t.height>2048?(console.warn("THREE.ImageUtils.getDataURL: Image converted to jpg for performance reasons",e),t.toDataURL("image/jpeg",.6)):t.toDataURL("image/png")}static sRGBToLinear(e){if(typeof HTMLImageElement<"u"&&e instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&e instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&e instanceof ImageBitmap){const t=_o("canvas");t.width=e.width,t.height=e.height;const n=t.getContext("2d");n.drawImage(e,0,0,e.width,e.height);const r=n.getImageData(0,0,e.width,e.height),s=r.data;for(let a=0;a<s.length;a++)s[a]=Ms(s[a]/255)*255;return n.putImageData(r,0,0),t}else if(e.data){const t=e.data.slice(0);for(let n=0;n<t.length;n++)t instanceof Uint8Array||t instanceof Uint8ClampedArray?t[n]=Math.floor(Ms(t[n]/255)*255):t[n]=Ms(t[n]);return{data:t,width:e.width,height:e.height}}else return console.warn("THREE.ImageUtils.sRGBToLinear(): Unsupported image type. No color space conversion applied."),e}}let Nm=0;class Yd{constructor(e=null){this.isSource=!0,Object.defineProperty(this,"id",{value:Nm++}),this.uuid=Li(),this.data=e,this.dataReady=!0,this.version=0}set needsUpdate(e){e===!0&&this.version++}toJSON(e){const t=e===void 0||typeof e=="string";if(!t&&e.images[this.uuid]!==void 0)return e.images[this.uuid];const n={uuid:this.uuid,url:""},r=this.data;if(r!==null){let s;if(Array.isArray(r)){s=[];for(let a=0,o=r.length;a<o;a++)r[a].isDataTexture?s.push(rl(r[a].image)):s.push(rl(r[a]))}else s=rl(r);n.url=s}return t||(e.images[this.uuid]=n),n}}function rl(i){return typeof HTMLImageElement<"u"&&i instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&i instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&i instanceof ImageBitmap?Um.getDataURL(i):i.data?{data:Array.from(i.data),width:i.width,height:i.height,type:i.data.constructor.name}:(console.warn("THREE.Texture: Unable to serialize Texture."),{})}let Fm=0;class Tn extends Ds{constructor(e=Tn.DEFAULT_IMAGE,t=Tn.DEFAULT_MAPPING,n=yr,r=yr,s=ti,a=Er,o=ri,l=Ui,c=Tn.DEFAULT_ANISOTROPY,u=Ki){super(),this.isTexture=!0,Object.defineProperty(this,"id",{value:Fm++}),this.uuid=Li(),this.name="",this.source=new Yd(e),this.mipmaps=[],this.mapping=t,this.channel=0,this.wrapS=n,this.wrapT=r,this.magFilter=s,this.minFilter=a,this.anisotropy=c,this.format=o,this.internalFormat=null,this.type=l,this.offset=new Xe(0,0),this.repeat=new Xe(1,1),this.center=new Xe(0,0),this.rotation=0,this.matrixAutoUpdate=!0,this.matrix=new rt,this.generateMipmaps=!0,this.premultiplyAlpha=!1,this.flipY=!0,this.unpackAlignment=4,this.colorSpace=u,this.userData={},this.version=0,this.onUpdate=null,this.isRenderTargetTexture=!1,this.pmremVersion=0}get image(){return this.source.data}set image(e=null){this.source.data=e}updateMatrix(){this.matrix.setUvTransform(this.offset.x,this.offset.y,this.repeat.x,this.repeat.y,this.rotation,this.center.x,this.center.y)}clone(){return new this.constructor().copy(this)}copy(e){return this.name=e.name,this.source=e.source,this.mipmaps=e.mipmaps.slice(0),this.mapping=e.mapping,this.channel=e.channel,this.wrapS=e.wrapS,this.wrapT=e.wrapT,this.magFilter=e.magFilter,this.minFilter=e.minFilter,this.anisotropy=e.anisotropy,this.format=e.format,this.internalFormat=e.internalFormat,this.type=e.type,this.offset.copy(e.offset),this.repeat.copy(e.repeat),this.center.copy(e.center),this.rotation=e.rotation,this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrix.copy(e.matrix),this.generateMipmaps=e.generateMipmaps,this.premultiplyAlpha=e.premultiplyAlpha,this.flipY=e.flipY,this.unpackAlignment=e.unpackAlignment,this.colorSpace=e.colorSpace,this.userData=JSON.parse(JSON.stringify(e.userData)),this.needsUpdate=!0,this}toJSON(e){const t=e===void 0||typeof e=="string";if(!t&&e.textures[this.uuid]!==void 0)return e.textures[this.uuid];const n={metadata:{version:4.6,type:"Texture",generator:"Texture.toJSON"},uuid:this.uuid,name:this.name,image:this.source.toJSON(e).uuid,mapping:this.mapping,channel:this.channel,repeat:[this.repeat.x,this.repeat.y],offset:[this.offset.x,this.offset.y],center:[this.center.x,this.center.y],rotation:this.rotation,wrap:[this.wrapS,this.wrapT],format:this.format,internalFormat:this.internalFormat,type:this.type,colorSpace:this.colorSpace,minFilter:this.minFilter,magFilter:this.magFilter,anisotropy:this.anisotropy,flipY:this.flipY,generateMipmaps:this.generateMipmaps,premultiplyAlpha:this.premultiplyAlpha,unpackAlignment:this.unpackAlignment};return Object.keys(this.userData).length>0&&(n.userData=this.userData),t||(e.textures[this.uuid]=n),n}dispose(){this.dispatchEvent({type:"dispose"})}transformUv(e){if(this.mapping!==Dd)return e;if(e.applyMatrix3(this.matrix),e.x<0||e.x>1)switch(this.wrapS){case Gl:e.x=e.x-Math.floor(e.x);break;case yr:e.x=e.x<0?0:1;break;case Wl:Math.abs(Math.floor(e.x)%2)===1?e.x=Math.ceil(e.x)-e.x:e.x=e.x-Math.floor(e.x);break}if(e.y<0||e.y>1)switch(this.wrapT){case Gl:e.y=e.y-Math.floor(e.y);break;case yr:e.y=e.y<0?0:1;break;case Wl:Math.abs(Math.floor(e.y)%2)===1?e.y=Math.ceil(e.y)-e.y:e.y=e.y-Math.floor(e.y);break}return this.flipY&&(e.y=1-e.y),e}set needsUpdate(e){e===!0&&(this.version++,this.source.needsUpdate=!0)}set needsPMREMUpdate(e){e===!0&&this.pmremVersion++}}Tn.DEFAULT_IMAGE=null;Tn.DEFAULT_MAPPING=Dd;Tn.DEFAULT_ANISOTROPY=1;class jt{constructor(e=0,t=0,n=0,r=1){jt.prototype.isVector4=!0,this.x=e,this.y=t,this.z=n,this.w=r}get width(){return this.z}set width(e){this.z=e}get height(){return this.w}set height(e){this.w=e}set(e,t,n,r){return this.x=e,this.y=t,this.z=n,this.w=r,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this.w=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setW(e){return this.w=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;case 3:this.w=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;case 3:return this.w;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z,this.w)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this.w=e.w!==void 0?e.w:1,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this.w+=e.w,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this.w+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this.w=e.w+t.w,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this.w+=e.w*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this.w-=e.w,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this.w-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this.w=e.w-t.w,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this.w*=e.w,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this.w*=e,this}applyMatrix4(e){const t=this.x,n=this.y,r=this.z,s=this.w,a=e.elements;return this.x=a[0]*t+a[4]*n+a[8]*r+a[12]*s,this.y=a[1]*t+a[5]*n+a[9]*r+a[13]*s,this.z=a[2]*t+a[6]*n+a[10]*r+a[14]*s,this.w=a[3]*t+a[7]*n+a[11]*r+a[15]*s,this}divideScalar(e){return this.multiplyScalar(1/e)}setAxisAngleFromQuaternion(e){this.w=2*Math.acos(e.w);const t=Math.sqrt(1-e.w*e.w);return t<1e-4?(this.x=1,this.y=0,this.z=0):(this.x=e.x/t,this.y=e.y/t,this.z=e.z/t),this}setAxisAngleFromRotationMatrix(e){let t,n,r,s;const l=e.elements,c=l[0],u=l[4],h=l[8],d=l[1],m=l[5],_=l[9],v=l[2],p=l[6],f=l[10];if(Math.abs(u-d)<.01&&Math.abs(h-v)<.01&&Math.abs(_-p)<.01){if(Math.abs(u+d)<.1&&Math.abs(h+v)<.1&&Math.abs(_+p)<.1&&Math.abs(c+m+f-3)<.1)return this.set(1,0,0,0),this;t=Math.PI;const y=(c+1)/2,T=(m+1)/2,z=(f+1)/2,C=(u+d)/4,D=(h+v)/4,B=(_+p)/4;return y>T&&y>z?y<.01?(n=0,r=.707106781,s=.707106781):(n=Math.sqrt(y),r=C/n,s=D/n):T>z?T<.01?(n=.707106781,r=0,s=.707106781):(r=Math.sqrt(T),n=C/r,s=B/r):z<.01?(n=.707106781,r=.707106781,s=0):(s=Math.sqrt(z),n=D/s,r=B/s),this.set(n,r,s,t),this}let E=Math.sqrt((p-_)*(p-_)+(h-v)*(h-v)+(d-u)*(d-u));return Math.abs(E)<.001&&(E=1),this.x=(p-_)/E,this.y=(h-v)/E,this.z=(d-u)/E,this.w=Math.acos((c+m+f-1)/2),this}setFromMatrixPosition(e){const t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this.w=t[15],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this.w=Math.min(this.w,e.w),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this.w=Math.max(this.w,e.w),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this.z=Math.max(e.z,Math.min(t.z,this.z)),this.w=Math.max(e.w,Math.min(t.w,this.w)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this.z=Math.max(e,Math.min(t,this.z)),this.w=Math.max(e,Math.min(t,this.w)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this.w=Math.floor(this.w),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this.w=Math.ceil(this.w),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this.w=Math.round(this.w),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this.w=Math.trunc(this.w),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this.w=-this.w,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z+this.w*e.w}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)+Math.abs(this.w)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this.w+=(e.w-this.w)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this.z=e.z+(t.z-e.z)*n,this.w=e.w+(t.w-e.w)*n,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z&&e.w===this.w}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this.w=e[t+3],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e[t+3]=this.w,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this.w=e.getW(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this.w=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z,yield this.w}}class Om extends Ds{constructor(e=1,t=1,n={}){super(),this.isRenderTarget=!0,this.width=e,this.height=t,this.depth=1,this.scissor=new jt(0,0,e,t),this.scissorTest=!1,this.viewport=new jt(0,0,e,t);const r={width:e,height:t,depth:1};n=Object.assign({generateMipmaps:!1,internalFormat:null,minFilter:ti,depthBuffer:!0,stencilBuffer:!1,resolveDepthBuffer:!0,resolveStencilBuffer:!0,depthTexture:null,samples:0,count:1},n);const s=new Tn(r,n.mapping,n.wrapS,n.wrapT,n.magFilter,n.minFilter,n.format,n.type,n.anisotropy,n.colorSpace);s.flipY=!1,s.generateMipmaps=n.generateMipmaps,s.internalFormat=n.internalFormat,this.textures=[];const a=n.count;for(let o=0;o<a;o++)this.textures[o]=s.clone(),this.textures[o].isRenderTargetTexture=!0;this.depthBuffer=n.depthBuffer,this.stencilBuffer=n.stencilBuffer,this.resolveDepthBuffer=n.resolveDepthBuffer,this.resolveStencilBuffer=n.resolveStencilBuffer,this.depthTexture=n.depthTexture,this.samples=n.samples}get texture(){return this.textures[0]}set texture(e){this.textures[0]=e}setSize(e,t,n=1){if(this.width!==e||this.height!==t||this.depth!==n){this.width=e,this.height=t,this.depth=n;for(let r=0,s=this.textures.length;r<s;r++)this.textures[r].image.width=e,this.textures[r].image.height=t,this.textures[r].image.depth=n;this.dispose()}this.viewport.set(0,0,e,t),this.scissor.set(0,0,e,t)}clone(){return new this.constructor().copy(this)}copy(e){this.width=e.width,this.height=e.height,this.depth=e.depth,this.scissor.copy(e.scissor),this.scissorTest=e.scissorTest,this.viewport.copy(e.viewport),this.textures.length=0;for(let n=0,r=e.textures.length;n<r;n++)this.textures[n]=e.textures[n].clone(),this.textures[n].isRenderTargetTexture=!0;const t=Object.assign({},e.texture.image);return this.texture.source=new Yd(t),this.depthBuffer=e.depthBuffer,this.stencilBuffer=e.stencilBuffer,this.resolveDepthBuffer=e.resolveDepthBuffer,this.resolveStencilBuffer=e.resolveStencilBuffer,e.depthTexture!==null&&(this.depthTexture=e.depthTexture.clone()),this.samples=e.samples,this}dispose(){this.dispatchEvent({type:"dispose"})}}class Ar extends Om{constructor(e=1,t=1,n={}){super(e,t,n),this.isWebGLRenderTarget=!0}}class qd extends Tn{constructor(e=null,t=1,n=1,r=1){super(null),this.isDataArrayTexture=!0,this.image={data:e,width:t,height:n,depth:r},this.magFilter=Wn,this.minFilter=Wn,this.wrapR=yr,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1,this.layerUpdates=new Set}addLayerUpdate(e){this.layerUpdates.add(e)}clearLayerUpdates(){this.layerUpdates.clear()}}class Bm extends Tn{constructor(e=null,t=1,n=1,r=1){super(null),this.isData3DTexture=!0,this.image={data:e,width:t,height:n,depth:r},this.magFilter=Wn,this.minFilter=Wn,this.wrapR=yr,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}}class Rr{constructor(e=0,t=0,n=0,r=1){this.isQuaternion=!0,this._x=e,this._y=t,this._z=n,this._w=r}static slerpFlat(e,t,n,r,s,a,o){let l=n[r+0],c=n[r+1],u=n[r+2],h=n[r+3];const d=s[a+0],m=s[a+1],_=s[a+2],v=s[a+3];if(o===0){e[t+0]=l,e[t+1]=c,e[t+2]=u,e[t+3]=h;return}if(o===1){e[t+0]=d,e[t+1]=m,e[t+2]=_,e[t+3]=v;return}if(h!==v||l!==d||c!==m||u!==_){let p=1-o;const f=l*d+c*m+u*_+h*v,E=f>=0?1:-1,y=1-f*f;if(y>Number.EPSILON){const z=Math.sqrt(y),C=Math.atan2(z,f*E);p=Math.sin(p*C)/z,o=Math.sin(o*C)/z}const T=o*E;if(l=l*p+d*T,c=c*p+m*T,u=u*p+_*T,h=h*p+v*T,p===1-o){const z=1/Math.sqrt(l*l+c*c+u*u+h*h);l*=z,c*=z,u*=z,h*=z}}e[t]=l,e[t+1]=c,e[t+2]=u,e[t+3]=h}static multiplyQuaternionsFlat(e,t,n,r,s,a){const o=n[r],l=n[r+1],c=n[r+2],u=n[r+3],h=s[a],d=s[a+1],m=s[a+2],_=s[a+3];return e[t]=o*_+u*h+l*m-c*d,e[t+1]=l*_+u*d+c*h-o*m,e[t+2]=c*_+u*m+o*d-l*h,e[t+3]=u*_-o*h-l*d-c*m,e}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get w(){return this._w}set w(e){this._w=e,this._onChangeCallback()}set(e,t,n,r){return this._x=e,this._y=t,this._z=n,this._w=r,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._w)}copy(e){return this._x=e.x,this._y=e.y,this._z=e.z,this._w=e.w,this._onChangeCallback(),this}setFromEuler(e,t=!0){const n=e._x,r=e._y,s=e._z,a=e._order,o=Math.cos,l=Math.sin,c=o(n/2),u=o(r/2),h=o(s/2),d=l(n/2),m=l(r/2),_=l(s/2);switch(a){case"XYZ":this._x=d*u*h+c*m*_,this._y=c*m*h-d*u*_,this._z=c*u*_+d*m*h,this._w=c*u*h-d*m*_;break;case"YXZ":this._x=d*u*h+c*m*_,this._y=c*m*h-d*u*_,this._z=c*u*_-d*m*h,this._w=c*u*h+d*m*_;break;case"ZXY":this._x=d*u*h-c*m*_,this._y=c*m*h+d*u*_,this._z=c*u*_+d*m*h,this._w=c*u*h-d*m*_;break;case"ZYX":this._x=d*u*h-c*m*_,this._y=c*m*h+d*u*_,this._z=c*u*_-d*m*h,this._w=c*u*h+d*m*_;break;case"YZX":this._x=d*u*h+c*m*_,this._y=c*m*h+d*u*_,this._z=c*u*_-d*m*h,this._w=c*u*h-d*m*_;break;case"XZY":this._x=d*u*h-c*m*_,this._y=c*m*h-d*u*_,this._z=c*u*_+d*m*h,this._w=c*u*h+d*m*_;break;default:console.warn("THREE.Quaternion: .setFromEuler() encountered an unknown order: "+a)}return t===!0&&this._onChangeCallback(),this}setFromAxisAngle(e,t){const n=t/2,r=Math.sin(n);return this._x=e.x*r,this._y=e.y*r,this._z=e.z*r,this._w=Math.cos(n),this._onChangeCallback(),this}setFromRotationMatrix(e){const t=e.elements,n=t[0],r=t[4],s=t[8],a=t[1],o=t[5],l=t[9],c=t[2],u=t[6],h=t[10],d=n+o+h;if(d>0){const m=.5/Math.sqrt(d+1);this._w=.25/m,this._x=(u-l)*m,this._y=(s-c)*m,this._z=(a-r)*m}else if(n>o&&n>h){const m=2*Math.sqrt(1+n-o-h);this._w=(u-l)/m,this._x=.25*m,this._y=(r+a)/m,this._z=(s+c)/m}else if(o>h){const m=2*Math.sqrt(1+o-n-h);this._w=(s-c)/m,this._x=(r+a)/m,this._y=.25*m,this._z=(l+u)/m}else{const m=2*Math.sqrt(1+h-n-o);this._w=(a-r)/m,this._x=(s+c)/m,this._y=(l+u)/m,this._z=.25*m}return this._onChangeCallback(),this}setFromUnitVectors(e,t){let n=e.dot(t)+1;return n<Number.EPSILON?(n=0,Math.abs(e.x)>Math.abs(e.z)?(this._x=-e.y,this._y=e.x,this._z=0,this._w=n):(this._x=0,this._y=-e.z,this._z=e.y,this._w=n)):(this._x=e.y*t.z-e.z*t.y,this._y=e.z*t.x-e.x*t.z,this._z=e.x*t.y-e.y*t.x,this._w=n),this.normalize()}angleTo(e){return 2*Math.acos(Math.abs(pn(this.dot(e),-1,1)))}rotateTowards(e,t){const n=this.angleTo(e);if(n===0)return this;const r=Math.min(1,t/n);return this.slerp(e,r),this}identity(){return this.set(0,0,0,1)}invert(){return this.conjugate()}conjugate(){return this._x*=-1,this._y*=-1,this._z*=-1,this._onChangeCallback(),this}dot(e){return this._x*e._x+this._y*e._y+this._z*e._z+this._w*e._w}lengthSq(){return this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w}length(){return Math.sqrt(this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w)}normalize(){let e=this.length();return e===0?(this._x=0,this._y=0,this._z=0,this._w=1):(e=1/e,this._x=this._x*e,this._y=this._y*e,this._z=this._z*e,this._w=this._w*e),this._onChangeCallback(),this}multiply(e){return this.multiplyQuaternions(this,e)}premultiply(e){return this.multiplyQuaternions(e,this)}multiplyQuaternions(e,t){const n=e._x,r=e._y,s=e._z,a=e._w,o=t._x,l=t._y,c=t._z,u=t._w;return this._x=n*u+a*o+r*c-s*l,this._y=r*u+a*l+s*o-n*c,this._z=s*u+a*c+n*l-r*o,this._w=a*u-n*o-r*l-s*c,this._onChangeCallback(),this}slerp(e,t){if(t===0)return this;if(t===1)return this.copy(e);const n=this._x,r=this._y,s=this._z,a=this._w;let o=a*e._w+n*e._x+r*e._y+s*e._z;if(o<0?(this._w=-e._w,this._x=-e._x,this._y=-e._y,this._z=-e._z,o=-o):this.copy(e),o>=1)return this._w=a,this._x=n,this._y=r,this._z=s,this;const l=1-o*o;if(l<=Number.EPSILON){const m=1-t;return this._w=m*a+t*this._w,this._x=m*n+t*this._x,this._y=m*r+t*this._y,this._z=m*s+t*this._z,this.normalize(),this}const c=Math.sqrt(l),u=Math.atan2(c,o),h=Math.sin((1-t)*u)/c,d=Math.sin(t*u)/c;return this._w=a*h+this._w*d,this._x=n*h+this._x*d,this._y=r*h+this._y*d,this._z=s*h+this._z*d,this._onChangeCallback(),this}slerpQuaternions(e,t,n){return this.copy(e).slerp(t,n)}random(){const e=2*Math.PI*Math.random(),t=2*Math.PI*Math.random(),n=Math.random(),r=Math.sqrt(1-n),s=Math.sqrt(n);return this.set(r*Math.sin(e),r*Math.cos(e),s*Math.sin(t),s*Math.cos(t))}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._w===this._w}fromArray(e,t=0){return this._x=e[t],this._y=e[t+1],this._z=e[t+2],this._w=e[t+3],this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._w,e}fromBufferAttribute(e,t){return this._x=e.getX(t),this._y=e.getY(t),this._z=e.getZ(t),this._w=e.getW(t),this._onChangeCallback(),this}toJSON(){return this.toArray()}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._w}}class V{constructor(e=0,t=0,n=0){V.prototype.isVector3=!0,this.x=e,this.y=t,this.z=n}set(e,t,n){return n===void 0&&(n=this.z),this.x=e,this.y=t,this.z=n,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this}multiplyVectors(e,t){return this.x=e.x*t.x,this.y=e.y*t.y,this.z=e.z*t.z,this}applyEuler(e){return this.applyQuaternion(Hu.setFromEuler(e))}applyAxisAngle(e,t){return this.applyQuaternion(Hu.setFromAxisAngle(e,t))}applyMatrix3(e){const t=this.x,n=this.y,r=this.z,s=e.elements;return this.x=s[0]*t+s[3]*n+s[6]*r,this.y=s[1]*t+s[4]*n+s[7]*r,this.z=s[2]*t+s[5]*n+s[8]*r,this}applyNormalMatrix(e){return this.applyMatrix3(e).normalize()}applyMatrix4(e){const t=this.x,n=this.y,r=this.z,s=e.elements,a=1/(s[3]*t+s[7]*n+s[11]*r+s[15]);return this.x=(s[0]*t+s[4]*n+s[8]*r+s[12])*a,this.y=(s[1]*t+s[5]*n+s[9]*r+s[13])*a,this.z=(s[2]*t+s[6]*n+s[10]*r+s[14])*a,this}applyQuaternion(e){const t=this.x,n=this.y,r=this.z,s=e.x,a=e.y,o=e.z,l=e.w,c=2*(a*r-o*n),u=2*(o*t-s*r),h=2*(s*n-a*t);return this.x=t+l*c+a*h-o*u,this.y=n+l*u+o*c-s*h,this.z=r+l*h+s*u-a*c,this}project(e){return this.applyMatrix4(e.matrixWorldInverse).applyMatrix4(e.projectionMatrix)}unproject(e){return this.applyMatrix4(e.projectionMatrixInverse).applyMatrix4(e.matrixWorld)}transformDirection(e){const t=this.x,n=this.y,r=this.z,s=e.elements;return this.x=s[0]*t+s[4]*n+s[8]*r,this.y=s[1]*t+s[5]*n+s[9]*r,this.z=s[2]*t+s[6]*n+s[10]*r,this.normalize()}divide(e){return this.x/=e.x,this.y/=e.y,this.z/=e.z,this}divideScalar(e){return this.multiplyScalar(1/e)}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this.z=Math.max(e.z,Math.min(t.z,this.z)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this.z=Math.max(e,Math.min(t,this.z)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this.z=e.z+(t.z-e.z)*n,this}cross(e){return this.crossVectors(this,e)}crossVectors(e,t){const n=e.x,r=e.y,s=e.z,a=t.x,o=t.y,l=t.z;return this.x=r*l-s*o,this.y=s*a-n*l,this.z=n*o-r*a,this}projectOnVector(e){const t=e.lengthSq();if(t===0)return this.set(0,0,0);const n=e.dot(this)/t;return this.copy(e).multiplyScalar(n)}projectOnPlane(e){return sl.copy(this).projectOnVector(e),this.sub(sl)}reflect(e){return this.sub(sl.copy(e).multiplyScalar(2*this.dot(e)))}angleTo(e){const t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;const n=this.dot(e)/t;return Math.acos(pn(n,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){const t=this.x-e.x,n=this.y-e.y,r=this.z-e.z;return t*t+n*n+r*r}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)+Math.abs(this.z-e.z)}setFromSpherical(e){return this.setFromSphericalCoords(e.radius,e.phi,e.theta)}setFromSphericalCoords(e,t,n){const r=Math.sin(t)*e;return this.x=r*Math.sin(n),this.y=Math.cos(t)*e,this.z=r*Math.cos(n),this}setFromCylindrical(e){return this.setFromCylindricalCoords(e.radius,e.theta,e.y)}setFromCylindricalCoords(e,t,n){return this.x=e*Math.sin(t),this.y=n,this.z=e*Math.cos(t),this}setFromMatrixPosition(e){const t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this}setFromMatrixScale(e){const t=this.setFromMatrixColumn(e,0).length(),n=this.setFromMatrixColumn(e,1).length(),r=this.setFromMatrixColumn(e,2).length();return this.x=t,this.y=n,this.z=r,this}setFromMatrixColumn(e,t){return this.fromArray(e.elements,t*4)}setFromMatrix3Column(e,t){return this.fromArray(e.elements,t*3)}setFromEuler(e){return this.x=e._x,this.y=e._y,this.z=e._z,this}setFromColor(e){return this.x=e.r,this.y=e.g,this.z=e.b,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this}randomDirection(){const e=Math.random()*Math.PI*2,t=Math.random()*2-1,n=Math.sqrt(1-t*t);return this.x=n*Math.cos(e),this.y=t,this.z=n*Math.sin(e),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z}}const sl=new V,Hu=new Rr;class da{constructor(e=new V(1/0,1/0,1/0),t=new V(-1/0,-1/0,-1/0)){this.isBox3=!0,this.min=e,this.max=t}set(e,t){return this.min.copy(e),this.max.copy(t),this}setFromArray(e){this.makeEmpty();for(let t=0,n=e.length;t<n;t+=3)this.expandByPoint(Kn.fromArray(e,t));return this}setFromBufferAttribute(e){this.makeEmpty();for(let t=0,n=e.count;t<n;t++)this.expandByPoint(Kn.fromBufferAttribute(e,t));return this}setFromPoints(e){this.makeEmpty();for(let t=0,n=e.length;t<n;t++)this.expandByPoint(e[t]);return this}setFromCenterAndSize(e,t){const n=Kn.copy(t).multiplyScalar(.5);return this.min.copy(e).sub(n),this.max.copy(e).add(n),this}setFromObject(e,t=!1){return this.makeEmpty(),this.expandByObject(e,t)}clone(){return new this.constructor().copy(this)}copy(e){return this.min.copy(e.min),this.max.copy(e.max),this}makeEmpty(){return this.min.x=this.min.y=this.min.z=1/0,this.max.x=this.max.y=this.max.z=-1/0,this}isEmpty(){return this.max.x<this.min.x||this.max.y<this.min.y||this.max.z<this.min.z}getCenter(e){return this.isEmpty()?e.set(0,0,0):e.addVectors(this.min,this.max).multiplyScalar(.5)}getSize(e){return this.isEmpty()?e.set(0,0,0):e.subVectors(this.max,this.min)}expandByPoint(e){return this.min.min(e),this.max.max(e),this}expandByVector(e){return this.min.sub(e),this.max.add(e),this}expandByScalar(e){return this.min.addScalar(-e),this.max.addScalar(e),this}expandByObject(e,t=!1){e.updateWorldMatrix(!1,!1);const n=e.geometry;if(n!==void 0){const s=n.getAttribute("position");if(t===!0&&s!==void 0&&e.isInstancedMesh!==!0)for(let a=0,o=s.count;a<o;a++)e.isMesh===!0?e.getVertexPosition(a,Kn):Kn.fromBufferAttribute(s,a),Kn.applyMatrix4(e.matrixWorld),this.expandByPoint(Kn);else e.boundingBox!==void 0?(e.boundingBox===null&&e.computeBoundingBox(),ya.copy(e.boundingBox)):(n.boundingBox===null&&n.computeBoundingBox(),ya.copy(n.boundingBox)),ya.applyMatrix4(e.matrixWorld),this.union(ya)}const r=e.children;for(let s=0,a=r.length;s<a;s++)this.expandByObject(r[s],t);return this}containsPoint(e){return e.x>=this.min.x&&e.x<=this.max.x&&e.y>=this.min.y&&e.y<=this.max.y&&e.z>=this.min.z&&e.z<=this.max.z}containsBox(e){return this.min.x<=e.min.x&&e.max.x<=this.max.x&&this.min.y<=e.min.y&&e.max.y<=this.max.y&&this.min.z<=e.min.z&&e.max.z<=this.max.z}getParameter(e,t){return t.set((e.x-this.min.x)/(this.max.x-this.min.x),(e.y-this.min.y)/(this.max.y-this.min.y),(e.z-this.min.z)/(this.max.z-this.min.z))}intersectsBox(e){return e.max.x>=this.min.x&&e.min.x<=this.max.x&&e.max.y>=this.min.y&&e.min.y<=this.max.y&&e.max.z>=this.min.z&&e.min.z<=this.max.z}intersectsSphere(e){return this.clampPoint(e.center,Kn),Kn.distanceToSquared(e.center)<=e.radius*e.radius}intersectsPlane(e){let t,n;return e.normal.x>0?(t=e.normal.x*this.min.x,n=e.normal.x*this.max.x):(t=e.normal.x*this.max.x,n=e.normal.x*this.min.x),e.normal.y>0?(t+=e.normal.y*this.min.y,n+=e.normal.y*this.max.y):(t+=e.normal.y*this.max.y,n+=e.normal.y*this.min.y),e.normal.z>0?(t+=e.normal.z*this.min.z,n+=e.normal.z*this.max.z):(t+=e.normal.z*this.max.z,n+=e.normal.z*this.min.z),t<=-e.constant&&n>=-e.constant}intersectsTriangle(e){if(this.isEmpty())return!1;this.getCenter(Xs),Ea.subVectors(this.max,Xs),$r.subVectors(e.a,Xs),jr.subVectors(e.b,Xs),Kr.subVectors(e.c,Xs),Hi.subVectors(jr,$r),Vi.subVectors(Kr,jr),ur.subVectors($r,Kr);let t=[0,-Hi.z,Hi.y,0,-Vi.z,Vi.y,0,-ur.z,ur.y,Hi.z,0,-Hi.x,Vi.z,0,-Vi.x,ur.z,0,-ur.x,-Hi.y,Hi.x,0,-Vi.y,Vi.x,0,-ur.y,ur.x,0];return!al(t,$r,jr,Kr,Ea)||(t=[1,0,0,0,1,0,0,0,1],!al(t,$r,jr,Kr,Ea))?!1:(ba.crossVectors(Hi,Vi),t=[ba.x,ba.y,ba.z],al(t,$r,jr,Kr,Ea))}clampPoint(e,t){return t.copy(e).clamp(this.min,this.max)}distanceToPoint(e){return this.clampPoint(e,Kn).distanceTo(e)}getBoundingSphere(e){return this.isEmpty()?e.makeEmpty():(this.getCenter(e.center),e.radius=this.getSize(Kn).length()*.5),e}intersect(e){return this.min.max(e.min),this.max.min(e.max),this.isEmpty()&&this.makeEmpty(),this}union(e){return this.min.min(e.min),this.max.max(e.max),this}applyMatrix4(e){return this.isEmpty()?this:(yi[0].set(this.min.x,this.min.y,this.min.z).applyMatrix4(e),yi[1].set(this.min.x,this.min.y,this.max.z).applyMatrix4(e),yi[2].set(this.min.x,this.max.y,this.min.z).applyMatrix4(e),yi[3].set(this.min.x,this.max.y,this.max.z).applyMatrix4(e),yi[4].set(this.max.x,this.min.y,this.min.z).applyMatrix4(e),yi[5].set(this.max.x,this.min.y,this.max.z).applyMatrix4(e),yi[6].set(this.max.x,this.max.y,this.min.z).applyMatrix4(e),yi[7].set(this.max.x,this.max.y,this.max.z).applyMatrix4(e),this.setFromPoints(yi),this)}translate(e){return this.min.add(e),this.max.add(e),this}equals(e){return e.min.equals(this.min)&&e.max.equals(this.max)}}const yi=[new V,new V,new V,new V,new V,new V,new V,new V],Kn=new V,ya=new da,$r=new V,jr=new V,Kr=new V,Hi=new V,Vi=new V,ur=new V,Xs=new V,Ea=new V,ba=new V,hr=new V;function al(i,e,t,n,r){for(let s=0,a=i.length-3;s<=a;s+=3){hr.fromArray(i,s);const o=r.x*Math.abs(hr.x)+r.y*Math.abs(hr.y)+r.z*Math.abs(hr.z),l=e.dot(hr),c=t.dot(hr),u=n.dot(hr);if(Math.max(-Math.max(l,c,u),Math.min(l,c,u))>o)return!1}return!0}const zm=new da,Ys=new V,ol=new V;class Co{constructor(e=new V,t=-1){this.isSphere=!0,this.center=e,this.radius=t}set(e,t){return this.center.copy(e),this.radius=t,this}setFromPoints(e,t){const n=this.center;t!==void 0?n.copy(t):zm.setFromPoints(e).getCenter(n);let r=0;for(let s=0,a=e.length;s<a;s++)r=Math.max(r,n.distanceToSquared(e[s]));return this.radius=Math.sqrt(r),this}copy(e){return this.center.copy(e.center),this.radius=e.radius,this}isEmpty(){return this.radius<0}makeEmpty(){return this.center.set(0,0,0),this.radius=-1,this}containsPoint(e){return e.distanceToSquared(this.center)<=this.radius*this.radius}distanceToPoint(e){return e.distanceTo(this.center)-this.radius}intersectsSphere(e){const t=this.radius+e.radius;return e.center.distanceToSquared(this.center)<=t*t}intersectsBox(e){return e.intersectsSphere(this)}intersectsPlane(e){return Math.abs(e.distanceToPoint(this.center))<=this.radius}clampPoint(e,t){const n=this.center.distanceToSquared(e);return t.copy(e),n>this.radius*this.radius&&(t.sub(this.center).normalize(),t.multiplyScalar(this.radius).add(this.center)),t}getBoundingBox(e){return this.isEmpty()?(e.makeEmpty(),e):(e.set(this.center,this.center),e.expandByScalar(this.radius),e)}applyMatrix4(e){return this.center.applyMatrix4(e),this.radius=this.radius*e.getMaxScaleOnAxis(),this}translate(e){return this.center.add(e),this}expandByPoint(e){if(this.isEmpty())return this.center.copy(e),this.radius=0,this;Ys.subVectors(e,this.center);const t=Ys.lengthSq();if(t>this.radius*this.radius){const n=Math.sqrt(t),r=(n-this.radius)*.5;this.center.addScaledVector(Ys,r/n),this.radius+=r}return this}union(e){return e.isEmpty()?this:this.isEmpty()?(this.copy(e),this):(this.center.equals(e.center)===!0?this.radius=Math.max(this.radius,e.radius):(ol.subVectors(e.center,this.center).setLength(e.radius),this.expandByPoint(Ys.copy(e.center).add(ol)),this.expandByPoint(Ys.copy(e.center).sub(ol))),this)}equals(e){return e.center.equals(this.center)&&e.radius===this.radius}clone(){return new this.constructor().copy(this)}}const Ei=new V,ll=new V,Ta=new V,Gi=new V,cl=new V,wa=new V,ul=new V;class Po{constructor(e=new V,t=new V(0,0,-1)){this.origin=e,this.direction=t}set(e,t){return this.origin.copy(e),this.direction.copy(t),this}copy(e){return this.origin.copy(e.origin),this.direction.copy(e.direction),this}at(e,t){return t.copy(this.origin).addScaledVector(this.direction,e)}lookAt(e){return this.direction.copy(e).sub(this.origin).normalize(),this}recast(e){return this.origin.copy(this.at(e,Ei)),this}closestPointToPoint(e,t){t.subVectors(e,this.origin);const n=t.dot(this.direction);return n<0?t.copy(this.origin):t.copy(this.origin).addScaledVector(this.direction,n)}distanceToPoint(e){return Math.sqrt(this.distanceSqToPoint(e))}distanceSqToPoint(e){const t=Ei.subVectors(e,this.origin).dot(this.direction);return t<0?this.origin.distanceToSquared(e):(Ei.copy(this.origin).addScaledVector(this.direction,t),Ei.distanceToSquared(e))}distanceSqToSegment(e,t,n,r){ll.copy(e).add(t).multiplyScalar(.5),Ta.copy(t).sub(e).normalize(),Gi.copy(this.origin).sub(ll);const s=e.distanceTo(t)*.5,a=-this.direction.dot(Ta),o=Gi.dot(this.direction),l=-Gi.dot(Ta),c=Gi.lengthSq(),u=Math.abs(1-a*a);let h,d,m,_;if(u>0)if(h=a*l-o,d=a*o-l,_=s*u,h>=0)if(d>=-_)if(d<=_){const v=1/u;h*=v,d*=v,m=h*(h+a*d+2*o)+d*(a*h+d+2*l)+c}else d=s,h=Math.max(0,-(a*d+o)),m=-h*h+d*(d+2*l)+c;else d=-s,h=Math.max(0,-(a*d+o)),m=-h*h+d*(d+2*l)+c;else d<=-_?(h=Math.max(0,-(-a*s+o)),d=h>0?-s:Math.min(Math.max(-s,-l),s),m=-h*h+d*(d+2*l)+c):d<=_?(h=0,d=Math.min(Math.max(-s,-l),s),m=d*(d+2*l)+c):(h=Math.max(0,-(a*s+o)),d=h>0?s:Math.min(Math.max(-s,-l),s),m=-h*h+d*(d+2*l)+c);else d=a>0?-s:s,h=Math.max(0,-(a*d+o)),m=-h*h+d*(d+2*l)+c;return n&&n.copy(this.origin).addScaledVector(this.direction,h),r&&r.copy(ll).addScaledVector(Ta,d),m}intersectSphere(e,t){Ei.subVectors(e.center,this.origin);const n=Ei.dot(this.direction),r=Ei.dot(Ei)-n*n,s=e.radius*e.radius;if(r>s)return null;const a=Math.sqrt(s-r),o=n-a,l=n+a;return l<0?null:o<0?this.at(l,t):this.at(o,t)}intersectsSphere(e){return this.distanceSqToPoint(e.center)<=e.radius*e.radius}distanceToPlane(e){const t=e.normal.dot(this.direction);if(t===0)return e.distanceToPoint(this.origin)===0?0:null;const n=-(this.origin.dot(e.normal)+e.constant)/t;return n>=0?n:null}intersectPlane(e,t){const n=this.distanceToPlane(e);return n===null?null:this.at(n,t)}intersectsPlane(e){const t=e.distanceToPoint(this.origin);return t===0||e.normal.dot(this.direction)*t<0}intersectBox(e,t){let n,r,s,a,o,l;const c=1/this.direction.x,u=1/this.direction.y,h=1/this.direction.z,d=this.origin;return c>=0?(n=(e.min.x-d.x)*c,r=(e.max.x-d.x)*c):(n=(e.max.x-d.x)*c,r=(e.min.x-d.x)*c),u>=0?(s=(e.min.y-d.y)*u,a=(e.max.y-d.y)*u):(s=(e.max.y-d.y)*u,a=(e.min.y-d.y)*u),n>a||s>r||((s>n||isNaN(n))&&(n=s),(a<r||isNaN(r))&&(r=a),h>=0?(o=(e.min.z-d.z)*h,l=(e.max.z-d.z)*h):(o=(e.max.z-d.z)*h,l=(e.min.z-d.z)*h),n>l||o>r)||((o>n||n!==n)&&(n=o),(l<r||r!==r)&&(r=l),r<0)?null:this.at(n>=0?n:r,t)}intersectsBox(e){return this.intersectBox(e,Ei)!==null}intersectTriangle(e,t,n,r,s){cl.subVectors(t,e),wa.subVectors(n,e),ul.crossVectors(cl,wa);let a=this.direction.dot(ul),o;if(a>0){if(r)return null;o=1}else if(a<0)o=-1,a=-a;else return null;Gi.subVectors(this.origin,e);const l=o*this.direction.dot(wa.crossVectors(Gi,wa));if(l<0)return null;const c=o*this.direction.dot(cl.cross(Gi));if(c<0||l+c>a)return null;const u=-o*Gi.dot(ul);return u<0?null:this.at(u/a,s)}applyMatrix4(e){return this.origin.applyMatrix4(e),this.direction.transformDirection(e),this}equals(e){return e.origin.equals(this.origin)&&e.direction.equals(this.direction)}clone(){return new this.constructor().copy(this)}}class zt{constructor(e,t,n,r,s,a,o,l,c,u,h,d,m,_,v,p){zt.prototype.isMatrix4=!0,this.elements=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],e!==void 0&&this.set(e,t,n,r,s,a,o,l,c,u,h,d,m,_,v,p)}set(e,t,n,r,s,a,o,l,c,u,h,d,m,_,v,p){const f=this.elements;return f[0]=e,f[4]=t,f[8]=n,f[12]=r,f[1]=s,f[5]=a,f[9]=o,f[13]=l,f[2]=c,f[6]=u,f[10]=h,f[14]=d,f[3]=m,f[7]=_,f[11]=v,f[15]=p,this}identity(){return this.set(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1),this}clone(){return new zt().fromArray(this.elements)}copy(e){const t=this.elements,n=e.elements;return t[0]=n[0],t[1]=n[1],t[2]=n[2],t[3]=n[3],t[4]=n[4],t[5]=n[5],t[6]=n[6],t[7]=n[7],t[8]=n[8],t[9]=n[9],t[10]=n[10],t[11]=n[11],t[12]=n[12],t[13]=n[13],t[14]=n[14],t[15]=n[15],this}copyPosition(e){const t=this.elements,n=e.elements;return t[12]=n[12],t[13]=n[13],t[14]=n[14],this}setFromMatrix3(e){const t=e.elements;return this.set(t[0],t[3],t[6],0,t[1],t[4],t[7],0,t[2],t[5],t[8],0,0,0,0,1),this}extractBasis(e,t,n){return e.setFromMatrixColumn(this,0),t.setFromMatrixColumn(this,1),n.setFromMatrixColumn(this,2),this}makeBasis(e,t,n){return this.set(e.x,t.x,n.x,0,e.y,t.y,n.y,0,e.z,t.z,n.z,0,0,0,0,1),this}extractRotation(e){const t=this.elements,n=e.elements,r=1/Zr.setFromMatrixColumn(e,0).length(),s=1/Zr.setFromMatrixColumn(e,1).length(),a=1/Zr.setFromMatrixColumn(e,2).length();return t[0]=n[0]*r,t[1]=n[1]*r,t[2]=n[2]*r,t[3]=0,t[4]=n[4]*s,t[5]=n[5]*s,t[6]=n[6]*s,t[7]=0,t[8]=n[8]*a,t[9]=n[9]*a,t[10]=n[10]*a,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromEuler(e){const t=this.elements,n=e.x,r=e.y,s=e.z,a=Math.cos(n),o=Math.sin(n),l=Math.cos(r),c=Math.sin(r),u=Math.cos(s),h=Math.sin(s);if(e.order==="XYZ"){const d=a*u,m=a*h,_=o*u,v=o*h;t[0]=l*u,t[4]=-l*h,t[8]=c,t[1]=m+_*c,t[5]=d-v*c,t[9]=-o*l,t[2]=v-d*c,t[6]=_+m*c,t[10]=a*l}else if(e.order==="YXZ"){const d=l*u,m=l*h,_=c*u,v=c*h;t[0]=d+v*o,t[4]=_*o-m,t[8]=a*c,t[1]=a*h,t[5]=a*u,t[9]=-o,t[2]=m*o-_,t[6]=v+d*o,t[10]=a*l}else if(e.order==="ZXY"){const d=l*u,m=l*h,_=c*u,v=c*h;t[0]=d-v*o,t[4]=-a*h,t[8]=_+m*o,t[1]=m+_*o,t[5]=a*u,t[9]=v-d*o,t[2]=-a*c,t[6]=o,t[10]=a*l}else if(e.order==="ZYX"){const d=a*u,m=a*h,_=o*u,v=o*h;t[0]=l*u,t[4]=_*c-m,t[8]=d*c+v,t[1]=l*h,t[5]=v*c+d,t[9]=m*c-_,t[2]=-c,t[6]=o*l,t[10]=a*l}else if(e.order==="YZX"){const d=a*l,m=a*c,_=o*l,v=o*c;t[0]=l*u,t[4]=v-d*h,t[8]=_*h+m,t[1]=h,t[5]=a*u,t[9]=-o*u,t[2]=-c*u,t[6]=m*h+_,t[10]=d-v*h}else if(e.order==="XZY"){const d=a*l,m=a*c,_=o*l,v=o*c;t[0]=l*u,t[4]=-h,t[8]=c*u,t[1]=d*h+v,t[5]=a*u,t[9]=m*h-_,t[2]=_*h-m,t[6]=o*u,t[10]=v*h+d}return t[3]=0,t[7]=0,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromQuaternion(e){return this.compose(km,e,Hm)}lookAt(e,t,n){const r=this.elements;return In.subVectors(e,t),In.lengthSq()===0&&(In.z=1),In.normalize(),Wi.crossVectors(n,In),Wi.lengthSq()===0&&(Math.abs(n.z)===1?In.x+=1e-4:In.z+=1e-4,In.normalize(),Wi.crossVectors(n,In)),Wi.normalize(),Aa.crossVectors(In,Wi),r[0]=Wi.x,r[4]=Aa.x,r[8]=In.x,r[1]=Wi.y,r[5]=Aa.y,r[9]=In.y,r[2]=Wi.z,r[6]=Aa.z,r[10]=In.z,this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){const n=e.elements,r=t.elements,s=this.elements,a=n[0],o=n[4],l=n[8],c=n[12],u=n[1],h=n[5],d=n[9],m=n[13],_=n[2],v=n[6],p=n[10],f=n[14],E=n[3],y=n[7],T=n[11],z=n[15],C=r[0],D=r[4],B=r[8],w=r[12],x=r[1],R=r[5],j=r[9],O=r[13],K=r[2],W=r[6],J=r[10],Y=r[14],ee=r[3],pe=r[7],ue=r[11],_e=r[15];return s[0]=a*C+o*x+l*K+c*ee,s[4]=a*D+o*R+l*W+c*pe,s[8]=a*B+o*j+l*J+c*ue,s[12]=a*w+o*O+l*Y+c*_e,s[1]=u*C+h*x+d*K+m*ee,s[5]=u*D+h*R+d*W+m*pe,s[9]=u*B+h*j+d*J+m*ue,s[13]=u*w+h*O+d*Y+m*_e,s[2]=_*C+v*x+p*K+f*ee,s[6]=_*D+v*R+p*W+f*pe,s[10]=_*B+v*j+p*J+f*ue,s[14]=_*w+v*O+p*Y+f*_e,s[3]=E*C+y*x+T*K+z*ee,s[7]=E*D+y*R+T*W+z*pe,s[11]=E*B+y*j+T*J+z*ue,s[15]=E*w+y*O+T*Y+z*_e,this}multiplyScalar(e){const t=this.elements;return t[0]*=e,t[4]*=e,t[8]*=e,t[12]*=e,t[1]*=e,t[5]*=e,t[9]*=e,t[13]*=e,t[2]*=e,t[6]*=e,t[10]*=e,t[14]*=e,t[3]*=e,t[7]*=e,t[11]*=e,t[15]*=e,this}determinant(){const e=this.elements,t=e[0],n=e[4],r=e[8],s=e[12],a=e[1],o=e[5],l=e[9],c=e[13],u=e[2],h=e[6],d=e[10],m=e[14],_=e[3],v=e[7],p=e[11],f=e[15];return _*(+s*l*h-r*c*h-s*o*d+n*c*d+r*o*m-n*l*m)+v*(+t*l*m-t*c*d+s*a*d-r*a*m+r*c*u-s*l*u)+p*(+t*c*h-t*o*m-s*a*h+n*a*m+s*o*u-n*c*u)+f*(-r*o*u-t*l*h+t*o*d+r*a*h-n*a*d+n*l*u)}transpose(){const e=this.elements;let t;return t=e[1],e[1]=e[4],e[4]=t,t=e[2],e[2]=e[8],e[8]=t,t=e[6],e[6]=e[9],e[9]=t,t=e[3],e[3]=e[12],e[12]=t,t=e[7],e[7]=e[13],e[13]=t,t=e[11],e[11]=e[14],e[14]=t,this}setPosition(e,t,n){const r=this.elements;return e.isVector3?(r[12]=e.x,r[13]=e.y,r[14]=e.z):(r[12]=e,r[13]=t,r[14]=n),this}invert(){const e=this.elements,t=e[0],n=e[1],r=e[2],s=e[3],a=e[4],o=e[5],l=e[6],c=e[7],u=e[8],h=e[9],d=e[10],m=e[11],_=e[12],v=e[13],p=e[14],f=e[15],E=h*p*c-v*d*c+v*l*m-o*p*m-h*l*f+o*d*f,y=_*d*c-u*p*c-_*l*m+a*p*m+u*l*f-a*d*f,T=u*v*c-_*h*c+_*o*m-a*v*m-u*o*f+a*h*f,z=_*h*l-u*v*l-_*o*d+a*v*d+u*o*p-a*h*p,C=t*E+n*y+r*T+s*z;if(C===0)return this.set(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);const D=1/C;return e[0]=E*D,e[1]=(v*d*s-h*p*s-v*r*m+n*p*m+h*r*f-n*d*f)*D,e[2]=(o*p*s-v*l*s+v*r*c-n*p*c-o*r*f+n*l*f)*D,e[3]=(h*l*s-o*d*s-h*r*c+n*d*c+o*r*m-n*l*m)*D,e[4]=y*D,e[5]=(u*p*s-_*d*s+_*r*m-t*p*m-u*r*f+t*d*f)*D,e[6]=(_*l*s-a*p*s-_*r*c+t*p*c+a*r*f-t*l*f)*D,e[7]=(a*d*s-u*l*s+u*r*c-t*d*c-a*r*m+t*l*m)*D,e[8]=T*D,e[9]=(_*h*s-u*v*s-_*n*m+t*v*m+u*n*f-t*h*f)*D,e[10]=(a*v*s-_*o*s+_*n*c-t*v*c-a*n*f+t*o*f)*D,e[11]=(u*o*s-a*h*s-u*n*c+t*h*c+a*n*m-t*o*m)*D,e[12]=z*D,e[13]=(u*v*r-_*h*r+_*n*d-t*v*d-u*n*p+t*h*p)*D,e[14]=(_*o*r-a*v*r-_*n*l+t*v*l+a*n*p-t*o*p)*D,e[15]=(a*h*r-u*o*r+u*n*l-t*h*l-a*n*d+t*o*d)*D,this}scale(e){const t=this.elements,n=e.x,r=e.y,s=e.z;return t[0]*=n,t[4]*=r,t[8]*=s,t[1]*=n,t[5]*=r,t[9]*=s,t[2]*=n,t[6]*=r,t[10]*=s,t[3]*=n,t[7]*=r,t[11]*=s,this}getMaxScaleOnAxis(){const e=this.elements,t=e[0]*e[0]+e[1]*e[1]+e[2]*e[2],n=e[4]*e[4]+e[5]*e[5]+e[6]*e[6],r=e[8]*e[8]+e[9]*e[9]+e[10]*e[10];return Math.sqrt(Math.max(t,n,r))}makeTranslation(e,t,n){return e.isVector3?this.set(1,0,0,e.x,0,1,0,e.y,0,0,1,e.z,0,0,0,1):this.set(1,0,0,e,0,1,0,t,0,0,1,n,0,0,0,1),this}makeRotationX(e){const t=Math.cos(e),n=Math.sin(e);return this.set(1,0,0,0,0,t,-n,0,0,n,t,0,0,0,0,1),this}makeRotationY(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,0,n,0,0,1,0,0,-n,0,t,0,0,0,0,1),this}makeRotationZ(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,-n,0,0,n,t,0,0,0,0,1,0,0,0,0,1),this}makeRotationAxis(e,t){const n=Math.cos(t),r=Math.sin(t),s=1-n,a=e.x,o=e.y,l=e.z,c=s*a,u=s*o;return this.set(c*a+n,c*o-r*l,c*l+r*o,0,c*o+r*l,u*o+n,u*l-r*a,0,c*l-r*o,u*l+r*a,s*l*l+n,0,0,0,0,1),this}makeScale(e,t,n){return this.set(e,0,0,0,0,t,0,0,0,0,n,0,0,0,0,1),this}makeShear(e,t,n,r,s,a){return this.set(1,n,s,0,e,1,a,0,t,r,1,0,0,0,0,1),this}compose(e,t,n){const r=this.elements,s=t._x,a=t._y,o=t._z,l=t._w,c=s+s,u=a+a,h=o+o,d=s*c,m=s*u,_=s*h,v=a*u,p=a*h,f=o*h,E=l*c,y=l*u,T=l*h,z=n.x,C=n.y,D=n.z;return r[0]=(1-(v+f))*z,r[1]=(m+T)*z,r[2]=(_-y)*z,r[3]=0,r[4]=(m-T)*C,r[5]=(1-(d+f))*C,r[6]=(p+E)*C,r[7]=0,r[8]=(_+y)*D,r[9]=(p-E)*D,r[10]=(1-(d+v))*D,r[11]=0,r[12]=e.x,r[13]=e.y,r[14]=e.z,r[15]=1,this}decompose(e,t,n){const r=this.elements;let s=Zr.set(r[0],r[1],r[2]).length();const a=Zr.set(r[4],r[5],r[6]).length(),o=Zr.set(r[8],r[9],r[10]).length();this.determinant()<0&&(s=-s),e.x=r[12],e.y=r[13],e.z=r[14],Zn.copy(this);const c=1/s,u=1/a,h=1/o;return Zn.elements[0]*=c,Zn.elements[1]*=c,Zn.elements[2]*=c,Zn.elements[4]*=u,Zn.elements[5]*=u,Zn.elements[6]*=u,Zn.elements[8]*=h,Zn.elements[9]*=h,Zn.elements[10]*=h,t.setFromRotationMatrix(Zn),n.x=s,n.y=a,n.z=o,this}makePerspective(e,t,n,r,s,a,o=Pi){const l=this.elements,c=2*s/(t-e),u=2*s/(n-r),h=(t+e)/(t-e),d=(n+r)/(n-r);let m,_;if(o===Pi)m=-(a+s)/(a-s),_=-2*a*s/(a-s);else if(o===go)m=-a/(a-s),_=-a*s/(a-s);else throw new Error("THREE.Matrix4.makePerspective(): Invalid coordinate system: "+o);return l[0]=c,l[4]=0,l[8]=h,l[12]=0,l[1]=0,l[5]=u,l[9]=d,l[13]=0,l[2]=0,l[6]=0,l[10]=m,l[14]=_,l[3]=0,l[7]=0,l[11]=-1,l[15]=0,this}makeOrthographic(e,t,n,r,s,a,o=Pi){const l=this.elements,c=1/(t-e),u=1/(n-r),h=1/(a-s),d=(t+e)*c,m=(n+r)*u;let _,v;if(o===Pi)_=(a+s)*h,v=-2*h;else if(o===go)_=s*h,v=-1*h;else throw new Error("THREE.Matrix4.makeOrthographic(): Invalid coordinate system: "+o);return l[0]=2*c,l[4]=0,l[8]=0,l[12]=-d,l[1]=0,l[5]=2*u,l[9]=0,l[13]=-m,l[2]=0,l[6]=0,l[10]=v,l[14]=-_,l[3]=0,l[7]=0,l[11]=0,l[15]=1,this}equals(e){const t=this.elements,n=e.elements;for(let r=0;r<16;r++)if(t[r]!==n[r])return!1;return!0}fromArray(e,t=0){for(let n=0;n<16;n++)this.elements[n]=e[n+t];return this}toArray(e=[],t=0){const n=this.elements;return e[t]=n[0],e[t+1]=n[1],e[t+2]=n[2],e[t+3]=n[3],e[t+4]=n[4],e[t+5]=n[5],e[t+6]=n[6],e[t+7]=n[7],e[t+8]=n[8],e[t+9]=n[9],e[t+10]=n[10],e[t+11]=n[11],e[t+12]=n[12],e[t+13]=n[13],e[t+14]=n[14],e[t+15]=n[15],e}}const Zr=new V,Zn=new zt,km=new V(0,0,0),Hm=new V(1,1,1),Wi=new V,Aa=new V,In=new V,Vu=new zt,Gu=new Rr;class gi{constructor(e=0,t=0,n=0,r=gi.DEFAULT_ORDER){this.isEuler=!0,this._x=e,this._y=t,this._z=n,this._order=r}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get order(){return this._order}set order(e){this._order=e,this._onChangeCallback()}set(e,t,n,r=this._order){return this._x=e,this._y=t,this._z=n,this._order=r,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._order)}copy(e){return this._x=e._x,this._y=e._y,this._z=e._z,this._order=e._order,this._onChangeCallback(),this}setFromRotationMatrix(e,t=this._order,n=!0){const r=e.elements,s=r[0],a=r[4],o=r[8],l=r[1],c=r[5],u=r[9],h=r[2],d=r[6],m=r[10];switch(t){case"XYZ":this._y=Math.asin(pn(o,-1,1)),Math.abs(o)<.9999999?(this._x=Math.atan2(-u,m),this._z=Math.atan2(-a,s)):(this._x=Math.atan2(d,c),this._z=0);break;case"YXZ":this._x=Math.asin(-pn(u,-1,1)),Math.abs(u)<.9999999?(this._y=Math.atan2(o,m),this._z=Math.atan2(l,c)):(this._y=Math.atan2(-h,s),this._z=0);break;case"ZXY":this._x=Math.asin(pn(d,-1,1)),Math.abs(d)<.9999999?(this._y=Math.atan2(-h,m),this._z=Math.atan2(-a,c)):(this._y=0,this._z=Math.atan2(l,s));break;case"ZYX":this._y=Math.asin(-pn(h,-1,1)),Math.abs(h)<.9999999?(this._x=Math.atan2(d,m),this._z=Math.atan2(l,s)):(this._x=0,this._z=Math.atan2(-a,c));break;case"YZX":this._z=Math.asin(pn(l,-1,1)),Math.abs(l)<.9999999?(this._x=Math.atan2(-u,c),this._y=Math.atan2(-h,s)):(this._x=0,this._y=Math.atan2(o,m));break;case"XZY":this._z=Math.asin(-pn(a,-1,1)),Math.abs(a)<.9999999?(this._x=Math.atan2(d,c),this._y=Math.atan2(o,s)):(this._x=Math.atan2(-u,m),this._y=0);break;default:console.warn("THREE.Euler: .setFromRotationMatrix() encountered an unknown order: "+t)}return this._order=t,n===!0&&this._onChangeCallback(),this}setFromQuaternion(e,t,n){return Vu.makeRotationFromQuaternion(e),this.setFromRotationMatrix(Vu,t,n)}setFromVector3(e,t=this._order){return this.set(e.x,e.y,e.z,t)}reorder(e){return Gu.setFromEuler(this),this.setFromQuaternion(Gu,e)}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._order===this._order}fromArray(e){return this._x=e[0],this._y=e[1],this._z=e[2],e[3]!==void 0&&(this._order=e[3]),this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._order,e}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._order}}gi.DEFAULT_ORDER="XYZ";class zc{constructor(){this.mask=1}set(e){this.mask=(1<<e|0)>>>0}enable(e){this.mask|=1<<e|0}enableAll(){this.mask=-1}toggle(e){this.mask^=1<<e|0}disable(e){this.mask&=~(1<<e|0)}disableAll(){this.mask=0}test(e){return(this.mask&e.mask)!==0}isEnabled(e){return(this.mask&(1<<e|0))!==0}}let Vm=0;const Wu=new V,Jr=new Rr,bi=new zt,Ra=new V,qs=new V,Gm=new V,Wm=new Rr,Xu=new V(1,0,0),Yu=new V(0,1,0),qu=new V(0,0,1),$u={type:"added"},Xm={type:"removed"},Qr={type:"childadded",child:null},hl={type:"childremoved",child:null};class Kt extends Ds{constructor(){super(),this.isObject3D=!0,Object.defineProperty(this,"id",{value:Vm++}),this.uuid=Li(),this.name="",this.type="Object3D",this.parent=null,this.children=[],this.up=Kt.DEFAULT_UP.clone();const e=new V,t=new gi,n=new Rr,r=new V(1,1,1);function s(){n.setFromEuler(t,!1)}function a(){t.setFromQuaternion(n,void 0,!1)}t._onChange(s),n._onChange(a),Object.defineProperties(this,{position:{configurable:!0,enumerable:!0,value:e},rotation:{configurable:!0,enumerable:!0,value:t},quaternion:{configurable:!0,enumerable:!0,value:n},scale:{configurable:!0,enumerable:!0,value:r},modelViewMatrix:{value:new zt},normalMatrix:{value:new rt}}),this.matrix=new zt,this.matrixWorld=new zt,this.matrixAutoUpdate=Kt.DEFAULT_MATRIX_AUTO_UPDATE,this.matrixWorldAutoUpdate=Kt.DEFAULT_MATRIX_WORLD_AUTO_UPDATE,this.matrixWorldNeedsUpdate=!1,this.layers=new zc,this.visible=!0,this.castShadow=!1,this.receiveShadow=!1,this.frustumCulled=!0,this.renderOrder=0,this.animations=[],this.userData={}}onBeforeShadow(){}onAfterShadow(){}onBeforeRender(){}onAfterRender(){}applyMatrix4(e){this.matrixAutoUpdate&&this.updateMatrix(),this.matrix.premultiply(e),this.matrix.decompose(this.position,this.quaternion,this.scale)}applyQuaternion(e){return this.quaternion.premultiply(e),this}setRotationFromAxisAngle(e,t){this.quaternion.setFromAxisAngle(e,t)}setRotationFromEuler(e){this.quaternion.setFromEuler(e,!0)}setRotationFromMatrix(e){this.quaternion.setFromRotationMatrix(e)}setRotationFromQuaternion(e){this.quaternion.copy(e)}rotateOnAxis(e,t){return Jr.setFromAxisAngle(e,t),this.quaternion.multiply(Jr),this}rotateOnWorldAxis(e,t){return Jr.setFromAxisAngle(e,t),this.quaternion.premultiply(Jr),this}rotateX(e){return this.rotateOnAxis(Xu,e)}rotateY(e){return this.rotateOnAxis(Yu,e)}rotateZ(e){return this.rotateOnAxis(qu,e)}translateOnAxis(e,t){return Wu.copy(e).applyQuaternion(this.quaternion),this.position.add(Wu.multiplyScalar(t)),this}translateX(e){return this.translateOnAxis(Xu,e)}translateY(e){return this.translateOnAxis(Yu,e)}translateZ(e){return this.translateOnAxis(qu,e)}localToWorld(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(this.matrixWorld)}worldToLocal(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(bi.copy(this.matrixWorld).invert())}lookAt(e,t,n){e.isVector3?Ra.copy(e):Ra.set(e,t,n);const r=this.parent;this.updateWorldMatrix(!0,!1),qs.setFromMatrixPosition(this.matrixWorld),this.isCamera||this.isLight?bi.lookAt(qs,Ra,this.up):bi.lookAt(Ra,qs,this.up),this.quaternion.setFromRotationMatrix(bi),r&&(bi.extractRotation(r.matrixWorld),Jr.setFromRotationMatrix(bi),this.quaternion.premultiply(Jr.invert()))}add(e){if(arguments.length>1){for(let t=0;t<arguments.length;t++)this.add(arguments[t]);return this}return e===this?(console.error("THREE.Object3D.add: object can't be added as a child of itself.",e),this):(e&&e.isObject3D?(e.removeFromParent(),e.parent=this,this.children.push(e),e.dispatchEvent($u),Qr.child=e,this.dispatchEvent(Qr),Qr.child=null):console.error("THREE.Object3D.add: object not an instance of THREE.Object3D.",e),this)}remove(e){if(arguments.length>1){for(let n=0;n<arguments.length;n++)this.remove(arguments[n]);return this}const t=this.children.indexOf(e);return t!==-1&&(e.parent=null,this.children.splice(t,1),e.dispatchEvent(Xm),hl.child=e,this.dispatchEvent(hl),hl.child=null),this}removeFromParent(){const e=this.parent;return e!==null&&e.remove(this),this}clear(){return this.remove(...this.children)}attach(e){return this.updateWorldMatrix(!0,!1),bi.copy(this.matrixWorld).invert(),e.parent!==null&&(e.parent.updateWorldMatrix(!0,!1),bi.multiply(e.parent.matrixWorld)),e.applyMatrix4(bi),e.removeFromParent(),e.parent=this,this.children.push(e),e.updateWorldMatrix(!1,!0),e.dispatchEvent($u),Qr.child=e,this.dispatchEvent(Qr),Qr.child=null,this}getObjectById(e){return this.getObjectByProperty("id",e)}getObjectByName(e){return this.getObjectByProperty("name",e)}getObjectByProperty(e,t){if(this[e]===t)return this;for(let n=0,r=this.children.length;n<r;n++){const a=this.children[n].getObjectByProperty(e,t);if(a!==void 0)return a}}getObjectsByProperty(e,t,n=[]){this[e]===t&&n.push(this);const r=this.children;for(let s=0,a=r.length;s<a;s++)r[s].getObjectsByProperty(e,t,n);return n}getWorldPosition(e){return this.updateWorldMatrix(!0,!1),e.setFromMatrixPosition(this.matrixWorld)}getWorldQuaternion(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(qs,e,Gm),e}getWorldScale(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(qs,Wm,e),e}getWorldDirection(e){this.updateWorldMatrix(!0,!1);const t=this.matrixWorld.elements;return e.set(t[8],t[9],t[10]).normalize()}raycast(){}traverse(e){e(this);const t=this.children;for(let n=0,r=t.length;n<r;n++)t[n].traverse(e)}traverseVisible(e){if(this.visible===!1)return;e(this);const t=this.children;for(let n=0,r=t.length;n<r;n++)t[n].traverseVisible(e)}traverseAncestors(e){const t=this.parent;t!==null&&(e(t),t.traverseAncestors(e))}updateMatrix(){this.matrix.compose(this.position,this.quaternion,this.scale),this.matrixWorldNeedsUpdate=!0}updateMatrixWorld(e){this.matrixAutoUpdate&&this.updateMatrix(),(this.matrixWorldNeedsUpdate||e)&&(this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),this.matrixWorldNeedsUpdate=!1,e=!0);const t=this.children;for(let n=0,r=t.length;n<r;n++)t[n].updateMatrixWorld(e)}updateWorldMatrix(e,t){const n=this.parent;if(e===!0&&n!==null&&n.updateWorldMatrix(!0,!1),this.matrixAutoUpdate&&this.updateMatrix(),this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),t===!0){const r=this.children;for(let s=0,a=r.length;s<a;s++)r[s].updateWorldMatrix(!1,!0)}}toJSON(e){const t=e===void 0||typeof e=="string",n={};t&&(e={geometries:{},materials:{},textures:{},images:{},shapes:{},skeletons:{},animations:{},nodes:{}},n.metadata={version:4.6,type:"Object",generator:"Object3D.toJSON"});const r={};r.uuid=this.uuid,r.type=this.type,this.name!==""&&(r.name=this.name),this.castShadow===!0&&(r.castShadow=!0),this.receiveShadow===!0&&(r.receiveShadow=!0),this.visible===!1&&(r.visible=!1),this.frustumCulled===!1&&(r.frustumCulled=!1),this.renderOrder!==0&&(r.renderOrder=this.renderOrder),Object.keys(this.userData).length>0&&(r.userData=this.userData),r.layers=this.layers.mask,r.matrix=this.matrix.toArray(),r.up=this.up.toArray(),this.matrixAutoUpdate===!1&&(r.matrixAutoUpdate=!1),this.isInstancedMesh&&(r.type="InstancedMesh",r.count=this.count,r.instanceMatrix=this.instanceMatrix.toJSON(),this.instanceColor!==null&&(r.instanceColor=this.instanceColor.toJSON())),this.isBatchedMesh&&(r.type="BatchedMesh",r.perObjectFrustumCulled=this.perObjectFrustumCulled,r.sortObjects=this.sortObjects,r.drawRanges=this._drawRanges,r.reservedRanges=this._reservedRanges,r.visibility=this._visibility,r.active=this._active,r.bounds=this._bounds.map(o=>({boxInitialized:o.boxInitialized,boxMin:o.box.min.toArray(),boxMax:o.box.max.toArray(),sphereInitialized:o.sphereInitialized,sphereRadius:o.sphere.radius,sphereCenter:o.sphere.center.toArray()})),r.maxInstanceCount=this._maxInstanceCount,r.maxVertexCount=this._maxVertexCount,r.maxIndexCount=this._maxIndexCount,r.geometryInitialized=this._geometryInitialized,r.geometryCount=this._geometryCount,r.matricesTexture=this._matricesTexture.toJSON(e),this._colorsTexture!==null&&(r.colorsTexture=this._colorsTexture.toJSON(e)),this.boundingSphere!==null&&(r.boundingSphere={center:r.boundingSphere.center.toArray(),radius:r.boundingSphere.radius}),this.boundingBox!==null&&(r.boundingBox={min:r.boundingBox.min.toArray(),max:r.boundingBox.max.toArray()}));function s(o,l){return o[l.uuid]===void 0&&(o[l.uuid]=l.toJSON(e)),l.uuid}if(this.isScene)this.background&&(this.background.isColor?r.background=this.background.toJSON():this.background.isTexture&&(r.background=this.background.toJSON(e).uuid)),this.environment&&this.environment.isTexture&&this.environment.isRenderTargetTexture!==!0&&(r.environment=this.environment.toJSON(e).uuid);else if(this.isMesh||this.isLine||this.isPoints){r.geometry=s(e.geometries,this.geometry);const o=this.geometry.parameters;if(o!==void 0&&o.shapes!==void 0){const l=o.shapes;if(Array.isArray(l))for(let c=0,u=l.length;c<u;c++){const h=l[c];s(e.shapes,h)}else s(e.shapes,l)}}if(this.isSkinnedMesh&&(r.bindMode=this.bindMode,r.bindMatrix=this.bindMatrix.toArray(),this.skeleton!==void 0&&(s(e.skeletons,this.skeleton),r.skeleton=this.skeleton.uuid)),this.material!==void 0)if(Array.isArray(this.material)){const o=[];for(let l=0,c=this.material.length;l<c;l++)o.push(s(e.materials,this.material[l]));r.material=o}else r.material=s(e.materials,this.material);if(this.children.length>0){r.children=[];for(let o=0;o<this.children.length;o++)r.children.push(this.children[o].toJSON(e).object)}if(this.animations.length>0){r.animations=[];for(let o=0;o<this.animations.length;o++){const l=this.animations[o];r.animations.push(s(e.animations,l))}}if(t){const o=a(e.geometries),l=a(e.materials),c=a(e.textures),u=a(e.images),h=a(e.shapes),d=a(e.skeletons),m=a(e.animations),_=a(e.nodes);o.length>0&&(n.geometries=o),l.length>0&&(n.materials=l),c.length>0&&(n.textures=c),u.length>0&&(n.images=u),h.length>0&&(n.shapes=h),d.length>0&&(n.skeletons=d),m.length>0&&(n.animations=m),_.length>0&&(n.nodes=_)}return n.object=r,n;function a(o){const l=[];for(const c in o){const u=o[c];delete u.metadata,l.push(u)}return l}}clone(e){return new this.constructor().copy(this,e)}copy(e,t=!0){if(this.name=e.name,this.up.copy(e.up),this.position.copy(e.position),this.rotation.order=e.rotation.order,this.quaternion.copy(e.quaternion),this.scale.copy(e.scale),this.matrix.copy(e.matrix),this.matrixWorld.copy(e.matrixWorld),this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrixWorldAutoUpdate=e.matrixWorldAutoUpdate,this.matrixWorldNeedsUpdate=e.matrixWorldNeedsUpdate,this.layers.mask=e.layers.mask,this.visible=e.visible,this.castShadow=e.castShadow,this.receiveShadow=e.receiveShadow,this.frustumCulled=e.frustumCulled,this.renderOrder=e.renderOrder,this.animations=e.animations.slice(),this.userData=JSON.parse(JSON.stringify(e.userData)),t===!0)for(let n=0;n<e.children.length;n++){const r=e.children[n];this.add(r.clone())}return this}}Kt.DEFAULT_UP=new V(0,1,0);Kt.DEFAULT_MATRIX_AUTO_UPDATE=!0;Kt.DEFAULT_MATRIX_WORLD_AUTO_UPDATE=!0;const Jn=new V,Ti=new V,dl=new V,wi=new V,es=new V,ts=new V,ju=new V,fl=new V,pl=new V,ml=new V;class Gn{constructor(e=new V,t=new V,n=new V){this.a=e,this.b=t,this.c=n}static getNormal(e,t,n,r){r.subVectors(n,t),Jn.subVectors(e,t),r.cross(Jn);const s=r.lengthSq();return s>0?r.multiplyScalar(1/Math.sqrt(s)):r.set(0,0,0)}static getBarycoord(e,t,n,r,s){Jn.subVectors(r,t),Ti.subVectors(n,t),dl.subVectors(e,t);const a=Jn.dot(Jn),o=Jn.dot(Ti),l=Jn.dot(dl),c=Ti.dot(Ti),u=Ti.dot(dl),h=a*c-o*o;if(h===0)return s.set(0,0,0),null;const d=1/h,m=(c*l-o*u)*d,_=(a*u-o*l)*d;return s.set(1-m-_,_,m)}static containsPoint(e,t,n,r){return this.getBarycoord(e,t,n,r,wi)===null?!1:wi.x>=0&&wi.y>=0&&wi.x+wi.y<=1}static getInterpolation(e,t,n,r,s,a,o,l){return this.getBarycoord(e,t,n,r,wi)===null?(l.x=0,l.y=0,"z"in l&&(l.z=0),"w"in l&&(l.w=0),null):(l.setScalar(0),l.addScaledVector(s,wi.x),l.addScaledVector(a,wi.y),l.addScaledVector(o,wi.z),l)}static isFrontFacing(e,t,n,r){return Jn.subVectors(n,t),Ti.subVectors(e,t),Jn.cross(Ti).dot(r)<0}set(e,t,n){return this.a.copy(e),this.b.copy(t),this.c.copy(n),this}setFromPointsAndIndices(e,t,n,r){return this.a.copy(e[t]),this.b.copy(e[n]),this.c.copy(e[r]),this}setFromAttributeAndIndices(e,t,n,r){return this.a.fromBufferAttribute(e,t),this.b.fromBufferAttribute(e,n),this.c.fromBufferAttribute(e,r),this}clone(){return new this.constructor().copy(this)}copy(e){return this.a.copy(e.a),this.b.copy(e.b),this.c.copy(e.c),this}getArea(){return Jn.subVectors(this.c,this.b),Ti.subVectors(this.a,this.b),Jn.cross(Ti).length()*.5}getMidpoint(e){return e.addVectors(this.a,this.b).add(this.c).multiplyScalar(1/3)}getNormal(e){return Gn.getNormal(this.a,this.b,this.c,e)}getPlane(e){return e.setFromCoplanarPoints(this.a,this.b,this.c)}getBarycoord(e,t){return Gn.getBarycoord(e,this.a,this.b,this.c,t)}getInterpolation(e,t,n,r,s){return Gn.getInterpolation(e,this.a,this.b,this.c,t,n,r,s)}containsPoint(e){return Gn.containsPoint(e,this.a,this.b,this.c)}isFrontFacing(e){return Gn.isFrontFacing(this.a,this.b,this.c,e)}intersectsBox(e){return e.intersectsTriangle(this)}closestPointToPoint(e,t){const n=this.a,r=this.b,s=this.c;let a,o;es.subVectors(r,n),ts.subVectors(s,n),fl.subVectors(e,n);const l=es.dot(fl),c=ts.dot(fl);if(l<=0&&c<=0)return t.copy(n);pl.subVectors(e,r);const u=es.dot(pl),h=ts.dot(pl);if(u>=0&&h<=u)return t.copy(r);const d=l*h-u*c;if(d<=0&&l>=0&&u<=0)return a=l/(l-u),t.copy(n).addScaledVector(es,a);ml.subVectors(e,s);const m=es.dot(ml),_=ts.dot(ml);if(_>=0&&m<=_)return t.copy(s);const v=m*c-l*_;if(v<=0&&c>=0&&_<=0)return o=c/(c-_),t.copy(n).addScaledVector(ts,o);const p=u*_-m*h;if(p<=0&&h-u>=0&&m-_>=0)return ju.subVectors(s,r),o=(h-u)/(h-u+(m-_)),t.copy(r).addScaledVector(ju,o);const f=1/(p+v+d);return a=v*f,o=d*f,t.copy(n).addScaledVector(es,a).addScaledVector(ts,o)}equals(e){return e.a.equals(this.a)&&e.b.equals(this.b)&&e.c.equals(this.c)}}const $d={aliceblue:15792383,antiquewhite:16444375,aqua:65535,aquamarine:8388564,azure:15794175,beige:16119260,bisque:16770244,black:0,blanchedalmond:16772045,blue:255,blueviolet:9055202,brown:10824234,burlywood:14596231,cadetblue:6266528,chartreuse:8388352,chocolate:13789470,coral:16744272,cornflowerblue:6591981,cornsilk:16775388,crimson:14423100,cyan:65535,darkblue:139,darkcyan:35723,darkgoldenrod:12092939,darkgray:11119017,darkgreen:25600,darkgrey:11119017,darkkhaki:12433259,darkmagenta:9109643,darkolivegreen:5597999,darkorange:16747520,darkorchid:10040012,darkred:9109504,darksalmon:15308410,darkseagreen:9419919,darkslateblue:4734347,darkslategray:3100495,darkslategrey:3100495,darkturquoise:52945,darkviolet:9699539,deeppink:16716947,deepskyblue:49151,dimgray:6908265,dimgrey:6908265,dodgerblue:2003199,firebrick:11674146,floralwhite:16775920,forestgreen:2263842,fuchsia:16711935,gainsboro:14474460,ghostwhite:16316671,gold:16766720,goldenrod:14329120,gray:8421504,green:32768,greenyellow:11403055,grey:8421504,honeydew:15794160,hotpink:16738740,indianred:13458524,indigo:4915330,ivory:16777200,khaki:15787660,lavender:15132410,lavenderblush:16773365,lawngreen:8190976,lemonchiffon:16775885,lightblue:11393254,lightcoral:15761536,lightcyan:14745599,lightgoldenrodyellow:16448210,lightgray:13882323,lightgreen:9498256,lightgrey:13882323,lightpink:16758465,lightsalmon:16752762,lightseagreen:2142890,lightskyblue:8900346,lightslategray:7833753,lightslategrey:7833753,lightsteelblue:11584734,lightyellow:16777184,lime:65280,limegreen:3329330,linen:16445670,magenta:16711935,maroon:8388608,mediumaquamarine:6737322,mediumblue:205,mediumorchid:12211667,mediumpurple:9662683,mediumseagreen:3978097,mediumslateblue:8087790,mediumspringgreen:64154,mediumturquoise:4772300,mediumvioletred:13047173,midnightblue:1644912,mintcream:16121850,mistyrose:16770273,moccasin:16770229,navajowhite:16768685,navy:128,oldlace:16643558,olive:8421376,olivedrab:7048739,orange:16753920,orangered:16729344,orchid:14315734,palegoldenrod:15657130,palegreen:10025880,paleturquoise:11529966,palevioletred:14381203,papayawhip:16773077,peachpuff:16767673,peru:13468991,pink:16761035,plum:14524637,powderblue:11591910,purple:8388736,rebeccapurple:6697881,red:16711680,rosybrown:12357519,royalblue:4286945,saddlebrown:9127187,salmon:16416882,sandybrown:16032864,seagreen:3050327,seashell:16774638,sienna:10506797,silver:12632256,skyblue:8900331,slateblue:6970061,slategray:7372944,slategrey:7372944,snow:16775930,springgreen:65407,steelblue:4620980,tan:13808780,teal:32896,thistle:14204888,tomato:16737095,turquoise:4251856,violet:15631086,wheat:16113331,white:16777215,whitesmoke:16119285,yellow:16776960,yellowgreen:10145074},Xi={h:0,s:0,l:0},Ca={h:0,s:0,l:0};function gl(i,e,t){return t<0&&(t+=1),t>1&&(t-=1),t<1/6?i+(e-i)*6*t:t<1/2?e:t<2/3?i+(e-i)*6*(2/3-t):i}class nt{constructor(e,t,n){return this.isColor=!0,this.r=1,this.g=1,this.b=1,this.set(e,t,n)}set(e,t,n){if(t===void 0&&n===void 0){const r=e;r&&r.isColor?this.copy(r):typeof r=="number"?this.setHex(r):typeof r=="string"&&this.setStyle(r)}else this.setRGB(e,t,n);return this}setScalar(e){return this.r=e,this.g=e,this.b=e,this}setHex(e,t=fi){return e=Math.floor(e),this.r=(e>>16&255)/255,this.g=(e>>8&255)/255,this.b=(e&255)/255,St.toWorkingColorSpace(this,t),this}setRGB(e,t,n,r=St.workingColorSpace){return this.r=e,this.g=t,this.b=n,St.toWorkingColorSpace(this,r),this}setHSL(e,t,n,r=St.workingColorSpace){if(e=Bc(e,1),t=pn(t,0,1),n=pn(n,0,1),t===0)this.r=this.g=this.b=n;else{const s=n<=.5?n*(1+t):n+t-n*t,a=2*n-s;this.r=gl(a,s,e+1/3),this.g=gl(a,s,e),this.b=gl(a,s,e-1/3)}return St.toWorkingColorSpace(this,r),this}setStyle(e,t=fi){function n(s){s!==void 0&&parseFloat(s)<1&&console.warn("THREE.Color: Alpha component of "+e+" will be ignored.")}let r;if(r=/^(\w+)\(([^\)]*)\)/.exec(e)){let s;const a=r[1],o=r[2];switch(a){case"rgb":case"rgba":if(s=/^\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(o))return n(s[4]),this.setRGB(Math.min(255,parseInt(s[1],10))/255,Math.min(255,parseInt(s[2],10))/255,Math.min(255,parseInt(s[3],10))/255,t);if(s=/^\s*(\d+)\%\s*,\s*(\d+)\%\s*,\s*(\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(o))return n(s[4]),this.setRGB(Math.min(100,parseInt(s[1],10))/100,Math.min(100,parseInt(s[2],10))/100,Math.min(100,parseInt(s[3],10))/100,t);break;case"hsl":case"hsla":if(s=/^\s*(\d*\.?\d+)\s*,\s*(\d*\.?\d+)\%\s*,\s*(\d*\.?\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(o))return n(s[4]),this.setHSL(parseFloat(s[1])/360,parseFloat(s[2])/100,parseFloat(s[3])/100,t);break;default:console.warn("THREE.Color: Unknown color model "+e)}}else if(r=/^\#([A-Fa-f\d]+)$/.exec(e)){const s=r[1],a=s.length;if(a===3)return this.setRGB(parseInt(s.charAt(0),16)/15,parseInt(s.charAt(1),16)/15,parseInt(s.charAt(2),16)/15,t);if(a===6)return this.setHex(parseInt(s,16),t);console.warn("THREE.Color: Invalid hex color "+e)}else if(e&&e.length>0)return this.setColorName(e,t);return this}setColorName(e,t=fi){const n=$d[e.toLowerCase()];return n!==void 0?this.setHex(n,t):console.warn("THREE.Color: Unknown color "+e),this}clone(){return new this.constructor(this.r,this.g,this.b)}copy(e){return this.r=e.r,this.g=e.g,this.b=e.b,this}copySRGBToLinear(e){return this.r=Ms(e.r),this.g=Ms(e.g),this.b=Ms(e.b),this}copyLinearToSRGB(e){return this.r=il(e.r),this.g=il(e.g),this.b=il(e.b),this}convertSRGBToLinear(){return this.copySRGBToLinear(this),this}convertLinearToSRGB(){return this.copyLinearToSRGB(this),this}getHex(e=fi){return St.fromWorkingColorSpace(fn.copy(this),e),Math.round(pn(fn.r*255,0,255))*65536+Math.round(pn(fn.g*255,0,255))*256+Math.round(pn(fn.b*255,0,255))}getHexString(e=fi){return("000000"+this.getHex(e).toString(16)).slice(-6)}getHSL(e,t=St.workingColorSpace){St.fromWorkingColorSpace(fn.copy(this),t);const n=fn.r,r=fn.g,s=fn.b,a=Math.max(n,r,s),o=Math.min(n,r,s);let l,c;const u=(o+a)/2;if(o===a)l=0,c=0;else{const h=a-o;switch(c=u<=.5?h/(a+o):h/(2-a-o),a){case n:l=(r-s)/h+(r<s?6:0);break;case r:l=(s-n)/h+2;break;case s:l=(n-r)/h+4;break}l/=6}return e.h=l,e.s=c,e.l=u,e}getRGB(e,t=St.workingColorSpace){return St.fromWorkingColorSpace(fn.copy(this),t),e.r=fn.r,e.g=fn.g,e.b=fn.b,e}getStyle(e=fi){St.fromWorkingColorSpace(fn.copy(this),e);const t=fn.r,n=fn.g,r=fn.b;return e!==fi?`color(${e} ${t.toFixed(3)} ${n.toFixed(3)} ${r.toFixed(3)})`:`rgb(${Math.round(t*255)},${Math.round(n*255)},${Math.round(r*255)})`}offsetHSL(e,t,n){return this.getHSL(Xi),this.setHSL(Xi.h+e,Xi.s+t,Xi.l+n)}add(e){return this.r+=e.r,this.g+=e.g,this.b+=e.b,this}addColors(e,t){return this.r=e.r+t.r,this.g=e.g+t.g,this.b=e.b+t.b,this}addScalar(e){return this.r+=e,this.g+=e,this.b+=e,this}sub(e){return this.r=Math.max(0,this.r-e.r),this.g=Math.max(0,this.g-e.g),this.b=Math.max(0,this.b-e.b),this}multiply(e){return this.r*=e.r,this.g*=e.g,this.b*=e.b,this}multiplyScalar(e){return this.r*=e,this.g*=e,this.b*=e,this}lerp(e,t){return this.r+=(e.r-this.r)*t,this.g+=(e.g-this.g)*t,this.b+=(e.b-this.b)*t,this}lerpColors(e,t,n){return this.r=e.r+(t.r-e.r)*n,this.g=e.g+(t.g-e.g)*n,this.b=e.b+(t.b-e.b)*n,this}lerpHSL(e,t){this.getHSL(Xi),e.getHSL(Ca);const n=sa(Xi.h,Ca.h,t),r=sa(Xi.s,Ca.s,t),s=sa(Xi.l,Ca.l,t);return this.setHSL(n,r,s),this}setFromVector3(e){return this.r=e.x,this.g=e.y,this.b=e.z,this}applyMatrix3(e){const t=this.r,n=this.g,r=this.b,s=e.elements;return this.r=s[0]*t+s[3]*n+s[6]*r,this.g=s[1]*t+s[4]*n+s[7]*r,this.b=s[2]*t+s[5]*n+s[8]*r,this}equals(e){return e.r===this.r&&e.g===this.g&&e.b===this.b}fromArray(e,t=0){return this.r=e[t],this.g=e[t+1],this.b=e[t+2],this}toArray(e=[],t=0){return e[t]=this.r,e[t+1]=this.g,e[t+2]=this.b,e}fromBufferAttribute(e,t){return this.r=e.getX(t),this.g=e.getY(t),this.b=e.getZ(t),this}toJSON(){return this.getHex()}*[Symbol.iterator](){yield this.r,yield this.g,yield this.b}}const fn=new nt;nt.NAMES=$d;let Ym=0;class Dr extends Ds{constructor(){super(),this.isMaterial=!0,Object.defineProperty(this,"id",{value:Ym++}),this.uuid=Li(),this.name="",this.type="Material",this.blending=gs,this.side=er,this.vertexColors=!1,this.opacity=1,this.transparent=!1,this.alphaHash=!1,this.blendSrc=zl,this.blendDst=kl,this.blendEquation=xr,this.blendSrcAlpha=null,this.blendDstAlpha=null,this.blendEquationAlpha=null,this.blendColor=new nt(0,0,0),this.blendAlpha=0,this.depthFunc=ho,this.depthTest=!0,this.depthWrite=!0,this.stencilWriteMask=255,this.stencilFunc=Nu,this.stencilRef=0,this.stencilFuncMask=255,this.stencilFail=Yr,this.stencilZFail=Yr,this.stencilZPass=Yr,this.stencilWrite=!1,this.clippingPlanes=null,this.clipIntersection=!1,this.clipShadows=!1,this.shadowSide=null,this.colorWrite=!0,this.precision=null,this.polygonOffset=!1,this.polygonOffsetFactor=0,this.polygonOffsetUnits=0,this.dithering=!1,this.alphaToCoverage=!1,this.premultipliedAlpha=!1,this.forceSinglePass=!1,this.visible=!0,this.toneMapped=!0,this.userData={},this.version=0,this._alphaTest=0}get alphaTest(){return this._alphaTest}set alphaTest(e){this._alphaTest>0!=e>0&&this.version++,this._alphaTest=e}onBeforeRender(){}onBeforeCompile(){}customProgramCacheKey(){return this.onBeforeCompile.toString()}setValues(e){if(e!==void 0)for(const t in e){const n=e[t];if(n===void 0){console.warn(`THREE.Material: parameter '${t}' has value of undefined.`);continue}const r=this[t];if(r===void 0){console.warn(`THREE.Material: '${t}' is not a property of THREE.${this.type}.`);continue}r&&r.isColor?r.set(n):r&&r.isVector3&&n&&n.isVector3?r.copy(n):this[t]=n}}toJSON(e){const t=e===void 0||typeof e=="string";t&&(e={textures:{},images:{}});const n={metadata:{version:4.6,type:"Material",generator:"Material.toJSON"}};n.uuid=this.uuid,n.type=this.type,this.name!==""&&(n.name=this.name),this.color&&this.color.isColor&&(n.color=this.color.getHex()),this.roughness!==void 0&&(n.roughness=this.roughness),this.metalness!==void 0&&(n.metalness=this.metalness),this.sheen!==void 0&&(n.sheen=this.sheen),this.sheenColor&&this.sheenColor.isColor&&(n.sheenColor=this.sheenColor.getHex()),this.sheenRoughness!==void 0&&(n.sheenRoughness=this.sheenRoughness),this.emissive&&this.emissive.isColor&&(n.emissive=this.emissive.getHex()),this.emissiveIntensity!==void 0&&this.emissiveIntensity!==1&&(n.emissiveIntensity=this.emissiveIntensity),this.specular&&this.specular.isColor&&(n.specular=this.specular.getHex()),this.specularIntensity!==void 0&&(n.specularIntensity=this.specularIntensity),this.specularColor&&this.specularColor.isColor&&(n.specularColor=this.specularColor.getHex()),this.shininess!==void 0&&(n.shininess=this.shininess),this.clearcoat!==void 0&&(n.clearcoat=this.clearcoat),this.clearcoatRoughness!==void 0&&(n.clearcoatRoughness=this.clearcoatRoughness),this.clearcoatMap&&this.clearcoatMap.isTexture&&(n.clearcoatMap=this.clearcoatMap.toJSON(e).uuid),this.clearcoatRoughnessMap&&this.clearcoatRoughnessMap.isTexture&&(n.clearcoatRoughnessMap=this.clearcoatRoughnessMap.toJSON(e).uuid),this.clearcoatNormalMap&&this.clearcoatNormalMap.isTexture&&(n.clearcoatNormalMap=this.clearcoatNormalMap.toJSON(e).uuid,n.clearcoatNormalScale=this.clearcoatNormalScale.toArray()),this.dispersion!==void 0&&(n.dispersion=this.dispersion),this.iridescence!==void 0&&(n.iridescence=this.iridescence),this.iridescenceIOR!==void 0&&(n.iridescenceIOR=this.iridescenceIOR),this.iridescenceThicknessRange!==void 0&&(n.iridescenceThicknessRange=this.iridescenceThicknessRange),this.iridescenceMap&&this.iridescenceMap.isTexture&&(n.iridescenceMap=this.iridescenceMap.toJSON(e).uuid),this.iridescenceThicknessMap&&this.iridescenceThicknessMap.isTexture&&(n.iridescenceThicknessMap=this.iridescenceThicknessMap.toJSON(e).uuid),this.anisotropy!==void 0&&(n.anisotropy=this.anisotropy),this.anisotropyRotation!==void 0&&(n.anisotropyRotation=this.anisotropyRotation),this.anisotropyMap&&this.anisotropyMap.isTexture&&(n.anisotropyMap=this.anisotropyMap.toJSON(e).uuid),this.map&&this.map.isTexture&&(n.map=this.map.toJSON(e).uuid),this.matcap&&this.matcap.isTexture&&(n.matcap=this.matcap.toJSON(e).uuid),this.alphaMap&&this.alphaMap.isTexture&&(n.alphaMap=this.alphaMap.toJSON(e).uuid),this.lightMap&&this.lightMap.isTexture&&(n.lightMap=this.lightMap.toJSON(e).uuid,n.lightMapIntensity=this.lightMapIntensity),this.aoMap&&this.aoMap.isTexture&&(n.aoMap=this.aoMap.toJSON(e).uuid,n.aoMapIntensity=this.aoMapIntensity),this.bumpMap&&this.bumpMap.isTexture&&(n.bumpMap=this.bumpMap.toJSON(e).uuid,n.bumpScale=this.bumpScale),this.normalMap&&this.normalMap.isTexture&&(n.normalMap=this.normalMap.toJSON(e).uuid,n.normalMapType=this.normalMapType,n.normalScale=this.normalScale.toArray()),this.displacementMap&&this.displacementMap.isTexture&&(n.displacementMap=this.displacementMap.toJSON(e).uuid,n.displacementScale=this.displacementScale,n.displacementBias=this.displacementBias),this.roughnessMap&&this.roughnessMap.isTexture&&(n.roughnessMap=this.roughnessMap.toJSON(e).uuid),this.metalnessMap&&this.metalnessMap.isTexture&&(n.metalnessMap=this.metalnessMap.toJSON(e).uuid),this.emissiveMap&&this.emissiveMap.isTexture&&(n.emissiveMap=this.emissiveMap.toJSON(e).uuid),this.specularMap&&this.specularMap.isTexture&&(n.specularMap=this.specularMap.toJSON(e).uuid),this.specularIntensityMap&&this.specularIntensityMap.isTexture&&(n.specularIntensityMap=this.specularIntensityMap.toJSON(e).uuid),this.specularColorMap&&this.specularColorMap.isTexture&&(n.specularColorMap=this.specularColorMap.toJSON(e).uuid),this.envMap&&this.envMap.isTexture&&(n.envMap=this.envMap.toJSON(e).uuid,this.combine!==void 0&&(n.combine=this.combine)),this.envMapRotation!==void 0&&(n.envMapRotation=this.envMapRotation.toArray()),this.envMapIntensity!==void 0&&(n.envMapIntensity=this.envMapIntensity),this.reflectivity!==void 0&&(n.reflectivity=this.reflectivity),this.refractionRatio!==void 0&&(n.refractionRatio=this.refractionRatio),this.gradientMap&&this.gradientMap.isTexture&&(n.gradientMap=this.gradientMap.toJSON(e).uuid),this.transmission!==void 0&&(n.transmission=this.transmission),this.transmissionMap&&this.transmissionMap.isTexture&&(n.transmissionMap=this.transmissionMap.toJSON(e).uuid),this.thickness!==void 0&&(n.thickness=this.thickness),this.thicknessMap&&this.thicknessMap.isTexture&&(n.thicknessMap=this.thicknessMap.toJSON(e).uuid),this.attenuationDistance!==void 0&&this.attenuationDistance!==1/0&&(n.attenuationDistance=this.attenuationDistance),this.attenuationColor!==void 0&&(n.attenuationColor=this.attenuationColor.getHex()),this.size!==void 0&&(n.size=this.size),this.shadowSide!==null&&(n.shadowSide=this.shadowSide),this.sizeAttenuation!==void 0&&(n.sizeAttenuation=this.sizeAttenuation),this.blending!==gs&&(n.blending=this.blending),this.side!==er&&(n.side=this.side),this.vertexColors===!0&&(n.vertexColors=!0),this.opacity<1&&(n.opacity=this.opacity),this.transparent===!0&&(n.transparent=!0),this.blendSrc!==zl&&(n.blendSrc=this.blendSrc),this.blendDst!==kl&&(n.blendDst=this.blendDst),this.blendEquation!==xr&&(n.blendEquation=this.blendEquation),this.blendSrcAlpha!==null&&(n.blendSrcAlpha=this.blendSrcAlpha),this.blendDstAlpha!==null&&(n.blendDstAlpha=this.blendDstAlpha),this.blendEquationAlpha!==null&&(n.blendEquationAlpha=this.blendEquationAlpha),this.blendColor&&this.blendColor.isColor&&(n.blendColor=this.blendColor.getHex()),this.blendAlpha!==0&&(n.blendAlpha=this.blendAlpha),this.depthFunc!==ho&&(n.depthFunc=this.depthFunc),this.depthTest===!1&&(n.depthTest=this.depthTest),this.depthWrite===!1&&(n.depthWrite=this.depthWrite),this.colorWrite===!1&&(n.colorWrite=this.colorWrite),this.stencilWriteMask!==255&&(n.stencilWriteMask=this.stencilWriteMask),this.stencilFunc!==Nu&&(n.stencilFunc=this.stencilFunc),this.stencilRef!==0&&(n.stencilRef=this.stencilRef),this.stencilFuncMask!==255&&(n.stencilFuncMask=this.stencilFuncMask),this.stencilFail!==Yr&&(n.stencilFail=this.stencilFail),this.stencilZFail!==Yr&&(n.stencilZFail=this.stencilZFail),this.stencilZPass!==Yr&&(n.stencilZPass=this.stencilZPass),this.stencilWrite===!0&&(n.stencilWrite=this.stencilWrite),this.rotation!==void 0&&this.rotation!==0&&(n.rotation=this.rotation),this.polygonOffset===!0&&(n.polygonOffset=!0),this.polygonOffsetFactor!==0&&(n.polygonOffsetFactor=this.polygonOffsetFactor),this.polygonOffsetUnits!==0&&(n.polygonOffsetUnits=this.polygonOffsetUnits),this.linewidth!==void 0&&this.linewidth!==1&&(n.linewidth=this.linewidth),this.dashSize!==void 0&&(n.dashSize=this.dashSize),this.gapSize!==void 0&&(n.gapSize=this.gapSize),this.scale!==void 0&&(n.scale=this.scale),this.dithering===!0&&(n.dithering=!0),this.alphaTest>0&&(n.alphaTest=this.alphaTest),this.alphaHash===!0&&(n.alphaHash=!0),this.alphaToCoverage===!0&&(n.alphaToCoverage=!0),this.premultipliedAlpha===!0&&(n.premultipliedAlpha=!0),this.forceSinglePass===!0&&(n.forceSinglePass=!0),this.wireframe===!0&&(n.wireframe=!0),this.wireframeLinewidth>1&&(n.wireframeLinewidth=this.wireframeLinewidth),this.wireframeLinecap!=="round"&&(n.wireframeLinecap=this.wireframeLinecap),this.wireframeLinejoin!=="round"&&(n.wireframeLinejoin=this.wireframeLinejoin),this.flatShading===!0&&(n.flatShading=!0),this.visible===!1&&(n.visible=!1),this.toneMapped===!1&&(n.toneMapped=!1),this.fog===!1&&(n.fog=!1),Object.keys(this.userData).length>0&&(n.userData=this.userData);function r(s){const a=[];for(const o in s){const l=s[o];delete l.metadata,a.push(l)}return a}if(t){const s=r(e.textures),a=r(e.images);s.length>0&&(n.textures=s),a.length>0&&(n.images=a)}return n}clone(){return new this.constructor().copy(this)}copy(e){this.name=e.name,this.blending=e.blending,this.side=e.side,this.vertexColors=e.vertexColors,this.opacity=e.opacity,this.transparent=e.transparent,this.blendSrc=e.blendSrc,this.blendDst=e.blendDst,this.blendEquation=e.blendEquation,this.blendSrcAlpha=e.blendSrcAlpha,this.blendDstAlpha=e.blendDstAlpha,this.blendEquationAlpha=e.blendEquationAlpha,this.blendColor.copy(e.blendColor),this.blendAlpha=e.blendAlpha,this.depthFunc=e.depthFunc,this.depthTest=e.depthTest,this.depthWrite=e.depthWrite,this.stencilWriteMask=e.stencilWriteMask,this.stencilFunc=e.stencilFunc,this.stencilRef=e.stencilRef,this.stencilFuncMask=e.stencilFuncMask,this.stencilFail=e.stencilFail,this.stencilZFail=e.stencilZFail,this.stencilZPass=e.stencilZPass,this.stencilWrite=e.stencilWrite;const t=e.clippingPlanes;let n=null;if(t!==null){const r=t.length;n=new Array(r);for(let s=0;s!==r;++s)n[s]=t[s].clone()}return this.clippingPlanes=n,this.clipIntersection=e.clipIntersection,this.clipShadows=e.clipShadows,this.shadowSide=e.shadowSide,this.colorWrite=e.colorWrite,this.precision=e.precision,this.polygonOffset=e.polygonOffset,this.polygonOffsetFactor=e.polygonOffsetFactor,this.polygonOffsetUnits=e.polygonOffsetUnits,this.dithering=e.dithering,this.alphaTest=e.alphaTest,this.alphaHash=e.alphaHash,this.alphaToCoverage=e.alphaToCoverage,this.premultipliedAlpha=e.premultipliedAlpha,this.forceSinglePass=e.forceSinglePass,this.visible=e.visible,this.toneMapped=e.toneMapped,this.userData=JSON.parse(JSON.stringify(e.userData)),this}dispose(){this.dispatchEvent({type:"dispose"})}set needsUpdate(e){e===!0&&this.version++}onBuild(){console.warn("Material: onBuild() has been removed.")}}class vo extends Dr{constructor(e){super(),this.isMeshBasicMaterial=!0,this.type="MeshBasicMaterial",this.color=new nt(16777215),this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.specularMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new gi,this.combine=Pd,this.reflectivity=1,this.refractionRatio=.98,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.lightMap=e.lightMap,this.lightMapIntensity=e.lightMapIntensity,this.aoMap=e.aoMap,this.aoMapIntensity=e.aoMapIntensity,this.specularMap=e.specularMap,this.alphaMap=e.alphaMap,this.envMap=e.envMap,this.envMapRotation.copy(e.envMapRotation),this.combine=e.combine,this.reflectivity=e.reflectivity,this.refractionRatio=e.refractionRatio,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.wireframeLinecap=e.wireframeLinecap,this.wireframeLinejoin=e.wireframeLinejoin,this.fog=e.fog,this}}const Xt=new V,Pa=new Xe;class Xn{constructor(e,t,n=!1){if(Array.isArray(e))throw new TypeError("THREE.BufferAttribute: array should be a Typed Array.");this.isBufferAttribute=!0,this.name="",this.array=e,this.itemSize=t,this.count=e!==void 0?e.length/t:0,this.normalized=n,this.usage=_c,this._updateRange={offset:0,count:-1},this.updateRanges=[],this.gpuType=Ci,this.version=0}onUploadCallback(){}set needsUpdate(e){e===!0&&this.version++}get updateRange(){return xs("THREE.BufferAttribute: updateRange() is deprecated and will be removed in r169. Use addUpdateRange() instead."),this._updateRange}setUsage(e){return this.usage=e,this}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}copy(e){return this.name=e.name,this.array=new e.array.constructor(e.array),this.itemSize=e.itemSize,this.count=e.count,this.normalized=e.normalized,this.usage=e.usage,this.gpuType=e.gpuType,this}copyAt(e,t,n){e*=this.itemSize,n*=t.itemSize;for(let r=0,s=this.itemSize;r<s;r++)this.array[e+r]=t.array[n+r];return this}copyArray(e){return this.array.set(e),this}applyMatrix3(e){if(this.itemSize===2)for(let t=0,n=this.count;t<n;t++)Pa.fromBufferAttribute(this,t),Pa.applyMatrix3(e),this.setXY(t,Pa.x,Pa.y);else if(this.itemSize===3)for(let t=0,n=this.count;t<n;t++)Xt.fromBufferAttribute(this,t),Xt.applyMatrix3(e),this.setXYZ(t,Xt.x,Xt.y,Xt.z);return this}applyMatrix4(e){for(let t=0,n=this.count;t<n;t++)Xt.fromBufferAttribute(this,t),Xt.applyMatrix4(e),this.setXYZ(t,Xt.x,Xt.y,Xt.z);return this}applyNormalMatrix(e){for(let t=0,n=this.count;t<n;t++)Xt.fromBufferAttribute(this,t),Xt.applyNormalMatrix(e),this.setXYZ(t,Xt.x,Xt.y,Xt.z);return this}transformDirection(e){for(let t=0,n=this.count;t<n;t++)Xt.fromBufferAttribute(this,t),Xt.transformDirection(e),this.setXYZ(t,Xt.x,Xt.y,Xt.z);return this}set(e,t=0){return this.array.set(e,t),this}getComponent(e,t){let n=this.array[e*this.itemSize+t];return this.normalized&&(n=ni(n,this.array)),n}setComponent(e,t,n){return this.normalized&&(n=bt(n,this.array)),this.array[e*this.itemSize+t]=n,this}getX(e){let t=this.array[e*this.itemSize];return this.normalized&&(t=ni(t,this.array)),t}setX(e,t){return this.normalized&&(t=bt(t,this.array)),this.array[e*this.itemSize]=t,this}getY(e){let t=this.array[e*this.itemSize+1];return this.normalized&&(t=ni(t,this.array)),t}setY(e,t){return this.normalized&&(t=bt(t,this.array)),this.array[e*this.itemSize+1]=t,this}getZ(e){let t=this.array[e*this.itemSize+2];return this.normalized&&(t=ni(t,this.array)),t}setZ(e,t){return this.normalized&&(t=bt(t,this.array)),this.array[e*this.itemSize+2]=t,this}getW(e){let t=this.array[e*this.itemSize+3];return this.normalized&&(t=ni(t,this.array)),t}setW(e,t){return this.normalized&&(t=bt(t,this.array)),this.array[e*this.itemSize+3]=t,this}setXY(e,t,n){return e*=this.itemSize,this.normalized&&(t=bt(t,this.array),n=bt(n,this.array)),this.array[e+0]=t,this.array[e+1]=n,this}setXYZ(e,t,n,r){return e*=this.itemSize,this.normalized&&(t=bt(t,this.array),n=bt(n,this.array),r=bt(r,this.array)),this.array[e+0]=t,this.array[e+1]=n,this.array[e+2]=r,this}setXYZW(e,t,n,r,s){return e*=this.itemSize,this.normalized&&(t=bt(t,this.array),n=bt(n,this.array),r=bt(r,this.array),s=bt(s,this.array)),this.array[e+0]=t,this.array[e+1]=n,this.array[e+2]=r,this.array[e+3]=s,this}onUpload(e){return this.onUploadCallback=e,this}clone(){return new this.constructor(this.array,this.itemSize).copy(this)}toJSON(){const e={itemSize:this.itemSize,type:this.array.constructor.name,array:Array.from(this.array),normalized:this.normalized};return this.name!==""&&(e.name=this.name),this.usage!==_c&&(e.usage=this.usage),e}}class jd extends Xn{constructor(e,t,n){super(new Uint16Array(e),t,n)}}class Kd extends Xn{constructor(e,t,n){super(new Uint32Array(e),t,n)}}class wn extends Xn{constructor(e,t,n){super(new Float32Array(e),t,n)}}let qm=0;const kn=new zt,_l=new Kt,ns=new V,Un=new da,$s=new da,an=new V;class gn extends Ds{constructor(){super(),this.isBufferGeometry=!0,Object.defineProperty(this,"id",{value:qm++}),this.uuid=Li(),this.name="",this.type="BufferGeometry",this.index=null,this.attributes={},this.morphAttributes={},this.morphTargetsRelative=!1,this.groups=[],this.boundingBox=null,this.boundingSphere=null,this.drawRange={start:0,count:1/0},this.userData={}}getIndex(){return this.index}setIndex(e){return Array.isArray(e)?this.index=new(Xd(e)?Kd:jd)(e,1):this.index=e,this}getAttribute(e){return this.attributes[e]}setAttribute(e,t){return this.attributes[e]=t,this}deleteAttribute(e){return delete this.attributes[e],this}hasAttribute(e){return this.attributes[e]!==void 0}addGroup(e,t,n=0){this.groups.push({start:e,count:t,materialIndex:n})}clearGroups(){this.groups=[]}setDrawRange(e,t){this.drawRange.start=e,this.drawRange.count=t}applyMatrix4(e){const t=this.attributes.position;t!==void 0&&(t.applyMatrix4(e),t.needsUpdate=!0);const n=this.attributes.normal;if(n!==void 0){const s=new rt().getNormalMatrix(e);n.applyNormalMatrix(s),n.needsUpdate=!0}const r=this.attributes.tangent;return r!==void 0&&(r.transformDirection(e),r.needsUpdate=!0),this.boundingBox!==null&&this.computeBoundingBox(),this.boundingSphere!==null&&this.computeBoundingSphere(),this}applyQuaternion(e){return kn.makeRotationFromQuaternion(e),this.applyMatrix4(kn),this}rotateX(e){return kn.makeRotationX(e),this.applyMatrix4(kn),this}rotateY(e){return kn.makeRotationY(e),this.applyMatrix4(kn),this}rotateZ(e){return kn.makeRotationZ(e),this.applyMatrix4(kn),this}translate(e,t,n){return kn.makeTranslation(e,t,n),this.applyMatrix4(kn),this}scale(e,t,n){return kn.makeScale(e,t,n),this.applyMatrix4(kn),this}lookAt(e){return _l.lookAt(e),_l.updateMatrix(),this.applyMatrix4(_l.matrix),this}center(){return this.computeBoundingBox(),this.boundingBox.getCenter(ns).negate(),this.translate(ns.x,ns.y,ns.z),this}setFromPoints(e){const t=[];for(let n=0,r=e.length;n<r;n++){const s=e[n];t.push(s.x,s.y,s.z||0)}return this.setAttribute("position",new wn(t,3)),this}computeBoundingBox(){this.boundingBox===null&&(this.boundingBox=new da);const e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingBox(): GLBufferAttribute requires a manual bounding box.",this),this.boundingBox.set(new V(-1/0,-1/0,-1/0),new V(1/0,1/0,1/0));return}if(e!==void 0){if(this.boundingBox.setFromBufferAttribute(e),t)for(let n=0,r=t.length;n<r;n++){const s=t[n];Un.setFromBufferAttribute(s),this.morphTargetsRelative?(an.addVectors(this.boundingBox.min,Un.min),this.boundingBox.expandByPoint(an),an.addVectors(this.boundingBox.max,Un.max),this.boundingBox.expandByPoint(an)):(this.boundingBox.expandByPoint(Un.min),this.boundingBox.expandByPoint(Un.max))}}else this.boundingBox.makeEmpty();(isNaN(this.boundingBox.min.x)||isNaN(this.boundingBox.min.y)||isNaN(this.boundingBox.min.z))&&console.error('THREE.BufferGeometry.computeBoundingBox(): Computed min/max have NaN values. The "position" attribute is likely to have NaN values.',this)}computeBoundingSphere(){this.boundingSphere===null&&(this.boundingSphere=new Co);const e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingSphere(): GLBufferAttribute requires a manual bounding sphere.",this),this.boundingSphere.set(new V,1/0);return}if(e){const n=this.boundingSphere.center;if(Un.setFromBufferAttribute(e),t)for(let s=0,a=t.length;s<a;s++){const o=t[s];$s.setFromBufferAttribute(o),this.morphTargetsRelative?(an.addVectors(Un.min,$s.min),Un.expandByPoint(an),an.addVectors(Un.max,$s.max),Un.expandByPoint(an)):(Un.expandByPoint($s.min),Un.expandByPoint($s.max))}Un.getCenter(n);let r=0;for(let s=0,a=e.count;s<a;s++)an.fromBufferAttribute(e,s),r=Math.max(r,n.distanceToSquared(an));if(t)for(let s=0,a=t.length;s<a;s++){const o=t[s],l=this.morphTargetsRelative;for(let c=0,u=o.count;c<u;c++)an.fromBufferAttribute(o,c),l&&(ns.fromBufferAttribute(e,c),an.add(ns)),r=Math.max(r,n.distanceToSquared(an))}this.boundingSphere.radius=Math.sqrt(r),isNaN(this.boundingSphere.radius)&&console.error('THREE.BufferGeometry.computeBoundingSphere(): Computed radius is NaN. The "position" attribute is likely to have NaN values.',this)}}computeTangents(){const e=this.index,t=this.attributes;if(e===null||t.position===void 0||t.normal===void 0||t.uv===void 0){console.error("THREE.BufferGeometry: .computeTangents() failed. Missing required attributes (index, position, normal or uv)");return}const n=t.position,r=t.normal,s=t.uv;this.hasAttribute("tangent")===!1&&this.setAttribute("tangent",new Xn(new Float32Array(4*n.count),4));const a=this.getAttribute("tangent"),o=[],l=[];for(let B=0;B<n.count;B++)o[B]=new V,l[B]=new V;const c=new V,u=new V,h=new V,d=new Xe,m=new Xe,_=new Xe,v=new V,p=new V;function f(B,w,x){c.fromBufferAttribute(n,B),u.fromBufferAttribute(n,w),h.fromBufferAttribute(n,x),d.fromBufferAttribute(s,B),m.fromBufferAttribute(s,w),_.fromBufferAttribute(s,x),u.sub(c),h.sub(c),m.sub(d),_.sub(d);const R=1/(m.x*_.y-_.x*m.y);isFinite(R)&&(v.copy(u).multiplyScalar(_.y).addScaledVector(h,-m.y).multiplyScalar(R),p.copy(h).multiplyScalar(m.x).addScaledVector(u,-_.x).multiplyScalar(R),o[B].add(v),o[w].add(v),o[x].add(v),l[B].add(p),l[w].add(p),l[x].add(p))}let E=this.groups;E.length===0&&(E=[{start:0,count:e.count}]);for(let B=0,w=E.length;B<w;++B){const x=E[B],R=x.start,j=x.count;for(let O=R,K=R+j;O<K;O+=3)f(e.getX(O+0),e.getX(O+1),e.getX(O+2))}const y=new V,T=new V,z=new V,C=new V;function D(B){z.fromBufferAttribute(r,B),C.copy(z);const w=o[B];y.copy(w),y.sub(z.multiplyScalar(z.dot(w))).normalize(),T.crossVectors(C,w);const R=T.dot(l[B])<0?-1:1;a.setXYZW(B,y.x,y.y,y.z,R)}for(let B=0,w=E.length;B<w;++B){const x=E[B],R=x.start,j=x.count;for(let O=R,K=R+j;O<K;O+=3)D(e.getX(O+0)),D(e.getX(O+1)),D(e.getX(O+2))}}computeVertexNormals(){const e=this.index,t=this.getAttribute("position");if(t!==void 0){let n=this.getAttribute("normal");if(n===void 0)n=new Xn(new Float32Array(t.count*3),3),this.setAttribute("normal",n);else for(let d=0,m=n.count;d<m;d++)n.setXYZ(d,0,0,0);const r=new V,s=new V,a=new V,o=new V,l=new V,c=new V,u=new V,h=new V;if(e)for(let d=0,m=e.count;d<m;d+=3){const _=e.getX(d+0),v=e.getX(d+1),p=e.getX(d+2);r.fromBufferAttribute(t,_),s.fromBufferAttribute(t,v),a.fromBufferAttribute(t,p),u.subVectors(a,s),h.subVectors(r,s),u.cross(h),o.fromBufferAttribute(n,_),l.fromBufferAttribute(n,v),c.fromBufferAttribute(n,p),o.add(u),l.add(u),c.add(u),n.setXYZ(_,o.x,o.y,o.z),n.setXYZ(v,l.x,l.y,l.z),n.setXYZ(p,c.x,c.y,c.z)}else for(let d=0,m=t.count;d<m;d+=3)r.fromBufferAttribute(t,d+0),s.fromBufferAttribute(t,d+1),a.fromBufferAttribute(t,d+2),u.subVectors(a,s),h.subVectors(r,s),u.cross(h),n.setXYZ(d+0,u.x,u.y,u.z),n.setXYZ(d+1,u.x,u.y,u.z),n.setXYZ(d+2,u.x,u.y,u.z);this.normalizeNormals(),n.needsUpdate=!0}}normalizeNormals(){const e=this.attributes.normal;for(let t=0,n=e.count;t<n;t++)an.fromBufferAttribute(e,t),an.normalize(),e.setXYZ(t,an.x,an.y,an.z)}toNonIndexed(){function e(o,l){const c=o.array,u=o.itemSize,h=o.normalized,d=new c.constructor(l.length*u);let m=0,_=0;for(let v=0,p=l.length;v<p;v++){o.isInterleavedBufferAttribute?m=l[v]*o.data.stride+o.offset:m=l[v]*u;for(let f=0;f<u;f++)d[_++]=c[m++]}return new Xn(d,u,h)}if(this.index===null)return console.warn("THREE.BufferGeometry.toNonIndexed(): BufferGeometry is already non-indexed."),this;const t=new gn,n=this.index.array,r=this.attributes;for(const o in r){const l=r[o],c=e(l,n);t.setAttribute(o,c)}const s=this.morphAttributes;for(const o in s){const l=[],c=s[o];for(let u=0,h=c.length;u<h;u++){const d=c[u],m=e(d,n);l.push(m)}t.morphAttributes[o]=l}t.morphTargetsRelative=this.morphTargetsRelative;const a=this.groups;for(let o=0,l=a.length;o<l;o++){const c=a[o];t.addGroup(c.start,c.count,c.materialIndex)}return t}toJSON(){const e={metadata:{version:4.6,type:"BufferGeometry",generator:"BufferGeometry.toJSON"}};if(e.uuid=this.uuid,e.type=this.type,this.name!==""&&(e.name=this.name),Object.keys(this.userData).length>0&&(e.userData=this.userData),this.parameters!==void 0){const l=this.parameters;for(const c in l)l[c]!==void 0&&(e[c]=l[c]);return e}e.data={attributes:{}};const t=this.index;t!==null&&(e.data.index={type:t.array.constructor.name,array:Array.prototype.slice.call(t.array)});const n=this.attributes;for(const l in n){const c=n[l];e.data.attributes[l]=c.toJSON(e.data)}const r={};let s=!1;for(const l in this.morphAttributes){const c=this.morphAttributes[l],u=[];for(let h=0,d=c.length;h<d;h++){const m=c[h];u.push(m.toJSON(e.data))}u.length>0&&(r[l]=u,s=!0)}s&&(e.data.morphAttributes=r,e.data.morphTargetsRelative=this.morphTargetsRelative);const a=this.groups;a.length>0&&(e.data.groups=JSON.parse(JSON.stringify(a)));const o=this.boundingSphere;return o!==null&&(e.data.boundingSphere={center:o.center.toArray(),radius:o.radius}),e}clone(){return new this.constructor().copy(this)}copy(e){this.index=null,this.attributes={},this.morphAttributes={},this.groups=[],this.boundingBox=null,this.boundingSphere=null;const t={};this.name=e.name;const n=e.index;n!==null&&this.setIndex(n.clone(t));const r=e.attributes;for(const c in r){const u=r[c];this.setAttribute(c,u.clone(t))}const s=e.morphAttributes;for(const c in s){const u=[],h=s[c];for(let d=0,m=h.length;d<m;d++)u.push(h[d].clone(t));this.morphAttributes[c]=u}this.morphTargetsRelative=e.morphTargetsRelative;const a=e.groups;for(let c=0,u=a.length;c<u;c++){const h=a[c];this.addGroup(h.start,h.count,h.materialIndex)}const o=e.boundingBox;o!==null&&(this.boundingBox=o.clone());const l=e.boundingSphere;return l!==null&&(this.boundingSphere=l.clone()),this.drawRange.start=e.drawRange.start,this.drawRange.count=e.drawRange.count,this.userData=e.userData,this}dispose(){this.dispatchEvent({type:"dispose"})}}const Ku=new zt,dr=new Po,La=new Co,Zu=new V,is=new V,rs=new V,ss=new V,vl=new V,Da=new V,Ia=new Xe,Ua=new Xe,Na=new Xe,Ju=new V,Qu=new V,eh=new V,Fa=new V,Oa=new V;class Rn extends Kt{constructor(e=new gn,t=new vo){super(),this.isMesh=!0,this.type="Mesh",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),e.morphTargetInfluences!==void 0&&(this.morphTargetInfluences=e.morphTargetInfluences.slice()),e.morphTargetDictionary!==void 0&&(this.morphTargetDictionary=Object.assign({},e.morphTargetDictionary)),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const r=t[n[0]];if(r!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let s=0,a=r.length;s<a;s++){const o=r[s].name||String(s);this.morphTargetInfluences.push(0),this.morphTargetDictionary[o]=s}}}}getVertexPosition(e,t){const n=this.geometry,r=n.attributes.position,s=n.morphAttributes.position,a=n.morphTargetsRelative;t.fromBufferAttribute(r,e);const o=this.morphTargetInfluences;if(s&&o){Da.set(0,0,0);for(let l=0,c=s.length;l<c;l++){const u=o[l],h=s[l];u!==0&&(vl.fromBufferAttribute(h,e),a?Da.addScaledVector(vl,u):Da.addScaledVector(vl.sub(t),u))}t.add(Da)}return t}raycast(e,t){const n=this.geometry,r=this.material,s=this.matrixWorld;r!==void 0&&(n.boundingSphere===null&&n.computeBoundingSphere(),La.copy(n.boundingSphere),La.applyMatrix4(s),dr.copy(e.ray).recast(e.near),!(La.containsPoint(dr.origin)===!1&&(dr.intersectSphere(La,Zu)===null||dr.origin.distanceToSquared(Zu)>(e.far-e.near)**2))&&(Ku.copy(s).invert(),dr.copy(e.ray).applyMatrix4(Ku),!(n.boundingBox!==null&&dr.intersectsBox(n.boundingBox)===!1)&&this._computeIntersections(e,t,dr)))}_computeIntersections(e,t,n){let r;const s=this.geometry,a=this.material,o=s.index,l=s.attributes.position,c=s.attributes.uv,u=s.attributes.uv1,h=s.attributes.normal,d=s.groups,m=s.drawRange;if(o!==null)if(Array.isArray(a))for(let _=0,v=d.length;_<v;_++){const p=d[_],f=a[p.materialIndex],E=Math.max(p.start,m.start),y=Math.min(o.count,Math.min(p.start+p.count,m.start+m.count));for(let T=E,z=y;T<z;T+=3){const C=o.getX(T),D=o.getX(T+1),B=o.getX(T+2);r=Ba(this,f,e,n,c,u,h,C,D,B),r&&(r.faceIndex=Math.floor(T/3),r.face.materialIndex=p.materialIndex,t.push(r))}}else{const _=Math.max(0,m.start),v=Math.min(o.count,m.start+m.count);for(let p=_,f=v;p<f;p+=3){const E=o.getX(p),y=o.getX(p+1),T=o.getX(p+2);r=Ba(this,a,e,n,c,u,h,E,y,T),r&&(r.faceIndex=Math.floor(p/3),t.push(r))}}else if(l!==void 0)if(Array.isArray(a))for(let _=0,v=d.length;_<v;_++){const p=d[_],f=a[p.materialIndex],E=Math.max(p.start,m.start),y=Math.min(l.count,Math.min(p.start+p.count,m.start+m.count));for(let T=E,z=y;T<z;T+=3){const C=T,D=T+1,B=T+2;r=Ba(this,f,e,n,c,u,h,C,D,B),r&&(r.faceIndex=Math.floor(T/3),r.face.materialIndex=p.materialIndex,t.push(r))}}else{const _=Math.max(0,m.start),v=Math.min(l.count,m.start+m.count);for(let p=_,f=v;p<f;p+=3){const E=p,y=p+1,T=p+2;r=Ba(this,a,e,n,c,u,h,E,y,T),r&&(r.faceIndex=Math.floor(p/3),t.push(r))}}}}function $m(i,e,t,n,r,s,a,o){let l;if(e.side===Cn?l=n.intersectTriangle(a,s,r,!0,o):l=n.intersectTriangle(r,s,a,e.side===er,o),l===null)return null;Oa.copy(o),Oa.applyMatrix4(i.matrixWorld);const c=t.ray.origin.distanceTo(Oa);return c<t.near||c>t.far?null:{distance:c,point:Oa.clone(),object:i}}function Ba(i,e,t,n,r,s,a,o,l,c){i.getVertexPosition(o,is),i.getVertexPosition(l,rs),i.getVertexPosition(c,ss);const u=$m(i,e,t,n,is,rs,ss,Fa);if(u){r&&(Ia.fromBufferAttribute(r,o),Ua.fromBufferAttribute(r,l),Na.fromBufferAttribute(r,c),u.uv=Gn.getInterpolation(Fa,is,rs,ss,Ia,Ua,Na,new Xe)),s&&(Ia.fromBufferAttribute(s,o),Ua.fromBufferAttribute(s,l),Na.fromBufferAttribute(s,c),u.uv1=Gn.getInterpolation(Fa,is,rs,ss,Ia,Ua,Na,new Xe)),a&&(Ju.fromBufferAttribute(a,o),Qu.fromBufferAttribute(a,l),eh.fromBufferAttribute(a,c),u.normal=Gn.getInterpolation(Fa,is,rs,ss,Ju,Qu,eh,new V),u.normal.dot(n.direction)>0&&u.normal.multiplyScalar(-1));const h={a:o,b:l,c,normal:new V,materialIndex:0};Gn.getNormal(is,rs,ss,h.normal),u.face=h}return u}class Qi extends gn{constructor(e=1,t=1,n=1,r=1,s=1,a=1){super(),this.type="BoxGeometry",this.parameters={width:e,height:t,depth:n,widthSegments:r,heightSegments:s,depthSegments:a};const o=this;r=Math.floor(r),s=Math.floor(s),a=Math.floor(a);const l=[],c=[],u=[],h=[];let d=0,m=0;_("z","y","x",-1,-1,n,t,e,a,s,0),_("z","y","x",1,-1,n,t,-e,a,s,1),_("x","z","y",1,1,e,n,t,r,a,2),_("x","z","y",1,-1,e,n,-t,r,a,3),_("x","y","z",1,-1,e,t,n,r,s,4),_("x","y","z",-1,-1,e,t,-n,r,s,5),this.setIndex(l),this.setAttribute("position",new wn(c,3)),this.setAttribute("normal",new wn(u,3)),this.setAttribute("uv",new wn(h,2));function _(v,p,f,E,y,T,z,C,D,B,w){const x=T/D,R=z/B,j=T/2,O=z/2,K=C/2,W=D+1,J=B+1;let Y=0,ee=0;const pe=new V;for(let ue=0;ue<J;ue++){const _e=ue*R-O;for(let be=0;be<W;be++){const ve=be*x-j;pe[v]=ve*E,pe[p]=_e*y,pe[f]=K,c.push(pe.x,pe.y,pe.z),pe[v]=0,pe[p]=0,pe[f]=C>0?1:-1,u.push(pe.x,pe.y,pe.z),h.push(be/D),h.push(1-ue/B),Y+=1}}for(let ue=0;ue<B;ue++)for(let _e=0;_e<D;_e++){const be=d+_e+W*ue,ve=d+_e+W*(ue+1),te=d+(_e+1)+W*(ue+1),le=d+(_e+1)+W*ue;l.push(be,ve,le),l.push(ve,te,le),ee+=6}o.addGroup(m,ee,w),m+=ee,d+=Y}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Qi(e.width,e.height,e.depth,e.widthSegments,e.heightSegments,e.depthSegments)}}function As(i){const e={};for(const t in i){e[t]={};for(const n in i[t]){const r=i[t][n];r&&(r.isColor||r.isMatrix3||r.isMatrix4||r.isVector2||r.isVector3||r.isVector4||r.isTexture||r.isQuaternion)?r.isRenderTargetTexture?(console.warn("UniformsUtils: Textures of render targets cannot be cloned via cloneUniforms() or mergeUniforms()."),e[t][n]=null):e[t][n]=r.clone():Array.isArray(r)?e[t][n]=r.slice():e[t][n]=r}}return e}function yn(i){const e={};for(let t=0;t<i.length;t++){const n=As(i[t]);for(const r in n)e[r]=n[r]}return e}function jm(i){const e=[];for(let t=0;t<i.length;t++)e.push(i[t].clone());return e}function Zd(i){const e=i.getRenderTarget();return e===null?i.outputColorSpace:e.isXRRenderTarget===!0?e.texture.colorSpace:St.workingColorSpace}const Km={clone:As,merge:yn};var Zm=`void main() {
	gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
}`,Jm=`void main() {
	gl_FragColor = vec4( 1.0, 0.0, 0.0, 1.0 );
}`;class tr extends Dr{constructor(e){super(),this.isShaderMaterial=!0,this.type="ShaderMaterial",this.defines={},this.uniforms={},this.uniformsGroups=[],this.vertexShader=Zm,this.fragmentShader=Jm,this.linewidth=1,this.wireframe=!1,this.wireframeLinewidth=1,this.fog=!1,this.lights=!1,this.clipping=!1,this.forceSinglePass=!0,this.extensions={clipCullDistance:!1,multiDraw:!1},this.defaultAttributeValues={color:[1,1,1],uv:[0,0],uv1:[0,0]},this.index0AttributeName=void 0,this.uniformsNeedUpdate=!1,this.glslVersion=null,e!==void 0&&this.setValues(e)}copy(e){return super.copy(e),this.fragmentShader=e.fragmentShader,this.vertexShader=e.vertexShader,this.uniforms=As(e.uniforms),this.uniformsGroups=jm(e.uniformsGroups),this.defines=Object.assign({},e.defines),this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.fog=e.fog,this.lights=e.lights,this.clipping=e.clipping,this.extensions=Object.assign({},e.extensions),this.glslVersion=e.glslVersion,this}toJSON(e){const t=super.toJSON(e);t.glslVersion=this.glslVersion,t.uniforms={};for(const r in this.uniforms){const a=this.uniforms[r].value;a&&a.isTexture?t.uniforms[r]={type:"t",value:a.toJSON(e).uuid}:a&&a.isColor?t.uniforms[r]={type:"c",value:a.getHex()}:a&&a.isVector2?t.uniforms[r]={type:"v2",value:a.toArray()}:a&&a.isVector3?t.uniforms[r]={type:"v3",value:a.toArray()}:a&&a.isVector4?t.uniforms[r]={type:"v4",value:a.toArray()}:a&&a.isMatrix3?t.uniforms[r]={type:"m3",value:a.toArray()}:a&&a.isMatrix4?t.uniforms[r]={type:"m4",value:a.toArray()}:t.uniforms[r]={value:a}}Object.keys(this.defines).length>0&&(t.defines=this.defines),t.vertexShader=this.vertexShader,t.fragmentShader=this.fragmentShader,t.lights=this.lights,t.clipping=this.clipping;const n={};for(const r in this.extensions)this.extensions[r]===!0&&(n[r]=!0);return Object.keys(n).length>0&&(t.extensions=n),t}}class kc extends Kt{constructor(){super(),this.isCamera=!0,this.type="Camera",this.matrixWorldInverse=new zt,this.projectionMatrix=new zt,this.projectionMatrixInverse=new zt,this.coordinateSystem=Pi}copy(e,t){return super.copy(e,t),this.matrixWorldInverse.copy(e.matrixWorldInverse),this.projectionMatrix.copy(e.projectionMatrix),this.projectionMatrixInverse.copy(e.projectionMatrixInverse),this.coordinateSystem=e.coordinateSystem,this}getWorldDirection(e){return super.getWorldDirection(e).negate()}updateMatrixWorld(e){super.updateMatrixWorld(e),this.matrixWorldInverse.copy(this.matrixWorld).invert()}updateWorldMatrix(e,t){super.updateWorldMatrix(e,t),this.matrixWorldInverse.copy(this.matrixWorld).invert()}clone(){return new this.constructor().copy(this)}}const Yi=new V,th=new Xe,nh=new Xe;class En extends kc{constructor(e=50,t=1,n=.1,r=2e3){super(),this.isPerspectiveCamera=!0,this.type="PerspectiveCamera",this.fov=e,this.zoom=1,this.near=n,this.far=r,this.focus=10,this.aspect=t,this.view=null,this.filmGauge=35,this.filmOffset=0,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.fov=e.fov,this.zoom=e.zoom,this.near=e.near,this.far=e.far,this.focus=e.focus,this.aspect=e.aspect,this.view=e.view===null?null:Object.assign({},e.view),this.filmGauge=e.filmGauge,this.filmOffset=e.filmOffset,this}setFocalLength(e){const t=.5*this.getFilmHeight()/e;this.fov=ca*2*Math.atan(t),this.updateProjectionMatrix()}getFocalLength(){const e=Math.tan(vs*.5*this.fov);return .5*this.getFilmHeight()/e}getEffectiveFOV(){return ca*2*Math.atan(Math.tan(vs*.5*this.fov)/this.zoom)}getFilmWidth(){return this.filmGauge*Math.min(this.aspect,1)}getFilmHeight(){return this.filmGauge/Math.max(this.aspect,1)}getViewBounds(e,t,n){Yi.set(-1,-1,.5).applyMatrix4(this.projectionMatrixInverse),t.set(Yi.x,Yi.y).multiplyScalar(-e/Yi.z),Yi.set(1,1,.5).applyMatrix4(this.projectionMatrixInverse),n.set(Yi.x,Yi.y).multiplyScalar(-e/Yi.z)}getViewSize(e,t){return this.getViewBounds(e,th,nh),t.subVectors(nh,th)}setViewOffset(e,t,n,r,s,a){this.aspect=e/t,this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=n,this.view.offsetY=r,this.view.width=s,this.view.height=a,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const e=this.near;let t=e*Math.tan(vs*.5*this.fov)/this.zoom,n=2*t,r=this.aspect*n,s=-.5*r;const a=this.view;if(this.view!==null&&this.view.enabled){const l=a.fullWidth,c=a.fullHeight;s+=a.offsetX*r/l,t-=a.offsetY*n/c,r*=a.width/l,n*=a.height/c}const o=this.filmOffset;o!==0&&(s+=e*o/this.getFilmWidth()),this.projectionMatrix.makePerspective(s,s+r,t,t-n,e,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){const t=super.toJSON(e);return t.object.fov=this.fov,t.object.zoom=this.zoom,t.object.near=this.near,t.object.far=this.far,t.object.focus=this.focus,t.object.aspect=this.aspect,this.view!==null&&(t.object.view=Object.assign({},this.view)),t.object.filmGauge=this.filmGauge,t.object.filmOffset=this.filmOffset,t}}const as=-90,os=1;class Qm extends Kt{constructor(e,t,n){super(),this.type="CubeCamera",this.renderTarget=n,this.coordinateSystem=null,this.activeMipmapLevel=0;const r=new En(as,os,e,t);r.layers=this.layers,this.add(r);const s=new En(as,os,e,t);s.layers=this.layers,this.add(s);const a=new En(as,os,e,t);a.layers=this.layers,this.add(a);const o=new En(as,os,e,t);o.layers=this.layers,this.add(o);const l=new En(as,os,e,t);l.layers=this.layers,this.add(l);const c=new En(as,os,e,t);c.layers=this.layers,this.add(c)}updateCoordinateSystem(){const e=this.coordinateSystem,t=this.children.concat(),[n,r,s,a,o,l]=t;for(const c of t)this.remove(c);if(e===Pi)n.up.set(0,1,0),n.lookAt(1,0,0),r.up.set(0,1,0),r.lookAt(-1,0,0),s.up.set(0,0,-1),s.lookAt(0,1,0),a.up.set(0,0,1),a.lookAt(0,-1,0),o.up.set(0,1,0),o.lookAt(0,0,1),l.up.set(0,1,0),l.lookAt(0,0,-1);else if(e===go)n.up.set(0,-1,0),n.lookAt(-1,0,0),r.up.set(0,-1,0),r.lookAt(1,0,0),s.up.set(0,0,1),s.lookAt(0,1,0),a.up.set(0,0,-1),a.lookAt(0,-1,0),o.up.set(0,-1,0),o.lookAt(0,0,1),l.up.set(0,-1,0),l.lookAt(0,0,-1);else throw new Error("THREE.CubeCamera.updateCoordinateSystem(): Invalid coordinate system: "+e);for(const c of t)this.add(c),c.updateMatrixWorld()}update(e,t){this.parent===null&&this.updateMatrixWorld();const{renderTarget:n,activeMipmapLevel:r}=this;this.coordinateSystem!==e.coordinateSystem&&(this.coordinateSystem=e.coordinateSystem,this.updateCoordinateSystem());const[s,a,o,l,c,u]=this.children,h=e.getRenderTarget(),d=e.getActiveCubeFace(),m=e.getActiveMipmapLevel(),_=e.xr.enabled;e.xr.enabled=!1;const v=n.texture.generateMipmaps;n.texture.generateMipmaps=!1,e.setRenderTarget(n,0,r),e.render(t,s),e.setRenderTarget(n,1,r),e.render(t,a),e.setRenderTarget(n,2,r),e.render(t,o),e.setRenderTarget(n,3,r),e.render(t,l),e.setRenderTarget(n,4,r),e.render(t,c),n.texture.generateMipmaps=v,e.setRenderTarget(n,5,r),e.render(t,u),e.setRenderTarget(h,d,m),e.xr.enabled=_,n.texture.needsPMREMUpdate=!0}}class Jd extends Tn{constructor(e,t,n,r,s,a,o,l,c,u){e=e!==void 0?e:[],t=t!==void 0?t:Es,super(e,t,n,r,s,a,o,l,c,u),this.isCubeTexture=!0,this.flipY=!1}get images(){return this.image}set images(e){this.image=e}}class eg extends Ar{constructor(e=1,t={}){super(e,e,t),this.isWebGLCubeRenderTarget=!0;const n={width:e,height:e,depth:1},r=[n,n,n,n,n,n];this.texture=new Jd(r,t.mapping,t.wrapS,t.wrapT,t.magFilter,t.minFilter,t.format,t.type,t.anisotropy,t.colorSpace),this.texture.isRenderTargetTexture=!0,this.texture.generateMipmaps=t.generateMipmaps!==void 0?t.generateMipmaps:!1,this.texture.minFilter=t.minFilter!==void 0?t.minFilter:ti}fromEquirectangularTexture(e,t){this.texture.type=t.type,this.texture.colorSpace=t.colorSpace,this.texture.generateMipmaps=t.generateMipmaps,this.texture.minFilter=t.minFilter,this.texture.magFilter=t.magFilter;const n={uniforms:{tEquirect:{value:null}},vertexShader:`

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
			`},r=new Qi(5,5,5),s=new tr({name:"CubemapFromEquirect",uniforms:As(n.uniforms),vertexShader:n.vertexShader,fragmentShader:n.fragmentShader,side:Cn,blending:Zi});s.uniforms.tEquirect.value=t;const a=new Rn(r,s),o=t.minFilter;return t.minFilter===Er&&(t.minFilter=ti),new Qm(1,10,this).update(e,a),t.minFilter=o,a.geometry.dispose(),a.material.dispose(),this}clear(e,t,n,r){const s=e.getRenderTarget();for(let a=0;a<6;a++)e.setRenderTarget(this,a),e.clear(t,n,r);e.setRenderTarget(s)}}const xl=new V,tg=new V,ng=new rt;class $i{constructor(e=new V(1,0,0),t=0){this.isPlane=!0,this.normal=e,this.constant=t}set(e,t){return this.normal.copy(e),this.constant=t,this}setComponents(e,t,n,r){return this.normal.set(e,t,n),this.constant=r,this}setFromNormalAndCoplanarPoint(e,t){return this.normal.copy(e),this.constant=-t.dot(this.normal),this}setFromCoplanarPoints(e,t,n){const r=xl.subVectors(n,t).cross(tg.subVectors(e,t)).normalize();return this.setFromNormalAndCoplanarPoint(r,e),this}copy(e){return this.normal.copy(e.normal),this.constant=e.constant,this}normalize(){const e=1/this.normal.length();return this.normal.multiplyScalar(e),this.constant*=e,this}negate(){return this.constant*=-1,this.normal.negate(),this}distanceToPoint(e){return this.normal.dot(e)+this.constant}distanceToSphere(e){return this.distanceToPoint(e.center)-e.radius}projectPoint(e,t){return t.copy(e).addScaledVector(this.normal,-this.distanceToPoint(e))}intersectLine(e,t){const n=e.delta(xl),r=this.normal.dot(n);if(r===0)return this.distanceToPoint(e.start)===0?t.copy(e.start):null;const s=-(e.start.dot(this.normal)+this.constant)/r;return s<0||s>1?null:t.copy(e.start).addScaledVector(n,s)}intersectsLine(e){const t=this.distanceToPoint(e.start),n=this.distanceToPoint(e.end);return t<0&&n>0||n<0&&t>0}intersectsBox(e){return e.intersectsPlane(this)}intersectsSphere(e){return e.intersectsPlane(this)}coplanarPoint(e){return e.copy(this.normal).multiplyScalar(-this.constant)}applyMatrix4(e,t){const n=t||ng.getNormalMatrix(e),r=this.coplanarPoint(xl).applyMatrix4(e),s=this.normal.applyMatrix3(n).normalize();return this.constant=-r.dot(s),this}translate(e){return this.constant-=e.dot(this.normal),this}equals(e){return e.normal.equals(this.normal)&&e.constant===this.constant}clone(){return new this.constructor().copy(this)}}const fr=new Co,za=new V;class Hc{constructor(e=new $i,t=new $i,n=new $i,r=new $i,s=new $i,a=new $i){this.planes=[e,t,n,r,s,a]}set(e,t,n,r,s,a){const o=this.planes;return o[0].copy(e),o[1].copy(t),o[2].copy(n),o[3].copy(r),o[4].copy(s),o[5].copy(a),this}copy(e){const t=this.planes;for(let n=0;n<6;n++)t[n].copy(e.planes[n]);return this}setFromProjectionMatrix(e,t=Pi){const n=this.planes,r=e.elements,s=r[0],a=r[1],o=r[2],l=r[3],c=r[4],u=r[5],h=r[6],d=r[7],m=r[8],_=r[9],v=r[10],p=r[11],f=r[12],E=r[13],y=r[14],T=r[15];if(n[0].setComponents(l-s,d-c,p-m,T-f).normalize(),n[1].setComponents(l+s,d+c,p+m,T+f).normalize(),n[2].setComponents(l+a,d+u,p+_,T+E).normalize(),n[3].setComponents(l-a,d-u,p-_,T-E).normalize(),n[4].setComponents(l-o,d-h,p-v,T-y).normalize(),t===Pi)n[5].setComponents(l+o,d+h,p+v,T+y).normalize();else if(t===go)n[5].setComponents(o,h,v,y).normalize();else throw new Error("THREE.Frustum.setFromProjectionMatrix(): Invalid coordinate system: "+t);return this}intersectsObject(e){if(e.boundingSphere!==void 0)e.boundingSphere===null&&e.computeBoundingSphere(),fr.copy(e.boundingSphere).applyMatrix4(e.matrixWorld);else{const t=e.geometry;t.boundingSphere===null&&t.computeBoundingSphere(),fr.copy(t.boundingSphere).applyMatrix4(e.matrixWorld)}return this.intersectsSphere(fr)}intersectsSprite(e){return fr.center.set(0,0,0),fr.radius=.7071067811865476,fr.applyMatrix4(e.matrixWorld),this.intersectsSphere(fr)}intersectsSphere(e){const t=this.planes,n=e.center,r=-e.radius;for(let s=0;s<6;s++)if(t[s].distanceToPoint(n)<r)return!1;return!0}intersectsBox(e){const t=this.planes;for(let n=0;n<6;n++){const r=t[n];if(za.x=r.normal.x>0?e.max.x:e.min.x,za.y=r.normal.y>0?e.max.y:e.min.y,za.z=r.normal.z>0?e.max.z:e.min.z,r.distanceToPoint(za)<0)return!1}return!0}containsPoint(e){const t=this.planes;for(let n=0;n<6;n++)if(t[n].distanceToPoint(e)<0)return!1;return!0}clone(){return new this.constructor().copy(this)}}function Qd(){let i=null,e=!1,t=null,n=null;function r(s,a){t(s,a),n=i.requestAnimationFrame(r)}return{start:function(){e!==!0&&t!==null&&(n=i.requestAnimationFrame(r),e=!0)},stop:function(){i.cancelAnimationFrame(n),e=!1},setAnimationLoop:function(s){t=s},setContext:function(s){i=s}}}function ig(i){const e=new WeakMap;function t(o,l){const c=o.array,u=o.usage,h=c.byteLength,d=i.createBuffer();i.bindBuffer(l,d),i.bufferData(l,c,u),o.onUploadCallback();let m;if(c instanceof Float32Array)m=i.FLOAT;else if(c instanceof Uint16Array)o.isFloat16BufferAttribute?m=i.HALF_FLOAT:m=i.UNSIGNED_SHORT;else if(c instanceof Int16Array)m=i.SHORT;else if(c instanceof Uint32Array)m=i.UNSIGNED_INT;else if(c instanceof Int32Array)m=i.INT;else if(c instanceof Int8Array)m=i.BYTE;else if(c instanceof Uint8Array)m=i.UNSIGNED_BYTE;else if(c instanceof Uint8ClampedArray)m=i.UNSIGNED_BYTE;else throw new Error("THREE.WebGLAttributes: Unsupported buffer data format: "+c);return{buffer:d,type:m,bytesPerElement:c.BYTES_PER_ELEMENT,version:o.version,size:h}}function n(o,l,c){const u=l.array,h=l._updateRange,d=l.updateRanges;if(i.bindBuffer(c,o),h.count===-1&&d.length===0&&i.bufferSubData(c,0,u),d.length!==0){for(let m=0,_=d.length;m<_;m++){const v=d[m];i.bufferSubData(c,v.start*u.BYTES_PER_ELEMENT,u,v.start,v.count)}l.clearUpdateRanges()}h.count!==-1&&(i.bufferSubData(c,h.offset*u.BYTES_PER_ELEMENT,u,h.offset,h.count),h.count=-1),l.onUploadCallback()}function r(o){return o.isInterleavedBufferAttribute&&(o=o.data),e.get(o)}function s(o){o.isInterleavedBufferAttribute&&(o=o.data);const l=e.get(o);l&&(i.deleteBuffer(l.buffer),e.delete(o))}function a(o,l){if(o.isInterleavedBufferAttribute&&(o=o.data),o.isGLBufferAttribute){const u=e.get(o);(!u||u.version<o.version)&&e.set(o,{buffer:o.buffer,type:o.type,bytesPerElement:o.elementSize,version:o.version});return}const c=e.get(o);if(c===void 0)e.set(o,t(o,l));else if(c.version<o.version){if(c.size!==o.array.byteLength)throw new Error("THREE.WebGLAttributes: The size of the buffer attribute's array buffer does not match the original size. Resizing buffer attributes is not supported.");n(c.buffer,o,l),c.version=o.version}}return{get:r,remove:s,update:a}}class Lo extends gn{constructor(e=1,t=1,n=1,r=1){super(),this.type="PlaneGeometry",this.parameters={width:e,height:t,widthSegments:n,heightSegments:r};const s=e/2,a=t/2,o=Math.floor(n),l=Math.floor(r),c=o+1,u=l+1,h=e/o,d=t/l,m=[],_=[],v=[],p=[];for(let f=0;f<u;f++){const E=f*d-a;for(let y=0;y<c;y++){const T=y*h-s;_.push(T,-E,0),v.push(0,0,1),p.push(y/o),p.push(1-f/l)}}for(let f=0;f<l;f++)for(let E=0;E<o;E++){const y=E+c*f,T=E+c*(f+1),z=E+1+c*(f+1),C=E+1+c*f;m.push(y,T,C),m.push(T,z,C)}this.setIndex(m),this.setAttribute("position",new wn(_,3)),this.setAttribute("normal",new wn(v,3)),this.setAttribute("uv",new wn(p,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Lo(e.width,e.height,e.widthSegments,e.heightSegments)}}var rg=`#ifdef USE_ALPHAHASH
	if ( diffuseColor.a < getAlphaHashThreshold( vPosition ) ) discard;
#endif`,sg=`#ifdef USE_ALPHAHASH
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
#endif`,ag=`#ifdef USE_ALPHAMAP
	diffuseColor.a *= texture2D( alphaMap, vAlphaMapUv ).g;
#endif`,og=`#ifdef USE_ALPHAMAP
	uniform sampler2D alphaMap;
#endif`,lg=`#ifdef USE_ALPHATEST
	#ifdef ALPHA_TO_COVERAGE
	diffuseColor.a = smoothstep( alphaTest, alphaTest + fwidth( diffuseColor.a ), diffuseColor.a );
	if ( diffuseColor.a == 0.0 ) discard;
	#else
	if ( diffuseColor.a < alphaTest ) discard;
	#endif
#endif`,cg=`#ifdef USE_ALPHATEST
	uniform float alphaTest;
#endif`,ug=`#ifdef USE_AOMAP
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
#endif`,hg=`#ifdef USE_AOMAP
	uniform sampler2D aoMap;
	uniform float aoMapIntensity;
#endif`,dg=`#ifdef USE_BATCHING
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
#endif`,fg=`#ifdef USE_BATCHING
	mat4 batchingMatrix = getBatchingMatrix( getIndirectIndex( gl_DrawID ) );
#endif`,pg=`vec3 transformed = vec3( position );
#ifdef USE_ALPHAHASH
	vPosition = vec3( position );
#endif`,mg=`vec3 objectNormal = vec3( normal );
#ifdef USE_TANGENT
	vec3 objectTangent = vec3( tangent.xyz );
#endif`,gg=`float G_BlinnPhong_Implicit( ) {
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
} // validated`,_g=`#ifdef USE_IRIDESCENCE
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
#endif`,vg=`#ifdef USE_BUMPMAP
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
#endif`,xg=`#if NUM_CLIPPING_PLANES > 0
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
#endif`,Mg=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
	uniform vec4 clippingPlanes[ NUM_CLIPPING_PLANES ];
#endif`,Sg=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
#endif`,yg=`#if NUM_CLIPPING_PLANES > 0
	vClipPosition = - mvPosition.xyz;
#endif`,Eg=`#if defined( USE_COLOR_ALPHA )
	diffuseColor *= vColor;
#elif defined( USE_COLOR )
	diffuseColor.rgb *= vColor;
#endif`,bg=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR )
	varying vec3 vColor;
#endif`,Tg=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR ) || defined( USE_INSTANCING_COLOR ) || defined( USE_BATCHING_COLOR )
	varying vec3 vColor;
#endif`,wg=`#if defined( USE_COLOR_ALPHA )
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
#endif`,Ag=`#define PI 3.141592653589793
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
} // validated`,Rg=`#ifdef ENVMAP_TYPE_CUBE_UV
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
#endif`,Cg=`vec3 transformedNormal = objectNormal;
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
#endif`,Pg=`#ifdef USE_DISPLACEMENTMAP
	uniform sampler2D displacementMap;
	uniform float displacementScale;
	uniform float displacementBias;
#endif`,Lg=`#ifdef USE_DISPLACEMENTMAP
	transformed += normalize( objectNormal ) * ( texture2D( displacementMap, vDisplacementMapUv ).x * displacementScale + displacementBias );
#endif`,Dg=`#ifdef USE_EMISSIVEMAP
	vec4 emissiveColor = texture2D( emissiveMap, vEmissiveMapUv );
	totalEmissiveRadiance *= emissiveColor.rgb;
#endif`,Ig=`#ifdef USE_EMISSIVEMAP
	uniform sampler2D emissiveMap;
#endif`,Ug="gl_FragColor = linearToOutputTexel( gl_FragColor );",Ng=`
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
}`,Fg=`#ifdef USE_ENVMAP
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
#endif`,Og=`#ifdef USE_ENVMAP
	uniform float envMapIntensity;
	uniform float flipEnvMap;
	uniform mat3 envMapRotation;
	#ifdef ENVMAP_TYPE_CUBE
		uniform samplerCube envMap;
	#else
		uniform sampler2D envMap;
	#endif
	
#endif`,Bg=`#ifdef USE_ENVMAP
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
#endif`,zg=`#ifdef USE_ENVMAP
	#if defined( USE_BUMPMAP ) || defined( USE_NORMALMAP ) || defined( PHONG ) || defined( LAMBERT )
		#define ENV_WORLDPOS
	#endif
	#ifdef ENV_WORLDPOS
		
		varying vec3 vWorldPosition;
	#else
		varying vec3 vReflect;
		uniform float refractionRatio;
	#endif
#endif`,kg=`#ifdef USE_ENVMAP
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
#endif`,Hg=`#ifdef USE_FOG
	vFogDepth = - mvPosition.z;
#endif`,Vg=`#ifdef USE_FOG
	varying float vFogDepth;
#endif`,Gg=`#ifdef USE_FOG
	#ifdef FOG_EXP2
		float fogFactor = 1.0 - exp( - fogDensity * fogDensity * vFogDepth * vFogDepth );
	#else
		float fogFactor = smoothstep( fogNear, fogFar, vFogDepth );
	#endif
	gl_FragColor.rgb = mix( gl_FragColor.rgb, fogColor, fogFactor );
#endif`,Wg=`#ifdef USE_FOG
	uniform vec3 fogColor;
	varying float vFogDepth;
	#ifdef FOG_EXP2
		uniform float fogDensity;
	#else
		uniform float fogNear;
		uniform float fogFar;
	#endif
#endif`,Xg=`#ifdef USE_GRADIENTMAP
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
}`,Yg=`#ifdef USE_LIGHTMAP
	uniform sampler2D lightMap;
	uniform float lightMapIntensity;
#endif`,qg=`LambertMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularStrength = specularStrength;`,$g=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Lambert`,jg=`uniform bool receiveShadow;
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
#endif`,Kg=`#ifdef USE_ENVMAP
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
#endif`,Zg=`ToonMaterial material;
material.diffuseColor = diffuseColor.rgb;`,Jg=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Toon`,Qg=`BlinnPhongMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularColor = specular;
material.specularShininess = shininess;
material.specularStrength = specularStrength;`,e_=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_BlinnPhong`,t_=`PhysicalMaterial material;
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
#endif`,n_=`struct PhysicalMaterial {
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
}`,i_=`
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
#endif`,r_=`#if defined( RE_IndirectDiffuse )
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
#endif`,s_=`#if defined( RE_IndirectDiffuse )
	RE_IndirectDiffuse( irradiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif
#if defined( RE_IndirectSpecular )
	RE_IndirectSpecular( radiance, iblIrradiance, clearcoatRadiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif`,a_=`#if defined( USE_LOGDEPTHBUF )
	gl_FragDepth = vIsPerspective == 0.0 ? gl_FragCoord.z : log2( vFragDepth ) * logDepthBufFC * 0.5;
#endif`,o_=`#if defined( USE_LOGDEPTHBUF )
	uniform float logDepthBufFC;
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,l_=`#ifdef USE_LOGDEPTHBUF
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,c_=`#ifdef USE_LOGDEPTHBUF
	vFragDepth = 1.0 + gl_Position.w;
	vIsPerspective = float( isPerspectiveMatrix( projectionMatrix ) );
#endif`,u_=`#ifdef USE_MAP
	vec4 sampledDiffuseColor = texture2D( map, vMapUv );
	#ifdef DECODE_VIDEO_TEXTURE
		sampledDiffuseColor = vec4( mix( pow( sampledDiffuseColor.rgb * 0.9478672986 + vec3( 0.0521327014 ), vec3( 2.4 ) ), sampledDiffuseColor.rgb * 0.0773993808, vec3( lessThanEqual( sampledDiffuseColor.rgb, vec3( 0.04045 ) ) ) ), sampledDiffuseColor.w );
	
	#endif
	diffuseColor *= sampledDiffuseColor;
#endif`,h_=`#ifdef USE_MAP
	uniform sampler2D map;
#endif`,d_=`#if defined( USE_MAP ) || defined( USE_ALPHAMAP )
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
#endif`,f_=`#if defined( USE_POINTS_UV )
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
#endif`,p_=`float metalnessFactor = metalness;
#ifdef USE_METALNESSMAP
	vec4 texelMetalness = texture2D( metalnessMap, vMetalnessMapUv );
	metalnessFactor *= texelMetalness.b;
#endif`,m_=`#ifdef USE_METALNESSMAP
	uniform sampler2D metalnessMap;
#endif`,g_=`#ifdef USE_INSTANCING_MORPH
	float morphTargetInfluences[ MORPHTARGETS_COUNT ];
	float morphTargetBaseInfluence = texelFetch( morphTexture, ivec2( 0, gl_InstanceID ), 0 ).r;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		morphTargetInfluences[i] =  texelFetch( morphTexture, ivec2( i + 1, gl_InstanceID ), 0 ).r;
	}
#endif`,__=`#if defined( USE_MORPHCOLORS )
	vColor *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		#if defined( USE_COLOR_ALPHA )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ) * morphTargetInfluences[ i ];
		#elif defined( USE_COLOR )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ).rgb * morphTargetInfluences[ i ];
		#endif
	}
#endif`,v_=`#ifdef USE_MORPHNORMALS
	objectNormal *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) objectNormal += getMorph( gl_VertexID, i, 1 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,x_=`#ifdef USE_MORPHTARGETS
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
#endif`,M_=`#ifdef USE_MORPHTARGETS
	transformed *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) transformed += getMorph( gl_VertexID, i, 0 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,S_=`float faceDirection = gl_FrontFacing ? 1.0 : - 1.0;
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
vec3 nonPerturbedNormal = normal;`,y_=`#ifdef USE_NORMALMAP_OBJECTSPACE
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
#endif`,E_=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,b_=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,T_=`#ifndef FLAT_SHADED
	vNormal = normalize( transformedNormal );
	#ifdef USE_TANGENT
		vTangent = normalize( transformedTangent );
		vBitangent = normalize( cross( vNormal, vTangent ) * tangent.w );
	#endif
#endif`,w_=`#ifdef USE_NORMALMAP
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
#endif`,A_=`#ifdef USE_CLEARCOAT
	vec3 clearcoatNormal = nonPerturbedNormal;
#endif`,R_=`#ifdef USE_CLEARCOAT_NORMALMAP
	vec3 clearcoatMapN = texture2D( clearcoatNormalMap, vClearcoatNormalMapUv ).xyz * 2.0 - 1.0;
	clearcoatMapN.xy *= clearcoatNormalScale;
	clearcoatNormal = normalize( tbn2 * clearcoatMapN );
#endif`,C_=`#ifdef USE_CLEARCOATMAP
	uniform sampler2D clearcoatMap;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	uniform sampler2D clearcoatNormalMap;
	uniform vec2 clearcoatNormalScale;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	uniform sampler2D clearcoatRoughnessMap;
#endif`,P_=`#ifdef USE_IRIDESCENCEMAP
	uniform sampler2D iridescenceMap;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	uniform sampler2D iridescenceThicknessMap;
#endif`,L_=`#ifdef OPAQUE
diffuseColor.a = 1.0;
#endif
#ifdef USE_TRANSMISSION
diffuseColor.a *= material.transmissionAlpha;
#endif
gl_FragColor = vec4( outgoingLight, diffuseColor.a );`,D_=`vec3 packNormalToRGB( const in vec3 normal ) {
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
}`,I_=`#ifdef PREMULTIPLIED_ALPHA
	gl_FragColor.rgb *= gl_FragColor.a;
#endif`,U_=`vec4 mvPosition = vec4( transformed, 1.0 );
#ifdef USE_BATCHING
	mvPosition = batchingMatrix * mvPosition;
#endif
#ifdef USE_INSTANCING
	mvPosition = instanceMatrix * mvPosition;
#endif
mvPosition = modelViewMatrix * mvPosition;
gl_Position = projectionMatrix * mvPosition;`,N_=`#ifdef DITHERING
	gl_FragColor.rgb = dithering( gl_FragColor.rgb );
#endif`,F_=`#ifdef DITHERING
	vec3 dithering( vec3 color ) {
		float grid_position = rand( gl_FragCoord.xy );
		vec3 dither_shift_RGB = vec3( 0.25 / 255.0, -0.25 / 255.0, 0.25 / 255.0 );
		dither_shift_RGB = mix( 2.0 * dither_shift_RGB, -2.0 * dither_shift_RGB, grid_position );
		return color + dither_shift_RGB;
	}
#endif`,O_=`float roughnessFactor = roughness;
#ifdef USE_ROUGHNESSMAP
	vec4 texelRoughness = texture2D( roughnessMap, vRoughnessMapUv );
	roughnessFactor *= texelRoughness.g;
#endif`,B_=`#ifdef USE_ROUGHNESSMAP
	uniform sampler2D roughnessMap;
#endif`,z_=`#if NUM_SPOT_LIGHT_COORDS > 0
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
#endif`,k_=`#if NUM_SPOT_LIGHT_COORDS > 0
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
#endif`,H_=`#if ( defined( USE_SHADOWMAP ) && ( NUM_DIR_LIGHT_SHADOWS > 0 || NUM_POINT_LIGHT_SHADOWS > 0 ) ) || ( NUM_SPOT_LIGHT_COORDS > 0 )
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
#endif`,V_=`float getShadowMask() {
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
}`,G_=`#ifdef USE_SKINNING
	mat4 boneMatX = getBoneMatrix( skinIndex.x );
	mat4 boneMatY = getBoneMatrix( skinIndex.y );
	mat4 boneMatZ = getBoneMatrix( skinIndex.z );
	mat4 boneMatW = getBoneMatrix( skinIndex.w );
#endif`,W_=`#ifdef USE_SKINNING
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
#endif`,X_=`#ifdef USE_SKINNING
	vec4 skinVertex = bindMatrix * vec4( transformed, 1.0 );
	vec4 skinned = vec4( 0.0 );
	skinned += boneMatX * skinVertex * skinWeight.x;
	skinned += boneMatY * skinVertex * skinWeight.y;
	skinned += boneMatZ * skinVertex * skinWeight.z;
	skinned += boneMatW * skinVertex * skinWeight.w;
	transformed = ( bindMatrixInverse * skinned ).xyz;
#endif`,Y_=`#ifdef USE_SKINNING
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
#endif`,q_=`float specularStrength;
#ifdef USE_SPECULARMAP
	vec4 texelSpecular = texture2D( specularMap, vSpecularMapUv );
	specularStrength = texelSpecular.r;
#else
	specularStrength = 1.0;
#endif`,$_=`#ifdef USE_SPECULARMAP
	uniform sampler2D specularMap;
#endif`,j_=`#if defined( TONE_MAPPING )
	gl_FragColor.rgb = toneMapping( gl_FragColor.rgb );
#endif`,K_=`#ifndef saturate
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
vec3 CustomToneMapping( vec3 color ) { return color; }`,Z_=`#ifdef USE_TRANSMISSION
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
#endif`,J_=`#ifdef USE_TRANSMISSION
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
#endif`,Q_=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
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
#endif`,e0=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
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
#endif`,t0=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
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
#endif`,n0=`#if defined( USE_ENVMAP ) || defined( DISTANCE ) || defined ( USE_SHADOWMAP ) || defined ( USE_TRANSMISSION ) || NUM_SPOT_LIGHT_COORDS > 0
	vec4 worldPosition = vec4( transformed, 1.0 );
	#ifdef USE_BATCHING
		worldPosition = batchingMatrix * worldPosition;
	#endif
	#ifdef USE_INSTANCING
		worldPosition = instanceMatrix * worldPosition;
	#endif
	worldPosition = modelMatrix * worldPosition;
#endif`;const i0=`varying vec2 vUv;
uniform mat3 uvTransform;
void main() {
	vUv = ( uvTransform * vec3( uv, 1 ) ).xy;
	gl_Position = vec4( position.xy, 1.0, 1.0 );
}`,r0=`uniform sampler2D t2D;
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
}`,s0=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,a0=`#ifdef ENVMAP_TYPE_CUBE
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
}`,o0=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,l0=`uniform samplerCube tCube;
uniform float tFlip;
uniform float opacity;
varying vec3 vWorldDirection;
void main() {
	vec4 texColor = textureCube( tCube, vec3( tFlip * vWorldDirection.x, vWorldDirection.yz ) );
	gl_FragColor = texColor;
	gl_FragColor.a *= opacity;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,c0=`#include <common>
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
}`,u0=`#if DEPTH_PACKING == 3200
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
}`,h0=`#define DISTANCE
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
}`,d0=`#define DISTANCE
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
}`,f0=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
}`,p0=`uniform sampler2D tEquirect;
varying vec3 vWorldDirection;
#include <common>
void main() {
	vec3 direction = normalize( vWorldDirection );
	vec2 sampleUV = equirectUv( direction );
	gl_FragColor = texture2D( tEquirect, sampleUV );
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,m0=`uniform float scale;
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
}`,g0=`uniform vec3 diffuse;
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
}`,_0=`#include <common>
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
}`,v0=`uniform vec3 diffuse;
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
}`,x0=`#define LAMBERT
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
}`,M0=`#define LAMBERT
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
}`,S0=`#define MATCAP
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
}`,y0=`#define MATCAP
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
}`,E0=`#define NORMAL
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
}`,b0=`#define NORMAL
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
}`,T0=`#define PHONG
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
}`,w0=`#define PHONG
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
}`,A0=`#define STANDARD
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
}`,R0=`#define STANDARD
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
}`,C0=`#define TOON
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
}`,P0=`#define TOON
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
}`,L0=`uniform float size;
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
}`,D0=`uniform vec3 diffuse;
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
}`,I0=`#include <common>
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
}`,U0=`uniform vec3 color;
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
}`,N0=`uniform float rotation;
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
}`,F0=`uniform vec3 diffuse;
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
}`,it={alphahash_fragment:rg,alphahash_pars_fragment:sg,alphamap_fragment:ag,alphamap_pars_fragment:og,alphatest_fragment:lg,alphatest_pars_fragment:cg,aomap_fragment:ug,aomap_pars_fragment:hg,batching_pars_vertex:dg,batching_vertex:fg,begin_vertex:pg,beginnormal_vertex:mg,bsdfs:gg,iridescence_fragment:_g,bumpmap_pars_fragment:vg,clipping_planes_fragment:xg,clipping_planes_pars_fragment:Mg,clipping_planes_pars_vertex:Sg,clipping_planes_vertex:yg,color_fragment:Eg,color_pars_fragment:bg,color_pars_vertex:Tg,color_vertex:wg,common:Ag,cube_uv_reflection_fragment:Rg,defaultnormal_vertex:Cg,displacementmap_pars_vertex:Pg,displacementmap_vertex:Lg,emissivemap_fragment:Dg,emissivemap_pars_fragment:Ig,colorspace_fragment:Ug,colorspace_pars_fragment:Ng,envmap_fragment:Fg,envmap_common_pars_fragment:Og,envmap_pars_fragment:Bg,envmap_pars_vertex:zg,envmap_physical_pars_fragment:Kg,envmap_vertex:kg,fog_vertex:Hg,fog_pars_vertex:Vg,fog_fragment:Gg,fog_pars_fragment:Wg,gradientmap_pars_fragment:Xg,lightmap_pars_fragment:Yg,lights_lambert_fragment:qg,lights_lambert_pars_fragment:$g,lights_pars_begin:jg,lights_toon_fragment:Zg,lights_toon_pars_fragment:Jg,lights_phong_fragment:Qg,lights_phong_pars_fragment:e_,lights_physical_fragment:t_,lights_physical_pars_fragment:n_,lights_fragment_begin:i_,lights_fragment_maps:r_,lights_fragment_end:s_,logdepthbuf_fragment:a_,logdepthbuf_pars_fragment:o_,logdepthbuf_pars_vertex:l_,logdepthbuf_vertex:c_,map_fragment:u_,map_pars_fragment:h_,map_particle_fragment:d_,map_particle_pars_fragment:f_,metalnessmap_fragment:p_,metalnessmap_pars_fragment:m_,morphinstance_vertex:g_,morphcolor_vertex:__,morphnormal_vertex:v_,morphtarget_pars_vertex:x_,morphtarget_vertex:M_,normal_fragment_begin:S_,normal_fragment_maps:y_,normal_pars_fragment:E_,normal_pars_vertex:b_,normal_vertex:T_,normalmap_pars_fragment:w_,clearcoat_normal_fragment_begin:A_,clearcoat_normal_fragment_maps:R_,clearcoat_pars_fragment:C_,iridescence_pars_fragment:P_,opaque_fragment:L_,packing:D_,premultiplied_alpha_fragment:I_,project_vertex:U_,dithering_fragment:N_,dithering_pars_fragment:F_,roughnessmap_fragment:O_,roughnessmap_pars_fragment:B_,shadowmap_pars_fragment:z_,shadowmap_pars_vertex:k_,shadowmap_vertex:H_,shadowmask_pars_fragment:V_,skinbase_vertex:G_,skinning_pars_vertex:W_,skinning_vertex:X_,skinnormal_vertex:Y_,specularmap_fragment:q_,specularmap_pars_fragment:$_,tonemapping_fragment:j_,tonemapping_pars_fragment:K_,transmission_fragment:Z_,transmission_pars_fragment:J_,uv_pars_fragment:Q_,uv_pars_vertex:e0,uv_vertex:t0,worldpos_vertex:n0,background_vert:i0,background_frag:r0,backgroundCube_vert:s0,backgroundCube_frag:a0,cube_vert:o0,cube_frag:l0,depth_vert:c0,depth_frag:u0,distanceRGBA_vert:h0,distanceRGBA_frag:d0,equirect_vert:f0,equirect_frag:p0,linedashed_vert:m0,linedashed_frag:g0,meshbasic_vert:_0,meshbasic_frag:v0,meshlambert_vert:x0,meshlambert_frag:M0,meshmatcap_vert:S0,meshmatcap_frag:y0,meshnormal_vert:E0,meshnormal_frag:b0,meshphong_vert:T0,meshphong_frag:w0,meshphysical_vert:A0,meshphysical_frag:R0,meshtoon_vert:C0,meshtoon_frag:P0,points_vert:L0,points_frag:D0,shadow_vert:I0,shadow_frag:U0,sprite_vert:N0,sprite_frag:F0},Ae={common:{diffuse:{value:new nt(16777215)},opacity:{value:1},map:{value:null},mapTransform:{value:new rt},alphaMap:{value:null},alphaMapTransform:{value:new rt},alphaTest:{value:0}},specularmap:{specularMap:{value:null},specularMapTransform:{value:new rt}},envmap:{envMap:{value:null},envMapRotation:{value:new rt},flipEnvMap:{value:-1},reflectivity:{value:1},ior:{value:1.5},refractionRatio:{value:.98}},aomap:{aoMap:{value:null},aoMapIntensity:{value:1},aoMapTransform:{value:new rt}},lightmap:{lightMap:{value:null},lightMapIntensity:{value:1},lightMapTransform:{value:new rt}},bumpmap:{bumpMap:{value:null},bumpMapTransform:{value:new rt},bumpScale:{value:1}},normalmap:{normalMap:{value:null},normalMapTransform:{value:new rt},normalScale:{value:new Xe(1,1)}},displacementmap:{displacementMap:{value:null},displacementMapTransform:{value:new rt},displacementScale:{value:1},displacementBias:{value:0}},emissivemap:{emissiveMap:{value:null},emissiveMapTransform:{value:new rt}},metalnessmap:{metalnessMap:{value:null},metalnessMapTransform:{value:new rt}},roughnessmap:{roughnessMap:{value:null},roughnessMapTransform:{value:new rt}},gradientmap:{gradientMap:{value:null}},fog:{fogDensity:{value:25e-5},fogNear:{value:1},fogFar:{value:2e3},fogColor:{value:new nt(16777215)}},lights:{ambientLightColor:{value:[]},lightProbe:{value:[]},directionalLights:{value:[],properties:{direction:{},color:{}}},directionalLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},directionalShadowMap:{value:[]},directionalShadowMatrix:{value:[]},spotLights:{value:[],properties:{color:{},position:{},direction:{},distance:{},coneCos:{},penumbraCos:{},decay:{}}},spotLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},spotLightMap:{value:[]},spotShadowMap:{value:[]},spotLightMatrix:{value:[]},pointLights:{value:[],properties:{color:{},position:{},decay:{},distance:{}}},pointLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{},shadowCameraNear:{},shadowCameraFar:{}}},pointShadowMap:{value:[]},pointShadowMatrix:{value:[]},hemisphereLights:{value:[],properties:{direction:{},skyColor:{},groundColor:{}}},rectAreaLights:{value:[],properties:{color:{},position:{},width:{},height:{}}},ltc_1:{value:null},ltc_2:{value:null}},points:{diffuse:{value:new nt(16777215)},opacity:{value:1},size:{value:1},scale:{value:1},map:{value:null},alphaMap:{value:null},alphaMapTransform:{value:new rt},alphaTest:{value:0},uvTransform:{value:new rt}},sprite:{diffuse:{value:new nt(16777215)},opacity:{value:1},center:{value:new Xe(.5,.5)},rotation:{value:0},map:{value:null},mapTransform:{value:new rt},alphaMap:{value:null},alphaMapTransform:{value:new rt},alphaTest:{value:0}}},pi={basic:{uniforms:yn([Ae.common,Ae.specularmap,Ae.envmap,Ae.aomap,Ae.lightmap,Ae.fog]),vertexShader:it.meshbasic_vert,fragmentShader:it.meshbasic_frag},lambert:{uniforms:yn([Ae.common,Ae.specularmap,Ae.envmap,Ae.aomap,Ae.lightmap,Ae.emissivemap,Ae.bumpmap,Ae.normalmap,Ae.displacementmap,Ae.fog,Ae.lights,{emissive:{value:new nt(0)}}]),vertexShader:it.meshlambert_vert,fragmentShader:it.meshlambert_frag},phong:{uniforms:yn([Ae.common,Ae.specularmap,Ae.envmap,Ae.aomap,Ae.lightmap,Ae.emissivemap,Ae.bumpmap,Ae.normalmap,Ae.displacementmap,Ae.fog,Ae.lights,{emissive:{value:new nt(0)},specular:{value:new nt(1118481)},shininess:{value:30}}]),vertexShader:it.meshphong_vert,fragmentShader:it.meshphong_frag},standard:{uniforms:yn([Ae.common,Ae.envmap,Ae.aomap,Ae.lightmap,Ae.emissivemap,Ae.bumpmap,Ae.normalmap,Ae.displacementmap,Ae.roughnessmap,Ae.metalnessmap,Ae.fog,Ae.lights,{emissive:{value:new nt(0)},roughness:{value:1},metalness:{value:0},envMapIntensity:{value:1}}]),vertexShader:it.meshphysical_vert,fragmentShader:it.meshphysical_frag},toon:{uniforms:yn([Ae.common,Ae.aomap,Ae.lightmap,Ae.emissivemap,Ae.bumpmap,Ae.normalmap,Ae.displacementmap,Ae.gradientmap,Ae.fog,Ae.lights,{emissive:{value:new nt(0)}}]),vertexShader:it.meshtoon_vert,fragmentShader:it.meshtoon_frag},matcap:{uniforms:yn([Ae.common,Ae.bumpmap,Ae.normalmap,Ae.displacementmap,Ae.fog,{matcap:{value:null}}]),vertexShader:it.meshmatcap_vert,fragmentShader:it.meshmatcap_frag},points:{uniforms:yn([Ae.points,Ae.fog]),vertexShader:it.points_vert,fragmentShader:it.points_frag},dashed:{uniforms:yn([Ae.common,Ae.fog,{scale:{value:1},dashSize:{value:1},totalSize:{value:2}}]),vertexShader:it.linedashed_vert,fragmentShader:it.linedashed_frag},depth:{uniforms:yn([Ae.common,Ae.displacementmap]),vertexShader:it.depth_vert,fragmentShader:it.depth_frag},normal:{uniforms:yn([Ae.common,Ae.bumpmap,Ae.normalmap,Ae.displacementmap,{opacity:{value:1}}]),vertexShader:it.meshnormal_vert,fragmentShader:it.meshnormal_frag},sprite:{uniforms:yn([Ae.sprite,Ae.fog]),vertexShader:it.sprite_vert,fragmentShader:it.sprite_frag},background:{uniforms:{uvTransform:{value:new rt},t2D:{value:null},backgroundIntensity:{value:1}},vertexShader:it.background_vert,fragmentShader:it.background_frag},backgroundCube:{uniforms:{envMap:{value:null},flipEnvMap:{value:-1},backgroundBlurriness:{value:0},backgroundIntensity:{value:1},backgroundRotation:{value:new rt}},vertexShader:it.backgroundCube_vert,fragmentShader:it.backgroundCube_frag},cube:{uniforms:{tCube:{value:null},tFlip:{value:-1},opacity:{value:1}},vertexShader:it.cube_vert,fragmentShader:it.cube_frag},equirect:{uniforms:{tEquirect:{value:null}},vertexShader:it.equirect_vert,fragmentShader:it.equirect_frag},distanceRGBA:{uniforms:yn([Ae.common,Ae.displacementmap,{referencePosition:{value:new V},nearDistance:{value:1},farDistance:{value:1e3}}]),vertexShader:it.distanceRGBA_vert,fragmentShader:it.distanceRGBA_frag},shadow:{uniforms:yn([Ae.lights,Ae.fog,{color:{value:new nt(0)},opacity:{value:1}}]),vertexShader:it.shadow_vert,fragmentShader:it.shadow_frag}};pi.physical={uniforms:yn([pi.standard.uniforms,{clearcoat:{value:0},clearcoatMap:{value:null},clearcoatMapTransform:{value:new rt},clearcoatNormalMap:{value:null},clearcoatNormalMapTransform:{value:new rt},clearcoatNormalScale:{value:new Xe(1,1)},clearcoatRoughness:{value:0},clearcoatRoughnessMap:{value:null},clearcoatRoughnessMapTransform:{value:new rt},dispersion:{value:0},iridescence:{value:0},iridescenceMap:{value:null},iridescenceMapTransform:{value:new rt},iridescenceIOR:{value:1.3},iridescenceThicknessMinimum:{value:100},iridescenceThicknessMaximum:{value:400},iridescenceThicknessMap:{value:null},iridescenceThicknessMapTransform:{value:new rt},sheen:{value:0},sheenColor:{value:new nt(0)},sheenColorMap:{value:null},sheenColorMapTransform:{value:new rt},sheenRoughness:{value:1},sheenRoughnessMap:{value:null},sheenRoughnessMapTransform:{value:new rt},transmission:{value:0},transmissionMap:{value:null},transmissionMapTransform:{value:new rt},transmissionSamplerSize:{value:new Xe},transmissionSamplerMap:{value:null},thickness:{value:0},thicknessMap:{value:null},thicknessMapTransform:{value:new rt},attenuationDistance:{value:0},attenuationColor:{value:new nt(0)},specularColor:{value:new nt(1,1,1)},specularColorMap:{value:null},specularColorMapTransform:{value:new rt},specularIntensity:{value:1},specularIntensityMap:{value:null},specularIntensityMapTransform:{value:new rt},anisotropyVector:{value:new Xe},anisotropyMap:{value:null},anisotropyMapTransform:{value:new rt}}]),vertexShader:it.meshphysical_vert,fragmentShader:it.meshphysical_frag};const ka={r:0,b:0,g:0},pr=new gi,O0=new zt;function B0(i,e,t,n,r,s,a){const o=new nt(0);let l=s===!0?0:1,c,u,h=null,d=0,m=null;function _(E){let y=E.isScene===!0?E.background:null;return y&&y.isTexture&&(y=(E.backgroundBlurriness>0?t:e).get(y)),y}function v(E){let y=!1;const T=_(E);T===null?f(o,l):T&&T.isColor&&(f(T,1),y=!0);const z=i.xr.getEnvironmentBlendMode();z==="additive"?n.buffers.color.setClear(0,0,0,1,a):z==="alpha-blend"&&n.buffers.color.setClear(0,0,0,0,a),(i.autoClear||y)&&(n.buffers.depth.setTest(!0),n.buffers.depth.setMask(!0),n.buffers.color.setMask(!0),i.clear(i.autoClearColor,i.autoClearDepth,i.autoClearStencil))}function p(E,y){const T=_(y);T&&(T.isCubeTexture||T.mapping===Ao)?(u===void 0&&(u=new Rn(new Qi(1,1,1),new tr({name:"BackgroundCubeMaterial",uniforms:As(pi.backgroundCube.uniforms),vertexShader:pi.backgroundCube.vertexShader,fragmentShader:pi.backgroundCube.fragmentShader,side:Cn,depthTest:!1,depthWrite:!1,fog:!1})),u.geometry.deleteAttribute("normal"),u.geometry.deleteAttribute("uv"),u.onBeforeRender=function(z,C,D){this.matrixWorld.copyPosition(D.matrixWorld)},Object.defineProperty(u.material,"envMap",{get:function(){return this.uniforms.envMap.value}}),r.update(u)),pr.copy(y.backgroundRotation),pr.x*=-1,pr.y*=-1,pr.z*=-1,T.isCubeTexture&&T.isRenderTargetTexture===!1&&(pr.y*=-1,pr.z*=-1),u.material.uniforms.envMap.value=T,u.material.uniforms.flipEnvMap.value=T.isCubeTexture&&T.isRenderTargetTexture===!1?-1:1,u.material.uniforms.backgroundBlurriness.value=y.backgroundBlurriness,u.material.uniforms.backgroundIntensity.value=y.backgroundIntensity,u.material.uniforms.backgroundRotation.value.setFromMatrix4(O0.makeRotationFromEuler(pr)),u.material.toneMapped=St.getTransfer(T.colorSpace)!==Nt,(h!==T||d!==T.version||m!==i.toneMapping)&&(u.material.needsUpdate=!0,h=T,d=T.version,m=i.toneMapping),u.layers.enableAll(),E.unshift(u,u.geometry,u.material,0,0,null)):T&&T.isTexture&&(c===void 0&&(c=new Rn(new Lo(2,2),new tr({name:"BackgroundMaterial",uniforms:As(pi.background.uniforms),vertexShader:pi.background.vertexShader,fragmentShader:pi.background.fragmentShader,side:er,depthTest:!1,depthWrite:!1,fog:!1})),c.geometry.deleteAttribute("normal"),Object.defineProperty(c.material,"map",{get:function(){return this.uniforms.t2D.value}}),r.update(c)),c.material.uniforms.t2D.value=T,c.material.uniforms.backgroundIntensity.value=y.backgroundIntensity,c.material.toneMapped=St.getTransfer(T.colorSpace)!==Nt,T.matrixAutoUpdate===!0&&T.updateMatrix(),c.material.uniforms.uvTransform.value.copy(T.matrix),(h!==T||d!==T.version||m!==i.toneMapping)&&(c.material.needsUpdate=!0,h=T,d=T.version,m=i.toneMapping),c.layers.enableAll(),E.unshift(c,c.geometry,c.material,0,0,null))}function f(E,y){E.getRGB(ka,Zd(i)),n.buffers.color.setClear(ka.r,ka.g,ka.b,y,a)}return{getClearColor:function(){return o},setClearColor:function(E,y=1){o.set(E),l=y,f(o,l)},getClearAlpha:function(){return l},setClearAlpha:function(E){l=E,f(o,l)},render:v,addToRenderList:p}}function z0(i,e){const t=i.getParameter(i.MAX_VERTEX_ATTRIBS),n={},r=d(null);let s=r,a=!1;function o(x,R,j,O,K){let W=!1;const J=h(O,j,R);s!==J&&(s=J,c(s.object)),W=m(x,O,j,K),W&&_(x,O,j,K),K!==null&&e.update(K,i.ELEMENT_ARRAY_BUFFER),(W||a)&&(a=!1,T(x,R,j,O),K!==null&&i.bindBuffer(i.ELEMENT_ARRAY_BUFFER,e.get(K).buffer))}function l(){return i.createVertexArray()}function c(x){return i.bindVertexArray(x)}function u(x){return i.deleteVertexArray(x)}function h(x,R,j){const O=j.wireframe===!0;let K=n[x.id];K===void 0&&(K={},n[x.id]=K);let W=K[R.id];W===void 0&&(W={},K[R.id]=W);let J=W[O];return J===void 0&&(J=d(l()),W[O]=J),J}function d(x){const R=[],j=[],O=[];for(let K=0;K<t;K++)R[K]=0,j[K]=0,O[K]=0;return{geometry:null,program:null,wireframe:!1,newAttributes:R,enabledAttributes:j,attributeDivisors:O,object:x,attributes:{},index:null}}function m(x,R,j,O){const K=s.attributes,W=R.attributes;let J=0;const Y=j.getAttributes();for(const ee in Y)if(Y[ee].location>=0){const ue=K[ee];let _e=W[ee];if(_e===void 0&&(ee==="instanceMatrix"&&x.instanceMatrix&&(_e=x.instanceMatrix),ee==="instanceColor"&&x.instanceColor&&(_e=x.instanceColor)),ue===void 0||ue.attribute!==_e||_e&&ue.data!==_e.data)return!0;J++}return s.attributesNum!==J||s.index!==O}function _(x,R,j,O){const K={},W=R.attributes;let J=0;const Y=j.getAttributes();for(const ee in Y)if(Y[ee].location>=0){let ue=W[ee];ue===void 0&&(ee==="instanceMatrix"&&x.instanceMatrix&&(ue=x.instanceMatrix),ee==="instanceColor"&&x.instanceColor&&(ue=x.instanceColor));const _e={};_e.attribute=ue,ue&&ue.data&&(_e.data=ue.data),K[ee]=_e,J++}s.attributes=K,s.attributesNum=J,s.index=O}function v(){const x=s.newAttributes;for(let R=0,j=x.length;R<j;R++)x[R]=0}function p(x){f(x,0)}function f(x,R){const j=s.newAttributes,O=s.enabledAttributes,K=s.attributeDivisors;j[x]=1,O[x]===0&&(i.enableVertexAttribArray(x),O[x]=1),K[x]!==R&&(i.vertexAttribDivisor(x,R),K[x]=R)}function E(){const x=s.newAttributes,R=s.enabledAttributes;for(let j=0,O=R.length;j<O;j++)R[j]!==x[j]&&(i.disableVertexAttribArray(j),R[j]=0)}function y(x,R,j,O,K,W,J){J===!0?i.vertexAttribIPointer(x,R,j,K,W):i.vertexAttribPointer(x,R,j,O,K,W)}function T(x,R,j,O){v();const K=O.attributes,W=j.getAttributes(),J=R.defaultAttributeValues;for(const Y in W){const ee=W[Y];if(ee.location>=0){let pe=K[Y];if(pe===void 0&&(Y==="instanceMatrix"&&x.instanceMatrix&&(pe=x.instanceMatrix),Y==="instanceColor"&&x.instanceColor&&(pe=x.instanceColor)),pe!==void 0){const ue=pe.normalized,_e=pe.itemSize,be=e.get(pe);if(be===void 0)continue;const ve=be.buffer,te=be.type,le=be.bytesPerElement,xe=te===i.INT||te===i.UNSIGNED_INT||pe.gpuType===Lc;if(pe.isInterleavedBufferAttribute){const he=pe.data,Be=he.stride,Ve=pe.offset;if(he.isInstancedInterleavedBuffer){for(let Ne=0;Ne<ee.locationSize;Ne++)f(ee.location+Ne,he.meshPerAttribute);x.isInstancedMesh!==!0&&O._maxInstanceCount===void 0&&(O._maxInstanceCount=he.meshPerAttribute*he.count)}else for(let Ne=0;Ne<ee.locationSize;Ne++)p(ee.location+Ne);i.bindBuffer(i.ARRAY_BUFFER,ve);for(let Ne=0;Ne<ee.locationSize;Ne++)y(ee.location+Ne,_e/ee.locationSize,te,ue,Be*le,(Ve+_e/ee.locationSize*Ne)*le,xe)}else{if(pe.isInstancedBufferAttribute){for(let he=0;he<ee.locationSize;he++)f(ee.location+he,pe.meshPerAttribute);x.isInstancedMesh!==!0&&O._maxInstanceCount===void 0&&(O._maxInstanceCount=pe.meshPerAttribute*pe.count)}else for(let he=0;he<ee.locationSize;he++)p(ee.location+he);i.bindBuffer(i.ARRAY_BUFFER,ve);for(let he=0;he<ee.locationSize;he++)y(ee.location+he,_e/ee.locationSize,te,ue,_e*le,_e/ee.locationSize*he*le,xe)}}else if(J!==void 0){const ue=J[Y];if(ue!==void 0)switch(ue.length){case 2:i.vertexAttrib2fv(ee.location,ue);break;case 3:i.vertexAttrib3fv(ee.location,ue);break;case 4:i.vertexAttrib4fv(ee.location,ue);break;default:i.vertexAttrib1fv(ee.location,ue)}}}}E()}function z(){B();for(const x in n){const R=n[x];for(const j in R){const O=R[j];for(const K in O)u(O[K].object),delete O[K];delete R[j]}delete n[x]}}function C(x){if(n[x.id]===void 0)return;const R=n[x.id];for(const j in R){const O=R[j];for(const K in O)u(O[K].object),delete O[K];delete R[j]}delete n[x.id]}function D(x){for(const R in n){const j=n[R];if(j[x.id]===void 0)continue;const O=j[x.id];for(const K in O)u(O[K].object),delete O[K];delete j[x.id]}}function B(){w(),a=!0,s!==r&&(s=r,c(s.object))}function w(){r.geometry=null,r.program=null,r.wireframe=!1}return{setup:o,reset:B,resetDefaultState:w,dispose:z,releaseStatesOfGeometry:C,releaseStatesOfProgram:D,initAttributes:v,enableAttribute:p,disableUnusedAttributes:E}}function k0(i,e,t){let n;function r(c){n=c}function s(c,u){i.drawArrays(n,c,u),t.update(u,n,1)}function a(c,u,h){h!==0&&(i.drawArraysInstanced(n,c,u,h),t.update(u,n,h))}function o(c,u,h){if(h===0)return;e.get("WEBGL_multi_draw").multiDrawArraysWEBGL(n,c,0,u,0,h);let m=0;for(let _=0;_<h;_++)m+=u[_];t.update(m,n,1)}function l(c,u,h,d){if(h===0)return;const m=e.get("WEBGL_multi_draw");if(m===null)for(let _=0;_<c.length;_++)a(c[_],u[_],d[_]);else{m.multiDrawArraysInstancedWEBGL(n,c,0,u,0,d,0,h);let _=0;for(let v=0;v<h;v++)_+=u[v];for(let v=0;v<d.length;v++)t.update(_,n,d[v])}}this.setMode=r,this.render=s,this.renderInstances=a,this.renderMultiDraw=o,this.renderMultiDrawInstances=l}function H0(i,e,t,n){let r;function s(){if(r!==void 0)return r;if(e.has("EXT_texture_filter_anisotropic")===!0){const C=e.get("EXT_texture_filter_anisotropic");r=i.getParameter(C.MAX_TEXTURE_MAX_ANISOTROPY_EXT)}else r=0;return r}function a(C){return!(C!==ri&&n.convert(C)!==i.getParameter(i.IMPLEMENTATION_COLOR_READ_FORMAT))}function o(C){const D=C===ha&&(e.has("EXT_color_buffer_half_float")||e.has("EXT_color_buffer_float"));return!(C!==Ui&&n.convert(C)!==i.getParameter(i.IMPLEMENTATION_COLOR_READ_TYPE)&&C!==Ci&&!D)}function l(C){if(C==="highp"){if(i.getShaderPrecisionFormat(i.VERTEX_SHADER,i.HIGH_FLOAT).precision>0&&i.getShaderPrecisionFormat(i.FRAGMENT_SHADER,i.HIGH_FLOAT).precision>0)return"highp";C="mediump"}return C==="mediump"&&i.getShaderPrecisionFormat(i.VERTEX_SHADER,i.MEDIUM_FLOAT).precision>0&&i.getShaderPrecisionFormat(i.FRAGMENT_SHADER,i.MEDIUM_FLOAT).precision>0?"mediump":"lowp"}let c=t.precision!==void 0?t.precision:"highp";const u=l(c);u!==c&&(console.warn("THREE.WebGLRenderer:",c,"not supported, using",u,"instead."),c=u);const h=t.logarithmicDepthBuffer===!0,d=i.getParameter(i.MAX_TEXTURE_IMAGE_UNITS),m=i.getParameter(i.MAX_VERTEX_TEXTURE_IMAGE_UNITS),_=i.getParameter(i.MAX_TEXTURE_SIZE),v=i.getParameter(i.MAX_CUBE_MAP_TEXTURE_SIZE),p=i.getParameter(i.MAX_VERTEX_ATTRIBS),f=i.getParameter(i.MAX_VERTEX_UNIFORM_VECTORS),E=i.getParameter(i.MAX_VARYING_VECTORS),y=i.getParameter(i.MAX_FRAGMENT_UNIFORM_VECTORS),T=m>0,z=i.getParameter(i.MAX_SAMPLES);return{isWebGL2:!0,getMaxAnisotropy:s,getMaxPrecision:l,textureFormatReadable:a,textureTypeReadable:o,precision:c,logarithmicDepthBuffer:h,maxTextures:d,maxVertexTextures:m,maxTextureSize:_,maxCubemapSize:v,maxAttributes:p,maxVertexUniforms:f,maxVaryings:E,maxFragmentUniforms:y,vertexTextures:T,maxSamples:z}}function V0(i){const e=this;let t=null,n=0,r=!1,s=!1;const a=new $i,o=new rt,l={value:null,needsUpdate:!1};this.uniform=l,this.numPlanes=0,this.numIntersection=0,this.init=function(h,d){const m=h.length!==0||d||n!==0||r;return r=d,n=h.length,m},this.beginShadows=function(){s=!0,u(null)},this.endShadows=function(){s=!1},this.setGlobalState=function(h,d){t=u(h,d,0)},this.setState=function(h,d,m){const _=h.clippingPlanes,v=h.clipIntersection,p=h.clipShadows,f=i.get(h);if(!r||_===null||_.length===0||s&&!p)s?u(null):c();else{const E=s?0:n,y=E*4;let T=f.clippingState||null;l.value=T,T=u(_,d,y,m);for(let z=0;z!==y;++z)T[z]=t[z];f.clippingState=T,this.numIntersection=v?this.numPlanes:0,this.numPlanes+=E}};function c(){l.value!==t&&(l.value=t,l.needsUpdate=n>0),e.numPlanes=n,e.numIntersection=0}function u(h,d,m,_){const v=h!==null?h.length:0;let p=null;if(v!==0){if(p=l.value,_!==!0||p===null){const f=m+v*4,E=d.matrixWorldInverse;o.getNormalMatrix(E),(p===null||p.length<f)&&(p=new Float32Array(f));for(let y=0,T=m;y!==v;++y,T+=4)a.copy(h[y]).applyMatrix4(E,o),a.normal.toArray(p,T),p[T+3]=a.constant}l.value=p,l.needsUpdate=!0}return e.numPlanes=v,e.numIntersection=0,p}}function G0(i){let e=new WeakMap;function t(a,o){return o===Hl?a.mapping=Es:o===Vl&&(a.mapping=bs),a}function n(a){if(a&&a.isTexture){const o=a.mapping;if(o===Hl||o===Vl)if(e.has(a)){const l=e.get(a).texture;return t(l,a.mapping)}else{const l=a.image;if(l&&l.height>0){const c=new eg(l.height);return c.fromEquirectangularTexture(i,a),e.set(a,c),a.addEventListener("dispose",r),t(c.texture,a.mapping)}else return null}}return a}function r(a){const o=a.target;o.removeEventListener("dispose",r);const l=e.get(o);l!==void 0&&(e.delete(o),l.dispose())}function s(){e=new WeakMap}return{get:n,dispose:s}}class Ss extends kc{constructor(e=-1,t=1,n=1,r=-1,s=.1,a=2e3){super(),this.isOrthographicCamera=!0,this.type="OrthographicCamera",this.zoom=1,this.view=null,this.left=e,this.right=t,this.top=n,this.bottom=r,this.near=s,this.far=a,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.left=e.left,this.right=e.right,this.top=e.top,this.bottom=e.bottom,this.near=e.near,this.far=e.far,this.zoom=e.zoom,this.view=e.view===null?null:Object.assign({},e.view),this}setViewOffset(e,t,n,r,s,a){this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=n,this.view.offsetY=r,this.view.width=s,this.view.height=a,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const e=(this.right-this.left)/(2*this.zoom),t=(this.top-this.bottom)/(2*this.zoom),n=(this.right+this.left)/2,r=(this.top+this.bottom)/2;let s=n-e,a=n+e,o=r+t,l=r-t;if(this.view!==null&&this.view.enabled){const c=(this.right-this.left)/this.view.fullWidth/this.zoom,u=(this.top-this.bottom)/this.view.fullHeight/this.zoom;s+=c*this.view.offsetX,a=s+c*this.view.width,o-=u*this.view.offsetY,l=o-u*this.view.height}this.projectionMatrix.makeOrthographic(s,a,o,l,this.near,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){const t=super.toJSON(e);return t.object.zoom=this.zoom,t.object.left=this.left,t.object.right=this.right,t.object.top=this.top,t.object.bottom=this.bottom,t.object.near=this.near,t.object.far=this.far,this.view!==null&&(t.object.view=Object.assign({},this.view)),t}}const ms=4,ih=[.125,.215,.35,.446,.526,.582],Mr=20,Ml=new Ss,rh=new nt;let Sl=null,yl=0,El=0,bl=!1;const gr=(1+Math.sqrt(5))/2,ls=1/gr,sh=[new V(-gr,ls,0),new V(gr,ls,0),new V(-ls,0,gr),new V(ls,0,gr),new V(0,gr,-ls),new V(0,gr,ls),new V(-1,1,-1),new V(1,1,-1),new V(-1,1,1),new V(1,1,1)];class ah{constructor(e){this._renderer=e,this._pingPongRenderTarget=null,this._lodMax=0,this._cubeSize=0,this._lodPlanes=[],this._sizeLods=[],this._sigmas=[],this._blurMaterial=null,this._cubemapMaterial=null,this._equirectMaterial=null,this._compileMaterial(this._blurMaterial)}fromScene(e,t=0,n=.1,r=100){Sl=this._renderer.getRenderTarget(),yl=this._renderer.getActiveCubeFace(),El=this._renderer.getActiveMipmapLevel(),bl=this._renderer.xr.enabled,this._renderer.xr.enabled=!1,this._setSize(256);const s=this._allocateTargets();return s.depthBuffer=!0,this._sceneToCubeUV(e,n,r,s),t>0&&this._blur(s,0,0,t),this._applyPMREM(s),this._cleanup(s),s}fromEquirectangular(e,t=null){return this._fromTexture(e,t)}fromCubemap(e,t=null){return this._fromTexture(e,t)}compileCubemapShader(){this._cubemapMaterial===null&&(this._cubemapMaterial=ch(),this._compileMaterial(this._cubemapMaterial))}compileEquirectangularShader(){this._equirectMaterial===null&&(this._equirectMaterial=lh(),this._compileMaterial(this._equirectMaterial))}dispose(){this._dispose(),this._cubemapMaterial!==null&&this._cubemapMaterial.dispose(),this._equirectMaterial!==null&&this._equirectMaterial.dispose()}_setSize(e){this._lodMax=Math.floor(Math.log2(e)),this._cubeSize=Math.pow(2,this._lodMax)}_dispose(){this._blurMaterial!==null&&this._blurMaterial.dispose(),this._pingPongRenderTarget!==null&&this._pingPongRenderTarget.dispose();for(let e=0;e<this._lodPlanes.length;e++)this._lodPlanes[e].dispose()}_cleanup(e){this._renderer.setRenderTarget(Sl,yl,El),this._renderer.xr.enabled=bl,e.scissorTest=!1,Ha(e,0,0,e.width,e.height)}_fromTexture(e,t){e.mapping===Es||e.mapping===bs?this._setSize(e.image.length===0?16:e.image[0].width||e.image[0].image.width):this._setSize(e.image.width/4),Sl=this._renderer.getRenderTarget(),yl=this._renderer.getActiveCubeFace(),El=this._renderer.getActiveMipmapLevel(),bl=this._renderer.xr.enabled,this._renderer.xr.enabled=!1;const n=t||this._allocateTargets();return this._textureToCubeUV(e,n),this._applyPMREM(n),this._cleanup(n),n}_allocateTargets(){const e=3*Math.max(this._cubeSize,112),t=4*this._cubeSize,n={magFilter:ti,minFilter:ti,generateMipmaps:!1,type:ha,format:ri,colorSpace:rr,depthBuffer:!1},r=oh(e,t,n);if(this._pingPongRenderTarget===null||this._pingPongRenderTarget.width!==e||this._pingPongRenderTarget.height!==t){this._pingPongRenderTarget!==null&&this._dispose(),this._pingPongRenderTarget=oh(e,t,n);const{_lodMax:s}=this;({sizeLods:this._sizeLods,lodPlanes:this._lodPlanes,sigmas:this._sigmas}=W0(s)),this._blurMaterial=X0(s,e,t)}return r}_compileMaterial(e){const t=new Rn(this._lodPlanes[0],e);this._renderer.compile(t,Ml)}_sceneToCubeUV(e,t,n,r){const o=new En(90,1,t,n),l=[1,-1,1,1,1,1],c=[1,1,1,-1,-1,-1],u=this._renderer,h=u.autoClear,d=u.toneMapping;u.getClearColor(rh),u.toneMapping=Ji,u.autoClear=!1;const m=new vo({name:"PMREM.Background",side:Cn,depthWrite:!1,depthTest:!1}),_=new Rn(new Qi,m);let v=!1;const p=e.background;p?p.isColor&&(m.color.copy(p),e.background=null,v=!0):(m.color.copy(rh),v=!0);for(let f=0;f<6;f++){const E=f%3;E===0?(o.up.set(0,l[f],0),o.lookAt(c[f],0,0)):E===1?(o.up.set(0,0,l[f]),o.lookAt(0,c[f],0)):(o.up.set(0,l[f],0),o.lookAt(0,0,c[f]));const y=this._cubeSize;Ha(r,E*y,f>2?y:0,y,y),u.setRenderTarget(r),v&&u.render(_,o),u.render(e,o)}_.geometry.dispose(),_.material.dispose(),u.toneMapping=d,u.autoClear=h,e.background=p}_textureToCubeUV(e,t){const n=this._renderer,r=e.mapping===Es||e.mapping===bs;r?(this._cubemapMaterial===null&&(this._cubemapMaterial=ch()),this._cubemapMaterial.uniforms.flipEnvMap.value=e.isRenderTargetTexture===!1?-1:1):this._equirectMaterial===null&&(this._equirectMaterial=lh());const s=r?this._cubemapMaterial:this._equirectMaterial,a=new Rn(this._lodPlanes[0],s),o=s.uniforms;o.envMap.value=e;const l=this._cubeSize;Ha(t,0,0,3*l,2*l),n.setRenderTarget(t),n.render(a,Ml)}_applyPMREM(e){const t=this._renderer,n=t.autoClear;t.autoClear=!1;const r=this._lodPlanes.length;for(let s=1;s<r;s++){const a=Math.sqrt(this._sigmas[s]*this._sigmas[s]-this._sigmas[s-1]*this._sigmas[s-1]),o=sh[(r-s-1)%sh.length];this._blur(e,s-1,s,a,o)}t.autoClear=n}_blur(e,t,n,r,s){const a=this._pingPongRenderTarget;this._halfBlur(e,a,t,n,r,"latitudinal",s),this._halfBlur(a,e,n,n,r,"longitudinal",s)}_halfBlur(e,t,n,r,s,a,o){const l=this._renderer,c=this._blurMaterial;a!=="latitudinal"&&a!=="longitudinal"&&console.error("blur direction must be either latitudinal or longitudinal!");const u=3,h=new Rn(this._lodPlanes[r],c),d=c.uniforms,m=this._sizeLods[n]-1,_=isFinite(s)?Math.PI/(2*m):2*Math.PI/(2*Mr-1),v=s/_,p=isFinite(s)?1+Math.floor(u*v):Mr;p>Mr&&console.warn(`sigmaRadians, ${s}, is too large and will clip, as it requested ${p} samples when the maximum is set to ${Mr}`);const f=[];let E=0;for(let D=0;D<Mr;++D){const B=D/v,w=Math.exp(-B*B/2);f.push(w),D===0?E+=w:D<p&&(E+=2*w)}for(let D=0;D<f.length;D++)f[D]=f[D]/E;d.envMap.value=e.texture,d.samples.value=p,d.weights.value=f,d.latitudinal.value=a==="latitudinal",o&&(d.poleAxis.value=o);const{_lodMax:y}=this;d.dTheta.value=_,d.mipInt.value=y-n;const T=this._sizeLods[r],z=3*T*(r>y-ms?r-y+ms:0),C=4*(this._cubeSize-T);Ha(t,z,C,3*T,2*T),l.setRenderTarget(t),l.render(h,Ml)}}function W0(i){const e=[],t=[],n=[];let r=i;const s=i-ms+1+ih.length;for(let a=0;a<s;a++){const o=Math.pow(2,r);t.push(o);let l=1/o;a>i-ms?l=ih[a-i+ms-1]:a===0&&(l=0),n.push(l);const c=1/(o-2),u=-c,h=1+c,d=[u,u,h,u,h,h,u,u,h,h,u,h],m=6,_=6,v=3,p=2,f=1,E=new Float32Array(v*_*m),y=new Float32Array(p*_*m),T=new Float32Array(f*_*m);for(let C=0;C<m;C++){const D=C%3*2/3-1,B=C>2?0:-1,w=[D,B,0,D+2/3,B,0,D+2/3,B+1,0,D,B,0,D+2/3,B+1,0,D,B+1,0];E.set(w,v*_*C),y.set(d,p*_*C);const x=[C,C,C,C,C,C];T.set(x,f*_*C)}const z=new gn;z.setAttribute("position",new Xn(E,v)),z.setAttribute("uv",new Xn(y,p)),z.setAttribute("faceIndex",new Xn(T,f)),e.push(z),r>ms&&r--}return{lodPlanes:e,sizeLods:t,sigmas:n}}function oh(i,e,t){const n=new Ar(i,e,t);return n.texture.mapping=Ao,n.texture.name="PMREM.cubeUv",n.scissorTest=!0,n}function Ha(i,e,t,n,r){i.viewport.set(e,t,n,r),i.scissor.set(e,t,n,r)}function X0(i,e,t){const n=new Float32Array(Mr),r=new V(0,1,0);return new tr({name:"SphericalGaussianBlur",defines:{n:Mr,CUBEUV_TEXEL_WIDTH:1/e,CUBEUV_TEXEL_HEIGHT:1/t,CUBEUV_MAX_MIP:`${i}.0`},uniforms:{envMap:{value:null},samples:{value:1},weights:{value:n},latitudinal:{value:!1},dTheta:{value:0},mipInt:{value:0},poleAxis:{value:r}},vertexShader:Vc(),fragmentShader:`

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
		`,blending:Zi,depthTest:!1,depthWrite:!1})}function lh(){return new tr({name:"EquirectangularToCubeUV",uniforms:{envMap:{value:null}},vertexShader:Vc(),fragmentShader:`

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
		`,blending:Zi,depthTest:!1,depthWrite:!1})}function ch(){return new tr({name:"CubemapToCubeUV",uniforms:{envMap:{value:null},flipEnvMap:{value:-1}},vertexShader:Vc(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			uniform float flipEnvMap;

			varying vec3 vOutputDirection;

			uniform samplerCube envMap;

			void main() {

				gl_FragColor = textureCube( envMap, vec3( flipEnvMap * vOutputDirection.x, vOutputDirection.yz ) );

			}
		`,blending:Zi,depthTest:!1,depthWrite:!1})}function Vc(){return`

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
	`}function Y0(i){let e=new WeakMap,t=null;function n(o){if(o&&o.isTexture){const l=o.mapping,c=l===Hl||l===Vl,u=l===Es||l===bs;if(c||u){let h=e.get(o);const d=h!==void 0?h.texture.pmremVersion:0;if(o.isRenderTargetTexture&&o.pmremVersion!==d)return t===null&&(t=new ah(i)),h=c?t.fromEquirectangular(o,h):t.fromCubemap(o,h),h.texture.pmremVersion=o.pmremVersion,e.set(o,h),h.texture;if(h!==void 0)return h.texture;{const m=o.image;return c&&m&&m.height>0||u&&m&&r(m)?(t===null&&(t=new ah(i)),h=c?t.fromEquirectangular(o):t.fromCubemap(o),h.texture.pmremVersion=o.pmremVersion,e.set(o,h),o.addEventListener("dispose",s),h.texture):null}}}return o}function r(o){let l=0;const c=6;for(let u=0;u<c;u++)o[u]!==void 0&&l++;return l===c}function s(o){const l=o.target;l.removeEventListener("dispose",s);const c=e.get(l);c!==void 0&&(e.delete(l),c.dispose())}function a(){e=new WeakMap,t!==null&&(t.dispose(),t=null)}return{get:n,dispose:a}}function q0(i){const e={};function t(n){if(e[n]!==void 0)return e[n];let r;switch(n){case"WEBGL_depth_texture":r=i.getExtension("WEBGL_depth_texture")||i.getExtension("MOZ_WEBGL_depth_texture")||i.getExtension("WEBKIT_WEBGL_depth_texture");break;case"EXT_texture_filter_anisotropic":r=i.getExtension("EXT_texture_filter_anisotropic")||i.getExtension("MOZ_EXT_texture_filter_anisotropic")||i.getExtension("WEBKIT_EXT_texture_filter_anisotropic");break;case"WEBGL_compressed_texture_s3tc":r=i.getExtension("WEBGL_compressed_texture_s3tc")||i.getExtension("MOZ_WEBGL_compressed_texture_s3tc")||i.getExtension("WEBKIT_WEBGL_compressed_texture_s3tc");break;case"WEBGL_compressed_texture_pvrtc":r=i.getExtension("WEBGL_compressed_texture_pvrtc")||i.getExtension("WEBKIT_WEBGL_compressed_texture_pvrtc");break;default:r=i.getExtension(n)}return e[n]=r,r}return{has:function(n){return t(n)!==null},init:function(){t("EXT_color_buffer_float"),t("WEBGL_clip_cull_distance"),t("OES_texture_float_linear"),t("EXT_color_buffer_half_float"),t("WEBGL_multisampled_render_to_texture"),t("WEBGL_render_shared_exponent")},get:function(n){const r=t(n);return r===null&&xs("THREE.WebGLRenderer: "+n+" extension not supported."),r}}}function $0(i,e,t,n){const r={},s=new WeakMap;function a(h){const d=h.target;d.index!==null&&e.remove(d.index);for(const _ in d.attributes)e.remove(d.attributes[_]);for(const _ in d.morphAttributes){const v=d.morphAttributes[_];for(let p=0,f=v.length;p<f;p++)e.remove(v[p])}d.removeEventListener("dispose",a),delete r[d.id];const m=s.get(d);m&&(e.remove(m),s.delete(d)),n.releaseStatesOfGeometry(d),d.isInstancedBufferGeometry===!0&&delete d._maxInstanceCount,t.memory.geometries--}function o(h,d){return r[d.id]===!0||(d.addEventListener("dispose",a),r[d.id]=!0,t.memory.geometries++),d}function l(h){const d=h.attributes;for(const _ in d)e.update(d[_],i.ARRAY_BUFFER);const m=h.morphAttributes;for(const _ in m){const v=m[_];for(let p=0,f=v.length;p<f;p++)e.update(v[p],i.ARRAY_BUFFER)}}function c(h){const d=[],m=h.index,_=h.attributes.position;let v=0;if(m!==null){const E=m.array;v=m.version;for(let y=0,T=E.length;y<T;y+=3){const z=E[y+0],C=E[y+1],D=E[y+2];d.push(z,C,C,D,D,z)}}else if(_!==void 0){const E=_.array;v=_.version;for(let y=0,T=E.length/3-1;y<T;y+=3){const z=y+0,C=y+1,D=y+2;d.push(z,C,C,D,D,z)}}else return;const p=new(Xd(d)?Kd:jd)(d,1);p.version=v;const f=s.get(h);f&&e.remove(f),s.set(h,p)}function u(h){const d=s.get(h);if(d){const m=h.index;m!==null&&d.version<m.version&&c(h)}else c(h);return s.get(h)}return{get:o,update:l,getWireframeAttribute:u}}function j0(i,e,t){let n;function r(d){n=d}let s,a;function o(d){s=d.type,a=d.bytesPerElement}function l(d,m){i.drawElements(n,m,s,d*a),t.update(m,n,1)}function c(d,m,_){_!==0&&(i.drawElementsInstanced(n,m,s,d*a,_),t.update(m,n,_))}function u(d,m,_){if(_===0)return;e.get("WEBGL_multi_draw").multiDrawElementsWEBGL(n,m,0,s,d,0,_);let p=0;for(let f=0;f<_;f++)p+=m[f];t.update(p,n,1)}function h(d,m,_,v){if(_===0)return;const p=e.get("WEBGL_multi_draw");if(p===null)for(let f=0;f<d.length;f++)c(d[f]/a,m[f],v[f]);else{p.multiDrawElementsInstancedWEBGL(n,m,0,s,d,0,v,0,_);let f=0;for(let E=0;E<_;E++)f+=m[E];for(let E=0;E<v.length;E++)t.update(f,n,v[E])}}this.setMode=r,this.setIndex=o,this.render=l,this.renderInstances=c,this.renderMultiDraw=u,this.renderMultiDrawInstances=h}function K0(i){const e={geometries:0,textures:0},t={frame:0,calls:0,triangles:0,points:0,lines:0};function n(s,a,o){switch(t.calls++,a){case i.TRIANGLES:t.triangles+=o*(s/3);break;case i.LINES:t.lines+=o*(s/2);break;case i.LINE_STRIP:t.lines+=o*(s-1);break;case i.LINE_LOOP:t.lines+=o*s;break;case i.POINTS:t.points+=o*s;break;default:console.error("THREE.WebGLInfo: Unknown draw mode:",a);break}}function r(){t.calls=0,t.triangles=0,t.points=0,t.lines=0}return{memory:e,render:t,programs:null,autoReset:!0,reset:r,update:n}}function Z0(i,e,t){const n=new WeakMap,r=new jt;function s(a,o,l){const c=a.morphTargetInfluences,u=o.morphAttributes.position||o.morphAttributes.normal||o.morphAttributes.color,h=u!==void 0?u.length:0;let d=n.get(o);if(d===void 0||d.count!==h){let x=function(){B.dispose(),n.delete(o),o.removeEventListener("dispose",x)};var m=x;d!==void 0&&d.texture.dispose();const _=o.morphAttributes.position!==void 0,v=o.morphAttributes.normal!==void 0,p=o.morphAttributes.color!==void 0,f=o.morphAttributes.position||[],E=o.morphAttributes.normal||[],y=o.morphAttributes.color||[];let T=0;_===!0&&(T=1),v===!0&&(T=2),p===!0&&(T=3);let z=o.attributes.position.count*T,C=1;z>e.maxTextureSize&&(C=Math.ceil(z/e.maxTextureSize),z=e.maxTextureSize);const D=new Float32Array(z*C*4*h),B=new qd(D,z,C,h);B.type=Ci,B.needsUpdate=!0;const w=T*4;for(let R=0;R<h;R++){const j=f[R],O=E[R],K=y[R],W=z*C*4*R;for(let J=0;J<j.count;J++){const Y=J*w;_===!0&&(r.fromBufferAttribute(j,J),D[W+Y+0]=r.x,D[W+Y+1]=r.y,D[W+Y+2]=r.z,D[W+Y+3]=0),v===!0&&(r.fromBufferAttribute(O,J),D[W+Y+4]=r.x,D[W+Y+5]=r.y,D[W+Y+6]=r.z,D[W+Y+7]=0),p===!0&&(r.fromBufferAttribute(K,J),D[W+Y+8]=r.x,D[W+Y+9]=r.y,D[W+Y+10]=r.z,D[W+Y+11]=K.itemSize===4?r.w:1)}}d={count:h,texture:B,size:new Xe(z,C)},n.set(o,d),o.addEventListener("dispose",x)}if(a.isInstancedMesh===!0&&a.morphTexture!==null)l.getUniforms().setValue(i,"morphTexture",a.morphTexture,t);else{let _=0;for(let p=0;p<c.length;p++)_+=c[p];const v=o.morphTargetsRelative?1:1-_;l.getUniforms().setValue(i,"morphTargetBaseInfluence",v),l.getUniforms().setValue(i,"morphTargetInfluences",c)}l.getUniforms().setValue(i,"morphTargetsTexture",d.texture,t),l.getUniforms().setValue(i,"morphTargetsTextureSize",d.size)}return{update:s}}function J0(i,e,t,n){let r=new WeakMap;function s(l){const c=n.render.frame,u=l.geometry,h=e.get(l,u);if(r.get(h)!==c&&(e.update(h),r.set(h,c)),l.isInstancedMesh&&(l.hasEventListener("dispose",o)===!1&&l.addEventListener("dispose",o),r.get(l)!==c&&(t.update(l.instanceMatrix,i.ARRAY_BUFFER),l.instanceColor!==null&&t.update(l.instanceColor,i.ARRAY_BUFFER),r.set(l,c))),l.isSkinnedMesh){const d=l.skeleton;r.get(d)!==c&&(d.update(),r.set(d,c))}return h}function a(){r=new WeakMap}function o(l){const c=l.target;c.removeEventListener("dispose",o),t.remove(c.instanceMatrix),c.instanceColor!==null&&t.remove(c.instanceColor)}return{update:s,dispose:a}}class ef extends Tn{constructor(e,t,n,r,s,a,o,l,c,u=_s){if(u!==_s&&u!==ws)throw new Error("DepthTexture format must be either THREE.DepthFormat or THREE.DepthStencilFormat");n===void 0&&u===_s&&(n=wr),n===void 0&&u===ws&&(n=Ts),super(null,r,s,a,o,l,u,n,c),this.isDepthTexture=!0,this.image={width:e,height:t},this.magFilter=o!==void 0?o:Wn,this.minFilter=l!==void 0?l:Wn,this.flipY=!1,this.generateMipmaps=!1,this.compareFunction=null}copy(e){return super.copy(e),this.compareFunction=e.compareFunction,this}toJSON(e){const t=super.toJSON(e);return this.compareFunction!==null&&(t.compareFunction=this.compareFunction),t}}const tf=new Tn,uh=new ef(1,1),nf=new qd,rf=new Bm,sf=new Jd,hh=[],dh=[],fh=new Float32Array(16),ph=new Float32Array(9),mh=new Float32Array(4);function Is(i,e,t){const n=i[0];if(n<=0||n>0)return i;const r=e*t;let s=hh[r];if(s===void 0&&(s=new Float32Array(r),hh[r]=s),e!==0){n.toArray(s,0);for(let a=1,o=0;a!==e;++a)o+=t,i[a].toArray(s,o)}return s}function Zt(i,e){if(i.length!==e.length)return!1;for(let t=0,n=i.length;t<n;t++)if(i[t]!==e[t])return!1;return!0}function Jt(i,e){for(let t=0,n=e.length;t<n;t++)i[t]=e[t]}function Do(i,e){let t=dh[e];t===void 0&&(t=new Int32Array(e),dh[e]=t);for(let n=0;n!==e;++n)t[n]=i.allocateTextureUnit();return t}function Q0(i,e){const t=this.cache;t[0]!==e&&(i.uniform1f(this.addr,e),t[0]=e)}function ev(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(i.uniform2f(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(Zt(t,e))return;i.uniform2fv(this.addr,e),Jt(t,e)}}function tv(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(i.uniform3f(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else if(e.r!==void 0)(t[0]!==e.r||t[1]!==e.g||t[2]!==e.b)&&(i.uniform3f(this.addr,e.r,e.g,e.b),t[0]=e.r,t[1]=e.g,t[2]=e.b);else{if(Zt(t,e))return;i.uniform3fv(this.addr,e),Jt(t,e)}}function nv(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(i.uniform4f(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(Zt(t,e))return;i.uniform4fv(this.addr,e),Jt(t,e)}}function iv(i,e){const t=this.cache,n=e.elements;if(n===void 0){if(Zt(t,e))return;i.uniformMatrix2fv(this.addr,!1,e),Jt(t,e)}else{if(Zt(t,n))return;mh.set(n),i.uniformMatrix2fv(this.addr,!1,mh),Jt(t,n)}}function rv(i,e){const t=this.cache,n=e.elements;if(n===void 0){if(Zt(t,e))return;i.uniformMatrix3fv(this.addr,!1,e),Jt(t,e)}else{if(Zt(t,n))return;ph.set(n),i.uniformMatrix3fv(this.addr,!1,ph),Jt(t,n)}}function sv(i,e){const t=this.cache,n=e.elements;if(n===void 0){if(Zt(t,e))return;i.uniformMatrix4fv(this.addr,!1,e),Jt(t,e)}else{if(Zt(t,n))return;fh.set(n),i.uniformMatrix4fv(this.addr,!1,fh),Jt(t,n)}}function av(i,e){const t=this.cache;t[0]!==e&&(i.uniform1i(this.addr,e),t[0]=e)}function ov(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(i.uniform2i(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(Zt(t,e))return;i.uniform2iv(this.addr,e),Jt(t,e)}}function lv(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(i.uniform3i(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(Zt(t,e))return;i.uniform3iv(this.addr,e),Jt(t,e)}}function cv(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(i.uniform4i(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(Zt(t,e))return;i.uniform4iv(this.addr,e),Jt(t,e)}}function uv(i,e){const t=this.cache;t[0]!==e&&(i.uniform1ui(this.addr,e),t[0]=e)}function hv(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(i.uniform2ui(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(Zt(t,e))return;i.uniform2uiv(this.addr,e),Jt(t,e)}}function dv(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(i.uniform3ui(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(Zt(t,e))return;i.uniform3uiv(this.addr,e),Jt(t,e)}}function fv(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(i.uniform4ui(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(Zt(t,e))return;i.uniform4uiv(this.addr,e),Jt(t,e)}}function pv(i,e,t){const n=this.cache,r=t.allocateTextureUnit();n[0]!==r&&(i.uniform1i(this.addr,r),n[0]=r);let s;this.type===i.SAMPLER_2D_SHADOW?(uh.compareFunction=Wd,s=uh):s=tf,t.setTexture2D(e||s,r)}function mv(i,e,t){const n=this.cache,r=t.allocateTextureUnit();n[0]!==r&&(i.uniform1i(this.addr,r),n[0]=r),t.setTexture3D(e||rf,r)}function gv(i,e,t){const n=this.cache,r=t.allocateTextureUnit();n[0]!==r&&(i.uniform1i(this.addr,r),n[0]=r),t.setTextureCube(e||sf,r)}function _v(i,e,t){const n=this.cache,r=t.allocateTextureUnit();n[0]!==r&&(i.uniform1i(this.addr,r),n[0]=r),t.setTexture2DArray(e||nf,r)}function vv(i){switch(i){case 5126:return Q0;case 35664:return ev;case 35665:return tv;case 35666:return nv;case 35674:return iv;case 35675:return rv;case 35676:return sv;case 5124:case 35670:return av;case 35667:case 35671:return ov;case 35668:case 35672:return lv;case 35669:case 35673:return cv;case 5125:return uv;case 36294:return hv;case 36295:return dv;case 36296:return fv;case 35678:case 36198:case 36298:case 36306:case 35682:return pv;case 35679:case 36299:case 36307:return mv;case 35680:case 36300:case 36308:case 36293:return gv;case 36289:case 36303:case 36311:case 36292:return _v}}function xv(i,e){i.uniform1fv(this.addr,e)}function Mv(i,e){const t=Is(e,this.size,2);i.uniform2fv(this.addr,t)}function Sv(i,e){const t=Is(e,this.size,3);i.uniform3fv(this.addr,t)}function yv(i,e){const t=Is(e,this.size,4);i.uniform4fv(this.addr,t)}function Ev(i,e){const t=Is(e,this.size,4);i.uniformMatrix2fv(this.addr,!1,t)}function bv(i,e){const t=Is(e,this.size,9);i.uniformMatrix3fv(this.addr,!1,t)}function Tv(i,e){const t=Is(e,this.size,16);i.uniformMatrix4fv(this.addr,!1,t)}function wv(i,e){i.uniform1iv(this.addr,e)}function Av(i,e){i.uniform2iv(this.addr,e)}function Rv(i,e){i.uniform3iv(this.addr,e)}function Cv(i,e){i.uniform4iv(this.addr,e)}function Pv(i,e){i.uniform1uiv(this.addr,e)}function Lv(i,e){i.uniform2uiv(this.addr,e)}function Dv(i,e){i.uniform3uiv(this.addr,e)}function Iv(i,e){i.uniform4uiv(this.addr,e)}function Uv(i,e,t){const n=this.cache,r=e.length,s=Do(t,r);Zt(n,s)||(i.uniform1iv(this.addr,s),Jt(n,s));for(let a=0;a!==r;++a)t.setTexture2D(e[a]||tf,s[a])}function Nv(i,e,t){const n=this.cache,r=e.length,s=Do(t,r);Zt(n,s)||(i.uniform1iv(this.addr,s),Jt(n,s));for(let a=0;a!==r;++a)t.setTexture3D(e[a]||rf,s[a])}function Fv(i,e,t){const n=this.cache,r=e.length,s=Do(t,r);Zt(n,s)||(i.uniform1iv(this.addr,s),Jt(n,s));for(let a=0;a!==r;++a)t.setTextureCube(e[a]||sf,s[a])}function Ov(i,e,t){const n=this.cache,r=e.length,s=Do(t,r);Zt(n,s)||(i.uniform1iv(this.addr,s),Jt(n,s));for(let a=0;a!==r;++a)t.setTexture2DArray(e[a]||nf,s[a])}function Bv(i){switch(i){case 5126:return xv;case 35664:return Mv;case 35665:return Sv;case 35666:return yv;case 35674:return Ev;case 35675:return bv;case 35676:return Tv;case 5124:case 35670:return wv;case 35667:case 35671:return Av;case 35668:case 35672:return Rv;case 35669:case 35673:return Cv;case 5125:return Pv;case 36294:return Lv;case 36295:return Dv;case 36296:return Iv;case 35678:case 36198:case 36298:case 36306:case 35682:return Uv;case 35679:case 36299:case 36307:return Nv;case 35680:case 36300:case 36308:case 36293:return Fv;case 36289:case 36303:case 36311:case 36292:return Ov}}class zv{constructor(e,t,n){this.id=e,this.addr=n,this.cache=[],this.type=t.type,this.setValue=vv(t.type)}}class kv{constructor(e,t,n){this.id=e,this.addr=n,this.cache=[],this.type=t.type,this.size=t.size,this.setValue=Bv(t.type)}}class Hv{constructor(e){this.id=e,this.seq=[],this.map={}}setValue(e,t,n){const r=this.seq;for(let s=0,a=r.length;s!==a;++s){const o=r[s];o.setValue(e,t[o.id],n)}}}const Tl=/(\w+)(\])?(\[|\.)?/g;function gh(i,e){i.seq.push(e),i.map[e.id]=e}function Vv(i,e,t){const n=i.name,r=n.length;for(Tl.lastIndex=0;;){const s=Tl.exec(n),a=Tl.lastIndex;let o=s[1];const l=s[2]==="]",c=s[3];if(l&&(o=o|0),c===void 0||c==="["&&a+2===r){gh(t,c===void 0?new zv(o,i,e):new kv(o,i,e));break}else{let h=t.map[o];h===void 0&&(h=new Hv(o),gh(t,h)),t=h}}}class lo{constructor(e,t){this.seq=[],this.map={};const n=e.getProgramParameter(t,e.ACTIVE_UNIFORMS);for(let r=0;r<n;++r){const s=e.getActiveUniform(t,r),a=e.getUniformLocation(t,s.name);Vv(s,a,this)}}setValue(e,t,n,r){const s=this.map[t];s!==void 0&&s.setValue(e,n,r)}setOptional(e,t,n){const r=t[n];r!==void 0&&this.setValue(e,n,r)}static upload(e,t,n,r){for(let s=0,a=t.length;s!==a;++s){const o=t[s],l=n[o.id];l.needsUpdate!==!1&&o.setValue(e,l.value,r)}}static seqWithValue(e,t){const n=[];for(let r=0,s=e.length;r!==s;++r){const a=e[r];a.id in t&&n.push(a)}return n}}function _h(i,e,t){const n=i.createShader(e);return i.shaderSource(n,t),i.compileShader(n),n}const Gv=37297;let Wv=0;function Xv(i,e){const t=i.split(`
`),n=[],r=Math.max(e-6,0),s=Math.min(e+6,t.length);for(let a=r;a<s;a++){const o=a+1;n.push(`${o===e?">":" "} ${o}: ${t[a]}`)}return n.join(`
`)}function Yv(i){const e=St.getPrimaries(St.workingColorSpace),t=St.getPrimaries(i);let n;switch(e===t?n="":e===mo&&t===po?n="LinearDisplayP3ToLinearSRGB":e===po&&t===mo&&(n="LinearSRGBToLinearDisplayP3"),i){case rr:case Ro:return[n,"LinearTransferOETF"];case fi:case Oc:return[n,"sRGBTransferOETF"];default:return console.warn("THREE.WebGLProgram: Unsupported color space:",i),[n,"LinearTransferOETF"]}}function vh(i,e,t){const n=i.getShaderParameter(e,i.COMPILE_STATUS),r=i.getShaderInfoLog(e).trim();if(n&&r==="")return"";const s=/ERROR: 0:(\d+)/.exec(r);if(s){const a=parseInt(s[1]);return t.toUpperCase()+`

`+r+`

`+Xv(i.getShaderSource(e),a)}else return r}function qv(i,e){const t=Yv(e);return`vec4 ${i}( vec4 value ) { return ${t[0]}( ${t[1]}( value ) ); }`}function $v(i,e){let t;switch(e){case Jp:t="Linear";break;case Qp:t="Reinhard";break;case em:t="Cineon";break;case Ld:t="ACESFilmic";break;case nm:t="AgX";break;case im:t="Neutral";break;case tm:t="Custom";break;default:console.warn("THREE.WebGLProgram: Unsupported toneMapping:",e),t="Linear"}return"vec3 "+i+"( vec3 color ) { return "+t+"ToneMapping( color ); }"}const Va=new V;function jv(){St.getLuminanceCoefficients(Va);const i=Va.x.toFixed(4),e=Va.y.toFixed(4),t=Va.z.toFixed(4);return["float luminance( const in vec3 rgb ) {",`	const vec3 weights = vec3( ${i}, ${e}, ${t} );`,"	return dot( weights, rgb );","}"].join(`
`)}function Kv(i){return[i.extensionClipCullDistance?"#extension GL_ANGLE_clip_cull_distance : require":"",i.extensionMultiDraw?"#extension GL_ANGLE_multi_draw : require":""].filter(ta).join(`
`)}function Zv(i){const e=[];for(const t in i){const n=i[t];n!==!1&&e.push("#define "+t+" "+n)}return e.join(`
`)}function Jv(i,e){const t={},n=i.getProgramParameter(e,i.ACTIVE_ATTRIBUTES);for(let r=0;r<n;r++){const s=i.getActiveAttrib(e,r),a=s.name;let o=1;s.type===i.FLOAT_MAT2&&(o=2),s.type===i.FLOAT_MAT3&&(o=3),s.type===i.FLOAT_MAT4&&(o=4),t[a]={type:s.type,location:i.getAttribLocation(e,a),locationSize:o}}return t}function ta(i){return i!==""}function xh(i,e){const t=e.numSpotLightShadows+e.numSpotLightMaps-e.numSpotLightShadowsWithMaps;return i.replace(/NUM_DIR_LIGHTS/g,e.numDirLights).replace(/NUM_SPOT_LIGHTS/g,e.numSpotLights).replace(/NUM_SPOT_LIGHT_MAPS/g,e.numSpotLightMaps).replace(/NUM_SPOT_LIGHT_COORDS/g,t).replace(/NUM_RECT_AREA_LIGHTS/g,e.numRectAreaLights).replace(/NUM_POINT_LIGHTS/g,e.numPointLights).replace(/NUM_HEMI_LIGHTS/g,e.numHemiLights).replace(/NUM_DIR_LIGHT_SHADOWS/g,e.numDirLightShadows).replace(/NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS/g,e.numSpotLightShadowsWithMaps).replace(/NUM_SPOT_LIGHT_SHADOWS/g,e.numSpotLightShadows).replace(/NUM_POINT_LIGHT_SHADOWS/g,e.numPointLightShadows)}function Mh(i,e){return i.replace(/NUM_CLIPPING_PLANES/g,e.numClippingPlanes).replace(/UNION_CLIPPING_PLANES/g,e.numClippingPlanes-e.numClipIntersection)}const Qv=/^[ \t]*#include +<([\w\d./]+)>/gm;function vc(i){return i.replace(Qv,tx)}const ex=new Map;function tx(i,e){let t=it[e];if(t===void 0){const n=ex.get(e);if(n!==void 0)t=it[n],console.warn('THREE.WebGLRenderer: Shader chunk "%s" has been deprecated. Use "%s" instead.',e,n);else throw new Error("Can not resolve #include <"+e+">")}return vc(t)}const nx=/#pragma unroll_loop_start\s+for\s*\(\s*int\s+i\s*=\s*(\d+)\s*;\s*i\s*<\s*(\d+)\s*;\s*i\s*\+\+\s*\)\s*{([\s\S]+?)}\s+#pragma unroll_loop_end/g;function Sh(i){return i.replace(nx,ix)}function ix(i,e,t,n){let r="";for(let s=parseInt(e);s<parseInt(t);s++)r+=n.replace(/\[\s*i\s*\]/g,"[ "+s+" ]").replace(/UNROLLED_LOOP_INDEX/g,s);return r}function yh(i){let e=`precision ${i.precision} float;
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
#define LOW_PRECISION`),e}function rx(i){let e="SHADOWMAP_TYPE_BASIC";return i.shadowMapType===Rd?e="SHADOWMAP_TYPE_PCF":i.shadowMapType===Cd?e="SHADOWMAP_TYPE_PCF_SOFT":i.shadowMapType===Ai&&(e="SHADOWMAP_TYPE_VSM"),e}function sx(i){let e="ENVMAP_TYPE_CUBE";if(i.envMap)switch(i.envMapMode){case Es:case bs:e="ENVMAP_TYPE_CUBE";break;case Ao:e="ENVMAP_TYPE_CUBE_UV";break}return e}function ax(i){let e="ENVMAP_MODE_REFLECTION";if(i.envMap)switch(i.envMapMode){case bs:e="ENVMAP_MODE_REFRACTION";break}return e}function ox(i){let e="ENVMAP_BLENDING_NONE";if(i.envMap)switch(i.combine){case Pd:e="ENVMAP_BLENDING_MULTIPLY";break;case Kp:e="ENVMAP_BLENDING_MIX";break;case Zp:e="ENVMAP_BLENDING_ADD";break}return e}function lx(i){const e=i.envMapCubeUVHeight;if(e===null)return null;const t=Math.log2(e)-2,n=1/e;return{texelWidth:1/(3*Math.max(Math.pow(2,t),7*16)),texelHeight:n,maxMip:t}}function cx(i,e,t,n){const r=i.getContext(),s=t.defines;let a=t.vertexShader,o=t.fragmentShader;const l=rx(t),c=sx(t),u=ax(t),h=ox(t),d=lx(t),m=Kv(t),_=Zv(s),v=r.createProgram();let p,f,E=t.glslVersion?"#version "+t.glslVersion+`
`:"";t.isRawShaderMaterial?(p=["#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,_].filter(ta).join(`
`),p.length>0&&(p+=`
`),f=["#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,_].filter(ta).join(`
`),f.length>0&&(f+=`
`)):(p=[yh(t),"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,_,t.extensionClipCullDistance?"#define USE_CLIP_DISTANCE":"",t.batching?"#define USE_BATCHING":"",t.batchingColor?"#define USE_BATCHING_COLOR":"",t.instancing?"#define USE_INSTANCING":"",t.instancingColor?"#define USE_INSTANCING_COLOR":"",t.instancingMorph?"#define USE_INSTANCING_MORPH":"",t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.map?"#define USE_MAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+u:"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",t.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",t.displacementMap?"#define USE_DISPLACEMENTMAP":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.anisotropy?"#define USE_ANISOTROPY":"",t.anisotropyMap?"#define USE_ANISOTROPYMAP":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",t.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaHash?"#define USE_ALPHAHASH":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",t.mapUv?"#define MAP_UV "+t.mapUv:"",t.alphaMapUv?"#define ALPHAMAP_UV "+t.alphaMapUv:"",t.lightMapUv?"#define LIGHTMAP_UV "+t.lightMapUv:"",t.aoMapUv?"#define AOMAP_UV "+t.aoMapUv:"",t.emissiveMapUv?"#define EMISSIVEMAP_UV "+t.emissiveMapUv:"",t.bumpMapUv?"#define BUMPMAP_UV "+t.bumpMapUv:"",t.normalMapUv?"#define NORMALMAP_UV "+t.normalMapUv:"",t.displacementMapUv?"#define DISPLACEMENTMAP_UV "+t.displacementMapUv:"",t.metalnessMapUv?"#define METALNESSMAP_UV "+t.metalnessMapUv:"",t.roughnessMapUv?"#define ROUGHNESSMAP_UV "+t.roughnessMapUv:"",t.anisotropyMapUv?"#define ANISOTROPYMAP_UV "+t.anisotropyMapUv:"",t.clearcoatMapUv?"#define CLEARCOATMAP_UV "+t.clearcoatMapUv:"",t.clearcoatNormalMapUv?"#define CLEARCOAT_NORMALMAP_UV "+t.clearcoatNormalMapUv:"",t.clearcoatRoughnessMapUv?"#define CLEARCOAT_ROUGHNESSMAP_UV "+t.clearcoatRoughnessMapUv:"",t.iridescenceMapUv?"#define IRIDESCENCEMAP_UV "+t.iridescenceMapUv:"",t.iridescenceThicknessMapUv?"#define IRIDESCENCE_THICKNESSMAP_UV "+t.iridescenceThicknessMapUv:"",t.sheenColorMapUv?"#define SHEEN_COLORMAP_UV "+t.sheenColorMapUv:"",t.sheenRoughnessMapUv?"#define SHEEN_ROUGHNESSMAP_UV "+t.sheenRoughnessMapUv:"",t.specularMapUv?"#define SPECULARMAP_UV "+t.specularMapUv:"",t.specularColorMapUv?"#define SPECULAR_COLORMAP_UV "+t.specularColorMapUv:"",t.specularIntensityMapUv?"#define SPECULAR_INTENSITYMAP_UV "+t.specularIntensityMapUv:"",t.transmissionMapUv?"#define TRANSMISSIONMAP_UV "+t.transmissionMapUv:"",t.thicknessMapUv?"#define THICKNESSMAP_UV "+t.thicknessMapUv:"",t.vertexTangents&&t.flatShading===!1?"#define USE_TANGENT":"",t.vertexColors?"#define USE_COLOR":"",t.vertexAlphas?"#define USE_COLOR_ALPHA":"",t.vertexUv1s?"#define USE_UV1":"",t.vertexUv2s?"#define USE_UV2":"",t.vertexUv3s?"#define USE_UV3":"",t.pointsUvs?"#define USE_POINTS_UV":"",t.flatShading?"#define FLAT_SHADED":"",t.skinning?"#define USE_SKINNING":"",t.morphTargets?"#define USE_MORPHTARGETS":"",t.morphNormals&&t.flatShading===!1?"#define USE_MORPHNORMALS":"",t.morphColors?"#define USE_MORPHCOLORS":"",t.morphTargetsCount>0?"#define MORPHTARGETS_TEXTURE_STRIDE "+t.morphTextureStride:"",t.morphTargetsCount>0?"#define MORPHTARGETS_COUNT "+t.morphTargetsCount:"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+l:"",t.sizeAttenuation?"#define USE_SIZEATTENUATION":"",t.numLightProbes>0?"#define USE_LIGHT_PROBES":"",t.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"","uniform mat4 modelMatrix;","uniform mat4 modelViewMatrix;","uniform mat4 projectionMatrix;","uniform mat4 viewMatrix;","uniform mat3 normalMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;","#ifdef USE_INSTANCING","	attribute mat4 instanceMatrix;","#endif","#ifdef USE_INSTANCING_COLOR","	attribute vec3 instanceColor;","#endif","#ifdef USE_INSTANCING_MORPH","	uniform sampler2D morphTexture;","#endif","attribute vec3 position;","attribute vec3 normal;","attribute vec2 uv;","#ifdef USE_UV1","	attribute vec2 uv1;","#endif","#ifdef USE_UV2","	attribute vec2 uv2;","#endif","#ifdef USE_UV3","	attribute vec2 uv3;","#endif","#ifdef USE_TANGENT","	attribute vec4 tangent;","#endif","#if defined( USE_COLOR_ALPHA )","	attribute vec4 color;","#elif defined( USE_COLOR )","	attribute vec3 color;","#endif","#ifdef USE_SKINNING","	attribute vec4 skinIndex;","	attribute vec4 skinWeight;","#endif",`
`].filter(ta).join(`
`),f=[yh(t),"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,_,t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.alphaToCoverage?"#define ALPHA_TO_COVERAGE":"",t.map?"#define USE_MAP":"",t.matcap?"#define USE_MATCAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+c:"",t.envMap?"#define "+u:"",t.envMap?"#define "+h:"",d?"#define CUBEUV_TEXEL_WIDTH "+d.texelWidth:"",d?"#define CUBEUV_TEXEL_HEIGHT "+d.texelHeight:"",d?"#define CUBEUV_MAX_MIP "+d.maxMip+".0":"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",t.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.anisotropy?"#define USE_ANISOTROPY":"",t.anisotropyMap?"#define USE_ANISOTROPYMAP":"",t.clearcoat?"#define USE_CLEARCOAT":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.dispersion?"#define USE_DISPERSION":"",t.iridescence?"#define USE_IRIDESCENCE":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",t.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaTest?"#define USE_ALPHATEST":"",t.alphaHash?"#define USE_ALPHAHASH":"",t.sheen?"#define USE_SHEEN":"",t.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.vertexTangents&&t.flatShading===!1?"#define USE_TANGENT":"",t.vertexColors||t.instancingColor||t.batchingColor?"#define USE_COLOR":"",t.vertexAlphas?"#define USE_COLOR_ALPHA":"",t.vertexUv1s?"#define USE_UV1":"",t.vertexUv2s?"#define USE_UV2":"",t.vertexUv3s?"#define USE_UV3":"",t.pointsUvs?"#define USE_POINTS_UV":"",t.gradientMap?"#define USE_GRADIENTMAP":"",t.flatShading?"#define FLAT_SHADED":"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+l:"",t.premultipliedAlpha?"#define PREMULTIPLIED_ALPHA":"",t.numLightProbes>0?"#define USE_LIGHT_PROBES":"",t.decodeVideoTexture?"#define DECODE_VIDEO_TEXTURE":"",t.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"","uniform mat4 viewMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;",t.toneMapping!==Ji?"#define TONE_MAPPING":"",t.toneMapping!==Ji?it.tonemapping_pars_fragment:"",t.toneMapping!==Ji?$v("toneMapping",t.toneMapping):"",t.dithering?"#define DITHERING":"",t.opaque?"#define OPAQUE":"",it.colorspace_pars_fragment,qv("linearToOutputTexel",t.outputColorSpace),jv(),t.useDepthPacking?"#define DEPTH_PACKING "+t.depthPacking:"",`
`].filter(ta).join(`
`)),a=vc(a),a=xh(a,t),a=Mh(a,t),o=vc(o),o=xh(o,t),o=Mh(o,t),a=Sh(a),o=Sh(o),t.isRawShaderMaterial!==!0&&(E=`#version 300 es
`,p=[m,"#define attribute in","#define varying out","#define texture2D texture"].join(`
`)+`
`+p,f=["#define varying in",t.glslVersion===Fu?"":"layout(location = 0) out highp vec4 pc_fragColor;",t.glslVersion===Fu?"":"#define gl_FragColor pc_fragColor","#define gl_FragDepthEXT gl_FragDepth","#define texture2D texture","#define textureCube texture","#define texture2DProj textureProj","#define texture2DLodEXT textureLod","#define texture2DProjLodEXT textureProjLod","#define textureCubeLodEXT textureLod","#define texture2DGradEXT textureGrad","#define texture2DProjGradEXT textureProjGrad","#define textureCubeGradEXT textureGrad"].join(`
`)+`
`+f);const y=E+p+a,T=E+f+o,z=_h(r,r.VERTEX_SHADER,y),C=_h(r,r.FRAGMENT_SHADER,T);r.attachShader(v,z),r.attachShader(v,C),t.index0AttributeName!==void 0?r.bindAttribLocation(v,0,t.index0AttributeName):t.morphTargets===!0&&r.bindAttribLocation(v,0,"position"),r.linkProgram(v);function D(R){if(i.debug.checkShaderErrors){const j=r.getProgramInfoLog(v).trim(),O=r.getShaderInfoLog(z).trim(),K=r.getShaderInfoLog(C).trim();let W=!0,J=!0;if(r.getProgramParameter(v,r.LINK_STATUS)===!1)if(W=!1,typeof i.debug.onShaderError=="function")i.debug.onShaderError(r,v,z,C);else{const Y=vh(r,z,"vertex"),ee=vh(r,C,"fragment");console.error("THREE.WebGLProgram: Shader Error "+r.getError()+" - VALIDATE_STATUS "+r.getProgramParameter(v,r.VALIDATE_STATUS)+`

Material Name: `+R.name+`
Material Type: `+R.type+`

Program Info Log: `+j+`
`+Y+`
`+ee)}else j!==""?console.warn("THREE.WebGLProgram: Program Info Log:",j):(O===""||K==="")&&(J=!1);J&&(R.diagnostics={runnable:W,programLog:j,vertexShader:{log:O,prefix:p},fragmentShader:{log:K,prefix:f}})}r.deleteShader(z),r.deleteShader(C),B=new lo(r,v),w=Jv(r,v)}let B;this.getUniforms=function(){return B===void 0&&D(this),B};let w;this.getAttributes=function(){return w===void 0&&D(this),w};let x=t.rendererExtensionParallelShaderCompile===!1;return this.isReady=function(){return x===!1&&(x=r.getProgramParameter(v,Gv)),x},this.destroy=function(){n.releaseStatesOfProgram(this),r.deleteProgram(v),this.program=void 0},this.type=t.shaderType,this.name=t.shaderName,this.id=Wv++,this.cacheKey=e,this.usedTimes=1,this.program=v,this.vertexShader=z,this.fragmentShader=C,this}let ux=0;class hx{constructor(){this.shaderCache=new Map,this.materialCache=new Map}update(e){const t=e.vertexShader,n=e.fragmentShader,r=this._getShaderStage(t),s=this._getShaderStage(n),a=this._getShaderCacheForMaterial(e);return a.has(r)===!1&&(a.add(r),r.usedTimes++),a.has(s)===!1&&(a.add(s),s.usedTimes++),this}remove(e){const t=this.materialCache.get(e);for(const n of t)n.usedTimes--,n.usedTimes===0&&this.shaderCache.delete(n.code);return this.materialCache.delete(e),this}getVertexShaderID(e){return this._getShaderStage(e.vertexShader).id}getFragmentShaderID(e){return this._getShaderStage(e.fragmentShader).id}dispose(){this.shaderCache.clear(),this.materialCache.clear()}_getShaderCacheForMaterial(e){const t=this.materialCache;let n=t.get(e);return n===void 0&&(n=new Set,t.set(e,n)),n}_getShaderStage(e){const t=this.shaderCache;let n=t.get(e);return n===void 0&&(n=new dx(e),t.set(e,n)),n}}class dx{constructor(e){this.id=ux++,this.code=e,this.usedTimes=0}}function fx(i,e,t,n,r,s,a){const o=new zc,l=new hx,c=new Set,u=[],h=r.logarithmicDepthBuffer,d=r.vertexTextures;let m=r.precision;const _={MeshDepthMaterial:"depth",MeshDistanceMaterial:"distanceRGBA",MeshNormalMaterial:"normal",MeshBasicMaterial:"basic",MeshLambertMaterial:"lambert",MeshPhongMaterial:"phong",MeshToonMaterial:"toon",MeshStandardMaterial:"physical",MeshPhysicalMaterial:"physical",MeshMatcapMaterial:"matcap",LineBasicMaterial:"basic",LineDashedMaterial:"dashed",PointsMaterial:"points",ShadowMaterial:"shadow",SpriteMaterial:"sprite"};function v(w){return c.add(w),w===0?"uv":`uv${w}`}function p(w,x,R,j,O){const K=j.fog,W=O.geometry,J=w.isMeshStandardMaterial?j.environment:null,Y=(w.isMeshStandardMaterial?t:e).get(w.envMap||J),ee=Y&&Y.mapping===Ao?Y.image.height:null,pe=_[w.type];w.precision!==null&&(m=r.getMaxPrecision(w.precision),m!==w.precision&&console.warn("THREE.WebGLProgram.getParameters:",w.precision,"not supported, using",m,"instead."));const ue=W.morphAttributes.position||W.morphAttributes.normal||W.morphAttributes.color,_e=ue!==void 0?ue.length:0;let be=0;W.morphAttributes.position!==void 0&&(be=1),W.morphAttributes.normal!==void 0&&(be=2),W.morphAttributes.color!==void 0&&(be=3);let ve,te,le,xe;if(pe){const at=pi[pe];ve=at.vertexShader,te=at.fragmentShader}else ve=w.vertexShader,te=w.fragmentShader,l.update(w),le=l.getVertexShaderID(w),xe=l.getFragmentShaderID(w);const he=i.getRenderTarget(),Be=O.isInstancedMesh===!0,Ve=O.isBatchedMesh===!0,Ne=!!w.map,dt=!!w.matcap,U=!!Y,ut=!!w.aoMap,tt=!!w.lightMap,ot=!!w.bumpMap,Fe=!!w.normalMap,yt=!!w.displacementMap,Ye=!!w.emissiveMap,We=!!w.metalnessMap,L=!!w.roughnessMap,S=w.anisotropy>0,Z=w.clearcoat>0,ae=w.dispersion>0,Q=w.iridescence>0,G=w.sheen>0,Ee=w.transmission>0,me=S&&!!w.anisotropyMap,we=Z&&!!w.clearcoatMap,je=Z&&!!w.clearcoatNormalMap,fe=Z&&!!w.clearcoatRoughnessMap,Te=Q&&!!w.iridescenceMap,Ke=Q&&!!w.iridescenceThicknessMap,ze=G&&!!w.sheenColorMap,Se=G&&!!w.sheenRoughnessMap,ke=!!w.specularMap,N=!!w.specularColorMap,oe=!!w.specularIntensityMap,I=Ee&&!!w.transmissionMap,re=Ee&&!!w.thicknessMap,ne=!!w.gradientMap,ie=!!w.alphaMap,ge=w.alphaTest>0,$e=!!w.alphaHash,st=!!w.extensions;let mt=Ji;w.toneMapped&&(he===null||he.isXRRenderTarget===!0)&&(mt=i.toneMapping);const Et={shaderID:pe,shaderType:w.type,shaderName:w.name,vertexShader:ve,fragmentShader:te,defines:w.defines,customVertexShaderID:le,customFragmentShaderID:xe,isRawShaderMaterial:w.isRawShaderMaterial===!0,glslVersion:w.glslVersion,precision:m,batching:Ve,batchingColor:Ve&&O._colorsTexture!==null,instancing:Be,instancingColor:Be&&O.instanceColor!==null,instancingMorph:Be&&O.morphTexture!==null,supportsVertexTextures:d,outputColorSpace:he===null?i.outputColorSpace:he.isXRRenderTarget===!0?he.texture.colorSpace:rr,alphaToCoverage:!!w.alphaToCoverage,map:Ne,matcap:dt,envMap:U,envMapMode:U&&Y.mapping,envMapCubeUVHeight:ee,aoMap:ut,lightMap:tt,bumpMap:ot,normalMap:Fe,displacementMap:d&&yt,emissiveMap:Ye,normalMapObjectSpace:Fe&&w.normalMapType===om,normalMapTangentSpace:Fe&&w.normalMapType===Gd,metalnessMap:We,roughnessMap:L,anisotropy:S,anisotropyMap:me,clearcoat:Z,clearcoatMap:we,clearcoatNormalMap:je,clearcoatRoughnessMap:fe,dispersion:ae,iridescence:Q,iridescenceMap:Te,iridescenceThicknessMap:Ke,sheen:G,sheenColorMap:ze,sheenRoughnessMap:Se,specularMap:ke,specularColorMap:N,specularIntensityMap:oe,transmission:Ee,transmissionMap:I,thicknessMap:re,gradientMap:ne,opaque:w.transparent===!1&&w.blending===gs&&w.alphaToCoverage===!1,alphaMap:ie,alphaTest:ge,alphaHash:$e,combine:w.combine,mapUv:Ne&&v(w.map.channel),aoMapUv:ut&&v(w.aoMap.channel),lightMapUv:tt&&v(w.lightMap.channel),bumpMapUv:ot&&v(w.bumpMap.channel),normalMapUv:Fe&&v(w.normalMap.channel),displacementMapUv:yt&&v(w.displacementMap.channel),emissiveMapUv:Ye&&v(w.emissiveMap.channel),metalnessMapUv:We&&v(w.metalnessMap.channel),roughnessMapUv:L&&v(w.roughnessMap.channel),anisotropyMapUv:me&&v(w.anisotropyMap.channel),clearcoatMapUv:we&&v(w.clearcoatMap.channel),clearcoatNormalMapUv:je&&v(w.clearcoatNormalMap.channel),clearcoatRoughnessMapUv:fe&&v(w.clearcoatRoughnessMap.channel),iridescenceMapUv:Te&&v(w.iridescenceMap.channel),iridescenceThicknessMapUv:Ke&&v(w.iridescenceThicknessMap.channel),sheenColorMapUv:ze&&v(w.sheenColorMap.channel),sheenRoughnessMapUv:Se&&v(w.sheenRoughnessMap.channel),specularMapUv:ke&&v(w.specularMap.channel),specularColorMapUv:N&&v(w.specularColorMap.channel),specularIntensityMapUv:oe&&v(w.specularIntensityMap.channel),transmissionMapUv:I&&v(w.transmissionMap.channel),thicknessMapUv:re&&v(w.thicknessMap.channel),alphaMapUv:ie&&v(w.alphaMap.channel),vertexTangents:!!W.attributes.tangent&&(Fe||S),vertexColors:w.vertexColors,vertexAlphas:w.vertexColors===!0&&!!W.attributes.color&&W.attributes.color.itemSize===4,pointsUvs:O.isPoints===!0&&!!W.attributes.uv&&(Ne||ie),fog:!!K,useFog:w.fog===!0,fogExp2:!!K&&K.isFogExp2,flatShading:w.flatShading===!0,sizeAttenuation:w.sizeAttenuation===!0,logarithmicDepthBuffer:h,skinning:O.isSkinnedMesh===!0,morphTargets:W.morphAttributes.position!==void 0,morphNormals:W.morphAttributes.normal!==void 0,morphColors:W.morphAttributes.color!==void 0,morphTargetsCount:_e,morphTextureStride:be,numDirLights:x.directional.length,numPointLights:x.point.length,numSpotLights:x.spot.length,numSpotLightMaps:x.spotLightMap.length,numRectAreaLights:x.rectArea.length,numHemiLights:x.hemi.length,numDirLightShadows:x.directionalShadowMap.length,numPointLightShadows:x.pointShadowMap.length,numSpotLightShadows:x.spotShadowMap.length,numSpotLightShadowsWithMaps:x.numSpotLightShadowsWithMaps,numLightProbes:x.numLightProbes,numClippingPlanes:a.numPlanes,numClipIntersection:a.numIntersection,dithering:w.dithering,shadowMapEnabled:i.shadowMap.enabled&&R.length>0,shadowMapType:i.shadowMap.type,toneMapping:mt,decodeVideoTexture:Ne&&w.map.isVideoTexture===!0&&St.getTransfer(w.map.colorSpace)===Nt,premultipliedAlpha:w.premultipliedAlpha,doubleSided:w.side===mi,flipSided:w.side===Cn,useDepthPacking:w.depthPacking>=0,depthPacking:w.depthPacking||0,index0AttributeName:w.index0AttributeName,extensionClipCullDistance:st&&w.extensions.clipCullDistance===!0&&n.has("WEBGL_clip_cull_distance"),extensionMultiDraw:(st&&w.extensions.multiDraw===!0||Ve)&&n.has("WEBGL_multi_draw"),rendererExtensionParallelShaderCompile:n.has("KHR_parallel_shader_compile"),customProgramCacheKey:w.customProgramCacheKey()};return Et.vertexUv1s=c.has(1),Et.vertexUv2s=c.has(2),Et.vertexUv3s=c.has(3),c.clear(),Et}function f(w){const x=[];if(w.shaderID?x.push(w.shaderID):(x.push(w.customVertexShaderID),x.push(w.customFragmentShaderID)),w.defines!==void 0)for(const R in w.defines)x.push(R),x.push(w.defines[R]);return w.isRawShaderMaterial===!1&&(E(x,w),y(x,w),x.push(i.outputColorSpace)),x.push(w.customProgramCacheKey),x.join()}function E(w,x){w.push(x.precision),w.push(x.outputColorSpace),w.push(x.envMapMode),w.push(x.envMapCubeUVHeight),w.push(x.mapUv),w.push(x.alphaMapUv),w.push(x.lightMapUv),w.push(x.aoMapUv),w.push(x.bumpMapUv),w.push(x.normalMapUv),w.push(x.displacementMapUv),w.push(x.emissiveMapUv),w.push(x.metalnessMapUv),w.push(x.roughnessMapUv),w.push(x.anisotropyMapUv),w.push(x.clearcoatMapUv),w.push(x.clearcoatNormalMapUv),w.push(x.clearcoatRoughnessMapUv),w.push(x.iridescenceMapUv),w.push(x.iridescenceThicknessMapUv),w.push(x.sheenColorMapUv),w.push(x.sheenRoughnessMapUv),w.push(x.specularMapUv),w.push(x.specularColorMapUv),w.push(x.specularIntensityMapUv),w.push(x.transmissionMapUv),w.push(x.thicknessMapUv),w.push(x.combine),w.push(x.fogExp2),w.push(x.sizeAttenuation),w.push(x.morphTargetsCount),w.push(x.morphAttributeCount),w.push(x.numDirLights),w.push(x.numPointLights),w.push(x.numSpotLights),w.push(x.numSpotLightMaps),w.push(x.numHemiLights),w.push(x.numRectAreaLights),w.push(x.numDirLightShadows),w.push(x.numPointLightShadows),w.push(x.numSpotLightShadows),w.push(x.numSpotLightShadowsWithMaps),w.push(x.numLightProbes),w.push(x.shadowMapType),w.push(x.toneMapping),w.push(x.numClippingPlanes),w.push(x.numClipIntersection),w.push(x.depthPacking)}function y(w,x){o.disableAll(),x.supportsVertexTextures&&o.enable(0),x.instancing&&o.enable(1),x.instancingColor&&o.enable(2),x.instancingMorph&&o.enable(3),x.matcap&&o.enable(4),x.envMap&&o.enable(5),x.normalMapObjectSpace&&o.enable(6),x.normalMapTangentSpace&&o.enable(7),x.clearcoat&&o.enable(8),x.iridescence&&o.enable(9),x.alphaTest&&o.enable(10),x.vertexColors&&o.enable(11),x.vertexAlphas&&o.enable(12),x.vertexUv1s&&o.enable(13),x.vertexUv2s&&o.enable(14),x.vertexUv3s&&o.enable(15),x.vertexTangents&&o.enable(16),x.anisotropy&&o.enable(17),x.alphaHash&&o.enable(18),x.batching&&o.enable(19),x.dispersion&&o.enable(20),x.batchingColor&&o.enable(21),w.push(o.mask),o.disableAll(),x.fog&&o.enable(0),x.useFog&&o.enable(1),x.flatShading&&o.enable(2),x.logarithmicDepthBuffer&&o.enable(3),x.skinning&&o.enable(4),x.morphTargets&&o.enable(5),x.morphNormals&&o.enable(6),x.morphColors&&o.enable(7),x.premultipliedAlpha&&o.enable(8),x.shadowMapEnabled&&o.enable(9),x.doubleSided&&o.enable(10),x.flipSided&&o.enable(11),x.useDepthPacking&&o.enable(12),x.dithering&&o.enable(13),x.transmission&&o.enable(14),x.sheen&&o.enable(15),x.opaque&&o.enable(16),x.pointsUvs&&o.enable(17),x.decodeVideoTexture&&o.enable(18),x.alphaToCoverage&&o.enable(19),w.push(o.mask)}function T(w){const x=_[w.type];let R;if(x){const j=pi[x];R=Km.clone(j.uniforms)}else R=w.uniforms;return R}function z(w,x){let R;for(let j=0,O=u.length;j<O;j++){const K=u[j];if(K.cacheKey===x){R=K,++R.usedTimes;break}}return R===void 0&&(R=new cx(i,x,w,s),u.push(R)),R}function C(w){if(--w.usedTimes===0){const x=u.indexOf(w);u[x]=u[u.length-1],u.pop(),w.destroy()}}function D(w){l.remove(w)}function B(){l.dispose()}return{getParameters:p,getProgramCacheKey:f,getUniforms:T,acquireProgram:z,releaseProgram:C,releaseShaderCache:D,programs:u,dispose:B}}function px(){let i=new WeakMap;function e(a){return i.has(a)}function t(a){let o=i.get(a);return o===void 0&&(o={},i.set(a,o)),o}function n(a){i.delete(a)}function r(a,o,l){i.get(a)[o]=l}function s(){i=new WeakMap}return{has:e,get:t,remove:n,update:r,dispose:s}}function mx(i,e){return i.groupOrder!==e.groupOrder?i.groupOrder-e.groupOrder:i.renderOrder!==e.renderOrder?i.renderOrder-e.renderOrder:i.material.id!==e.material.id?i.material.id-e.material.id:i.z!==e.z?i.z-e.z:i.id-e.id}function Eh(i,e){return i.groupOrder!==e.groupOrder?i.groupOrder-e.groupOrder:i.renderOrder!==e.renderOrder?i.renderOrder-e.renderOrder:i.z!==e.z?e.z-i.z:i.id-e.id}function bh(){const i=[];let e=0;const t=[],n=[],r=[];function s(){e=0,t.length=0,n.length=0,r.length=0}function a(h,d,m,_,v,p){let f=i[e];return f===void 0?(f={id:h.id,object:h,geometry:d,material:m,groupOrder:_,renderOrder:h.renderOrder,z:v,group:p},i[e]=f):(f.id=h.id,f.object=h,f.geometry=d,f.material=m,f.groupOrder=_,f.renderOrder=h.renderOrder,f.z=v,f.group=p),e++,f}function o(h,d,m,_,v,p){const f=a(h,d,m,_,v,p);m.transmission>0?n.push(f):m.transparent===!0?r.push(f):t.push(f)}function l(h,d,m,_,v,p){const f=a(h,d,m,_,v,p);m.transmission>0?n.unshift(f):m.transparent===!0?r.unshift(f):t.unshift(f)}function c(h,d){t.length>1&&t.sort(h||mx),n.length>1&&n.sort(d||Eh),r.length>1&&r.sort(d||Eh)}function u(){for(let h=e,d=i.length;h<d;h++){const m=i[h];if(m.id===null)break;m.id=null,m.object=null,m.geometry=null,m.material=null,m.group=null}}return{opaque:t,transmissive:n,transparent:r,init:s,push:o,unshift:l,finish:u,sort:c}}function gx(){let i=new WeakMap;function e(n,r){const s=i.get(n);let a;return s===void 0?(a=new bh,i.set(n,[a])):r>=s.length?(a=new bh,s.push(a)):a=s[r],a}function t(){i=new WeakMap}return{get:e,dispose:t}}function _x(){const i={};return{get:function(e){if(i[e.id]!==void 0)return i[e.id];let t;switch(e.type){case"DirectionalLight":t={direction:new V,color:new nt};break;case"SpotLight":t={position:new V,direction:new V,color:new nt,distance:0,coneCos:0,penumbraCos:0,decay:0};break;case"PointLight":t={position:new V,color:new nt,distance:0,decay:0};break;case"HemisphereLight":t={direction:new V,skyColor:new nt,groundColor:new nt};break;case"RectAreaLight":t={color:new nt,position:new V,halfWidth:new V,halfHeight:new V};break}return i[e.id]=t,t}}}function vx(){const i={};return{get:function(e){if(i[e.id]!==void 0)return i[e.id];let t;switch(e.type){case"DirectionalLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new Xe};break;case"SpotLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new Xe};break;case"PointLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new Xe,shadowCameraNear:1,shadowCameraFar:1e3};break}return i[e.id]=t,t}}}let xx=0;function Mx(i,e){return(e.castShadow?2:0)-(i.castShadow?2:0)+(e.map?1:0)-(i.map?1:0)}function Sx(i){const e=new _x,t=vx(),n={version:0,hash:{directionalLength:-1,pointLength:-1,spotLength:-1,rectAreaLength:-1,hemiLength:-1,numDirectionalShadows:-1,numPointShadows:-1,numSpotShadows:-1,numSpotMaps:-1,numLightProbes:-1},ambient:[0,0,0],probe:[],directional:[],directionalShadow:[],directionalShadowMap:[],directionalShadowMatrix:[],spot:[],spotLightMap:[],spotShadow:[],spotShadowMap:[],spotLightMatrix:[],rectArea:[],rectAreaLTC1:null,rectAreaLTC2:null,point:[],pointShadow:[],pointShadowMap:[],pointShadowMatrix:[],hemi:[],numSpotLightShadowsWithMaps:0,numLightProbes:0};for(let c=0;c<9;c++)n.probe.push(new V);const r=new V,s=new zt,a=new zt;function o(c){let u=0,h=0,d=0;for(let w=0;w<9;w++)n.probe[w].set(0,0,0);let m=0,_=0,v=0,p=0,f=0,E=0,y=0,T=0,z=0,C=0,D=0;c.sort(Mx);for(let w=0,x=c.length;w<x;w++){const R=c[w],j=R.color,O=R.intensity,K=R.distance,W=R.shadow&&R.shadow.map?R.shadow.map.texture:null;if(R.isAmbientLight)u+=j.r*O,h+=j.g*O,d+=j.b*O;else if(R.isLightProbe){for(let J=0;J<9;J++)n.probe[J].addScaledVector(R.sh.coefficients[J],O);D++}else if(R.isDirectionalLight){const J=e.get(R);if(J.color.copy(R.color).multiplyScalar(R.intensity),R.castShadow){const Y=R.shadow,ee=t.get(R);ee.shadowIntensity=Y.intensity,ee.shadowBias=Y.bias,ee.shadowNormalBias=Y.normalBias,ee.shadowRadius=Y.radius,ee.shadowMapSize=Y.mapSize,n.directionalShadow[m]=ee,n.directionalShadowMap[m]=W,n.directionalShadowMatrix[m]=R.shadow.matrix,E++}n.directional[m]=J,m++}else if(R.isSpotLight){const J=e.get(R);J.position.setFromMatrixPosition(R.matrixWorld),J.color.copy(j).multiplyScalar(O),J.distance=K,J.coneCos=Math.cos(R.angle),J.penumbraCos=Math.cos(R.angle*(1-R.penumbra)),J.decay=R.decay,n.spot[v]=J;const Y=R.shadow;if(R.map&&(n.spotLightMap[z]=R.map,z++,Y.updateMatrices(R),R.castShadow&&C++),n.spotLightMatrix[v]=Y.matrix,R.castShadow){const ee=t.get(R);ee.shadowIntensity=Y.intensity,ee.shadowBias=Y.bias,ee.shadowNormalBias=Y.normalBias,ee.shadowRadius=Y.radius,ee.shadowMapSize=Y.mapSize,n.spotShadow[v]=ee,n.spotShadowMap[v]=W,T++}v++}else if(R.isRectAreaLight){const J=e.get(R);J.color.copy(j).multiplyScalar(O),J.halfWidth.set(R.width*.5,0,0),J.halfHeight.set(0,R.height*.5,0),n.rectArea[p]=J,p++}else if(R.isPointLight){const J=e.get(R);if(J.color.copy(R.color).multiplyScalar(R.intensity),J.distance=R.distance,J.decay=R.decay,R.castShadow){const Y=R.shadow,ee=t.get(R);ee.shadowIntensity=Y.intensity,ee.shadowBias=Y.bias,ee.shadowNormalBias=Y.normalBias,ee.shadowRadius=Y.radius,ee.shadowMapSize=Y.mapSize,ee.shadowCameraNear=Y.camera.near,ee.shadowCameraFar=Y.camera.far,n.pointShadow[_]=ee,n.pointShadowMap[_]=W,n.pointShadowMatrix[_]=R.shadow.matrix,y++}n.point[_]=J,_++}else if(R.isHemisphereLight){const J=e.get(R);J.skyColor.copy(R.color).multiplyScalar(O),J.groundColor.copy(R.groundColor).multiplyScalar(O),n.hemi[f]=J,f++}}p>0&&(i.has("OES_texture_float_linear")===!0?(n.rectAreaLTC1=Ae.LTC_FLOAT_1,n.rectAreaLTC2=Ae.LTC_FLOAT_2):(n.rectAreaLTC1=Ae.LTC_HALF_1,n.rectAreaLTC2=Ae.LTC_HALF_2)),n.ambient[0]=u,n.ambient[1]=h,n.ambient[2]=d;const B=n.hash;(B.directionalLength!==m||B.pointLength!==_||B.spotLength!==v||B.rectAreaLength!==p||B.hemiLength!==f||B.numDirectionalShadows!==E||B.numPointShadows!==y||B.numSpotShadows!==T||B.numSpotMaps!==z||B.numLightProbes!==D)&&(n.directional.length=m,n.spot.length=v,n.rectArea.length=p,n.point.length=_,n.hemi.length=f,n.directionalShadow.length=E,n.directionalShadowMap.length=E,n.pointShadow.length=y,n.pointShadowMap.length=y,n.spotShadow.length=T,n.spotShadowMap.length=T,n.directionalShadowMatrix.length=E,n.pointShadowMatrix.length=y,n.spotLightMatrix.length=T+z-C,n.spotLightMap.length=z,n.numSpotLightShadowsWithMaps=C,n.numLightProbes=D,B.directionalLength=m,B.pointLength=_,B.spotLength=v,B.rectAreaLength=p,B.hemiLength=f,B.numDirectionalShadows=E,B.numPointShadows=y,B.numSpotShadows=T,B.numSpotMaps=z,B.numLightProbes=D,n.version=xx++)}function l(c,u){let h=0,d=0,m=0,_=0,v=0;const p=u.matrixWorldInverse;for(let f=0,E=c.length;f<E;f++){const y=c[f];if(y.isDirectionalLight){const T=n.directional[h];T.direction.setFromMatrixPosition(y.matrixWorld),r.setFromMatrixPosition(y.target.matrixWorld),T.direction.sub(r),T.direction.transformDirection(p),h++}else if(y.isSpotLight){const T=n.spot[m];T.position.setFromMatrixPosition(y.matrixWorld),T.position.applyMatrix4(p),T.direction.setFromMatrixPosition(y.matrixWorld),r.setFromMatrixPosition(y.target.matrixWorld),T.direction.sub(r),T.direction.transformDirection(p),m++}else if(y.isRectAreaLight){const T=n.rectArea[_];T.position.setFromMatrixPosition(y.matrixWorld),T.position.applyMatrix4(p),a.identity(),s.copy(y.matrixWorld),s.premultiply(p),a.extractRotation(s),T.halfWidth.set(y.width*.5,0,0),T.halfHeight.set(0,y.height*.5,0),T.halfWidth.applyMatrix4(a),T.halfHeight.applyMatrix4(a),_++}else if(y.isPointLight){const T=n.point[d];T.position.setFromMatrixPosition(y.matrixWorld),T.position.applyMatrix4(p),d++}else if(y.isHemisphereLight){const T=n.hemi[v];T.direction.setFromMatrixPosition(y.matrixWorld),T.direction.transformDirection(p),v++}}}return{setup:o,setupView:l,state:n}}function Th(i){const e=new Sx(i),t=[],n=[];function r(u){c.camera=u,t.length=0,n.length=0}function s(u){t.push(u)}function a(u){n.push(u)}function o(){e.setup(t)}function l(u){e.setupView(t,u)}const c={lightsArray:t,shadowsArray:n,camera:null,lights:e,transmissionRenderTarget:{}};return{init:r,state:c,setupLights:o,setupLightsView:l,pushLight:s,pushShadow:a}}function yx(i){let e=new WeakMap;function t(r,s=0){const a=e.get(r);let o;return a===void 0?(o=new Th(i),e.set(r,[o])):s>=a.length?(o=new Th(i),a.push(o)):o=a[s],o}function n(){e=new WeakMap}return{get:t,dispose:n}}class Ex extends Dr{constructor(e){super(),this.isMeshDepthMaterial=!0,this.type="MeshDepthMaterial",this.depthPacking=sm,this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.wireframe=!1,this.wireframeLinewidth=1,this.setValues(e)}copy(e){return super.copy(e),this.depthPacking=e.depthPacking,this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this}}class bx extends Dr{constructor(e){super(),this.isMeshDistanceMaterial=!0,this.type="MeshDistanceMaterial",this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.setValues(e)}copy(e){return super.copy(e),this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this}}const Tx=`void main() {
	gl_Position = vec4( position, 1.0 );
}`,wx=`uniform sampler2D shadow_pass;
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
}`;function Ax(i,e,t){let n=new Hc;const r=new Xe,s=new Xe,a=new jt,o=new Ex({depthPacking:am}),l=new bx,c={},u=t.maxTextureSize,h={[er]:Cn,[Cn]:er,[mi]:mi},d=new tr({defines:{VSM_SAMPLES:8},uniforms:{shadow_pass:{value:null},resolution:{value:new Xe},radius:{value:4}},vertexShader:Tx,fragmentShader:wx}),m=d.clone();m.defines.HORIZONTAL_PASS=1;const _=new gn;_.setAttribute("position",new Xn(new Float32Array([-1,-1,.5,3,-1,.5,-1,3,.5]),3));const v=new Rn(_,d),p=this;this.enabled=!1,this.autoUpdate=!0,this.needsUpdate=!1,this.type=Rd;let f=this.type;this.render=function(C,D,B){if(p.enabled===!1||p.autoUpdate===!1&&p.needsUpdate===!1||C.length===0)return;const w=i.getRenderTarget(),x=i.getActiveCubeFace(),R=i.getActiveMipmapLevel(),j=i.state;j.setBlending(Zi),j.buffers.color.setClear(1,1,1,1),j.buffers.depth.setTest(!0),j.setScissorTest(!1);const O=f!==Ai&&this.type===Ai,K=f===Ai&&this.type!==Ai;for(let W=0,J=C.length;W<J;W++){const Y=C[W],ee=Y.shadow;if(ee===void 0){console.warn("THREE.WebGLShadowMap:",Y,"has no shadow.");continue}if(ee.autoUpdate===!1&&ee.needsUpdate===!1)continue;r.copy(ee.mapSize);const pe=ee.getFrameExtents();if(r.multiply(pe),s.copy(ee.mapSize),(r.x>u||r.y>u)&&(r.x>u&&(s.x=Math.floor(u/pe.x),r.x=s.x*pe.x,ee.mapSize.x=s.x),r.y>u&&(s.y=Math.floor(u/pe.y),r.y=s.y*pe.y,ee.mapSize.y=s.y)),ee.map===null||O===!0||K===!0){const _e=this.type!==Ai?{minFilter:Wn,magFilter:Wn}:{};ee.map!==null&&ee.map.dispose(),ee.map=new Ar(r.x,r.y,_e),ee.map.texture.name=Y.name+".shadowMap",ee.camera.updateProjectionMatrix()}i.setRenderTarget(ee.map),i.clear();const ue=ee.getViewportCount();for(let _e=0;_e<ue;_e++){const be=ee.getViewport(_e);a.set(s.x*be.x,s.y*be.y,s.x*be.z,s.y*be.w),j.viewport(a),ee.updateMatrices(Y,_e),n=ee.getFrustum(),T(D,B,ee.camera,Y,this.type)}ee.isPointLightShadow!==!0&&this.type===Ai&&E(ee,B),ee.needsUpdate=!1}f=this.type,p.needsUpdate=!1,i.setRenderTarget(w,x,R)};function E(C,D){const B=e.update(v);d.defines.VSM_SAMPLES!==C.blurSamples&&(d.defines.VSM_SAMPLES=C.blurSamples,m.defines.VSM_SAMPLES=C.blurSamples,d.needsUpdate=!0,m.needsUpdate=!0),C.mapPass===null&&(C.mapPass=new Ar(r.x,r.y)),d.uniforms.shadow_pass.value=C.map.texture,d.uniforms.resolution.value=C.mapSize,d.uniforms.radius.value=C.radius,i.setRenderTarget(C.mapPass),i.clear(),i.renderBufferDirect(D,null,B,d,v,null),m.uniforms.shadow_pass.value=C.mapPass.texture,m.uniforms.resolution.value=C.mapSize,m.uniforms.radius.value=C.radius,i.setRenderTarget(C.map),i.clear(),i.renderBufferDirect(D,null,B,m,v,null)}function y(C,D,B,w){let x=null;const R=B.isPointLight===!0?C.customDistanceMaterial:C.customDepthMaterial;if(R!==void 0)x=R;else if(x=B.isPointLight===!0?l:o,i.localClippingEnabled&&D.clipShadows===!0&&Array.isArray(D.clippingPlanes)&&D.clippingPlanes.length!==0||D.displacementMap&&D.displacementScale!==0||D.alphaMap&&D.alphaTest>0||D.map&&D.alphaTest>0){const j=x.uuid,O=D.uuid;let K=c[j];K===void 0&&(K={},c[j]=K);let W=K[O];W===void 0&&(W=x.clone(),K[O]=W,D.addEventListener("dispose",z)),x=W}if(x.visible=D.visible,x.wireframe=D.wireframe,w===Ai?x.side=D.shadowSide!==null?D.shadowSide:D.side:x.side=D.shadowSide!==null?D.shadowSide:h[D.side],x.alphaMap=D.alphaMap,x.alphaTest=D.alphaTest,x.map=D.map,x.clipShadows=D.clipShadows,x.clippingPlanes=D.clippingPlanes,x.clipIntersection=D.clipIntersection,x.displacementMap=D.displacementMap,x.displacementScale=D.displacementScale,x.displacementBias=D.displacementBias,x.wireframeLinewidth=D.wireframeLinewidth,x.linewidth=D.linewidth,B.isPointLight===!0&&x.isMeshDistanceMaterial===!0){const j=i.properties.get(x);j.light=B}return x}function T(C,D,B,w,x){if(C.visible===!1)return;if(C.layers.test(D.layers)&&(C.isMesh||C.isLine||C.isPoints)&&(C.castShadow||C.receiveShadow&&x===Ai)&&(!C.frustumCulled||n.intersectsObject(C))){C.modelViewMatrix.multiplyMatrices(B.matrixWorldInverse,C.matrixWorld);const O=e.update(C),K=C.material;if(Array.isArray(K)){const W=O.groups;for(let J=0,Y=W.length;J<Y;J++){const ee=W[J],pe=K[ee.materialIndex];if(pe&&pe.visible){const ue=y(C,pe,w,x);C.onBeforeShadow(i,C,D,B,O,ue,ee),i.renderBufferDirect(B,null,O,ue,C,ee),C.onAfterShadow(i,C,D,B,O,ue,ee)}}}else if(K.visible){const W=y(C,K,w,x);C.onBeforeShadow(i,C,D,B,O,W,null),i.renderBufferDirect(B,null,O,W,C,null),C.onAfterShadow(i,C,D,B,O,W,null)}}const j=C.children;for(let O=0,K=j.length;O<K;O++)T(j[O],D,B,w,x)}function z(C){C.target.removeEventListener("dispose",z);for(const B in c){const w=c[B],x=C.target.uuid;x in w&&(w[x].dispose(),delete w[x])}}}function Rx(i){function e(){let I=!1;const re=new jt;let ne=null;const ie=new jt(0,0,0,0);return{setMask:function(ge){ne!==ge&&!I&&(i.colorMask(ge,ge,ge,ge),ne=ge)},setLocked:function(ge){I=ge},setClear:function(ge,$e,st,mt,Et){Et===!0&&(ge*=mt,$e*=mt,st*=mt),re.set(ge,$e,st,mt),ie.equals(re)===!1&&(i.clearColor(ge,$e,st,mt),ie.copy(re))},reset:function(){I=!1,ne=null,ie.set(-1,0,0,0)}}}function t(){let I=!1,re=null,ne=null,ie=null;return{setTest:function(ge){ge?xe(i.DEPTH_TEST):he(i.DEPTH_TEST)},setMask:function(ge){re!==ge&&!I&&(i.depthMask(ge),re=ge)},setFunc:function(ge){if(ne!==ge){switch(ge){case Gp:i.depthFunc(i.NEVER);break;case Wp:i.depthFunc(i.ALWAYS);break;case Xp:i.depthFunc(i.LESS);break;case ho:i.depthFunc(i.LEQUAL);break;case Yp:i.depthFunc(i.EQUAL);break;case qp:i.depthFunc(i.GEQUAL);break;case $p:i.depthFunc(i.GREATER);break;case jp:i.depthFunc(i.NOTEQUAL);break;default:i.depthFunc(i.LEQUAL)}ne=ge}},setLocked:function(ge){I=ge},setClear:function(ge){ie!==ge&&(i.clearDepth(ge),ie=ge)},reset:function(){I=!1,re=null,ne=null,ie=null}}}function n(){let I=!1,re=null,ne=null,ie=null,ge=null,$e=null,st=null,mt=null,Et=null;return{setTest:function(at){I||(at?xe(i.STENCIL_TEST):he(i.STENCIL_TEST))},setMask:function(at){re!==at&&!I&&(i.stencilMask(at),re=at)},setFunc:function(at,ln,Ft){(ne!==at||ie!==ln||ge!==Ft)&&(i.stencilFunc(at,ln,Ft),ne=at,ie=ln,ge=Ft)},setOp:function(at,ln,Ft){($e!==at||st!==ln||mt!==Ft)&&(i.stencilOp(at,ln,Ft),$e=at,st=ln,mt=Ft)},setLocked:function(at){I=at},setClear:function(at){Et!==at&&(i.clearStencil(at),Et=at)},reset:function(){I=!1,re=null,ne=null,ie=null,ge=null,$e=null,st=null,mt=null,Et=null}}}const r=new e,s=new t,a=new n,o=new WeakMap,l=new WeakMap;let c={},u={},h=new WeakMap,d=[],m=null,_=!1,v=null,p=null,f=null,E=null,y=null,T=null,z=null,C=new nt(0,0,0),D=0,B=!1,w=null,x=null,R=null,j=null,O=null;const K=i.getParameter(i.MAX_COMBINED_TEXTURE_IMAGE_UNITS);let W=!1,J=0;const Y=i.getParameter(i.VERSION);Y.indexOf("WebGL")!==-1?(J=parseFloat(/^WebGL (\d)/.exec(Y)[1]),W=J>=1):Y.indexOf("OpenGL ES")!==-1&&(J=parseFloat(/^OpenGL ES (\d)/.exec(Y)[1]),W=J>=2);let ee=null,pe={};const ue=i.getParameter(i.SCISSOR_BOX),_e=i.getParameter(i.VIEWPORT),be=new jt().fromArray(ue),ve=new jt().fromArray(_e);function te(I,re,ne,ie){const ge=new Uint8Array(4),$e=i.createTexture();i.bindTexture(I,$e),i.texParameteri(I,i.TEXTURE_MIN_FILTER,i.NEAREST),i.texParameteri(I,i.TEXTURE_MAG_FILTER,i.NEAREST);for(let st=0;st<ne;st++)I===i.TEXTURE_3D||I===i.TEXTURE_2D_ARRAY?i.texImage3D(re,0,i.RGBA,1,1,ie,0,i.RGBA,i.UNSIGNED_BYTE,ge):i.texImage2D(re+st,0,i.RGBA,1,1,0,i.RGBA,i.UNSIGNED_BYTE,ge);return $e}const le={};le[i.TEXTURE_2D]=te(i.TEXTURE_2D,i.TEXTURE_2D,1),le[i.TEXTURE_CUBE_MAP]=te(i.TEXTURE_CUBE_MAP,i.TEXTURE_CUBE_MAP_POSITIVE_X,6),le[i.TEXTURE_2D_ARRAY]=te(i.TEXTURE_2D_ARRAY,i.TEXTURE_2D_ARRAY,1,1),le[i.TEXTURE_3D]=te(i.TEXTURE_3D,i.TEXTURE_3D,1,1),r.setClear(0,0,0,1),s.setClear(1),a.setClear(0),xe(i.DEPTH_TEST),s.setFunc(ho),ot(!1),Fe(Lu),xe(i.CULL_FACE),ut(Zi);function xe(I){c[I]!==!0&&(i.enable(I),c[I]=!0)}function he(I){c[I]!==!1&&(i.disable(I),c[I]=!1)}function Be(I,re){return u[I]!==re?(i.bindFramebuffer(I,re),u[I]=re,I===i.DRAW_FRAMEBUFFER&&(u[i.FRAMEBUFFER]=re),I===i.FRAMEBUFFER&&(u[i.DRAW_FRAMEBUFFER]=re),!0):!1}function Ve(I,re){let ne=d,ie=!1;if(I){ne=h.get(re),ne===void 0&&(ne=[],h.set(re,ne));const ge=I.textures;if(ne.length!==ge.length||ne[0]!==i.COLOR_ATTACHMENT0){for(let $e=0,st=ge.length;$e<st;$e++)ne[$e]=i.COLOR_ATTACHMENT0+$e;ne.length=ge.length,ie=!0}}else ne[0]!==i.BACK&&(ne[0]=i.BACK,ie=!0);ie&&i.drawBuffers(ne)}function Ne(I){return m!==I?(i.useProgram(I),m=I,!0):!1}const dt={[xr]:i.FUNC_ADD,[wp]:i.FUNC_SUBTRACT,[Ap]:i.FUNC_REVERSE_SUBTRACT};dt[Rp]=i.MIN,dt[Cp]=i.MAX;const U={[Pp]:i.ZERO,[Lp]:i.ONE,[Dp]:i.SRC_COLOR,[zl]:i.SRC_ALPHA,[Bp]:i.SRC_ALPHA_SATURATE,[Fp]:i.DST_COLOR,[Up]:i.DST_ALPHA,[Ip]:i.ONE_MINUS_SRC_COLOR,[kl]:i.ONE_MINUS_SRC_ALPHA,[Op]:i.ONE_MINUS_DST_COLOR,[Np]:i.ONE_MINUS_DST_ALPHA,[zp]:i.CONSTANT_COLOR,[kp]:i.ONE_MINUS_CONSTANT_COLOR,[Hp]:i.CONSTANT_ALPHA,[Vp]:i.ONE_MINUS_CONSTANT_ALPHA};function ut(I,re,ne,ie,ge,$e,st,mt,Et,at){if(I===Zi){_===!0&&(he(i.BLEND),_=!1);return}if(_===!1&&(xe(i.BLEND),_=!0),I!==Tp){if(I!==v||at!==B){if((p!==xr||y!==xr)&&(i.blendEquation(i.FUNC_ADD),p=xr,y=xr),at)switch(I){case gs:i.blendFuncSeparate(i.ONE,i.ONE_MINUS_SRC_ALPHA,i.ONE,i.ONE_MINUS_SRC_ALPHA);break;case Du:i.blendFunc(i.ONE,i.ONE);break;case Iu:i.blendFuncSeparate(i.ZERO,i.ONE_MINUS_SRC_COLOR,i.ZERO,i.ONE);break;case Uu:i.blendFuncSeparate(i.ZERO,i.SRC_COLOR,i.ZERO,i.SRC_ALPHA);break;default:console.error("THREE.WebGLState: Invalid blending: ",I);break}else switch(I){case gs:i.blendFuncSeparate(i.SRC_ALPHA,i.ONE_MINUS_SRC_ALPHA,i.ONE,i.ONE_MINUS_SRC_ALPHA);break;case Du:i.blendFunc(i.SRC_ALPHA,i.ONE);break;case Iu:i.blendFuncSeparate(i.ZERO,i.ONE_MINUS_SRC_COLOR,i.ZERO,i.ONE);break;case Uu:i.blendFunc(i.ZERO,i.SRC_COLOR);break;default:console.error("THREE.WebGLState: Invalid blending: ",I);break}f=null,E=null,T=null,z=null,C.set(0,0,0),D=0,v=I,B=at}return}ge=ge||re,$e=$e||ne,st=st||ie,(re!==p||ge!==y)&&(i.blendEquationSeparate(dt[re],dt[ge]),p=re,y=ge),(ne!==f||ie!==E||$e!==T||st!==z)&&(i.blendFuncSeparate(U[ne],U[ie],U[$e],U[st]),f=ne,E=ie,T=$e,z=st),(mt.equals(C)===!1||Et!==D)&&(i.blendColor(mt.r,mt.g,mt.b,Et),C.copy(mt),D=Et),v=I,B=!1}function tt(I,re){I.side===mi?he(i.CULL_FACE):xe(i.CULL_FACE);let ne=I.side===Cn;re&&(ne=!ne),ot(ne),I.blending===gs&&I.transparent===!1?ut(Zi):ut(I.blending,I.blendEquation,I.blendSrc,I.blendDst,I.blendEquationAlpha,I.blendSrcAlpha,I.blendDstAlpha,I.blendColor,I.blendAlpha,I.premultipliedAlpha),s.setFunc(I.depthFunc),s.setTest(I.depthTest),s.setMask(I.depthWrite),r.setMask(I.colorWrite);const ie=I.stencilWrite;a.setTest(ie),ie&&(a.setMask(I.stencilWriteMask),a.setFunc(I.stencilFunc,I.stencilRef,I.stencilFuncMask),a.setOp(I.stencilFail,I.stencilZFail,I.stencilZPass)),Ye(I.polygonOffset,I.polygonOffsetFactor,I.polygonOffsetUnits),I.alphaToCoverage===!0?xe(i.SAMPLE_ALPHA_TO_COVERAGE):he(i.SAMPLE_ALPHA_TO_COVERAGE)}function ot(I){w!==I&&(I?i.frontFace(i.CW):i.frontFace(i.CCW),w=I)}function Fe(I){I!==Ep?(xe(i.CULL_FACE),I!==x&&(I===Lu?i.cullFace(i.BACK):I===bp?i.cullFace(i.FRONT):i.cullFace(i.FRONT_AND_BACK))):he(i.CULL_FACE),x=I}function yt(I){I!==R&&(W&&i.lineWidth(I),R=I)}function Ye(I,re,ne){I?(xe(i.POLYGON_OFFSET_FILL),(j!==re||O!==ne)&&(i.polygonOffset(re,ne),j=re,O=ne)):he(i.POLYGON_OFFSET_FILL)}function We(I){I?xe(i.SCISSOR_TEST):he(i.SCISSOR_TEST)}function L(I){I===void 0&&(I=i.TEXTURE0+K-1),ee!==I&&(i.activeTexture(I),ee=I)}function S(I,re,ne){ne===void 0&&(ee===null?ne=i.TEXTURE0+K-1:ne=ee);let ie=pe[ne];ie===void 0&&(ie={type:void 0,texture:void 0},pe[ne]=ie),(ie.type!==I||ie.texture!==re)&&(ee!==ne&&(i.activeTexture(ne),ee=ne),i.bindTexture(I,re||le[I]),ie.type=I,ie.texture=re)}function Z(){const I=pe[ee];I!==void 0&&I.type!==void 0&&(i.bindTexture(I.type,null),I.type=void 0,I.texture=void 0)}function ae(){try{i.compressedTexImage2D.apply(i,arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function Q(){try{i.compressedTexImage3D.apply(i,arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function G(){try{i.texSubImage2D.apply(i,arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function Ee(){try{i.texSubImage3D.apply(i,arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function me(){try{i.compressedTexSubImage2D.apply(i,arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function we(){try{i.compressedTexSubImage3D.apply(i,arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function je(){try{i.texStorage2D.apply(i,arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function fe(){try{i.texStorage3D.apply(i,arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function Te(){try{i.texImage2D.apply(i,arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function Ke(){try{i.texImage3D.apply(i,arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function ze(I){be.equals(I)===!1&&(i.scissor(I.x,I.y,I.z,I.w),be.copy(I))}function Se(I){ve.equals(I)===!1&&(i.viewport(I.x,I.y,I.z,I.w),ve.copy(I))}function ke(I,re){let ne=l.get(re);ne===void 0&&(ne=new WeakMap,l.set(re,ne));let ie=ne.get(I);ie===void 0&&(ie=i.getUniformBlockIndex(re,I.name),ne.set(I,ie))}function N(I,re){const ie=l.get(re).get(I);o.get(re)!==ie&&(i.uniformBlockBinding(re,ie,I.__bindingPointIndex),o.set(re,ie))}function oe(){i.disable(i.BLEND),i.disable(i.CULL_FACE),i.disable(i.DEPTH_TEST),i.disable(i.POLYGON_OFFSET_FILL),i.disable(i.SCISSOR_TEST),i.disable(i.STENCIL_TEST),i.disable(i.SAMPLE_ALPHA_TO_COVERAGE),i.blendEquation(i.FUNC_ADD),i.blendFunc(i.ONE,i.ZERO),i.blendFuncSeparate(i.ONE,i.ZERO,i.ONE,i.ZERO),i.blendColor(0,0,0,0),i.colorMask(!0,!0,!0,!0),i.clearColor(0,0,0,0),i.depthMask(!0),i.depthFunc(i.LESS),i.clearDepth(1),i.stencilMask(4294967295),i.stencilFunc(i.ALWAYS,0,4294967295),i.stencilOp(i.KEEP,i.KEEP,i.KEEP),i.clearStencil(0),i.cullFace(i.BACK),i.frontFace(i.CCW),i.polygonOffset(0,0),i.activeTexture(i.TEXTURE0),i.bindFramebuffer(i.FRAMEBUFFER,null),i.bindFramebuffer(i.DRAW_FRAMEBUFFER,null),i.bindFramebuffer(i.READ_FRAMEBUFFER,null),i.useProgram(null),i.lineWidth(1),i.scissor(0,0,i.canvas.width,i.canvas.height),i.viewport(0,0,i.canvas.width,i.canvas.height),c={},ee=null,pe={},u={},h=new WeakMap,d=[],m=null,_=!1,v=null,p=null,f=null,E=null,y=null,T=null,z=null,C=new nt(0,0,0),D=0,B=!1,w=null,x=null,R=null,j=null,O=null,be.set(0,0,i.canvas.width,i.canvas.height),ve.set(0,0,i.canvas.width,i.canvas.height),r.reset(),s.reset(),a.reset()}return{buffers:{color:r,depth:s,stencil:a},enable:xe,disable:he,bindFramebuffer:Be,drawBuffers:Ve,useProgram:Ne,setBlending:ut,setMaterial:tt,setFlipSided:ot,setCullFace:Fe,setLineWidth:yt,setPolygonOffset:Ye,setScissorTest:We,activeTexture:L,bindTexture:S,unbindTexture:Z,compressedTexImage2D:ae,compressedTexImage3D:Q,texImage2D:Te,texImage3D:Ke,updateUBOMapping:ke,uniformBlockBinding:N,texStorage2D:je,texStorage3D:fe,texSubImage2D:G,texSubImage3D:Ee,compressedTexSubImage2D:me,compressedTexSubImage3D:we,scissor:ze,viewport:Se,reset:oe}}function wh(i,e,t,n){const r=Cx(n);switch(t){case Fd:return i*e;case Bd:return i*e;case zd:return i*e*2;case kd:return i*e/r.components*r.byteLength;case Uc:return i*e/r.components*r.byteLength;case Hd:return i*e*2/r.components*r.byteLength;case Nc:return i*e*2/r.components*r.byteLength;case Od:return i*e*3/r.components*r.byteLength;case ri:return i*e*4/r.components*r.byteLength;case Fc:return i*e*4/r.components*r.byteLength;case no:case io:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*8;case ro:case so:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*16;case Yl:case $l:return Math.max(i,16)*Math.max(e,8)/4;case Xl:case ql:return Math.max(i,8)*Math.max(e,8)/2;case jl:case Kl:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*8;case Zl:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*16;case Jl:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*16;case Ql:return Math.floor((i+4)/5)*Math.floor((e+3)/4)*16;case ec:return Math.floor((i+4)/5)*Math.floor((e+4)/5)*16;case tc:return Math.floor((i+5)/6)*Math.floor((e+4)/5)*16;case nc:return Math.floor((i+5)/6)*Math.floor((e+5)/6)*16;case ic:return Math.floor((i+7)/8)*Math.floor((e+4)/5)*16;case rc:return Math.floor((i+7)/8)*Math.floor((e+5)/6)*16;case sc:return Math.floor((i+7)/8)*Math.floor((e+7)/8)*16;case ac:return Math.floor((i+9)/10)*Math.floor((e+4)/5)*16;case oc:return Math.floor((i+9)/10)*Math.floor((e+5)/6)*16;case lc:return Math.floor((i+9)/10)*Math.floor((e+7)/8)*16;case cc:return Math.floor((i+9)/10)*Math.floor((e+9)/10)*16;case uc:return Math.floor((i+11)/12)*Math.floor((e+9)/10)*16;case hc:return Math.floor((i+11)/12)*Math.floor((e+11)/12)*16;case ao:case dc:case fc:return Math.ceil(i/4)*Math.ceil(e/4)*16;case Vd:case pc:return Math.ceil(i/4)*Math.ceil(e/4)*8;case mc:case gc:return Math.ceil(i/4)*Math.ceil(e/4)*16}throw new Error(`Unable to determine texture byte length for ${t} format.`)}function Cx(i){switch(i){case Ui:case Id:return{byteLength:1,components:1};case la:case Ud:case ha:return{byteLength:2,components:1};case Dc:case Ic:return{byteLength:2,components:4};case wr:case Lc:case Ci:return{byteLength:4,components:1};case Nd:return{byteLength:4,components:3}}throw new Error(`Unknown texture type ${i}.`)}function Px(i,e,t,n,r,s,a){const o=e.has("WEBGL_multisampled_render_to_texture")?e.get("WEBGL_multisampled_render_to_texture"):null,l=typeof navigator>"u"?!1:/OculusBrowser/g.test(navigator.userAgent),c=new Xe,u=new WeakMap;let h;const d=new WeakMap;let m=!1;try{m=typeof OffscreenCanvas<"u"&&new OffscreenCanvas(1,1).getContext("2d")!==null}catch{}function _(L,S){return m?new OffscreenCanvas(L,S):_o("canvas")}function v(L,S,Z){let ae=1;const Q=We(L);if((Q.width>Z||Q.height>Z)&&(ae=Z/Math.max(Q.width,Q.height)),ae<1)if(typeof HTMLImageElement<"u"&&L instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&L instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&L instanceof ImageBitmap||typeof VideoFrame<"u"&&L instanceof VideoFrame){const G=Math.floor(ae*Q.width),Ee=Math.floor(ae*Q.height);h===void 0&&(h=_(G,Ee));const me=S?_(G,Ee):h;return me.width=G,me.height=Ee,me.getContext("2d").drawImage(L,0,0,G,Ee),console.warn("THREE.WebGLRenderer: Texture has been resized from ("+Q.width+"x"+Q.height+") to ("+G+"x"+Ee+")."),me}else return"data"in L&&console.warn("THREE.WebGLRenderer: Image in DataTexture is too big ("+Q.width+"x"+Q.height+")."),L;return L}function p(L){return L.generateMipmaps&&L.minFilter!==Wn&&L.minFilter!==ti}function f(L){i.generateMipmap(L)}function E(L,S,Z,ae,Q=!1){if(L!==null){if(i[L]!==void 0)return i[L];console.warn("THREE.WebGLRenderer: Attempt to use non-existing WebGL internal format '"+L+"'")}let G=S;if(S===i.RED&&(Z===i.FLOAT&&(G=i.R32F),Z===i.HALF_FLOAT&&(G=i.R16F),Z===i.UNSIGNED_BYTE&&(G=i.R8)),S===i.RED_INTEGER&&(Z===i.UNSIGNED_BYTE&&(G=i.R8UI),Z===i.UNSIGNED_SHORT&&(G=i.R16UI),Z===i.UNSIGNED_INT&&(G=i.R32UI),Z===i.BYTE&&(G=i.R8I),Z===i.SHORT&&(G=i.R16I),Z===i.INT&&(G=i.R32I)),S===i.RG&&(Z===i.FLOAT&&(G=i.RG32F),Z===i.HALF_FLOAT&&(G=i.RG16F),Z===i.UNSIGNED_BYTE&&(G=i.RG8)),S===i.RG_INTEGER&&(Z===i.UNSIGNED_BYTE&&(G=i.RG8UI),Z===i.UNSIGNED_SHORT&&(G=i.RG16UI),Z===i.UNSIGNED_INT&&(G=i.RG32UI),Z===i.BYTE&&(G=i.RG8I),Z===i.SHORT&&(G=i.RG16I),Z===i.INT&&(G=i.RG32I)),S===i.RGB&&Z===i.UNSIGNED_INT_5_9_9_9_REV&&(G=i.RGB9_E5),S===i.RGBA){const Ee=Q?fo:St.getTransfer(ae);Z===i.FLOAT&&(G=i.RGBA32F),Z===i.HALF_FLOAT&&(G=i.RGBA16F),Z===i.UNSIGNED_BYTE&&(G=Ee===Nt?i.SRGB8_ALPHA8:i.RGBA8),Z===i.UNSIGNED_SHORT_4_4_4_4&&(G=i.RGBA4),Z===i.UNSIGNED_SHORT_5_5_5_1&&(G=i.RGB5_A1)}return(G===i.R16F||G===i.R32F||G===i.RG16F||G===i.RG32F||G===i.RGBA16F||G===i.RGBA32F)&&e.get("EXT_color_buffer_float"),G}function y(L,S){let Z;return L?S===null||S===wr||S===Ts?Z=i.DEPTH24_STENCIL8:S===Ci?Z=i.DEPTH32F_STENCIL8:S===la&&(Z=i.DEPTH24_STENCIL8,console.warn("DepthTexture: 16 bit depth attachment is not supported with stencil. Using 24-bit attachment.")):S===null||S===wr||S===Ts?Z=i.DEPTH_COMPONENT24:S===Ci?Z=i.DEPTH_COMPONENT32F:S===la&&(Z=i.DEPTH_COMPONENT16),Z}function T(L,S){return p(L)===!0||L.isFramebufferTexture&&L.minFilter!==Wn&&L.minFilter!==ti?Math.log2(Math.max(S.width,S.height))+1:L.mipmaps!==void 0&&L.mipmaps.length>0?L.mipmaps.length:L.isCompressedTexture&&Array.isArray(L.image)?S.mipmaps.length:1}function z(L){const S=L.target;S.removeEventListener("dispose",z),D(S),S.isVideoTexture&&u.delete(S)}function C(L){const S=L.target;S.removeEventListener("dispose",C),w(S)}function D(L){const S=n.get(L);if(S.__webglInit===void 0)return;const Z=L.source,ae=d.get(Z);if(ae){const Q=ae[S.__cacheKey];Q.usedTimes--,Q.usedTimes===0&&B(L),Object.keys(ae).length===0&&d.delete(Z)}n.remove(L)}function B(L){const S=n.get(L);i.deleteTexture(S.__webglTexture);const Z=L.source,ae=d.get(Z);delete ae[S.__cacheKey],a.memory.textures--}function w(L){const S=n.get(L);if(L.depthTexture&&L.depthTexture.dispose(),L.isWebGLCubeRenderTarget)for(let ae=0;ae<6;ae++){if(Array.isArray(S.__webglFramebuffer[ae]))for(let Q=0;Q<S.__webglFramebuffer[ae].length;Q++)i.deleteFramebuffer(S.__webglFramebuffer[ae][Q]);else i.deleteFramebuffer(S.__webglFramebuffer[ae]);S.__webglDepthbuffer&&i.deleteRenderbuffer(S.__webglDepthbuffer[ae])}else{if(Array.isArray(S.__webglFramebuffer))for(let ae=0;ae<S.__webglFramebuffer.length;ae++)i.deleteFramebuffer(S.__webglFramebuffer[ae]);else i.deleteFramebuffer(S.__webglFramebuffer);if(S.__webglDepthbuffer&&i.deleteRenderbuffer(S.__webglDepthbuffer),S.__webglMultisampledFramebuffer&&i.deleteFramebuffer(S.__webglMultisampledFramebuffer),S.__webglColorRenderbuffer)for(let ae=0;ae<S.__webglColorRenderbuffer.length;ae++)S.__webglColorRenderbuffer[ae]&&i.deleteRenderbuffer(S.__webglColorRenderbuffer[ae]);S.__webglDepthRenderbuffer&&i.deleteRenderbuffer(S.__webglDepthRenderbuffer)}const Z=L.textures;for(let ae=0,Q=Z.length;ae<Q;ae++){const G=n.get(Z[ae]);G.__webglTexture&&(i.deleteTexture(G.__webglTexture),a.memory.textures--),n.remove(Z[ae])}n.remove(L)}let x=0;function R(){x=0}function j(){const L=x;return L>=r.maxTextures&&console.warn("THREE.WebGLTextures: Trying to use "+L+" texture units while this GPU supports only "+r.maxTextures),x+=1,L}function O(L){const S=[];return S.push(L.wrapS),S.push(L.wrapT),S.push(L.wrapR||0),S.push(L.magFilter),S.push(L.minFilter),S.push(L.anisotropy),S.push(L.internalFormat),S.push(L.format),S.push(L.type),S.push(L.generateMipmaps),S.push(L.premultiplyAlpha),S.push(L.flipY),S.push(L.unpackAlignment),S.push(L.colorSpace),S.join()}function K(L,S){const Z=n.get(L);if(L.isVideoTexture&&yt(L),L.isRenderTargetTexture===!1&&L.version>0&&Z.__version!==L.version){const ae=L.image;if(ae===null)console.warn("THREE.WebGLRenderer: Texture marked for update but no image data found.");else if(ae.complete===!1)console.warn("THREE.WebGLRenderer: Texture marked for update but image is incomplete");else{ve(Z,L,S);return}}t.bindTexture(i.TEXTURE_2D,Z.__webglTexture,i.TEXTURE0+S)}function W(L,S){const Z=n.get(L);if(L.version>0&&Z.__version!==L.version){ve(Z,L,S);return}t.bindTexture(i.TEXTURE_2D_ARRAY,Z.__webglTexture,i.TEXTURE0+S)}function J(L,S){const Z=n.get(L);if(L.version>0&&Z.__version!==L.version){ve(Z,L,S);return}t.bindTexture(i.TEXTURE_3D,Z.__webglTexture,i.TEXTURE0+S)}function Y(L,S){const Z=n.get(L);if(L.version>0&&Z.__version!==L.version){te(Z,L,S);return}t.bindTexture(i.TEXTURE_CUBE_MAP,Z.__webglTexture,i.TEXTURE0+S)}const ee={[Gl]:i.REPEAT,[yr]:i.CLAMP_TO_EDGE,[Wl]:i.MIRRORED_REPEAT},pe={[Wn]:i.NEAREST,[rm]:i.NEAREST_MIPMAP_NEAREST,[Sa]:i.NEAREST_MIPMAP_LINEAR,[ti]:i.LINEAR,[tl]:i.LINEAR_MIPMAP_NEAREST,[Er]:i.LINEAR_MIPMAP_LINEAR},ue={[lm]:i.NEVER,[pm]:i.ALWAYS,[cm]:i.LESS,[Wd]:i.LEQUAL,[um]:i.EQUAL,[fm]:i.GEQUAL,[hm]:i.GREATER,[dm]:i.NOTEQUAL};function _e(L,S){if(S.type===Ci&&e.has("OES_texture_float_linear")===!1&&(S.magFilter===ti||S.magFilter===tl||S.magFilter===Sa||S.magFilter===Er||S.minFilter===ti||S.minFilter===tl||S.minFilter===Sa||S.minFilter===Er)&&console.warn("THREE.WebGLRenderer: Unable to use linear filtering with floating point textures. OES_texture_float_linear not supported on this device."),i.texParameteri(L,i.TEXTURE_WRAP_S,ee[S.wrapS]),i.texParameteri(L,i.TEXTURE_WRAP_T,ee[S.wrapT]),(L===i.TEXTURE_3D||L===i.TEXTURE_2D_ARRAY)&&i.texParameteri(L,i.TEXTURE_WRAP_R,ee[S.wrapR]),i.texParameteri(L,i.TEXTURE_MAG_FILTER,pe[S.magFilter]),i.texParameteri(L,i.TEXTURE_MIN_FILTER,pe[S.minFilter]),S.compareFunction&&(i.texParameteri(L,i.TEXTURE_COMPARE_MODE,i.COMPARE_REF_TO_TEXTURE),i.texParameteri(L,i.TEXTURE_COMPARE_FUNC,ue[S.compareFunction])),e.has("EXT_texture_filter_anisotropic")===!0){if(S.magFilter===Wn||S.minFilter!==Sa&&S.minFilter!==Er||S.type===Ci&&e.has("OES_texture_float_linear")===!1)return;if(S.anisotropy>1||n.get(S).__currentAnisotropy){const Z=e.get("EXT_texture_filter_anisotropic");i.texParameterf(L,Z.TEXTURE_MAX_ANISOTROPY_EXT,Math.min(S.anisotropy,r.getMaxAnisotropy())),n.get(S).__currentAnisotropy=S.anisotropy}}}function be(L,S){let Z=!1;L.__webglInit===void 0&&(L.__webglInit=!0,S.addEventListener("dispose",z));const ae=S.source;let Q=d.get(ae);Q===void 0&&(Q={},d.set(ae,Q));const G=O(S);if(G!==L.__cacheKey){Q[G]===void 0&&(Q[G]={texture:i.createTexture(),usedTimes:0},a.memory.textures++,Z=!0),Q[G].usedTimes++;const Ee=Q[L.__cacheKey];Ee!==void 0&&(Q[L.__cacheKey].usedTimes--,Ee.usedTimes===0&&B(S)),L.__cacheKey=G,L.__webglTexture=Q[G].texture}return Z}function ve(L,S,Z){let ae=i.TEXTURE_2D;(S.isDataArrayTexture||S.isCompressedArrayTexture)&&(ae=i.TEXTURE_2D_ARRAY),S.isData3DTexture&&(ae=i.TEXTURE_3D);const Q=be(L,S),G=S.source;t.bindTexture(ae,L.__webglTexture,i.TEXTURE0+Z);const Ee=n.get(G);if(G.version!==Ee.__version||Q===!0){t.activeTexture(i.TEXTURE0+Z);const me=St.getPrimaries(St.workingColorSpace),we=S.colorSpace===Ki?null:St.getPrimaries(S.colorSpace),je=S.colorSpace===Ki||me===we?i.NONE:i.BROWSER_DEFAULT_WEBGL;i.pixelStorei(i.UNPACK_FLIP_Y_WEBGL,S.flipY),i.pixelStorei(i.UNPACK_PREMULTIPLY_ALPHA_WEBGL,S.premultiplyAlpha),i.pixelStorei(i.UNPACK_ALIGNMENT,S.unpackAlignment),i.pixelStorei(i.UNPACK_COLORSPACE_CONVERSION_WEBGL,je);let fe=v(S.image,!1,r.maxTextureSize);fe=Ye(S,fe);const Te=s.convert(S.format,S.colorSpace),Ke=s.convert(S.type);let ze=E(S.internalFormat,Te,Ke,S.colorSpace,S.isVideoTexture);_e(ae,S);let Se;const ke=S.mipmaps,N=S.isVideoTexture!==!0,oe=Ee.__version===void 0||Q===!0,I=G.dataReady,re=T(S,fe);if(S.isDepthTexture)ze=y(S.format===ws,S.type),oe&&(N?t.texStorage2D(i.TEXTURE_2D,1,ze,fe.width,fe.height):t.texImage2D(i.TEXTURE_2D,0,ze,fe.width,fe.height,0,Te,Ke,null));else if(S.isDataTexture)if(ke.length>0){N&&oe&&t.texStorage2D(i.TEXTURE_2D,re,ze,ke[0].width,ke[0].height);for(let ne=0,ie=ke.length;ne<ie;ne++)Se=ke[ne],N?I&&t.texSubImage2D(i.TEXTURE_2D,ne,0,0,Se.width,Se.height,Te,Ke,Se.data):t.texImage2D(i.TEXTURE_2D,ne,ze,Se.width,Se.height,0,Te,Ke,Se.data);S.generateMipmaps=!1}else N?(oe&&t.texStorage2D(i.TEXTURE_2D,re,ze,fe.width,fe.height),I&&t.texSubImage2D(i.TEXTURE_2D,0,0,0,fe.width,fe.height,Te,Ke,fe.data)):t.texImage2D(i.TEXTURE_2D,0,ze,fe.width,fe.height,0,Te,Ke,fe.data);else if(S.isCompressedTexture)if(S.isCompressedArrayTexture){N&&oe&&t.texStorage3D(i.TEXTURE_2D_ARRAY,re,ze,ke[0].width,ke[0].height,fe.depth);for(let ne=0,ie=ke.length;ne<ie;ne++)if(Se=ke[ne],S.format!==ri)if(Te!==null)if(N){if(I)if(S.layerUpdates.size>0){const ge=wh(Se.width,Se.height,S.format,S.type);for(const $e of S.layerUpdates){const st=Se.data.subarray($e*ge/Se.data.BYTES_PER_ELEMENT,($e+1)*ge/Se.data.BYTES_PER_ELEMENT);t.compressedTexSubImage3D(i.TEXTURE_2D_ARRAY,ne,0,0,$e,Se.width,Se.height,1,Te,st,0,0)}S.clearLayerUpdates()}else t.compressedTexSubImage3D(i.TEXTURE_2D_ARRAY,ne,0,0,0,Se.width,Se.height,fe.depth,Te,Se.data,0,0)}else t.compressedTexImage3D(i.TEXTURE_2D_ARRAY,ne,ze,Se.width,Se.height,fe.depth,0,Se.data,0,0);else console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()");else N?I&&t.texSubImage3D(i.TEXTURE_2D_ARRAY,ne,0,0,0,Se.width,Se.height,fe.depth,Te,Ke,Se.data):t.texImage3D(i.TEXTURE_2D_ARRAY,ne,ze,Se.width,Se.height,fe.depth,0,Te,Ke,Se.data)}else{N&&oe&&t.texStorage2D(i.TEXTURE_2D,re,ze,ke[0].width,ke[0].height);for(let ne=0,ie=ke.length;ne<ie;ne++)Se=ke[ne],S.format!==ri?Te!==null?N?I&&t.compressedTexSubImage2D(i.TEXTURE_2D,ne,0,0,Se.width,Se.height,Te,Se.data):t.compressedTexImage2D(i.TEXTURE_2D,ne,ze,Se.width,Se.height,0,Se.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()"):N?I&&t.texSubImage2D(i.TEXTURE_2D,ne,0,0,Se.width,Se.height,Te,Ke,Se.data):t.texImage2D(i.TEXTURE_2D,ne,ze,Se.width,Se.height,0,Te,Ke,Se.data)}else if(S.isDataArrayTexture)if(N){if(oe&&t.texStorage3D(i.TEXTURE_2D_ARRAY,re,ze,fe.width,fe.height,fe.depth),I)if(S.layerUpdates.size>0){const ne=wh(fe.width,fe.height,S.format,S.type);for(const ie of S.layerUpdates){const ge=fe.data.subarray(ie*ne/fe.data.BYTES_PER_ELEMENT,(ie+1)*ne/fe.data.BYTES_PER_ELEMENT);t.texSubImage3D(i.TEXTURE_2D_ARRAY,0,0,0,ie,fe.width,fe.height,1,Te,Ke,ge)}S.clearLayerUpdates()}else t.texSubImage3D(i.TEXTURE_2D_ARRAY,0,0,0,0,fe.width,fe.height,fe.depth,Te,Ke,fe.data)}else t.texImage3D(i.TEXTURE_2D_ARRAY,0,ze,fe.width,fe.height,fe.depth,0,Te,Ke,fe.data);else if(S.isData3DTexture)N?(oe&&t.texStorage3D(i.TEXTURE_3D,re,ze,fe.width,fe.height,fe.depth),I&&t.texSubImage3D(i.TEXTURE_3D,0,0,0,0,fe.width,fe.height,fe.depth,Te,Ke,fe.data)):t.texImage3D(i.TEXTURE_3D,0,ze,fe.width,fe.height,fe.depth,0,Te,Ke,fe.data);else if(S.isFramebufferTexture){if(oe)if(N)t.texStorage2D(i.TEXTURE_2D,re,ze,fe.width,fe.height);else{let ne=fe.width,ie=fe.height;for(let ge=0;ge<re;ge++)t.texImage2D(i.TEXTURE_2D,ge,ze,ne,ie,0,Te,Ke,null),ne>>=1,ie>>=1}}else if(ke.length>0){if(N&&oe){const ne=We(ke[0]);t.texStorage2D(i.TEXTURE_2D,re,ze,ne.width,ne.height)}for(let ne=0,ie=ke.length;ne<ie;ne++)Se=ke[ne],N?I&&t.texSubImage2D(i.TEXTURE_2D,ne,0,0,Te,Ke,Se):t.texImage2D(i.TEXTURE_2D,ne,ze,Te,Ke,Se);S.generateMipmaps=!1}else if(N){if(oe){const ne=We(fe);t.texStorage2D(i.TEXTURE_2D,re,ze,ne.width,ne.height)}I&&t.texSubImage2D(i.TEXTURE_2D,0,0,0,Te,Ke,fe)}else t.texImage2D(i.TEXTURE_2D,0,ze,Te,Ke,fe);p(S)&&f(ae),Ee.__version=G.version,S.onUpdate&&S.onUpdate(S)}L.__version=S.version}function te(L,S,Z){if(S.image.length!==6)return;const ae=be(L,S),Q=S.source;t.bindTexture(i.TEXTURE_CUBE_MAP,L.__webglTexture,i.TEXTURE0+Z);const G=n.get(Q);if(Q.version!==G.__version||ae===!0){t.activeTexture(i.TEXTURE0+Z);const Ee=St.getPrimaries(St.workingColorSpace),me=S.colorSpace===Ki?null:St.getPrimaries(S.colorSpace),we=S.colorSpace===Ki||Ee===me?i.NONE:i.BROWSER_DEFAULT_WEBGL;i.pixelStorei(i.UNPACK_FLIP_Y_WEBGL,S.flipY),i.pixelStorei(i.UNPACK_PREMULTIPLY_ALPHA_WEBGL,S.premultiplyAlpha),i.pixelStorei(i.UNPACK_ALIGNMENT,S.unpackAlignment),i.pixelStorei(i.UNPACK_COLORSPACE_CONVERSION_WEBGL,we);const je=S.isCompressedTexture||S.image[0].isCompressedTexture,fe=S.image[0]&&S.image[0].isDataTexture,Te=[];for(let ie=0;ie<6;ie++)!je&&!fe?Te[ie]=v(S.image[ie],!0,r.maxCubemapSize):Te[ie]=fe?S.image[ie].image:S.image[ie],Te[ie]=Ye(S,Te[ie]);const Ke=Te[0],ze=s.convert(S.format,S.colorSpace),Se=s.convert(S.type),ke=E(S.internalFormat,ze,Se,S.colorSpace),N=S.isVideoTexture!==!0,oe=G.__version===void 0||ae===!0,I=Q.dataReady;let re=T(S,Ke);_e(i.TEXTURE_CUBE_MAP,S);let ne;if(je){N&&oe&&t.texStorage2D(i.TEXTURE_CUBE_MAP,re,ke,Ke.width,Ke.height);for(let ie=0;ie<6;ie++){ne=Te[ie].mipmaps;for(let ge=0;ge<ne.length;ge++){const $e=ne[ge];S.format!==ri?ze!==null?N?I&&t.compressedTexSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+ie,ge,0,0,$e.width,$e.height,ze,$e.data):t.compressedTexImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+ie,ge,ke,$e.width,$e.height,0,$e.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .setTextureCube()"):N?I&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+ie,ge,0,0,$e.width,$e.height,ze,Se,$e.data):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+ie,ge,ke,$e.width,$e.height,0,ze,Se,$e.data)}}}else{if(ne=S.mipmaps,N&&oe){ne.length>0&&re++;const ie=We(Te[0]);t.texStorage2D(i.TEXTURE_CUBE_MAP,re,ke,ie.width,ie.height)}for(let ie=0;ie<6;ie++)if(fe){N?I&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+ie,0,0,0,Te[ie].width,Te[ie].height,ze,Se,Te[ie].data):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+ie,0,ke,Te[ie].width,Te[ie].height,0,ze,Se,Te[ie].data);for(let ge=0;ge<ne.length;ge++){const st=ne[ge].image[ie].image;N?I&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+ie,ge+1,0,0,st.width,st.height,ze,Se,st.data):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+ie,ge+1,ke,st.width,st.height,0,ze,Se,st.data)}}else{N?I&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+ie,0,0,0,ze,Se,Te[ie]):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+ie,0,ke,ze,Se,Te[ie]);for(let ge=0;ge<ne.length;ge++){const $e=ne[ge];N?I&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+ie,ge+1,0,0,ze,Se,$e.image[ie]):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+ie,ge+1,ke,ze,Se,$e.image[ie])}}}p(S)&&f(i.TEXTURE_CUBE_MAP),G.__version=Q.version,S.onUpdate&&S.onUpdate(S)}L.__version=S.version}function le(L,S,Z,ae,Q,G){const Ee=s.convert(Z.format,Z.colorSpace),me=s.convert(Z.type),we=E(Z.internalFormat,Ee,me,Z.colorSpace);if(!n.get(S).__hasExternalTextures){const fe=Math.max(1,S.width>>G),Te=Math.max(1,S.height>>G);Q===i.TEXTURE_3D||Q===i.TEXTURE_2D_ARRAY?t.texImage3D(Q,G,we,fe,Te,S.depth,0,Ee,me,null):t.texImage2D(Q,G,we,fe,Te,0,Ee,me,null)}t.bindFramebuffer(i.FRAMEBUFFER,L),Fe(S)?o.framebufferTexture2DMultisampleEXT(i.FRAMEBUFFER,ae,Q,n.get(Z).__webglTexture,0,ot(S)):(Q===i.TEXTURE_2D||Q>=i.TEXTURE_CUBE_MAP_POSITIVE_X&&Q<=i.TEXTURE_CUBE_MAP_NEGATIVE_Z)&&i.framebufferTexture2D(i.FRAMEBUFFER,ae,Q,n.get(Z).__webglTexture,G),t.bindFramebuffer(i.FRAMEBUFFER,null)}function xe(L,S,Z){if(i.bindRenderbuffer(i.RENDERBUFFER,L),S.depthBuffer){const ae=S.depthTexture,Q=ae&&ae.isDepthTexture?ae.type:null,G=y(S.stencilBuffer,Q),Ee=S.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,me=ot(S);Fe(S)?o.renderbufferStorageMultisampleEXT(i.RENDERBUFFER,me,G,S.width,S.height):Z?i.renderbufferStorageMultisample(i.RENDERBUFFER,me,G,S.width,S.height):i.renderbufferStorage(i.RENDERBUFFER,G,S.width,S.height),i.framebufferRenderbuffer(i.FRAMEBUFFER,Ee,i.RENDERBUFFER,L)}else{const ae=S.textures;for(let Q=0;Q<ae.length;Q++){const G=ae[Q],Ee=s.convert(G.format,G.colorSpace),me=s.convert(G.type),we=E(G.internalFormat,Ee,me,G.colorSpace),je=ot(S);Z&&Fe(S)===!1?i.renderbufferStorageMultisample(i.RENDERBUFFER,je,we,S.width,S.height):Fe(S)?o.renderbufferStorageMultisampleEXT(i.RENDERBUFFER,je,we,S.width,S.height):i.renderbufferStorage(i.RENDERBUFFER,we,S.width,S.height)}}i.bindRenderbuffer(i.RENDERBUFFER,null)}function he(L,S){if(S&&S.isWebGLCubeRenderTarget)throw new Error("Depth Texture with cube render targets is not supported");if(t.bindFramebuffer(i.FRAMEBUFFER,L),!(S.depthTexture&&S.depthTexture.isDepthTexture))throw new Error("renderTarget.depthTexture must be an instance of THREE.DepthTexture");(!n.get(S.depthTexture).__webglTexture||S.depthTexture.image.width!==S.width||S.depthTexture.image.height!==S.height)&&(S.depthTexture.image.width=S.width,S.depthTexture.image.height=S.height,S.depthTexture.needsUpdate=!0),K(S.depthTexture,0);const ae=n.get(S.depthTexture).__webglTexture,Q=ot(S);if(S.depthTexture.format===_s)Fe(S)?o.framebufferTexture2DMultisampleEXT(i.FRAMEBUFFER,i.DEPTH_ATTACHMENT,i.TEXTURE_2D,ae,0,Q):i.framebufferTexture2D(i.FRAMEBUFFER,i.DEPTH_ATTACHMENT,i.TEXTURE_2D,ae,0);else if(S.depthTexture.format===ws)Fe(S)?o.framebufferTexture2DMultisampleEXT(i.FRAMEBUFFER,i.DEPTH_STENCIL_ATTACHMENT,i.TEXTURE_2D,ae,0,Q):i.framebufferTexture2D(i.FRAMEBUFFER,i.DEPTH_STENCIL_ATTACHMENT,i.TEXTURE_2D,ae,0);else throw new Error("Unknown depthTexture format")}function Be(L){const S=n.get(L),Z=L.isWebGLCubeRenderTarget===!0;if(S.__boundDepthTexture!==L.depthTexture){const ae=L.depthTexture;if(S.__depthDisposeCallback&&S.__depthDisposeCallback(),ae){const Q=()=>{delete S.__boundDepthTexture,delete S.__depthDisposeCallback,ae.removeEventListener("dispose",Q)};ae.addEventListener("dispose",Q),S.__depthDisposeCallback=Q}S.__boundDepthTexture=ae}if(L.depthTexture&&!S.__autoAllocateDepthBuffer){if(Z)throw new Error("target.depthTexture not supported in Cube render targets");he(S.__webglFramebuffer,L)}else if(Z){S.__webglDepthbuffer=[];for(let ae=0;ae<6;ae++)if(t.bindFramebuffer(i.FRAMEBUFFER,S.__webglFramebuffer[ae]),S.__webglDepthbuffer[ae]===void 0)S.__webglDepthbuffer[ae]=i.createRenderbuffer(),xe(S.__webglDepthbuffer[ae],L,!1);else{const Q=L.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,G=S.__webglDepthbuffer[ae];i.bindRenderbuffer(i.RENDERBUFFER,G),i.framebufferRenderbuffer(i.FRAMEBUFFER,Q,i.RENDERBUFFER,G)}}else if(t.bindFramebuffer(i.FRAMEBUFFER,S.__webglFramebuffer),S.__webglDepthbuffer===void 0)S.__webglDepthbuffer=i.createRenderbuffer(),xe(S.__webglDepthbuffer,L,!1);else{const ae=L.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,Q=S.__webglDepthbuffer;i.bindRenderbuffer(i.RENDERBUFFER,Q),i.framebufferRenderbuffer(i.FRAMEBUFFER,ae,i.RENDERBUFFER,Q)}t.bindFramebuffer(i.FRAMEBUFFER,null)}function Ve(L,S,Z){const ae=n.get(L);S!==void 0&&le(ae.__webglFramebuffer,L,L.texture,i.COLOR_ATTACHMENT0,i.TEXTURE_2D,0),Z!==void 0&&Be(L)}function Ne(L){const S=L.texture,Z=n.get(L),ae=n.get(S);L.addEventListener("dispose",C);const Q=L.textures,G=L.isWebGLCubeRenderTarget===!0,Ee=Q.length>1;if(Ee||(ae.__webglTexture===void 0&&(ae.__webglTexture=i.createTexture()),ae.__version=S.version,a.memory.textures++),G){Z.__webglFramebuffer=[];for(let me=0;me<6;me++)if(S.mipmaps&&S.mipmaps.length>0){Z.__webglFramebuffer[me]=[];for(let we=0;we<S.mipmaps.length;we++)Z.__webglFramebuffer[me][we]=i.createFramebuffer()}else Z.__webglFramebuffer[me]=i.createFramebuffer()}else{if(S.mipmaps&&S.mipmaps.length>0){Z.__webglFramebuffer=[];for(let me=0;me<S.mipmaps.length;me++)Z.__webglFramebuffer[me]=i.createFramebuffer()}else Z.__webglFramebuffer=i.createFramebuffer();if(Ee)for(let me=0,we=Q.length;me<we;me++){const je=n.get(Q[me]);je.__webglTexture===void 0&&(je.__webglTexture=i.createTexture(),a.memory.textures++)}if(L.samples>0&&Fe(L)===!1){Z.__webglMultisampledFramebuffer=i.createFramebuffer(),Z.__webglColorRenderbuffer=[],t.bindFramebuffer(i.FRAMEBUFFER,Z.__webglMultisampledFramebuffer);for(let me=0;me<Q.length;me++){const we=Q[me];Z.__webglColorRenderbuffer[me]=i.createRenderbuffer(),i.bindRenderbuffer(i.RENDERBUFFER,Z.__webglColorRenderbuffer[me]);const je=s.convert(we.format,we.colorSpace),fe=s.convert(we.type),Te=E(we.internalFormat,je,fe,we.colorSpace,L.isXRRenderTarget===!0),Ke=ot(L);i.renderbufferStorageMultisample(i.RENDERBUFFER,Ke,Te,L.width,L.height),i.framebufferRenderbuffer(i.FRAMEBUFFER,i.COLOR_ATTACHMENT0+me,i.RENDERBUFFER,Z.__webglColorRenderbuffer[me])}i.bindRenderbuffer(i.RENDERBUFFER,null),L.depthBuffer&&(Z.__webglDepthRenderbuffer=i.createRenderbuffer(),xe(Z.__webglDepthRenderbuffer,L,!0)),t.bindFramebuffer(i.FRAMEBUFFER,null)}}if(G){t.bindTexture(i.TEXTURE_CUBE_MAP,ae.__webglTexture),_e(i.TEXTURE_CUBE_MAP,S);for(let me=0;me<6;me++)if(S.mipmaps&&S.mipmaps.length>0)for(let we=0;we<S.mipmaps.length;we++)le(Z.__webglFramebuffer[me][we],L,S,i.COLOR_ATTACHMENT0,i.TEXTURE_CUBE_MAP_POSITIVE_X+me,we);else le(Z.__webglFramebuffer[me],L,S,i.COLOR_ATTACHMENT0,i.TEXTURE_CUBE_MAP_POSITIVE_X+me,0);p(S)&&f(i.TEXTURE_CUBE_MAP),t.unbindTexture()}else if(Ee){for(let me=0,we=Q.length;me<we;me++){const je=Q[me],fe=n.get(je);t.bindTexture(i.TEXTURE_2D,fe.__webglTexture),_e(i.TEXTURE_2D,je),le(Z.__webglFramebuffer,L,je,i.COLOR_ATTACHMENT0+me,i.TEXTURE_2D,0),p(je)&&f(i.TEXTURE_2D)}t.unbindTexture()}else{let me=i.TEXTURE_2D;if((L.isWebGL3DRenderTarget||L.isWebGLArrayRenderTarget)&&(me=L.isWebGL3DRenderTarget?i.TEXTURE_3D:i.TEXTURE_2D_ARRAY),t.bindTexture(me,ae.__webglTexture),_e(me,S),S.mipmaps&&S.mipmaps.length>0)for(let we=0;we<S.mipmaps.length;we++)le(Z.__webglFramebuffer[we],L,S,i.COLOR_ATTACHMENT0,me,we);else le(Z.__webglFramebuffer,L,S,i.COLOR_ATTACHMENT0,me,0);p(S)&&f(me),t.unbindTexture()}L.depthBuffer&&Be(L)}function dt(L){const S=L.textures;for(let Z=0,ae=S.length;Z<ae;Z++){const Q=S[Z];if(p(Q)){const G=L.isWebGLCubeRenderTarget?i.TEXTURE_CUBE_MAP:i.TEXTURE_2D,Ee=n.get(Q).__webglTexture;t.bindTexture(G,Ee),f(G),t.unbindTexture()}}}const U=[],ut=[];function tt(L){if(L.samples>0){if(Fe(L)===!1){const S=L.textures,Z=L.width,ae=L.height;let Q=i.COLOR_BUFFER_BIT;const G=L.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,Ee=n.get(L),me=S.length>1;if(me)for(let we=0;we<S.length;we++)t.bindFramebuffer(i.FRAMEBUFFER,Ee.__webglMultisampledFramebuffer),i.framebufferRenderbuffer(i.FRAMEBUFFER,i.COLOR_ATTACHMENT0+we,i.RENDERBUFFER,null),t.bindFramebuffer(i.FRAMEBUFFER,Ee.__webglFramebuffer),i.framebufferTexture2D(i.DRAW_FRAMEBUFFER,i.COLOR_ATTACHMENT0+we,i.TEXTURE_2D,null,0);t.bindFramebuffer(i.READ_FRAMEBUFFER,Ee.__webglMultisampledFramebuffer),t.bindFramebuffer(i.DRAW_FRAMEBUFFER,Ee.__webglFramebuffer);for(let we=0;we<S.length;we++){if(L.resolveDepthBuffer&&(L.depthBuffer&&(Q|=i.DEPTH_BUFFER_BIT),L.stencilBuffer&&L.resolveStencilBuffer&&(Q|=i.STENCIL_BUFFER_BIT)),me){i.framebufferRenderbuffer(i.READ_FRAMEBUFFER,i.COLOR_ATTACHMENT0,i.RENDERBUFFER,Ee.__webglColorRenderbuffer[we]);const je=n.get(S[we]).__webglTexture;i.framebufferTexture2D(i.DRAW_FRAMEBUFFER,i.COLOR_ATTACHMENT0,i.TEXTURE_2D,je,0)}i.blitFramebuffer(0,0,Z,ae,0,0,Z,ae,Q,i.NEAREST),l===!0&&(U.length=0,ut.length=0,U.push(i.COLOR_ATTACHMENT0+we),L.depthBuffer&&L.resolveDepthBuffer===!1&&(U.push(G),ut.push(G),i.invalidateFramebuffer(i.DRAW_FRAMEBUFFER,ut)),i.invalidateFramebuffer(i.READ_FRAMEBUFFER,U))}if(t.bindFramebuffer(i.READ_FRAMEBUFFER,null),t.bindFramebuffer(i.DRAW_FRAMEBUFFER,null),me)for(let we=0;we<S.length;we++){t.bindFramebuffer(i.FRAMEBUFFER,Ee.__webglMultisampledFramebuffer),i.framebufferRenderbuffer(i.FRAMEBUFFER,i.COLOR_ATTACHMENT0+we,i.RENDERBUFFER,Ee.__webglColorRenderbuffer[we]);const je=n.get(S[we]).__webglTexture;t.bindFramebuffer(i.FRAMEBUFFER,Ee.__webglFramebuffer),i.framebufferTexture2D(i.DRAW_FRAMEBUFFER,i.COLOR_ATTACHMENT0+we,i.TEXTURE_2D,je,0)}t.bindFramebuffer(i.DRAW_FRAMEBUFFER,Ee.__webglMultisampledFramebuffer)}else if(L.depthBuffer&&L.resolveDepthBuffer===!1&&l){const S=L.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT;i.invalidateFramebuffer(i.DRAW_FRAMEBUFFER,[S])}}}function ot(L){return Math.min(r.maxSamples,L.samples)}function Fe(L){const S=n.get(L);return L.samples>0&&e.has("WEBGL_multisampled_render_to_texture")===!0&&S.__useRenderToTexture!==!1}function yt(L){const S=a.render.frame;u.get(L)!==S&&(u.set(L,S),L.update())}function Ye(L,S){const Z=L.colorSpace,ae=L.format,Q=L.type;return L.isCompressedTexture===!0||L.isVideoTexture===!0||Z!==rr&&Z!==Ki&&(St.getTransfer(Z)===Nt?(ae!==ri||Q!==Ui)&&console.warn("THREE.WebGLTextures: sRGB encoded textures have to use RGBAFormat and UnsignedByteType."):console.error("THREE.WebGLTextures: Unsupported texture color space:",Z)),S}function We(L){return typeof HTMLImageElement<"u"&&L instanceof HTMLImageElement?(c.width=L.naturalWidth||L.width,c.height=L.naturalHeight||L.height):typeof VideoFrame<"u"&&L instanceof VideoFrame?(c.width=L.displayWidth,c.height=L.displayHeight):(c.width=L.width,c.height=L.height),c}this.allocateTextureUnit=j,this.resetTextureUnits=R,this.setTexture2D=K,this.setTexture2DArray=W,this.setTexture3D=J,this.setTextureCube=Y,this.rebindTextures=Ve,this.setupRenderTarget=Ne,this.updateRenderTargetMipmap=dt,this.updateMultisampleRenderTarget=tt,this.setupDepthRenderbuffer=Be,this.setupFrameBufferTexture=le,this.useMultisampledRTT=Fe}function Lx(i,e){function t(n,r=Ki){let s;const a=St.getTransfer(r);if(n===Ui)return i.UNSIGNED_BYTE;if(n===Dc)return i.UNSIGNED_SHORT_4_4_4_4;if(n===Ic)return i.UNSIGNED_SHORT_5_5_5_1;if(n===Nd)return i.UNSIGNED_INT_5_9_9_9_REV;if(n===Id)return i.BYTE;if(n===Ud)return i.SHORT;if(n===la)return i.UNSIGNED_SHORT;if(n===Lc)return i.INT;if(n===wr)return i.UNSIGNED_INT;if(n===Ci)return i.FLOAT;if(n===ha)return i.HALF_FLOAT;if(n===Fd)return i.ALPHA;if(n===Od)return i.RGB;if(n===ri)return i.RGBA;if(n===Bd)return i.LUMINANCE;if(n===zd)return i.LUMINANCE_ALPHA;if(n===_s)return i.DEPTH_COMPONENT;if(n===ws)return i.DEPTH_STENCIL;if(n===kd)return i.RED;if(n===Uc)return i.RED_INTEGER;if(n===Hd)return i.RG;if(n===Nc)return i.RG_INTEGER;if(n===Fc)return i.RGBA_INTEGER;if(n===no||n===io||n===ro||n===so)if(a===Nt)if(s=e.get("WEBGL_compressed_texture_s3tc_srgb"),s!==null){if(n===no)return s.COMPRESSED_SRGB_S3TC_DXT1_EXT;if(n===io)return s.COMPRESSED_SRGB_ALPHA_S3TC_DXT1_EXT;if(n===ro)return s.COMPRESSED_SRGB_ALPHA_S3TC_DXT3_EXT;if(n===so)return s.COMPRESSED_SRGB_ALPHA_S3TC_DXT5_EXT}else return null;else if(s=e.get("WEBGL_compressed_texture_s3tc"),s!==null){if(n===no)return s.COMPRESSED_RGB_S3TC_DXT1_EXT;if(n===io)return s.COMPRESSED_RGBA_S3TC_DXT1_EXT;if(n===ro)return s.COMPRESSED_RGBA_S3TC_DXT3_EXT;if(n===so)return s.COMPRESSED_RGBA_S3TC_DXT5_EXT}else return null;if(n===Xl||n===Yl||n===ql||n===$l)if(s=e.get("WEBGL_compressed_texture_pvrtc"),s!==null){if(n===Xl)return s.COMPRESSED_RGB_PVRTC_4BPPV1_IMG;if(n===Yl)return s.COMPRESSED_RGB_PVRTC_2BPPV1_IMG;if(n===ql)return s.COMPRESSED_RGBA_PVRTC_4BPPV1_IMG;if(n===$l)return s.COMPRESSED_RGBA_PVRTC_2BPPV1_IMG}else return null;if(n===jl||n===Kl||n===Zl)if(s=e.get("WEBGL_compressed_texture_etc"),s!==null){if(n===jl||n===Kl)return a===Nt?s.COMPRESSED_SRGB8_ETC2:s.COMPRESSED_RGB8_ETC2;if(n===Zl)return a===Nt?s.COMPRESSED_SRGB8_ALPHA8_ETC2_EAC:s.COMPRESSED_RGBA8_ETC2_EAC}else return null;if(n===Jl||n===Ql||n===ec||n===tc||n===nc||n===ic||n===rc||n===sc||n===ac||n===oc||n===lc||n===cc||n===uc||n===hc)if(s=e.get("WEBGL_compressed_texture_astc"),s!==null){if(n===Jl)return a===Nt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_4x4_KHR:s.COMPRESSED_RGBA_ASTC_4x4_KHR;if(n===Ql)return a===Nt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_5x4_KHR:s.COMPRESSED_RGBA_ASTC_5x4_KHR;if(n===ec)return a===Nt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_5x5_KHR:s.COMPRESSED_RGBA_ASTC_5x5_KHR;if(n===tc)return a===Nt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_6x5_KHR:s.COMPRESSED_RGBA_ASTC_6x5_KHR;if(n===nc)return a===Nt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_6x6_KHR:s.COMPRESSED_RGBA_ASTC_6x6_KHR;if(n===ic)return a===Nt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_8x5_KHR:s.COMPRESSED_RGBA_ASTC_8x5_KHR;if(n===rc)return a===Nt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_8x6_KHR:s.COMPRESSED_RGBA_ASTC_8x6_KHR;if(n===sc)return a===Nt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_8x8_KHR:s.COMPRESSED_RGBA_ASTC_8x8_KHR;if(n===ac)return a===Nt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_10x5_KHR:s.COMPRESSED_RGBA_ASTC_10x5_KHR;if(n===oc)return a===Nt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_10x6_KHR:s.COMPRESSED_RGBA_ASTC_10x6_KHR;if(n===lc)return a===Nt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_10x8_KHR:s.COMPRESSED_RGBA_ASTC_10x8_KHR;if(n===cc)return a===Nt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_10x10_KHR:s.COMPRESSED_RGBA_ASTC_10x10_KHR;if(n===uc)return a===Nt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_12x10_KHR:s.COMPRESSED_RGBA_ASTC_12x10_KHR;if(n===hc)return a===Nt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_12x12_KHR:s.COMPRESSED_RGBA_ASTC_12x12_KHR}else return null;if(n===ao||n===dc||n===fc)if(s=e.get("EXT_texture_compression_bptc"),s!==null){if(n===ao)return a===Nt?s.COMPRESSED_SRGB_ALPHA_BPTC_UNORM_EXT:s.COMPRESSED_RGBA_BPTC_UNORM_EXT;if(n===dc)return s.COMPRESSED_RGB_BPTC_SIGNED_FLOAT_EXT;if(n===fc)return s.COMPRESSED_RGB_BPTC_UNSIGNED_FLOAT_EXT}else return null;if(n===Vd||n===pc||n===mc||n===gc)if(s=e.get("EXT_texture_compression_rgtc"),s!==null){if(n===ao)return s.COMPRESSED_RED_RGTC1_EXT;if(n===pc)return s.COMPRESSED_SIGNED_RED_RGTC1_EXT;if(n===mc)return s.COMPRESSED_RED_GREEN_RGTC2_EXT;if(n===gc)return s.COMPRESSED_SIGNED_RED_GREEN_RGTC2_EXT}else return null;return n===Ts?i.UNSIGNED_INT_24_8:i[n]!==void 0?i[n]:null}return{convert:t}}class Dx extends En{constructor(e=[]){super(),this.isArrayCamera=!0,this.cameras=e}}class Ga extends Kt{constructor(){super(),this.isGroup=!0,this.type="Group"}}const Ix={type:"move"};class wl{constructor(){this._targetRay=null,this._grip=null,this._hand=null}getHandSpace(){return this._hand===null&&(this._hand=new Ga,this._hand.matrixAutoUpdate=!1,this._hand.visible=!1,this._hand.joints={},this._hand.inputState={pinching:!1}),this._hand}getTargetRaySpace(){return this._targetRay===null&&(this._targetRay=new Ga,this._targetRay.matrixAutoUpdate=!1,this._targetRay.visible=!1,this._targetRay.hasLinearVelocity=!1,this._targetRay.linearVelocity=new V,this._targetRay.hasAngularVelocity=!1,this._targetRay.angularVelocity=new V),this._targetRay}getGripSpace(){return this._grip===null&&(this._grip=new Ga,this._grip.matrixAutoUpdate=!1,this._grip.visible=!1,this._grip.hasLinearVelocity=!1,this._grip.linearVelocity=new V,this._grip.hasAngularVelocity=!1,this._grip.angularVelocity=new V),this._grip}dispatchEvent(e){return this._targetRay!==null&&this._targetRay.dispatchEvent(e),this._grip!==null&&this._grip.dispatchEvent(e),this._hand!==null&&this._hand.dispatchEvent(e),this}connect(e){if(e&&e.hand){const t=this._hand;if(t)for(const n of e.hand.values())this._getHandJoint(t,n)}return this.dispatchEvent({type:"connected",data:e}),this}disconnect(e){return this.dispatchEvent({type:"disconnected",data:e}),this._targetRay!==null&&(this._targetRay.visible=!1),this._grip!==null&&(this._grip.visible=!1),this._hand!==null&&(this._hand.visible=!1),this}update(e,t,n){let r=null,s=null,a=null;const o=this._targetRay,l=this._grip,c=this._hand;if(e&&t.session.visibilityState!=="visible-blurred"){if(c&&e.hand){a=!0;for(const v of e.hand.values()){const p=t.getJointPose(v,n),f=this._getHandJoint(c,v);p!==null&&(f.matrix.fromArray(p.transform.matrix),f.matrix.decompose(f.position,f.rotation,f.scale),f.matrixWorldNeedsUpdate=!0,f.jointRadius=p.radius),f.visible=p!==null}const u=c.joints["index-finger-tip"],h=c.joints["thumb-tip"],d=u.position.distanceTo(h.position),m=.02,_=.005;c.inputState.pinching&&d>m+_?(c.inputState.pinching=!1,this.dispatchEvent({type:"pinchend",handedness:e.handedness,target:this})):!c.inputState.pinching&&d<=m-_&&(c.inputState.pinching=!0,this.dispatchEvent({type:"pinchstart",handedness:e.handedness,target:this}))}else l!==null&&e.gripSpace&&(s=t.getPose(e.gripSpace,n),s!==null&&(l.matrix.fromArray(s.transform.matrix),l.matrix.decompose(l.position,l.rotation,l.scale),l.matrixWorldNeedsUpdate=!0,s.linearVelocity?(l.hasLinearVelocity=!0,l.linearVelocity.copy(s.linearVelocity)):l.hasLinearVelocity=!1,s.angularVelocity?(l.hasAngularVelocity=!0,l.angularVelocity.copy(s.angularVelocity)):l.hasAngularVelocity=!1));o!==null&&(r=t.getPose(e.targetRaySpace,n),r===null&&s!==null&&(r=s),r!==null&&(o.matrix.fromArray(r.transform.matrix),o.matrix.decompose(o.position,o.rotation,o.scale),o.matrixWorldNeedsUpdate=!0,r.linearVelocity?(o.hasLinearVelocity=!0,o.linearVelocity.copy(r.linearVelocity)):o.hasLinearVelocity=!1,r.angularVelocity?(o.hasAngularVelocity=!0,o.angularVelocity.copy(r.angularVelocity)):o.hasAngularVelocity=!1,this.dispatchEvent(Ix)))}return o!==null&&(o.visible=r!==null),l!==null&&(l.visible=s!==null),c!==null&&(c.visible=a!==null),this}_getHandJoint(e,t){if(e.joints[t.jointName]===void 0){const n=new Ga;n.matrixAutoUpdate=!1,n.visible=!1,e.joints[t.jointName]=n,e.add(n)}return e.joints[t.jointName]}}const Ux=`
void main() {

	gl_Position = vec4( position, 1.0 );

}`,Nx=`
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

}`;class Fx{constructor(){this.texture=null,this.mesh=null,this.depthNear=0,this.depthFar=0}init(e,t,n){if(this.texture===null){const r=new Tn,s=e.properties.get(r);s.__webglTexture=t.texture,(t.depthNear!=n.depthNear||t.depthFar!=n.depthFar)&&(this.depthNear=t.depthNear,this.depthFar=t.depthFar),this.texture=r}}getMesh(e){if(this.texture!==null&&this.mesh===null){const t=e.cameras[0].viewport,n=new tr({vertexShader:Ux,fragmentShader:Nx,uniforms:{depthColor:{value:this.texture},depthWidth:{value:t.z},depthHeight:{value:t.w}}});this.mesh=new Rn(new Lo(20,20),n)}return this.mesh}reset(){this.texture=null,this.mesh=null}getDepthTexture(){return this.texture}}class Ox extends Ds{constructor(e,t){super();const n=this;let r=null,s=1,a=null,o="local-floor",l=1,c=null,u=null,h=null,d=null,m=null,_=null;const v=new Fx,p=t.getContextAttributes();let f=null,E=null;const y=[],T=[],z=new Xe;let C=null;const D=new En;D.layers.enable(1),D.viewport=new jt;const B=new En;B.layers.enable(2),B.viewport=new jt;const w=[D,B],x=new Dx;x.layers.enable(1),x.layers.enable(2);let R=null,j=null;this.cameraAutoUpdate=!0,this.enabled=!1,this.isPresenting=!1,this.getController=function(te){let le=y[te];return le===void 0&&(le=new wl,y[te]=le),le.getTargetRaySpace()},this.getControllerGrip=function(te){let le=y[te];return le===void 0&&(le=new wl,y[te]=le),le.getGripSpace()},this.getHand=function(te){let le=y[te];return le===void 0&&(le=new wl,y[te]=le),le.getHandSpace()};function O(te){const le=T.indexOf(te.inputSource);if(le===-1)return;const xe=y[le];xe!==void 0&&(xe.update(te.inputSource,te.frame,c||a),xe.dispatchEvent({type:te.type,data:te.inputSource}))}function K(){r.removeEventListener("select",O),r.removeEventListener("selectstart",O),r.removeEventListener("selectend",O),r.removeEventListener("squeeze",O),r.removeEventListener("squeezestart",O),r.removeEventListener("squeezeend",O),r.removeEventListener("end",K),r.removeEventListener("inputsourceschange",W);for(let te=0;te<y.length;te++){const le=T[te];le!==null&&(T[te]=null,y[te].disconnect(le))}R=null,j=null,v.reset(),e.setRenderTarget(f),m=null,d=null,h=null,r=null,E=null,ve.stop(),n.isPresenting=!1,e.setPixelRatio(C),e.setSize(z.width,z.height,!1),n.dispatchEvent({type:"sessionend"})}this.setFramebufferScaleFactor=function(te){s=te,n.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change framebuffer scale while presenting.")},this.setReferenceSpaceType=function(te){o=te,n.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change reference space type while presenting.")},this.getReferenceSpace=function(){return c||a},this.setReferenceSpace=function(te){c=te},this.getBaseLayer=function(){return d!==null?d:m},this.getBinding=function(){return h},this.getFrame=function(){return _},this.getSession=function(){return r},this.setSession=async function(te){if(r=te,r!==null){if(f=e.getRenderTarget(),r.addEventListener("select",O),r.addEventListener("selectstart",O),r.addEventListener("selectend",O),r.addEventListener("squeeze",O),r.addEventListener("squeezestart",O),r.addEventListener("squeezeend",O),r.addEventListener("end",K),r.addEventListener("inputsourceschange",W),p.xrCompatible!==!0&&await t.makeXRCompatible(),C=e.getPixelRatio(),e.getSize(z),r.renderState.layers===void 0){const le={antialias:p.antialias,alpha:!0,depth:p.depth,stencil:p.stencil,framebufferScaleFactor:s};m=new XRWebGLLayer(r,t,le),r.updateRenderState({baseLayer:m}),e.setPixelRatio(1),e.setSize(m.framebufferWidth,m.framebufferHeight,!1),E=new Ar(m.framebufferWidth,m.framebufferHeight,{format:ri,type:Ui,colorSpace:e.outputColorSpace,stencilBuffer:p.stencil})}else{let le=null,xe=null,he=null;p.depth&&(he=p.stencil?t.DEPTH24_STENCIL8:t.DEPTH_COMPONENT24,le=p.stencil?ws:_s,xe=p.stencil?Ts:wr);const Be={colorFormat:t.RGBA8,depthFormat:he,scaleFactor:s};h=new XRWebGLBinding(r,t),d=h.createProjectionLayer(Be),r.updateRenderState({layers:[d]}),e.setPixelRatio(1),e.setSize(d.textureWidth,d.textureHeight,!1),E=new Ar(d.textureWidth,d.textureHeight,{format:ri,type:Ui,depthTexture:new ef(d.textureWidth,d.textureHeight,xe,void 0,void 0,void 0,void 0,void 0,void 0,le),stencilBuffer:p.stencil,colorSpace:e.outputColorSpace,samples:p.antialias?4:0,resolveDepthBuffer:d.ignoreDepthValues===!1})}E.isXRRenderTarget=!0,this.setFoveation(l),c=null,a=await r.requestReferenceSpace(o),ve.setContext(r),ve.start(),n.isPresenting=!0,n.dispatchEvent({type:"sessionstart"})}},this.getEnvironmentBlendMode=function(){if(r!==null)return r.environmentBlendMode},this.getDepthTexture=function(){return v.getDepthTexture()};function W(te){for(let le=0;le<te.removed.length;le++){const xe=te.removed[le],he=T.indexOf(xe);he>=0&&(T[he]=null,y[he].disconnect(xe))}for(let le=0;le<te.added.length;le++){const xe=te.added[le];let he=T.indexOf(xe);if(he===-1){for(let Ve=0;Ve<y.length;Ve++)if(Ve>=T.length){T.push(xe),he=Ve;break}else if(T[Ve]===null){T[Ve]=xe,he=Ve;break}if(he===-1)break}const Be=y[he];Be&&Be.connect(xe)}}const J=new V,Y=new V;function ee(te,le,xe){J.setFromMatrixPosition(le.matrixWorld),Y.setFromMatrixPosition(xe.matrixWorld);const he=J.distanceTo(Y),Be=le.projectionMatrix.elements,Ve=xe.projectionMatrix.elements,Ne=Be[14]/(Be[10]-1),dt=Be[14]/(Be[10]+1),U=(Be[9]+1)/Be[5],ut=(Be[9]-1)/Be[5],tt=(Be[8]-1)/Be[0],ot=(Ve[8]+1)/Ve[0],Fe=Ne*tt,yt=Ne*ot,Ye=he/(-tt+ot),We=Ye*-tt;if(le.matrixWorld.decompose(te.position,te.quaternion,te.scale),te.translateX(We),te.translateZ(Ye),te.matrixWorld.compose(te.position,te.quaternion,te.scale),te.matrixWorldInverse.copy(te.matrixWorld).invert(),Be[10]===-1)te.projectionMatrix.copy(le.projectionMatrix),te.projectionMatrixInverse.copy(le.projectionMatrixInverse);else{const L=Ne+Ye,S=dt+Ye,Z=Fe-We,ae=yt+(he-We),Q=U*dt/S*L,G=ut*dt/S*L;te.projectionMatrix.makePerspective(Z,ae,Q,G,L,S),te.projectionMatrixInverse.copy(te.projectionMatrix).invert()}}function pe(te,le){le===null?te.matrixWorld.copy(te.matrix):te.matrixWorld.multiplyMatrices(le.matrixWorld,te.matrix),te.matrixWorldInverse.copy(te.matrixWorld).invert()}this.updateCamera=function(te){if(r===null)return;let le=te.near,xe=te.far;v.texture!==null&&(v.depthNear>0&&(le=v.depthNear),v.depthFar>0&&(xe=v.depthFar)),x.near=B.near=D.near=le,x.far=B.far=D.far=xe,(R!==x.near||j!==x.far)&&(r.updateRenderState({depthNear:x.near,depthFar:x.far}),R=x.near,j=x.far);const he=te.parent,Be=x.cameras;pe(x,he);for(let Ve=0;Ve<Be.length;Ve++)pe(Be[Ve],he);Be.length===2?ee(x,D,B):x.projectionMatrix.copy(D.projectionMatrix),ue(te,x,he)};function ue(te,le,xe){xe===null?te.matrix.copy(le.matrixWorld):(te.matrix.copy(xe.matrixWorld),te.matrix.invert(),te.matrix.multiply(le.matrixWorld)),te.matrix.decompose(te.position,te.quaternion,te.scale),te.updateMatrixWorld(!0),te.projectionMatrix.copy(le.projectionMatrix),te.projectionMatrixInverse.copy(le.projectionMatrixInverse),te.isPerspectiveCamera&&(te.fov=ca*2*Math.atan(1/te.projectionMatrix.elements[5]),te.zoom=1)}this.getCamera=function(){return x},this.getFoveation=function(){if(!(d===null&&m===null))return l},this.setFoveation=function(te){l=te,d!==null&&(d.fixedFoveation=te),m!==null&&m.fixedFoveation!==void 0&&(m.fixedFoveation=te)},this.hasDepthSensing=function(){return v.texture!==null},this.getDepthSensingMesh=function(){return v.getMesh(x)};let _e=null;function be(te,le){if(u=le.getViewerPose(c||a),_=le,u!==null){const xe=u.views;m!==null&&(e.setRenderTargetFramebuffer(E,m.framebuffer),e.setRenderTarget(E));let he=!1;xe.length!==x.cameras.length&&(x.cameras.length=0,he=!0);for(let Ve=0;Ve<xe.length;Ve++){const Ne=xe[Ve];let dt=null;if(m!==null)dt=m.getViewport(Ne);else{const ut=h.getViewSubImage(d,Ne);dt=ut.viewport,Ve===0&&(e.setRenderTargetTextures(E,ut.colorTexture,d.ignoreDepthValues?void 0:ut.depthStencilTexture),e.setRenderTarget(E))}let U=w[Ve];U===void 0&&(U=new En,U.layers.enable(Ve),U.viewport=new jt,w[Ve]=U),U.matrix.fromArray(Ne.transform.matrix),U.matrix.decompose(U.position,U.quaternion,U.scale),U.projectionMatrix.fromArray(Ne.projectionMatrix),U.projectionMatrixInverse.copy(U.projectionMatrix).invert(),U.viewport.set(dt.x,dt.y,dt.width,dt.height),Ve===0&&(x.matrix.copy(U.matrix),x.matrix.decompose(x.position,x.quaternion,x.scale)),he===!0&&x.cameras.push(U)}const Be=r.enabledFeatures;if(Be&&Be.includes("depth-sensing")){const Ve=h.getDepthInformation(xe[0]);Ve&&Ve.isValid&&Ve.texture&&v.init(e,Ve,r.renderState)}}for(let xe=0;xe<y.length;xe++){const he=T[xe],Be=y[xe];he!==null&&Be!==void 0&&Be.update(he,le,c||a)}_e&&_e(te,le),le.detectedPlanes&&n.dispatchEvent({type:"planesdetected",data:le}),_=null}const ve=new Qd;ve.setAnimationLoop(be),this.setAnimationLoop=function(te){_e=te},this.dispose=function(){}}}const mr=new gi,Bx=new zt;function zx(i,e){function t(p,f){p.matrixAutoUpdate===!0&&p.updateMatrix(),f.value.copy(p.matrix)}function n(p,f){f.color.getRGB(p.fogColor.value,Zd(i)),f.isFog?(p.fogNear.value=f.near,p.fogFar.value=f.far):f.isFogExp2&&(p.fogDensity.value=f.density)}function r(p,f,E,y,T){f.isMeshBasicMaterial||f.isMeshLambertMaterial?s(p,f):f.isMeshToonMaterial?(s(p,f),h(p,f)):f.isMeshPhongMaterial?(s(p,f),u(p,f)):f.isMeshStandardMaterial?(s(p,f),d(p,f),f.isMeshPhysicalMaterial&&m(p,f,T)):f.isMeshMatcapMaterial?(s(p,f),_(p,f)):f.isMeshDepthMaterial?s(p,f):f.isMeshDistanceMaterial?(s(p,f),v(p,f)):f.isMeshNormalMaterial?s(p,f):f.isLineBasicMaterial?(a(p,f),f.isLineDashedMaterial&&o(p,f)):f.isPointsMaterial?l(p,f,E,y):f.isSpriteMaterial?c(p,f):f.isShadowMaterial?(p.color.value.copy(f.color),p.opacity.value=f.opacity):f.isShaderMaterial&&(f.uniformsNeedUpdate=!1)}function s(p,f){p.opacity.value=f.opacity,f.color&&p.diffuse.value.copy(f.color),f.emissive&&p.emissive.value.copy(f.emissive).multiplyScalar(f.emissiveIntensity),f.map&&(p.map.value=f.map,t(f.map,p.mapTransform)),f.alphaMap&&(p.alphaMap.value=f.alphaMap,t(f.alphaMap,p.alphaMapTransform)),f.bumpMap&&(p.bumpMap.value=f.bumpMap,t(f.bumpMap,p.bumpMapTransform),p.bumpScale.value=f.bumpScale,f.side===Cn&&(p.bumpScale.value*=-1)),f.normalMap&&(p.normalMap.value=f.normalMap,t(f.normalMap,p.normalMapTransform),p.normalScale.value.copy(f.normalScale),f.side===Cn&&p.normalScale.value.negate()),f.displacementMap&&(p.displacementMap.value=f.displacementMap,t(f.displacementMap,p.displacementMapTransform),p.displacementScale.value=f.displacementScale,p.displacementBias.value=f.displacementBias),f.emissiveMap&&(p.emissiveMap.value=f.emissiveMap,t(f.emissiveMap,p.emissiveMapTransform)),f.specularMap&&(p.specularMap.value=f.specularMap,t(f.specularMap,p.specularMapTransform)),f.alphaTest>0&&(p.alphaTest.value=f.alphaTest);const E=e.get(f),y=E.envMap,T=E.envMapRotation;y&&(p.envMap.value=y,mr.copy(T),mr.x*=-1,mr.y*=-1,mr.z*=-1,y.isCubeTexture&&y.isRenderTargetTexture===!1&&(mr.y*=-1,mr.z*=-1),p.envMapRotation.value.setFromMatrix4(Bx.makeRotationFromEuler(mr)),p.flipEnvMap.value=y.isCubeTexture&&y.isRenderTargetTexture===!1?-1:1,p.reflectivity.value=f.reflectivity,p.ior.value=f.ior,p.refractionRatio.value=f.refractionRatio),f.lightMap&&(p.lightMap.value=f.lightMap,p.lightMapIntensity.value=f.lightMapIntensity,t(f.lightMap,p.lightMapTransform)),f.aoMap&&(p.aoMap.value=f.aoMap,p.aoMapIntensity.value=f.aoMapIntensity,t(f.aoMap,p.aoMapTransform))}function a(p,f){p.diffuse.value.copy(f.color),p.opacity.value=f.opacity,f.map&&(p.map.value=f.map,t(f.map,p.mapTransform))}function o(p,f){p.dashSize.value=f.dashSize,p.totalSize.value=f.dashSize+f.gapSize,p.scale.value=f.scale}function l(p,f,E,y){p.diffuse.value.copy(f.color),p.opacity.value=f.opacity,p.size.value=f.size*E,p.scale.value=y*.5,f.map&&(p.map.value=f.map,t(f.map,p.uvTransform)),f.alphaMap&&(p.alphaMap.value=f.alphaMap,t(f.alphaMap,p.alphaMapTransform)),f.alphaTest>0&&(p.alphaTest.value=f.alphaTest)}function c(p,f){p.diffuse.value.copy(f.color),p.opacity.value=f.opacity,p.rotation.value=f.rotation,f.map&&(p.map.value=f.map,t(f.map,p.mapTransform)),f.alphaMap&&(p.alphaMap.value=f.alphaMap,t(f.alphaMap,p.alphaMapTransform)),f.alphaTest>0&&(p.alphaTest.value=f.alphaTest)}function u(p,f){p.specular.value.copy(f.specular),p.shininess.value=Math.max(f.shininess,1e-4)}function h(p,f){f.gradientMap&&(p.gradientMap.value=f.gradientMap)}function d(p,f){p.metalness.value=f.metalness,f.metalnessMap&&(p.metalnessMap.value=f.metalnessMap,t(f.metalnessMap,p.metalnessMapTransform)),p.roughness.value=f.roughness,f.roughnessMap&&(p.roughnessMap.value=f.roughnessMap,t(f.roughnessMap,p.roughnessMapTransform)),f.envMap&&(p.envMapIntensity.value=f.envMapIntensity)}function m(p,f,E){p.ior.value=f.ior,f.sheen>0&&(p.sheenColor.value.copy(f.sheenColor).multiplyScalar(f.sheen),p.sheenRoughness.value=f.sheenRoughness,f.sheenColorMap&&(p.sheenColorMap.value=f.sheenColorMap,t(f.sheenColorMap,p.sheenColorMapTransform)),f.sheenRoughnessMap&&(p.sheenRoughnessMap.value=f.sheenRoughnessMap,t(f.sheenRoughnessMap,p.sheenRoughnessMapTransform))),f.clearcoat>0&&(p.clearcoat.value=f.clearcoat,p.clearcoatRoughness.value=f.clearcoatRoughness,f.clearcoatMap&&(p.clearcoatMap.value=f.clearcoatMap,t(f.clearcoatMap,p.clearcoatMapTransform)),f.clearcoatRoughnessMap&&(p.clearcoatRoughnessMap.value=f.clearcoatRoughnessMap,t(f.clearcoatRoughnessMap,p.clearcoatRoughnessMapTransform)),f.clearcoatNormalMap&&(p.clearcoatNormalMap.value=f.clearcoatNormalMap,t(f.clearcoatNormalMap,p.clearcoatNormalMapTransform),p.clearcoatNormalScale.value.copy(f.clearcoatNormalScale),f.side===Cn&&p.clearcoatNormalScale.value.negate())),f.dispersion>0&&(p.dispersion.value=f.dispersion),f.iridescence>0&&(p.iridescence.value=f.iridescence,p.iridescenceIOR.value=f.iridescenceIOR,p.iridescenceThicknessMinimum.value=f.iridescenceThicknessRange[0],p.iridescenceThicknessMaximum.value=f.iridescenceThicknessRange[1],f.iridescenceMap&&(p.iridescenceMap.value=f.iridescenceMap,t(f.iridescenceMap,p.iridescenceMapTransform)),f.iridescenceThicknessMap&&(p.iridescenceThicknessMap.value=f.iridescenceThicknessMap,t(f.iridescenceThicknessMap,p.iridescenceThicknessMapTransform))),f.transmission>0&&(p.transmission.value=f.transmission,p.transmissionSamplerMap.value=E.texture,p.transmissionSamplerSize.value.set(E.width,E.height),f.transmissionMap&&(p.transmissionMap.value=f.transmissionMap,t(f.transmissionMap,p.transmissionMapTransform)),p.thickness.value=f.thickness,f.thicknessMap&&(p.thicknessMap.value=f.thicknessMap,t(f.thicknessMap,p.thicknessMapTransform)),p.attenuationDistance.value=f.attenuationDistance,p.attenuationColor.value.copy(f.attenuationColor)),f.anisotropy>0&&(p.anisotropyVector.value.set(f.anisotropy*Math.cos(f.anisotropyRotation),f.anisotropy*Math.sin(f.anisotropyRotation)),f.anisotropyMap&&(p.anisotropyMap.value=f.anisotropyMap,t(f.anisotropyMap,p.anisotropyMapTransform))),p.specularIntensity.value=f.specularIntensity,p.specularColor.value.copy(f.specularColor),f.specularColorMap&&(p.specularColorMap.value=f.specularColorMap,t(f.specularColorMap,p.specularColorMapTransform)),f.specularIntensityMap&&(p.specularIntensityMap.value=f.specularIntensityMap,t(f.specularIntensityMap,p.specularIntensityMapTransform))}function _(p,f){f.matcap&&(p.matcap.value=f.matcap)}function v(p,f){const E=e.get(f).light;p.referencePosition.value.setFromMatrixPosition(E.matrixWorld),p.nearDistance.value=E.shadow.camera.near,p.farDistance.value=E.shadow.camera.far}return{refreshFogUniforms:n,refreshMaterialUniforms:r}}function kx(i,e,t,n){let r={},s={},a=[];const o=i.getParameter(i.MAX_UNIFORM_BUFFER_BINDINGS);function l(E,y){const T=y.program;n.uniformBlockBinding(E,T)}function c(E,y){let T=r[E.id];T===void 0&&(_(E),T=u(E),r[E.id]=T,E.addEventListener("dispose",p));const z=y.program;n.updateUBOMapping(E,z);const C=e.render.frame;s[E.id]!==C&&(d(E),s[E.id]=C)}function u(E){const y=h();E.__bindingPointIndex=y;const T=i.createBuffer(),z=E.__size,C=E.usage;return i.bindBuffer(i.UNIFORM_BUFFER,T),i.bufferData(i.UNIFORM_BUFFER,z,C),i.bindBuffer(i.UNIFORM_BUFFER,null),i.bindBufferBase(i.UNIFORM_BUFFER,y,T),T}function h(){for(let E=0;E<o;E++)if(a.indexOf(E)===-1)return a.push(E),E;return console.error("THREE.WebGLRenderer: Maximum number of simultaneously usable uniforms groups reached."),0}function d(E){const y=r[E.id],T=E.uniforms,z=E.__cache;i.bindBuffer(i.UNIFORM_BUFFER,y);for(let C=0,D=T.length;C<D;C++){const B=Array.isArray(T[C])?T[C]:[T[C]];for(let w=0,x=B.length;w<x;w++){const R=B[w];if(m(R,C,w,z)===!0){const j=R.__offset,O=Array.isArray(R.value)?R.value:[R.value];let K=0;for(let W=0;W<O.length;W++){const J=O[W],Y=v(J);typeof J=="number"||typeof J=="boolean"?(R.__data[0]=J,i.bufferSubData(i.UNIFORM_BUFFER,j+K,R.__data)):J.isMatrix3?(R.__data[0]=J.elements[0],R.__data[1]=J.elements[1],R.__data[2]=J.elements[2],R.__data[3]=0,R.__data[4]=J.elements[3],R.__data[5]=J.elements[4],R.__data[6]=J.elements[5],R.__data[7]=0,R.__data[8]=J.elements[6],R.__data[9]=J.elements[7],R.__data[10]=J.elements[8],R.__data[11]=0):(J.toArray(R.__data,K),K+=Y.storage/Float32Array.BYTES_PER_ELEMENT)}i.bufferSubData(i.UNIFORM_BUFFER,j,R.__data)}}}i.bindBuffer(i.UNIFORM_BUFFER,null)}function m(E,y,T,z){const C=E.value,D=y+"_"+T;if(z[D]===void 0)return typeof C=="number"||typeof C=="boolean"?z[D]=C:z[D]=C.clone(),!0;{const B=z[D];if(typeof C=="number"||typeof C=="boolean"){if(B!==C)return z[D]=C,!0}else if(B.equals(C)===!1)return B.copy(C),!0}return!1}function _(E){const y=E.uniforms;let T=0;const z=16;for(let D=0,B=y.length;D<B;D++){const w=Array.isArray(y[D])?y[D]:[y[D]];for(let x=0,R=w.length;x<R;x++){const j=w[x],O=Array.isArray(j.value)?j.value:[j.value];for(let K=0,W=O.length;K<W;K++){const J=O[K],Y=v(J),ee=T%z,pe=ee%Y.boundary,ue=ee+pe;T+=pe,ue!==0&&z-ue<Y.storage&&(T+=z-ue),j.__data=new Float32Array(Y.storage/Float32Array.BYTES_PER_ELEMENT),j.__offset=T,T+=Y.storage}}}const C=T%z;return C>0&&(T+=z-C),E.__size=T,E.__cache={},this}function v(E){const y={boundary:0,storage:0};return typeof E=="number"||typeof E=="boolean"?(y.boundary=4,y.storage=4):E.isVector2?(y.boundary=8,y.storage=8):E.isVector3||E.isColor?(y.boundary=16,y.storage=12):E.isVector4?(y.boundary=16,y.storage=16):E.isMatrix3?(y.boundary=48,y.storage=48):E.isMatrix4?(y.boundary=64,y.storage=64):E.isTexture?console.warn("THREE.WebGLRenderer: Texture samplers can not be part of an uniforms group."):console.warn("THREE.WebGLRenderer: Unsupported uniform value type.",E),y}function p(E){const y=E.target;y.removeEventListener("dispose",p);const T=a.indexOf(y.__bindingPointIndex);a.splice(T,1),i.deleteBuffer(r[y.id]),delete r[y.id],delete s[y.id]}function f(){for(const E in r)i.deleteBuffer(r[E]);a=[],r={},s={}}return{bind:l,update:c,dispose:f}}class af{constructor(e={}){const{canvas:t=Lm(),context:n=null,depth:r=!0,stencil:s=!1,alpha:a=!1,antialias:o=!1,premultipliedAlpha:l=!0,preserveDrawingBuffer:c=!1,powerPreference:u="default",failIfMajorPerformanceCaveat:h=!1}=e;this.isWebGLRenderer=!0;let d;if(n!==null){if(typeof WebGLRenderingContext<"u"&&n instanceof WebGLRenderingContext)throw new Error("THREE.WebGLRenderer: WebGL 1 is not supported since r163.");d=n.getContextAttributes().alpha}else d=a;const m=new Uint32Array(4),_=new Int32Array(4);let v=null,p=null;const f=[],E=[];this.domElement=t,this.debug={checkShaderErrors:!0,onShaderError:null},this.autoClear=!0,this.autoClearColor=!0,this.autoClearDepth=!0,this.autoClearStencil=!0,this.sortObjects=!0,this.clippingPlanes=[],this.localClippingEnabled=!1,this._outputColorSpace=fi,this.toneMapping=Ji,this.toneMappingExposure=1;const y=this;let T=!1,z=0,C=0,D=null,B=-1,w=null;const x=new jt,R=new jt;let j=null;const O=new nt(0);let K=0,W=t.width,J=t.height,Y=1,ee=null,pe=null;const ue=new jt(0,0,W,J),_e=new jt(0,0,W,J);let be=!1;const ve=new Hc;let te=!1,le=!1;const xe=new zt,he=new V,Be=new jt,Ve={background:null,fog:null,environment:null,overrideMaterial:null,isScene:!0};let Ne=!1;function dt(){return D===null?Y:1}let U=n;function ut(b,H){return t.getContext(b,H)}try{const b={alpha:!0,depth:r,stencil:s,antialias:o,premultipliedAlpha:l,preserveDrawingBuffer:c,powerPreference:u,failIfMajorPerformanceCaveat:h};if("setAttribute"in t&&t.setAttribute("data-engine",`three.js r${Pc}`),t.addEventListener("webglcontextlost",ne,!1),t.addEventListener("webglcontextrestored",ie,!1),t.addEventListener("webglcontextcreationerror",ge,!1),U===null){const H="webgl2";if(U=ut(H,b),U===null)throw ut(H)?new Error("Error creating WebGL context with your selected attributes."):new Error("Error creating WebGL context.")}}catch(b){throw console.error("THREE.WebGLRenderer: "+b.message),b}let tt,ot,Fe,yt,Ye,We,L,S,Z,ae,Q,G,Ee,me,we,je,fe,Te,Ke,ze,Se,ke,N,oe;function I(){tt=new q0(U),tt.init(),ke=new Lx(U,tt),ot=new H0(U,tt,e,ke),Fe=new Rx(U),yt=new K0(U),Ye=new px,We=new Px(U,tt,Fe,Ye,ot,ke,yt),L=new G0(y),S=new Y0(y),Z=new ig(U),N=new z0(U,Z),ae=new $0(U,Z,yt,N),Q=new J0(U,ae,Z,yt),Ke=new Z0(U,ot,We),je=new V0(Ye),G=new fx(y,L,S,tt,ot,N,je),Ee=new zx(y,Ye),me=new gx,we=new yx(tt),Te=new B0(y,L,S,Fe,Q,d,l),fe=new Ax(y,Q,ot),oe=new kx(U,yt,ot,Fe),ze=new k0(U,tt,yt),Se=new j0(U,tt,yt),yt.programs=G.programs,y.capabilities=ot,y.extensions=tt,y.properties=Ye,y.renderLists=me,y.shadowMap=fe,y.state=Fe,y.info=yt}I();const re=new Ox(y,U);this.xr=re,this.getContext=function(){return U},this.getContextAttributes=function(){return U.getContextAttributes()},this.forceContextLoss=function(){const b=tt.get("WEBGL_lose_context");b&&b.loseContext()},this.forceContextRestore=function(){const b=tt.get("WEBGL_lose_context");b&&b.restoreContext()},this.getPixelRatio=function(){return Y},this.setPixelRatio=function(b){b!==void 0&&(Y=b,this.setSize(W,J,!1))},this.getSize=function(b){return b.set(W,J)},this.setSize=function(b,H,$=!0){if(re.isPresenting){console.warn("THREE.WebGLRenderer: Can't change size while VR device is presenting.");return}W=b,J=H,t.width=Math.floor(b*Y),t.height=Math.floor(H*Y),$===!0&&(t.style.width=b+"px",t.style.height=H+"px"),this.setViewport(0,0,b,H)},this.getDrawingBufferSize=function(b){return b.set(W*Y,J*Y).floor()},this.setDrawingBufferSize=function(b,H,$){W=b,J=H,Y=$,t.width=Math.floor(b*$),t.height=Math.floor(H*$),this.setViewport(0,0,b,H)},this.getCurrentViewport=function(b){return b.copy(x)},this.getViewport=function(b){return b.copy(ue)},this.setViewport=function(b,H,$,X){b.isVector4?ue.set(b.x,b.y,b.z,b.w):ue.set(b,H,$,X),Fe.viewport(x.copy(ue).multiplyScalar(Y).round())},this.getScissor=function(b){return b.copy(_e)},this.setScissor=function(b,H,$,X){b.isVector4?_e.set(b.x,b.y,b.z,b.w):_e.set(b,H,$,X),Fe.scissor(R.copy(_e).multiplyScalar(Y).round())},this.getScissorTest=function(){return be},this.setScissorTest=function(b){Fe.setScissorTest(be=b)},this.setOpaqueSort=function(b){ee=b},this.setTransparentSort=function(b){pe=b},this.getClearColor=function(b){return b.copy(Te.getClearColor())},this.setClearColor=function(){Te.setClearColor.apply(Te,arguments)},this.getClearAlpha=function(){return Te.getClearAlpha()},this.setClearAlpha=function(){Te.setClearAlpha.apply(Te,arguments)},this.clear=function(b=!0,H=!0,$=!0){let X=0;if(b){let k=!1;if(D!==null){const ce=D.texture.format;k=ce===Fc||ce===Nc||ce===Uc}if(k){const ce=D.texture.type,Re=ce===Ui||ce===wr||ce===la||ce===Ts||ce===Dc||ce===Ic,Ce=Te.getClearColor(),De=Te.getClearAlpha(),Ze=Ce.r,Je=Ce.g,Oe=Ce.b;Re?(m[0]=Ze,m[1]=Je,m[2]=Oe,m[3]=De,U.clearBufferuiv(U.COLOR,0,m)):(_[0]=Ze,_[1]=Je,_[2]=Oe,_[3]=De,U.clearBufferiv(U.COLOR,0,_))}else X|=U.COLOR_BUFFER_BIT}H&&(X|=U.DEPTH_BUFFER_BIT),$&&(X|=U.STENCIL_BUFFER_BIT,this.state.buffers.stencil.setMask(4294967295)),U.clear(X)},this.clearColor=function(){this.clear(!0,!1,!1)},this.clearDepth=function(){this.clear(!1,!0,!1)},this.clearStencil=function(){this.clear(!1,!1,!0)},this.dispose=function(){t.removeEventListener("webglcontextlost",ne,!1),t.removeEventListener("webglcontextrestored",ie,!1),t.removeEventListener("webglcontextcreationerror",ge,!1),me.dispose(),we.dispose(),Ye.dispose(),L.dispose(),S.dispose(),Q.dispose(),N.dispose(),oe.dispose(),G.dispose(),re.dispose(),re.removeEventListener("sessionstart",Ft),re.removeEventListener("sessionend",Ot),en.stop()};function ne(b){b.preventDefault(),console.log("THREE.WebGLRenderer: Context Lost."),T=!0}function ie(){console.log("THREE.WebGLRenderer: Context Restored."),T=!1;const b=yt.autoReset,H=fe.enabled,$=fe.autoUpdate,X=fe.needsUpdate,k=fe.type;I(),yt.autoReset=b,fe.enabled=H,fe.autoUpdate=$,fe.needsUpdate=X,fe.type=k}function ge(b){console.error("THREE.WebGLRenderer: A WebGL context could not be created. Reason: ",b.statusMessage)}function $e(b){const H=b.target;H.removeEventListener("dispose",$e),st(H)}function st(b){mt(b),Ye.remove(b)}function mt(b){const H=Ye.get(b).programs;H!==void 0&&(H.forEach(function($){G.releaseProgram($)}),b.isShaderMaterial&&G.releaseShaderCache(b))}this.renderBufferDirect=function(b,H,$,X,k,ce){H===null&&(H=Ve);const Re=k.isMesh&&k.matrixWorld.determinant()<0,Ce=Ho(b,H,$,X,k);Fe.setMaterial(X,Re);let De=$.index,Ze=1;if(X.wireframe===!0){if(De=ae.getWireframeAttribute($),De===void 0)return;Ze=2}const Je=$.drawRange,Oe=$.attributes.position;let lt=Je.start*Ze,Rt=(Je.start+Je.count)*Ze;ce!==null&&(lt=Math.max(lt,ce.start*Ze),Rt=Math.min(Rt,(ce.start+ce.count)*Ze)),De!==null?(lt=Math.max(lt,0),Rt=Math.min(Rt,De.count)):Oe!=null&&(lt=Math.max(lt,0),Rt=Math.min(Rt,Oe.count));const Ct=Rt-lt;if(Ct<0||Ct===1/0)return;N.setup(k,X,Ce,$,De);let cn,ft=ze;if(De!==null&&(cn=Z.get(De),ft=Se,ft.setIndex(cn)),k.isMesh)X.wireframe===!0?(Fe.setLineWidth(X.wireframeLinewidth*dt()),ft.setMode(U.LINES)):ft.setMode(U.TRIANGLES);else if(k.isLine){let He=X.linewidth;He===void 0&&(He=1),Fe.setLineWidth(He*dt()),k.isLineSegments?ft.setMode(U.LINES):k.isLineLoop?ft.setMode(U.LINE_LOOP):ft.setMode(U.LINE_STRIP)}else k.isPoints?ft.setMode(U.POINTS):k.isSprite&&ft.setMode(U.TRIANGLES);if(k.isBatchedMesh)if(k._multiDrawInstances!==null)ft.renderMultiDrawInstances(k._multiDrawStarts,k._multiDrawCounts,k._multiDrawCount,k._multiDrawInstances);else if(tt.get("WEBGL_multi_draw"))ft.renderMultiDraw(k._multiDrawStarts,k._multiDrawCounts,k._multiDrawCount);else{const He=k._multiDrawStarts,Gt=k._multiDrawCounts,pt=k._multiDrawCount,Pt=De?Z.get(De).bytesPerElement:1,Mi=Ye.get(X).currentProgram.getUniforms();for(let hn=0;hn<pt;hn++)Mi.setValue(U,"_gl_DrawID",hn),ft.render(He[hn]/Pt,Gt[hn])}else if(k.isInstancedMesh)ft.renderInstances(lt,Ct,k.count);else if($.isInstancedBufferGeometry){const He=$._maxInstanceCount!==void 0?$._maxInstanceCount:1/0,Gt=Math.min($.instanceCount,He);ft.renderInstances(lt,Ct,Gt)}else ft.render(lt,Ct)};function Et(b,H,$){b.transparent===!0&&b.side===mi&&b.forceSinglePass===!1?(b.side=Cn,b.needsUpdate=!0,sr(b,H,$),b.side=er,b.needsUpdate=!0,sr(b,H,$),b.side=mi):sr(b,H,$)}this.compile=function(b,H,$=null){$===null&&($=b),p=we.get($),p.init(H),E.push(p),$.traverseVisible(function(k){k.isLight&&k.layers.test(H.layers)&&(p.pushLight(k),k.castShadow&&p.pushShadow(k))}),b!==$&&b.traverseVisible(function(k){k.isLight&&k.layers.test(H.layers)&&(p.pushLight(k),k.castShadow&&p.pushShadow(k))}),p.setupLights();const X=new Set;return b.traverse(function(k){const ce=k.material;if(ce)if(Array.isArray(ce))for(let Re=0;Re<ce.length;Re++){const Ce=ce[Re];Et(Ce,$,k),X.add(Ce)}else Et(ce,$,k),X.add(ce)}),E.pop(),p=null,X},this.compileAsync=function(b,H,$=null){const X=this.compile(b,H,$);return new Promise(k=>{function ce(){if(X.forEach(function(Re){Ye.get(Re).currentProgram.isReady()&&X.delete(Re)}),X.size===0){k(b);return}setTimeout(ce,10)}tt.get("KHR_parallel_shader_compile")!==null?ce():setTimeout(ce,10)})};let at=null;function ln(b){at&&at(b)}function Ft(){en.stop()}function Ot(){en.start()}const en=new Qd;en.setAnimationLoop(ln),typeof self<"u"&&en.setContext(self),this.setAnimationLoop=function(b){at=b,re.setAnimationLoop(b),b===null?en.stop():en.start()},re.addEventListener("sessionstart",Ft),re.addEventListener("sessionend",Ot),this.render=function(b,H){if(H!==void 0&&H.isCamera!==!0){console.error("THREE.WebGLRenderer.render: camera is not an instance of THREE.Camera.");return}if(T===!0)return;if(b.matrixWorldAutoUpdate===!0&&b.updateMatrixWorld(),H.parent===null&&H.matrixWorldAutoUpdate===!0&&H.updateMatrixWorld(),re.enabled===!0&&re.isPresenting===!0&&(re.cameraAutoUpdate===!0&&re.updateCamera(H),H=re.getCamera()),b.isScene===!0&&b.onBeforeRender(y,b,H,D),p=we.get(b,E.length),p.init(H),E.push(p),xe.multiplyMatrices(H.projectionMatrix,H.matrixWorldInverse),ve.setFromProjectionMatrix(xe),le=this.localClippingEnabled,te=je.init(this.clippingPlanes,le),v=me.get(b,f.length),v.init(),f.push(v),re.enabled===!0&&re.isPresenting===!0){const ce=y.xr.getDepthSensingMesh();ce!==null&&ai(ce,H,-1/0,y.sortObjects)}ai(b,H,0,y.sortObjects),v.finish(),y.sortObjects===!0&&v.sort(ee,pe),Ne=re.enabled===!1||re.isPresenting===!1||re.hasDepthSensing()===!1,Ne&&Te.addToRenderList(v,b),this.info.render.frame++,te===!0&&je.beginShadows();const $=p.state.shadowsArray;fe.render($,b,H),te===!0&&je.endShadows(),this.info.autoReset===!0&&this.info.reset();const X=v.opaque,k=v.transmissive;if(p.setupLights(),H.isArrayCamera){const ce=H.cameras;if(k.length>0)for(let Re=0,Ce=ce.length;Re<Ce;Re++){const De=ce[Re];_n(X,k,b,De)}Ne&&Te.render(b);for(let Re=0,Ce=ce.length;Re<Ce;Re++){const De=ce[Re];_i(v,b,De,De.viewport)}}else k.length>0&&_n(X,k,b,H),Ne&&Te.render(b),_i(v,b,H);D!==null&&(We.updateMultisampleRenderTarget(D),We.updateRenderTargetMipmap(D)),b.isScene===!0&&b.onAfterRender(y,b,H),N.resetDefaultState(),B=-1,w=null,E.pop(),E.length>0?(p=E[E.length-1],te===!0&&je.setGlobalState(y.clippingPlanes,p.state.camera)):p=null,f.pop(),f.length>0?v=f[f.length-1]:v=null};function ai(b,H,$,X){if(b.visible===!1)return;if(b.layers.test(H.layers)){if(b.isGroup)$=b.renderOrder;else if(b.isLOD)b.autoUpdate===!0&&b.update(H);else if(b.isLight)p.pushLight(b),b.castShadow&&p.pushShadow(b);else if(b.isSprite){if(!b.frustumCulled||ve.intersectsSprite(b)){X&&Be.setFromMatrixPosition(b.matrixWorld).applyMatrix4(xe);const Re=Q.update(b),Ce=b.material;Ce.visible&&v.push(b,Re,Ce,$,Be.z,null)}}else if((b.isMesh||b.isLine||b.isPoints)&&(!b.frustumCulled||ve.intersectsObject(b))){const Re=Q.update(b),Ce=b.material;if(X&&(b.boundingSphere!==void 0?(b.boundingSphere===null&&b.computeBoundingSphere(),Be.copy(b.boundingSphere.center)):(Re.boundingSphere===null&&Re.computeBoundingSphere(),Be.copy(Re.boundingSphere.center)),Be.applyMatrix4(b.matrixWorld).applyMatrix4(xe)),Array.isArray(Ce)){const De=Re.groups;for(let Ze=0,Je=De.length;Ze<Je;Ze++){const Oe=De[Ze],lt=Ce[Oe.materialIndex];lt&&lt.visible&&v.push(b,Re,lt,$,Be.z,Oe)}}else Ce.visible&&v.push(b,Re,Ce,$,Be.z,null)}}const ce=b.children;for(let Re=0,Ce=ce.length;Re<Ce;Re++)ai(ce[Re],H,$,X)}function _i(b,H,$,X){const k=b.opaque,ce=b.transmissive,Re=b.transparent;p.setupLightsView($),te===!0&&je.setGlobalState(y.clippingPlanes,$),X&&Fe.viewport(x.copy(X)),k.length>0&&qn(k,H,$),ce.length>0&&qn(ce,H,$),Re.length>0&&qn(Re,H,$),Fe.buffers.depth.setTest(!0),Fe.buffers.depth.setMask(!0),Fe.buffers.color.setMask(!0),Fe.setPolygonOffset(!1)}function _n(b,H,$,X){if(($.isScene===!0?$.overrideMaterial:null)!==null)return;p.state.transmissionRenderTarget[X.id]===void 0&&(p.state.transmissionRenderTarget[X.id]=new Ar(1,1,{generateMipmaps:!0,type:tt.has("EXT_color_buffer_half_float")||tt.has("EXT_color_buffer_float")?ha:Ui,minFilter:Er,samples:4,stencilBuffer:s,resolveDepthBuffer:!1,resolveStencilBuffer:!1,colorSpace:St.workingColorSpace}));const ce=p.state.transmissionRenderTarget[X.id],Re=X.viewport||x;ce.setSize(Re.z,Re.w);const Ce=y.getRenderTarget();y.setRenderTarget(ce),y.getClearColor(O),K=y.getClearAlpha(),K<1&&y.setClearColor(16777215,.5),y.clear(),Ne&&Te.render($);const De=y.toneMapping;y.toneMapping=Ji;const Ze=X.viewport;if(X.viewport!==void 0&&(X.viewport=void 0),p.setupLightsView(X),te===!0&&je.setGlobalState(y.clippingPlanes,X),qn(b,$,X),We.updateMultisampleRenderTarget(ce),We.updateRenderTargetMipmap(ce),tt.has("WEBGL_multisampled_render_to_texture")===!1){let Je=!1;for(let Oe=0,lt=H.length;Oe<lt;Oe++){const Rt=H[Oe],Ct=Rt.object,cn=Rt.geometry,ft=Rt.material,He=Rt.group;if(ft.side===mi&&Ct.layers.test(X.layers)){const Gt=ft.side;ft.side=Cn,ft.needsUpdate=!0,vi(Ct,$,X,cn,ft,He),ft.side=Gt,ft.needsUpdate=!0,Je=!0}}Je===!0&&(We.updateMultisampleRenderTarget(ce),We.updateRenderTargetMipmap(ce))}y.setRenderTarget(Ce),y.setClearColor(O,K),Ze!==void 0&&(X.viewport=Ze),y.toneMapping=De}function qn(b,H,$){const X=H.isScene===!0?H.overrideMaterial:null;for(let k=0,ce=b.length;k<ce;k++){const Re=b[k],Ce=Re.object,De=Re.geometry,Ze=X===null?Re.material:X,Je=Re.group;Ce.layers.test($.layers)&&vi(Ce,H,$,De,Ze,Je)}}function vi(b,H,$,X,k,ce){b.onBeforeRender(y,H,$,X,k,ce),b.modelViewMatrix.multiplyMatrices($.matrixWorldInverse,b.matrixWorld),b.normalMatrix.getNormalMatrix(b.modelViewMatrix),k.onBeforeRender(y,H,$,X,b,ce),k.transparent===!0&&k.side===mi&&k.forceSinglePass===!1?(k.side=Cn,k.needsUpdate=!0,y.renderBufferDirect($,H,X,k,b,ce),k.side=er,k.needsUpdate=!0,y.renderBufferDirect($,H,X,k,b,ce),k.side=mi):y.renderBufferDirect($,H,X,k,b,ce),b.onAfterRender(y,H,$,X,k,ce)}function sr(b,H,$){H.isScene!==!0&&(H=Ve);const X=Ye.get(b),k=p.state.lights,ce=p.state.shadowsArray,Re=k.state.version,Ce=G.getParameters(b,k.state,ce,H,$),De=G.getProgramCacheKey(Ce);let Ze=X.programs;X.environment=b.isMeshStandardMaterial?H.environment:null,X.fog=H.fog,X.envMap=(b.isMeshStandardMaterial?S:L).get(b.envMap||X.environment),X.envMapRotation=X.environment!==null&&b.envMap===null?H.environmentRotation:b.envMapRotation,Ze===void 0&&(b.addEventListener("dispose",$e),Ze=new Map,X.programs=Ze);let Je=Ze.get(De);if(Je!==void 0){if(X.currentProgram===Je&&X.lightsStateVersion===Re)return fa(b,Ce),Je}else Ce.uniforms=G.getUniforms(b),b.onBeforeCompile(Ce,y),Je=G.acquireProgram(Ce,De),Ze.set(De,Je),X.uniforms=Ce.uniforms;const Oe=X.uniforms;return(!b.isShaderMaterial&&!b.isRawShaderMaterial||b.clipping===!0)&&(Oe.clippingPlanes=je.uniform),fa(b,Ce),X.needsLights=Vo(b),X.lightsStateVersion=Re,X.needsLights&&(Oe.ambientLightColor.value=k.state.ambient,Oe.lightProbe.value=k.state.probe,Oe.directionalLights.value=k.state.directional,Oe.directionalLightShadows.value=k.state.directionalShadow,Oe.spotLights.value=k.state.spot,Oe.spotLightShadows.value=k.state.spotShadow,Oe.rectAreaLights.value=k.state.rectArea,Oe.ltc_1.value=k.state.rectAreaLTC1,Oe.ltc_2.value=k.state.rectAreaLTC2,Oe.pointLights.value=k.state.point,Oe.pointLightShadows.value=k.state.pointShadow,Oe.hemisphereLights.value=k.state.hemi,Oe.directionalShadowMap.value=k.state.directionalShadowMap,Oe.directionalShadowMatrix.value=k.state.directionalShadowMatrix,Oe.spotShadowMap.value=k.state.spotShadowMap,Oe.spotLightMatrix.value=k.state.spotLightMatrix,Oe.spotLightMap.value=k.state.spotLightMap,Oe.pointShadowMap.value=k.state.pointShadowMap,Oe.pointShadowMatrix.value=k.state.pointShadowMatrix),X.currentProgram=Je,X.uniformsList=null,Je}function Os(b){if(b.uniformsList===null){const H=b.currentProgram.getUniforms();b.uniformsList=lo.seqWithValue(H.seq,b.uniforms)}return b.uniformsList}function fa(b,H){const $=Ye.get(b);$.outputColorSpace=H.outputColorSpace,$.batching=H.batching,$.batchingColor=H.batchingColor,$.instancing=H.instancing,$.instancingColor=H.instancingColor,$.instancingMorph=H.instancingMorph,$.skinning=H.skinning,$.morphTargets=H.morphTargets,$.morphNormals=H.morphNormals,$.morphColors=H.morphColors,$.morphTargetsCount=H.morphTargetsCount,$.numClippingPlanes=H.numClippingPlanes,$.numIntersection=H.numClipIntersection,$.vertexAlphas=H.vertexAlphas,$.vertexTangents=H.vertexTangents,$.toneMapping=H.toneMapping}function Ho(b,H,$,X,k){H.isScene!==!0&&(H=Ve),We.resetTextureUnits();const ce=H.fog,Re=X.isMeshStandardMaterial?H.environment:null,Ce=D===null?y.outputColorSpace:D.isXRRenderTarget===!0?D.texture.colorSpace:rr,De=(X.isMeshStandardMaterial?S:L).get(X.envMap||Re),Ze=X.vertexColors===!0&&!!$.attributes.color&&$.attributes.color.itemSize===4,Je=!!$.attributes.tangent&&(!!X.normalMap||X.anisotropy>0),Oe=!!$.morphAttributes.position,lt=!!$.morphAttributes.normal,Rt=!!$.morphAttributes.color;let Ct=Ji;X.toneMapped&&(D===null||D.isXRRenderTarget===!0)&&(Ct=y.toneMapping);const cn=$.morphAttributes.position||$.morphAttributes.normal||$.morphAttributes.color,ft=cn!==void 0?cn.length:0,He=Ye.get(X),Gt=p.state.lights;if(te===!0&&(le===!0||b!==w)){const An=b===w&&X.id===B;je.setState(X,b,An)}let pt=!1;X.version===He.__version?(He.needsLights&&He.lightsStateVersion!==Gt.state.version||He.outputColorSpace!==Ce||k.isBatchedMesh&&He.batching===!1||!k.isBatchedMesh&&He.batching===!0||k.isBatchedMesh&&He.batchingColor===!0&&k.colorTexture===null||k.isBatchedMesh&&He.batchingColor===!1&&k.colorTexture!==null||k.isInstancedMesh&&He.instancing===!1||!k.isInstancedMesh&&He.instancing===!0||k.isSkinnedMesh&&He.skinning===!1||!k.isSkinnedMesh&&He.skinning===!0||k.isInstancedMesh&&He.instancingColor===!0&&k.instanceColor===null||k.isInstancedMesh&&He.instancingColor===!1&&k.instanceColor!==null||k.isInstancedMesh&&He.instancingMorph===!0&&k.morphTexture===null||k.isInstancedMesh&&He.instancingMorph===!1&&k.morphTexture!==null||He.envMap!==De||X.fog===!0&&He.fog!==ce||He.numClippingPlanes!==void 0&&(He.numClippingPlanes!==je.numPlanes||He.numIntersection!==je.numIntersection)||He.vertexAlphas!==Ze||He.vertexTangents!==Je||He.morphTargets!==Oe||He.morphNormals!==lt||He.morphColors!==Rt||He.toneMapping!==Ct||He.morphTargetsCount!==ft)&&(pt=!0):(pt=!0,He.__version=X.version);let Pt=He.currentProgram;pt===!0&&(Pt=sr(X,H,k));let Mi=!1,hn=!1,ar=!1;const kt=Pt.getUniforms(),oi=He.uniforms;if(Fe.useProgram(Pt.program)&&(Mi=!0,hn=!0,ar=!0),X.id!==B&&(B=X.id,hn=!0),Mi||w!==b){kt.setValue(U,"projectionMatrix",b.projectionMatrix),kt.setValue(U,"viewMatrix",b.matrixWorldInverse);const An=kt.map.cameraPosition;An!==void 0&&An.setValue(U,he.setFromMatrixPosition(b.matrixWorld)),ot.logarithmicDepthBuffer&&kt.setValue(U,"logDepthBufFC",2/(Math.log(b.far+1)/Math.LN2)),(X.isMeshPhongMaterial||X.isMeshToonMaterial||X.isMeshLambertMaterial||X.isMeshBasicMaterial||X.isMeshStandardMaterial||X.isShaderMaterial)&&kt.setValue(U,"isOrthographic",b.isOrthographicCamera===!0),w!==b&&(w=b,hn=!0,ar=!0)}if(k.isSkinnedMesh){kt.setOptional(U,k,"bindMatrix"),kt.setOptional(U,k,"bindMatrixInverse");const An=k.skeleton;An&&(An.boneTexture===null&&An.computeBoneTexture(),kt.setValue(U,"boneTexture",An.boneTexture,We))}k.isBatchedMesh&&(kt.setOptional(U,k,"batchingTexture"),kt.setValue(U,"batchingTexture",k._matricesTexture,We),kt.setOptional(U,k,"batchingIdTexture"),kt.setValue(U,"batchingIdTexture",k._indirectTexture,We),kt.setOptional(U,k,"batchingColorTexture"),k._colorsTexture!==null&&kt.setValue(U,"batchingColorTexture",k._colorsTexture,We));const Bs=$.morphAttributes;if((Bs.position!==void 0||Bs.normal!==void 0||Bs.color!==void 0)&&Ke.update(k,$,Pt),(hn||He.receiveShadow!==k.receiveShadow)&&(He.receiveShadow=k.receiveShadow,kt.setValue(U,"receiveShadow",k.receiveShadow)),X.isMeshGouraudMaterial&&X.envMap!==null&&(oi.envMap.value=De,oi.flipEnvMap.value=De.isCubeTexture&&De.isRenderTargetTexture===!1?-1:1),X.isMeshStandardMaterial&&X.envMap===null&&H.environment!==null&&(oi.envMapIntensity.value=H.environmentIntensity),hn&&(kt.setValue(U,"toneMappingExposure",y.toneMappingExposure),He.needsLights&&xi(oi,ar),ce&&X.fog===!0&&Ee.refreshFogUniforms(oi,ce),Ee.refreshMaterialUniforms(oi,X,Y,J,p.state.transmissionRenderTarget[b.id]),lo.upload(U,Os(He),oi,We)),X.isShaderMaterial&&X.uniformsNeedUpdate===!0&&(lo.upload(U,Os(He),oi,We),X.uniformsNeedUpdate=!1),X.isSpriteMaterial&&kt.setValue(U,"center",k.center),kt.setValue(U,"modelViewMatrix",k.modelViewMatrix),kt.setValue(U,"normalMatrix",k.normalMatrix),kt.setValue(U,"modelMatrix",k.matrixWorld),X.isShaderMaterial||X.isRawShaderMaterial){const An=X.uniformsGroups;for(let Ur=0,pa=An.length;Ur<pa;Ur++){const ma=An[Ur];oe.update(ma,Pt),oe.bind(ma,Pt)}}return Pt}function xi(b,H){b.ambientLightColor.needsUpdate=H,b.lightProbe.needsUpdate=H,b.directionalLights.needsUpdate=H,b.directionalLightShadows.needsUpdate=H,b.pointLights.needsUpdate=H,b.pointLightShadows.needsUpdate=H,b.spotLights.needsUpdate=H,b.spotLightShadows.needsUpdate=H,b.rectAreaLights.needsUpdate=H,b.hemisphereLights.needsUpdate=H}function Vo(b){return b.isMeshLambertMaterial||b.isMeshToonMaterial||b.isMeshPhongMaterial||b.isMeshStandardMaterial||b.isShadowMaterial||b.isShaderMaterial&&b.lights===!0}this.getActiveCubeFace=function(){return z},this.getActiveMipmapLevel=function(){return C},this.getRenderTarget=function(){return D},this.setRenderTargetTextures=function(b,H,$){Ye.get(b.texture).__webglTexture=H,Ye.get(b.depthTexture).__webglTexture=$;const X=Ye.get(b);X.__hasExternalTextures=!0,X.__autoAllocateDepthBuffer=$===void 0,X.__autoAllocateDepthBuffer||tt.has("WEBGL_multisampled_render_to_texture")===!0&&(console.warn("THREE.WebGLRenderer: Render-to-texture extension was disabled because an external texture was provided"),X.__useRenderToTexture=!1)},this.setRenderTargetFramebuffer=function(b,H){const $=Ye.get(b);$.__webglFramebuffer=H,$.__useDefaultFramebuffer=H===void 0},this.setRenderTarget=function(b,H=0,$=0){D=b,z=H,C=$;let X=!0,k=null,ce=!1,Re=!1;if(b){const De=Ye.get(b);if(De.__useDefaultFramebuffer!==void 0)Fe.bindFramebuffer(U.FRAMEBUFFER,null),X=!1;else if(De.__webglFramebuffer===void 0)We.setupRenderTarget(b);else if(De.__hasExternalTextures)We.rebindTextures(b,Ye.get(b.texture).__webglTexture,Ye.get(b.depthTexture).__webglTexture);else if(b.depthBuffer){const Oe=b.depthTexture;if(De.__boundDepthTexture!==Oe){if(Oe!==null&&Ye.has(Oe)&&(b.width!==Oe.image.width||b.height!==Oe.image.height))throw new Error("WebGLRenderTarget: Attached DepthTexture is initialized to the incorrect size.");We.setupDepthRenderbuffer(b)}}const Ze=b.texture;(Ze.isData3DTexture||Ze.isDataArrayTexture||Ze.isCompressedArrayTexture)&&(Re=!0);const Je=Ye.get(b).__webglFramebuffer;b.isWebGLCubeRenderTarget?(Array.isArray(Je[H])?k=Je[H][$]:k=Je[H],ce=!0):b.samples>0&&We.useMultisampledRTT(b)===!1?k=Ye.get(b).__webglMultisampledFramebuffer:Array.isArray(Je)?k=Je[$]:k=Je,x.copy(b.viewport),R.copy(b.scissor),j=b.scissorTest}else x.copy(ue).multiplyScalar(Y).floor(),R.copy(_e).multiplyScalar(Y).floor(),j=be;if(Fe.bindFramebuffer(U.FRAMEBUFFER,k)&&X&&Fe.drawBuffers(b,k),Fe.viewport(x),Fe.scissor(R),Fe.setScissorTest(j),ce){const De=Ye.get(b.texture);U.framebufferTexture2D(U.FRAMEBUFFER,U.COLOR_ATTACHMENT0,U.TEXTURE_CUBE_MAP_POSITIVE_X+H,De.__webglTexture,$)}else if(Re){const De=Ye.get(b.texture),Ze=H||0;U.framebufferTextureLayer(U.FRAMEBUFFER,U.COLOR_ATTACHMENT0,De.__webglTexture,$||0,Ze)}B=-1},this.readRenderTargetPixels=function(b,H,$,X,k,ce,Re){if(!(b&&b.isWebGLRenderTarget)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");return}let Ce=Ye.get(b).__webglFramebuffer;if(b.isWebGLCubeRenderTarget&&Re!==void 0&&(Ce=Ce[Re]),Ce){Fe.bindFramebuffer(U.FRAMEBUFFER,Ce);try{const De=b.texture,Ze=De.format,Je=De.type;if(!ot.textureFormatReadable(Ze)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in RGBA or implementation defined format.");return}if(!ot.textureTypeReadable(Je)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in UnsignedByteType or implementation defined type.");return}H>=0&&H<=b.width-X&&$>=0&&$<=b.height-k&&U.readPixels(H,$,X,k,ke.convert(Ze),ke.convert(Je),ce)}finally{const De=D!==null?Ye.get(D).__webglFramebuffer:null;Fe.bindFramebuffer(U.FRAMEBUFFER,De)}}},this.readRenderTargetPixelsAsync=async function(b,H,$,X,k,ce,Re){if(!(b&&b.isWebGLRenderTarget))throw new Error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");let Ce=Ye.get(b).__webglFramebuffer;if(b.isWebGLCubeRenderTarget&&Re!==void 0&&(Ce=Ce[Re]),Ce){Fe.bindFramebuffer(U.FRAMEBUFFER,Ce);try{const De=b.texture,Ze=De.format,Je=De.type;if(!ot.textureFormatReadable(Ze))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in RGBA or implementation defined format.");if(!ot.textureTypeReadable(Je))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in UnsignedByteType or implementation defined type.");if(H>=0&&H<=b.width-X&&$>=0&&$<=b.height-k){const Oe=U.createBuffer();U.bindBuffer(U.PIXEL_PACK_BUFFER,Oe),U.bufferData(U.PIXEL_PACK_BUFFER,ce.byteLength,U.STREAM_READ),U.readPixels(H,$,X,k,ke.convert(Ze),ke.convert(Je),0),U.flush();const lt=U.fenceSync(U.SYNC_GPU_COMMANDS_COMPLETE,0);await Dm(U,lt,4);try{U.bindBuffer(U.PIXEL_PACK_BUFFER,Oe),U.getBufferSubData(U.PIXEL_PACK_BUFFER,0,ce)}finally{U.deleteBuffer(Oe),U.deleteSync(lt)}return ce}}finally{const De=D!==null?Ye.get(D).__webglFramebuffer:null;Fe.bindFramebuffer(U.FRAMEBUFFER,De)}}},this.copyFramebufferToTexture=function(b,H=null,$=0){b.isTexture!==!0&&(xs("WebGLRenderer: copyFramebufferToTexture function signature has changed."),H=arguments[0]||null,b=arguments[1]);const X=Math.pow(2,-$),k=Math.floor(b.image.width*X),ce=Math.floor(b.image.height*X),Re=H!==null?H.x:0,Ce=H!==null?H.y:0;We.setTexture2D(b,0),U.copyTexSubImage2D(U.TEXTURE_2D,$,0,0,Re,Ce,k,ce),Fe.unbindTexture()},this.copyTextureToTexture=function(b,H,$=null,X=null,k=0){b.isTexture!==!0&&(xs("WebGLRenderer: copyTextureToTexture function signature has changed."),X=arguments[0]||null,b=arguments[1],H=arguments[2],k=arguments[3]||0,$=null);let ce,Re,Ce,De,Ze,Je;$!==null?(ce=$.max.x-$.min.x,Re=$.max.y-$.min.y,Ce=$.min.x,De=$.min.y):(ce=b.image.width,Re=b.image.height,Ce=0,De=0),X!==null?(Ze=X.x,Je=X.y):(Ze=0,Je=0);const Oe=ke.convert(H.format),lt=ke.convert(H.type);We.setTexture2D(H,0),U.pixelStorei(U.UNPACK_FLIP_Y_WEBGL,H.flipY),U.pixelStorei(U.UNPACK_PREMULTIPLY_ALPHA_WEBGL,H.premultiplyAlpha),U.pixelStorei(U.UNPACK_ALIGNMENT,H.unpackAlignment);const Rt=U.getParameter(U.UNPACK_ROW_LENGTH),Ct=U.getParameter(U.UNPACK_IMAGE_HEIGHT),cn=U.getParameter(U.UNPACK_SKIP_PIXELS),ft=U.getParameter(U.UNPACK_SKIP_ROWS),He=U.getParameter(U.UNPACK_SKIP_IMAGES),Gt=b.isCompressedTexture?b.mipmaps[k]:b.image;U.pixelStorei(U.UNPACK_ROW_LENGTH,Gt.width),U.pixelStorei(U.UNPACK_IMAGE_HEIGHT,Gt.height),U.pixelStorei(U.UNPACK_SKIP_PIXELS,Ce),U.pixelStorei(U.UNPACK_SKIP_ROWS,De),b.isDataTexture?U.texSubImage2D(U.TEXTURE_2D,k,Ze,Je,ce,Re,Oe,lt,Gt.data):b.isCompressedTexture?U.compressedTexSubImage2D(U.TEXTURE_2D,k,Ze,Je,Gt.width,Gt.height,Oe,Gt.data):U.texSubImage2D(U.TEXTURE_2D,k,Ze,Je,ce,Re,Oe,lt,Gt),U.pixelStorei(U.UNPACK_ROW_LENGTH,Rt),U.pixelStorei(U.UNPACK_IMAGE_HEIGHT,Ct),U.pixelStorei(U.UNPACK_SKIP_PIXELS,cn),U.pixelStorei(U.UNPACK_SKIP_ROWS,ft),U.pixelStorei(U.UNPACK_SKIP_IMAGES,He),k===0&&H.generateMipmaps&&U.generateMipmap(U.TEXTURE_2D),Fe.unbindTexture()},this.copyTextureToTexture3D=function(b,H,$=null,X=null,k=0){b.isTexture!==!0&&(xs("WebGLRenderer: copyTextureToTexture3D function signature has changed."),$=arguments[0]||null,X=arguments[1]||null,b=arguments[2],H=arguments[3],k=arguments[4]||0);let ce,Re,Ce,De,Ze,Je,Oe,lt,Rt;const Ct=b.isCompressedTexture?b.mipmaps[k]:b.image;$!==null?(ce=$.max.x-$.min.x,Re=$.max.y-$.min.y,Ce=$.max.z-$.min.z,De=$.min.x,Ze=$.min.y,Je=$.min.z):(ce=Ct.width,Re=Ct.height,Ce=Ct.depth,De=0,Ze=0,Je=0),X!==null?(Oe=X.x,lt=X.y,Rt=X.z):(Oe=0,lt=0,Rt=0);const cn=ke.convert(H.format),ft=ke.convert(H.type);let He;if(H.isData3DTexture)We.setTexture3D(H,0),He=U.TEXTURE_3D;else if(H.isDataArrayTexture||H.isCompressedArrayTexture)We.setTexture2DArray(H,0),He=U.TEXTURE_2D_ARRAY;else{console.warn("THREE.WebGLRenderer.copyTextureToTexture3D: only supports THREE.DataTexture3D and THREE.DataTexture2DArray.");return}U.pixelStorei(U.UNPACK_FLIP_Y_WEBGL,H.flipY),U.pixelStorei(U.UNPACK_PREMULTIPLY_ALPHA_WEBGL,H.premultiplyAlpha),U.pixelStorei(U.UNPACK_ALIGNMENT,H.unpackAlignment);const Gt=U.getParameter(U.UNPACK_ROW_LENGTH),pt=U.getParameter(U.UNPACK_IMAGE_HEIGHT),Pt=U.getParameter(U.UNPACK_SKIP_PIXELS),Mi=U.getParameter(U.UNPACK_SKIP_ROWS),hn=U.getParameter(U.UNPACK_SKIP_IMAGES);U.pixelStorei(U.UNPACK_ROW_LENGTH,Ct.width),U.pixelStorei(U.UNPACK_IMAGE_HEIGHT,Ct.height),U.pixelStorei(U.UNPACK_SKIP_PIXELS,De),U.pixelStorei(U.UNPACK_SKIP_ROWS,Ze),U.pixelStorei(U.UNPACK_SKIP_IMAGES,Je),b.isDataTexture||b.isData3DTexture?U.texSubImage3D(He,k,Oe,lt,Rt,ce,Re,Ce,cn,ft,Ct.data):H.isCompressedArrayTexture?U.compressedTexSubImage3D(He,k,Oe,lt,Rt,ce,Re,Ce,cn,Ct.data):U.texSubImage3D(He,k,Oe,lt,Rt,ce,Re,Ce,cn,ft,Ct),U.pixelStorei(U.UNPACK_ROW_LENGTH,Gt),U.pixelStorei(U.UNPACK_IMAGE_HEIGHT,pt),U.pixelStorei(U.UNPACK_SKIP_PIXELS,Pt),U.pixelStorei(U.UNPACK_SKIP_ROWS,Mi),U.pixelStorei(U.UNPACK_SKIP_IMAGES,hn),k===0&&H.generateMipmaps&&U.generateMipmap(He),Fe.unbindTexture()},this.initRenderTarget=function(b){Ye.get(b).__webglFramebuffer===void 0&&We.setupRenderTarget(b)},this.initTexture=function(b){b.isCubeTexture?We.setTextureCube(b,0):b.isData3DTexture?We.setTexture3D(b,0):b.isDataArrayTexture||b.isCompressedArrayTexture?We.setTexture2DArray(b,0):We.setTexture2D(b,0),Fe.unbindTexture()},this.resetState=function(){z=0,C=0,D=null,Fe.reset(),N.reset()},typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}get coordinateSystem(){return Pi}get outputColorSpace(){return this._outputColorSpace}set outputColorSpace(e){this._outputColorSpace=e;const t=this.getContext();t.drawingBufferColorSpace=e===Oc?"display-p3":"srgb",t.unpackColorSpace=St.workingColorSpace===Ro?"display-p3":"srgb"}}class Gc{constructor(e,t=25e-5){this.isFogExp2=!0,this.name="",this.color=new nt(e),this.density=t}clone(){return new Gc(this.color,this.density)}toJSON(){return{type:"FogExp2",name:this.name,color:this.color.getHex(),density:this.density}}}class Wc extends Kt{constructor(){super(),this.isScene=!0,this.type="Scene",this.background=null,this.environment=null,this.fog=null,this.backgroundBlurriness=0,this.backgroundIntensity=1,this.backgroundRotation=new gi,this.environmentIntensity=1,this.environmentRotation=new gi,this.overrideMaterial=null,typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}copy(e,t){return super.copy(e,t),e.background!==null&&(this.background=e.background.clone()),e.environment!==null&&(this.environment=e.environment.clone()),e.fog!==null&&(this.fog=e.fog.clone()),this.backgroundBlurriness=e.backgroundBlurriness,this.backgroundIntensity=e.backgroundIntensity,this.backgroundRotation.copy(e.backgroundRotation),this.environmentIntensity=e.environmentIntensity,this.environmentRotation.copy(e.environmentRotation),e.overrideMaterial!==null&&(this.overrideMaterial=e.overrideMaterial.clone()),this.matrixAutoUpdate=e.matrixAutoUpdate,this}toJSON(e){const t=super.toJSON(e);return this.fog!==null&&(t.object.fog=this.fog.toJSON()),this.backgroundBlurriness>0&&(t.object.backgroundBlurriness=this.backgroundBlurriness),this.backgroundIntensity!==1&&(t.object.backgroundIntensity=this.backgroundIntensity),t.object.backgroundRotation=this.backgroundRotation.toArray(),this.environmentIntensity!==1&&(t.object.environmentIntensity=this.environmentIntensity),t.object.environmentRotation=this.environmentRotation.toArray(),t}}class Hx{constructor(e,t){this.isInterleavedBuffer=!0,this.array=e,this.stride=t,this.count=e!==void 0?e.length/t:0,this.usage=_c,this._updateRange={offset:0,count:-1},this.updateRanges=[],this.version=0,this.uuid=Li()}onUploadCallback(){}set needsUpdate(e){e===!0&&this.version++}get updateRange(){return xs("THREE.InterleavedBuffer: updateRange() is deprecated and will be removed in r169. Use addUpdateRange() instead."),this._updateRange}setUsage(e){return this.usage=e,this}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}copy(e){return this.array=new e.array.constructor(e.array),this.count=e.count,this.stride=e.stride,this.usage=e.usage,this}copyAt(e,t,n){e*=this.stride,n*=t.stride;for(let r=0,s=this.stride;r<s;r++)this.array[e+r]=t.array[n+r];return this}set(e,t=0){return this.array.set(e,t),this}clone(e){e.arrayBuffers===void 0&&(e.arrayBuffers={}),this.array.buffer._uuid===void 0&&(this.array.buffer._uuid=Li()),e.arrayBuffers[this.array.buffer._uuid]===void 0&&(e.arrayBuffers[this.array.buffer._uuid]=this.array.slice(0).buffer);const t=new this.array.constructor(e.arrayBuffers[this.array.buffer._uuid]),n=new this.constructor(t,this.stride);return n.setUsage(this.usage),n}onUpload(e){return this.onUploadCallback=e,this}toJSON(e){return e.arrayBuffers===void 0&&(e.arrayBuffers={}),this.array.buffer._uuid===void 0&&(this.array.buffer._uuid=Li()),e.arrayBuffers[this.array.buffer._uuid]===void 0&&(e.arrayBuffers[this.array.buffer._uuid]=Array.from(new Uint32Array(this.array.buffer))),{uuid:this.uuid,buffer:this.array.buffer._uuid,type:this.array.constructor.name,stride:this.stride}}}const Sn=new V;class xo{constructor(e,t,n,r=!1){this.isInterleavedBufferAttribute=!0,this.name="",this.data=e,this.itemSize=t,this.offset=n,this.normalized=r}get count(){return this.data.count}get array(){return this.data.array}set needsUpdate(e){this.data.needsUpdate=e}applyMatrix4(e){for(let t=0,n=this.data.count;t<n;t++)Sn.fromBufferAttribute(this,t),Sn.applyMatrix4(e),this.setXYZ(t,Sn.x,Sn.y,Sn.z);return this}applyNormalMatrix(e){for(let t=0,n=this.count;t<n;t++)Sn.fromBufferAttribute(this,t),Sn.applyNormalMatrix(e),this.setXYZ(t,Sn.x,Sn.y,Sn.z);return this}transformDirection(e){for(let t=0,n=this.count;t<n;t++)Sn.fromBufferAttribute(this,t),Sn.transformDirection(e),this.setXYZ(t,Sn.x,Sn.y,Sn.z);return this}getComponent(e,t){let n=this.array[e*this.data.stride+this.offset+t];return this.normalized&&(n=ni(n,this.array)),n}setComponent(e,t,n){return this.normalized&&(n=bt(n,this.array)),this.data.array[e*this.data.stride+this.offset+t]=n,this}setX(e,t){return this.normalized&&(t=bt(t,this.array)),this.data.array[e*this.data.stride+this.offset]=t,this}setY(e,t){return this.normalized&&(t=bt(t,this.array)),this.data.array[e*this.data.stride+this.offset+1]=t,this}setZ(e,t){return this.normalized&&(t=bt(t,this.array)),this.data.array[e*this.data.stride+this.offset+2]=t,this}setW(e,t){return this.normalized&&(t=bt(t,this.array)),this.data.array[e*this.data.stride+this.offset+3]=t,this}getX(e){let t=this.data.array[e*this.data.stride+this.offset];return this.normalized&&(t=ni(t,this.array)),t}getY(e){let t=this.data.array[e*this.data.stride+this.offset+1];return this.normalized&&(t=ni(t,this.array)),t}getZ(e){let t=this.data.array[e*this.data.stride+this.offset+2];return this.normalized&&(t=ni(t,this.array)),t}getW(e){let t=this.data.array[e*this.data.stride+this.offset+3];return this.normalized&&(t=ni(t,this.array)),t}setXY(e,t,n){return e=e*this.data.stride+this.offset,this.normalized&&(t=bt(t,this.array),n=bt(n,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this}setXYZ(e,t,n,r){return e=e*this.data.stride+this.offset,this.normalized&&(t=bt(t,this.array),n=bt(n,this.array),r=bt(r,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this.data.array[e+2]=r,this}setXYZW(e,t,n,r,s){return e=e*this.data.stride+this.offset,this.normalized&&(t=bt(t,this.array),n=bt(n,this.array),r=bt(r,this.array),s=bt(s,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this.data.array[e+2]=r,this.data.array[e+3]=s,this}clone(e){if(e===void 0){console.log("THREE.InterleavedBufferAttribute.clone(): Cloning an interleaved buffer attribute will de-interleave buffer data.");const t=[];for(let n=0;n<this.count;n++){const r=n*this.data.stride+this.offset;for(let s=0;s<this.itemSize;s++)t.push(this.data.array[r+s])}return new Xn(new this.array.constructor(t),this.itemSize,this.normalized)}else return e.interleavedBuffers===void 0&&(e.interleavedBuffers={}),e.interleavedBuffers[this.data.uuid]===void 0&&(e.interleavedBuffers[this.data.uuid]=this.data.clone(e)),new xo(e.interleavedBuffers[this.data.uuid],this.itemSize,this.offset,this.normalized)}toJSON(e){if(e===void 0){console.log("THREE.InterleavedBufferAttribute.toJSON(): Serializing an interleaved buffer attribute will de-interleave buffer data.");const t=[];for(let n=0;n<this.count;n++){const r=n*this.data.stride+this.offset;for(let s=0;s<this.itemSize;s++)t.push(this.data.array[r+s])}return{itemSize:this.itemSize,type:this.array.constructor.name,array:t,normalized:this.normalized}}else return e.interleavedBuffers===void 0&&(e.interleavedBuffers={}),e.interleavedBuffers[this.data.uuid]===void 0&&(e.interleavedBuffers[this.data.uuid]=this.data.toJSON(e)),{isInterleavedBufferAttribute:!0,itemSize:this.itemSize,data:this.data.uuid,offset:this.offset,normalized:this.normalized}}}class of extends Dr{constructor(e){super(),this.isSpriteMaterial=!0,this.type="SpriteMaterial",this.color=new nt(16777215),this.map=null,this.alphaMap=null,this.rotation=0,this.sizeAttenuation=!0,this.transparent=!0,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.alphaMap=e.alphaMap,this.rotation=e.rotation,this.sizeAttenuation=e.sizeAttenuation,this.fog=e.fog,this}}let cs;const js=new V,us=new V,hs=new V,ds=new Xe,Ks=new Xe,lf=new zt,Wa=new V,Zs=new V,Xa=new V,Ah=new Xe,Al=new Xe,Rh=new Xe;class Vx extends Kt{constructor(e=new of){if(super(),this.isSprite=!0,this.type="Sprite",cs===void 0){cs=new gn;const t=new Float32Array([-.5,-.5,0,0,0,.5,-.5,0,1,0,.5,.5,0,1,1,-.5,.5,0,0,1]),n=new Hx(t,5);cs.setIndex([0,1,2,0,2,3]),cs.setAttribute("position",new xo(n,3,0,!1)),cs.setAttribute("uv",new xo(n,2,3,!1))}this.geometry=cs,this.material=e,this.center=new Xe(.5,.5)}raycast(e,t){e.camera===null&&console.error('THREE.Sprite: "Raycaster.camera" needs to be set in order to raycast against sprites.'),us.setFromMatrixScale(this.matrixWorld),lf.copy(e.camera.matrixWorld),this.modelViewMatrix.multiplyMatrices(e.camera.matrixWorldInverse,this.matrixWorld),hs.setFromMatrixPosition(this.modelViewMatrix),e.camera.isPerspectiveCamera&&this.material.sizeAttenuation===!1&&us.multiplyScalar(-hs.z);const n=this.material.rotation;let r,s;n!==0&&(s=Math.cos(n),r=Math.sin(n));const a=this.center;Ya(Wa.set(-.5,-.5,0),hs,a,us,r,s),Ya(Zs.set(.5,-.5,0),hs,a,us,r,s),Ya(Xa.set(.5,.5,0),hs,a,us,r,s),Ah.set(0,0),Al.set(1,0),Rh.set(1,1);let o=e.ray.intersectTriangle(Wa,Zs,Xa,!1,js);if(o===null&&(Ya(Zs.set(-.5,.5,0),hs,a,us,r,s),Al.set(0,1),o=e.ray.intersectTriangle(Wa,Xa,Zs,!1,js),o===null))return;const l=e.ray.origin.distanceTo(js);l<e.near||l>e.far||t.push({distance:l,point:js.clone(),uv:Gn.getInterpolation(js,Wa,Zs,Xa,Ah,Al,Rh,new Xe),face:null,object:this})}copy(e,t){return super.copy(e,t),e.center!==void 0&&this.center.copy(e.center),this.material=e.material,this}}function Ya(i,e,t,n,r,s){ds.subVectors(i,t).addScalar(.5).multiply(n),r!==void 0?(Ks.x=s*ds.x-r*ds.y,Ks.y=r*ds.x+s*ds.y):Ks.copy(ds),i.copy(e),i.x+=Ks.x,i.y+=Ks.y,i.applyMatrix4(lf)}class Cr extends Dr{constructor(e){super(),this.isLineBasicMaterial=!0,this.type="LineBasicMaterial",this.color=new nt(16777215),this.map=null,this.linewidth=1,this.linecap="round",this.linejoin="round",this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.linewidth=e.linewidth,this.linecap=e.linecap,this.linejoin=e.linejoin,this.fog=e.fog,this}}const Mo=new V,So=new V,Ch=new zt,Js=new Po,qa=new Co,Rl=new V,Ph=new V;class yo extends Kt{constructor(e=new gn,t=new Cr){super(),this.isLine=!0,this.type="Line",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}computeLineDistances(){const e=this.geometry;if(e.index===null){const t=e.attributes.position,n=[0];for(let r=1,s=t.count;r<s;r++)Mo.fromBufferAttribute(t,r-1),So.fromBufferAttribute(t,r),n[r]=n[r-1],n[r]+=Mo.distanceTo(So);e.setAttribute("lineDistance",new wn(n,1))}else console.warn("THREE.Line.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.");return this}raycast(e,t){const n=this.geometry,r=this.matrixWorld,s=e.params.Line.threshold,a=n.drawRange;if(n.boundingSphere===null&&n.computeBoundingSphere(),qa.copy(n.boundingSphere),qa.applyMatrix4(r),qa.radius+=s,e.ray.intersectsSphere(qa)===!1)return;Ch.copy(r).invert(),Js.copy(e.ray).applyMatrix4(Ch);const o=s/((this.scale.x+this.scale.y+this.scale.z)/3),l=o*o,c=this.isLineSegments?2:1,u=n.index,d=n.attributes.position;if(u!==null){const m=Math.max(0,a.start),_=Math.min(u.count,a.start+a.count);for(let v=m,p=_-1;v<p;v+=c){const f=u.getX(v),E=u.getX(v+1),y=$a(this,e,Js,l,f,E);y&&t.push(y)}if(this.isLineLoop){const v=u.getX(_-1),p=u.getX(m),f=$a(this,e,Js,l,v,p);f&&t.push(f)}}else{const m=Math.max(0,a.start),_=Math.min(d.count,a.start+a.count);for(let v=m,p=_-1;v<p;v+=c){const f=$a(this,e,Js,l,v,v+1);f&&t.push(f)}if(this.isLineLoop){const v=$a(this,e,Js,l,_-1,m);v&&t.push(v)}}}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const r=t[n[0]];if(r!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let s=0,a=r.length;s<a;s++){const o=r[s].name||String(s);this.morphTargetInfluences.push(0),this.morphTargetDictionary[o]=s}}}}}function $a(i,e,t,n,r,s){const a=i.geometry.attributes.position;if(Mo.fromBufferAttribute(a,r),So.fromBufferAttribute(a,s),t.distanceSqToSegment(Mo,So,Rl,Ph)>n)return;Rl.applyMatrix4(i.matrixWorld);const l=e.ray.origin.distanceTo(Rl);if(!(l<e.near||l>e.far))return{distance:l,point:Ph.clone().applyMatrix4(i.matrixWorld),index:r,face:null,faceIndex:null,object:i}}const Lh=new V,Dh=new V;class Xc extends yo{constructor(e,t){super(e,t),this.isLineSegments=!0,this.type="LineSegments"}computeLineDistances(){const e=this.geometry;if(e.index===null){const t=e.attributes.position,n=[];for(let r=0,s=t.count;r<s;r+=2)Lh.fromBufferAttribute(t,r),Dh.fromBufferAttribute(t,r+1),n[r]=r===0?0:n[r-1],n[r+1]=n[r]+Lh.distanceTo(Dh);e.setAttribute("lineDistance",new wn(n,1))}else console.warn("THREE.LineSegments.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.");return this}}class Gx extends Tn{constructor(e,t,n,r,s,a,o,l,c){super(e,t,n,r,s,a,o,l,c),this.isCanvasTexture=!0,this.needsUpdate=!0}}const ja=new V,Ka=new V,Cl=new V,Za=new Gn;class Wx extends gn{constructor(e=null,t=1){if(super(),this.type="EdgesGeometry",this.parameters={geometry:e,thresholdAngle:t},e!==null){const r=Math.pow(10,4),s=Math.cos(vs*t),a=e.getIndex(),o=e.getAttribute("position"),l=a?a.count:o.count,c=[0,0,0],u=["a","b","c"],h=new Array(3),d={},m=[];for(let _=0;_<l;_+=3){a?(c[0]=a.getX(_),c[1]=a.getX(_+1),c[2]=a.getX(_+2)):(c[0]=_,c[1]=_+1,c[2]=_+2);const{a:v,b:p,c:f}=Za;if(v.fromBufferAttribute(o,c[0]),p.fromBufferAttribute(o,c[1]),f.fromBufferAttribute(o,c[2]),Za.getNormal(Cl),h[0]=`${Math.round(v.x*r)},${Math.round(v.y*r)},${Math.round(v.z*r)}`,h[1]=`${Math.round(p.x*r)},${Math.round(p.y*r)},${Math.round(p.z*r)}`,h[2]=`${Math.round(f.x*r)},${Math.round(f.y*r)},${Math.round(f.z*r)}`,!(h[0]===h[1]||h[1]===h[2]||h[2]===h[0]))for(let E=0;E<3;E++){const y=(E+1)%3,T=h[E],z=h[y],C=Za[u[E]],D=Za[u[y]],B=`${T}_${z}`,w=`${z}_${T}`;w in d&&d[w]?(Cl.dot(d[w].normal)<=s&&(m.push(C.x,C.y,C.z),m.push(D.x,D.y,D.z)),d[w]=null):B in d||(d[B]={index0:c[E],index1:c[y],normal:Cl.clone()})}}for(const _ in d)if(d[_]){const{index0:v,index1:p}=d[_];ja.fromBufferAttribute(o,v),Ka.fromBufferAttribute(o,p),m.push(ja.x,ja.y,ja.z),m.push(Ka.x,Ka.y,Ka.z)}this.setAttribute("position",new wn(m,3))}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}}class Yc extends gn{constructor(e=.5,t=1,n=32,r=1,s=0,a=Math.PI*2){super(),this.type="RingGeometry",this.parameters={innerRadius:e,outerRadius:t,thetaSegments:n,phiSegments:r,thetaStart:s,thetaLength:a},n=Math.max(3,n),r=Math.max(1,r);const o=[],l=[],c=[],u=[];let h=e;const d=(t-e)/r,m=new V,_=new Xe;for(let v=0;v<=r;v++){for(let p=0;p<=n;p++){const f=s+p/n*a;m.x=h*Math.cos(f),m.y=h*Math.sin(f),l.push(m.x,m.y,m.z),c.push(0,0,1),_.x=(m.x/t+1)/2,_.y=(m.y/t+1)/2,u.push(_.x,_.y)}h+=d}for(let v=0;v<r;v++){const p=v*(n+1);for(let f=0;f<n;f++){const E=f+p,y=E,T=E+n+1,z=E+n+2,C=E+1;o.push(y,T,C),o.push(T,z,C)}}this.setIndex(o),this.setAttribute("position",new wn(l,3)),this.setAttribute("normal",new wn(c,3)),this.setAttribute("uv",new wn(u,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Yc(e.innerRadius,e.outerRadius,e.thetaSegments,e.phiSegments,e.thetaStart,e.thetaLength)}}class Pl extends Dr{constructor(e){super(),this.isMeshStandardMaterial=!0,this.defines={STANDARD:""},this.type="MeshStandardMaterial",this.color=new nt(16777215),this.roughness=1,this.metalness=0,this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.emissive=new nt(0),this.emissiveIntensity=1,this.emissiveMap=null,this.bumpMap=null,this.bumpScale=1,this.normalMap=null,this.normalMapType=Gd,this.normalScale=new Xe(1,1),this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.roughnessMap=null,this.metalnessMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new gi,this.envMapIntensity=1,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.flatShading=!1,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.defines={STANDARD:""},this.color.copy(e.color),this.roughness=e.roughness,this.metalness=e.metalness,this.map=e.map,this.lightMap=e.lightMap,this.lightMapIntensity=e.lightMapIntensity,this.aoMap=e.aoMap,this.aoMapIntensity=e.aoMapIntensity,this.emissive.copy(e.emissive),this.emissiveMap=e.emissiveMap,this.emissiveIntensity=e.emissiveIntensity,this.bumpMap=e.bumpMap,this.bumpScale=e.bumpScale,this.normalMap=e.normalMap,this.normalMapType=e.normalMapType,this.normalScale.copy(e.normalScale),this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this.roughnessMap=e.roughnessMap,this.metalnessMap=e.metalnessMap,this.alphaMap=e.alphaMap,this.envMap=e.envMap,this.envMapRotation.copy(e.envMapRotation),this.envMapIntensity=e.envMapIntensity,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.wireframeLinecap=e.wireframeLinecap,this.wireframeLinejoin=e.wireframeLinejoin,this.flatShading=e.flatShading,this.fog=e.fog,this}}class Xx extends Cr{constructor(e){super(),this.isLineDashedMaterial=!0,this.type="LineDashedMaterial",this.scale=1,this.dashSize=3,this.gapSize=1,this.setValues(e)}copy(e){return super.copy(e),this.scale=e.scale,this.dashSize=e.dashSize,this.gapSize=e.gapSize,this}}class qc extends Kt{constructor(e,t=1){super(),this.isLight=!0,this.type="Light",this.color=new nt(e),this.intensity=t}dispose(){}copy(e,t){return super.copy(e,t),this.color.copy(e.color),this.intensity=e.intensity,this}toJSON(e){const t=super.toJSON(e);return t.object.color=this.color.getHex(),t.object.intensity=this.intensity,this.groundColor!==void 0&&(t.object.groundColor=this.groundColor.getHex()),this.distance!==void 0&&(t.object.distance=this.distance),this.angle!==void 0&&(t.object.angle=this.angle),this.decay!==void 0&&(t.object.decay=this.decay),this.penumbra!==void 0&&(t.object.penumbra=this.penumbra),this.shadow!==void 0&&(t.object.shadow=this.shadow.toJSON()),this.target!==void 0&&(t.object.target=this.target.uuid),t}}class Yx extends qc{constructor(e,t,n){super(e,n),this.isHemisphereLight=!0,this.type="HemisphereLight",this.position.copy(Kt.DEFAULT_UP),this.updateMatrix(),this.groundColor=new nt(t)}copy(e,t){return super.copy(e,t),this.groundColor.copy(e.groundColor),this}}const Ll=new zt,Ih=new V,Uh=new V;class qx{constructor(e){this.camera=e,this.intensity=1,this.bias=0,this.normalBias=0,this.radius=1,this.blurSamples=8,this.mapSize=new Xe(512,512),this.map=null,this.mapPass=null,this.matrix=new zt,this.autoUpdate=!0,this.needsUpdate=!1,this._frustum=new Hc,this._frameExtents=new Xe(1,1),this._viewportCount=1,this._viewports=[new jt(0,0,1,1)]}getViewportCount(){return this._viewportCount}getFrustum(){return this._frustum}updateMatrices(e){const t=this.camera,n=this.matrix;Ih.setFromMatrixPosition(e.matrixWorld),t.position.copy(Ih),Uh.setFromMatrixPosition(e.target.matrixWorld),t.lookAt(Uh),t.updateMatrixWorld(),Ll.multiplyMatrices(t.projectionMatrix,t.matrixWorldInverse),this._frustum.setFromProjectionMatrix(Ll),n.set(.5,0,0,.5,0,.5,0,.5,0,0,.5,.5,0,0,0,1),n.multiply(Ll)}getViewport(e){return this._viewports[e]}getFrameExtents(){return this._frameExtents}dispose(){this.map&&this.map.dispose(),this.mapPass&&this.mapPass.dispose()}copy(e){return this.camera=e.camera.clone(),this.intensity=e.intensity,this.bias=e.bias,this.radius=e.radius,this.mapSize.copy(e.mapSize),this}clone(){return new this.constructor().copy(this)}toJSON(){const e={};return this.intensity!==1&&(e.intensity=this.intensity),this.bias!==0&&(e.bias=this.bias),this.normalBias!==0&&(e.normalBias=this.normalBias),this.radius!==1&&(e.radius=this.radius),(this.mapSize.x!==512||this.mapSize.y!==512)&&(e.mapSize=this.mapSize.toArray()),e.camera=this.camera.toJSON(!1).object,delete e.camera.matrix,e}}class $x extends qx{constructor(){super(new Ss(-5,5,5,-5,.5,500)),this.isDirectionalLightShadow=!0}}class jx extends qc{constructor(e,t){super(e,t),this.isDirectionalLight=!0,this.type="DirectionalLight",this.position.copy(Kt.DEFAULT_UP),this.updateMatrix(),this.target=new Kt,this.shadow=new $x}dispose(){this.shadow.dispose()}copy(e){return super.copy(e),this.target=e.target.clone(),this.shadow=e.shadow.clone(),this}}class Kx extends qc{constructor(e,t){super(e,t),this.isAmbientLight=!0,this.type="AmbientLight"}}const Nh=new zt;class Zx{constructor(e,t,n=0,r=1/0){this.ray=new Po(e,t),this.near=n,this.far=r,this.camera=null,this.layers=new zc,this.params={Mesh:{},Line:{threshold:1},LOD:{},Points:{threshold:1},Sprite:{}}}set(e,t){this.ray.set(e,t)}setFromCamera(e,t){t.isPerspectiveCamera?(this.ray.origin.setFromMatrixPosition(t.matrixWorld),this.ray.direction.set(e.x,e.y,.5).unproject(t).sub(this.ray.origin).normalize(),this.camera=t):t.isOrthographicCamera?(this.ray.origin.set(e.x,e.y,(t.near+t.far)/(t.near-t.far)).unproject(t),this.ray.direction.set(0,0,-1).transformDirection(t.matrixWorld),this.camera=t):console.error("THREE.Raycaster: Unsupported camera type: "+t.type)}setFromXRController(e){return Nh.identity().extractRotation(e.matrixWorld),this.ray.origin.setFromMatrixPosition(e.matrixWorld),this.ray.direction.set(0,0,-1).applyMatrix4(Nh),this}intersectObject(e,t=!0,n=[]){return xc(e,this,n,t),n.sort(Fh),n}intersectObjects(e,t=!0,n=[]){for(let r=0,s=e.length;r<s;r++)xc(e[r],this,n,t);return n.sort(Fh),n}}function Fh(i,e){return i.distance-e.distance}function xc(i,e,t,n){let r=!0;if(i.layers.test(e.layers)&&i.raycast(e,t)===!1&&(r=!1),r===!0&&n===!0){const s=i.children;for(let a=0,o=s.length;a<o;a++)xc(s[a],e,t,!0)}}class Oh{constructor(e=1,t=0,n=0){return this.radius=e,this.phi=t,this.theta=n,this}set(e,t,n){return this.radius=e,this.phi=t,this.theta=n,this}copy(e){return this.radius=e.radius,this.phi=e.phi,this.theta=e.theta,this}makeSafe(){return this.phi=Math.max(1e-6,Math.min(Math.PI-1e-6,this.phi)),this}setFromVector3(e){return this.setFromCartesianCoords(e.x,e.y,e.z)}setFromCartesianCoords(e,t,n){return this.radius=Math.sqrt(e*e+t*t+n*n),this.radius===0?(this.theta=0,this.phi=0):(this.theta=Math.atan2(e,n),this.phi=Math.acos(pn(t/this.radius,-1,1))),this}clone(){return new this.constructor().copy(this)}}class Jx extends Xc{constructor(e=10,t=10,n=4473924,r=8947848){n=new nt(n),r=new nt(r);const s=t/2,a=e/t,o=e/2,l=[],c=[];for(let d=0,m=0,_=-o;d<=t;d++,_+=a){l.push(-o,0,_,o,0,_),l.push(_,0,-o,_,0,o);const v=d===s?n:r;v.toArray(c,m),m+=3,v.toArray(c,m),m+=3,v.toArray(c,m),m+=3,v.toArray(c,m),m+=3}const u=new gn;u.setAttribute("position",new wn(l,3)),u.setAttribute("color",new wn(c,3));const h=new Cr({vertexColors:!0,toneMapped:!1});super(u,h),this.type="GridHelper"}dispose(){this.geometry.dispose(),this.material.dispose()}}typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("register",{detail:{revision:Pc}}));typeof window<"u"&&(window.__THREE__?console.warn("WARNING: Multiple instances of Three.js being imported."):window.__THREE__=Pc);var Qx=Object.defineProperty,eM=(i,e,t)=>e in i?Qx(i,e,{enumerable:!0,configurable:!0,writable:!0,value:t}):i[e]=t,tM=(i,e,t)=>(eM(i,e+"",t),t);class nM{constructor(){tM(this,"_listeners")}addEventListener(e,t){this._listeners===void 0&&(this._listeners={});const n=this._listeners;n[e]===void 0&&(n[e]=[]),n[e].indexOf(t)===-1&&n[e].push(t)}hasEventListener(e,t){if(this._listeners===void 0)return!1;const n=this._listeners;return n[e]!==void 0&&n[e].indexOf(t)!==-1}removeEventListener(e,t){if(this._listeners===void 0)return;const r=this._listeners[e];if(r!==void 0){const s=r.indexOf(t);s!==-1&&r.splice(s,1)}}dispatchEvent(e){if(this._listeners===void 0)return;const n=this._listeners[e.type];if(n!==void 0){e.target=this;const r=n.slice(0);for(let s=0,a=r.length;s<a;s++)r[s].call(this,e);e.target=null}}}var iM=Object.defineProperty,rM=(i,e,t)=>e in i?iM(i,e,{enumerable:!0,configurable:!0,writable:!0,value:t}):i[e]=t,qe=(i,e,t)=>(rM(i,typeof e!="symbol"?e+"":e,t),t);const Ja=new Po,Bh=new $i,sM=Math.cos(70*(Math.PI/180)),zh=(i,e)=>(i%e+e)%e;class aM extends nM{constructor(e,t){super(),qe(this,"object"),qe(this,"domElement"),qe(this,"enabled",!0),qe(this,"target",new V),qe(this,"minDistance",0),qe(this,"maxDistance",1/0),qe(this,"minZoom",0),qe(this,"maxZoom",1/0),qe(this,"minPolarAngle",0),qe(this,"maxPolarAngle",Math.PI),qe(this,"minAzimuthAngle",-1/0),qe(this,"maxAzimuthAngle",1/0),qe(this,"enableDamping",!1),qe(this,"dampingFactor",.05),qe(this,"enableZoom",!0),qe(this,"zoomSpeed",1),qe(this,"enableRotate",!0),qe(this,"rotateSpeed",1),qe(this,"enablePan",!0),qe(this,"panSpeed",1),qe(this,"screenSpacePanning",!0),qe(this,"keyPanSpeed",7),qe(this,"zoomToCursor",!1),qe(this,"autoRotate",!1),qe(this,"autoRotateSpeed",2),qe(this,"reverseOrbit",!1),qe(this,"reverseHorizontalOrbit",!1),qe(this,"reverseVerticalOrbit",!1),qe(this,"keys",{LEFT:"ArrowLeft",UP:"ArrowUp",RIGHT:"ArrowRight",BOTTOM:"ArrowDown"}),qe(this,"mouseButtons",{LEFT:Wr.ROTATE,MIDDLE:Wr.DOLLY,RIGHT:Wr.PAN}),qe(this,"touches",{ONE:Xr.ROTATE,TWO:Xr.DOLLY_PAN}),qe(this,"target0"),qe(this,"position0"),qe(this,"zoom0"),qe(this,"_domElementKeyEvents",null),qe(this,"getPolarAngle"),qe(this,"getAzimuthalAngle"),qe(this,"setPolarAngle"),qe(this,"setAzimuthalAngle"),qe(this,"getDistance"),qe(this,"getZoomScale"),qe(this,"listenToKeyEvents"),qe(this,"stopListenToKeyEvents"),qe(this,"saveState"),qe(this,"reset"),qe(this,"update"),qe(this,"connect"),qe(this,"dispose"),qe(this,"dollyIn"),qe(this,"dollyOut"),qe(this,"getScale"),qe(this,"setScale"),this.object=e,this.domElement=t,this.target0=this.target.clone(),this.position0=this.object.position.clone(),this.zoom0=this.object.zoom,this.getPolarAngle=()=>u.phi,this.getAzimuthalAngle=()=>u.theta,this.setPolarAngle=N=>{let oe=zh(N,2*Math.PI),I=u.phi;I<0&&(I+=2*Math.PI),oe<0&&(oe+=2*Math.PI);let re=Math.abs(oe-I);2*Math.PI-re<re&&(oe<I?oe+=2*Math.PI:I+=2*Math.PI),h.phi=oe-I,n.update()},this.setAzimuthalAngle=N=>{let oe=zh(N,2*Math.PI),I=u.theta;I<0&&(I+=2*Math.PI),oe<0&&(oe+=2*Math.PI);let re=Math.abs(oe-I);2*Math.PI-re<re&&(oe<I?oe+=2*Math.PI:I+=2*Math.PI),h.theta=oe-I,n.update()},this.getDistance=()=>n.object.position.distanceTo(n.target),this.listenToKeyEvents=N=>{N.addEventListener("keydown",we),this._domElementKeyEvents=N},this.stopListenToKeyEvents=()=>{this._domElementKeyEvents.removeEventListener("keydown",we),this._domElementKeyEvents=null},this.saveState=()=>{n.target0.copy(n.target),n.position0.copy(n.object.position),n.zoom0=n.object.zoom},this.reset=()=>{n.target.copy(n.target0),n.object.position.copy(n.position0),n.object.zoom=n.zoom0,n.object.updateProjectionMatrix(),n.dispatchEvent(r),n.update(),l=o.NONE},this.update=(()=>{const N=new V,oe=new V(0,1,0),I=new Rr().setFromUnitVectors(e.up,oe),re=I.clone().invert(),ne=new V,ie=new Rr,ge=2*Math.PI;return function(){const st=n.object.position;I.setFromUnitVectors(e.up,oe),re.copy(I).invert(),N.copy(st).sub(n.target),N.applyQuaternion(I),u.setFromVector3(N),n.autoRotate&&l===o.NONE&&K(j()),n.enableDamping?(u.theta+=h.theta*n.dampingFactor,u.phi+=h.phi*n.dampingFactor):(u.theta+=h.theta,u.phi+=h.phi);let mt=n.minAzimuthAngle,Et=n.maxAzimuthAngle;isFinite(mt)&&isFinite(Et)&&(mt<-Math.PI?mt+=ge:mt>Math.PI&&(mt-=ge),Et<-Math.PI?Et+=ge:Et>Math.PI&&(Et-=ge),mt<=Et?u.theta=Math.max(mt,Math.min(Et,u.theta)):u.theta=u.theta>(mt+Et)/2?Math.max(mt,u.theta):Math.min(Et,u.theta)),u.phi=Math.max(n.minPolarAngle,Math.min(n.maxPolarAngle,u.phi)),u.makeSafe(),n.enableDamping===!0?n.target.addScaledVector(m,n.dampingFactor):n.target.add(m),n.zoomToCursor&&w||n.object.isOrthographicCamera?u.radius=ve(u.radius):u.radius=ve(u.radius*d),N.setFromSpherical(u),N.applyQuaternion(re),st.copy(n.target).add(N),n.object.matrixAutoUpdate||n.object.updateMatrix(),n.object.lookAt(n.target),n.enableDamping===!0?(h.theta*=1-n.dampingFactor,h.phi*=1-n.dampingFactor,m.multiplyScalar(1-n.dampingFactor)):(h.set(0,0,0),m.set(0,0,0));let at=!1;if(n.zoomToCursor&&w){let ln=null;if(n.object instanceof En&&n.object.isPerspectiveCamera){const Ft=N.length();ln=ve(Ft*d);const Ot=Ft-ln;n.object.position.addScaledVector(D,Ot),n.object.updateMatrixWorld()}else if(n.object.isOrthographicCamera){const Ft=new V(B.x,B.y,0);Ft.unproject(n.object),n.object.zoom=Math.max(n.minZoom,Math.min(n.maxZoom,n.object.zoom/d)),n.object.updateProjectionMatrix(),at=!0;const Ot=new V(B.x,B.y,0);Ot.unproject(n.object),n.object.position.sub(Ot).add(Ft),n.object.updateMatrixWorld(),ln=N.length()}else console.warn("WARNING: OrbitControls.js encountered an unknown camera type - zoom to cursor disabled."),n.zoomToCursor=!1;ln!==null&&(n.screenSpacePanning?n.target.set(0,0,-1).transformDirection(n.object.matrix).multiplyScalar(ln).add(n.object.position):(Ja.origin.copy(n.object.position),Ja.direction.set(0,0,-1).transformDirection(n.object.matrix),Math.abs(n.object.up.dot(Ja.direction))<sM?e.lookAt(n.target):(Bh.setFromNormalAndCoplanarPoint(n.object.up,n.target),Ja.intersectPlane(Bh,n.target))))}else n.object instanceof Ss&&n.object.isOrthographicCamera&&(at=d!==1,at&&(n.object.zoom=Math.max(n.minZoom,Math.min(n.maxZoom,n.object.zoom/d)),n.object.updateProjectionMatrix()));return d=1,w=!1,at||ne.distanceToSquared(n.object.position)>c||8*(1-ie.dot(n.object.quaternion))>c?(n.dispatchEvent(r),ne.copy(n.object.position),ie.copy(n.object.quaternion),at=!1,!0):!1}})(),this.connect=N=>{n.domElement=N,n.domElement.style.touchAction="none",n.domElement.addEventListener("contextmenu",Te),n.domElement.addEventListener("pointerdown",Z),n.domElement.addEventListener("pointercancel",Q),n.domElement.addEventListener("wheel",me)},this.dispose=()=>{var N,oe,I,re,ne,ie;n.domElement&&(n.domElement.style.touchAction="auto"),(N=n.domElement)==null||N.removeEventListener("contextmenu",Te),(oe=n.domElement)==null||oe.removeEventListener("pointerdown",Z),(I=n.domElement)==null||I.removeEventListener("pointercancel",Q),(re=n.domElement)==null||re.removeEventListener("wheel",me),(ne=n.domElement)==null||ne.ownerDocument.removeEventListener("pointermove",ae),(ie=n.domElement)==null||ie.ownerDocument.removeEventListener("pointerup",Q),n._domElementKeyEvents!==null&&n._domElementKeyEvents.removeEventListener("keydown",we)};const n=this,r={type:"change"},s={type:"start"},a={type:"end"},o={NONE:-1,ROTATE:0,DOLLY:1,PAN:2,TOUCH_ROTATE:3,TOUCH_PAN:4,TOUCH_DOLLY_PAN:5,TOUCH_DOLLY_ROTATE:6};let l=o.NONE;const c=1e-6,u=new Oh,h=new Oh;let d=1;const m=new V,_=new Xe,v=new Xe,p=new Xe,f=new Xe,E=new Xe,y=new Xe,T=new Xe,z=new Xe,C=new Xe,D=new V,B=new Xe;let w=!1;const x=[],R={};function j(){return 2*Math.PI/60/60*n.autoRotateSpeed}function O(){return Math.pow(.95,n.zoomSpeed)}function K(N){n.reverseOrbit||n.reverseHorizontalOrbit?h.theta+=N:h.theta-=N}function W(N){n.reverseOrbit||n.reverseVerticalOrbit?h.phi+=N:h.phi-=N}const J=(()=>{const N=new V;return function(I,re){N.setFromMatrixColumn(re,0),N.multiplyScalar(-I),m.add(N)}})(),Y=(()=>{const N=new V;return function(I,re){n.screenSpacePanning===!0?N.setFromMatrixColumn(re,1):(N.setFromMatrixColumn(re,0),N.crossVectors(n.object.up,N)),N.multiplyScalar(I),m.add(N)}})(),ee=(()=>{const N=new V;return function(I,re){const ne=n.domElement;if(ne&&n.object instanceof En&&n.object.isPerspectiveCamera){const ie=n.object.position;N.copy(ie).sub(n.target);let ge=N.length();ge*=Math.tan(n.object.fov/2*Math.PI/180),J(2*I*ge/ne.clientHeight,n.object.matrix),Y(2*re*ge/ne.clientHeight,n.object.matrix)}else ne&&n.object instanceof Ss&&n.object.isOrthographicCamera?(J(I*(n.object.right-n.object.left)/n.object.zoom/ne.clientWidth,n.object.matrix),Y(re*(n.object.top-n.object.bottom)/n.object.zoom/ne.clientHeight,n.object.matrix)):(console.warn("WARNING: OrbitControls.js encountered an unknown camera type - pan disabled."),n.enablePan=!1)}})();function pe(N){n.object instanceof En&&n.object.isPerspectiveCamera||n.object instanceof Ss&&n.object.isOrthographicCamera?d=N:(console.warn("WARNING: OrbitControls.js encountered an unknown camera type - dolly/zoom disabled."),n.enableZoom=!1)}function ue(N){pe(d/N)}function _e(N){pe(d*N)}function be(N){if(!n.zoomToCursor||!n.domElement)return;w=!0;const oe=n.domElement.getBoundingClientRect(),I=N.clientX-oe.left,re=N.clientY-oe.top,ne=oe.width,ie=oe.height;B.x=I/ne*2-1,B.y=-(re/ie)*2+1,D.set(B.x,B.y,1).unproject(n.object).sub(n.object.position).normalize()}function ve(N){return Math.max(n.minDistance,Math.min(n.maxDistance,N))}function te(N){_.set(N.clientX,N.clientY)}function le(N){be(N),T.set(N.clientX,N.clientY)}function xe(N){f.set(N.clientX,N.clientY)}function he(N){v.set(N.clientX,N.clientY),p.subVectors(v,_).multiplyScalar(n.rotateSpeed);const oe=n.domElement;oe&&(K(2*Math.PI*p.x/oe.clientHeight),W(2*Math.PI*p.y/oe.clientHeight)),_.copy(v),n.update()}function Be(N){z.set(N.clientX,N.clientY),C.subVectors(z,T),C.y>0?ue(O()):C.y<0&&_e(O()),T.copy(z),n.update()}function Ve(N){E.set(N.clientX,N.clientY),y.subVectors(E,f).multiplyScalar(n.panSpeed),ee(y.x,y.y),f.copy(E),n.update()}function Ne(N){be(N),N.deltaY<0?_e(O()):N.deltaY>0&&ue(O()),n.update()}function dt(N){let oe=!1;switch(N.code){case n.keys.UP:ee(0,n.keyPanSpeed),oe=!0;break;case n.keys.BOTTOM:ee(0,-n.keyPanSpeed),oe=!0;break;case n.keys.LEFT:ee(n.keyPanSpeed,0),oe=!0;break;case n.keys.RIGHT:ee(-n.keyPanSpeed,0),oe=!0;break}oe&&(N.preventDefault(),n.update())}function U(){if(x.length==1)_.set(x[0].pageX,x[0].pageY);else{const N=.5*(x[0].pageX+x[1].pageX),oe=.5*(x[0].pageY+x[1].pageY);_.set(N,oe)}}function ut(){if(x.length==1)f.set(x[0].pageX,x[0].pageY);else{const N=.5*(x[0].pageX+x[1].pageX),oe=.5*(x[0].pageY+x[1].pageY);f.set(N,oe)}}function tt(){const N=x[0].pageX-x[1].pageX,oe=x[0].pageY-x[1].pageY,I=Math.sqrt(N*N+oe*oe);T.set(0,I)}function ot(){n.enableZoom&&tt(),n.enablePan&&ut()}function Fe(){n.enableZoom&&tt(),n.enableRotate&&U()}function yt(N){if(x.length==1)v.set(N.pageX,N.pageY);else{const I=ke(N),re=.5*(N.pageX+I.x),ne=.5*(N.pageY+I.y);v.set(re,ne)}p.subVectors(v,_).multiplyScalar(n.rotateSpeed);const oe=n.domElement;oe&&(K(2*Math.PI*p.x/oe.clientHeight),W(2*Math.PI*p.y/oe.clientHeight)),_.copy(v)}function Ye(N){if(x.length==1)E.set(N.pageX,N.pageY);else{const oe=ke(N),I=.5*(N.pageX+oe.x),re=.5*(N.pageY+oe.y);E.set(I,re)}y.subVectors(E,f).multiplyScalar(n.panSpeed),ee(y.x,y.y),f.copy(E)}function We(N){const oe=ke(N),I=N.pageX-oe.x,re=N.pageY-oe.y,ne=Math.sqrt(I*I+re*re);z.set(0,ne),C.set(0,Math.pow(z.y/T.y,n.zoomSpeed)),ue(C.y),T.copy(z)}function L(N){n.enableZoom&&We(N),n.enablePan&&Ye(N)}function S(N){n.enableZoom&&We(N),n.enableRotate&&yt(N)}function Z(N){var oe,I;n.enabled!==!1&&(x.length===0&&((oe=n.domElement)==null||oe.ownerDocument.addEventListener("pointermove",ae),(I=n.domElement)==null||I.ownerDocument.addEventListener("pointerup",Q)),Ke(N),N.pointerType==="touch"?je(N):G(N))}function ae(N){n.enabled!==!1&&(N.pointerType==="touch"?fe(N):Ee(N))}function Q(N){var oe,I,re;ze(N),x.length===0&&((oe=n.domElement)==null||oe.releasePointerCapture(N.pointerId),(I=n.domElement)==null||I.ownerDocument.removeEventListener("pointermove",ae),(re=n.domElement)==null||re.ownerDocument.removeEventListener("pointerup",Q)),n.dispatchEvent(a),l=o.NONE}function G(N){let oe;switch(N.button){case 0:oe=n.mouseButtons.LEFT;break;case 1:oe=n.mouseButtons.MIDDLE;break;case 2:oe=n.mouseButtons.RIGHT;break;default:oe=-1}switch(oe){case Wr.DOLLY:if(n.enableZoom===!1)return;le(N),l=o.DOLLY;break;case Wr.ROTATE:if(N.ctrlKey||N.metaKey||N.shiftKey){if(n.enablePan===!1)return;xe(N),l=o.PAN}else{if(n.enableRotate===!1)return;te(N),l=o.ROTATE}break;case Wr.PAN:if(N.ctrlKey||N.metaKey||N.shiftKey){if(n.enableRotate===!1)return;te(N),l=o.ROTATE}else{if(n.enablePan===!1)return;xe(N),l=o.PAN}break;default:l=o.NONE}l!==o.NONE&&n.dispatchEvent(s)}function Ee(N){if(n.enabled!==!1)switch(l){case o.ROTATE:if(n.enableRotate===!1)return;he(N);break;case o.DOLLY:if(n.enableZoom===!1)return;Be(N);break;case o.PAN:if(n.enablePan===!1)return;Ve(N);break}}function me(N){n.enabled===!1||n.enableZoom===!1||l!==o.NONE&&l!==o.ROTATE||(N.preventDefault(),n.dispatchEvent(s),Ne(N),n.dispatchEvent(a))}function we(N){n.enabled===!1||n.enablePan===!1||dt(N)}function je(N){switch(Se(N),x.length){case 1:switch(n.touches.ONE){case Xr.ROTATE:if(n.enableRotate===!1)return;U(),l=o.TOUCH_ROTATE;break;case Xr.PAN:if(n.enablePan===!1)return;ut(),l=o.TOUCH_PAN;break;default:l=o.NONE}break;case 2:switch(n.touches.TWO){case Xr.DOLLY_PAN:if(n.enableZoom===!1&&n.enablePan===!1)return;ot(),l=o.TOUCH_DOLLY_PAN;break;case Xr.DOLLY_ROTATE:if(n.enableZoom===!1&&n.enableRotate===!1)return;Fe(),l=o.TOUCH_DOLLY_ROTATE;break;default:l=o.NONE}break;default:l=o.NONE}l!==o.NONE&&n.dispatchEvent(s)}function fe(N){switch(Se(N),l){case o.TOUCH_ROTATE:if(n.enableRotate===!1)return;yt(N),n.update();break;case o.TOUCH_PAN:if(n.enablePan===!1)return;Ye(N),n.update();break;case o.TOUCH_DOLLY_PAN:if(n.enableZoom===!1&&n.enablePan===!1)return;L(N),n.update();break;case o.TOUCH_DOLLY_ROTATE:if(n.enableZoom===!1&&n.enableRotate===!1)return;S(N),n.update();break;default:l=o.NONE}}function Te(N){n.enabled!==!1&&N.preventDefault()}function Ke(N){x.push(N)}function ze(N){delete R[N.pointerId];for(let oe=0;oe<x.length;oe++)if(x[oe].pointerId==N.pointerId){x.splice(oe,1);return}}function Se(N){let oe=R[N.pointerId];oe===void 0&&(oe=new Xe,R[N.pointerId]=oe),oe.set(N.pageX,N.pageY)}function ke(N){const oe=N.pointerId===x[0].pointerId?x[1]:x[0];return R[oe.pointerId]}this.dollyIn=(N=O())=>{_e(N),n.update()},this.dollyOut=(N=O())=>{ue(N),n.update()},this.getScale=()=>d,this.setScale=N=>{pe(N),n.update()},this.getZoomScale=()=>O(),t!==void 0&&this.connect(t),this.update()}}class oM{constructor(){ye(this,"handlers",new Map);ye(this,"onceHandlers",new Map);ye(this,"messageBuffer",new Map)}register(e,t){if(!this.handlers.has(e)){this.handlers.set(e,new Set);const n=this.messageBuffer.get(e);n&&(n.forEach(r=>Promise.resolve(t(r))),this.messageBuffer.delete(e))}return this.handlers.get(e).add(t),()=>this.unregister(e,t)}once(e,t){return this.onceHandlers.has(e)||this.onceHandlers.set(e,new Set),this.onceHandlers.get(e).add(t),()=>this.unregisterOnce(e,t)}unregister(e,t){var n;(n=this.handlers.get(e))==null||n.delete(t)}unregisterOnce(e,t){var n;(n=this.onceHandlers.get(e))==null||n.delete(t)}buffer(e){const{type:t}=e;this.messageBuffer.has(t)||this.messageBuffer.set(t,[]),this.messageBuffer.get(t).push(e)}async dispatch(e){const{type:t,...n}=e,r=this.handlers.get(t);if(r&&r.size>0){await Promise.all(Array.from(r).map(a=>Promise.resolve(a(n))));return}const s=this.onceHandlers.get(t);if(s&&s.size>0){await Promise.all(Array.from(s).map(a=>Promise.resolve(a(n)))),this.onceHandlers.delete(t);return}this.buffer(e)}clear(){this.handlers.clear(),this.onceHandlers.clear(),this.messageBuffer.clear()}getBuffered(e){return this.messageBuffer.get(e)??[]}hasHandlers(e){var t;return(((t=this.handlers.get(e))==null?void 0:t.size)??0)>0}}class lM{constructor(e,t){ye(this,"ws",null);ye(this,"url");ye(this,"router");ye(this,"reconnectDelay",1e3);ye(this,"maxReconnectDelay",3e4);ye(this,"reconnectAttempts",0);ye(this,"shouldReconnect",!0);ye(this,"state","disconnected");ye(this,"stateListeners",new Set);ye(this,"messageQueue",[]);this.url=e,this.router=t}get connectionState(){return this.state}onStateChange(e){return this.stateListeners.add(e),e(this.state),()=>this.stateListeners.delete(e)}setState(e){this.state!==e&&(this.state=e,this.stateListeners.forEach(t=>t(e)))}connect(){var n;if(((n=this.ws)==null?void 0:n.readyState)===WebSocket.OPEN||this.state==="connecting")return;this.setState("connecting");const t=`${window.location.protocol==="https:"?"wss:":"ws:"}//${window.location.host}${this.url}`;this.ws=new WebSocket(t),this.ws.binaryType="arraybuffer",this.ws.onopen=()=>{console.log("[WS] Connected"),this.reconnectAttempts=0,this.reconnectDelay=1e3,this.setState("connected"),this.flushQueue()},this.ws.onmessage=async r=>{try{const s=JSON.parse(r.data);await this.router.dispatch(s)}catch(s){console.error("[WS] Failed to parse message:",s)}},this.ws.onclose=()=>{console.log("[WS] Disconnected"),this.setState("disconnected"),this.shouldReconnect&&this.scheduleReconnect()},this.ws.onerror=r=>{console.error("[WS] Error:",r)}}scheduleReconnect(){if(this.state==="reconnecting")return;this.setState("reconnecting");const e=Math.min(this.reconnectDelay*Math.pow(1.5,this.reconnectAttempts),this.maxReconnectDelay);this.reconnectAttempts++,console.log(`[WS] Reconnecting in ${e}ms (attempt ${this.reconnectAttempts})`),setTimeout(()=>this.connect(),e)}send(e){var t;((t=this.ws)==null?void 0:t.readyState)===WebSocket.OPEN?this.ws.send(JSON.stringify(e)):this.messageQueue.push(e)}flushQueue(){var e;for(;this.messageQueue.length>0&&((e=this.ws)==null?void 0:e.readyState)===WebSocket.OPEN;){const t=this.messageQueue.shift();this.ws.send(JSON.stringify(t))}}disconnect(){var e;this.shouldReconnect=!1,(e=this.ws)==null||e.close(),this.ws=null,this.setState("disconnected")}async waitForConnection(e=1e4){return this.state==="connected"?!0:new Promise(t=>{const n=setTimeout(()=>{r(),t(!1)},e),r=this.onStateChange(s=>{s==="connected"&&(clearTimeout(n),r(),t(!0))})})}get isConnected(){var e;return((e=this.ws)==null?void 0:e.readyState)===WebSocket.OPEN}}const mn=new oM,Eo=new lM("/ws",mn);let cf=null;function cM(i){cf=i}function uM(){return cf}class hM{constructor(){ye(this,"components",new Map);ye(this,"initialized",!1)}register(e){const t=e.name||e.constructor.name;this.components.has(t)&&console.warn(`[ComponentRegistry] Component "${t}" already registered, replacing`),this.components.set(t,e),this.initialized&&e.init().catch(console.error)}unregister(e){const t=this.components.get(e);t&&(t.destroy().catch(console.error),this.components.delete(e))}async initAll(){this.initialized=!0;for(const[e,t]of this.components)try{await t.init(),console.log(`[ComponentRegistry] Initialized: ${e}`)}catch(n){console.error(`[ComponentRegistry] Failed to initialize ${e}:`,n)}}async destroyAll(){for(const[e,t]of this.components)try{await t.destroy(),console.log(`[ComponentRegistry] Destroyed: ${e}`)}catch(n){console.error(`[ComponentRegistry] Failed to destroy ${e}:`,n)}this.components.clear(),this.initialized=!1}get(e){return this.components.get(e)}list(){return Array.from(this.components.keys())}}const Pr=new hM;typeof window<"u"&&(document.addEventListener("DOMContentLoaded",()=>{Pr.initAll().catch(console.error)}),window.addEventListener("beforeunload",()=>{Pr.destroyAll().catch(console.error)}));const br={gradient:"#58a6ff",pepita:"#d4a843",random_projections:"#f78166",local_goodness:"#a371f7",thermodynamic_contrast:"#3fb950",contrastive:"#ff7b72",hebbian:"#79c0ff",predictive:"#d2a8ff"},Ue={border:"#2a3a4a",text_secondary:"#8b98a8",text_muted:"#5a6a7a",gradient:"#58a6ff",legal_unmeasured:"#58a6ff",void:"#f85149",pareto:"#a371f7",chance_line:"#f85149",gpu:"#58a6ff",cpu:"#3fb950",memory:"#d29922",ok:"#3fb950",warn:"#d29922",error:"#f85149",passed:"#3fb950",insufficient:"#d29922",rejected:"#f85149"};function co(i){return i.length===0?0:i.reduce((e,t)=>e+t,0)/i.length}function dM(i){if(i.length<2)return 0;const e=co(i),t=i.reduce((n,r)=>n+(r-e)**2,0)/(i.length-1);return Math.sqrt(t)}class fM{constructor(){ye(this,"name","DiscoveryMap");ye(this,"scene",new Wc);ye(this,"camera",new kc);ye(this,"renderer",null);ye(this,"cells",new Map);ye(this,"cellDataMap",new Map);ye(this,"axes",{x:"credit",y:"geometry",z:"dynamics"});ye(this,"xValues",[]);ye(this,"yValues",[]);ye(this,"zValues",[]);ye(this,"cellSize",.8);ye(this,"spacing",1.1);ye(this,"raycaster",new Zx);ye(this,"mouse",new Xe);ye(this,"selectedCell",null);ye(this,"hoveredCell",null);ye(this,"legendElement",null);ye(this,"axisLabelMeshes",[]);ye(this,"initialized",!1);ye(this,"onQueueUpdate",e=>{e.campaigns});ye(this,"onCampaignMetrics",e=>{var s;const{data:t}=e;if(!((s=t==null?void 0:t.records)!=null&&s.length))return;const n=new Map;t.records.forEach((a,o)=>{var d;const l=a.coordinate;if(!l)return;const c=`${l.credit}|${l.geometry}|${l.dynamics}`;let u=n.get(c);u||(u={acc:[],walltime:[],params:[],pareto:!1},n.set(c,u));const h=a.payload??{};typeof h.val_acc=="number"&&u.acc.push(h.val_acc),typeof h.walltime_s=="number"&&u.walltime.push(h.walltime_s),typeof h.param_count=="number"&&u.params.push(h.param_count),(d=t.pareto)!=null&&d[o]&&(u.pareto=!0)});const r=t.required_seeds;n.forEach((a,o)=>{const l=this.cellDataMap.get(o);l&&(l.status="measured",l.metrics={val_acc:co(a.acc),val_acc_std:dM(a.acc),walltime_s:co(a.walltime),param_count:co(a.params),n_seeds:a.acc.length},l.requiredSeeds=r,this.updateCellVisual(o,l,a.pareto))})});mn.register("queue_update",this.onQueueUpdate),mn.register("campaign_metrics",this.onCampaignMetrics)}async init(){const e=uM();e&&(this.scene=e.scene,this.camera=e.camera,this.renderer=e.renderer),this.setupInteraction(),this.xValues=["gradient","random_projections","pepita","local_goodness"],this.yValues=["feedforward"],this.zValues=["instantaneous"],this.createLegend(),this.buildGrid(),console.log("[DiscoveryMap] Initialized")}async destroy(){var e;mn.unregister("queue_update",this.onQueueUpdate),mn.unregister("campaign_metrics",this.onCampaignMetrics),this.clearGrid(),(e=this.legendElement)==null||e.remove()}setupInteraction(){var t;const e=(t=this.renderer)==null?void 0:t.domElement;e&&(e.addEventListener("mousemove",n=>{const r=e.getBoundingClientRect();this.mouse.x=(n.clientX-r.left)/r.width*2-1,this.mouse.y=-((n.clientY-r.top)/r.height)*2+1}),e.addEventListener("click",()=>{this.hoveredCell&&this.selectCell(this.hoveredCell)}))}createLegend(){const e=document.getElementById("ui-overlay");e&&(this.legendElement=document.createElement("div"),this.legendElement.id="discovery-legend",this.legendElement.style.cssText=`
      position: fixed;
      bottom: 140px;
      left: 20px;
      background: var(--bg-secondary);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px;
      font-size: 12px;
      z-index: 100;
      min-width: 200px;
    `,this.legendElement.innerHTML=`
      <div style="font-weight: 600; margin-bottom: 12px; color: var(--text-primary);">Discovery Map</div>
      <div style="display: flex; flex-direction: column; gap: 8px;">
        <div class="legend-item" style="display: flex; align-items: center; gap: 8px;">
          <div style="width: 16px; height: 16px; background: var(--measured); border-radius: 3px; box-shadow: 0 0 8px var(--measured);"></div>
          <span>Measured (glowing pillar)</span>
        </div>
        <div class="legend-item" style="display: flex; align-items: center; gap: 8px;">
          <div style="width: 16px; height: 16px; background: transparent; border: 2px solid var(--legal-unmeasured); border-radius: 3px;"></div>
          <span>Legal / Unmeasured</span>
        </div>
        <div class="legend-item" style="display: flex; align-items: center; gap: 8px;">
          <svg width="16" height="16" viewBox="0 0 16 16"><line x1="3" y1="3" x2="13" y2="13" stroke="var(--void)" stroke-width="2"/><line x1="13" y1="3" x2="3" y2="13" stroke="var(--void)" stroke-width="2"/></svg>
          <span>Void (invalid combination)</span>
        </div>
      </div>
      <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--border);">
        <div style="font-weight: 600; margin-bottom: 8px;">Arms</div>
        <div id="legend-arms" style="display: flex; flex-wrap: wrap; gap: 6px;"></div>
      </div>
      <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--border);">
        <div style="font-weight: 600; margin-bottom: 8px;">Axes</div>
        <div id="legend-axes" style="font-size: 11px; color: var(--text-secondary);"></div>
      </div>
    `,e.appendChild(this.legendElement),this.updateLegendArms(),this.updateLegendAxes())}updateLegendArms(){var t;const e=(t=this.legendElement)==null?void 0:t.querySelector("#legend-arms");e&&(e.innerHTML=this.xValues.map(n=>{const r=br[n]||Ue.gradient;return`<span style="display: inline-flex; align-items: center; gap: 4px; padding: 2px 8px; background: ${r}22; border: 1px solid ${r}88; border-radius: 12px; color: ${r}; font-size: 11px;">${n}</span>`}).join(""))}updateLegendAxes(){var t;const e=(t=this.legendElement)==null?void 0:t.querySelector("#legend-axes");e&&(e.textContent=`X: ${this.axes.x} (${this.xValues.join(", ")}) | Y: ${this.axes.y} (${this.yValues.join(", ")}) | Z: ${this.axes.z} (${this.zValues.join(", ")})`)}buildGrid(){this.clearGrid(),this.createAxisLabels(),this.yValues.forEach((e,t)=>{this.zValues.forEach((n,r)=>{this.xValues.forEach((s,a)=>{const o=`${s}|${e}|${n}`,l={coordinate:{credit:s,geometry:e,dynamics:n},status:"legal"};this.cellDataMap.set(o,l),this.createCell(o,l,a,t,r)})})})}createAxisLabels(){this.axisLabelMeshes.forEach(r=>this.scene.remove(r)),this.axisLabelMeshes=[];const e=new of({color:9148584,sizeAttenuation:!0});this.xValues.forEach((r,s)=>{const a=(s-(this.xValues.length-1)/2)*this.spacing,o=this.createTextSprite(r,.3,e);o.position.set(a,-.06,.72),this.scene.add(o),this.axisLabelMeshes.push(o)});const t=this.createTextSprite(this.axes.y,.28,e);t.position.set(0,3.5,0),this.scene.add(t),this.axisLabelMeshes.push(t);const n=this.createTextSprite(this.axes.z,.28,e);n.position.set((this.xValues.length-1)/2*this.spacing+1.7,-.06,.72),this.scene.add(n),this.axisLabelMeshes.push(n)}createTextSprite(e,t,n){const r=document.createElement("canvas"),s=r.getContext("2d"),a=64;s.font=`bold ${a}px "JetBrains Mono", monospace`;const o=Math.ceil(s.measureText(e).width)+16;r.width=Math.max(64,o),r.height=96,s.font=`bold ${a}px "JetBrains Mono", monospace`,s.fillStyle="#8b98a8",s.textAlign="center",s.textBaseline="middle",s.fillText(e,r.width/2,r.height/2);const l=new Gx(r);l.needsUpdate=!0;const c=n.clone();c.map=l,c.transparent=!0;const u=new Vx(c),h=r.width/r.height;return u.scale.set(t*h,t,1),u}createCell(e,t,n,r,s){const a=(n-(this.xValues.length-1)/2)*this.spacing,o=r*this.spacing,l=(s-(this.zValues.length-1)/2)*this.spacing;let c;switch(t.status){case"measured":c=this.createMeasuredCell(t);break;case"legal":c=this.createLegalCell();break;case"void":c=this.createVoidCell();break;default:c=this.createLegalCell()}c.position.set(a,o,l),c.userData={cellKey:e},this.scene.add(c),this.cells.set(e,c)}createMeasuredCell(e){var u;const t=oo.lerp(.4,3.4,((u=e.metrics)==null?void 0:u.val_acc)??0),n=br[e.coordinate.credit]||Ue.gradient,r=new Qi(this.cellSize,t,this.cellSize);r.translate(0,t/2,0);const s=new Pl({color:new nt(n),emissive:new nt(n),emissiveIntensity:.5,transparent:!0,opacity:.9,metalness:.3,roughness:.4}),a=new Rn(r,s);a.castShadow=!0,a.receiveShadow=!0;const o=new Qi(this.cellSize*1.1,t*1.1,this.cellSize*1.1);o.translate(0,t/2,0);const l=new vo({color:new nt(n),transparent:!0,opacity:.15,depthWrite:!1}),c=new Rn(o,l);return a.add(c),a.userData.glow=c,a}createLegalCell(){const e=new Qi(this.cellSize,this.cellSize,this.cellSize),t=new Wx(e);t.translate(0,this.cellSize/2,0);const n=new Cr({color:Ue.legal_unmeasured,transparent:!0,opacity:.4});return new Xc(t,n)}createVoidCell(){const e=new gn,t=this.cellSize*.6,n=new Float32Array([-t,0,-t,t,0,t,t,0,-t,-t,0,t]);e.setAttribute("position",new Xn(n,3));const r=new Cr({color:Ue.void,linewidth:3}),s=new yo(e,r);return s.position.y=.1,s}clearGrid(){this.cells.forEach(e=>{this.scene.remove(e),e.geometry.dispose(),Array.isArray(e.material)?e.material.forEach(t=>t.dispose()):e.material.dispose()}),this.cells.clear(),this.cellDataMap.clear()}updateCellVisual(e,t,n){const r=this.cells.get(e);if(!r)return;const s=r.position.clone(),a=r.userData.glow;a&&r.remove(a),this.scene.remove(r),r.geometry.dispose(),Array.isArray(r.material)?r.material.forEach(l=>l.dispose()):r.material.dispose();const o=this.createMeasuredCell(t);if(o.position.copy(s),n){const l=new Yc(this.cellSize*.6,this.cellSize*.8,32),c=new vo({color:Ue.pareto,side:mi,transparent:!0,opacity:.6}),u=new Rn(l,c);u.rotation.x=-Math.PI/2,u.position.y=.05,o.add(u),o.userData.paretoRing=u}this.scene.add(o),this.cells.set(e,o)}selectCell(e){this.selectedCell=e;const t=this.cellDataMap.get(e);t&&window.dispatchEvent(new CustomEvent("cell-selected",{detail:t}))}update(e){var n;this.cells.forEach((r,s)=>{const a=this.cellDataMap.get(s);if((a==null?void 0:a.status)==="measured"&&r instanceof Rn&&r.material instanceof Pl){const o=r.userData.glow;o&&(o.material.opacity=.1+.1*Math.sin(Date.now()*.003));const l=r.userData.paretoRing;l&&(l.material.opacity=.4+.2*Math.sin(Date.now()*.005))}}),this.raycaster.setFromCamera(this.mouse,this.camera);const t=this.raycaster.intersectObjects(Array.from(this.cells.values()),!0);if(t.length>0){const r=t[0].object,s=r.userData.cellKey||((n=r.parent)==null?void 0:n.userData.cellKey);s&&s!==this.hoveredCell&&(this.hoveredCell=s,this.highlightCell(s,!0))}else this.hoveredCell&&(this.highlightCell(this.hoveredCell,!1),this.hoveredCell=null)}highlightCell(e,t){const n=this.cells.get(e);n&&n instanceof Rn&&n.material instanceof Pl&&(t?(n.userData.originalEmissive=n.material.emissiveIntensity,n.material.emissiveIntensity=(n.userData.originalEmissive||.5)+.5):n.userData.originalEmissive!==void 0&&(n.material.emissiveIntensity=n.userData.originalEmissive))}}const $c=new fM;Pr.register($c);class pM{constructor(){ye(this,"name","CellDrawer");ye(this,"panel",null);ye(this,"content",null);ye(this,"sparklineScene",null);ye(this,"sparklineRenderer",null);ye(this,"sparklineCamera",null);ye(this,"sparklineAnimationId",null);ye(this,"currentData",null);ye(this,"onCellSelected",e=>{this.show(e.detail)})}async init(){this.createPanel(),this.setupEvents(),console.log("[CellDrawer] Initialized")}async destroy(){var e;this.stopSparkline(),(e=this.panel)==null||e.remove(),window.removeEventListener("cell-selected",this.onCellSelected)}createPanel(){const e=document.getElementById("ui-overlay");e&&(this.panel=document.createElement("div"),this.panel.id="cell-drawer",this.panel.style.cssText=`
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
    `,e.appendChild(this.panel),this.content=this.panel.querySelector("#drawer-content"),this.panel.querySelector("#drawer-close").addEventListener("click",()=>this.hide()))}setupEvents(){window.addEventListener("cell-selected",this.onCellSelected)}show(e){this.currentData=e,this.renderContent(e),this.panel.style.transform="translateX(0)",this.startSparkline(e)}hide(){this.panel.style.transform="translateX(100%)",this.stopSparkline(),this.currentData=null}renderContent(e){if(!this.content)return;const{coordinate:t,metrics:n,status:r}=e,s=br[t.credit]||Ue.gradient,a=(n==null?void 0:n.val_acc)??0,o=(n==null?void 0:n.n_seeds)??0,l=.1,c=e.requiredSeeds??0;let u="UNKNOWN",h=Ue.text_secondary;r==="measured"&&(a>l+.1?(u="PASSED",h=Ue.passed):a>l?(u="INSUFFICIENT",h=Ue.insufficient):(u="REJECTED",h=Ue.rejected));const d=r==="measured"&&c>0?Math.max(0,c-o):"N/A";this.content.innerHTML=`
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
        <div style="height: 4px; background: var(--bg); border-radius: 2px; overflow: hidden;">
          <div style="
            width: ${Math.min(100,a/(l*2)*100)}%;
            height: 100%;
            background: linear-gradient(90deg, ${Ue.rejected}, ${Ue.insufficient}, ${Ue.passed});
            border-radius: 2px;
          "></div>
        </div>
      </div>

      ${r==="measured"?`
        <div style="margin-bottom: 20px;">
          <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 8px;">SEEDS TO CLAIM</div>
          <div style="font-size: 24px; font-weight: 700; font-family: 'JetBrains Mono', monospace; color: ${Ue.insufficient};">
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

      <!-- Actions (visual only for v1) -->
      <div style="
        display: flex;
        gap: 8px;
        padding-top: 16px;
        border-top: 1px solid var(--border);
      ">
        <button class="drawer-btn" style="flex: 1;" disabled>Queue Rest</button>
        <button class="drawer-btn" style="flex: 1;" disabled>Preregister</button>
        <button class="drawer-btn" style="flex: 1;" disabled>Adopt as Quest</button>
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
    `,this.content.appendChild(m)}startSparkline(e){const t=document.getElementById("sparkline-container");if(!t)return;this.sparklineScene=new Wc,this.sparklineCamera=new Ss(-1,1,1,-1,.1,10),this.sparklineCamera.position.z=2,this.sparklineRenderer=new af({alpha:!0,antialias:!0}),this.sparklineRenderer.setSize(t.clientWidth,t.clientHeight),this.sparklineRenderer.setPixelRatio(Math.min(window.devicePixelRatio,2)),t.appendChild(this.sparklineRenderer.domElement);const n=10,s=Array.from({length:n},(f,E)=>{const T=.1+E/(n-1)*.3,z=(Math.random()-.5)*.05;return Math.max(.1,Math.min(.95,T+z))}).map((f,E)=>{const y=oo.lerp(-.9,.9,E/(n-1)),T=oo.lerp(-.7,.7,(f-.1)/.85);return new V(y,T,0)}),a=new gn().setFromPoints(s),o=new Cr({color:br[e.coordinate.credit]||Ue.gradient,linewidth:2}),l=new yo(a,o);this.sparklineScene.add(l);const c=oo.lerp(-.7,.7,(.1-.1)/.85),u=new gn().setFromPoints([new V(-.9,c,0),new V(.9,c,0)]),h=new Xx({color:Ue.chance_line,dashSize:.05,gapSize:.03,linewidth:1}),d=new yo(u,h);d.computeLineDistances(),this.sparklineScene.add(d);const m=new gn().setFromPoints([new V(-.9,-.7,0),new V(.9,-.7,0),new V(-.9,-.7,0),new V(-.9,.7,0)]),_=new Cr({color:Ue.border,linewidth:1}),v=new Xc(m,_);this.sparklineScene.add(v);const p=()=>{!this.sparklineRenderer||!this.sparklineScene||!this.sparklineCamera||(this.sparklineRenderer.render(this.sparklineScene,this.sparklineCamera),this.sparklineAnimationId=requestAnimationFrame(p))};p()}stopSparkline(){this.sparklineAnimationId&&(cancelAnimationFrame(this.sparklineAnimationId),this.sparklineAnimationId=null),this.sparklineRenderer&&(this.sparklineRenderer.dispose(),this.sparklineRenderer=null),this.sparklineScene=null,this.sparklineCamera=null}}const uf=new pM;Pr.register(uf);const mM=!0,Qt="u-",gM="uplot",_M=Qt+"hz",vM=Qt+"vt",xM=Qt+"title",MM=Qt+"wrap",SM=Qt+"under",yM=Qt+"over",EM=Qt+"axis",Sr=Qt+"off",bM=Qt+"select",TM=Qt+"cursor-x",wM=Qt+"cursor-y",AM=Qt+"cursor-pt",RM=Qt+"legend",CM=Qt+"live",PM=Qt+"inline",LM=Qt+"series",DM=Qt+"marker",kh=Qt+"label",IM=Qt+"value",na="width",ia="height",Qs="top",Hh="bottom",fs="left",Dl="right",jc="#000",Vh=jc+"0",Il="mousemove",Gh="mousedown",Ul="mouseup",Wh="mouseenter",Xh="mouseleave",Yh="dblclick",UM="resize",NM="scroll",qh="change",bo="dppxchange",Kc="--",Us=typeof window<"u",Mc=Us?document:null,ys=Us?window:null,FM=Us?navigator:null;let xt,Qa;function Sc(){let i=devicePixelRatio;xt!=i&&(xt=i,Qa&&Ec(qh,Qa,Sc),Qa=matchMedia(`(min-resolution: ${xt-.001}dppx) and (max-resolution: ${xt+.001}dppx)`),Tr(qh,Qa,Sc),ys.dispatchEvent(new CustomEvent(bo)))}function Nn(i,e){if(e!=null){let t=i.classList;!t.contains(e)&&t.add(e)}}function yc(i,e){let t=i.classList;t.contains(e)&&t.remove(e)}function Ut(i,e,t){i.style[e]=t+"px"}function Qn(i,e,t,n){let r=Mc.createElement(i);return e!=null&&Nn(r,e),t!=null&&t.insertBefore(r,n),r}function Hn(i,e){return Qn("div",i,e)}const $h=new WeakMap;function di(i,e,t,n,r){let s="translate("+e+"px,"+t+"px)",a=$h.get(i);s!=a&&(i.style.transform=s,$h.set(i,s),e<0||t<0||e>n||t>r?Nn(i,Sr):yc(i,Sr))}const jh=new WeakMap;function Kh(i,e,t){let n=e+t,r=jh.get(i);n!=r&&(jh.set(i,n),i.style.background=e,i.style.borderColor=t)}const Zh=new WeakMap;function Jh(i,e,t,n){let r=e+""+t,s=Zh.get(i);r!=s&&(Zh.set(i,r),i.style.height=t+"px",i.style.width=e+"px",i.style.marginLeft=n?-e/2+"px":0,i.style.marginTop=n?-t/2+"px":0)}const Zc={passive:!0},OM={...Zc,capture:!0};function Tr(i,e,t,n){e.addEventListener(i,t,n?OM:Zc)}function Ec(i,e,t,n){e.removeEventListener(i,t,Zc)}Us&&Sc();function ei(i,e,t,n){let r;t=t||0,n=n||e.length-1;let s=n<=2147483647;for(;n-t>1;)r=s?t+n>>1:Fn((t+n)/2),e[r]<i?t=r:n=r;return i-e[t]<=e[n]-i?t:n}function hf(i){return(t,n,r)=>{let s=-1,a=-1;for(let o=n;o<=r;o++)if(i(t[o])){s=o;break}for(let o=r;o>=n;o--)if(i(t[o])){a=o;break}return[s,a]}}const df=i=>i!=null,ff=i=>i!=null&&i>0,Io=hf(df),BM=hf(ff);function zM(i,e,t,n=0,r=!1){let s=r?BM:Io,a=r?ff:df;[e,t]=s(i,e,t);let o=i[e],l=i[e];if(e>-1)if(n==1)o=i[e],l=i[t];else if(n==-1)o=i[t],l=i[e];else for(let c=e;c<=t;c++){let u=i[c];a(u)&&(u<o?o=u:u>l&&(l=u))}return[o??wt,l??-wt]}function Uo(i,e,t,n){let r=td(i),s=td(e);i==e&&(r==-1?(i*=t,e/=t):(i/=t,e*=t));let a=t==10?Di:pf,o=r==1?Fn:Vn,l=s==1?Vn:Fn,c=o(a($t(i))),u=l(a($t(e))),h=Rs(t,c),d=Rs(t,u);return t==10&&(c<0&&(h=At(h,-c)),u<0&&(d=At(d,-u))),n||t==2?(i=h*r,e=d*s):(i=vf(i,h),e=No(e,d)),[i,e]}function Jc(i,e,t,n){let r=Uo(i,e,t,n);return i==0&&(r[0]=0),e==0&&(r[1]=0),r}const Qc=.1,Qh={mode:3,pad:Qc},aa={pad:0,soft:null,mode:0},kM={min:aa,max:aa};function To(i,e,t,n){return Fo(t)?ed(i,e,t):(aa.pad=t,aa.soft=n?0:null,aa.mode=n?3:0,ed(i,e,kM))}function _t(i,e){return i??e}function HM(i,e,t){for(e=_t(e,0),t=_t(t,i.length-1);e<=t;){if(i[e]!=null)return!0;e++}return!1}function ed(i,e,t){let n=t.min,r=t.max,s=_t(n.pad,0),a=_t(r.pad,0),o=_t(n.hard,-wt),l=_t(r.hard,wt),c=_t(n.soft,wt),u=_t(r.soft,-wt),h=_t(n.mode,0),d=_t(r.mode,0),m=e-i,_=Di(m),v=bn($t(i),$t(e)),p=Di(v),f=$t(p-_);(m<1e-24||f>10)&&(m=0,(i==0||e==0)&&(m=1e-24,h==2&&c!=wt&&(s=0),d==2&&u!=-wt&&(a=0)));let E=m||v||1e3,y=Di(E),T=Rs(10,Fn(y)),z=E*(m==0?i==0?.1:1:s),C=At(vf(i-z,T/10),24),D=i>=c&&(h==1||h==3&&C<=c||h==2&&C>=c)?c:wt,B=bn(o,C<D&&i>=D?D:ii(D,C)),w=E*(m==0?e==0?.1:1:a),x=At(No(e+w,T/10),24),R=e<=u&&(d==1||d==3&&x>=u||d==2&&x<=u)?u:-wt,j=ii(l,x>R&&e<=R?R:bn(R,x));return B==j&&B==0&&(j=100),[B,j]}const VM=new Intl.NumberFormat(Us?FM.language:"en-US"),eu=i=>VM.format(i),On=Math,uo=On.PI,$t=On.abs,Fn=On.floor,qt=On.round,Vn=On.ceil,ii=On.min,bn=On.max,Rs=On.pow,td=On.sign,Di=On.log10,pf=On.log2,GM=(i,e=1)=>On.sinh(i)*e,Nl=(i,e=1)=>On.asinh(i/e),wt=1/0;function nd(i){return(Di((i^i>>31)-(i>>31))|0)+1}function bc(i,e,t){return ii(bn(i,e),t)}function mf(i){return typeof i=="function"}function ht(i){return mf(i)?i:()=>i}const WM=()=>{},gf=i=>i,_f=(i,e)=>e,XM=i=>null,id=i=>!0,rd=(i,e)=>i==e,YM=/\.\d*?(?=9{6,}|0{6,})/gm,Lr=i=>{if(Mf(i)||nr.has(i))return i;const e=`${i}`,t=e.match(YM);if(t==null)return i;let n=t[0].length-1;if(e.indexOf("e-")!=-1){let[r,s]=e.split("e");return+`${Lr(r)}e${s}`}return At(i,n)};function _r(i,e){return Lr(At(Lr(i/e))*e)}function No(i,e){return Lr(Vn(Lr(i/e))*e)}function vf(i,e){return Lr(Fn(Lr(i/e))*e)}function At(i,e=0){if(Mf(i))return i;let t=10**e,n=i*t*(1+Number.EPSILON);return qt(n)/t}const nr=new Map;function xf(i){return((""+i).split(".")[1]||"").length}function ua(i,e,t,n){let r=[],s=n.map(xf);for(let a=e;a<t;a++){let o=$t(a),l=At(Rs(i,a),o);for(let c=0;c<n.length;c++){let u=i==10?+`${n[c]}e${a}`:n[c]*l,h=(a>=0?0:o)+(a>=s[c]?0:s[c]),d=i==10?u:At(u,h);r.push(d),nr.set(d,h)}}return r}const oa={},tu=[],Cs=[null,null],ji=Array.isArray,Mf=Number.isInteger,qM=i=>i===void 0;function sd(i){return typeof i=="string"}function Fo(i){let e=!1;if(i!=null){let t=i.constructor;e=t==null||t==Object}return e}function $M(i){return i!=null&&typeof i=="object"}const jM=Object.getPrototypeOf(Uint8Array),Sf="__proto__";function Ps(i,e=Fo){let t;if(ji(i)){let n=i.find(r=>r!=null);if(ji(n)||e(n)){t=Array(i.length);for(let r=0;r<i.length;r++)t[r]=Ps(i[r],e)}else t=i.slice()}else if(i instanceof jM)t=i.slice();else if(e(i)){t={};for(let n in i)n!=Sf&&(t[n]=Ps(i[n],e))}else t=i;return t}function Yt(i){let e=arguments;for(let t=1;t<e.length;t++){let n=e[t];for(let r in n)r!=Sf&&(Fo(i[r])?Yt(i[r],Ps(n[r])):i[r]=Ps(n[r]))}return i}const KM=0,ZM=1,JM=2;function QM(i,e,t){for(let n=0,r,s=-1;n<e.length;n++){let a=e[n];if(a>s){for(r=a-1;r>=0&&i[r]==null;)i[r--]=null;for(r=a+1;r<t&&i[r]==null;)i[s=r++]=null}}}function eS(i,e){if(iS(i)){let a=i[0].slice();for(let o=1;o<i.length;o++)a.push(...i[o].slice(1));return rS(a[0])||(a=nS(a)),a}let t=new Set;for(let a=0;a<i.length;a++){let l=i[a][0],c=l.length;for(let u=0;u<c;u++)t.add(l[u])}let n=[Array.from(t).sort((a,o)=>a-o)],r=n[0].length,s=new Map;for(let a=0;a<r;a++)s.set(n[0][a],a);for(let a=0;a<i.length;a++){let o=i[a],l=o[0];for(let c=1;c<o.length;c++){let u=o[c],h=Array(r).fill(void 0),d=e?e[a][c]:ZM,m=[];for(let _=0;_<u.length;_++){let v=u[_],p=s.get(l[_]);v===null?d!=KM&&(h[p]=v,d==JM&&m.push(p)):h[p]=v}QM(h,m,r),n.push(h)}}return n}const tS=typeof queueMicrotask>"u"?i=>Promise.resolve().then(i):queueMicrotask;function nS(i){let e=i[0],t=e.length,n=Array(t);for(let s=0;s<n.length;s++)n[s]=s;n.sort((s,a)=>e[s]-e[a]);let r=[];for(let s=0;s<i.length;s++){let a=i[s],o=Array(t);for(let l=0;l<t;l++)o[l]=a[n[l]];r.push(o)}return r}function iS(i){let e=i[0][0],t=e.length;for(let n=1;n<i.length;n++){let r=i[n][0];if(r.length!=t)return!1;if(r!=e){for(let s=0;s<t;s++)if(r[s]!=e[s])return!1}}return!0}function rS(i,e=100){const t=i.length;if(t<=1)return!0;let n=0,r=t-1;for(;n<=r&&i[n]==null;)n++;for(;r>=n&&i[r]==null;)r--;if(r<=n)return!0;const s=bn(1,Fn((r-n+1)/e));for(let a=i[n],o=n+s;o<=r;o+=s){const l=i[o];if(l!=null){if(l<=a)return!1;a=l}}return!0}const yf=["January","February","March","April","May","June","July","August","September","October","November","December"],Ef=["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];function bf(i){return i.slice(0,3)}const sS=Ef.map(bf),aS=yf.map(bf),oS={MMMM:yf,MMM:aS,WWWW:Ef,WWW:sS};function ea(i){return(i<10?"0":"")+i}function lS(i){return(i<10?"00":i<100?"0":"")+i}const cS={YYYY:i=>i.getFullYear(),YY:i=>(i.getFullYear()+"").slice(2),MMMM:(i,e)=>e.MMMM[i.getMonth()],MMM:(i,e)=>e.MMM[i.getMonth()],MM:i=>ea(i.getMonth()+1),M:i=>i.getMonth()+1,DD:i=>ea(i.getDate()),D:i=>i.getDate(),WWWW:(i,e)=>e.WWWW[i.getDay()],WWW:(i,e)=>e.WWW[i.getDay()],HH:i=>ea(i.getHours()),H:i=>i.getHours(),h:i=>{let e=i.getHours();return e==0?12:e>12?e-12:e},AA:i=>i.getHours()>=12?"PM":"AM",aa:i=>i.getHours()>=12?"pm":"am",a:i=>i.getHours()>=12?"p":"a",mm:i=>ea(i.getMinutes()),m:i=>i.getMinutes(),ss:i=>ea(i.getSeconds()),s:i=>i.getSeconds(),fff:i=>lS(i.getMilliseconds())};function nu(i,e){e=e||oS;let t=[],n=/\{([a-z]+)\}|[^{]+/gi,r;for(;r=n.exec(i);)t.push(r[0][0]=="{"?cS[r[1]]:r[0]);return s=>{let a="";for(let o=0;o<t.length;o++)a+=typeof t[o]=="string"?t[o]:t[o](s,e);return a}}const uS=new Intl.DateTimeFormat().resolvedOptions().timeZone;function hS(i,e){let t;return e=="UTC"||e=="Etc/UTC"?t=new Date(+i+i.getTimezoneOffset()*6e4):e==uS?t=i:(t=new Date(i.toLocaleString("en-US",{timeZone:e})),t.setMilliseconds(i.getMilliseconds())),t}const Tf=i=>i%1==0,wo=[1,2,2.5,5],dS=ua(10,-32,0,wo),wf=ua(10,0,32,wo),fS=wf.filter(Tf),vr=dS.concat(wf),iu=`
`,Af="{YYYY}",ad=iu+Af,Rf="{M}/{D}",ra=iu+Rf,eo=ra+"/{YY}",Cf="{aa}",pS="{h}:{mm}",ps=pS+Cf,od=iu+ps,ld=":{ss}",Mt=null;function Pf(i){let e=i*1e3,t=e*60,n=t*60,r=n*24,s=r*30,a=r*365,l=(i==1?ua(10,0,3,wo).filter(Tf):ua(10,-3,0,wo)).concat([e,e*5,e*10,e*15,e*30,t,t*5,t*10,t*15,t*30,n,n*2,n*3,n*4,n*6,n*8,n*12,r,r*2,r*3,r*4,r*5,r*6,r*7,r*8,r*9,r*10,r*15,s,s*2,s*3,s*4,s*6,a,a*2,a*5,a*10,a*25,a*50,a*100]);const c=[[a,Af,Mt,Mt,Mt,Mt,Mt,Mt,1],[r*28,"{MMM}",ad,Mt,Mt,Mt,Mt,Mt,1],[r,Rf,ad,Mt,Mt,Mt,Mt,Mt,1],[n,"{h}"+Cf,eo,Mt,ra,Mt,Mt,Mt,1],[t,ps,eo,Mt,ra,Mt,Mt,Mt,1],[e,ld,eo+" "+ps,Mt,ra+" "+ps,Mt,od,Mt,1],[i,ld+".{fff}",eo+" "+ps,Mt,ra+" "+ps,Mt,od,Mt,1]];function u(h){return(d,m,_,v,p,f)=>{let E=[],y=p>=a,T=p>=s&&p<a,z=h(_),C=At(z*i,3),D=Fl(z.getFullYear(),y?0:z.getMonth(),T||y?1:z.getDate()),B=At(D*i,3);if(T||y){let w=T?p/s:0,x=y?p/a:0,R=C==B?C:At(Fl(D.getFullYear()+x,D.getMonth()+w,1)*i,3),j=new Date(qt(R/i)),O=j.getFullYear(),K=j.getMonth();for(let W=0;R<=v;W++){let J=Fl(O+x*W,K+w*W,1),Y=J-h(At(J*i,3));R=At((+J+Y)*i,3),R<=v&&E.push(R)}}else{let w=p>=r?r:p,x=Fn(_)-Fn(C),R=B+x+No(C-B,w);E.push(R);let j=h(R),O=j.getHours()+j.getMinutes()/t+j.getSeconds()/n,K=p/n,W=d.axes[m]._space,J=f/W;for(;R=At(R+p,i==1?0:3),!(R>v);)if(K>1){let Y=Fn(At(O+K,6))%24,ue=h(R).getHours()-Y;ue>1&&(ue=-1),R-=ue*n,O=(O+K)%24;let _e=E[E.length-1];At((R-_e)/p,3)*J>=.7&&E.push(R)}else E.push(R)}return E}}return[l,c,u]}const[mS,gS,_S]=Pf(1),[vS,xS,MS]=Pf(.001);ua(2,-53,53,[1]);function cd(i,e){return i.map(t=>t.map((n,r)=>r==0||r==8||n==null?n:e(r==1||t[8]==0?n:t[1]+n)))}function ud(i,e){return(t,n,r,s,a)=>{let o=e.find(_=>a>=_[0])||e[e.length-1],l,c,u,h,d,m;return n.map(_=>{let v=i(_),p=v.getFullYear(),f=v.getMonth(),E=v.getDate(),y=v.getHours(),T=v.getMinutes(),z=v.getSeconds(),C=p!=l&&o[2]||f!=c&&o[3]||E!=u&&o[4]||y!=h&&o[5]||T!=d&&o[6]||z!=m&&o[7]||o[1];return l=p,c=f,u=E,h=y,d=T,m=z,C(v)})}}function SS(i,e){let t=nu(e);return(n,r,s,a,o)=>r.map(l=>t(i(l)))}function Fl(i,e,t){return new Date(i,e,t)}function hd(i,e){return e(i)}const yS="{YYYY}-{MM}-{DD} {h}:{mm}{aa}";function dd(i,e){return(t,n,r,s)=>s==null?Kc:e(i(n))}function ES(i,e){let t=i.series[e];return t.width?t.stroke(i,e):t.points.width?t.points.stroke(i,e):null}function bS(i,e){return i.series[e].fill(i,e)}const TS={show:!0,live:!0,isolate:!1,mount:WM,markers:{show:!0,width:2,stroke:ES,fill:bS,dash:"solid"},idx:null,idxs:null,values:[]};function wS(i,e){let t=i.cursor.points,n=Hn(),r=t.size(i,e);Ut(n,na,r),Ut(n,ia,r);let s=r/-2;Ut(n,"marginLeft",s),Ut(n,"marginTop",s);let a=t.width(i,e,r);return a&&Ut(n,"borderWidth",a),n}function AS(i,e){let t=i.series[e].points;return t._fill||t._stroke}function RS(i,e){let t=i.series[e].points;return t._stroke||t._fill}function CS(i,e){return i.series[e].points.size}const Ol=[0,0];function PS(i,e,t){return Ol[0]=e,Ol[1]=t,Ol}function to(i,e,t,n=!0){return r=>{r.button==0&&(!n||r.target==e)&&t(r)}}function Bl(i,e,t,n=!0){return r=>{(!n||r.target==e)&&t(r)}}const LS={show:!0,x:!0,y:!0,lock:!1,move:PS,points:{one:!1,show:wS,size:CS,width:0,stroke:RS,fill:AS},bind:{mousedown:to,mouseup:to,click:to,dblclick:to,mousemove:Bl,mouseleave:Bl,mouseenter:Bl},drag:{setScale:!0,x:!0,y:!1,dist:0,uni:null,click:(i,e)=>{e.stopPropagation(),e.stopImmediatePropagation()},_x:!1,_y:!1},focus:{dist:(i,e,t,n,r)=>n-r,prox:-1,bias:0},hover:{skip:[void 0],prox:null,bias:0},left:-10,top:-10,idx:null,dataIdx:null,idxs:null,event:null},Lf={show:!0,stroke:"rgba(0,0,0,0.07)",width:2},ru=Yt({},Lf,{filter:_f}),Df=Yt({},ru,{size:10}),If=Yt({},Lf,{show:!1}),su='12px system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji"',Uf="bold "+su,Nf=1.5,fd={show:!0,scale:"x",stroke:jc,space:50,gap:5,alignTo:1,size:50,labelGap:0,labelSize:30,labelFont:Uf,side:2,grid:ru,ticks:Df,border:If,font:su,lineGap:Nf,rotate:0},DS="Value",IS="Time",pd={show:!0,scale:"x",auto:!1,sorted:1,min:wt,max:-wt,idxs:[]};function US(i,e,t,n,r){return e.map(s=>s==null?"":eu(s))}function NS(i,e,t,n,r,s,a){let o=[],l=nr.get(r)||0;t=a?t:At(No(t,r),l);for(let c=t;c<=n;c=At(c+r,l))o.push(Object.is(c,-0)?0:c);return o}function Tc(i,e,t,n,r,s,a){const o=[],l=i.scales[i.axes[e].scale].log,c=l==10?Di:pf,u=Fn(c(t));r=Rs(l,u),l==10&&(r=vr[ei(r,vr)]);let h=t,d=r*l;l==10&&(d=vr[ei(d,vr)]);do o.push(h),h=h+r,l==10&&!nr.has(h)&&(h=At(h,nr.get(r))),h>=d&&(r=h,d=r*l,l==10&&(d=vr[ei(d,vr)]));while(h<=n);return o}function FS(i,e,t,n,r,s,a){let l=i.scales[i.axes[e].scale].asinh,c=n>l?Tc(i,e,bn(l,t),n,r):[l],u=n>=0&&t<=0?[0]:[];return(t<-l?Tc(i,e,bn(l,-n),-t,r):[l]).reverse().map(d=>-d).concat(u,c)}const Ff=/./,OS=/[12357]/,BS=/[125]/,md=/1/,wc=(i,e,t,n)=>i.map((r,s)=>e==4&&r==0||s%n==0&&t.test(r.toExponential()[r<0?1:0])?r:null);function zS(i,e,t,n,r){let s=i.axes[t],a=s.scale,o=i.scales[a],l=i.valToPos,c=s._space,u=l(10,a),h=l(9,a)-u>=c?Ff:l(7,a)-u>=c?OS:l(5,a)-u>=c?BS:md;if(h==md){let d=$t(l(1,a)-u);if(d<c)return wc(e.slice().reverse(),o.distr,h,Vn(c/d)).reverse()}return wc(e,o.distr,h,1)}function kS(i,e,t,n,r){let s=i.axes[t],a=s.scale,o=s._space,l=i.valToPos,c=$t(l(1,a)-l(2,a));return c<o?wc(e.slice().reverse(),3,Ff,Vn(o/c)).reverse():e}function HS(i,e,t,n){return n==null?Kc:e==null?"":eu(e)}const gd={show:!0,scale:"y",stroke:jc,space:30,gap:5,alignTo:1,size:50,labelGap:0,labelSize:30,labelFont:Uf,side:3,grid:ru,ticks:Df,border:If,font:su,lineGap:Nf,rotate:0};function VS(i,e){let t=3+(i||1)*2;return At(t*e,3)}function GS(i,e){let{scale:t,idxs:n}=i.series[0],r=i._data[0],s=i.valToPos(r[n[0]],t,!0),a=i.valToPos(r[n[1]],t,!0),o=$t(a-s),l=i.series[e],c=o/(l.points.space*xt);return n[1]-n[0]<=c}const _d={scale:null,auto:!0,sorted:0,min:wt,max:-wt},Of=(i,e,t,n,r)=>r,vd={show:!0,auto:!0,sorted:0,gaps:Of,alpha:1,facets:[Yt({},_d,{scale:"x"}),Yt({},_d,{scale:"y"})]},xd={scale:"y",auto:!0,sorted:0,show:!0,spanGaps:!1,gaps:Of,alpha:1,points:{show:GS,filter:null},values:null,min:wt,max:-wt,idxs:[],path:null,clip:null};function WS(i,e,t,n,r){return t/10}const Bf={time:mM,auto:!0,distr:1,log:10,asinh:1,min:null,max:null,dir:1,ori:0},XS=Yt({},Bf,{time:!1,ori:1}),Md={};function zf(i,e){let t=Md[i];return t||(t={key:i,plots:[],sub(n){t.plots.push(n)},unsub(n){t.plots=t.plots.filter(r=>r!=n)},pub(n,r,s,a,o,l,c){for(let u=0;u<t.plots.length;u++)t.plots[u]!=r&&t.plots[u].pub(n,r,s,a,o,l,c)}},i!=null&&(Md[i]=t)),t}const Ls=1,Ac=2;function Ir(i,e,t){const n=i.mode,r=i.series[e],s=n==2?i._data[e]:i._data,a=i.scales,o=i.bbox;let l=s[0],c=n==2?s[1]:s[e],u=n==2?a[r.facets[0].scale]:a[i.series[0].scale],h=n==2?a[r.facets[1].scale]:a[r.scale],d=o.left,m=o.top,_=o.width,v=o.height,p=i.valToPosH,f=i.valToPosV;return u.ori==0?t(r,l,c,u,h,p,f,d,m,_,v,Bo,Ns,ko,Hf,Gf):t(r,l,c,u,h,f,p,m,d,v,_,zo,Fs,lu,Vf,Wf)}function au(i,e){let t=0,n=0,r=_t(i.bands,tu);for(let s=0;s<r.length;s++){let a=r[s];a.series[0]==e?t=a.dir:a.series[1]==e&&(a.dir==1?n|=1:n|=2)}return[t,n==1?-1:n==2?1:n==3?2:0]}function YS(i,e,t,n,r){let s=i.mode,a=i.series[e],o=s==2?a.facets[1].scale:a.scale,l=i.scales[o];return r==-1?l.min:r==1?l.max:l.distr==3?l.dir==1?l.min:l.max:0}function Ii(i,e,t,n,r,s){return Ir(i,e,(a,o,l,c,u,h,d,m,_,v,p)=>{let f=a.pxRound;const E=c.dir*(c.ori==0?1:-1),y=c.ori==0?Ns:Fs;let T,z;E==1?(T=t,z=n):(T=n,z=t);let C=f(h(o[T],c,v,m)),D=f(d(l[T],u,p,_)),B=f(h(o[z],c,v,m)),w=f(d(s==1?u.max:u.min,u,p,_)),x=new Path2D(r);return y(x,B,w),y(x,C,w),y(x,C,D),x})}function Oo(i,e,t,n,r,s){let a=null;if(i.length>0){a=new Path2D;const o=e==0?ko:lu;let l=t;for(let h=0;h<i.length;h++){let d=i[h];if(d[1]>d[0]){let m=d[0]-l;m>0&&o(a,l,n,m,n+s),l=d[1]}}let c=t+r-l,u=10;c>0&&o(a,l,n-u/2,c,n+s+u)}return a}function qS(i,e,t){let n=i[i.length-1];n&&n[0]==e?n[1]=t:i.push([e,t])}function ou(i,e,t,n,r,s,a){let o=[],l=i.length;for(let c=r==1?t:n;c>=t&&c<=n;c+=r)if(e[c]===null){let h=c,d=c;if(r==1)for(;++c<=n&&e[c]===null;)d=c;else for(;--c>=t&&e[c]===null;)d=c;let m=s(i[h]),_=d==h?m:s(i[d]),v=h-r;m=a<=0&&v>=0&&v<l?s(i[v]):m;let f=d+r;_=a>=0&&f>=0&&f<l?s(i[f]):_,_>=m&&o.push([m,_])}return o}function Sd(i){return i==0?gf:i==1?qt:e=>_r(e,i)}function kf(i){let e=i==0?Bo:zo,t=i==0?(r,s,a,o,l,c)=>{r.arcTo(s,a,o,l,c)}:(r,s,a,o,l,c)=>{r.arcTo(a,s,l,o,c)},n=i==0?(r,s,a,o,l)=>{r.rect(s,a,o,l)}:(r,s,a,o,l)=>{r.rect(a,s,l,o)};return(r,s,a,o,l,c=0,u=0)=>{c==0&&u==0?n(r,s,a,o,l):(c=ii(c,o/2,l/2),u=ii(u,o/2,l/2),e(r,s+c,a),t(r,s+o,a,s+o,a+l,c),t(r,s+o,a+l,s,a+l,u),t(r,s,a+l,s,a,u),t(r,s,a,s+o,a,c),r.closePath())}}const Bo=(i,e,t)=>{i.moveTo(e,t)},zo=(i,e,t)=>{i.moveTo(t,e)},Ns=(i,e,t)=>{i.lineTo(e,t)},Fs=(i,e,t)=>{i.lineTo(t,e)},ko=kf(0),lu=kf(1),Hf=(i,e,t,n,r,s)=>{i.arc(e,t,n,r,s)},Vf=(i,e,t,n,r,s)=>{i.arc(t,e,n,r,s)},Gf=(i,e,t,n,r,s,a)=>{i.bezierCurveTo(e,t,n,r,s,a)},Wf=(i,e,t,n,r,s,a)=>{i.bezierCurveTo(t,e,r,n,a,s)};function Xf(i){return(e,t,n,r,s)=>Ir(e,t,(a,o,l,c,u,h,d,m,_,v,p)=>{let{pxRound:f,points:E}=a,y,T;c.ori==0?(y=Bo,T=Hf):(y=zo,T=Vf);const z=At(E.width*xt,3);let C=(E.size-E.width)/2*xt,D=At(C*2,3),B=new Path2D,w=new Path2D,{left:x,top:R,width:j,height:O}=e.bbox;ko(w,x-D,R-D,j+D*2,O+D*2);const K=W=>{if(l[W]!=null){let J=f(h(o[W],c,v,m)),Y=f(d(l[W],u,p,_));y(B,J+C,Y),T(B,J,Y,C,0,uo*2)}};if(s)s.forEach(K);else for(let W=n;W<=r;W++)K(W);return{stroke:z>0?B:null,fill:B,clip:w,flags:Ls|Ac}})}function Yf(i){return(e,t,n,r,s,a)=>{n!=r&&(s!=n&&a!=n&&i(e,t,n),s!=r&&a!=r&&i(e,t,r),i(e,t,a))}}const $S=Yf(Ns),jS=Yf(Fs);function qf(i){const e=_t(i==null?void 0:i.alignGaps,0);return(t,n,r,s)=>Ir(t,n,(a,o,l,c,u,h,d,m,_,v,p)=>{[r,s]=Io(l,r,s);let f=a.pxRound,E=O=>f(h(O,c,v,m)),y=O=>f(d(O,u,p,_)),T,z;c.ori==0?(T=Ns,z=$S):(T=Fs,z=jS);const C=c.dir*(c.ori==0?1:-1),D={stroke:new Path2D,fill:null,clip:null,band:null,gaps:null,flags:Ls},B=D.stroke;let w=!1;if(s-r>=v*4){let O=ve=>t.posToVal(ve,c.key,!0),K=null,W=null,J,Y,ee,pe=E(o[C==1?r:s]),ue=E(o[r]),_e=E(o[s]),be=O(C==1?ue+1:_e-1);for(let ve=C==1?r:s;ve>=r&&ve<=s;ve+=C){let te=o[ve],xe=(C==1?te<be:te>be)?pe:E(te),he=l[ve];xe==pe?he!=null?(Y=he,K==null?(T(B,xe,y(Y)),J=K=W=Y):Y<K?K=Y:Y>W&&(W=Y)):he===null&&(w=!0):(K!=null&&z(B,pe,y(K),y(W),y(J),y(Y)),he!=null?(Y=he,T(B,xe,y(Y)),K=W=J=Y):(K=W=null,he===null&&(w=!0)),pe=xe,be=O(pe+C))}K!=null&&K!=W&&ee!=pe&&z(B,pe,y(K),y(W),y(J),y(Y))}else for(let O=C==1?r:s;O>=r&&O<=s;O+=C){let K=l[O];K===null?w=!0:K!=null&&T(B,E(o[O]),y(K))}let[R,j]=au(t,n);if(a.fill!=null||R!=0){let O=D.fill=new Path2D(B),K=a.fillTo(t,n,a.min,a.max,R),W=y(K),J=E(o[r]),Y=E(o[s]);C==-1&&([Y,J]=[J,Y]),T(O,Y,W),T(O,J,W)}if(!a.spanGaps){let O=[];w&&O.push(...ou(o,l,r,s,C,E,e)),D.gaps=O=a.gaps(t,n,r,s,O),D.clip=Oo(O,c.ori,m,_,v,p)}return j!=0&&(D.band=j==2?[Ii(t,n,r,s,B,-1),Ii(t,n,r,s,B,1)]:Ii(t,n,r,s,B,j)),D})}function KS(i){const e=_t(i.align,1),t=_t(i.ascDesc,!1),n=_t(i.alignGaps,0),r=_t(i.extend,!1);return(s,a,o,l)=>Ir(s,a,(c,u,h,d,m,_,v,p,f,E,y)=>{[o,l]=Io(h,o,l);let T=c.pxRound,{left:z,width:C}=s.bbox,D=ue=>T(_(ue,d,E,p)),B=ue=>T(v(ue,m,y,f)),w=d.ori==0?Ns:Fs;const x={stroke:new Path2D,fill:null,clip:null,band:null,gaps:null,flags:Ls},R=x.stroke,j=d.dir*(d.ori==0?1:-1);let O=B(h[j==1?o:l]),K=D(u[j==1?o:l]),W=K,J=K;r&&e==-1&&(J=z,w(R,J,O)),w(R,K,O);for(let ue=j==1?o:l;ue>=o&&ue<=l;ue+=j){let _e=h[ue];if(_e==null)continue;let be=D(u[ue]),ve=B(_e);e==1?w(R,be,O):w(R,W,ve),w(R,be,ve),O=ve,W=be}let Y=W;r&&e==1&&(Y=z+C,w(R,Y,O));let[ee,pe]=au(s,a);if(c.fill!=null||ee!=0){let ue=x.fill=new Path2D(R),_e=c.fillTo(s,a,c.min,c.max,ee),be=B(_e);w(ue,Y,be),w(ue,J,be)}if(!c.spanGaps){let ue=[];ue.push(...ou(u,h,o,l,j,D,n));let _e=c.width*xt/2,be=t||e==1?_e:-_e,ve=t||e==-1?-_e:_e;ue.forEach(te=>{te[0]+=be,te[1]+=ve}),x.gaps=ue=c.gaps(s,a,o,l,ue),x.clip=Oo(ue,d.ori,p,f,E,y)}return pe!=0&&(x.band=pe==2?[Ii(s,a,o,l,R,-1),Ii(s,a,o,l,R,1)]:Ii(s,a,o,l,R,pe)),x})}function yd(i,e,t,n,r,s,a=wt){if(i.length>1){let o=null;for(let l=0,c=1/0;l<i.length;l++)if(e[l]!==void 0){if(o!=null){let u=$t(i[l]-i[o]);u<c&&(c=u,a=$t(t(i[l],n,r,s)-t(i[o],n,r,s)))}o=l}}return a}function ZS(i){i=i||oa;const e=_t(i.size,[.6,wt,1]),t=i.align||0,n=i.gap||0;let r=i.radius;r=r==null?[0,0]:typeof r=="number"?[r,0]:r;const s=ht(r),a=1-e[0],o=_t(e[1],wt),l=_t(e[2],1),c=_t(i.disp,oa),u=_t(i.each,m=>{}),{fill:h,stroke:d}=c;return(m,_,v,p)=>Ir(m,_,(f,E,y,T,z,C,D,B,w,x,R)=>{let j=f.pxRound,O=t,K=n*xt,W=o*xt,J=l*xt,Y,ee;T.ori==0?[Y,ee]=s(m,_):[ee,Y]=s(m,_);const pe=T.dir*(T.ori==0?1:-1);let ue=T.ori==0?ko:lu,_e=T.ori==0?u:(G,Ee,me,we,je,fe,Te)=>{u(G,Ee,me,je,we,Te,fe)},be=_t(m.bands,tu).find(G=>G.series[0]==_),ve=be!=null?be.dir:0,te=f.fillTo(m,_,f.min,f.max,ve),le=j(D(te,z,R,w)),xe,he,Be,Ve=x,Ne=j(f.width*xt),dt=!1,U=null,ut=null,tt=null,ot=null;h!=null&&(Ne==0||d!=null)&&(dt=!0,U=h.values(m,_,v,p),ut=new Map,new Set(U).forEach(G=>{G!=null&&ut.set(G,new Path2D)}),Ne>0&&(tt=d.values(m,_,v,p),ot=new Map,new Set(tt).forEach(G=>{G!=null&&ot.set(G,new Path2D)})));let{x0:Fe,size:yt}=c;if(Fe!=null&&yt!=null){O=1,E=Fe.values(m,_,v,p),Fe.unit==2&&(E=E.map(me=>m.posToVal(B+me*x,T.key,!0)));let G=yt.values(m,_,v,p);yt.unit==2?he=G[0]*x:he=C(G[0],T,x,B)-C(0,T,x,B),Ve=yd(E,y,C,T,x,B,Ve),Be=Ve-he+K}else Ve=yd(E,y,C,T,x,B,Ve),Be=Ve*a+K,he=Ve-Be;Be<1&&(Be=0),Ne>=he/2&&(Ne=0),Be<5&&(j=gf);let Ye=Be>0,We=Ve-Be-(Ye?Ne:0);he=j(bc(We,J,W)),xe=(O==0?he/2:O==pe?0:he)-O*pe*((O==0?K/2:0)+(Ye?Ne/2:0));const L={stroke:null,fill:null,clip:null,band:null,gaps:null,flags:0},S=dt?null:new Path2D;let Z=null;if(be!=null)Z=m.data[be.series[1]];else{let{y0:G,y1:Ee}=c;G!=null&&Ee!=null&&(y=Ee.values(m,_,v,p),Z=G.values(m,_,v,p))}let ae=Y*he,Q=ee*he;for(let G=pe==1?v:p;G>=v&&G<=p;G+=pe){let Ee=y[G];if(Ee==null)continue;if(Z!=null){let Se=Z[G]??0;if(Ee-Se==0)continue;le=D(Se,z,R,w)}let me=T.distr!=2||c!=null?E[G]:G,we=C(me,T,x,B),je=D(_t(Ee,te),z,R,w),fe=j(we-xe),Te=j(bn(je,le)),Ke=j(ii(je,le)),ze=Te-Ke;if(Ee!=null){let Se=Ee<0?Q:ae,ke=Ee<0?ae:Q;dt?(Ne>0&&tt[G]!=null&&ue(ot.get(tt[G]),fe,Ke+Fn(Ne/2),he,bn(0,ze-Ne),Se,ke),U[G]!=null&&ue(ut.get(U[G]),fe,Ke+Fn(Ne/2),he,bn(0,ze-Ne),Se,ke)):ue(S,fe,Ke+Fn(Ne/2),he,bn(0,ze-Ne),Se,ke),_e(m,_,G,fe-Ne/2,Ke,he+Ne,ze)}}return Ne>0?L.stroke=dt?ot:S:dt||(L._fill=f.width==0?f._fill:f._stroke??f._fill,L.width=0),L.fill=dt?ut:S,L})}function JS(i,e){const t=_t(e==null?void 0:e.alignGaps,0);return(n,r,s,a)=>Ir(n,r,(o,l,c,u,h,d,m,_,v,p,f)=>{[s,a]=Io(c,s,a);let E=o.pxRound,y=Y=>E(d(Y,u,p,_)),T=Y=>E(m(Y,h,f,v)),z,C,D;u.ori==0?(z=Bo,D=Ns,C=Gf):(z=zo,D=Fs,C=Wf);const B=u.dir*(u.ori==0?1:-1);let w=y(l[B==1?s:a]),x=w,R=[],j=[];for(let Y=B==1?s:a;Y>=s&&Y<=a;Y+=B)if(c[Y]!=null){let pe=l[Y],ue=y(pe);R.push(x=ue),j.push(T(c[Y]))}const O={stroke:i(R,j,z,D,C,E),fill:null,clip:null,band:null,gaps:null,flags:Ls},K=O.stroke;let[W,J]=au(n,r);if(o.fill!=null||W!=0){let Y=O.fill=new Path2D(K),ee=o.fillTo(n,r,o.min,o.max,W),pe=T(ee);D(Y,x,pe),D(Y,w,pe)}if(!o.spanGaps){let Y=[];Y.push(...ou(l,c,s,a,B,y,t)),O.gaps=Y=o.gaps(n,r,s,a,Y),O.clip=Oo(Y,u.ori,_,v,p,f)}return J!=0&&(O.band=J==2?[Ii(n,r,s,a,K,-1),Ii(n,r,s,a,K,1)]:Ii(n,r,s,a,K,J)),O})}function QS(i){return JS(ey,i)}function ey(i,e,t,n,r,s){const a=i.length;if(a<2)return null;const o=new Path2D;if(t(o,i[0],e[0]),a==2)n(o,i[1],e[1]);else{let l=Array(a),c=Array(a-1),u=Array(a-1),h=Array(a-1);for(let d=0;d<a-1;d++)u[d]=e[d+1]-e[d],h[d]=i[d+1]-i[d],c[d]=u[d]/h[d];l[0]=c[0];for(let d=1;d<a-1;d++)c[d]===0||c[d-1]===0||c[d-1]>0!=c[d]>0?l[d]=0:(l[d]=3*(h[d-1]+h[d])/((2*h[d]+h[d-1])/c[d-1]+(h[d]+2*h[d-1])/c[d]),isFinite(l[d])||(l[d]=0));l[a-1]=c[a-2];for(let d=0;d<a-1;d++)r(o,i[d]+h[d]/3,e[d]+l[d]*h[d]/3,i[d+1]-h[d]/3,e[d+1]-l[d+1]*h[d]/3,i[d+1],e[d+1])}return o}const Rc=new Set;function Ed(){for(let i of Rc)i.syncRect(!0)}Us&&(Tr(UM,ys,Ed),Tr(NM,ys,Ed,!0),Tr(bo,ys,()=>{on.pxRatio=xt}));const ty=qf(),ny=Xf();function bd(i,e,t,n){return(n?[i[0],i[1]].concat(i.slice(2)):[i[0]].concat(i.slice(1))).map((s,a)=>Cc(s,a,e,t))}function iy(i,e){return i.map((t,n)=>n==0?{}:Yt({},e,t))}function Cc(i,e,t,n){return Yt({},e==0?t:n,i)}function $f(i,e,t){return e==null?Cs:[e,t]}const ry=$f;function sy(i,e,t){return e==null?Cs:To(e,t,Qc,!0)}function jf(i,e,t,n){return e==null?Cs:Uo(e,t,i.scales[n].log,!1)}const ay=jf;function Kf(i,e,t,n){return e==null?Cs:Jc(e,t,i.scales[n].log,!1)}const oy=Kf;function ly(i,e,t,n,r){let s=bn(nd(i),nd(e)),a=e-i,o=ei(r/n*a,t);do{let l=t[o],c=n*l/a;if(c>=r&&s+(l<5?nr.get(l):0)<=17)return[l,c]}while(++o<t.length);return[0,0]}function Td(i){let e,t;return i=i.replace(/(\d+)px/,(n,r)=>(e=qt((t=+r)*xt))+"px"),[i,e,t]}function cy(i){i.show&&[i.font,i.labelFont].forEach(e=>{let t=At(e[2]*xt,1);e[0]=e[0].replace(/[0-9.]+px/,t+"px"),e[1]=t})}function on(i,e,t){const n={mode:_t(i.mode,1)},r=n.mode;function s(g,M,A,P){let F=M.valToPct(g);return P+A*(M.dir==-1?1-F:F)}function a(g,M,A,P){let F=M.valToPct(g);return P+A*(M.dir==-1?F:1-F)}function o(g,M,A,P){return M.ori==0?s(g,M,A,P):a(g,M,A,P)}n.valToPosH=s,n.valToPosV=a;let l=!1;n.status=0;const c=n.root=Hn(gM);if(i.id!=null&&(c.id=i.id),Nn(c,i.class),i.title){let g=Hn(xM,c);g.textContent=i.title}const u=Qn("canvas"),h=n.ctx=u.getContext("2d"),d=Hn(MM,c);Tr("click",d,g=>{g.target===_&&(Lt!=zr||Bt!=kr)&&un.click(n,g)},!0);const m=n.under=Hn(SM,d);d.appendChild(u);const _=n.over=Hn(yM,d);i=Ps(i);const v=+_t(i.pxAlign,1),p=Sd(v);(i.plugins||[]).forEach(g=>{g.opts&&(i=g.opts(n,i)||i)});const f=i.ms||.001,E=n.series=r==1?bd(i.series||[],pd,xd,!1):iy(i.series||[null],vd),y=n.axes=bd(i.axes||[],fd,gd,!0),T=n.scales={},z=n.bands=i.bands||[];z.forEach(g=>{g.fill=ht(g.fill||null),g.dir=_t(g.dir,-1)});const C=r==2?E[1].facets[0].scale:E[0].scale,D={axes:ap,series:An},B=(i.drawOrder||["axes","series"]).map(g=>D[g]);function w(g){const M=g.distr==3?A=>Di(A>0?A:g.clamp(n,A,g.min,g.max,g.key)):g.distr==4?A=>Nl(A,g.asinh):g.distr==100?A=>g.fwd(A):A=>A;return A=>{let P=M(A),{_min:F,_max:q}=g,se=q-F;return(P-F)/se}}function x(g){let M=T[g];if(M==null){let A=(i.scales||oa)[g]||oa;if(A.from!=null){x(A.from);let P=Yt({},T[A.from],A,{key:g});P.valToPct=w(P),T[g]=P}else{M=T[g]=Yt({},g==C?Bf:XS,A),M.key=g;let P=M.time,F=M.range,q=ji(F);if((g!=C||r==2&&!P)&&(q&&(F[0]==null||F[1]==null)&&(F={min:F[0]==null?Qh:{mode:1,hard:F[0],soft:F[0]},max:F[1]==null?Qh:{mode:1,hard:F[1],soft:F[1]}},q=!1),!q&&Fo(F))){let se=F;F=(de,Me,Pe)=>Me==null?Cs:To(Me,Pe,se)}M.range=ht(F||(P?ry:g==C?M.distr==3?ay:M.distr==4?oy:$f:M.distr==3?jf:M.distr==4?Kf:sy)),M.auto=ht(q?!1:M.auto),M.clamp=ht(M.clamp||WS),M._min=M._max=null,M.valToPct=w(M)}}}x("x"),x("y"),r==1&&E.forEach(g=>{x(g.scale)}),y.forEach(g=>{x(g.scale)});for(let g in i.scales)x(g);const R=T[C],j=R.distr;let O,K;R.ori==0?(Nn(c,_M),O=s,K=a):(Nn(c,vM),O=a,K=s);const W={};for(let g in T){let M=T[g];(M.min!=null||M.max!=null)&&(W[g]={min:M.min,max:M.max},M.min=M.max=null)}const J=i.tzDate||(g=>new Date(qt(g/f))),Y=i.fmtDate||nu,ee=f==1?_S(J):MS(J),pe=ud(J,cd(f==1?gS:xS,Y)),ue=dd(J,hd(yS,Y)),_e=[],be=n.legend=Yt({},TS,i.legend),ve=n.cursor=Yt({},LS,{drag:{y:r==2}},i.cursor),te=be.show,le=ve.show,xe=be.markers;be.idxs=_e,xe.width=ht(xe.width),xe.dash=ht(xe.dash),xe.stroke=ht(xe.stroke),xe.fill=ht(xe.fill);let he,Be,Ve,Ne=[],dt=[],U,ut=!1,tt={};if(be.live){const g=E[1]?E[1].values:null;ut=g!=null,U=ut?g(n,1,0):{_:0};for(let M in U)tt[M]=Kc}if(te)if(he=Qn("table",RM,c),Ve=Qn("tbody",null,he),be.mount(n,he),ut){Be=Qn("thead",null,he,Ve);let g=Qn("tr",null,Be);Qn("th",null,g);for(var ot in U)Qn("th",kh,g).textContent=ot}else Nn(he,PM),be.live&&Nn(he,CM);const Fe={show:!0},yt={show:!1};function Ye(g,M){if(M==0&&(ut||!be.live||r==2))return Cs;let A=[],P=Qn("tr",LM,Ve,Ve.childNodes[M]);Nn(P,g.class),g.show||Nn(P,Sr);let F=Qn("th",null,P);if(xe.show){let de=Hn(DM,F);if(M>0){let Me=xe.width(n,M);Me&&(de.style.border=Me+"px "+xe.dash(n,M)+" "+xe.stroke(n,M)),de.style.background=xe.fill(n,M)}}let q=Hn(kh,F);g.label instanceof HTMLElement?q.appendChild(g.label):q.textContent=g.label,M>0&&(xe.show||(q.style.color=g.width>0?xe.stroke(n,M):xe.fill(n,M)),L("click",F,de=>{if(ve._lock)return;Ft(de);let Me=E.indexOf(g);if((de.ctrlKey||de.metaKey)!=be.isolate){let Pe=E.some((Le,Ie)=>Ie>0&&Ie!=Me&&Le.show);E.forEach((Le,Ie)=>{Ie>0&&li(Ie,Pe?Ie==Me?Fe:yt:Fe,!0,Wt.setSeries)})}else li(Me,{show:!g.show},!0,Wt.setSeries)},!1),ai&&L(Wh,F,de=>{ve._lock||(Ft(de),li(E.indexOf(g),Vr,!0,Wt.setSeries))},!1));for(var se in U){let de=Qn("td",IM,P);de.textContent="--",A.push(de)}return[P,A]}const We=new Map;function L(g,M,A,P=!0){const F=We.get(M)||{},q=ve.bind[g](n,M,A,P);q&&(Tr(g,M,F[g]=q),We.set(M,F))}function S(g,M,A){const P=We.get(M)||{};for(let F in P)(g==null||F==g)&&(Ec(F,M,P[F]),delete P[F]);g==null&&We.delete(M)}let Z=0,ae=0,Q=0,G=0,Ee=0,me=0,we=Ee,je=me,fe=Q,Te=G,Ke=0,ze=0,Se=0,ke=0;n.bbox={};let N=!1,oe=!1,I=!1,re=!1,ne=!1,ie=!1;function ge(g,M,A){(A||g!=n.width||M!=n.height)&&$e(g,M),Nr(!1),I=!0,oe=!0,Fr()}function $e(g,M){n.width=Z=Q=g,n.height=ae=G=M,Ee=me=0,at(),ln();let A=n.bbox;Ke=A.left=_r(Ee*xt,.5),ze=A.top=_r(me*xt,.5),Se=A.width=_r(Q*xt,.5),ke=A.height=_r(G*xt,.5)}const st=3;function mt(){let g=!1,M=0;for(;!g;){M++;let A=rp(M),P=sp(M);g=M==st||A&&P,g||($e(n.width,n.height),oe=!0)}}function Et({width:g,height:M}){ge(g,M)}n.setSize=Et;function at(){let g=!1,M=!1,A=!1,P=!1;y.forEach((F,q)=>{if(F.show&&F._show){let{side:se,_size:de}=F,Me=se%2,Pe=F.label!=null?F.labelSize:0,Le=de+Pe;Le>0&&(Me?(Q-=Le,se==3?(Ee+=Le,P=!0):A=!0):(G-=Le,se==0?(me+=Le,g=!0):M=!0))}}),xi[0]=g,xi[1]=A,xi[2]=M,xi[3]=P,Q-=$[1]+$[3],Ee+=$[3],G-=$[2]+$[0],me+=$[0]}function ln(){let g=Ee+Q,M=me+G,A=Ee,P=me;function F(q,se){switch(q){case 1:return g+=se,g-se;case 2:return M+=se,M-se;case 3:return A-=se,A+se;case 0:return P-=se,P+se}}y.forEach((q,se)=>{if(q.show&&q._show){let de=q.side;q._pos=F(de,q._size),q.label!=null&&(q._lpos=F(de,q.labelSize))}})}if(ve.dataIdx==null){let g=ve.hover,M=g.skip=new Set(g.skip??[]);M.add(void 0);let A=g.prox=ht(g.prox),P=g.bias??(g.bias=0);ve.dataIdx=(F,q,se,de)=>{if(q==0)return se;let Me=se,Pe=A(F,q,se,de)??wt,Le=Pe>=0&&Pe<wt,Ie=R.ori==0?Q:G,et=ve.left,vt=e[0],gt=e[q];if(M.has(gt[se])){Me=null;let ct=null,Qe=null,Ge;if(P==0||P==-1)for(Ge=se;ct==null&&Ge-- >0;)M.has(gt[Ge])||(ct=Ge);if(P==0||P==1)for(Ge=se;Qe==null&&Ge++<gt.length;)M.has(gt[Ge])||(Qe=Ge);if(ct!=null||Qe!=null)if(Le){let It=ct==null?-1/0:O(vt[ct],R,Ie,0),Ht=Qe==null?1/0:O(vt[Qe],R,Ie,0),sn=et-It,Tt=Ht-et;sn<=Tt?sn<=Pe&&(Me=ct):Tt<=Pe&&(Me=Qe)}else Me=Qe==null?ct:ct==null?Qe:se-ct<=Qe-se?ct:Qe}else Le&&$t(et-O(vt[se],R,Ie,0))>Pe&&(Me=null);return Me}}const Ft=g=>{ve.event=g};ve.idxs=_e,ve._lock=!1;let Ot=ve.points;Ot.show=ht(Ot.show),Ot.size=ht(Ot.size),Ot.stroke=ht(Ot.stroke),Ot.width=ht(Ot.width),Ot.fill=ht(Ot.fill);const en=n.focus=Yt({},i.focus||{alpha:.3},ve.focus),ai=en.prox>=0,_i=ai&&Ot.one;let _n=[],qn=[],vi=[];function sr(g,M){let A=Ot.show(n,M);if(A instanceof HTMLElement)return Nn(A,AM),Nn(A,g.class),di(A,-10,-10,Q,G),_.insertBefore(A,_n[M]),A}function Os(g,M){if(r==1||M>0){let A=r==1&&T[g.scale].time,P=g.value;g.value=A?sd(P)?dd(J,hd(P,Y)):P||ue:P||HS,g.label=g.label||(A?IS:DS)}if(_i||M>0){g.width=g.width==null?1:g.width,g.paths=g.paths||ty||XM,g.fillTo=ht(g.fillTo||YS),g.pxAlign=+_t(g.pxAlign,v),g.pxRound=Sd(g.pxAlign),g.stroke=ht(g.stroke||null),g.fill=ht(g.fill||null),g._stroke=g._fill=g._paths=g._focus=null;let A=VS(bn(1,g.width),1),P=g.points=Yt({},{size:A,width:bn(1,A*.2),stroke:g.stroke,space:A*2,paths:ny,_stroke:null,_fill:null},g.points);P.show=ht(P.show),P.filter=ht(P.filter),P.fill=ht(P.fill),P.stroke=ht(P.stroke),P.paths=ht(P.paths),P.pxAlign=g.pxAlign}if(te){let A=Ye(g,M);Ne.splice(M,0,A[0]),dt.splice(M,0,A[1]),be.values.push(null)}if(le){_e.splice(M,0,null);let A=null;_i?M==0&&(A=sr(g,M)):M>0&&(A=sr(g,M)),_n.splice(M,0,A),qn.splice(M,0,0),vi.splice(M,0,0)}rn("addSeries",M)}function fa(g,M){M=M??E.length,g=r==1?Cc(g,M,pd,xd):Cc(g,M,{},vd),E.splice(M,0,g),Os(E[M],M)}n.addSeries=fa;function Ho(g){if(E.splice(g,1),te){be.values.splice(g,1),dt.splice(g,1);let M=Ne.splice(g,1)[0];S(null,M.firstChild),M.remove()}le&&(_e.splice(g,1),_n.splice(g,1)[0].remove(),qn.splice(g,1),vi.splice(g,1)),rn("delSeries",g)}n.delSeries=Ho;const xi=[!1,!1,!1,!1];function Vo(g,M){if(g._show=g.show,g.show){let A=g.side%2,P=T[g.scale];P==null&&(g.scale=A?E[1].scale:C,P=T[g.scale]);let F=P.time;g.size=ht(g.size),g.space=ht(g.space),g.rotate=ht(g.rotate),ji(g.incrs)&&g.incrs.forEach(se=>{!nr.has(se)&&nr.set(se,xf(se))}),g.incrs=ht(g.incrs||(P.distr==2?fS:F?f==1?mS:vS:vr)),g.splits=ht(g.splits||(F&&P.distr==1?ee:P.distr==3?Tc:P.distr==4?FS:NS)),g.stroke=ht(g.stroke),g.grid.stroke=ht(g.grid.stroke),g.ticks.stroke=ht(g.ticks.stroke),g.border.stroke=ht(g.border.stroke);let q=g.values;g.values=ji(q)&&!ji(q[0])?ht(q):F?ji(q)?ud(J,cd(q,Y)):sd(q)?SS(J,q):q||pe:q||US,g.filter=ht(g.filter||(P.distr>=3&&P.log==10?zS:P.distr==3&&P.log==2?kS:_f)),g.font=Td(g.font),g.labelFont=Td(g.labelFont),g._size=g.size(n,null,M,0),g._space=g._rotate=g._incrs=g._found=g._splits=g._values=null,g._size>0&&(xi[M]=!0,g._el=Hn(EM,d))}}function b(g,M,A,P){let[F,q,se,de]=A,Me=M%2,Pe=0;return Me==0&&(de||q)&&(Pe=M==0&&!F||M==2&&!se?qt(fd.size/3):0),Me==1&&(F||se)&&(Pe=M==1&&!q||M==3&&!de?qt(gd.size/2):0),Pe}const H=n.padding=(i.padding||[b,b,b,b]).map(g=>ht(_t(g,b))),$=n._padding=H.map((g,M)=>g(n,M,xi,0));let X,k=null,ce=null;const Re=r==1?E[0].idxs:null;let Ce=null,De=!1;function Ze(g,M){if(e=g??[],n.data=n._data=e,r==2){X=0;for(let A=1;A<E.length;A++)X+=e[A][0].length}else{e.length==0&&(n.data=n._data=e=[[]]),Ce=e[0],X=Ce.length;let A=e;if(j==2){A=e.slice();let P=A[0]=Array(X);for(let F=0;F<X;F++)P[F]=F}n._data=e=A}if(Nr(!0),rn("setData"),j==2&&(I=!0),M!==!1){let A=R;A.auto(n,De)?Je():Bi(C,A.min,A.max),re=re||ve.left>=0,ie=!0,Fr()}}n.setData=Ze;function Je(){De=!0;let g,M;r==1&&(X>0?(k=Re[0]=0,ce=Re[1]=X-1,g=e[0][k],M=e[0][ce],j==2?(g=k,M=ce):g==M&&(j==3?[g,M]=Uo(g,g,R.log,!1):j==4?[g,M]=Jc(g,g,R.log,!1):R.time?M=g+qt(86400/f):[g,M]=To(g,M,Qc,!0))):(k=Re[0]=g=null,ce=Re[1]=M=null)),Bi(C,g,M)}let Oe,lt,Rt,Ct,cn,ft,He,Gt,pt,Pt;function Mi(g,M,A,P,F,q){g??(g=Vh),A??(A=tu),P??(P="butt"),F??(F=Vh),q??(q="round"),g!=Oe&&(h.strokeStyle=Oe=g),F!=lt&&(h.fillStyle=lt=F),M!=Rt&&(h.lineWidth=Rt=M),q!=cn&&(h.lineJoin=cn=q),P!=ft&&(h.lineCap=ft=P),A!=Ct&&h.setLineDash(Ct=A)}function hn(g,M,A,P){M!=lt&&(h.fillStyle=lt=M),g!=He&&(h.font=He=g),A!=Gt&&(h.textAlign=Gt=A),P!=pt&&(h.textBaseline=pt=P)}function ar(g,M,A,P,F=0){if(P.length>0&&g.auto(n,De)&&(M==null||M.min==null)){let q=_t(k,0),se=_t(ce,P.length-1),de=A.min==null?zM(P,q,se,F,g.distr==3):[A.min,A.max];g.min=ii(g.min,A.min=de[0]),g.max=bn(g.max,A.max=de[1])}}const kt={min:null,max:null};function oi(){for(let P in T){let F=T[P];W[P]==null&&(F.min==null||W[C]!=null&&F.auto(n,De))&&(W[P]=kt)}for(let P in T){let F=T[P];W[P]==null&&F.from!=null&&W[F.from]!=null&&(W[P]=kt)}W[C]!=null&&Nr(!0);let g={};for(let P in W){let F=W[P];if(F!=null){let q=g[P]=Ps(T[P],$M);if(F.min!=null)Yt(q,F);else if(P!=C||r==2)if(X==0&&q.from==null){let se=q.range(n,null,null,P);q.min=se[0],q.max=se[1]}else q.min=wt,q.max=-wt}}if(X>0){E.forEach((P,F)=>{if(r==1){let q=P.scale,se=W[q];if(se==null)return;let de=g[q];if(F==0){let Me=de.range(n,de.min,de.max,q);de.min=Me[0],de.max=Me[1],k=ei(de.min,e[0]),ce=ei(de.max,e[0]),ce-k>1&&(e[0][k]<de.min&&k++,e[0][ce]>de.max&&ce--),P.min=Ce[k],P.max=Ce[ce]}else P.show&&P.auto&&ar(de,se,P,e[F],P.sorted);P.idxs[0]=k,P.idxs[1]=ce}else if(F>0&&P.show&&P.auto){let[q,se]=P.facets,de=q.scale,Me=se.scale,[Pe,Le]=e[F],Ie=g[de],et=g[Me];Ie!=null&&ar(Ie,W[de],q,Pe,q.sorted),et!=null&&ar(et,W[Me],se,Le,se.sorted),P.min=se.min,P.max=se.max}});for(let P in g){let F=g[P],q=W[P];if(F.from==null&&(q==null||q.min==null)){let se=F.range(n,F.min==wt?null:F.min,F.max==-wt?null:F.max,P);F.min=se[0],F.max=se[1]}}}for(let P in g){let F=g[P];if(F.from!=null){let q=g[F.from];if(q.min==null)F.min=F.max=null;else{let se=F.range(n,q.min,q.max,P);F.min=se[0],F.max=se[1]}}}let M={},A=!1;for(let P in g){let F=g[P],q=T[P];if(q.min!=F.min||q.max!=F.max){q.min=F.min,q.max=F.max;let se=q.distr;q._min=se==3?Di(q.min):se==4?Nl(q.min,q.asinh):se==100?q.fwd(q.min):q.min,q._max=se==3?Di(q.max):se==4?Nl(q.max,q.asinh):se==100?q.fwd(q.max):q.max,M[P]=A=!0}}if(A){E.forEach((P,F)=>{r==2?F>0&&M.y&&(P._paths=null):M[P.scale]&&(P._paths=null)});for(let P in M)I=!0,rn("setScale",P);le&&ve.left>=0&&(re=ie=!0)}for(let P in W)W[P]=null}function Bs(g){let M=bc(k-1,0,X-1),A=bc(ce+1,0,X-1);for(;g[M]==null&&M>0;)M--;for(;g[A]==null&&A<X-1;)A++;return[M,A]}function An(){if(X>0){let g=E.some(M=>M._focus)&&Pt!=en.alpha;g&&(h.globalAlpha=Pt=en.alpha),E.forEach((M,A)=>{if(A>0&&M.show&&(Ur(A,!1),Ur(A,!0),M._paths==null)){let P=Pt;Pt!=M.alpha&&(h.globalAlpha=Pt=M.alpha);let F=r==2?[0,e[A][0].length-1]:Bs(e[A]);M._paths=M.paths(n,A,F[0],F[1]),Pt!=P&&(h.globalAlpha=Pt=P)}}),E.forEach((M,A)=>{if(A>0&&M.show){let P=Pt;Pt!=M.alpha&&(h.globalAlpha=Pt=M.alpha),M._paths!=null&&pa(A,!1);{let F=M._paths!=null?M._paths.gaps:null,q=M.points.show(n,A,k,ce,F),se=M.points.filter(n,A,q,F);(q||se)&&(M.points._paths=M.points.paths(n,A,k,ce,se),pa(A,!0))}Pt!=P&&(h.globalAlpha=Pt=P),rn("drawSeries",A)}}),g&&(h.globalAlpha=Pt=1)}}function Ur(g,M){let A=M?E[g].points:E[g];A._stroke=A.stroke(n,g),A._fill=A.fill(n,g)}function pa(g,M){let A=M?E[g].points:E[g],{stroke:P,fill:F,clip:q,flags:se,_stroke:de=A._stroke,_fill:Me=A._fill,_width:Pe=A.width}=A._paths;Pe=At(Pe*xt,3);let Le=null,Ie=Pe%2/2;M&&Me==null&&(Me=Pe>0?"#fff":de);let et=A.pxAlign==1&&Ie>0;if(et&&h.translate(Ie,Ie),!M){let vt=Ke-Pe/2,gt=ze-Pe/2,ct=Se+Pe,Qe=ke+Pe;Le=new Path2D,Le.rect(vt,gt,ct,Qe)}M?Go(de,Pe,A.dash,A.cap,Me,P,F,se,q):ma(g,de,Pe,A.dash,A.cap,Me,P,F,se,Le,q),et&&h.translate(-Ie,-Ie)}function ma(g,M,A,P,F,q,se,de,Me,Pe,Le){let Ie=!1;Me!=0&&z.forEach((et,vt)=>{if(et.series[0]==g){let gt=E[et.series[1]],ct=e[et.series[1]],Qe=(gt._paths||oa).band;ji(Qe)&&(Qe=et.dir==1?Qe[0]:Qe[1]);let Ge,It=null;gt.show&&Qe&&HM(ct,k,ce)?(It=et.fill(n,vt)||q,Ge=gt._paths.clip):Qe=null,Go(M,A,P,F,It,se,de,Me,Pe,Le,Ge,Qe),Ie=!0}}),Ie||Go(M,A,P,F,q,se,de,Me,Pe,Le)}const hu=Ls|Ac;function Go(g,M,A,P,F,q,se,de,Me,Pe,Le,Ie){Mi(g,M,A,P,F),(Me||Pe||Ie)&&(h.save(),Me&&h.clip(Me),Pe&&h.clip(Pe)),Ie?(de&hu)==hu?(h.clip(Ie),Le&&h.clip(Le),_a(F,se),ga(g,q,M)):de&Ac?(_a(F,se),h.clip(Ie),ga(g,q,M)):de&Ls&&(h.save(),h.clip(Ie),Le&&h.clip(Le),_a(F,se),h.restore(),ga(g,q,M)):(_a(F,se),ga(g,q,M)),(Me||Pe||Ie)&&h.restore()}function ga(g,M,A){A>0&&(M instanceof Map?M.forEach((P,F)=>{h.strokeStyle=Oe=F,h.stroke(P)}):M!=null&&g&&h.stroke(M))}function _a(g,M){M instanceof Map?M.forEach((A,P)=>{h.fillStyle=lt=P,h.fill(A)}):M!=null&&g&&h.fill(M)}function ip(g,M,A,P){let F=y[g],q;if(P<=0)q=[0,0];else{let se=F._space=F.space(n,g,M,A,P),de=F._incrs=F.incrs(n,g,M,A,P,se);q=ly(M,A,de,P,se)}return F._found=q}function Wo(g,M,A,P,F,q,se,de,Me,Pe){let Le=se%2/2;v==1&&h.translate(Le,Le),Mi(de,se,Me,Pe,de),h.beginPath();let Ie,et,vt,gt,ct=F+(P==0||P==3?-q:q);A==0?(et=F,gt=ct):(Ie=F,vt=ct);for(let Qe=0;Qe<g.length;Qe++)M[Qe]!=null&&(A==0?Ie=vt=g[Qe]:et=gt=g[Qe],h.moveTo(Ie,et),h.lineTo(vt,gt));h.stroke(),v==1&&h.translate(-Le,-Le)}function rp(g){let M=!0;return y.forEach((A,P)=>{if(!A.show)return;let F=T[A.scale];if(F.min==null){A._show&&(M=!1,A._show=!1,Nr(!1));return}else A._show||(M=!1,A._show=!0,Nr(!1));let q=A.side,se=q%2,{min:de,max:Me}=F,[Pe,Le]=ip(P,de,Me,se==0?Q:G);if(Le==0)return;let Ie=F.distr==2,et=A._splits=A.splits(n,P,de,Me,Pe,Le,Ie),vt=F.distr==2?et.map(Ge=>Ce[Ge]):et,gt=F.distr==2?Ce[et[1]]-Ce[et[0]]:Pe,ct=A._values=A.values(n,A.filter(n,vt,P,Le,gt),P,Le,gt);A._rotate=q==2?A.rotate(n,ct,P,Le):0;let Qe=A._size;A._size=Vn(A.size(n,ct,P,g)),Qe!=null&&A._size!=Qe&&(M=!1)}),M}function sp(g){let M=!0;return H.forEach((A,P)=>{let F=A(n,P,xi,g);F!=$[P]&&(M=!1),$[P]=F}),M}function ap(){for(let g=0;g<y.length;g++){let M=y[g];if(!M.show||!M._show)continue;let A=M.side,P=A%2,F,q,se=M.stroke(n,g),de=A==0||A==3?-1:1,[Me,Pe]=M._found;if(M.label!=null){let xn=M.labelGap*de,Dn=qt((M._lpos+xn)*xt);hn(M.labelFont[0],se,"center",A==2?Qs:Hh),h.save(),P==1?(F=q=0,h.translate(Dn,qt(ze+ke/2)),h.rotate((A==3?-uo:uo)/2)):(F=qt(Ke+Se/2),q=Dn);let cr=mf(M.label)?M.label(n,g,Me,Pe):M.label;h.fillText(cr,F,q),h.restore()}if(Pe==0)continue;let Le=T[M.scale],Ie=P==0?Se:ke,et=P==0?Ke:ze,vt=M._splits,gt=Le.distr==2?vt.map(xn=>Ce[xn]):vt,ct=Le.distr==2?Ce[vt[1]]-Ce[vt[0]]:Me,Qe=M.ticks,Ge=M.border,It=Qe.show?Qe.size:0,Ht=qt(It*xt),sn=qt((M.alignTo==2?M._size-It-M.gap:M.gap)*xt),Tt=M._rotate*-uo/180,Vt=p(M._pos*xt),Pn=(Ht+sn)*de,vn=Vt+Pn;q=P==0?vn:0,F=P==1?vn:0;let Bn=M.font[0],$n=M.align==1?fs:M.align==2?Dl:Tt>0?fs:Tt<0?Dl:P==0?"center":A==3?Dl:fs,ui=Tt||P==1?"middle":A==2?Qs:Hh;hn(Bn,se,$n,ui);let Ln=M.font[1]*M.lineGap,zn=vt.map(xn=>p(o(xn,Le,Ie,et))),jn=M._values;for(let xn=0;xn<jn.length;xn++){let Dn=jn[xn];if(Dn!=null){P==0?F=zn[xn]:q=zn[xn],Dn=""+Dn;let cr=Dn.indexOf(`
`)==-1?[Dn]:Dn.split(/\n/gm);for(let Mn=0;Mn<cr.length;Mn++){let Pu=cr[Mn];Tt?(h.save(),h.translate(F,q+Mn*Ln),h.rotate(Tt),h.fillText(Pu,0,0),h.restore()):h.fillText(Pu,F,q+Mn*Ln)}}}Qe.show&&Wo(zn,Qe.filter(n,gt,g,Pe,ct),P,A,Vt,Ht,At(Qe.width*xt,3),Qe.stroke(n,g),Qe.dash,Qe.cap);let hi=M.grid;hi.show&&Wo(zn,hi.filter(n,gt,g,Pe,ct),P,P==0?2:1,P==0?ze:Ke,P==0?ke:Se,At(hi.width*xt,3),hi.stroke(n,g),hi.dash,hi.cap),Ge.show&&Wo([Vt],[1],P==0?1:0,P==0?1:2,P==1?ze:Ke,P==1?ke:Se,At(Ge.width*xt,3),Ge.stroke(n,g),Ge.dash,Ge.cap)}rn("drawAxes")}function Nr(g){E.forEach((M,A)=>{A>0&&(M._paths=null,g&&(r==1?(M.min=null,M.max=null):M.facets.forEach(P=>{P.min=null,P.max=null})))})}let va=!1,Xo=!1,zs=[];function op(){Xo=!1;for(let g=0;g<zs.length;g++)rn(...zs[g]);zs.length=0}function Fr(){va||(tS(du),va=!0)}function lp(g,M=!1){va=!0,Xo=M,g(n),du(),M&&zs.length>0&&queueMicrotask(op)}n.batch=lp;function du(){if(N&&(oi(),N=!1),I&&(mt(),I=!1),oe){if(Ut(m,fs,Ee),Ut(m,Qs,me),Ut(m,na,Q),Ut(m,ia,G),Ut(_,fs,Ee),Ut(_,Qs,me),Ut(_,na,Q),Ut(_,ia,G),Ut(d,na,Z),Ut(d,ia,ae),u.width=qt(Z*xt),u.height=qt(ae*xt),y.forEach(({_el:g,_show:M,_size:A,_pos:P,side:F})=>{if(g!=null)if(M){let q=F===3||F===0?A:0,se=F%2==1;Ut(g,se?"left":"top",P-q),Ut(g,se?"width":"height",A),Ut(g,se?"top":"left",se?me:Ee),Ut(g,se?"height":"width",se?G:Q),yc(g,Sr)}else Nn(g,Sr)}),Oe=lt=Rt=cn=ft=He=Gt=pt=Ct=null,Pt=1,Vs(!0),Ee!=we||me!=je||Q!=fe||G!=Te){Nr(!1);let g=Q/fe,M=G/Te;if(le&&!re&&ve.left>=0){ve.left*=g,ve.top*=M,Or&&di(Or,qt(ve.left),0,Q,G),Br&&di(Br,0,qt(ve.top),Q,G);for(let A=0;A<_n.length;A++){let P=_n[A];P!=null&&(qn[A]*=g,vi[A]*=M,di(P,Vn(qn[A]),Vn(vi[A]),Q,G))}}if(Dt.show&&!ne&&Dt.left>=0&&Dt.width>0){Dt.left*=g,Dt.width*=g,Dt.top*=M,Dt.height*=M;for(let A in Zo)Ut(Hr,A,Dt[A])}we=Ee,je=me,fe=Q,Te=G}rn("setSize"),oe=!1}Z>0&&ae>0&&(h.clearRect(0,0,u.width,u.height),rn("drawClear"),B.forEach(g=>g()),rn("draw")),Dt.show&&ne&&(xa(Dt),ne=!1),le&&re&&(lr(null,!0,!1),re=!1),be.show&&be.live&&ie&&(jo(),ie=!1),l||(l=!0,n.status=1,rn("ready")),De=!1,va=!1}n.redraw=(g,M)=>{I=M||!1,g!==!1?Bi(C,R.min,R.max):Fr()};function Yo(g,M){let A=T[g];if(A.from==null){if(X==0){let P=A.range(n,M.min,M.max,g);M.min=P[0],M.max=P[1]}if(M.min>M.max){let P=M.min;M.min=M.max,M.max=P}if(X>1&&M.min!=null&&M.max!=null&&M.max-M.min<1e-16)return;g==C&&A.distr==2&&X>0&&(M.min=ei(M.min,e[0]),M.max=ei(M.max,e[0]),M.min==M.max&&M.max++),W[g]=M,N=!0,Fr()}}n.setScale=Yo;let qo,$o,Or,Br,fu,pu,zr,kr,mu,gu,Lt,Bt,Oi=!1;const un=ve.drag;let tn=un.x,nn=un.y;le&&(ve.x&&(qo=Hn(TM,_)),ve.y&&($o=Hn(wM,_)),R.ori==0?(Or=qo,Br=$o):(Or=$o,Br=qo),Lt=ve.left,Bt=ve.top);const Dt=n.select=Yt({show:!0,over:!0,left:0,width:0,top:0,height:0},i.select),Hr=Dt.show?Hn(bM,Dt.over?_:m):null;function xa(g,M){if(Dt.show){for(let A in g)Dt[A]=g[A],A in Zo&&Ut(Hr,A,g[A]);M!==!1&&rn("setSelect")}}n.setSelect=xa;function cp(g){if(E[g].show)te&&yc(Ne[g],Sr);else if(te&&Nn(Ne[g],Sr),le){let A=_i?_n[0]:_n[g];A!=null&&di(A,-10,-10,Q,G)}}function Bi(g,M,A){Yo(g,{min:M,max:A})}function li(g,M,A,P){M.focus!=null&&pp(g),M.show!=null&&E.forEach((F,q)=>{q>0&&(g==q||g==null)&&(F.show=M.show,cp(q),r==2?(Bi(F.facets[0].scale,null,null),Bi(F.facets[1].scale,null,null)):Bi(F.scale,null,null),Fr())}),A!==!1&&rn("setSeries",g,M),P&&Gs("setSeries",n,g,M)}n.setSeries=li;function up(g,M){Yt(z[g],M)}function hp(g,M){g.fill=ht(g.fill||null),g.dir=_t(g.dir,-1),M=M??z.length,z.splice(M,0,g)}function dp(g){g==null?z.length=0:z.splice(g,1)}n.addBand=hp,n.setBand=up,n.delBand=dp;function fp(g,M){E[g].alpha=M,le&&_n[g]!=null&&(_n[g].style.opacity=M),te&&Ne[g]&&(Ne[g].style.opacity=M)}let Si,zi,or;const Vr={focus:!0};function pp(g){if(g!=or){let M=g==null,A=en.alpha!=1;E.forEach((P,F)=>{if(r==1||F>0){let q=M||F==0||F==g;P._focus=M?null:q,A&&fp(F,q?1:en.alpha)}}),or=g,A&&Fr()}}te&&ai&&L(Xh,he,g=>{ve._lock||(Ft(g),or!=null&&li(null,Vr,!0,Wt.setSeries))});function ci(g,M,A){let P=T[M];A&&(g=g/xt-(P.ori==1?me:Ee));let F=Q;P.ori==1&&(F=G,g=F-g),P.dir==-1&&(g=F-g);let q=P._min,se=P._max,de=g/F,Me=q+(se-q)*de,Pe=P.distr;return Pe==3?Rs(10,Me):Pe==4?GM(Me,P.asinh):Pe==100?P.bwd(Me):Me}function mp(g,M){let A=ci(g,C,M);return ei(A,e[0],k,ce)}n.valToIdx=g=>ei(g,e[0]),n.posToIdx=mp,n.posToVal=ci,n.valToPos=(g,M,A)=>T[M].ori==0?s(g,T[M],A?Se:Q,A?Ke:0):a(g,T[M],A?ke:G,A?ze:0),n.setCursor=(g,M,A)=>{Lt=g.left,Bt=g.top,lr(null,M,A)};function _u(g,M){Ut(Hr,fs,Dt.left=g),Ut(Hr,na,Dt.width=M)}function vu(g,M){Ut(Hr,Qs,Dt.top=g),Ut(Hr,ia,Dt.height=M)}let ks=R.ori==0?_u:vu,Hs=R.ori==1?_u:vu;function gp(){if(te&&be.live)for(let g=r==2?1:0;g<E.length;g++){if(g==0&&ut)continue;let M=be.values[g],A=0;for(let P in M)dt[g][A++].firstChild.nodeValue=M[P]}}function jo(g,M){if(g!=null&&(g.idxs?g.idxs.forEach((A,P)=>{_e[P]=A}):qM(g.idx)||_e.fill(g.idx),be.idx=_e[0]),te&&be.live){for(let A=0;A<E.length;A++)(A>0||r==1&&!ut)&&_p(A,_e[A]);gp()}ie=!1,M!==!1&&rn("setLegend")}n.setLegend=jo;function _p(g,M){let A=E[g],P=g==0&&j==2?Ce:e[g],F;ut?F=A.values(n,g,M)??tt:(F=A.value(n,M==null?null:P[M],g,M),F=F==null?tt:{_:F}),be.values[g]=F}function lr(g,M,A){mu=Lt,gu=Bt,[Lt,Bt]=ve.move(n,Lt,Bt),ve.left=Lt,ve.top=Bt,le&&(Or&&di(Or,qt(Lt),0,Q,G),Br&&di(Br,0,qt(Bt),Q,G));let P,F=k>ce;Si=wt,zi=null;let q=R.ori==0?Q:G,se=R.ori==1?Q:G;if(Lt<0||X==0||F){P=ve.idx=null;for(let de=0;de<E.length;de++){let Me=_n[de];Me!=null&&di(Me,-10,-10,Q,G)}ai&&li(null,Vr,!0,g==null&&Wt.setSeries),be.live&&(_e.fill(P),ie=!0)}else{let de,Me,Pe;r==1&&(de=R.ori==0?Lt:Bt,Me=ci(de,C),P=ve.idx=ei(Me,e[0],k,ce),Pe=O(e[0][P],R,q,0));let Le=-10,Ie=-10,et=0,vt=0,gt=!0,ct="",Qe="";for(let Ge=r==2?1:0;Ge<E.length;Ge++){let It=E[Ge],Ht=_e[Ge],sn=Ht==null?null:r==1?e[Ge][Ht]:e[Ge][1][Ht],Tt=ve.dataIdx(n,Ge,P,Me),Vt=Tt==null?null:r==1?e[Ge][Tt]:e[Ge][1][Tt];if(ie=ie||Vt!=sn||Tt!=Ht,_e[Ge]=Tt,Ge>0&&It.show){let Pn=Tt==null?-10:Tt==P?Pe:O(r==1?e[0][Tt]:e[Ge][0][Tt],R,q,0),vn=Vt==null?-10:K(Vt,r==1?T[It.scale]:T[It.facets[1].scale],se,0);if(ai&&Vt!=null){let Bn=R.ori==1?Lt:Bt,$n=$t(en.dist(n,Ge,Tt,vn,Bn));if($n<Si){let ui=en.bias;if(ui!=0){let Ln=ci(Bn,It.scale),zn=Vt>=0?1:-1,jn=Ln>=0?1:-1;jn==zn&&(jn==1?ui==1?Vt>=Ln:Vt<=Ln:ui==1?Vt<=Ln:Vt>=Ln)&&(Si=$n,zi=Ge)}else Si=$n,zi=Ge}}if(ie||_i){let Bn,$n;R.ori==0?(Bn=Pn,$n=vn):(Bn=vn,$n=Pn);let ui,Ln,zn,jn,hi,xn,Dn=!0,cr=Ot.bbox;if(cr!=null){Dn=!1;let Mn=cr(n,Ge);zn=Mn.left,jn=Mn.top,ui=Mn.width,Ln=Mn.height}else zn=Bn,jn=$n,ui=Ln=Ot.size(n,Ge);if(xn=Ot.fill(n,Ge),hi=Ot.stroke(n,Ge),_i)Ge==zi&&Si<=en.prox&&(Le=zn,Ie=jn,et=ui,vt=Ln,gt=Dn,ct=xn,Qe=hi);else{let Mn=_n[Ge];Mn!=null&&(qn[Ge]=zn,vi[Ge]=jn,Jh(Mn,ui,Ln,Dn),Kh(Mn,xn,hi),di(Mn,Vn(zn),Vn(jn),Q,G))}}}}if(_i){let Ge=en.prox,It=or==null?Si<=Ge:Si>Ge||zi!=or;if(ie||It){let Ht=_n[0];Ht!=null&&(qn[0]=Le,vi[0]=Ie,Jh(Ht,et,vt,gt),Kh(Ht,ct,Qe),di(Ht,Vn(Le),Vn(Ie),Q,G))}}}if(Dt.show&&Oi)if(g!=null){let[de,Me]=Wt.scales,[Pe,Le]=Wt.match,[Ie,et]=g.cursor.sync.scales,vt=g.cursor.drag;if(tn=vt._x,nn=vt._y,tn||nn){let{left:gt,top:ct,width:Qe,height:Ge}=g.select,It=g.scales[Ie].ori,Ht=g.posToVal,sn,Tt,Vt,Pn,vn,Bn=de!=null&&Pe(de,Ie),$n=Me!=null&&Le(Me,et);Bn&&tn?(It==0?(sn=gt,Tt=Qe):(sn=ct,Tt=Ge),Vt=T[de],Pn=O(Ht(sn,Ie),Vt,q,0),vn=O(Ht(sn+Tt,Ie),Vt,q,0),ks(ii(Pn,vn),$t(vn-Pn))):ks(0,q),$n&&nn?(It==1?(sn=gt,Tt=Qe):(sn=ct,Tt=Ge),Vt=T[Me],Pn=K(Ht(sn,et),Vt,se,0),vn=K(Ht(sn+Tt,et),Vt,se,0),Hs(ii(Pn,vn),$t(vn-Pn))):Hs(0,se)}else Jo()}else{let de=$t(mu-fu),Me=$t(gu-pu);if(R.ori==1){let et=de;de=Me,Me=et}tn=un.x&&de>=un.dist,nn=un.y&&Me>=un.dist;let Pe=un.uni;Pe!=null?tn&&nn&&(tn=de>=Pe,nn=Me>=Pe,!tn&&!nn&&(Me>de?nn=!0:tn=!0)):un.x&&un.y&&(tn||nn)&&(tn=nn=!0);let Le,Ie;tn&&(R.ori==0?(Le=zr,Ie=Lt):(Le=kr,Ie=Bt),ks(ii(Le,Ie),$t(Ie-Le)),nn||Hs(0,se)),nn&&(R.ori==1?(Le=zr,Ie=Lt):(Le=kr,Ie=Bt),Hs(ii(Le,Ie),$t(Ie-Le)),tn||ks(0,q)),!tn&&!nn&&(ks(0,0),Hs(0,0))}if(un._x=tn,un._y=nn,g==null){if(A){if(Cu!=null){let[de,Me]=Wt.scales;Wt.values[0]=de!=null?ci(R.ori==0?Lt:Bt,de):null,Wt.values[1]=Me!=null?ci(R.ori==1?Lt:Bt,Me):null}Gs(Il,n,Lt,Bt,Q,G,P)}if(ai){let de=A&&Wt.setSeries,Me=en.prox;or==null?Si<=Me&&li(zi,Vr,!0,de):Si>Me?li(null,Vr,!0,de):zi!=or&&li(zi,Vr,!0,de)}}ie&&(be.idx=P,jo()),M!==!1&&rn("setCursor")}let ki=null;Object.defineProperty(n,"rect",{get(){return ki==null&&Vs(!1),ki}});function Vs(g=!1){g?ki=null:(ki=_.getBoundingClientRect(),rn("syncRect",ki))}function xu(g,M,A,P,F,q,se){ve._lock||Oi&&g!=null&&g.movementX==0&&g.movementY==0||(Ko(g,M,A,P,F,q,se,!1,g!=null),g!=null?lr(null,!0,!0):lr(M,!0,!1))}function Ko(g,M,A,P,F,q,se,de,Me){if(ki==null&&Vs(!1),Ft(g),g!=null)A=g.clientX-ki.left,P=g.clientY-ki.top;else{if(A<0||P<0){Lt=-10,Bt=-10;return}let[Pe,Le]=Wt.scales,Ie=M.cursor.sync,[et,vt]=Ie.values,[gt,ct]=Ie.scales,[Qe,Ge]=Wt.match,It=M.axes[0].side%2==1,Ht=R.ori==0?Q:G,sn=R.ori==1?Q:G,Tt=It?q:F,Vt=It?F:q,Pn=It?P:A,vn=It?A:P;if(gt!=null?A=Qe(Pe,gt)?o(et,T[Pe],Ht,0):-10:A=Ht*(Pn/Tt),ct!=null?P=Ge(Le,ct)?o(vt,T[Le],sn,0):-10:P=sn*(vn/Vt),R.ori==1){let Bn=A;A=P,P=Bn}}Me&&(M==null||M.cursor.event.type==Il)&&((A<=1||A>=Q-1)&&(A=_r(A,Q)),(P<=1||P>=G-1)&&(P=_r(P,G))),de?(fu=A,pu=P,[zr,kr]=ve.move(n,A,P)):(Lt=A,Bt=P)}const Zo={width:0,height:0,left:0,top:0};function Jo(){xa(Zo,!1)}let Mu,Su,yu,Eu;function bu(g,M,A,P,F,q,se){Oi=!0,tn=nn=un._x=un._y=!1,Ko(g,M,A,P,F,q,se,!0,!1),g!=null&&(L(Ul,Mc,Tu,!1),Gs(Gh,n,zr,kr,Q,G,null));let{left:de,top:Me,width:Pe,height:Le}=Dt;Mu=de,Su=Me,yu=Pe,Eu=Le}function Tu(g,M,A,P,F,q,se){Oi=un._x=un._y=!1,Ko(g,M,A,P,F,q,se,!1,!0);let{left:de,top:Me,width:Pe,height:Le}=Dt,Ie=Pe>0||Le>0,et=Mu!=de||Su!=Me||yu!=Pe||Eu!=Le;if(Ie&&et&&xa(Dt),un.setScale&&Ie&&et){let vt=de,gt=Pe,ct=Me,Qe=Le;if(R.ori==1&&(vt=Me,gt=Le,ct=de,Qe=Pe),tn&&Bi(C,ci(vt,C),ci(vt+gt,C)),nn)for(let Ge in T){let It=T[Ge];Ge!=C&&It.from==null&&It.min!=wt&&Bi(Ge,ci(ct+Qe,Ge),ci(ct,Ge))}Jo()}else ve.lock&&(ve._lock=!ve._lock,lr(M,!0,g!=null));g!=null&&(S(Ul,Mc),Gs(Ul,n,Lt,Bt,Q,G,null))}function vp(g,M,A,P,F,q,se){if(ve._lock)return;Ft(g);let de=Oi;if(Oi){let Me=!0,Pe=!0,Le=10,Ie,et;R.ori==0?(Ie=tn,et=nn):(Ie=nn,et=tn),Ie&&et&&(Me=Lt<=Le||Lt>=Q-Le,Pe=Bt<=Le||Bt>=G-Le),Ie&&Me&&(Lt=Lt<zr?0:Q),et&&Pe&&(Bt=Bt<kr?0:G),lr(null,!0,!0),Oi=!1}Lt=-10,Bt=-10,_e.fill(null),lr(null,!0,!0),de&&(Oi=de)}function wu(g,M,A,P,F,q,se){ve._lock||(Ft(g),Je(),Jo(),g!=null&&Gs(Yh,n,Lt,Bt,Q,G,null))}function Au(){y.forEach(cy),ge(n.width,n.height,!0)}Tr(bo,ys,Au);const Gr={};Gr.mousedown=bu,Gr.mousemove=xu,Gr.mouseup=Tu,Gr.dblclick=wu,Gr.setSeries=(g,M,A,P)=>{let F=Wt.match[2];A=F(n,M,A),A!=-1&&li(A,P,!0,!1)},le&&(L(Gh,_,bu),L(Il,_,xu),L(Wh,_,g=>{Ft(g),Vs(!1)}),L(Xh,_,vp),L(Yh,_,wu),Rc.add(n),n.syncRect=Vs);const Ma=n.hooks=i.hooks||{};function rn(g,M,A){Xo?zs.push([g,M,A]):g in Ma&&Ma[g].forEach(P=>{P.call(null,n,M,A)})}(i.plugins||[]).forEach(g=>{for(let M in g.hooks)Ma[M]=(Ma[M]||[]).concat(g.hooks[M])});const Ru=(g,M,A)=>A,Wt=Yt({key:null,setSeries:!1,filters:{pub:id,sub:id},scales:[C,E[1]?E[1].scale:null],match:[rd,rd,Ru],values:[null,null]},ve.sync);Wt.match.length==2&&Wt.match.push(Ru),ve.sync=Wt;const Cu=Wt.key,Qo=zf(Cu);function Gs(g,M,A,P,F,q,se){Wt.filters.pub(g,M,A,P,F,q,se)&&Qo.pub(g,M,A,P,F,q,se)}Qo.sub(n);function xp(g,M,A,P,F,q,se){Wt.filters.sub(g,M,A,P,F,q,se)&&Gr[g](null,M,A,P,F,q,se)}n.pub=xp;function Mp(){Qo.unsub(n),Rc.delete(n),We.clear(),Ec(bo,ys,Au),c.remove(),he==null||he.remove(),rn("destroy")}n.destroy=Mp;function el(){rn("init",i,e),Ze(e||i.data,!1),W[C]?Yo(C,W[C]):Je(),ne=Dt.show&&(Dt.width>0||Dt.height>0),re=ie=!0,ge(i.width,i.height)}return E.forEach(Os),y.forEach(Vo),t?t instanceof HTMLElement?(t.appendChild(c),el()):t(n,el):el(),n}on.assign=Yt;on.fmtNum=eu;on.rangeNum=To;on.rangeLog=Uo;on.rangeAsinh=Jc;on.orient=Ir;on.pxRatio=xt;on.join=eS;on.fmtDate=nu,on.tzDate=hS;on.sync=zf;{on.addGap=qS,on.clipGaps=Oo;let i=on.paths={points:Xf};i.linear=qf,i.stepped=KS,i.bars=ZS,i.spline=QS}class uy{constructor(){ye(this,"name","Plotter");ye(this,"container",null);ye(this,"tabsContainer",null);ye(this,"contentContainer",null);ye(this,"paretoPlot",null);ye(this,"ablationPlot",null);ye(this,"variabilityPlot",null);ye(this,"currentTab","pareto");ye(this,"records",[]);ye(this,"ablationGroups",[]);ye(this,"paretoFlags",[]);ye(this,"chance",.1);ye(this,"onCampaignMetrics",e=>{const{data:t}=e;t!=null&&t.records&&(this.records=t.records,this.paretoFlags=t.pareto||[],this.ablationGroups=t.ablation_groups||[],typeof t.chance=="number"&&(this.chance=t.chance),this.updatePlots(),this.updateStatus())});mn.register("campaign_metrics",this.onCampaignMetrics)}async init(){this.createUI(),console.log("[Plotter] Initialized")}async destroy(){var e,t,n,r;mn.unregister("campaign_metrics",this.onCampaignMetrics),(e=this.paretoPlot)==null||e.destroy(),(t=this.ablationPlot)==null||t.destroy(),(n=this.variabilityPlot)==null||n.destroy(),(r=this.container)==null||r.remove()}createUI(){const e=document.getElementById("ui-overlay");e&&(this.container=document.createElement("div"),this.container.id="plotter",this.container.style.cssText=`
      position: fixed;
      bottom: 20px;
      right: 20px;
      width: 520px;
      height: 380px;
      background: var(--bg-secondary);
      border: 1px solid var(--border);
      border-radius: 8px;
      display: flex;
      flex-direction: column;
      z-index: 150;
      box-shadow: 0 8px 32px rgba(0,0,0,0.4);
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
        <span id="plotter-status">No data</span>
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
    `,e.appendChild(this.container),this.tabsContainer=this.container.querySelector("#plotter-tabs"),this.contentContainer=this.container.querySelector("#plotter-content"),this.tabsContainer.querySelectorAll(".plotter-tab").forEach(t=>{t.addEventListener("click",()=>this.switchTab(t.getAttribute("data-tab")))}),this.container.querySelector("#plotter-download").addEventListener("click",()=>this.downloadCurrent()),this.switchTab(this.currentTab))}switchTab(e){this.currentTab=e,this.tabsContainer.querySelectorAll(".plotter-tab").forEach(n=>{n.classList.toggle("active",n.getAttribute("data-tab")===e)}),Object.entries({pareto:"plotter-pareto",ablation:"plotter-ablation",variability:"plotter-variability"}).forEach(([n,r])=>{const s=document.getElementById(r);s&&(s.style.display=n===e?"block":"none")}),e==="pareto"&&!this.paretoPlot&&this.initParetoPlot(),e==="ablation"&&!this.ablationPlot&&this.initAblationPlot(),e==="variability"&&!this.variabilityPlot&&this.initVariabilityPlot(),this.updatePlots()}updateStatus(){var t;const e=(t=this.container)==null?void 0:t.querySelector("#plotter-status");e&&(e.textContent=`${this.records.length} records | ${this.paretoFlags.filter(n=>n).length} Pareto`)}updatePlots(){this.currentTab==="pareto"&&this.paretoPlot&&this.updateParetoPlot(),this.currentTab==="ablation"&&this.ablationPlot&&this.updateAblationPlot(),this.currentTab==="variability"&&this.variabilityPlot&&this.updateVariabilityPlot()}initParetoPlot(){const e=document.getElementById("plotter-pareto");if(!e)return;const t={width:e.clientWidth,height:e.clientHeight,title:"Pareto Frontier: val_acc vs 1/walltime_s",axes:[{grid:{stroke:Ue.border}},{grid:{stroke:Ue.border},side:1}],scales:{x:{time:!1},y:{time:!1}},series:[{},{label:"val_acc",stroke:Ue.gradient,width:0,points:{show:!0,size:6,stroke:"white",width:1,fill:(n,r)=>{var s,a;return this.paretoFlags[r]?Ue.pareto:br[(a=(s=this.records[r])==null?void 0:s.coordinate)==null?void 0:a.credit]||Ue.gradient}}}],hooks:{draw:[n=>{if(this.paretoFlags.some(r=>r)){const r=[];this.records.forEach((o,l)=>{this.paretoFlags[l]&&o.payload.walltime_s&&o.payload.val_acc&&r.push([1/o.payload.walltime_s,o.payload.val_acc])}),r.sort((o,l)=>o[0]-l[0]);const s=n.ctx;r.length>1&&(s.beginPath(),s.strokeStyle=Ue.pareto,s.lineWidth=2,s.setLineDash([5,5]),r.forEach((o,l)=>{const c=n.valToPos(o[0],"x"),u=n.valToPos(o[1],"y");l===0?s.moveTo(c,u):s.lineTo(c,u)}),s.stroke(),s.setLineDash([]));const a=n.valToPos(this.chance,"y");s.strokeStyle=Ue.chance_line,s.lineWidth=1.5,s.setLineDash([4,4]),s.beginPath(),s.moveTo(n.bbox.left,a),s.lineTo(n.bbox.width,a),s.stroke(),s.setLineDash([])}}]},cursor:{show:!0,drag:{setScale:!0},focus:{prox:16}}};this.paretoPlot=new on(t,[[],[]],e)}updateParetoPlot(){if(!this.paretoPlot||this.records.length===0)return;const e=[],t=[];this.records.forEach(n=>{const r=n.payload.walltime_s,s=n.payload.val_acc;r&&s?(e.push(1/r),t.push(s)):(e.push(NaN),t.push(NaN))}),this.paretoPlot.setData([e,t])}initAblationPlot(){const e=document.getElementById("plotter-ablation");if(!e)return;const t={width:e.clientWidth,height:e.clientHeight,title:"Ablation: Credit Arm vs val_acc",axes:[{grid:{stroke:Ue.border}},{grid:{stroke:Ue.border},side:1}],scales:{x:{time:!1},y:{time:!1}},series:[{},{label:"val_acc",fill:Ue.gradient,stroke:Ue.gradient,width:0}],hooks:{draw:[n=>{if(!this.ablationGroups.length)return;const r=n.ctx,s=this.ablationGroups.find(u=>u.axis==="credit");if(!s)return;const a=s.metrics.find(u=>u.metric==="val_acc");if(!a)return;const o=a.arms,l=n.bbox.width/(o.length*1.5);n.bbox.left,o.forEach((u,h)=>{const d=n.valToPos(h,"x"),m=n.valToPos(0,"y"),_=n.valToPos(u.mean,"y"),v=m-_;if(r.fillStyle=br[u.value]||Ue.gradient,r.fillRect(d-l/2,_,l,v),u.std>0){const p=n.valToPos(u.mean+u.std,"y");r.strokeStyle=Ue.text_muted,r.lineWidth=1,r.beginPath(),r.moveTo(d,p),r.lineTo(d,m),r.stroke(),r.moveTo(d-3,p),r.lineTo(d+3,p),r.stroke()}});const c=n.valToPos(this.chance,"y");r.strokeStyle=Ue.chance_line,r.lineWidth=2,r.setLineDash([5,5]),r.beginPath(),r.moveTo(n.bbox.left,c),r.lineTo(n.bbox.width,c),r.stroke(),r.setLineDash([])}]},cursor:{show:!0,drag:{setScale:!0}}};this.ablationPlot=new on(t,[[],[]],e)}updateAblationPlot(){if(!this.ablationPlot||!this.ablationGroups.length)return;const e=this.ablationGroups.find(s=>s.axis==="credit");if(!e)return;const t=e.metrics.find(s=>s.metric==="val_acc");if(!t)return;const n=t.arms.map((s,a)=>a),r=t.arms.map(s=>s.mean);this.ablationPlot.setData([n,r]),this.ablationPlot.opts.title=`Ablation: ${e.axis} vs val_acc (fixed: ${e.fixed_axes})`,this.ablationPlot.redraw()}initVariabilityPlot(){const e=document.getElementById("plotter-variability");if(!e)return;const t={width:e.clientWidth,height:e.clientHeight,title:"Seed Variability: val_acc per Credit Arm",axes:[{grid:{stroke:Ue.border}},{grid:{stroke:Ue.border},side:1}],scales:{x:{time:!1},y:{time:!1}},series:[{},{label:"val_acc",fill:Ue.gradient,stroke:Ue.gradient,width:0}],hooks:{draw:[n=>{if(!this.records.length)return;const r=n.ctx,s={};this.records.forEach(c=>{const u=c.coordinate.credit,h=c.payload.val_acc;h!==void 0&&(s[u]||(s[u]=[])).push(h)});const a=Object.keys(s).sort(),o=n.bbox.width/(a.length*2);a.forEach((c,u)=>{const h=s[c].sort((x,R)=>x-R),d=h.length;if(d===0)return;const m=h[Math.floor(d*.25)],_=h[Math.floor(d*.5)],v=h[Math.floor(d*.75)],p=v-m,f=Math.max(h[0],m-1.5*p),E=Math.min(h[d-1],v+1.5*p),y=n.valToPos(u,"x"),T=n.valToPos(f,"y"),z=n.valToPos(m,"y"),C=n.valToPos(_,"y"),D=n.valToPos(v,"y"),B=n.valToPos(E,"y"),w=br[c]||Ue.gradient;r.strokeStyle=w,r.lineWidth=1.5,r.beginPath(),r.moveTo(y,T),r.lineTo(y,z),r.moveTo(y,D),r.lineTo(y,B),r.stroke(),r.fillStyle=w+"44",r.strokeStyle=w,r.lineWidth=1.5,r.fillRect(y-o/2,D,o,z-D),r.strokeRect(y-o/2,D,o,z-D),r.strokeStyle="white",r.lineWidth=2,r.beginPath(),r.moveTo(y-o/2,C),r.lineTo(y+o/2,C),r.stroke(),h.forEach(x=>{if(x<f||x>E){const R=n.valToPos(x,"y");r.fillStyle=w,r.beginPath(),r.arc(y,R,2,0,Math.PI*2),r.fill()}})});const l=n.valToPos(this.chance,"y");r.strokeStyle=Ue.chance_line,r.lineWidth=2,r.setLineDash([5,5]),r.beginPath(),r.moveTo(n.bbox.left,l),r.lineTo(n.bbox.width,l),r.stroke(),r.setLineDash([])}]},cursor:{show:!0,drag:{setScale:!0}}};this.variabilityPlot=new on(t,[[],[]],e)}updateVariabilityPlot(){if(!this.variabilityPlot||!this.records.length)return;const e=Array.from(new Set(this.records.map(r=>r.coordinate.credit))).sort(),t=e.map((r,s)=>s),n=e.map(()=>0);this.variabilityPlot.setData([t,n])}downloadCurrent(){const t={pareto:this.paretoPlot,ablation:this.ablationPlot,variability:this.variabilityPlot}[this.currentTab];if(!t)return;const n=document.createElement("a");n.download=`computronium-${this.currentTab}-${Date.now()}.png`,n.href=t.ctx.canvas.toDataURL("image/png"),n.click()}}const Zf=new uy;Pr.register(Zf);class hy{constructor(){ye(this,"name","LiveRail");ye(this,"container",null);ye(this,"logContainer",null);ye(this,"events",[]);ye(this,"maxEvents",50);ye(this,"onPipelineEvent",e=>{this.events.unshift(e),this.events.length>this.maxEvents&&this.events.pop(),this.render()});ye(this,"onStatusUpdate",e=>{var s,a;const t=(s=this.container)==null?void 0:s.querySelector("#rail-connection");if(!t)return;const n=t.querySelector(".dot");if(!n)return;const r=t.querySelector(".rail-label");r&&(((a=e.data)==null?void 0:a.running_campaigns)>0?(n.style.background=Ue.ok,t.style.background=Ue.ok+"22",t.style.borderColor=Ue.ok+"88",t.style.color=Ue.ok,r.textContent="Connected"):(n.style.background=Ue.warn,t.style.background=Ue.warn+"22",t.style.borderColor=Ue.warn+"88",t.style.color=Ue.warn,r.textContent="Idle"))});mn.register("pipeline_event",this.onPipelineEvent),mn.register("status_update",this.onStatusUpdate)}async init(){this.createUI(),console.log("[LiveRail] Initialized")}async destroy(){var e;mn.unregister("pipeline_event",this.onPipelineEvent),mn.unregister("status_update",this.onStatusUpdate),(e=this.container)==null||e.remove()}createUI(){const e=document.getElementById("ui-overlay");e&&(this.container=document.createElement("div"),this.container.id="live-rail",this.container.style.cssText=`
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
    `,e.appendChild(this.container),this.logContainer=this.container.querySelector("#rail-log"))}render(){var t;if(!this.logContainer)return;this.logContainer.innerHTML=this.events.map(n=>{const r=new Date(n.timestamp).toLocaleTimeString(),a={ok:Ue.ok,warn:Ue.warn,error:Ue.error}[n.level]||Ue.text_secondary,o=n.level==="ok"?"✓":n.level==="warn"?"⚠":"✗";return`
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
        `}).join("");const e=(t=this.container)==null?void 0:t.querySelector("#rail-count");e&&(e.textContent=`${this.events.length} events`),this.logContainer.scrollLeft=0}}const Jf=new hy;Pr.register(Jf);class dy{constructor(){ye(this,"name","HUD");ye(this,"panel",null);ye(this,"modeChip",null);ye(this,"connectionPill",null);ye(this,"rows",new Map);ye(this,"rowElements",new Map);ye(this,"claimValue",null);ye(this,"statusData",{});ye(this,"resources",{});ye(this,"requiredSeeds",0);ye(this,"measuredSeeds",0);ye(this,"connected",!1);ye(this,"animationTime",0);ye(this,"onStatusUpdate",e=>{const t=(e==null?void 0:e.data)??e;t&&(this.statusData=t,this.connected=!0,this.updateConnection(),this.updateQueueRows())});ye(this,"onCampaignMetrics",e=>{var n;const t=e==null?void 0:e.data;t&&(this.resources=t.resources??{},typeof t.required_seeds=="number"&&(this.requiredSeeds=t.required_seeds),this.measuredSeeds=this.resources.seeds_per_arm??((n=t.records)==null?void 0:n.length)??0,this.updateResourceRows(),this.updateClaim())});mn.register("status_update",this.onStatusUpdate),mn.register("campaign_metrics",this.onCampaignMetrics)}async init(){this.createPanel(),this.createModeChip(),console.log("[HUD] Initialized")}async destroy(){var e,t;mn.unregister("status_update",this.onStatusUpdate),mn.unregister("campaign_metrics",this.onCampaignMetrics),(e=this.panel)==null||e.remove(),(t=this.modeChip)==null||t.remove()}createPanel(){const e=document.getElementById("ui-overlay");if(!e)return;this.panel=document.createElement("div"),this.panel.id="hud",this.panel.style.cssText=`
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
        <span style="color: var(--text-secondary);">SEEDS TO CLAIM</span>
        <span id="hud-claim" style="font-weight: 700; color: ${Ue.insufficient};">—</span>
      </div>
    `,e.appendChild(this.panel);const t=this.panel.querySelector("#hud-meters");this.addMeter(t,"device","DEVICE",Ue.gradient),this.addMeter(t,"memory","MEMORY",Ue.memory),this.addMeter(t,"walltime","WALLTIME",Ue.cpu),this.addMeter(t,"gpu","GPU",Ue.gpu),this.addMeter(t,"cpu","CPU",Ue.cpu),this.addMeter(t,"records","RECORDS",Ue.pareto),this.claimValue=this.panel.querySelector("#hud-claim"),this.connectionPill=this.panel.querySelector("#hud-connection")}addMeter(e,t,n,r){const s=document.createElement("div");s.style.cssText="display: flex; flex-direction: column; gap: 3px;",s.innerHTML=`
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
      background: ${Ue.insufficient}22;
      border: 1px solid ${Ue.insufficient}88;
      color: ${Ue.insufficient};
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 0.1em;
      z-index: 150;
    `,this.modeChip.textContent="EXPLORATORY",e.appendChild(this.modeChip))}setMeter(e,t,n){const r=this.rows.get(e),s=this.rowElements.get(e);!r||!s||(r.value=t,r.fraction=Math.max(0,Math.min(1,n)),s.value.textContent=t,s.fill.style.width=`${(r.fraction*100).toFixed(1)}%`)}updateQueueRows(){const e=this.statusData;this.setMeter("gpu",e.max_gpus?`${e.used_gpus??0} / ${e.max_gpus}`:"—",e.max_gpus?(e.used_gpus??0)/e.max_gpus:0),this.setMeter("cpu",e.max_cpus?`${e.used_cpus??0} / ${e.max_cpus}`:"—",e.max_cpus?(e.used_cpus??0)/e.max_cpus:0)}updateResourceRows(){const e=this.resources;this.setMeter("device",e.device??"—",e.device?1:0),this.setMeter("memory",e.memory_mb!==void 0?`${e.memory_mb.toFixed(1)} MB`:"—",e.memory_mb!==void 0?Math.min(1,e.memory_mb/2048):0),this.setMeter("walltime",e.walltime_s!==void 0?`${e.walltime_s.toFixed(1)} s`:"—",e.walltime_s!==void 0?Math.min(1,e.walltime_s/120):0),this.setMeter("records",e.records!==void 0?`${e.records}`:"—",e.records!==void 0?Math.min(1,e.records/20):0)}updateClaim(){if(!this.claimValue)return;if(this.requiredSeeds<=0){this.claimValue.textContent="—";return}const e=Math.max(0,this.requiredSeeds-this.measuredSeeds);this.claimValue.textContent=`${e} more (${this.requiredSeeds} needed)`}updateConnection(){if(!this.connectionPill)return;const e=this.connectionPill.querySelector(".dot"),t=this.connectionPill.querySelector("span:last-child"),n=this.connected?Ue.ok:Ue.error;e.style.background=n,this.connectionPill.style.background=`${n}22`,this.connectionPill.style.borderColor=`${n}88`,this.connectionPill.style.color=n,t.textContent=this.connected?"live":"offline"}update(e){var n;this.animationTime+=e;const t=.5+.5*Math.sin(this.animationTime*2);(n=this.connectionPill)==null||n.style.setProperty("opacity",`${.75+.25*t}`)}}const cu=new dy;Pr.register(cu);window.addEventListener("error",i=>{var e;console.error("[Global Error]",i.error),ep(((e=i.error)==null?void 0:e.message)||"Unknown error")});window.addEventListener("unhandledrejection",i=>{var e;console.error("[Unhandled Rejection]",i.reason),ep(((e=i.reason)==null?void 0:e.message)||"Unhandled promise rejection")});let Ri=null,qi=null;function Qf(i="Initializing dashboard..."){const e=document.getElementById("ui-overlay");e&&(Ri=document.createElement("div"),Ri.id="global-loading",Ri.style.cssText=`
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
  `,Ri.innerHTML=`
    <div style="
      width: 48px;
      height: 48px;
      border: 3px solid var(--border);
      border-top-color: ${Ue.gradient};
      border-radius: 50%;
      animation: spin 1s linear infinite;
    "></div>
    <div style="font-size: 14px; color: var(--text-primary);">${i}</div>
    <style>
      @keyframes spin { to { transform: rotate(360deg); } }
    </style>
  `,e.appendChild(Ri))}function wd(){Ri==null||Ri.remove(),Ri=null}function ep(i){const e=document.getElementById("ui-overlay");e&&(qi=document.createElement("div"),qi.id="global-error",qi.style.cssText=`
    position: fixed;
    top: 20px;
    right: 20px;
    background: ${Ue.error}22;
    border: 1px solid ${Ue.error}88;
    border-radius: 8px;
    padding: 16px 24px;
    color: ${Ue.error};
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    z-index: 1000;
    max-width: 400px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    display: flex;
    align-items: center;
    gap: 12px;
  `,qi.innerHTML=`
    <span>✗</span>
    <span>${i}</span>
    <button onclick="this.parentElement.remove()" style="
      background: none;
      border: none;
      color: ${Ue.error};
      font-size: 18px;
      cursor: pointer;
      line-height: 1;
      padding: 0 4px;
    ">&times;</button>
  `,e.appendChild(qi),setTimeout(()=>qi==null?void 0:qi.remove(),1e4))}Eo.connect();Qf("Connecting to dashboard...");Eo.waitForConnection(15e3).then(i=>{i?wd():(Qf("Connection timeout — retrying..."),Eo.onStateChange(e=>{e==="connected"&&wd()}))});const fy=document.getElementById("dashboard-canvas"),Yn=new af({canvas:fy,antialias:!0,alpha:!0,powerPreference:"high-performance"});Yn.setSize(window.innerWidth,window.innerHeight);Yn.setPixelRatio(Math.min(window.devicePixelRatio,2));Yn.shadowMap.enabled=!0;Yn.shadowMap.type=Cd;Yn.toneMapping=Ld;Yn.toneMappingExposure=1.2;const Ni=new Wc;Ni.background=new nt(658964);Ni.fog=new Gc(658964,.015);const ir=new En(60,window.innerWidth/window.innerHeight,.1,200);ir.position.set(3.5,4.8,9.5);ir.lookAt(0,1.1,0);cM({scene:Ni,camera:ir,renderer:Yn});const Fi=new aM(ir,Yn.domElement);Fi.target.set(0,1.1,0);Fi.enableDamping=!0;Fi.dampingFactor=.05;Fi.enablePan=!0;Fi.minDistance=5;Fi.maxDistance=80;Fi.maxPolarAngle=Math.PI/2-.05;const py=new Kx(4473958,.6);Ni.add(py);const si=new jx(16777215,1.2);si.position.set(10,20,10);si.castShadow=!0;si.shadow.mapSize.width=2048;si.shadow.mapSize.height=2048;si.shadow.camera.near=1;si.shadow.camera.far=50;si.shadow.camera.left=-20;si.shadow.camera.right=20;si.shadow.camera.top=20;si.shadow.camera.bottom=-20;Ni.add(si);const my=new Yx(8956671,2236979,.5);Ni.add(my);const uu=new Jx(8,8,2371648,1449256);uu.position.y=-.01;const tp=uu.material;tp.transparent=!0;tp.opacity=.35;Ni.add(uu);function gy(){ir.aspect=window.innerWidth/window.innerHeight,ir.updateProjectionMatrix(),Yn.setSize(window.innerWidth,window.innerHeight),Yn.setPixelRatio(Math.min(window.devicePixelRatio,2))}window.addEventListener("resize",gy);let Ad=0;function np(i){requestAnimationFrame(np);const e=(i-Ad)/1e3;Ad=i,Fi.update(),$c.update(e),cu.update(e),Yn.render(Ni,ir)}requestAnimationFrame(np);window.__DASHBOARD__={scene:Ni,camera:ir,renderer:Yn,controls:Fi,discoveryMap:$c,cellDrawer:uf,plotter:Zf,liveRail:Jf,hud:cu,wsClient:Eo,router:mn};console.log("🚀 Computronium Dashboard initialized");
//# sourceMappingURL=dashboard.js.map
