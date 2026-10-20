var vm=Object.defineProperty;var xm=(i,e,t)=>e in i?vm(i,e,{enumerable:!0,configurable:!0,writable:!0,value:t}):i[e]=t;var G=(i,e,t)=>xm(i,typeof e!="symbol"?e+"":e,t);/**
 * @license
 * Copyright 2010-2024 Three.js Authors
 * SPDX-License-Identifier: MIT
 */const hu="168",Qs={ROTATE:0,DOLLY:1,PAN:2},er={ROTATE:0,PAN:1,DOLLY_PAN:2,DOLLY_ROTATE:3},ym=0,gh=1,Mm=2,Mf=1,Sf=2,Ui=3,cs=0,In=1,$n=2,os=0,Cr=1,_h=2,vh=3,xh=4,Sm=5,Rs=100,bm=101,Em=102,wm=103,Tm=104,Am=200,Cm=201,Rm=202,Pm=203,vc=204,xc=205,Lm=206,Dm=207,Im=208,Um=209,Nm=210,Fm=211,Om=212,Bm=213,zm=214,km=0,Hm=1,Vm=2,zo=3,Gm=4,Wm=5,Xm=6,qm=7,bf=0,Ym=1,$m=2,ls=0,jm=1,Km=2,Zm=3,Ef=4,Jm=5,Qm=6,eg=7,wf=300,Or=301,Br=302,yc=303,Mc=304,il=306,Sc=1e3,Ds=1001,bc=1002,Kn=1003,tg=1004,Ya=1005,ai=1006,Ll=1007,Is=1008,Gi=1009,Tf=1010,Af=1011,Ca=1012,du=1013,Os=1014,Fi=1015,Ia=1016,fu=1017,pu=1018,zr=1020,Cf=35902,Rf=1021,Pf=1022,ci=1023,Lf=1024,Df=1025,Rr=1026,kr=1027,If=1028,mu=1029,Uf=1030,gu=1031,_u=1033,Lo=33776,Do=33777,Io=33778,Uo=33779,Ec=35840,wc=35841,Tc=35842,Ac=35843,Cc=36196,Rc=37492,Pc=37496,Lc=37808,Dc=37809,Ic=37810,Uc=37811,Nc=37812,Fc=37813,Oc=37814,Bc=37815,zc=37816,kc=37817,Hc=37818,Vc=37819,Gc=37820,Wc=37821,No=36492,Xc=36494,qc=36495,Nf=36283,Yc=36284,$c=36285,jc=36286,ng=3200,ig=3201,Ff=0,sg=1,rs="",xi="srgb",fs="srgb-linear",vu="display-p3",sl="display-p3-linear",ko="linear",Ft="srgb",Ho="rec709",Vo="p3",tr=7680,yh=519,rg=512,ag=513,og=514,Of=515,lg=516,cg=517,ug=518,hg=519,Kc=35044,Mh="300 es",Oi=2e3,Go=2001;let jr=class{addEventListener(e,t){this._listeners===void 0&&(this._listeners={});const n=this._listeners;n[e]===void 0&&(n[e]=[]),n[e].indexOf(t)===-1&&n[e].push(t)}hasEventListener(e,t){if(this._listeners===void 0)return!1;const n=this._listeners;return n[e]!==void 0&&n[e].indexOf(t)!==-1}removeEventListener(e,t){if(this._listeners===void 0)return;const s=this._listeners[e];if(s!==void 0){const r=s.indexOf(t);r!==-1&&s.splice(r,1)}}dispatchEvent(e){if(this._listeners===void 0)return;const n=this._listeners[e.type];if(n!==void 0){e.target=this;const s=n.slice(0);for(let r=0,a=s.length;r<a;r++)s[r].call(this,e);e.target=null}}};const xn=["00","01","02","03","04","05","06","07","08","09","0a","0b","0c","0d","0e","0f","10","11","12","13","14","15","16","17","18","19","1a","1b","1c","1d","1e","1f","20","21","22","23","24","25","26","27","28","29","2a","2b","2c","2d","2e","2f","30","31","32","33","34","35","36","37","38","39","3a","3b","3c","3d","3e","3f","40","41","42","43","44","45","46","47","48","49","4a","4b","4c","4d","4e","4f","50","51","52","53","54","55","56","57","58","59","5a","5b","5c","5d","5e","5f","60","61","62","63","64","65","66","67","68","69","6a","6b","6c","6d","6e","6f","70","71","72","73","74","75","76","77","78","79","7a","7b","7c","7d","7e","7f","80","81","82","83","84","85","86","87","88","89","8a","8b","8c","8d","8e","8f","90","91","92","93","94","95","96","97","98","99","9a","9b","9c","9d","9e","9f","a0","a1","a2","a3","a4","a5","a6","a7","a8","a9","aa","ab","ac","ad","ae","af","b0","b1","b2","b3","b4","b5","b6","b7","b8","b9","ba","bb","bc","bd","be","bf","c0","c1","c2","c3","c4","c5","c6","c7","c8","c9","ca","cb","cc","cd","ce","cf","d0","d1","d2","d3","d4","d5","d6","d7","d8","d9","da","db","dc","dd","de","df","e0","e1","e2","e3","e4","e5","e6","e7","e8","e9","ea","eb","ec","ed","ee","ef","f0","f1","f2","f3","f4","f5","f6","f7","f8","f9","fa","fb","fc","fd","fe","ff"];let Sh=1234567;const Pr=Math.PI/180,Ra=180/Math.PI;function zi(){const i=Math.random()*4294967295|0,e=Math.random()*4294967295|0,t=Math.random()*4294967295|0,n=Math.random()*4294967295|0;return(xn[i&255]+xn[i>>8&255]+xn[i>>16&255]+xn[i>>24&255]+"-"+xn[e&255]+xn[e>>8&255]+"-"+xn[e>>16&15|64]+xn[e>>24&255]+"-"+xn[t&63|128]+xn[t>>8&255]+"-"+xn[t>>16&255]+xn[t>>24&255]+xn[n&255]+xn[n>>8&255]+xn[n>>16&255]+xn[n>>24&255]).toLowerCase()}function Mn(i,e,t){return Math.max(e,Math.min(t,i))}function xu(i,e){return(i%e+e)%e}function dg(i,e,t,n,s){return n+(i-e)*(s-n)/(t-e)}function fg(i,e,t){return i!==e?(t-i)/(e-i):0}function Ea(i,e,t){return(1-t)*i+t*e}function pg(i,e,t,n){return Ea(i,e,1-Math.exp(-t*n))}function mg(i,e=1){return e-Math.abs(xu(i,e*2)-e)}function gg(i,e,t){return i<=e?0:i>=t?1:(i=(i-e)/(t-e),i*i*(3-2*i))}function _g(i,e,t){return i<=e?0:i>=t?1:(i=(i-e)/(t-e),i*i*i*(i*(i*6-15)+10))}function vg(i,e){return i+Math.floor(Math.random()*(e-i+1))}function xg(i,e){return i+Math.random()*(e-i)}function yg(i){return i*(.5-Math.random())}function Mg(i){i!==void 0&&(Sh=i);let e=Sh+=1831565813;return e=Math.imul(e^e>>>15,e|1),e^=e+Math.imul(e^e>>>7,e|61),((e^e>>>14)>>>0)/4294967296}function Sg(i){return i*Pr}function bg(i){return i*Ra}function Eg(i){return(i&i-1)===0&&i!==0}function wg(i){return Math.pow(2,Math.ceil(Math.log(i)/Math.LN2))}function Tg(i){return Math.pow(2,Math.floor(Math.log(i)/Math.LN2))}function Ag(i,e,t,n,s){const r=Math.cos,a=Math.sin,o=r(t/2),l=a(t/2),c=r((e+n)/2),u=a((e+n)/2),h=r((e-n)/2),d=a((e-n)/2),f=r((n-e)/2),g=a((n-e)/2);switch(s){case"XYX":i.set(o*u,l*h,l*d,o*c);break;case"YZY":i.set(l*d,o*u,l*h,o*c);break;case"ZXZ":i.set(l*h,l*d,o*u,o*c);break;case"XZX":i.set(o*u,l*g,l*f,o*c);break;case"YXY":i.set(l*f,o*u,l*g,o*c);break;case"ZYZ":i.set(l*g,l*f,o*u,o*c);break;default:console.warn("THREE.MathUtils: .setQuaternionFromProperEuler() encountered an unknown order: "+s)}}function oi(i,e){switch(e.constructor){case Float32Array:return i;case Uint32Array:return i/4294967295;case Uint16Array:return i/65535;case Uint8Array:return i/255;case Int32Array:return Math.max(i/2147483647,-1);case Int16Array:return Math.max(i/32767,-1);case Int8Array:return Math.max(i/127,-1);default:throw new Error("Invalid component type.")}}function wt(i,e){switch(e.constructor){case Float32Array:return i;case Uint32Array:return Math.round(i*4294967295);case Uint16Array:return Math.round(i*65535);case Uint8Array:return Math.round(i*255);case Int32Array:return Math.round(i*2147483647);case Int16Array:return Math.round(i*32767);case Int8Array:return Math.round(i*127);default:throw new Error("Invalid component type.")}}const Zc={DEG2RAD:Pr,RAD2DEG:Ra,generateUUID:zi,clamp:Mn,euclideanModulo:xu,mapLinear:dg,inverseLerp:fg,lerp:Ea,damp:pg,pingpong:mg,smoothstep:gg,smootherstep:_g,randInt:vg,randFloat:xg,randFloatSpread:yg,seededRandom:Mg,degToRad:Sg,radToDeg:bg,isPowerOfTwo:Eg,ceilPowerOfTwo:wg,floorPowerOfTwo:Tg,setQuaternionFromProperEuler:Ag,normalize:wt,denormalize:oi};class qe{constructor(e=0,t=0){qe.prototype.isVector2=!0,this.x=e,this.y=t}get width(){return this.x}set width(e){this.x=e}get height(){return this.y}set height(e){this.y=e}set(e,t){return this.x=e,this.y=t,this}setScalar(e){return this.x=e,this.y=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y)}copy(e){return this.x=e.x,this.y=e.y,this}add(e){return this.x+=e.x,this.y+=e.y,this}addScalar(e){return this.x+=e,this.y+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this}subScalar(e){return this.x-=e,this.y-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this}multiply(e){return this.x*=e.x,this.y*=e.y,this}multiplyScalar(e){return this.x*=e,this.y*=e,this}divide(e){return this.x/=e.x,this.y/=e.y,this}divideScalar(e){return this.multiplyScalar(1/e)}applyMatrix3(e){const t=this.x,n=this.y,s=e.elements;return this.x=s[0]*t+s[3]*n+s[6],this.y=s[1]*t+s[4]*n+s[7],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this}negate(){return this.x=-this.x,this.y=-this.y,this}dot(e){return this.x*e.x+this.y*e.y}cross(e){return this.x*e.y-this.y*e.x}lengthSq(){return this.x*this.x+this.y*this.y}length(){return Math.sqrt(this.x*this.x+this.y*this.y)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)}normalize(){return this.divideScalar(this.length()||1)}angle(){return Math.atan2(-this.y,-this.x)+Math.PI}angleTo(e){const t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;const n=this.dot(e)/t;return Math.acos(Mn(n,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){const t=this.x-e.x,n=this.y-e.y;return t*t+n*n}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this}equals(e){return e.x===this.x&&e.y===this.y}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this}rotateAround(e,t){const n=Math.cos(t),s=Math.sin(t),r=this.x-e.x,a=this.y-e.y;return this.x=r*n-a*s+e.x,this.y=r*s+a*n+e.y,this}random(){return this.x=Math.random(),this.y=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y}}class rt{constructor(e,t,n,s,r,a,o,l,c){rt.prototype.isMatrix3=!0,this.elements=[1,0,0,0,1,0,0,0,1],e!==void 0&&this.set(e,t,n,s,r,a,o,l,c)}set(e,t,n,s,r,a,o,l,c){const u=this.elements;return u[0]=e,u[1]=s,u[2]=o,u[3]=t,u[4]=r,u[5]=l,u[6]=n,u[7]=a,u[8]=c,this}identity(){return this.set(1,0,0,0,1,0,0,0,1),this}copy(e){const t=this.elements,n=e.elements;return t[0]=n[0],t[1]=n[1],t[2]=n[2],t[3]=n[3],t[4]=n[4],t[5]=n[5],t[6]=n[6],t[7]=n[7],t[8]=n[8],this}extractBasis(e,t,n){return e.setFromMatrix3Column(this,0),t.setFromMatrix3Column(this,1),n.setFromMatrix3Column(this,2),this}setFromMatrix4(e){const t=e.elements;return this.set(t[0],t[4],t[8],t[1],t[5],t[9],t[2],t[6],t[10]),this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){const n=e.elements,s=t.elements,r=this.elements,a=n[0],o=n[3],l=n[6],c=n[1],u=n[4],h=n[7],d=n[2],f=n[5],g=n[8],v=s[0],m=s[3],p=s[6],S=s[1],y=s[4],w=s[7],O=s[2],A=s[5],P=s[8];return r[0]=a*v+o*S+l*O,r[3]=a*m+o*y+l*A,r[6]=a*p+o*w+l*P,r[1]=c*v+u*S+h*O,r[4]=c*m+u*y+h*A,r[7]=c*p+u*w+h*P,r[2]=d*v+f*S+g*O,r[5]=d*m+f*y+g*A,r[8]=d*p+f*w+g*P,this}multiplyScalar(e){const t=this.elements;return t[0]*=e,t[3]*=e,t[6]*=e,t[1]*=e,t[4]*=e,t[7]*=e,t[2]*=e,t[5]*=e,t[8]*=e,this}determinant(){const e=this.elements,t=e[0],n=e[1],s=e[2],r=e[3],a=e[4],o=e[5],l=e[6],c=e[7],u=e[8];return t*a*u-t*o*c-n*r*u+n*o*l+s*r*c-s*a*l}invert(){const e=this.elements,t=e[0],n=e[1],s=e[2],r=e[3],a=e[4],o=e[5],l=e[6],c=e[7],u=e[8],h=u*a-o*c,d=o*l-u*r,f=c*r-a*l,g=t*h+n*d+s*f;if(g===0)return this.set(0,0,0,0,0,0,0,0,0);const v=1/g;return e[0]=h*v,e[1]=(s*c-u*n)*v,e[2]=(o*n-s*a)*v,e[3]=d*v,e[4]=(u*t-s*l)*v,e[5]=(s*r-o*t)*v,e[6]=f*v,e[7]=(n*l-c*t)*v,e[8]=(a*t-n*r)*v,this}transpose(){let e;const t=this.elements;return e=t[1],t[1]=t[3],t[3]=e,e=t[2],t[2]=t[6],t[6]=e,e=t[5],t[5]=t[7],t[7]=e,this}getNormalMatrix(e){return this.setFromMatrix4(e).invert().transpose()}transposeIntoArray(e){const t=this.elements;return e[0]=t[0],e[1]=t[3],e[2]=t[6],e[3]=t[1],e[4]=t[4],e[5]=t[7],e[6]=t[2],e[7]=t[5],e[8]=t[8],this}setUvTransform(e,t,n,s,r,a,o){const l=Math.cos(r),c=Math.sin(r);return this.set(n*l,n*c,-n*(l*a+c*o)+a+e,-s*c,s*l,-s*(-c*a+l*o)+o+t,0,0,1),this}scale(e,t){return this.premultiply(Dl.makeScale(e,t)),this}rotate(e){return this.premultiply(Dl.makeRotation(-e)),this}translate(e,t){return this.premultiply(Dl.makeTranslation(e,t)),this}makeTranslation(e,t){return e.isVector2?this.set(1,0,e.x,0,1,e.y,0,0,1):this.set(1,0,e,0,1,t,0,0,1),this}makeRotation(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,-n,0,n,t,0,0,0,1),this}makeScale(e,t){return this.set(e,0,0,0,t,0,0,0,1),this}equals(e){const t=this.elements,n=e.elements;for(let s=0;s<9;s++)if(t[s]!==n[s])return!1;return!0}fromArray(e,t=0){for(let n=0;n<9;n++)this.elements[n]=e[n+t];return this}toArray(e=[],t=0){const n=this.elements;return e[t]=n[0],e[t+1]=n[1],e[t+2]=n[2],e[t+3]=n[3],e[t+4]=n[4],e[t+5]=n[5],e[t+6]=n[6],e[t+7]=n[7],e[t+8]=n[8],e}clone(){return new this.constructor().fromArray(this.elements)}}const Dl=new rt;function Bf(i){for(let e=i.length-1;e>=0;--e)if(i[e]>=65535)return!0;return!1}function Wo(i){return document.createElementNS("http://www.w3.org/1999/xhtml",i)}function Cg(){const i=Wo("canvas");return i.style.display="block",i}const bh={};function Lr(i){i in bh||(bh[i]=!0,console.warn(i))}function Rg(i,e,t){return new Promise(function(n,s){function r(){switch(i.clientWaitSync(e,i.SYNC_FLUSH_COMMANDS_BIT,0)){case i.WAIT_FAILED:s();break;case i.TIMEOUT_EXPIRED:setTimeout(r,t);break;default:n()}}setTimeout(r,t)})}const Eh=new rt().set(.8224621,.177538,0,.0331941,.9668058,0,.0170827,.0723974,.9105199),wh=new rt().set(1.2249401,-.2249404,0,-.0420569,1.0420571,0,-.0196376,-.0786361,1.0982735),la={[fs]:{transfer:ko,primaries:Ho,luminanceCoefficients:[.2126,.7152,.0722],toReference:i=>i,fromReference:i=>i},[xi]:{transfer:Ft,primaries:Ho,luminanceCoefficients:[.2126,.7152,.0722],toReference:i=>i.convertSRGBToLinear(),fromReference:i=>i.convertLinearToSRGB()},[sl]:{transfer:ko,primaries:Vo,luminanceCoefficients:[.2289,.6917,.0793],toReference:i=>i.applyMatrix3(wh),fromReference:i=>i.applyMatrix3(Eh)},[vu]:{transfer:Ft,primaries:Vo,luminanceCoefficients:[.2289,.6917,.0793],toReference:i=>i.convertSRGBToLinear().applyMatrix3(wh),fromReference:i=>i.applyMatrix3(Eh).convertLinearToSRGB()}},Pg=new Set([fs,sl]),St={enabled:!0,_workingColorSpace:fs,get workingColorSpace(){return this._workingColorSpace},set workingColorSpace(i){if(!Pg.has(i))throw new Error(`Unsupported working color space, "${i}".`);this._workingColorSpace=i},convert:function(i,e,t){if(this.enabled===!1||e===t||!e||!t)return i;const n=la[e].toReference,s=la[t].fromReference;return s(n(i))},fromWorkingColorSpace:function(i,e){return this.convert(i,this._workingColorSpace,e)},toWorkingColorSpace:function(i,e){return this.convert(i,e,this._workingColorSpace)},getPrimaries:function(i){return la[i].primaries},getTransfer:function(i){return i===rs?ko:la[i].transfer},getLuminanceCoefficients:function(i,e=this._workingColorSpace){return i.fromArray(la[e].luminanceCoefficients)}};function Dr(i){return i<.04045?i*.0773993808:Math.pow(i*.9478672986+.0521327014,2.4)}function Il(i){return i<.0031308?i*12.92:1.055*Math.pow(i,.41666)-.055}let nr;class Lg{static getDataURL(e){if(/^data:/i.test(e.src)||typeof HTMLCanvasElement>"u")return e.src;let t;if(e instanceof HTMLCanvasElement)t=e;else{nr===void 0&&(nr=Wo("canvas")),nr.width=e.width,nr.height=e.height;const n=nr.getContext("2d");e instanceof ImageData?n.putImageData(e,0,0):n.drawImage(e,0,0,e.width,e.height),t=nr}return t.width>2048||t.height>2048?(console.warn("THREE.ImageUtils.getDataURL: Image converted to jpg for performance reasons",e),t.toDataURL("image/jpeg",.6)):t.toDataURL("image/png")}static sRGBToLinear(e){if(typeof HTMLImageElement<"u"&&e instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&e instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&e instanceof ImageBitmap){const t=Wo("canvas");t.width=e.width,t.height=e.height;const n=t.getContext("2d");n.drawImage(e,0,0,e.width,e.height);const s=n.getImageData(0,0,e.width,e.height),r=s.data;for(let a=0;a<r.length;a++)r[a]=Dr(r[a]/255)*255;return n.putImageData(s,0,0),t}else if(e.data){const t=e.data.slice(0);for(let n=0;n<t.length;n++)t instanceof Uint8Array||t instanceof Uint8ClampedArray?t[n]=Math.floor(Dr(t[n]/255)*255):t[n]=Dr(t[n]);return{data:t,width:e.width,height:e.height}}else return console.warn("THREE.ImageUtils.sRGBToLinear(): Unsupported image type. No color space conversion applied."),e}}let Dg=0;class zf{constructor(e=null){this.isSource=!0,Object.defineProperty(this,"id",{value:Dg++}),this.uuid=zi(),this.data=e,this.dataReady=!0,this.version=0}set needsUpdate(e){e===!0&&this.version++}toJSON(e){const t=e===void 0||typeof e=="string";if(!t&&e.images[this.uuid]!==void 0)return e.images[this.uuid];const n={uuid:this.uuid,url:""},s=this.data;if(s!==null){let r;if(Array.isArray(s)){r=[];for(let a=0,o=s.length;a<o;a++)s[a].isDataTexture?r.push(Ul(s[a].image)):r.push(Ul(s[a]))}else r=Ul(s);n.url=r}return t||(e.images[this.uuid]=n),n}}function Ul(i){return typeof HTMLImageElement<"u"&&i instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&i instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&i instanceof ImageBitmap?Lg.getDataURL(i):i.data?{data:Array.from(i.data),width:i.width,height:i.height,type:i.data.constructor.name}:(console.warn("THREE.Texture: Unable to serialize Texture."),{})}let Ig=0;class Ln extends jr{constructor(e=Ln.DEFAULT_IMAGE,t=Ln.DEFAULT_MAPPING,n=Ds,s=Ds,r=ai,a=Is,o=ci,l=Gi,c=Ln.DEFAULT_ANISOTROPY,u=rs){super(),this.isTexture=!0,Object.defineProperty(this,"id",{value:Ig++}),this.uuid=zi(),this.name="",this.source=new zf(e),this.mipmaps=[],this.mapping=t,this.channel=0,this.wrapS=n,this.wrapT=s,this.magFilter=r,this.minFilter=a,this.anisotropy=c,this.format=o,this.internalFormat=null,this.type=l,this.offset=new qe(0,0),this.repeat=new qe(1,1),this.center=new qe(0,0),this.rotation=0,this.matrixAutoUpdate=!0,this.matrix=new rt,this.generateMipmaps=!0,this.premultiplyAlpha=!1,this.flipY=!0,this.unpackAlignment=4,this.colorSpace=u,this.userData={},this.version=0,this.onUpdate=null,this.isRenderTargetTexture=!1,this.pmremVersion=0}get image(){return this.source.data}set image(e=null){this.source.data=e}updateMatrix(){this.matrix.setUvTransform(this.offset.x,this.offset.y,this.repeat.x,this.repeat.y,this.rotation,this.center.x,this.center.y)}clone(){return new this.constructor().copy(this)}copy(e){return this.name=e.name,this.source=e.source,this.mipmaps=e.mipmaps.slice(0),this.mapping=e.mapping,this.channel=e.channel,this.wrapS=e.wrapS,this.wrapT=e.wrapT,this.magFilter=e.magFilter,this.minFilter=e.minFilter,this.anisotropy=e.anisotropy,this.format=e.format,this.internalFormat=e.internalFormat,this.type=e.type,this.offset.copy(e.offset),this.repeat.copy(e.repeat),this.center.copy(e.center),this.rotation=e.rotation,this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrix.copy(e.matrix),this.generateMipmaps=e.generateMipmaps,this.premultiplyAlpha=e.premultiplyAlpha,this.flipY=e.flipY,this.unpackAlignment=e.unpackAlignment,this.colorSpace=e.colorSpace,this.userData=JSON.parse(JSON.stringify(e.userData)),this.needsUpdate=!0,this}toJSON(e){const t=e===void 0||typeof e=="string";if(!t&&e.textures[this.uuid]!==void 0)return e.textures[this.uuid];const n={metadata:{version:4.6,type:"Texture",generator:"Texture.toJSON"},uuid:this.uuid,name:this.name,image:this.source.toJSON(e).uuid,mapping:this.mapping,channel:this.channel,repeat:[this.repeat.x,this.repeat.y],offset:[this.offset.x,this.offset.y],center:[this.center.x,this.center.y],rotation:this.rotation,wrap:[this.wrapS,this.wrapT],format:this.format,internalFormat:this.internalFormat,type:this.type,colorSpace:this.colorSpace,minFilter:this.minFilter,magFilter:this.magFilter,anisotropy:this.anisotropy,flipY:this.flipY,generateMipmaps:this.generateMipmaps,premultiplyAlpha:this.premultiplyAlpha,unpackAlignment:this.unpackAlignment};return Object.keys(this.userData).length>0&&(n.userData=this.userData),t||(e.textures[this.uuid]=n),n}dispose(){this.dispatchEvent({type:"dispose"})}transformUv(e){if(this.mapping!==wf)return e;if(e.applyMatrix3(this.matrix),e.x<0||e.x>1)switch(this.wrapS){case Sc:e.x=e.x-Math.floor(e.x);break;case Ds:e.x=e.x<0?0:1;break;case bc:Math.abs(Math.floor(e.x)%2)===1?e.x=Math.ceil(e.x)-e.x:e.x=e.x-Math.floor(e.x);break}if(e.y<0||e.y>1)switch(this.wrapT){case Sc:e.y=e.y-Math.floor(e.y);break;case Ds:e.y=e.y<0?0:1;break;case bc:Math.abs(Math.floor(e.y)%2)===1?e.y=Math.ceil(e.y)-e.y:e.y=e.y-Math.floor(e.y);break}return this.flipY&&(e.y=1-e.y),e}set needsUpdate(e){e===!0&&(this.version++,this.source.needsUpdate=!0)}set needsPMREMUpdate(e){e===!0&&this.pmremVersion++}}Ln.DEFAULT_IMAGE=null;Ln.DEFAULT_MAPPING=wf;Ln.DEFAULT_ANISOTROPY=1;class tn{constructor(e=0,t=0,n=0,s=1){tn.prototype.isVector4=!0,this.x=e,this.y=t,this.z=n,this.w=s}get width(){return this.z}set width(e){this.z=e}get height(){return this.w}set height(e){this.w=e}set(e,t,n,s){return this.x=e,this.y=t,this.z=n,this.w=s,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this.w=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setW(e){return this.w=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;case 3:this.w=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;case 3:return this.w;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z,this.w)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this.w=e.w!==void 0?e.w:1,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this.w+=e.w,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this.w+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this.w=e.w+t.w,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this.w+=e.w*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this.w-=e.w,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this.w-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this.w=e.w-t.w,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this.w*=e.w,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this.w*=e,this}applyMatrix4(e){const t=this.x,n=this.y,s=this.z,r=this.w,a=e.elements;return this.x=a[0]*t+a[4]*n+a[8]*s+a[12]*r,this.y=a[1]*t+a[5]*n+a[9]*s+a[13]*r,this.z=a[2]*t+a[6]*n+a[10]*s+a[14]*r,this.w=a[3]*t+a[7]*n+a[11]*s+a[15]*r,this}divideScalar(e){return this.multiplyScalar(1/e)}setAxisAngleFromQuaternion(e){this.w=2*Math.acos(e.w);const t=Math.sqrt(1-e.w*e.w);return t<1e-4?(this.x=1,this.y=0,this.z=0):(this.x=e.x/t,this.y=e.y/t,this.z=e.z/t),this}setAxisAngleFromRotationMatrix(e){let t,n,s,r;const l=e.elements,c=l[0],u=l[4],h=l[8],d=l[1],f=l[5],g=l[9],v=l[2],m=l[6],p=l[10];if(Math.abs(u-d)<.01&&Math.abs(h-v)<.01&&Math.abs(g-m)<.01){if(Math.abs(u+d)<.1&&Math.abs(h+v)<.1&&Math.abs(g+m)<.1&&Math.abs(c+f+p-3)<.1)return this.set(1,0,0,0),this;t=Math.PI;const y=(c+1)/2,w=(f+1)/2,O=(p+1)/2,A=(u+d)/4,P=(h+v)/4,N=(g+m)/4;return y>w&&y>O?y<.01?(n=0,s=.707106781,r=.707106781):(n=Math.sqrt(y),s=A/n,r=P/n):w>O?w<.01?(n=.707106781,s=0,r=.707106781):(s=Math.sqrt(w),n=A/s,r=N/s):O<.01?(n=.707106781,s=.707106781,r=0):(r=Math.sqrt(O),n=P/r,s=N/r),this.set(n,s,r,t),this}let S=Math.sqrt((m-g)*(m-g)+(h-v)*(h-v)+(d-u)*(d-u));return Math.abs(S)<.001&&(S=1),this.x=(m-g)/S,this.y=(h-v)/S,this.z=(d-u)/S,this.w=Math.acos((c+f+p-1)/2),this}setFromMatrixPosition(e){const t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this.w=t[15],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this.w=Math.min(this.w,e.w),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this.w=Math.max(this.w,e.w),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this.z=Math.max(e.z,Math.min(t.z,this.z)),this.w=Math.max(e.w,Math.min(t.w,this.w)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this.z=Math.max(e,Math.min(t,this.z)),this.w=Math.max(e,Math.min(t,this.w)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this.w=Math.floor(this.w),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this.w=Math.ceil(this.w),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this.w=Math.round(this.w),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this.w=Math.trunc(this.w),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this.w=-this.w,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z+this.w*e.w}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)+Math.abs(this.w)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this.w+=(e.w-this.w)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this.z=e.z+(t.z-e.z)*n,this.w=e.w+(t.w-e.w)*n,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z&&e.w===this.w}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this.w=e[t+3],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e[t+3]=this.w,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this.w=e.getW(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this.w=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z,yield this.w}}class Ug extends jr{constructor(e=1,t=1,n={}){super(),this.isRenderTarget=!0,this.width=e,this.height=t,this.depth=1,this.scissor=new tn(0,0,e,t),this.scissorTest=!1,this.viewport=new tn(0,0,e,t);const s={width:e,height:t,depth:1};n=Object.assign({generateMipmaps:!1,internalFormat:null,minFilter:ai,depthBuffer:!0,stencilBuffer:!1,resolveDepthBuffer:!0,resolveStencilBuffer:!0,depthTexture:null,samples:0,count:1},n);const r=new Ln(s,n.mapping,n.wrapS,n.wrapT,n.magFilter,n.minFilter,n.format,n.type,n.anisotropy,n.colorSpace);r.flipY=!1,r.generateMipmaps=n.generateMipmaps,r.internalFormat=n.internalFormat,this.textures=[];const a=n.count;for(let o=0;o<a;o++)this.textures[o]=r.clone(),this.textures[o].isRenderTargetTexture=!0;this.depthBuffer=n.depthBuffer,this.stencilBuffer=n.stencilBuffer,this.resolveDepthBuffer=n.resolveDepthBuffer,this.resolveStencilBuffer=n.resolveStencilBuffer,this.depthTexture=n.depthTexture,this.samples=n.samples}get texture(){return this.textures[0]}set texture(e){this.textures[0]=e}setSize(e,t,n=1){if(this.width!==e||this.height!==t||this.depth!==n){this.width=e,this.height=t,this.depth=n;for(let s=0,r=this.textures.length;s<r;s++)this.textures[s].image.width=e,this.textures[s].image.height=t,this.textures[s].image.depth=n;this.dispose()}this.viewport.set(0,0,e,t),this.scissor.set(0,0,e,t)}clone(){return new this.constructor().copy(this)}copy(e){this.width=e.width,this.height=e.height,this.depth=e.depth,this.scissor.copy(e.scissor),this.scissorTest=e.scissorTest,this.viewport.copy(e.viewport),this.textures.length=0;for(let n=0,s=e.textures.length;n<s;n++)this.textures[n]=e.textures[n].clone(),this.textures[n].isRenderTargetTexture=!0;const t=Object.assign({},e.texture.image);return this.texture.source=new zf(t),this.depthBuffer=e.depthBuffer,this.stencilBuffer=e.stencilBuffer,this.resolveDepthBuffer=e.resolveDepthBuffer,this.resolveStencilBuffer=e.resolveStencilBuffer,e.depthTexture!==null&&(this.depthTexture=e.depthTexture.clone()),this.samples=e.samples,this}dispose(){this.dispatchEvent({type:"dispose"})}}class Bs extends Ug{constructor(e=1,t=1,n={}){super(e,t,n),this.isWebGLRenderTarget=!0}}class kf extends Ln{constructor(e=null,t=1,n=1,s=1){super(null),this.isDataArrayTexture=!0,this.image={data:e,width:t,height:n,depth:s},this.magFilter=Kn,this.minFilter=Kn,this.wrapR=Ds,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1,this.layerUpdates=new Set}addLayerUpdate(e){this.layerUpdates.add(e)}clearLayerUpdates(){this.layerUpdates.clear()}}class Ng extends Ln{constructor(e=null,t=1,n=1,s=1){super(null),this.isData3DTexture=!0,this.image={data:e,width:t,height:n,depth:s},this.magFilter=Kn,this.minFilter=Kn,this.wrapR=Ds,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}}class zs{constructor(e=0,t=0,n=0,s=1){this.isQuaternion=!0,this._x=e,this._y=t,this._z=n,this._w=s}static slerpFlat(e,t,n,s,r,a,o){let l=n[s+0],c=n[s+1],u=n[s+2],h=n[s+3];const d=r[a+0],f=r[a+1],g=r[a+2],v=r[a+3];if(o===0){e[t+0]=l,e[t+1]=c,e[t+2]=u,e[t+3]=h;return}if(o===1){e[t+0]=d,e[t+1]=f,e[t+2]=g,e[t+3]=v;return}if(h!==v||l!==d||c!==f||u!==g){let m=1-o;const p=l*d+c*f+u*g+h*v,S=p>=0?1:-1,y=1-p*p;if(y>Number.EPSILON){const O=Math.sqrt(y),A=Math.atan2(O,p*S);m=Math.sin(m*A)/O,o=Math.sin(o*A)/O}const w=o*S;if(l=l*m+d*w,c=c*m+f*w,u=u*m+g*w,h=h*m+v*w,m===1-o){const O=1/Math.sqrt(l*l+c*c+u*u+h*h);l*=O,c*=O,u*=O,h*=O}}e[t]=l,e[t+1]=c,e[t+2]=u,e[t+3]=h}static multiplyQuaternionsFlat(e,t,n,s,r,a){const o=n[s],l=n[s+1],c=n[s+2],u=n[s+3],h=r[a],d=r[a+1],f=r[a+2],g=r[a+3];return e[t]=o*g+u*h+l*f-c*d,e[t+1]=l*g+u*d+c*h-o*f,e[t+2]=c*g+u*f+o*d-l*h,e[t+3]=u*g-o*h-l*d-c*f,e}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get w(){return this._w}set w(e){this._w=e,this._onChangeCallback()}set(e,t,n,s){return this._x=e,this._y=t,this._z=n,this._w=s,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._w)}copy(e){return this._x=e.x,this._y=e.y,this._z=e.z,this._w=e.w,this._onChangeCallback(),this}setFromEuler(e,t=!0){const n=e._x,s=e._y,r=e._z,a=e._order,o=Math.cos,l=Math.sin,c=o(n/2),u=o(s/2),h=o(r/2),d=l(n/2),f=l(s/2),g=l(r/2);switch(a){case"XYZ":this._x=d*u*h+c*f*g,this._y=c*f*h-d*u*g,this._z=c*u*g+d*f*h,this._w=c*u*h-d*f*g;break;case"YXZ":this._x=d*u*h+c*f*g,this._y=c*f*h-d*u*g,this._z=c*u*g-d*f*h,this._w=c*u*h+d*f*g;break;case"ZXY":this._x=d*u*h-c*f*g,this._y=c*f*h+d*u*g,this._z=c*u*g+d*f*h,this._w=c*u*h-d*f*g;break;case"ZYX":this._x=d*u*h-c*f*g,this._y=c*f*h+d*u*g,this._z=c*u*g-d*f*h,this._w=c*u*h+d*f*g;break;case"YZX":this._x=d*u*h+c*f*g,this._y=c*f*h+d*u*g,this._z=c*u*g-d*f*h,this._w=c*u*h-d*f*g;break;case"XZY":this._x=d*u*h-c*f*g,this._y=c*f*h-d*u*g,this._z=c*u*g+d*f*h,this._w=c*u*h+d*f*g;break;default:console.warn("THREE.Quaternion: .setFromEuler() encountered an unknown order: "+a)}return t===!0&&this._onChangeCallback(),this}setFromAxisAngle(e,t){const n=t/2,s=Math.sin(n);return this._x=e.x*s,this._y=e.y*s,this._z=e.z*s,this._w=Math.cos(n),this._onChangeCallback(),this}setFromRotationMatrix(e){const t=e.elements,n=t[0],s=t[4],r=t[8],a=t[1],o=t[5],l=t[9],c=t[2],u=t[6],h=t[10],d=n+o+h;if(d>0){const f=.5/Math.sqrt(d+1);this._w=.25/f,this._x=(u-l)*f,this._y=(r-c)*f,this._z=(a-s)*f}else if(n>o&&n>h){const f=2*Math.sqrt(1+n-o-h);this._w=(u-l)/f,this._x=.25*f,this._y=(s+a)/f,this._z=(r+c)/f}else if(o>h){const f=2*Math.sqrt(1+o-n-h);this._w=(r-c)/f,this._x=(s+a)/f,this._y=.25*f,this._z=(l+u)/f}else{const f=2*Math.sqrt(1+h-n-o);this._w=(a-s)/f,this._x=(r+c)/f,this._y=(l+u)/f,this._z=.25*f}return this._onChangeCallback(),this}setFromUnitVectors(e,t){let n=e.dot(t)+1;return n<Number.EPSILON?(n=0,Math.abs(e.x)>Math.abs(e.z)?(this._x=-e.y,this._y=e.x,this._z=0,this._w=n):(this._x=0,this._y=-e.z,this._z=e.y,this._w=n)):(this._x=e.y*t.z-e.z*t.y,this._y=e.z*t.x-e.x*t.z,this._z=e.x*t.y-e.y*t.x,this._w=n),this.normalize()}angleTo(e){return 2*Math.acos(Math.abs(Mn(this.dot(e),-1,1)))}rotateTowards(e,t){const n=this.angleTo(e);if(n===0)return this;const s=Math.min(1,t/n);return this.slerp(e,s),this}identity(){return this.set(0,0,0,1)}invert(){return this.conjugate()}conjugate(){return this._x*=-1,this._y*=-1,this._z*=-1,this._onChangeCallback(),this}dot(e){return this._x*e._x+this._y*e._y+this._z*e._z+this._w*e._w}lengthSq(){return this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w}length(){return Math.sqrt(this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w)}normalize(){let e=this.length();return e===0?(this._x=0,this._y=0,this._z=0,this._w=1):(e=1/e,this._x=this._x*e,this._y=this._y*e,this._z=this._z*e,this._w=this._w*e),this._onChangeCallback(),this}multiply(e){return this.multiplyQuaternions(this,e)}premultiply(e){return this.multiplyQuaternions(e,this)}multiplyQuaternions(e,t){const n=e._x,s=e._y,r=e._z,a=e._w,o=t._x,l=t._y,c=t._z,u=t._w;return this._x=n*u+a*o+s*c-r*l,this._y=s*u+a*l+r*o-n*c,this._z=r*u+a*c+n*l-s*o,this._w=a*u-n*o-s*l-r*c,this._onChangeCallback(),this}slerp(e,t){if(t===0)return this;if(t===1)return this.copy(e);const n=this._x,s=this._y,r=this._z,a=this._w;let o=a*e._w+n*e._x+s*e._y+r*e._z;if(o<0?(this._w=-e._w,this._x=-e._x,this._y=-e._y,this._z=-e._z,o=-o):this.copy(e),o>=1)return this._w=a,this._x=n,this._y=s,this._z=r,this;const l=1-o*o;if(l<=Number.EPSILON){const f=1-t;return this._w=f*a+t*this._w,this._x=f*n+t*this._x,this._y=f*s+t*this._y,this._z=f*r+t*this._z,this.normalize(),this}const c=Math.sqrt(l),u=Math.atan2(c,o),h=Math.sin((1-t)*u)/c,d=Math.sin(t*u)/c;return this._w=a*h+this._w*d,this._x=n*h+this._x*d,this._y=s*h+this._y*d,this._z=r*h+this._z*d,this._onChangeCallback(),this}slerpQuaternions(e,t,n){return this.copy(e).slerp(t,n)}random(){const e=2*Math.PI*Math.random(),t=2*Math.PI*Math.random(),n=Math.random(),s=Math.sqrt(1-n),r=Math.sqrt(n);return this.set(s*Math.sin(e),s*Math.cos(e),r*Math.sin(t),r*Math.cos(t))}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._w===this._w}fromArray(e,t=0){return this._x=e[t],this._y=e[t+1],this._z=e[t+2],this._w=e[t+3],this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._w,e}fromBufferAttribute(e,t){return this._x=e.getX(t),this._y=e.getY(t),this._z=e.getZ(t),this._w=e.getW(t),this._onChangeCallback(),this}toJSON(){return this.toArray()}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._w}}class k{constructor(e=0,t=0,n=0){k.prototype.isVector3=!0,this.x=e,this.y=t,this.z=n}set(e,t,n){return n===void 0&&(n=this.z),this.x=e,this.y=t,this.z=n,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this}multiplyVectors(e,t){return this.x=e.x*t.x,this.y=e.y*t.y,this.z=e.z*t.z,this}applyEuler(e){return this.applyQuaternion(Th.setFromEuler(e))}applyAxisAngle(e,t){return this.applyQuaternion(Th.setFromAxisAngle(e,t))}applyMatrix3(e){const t=this.x,n=this.y,s=this.z,r=e.elements;return this.x=r[0]*t+r[3]*n+r[6]*s,this.y=r[1]*t+r[4]*n+r[7]*s,this.z=r[2]*t+r[5]*n+r[8]*s,this}applyNormalMatrix(e){return this.applyMatrix3(e).normalize()}applyMatrix4(e){const t=this.x,n=this.y,s=this.z,r=e.elements,a=1/(r[3]*t+r[7]*n+r[11]*s+r[15]);return this.x=(r[0]*t+r[4]*n+r[8]*s+r[12])*a,this.y=(r[1]*t+r[5]*n+r[9]*s+r[13])*a,this.z=(r[2]*t+r[6]*n+r[10]*s+r[14])*a,this}applyQuaternion(e){const t=this.x,n=this.y,s=this.z,r=e.x,a=e.y,o=e.z,l=e.w,c=2*(a*s-o*n),u=2*(o*t-r*s),h=2*(r*n-a*t);return this.x=t+l*c+a*h-o*u,this.y=n+l*u+o*c-r*h,this.z=s+l*h+r*u-a*c,this}project(e){return this.applyMatrix4(e.matrixWorldInverse).applyMatrix4(e.projectionMatrix)}unproject(e){return this.applyMatrix4(e.projectionMatrixInverse).applyMatrix4(e.matrixWorld)}transformDirection(e){const t=this.x,n=this.y,s=this.z,r=e.elements;return this.x=r[0]*t+r[4]*n+r[8]*s,this.y=r[1]*t+r[5]*n+r[9]*s,this.z=r[2]*t+r[6]*n+r[10]*s,this.normalize()}divide(e){return this.x/=e.x,this.y/=e.y,this.z/=e.z,this}divideScalar(e){return this.multiplyScalar(1/e)}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this.z=Math.max(e.z,Math.min(t.z,this.z)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this.z=Math.max(e,Math.min(t,this.z)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this.z=e.z+(t.z-e.z)*n,this}cross(e){return this.crossVectors(this,e)}crossVectors(e,t){const n=e.x,s=e.y,r=e.z,a=t.x,o=t.y,l=t.z;return this.x=s*l-r*o,this.y=r*a-n*l,this.z=n*o-s*a,this}projectOnVector(e){const t=e.lengthSq();if(t===0)return this.set(0,0,0);const n=e.dot(this)/t;return this.copy(e).multiplyScalar(n)}projectOnPlane(e){return Nl.copy(this).projectOnVector(e),this.sub(Nl)}reflect(e){return this.sub(Nl.copy(e).multiplyScalar(2*this.dot(e)))}angleTo(e){const t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;const n=this.dot(e)/t;return Math.acos(Mn(n,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){const t=this.x-e.x,n=this.y-e.y,s=this.z-e.z;return t*t+n*n+s*s}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)+Math.abs(this.z-e.z)}setFromSpherical(e){return this.setFromSphericalCoords(e.radius,e.phi,e.theta)}setFromSphericalCoords(e,t,n){const s=Math.sin(t)*e;return this.x=s*Math.sin(n),this.y=Math.cos(t)*e,this.z=s*Math.cos(n),this}setFromCylindrical(e){return this.setFromCylindricalCoords(e.radius,e.theta,e.y)}setFromCylindricalCoords(e,t,n){return this.x=e*Math.sin(t),this.y=n,this.z=e*Math.cos(t),this}setFromMatrixPosition(e){const t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this}setFromMatrixScale(e){const t=this.setFromMatrixColumn(e,0).length(),n=this.setFromMatrixColumn(e,1).length(),s=this.setFromMatrixColumn(e,2).length();return this.x=t,this.y=n,this.z=s,this}setFromMatrixColumn(e,t){return this.fromArray(e.elements,t*4)}setFromMatrix3Column(e,t){return this.fromArray(e.elements,t*3)}setFromEuler(e){return this.x=e._x,this.y=e._y,this.z=e._z,this}setFromColor(e){return this.x=e.r,this.y=e.g,this.z=e.b,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this}randomDirection(){const e=Math.random()*Math.PI*2,t=Math.random()*2-1,n=Math.sqrt(1-t*t);return this.x=n*Math.cos(e),this.y=t,this.z=n*Math.sin(e),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z}}const Nl=new k,Th=new zs;class Ua{constructor(e=new k(1/0,1/0,1/0),t=new k(-1/0,-1/0,-1/0)){this.isBox3=!0,this.min=e,this.max=t}set(e,t){return this.min.copy(e),this.max.copy(t),this}setFromArray(e){this.makeEmpty();for(let t=0,n=e.length;t<n;t+=3)this.expandByPoint(ti.fromArray(e,t));return this}setFromBufferAttribute(e){this.makeEmpty();for(let t=0,n=e.count;t<n;t++)this.expandByPoint(ti.fromBufferAttribute(e,t));return this}setFromPoints(e){this.makeEmpty();for(let t=0,n=e.length;t<n;t++)this.expandByPoint(e[t]);return this}setFromCenterAndSize(e,t){const n=ti.copy(t).multiplyScalar(.5);return this.min.copy(e).sub(n),this.max.copy(e).add(n),this}setFromObject(e,t=!1){return this.makeEmpty(),this.expandByObject(e,t)}clone(){return new this.constructor().copy(this)}copy(e){return this.min.copy(e.min),this.max.copy(e.max),this}makeEmpty(){return this.min.x=this.min.y=this.min.z=1/0,this.max.x=this.max.y=this.max.z=-1/0,this}isEmpty(){return this.max.x<this.min.x||this.max.y<this.min.y||this.max.z<this.min.z}getCenter(e){return this.isEmpty()?e.set(0,0,0):e.addVectors(this.min,this.max).multiplyScalar(.5)}getSize(e){return this.isEmpty()?e.set(0,0,0):e.subVectors(this.max,this.min)}expandByPoint(e){return this.min.min(e),this.max.max(e),this}expandByVector(e){return this.min.sub(e),this.max.add(e),this}expandByScalar(e){return this.min.addScalar(-e),this.max.addScalar(e),this}expandByObject(e,t=!1){e.updateWorldMatrix(!1,!1);const n=e.geometry;if(n!==void 0){const r=n.getAttribute("position");if(t===!0&&r!==void 0&&e.isInstancedMesh!==!0)for(let a=0,o=r.count;a<o;a++)e.isMesh===!0?e.getVertexPosition(a,ti):ti.fromBufferAttribute(r,a),ti.applyMatrix4(e.matrixWorld),this.expandByPoint(ti);else e.boundingBox!==void 0?(e.boundingBox===null&&e.computeBoundingBox(),$a.copy(e.boundingBox)):(n.boundingBox===null&&n.computeBoundingBox(),$a.copy(n.boundingBox)),$a.applyMatrix4(e.matrixWorld),this.union($a)}const s=e.children;for(let r=0,a=s.length;r<a;r++)this.expandByObject(s[r],t);return this}containsPoint(e){return e.x>=this.min.x&&e.x<=this.max.x&&e.y>=this.min.y&&e.y<=this.max.y&&e.z>=this.min.z&&e.z<=this.max.z}containsBox(e){return this.min.x<=e.min.x&&e.max.x<=this.max.x&&this.min.y<=e.min.y&&e.max.y<=this.max.y&&this.min.z<=e.min.z&&e.max.z<=this.max.z}getParameter(e,t){return t.set((e.x-this.min.x)/(this.max.x-this.min.x),(e.y-this.min.y)/(this.max.y-this.min.y),(e.z-this.min.z)/(this.max.z-this.min.z))}intersectsBox(e){return e.max.x>=this.min.x&&e.min.x<=this.max.x&&e.max.y>=this.min.y&&e.min.y<=this.max.y&&e.max.z>=this.min.z&&e.min.z<=this.max.z}intersectsSphere(e){return this.clampPoint(e.center,ti),ti.distanceToSquared(e.center)<=e.radius*e.radius}intersectsPlane(e){let t,n;return e.normal.x>0?(t=e.normal.x*this.min.x,n=e.normal.x*this.max.x):(t=e.normal.x*this.max.x,n=e.normal.x*this.min.x),e.normal.y>0?(t+=e.normal.y*this.min.y,n+=e.normal.y*this.max.y):(t+=e.normal.y*this.max.y,n+=e.normal.y*this.min.y),e.normal.z>0?(t+=e.normal.z*this.min.z,n+=e.normal.z*this.max.z):(t+=e.normal.z*this.max.z,n+=e.normal.z*this.min.z),t<=-e.constant&&n>=-e.constant}intersectsTriangle(e){if(this.isEmpty())return!1;this.getCenter(ca),ja.subVectors(this.max,ca),ir.subVectors(e.a,ca),sr.subVectors(e.b,ca),rr.subVectors(e.c,ca),Ki.subVectors(sr,ir),Zi.subVectors(rr,sr),ys.subVectors(ir,rr);let t=[0,-Ki.z,Ki.y,0,-Zi.z,Zi.y,0,-ys.z,ys.y,Ki.z,0,-Ki.x,Zi.z,0,-Zi.x,ys.z,0,-ys.x,-Ki.y,Ki.x,0,-Zi.y,Zi.x,0,-ys.y,ys.x,0];return!Fl(t,ir,sr,rr,ja)||(t=[1,0,0,0,1,0,0,0,1],!Fl(t,ir,sr,rr,ja))?!1:(Ka.crossVectors(Ki,Zi),t=[Ka.x,Ka.y,Ka.z],Fl(t,ir,sr,rr,ja))}clampPoint(e,t){return t.copy(e).clamp(this.min,this.max)}distanceToPoint(e){return this.clampPoint(e,ti).distanceTo(e)}getBoundingSphere(e){return this.isEmpty()?e.makeEmpty():(this.getCenter(e.center),e.radius=this.getSize(ti).length()*.5),e}intersect(e){return this.min.max(e.min),this.max.min(e.max),this.isEmpty()&&this.makeEmpty(),this}union(e){return this.min.min(e.min),this.max.max(e.max),this}applyMatrix4(e){return this.isEmpty()?this:(Ri[0].set(this.min.x,this.min.y,this.min.z).applyMatrix4(e),Ri[1].set(this.min.x,this.min.y,this.max.z).applyMatrix4(e),Ri[2].set(this.min.x,this.max.y,this.min.z).applyMatrix4(e),Ri[3].set(this.min.x,this.max.y,this.max.z).applyMatrix4(e),Ri[4].set(this.max.x,this.min.y,this.min.z).applyMatrix4(e),Ri[5].set(this.max.x,this.min.y,this.max.z).applyMatrix4(e),Ri[6].set(this.max.x,this.max.y,this.min.z).applyMatrix4(e),Ri[7].set(this.max.x,this.max.y,this.max.z).applyMatrix4(e),this.setFromPoints(Ri),this)}translate(e){return this.min.add(e),this.max.add(e),this}equals(e){return e.min.equals(this.min)&&e.max.equals(this.max)}}const Ri=[new k,new k,new k,new k,new k,new k,new k,new k],ti=new k,$a=new Ua,ir=new k,sr=new k,rr=new k,Ki=new k,Zi=new k,ys=new k,ca=new k,ja=new k,Ka=new k,Ms=new k;function Fl(i,e,t,n,s){for(let r=0,a=i.length-3;r<=a;r+=3){Ms.fromArray(i,r);const o=s.x*Math.abs(Ms.x)+s.y*Math.abs(Ms.y)+s.z*Math.abs(Ms.z),l=e.dot(Ms),c=t.dot(Ms),u=n.dot(Ms);if(Math.max(-Math.max(l,c,u),Math.min(l,c,u))>o)return!1}return!0}const Fg=new Ua,ua=new k,Ol=new k;class Na{constructor(e=new k,t=-1){this.isSphere=!0,this.center=e,this.radius=t}set(e,t){return this.center.copy(e),this.radius=t,this}setFromPoints(e,t){const n=this.center;t!==void 0?n.copy(t):Fg.setFromPoints(e).getCenter(n);let s=0;for(let r=0,a=e.length;r<a;r++)s=Math.max(s,n.distanceToSquared(e[r]));return this.radius=Math.sqrt(s),this}copy(e){return this.center.copy(e.center),this.radius=e.radius,this}isEmpty(){return this.radius<0}makeEmpty(){return this.center.set(0,0,0),this.radius=-1,this}containsPoint(e){return e.distanceToSquared(this.center)<=this.radius*this.radius}distanceToPoint(e){return e.distanceTo(this.center)-this.radius}intersectsSphere(e){const t=this.radius+e.radius;return e.center.distanceToSquared(this.center)<=t*t}intersectsBox(e){return e.intersectsSphere(this)}intersectsPlane(e){return Math.abs(e.distanceToPoint(this.center))<=this.radius}clampPoint(e,t){const n=this.center.distanceToSquared(e);return t.copy(e),n>this.radius*this.radius&&(t.sub(this.center).normalize(),t.multiplyScalar(this.radius).add(this.center)),t}getBoundingBox(e){return this.isEmpty()?(e.makeEmpty(),e):(e.set(this.center,this.center),e.expandByScalar(this.radius),e)}applyMatrix4(e){return this.center.applyMatrix4(e),this.radius=this.radius*e.getMaxScaleOnAxis(),this}translate(e){return this.center.add(e),this}expandByPoint(e){if(this.isEmpty())return this.center.copy(e),this.radius=0,this;ua.subVectors(e,this.center);const t=ua.lengthSq();if(t>this.radius*this.radius){const n=Math.sqrt(t),s=(n-this.radius)*.5;this.center.addScaledVector(ua,s/n),this.radius+=s}return this}union(e){return e.isEmpty()?this:this.isEmpty()?(this.copy(e),this):(this.center.equals(e.center)===!0?this.radius=Math.max(this.radius,e.radius):(Ol.subVectors(e.center,this.center).setLength(e.radius),this.expandByPoint(ua.copy(e.center).add(Ol)),this.expandByPoint(ua.copy(e.center).sub(Ol))),this)}equals(e){return e.center.equals(this.center)&&e.radius===this.radius}clone(){return new this.constructor().copy(this)}}const Pi=new k,Bl=new k,Za=new k,Ji=new k,zl=new k,Ja=new k,kl=new k;class Fa{constructor(e=new k,t=new k(0,0,-1)){this.origin=e,this.direction=t}set(e,t){return this.origin.copy(e),this.direction.copy(t),this}copy(e){return this.origin.copy(e.origin),this.direction.copy(e.direction),this}at(e,t){return t.copy(this.origin).addScaledVector(this.direction,e)}lookAt(e){return this.direction.copy(e).sub(this.origin).normalize(),this}recast(e){return this.origin.copy(this.at(e,Pi)),this}closestPointToPoint(e,t){t.subVectors(e,this.origin);const n=t.dot(this.direction);return n<0?t.copy(this.origin):t.copy(this.origin).addScaledVector(this.direction,n)}distanceToPoint(e){return Math.sqrt(this.distanceSqToPoint(e))}distanceSqToPoint(e){const t=Pi.subVectors(e,this.origin).dot(this.direction);return t<0?this.origin.distanceToSquared(e):(Pi.copy(this.origin).addScaledVector(this.direction,t),Pi.distanceToSquared(e))}distanceSqToSegment(e,t,n,s){Bl.copy(e).add(t).multiplyScalar(.5),Za.copy(t).sub(e).normalize(),Ji.copy(this.origin).sub(Bl);const r=e.distanceTo(t)*.5,a=-this.direction.dot(Za),o=Ji.dot(this.direction),l=-Ji.dot(Za),c=Ji.lengthSq(),u=Math.abs(1-a*a);let h,d,f,g;if(u>0)if(h=a*l-o,d=a*o-l,g=r*u,h>=0)if(d>=-g)if(d<=g){const v=1/u;h*=v,d*=v,f=h*(h+a*d+2*o)+d*(a*h+d+2*l)+c}else d=r,h=Math.max(0,-(a*d+o)),f=-h*h+d*(d+2*l)+c;else d=-r,h=Math.max(0,-(a*d+o)),f=-h*h+d*(d+2*l)+c;else d<=-g?(h=Math.max(0,-(-a*r+o)),d=h>0?-r:Math.min(Math.max(-r,-l),r),f=-h*h+d*(d+2*l)+c):d<=g?(h=0,d=Math.min(Math.max(-r,-l),r),f=d*(d+2*l)+c):(h=Math.max(0,-(a*r+o)),d=h>0?r:Math.min(Math.max(-r,-l),r),f=-h*h+d*(d+2*l)+c);else d=a>0?-r:r,h=Math.max(0,-(a*d+o)),f=-h*h+d*(d+2*l)+c;return n&&n.copy(this.origin).addScaledVector(this.direction,h),s&&s.copy(Bl).addScaledVector(Za,d),f}intersectSphere(e,t){Pi.subVectors(e.center,this.origin);const n=Pi.dot(this.direction),s=Pi.dot(Pi)-n*n,r=e.radius*e.radius;if(s>r)return null;const a=Math.sqrt(r-s),o=n-a,l=n+a;return l<0?null:o<0?this.at(l,t):this.at(o,t)}intersectsSphere(e){return this.distanceSqToPoint(e.center)<=e.radius*e.radius}distanceToPlane(e){const t=e.normal.dot(this.direction);if(t===0)return e.distanceToPoint(this.origin)===0?0:null;const n=-(this.origin.dot(e.normal)+e.constant)/t;return n>=0?n:null}intersectPlane(e,t){const n=this.distanceToPlane(e);return n===null?null:this.at(n,t)}intersectsPlane(e){const t=e.distanceToPoint(this.origin);return t===0||e.normal.dot(this.direction)*t<0}intersectBox(e,t){let n,s,r,a,o,l;const c=1/this.direction.x,u=1/this.direction.y,h=1/this.direction.z,d=this.origin;return c>=0?(n=(e.min.x-d.x)*c,s=(e.max.x-d.x)*c):(n=(e.max.x-d.x)*c,s=(e.min.x-d.x)*c),u>=0?(r=(e.min.y-d.y)*u,a=(e.max.y-d.y)*u):(r=(e.max.y-d.y)*u,a=(e.min.y-d.y)*u),n>a||r>s||((r>n||isNaN(n))&&(n=r),(a<s||isNaN(s))&&(s=a),h>=0?(o=(e.min.z-d.z)*h,l=(e.max.z-d.z)*h):(o=(e.max.z-d.z)*h,l=(e.min.z-d.z)*h),n>l||o>s)||((o>n||n!==n)&&(n=o),(l<s||s!==s)&&(s=l),s<0)?null:this.at(n>=0?n:s,t)}intersectsBox(e){return this.intersectBox(e,Pi)!==null}intersectTriangle(e,t,n,s,r){zl.subVectors(t,e),Ja.subVectors(n,e),kl.crossVectors(zl,Ja);let a=this.direction.dot(kl),o;if(a>0){if(s)return null;o=1}else if(a<0)o=-1,a=-a;else return null;Ji.subVectors(this.origin,e);const l=o*this.direction.dot(Ja.crossVectors(Ji,Ja));if(l<0)return null;const c=o*this.direction.dot(zl.cross(Ji));if(c<0||l+c>a)return null;const u=-o*Ji.dot(kl);return u<0?null:this.at(u/a,r)}applyMatrix4(e){return this.origin.applyMatrix4(e),this.direction.transformDirection(e),this}equals(e){return e.origin.equals(this.origin)&&e.direction.equals(this.direction)}clone(){return new this.constructor().copy(this)}}class Ot{constructor(e,t,n,s,r,a,o,l,c,u,h,d,f,g,v,m){Ot.prototype.isMatrix4=!0,this.elements=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],e!==void 0&&this.set(e,t,n,s,r,a,o,l,c,u,h,d,f,g,v,m)}set(e,t,n,s,r,a,o,l,c,u,h,d,f,g,v,m){const p=this.elements;return p[0]=e,p[4]=t,p[8]=n,p[12]=s,p[1]=r,p[5]=a,p[9]=o,p[13]=l,p[2]=c,p[6]=u,p[10]=h,p[14]=d,p[3]=f,p[7]=g,p[11]=v,p[15]=m,this}identity(){return this.set(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1),this}clone(){return new Ot().fromArray(this.elements)}copy(e){const t=this.elements,n=e.elements;return t[0]=n[0],t[1]=n[1],t[2]=n[2],t[3]=n[3],t[4]=n[4],t[5]=n[5],t[6]=n[6],t[7]=n[7],t[8]=n[8],t[9]=n[9],t[10]=n[10],t[11]=n[11],t[12]=n[12],t[13]=n[13],t[14]=n[14],t[15]=n[15],this}copyPosition(e){const t=this.elements,n=e.elements;return t[12]=n[12],t[13]=n[13],t[14]=n[14],this}setFromMatrix3(e){const t=e.elements;return this.set(t[0],t[3],t[6],0,t[1],t[4],t[7],0,t[2],t[5],t[8],0,0,0,0,1),this}extractBasis(e,t,n){return e.setFromMatrixColumn(this,0),t.setFromMatrixColumn(this,1),n.setFromMatrixColumn(this,2),this}makeBasis(e,t,n){return this.set(e.x,t.x,n.x,0,e.y,t.y,n.y,0,e.z,t.z,n.z,0,0,0,0,1),this}extractRotation(e){const t=this.elements,n=e.elements,s=1/ar.setFromMatrixColumn(e,0).length(),r=1/ar.setFromMatrixColumn(e,1).length(),a=1/ar.setFromMatrixColumn(e,2).length();return t[0]=n[0]*s,t[1]=n[1]*s,t[2]=n[2]*s,t[3]=0,t[4]=n[4]*r,t[5]=n[5]*r,t[6]=n[6]*r,t[7]=0,t[8]=n[8]*a,t[9]=n[9]*a,t[10]=n[10]*a,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromEuler(e){const t=this.elements,n=e.x,s=e.y,r=e.z,a=Math.cos(n),o=Math.sin(n),l=Math.cos(s),c=Math.sin(s),u=Math.cos(r),h=Math.sin(r);if(e.order==="XYZ"){const d=a*u,f=a*h,g=o*u,v=o*h;t[0]=l*u,t[4]=-l*h,t[8]=c,t[1]=f+g*c,t[5]=d-v*c,t[9]=-o*l,t[2]=v-d*c,t[6]=g+f*c,t[10]=a*l}else if(e.order==="YXZ"){const d=l*u,f=l*h,g=c*u,v=c*h;t[0]=d+v*o,t[4]=g*o-f,t[8]=a*c,t[1]=a*h,t[5]=a*u,t[9]=-o,t[2]=f*o-g,t[6]=v+d*o,t[10]=a*l}else if(e.order==="ZXY"){const d=l*u,f=l*h,g=c*u,v=c*h;t[0]=d-v*o,t[4]=-a*h,t[8]=g+f*o,t[1]=f+g*o,t[5]=a*u,t[9]=v-d*o,t[2]=-a*c,t[6]=o,t[10]=a*l}else if(e.order==="ZYX"){const d=a*u,f=a*h,g=o*u,v=o*h;t[0]=l*u,t[4]=g*c-f,t[8]=d*c+v,t[1]=l*h,t[5]=v*c+d,t[9]=f*c-g,t[2]=-c,t[6]=o*l,t[10]=a*l}else if(e.order==="YZX"){const d=a*l,f=a*c,g=o*l,v=o*c;t[0]=l*u,t[4]=v-d*h,t[8]=g*h+f,t[1]=h,t[5]=a*u,t[9]=-o*u,t[2]=-c*u,t[6]=f*h+g,t[10]=d-v*h}else if(e.order==="XZY"){const d=a*l,f=a*c,g=o*l,v=o*c;t[0]=l*u,t[4]=-h,t[8]=c*u,t[1]=d*h+v,t[5]=a*u,t[9]=f*h-g,t[2]=g*h-f,t[6]=o*u,t[10]=v*h+d}return t[3]=0,t[7]=0,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromQuaternion(e){return this.compose(Og,e,Bg)}lookAt(e,t,n){const s=this.elements;return On.subVectors(e,t),On.lengthSq()===0&&(On.z=1),On.normalize(),Qi.crossVectors(n,On),Qi.lengthSq()===0&&(Math.abs(n.z)===1?On.x+=1e-4:On.z+=1e-4,On.normalize(),Qi.crossVectors(n,On)),Qi.normalize(),Qa.crossVectors(On,Qi),s[0]=Qi.x,s[4]=Qa.x,s[8]=On.x,s[1]=Qi.y,s[5]=Qa.y,s[9]=On.y,s[2]=Qi.z,s[6]=Qa.z,s[10]=On.z,this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){const n=e.elements,s=t.elements,r=this.elements,a=n[0],o=n[4],l=n[8],c=n[12],u=n[1],h=n[5],d=n[9],f=n[13],g=n[2],v=n[6],m=n[10],p=n[14],S=n[3],y=n[7],w=n[11],O=n[15],A=s[0],P=s[4],N=s[8],b=s[12],x=s[1],R=s[5],j=s[9],z=s[13],K=s[2],X=s[6],Q=s[10],Y=s[14],ne=s[3],ge=s[7],de=s[11],xe=s[15];return r[0]=a*A+o*x+l*K+c*ne,r[4]=a*P+o*R+l*X+c*ge,r[8]=a*N+o*j+l*Q+c*de,r[12]=a*b+o*z+l*Y+c*xe,r[1]=u*A+h*x+d*K+f*ne,r[5]=u*P+h*R+d*X+f*ge,r[9]=u*N+h*j+d*Q+f*de,r[13]=u*b+h*z+d*Y+f*xe,r[2]=g*A+v*x+m*K+p*ne,r[6]=g*P+v*R+m*X+p*ge,r[10]=g*N+v*j+m*Q+p*de,r[14]=g*b+v*z+m*Y+p*xe,r[3]=S*A+y*x+w*K+O*ne,r[7]=S*P+y*R+w*X+O*ge,r[11]=S*N+y*j+w*Q+O*de,r[15]=S*b+y*z+w*Y+O*xe,this}multiplyScalar(e){const t=this.elements;return t[0]*=e,t[4]*=e,t[8]*=e,t[12]*=e,t[1]*=e,t[5]*=e,t[9]*=e,t[13]*=e,t[2]*=e,t[6]*=e,t[10]*=e,t[14]*=e,t[3]*=e,t[7]*=e,t[11]*=e,t[15]*=e,this}determinant(){const e=this.elements,t=e[0],n=e[4],s=e[8],r=e[12],a=e[1],o=e[5],l=e[9],c=e[13],u=e[2],h=e[6],d=e[10],f=e[14],g=e[3],v=e[7],m=e[11],p=e[15];return g*(+r*l*h-s*c*h-r*o*d+n*c*d+s*o*f-n*l*f)+v*(+t*l*f-t*c*d+r*a*d-s*a*f+s*c*u-r*l*u)+m*(+t*c*h-t*o*f-r*a*h+n*a*f+r*o*u-n*c*u)+p*(-s*o*u-t*l*h+t*o*d+s*a*h-n*a*d+n*l*u)}transpose(){const e=this.elements;let t;return t=e[1],e[1]=e[4],e[4]=t,t=e[2],e[2]=e[8],e[8]=t,t=e[6],e[6]=e[9],e[9]=t,t=e[3],e[3]=e[12],e[12]=t,t=e[7],e[7]=e[13],e[13]=t,t=e[11],e[11]=e[14],e[14]=t,this}setPosition(e,t,n){const s=this.elements;return e.isVector3?(s[12]=e.x,s[13]=e.y,s[14]=e.z):(s[12]=e,s[13]=t,s[14]=n),this}invert(){const e=this.elements,t=e[0],n=e[1],s=e[2],r=e[3],a=e[4],o=e[5],l=e[6],c=e[7],u=e[8],h=e[9],d=e[10],f=e[11],g=e[12],v=e[13],m=e[14],p=e[15],S=h*m*c-v*d*c+v*l*f-o*m*f-h*l*p+o*d*p,y=g*d*c-u*m*c-g*l*f+a*m*f+u*l*p-a*d*p,w=u*v*c-g*h*c+g*o*f-a*v*f-u*o*p+a*h*p,O=g*h*l-u*v*l-g*o*d+a*v*d+u*o*m-a*h*m,A=t*S+n*y+s*w+r*O;if(A===0)return this.set(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);const P=1/A;return e[0]=S*P,e[1]=(v*d*r-h*m*r-v*s*f+n*m*f+h*s*p-n*d*p)*P,e[2]=(o*m*r-v*l*r+v*s*c-n*m*c-o*s*p+n*l*p)*P,e[3]=(h*l*r-o*d*r-h*s*c+n*d*c+o*s*f-n*l*f)*P,e[4]=y*P,e[5]=(u*m*r-g*d*r+g*s*f-t*m*f-u*s*p+t*d*p)*P,e[6]=(g*l*r-a*m*r-g*s*c+t*m*c+a*s*p-t*l*p)*P,e[7]=(a*d*r-u*l*r+u*s*c-t*d*c-a*s*f+t*l*f)*P,e[8]=w*P,e[9]=(g*h*r-u*v*r-g*n*f+t*v*f+u*n*p-t*h*p)*P,e[10]=(a*v*r-g*o*r+g*n*c-t*v*c-a*n*p+t*o*p)*P,e[11]=(u*o*r-a*h*r-u*n*c+t*h*c+a*n*f-t*o*f)*P,e[12]=O*P,e[13]=(u*v*s-g*h*s+g*n*d-t*v*d-u*n*m+t*h*m)*P,e[14]=(g*o*s-a*v*s-g*n*l+t*v*l+a*n*m-t*o*m)*P,e[15]=(a*h*s-u*o*s+u*n*l-t*h*l-a*n*d+t*o*d)*P,this}scale(e){const t=this.elements,n=e.x,s=e.y,r=e.z;return t[0]*=n,t[4]*=s,t[8]*=r,t[1]*=n,t[5]*=s,t[9]*=r,t[2]*=n,t[6]*=s,t[10]*=r,t[3]*=n,t[7]*=s,t[11]*=r,this}getMaxScaleOnAxis(){const e=this.elements,t=e[0]*e[0]+e[1]*e[1]+e[2]*e[2],n=e[4]*e[4]+e[5]*e[5]+e[6]*e[6],s=e[8]*e[8]+e[9]*e[9]+e[10]*e[10];return Math.sqrt(Math.max(t,n,s))}makeTranslation(e,t,n){return e.isVector3?this.set(1,0,0,e.x,0,1,0,e.y,0,0,1,e.z,0,0,0,1):this.set(1,0,0,e,0,1,0,t,0,0,1,n,0,0,0,1),this}makeRotationX(e){const t=Math.cos(e),n=Math.sin(e);return this.set(1,0,0,0,0,t,-n,0,0,n,t,0,0,0,0,1),this}makeRotationY(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,0,n,0,0,1,0,0,-n,0,t,0,0,0,0,1),this}makeRotationZ(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,-n,0,0,n,t,0,0,0,0,1,0,0,0,0,1),this}makeRotationAxis(e,t){const n=Math.cos(t),s=Math.sin(t),r=1-n,a=e.x,o=e.y,l=e.z,c=r*a,u=r*o;return this.set(c*a+n,c*o-s*l,c*l+s*o,0,c*o+s*l,u*o+n,u*l-s*a,0,c*l-s*o,u*l+s*a,r*l*l+n,0,0,0,0,1),this}makeScale(e,t,n){return this.set(e,0,0,0,0,t,0,0,0,0,n,0,0,0,0,1),this}makeShear(e,t,n,s,r,a){return this.set(1,n,r,0,e,1,a,0,t,s,1,0,0,0,0,1),this}compose(e,t,n){const s=this.elements,r=t._x,a=t._y,o=t._z,l=t._w,c=r+r,u=a+a,h=o+o,d=r*c,f=r*u,g=r*h,v=a*u,m=a*h,p=o*h,S=l*c,y=l*u,w=l*h,O=n.x,A=n.y,P=n.z;return s[0]=(1-(v+p))*O,s[1]=(f+w)*O,s[2]=(g-y)*O,s[3]=0,s[4]=(f-w)*A,s[5]=(1-(d+p))*A,s[6]=(m+S)*A,s[7]=0,s[8]=(g+y)*P,s[9]=(m-S)*P,s[10]=(1-(d+v))*P,s[11]=0,s[12]=e.x,s[13]=e.y,s[14]=e.z,s[15]=1,this}decompose(e,t,n){const s=this.elements;let r=ar.set(s[0],s[1],s[2]).length();const a=ar.set(s[4],s[5],s[6]).length(),o=ar.set(s[8],s[9],s[10]).length();this.determinant()<0&&(r=-r),e.x=s[12],e.y=s[13],e.z=s[14],ni.copy(this);const c=1/r,u=1/a,h=1/o;return ni.elements[0]*=c,ni.elements[1]*=c,ni.elements[2]*=c,ni.elements[4]*=u,ni.elements[5]*=u,ni.elements[6]*=u,ni.elements[8]*=h,ni.elements[9]*=h,ni.elements[10]*=h,t.setFromRotationMatrix(ni),n.x=r,n.y=a,n.z=o,this}makePerspective(e,t,n,s,r,a,o=Oi){const l=this.elements,c=2*r/(t-e),u=2*r/(n-s),h=(t+e)/(t-e),d=(n+s)/(n-s);let f,g;if(o===Oi)f=-(a+r)/(a-r),g=-2*a*r/(a-r);else if(o===Go)f=-a/(a-r),g=-a*r/(a-r);else throw new Error("THREE.Matrix4.makePerspective(): Invalid coordinate system: "+o);return l[0]=c,l[4]=0,l[8]=h,l[12]=0,l[1]=0,l[5]=u,l[9]=d,l[13]=0,l[2]=0,l[6]=0,l[10]=f,l[14]=g,l[3]=0,l[7]=0,l[11]=-1,l[15]=0,this}makeOrthographic(e,t,n,s,r,a,o=Oi){const l=this.elements,c=1/(t-e),u=1/(n-s),h=1/(a-r),d=(t+e)*c,f=(n+s)*u;let g,v;if(o===Oi)g=(a+r)*h,v=-2*h;else if(o===Go)g=r*h,v=-1*h;else throw new Error("THREE.Matrix4.makeOrthographic(): Invalid coordinate system: "+o);return l[0]=2*c,l[4]=0,l[8]=0,l[12]=-d,l[1]=0,l[5]=2*u,l[9]=0,l[13]=-f,l[2]=0,l[6]=0,l[10]=v,l[14]=-g,l[3]=0,l[7]=0,l[11]=0,l[15]=1,this}equals(e){const t=this.elements,n=e.elements;for(let s=0;s<16;s++)if(t[s]!==n[s])return!1;return!0}fromArray(e,t=0){for(let n=0;n<16;n++)this.elements[n]=e[n+t];return this}toArray(e=[],t=0){const n=this.elements;return e[t]=n[0],e[t+1]=n[1],e[t+2]=n[2],e[t+3]=n[3],e[t+4]=n[4],e[t+5]=n[5],e[t+6]=n[6],e[t+7]=n[7],e[t+8]=n[8],e[t+9]=n[9],e[t+10]=n[10],e[t+11]=n[11],e[t+12]=n[12],e[t+13]=n[13],e[t+14]=n[14],e[t+15]=n[15],e}}const ar=new k,ni=new Ot,Og=new k(0,0,0),Bg=new k(1,1,1),Qi=new k,Qa=new k,On=new k,Ah=new Ot,Ch=new zs;class Si{constructor(e=0,t=0,n=0,s=Si.DEFAULT_ORDER){this.isEuler=!0,this._x=e,this._y=t,this._z=n,this._order=s}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get order(){return this._order}set order(e){this._order=e,this._onChangeCallback()}set(e,t,n,s=this._order){return this._x=e,this._y=t,this._z=n,this._order=s,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._order)}copy(e){return this._x=e._x,this._y=e._y,this._z=e._z,this._order=e._order,this._onChangeCallback(),this}setFromRotationMatrix(e,t=this._order,n=!0){const s=e.elements,r=s[0],a=s[4],o=s[8],l=s[1],c=s[5],u=s[9],h=s[2],d=s[6],f=s[10];switch(t){case"XYZ":this._y=Math.asin(Mn(o,-1,1)),Math.abs(o)<.9999999?(this._x=Math.atan2(-u,f),this._z=Math.atan2(-a,r)):(this._x=Math.atan2(d,c),this._z=0);break;case"YXZ":this._x=Math.asin(-Mn(u,-1,1)),Math.abs(u)<.9999999?(this._y=Math.atan2(o,f),this._z=Math.atan2(l,c)):(this._y=Math.atan2(-h,r),this._z=0);break;case"ZXY":this._x=Math.asin(Mn(d,-1,1)),Math.abs(d)<.9999999?(this._y=Math.atan2(-h,f),this._z=Math.atan2(-a,c)):(this._y=0,this._z=Math.atan2(l,r));break;case"ZYX":this._y=Math.asin(-Mn(h,-1,1)),Math.abs(h)<.9999999?(this._x=Math.atan2(d,f),this._z=Math.atan2(l,r)):(this._x=0,this._z=Math.atan2(-a,c));break;case"YZX":this._z=Math.asin(Mn(l,-1,1)),Math.abs(l)<.9999999?(this._x=Math.atan2(-u,c),this._y=Math.atan2(-h,r)):(this._x=0,this._y=Math.atan2(o,f));break;case"XZY":this._z=Math.asin(-Mn(a,-1,1)),Math.abs(a)<.9999999?(this._x=Math.atan2(d,c),this._y=Math.atan2(o,r)):(this._x=Math.atan2(-u,f),this._y=0);break;default:console.warn("THREE.Euler: .setFromRotationMatrix() encountered an unknown order: "+t)}return this._order=t,n===!0&&this._onChangeCallback(),this}setFromQuaternion(e,t,n){return Ah.makeRotationFromQuaternion(e),this.setFromRotationMatrix(Ah,t,n)}setFromVector3(e,t=this._order){return this.set(e.x,e.y,e.z,t)}reorder(e){return Ch.setFromEuler(this),this.setFromQuaternion(Ch,e)}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._order===this._order}fromArray(e){return this._x=e[0],this._y=e[1],this._z=e[2],e[3]!==void 0&&(this._order=e[3]),this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._order,e}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._order}}Si.DEFAULT_ORDER="XYZ";class yu{constructor(){this.mask=1}set(e){this.mask=(1<<e|0)>>>0}enable(e){this.mask|=1<<e|0}enableAll(){this.mask=-1}toggle(e){this.mask^=1<<e|0}disable(e){this.mask&=~(1<<e|0)}disableAll(){this.mask=0}test(e){return(this.mask&e.mask)!==0}isEnabled(e){return(this.mask&(1<<e|0))!==0}}let zg=0;const Rh=new k,or=new zs,Li=new Ot,eo=new k,ha=new k,kg=new k,Hg=new zs,Ph=new k(1,0,0),Lh=new k(0,1,0),Dh=new k(0,0,1),Ih={type:"added"},Vg={type:"removed"},lr={type:"childadded",child:null},Hl={type:"childremoved",child:null};class Jt extends jr{constructor(){super(),this.isObject3D=!0,Object.defineProperty(this,"id",{value:zg++}),this.uuid=zi(),this.name="",this.type="Object3D",this.parent=null,this.children=[],this.up=Jt.DEFAULT_UP.clone();const e=new k,t=new Si,n=new zs,s=new k(1,1,1);function r(){n.setFromEuler(t,!1)}function a(){t.setFromQuaternion(n,void 0,!1)}t._onChange(r),n._onChange(a),Object.defineProperties(this,{position:{configurable:!0,enumerable:!0,value:e},rotation:{configurable:!0,enumerable:!0,value:t},quaternion:{configurable:!0,enumerable:!0,value:n},scale:{configurable:!0,enumerable:!0,value:s},modelViewMatrix:{value:new Ot},normalMatrix:{value:new rt}}),this.matrix=new Ot,this.matrixWorld=new Ot,this.matrixAutoUpdate=Jt.DEFAULT_MATRIX_AUTO_UPDATE,this.matrixWorldAutoUpdate=Jt.DEFAULT_MATRIX_WORLD_AUTO_UPDATE,this.matrixWorldNeedsUpdate=!1,this.layers=new yu,this.visible=!0,this.castShadow=!1,this.receiveShadow=!1,this.frustumCulled=!0,this.renderOrder=0,this.animations=[],this.userData={}}onBeforeShadow(){}onAfterShadow(){}onBeforeRender(){}onAfterRender(){}applyMatrix4(e){this.matrixAutoUpdate&&this.updateMatrix(),this.matrix.premultiply(e),this.matrix.decompose(this.position,this.quaternion,this.scale)}applyQuaternion(e){return this.quaternion.premultiply(e),this}setRotationFromAxisAngle(e,t){this.quaternion.setFromAxisAngle(e,t)}setRotationFromEuler(e){this.quaternion.setFromEuler(e,!0)}setRotationFromMatrix(e){this.quaternion.setFromRotationMatrix(e)}setRotationFromQuaternion(e){this.quaternion.copy(e)}rotateOnAxis(e,t){return or.setFromAxisAngle(e,t),this.quaternion.multiply(or),this}rotateOnWorldAxis(e,t){return or.setFromAxisAngle(e,t),this.quaternion.premultiply(or),this}rotateX(e){return this.rotateOnAxis(Ph,e)}rotateY(e){return this.rotateOnAxis(Lh,e)}rotateZ(e){return this.rotateOnAxis(Dh,e)}translateOnAxis(e,t){return Rh.copy(e).applyQuaternion(this.quaternion),this.position.add(Rh.multiplyScalar(t)),this}translateX(e){return this.translateOnAxis(Ph,e)}translateY(e){return this.translateOnAxis(Lh,e)}translateZ(e){return this.translateOnAxis(Dh,e)}localToWorld(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(this.matrixWorld)}worldToLocal(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(Li.copy(this.matrixWorld).invert())}lookAt(e,t,n){e.isVector3?eo.copy(e):eo.set(e,t,n);const s=this.parent;this.updateWorldMatrix(!0,!1),ha.setFromMatrixPosition(this.matrixWorld),this.isCamera||this.isLight?Li.lookAt(ha,eo,this.up):Li.lookAt(eo,ha,this.up),this.quaternion.setFromRotationMatrix(Li),s&&(Li.extractRotation(s.matrixWorld),or.setFromRotationMatrix(Li),this.quaternion.premultiply(or.invert()))}add(e){if(arguments.length>1){for(let t=0;t<arguments.length;t++)this.add(arguments[t]);return this}return e===this?(console.error("THREE.Object3D.add: object can't be added as a child of itself.",e),this):(e&&e.isObject3D?(e.removeFromParent(),e.parent=this,this.children.push(e),e.dispatchEvent(Ih),lr.child=e,this.dispatchEvent(lr),lr.child=null):console.error("THREE.Object3D.add: object not an instance of THREE.Object3D.",e),this)}remove(e){if(arguments.length>1){for(let n=0;n<arguments.length;n++)this.remove(arguments[n]);return this}const t=this.children.indexOf(e);return t!==-1&&(e.parent=null,this.children.splice(t,1),e.dispatchEvent(Vg),Hl.child=e,this.dispatchEvent(Hl),Hl.child=null),this}removeFromParent(){const e=this.parent;return e!==null&&e.remove(this),this}clear(){return this.remove(...this.children)}attach(e){return this.updateWorldMatrix(!0,!1),Li.copy(this.matrixWorld).invert(),e.parent!==null&&(e.parent.updateWorldMatrix(!0,!1),Li.multiply(e.parent.matrixWorld)),e.applyMatrix4(Li),e.removeFromParent(),e.parent=this,this.children.push(e),e.updateWorldMatrix(!1,!0),e.dispatchEvent(Ih),lr.child=e,this.dispatchEvent(lr),lr.child=null,this}getObjectById(e){return this.getObjectByProperty("id",e)}getObjectByName(e){return this.getObjectByProperty("name",e)}getObjectByProperty(e,t){if(this[e]===t)return this;for(let n=0,s=this.children.length;n<s;n++){const a=this.children[n].getObjectByProperty(e,t);if(a!==void 0)return a}}getObjectsByProperty(e,t,n=[]){this[e]===t&&n.push(this);const s=this.children;for(let r=0,a=s.length;r<a;r++)s[r].getObjectsByProperty(e,t,n);return n}getWorldPosition(e){return this.updateWorldMatrix(!0,!1),e.setFromMatrixPosition(this.matrixWorld)}getWorldQuaternion(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(ha,e,kg),e}getWorldScale(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(ha,Hg,e),e}getWorldDirection(e){this.updateWorldMatrix(!0,!1);const t=this.matrixWorld.elements;return e.set(t[8],t[9],t[10]).normalize()}raycast(){}traverse(e){e(this);const t=this.children;for(let n=0,s=t.length;n<s;n++)t[n].traverse(e)}traverseVisible(e){if(this.visible===!1)return;e(this);const t=this.children;for(let n=0,s=t.length;n<s;n++)t[n].traverseVisible(e)}traverseAncestors(e){const t=this.parent;t!==null&&(e(t),t.traverseAncestors(e))}updateMatrix(){this.matrix.compose(this.position,this.quaternion,this.scale),this.matrixWorldNeedsUpdate=!0}updateMatrixWorld(e){this.matrixAutoUpdate&&this.updateMatrix(),(this.matrixWorldNeedsUpdate||e)&&(this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),this.matrixWorldNeedsUpdate=!1,e=!0);const t=this.children;for(let n=0,s=t.length;n<s;n++)t[n].updateMatrixWorld(e)}updateWorldMatrix(e,t){const n=this.parent;if(e===!0&&n!==null&&n.updateWorldMatrix(!0,!1),this.matrixAutoUpdate&&this.updateMatrix(),this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),t===!0){const s=this.children;for(let r=0,a=s.length;r<a;r++)s[r].updateWorldMatrix(!1,!0)}}toJSON(e){const t=e===void 0||typeof e=="string",n={};t&&(e={geometries:{},materials:{},textures:{},images:{},shapes:{},skeletons:{},animations:{},nodes:{}},n.metadata={version:4.6,type:"Object",generator:"Object3D.toJSON"});const s={};s.uuid=this.uuid,s.type=this.type,this.name!==""&&(s.name=this.name),this.castShadow===!0&&(s.castShadow=!0),this.receiveShadow===!0&&(s.receiveShadow=!0),this.visible===!1&&(s.visible=!1),this.frustumCulled===!1&&(s.frustumCulled=!1),this.renderOrder!==0&&(s.renderOrder=this.renderOrder),Object.keys(this.userData).length>0&&(s.userData=this.userData),s.layers=this.layers.mask,s.matrix=this.matrix.toArray(),s.up=this.up.toArray(),this.matrixAutoUpdate===!1&&(s.matrixAutoUpdate=!1),this.isInstancedMesh&&(s.type="InstancedMesh",s.count=this.count,s.instanceMatrix=this.instanceMatrix.toJSON(),this.instanceColor!==null&&(s.instanceColor=this.instanceColor.toJSON())),this.isBatchedMesh&&(s.type="BatchedMesh",s.perObjectFrustumCulled=this.perObjectFrustumCulled,s.sortObjects=this.sortObjects,s.drawRanges=this._drawRanges,s.reservedRanges=this._reservedRanges,s.visibility=this._visibility,s.active=this._active,s.bounds=this._bounds.map(o=>({boxInitialized:o.boxInitialized,boxMin:o.box.min.toArray(),boxMax:o.box.max.toArray(),sphereInitialized:o.sphereInitialized,sphereRadius:o.sphere.radius,sphereCenter:o.sphere.center.toArray()})),s.maxInstanceCount=this._maxInstanceCount,s.maxVertexCount=this._maxVertexCount,s.maxIndexCount=this._maxIndexCount,s.geometryInitialized=this._geometryInitialized,s.geometryCount=this._geometryCount,s.matricesTexture=this._matricesTexture.toJSON(e),this._colorsTexture!==null&&(s.colorsTexture=this._colorsTexture.toJSON(e)),this.boundingSphere!==null&&(s.boundingSphere={center:s.boundingSphere.center.toArray(),radius:s.boundingSphere.radius}),this.boundingBox!==null&&(s.boundingBox={min:s.boundingBox.min.toArray(),max:s.boundingBox.max.toArray()}));function r(o,l){return o[l.uuid]===void 0&&(o[l.uuid]=l.toJSON(e)),l.uuid}if(this.isScene)this.background&&(this.background.isColor?s.background=this.background.toJSON():this.background.isTexture&&(s.background=this.background.toJSON(e).uuid)),this.environment&&this.environment.isTexture&&this.environment.isRenderTargetTexture!==!0&&(s.environment=this.environment.toJSON(e).uuid);else if(this.isMesh||this.isLine||this.isPoints){s.geometry=r(e.geometries,this.geometry);const o=this.geometry.parameters;if(o!==void 0&&o.shapes!==void 0){const l=o.shapes;if(Array.isArray(l))for(let c=0,u=l.length;c<u;c++){const h=l[c];r(e.shapes,h)}else r(e.shapes,l)}}if(this.isSkinnedMesh&&(s.bindMode=this.bindMode,s.bindMatrix=this.bindMatrix.toArray(),this.skeleton!==void 0&&(r(e.skeletons,this.skeleton),s.skeleton=this.skeleton.uuid)),this.material!==void 0)if(Array.isArray(this.material)){const o=[];for(let l=0,c=this.material.length;l<c;l++)o.push(r(e.materials,this.material[l]));s.material=o}else s.material=r(e.materials,this.material);if(this.children.length>0){s.children=[];for(let o=0;o<this.children.length;o++)s.children.push(this.children[o].toJSON(e).object)}if(this.animations.length>0){s.animations=[];for(let o=0;o<this.animations.length;o++){const l=this.animations[o];s.animations.push(r(e.animations,l))}}if(t){const o=a(e.geometries),l=a(e.materials),c=a(e.textures),u=a(e.images),h=a(e.shapes),d=a(e.skeletons),f=a(e.animations),g=a(e.nodes);o.length>0&&(n.geometries=o),l.length>0&&(n.materials=l),c.length>0&&(n.textures=c),u.length>0&&(n.images=u),h.length>0&&(n.shapes=h),d.length>0&&(n.skeletons=d),f.length>0&&(n.animations=f),g.length>0&&(n.nodes=g)}return n.object=s,n;function a(o){const l=[];for(const c in o){const u=o[c];delete u.metadata,l.push(u)}return l}}clone(e){return new this.constructor().copy(this,e)}copy(e,t=!0){if(this.name=e.name,this.up.copy(e.up),this.position.copy(e.position),this.rotation.order=e.rotation.order,this.quaternion.copy(e.quaternion),this.scale.copy(e.scale),this.matrix.copy(e.matrix),this.matrixWorld.copy(e.matrixWorld),this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrixWorldAutoUpdate=e.matrixWorldAutoUpdate,this.matrixWorldNeedsUpdate=e.matrixWorldNeedsUpdate,this.layers.mask=e.layers.mask,this.visible=e.visible,this.castShadow=e.castShadow,this.receiveShadow=e.receiveShadow,this.frustumCulled=e.frustumCulled,this.renderOrder=e.renderOrder,this.animations=e.animations.slice(),this.userData=JSON.parse(JSON.stringify(e.userData)),t===!0)for(let n=0;n<e.children.length;n++){const s=e.children[n];this.add(s.clone())}return this}}Jt.DEFAULT_UP=new k(0,1,0);Jt.DEFAULT_MATRIX_AUTO_UPDATE=!0;Jt.DEFAULT_MATRIX_WORLD_AUTO_UPDATE=!0;const ii=new k,Di=new k,Vl=new k,Ii=new k,cr=new k,ur=new k,Uh=new k,Gl=new k,Wl=new k,Xl=new k;class jn{constructor(e=new k,t=new k,n=new k){this.a=e,this.b=t,this.c=n}static getNormal(e,t,n,s){s.subVectors(n,t),ii.subVectors(e,t),s.cross(ii);const r=s.lengthSq();return r>0?s.multiplyScalar(1/Math.sqrt(r)):s.set(0,0,0)}static getBarycoord(e,t,n,s,r){ii.subVectors(s,t),Di.subVectors(n,t),Vl.subVectors(e,t);const a=ii.dot(ii),o=ii.dot(Di),l=ii.dot(Vl),c=Di.dot(Di),u=Di.dot(Vl),h=a*c-o*o;if(h===0)return r.set(0,0,0),null;const d=1/h,f=(c*l-o*u)*d,g=(a*u-o*l)*d;return r.set(1-f-g,g,f)}static containsPoint(e,t,n,s){return this.getBarycoord(e,t,n,s,Ii)===null?!1:Ii.x>=0&&Ii.y>=0&&Ii.x+Ii.y<=1}static getInterpolation(e,t,n,s,r,a,o,l){return this.getBarycoord(e,t,n,s,Ii)===null?(l.x=0,l.y=0,"z"in l&&(l.z=0),"w"in l&&(l.w=0),null):(l.setScalar(0),l.addScaledVector(r,Ii.x),l.addScaledVector(a,Ii.y),l.addScaledVector(o,Ii.z),l)}static isFrontFacing(e,t,n,s){return ii.subVectors(n,t),Di.subVectors(e,t),ii.cross(Di).dot(s)<0}set(e,t,n){return this.a.copy(e),this.b.copy(t),this.c.copy(n),this}setFromPointsAndIndices(e,t,n,s){return this.a.copy(e[t]),this.b.copy(e[n]),this.c.copy(e[s]),this}setFromAttributeAndIndices(e,t,n,s){return this.a.fromBufferAttribute(e,t),this.b.fromBufferAttribute(e,n),this.c.fromBufferAttribute(e,s),this}clone(){return new this.constructor().copy(this)}copy(e){return this.a.copy(e.a),this.b.copy(e.b),this.c.copy(e.c),this}getArea(){return ii.subVectors(this.c,this.b),Di.subVectors(this.a,this.b),ii.cross(Di).length()*.5}getMidpoint(e){return e.addVectors(this.a,this.b).add(this.c).multiplyScalar(1/3)}getNormal(e){return jn.getNormal(this.a,this.b,this.c,e)}getPlane(e){return e.setFromCoplanarPoints(this.a,this.b,this.c)}getBarycoord(e,t){return jn.getBarycoord(e,this.a,this.b,this.c,t)}getInterpolation(e,t,n,s,r){return jn.getInterpolation(e,this.a,this.b,this.c,t,n,s,r)}containsPoint(e){return jn.containsPoint(e,this.a,this.b,this.c)}isFrontFacing(e){return jn.isFrontFacing(this.a,this.b,this.c,e)}intersectsBox(e){return e.intersectsTriangle(this)}closestPointToPoint(e,t){const n=this.a,s=this.b,r=this.c;let a,o;cr.subVectors(s,n),ur.subVectors(r,n),Gl.subVectors(e,n);const l=cr.dot(Gl),c=ur.dot(Gl);if(l<=0&&c<=0)return t.copy(n);Wl.subVectors(e,s);const u=cr.dot(Wl),h=ur.dot(Wl);if(u>=0&&h<=u)return t.copy(s);const d=l*h-u*c;if(d<=0&&l>=0&&u<=0)return a=l/(l-u),t.copy(n).addScaledVector(cr,a);Xl.subVectors(e,r);const f=cr.dot(Xl),g=ur.dot(Xl);if(g>=0&&f<=g)return t.copy(r);const v=f*c-l*g;if(v<=0&&c>=0&&g<=0)return o=c/(c-g),t.copy(n).addScaledVector(ur,o);const m=u*g-f*h;if(m<=0&&h-u>=0&&f-g>=0)return Uh.subVectors(r,s),o=(h-u)/(h-u+(f-g)),t.copy(s).addScaledVector(Uh,o);const p=1/(m+v+d);return a=v*p,o=d*p,t.copy(n).addScaledVector(cr,a).addScaledVector(ur,o)}equals(e){return e.a.equals(this.a)&&e.b.equals(this.b)&&e.c.equals(this.c)}}const Hf={aliceblue:15792383,antiquewhite:16444375,aqua:65535,aquamarine:8388564,azure:15794175,beige:16119260,bisque:16770244,black:0,blanchedalmond:16772045,blue:255,blueviolet:9055202,brown:10824234,burlywood:14596231,cadetblue:6266528,chartreuse:8388352,chocolate:13789470,coral:16744272,cornflowerblue:6591981,cornsilk:16775388,crimson:14423100,cyan:65535,darkblue:139,darkcyan:35723,darkgoldenrod:12092939,darkgray:11119017,darkgreen:25600,darkgrey:11119017,darkkhaki:12433259,darkmagenta:9109643,darkolivegreen:5597999,darkorange:16747520,darkorchid:10040012,darkred:9109504,darksalmon:15308410,darkseagreen:9419919,darkslateblue:4734347,darkslategray:3100495,darkslategrey:3100495,darkturquoise:52945,darkviolet:9699539,deeppink:16716947,deepskyblue:49151,dimgray:6908265,dimgrey:6908265,dodgerblue:2003199,firebrick:11674146,floralwhite:16775920,forestgreen:2263842,fuchsia:16711935,gainsboro:14474460,ghostwhite:16316671,gold:16766720,goldenrod:14329120,gray:8421504,green:32768,greenyellow:11403055,grey:8421504,honeydew:15794160,hotpink:16738740,indianred:13458524,indigo:4915330,ivory:16777200,khaki:15787660,lavender:15132410,lavenderblush:16773365,lawngreen:8190976,lemonchiffon:16775885,lightblue:11393254,lightcoral:15761536,lightcyan:14745599,lightgoldenrodyellow:16448210,lightgray:13882323,lightgreen:9498256,lightgrey:13882323,lightpink:16758465,lightsalmon:16752762,lightseagreen:2142890,lightskyblue:8900346,lightslategray:7833753,lightslategrey:7833753,lightsteelblue:11584734,lightyellow:16777184,lime:65280,limegreen:3329330,linen:16445670,magenta:16711935,maroon:8388608,mediumaquamarine:6737322,mediumblue:205,mediumorchid:12211667,mediumpurple:9662683,mediumseagreen:3978097,mediumslateblue:8087790,mediumspringgreen:64154,mediumturquoise:4772300,mediumvioletred:13047173,midnightblue:1644912,mintcream:16121850,mistyrose:16770273,moccasin:16770229,navajowhite:16768685,navy:128,oldlace:16643558,olive:8421376,olivedrab:7048739,orange:16753920,orangered:16729344,orchid:14315734,palegoldenrod:15657130,palegreen:10025880,paleturquoise:11529966,palevioletred:14381203,papayawhip:16773077,peachpuff:16767673,peru:13468991,pink:16761035,plum:14524637,powderblue:11591910,purple:8388736,rebeccapurple:6697881,red:16711680,rosybrown:12357519,royalblue:4286945,saddlebrown:9127187,salmon:16416882,sandybrown:16032864,seagreen:3050327,seashell:16774638,sienna:10506797,silver:12632256,skyblue:8900331,slateblue:6970061,slategray:7372944,slategrey:7372944,snow:16775930,springgreen:65407,steelblue:4620980,tan:13808780,teal:32896,thistle:14204888,tomato:16737095,turquoise:4251856,violet:15631086,wheat:16113331,white:16777215,whitesmoke:16119285,yellow:16776960,yellowgreen:10145074},es={h:0,s:0,l:0},to={h:0,s:0,l:0};function ql(i,e,t){return t<0&&(t+=1),t>1&&(t-=1),t<1/6?i+(e-i)*6*t:t<1/2?e:t<2/3?i+(e-i)*6*(2/3-t):i}class nt{constructor(e,t,n){return this.isColor=!0,this.r=1,this.g=1,this.b=1,this.set(e,t,n)}set(e,t,n){if(t===void 0&&n===void 0){const s=e;s&&s.isColor?this.copy(s):typeof s=="number"?this.setHex(s):typeof s=="string"&&this.setStyle(s)}else this.setRGB(e,t,n);return this}setScalar(e){return this.r=e,this.g=e,this.b=e,this}setHex(e,t=xi){return e=Math.floor(e),this.r=(e>>16&255)/255,this.g=(e>>8&255)/255,this.b=(e&255)/255,St.toWorkingColorSpace(this,t),this}setRGB(e,t,n,s=St.workingColorSpace){return this.r=e,this.g=t,this.b=n,St.toWorkingColorSpace(this,s),this}setHSL(e,t,n,s=St.workingColorSpace){if(e=xu(e,1),t=Mn(t,0,1),n=Mn(n,0,1),t===0)this.r=this.g=this.b=n;else{const r=n<=.5?n*(1+t):n+t-n*t,a=2*n-r;this.r=ql(a,r,e+1/3),this.g=ql(a,r,e),this.b=ql(a,r,e-1/3)}return St.toWorkingColorSpace(this,s),this}setStyle(e,t=xi){function n(r){r!==void 0&&parseFloat(r)<1&&console.warn("THREE.Color: Alpha component of "+e+" will be ignored.")}let s;if(s=/^(\w+)\(([^\)]*)\)/.exec(e)){let r;const a=s[1],o=s[2];switch(a){case"rgb":case"rgba":if(r=/^\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(o))return n(r[4]),this.setRGB(Math.min(255,parseInt(r[1],10))/255,Math.min(255,parseInt(r[2],10))/255,Math.min(255,parseInt(r[3],10))/255,t);if(r=/^\s*(\d+)\%\s*,\s*(\d+)\%\s*,\s*(\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(o))return n(r[4]),this.setRGB(Math.min(100,parseInt(r[1],10))/100,Math.min(100,parseInt(r[2],10))/100,Math.min(100,parseInt(r[3],10))/100,t);break;case"hsl":case"hsla":if(r=/^\s*(\d*\.?\d+)\s*,\s*(\d*\.?\d+)\%\s*,\s*(\d*\.?\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(o))return n(r[4]),this.setHSL(parseFloat(r[1])/360,parseFloat(r[2])/100,parseFloat(r[3])/100,t);break;default:console.warn("THREE.Color: Unknown color model "+e)}}else if(s=/^\#([A-Fa-f\d]+)$/.exec(e)){const r=s[1],a=r.length;if(a===3)return this.setRGB(parseInt(r.charAt(0),16)/15,parseInt(r.charAt(1),16)/15,parseInt(r.charAt(2),16)/15,t);if(a===6)return this.setHex(parseInt(r,16),t);console.warn("THREE.Color: Invalid hex color "+e)}else if(e&&e.length>0)return this.setColorName(e,t);return this}setColorName(e,t=xi){const n=Hf[e.toLowerCase()];return n!==void 0?this.setHex(n,t):console.warn("THREE.Color: Unknown color "+e),this}clone(){return new this.constructor(this.r,this.g,this.b)}copy(e){return this.r=e.r,this.g=e.g,this.b=e.b,this}copySRGBToLinear(e){return this.r=Dr(e.r),this.g=Dr(e.g),this.b=Dr(e.b),this}copyLinearToSRGB(e){return this.r=Il(e.r),this.g=Il(e.g),this.b=Il(e.b),this}convertSRGBToLinear(){return this.copySRGBToLinear(this),this}convertLinearToSRGB(){return this.copyLinearToSRGB(this),this}getHex(e=xi){return St.fromWorkingColorSpace(yn.copy(this),e),Math.round(Mn(yn.r*255,0,255))*65536+Math.round(Mn(yn.g*255,0,255))*256+Math.round(Mn(yn.b*255,0,255))}getHexString(e=xi){return("000000"+this.getHex(e).toString(16)).slice(-6)}getHSL(e,t=St.workingColorSpace){St.fromWorkingColorSpace(yn.copy(this),t);const n=yn.r,s=yn.g,r=yn.b,a=Math.max(n,s,r),o=Math.min(n,s,r);let l,c;const u=(o+a)/2;if(o===a)l=0,c=0;else{const h=a-o;switch(c=u<=.5?h/(a+o):h/(2-a-o),a){case n:l=(s-r)/h+(s<r?6:0);break;case s:l=(r-n)/h+2;break;case r:l=(n-s)/h+4;break}l/=6}return e.h=l,e.s=c,e.l=u,e}getRGB(e,t=St.workingColorSpace){return St.fromWorkingColorSpace(yn.copy(this),t),e.r=yn.r,e.g=yn.g,e.b=yn.b,e}getStyle(e=xi){St.fromWorkingColorSpace(yn.copy(this),e);const t=yn.r,n=yn.g,s=yn.b;return e!==xi?`color(${e} ${t.toFixed(3)} ${n.toFixed(3)} ${s.toFixed(3)})`:`rgb(${Math.round(t*255)},${Math.round(n*255)},${Math.round(s*255)})`}offsetHSL(e,t,n){return this.getHSL(es),this.setHSL(es.h+e,es.s+t,es.l+n)}add(e){return this.r+=e.r,this.g+=e.g,this.b+=e.b,this}addColors(e,t){return this.r=e.r+t.r,this.g=e.g+t.g,this.b=e.b+t.b,this}addScalar(e){return this.r+=e,this.g+=e,this.b+=e,this}sub(e){return this.r=Math.max(0,this.r-e.r),this.g=Math.max(0,this.g-e.g),this.b=Math.max(0,this.b-e.b),this}multiply(e){return this.r*=e.r,this.g*=e.g,this.b*=e.b,this}multiplyScalar(e){return this.r*=e,this.g*=e,this.b*=e,this}lerp(e,t){return this.r+=(e.r-this.r)*t,this.g+=(e.g-this.g)*t,this.b+=(e.b-this.b)*t,this}lerpColors(e,t,n){return this.r=e.r+(t.r-e.r)*n,this.g=e.g+(t.g-e.g)*n,this.b=e.b+(t.b-e.b)*n,this}lerpHSL(e,t){this.getHSL(es),e.getHSL(to);const n=Ea(es.h,to.h,t),s=Ea(es.s,to.s,t),r=Ea(es.l,to.l,t);return this.setHSL(n,s,r),this}setFromVector3(e){return this.r=e.x,this.g=e.y,this.b=e.z,this}applyMatrix3(e){const t=this.r,n=this.g,s=this.b,r=e.elements;return this.r=r[0]*t+r[3]*n+r[6]*s,this.g=r[1]*t+r[4]*n+r[7]*s,this.b=r[2]*t+r[5]*n+r[8]*s,this}equals(e){return e.r===this.r&&e.g===this.g&&e.b===this.b}fromArray(e,t=0){return this.r=e[t],this.g=e[t+1],this.b=e[t+2],this}toArray(e=[],t=0){return e[t]=this.r,e[t+1]=this.g,e[t+2]=this.b,e}fromBufferAttribute(e,t){return this.r=e.getX(t),this.g=e.getY(t),this.b=e.getZ(t),this}toJSON(){return this.getHex()}*[Symbol.iterator](){yield this.r,yield this.g,yield this.b}}const yn=new nt;nt.NAMES=Hf;let Gg=0;class ps extends jr{constructor(){super(),this.isMaterial=!0,Object.defineProperty(this,"id",{value:Gg++}),this.uuid=zi(),this.name="",this.type="Material",this.blending=Cr,this.side=cs,this.vertexColors=!1,this.opacity=1,this.transparent=!1,this.alphaHash=!1,this.blendSrc=vc,this.blendDst=xc,this.blendEquation=Rs,this.blendSrcAlpha=null,this.blendDstAlpha=null,this.blendEquationAlpha=null,this.blendColor=new nt(0,0,0),this.blendAlpha=0,this.depthFunc=zo,this.depthTest=!0,this.depthWrite=!0,this.stencilWriteMask=255,this.stencilFunc=yh,this.stencilRef=0,this.stencilFuncMask=255,this.stencilFail=tr,this.stencilZFail=tr,this.stencilZPass=tr,this.stencilWrite=!1,this.clippingPlanes=null,this.clipIntersection=!1,this.clipShadows=!1,this.shadowSide=null,this.colorWrite=!0,this.precision=null,this.polygonOffset=!1,this.polygonOffsetFactor=0,this.polygonOffsetUnits=0,this.dithering=!1,this.alphaToCoverage=!1,this.premultipliedAlpha=!1,this.forceSinglePass=!1,this.visible=!0,this.toneMapped=!0,this.userData={},this.version=0,this._alphaTest=0}get alphaTest(){return this._alphaTest}set alphaTest(e){this._alphaTest>0!=e>0&&this.version++,this._alphaTest=e}onBeforeRender(){}onBeforeCompile(){}customProgramCacheKey(){return this.onBeforeCompile.toString()}setValues(e){if(e!==void 0)for(const t in e){const n=e[t];if(n===void 0){console.warn(`THREE.Material: parameter '${t}' has value of undefined.`);continue}const s=this[t];if(s===void 0){console.warn(`THREE.Material: '${t}' is not a property of THREE.${this.type}.`);continue}s&&s.isColor?s.set(n):s&&s.isVector3&&n&&n.isVector3?s.copy(n):this[t]=n}}toJSON(e){const t=e===void 0||typeof e=="string";t&&(e={textures:{},images:{}});const n={metadata:{version:4.6,type:"Material",generator:"Material.toJSON"}};n.uuid=this.uuid,n.type=this.type,this.name!==""&&(n.name=this.name),this.color&&this.color.isColor&&(n.color=this.color.getHex()),this.roughness!==void 0&&(n.roughness=this.roughness),this.metalness!==void 0&&(n.metalness=this.metalness),this.sheen!==void 0&&(n.sheen=this.sheen),this.sheenColor&&this.sheenColor.isColor&&(n.sheenColor=this.sheenColor.getHex()),this.sheenRoughness!==void 0&&(n.sheenRoughness=this.sheenRoughness),this.emissive&&this.emissive.isColor&&(n.emissive=this.emissive.getHex()),this.emissiveIntensity!==void 0&&this.emissiveIntensity!==1&&(n.emissiveIntensity=this.emissiveIntensity),this.specular&&this.specular.isColor&&(n.specular=this.specular.getHex()),this.specularIntensity!==void 0&&(n.specularIntensity=this.specularIntensity),this.specularColor&&this.specularColor.isColor&&(n.specularColor=this.specularColor.getHex()),this.shininess!==void 0&&(n.shininess=this.shininess),this.clearcoat!==void 0&&(n.clearcoat=this.clearcoat),this.clearcoatRoughness!==void 0&&(n.clearcoatRoughness=this.clearcoatRoughness),this.clearcoatMap&&this.clearcoatMap.isTexture&&(n.clearcoatMap=this.clearcoatMap.toJSON(e).uuid),this.clearcoatRoughnessMap&&this.clearcoatRoughnessMap.isTexture&&(n.clearcoatRoughnessMap=this.clearcoatRoughnessMap.toJSON(e).uuid),this.clearcoatNormalMap&&this.clearcoatNormalMap.isTexture&&(n.clearcoatNormalMap=this.clearcoatNormalMap.toJSON(e).uuid,n.clearcoatNormalScale=this.clearcoatNormalScale.toArray()),this.dispersion!==void 0&&(n.dispersion=this.dispersion),this.iridescence!==void 0&&(n.iridescence=this.iridescence),this.iridescenceIOR!==void 0&&(n.iridescenceIOR=this.iridescenceIOR),this.iridescenceThicknessRange!==void 0&&(n.iridescenceThicknessRange=this.iridescenceThicknessRange),this.iridescenceMap&&this.iridescenceMap.isTexture&&(n.iridescenceMap=this.iridescenceMap.toJSON(e).uuid),this.iridescenceThicknessMap&&this.iridescenceThicknessMap.isTexture&&(n.iridescenceThicknessMap=this.iridescenceThicknessMap.toJSON(e).uuid),this.anisotropy!==void 0&&(n.anisotropy=this.anisotropy),this.anisotropyRotation!==void 0&&(n.anisotropyRotation=this.anisotropyRotation),this.anisotropyMap&&this.anisotropyMap.isTexture&&(n.anisotropyMap=this.anisotropyMap.toJSON(e).uuid),this.map&&this.map.isTexture&&(n.map=this.map.toJSON(e).uuid),this.matcap&&this.matcap.isTexture&&(n.matcap=this.matcap.toJSON(e).uuid),this.alphaMap&&this.alphaMap.isTexture&&(n.alphaMap=this.alphaMap.toJSON(e).uuid),this.lightMap&&this.lightMap.isTexture&&(n.lightMap=this.lightMap.toJSON(e).uuid,n.lightMapIntensity=this.lightMapIntensity),this.aoMap&&this.aoMap.isTexture&&(n.aoMap=this.aoMap.toJSON(e).uuid,n.aoMapIntensity=this.aoMapIntensity),this.bumpMap&&this.bumpMap.isTexture&&(n.bumpMap=this.bumpMap.toJSON(e).uuid,n.bumpScale=this.bumpScale),this.normalMap&&this.normalMap.isTexture&&(n.normalMap=this.normalMap.toJSON(e).uuid,n.normalMapType=this.normalMapType,n.normalScale=this.normalScale.toArray()),this.displacementMap&&this.displacementMap.isTexture&&(n.displacementMap=this.displacementMap.toJSON(e).uuid,n.displacementScale=this.displacementScale,n.displacementBias=this.displacementBias),this.roughnessMap&&this.roughnessMap.isTexture&&(n.roughnessMap=this.roughnessMap.toJSON(e).uuid),this.metalnessMap&&this.metalnessMap.isTexture&&(n.metalnessMap=this.metalnessMap.toJSON(e).uuid),this.emissiveMap&&this.emissiveMap.isTexture&&(n.emissiveMap=this.emissiveMap.toJSON(e).uuid),this.specularMap&&this.specularMap.isTexture&&(n.specularMap=this.specularMap.toJSON(e).uuid),this.specularIntensityMap&&this.specularIntensityMap.isTexture&&(n.specularIntensityMap=this.specularIntensityMap.toJSON(e).uuid),this.specularColorMap&&this.specularColorMap.isTexture&&(n.specularColorMap=this.specularColorMap.toJSON(e).uuid),this.envMap&&this.envMap.isTexture&&(n.envMap=this.envMap.toJSON(e).uuid,this.combine!==void 0&&(n.combine=this.combine)),this.envMapRotation!==void 0&&(n.envMapRotation=this.envMapRotation.toArray()),this.envMapIntensity!==void 0&&(n.envMapIntensity=this.envMapIntensity),this.reflectivity!==void 0&&(n.reflectivity=this.reflectivity),this.refractionRatio!==void 0&&(n.refractionRatio=this.refractionRatio),this.gradientMap&&this.gradientMap.isTexture&&(n.gradientMap=this.gradientMap.toJSON(e).uuid),this.transmission!==void 0&&(n.transmission=this.transmission),this.transmissionMap&&this.transmissionMap.isTexture&&(n.transmissionMap=this.transmissionMap.toJSON(e).uuid),this.thickness!==void 0&&(n.thickness=this.thickness),this.thicknessMap&&this.thicknessMap.isTexture&&(n.thicknessMap=this.thicknessMap.toJSON(e).uuid),this.attenuationDistance!==void 0&&this.attenuationDistance!==1/0&&(n.attenuationDistance=this.attenuationDistance),this.attenuationColor!==void 0&&(n.attenuationColor=this.attenuationColor.getHex()),this.size!==void 0&&(n.size=this.size),this.shadowSide!==null&&(n.shadowSide=this.shadowSide),this.sizeAttenuation!==void 0&&(n.sizeAttenuation=this.sizeAttenuation),this.blending!==Cr&&(n.blending=this.blending),this.side!==cs&&(n.side=this.side),this.vertexColors===!0&&(n.vertexColors=!0),this.opacity<1&&(n.opacity=this.opacity),this.transparent===!0&&(n.transparent=!0),this.blendSrc!==vc&&(n.blendSrc=this.blendSrc),this.blendDst!==xc&&(n.blendDst=this.blendDst),this.blendEquation!==Rs&&(n.blendEquation=this.blendEquation),this.blendSrcAlpha!==null&&(n.blendSrcAlpha=this.blendSrcAlpha),this.blendDstAlpha!==null&&(n.blendDstAlpha=this.blendDstAlpha),this.blendEquationAlpha!==null&&(n.blendEquationAlpha=this.blendEquationAlpha),this.blendColor&&this.blendColor.isColor&&(n.blendColor=this.blendColor.getHex()),this.blendAlpha!==0&&(n.blendAlpha=this.blendAlpha),this.depthFunc!==zo&&(n.depthFunc=this.depthFunc),this.depthTest===!1&&(n.depthTest=this.depthTest),this.depthWrite===!1&&(n.depthWrite=this.depthWrite),this.colorWrite===!1&&(n.colorWrite=this.colorWrite),this.stencilWriteMask!==255&&(n.stencilWriteMask=this.stencilWriteMask),this.stencilFunc!==yh&&(n.stencilFunc=this.stencilFunc),this.stencilRef!==0&&(n.stencilRef=this.stencilRef),this.stencilFuncMask!==255&&(n.stencilFuncMask=this.stencilFuncMask),this.stencilFail!==tr&&(n.stencilFail=this.stencilFail),this.stencilZFail!==tr&&(n.stencilZFail=this.stencilZFail),this.stencilZPass!==tr&&(n.stencilZPass=this.stencilZPass),this.stencilWrite===!0&&(n.stencilWrite=this.stencilWrite),this.rotation!==void 0&&this.rotation!==0&&(n.rotation=this.rotation),this.polygonOffset===!0&&(n.polygonOffset=!0),this.polygonOffsetFactor!==0&&(n.polygonOffsetFactor=this.polygonOffsetFactor),this.polygonOffsetUnits!==0&&(n.polygonOffsetUnits=this.polygonOffsetUnits),this.linewidth!==void 0&&this.linewidth!==1&&(n.linewidth=this.linewidth),this.dashSize!==void 0&&(n.dashSize=this.dashSize),this.gapSize!==void 0&&(n.gapSize=this.gapSize),this.scale!==void 0&&(n.scale=this.scale),this.dithering===!0&&(n.dithering=!0),this.alphaTest>0&&(n.alphaTest=this.alphaTest),this.alphaHash===!0&&(n.alphaHash=!0),this.alphaToCoverage===!0&&(n.alphaToCoverage=!0),this.premultipliedAlpha===!0&&(n.premultipliedAlpha=!0),this.forceSinglePass===!0&&(n.forceSinglePass=!0),this.wireframe===!0&&(n.wireframe=!0),this.wireframeLinewidth>1&&(n.wireframeLinewidth=this.wireframeLinewidth),this.wireframeLinecap!=="round"&&(n.wireframeLinecap=this.wireframeLinecap),this.wireframeLinejoin!=="round"&&(n.wireframeLinejoin=this.wireframeLinejoin),this.flatShading===!0&&(n.flatShading=!0),this.visible===!1&&(n.visible=!1),this.toneMapped===!1&&(n.toneMapped=!1),this.fog===!1&&(n.fog=!1),Object.keys(this.userData).length>0&&(n.userData=this.userData);function s(r){const a=[];for(const o in r){const l=r[o];delete l.metadata,a.push(l)}return a}if(t){const r=s(e.textures),a=s(e.images);r.length>0&&(n.textures=r),a.length>0&&(n.images=a)}return n}clone(){return new this.constructor().copy(this)}copy(e){this.name=e.name,this.blending=e.blending,this.side=e.side,this.vertexColors=e.vertexColors,this.opacity=e.opacity,this.transparent=e.transparent,this.blendSrc=e.blendSrc,this.blendDst=e.blendDst,this.blendEquation=e.blendEquation,this.blendSrcAlpha=e.blendSrcAlpha,this.blendDstAlpha=e.blendDstAlpha,this.blendEquationAlpha=e.blendEquationAlpha,this.blendColor.copy(e.blendColor),this.blendAlpha=e.blendAlpha,this.depthFunc=e.depthFunc,this.depthTest=e.depthTest,this.depthWrite=e.depthWrite,this.stencilWriteMask=e.stencilWriteMask,this.stencilFunc=e.stencilFunc,this.stencilRef=e.stencilRef,this.stencilFuncMask=e.stencilFuncMask,this.stencilFail=e.stencilFail,this.stencilZFail=e.stencilZFail,this.stencilZPass=e.stencilZPass,this.stencilWrite=e.stencilWrite;const t=e.clippingPlanes;let n=null;if(t!==null){const s=t.length;n=new Array(s);for(let r=0;r!==s;++r)n[r]=t[r].clone()}return this.clippingPlanes=n,this.clipIntersection=e.clipIntersection,this.clipShadows=e.clipShadows,this.shadowSide=e.shadowSide,this.colorWrite=e.colorWrite,this.precision=e.precision,this.polygonOffset=e.polygonOffset,this.polygonOffsetFactor=e.polygonOffsetFactor,this.polygonOffsetUnits=e.polygonOffsetUnits,this.dithering=e.dithering,this.alphaTest=e.alphaTest,this.alphaHash=e.alphaHash,this.alphaToCoverage=e.alphaToCoverage,this.premultipliedAlpha=e.premultipliedAlpha,this.forceSinglePass=e.forceSinglePass,this.visible=e.visible,this.toneMapped=e.toneMapped,this.userData=JSON.parse(JSON.stringify(e.userData)),this}dispose(){this.dispatchEvent({type:"dispose"})}set needsUpdate(e){e===!0&&this.version++}onBuild(){console.warn("Material: onBuild() has been removed.")}}class Ir extends ps{constructor(e){super(),this.isMeshBasicMaterial=!0,this.type="MeshBasicMaterial",this.color=new nt(16777215),this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.specularMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new Si,this.combine=bf,this.reflectivity=1,this.refractionRatio=.98,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.lightMap=e.lightMap,this.lightMapIntensity=e.lightMapIntensity,this.aoMap=e.aoMap,this.aoMapIntensity=e.aoMapIntensity,this.specularMap=e.specularMap,this.alphaMap=e.alphaMap,this.envMap=e.envMap,this.envMapRotation.copy(e.envMapRotation),this.combine=e.combine,this.reflectivity=e.reflectivity,this.refractionRatio=e.refractionRatio,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.wireframeLinecap=e.wireframeLinecap,this.wireframeLinejoin=e.wireframeLinejoin,this.fog=e.fog,this}}const jt=new k,no=new qe;class ui{constructor(e,t,n=!1){if(Array.isArray(e))throw new TypeError("THREE.BufferAttribute: array should be a Typed Array.");this.isBufferAttribute=!0,this.name="",this.array=e,this.itemSize=t,this.count=e!==void 0?e.length/t:0,this.normalized=n,this.usage=Kc,this._updateRange={offset:0,count:-1},this.updateRanges=[],this.gpuType=Fi,this.version=0}onUploadCallback(){}set needsUpdate(e){e===!0&&this.version++}get updateRange(){return Lr("THREE.BufferAttribute: updateRange() is deprecated and will be removed in r169. Use addUpdateRange() instead."),this._updateRange}setUsage(e){return this.usage=e,this}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}copy(e){return this.name=e.name,this.array=new e.array.constructor(e.array),this.itemSize=e.itemSize,this.count=e.count,this.normalized=e.normalized,this.usage=e.usage,this.gpuType=e.gpuType,this}copyAt(e,t,n){e*=this.itemSize,n*=t.itemSize;for(let s=0,r=this.itemSize;s<r;s++)this.array[e+s]=t.array[n+s];return this}copyArray(e){return this.array.set(e),this}applyMatrix3(e){if(this.itemSize===2)for(let t=0,n=this.count;t<n;t++)no.fromBufferAttribute(this,t),no.applyMatrix3(e),this.setXY(t,no.x,no.y);else if(this.itemSize===3)for(let t=0,n=this.count;t<n;t++)jt.fromBufferAttribute(this,t),jt.applyMatrix3(e),this.setXYZ(t,jt.x,jt.y,jt.z);return this}applyMatrix4(e){for(let t=0,n=this.count;t<n;t++)jt.fromBufferAttribute(this,t),jt.applyMatrix4(e),this.setXYZ(t,jt.x,jt.y,jt.z);return this}applyNormalMatrix(e){for(let t=0,n=this.count;t<n;t++)jt.fromBufferAttribute(this,t),jt.applyNormalMatrix(e),this.setXYZ(t,jt.x,jt.y,jt.z);return this}transformDirection(e){for(let t=0,n=this.count;t<n;t++)jt.fromBufferAttribute(this,t),jt.transformDirection(e),this.setXYZ(t,jt.x,jt.y,jt.z);return this}set(e,t=0){return this.array.set(e,t),this}getComponent(e,t){let n=this.array[e*this.itemSize+t];return this.normalized&&(n=oi(n,this.array)),n}setComponent(e,t,n){return this.normalized&&(n=wt(n,this.array)),this.array[e*this.itemSize+t]=n,this}getX(e){let t=this.array[e*this.itemSize];return this.normalized&&(t=oi(t,this.array)),t}setX(e,t){return this.normalized&&(t=wt(t,this.array)),this.array[e*this.itemSize]=t,this}getY(e){let t=this.array[e*this.itemSize+1];return this.normalized&&(t=oi(t,this.array)),t}setY(e,t){return this.normalized&&(t=wt(t,this.array)),this.array[e*this.itemSize+1]=t,this}getZ(e){let t=this.array[e*this.itemSize+2];return this.normalized&&(t=oi(t,this.array)),t}setZ(e,t){return this.normalized&&(t=wt(t,this.array)),this.array[e*this.itemSize+2]=t,this}getW(e){let t=this.array[e*this.itemSize+3];return this.normalized&&(t=oi(t,this.array)),t}setW(e,t){return this.normalized&&(t=wt(t,this.array)),this.array[e*this.itemSize+3]=t,this}setXY(e,t,n){return e*=this.itemSize,this.normalized&&(t=wt(t,this.array),n=wt(n,this.array)),this.array[e+0]=t,this.array[e+1]=n,this}setXYZ(e,t,n,s){return e*=this.itemSize,this.normalized&&(t=wt(t,this.array),n=wt(n,this.array),s=wt(s,this.array)),this.array[e+0]=t,this.array[e+1]=n,this.array[e+2]=s,this}setXYZW(e,t,n,s,r){return e*=this.itemSize,this.normalized&&(t=wt(t,this.array),n=wt(n,this.array),s=wt(s,this.array),r=wt(r,this.array)),this.array[e+0]=t,this.array[e+1]=n,this.array[e+2]=s,this.array[e+3]=r,this}onUpload(e){return this.onUploadCallback=e,this}clone(){return new this.constructor(this.array,this.itemSize).copy(this)}toJSON(){const e={itemSize:this.itemSize,type:this.array.constructor.name,array:Array.from(this.array),normalized:this.normalized};return this.name!==""&&(e.name=this.name),this.usage!==Kc&&(e.usage=this.usage),e}}class Vf extends ui{constructor(e,t,n){super(new Uint16Array(e),t,n)}}class Gf extends ui{constructor(e,t,n){super(new Uint32Array(e),t,n)}}class qt extends ui{constructor(e,t,n){super(new Float32Array(e),t,n)}}let Wg=0;const Wn=new Ot,Yl=new Jt,hr=new k,Bn=new Ua,da=new Ua,hn=new k;class Xt extends jr{constructor(){super(),this.isBufferGeometry=!0,Object.defineProperty(this,"id",{value:Wg++}),this.uuid=zi(),this.name="",this.type="BufferGeometry",this.index=null,this.attributes={},this.morphAttributes={},this.morphTargetsRelative=!1,this.groups=[],this.boundingBox=null,this.boundingSphere=null,this.drawRange={start:0,count:1/0},this.userData={}}getIndex(){return this.index}setIndex(e){return Array.isArray(e)?this.index=new(Bf(e)?Gf:Vf)(e,1):this.index=e,this}getAttribute(e){return this.attributes[e]}setAttribute(e,t){return this.attributes[e]=t,this}deleteAttribute(e){return delete this.attributes[e],this}hasAttribute(e){return this.attributes[e]!==void 0}addGroup(e,t,n=0){this.groups.push({start:e,count:t,materialIndex:n})}clearGroups(){this.groups=[]}setDrawRange(e,t){this.drawRange.start=e,this.drawRange.count=t}applyMatrix4(e){const t=this.attributes.position;t!==void 0&&(t.applyMatrix4(e),t.needsUpdate=!0);const n=this.attributes.normal;if(n!==void 0){const r=new rt().getNormalMatrix(e);n.applyNormalMatrix(r),n.needsUpdate=!0}const s=this.attributes.tangent;return s!==void 0&&(s.transformDirection(e),s.needsUpdate=!0),this.boundingBox!==null&&this.computeBoundingBox(),this.boundingSphere!==null&&this.computeBoundingSphere(),this}applyQuaternion(e){return Wn.makeRotationFromQuaternion(e),this.applyMatrix4(Wn),this}rotateX(e){return Wn.makeRotationX(e),this.applyMatrix4(Wn),this}rotateY(e){return Wn.makeRotationY(e),this.applyMatrix4(Wn),this}rotateZ(e){return Wn.makeRotationZ(e),this.applyMatrix4(Wn),this}translate(e,t,n){return Wn.makeTranslation(e,t,n),this.applyMatrix4(Wn),this}scale(e,t,n){return Wn.makeScale(e,t,n),this.applyMatrix4(Wn),this}lookAt(e){return Yl.lookAt(e),Yl.updateMatrix(),this.applyMatrix4(Yl.matrix),this}center(){return this.computeBoundingBox(),this.boundingBox.getCenter(hr).negate(),this.translate(hr.x,hr.y,hr.z),this}setFromPoints(e){const t=[];for(let n=0,s=e.length;n<s;n++){const r=e[n];t.push(r.x,r.y,r.z||0)}return this.setAttribute("position",new qt(t,3)),this}computeBoundingBox(){this.boundingBox===null&&(this.boundingBox=new Ua);const e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingBox(): GLBufferAttribute requires a manual bounding box.",this),this.boundingBox.set(new k(-1/0,-1/0,-1/0),new k(1/0,1/0,1/0));return}if(e!==void 0){if(this.boundingBox.setFromBufferAttribute(e),t)for(let n=0,s=t.length;n<s;n++){const r=t[n];Bn.setFromBufferAttribute(r),this.morphTargetsRelative?(hn.addVectors(this.boundingBox.min,Bn.min),this.boundingBox.expandByPoint(hn),hn.addVectors(this.boundingBox.max,Bn.max),this.boundingBox.expandByPoint(hn)):(this.boundingBox.expandByPoint(Bn.min),this.boundingBox.expandByPoint(Bn.max))}}else this.boundingBox.makeEmpty();(isNaN(this.boundingBox.min.x)||isNaN(this.boundingBox.min.y)||isNaN(this.boundingBox.min.z))&&console.error('THREE.BufferGeometry.computeBoundingBox(): Computed min/max have NaN values. The "position" attribute is likely to have NaN values.',this)}computeBoundingSphere(){this.boundingSphere===null&&(this.boundingSphere=new Na);const e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingSphere(): GLBufferAttribute requires a manual bounding sphere.",this),this.boundingSphere.set(new k,1/0);return}if(e){const n=this.boundingSphere.center;if(Bn.setFromBufferAttribute(e),t)for(let r=0,a=t.length;r<a;r++){const o=t[r];da.setFromBufferAttribute(o),this.morphTargetsRelative?(hn.addVectors(Bn.min,da.min),Bn.expandByPoint(hn),hn.addVectors(Bn.max,da.max),Bn.expandByPoint(hn)):(Bn.expandByPoint(da.min),Bn.expandByPoint(da.max))}Bn.getCenter(n);let s=0;for(let r=0,a=e.count;r<a;r++)hn.fromBufferAttribute(e,r),s=Math.max(s,n.distanceToSquared(hn));if(t)for(let r=0,a=t.length;r<a;r++){const o=t[r],l=this.morphTargetsRelative;for(let c=0,u=o.count;c<u;c++)hn.fromBufferAttribute(o,c),l&&(hr.fromBufferAttribute(e,c),hn.add(hr)),s=Math.max(s,n.distanceToSquared(hn))}this.boundingSphere.radius=Math.sqrt(s),isNaN(this.boundingSphere.radius)&&console.error('THREE.BufferGeometry.computeBoundingSphere(): Computed radius is NaN. The "position" attribute is likely to have NaN values.',this)}}computeTangents(){const e=this.index,t=this.attributes;if(e===null||t.position===void 0||t.normal===void 0||t.uv===void 0){console.error("THREE.BufferGeometry: .computeTangents() failed. Missing required attributes (index, position, normal or uv)");return}const n=t.position,s=t.normal,r=t.uv;this.hasAttribute("tangent")===!1&&this.setAttribute("tangent",new ui(new Float32Array(4*n.count),4));const a=this.getAttribute("tangent"),o=[],l=[];for(let N=0;N<n.count;N++)o[N]=new k,l[N]=new k;const c=new k,u=new k,h=new k,d=new qe,f=new qe,g=new qe,v=new k,m=new k;function p(N,b,x){c.fromBufferAttribute(n,N),u.fromBufferAttribute(n,b),h.fromBufferAttribute(n,x),d.fromBufferAttribute(r,N),f.fromBufferAttribute(r,b),g.fromBufferAttribute(r,x),u.sub(c),h.sub(c),f.sub(d),g.sub(d);const R=1/(f.x*g.y-g.x*f.y);isFinite(R)&&(v.copy(u).multiplyScalar(g.y).addScaledVector(h,-f.y).multiplyScalar(R),m.copy(h).multiplyScalar(f.x).addScaledVector(u,-g.x).multiplyScalar(R),o[N].add(v),o[b].add(v),o[x].add(v),l[N].add(m),l[b].add(m),l[x].add(m))}let S=this.groups;S.length===0&&(S=[{start:0,count:e.count}]);for(let N=0,b=S.length;N<b;++N){const x=S[N],R=x.start,j=x.count;for(let z=R,K=R+j;z<K;z+=3)p(e.getX(z+0),e.getX(z+1),e.getX(z+2))}const y=new k,w=new k,O=new k,A=new k;function P(N){O.fromBufferAttribute(s,N),A.copy(O);const b=o[N];y.copy(b),y.sub(O.multiplyScalar(O.dot(b))).normalize(),w.crossVectors(A,b);const R=w.dot(l[N])<0?-1:1;a.setXYZW(N,y.x,y.y,y.z,R)}for(let N=0,b=S.length;N<b;++N){const x=S[N],R=x.start,j=x.count;for(let z=R,K=R+j;z<K;z+=3)P(e.getX(z+0)),P(e.getX(z+1)),P(e.getX(z+2))}}computeVertexNormals(){const e=this.index,t=this.getAttribute("position");if(t!==void 0){let n=this.getAttribute("normal");if(n===void 0)n=new ui(new Float32Array(t.count*3),3),this.setAttribute("normal",n);else for(let d=0,f=n.count;d<f;d++)n.setXYZ(d,0,0,0);const s=new k,r=new k,a=new k,o=new k,l=new k,c=new k,u=new k,h=new k;if(e)for(let d=0,f=e.count;d<f;d+=3){const g=e.getX(d+0),v=e.getX(d+1),m=e.getX(d+2);s.fromBufferAttribute(t,g),r.fromBufferAttribute(t,v),a.fromBufferAttribute(t,m),u.subVectors(a,r),h.subVectors(s,r),u.cross(h),o.fromBufferAttribute(n,g),l.fromBufferAttribute(n,v),c.fromBufferAttribute(n,m),o.add(u),l.add(u),c.add(u),n.setXYZ(g,o.x,o.y,o.z),n.setXYZ(v,l.x,l.y,l.z),n.setXYZ(m,c.x,c.y,c.z)}else for(let d=0,f=t.count;d<f;d+=3)s.fromBufferAttribute(t,d+0),r.fromBufferAttribute(t,d+1),a.fromBufferAttribute(t,d+2),u.subVectors(a,r),h.subVectors(s,r),u.cross(h),n.setXYZ(d+0,u.x,u.y,u.z),n.setXYZ(d+1,u.x,u.y,u.z),n.setXYZ(d+2,u.x,u.y,u.z);this.normalizeNormals(),n.needsUpdate=!0}}normalizeNormals(){const e=this.attributes.normal;for(let t=0,n=e.count;t<n;t++)hn.fromBufferAttribute(e,t),hn.normalize(),e.setXYZ(t,hn.x,hn.y,hn.z)}toNonIndexed(){function e(o,l){const c=o.array,u=o.itemSize,h=o.normalized,d=new c.constructor(l.length*u);let f=0,g=0;for(let v=0,m=l.length;v<m;v++){o.isInterleavedBufferAttribute?f=l[v]*o.data.stride+o.offset:f=l[v]*u;for(let p=0;p<u;p++)d[g++]=c[f++]}return new ui(d,u,h)}if(this.index===null)return console.warn("THREE.BufferGeometry.toNonIndexed(): BufferGeometry is already non-indexed."),this;const t=new Xt,n=this.index.array,s=this.attributes;for(const o in s){const l=s[o],c=e(l,n);t.setAttribute(o,c)}const r=this.morphAttributes;for(const o in r){const l=[],c=r[o];for(let u=0,h=c.length;u<h;u++){const d=c[u],f=e(d,n);l.push(f)}t.morphAttributes[o]=l}t.morphTargetsRelative=this.morphTargetsRelative;const a=this.groups;for(let o=0,l=a.length;o<l;o++){const c=a[o];t.addGroup(c.start,c.count,c.materialIndex)}return t}toJSON(){const e={metadata:{version:4.6,type:"BufferGeometry",generator:"BufferGeometry.toJSON"}};if(e.uuid=this.uuid,e.type=this.type,this.name!==""&&(e.name=this.name),Object.keys(this.userData).length>0&&(e.userData=this.userData),this.parameters!==void 0){const l=this.parameters;for(const c in l)l[c]!==void 0&&(e[c]=l[c]);return e}e.data={attributes:{}};const t=this.index;t!==null&&(e.data.index={type:t.array.constructor.name,array:Array.prototype.slice.call(t.array)});const n=this.attributes;for(const l in n){const c=n[l];e.data.attributes[l]=c.toJSON(e.data)}const s={};let r=!1;for(const l in this.morphAttributes){const c=this.morphAttributes[l],u=[];for(let h=0,d=c.length;h<d;h++){const f=c[h];u.push(f.toJSON(e.data))}u.length>0&&(s[l]=u,r=!0)}r&&(e.data.morphAttributes=s,e.data.morphTargetsRelative=this.morphTargetsRelative);const a=this.groups;a.length>0&&(e.data.groups=JSON.parse(JSON.stringify(a)));const o=this.boundingSphere;return o!==null&&(e.data.boundingSphere={center:o.center.toArray(),radius:o.radius}),e}clone(){return new this.constructor().copy(this)}copy(e){this.index=null,this.attributes={},this.morphAttributes={},this.groups=[],this.boundingBox=null,this.boundingSphere=null;const t={};this.name=e.name;const n=e.index;n!==null&&this.setIndex(n.clone(t));const s=e.attributes;for(const c in s){const u=s[c];this.setAttribute(c,u.clone(t))}const r=e.morphAttributes;for(const c in r){const u=[],h=r[c];for(let d=0,f=h.length;d<f;d++)u.push(h[d].clone(t));this.morphAttributes[c]=u}this.morphTargetsRelative=e.morphTargetsRelative;const a=e.groups;for(let c=0,u=a.length;c<u;c++){const h=a[c];this.addGroup(h.start,h.count,h.materialIndex)}const o=e.boundingBox;o!==null&&(this.boundingBox=o.clone());const l=e.boundingSphere;return l!==null&&(this.boundingSphere=l.clone()),this.drawRange.start=e.drawRange.start,this.drawRange.count=e.drawRange.count,this.userData=e.userData,this}dispose(){this.dispatchEvent({type:"dispose"})}}const Nh=new Ot,Ss=new Fa,io=new Na,Fh=new k,dr=new k,fr=new k,pr=new k,$l=new k,so=new k,ro=new qe,ao=new qe,oo=new qe,Oh=new k,Bh=new k,zh=new k,lo=new k,co=new k;class gn extends Jt{constructor(e=new Xt,t=new Ir){super(),this.isMesh=!0,this.type="Mesh",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),e.morphTargetInfluences!==void 0&&(this.morphTargetInfluences=e.morphTargetInfluences.slice()),e.morphTargetDictionary!==void 0&&(this.morphTargetDictionary=Object.assign({},e.morphTargetDictionary)),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const s=t[n[0]];if(s!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let r=0,a=s.length;r<a;r++){const o=s[r].name||String(r);this.morphTargetInfluences.push(0),this.morphTargetDictionary[o]=r}}}}getVertexPosition(e,t){const n=this.geometry,s=n.attributes.position,r=n.morphAttributes.position,a=n.morphTargetsRelative;t.fromBufferAttribute(s,e);const o=this.morphTargetInfluences;if(r&&o){so.set(0,0,0);for(let l=0,c=r.length;l<c;l++){const u=o[l],h=r[l];u!==0&&($l.fromBufferAttribute(h,e),a?so.addScaledVector($l,u):so.addScaledVector($l.sub(t),u))}t.add(so)}return t}raycast(e,t){const n=this.geometry,s=this.material,r=this.matrixWorld;s!==void 0&&(n.boundingSphere===null&&n.computeBoundingSphere(),io.copy(n.boundingSphere),io.applyMatrix4(r),Ss.copy(e.ray).recast(e.near),!(io.containsPoint(Ss.origin)===!1&&(Ss.intersectSphere(io,Fh)===null||Ss.origin.distanceToSquared(Fh)>(e.far-e.near)**2))&&(Nh.copy(r).invert(),Ss.copy(e.ray).applyMatrix4(Nh),!(n.boundingBox!==null&&Ss.intersectsBox(n.boundingBox)===!1)&&this._computeIntersections(e,t,Ss)))}_computeIntersections(e,t,n){let s;const r=this.geometry,a=this.material,o=r.index,l=r.attributes.position,c=r.attributes.uv,u=r.attributes.uv1,h=r.attributes.normal,d=r.groups,f=r.drawRange;if(o!==null)if(Array.isArray(a))for(let g=0,v=d.length;g<v;g++){const m=d[g],p=a[m.materialIndex],S=Math.max(m.start,f.start),y=Math.min(o.count,Math.min(m.start+m.count,f.start+f.count));for(let w=S,O=y;w<O;w+=3){const A=o.getX(w),P=o.getX(w+1),N=o.getX(w+2);s=uo(this,p,e,n,c,u,h,A,P,N),s&&(s.faceIndex=Math.floor(w/3),s.face.materialIndex=m.materialIndex,t.push(s))}}else{const g=Math.max(0,f.start),v=Math.min(o.count,f.start+f.count);for(let m=g,p=v;m<p;m+=3){const S=o.getX(m),y=o.getX(m+1),w=o.getX(m+2);s=uo(this,a,e,n,c,u,h,S,y,w),s&&(s.faceIndex=Math.floor(m/3),t.push(s))}}else if(l!==void 0)if(Array.isArray(a))for(let g=0,v=d.length;g<v;g++){const m=d[g],p=a[m.materialIndex],S=Math.max(m.start,f.start),y=Math.min(l.count,Math.min(m.start+m.count,f.start+f.count));for(let w=S,O=y;w<O;w+=3){const A=w,P=w+1,N=w+2;s=uo(this,p,e,n,c,u,h,A,P,N),s&&(s.faceIndex=Math.floor(w/3),s.face.materialIndex=m.materialIndex,t.push(s))}}else{const g=Math.max(0,f.start),v=Math.min(l.count,f.start+f.count);for(let m=g,p=v;m<p;m+=3){const S=m,y=m+1,w=m+2;s=uo(this,a,e,n,c,u,h,S,y,w),s&&(s.faceIndex=Math.floor(m/3),t.push(s))}}}}function Xg(i,e,t,n,s,r,a,o){let l;if(e.side===In?l=n.intersectTriangle(a,r,s,!0,o):l=n.intersectTriangle(s,r,a,e.side===cs,o),l===null)return null;co.copy(o),co.applyMatrix4(i.matrixWorld);const c=t.ray.origin.distanceTo(co);return c<t.near||c>t.far?null:{distance:c,point:co.clone(),object:i}}function uo(i,e,t,n,s,r,a,o,l,c){i.getVertexPosition(o,dr),i.getVertexPosition(l,fr),i.getVertexPosition(c,pr);const u=Xg(i,e,t,n,dr,fr,pr,lo);if(u){s&&(ro.fromBufferAttribute(s,o),ao.fromBufferAttribute(s,l),oo.fromBufferAttribute(s,c),u.uv=jn.getInterpolation(lo,dr,fr,pr,ro,ao,oo,new qe)),r&&(ro.fromBufferAttribute(r,o),ao.fromBufferAttribute(r,l),oo.fromBufferAttribute(r,c),u.uv1=jn.getInterpolation(lo,dr,fr,pr,ro,ao,oo,new qe)),a&&(Oh.fromBufferAttribute(a,o),Bh.fromBufferAttribute(a,l),zh.fromBufferAttribute(a,c),u.normal=jn.getInterpolation(lo,dr,fr,pr,Oh,Bh,zh,new k),u.normal.dot(n.direction)>0&&u.normal.multiplyScalar(-1));const h={a:o,b:l,c,normal:new k,materialIndex:0};jn.getNormal(dr,fr,pr,h.normal),u.face=h}return u}class Bi extends Xt{constructor(e=1,t=1,n=1,s=1,r=1,a=1){super(),this.type="BoxGeometry",this.parameters={width:e,height:t,depth:n,widthSegments:s,heightSegments:r,depthSegments:a};const o=this;s=Math.floor(s),r=Math.floor(r),a=Math.floor(a);const l=[],c=[],u=[],h=[];let d=0,f=0;g("z","y","x",-1,-1,n,t,e,a,r,0),g("z","y","x",1,-1,n,t,-e,a,r,1),g("x","z","y",1,1,e,n,t,s,a,2),g("x","z","y",1,-1,e,n,-t,s,a,3),g("x","y","z",1,-1,e,t,n,s,r,4),g("x","y","z",-1,-1,e,t,-n,s,r,5),this.setIndex(l),this.setAttribute("position",new qt(c,3)),this.setAttribute("normal",new qt(u,3)),this.setAttribute("uv",new qt(h,2));function g(v,m,p,S,y,w,O,A,P,N,b){const x=w/P,R=O/N,j=w/2,z=O/2,K=A/2,X=P+1,Q=N+1;let Y=0,ne=0;const ge=new k;for(let de=0;de<Q;de++){const xe=de*R-z;for(let we=0;we<X;we++){const ye=we*x-j;ge[v]=ye*S,ge[m]=xe*y,ge[p]=K,c.push(ge.x,ge.y,ge.z),ge[v]=0,ge[m]=0,ge[p]=A>0?1:-1,u.push(ge.x,ge.y,ge.z),h.push(we/P),h.push(1-de/N),Y+=1}}for(let de=0;de<N;de++)for(let xe=0;xe<P;xe++){const we=d+xe+X*de,ye=d+xe+X*(de+1),ie=d+(xe+1)+X*(de+1),ue=d+(xe+1)+X*de;l.push(we,ye,ue),l.push(ye,ie,ue),ne+=6}o.addGroup(f,ne,b),f+=ne,d+=Y}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Bi(e.width,e.height,e.depth,e.widthSegments,e.heightSegments,e.depthSegments)}}function Hr(i){const e={};for(const t in i){e[t]={};for(const n in i[t]){const s=i[t][n];s&&(s.isColor||s.isMatrix3||s.isMatrix4||s.isVector2||s.isVector3||s.isVector4||s.isTexture||s.isQuaternion)?s.isRenderTargetTexture?(console.warn("UniformsUtils: Textures of render targets cannot be cloned via cloneUniforms() or mergeUniforms()."),e[t][n]=null):e[t][n]=s.clone():Array.isArray(s)?e[t][n]=s.slice():e[t][n]=s}}return e}function Rn(i){const e={};for(let t=0;t<i.length;t++){const n=Hr(i[t]);for(const s in n)e[s]=n[s]}return e}function qg(i){const e=[];for(let t=0;t<i.length;t++)e.push(i[t].clone());return e}function Wf(i){const e=i.getRenderTarget();return e===null?i.outputColorSpace:e.isXRRenderTarget===!0?e.texture.colorSpace:St.workingColorSpace}const Yg={clone:Hr,merge:Rn};var $g=`void main() {
	gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
}`,jg=`void main() {
	gl_FragColor = vec4( 1.0, 0.0, 0.0, 1.0 );
}`;class us extends ps{constructor(e){super(),this.isShaderMaterial=!0,this.type="ShaderMaterial",this.defines={},this.uniforms={},this.uniformsGroups=[],this.vertexShader=$g,this.fragmentShader=jg,this.linewidth=1,this.wireframe=!1,this.wireframeLinewidth=1,this.fog=!1,this.lights=!1,this.clipping=!1,this.forceSinglePass=!0,this.extensions={clipCullDistance:!1,multiDraw:!1},this.defaultAttributeValues={color:[1,1,1],uv:[0,0],uv1:[0,0]},this.index0AttributeName=void 0,this.uniformsNeedUpdate=!1,this.glslVersion=null,e!==void 0&&this.setValues(e)}copy(e){return super.copy(e),this.fragmentShader=e.fragmentShader,this.vertexShader=e.vertexShader,this.uniforms=Hr(e.uniforms),this.uniformsGroups=qg(e.uniformsGroups),this.defines=Object.assign({},e.defines),this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.fog=e.fog,this.lights=e.lights,this.clipping=e.clipping,this.extensions=Object.assign({},e.extensions),this.glslVersion=e.glslVersion,this}toJSON(e){const t=super.toJSON(e);t.glslVersion=this.glslVersion,t.uniforms={};for(const s in this.uniforms){const a=this.uniforms[s].value;a&&a.isTexture?t.uniforms[s]={type:"t",value:a.toJSON(e).uuid}:a&&a.isColor?t.uniforms[s]={type:"c",value:a.getHex()}:a&&a.isVector2?t.uniforms[s]={type:"v2",value:a.toArray()}:a&&a.isVector3?t.uniforms[s]={type:"v3",value:a.toArray()}:a&&a.isVector4?t.uniforms[s]={type:"v4",value:a.toArray()}:a&&a.isMatrix3?t.uniforms[s]={type:"m3",value:a.toArray()}:a&&a.isMatrix4?t.uniforms[s]={type:"m4",value:a.toArray()}:t.uniforms[s]={value:a}}Object.keys(this.defines).length>0&&(t.defines=this.defines),t.vertexShader=this.vertexShader,t.fragmentShader=this.fragmentShader,t.lights=this.lights,t.clipping=this.clipping;const n={};for(const s in this.extensions)this.extensions[s]===!0&&(n[s]=!0);return Object.keys(n).length>0&&(t.extensions=n),t}}class Xf extends Jt{constructor(){super(),this.isCamera=!0,this.type="Camera",this.matrixWorldInverse=new Ot,this.projectionMatrix=new Ot,this.projectionMatrixInverse=new Ot,this.coordinateSystem=Oi}copy(e,t){return super.copy(e,t),this.matrixWorldInverse.copy(e.matrixWorldInverse),this.projectionMatrix.copy(e.projectionMatrix),this.projectionMatrixInverse.copy(e.projectionMatrixInverse),this.coordinateSystem=e.coordinateSystem,this}getWorldDirection(e){return super.getWorldDirection(e).negate()}updateMatrixWorld(e){super.updateMatrixWorld(e),this.matrixWorldInverse.copy(this.matrixWorld).invert()}updateWorldMatrix(e,t){super.updateWorldMatrix(e,t),this.matrixWorldInverse.copy(this.matrixWorld).invert()}clone(){return new this.constructor().copy(this)}}const ts=new k,kh=new qe,Hh=new qe;class Sn extends Xf{constructor(e=50,t=1,n=.1,s=2e3){super(),this.isPerspectiveCamera=!0,this.type="PerspectiveCamera",this.fov=e,this.zoom=1,this.near=n,this.far=s,this.focus=10,this.aspect=t,this.view=null,this.filmGauge=35,this.filmOffset=0,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.fov=e.fov,this.zoom=e.zoom,this.near=e.near,this.far=e.far,this.focus=e.focus,this.aspect=e.aspect,this.view=e.view===null?null:Object.assign({},e.view),this.filmGauge=e.filmGauge,this.filmOffset=e.filmOffset,this}setFocalLength(e){const t=.5*this.getFilmHeight()/e;this.fov=Ra*2*Math.atan(t),this.updateProjectionMatrix()}getFocalLength(){const e=Math.tan(Pr*.5*this.fov);return .5*this.getFilmHeight()/e}getEffectiveFOV(){return Ra*2*Math.atan(Math.tan(Pr*.5*this.fov)/this.zoom)}getFilmWidth(){return this.filmGauge*Math.min(this.aspect,1)}getFilmHeight(){return this.filmGauge/Math.max(this.aspect,1)}getViewBounds(e,t,n){ts.set(-1,-1,.5).applyMatrix4(this.projectionMatrixInverse),t.set(ts.x,ts.y).multiplyScalar(-e/ts.z),ts.set(1,1,.5).applyMatrix4(this.projectionMatrixInverse),n.set(ts.x,ts.y).multiplyScalar(-e/ts.z)}getViewSize(e,t){return this.getViewBounds(e,kh,Hh),t.subVectors(Hh,kh)}setViewOffset(e,t,n,s,r,a){this.aspect=e/t,this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=n,this.view.offsetY=s,this.view.width=r,this.view.height=a,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const e=this.near;let t=e*Math.tan(Pr*.5*this.fov)/this.zoom,n=2*t,s=this.aspect*n,r=-.5*s;const a=this.view;if(this.view!==null&&this.view.enabled){const l=a.fullWidth,c=a.fullHeight;r+=a.offsetX*s/l,t-=a.offsetY*n/c,s*=a.width/l,n*=a.height/c}const o=this.filmOffset;o!==0&&(r+=e*o/this.getFilmWidth()),this.projectionMatrix.makePerspective(r,r+s,t,t-n,e,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){const t=super.toJSON(e);return t.object.fov=this.fov,t.object.zoom=this.zoom,t.object.near=this.near,t.object.far=this.far,t.object.focus=this.focus,t.object.aspect=this.aspect,this.view!==null&&(t.object.view=Object.assign({},this.view)),t.object.filmGauge=this.filmGauge,t.object.filmOffset=this.filmOffset,t}}const mr=-90,gr=1;class Kg extends Jt{constructor(e,t,n){super(),this.type="CubeCamera",this.renderTarget=n,this.coordinateSystem=null,this.activeMipmapLevel=0;const s=new Sn(mr,gr,e,t);s.layers=this.layers,this.add(s);const r=new Sn(mr,gr,e,t);r.layers=this.layers,this.add(r);const a=new Sn(mr,gr,e,t);a.layers=this.layers,this.add(a);const o=new Sn(mr,gr,e,t);o.layers=this.layers,this.add(o);const l=new Sn(mr,gr,e,t);l.layers=this.layers,this.add(l);const c=new Sn(mr,gr,e,t);c.layers=this.layers,this.add(c)}updateCoordinateSystem(){const e=this.coordinateSystem,t=this.children.concat(),[n,s,r,a,o,l]=t;for(const c of t)this.remove(c);if(e===Oi)n.up.set(0,1,0),n.lookAt(1,0,0),s.up.set(0,1,0),s.lookAt(-1,0,0),r.up.set(0,0,-1),r.lookAt(0,1,0),a.up.set(0,0,1),a.lookAt(0,-1,0),o.up.set(0,1,0),o.lookAt(0,0,1),l.up.set(0,1,0),l.lookAt(0,0,-1);else if(e===Go)n.up.set(0,-1,0),n.lookAt(-1,0,0),s.up.set(0,-1,0),s.lookAt(1,0,0),r.up.set(0,0,1),r.lookAt(0,1,0),a.up.set(0,0,-1),a.lookAt(0,-1,0),o.up.set(0,-1,0),o.lookAt(0,0,1),l.up.set(0,-1,0),l.lookAt(0,0,-1);else throw new Error("THREE.CubeCamera.updateCoordinateSystem(): Invalid coordinate system: "+e);for(const c of t)this.add(c),c.updateMatrixWorld()}update(e,t){this.parent===null&&this.updateMatrixWorld();const{renderTarget:n,activeMipmapLevel:s}=this;this.coordinateSystem!==e.coordinateSystem&&(this.coordinateSystem=e.coordinateSystem,this.updateCoordinateSystem());const[r,a,o,l,c,u]=this.children,h=e.getRenderTarget(),d=e.getActiveCubeFace(),f=e.getActiveMipmapLevel(),g=e.xr.enabled;e.xr.enabled=!1;const v=n.texture.generateMipmaps;n.texture.generateMipmaps=!1,e.setRenderTarget(n,0,s),e.render(t,r),e.setRenderTarget(n,1,s),e.render(t,a),e.setRenderTarget(n,2,s),e.render(t,o),e.setRenderTarget(n,3,s),e.render(t,l),e.setRenderTarget(n,4,s),e.render(t,c),n.texture.generateMipmaps=v,e.setRenderTarget(n,5,s),e.render(t,u),e.setRenderTarget(h,d,f),e.xr.enabled=g,n.texture.needsPMREMUpdate=!0}}class qf extends Ln{constructor(e,t,n,s,r,a,o,l,c,u){e=e!==void 0?e:[],t=t!==void 0?t:Or,super(e,t,n,s,r,a,o,l,c,u),this.isCubeTexture=!0,this.flipY=!1}get images(){return this.image}set images(e){this.image=e}}class Zg extends Bs{constructor(e=1,t={}){super(e,e,t),this.isWebGLCubeRenderTarget=!0;const n={width:e,height:e,depth:1},s=[n,n,n,n,n,n];this.texture=new qf(s,t.mapping,t.wrapS,t.wrapT,t.magFilter,t.minFilter,t.format,t.type,t.anisotropy,t.colorSpace),this.texture.isRenderTargetTexture=!0,this.texture.generateMipmaps=t.generateMipmaps!==void 0?t.generateMipmaps:!1,this.texture.minFilter=t.minFilter!==void 0?t.minFilter:ai}fromEquirectangularTexture(e,t){this.texture.type=t.type,this.texture.colorSpace=t.colorSpace,this.texture.generateMipmaps=t.generateMipmaps,this.texture.minFilter=t.minFilter,this.texture.magFilter=t.magFilter;const n={uniforms:{tEquirect:{value:null}},vertexShader:`

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
			`},s=new Bi(5,5,5),r=new us({name:"CubemapFromEquirect",uniforms:Hr(n.uniforms),vertexShader:n.vertexShader,fragmentShader:n.fragmentShader,side:In,blending:os});r.uniforms.tEquirect.value=t;const a=new gn(s,r),o=t.minFilter;return t.minFilter===Is&&(t.minFilter=ai),new Kg(1,10,this).update(e,a),t.minFilter=o,a.geometry.dispose(),a.material.dispose(),this}clear(e,t,n,s){const r=e.getRenderTarget();for(let a=0;a<6;a++)e.setRenderTarget(this,a),e.clear(t,n,s);e.setRenderTarget(r)}}const jl=new k,Jg=new k,Qg=new rt;class is{constructor(e=new k(1,0,0),t=0){this.isPlane=!0,this.normal=e,this.constant=t}set(e,t){return this.normal.copy(e),this.constant=t,this}setComponents(e,t,n,s){return this.normal.set(e,t,n),this.constant=s,this}setFromNormalAndCoplanarPoint(e,t){return this.normal.copy(e),this.constant=-t.dot(this.normal),this}setFromCoplanarPoints(e,t,n){const s=jl.subVectors(n,t).cross(Jg.subVectors(e,t)).normalize();return this.setFromNormalAndCoplanarPoint(s,e),this}copy(e){return this.normal.copy(e.normal),this.constant=e.constant,this}normalize(){const e=1/this.normal.length();return this.normal.multiplyScalar(e),this.constant*=e,this}negate(){return this.constant*=-1,this.normal.negate(),this}distanceToPoint(e){return this.normal.dot(e)+this.constant}distanceToSphere(e){return this.distanceToPoint(e.center)-e.radius}projectPoint(e,t){return t.copy(e).addScaledVector(this.normal,-this.distanceToPoint(e))}intersectLine(e,t){const n=e.delta(jl),s=this.normal.dot(n);if(s===0)return this.distanceToPoint(e.start)===0?t.copy(e.start):null;const r=-(e.start.dot(this.normal)+this.constant)/s;return r<0||r>1?null:t.copy(e.start).addScaledVector(n,r)}intersectsLine(e){const t=this.distanceToPoint(e.start),n=this.distanceToPoint(e.end);return t<0&&n>0||n<0&&t>0}intersectsBox(e){return e.intersectsPlane(this)}intersectsSphere(e){return e.intersectsPlane(this)}coplanarPoint(e){return e.copy(this.normal).multiplyScalar(-this.constant)}applyMatrix4(e,t){const n=t||Qg.getNormalMatrix(e),s=this.coplanarPoint(jl).applyMatrix4(e),r=this.normal.applyMatrix3(n).normalize();return this.constant=-s.dot(r),this}translate(e){return this.constant-=e.dot(this.normal),this}equals(e){return e.normal.equals(this.normal)&&e.constant===this.constant}clone(){return new this.constructor().copy(this)}}const bs=new Na,ho=new k;class Mu{constructor(e=new is,t=new is,n=new is,s=new is,r=new is,a=new is){this.planes=[e,t,n,s,r,a]}set(e,t,n,s,r,a){const o=this.planes;return o[0].copy(e),o[1].copy(t),o[2].copy(n),o[3].copy(s),o[4].copy(r),o[5].copy(a),this}copy(e){const t=this.planes;for(let n=0;n<6;n++)t[n].copy(e.planes[n]);return this}setFromProjectionMatrix(e,t=Oi){const n=this.planes,s=e.elements,r=s[0],a=s[1],o=s[2],l=s[3],c=s[4],u=s[5],h=s[6],d=s[7],f=s[8],g=s[9],v=s[10],m=s[11],p=s[12],S=s[13],y=s[14],w=s[15];if(n[0].setComponents(l-r,d-c,m-f,w-p).normalize(),n[1].setComponents(l+r,d+c,m+f,w+p).normalize(),n[2].setComponents(l+a,d+u,m+g,w+S).normalize(),n[3].setComponents(l-a,d-u,m-g,w-S).normalize(),n[4].setComponents(l-o,d-h,m-v,w-y).normalize(),t===Oi)n[5].setComponents(l+o,d+h,m+v,w+y).normalize();else if(t===Go)n[5].setComponents(o,h,v,y).normalize();else throw new Error("THREE.Frustum.setFromProjectionMatrix(): Invalid coordinate system: "+t);return this}intersectsObject(e){if(e.boundingSphere!==void 0)e.boundingSphere===null&&e.computeBoundingSphere(),bs.copy(e.boundingSphere).applyMatrix4(e.matrixWorld);else{const t=e.geometry;t.boundingSphere===null&&t.computeBoundingSphere(),bs.copy(t.boundingSphere).applyMatrix4(e.matrixWorld)}return this.intersectsSphere(bs)}intersectsSprite(e){return bs.center.set(0,0,0),bs.radius=.7071067811865476,bs.applyMatrix4(e.matrixWorld),this.intersectsSphere(bs)}intersectsSphere(e){const t=this.planes,n=e.center,s=-e.radius;for(let r=0;r<6;r++)if(t[r].distanceToPoint(n)<s)return!1;return!0}intersectsBox(e){const t=this.planes;for(let n=0;n<6;n++){const s=t[n];if(ho.x=s.normal.x>0?e.max.x:e.min.x,ho.y=s.normal.y>0?e.max.y:e.min.y,ho.z=s.normal.z>0?e.max.z:e.min.z,s.distanceToPoint(ho)<0)return!1}return!0}containsPoint(e){const t=this.planes;for(let n=0;n<6;n++)if(t[n].distanceToPoint(e)<0)return!1;return!0}clone(){return new this.constructor().copy(this)}}function Yf(){let i=null,e=!1,t=null,n=null;function s(r,a){t(r,a),n=i.requestAnimationFrame(s)}return{start:function(){e!==!0&&t!==null&&(n=i.requestAnimationFrame(s),e=!0)},stop:function(){i.cancelAnimationFrame(n),e=!1},setAnimationLoop:function(r){t=r},setContext:function(r){i=r}}}function e_(i){const e=new WeakMap;function t(o,l){const c=o.array,u=o.usage,h=c.byteLength,d=i.createBuffer();i.bindBuffer(l,d),i.bufferData(l,c,u),o.onUploadCallback();let f;if(c instanceof Float32Array)f=i.FLOAT;else if(c instanceof Uint16Array)o.isFloat16BufferAttribute?f=i.HALF_FLOAT:f=i.UNSIGNED_SHORT;else if(c instanceof Int16Array)f=i.SHORT;else if(c instanceof Uint32Array)f=i.UNSIGNED_INT;else if(c instanceof Int32Array)f=i.INT;else if(c instanceof Int8Array)f=i.BYTE;else if(c instanceof Uint8Array)f=i.UNSIGNED_BYTE;else if(c instanceof Uint8ClampedArray)f=i.UNSIGNED_BYTE;else throw new Error("THREE.WebGLAttributes: Unsupported buffer data format: "+c);return{buffer:d,type:f,bytesPerElement:c.BYTES_PER_ELEMENT,version:o.version,size:h}}function n(o,l,c){const u=l.array,h=l._updateRange,d=l.updateRanges;if(i.bindBuffer(c,o),h.count===-1&&d.length===0&&i.bufferSubData(c,0,u),d.length!==0){for(let f=0,g=d.length;f<g;f++){const v=d[f];i.bufferSubData(c,v.start*u.BYTES_PER_ELEMENT,u,v.start,v.count)}l.clearUpdateRanges()}h.count!==-1&&(i.bufferSubData(c,h.offset*u.BYTES_PER_ELEMENT,u,h.offset,h.count),h.count=-1),l.onUploadCallback()}function s(o){return o.isInterleavedBufferAttribute&&(o=o.data),e.get(o)}function r(o){o.isInterleavedBufferAttribute&&(o=o.data);const l=e.get(o);l&&(i.deleteBuffer(l.buffer),e.delete(o))}function a(o,l){if(o.isInterleavedBufferAttribute&&(o=o.data),o.isGLBufferAttribute){const u=e.get(o);(!u||u.version<o.version)&&e.set(o,{buffer:o.buffer,type:o.type,bytesPerElement:o.elementSize,version:o.version});return}const c=e.get(o);if(c===void 0)e.set(o,t(o,l));else if(c.version<o.version){if(c.size!==o.array.byteLength)throw new Error("THREE.WebGLAttributes: The size of the buffer attribute's array buffer does not match the original size. Resizing buffer attributes is not supported.");n(c.buffer,o,l),c.version=o.version}}return{get:s,remove:r,update:a}}class Oa extends Xt{constructor(e=1,t=1,n=1,s=1){super(),this.type="PlaneGeometry",this.parameters={width:e,height:t,widthSegments:n,heightSegments:s};const r=e/2,a=t/2,o=Math.floor(n),l=Math.floor(s),c=o+1,u=l+1,h=e/o,d=t/l,f=[],g=[],v=[],m=[];for(let p=0;p<u;p++){const S=p*d-a;for(let y=0;y<c;y++){const w=y*h-r;g.push(w,-S,0),v.push(0,0,1),m.push(y/o),m.push(1-p/l)}}for(let p=0;p<l;p++)for(let S=0;S<o;S++){const y=S+c*p,w=S+c*(p+1),O=S+1+c*(p+1),A=S+1+c*p;f.push(y,w,A),f.push(w,O,A)}this.setIndex(f),this.setAttribute("position",new qt(g,3)),this.setAttribute("normal",new qt(v,3)),this.setAttribute("uv",new qt(m,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Oa(e.width,e.height,e.widthSegments,e.heightSegments)}}var t_=`#ifdef USE_ALPHAHASH
	if ( diffuseColor.a < getAlphaHashThreshold( vPosition ) ) discard;
#endif`,n_=`#ifdef USE_ALPHAHASH
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
#endif`,i_=`#ifdef USE_ALPHAMAP
	diffuseColor.a *= texture2D( alphaMap, vAlphaMapUv ).g;
#endif`,s_=`#ifdef USE_ALPHAMAP
	uniform sampler2D alphaMap;
#endif`,r_=`#ifdef USE_ALPHATEST
	#ifdef ALPHA_TO_COVERAGE
	diffuseColor.a = smoothstep( alphaTest, alphaTest + fwidth( diffuseColor.a ), diffuseColor.a );
	if ( diffuseColor.a == 0.0 ) discard;
	#else
	if ( diffuseColor.a < alphaTest ) discard;
	#endif
#endif`,a_=`#ifdef USE_ALPHATEST
	uniform float alphaTest;
#endif`,o_=`#ifdef USE_AOMAP
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
#endif`,l_=`#ifdef USE_AOMAP
	uniform sampler2D aoMap;
	uniform float aoMapIntensity;
#endif`,c_=`#ifdef USE_BATCHING
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
#endif`,u_=`#ifdef USE_BATCHING
	mat4 batchingMatrix = getBatchingMatrix( getIndirectIndex( gl_DrawID ) );
#endif`,h_=`vec3 transformed = vec3( position );
#ifdef USE_ALPHAHASH
	vPosition = vec3( position );
#endif`,d_=`vec3 objectNormal = vec3( normal );
#ifdef USE_TANGENT
	vec3 objectTangent = vec3( tangent.xyz );
#endif`,f_=`float G_BlinnPhong_Implicit( ) {
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
} // validated`,p_=`#ifdef USE_IRIDESCENCE
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
#endif`,m_=`#ifdef USE_BUMPMAP
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
#endif`,g_=`#if NUM_CLIPPING_PLANES > 0
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
#endif`,__=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
	uniform vec4 clippingPlanes[ NUM_CLIPPING_PLANES ];
#endif`,v_=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
#endif`,x_=`#if NUM_CLIPPING_PLANES > 0
	vClipPosition = - mvPosition.xyz;
#endif`,y_=`#if defined( USE_COLOR_ALPHA )
	diffuseColor *= vColor;
#elif defined( USE_COLOR )
	diffuseColor.rgb *= vColor;
#endif`,M_=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR )
	varying vec3 vColor;
#endif`,S_=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR ) || defined( USE_INSTANCING_COLOR ) || defined( USE_BATCHING_COLOR )
	varying vec3 vColor;
#endif`,b_=`#if defined( USE_COLOR_ALPHA )
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
#endif`,E_=`#define PI 3.141592653589793
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
} // validated`,w_=`#ifdef ENVMAP_TYPE_CUBE_UV
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
#endif`,T_=`vec3 transformedNormal = objectNormal;
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
#endif`,A_=`#ifdef USE_DISPLACEMENTMAP
	uniform sampler2D displacementMap;
	uniform float displacementScale;
	uniform float displacementBias;
#endif`,C_=`#ifdef USE_DISPLACEMENTMAP
	transformed += normalize( objectNormal ) * ( texture2D( displacementMap, vDisplacementMapUv ).x * displacementScale + displacementBias );
#endif`,R_=`#ifdef USE_EMISSIVEMAP
	vec4 emissiveColor = texture2D( emissiveMap, vEmissiveMapUv );
	totalEmissiveRadiance *= emissiveColor.rgb;
#endif`,P_=`#ifdef USE_EMISSIVEMAP
	uniform sampler2D emissiveMap;
#endif`,L_="gl_FragColor = linearToOutputTexel( gl_FragColor );",D_=`
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
}`,I_=`#ifdef USE_ENVMAP
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
#endif`,U_=`#ifdef USE_ENVMAP
	uniform float envMapIntensity;
	uniform float flipEnvMap;
	uniform mat3 envMapRotation;
	#ifdef ENVMAP_TYPE_CUBE
		uniform samplerCube envMap;
	#else
		uniform sampler2D envMap;
	#endif
	
#endif`,N_=`#ifdef USE_ENVMAP
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
#endif`,F_=`#ifdef USE_ENVMAP
	#if defined( USE_BUMPMAP ) || defined( USE_NORMALMAP ) || defined( PHONG ) || defined( LAMBERT )
		#define ENV_WORLDPOS
	#endif
	#ifdef ENV_WORLDPOS
		
		varying vec3 vWorldPosition;
	#else
		varying vec3 vReflect;
		uniform float refractionRatio;
	#endif
#endif`,O_=`#ifdef USE_ENVMAP
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
#endif`,B_=`#ifdef USE_FOG
	vFogDepth = - mvPosition.z;
#endif`,z_=`#ifdef USE_FOG
	varying float vFogDepth;
#endif`,k_=`#ifdef USE_FOG
	#ifdef FOG_EXP2
		float fogFactor = 1.0 - exp( - fogDensity * fogDensity * vFogDepth * vFogDepth );
	#else
		float fogFactor = smoothstep( fogNear, fogFar, vFogDepth );
	#endif
	gl_FragColor.rgb = mix( gl_FragColor.rgb, fogColor, fogFactor );
#endif`,H_=`#ifdef USE_FOG
	uniform vec3 fogColor;
	varying float vFogDepth;
	#ifdef FOG_EXP2
		uniform float fogDensity;
	#else
		uniform float fogNear;
		uniform float fogFar;
	#endif
#endif`,V_=`#ifdef USE_GRADIENTMAP
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
}`,G_=`#ifdef USE_LIGHTMAP
	uniform sampler2D lightMap;
	uniform float lightMapIntensity;
#endif`,W_=`LambertMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularStrength = specularStrength;`,X_=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Lambert`,q_=`uniform bool receiveShadow;
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
#endif`,Y_=`#ifdef USE_ENVMAP
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
#endif`,$_=`ToonMaterial material;
material.diffuseColor = diffuseColor.rgb;`,j_=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Toon`,K_=`BlinnPhongMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularColor = specular;
material.specularShininess = shininess;
material.specularStrength = specularStrength;`,Z_=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_BlinnPhong`,J_=`PhysicalMaterial material;
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
#endif`,Q_=`struct PhysicalMaterial {
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
}`,e0=`
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
#endif`,t0=`#if defined( RE_IndirectDiffuse )
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
#endif`,n0=`#if defined( RE_IndirectDiffuse )
	RE_IndirectDiffuse( irradiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif
#if defined( RE_IndirectSpecular )
	RE_IndirectSpecular( radiance, iblIrradiance, clearcoatRadiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif`,i0=`#if defined( USE_LOGDEPTHBUF )
	gl_FragDepth = vIsPerspective == 0.0 ? gl_FragCoord.z : log2( vFragDepth ) * logDepthBufFC * 0.5;
#endif`,s0=`#if defined( USE_LOGDEPTHBUF )
	uniform float logDepthBufFC;
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,r0=`#ifdef USE_LOGDEPTHBUF
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,a0=`#ifdef USE_LOGDEPTHBUF
	vFragDepth = 1.0 + gl_Position.w;
	vIsPerspective = float( isPerspectiveMatrix( projectionMatrix ) );
#endif`,o0=`#ifdef USE_MAP
	vec4 sampledDiffuseColor = texture2D( map, vMapUv );
	#ifdef DECODE_VIDEO_TEXTURE
		sampledDiffuseColor = vec4( mix( pow( sampledDiffuseColor.rgb * 0.9478672986 + vec3( 0.0521327014 ), vec3( 2.4 ) ), sampledDiffuseColor.rgb * 0.0773993808, vec3( lessThanEqual( sampledDiffuseColor.rgb, vec3( 0.04045 ) ) ) ), sampledDiffuseColor.w );
	
	#endif
	diffuseColor *= sampledDiffuseColor;
#endif`,l0=`#ifdef USE_MAP
	uniform sampler2D map;
#endif`,c0=`#if defined( USE_MAP ) || defined( USE_ALPHAMAP )
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
#endif`,u0=`#if defined( USE_POINTS_UV )
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
#endif`,h0=`float metalnessFactor = metalness;
#ifdef USE_METALNESSMAP
	vec4 texelMetalness = texture2D( metalnessMap, vMetalnessMapUv );
	metalnessFactor *= texelMetalness.b;
#endif`,d0=`#ifdef USE_METALNESSMAP
	uniform sampler2D metalnessMap;
#endif`,f0=`#ifdef USE_INSTANCING_MORPH
	float morphTargetInfluences[ MORPHTARGETS_COUNT ];
	float morphTargetBaseInfluence = texelFetch( morphTexture, ivec2( 0, gl_InstanceID ), 0 ).r;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		morphTargetInfluences[i] =  texelFetch( morphTexture, ivec2( i + 1, gl_InstanceID ), 0 ).r;
	}
#endif`,p0=`#if defined( USE_MORPHCOLORS )
	vColor *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		#if defined( USE_COLOR_ALPHA )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ) * morphTargetInfluences[ i ];
		#elif defined( USE_COLOR )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ).rgb * morphTargetInfluences[ i ];
		#endif
	}
#endif`,m0=`#ifdef USE_MORPHNORMALS
	objectNormal *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) objectNormal += getMorph( gl_VertexID, i, 1 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,g0=`#ifdef USE_MORPHTARGETS
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
#endif`,_0=`#ifdef USE_MORPHTARGETS
	transformed *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) transformed += getMorph( gl_VertexID, i, 0 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,v0=`float faceDirection = gl_FrontFacing ? 1.0 : - 1.0;
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
vec3 nonPerturbedNormal = normal;`,x0=`#ifdef USE_NORMALMAP_OBJECTSPACE
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
#endif`,y0=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,M0=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,S0=`#ifndef FLAT_SHADED
	vNormal = normalize( transformedNormal );
	#ifdef USE_TANGENT
		vTangent = normalize( transformedTangent );
		vBitangent = normalize( cross( vNormal, vTangent ) * tangent.w );
	#endif
#endif`,b0=`#ifdef USE_NORMALMAP
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
#endif`,E0=`#ifdef USE_CLEARCOAT
	vec3 clearcoatNormal = nonPerturbedNormal;
#endif`,w0=`#ifdef USE_CLEARCOAT_NORMALMAP
	vec3 clearcoatMapN = texture2D( clearcoatNormalMap, vClearcoatNormalMapUv ).xyz * 2.0 - 1.0;
	clearcoatMapN.xy *= clearcoatNormalScale;
	clearcoatNormal = normalize( tbn2 * clearcoatMapN );
#endif`,T0=`#ifdef USE_CLEARCOATMAP
	uniform sampler2D clearcoatMap;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	uniform sampler2D clearcoatNormalMap;
	uniform vec2 clearcoatNormalScale;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	uniform sampler2D clearcoatRoughnessMap;
#endif`,A0=`#ifdef USE_IRIDESCENCEMAP
	uniform sampler2D iridescenceMap;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	uniform sampler2D iridescenceThicknessMap;
#endif`,C0=`#ifdef OPAQUE
diffuseColor.a = 1.0;
#endif
#ifdef USE_TRANSMISSION
diffuseColor.a *= material.transmissionAlpha;
#endif
gl_FragColor = vec4( outgoingLight, diffuseColor.a );`,R0=`vec3 packNormalToRGB( const in vec3 normal ) {
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
}`,P0=`#ifdef PREMULTIPLIED_ALPHA
	gl_FragColor.rgb *= gl_FragColor.a;
#endif`,L0=`vec4 mvPosition = vec4( transformed, 1.0 );
#ifdef USE_BATCHING
	mvPosition = batchingMatrix * mvPosition;
#endif
#ifdef USE_INSTANCING
	mvPosition = instanceMatrix * mvPosition;
#endif
mvPosition = modelViewMatrix * mvPosition;
gl_Position = projectionMatrix * mvPosition;`,D0=`#ifdef DITHERING
	gl_FragColor.rgb = dithering( gl_FragColor.rgb );
#endif`,I0=`#ifdef DITHERING
	vec3 dithering( vec3 color ) {
		float grid_position = rand( gl_FragCoord.xy );
		vec3 dither_shift_RGB = vec3( 0.25 / 255.0, -0.25 / 255.0, 0.25 / 255.0 );
		dither_shift_RGB = mix( 2.0 * dither_shift_RGB, -2.0 * dither_shift_RGB, grid_position );
		return color + dither_shift_RGB;
	}
#endif`,U0=`float roughnessFactor = roughness;
#ifdef USE_ROUGHNESSMAP
	vec4 texelRoughness = texture2D( roughnessMap, vRoughnessMapUv );
	roughnessFactor *= texelRoughness.g;
#endif`,N0=`#ifdef USE_ROUGHNESSMAP
	uniform sampler2D roughnessMap;
#endif`,F0=`#if NUM_SPOT_LIGHT_COORDS > 0
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
#endif`,O0=`#if NUM_SPOT_LIGHT_COORDS > 0
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
#endif`,B0=`#if ( defined( USE_SHADOWMAP ) && ( NUM_DIR_LIGHT_SHADOWS > 0 || NUM_POINT_LIGHT_SHADOWS > 0 ) ) || ( NUM_SPOT_LIGHT_COORDS > 0 )
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
#endif`,z0=`float getShadowMask() {
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
}`,k0=`#ifdef USE_SKINNING
	mat4 boneMatX = getBoneMatrix( skinIndex.x );
	mat4 boneMatY = getBoneMatrix( skinIndex.y );
	mat4 boneMatZ = getBoneMatrix( skinIndex.z );
	mat4 boneMatW = getBoneMatrix( skinIndex.w );
#endif`,H0=`#ifdef USE_SKINNING
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
#endif`,V0=`#ifdef USE_SKINNING
	vec4 skinVertex = bindMatrix * vec4( transformed, 1.0 );
	vec4 skinned = vec4( 0.0 );
	skinned += boneMatX * skinVertex * skinWeight.x;
	skinned += boneMatY * skinVertex * skinWeight.y;
	skinned += boneMatZ * skinVertex * skinWeight.z;
	skinned += boneMatW * skinVertex * skinWeight.w;
	transformed = ( bindMatrixInverse * skinned ).xyz;
#endif`,G0=`#ifdef USE_SKINNING
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
#endif`,W0=`float specularStrength;
#ifdef USE_SPECULARMAP
	vec4 texelSpecular = texture2D( specularMap, vSpecularMapUv );
	specularStrength = texelSpecular.r;
#else
	specularStrength = 1.0;
#endif`,X0=`#ifdef USE_SPECULARMAP
	uniform sampler2D specularMap;
#endif`,q0=`#if defined( TONE_MAPPING )
	gl_FragColor.rgb = toneMapping( gl_FragColor.rgb );
#endif`,Y0=`#ifndef saturate
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
vec3 CustomToneMapping( vec3 color ) { return color; }`,$0=`#ifdef USE_TRANSMISSION
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
#endif`,j0=`#ifdef USE_TRANSMISSION
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
#endif`,K0=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
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
#endif`,Z0=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
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
#endif`,J0=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
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
#endif`,Q0=`#if defined( USE_ENVMAP ) || defined( DISTANCE ) || defined ( USE_SHADOWMAP ) || defined ( USE_TRANSMISSION ) || NUM_SPOT_LIGHT_COORDS > 0
	vec4 worldPosition = vec4( transformed, 1.0 );
	#ifdef USE_BATCHING
		worldPosition = batchingMatrix * worldPosition;
	#endif
	#ifdef USE_INSTANCING
		worldPosition = instanceMatrix * worldPosition;
	#endif
	worldPosition = modelMatrix * worldPosition;
#endif`;const ev=`varying vec2 vUv;
uniform mat3 uvTransform;
void main() {
	vUv = ( uvTransform * vec3( uv, 1 ) ).xy;
	gl_Position = vec4( position.xy, 1.0, 1.0 );
}`,tv=`uniform sampler2D t2D;
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
}`,nv=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,iv=`#ifdef ENVMAP_TYPE_CUBE
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
}`,sv=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,rv=`uniform samplerCube tCube;
uniform float tFlip;
uniform float opacity;
varying vec3 vWorldDirection;
void main() {
	vec4 texColor = textureCube( tCube, vec3( tFlip * vWorldDirection.x, vWorldDirection.yz ) );
	gl_FragColor = texColor;
	gl_FragColor.a *= opacity;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,av=`#include <common>
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
}`,ov=`#if DEPTH_PACKING == 3200
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
}`,lv=`#define DISTANCE
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
}`,cv=`#define DISTANCE
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
}`,uv=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
}`,hv=`uniform sampler2D tEquirect;
varying vec3 vWorldDirection;
#include <common>
void main() {
	vec3 direction = normalize( vWorldDirection );
	vec2 sampleUV = equirectUv( direction );
	gl_FragColor = texture2D( tEquirect, sampleUV );
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,dv=`uniform float scale;
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
}`,fv=`uniform vec3 diffuse;
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
}`,pv=`#include <common>
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
}`,mv=`uniform vec3 diffuse;
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
}`,gv=`#define LAMBERT
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
}`,_v=`#define LAMBERT
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
}`,vv=`#define MATCAP
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
}`,xv=`#define MATCAP
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
}`,yv=`#define NORMAL
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
}`,Mv=`#define NORMAL
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
}`,Sv=`#define PHONG
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
}`,bv=`#define PHONG
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
}`,Ev=`#define STANDARD
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
}`,wv=`#define STANDARD
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
}`,Tv=`#define TOON
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
}`,Av=`#define TOON
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
}`,Cv=`uniform float size;
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
}`,Rv=`uniform vec3 diffuse;
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
}`,Pv=`#include <common>
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
}`,Lv=`uniform vec3 color;
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
}`,Dv=`uniform float rotation;
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
}`,Iv=`uniform vec3 diffuse;
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
}`,st={alphahash_fragment:t_,alphahash_pars_fragment:n_,alphamap_fragment:i_,alphamap_pars_fragment:s_,alphatest_fragment:r_,alphatest_pars_fragment:a_,aomap_fragment:o_,aomap_pars_fragment:l_,batching_pars_vertex:c_,batching_vertex:u_,begin_vertex:h_,beginnormal_vertex:d_,bsdfs:f_,iridescence_fragment:p_,bumpmap_pars_fragment:m_,clipping_planes_fragment:g_,clipping_planes_pars_fragment:__,clipping_planes_pars_vertex:v_,clipping_planes_vertex:x_,color_fragment:y_,color_pars_fragment:M_,color_pars_vertex:S_,color_vertex:b_,common:E_,cube_uv_reflection_fragment:w_,defaultnormal_vertex:T_,displacementmap_pars_vertex:A_,displacementmap_vertex:C_,emissivemap_fragment:R_,emissivemap_pars_fragment:P_,colorspace_fragment:L_,colorspace_pars_fragment:D_,envmap_fragment:I_,envmap_common_pars_fragment:U_,envmap_pars_fragment:N_,envmap_pars_vertex:F_,envmap_physical_pars_fragment:Y_,envmap_vertex:O_,fog_vertex:B_,fog_pars_vertex:z_,fog_fragment:k_,fog_pars_fragment:H_,gradientmap_pars_fragment:V_,lightmap_pars_fragment:G_,lights_lambert_fragment:W_,lights_lambert_pars_fragment:X_,lights_pars_begin:q_,lights_toon_fragment:$_,lights_toon_pars_fragment:j_,lights_phong_fragment:K_,lights_phong_pars_fragment:Z_,lights_physical_fragment:J_,lights_physical_pars_fragment:Q_,lights_fragment_begin:e0,lights_fragment_maps:t0,lights_fragment_end:n0,logdepthbuf_fragment:i0,logdepthbuf_pars_fragment:s0,logdepthbuf_pars_vertex:r0,logdepthbuf_vertex:a0,map_fragment:o0,map_pars_fragment:l0,map_particle_fragment:c0,map_particle_pars_fragment:u0,metalnessmap_fragment:h0,metalnessmap_pars_fragment:d0,morphinstance_vertex:f0,morphcolor_vertex:p0,morphnormal_vertex:m0,morphtarget_pars_vertex:g0,morphtarget_vertex:_0,normal_fragment_begin:v0,normal_fragment_maps:x0,normal_pars_fragment:y0,normal_pars_vertex:M0,normal_vertex:S0,normalmap_pars_fragment:b0,clearcoat_normal_fragment_begin:E0,clearcoat_normal_fragment_maps:w0,clearcoat_pars_fragment:T0,iridescence_pars_fragment:A0,opaque_fragment:C0,packing:R0,premultiplied_alpha_fragment:P0,project_vertex:L0,dithering_fragment:D0,dithering_pars_fragment:I0,roughnessmap_fragment:U0,roughnessmap_pars_fragment:N0,shadowmap_pars_fragment:F0,shadowmap_pars_vertex:O0,shadowmap_vertex:B0,shadowmask_pars_fragment:z0,skinbase_vertex:k0,skinning_pars_vertex:H0,skinning_vertex:V0,skinnormal_vertex:G0,specularmap_fragment:W0,specularmap_pars_fragment:X0,tonemapping_fragment:q0,tonemapping_pars_fragment:Y0,transmission_fragment:$0,transmission_pars_fragment:j0,uv_pars_fragment:K0,uv_pars_vertex:Z0,uv_vertex:J0,worldpos_vertex:Q0,background_vert:ev,background_frag:tv,backgroundCube_vert:nv,backgroundCube_frag:iv,cube_vert:sv,cube_frag:rv,depth_vert:av,depth_frag:ov,distanceRGBA_vert:lv,distanceRGBA_frag:cv,equirect_vert:uv,equirect_frag:hv,linedashed_vert:dv,linedashed_frag:fv,meshbasic_vert:pv,meshbasic_frag:mv,meshlambert_vert:gv,meshlambert_frag:_v,meshmatcap_vert:vv,meshmatcap_frag:xv,meshnormal_vert:yv,meshnormal_frag:Mv,meshphong_vert:Sv,meshphong_frag:bv,meshphysical_vert:Ev,meshphysical_frag:wv,meshtoon_vert:Tv,meshtoon_frag:Av,points_vert:Cv,points_frag:Rv,shadow_vert:Pv,shadow_frag:Lv,sprite_vert:Dv,sprite_frag:Iv},Ce={common:{diffuse:{value:new nt(16777215)},opacity:{value:1},map:{value:null},mapTransform:{value:new rt},alphaMap:{value:null},alphaMapTransform:{value:new rt},alphaTest:{value:0}},specularmap:{specularMap:{value:null},specularMapTransform:{value:new rt}},envmap:{envMap:{value:null},envMapRotation:{value:new rt},flipEnvMap:{value:-1},reflectivity:{value:1},ior:{value:1.5},refractionRatio:{value:.98}},aomap:{aoMap:{value:null},aoMapIntensity:{value:1},aoMapTransform:{value:new rt}},lightmap:{lightMap:{value:null},lightMapIntensity:{value:1},lightMapTransform:{value:new rt}},bumpmap:{bumpMap:{value:null},bumpMapTransform:{value:new rt},bumpScale:{value:1}},normalmap:{normalMap:{value:null},normalMapTransform:{value:new rt},normalScale:{value:new qe(1,1)}},displacementmap:{displacementMap:{value:null},displacementMapTransform:{value:new rt},displacementScale:{value:1},displacementBias:{value:0}},emissivemap:{emissiveMap:{value:null},emissiveMapTransform:{value:new rt}},metalnessmap:{metalnessMap:{value:null},metalnessMapTransform:{value:new rt}},roughnessmap:{roughnessMap:{value:null},roughnessMapTransform:{value:new rt}},gradientmap:{gradientMap:{value:null}},fog:{fogDensity:{value:25e-5},fogNear:{value:1},fogFar:{value:2e3},fogColor:{value:new nt(16777215)}},lights:{ambientLightColor:{value:[]},lightProbe:{value:[]},directionalLights:{value:[],properties:{direction:{},color:{}}},directionalLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},directionalShadowMap:{value:[]},directionalShadowMatrix:{value:[]},spotLights:{value:[],properties:{color:{},position:{},direction:{},distance:{},coneCos:{},penumbraCos:{},decay:{}}},spotLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},spotLightMap:{value:[]},spotShadowMap:{value:[]},spotLightMatrix:{value:[]},pointLights:{value:[],properties:{color:{},position:{},decay:{},distance:{}}},pointLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{},shadowCameraNear:{},shadowCameraFar:{}}},pointShadowMap:{value:[]},pointShadowMatrix:{value:[]},hemisphereLights:{value:[],properties:{direction:{},skyColor:{},groundColor:{}}},rectAreaLights:{value:[],properties:{color:{},position:{},width:{},height:{}}},ltc_1:{value:null},ltc_2:{value:null}},points:{diffuse:{value:new nt(16777215)},opacity:{value:1},size:{value:1},scale:{value:1},map:{value:null},alphaMap:{value:null},alphaMapTransform:{value:new rt},alphaTest:{value:0},uvTransform:{value:new rt}},sprite:{diffuse:{value:new nt(16777215)},opacity:{value:1},center:{value:new qe(.5,.5)},rotation:{value:0},map:{value:null},mapTransform:{value:new rt},alphaMap:{value:null},alphaMapTransform:{value:new rt},alphaTest:{value:0}}},yi={basic:{uniforms:Rn([Ce.common,Ce.specularmap,Ce.envmap,Ce.aomap,Ce.lightmap,Ce.fog]),vertexShader:st.meshbasic_vert,fragmentShader:st.meshbasic_frag},lambert:{uniforms:Rn([Ce.common,Ce.specularmap,Ce.envmap,Ce.aomap,Ce.lightmap,Ce.emissivemap,Ce.bumpmap,Ce.normalmap,Ce.displacementmap,Ce.fog,Ce.lights,{emissive:{value:new nt(0)}}]),vertexShader:st.meshlambert_vert,fragmentShader:st.meshlambert_frag},phong:{uniforms:Rn([Ce.common,Ce.specularmap,Ce.envmap,Ce.aomap,Ce.lightmap,Ce.emissivemap,Ce.bumpmap,Ce.normalmap,Ce.displacementmap,Ce.fog,Ce.lights,{emissive:{value:new nt(0)},specular:{value:new nt(1118481)},shininess:{value:30}}]),vertexShader:st.meshphong_vert,fragmentShader:st.meshphong_frag},standard:{uniforms:Rn([Ce.common,Ce.envmap,Ce.aomap,Ce.lightmap,Ce.emissivemap,Ce.bumpmap,Ce.normalmap,Ce.displacementmap,Ce.roughnessmap,Ce.metalnessmap,Ce.fog,Ce.lights,{emissive:{value:new nt(0)},roughness:{value:1},metalness:{value:0},envMapIntensity:{value:1}}]),vertexShader:st.meshphysical_vert,fragmentShader:st.meshphysical_frag},toon:{uniforms:Rn([Ce.common,Ce.aomap,Ce.lightmap,Ce.emissivemap,Ce.bumpmap,Ce.normalmap,Ce.displacementmap,Ce.gradientmap,Ce.fog,Ce.lights,{emissive:{value:new nt(0)}}]),vertexShader:st.meshtoon_vert,fragmentShader:st.meshtoon_frag},matcap:{uniforms:Rn([Ce.common,Ce.bumpmap,Ce.normalmap,Ce.displacementmap,Ce.fog,{matcap:{value:null}}]),vertexShader:st.meshmatcap_vert,fragmentShader:st.meshmatcap_frag},points:{uniforms:Rn([Ce.points,Ce.fog]),vertexShader:st.points_vert,fragmentShader:st.points_frag},dashed:{uniforms:Rn([Ce.common,Ce.fog,{scale:{value:1},dashSize:{value:1},totalSize:{value:2}}]),vertexShader:st.linedashed_vert,fragmentShader:st.linedashed_frag},depth:{uniforms:Rn([Ce.common,Ce.displacementmap]),vertexShader:st.depth_vert,fragmentShader:st.depth_frag},normal:{uniforms:Rn([Ce.common,Ce.bumpmap,Ce.normalmap,Ce.displacementmap,{opacity:{value:1}}]),vertexShader:st.meshnormal_vert,fragmentShader:st.meshnormal_frag},sprite:{uniforms:Rn([Ce.sprite,Ce.fog]),vertexShader:st.sprite_vert,fragmentShader:st.sprite_frag},background:{uniforms:{uvTransform:{value:new rt},t2D:{value:null},backgroundIntensity:{value:1}},vertexShader:st.background_vert,fragmentShader:st.background_frag},backgroundCube:{uniforms:{envMap:{value:null},flipEnvMap:{value:-1},backgroundBlurriness:{value:0},backgroundIntensity:{value:1},backgroundRotation:{value:new rt}},vertexShader:st.backgroundCube_vert,fragmentShader:st.backgroundCube_frag},cube:{uniforms:{tCube:{value:null},tFlip:{value:-1},opacity:{value:1}},vertexShader:st.cube_vert,fragmentShader:st.cube_frag},equirect:{uniforms:{tEquirect:{value:null}},vertexShader:st.equirect_vert,fragmentShader:st.equirect_frag},distanceRGBA:{uniforms:Rn([Ce.common,Ce.displacementmap,{referencePosition:{value:new k},nearDistance:{value:1},farDistance:{value:1e3}}]),vertexShader:st.distanceRGBA_vert,fragmentShader:st.distanceRGBA_frag},shadow:{uniforms:Rn([Ce.lights,Ce.fog,{color:{value:new nt(0)},opacity:{value:1}}]),vertexShader:st.shadow_vert,fragmentShader:st.shadow_frag}};yi.physical={uniforms:Rn([yi.standard.uniforms,{clearcoat:{value:0},clearcoatMap:{value:null},clearcoatMapTransform:{value:new rt},clearcoatNormalMap:{value:null},clearcoatNormalMapTransform:{value:new rt},clearcoatNormalScale:{value:new qe(1,1)},clearcoatRoughness:{value:0},clearcoatRoughnessMap:{value:null},clearcoatRoughnessMapTransform:{value:new rt},dispersion:{value:0},iridescence:{value:0},iridescenceMap:{value:null},iridescenceMapTransform:{value:new rt},iridescenceIOR:{value:1.3},iridescenceThicknessMinimum:{value:100},iridescenceThicknessMaximum:{value:400},iridescenceThicknessMap:{value:null},iridescenceThicknessMapTransform:{value:new rt},sheen:{value:0},sheenColor:{value:new nt(0)},sheenColorMap:{value:null},sheenColorMapTransform:{value:new rt},sheenRoughness:{value:1},sheenRoughnessMap:{value:null},sheenRoughnessMapTransform:{value:new rt},transmission:{value:0},transmissionMap:{value:null},transmissionMapTransform:{value:new rt},transmissionSamplerSize:{value:new qe},transmissionSamplerMap:{value:null},thickness:{value:0},thicknessMap:{value:null},thicknessMapTransform:{value:new rt},attenuationDistance:{value:0},attenuationColor:{value:new nt(0)},specularColor:{value:new nt(1,1,1)},specularColorMap:{value:null},specularColorMapTransform:{value:new rt},specularIntensity:{value:1},specularIntensityMap:{value:null},specularIntensityMapTransform:{value:new rt},anisotropyVector:{value:new qe},anisotropyMap:{value:null},anisotropyMapTransform:{value:new rt}}]),vertexShader:st.meshphysical_vert,fragmentShader:st.meshphysical_frag};const fo={r:0,b:0,g:0},Es=new Si,Uv=new Ot;function Nv(i,e,t,n,s,r,a){const o=new nt(0);let l=r===!0?0:1,c,u,h=null,d=0,f=null;function g(S){let y=S.isScene===!0?S.background:null;return y&&y.isTexture&&(y=(S.backgroundBlurriness>0?t:e).get(y)),y}function v(S){let y=!1;const w=g(S);w===null?p(o,l):w&&w.isColor&&(p(w,1),y=!0);const O=i.xr.getEnvironmentBlendMode();O==="additive"?n.buffers.color.setClear(0,0,0,1,a):O==="alpha-blend"&&n.buffers.color.setClear(0,0,0,0,a),(i.autoClear||y)&&(n.buffers.depth.setTest(!0),n.buffers.depth.setMask(!0),n.buffers.color.setMask(!0),i.clear(i.autoClearColor,i.autoClearDepth,i.autoClearStencil))}function m(S,y){const w=g(y);w&&(w.isCubeTexture||w.mapping===il)?(u===void 0&&(u=new gn(new Bi(1,1,1),new us({name:"BackgroundCubeMaterial",uniforms:Hr(yi.backgroundCube.uniforms),vertexShader:yi.backgroundCube.vertexShader,fragmentShader:yi.backgroundCube.fragmentShader,side:In,depthTest:!1,depthWrite:!1,fog:!1})),u.geometry.deleteAttribute("normal"),u.geometry.deleteAttribute("uv"),u.onBeforeRender=function(O,A,P){this.matrixWorld.copyPosition(P.matrixWorld)},Object.defineProperty(u.material,"envMap",{get:function(){return this.uniforms.envMap.value}}),s.update(u)),Es.copy(y.backgroundRotation),Es.x*=-1,Es.y*=-1,Es.z*=-1,w.isCubeTexture&&w.isRenderTargetTexture===!1&&(Es.y*=-1,Es.z*=-1),u.material.uniforms.envMap.value=w,u.material.uniforms.flipEnvMap.value=w.isCubeTexture&&w.isRenderTargetTexture===!1?-1:1,u.material.uniforms.backgroundBlurriness.value=y.backgroundBlurriness,u.material.uniforms.backgroundIntensity.value=y.backgroundIntensity,u.material.uniforms.backgroundRotation.value.setFromMatrix4(Uv.makeRotationFromEuler(Es)),u.material.toneMapped=St.getTransfer(w.colorSpace)!==Ft,(h!==w||d!==w.version||f!==i.toneMapping)&&(u.material.needsUpdate=!0,h=w,d=w.version,f=i.toneMapping),u.layers.enableAll(),S.unshift(u,u.geometry,u.material,0,0,null)):w&&w.isTexture&&(c===void 0&&(c=new gn(new Oa(2,2),new us({name:"BackgroundMaterial",uniforms:Hr(yi.background.uniforms),vertexShader:yi.background.vertexShader,fragmentShader:yi.background.fragmentShader,side:cs,depthTest:!1,depthWrite:!1,fog:!1})),c.geometry.deleteAttribute("normal"),Object.defineProperty(c.material,"map",{get:function(){return this.uniforms.t2D.value}}),s.update(c)),c.material.uniforms.t2D.value=w,c.material.uniforms.backgroundIntensity.value=y.backgroundIntensity,c.material.toneMapped=St.getTransfer(w.colorSpace)!==Ft,w.matrixAutoUpdate===!0&&w.updateMatrix(),c.material.uniforms.uvTransform.value.copy(w.matrix),(h!==w||d!==w.version||f!==i.toneMapping)&&(c.material.needsUpdate=!0,h=w,d=w.version,f=i.toneMapping),c.layers.enableAll(),S.unshift(c,c.geometry,c.material,0,0,null))}function p(S,y){S.getRGB(fo,Wf(i)),n.buffers.color.setClear(fo.r,fo.g,fo.b,y,a)}return{getClearColor:function(){return o},setClearColor:function(S,y=1){o.set(S),l=y,p(o,l)},getClearAlpha:function(){return l},setClearAlpha:function(S){l=S,p(o,l)},render:v,addToRenderList:m}}function Fv(i,e){const t=i.getParameter(i.MAX_VERTEX_ATTRIBS),n={},s=d(null);let r=s,a=!1;function o(x,R,j,z,K){let X=!1;const Q=h(z,j,R);r!==Q&&(r=Q,c(r.object)),X=f(x,z,j,K),X&&g(x,z,j,K),K!==null&&e.update(K,i.ELEMENT_ARRAY_BUFFER),(X||a)&&(a=!1,w(x,R,j,z),K!==null&&i.bindBuffer(i.ELEMENT_ARRAY_BUFFER,e.get(K).buffer))}function l(){return i.createVertexArray()}function c(x){return i.bindVertexArray(x)}function u(x){return i.deleteVertexArray(x)}function h(x,R,j){const z=j.wireframe===!0;let K=n[x.id];K===void 0&&(K={},n[x.id]=K);let X=K[R.id];X===void 0&&(X={},K[R.id]=X);let Q=X[z];return Q===void 0&&(Q=d(l()),X[z]=Q),Q}function d(x){const R=[],j=[],z=[];for(let K=0;K<t;K++)R[K]=0,j[K]=0,z[K]=0;return{geometry:null,program:null,wireframe:!1,newAttributes:R,enabledAttributes:j,attributeDivisors:z,object:x,attributes:{},index:null}}function f(x,R,j,z){const K=r.attributes,X=R.attributes;let Q=0;const Y=j.getAttributes();for(const ne in Y)if(Y[ne].location>=0){const de=K[ne];let xe=X[ne];if(xe===void 0&&(ne==="instanceMatrix"&&x.instanceMatrix&&(xe=x.instanceMatrix),ne==="instanceColor"&&x.instanceColor&&(xe=x.instanceColor)),de===void 0||de.attribute!==xe||xe&&de.data!==xe.data)return!0;Q++}return r.attributesNum!==Q||r.index!==z}function g(x,R,j,z){const K={},X=R.attributes;let Q=0;const Y=j.getAttributes();for(const ne in Y)if(Y[ne].location>=0){let de=X[ne];de===void 0&&(ne==="instanceMatrix"&&x.instanceMatrix&&(de=x.instanceMatrix),ne==="instanceColor"&&x.instanceColor&&(de=x.instanceColor));const xe={};xe.attribute=de,de&&de.data&&(xe.data=de.data),K[ne]=xe,Q++}r.attributes=K,r.attributesNum=Q,r.index=z}function v(){const x=r.newAttributes;for(let R=0,j=x.length;R<j;R++)x[R]=0}function m(x){p(x,0)}function p(x,R){const j=r.newAttributes,z=r.enabledAttributes,K=r.attributeDivisors;j[x]=1,z[x]===0&&(i.enableVertexAttribArray(x),z[x]=1),K[x]!==R&&(i.vertexAttribDivisor(x,R),K[x]=R)}function S(){const x=r.newAttributes,R=r.enabledAttributes;for(let j=0,z=R.length;j<z;j++)R[j]!==x[j]&&(i.disableVertexAttribArray(j),R[j]=0)}function y(x,R,j,z,K,X,Q){Q===!0?i.vertexAttribIPointer(x,R,j,K,X):i.vertexAttribPointer(x,R,j,z,K,X)}function w(x,R,j,z){v();const K=z.attributes,X=j.getAttributes(),Q=R.defaultAttributeValues;for(const Y in X){const ne=X[Y];if(ne.location>=0){let ge=K[Y];if(ge===void 0&&(Y==="instanceMatrix"&&x.instanceMatrix&&(ge=x.instanceMatrix),Y==="instanceColor"&&x.instanceColor&&(ge=x.instanceColor)),ge!==void 0){const de=ge.normalized,xe=ge.itemSize,we=e.get(ge);if(we===void 0)continue;const ye=we.buffer,ie=we.type,ue=we.bytesPerElement,Me=ie===i.INT||ie===i.UNSIGNED_INT||ge.gpuType===du;if(ge.isInterleavedBufferAttribute){const fe=ge.data,ze=fe.stride,Ge=ge.offset;if(fe.isInstancedInterleavedBuffer){for(let Fe=0;Fe<ne.locationSize;Fe++)p(ne.location+Fe,fe.meshPerAttribute);x.isInstancedMesh!==!0&&z._maxInstanceCount===void 0&&(z._maxInstanceCount=fe.meshPerAttribute*fe.count)}else for(let Fe=0;Fe<ne.locationSize;Fe++)m(ne.location+Fe);i.bindBuffer(i.ARRAY_BUFFER,ye);for(let Fe=0;Fe<ne.locationSize;Fe++)y(ne.location+Fe,xe/ne.locationSize,ie,de,ze*ue,(Ge+xe/ne.locationSize*Fe)*ue,Me)}else{if(ge.isInstancedBufferAttribute){for(let fe=0;fe<ne.locationSize;fe++)p(ne.location+fe,ge.meshPerAttribute);x.isInstancedMesh!==!0&&z._maxInstanceCount===void 0&&(z._maxInstanceCount=ge.meshPerAttribute*ge.count)}else for(let fe=0;fe<ne.locationSize;fe++)m(ne.location+fe);i.bindBuffer(i.ARRAY_BUFFER,ye);for(let fe=0;fe<ne.locationSize;fe++)y(ne.location+fe,xe/ne.locationSize,ie,de,xe*ue,xe/ne.locationSize*fe*ue,Me)}}else if(Q!==void 0){const de=Q[Y];if(de!==void 0)switch(de.length){case 2:i.vertexAttrib2fv(ne.location,de);break;case 3:i.vertexAttrib3fv(ne.location,de);break;case 4:i.vertexAttrib4fv(ne.location,de);break;default:i.vertexAttrib1fv(ne.location,de)}}}}S()}function O(){N();for(const x in n){const R=n[x];for(const j in R){const z=R[j];for(const K in z)u(z[K].object),delete z[K];delete R[j]}delete n[x]}}function A(x){if(n[x.id]===void 0)return;const R=n[x.id];for(const j in R){const z=R[j];for(const K in z)u(z[K].object),delete z[K];delete R[j]}delete n[x.id]}function P(x){for(const R in n){const j=n[R];if(j[x.id]===void 0)continue;const z=j[x.id];for(const K in z)u(z[K].object),delete z[K];delete j[x.id]}}function N(){b(),a=!0,r!==s&&(r=s,c(r.object))}function b(){s.geometry=null,s.program=null,s.wireframe=!1}return{setup:o,reset:N,resetDefaultState:b,dispose:O,releaseStatesOfGeometry:A,releaseStatesOfProgram:P,initAttributes:v,enableAttribute:m,disableUnusedAttributes:S}}function Ov(i,e,t){let n;function s(c){n=c}function r(c,u){i.drawArrays(n,c,u),t.update(u,n,1)}function a(c,u,h){h!==0&&(i.drawArraysInstanced(n,c,u,h),t.update(u,n,h))}function o(c,u,h){if(h===0)return;e.get("WEBGL_multi_draw").multiDrawArraysWEBGL(n,c,0,u,0,h);let f=0;for(let g=0;g<h;g++)f+=u[g];t.update(f,n,1)}function l(c,u,h,d){if(h===0)return;const f=e.get("WEBGL_multi_draw");if(f===null)for(let g=0;g<c.length;g++)a(c[g],u[g],d[g]);else{f.multiDrawArraysInstancedWEBGL(n,c,0,u,0,d,0,h);let g=0;for(let v=0;v<h;v++)g+=u[v];for(let v=0;v<d.length;v++)t.update(g,n,d[v])}}this.setMode=s,this.render=r,this.renderInstances=a,this.renderMultiDraw=o,this.renderMultiDrawInstances=l}function Bv(i,e,t,n){let s;function r(){if(s!==void 0)return s;if(e.has("EXT_texture_filter_anisotropic")===!0){const A=e.get("EXT_texture_filter_anisotropic");s=i.getParameter(A.MAX_TEXTURE_MAX_ANISOTROPY_EXT)}else s=0;return s}function a(A){return!(A!==ci&&n.convert(A)!==i.getParameter(i.IMPLEMENTATION_COLOR_READ_FORMAT))}function o(A){const P=A===Ia&&(e.has("EXT_color_buffer_half_float")||e.has("EXT_color_buffer_float"));return!(A!==Gi&&n.convert(A)!==i.getParameter(i.IMPLEMENTATION_COLOR_READ_TYPE)&&A!==Fi&&!P)}function l(A){if(A==="highp"){if(i.getShaderPrecisionFormat(i.VERTEX_SHADER,i.HIGH_FLOAT).precision>0&&i.getShaderPrecisionFormat(i.FRAGMENT_SHADER,i.HIGH_FLOAT).precision>0)return"highp";A="mediump"}return A==="mediump"&&i.getShaderPrecisionFormat(i.VERTEX_SHADER,i.MEDIUM_FLOAT).precision>0&&i.getShaderPrecisionFormat(i.FRAGMENT_SHADER,i.MEDIUM_FLOAT).precision>0?"mediump":"lowp"}let c=t.precision!==void 0?t.precision:"highp";const u=l(c);u!==c&&(console.warn("THREE.WebGLRenderer:",c,"not supported, using",u,"instead."),c=u);const h=t.logarithmicDepthBuffer===!0,d=i.getParameter(i.MAX_TEXTURE_IMAGE_UNITS),f=i.getParameter(i.MAX_VERTEX_TEXTURE_IMAGE_UNITS),g=i.getParameter(i.MAX_TEXTURE_SIZE),v=i.getParameter(i.MAX_CUBE_MAP_TEXTURE_SIZE),m=i.getParameter(i.MAX_VERTEX_ATTRIBS),p=i.getParameter(i.MAX_VERTEX_UNIFORM_VECTORS),S=i.getParameter(i.MAX_VARYING_VECTORS),y=i.getParameter(i.MAX_FRAGMENT_UNIFORM_VECTORS),w=f>0,O=i.getParameter(i.MAX_SAMPLES);return{isWebGL2:!0,getMaxAnisotropy:r,getMaxPrecision:l,textureFormatReadable:a,textureTypeReadable:o,precision:c,logarithmicDepthBuffer:h,maxTextures:d,maxVertexTextures:f,maxTextureSize:g,maxCubemapSize:v,maxAttributes:m,maxVertexUniforms:p,maxVaryings:S,maxFragmentUniforms:y,vertexTextures:w,maxSamples:O}}function zv(i){const e=this;let t=null,n=0,s=!1,r=!1;const a=new is,o=new rt,l={value:null,needsUpdate:!1};this.uniform=l,this.numPlanes=0,this.numIntersection=0,this.init=function(h,d){const f=h.length!==0||d||n!==0||s;return s=d,n=h.length,f},this.beginShadows=function(){r=!0,u(null)},this.endShadows=function(){r=!1},this.setGlobalState=function(h,d){t=u(h,d,0)},this.setState=function(h,d,f){const g=h.clippingPlanes,v=h.clipIntersection,m=h.clipShadows,p=i.get(h);if(!s||g===null||g.length===0||r&&!m)r?u(null):c();else{const S=r?0:n,y=S*4;let w=p.clippingState||null;l.value=w,w=u(g,d,y,f);for(let O=0;O!==y;++O)w[O]=t[O];p.clippingState=w,this.numIntersection=v?this.numPlanes:0,this.numPlanes+=S}};function c(){l.value!==t&&(l.value=t,l.needsUpdate=n>0),e.numPlanes=n,e.numIntersection=0}function u(h,d,f,g){const v=h!==null?h.length:0;let m=null;if(v!==0){if(m=l.value,g!==!0||m===null){const p=f+v*4,S=d.matrixWorldInverse;o.getNormalMatrix(S),(m===null||m.length<p)&&(m=new Float32Array(p));for(let y=0,w=f;y!==v;++y,w+=4)a.copy(h[y]).applyMatrix4(S,o),a.normal.toArray(m,w),m[w+3]=a.constant}l.value=m,l.needsUpdate=!0}return e.numPlanes=v,e.numIntersection=0,m}}function kv(i){let e=new WeakMap;function t(a,o){return o===yc?a.mapping=Or:o===Mc&&(a.mapping=Br),a}function n(a){if(a&&a.isTexture){const o=a.mapping;if(o===yc||o===Mc)if(e.has(a)){const l=e.get(a).texture;return t(l,a.mapping)}else{const l=a.image;if(l&&l.height>0){const c=new Zg(l.height);return c.fromEquirectangularTexture(i,a),e.set(a,c),a.addEventListener("dispose",s),t(c.texture,a.mapping)}else return null}}return a}function s(a){const o=a.target;o.removeEventListener("dispose",s);const l=e.get(o);l!==void 0&&(e.delete(o),l.dispose())}function r(){e=new WeakMap}return{get:n,dispose:r}}class Ur extends Xf{constructor(e=-1,t=1,n=1,s=-1,r=.1,a=2e3){super(),this.isOrthographicCamera=!0,this.type="OrthographicCamera",this.zoom=1,this.view=null,this.left=e,this.right=t,this.top=n,this.bottom=s,this.near=r,this.far=a,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.left=e.left,this.right=e.right,this.top=e.top,this.bottom=e.bottom,this.near=e.near,this.far=e.far,this.zoom=e.zoom,this.view=e.view===null?null:Object.assign({},e.view),this}setViewOffset(e,t,n,s,r,a){this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=n,this.view.offsetY=s,this.view.width=r,this.view.height=a,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const e=(this.right-this.left)/(2*this.zoom),t=(this.top-this.bottom)/(2*this.zoom),n=(this.right+this.left)/2,s=(this.top+this.bottom)/2;let r=n-e,a=n+e,o=s+t,l=s-t;if(this.view!==null&&this.view.enabled){const c=(this.right-this.left)/this.view.fullWidth/this.zoom,u=(this.top-this.bottom)/this.view.fullHeight/this.zoom;r+=c*this.view.offsetX,a=r+c*this.view.width,o-=u*this.view.offsetY,l=o-u*this.view.height}this.projectionMatrix.makeOrthographic(r,a,o,l,this.near,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){const t=super.toJSON(e);return t.object.zoom=this.zoom,t.object.left=this.left,t.object.right=this.right,t.object.top=this.top,t.object.bottom=this.bottom,t.object.near=this.near,t.object.far=this.far,this.view!==null&&(t.object.view=Object.assign({},this.view)),t}}const Ar=4,Vh=[.125,.215,.35,.446,.526,.582],Ps=20,Kl=new Ur,Gh=new nt;let Zl=null,Jl=0,Ql=0,ec=!1;const Ts=(1+Math.sqrt(5))/2,_r=1/Ts,Wh=[new k(-Ts,_r,0),new k(Ts,_r,0),new k(-_r,0,Ts),new k(_r,0,Ts),new k(0,Ts,-_r),new k(0,Ts,_r),new k(-1,1,-1),new k(1,1,-1),new k(-1,1,1),new k(1,1,1)];class Xh{constructor(e){this._renderer=e,this._pingPongRenderTarget=null,this._lodMax=0,this._cubeSize=0,this._lodPlanes=[],this._sizeLods=[],this._sigmas=[],this._blurMaterial=null,this._cubemapMaterial=null,this._equirectMaterial=null,this._compileMaterial(this._blurMaterial)}fromScene(e,t=0,n=.1,s=100){Zl=this._renderer.getRenderTarget(),Jl=this._renderer.getActiveCubeFace(),Ql=this._renderer.getActiveMipmapLevel(),ec=this._renderer.xr.enabled,this._renderer.xr.enabled=!1,this._setSize(256);const r=this._allocateTargets();return r.depthBuffer=!0,this._sceneToCubeUV(e,n,s,r),t>0&&this._blur(r,0,0,t),this._applyPMREM(r),this._cleanup(r),r}fromEquirectangular(e,t=null){return this._fromTexture(e,t)}fromCubemap(e,t=null){return this._fromTexture(e,t)}compileCubemapShader(){this._cubemapMaterial===null&&(this._cubemapMaterial=$h(),this._compileMaterial(this._cubemapMaterial))}compileEquirectangularShader(){this._equirectMaterial===null&&(this._equirectMaterial=Yh(),this._compileMaterial(this._equirectMaterial))}dispose(){this._dispose(),this._cubemapMaterial!==null&&this._cubemapMaterial.dispose(),this._equirectMaterial!==null&&this._equirectMaterial.dispose()}_setSize(e){this._lodMax=Math.floor(Math.log2(e)),this._cubeSize=Math.pow(2,this._lodMax)}_dispose(){this._blurMaterial!==null&&this._blurMaterial.dispose(),this._pingPongRenderTarget!==null&&this._pingPongRenderTarget.dispose();for(let e=0;e<this._lodPlanes.length;e++)this._lodPlanes[e].dispose()}_cleanup(e){this._renderer.setRenderTarget(Zl,Jl,Ql),this._renderer.xr.enabled=ec,e.scissorTest=!1,po(e,0,0,e.width,e.height)}_fromTexture(e,t){e.mapping===Or||e.mapping===Br?this._setSize(e.image.length===0?16:e.image[0].width||e.image[0].image.width):this._setSize(e.image.width/4),Zl=this._renderer.getRenderTarget(),Jl=this._renderer.getActiveCubeFace(),Ql=this._renderer.getActiveMipmapLevel(),ec=this._renderer.xr.enabled,this._renderer.xr.enabled=!1;const n=t||this._allocateTargets();return this._textureToCubeUV(e,n),this._applyPMREM(n),this._cleanup(n),n}_allocateTargets(){const e=3*Math.max(this._cubeSize,112),t=4*this._cubeSize,n={magFilter:ai,minFilter:ai,generateMipmaps:!1,type:Ia,format:ci,colorSpace:fs,depthBuffer:!1},s=qh(e,t,n);if(this._pingPongRenderTarget===null||this._pingPongRenderTarget.width!==e||this._pingPongRenderTarget.height!==t){this._pingPongRenderTarget!==null&&this._dispose(),this._pingPongRenderTarget=qh(e,t,n);const{_lodMax:r}=this;({sizeLods:this._sizeLods,lodPlanes:this._lodPlanes,sigmas:this._sigmas}=Hv(r)),this._blurMaterial=Vv(r,e,t)}return s}_compileMaterial(e){const t=new gn(this._lodPlanes[0],e);this._renderer.compile(t,Kl)}_sceneToCubeUV(e,t,n,s){const o=new Sn(90,1,t,n),l=[1,-1,1,1,1,1],c=[1,1,1,-1,-1,-1],u=this._renderer,h=u.autoClear,d=u.toneMapping;u.getClearColor(Gh),u.toneMapping=ls,u.autoClear=!1;const f=new Ir({name:"PMREM.Background",side:In,depthWrite:!1,depthTest:!1}),g=new gn(new Bi,f);let v=!1;const m=e.background;m?m.isColor&&(f.color.copy(m),e.background=null,v=!0):(f.color.copy(Gh),v=!0);for(let p=0;p<6;p++){const S=p%3;S===0?(o.up.set(0,l[p],0),o.lookAt(c[p],0,0)):S===1?(o.up.set(0,0,l[p]),o.lookAt(0,c[p],0)):(o.up.set(0,l[p],0),o.lookAt(0,0,c[p]));const y=this._cubeSize;po(s,S*y,p>2?y:0,y,y),u.setRenderTarget(s),v&&u.render(g,o),u.render(e,o)}g.geometry.dispose(),g.material.dispose(),u.toneMapping=d,u.autoClear=h,e.background=m}_textureToCubeUV(e,t){const n=this._renderer,s=e.mapping===Or||e.mapping===Br;s?(this._cubemapMaterial===null&&(this._cubemapMaterial=$h()),this._cubemapMaterial.uniforms.flipEnvMap.value=e.isRenderTargetTexture===!1?-1:1):this._equirectMaterial===null&&(this._equirectMaterial=Yh());const r=s?this._cubemapMaterial:this._equirectMaterial,a=new gn(this._lodPlanes[0],r),o=r.uniforms;o.envMap.value=e;const l=this._cubeSize;po(t,0,0,3*l,2*l),n.setRenderTarget(t),n.render(a,Kl)}_applyPMREM(e){const t=this._renderer,n=t.autoClear;t.autoClear=!1;const s=this._lodPlanes.length;for(let r=1;r<s;r++){const a=Math.sqrt(this._sigmas[r]*this._sigmas[r]-this._sigmas[r-1]*this._sigmas[r-1]),o=Wh[(s-r-1)%Wh.length];this._blur(e,r-1,r,a,o)}t.autoClear=n}_blur(e,t,n,s,r){const a=this._pingPongRenderTarget;this._halfBlur(e,a,t,n,s,"latitudinal",r),this._halfBlur(a,e,n,n,s,"longitudinal",r)}_halfBlur(e,t,n,s,r,a,o){const l=this._renderer,c=this._blurMaterial;a!=="latitudinal"&&a!=="longitudinal"&&console.error("blur direction must be either latitudinal or longitudinal!");const u=3,h=new gn(this._lodPlanes[s],c),d=c.uniforms,f=this._sizeLods[n]-1,g=isFinite(r)?Math.PI/(2*f):2*Math.PI/(2*Ps-1),v=r/g,m=isFinite(r)?1+Math.floor(u*v):Ps;m>Ps&&console.warn(`sigmaRadians, ${r}, is too large and will clip, as it requested ${m} samples when the maximum is set to ${Ps}`);const p=[];let S=0;for(let P=0;P<Ps;++P){const N=P/v,b=Math.exp(-N*N/2);p.push(b),P===0?S+=b:P<m&&(S+=2*b)}for(let P=0;P<p.length;P++)p[P]=p[P]/S;d.envMap.value=e.texture,d.samples.value=m,d.weights.value=p,d.latitudinal.value=a==="latitudinal",o&&(d.poleAxis.value=o);const{_lodMax:y}=this;d.dTheta.value=g,d.mipInt.value=y-n;const w=this._sizeLods[s],O=3*w*(s>y-Ar?s-y+Ar:0),A=4*(this._cubeSize-w);po(t,O,A,3*w,2*w),l.setRenderTarget(t),l.render(h,Kl)}}function Hv(i){const e=[],t=[],n=[];let s=i;const r=i-Ar+1+Vh.length;for(let a=0;a<r;a++){const o=Math.pow(2,s);t.push(o);let l=1/o;a>i-Ar?l=Vh[a-i+Ar-1]:a===0&&(l=0),n.push(l);const c=1/(o-2),u=-c,h=1+c,d=[u,u,h,u,h,h,u,u,h,h,u,h],f=6,g=6,v=3,m=2,p=1,S=new Float32Array(v*g*f),y=new Float32Array(m*g*f),w=new Float32Array(p*g*f);for(let A=0;A<f;A++){const P=A%3*2/3-1,N=A>2?0:-1,b=[P,N,0,P+2/3,N,0,P+2/3,N+1,0,P,N,0,P+2/3,N+1,0,P,N+1,0];S.set(b,v*g*A),y.set(d,m*g*A);const x=[A,A,A,A,A,A];w.set(x,p*g*A)}const O=new Xt;O.setAttribute("position",new ui(S,v)),O.setAttribute("uv",new ui(y,m)),O.setAttribute("faceIndex",new ui(w,p)),e.push(O),s>Ar&&s--}return{lodPlanes:e,sizeLods:t,sigmas:n}}function qh(i,e,t){const n=new Bs(i,e,t);return n.texture.mapping=il,n.texture.name="PMREM.cubeUv",n.scissorTest=!0,n}function po(i,e,t,n,s){i.viewport.set(e,t,n,s),i.scissor.set(e,t,n,s)}function Vv(i,e,t){const n=new Float32Array(Ps),s=new k(0,1,0);return new us({name:"SphericalGaussianBlur",defines:{n:Ps,CUBEUV_TEXEL_WIDTH:1/e,CUBEUV_TEXEL_HEIGHT:1/t,CUBEUV_MAX_MIP:`${i}.0`},uniforms:{envMap:{value:null},samples:{value:1},weights:{value:n},latitudinal:{value:!1},dTheta:{value:0},mipInt:{value:0},poleAxis:{value:s}},vertexShader:Su(),fragmentShader:`

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
		`,blending:os,depthTest:!1,depthWrite:!1})}function Yh(){return new us({name:"EquirectangularToCubeUV",uniforms:{envMap:{value:null}},vertexShader:Su(),fragmentShader:`

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
		`,blending:os,depthTest:!1,depthWrite:!1})}function $h(){return new us({name:"CubemapToCubeUV",uniforms:{envMap:{value:null},flipEnvMap:{value:-1}},vertexShader:Su(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			uniform float flipEnvMap;

			varying vec3 vOutputDirection;

			uniform samplerCube envMap;

			void main() {

				gl_FragColor = textureCube( envMap, vec3( flipEnvMap * vOutputDirection.x, vOutputDirection.yz ) );

			}
		`,blending:os,depthTest:!1,depthWrite:!1})}function Su(){return`

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
	`}function Gv(i){let e=new WeakMap,t=null;function n(o){if(o&&o.isTexture){const l=o.mapping,c=l===yc||l===Mc,u=l===Or||l===Br;if(c||u){let h=e.get(o);const d=h!==void 0?h.texture.pmremVersion:0;if(o.isRenderTargetTexture&&o.pmremVersion!==d)return t===null&&(t=new Xh(i)),h=c?t.fromEquirectangular(o,h):t.fromCubemap(o,h),h.texture.pmremVersion=o.pmremVersion,e.set(o,h),h.texture;if(h!==void 0)return h.texture;{const f=o.image;return c&&f&&f.height>0||u&&f&&s(f)?(t===null&&(t=new Xh(i)),h=c?t.fromEquirectangular(o):t.fromCubemap(o),h.texture.pmremVersion=o.pmremVersion,e.set(o,h),o.addEventListener("dispose",r),h.texture):null}}}return o}function s(o){let l=0;const c=6;for(let u=0;u<c;u++)o[u]!==void 0&&l++;return l===c}function r(o){const l=o.target;l.removeEventListener("dispose",r);const c=e.get(l);c!==void 0&&(e.delete(l),c.dispose())}function a(){e=new WeakMap,t!==null&&(t.dispose(),t=null)}return{get:n,dispose:a}}function Wv(i){const e={};function t(n){if(e[n]!==void 0)return e[n];let s;switch(n){case"WEBGL_depth_texture":s=i.getExtension("WEBGL_depth_texture")||i.getExtension("MOZ_WEBGL_depth_texture")||i.getExtension("WEBKIT_WEBGL_depth_texture");break;case"EXT_texture_filter_anisotropic":s=i.getExtension("EXT_texture_filter_anisotropic")||i.getExtension("MOZ_EXT_texture_filter_anisotropic")||i.getExtension("WEBKIT_EXT_texture_filter_anisotropic");break;case"WEBGL_compressed_texture_s3tc":s=i.getExtension("WEBGL_compressed_texture_s3tc")||i.getExtension("MOZ_WEBGL_compressed_texture_s3tc")||i.getExtension("WEBKIT_WEBGL_compressed_texture_s3tc");break;case"WEBGL_compressed_texture_pvrtc":s=i.getExtension("WEBGL_compressed_texture_pvrtc")||i.getExtension("WEBKIT_WEBGL_compressed_texture_pvrtc");break;default:s=i.getExtension(n)}return e[n]=s,s}return{has:function(n){return t(n)!==null},init:function(){t("EXT_color_buffer_float"),t("WEBGL_clip_cull_distance"),t("OES_texture_float_linear"),t("EXT_color_buffer_half_float"),t("WEBGL_multisampled_render_to_texture"),t("WEBGL_render_shared_exponent")},get:function(n){const s=t(n);return s===null&&Lr("THREE.WebGLRenderer: "+n+" extension not supported."),s}}}function Xv(i,e,t,n){const s={},r=new WeakMap;function a(h){const d=h.target;d.index!==null&&e.remove(d.index);for(const g in d.attributes)e.remove(d.attributes[g]);for(const g in d.morphAttributes){const v=d.morphAttributes[g];for(let m=0,p=v.length;m<p;m++)e.remove(v[m])}d.removeEventListener("dispose",a),delete s[d.id];const f=r.get(d);f&&(e.remove(f),r.delete(d)),n.releaseStatesOfGeometry(d),d.isInstancedBufferGeometry===!0&&delete d._maxInstanceCount,t.memory.geometries--}function o(h,d){return s[d.id]===!0||(d.addEventListener("dispose",a),s[d.id]=!0,t.memory.geometries++),d}function l(h){const d=h.attributes;for(const g in d)e.update(d[g],i.ARRAY_BUFFER);const f=h.morphAttributes;for(const g in f){const v=f[g];for(let m=0,p=v.length;m<p;m++)e.update(v[m],i.ARRAY_BUFFER)}}function c(h){const d=[],f=h.index,g=h.attributes.position;let v=0;if(f!==null){const S=f.array;v=f.version;for(let y=0,w=S.length;y<w;y+=3){const O=S[y+0],A=S[y+1],P=S[y+2];d.push(O,A,A,P,P,O)}}else if(g!==void 0){const S=g.array;v=g.version;for(let y=0,w=S.length/3-1;y<w;y+=3){const O=y+0,A=y+1,P=y+2;d.push(O,A,A,P,P,O)}}else return;const m=new(Bf(d)?Gf:Vf)(d,1);m.version=v;const p=r.get(h);p&&e.remove(p),r.set(h,m)}function u(h){const d=r.get(h);if(d){const f=h.index;f!==null&&d.version<f.version&&c(h)}else c(h);return r.get(h)}return{get:o,update:l,getWireframeAttribute:u}}function qv(i,e,t){let n;function s(d){n=d}let r,a;function o(d){r=d.type,a=d.bytesPerElement}function l(d,f){i.drawElements(n,f,r,d*a),t.update(f,n,1)}function c(d,f,g){g!==0&&(i.drawElementsInstanced(n,f,r,d*a,g),t.update(f,n,g))}function u(d,f,g){if(g===0)return;e.get("WEBGL_multi_draw").multiDrawElementsWEBGL(n,f,0,r,d,0,g);let m=0;for(let p=0;p<g;p++)m+=f[p];t.update(m,n,1)}function h(d,f,g,v){if(g===0)return;const m=e.get("WEBGL_multi_draw");if(m===null)for(let p=0;p<d.length;p++)c(d[p]/a,f[p],v[p]);else{m.multiDrawElementsInstancedWEBGL(n,f,0,r,d,0,v,0,g);let p=0;for(let S=0;S<g;S++)p+=f[S];for(let S=0;S<v.length;S++)t.update(p,n,v[S])}}this.setMode=s,this.setIndex=o,this.render=l,this.renderInstances=c,this.renderMultiDraw=u,this.renderMultiDrawInstances=h}function Yv(i){const e={geometries:0,textures:0},t={frame:0,calls:0,triangles:0,points:0,lines:0};function n(r,a,o){switch(t.calls++,a){case i.TRIANGLES:t.triangles+=o*(r/3);break;case i.LINES:t.lines+=o*(r/2);break;case i.LINE_STRIP:t.lines+=o*(r-1);break;case i.LINE_LOOP:t.lines+=o*r;break;case i.POINTS:t.points+=o*r;break;default:console.error("THREE.WebGLInfo: Unknown draw mode:",a);break}}function s(){t.calls=0,t.triangles=0,t.points=0,t.lines=0}return{memory:e,render:t,programs:null,autoReset:!0,reset:s,update:n}}function $v(i,e,t){const n=new WeakMap,s=new tn;function r(a,o,l){const c=a.morphTargetInfluences,u=o.morphAttributes.position||o.morphAttributes.normal||o.morphAttributes.color,h=u!==void 0?u.length:0;let d=n.get(o);if(d===void 0||d.count!==h){let x=function(){N.dispose(),n.delete(o),o.removeEventListener("dispose",x)};var f=x;d!==void 0&&d.texture.dispose();const g=o.morphAttributes.position!==void 0,v=o.morphAttributes.normal!==void 0,m=o.morphAttributes.color!==void 0,p=o.morphAttributes.position||[],S=o.morphAttributes.normal||[],y=o.morphAttributes.color||[];let w=0;g===!0&&(w=1),v===!0&&(w=2),m===!0&&(w=3);let O=o.attributes.position.count*w,A=1;O>e.maxTextureSize&&(A=Math.ceil(O/e.maxTextureSize),O=e.maxTextureSize);const P=new Float32Array(O*A*4*h),N=new kf(P,O,A,h);N.type=Fi,N.needsUpdate=!0;const b=w*4;for(let R=0;R<h;R++){const j=p[R],z=S[R],K=y[R],X=O*A*4*R;for(let Q=0;Q<j.count;Q++){const Y=Q*b;g===!0&&(s.fromBufferAttribute(j,Q),P[X+Y+0]=s.x,P[X+Y+1]=s.y,P[X+Y+2]=s.z,P[X+Y+3]=0),v===!0&&(s.fromBufferAttribute(z,Q),P[X+Y+4]=s.x,P[X+Y+5]=s.y,P[X+Y+6]=s.z,P[X+Y+7]=0),m===!0&&(s.fromBufferAttribute(K,Q),P[X+Y+8]=s.x,P[X+Y+9]=s.y,P[X+Y+10]=s.z,P[X+Y+11]=K.itemSize===4?s.w:1)}}d={count:h,texture:N,size:new qe(O,A)},n.set(o,d),o.addEventListener("dispose",x)}if(a.isInstancedMesh===!0&&a.morphTexture!==null)l.getUniforms().setValue(i,"morphTexture",a.morphTexture,t);else{let g=0;for(let m=0;m<c.length;m++)g+=c[m];const v=o.morphTargetsRelative?1:1-g;l.getUniforms().setValue(i,"morphTargetBaseInfluence",v),l.getUniforms().setValue(i,"morphTargetInfluences",c)}l.getUniforms().setValue(i,"morphTargetsTexture",d.texture,t),l.getUniforms().setValue(i,"morphTargetsTextureSize",d.size)}return{update:r}}function jv(i,e,t,n){let s=new WeakMap;function r(l){const c=n.render.frame,u=l.geometry,h=e.get(l,u);if(s.get(h)!==c&&(e.update(h),s.set(h,c)),l.isInstancedMesh&&(l.hasEventListener("dispose",o)===!1&&l.addEventListener("dispose",o),s.get(l)!==c&&(t.update(l.instanceMatrix,i.ARRAY_BUFFER),l.instanceColor!==null&&t.update(l.instanceColor,i.ARRAY_BUFFER),s.set(l,c))),l.isSkinnedMesh){const d=l.skeleton;s.get(d)!==c&&(d.update(),s.set(d,c))}return h}function a(){s=new WeakMap}function o(l){const c=l.target;c.removeEventListener("dispose",o),t.remove(c.instanceMatrix),c.instanceColor!==null&&t.remove(c.instanceColor)}return{update:r,dispose:a}}class $f extends Ln{constructor(e,t,n,s,r,a,o,l,c,u=Rr){if(u!==Rr&&u!==kr)throw new Error("DepthTexture format must be either THREE.DepthFormat or THREE.DepthStencilFormat");n===void 0&&u===Rr&&(n=Os),n===void 0&&u===kr&&(n=zr),super(null,s,r,a,o,l,u,n,c),this.isDepthTexture=!0,this.image={width:e,height:t},this.magFilter=o!==void 0?o:Kn,this.minFilter=l!==void 0?l:Kn,this.flipY=!1,this.generateMipmaps=!1,this.compareFunction=null}copy(e){return super.copy(e),this.compareFunction=e.compareFunction,this}toJSON(e){const t=super.toJSON(e);return this.compareFunction!==null&&(t.compareFunction=this.compareFunction),t}}const jf=new Ln,jh=new $f(1,1),Kf=new kf,Zf=new Ng,Jf=new qf,Kh=[],Zh=[],Jh=new Float32Array(16),Qh=new Float32Array(9),ed=new Float32Array(4);function Kr(i,e,t){const n=i[0];if(n<=0||n>0)return i;const s=e*t;let r=Kh[s];if(r===void 0&&(r=new Float32Array(s),Kh[s]=r),e!==0){n.toArray(r,0);for(let a=1,o=0;a!==e;++a)o+=t,i[a].toArray(r,o)}return r}function nn(i,e){if(i.length!==e.length)return!1;for(let t=0,n=i.length;t<n;t++)if(i[t]!==e[t])return!1;return!0}function sn(i,e){for(let t=0,n=e.length;t<n;t++)i[t]=e[t]}function rl(i,e){let t=Zh[e];t===void 0&&(t=new Int32Array(e),Zh[e]=t);for(let n=0;n!==e;++n)t[n]=i.allocateTextureUnit();return t}function Kv(i,e){const t=this.cache;t[0]!==e&&(i.uniform1f(this.addr,e),t[0]=e)}function Zv(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(i.uniform2f(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(nn(t,e))return;i.uniform2fv(this.addr,e),sn(t,e)}}function Jv(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(i.uniform3f(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else if(e.r!==void 0)(t[0]!==e.r||t[1]!==e.g||t[2]!==e.b)&&(i.uniform3f(this.addr,e.r,e.g,e.b),t[0]=e.r,t[1]=e.g,t[2]=e.b);else{if(nn(t,e))return;i.uniform3fv(this.addr,e),sn(t,e)}}function Qv(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(i.uniform4f(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(nn(t,e))return;i.uniform4fv(this.addr,e),sn(t,e)}}function ex(i,e){const t=this.cache,n=e.elements;if(n===void 0){if(nn(t,e))return;i.uniformMatrix2fv(this.addr,!1,e),sn(t,e)}else{if(nn(t,n))return;ed.set(n),i.uniformMatrix2fv(this.addr,!1,ed),sn(t,n)}}function tx(i,e){const t=this.cache,n=e.elements;if(n===void 0){if(nn(t,e))return;i.uniformMatrix3fv(this.addr,!1,e),sn(t,e)}else{if(nn(t,n))return;Qh.set(n),i.uniformMatrix3fv(this.addr,!1,Qh),sn(t,n)}}function nx(i,e){const t=this.cache,n=e.elements;if(n===void 0){if(nn(t,e))return;i.uniformMatrix4fv(this.addr,!1,e),sn(t,e)}else{if(nn(t,n))return;Jh.set(n),i.uniformMatrix4fv(this.addr,!1,Jh),sn(t,n)}}function ix(i,e){const t=this.cache;t[0]!==e&&(i.uniform1i(this.addr,e),t[0]=e)}function sx(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(i.uniform2i(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(nn(t,e))return;i.uniform2iv(this.addr,e),sn(t,e)}}function rx(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(i.uniform3i(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(nn(t,e))return;i.uniform3iv(this.addr,e),sn(t,e)}}function ax(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(i.uniform4i(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(nn(t,e))return;i.uniform4iv(this.addr,e),sn(t,e)}}function ox(i,e){const t=this.cache;t[0]!==e&&(i.uniform1ui(this.addr,e),t[0]=e)}function lx(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(i.uniform2ui(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(nn(t,e))return;i.uniform2uiv(this.addr,e),sn(t,e)}}function cx(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(i.uniform3ui(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(nn(t,e))return;i.uniform3uiv(this.addr,e),sn(t,e)}}function ux(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(i.uniform4ui(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(nn(t,e))return;i.uniform4uiv(this.addr,e),sn(t,e)}}function hx(i,e,t){const n=this.cache,s=t.allocateTextureUnit();n[0]!==s&&(i.uniform1i(this.addr,s),n[0]=s);let r;this.type===i.SAMPLER_2D_SHADOW?(jh.compareFunction=Of,r=jh):r=jf,t.setTexture2D(e||r,s)}function dx(i,e,t){const n=this.cache,s=t.allocateTextureUnit();n[0]!==s&&(i.uniform1i(this.addr,s),n[0]=s),t.setTexture3D(e||Zf,s)}function fx(i,e,t){const n=this.cache,s=t.allocateTextureUnit();n[0]!==s&&(i.uniform1i(this.addr,s),n[0]=s),t.setTextureCube(e||Jf,s)}function px(i,e,t){const n=this.cache,s=t.allocateTextureUnit();n[0]!==s&&(i.uniform1i(this.addr,s),n[0]=s),t.setTexture2DArray(e||Kf,s)}function mx(i){switch(i){case 5126:return Kv;case 35664:return Zv;case 35665:return Jv;case 35666:return Qv;case 35674:return ex;case 35675:return tx;case 35676:return nx;case 5124:case 35670:return ix;case 35667:case 35671:return sx;case 35668:case 35672:return rx;case 35669:case 35673:return ax;case 5125:return ox;case 36294:return lx;case 36295:return cx;case 36296:return ux;case 35678:case 36198:case 36298:case 36306:case 35682:return hx;case 35679:case 36299:case 36307:return dx;case 35680:case 36300:case 36308:case 36293:return fx;case 36289:case 36303:case 36311:case 36292:return px}}function gx(i,e){i.uniform1fv(this.addr,e)}function _x(i,e){const t=Kr(e,this.size,2);i.uniform2fv(this.addr,t)}function vx(i,e){const t=Kr(e,this.size,3);i.uniform3fv(this.addr,t)}function xx(i,e){const t=Kr(e,this.size,4);i.uniform4fv(this.addr,t)}function yx(i,e){const t=Kr(e,this.size,4);i.uniformMatrix2fv(this.addr,!1,t)}function Mx(i,e){const t=Kr(e,this.size,9);i.uniformMatrix3fv(this.addr,!1,t)}function Sx(i,e){const t=Kr(e,this.size,16);i.uniformMatrix4fv(this.addr,!1,t)}function bx(i,e){i.uniform1iv(this.addr,e)}function Ex(i,e){i.uniform2iv(this.addr,e)}function wx(i,e){i.uniform3iv(this.addr,e)}function Tx(i,e){i.uniform4iv(this.addr,e)}function Ax(i,e){i.uniform1uiv(this.addr,e)}function Cx(i,e){i.uniform2uiv(this.addr,e)}function Rx(i,e){i.uniform3uiv(this.addr,e)}function Px(i,e){i.uniform4uiv(this.addr,e)}function Lx(i,e,t){const n=this.cache,s=e.length,r=rl(t,s);nn(n,r)||(i.uniform1iv(this.addr,r),sn(n,r));for(let a=0;a!==s;++a)t.setTexture2D(e[a]||jf,r[a])}function Dx(i,e,t){const n=this.cache,s=e.length,r=rl(t,s);nn(n,r)||(i.uniform1iv(this.addr,r),sn(n,r));for(let a=0;a!==s;++a)t.setTexture3D(e[a]||Zf,r[a])}function Ix(i,e,t){const n=this.cache,s=e.length,r=rl(t,s);nn(n,r)||(i.uniform1iv(this.addr,r),sn(n,r));for(let a=0;a!==s;++a)t.setTextureCube(e[a]||Jf,r[a])}function Ux(i,e,t){const n=this.cache,s=e.length,r=rl(t,s);nn(n,r)||(i.uniform1iv(this.addr,r),sn(n,r));for(let a=0;a!==s;++a)t.setTexture2DArray(e[a]||Kf,r[a])}function Nx(i){switch(i){case 5126:return gx;case 35664:return _x;case 35665:return vx;case 35666:return xx;case 35674:return yx;case 35675:return Mx;case 35676:return Sx;case 5124:case 35670:return bx;case 35667:case 35671:return Ex;case 35668:case 35672:return wx;case 35669:case 35673:return Tx;case 5125:return Ax;case 36294:return Cx;case 36295:return Rx;case 36296:return Px;case 35678:case 36198:case 36298:case 36306:case 35682:return Lx;case 35679:case 36299:case 36307:return Dx;case 35680:case 36300:case 36308:case 36293:return Ix;case 36289:case 36303:case 36311:case 36292:return Ux}}class Fx{constructor(e,t,n){this.id=e,this.addr=n,this.cache=[],this.type=t.type,this.setValue=mx(t.type)}}class Ox{constructor(e,t,n){this.id=e,this.addr=n,this.cache=[],this.type=t.type,this.size=t.size,this.setValue=Nx(t.type)}}class Bx{constructor(e){this.id=e,this.seq=[],this.map={}}setValue(e,t,n){const s=this.seq;for(let r=0,a=s.length;r!==a;++r){const o=s[r];o.setValue(e,t[o.id],n)}}}const tc=/(\w+)(\])?(\[|\.)?/g;function td(i,e){i.seq.push(e),i.map[e.id]=e}function zx(i,e,t){const n=i.name,s=n.length;for(tc.lastIndex=0;;){const r=tc.exec(n),a=tc.lastIndex;let o=r[1];const l=r[2]==="]",c=r[3];if(l&&(o=o|0),c===void 0||c==="["&&a+2===s){td(t,c===void 0?new Fx(o,i,e):new Ox(o,i,e));break}else{let h=t.map[o];h===void 0&&(h=new Bx(o),td(t,h)),t=h}}}class Fo{constructor(e,t){this.seq=[],this.map={};const n=e.getProgramParameter(t,e.ACTIVE_UNIFORMS);for(let s=0;s<n;++s){const r=e.getActiveUniform(t,s),a=e.getUniformLocation(t,r.name);zx(r,a,this)}}setValue(e,t,n,s){const r=this.map[t];r!==void 0&&r.setValue(e,n,s)}setOptional(e,t,n){const s=t[n];s!==void 0&&this.setValue(e,n,s)}static upload(e,t,n,s){for(let r=0,a=t.length;r!==a;++r){const o=t[r],l=n[o.id];l.needsUpdate!==!1&&o.setValue(e,l.value,s)}}static seqWithValue(e,t){const n=[];for(let s=0,r=e.length;s!==r;++s){const a=e[s];a.id in t&&n.push(a)}return n}}function nd(i,e,t){const n=i.createShader(e);return i.shaderSource(n,t),i.compileShader(n),n}const kx=37297;let Hx=0;function Vx(i,e){const t=i.split(`
`),n=[],s=Math.max(e-6,0),r=Math.min(e+6,t.length);for(let a=s;a<r;a++){const o=a+1;n.push(`${o===e?">":" "} ${o}: ${t[a]}`)}return n.join(`
`)}function Gx(i){const e=St.getPrimaries(St.workingColorSpace),t=St.getPrimaries(i);let n;switch(e===t?n="":e===Vo&&t===Ho?n="LinearDisplayP3ToLinearSRGB":e===Ho&&t===Vo&&(n="LinearSRGBToLinearDisplayP3"),i){case fs:case sl:return[n,"LinearTransferOETF"];case xi:case vu:return[n,"sRGBTransferOETF"];default:return console.warn("THREE.WebGLProgram: Unsupported color space:",i),[n,"LinearTransferOETF"]}}function id(i,e,t){const n=i.getShaderParameter(e,i.COMPILE_STATUS),s=i.getShaderInfoLog(e).trim();if(n&&s==="")return"";const r=/ERROR: 0:(\d+)/.exec(s);if(r){const a=parseInt(r[1]);return t.toUpperCase()+`

`+s+`

`+Vx(i.getShaderSource(e),a)}else return s}function Wx(i,e){const t=Gx(e);return`vec4 ${i}( vec4 value ) { return ${t[0]}( ${t[1]}( value ) ); }`}function Xx(i,e){let t;switch(e){case jm:t="Linear";break;case Km:t="Reinhard";break;case Zm:t="Cineon";break;case Ef:t="ACESFilmic";break;case Qm:t="AgX";break;case eg:t="Neutral";break;case Jm:t="Custom";break;default:console.warn("THREE.WebGLProgram: Unsupported toneMapping:",e),t="Linear"}return"vec3 "+i+"( vec3 color ) { return "+t+"ToneMapping( color ); }"}const mo=new k;function qx(){St.getLuminanceCoefficients(mo);const i=mo.x.toFixed(4),e=mo.y.toFixed(4),t=mo.z.toFixed(4);return["float luminance( const in vec3 rgb ) {",`	const vec3 weights = vec3( ${i}, ${e}, ${t} );`,"	return dot( weights, rgb );","}"].join(`
`)}function Yx(i){return[i.extensionClipCullDistance?"#extension GL_ANGLE_clip_cull_distance : require":"",i.extensionMultiDraw?"#extension GL_ANGLE_multi_draw : require":""].filter(ya).join(`
`)}function $x(i){const e=[];for(const t in i){const n=i[t];n!==!1&&e.push("#define "+t+" "+n)}return e.join(`
`)}function jx(i,e){const t={},n=i.getProgramParameter(e,i.ACTIVE_ATTRIBUTES);for(let s=0;s<n;s++){const r=i.getActiveAttrib(e,s),a=r.name;let o=1;r.type===i.FLOAT_MAT2&&(o=2),r.type===i.FLOAT_MAT3&&(o=3),r.type===i.FLOAT_MAT4&&(o=4),t[a]={type:r.type,location:i.getAttribLocation(e,a),locationSize:o}}return t}function ya(i){return i!==""}function sd(i,e){const t=e.numSpotLightShadows+e.numSpotLightMaps-e.numSpotLightShadowsWithMaps;return i.replace(/NUM_DIR_LIGHTS/g,e.numDirLights).replace(/NUM_SPOT_LIGHTS/g,e.numSpotLights).replace(/NUM_SPOT_LIGHT_MAPS/g,e.numSpotLightMaps).replace(/NUM_SPOT_LIGHT_COORDS/g,t).replace(/NUM_RECT_AREA_LIGHTS/g,e.numRectAreaLights).replace(/NUM_POINT_LIGHTS/g,e.numPointLights).replace(/NUM_HEMI_LIGHTS/g,e.numHemiLights).replace(/NUM_DIR_LIGHT_SHADOWS/g,e.numDirLightShadows).replace(/NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS/g,e.numSpotLightShadowsWithMaps).replace(/NUM_SPOT_LIGHT_SHADOWS/g,e.numSpotLightShadows).replace(/NUM_POINT_LIGHT_SHADOWS/g,e.numPointLightShadows)}function rd(i,e){return i.replace(/NUM_CLIPPING_PLANES/g,e.numClippingPlanes).replace(/UNION_CLIPPING_PLANES/g,e.numClippingPlanes-e.numClipIntersection)}const Kx=/^[ \t]*#include +<([\w\d./]+)>/gm;function Jc(i){return i.replace(Kx,Jx)}const Zx=new Map;function Jx(i,e){let t=st[e];if(t===void 0){const n=Zx.get(e);if(n!==void 0)t=st[n],console.warn('THREE.WebGLRenderer: Shader chunk "%s" has been deprecated. Use "%s" instead.',e,n);else throw new Error("Can not resolve #include <"+e+">")}return Jc(t)}const Qx=/#pragma unroll_loop_start\s+for\s*\(\s*int\s+i\s*=\s*(\d+)\s*;\s*i\s*<\s*(\d+)\s*;\s*i\s*\+\+\s*\)\s*{([\s\S]+?)}\s+#pragma unroll_loop_end/g;function ad(i){return i.replace(Qx,ey)}function ey(i,e,t,n){let s="";for(let r=parseInt(e);r<parseInt(t);r++)s+=n.replace(/\[\s*i\s*\]/g,"[ "+r+" ]").replace(/UNROLLED_LOOP_INDEX/g,r);return s}function od(i){let e=`precision ${i.precision} float;
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
#define LOW_PRECISION`),e}function ty(i){let e="SHADOWMAP_TYPE_BASIC";return i.shadowMapType===Mf?e="SHADOWMAP_TYPE_PCF":i.shadowMapType===Sf?e="SHADOWMAP_TYPE_PCF_SOFT":i.shadowMapType===Ui&&(e="SHADOWMAP_TYPE_VSM"),e}function ny(i){let e="ENVMAP_TYPE_CUBE";if(i.envMap)switch(i.envMapMode){case Or:case Br:e="ENVMAP_TYPE_CUBE";break;case il:e="ENVMAP_TYPE_CUBE_UV";break}return e}function iy(i){let e="ENVMAP_MODE_REFLECTION";if(i.envMap)switch(i.envMapMode){case Br:e="ENVMAP_MODE_REFRACTION";break}return e}function sy(i){let e="ENVMAP_BLENDING_NONE";if(i.envMap)switch(i.combine){case bf:e="ENVMAP_BLENDING_MULTIPLY";break;case Ym:e="ENVMAP_BLENDING_MIX";break;case $m:e="ENVMAP_BLENDING_ADD";break}return e}function ry(i){const e=i.envMapCubeUVHeight;if(e===null)return null;const t=Math.log2(e)-2,n=1/e;return{texelWidth:1/(3*Math.max(Math.pow(2,t),7*16)),texelHeight:n,maxMip:t}}function ay(i,e,t,n){const s=i.getContext(),r=t.defines;let a=t.vertexShader,o=t.fragmentShader;const l=ty(t),c=ny(t),u=iy(t),h=sy(t),d=ry(t),f=Yx(t),g=$x(r),v=s.createProgram();let m,p,S=t.glslVersion?"#version "+t.glslVersion+`
`:"";t.isRawShaderMaterial?(m=["#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,g].filter(ya).join(`
`),m.length>0&&(m+=`
`),p=["#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,g].filter(ya).join(`
`),p.length>0&&(p+=`
`)):(m=[od(t),"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,g,t.extensionClipCullDistance?"#define USE_CLIP_DISTANCE":"",t.batching?"#define USE_BATCHING":"",t.batchingColor?"#define USE_BATCHING_COLOR":"",t.instancing?"#define USE_INSTANCING":"",t.instancingColor?"#define USE_INSTANCING_COLOR":"",t.instancingMorph?"#define USE_INSTANCING_MORPH":"",t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.map?"#define USE_MAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+u:"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",t.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",t.displacementMap?"#define USE_DISPLACEMENTMAP":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.anisotropy?"#define USE_ANISOTROPY":"",t.anisotropyMap?"#define USE_ANISOTROPYMAP":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",t.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaHash?"#define USE_ALPHAHASH":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",t.mapUv?"#define MAP_UV "+t.mapUv:"",t.alphaMapUv?"#define ALPHAMAP_UV "+t.alphaMapUv:"",t.lightMapUv?"#define LIGHTMAP_UV "+t.lightMapUv:"",t.aoMapUv?"#define AOMAP_UV "+t.aoMapUv:"",t.emissiveMapUv?"#define EMISSIVEMAP_UV "+t.emissiveMapUv:"",t.bumpMapUv?"#define BUMPMAP_UV "+t.bumpMapUv:"",t.normalMapUv?"#define NORMALMAP_UV "+t.normalMapUv:"",t.displacementMapUv?"#define DISPLACEMENTMAP_UV "+t.displacementMapUv:"",t.metalnessMapUv?"#define METALNESSMAP_UV "+t.metalnessMapUv:"",t.roughnessMapUv?"#define ROUGHNESSMAP_UV "+t.roughnessMapUv:"",t.anisotropyMapUv?"#define ANISOTROPYMAP_UV "+t.anisotropyMapUv:"",t.clearcoatMapUv?"#define CLEARCOATMAP_UV "+t.clearcoatMapUv:"",t.clearcoatNormalMapUv?"#define CLEARCOAT_NORMALMAP_UV "+t.clearcoatNormalMapUv:"",t.clearcoatRoughnessMapUv?"#define CLEARCOAT_ROUGHNESSMAP_UV "+t.clearcoatRoughnessMapUv:"",t.iridescenceMapUv?"#define IRIDESCENCEMAP_UV "+t.iridescenceMapUv:"",t.iridescenceThicknessMapUv?"#define IRIDESCENCE_THICKNESSMAP_UV "+t.iridescenceThicknessMapUv:"",t.sheenColorMapUv?"#define SHEEN_COLORMAP_UV "+t.sheenColorMapUv:"",t.sheenRoughnessMapUv?"#define SHEEN_ROUGHNESSMAP_UV "+t.sheenRoughnessMapUv:"",t.specularMapUv?"#define SPECULARMAP_UV "+t.specularMapUv:"",t.specularColorMapUv?"#define SPECULAR_COLORMAP_UV "+t.specularColorMapUv:"",t.specularIntensityMapUv?"#define SPECULAR_INTENSITYMAP_UV "+t.specularIntensityMapUv:"",t.transmissionMapUv?"#define TRANSMISSIONMAP_UV "+t.transmissionMapUv:"",t.thicknessMapUv?"#define THICKNESSMAP_UV "+t.thicknessMapUv:"",t.vertexTangents&&t.flatShading===!1?"#define USE_TANGENT":"",t.vertexColors?"#define USE_COLOR":"",t.vertexAlphas?"#define USE_COLOR_ALPHA":"",t.vertexUv1s?"#define USE_UV1":"",t.vertexUv2s?"#define USE_UV2":"",t.vertexUv3s?"#define USE_UV3":"",t.pointsUvs?"#define USE_POINTS_UV":"",t.flatShading?"#define FLAT_SHADED":"",t.skinning?"#define USE_SKINNING":"",t.morphTargets?"#define USE_MORPHTARGETS":"",t.morphNormals&&t.flatShading===!1?"#define USE_MORPHNORMALS":"",t.morphColors?"#define USE_MORPHCOLORS":"",t.morphTargetsCount>0?"#define MORPHTARGETS_TEXTURE_STRIDE "+t.morphTextureStride:"",t.morphTargetsCount>0?"#define MORPHTARGETS_COUNT "+t.morphTargetsCount:"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+l:"",t.sizeAttenuation?"#define USE_SIZEATTENUATION":"",t.numLightProbes>0?"#define USE_LIGHT_PROBES":"",t.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"","uniform mat4 modelMatrix;","uniform mat4 modelViewMatrix;","uniform mat4 projectionMatrix;","uniform mat4 viewMatrix;","uniform mat3 normalMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;","#ifdef USE_INSTANCING","	attribute mat4 instanceMatrix;","#endif","#ifdef USE_INSTANCING_COLOR","	attribute vec3 instanceColor;","#endif","#ifdef USE_INSTANCING_MORPH","	uniform sampler2D morphTexture;","#endif","attribute vec3 position;","attribute vec3 normal;","attribute vec2 uv;","#ifdef USE_UV1","	attribute vec2 uv1;","#endif","#ifdef USE_UV2","	attribute vec2 uv2;","#endif","#ifdef USE_UV3","	attribute vec2 uv3;","#endif","#ifdef USE_TANGENT","	attribute vec4 tangent;","#endif","#if defined( USE_COLOR_ALPHA )","	attribute vec4 color;","#elif defined( USE_COLOR )","	attribute vec3 color;","#endif","#ifdef USE_SKINNING","	attribute vec4 skinIndex;","	attribute vec4 skinWeight;","#endif",`
`].filter(ya).join(`
`),p=[od(t),"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,g,t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.alphaToCoverage?"#define ALPHA_TO_COVERAGE":"",t.map?"#define USE_MAP":"",t.matcap?"#define USE_MATCAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+c:"",t.envMap?"#define "+u:"",t.envMap?"#define "+h:"",d?"#define CUBEUV_TEXEL_WIDTH "+d.texelWidth:"",d?"#define CUBEUV_TEXEL_HEIGHT "+d.texelHeight:"",d?"#define CUBEUV_MAX_MIP "+d.maxMip+".0":"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",t.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.anisotropy?"#define USE_ANISOTROPY":"",t.anisotropyMap?"#define USE_ANISOTROPYMAP":"",t.clearcoat?"#define USE_CLEARCOAT":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.dispersion?"#define USE_DISPERSION":"",t.iridescence?"#define USE_IRIDESCENCE":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",t.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaTest?"#define USE_ALPHATEST":"",t.alphaHash?"#define USE_ALPHAHASH":"",t.sheen?"#define USE_SHEEN":"",t.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.vertexTangents&&t.flatShading===!1?"#define USE_TANGENT":"",t.vertexColors||t.instancingColor||t.batchingColor?"#define USE_COLOR":"",t.vertexAlphas?"#define USE_COLOR_ALPHA":"",t.vertexUv1s?"#define USE_UV1":"",t.vertexUv2s?"#define USE_UV2":"",t.vertexUv3s?"#define USE_UV3":"",t.pointsUvs?"#define USE_POINTS_UV":"",t.gradientMap?"#define USE_GRADIENTMAP":"",t.flatShading?"#define FLAT_SHADED":"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+l:"",t.premultipliedAlpha?"#define PREMULTIPLIED_ALPHA":"",t.numLightProbes>0?"#define USE_LIGHT_PROBES":"",t.decodeVideoTexture?"#define DECODE_VIDEO_TEXTURE":"",t.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"","uniform mat4 viewMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;",t.toneMapping!==ls?"#define TONE_MAPPING":"",t.toneMapping!==ls?st.tonemapping_pars_fragment:"",t.toneMapping!==ls?Xx("toneMapping",t.toneMapping):"",t.dithering?"#define DITHERING":"",t.opaque?"#define OPAQUE":"",st.colorspace_pars_fragment,Wx("linearToOutputTexel",t.outputColorSpace),qx(),t.useDepthPacking?"#define DEPTH_PACKING "+t.depthPacking:"",`
`].filter(ya).join(`
`)),a=Jc(a),a=sd(a,t),a=rd(a,t),o=Jc(o),o=sd(o,t),o=rd(o,t),a=ad(a),o=ad(o),t.isRawShaderMaterial!==!0&&(S=`#version 300 es
`,m=[f,"#define attribute in","#define varying out","#define texture2D texture"].join(`
`)+`
`+m,p=["#define varying in",t.glslVersion===Mh?"":"layout(location = 0) out highp vec4 pc_fragColor;",t.glslVersion===Mh?"":"#define gl_FragColor pc_fragColor","#define gl_FragDepthEXT gl_FragDepth","#define texture2D texture","#define textureCube texture","#define texture2DProj textureProj","#define texture2DLodEXT textureLod","#define texture2DProjLodEXT textureProjLod","#define textureCubeLodEXT textureLod","#define texture2DGradEXT textureGrad","#define texture2DProjGradEXT textureProjGrad","#define textureCubeGradEXT textureGrad"].join(`
`)+`
`+p);const y=S+m+a,w=S+p+o,O=nd(s,s.VERTEX_SHADER,y),A=nd(s,s.FRAGMENT_SHADER,w);s.attachShader(v,O),s.attachShader(v,A),t.index0AttributeName!==void 0?s.bindAttribLocation(v,0,t.index0AttributeName):t.morphTargets===!0&&s.bindAttribLocation(v,0,"position"),s.linkProgram(v);function P(R){if(i.debug.checkShaderErrors){const j=s.getProgramInfoLog(v).trim(),z=s.getShaderInfoLog(O).trim(),K=s.getShaderInfoLog(A).trim();let X=!0,Q=!0;if(s.getProgramParameter(v,s.LINK_STATUS)===!1)if(X=!1,typeof i.debug.onShaderError=="function")i.debug.onShaderError(s,v,O,A);else{const Y=id(s,O,"vertex"),ne=id(s,A,"fragment");console.error("THREE.WebGLProgram: Shader Error "+s.getError()+" - VALIDATE_STATUS "+s.getProgramParameter(v,s.VALIDATE_STATUS)+`

Material Name: `+R.name+`
Material Type: `+R.type+`

Program Info Log: `+j+`
`+Y+`
`+ne)}else j!==""?console.warn("THREE.WebGLProgram: Program Info Log:",j):(z===""||K==="")&&(Q=!1);Q&&(R.diagnostics={runnable:X,programLog:j,vertexShader:{log:z,prefix:m},fragmentShader:{log:K,prefix:p}})}s.deleteShader(O),s.deleteShader(A),N=new Fo(s,v),b=jx(s,v)}let N;this.getUniforms=function(){return N===void 0&&P(this),N};let b;this.getAttributes=function(){return b===void 0&&P(this),b};let x=t.rendererExtensionParallelShaderCompile===!1;return this.isReady=function(){return x===!1&&(x=s.getProgramParameter(v,kx)),x},this.destroy=function(){n.releaseStatesOfProgram(this),s.deleteProgram(v),this.program=void 0},this.type=t.shaderType,this.name=t.shaderName,this.id=Hx++,this.cacheKey=e,this.usedTimes=1,this.program=v,this.vertexShader=O,this.fragmentShader=A,this}let oy=0;class ly{constructor(){this.shaderCache=new Map,this.materialCache=new Map}update(e){const t=e.vertexShader,n=e.fragmentShader,s=this._getShaderStage(t),r=this._getShaderStage(n),a=this._getShaderCacheForMaterial(e);return a.has(s)===!1&&(a.add(s),s.usedTimes++),a.has(r)===!1&&(a.add(r),r.usedTimes++),this}remove(e){const t=this.materialCache.get(e);for(const n of t)n.usedTimes--,n.usedTimes===0&&this.shaderCache.delete(n.code);return this.materialCache.delete(e),this}getVertexShaderID(e){return this._getShaderStage(e.vertexShader).id}getFragmentShaderID(e){return this._getShaderStage(e.fragmentShader).id}dispose(){this.shaderCache.clear(),this.materialCache.clear()}_getShaderCacheForMaterial(e){const t=this.materialCache;let n=t.get(e);return n===void 0&&(n=new Set,t.set(e,n)),n}_getShaderStage(e){const t=this.shaderCache;let n=t.get(e);return n===void 0&&(n=new cy(e),t.set(e,n)),n}}class cy{constructor(e){this.id=oy++,this.code=e,this.usedTimes=0}}function uy(i,e,t,n,s,r,a){const o=new yu,l=new ly,c=new Set,u=[],h=s.logarithmicDepthBuffer,d=s.vertexTextures;let f=s.precision;const g={MeshDepthMaterial:"depth",MeshDistanceMaterial:"distanceRGBA",MeshNormalMaterial:"normal",MeshBasicMaterial:"basic",MeshLambertMaterial:"lambert",MeshPhongMaterial:"phong",MeshToonMaterial:"toon",MeshStandardMaterial:"physical",MeshPhysicalMaterial:"physical",MeshMatcapMaterial:"matcap",LineBasicMaterial:"basic",LineDashedMaterial:"dashed",PointsMaterial:"points",ShadowMaterial:"shadow",SpriteMaterial:"sprite"};function v(b){return c.add(b),b===0?"uv":`uv${b}`}function m(b,x,R,j,z){const K=j.fog,X=z.geometry,Q=b.isMeshStandardMaterial?j.environment:null,Y=(b.isMeshStandardMaterial?t:e).get(b.envMap||Q),ne=Y&&Y.mapping===il?Y.image.height:null,ge=g[b.type];b.precision!==null&&(f=s.getMaxPrecision(b.precision),f!==b.precision&&console.warn("THREE.WebGLProgram.getParameters:",b.precision,"not supported, using",f,"instead."));const de=X.morphAttributes.position||X.morphAttributes.normal||X.morphAttributes.color,xe=de!==void 0?de.length:0;let we=0;X.morphAttributes.position!==void 0&&(we=1),X.morphAttributes.normal!==void 0&&(we=2),X.morphAttributes.color!==void 0&&(we=3);let ye,ie,ue,Me;if(ge){const ot=yi[ge];ye=ot.vertexShader,ie=ot.fragmentShader}else ye=b.vertexShader,ie=b.fragmentShader,l.update(b),ue=l.getVertexShaderID(b),Me=l.getFragmentShaderID(b);const fe=i.getRenderTarget(),ze=z.isInstancedMesh===!0,Ge=z.isBatchedMesh===!0,Fe=!!b.map,ft=!!b.matcap,U=!!Y,ht=!!b.aoMap,it=!!b.lightMap,lt=!!b.bumpMap,Oe=!!b.normalMap,bt=!!b.displacementMap,Ye=!!b.emissiveMap,Xe=!!b.metalnessMap,D=!!b.roughnessMap,E=b.anisotropy>0,J=b.clearcoat>0,le=b.dispersion>0,ee=b.iridescence>0,W=b.sheen>0,Ee=b.transmission>0,_e=E&&!!b.anisotropyMap,Ae=J&&!!b.clearcoatMap,Ke=J&&!!b.clearcoatNormalMap,me=J&&!!b.clearcoatRoughnessMap,Te=ee&&!!b.iridescenceMap,Ze=ee&&!!b.iridescenceThicknessMap,ke=W&&!!b.sheenColorMap,be=W&&!!b.sheenRoughnessMap,He=!!b.specularMap,F=!!b.specularColorMap,ce=!!b.specularIntensityMap,I=Ee&&!!b.transmissionMap,ae=Ee&&!!b.thicknessMap,se=!!b.gradientMap,re=!!b.alphaMap,ve=b.alphaTest>0,je=!!b.alphaHash,at=!!b.extensions;let gt=ls;b.toneMapped&&(fe===null||fe.isXRRenderTarget===!0)&&(gt=i.toneMapping);const Et={shaderID:ge,shaderType:b.type,shaderName:b.name,vertexShader:ye,fragmentShader:ie,defines:b.defines,customVertexShaderID:ue,customFragmentShaderID:Me,isRawShaderMaterial:b.isRawShaderMaterial===!0,glslVersion:b.glslVersion,precision:f,batching:Ge,batchingColor:Ge&&z._colorsTexture!==null,instancing:ze,instancingColor:ze&&z.instanceColor!==null,instancingMorph:ze&&z.morphTexture!==null,supportsVertexTextures:d,outputColorSpace:fe===null?i.outputColorSpace:fe.isXRRenderTarget===!0?fe.texture.colorSpace:fs,alphaToCoverage:!!b.alphaToCoverage,map:Fe,matcap:ft,envMap:U,envMapMode:U&&Y.mapping,envMapCubeUVHeight:ne,aoMap:ht,lightMap:it,bumpMap:lt,normalMap:Oe,displacementMap:d&&bt,emissiveMap:Ye,normalMapObjectSpace:Oe&&b.normalMapType===sg,normalMapTangentSpace:Oe&&b.normalMapType===Ff,metalnessMap:Xe,roughnessMap:D,anisotropy:E,anisotropyMap:_e,clearcoat:J,clearcoatMap:Ae,clearcoatNormalMap:Ke,clearcoatRoughnessMap:me,dispersion:le,iridescence:ee,iridescenceMap:Te,iridescenceThicknessMap:Ze,sheen:W,sheenColorMap:ke,sheenRoughnessMap:be,specularMap:He,specularColorMap:F,specularIntensityMap:ce,transmission:Ee,transmissionMap:I,thicknessMap:ae,gradientMap:se,opaque:b.transparent===!1&&b.blending===Cr&&b.alphaToCoverage===!1,alphaMap:re,alphaTest:ve,alphaHash:je,combine:b.combine,mapUv:Fe&&v(b.map.channel),aoMapUv:ht&&v(b.aoMap.channel),lightMapUv:it&&v(b.lightMap.channel),bumpMapUv:lt&&v(b.bumpMap.channel),normalMapUv:Oe&&v(b.normalMap.channel),displacementMapUv:bt&&v(b.displacementMap.channel),emissiveMapUv:Ye&&v(b.emissiveMap.channel),metalnessMapUv:Xe&&v(b.metalnessMap.channel),roughnessMapUv:D&&v(b.roughnessMap.channel),anisotropyMapUv:_e&&v(b.anisotropyMap.channel),clearcoatMapUv:Ae&&v(b.clearcoatMap.channel),clearcoatNormalMapUv:Ke&&v(b.clearcoatNormalMap.channel),clearcoatRoughnessMapUv:me&&v(b.clearcoatRoughnessMap.channel),iridescenceMapUv:Te&&v(b.iridescenceMap.channel),iridescenceThicknessMapUv:Ze&&v(b.iridescenceThicknessMap.channel),sheenColorMapUv:ke&&v(b.sheenColorMap.channel),sheenRoughnessMapUv:be&&v(b.sheenRoughnessMap.channel),specularMapUv:He&&v(b.specularMap.channel),specularColorMapUv:F&&v(b.specularColorMap.channel),specularIntensityMapUv:ce&&v(b.specularIntensityMap.channel),transmissionMapUv:I&&v(b.transmissionMap.channel),thicknessMapUv:ae&&v(b.thicknessMap.channel),alphaMapUv:re&&v(b.alphaMap.channel),vertexTangents:!!X.attributes.tangent&&(Oe||E),vertexColors:b.vertexColors,vertexAlphas:b.vertexColors===!0&&!!X.attributes.color&&X.attributes.color.itemSize===4,pointsUvs:z.isPoints===!0&&!!X.attributes.uv&&(Fe||re),fog:!!K,useFog:b.fog===!0,fogExp2:!!K&&K.isFogExp2,flatShading:b.flatShading===!0,sizeAttenuation:b.sizeAttenuation===!0,logarithmicDepthBuffer:h,skinning:z.isSkinnedMesh===!0,morphTargets:X.morphAttributes.position!==void 0,morphNormals:X.morphAttributes.normal!==void 0,morphColors:X.morphAttributes.color!==void 0,morphTargetsCount:xe,morphTextureStride:we,numDirLights:x.directional.length,numPointLights:x.point.length,numSpotLights:x.spot.length,numSpotLightMaps:x.spotLightMap.length,numRectAreaLights:x.rectArea.length,numHemiLights:x.hemi.length,numDirLightShadows:x.directionalShadowMap.length,numPointLightShadows:x.pointShadowMap.length,numSpotLightShadows:x.spotShadowMap.length,numSpotLightShadowsWithMaps:x.numSpotLightShadowsWithMaps,numLightProbes:x.numLightProbes,numClippingPlanes:a.numPlanes,numClipIntersection:a.numIntersection,dithering:b.dithering,shadowMapEnabled:i.shadowMap.enabled&&R.length>0,shadowMapType:i.shadowMap.type,toneMapping:gt,decodeVideoTexture:Fe&&b.map.isVideoTexture===!0&&St.getTransfer(b.map.colorSpace)===Ft,premultipliedAlpha:b.premultipliedAlpha,doubleSided:b.side===$n,flipSided:b.side===In,useDepthPacking:b.depthPacking>=0,depthPacking:b.depthPacking||0,index0AttributeName:b.index0AttributeName,extensionClipCullDistance:at&&b.extensions.clipCullDistance===!0&&n.has("WEBGL_clip_cull_distance"),extensionMultiDraw:(at&&b.extensions.multiDraw===!0||Ge)&&n.has("WEBGL_multi_draw"),rendererExtensionParallelShaderCompile:n.has("KHR_parallel_shader_compile"),customProgramCacheKey:b.customProgramCacheKey()};return Et.vertexUv1s=c.has(1),Et.vertexUv2s=c.has(2),Et.vertexUv3s=c.has(3),c.clear(),Et}function p(b){const x=[];if(b.shaderID?x.push(b.shaderID):(x.push(b.customVertexShaderID),x.push(b.customFragmentShaderID)),b.defines!==void 0)for(const R in b.defines)x.push(R),x.push(b.defines[R]);return b.isRawShaderMaterial===!1&&(S(x,b),y(x,b),x.push(i.outputColorSpace)),x.push(b.customProgramCacheKey),x.join()}function S(b,x){b.push(x.precision),b.push(x.outputColorSpace),b.push(x.envMapMode),b.push(x.envMapCubeUVHeight),b.push(x.mapUv),b.push(x.alphaMapUv),b.push(x.lightMapUv),b.push(x.aoMapUv),b.push(x.bumpMapUv),b.push(x.normalMapUv),b.push(x.displacementMapUv),b.push(x.emissiveMapUv),b.push(x.metalnessMapUv),b.push(x.roughnessMapUv),b.push(x.anisotropyMapUv),b.push(x.clearcoatMapUv),b.push(x.clearcoatNormalMapUv),b.push(x.clearcoatRoughnessMapUv),b.push(x.iridescenceMapUv),b.push(x.iridescenceThicknessMapUv),b.push(x.sheenColorMapUv),b.push(x.sheenRoughnessMapUv),b.push(x.specularMapUv),b.push(x.specularColorMapUv),b.push(x.specularIntensityMapUv),b.push(x.transmissionMapUv),b.push(x.thicknessMapUv),b.push(x.combine),b.push(x.fogExp2),b.push(x.sizeAttenuation),b.push(x.morphTargetsCount),b.push(x.morphAttributeCount),b.push(x.numDirLights),b.push(x.numPointLights),b.push(x.numSpotLights),b.push(x.numSpotLightMaps),b.push(x.numHemiLights),b.push(x.numRectAreaLights),b.push(x.numDirLightShadows),b.push(x.numPointLightShadows),b.push(x.numSpotLightShadows),b.push(x.numSpotLightShadowsWithMaps),b.push(x.numLightProbes),b.push(x.shadowMapType),b.push(x.toneMapping),b.push(x.numClippingPlanes),b.push(x.numClipIntersection),b.push(x.depthPacking)}function y(b,x){o.disableAll(),x.supportsVertexTextures&&o.enable(0),x.instancing&&o.enable(1),x.instancingColor&&o.enable(2),x.instancingMorph&&o.enable(3),x.matcap&&o.enable(4),x.envMap&&o.enable(5),x.normalMapObjectSpace&&o.enable(6),x.normalMapTangentSpace&&o.enable(7),x.clearcoat&&o.enable(8),x.iridescence&&o.enable(9),x.alphaTest&&o.enable(10),x.vertexColors&&o.enable(11),x.vertexAlphas&&o.enable(12),x.vertexUv1s&&o.enable(13),x.vertexUv2s&&o.enable(14),x.vertexUv3s&&o.enable(15),x.vertexTangents&&o.enable(16),x.anisotropy&&o.enable(17),x.alphaHash&&o.enable(18),x.batching&&o.enable(19),x.dispersion&&o.enable(20),x.batchingColor&&o.enable(21),b.push(o.mask),o.disableAll(),x.fog&&o.enable(0),x.useFog&&o.enable(1),x.flatShading&&o.enable(2),x.logarithmicDepthBuffer&&o.enable(3),x.skinning&&o.enable(4),x.morphTargets&&o.enable(5),x.morphNormals&&o.enable(6),x.morphColors&&o.enable(7),x.premultipliedAlpha&&o.enable(8),x.shadowMapEnabled&&o.enable(9),x.doubleSided&&o.enable(10),x.flipSided&&o.enable(11),x.useDepthPacking&&o.enable(12),x.dithering&&o.enable(13),x.transmission&&o.enable(14),x.sheen&&o.enable(15),x.opaque&&o.enable(16),x.pointsUvs&&o.enable(17),x.decodeVideoTexture&&o.enable(18),x.alphaToCoverage&&o.enable(19),b.push(o.mask)}function w(b){const x=g[b.type];let R;if(x){const j=yi[x];R=Yg.clone(j.uniforms)}else R=b.uniforms;return R}function O(b,x){let R;for(let j=0,z=u.length;j<z;j++){const K=u[j];if(K.cacheKey===x){R=K,++R.usedTimes;break}}return R===void 0&&(R=new ay(i,x,b,r),u.push(R)),R}function A(b){if(--b.usedTimes===0){const x=u.indexOf(b);u[x]=u[u.length-1],u.pop(),b.destroy()}}function P(b){l.remove(b)}function N(){l.dispose()}return{getParameters:m,getProgramCacheKey:p,getUniforms:w,acquireProgram:O,releaseProgram:A,releaseShaderCache:P,programs:u,dispose:N}}function hy(){let i=new WeakMap;function e(a){return i.has(a)}function t(a){let o=i.get(a);return o===void 0&&(o={},i.set(a,o)),o}function n(a){i.delete(a)}function s(a,o,l){i.get(a)[o]=l}function r(){i=new WeakMap}return{has:e,get:t,remove:n,update:s,dispose:r}}function dy(i,e){return i.groupOrder!==e.groupOrder?i.groupOrder-e.groupOrder:i.renderOrder!==e.renderOrder?i.renderOrder-e.renderOrder:i.material.id!==e.material.id?i.material.id-e.material.id:i.z!==e.z?i.z-e.z:i.id-e.id}function ld(i,e){return i.groupOrder!==e.groupOrder?i.groupOrder-e.groupOrder:i.renderOrder!==e.renderOrder?i.renderOrder-e.renderOrder:i.z!==e.z?e.z-i.z:i.id-e.id}function cd(){const i=[];let e=0;const t=[],n=[],s=[];function r(){e=0,t.length=0,n.length=0,s.length=0}function a(h,d,f,g,v,m){let p=i[e];return p===void 0?(p={id:h.id,object:h,geometry:d,material:f,groupOrder:g,renderOrder:h.renderOrder,z:v,group:m},i[e]=p):(p.id=h.id,p.object=h,p.geometry=d,p.material=f,p.groupOrder=g,p.renderOrder=h.renderOrder,p.z=v,p.group=m),e++,p}function o(h,d,f,g,v,m){const p=a(h,d,f,g,v,m);f.transmission>0?n.push(p):f.transparent===!0?s.push(p):t.push(p)}function l(h,d,f,g,v,m){const p=a(h,d,f,g,v,m);f.transmission>0?n.unshift(p):f.transparent===!0?s.unshift(p):t.unshift(p)}function c(h,d){t.length>1&&t.sort(h||dy),n.length>1&&n.sort(d||ld),s.length>1&&s.sort(d||ld)}function u(){for(let h=e,d=i.length;h<d;h++){const f=i[h];if(f.id===null)break;f.id=null,f.object=null,f.geometry=null,f.material=null,f.group=null}}return{opaque:t,transmissive:n,transparent:s,init:r,push:o,unshift:l,finish:u,sort:c}}function fy(){let i=new WeakMap;function e(n,s){const r=i.get(n);let a;return r===void 0?(a=new cd,i.set(n,[a])):s>=r.length?(a=new cd,r.push(a)):a=r[s],a}function t(){i=new WeakMap}return{get:e,dispose:t}}function py(){const i={};return{get:function(e){if(i[e.id]!==void 0)return i[e.id];let t;switch(e.type){case"DirectionalLight":t={direction:new k,color:new nt};break;case"SpotLight":t={position:new k,direction:new k,color:new nt,distance:0,coneCos:0,penumbraCos:0,decay:0};break;case"PointLight":t={position:new k,color:new nt,distance:0,decay:0};break;case"HemisphereLight":t={direction:new k,skyColor:new nt,groundColor:new nt};break;case"RectAreaLight":t={color:new nt,position:new k,halfWidth:new k,halfHeight:new k};break}return i[e.id]=t,t}}}function my(){const i={};return{get:function(e){if(i[e.id]!==void 0)return i[e.id];let t;switch(e.type){case"DirectionalLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new qe};break;case"SpotLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new qe};break;case"PointLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new qe,shadowCameraNear:1,shadowCameraFar:1e3};break}return i[e.id]=t,t}}}let gy=0;function _y(i,e){return(e.castShadow?2:0)-(i.castShadow?2:0)+(e.map?1:0)-(i.map?1:0)}function vy(i){const e=new py,t=my(),n={version:0,hash:{directionalLength:-1,pointLength:-1,spotLength:-1,rectAreaLength:-1,hemiLength:-1,numDirectionalShadows:-1,numPointShadows:-1,numSpotShadows:-1,numSpotMaps:-1,numLightProbes:-1},ambient:[0,0,0],probe:[],directional:[],directionalShadow:[],directionalShadowMap:[],directionalShadowMatrix:[],spot:[],spotLightMap:[],spotShadow:[],spotShadowMap:[],spotLightMatrix:[],rectArea:[],rectAreaLTC1:null,rectAreaLTC2:null,point:[],pointShadow:[],pointShadowMap:[],pointShadowMatrix:[],hemi:[],numSpotLightShadowsWithMaps:0,numLightProbes:0};for(let c=0;c<9;c++)n.probe.push(new k);const s=new k,r=new Ot,a=new Ot;function o(c){let u=0,h=0,d=0;for(let b=0;b<9;b++)n.probe[b].set(0,0,0);let f=0,g=0,v=0,m=0,p=0,S=0,y=0,w=0,O=0,A=0,P=0;c.sort(_y);for(let b=0,x=c.length;b<x;b++){const R=c[b],j=R.color,z=R.intensity,K=R.distance,X=R.shadow&&R.shadow.map?R.shadow.map.texture:null;if(R.isAmbientLight)u+=j.r*z,h+=j.g*z,d+=j.b*z;else if(R.isLightProbe){for(let Q=0;Q<9;Q++)n.probe[Q].addScaledVector(R.sh.coefficients[Q],z);P++}else if(R.isDirectionalLight){const Q=e.get(R);if(Q.color.copy(R.color).multiplyScalar(R.intensity),R.castShadow){const Y=R.shadow,ne=t.get(R);ne.shadowIntensity=Y.intensity,ne.shadowBias=Y.bias,ne.shadowNormalBias=Y.normalBias,ne.shadowRadius=Y.radius,ne.shadowMapSize=Y.mapSize,n.directionalShadow[f]=ne,n.directionalShadowMap[f]=X,n.directionalShadowMatrix[f]=R.shadow.matrix,S++}n.directional[f]=Q,f++}else if(R.isSpotLight){const Q=e.get(R);Q.position.setFromMatrixPosition(R.matrixWorld),Q.color.copy(j).multiplyScalar(z),Q.distance=K,Q.coneCos=Math.cos(R.angle),Q.penumbraCos=Math.cos(R.angle*(1-R.penumbra)),Q.decay=R.decay,n.spot[v]=Q;const Y=R.shadow;if(R.map&&(n.spotLightMap[O]=R.map,O++,Y.updateMatrices(R),R.castShadow&&A++),n.spotLightMatrix[v]=Y.matrix,R.castShadow){const ne=t.get(R);ne.shadowIntensity=Y.intensity,ne.shadowBias=Y.bias,ne.shadowNormalBias=Y.normalBias,ne.shadowRadius=Y.radius,ne.shadowMapSize=Y.mapSize,n.spotShadow[v]=ne,n.spotShadowMap[v]=X,w++}v++}else if(R.isRectAreaLight){const Q=e.get(R);Q.color.copy(j).multiplyScalar(z),Q.halfWidth.set(R.width*.5,0,0),Q.halfHeight.set(0,R.height*.5,0),n.rectArea[m]=Q,m++}else if(R.isPointLight){const Q=e.get(R);if(Q.color.copy(R.color).multiplyScalar(R.intensity),Q.distance=R.distance,Q.decay=R.decay,R.castShadow){const Y=R.shadow,ne=t.get(R);ne.shadowIntensity=Y.intensity,ne.shadowBias=Y.bias,ne.shadowNormalBias=Y.normalBias,ne.shadowRadius=Y.radius,ne.shadowMapSize=Y.mapSize,ne.shadowCameraNear=Y.camera.near,ne.shadowCameraFar=Y.camera.far,n.pointShadow[g]=ne,n.pointShadowMap[g]=X,n.pointShadowMatrix[g]=R.shadow.matrix,y++}n.point[g]=Q,g++}else if(R.isHemisphereLight){const Q=e.get(R);Q.skyColor.copy(R.color).multiplyScalar(z),Q.groundColor.copy(R.groundColor).multiplyScalar(z),n.hemi[p]=Q,p++}}m>0&&(i.has("OES_texture_float_linear")===!0?(n.rectAreaLTC1=Ce.LTC_FLOAT_1,n.rectAreaLTC2=Ce.LTC_FLOAT_2):(n.rectAreaLTC1=Ce.LTC_HALF_1,n.rectAreaLTC2=Ce.LTC_HALF_2)),n.ambient[0]=u,n.ambient[1]=h,n.ambient[2]=d;const N=n.hash;(N.directionalLength!==f||N.pointLength!==g||N.spotLength!==v||N.rectAreaLength!==m||N.hemiLength!==p||N.numDirectionalShadows!==S||N.numPointShadows!==y||N.numSpotShadows!==w||N.numSpotMaps!==O||N.numLightProbes!==P)&&(n.directional.length=f,n.spot.length=v,n.rectArea.length=m,n.point.length=g,n.hemi.length=p,n.directionalShadow.length=S,n.directionalShadowMap.length=S,n.pointShadow.length=y,n.pointShadowMap.length=y,n.spotShadow.length=w,n.spotShadowMap.length=w,n.directionalShadowMatrix.length=S,n.pointShadowMatrix.length=y,n.spotLightMatrix.length=w+O-A,n.spotLightMap.length=O,n.numSpotLightShadowsWithMaps=A,n.numLightProbes=P,N.directionalLength=f,N.pointLength=g,N.spotLength=v,N.rectAreaLength=m,N.hemiLength=p,N.numDirectionalShadows=S,N.numPointShadows=y,N.numSpotShadows=w,N.numSpotMaps=O,N.numLightProbes=P,n.version=gy++)}function l(c,u){let h=0,d=0,f=0,g=0,v=0;const m=u.matrixWorldInverse;for(let p=0,S=c.length;p<S;p++){const y=c[p];if(y.isDirectionalLight){const w=n.directional[h];w.direction.setFromMatrixPosition(y.matrixWorld),s.setFromMatrixPosition(y.target.matrixWorld),w.direction.sub(s),w.direction.transformDirection(m),h++}else if(y.isSpotLight){const w=n.spot[f];w.position.setFromMatrixPosition(y.matrixWorld),w.position.applyMatrix4(m),w.direction.setFromMatrixPosition(y.matrixWorld),s.setFromMatrixPosition(y.target.matrixWorld),w.direction.sub(s),w.direction.transformDirection(m),f++}else if(y.isRectAreaLight){const w=n.rectArea[g];w.position.setFromMatrixPosition(y.matrixWorld),w.position.applyMatrix4(m),a.identity(),r.copy(y.matrixWorld),r.premultiply(m),a.extractRotation(r),w.halfWidth.set(y.width*.5,0,0),w.halfHeight.set(0,y.height*.5,0),w.halfWidth.applyMatrix4(a),w.halfHeight.applyMatrix4(a),g++}else if(y.isPointLight){const w=n.point[d];w.position.setFromMatrixPosition(y.matrixWorld),w.position.applyMatrix4(m),d++}else if(y.isHemisphereLight){const w=n.hemi[v];w.direction.setFromMatrixPosition(y.matrixWorld),w.direction.transformDirection(m),v++}}}return{setup:o,setupView:l,state:n}}function ud(i){const e=new vy(i),t=[],n=[];function s(u){c.camera=u,t.length=0,n.length=0}function r(u){t.push(u)}function a(u){n.push(u)}function o(){e.setup(t)}function l(u){e.setupView(t,u)}const c={lightsArray:t,shadowsArray:n,camera:null,lights:e,transmissionRenderTarget:{}};return{init:s,state:c,setupLights:o,setupLightsView:l,pushLight:r,pushShadow:a}}function xy(i){let e=new WeakMap;function t(s,r=0){const a=e.get(s);let o;return a===void 0?(o=new ud(i),e.set(s,[o])):r>=a.length?(o=new ud(i),a.push(o)):o=a[r],o}function n(){e=new WeakMap}return{get:t,dispose:n}}class yy extends ps{constructor(e){super(),this.isMeshDepthMaterial=!0,this.type="MeshDepthMaterial",this.depthPacking=ng,this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.wireframe=!1,this.wireframeLinewidth=1,this.setValues(e)}copy(e){return super.copy(e),this.depthPacking=e.depthPacking,this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this}}class My extends ps{constructor(e){super(),this.isMeshDistanceMaterial=!0,this.type="MeshDistanceMaterial",this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.setValues(e)}copy(e){return super.copy(e),this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this}}const Sy=`void main() {
	gl_Position = vec4( position, 1.0 );
}`,by=`uniform sampler2D shadow_pass;
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
}`;function Ey(i,e,t){let n=new Mu;const s=new qe,r=new qe,a=new tn,o=new yy({depthPacking:ig}),l=new My,c={},u=t.maxTextureSize,h={[cs]:In,[In]:cs,[$n]:$n},d=new us({defines:{VSM_SAMPLES:8},uniforms:{shadow_pass:{value:null},resolution:{value:new qe},radius:{value:4}},vertexShader:Sy,fragmentShader:by}),f=d.clone();f.defines.HORIZONTAL_PASS=1;const g=new Xt;g.setAttribute("position",new ui(new Float32Array([-1,-1,.5,3,-1,.5,-1,3,.5]),3));const v=new gn(g,d),m=this;this.enabled=!1,this.autoUpdate=!0,this.needsUpdate=!1,this.type=Mf;let p=this.type;this.render=function(A,P,N){if(m.enabled===!1||m.autoUpdate===!1&&m.needsUpdate===!1||A.length===0)return;const b=i.getRenderTarget(),x=i.getActiveCubeFace(),R=i.getActiveMipmapLevel(),j=i.state;j.setBlending(os),j.buffers.color.setClear(1,1,1,1),j.buffers.depth.setTest(!0),j.setScissorTest(!1);const z=p!==Ui&&this.type===Ui,K=p===Ui&&this.type!==Ui;for(let X=0,Q=A.length;X<Q;X++){const Y=A[X],ne=Y.shadow;if(ne===void 0){console.warn("THREE.WebGLShadowMap:",Y,"has no shadow.");continue}if(ne.autoUpdate===!1&&ne.needsUpdate===!1)continue;s.copy(ne.mapSize);const ge=ne.getFrameExtents();if(s.multiply(ge),r.copy(ne.mapSize),(s.x>u||s.y>u)&&(s.x>u&&(r.x=Math.floor(u/ge.x),s.x=r.x*ge.x,ne.mapSize.x=r.x),s.y>u&&(r.y=Math.floor(u/ge.y),s.y=r.y*ge.y,ne.mapSize.y=r.y)),ne.map===null||z===!0||K===!0){const xe=this.type!==Ui?{minFilter:Kn,magFilter:Kn}:{};ne.map!==null&&ne.map.dispose(),ne.map=new Bs(s.x,s.y,xe),ne.map.texture.name=Y.name+".shadowMap",ne.camera.updateProjectionMatrix()}i.setRenderTarget(ne.map),i.clear();const de=ne.getViewportCount();for(let xe=0;xe<de;xe++){const we=ne.getViewport(xe);a.set(r.x*we.x,r.y*we.y,r.x*we.z,r.y*we.w),j.viewport(a),ne.updateMatrices(Y,xe),n=ne.getFrustum(),w(P,N,ne.camera,Y,this.type)}ne.isPointLightShadow!==!0&&this.type===Ui&&S(ne,N),ne.needsUpdate=!1}p=this.type,m.needsUpdate=!1,i.setRenderTarget(b,x,R)};function S(A,P){const N=e.update(v);d.defines.VSM_SAMPLES!==A.blurSamples&&(d.defines.VSM_SAMPLES=A.blurSamples,f.defines.VSM_SAMPLES=A.blurSamples,d.needsUpdate=!0,f.needsUpdate=!0),A.mapPass===null&&(A.mapPass=new Bs(s.x,s.y)),d.uniforms.shadow_pass.value=A.map.texture,d.uniforms.resolution.value=A.mapSize,d.uniforms.radius.value=A.radius,i.setRenderTarget(A.mapPass),i.clear(),i.renderBufferDirect(P,null,N,d,v,null),f.uniforms.shadow_pass.value=A.mapPass.texture,f.uniforms.resolution.value=A.mapSize,f.uniforms.radius.value=A.radius,i.setRenderTarget(A.map),i.clear(),i.renderBufferDirect(P,null,N,f,v,null)}function y(A,P,N,b){let x=null;const R=N.isPointLight===!0?A.customDistanceMaterial:A.customDepthMaterial;if(R!==void 0)x=R;else if(x=N.isPointLight===!0?l:o,i.localClippingEnabled&&P.clipShadows===!0&&Array.isArray(P.clippingPlanes)&&P.clippingPlanes.length!==0||P.displacementMap&&P.displacementScale!==0||P.alphaMap&&P.alphaTest>0||P.map&&P.alphaTest>0){const j=x.uuid,z=P.uuid;let K=c[j];K===void 0&&(K={},c[j]=K);let X=K[z];X===void 0&&(X=x.clone(),K[z]=X,P.addEventListener("dispose",O)),x=X}if(x.visible=P.visible,x.wireframe=P.wireframe,b===Ui?x.side=P.shadowSide!==null?P.shadowSide:P.side:x.side=P.shadowSide!==null?P.shadowSide:h[P.side],x.alphaMap=P.alphaMap,x.alphaTest=P.alphaTest,x.map=P.map,x.clipShadows=P.clipShadows,x.clippingPlanes=P.clippingPlanes,x.clipIntersection=P.clipIntersection,x.displacementMap=P.displacementMap,x.displacementScale=P.displacementScale,x.displacementBias=P.displacementBias,x.wireframeLinewidth=P.wireframeLinewidth,x.linewidth=P.linewidth,N.isPointLight===!0&&x.isMeshDistanceMaterial===!0){const j=i.properties.get(x);j.light=N}return x}function w(A,P,N,b,x){if(A.visible===!1)return;if(A.layers.test(P.layers)&&(A.isMesh||A.isLine||A.isPoints)&&(A.castShadow||A.receiveShadow&&x===Ui)&&(!A.frustumCulled||n.intersectsObject(A))){A.modelViewMatrix.multiplyMatrices(N.matrixWorldInverse,A.matrixWorld);const z=e.update(A),K=A.material;if(Array.isArray(K)){const X=z.groups;for(let Q=0,Y=X.length;Q<Y;Q++){const ne=X[Q],ge=K[ne.materialIndex];if(ge&&ge.visible){const de=y(A,ge,b,x);A.onBeforeShadow(i,A,P,N,z,de,ne),i.renderBufferDirect(N,null,z,de,A,ne),A.onAfterShadow(i,A,P,N,z,de,ne)}}}else if(K.visible){const X=y(A,K,b,x);A.onBeforeShadow(i,A,P,N,z,X,null),i.renderBufferDirect(N,null,z,X,A,null),A.onAfterShadow(i,A,P,N,z,X,null)}}const j=A.children;for(let z=0,K=j.length;z<K;z++)w(j[z],P,N,b,x)}function O(A){A.target.removeEventListener("dispose",O);for(const N in c){const b=c[N],x=A.target.uuid;x in b&&(b[x].dispose(),delete b[x])}}}function wy(i){function e(){let I=!1;const ae=new tn;let se=null;const re=new tn(0,0,0,0);return{setMask:function(ve){se!==ve&&!I&&(i.colorMask(ve,ve,ve,ve),se=ve)},setLocked:function(ve){I=ve},setClear:function(ve,je,at,gt,Et){Et===!0&&(ve*=gt,je*=gt,at*=gt),ae.set(ve,je,at,gt),re.equals(ae)===!1&&(i.clearColor(ve,je,at,gt),re.copy(ae))},reset:function(){I=!1,se=null,re.set(-1,0,0,0)}}}function t(){let I=!1,ae=null,se=null,re=null;return{setTest:function(ve){ve?Me(i.DEPTH_TEST):fe(i.DEPTH_TEST)},setMask:function(ve){ae!==ve&&!I&&(i.depthMask(ve),ae=ve)},setFunc:function(ve){if(se!==ve){switch(ve){case km:i.depthFunc(i.NEVER);break;case Hm:i.depthFunc(i.ALWAYS);break;case Vm:i.depthFunc(i.LESS);break;case zo:i.depthFunc(i.LEQUAL);break;case Gm:i.depthFunc(i.EQUAL);break;case Wm:i.depthFunc(i.GEQUAL);break;case Xm:i.depthFunc(i.GREATER);break;case qm:i.depthFunc(i.NOTEQUAL);break;default:i.depthFunc(i.LEQUAL)}se=ve}},setLocked:function(ve){I=ve},setClear:function(ve){re!==ve&&(i.clearDepth(ve),re=ve)},reset:function(){I=!1,ae=null,se=null,re=null}}}function n(){let I=!1,ae=null,se=null,re=null,ve=null,je=null,at=null,gt=null,Et=null;return{setTest:function(ot){I||(ot?Me(i.STENCIL_TEST):fe(i.STENCIL_TEST))},setMask:function(ot){ae!==ot&&!I&&(i.stencilMask(ot),ae=ot)},setFunc:function(ot,fn,Bt){(se!==ot||re!==fn||ve!==Bt)&&(i.stencilFunc(ot,fn,Bt),se=ot,re=fn,ve=Bt)},setOp:function(ot,fn,Bt){(je!==ot||at!==fn||gt!==Bt)&&(i.stencilOp(ot,fn,Bt),je=ot,at=fn,gt=Bt)},setLocked:function(ot){I=ot},setClear:function(ot){Et!==ot&&(i.clearStencil(ot),Et=ot)},reset:function(){I=!1,ae=null,se=null,re=null,ve=null,je=null,at=null,gt=null,Et=null}}}const s=new e,r=new t,a=new n,o=new WeakMap,l=new WeakMap;let c={},u={},h=new WeakMap,d=[],f=null,g=!1,v=null,m=null,p=null,S=null,y=null,w=null,O=null,A=new nt(0,0,0),P=0,N=!1,b=null,x=null,R=null,j=null,z=null;const K=i.getParameter(i.MAX_COMBINED_TEXTURE_IMAGE_UNITS);let X=!1,Q=0;const Y=i.getParameter(i.VERSION);Y.indexOf("WebGL")!==-1?(Q=parseFloat(/^WebGL (\d)/.exec(Y)[1]),X=Q>=1):Y.indexOf("OpenGL ES")!==-1&&(Q=parseFloat(/^OpenGL ES (\d)/.exec(Y)[1]),X=Q>=2);let ne=null,ge={};const de=i.getParameter(i.SCISSOR_BOX),xe=i.getParameter(i.VIEWPORT),we=new tn().fromArray(de),ye=new tn().fromArray(xe);function ie(I,ae,se,re){const ve=new Uint8Array(4),je=i.createTexture();i.bindTexture(I,je),i.texParameteri(I,i.TEXTURE_MIN_FILTER,i.NEAREST),i.texParameteri(I,i.TEXTURE_MAG_FILTER,i.NEAREST);for(let at=0;at<se;at++)I===i.TEXTURE_3D||I===i.TEXTURE_2D_ARRAY?i.texImage3D(ae,0,i.RGBA,1,1,re,0,i.RGBA,i.UNSIGNED_BYTE,ve):i.texImage2D(ae+at,0,i.RGBA,1,1,0,i.RGBA,i.UNSIGNED_BYTE,ve);return je}const ue={};ue[i.TEXTURE_2D]=ie(i.TEXTURE_2D,i.TEXTURE_2D,1),ue[i.TEXTURE_CUBE_MAP]=ie(i.TEXTURE_CUBE_MAP,i.TEXTURE_CUBE_MAP_POSITIVE_X,6),ue[i.TEXTURE_2D_ARRAY]=ie(i.TEXTURE_2D_ARRAY,i.TEXTURE_2D_ARRAY,1,1),ue[i.TEXTURE_3D]=ie(i.TEXTURE_3D,i.TEXTURE_3D,1,1),s.setClear(0,0,0,1),r.setClear(1),a.setClear(0),Me(i.DEPTH_TEST),r.setFunc(zo),lt(!1),Oe(gh),Me(i.CULL_FACE),ht(os);function Me(I){c[I]!==!0&&(i.enable(I),c[I]=!0)}function fe(I){c[I]!==!1&&(i.disable(I),c[I]=!1)}function ze(I,ae){return u[I]!==ae?(i.bindFramebuffer(I,ae),u[I]=ae,I===i.DRAW_FRAMEBUFFER&&(u[i.FRAMEBUFFER]=ae),I===i.FRAMEBUFFER&&(u[i.DRAW_FRAMEBUFFER]=ae),!0):!1}function Ge(I,ae){let se=d,re=!1;if(I){se=h.get(ae),se===void 0&&(se=[],h.set(ae,se));const ve=I.textures;if(se.length!==ve.length||se[0]!==i.COLOR_ATTACHMENT0){for(let je=0,at=ve.length;je<at;je++)se[je]=i.COLOR_ATTACHMENT0+je;se.length=ve.length,re=!0}}else se[0]!==i.BACK&&(se[0]=i.BACK,re=!0);re&&i.drawBuffers(se)}function Fe(I){return f!==I?(i.useProgram(I),f=I,!0):!1}const ft={[Rs]:i.FUNC_ADD,[bm]:i.FUNC_SUBTRACT,[Em]:i.FUNC_REVERSE_SUBTRACT};ft[wm]=i.MIN,ft[Tm]=i.MAX;const U={[Am]:i.ZERO,[Cm]:i.ONE,[Rm]:i.SRC_COLOR,[vc]:i.SRC_ALPHA,[Nm]:i.SRC_ALPHA_SATURATE,[Im]:i.DST_COLOR,[Lm]:i.DST_ALPHA,[Pm]:i.ONE_MINUS_SRC_COLOR,[xc]:i.ONE_MINUS_SRC_ALPHA,[Um]:i.ONE_MINUS_DST_COLOR,[Dm]:i.ONE_MINUS_DST_ALPHA,[Fm]:i.CONSTANT_COLOR,[Om]:i.ONE_MINUS_CONSTANT_COLOR,[Bm]:i.CONSTANT_ALPHA,[zm]:i.ONE_MINUS_CONSTANT_ALPHA};function ht(I,ae,se,re,ve,je,at,gt,Et,ot){if(I===os){g===!0&&(fe(i.BLEND),g=!1);return}if(g===!1&&(Me(i.BLEND),g=!0),I!==Sm){if(I!==v||ot!==N){if((m!==Rs||y!==Rs)&&(i.blendEquation(i.FUNC_ADD),m=Rs,y=Rs),ot)switch(I){case Cr:i.blendFuncSeparate(i.ONE,i.ONE_MINUS_SRC_ALPHA,i.ONE,i.ONE_MINUS_SRC_ALPHA);break;case _h:i.blendFunc(i.ONE,i.ONE);break;case vh:i.blendFuncSeparate(i.ZERO,i.ONE_MINUS_SRC_COLOR,i.ZERO,i.ONE);break;case xh:i.blendFuncSeparate(i.ZERO,i.SRC_COLOR,i.ZERO,i.SRC_ALPHA);break;default:console.error("THREE.WebGLState: Invalid blending: ",I);break}else switch(I){case Cr:i.blendFuncSeparate(i.SRC_ALPHA,i.ONE_MINUS_SRC_ALPHA,i.ONE,i.ONE_MINUS_SRC_ALPHA);break;case _h:i.blendFunc(i.SRC_ALPHA,i.ONE);break;case vh:i.blendFuncSeparate(i.ZERO,i.ONE_MINUS_SRC_COLOR,i.ZERO,i.ONE);break;case xh:i.blendFunc(i.ZERO,i.SRC_COLOR);break;default:console.error("THREE.WebGLState: Invalid blending: ",I);break}p=null,S=null,w=null,O=null,A.set(0,0,0),P=0,v=I,N=ot}return}ve=ve||ae,je=je||se,at=at||re,(ae!==m||ve!==y)&&(i.blendEquationSeparate(ft[ae],ft[ve]),m=ae,y=ve),(se!==p||re!==S||je!==w||at!==O)&&(i.blendFuncSeparate(U[se],U[re],U[je],U[at]),p=se,S=re,w=je,O=at),(gt.equals(A)===!1||Et!==P)&&(i.blendColor(gt.r,gt.g,gt.b,Et),A.copy(gt),P=Et),v=I,N=!1}function it(I,ae){I.side===$n?fe(i.CULL_FACE):Me(i.CULL_FACE);let se=I.side===In;ae&&(se=!se),lt(se),I.blending===Cr&&I.transparent===!1?ht(os):ht(I.blending,I.blendEquation,I.blendSrc,I.blendDst,I.blendEquationAlpha,I.blendSrcAlpha,I.blendDstAlpha,I.blendColor,I.blendAlpha,I.premultipliedAlpha),r.setFunc(I.depthFunc),r.setTest(I.depthTest),r.setMask(I.depthWrite),s.setMask(I.colorWrite);const re=I.stencilWrite;a.setTest(re),re&&(a.setMask(I.stencilWriteMask),a.setFunc(I.stencilFunc,I.stencilRef,I.stencilFuncMask),a.setOp(I.stencilFail,I.stencilZFail,I.stencilZPass)),Ye(I.polygonOffset,I.polygonOffsetFactor,I.polygonOffsetUnits),I.alphaToCoverage===!0?Me(i.SAMPLE_ALPHA_TO_COVERAGE):fe(i.SAMPLE_ALPHA_TO_COVERAGE)}function lt(I){b!==I&&(I?i.frontFace(i.CW):i.frontFace(i.CCW),b=I)}function Oe(I){I!==ym?(Me(i.CULL_FACE),I!==x&&(I===gh?i.cullFace(i.BACK):I===Mm?i.cullFace(i.FRONT):i.cullFace(i.FRONT_AND_BACK))):fe(i.CULL_FACE),x=I}function bt(I){I!==R&&(X&&i.lineWidth(I),R=I)}function Ye(I,ae,se){I?(Me(i.POLYGON_OFFSET_FILL),(j!==ae||z!==se)&&(i.polygonOffset(ae,se),j=ae,z=se)):fe(i.POLYGON_OFFSET_FILL)}function Xe(I){I?Me(i.SCISSOR_TEST):fe(i.SCISSOR_TEST)}function D(I){I===void 0&&(I=i.TEXTURE0+K-1),ne!==I&&(i.activeTexture(I),ne=I)}function E(I,ae,se){se===void 0&&(ne===null?se=i.TEXTURE0+K-1:se=ne);let re=ge[se];re===void 0&&(re={type:void 0,texture:void 0},ge[se]=re),(re.type!==I||re.texture!==ae)&&(ne!==se&&(i.activeTexture(se),ne=se),i.bindTexture(I,ae||ue[I]),re.type=I,re.texture=ae)}function J(){const I=ge[ne];I!==void 0&&I.type!==void 0&&(i.bindTexture(I.type,null),I.type=void 0,I.texture=void 0)}function le(){try{i.compressedTexImage2D.apply(i,arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function ee(){try{i.compressedTexImage3D.apply(i,arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function W(){try{i.texSubImage2D.apply(i,arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function Ee(){try{i.texSubImage3D.apply(i,arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function _e(){try{i.compressedTexSubImage2D.apply(i,arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function Ae(){try{i.compressedTexSubImage3D.apply(i,arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function Ke(){try{i.texStorage2D.apply(i,arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function me(){try{i.texStorage3D.apply(i,arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function Te(){try{i.texImage2D.apply(i,arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function Ze(){try{i.texImage3D.apply(i,arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function ke(I){we.equals(I)===!1&&(i.scissor(I.x,I.y,I.z,I.w),we.copy(I))}function be(I){ye.equals(I)===!1&&(i.viewport(I.x,I.y,I.z,I.w),ye.copy(I))}function He(I,ae){let se=l.get(ae);se===void 0&&(se=new WeakMap,l.set(ae,se));let re=se.get(I);re===void 0&&(re=i.getUniformBlockIndex(ae,I.name),se.set(I,re))}function F(I,ae){const re=l.get(ae).get(I);o.get(ae)!==re&&(i.uniformBlockBinding(ae,re,I.__bindingPointIndex),o.set(ae,re))}function ce(){i.disable(i.BLEND),i.disable(i.CULL_FACE),i.disable(i.DEPTH_TEST),i.disable(i.POLYGON_OFFSET_FILL),i.disable(i.SCISSOR_TEST),i.disable(i.STENCIL_TEST),i.disable(i.SAMPLE_ALPHA_TO_COVERAGE),i.blendEquation(i.FUNC_ADD),i.blendFunc(i.ONE,i.ZERO),i.blendFuncSeparate(i.ONE,i.ZERO,i.ONE,i.ZERO),i.blendColor(0,0,0,0),i.colorMask(!0,!0,!0,!0),i.clearColor(0,0,0,0),i.depthMask(!0),i.depthFunc(i.LESS),i.clearDepth(1),i.stencilMask(4294967295),i.stencilFunc(i.ALWAYS,0,4294967295),i.stencilOp(i.KEEP,i.KEEP,i.KEEP),i.clearStencil(0),i.cullFace(i.BACK),i.frontFace(i.CCW),i.polygonOffset(0,0),i.activeTexture(i.TEXTURE0),i.bindFramebuffer(i.FRAMEBUFFER,null),i.bindFramebuffer(i.DRAW_FRAMEBUFFER,null),i.bindFramebuffer(i.READ_FRAMEBUFFER,null),i.useProgram(null),i.lineWidth(1),i.scissor(0,0,i.canvas.width,i.canvas.height),i.viewport(0,0,i.canvas.width,i.canvas.height),c={},ne=null,ge={},u={},h=new WeakMap,d=[],f=null,g=!1,v=null,m=null,p=null,S=null,y=null,w=null,O=null,A=new nt(0,0,0),P=0,N=!1,b=null,x=null,R=null,j=null,z=null,we.set(0,0,i.canvas.width,i.canvas.height),ye.set(0,0,i.canvas.width,i.canvas.height),s.reset(),r.reset(),a.reset()}return{buffers:{color:s,depth:r,stencil:a},enable:Me,disable:fe,bindFramebuffer:ze,drawBuffers:Ge,useProgram:Fe,setBlending:ht,setMaterial:it,setFlipSided:lt,setCullFace:Oe,setLineWidth:bt,setPolygonOffset:Ye,setScissorTest:Xe,activeTexture:D,bindTexture:E,unbindTexture:J,compressedTexImage2D:le,compressedTexImage3D:ee,texImage2D:Te,texImage3D:Ze,updateUBOMapping:He,uniformBlockBinding:F,texStorage2D:Ke,texStorage3D:me,texSubImage2D:W,texSubImage3D:Ee,compressedTexSubImage2D:_e,compressedTexSubImage3D:Ae,scissor:ke,viewport:be,reset:ce}}function hd(i,e,t,n){const s=Ty(n);switch(t){case Rf:return i*e;case Lf:return i*e;case Df:return i*e*2;case If:return i*e/s.components*s.byteLength;case mu:return i*e/s.components*s.byteLength;case Uf:return i*e*2/s.components*s.byteLength;case gu:return i*e*2/s.components*s.byteLength;case Pf:return i*e*3/s.components*s.byteLength;case ci:return i*e*4/s.components*s.byteLength;case _u:return i*e*4/s.components*s.byteLength;case Lo:case Do:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*8;case Io:case Uo:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*16;case wc:case Ac:return Math.max(i,16)*Math.max(e,8)/4;case Ec:case Tc:return Math.max(i,8)*Math.max(e,8)/2;case Cc:case Rc:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*8;case Pc:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*16;case Lc:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*16;case Dc:return Math.floor((i+4)/5)*Math.floor((e+3)/4)*16;case Ic:return Math.floor((i+4)/5)*Math.floor((e+4)/5)*16;case Uc:return Math.floor((i+5)/6)*Math.floor((e+4)/5)*16;case Nc:return Math.floor((i+5)/6)*Math.floor((e+5)/6)*16;case Fc:return Math.floor((i+7)/8)*Math.floor((e+4)/5)*16;case Oc:return Math.floor((i+7)/8)*Math.floor((e+5)/6)*16;case Bc:return Math.floor((i+7)/8)*Math.floor((e+7)/8)*16;case zc:return Math.floor((i+9)/10)*Math.floor((e+4)/5)*16;case kc:return Math.floor((i+9)/10)*Math.floor((e+5)/6)*16;case Hc:return Math.floor((i+9)/10)*Math.floor((e+7)/8)*16;case Vc:return Math.floor((i+9)/10)*Math.floor((e+9)/10)*16;case Gc:return Math.floor((i+11)/12)*Math.floor((e+9)/10)*16;case Wc:return Math.floor((i+11)/12)*Math.floor((e+11)/12)*16;case No:case Xc:case qc:return Math.ceil(i/4)*Math.ceil(e/4)*16;case Nf:case Yc:return Math.ceil(i/4)*Math.ceil(e/4)*8;case $c:case jc:return Math.ceil(i/4)*Math.ceil(e/4)*16}throw new Error(`Unable to determine texture byte length for ${t} format.`)}function Ty(i){switch(i){case Gi:case Tf:return{byteLength:1,components:1};case Ca:case Af:case Ia:return{byteLength:2,components:1};case fu:case pu:return{byteLength:2,components:4};case Os:case du:case Fi:return{byteLength:4,components:1};case Cf:return{byteLength:4,components:3}}throw new Error(`Unknown texture type ${i}.`)}function Ay(i,e,t,n,s,r,a){const o=e.has("WEBGL_multisampled_render_to_texture")?e.get("WEBGL_multisampled_render_to_texture"):null,l=typeof navigator>"u"?!1:/OculusBrowser/g.test(navigator.userAgent),c=new qe,u=new WeakMap;let h;const d=new WeakMap;let f=!1;try{f=typeof OffscreenCanvas<"u"&&new OffscreenCanvas(1,1).getContext("2d")!==null}catch{}function g(D,E){return f?new OffscreenCanvas(D,E):Wo("canvas")}function v(D,E,J){let le=1;const ee=Xe(D);if((ee.width>J||ee.height>J)&&(le=J/Math.max(ee.width,ee.height)),le<1)if(typeof HTMLImageElement<"u"&&D instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&D instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&D instanceof ImageBitmap||typeof VideoFrame<"u"&&D instanceof VideoFrame){const W=Math.floor(le*ee.width),Ee=Math.floor(le*ee.height);h===void 0&&(h=g(W,Ee));const _e=E?g(W,Ee):h;return _e.width=W,_e.height=Ee,_e.getContext("2d").drawImage(D,0,0,W,Ee),console.warn("THREE.WebGLRenderer: Texture has been resized from ("+ee.width+"x"+ee.height+") to ("+W+"x"+Ee+")."),_e}else return"data"in D&&console.warn("THREE.WebGLRenderer: Image in DataTexture is too big ("+ee.width+"x"+ee.height+")."),D;return D}function m(D){return D.generateMipmaps&&D.minFilter!==Kn&&D.minFilter!==ai}function p(D){i.generateMipmap(D)}function S(D,E,J,le,ee=!1){if(D!==null){if(i[D]!==void 0)return i[D];console.warn("THREE.WebGLRenderer: Attempt to use non-existing WebGL internal format '"+D+"'")}let W=E;if(E===i.RED&&(J===i.FLOAT&&(W=i.R32F),J===i.HALF_FLOAT&&(W=i.R16F),J===i.UNSIGNED_BYTE&&(W=i.R8)),E===i.RED_INTEGER&&(J===i.UNSIGNED_BYTE&&(W=i.R8UI),J===i.UNSIGNED_SHORT&&(W=i.R16UI),J===i.UNSIGNED_INT&&(W=i.R32UI),J===i.BYTE&&(W=i.R8I),J===i.SHORT&&(W=i.R16I),J===i.INT&&(W=i.R32I)),E===i.RG&&(J===i.FLOAT&&(W=i.RG32F),J===i.HALF_FLOAT&&(W=i.RG16F),J===i.UNSIGNED_BYTE&&(W=i.RG8)),E===i.RG_INTEGER&&(J===i.UNSIGNED_BYTE&&(W=i.RG8UI),J===i.UNSIGNED_SHORT&&(W=i.RG16UI),J===i.UNSIGNED_INT&&(W=i.RG32UI),J===i.BYTE&&(W=i.RG8I),J===i.SHORT&&(W=i.RG16I),J===i.INT&&(W=i.RG32I)),E===i.RGB&&J===i.UNSIGNED_INT_5_9_9_9_REV&&(W=i.RGB9_E5),E===i.RGBA){const Ee=ee?ko:St.getTransfer(le);J===i.FLOAT&&(W=i.RGBA32F),J===i.HALF_FLOAT&&(W=i.RGBA16F),J===i.UNSIGNED_BYTE&&(W=Ee===Ft?i.SRGB8_ALPHA8:i.RGBA8),J===i.UNSIGNED_SHORT_4_4_4_4&&(W=i.RGBA4),J===i.UNSIGNED_SHORT_5_5_5_1&&(W=i.RGB5_A1)}return(W===i.R16F||W===i.R32F||W===i.RG16F||W===i.RG32F||W===i.RGBA16F||W===i.RGBA32F)&&e.get("EXT_color_buffer_float"),W}function y(D,E){let J;return D?E===null||E===Os||E===zr?J=i.DEPTH24_STENCIL8:E===Fi?J=i.DEPTH32F_STENCIL8:E===Ca&&(J=i.DEPTH24_STENCIL8,console.warn("DepthTexture: 16 bit depth attachment is not supported with stencil. Using 24-bit attachment.")):E===null||E===Os||E===zr?J=i.DEPTH_COMPONENT24:E===Fi?J=i.DEPTH_COMPONENT32F:E===Ca&&(J=i.DEPTH_COMPONENT16),J}function w(D,E){return m(D)===!0||D.isFramebufferTexture&&D.minFilter!==Kn&&D.minFilter!==ai?Math.log2(Math.max(E.width,E.height))+1:D.mipmaps!==void 0&&D.mipmaps.length>0?D.mipmaps.length:D.isCompressedTexture&&Array.isArray(D.image)?E.mipmaps.length:1}function O(D){const E=D.target;E.removeEventListener("dispose",O),P(E),E.isVideoTexture&&u.delete(E)}function A(D){const E=D.target;E.removeEventListener("dispose",A),b(E)}function P(D){const E=n.get(D);if(E.__webglInit===void 0)return;const J=D.source,le=d.get(J);if(le){const ee=le[E.__cacheKey];ee.usedTimes--,ee.usedTimes===0&&N(D),Object.keys(le).length===0&&d.delete(J)}n.remove(D)}function N(D){const E=n.get(D);i.deleteTexture(E.__webglTexture);const J=D.source,le=d.get(J);delete le[E.__cacheKey],a.memory.textures--}function b(D){const E=n.get(D);if(D.depthTexture&&D.depthTexture.dispose(),D.isWebGLCubeRenderTarget)for(let le=0;le<6;le++){if(Array.isArray(E.__webglFramebuffer[le]))for(let ee=0;ee<E.__webglFramebuffer[le].length;ee++)i.deleteFramebuffer(E.__webglFramebuffer[le][ee]);else i.deleteFramebuffer(E.__webglFramebuffer[le]);E.__webglDepthbuffer&&i.deleteRenderbuffer(E.__webglDepthbuffer[le])}else{if(Array.isArray(E.__webglFramebuffer))for(let le=0;le<E.__webglFramebuffer.length;le++)i.deleteFramebuffer(E.__webglFramebuffer[le]);else i.deleteFramebuffer(E.__webglFramebuffer);if(E.__webglDepthbuffer&&i.deleteRenderbuffer(E.__webglDepthbuffer),E.__webglMultisampledFramebuffer&&i.deleteFramebuffer(E.__webglMultisampledFramebuffer),E.__webglColorRenderbuffer)for(let le=0;le<E.__webglColorRenderbuffer.length;le++)E.__webglColorRenderbuffer[le]&&i.deleteRenderbuffer(E.__webglColorRenderbuffer[le]);E.__webglDepthRenderbuffer&&i.deleteRenderbuffer(E.__webglDepthRenderbuffer)}const J=D.textures;for(let le=0,ee=J.length;le<ee;le++){const W=n.get(J[le]);W.__webglTexture&&(i.deleteTexture(W.__webglTexture),a.memory.textures--),n.remove(J[le])}n.remove(D)}let x=0;function R(){x=0}function j(){const D=x;return D>=s.maxTextures&&console.warn("THREE.WebGLTextures: Trying to use "+D+" texture units while this GPU supports only "+s.maxTextures),x+=1,D}function z(D){const E=[];return E.push(D.wrapS),E.push(D.wrapT),E.push(D.wrapR||0),E.push(D.magFilter),E.push(D.minFilter),E.push(D.anisotropy),E.push(D.internalFormat),E.push(D.format),E.push(D.type),E.push(D.generateMipmaps),E.push(D.premultiplyAlpha),E.push(D.flipY),E.push(D.unpackAlignment),E.push(D.colorSpace),E.join()}function K(D,E){const J=n.get(D);if(D.isVideoTexture&&bt(D),D.isRenderTargetTexture===!1&&D.version>0&&J.__version!==D.version){const le=D.image;if(le===null)console.warn("THREE.WebGLRenderer: Texture marked for update but no image data found.");else if(le.complete===!1)console.warn("THREE.WebGLRenderer: Texture marked for update but image is incomplete");else{ye(J,D,E);return}}t.bindTexture(i.TEXTURE_2D,J.__webglTexture,i.TEXTURE0+E)}function X(D,E){const J=n.get(D);if(D.version>0&&J.__version!==D.version){ye(J,D,E);return}t.bindTexture(i.TEXTURE_2D_ARRAY,J.__webglTexture,i.TEXTURE0+E)}function Q(D,E){const J=n.get(D);if(D.version>0&&J.__version!==D.version){ye(J,D,E);return}t.bindTexture(i.TEXTURE_3D,J.__webglTexture,i.TEXTURE0+E)}function Y(D,E){const J=n.get(D);if(D.version>0&&J.__version!==D.version){ie(J,D,E);return}t.bindTexture(i.TEXTURE_CUBE_MAP,J.__webglTexture,i.TEXTURE0+E)}const ne={[Sc]:i.REPEAT,[Ds]:i.CLAMP_TO_EDGE,[bc]:i.MIRRORED_REPEAT},ge={[Kn]:i.NEAREST,[tg]:i.NEAREST_MIPMAP_NEAREST,[Ya]:i.NEAREST_MIPMAP_LINEAR,[ai]:i.LINEAR,[Ll]:i.LINEAR_MIPMAP_NEAREST,[Is]:i.LINEAR_MIPMAP_LINEAR},de={[rg]:i.NEVER,[hg]:i.ALWAYS,[ag]:i.LESS,[Of]:i.LEQUAL,[og]:i.EQUAL,[ug]:i.GEQUAL,[lg]:i.GREATER,[cg]:i.NOTEQUAL};function xe(D,E){if(E.type===Fi&&e.has("OES_texture_float_linear")===!1&&(E.magFilter===ai||E.magFilter===Ll||E.magFilter===Ya||E.magFilter===Is||E.minFilter===ai||E.minFilter===Ll||E.minFilter===Ya||E.minFilter===Is)&&console.warn("THREE.WebGLRenderer: Unable to use linear filtering with floating point textures. OES_texture_float_linear not supported on this device."),i.texParameteri(D,i.TEXTURE_WRAP_S,ne[E.wrapS]),i.texParameteri(D,i.TEXTURE_WRAP_T,ne[E.wrapT]),(D===i.TEXTURE_3D||D===i.TEXTURE_2D_ARRAY)&&i.texParameteri(D,i.TEXTURE_WRAP_R,ne[E.wrapR]),i.texParameteri(D,i.TEXTURE_MAG_FILTER,ge[E.magFilter]),i.texParameteri(D,i.TEXTURE_MIN_FILTER,ge[E.minFilter]),E.compareFunction&&(i.texParameteri(D,i.TEXTURE_COMPARE_MODE,i.COMPARE_REF_TO_TEXTURE),i.texParameteri(D,i.TEXTURE_COMPARE_FUNC,de[E.compareFunction])),e.has("EXT_texture_filter_anisotropic")===!0){if(E.magFilter===Kn||E.minFilter!==Ya&&E.minFilter!==Is||E.type===Fi&&e.has("OES_texture_float_linear")===!1)return;if(E.anisotropy>1||n.get(E).__currentAnisotropy){const J=e.get("EXT_texture_filter_anisotropic");i.texParameterf(D,J.TEXTURE_MAX_ANISOTROPY_EXT,Math.min(E.anisotropy,s.getMaxAnisotropy())),n.get(E).__currentAnisotropy=E.anisotropy}}}function we(D,E){let J=!1;D.__webglInit===void 0&&(D.__webglInit=!0,E.addEventListener("dispose",O));const le=E.source;let ee=d.get(le);ee===void 0&&(ee={},d.set(le,ee));const W=z(E);if(W!==D.__cacheKey){ee[W]===void 0&&(ee[W]={texture:i.createTexture(),usedTimes:0},a.memory.textures++,J=!0),ee[W].usedTimes++;const Ee=ee[D.__cacheKey];Ee!==void 0&&(ee[D.__cacheKey].usedTimes--,Ee.usedTimes===0&&N(E)),D.__cacheKey=W,D.__webglTexture=ee[W].texture}return J}function ye(D,E,J){let le=i.TEXTURE_2D;(E.isDataArrayTexture||E.isCompressedArrayTexture)&&(le=i.TEXTURE_2D_ARRAY),E.isData3DTexture&&(le=i.TEXTURE_3D);const ee=we(D,E),W=E.source;t.bindTexture(le,D.__webglTexture,i.TEXTURE0+J);const Ee=n.get(W);if(W.version!==Ee.__version||ee===!0){t.activeTexture(i.TEXTURE0+J);const _e=St.getPrimaries(St.workingColorSpace),Ae=E.colorSpace===rs?null:St.getPrimaries(E.colorSpace),Ke=E.colorSpace===rs||_e===Ae?i.NONE:i.BROWSER_DEFAULT_WEBGL;i.pixelStorei(i.UNPACK_FLIP_Y_WEBGL,E.flipY),i.pixelStorei(i.UNPACK_PREMULTIPLY_ALPHA_WEBGL,E.premultiplyAlpha),i.pixelStorei(i.UNPACK_ALIGNMENT,E.unpackAlignment),i.pixelStorei(i.UNPACK_COLORSPACE_CONVERSION_WEBGL,Ke);let me=v(E.image,!1,s.maxTextureSize);me=Ye(E,me);const Te=r.convert(E.format,E.colorSpace),Ze=r.convert(E.type);let ke=S(E.internalFormat,Te,Ze,E.colorSpace,E.isVideoTexture);xe(le,E);let be;const He=E.mipmaps,F=E.isVideoTexture!==!0,ce=Ee.__version===void 0||ee===!0,I=W.dataReady,ae=w(E,me);if(E.isDepthTexture)ke=y(E.format===kr,E.type),ce&&(F?t.texStorage2D(i.TEXTURE_2D,1,ke,me.width,me.height):t.texImage2D(i.TEXTURE_2D,0,ke,me.width,me.height,0,Te,Ze,null));else if(E.isDataTexture)if(He.length>0){F&&ce&&t.texStorage2D(i.TEXTURE_2D,ae,ke,He[0].width,He[0].height);for(let se=0,re=He.length;se<re;se++)be=He[se],F?I&&t.texSubImage2D(i.TEXTURE_2D,se,0,0,be.width,be.height,Te,Ze,be.data):t.texImage2D(i.TEXTURE_2D,se,ke,be.width,be.height,0,Te,Ze,be.data);E.generateMipmaps=!1}else F?(ce&&t.texStorage2D(i.TEXTURE_2D,ae,ke,me.width,me.height),I&&t.texSubImage2D(i.TEXTURE_2D,0,0,0,me.width,me.height,Te,Ze,me.data)):t.texImage2D(i.TEXTURE_2D,0,ke,me.width,me.height,0,Te,Ze,me.data);else if(E.isCompressedTexture)if(E.isCompressedArrayTexture){F&&ce&&t.texStorage3D(i.TEXTURE_2D_ARRAY,ae,ke,He[0].width,He[0].height,me.depth);for(let se=0,re=He.length;se<re;se++)if(be=He[se],E.format!==ci)if(Te!==null)if(F){if(I)if(E.layerUpdates.size>0){const ve=hd(be.width,be.height,E.format,E.type);for(const je of E.layerUpdates){const at=be.data.subarray(je*ve/be.data.BYTES_PER_ELEMENT,(je+1)*ve/be.data.BYTES_PER_ELEMENT);t.compressedTexSubImage3D(i.TEXTURE_2D_ARRAY,se,0,0,je,be.width,be.height,1,Te,at,0,0)}E.clearLayerUpdates()}else t.compressedTexSubImage3D(i.TEXTURE_2D_ARRAY,se,0,0,0,be.width,be.height,me.depth,Te,be.data,0,0)}else t.compressedTexImage3D(i.TEXTURE_2D_ARRAY,se,ke,be.width,be.height,me.depth,0,be.data,0,0);else console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()");else F?I&&t.texSubImage3D(i.TEXTURE_2D_ARRAY,se,0,0,0,be.width,be.height,me.depth,Te,Ze,be.data):t.texImage3D(i.TEXTURE_2D_ARRAY,se,ke,be.width,be.height,me.depth,0,Te,Ze,be.data)}else{F&&ce&&t.texStorage2D(i.TEXTURE_2D,ae,ke,He[0].width,He[0].height);for(let se=0,re=He.length;se<re;se++)be=He[se],E.format!==ci?Te!==null?F?I&&t.compressedTexSubImage2D(i.TEXTURE_2D,se,0,0,be.width,be.height,Te,be.data):t.compressedTexImage2D(i.TEXTURE_2D,se,ke,be.width,be.height,0,be.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()"):F?I&&t.texSubImage2D(i.TEXTURE_2D,se,0,0,be.width,be.height,Te,Ze,be.data):t.texImage2D(i.TEXTURE_2D,se,ke,be.width,be.height,0,Te,Ze,be.data)}else if(E.isDataArrayTexture)if(F){if(ce&&t.texStorage3D(i.TEXTURE_2D_ARRAY,ae,ke,me.width,me.height,me.depth),I)if(E.layerUpdates.size>0){const se=hd(me.width,me.height,E.format,E.type);for(const re of E.layerUpdates){const ve=me.data.subarray(re*se/me.data.BYTES_PER_ELEMENT,(re+1)*se/me.data.BYTES_PER_ELEMENT);t.texSubImage3D(i.TEXTURE_2D_ARRAY,0,0,0,re,me.width,me.height,1,Te,Ze,ve)}E.clearLayerUpdates()}else t.texSubImage3D(i.TEXTURE_2D_ARRAY,0,0,0,0,me.width,me.height,me.depth,Te,Ze,me.data)}else t.texImage3D(i.TEXTURE_2D_ARRAY,0,ke,me.width,me.height,me.depth,0,Te,Ze,me.data);else if(E.isData3DTexture)F?(ce&&t.texStorage3D(i.TEXTURE_3D,ae,ke,me.width,me.height,me.depth),I&&t.texSubImage3D(i.TEXTURE_3D,0,0,0,0,me.width,me.height,me.depth,Te,Ze,me.data)):t.texImage3D(i.TEXTURE_3D,0,ke,me.width,me.height,me.depth,0,Te,Ze,me.data);else if(E.isFramebufferTexture){if(ce)if(F)t.texStorage2D(i.TEXTURE_2D,ae,ke,me.width,me.height);else{let se=me.width,re=me.height;for(let ve=0;ve<ae;ve++)t.texImage2D(i.TEXTURE_2D,ve,ke,se,re,0,Te,Ze,null),se>>=1,re>>=1}}else if(He.length>0){if(F&&ce){const se=Xe(He[0]);t.texStorage2D(i.TEXTURE_2D,ae,ke,se.width,se.height)}for(let se=0,re=He.length;se<re;se++)be=He[se],F?I&&t.texSubImage2D(i.TEXTURE_2D,se,0,0,Te,Ze,be):t.texImage2D(i.TEXTURE_2D,se,ke,Te,Ze,be);E.generateMipmaps=!1}else if(F){if(ce){const se=Xe(me);t.texStorage2D(i.TEXTURE_2D,ae,ke,se.width,se.height)}I&&t.texSubImage2D(i.TEXTURE_2D,0,0,0,Te,Ze,me)}else t.texImage2D(i.TEXTURE_2D,0,ke,Te,Ze,me);m(E)&&p(le),Ee.__version=W.version,E.onUpdate&&E.onUpdate(E)}D.__version=E.version}function ie(D,E,J){if(E.image.length!==6)return;const le=we(D,E),ee=E.source;t.bindTexture(i.TEXTURE_CUBE_MAP,D.__webglTexture,i.TEXTURE0+J);const W=n.get(ee);if(ee.version!==W.__version||le===!0){t.activeTexture(i.TEXTURE0+J);const Ee=St.getPrimaries(St.workingColorSpace),_e=E.colorSpace===rs?null:St.getPrimaries(E.colorSpace),Ae=E.colorSpace===rs||Ee===_e?i.NONE:i.BROWSER_DEFAULT_WEBGL;i.pixelStorei(i.UNPACK_FLIP_Y_WEBGL,E.flipY),i.pixelStorei(i.UNPACK_PREMULTIPLY_ALPHA_WEBGL,E.premultiplyAlpha),i.pixelStorei(i.UNPACK_ALIGNMENT,E.unpackAlignment),i.pixelStorei(i.UNPACK_COLORSPACE_CONVERSION_WEBGL,Ae);const Ke=E.isCompressedTexture||E.image[0].isCompressedTexture,me=E.image[0]&&E.image[0].isDataTexture,Te=[];for(let re=0;re<6;re++)!Ke&&!me?Te[re]=v(E.image[re],!0,s.maxCubemapSize):Te[re]=me?E.image[re].image:E.image[re],Te[re]=Ye(E,Te[re]);const Ze=Te[0],ke=r.convert(E.format,E.colorSpace),be=r.convert(E.type),He=S(E.internalFormat,ke,be,E.colorSpace),F=E.isVideoTexture!==!0,ce=W.__version===void 0||le===!0,I=ee.dataReady;let ae=w(E,Ze);xe(i.TEXTURE_CUBE_MAP,E);let se;if(Ke){F&&ce&&t.texStorage2D(i.TEXTURE_CUBE_MAP,ae,He,Ze.width,Ze.height);for(let re=0;re<6;re++){se=Te[re].mipmaps;for(let ve=0;ve<se.length;ve++){const je=se[ve];E.format!==ci?ke!==null?F?I&&t.compressedTexSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,ve,0,0,je.width,je.height,ke,je.data):t.compressedTexImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,ve,He,je.width,je.height,0,je.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .setTextureCube()"):F?I&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,ve,0,0,je.width,je.height,ke,be,je.data):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,ve,He,je.width,je.height,0,ke,be,je.data)}}}else{if(se=E.mipmaps,F&&ce){se.length>0&&ae++;const re=Xe(Te[0]);t.texStorage2D(i.TEXTURE_CUBE_MAP,ae,He,re.width,re.height)}for(let re=0;re<6;re++)if(me){F?I&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,0,0,0,Te[re].width,Te[re].height,ke,be,Te[re].data):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,0,He,Te[re].width,Te[re].height,0,ke,be,Te[re].data);for(let ve=0;ve<se.length;ve++){const at=se[ve].image[re].image;F?I&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,ve+1,0,0,at.width,at.height,ke,be,at.data):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,ve+1,He,at.width,at.height,0,ke,be,at.data)}}else{F?I&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,0,0,0,ke,be,Te[re]):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,0,He,ke,be,Te[re]);for(let ve=0;ve<se.length;ve++){const je=se[ve];F?I&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,ve+1,0,0,ke,be,je.image[re]):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,ve+1,He,ke,be,je.image[re])}}}m(E)&&p(i.TEXTURE_CUBE_MAP),W.__version=ee.version,E.onUpdate&&E.onUpdate(E)}D.__version=E.version}function ue(D,E,J,le,ee,W){const Ee=r.convert(J.format,J.colorSpace),_e=r.convert(J.type),Ae=S(J.internalFormat,Ee,_e,J.colorSpace);if(!n.get(E).__hasExternalTextures){const me=Math.max(1,E.width>>W),Te=Math.max(1,E.height>>W);ee===i.TEXTURE_3D||ee===i.TEXTURE_2D_ARRAY?t.texImage3D(ee,W,Ae,me,Te,E.depth,0,Ee,_e,null):t.texImage2D(ee,W,Ae,me,Te,0,Ee,_e,null)}t.bindFramebuffer(i.FRAMEBUFFER,D),Oe(E)?o.framebufferTexture2DMultisampleEXT(i.FRAMEBUFFER,le,ee,n.get(J).__webglTexture,0,lt(E)):(ee===i.TEXTURE_2D||ee>=i.TEXTURE_CUBE_MAP_POSITIVE_X&&ee<=i.TEXTURE_CUBE_MAP_NEGATIVE_Z)&&i.framebufferTexture2D(i.FRAMEBUFFER,le,ee,n.get(J).__webglTexture,W),t.bindFramebuffer(i.FRAMEBUFFER,null)}function Me(D,E,J){if(i.bindRenderbuffer(i.RENDERBUFFER,D),E.depthBuffer){const le=E.depthTexture,ee=le&&le.isDepthTexture?le.type:null,W=y(E.stencilBuffer,ee),Ee=E.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,_e=lt(E);Oe(E)?o.renderbufferStorageMultisampleEXT(i.RENDERBUFFER,_e,W,E.width,E.height):J?i.renderbufferStorageMultisample(i.RENDERBUFFER,_e,W,E.width,E.height):i.renderbufferStorage(i.RENDERBUFFER,W,E.width,E.height),i.framebufferRenderbuffer(i.FRAMEBUFFER,Ee,i.RENDERBUFFER,D)}else{const le=E.textures;for(let ee=0;ee<le.length;ee++){const W=le[ee],Ee=r.convert(W.format,W.colorSpace),_e=r.convert(W.type),Ae=S(W.internalFormat,Ee,_e,W.colorSpace),Ke=lt(E);J&&Oe(E)===!1?i.renderbufferStorageMultisample(i.RENDERBUFFER,Ke,Ae,E.width,E.height):Oe(E)?o.renderbufferStorageMultisampleEXT(i.RENDERBUFFER,Ke,Ae,E.width,E.height):i.renderbufferStorage(i.RENDERBUFFER,Ae,E.width,E.height)}}i.bindRenderbuffer(i.RENDERBUFFER,null)}function fe(D,E){if(E&&E.isWebGLCubeRenderTarget)throw new Error("Depth Texture with cube render targets is not supported");if(t.bindFramebuffer(i.FRAMEBUFFER,D),!(E.depthTexture&&E.depthTexture.isDepthTexture))throw new Error("renderTarget.depthTexture must be an instance of THREE.DepthTexture");(!n.get(E.depthTexture).__webglTexture||E.depthTexture.image.width!==E.width||E.depthTexture.image.height!==E.height)&&(E.depthTexture.image.width=E.width,E.depthTexture.image.height=E.height,E.depthTexture.needsUpdate=!0),K(E.depthTexture,0);const le=n.get(E.depthTexture).__webglTexture,ee=lt(E);if(E.depthTexture.format===Rr)Oe(E)?o.framebufferTexture2DMultisampleEXT(i.FRAMEBUFFER,i.DEPTH_ATTACHMENT,i.TEXTURE_2D,le,0,ee):i.framebufferTexture2D(i.FRAMEBUFFER,i.DEPTH_ATTACHMENT,i.TEXTURE_2D,le,0);else if(E.depthTexture.format===kr)Oe(E)?o.framebufferTexture2DMultisampleEXT(i.FRAMEBUFFER,i.DEPTH_STENCIL_ATTACHMENT,i.TEXTURE_2D,le,0,ee):i.framebufferTexture2D(i.FRAMEBUFFER,i.DEPTH_STENCIL_ATTACHMENT,i.TEXTURE_2D,le,0);else throw new Error("Unknown depthTexture format")}function ze(D){const E=n.get(D),J=D.isWebGLCubeRenderTarget===!0;if(E.__boundDepthTexture!==D.depthTexture){const le=D.depthTexture;if(E.__depthDisposeCallback&&E.__depthDisposeCallback(),le){const ee=()=>{delete E.__boundDepthTexture,delete E.__depthDisposeCallback,le.removeEventListener("dispose",ee)};le.addEventListener("dispose",ee),E.__depthDisposeCallback=ee}E.__boundDepthTexture=le}if(D.depthTexture&&!E.__autoAllocateDepthBuffer){if(J)throw new Error("target.depthTexture not supported in Cube render targets");fe(E.__webglFramebuffer,D)}else if(J){E.__webglDepthbuffer=[];for(let le=0;le<6;le++)if(t.bindFramebuffer(i.FRAMEBUFFER,E.__webglFramebuffer[le]),E.__webglDepthbuffer[le]===void 0)E.__webglDepthbuffer[le]=i.createRenderbuffer(),Me(E.__webglDepthbuffer[le],D,!1);else{const ee=D.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,W=E.__webglDepthbuffer[le];i.bindRenderbuffer(i.RENDERBUFFER,W),i.framebufferRenderbuffer(i.FRAMEBUFFER,ee,i.RENDERBUFFER,W)}}else if(t.bindFramebuffer(i.FRAMEBUFFER,E.__webglFramebuffer),E.__webglDepthbuffer===void 0)E.__webglDepthbuffer=i.createRenderbuffer(),Me(E.__webglDepthbuffer,D,!1);else{const le=D.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,ee=E.__webglDepthbuffer;i.bindRenderbuffer(i.RENDERBUFFER,ee),i.framebufferRenderbuffer(i.FRAMEBUFFER,le,i.RENDERBUFFER,ee)}t.bindFramebuffer(i.FRAMEBUFFER,null)}function Ge(D,E,J){const le=n.get(D);E!==void 0&&ue(le.__webglFramebuffer,D,D.texture,i.COLOR_ATTACHMENT0,i.TEXTURE_2D,0),J!==void 0&&ze(D)}function Fe(D){const E=D.texture,J=n.get(D),le=n.get(E);D.addEventListener("dispose",A);const ee=D.textures,W=D.isWebGLCubeRenderTarget===!0,Ee=ee.length>1;if(Ee||(le.__webglTexture===void 0&&(le.__webglTexture=i.createTexture()),le.__version=E.version,a.memory.textures++),W){J.__webglFramebuffer=[];for(let _e=0;_e<6;_e++)if(E.mipmaps&&E.mipmaps.length>0){J.__webglFramebuffer[_e]=[];for(let Ae=0;Ae<E.mipmaps.length;Ae++)J.__webglFramebuffer[_e][Ae]=i.createFramebuffer()}else J.__webglFramebuffer[_e]=i.createFramebuffer()}else{if(E.mipmaps&&E.mipmaps.length>0){J.__webglFramebuffer=[];for(let _e=0;_e<E.mipmaps.length;_e++)J.__webglFramebuffer[_e]=i.createFramebuffer()}else J.__webglFramebuffer=i.createFramebuffer();if(Ee)for(let _e=0,Ae=ee.length;_e<Ae;_e++){const Ke=n.get(ee[_e]);Ke.__webglTexture===void 0&&(Ke.__webglTexture=i.createTexture(),a.memory.textures++)}if(D.samples>0&&Oe(D)===!1){J.__webglMultisampledFramebuffer=i.createFramebuffer(),J.__webglColorRenderbuffer=[],t.bindFramebuffer(i.FRAMEBUFFER,J.__webglMultisampledFramebuffer);for(let _e=0;_e<ee.length;_e++){const Ae=ee[_e];J.__webglColorRenderbuffer[_e]=i.createRenderbuffer(),i.bindRenderbuffer(i.RENDERBUFFER,J.__webglColorRenderbuffer[_e]);const Ke=r.convert(Ae.format,Ae.colorSpace),me=r.convert(Ae.type),Te=S(Ae.internalFormat,Ke,me,Ae.colorSpace,D.isXRRenderTarget===!0),Ze=lt(D);i.renderbufferStorageMultisample(i.RENDERBUFFER,Ze,Te,D.width,D.height),i.framebufferRenderbuffer(i.FRAMEBUFFER,i.COLOR_ATTACHMENT0+_e,i.RENDERBUFFER,J.__webglColorRenderbuffer[_e])}i.bindRenderbuffer(i.RENDERBUFFER,null),D.depthBuffer&&(J.__webglDepthRenderbuffer=i.createRenderbuffer(),Me(J.__webglDepthRenderbuffer,D,!0)),t.bindFramebuffer(i.FRAMEBUFFER,null)}}if(W){t.bindTexture(i.TEXTURE_CUBE_MAP,le.__webglTexture),xe(i.TEXTURE_CUBE_MAP,E);for(let _e=0;_e<6;_e++)if(E.mipmaps&&E.mipmaps.length>0)for(let Ae=0;Ae<E.mipmaps.length;Ae++)ue(J.__webglFramebuffer[_e][Ae],D,E,i.COLOR_ATTACHMENT0,i.TEXTURE_CUBE_MAP_POSITIVE_X+_e,Ae);else ue(J.__webglFramebuffer[_e],D,E,i.COLOR_ATTACHMENT0,i.TEXTURE_CUBE_MAP_POSITIVE_X+_e,0);m(E)&&p(i.TEXTURE_CUBE_MAP),t.unbindTexture()}else if(Ee){for(let _e=0,Ae=ee.length;_e<Ae;_e++){const Ke=ee[_e],me=n.get(Ke);t.bindTexture(i.TEXTURE_2D,me.__webglTexture),xe(i.TEXTURE_2D,Ke),ue(J.__webglFramebuffer,D,Ke,i.COLOR_ATTACHMENT0+_e,i.TEXTURE_2D,0),m(Ke)&&p(i.TEXTURE_2D)}t.unbindTexture()}else{let _e=i.TEXTURE_2D;if((D.isWebGL3DRenderTarget||D.isWebGLArrayRenderTarget)&&(_e=D.isWebGL3DRenderTarget?i.TEXTURE_3D:i.TEXTURE_2D_ARRAY),t.bindTexture(_e,le.__webglTexture),xe(_e,E),E.mipmaps&&E.mipmaps.length>0)for(let Ae=0;Ae<E.mipmaps.length;Ae++)ue(J.__webglFramebuffer[Ae],D,E,i.COLOR_ATTACHMENT0,_e,Ae);else ue(J.__webglFramebuffer,D,E,i.COLOR_ATTACHMENT0,_e,0);m(E)&&p(_e),t.unbindTexture()}D.depthBuffer&&ze(D)}function ft(D){const E=D.textures;for(let J=0,le=E.length;J<le;J++){const ee=E[J];if(m(ee)){const W=D.isWebGLCubeRenderTarget?i.TEXTURE_CUBE_MAP:i.TEXTURE_2D,Ee=n.get(ee).__webglTexture;t.bindTexture(W,Ee),p(W),t.unbindTexture()}}}const U=[],ht=[];function it(D){if(D.samples>0){if(Oe(D)===!1){const E=D.textures,J=D.width,le=D.height;let ee=i.COLOR_BUFFER_BIT;const W=D.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,Ee=n.get(D),_e=E.length>1;if(_e)for(let Ae=0;Ae<E.length;Ae++)t.bindFramebuffer(i.FRAMEBUFFER,Ee.__webglMultisampledFramebuffer),i.framebufferRenderbuffer(i.FRAMEBUFFER,i.COLOR_ATTACHMENT0+Ae,i.RENDERBUFFER,null),t.bindFramebuffer(i.FRAMEBUFFER,Ee.__webglFramebuffer),i.framebufferTexture2D(i.DRAW_FRAMEBUFFER,i.COLOR_ATTACHMENT0+Ae,i.TEXTURE_2D,null,0);t.bindFramebuffer(i.READ_FRAMEBUFFER,Ee.__webglMultisampledFramebuffer),t.bindFramebuffer(i.DRAW_FRAMEBUFFER,Ee.__webglFramebuffer);for(let Ae=0;Ae<E.length;Ae++){if(D.resolveDepthBuffer&&(D.depthBuffer&&(ee|=i.DEPTH_BUFFER_BIT),D.stencilBuffer&&D.resolveStencilBuffer&&(ee|=i.STENCIL_BUFFER_BIT)),_e){i.framebufferRenderbuffer(i.READ_FRAMEBUFFER,i.COLOR_ATTACHMENT0,i.RENDERBUFFER,Ee.__webglColorRenderbuffer[Ae]);const Ke=n.get(E[Ae]).__webglTexture;i.framebufferTexture2D(i.DRAW_FRAMEBUFFER,i.COLOR_ATTACHMENT0,i.TEXTURE_2D,Ke,0)}i.blitFramebuffer(0,0,J,le,0,0,J,le,ee,i.NEAREST),l===!0&&(U.length=0,ht.length=0,U.push(i.COLOR_ATTACHMENT0+Ae),D.depthBuffer&&D.resolveDepthBuffer===!1&&(U.push(W),ht.push(W),i.invalidateFramebuffer(i.DRAW_FRAMEBUFFER,ht)),i.invalidateFramebuffer(i.READ_FRAMEBUFFER,U))}if(t.bindFramebuffer(i.READ_FRAMEBUFFER,null),t.bindFramebuffer(i.DRAW_FRAMEBUFFER,null),_e)for(let Ae=0;Ae<E.length;Ae++){t.bindFramebuffer(i.FRAMEBUFFER,Ee.__webglMultisampledFramebuffer),i.framebufferRenderbuffer(i.FRAMEBUFFER,i.COLOR_ATTACHMENT0+Ae,i.RENDERBUFFER,Ee.__webglColorRenderbuffer[Ae]);const Ke=n.get(E[Ae]).__webglTexture;t.bindFramebuffer(i.FRAMEBUFFER,Ee.__webglFramebuffer),i.framebufferTexture2D(i.DRAW_FRAMEBUFFER,i.COLOR_ATTACHMENT0+Ae,i.TEXTURE_2D,Ke,0)}t.bindFramebuffer(i.DRAW_FRAMEBUFFER,Ee.__webglMultisampledFramebuffer)}else if(D.depthBuffer&&D.resolveDepthBuffer===!1&&l){const E=D.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT;i.invalidateFramebuffer(i.DRAW_FRAMEBUFFER,[E])}}}function lt(D){return Math.min(s.maxSamples,D.samples)}function Oe(D){const E=n.get(D);return D.samples>0&&e.has("WEBGL_multisampled_render_to_texture")===!0&&E.__useRenderToTexture!==!1}function bt(D){const E=a.render.frame;u.get(D)!==E&&(u.set(D,E),D.update())}function Ye(D,E){const J=D.colorSpace,le=D.format,ee=D.type;return D.isCompressedTexture===!0||D.isVideoTexture===!0||J!==fs&&J!==rs&&(St.getTransfer(J)===Ft?(le!==ci||ee!==Gi)&&console.warn("THREE.WebGLTextures: sRGB encoded textures have to use RGBAFormat and UnsignedByteType."):console.error("THREE.WebGLTextures: Unsupported texture color space:",J)),E}function Xe(D){return typeof HTMLImageElement<"u"&&D instanceof HTMLImageElement?(c.width=D.naturalWidth||D.width,c.height=D.naturalHeight||D.height):typeof VideoFrame<"u"&&D instanceof VideoFrame?(c.width=D.displayWidth,c.height=D.displayHeight):(c.width=D.width,c.height=D.height),c}this.allocateTextureUnit=j,this.resetTextureUnits=R,this.setTexture2D=K,this.setTexture2DArray=X,this.setTexture3D=Q,this.setTextureCube=Y,this.rebindTextures=Ge,this.setupRenderTarget=Fe,this.updateRenderTargetMipmap=ft,this.updateMultisampleRenderTarget=it,this.setupDepthRenderbuffer=ze,this.setupFrameBufferTexture=ue,this.useMultisampledRTT=Oe}function Cy(i,e){function t(n,s=rs){let r;const a=St.getTransfer(s);if(n===Gi)return i.UNSIGNED_BYTE;if(n===fu)return i.UNSIGNED_SHORT_4_4_4_4;if(n===pu)return i.UNSIGNED_SHORT_5_5_5_1;if(n===Cf)return i.UNSIGNED_INT_5_9_9_9_REV;if(n===Tf)return i.BYTE;if(n===Af)return i.SHORT;if(n===Ca)return i.UNSIGNED_SHORT;if(n===du)return i.INT;if(n===Os)return i.UNSIGNED_INT;if(n===Fi)return i.FLOAT;if(n===Ia)return i.HALF_FLOAT;if(n===Rf)return i.ALPHA;if(n===Pf)return i.RGB;if(n===ci)return i.RGBA;if(n===Lf)return i.LUMINANCE;if(n===Df)return i.LUMINANCE_ALPHA;if(n===Rr)return i.DEPTH_COMPONENT;if(n===kr)return i.DEPTH_STENCIL;if(n===If)return i.RED;if(n===mu)return i.RED_INTEGER;if(n===Uf)return i.RG;if(n===gu)return i.RG_INTEGER;if(n===_u)return i.RGBA_INTEGER;if(n===Lo||n===Do||n===Io||n===Uo)if(a===Ft)if(r=e.get("WEBGL_compressed_texture_s3tc_srgb"),r!==null){if(n===Lo)return r.COMPRESSED_SRGB_S3TC_DXT1_EXT;if(n===Do)return r.COMPRESSED_SRGB_ALPHA_S3TC_DXT1_EXT;if(n===Io)return r.COMPRESSED_SRGB_ALPHA_S3TC_DXT3_EXT;if(n===Uo)return r.COMPRESSED_SRGB_ALPHA_S3TC_DXT5_EXT}else return null;else if(r=e.get("WEBGL_compressed_texture_s3tc"),r!==null){if(n===Lo)return r.COMPRESSED_RGB_S3TC_DXT1_EXT;if(n===Do)return r.COMPRESSED_RGBA_S3TC_DXT1_EXT;if(n===Io)return r.COMPRESSED_RGBA_S3TC_DXT3_EXT;if(n===Uo)return r.COMPRESSED_RGBA_S3TC_DXT5_EXT}else return null;if(n===Ec||n===wc||n===Tc||n===Ac)if(r=e.get("WEBGL_compressed_texture_pvrtc"),r!==null){if(n===Ec)return r.COMPRESSED_RGB_PVRTC_4BPPV1_IMG;if(n===wc)return r.COMPRESSED_RGB_PVRTC_2BPPV1_IMG;if(n===Tc)return r.COMPRESSED_RGBA_PVRTC_4BPPV1_IMG;if(n===Ac)return r.COMPRESSED_RGBA_PVRTC_2BPPV1_IMG}else return null;if(n===Cc||n===Rc||n===Pc)if(r=e.get("WEBGL_compressed_texture_etc"),r!==null){if(n===Cc||n===Rc)return a===Ft?r.COMPRESSED_SRGB8_ETC2:r.COMPRESSED_RGB8_ETC2;if(n===Pc)return a===Ft?r.COMPRESSED_SRGB8_ALPHA8_ETC2_EAC:r.COMPRESSED_RGBA8_ETC2_EAC}else return null;if(n===Lc||n===Dc||n===Ic||n===Uc||n===Nc||n===Fc||n===Oc||n===Bc||n===zc||n===kc||n===Hc||n===Vc||n===Gc||n===Wc)if(r=e.get("WEBGL_compressed_texture_astc"),r!==null){if(n===Lc)return a===Ft?r.COMPRESSED_SRGB8_ALPHA8_ASTC_4x4_KHR:r.COMPRESSED_RGBA_ASTC_4x4_KHR;if(n===Dc)return a===Ft?r.COMPRESSED_SRGB8_ALPHA8_ASTC_5x4_KHR:r.COMPRESSED_RGBA_ASTC_5x4_KHR;if(n===Ic)return a===Ft?r.COMPRESSED_SRGB8_ALPHA8_ASTC_5x5_KHR:r.COMPRESSED_RGBA_ASTC_5x5_KHR;if(n===Uc)return a===Ft?r.COMPRESSED_SRGB8_ALPHA8_ASTC_6x5_KHR:r.COMPRESSED_RGBA_ASTC_6x5_KHR;if(n===Nc)return a===Ft?r.COMPRESSED_SRGB8_ALPHA8_ASTC_6x6_KHR:r.COMPRESSED_RGBA_ASTC_6x6_KHR;if(n===Fc)return a===Ft?r.COMPRESSED_SRGB8_ALPHA8_ASTC_8x5_KHR:r.COMPRESSED_RGBA_ASTC_8x5_KHR;if(n===Oc)return a===Ft?r.COMPRESSED_SRGB8_ALPHA8_ASTC_8x6_KHR:r.COMPRESSED_RGBA_ASTC_8x6_KHR;if(n===Bc)return a===Ft?r.COMPRESSED_SRGB8_ALPHA8_ASTC_8x8_KHR:r.COMPRESSED_RGBA_ASTC_8x8_KHR;if(n===zc)return a===Ft?r.COMPRESSED_SRGB8_ALPHA8_ASTC_10x5_KHR:r.COMPRESSED_RGBA_ASTC_10x5_KHR;if(n===kc)return a===Ft?r.COMPRESSED_SRGB8_ALPHA8_ASTC_10x6_KHR:r.COMPRESSED_RGBA_ASTC_10x6_KHR;if(n===Hc)return a===Ft?r.COMPRESSED_SRGB8_ALPHA8_ASTC_10x8_KHR:r.COMPRESSED_RGBA_ASTC_10x8_KHR;if(n===Vc)return a===Ft?r.COMPRESSED_SRGB8_ALPHA8_ASTC_10x10_KHR:r.COMPRESSED_RGBA_ASTC_10x10_KHR;if(n===Gc)return a===Ft?r.COMPRESSED_SRGB8_ALPHA8_ASTC_12x10_KHR:r.COMPRESSED_RGBA_ASTC_12x10_KHR;if(n===Wc)return a===Ft?r.COMPRESSED_SRGB8_ALPHA8_ASTC_12x12_KHR:r.COMPRESSED_RGBA_ASTC_12x12_KHR}else return null;if(n===No||n===Xc||n===qc)if(r=e.get("EXT_texture_compression_bptc"),r!==null){if(n===No)return a===Ft?r.COMPRESSED_SRGB_ALPHA_BPTC_UNORM_EXT:r.COMPRESSED_RGBA_BPTC_UNORM_EXT;if(n===Xc)return r.COMPRESSED_RGB_BPTC_SIGNED_FLOAT_EXT;if(n===qc)return r.COMPRESSED_RGB_BPTC_UNSIGNED_FLOAT_EXT}else return null;if(n===Nf||n===Yc||n===$c||n===jc)if(r=e.get("EXT_texture_compression_rgtc"),r!==null){if(n===No)return r.COMPRESSED_RED_RGTC1_EXT;if(n===Yc)return r.COMPRESSED_SIGNED_RED_RGTC1_EXT;if(n===$c)return r.COMPRESSED_RED_GREEN_RGTC2_EXT;if(n===jc)return r.COMPRESSED_SIGNED_RED_GREEN_RGTC2_EXT}else return null;return n===zr?i.UNSIGNED_INT_24_8:i[n]!==void 0?i[n]:null}return{convert:t}}class Ry extends Sn{constructor(e=[]){super(),this.isArrayCamera=!0,this.cameras=e}}class as extends Jt{constructor(){super(),this.isGroup=!0,this.type="Group"}}const Py={type:"move"};class nc{constructor(){this._targetRay=null,this._grip=null,this._hand=null}getHandSpace(){return this._hand===null&&(this._hand=new as,this._hand.matrixAutoUpdate=!1,this._hand.visible=!1,this._hand.joints={},this._hand.inputState={pinching:!1}),this._hand}getTargetRaySpace(){return this._targetRay===null&&(this._targetRay=new as,this._targetRay.matrixAutoUpdate=!1,this._targetRay.visible=!1,this._targetRay.hasLinearVelocity=!1,this._targetRay.linearVelocity=new k,this._targetRay.hasAngularVelocity=!1,this._targetRay.angularVelocity=new k),this._targetRay}getGripSpace(){return this._grip===null&&(this._grip=new as,this._grip.matrixAutoUpdate=!1,this._grip.visible=!1,this._grip.hasLinearVelocity=!1,this._grip.linearVelocity=new k,this._grip.hasAngularVelocity=!1,this._grip.angularVelocity=new k),this._grip}dispatchEvent(e){return this._targetRay!==null&&this._targetRay.dispatchEvent(e),this._grip!==null&&this._grip.dispatchEvent(e),this._hand!==null&&this._hand.dispatchEvent(e),this}connect(e){if(e&&e.hand){const t=this._hand;if(t)for(const n of e.hand.values())this._getHandJoint(t,n)}return this.dispatchEvent({type:"connected",data:e}),this}disconnect(e){return this.dispatchEvent({type:"disconnected",data:e}),this._targetRay!==null&&(this._targetRay.visible=!1),this._grip!==null&&(this._grip.visible=!1),this._hand!==null&&(this._hand.visible=!1),this}update(e,t,n){let s=null,r=null,a=null;const o=this._targetRay,l=this._grip,c=this._hand;if(e&&t.session.visibilityState!=="visible-blurred"){if(c&&e.hand){a=!0;for(const v of e.hand.values()){const m=t.getJointPose(v,n),p=this._getHandJoint(c,v);m!==null&&(p.matrix.fromArray(m.transform.matrix),p.matrix.decompose(p.position,p.rotation,p.scale),p.matrixWorldNeedsUpdate=!0,p.jointRadius=m.radius),p.visible=m!==null}const u=c.joints["index-finger-tip"],h=c.joints["thumb-tip"],d=u.position.distanceTo(h.position),f=.02,g=.005;c.inputState.pinching&&d>f+g?(c.inputState.pinching=!1,this.dispatchEvent({type:"pinchend",handedness:e.handedness,target:this})):!c.inputState.pinching&&d<=f-g&&(c.inputState.pinching=!0,this.dispatchEvent({type:"pinchstart",handedness:e.handedness,target:this}))}else l!==null&&e.gripSpace&&(r=t.getPose(e.gripSpace,n),r!==null&&(l.matrix.fromArray(r.transform.matrix),l.matrix.decompose(l.position,l.rotation,l.scale),l.matrixWorldNeedsUpdate=!0,r.linearVelocity?(l.hasLinearVelocity=!0,l.linearVelocity.copy(r.linearVelocity)):l.hasLinearVelocity=!1,r.angularVelocity?(l.hasAngularVelocity=!0,l.angularVelocity.copy(r.angularVelocity)):l.hasAngularVelocity=!1));o!==null&&(s=t.getPose(e.targetRaySpace,n),s===null&&r!==null&&(s=r),s!==null&&(o.matrix.fromArray(s.transform.matrix),o.matrix.decompose(o.position,o.rotation,o.scale),o.matrixWorldNeedsUpdate=!0,s.linearVelocity?(o.hasLinearVelocity=!0,o.linearVelocity.copy(s.linearVelocity)):o.hasLinearVelocity=!1,s.angularVelocity?(o.hasAngularVelocity=!0,o.angularVelocity.copy(s.angularVelocity)):o.hasAngularVelocity=!1,this.dispatchEvent(Py)))}return o!==null&&(o.visible=s!==null),l!==null&&(l.visible=r!==null),c!==null&&(c.visible=a!==null),this}_getHandJoint(e,t){if(e.joints[t.jointName]===void 0){const n=new as;n.matrixAutoUpdate=!1,n.visible=!1,e.joints[t.jointName]=n,e.add(n)}return e.joints[t.jointName]}}const Ly=`
void main() {

	gl_Position = vec4( position, 1.0 );

}`,Dy=`
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

}`;class Iy{constructor(){this.texture=null,this.mesh=null,this.depthNear=0,this.depthFar=0}init(e,t,n){if(this.texture===null){const s=new Ln,r=e.properties.get(s);r.__webglTexture=t.texture,(t.depthNear!=n.depthNear||t.depthFar!=n.depthFar)&&(this.depthNear=t.depthNear,this.depthFar=t.depthFar),this.texture=s}}getMesh(e){if(this.texture!==null&&this.mesh===null){const t=e.cameras[0].viewport,n=new us({vertexShader:Ly,fragmentShader:Dy,uniforms:{depthColor:{value:this.texture},depthWidth:{value:t.z},depthHeight:{value:t.w}}});this.mesh=new gn(new Oa(20,20),n)}return this.mesh}reset(){this.texture=null,this.mesh=null}getDepthTexture(){return this.texture}}class Uy extends jr{constructor(e,t){super();const n=this;let s=null,r=1,a=null,o="local-floor",l=1,c=null,u=null,h=null,d=null,f=null,g=null;const v=new Iy,m=t.getContextAttributes();let p=null,S=null;const y=[],w=[],O=new qe;let A=null;const P=new Sn;P.layers.enable(1),P.viewport=new tn;const N=new Sn;N.layers.enable(2),N.viewport=new tn;const b=[P,N],x=new Ry;x.layers.enable(1),x.layers.enable(2);let R=null,j=null;this.cameraAutoUpdate=!0,this.enabled=!1,this.isPresenting=!1,this.getController=function(ie){let ue=y[ie];return ue===void 0&&(ue=new nc,y[ie]=ue),ue.getTargetRaySpace()},this.getControllerGrip=function(ie){let ue=y[ie];return ue===void 0&&(ue=new nc,y[ie]=ue),ue.getGripSpace()},this.getHand=function(ie){let ue=y[ie];return ue===void 0&&(ue=new nc,y[ie]=ue),ue.getHandSpace()};function z(ie){const ue=w.indexOf(ie.inputSource);if(ue===-1)return;const Me=y[ue];Me!==void 0&&(Me.update(ie.inputSource,ie.frame,c||a),Me.dispatchEvent({type:ie.type,data:ie.inputSource}))}function K(){s.removeEventListener("select",z),s.removeEventListener("selectstart",z),s.removeEventListener("selectend",z),s.removeEventListener("squeeze",z),s.removeEventListener("squeezestart",z),s.removeEventListener("squeezeend",z),s.removeEventListener("end",K),s.removeEventListener("inputsourceschange",X);for(let ie=0;ie<y.length;ie++){const ue=w[ie];ue!==null&&(w[ie]=null,y[ie].disconnect(ue))}R=null,j=null,v.reset(),e.setRenderTarget(p),f=null,d=null,h=null,s=null,S=null,ye.stop(),n.isPresenting=!1,e.setPixelRatio(A),e.setSize(O.width,O.height,!1),n.dispatchEvent({type:"sessionend"})}this.setFramebufferScaleFactor=function(ie){r=ie,n.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change framebuffer scale while presenting.")},this.setReferenceSpaceType=function(ie){o=ie,n.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change reference space type while presenting.")},this.getReferenceSpace=function(){return c||a},this.setReferenceSpace=function(ie){c=ie},this.getBaseLayer=function(){return d!==null?d:f},this.getBinding=function(){return h},this.getFrame=function(){return g},this.getSession=function(){return s},this.setSession=async function(ie){if(s=ie,s!==null){if(p=e.getRenderTarget(),s.addEventListener("select",z),s.addEventListener("selectstart",z),s.addEventListener("selectend",z),s.addEventListener("squeeze",z),s.addEventListener("squeezestart",z),s.addEventListener("squeezeend",z),s.addEventListener("end",K),s.addEventListener("inputsourceschange",X),m.xrCompatible!==!0&&await t.makeXRCompatible(),A=e.getPixelRatio(),e.getSize(O),s.renderState.layers===void 0){const ue={antialias:m.antialias,alpha:!0,depth:m.depth,stencil:m.stencil,framebufferScaleFactor:r};f=new XRWebGLLayer(s,t,ue),s.updateRenderState({baseLayer:f}),e.setPixelRatio(1),e.setSize(f.framebufferWidth,f.framebufferHeight,!1),S=new Bs(f.framebufferWidth,f.framebufferHeight,{format:ci,type:Gi,colorSpace:e.outputColorSpace,stencilBuffer:m.stencil})}else{let ue=null,Me=null,fe=null;m.depth&&(fe=m.stencil?t.DEPTH24_STENCIL8:t.DEPTH_COMPONENT24,ue=m.stencil?kr:Rr,Me=m.stencil?zr:Os);const ze={colorFormat:t.RGBA8,depthFormat:fe,scaleFactor:r};h=new XRWebGLBinding(s,t),d=h.createProjectionLayer(ze),s.updateRenderState({layers:[d]}),e.setPixelRatio(1),e.setSize(d.textureWidth,d.textureHeight,!1),S=new Bs(d.textureWidth,d.textureHeight,{format:ci,type:Gi,depthTexture:new $f(d.textureWidth,d.textureHeight,Me,void 0,void 0,void 0,void 0,void 0,void 0,ue),stencilBuffer:m.stencil,colorSpace:e.outputColorSpace,samples:m.antialias?4:0,resolveDepthBuffer:d.ignoreDepthValues===!1})}S.isXRRenderTarget=!0,this.setFoveation(l),c=null,a=await s.requestReferenceSpace(o),ye.setContext(s),ye.start(),n.isPresenting=!0,n.dispatchEvent({type:"sessionstart"})}},this.getEnvironmentBlendMode=function(){if(s!==null)return s.environmentBlendMode},this.getDepthTexture=function(){return v.getDepthTexture()};function X(ie){for(let ue=0;ue<ie.removed.length;ue++){const Me=ie.removed[ue],fe=w.indexOf(Me);fe>=0&&(w[fe]=null,y[fe].disconnect(Me))}for(let ue=0;ue<ie.added.length;ue++){const Me=ie.added[ue];let fe=w.indexOf(Me);if(fe===-1){for(let Ge=0;Ge<y.length;Ge++)if(Ge>=w.length){w.push(Me),fe=Ge;break}else if(w[Ge]===null){w[Ge]=Me,fe=Ge;break}if(fe===-1)break}const ze=y[fe];ze&&ze.connect(Me)}}const Q=new k,Y=new k;function ne(ie,ue,Me){Q.setFromMatrixPosition(ue.matrixWorld),Y.setFromMatrixPosition(Me.matrixWorld);const fe=Q.distanceTo(Y),ze=ue.projectionMatrix.elements,Ge=Me.projectionMatrix.elements,Fe=ze[14]/(ze[10]-1),ft=ze[14]/(ze[10]+1),U=(ze[9]+1)/ze[5],ht=(ze[9]-1)/ze[5],it=(ze[8]-1)/ze[0],lt=(Ge[8]+1)/Ge[0],Oe=Fe*it,bt=Fe*lt,Ye=fe/(-it+lt),Xe=Ye*-it;if(ue.matrixWorld.decompose(ie.position,ie.quaternion,ie.scale),ie.translateX(Xe),ie.translateZ(Ye),ie.matrixWorld.compose(ie.position,ie.quaternion,ie.scale),ie.matrixWorldInverse.copy(ie.matrixWorld).invert(),ze[10]===-1)ie.projectionMatrix.copy(ue.projectionMatrix),ie.projectionMatrixInverse.copy(ue.projectionMatrixInverse);else{const D=Fe+Ye,E=ft+Ye,J=Oe-Xe,le=bt+(fe-Xe),ee=U*ft/E*D,W=ht*ft/E*D;ie.projectionMatrix.makePerspective(J,le,ee,W,D,E),ie.projectionMatrixInverse.copy(ie.projectionMatrix).invert()}}function ge(ie,ue){ue===null?ie.matrixWorld.copy(ie.matrix):ie.matrixWorld.multiplyMatrices(ue.matrixWorld,ie.matrix),ie.matrixWorldInverse.copy(ie.matrixWorld).invert()}this.updateCamera=function(ie){if(s===null)return;let ue=ie.near,Me=ie.far;v.texture!==null&&(v.depthNear>0&&(ue=v.depthNear),v.depthFar>0&&(Me=v.depthFar)),x.near=N.near=P.near=ue,x.far=N.far=P.far=Me,(R!==x.near||j!==x.far)&&(s.updateRenderState({depthNear:x.near,depthFar:x.far}),R=x.near,j=x.far);const fe=ie.parent,ze=x.cameras;ge(x,fe);for(let Ge=0;Ge<ze.length;Ge++)ge(ze[Ge],fe);ze.length===2?ne(x,P,N):x.projectionMatrix.copy(P.projectionMatrix),de(ie,x,fe)};function de(ie,ue,Me){Me===null?ie.matrix.copy(ue.matrixWorld):(ie.matrix.copy(Me.matrixWorld),ie.matrix.invert(),ie.matrix.multiply(ue.matrixWorld)),ie.matrix.decompose(ie.position,ie.quaternion,ie.scale),ie.updateMatrixWorld(!0),ie.projectionMatrix.copy(ue.projectionMatrix),ie.projectionMatrixInverse.copy(ue.projectionMatrixInverse),ie.isPerspectiveCamera&&(ie.fov=Ra*2*Math.atan(1/ie.projectionMatrix.elements[5]),ie.zoom=1)}this.getCamera=function(){return x},this.getFoveation=function(){if(!(d===null&&f===null))return l},this.setFoveation=function(ie){l=ie,d!==null&&(d.fixedFoveation=ie),f!==null&&f.fixedFoveation!==void 0&&(f.fixedFoveation=ie)},this.hasDepthSensing=function(){return v.texture!==null},this.getDepthSensingMesh=function(){return v.getMesh(x)};let xe=null;function we(ie,ue){if(u=ue.getViewerPose(c||a),g=ue,u!==null){const Me=u.views;f!==null&&(e.setRenderTargetFramebuffer(S,f.framebuffer),e.setRenderTarget(S));let fe=!1;Me.length!==x.cameras.length&&(x.cameras.length=0,fe=!0);for(let Ge=0;Ge<Me.length;Ge++){const Fe=Me[Ge];let ft=null;if(f!==null)ft=f.getViewport(Fe);else{const ht=h.getViewSubImage(d,Fe);ft=ht.viewport,Ge===0&&(e.setRenderTargetTextures(S,ht.colorTexture,d.ignoreDepthValues?void 0:ht.depthStencilTexture),e.setRenderTarget(S))}let U=b[Ge];U===void 0&&(U=new Sn,U.layers.enable(Ge),U.viewport=new tn,b[Ge]=U),U.matrix.fromArray(Fe.transform.matrix),U.matrix.decompose(U.position,U.quaternion,U.scale),U.projectionMatrix.fromArray(Fe.projectionMatrix),U.projectionMatrixInverse.copy(U.projectionMatrix).invert(),U.viewport.set(ft.x,ft.y,ft.width,ft.height),Ge===0&&(x.matrix.copy(U.matrix),x.matrix.decompose(x.position,x.quaternion,x.scale)),fe===!0&&x.cameras.push(U)}const ze=s.enabledFeatures;if(ze&&ze.includes("depth-sensing")){const Ge=h.getDepthInformation(Me[0]);Ge&&Ge.isValid&&Ge.texture&&v.init(e,Ge,s.renderState)}}for(let Me=0;Me<y.length;Me++){const fe=w[Me],ze=y[Me];fe!==null&&ze!==void 0&&ze.update(fe,ue,c||a)}xe&&xe(ie,ue),ue.detectedPlanes&&n.dispatchEvent({type:"planesdetected",data:ue}),g=null}const ye=new Yf;ye.setAnimationLoop(we),this.setAnimationLoop=function(ie){xe=ie},this.dispose=function(){}}}const ws=new Si,Ny=new Ot;function Fy(i,e){function t(m,p){m.matrixAutoUpdate===!0&&m.updateMatrix(),p.value.copy(m.matrix)}function n(m,p){p.color.getRGB(m.fogColor.value,Wf(i)),p.isFog?(m.fogNear.value=p.near,m.fogFar.value=p.far):p.isFogExp2&&(m.fogDensity.value=p.density)}function s(m,p,S,y,w){p.isMeshBasicMaterial||p.isMeshLambertMaterial?r(m,p):p.isMeshToonMaterial?(r(m,p),h(m,p)):p.isMeshPhongMaterial?(r(m,p),u(m,p)):p.isMeshStandardMaterial?(r(m,p),d(m,p),p.isMeshPhysicalMaterial&&f(m,p,w)):p.isMeshMatcapMaterial?(r(m,p),g(m,p)):p.isMeshDepthMaterial?r(m,p):p.isMeshDistanceMaterial?(r(m,p),v(m,p)):p.isMeshNormalMaterial?r(m,p):p.isLineBasicMaterial?(a(m,p),p.isLineDashedMaterial&&o(m,p)):p.isPointsMaterial?l(m,p,S,y):p.isSpriteMaterial?c(m,p):p.isShadowMaterial?(m.color.value.copy(p.color),m.opacity.value=p.opacity):p.isShaderMaterial&&(p.uniformsNeedUpdate=!1)}function r(m,p){m.opacity.value=p.opacity,p.color&&m.diffuse.value.copy(p.color),p.emissive&&m.emissive.value.copy(p.emissive).multiplyScalar(p.emissiveIntensity),p.map&&(m.map.value=p.map,t(p.map,m.mapTransform)),p.alphaMap&&(m.alphaMap.value=p.alphaMap,t(p.alphaMap,m.alphaMapTransform)),p.bumpMap&&(m.bumpMap.value=p.bumpMap,t(p.bumpMap,m.bumpMapTransform),m.bumpScale.value=p.bumpScale,p.side===In&&(m.bumpScale.value*=-1)),p.normalMap&&(m.normalMap.value=p.normalMap,t(p.normalMap,m.normalMapTransform),m.normalScale.value.copy(p.normalScale),p.side===In&&m.normalScale.value.negate()),p.displacementMap&&(m.displacementMap.value=p.displacementMap,t(p.displacementMap,m.displacementMapTransform),m.displacementScale.value=p.displacementScale,m.displacementBias.value=p.displacementBias),p.emissiveMap&&(m.emissiveMap.value=p.emissiveMap,t(p.emissiveMap,m.emissiveMapTransform)),p.specularMap&&(m.specularMap.value=p.specularMap,t(p.specularMap,m.specularMapTransform)),p.alphaTest>0&&(m.alphaTest.value=p.alphaTest);const S=e.get(p),y=S.envMap,w=S.envMapRotation;y&&(m.envMap.value=y,ws.copy(w),ws.x*=-1,ws.y*=-1,ws.z*=-1,y.isCubeTexture&&y.isRenderTargetTexture===!1&&(ws.y*=-1,ws.z*=-1),m.envMapRotation.value.setFromMatrix4(Ny.makeRotationFromEuler(ws)),m.flipEnvMap.value=y.isCubeTexture&&y.isRenderTargetTexture===!1?-1:1,m.reflectivity.value=p.reflectivity,m.ior.value=p.ior,m.refractionRatio.value=p.refractionRatio),p.lightMap&&(m.lightMap.value=p.lightMap,m.lightMapIntensity.value=p.lightMapIntensity,t(p.lightMap,m.lightMapTransform)),p.aoMap&&(m.aoMap.value=p.aoMap,m.aoMapIntensity.value=p.aoMapIntensity,t(p.aoMap,m.aoMapTransform))}function a(m,p){m.diffuse.value.copy(p.color),m.opacity.value=p.opacity,p.map&&(m.map.value=p.map,t(p.map,m.mapTransform))}function o(m,p){m.dashSize.value=p.dashSize,m.totalSize.value=p.dashSize+p.gapSize,m.scale.value=p.scale}function l(m,p,S,y){m.diffuse.value.copy(p.color),m.opacity.value=p.opacity,m.size.value=p.size*S,m.scale.value=y*.5,p.map&&(m.map.value=p.map,t(p.map,m.uvTransform)),p.alphaMap&&(m.alphaMap.value=p.alphaMap,t(p.alphaMap,m.alphaMapTransform)),p.alphaTest>0&&(m.alphaTest.value=p.alphaTest)}function c(m,p){m.diffuse.value.copy(p.color),m.opacity.value=p.opacity,m.rotation.value=p.rotation,p.map&&(m.map.value=p.map,t(p.map,m.mapTransform)),p.alphaMap&&(m.alphaMap.value=p.alphaMap,t(p.alphaMap,m.alphaMapTransform)),p.alphaTest>0&&(m.alphaTest.value=p.alphaTest)}function u(m,p){m.specular.value.copy(p.specular),m.shininess.value=Math.max(p.shininess,1e-4)}function h(m,p){p.gradientMap&&(m.gradientMap.value=p.gradientMap)}function d(m,p){m.metalness.value=p.metalness,p.metalnessMap&&(m.metalnessMap.value=p.metalnessMap,t(p.metalnessMap,m.metalnessMapTransform)),m.roughness.value=p.roughness,p.roughnessMap&&(m.roughnessMap.value=p.roughnessMap,t(p.roughnessMap,m.roughnessMapTransform)),p.envMap&&(m.envMapIntensity.value=p.envMapIntensity)}function f(m,p,S){m.ior.value=p.ior,p.sheen>0&&(m.sheenColor.value.copy(p.sheenColor).multiplyScalar(p.sheen),m.sheenRoughness.value=p.sheenRoughness,p.sheenColorMap&&(m.sheenColorMap.value=p.sheenColorMap,t(p.sheenColorMap,m.sheenColorMapTransform)),p.sheenRoughnessMap&&(m.sheenRoughnessMap.value=p.sheenRoughnessMap,t(p.sheenRoughnessMap,m.sheenRoughnessMapTransform))),p.clearcoat>0&&(m.clearcoat.value=p.clearcoat,m.clearcoatRoughness.value=p.clearcoatRoughness,p.clearcoatMap&&(m.clearcoatMap.value=p.clearcoatMap,t(p.clearcoatMap,m.clearcoatMapTransform)),p.clearcoatRoughnessMap&&(m.clearcoatRoughnessMap.value=p.clearcoatRoughnessMap,t(p.clearcoatRoughnessMap,m.clearcoatRoughnessMapTransform)),p.clearcoatNormalMap&&(m.clearcoatNormalMap.value=p.clearcoatNormalMap,t(p.clearcoatNormalMap,m.clearcoatNormalMapTransform),m.clearcoatNormalScale.value.copy(p.clearcoatNormalScale),p.side===In&&m.clearcoatNormalScale.value.negate())),p.dispersion>0&&(m.dispersion.value=p.dispersion),p.iridescence>0&&(m.iridescence.value=p.iridescence,m.iridescenceIOR.value=p.iridescenceIOR,m.iridescenceThicknessMinimum.value=p.iridescenceThicknessRange[0],m.iridescenceThicknessMaximum.value=p.iridescenceThicknessRange[1],p.iridescenceMap&&(m.iridescenceMap.value=p.iridescenceMap,t(p.iridescenceMap,m.iridescenceMapTransform)),p.iridescenceThicknessMap&&(m.iridescenceThicknessMap.value=p.iridescenceThicknessMap,t(p.iridescenceThicknessMap,m.iridescenceThicknessMapTransform))),p.transmission>0&&(m.transmission.value=p.transmission,m.transmissionSamplerMap.value=S.texture,m.transmissionSamplerSize.value.set(S.width,S.height),p.transmissionMap&&(m.transmissionMap.value=p.transmissionMap,t(p.transmissionMap,m.transmissionMapTransform)),m.thickness.value=p.thickness,p.thicknessMap&&(m.thicknessMap.value=p.thicknessMap,t(p.thicknessMap,m.thicknessMapTransform)),m.attenuationDistance.value=p.attenuationDistance,m.attenuationColor.value.copy(p.attenuationColor)),p.anisotropy>0&&(m.anisotropyVector.value.set(p.anisotropy*Math.cos(p.anisotropyRotation),p.anisotropy*Math.sin(p.anisotropyRotation)),p.anisotropyMap&&(m.anisotropyMap.value=p.anisotropyMap,t(p.anisotropyMap,m.anisotropyMapTransform))),m.specularIntensity.value=p.specularIntensity,m.specularColor.value.copy(p.specularColor),p.specularColorMap&&(m.specularColorMap.value=p.specularColorMap,t(p.specularColorMap,m.specularColorMapTransform)),p.specularIntensityMap&&(m.specularIntensityMap.value=p.specularIntensityMap,t(p.specularIntensityMap,m.specularIntensityMapTransform))}function g(m,p){p.matcap&&(m.matcap.value=p.matcap)}function v(m,p){const S=e.get(p).light;m.referencePosition.value.setFromMatrixPosition(S.matrixWorld),m.nearDistance.value=S.shadow.camera.near,m.farDistance.value=S.shadow.camera.far}return{refreshFogUniforms:n,refreshMaterialUniforms:s}}function Oy(i,e,t,n){let s={},r={},a=[];const o=i.getParameter(i.MAX_UNIFORM_BUFFER_BINDINGS);function l(S,y){const w=y.program;n.uniformBlockBinding(S,w)}function c(S,y){let w=s[S.id];w===void 0&&(g(S),w=u(S),s[S.id]=w,S.addEventListener("dispose",m));const O=y.program;n.updateUBOMapping(S,O);const A=e.render.frame;r[S.id]!==A&&(d(S),r[S.id]=A)}function u(S){const y=h();S.__bindingPointIndex=y;const w=i.createBuffer(),O=S.__size,A=S.usage;return i.bindBuffer(i.UNIFORM_BUFFER,w),i.bufferData(i.UNIFORM_BUFFER,O,A),i.bindBuffer(i.UNIFORM_BUFFER,null),i.bindBufferBase(i.UNIFORM_BUFFER,y,w),w}function h(){for(let S=0;S<o;S++)if(a.indexOf(S)===-1)return a.push(S),S;return console.error("THREE.WebGLRenderer: Maximum number of simultaneously usable uniforms groups reached."),0}function d(S){const y=s[S.id],w=S.uniforms,O=S.__cache;i.bindBuffer(i.UNIFORM_BUFFER,y);for(let A=0,P=w.length;A<P;A++){const N=Array.isArray(w[A])?w[A]:[w[A]];for(let b=0,x=N.length;b<x;b++){const R=N[b];if(f(R,A,b,O)===!0){const j=R.__offset,z=Array.isArray(R.value)?R.value:[R.value];let K=0;for(let X=0;X<z.length;X++){const Q=z[X],Y=v(Q);typeof Q=="number"||typeof Q=="boolean"?(R.__data[0]=Q,i.bufferSubData(i.UNIFORM_BUFFER,j+K,R.__data)):Q.isMatrix3?(R.__data[0]=Q.elements[0],R.__data[1]=Q.elements[1],R.__data[2]=Q.elements[2],R.__data[3]=0,R.__data[4]=Q.elements[3],R.__data[5]=Q.elements[4],R.__data[6]=Q.elements[5],R.__data[7]=0,R.__data[8]=Q.elements[6],R.__data[9]=Q.elements[7],R.__data[10]=Q.elements[8],R.__data[11]=0):(Q.toArray(R.__data,K),K+=Y.storage/Float32Array.BYTES_PER_ELEMENT)}i.bufferSubData(i.UNIFORM_BUFFER,j,R.__data)}}}i.bindBuffer(i.UNIFORM_BUFFER,null)}function f(S,y,w,O){const A=S.value,P=y+"_"+w;if(O[P]===void 0)return typeof A=="number"||typeof A=="boolean"?O[P]=A:O[P]=A.clone(),!0;{const N=O[P];if(typeof A=="number"||typeof A=="boolean"){if(N!==A)return O[P]=A,!0}else if(N.equals(A)===!1)return N.copy(A),!0}return!1}function g(S){const y=S.uniforms;let w=0;const O=16;for(let P=0,N=y.length;P<N;P++){const b=Array.isArray(y[P])?y[P]:[y[P]];for(let x=0,R=b.length;x<R;x++){const j=b[x],z=Array.isArray(j.value)?j.value:[j.value];for(let K=0,X=z.length;K<X;K++){const Q=z[K],Y=v(Q),ne=w%O,ge=ne%Y.boundary,de=ne+ge;w+=ge,de!==0&&O-de<Y.storage&&(w+=O-de),j.__data=new Float32Array(Y.storage/Float32Array.BYTES_PER_ELEMENT),j.__offset=w,w+=Y.storage}}}const A=w%O;return A>0&&(w+=O-A),S.__size=w,S.__cache={},this}function v(S){const y={boundary:0,storage:0};return typeof S=="number"||typeof S=="boolean"?(y.boundary=4,y.storage=4):S.isVector2?(y.boundary=8,y.storage=8):S.isVector3||S.isColor?(y.boundary=16,y.storage=12):S.isVector4?(y.boundary=16,y.storage=16):S.isMatrix3?(y.boundary=48,y.storage=48):S.isMatrix4?(y.boundary=64,y.storage=64):S.isTexture?console.warn("THREE.WebGLRenderer: Texture samplers can not be part of an uniforms group."):console.warn("THREE.WebGLRenderer: Unsupported uniform value type.",S),y}function m(S){const y=S.target;y.removeEventListener("dispose",m);const w=a.indexOf(y.__bindingPointIndex);a.splice(w,1),i.deleteBuffer(s[y.id]),delete s[y.id],delete r[y.id]}function p(){for(const S in s)i.deleteBuffer(s[S]);a=[],s={},r={}}return{bind:l,update:c,dispose:p}}class Qf{constructor(e={}){const{canvas:t=Cg(),context:n=null,depth:s=!0,stencil:r=!1,alpha:a=!1,antialias:o=!1,premultipliedAlpha:l=!0,preserveDrawingBuffer:c=!1,powerPreference:u="default",failIfMajorPerformanceCaveat:h=!1}=e;this.isWebGLRenderer=!0;let d;if(n!==null){if(typeof WebGLRenderingContext<"u"&&n instanceof WebGLRenderingContext)throw new Error("THREE.WebGLRenderer: WebGL 1 is not supported since r163.");d=n.getContextAttributes().alpha}else d=a;const f=new Uint32Array(4),g=new Int32Array(4);let v=null,m=null;const p=[],S=[];this.domElement=t,this.debug={checkShaderErrors:!0,onShaderError:null},this.autoClear=!0,this.autoClearColor=!0,this.autoClearDepth=!0,this.autoClearStencil=!0,this.sortObjects=!0,this.clippingPlanes=[],this.localClippingEnabled=!1,this._outputColorSpace=xi,this.toneMapping=ls,this.toneMappingExposure=1;const y=this;let w=!1,O=0,A=0,P=null,N=-1,b=null;const x=new tn,R=new tn;let j=null;const z=new nt(0);let K=0,X=t.width,Q=t.height,Y=1,ne=null,ge=null;const de=new tn(0,0,X,Q),xe=new tn(0,0,X,Q);let we=!1;const ye=new Mu;let ie=!1,ue=!1;const Me=new Ot,fe=new k,ze=new tn,Ge={background:null,fog:null,environment:null,overrideMaterial:null,isScene:!0};let Fe=!1;function ft(){return P===null?Y:1}let U=n;function ht(T,V){return t.getContext(T,V)}try{const T={alpha:!0,depth:s,stencil:r,antialias:o,premultipliedAlpha:l,preserveDrawingBuffer:c,powerPreference:u,failIfMajorPerformanceCaveat:h};if("setAttribute"in t&&t.setAttribute("data-engine",`three.js r${hu}`),t.addEventListener("webglcontextlost",se,!1),t.addEventListener("webglcontextrestored",re,!1),t.addEventListener("webglcontextcreationerror",ve,!1),U===null){const V="webgl2";if(U=ht(V,T),U===null)throw ht(V)?new Error("Error creating WebGL context with your selected attributes."):new Error("Error creating WebGL context.")}}catch(T){throw console.error("THREE.WebGLRenderer: "+T.message),T}let it,lt,Oe,bt,Ye,Xe,D,E,J,le,ee,W,Ee,_e,Ae,Ke,me,Te,Ze,ke,be,He,F,ce;function I(){it=new Wv(U),it.init(),He=new Cy(U,it),lt=new Bv(U,it,e,He),Oe=new wy(U),bt=new Yv(U),Ye=new hy,Xe=new Ay(U,it,Oe,Ye,lt,He,bt),D=new kv(y),E=new Gv(y),J=new e_(U),F=new Fv(U,J),le=new Xv(U,J,bt,F),ee=new jv(U,le,J,bt),Ze=new $v(U,lt,Xe),Ke=new zv(Ye),W=new uy(y,D,E,it,lt,F,Ke),Ee=new Fy(y,Ye),_e=new fy,Ae=new xy(it),Te=new Nv(y,D,E,Oe,ee,d,l),me=new Ey(y,ee,lt),ce=new Oy(U,bt,lt,Oe),ke=new Ov(U,it,bt),be=new qv(U,it,bt),bt.programs=W.programs,y.capabilities=lt,y.extensions=it,y.properties=Ye,y.renderLists=_e,y.shadowMap=me,y.state=Oe,y.info=bt}I();const ae=new Uy(y,U);this.xr=ae,this.getContext=function(){return U},this.getContextAttributes=function(){return U.getContextAttributes()},this.forceContextLoss=function(){const T=it.get("WEBGL_lose_context");T&&T.loseContext()},this.forceContextRestore=function(){const T=it.get("WEBGL_lose_context");T&&T.restoreContext()},this.getPixelRatio=function(){return Y},this.setPixelRatio=function(T){T!==void 0&&(Y=T,this.setSize(X,Q,!1))},this.getSize=function(T){return T.set(X,Q)},this.setSize=function(T,V,Z=!0){if(ae.isPresenting){console.warn("THREE.WebGLRenderer: Can't change size while VR device is presenting.");return}X=T,Q=V,t.width=Math.floor(T*Y),t.height=Math.floor(V*Y),Z===!0&&(t.style.width=T+"px",t.style.height=V+"px"),this.setViewport(0,0,T,V)},this.getDrawingBufferSize=function(T){return T.set(X*Y,Q*Y).floor()},this.setDrawingBufferSize=function(T,V,Z){X=T,Q=V,Y=Z,t.width=Math.floor(T*Z),t.height=Math.floor(V*Z),this.setViewport(0,0,T,V)},this.getCurrentViewport=function(T){return T.copy(x)},this.getViewport=function(T){return T.copy(de)},this.setViewport=function(T,V,Z,q){T.isVector4?de.set(T.x,T.y,T.z,T.w):de.set(T,V,Z,q),Oe.viewport(x.copy(de).multiplyScalar(Y).round())},this.getScissor=function(T){return T.copy(xe)},this.setScissor=function(T,V,Z,q){T.isVector4?xe.set(T.x,T.y,T.z,T.w):xe.set(T,V,Z,q),Oe.scissor(R.copy(xe).multiplyScalar(Y).round())},this.getScissorTest=function(){return we},this.setScissorTest=function(T){Oe.setScissorTest(we=T)},this.setOpaqueSort=function(T){ne=T},this.setTransparentSort=function(T){ge=T},this.getClearColor=function(T){return T.copy(Te.getClearColor())},this.setClearColor=function(){Te.setClearColor.apply(Te,arguments)},this.getClearAlpha=function(){return Te.getClearAlpha()},this.setClearAlpha=function(){Te.setClearAlpha.apply(Te,arguments)},this.clear=function(T=!0,V=!0,Z=!0){let q=0;if(T){let H=!1;if(P!==null){const he=P.texture.format;H=he===_u||he===gu||he===mu}if(H){const he=P.texture.type,Re=he===Gi||he===Os||he===Ca||he===zr||he===fu||he===pu,Pe=Te.getClearColor(),Ie=Te.getClearAlpha(),Je=Pe.r,Qe=Pe.g,Be=Pe.b;Re?(f[0]=Je,f[1]=Qe,f[2]=Be,f[3]=Ie,U.clearBufferuiv(U.COLOR,0,f)):(g[0]=Je,g[1]=Qe,g[2]=Be,g[3]=Ie,U.clearBufferiv(U.COLOR,0,g))}else q|=U.COLOR_BUFFER_BIT}V&&(q|=U.DEPTH_BUFFER_BIT),Z&&(q|=U.STENCIL_BUFFER_BIT,this.state.buffers.stencil.setMask(4294967295)),U.clear(q)},this.clearColor=function(){this.clear(!0,!1,!1)},this.clearDepth=function(){this.clear(!1,!0,!1)},this.clearStencil=function(){this.clear(!1,!1,!0)},this.dispose=function(){t.removeEventListener("webglcontextlost",se,!1),t.removeEventListener("webglcontextrestored",re,!1),t.removeEventListener("webglcontextcreationerror",ve,!1),_e.dispose(),Ae.dispose(),Ye.dispose(),D.dispose(),E.dispose(),ee.dispose(),F.dispose(),ce.dispose(),W.dispose(),ae.dispose(),ae.removeEventListener("sessionstart",Bt),ae.removeEventListener("sessionend",zt),an.stop()};function se(T){T.preventDefault(),console.log("THREE.WebGLRenderer: Context Lost."),w=!0}function re(){console.log("THREE.WebGLRenderer: Context Restored."),w=!1;const T=bt.autoReset,V=me.enabled,Z=me.autoUpdate,q=me.needsUpdate,H=me.type;I(),bt.autoReset=T,me.enabled=V,me.autoUpdate=Z,me.needsUpdate=q,me.type=H}function ve(T){console.error("THREE.WebGLRenderer: A WebGL context could not be created. Reason: ",T.statusMessage)}function je(T){const V=T.target;V.removeEventListener("dispose",je),at(V)}function at(T){gt(T),Ye.remove(T)}function gt(T){const V=Ye.get(T).programs;V!==void 0&&(V.forEach(function(Z){W.releaseProgram(Z)}),T.isShaderMaterial&&W.releaseShaderCache(T))}this.renderBufferDirect=function(T,V,Z,q,H,he){V===null&&(V=Ge);const Re=H.isMesh&&H.matrixWorld.determinant()<0,Pe=_l(T,V,Z,q,H);Oe.setMaterial(q,Re);let Ie=Z.index,Je=1;if(q.wireframe===!0){if(Ie=le.getWireframeAttribute(Z),Ie===void 0)return;Je=2}const Qe=Z.drawRange,Be=Z.attributes.position;let ct=Qe.start*Je,Rt=(Qe.start+Qe.count)*Je;he!==null&&(ct=Math.max(ct,he.start*Je),Rt=Math.min(Rt,(he.start+he.count)*Je)),Ie!==null?(ct=Math.max(ct,0),Rt=Math.min(Rt,Ie.count)):Be!=null&&(ct=Math.max(ct,0),Rt=Math.min(Rt,Be.count));const Pt=Rt-ct;if(Pt<0||Pt===1/0)return;F.setup(H,q,Pe,Z,Ie);let pn,pt=ke;if(Ie!==null&&(pn=J.get(Ie),pt=be,pt.setIndex(pn)),H.isMesh)q.wireframe===!0?(Oe.setLineWidth(q.wireframeLinewidth*ft()),pt.setMode(U.LINES)):pt.setMode(U.TRIANGLES);else if(H.isLine){let Ve=q.linewidth;Ve===void 0&&(Ve=1),Oe.setLineWidth(Ve*ft()),H.isLineSegments?pt.setMode(U.LINES):H.isLineLoop?pt.setMode(U.LINE_LOOP):pt.setMode(U.LINE_STRIP)}else H.isPoints?pt.setMode(U.POINTS):H.isSprite&&pt.setMode(U.TRIANGLES);if(H.isBatchedMesh)if(H._multiDrawInstances!==null)pt.renderMultiDrawInstances(H._multiDrawStarts,H._multiDrawCounts,H._multiDrawCount,H._multiDrawInstances);else if(it.get("WEBGL_multi_draw"))pt.renderMultiDraw(H._multiDrawStarts,H._multiDrawCounts,H._multiDrawCount);else{const Ve=H._multiDrawStarts,Yt=H._multiDrawCounts,mt=H._multiDrawCount,Lt=Ie?J.get(Ie).bytesPerElement:1,Ai=Ye.get(q).currentProgram.getUniforms();for(let vn=0;vn<mt;vn++)Ai.setValue(U,"_gl_DrawID",vn),pt.render(Ve[vn]/Lt,Yt[vn])}else if(H.isInstancedMesh)pt.renderInstances(ct,Pt,H.count);else if(Z.isInstancedBufferGeometry){const Ve=Z._maxInstanceCount!==void 0?Z._maxInstanceCount:1/0,Yt=Math.min(Z.instanceCount,Ve);pt.renderInstances(ct,Pt,Yt)}else pt.render(ct,Pt)};function Et(T,V,Z){T.transparent===!0&&T.side===$n&&T.forceSinglePass===!1?(T.side=In,T.needsUpdate=!0,ms(T,V,Z),T.side=cs,T.needsUpdate=!0,ms(T,V,Z),T.side=$n):ms(T,V,Z)}this.compile=function(T,V,Z=null){Z===null&&(Z=T),m=Ae.get(Z),m.init(V),S.push(m),Z.traverseVisible(function(H){H.isLight&&H.layers.test(V.layers)&&(m.pushLight(H),H.castShadow&&m.pushShadow(H))}),T!==Z&&T.traverseVisible(function(H){H.isLight&&H.layers.test(V.layers)&&(m.pushLight(H),H.castShadow&&m.pushShadow(H))}),m.setupLights();const q=new Set;return T.traverse(function(H){const he=H.material;if(he)if(Array.isArray(he))for(let Re=0;Re<he.length;Re++){const Pe=he[Re];Et(Pe,Z,H),q.add(Pe)}else Et(he,Z,H),q.add(he)}),S.pop(),m=null,q},this.compileAsync=function(T,V,Z=null){const q=this.compile(T,V,Z);return new Promise(H=>{function he(){if(q.forEach(function(Re){Ye.get(Re).currentProgram.isReady()&&q.delete(Re)}),q.size===0){H(T);return}setTimeout(he,10)}it.get("KHR_parallel_shader_compile")!==null?he():setTimeout(he,10)})};let ot=null;function fn(T){ot&&ot(T)}function Bt(){an.stop()}function zt(){an.start()}const an=new Yf;an.setAnimationLoop(fn),typeof self<"u"&&an.setContext(self),this.setAnimationLoop=function(T){ot=T,ae.setAnimationLoop(T),T===null?an.stop():an.start()},ae.addEventListener("sessionstart",Bt),ae.addEventListener("sessionend",zt),this.render=function(T,V){if(V!==void 0&&V.isCamera!==!0){console.error("THREE.WebGLRenderer.render: camera is not an instance of THREE.Camera.");return}if(w===!0)return;if(T.matrixWorldAutoUpdate===!0&&T.updateMatrixWorld(),V.parent===null&&V.matrixWorldAutoUpdate===!0&&V.updateMatrixWorld(),ae.enabled===!0&&ae.isPresenting===!0&&(ae.cameraAutoUpdate===!0&&ae.updateCamera(V),V=ae.getCamera()),T.isScene===!0&&T.onBeforeRender(y,T,V,P),m=Ae.get(T,S.length),m.init(V),S.push(m),Me.multiplyMatrices(V.projectionMatrix,V.matrixWorldInverse),ye.setFromProjectionMatrix(Me),ue=this.localClippingEnabled,ie=Ke.init(this.clippingPlanes,ue),v=_e.get(T,p.length),v.init(),p.push(v),ae.enabled===!0&&ae.isPresenting===!0){const he=y.xr.getDepthSensingMesh();he!==null&&di(he,V,-1/0,y.sortObjects)}di(T,V,0,y.sortObjects),v.finish(),y.sortObjects===!0&&v.sort(ne,ge),Fe=ae.enabled===!1||ae.isPresenting===!1||ae.hasDepthSensing()===!1,Fe&&Te.addToRenderList(v,T),this.info.render.frame++,ie===!0&&Ke.beginShadows();const Z=m.state.shadowsArray;me.render(Z,T,V),ie===!0&&Ke.endShadows(),this.info.autoReset===!0&&this.info.reset();const q=v.opaque,H=v.transmissive;if(m.setupLights(),V.isArrayCamera){const he=V.cameras;if(H.length>0)for(let Re=0,Pe=he.length;Re<Pe;Re++){const Ie=he[Re];En(q,H,T,Ie)}Fe&&Te.render(T);for(let Re=0,Pe=he.length;Re<Pe;Re++){const Ie=he[Re];Ei(v,T,Ie,Ie.viewport)}}else H.length>0&&En(q,H,T,V),Fe&&Te.render(T),Ei(v,T,V);P!==null&&(Xe.updateMultisampleRenderTarget(P),Xe.updateRenderTargetMipmap(P)),T.isScene===!0&&T.onAfterRender(y,T,V),F.resetDefaultState(),N=-1,b=null,S.pop(),S.length>0?(m=S[S.length-1],ie===!0&&Ke.setGlobalState(y.clippingPlanes,m.state.camera)):m=null,p.pop(),p.length>0?v=p[p.length-1]:v=null};function di(T,V,Z,q){if(T.visible===!1)return;if(T.layers.test(V.layers)){if(T.isGroup)Z=T.renderOrder;else if(T.isLOD)T.autoUpdate===!0&&T.update(V);else if(T.isLight)m.pushLight(T),T.castShadow&&m.pushShadow(T);else if(T.isSprite){if(!T.frustumCulled||ye.intersectsSprite(T)){q&&ze.setFromMatrixPosition(T.matrixWorld).applyMatrix4(Me);const Re=ee.update(T),Pe=T.material;Pe.visible&&v.push(T,Re,Pe,Z,ze.z,null)}}else if((T.isMesh||T.isLine||T.isPoints)&&(!T.frustumCulled||ye.intersectsObject(T))){const Re=ee.update(T),Pe=T.material;if(q&&(T.boundingSphere!==void 0?(T.boundingSphere===null&&T.computeBoundingSphere(),ze.copy(T.boundingSphere.center)):(Re.boundingSphere===null&&Re.computeBoundingSphere(),ze.copy(Re.boundingSphere.center)),ze.applyMatrix4(T.matrixWorld).applyMatrix4(Me)),Array.isArray(Pe)){const Ie=Re.groups;for(let Je=0,Qe=Ie.length;Je<Qe;Je++){const Be=Ie[Je],ct=Pe[Be.materialIndex];ct&&ct.visible&&v.push(T,Re,ct,Z,ze.z,Be)}}else Pe.visible&&v.push(T,Re,Pe,Z,ze.z,null)}}const he=T.children;for(let Re=0,Pe=he.length;Re<Pe;Re++)di(he[Re],V,Z,q)}function Ei(T,V,Z,q){const H=T.opaque,he=T.transmissive,Re=T.transparent;m.setupLightsView(Z),ie===!0&&Ke.setGlobalState(y.clippingPlanes,Z),q&&Oe.viewport(x.copy(q)),H.length>0&&Jn(H,V,Z),he.length>0&&Jn(he,V,Z),Re.length>0&&Jn(Re,V,Z),Oe.buffers.depth.setTest(!0),Oe.buffers.depth.setMask(!0),Oe.buffers.color.setMask(!0),Oe.setPolygonOffset(!1)}function En(T,V,Z,q){if((Z.isScene===!0?Z.overrideMaterial:null)!==null)return;m.state.transmissionRenderTarget[q.id]===void 0&&(m.state.transmissionRenderTarget[q.id]=new Bs(1,1,{generateMipmaps:!0,type:it.has("EXT_color_buffer_half_float")||it.has("EXT_color_buffer_float")?Ia:Gi,minFilter:Is,samples:4,stencilBuffer:r,resolveDepthBuffer:!1,resolveStencilBuffer:!1,colorSpace:St.workingColorSpace}));const he=m.state.transmissionRenderTarget[q.id],Re=q.viewport||x;he.setSize(Re.z,Re.w);const Pe=y.getRenderTarget();y.setRenderTarget(he),y.getClearColor(z),K=y.getClearAlpha(),K<1&&y.setClearColor(16777215,.5),y.clear(),Fe&&Te.render(Z);const Ie=y.toneMapping;y.toneMapping=ls;const Je=q.viewport;if(q.viewport!==void 0&&(q.viewport=void 0),m.setupLightsView(q),ie===!0&&Ke.setGlobalState(y.clippingPlanes,q),Jn(T,Z,q),Xe.updateMultisampleRenderTarget(he),Xe.updateRenderTargetMipmap(he),it.has("WEBGL_multisampled_render_to_texture")===!1){let Qe=!1;for(let Be=0,ct=V.length;Be<ct;Be++){const Rt=V[Be],Pt=Rt.object,pn=Rt.geometry,pt=Rt.material,Ve=Rt.group;if(pt.side===$n&&Pt.layers.test(q.layers)){const Yt=pt.side;pt.side=In,pt.needsUpdate=!0,wi(Pt,Z,q,pn,pt,Ve),pt.side=Yt,pt.needsUpdate=!0,Qe=!0}}Qe===!0&&(Xe.updateMultisampleRenderTarget(he),Xe.updateRenderTargetMipmap(he))}y.setRenderTarget(Pe),y.setClearColor(z,K),Je!==void 0&&(q.viewport=Je),y.toneMapping=Ie}function Jn(T,V,Z){const q=V.isScene===!0?V.overrideMaterial:null;for(let H=0,he=T.length;H<he;H++){const Re=T[H],Pe=Re.object,Ie=Re.geometry,Je=q===null?Re.material:q,Qe=Re.group;Pe.layers.test(Z.layers)&&wi(Pe,V,Z,Ie,Je,Qe)}}function wi(T,V,Z,q,H,he){T.onBeforeRender(y,V,Z,q,H,he),T.modelViewMatrix.multiplyMatrices(Z.matrixWorldInverse,T.matrixWorld),T.normalMatrix.getNormalMatrix(T.modelViewMatrix),H.onBeforeRender(y,V,Z,q,T,he),H.transparent===!0&&H.side===$n&&H.forceSinglePass===!1?(H.side=In,H.needsUpdate=!0,y.renderBufferDirect(Z,V,q,H,T,he),H.side=cs,H.needsUpdate=!0,y.renderBufferDirect(Z,V,q,H,T,he),H.side=$n):y.renderBufferDirect(Z,V,q,H,T,he),T.onAfterRender(y,V,Z,q,H,he)}function ms(T,V,Z){V.isScene!==!0&&(V=Ge);const q=Ye.get(T),H=m.state.lights,he=m.state.shadowsArray,Re=H.state.version,Pe=W.getParameters(T,H.state,he,V,Z),Ie=W.getProgramCacheKey(Pe);let Je=q.programs;q.environment=T.isMeshStandardMaterial?V.environment:null,q.fog=V.fog,q.envMap=(T.isMeshStandardMaterial?E:D).get(T.envMap||q.environment),q.envMapRotation=q.environment!==null&&T.envMap===null?V.environmentRotation:T.envMapRotation,Je===void 0&&(T.addEventListener("dispose",je),Je=new Map,q.programs=Je);let Qe=Je.get(Ie);if(Qe!==void 0){if(q.currentProgram===Qe&&q.lightsStateVersion===Re)return za(T,Pe),Qe}else Pe.uniforms=W.getUniforms(T),T.onBeforeCompile(Pe,y),Qe=W.acquireProgram(Pe,Ie),Je.set(Ie,Qe),q.uniforms=Pe.uniforms;const Be=q.uniforms;return(!T.isShaderMaterial&&!T.isRawShaderMaterial||T.clipping===!0)&&(Be.clippingPlanes=Ke.uniform),za(T,Pe),q.needsLights=vl(T),q.lightsStateVersion=Re,q.needsLights&&(Be.ambientLightColor.value=H.state.ambient,Be.lightProbe.value=H.state.probe,Be.directionalLights.value=H.state.directional,Be.directionalLightShadows.value=H.state.directionalShadow,Be.spotLights.value=H.state.spot,Be.spotLightShadows.value=H.state.spotShadow,Be.rectAreaLights.value=H.state.rectArea,Be.ltc_1.value=H.state.rectAreaLTC1,Be.ltc_2.value=H.state.rectAreaLTC2,Be.pointLights.value=H.state.point,Be.pointLightShadows.value=H.state.pointShadow,Be.hemisphereLights.value=H.state.hemi,Be.directionalShadowMap.value=H.state.directionalShadowMap,Be.directionalShadowMatrix.value=H.state.directionalShadowMatrix,Be.spotShadowMap.value=H.state.spotShadowMap,Be.spotLightMatrix.value=H.state.spotLightMatrix,Be.spotLightMap.value=H.state.spotLightMap,Be.pointShadowMap.value=H.state.pointShadowMap,Be.pointShadowMatrix.value=H.state.pointShadowMatrix),q.currentProgram=Qe,q.uniformsList=null,Qe}function ta(T){if(T.uniformsList===null){const V=T.currentProgram.getUniforms();T.uniformsList=Fo.seqWithValue(V.seq,T.uniforms)}return T.uniformsList}function za(T,V){const Z=Ye.get(T);Z.outputColorSpace=V.outputColorSpace,Z.batching=V.batching,Z.batchingColor=V.batchingColor,Z.instancing=V.instancing,Z.instancingColor=V.instancingColor,Z.instancingMorph=V.instancingMorph,Z.skinning=V.skinning,Z.morphTargets=V.morphTargets,Z.morphNormals=V.morphNormals,Z.morphColors=V.morphColors,Z.morphTargetsCount=V.morphTargetsCount,Z.numClippingPlanes=V.numClippingPlanes,Z.numIntersection=V.numClipIntersection,Z.vertexAlphas=V.vertexAlphas,Z.vertexTangents=V.vertexTangents,Z.toneMapping=V.toneMapping}function _l(T,V,Z,q,H){V.isScene!==!0&&(V=Ge),Xe.resetTextureUnits();const he=V.fog,Re=q.isMeshStandardMaterial?V.environment:null,Pe=P===null?y.outputColorSpace:P.isXRRenderTarget===!0?P.texture.colorSpace:fs,Ie=(q.isMeshStandardMaterial?E:D).get(q.envMap||Re),Je=q.vertexColors===!0&&!!Z.attributes.color&&Z.attributes.color.itemSize===4,Qe=!!Z.attributes.tangent&&(!!q.normalMap||q.anisotropy>0),Be=!!Z.morphAttributes.position,ct=!!Z.morphAttributes.normal,Rt=!!Z.morphAttributes.color;let Pt=ls;q.toneMapped&&(P===null||P.isXRRenderTarget===!0)&&(Pt=y.toneMapping);const pn=Z.morphAttributes.position||Z.morphAttributes.normal||Z.morphAttributes.color,pt=pn!==void 0?pn.length:0,Ve=Ye.get(q),Yt=m.state.lights;if(ie===!0&&(ue===!0||T!==b)){const Dn=T===b&&q.id===N;Ke.setState(q,T,Dn)}let mt=!1;q.version===Ve.__version?(Ve.needsLights&&Ve.lightsStateVersion!==Yt.state.version||Ve.outputColorSpace!==Pe||H.isBatchedMesh&&Ve.batching===!1||!H.isBatchedMesh&&Ve.batching===!0||H.isBatchedMesh&&Ve.batchingColor===!0&&H.colorTexture===null||H.isBatchedMesh&&Ve.batchingColor===!1&&H.colorTexture!==null||H.isInstancedMesh&&Ve.instancing===!1||!H.isInstancedMesh&&Ve.instancing===!0||H.isSkinnedMesh&&Ve.skinning===!1||!H.isSkinnedMesh&&Ve.skinning===!0||H.isInstancedMesh&&Ve.instancingColor===!0&&H.instanceColor===null||H.isInstancedMesh&&Ve.instancingColor===!1&&H.instanceColor!==null||H.isInstancedMesh&&Ve.instancingMorph===!0&&H.morphTexture===null||H.isInstancedMesh&&Ve.instancingMorph===!1&&H.morphTexture!==null||Ve.envMap!==Ie||q.fog===!0&&Ve.fog!==he||Ve.numClippingPlanes!==void 0&&(Ve.numClippingPlanes!==Ke.numPlanes||Ve.numIntersection!==Ke.numIntersection)||Ve.vertexAlphas!==Je||Ve.vertexTangents!==Qe||Ve.morphTargets!==Be||Ve.morphNormals!==ct||Ve.morphColors!==Rt||Ve.toneMapping!==Pt||Ve.morphTargetsCount!==pt)&&(mt=!0):(mt=!0,Ve.__version=q.version);let Lt=Ve.currentProgram;mt===!0&&(Lt=ms(q,V,H));let Ai=!1,vn=!1,gs=!1;const Vt=Lt.getUniforms(),fi=Ve.uniforms;if(Oe.useProgram(Lt.program)&&(Ai=!0,vn=!0,gs=!0),q.id!==N&&(N=q.id,vn=!0),Ai||b!==T){Vt.setValue(U,"projectionMatrix",T.projectionMatrix),Vt.setValue(U,"viewMatrix",T.matrixWorldInverse);const Dn=Vt.map.cameraPosition;Dn!==void 0&&Dn.setValue(U,fe.setFromMatrixPosition(T.matrixWorld)),lt.logarithmicDepthBuffer&&Vt.setValue(U,"logDepthBufFC",2/(Math.log(T.far+1)/Math.LN2)),(q.isMeshPhongMaterial||q.isMeshToonMaterial||q.isMeshLambertMaterial||q.isMeshBasicMaterial||q.isMeshStandardMaterial||q.isShaderMaterial)&&Vt.setValue(U,"isOrthographic",T.isOrthographicCamera===!0),b!==T&&(b=T,vn=!0,gs=!0)}if(H.isSkinnedMesh){Vt.setOptional(U,H,"bindMatrix"),Vt.setOptional(U,H,"bindMatrixInverse");const Dn=H.skeleton;Dn&&(Dn.boneTexture===null&&Dn.computeBoneTexture(),Vt.setValue(U,"boneTexture",Dn.boneTexture,Xe))}H.isBatchedMesh&&(Vt.setOptional(U,H,"batchingTexture"),Vt.setValue(U,"batchingTexture",H._matricesTexture,Xe),Vt.setOptional(U,H,"batchingIdTexture"),Vt.setValue(U,"batchingIdTexture",H._indirectTexture,Xe),Vt.setOptional(U,H,"batchingColorTexture"),H._colorsTexture!==null&&Vt.setValue(U,"batchingColorTexture",H._colorsTexture,Xe));const na=Z.morphAttributes;if((na.position!==void 0||na.normal!==void 0||na.color!==void 0)&&Ze.update(H,Z,Lt),(vn||Ve.receiveShadow!==H.receiveShadow)&&(Ve.receiveShadow=H.receiveShadow,Vt.setValue(U,"receiveShadow",H.receiveShadow)),q.isMeshGouraudMaterial&&q.envMap!==null&&(fi.envMap.value=Ie,fi.flipEnvMap.value=Ie.isCubeTexture&&Ie.isRenderTargetTexture===!1?-1:1),q.isMeshStandardMaterial&&q.envMap===null&&V.environment!==null&&(fi.envMapIntensity.value=V.environmentIntensity),vn&&(Vt.setValue(U,"toneMappingExposure",y.toneMappingExposure),Ve.needsLights&&Ti(fi,gs),he&&q.fog===!0&&Ee.refreshFogUniforms(fi,he),Ee.refreshMaterialUniforms(fi,q,Y,Q,m.state.transmissionRenderTarget[T.id]),Fo.upload(U,ta(Ve),fi,Xe)),q.isShaderMaterial&&q.uniformsNeedUpdate===!0&&(Fo.upload(U,ta(Ve),fi,Xe),q.uniformsNeedUpdate=!1),q.isSpriteMaterial&&Vt.setValue(U,"center",H.center),Vt.setValue(U,"modelViewMatrix",H.modelViewMatrix),Vt.setValue(U,"normalMatrix",H.normalMatrix),Vt.setValue(U,"modelMatrix",H.matrixWorld),q.isShaderMaterial||q.isRawShaderMaterial){const Dn=q.uniformsGroups;for(let Gs=0,ka=Dn.length;Gs<ka;Gs++){const Ha=Dn[Gs];ce.update(Ha,Lt),ce.bind(Ha,Lt)}}return Lt}function Ti(T,V){T.ambientLightColor.needsUpdate=V,T.lightProbe.needsUpdate=V,T.directionalLights.needsUpdate=V,T.directionalLightShadows.needsUpdate=V,T.pointLights.needsUpdate=V,T.pointLightShadows.needsUpdate=V,T.spotLights.needsUpdate=V,T.spotLightShadows.needsUpdate=V,T.rectAreaLights.needsUpdate=V,T.hemisphereLights.needsUpdate=V}function vl(T){return T.isMeshLambertMaterial||T.isMeshToonMaterial||T.isMeshPhongMaterial||T.isMeshStandardMaterial||T.isShadowMaterial||T.isShaderMaterial&&T.lights===!0}this.getActiveCubeFace=function(){return O},this.getActiveMipmapLevel=function(){return A},this.getRenderTarget=function(){return P},this.setRenderTargetTextures=function(T,V,Z){Ye.get(T.texture).__webglTexture=V,Ye.get(T.depthTexture).__webglTexture=Z;const q=Ye.get(T);q.__hasExternalTextures=!0,q.__autoAllocateDepthBuffer=Z===void 0,q.__autoAllocateDepthBuffer||it.has("WEBGL_multisampled_render_to_texture")===!0&&(console.warn("THREE.WebGLRenderer: Render-to-texture extension was disabled because an external texture was provided"),q.__useRenderToTexture=!1)},this.setRenderTargetFramebuffer=function(T,V){const Z=Ye.get(T);Z.__webglFramebuffer=V,Z.__useDefaultFramebuffer=V===void 0},this.setRenderTarget=function(T,V=0,Z=0){P=T,O=V,A=Z;let q=!0,H=null,he=!1,Re=!1;if(T){const Ie=Ye.get(T);if(Ie.__useDefaultFramebuffer!==void 0)Oe.bindFramebuffer(U.FRAMEBUFFER,null),q=!1;else if(Ie.__webglFramebuffer===void 0)Xe.setupRenderTarget(T);else if(Ie.__hasExternalTextures)Xe.rebindTextures(T,Ye.get(T.texture).__webglTexture,Ye.get(T.depthTexture).__webglTexture);else if(T.depthBuffer){const Be=T.depthTexture;if(Ie.__boundDepthTexture!==Be){if(Be!==null&&Ye.has(Be)&&(T.width!==Be.image.width||T.height!==Be.image.height))throw new Error("WebGLRenderTarget: Attached DepthTexture is initialized to the incorrect size.");Xe.setupDepthRenderbuffer(T)}}const Je=T.texture;(Je.isData3DTexture||Je.isDataArrayTexture||Je.isCompressedArrayTexture)&&(Re=!0);const Qe=Ye.get(T).__webglFramebuffer;T.isWebGLCubeRenderTarget?(Array.isArray(Qe[V])?H=Qe[V][Z]:H=Qe[V],he=!0):T.samples>0&&Xe.useMultisampledRTT(T)===!1?H=Ye.get(T).__webglMultisampledFramebuffer:Array.isArray(Qe)?H=Qe[Z]:H=Qe,x.copy(T.viewport),R.copy(T.scissor),j=T.scissorTest}else x.copy(de).multiplyScalar(Y).floor(),R.copy(xe).multiplyScalar(Y).floor(),j=we;if(Oe.bindFramebuffer(U.FRAMEBUFFER,H)&&q&&Oe.drawBuffers(T,H),Oe.viewport(x),Oe.scissor(R),Oe.setScissorTest(j),he){const Ie=Ye.get(T.texture);U.framebufferTexture2D(U.FRAMEBUFFER,U.COLOR_ATTACHMENT0,U.TEXTURE_CUBE_MAP_POSITIVE_X+V,Ie.__webglTexture,Z)}else if(Re){const Ie=Ye.get(T.texture),Je=V||0;U.framebufferTextureLayer(U.FRAMEBUFFER,U.COLOR_ATTACHMENT0,Ie.__webglTexture,Z||0,Je)}N=-1},this.readRenderTargetPixels=function(T,V,Z,q,H,he,Re){if(!(T&&T.isWebGLRenderTarget)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");return}let Pe=Ye.get(T).__webglFramebuffer;if(T.isWebGLCubeRenderTarget&&Re!==void 0&&(Pe=Pe[Re]),Pe){Oe.bindFramebuffer(U.FRAMEBUFFER,Pe);try{const Ie=T.texture,Je=Ie.format,Qe=Ie.type;if(!lt.textureFormatReadable(Je)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in RGBA or implementation defined format.");return}if(!lt.textureTypeReadable(Qe)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in UnsignedByteType or implementation defined type.");return}V>=0&&V<=T.width-q&&Z>=0&&Z<=T.height-H&&U.readPixels(V,Z,q,H,He.convert(Je),He.convert(Qe),he)}finally{const Ie=P!==null?Ye.get(P).__webglFramebuffer:null;Oe.bindFramebuffer(U.FRAMEBUFFER,Ie)}}},this.readRenderTargetPixelsAsync=async function(T,V,Z,q,H,he,Re){if(!(T&&T.isWebGLRenderTarget))throw new Error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");let Pe=Ye.get(T).__webglFramebuffer;if(T.isWebGLCubeRenderTarget&&Re!==void 0&&(Pe=Pe[Re]),Pe){Oe.bindFramebuffer(U.FRAMEBUFFER,Pe);try{const Ie=T.texture,Je=Ie.format,Qe=Ie.type;if(!lt.textureFormatReadable(Je))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in RGBA or implementation defined format.");if(!lt.textureTypeReadable(Qe))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in UnsignedByteType or implementation defined type.");if(V>=0&&V<=T.width-q&&Z>=0&&Z<=T.height-H){const Be=U.createBuffer();U.bindBuffer(U.PIXEL_PACK_BUFFER,Be),U.bufferData(U.PIXEL_PACK_BUFFER,he.byteLength,U.STREAM_READ),U.readPixels(V,Z,q,H,He.convert(Je),He.convert(Qe),0),U.flush();const ct=U.fenceSync(U.SYNC_GPU_COMMANDS_COMPLETE,0);await Rg(U,ct,4);try{U.bindBuffer(U.PIXEL_PACK_BUFFER,Be),U.getBufferSubData(U.PIXEL_PACK_BUFFER,0,he)}finally{U.deleteBuffer(Be),U.deleteSync(ct)}return he}}finally{const Ie=P!==null?Ye.get(P).__webglFramebuffer:null;Oe.bindFramebuffer(U.FRAMEBUFFER,Ie)}}},this.copyFramebufferToTexture=function(T,V=null,Z=0){T.isTexture!==!0&&(Lr("WebGLRenderer: copyFramebufferToTexture function signature has changed."),V=arguments[0]||null,T=arguments[1]);const q=Math.pow(2,-Z),H=Math.floor(T.image.width*q),he=Math.floor(T.image.height*q),Re=V!==null?V.x:0,Pe=V!==null?V.y:0;Xe.setTexture2D(T,0),U.copyTexSubImage2D(U.TEXTURE_2D,Z,0,0,Re,Pe,H,he),Oe.unbindTexture()},this.copyTextureToTexture=function(T,V,Z=null,q=null,H=0){T.isTexture!==!0&&(Lr("WebGLRenderer: copyTextureToTexture function signature has changed."),q=arguments[0]||null,T=arguments[1],V=arguments[2],H=arguments[3]||0,Z=null);let he,Re,Pe,Ie,Je,Qe;Z!==null?(he=Z.max.x-Z.min.x,Re=Z.max.y-Z.min.y,Pe=Z.min.x,Ie=Z.min.y):(he=T.image.width,Re=T.image.height,Pe=0,Ie=0),q!==null?(Je=q.x,Qe=q.y):(Je=0,Qe=0);const Be=He.convert(V.format),ct=He.convert(V.type);Xe.setTexture2D(V,0),U.pixelStorei(U.UNPACK_FLIP_Y_WEBGL,V.flipY),U.pixelStorei(U.UNPACK_PREMULTIPLY_ALPHA_WEBGL,V.premultiplyAlpha),U.pixelStorei(U.UNPACK_ALIGNMENT,V.unpackAlignment);const Rt=U.getParameter(U.UNPACK_ROW_LENGTH),Pt=U.getParameter(U.UNPACK_IMAGE_HEIGHT),pn=U.getParameter(U.UNPACK_SKIP_PIXELS),pt=U.getParameter(U.UNPACK_SKIP_ROWS),Ve=U.getParameter(U.UNPACK_SKIP_IMAGES),Yt=T.isCompressedTexture?T.mipmaps[H]:T.image;U.pixelStorei(U.UNPACK_ROW_LENGTH,Yt.width),U.pixelStorei(U.UNPACK_IMAGE_HEIGHT,Yt.height),U.pixelStorei(U.UNPACK_SKIP_PIXELS,Pe),U.pixelStorei(U.UNPACK_SKIP_ROWS,Ie),T.isDataTexture?U.texSubImage2D(U.TEXTURE_2D,H,Je,Qe,he,Re,Be,ct,Yt.data):T.isCompressedTexture?U.compressedTexSubImage2D(U.TEXTURE_2D,H,Je,Qe,Yt.width,Yt.height,Be,Yt.data):U.texSubImage2D(U.TEXTURE_2D,H,Je,Qe,he,Re,Be,ct,Yt),U.pixelStorei(U.UNPACK_ROW_LENGTH,Rt),U.pixelStorei(U.UNPACK_IMAGE_HEIGHT,Pt),U.pixelStorei(U.UNPACK_SKIP_PIXELS,pn),U.pixelStorei(U.UNPACK_SKIP_ROWS,pt),U.pixelStorei(U.UNPACK_SKIP_IMAGES,Ve),H===0&&V.generateMipmaps&&U.generateMipmap(U.TEXTURE_2D),Oe.unbindTexture()},this.copyTextureToTexture3D=function(T,V,Z=null,q=null,H=0){T.isTexture!==!0&&(Lr("WebGLRenderer: copyTextureToTexture3D function signature has changed."),Z=arguments[0]||null,q=arguments[1]||null,T=arguments[2],V=arguments[3],H=arguments[4]||0);let he,Re,Pe,Ie,Je,Qe,Be,ct,Rt;const Pt=T.isCompressedTexture?T.mipmaps[H]:T.image;Z!==null?(he=Z.max.x-Z.min.x,Re=Z.max.y-Z.min.y,Pe=Z.max.z-Z.min.z,Ie=Z.min.x,Je=Z.min.y,Qe=Z.min.z):(he=Pt.width,Re=Pt.height,Pe=Pt.depth,Ie=0,Je=0,Qe=0),q!==null?(Be=q.x,ct=q.y,Rt=q.z):(Be=0,ct=0,Rt=0);const pn=He.convert(V.format),pt=He.convert(V.type);let Ve;if(V.isData3DTexture)Xe.setTexture3D(V,0),Ve=U.TEXTURE_3D;else if(V.isDataArrayTexture||V.isCompressedArrayTexture)Xe.setTexture2DArray(V,0),Ve=U.TEXTURE_2D_ARRAY;else{console.warn("THREE.WebGLRenderer.copyTextureToTexture3D: only supports THREE.DataTexture3D and THREE.DataTexture2DArray.");return}U.pixelStorei(U.UNPACK_FLIP_Y_WEBGL,V.flipY),U.pixelStorei(U.UNPACK_PREMULTIPLY_ALPHA_WEBGL,V.premultiplyAlpha),U.pixelStorei(U.UNPACK_ALIGNMENT,V.unpackAlignment);const Yt=U.getParameter(U.UNPACK_ROW_LENGTH),mt=U.getParameter(U.UNPACK_IMAGE_HEIGHT),Lt=U.getParameter(U.UNPACK_SKIP_PIXELS),Ai=U.getParameter(U.UNPACK_SKIP_ROWS),vn=U.getParameter(U.UNPACK_SKIP_IMAGES);U.pixelStorei(U.UNPACK_ROW_LENGTH,Pt.width),U.pixelStorei(U.UNPACK_IMAGE_HEIGHT,Pt.height),U.pixelStorei(U.UNPACK_SKIP_PIXELS,Ie),U.pixelStorei(U.UNPACK_SKIP_ROWS,Je),U.pixelStorei(U.UNPACK_SKIP_IMAGES,Qe),T.isDataTexture||T.isData3DTexture?U.texSubImage3D(Ve,H,Be,ct,Rt,he,Re,Pe,pn,pt,Pt.data):V.isCompressedArrayTexture?U.compressedTexSubImage3D(Ve,H,Be,ct,Rt,he,Re,Pe,pn,Pt.data):U.texSubImage3D(Ve,H,Be,ct,Rt,he,Re,Pe,pn,pt,Pt),U.pixelStorei(U.UNPACK_ROW_LENGTH,Yt),U.pixelStorei(U.UNPACK_IMAGE_HEIGHT,mt),U.pixelStorei(U.UNPACK_SKIP_PIXELS,Lt),U.pixelStorei(U.UNPACK_SKIP_ROWS,Ai),U.pixelStorei(U.UNPACK_SKIP_IMAGES,vn),H===0&&V.generateMipmaps&&U.generateMipmap(Ve),Oe.unbindTexture()},this.initRenderTarget=function(T){Ye.get(T).__webglFramebuffer===void 0&&Xe.setupRenderTarget(T)},this.initTexture=function(T){T.isCubeTexture?Xe.setTextureCube(T,0):T.isData3DTexture?Xe.setTexture3D(T,0):T.isDataArrayTexture||T.isCompressedArrayTexture?Xe.setTexture2DArray(T,0):Xe.setTexture2D(T,0),Oe.unbindTexture()},this.resetState=function(){O=0,A=0,P=null,Oe.reset(),F.reset()},typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}get coordinateSystem(){return Oi}get outputColorSpace(){return this._outputColorSpace}set outputColorSpace(e){this._outputColorSpace=e;const t=this.getContext();t.drawingBufferColorSpace=e===vu?"display-p3":"srgb",t.unpackColorSpace=St.workingColorSpace===sl?"display-p3":"srgb"}}class bu{constructor(e,t=25e-5){this.isFogExp2=!0,this.name="",this.color=new nt(e),this.density=t}clone(){return new bu(this.color,this.density)}toJSON(){return{type:"FogExp2",name:this.name,color:this.color.getHex(),density:this.density}}}class Eu extends Jt{constructor(){super(),this.isScene=!0,this.type="Scene",this.background=null,this.environment=null,this.fog=null,this.backgroundBlurriness=0,this.backgroundIntensity=1,this.backgroundRotation=new Si,this.environmentIntensity=1,this.environmentRotation=new Si,this.overrideMaterial=null,typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}copy(e,t){return super.copy(e,t),e.background!==null&&(this.background=e.background.clone()),e.environment!==null&&(this.environment=e.environment.clone()),e.fog!==null&&(this.fog=e.fog.clone()),this.backgroundBlurriness=e.backgroundBlurriness,this.backgroundIntensity=e.backgroundIntensity,this.backgroundRotation.copy(e.backgroundRotation),this.environmentIntensity=e.environmentIntensity,this.environmentRotation.copy(e.environmentRotation),e.overrideMaterial!==null&&(this.overrideMaterial=e.overrideMaterial.clone()),this.matrixAutoUpdate=e.matrixAutoUpdate,this}toJSON(e){const t=super.toJSON(e);return this.fog!==null&&(t.object.fog=this.fog.toJSON()),this.backgroundBlurriness>0&&(t.object.backgroundBlurriness=this.backgroundBlurriness),this.backgroundIntensity!==1&&(t.object.backgroundIntensity=this.backgroundIntensity),t.object.backgroundRotation=this.backgroundRotation.toArray(),this.environmentIntensity!==1&&(t.object.environmentIntensity=this.environmentIntensity),t.object.environmentRotation=this.environmentRotation.toArray(),t}}class By{constructor(e,t){this.isInterleavedBuffer=!0,this.array=e,this.stride=t,this.count=e!==void 0?e.length/t:0,this.usage=Kc,this._updateRange={offset:0,count:-1},this.updateRanges=[],this.version=0,this.uuid=zi()}onUploadCallback(){}set needsUpdate(e){e===!0&&this.version++}get updateRange(){return Lr("THREE.InterleavedBuffer: updateRange() is deprecated and will be removed in r169. Use addUpdateRange() instead."),this._updateRange}setUsage(e){return this.usage=e,this}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}copy(e){return this.array=new e.array.constructor(e.array),this.count=e.count,this.stride=e.stride,this.usage=e.usage,this}copyAt(e,t,n){e*=this.stride,n*=t.stride;for(let s=0,r=this.stride;s<r;s++)this.array[e+s]=t.array[n+s];return this}set(e,t=0){return this.array.set(e,t),this}clone(e){e.arrayBuffers===void 0&&(e.arrayBuffers={}),this.array.buffer._uuid===void 0&&(this.array.buffer._uuid=zi()),e.arrayBuffers[this.array.buffer._uuid]===void 0&&(e.arrayBuffers[this.array.buffer._uuid]=this.array.slice(0).buffer);const t=new this.array.constructor(e.arrayBuffers[this.array.buffer._uuid]),n=new this.constructor(t,this.stride);return n.setUsage(this.usage),n}onUpload(e){return this.onUploadCallback=e,this}toJSON(e){return e.arrayBuffers===void 0&&(e.arrayBuffers={}),this.array.buffer._uuid===void 0&&(this.array.buffer._uuid=zi()),e.arrayBuffers[this.array.buffer._uuid]===void 0&&(e.arrayBuffers[this.array.buffer._uuid]=Array.from(new Uint32Array(this.array.buffer))),{uuid:this.uuid,buffer:this.array.buffer._uuid,type:this.array.constructor.name,stride:this.stride}}}const Cn=new k;class Xo{constructor(e,t,n,s=!1){this.isInterleavedBufferAttribute=!0,this.name="",this.data=e,this.itemSize=t,this.offset=n,this.normalized=s}get count(){return this.data.count}get array(){return this.data.array}set needsUpdate(e){this.data.needsUpdate=e}applyMatrix4(e){for(let t=0,n=this.data.count;t<n;t++)Cn.fromBufferAttribute(this,t),Cn.applyMatrix4(e),this.setXYZ(t,Cn.x,Cn.y,Cn.z);return this}applyNormalMatrix(e){for(let t=0,n=this.count;t<n;t++)Cn.fromBufferAttribute(this,t),Cn.applyNormalMatrix(e),this.setXYZ(t,Cn.x,Cn.y,Cn.z);return this}transformDirection(e){for(let t=0,n=this.count;t<n;t++)Cn.fromBufferAttribute(this,t),Cn.transformDirection(e),this.setXYZ(t,Cn.x,Cn.y,Cn.z);return this}getComponent(e,t){let n=this.array[e*this.data.stride+this.offset+t];return this.normalized&&(n=oi(n,this.array)),n}setComponent(e,t,n){return this.normalized&&(n=wt(n,this.array)),this.data.array[e*this.data.stride+this.offset+t]=n,this}setX(e,t){return this.normalized&&(t=wt(t,this.array)),this.data.array[e*this.data.stride+this.offset]=t,this}setY(e,t){return this.normalized&&(t=wt(t,this.array)),this.data.array[e*this.data.stride+this.offset+1]=t,this}setZ(e,t){return this.normalized&&(t=wt(t,this.array)),this.data.array[e*this.data.stride+this.offset+2]=t,this}setW(e,t){return this.normalized&&(t=wt(t,this.array)),this.data.array[e*this.data.stride+this.offset+3]=t,this}getX(e){let t=this.data.array[e*this.data.stride+this.offset];return this.normalized&&(t=oi(t,this.array)),t}getY(e){let t=this.data.array[e*this.data.stride+this.offset+1];return this.normalized&&(t=oi(t,this.array)),t}getZ(e){let t=this.data.array[e*this.data.stride+this.offset+2];return this.normalized&&(t=oi(t,this.array)),t}getW(e){let t=this.data.array[e*this.data.stride+this.offset+3];return this.normalized&&(t=oi(t,this.array)),t}setXY(e,t,n){return e=e*this.data.stride+this.offset,this.normalized&&(t=wt(t,this.array),n=wt(n,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this}setXYZ(e,t,n,s){return e=e*this.data.stride+this.offset,this.normalized&&(t=wt(t,this.array),n=wt(n,this.array),s=wt(s,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this.data.array[e+2]=s,this}setXYZW(e,t,n,s,r){return e=e*this.data.stride+this.offset,this.normalized&&(t=wt(t,this.array),n=wt(n,this.array),s=wt(s,this.array),r=wt(r,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this.data.array[e+2]=s,this.data.array[e+3]=r,this}clone(e){if(e===void 0){console.log("THREE.InterleavedBufferAttribute.clone(): Cloning an interleaved buffer attribute will de-interleave buffer data.");const t=[];for(let n=0;n<this.count;n++){const s=n*this.data.stride+this.offset;for(let r=0;r<this.itemSize;r++)t.push(this.data.array[s+r])}return new ui(new this.array.constructor(t),this.itemSize,this.normalized)}else return e.interleavedBuffers===void 0&&(e.interleavedBuffers={}),e.interleavedBuffers[this.data.uuid]===void 0&&(e.interleavedBuffers[this.data.uuid]=this.data.clone(e)),new Xo(e.interleavedBuffers[this.data.uuid],this.itemSize,this.offset,this.normalized)}toJSON(e){if(e===void 0){console.log("THREE.InterleavedBufferAttribute.toJSON(): Serializing an interleaved buffer attribute will de-interleave buffer data.");const t=[];for(let n=0;n<this.count;n++){const s=n*this.data.stride+this.offset;for(let r=0;r<this.itemSize;r++)t.push(this.data.array[s+r])}return{itemSize:this.itemSize,type:this.array.constructor.name,array:t,normalized:this.normalized}}else return e.interleavedBuffers===void 0&&(e.interleavedBuffers={}),e.interleavedBuffers[this.data.uuid]===void 0&&(e.interleavedBuffers[this.data.uuid]=this.data.toJSON(e)),{isInterleavedBufferAttribute:!0,itemSize:this.itemSize,data:this.data.uuid,offset:this.offset,normalized:this.normalized}}}class ks extends ps{constructor(e){super(),this.isSpriteMaterial=!0,this.type="SpriteMaterial",this.color=new nt(16777215),this.map=null,this.alphaMap=null,this.rotation=0,this.sizeAttenuation=!0,this.transparent=!0,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.alphaMap=e.alphaMap,this.rotation=e.rotation,this.sizeAttenuation=e.sizeAttenuation,this.fog=e.fog,this}}let vr;const fa=new k,xr=new k,yr=new k,Mr=new qe,pa=new qe,ep=new Ot,go=new k,ma=new k,_o=new k,dd=new qe,ic=new qe,fd=new qe;class tp extends Jt{constructor(e=new ks){if(super(),this.isSprite=!0,this.type="Sprite",vr===void 0){vr=new Xt;const t=new Float32Array([-.5,-.5,0,0,0,.5,-.5,0,1,0,.5,.5,0,1,1,-.5,.5,0,0,1]),n=new By(t,5);vr.setIndex([0,1,2,0,2,3]),vr.setAttribute("position",new Xo(n,3,0,!1)),vr.setAttribute("uv",new Xo(n,2,3,!1))}this.geometry=vr,this.material=e,this.center=new qe(.5,.5)}raycast(e,t){e.camera===null&&console.error('THREE.Sprite: "Raycaster.camera" needs to be set in order to raycast against sprites.'),xr.setFromMatrixScale(this.matrixWorld),ep.copy(e.camera.matrixWorld),this.modelViewMatrix.multiplyMatrices(e.camera.matrixWorldInverse,this.matrixWorld),yr.setFromMatrixPosition(this.modelViewMatrix),e.camera.isPerspectiveCamera&&this.material.sizeAttenuation===!1&&xr.multiplyScalar(-yr.z);const n=this.material.rotation;let s,r;n!==0&&(r=Math.cos(n),s=Math.sin(n));const a=this.center;vo(go.set(-.5,-.5,0),yr,a,xr,s,r),vo(ma.set(.5,-.5,0),yr,a,xr,s,r),vo(_o.set(.5,.5,0),yr,a,xr,s,r),dd.set(0,0),ic.set(1,0),fd.set(1,1);let o=e.ray.intersectTriangle(go,ma,_o,!1,fa);if(o===null&&(vo(ma.set(-.5,.5,0),yr,a,xr,s,r),ic.set(0,1),o=e.ray.intersectTriangle(go,_o,ma,!1,fa),o===null))return;const l=e.ray.origin.distanceTo(fa);l<e.near||l>e.far||t.push({distance:l,point:fa.clone(),uv:jn.getInterpolation(fa,go,ma,_o,dd,ic,fd,new qe),face:null,object:this})}copy(e,t){return super.copy(e,t),e.center!==void 0&&this.center.copy(e.center),this.material=e.material,this}}function vo(i,e,t,n,s,r){Mr.subVectors(i,t).addScalar(.5).multiply(n),s!==void 0?(pa.x=r*Mr.x-s*Mr.y,pa.y=s*Mr.x+r*Mr.y):pa.copy(Mr),i.copy(e),i.x+=pa.x,i.y+=pa.y,i.applyMatrix4(ep)}class ki extends ps{constructor(e){super(),this.isLineBasicMaterial=!0,this.type="LineBasicMaterial",this.color=new nt(16777215),this.map=null,this.linewidth=1,this.linecap="round",this.linejoin="round",this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.linewidth=e.linewidth,this.linecap=e.linecap,this.linejoin=e.linejoin,this.fog=e.fog,this}}const qo=new k,Yo=new k,pd=new Ot,ga=new Fa,xo=new Na,sc=new k,md=new k;class $o extends Jt{constructor(e=new Xt,t=new ki){super(),this.isLine=!0,this.type="Line",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}computeLineDistances(){const e=this.geometry;if(e.index===null){const t=e.attributes.position,n=[0];for(let s=1,r=t.count;s<r;s++)qo.fromBufferAttribute(t,s-1),Yo.fromBufferAttribute(t,s),n[s]=n[s-1],n[s]+=qo.distanceTo(Yo);e.setAttribute("lineDistance",new qt(n,1))}else console.warn("THREE.Line.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.");return this}raycast(e,t){const n=this.geometry,s=this.matrixWorld,r=e.params.Line.threshold,a=n.drawRange;if(n.boundingSphere===null&&n.computeBoundingSphere(),xo.copy(n.boundingSphere),xo.applyMatrix4(s),xo.radius+=r,e.ray.intersectsSphere(xo)===!1)return;pd.copy(s).invert(),ga.copy(e.ray).applyMatrix4(pd);const o=r/((this.scale.x+this.scale.y+this.scale.z)/3),l=o*o,c=this.isLineSegments?2:1,u=n.index,d=n.attributes.position;if(u!==null){const f=Math.max(0,a.start),g=Math.min(u.count,a.start+a.count);for(let v=f,m=g-1;v<m;v+=c){const p=u.getX(v),S=u.getX(v+1),y=yo(this,e,ga,l,p,S);y&&t.push(y)}if(this.isLineLoop){const v=u.getX(g-1),m=u.getX(f),p=yo(this,e,ga,l,v,m);p&&t.push(p)}}else{const f=Math.max(0,a.start),g=Math.min(d.count,a.start+a.count);for(let v=f,m=g-1;v<m;v+=c){const p=yo(this,e,ga,l,v,v+1);p&&t.push(p)}if(this.isLineLoop){const v=yo(this,e,ga,l,g-1,f);v&&t.push(v)}}}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const s=t[n[0]];if(s!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let r=0,a=s.length;r<a;r++){const o=s[r].name||String(r);this.morphTargetInfluences.push(0),this.morphTargetDictionary[o]=r}}}}}function yo(i,e,t,n,s,r){const a=i.geometry.attributes.position;if(qo.fromBufferAttribute(a,s),Yo.fromBufferAttribute(a,r),t.distanceSqToSegment(qo,Yo,sc,md)>n)return;sc.applyMatrix4(i.matrixWorld);const l=e.ray.origin.distanceTo(sc);if(!(l<e.near||l>e.far))return{distance:l,point:md.clone().applyMatrix4(i.matrixWorld),index:s,face:null,faceIndex:null,object:i}}const gd=new k,_d=new k;class Nr extends $o{constructor(e,t){super(e,t),this.isLineSegments=!0,this.type="LineSegments"}computeLineDistances(){const e=this.geometry;if(e.index===null){const t=e.attributes.position,n=[];for(let s=0,r=t.count;s<r;s+=2)gd.fromBufferAttribute(t,s),_d.fromBufferAttribute(t,s+1),n[s]=s===0?0:n[s-1],n[s+1]=n[s]+gd.distanceTo(_d);e.setAttribute("lineDistance",new qt(n,1))}else console.warn("THREE.LineSegments.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.");return this}}class wu extends ps{constructor(e){super(),this.isPointsMaterial=!0,this.type="PointsMaterial",this.color=new nt(16777215),this.map=null,this.alphaMap=null,this.size=1,this.sizeAttenuation=!0,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.alphaMap=e.alphaMap,this.size=e.size,this.sizeAttenuation=e.sizeAttenuation,this.fog=e.fog,this}}const vd=new Ot,Qc=new Fa,Mo=new Na,So=new k;class np extends Jt{constructor(e=new Xt,t=new wu){super(),this.isPoints=!0,this.type="Points",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}raycast(e,t){const n=this.geometry,s=this.matrixWorld,r=e.params.Points.threshold,a=n.drawRange;if(n.boundingSphere===null&&n.computeBoundingSphere(),Mo.copy(n.boundingSphere),Mo.applyMatrix4(s),Mo.radius+=r,e.ray.intersectsSphere(Mo)===!1)return;vd.copy(s).invert(),Qc.copy(e.ray).applyMatrix4(vd);const o=r/((this.scale.x+this.scale.y+this.scale.z)/3),l=o*o,c=n.index,h=n.attributes.position;if(c!==null){const d=Math.max(0,a.start),f=Math.min(c.count,a.start+a.count);for(let g=d,v=f;g<v;g++){const m=c.getX(g);So.fromBufferAttribute(h,m),xd(So,m,l,s,e,t,this)}}else{const d=Math.max(0,a.start),f=Math.min(h.count,a.start+a.count);for(let g=d,v=f;g<v;g++)So.fromBufferAttribute(h,g),xd(So,g,l,s,e,t,this)}}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const s=t[n[0]];if(s!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let r=0,a=s.length;r<a;r++){const o=s[r].name||String(r);this.morphTargetInfluences.push(0),this.morphTargetDictionary[o]=r}}}}}function xd(i,e,t,n,s,r,a){const o=Qc.distanceSqToPoint(i);if(o<t){const l=new k;Qc.closestPointToPoint(i,l),l.applyMatrix4(n);const c=s.ray.origin.distanceTo(l);if(c<s.near||c>s.far)return;r.push({distance:c,distanceToRay:Math.sqrt(o),point:l,index:e,face:null,object:a})}}class Tu extends Ln{constructor(e,t,n,s,r,a,o,l,c){super(e,t,n,s,r,a,o,l,c),this.isCanvasTexture=!0,this.needsUpdate=!0}}const bo=new k,Eo=new k,rc=new k,wo=new jn;class zy extends Xt{constructor(e=null,t=1){if(super(),this.type="EdgesGeometry",this.parameters={geometry:e,thresholdAngle:t},e!==null){const s=Math.pow(10,4),r=Math.cos(Pr*t),a=e.getIndex(),o=e.getAttribute("position"),l=a?a.count:o.count,c=[0,0,0],u=["a","b","c"],h=new Array(3),d={},f=[];for(let g=0;g<l;g+=3){a?(c[0]=a.getX(g),c[1]=a.getX(g+1),c[2]=a.getX(g+2)):(c[0]=g,c[1]=g+1,c[2]=g+2);const{a:v,b:m,c:p}=wo;if(v.fromBufferAttribute(o,c[0]),m.fromBufferAttribute(o,c[1]),p.fromBufferAttribute(o,c[2]),wo.getNormal(rc),h[0]=`${Math.round(v.x*s)},${Math.round(v.y*s)},${Math.round(v.z*s)}`,h[1]=`${Math.round(m.x*s)},${Math.round(m.y*s)},${Math.round(m.z*s)}`,h[2]=`${Math.round(p.x*s)},${Math.round(p.y*s)},${Math.round(p.z*s)}`,!(h[0]===h[1]||h[1]===h[2]||h[2]===h[0]))for(let S=0;S<3;S++){const y=(S+1)%3,w=h[S],O=h[y],A=wo[u[S]],P=wo[u[y]],N=`${w}_${O}`,b=`${O}_${w}`;b in d&&d[b]?(rc.dot(d[b].normal)<=r&&(f.push(A.x,A.y,A.z),f.push(P.x,P.y,P.z)),d[b]=null):N in d||(d[N]={index0:c[S],index1:c[y],normal:rc.clone()})}}for(const g in d)if(d[g]){const{index0:v,index1:m}=d[g];bo.fromBufferAttribute(o,v),Eo.fromBufferAttribute(o,m),f.push(bo.x,bo.y,bo.z),f.push(Eo.x,Eo.y,Eo.z)}this.setAttribute("position",new qt(f,3))}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}}class Au extends Xt{constructor(e=.5,t=1,n=32,s=1,r=0,a=Math.PI*2){super(),this.type="RingGeometry",this.parameters={innerRadius:e,outerRadius:t,thetaSegments:n,phiSegments:s,thetaStart:r,thetaLength:a},n=Math.max(3,n),s=Math.max(1,s);const o=[],l=[],c=[],u=[];let h=e;const d=(t-e)/s,f=new k,g=new qe;for(let v=0;v<=s;v++){for(let m=0;m<=n;m++){const p=r+m/n*a;f.x=h*Math.cos(p),f.y=h*Math.sin(p),l.push(f.x,f.y,f.z),c.push(0,0,1),g.x=(f.x/t+1)/2,g.y=(f.y/t+1)/2,u.push(g.x,g.y)}h+=d}for(let v=0;v<s;v++){const m=v*(n+1);for(let p=0;p<n;p++){const S=p+m,y=S,w=S+n+1,O=S+n+2,A=S+1;o.push(y,w,A),o.push(w,O,A)}}this.setIndex(o),this.setAttribute("position",new qt(l,3)),this.setAttribute("normal",new qt(c,3)),this.setAttribute("uv",new qt(u,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Au(e.innerRadius,e.outerRadius,e.thetaSegments,e.phiSegments,e.thetaStart,e.thetaLength)}}class Oo extends ps{constructor(e){super(),this.isMeshStandardMaterial=!0,this.defines={STANDARD:""},this.type="MeshStandardMaterial",this.color=new nt(16777215),this.roughness=1,this.metalness=0,this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.emissive=new nt(0),this.emissiveIntensity=1,this.emissiveMap=null,this.bumpMap=null,this.bumpScale=1,this.normalMap=null,this.normalMapType=Ff,this.normalScale=new qe(1,1),this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.roughnessMap=null,this.metalnessMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new Si,this.envMapIntensity=1,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.flatShading=!1,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.defines={STANDARD:""},this.color.copy(e.color),this.roughness=e.roughness,this.metalness=e.metalness,this.map=e.map,this.lightMap=e.lightMap,this.lightMapIntensity=e.lightMapIntensity,this.aoMap=e.aoMap,this.aoMapIntensity=e.aoMapIntensity,this.emissive.copy(e.emissive),this.emissiveMap=e.emissiveMap,this.emissiveIntensity=e.emissiveIntensity,this.bumpMap=e.bumpMap,this.bumpScale=e.bumpScale,this.normalMap=e.normalMap,this.normalMapType=e.normalMapType,this.normalScale.copy(e.normalScale),this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this.roughnessMap=e.roughnessMap,this.metalnessMap=e.metalnessMap,this.alphaMap=e.alphaMap,this.envMap=e.envMap,this.envMapRotation.copy(e.envMapRotation),this.envMapIntensity=e.envMapIntensity,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.wireframeLinecap=e.wireframeLinecap,this.wireframeLinejoin=e.wireframeLinejoin,this.flatShading=e.flatShading,this.fog=e.fog,this}}class ip extends ki{constructor(e){super(),this.isLineDashedMaterial=!0,this.type="LineDashedMaterial",this.scale=1,this.dashSize=3,this.gapSize=1,this.setValues(e)}copy(e){return super.copy(e),this.scale=e.scale,this.dashSize=e.dashSize,this.gapSize=e.gapSize,this}}class Cu extends Jt{constructor(e,t=1){super(),this.isLight=!0,this.type="Light",this.color=new nt(e),this.intensity=t}dispose(){}copy(e,t){return super.copy(e,t),this.color.copy(e.color),this.intensity=e.intensity,this}toJSON(e){const t=super.toJSON(e);return t.object.color=this.color.getHex(),t.object.intensity=this.intensity,this.groundColor!==void 0&&(t.object.groundColor=this.groundColor.getHex()),this.distance!==void 0&&(t.object.distance=this.distance),this.angle!==void 0&&(t.object.angle=this.angle),this.decay!==void 0&&(t.object.decay=this.decay),this.penumbra!==void 0&&(t.object.penumbra=this.penumbra),this.shadow!==void 0&&(t.object.shadow=this.shadow.toJSON()),this.target!==void 0&&(t.object.target=this.target.uuid),t}}class ky extends Cu{constructor(e,t,n){super(e,n),this.isHemisphereLight=!0,this.type="HemisphereLight",this.position.copy(Jt.DEFAULT_UP),this.updateMatrix(),this.groundColor=new nt(t)}copy(e,t){return super.copy(e,t),this.groundColor.copy(e.groundColor),this}}const ac=new Ot,yd=new k,Md=new k;class Hy{constructor(e){this.camera=e,this.intensity=1,this.bias=0,this.normalBias=0,this.radius=1,this.blurSamples=8,this.mapSize=new qe(512,512),this.map=null,this.mapPass=null,this.matrix=new Ot,this.autoUpdate=!0,this.needsUpdate=!1,this._frustum=new Mu,this._frameExtents=new qe(1,1),this._viewportCount=1,this._viewports=[new tn(0,0,1,1)]}getViewportCount(){return this._viewportCount}getFrustum(){return this._frustum}updateMatrices(e){const t=this.camera,n=this.matrix;yd.setFromMatrixPosition(e.matrixWorld),t.position.copy(yd),Md.setFromMatrixPosition(e.target.matrixWorld),t.lookAt(Md),t.updateMatrixWorld(),ac.multiplyMatrices(t.projectionMatrix,t.matrixWorldInverse),this._frustum.setFromProjectionMatrix(ac),n.set(.5,0,0,.5,0,.5,0,.5,0,0,.5,.5,0,0,0,1),n.multiply(ac)}getViewport(e){return this._viewports[e]}getFrameExtents(){return this._frameExtents}dispose(){this.map&&this.map.dispose(),this.mapPass&&this.mapPass.dispose()}copy(e){return this.camera=e.camera.clone(),this.intensity=e.intensity,this.bias=e.bias,this.radius=e.radius,this.mapSize.copy(e.mapSize),this}clone(){return new this.constructor().copy(this)}toJSON(){const e={};return this.intensity!==1&&(e.intensity=this.intensity),this.bias!==0&&(e.bias=this.bias),this.normalBias!==0&&(e.normalBias=this.normalBias),this.radius!==1&&(e.radius=this.radius),(this.mapSize.x!==512||this.mapSize.y!==512)&&(e.mapSize=this.mapSize.toArray()),e.camera=this.camera.toJSON(!1).object,delete e.camera.matrix,e}}class Vy extends Hy{constructor(){super(new Ur(-5,5,5,-5,.5,500)),this.isDirectionalLightShadow=!0}}class Gy extends Cu{constructor(e,t){super(e,t),this.isDirectionalLight=!0,this.type="DirectionalLight",this.position.copy(Jt.DEFAULT_UP),this.updateMatrix(),this.target=new Jt,this.shadow=new Vy}dispose(){this.shadow.dispose()}copy(e){return super.copy(e),this.target=e.target.clone(),this.shadow=e.shadow.clone(),this}}class Wy extends Cu{constructor(e,t){super(e,t),this.isAmbientLight=!0,this.type="AmbientLight"}}const Sd=new Ot;class Xy{constructor(e,t,n=0,s=1/0){this.ray=new Fa(e,t),this.near=n,this.far=s,this.camera=null,this.layers=new yu,this.params={Mesh:{},Line:{threshold:1},LOD:{},Points:{threshold:1},Sprite:{}}}set(e,t){this.ray.set(e,t)}setFromCamera(e,t){t.isPerspectiveCamera?(this.ray.origin.setFromMatrixPosition(t.matrixWorld),this.ray.direction.set(e.x,e.y,.5).unproject(t).sub(this.ray.origin).normalize(),this.camera=t):t.isOrthographicCamera?(this.ray.origin.set(e.x,e.y,(t.near+t.far)/(t.near-t.far)).unproject(t),this.ray.direction.set(0,0,-1).transformDirection(t.matrixWorld),this.camera=t):console.error("THREE.Raycaster: Unsupported camera type: "+t.type)}setFromXRController(e){return Sd.identity().extractRotation(e.matrixWorld),this.ray.origin.setFromMatrixPosition(e.matrixWorld),this.ray.direction.set(0,0,-1).applyMatrix4(Sd),this}intersectObject(e,t=!0,n=[]){return eu(e,this,n,t),n.sort(bd),n}intersectObjects(e,t=!0,n=[]){for(let s=0,r=e.length;s<r;s++)eu(e[s],this,n,t);return n.sort(bd),n}}function bd(i,e){return i.distance-e.distance}function eu(i,e,t,n){let s=!0;if(i.layers.test(e.layers)&&i.raycast(e,t)===!1&&(s=!1),s===!0&&n===!0){const r=i.children;for(let a=0,o=r.length;a<o;a++)eu(r[a],e,t,!0)}}class Ed{constructor(e=1,t=0,n=0){return this.radius=e,this.phi=t,this.theta=n,this}set(e,t,n){return this.radius=e,this.phi=t,this.theta=n,this}copy(e){return this.radius=e.radius,this.phi=e.phi,this.theta=e.theta,this}makeSafe(){return this.phi=Math.max(1e-6,Math.min(Math.PI-1e-6,this.phi)),this}setFromVector3(e){return this.setFromCartesianCoords(e.x,e.y,e.z)}setFromCartesianCoords(e,t,n){return this.radius=Math.sqrt(e*e+t*t+n*n),this.radius===0?(this.theta=0,this.phi=0):(this.theta=Math.atan2(e,n),this.phi=Math.acos(Mn(t/this.radius,-1,1))),this}clone(){return new this.constructor().copy(this)}}class qy extends Nr{constructor(e=10,t=10,n=4473924,s=8947848){n=new nt(n),s=new nt(s);const r=t/2,a=e/t,o=e/2,l=[],c=[];for(let d=0,f=0,g=-o;d<=t;d++,g+=a){l.push(-o,0,g,o,0,g),l.push(g,0,-o,g,0,o);const v=d===r?n:s;v.toArray(c,f),f+=3,v.toArray(c,f),f+=3,v.toArray(c,f),f+=3,v.toArray(c,f),f+=3}const u=new Xt;u.setAttribute("position",new qt(l,3)),u.setAttribute("color",new qt(c,3));const h=new ki({vertexColors:!0,toneMapped:!1});super(u,h),this.type="GridHelper"}dispose(){this.geometry.dispose(),this.material.dispose()}}typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("register",{detail:{revision:hu}}));typeof window<"u"&&(window.__THREE__?console.warn("WARNING: Multiple instances of Three.js being imported."):window.__THREE__=hu);var Yy=Object.defineProperty,$y=(i,e,t)=>e in i?Yy(i,e,{enumerable:!0,configurable:!0,writable:!0,value:t}):i[e]=t,jy=(i,e,t)=>($y(i,e+"",t),t);class Ky{constructor(){jy(this,"_listeners")}addEventListener(e,t){this._listeners===void 0&&(this._listeners={});const n=this._listeners;n[e]===void 0&&(n[e]=[]),n[e].indexOf(t)===-1&&n[e].push(t)}hasEventListener(e,t){if(this._listeners===void 0)return!1;const n=this._listeners;return n[e]!==void 0&&n[e].indexOf(t)!==-1}removeEventListener(e,t){if(this._listeners===void 0)return;const s=this._listeners[e];if(s!==void 0){const r=s.indexOf(t);r!==-1&&s.splice(r,1)}}dispatchEvent(e){if(this._listeners===void 0)return;const n=this._listeners[e.type];if(n!==void 0){e.target=this;const s=n.slice(0);for(let r=0,a=s.length;r<a;r++)s[r].call(this,e);e.target=null}}}var Zy=Object.defineProperty,Jy=(i,e,t)=>e in i?Zy(i,e,{enumerable:!0,configurable:!0,writable:!0,value:t}):i[e]=t,$e=(i,e,t)=>(Jy(i,typeof e!="symbol"?e+"":e,t),t);const To=new Fa,wd=new is,Qy=Math.cos(70*(Math.PI/180)),Td=(i,e)=>(i%e+e)%e;class eM extends Ky{constructor(e,t){super(),$e(this,"object"),$e(this,"domElement"),$e(this,"enabled",!0),$e(this,"target",new k),$e(this,"minDistance",0),$e(this,"maxDistance",1/0),$e(this,"minZoom",0),$e(this,"maxZoom",1/0),$e(this,"minPolarAngle",0),$e(this,"maxPolarAngle",Math.PI),$e(this,"minAzimuthAngle",-1/0),$e(this,"maxAzimuthAngle",1/0),$e(this,"enableDamping",!1),$e(this,"dampingFactor",.05),$e(this,"enableZoom",!0),$e(this,"zoomSpeed",1),$e(this,"enableRotate",!0),$e(this,"rotateSpeed",1),$e(this,"enablePan",!0),$e(this,"panSpeed",1),$e(this,"screenSpacePanning",!0),$e(this,"keyPanSpeed",7),$e(this,"zoomToCursor",!1),$e(this,"autoRotate",!1),$e(this,"autoRotateSpeed",2),$e(this,"reverseOrbit",!1),$e(this,"reverseHorizontalOrbit",!1),$e(this,"reverseVerticalOrbit",!1),$e(this,"keys",{LEFT:"ArrowLeft",UP:"ArrowUp",RIGHT:"ArrowRight",BOTTOM:"ArrowDown"}),$e(this,"mouseButtons",{LEFT:Qs.ROTATE,MIDDLE:Qs.DOLLY,RIGHT:Qs.PAN}),$e(this,"touches",{ONE:er.ROTATE,TWO:er.DOLLY_PAN}),$e(this,"target0"),$e(this,"position0"),$e(this,"zoom0"),$e(this,"_domElementKeyEvents",null),$e(this,"getPolarAngle"),$e(this,"getAzimuthalAngle"),$e(this,"setPolarAngle"),$e(this,"setAzimuthalAngle"),$e(this,"getDistance"),$e(this,"getZoomScale"),$e(this,"listenToKeyEvents"),$e(this,"stopListenToKeyEvents"),$e(this,"saveState"),$e(this,"reset"),$e(this,"update"),$e(this,"connect"),$e(this,"dispose"),$e(this,"dollyIn"),$e(this,"dollyOut"),$e(this,"getScale"),$e(this,"setScale"),this.object=e,this.domElement=t,this.target0=this.target.clone(),this.position0=this.object.position.clone(),this.zoom0=this.object.zoom,this.getPolarAngle=()=>u.phi,this.getAzimuthalAngle=()=>u.theta,this.setPolarAngle=F=>{let ce=Td(F,2*Math.PI),I=u.phi;I<0&&(I+=2*Math.PI),ce<0&&(ce+=2*Math.PI);let ae=Math.abs(ce-I);2*Math.PI-ae<ae&&(ce<I?ce+=2*Math.PI:I+=2*Math.PI),h.phi=ce-I,n.update()},this.setAzimuthalAngle=F=>{let ce=Td(F,2*Math.PI),I=u.theta;I<0&&(I+=2*Math.PI),ce<0&&(ce+=2*Math.PI);let ae=Math.abs(ce-I);2*Math.PI-ae<ae&&(ce<I?ce+=2*Math.PI:I+=2*Math.PI),h.theta=ce-I,n.update()},this.getDistance=()=>n.object.position.distanceTo(n.target),this.listenToKeyEvents=F=>{F.addEventListener("keydown",Ae),this._domElementKeyEvents=F},this.stopListenToKeyEvents=()=>{this._domElementKeyEvents.removeEventListener("keydown",Ae),this._domElementKeyEvents=null},this.saveState=()=>{n.target0.copy(n.target),n.position0.copy(n.object.position),n.zoom0=n.object.zoom},this.reset=()=>{n.target.copy(n.target0),n.object.position.copy(n.position0),n.object.zoom=n.zoom0,n.object.updateProjectionMatrix(),n.dispatchEvent(s),n.update(),l=o.NONE},this.update=(()=>{const F=new k,ce=new k(0,1,0),I=new zs().setFromUnitVectors(e.up,ce),ae=I.clone().invert(),se=new k,re=new zs,ve=2*Math.PI;return function(){const at=n.object.position;I.setFromUnitVectors(e.up,ce),ae.copy(I).invert(),F.copy(at).sub(n.target),F.applyQuaternion(I),u.setFromVector3(F),n.autoRotate&&l===o.NONE&&K(j()),n.enableDamping?(u.theta+=h.theta*n.dampingFactor,u.phi+=h.phi*n.dampingFactor):(u.theta+=h.theta,u.phi+=h.phi);let gt=n.minAzimuthAngle,Et=n.maxAzimuthAngle;isFinite(gt)&&isFinite(Et)&&(gt<-Math.PI?gt+=ve:gt>Math.PI&&(gt-=ve),Et<-Math.PI?Et+=ve:Et>Math.PI&&(Et-=ve),gt<=Et?u.theta=Math.max(gt,Math.min(Et,u.theta)):u.theta=u.theta>(gt+Et)/2?Math.max(gt,u.theta):Math.min(Et,u.theta)),u.phi=Math.max(n.minPolarAngle,Math.min(n.maxPolarAngle,u.phi)),u.makeSafe(),n.enableDamping===!0?n.target.addScaledVector(f,n.dampingFactor):n.target.add(f),n.zoomToCursor&&b||n.object.isOrthographicCamera?u.radius=ye(u.radius):u.radius=ye(u.radius*d),F.setFromSpherical(u),F.applyQuaternion(ae),at.copy(n.target).add(F),n.object.matrixAutoUpdate||n.object.updateMatrix(),n.object.lookAt(n.target),n.enableDamping===!0?(h.theta*=1-n.dampingFactor,h.phi*=1-n.dampingFactor,f.multiplyScalar(1-n.dampingFactor)):(h.set(0,0,0),f.set(0,0,0));let ot=!1;if(n.zoomToCursor&&b){let fn=null;if(n.object instanceof Sn&&n.object.isPerspectiveCamera){const Bt=F.length();fn=ye(Bt*d);const zt=Bt-fn;n.object.position.addScaledVector(P,zt),n.object.updateMatrixWorld()}else if(n.object.isOrthographicCamera){const Bt=new k(N.x,N.y,0);Bt.unproject(n.object),n.object.zoom=Math.max(n.minZoom,Math.min(n.maxZoom,n.object.zoom/d)),n.object.updateProjectionMatrix(),ot=!0;const zt=new k(N.x,N.y,0);zt.unproject(n.object),n.object.position.sub(zt).add(Bt),n.object.updateMatrixWorld(),fn=F.length()}else console.warn("WARNING: OrbitControls.js encountered an unknown camera type - zoom to cursor disabled."),n.zoomToCursor=!1;fn!==null&&(n.screenSpacePanning?n.target.set(0,0,-1).transformDirection(n.object.matrix).multiplyScalar(fn).add(n.object.position):(To.origin.copy(n.object.position),To.direction.set(0,0,-1).transformDirection(n.object.matrix),Math.abs(n.object.up.dot(To.direction))<Qy?e.lookAt(n.target):(wd.setFromNormalAndCoplanarPoint(n.object.up,n.target),To.intersectPlane(wd,n.target))))}else n.object instanceof Ur&&n.object.isOrthographicCamera&&(ot=d!==1,ot&&(n.object.zoom=Math.max(n.minZoom,Math.min(n.maxZoom,n.object.zoom/d)),n.object.updateProjectionMatrix()));return d=1,b=!1,ot||se.distanceToSquared(n.object.position)>c||8*(1-re.dot(n.object.quaternion))>c?(n.dispatchEvent(s),se.copy(n.object.position),re.copy(n.object.quaternion),ot=!1,!0):!1}})(),this.connect=F=>{n.domElement=F,n.domElement.style.touchAction="none",n.domElement.addEventListener("contextmenu",Te),n.domElement.addEventListener("pointerdown",J),n.domElement.addEventListener("pointercancel",ee),n.domElement.addEventListener("wheel",_e)},this.dispose=()=>{var F,ce,I,ae,se,re;n.domElement&&(n.domElement.style.touchAction="auto"),(F=n.domElement)==null||F.removeEventListener("contextmenu",Te),(ce=n.domElement)==null||ce.removeEventListener("pointerdown",J),(I=n.domElement)==null||I.removeEventListener("pointercancel",ee),(ae=n.domElement)==null||ae.removeEventListener("wheel",_e),(se=n.domElement)==null||se.ownerDocument.removeEventListener("pointermove",le),(re=n.domElement)==null||re.ownerDocument.removeEventListener("pointerup",ee),n._domElementKeyEvents!==null&&n._domElementKeyEvents.removeEventListener("keydown",Ae)};const n=this,s={type:"change"},r={type:"start"},a={type:"end"},o={NONE:-1,ROTATE:0,DOLLY:1,PAN:2,TOUCH_ROTATE:3,TOUCH_PAN:4,TOUCH_DOLLY_PAN:5,TOUCH_DOLLY_ROTATE:6};let l=o.NONE;const c=1e-6,u=new Ed,h=new Ed;let d=1;const f=new k,g=new qe,v=new qe,m=new qe,p=new qe,S=new qe,y=new qe,w=new qe,O=new qe,A=new qe,P=new k,N=new qe;let b=!1;const x=[],R={};function j(){return 2*Math.PI/60/60*n.autoRotateSpeed}function z(){return Math.pow(.95,n.zoomSpeed)}function K(F){n.reverseOrbit||n.reverseHorizontalOrbit?h.theta+=F:h.theta-=F}function X(F){n.reverseOrbit||n.reverseVerticalOrbit?h.phi+=F:h.phi-=F}const Q=(()=>{const F=new k;return function(I,ae){F.setFromMatrixColumn(ae,0),F.multiplyScalar(-I),f.add(F)}})(),Y=(()=>{const F=new k;return function(I,ae){n.screenSpacePanning===!0?F.setFromMatrixColumn(ae,1):(F.setFromMatrixColumn(ae,0),F.crossVectors(n.object.up,F)),F.multiplyScalar(I),f.add(F)}})(),ne=(()=>{const F=new k;return function(I,ae){const se=n.domElement;if(se&&n.object instanceof Sn&&n.object.isPerspectiveCamera){const re=n.object.position;F.copy(re).sub(n.target);let ve=F.length();ve*=Math.tan(n.object.fov/2*Math.PI/180),Q(2*I*ve/se.clientHeight,n.object.matrix),Y(2*ae*ve/se.clientHeight,n.object.matrix)}else se&&n.object instanceof Ur&&n.object.isOrthographicCamera?(Q(I*(n.object.right-n.object.left)/n.object.zoom/se.clientWidth,n.object.matrix),Y(ae*(n.object.top-n.object.bottom)/n.object.zoom/se.clientHeight,n.object.matrix)):(console.warn("WARNING: OrbitControls.js encountered an unknown camera type - pan disabled."),n.enablePan=!1)}})();function ge(F){n.object instanceof Sn&&n.object.isPerspectiveCamera||n.object instanceof Ur&&n.object.isOrthographicCamera?d=F:(console.warn("WARNING: OrbitControls.js encountered an unknown camera type - dolly/zoom disabled."),n.enableZoom=!1)}function de(F){ge(d/F)}function xe(F){ge(d*F)}function we(F){if(!n.zoomToCursor||!n.domElement)return;b=!0;const ce=n.domElement.getBoundingClientRect(),I=F.clientX-ce.left,ae=F.clientY-ce.top,se=ce.width,re=ce.height;N.x=I/se*2-1,N.y=-(ae/re)*2+1,P.set(N.x,N.y,1).unproject(n.object).sub(n.object.position).normalize()}function ye(F){return Math.max(n.minDistance,Math.min(n.maxDistance,F))}function ie(F){g.set(F.clientX,F.clientY)}function ue(F){we(F),w.set(F.clientX,F.clientY)}function Me(F){p.set(F.clientX,F.clientY)}function fe(F){v.set(F.clientX,F.clientY),m.subVectors(v,g).multiplyScalar(n.rotateSpeed);const ce=n.domElement;ce&&(K(2*Math.PI*m.x/ce.clientHeight),X(2*Math.PI*m.y/ce.clientHeight)),g.copy(v),n.update()}function ze(F){O.set(F.clientX,F.clientY),A.subVectors(O,w),A.y>0?de(z()):A.y<0&&xe(z()),w.copy(O),n.update()}function Ge(F){S.set(F.clientX,F.clientY),y.subVectors(S,p).multiplyScalar(n.panSpeed),ne(y.x,y.y),p.copy(S),n.update()}function Fe(F){we(F),F.deltaY<0?xe(z()):F.deltaY>0&&de(z()),n.update()}function ft(F){let ce=!1;switch(F.code){case n.keys.UP:ne(0,n.keyPanSpeed),ce=!0;break;case n.keys.BOTTOM:ne(0,-n.keyPanSpeed),ce=!0;break;case n.keys.LEFT:ne(n.keyPanSpeed,0),ce=!0;break;case n.keys.RIGHT:ne(-n.keyPanSpeed,0),ce=!0;break}ce&&(F.preventDefault(),n.update())}function U(){if(x.length==1)g.set(x[0].pageX,x[0].pageY);else{const F=.5*(x[0].pageX+x[1].pageX),ce=.5*(x[0].pageY+x[1].pageY);g.set(F,ce)}}function ht(){if(x.length==1)p.set(x[0].pageX,x[0].pageY);else{const F=.5*(x[0].pageX+x[1].pageX),ce=.5*(x[0].pageY+x[1].pageY);p.set(F,ce)}}function it(){const F=x[0].pageX-x[1].pageX,ce=x[0].pageY-x[1].pageY,I=Math.sqrt(F*F+ce*ce);w.set(0,I)}function lt(){n.enableZoom&&it(),n.enablePan&&ht()}function Oe(){n.enableZoom&&it(),n.enableRotate&&U()}function bt(F){if(x.length==1)v.set(F.pageX,F.pageY);else{const I=He(F),ae=.5*(F.pageX+I.x),se=.5*(F.pageY+I.y);v.set(ae,se)}m.subVectors(v,g).multiplyScalar(n.rotateSpeed);const ce=n.domElement;ce&&(K(2*Math.PI*m.x/ce.clientHeight),X(2*Math.PI*m.y/ce.clientHeight)),g.copy(v)}function Ye(F){if(x.length==1)S.set(F.pageX,F.pageY);else{const ce=He(F),I=.5*(F.pageX+ce.x),ae=.5*(F.pageY+ce.y);S.set(I,ae)}y.subVectors(S,p).multiplyScalar(n.panSpeed),ne(y.x,y.y),p.copy(S)}function Xe(F){const ce=He(F),I=F.pageX-ce.x,ae=F.pageY-ce.y,se=Math.sqrt(I*I+ae*ae);O.set(0,se),A.set(0,Math.pow(O.y/w.y,n.zoomSpeed)),de(A.y),w.copy(O)}function D(F){n.enableZoom&&Xe(F),n.enablePan&&Ye(F)}function E(F){n.enableZoom&&Xe(F),n.enableRotate&&bt(F)}function J(F){var ce,I;n.enabled!==!1&&(x.length===0&&((ce=n.domElement)==null||ce.ownerDocument.addEventListener("pointermove",le),(I=n.domElement)==null||I.ownerDocument.addEventListener("pointerup",ee)),Ze(F),F.pointerType==="touch"?Ke(F):W(F))}function le(F){n.enabled!==!1&&(F.pointerType==="touch"?me(F):Ee(F))}function ee(F){var ce,I,ae;ke(F),x.length===0&&((ce=n.domElement)==null||ce.releasePointerCapture(F.pointerId),(I=n.domElement)==null||I.ownerDocument.removeEventListener("pointermove",le),(ae=n.domElement)==null||ae.ownerDocument.removeEventListener("pointerup",ee)),n.dispatchEvent(a),l=o.NONE}function W(F){let ce;switch(F.button){case 0:ce=n.mouseButtons.LEFT;break;case 1:ce=n.mouseButtons.MIDDLE;break;case 2:ce=n.mouseButtons.RIGHT;break;default:ce=-1}switch(ce){case Qs.DOLLY:if(n.enableZoom===!1)return;ue(F),l=o.DOLLY;break;case Qs.ROTATE:if(F.ctrlKey||F.metaKey||F.shiftKey){if(n.enablePan===!1)return;Me(F),l=o.PAN}else{if(n.enableRotate===!1)return;ie(F),l=o.ROTATE}break;case Qs.PAN:if(F.ctrlKey||F.metaKey||F.shiftKey){if(n.enableRotate===!1)return;ie(F),l=o.ROTATE}else{if(n.enablePan===!1)return;Me(F),l=o.PAN}break;default:l=o.NONE}l!==o.NONE&&n.dispatchEvent(r)}function Ee(F){if(n.enabled!==!1)switch(l){case o.ROTATE:if(n.enableRotate===!1)return;fe(F);break;case o.DOLLY:if(n.enableZoom===!1)return;ze(F);break;case o.PAN:if(n.enablePan===!1)return;Ge(F);break}}function _e(F){n.enabled===!1||n.enableZoom===!1||l!==o.NONE&&l!==o.ROTATE||(F.preventDefault(),n.dispatchEvent(r),Fe(F),n.dispatchEvent(a))}function Ae(F){n.enabled===!1||n.enablePan===!1||ft(F)}function Ke(F){switch(be(F),x.length){case 1:switch(n.touches.ONE){case er.ROTATE:if(n.enableRotate===!1)return;U(),l=o.TOUCH_ROTATE;break;case er.PAN:if(n.enablePan===!1)return;ht(),l=o.TOUCH_PAN;break;default:l=o.NONE}break;case 2:switch(n.touches.TWO){case er.DOLLY_PAN:if(n.enableZoom===!1&&n.enablePan===!1)return;lt(),l=o.TOUCH_DOLLY_PAN;break;case er.DOLLY_ROTATE:if(n.enableZoom===!1&&n.enableRotate===!1)return;Oe(),l=o.TOUCH_DOLLY_ROTATE;break;default:l=o.NONE}break;default:l=o.NONE}l!==o.NONE&&n.dispatchEvent(r)}function me(F){switch(be(F),l){case o.TOUCH_ROTATE:if(n.enableRotate===!1)return;bt(F),n.update();break;case o.TOUCH_PAN:if(n.enablePan===!1)return;Ye(F),n.update();break;case o.TOUCH_DOLLY_PAN:if(n.enableZoom===!1&&n.enablePan===!1)return;D(F),n.update();break;case o.TOUCH_DOLLY_ROTATE:if(n.enableZoom===!1&&n.enableRotate===!1)return;E(F),n.update();break;default:l=o.NONE}}function Te(F){n.enabled!==!1&&F.preventDefault()}function Ze(F){x.push(F)}function ke(F){delete R[F.pointerId];for(let ce=0;ce<x.length;ce++)if(x[ce].pointerId==F.pointerId){x.splice(ce,1);return}}function be(F){let ce=R[F.pointerId];ce===void 0&&(ce=new qe,R[F.pointerId]=ce),ce.set(F.pageX,F.pageY)}function He(F){const ce=F.pointerId===x[0].pointerId?x[1]:x[0];return R[ce.pointerId]}this.dollyIn=(F=z())=>{xe(F),n.update()},this.dollyOut=(F=z())=>{de(F),n.update()},this.getScale=()=>d,this.setScale=F=>{ge(F),n.update()},this.getZoomScale=()=>z(),t!==void 0&&this.connect(t),this.update()}}class tM{constructor(){G(this,"handlers",new Map);G(this,"onceHandlers",new Map);G(this,"messageBuffer",new Map)}register(e,t){if(!this.handlers.has(e)){this.handlers.set(e,new Set);const n=this.messageBuffer.get(e);n&&(n.forEach(s=>Promise.resolve(t(s))),this.messageBuffer.delete(e))}return this.handlers.get(e).add(t),()=>this.unregister(e,t)}once(e,t){return this.onceHandlers.has(e)||this.onceHandlers.set(e,new Set),this.onceHandlers.get(e).add(t),()=>this.unregisterOnce(e,t)}unregister(e,t){var n;(n=this.handlers.get(e))==null||n.delete(t)}unregisterOnce(e,t){var n;(n=this.onceHandlers.get(e))==null||n.delete(t)}buffer(e){const{type:t}=e;this.messageBuffer.has(t)||this.messageBuffer.set(t,[]),this.messageBuffer.get(t).push(e)}async dispatch(e){const{type:t,...n}=e,s=this.handlers.get(t);if(s&&s.size>0){await Promise.all(Array.from(s).map(a=>Promise.resolve(a(n))));return}const r=this.onceHandlers.get(t);if(r&&r.size>0){await Promise.all(Array.from(r).map(a=>Promise.resolve(a(n)))),this.onceHandlers.delete(t);return}this.buffer(e)}clear(){this.handlers.clear(),this.onceHandlers.clear(),this.messageBuffer.clear()}getBuffered(e){return this.messageBuffer.get(e)??[]}hasHandlers(e){var t;return(((t=this.handlers.get(e))==null?void 0:t.size)??0)>0}}class nM{constructor(e,t){G(this,"ws",null);G(this,"url");G(this,"router");G(this,"reconnectDelay",1e3);G(this,"maxReconnectDelay",3e4);G(this,"reconnectAttempts",0);G(this,"shouldReconnect",!0);G(this,"state","disconnected");G(this,"stateListeners",new Set);G(this,"messageQueue",[]);this.url=e,this.router=t}get connectionState(){return this.state}onStateChange(e){return this.stateListeners.add(e),e(this.state),()=>this.stateListeners.delete(e)}setState(e){this.state!==e&&(this.state=e,this.stateListeners.forEach(t=>t(e)))}connect(){var n;if(((n=this.ws)==null?void 0:n.readyState)===WebSocket.OPEN||this.state==="connecting")return;this.setState("connecting");const t=`${window.location.protocol==="https:"?"wss:":"ws:"}//${window.location.host}${this.url}`;this.ws=new WebSocket(t),this.ws.binaryType="arraybuffer",this.ws.onopen=()=>{console.log("[WS] Connected"),this.reconnectAttempts=0,this.reconnectDelay=1e3,this.setState("connected"),this.flushQueue()},this.ws.onmessage=async s=>{try{const r=JSON.parse(s.data);await this.router.dispatch(r)}catch(r){console.error("[WS] Failed to parse message:",r)}},this.ws.onclose=()=>{console.log("[WS] Disconnected"),this.setState("disconnected"),this.shouldReconnect&&this.scheduleReconnect()},this.ws.onerror=s=>{console.error("[WS] Error:",s)}}scheduleReconnect(){if(this.state==="reconnecting")return;this.setState("reconnecting");const e=Math.min(this.reconnectDelay*Math.pow(1.5,this.reconnectAttempts),this.maxReconnectDelay);this.reconnectAttempts++,console.log(`[WS] Reconnecting in ${e}ms (attempt ${this.reconnectAttempts})`),setTimeout(()=>this.connect(),e)}send(e){var t;((t=this.ws)==null?void 0:t.readyState)===WebSocket.OPEN?this.ws.send(JSON.stringify(e)):this.messageQueue.push(e)}flushQueue(){var e;for(;this.messageQueue.length>0&&((e=this.ws)==null?void 0:e.readyState)===WebSocket.OPEN;){const t=this.messageQueue.shift();this.ws.send(JSON.stringify(t))}}disconnect(){var e;this.shouldReconnect=!1,(e=this.ws)==null||e.close(),this.ws=null,this.setState("disconnected")}async waitForConnection(e=1e4){return this.state==="connected"?!0:new Promise(t=>{const n=setTimeout(()=>{s(),t(!1)},e),s=this.onStateChange(r=>{r==="connected"&&(clearTimeout(n),s(),t(!0))})})}get isConnected(){var e;return((e=this.ws)==null?void 0:e.readyState)===WebSocket.OPEN}}const Zt=new tM,Vr=new nM("/ws",Zt);let sp=null;function iM(i){sp=i}function Gr(){return sp}class sM{constructor(){G(this,"components",new Map);G(this,"initialized",!1)}register(e){const t=e.name||e.constructor.name;this.components.has(t)&&console.warn(`[ComponentRegistry] Component "${t}" already registered, replacing`),this.components.set(t,e),this.initialized&&e.init().catch(console.error)}unregister(e){const t=this.components.get(e);t&&(t.destroy().catch(console.error),this.components.delete(e))}async initAll(){this.initialized=!0;for(const[e,t]of this.components)try{await t.init(),console.log(`[ComponentRegistry] Initialized: ${e}`)}catch(n){console.error(`[ComponentRegistry] Failed to initialize ${e}:`,n)}}async destroyAll(){for(const[e,t]of this.components)try{await t.destroy(),console.log(`[ComponentRegistry] Destroyed: ${e}`)}catch(n){console.error(`[ComponentRegistry] Failed to destroy ${e}:`,n)}this.components.clear(),this.initialized=!1}get(e){return this.components.get(e)}list(){return Array.from(this.components.keys())}}const Wi=new sM;typeof window<"u"&&(document.addEventListener("DOMContentLoaded",()=>{Wi.initAll().catch(console.error)}),window.addEventListener("beforeunload",()=>{Wi.destroyAll().catch(console.error)}));const bn={gradient:"#58a6ff",pepita:"#d4a843",random_projections:"#f78166",local_goodness:"#a371f7",thermodynamic_contrast:"#3fb950",contrastive:"#ff7b72",hebbian:"#79c0ff",predictive:"#d2a8ff"},te={bg:"#0a0e14",bg_tertiary:"#1a2330",border:"#2a3a4a",border_bright:"#3a4a5a",text_primary:"#e8ecf0",text_secondary:"#8b98a8",text_muted:"#5a6a7a",gradient:"#58a6ff",measured:"#d4a843",legal_unmeasured:"#58a6ff",void:"#f85149",pareto:"#e8ecf0",chance_line:"#f85149",gpu:"#58a6ff",cpu:"#3fb950",memory:"#d29922",ok:"#3fb950",warn:"#d29922",error:"#f85149",passed:"#3fb950",insufficient:"#d29922",rejected:"#f85149",promoted:"#a371f7",ramp_low:"#1f3a5f",ramp_mid:"#58a6ff",ramp_high:"#d4a843"};class rM{constructor(){G(this,"metricsByRun",new Map);G(this,"selectedRunId",null);G(this,"chosenByReader",!1);G(this,"listeners",[])}observe(e,t){this.metricsByRun.set(e,t),this.chosenByReader||(this.selectedRunId=this.newestRunId()),this.notify()}select(e){this.chosenByReader=!0,this.selectedRunId=e,this.notify()}get selectedId(){return this.selectedRunId}get selected(){return this.selectedRunId?this.metricsByRun.get(this.selectedRunId)??null:null}get runs(){return Array.from(this.metricsByRun.entries())}onChange(e){this.listeners.push(e)}notify(){this.listeners.forEach(e=>e(this.selectedRunId,this.selected))}newestRunId(){let e=null,t=-1/0;if(this.metricsByRun.forEach((s,r)=>{var l;const a=(l=s.run)==null?void 0:l.started_at,o=a?Date.parse(a):Number.NaN;Number.isNaN(o)||o>=t&&(t=o,e=r)}),e)return e;const n=this.metricsByRun.keys().next();return n.done?null:n.value}}const qn=new rM,aM={substrate:{display_name:"Substrate",description:"Physical or computational substrate",primitives:[{name:"digital",summary:"Digital substrate: exact arithmetic, full precision",available:!0},{name:"analog",summary:"Analog substrate: continuous-valued physical state",available:!0},{name:"memristive",summary:"Memristive substrate: conductance, IR-drop, noise",available:!0},{name:"neuromorphic",summary:"Neuromorphic substrate: asynchronous spike events",available:!0},{name:"optical",summary:"Photonic substrate: phase/amplitude modulation",available:!0},{name:"quantum",summary:"Quantum substrate: unitary gate simulation",available:!0},{name:"complex",summary:"Complex-valued substrate",available:!0},{name:"sparse",summary:"Sparse substrate: sparsity-masked state",available:!0},{name:"ternary",summary:"Ternary substrate: weights in {-alpha, 0, +alpha}",available:!0}]},geometry:{display_name:"Geometry",description:"Network architecture and connectivity",primitives:[{name:"feedforward",summary:"Feedforward DAG (MLP/CNN)",available:!0},{name:"recurrent",summary:"Recurrent attractor (Hopfield/EqProp)",available:!0},{name:"causal_transformer",summary:"Causal transformer with KV cache",available:!0},{name:"tile",summary:"TileNet modular tile mesh",available:!0},{name:"tile_mesh",summary:"TileNet mesh topology",available:!0},{name:"conv",summary:"Convolutional geometry",available:!0},{name:"graph",summary:"Arbitrary node-edge fabric (FabricPC)",available:!0},{name:"attention",summary:"Attention geometry",available:!0},{name:"spatial_lattice",summary:"3-D spatial lattice (neural_cube)",available:!0},{name:"nca",summary:"Neural cellular automaton fabric",available:!0},{name:"ntm",summary:"Neural Turing Machine tape",available:!0}]},dynamics:{display_name:"Dynamics",description:"State evolution and settling",primitives:[{name:"energy_minimization",summary:"Equilibrium propagation energy minimization",available:!0},{name:"predictive_settling",summary:"Predictive coding settling",available:!0},{name:"error_predictive_coding",summary:"Error predictive coding",available:!0},{name:"spike_integration",summary:"LIF/Izhikevich spike integration",available:!0},{name:"instantaneous",summary:"Instantaneous pass (FF/Backprop)",available:!0},{name:"diffusion",summary:"Continuous-time diffusion settling",available:!0},{name:"lazy",summary:"Lazy/on-demand state dynamics",available:!0},{name:"pc_alm",summary:"Augmented Lagrangian predictive coding",available:!0}]},plasticity:{display_name:"Plasticity",description:"Local learning and adaptation",primitives:[{name:"null",summary:"Null plasticity (5-D slice)",available:!0},{name:"routing",summary:"Routing plasticity: state-dependent gating",available:!0},{name:"fast_weights",summary:"Fast-weight episode-local memory",available:!0},{name:"substrate_coupled",summary:"Physical substrate-coupled plasticity",available:!0},{name:"rule_state",summary:"Rule-state plasticity (Z3)",available:!0},{name:"temporal_psi",summary:"Trace-decayed supervised psi",available:!0},{name:"conflict_adaptive",summary:"Conflict-adaptive psi",available:!0}]},credit:{display_name:"Credit Assignment",description:"How learning signals reach parameters",primitives:[{name:"thermodynamic_contrast",summary:"EqProp free/nudged contrast (Scellier-Bengio)",available:!0},{name:"random_projections",summary:"Fixed random feedback (FA/DFA)",available:!0},{name:"local_goodness",summary:"Forward-Forward / PEPITA goodness",available:!0},{name:"local_contrastive",summary:"Local contrastive credit",available:!0},{name:"temporal_trace",summary:"Hebbian/STDP temporal trace",available:!0},{name:"target_inversion",summary:"Target propagation inversion",available:!0},{name:"homeostatic",summary:"Autonomous Lipschitz scaling",available:!0},{name:"pepita",summary:"PEPITA input-modulation credit",available:!0},{name:"gradient",summary:"Backprop gradient credit (ruler reference)",available:!0},{name:"pc_alm",summary:"PC-ALM primal-dual credit",available:!0}]},update:{display_name:"Update Rule",description:"How parameters are updated",primitives:[{name:"euclidean",summary:"SGD/Adam Euclidean update",available:!0},{name:"adam",summary:"Adam adaptive moment",available:!0},{name:"local_adam",summary:"Local Adam",available:!0},{name:"ortho_adam",summary:"Orthogonal Adam",available:!0},{name:"riemannian_orthogonal",summary:"Riemannian orthogonal update (Muon-family)",available:!0},{name:"muon",summary:"Muon update",available:!0},{name:"lion",summary:"Lion optimizer",available:!0},{name:"spectral_constrained",summary:"Spectral-norm constrained update",available:!0},{name:"mean_norm",summary:"Mean-norm update",available:!0},{name:"elastic_consolidation",summary:"EWC elastic consolidation",available:!0},{name:"natural_gradient",summary:"Natural gradient (Fisher)",available:!0},{name:"role_split",summary:"Role-split update",available:!0}]}},oM={axes:aM},rp=.72,ap=.86;function Ru(i,e,t,n,s){const{camera:r,controls:a}=i,o=(s==null?void 0:s.clone())??r.position.clone().sub(a.target);o.lengthSq()===0&&o.set(.4,.5,.8),o.normalize();const l=o.clone().negate(),c=new k().crossVectors(l,new k(0,1,0)).normalize(),u=new k().crossVectors(c,l).normalize(),h=Math.tan((r.fov??60)*Math.PI/360),d=h*(r.aspect||1),f=h*ap,g=d*rp;let v=0;[e.x,t.x].forEach(m=>{[e.y,t.y].forEach(p=>{[e.z,t.z].forEach(S=>{const y=new k(m,p,S),w=Math.max(Math.abs(y.dot(c))/g,Math.abs(y.dot(u))/f)+y.dot(o);v=Math.max(v,w)})})}),v*=1.06,n.add(c.clone().multiplyScalar(.28*d*v)).add(u.clone().multiplyScalar(-.14*h*v)),a.target.copy(n),r.position.copy(n).add(o.clone().multiplyScalar(v)),a.update()}const Pa=["credit","geometry","dynamics","substrate","plasticity","update"];function Wr(i,e,t){return`${i}|${e}|${t}`}function Ns(i){return i.length===0?0:i.reduce((e,t)=>e+t,0)/i.length}function lM(i){if(i.length<2)return 0;const e=Ns(i),t=i.reduce((n,s)=>n+(s-e)**2,0)/(i.length-1);return Math.sqrt(t)}function cM(i){const e=new Map;for(const t of i)for(const n of t){const s=e.get(n.epoch)??[];s.push(n.val_acc),e.set(n.epoch,s)}return Array.from(e.entries()).sort((t,n)=>t[0]-n[0]).map(([t,n])=>({epoch:t,val_acc:Ns(n)}))}function uM(i,e){const t=new Map;return i.cells.forEach(n=>{t.set(Wr(n.coordinate[e.x],n.coordinate[e.y],n.coordinate[e.z]),n)}),t}function hM(i,e){const t=new Map;return((i==null?void 0:i.records)??[]).forEach((s,r)=>{var u;const a=s==null?void 0:s.coordinate;if(!a)return;const o=Wr(a[e.x],a[e.y],a[e.z]);let l=t.get(o);l||(l={acc:[],walltime:[],params:[],curves:[],pareto:!1,coordinate:{...a},seeds:0},t.set(o,l)),l.seeds+=1;const c=s.payload??{};if(typeof c.val_acc=="number"&&l.acc.push(c.val_acc),typeof c.walltime_s=="number"&&l.walltime.push(c.walltime_s),typeof c.param_count=="number"&&l.params.push(c.param_count),Array.isArray(c.convergence_curve)){const h=c.convergence_curve.filter(d=>typeof(d==null?void 0:d.epoch)=="number"&&typeof(d==null?void 0:d.val_acc)=="number").map(d=>({epoch:d.epoch,val_acc:d.val_acc}));h.length>0&&l.curves.push(h)}(u=i==null?void 0:i.pareto)!=null&&u[r]&&(l.pareto=!0)}),t}function Pu(i,e){const t=Array.from(i.values()),n=al(t,e);return t.sort((s,r)=>La(s,e,n).localeCompare(La(r,e,n)))}function al(i,e){return[e.x,e.y,e.z].filter(n=>new Set(i.map(r=>r.coordinate[n])).size>1)}function La(i,e,t){return(t.length>0?t:[e.x,e.y,e.z]).map(s=>i.coordinate[s]??"").join(" · ")}function Ad(i){const e={credit:new Set,geometry:new Set,dynamics:new Set,substrate:new Set,plasticity:new Set,update:new Set};i.forEach(n=>{const s=n==null?void 0:n.coordinate;s&&Pa.forEach(r=>{const a=s[r];typeof a=="string"&&a.length>0&&e[r].add(a)})});const t={};return Pa.forEach(n=>{t[n]=Array.from(e[n]).sort()}),t}class dM{constructor(){G(this,"runId",null);G(this,"metrics",null);G(this,"axes",{x:"credit",y:"geometry",z:"dynamics"});G(this,"space",null);G(this,"spaceCells",new Map);G(this,"aggregates",new Map);G(this,"values",Ad([]));G(this,"chance",.1);G(this,"requiredSeeds",0);G(this,"gate",null);G(this,"spaceRequest","");G(this,"listeners",[]);qn.onChange((e,t)=>{this.absorb(e,t)})}onChange(e){this.listeners.push(e)}notify(e){this.listeners.forEach(t=>t(e))}async absorb(e,t){this.runId=e,this.metrics=t,t&&(typeof t.chance=="number"&&(this.chance=t.chance),typeof t.required_seeds=="number"&&(this.requiredSeeds=t.required_seeds),t.gate&&(this.gate=t.gate,typeof t.gate.required_seeds_per_group=="number"&&(this.requiredSeeds=t.gate.required_seeds_per_group)),this.values=Ad(t.records??[])),this.recomputeEvidence(),await this.syncSpace()}setAxes(e){this.axes=e,this.notify("axes"),this.recomputeEvidence(),this.syncSpace()}recomputeEvidence(){this.aggregates=hM(this.metrics,this.axes),this.notify("evidence")}async syncSpace(){if(!this.runId)return;const e=[this.runId,this.axes.x,this.axes.y,this.axes.z,...Pa.map(n=>this.values[n].join(","))].join("|");if(e===this.spaceRequest)return;const t=await this.fetchSpace();t&&(this.spaceRequest=e,this.space=t,this.spaceCells=uM(t,this.axes),this.notify("space"))}async fetchSpace(){try{const e=await fetch(`/api/cells/${this.runId}/space`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({axes:[this.axes.x,this.axes.y,this.axes.z]})});return e.ok?await e.json():(console.warn("[StageState] The space was refused",e.status),null)}catch(e){return console.warn("[StageState] The space could not be read",e),null}}}const Ue=new dM;function jo(i,e=10){if(i.length<=e)return[i];const t=[];let n="";for(const s of i.split("_")){const r=n?`${n}_${s}`:s;r.length>e&&n?(t.push(n),n=s):n=r}return n&&t.push(n),t}function Mi(i,e,t,n){const s=jo(i),r=document.createElement("canvas"),a=r.getContext("2d"),o=64,l=72;a.font=`bold ${o}px "JetBrains Mono", monospace`;const c=Math.max(...s.map(v=>a.measureText(v).width))+16;r.width=Math.max(64,Math.ceil(c)),r.height=s.length*l+16,a.font=`bold ${o}px "JetBrains Mono", monospace`,a.fillStyle="#ffffff",a.textAlign="center",a.textBaseline="middle",s.forEach((v,m)=>{a.fillText(v,r.width/2,l*m+l/2+8)});const u=new Tu(r);u.needsUpdate=!0;const h=t.clone();h.map=u,h.transparent=!0;const d=new tp(h),f=r.width/r.height;let g=e*s.length;return n!==void 0&&(g=Math.min(g,n/f)),d.scale.set(g*f,g,1),d}function fM(){const e=document.createElement("canvas");e.width=64,e.height=64;const t=e.getContext("2d");t.fillStyle="#ffffff",t.beginPath(),t.arc(64/2,64/2,64/2-2,0,Math.PI*2),t.fill();const n=new Tu(e);return n.needsUpdate=!0,n}function pM(i,e,t=.14){const s=document.createElement("canvas");s.width=128,s.height=128;const r=s.getContext("2d");r.strokeStyle=i,r.lineWidth=128*t,r.beginPath(),r.arc(128/2,128/2,128/2-r.lineWidth,0,Math.PI*2),r.stroke();const a=new Tu(s);a.needsUpdate=!0;const o=new ks({map:a,transparent:!0,depthWrite:!1}),l=new tp(o);return l.scale.set(e*2,e*2,1),l}const Cd=oM.axes,mM={measured:"Measured — the run has evidence here",legal:"Legal — a gap nobody has measured",void:"Void — the system refuses this cell"};class gM{constructor(){G(this,"name","DiscoveryMap");G(this,"scene",new Eu);G(this,"camera",new Sn);G(this,"renderer",null);G(this,"cells",new Map);G(this,"cellDataMap",new Map);G(this,"cellHeights",new Map);G(this,"xValues",[]);G(this,"yValues",[]);G(this,"zValues",[]);G(this,"cellSize",.8);G(this,"spacing",1.1);G(this,"raycaster",new Xy);G(this,"mouse",new qe);G(this,"selectedCell",null);G(this,"hoveredCell",null);G(this,"legendElement",null);G(this,"readoutElement",null);G(this,"pointerX",0);G(this,"pointerY",0);G(this,"axisLabelMeshes",[]);G(this,"voidMesh",null);G(this,"visible",!1);G(this,"onQueueUpdate",e=>{});G(this,"onCampaignMetrics",e=>{const t=e==null?void 0:e.data;if(!(t!=null&&t.run))return;const n=typeof(e==null?void 0:e.campaign_id)=="string"?e.campaign_id:null;n&&qn.observe(n,t)});Zt.register("queue_update",this.onQueueUpdate),Zt.register("campaign_metrics",this.onCampaignMetrics)}async init(){const e=Gr();e&&(this.scene=e.scene,this.camera=e.camera,this.renderer=e.renderer),this.setupInteraction(),this.createLegend(),this.createReadout(),Ue.onChange(()=>this.updateLegend()),qn.onChange(()=>this.updateRunPicker()),console.log("[DiscoveryMap] Initialized")}async destroy(){var e,t;Zt.unregister("queue_update",this.onQueueUpdate),Zt.unregister("campaign_metrics",this.onCampaignMetrics),this.clearGrid(),(e=this.legendElement)==null||e.remove(),(t=this.readoutElement)==null||t.remove()}show(){this.visible=!0,this.applyAxes()}hide(){this.visible=!1,this.clearGrid()}refreshView(e){if(this.visible){if(e==="space"){this.applyAxes();return}e==="evidence"&&this.applyAggregates()}}hasMeasured(){return this.cellDataMap.size>0&&this.cellHeights.size>0}updateLegend(){this.refreshAxisOptions(),this.updateLegendArms(),this.updateLegendAxes()}setupInteraction(){var t;const e=(t=this.renderer)==null?void 0:t.domElement;e&&(this.raycaster.params.Line.threshold=this.cellSize*.2,e.addEventListener("mousemove",n=>{const s=e.getBoundingClientRect();this.mouse.x=(n.clientX-s.left)/s.width*2-1,this.mouse.y=-((n.clientY-s.top)/s.height)*2+1,this.pointerX=n.clientX,this.pointerY=n.clientY}),e.addEventListener("mouseleave",()=>{this.hideReadout()}),e.addEventListener("click",()=>{this.hoveredCell&&this.selectCell(this.hoveredCell)}))}createReadout(){const e=document.getElementById("ui-overlay");e&&(this.readoutElement=document.createElement("div"),this.readoutElement.id="cell-readout",this.readoutElement.style.cssText=`
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
    `,e.appendChild(this.readoutElement))}showReadout(e){const t=this.readoutElement;if(!t)return;const n=document.createElement("div");n.style.color="var(--text-secondary)",n.textContent=Object.entries(e.coordinate).filter(([,l])=>l).map(([l,c])=>`${l}=${c}`).join("  "),t.replaceChildren(n);const s=document.createElement("div");if(s.style.marginTop="4px",s.style.fontWeight="600",s.style.color=e.status==="void"?te.void:e.status==="measured"?te.measured:te.legal_unmeasured,s.textContent=mM[e.status],t.appendChild(s),e.voidReason){const l=document.createElement("div");l.style.marginTop="4px",l.style.color="var(--text-secondary)",l.textContent=e.voidReason,t.appendChild(l)}t.style.display="block";const r=t.getBoundingClientRect(),a=Math.min(this.pointerX+16,window.innerWidth-r.width-8),o=Math.min(this.pointerY+16,window.innerHeight-r.height-8);t.style.left=`${Math.max(8,a)}px`,t.style.top=`${Math.max(8,o)}px`}hideReadout(){this.readoutElement&&(this.readoutElement.style.display="none")}createLegend(){const e=document.getElementById("ui-overlay");e&&(this.legendElement=document.createElement("div"),this.legendElement.id="discovery-legend",this.legendElement.style.cssText=`
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
      <div id="legend-title" style="font-weight: 600; margin-bottom: 12px; color: var(--text-primary);">Discovery Map</div>
      <div id="legend-view"></div>
      <div id="legend-marks" style="display: flex; flex-direction: column; gap: 8px;">
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
    `,e.appendChild(this.legendElement),this.createRunPicker(),this.createAxisPicker(),this.updateLegendArms(),this.updateLegendAxes())}createRunPicker(){var t;const e=(t=this.legendElement)==null?void 0:t.querySelector("#legend-run-picker");e&&e.addEventListener("change",()=>{qn.select(e.value||null)})}updateRunPicker(){var a,o,l;const e=(a=this.legendElement)==null?void 0:a.querySelector("#legend-run-picker"),t=(o=this.legendElement)==null?void 0:o.querySelector("#legend-run");if(!e)return;const n=qn.runs;if(e.innerHTML="",n.forEach(([c,u])=>{var g,v;const h=document.createElement("option"),d=((g=u==null?void 0:u.run)==null?void 0:g.profile)??"run",f=((v=u==null?void 0:u.records)==null?void 0:v.length)??0;h.value=c,h.textContent=`${c.slice(0,8)} · ${d} · ${f}`,h.selected=c===qn.selectedId,e.appendChild(h)}),n.length===0){e.disabled=!0,t&&(t.textContent="No run has reported yet.");return}e.disabled=!1;const s=qn.selected;if(!t)return;if(!s){t.textContent="";return}const r=s.run??{};t.textContent=[`run ${(qn.selectedId??"").slice(0,8)}`,r.mode,`${((l=s.records)==null?void 0:l.length)??0} records`].filter(Boolean).join(" · ")}createAxisPicker(){var n;const e=(n=this.legendElement)==null?void 0:n.querySelector("#legend-axis-picker");if(!e)return;["x","y","z"].forEach(s=>{const r=document.createElement("div");r.style.cssText="display: flex; align-items: center; gap: 6px; font-size: 11px;";const a=document.createElement("span");a.textContent=s.toUpperCase(),a.style.cssText="color: var(--text-secondary); width: 12px;";const o=document.createElement("select");o.dataset.dimension=s,o.style.cssText=`
        flex: 1;
        background: var(--bg-tertiary);
        color: var(--text-primary);
        border: 1px solid var(--border);
        border-radius: 4px;
        font-size: 11px;
        padding: 2px 4px;
      `,o.addEventListener("change",()=>{Ue.setAxes({...Ue.axes,[s]:o.value})}),r.appendChild(a),r.appendChild(o),e.appendChild(r)}),this.refreshAxisOptions()}refreshAxisOptions(){var t;const e=(t=this.legendElement)==null?void 0:t.querySelectorAll("#legend-axis-picker select");e&&e.forEach(n=>{const s=n.dataset.dimension,r=new Set(["x","y","z"].filter(a=>a!==s).map(a=>Ue.axes[a]));n.innerHTML="",Pa.forEach(a=>{var l;const o=document.createElement("option");o.value=a,o.textContent=((l=Cd[a])==null?void 0:l.display_name)??a,o.disabled=r.has(a),o.selected=Ue.axes[s]===a,n.appendChild(o)})})}updateLegendArms(){var n;const e=(n=this.legendElement)==null?void 0:n.querySelector("#legend-arms");if(!e)return;const t=Ue.values.credit;if(t.length===0){e.innerHTML='<span style="color: var(--text-muted); font-size: 11px;">No arm measured yet.</span>';return}e.innerHTML=t.map(s=>{const r=bn[s]||te.gradient;return`<span style="display: inline-flex; align-items: center; gap: 4px; padding: 2px 8px; background: ${r}22; border: 1px solid ${r}88; border-radius: 12px; color: ${r}; font-size: 11px;">${s}</span>`}).join("")}updateLegendAxes(){var l;const e=(l=this.legendElement)==null?void 0:l.querySelector("#legend-axes");if(!e)return;const t=Ue.space;if(!t){e.textContent="Waiting for the run's declared space — the axes come from the ontology.";return}const n=(c,u)=>{var g;const h=t.available[c]??u.length,d=h>u.length?` (${u.length} of ${h})`:"";return`${((g=Cd[c])==null?void 0:g.display_name)??c}${d}`},s=Object.entries(t.held).map(([c,u])=>`${c}=${u}`),r={measured:Array.from(Ue.aggregates.keys()).filter(c=>Ue.spaceCells.has(c)).length,legal:t.counts.legal,void:t.counts.void},a=t.cells.length,o=Object.entries(t.void_rules??{}).sort((c,u)=>u[1]-c[1]).slice(0,2).map(([c,u])=>`${c.replace(/_/g," ")} (${u})`);e.innerHTML=[`<div>X: ${n(Ue.axes.x,t.values[Ue.axes.x]??[])}</div>`,`<div>Y: ${n(Ue.axes.y,t.values[Ue.axes.y]??[])}</div>`,`<div>Z: ${n(Ue.axes.z,t.values[Ue.axes.z]??[])}</div>`,`<div style="margin-top: 6px;">held: ${s.join(" · ")||"—"}</div>`,`<div style="margin-top: 6px;">${r.measured} measured · ${r.legal} legal · ${r.void} void (of ${a})</div>`,o.length>0?`<div style="margin-top: 6px;">refused by: ${o.join(", ")}</div>`:""].join("")}applyAxes(){const e=Ue.space,t=Ue.axes;this.xValues=(e==null?void 0:e.values[t.x])??[],this.yValues=(e==null?void 0:e.values[t.y])??[],this.zValues=(e==null?void 0:e.values[t.z])??[],this.buildGrid(),this.updateLegend()}buildGrid(){if(this.clearGrid(),!this.visible)return;this.createAxisLabels();const e=[];this.yValues.forEach((t,n)=>{this.zValues.forEach((s,r)=>{this.xValues.forEach((a,o)=>{const l=Wr(a,t,s),c=Ue.spaceCells.get(l),u=(c==null?void 0:c.status)??"legal",h={coordinate:this.coordinateFor(a,t,s),status:u,chance:Ue.chance,requiredSeeds:Ue.requiredSeeds,runId:Ue.runId??void 0,voidReason:c==null?void 0:c.reason,inDeclaration:c==null?void 0:c.in_declaration};if(this.cellDataMap.set(l,h),u==="void"){e.push(...this.voidMarkerPositions(o,n,r));return}this.createCell(l,h,o,n,r)})})}),e.length>0&&this.createVoidMarkers(e),this.frameGrid()}coordinateFor(e,t,n){const s={credit:"",geometry:"",dynamics:"",substrate:"",plasticity:"",update:""};return s[Ue.axes.x]=e,s[Ue.axes.y]=t,s[Ue.axes.z]=n,Pa.forEach(r=>{var o,l;if(s[r])return;const a=(l=(o=Ue.space)==null?void 0:o.held)==null?void 0:l[r];a&&(s[r]=a)}),s}createAxisLabels(){this.axisLabelMeshes.forEach(u=>this.scene.remove(u)),this.axisLabelMeshes=[];const e=new ks({color:9148584,sizeAttenuation:!0}),t=new ks({color:13227232,sizeAttenuation:!0}),n=(this.xValues.length-1)*this.spacing,r=(this.zValues.length-1)*this.spacing/2+1.2,a=-.45;this.xValues.forEach((u,h)=>{const d=(h-(this.xValues.length-1)/2)*this.spacing,f=Mi(u,.3,e,this.spacing*.95);f.position.set(d,a,r),this.scene.add(f),this.axisLabelMeshes.push(f)});const o=Mi(Ue.axes.x,.3,t);o.position.set(n/2+1.15,a,r),this.scene.add(o),this.axisLabelMeshes.push(o);const l=Mi(Ue.axes.z,.3,t);l.position.set(0,a,r+1.1),this.scene.add(l),this.axisLabelMeshes.push(l);const c=Mi(Ue.axes.y,.3,t);c.position.set(-(n/2)-1.5,1.3,0),this.scene.add(c),this.axisLabelMeshes.push(c)}createCell(e,t,n,s,r){const a=(n-(this.xValues.length-1)/2)*this.spacing,o=s*this.spacing,l=(r-(this.zValues.length-1)/2)*this.spacing,c=t.status==="measured"?this.createMeasuredCell(t):this.createLegalCell();c.position.set(a,o,l),c.userData={...c.userData,cellKey:e},this.scene.add(c),this.cells.set(e,c)}createMeasuredCell(e){const t=this.pillarHeight(e),n=bn[e.coordinate.credit]||te.gradient,s=new Bi(this.cellSize,t,this.cellSize);s.translate(0,t/2,0);const r=new Oo({color:new nt(n),emissive:new nt(n),emissiveIntensity:.5,transparent:!0,opacity:.9,metalness:.3,roughness:.4}),a=new gn(s,r);a.castShadow=!0,a.receiveShadow=!0;const o=new Bi(this.cellSize*1.1,t*1.1,this.cellSize*1.1);o.translate(0,t/2,0);const l=new Ir({color:new nt(n),transparent:!0,opacity:.15,depthWrite:!1}),c=new gn(o,l);return a.add(c),a.userData.glow=c,a}createLegalCell(){const e=new Bi(this.cellSize,this.cellSize,this.cellSize),t=new zy(e);t.translate(0,this.cellSize/2,0);const n=new ki({color:te.legal_unmeasured,transparent:!0,opacity:.55}),s=new Nr(t,n),r=new gn(new Bi(this.cellSize,this.cellSize,this.cellSize),new Ir);return r.position.y=this.cellSize/2,r.visible=!1,s.add(r),s}disposeMesh(e){e.traverse(t=>{const n=t.geometry;n&&n.dispose();const s=t.material;Array.isArray(s)?s.forEach(r=>r.dispose()):s&&s.dispose()})}voidMarkerPositions(e,t,n){const s=(e-(this.xValues.length-1)/2)*this.spacing,r=t*this.spacing,a=(n-(this.zValues.length-1)/2)*this.spacing,o=this.cellSize*.6,l=.1;return[s-o,r+l,a-o,s+o,r+l,a+o,s+o,r+l,a-o,s-o,r+l,a+o]}createVoidMarkers(e){const t=new Xt;t.setAttribute("position",new qt(e,3));const n=new ki({color:te.void,transparent:!0,opacity:.32});this.voidMesh=new Nr(t,n),this.scene.add(this.voidMesh)}frameGrid(){const e=Gr();if(!(e!=null&&e.controls)||this.xValues.length===0||this.zValues.length===0)return;const t=(this.xValues.length-1)*this.spacing/2+this.cellSize,n=(this.zValues.length-1)*this.spacing/2+this.cellSize,s=(this.yValues.length-1)*this.spacing+this.cellSize,r=n+1.8,a=-.8;Ru(e,new k(-t,a,-n),new k(t,s,r),new k(0,s/2,0))}clearGrid(){this.cells.forEach(e=>{this.scene.remove(e),this.disposeMesh(e)}),this.cells.clear(),this.cellDataMap.clear(),this.cellHeights.clear(),this.axisLabelMeshes.forEach(e=>{this.scene.remove(e),this.disposeMesh(e)}),this.axisLabelMeshes=[],this.voidMesh&&(this.scene.remove(this.voidMesh),this.voidMesh.geometry.dispose(),Array.isArray(this.voidMesh.material)?this.voidMesh.material.forEach(e=>e.dispose()):this.voidMesh.material.dispose(),this.voidMesh=null)}applyAggregates(){this.visible&&(Ue.aggregates.forEach((e,t)=>{const n=this.cellDataMap.get(t);n&&(n.status="measured",n.coordinate={...e.coordinate},n.metrics={val_acc:Ns(e.acc),val_acc_std:lM(e.acc),walltime_s:Ns(e.walltime),param_count:Ns(e.params),n_seeds:e.acc.length},n.curve=cM(e.curves),n.pareto=e.pareto,n.chance=Ue.chance,n.requiredSeeds=Ue.requiredSeeds,n.runId=Ue.runId??void 0,this.updateCellVisual(t,n,e.pareto))}),this.updateLegendAxes())}pillarHeight(e){var t;return Zc.lerp(.4,3.4,((t=e.metrics)==null?void 0:t.val_acc)??0)}updateCellVisual(e,t,n){const s=this.cells.get(e);if(!s)return;const r=s.position.clone(),a=s.userData.glow;a&&s.remove(a),this.scene.remove(s),this.disposeMesh(s);const o=this.createMeasuredCell(t);o.position.copy(r),o.userData.cellKey=e;const l=this.pillarHeight(t),c=this.cellHeights.get(e)??0;if(this.cellHeights.set(e,l),o.scale.y=l>0?Math.min(1,Math.max(c/l,.001)):1,n){const u=new Au(this.cellSize*.6,this.cellSize*.8,32),h=new Ir({color:te.pareto,side:$n,transparent:!0,opacity:.6}),d=new gn(u,h);d.rotation.x=-Math.PI/2,d.position.y=.05,o.add(d),o.userData.paretoRing=d}this.scene.add(o),this.cells.set(e,o)}selectCell(e){this.selectedCell=e;const t=this.cellDataMap.get(e);t&&window.dispatchEvent(new CustomEvent("cell-selected",{detail:t}))}update(e){if(!this.visible){this.hideReadout();return}const t=1-Math.exp(-e*8);this.cells.forEach((a,o)=>{const l=this.cellDataMap.get(o);if((l==null?void 0:l.status)==="measured"&&a instanceof gn&&a.material instanceof Oo){a.scale.y<1&&(a.scale.y=Math.min(1,a.scale.y+(1-a.scale.y)*t));const c=a.userData.glow;c&&(c.material.opacity=.1+.1*Math.sin(Date.now()*.003));const u=a.userData.paretoRing;u&&(u.material.opacity=.4+.2*Math.sin(Date.now()*.005))}}),this.raycaster.setFromCamera(this.mouse,this.camera);const n=this.raycaster.intersectObjects(Array.from(this.cells.values()),!0);let s=null;n.length>0&&(s=this.pickCell(n)),s||(s=this.voidCellUnderCursor()),s!==this.hoveredCell&&(this.hoveredCell&&this.highlightCell(this.hoveredCell,!1),this.hoveredCell=s,s&&this.highlightCell(s,!0));const r=s?this.cellDataMap.get(s):void 0;r?this.showReadout(r):this.hideReadout()}pickCell(e){var n,s;let t=null;for(const r of e){const a=r.object.userData.cellKey||((n=r.object.parent)==null?void 0:n.userData.cellKey);if(a&&(t??(t=a),((s=this.cellDataMap.get(a))==null?void 0:s.status)==="measured"))return a}return t}voidCellUnderCursor(){if(!this.voidMesh)return null;const e=this.raycaster.params.Line.threshold;this.raycaster.params.Line.threshold=this.cellSize*.3;try{const t=this.raycaster.intersectObject(this.voidMesh,!1);return t.length===0?null:this.cellAt(t[0].point)}finally{this.raycaster.params.Line.threshold=e}}cellAt(e){const t=Math.round(e.x/this.spacing+(this.xValues.length-1)/2),n=Math.round(e.y/this.spacing),s=Math.round(e.z/this.spacing+(this.zValues.length-1)/2);return t<0||t>=this.xValues.length||n<0||n>=this.yValues.length||s<0||s>=this.zValues.length?null:Wr(this.xValues[t],this.yValues[n],this.zValues[s])}highlightCell(e,t){const n=this.cells.get(e);if(n){if(n instanceof gn&&n.material instanceof Oo){t?(n.userData.originalEmissive=n.material.emissiveIntensity,n.material.emissiveIntensity=(n.userData.originalEmissive||.5)+.5):n.userData.originalEmissive!==void 0&&(n.material.emissiveIntensity=n.userData.originalEmissive);return}n instanceof Nr&&n.material instanceof ki&&(t?(n.userData.originalOpacity=n.material.opacity,n.material.opacity=.95):n.userData.originalOpacity!==void 0&&(n.material.opacity=n.userData.originalOpacity))}}}const Us=new gM;Wi.register(Us);class _M{constructor(){G(this,"name","CellDrawer");G(this,"panel",null);G(this,"content",null);G(this,"sparklineScene",null);G(this,"sparklineRenderer",null);G(this,"sparklineCamera",null);G(this,"sparklineAnimationId",null);G(this,"currentData",null);G(this,"onKeyDown",e=>{e.key==="Escape"&&this.currentData&&this.hide()});G(this,"onCellSelected",e=>{this.show(e.detail)})}async init(){this.createPanel(),this.setupEvents(),console.log("[CellDrawer] Initialized")}async destroy(){var e;this.stopSparkline(),(e=this.panel)==null||e.remove(),window.removeEventListener("cell-selected",this.onCellSelected),window.removeEventListener("keydown",this.onKeyDown)}createPanel(){const e=document.getElementById("ui-overlay");e&&(this.panel=document.createElement("div"),this.panel.id="cell-drawer",this.panel.style.cssText=`
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
    `,e.appendChild(this.panel),this.content=this.panel.querySelector("#drawer-content"),this.panel.querySelector("#drawer-close").addEventListener("click",()=>this.hide()))}setupEvents(){window.addEventListener("cell-selected",this.onCellSelected),window.addEventListener("keydown",this.onKeyDown)}shiftPanels(e){const t=e?400:20;["hud","plotter"].forEach(n=>{var s;(s=document.getElementById(n))==null||s.style.setProperty("right",`${t}px`)})}show(e){this.currentData=e,this.renderContent(e),this.panel.style.transform="translateX(0)",this.shiftPanels(!0),this.startSparkline(e)}hide(){this.panel.style.transform="translateX(100%)",this.shiftPanels(!1),this.stopSparkline(),this.currentData=null}renderContent(e){if(!this.content)return;const{coordinate:t,metrics:n,status:s}=e,r=bn[t.credit]||te.gradient,a=(n==null?void 0:n.val_acc)??0,o=(n==null?void 0:n.n_seeds)??0,l=e.chance??.1,c=e.requiredSeeds??0;let u="UNMEASURED",h=te.legal_unmeasured;s==="void"&&(u="VOID",h=te.void),s==="measured"&&(a<=l?(u="REJECTED",h=te.rejected):c>0&&o<c?(u="INSUFFICIENT",h=te.insufficient):a>l+.1?(u="PASSED",h=te.passed):(u="INSUFFICIENT",h=te.insufficient));const d=s==="measured"&&c>0?Math.max(0,c-o):"N/A";this.content.innerHTML=`
      <div style="margin-bottom: 20px;">
        <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px;">
          ${Object.entries(t).filter(([,g])=>g).map(([g,v])=>`
              <span style="
                padding: 4px 10px;
                background: ${g==="credit"?r+"22":"var(--bg-tertiary)"};
                border: 1px solid ${g==="credit"?r+"88":"var(--border)"};
                border-radius: 12px;
                font-size: 11px;
                color: ${g==="credit"?r:"var(--text-primary)"};
              ">
                ${g}=${v}
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
            background: linear-gradient(90deg, ${te.rejected}, ${te.insufficient}, ${te.passed});
            border-radius: 2px;
          "></div>
        </div>
      </div>

      ${s==="measured"?`
        <div style="margin-bottom: 20px;">
          <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 8px;">SEEDS TO CLAIM</div>
          <div style="font-size: 24px; font-weight: 700; font-family: 'JetBrains Mono', monospace; color: ${te.insufficient};">
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
    `;const f=document.createElement("style");f.textContent=`
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
    `,this.content.appendChild(f),this.wireActions(e)}actionStates(e){var a;if(e.status==="void")return{replicate:!1,preregister:!1,quest:!1};const t=e.status==="measured",n=((a=e.metrics)==null?void 0:a.n_seeds)??0,s=e.requiredSeeds??0;return{replicate:(s>0?Math.max(0,s-n):0)>0||!t,preregister:t,quest:!t}}wireActions(e){const t=this.content;if(!t)return;const n=this.actionStates(e);t.querySelectorAll(".drawer-btn[data-action]").forEach(o=>{const l=o.dataset.action??"",c=n[l]===!0;o.disabled=!c,o.addEventListener("click",()=>{this.runAction(l,e)})});const r=t.querySelector('.drawer-btn[data-action="replicate"]');r&&(r.textContent=e.status==="measured"?"Queue Rest":"Queue");const a=t.querySelector("#drawer-action-note");a&&(a.textContent=this.actionNote(e))}actionNote(e){var s;if(!e.runId)return"This cell belongs to no run yet, so there is nothing to queue or register.";if(e.status==="void")return`The system refuses this cell, so nothing can be measured here.${e.voidReason?` ${e.voidReason}.`:""}`;if(e.status==="measured"){const r=((s=e.metrics)==null?void 0:s.n_seeds)??0,a=e.requiredSeeds??0;return`Queue Rest measures the ${Math.max(0,a-r)} seeds this cell still owes. Preregister writes down the protocol a confirming run must meet.`}const t=e.inDeclaration===!1?" It lies outside this run's declaration, so the run did not set out to measure it.":"";return`The system would measure this cell and nobody has. Queue measures it (${e.requiredSeeds??0} seeds). Adopt as Quest writes the question down first and then queues the run that would answer it — a new run, because a threshold written now cannot confirm a run that has already begun.${t}`}setStatus(e,t=!1){var s;const n=(s=this.content)==null?void 0:s.querySelector("#drawer-status");n&&(n.textContent=e,n.style.color=t?te.rejected:te.text_secondary)}async runAction(e,t){var o,l;if(!t.runId){this.setStatus("This cell belongs to no run yet.",!0);return}const n=Array.from(((o=this.content)==null?void 0:o.querySelectorAll(".drawer-btn"))??[]);n.forEach(c=>{c.disabled=!0}),this.setStatus("Working…");const s=(l=this.content)==null?void 0:l.querySelector("#drawer-threshold"),r=s!=null&&s.value?Number(s.value):null,a={coordinate:t.coordinate};r!==null&&Number.isFinite(r)&&(a.threshold=r);try{const c=await fetch(`/api/cells/${t.runId}/${e}`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(a)}),u=await c.json();if(!c.ok){this.setStatus((u==null?void 0:u.error)??"The action failed.",!0);return}this.setStatus(this.actionSummary(e,u))}catch(c){this.setStatus(`The action failed: ${String(c)}`,!0)}finally{n.forEach(c=>{c.disabled=!1})}}actionSummary(e,t){if(e==="replicate")return`Queued campaign ${t.campaign_id}: ${t.measurements} measurements in a plan of ${t.plan}.`;const s=`${t.written?"Registered":"Already registered"} ${t.path} — commit it; the run that follows it can be confirmatory.`;return e!=="quest"?s:t.campaign_id?`${s} Queued campaign ${t.campaign_id}: ${t.measurements} measurements in a plan of ${t.plan}, in a new run.`:`${s} No campaign queue is attached, so nothing is scheduled.`}startSparkline(e){const t=document.getElementById("sparkline-container");if(!t)return;this.stopSparkline();const n=e.curve??[];if(n.length===0){t.innerHTML=`
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
      `;return}this.sparklineScene=new Eu,this.sparklineCamera=new Ur(-1,1,1,-1,.1,10),this.sparklineCamera.position.z=2,this.sparklineRenderer=new Qf({alpha:!0,antialias:!0}),this.sparklineRenderer.setSize(t.clientWidth,t.clientHeight),this.sparklineRenderer.setPixelRatio(Math.min(window.devicePixelRatio,2)),t.appendChild(this.sparklineRenderer.domElement);const s=e.chance??.1,r=n.map(P=>P.val_acc),a=Math.min(s,...r),l=Math.max(...r,s)-a||1,c=P=>Zc.lerp(-.7,.7,(P-a)/l),u=n.map((P,N)=>{const b=Zc.lerp(-.9,.9,N/(n.length-1||1));return new k(b,c(P.val_acc),0)}),h=new Xt().setFromPoints(u),d=new ki({color:bn[e.coordinate.credit]||te.gradient,linewidth:2}),f=new $o(h,d);this.sparklineScene.add(f);const g=new np(new Xt().setFromPoints(u),new wu({color:bn[e.coordinate.credit]||te.gradient,size:6,sizeAttenuation:!1}));this.sparklineScene.add(g);const v=c(s),m=new Xt().setFromPoints([new k(-.9,v,0),new k(.9,v,0)]),p=new ip({color:te.chance_line,dashSize:.05,gapSize:.03,linewidth:1}),S=new $o(m,p);S.computeLineDistances(),this.sparklineScene.add(S);const y=new Xt().setFromPoints([new k(-.9,-.7,0),new k(.9,-.7,0),new k(-.9,-.7,0),new k(-.9,.7,0)]),w=new ki({color:te.border,linewidth:1}),O=new Nr(y,w);this.sparklineScene.add(O);const A=()=>{!this.sparklineRenderer||!this.sparklineScene||!this.sparklineCamera||(this.sparklineRenderer.render(this.sparklineScene,this.sparklineCamera),this.sparklineAnimationId=requestAnimationFrame(A))};A()}stopSparkline(){this.sparklineAnimationId&&(cancelAnimationFrame(this.sparklineAnimationId),this.sparklineAnimationId=null),this.sparklineRenderer&&(this.sparklineRenderer.dispose(),this.sparklineRenderer=null),this.sparklineScene=null,this.sparklineCamera=null}}const op=new _M;Wi.register(op);const vM=!0,rn="u-",xM="uplot",yM=rn+"hz",MM=rn+"vt",SM=rn+"title",bM=rn+"wrap",EM=rn+"under",wM=rn+"over",TM=rn+"axis",Ls=rn+"off",AM=rn+"select",CM=rn+"cursor-x",RM=rn+"cursor-y",PM=rn+"cursor-pt",LM=rn+"legend",DM=rn+"live",IM=rn+"inline",UM=rn+"series",NM=rn+"marker",Rd=rn+"label",FM=rn+"value",Ma="width",Sa="height",_a="top",Pd="bottom",Sr="left",oc="right",Lu="#000",Ld=Lu+"0",lc="mousemove",Dd="mousedown",cc="mouseup",Id="mouseenter",Ud="mouseleave",Nd="dblclick",OM="resize",BM="scroll",Fd="change",Ko="dppxchange",Du="--",Zr=typeof window<"u",tu=Zr?document:null,Fr=Zr?window:null,zM=Zr?navigator:null;let yt,Ao;function nu(){let i=devicePixelRatio;yt!=i&&(yt=i,Ao&&su(Fd,Ao,nu),Ao=matchMedia(`(min-resolution: ${yt-.001}dppx) and (max-resolution: ${yt+.001}dppx)`),Fs(Fd,Ao,nu),Fr.dispatchEvent(new CustomEvent(Ko)))}function zn(i,e){if(e!=null){let t=i.classList;!t.contains(e)&&t.add(e)}}function iu(i,e){let t=i.classList;t.contains(e)&&t.remove(e)}function Nt(i,e,t){i.style[e]=t+"px"}function si(i,e,t,n){let s=tu.createElement(i);return e!=null&&zn(s,e),t!=null&&t.insertBefore(s,n),s}function Xn(i,e){return si("div",i,e)}const Od=new WeakMap;function vi(i,e,t,n,s){let r="translate("+e+"px,"+t+"px)",a=Od.get(i);r!=a&&(i.style.transform=r,Od.set(i,r),e<0||t<0||e>n||t>s?zn(i,Ls):iu(i,Ls))}const Bd=new WeakMap;function zd(i,e,t){let n=e+t,s=Bd.get(i);n!=s&&(Bd.set(i,n),i.style.background=e,i.style.borderColor=t)}const kd=new WeakMap;function Hd(i,e,t,n){let s=e+""+t,r=kd.get(i);s!=r&&(kd.set(i,s),i.style.height=t+"px",i.style.width=e+"px",i.style.marginLeft=n?-e/2+"px":0,i.style.marginTop=n?-t/2+"px":0)}const Iu={passive:!0},kM={...Iu,capture:!0};function Fs(i,e,t,n){e.addEventListener(i,t,n?kM:Iu)}function su(i,e,t,n){e.removeEventListener(i,t,Iu)}Zr&&nu();function ri(i,e,t,n){let s;t=t||0,n=n||e.length-1;let r=n<=2147483647;for(;n-t>1;)s=r?t+n>>1:kn((t+n)/2),e[s]<i?t=s:n=s;return i-e[t]<=e[n]-i?t:n}function lp(i){return(t,n,s)=>{let r=-1,a=-1;for(let o=n;o<=s;o++)if(i(t[o])){r=o;break}for(let o=s;o>=n;o--)if(i(t[o])){a=o;break}return[r,a]}}const cp=i=>i!=null,up=i=>i!=null&&i>0,ol=lp(cp),HM=lp(up);function VM(i,e,t,n=0,s=!1){let r=s?HM:ol,a=s?up:cp;[e,t]=r(i,e,t);let o=i[e],l=i[e];if(e>-1)if(n==1)o=i[e],l=i[t];else if(n==-1)o=i[t],l=i[e];else for(let c=e;c<=t;c++){let u=i[c];a(u)&&(u<o?o=u:u>l&&(l=u))}return[o??At,l??-At]}function ll(i,e,t,n){let s=Wd(i),r=Wd(e);i==e&&(s==-1?(i*=t,e/=t):(i/=t,e*=t));let a=t==10?Hi:hp,o=s==1?kn:Yn,l=r==1?Yn:kn,c=o(a(en(i))),u=l(a(en(e))),h=Xr(t,c),d=Xr(t,u);return t==10&&(c<0&&(h=Ct(h,-c)),u<0&&(d=Ct(d,-u))),n||t==2?(i=h*s,e=d*r):(i=mp(i,h),e=cl(e,d)),[i,e]}function Uu(i,e,t,n){let s=ll(i,e,t,n);return i==0&&(s[0]=0),e==0&&(s[1]=0),s}const Nu=.1,Vd={mode:3,pad:Nu},wa={pad:0,soft:null,mode:0},GM={min:wa,max:wa};function Zo(i,e,t,n){return ul(t)?Gd(i,e,t):(wa.pad=t,wa.soft=n?0:null,wa.mode=n?3:0,Gd(i,e,GM))}function vt(i,e){return i??e}function WM(i,e,t){for(e=vt(e,0),t=vt(t,i.length-1);e<=t;){if(i[e]!=null)return!0;e++}return!1}function Gd(i,e,t){let n=t.min,s=t.max,r=vt(n.pad,0),a=vt(s.pad,0),o=vt(n.hard,-At),l=vt(s.hard,At),c=vt(n.soft,At),u=vt(s.soft,-At),h=vt(n.mode,0),d=vt(s.mode,0),f=e-i,g=Hi(f),v=Pn(en(i),en(e)),m=Hi(v),p=en(m-g);(f<1e-24||p>10)&&(f=0,(i==0||e==0)&&(f=1e-24,h==2&&c!=At&&(r=0),d==2&&u!=-At&&(a=0)));let S=f||v||1e3,y=Hi(S),w=Xr(10,kn(y)),O=S*(f==0?i==0?.1:1:r),A=Ct(mp(i-O,w/10),24),P=i>=c&&(h==1||h==3&&A<=c||h==2&&A>=c)?c:At,N=Pn(o,A<P&&i>=P?P:li(P,A)),b=S*(f==0?e==0?.1:1:a),x=Ct(cl(e+b,w/10),24),R=e<=u&&(d==1||d==3&&x>=u||d==2&&x<=u)?u:-At,j=li(l,x>R&&e<=R?R:Pn(R,x));return N==j&&N==0&&(j=100),[N,j]}const XM=new Intl.NumberFormat(Zr?zM.language:"en-US"),Fu=i=>XM.format(i),Hn=Math,Bo=Hn.PI,en=Hn.abs,kn=Hn.floor,Qt=Hn.round,Yn=Hn.ceil,li=Hn.min,Pn=Hn.max,Xr=Hn.pow,Wd=Hn.sign,Hi=Hn.log10,hp=Hn.log2,qM=(i,e=1)=>Hn.sinh(i)*e,uc=(i,e=1)=>Hn.asinh(i/e),At=1/0;function Xd(i){return(Hi((i^i>>31)-(i>>31))|0)+1}function ru(i,e,t){return li(Pn(i,e),t)}function dp(i){return typeof i=="function"}function dt(i){return dp(i)?i:()=>i}const YM=()=>{},fp=i=>i,pp=(i,e)=>e,$M=i=>null,qd=i=>!0,Yd=(i,e)=>i==e,jM=/\.\d*?(?=9{6,}|0{6,})/gm,Hs=i=>{if(_p(i)||hs.has(i))return i;const e=`${i}`,t=e.match(jM);if(t==null)return i;let n=t[0].length-1;if(e.indexOf("e-")!=-1){let[s,r]=e.split("e");return+`${Hs(s)}e${r}`}return Ct(i,n)};function As(i,e){return Hs(Ct(Hs(i/e))*e)}function cl(i,e){return Hs(Yn(Hs(i/e))*e)}function mp(i,e){return Hs(kn(Hs(i/e))*e)}function Ct(i,e=0){if(_p(i))return i;let t=10**e,n=i*t*(1+Number.EPSILON);return Qt(n)/t}const hs=new Map;function gp(i){return((""+i).split(".")[1]||"").length}function Da(i,e,t,n){let s=[],r=n.map(gp);for(let a=e;a<t;a++){let o=en(a),l=Ct(Xr(i,a),o);for(let c=0;c<n.length;c++){let u=i==10?+`${n[c]}e${a}`:n[c]*l,h=(a>=0?0:o)+(a>=r[c]?0:r[c]),d=i==10?u:Ct(u,h);s.push(d),hs.set(d,h)}}return s}const Ta={},Ou=[],qr=[null,null],ss=Array.isArray,_p=Number.isInteger,KM=i=>i===void 0;function $d(i){return typeof i=="string"}function ul(i){let e=!1;if(i!=null){let t=i.constructor;e=t==null||t==Object}return e}function ZM(i){return i!=null&&typeof i=="object"}const JM=Object.getPrototypeOf(Uint8Array),vp="__proto__";function Yr(i,e=ul){let t;if(ss(i)){let n=i.find(s=>s!=null);if(ss(n)||e(n)){t=Array(i.length);for(let s=0;s<i.length;s++)t[s]=Yr(i[s],e)}else t=i.slice()}else if(i instanceof JM)t=i.slice();else if(e(i)){t={};for(let n in i)n!=vp&&(t[n]=Yr(i[n],e))}else t=i;return t}function Kt(i){let e=arguments;for(let t=1;t<e.length;t++){let n=e[t];for(let s in n)s!=vp&&(ul(i[s])?Kt(i[s],Yr(n[s])):i[s]=Yr(n[s]))}return i}const QM=0,eS=1,tS=2;function nS(i,e,t){for(let n=0,s,r=-1;n<e.length;n++){let a=e[n];if(a>r){for(s=a-1;s>=0&&i[s]==null;)i[s--]=null;for(s=a+1;s<t&&i[s]==null;)i[r=s++]=null}}}function iS(i,e){if(aS(i)){let a=i[0].slice();for(let o=1;o<i.length;o++)a.push(...i[o].slice(1));return oS(a[0])||(a=rS(a)),a}let t=new Set;for(let a=0;a<i.length;a++){let l=i[a][0],c=l.length;for(let u=0;u<c;u++)t.add(l[u])}let n=[Array.from(t).sort((a,o)=>a-o)],s=n[0].length,r=new Map;for(let a=0;a<s;a++)r.set(n[0][a],a);for(let a=0;a<i.length;a++){let o=i[a],l=o[0];for(let c=1;c<o.length;c++){let u=o[c],h=Array(s).fill(void 0),d=e?e[a][c]:eS,f=[];for(let g=0;g<u.length;g++){let v=u[g],m=r.get(l[g]);v===null?d!=QM&&(h[m]=v,d==tS&&f.push(m)):h[m]=v}nS(h,f,s),n.push(h)}}return n}const sS=typeof queueMicrotask>"u"?i=>Promise.resolve().then(i):queueMicrotask;function rS(i){let e=i[0],t=e.length,n=Array(t);for(let r=0;r<n.length;r++)n[r]=r;n.sort((r,a)=>e[r]-e[a]);let s=[];for(let r=0;r<i.length;r++){let a=i[r],o=Array(t);for(let l=0;l<t;l++)o[l]=a[n[l]];s.push(o)}return s}function aS(i){let e=i[0][0],t=e.length;for(let n=1;n<i.length;n++){let s=i[n][0];if(s.length!=t)return!1;if(s!=e){for(let r=0;r<t;r++)if(s[r]!=e[r])return!1}}return!0}function oS(i,e=100){const t=i.length;if(t<=1)return!0;let n=0,s=t-1;for(;n<=s&&i[n]==null;)n++;for(;s>=n&&i[s]==null;)s--;if(s<=n)return!0;const r=Pn(1,kn((s-n+1)/e));for(let a=i[n],o=n+r;o<=s;o+=r){const l=i[o];if(l!=null){if(l<=a)return!1;a=l}}return!0}const xp=["January","February","March","April","May","June","July","August","September","October","November","December"],yp=["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];function Mp(i){return i.slice(0,3)}const lS=yp.map(Mp),cS=xp.map(Mp),uS={MMMM:xp,MMM:cS,WWWW:yp,WWW:lS};function va(i){return(i<10?"0":"")+i}function hS(i){return(i<10?"00":i<100?"0":"")+i}const dS={YYYY:i=>i.getFullYear(),YY:i=>(i.getFullYear()+"").slice(2),MMMM:(i,e)=>e.MMMM[i.getMonth()],MMM:(i,e)=>e.MMM[i.getMonth()],MM:i=>va(i.getMonth()+1),M:i=>i.getMonth()+1,DD:i=>va(i.getDate()),D:i=>i.getDate(),WWWW:(i,e)=>e.WWWW[i.getDay()],WWW:(i,e)=>e.WWW[i.getDay()],HH:i=>va(i.getHours()),H:i=>i.getHours(),h:i=>{let e=i.getHours();return e==0?12:e>12?e-12:e},AA:i=>i.getHours()>=12?"PM":"AM",aa:i=>i.getHours()>=12?"pm":"am",a:i=>i.getHours()>=12?"p":"a",mm:i=>va(i.getMinutes()),m:i=>i.getMinutes(),ss:i=>va(i.getSeconds()),s:i=>i.getSeconds(),fff:i=>hS(i.getMilliseconds())};function Bu(i,e){e=e||uS;let t=[],n=/\{([a-z]+)\}|[^{]+/gi,s;for(;s=n.exec(i);)t.push(s[0][0]=="{"?dS[s[1]]:s[0]);return r=>{let a="";for(let o=0;o<t.length;o++)a+=typeof t[o]=="string"?t[o]:t[o](r,e);return a}}const fS=new Intl.DateTimeFormat().resolvedOptions().timeZone;function pS(i,e){let t;return e=="UTC"||e=="Etc/UTC"?t=new Date(+i+i.getTimezoneOffset()*6e4):e==fS?t=i:(t=new Date(i.toLocaleString("en-US",{timeZone:e})),t.setMilliseconds(i.getMilliseconds())),t}const Sp=i=>i%1==0,Jo=[1,2,2.5,5],mS=Da(10,-32,0,Jo),bp=Da(10,0,32,Jo),gS=bp.filter(Sp),Cs=mS.concat(bp),zu=`
`,Ep="{YYYY}",jd=zu+Ep,wp="{M}/{D}",ba=zu+wp,Co=ba+"/{YY}",Tp="{aa}",_S="{h}:{mm}",Tr=_S+Tp,Kd=zu+Tr,Zd=":{ss}",Mt=null;function Ap(i){let e=i*1e3,t=e*60,n=t*60,s=n*24,r=s*30,a=s*365,l=(i==1?Da(10,0,3,Jo).filter(Sp):Da(10,-3,0,Jo)).concat([e,e*5,e*10,e*15,e*30,t,t*5,t*10,t*15,t*30,n,n*2,n*3,n*4,n*6,n*8,n*12,s,s*2,s*3,s*4,s*5,s*6,s*7,s*8,s*9,s*10,s*15,r,r*2,r*3,r*4,r*6,a,a*2,a*5,a*10,a*25,a*50,a*100]);const c=[[a,Ep,Mt,Mt,Mt,Mt,Mt,Mt,1],[s*28,"{MMM}",jd,Mt,Mt,Mt,Mt,Mt,1],[s,wp,jd,Mt,Mt,Mt,Mt,Mt,1],[n,"{h}"+Tp,Co,Mt,ba,Mt,Mt,Mt,1],[t,Tr,Co,Mt,ba,Mt,Mt,Mt,1],[e,Zd,Co+" "+Tr,Mt,ba+" "+Tr,Mt,Kd,Mt,1],[i,Zd+".{fff}",Co+" "+Tr,Mt,ba+" "+Tr,Mt,Kd,Mt,1]];function u(h){return(d,f,g,v,m,p)=>{let S=[],y=m>=a,w=m>=r&&m<a,O=h(g),A=Ct(O*i,3),P=hc(O.getFullYear(),y?0:O.getMonth(),w||y?1:O.getDate()),N=Ct(P*i,3);if(w||y){let b=w?m/r:0,x=y?m/a:0,R=A==N?A:Ct(hc(P.getFullYear()+x,P.getMonth()+b,1)*i,3),j=new Date(Qt(R/i)),z=j.getFullYear(),K=j.getMonth();for(let X=0;R<=v;X++){let Q=hc(z+x*X,K+b*X,1),Y=Q-h(Ct(Q*i,3));R=Ct((+Q+Y)*i,3),R<=v&&S.push(R)}}else{let b=m>=s?s:m,x=kn(g)-kn(A),R=N+x+cl(A-N,b);S.push(R);let j=h(R),z=j.getHours()+j.getMinutes()/t+j.getSeconds()/n,K=m/n,X=d.axes[f]._space,Q=p/X;for(;R=Ct(R+m,i==1?0:3),!(R>v);)if(K>1){let Y=kn(Ct(z+K,6))%24,de=h(R).getHours()-Y;de>1&&(de=-1),R-=de*n,z=(z+K)%24;let xe=S[S.length-1];Ct((R-xe)/m,3)*Q>=.7&&S.push(R)}else S.push(R)}return S}}return[l,c,u]}const[vS,xS,yS]=Ap(1),[MS,SS,bS]=Ap(.001);Da(2,-53,53,[1]);function Jd(i,e){return i.map(t=>t.map((n,s)=>s==0||s==8||n==null?n:e(s==1||t[8]==0?n:t[1]+n)))}function Qd(i,e){return(t,n,s,r,a)=>{let o=e.find(g=>a>=g[0])||e[e.length-1],l,c,u,h,d,f;return n.map(g=>{let v=i(g),m=v.getFullYear(),p=v.getMonth(),S=v.getDate(),y=v.getHours(),w=v.getMinutes(),O=v.getSeconds(),A=m!=l&&o[2]||p!=c&&o[3]||S!=u&&o[4]||y!=h&&o[5]||w!=d&&o[6]||O!=f&&o[7]||o[1];return l=m,c=p,u=S,h=y,d=w,f=O,A(v)})}}function ES(i,e){let t=Bu(e);return(n,s,r,a,o)=>s.map(l=>t(i(l)))}function hc(i,e,t){return new Date(i,e,t)}function ef(i,e){return e(i)}const wS="{YYYY}-{MM}-{DD} {h}:{mm}{aa}";function tf(i,e){return(t,n,s,r)=>r==null?Du:e(i(n))}function TS(i,e){let t=i.series[e];return t.width?t.stroke(i,e):t.points.width?t.points.stroke(i,e):null}function AS(i,e){return i.series[e].fill(i,e)}const CS={show:!0,live:!0,isolate:!1,mount:YM,markers:{show:!0,width:2,stroke:TS,fill:AS,dash:"solid"},idx:null,idxs:null,values:[]};function RS(i,e){let t=i.cursor.points,n=Xn(),s=t.size(i,e);Nt(n,Ma,s),Nt(n,Sa,s);let r=s/-2;Nt(n,"marginLeft",r),Nt(n,"marginTop",r);let a=t.width(i,e,s);return a&&Nt(n,"borderWidth",a),n}function PS(i,e){let t=i.series[e].points;return t._fill||t._stroke}function LS(i,e){let t=i.series[e].points;return t._stroke||t._fill}function DS(i,e){return i.series[e].points.size}const dc=[0,0];function IS(i,e,t){return dc[0]=e,dc[1]=t,dc}function Ro(i,e,t,n=!0){return s=>{s.button==0&&(!n||s.target==e)&&t(s)}}function fc(i,e,t,n=!0){return s=>{(!n||s.target==e)&&t(s)}}const US={show:!0,x:!0,y:!0,lock:!1,move:IS,points:{one:!1,show:RS,size:DS,width:0,stroke:LS,fill:PS},bind:{mousedown:Ro,mouseup:Ro,click:Ro,dblclick:Ro,mousemove:fc,mouseleave:fc,mouseenter:fc},drag:{setScale:!0,x:!0,y:!1,dist:0,uni:null,click:(i,e)=>{e.stopPropagation(),e.stopImmediatePropagation()},_x:!1,_y:!1},focus:{dist:(i,e,t,n,s)=>n-s,prox:-1,bias:0},hover:{skip:[void 0],prox:null,bias:0},left:-10,top:-10,idx:null,dataIdx:null,idxs:null,event:null},Cp={show:!0,stroke:"rgba(0,0,0,0.07)",width:2},ku=Kt({},Cp,{filter:pp}),Rp=Kt({},ku,{size:10}),Pp=Kt({},Cp,{show:!1}),Hu='12px system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji"',Lp="bold "+Hu,Dp=1.5,nf={show:!0,scale:"x",stroke:Lu,space:50,gap:5,alignTo:1,size:50,labelGap:0,labelSize:30,labelFont:Lp,side:2,grid:ku,ticks:Rp,border:Pp,font:Hu,lineGap:Dp,rotate:0},NS="Value",FS="Time",sf={show:!0,scale:"x",auto:!1,sorted:1,min:At,max:-At,idxs:[]};function OS(i,e,t,n,s){return e.map(r=>r==null?"":Fu(r))}function BS(i,e,t,n,s,r,a){let o=[],l=hs.get(s)||0;t=a?t:Ct(cl(t,s),l);for(let c=t;c<=n;c=Ct(c+s,l))o.push(Object.is(c,-0)?0:c);return o}function au(i,e,t,n,s,r,a){const o=[],l=i.scales[i.axes[e].scale].log,c=l==10?Hi:hp,u=kn(c(t));s=Xr(l,u),l==10&&(s=Cs[ri(s,Cs)]);let h=t,d=s*l;l==10&&(d=Cs[ri(d,Cs)]);do o.push(h),h=h+s,l==10&&!hs.has(h)&&(h=Ct(h,hs.get(s))),h>=d&&(s=h,d=s*l,l==10&&(d=Cs[ri(d,Cs)]));while(h<=n);return o}function zS(i,e,t,n,s,r,a){let l=i.scales[i.axes[e].scale].asinh,c=n>l?au(i,e,Pn(l,t),n,s):[l],u=n>=0&&t<=0?[0]:[];return(t<-l?au(i,e,Pn(l,-n),-t,s):[l]).reverse().map(d=>-d).concat(u,c)}const Ip=/./,kS=/[12357]/,HS=/[125]/,rf=/1/,ou=(i,e,t,n)=>i.map((s,r)=>e==4&&s==0||r%n==0&&t.test(s.toExponential()[s<0?1:0])?s:null);function VS(i,e,t,n,s){let r=i.axes[t],a=r.scale,o=i.scales[a],l=i.valToPos,c=r._space,u=l(10,a),h=l(9,a)-u>=c?Ip:l(7,a)-u>=c?kS:l(5,a)-u>=c?HS:rf;if(h==rf){let d=en(l(1,a)-u);if(d<c)return ou(e.slice().reverse(),o.distr,h,Yn(c/d)).reverse()}return ou(e,o.distr,h,1)}function GS(i,e,t,n,s){let r=i.axes[t],a=r.scale,o=r._space,l=i.valToPos,c=en(l(1,a)-l(2,a));return c<o?ou(e.slice().reverse(),3,Ip,Yn(o/c)).reverse():e}function WS(i,e,t,n){return n==null?Du:e==null?"":Fu(e)}const af={show:!0,scale:"y",stroke:Lu,space:30,gap:5,alignTo:1,size:50,labelGap:0,labelSize:30,labelFont:Lp,side:3,grid:ku,ticks:Rp,border:Pp,font:Hu,lineGap:Dp,rotate:0};function XS(i,e){let t=3+(i||1)*2;return Ct(t*e,3)}function qS(i,e){let{scale:t,idxs:n}=i.series[0],s=i._data[0],r=i.valToPos(s[n[0]],t,!0),a=i.valToPos(s[n[1]],t,!0),o=en(a-r),l=i.series[e],c=o/(l.points.space*yt);return n[1]-n[0]<=c}const of={scale:null,auto:!0,sorted:0,min:At,max:-At},Up=(i,e,t,n,s)=>s,lf={show:!0,auto:!0,sorted:0,gaps:Up,alpha:1,facets:[Kt({},of,{scale:"x"}),Kt({},of,{scale:"y"})]},cf={scale:"y",auto:!0,sorted:0,show:!0,spanGaps:!1,gaps:Up,alpha:1,points:{show:qS,filter:null},values:null,min:At,max:-At,idxs:[],path:null,clip:null};function YS(i,e,t,n,s){return t/10}const Np={time:vM,auto:!0,distr:1,log:10,asinh:1,min:null,max:null,dir:1,ori:0},$S=Kt({},Np,{time:!1,ori:1}),uf={};function Fp(i,e){let t=uf[i];return t||(t={key:i,plots:[],sub(n){t.plots.push(n)},unsub(n){t.plots=t.plots.filter(s=>s!=n)},pub(n,s,r,a,o,l,c){for(let u=0;u<t.plots.length;u++)t.plots[u]!=s&&t.plots[u].pub(n,s,r,a,o,l,c)}},i!=null&&(uf[i]=t)),t}const $r=1,lu=2;function Vs(i,e,t){const n=i.mode,s=i.series[e],r=n==2?i._data[e]:i._data,a=i.scales,o=i.bbox;let l=r[0],c=n==2?r[1]:r[e],u=n==2?a[s.facets[0].scale]:a[i.series[0].scale],h=n==2?a[s.facets[1].scale]:a[s.scale],d=o.left,f=o.top,g=o.width,v=o.height,m=i.valToPosH,p=i.valToPosV;return u.ori==0?t(s,l,c,u,h,m,p,d,f,g,v,dl,Jr,pl,Bp,kp):t(s,l,c,u,h,p,m,f,d,v,g,fl,Qr,Wu,zp,Hp)}function Vu(i,e){let t=0,n=0,s=vt(i.bands,Ou);for(let r=0;r<s.length;r++){let a=s[r];a.series[0]==e?t=a.dir:a.series[1]==e&&(a.dir==1?n|=1:n|=2)}return[t,n==1?-1:n==2?1:n==3?2:0]}function jS(i,e,t,n,s){let r=i.mode,a=i.series[e],o=r==2?a.facets[1].scale:a.scale,l=i.scales[o];return s==-1?l.min:s==1?l.max:l.distr==3?l.dir==1?l.min:l.max:0}function Vi(i,e,t,n,s,r){return Vs(i,e,(a,o,l,c,u,h,d,f,g,v,m)=>{let p=a.pxRound;const S=c.dir*(c.ori==0?1:-1),y=c.ori==0?Jr:Qr;let w,O;S==1?(w=t,O=n):(w=n,O=t);let A=p(h(o[w],c,v,f)),P=p(d(l[w],u,m,g)),N=p(h(o[O],c,v,f)),b=p(d(r==1?u.max:u.min,u,m,g)),x=new Path2D(s);return y(x,N,b),y(x,A,b),y(x,A,P),x})}function hl(i,e,t,n,s,r){let a=null;if(i.length>0){a=new Path2D;const o=e==0?pl:Wu;let l=t;for(let h=0;h<i.length;h++){let d=i[h];if(d[1]>d[0]){let f=d[0]-l;f>0&&o(a,l,n,f,n+r),l=d[1]}}let c=t+s-l,u=10;c>0&&o(a,l,n-u/2,c,n+r+u)}return a}function KS(i,e,t){let n=i[i.length-1];n&&n[0]==e?n[1]=t:i.push([e,t])}function Gu(i,e,t,n,s,r,a){let o=[],l=i.length;for(let c=s==1?t:n;c>=t&&c<=n;c+=s)if(e[c]===null){let h=c,d=c;if(s==1)for(;++c<=n&&e[c]===null;)d=c;else for(;--c>=t&&e[c]===null;)d=c;let f=r(i[h]),g=d==h?f:r(i[d]),v=h-s;f=a<=0&&v>=0&&v<l?r(i[v]):f;let p=d+s;g=a>=0&&p>=0&&p<l?r(i[p]):g,g>=f&&o.push([f,g])}return o}function hf(i){return i==0?fp:i==1?Qt:e=>As(e,i)}function Op(i){let e=i==0?dl:fl,t=i==0?(s,r,a,o,l,c)=>{s.arcTo(r,a,o,l,c)}:(s,r,a,o,l,c)=>{s.arcTo(a,r,l,o,c)},n=i==0?(s,r,a,o,l)=>{s.rect(r,a,o,l)}:(s,r,a,o,l)=>{s.rect(a,r,l,o)};return(s,r,a,o,l,c=0,u=0)=>{c==0&&u==0?n(s,r,a,o,l):(c=li(c,o/2,l/2),u=li(u,o/2,l/2),e(s,r+c,a),t(s,r+o,a,r+o,a+l,c),t(s,r+o,a+l,r,a+l,u),t(s,r,a+l,r,a,u),t(s,r,a,r+o,a,c),s.closePath())}}const dl=(i,e,t)=>{i.moveTo(e,t)},fl=(i,e,t)=>{i.moveTo(t,e)},Jr=(i,e,t)=>{i.lineTo(e,t)},Qr=(i,e,t)=>{i.lineTo(t,e)},pl=Op(0),Wu=Op(1),Bp=(i,e,t,n,s,r)=>{i.arc(e,t,n,s,r)},zp=(i,e,t,n,s,r)=>{i.arc(t,e,n,s,r)},kp=(i,e,t,n,s,r,a)=>{i.bezierCurveTo(e,t,n,s,r,a)},Hp=(i,e,t,n,s,r,a)=>{i.bezierCurveTo(t,e,s,n,a,r)};function Vp(i){return(e,t,n,s,r)=>Vs(e,t,(a,o,l,c,u,h,d,f,g,v,m)=>{let{pxRound:p,points:S}=a,y,w;c.ori==0?(y=dl,w=Bp):(y=fl,w=zp);const O=Ct(S.width*yt,3);let A=(S.size-S.width)/2*yt,P=Ct(A*2,3),N=new Path2D,b=new Path2D,{left:x,top:R,width:j,height:z}=e.bbox;pl(b,x-P,R-P,j+P*2,z+P*2);const K=X=>{if(l[X]!=null){let Q=p(h(o[X],c,v,f)),Y=p(d(l[X],u,m,g));y(N,Q+A,Y),w(N,Q,Y,A,0,Bo*2)}};if(r)r.forEach(K);else for(let X=n;X<=s;X++)K(X);return{stroke:O>0?N:null,fill:N,clip:b,flags:$r|lu}})}function Gp(i){return(e,t,n,s,r,a)=>{n!=s&&(r!=n&&a!=n&&i(e,t,n),r!=s&&a!=s&&i(e,t,s),i(e,t,a))}}const ZS=Gp(Jr),JS=Gp(Qr);function Wp(i){const e=vt(i==null?void 0:i.alignGaps,0);return(t,n,s,r)=>Vs(t,n,(a,o,l,c,u,h,d,f,g,v,m)=>{[s,r]=ol(l,s,r);let p=a.pxRound,S=z=>p(h(z,c,v,f)),y=z=>p(d(z,u,m,g)),w,O;c.ori==0?(w=Jr,O=ZS):(w=Qr,O=JS);const A=c.dir*(c.ori==0?1:-1),P={stroke:new Path2D,fill:null,clip:null,band:null,gaps:null,flags:$r},N=P.stroke;let b=!1;if(r-s>=v*4){let z=ye=>t.posToVal(ye,c.key,!0),K=null,X=null,Q,Y,ne,ge=S(o[A==1?s:r]),de=S(o[s]),xe=S(o[r]),we=z(A==1?de+1:xe-1);for(let ye=A==1?s:r;ye>=s&&ye<=r;ye+=A){let ie=o[ye],Me=(A==1?ie<we:ie>we)?ge:S(ie),fe=l[ye];Me==ge?fe!=null?(Y=fe,K==null?(w(N,Me,y(Y)),Q=K=X=Y):Y<K?K=Y:Y>X&&(X=Y)):fe===null&&(b=!0):(K!=null&&O(N,ge,y(K),y(X),y(Q),y(Y)),fe!=null?(Y=fe,w(N,Me,y(Y)),K=X=Q=Y):(K=X=null,fe===null&&(b=!0)),ge=Me,we=z(ge+A))}K!=null&&K!=X&&ne!=ge&&O(N,ge,y(K),y(X),y(Q),y(Y))}else for(let z=A==1?s:r;z>=s&&z<=r;z+=A){let K=l[z];K===null?b=!0:K!=null&&w(N,S(o[z]),y(K))}let[R,j]=Vu(t,n);if(a.fill!=null||R!=0){let z=P.fill=new Path2D(N),K=a.fillTo(t,n,a.min,a.max,R),X=y(K),Q=S(o[s]),Y=S(o[r]);A==-1&&([Y,Q]=[Q,Y]),w(z,Y,X),w(z,Q,X)}if(!a.spanGaps){let z=[];b&&z.push(...Gu(o,l,s,r,A,S,e)),P.gaps=z=a.gaps(t,n,s,r,z),P.clip=hl(z,c.ori,f,g,v,m)}return j!=0&&(P.band=j==2?[Vi(t,n,s,r,N,-1),Vi(t,n,s,r,N,1)]:Vi(t,n,s,r,N,j)),P})}function QS(i){const e=vt(i.align,1),t=vt(i.ascDesc,!1),n=vt(i.alignGaps,0),s=vt(i.extend,!1);return(r,a,o,l)=>Vs(r,a,(c,u,h,d,f,g,v,m,p,S,y)=>{[o,l]=ol(h,o,l);let w=c.pxRound,{left:O,width:A}=r.bbox,P=de=>w(g(de,d,S,m)),N=de=>w(v(de,f,y,p)),b=d.ori==0?Jr:Qr;const x={stroke:new Path2D,fill:null,clip:null,band:null,gaps:null,flags:$r},R=x.stroke,j=d.dir*(d.ori==0?1:-1);let z=N(h[j==1?o:l]),K=P(u[j==1?o:l]),X=K,Q=K;s&&e==-1&&(Q=O,b(R,Q,z)),b(R,K,z);for(let de=j==1?o:l;de>=o&&de<=l;de+=j){let xe=h[de];if(xe==null)continue;let we=P(u[de]),ye=N(xe);e==1?b(R,we,z):b(R,X,ye),b(R,we,ye),z=ye,X=we}let Y=X;s&&e==1&&(Y=O+A,b(R,Y,z));let[ne,ge]=Vu(r,a);if(c.fill!=null||ne!=0){let de=x.fill=new Path2D(R),xe=c.fillTo(r,a,c.min,c.max,ne),we=N(xe);b(de,Y,we),b(de,Q,we)}if(!c.spanGaps){let de=[];de.push(...Gu(u,h,o,l,j,P,n));let xe=c.width*yt/2,we=t||e==1?xe:-xe,ye=t||e==-1?-xe:xe;de.forEach(ie=>{ie[0]+=we,ie[1]+=ye}),x.gaps=de=c.gaps(r,a,o,l,de),x.clip=hl(de,d.ori,m,p,S,y)}return ge!=0&&(x.band=ge==2?[Vi(r,a,o,l,R,-1),Vi(r,a,o,l,R,1)]:Vi(r,a,o,l,R,ge)),x})}function df(i,e,t,n,s,r,a=At){if(i.length>1){let o=null;for(let l=0,c=1/0;l<i.length;l++)if(e[l]!==void 0){if(o!=null){let u=en(i[l]-i[o]);u<c&&(c=u,a=en(t(i[l],n,s,r)-t(i[o],n,s,r)))}o=l}}return a}function eb(i){i=i||Ta;const e=vt(i.size,[.6,At,1]),t=i.align||0,n=i.gap||0;let s=i.radius;s=s==null?[0,0]:typeof s=="number"?[s,0]:s;const r=dt(s),a=1-e[0],o=vt(e[1],At),l=vt(e[2],1),c=vt(i.disp,Ta),u=vt(i.each,f=>{}),{fill:h,stroke:d}=c;return(f,g,v,m)=>Vs(f,g,(p,S,y,w,O,A,P,N,b,x,R)=>{let j=p.pxRound,z=t,K=n*yt,X=o*yt,Q=l*yt,Y,ne;w.ori==0?[Y,ne]=r(f,g):[ne,Y]=r(f,g);const ge=w.dir*(w.ori==0?1:-1);let de=w.ori==0?pl:Wu,xe=w.ori==0?u:(W,Ee,_e,Ae,Ke,me,Te)=>{u(W,Ee,_e,Ke,Ae,Te,me)},we=vt(f.bands,Ou).find(W=>W.series[0]==g),ye=we!=null?we.dir:0,ie=p.fillTo(f,g,p.min,p.max,ye),ue=j(P(ie,O,R,b)),Me,fe,ze,Ge=x,Fe=j(p.width*yt),ft=!1,U=null,ht=null,it=null,lt=null;h!=null&&(Fe==0||d!=null)&&(ft=!0,U=h.values(f,g,v,m),ht=new Map,new Set(U).forEach(W=>{W!=null&&ht.set(W,new Path2D)}),Fe>0&&(it=d.values(f,g,v,m),lt=new Map,new Set(it).forEach(W=>{W!=null&&lt.set(W,new Path2D)})));let{x0:Oe,size:bt}=c;if(Oe!=null&&bt!=null){z=1,S=Oe.values(f,g,v,m),Oe.unit==2&&(S=S.map(_e=>f.posToVal(N+_e*x,w.key,!0)));let W=bt.values(f,g,v,m);bt.unit==2?fe=W[0]*x:fe=A(W[0],w,x,N)-A(0,w,x,N),Ge=df(S,y,A,w,x,N,Ge),ze=Ge-fe+K}else Ge=df(S,y,A,w,x,N,Ge),ze=Ge*a+K,fe=Ge-ze;ze<1&&(ze=0),Fe>=fe/2&&(Fe=0),ze<5&&(j=fp);let Ye=ze>0,Xe=Ge-ze-(Ye?Fe:0);fe=j(ru(Xe,Q,X)),Me=(z==0?fe/2:z==ge?0:fe)-z*ge*((z==0?K/2:0)+(Ye?Fe/2:0));const D={stroke:null,fill:null,clip:null,band:null,gaps:null,flags:0},E=ft?null:new Path2D;let J=null;if(we!=null)J=f.data[we.series[1]];else{let{y0:W,y1:Ee}=c;W!=null&&Ee!=null&&(y=Ee.values(f,g,v,m),J=W.values(f,g,v,m))}let le=Y*fe,ee=ne*fe;for(let W=ge==1?v:m;W>=v&&W<=m;W+=ge){let Ee=y[W];if(Ee==null)continue;if(J!=null){let be=J[W]??0;if(Ee-be==0)continue;ue=P(be,O,R,b)}let _e=w.distr!=2||c!=null?S[W]:W,Ae=A(_e,w,x,N),Ke=P(vt(Ee,ie),O,R,b),me=j(Ae-Me),Te=j(Pn(Ke,ue)),Ze=j(li(Ke,ue)),ke=Te-Ze;if(Ee!=null){let be=Ee<0?ee:le,He=Ee<0?le:ee;ft?(Fe>0&&it[W]!=null&&de(lt.get(it[W]),me,Ze+kn(Fe/2),fe,Pn(0,ke-Fe),be,He),U[W]!=null&&de(ht.get(U[W]),me,Ze+kn(Fe/2),fe,Pn(0,ke-Fe),be,He)):de(E,me,Ze+kn(Fe/2),fe,Pn(0,ke-Fe),be,He),xe(f,g,W,me-Fe/2,Ze,fe+Fe,ke)}}return Fe>0?D.stroke=ft?lt:E:ft||(D._fill=p.width==0?p._fill:p._stroke??p._fill,D.width=0),D.fill=ft?ht:E,D})}function tb(i,e){const t=vt(e==null?void 0:e.alignGaps,0);return(n,s,r,a)=>Vs(n,s,(o,l,c,u,h,d,f,g,v,m,p)=>{[r,a]=ol(c,r,a);let S=o.pxRound,y=Y=>S(d(Y,u,m,g)),w=Y=>S(f(Y,h,p,v)),O,A,P;u.ori==0?(O=dl,P=Jr,A=kp):(O=fl,P=Qr,A=Hp);const N=u.dir*(u.ori==0?1:-1);let b=y(l[N==1?r:a]),x=b,R=[],j=[];for(let Y=N==1?r:a;Y>=r&&Y<=a;Y+=N)if(c[Y]!=null){let ge=l[Y],de=y(ge);R.push(x=de),j.push(w(c[Y]))}const z={stroke:i(R,j,O,P,A,S),fill:null,clip:null,band:null,gaps:null,flags:$r},K=z.stroke;let[X,Q]=Vu(n,s);if(o.fill!=null||X!=0){let Y=z.fill=new Path2D(K),ne=o.fillTo(n,s,o.min,o.max,X),ge=w(ne);P(Y,x,ge),P(Y,b,ge)}if(!o.spanGaps){let Y=[];Y.push(...Gu(l,c,r,a,N,y,t)),z.gaps=Y=o.gaps(n,s,r,a,Y),z.clip=hl(Y,u.ori,g,v,m,p)}return Q!=0&&(z.band=Q==2?[Vi(n,s,r,a,K,-1),Vi(n,s,r,a,K,1)]:Vi(n,s,r,a,K,Q)),z})}function nb(i){return tb(ib,i)}function ib(i,e,t,n,s,r){const a=i.length;if(a<2)return null;const o=new Path2D;if(t(o,i[0],e[0]),a==2)n(o,i[1],e[1]);else{let l=Array(a),c=Array(a-1),u=Array(a-1),h=Array(a-1);for(let d=0;d<a-1;d++)u[d]=e[d+1]-e[d],h[d]=i[d+1]-i[d],c[d]=u[d]/h[d];l[0]=c[0];for(let d=1;d<a-1;d++)c[d]===0||c[d-1]===0||c[d-1]>0!=c[d]>0?l[d]=0:(l[d]=3*(h[d-1]+h[d])/((2*h[d]+h[d-1])/c[d-1]+(h[d]+2*h[d-1])/c[d]),isFinite(l[d])||(l[d]=0));l[a-1]=c[a-2];for(let d=0;d<a-1;d++)s(o,i[d]+h[d]/3,e[d]+l[d]*h[d]/3,i[d+1]-h[d]/3,e[d+1]-l[d+1]*h[d]/3,i[d+1],e[d+1])}return o}const cu=new Set;function ff(){for(let i of cu)i.syncRect(!0)}Zr&&(Fs(OM,Fr,ff),Fs(BM,Fr,ff,!0),Fs(Ko,Fr,()=>{dn.pxRatio=yt}));const sb=Wp(),rb=Vp();function pf(i,e,t,n){return(n?[i[0],i[1]].concat(i.slice(2)):[i[0]].concat(i.slice(1))).map((r,a)=>uu(r,a,e,t))}function ab(i,e){return i.map((t,n)=>n==0?{}:Kt({},e,t))}function uu(i,e,t,n){return Kt({},e==0?t:n,i)}function Xp(i,e,t){return e==null?qr:[e,t]}const ob=Xp;function lb(i,e,t){return e==null?qr:Zo(e,t,Nu,!0)}function qp(i,e,t,n){return e==null?qr:ll(e,t,i.scales[n].log,!1)}const cb=qp;function Yp(i,e,t,n){return e==null?qr:Uu(e,t,i.scales[n].log,!1)}const ub=Yp;function hb(i,e,t,n,s){let r=Pn(Xd(i),Xd(e)),a=e-i,o=ri(s/n*a,t);do{let l=t[o],c=n*l/a;if(c>=s&&r+(l<5?hs.get(l):0)<=17)return[l,c]}while(++o<t.length);return[0,0]}function mf(i){let e,t;return i=i.replace(/(\d+)px/,(n,s)=>(e=Qt((t=+s)*yt))+"px"),[i,e,t]}function db(i){i.show&&[i.font,i.labelFont].forEach(e=>{let t=Ct(e[2]*yt,1);e[0]=e[0].replace(/[0-9.]+px/,t+"px"),e[1]=t})}function dn(i,e,t){const n={mode:vt(i.mode,1)},s=n.mode;function r(_,M,C,L){let B=M.valToPct(_);return L+C*(M.dir==-1?1-B:B)}function a(_,M,C,L){let B=M.valToPct(_);return L+C*(M.dir==-1?B:1-B)}function o(_,M,C,L){return M.ori==0?r(_,M,C,L):a(_,M,C,L)}n.valToPosH=r,n.valToPosV=a;let l=!1;n.status=0;const c=n.root=Xn(xM);if(i.id!=null&&(c.id=i.id),zn(c,i.class),i.title){let _=Xn(SM,c);_.textContent=i.title}const u=si("canvas"),h=n.ctx=u.getContext("2d"),d=Xn(bM,c);Fs("click",d,_=>{_.target===g&&(Dt!=$s||kt!=js)&&mn.click(n,_)},!0);const f=n.under=Xn(EM,d);d.appendChild(u);const g=n.over=Xn(wM,d);i=Yr(i);const v=+vt(i.pxAlign,1),m=hf(v);(i.plugins||[]).forEach(_=>{_.opts&&(i=_.opts(n,i)||i)});const p=i.ms||.001,S=n.series=s==1?pf(i.series||[],sf,cf,!1):ab(i.series||[null],lf),y=n.axes=pf(i.axes||[],nf,af,!0),w=n.scales={},O=n.bands=i.bands||[];O.forEach(_=>{_.fill=dt(_.fill||null),_.dir=vt(_.dir,-1)});const A=s==2?S[1].facets[0].scale:S[0].scale,P={axes:im,series:Dn},N=(i.drawOrder||["axes","series"]).map(_=>P[_]);function b(_){const M=_.distr==3?C=>Hi(C>0?C:_.clamp(n,C,_.min,_.max,_.key)):_.distr==4?C=>uc(C,_.asinh):_.distr==100?C=>_.fwd(C):C=>C;return C=>{let L=M(C),{_min:B,_max:$}=_,oe=$-B;return(L-B)/oe}}function x(_){let M=w[_];if(M==null){let C=(i.scales||Ta)[_]||Ta;if(C.from!=null){x(C.from);let L=Kt({},w[C.from],C,{key:_});L.valToPct=b(L),w[_]=L}else{M=w[_]=Kt({},_==A?Np:$S,C),M.key=_;let L=M.time,B=M.range,$=ss(B);if((_!=A||s==2&&!L)&&($&&(B[0]==null||B[1]==null)&&(B={min:B[0]==null?Vd:{mode:1,hard:B[0],soft:B[0]},max:B[1]==null?Vd:{mode:1,hard:B[1],soft:B[1]}},$=!1),!$&&ul(B))){let oe=B;B=(pe,Se,Le)=>Se==null?qr:Zo(Se,Le,oe)}M.range=dt(B||(L?ob:_==A?M.distr==3?cb:M.distr==4?ub:Xp:M.distr==3?qp:M.distr==4?Yp:lb)),M.auto=dt($?!1:M.auto),M.clamp=dt(M.clamp||YS),M._min=M._max=null,M.valToPct=b(M)}}}x("x"),x("y"),s==1&&S.forEach(_=>{x(_.scale)}),y.forEach(_=>{x(_.scale)});for(let _ in i.scales)x(_);const R=w[A],j=R.distr;let z,K;R.ori==0?(zn(c,yM),z=r,K=a):(zn(c,MM),z=a,K=r);const X={};for(let _ in w){let M=w[_];(M.min!=null||M.max!=null)&&(X[_]={min:M.min,max:M.max},M.min=M.max=null)}const Q=i.tzDate||(_=>new Date(Qt(_/p))),Y=i.fmtDate||Bu,ne=p==1?yS(Q):bS(Q),ge=Qd(Q,Jd(p==1?xS:SS,Y)),de=tf(Q,ef(wS,Y)),xe=[],we=n.legend=Kt({},CS,i.legend),ye=n.cursor=Kt({},US,{drag:{y:s==2}},i.cursor),ie=we.show,ue=ye.show,Me=we.markers;we.idxs=xe,Me.width=dt(Me.width),Me.dash=dt(Me.dash),Me.stroke=dt(Me.stroke),Me.fill=dt(Me.fill);let fe,ze,Ge,Fe=[],ft=[],U,ht=!1,it={};if(we.live){const _=S[1]?S[1].values:null;ht=_!=null,U=ht?_(n,1,0):{_:0};for(let M in U)it[M]=Du}if(ie)if(fe=si("table",LM,c),Ge=si("tbody",null,fe),we.mount(n,fe),ht){ze=si("thead",null,fe,Ge);let _=si("tr",null,ze);si("th",null,_);for(var lt in U)si("th",Rd,_).textContent=lt}else zn(fe,IM),we.live&&zn(fe,DM);const Oe={show:!0},bt={show:!1};function Ye(_,M){if(M==0&&(ht||!we.live||s==2))return qr;let C=[],L=si("tr",UM,Ge,Ge.childNodes[M]);zn(L,_.class),_.show||zn(L,Ls);let B=si("th",null,L);if(Me.show){let pe=Xn(NM,B);if(M>0){let Se=Me.width(n,M);Se&&(pe.style.border=Se+"px "+Me.dash(n,M)+" "+Me.stroke(n,M)),pe.style.background=Me.fill(n,M)}}let $=Xn(Rd,B);_.label instanceof HTMLElement?$.appendChild(_.label):$.textContent=_.label,M>0&&(Me.show||($.style.color=_.width>0?Me.stroke(n,M):Me.fill(n,M)),D("click",B,pe=>{if(ye._lock)return;Bt(pe);let Se=S.indexOf(_);if((pe.ctrlKey||pe.metaKey)!=we.isolate){let Le=S.some((De,Ne)=>Ne>0&&Ne!=Se&&De.show);S.forEach((De,Ne)=>{Ne>0&&pi(Ne,Le?Ne==Se?Oe:bt:Oe,!0,$t.setSeries)})}else pi(Se,{show:!_.show},!0,$t.setSeries)},!1),di&&D(Id,B,pe=>{ye._lock||(Bt(pe),pi(S.indexOf(_),Zs,!0,$t.setSeries))},!1));for(var oe in U){let pe=si("td",FM,L);pe.textContent="--",C.push(pe)}return[L,C]}const Xe=new Map;function D(_,M,C,L=!0){const B=Xe.get(M)||{},$=ye.bind[_](n,M,C,L);$&&(Fs(_,M,B[_]=$),Xe.set(M,B))}function E(_,M,C){const L=Xe.get(M)||{};for(let B in L)(_==null||B==_)&&(su(B,M,L[B]),delete L[B]);_==null&&Xe.delete(M)}let J=0,le=0,ee=0,W=0,Ee=0,_e=0,Ae=Ee,Ke=_e,me=ee,Te=W,Ze=0,ke=0,be=0,He=0;n.bbox={};let F=!1,ce=!1,I=!1,ae=!1,se=!1,re=!1;function ve(_,M,C){(C||_!=n.width||M!=n.height)&&je(_,M),Ws(!1),I=!0,ce=!0,Xs()}function je(_,M){n.width=J=ee=_,n.height=le=W=M,Ee=_e=0,ot(),fn();let C=n.bbox;Ze=C.left=As(Ee*yt,.5),ke=C.top=As(_e*yt,.5),be=C.width=As(ee*yt,.5),He=C.height=As(W*yt,.5)}const at=3;function gt(){let _=!1,M=0;for(;!_;){M++;let C=tm(M),L=nm(M);_=M==at||C&&L,_||(je(n.width,n.height),ce=!0)}}function Et({width:_,height:M}){ve(_,M)}n.setSize=Et;function ot(){let _=!1,M=!1,C=!1,L=!1;y.forEach((B,$)=>{if(B.show&&B._show){let{side:oe,_size:pe}=B,Se=oe%2,Le=B.label!=null?B.labelSize:0,De=pe+Le;De>0&&(Se?(ee-=De,oe==3?(Ee+=De,L=!0):C=!0):(W-=De,oe==0?(_e+=De,_=!0):M=!0))}}),Ti[0]=_,Ti[1]=C,Ti[2]=M,Ti[3]=L,ee-=Z[1]+Z[3],Ee+=Z[3],W-=Z[2]+Z[0],_e+=Z[0]}function fn(){let _=Ee+ee,M=_e+W,C=Ee,L=_e;function B($,oe){switch($){case 1:return _+=oe,_-oe;case 2:return M+=oe,M-oe;case 3:return C-=oe,C+oe;case 0:return L-=oe,L+oe}}y.forEach(($,oe)=>{if($.show&&$._show){let pe=$.side;$._pos=B(pe,$._size),$.label!=null&&($._lpos=B(pe,$.labelSize))}})}if(ye.dataIdx==null){let _=ye.hover,M=_.skip=new Set(_.skip??[]);M.add(void 0);let C=_.prox=dt(_.prox),L=_.bias??(_.bias=0);ye.dataIdx=(B,$,oe,pe)=>{if($==0)return oe;let Se=oe,Le=C(B,$,oe,pe)??At,De=Le>=0&&Le<At,Ne=R.ori==0?ee:W,tt=ye.left,xt=e[0],_t=e[$];if(M.has(_t[oe])){Se=null;let ut=null,et=null,We;if(L==0||L==-1)for(We=oe;ut==null&&We-- >0;)M.has(_t[We])||(ut=We);if(L==0||L==1)for(We=oe;et==null&&We++<_t.length;)M.has(_t[We])||(et=We);if(ut!=null||et!=null)if(De){let Ut=ut==null?-1/0:z(xt[ut],R,Ne,0),Gt=et==null?1/0:z(xt[et],R,Ne,0),un=tt-Ut,Tt=Gt-tt;un<=Tt?un<=Le&&(Se=ut):Tt<=Le&&(Se=et)}else Se=et==null?ut:ut==null?et:oe-ut<=et-oe?ut:et}else De&&en(tt-z(xt[oe],R,Ne,0))>Le&&(Se=null);return Se}}const Bt=_=>{ye.event=_};ye.idxs=xe,ye._lock=!1;let zt=ye.points;zt.show=dt(zt.show),zt.size=dt(zt.size),zt.stroke=dt(zt.stroke),zt.width=dt(zt.width),zt.fill=dt(zt.fill);const an=n.focus=Kt({},i.focus||{alpha:.3},ye.focus),di=an.prox>=0,Ei=di&&zt.one;let En=[],Jn=[],wi=[];function ms(_,M){let C=zt.show(n,M);if(C instanceof HTMLElement)return zn(C,PM),zn(C,_.class),vi(C,-10,-10,ee,W),g.insertBefore(C,En[M]),C}function ta(_,M){if(s==1||M>0){let C=s==1&&w[_.scale].time,L=_.value;_.value=C?$d(L)?tf(Q,ef(L,Y)):L||de:L||WS,_.label=_.label||(C?FS:NS)}if(Ei||M>0){_.width=_.width==null?1:_.width,_.paths=_.paths||sb||$M,_.fillTo=dt(_.fillTo||jS),_.pxAlign=+vt(_.pxAlign,v),_.pxRound=hf(_.pxAlign),_.stroke=dt(_.stroke||null),_.fill=dt(_.fill||null),_._stroke=_._fill=_._paths=_._focus=null;let C=XS(Pn(1,_.width),1),L=_.points=Kt({},{size:C,width:Pn(1,C*.2),stroke:_.stroke,space:C*2,paths:rb,_stroke:null,_fill:null},_.points);L.show=dt(L.show),L.filter=dt(L.filter),L.fill=dt(L.fill),L.stroke=dt(L.stroke),L.paths=dt(L.paths),L.pxAlign=_.pxAlign}if(ie){let C=Ye(_,M);Fe.splice(M,0,C[0]),ft.splice(M,0,C[1]),we.values.push(null)}if(ue){xe.splice(M,0,null);let C=null;Ei?M==0&&(C=ms(_,M)):M>0&&(C=ms(_,M)),En.splice(M,0,C),Jn.splice(M,0,0),wi.splice(M,0,0)}cn("addSeries",M)}function za(_,M){M=M??S.length,_=s==1?uu(_,M,sf,cf):uu(_,M,{},lf),S.splice(M,0,_),ta(S[M],M)}n.addSeries=za;function _l(_){if(S.splice(_,1),ie){we.values.splice(_,1),ft.splice(_,1);let M=Fe.splice(_,1)[0];E(null,M.firstChild),M.remove()}ue&&(xe.splice(_,1),En.splice(_,1)[0].remove(),Jn.splice(_,1),wi.splice(_,1)),cn("delSeries",_)}n.delSeries=_l;const Ti=[!1,!1,!1,!1];function vl(_,M){if(_._show=_.show,_.show){let C=_.side%2,L=w[_.scale];L==null&&(_.scale=C?S[1].scale:A,L=w[_.scale]);let B=L.time;_.size=dt(_.size),_.space=dt(_.space),_.rotate=dt(_.rotate),ss(_.incrs)&&_.incrs.forEach(oe=>{!hs.has(oe)&&hs.set(oe,gp(oe))}),_.incrs=dt(_.incrs||(L.distr==2?gS:B?p==1?vS:MS:Cs)),_.splits=dt(_.splits||(B&&L.distr==1?ne:L.distr==3?au:L.distr==4?zS:BS)),_.stroke=dt(_.stroke),_.grid.stroke=dt(_.grid.stroke),_.ticks.stroke=dt(_.ticks.stroke),_.border.stroke=dt(_.border.stroke);let $=_.values;_.values=ss($)&&!ss($[0])?dt($):B?ss($)?Qd(Q,Jd($,Y)):$d($)?ES(Q,$):$||ge:$||OS,_.filter=dt(_.filter||(L.distr>=3&&L.log==10?VS:L.distr==3&&L.log==2?GS:pp)),_.font=mf(_.font),_.labelFont=mf(_.labelFont),_._size=_.size(n,null,M,0),_._space=_._rotate=_._incrs=_._found=_._splits=_._values=null,_._size>0&&(Ti[M]=!0,_._el=Xn(TM,d))}}function T(_,M,C,L){let[B,$,oe,pe]=C,Se=M%2,Le=0;return Se==0&&(pe||$)&&(Le=M==0&&!B||M==2&&!oe?Qt(nf.size/3):0),Se==1&&(B||oe)&&(Le=M==1&&!$||M==3&&!pe?Qt(af.size/2):0),Le}const V=n.padding=(i.padding||[T,T,T,T]).map(_=>dt(vt(_,T))),Z=n._padding=V.map((_,M)=>_(n,M,Ti,0));let q,H=null,he=null;const Re=s==1?S[0].idxs:null;let Pe=null,Ie=!1;function Je(_,M){if(e=_??[],n.data=n._data=e,s==2){q=0;for(let C=1;C<S.length;C++)q+=e[C][0].length}else{e.length==0&&(n.data=n._data=e=[[]]),Pe=e[0],q=Pe.length;let C=e;if(j==2){C=e.slice();let L=C[0]=Array(q);for(let B=0;B<q;B++)L[B]=B}n._data=e=C}if(Ws(!0),cn("setData"),j==2&&(I=!0),M!==!1){let C=R;C.auto(n,Ie)?Qe():Yi(A,C.min,C.max),ae=ae||ye.left>=0,re=!0,Xs()}}n.setData=Je;function Qe(){Ie=!0;let _,M;s==1&&(q>0?(H=Re[0]=0,he=Re[1]=q-1,_=e[0][H],M=e[0][he],j==2?(_=H,M=he):_==M&&(j==3?[_,M]=ll(_,_,R.log,!1):j==4?[_,M]=Uu(_,_,R.log,!1):R.time?M=_+Qt(86400/p):[_,M]=Zo(_,M,Nu,!0))):(H=Re[0]=_=null,he=Re[1]=M=null)),Yi(A,_,M)}let Be,ct,Rt,Pt,pn,pt,Ve,Yt,mt,Lt;function Ai(_,M,C,L,B,$){_??(_=Ld),C??(C=Ou),L??(L="butt"),B??(B=Ld),$??($="round"),_!=Be&&(h.strokeStyle=Be=_),B!=ct&&(h.fillStyle=ct=B),M!=Rt&&(h.lineWidth=Rt=M),$!=pn&&(h.lineJoin=pn=$),L!=pt&&(h.lineCap=pt=L),C!=Pt&&h.setLineDash(Pt=C)}function vn(_,M,C,L){M!=ct&&(h.fillStyle=ct=M),_!=Ve&&(h.font=Ve=_),C!=Yt&&(h.textAlign=Yt=C),L!=mt&&(h.textBaseline=mt=L)}function gs(_,M,C,L,B=0){if(L.length>0&&_.auto(n,Ie)&&(M==null||M.min==null)){let $=vt(H,0),oe=vt(he,L.length-1),pe=C.min==null?VM(L,$,oe,B,_.distr==3):[C.min,C.max];_.min=li(_.min,C.min=pe[0]),_.max=Pn(_.max,C.max=pe[1])}}const Vt={min:null,max:null};function fi(){for(let L in w){let B=w[L];X[L]==null&&(B.min==null||X[A]!=null&&B.auto(n,Ie))&&(X[L]=Vt)}for(let L in w){let B=w[L];X[L]==null&&B.from!=null&&X[B.from]!=null&&(X[L]=Vt)}X[A]!=null&&Ws(!0);let _={};for(let L in X){let B=X[L];if(B!=null){let $=_[L]=Yr(w[L],ZM);if(B.min!=null)Kt($,B);else if(L!=A||s==2)if(q==0&&$.from==null){let oe=$.range(n,null,null,L);$.min=oe[0],$.max=oe[1]}else $.min=At,$.max=-At}}if(q>0){S.forEach((L,B)=>{if(s==1){let $=L.scale,oe=X[$];if(oe==null)return;let pe=_[$];if(B==0){let Se=pe.range(n,pe.min,pe.max,$);pe.min=Se[0],pe.max=Se[1],H=ri(pe.min,e[0]),he=ri(pe.max,e[0]),he-H>1&&(e[0][H]<pe.min&&H++,e[0][he]>pe.max&&he--),L.min=Pe[H],L.max=Pe[he]}else L.show&&L.auto&&gs(pe,oe,L,e[B],L.sorted);L.idxs[0]=H,L.idxs[1]=he}else if(B>0&&L.show&&L.auto){let[$,oe]=L.facets,pe=$.scale,Se=oe.scale,[Le,De]=e[B],Ne=_[pe],tt=_[Se];Ne!=null&&gs(Ne,X[pe],$,Le,$.sorted),tt!=null&&gs(tt,X[Se],oe,De,oe.sorted),L.min=oe.min,L.max=oe.max}});for(let L in _){let B=_[L],$=X[L];if(B.from==null&&($==null||$.min==null)){let oe=B.range(n,B.min==At?null:B.min,B.max==-At?null:B.max,L);B.min=oe[0],B.max=oe[1]}}}for(let L in _){let B=_[L];if(B.from!=null){let $=_[B.from];if($.min==null)B.min=B.max=null;else{let oe=B.range(n,$.min,$.max,L);B.min=oe[0],B.max=oe[1]}}}let M={},C=!1;for(let L in _){let B=_[L],$=w[L];if($.min!=B.min||$.max!=B.max){$.min=B.min,$.max=B.max;let oe=$.distr;$._min=oe==3?Hi($.min):oe==4?uc($.min,$.asinh):oe==100?$.fwd($.min):$.min,$._max=oe==3?Hi($.max):oe==4?uc($.max,$.asinh):oe==100?$.fwd($.max):$.max,M[L]=C=!0}}if(C){S.forEach((L,B)=>{s==2?B>0&&M.y&&(L._paths=null):M[L.scale]&&(L._paths=null)});for(let L in M)I=!0,cn("setScale",L);ue&&ye.left>=0&&(ae=re=!0)}for(let L in X)X[L]=null}function na(_){let M=ru(H-1,0,q-1),C=ru(he+1,0,q-1);for(;_[M]==null&&M>0;)M--;for(;_[C]==null&&C<q-1;)C++;return[M,C]}function Dn(){if(q>0){let _=S.some(M=>M._focus)&&Lt!=an.alpha;_&&(h.globalAlpha=Lt=an.alpha),S.forEach((M,C)=>{if(C>0&&M.show&&(Gs(C,!1),Gs(C,!0),M._paths==null)){let L=Lt;Lt!=M.alpha&&(h.globalAlpha=Lt=M.alpha);let B=s==2?[0,e[C][0].length-1]:na(e[C]);M._paths=M.paths(n,C,B[0],B[1]),Lt!=L&&(h.globalAlpha=Lt=L)}}),S.forEach((M,C)=>{if(C>0&&M.show){let L=Lt;Lt!=M.alpha&&(h.globalAlpha=Lt=M.alpha),M._paths!=null&&ka(C,!1);{let B=M._paths!=null?M._paths.gaps:null,$=M.points.show(n,C,H,he,B),oe=M.points.filter(n,C,$,B);($||oe)&&(M.points._paths=M.points.paths(n,C,H,he,oe),ka(C,!0))}Lt!=L&&(h.globalAlpha=Lt=L),cn("drawSeries",C)}}),_&&(h.globalAlpha=Lt=1)}}function Gs(_,M){let C=M?S[_].points:S[_];C._stroke=C.stroke(n,_),C._fill=C.fill(n,_)}function ka(_,M){let C=M?S[_].points:S[_],{stroke:L,fill:B,clip:$,flags:oe,_stroke:pe=C._stroke,_fill:Se=C._fill,_width:Le=C.width}=C._paths;Le=Ct(Le*yt,3);let De=null,Ne=Le%2/2;M&&Se==null&&(Se=Le>0?"#fff":pe);let tt=C.pxAlign==1&&Ne>0;if(tt&&h.translate(Ne,Ne),!M){let xt=Ze-Le/2,_t=ke-Le/2,ut=be+Le,et=He+Le;De=new Path2D,De.rect(xt,_t,ut,et)}M?xl(pe,Le,C.dash,C.cap,Se,L,B,oe,$):Ha(_,pe,Le,C.dash,C.cap,Se,L,B,oe,De,$),tt&&h.translate(-Ne,-Ne)}function Ha(_,M,C,L,B,$,oe,pe,Se,Le,De){let Ne=!1;Se!=0&&O.forEach((tt,xt)=>{if(tt.series[0]==_){let _t=S[tt.series[1]],ut=e[tt.series[1]],et=(_t._paths||Ta).band;ss(et)&&(et=tt.dir==1?et[0]:et[1]);let We,Ut=null;_t.show&&et&&WM(ut,H,he)?(Ut=tt.fill(n,xt)||$,We=_t._paths.clip):et=null,xl(M,C,L,B,Ut,oe,pe,Se,Le,De,We,et),Ne=!0}}),Ne||xl(M,C,L,B,$,oe,pe,Se,Le,De)}const Ku=$r|lu;function xl(_,M,C,L,B,$,oe,pe,Se,Le,De,Ne){Ai(_,M,C,L,B),(Se||Le||Ne)&&(h.save(),Se&&h.clip(Se),Le&&h.clip(Le)),Ne?(pe&Ku)==Ku?(h.clip(Ne),De&&h.clip(De),Ga(B,oe),Va(_,$,M)):pe&lu?(Ga(B,oe),h.clip(Ne),Va(_,$,M)):pe&$r&&(h.save(),h.clip(Ne),De&&h.clip(De),Ga(B,oe),h.restore(),Va(_,$,M)):(Ga(B,oe),Va(_,$,M)),(Se||Le||Ne)&&h.restore()}function Va(_,M,C){C>0&&(M instanceof Map?M.forEach((L,B)=>{h.strokeStyle=Be=B,h.stroke(L)}):M!=null&&_&&h.stroke(M))}function Ga(_,M){M instanceof Map?M.forEach((C,L)=>{h.fillStyle=ct=L,h.fill(C)}):M!=null&&_&&h.fill(M)}function em(_,M,C,L){let B=y[_],$;if(L<=0)$=[0,0];else{let oe=B._space=B.space(n,_,M,C,L),pe=B._incrs=B.incrs(n,_,M,C,L,oe);$=hb(M,C,pe,L,oe)}return B._found=$}function yl(_,M,C,L,B,$,oe,pe,Se,Le){let De=oe%2/2;v==1&&h.translate(De,De),Ai(pe,oe,Se,Le,pe),h.beginPath();let Ne,tt,xt,_t,ut=B+(L==0||L==3?-$:$);C==0?(tt=B,_t=ut):(Ne=B,xt=ut);for(let et=0;et<_.length;et++)M[et]!=null&&(C==0?Ne=xt=_[et]:tt=_t=_[et],h.moveTo(Ne,tt),h.lineTo(xt,_t));h.stroke(),v==1&&h.translate(-De,-De)}function tm(_){let M=!0;return y.forEach((C,L)=>{if(!C.show)return;let B=w[C.scale];if(B.min==null){C._show&&(M=!1,C._show=!1,Ws(!1));return}else C._show||(M=!1,C._show=!0,Ws(!1));let $=C.side,oe=$%2,{min:pe,max:Se}=B,[Le,De]=em(L,pe,Se,oe==0?ee:W);if(De==0)return;let Ne=B.distr==2,tt=C._splits=C.splits(n,L,pe,Se,Le,De,Ne),xt=B.distr==2?tt.map(We=>Pe[We]):tt,_t=B.distr==2?Pe[tt[1]]-Pe[tt[0]]:Le,ut=C._values=C.values(n,C.filter(n,xt,L,De,_t),L,De,_t);C._rotate=$==2?C.rotate(n,ut,L,De):0;let et=C._size;C._size=Yn(C.size(n,ut,L,_)),et!=null&&C._size!=et&&(M=!1)}),M}function nm(_){let M=!0;return V.forEach((C,L)=>{let B=C(n,L,Ti,_);B!=Z[L]&&(M=!1),Z[L]=B}),M}function im(){for(let _=0;_<y.length;_++){let M=y[_];if(!M.show||!M._show)continue;let C=M.side,L=C%2,B,$,oe=M.stroke(n,_),pe=C==0||C==3?-1:1,[Se,Le]=M._found;if(M.label!=null){let Tn=M.labelGap*pe,Fn=Qt((M._lpos+Tn)*yt);vn(M.labelFont[0],oe,"center",C==2?_a:Pd),h.save(),L==1?(B=$=0,h.translate(Fn,Qt(ke+He/2)),h.rotate((C==3?-Bo:Bo)/2)):(B=Qt(Ze+be/2),$=Fn);let xs=dp(M.label)?M.label(n,_,Se,Le):M.label;h.fillText(xs,B,$),h.restore()}if(Le==0)continue;let De=w[M.scale],Ne=L==0?be:He,tt=L==0?Ze:ke,xt=M._splits,_t=De.distr==2?xt.map(Tn=>Pe[Tn]):xt,ut=De.distr==2?Pe[xt[1]]-Pe[xt[0]]:Se,et=M.ticks,We=M.border,Ut=et.show?et.size:0,Gt=Qt(Ut*yt),un=Qt((M.alignTo==2?M._size-Ut-M.gap:M.gap)*yt),Tt=M._rotate*-Bo/180,Wt=m(M._pos*yt),Un=(Gt+un)*pe,wn=Wt+Un;$=L==0?wn:0,B=L==1?wn:0;let Vn=M.font[0],Qn=M.align==1?Sr:M.align==2?oc:Tt>0?Sr:Tt<0?oc:L==0?"center":C==3?oc:Sr,gi=Tt||L==1?"middle":C==2?_a:Pd;vn(Vn,oe,Qn,gi);let Nn=M.font[1]*M.lineGap,Gn=xt.map(Tn=>m(o(Tn,De,Ne,tt))),ei=M._values;for(let Tn=0;Tn<ei.length;Tn++){let Fn=ei[Tn];if(Fn!=null){L==0?B=Gn[Tn]:$=Gn[Tn],Fn=""+Fn;let xs=Fn.indexOf(`
`)==-1?[Fn]:Fn.split(/\n/gm);for(let An=0;An<xs.length;An++){let mh=xs[An];Tt?(h.save(),h.translate(B,$+An*Nn),h.rotate(Tt),h.fillText(mh,0,0),h.restore()):h.fillText(mh,B,$+An*Nn)}}}et.show&&yl(Gn,et.filter(n,_t,_,Le,ut),L,C,Wt,Gt,Ct(et.width*yt,3),et.stroke(n,_),et.dash,et.cap);let _i=M.grid;_i.show&&yl(Gn,_i.filter(n,_t,_,Le,ut),L,L==0?2:1,L==0?ke:Ze,L==0?He:be,Ct(_i.width*yt,3),_i.stroke(n,_),_i.dash,_i.cap),We.show&&yl([Wt],[1],L==0?1:0,L==0?1:2,L==1?ke:Ze,L==1?He:be,Ct(We.width*yt,3),We.stroke(n,_),We.dash,We.cap)}cn("drawAxes")}function Ws(_){S.forEach((M,C)=>{C>0&&(M._paths=null,_&&(s==1?(M.min=null,M.max=null):M.facets.forEach(L=>{L.min=null,L.max=null})))})}let Wa=!1,Ml=!1,ia=[];function sm(){Ml=!1;for(let _=0;_<ia.length;_++)cn(...ia[_]);ia.length=0}function Xs(){Wa||(sS(Zu),Wa=!0)}function rm(_,M=!1){Wa=!0,Ml=M,_(n),Zu(),M&&ia.length>0&&queueMicrotask(sm)}n.batch=rm;function Zu(){if(F&&(fi(),F=!1),I&&(gt(),I=!1),ce){if(Nt(f,Sr,Ee),Nt(f,_a,_e),Nt(f,Ma,ee),Nt(f,Sa,W),Nt(g,Sr,Ee),Nt(g,_a,_e),Nt(g,Ma,ee),Nt(g,Sa,W),Nt(d,Ma,J),Nt(d,Sa,le),u.width=Qt(J*yt),u.height=Qt(le*yt),y.forEach(({_el:_,_show:M,_size:C,_pos:L,side:B})=>{if(_!=null)if(M){let $=B===3||B===0?C:0,oe=B%2==1;Nt(_,oe?"left":"top",L-$),Nt(_,oe?"width":"height",C),Nt(_,oe?"top":"left",oe?_e:Ee),Nt(_,oe?"height":"width",oe?W:ee),iu(_,Ls)}else zn(_,Ls)}),Be=ct=Rt=pn=pt=Ve=Yt=mt=Pt=null,Lt=1,aa(!0),Ee!=Ae||_e!=Ke||ee!=me||W!=Te){Ws(!1);let _=ee/me,M=W/Te;if(ue&&!ae&&ye.left>=0){ye.left*=_,ye.top*=M,qs&&vi(qs,Qt(ye.left),0,ee,W),Ys&&vi(Ys,0,Qt(ye.top),ee,W);for(let C=0;C<En.length;C++){let L=En[C];L!=null&&(Jn[C]*=_,wi[C]*=M,vi(L,Yn(Jn[C]),Yn(wi[C]),ee,W))}}if(It.show&&!se&&It.left>=0&&It.width>0){It.left*=_,It.width*=_,It.top*=M,It.height*=M;for(let C in Al)Nt(Ks,C,It[C])}Ae=Ee,Ke=_e,me=ee,Te=W}cn("setSize"),ce=!1}J>0&&le>0&&(h.clearRect(0,0,u.width,u.height),cn("drawClear"),N.forEach(_=>_()),cn("draw")),It.show&&se&&(Xa(It),se=!1),ue&&ae&&(vs(null,!0,!1),ae=!1),we.show&&we.live&&re&&(wl(),re=!1),l||(l=!0,n.status=1,cn("ready")),Ie=!1,Wa=!1}n.redraw=(_,M)=>{I=M||!1,_!==!1?Yi(A,R.min,R.max):Xs()};function Sl(_,M){let C=w[_];if(C.from==null){if(q==0){let L=C.range(n,M.min,M.max,_);M.min=L[0],M.max=L[1]}if(M.min>M.max){let L=M.min;M.min=M.max,M.max=L}if(q>1&&M.min!=null&&M.max!=null&&M.max-M.min<1e-16)return;_==A&&C.distr==2&&q>0&&(M.min=ri(M.min,e[0]),M.max=ri(M.max,e[0]),M.min==M.max&&M.max++),X[_]=M,F=!0,Xs()}}n.setScale=Sl;let bl,El,qs,Ys,Ju,Qu,$s,js,eh,th,Dt,kt,qi=!1;const mn=ye.drag;let on=mn.x,ln=mn.y;ue&&(ye.x&&(bl=Xn(CM,g)),ye.y&&(El=Xn(RM,g)),R.ori==0?(qs=bl,Ys=El):(qs=El,Ys=bl),Dt=ye.left,kt=ye.top);const It=n.select=Kt({show:!0,over:!0,left:0,width:0,top:0,height:0},i.select),Ks=It.show?Xn(AM,It.over?g:f):null;function Xa(_,M){if(It.show){for(let C in _)It[C]=_[C],C in Al&&Nt(Ks,C,_[C]);M!==!1&&cn("setSelect")}}n.setSelect=Xa;function am(_){if(S[_].show)ie&&iu(Fe[_],Ls);else if(ie&&zn(Fe[_],Ls),ue){let C=Ei?En[0]:En[_];C!=null&&vi(C,-10,-10,ee,W)}}function Yi(_,M,C){Sl(_,{min:M,max:C})}function pi(_,M,C,L){M.focus!=null&&hm(_),M.show!=null&&S.forEach((B,$)=>{$>0&&(_==$||_==null)&&(B.show=M.show,am($),s==2?(Yi(B.facets[0].scale,null,null),Yi(B.facets[1].scale,null,null)):Yi(B.scale,null,null),Xs())}),C!==!1&&cn("setSeries",_,M),L&&oa("setSeries",n,_,M)}n.setSeries=pi;function om(_,M){Kt(O[_],M)}function lm(_,M){_.fill=dt(_.fill||null),_.dir=vt(_.dir,-1),M=M??O.length,O.splice(M,0,_)}function cm(_){_==null?O.length=0:O.splice(_,1)}n.addBand=lm,n.setBand=om,n.delBand=cm;function um(_,M){S[_].alpha=M,ue&&En[_]!=null&&(En[_].style.opacity=M),ie&&Fe[_]&&(Fe[_].style.opacity=M)}let Ci,$i,_s;const Zs={focus:!0};function hm(_){if(_!=_s){let M=_==null,C=an.alpha!=1;S.forEach((L,B)=>{if(s==1||B>0){let $=M||B==0||B==_;L._focus=M?null:$,C&&um(B,$?1:an.alpha)}}),_s=_,C&&Xs()}}ie&&di&&D(Ud,fe,_=>{ye._lock||(Bt(_),_s!=null&&pi(null,Zs,!0,$t.setSeries))});function mi(_,M,C){let L=w[M];C&&(_=_/yt-(L.ori==1?_e:Ee));let B=ee;L.ori==1&&(B=W,_=B-_),L.dir==-1&&(_=B-_);let $=L._min,oe=L._max,pe=_/B,Se=$+(oe-$)*pe,Le=L.distr;return Le==3?Xr(10,Se):Le==4?qM(Se,L.asinh):Le==100?L.bwd(Se):Se}function dm(_,M){let C=mi(_,A,M);return ri(C,e[0],H,he)}n.valToIdx=_=>ri(_,e[0]),n.posToIdx=dm,n.posToVal=mi,n.valToPos=(_,M,C)=>w[M].ori==0?r(_,w[M],C?be:ee,C?Ze:0):a(_,w[M],C?He:W,C?ke:0),n.setCursor=(_,M,C)=>{Dt=_.left,kt=_.top,vs(null,M,C)};function nh(_,M){Nt(Ks,Sr,It.left=_),Nt(Ks,Ma,It.width=M)}function ih(_,M){Nt(Ks,_a,It.top=_),Nt(Ks,Sa,It.height=M)}let sa=R.ori==0?nh:ih,ra=R.ori==1?nh:ih;function fm(){if(ie&&we.live)for(let _=s==2?1:0;_<S.length;_++){if(_==0&&ht)continue;let M=we.values[_],C=0;for(let L in M)ft[_][C++].firstChild.nodeValue=M[L]}}function wl(_,M){if(_!=null&&(_.idxs?_.idxs.forEach((C,L)=>{xe[L]=C}):KM(_.idx)||xe.fill(_.idx),we.idx=xe[0]),ie&&we.live){for(let C=0;C<S.length;C++)(C>0||s==1&&!ht)&&pm(C,xe[C]);fm()}re=!1,M!==!1&&cn("setLegend")}n.setLegend=wl;function pm(_,M){let C=S[_],L=_==0&&j==2?Pe:e[_],B;ht?B=C.values(n,_,M)??it:(B=C.value(n,M==null?null:L[M],_,M),B=B==null?it:{_:B}),we.values[_]=B}function vs(_,M,C){eh=Dt,th=kt,[Dt,kt]=ye.move(n,Dt,kt),ye.left=Dt,ye.top=kt,ue&&(qs&&vi(qs,Qt(Dt),0,ee,W),Ys&&vi(Ys,0,Qt(kt),ee,W));let L,B=H>he;Ci=At,$i=null;let $=R.ori==0?ee:W,oe=R.ori==1?ee:W;if(Dt<0||q==0||B){L=ye.idx=null;for(let pe=0;pe<S.length;pe++){let Se=En[pe];Se!=null&&vi(Se,-10,-10,ee,W)}di&&pi(null,Zs,!0,_==null&&$t.setSeries),we.live&&(xe.fill(L),re=!0)}else{let pe,Se,Le;s==1&&(pe=R.ori==0?Dt:kt,Se=mi(pe,A),L=ye.idx=ri(Se,e[0],H,he),Le=z(e[0][L],R,$,0));let De=-10,Ne=-10,tt=0,xt=0,_t=!0,ut="",et="";for(let We=s==2?1:0;We<S.length;We++){let Ut=S[We],Gt=xe[We],un=Gt==null?null:s==1?e[We][Gt]:e[We][1][Gt],Tt=ye.dataIdx(n,We,L,Se),Wt=Tt==null?null:s==1?e[We][Tt]:e[We][1][Tt];if(re=re||Wt!=un||Tt!=Gt,xe[We]=Tt,We>0&&Ut.show){let Un=Tt==null?-10:Tt==L?Le:z(s==1?e[0][Tt]:e[We][0][Tt],R,$,0),wn=Wt==null?-10:K(Wt,s==1?w[Ut.scale]:w[Ut.facets[1].scale],oe,0);if(di&&Wt!=null){let Vn=R.ori==1?Dt:kt,Qn=en(an.dist(n,We,Tt,wn,Vn));if(Qn<Ci){let gi=an.bias;if(gi!=0){let Nn=mi(Vn,Ut.scale),Gn=Wt>=0?1:-1,ei=Nn>=0?1:-1;ei==Gn&&(ei==1?gi==1?Wt>=Nn:Wt<=Nn:gi==1?Wt<=Nn:Wt>=Nn)&&(Ci=Qn,$i=We)}else Ci=Qn,$i=We}}if(re||Ei){let Vn,Qn;R.ori==0?(Vn=Un,Qn=wn):(Vn=wn,Qn=Un);let gi,Nn,Gn,ei,_i,Tn,Fn=!0,xs=zt.bbox;if(xs!=null){Fn=!1;let An=xs(n,We);Gn=An.left,ei=An.top,gi=An.width,Nn=An.height}else Gn=Vn,ei=Qn,gi=Nn=zt.size(n,We);if(Tn=zt.fill(n,We),_i=zt.stroke(n,We),Ei)We==$i&&Ci<=an.prox&&(De=Gn,Ne=ei,tt=gi,xt=Nn,_t=Fn,ut=Tn,et=_i);else{let An=En[We];An!=null&&(Jn[We]=Gn,wi[We]=ei,Hd(An,gi,Nn,Fn),zd(An,Tn,_i),vi(An,Yn(Gn),Yn(ei),ee,W))}}}}if(Ei){let We=an.prox,Ut=_s==null?Ci<=We:Ci>We||$i!=_s;if(re||Ut){let Gt=En[0];Gt!=null&&(Jn[0]=De,wi[0]=Ne,Hd(Gt,tt,xt,_t),zd(Gt,ut,et),vi(Gt,Yn(De),Yn(Ne),ee,W))}}}if(It.show&&qi)if(_!=null){let[pe,Se]=$t.scales,[Le,De]=$t.match,[Ne,tt]=_.cursor.sync.scales,xt=_.cursor.drag;if(on=xt._x,ln=xt._y,on||ln){let{left:_t,top:ut,width:et,height:We}=_.select,Ut=_.scales[Ne].ori,Gt=_.posToVal,un,Tt,Wt,Un,wn,Vn=pe!=null&&Le(pe,Ne),Qn=Se!=null&&De(Se,tt);Vn&&on?(Ut==0?(un=_t,Tt=et):(un=ut,Tt=We),Wt=w[pe],Un=z(Gt(un,Ne),Wt,$,0),wn=z(Gt(un+Tt,Ne),Wt,$,0),sa(li(Un,wn),en(wn-Un))):sa(0,$),Qn&&ln?(Ut==1?(un=_t,Tt=et):(un=ut,Tt=We),Wt=w[Se],Un=K(Gt(un,tt),Wt,oe,0),wn=K(Gt(un+Tt,tt),Wt,oe,0),ra(li(Un,wn),en(wn-Un))):ra(0,oe)}else Cl()}else{let pe=en(eh-Ju),Se=en(th-Qu);if(R.ori==1){let tt=pe;pe=Se,Se=tt}on=mn.x&&pe>=mn.dist,ln=mn.y&&Se>=mn.dist;let Le=mn.uni;Le!=null?on&&ln&&(on=pe>=Le,ln=Se>=Le,!on&&!ln&&(Se>pe?ln=!0:on=!0)):mn.x&&mn.y&&(on||ln)&&(on=ln=!0);let De,Ne;on&&(R.ori==0?(De=$s,Ne=Dt):(De=js,Ne=kt),sa(li(De,Ne),en(Ne-De)),ln||ra(0,oe)),ln&&(R.ori==1?(De=$s,Ne=Dt):(De=js,Ne=kt),ra(li(De,Ne),en(Ne-De)),on||sa(0,$)),!on&&!ln&&(sa(0,0),ra(0,0))}if(mn._x=on,mn._y=ln,_==null){if(C){if(ph!=null){let[pe,Se]=$t.scales;$t.values[0]=pe!=null?mi(R.ori==0?Dt:kt,pe):null,$t.values[1]=Se!=null?mi(R.ori==1?Dt:kt,Se):null}oa(lc,n,Dt,kt,ee,W,L)}if(di){let pe=C&&$t.setSeries,Se=an.prox;_s==null?Ci<=Se&&pi($i,Zs,!0,pe):Ci>Se?pi(null,Zs,!0,pe):$i!=_s&&pi($i,Zs,!0,pe)}}re&&(we.idx=L,wl()),M!==!1&&cn("setCursor")}let ji=null;Object.defineProperty(n,"rect",{get(){return ji==null&&aa(!1),ji}});function aa(_=!1){_?ji=null:(ji=g.getBoundingClientRect(),cn("syncRect",ji))}function sh(_,M,C,L,B,$,oe){ye._lock||qi&&_!=null&&_.movementX==0&&_.movementY==0||(Tl(_,M,C,L,B,$,oe,!1,_!=null),_!=null?vs(null,!0,!0):vs(M,!0,!1))}function Tl(_,M,C,L,B,$,oe,pe,Se){if(ji==null&&aa(!1),Bt(_),_!=null)C=_.clientX-ji.left,L=_.clientY-ji.top;else{if(C<0||L<0){Dt=-10,kt=-10;return}let[Le,De]=$t.scales,Ne=M.cursor.sync,[tt,xt]=Ne.values,[_t,ut]=Ne.scales,[et,We]=$t.match,Ut=M.axes[0].side%2==1,Gt=R.ori==0?ee:W,un=R.ori==1?ee:W,Tt=Ut?$:B,Wt=Ut?B:$,Un=Ut?L:C,wn=Ut?C:L;if(_t!=null?C=et(Le,_t)?o(tt,w[Le],Gt,0):-10:C=Gt*(Un/Tt),ut!=null?L=We(De,ut)?o(xt,w[De],un,0):-10:L=un*(wn/Wt),R.ori==1){let Vn=C;C=L,L=Vn}}Se&&(M==null||M.cursor.event.type==lc)&&((C<=1||C>=ee-1)&&(C=As(C,ee)),(L<=1||L>=W-1)&&(L=As(L,W))),pe?(Ju=C,Qu=L,[$s,js]=ye.move(n,C,L)):(Dt=C,kt=L)}const Al={width:0,height:0,left:0,top:0};function Cl(){Xa(Al,!1)}let rh,ah,oh,lh;function ch(_,M,C,L,B,$,oe){qi=!0,on=ln=mn._x=mn._y=!1,Tl(_,M,C,L,B,$,oe,!0,!1),_!=null&&(D(cc,tu,uh,!1),oa(Dd,n,$s,js,ee,W,null));let{left:pe,top:Se,width:Le,height:De}=It;rh=pe,ah=Se,oh=Le,lh=De}function uh(_,M,C,L,B,$,oe){qi=mn._x=mn._y=!1,Tl(_,M,C,L,B,$,oe,!1,!0);let{left:pe,top:Se,width:Le,height:De}=It,Ne=Le>0||De>0,tt=rh!=pe||ah!=Se||oh!=Le||lh!=De;if(Ne&&tt&&Xa(It),mn.setScale&&Ne&&tt){let xt=pe,_t=Le,ut=Se,et=De;if(R.ori==1&&(xt=Se,_t=De,ut=pe,et=Le),on&&Yi(A,mi(xt,A),mi(xt+_t,A)),ln)for(let We in w){let Ut=w[We];We!=A&&Ut.from==null&&Ut.min!=At&&Yi(We,mi(ut+et,We),mi(ut,We))}Cl()}else ye.lock&&(ye._lock=!ye._lock,vs(M,!0,_!=null));_!=null&&(E(cc,tu),oa(cc,n,Dt,kt,ee,W,null))}function mm(_,M,C,L,B,$,oe){if(ye._lock)return;Bt(_);let pe=qi;if(qi){let Se=!0,Le=!0,De=10,Ne,tt;R.ori==0?(Ne=on,tt=ln):(Ne=ln,tt=on),Ne&&tt&&(Se=Dt<=De||Dt>=ee-De,Le=kt<=De||kt>=W-De),Ne&&Se&&(Dt=Dt<$s?0:ee),tt&&Le&&(kt=kt<js?0:W),vs(null,!0,!0),qi=!1}Dt=-10,kt=-10,xe.fill(null),vs(null,!0,!0),pe&&(qi=pe)}function hh(_,M,C,L,B,$,oe){ye._lock||(Bt(_),Qe(),Cl(),_!=null&&oa(Nd,n,Dt,kt,ee,W,null))}function dh(){y.forEach(db),ve(n.width,n.height,!0)}Fs(Ko,Fr,dh);const Js={};Js.mousedown=ch,Js.mousemove=sh,Js.mouseup=uh,Js.dblclick=hh,Js.setSeries=(_,M,C,L)=>{let B=$t.match[2];C=B(n,M,C),C!=-1&&pi(C,L,!0,!1)},ue&&(D(Dd,g,ch),D(lc,g,sh),D(Id,g,_=>{Bt(_),aa(!1)}),D(Ud,g,mm),D(Nd,g,hh),cu.add(n),n.syncRect=aa);const qa=n.hooks=i.hooks||{};function cn(_,M,C){Ml?ia.push([_,M,C]):_ in qa&&qa[_].forEach(L=>{L.call(null,n,M,C)})}(i.plugins||[]).forEach(_=>{for(let M in _.hooks)qa[M]=(qa[M]||[]).concat(_.hooks[M])});const fh=(_,M,C)=>C,$t=Kt({key:null,setSeries:!1,filters:{pub:qd,sub:qd},scales:[A,S[1]?S[1].scale:null],match:[Yd,Yd,fh],values:[null,null]},ye.sync);$t.match.length==2&&$t.match.push(fh),ye.sync=$t;const ph=$t.key,Rl=Fp(ph);function oa(_,M,C,L,B,$,oe){$t.filters.pub(_,M,C,L,B,$,oe)&&Rl.pub(_,M,C,L,B,$,oe)}Rl.sub(n);function gm(_,M,C,L,B,$,oe){$t.filters.sub(_,M,C,L,B,$,oe)&&Js[_](null,M,C,L,B,$,oe)}n.pub=gm;function _m(){Rl.unsub(n),cu.delete(n),Xe.clear(),su(Ko,Fr,dh),c.remove(),fe==null||fe.remove(),cn("destroy")}n.destroy=_m;function Pl(){cn("init",i,e),Je(e||i.data,!1),X[A]?Sl(A,X[A]):Qe(),se=It.show&&(It.width>0||It.height>0),ae=re=!0,ve(i.width,i.height)}return S.forEach(ta),y.forEach(vl),t?t instanceof HTMLElement?(t.appendChild(c),Pl()):t(n,Pl):Pl(),n}dn.assign=Kt;dn.fmtNum=Fu;dn.rangeNum=Zo;dn.rangeLog=ll;dn.rangeAsinh=Uu;dn.orient=Vs;dn.pxRatio=yt;dn.join=iS;dn.fmtDate=Bu,dn.tzDate=pS;dn.sync=Fp;{dn.addGap=KS,dn.clipGaps=hl;let i=dn.paths={points:Vp};i.linear=Wp,i.stepped=QS,i.bars=eb,i.spline=nb}function pc(i){return Math.max(120,i.clientHeight-30)}class fb{constructor(){G(this,"name","Plotter");G(this,"container",null);G(this,"tabsContainer",null);G(this,"contentContainer",null);G(this,"tooltip",null);G(this,"paretoPlot",null);G(this,"ablationPlot",null);G(this,"variabilityPlot",null);G(this,"currentTab","pareto");G(this,"records",[]);G(this,"ablationGroups",[]);G(this,"paretoFlags",[]);G(this,"chance",.1);G(this,"paretoRecordIndices",[]);G(this,"paretoXData",[]);G(this,"paretoYData",[]);G(this,"categoryLabels",[]);G(this,"ablationFixedAxes","");G(this,"onCampaignMetrics",e=>{const{data:t}=e;t!=null&&t.records&&qn.observe(e==null?void 0:e.campaign_id,t)});G(this,"onRunChanged",(e,t)=>{t&&(this.records=t.records??[],this.paretoFlags=t.pareto??[],this.ablationGroups=t.ablation_groups??[],typeof t.chance=="number"&&(this.chance=t.chance),this.updatePlots(),this.updateStatus())});Zt.register("campaign_metrics",this.onCampaignMetrics),qn.onChange(this.onRunChanged)}async init(){this.createUI(),console.log("[Plotter] Initialized")}async destroy(){var e,t,n,s;Zt.unregister("campaign_metrics",this.onCampaignMetrics),(e=this.paretoPlot)==null||e.destroy(),(t=this.ablationPlot)==null||t.destroy(),(n=this.variabilityPlot)==null||n.destroy(),(s=this.container)==null||s.remove()}createUI(){const e=document.getElementById("ui-overlay");e&&(this.container=document.createElement("div"),this.container.id="plotter",this.container.style.cssText=`
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
    `,this.container.appendChild(this.tooltip),this.tabsContainer.querySelectorAll(".plotter-tab").forEach(t=>{t.addEventListener("click",()=>this.switchTab(t.getAttribute("data-tab")))}),this.container.querySelector("#plotter-download").addEventListener("click",()=>this.downloadCurrent()),this.switchTab(this.currentTab))}showTab(e){e!==this.currentTab&&this.switchTab(e)}switchTab(e){this.currentTab=e,this.tabsContainer.querySelectorAll(".plotter-tab").forEach(n=>{n.classList.toggle("active",n.getAttribute("data-tab")===e)}),Object.entries({pareto:"plotter-pareto",ablation:"plotter-ablation",variability:"plotter-variability"}).forEach(([n,s])=>{const r=document.getElementById(s);r&&(r.style.display=n===e?"block":"none")}),e==="pareto"&&!this.paretoPlot&&this.initParetoPlot(),e==="ablation"&&!this.ablationPlot&&this.initAblationPlot(),e==="variability"&&!this.variabilityPlot&&this.initVariabilityPlot(),this.updatePlots()}updateStatus(){var s;const e=(s=this.container)==null?void 0:s.querySelector("#plotter-status");if(!e)return;const t=`${this.records.length} records | ${this.paretoFlags.filter(r=>r).length} Pareto`,n=this.ablationFixedAxes?` | fixed: ${this.ablationFixedAxes}`:"";e.textContent=t+n,e.title=e.textContent}updatePlots(){this.currentTab==="pareto"&&this.paretoPlot&&this.updateParetoPlot(),this.currentTab==="ablation"&&this.ablationPlot&&this.updateAblationPlot(),this.currentTab==="variability"&&this.variabilityPlot&&this.updateVariabilityPlot()}initParetoPlot(){const e=document.getElementById("plotter-pareto");if(!e)return;const t={width:e.clientWidth,height:pc(e),title:"Pareto Frontier: validation accuracy vs speed",axes:[{label:"1 / walltime_s   (faster →)",grid:{stroke:te.border}},{label:"accuracy",grid:{stroke:te.border},side:1}],scales:{x:{time:!1},y:{time:!1}},series:[{},{label:"val_acc",stroke:te.gradient,width:0,points:{show:!0,size:8,stroke:"white",width:1,fill:(n,s)=>{var o;const r=this.paretoRecordIndices[s],a=r===void 0?void 0:this.records[r];return a&&bn[(o=a.coordinate)==null?void 0:o.credit]||te.gradient}}}],hooks:{draw:[n=>{const s=n.ctx;if(this.paretoFlags.some(a=>a)){const a=[];this.records.forEach((o,l)=>{this.paretoFlags[l]&&o.payload.walltime_s&&o.payload.val_acc&&a.push([1/o.payload.walltime_s,o.payload.val_acc])}),a.sort((o,l)=>o[0]-l[0]),a.length>1&&(s.beginPath(),s.strokeStyle=te.pareto,s.lineWidth=2,s.setLineDash([5,5]),a.forEach((o,l)=>{const c=n.valToPos(o[0],"x"),u=n.valToPos(o[1],"y");l===0?s.moveTo(c,u):s.lineTo(c,u)}),s.stroke(),s.setLineDash([])),a.forEach(o=>{const l=n.valToPos(o[0],"x"),c=n.valToPos(o[1],"y");s.beginPath(),s.arc(l,c,7,0,Math.PI*2),s.strokeStyle=te.pareto,s.lineWidth=1.5,s.stroke()})}const r=n.valToPos(this.chance,"y");s.strokeStyle=te.chance_line,s.lineWidth=1.5,s.setLineDash([4,4]),s.beginPath(),s.moveTo(n.bbox.left,r),s.lineTo(n.bbox.width,r),s.stroke(),s.setLineDash([])}],setCursor:[n=>{this.showScatterTooltip(n)}]},cursor:{show:!0,drag:{setScale:!0},focus:{prox:16}}};this.paretoPlot=new dn(t,[[],[]],e)}recordAt(e){const t=this.paretoRecordIndices[e];return t===void 0?void 0:this.records[t]}updateParetoPlot(){if(!this.paretoPlot||this.records.length===0)return;const e=[],t=[];this.paretoRecordIndices=[],this.records.forEach((r,a)=>{const o=r.payload.walltime_s,l=r.payload.val_acc;this.paretoRecordIndices.push(a),o&&l?(e.push(1/o),t.push(l)):(e.push(NaN),t.push(NaN))}),this.paretoPlot.setData([e,t]),this.paretoXData=e,this.paretoYData=t;const n=e.filter(Number.isFinite),s=t.filter(Number.isFinite);n.length>0&&this.fitScale(this.paretoPlot,"x",Math.min(...n),Math.max(...n)),s.length>0&&this.fitScale(this.paretoPlot,"y",Math.min(Math.min(...s),this.chance),Math.max(...s))}fitScale(e,t,n,s){if(!Number.isFinite(n)||!Number.isFinite(s))return;n===s&&(n-=.01,s+=.01);const r=(s-n)*.05;e.setScale(t,{min:n-r,max:s+r})}initAblationPlot(){const e=document.getElementById("plotter-ablation");if(!e)return;const t={width:e.clientWidth,height:pc(e),title:"Ablation: credit arm → validation accuracy",axes:[{label:"credit arm",splits:()=>this.categoryIndices(),values:(n,s)=>s.map(r=>this.categoryLabels[r]??String(r)),grid:{stroke:te.border}},{label:"accuracy",grid:{stroke:te.border},side:1}],scales:{x:{time:!1},y:{time:!1}},series:[{},{label:"val_acc",width:0,points:{show:!1}}],hooks:{draw:[n=>{if(!this.ablationGroups.length)return;const s=n.ctx,r=this.ablationGroups.find(u=>u.axis==="credit");if(!r)return;const a=r.metrics.find(u=>u.metric==="val_acc");if(!a)return;const o=a.arms,l=n.bbox.width/(o.length*1.5);n.bbox.left,o.forEach((u,h)=>{const d=n.valToPos(h,"x"),f=n.valToPos(0,"y"),g=n.valToPos(u.mean,"y"),v=f-g;if(s.fillStyle=bn[u.value]||te.gradient,s.fillRect(d-l/2,g,l,v),u.std>0){const m=n.valToPos(u.mean+u.std,"y");s.strokeStyle=te.text_muted,s.lineWidth=1,s.beginPath(),s.moveTo(d,m),s.lineTo(d,f),s.stroke(),s.moveTo(d-3,m),s.lineTo(d+3,m),s.stroke()}});const c=n.valToPos(this.chance,"y");s.strokeStyle=te.chance_line,s.lineWidth=2,s.setLineDash([5,5]),s.beginPath(),s.moveTo(n.bbox.left,c),s.lineTo(n.bbox.width,c),s.stroke(),s.setLineDash([])}],setCursor:[n=>{this.showCategoryTooltip(n,"ablation")}]},cursor:{show:!0,drag:{setScale:!0}}};this.ablationPlot=new dn(t,[[],[]],e)}updateAblationPlot(){if(!this.ablationPlot||!this.ablationGroups.length)return;const e=this.ablationGroups.find(o=>o.axis==="credit");if(!e)return;const t=e.metrics.find(o=>o.metric==="val_acc");if(!t)return;const n=t.arms.map((o,l)=>l),s=t.arms.map(o=>o.mean);this.categoryLabels=t.arms.map(o=>o.value),this.ablationFixedAxes=e.fixed_axes.split(",").map(o=>o.split("=").pop()??o).join(", "),this.ablationPlot.setData([n,s]),this.fitScale(this.ablationPlot,"x",-.5,Math.max(n.length-.5,.5));const r=t.arms.flatMap(o=>[o.mean-o.std,o.mean+o.std]);r.length>0&&this.fitScale(this.ablationPlot,"y",Math.min(Math.min(...r),this.chance),Math.max(...r));const a=this.ablationPlot.root.querySelector(".u-title");a&&(a.textContent=`Ablation: ${e.axis} vs val_acc`)}initVariabilityPlot(){const e=document.getElementById("plotter-variability");if(!e)return;const t={width:e.clientWidth,height:pc(e),title:"Seed variability: validation accuracy per arm",axes:[{label:"credit arm",splits:()=>this.categoryIndices(),values:(n,s)=>s.map(r=>this.categoryLabels[r]??String(r)),grid:{stroke:te.border}},{label:"accuracy",grid:{stroke:te.border},side:1}],scales:{x:{time:!1},y:{time:!1}},series:[{},{label:"val_acc",width:0,points:{show:!1}}],hooks:{draw:[n=>{if(!this.records.length)return;const s=n.ctx,r={};this.records.forEach(c=>{const u=c.coordinate.credit,h=c.payload.val_acc;h!==void 0&&(r[u]||(r[u]=[])).push(h)});const a=Object.keys(r).sort(),o=n.bbox.width/(a.length*2);a.forEach((c,u)=>{const h=r[c].sort((x,R)=>x-R),d=h.length;if(d===0)return;const f=h[Math.floor(d*.25)],g=h[Math.floor(d*.5)],v=h[Math.floor(d*.75)],m=v-f,p=Math.max(h[0],f-1.5*m),S=Math.min(h[d-1],v+1.5*m),y=n.valToPos(u,"x"),w=n.valToPos(p,"y"),O=n.valToPos(f,"y"),A=n.valToPos(g,"y"),P=n.valToPos(v,"y"),N=n.valToPos(S,"y"),b=bn[c]||te.gradient;s.strokeStyle=b,s.lineWidth=1.5,s.beginPath(),s.moveTo(y,w),s.lineTo(y,O),s.moveTo(y,P),s.lineTo(y,N),s.stroke(),s.fillStyle=b+"44",s.strokeStyle=b,s.lineWidth=1.5,s.fillRect(y-o/2,P,o,O-P),s.strokeRect(y-o/2,P,o,O-P),s.strokeStyle="white",s.lineWidth=2,s.beginPath(),s.moveTo(y-o/2,A),s.lineTo(y+o/2,A),s.stroke(),h.forEach(x=>{if(x<p||x>S){const R=n.valToPos(x,"y");s.fillStyle=b,s.beginPath(),s.arc(y,R,2,0,Math.PI*2),s.fill()}})});const l=n.valToPos(this.chance,"y");s.strokeStyle=te.chance_line,s.lineWidth=2,s.setLineDash([5,5]),s.beginPath(),s.moveTo(n.bbox.left,l),s.lineTo(n.bbox.width,l),s.stroke(),s.setLineDash([])}],setCursor:[n=>{this.showCategoryTooltip(n,"variability")}]},cursor:{show:!0,drag:{setScale:!0}}};this.variabilityPlot=new dn(t,[[],[]],e)}updateVariabilityPlot(){if(!this.variabilityPlot||!this.records.length)return;const e=Array.from(new Set(this.records.map(r=>r.coordinate.credit))).sort(),t=e.map((r,a)=>a),n=e.map(()=>0);this.categoryLabels=e,this.variabilityPlot.setData([t,n]),this.fitScale(this.variabilityPlot,"x",-.5,Math.max(e.length-.5,.5));const s=this.records.map(r=>r.payload.val_acc).filter(r=>typeof r=="number");s.length>0&&this.fitScale(this.variabilityPlot,"y",Math.min(Math.min(...s),this.chance),Math.max(...s))}categoryIndices(){return this.categoryLabels.map((e,t)=>t)}showTooltip(e,t){if(!this.tooltip||!this.container)return;const n=e.cursor;if(!n||n.left==null||n.top==null){this.hideTooltip();return}const s=e.ctx.canvas.getBoundingClientRect(),r=this.container.getBoundingClientRect();this.tooltip.innerHTML=t,this.tooltip.style.display="block",this.tooltip.style.left=`${s.left-r.left+e.bbox.left+n.left+14}px`,this.tooltip.style.top=`${s.top-r.top+e.bbox.top+n.top+14}px`}hideTooltip(){this.tooltip&&(this.tooltip.style.display="none")}showScatterTooltip(e){var d,f;const t=e.cursor;if(!t||t.left==null||t.top==null){this.hideTooltip();return}let n=-1,s=1/0;if(this.paretoXData.forEach((g,v)=>{const m=this.paretoYData[v];if(!Number.isFinite(g)||!Number.isFinite(m))return;const p=e.valToPos(g,"x"),S=e.valToPos(m,"y");if(!Number.isFinite(p)||!Number.isFinite(S))return;const y=(p-t.left)**2+(S-t.top)**2;y<s&&(s=y,n=v)}),n<0||s>400){this.hideTooltip();return}const r=this.recordAt(n);if(!r){this.hideTooltip();return}const a=this.paretoRecordIndices[n],o=((d=r.coordinate)==null?void 0:d.credit)??"?",l=r.payload.val_acc??0,c=r.payload.walltime_s??0,u=((f=r.schedule)==null?void 0:f.seed)??"?",h=this.paretoFlags[a]?" · PARETO":"";this.showTooltip(e,`${o} · val_acc ${l.toFixed(3)} · ${c.toFixed(1)}s · seed ${u}${h}`)}showCategoryTooltip(e,t){const n=e.cursor;if(!n||n.left==null||n.top==null){this.hideTooltip();return}const s=Math.round(e.posToVal(n.left,"x"));if(s<0||s>=this.categoryLabels.length){this.hideTooltip();return}const r=this.categoryLabels[s];if(t==="ablation"){const u=this.ablationGroups.find(f=>f.axis==="credit"),h=u==null?void 0:u.metrics.find(f=>f.metric==="val_acc"),d=h==null?void 0:h.arms[s];if(!d){this.hideTooltip();return}this.showTooltip(e,`${r} · ${d.mean.toFixed(3)} ± ${d.std.toFixed(3)} (n=${d.count})${d.at_chance?" · at chance":""}`);return}const a=this.records.filter(u=>u.coordinate.credit===r).map(u=>u.payload.val_acc).filter(u=>typeof u=="number").sort((u,h)=>u-h);if(a.length===0){this.hideTooltip();return}const o=a[Math.floor(a.length*.5)],l=a[Math.floor(a.length*.25)],c=a[Math.floor(a.length*.75)];this.showTooltip(e,`${r} · median ${o.toFixed(3)} · IQR ${(c-l).toFixed(3)} · n=${a.length}`)}downloadCurrent(){const t={pareto:this.paretoPlot,ablation:this.ablationPlot,variability:this.variabilityPlot}[this.currentTab];if(!t)return;const n=document.createElement("a");n.download=`computronium-${this.currentTab}-${Date.now()}.png`,n.href=this.exportImage(t),n.click()}exportImage(e){const t=Array.from(e.root.querySelectorAll("canvas")),n=e.root.getBoundingClientRect(),s=Math.max(...t.map(l=>l.width),1),r=Math.max(...t.map(l=>l.height),1),a=document.createElement("canvas");a.width=s,a.height=r;const o=a.getContext("2d");return o?(o.fillStyle=te.bg,o.fillRect(0,0,s,r),t.forEach(l=>{const c=l.getBoundingClientRect();if(c.width===0||c.height===0)return;const u=l.width/c.width;o.drawImage(l,(c.left-n.left)*u,(c.top-n.top)*u,l.width,l.height)}),a.toDataURL("image/png")):e.ctx.canvas.toDataURL("image/png")}}const Xu=new fb;Wi.register(Xu);class pb{constructor(){G(this,"name","LiveRail");G(this,"container",null);G(this,"logContainer",null);G(this,"events",[]);G(this,"maxEvents",50);G(this,"onPipelineEvent",e=>{this.events.unshift(e),this.events.length>this.maxEvents&&this.events.pop(),this.render()});G(this,"onStatusUpdate",e=>{var r,a,o;const t=((r=e==null?void 0:e.data)==null?void 0:r.running_campaigns)??0,n=((a=e==null?void 0:e.data)==null?void 0:a.queued_campaigns)??0,s=(o=this.container)==null?void 0:o.querySelector("#rail-queue");s&&(s.textContent=`${t} running · ${n} queued`)});Zt.register("pipeline_event",this.onPipelineEvent),Zt.register("status_update",this.onStatusUpdate)}async init(){this.createUI(),Vr.onStateChange(e=>this.setConnected(e==="connected")),console.log("[LiveRail] Initialized")}async destroy(){var e;Zt.unregister("pipeline_event",this.onPipelineEvent),Zt.unregister("status_update",this.onStatusUpdate),(e=this.container)==null||e.remove()}createUI(){const e=document.getElementById("ui-overlay");e&&(this.container=document.createElement("div"),this.container.id="live-rail",this.container.style.cssText=`
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
    `,e.appendChild(this.container),this.logContainer=this.container.querySelector("#rail-log"))}toggle(){this.container&&(this.container.style.display=this.container.style.display==="none"?"":"none")}setConnected(e){var a;const t=(a=this.container)==null?void 0:a.querySelector("#rail-connection");if(!t)return;const n=t.querySelector(".dot"),s=t.querySelector(".rail-label");if(!n||!s)return;const r=e?te.ok:te.error;n.style.background=r,t.style.background=r+"22",t.style.borderColor=r+"88",t.style.color=r,s.textContent=e?"Connected":"Disconnected"}render(){var t;if(!this.logContainer)return;this.logContainer.innerHTML=this.events.map(n=>{const s=new Date(n.timestamp).toLocaleTimeString(),a={ok:te.ok,warn:te.warn,error:te.error}[n.level]||te.text_secondary,o=n.level==="ok"?"✓":n.level==="warn"?"⚠":"✗";return`
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
            <span style="color: var(--text-secondary);">${s}</span>
            <span style="color: ${a};">${o}</span>
            <span style="color: var(--text-muted);">[${n.stage}]</span>
            <span>${n.message}</span>
          </span>
        `}).join("");const e=(t=this.container)==null?void 0:t.querySelector("#rail-count");e&&(e.textContent=`${this.events.length} events`),this.logContainer.scrollLeft=0}}const qu=new pb;Wi.register(qu);const mb=4e3,gb={ok:te.text_primary,warn:te.warn,error:te.error};class _b{constructor(){G(this,"name","Caption");G(this,"container",null);G(this,"headline",null);G(this,"context",null);G(this,"state",[]);G(this,"spoken",null);G(this,"last",null);G(this,"holdTimer",null);G(this,"onNarration",e=>{this.state=(e==null?void 0:e.state)??[],this.render()});G(this,"onEvent",e=>{e!=null&&e.sentence&&this.say(e.sentence,e.level??"ok")});Zt.register("narration",this.onNarration),Zt.register("pipeline_event",this.onEvent)}async init(){this.createUI(),this.render()}async destroy(){var e;Zt.unregister("narration",this.onNarration),Zt.unregister("pipeline_event",this.onEvent),this.holdTimer!==null&&window.clearTimeout(this.holdTimer),(e=this.container)==null||e.remove()}toggle(){this.container&&(this.container.style.display=this.container.style.display==="none"?"":"none")}say(e,t="ok"){e&&(this.spoken={text:e,level:t},this.last={text:e,level:t},this.render(),this.holdTimer!==null&&window.clearTimeout(this.holdTimer),this.holdTimer=window.setTimeout(()=>{this.spoken=null,this.holdTimer=null,this.render()},mb))}createUI(){const e=document.getElementById("ui-overlay");e&&(this.container=document.createElement("div"),this.container.id="caption",this.container.style.cssText=`
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
    `,e.appendChild(this.container),this.headline=this.container.querySelector("#caption-headline"),this.context=this.container.querySelector("#caption-context"))}render(){if(!(!this.headline||!this.context)){if(this.spoken){this.headline.textContent=this.spoken.text,this.headline.style.color=this.colorOf(this.spoken.level),this.context.textContent=this.state.join(" ");return}if(this.state.length>0){this.headline.textContent=this.state[0],this.headline.style.color=te.text_primary,this.context.textContent=this.state.slice(1).join(" ");return}if(this.last){this.headline.textContent=this.last.text,this.headline.style.color=this.colorOf(this.last.level),this.context.textContent="";return}this.headline.textContent="The dashboard is starting.",this.headline.style.color=te.text_primary,this.context.textContent=""}}colorOf(e){return gb[e]??te.text_primary}}const Yu=new _b;Wi.register(Yu);class vb{constructor(){G(this,"name","HUD");G(this,"panel",null);G(this,"modeChip",null);G(this,"connectionPill",null);G(this,"rows",new Map);G(this,"rowElements",new Map);G(this,"claimValue",null);G(this,"sourceValue",null);G(this,"statusData",{});G(this,"resources",{});G(this,"requiredSeeds",0);G(this,"measuredSeeds",0);G(this,"connected",!1);G(this,"animationTime",0);G(this,"onStatusUpdate",e=>{const t=(e==null?void 0:e.data)??e;t&&(this.statusData=t,this.updateQueueRows())});G(this,"onCampaignMetrics",e=>{const t=e==null?void 0:e.data;t&&qn.observe(e==null?void 0:e.campaign_id,t)});G(this,"onRunChanged",(e,t)=>{var n;t&&(this.resources=t.resources??{},typeof t.required_seeds=="number"&&(this.requiredSeeds=t.required_seeds),this.measuredSeeds=this.resources.seeds_per_arm??((n=t.records)==null?void 0:n.length)??0,this.updateModeChip(t.run),this.updateSource(t.store),this.updateResourceRows(),this.updateClaim())});Zt.register("status_update",this.onStatusUpdate),Zt.register("campaign_metrics",this.onCampaignMetrics),qn.onChange(this.onRunChanged)}async init(){this.createPanel(),this.createModeChip(),Vr.onStateChange(e=>{this.connected=e==="connected",this.updateConnection()}),console.log("[HUD] Initialized")}async destroy(){var e,t;Zt.unregister("status_update",this.onStatusUpdate),Zt.unregister("campaign_metrics",this.onCampaignMetrics),(e=this.panel)==null||e.remove(),(t=this.modeChip)==null||t.remove()}createPanel(){const e=document.getElementById("ui-overlay");if(!e)return;this.panel=document.createElement("div"),this.panel.id="hud",this.panel.style.cssText=`
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
        <span id="hud-source" style="font-weight: 600; color: ${te.text_secondary};">—</span>
      </div>
      <div style="margin-top: 12px; padding-top: 10px; border-top: 1px solid var(--border); display: flex; justify-content: space-between; align-items: baseline;">
        <span style="color: var(--text-secondary);">SEEDS TO CLAIM</span>
        <span id="hud-claim" style="font-weight: 700; color: ${te.insufficient};">—</span>
      </div>
    `,e.appendChild(this.panel);const t=this.panel.querySelector("#hud-meters");this.addMeter(t,"device","DEVICE",te.gradient),this.addMeter(t,"memory","MEMORY",te.memory),this.addMeter(t,"walltime","WALLTIME",te.cpu),this.addMeter(t,"gpu","GPU",te.gpu),this.addMeter(t,"cpu","CPU",te.cpu),this.addMeter(t,"records","RECORDS",te.promoted),this.claimValue=this.panel.querySelector("#hud-claim"),this.connectionPill=this.panel.querySelector("#hud-connection"),this.sourceValue=this.panel.querySelector("#hud-source")}addMeter(e,t,n,s){const r=document.createElement("div");r.style.cssText="display: flex; flex-direction: column; gap: 3px;",r.innerHTML=`
      <div style="display: flex; justify-content: space-between;">
        <span style="color: var(--text-secondary);">${n}</span>
        <span class="hud-value" style="color: var(--text-primary);">—</span>
      </div>
      <div style="height: 4px; background: var(--bg); border-radius: 2px; overflow: hidden;">
        <div class="hud-fill" style="height: 100%; width: 0%; background: ${s}; border-radius: 2px; transition: width 0.4s ease;"></div>
      </div>
    `,e.appendChild(r),this.rows.set(t,{key:t,label:n,value:"",fraction:0,color:s}),this.rowElements.set(t,{fill:r.querySelector(".hud-fill"),value:r.querySelector(".hud-value")})}createModeChip(){const e=document.getElementById("ui-overlay");e&&(this.modeChip=document.createElement("div"),this.modeChip.id="mode-chip",this.modeChip.style.cssText=`
      position: fixed;
      top: 20px;
      left: 20px;
      padding: 6px 14px;
      border-radius: 16px;
      background: ${te.text_muted}22;
      border: 1px solid ${te.text_muted}88;
      color: ${te.text_muted};
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
    `,e.appendChild(this.modeChip))}updateModeChip(e){if(!this.modeChip)return;const t=(e==null?void 0:e.mode)??"NO RUN",n=t==="PREREGISTERED"?te.passed:t==="EXPLORATORY"?te.insufficient:te.text_muted;this.modeChip.style.background=`${n}22`,this.modeChip.style.borderColor=`${n}88`,this.modeChip.style.color=n;const s=this.modeChip.querySelector(".mode-label");s&&(s.textContent=t);const r=this.modeChip.querySelector(".mode-detail");r&&(r.textContent=[e==null?void 0:e.profile,((e==null?void 0:e.tasks)??[]).join(", "),e==null?void 0:e.fidelity].filter(Boolean).join(" · ")),this.modeChip.title=e?`run ${e.run_id??"?"} · objectives: ${(e.objectives??[]).join(", ")||"none"}`:"No run has reported yet"}setMeter(e,t,n){const s=this.rows.get(e),r=this.rowElements.get(e);!s||!r||(s.value=t,s.fraction=Math.max(0,Math.min(1,n)),r.value.textContent=t,r.fill.style.width=`${(s.fraction*100).toFixed(1)}%`)}updateSource(e){if(!this.sourceValue)return;const t=e==null?void 0:e.source;if(!t){this.sourceValue.textContent="—",this.sourceValue.style.color=te.text_secondary;return}if(t==="snapshot"){const n=e!=null&&e.published_at?new Date(e.published_at).toLocaleTimeString():"";this.sourceValue.textContent=n?`snapshot ${n}`:"snapshot",this.sourceValue.style.color=te.insufficient,this.sourceValue.title="The writer published this copy; it is as fresh as its last publish.";return}this.sourceValue.textContent="live",this.sourceValue.style.color=te.passed,this.sourceValue.title="The store itself, read as it is written."}updateQueueRows(){const e=this.statusData;this.setMeter("gpu",e.max_gpus?`${e.used_gpus??0} / ${e.max_gpus}`:"—",e.max_gpus?(e.used_gpus??0)/e.max_gpus:0),this.setMeter("cpu",e.max_cpus?`${e.used_cpus??0} / ${e.max_cpus}`:"—",e.max_cpus?(e.used_cpus??0)/e.max_cpus:0)}updateResourceRows(){const e=this.resources;this.setMeter("device",e.device??"—",e.device?1:0),this.setMeter("memory",e.memory_mb!==void 0?`${e.memory_mb.toFixed(1)} MB`:"—",e.memory_mb!==void 0?Math.min(1,e.memory_mb/2048):0),this.setMeter("walltime",e.walltime_s!==void 0?`${e.walltime_s.toFixed(1)} s`:"—",e.walltime_s!==void 0?Math.min(1,e.walltime_s/120):0),this.setMeter("records",e.records!==void 0?`${e.records}`:"—",e.records!==void 0?Math.min(1,e.records/20):0)}updateClaim(){if(!this.claimValue)return;if(this.requiredSeeds<=0){this.claimValue.textContent="—";return}const e=Math.max(0,this.requiredSeeds-this.measuredSeeds);this.claimValue.textContent=`${e} more (${this.requiredSeeds} needed)`}updateConnection(){if(!this.connectionPill)return;const e=this.connectionPill.querySelector(".dot"),t=this.connectionPill.querySelector("span:last-child"),n=this.connected?te.ok:te.error;e.style.background=n,this.connectionPill.style.background=`${n}22`,this.connectionPill.style.borderColor=`${n}88`,this.connectionPill.style.color=n,t.textContent=this.connected?"live":"offline"}toggle(){this.panel&&(this.panel.style.display=this.panel.style.display==="none"?"":"none")}update(e){var n;this.animationTime+=e;const t=.5+.5*Math.sin(this.animationTime*2);(n=this.connectionPill)==null||n.style.setProperty("opacity",`${.75+.25*t}`)}}const ml=new vb;Wi.register(ml);class xb{constructor(e){G(this,"canvas");G(this,"context");G(this,"visible",!1);this.canvas=document.createElement("canvas"),this.canvas.id=e,this.canvas.style.cssText=`
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      z-index: 50;
      display: none;
      background: var(--bg);
      pointer-events: none;
    `,document.body.appendChild(this.canvas),this.context=this.canvas.getContext("2d"),this.resize(),window.addEventListener("resize",()=>{this.resize()})}show(){this.visible=!0,this.canvas.style.display="block",this.resize()}hide(){this.visible=!1,this.canvas.style.display="none"}resize(){const e=Math.min(window.devicePixelRatio||1,2);this.canvas.width=Math.floor(window.innerWidth*e),this.canvas.height=Math.floor(window.innerHeight*e),this.context.setTransform(e,0,0,e,0,0)}begin(){const e=this.context;return e.clearRect(0,0,window.innerWidth,window.innerHeight),e.fillStyle="#0a0e14",e.fillRect(0,0,window.innerWidth,window.innerHeight),e}area(){const e=document.getElementById("discovery-legend"),t=e?e.getBoundingClientRect().right:0,n=Math.max(40,t+24),s=Math.max(200,window.innerWidth*rp-n);return{x:n,y:70,width:s,height:Math.max(200,window.innerHeight*ap-70)}}}const Ht=new xb("stage-2d"),_n={top:64,right:36,bottom:62,left:78};function gl(i,e,t,n){i.fillStyle=te.text_primary,i.font="600 22px 'JetBrains Mono', monospace",i.textAlign="left",i.textBaseline="alphabetic",i.fillText(t,e.x,e.y+14),n&&(i.fillStyle=te.text_secondary,i.font="13px 'JetBrains Mono', monospace",i.fillText(n,e.x,e.y+40))}function Qo(i,e,t=5){if(!Number.isFinite(i)||!Number.isFinite(e))return[i];if(i===e)return[i];const s=(e-i)/Math.max(1,t),r=10**Math.floor(Math.log10(s)),a=s/r,o=(a>=5?10:a>=2?5:a>=1?2:1)*r,l=Math.ceil(i/o)*o,c=[];for(let u=l;u<=e+o*1e-6;u+=o)c.push(Number(u.toFixed(10)));return c}function el(i){const e=Math.abs(i);return e===0?"0":e>=1e3||e>=10?i.toFixed(0):e>=1?i.toFixed(1):e>=.01?i.toFixed(2):i.toExponential(1)}function tl(i,e){const t=e.xMax-e.xMin;return t===0?e.rect.x:e.rect.x+(i-e.xMin)/t*e.rect.width}function Aa(i,e){const t=e.yMax-e.yMin;return t===0?e.rect.y+e.rect.height:e.rect.y+e.rect.height-(i-e.yMin)/t*e.rect.height}function yb(i,e,t){const n={x:e.x+_n.left,y:e.y+_n.top,width:Math.max(40,e.width-_n.left-_n.right),height:Math.max(40,e.height-_n.top-_n.bottom)},s={rect:n,xMin:t.xMin,xMax:t.xMax,yMin:t.yMin,yMax:t.yMax};gl(i,e,t.title,t.subtitle);const r=Qo(t.xMin,t.xMax,6),a=Qo(t.yMin,t.yMax,5);return i.strokeStyle=te.border,i.lineWidth=1,i.beginPath(),i.rect(n.x,n.y,n.width,n.height),i.stroke(),i.font="12px 'JetBrains Mono', monospace",i.fillStyle=te.text_secondary,r.forEach(o=>{const l=tl(o,s);l<n.x-1||l>n.x+n.width+1||(i.strokeStyle=te.border,i.beginPath(),i.moveTo(l,n.y),i.lineTo(l,n.y+n.height),i.stroke(),i.textAlign="center",i.fillText(el(o),l,n.y+n.height+20))}),a.forEach(o=>{const l=Aa(o,s);l<n.y-1||l>n.y+n.height+1||(i.strokeStyle=te.border,i.beginPath(),i.moveTo(n.x,l),i.lineTo(n.x+n.width,l),i.stroke(),i.textAlign="right",i.fillText(el(o),n.x-10,l+4))}),i.fillStyle=te.text_secondary,i.font="13px 'JetBrains Mono', monospace",i.textAlign="center",i.fillText(t.xLabel,n.x+n.width/2,n.y+n.height+46),i.save(),i.translate(n.x-56,n.y+n.height/2),i.rotate(-Math.PI/2),i.textAlign="center",i.fillText(t.yLabel,0,0),i.restore(),s}function Ba(i,e,t){i.fillStyle=te.text_secondary,i.font="12px 'JetBrains Mono', monospace",i.textAlign="left",i.textBaseline="alphabetic",i.fillText(t,e.x,e.y+e.height+40)}function Mb(i,e,t){const n={x:e.x+_n.left,y:e.y+_n.top,width:Math.max(40,e.width-_n.left-_n.right),height:Math.max(40,e.height-_n.top-_n.bottom)},s=n.width/Math.max(1,t.categories.length),r={rect:n,yMin:t.yMin,yMax:t.yMax,categories:t.categories,bandWidth:s,band:l=>n.x+s*(l+.5)},a={rect:n,yMin:t.yMin,yMax:t.yMax};return gl(i,e,t.title,t.subtitle),i.strokeStyle=te.border,i.lineWidth=1,i.strokeRect(n.x+.5,n.y+.5,n.width-1,n.height-1),i.font="12px 'JetBrains Mono', monospace",i.fillStyle=te.text_secondary,(t.yTicks??Qo(t.yMin,t.yMax,5)).forEach(l=>{const c=Aa(l,a);c<n.y-1||c>n.y+n.height+1||(i.strokeStyle=te.border,i.beginPath(),i.moveTo(n.x,c),i.lineTo(n.x+n.width,c),i.stroke(),i.textAlign="right",i.fillText(el(l),n.x-10,c+4))}),i.textAlign="center",i.textBaseline="top",t.categories.forEach((l,c)=>{jo(l,14).forEach((u,h)=>{i.fillText(u,r.band(c),n.y+n.height+12+h*16)})}),i.fillStyle=te.text_secondary,i.font="13px 'JetBrains Mono', monospace",i.save(),i.translate(n.x-56,n.y+n.height/2),i.rotate(-Math.PI/2),i.textAlign="center",i.textBaseline="alphabetic",i.fillText(t.yLabel,0,0),i.restore(),r}function $p(i,e,t){i.font="12px 'JetBrains Mono', monospace";const n=t.rows.reduce((u,h)=>Math.max(u,i.measureText(h).width),0),s=Math.min(e.width*.45,Math.max(_n.left,n+24)),r={x:e.x+s,y:e.y+_n.top,width:Math.max(40,e.width-s-_n.right),height:Math.max(40,e.height-_n.top-_n.bottom)},a=r.height/Math.max(1,t.rows.length),o={rect:r,xMin:t.xMin,xMax:t.xMax,rows:t.rows,rowHeight:a,rowY:u=>r.y+a*(u+.5)},l={rect:r,xMin:t.xMin,xMax:t.xMax};return gl(i,e,t.title,t.subtitle),i.strokeStyle=te.border,i.lineWidth=1,i.strokeRect(r.x+.5,r.y+.5,r.width-1,r.height-1),i.font="12px 'JetBrains Mono', monospace",i.fillStyle=te.text_secondary,(t.xTicks??Qo(t.xMin,t.xMax,6)).forEach(u=>{const h=tl(u,l);h<r.x-1||h>r.x+r.width+1||(i.strokeStyle=te.border,i.beginPath(),i.moveTo(h,r.y),i.lineTo(h,r.y+r.height),i.stroke(),i.textAlign="center",i.textBaseline="alphabetic",i.fillText(el(u),h,r.y+r.height+20))}),i.textAlign="right",i.textBaseline="middle",t.rows.forEach((u,h)=>{i.fillText(u,r.x-12,o.rowY(h))}),i.fillStyle=te.text_secondary,i.font="13px 'JetBrains Mono', monospace",i.textAlign="center",i.textBaseline="alphabetic",i.fillText(t.xLabel,r.x+r.width/2,r.y+r.height+46),o}class Sb{constructor(){G(this,"id","cost");G(this,"name","The claim's cost");G(this,"caption","The seeds each cell measured, against the seeds a claim is measured against.");G(this,"visible",!1);G(this,"drawn",!1)}enter(){this.visible=!0,Ht.show(),this.draw()}exit(){this.visible=!1,Ht.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}costs(){const e=Ue.axes,t=Ue.requiredSeeds,n=Pu(Ue.aggregates,e),s=al(n,e);return n.map(r=>({cell:r,label:La(r,e,s),color:bn[r.coordinate.credit]??te.gradient,measured:r.seeds,required:t})).sort((r,a)=>a.required-a.measured-(r.required-r.measured))}draw(){const e=this.costs();if(e.length===0){this.drawn=!1;return}const t=Ht.begin(),n=Ht.area(),s=Math.max(Ue.requiredSeeds,...e.map(c=>c.measured)),r=$p(t,n,{xMin:0,xMax:s,rows:e.map(c=>c.label),title:"The claim's cost",subtitle:"the seeds measured, and the seeds a claim still needs",xLabel:"seeds"}),a=c=>r.rect.x+c/(r.xMax||1)*r.rect.width;e.forEach((c,u)=>{const h=r.rowY(u),d=Math.min(26,r.rowHeight*.5);t.fillStyle=te.bg_tertiary,t.fillRect(r.rect.x,h-d/2,a(c.required)-r.rect.x,d);const f=a(c.measured)-r.rect.x;t.fillStyle=c.color,t.fillRect(r.rect.x,h-d/2,f,d);const g=Math.max(0,c.required-c.measured);g>0&&(t.strokeStyle=te.warn,t.lineWidth=2,t.setLineDash([5,4]),t.beginPath(),t.moveTo(a(c.measured)+4,h),t.lineTo(a(c.required)-4,h),t.stroke(),t.setLineDash([])),t.strokeStyle=te.border,t.lineWidth=1,t.strokeRect(r.rect.x+.5,h-d/2,a(c.required)-r.rect.x-1,d-1),t.font="12px 'JetBrains Mono', monospace",t.textAlign="left",t.textBaseline="middle",t.fillStyle=te.text_secondary,t.fillText(`${c.measured} of ${c.required}`,r.rect.x+r.rect.width+12,h-8),g>0&&(t.fillStyle=te.warn,t.fillText(`${g} short`,r.rect.x+r.rect.width+12,h+9))});const o=a(Ue.requiredSeeds);o>r.rect.x&&o<r.rect.x+r.rect.width&&(t.strokeStyle=te.text_secondary,t.lineWidth=1,t.setLineDash([3,4]),t.beginPath(),t.moveTo(o,r.rect.y),t.lineTo(o,r.rect.y+r.rect.height),t.stroke(),t.setLineDash([]));const l=e.reduce((c,u)=>c+Math.max(0,u.required-u.measured),0);Ba(t,n,`the claim is ${l} seeds short over ${e.length} cells`),this.drawn=!0}}class bb{constructor(){G(this,"id","convergence");G(this,"name","Convergence");G(this,"caption","Accuracy against epoch, one curve per arm, with the chance level under them.");G(this,"visible",!1);G(this,"drawn",!1)}enter(){this.visible=!0,Ht.show(),this.draw()}exit(){this.visible=!1,Ht.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}curves(){var n;const e=((n=Ue.metrics)==null?void 0:n.records)??[],t=new Map;return e.forEach(s=>{var l,c;const r=(l=s==null?void 0:s.payload)==null?void 0:l.convergence_curve;if(!Array.isArray(r)||r.length===0)return;const a=((c=s==null?void 0:s.coordinate)==null?void 0:c.credit)??"",o=t.get(a)??new Map;r.forEach(u=>{if(typeof(u==null?void 0:u.epoch)!="number"||typeof(u==null?void 0:u.val_acc)!="number")return;const h=o.get(u.epoch)??[];h.push(u.val_acc),o.set(u.epoch,h)}),t.set(a,o)}),Array.from(t.entries()).map(([s,r])=>({arm:s,points:Array.from(r.entries()).sort((a,o)=>a[0]-o[0]).map(([a,o])=>({epoch:a,val_acc:o.reduce((l,c)=>l+c,0)/o.length}))}))}draw(){const e=this.curves();if(e.length===0){this.drawn=!1;return}const t=Ht.begin(),n=Ht.area(),s=Ue.chance,r=Math.max(...e.flatMap(u=>u.points.map(h=>h.epoch))),a=Math.max(s,...e.flatMap(u=>u.points.map(h=>h.val_acc))),o=yb(t,n,{xMin:0,xMax:r,yMin:0,yMax:a,xLabel:"epoch",yLabel:"accuracy",title:"Convergence",subtitle:"the mean accuracy of each arm, epoch by epoch"}),l=Aa(s,o);t.strokeStyle=te.chance_line,t.lineWidth=1.5,t.setLineDash([6,5]),t.beginPath(),t.moveTo(o.rect.x,l),t.lineTo(o.rect.x+o.rect.width,l),t.stroke(),t.setLineDash([]),e.forEach(u=>{const h=bn[u.arm]||te.gradient;t.strokeStyle=h,t.lineWidth=2.5,t.beginPath(),u.points.forEach((d,f)=>{const g=tl(d.epoch,o),v=Aa(d.val_acc,o);f===0?t.moveTo(g,v):t.lineTo(g,v)}),t.stroke(),u.points.forEach(d=>{t.fillStyle=h,t.beginPath(),t.arc(tl(d.epoch,o),Aa(d.val_acc,o),3,0,Math.PI*2),t.fill()})}),t.font="12px 'JetBrains Mono', monospace",t.textAlign="left",t.textBaseline="middle";let c=o.rect.y+10;e.forEach(u=>{const h=bn[u.arm]||te.gradient;t.fillStyle=h,t.fillRect(o.rect.x+o.rect.width+18,c-5,10,10),t.fillStyle=te.text_secondary,t.fillText(u.arm,o.rect.x+o.rect.width+34,c),c+=20}),Ba(t,n,`${e.length} arms · the dashed line is the chance level (${s.toFixed(2)})`),this.drawn=!0}}function nl(i){i.traverse(e=>{var s;const t=e;(s=t.geometry)==null||s.dispose();const n=t.material;Array.isArray(n)?n.forEach(r=>r.dispose()):n==null||n.dispose()})}const br=6.4,xa=4,Er=5;class Eb{constructor(){G(this,"id","frontier");G(this,"name","Frontier");G(this,"caption","Every measured cell in accuracy, speed and parameters; the frontier is the line nothing beat.");G(this,"group",new as);G(this,"visible",!1);G(this,"drawn",!1);G(this,"framed",!1);G(this,"accuracy",{min:0,max:0,span:0})}enter(){this.visible=!0;const e=Gr();e&&e.scene.add(this.group),this.draw(!0)}exit(){var e;this.visible=!1,(e=this.group.parent)==null||e.remove(this.group),nl(this.group),this.group=new as,this.drawn=!1,this.framed=!1}refresh(){this.visible&&this.draw(!1)}ready(){return this.drawn}points(){var h,d;const e=((h=Ue.metrics)==null?void 0:h.records)??[],t=((d=Ue.metrics)==null?void 0:d.pareto)??[],n=Ue.chance,s=[],r=[],a=[];e.forEach(f=>{const g=(f==null?void 0:f.payload)??{};typeof g.val_acc=="number"&&s.push(g.val_acc),typeof g.walltime_s=="number"&&g.walltime_s>0&&r.push(1/g.walltime_s),typeof g.param_count=="number"&&g.param_count>0&&a.push(Math.log10(g.param_count))});const o=mc([...s,n]);this.accuracy=o;const l=mc(r),c=mc(a),u=[];return e.forEach((f,g)=>{var S;const v=(f==null?void 0:f.payload)??{};if(typeof v.val_acc!="number")return;const m=typeof v.walltime_s=="number"&&v.walltime_s>0?1/v.walltime_s:null,p=typeof v.param_count=="number"&&v.param_count>0?Math.log10(v.param_count):null;u.push({x:m===null||l.span===0?0:((m-l.min)/l.span-.5)*br,y:o.span===0?0:(v.val_acc-o.min)/o.span*xa,z:p===null||c.span===0?0:((p-c.min)/c.span-.5)*Er,arm:((S=f==null?void 0:f.coordinate)==null?void 0:S.credit)??"",pareto:t[g]===!0})}),u}draw(e){const t=this.points();if(t.length===0){this.drawn=!1;return}this.clear(),this.addPoints(t),this.addFront(t),this.addChanceFloor(),this.addLabels(),this.drawn=!0,(e||!this.framed)&&(this.frame(),this.framed=!0)}clear(){[...this.group.children].forEach(e=>{this.group.remove(e),nl(e)})}addPoints(e){const t=[],n=[];e.forEach(o=>{t.push(o.x,o.y,o.z);const l=new nt(bn[o.arm]||te.gradient);n.push(l.r,l.g,l.b)});const s=new Xt;s.setAttribute("position",new qt(t,3)),s.setAttribute("color",new qt(n,3));const r=new wu({size:.26,sizeAttenuation:!0,vertexColors:!0,map:fM(),alphaTest:.4,transparent:!0,opacity:.95});this.group.add(new np(s,r));const a=e.filter(o=>o.pareto);a.length!==0&&a.forEach(o=>{const l=pM(te.pareto,.26);l.position.set(o.x,o.y,o.z),this.group.add(l)})}addFront(e){const t=e.filter(a=>a.pareto).sort((a,o)=>a.y-o.y);if(t.length<2)return;const n=[];t.forEach(a=>n.push(a.x,a.y,a.z));const s=new Xt;s.setAttribute("position",new qt(n,3));const r=new $o(s,new ip({color:te.pareto,dashSize:.22,gapSize:.16,transparent:!0,opacity:.85}));r.computeLineDistances(),this.group.add(r)}addChanceFloor(){const e=Ue.chance,t=this.accuracy;if(t.span===0)return;const n=(e-t.min)/t.span*xa,s=new Oa(br*1.02,Er*1.02);s.rotateX(-Math.PI/2);const r=new gn(s,new Ir({color:te.chance_line,transparent:!0,opacity:.07,side:$n,depthWrite:!1}));r.position.y=n,this.group.add(r);const a=Mi("chance",.24,new ks({color:te.chance_line,sizeAttenuation:!0}));a.position.set(br/2+.3,n,Er/2+.3),this.group.add(a)}addLabels(){const e=new ks({color:13227232,sizeAttenuation:!0}),t=Mi("speed 1/s",.26,e);t.position.set(br/2+.6,.1,0),this.group.add(t);const n=Mi("accuracy",.26,e);n.position.set(0,xa+.4,0),this.group.add(n);const s=Mi("parameters",.26,e);s.position.set(0,.1,Er/2+.7),this.group.add(s)}frame(){const e=Gr();e&&Ru(e,new k(-br/2-.6,-.2,-Er/2-.6),new k(br/2+.6,xa+.6,Er/2+.6),new k(0,xa/2,0))}}function mc(i){const e=i.filter(s=>Number.isFinite(s));if(e.length===0)return{min:0,max:0,span:0};const t=Math.min(...e),n=Math.max(...e);return{min:t,max:n,span:n-t}}function $u(i){const e=i.replace("#","");return[parseInt(e.slice(0,2),16),parseInt(e.slice(2,4),16),parseInt(e.slice(4,6),16)]}function gf(i){return`#${i.map(e=>Math.round(Math.max(0,Math.min(255,e))).toString(16).padStart(2,"0")).join("")}`}function _f(i,e,t){return[i[0]+(e[0]-i[0])*t,i[1]+(e[1]-i[1])*t,i[2]+(e[2]-i[2])*t]}const wb=$u(te.ramp_low),vf=$u(te.ramp_mid),Tb=$u(te.ramp_high);function Po(i){const e=Math.max(0,Math.min(1,i));return e<=.5?gf(_f(wb,vf,e*2)):gf(_f(vf,Tb,(e-.5)*2))}class Ab{constructor(){G(this,"id","matrix");G(this,"name","Evidence matrix");G(this,"caption","The space seen from above: one axis against another, every column a number, the refusals in the void colour.");G(this,"visible",!1);G(this,"drawn",!1)}enter(){this.visible=!0,Ht.show(),this.draw()}exit(){this.visible=!1,Ht.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}columns(){const e=Ue.space;if(!e)return{columns:[],xValues:[],yValues:[]};const t=Ue.axes,n=e.values[t.x]??[],s=e.values[t.y]??[],r=e.values[t.z]??[],a=[];return n.forEach(o=>{s.forEach(l=>{let c=0,u=0,h=-1/0,d="";r.forEach(g=>{const v=Wr(o,l,g),m=Ue.spaceCells.get(v);if((m==null?void 0:m.status)==="void"){c+=1;return}u+=1;const p=Ue.aggregates.get(v);if(!p||p.acc.length===0)return;const S=Ns(p.acc);S>h&&(h=S,d=p.coordinate.credit??"")});const f=c>0&&u===0?"void":h>-1/0?"measured":"gap";a.push({status:f,accuracy:h>-1/0?h:0,arm:d})})}),{columns:a,xValues:n,yValues:s}}draw(){const{columns:e,xValues:t,yValues:n}=this.columns();if(e.length===0){this.drawn=!1;return}const s=Ht.begin(),r=Ht.area(),a=Ue.axes,o=t.length,l=n.length,c=150,h={x:r.x+c,y:r.y+70,width:Math.max(80,r.width-c-40),height:Math.max(80,r.height-70-96)},d=h.width/o,f=h.height/l,g=Math.max(...e.map(A=>A.accuracy),1e-4);s.fillStyle=te.text_primary,s.font="600 22px 'JetBrains Mono', monospace",s.textAlign="left",s.textBaseline="alphabetic",s.fillText("Evidence matrix",r.x,r.y+14),s.fillStyle=te.text_secondary,s.font="13px 'JetBrains Mono', monospace",s.fillText(`${a.x} against ${a.y} — the best cell of each column`,r.x,r.y+40);let v=0,m=0,p=0;e.forEach((A,P)=>{const N=Math.floor(P/l),b=P%l,x=h.x+N*d,R=h.y+b*f;A.status==="void"?(p+=1,s.fillStyle=`${te.void}22`,s.fillRect(x,R,d,f),this.drawCross(s,x,R,d,f)):A.status==="gap"?(m+=1,s.fillStyle=te.bg_tertiary,s.fillRect(x,R,d,f)):(v+=1,s.fillStyle=Po(A.accuracy/g),s.fillRect(x,R,d,f),d>44&&f>26&&(s.fillStyle=Cb(A.accuracy/g),s.font="600 15px 'JetBrains Mono', monospace",s.textAlign="center",s.textBaseline="middle",s.fillText(A.accuracy.toFixed(2),x+d/2,R+f/2))),s.strokeStyle=te.bg,s.lineWidth=1,s.strokeRect(x+.5,R+.5,d-1,f-1)}),s.fillStyle=te.text_secondary,s.font="12px 'JetBrains Mono', monospace",t.forEach((A,P)=>{const N=jo(A,14);s.textAlign="center",s.textBaseline="top",N.forEach((b,x)=>{s.fillText(b,h.x+P*d+d/2,h.y+h.height+12+x*16)})}),n.forEach((A,P)=>{const N=jo(A,16);s.textAlign="right",s.textBaseline="middle",N.forEach((b,x)=>{s.fillText(b,h.x-12,h.y+P*f+f/2-(N.length-1)*8+x*16)})});const S=180,y=h.x+h.width-S,w=r.y+16,O=s.createLinearGradient(y,0,y+S,0);O.addColorStop(0,Po(0)),O.addColorStop(.5,Po(.5)),O.addColorStop(1,Po(1)),s.fillStyle=O,s.fillRect(y,w,S,12),s.strokeStyle=te.border,s.strokeRect(y+.5,w+.5,S-1,11),s.fillStyle=te.text_secondary,s.font="11px 'JetBrains Mono', monospace",s.textAlign="left",s.textBaseline="top",s.fillText("0",y,w+18),s.textAlign="right",s.fillText(g.toFixed(2),y+S,w+18),s.textAlign="left",s.fillText(`${v} measured · ${m} gaps · ${p} refused`,r.x,r.y+r.height+30),this.drawn=v>0}drawCross(e,t,n,s,r){const a=Math.min(s,r)*.28,o=t+s/2,l=n+r/2;e.strokeStyle=te.void,e.lineWidth=2,e.beginPath(),e.moveTo(o-a,l-a),e.lineTo(o+a,l+a),e.moveTo(o+a,l-a),e.lineTo(o-a,l+a),e.stroke()}}function Cb(i){return i>.62?te.bg:te.text_primary}class Rb{constructor(){G(this,"id","multiples");G(this,"name","Small multiples");G(this,"caption","One panel per cell: every seed's own curve, on the same accuracy scale.");G(this,"visible",!1);G(this,"drawn",!1)}enter(){this.visible=!0,Ht.show(),this.draw()}exit(){this.visible=!1,Ht.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}panels(){const e=Ue.axes,t=Pu(Ue.aggregates,e),n=al(t,e);return t.filter(s=>s.curves.length>0).map(s=>({cell:s,label:La(s,e,n),color:bn[s.coordinate.credit]??te.gradient,curves:s.curves}))}draw(){const e=this.panels();if(e.length===0){this.drawn=!1;return}const t=Ht.begin(),n=Ht.area(),s=Ue.chance,r=e.flatMap(y=>y.curves.flatMap(w=>w.map(O=>O.val_acc))),a=e.flatMap(y=>y.curves.flatMap(w=>w.map(O=>O.epoch)));let o=Math.min(s,...r),l=Math.max(s,...r);l-o<1e-6&&(o-=.05,l+=.05);const c=(l-o)*.14;o-=c,l+=c;const u=Math.max(1,...a),h=Math.ceil(Math.sqrt(e.length)),d=Math.ceil(e.length/h),f=18,g=n.width-f*(h-1),v=n.height-64-44-f*(d-1),m=g/h,p=v/d;gl(t,n,"Small multiples","every seed of every cell, on one accuracy scale"),e.forEach((y,w)=>{const O=w%h,A=Math.floor(w/h),P=n.x+O*(m+f),N=n.y+64+A*(p+f);t.fillStyle=y.color,t.font="600 13px 'JetBrains Mono', monospace",t.textAlign="left",t.textBaseline="alphabetic",t.fillText(y.label,P,N+12);const b={x:P+(O===0?44:10),y:N+30,width:m-(O===0?54:20),height:p-56};t.strokeStyle=te.border,t.lineWidth=1,t.strokeRect(b.x+.5,b.y+.5,b.width-1,b.height-1);const x=b.y+b.height*(1-(s-o)/(l-o));t.strokeStyle=te.chance_line,t.lineWidth=1,t.setLineDash([4,4]),t.beginPath(),t.moveTo(b.x,x),t.lineTo(b.x+b.width,x),t.stroke(),t.setLineDash([]),y.curves.forEach(R=>{t.strokeStyle=y.color,t.lineWidth=1.8,t.beginPath(),R.forEach((j,z)=>{const K=b.x+j.epoch/u*b.width,X=b.y+b.height*(1-(j.val_acc-o)/(l-o));z===0?t.moveTo(K,X):t.lineTo(K,X)}),t.stroke()}),t.fillStyle=te.text_muted,t.font="9px 'JetBrains Mono', monospace",O===0&&(t.textAlign="right",t.textBaseline="middle",[l,(l+o)/2,o].forEach(R=>{const j=b.y+b.height*(1-(R-o)/(l-o));t.fillText(R.toFixed(2),b.x-6,j)})),A===d-1&&(t.textAlign="left",t.textBaseline="top",t.fillText("epoch 0",b.x,b.y+b.height+6),t.textAlign="right",t.fillText(`epoch ${u}`,b.x+b.width,b.y+b.height+6))});const S=e.reduce((y,w)=>y+w.curves.length,0);Ba(t,n,`${e.length} cells · ${S} seeds · the dashed line is the chance level (${s.toFixed(2)})`),this.drawn=!0}}function Pb(i,e,t){let n=0;return i.forEach(s=>{const r=(e-s)/t;n+=Math.exp(-.5*r*r)}),n/(i.length*t*Math.sqrt(2*Math.PI))}function xf(i){if(i.length<2)return .02;const e=i.reduce((r,a)=>r+a,0)/i.length,t=i.reduce((r,a)=>r+(a-e)**2,0)/(i.length-1),s=1.06*Math.sqrt(t)*i.length**-.2;return Math.max(s,.01)}class Lb{constructor(){G(this,"id","spread");G(this,"name","The spread");G(this,"caption","One violin per arm, across its seeds: the width is the spread, not the mean.");G(this,"visible",!1);G(this,"drawn",!1)}enter(){this.visible=!0,Ht.show(),this.draw()}exit(){this.visible=!1,Ht.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}arms(){var n;const e=((n=Ue.metrics)==null?void 0:n.records)??[],t=new Map;return e.forEach(s=>{var l,c;const r=(l=s==null?void 0:s.payload)==null?void 0:l.val_acc,a=(c=s==null?void 0:s.coordinate)==null?void 0:c.credit;if(typeof r!="number"||!a)return;const o=t.get(a)??[];o.push(r),t.set(a,o)}),Array.from(t.entries()).map(([s,r])=>({name:s,values:r.slice().sort((a,o)=>a-o),color:bn[s]??te.gradient})).sort((s,r)=>s.name.localeCompare(r.name))}draw(){const e=this.arms();if(e.length===0){this.drawn=!1;return}const t=Ht.begin(),n=Ht.area(),s=Ue.chance,r=Ue.requiredSeeds,a=e.map(u=>{const h=xf(u.values);return{high:u.values[u.values.length-1]+1.5*h,low:u.values[0]-1.5*h}}),o=Math.max(s,...a.map(u=>u.high))*1.03,l=Mb(t,n,{yMin:0,yMax:o,categories:e.map(u=>u.name),title:"The spread",subtitle:"every seed of every arm, as a distribution",yLabel:"accuracy"}),c=l.rect.y+l.rect.height*(1-s/l.yMax);t.strokeStyle=te.chance_line,t.lineWidth=1.5,t.setLineDash([6,5]),t.beginPath(),t.moveTo(l.rect.x,c),t.lineTo(l.rect.x+l.rect.width,c),t.stroke(),t.setLineDash([]),t.save(),t.beginPath(),t.rect(l.rect.x,l.rect.y,l.rect.width,l.rect.height),t.clip(),e.forEach((u,h)=>{const d=l.band(h),f=Math.min(l.bandWidth*.36,90),g=xf(u.values),v=u.values[0]-1.5*g,m=u.values[u.values.length-1]+1.5*g,p=48,S=[];let y=0;for(let P=0;P<=p;P+=1){const N=v+(m-v)*P/p,b=Pb(u.values,N,g);S.push(b),y=Math.max(y,b)}const w=y>0?1/y:0,O=P=>l.rect.y+l.rect.height*(1-P/l.yMax);t.beginPath(),S.forEach((P,N)=>{const b=v+(m-v)*N/p,x=d+P*w*f,R=O(b);N===0?t.moveTo(x,R):t.lineTo(x,R)});for(let P=S.length-1;P>=0;P-=1){const N=v+(m-v)*P/p,b=d-S[P]*w*f;t.lineTo(b,O(N))}t.closePath(),t.fillStyle=`${u.color}33`,t.fill(),t.strokeStyle=u.color,t.lineWidth=1.5,t.stroke(),u.values.forEach((P,N)=>{const b=(N-(u.values.length-1)/2)*7;t.fillStyle=u.color,t.beginPath(),t.arc(d+b,O(P),3,0,Math.PI*2),t.fill()});const A=u.values.reduce((P,N)=>P+N,0)/u.values.length;t.strokeStyle=te.text_primary,t.lineWidth=1.5,t.beginPath(),t.moveTo(d-f,O(A)),t.lineTo(d+f,O(A)),t.stroke()}),t.restore(),e.forEach((u,h)=>{const d=Math.max(0,r-u.values.length);t.font="11px 'JetBrains Mono', monospace",t.textAlign="center",t.textBaseline="top",t.fillStyle=te.text_secondary,t.fillText(`${u.values.length} of ${r} seeds`,l.band(h),l.rect.y+l.rect.height+46),d>0&&(t.fillStyle=te.warn,t.fillText(`${d} short`,l.band(h),l.rect.y+l.rect.height+62))}),Ba(t,n,`the white line is each arm's mean · a claim needs ${r} seeds per group`),this.drawn=!0}}const gc=3.4,wr=1.15,Db=new k(.34,.4,.85);class Ib{constructor(){G(this,"id","terrain");G(this,"name","Terrain");G(this,"caption","The space as a heightfield: accuracy is the height, the gaps are flat, the refusals are craters.");G(this,"group",new as);G(this,"visible",!1);G(this,"drawn",!1);G(this,"framed",!1)}enter(){this.visible=!0;const e=Gr();e&&e.scene.add(this.group),this.draw(!0)}exit(){var e;this.visible=!1,(e=this.group.parent)==null||e.remove(this.group),nl(this.group),this.group=new as,this.drawn=!1,this.framed=!1}refresh(){this.visible&&this.draw(!1)}ready(){return this.drawn}columns(){const e=Ue.space;if(!e)return{columns:[],xValues:[],yValues:[]};const t=Ue.axes,n=e.values[t.x]??[],s=e.values[t.y]??[],r=e.values[t.z]??[],a=[];return n.forEach((o,l)=>{s.forEach((c,u)=>{let h=0,d=0,f=-1/0,g="";r.forEach(m=>{const p=Wr(o,c,m),S=Ue.spaceCells.get(p);if((S==null?void 0:S.status)==="void"){h+=1;return}d+=1;const y=Ue.aggregates.get(p);if(!y||y.acc.length===0)return;const w=Ns(y.acc);w>f&&(f=w,g=y.coordinate.credit??"")});const v=h>0&&d===0?"void":f>-1/0?"measured":"gap";a.push({status:v,accuracy:f>-1/0?f:0,arm:g,x:(l-(n.length-1)/2)*wr,y:(u-(s.length-1)/2)*wr})})}),{columns:a,xValues:n,yValues:s}}draw(e){const{columns:t,xValues:n,yValues:s}=this.columns();if(t.length===0){this.drawn=!1;return}this.clear();const r=Math.max(...t.map(f=>f.accuracy),1e-4),a=[],o=[],l=[];t.forEach(f=>{const g=f.status==="measured"?f.accuracy/r*gc:f.status==="void"?-1.1:0;a.push(f.x,g,f.y);const v=new nt(f.status==="measured"?bn[f.arm]||te.gradient:f.status==="void"?te.void:te.border_bright);if(f.status==="measured"){const m=.6+.4*(f.accuracy/r);v.multiplyScalar(m)}else f.status==="void"&&v.multiplyScalar(.55);o.push(v.r,v.g,v.b)});const c=n.length,u=s.length;for(let f=0;f<c-1;f+=1)for(let g=0;g<u-1;g+=1){const v=f*u+g,m=(f+1)*u+g,p=(f+1)*u+g+1,S=f*u+g+1;l.push(v,S,m,m,S,p)}const h=new Xt;h.setAttribute("position",new qt(a,3)),h.setAttribute("color",new qt(o,3)),h.setIndex(l),h.computeVertexNormals();const d=new gn(h,new Oo({vertexColors:!0,roughness:.7,metalness:.1,side:$n}));this.group.add(d),this.addVoidMarkers(t),this.addLabels(n,s),this.drawn=t.some(f=>f.status==="measured"),(e||!this.framed)&&(this.frame(t,n,s),this.framed=!0)}clear(){[...this.group.children].forEach(e=>{this.group.remove(e),nl(e)})}addVoidMarkers(e){const t=[];if(e.forEach(r=>{r.status==="void"&&t.push(r.x-.22,-1.1+.02,r.y-.22,r.x+.22,-1.1+.02,r.y+.22,r.x+.22,-1.1+.02,r.y-.22,r.x-.22,-1.1+.02,r.y+.22)}),t.length===0)return;const s=new Xt;s.setAttribute("position",new qt(t,3)),this.group.add(new Nr(s,new ki({color:te.void,transparent:!0,opacity:.75})))}addLabels(e,t){const n=new ks({color:13227232,sizeAttenuation:!0}),s=(e.length-1)*wr/2,r=(t.length-1)*wr/2,a=Mi(Ue.axes.x,.22,n);a.position.set(s+1,-.2,r+.9),this.group.add(a);const o=Mi(Ue.axes.y,.22,n);o.position.set(-s-1,.2,-r),this.group.add(o)}frame(e,t,n){const s=Gr();if(!s||e.length===0)return;const r=(t.length-1)*wr/2,a=(n.length-1)*wr/2;Ru(s,new k(-r-1.2,-1.1-.3,-a),new k(r+1.2,gc,a+1.4),new k(0,gc/3,0),Db)}}class Ub{constructor(){G(this,"id","uncertainty");G(this,"name","The uncertainty");G(this,"caption","Each cell's mean and the margin the gate asks for, against the chance level.");G(this,"visible",!1);G(this,"drawn",!1)}enter(){this.visible=!0,Ht.show(),this.draw()}exit(){this.visible=!1,Ht.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}sigma(){const e=Ue.gate;return e&&typeof e.superiority_margin_sigma=="number"?e.superiority_margin_sigma:2}intervals(){const e=Ue.axes,t=Ue.chance,n=this.sigma(),s=Pu(Ue.aggregates,e),r=al(s,e);return s.filter(a=>a.acc.length>0).map(a=>{const o=a.acc.length,l=a.acc.reduce((d,f)=>d+f,0)/o,c=a.acc.reduce((d,f)=>d+(f-l)**2,0)/Math.max(1,o-1),u=o>1?Math.sqrt(c/o):0,h=n*u;return{cell:a,label:La(a,e,r),color:bn[a.coordinate.credit]??te.gradient,mean:l,margin:h,lower:l-h,upper:l+h,threshold:t+h}}).sort((a,o)=>o.mean-a.mean)}draw(){const e=this.intervals();if(e.length===0){this.drawn=!1;return}const t=Ht.begin(),n=Ht.area(),s=Ue.chance,r=this.sigma(),a=Math.max(s,...e.map(u=>Math.max(u.upper,u.threshold))),o=$p(t,n,{xMin:0,xMax:a*1.12,rows:e.map(u=>u.label),title:"The uncertainty",subtitle:"each cell's mean, and the margin the gate asks for",xLabel:"accuracy"}),l=u=>o.rect.x+u/(o.xMax||1)*o.rect.width,c=l(s);t.strokeStyle=te.chance_line,t.lineWidth=1.5,t.setLineDash([6,5]),t.beginPath(),t.moveTo(c,o.rect.y),t.lineTo(c,o.rect.y+o.rect.height),t.stroke(),t.setLineDash([]),t.font="11px 'JetBrains Mono', monospace",t.textAlign="left",t.textBaseline="alphabetic",t.fillStyle=te.chance_line,t.fillText("chance",c+6,o.rect.y+14),e.forEach((u,h)=>{const d=o.rowY(h),f=u.lower>s;t.strokeStyle=u.color,t.lineWidth=3,t.beginPath(),t.moveTo(l(u.lower),d),t.lineTo(l(u.upper),d),t.stroke(),t.strokeStyle=f?te.ok:te.warn,t.lineWidth=2,t.beginPath(),t.moveTo(l(u.threshold),d-11),t.lineTo(l(u.threshold),d+11),t.stroke(),t.fillStyle=u.color,t.beginPath(),t.arc(l(u.mean),d,5,0,Math.PI*2),t.fill(),t.textAlign="left",t.textBaseline="middle",t.font="12px 'JetBrains Mono', monospace",t.fillStyle=f?te.ok:te.warn,t.fillText(f?"clears chance":"not yet separable",o.rect.x+o.rect.width+12,d)}),Ba(t,n,`the bar is ±${r}·SE · the tick is the threshold each cell has to clear · a claim needs ${Ue.requiredSeeds} seeds per cell`),this.drawn=!0}}class Nb{constructor(){G(this,"id","space");G(this,"name","Space");G(this,"caption","The declared space: the gaps as cages, the measured cells as pillars, the refusals as crosses.")}enter(){Us.show()}exit(){Us.hide()}refresh(e){Us.refreshView(e)}ready(){return Us.hasMeasured()}}class Fb{constructor(){G(this,"name","ViewSwitcher");G(this,"views",[]);G(this,"active",null);G(this,"selector",null);G(this,"captionElement",null);G(this,"section",null);G(this,"onKeyDown",e=>{if(e.metaKey||e.ctrlKey||e.altKey)return;const t=e.target;if(t&&["INPUT","SELECT","TEXTAREA"].includes(t.tagName))return;if(e.key.toLowerCase()==="v"){this.cycle();return}const s=Number.parseInt(e.key,10)-1;!Number.isNaN(s)&&s>=0&&s<this.views.length&&this.show(this.views[s].id)});this.views=[new Nb,new Ib,new Eb,new Ab,new bb,new Rb,new Lb,new Sb,new Ub]}async init(){window.addEventListener("keydown",this.onKeyDown),Ue.onChange(e=>{var t;return(t=this.active)==null?void 0:t.refresh(e)}),this.buildSection(),this.attachSection(),this.show(this.views[0].id),console.log("[ViewSwitcher] Initialized")}async destroy(){var e,t;window.removeEventListener("keydown",this.onKeyDown),(e=this.active)==null||e.exit(),this.active=null,(t=this.section)==null||t.remove(),this.section=null}get activeId(){var e;return((e=this.active)==null?void 0:e.id)??null}isReady(e){const t=this.views.find(n=>n.id===e);return t?t.ready():!1}show(e){var n;const t=this.views.find(s=>s.id===e);!t||t===this.active||((n=this.active)==null||n.exit(),this.active=t,t.enter(),this.updateSelector(),this.updateLegend())}cycle(){if(this.views.length===0)return;const e=this.views.findIndex(n=>n===this.active),t=this.views[(e+1)%this.views.length];this.show(t.id)}buildSection(){const e=document.createElement("div");e.id="legend-view-section",e.style.cssText="margin-bottom: 12px;";const t=document.createElement("div");t.textContent="View",t.style.cssText="font-weight: 600; margin-bottom: 8px;",e.appendChild(t);const n=document.createElement("select");n.id="view-picker",n.style.cssText=`
      width: 100%;
      background: var(--bg-tertiary);
      color: var(--text-primary);
      border: 1px solid var(--border);
      border-radius: 4px;
      font-size: 11px;
      padding: 2px 4px;
    `,this.views.forEach(a=>{const o=document.createElement("option");o.value=a.id,o.textContent=a.name,n.appendChild(o)}),n.addEventListener("change",()=>this.show(n.value)),e.appendChild(n),this.selector=n;const s=document.createElement("div");s.id="view-caption",s.style.cssText="font-size: 11px; color: var(--text-secondary); margin-top: 8px;",e.appendChild(s),this.captionElement=s;const r=document.createElement("div");r.textContent=`V cycles · 1–${this.views.length} pick`,r.style.cssText="font-size: 10px; color: var(--text-muted); margin-top: 6px;",e.appendChild(r),this.section=e}attachSection(e=0){const t=document.getElementById("legend-view");if(!t){e<50&&window.setTimeout(()=>this.attachSection(e+1),100);return}this.section&&this.section.parentElement!==t&&t.appendChild(this.section),this.updateSelector(),this.updateLegend()}updateSelector(){!this.selector||!this.active||(this.selector.value=this.active.id)}updateLegend(){if(!this.active)return;const e=document.getElementById("legend-title");e&&(e.textContent=this.active.name);const t=document.getElementById("legend-marks");t&&(t.style.display=this.active.id==="space"?"":"none"),this.captionElement&&(this.captionElement.textContent=this.active.caption)}}const jp=new Fb;Wi.register(jp);const Ob=/swiftshader|llvmpipe|software|basic render/i;function Bb(){const i=zb();return{software:i,fps:i?12:60,shadows:!i,antialias:!i}}function zb(){try{const i=document.createElement("canvas"),e=i.getContext("webgl2")??i.getContext("webgl");if(!e)return!0;const t=e.getExtension("WEBGL_debug_renderer_info"),n=String(t?e.getParameter(t.UNMASKED_RENDERER_WEBGL):e.getParameter(e.RENDERER));return Ob.test(n)}catch{return!0}}window.addEventListener("error",i=>{var e;console.error("[Global Error]",i.error),Zp(((e=i.error)==null?void 0:e.message)||"Unknown error")});window.addEventListener("unhandledrejection",i=>{var e;console.error("[Unhandled Rejection]",i.reason),Zp(((e=i.reason)==null?void 0:e.message)||"Unhandled promise rejection")});let Ni=null,ns=null;function Kp(i="Initializing dashboard..."){const e=document.getElementById("ui-overlay");e&&(Ni=document.createElement("div"),Ni.id="global-loading",Ni.style.cssText=`
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
  `,Ni.innerHTML=`
    <div style="
      width: 48px;
      height: 48px;
      border: 3px solid var(--border);
      border-top-color: ${te.gradient};
      border-radius: 50%;
      animation: spin 1s linear infinite;
    "></div>
    <div style="font-size: 14px; color: var(--text-primary);">${i}</div>
    <style>
      @keyframes spin { to { transform: rotate(360deg); } }
    </style>
  `,e.appendChild(Ni))}function yf(){Ni==null||Ni.remove(),Ni=null}function Zp(i){const e=document.getElementById("ui-overlay");e&&(ns=document.createElement("div"),ns.id="global-error",ns.style.cssText=`
    position: fixed;
    top: 20px;
    right: 20px;
    background: ${te.error}22;
    border: 1px solid ${te.error}88;
    border-radius: 8px;
    padding: 16px 24px;
    color: ${te.error};
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    z-index: 1000;
    max-width: 400px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    display: flex;
    align-items: center;
    gap: 12px;
  `,ns.innerHTML=`
    <span>✗</span>
    <span>${i}</span>
    <button onclick="this.parentElement.remove()" style="
      background: none;
      border: none;
      color: ${te.error};
      font-size: 18px;
      cursor: pointer;
      line-height: 1;
      padding: 0 4px;
    ">&times;</button>
  `,e.appendChild(ns),setTimeout(()=>ns==null?void 0:ns.remove(),1e4))}Vr.connect();Kp("Connecting to dashboard...");Vr.waitForConnection(15e3).then(i=>{i?yf():(Kp("Connection timeout — retrying..."),Vr.onStateChange(e=>{e==="connected"&&yf()}))});const kb={p:"pareto",a:"ablation",s:"variability"};window.addEventListener("keydown",i=>{if(i.metaKey||i.ctrlKey||i.altKey)return;const e=kb[i.key];if(e){Xu.showTab(e);return}const t=i.key.toLowerCase();t==="h"&&ml.toggle(),t==="l"&&qu.toggle(),t==="c"&&Yu.toggle()});const Hb=document.getElementById("dashboard-canvas"),ea=Bb(),Zn=new Qf({canvas:Hb,antialias:ea.antialias,alpha:!0,powerPreference:"high-performance"});Zn.setSize(window.innerWidth,window.innerHeight);Zn.setPixelRatio(ea.software?1:Math.min(window.devicePixelRatio,2));Zn.shadowMap.enabled=ea.shadows;Zn.shadowMap.type=Sf;Zn.toneMapping=Ef;Zn.toneMappingExposure=1.2;const Xi=new Eu;Xi.background=new nt(658964);Xi.fog=new bu(658964,.015);const ds=new Sn(60,window.innerWidth/window.innerHeight,.1,200);ds.position.set(3.3,4.4,8.8);ds.lookAt(0,1,.1);const bi=new eM(ds,Zn.domElement);bi.target.set(0,1,.1);bi.enableDamping=!0;bi.dampingFactor=.05;bi.enablePan=!0;bi.minDistance=5;bi.maxDistance=80;bi.maxPolarAngle=Math.PI/2-.05;iM({scene:Xi,camera:ds,renderer:Zn,controls:bi});const Vb=new Wy(4473958,.6);Xi.add(Vb);const hi=new Gy(16777215,1.2);hi.position.set(10,20,10);hi.castShadow=ea.shadows;hi.shadow.mapSize.width=2048;hi.shadow.mapSize.height=2048;hi.shadow.camera.near=1;hi.shadow.camera.far=50;hi.shadow.camera.left=-20;hi.shadow.camera.right=20;hi.shadow.camera.top=20;hi.shadow.camera.bottom=-20;Xi.add(hi);const Gb=new ky(8956671,2236979,.5);Xi.add(Gb);const ju=new qy(8,8,2371648,1449256);ju.position.y=-.01;const Jp=ju.material;Jp.transparent=!0;Jp.opacity=.35;Xi.add(ju);function Wb(){ds.aspect=window.innerWidth/window.innerHeight,ds.updateProjectionMatrix(),Zn.setSize(window.innerWidth,window.innerHeight),Zn.setPixelRatio(ea.software?1:Math.min(window.devicePixelRatio,2))}window.addEventListener("resize",Wb);const Xb=1e3/ea.fps;let _c=0;function Qp(i){if(requestAnimationFrame(Qp),i-_c<Xb)return;const e=(i-_c)/1e3;_c=i,bi.update(),Us.update(e),ml.update(e),Zn.render(Xi,ds)}requestAnimationFrame(Qp);window.__DASHBOARD__={scene:Xi,camera:ds,renderer:Zn,controls:bi,discoveryMap:Us,cellDrawer:op,plotter:Xu,liveRail:qu,caption:Yu,hud:ml,viewSwitcher:jp,wsClient:Vr,router:Zt};console.log("🚀 Computronium Dashboard initialized");
//# sourceMappingURL=dashboard.js.map
