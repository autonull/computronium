var ym=Object.defineProperty;var bm=(i,e,t)=>e in i?ym(i,e,{enumerable:!0,configurable:!0,writable:!0,value:t}):i[e]=t;var R=(i,e,t)=>bm(i,typeof e!="symbol"?e+"":e,t);/**
 * @license
 * Copyright 2010-2024 Three.js Authors
 * SPDX-License-Identifier: MIT
 */const mu="168",or={ROTATE:0,DOLLY:1,PAN:2},lr={ROTATE:0,PAN:1,DOLLY_PAN:2,DOLLY_ROTATE:3},Sm=0,ph=1,Mm=2,bf=1,Sf=2,Bi=3,hs=0,Nn=1,Ei=2,ls=0,Ur=1,mh=2,gh=3,vh=4,wm=5,Ns=100,Em=101,Tm=102,Am=103,Cm=104,Rm=200,Pm=201,Lm=202,Dm=203,xc=204,yc=205,Im=206,Um=207,Nm=208,Om=209,Fm=210,km=211,Bm=212,zm=213,Hm=214,Vm=0,Gm=1,Wm=2,Bo=3,qm=4,Xm=5,$m=6,Ym=7,Mf=0,jm=1,Km=2,cs=0,Zm=1,Jm=2,Qm=3,wf=4,eg=5,tg=6,ng=7,Ef=300,zr=301,Hr=302,bc=303,Sc=304,nl=306,Mc=1e3,ks=1001,wc=1002,ei=1003,ig=1004,Ya=1005,ui=1006,Pl=1007,Bs=1008,$i=1009,Tf=1010,Af=1011,Ua=1012,gu=1013,Vs=1014,Hi=1015,ka=1016,vu=1017,_u=1018,Vr=1020,Cf=35902,Rf=1021,Pf=1022,fi=1023,Lf=1024,Df=1025,Nr=1026,Gr=1027,If=1028,xu=1029,Uf=1030,yu=1031,bu=1033,Lo=33776,Do=33777,Io=33778,Uo=33779,Ec=35840,Tc=35841,Ac=35842,Cc=35843,Rc=36196,Pc=37492,Lc=37496,Dc=37808,Ic=37809,Uc=37810,Nc=37811,Oc=37812,Fc=37813,kc=37814,Bc=37815,zc=37816,Hc=37817,Vc=37818,Gc=37819,Wc=37820,qc=37821,No=36492,Xc=36494,$c=36495,Nf=36283,Yc=36284,jc=36285,Kc=36286,sg=3200,rg=3201,Of=0,ag=1,os="",Mi="srgb",gs="srgb-linear",Su="display-p3",il="display-p3-linear",zo="linear",Bt="srgb",Ho="rec709",Vo="p3",cr=7680,_h=519,og=512,lg=513,cg=514,Ff=515,ug=516,hg=517,dg=518,fg=519,Zc=35044,xh="300 es",Vi=2e3,Go=2001;let Kr=class{addEventListener(e,t){this._listeners===void 0&&(this._listeners={});const n=this._listeners;n[e]===void 0&&(n[e]=[]),n[e].indexOf(t)===-1&&n[e].push(t)}hasEventListener(e,t){if(this._listeners===void 0)return!1;const n=this._listeners;return n[e]!==void 0&&n[e].indexOf(t)!==-1}removeEventListener(e,t){if(this._listeners===void 0)return;const s=this._listeners[e];if(s!==void 0){const r=s.indexOf(t);r!==-1&&s.splice(r,1)}}dispatchEvent(e){if(this._listeners===void 0)return;const n=this._listeners[e.type];if(n!==void 0){e.target=this;const s=n.slice(0);for(let r=0,o=s.length;r<o;r++)s[r].call(this,e);e.target=null}}};const xn=["00","01","02","03","04","05","06","07","08","09","0a","0b","0c","0d","0e","0f","10","11","12","13","14","15","16","17","18","19","1a","1b","1c","1d","1e","1f","20","21","22","23","24","25","26","27","28","29","2a","2b","2c","2d","2e","2f","30","31","32","33","34","35","36","37","38","39","3a","3b","3c","3d","3e","3f","40","41","42","43","44","45","46","47","48","49","4a","4b","4c","4d","4e","4f","50","51","52","53","54","55","56","57","58","59","5a","5b","5c","5d","5e","5f","60","61","62","63","64","65","66","67","68","69","6a","6b","6c","6d","6e","6f","70","71","72","73","74","75","76","77","78","79","7a","7b","7c","7d","7e","7f","80","81","82","83","84","85","86","87","88","89","8a","8b","8c","8d","8e","8f","90","91","92","93","94","95","96","97","98","99","9a","9b","9c","9d","9e","9f","a0","a1","a2","a3","a4","a5","a6","a7","a8","a9","aa","ab","ac","ad","ae","af","b0","b1","b2","b3","b4","b5","b6","b7","b8","b9","ba","bb","bc","bd","be","bf","c0","c1","c2","c3","c4","c5","c6","c7","c8","c9","ca","cb","cc","cd","ce","cf","d0","d1","d2","d3","d4","d5","d6","d7","d8","d9","da","db","dc","dd","de","df","e0","e1","e2","e3","e4","e5","e6","e7","e8","e9","ea","eb","ec","ed","ee","ef","f0","f1","f2","f3","f4","f5","f6","f7","f8","f9","fa","fb","fc","fd","fe","ff"];let yh=1234567;const Or=Math.PI/180,Na=180/Math.PI;function Wi(){const i=Math.random()*4294967295|0,e=Math.random()*4294967295|0,t=Math.random()*4294967295|0,n=Math.random()*4294967295|0;return(xn[i&255]+xn[i>>8&255]+xn[i>>16&255]+xn[i>>24&255]+"-"+xn[e&255]+xn[e>>8&255]+"-"+xn[e>>16&15|64]+xn[e>>24&255]+"-"+xn[t&63|128]+xn[t>>8&255]+"-"+xn[t>>16&255]+xn[t>>24&255]+xn[n&255]+xn[n>>8&255]+xn[n>>16&255]+xn[n>>24&255]).toLowerCase()}function bn(i,e,t){return Math.max(e,Math.min(t,i))}function Mu(i,e){return(i%e+e)%e}function pg(i,e,t,n,s){return n+(i-e)*(s-n)/(t-e)}function mg(i,e,t){return i!==e?(t-i)/(e-i):0}function Ea(i,e,t){return(1-t)*i+t*e}function gg(i,e,t,n){return Ea(i,e,1-Math.exp(-t*n))}function vg(i,e=1){return e-Math.abs(Mu(i,e*2)-e)}function _g(i,e,t){return i<=e?0:i>=t?1:(i=(i-e)/(t-e),i*i*(3-2*i))}function xg(i,e,t){return i<=e?0:i>=t?1:(i=(i-e)/(t-e),i*i*i*(i*(i*6-15)+10))}function yg(i,e){return i+Math.floor(Math.random()*(e-i+1))}function bg(i,e){return i+Math.random()*(e-i)}function Sg(i){return i*(.5-Math.random())}function Mg(i){i!==void 0&&(yh=i);let e=yh+=1831565813;return e=Math.imul(e^e>>>15,e|1),e^=e+Math.imul(e^e>>>7,e|61),((e^e>>>14)>>>0)/4294967296}function wg(i){return i*Or}function Eg(i){return i*Na}function Tg(i){return(i&i-1)===0&&i!==0}function Ag(i){return Math.pow(2,Math.ceil(Math.log(i)/Math.LN2))}function Cg(i){return Math.pow(2,Math.floor(Math.log(i)/Math.LN2))}function Rg(i,e,t,n,s){const r=Math.cos,o=Math.sin,a=r(t/2),l=o(t/2),c=r((e+n)/2),u=o((e+n)/2),h=r((e-n)/2),d=o((e-n)/2),f=r((n-e)/2),v=o((n-e)/2);switch(s){case"XYX":i.set(a*u,l*h,l*d,a*c);break;case"YZY":i.set(l*d,a*u,l*h,a*c);break;case"ZXZ":i.set(l*h,l*d,a*u,a*c);break;case"XZX":i.set(a*u,l*v,l*f,a*c);break;case"YXY":i.set(l*f,a*u,l*v,a*c);break;case"ZYZ":i.set(l*v,l*f,a*u,a*c);break;default:console.warn("THREE.MathUtils: .setQuaternionFromProperEuler() encountered an unknown order: "+s)}}function hi(i,e){switch(e.constructor){case Float32Array:return i;case Uint32Array:return i/4294967295;case Uint16Array:return i/65535;case Uint8Array:return i/255;case Int32Array:return Math.max(i/2147483647,-1);case Int16Array:return Math.max(i/32767,-1);case Int8Array:return Math.max(i/127,-1);default:throw new Error("Invalid component type.")}}function At(i,e){switch(e.constructor){case Float32Array:return i;case Uint32Array:return Math.round(i*4294967295);case Uint16Array:return Math.round(i*65535);case Uint8Array:return Math.round(i*255);case Int32Array:return Math.round(i*2147483647);case Int16Array:return Math.round(i*32767);case Int8Array:return Math.round(i*127);default:throw new Error("Invalid component type.")}}const Pg={DEG2RAD:Or,RAD2DEG:Na,generateUUID:Wi,clamp:bn,euclideanModulo:Mu,mapLinear:pg,inverseLerp:mg,lerp:Ea,damp:gg,pingpong:vg,smoothstep:_g,smootherstep:xg,randInt:yg,randFloat:bg,randFloatSpread:Sg,seededRandom:Mg,degToRad:wg,radToDeg:Eg,isPowerOfTwo:Tg,ceilPowerOfTwo:Ag,floorPowerOfTwo:Cg,setQuaternionFromProperEuler:Rg,normalize:At,denormalize:hi};class qe{constructor(e=0,t=0){qe.prototype.isVector2=!0,this.x=e,this.y=t}get width(){return this.x}set width(e){this.x=e}get height(){return this.y}set height(e){this.y=e}set(e,t){return this.x=e,this.y=t,this}setScalar(e){return this.x=e,this.y=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y)}copy(e){return this.x=e.x,this.y=e.y,this}add(e){return this.x+=e.x,this.y+=e.y,this}addScalar(e){return this.x+=e,this.y+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this}subScalar(e){return this.x-=e,this.y-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this}multiply(e){return this.x*=e.x,this.y*=e.y,this}multiplyScalar(e){return this.x*=e,this.y*=e,this}divide(e){return this.x/=e.x,this.y/=e.y,this}divideScalar(e){return this.multiplyScalar(1/e)}applyMatrix3(e){const t=this.x,n=this.y,s=e.elements;return this.x=s[0]*t+s[3]*n+s[6],this.y=s[1]*t+s[4]*n+s[7],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this}negate(){return this.x=-this.x,this.y=-this.y,this}dot(e){return this.x*e.x+this.y*e.y}cross(e){return this.x*e.y-this.y*e.x}lengthSq(){return this.x*this.x+this.y*this.y}length(){return Math.sqrt(this.x*this.x+this.y*this.y)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)}normalize(){return this.divideScalar(this.length()||1)}angle(){return Math.atan2(-this.y,-this.x)+Math.PI}angleTo(e){const t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;const n=this.dot(e)/t;return Math.acos(bn(n,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){const t=this.x-e.x,n=this.y-e.y;return t*t+n*n}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this}equals(e){return e.x===this.x&&e.y===this.y}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this}rotateAround(e,t){const n=Math.cos(t),s=Math.sin(t),r=this.x-e.x,o=this.y-e.y;return this.x=r*n-o*s+e.x,this.y=r*s+o*n+e.y,this}random(){return this.x=Math.random(),this.y=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y}}class at{constructor(e,t,n,s,r,o,a,l,c){at.prototype.isMatrix3=!0,this.elements=[1,0,0,0,1,0,0,0,1],e!==void 0&&this.set(e,t,n,s,r,o,a,l,c)}set(e,t,n,s,r,o,a,l,c){const u=this.elements;return u[0]=e,u[1]=s,u[2]=a,u[3]=t,u[4]=r,u[5]=l,u[6]=n,u[7]=o,u[8]=c,this}identity(){return this.set(1,0,0,0,1,0,0,0,1),this}copy(e){const t=this.elements,n=e.elements;return t[0]=n[0],t[1]=n[1],t[2]=n[2],t[3]=n[3],t[4]=n[4],t[5]=n[5],t[6]=n[6],t[7]=n[7],t[8]=n[8],this}extractBasis(e,t,n){return e.setFromMatrix3Column(this,0),t.setFromMatrix3Column(this,1),n.setFromMatrix3Column(this,2),this}setFromMatrix4(e){const t=e.elements;return this.set(t[0],t[4],t[8],t[1],t[5],t[9],t[2],t[6],t[10]),this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){const n=e.elements,s=t.elements,r=this.elements,o=n[0],a=n[3],l=n[6],c=n[1],u=n[4],h=n[7],d=n[2],f=n[5],v=n[8],g=s[0],m=s[3],p=s[6],x=s[1],b=s[4],w=s[7],O=s[2],A=s[5],L=s[8];return r[0]=o*g+a*x+l*O,r[3]=o*m+a*b+l*A,r[6]=o*p+a*w+l*L,r[1]=c*g+u*x+h*O,r[4]=c*m+u*b+h*A,r[7]=c*p+u*w+h*L,r[2]=d*g+f*x+v*O,r[5]=d*m+f*b+v*A,r[8]=d*p+f*w+v*L,this}multiplyScalar(e){const t=this.elements;return t[0]*=e,t[3]*=e,t[6]*=e,t[1]*=e,t[4]*=e,t[7]*=e,t[2]*=e,t[5]*=e,t[8]*=e,this}determinant(){const e=this.elements,t=e[0],n=e[1],s=e[2],r=e[3],o=e[4],a=e[5],l=e[6],c=e[7],u=e[8];return t*o*u-t*a*c-n*r*u+n*a*l+s*r*c-s*o*l}invert(){const e=this.elements,t=e[0],n=e[1],s=e[2],r=e[3],o=e[4],a=e[5],l=e[6],c=e[7],u=e[8],h=u*o-a*c,d=a*l-u*r,f=c*r-o*l,v=t*h+n*d+s*f;if(v===0)return this.set(0,0,0,0,0,0,0,0,0);const g=1/v;return e[0]=h*g,e[1]=(s*c-u*n)*g,e[2]=(a*n-s*o)*g,e[3]=d*g,e[4]=(u*t-s*l)*g,e[5]=(s*r-a*t)*g,e[6]=f*g,e[7]=(n*l-c*t)*g,e[8]=(o*t-n*r)*g,this}transpose(){let e;const t=this.elements;return e=t[1],t[1]=t[3],t[3]=e,e=t[2],t[2]=t[6],t[6]=e,e=t[5],t[5]=t[7],t[7]=e,this}getNormalMatrix(e){return this.setFromMatrix4(e).invert().transpose()}transposeIntoArray(e){const t=this.elements;return e[0]=t[0],e[1]=t[3],e[2]=t[6],e[3]=t[1],e[4]=t[4],e[5]=t[7],e[6]=t[2],e[7]=t[5],e[8]=t[8],this}setUvTransform(e,t,n,s,r,o,a){const l=Math.cos(r),c=Math.sin(r);return this.set(n*l,n*c,-n*(l*o+c*a)+o+e,-s*c,s*l,-s*(-c*o+l*a)+a+t,0,0,1),this}scale(e,t){return this.premultiply(Ll.makeScale(e,t)),this}rotate(e){return this.premultiply(Ll.makeRotation(-e)),this}translate(e,t){return this.premultiply(Ll.makeTranslation(e,t)),this}makeTranslation(e,t){return e.isVector2?this.set(1,0,e.x,0,1,e.y,0,0,1):this.set(1,0,e,0,1,t,0,0,1),this}makeRotation(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,-n,0,n,t,0,0,0,1),this}makeScale(e,t){return this.set(e,0,0,0,t,0,0,0,1),this}equals(e){const t=this.elements,n=e.elements;for(let s=0;s<9;s++)if(t[s]!==n[s])return!1;return!0}fromArray(e,t=0){for(let n=0;n<9;n++)this.elements[n]=e[n+t];return this}toArray(e=[],t=0){const n=this.elements;return e[t]=n[0],e[t+1]=n[1],e[t+2]=n[2],e[t+3]=n[3],e[t+4]=n[4],e[t+5]=n[5],e[t+6]=n[6],e[t+7]=n[7],e[t+8]=n[8],e}clone(){return new this.constructor().fromArray(this.elements)}}const Ll=new at;function kf(i){for(let e=i.length-1;e>=0;--e)if(i[e]>=65535)return!0;return!1}function Wo(i){return document.createElementNS("http://www.w3.org/1999/xhtml",i)}function Lg(){const i=Wo("canvas");return i.style.display="block",i}const bh={};function Fr(i){i in bh||(bh[i]=!0,console.warn(i))}function Dg(i,e,t){return new Promise(function(n,s){function r(){switch(i.clientWaitSync(e,i.SYNC_FLUSH_COMMANDS_BIT,0)){case i.WAIT_FAILED:s();break;case i.TIMEOUT_EXPIRED:setTimeout(r,t);break;default:n()}}setTimeout(r,t)})}const Sh=new at().set(.8224621,.177538,0,.0331941,.9668058,0,.0170827,.0723974,.9105199),Mh=new at().set(1.2249401,-.2249404,0,-.0420569,1.0420571,0,-.0196376,-.0786361,1.0982735),ua={[gs]:{transfer:zo,primaries:Ho,luminanceCoefficients:[.2126,.7152,.0722],toReference:i=>i,fromReference:i=>i},[Mi]:{transfer:Bt,primaries:Ho,luminanceCoefficients:[.2126,.7152,.0722],toReference:i=>i.convertSRGBToLinear(),fromReference:i=>i.convertLinearToSRGB()},[il]:{transfer:zo,primaries:Vo,luminanceCoefficients:[.2289,.6917,.0793],toReference:i=>i.applyMatrix3(Mh),fromReference:i=>i.applyMatrix3(Sh)},[Su]:{transfer:Bt,primaries:Vo,luminanceCoefficients:[.2289,.6917,.0793],toReference:i=>i.convertSRGBToLinear().applyMatrix3(Mh),fromReference:i=>i.applyMatrix3(Sh).convertLinearToSRGB()}},Ig=new Set([gs,il]),wt={enabled:!0,_workingColorSpace:gs,get workingColorSpace(){return this._workingColorSpace},set workingColorSpace(i){if(!Ig.has(i))throw new Error(`Unsupported working color space, "${i}".`);this._workingColorSpace=i},convert:function(i,e,t){if(this.enabled===!1||e===t||!e||!t)return i;const n=ua[e].toReference,s=ua[t].fromReference;return s(n(i))},fromWorkingColorSpace:function(i,e){return this.convert(i,this._workingColorSpace,e)},toWorkingColorSpace:function(i,e){return this.convert(i,e,this._workingColorSpace)},getPrimaries:function(i){return ua[i].primaries},getTransfer:function(i){return i===os?zo:ua[i].transfer},getLuminanceCoefficients:function(i,e=this._workingColorSpace){return i.fromArray(ua[e].luminanceCoefficients)}};function kr(i){return i<.04045?i*.0773993808:Math.pow(i*.9478672986+.0521327014,2.4)}function Dl(i){return i<.0031308?i*12.92:1.055*Math.pow(i,.41666)-.055}let ur;class Ug{static getDataURL(e){if(/^data:/i.test(e.src)||typeof HTMLCanvasElement>"u")return e.src;let t;if(e instanceof HTMLCanvasElement)t=e;else{ur===void 0&&(ur=Wo("canvas")),ur.width=e.width,ur.height=e.height;const n=ur.getContext("2d");e instanceof ImageData?n.putImageData(e,0,0):n.drawImage(e,0,0,e.width,e.height),t=ur}return t.width>2048||t.height>2048?(console.warn("THREE.ImageUtils.getDataURL: Image converted to jpg for performance reasons",e),t.toDataURL("image/jpeg",.6)):t.toDataURL("image/png")}static sRGBToLinear(e){if(typeof HTMLImageElement<"u"&&e instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&e instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&e instanceof ImageBitmap){const t=Wo("canvas");t.width=e.width,t.height=e.height;const n=t.getContext("2d");n.drawImage(e,0,0,e.width,e.height);const s=n.getImageData(0,0,e.width,e.height),r=s.data;for(let o=0;o<r.length;o++)r[o]=kr(r[o]/255)*255;return n.putImageData(s,0,0),t}else if(e.data){const t=e.data.slice(0);for(let n=0;n<t.length;n++)t instanceof Uint8Array||t instanceof Uint8ClampedArray?t[n]=Math.floor(kr(t[n]/255)*255):t[n]=kr(t[n]);return{data:t,width:e.width,height:e.height}}else return console.warn("THREE.ImageUtils.sRGBToLinear(): Unsupported image type. No color space conversion applied."),e}}let Ng=0;class Bf{constructor(e=null){this.isSource=!0,Object.defineProperty(this,"id",{value:Ng++}),this.uuid=Wi(),this.data=e,this.dataReady=!0,this.version=0}set needsUpdate(e){e===!0&&this.version++}toJSON(e){const t=e===void 0||typeof e=="string";if(!t&&e.images[this.uuid]!==void 0)return e.images[this.uuid];const n={uuid:this.uuid,url:""},s=this.data;if(s!==null){let r;if(Array.isArray(s)){r=[];for(let o=0,a=s.length;o<a;o++)s[o].isDataTexture?r.push(Il(s[o].image)):r.push(Il(s[o]))}else r=Il(s);n.url=r}return t||(e.images[this.uuid]=n),n}}function Il(i){return typeof HTMLImageElement<"u"&&i instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&i instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&i instanceof ImageBitmap?Ug.getDataURL(i):i.data?{data:Array.from(i.data),width:i.width,height:i.height,type:i.data.constructor.name}:(console.warn("THREE.Texture: Unable to serialize Texture."),{})}let Og=0;class Dn extends Kr{constructor(e=Dn.DEFAULT_IMAGE,t=Dn.DEFAULT_MAPPING,n=ks,s=ks,r=ui,o=Bs,a=fi,l=$i,c=Dn.DEFAULT_ANISOTROPY,u=os){super(),this.isTexture=!0,Object.defineProperty(this,"id",{value:Og++}),this.uuid=Wi(),this.name="",this.source=new Bf(e),this.mipmaps=[],this.mapping=t,this.channel=0,this.wrapS=n,this.wrapT=s,this.magFilter=r,this.minFilter=o,this.anisotropy=c,this.format=a,this.internalFormat=null,this.type=l,this.offset=new qe(0,0),this.repeat=new qe(1,1),this.center=new qe(0,0),this.rotation=0,this.matrixAutoUpdate=!0,this.matrix=new at,this.generateMipmaps=!0,this.premultiplyAlpha=!1,this.flipY=!0,this.unpackAlignment=4,this.colorSpace=u,this.userData={},this.version=0,this.onUpdate=null,this.isRenderTargetTexture=!1,this.pmremVersion=0}get image(){return this.source.data}set image(e=null){this.source.data=e}updateMatrix(){this.matrix.setUvTransform(this.offset.x,this.offset.y,this.repeat.x,this.repeat.y,this.rotation,this.center.x,this.center.y)}clone(){return new this.constructor().copy(this)}copy(e){return this.name=e.name,this.source=e.source,this.mipmaps=e.mipmaps.slice(0),this.mapping=e.mapping,this.channel=e.channel,this.wrapS=e.wrapS,this.wrapT=e.wrapT,this.magFilter=e.magFilter,this.minFilter=e.minFilter,this.anisotropy=e.anisotropy,this.format=e.format,this.internalFormat=e.internalFormat,this.type=e.type,this.offset.copy(e.offset),this.repeat.copy(e.repeat),this.center.copy(e.center),this.rotation=e.rotation,this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrix.copy(e.matrix),this.generateMipmaps=e.generateMipmaps,this.premultiplyAlpha=e.premultiplyAlpha,this.flipY=e.flipY,this.unpackAlignment=e.unpackAlignment,this.colorSpace=e.colorSpace,this.userData=JSON.parse(JSON.stringify(e.userData)),this.needsUpdate=!0,this}toJSON(e){const t=e===void 0||typeof e=="string";if(!t&&e.textures[this.uuid]!==void 0)return e.textures[this.uuid];const n={metadata:{version:4.6,type:"Texture",generator:"Texture.toJSON"},uuid:this.uuid,name:this.name,image:this.source.toJSON(e).uuid,mapping:this.mapping,channel:this.channel,repeat:[this.repeat.x,this.repeat.y],offset:[this.offset.x,this.offset.y],center:[this.center.x,this.center.y],rotation:this.rotation,wrap:[this.wrapS,this.wrapT],format:this.format,internalFormat:this.internalFormat,type:this.type,colorSpace:this.colorSpace,minFilter:this.minFilter,magFilter:this.magFilter,anisotropy:this.anisotropy,flipY:this.flipY,generateMipmaps:this.generateMipmaps,premultiplyAlpha:this.premultiplyAlpha,unpackAlignment:this.unpackAlignment};return Object.keys(this.userData).length>0&&(n.userData=this.userData),t||(e.textures[this.uuid]=n),n}dispose(){this.dispatchEvent({type:"dispose"})}transformUv(e){if(this.mapping!==Ef)return e;if(e.applyMatrix3(this.matrix),e.x<0||e.x>1)switch(this.wrapS){case Mc:e.x=e.x-Math.floor(e.x);break;case ks:e.x=e.x<0?0:1;break;case wc:Math.abs(Math.floor(e.x)%2)===1?e.x=Math.ceil(e.x)-e.x:e.x=e.x-Math.floor(e.x);break}if(e.y<0||e.y>1)switch(this.wrapT){case Mc:e.y=e.y-Math.floor(e.y);break;case ks:e.y=e.y<0?0:1;break;case wc:Math.abs(Math.floor(e.y)%2)===1?e.y=Math.ceil(e.y)-e.y:e.y=e.y-Math.floor(e.y);break}return this.flipY&&(e.y=1-e.y),e}set needsUpdate(e){e===!0&&(this.version++,this.source.needsUpdate=!0)}set needsPMREMUpdate(e){e===!0&&this.pmremVersion++}}Dn.DEFAULT_IMAGE=null;Dn.DEFAULT_MAPPING=Ef;Dn.DEFAULT_ANISOTROPY=1;class en{constructor(e=0,t=0,n=0,s=1){en.prototype.isVector4=!0,this.x=e,this.y=t,this.z=n,this.w=s}get width(){return this.z}set width(e){this.z=e}get height(){return this.w}set height(e){this.w=e}set(e,t,n,s){return this.x=e,this.y=t,this.z=n,this.w=s,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this.w=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setW(e){return this.w=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;case 3:this.w=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;case 3:return this.w;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z,this.w)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this.w=e.w!==void 0?e.w:1,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this.w+=e.w,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this.w+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this.w=e.w+t.w,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this.w+=e.w*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this.w-=e.w,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this.w-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this.w=e.w-t.w,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this.w*=e.w,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this.w*=e,this}applyMatrix4(e){const t=this.x,n=this.y,s=this.z,r=this.w,o=e.elements;return this.x=o[0]*t+o[4]*n+o[8]*s+o[12]*r,this.y=o[1]*t+o[5]*n+o[9]*s+o[13]*r,this.z=o[2]*t+o[6]*n+o[10]*s+o[14]*r,this.w=o[3]*t+o[7]*n+o[11]*s+o[15]*r,this}divideScalar(e){return this.multiplyScalar(1/e)}setAxisAngleFromQuaternion(e){this.w=2*Math.acos(e.w);const t=Math.sqrt(1-e.w*e.w);return t<1e-4?(this.x=1,this.y=0,this.z=0):(this.x=e.x/t,this.y=e.y/t,this.z=e.z/t),this}setAxisAngleFromRotationMatrix(e){let t,n,s,r;const l=e.elements,c=l[0],u=l[4],h=l[8],d=l[1],f=l[5],v=l[9],g=l[2],m=l[6],p=l[10];if(Math.abs(u-d)<.01&&Math.abs(h-g)<.01&&Math.abs(v-m)<.01){if(Math.abs(u+d)<.1&&Math.abs(h+g)<.1&&Math.abs(v+m)<.1&&Math.abs(c+f+p-3)<.1)return this.set(1,0,0,0),this;t=Math.PI;const b=(c+1)/2,w=(f+1)/2,O=(p+1)/2,A=(u+d)/4,L=(h+g)/4,k=(v+m)/4;return b>w&&b>O?b<.01?(n=0,s=.707106781,r=.707106781):(n=Math.sqrt(b),s=A/n,r=L/n):w>O?w<.01?(n=.707106781,s=0,r=.707106781):(s=Math.sqrt(w),n=A/s,r=k/s):O<.01?(n=.707106781,s=.707106781,r=0):(r=Math.sqrt(O),n=L/r,s=k/r),this.set(n,s,r,t),this}let x=Math.sqrt((m-v)*(m-v)+(h-g)*(h-g)+(d-u)*(d-u));return Math.abs(x)<.001&&(x=1),this.x=(m-v)/x,this.y=(h-g)/x,this.z=(d-u)/x,this.w=Math.acos((c+f+p-1)/2),this}setFromMatrixPosition(e){const t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this.w=t[15],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this.w=Math.min(this.w,e.w),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this.w=Math.max(this.w,e.w),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this.z=Math.max(e.z,Math.min(t.z,this.z)),this.w=Math.max(e.w,Math.min(t.w,this.w)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this.z=Math.max(e,Math.min(t,this.z)),this.w=Math.max(e,Math.min(t,this.w)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this.w=Math.floor(this.w),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this.w=Math.ceil(this.w),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this.w=Math.round(this.w),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this.w=Math.trunc(this.w),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this.w=-this.w,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z+this.w*e.w}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)+Math.abs(this.w)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this.w+=(e.w-this.w)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this.z=e.z+(t.z-e.z)*n,this.w=e.w+(t.w-e.w)*n,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z&&e.w===this.w}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this.w=e[t+3],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e[t+3]=this.w,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this.w=e.getW(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this.w=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z,yield this.w}}class Fg extends Kr{constructor(e=1,t=1,n={}){super(),this.isRenderTarget=!0,this.width=e,this.height=t,this.depth=1,this.scissor=new en(0,0,e,t),this.scissorTest=!1,this.viewport=new en(0,0,e,t);const s={width:e,height:t,depth:1};n=Object.assign({generateMipmaps:!1,internalFormat:null,minFilter:ui,depthBuffer:!0,stencilBuffer:!1,resolveDepthBuffer:!0,resolveStencilBuffer:!0,depthTexture:null,samples:0,count:1},n);const r=new Dn(s,n.mapping,n.wrapS,n.wrapT,n.magFilter,n.minFilter,n.format,n.type,n.anisotropy,n.colorSpace);r.flipY=!1,r.generateMipmaps=n.generateMipmaps,r.internalFormat=n.internalFormat,this.textures=[];const o=n.count;for(let a=0;a<o;a++)this.textures[a]=r.clone(),this.textures[a].isRenderTargetTexture=!0;this.depthBuffer=n.depthBuffer,this.stencilBuffer=n.stencilBuffer,this.resolveDepthBuffer=n.resolveDepthBuffer,this.resolveStencilBuffer=n.resolveStencilBuffer,this.depthTexture=n.depthTexture,this.samples=n.samples}get texture(){return this.textures[0]}set texture(e){this.textures[0]=e}setSize(e,t,n=1){if(this.width!==e||this.height!==t||this.depth!==n){this.width=e,this.height=t,this.depth=n;for(let s=0,r=this.textures.length;s<r;s++)this.textures[s].image.width=e,this.textures[s].image.height=t,this.textures[s].image.depth=n;this.dispose()}this.viewport.set(0,0,e,t),this.scissor.set(0,0,e,t)}clone(){return new this.constructor().copy(this)}copy(e){this.width=e.width,this.height=e.height,this.depth=e.depth,this.scissor.copy(e.scissor),this.scissorTest=e.scissorTest,this.viewport.copy(e.viewport),this.textures.length=0;for(let n=0,s=e.textures.length;n<s;n++)this.textures[n]=e.textures[n].clone(),this.textures[n].isRenderTargetTexture=!0;const t=Object.assign({},e.texture.image);return this.texture.source=new Bf(t),this.depthBuffer=e.depthBuffer,this.stencilBuffer=e.stencilBuffer,this.resolveDepthBuffer=e.resolveDepthBuffer,this.resolveStencilBuffer=e.resolveStencilBuffer,e.depthTexture!==null&&(this.depthTexture=e.depthTexture.clone()),this.samples=e.samples,this}dispose(){this.dispatchEvent({type:"dispose"})}}class Gs extends Fg{constructor(e=1,t=1,n={}){super(e,t,n),this.isWebGLRenderTarget=!0}}class zf extends Dn{constructor(e=null,t=1,n=1,s=1){super(null),this.isDataArrayTexture=!0,this.image={data:e,width:t,height:n,depth:s},this.magFilter=ei,this.minFilter=ei,this.wrapR=ks,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1,this.layerUpdates=new Set}addLayerUpdate(e){this.layerUpdates.add(e)}clearLayerUpdates(){this.layerUpdates.clear()}}class kg extends Dn{constructor(e=null,t=1,n=1,s=1){super(null),this.isData3DTexture=!0,this.image={data:e,width:t,height:n,depth:s},this.magFilter=ei,this.minFilter=ei,this.wrapR=ks,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}}class Ws{constructor(e=0,t=0,n=0,s=1){this.isQuaternion=!0,this._x=e,this._y=t,this._z=n,this._w=s}static slerpFlat(e,t,n,s,r,o,a){let l=n[s+0],c=n[s+1],u=n[s+2],h=n[s+3];const d=r[o+0],f=r[o+1],v=r[o+2],g=r[o+3];if(a===0){e[t+0]=l,e[t+1]=c,e[t+2]=u,e[t+3]=h;return}if(a===1){e[t+0]=d,e[t+1]=f,e[t+2]=v,e[t+3]=g;return}if(h!==g||l!==d||c!==f||u!==v){let m=1-a;const p=l*d+c*f+u*v+h*g,x=p>=0?1:-1,b=1-p*p;if(b>Number.EPSILON){const O=Math.sqrt(b),A=Math.atan2(O,p*x);m=Math.sin(m*A)/O,a=Math.sin(a*A)/O}const w=a*x;if(l=l*m+d*w,c=c*m+f*w,u=u*m+v*w,h=h*m+g*w,m===1-a){const O=1/Math.sqrt(l*l+c*c+u*u+h*h);l*=O,c*=O,u*=O,h*=O}}e[t]=l,e[t+1]=c,e[t+2]=u,e[t+3]=h}static multiplyQuaternionsFlat(e,t,n,s,r,o){const a=n[s],l=n[s+1],c=n[s+2],u=n[s+3],h=r[o],d=r[o+1],f=r[o+2],v=r[o+3];return e[t]=a*v+u*h+l*f-c*d,e[t+1]=l*v+u*d+c*h-a*f,e[t+2]=c*v+u*f+a*d-l*h,e[t+3]=u*v-a*h-l*d-c*f,e}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get w(){return this._w}set w(e){this._w=e,this._onChangeCallback()}set(e,t,n,s){return this._x=e,this._y=t,this._z=n,this._w=s,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._w)}copy(e){return this._x=e.x,this._y=e.y,this._z=e.z,this._w=e.w,this._onChangeCallback(),this}setFromEuler(e,t=!0){const n=e._x,s=e._y,r=e._z,o=e._order,a=Math.cos,l=Math.sin,c=a(n/2),u=a(s/2),h=a(r/2),d=l(n/2),f=l(s/2),v=l(r/2);switch(o){case"XYZ":this._x=d*u*h+c*f*v,this._y=c*f*h-d*u*v,this._z=c*u*v+d*f*h,this._w=c*u*h-d*f*v;break;case"YXZ":this._x=d*u*h+c*f*v,this._y=c*f*h-d*u*v,this._z=c*u*v-d*f*h,this._w=c*u*h+d*f*v;break;case"ZXY":this._x=d*u*h-c*f*v,this._y=c*f*h+d*u*v,this._z=c*u*v+d*f*h,this._w=c*u*h-d*f*v;break;case"ZYX":this._x=d*u*h-c*f*v,this._y=c*f*h+d*u*v,this._z=c*u*v-d*f*h,this._w=c*u*h+d*f*v;break;case"YZX":this._x=d*u*h+c*f*v,this._y=c*f*h+d*u*v,this._z=c*u*v-d*f*h,this._w=c*u*h-d*f*v;break;case"XZY":this._x=d*u*h-c*f*v,this._y=c*f*h-d*u*v,this._z=c*u*v+d*f*h,this._w=c*u*h+d*f*v;break;default:console.warn("THREE.Quaternion: .setFromEuler() encountered an unknown order: "+o)}return t===!0&&this._onChangeCallback(),this}setFromAxisAngle(e,t){const n=t/2,s=Math.sin(n);return this._x=e.x*s,this._y=e.y*s,this._z=e.z*s,this._w=Math.cos(n),this._onChangeCallback(),this}setFromRotationMatrix(e){const t=e.elements,n=t[0],s=t[4],r=t[8],o=t[1],a=t[5],l=t[9],c=t[2],u=t[6],h=t[10],d=n+a+h;if(d>0){const f=.5/Math.sqrt(d+1);this._w=.25/f,this._x=(u-l)*f,this._y=(r-c)*f,this._z=(o-s)*f}else if(n>a&&n>h){const f=2*Math.sqrt(1+n-a-h);this._w=(u-l)/f,this._x=.25*f,this._y=(s+o)/f,this._z=(r+c)/f}else if(a>h){const f=2*Math.sqrt(1+a-n-h);this._w=(r-c)/f,this._x=(s+o)/f,this._y=.25*f,this._z=(l+u)/f}else{const f=2*Math.sqrt(1+h-n-a);this._w=(o-s)/f,this._x=(r+c)/f,this._y=(l+u)/f,this._z=.25*f}return this._onChangeCallback(),this}setFromUnitVectors(e,t){let n=e.dot(t)+1;return n<Number.EPSILON?(n=0,Math.abs(e.x)>Math.abs(e.z)?(this._x=-e.y,this._y=e.x,this._z=0,this._w=n):(this._x=0,this._y=-e.z,this._z=e.y,this._w=n)):(this._x=e.y*t.z-e.z*t.y,this._y=e.z*t.x-e.x*t.z,this._z=e.x*t.y-e.y*t.x,this._w=n),this.normalize()}angleTo(e){return 2*Math.acos(Math.abs(bn(this.dot(e),-1,1)))}rotateTowards(e,t){const n=this.angleTo(e);if(n===0)return this;const s=Math.min(1,t/n);return this.slerp(e,s),this}identity(){return this.set(0,0,0,1)}invert(){return this.conjugate()}conjugate(){return this._x*=-1,this._y*=-1,this._z*=-1,this._onChangeCallback(),this}dot(e){return this._x*e._x+this._y*e._y+this._z*e._z+this._w*e._w}lengthSq(){return this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w}length(){return Math.sqrt(this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w)}normalize(){let e=this.length();return e===0?(this._x=0,this._y=0,this._z=0,this._w=1):(e=1/e,this._x=this._x*e,this._y=this._y*e,this._z=this._z*e,this._w=this._w*e),this._onChangeCallback(),this}multiply(e){return this.multiplyQuaternions(this,e)}premultiply(e){return this.multiplyQuaternions(e,this)}multiplyQuaternions(e,t){const n=e._x,s=e._y,r=e._z,o=e._w,a=t._x,l=t._y,c=t._z,u=t._w;return this._x=n*u+o*a+s*c-r*l,this._y=s*u+o*l+r*a-n*c,this._z=r*u+o*c+n*l-s*a,this._w=o*u-n*a-s*l-r*c,this._onChangeCallback(),this}slerp(e,t){if(t===0)return this;if(t===1)return this.copy(e);const n=this._x,s=this._y,r=this._z,o=this._w;let a=o*e._w+n*e._x+s*e._y+r*e._z;if(a<0?(this._w=-e._w,this._x=-e._x,this._y=-e._y,this._z=-e._z,a=-a):this.copy(e),a>=1)return this._w=o,this._x=n,this._y=s,this._z=r,this;const l=1-a*a;if(l<=Number.EPSILON){const f=1-t;return this._w=f*o+t*this._w,this._x=f*n+t*this._x,this._y=f*s+t*this._y,this._z=f*r+t*this._z,this.normalize(),this}const c=Math.sqrt(l),u=Math.atan2(c,a),h=Math.sin((1-t)*u)/c,d=Math.sin(t*u)/c;return this._w=o*h+this._w*d,this._x=n*h+this._x*d,this._y=s*h+this._y*d,this._z=r*h+this._z*d,this._onChangeCallback(),this}slerpQuaternions(e,t,n){return this.copy(e).slerp(t,n)}random(){const e=2*Math.PI*Math.random(),t=2*Math.PI*Math.random(),n=Math.random(),s=Math.sqrt(1-n),r=Math.sqrt(n);return this.set(s*Math.sin(e),s*Math.cos(e),r*Math.sin(t),r*Math.cos(t))}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._w===this._w}fromArray(e,t=0){return this._x=e[t],this._y=e[t+1],this._z=e[t+2],this._w=e[t+3],this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._w,e}fromBufferAttribute(e,t){return this._x=e.getX(t),this._y=e.getY(t),this._z=e.getZ(t),this._w=e.getW(t),this._onChangeCallback(),this}toJSON(){return this.toArray()}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._w}}class G{constructor(e=0,t=0,n=0){G.prototype.isVector3=!0,this.x=e,this.y=t,this.z=n}set(e,t,n){return n===void 0&&(n=this.z),this.x=e,this.y=t,this.z=n,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this}multiplyVectors(e,t){return this.x=e.x*t.x,this.y=e.y*t.y,this.z=e.z*t.z,this}applyEuler(e){return this.applyQuaternion(wh.setFromEuler(e))}applyAxisAngle(e,t){return this.applyQuaternion(wh.setFromAxisAngle(e,t))}applyMatrix3(e){const t=this.x,n=this.y,s=this.z,r=e.elements;return this.x=r[0]*t+r[3]*n+r[6]*s,this.y=r[1]*t+r[4]*n+r[7]*s,this.z=r[2]*t+r[5]*n+r[8]*s,this}applyNormalMatrix(e){return this.applyMatrix3(e).normalize()}applyMatrix4(e){const t=this.x,n=this.y,s=this.z,r=e.elements,o=1/(r[3]*t+r[7]*n+r[11]*s+r[15]);return this.x=(r[0]*t+r[4]*n+r[8]*s+r[12])*o,this.y=(r[1]*t+r[5]*n+r[9]*s+r[13])*o,this.z=(r[2]*t+r[6]*n+r[10]*s+r[14])*o,this}applyQuaternion(e){const t=this.x,n=this.y,s=this.z,r=e.x,o=e.y,a=e.z,l=e.w,c=2*(o*s-a*n),u=2*(a*t-r*s),h=2*(r*n-o*t);return this.x=t+l*c+o*h-a*u,this.y=n+l*u+a*c-r*h,this.z=s+l*h+r*u-o*c,this}project(e){return this.applyMatrix4(e.matrixWorldInverse).applyMatrix4(e.projectionMatrix)}unproject(e){return this.applyMatrix4(e.projectionMatrixInverse).applyMatrix4(e.matrixWorld)}transformDirection(e){const t=this.x,n=this.y,s=this.z,r=e.elements;return this.x=r[0]*t+r[4]*n+r[8]*s,this.y=r[1]*t+r[5]*n+r[9]*s,this.z=r[2]*t+r[6]*n+r[10]*s,this.normalize()}divide(e){return this.x/=e.x,this.y/=e.y,this.z/=e.z,this}divideScalar(e){return this.multiplyScalar(1/e)}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this.z=Math.max(e.z,Math.min(t.z,this.z)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this.z=Math.max(e,Math.min(t,this.z)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this.z=e.z+(t.z-e.z)*n,this}cross(e){return this.crossVectors(this,e)}crossVectors(e,t){const n=e.x,s=e.y,r=e.z,o=t.x,a=t.y,l=t.z;return this.x=s*l-r*a,this.y=r*o-n*l,this.z=n*a-s*o,this}projectOnVector(e){const t=e.lengthSq();if(t===0)return this.set(0,0,0);const n=e.dot(this)/t;return this.copy(e).multiplyScalar(n)}projectOnPlane(e){return Ul.copy(this).projectOnVector(e),this.sub(Ul)}reflect(e){return this.sub(Ul.copy(e).multiplyScalar(2*this.dot(e)))}angleTo(e){const t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;const n=this.dot(e)/t;return Math.acos(bn(n,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){const t=this.x-e.x,n=this.y-e.y,s=this.z-e.z;return t*t+n*n+s*s}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)+Math.abs(this.z-e.z)}setFromSpherical(e){return this.setFromSphericalCoords(e.radius,e.phi,e.theta)}setFromSphericalCoords(e,t,n){const s=Math.sin(t)*e;return this.x=s*Math.sin(n),this.y=Math.cos(t)*e,this.z=s*Math.cos(n),this}setFromCylindrical(e){return this.setFromCylindricalCoords(e.radius,e.theta,e.y)}setFromCylindricalCoords(e,t,n){return this.x=e*Math.sin(t),this.y=n,this.z=e*Math.cos(t),this}setFromMatrixPosition(e){const t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this}setFromMatrixScale(e){const t=this.setFromMatrixColumn(e,0).length(),n=this.setFromMatrixColumn(e,1).length(),s=this.setFromMatrixColumn(e,2).length();return this.x=t,this.y=n,this.z=s,this}setFromMatrixColumn(e,t){return this.fromArray(e.elements,t*4)}setFromMatrix3Column(e,t){return this.fromArray(e.elements,t*3)}setFromEuler(e){return this.x=e._x,this.y=e._y,this.z=e._z,this}setFromColor(e){return this.x=e.r,this.y=e.g,this.z=e.b,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this}randomDirection(){const e=Math.random()*Math.PI*2,t=Math.random()*2-1,n=Math.sqrt(1-t*t);return this.x=n*Math.cos(e),this.y=t,this.z=n*Math.sin(e),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z}}const Ul=new G,wh=new Ws;class Ba{constructor(e=new G(1/0,1/0,1/0),t=new G(-1/0,-1/0,-1/0)){this.isBox3=!0,this.min=e,this.max=t}set(e,t){return this.min.copy(e),this.max.copy(t),this}setFromArray(e){this.makeEmpty();for(let t=0,n=e.length;t<n;t+=3)this.expandByPoint(ri.fromArray(e,t));return this}setFromBufferAttribute(e){this.makeEmpty();for(let t=0,n=e.count;t<n;t++)this.expandByPoint(ri.fromBufferAttribute(e,t));return this}setFromPoints(e){this.makeEmpty();for(let t=0,n=e.length;t<n;t++)this.expandByPoint(e[t]);return this}setFromCenterAndSize(e,t){const n=ri.copy(t).multiplyScalar(.5);return this.min.copy(e).sub(n),this.max.copy(e).add(n),this}setFromObject(e,t=!1){return this.makeEmpty(),this.expandByObject(e,t)}clone(){return new this.constructor().copy(this)}copy(e){return this.min.copy(e.min),this.max.copy(e.max),this}makeEmpty(){return this.min.x=this.min.y=this.min.z=1/0,this.max.x=this.max.y=this.max.z=-1/0,this}isEmpty(){return this.max.x<this.min.x||this.max.y<this.min.y||this.max.z<this.min.z}getCenter(e){return this.isEmpty()?e.set(0,0,0):e.addVectors(this.min,this.max).multiplyScalar(.5)}getSize(e){return this.isEmpty()?e.set(0,0,0):e.subVectors(this.max,this.min)}expandByPoint(e){return this.min.min(e),this.max.max(e),this}expandByVector(e){return this.min.sub(e),this.max.add(e),this}expandByScalar(e){return this.min.addScalar(-e),this.max.addScalar(e),this}expandByObject(e,t=!1){e.updateWorldMatrix(!1,!1);const n=e.geometry;if(n!==void 0){const r=n.getAttribute("position");if(t===!0&&r!==void 0&&e.isInstancedMesh!==!0)for(let o=0,a=r.count;o<a;o++)e.isMesh===!0?e.getVertexPosition(o,ri):ri.fromBufferAttribute(r,o),ri.applyMatrix4(e.matrixWorld),this.expandByPoint(ri);else e.boundingBox!==void 0?(e.boundingBox===null&&e.computeBoundingBox(),ja.copy(e.boundingBox)):(n.boundingBox===null&&n.computeBoundingBox(),ja.copy(n.boundingBox)),ja.applyMatrix4(e.matrixWorld),this.union(ja)}const s=e.children;for(let r=0,o=s.length;r<o;r++)this.expandByObject(s[r],t);return this}containsPoint(e){return e.x>=this.min.x&&e.x<=this.max.x&&e.y>=this.min.y&&e.y<=this.max.y&&e.z>=this.min.z&&e.z<=this.max.z}containsBox(e){return this.min.x<=e.min.x&&e.max.x<=this.max.x&&this.min.y<=e.min.y&&e.max.y<=this.max.y&&this.min.z<=e.min.z&&e.max.z<=this.max.z}getParameter(e,t){return t.set((e.x-this.min.x)/(this.max.x-this.min.x),(e.y-this.min.y)/(this.max.y-this.min.y),(e.z-this.min.z)/(this.max.z-this.min.z))}intersectsBox(e){return e.max.x>=this.min.x&&e.min.x<=this.max.x&&e.max.y>=this.min.y&&e.min.y<=this.max.y&&e.max.z>=this.min.z&&e.min.z<=this.max.z}intersectsSphere(e){return this.clampPoint(e.center,ri),ri.distanceToSquared(e.center)<=e.radius*e.radius}intersectsPlane(e){let t,n;return e.normal.x>0?(t=e.normal.x*this.min.x,n=e.normal.x*this.max.x):(t=e.normal.x*this.max.x,n=e.normal.x*this.min.x),e.normal.y>0?(t+=e.normal.y*this.min.y,n+=e.normal.y*this.max.y):(t+=e.normal.y*this.max.y,n+=e.normal.y*this.min.y),e.normal.z>0?(t+=e.normal.z*this.min.z,n+=e.normal.z*this.max.z):(t+=e.normal.z*this.max.z,n+=e.normal.z*this.min.z),t<=-e.constant&&n>=-e.constant}intersectsTriangle(e){if(this.isEmpty())return!1;this.getCenter(ha),Ka.subVectors(this.max,ha),hr.subVectors(e.a,ha),dr.subVectors(e.b,ha),fr.subVectors(e.c,ha),Qi.subVectors(dr,hr),es.subVectors(fr,dr),Ts.subVectors(hr,fr);let t=[0,-Qi.z,Qi.y,0,-es.z,es.y,0,-Ts.z,Ts.y,Qi.z,0,-Qi.x,es.z,0,-es.x,Ts.z,0,-Ts.x,-Qi.y,Qi.x,0,-es.y,es.x,0,-Ts.y,Ts.x,0];return!Nl(t,hr,dr,fr,Ka)||(t=[1,0,0,0,1,0,0,0,1],!Nl(t,hr,dr,fr,Ka))?!1:(Za.crossVectors(Qi,es),t=[Za.x,Za.y,Za.z],Nl(t,hr,dr,fr,Ka))}clampPoint(e,t){return t.copy(e).clamp(this.min,this.max)}distanceToPoint(e){return this.clampPoint(e,ri).distanceTo(e)}getBoundingSphere(e){return this.isEmpty()?e.makeEmpty():(this.getCenter(e.center),e.radius=this.getSize(ri).length()*.5),e}intersect(e){return this.min.max(e.min),this.max.min(e.max),this.isEmpty()&&this.makeEmpty(),this}union(e){return this.min.min(e.min),this.max.max(e.max),this}applyMatrix4(e){return this.isEmpty()?this:(Ui[0].set(this.min.x,this.min.y,this.min.z).applyMatrix4(e),Ui[1].set(this.min.x,this.min.y,this.max.z).applyMatrix4(e),Ui[2].set(this.min.x,this.max.y,this.min.z).applyMatrix4(e),Ui[3].set(this.min.x,this.max.y,this.max.z).applyMatrix4(e),Ui[4].set(this.max.x,this.min.y,this.min.z).applyMatrix4(e),Ui[5].set(this.max.x,this.min.y,this.max.z).applyMatrix4(e),Ui[6].set(this.max.x,this.max.y,this.min.z).applyMatrix4(e),Ui[7].set(this.max.x,this.max.y,this.max.z).applyMatrix4(e),this.setFromPoints(Ui),this)}translate(e){return this.min.add(e),this.max.add(e),this}equals(e){return e.min.equals(this.min)&&e.max.equals(this.max)}}const Ui=[new G,new G,new G,new G,new G,new G,new G,new G],ri=new G,ja=new Ba,hr=new G,dr=new G,fr=new G,Qi=new G,es=new G,Ts=new G,ha=new G,Ka=new G,Za=new G,As=new G;function Nl(i,e,t,n,s){for(let r=0,o=i.length-3;r<=o;r+=3){As.fromArray(i,r);const a=s.x*Math.abs(As.x)+s.y*Math.abs(As.y)+s.z*Math.abs(As.z),l=e.dot(As),c=t.dot(As),u=n.dot(As);if(Math.max(-Math.max(l,c,u),Math.min(l,c,u))>a)return!1}return!0}const Bg=new Ba,da=new G,Ol=new G;class sl{constructor(e=new G,t=-1){this.isSphere=!0,this.center=e,this.radius=t}set(e,t){return this.center.copy(e),this.radius=t,this}setFromPoints(e,t){const n=this.center;t!==void 0?n.copy(t):Bg.setFromPoints(e).getCenter(n);let s=0;for(let r=0,o=e.length;r<o;r++)s=Math.max(s,n.distanceToSquared(e[r]));return this.radius=Math.sqrt(s),this}copy(e){return this.center.copy(e.center),this.radius=e.radius,this}isEmpty(){return this.radius<0}makeEmpty(){return this.center.set(0,0,0),this.radius=-1,this}containsPoint(e){return e.distanceToSquared(this.center)<=this.radius*this.radius}distanceToPoint(e){return e.distanceTo(this.center)-this.radius}intersectsSphere(e){const t=this.radius+e.radius;return e.center.distanceToSquared(this.center)<=t*t}intersectsBox(e){return e.intersectsSphere(this)}intersectsPlane(e){return Math.abs(e.distanceToPoint(this.center))<=this.radius}clampPoint(e,t){const n=this.center.distanceToSquared(e);return t.copy(e),n>this.radius*this.radius&&(t.sub(this.center).normalize(),t.multiplyScalar(this.radius).add(this.center)),t}getBoundingBox(e){return this.isEmpty()?(e.makeEmpty(),e):(e.set(this.center,this.center),e.expandByScalar(this.radius),e)}applyMatrix4(e){return this.center.applyMatrix4(e),this.radius=this.radius*e.getMaxScaleOnAxis(),this}translate(e){return this.center.add(e),this}expandByPoint(e){if(this.isEmpty())return this.center.copy(e),this.radius=0,this;da.subVectors(e,this.center);const t=da.lengthSq();if(t>this.radius*this.radius){const n=Math.sqrt(t),s=(n-this.radius)*.5;this.center.addScaledVector(da,s/n),this.radius+=s}return this}union(e){return e.isEmpty()?this:this.isEmpty()?(this.copy(e),this):(this.center.equals(e.center)===!0?this.radius=Math.max(this.radius,e.radius):(Ol.subVectors(e.center,this.center).setLength(e.radius),this.expandByPoint(da.copy(e.center).add(Ol)),this.expandByPoint(da.copy(e.center).sub(Ol))),this)}equals(e){return e.center.equals(this.center)&&e.radius===this.radius}clone(){return new this.constructor().copy(this)}}const Ni=new G,Fl=new G,Ja=new G,ts=new G,kl=new G,Qa=new G,Bl=new G;class rl{constructor(e=new G,t=new G(0,0,-1)){this.origin=e,this.direction=t}set(e,t){return this.origin.copy(e),this.direction.copy(t),this}copy(e){return this.origin.copy(e.origin),this.direction.copy(e.direction),this}at(e,t){return t.copy(this.origin).addScaledVector(this.direction,e)}lookAt(e){return this.direction.copy(e).sub(this.origin).normalize(),this}recast(e){return this.origin.copy(this.at(e,Ni)),this}closestPointToPoint(e,t){t.subVectors(e,this.origin);const n=t.dot(this.direction);return n<0?t.copy(this.origin):t.copy(this.origin).addScaledVector(this.direction,n)}distanceToPoint(e){return Math.sqrt(this.distanceSqToPoint(e))}distanceSqToPoint(e){const t=Ni.subVectors(e,this.origin).dot(this.direction);return t<0?this.origin.distanceToSquared(e):(Ni.copy(this.origin).addScaledVector(this.direction,t),Ni.distanceToSquared(e))}distanceSqToSegment(e,t,n,s){Fl.copy(e).add(t).multiplyScalar(.5),Ja.copy(t).sub(e).normalize(),ts.copy(this.origin).sub(Fl);const r=e.distanceTo(t)*.5,o=-this.direction.dot(Ja),a=ts.dot(this.direction),l=-ts.dot(Ja),c=ts.lengthSq(),u=Math.abs(1-o*o);let h,d,f,v;if(u>0)if(h=o*l-a,d=o*a-l,v=r*u,h>=0)if(d>=-v)if(d<=v){const g=1/u;h*=g,d*=g,f=h*(h+o*d+2*a)+d*(o*h+d+2*l)+c}else d=r,h=Math.max(0,-(o*d+a)),f=-h*h+d*(d+2*l)+c;else d=-r,h=Math.max(0,-(o*d+a)),f=-h*h+d*(d+2*l)+c;else d<=-v?(h=Math.max(0,-(-o*r+a)),d=h>0?-r:Math.min(Math.max(-r,-l),r),f=-h*h+d*(d+2*l)+c):d<=v?(h=0,d=Math.min(Math.max(-r,-l),r),f=d*(d+2*l)+c):(h=Math.max(0,-(o*r+a)),d=h>0?r:Math.min(Math.max(-r,-l),r),f=-h*h+d*(d+2*l)+c);else d=o>0?-r:r,h=Math.max(0,-(o*d+a)),f=-h*h+d*(d+2*l)+c;return n&&n.copy(this.origin).addScaledVector(this.direction,h),s&&s.copy(Fl).addScaledVector(Ja,d),f}intersectSphere(e,t){Ni.subVectors(e.center,this.origin);const n=Ni.dot(this.direction),s=Ni.dot(Ni)-n*n,r=e.radius*e.radius;if(s>r)return null;const o=Math.sqrt(r-s),a=n-o,l=n+o;return l<0?null:a<0?this.at(l,t):this.at(a,t)}intersectsSphere(e){return this.distanceSqToPoint(e.center)<=e.radius*e.radius}distanceToPlane(e){const t=e.normal.dot(this.direction);if(t===0)return e.distanceToPoint(this.origin)===0?0:null;const n=-(this.origin.dot(e.normal)+e.constant)/t;return n>=0?n:null}intersectPlane(e,t){const n=this.distanceToPlane(e);return n===null?null:this.at(n,t)}intersectsPlane(e){const t=e.distanceToPoint(this.origin);return t===0||e.normal.dot(this.direction)*t<0}intersectBox(e,t){let n,s,r,o,a,l;const c=1/this.direction.x,u=1/this.direction.y,h=1/this.direction.z,d=this.origin;return c>=0?(n=(e.min.x-d.x)*c,s=(e.max.x-d.x)*c):(n=(e.max.x-d.x)*c,s=(e.min.x-d.x)*c),u>=0?(r=(e.min.y-d.y)*u,o=(e.max.y-d.y)*u):(r=(e.max.y-d.y)*u,o=(e.min.y-d.y)*u),n>o||r>s||((r>n||isNaN(n))&&(n=r),(o<s||isNaN(s))&&(s=o),h>=0?(a=(e.min.z-d.z)*h,l=(e.max.z-d.z)*h):(a=(e.max.z-d.z)*h,l=(e.min.z-d.z)*h),n>l||a>s)||((a>n||n!==n)&&(n=a),(l<s||s!==s)&&(s=l),s<0)?null:this.at(n>=0?n:s,t)}intersectsBox(e){return this.intersectBox(e,Ni)!==null}intersectTriangle(e,t,n,s,r){kl.subVectors(t,e),Qa.subVectors(n,e),Bl.crossVectors(kl,Qa);let o=this.direction.dot(Bl),a;if(o>0){if(s)return null;a=1}else if(o<0)a=-1,o=-o;else return null;ts.subVectors(this.origin,e);const l=a*this.direction.dot(Qa.crossVectors(ts,Qa));if(l<0)return null;const c=a*this.direction.dot(kl.cross(ts));if(c<0||l+c>o)return null;const u=-a*ts.dot(Bl);return u<0?null:this.at(u/o,r)}applyMatrix4(e){return this.origin.applyMatrix4(e),this.direction.transformDirection(e),this}equals(e){return e.origin.equals(this.origin)&&e.direction.equals(this.direction)}clone(){return new this.constructor().copy(this)}}class Gt{constructor(e,t,n,s,r,o,a,l,c,u,h,d,f,v,g,m){Gt.prototype.isMatrix4=!0,this.elements=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],e!==void 0&&this.set(e,t,n,s,r,o,a,l,c,u,h,d,f,v,g,m)}set(e,t,n,s,r,o,a,l,c,u,h,d,f,v,g,m){const p=this.elements;return p[0]=e,p[4]=t,p[8]=n,p[12]=s,p[1]=r,p[5]=o,p[9]=a,p[13]=l,p[2]=c,p[6]=u,p[10]=h,p[14]=d,p[3]=f,p[7]=v,p[11]=g,p[15]=m,this}identity(){return this.set(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1),this}clone(){return new Gt().fromArray(this.elements)}copy(e){const t=this.elements,n=e.elements;return t[0]=n[0],t[1]=n[1],t[2]=n[2],t[3]=n[3],t[4]=n[4],t[5]=n[5],t[6]=n[6],t[7]=n[7],t[8]=n[8],t[9]=n[9],t[10]=n[10],t[11]=n[11],t[12]=n[12],t[13]=n[13],t[14]=n[14],t[15]=n[15],this}copyPosition(e){const t=this.elements,n=e.elements;return t[12]=n[12],t[13]=n[13],t[14]=n[14],this}setFromMatrix3(e){const t=e.elements;return this.set(t[0],t[3],t[6],0,t[1],t[4],t[7],0,t[2],t[5],t[8],0,0,0,0,1),this}extractBasis(e,t,n){return e.setFromMatrixColumn(this,0),t.setFromMatrixColumn(this,1),n.setFromMatrixColumn(this,2),this}makeBasis(e,t,n){return this.set(e.x,t.x,n.x,0,e.y,t.y,n.y,0,e.z,t.z,n.z,0,0,0,0,1),this}extractRotation(e){const t=this.elements,n=e.elements,s=1/pr.setFromMatrixColumn(e,0).length(),r=1/pr.setFromMatrixColumn(e,1).length(),o=1/pr.setFromMatrixColumn(e,2).length();return t[0]=n[0]*s,t[1]=n[1]*s,t[2]=n[2]*s,t[3]=0,t[4]=n[4]*r,t[5]=n[5]*r,t[6]=n[6]*r,t[7]=0,t[8]=n[8]*o,t[9]=n[9]*o,t[10]=n[10]*o,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromEuler(e){const t=this.elements,n=e.x,s=e.y,r=e.z,o=Math.cos(n),a=Math.sin(n),l=Math.cos(s),c=Math.sin(s),u=Math.cos(r),h=Math.sin(r);if(e.order==="XYZ"){const d=o*u,f=o*h,v=a*u,g=a*h;t[0]=l*u,t[4]=-l*h,t[8]=c,t[1]=f+v*c,t[5]=d-g*c,t[9]=-a*l,t[2]=g-d*c,t[6]=v+f*c,t[10]=o*l}else if(e.order==="YXZ"){const d=l*u,f=l*h,v=c*u,g=c*h;t[0]=d+g*a,t[4]=v*a-f,t[8]=o*c,t[1]=o*h,t[5]=o*u,t[9]=-a,t[2]=f*a-v,t[6]=g+d*a,t[10]=o*l}else if(e.order==="ZXY"){const d=l*u,f=l*h,v=c*u,g=c*h;t[0]=d-g*a,t[4]=-o*h,t[8]=v+f*a,t[1]=f+v*a,t[5]=o*u,t[9]=g-d*a,t[2]=-o*c,t[6]=a,t[10]=o*l}else if(e.order==="ZYX"){const d=o*u,f=o*h,v=a*u,g=a*h;t[0]=l*u,t[4]=v*c-f,t[8]=d*c+g,t[1]=l*h,t[5]=g*c+d,t[9]=f*c-v,t[2]=-c,t[6]=a*l,t[10]=o*l}else if(e.order==="YZX"){const d=o*l,f=o*c,v=a*l,g=a*c;t[0]=l*u,t[4]=g-d*h,t[8]=v*h+f,t[1]=h,t[5]=o*u,t[9]=-a*u,t[2]=-c*u,t[6]=f*h+v,t[10]=d-g*h}else if(e.order==="XZY"){const d=o*l,f=o*c,v=a*l,g=a*c;t[0]=l*u,t[4]=-h,t[8]=c*u,t[1]=d*h+g,t[5]=o*u,t[9]=f*h-v,t[2]=v*h-f,t[6]=a*u,t[10]=g*h+d}return t[3]=0,t[7]=0,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromQuaternion(e){return this.compose(zg,e,Hg)}lookAt(e,t,n){const s=this.elements;return Bn.subVectors(e,t),Bn.lengthSq()===0&&(Bn.z=1),Bn.normalize(),ns.crossVectors(n,Bn),ns.lengthSq()===0&&(Math.abs(n.z)===1?Bn.x+=1e-4:Bn.z+=1e-4,Bn.normalize(),ns.crossVectors(n,Bn)),ns.normalize(),eo.crossVectors(Bn,ns),s[0]=ns.x,s[4]=eo.x,s[8]=Bn.x,s[1]=ns.y,s[5]=eo.y,s[9]=Bn.y,s[2]=ns.z,s[6]=eo.z,s[10]=Bn.z,this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){const n=e.elements,s=t.elements,r=this.elements,o=n[0],a=n[4],l=n[8],c=n[12],u=n[1],h=n[5],d=n[9],f=n[13],v=n[2],g=n[6],m=n[10],p=n[14],x=n[3],b=n[7],w=n[11],O=n[15],A=s[0],L=s[4],k=s[8],E=s[12],y=s[1],P=s[5],K=s[9],z=s[13],Z=s[2],q=s[6],Q=s[10],$=s[14],te=s[3],ge=s[7],de=s[11],xe=s[15];return r[0]=o*A+a*y+l*Z+c*te,r[4]=o*L+a*P+l*q+c*ge,r[8]=o*k+a*K+l*Q+c*de,r[12]=o*E+a*z+l*$+c*xe,r[1]=u*A+h*y+d*Z+f*te,r[5]=u*L+h*P+d*q+f*ge,r[9]=u*k+h*K+d*Q+f*de,r[13]=u*E+h*z+d*$+f*xe,r[2]=v*A+g*y+m*Z+p*te,r[6]=v*L+g*P+m*q+p*ge,r[10]=v*k+g*K+m*Q+p*de,r[14]=v*E+g*z+m*$+p*xe,r[3]=x*A+b*y+w*Z+O*te,r[7]=x*L+b*P+w*q+O*ge,r[11]=x*k+b*K+w*Q+O*de,r[15]=x*E+b*z+w*$+O*xe,this}multiplyScalar(e){const t=this.elements;return t[0]*=e,t[4]*=e,t[8]*=e,t[12]*=e,t[1]*=e,t[5]*=e,t[9]*=e,t[13]*=e,t[2]*=e,t[6]*=e,t[10]*=e,t[14]*=e,t[3]*=e,t[7]*=e,t[11]*=e,t[15]*=e,this}determinant(){const e=this.elements,t=e[0],n=e[4],s=e[8],r=e[12],o=e[1],a=e[5],l=e[9],c=e[13],u=e[2],h=e[6],d=e[10],f=e[14],v=e[3],g=e[7],m=e[11],p=e[15];return v*(+r*l*h-s*c*h-r*a*d+n*c*d+s*a*f-n*l*f)+g*(+t*l*f-t*c*d+r*o*d-s*o*f+s*c*u-r*l*u)+m*(+t*c*h-t*a*f-r*o*h+n*o*f+r*a*u-n*c*u)+p*(-s*a*u-t*l*h+t*a*d+s*o*h-n*o*d+n*l*u)}transpose(){const e=this.elements;let t;return t=e[1],e[1]=e[4],e[4]=t,t=e[2],e[2]=e[8],e[8]=t,t=e[6],e[6]=e[9],e[9]=t,t=e[3],e[3]=e[12],e[12]=t,t=e[7],e[7]=e[13],e[13]=t,t=e[11],e[11]=e[14],e[14]=t,this}setPosition(e,t,n){const s=this.elements;return e.isVector3?(s[12]=e.x,s[13]=e.y,s[14]=e.z):(s[12]=e,s[13]=t,s[14]=n),this}invert(){const e=this.elements,t=e[0],n=e[1],s=e[2],r=e[3],o=e[4],a=e[5],l=e[6],c=e[7],u=e[8],h=e[9],d=e[10],f=e[11],v=e[12],g=e[13],m=e[14],p=e[15],x=h*m*c-g*d*c+g*l*f-a*m*f-h*l*p+a*d*p,b=v*d*c-u*m*c-v*l*f+o*m*f+u*l*p-o*d*p,w=u*g*c-v*h*c+v*a*f-o*g*f-u*a*p+o*h*p,O=v*h*l-u*g*l-v*a*d+o*g*d+u*a*m-o*h*m,A=t*x+n*b+s*w+r*O;if(A===0)return this.set(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);const L=1/A;return e[0]=x*L,e[1]=(g*d*r-h*m*r-g*s*f+n*m*f+h*s*p-n*d*p)*L,e[2]=(a*m*r-g*l*r+g*s*c-n*m*c-a*s*p+n*l*p)*L,e[3]=(h*l*r-a*d*r-h*s*c+n*d*c+a*s*f-n*l*f)*L,e[4]=b*L,e[5]=(u*m*r-v*d*r+v*s*f-t*m*f-u*s*p+t*d*p)*L,e[6]=(v*l*r-o*m*r-v*s*c+t*m*c+o*s*p-t*l*p)*L,e[7]=(o*d*r-u*l*r+u*s*c-t*d*c-o*s*f+t*l*f)*L,e[8]=w*L,e[9]=(v*h*r-u*g*r-v*n*f+t*g*f+u*n*p-t*h*p)*L,e[10]=(o*g*r-v*a*r+v*n*c-t*g*c-o*n*p+t*a*p)*L,e[11]=(u*a*r-o*h*r-u*n*c+t*h*c+o*n*f-t*a*f)*L,e[12]=O*L,e[13]=(u*g*s-v*h*s+v*n*d-t*g*d-u*n*m+t*h*m)*L,e[14]=(v*a*s-o*g*s-v*n*l+t*g*l+o*n*m-t*a*m)*L,e[15]=(o*h*s-u*a*s+u*n*l-t*h*l-o*n*d+t*a*d)*L,this}scale(e){const t=this.elements,n=e.x,s=e.y,r=e.z;return t[0]*=n,t[4]*=s,t[8]*=r,t[1]*=n,t[5]*=s,t[9]*=r,t[2]*=n,t[6]*=s,t[10]*=r,t[3]*=n,t[7]*=s,t[11]*=r,this}getMaxScaleOnAxis(){const e=this.elements,t=e[0]*e[0]+e[1]*e[1]+e[2]*e[2],n=e[4]*e[4]+e[5]*e[5]+e[6]*e[6],s=e[8]*e[8]+e[9]*e[9]+e[10]*e[10];return Math.sqrt(Math.max(t,n,s))}makeTranslation(e,t,n){return e.isVector3?this.set(1,0,0,e.x,0,1,0,e.y,0,0,1,e.z,0,0,0,1):this.set(1,0,0,e,0,1,0,t,0,0,1,n,0,0,0,1),this}makeRotationX(e){const t=Math.cos(e),n=Math.sin(e);return this.set(1,0,0,0,0,t,-n,0,0,n,t,0,0,0,0,1),this}makeRotationY(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,0,n,0,0,1,0,0,-n,0,t,0,0,0,0,1),this}makeRotationZ(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,-n,0,0,n,t,0,0,0,0,1,0,0,0,0,1),this}makeRotationAxis(e,t){const n=Math.cos(t),s=Math.sin(t),r=1-n,o=e.x,a=e.y,l=e.z,c=r*o,u=r*a;return this.set(c*o+n,c*a-s*l,c*l+s*a,0,c*a+s*l,u*a+n,u*l-s*o,0,c*l-s*a,u*l+s*o,r*l*l+n,0,0,0,0,1),this}makeScale(e,t,n){return this.set(e,0,0,0,0,t,0,0,0,0,n,0,0,0,0,1),this}makeShear(e,t,n,s,r,o){return this.set(1,n,r,0,e,1,o,0,t,s,1,0,0,0,0,1),this}compose(e,t,n){const s=this.elements,r=t._x,o=t._y,a=t._z,l=t._w,c=r+r,u=o+o,h=a+a,d=r*c,f=r*u,v=r*h,g=o*u,m=o*h,p=a*h,x=l*c,b=l*u,w=l*h,O=n.x,A=n.y,L=n.z;return s[0]=(1-(g+p))*O,s[1]=(f+w)*O,s[2]=(v-b)*O,s[3]=0,s[4]=(f-w)*A,s[5]=(1-(d+p))*A,s[6]=(m+x)*A,s[7]=0,s[8]=(v+b)*L,s[9]=(m-x)*L,s[10]=(1-(d+g))*L,s[11]=0,s[12]=e.x,s[13]=e.y,s[14]=e.z,s[15]=1,this}decompose(e,t,n){const s=this.elements;let r=pr.set(s[0],s[1],s[2]).length();const o=pr.set(s[4],s[5],s[6]).length(),a=pr.set(s[8],s[9],s[10]).length();this.determinant()<0&&(r=-r),e.x=s[12],e.y=s[13],e.z=s[14],ai.copy(this);const c=1/r,u=1/o,h=1/a;return ai.elements[0]*=c,ai.elements[1]*=c,ai.elements[2]*=c,ai.elements[4]*=u,ai.elements[5]*=u,ai.elements[6]*=u,ai.elements[8]*=h,ai.elements[9]*=h,ai.elements[10]*=h,t.setFromRotationMatrix(ai),n.x=r,n.y=o,n.z=a,this}makePerspective(e,t,n,s,r,o,a=Vi){const l=this.elements,c=2*r/(t-e),u=2*r/(n-s),h=(t+e)/(t-e),d=(n+s)/(n-s);let f,v;if(a===Vi)f=-(o+r)/(o-r),v=-2*o*r/(o-r);else if(a===Go)f=-o/(o-r),v=-o*r/(o-r);else throw new Error("THREE.Matrix4.makePerspective(): Invalid coordinate system: "+a);return l[0]=c,l[4]=0,l[8]=h,l[12]=0,l[1]=0,l[5]=u,l[9]=d,l[13]=0,l[2]=0,l[6]=0,l[10]=f,l[14]=v,l[3]=0,l[7]=0,l[11]=-1,l[15]=0,this}makeOrthographic(e,t,n,s,r,o,a=Vi){const l=this.elements,c=1/(t-e),u=1/(n-s),h=1/(o-r),d=(t+e)*c,f=(n+s)*u;let v,g;if(a===Vi)v=(o+r)*h,g=-2*h;else if(a===Go)v=r*h,g=-1*h;else throw new Error("THREE.Matrix4.makeOrthographic(): Invalid coordinate system: "+a);return l[0]=2*c,l[4]=0,l[8]=0,l[12]=-d,l[1]=0,l[5]=2*u,l[9]=0,l[13]=-f,l[2]=0,l[6]=0,l[10]=g,l[14]=-v,l[3]=0,l[7]=0,l[11]=0,l[15]=1,this}equals(e){const t=this.elements,n=e.elements;for(let s=0;s<16;s++)if(t[s]!==n[s])return!1;return!0}fromArray(e,t=0){for(let n=0;n<16;n++)this.elements[n]=e[n+t];return this}toArray(e=[],t=0){const n=this.elements;return e[t]=n[0],e[t+1]=n[1],e[t+2]=n[2],e[t+3]=n[3],e[t+4]=n[4],e[t+5]=n[5],e[t+6]=n[6],e[t+7]=n[7],e[t+8]=n[8],e[t+9]=n[9],e[t+10]=n[10],e[t+11]=n[11],e[t+12]=n[12],e[t+13]=n[13],e[t+14]=n[14],e[t+15]=n[15],e}}const pr=new G,ai=new Gt,zg=new G(0,0,0),Hg=new G(1,1,1),ns=new G,eo=new G,Bn=new G,Eh=new Gt,Th=new Ws;class Ai{constructor(e=0,t=0,n=0,s=Ai.DEFAULT_ORDER){this.isEuler=!0,this._x=e,this._y=t,this._z=n,this._order=s}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get order(){return this._order}set order(e){this._order=e,this._onChangeCallback()}set(e,t,n,s=this._order){return this._x=e,this._y=t,this._z=n,this._order=s,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._order)}copy(e){return this._x=e._x,this._y=e._y,this._z=e._z,this._order=e._order,this._onChangeCallback(),this}setFromRotationMatrix(e,t=this._order,n=!0){const s=e.elements,r=s[0],o=s[4],a=s[8],l=s[1],c=s[5],u=s[9],h=s[2],d=s[6],f=s[10];switch(t){case"XYZ":this._y=Math.asin(bn(a,-1,1)),Math.abs(a)<.9999999?(this._x=Math.atan2(-u,f),this._z=Math.atan2(-o,r)):(this._x=Math.atan2(d,c),this._z=0);break;case"YXZ":this._x=Math.asin(-bn(u,-1,1)),Math.abs(u)<.9999999?(this._y=Math.atan2(a,f),this._z=Math.atan2(l,c)):(this._y=Math.atan2(-h,r),this._z=0);break;case"ZXY":this._x=Math.asin(bn(d,-1,1)),Math.abs(d)<.9999999?(this._y=Math.atan2(-h,f),this._z=Math.atan2(-o,c)):(this._y=0,this._z=Math.atan2(l,r));break;case"ZYX":this._y=Math.asin(-bn(h,-1,1)),Math.abs(h)<.9999999?(this._x=Math.atan2(d,f),this._z=Math.atan2(l,r)):(this._x=0,this._z=Math.atan2(-o,c));break;case"YZX":this._z=Math.asin(bn(l,-1,1)),Math.abs(l)<.9999999?(this._x=Math.atan2(-u,c),this._y=Math.atan2(-h,r)):(this._x=0,this._y=Math.atan2(a,f));break;case"XZY":this._z=Math.asin(-bn(o,-1,1)),Math.abs(o)<.9999999?(this._x=Math.atan2(d,c),this._y=Math.atan2(a,r)):(this._x=Math.atan2(-u,f),this._y=0);break;default:console.warn("THREE.Euler: .setFromRotationMatrix() encountered an unknown order: "+t)}return this._order=t,n===!0&&this._onChangeCallback(),this}setFromQuaternion(e,t,n){return Eh.makeRotationFromQuaternion(e),this.setFromRotationMatrix(Eh,t,n)}setFromVector3(e,t=this._order){return this.set(e.x,e.y,e.z,t)}reorder(e){return Th.setFromEuler(this),this.setFromQuaternion(Th,e)}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._order===this._order}fromArray(e){return this._x=e[0],this._y=e[1],this._z=e[2],e[3]!==void 0&&(this._order=e[3]),this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._order,e}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._order}}Ai.DEFAULT_ORDER="XYZ";class wu{constructor(){this.mask=1}set(e){this.mask=(1<<e|0)>>>0}enable(e){this.mask|=1<<e|0}enableAll(){this.mask=-1}toggle(e){this.mask^=1<<e|0}disable(e){this.mask&=~(1<<e|0)}disableAll(){this.mask=0}test(e){return(this.mask&e.mask)!==0}isEnabled(e){return(this.mask&(1<<e|0))!==0}}let Vg=0;const Ah=new G,mr=new Ws,Oi=new Gt,to=new G,fa=new G,Gg=new G,Wg=new Ws,Ch=new G(1,0,0),Rh=new G(0,1,0),Ph=new G(0,0,1),Lh={type:"added"},qg={type:"removed"},gr={type:"childadded",child:null},zl={type:"childremoved",child:null};class tn extends Kr{constructor(){super(),this.isObject3D=!0,Object.defineProperty(this,"id",{value:Vg++}),this.uuid=Wi(),this.name="",this.type="Object3D",this.parent=null,this.children=[],this.up=tn.DEFAULT_UP.clone();const e=new G,t=new Ai,n=new Ws,s=new G(1,1,1);function r(){n.setFromEuler(t,!1)}function o(){t.setFromQuaternion(n,void 0,!1)}t._onChange(r),n._onChange(o),Object.defineProperties(this,{position:{configurable:!0,enumerable:!0,value:e},rotation:{configurable:!0,enumerable:!0,value:t},quaternion:{configurable:!0,enumerable:!0,value:n},scale:{configurable:!0,enumerable:!0,value:s},modelViewMatrix:{value:new Gt},normalMatrix:{value:new at}}),this.matrix=new Gt,this.matrixWorld=new Gt,this.matrixAutoUpdate=tn.DEFAULT_MATRIX_AUTO_UPDATE,this.matrixWorldAutoUpdate=tn.DEFAULT_MATRIX_WORLD_AUTO_UPDATE,this.matrixWorldNeedsUpdate=!1,this.layers=new wu,this.visible=!0,this.castShadow=!1,this.receiveShadow=!1,this.frustumCulled=!0,this.renderOrder=0,this.animations=[],this.userData={}}onBeforeShadow(){}onAfterShadow(){}onBeforeRender(){}onAfterRender(){}applyMatrix4(e){this.matrixAutoUpdate&&this.updateMatrix(),this.matrix.premultiply(e),this.matrix.decompose(this.position,this.quaternion,this.scale)}applyQuaternion(e){return this.quaternion.premultiply(e),this}setRotationFromAxisAngle(e,t){this.quaternion.setFromAxisAngle(e,t)}setRotationFromEuler(e){this.quaternion.setFromEuler(e,!0)}setRotationFromMatrix(e){this.quaternion.setFromRotationMatrix(e)}setRotationFromQuaternion(e){this.quaternion.copy(e)}rotateOnAxis(e,t){return mr.setFromAxisAngle(e,t),this.quaternion.multiply(mr),this}rotateOnWorldAxis(e,t){return mr.setFromAxisAngle(e,t),this.quaternion.premultiply(mr),this}rotateX(e){return this.rotateOnAxis(Ch,e)}rotateY(e){return this.rotateOnAxis(Rh,e)}rotateZ(e){return this.rotateOnAxis(Ph,e)}translateOnAxis(e,t){return Ah.copy(e).applyQuaternion(this.quaternion),this.position.add(Ah.multiplyScalar(t)),this}translateX(e){return this.translateOnAxis(Ch,e)}translateY(e){return this.translateOnAxis(Rh,e)}translateZ(e){return this.translateOnAxis(Ph,e)}localToWorld(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(this.matrixWorld)}worldToLocal(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(Oi.copy(this.matrixWorld).invert())}lookAt(e,t,n){e.isVector3?to.copy(e):to.set(e,t,n);const s=this.parent;this.updateWorldMatrix(!0,!1),fa.setFromMatrixPosition(this.matrixWorld),this.isCamera||this.isLight?Oi.lookAt(fa,to,this.up):Oi.lookAt(to,fa,this.up),this.quaternion.setFromRotationMatrix(Oi),s&&(Oi.extractRotation(s.matrixWorld),mr.setFromRotationMatrix(Oi),this.quaternion.premultiply(mr.invert()))}add(e){if(arguments.length>1){for(let t=0;t<arguments.length;t++)this.add(arguments[t]);return this}return e===this?(console.error("THREE.Object3D.add: object can't be added as a child of itself.",e),this):(e&&e.isObject3D?(e.removeFromParent(),e.parent=this,this.children.push(e),e.dispatchEvent(Lh),gr.child=e,this.dispatchEvent(gr),gr.child=null):console.error("THREE.Object3D.add: object not an instance of THREE.Object3D.",e),this)}remove(e){if(arguments.length>1){for(let n=0;n<arguments.length;n++)this.remove(arguments[n]);return this}const t=this.children.indexOf(e);return t!==-1&&(e.parent=null,this.children.splice(t,1),e.dispatchEvent(qg),zl.child=e,this.dispatchEvent(zl),zl.child=null),this}removeFromParent(){const e=this.parent;return e!==null&&e.remove(this),this}clear(){return this.remove(...this.children)}attach(e){return this.updateWorldMatrix(!0,!1),Oi.copy(this.matrixWorld).invert(),e.parent!==null&&(e.parent.updateWorldMatrix(!0,!1),Oi.multiply(e.parent.matrixWorld)),e.applyMatrix4(Oi),e.removeFromParent(),e.parent=this,this.children.push(e),e.updateWorldMatrix(!1,!0),e.dispatchEvent(Lh),gr.child=e,this.dispatchEvent(gr),gr.child=null,this}getObjectById(e){return this.getObjectByProperty("id",e)}getObjectByName(e){return this.getObjectByProperty("name",e)}getObjectByProperty(e,t){if(this[e]===t)return this;for(let n=0,s=this.children.length;n<s;n++){const o=this.children[n].getObjectByProperty(e,t);if(o!==void 0)return o}}getObjectsByProperty(e,t,n=[]){this[e]===t&&n.push(this);const s=this.children;for(let r=0,o=s.length;r<o;r++)s[r].getObjectsByProperty(e,t,n);return n}getWorldPosition(e){return this.updateWorldMatrix(!0,!1),e.setFromMatrixPosition(this.matrixWorld)}getWorldQuaternion(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(fa,e,Gg),e}getWorldScale(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(fa,Wg,e),e}getWorldDirection(e){this.updateWorldMatrix(!0,!1);const t=this.matrixWorld.elements;return e.set(t[8],t[9],t[10]).normalize()}raycast(){}traverse(e){e(this);const t=this.children;for(let n=0,s=t.length;n<s;n++)t[n].traverse(e)}traverseVisible(e){if(this.visible===!1)return;e(this);const t=this.children;for(let n=0,s=t.length;n<s;n++)t[n].traverseVisible(e)}traverseAncestors(e){const t=this.parent;t!==null&&(e(t),t.traverseAncestors(e))}updateMatrix(){this.matrix.compose(this.position,this.quaternion,this.scale),this.matrixWorldNeedsUpdate=!0}updateMatrixWorld(e){this.matrixAutoUpdate&&this.updateMatrix(),(this.matrixWorldNeedsUpdate||e)&&(this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),this.matrixWorldNeedsUpdate=!1,e=!0);const t=this.children;for(let n=0,s=t.length;n<s;n++)t[n].updateMatrixWorld(e)}updateWorldMatrix(e,t){const n=this.parent;if(e===!0&&n!==null&&n.updateWorldMatrix(!0,!1),this.matrixAutoUpdate&&this.updateMatrix(),this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),t===!0){const s=this.children;for(let r=0,o=s.length;r<o;r++)s[r].updateWorldMatrix(!1,!0)}}toJSON(e){const t=e===void 0||typeof e=="string",n={};t&&(e={geometries:{},materials:{},textures:{},images:{},shapes:{},skeletons:{},animations:{},nodes:{}},n.metadata={version:4.6,type:"Object",generator:"Object3D.toJSON"});const s={};s.uuid=this.uuid,s.type=this.type,this.name!==""&&(s.name=this.name),this.castShadow===!0&&(s.castShadow=!0),this.receiveShadow===!0&&(s.receiveShadow=!0),this.visible===!1&&(s.visible=!1),this.frustumCulled===!1&&(s.frustumCulled=!1),this.renderOrder!==0&&(s.renderOrder=this.renderOrder),Object.keys(this.userData).length>0&&(s.userData=this.userData),s.layers=this.layers.mask,s.matrix=this.matrix.toArray(),s.up=this.up.toArray(),this.matrixAutoUpdate===!1&&(s.matrixAutoUpdate=!1),this.isInstancedMesh&&(s.type="InstancedMesh",s.count=this.count,s.instanceMatrix=this.instanceMatrix.toJSON(),this.instanceColor!==null&&(s.instanceColor=this.instanceColor.toJSON())),this.isBatchedMesh&&(s.type="BatchedMesh",s.perObjectFrustumCulled=this.perObjectFrustumCulled,s.sortObjects=this.sortObjects,s.drawRanges=this._drawRanges,s.reservedRanges=this._reservedRanges,s.visibility=this._visibility,s.active=this._active,s.bounds=this._bounds.map(a=>({boxInitialized:a.boxInitialized,boxMin:a.box.min.toArray(),boxMax:a.box.max.toArray(),sphereInitialized:a.sphereInitialized,sphereRadius:a.sphere.radius,sphereCenter:a.sphere.center.toArray()})),s.maxInstanceCount=this._maxInstanceCount,s.maxVertexCount=this._maxVertexCount,s.maxIndexCount=this._maxIndexCount,s.geometryInitialized=this._geometryInitialized,s.geometryCount=this._geometryCount,s.matricesTexture=this._matricesTexture.toJSON(e),this._colorsTexture!==null&&(s.colorsTexture=this._colorsTexture.toJSON(e)),this.boundingSphere!==null&&(s.boundingSphere={center:s.boundingSphere.center.toArray(),radius:s.boundingSphere.radius}),this.boundingBox!==null&&(s.boundingBox={min:s.boundingBox.min.toArray(),max:s.boundingBox.max.toArray()}));function r(a,l){return a[l.uuid]===void 0&&(a[l.uuid]=l.toJSON(e)),l.uuid}if(this.isScene)this.background&&(this.background.isColor?s.background=this.background.toJSON():this.background.isTexture&&(s.background=this.background.toJSON(e).uuid)),this.environment&&this.environment.isTexture&&this.environment.isRenderTargetTexture!==!0&&(s.environment=this.environment.toJSON(e).uuid);else if(this.isMesh||this.isLine||this.isPoints){s.geometry=r(e.geometries,this.geometry);const a=this.geometry.parameters;if(a!==void 0&&a.shapes!==void 0){const l=a.shapes;if(Array.isArray(l))for(let c=0,u=l.length;c<u;c++){const h=l[c];r(e.shapes,h)}else r(e.shapes,l)}}if(this.isSkinnedMesh&&(s.bindMode=this.bindMode,s.bindMatrix=this.bindMatrix.toArray(),this.skeleton!==void 0&&(r(e.skeletons,this.skeleton),s.skeleton=this.skeleton.uuid)),this.material!==void 0)if(Array.isArray(this.material)){const a=[];for(let l=0,c=this.material.length;l<c;l++)a.push(r(e.materials,this.material[l]));s.material=a}else s.material=r(e.materials,this.material);if(this.children.length>0){s.children=[];for(let a=0;a<this.children.length;a++)s.children.push(this.children[a].toJSON(e).object)}if(this.animations.length>0){s.animations=[];for(let a=0;a<this.animations.length;a++){const l=this.animations[a];s.animations.push(r(e.animations,l))}}if(t){const a=o(e.geometries),l=o(e.materials),c=o(e.textures),u=o(e.images),h=o(e.shapes),d=o(e.skeletons),f=o(e.animations),v=o(e.nodes);a.length>0&&(n.geometries=a),l.length>0&&(n.materials=l),c.length>0&&(n.textures=c),u.length>0&&(n.images=u),h.length>0&&(n.shapes=h),d.length>0&&(n.skeletons=d),f.length>0&&(n.animations=f),v.length>0&&(n.nodes=v)}return n.object=s,n;function o(a){const l=[];for(const c in a){const u=a[c];delete u.metadata,l.push(u)}return l}}clone(e){return new this.constructor().copy(this,e)}copy(e,t=!0){if(this.name=e.name,this.up.copy(e.up),this.position.copy(e.position),this.rotation.order=e.rotation.order,this.quaternion.copy(e.quaternion),this.scale.copy(e.scale),this.matrix.copy(e.matrix),this.matrixWorld.copy(e.matrixWorld),this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrixWorldAutoUpdate=e.matrixWorldAutoUpdate,this.matrixWorldNeedsUpdate=e.matrixWorldNeedsUpdate,this.layers.mask=e.layers.mask,this.visible=e.visible,this.castShadow=e.castShadow,this.receiveShadow=e.receiveShadow,this.frustumCulled=e.frustumCulled,this.renderOrder=e.renderOrder,this.animations=e.animations.slice(),this.userData=JSON.parse(JSON.stringify(e.userData)),t===!0)for(let n=0;n<e.children.length;n++){const s=e.children[n];this.add(s.clone())}return this}}tn.DEFAULT_UP=new G(0,1,0);tn.DEFAULT_MATRIX_AUTO_UPDATE=!0;tn.DEFAULT_MATRIX_WORLD_AUTO_UPDATE=!0;const oi=new G,Fi=new G,Hl=new G,ki=new G,vr=new G,_r=new G,Dh=new G,Vl=new G,Gl=new G,Wl=new G;class Qn{constructor(e=new G,t=new G,n=new G){this.a=e,this.b=t,this.c=n}static getNormal(e,t,n,s){s.subVectors(n,t),oi.subVectors(e,t),s.cross(oi);const r=s.lengthSq();return r>0?s.multiplyScalar(1/Math.sqrt(r)):s.set(0,0,0)}static getBarycoord(e,t,n,s,r){oi.subVectors(s,t),Fi.subVectors(n,t),Hl.subVectors(e,t);const o=oi.dot(oi),a=oi.dot(Fi),l=oi.dot(Hl),c=Fi.dot(Fi),u=Fi.dot(Hl),h=o*c-a*a;if(h===0)return r.set(0,0,0),null;const d=1/h,f=(c*l-a*u)*d,v=(o*u-a*l)*d;return r.set(1-f-v,v,f)}static containsPoint(e,t,n,s){return this.getBarycoord(e,t,n,s,ki)===null?!1:ki.x>=0&&ki.y>=0&&ki.x+ki.y<=1}static getInterpolation(e,t,n,s,r,o,a,l){return this.getBarycoord(e,t,n,s,ki)===null?(l.x=0,l.y=0,"z"in l&&(l.z=0),"w"in l&&(l.w=0),null):(l.setScalar(0),l.addScaledVector(r,ki.x),l.addScaledVector(o,ki.y),l.addScaledVector(a,ki.z),l)}static isFrontFacing(e,t,n,s){return oi.subVectors(n,t),Fi.subVectors(e,t),oi.cross(Fi).dot(s)<0}set(e,t,n){return this.a.copy(e),this.b.copy(t),this.c.copy(n),this}setFromPointsAndIndices(e,t,n,s){return this.a.copy(e[t]),this.b.copy(e[n]),this.c.copy(e[s]),this}setFromAttributeAndIndices(e,t,n,s){return this.a.fromBufferAttribute(e,t),this.b.fromBufferAttribute(e,n),this.c.fromBufferAttribute(e,s),this}clone(){return new this.constructor().copy(this)}copy(e){return this.a.copy(e.a),this.b.copy(e.b),this.c.copy(e.c),this}getArea(){return oi.subVectors(this.c,this.b),Fi.subVectors(this.a,this.b),oi.cross(Fi).length()*.5}getMidpoint(e){return e.addVectors(this.a,this.b).add(this.c).multiplyScalar(1/3)}getNormal(e){return Qn.getNormal(this.a,this.b,this.c,e)}getPlane(e){return e.setFromCoplanarPoints(this.a,this.b,this.c)}getBarycoord(e,t){return Qn.getBarycoord(e,this.a,this.b,this.c,t)}getInterpolation(e,t,n,s,r){return Qn.getInterpolation(e,this.a,this.b,this.c,t,n,s,r)}containsPoint(e){return Qn.containsPoint(e,this.a,this.b,this.c)}isFrontFacing(e){return Qn.isFrontFacing(this.a,this.b,this.c,e)}intersectsBox(e){return e.intersectsTriangle(this)}closestPointToPoint(e,t){const n=this.a,s=this.b,r=this.c;let o,a;vr.subVectors(s,n),_r.subVectors(r,n),Vl.subVectors(e,n);const l=vr.dot(Vl),c=_r.dot(Vl);if(l<=0&&c<=0)return t.copy(n);Gl.subVectors(e,s);const u=vr.dot(Gl),h=_r.dot(Gl);if(u>=0&&h<=u)return t.copy(s);const d=l*h-u*c;if(d<=0&&l>=0&&u<=0)return o=l/(l-u),t.copy(n).addScaledVector(vr,o);Wl.subVectors(e,r);const f=vr.dot(Wl),v=_r.dot(Wl);if(v>=0&&f<=v)return t.copy(r);const g=f*c-l*v;if(g<=0&&c>=0&&v<=0)return a=c/(c-v),t.copy(n).addScaledVector(_r,a);const m=u*v-f*h;if(m<=0&&h-u>=0&&f-v>=0)return Dh.subVectors(r,s),a=(h-u)/(h-u+(f-v)),t.copy(s).addScaledVector(Dh,a);const p=1/(m+g+d);return o=g*p,a=d*p,t.copy(n).addScaledVector(vr,o).addScaledVector(_r,a)}equals(e){return e.a.equals(this.a)&&e.b.equals(this.b)&&e.c.equals(this.c)}}const Hf={aliceblue:15792383,antiquewhite:16444375,aqua:65535,aquamarine:8388564,azure:15794175,beige:16119260,bisque:16770244,black:0,blanchedalmond:16772045,blue:255,blueviolet:9055202,brown:10824234,burlywood:14596231,cadetblue:6266528,chartreuse:8388352,chocolate:13789470,coral:16744272,cornflowerblue:6591981,cornsilk:16775388,crimson:14423100,cyan:65535,darkblue:139,darkcyan:35723,darkgoldenrod:12092939,darkgray:11119017,darkgreen:25600,darkgrey:11119017,darkkhaki:12433259,darkmagenta:9109643,darkolivegreen:5597999,darkorange:16747520,darkorchid:10040012,darkred:9109504,darksalmon:15308410,darkseagreen:9419919,darkslateblue:4734347,darkslategray:3100495,darkslategrey:3100495,darkturquoise:52945,darkviolet:9699539,deeppink:16716947,deepskyblue:49151,dimgray:6908265,dimgrey:6908265,dodgerblue:2003199,firebrick:11674146,floralwhite:16775920,forestgreen:2263842,fuchsia:16711935,gainsboro:14474460,ghostwhite:16316671,gold:16766720,goldenrod:14329120,gray:8421504,green:32768,greenyellow:11403055,grey:8421504,honeydew:15794160,hotpink:16738740,indianred:13458524,indigo:4915330,ivory:16777200,khaki:15787660,lavender:15132410,lavenderblush:16773365,lawngreen:8190976,lemonchiffon:16775885,lightblue:11393254,lightcoral:15761536,lightcyan:14745599,lightgoldenrodyellow:16448210,lightgray:13882323,lightgreen:9498256,lightgrey:13882323,lightpink:16758465,lightsalmon:16752762,lightseagreen:2142890,lightskyblue:8900346,lightslategray:7833753,lightslategrey:7833753,lightsteelblue:11584734,lightyellow:16777184,lime:65280,limegreen:3329330,linen:16445670,magenta:16711935,maroon:8388608,mediumaquamarine:6737322,mediumblue:205,mediumorchid:12211667,mediumpurple:9662683,mediumseagreen:3978097,mediumslateblue:8087790,mediumspringgreen:64154,mediumturquoise:4772300,mediumvioletred:13047173,midnightblue:1644912,mintcream:16121850,mistyrose:16770273,moccasin:16770229,navajowhite:16768685,navy:128,oldlace:16643558,olive:8421376,olivedrab:7048739,orange:16753920,orangered:16729344,orchid:14315734,palegoldenrod:15657130,palegreen:10025880,paleturquoise:11529966,palevioletred:14381203,papayawhip:16773077,peachpuff:16767673,peru:13468991,pink:16761035,plum:14524637,powderblue:11591910,purple:8388736,rebeccapurple:6697881,red:16711680,rosybrown:12357519,royalblue:4286945,saddlebrown:9127187,salmon:16416882,sandybrown:16032864,seagreen:3050327,seashell:16774638,sienna:10506797,silver:12632256,skyblue:8900331,slateblue:6970061,slategray:7372944,slategrey:7372944,snow:16775930,springgreen:65407,steelblue:4620980,tan:13808780,teal:32896,thistle:14204888,tomato:16737095,turquoise:4251856,violet:15631086,wheat:16113331,white:16777215,whitesmoke:16119285,yellow:16776960,yellowgreen:10145074},is={h:0,s:0,l:0},no={h:0,s:0,l:0};function ql(i,e,t){return t<0&&(t+=1),t>1&&(t-=1),t<1/6?i+(e-i)*6*t:t<1/2?e:t<2/3?i+(e-i)*6*(2/3-t):i}class st{constructor(e,t,n){return this.isColor=!0,this.r=1,this.g=1,this.b=1,this.set(e,t,n)}set(e,t,n){if(t===void 0&&n===void 0){const s=e;s&&s.isColor?this.copy(s):typeof s=="number"?this.setHex(s):typeof s=="string"&&this.setStyle(s)}else this.setRGB(e,t,n);return this}setScalar(e){return this.r=e,this.g=e,this.b=e,this}setHex(e,t=Mi){return e=Math.floor(e),this.r=(e>>16&255)/255,this.g=(e>>8&255)/255,this.b=(e&255)/255,wt.toWorkingColorSpace(this,t),this}setRGB(e,t,n,s=wt.workingColorSpace){return this.r=e,this.g=t,this.b=n,wt.toWorkingColorSpace(this,s),this}setHSL(e,t,n,s=wt.workingColorSpace){if(e=Mu(e,1),t=bn(t,0,1),n=bn(n,0,1),t===0)this.r=this.g=this.b=n;else{const r=n<=.5?n*(1+t):n+t-n*t,o=2*n-r;this.r=ql(o,r,e+1/3),this.g=ql(o,r,e),this.b=ql(o,r,e-1/3)}return wt.toWorkingColorSpace(this,s),this}setStyle(e,t=Mi){function n(r){r!==void 0&&parseFloat(r)<1&&console.warn("THREE.Color: Alpha component of "+e+" will be ignored.")}let s;if(s=/^(\w+)\(([^\)]*)\)/.exec(e)){let r;const o=s[1],a=s[2];switch(o){case"rgb":case"rgba":if(r=/^\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(a))return n(r[4]),this.setRGB(Math.min(255,parseInt(r[1],10))/255,Math.min(255,parseInt(r[2],10))/255,Math.min(255,parseInt(r[3],10))/255,t);if(r=/^\s*(\d+)\%\s*,\s*(\d+)\%\s*,\s*(\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(a))return n(r[4]),this.setRGB(Math.min(100,parseInt(r[1],10))/100,Math.min(100,parseInt(r[2],10))/100,Math.min(100,parseInt(r[3],10))/100,t);break;case"hsl":case"hsla":if(r=/^\s*(\d*\.?\d+)\s*,\s*(\d*\.?\d+)\%\s*,\s*(\d*\.?\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(a))return n(r[4]),this.setHSL(parseFloat(r[1])/360,parseFloat(r[2])/100,parseFloat(r[3])/100,t);break;default:console.warn("THREE.Color: Unknown color model "+e)}}else if(s=/^\#([A-Fa-f\d]+)$/.exec(e)){const r=s[1],o=r.length;if(o===3)return this.setRGB(parseInt(r.charAt(0),16)/15,parseInt(r.charAt(1),16)/15,parseInt(r.charAt(2),16)/15,t);if(o===6)return this.setHex(parseInt(r,16),t);console.warn("THREE.Color: Invalid hex color "+e)}else if(e&&e.length>0)return this.setColorName(e,t);return this}setColorName(e,t=Mi){const n=Hf[e.toLowerCase()];return n!==void 0?this.setHex(n,t):console.warn("THREE.Color: Unknown color "+e),this}clone(){return new this.constructor(this.r,this.g,this.b)}copy(e){return this.r=e.r,this.g=e.g,this.b=e.b,this}copySRGBToLinear(e){return this.r=kr(e.r),this.g=kr(e.g),this.b=kr(e.b),this}copyLinearToSRGB(e){return this.r=Dl(e.r),this.g=Dl(e.g),this.b=Dl(e.b),this}convertSRGBToLinear(){return this.copySRGBToLinear(this),this}convertLinearToSRGB(){return this.copyLinearToSRGB(this),this}getHex(e=Mi){return wt.fromWorkingColorSpace(yn.copy(this),e),Math.round(bn(yn.r*255,0,255))*65536+Math.round(bn(yn.g*255,0,255))*256+Math.round(bn(yn.b*255,0,255))}getHexString(e=Mi){return("000000"+this.getHex(e).toString(16)).slice(-6)}getHSL(e,t=wt.workingColorSpace){wt.fromWorkingColorSpace(yn.copy(this),t);const n=yn.r,s=yn.g,r=yn.b,o=Math.max(n,s,r),a=Math.min(n,s,r);let l,c;const u=(a+o)/2;if(a===o)l=0,c=0;else{const h=o-a;switch(c=u<=.5?h/(o+a):h/(2-o-a),o){case n:l=(s-r)/h+(s<r?6:0);break;case s:l=(r-n)/h+2;break;case r:l=(n-s)/h+4;break}l/=6}return e.h=l,e.s=c,e.l=u,e}getRGB(e,t=wt.workingColorSpace){return wt.fromWorkingColorSpace(yn.copy(this),t),e.r=yn.r,e.g=yn.g,e.b=yn.b,e}getStyle(e=Mi){wt.fromWorkingColorSpace(yn.copy(this),e);const t=yn.r,n=yn.g,s=yn.b;return e!==Mi?`color(${e} ${t.toFixed(3)} ${n.toFixed(3)} ${s.toFixed(3)})`:`rgb(${Math.round(t*255)},${Math.round(n*255)},${Math.round(s*255)})`}offsetHSL(e,t,n){return this.getHSL(is),this.setHSL(is.h+e,is.s+t,is.l+n)}add(e){return this.r+=e.r,this.g+=e.g,this.b+=e.b,this}addColors(e,t){return this.r=e.r+t.r,this.g=e.g+t.g,this.b=e.b+t.b,this}addScalar(e){return this.r+=e,this.g+=e,this.b+=e,this}sub(e){return this.r=Math.max(0,this.r-e.r),this.g=Math.max(0,this.g-e.g),this.b=Math.max(0,this.b-e.b),this}multiply(e){return this.r*=e.r,this.g*=e.g,this.b*=e.b,this}multiplyScalar(e){return this.r*=e,this.g*=e,this.b*=e,this}lerp(e,t){return this.r+=(e.r-this.r)*t,this.g+=(e.g-this.g)*t,this.b+=(e.b-this.b)*t,this}lerpColors(e,t,n){return this.r=e.r+(t.r-e.r)*n,this.g=e.g+(t.g-e.g)*n,this.b=e.b+(t.b-e.b)*n,this}lerpHSL(e,t){this.getHSL(is),e.getHSL(no);const n=Ea(is.h,no.h,t),s=Ea(is.s,no.s,t),r=Ea(is.l,no.l,t);return this.setHSL(n,s,r),this}setFromVector3(e){return this.r=e.x,this.g=e.y,this.b=e.z,this}applyMatrix3(e){const t=this.r,n=this.g,s=this.b,r=e.elements;return this.r=r[0]*t+r[3]*n+r[6]*s,this.g=r[1]*t+r[4]*n+r[7]*s,this.b=r[2]*t+r[5]*n+r[8]*s,this}equals(e){return e.r===this.r&&e.g===this.g&&e.b===this.b}fromArray(e,t=0){return this.r=e[t],this.g=e[t+1],this.b=e[t+2],this}toArray(e=[],t=0){return e[t]=this.r,e[t+1]=this.g,e[t+2]=this.b,e}fromBufferAttribute(e,t){return this.r=e.getX(t),this.g=e.getY(t),this.b=e.getZ(t),this}toJSON(){return this.getHex()}*[Symbol.iterator](){yield this.r,yield this.g,yield this.b}}const yn=new st;st.NAMES=Hf;let Xg=0;class Ys extends Kr{constructor(){super(),this.isMaterial=!0,Object.defineProperty(this,"id",{value:Xg++}),this.uuid=Wi(),this.name="",this.type="Material",this.blending=Ur,this.side=hs,this.vertexColors=!1,this.opacity=1,this.transparent=!1,this.alphaHash=!1,this.blendSrc=xc,this.blendDst=yc,this.blendEquation=Ns,this.blendSrcAlpha=null,this.blendDstAlpha=null,this.blendEquationAlpha=null,this.blendColor=new st(0,0,0),this.blendAlpha=0,this.depthFunc=Bo,this.depthTest=!0,this.depthWrite=!0,this.stencilWriteMask=255,this.stencilFunc=_h,this.stencilRef=0,this.stencilFuncMask=255,this.stencilFail=cr,this.stencilZFail=cr,this.stencilZPass=cr,this.stencilWrite=!1,this.clippingPlanes=null,this.clipIntersection=!1,this.clipShadows=!1,this.shadowSide=null,this.colorWrite=!0,this.precision=null,this.polygonOffset=!1,this.polygonOffsetFactor=0,this.polygonOffsetUnits=0,this.dithering=!1,this.alphaToCoverage=!1,this.premultipliedAlpha=!1,this.forceSinglePass=!1,this.visible=!0,this.toneMapped=!0,this.userData={},this.version=0,this._alphaTest=0}get alphaTest(){return this._alphaTest}set alphaTest(e){this._alphaTest>0!=e>0&&this.version++,this._alphaTest=e}onBeforeRender(){}onBeforeCompile(){}customProgramCacheKey(){return this.onBeforeCompile.toString()}setValues(e){if(e!==void 0)for(const t in e){const n=e[t];if(n===void 0){console.warn(`THREE.Material: parameter '${t}' has value of undefined.`);continue}const s=this[t];if(s===void 0){console.warn(`THREE.Material: '${t}' is not a property of THREE.${this.type}.`);continue}s&&s.isColor?s.set(n):s&&s.isVector3&&n&&n.isVector3?s.copy(n):this[t]=n}}toJSON(e){const t=e===void 0||typeof e=="string";t&&(e={textures:{},images:{}});const n={metadata:{version:4.6,type:"Material",generator:"Material.toJSON"}};n.uuid=this.uuid,n.type=this.type,this.name!==""&&(n.name=this.name),this.color&&this.color.isColor&&(n.color=this.color.getHex()),this.roughness!==void 0&&(n.roughness=this.roughness),this.metalness!==void 0&&(n.metalness=this.metalness),this.sheen!==void 0&&(n.sheen=this.sheen),this.sheenColor&&this.sheenColor.isColor&&(n.sheenColor=this.sheenColor.getHex()),this.sheenRoughness!==void 0&&(n.sheenRoughness=this.sheenRoughness),this.emissive&&this.emissive.isColor&&(n.emissive=this.emissive.getHex()),this.emissiveIntensity!==void 0&&this.emissiveIntensity!==1&&(n.emissiveIntensity=this.emissiveIntensity),this.specular&&this.specular.isColor&&(n.specular=this.specular.getHex()),this.specularIntensity!==void 0&&(n.specularIntensity=this.specularIntensity),this.specularColor&&this.specularColor.isColor&&(n.specularColor=this.specularColor.getHex()),this.shininess!==void 0&&(n.shininess=this.shininess),this.clearcoat!==void 0&&(n.clearcoat=this.clearcoat),this.clearcoatRoughness!==void 0&&(n.clearcoatRoughness=this.clearcoatRoughness),this.clearcoatMap&&this.clearcoatMap.isTexture&&(n.clearcoatMap=this.clearcoatMap.toJSON(e).uuid),this.clearcoatRoughnessMap&&this.clearcoatRoughnessMap.isTexture&&(n.clearcoatRoughnessMap=this.clearcoatRoughnessMap.toJSON(e).uuid),this.clearcoatNormalMap&&this.clearcoatNormalMap.isTexture&&(n.clearcoatNormalMap=this.clearcoatNormalMap.toJSON(e).uuid,n.clearcoatNormalScale=this.clearcoatNormalScale.toArray()),this.dispersion!==void 0&&(n.dispersion=this.dispersion),this.iridescence!==void 0&&(n.iridescence=this.iridescence),this.iridescenceIOR!==void 0&&(n.iridescenceIOR=this.iridescenceIOR),this.iridescenceThicknessRange!==void 0&&(n.iridescenceThicknessRange=this.iridescenceThicknessRange),this.iridescenceMap&&this.iridescenceMap.isTexture&&(n.iridescenceMap=this.iridescenceMap.toJSON(e).uuid),this.iridescenceThicknessMap&&this.iridescenceThicknessMap.isTexture&&(n.iridescenceThicknessMap=this.iridescenceThicknessMap.toJSON(e).uuid),this.anisotropy!==void 0&&(n.anisotropy=this.anisotropy),this.anisotropyRotation!==void 0&&(n.anisotropyRotation=this.anisotropyRotation),this.anisotropyMap&&this.anisotropyMap.isTexture&&(n.anisotropyMap=this.anisotropyMap.toJSON(e).uuid),this.map&&this.map.isTexture&&(n.map=this.map.toJSON(e).uuid),this.matcap&&this.matcap.isTexture&&(n.matcap=this.matcap.toJSON(e).uuid),this.alphaMap&&this.alphaMap.isTexture&&(n.alphaMap=this.alphaMap.toJSON(e).uuid),this.lightMap&&this.lightMap.isTexture&&(n.lightMap=this.lightMap.toJSON(e).uuid,n.lightMapIntensity=this.lightMapIntensity),this.aoMap&&this.aoMap.isTexture&&(n.aoMap=this.aoMap.toJSON(e).uuid,n.aoMapIntensity=this.aoMapIntensity),this.bumpMap&&this.bumpMap.isTexture&&(n.bumpMap=this.bumpMap.toJSON(e).uuid,n.bumpScale=this.bumpScale),this.normalMap&&this.normalMap.isTexture&&(n.normalMap=this.normalMap.toJSON(e).uuid,n.normalMapType=this.normalMapType,n.normalScale=this.normalScale.toArray()),this.displacementMap&&this.displacementMap.isTexture&&(n.displacementMap=this.displacementMap.toJSON(e).uuid,n.displacementScale=this.displacementScale,n.displacementBias=this.displacementBias),this.roughnessMap&&this.roughnessMap.isTexture&&(n.roughnessMap=this.roughnessMap.toJSON(e).uuid),this.metalnessMap&&this.metalnessMap.isTexture&&(n.metalnessMap=this.metalnessMap.toJSON(e).uuid),this.emissiveMap&&this.emissiveMap.isTexture&&(n.emissiveMap=this.emissiveMap.toJSON(e).uuid),this.specularMap&&this.specularMap.isTexture&&(n.specularMap=this.specularMap.toJSON(e).uuid),this.specularIntensityMap&&this.specularIntensityMap.isTexture&&(n.specularIntensityMap=this.specularIntensityMap.toJSON(e).uuid),this.specularColorMap&&this.specularColorMap.isTexture&&(n.specularColorMap=this.specularColorMap.toJSON(e).uuid),this.envMap&&this.envMap.isTexture&&(n.envMap=this.envMap.toJSON(e).uuid,this.combine!==void 0&&(n.combine=this.combine)),this.envMapRotation!==void 0&&(n.envMapRotation=this.envMapRotation.toArray()),this.envMapIntensity!==void 0&&(n.envMapIntensity=this.envMapIntensity),this.reflectivity!==void 0&&(n.reflectivity=this.reflectivity),this.refractionRatio!==void 0&&(n.refractionRatio=this.refractionRatio),this.gradientMap&&this.gradientMap.isTexture&&(n.gradientMap=this.gradientMap.toJSON(e).uuid),this.transmission!==void 0&&(n.transmission=this.transmission),this.transmissionMap&&this.transmissionMap.isTexture&&(n.transmissionMap=this.transmissionMap.toJSON(e).uuid),this.thickness!==void 0&&(n.thickness=this.thickness),this.thicknessMap&&this.thicknessMap.isTexture&&(n.thicknessMap=this.thicknessMap.toJSON(e).uuid),this.attenuationDistance!==void 0&&this.attenuationDistance!==1/0&&(n.attenuationDistance=this.attenuationDistance),this.attenuationColor!==void 0&&(n.attenuationColor=this.attenuationColor.getHex()),this.size!==void 0&&(n.size=this.size),this.shadowSide!==null&&(n.shadowSide=this.shadowSide),this.sizeAttenuation!==void 0&&(n.sizeAttenuation=this.sizeAttenuation),this.blending!==Ur&&(n.blending=this.blending),this.side!==hs&&(n.side=this.side),this.vertexColors===!0&&(n.vertexColors=!0),this.opacity<1&&(n.opacity=this.opacity),this.transparent===!0&&(n.transparent=!0),this.blendSrc!==xc&&(n.blendSrc=this.blendSrc),this.blendDst!==yc&&(n.blendDst=this.blendDst),this.blendEquation!==Ns&&(n.blendEquation=this.blendEquation),this.blendSrcAlpha!==null&&(n.blendSrcAlpha=this.blendSrcAlpha),this.blendDstAlpha!==null&&(n.blendDstAlpha=this.blendDstAlpha),this.blendEquationAlpha!==null&&(n.blendEquationAlpha=this.blendEquationAlpha),this.blendColor&&this.blendColor.isColor&&(n.blendColor=this.blendColor.getHex()),this.blendAlpha!==0&&(n.blendAlpha=this.blendAlpha),this.depthFunc!==Bo&&(n.depthFunc=this.depthFunc),this.depthTest===!1&&(n.depthTest=this.depthTest),this.depthWrite===!1&&(n.depthWrite=this.depthWrite),this.colorWrite===!1&&(n.colorWrite=this.colorWrite),this.stencilWriteMask!==255&&(n.stencilWriteMask=this.stencilWriteMask),this.stencilFunc!==_h&&(n.stencilFunc=this.stencilFunc),this.stencilRef!==0&&(n.stencilRef=this.stencilRef),this.stencilFuncMask!==255&&(n.stencilFuncMask=this.stencilFuncMask),this.stencilFail!==cr&&(n.stencilFail=this.stencilFail),this.stencilZFail!==cr&&(n.stencilZFail=this.stencilZFail),this.stencilZPass!==cr&&(n.stencilZPass=this.stencilZPass),this.stencilWrite===!0&&(n.stencilWrite=this.stencilWrite),this.rotation!==void 0&&this.rotation!==0&&(n.rotation=this.rotation),this.polygonOffset===!0&&(n.polygonOffset=!0),this.polygonOffsetFactor!==0&&(n.polygonOffsetFactor=this.polygonOffsetFactor),this.polygonOffsetUnits!==0&&(n.polygonOffsetUnits=this.polygonOffsetUnits),this.linewidth!==void 0&&this.linewidth!==1&&(n.linewidth=this.linewidth),this.dashSize!==void 0&&(n.dashSize=this.dashSize),this.gapSize!==void 0&&(n.gapSize=this.gapSize),this.scale!==void 0&&(n.scale=this.scale),this.dithering===!0&&(n.dithering=!0),this.alphaTest>0&&(n.alphaTest=this.alphaTest),this.alphaHash===!0&&(n.alphaHash=!0),this.alphaToCoverage===!0&&(n.alphaToCoverage=!0),this.premultipliedAlpha===!0&&(n.premultipliedAlpha=!0),this.forceSinglePass===!0&&(n.forceSinglePass=!0),this.wireframe===!0&&(n.wireframe=!0),this.wireframeLinewidth>1&&(n.wireframeLinewidth=this.wireframeLinewidth),this.wireframeLinecap!=="round"&&(n.wireframeLinecap=this.wireframeLinecap),this.wireframeLinejoin!=="round"&&(n.wireframeLinejoin=this.wireframeLinejoin),this.flatShading===!0&&(n.flatShading=!0),this.visible===!1&&(n.visible=!1),this.toneMapped===!1&&(n.toneMapped=!1),this.fog===!1&&(n.fog=!1),Object.keys(this.userData).length>0&&(n.userData=this.userData);function s(r){const o=[];for(const a in r){const l=r[a];delete l.metadata,o.push(l)}return o}if(t){const r=s(e.textures),o=s(e.images);r.length>0&&(n.textures=r),o.length>0&&(n.images=o)}return n}clone(){return new this.constructor().copy(this)}copy(e){this.name=e.name,this.blending=e.blending,this.side=e.side,this.vertexColors=e.vertexColors,this.opacity=e.opacity,this.transparent=e.transparent,this.blendSrc=e.blendSrc,this.blendDst=e.blendDst,this.blendEquation=e.blendEquation,this.blendSrcAlpha=e.blendSrcAlpha,this.blendDstAlpha=e.blendDstAlpha,this.blendEquationAlpha=e.blendEquationAlpha,this.blendColor.copy(e.blendColor),this.blendAlpha=e.blendAlpha,this.depthFunc=e.depthFunc,this.depthTest=e.depthTest,this.depthWrite=e.depthWrite,this.stencilWriteMask=e.stencilWriteMask,this.stencilFunc=e.stencilFunc,this.stencilRef=e.stencilRef,this.stencilFuncMask=e.stencilFuncMask,this.stencilFail=e.stencilFail,this.stencilZFail=e.stencilZFail,this.stencilZPass=e.stencilZPass,this.stencilWrite=e.stencilWrite;const t=e.clippingPlanes;let n=null;if(t!==null){const s=t.length;n=new Array(s);for(let r=0;r!==s;++r)n[r]=t[r].clone()}return this.clippingPlanes=n,this.clipIntersection=e.clipIntersection,this.clipShadows=e.clipShadows,this.shadowSide=e.shadowSide,this.colorWrite=e.colorWrite,this.precision=e.precision,this.polygonOffset=e.polygonOffset,this.polygonOffsetFactor=e.polygonOffsetFactor,this.polygonOffsetUnits=e.polygonOffsetUnits,this.dithering=e.dithering,this.alphaTest=e.alphaTest,this.alphaHash=e.alphaHash,this.alphaToCoverage=e.alphaToCoverage,this.premultipliedAlpha=e.premultipliedAlpha,this.forceSinglePass=e.forceSinglePass,this.visible=e.visible,this.toneMapped=e.toneMapped,this.userData=JSON.parse(JSON.stringify(e.userData)),this}dispose(){this.dispatchEvent({type:"dispose"})}set needsUpdate(e){e===!0&&this.version++}onBuild(){console.warn("Material: onBuild() has been removed.")}}class Ta extends Ys{constructor(e){super(),this.isMeshBasicMaterial=!0,this.type="MeshBasicMaterial",this.color=new st(16777215),this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.specularMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new Ai,this.combine=Mf,this.reflectivity=1,this.refractionRatio=.98,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.lightMap=e.lightMap,this.lightMapIntensity=e.lightMapIntensity,this.aoMap=e.aoMap,this.aoMapIntensity=e.aoMapIntensity,this.specularMap=e.specularMap,this.alphaMap=e.alphaMap,this.envMap=e.envMap,this.envMapRotation.copy(e.envMapRotation),this.combine=e.combine,this.reflectivity=e.reflectivity,this.refractionRatio=e.refractionRatio,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.wireframeLinecap=e.wireframeLinecap,this.wireframeLinejoin=e.wireframeLinejoin,this.fog=e.fog,this}}const Kt=new G,io=new qe;class pi{constructor(e,t,n=!1){if(Array.isArray(e))throw new TypeError("THREE.BufferAttribute: array should be a Typed Array.");this.isBufferAttribute=!0,this.name="",this.array=e,this.itemSize=t,this.count=e!==void 0?e.length/t:0,this.normalized=n,this.usage=Zc,this._updateRange={offset:0,count:-1},this.updateRanges=[],this.gpuType=Hi,this.version=0}onUploadCallback(){}set needsUpdate(e){e===!0&&this.version++}get updateRange(){return Fr("THREE.BufferAttribute: updateRange() is deprecated and will be removed in r169. Use addUpdateRange() instead."),this._updateRange}setUsage(e){return this.usage=e,this}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}copy(e){return this.name=e.name,this.array=new e.array.constructor(e.array),this.itemSize=e.itemSize,this.count=e.count,this.normalized=e.normalized,this.usage=e.usage,this.gpuType=e.gpuType,this}copyAt(e,t,n){e*=this.itemSize,n*=t.itemSize;for(let s=0,r=this.itemSize;s<r;s++)this.array[e+s]=t.array[n+s];return this}copyArray(e){return this.array.set(e),this}applyMatrix3(e){if(this.itemSize===2)for(let t=0,n=this.count;t<n;t++)io.fromBufferAttribute(this,t),io.applyMatrix3(e),this.setXY(t,io.x,io.y);else if(this.itemSize===3)for(let t=0,n=this.count;t<n;t++)Kt.fromBufferAttribute(this,t),Kt.applyMatrix3(e),this.setXYZ(t,Kt.x,Kt.y,Kt.z);return this}applyMatrix4(e){for(let t=0,n=this.count;t<n;t++)Kt.fromBufferAttribute(this,t),Kt.applyMatrix4(e),this.setXYZ(t,Kt.x,Kt.y,Kt.z);return this}applyNormalMatrix(e){for(let t=0,n=this.count;t<n;t++)Kt.fromBufferAttribute(this,t),Kt.applyNormalMatrix(e),this.setXYZ(t,Kt.x,Kt.y,Kt.z);return this}transformDirection(e){for(let t=0,n=this.count;t<n;t++)Kt.fromBufferAttribute(this,t),Kt.transformDirection(e),this.setXYZ(t,Kt.x,Kt.y,Kt.z);return this}set(e,t=0){return this.array.set(e,t),this}getComponent(e,t){let n=this.array[e*this.itemSize+t];return this.normalized&&(n=hi(n,this.array)),n}setComponent(e,t,n){return this.normalized&&(n=At(n,this.array)),this.array[e*this.itemSize+t]=n,this}getX(e){let t=this.array[e*this.itemSize];return this.normalized&&(t=hi(t,this.array)),t}setX(e,t){return this.normalized&&(t=At(t,this.array)),this.array[e*this.itemSize]=t,this}getY(e){let t=this.array[e*this.itemSize+1];return this.normalized&&(t=hi(t,this.array)),t}setY(e,t){return this.normalized&&(t=At(t,this.array)),this.array[e*this.itemSize+1]=t,this}getZ(e){let t=this.array[e*this.itemSize+2];return this.normalized&&(t=hi(t,this.array)),t}setZ(e,t){return this.normalized&&(t=At(t,this.array)),this.array[e*this.itemSize+2]=t,this}getW(e){let t=this.array[e*this.itemSize+3];return this.normalized&&(t=hi(t,this.array)),t}setW(e,t){return this.normalized&&(t=At(t,this.array)),this.array[e*this.itemSize+3]=t,this}setXY(e,t,n){return e*=this.itemSize,this.normalized&&(t=At(t,this.array),n=At(n,this.array)),this.array[e+0]=t,this.array[e+1]=n,this}setXYZ(e,t,n,s){return e*=this.itemSize,this.normalized&&(t=At(t,this.array),n=At(n,this.array),s=At(s,this.array)),this.array[e+0]=t,this.array[e+1]=n,this.array[e+2]=s,this}setXYZW(e,t,n,s,r){return e*=this.itemSize,this.normalized&&(t=At(t,this.array),n=At(n,this.array),s=At(s,this.array),r=At(r,this.array)),this.array[e+0]=t,this.array[e+1]=n,this.array[e+2]=s,this.array[e+3]=r,this}onUpload(e){return this.onUploadCallback=e,this}clone(){return new this.constructor(this.array,this.itemSize).copy(this)}toJSON(){const e={itemSize:this.itemSize,type:this.array.constructor.name,array:Array.from(this.array),normalized:this.normalized};return this.name!==""&&(e.name=this.name),this.usage!==Zc&&(e.usage=this.usage),e}}class Vf extends pi{constructor(e,t,n){super(new Uint16Array(e),t,n)}}class Gf extends pi{constructor(e,t,n){super(new Uint32Array(e),t,n)}}class Mn extends pi{constructor(e,t,n){super(new Float32Array(e),t,n)}}let $g=0;const Kn=new Gt,Xl=new tn,xr=new G,zn=new Ba,pa=new Ba,hn=new G;class Xn extends Kr{constructor(){super(),this.isBufferGeometry=!0,Object.defineProperty(this,"id",{value:$g++}),this.uuid=Wi(),this.name="",this.type="BufferGeometry",this.index=null,this.attributes={},this.morphAttributes={},this.morphTargetsRelative=!1,this.groups=[],this.boundingBox=null,this.boundingSphere=null,this.drawRange={start:0,count:1/0},this.userData={}}getIndex(){return this.index}setIndex(e){return Array.isArray(e)?this.index=new(kf(e)?Gf:Vf)(e,1):this.index=e,this}getAttribute(e){return this.attributes[e]}setAttribute(e,t){return this.attributes[e]=t,this}deleteAttribute(e){return delete this.attributes[e],this}hasAttribute(e){return this.attributes[e]!==void 0}addGroup(e,t,n=0){this.groups.push({start:e,count:t,materialIndex:n})}clearGroups(){this.groups=[]}setDrawRange(e,t){this.drawRange.start=e,this.drawRange.count=t}applyMatrix4(e){const t=this.attributes.position;t!==void 0&&(t.applyMatrix4(e),t.needsUpdate=!0);const n=this.attributes.normal;if(n!==void 0){const r=new at().getNormalMatrix(e);n.applyNormalMatrix(r),n.needsUpdate=!0}const s=this.attributes.tangent;return s!==void 0&&(s.transformDirection(e),s.needsUpdate=!0),this.boundingBox!==null&&this.computeBoundingBox(),this.boundingSphere!==null&&this.computeBoundingSphere(),this}applyQuaternion(e){return Kn.makeRotationFromQuaternion(e),this.applyMatrix4(Kn),this}rotateX(e){return Kn.makeRotationX(e),this.applyMatrix4(Kn),this}rotateY(e){return Kn.makeRotationY(e),this.applyMatrix4(Kn),this}rotateZ(e){return Kn.makeRotationZ(e),this.applyMatrix4(Kn),this}translate(e,t,n){return Kn.makeTranslation(e,t,n),this.applyMatrix4(Kn),this}scale(e,t,n){return Kn.makeScale(e,t,n),this.applyMatrix4(Kn),this}lookAt(e){return Xl.lookAt(e),Xl.updateMatrix(),this.applyMatrix4(Xl.matrix),this}center(){return this.computeBoundingBox(),this.boundingBox.getCenter(xr).negate(),this.translate(xr.x,xr.y,xr.z),this}setFromPoints(e){const t=[];for(let n=0,s=e.length;n<s;n++){const r=e[n];t.push(r.x,r.y,r.z||0)}return this.setAttribute("position",new Mn(t,3)),this}computeBoundingBox(){this.boundingBox===null&&(this.boundingBox=new Ba);const e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingBox(): GLBufferAttribute requires a manual bounding box.",this),this.boundingBox.set(new G(-1/0,-1/0,-1/0),new G(1/0,1/0,1/0));return}if(e!==void 0){if(this.boundingBox.setFromBufferAttribute(e),t)for(let n=0,s=t.length;n<s;n++){const r=t[n];zn.setFromBufferAttribute(r),this.morphTargetsRelative?(hn.addVectors(this.boundingBox.min,zn.min),this.boundingBox.expandByPoint(hn),hn.addVectors(this.boundingBox.max,zn.max),this.boundingBox.expandByPoint(hn)):(this.boundingBox.expandByPoint(zn.min),this.boundingBox.expandByPoint(zn.max))}}else this.boundingBox.makeEmpty();(isNaN(this.boundingBox.min.x)||isNaN(this.boundingBox.min.y)||isNaN(this.boundingBox.min.z))&&console.error('THREE.BufferGeometry.computeBoundingBox(): Computed min/max have NaN values. The "position" attribute is likely to have NaN values.',this)}computeBoundingSphere(){this.boundingSphere===null&&(this.boundingSphere=new sl);const e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingSphere(): GLBufferAttribute requires a manual bounding sphere.",this),this.boundingSphere.set(new G,1/0);return}if(e){const n=this.boundingSphere.center;if(zn.setFromBufferAttribute(e),t)for(let r=0,o=t.length;r<o;r++){const a=t[r];pa.setFromBufferAttribute(a),this.morphTargetsRelative?(hn.addVectors(zn.min,pa.min),zn.expandByPoint(hn),hn.addVectors(zn.max,pa.max),zn.expandByPoint(hn)):(zn.expandByPoint(pa.min),zn.expandByPoint(pa.max))}zn.getCenter(n);let s=0;for(let r=0,o=e.count;r<o;r++)hn.fromBufferAttribute(e,r),s=Math.max(s,n.distanceToSquared(hn));if(t)for(let r=0,o=t.length;r<o;r++){const a=t[r],l=this.morphTargetsRelative;for(let c=0,u=a.count;c<u;c++)hn.fromBufferAttribute(a,c),l&&(xr.fromBufferAttribute(e,c),hn.add(xr)),s=Math.max(s,n.distanceToSquared(hn))}this.boundingSphere.radius=Math.sqrt(s),isNaN(this.boundingSphere.radius)&&console.error('THREE.BufferGeometry.computeBoundingSphere(): Computed radius is NaN. The "position" attribute is likely to have NaN values.',this)}}computeTangents(){const e=this.index,t=this.attributes;if(e===null||t.position===void 0||t.normal===void 0||t.uv===void 0){console.error("THREE.BufferGeometry: .computeTangents() failed. Missing required attributes (index, position, normal or uv)");return}const n=t.position,s=t.normal,r=t.uv;this.hasAttribute("tangent")===!1&&this.setAttribute("tangent",new pi(new Float32Array(4*n.count),4));const o=this.getAttribute("tangent"),a=[],l=[];for(let k=0;k<n.count;k++)a[k]=new G,l[k]=new G;const c=new G,u=new G,h=new G,d=new qe,f=new qe,v=new qe,g=new G,m=new G;function p(k,E,y){c.fromBufferAttribute(n,k),u.fromBufferAttribute(n,E),h.fromBufferAttribute(n,y),d.fromBufferAttribute(r,k),f.fromBufferAttribute(r,E),v.fromBufferAttribute(r,y),u.sub(c),h.sub(c),f.sub(d),v.sub(d);const P=1/(f.x*v.y-v.x*f.y);isFinite(P)&&(g.copy(u).multiplyScalar(v.y).addScaledVector(h,-f.y).multiplyScalar(P),m.copy(h).multiplyScalar(f.x).addScaledVector(u,-v.x).multiplyScalar(P),a[k].add(g),a[E].add(g),a[y].add(g),l[k].add(m),l[E].add(m),l[y].add(m))}let x=this.groups;x.length===0&&(x=[{start:0,count:e.count}]);for(let k=0,E=x.length;k<E;++k){const y=x[k],P=y.start,K=y.count;for(let z=P,Z=P+K;z<Z;z+=3)p(e.getX(z+0),e.getX(z+1),e.getX(z+2))}const b=new G,w=new G,O=new G,A=new G;function L(k){O.fromBufferAttribute(s,k),A.copy(O);const E=a[k];b.copy(E),b.sub(O.multiplyScalar(O.dot(E))).normalize(),w.crossVectors(A,E);const P=w.dot(l[k])<0?-1:1;o.setXYZW(k,b.x,b.y,b.z,P)}for(let k=0,E=x.length;k<E;++k){const y=x[k],P=y.start,K=y.count;for(let z=P,Z=P+K;z<Z;z+=3)L(e.getX(z+0)),L(e.getX(z+1)),L(e.getX(z+2))}}computeVertexNormals(){const e=this.index,t=this.getAttribute("position");if(t!==void 0){let n=this.getAttribute("normal");if(n===void 0)n=new pi(new Float32Array(t.count*3),3),this.setAttribute("normal",n);else for(let d=0,f=n.count;d<f;d++)n.setXYZ(d,0,0,0);const s=new G,r=new G,o=new G,a=new G,l=new G,c=new G,u=new G,h=new G;if(e)for(let d=0,f=e.count;d<f;d+=3){const v=e.getX(d+0),g=e.getX(d+1),m=e.getX(d+2);s.fromBufferAttribute(t,v),r.fromBufferAttribute(t,g),o.fromBufferAttribute(t,m),u.subVectors(o,r),h.subVectors(s,r),u.cross(h),a.fromBufferAttribute(n,v),l.fromBufferAttribute(n,g),c.fromBufferAttribute(n,m),a.add(u),l.add(u),c.add(u),n.setXYZ(v,a.x,a.y,a.z),n.setXYZ(g,l.x,l.y,l.z),n.setXYZ(m,c.x,c.y,c.z)}else for(let d=0,f=t.count;d<f;d+=3)s.fromBufferAttribute(t,d+0),r.fromBufferAttribute(t,d+1),o.fromBufferAttribute(t,d+2),u.subVectors(o,r),h.subVectors(s,r),u.cross(h),n.setXYZ(d+0,u.x,u.y,u.z),n.setXYZ(d+1,u.x,u.y,u.z),n.setXYZ(d+2,u.x,u.y,u.z);this.normalizeNormals(),n.needsUpdate=!0}}normalizeNormals(){const e=this.attributes.normal;for(let t=0,n=e.count;t<n;t++)hn.fromBufferAttribute(e,t),hn.normalize(),e.setXYZ(t,hn.x,hn.y,hn.z)}toNonIndexed(){function e(a,l){const c=a.array,u=a.itemSize,h=a.normalized,d=new c.constructor(l.length*u);let f=0,v=0;for(let g=0,m=l.length;g<m;g++){a.isInterleavedBufferAttribute?f=l[g]*a.data.stride+a.offset:f=l[g]*u;for(let p=0;p<u;p++)d[v++]=c[f++]}return new pi(d,u,h)}if(this.index===null)return console.warn("THREE.BufferGeometry.toNonIndexed(): BufferGeometry is already non-indexed."),this;const t=new Xn,n=this.index.array,s=this.attributes;for(const a in s){const l=s[a],c=e(l,n);t.setAttribute(a,c)}const r=this.morphAttributes;for(const a in r){const l=[],c=r[a];for(let u=0,h=c.length;u<h;u++){const d=c[u],f=e(d,n);l.push(f)}t.morphAttributes[a]=l}t.morphTargetsRelative=this.morphTargetsRelative;const o=this.groups;for(let a=0,l=o.length;a<l;a++){const c=o[a];t.addGroup(c.start,c.count,c.materialIndex)}return t}toJSON(){const e={metadata:{version:4.6,type:"BufferGeometry",generator:"BufferGeometry.toJSON"}};if(e.uuid=this.uuid,e.type=this.type,this.name!==""&&(e.name=this.name),Object.keys(this.userData).length>0&&(e.userData=this.userData),this.parameters!==void 0){const l=this.parameters;for(const c in l)l[c]!==void 0&&(e[c]=l[c]);return e}e.data={attributes:{}};const t=this.index;t!==null&&(e.data.index={type:t.array.constructor.name,array:Array.prototype.slice.call(t.array)});const n=this.attributes;for(const l in n){const c=n[l];e.data.attributes[l]=c.toJSON(e.data)}const s={};let r=!1;for(const l in this.morphAttributes){const c=this.morphAttributes[l],u=[];for(let h=0,d=c.length;h<d;h++){const f=c[h];u.push(f.toJSON(e.data))}u.length>0&&(s[l]=u,r=!0)}r&&(e.data.morphAttributes=s,e.data.morphTargetsRelative=this.morphTargetsRelative);const o=this.groups;o.length>0&&(e.data.groups=JSON.parse(JSON.stringify(o)));const a=this.boundingSphere;return a!==null&&(e.data.boundingSphere={center:a.center.toArray(),radius:a.radius}),e}clone(){return new this.constructor().copy(this)}copy(e){this.index=null,this.attributes={},this.morphAttributes={},this.groups=[],this.boundingBox=null,this.boundingSphere=null;const t={};this.name=e.name;const n=e.index;n!==null&&this.setIndex(n.clone(t));const s=e.attributes;for(const c in s){const u=s[c];this.setAttribute(c,u.clone(t))}const r=e.morphAttributes;for(const c in r){const u=[],h=r[c];for(let d=0,f=h.length;d<f;d++)u.push(h[d].clone(t));this.morphAttributes[c]=u}this.morphTargetsRelative=e.morphTargetsRelative;const o=e.groups;for(let c=0,u=o.length;c<u;c++){const h=o[c];this.addGroup(h.start,h.count,h.materialIndex)}const a=e.boundingBox;a!==null&&(this.boundingBox=a.clone());const l=e.boundingSphere;return l!==null&&(this.boundingSphere=l.clone()),this.drawRange.start=e.drawRange.start,this.drawRange.count=e.drawRange.count,this.userData=e.userData,this}dispose(){this.dispatchEvent({type:"dispose"})}}const Ih=new Gt,Cs=new rl,so=new sl,Uh=new G,yr=new G,br=new G,Sr=new G,$l=new G,ro=new G,ao=new qe,oo=new qe,lo=new qe,Nh=new G,Oh=new G,Fh=new G,co=new G,uo=new G;class Pn extends tn{constructor(e=new Xn,t=new Ta){super(),this.isMesh=!0,this.type="Mesh",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),e.morphTargetInfluences!==void 0&&(this.morphTargetInfluences=e.morphTargetInfluences.slice()),e.morphTargetDictionary!==void 0&&(this.morphTargetDictionary=Object.assign({},e.morphTargetDictionary)),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const s=t[n[0]];if(s!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let r=0,o=s.length;r<o;r++){const a=s[r].name||String(r);this.morphTargetInfluences.push(0),this.morphTargetDictionary[a]=r}}}}getVertexPosition(e,t){const n=this.geometry,s=n.attributes.position,r=n.morphAttributes.position,o=n.morphTargetsRelative;t.fromBufferAttribute(s,e);const a=this.morphTargetInfluences;if(r&&a){ro.set(0,0,0);for(let l=0,c=r.length;l<c;l++){const u=a[l],h=r[l];u!==0&&($l.fromBufferAttribute(h,e),o?ro.addScaledVector($l,u):ro.addScaledVector($l.sub(t),u))}t.add(ro)}return t}raycast(e,t){const n=this.geometry,s=this.material,r=this.matrixWorld;s!==void 0&&(n.boundingSphere===null&&n.computeBoundingSphere(),so.copy(n.boundingSphere),so.applyMatrix4(r),Cs.copy(e.ray).recast(e.near),!(so.containsPoint(Cs.origin)===!1&&(Cs.intersectSphere(so,Uh)===null||Cs.origin.distanceToSquared(Uh)>(e.far-e.near)**2))&&(Ih.copy(r).invert(),Cs.copy(e.ray).applyMatrix4(Ih),!(n.boundingBox!==null&&Cs.intersectsBox(n.boundingBox)===!1)&&this._computeIntersections(e,t,Cs)))}_computeIntersections(e,t,n){let s;const r=this.geometry,o=this.material,a=r.index,l=r.attributes.position,c=r.attributes.uv,u=r.attributes.uv1,h=r.attributes.normal,d=r.groups,f=r.drawRange;if(a!==null)if(Array.isArray(o))for(let v=0,g=d.length;v<g;v++){const m=d[v],p=o[m.materialIndex],x=Math.max(m.start,f.start),b=Math.min(a.count,Math.min(m.start+m.count,f.start+f.count));for(let w=x,O=b;w<O;w+=3){const A=a.getX(w),L=a.getX(w+1),k=a.getX(w+2);s=ho(this,p,e,n,c,u,h,A,L,k),s&&(s.faceIndex=Math.floor(w/3),s.face.materialIndex=m.materialIndex,t.push(s))}}else{const v=Math.max(0,f.start),g=Math.min(a.count,f.start+f.count);for(let m=v,p=g;m<p;m+=3){const x=a.getX(m),b=a.getX(m+1),w=a.getX(m+2);s=ho(this,o,e,n,c,u,h,x,b,w),s&&(s.faceIndex=Math.floor(m/3),t.push(s))}}else if(l!==void 0)if(Array.isArray(o))for(let v=0,g=d.length;v<g;v++){const m=d[v],p=o[m.materialIndex],x=Math.max(m.start,f.start),b=Math.min(l.count,Math.min(m.start+m.count,f.start+f.count));for(let w=x,O=b;w<O;w+=3){const A=w,L=w+1,k=w+2;s=ho(this,p,e,n,c,u,h,A,L,k),s&&(s.faceIndex=Math.floor(w/3),s.face.materialIndex=m.materialIndex,t.push(s))}}else{const v=Math.max(0,f.start),g=Math.min(l.count,f.start+f.count);for(let m=v,p=g;m<p;m+=3){const x=m,b=m+1,w=m+2;s=ho(this,o,e,n,c,u,h,x,b,w),s&&(s.faceIndex=Math.floor(m/3),t.push(s))}}}}function Yg(i,e,t,n,s,r,o,a){let l;if(e.side===Nn?l=n.intersectTriangle(o,r,s,!0,a):l=n.intersectTriangle(s,r,o,e.side===hs,a),l===null)return null;uo.copy(a),uo.applyMatrix4(i.matrixWorld);const c=t.ray.origin.distanceTo(uo);return c<t.near||c>t.far?null:{distance:c,point:uo.clone(),object:i}}function ho(i,e,t,n,s,r,o,a,l,c){i.getVertexPosition(a,yr),i.getVertexPosition(l,br),i.getVertexPosition(c,Sr);const u=Yg(i,e,t,n,yr,br,Sr,co);if(u){s&&(ao.fromBufferAttribute(s,a),oo.fromBufferAttribute(s,l),lo.fromBufferAttribute(s,c),u.uv=Qn.getInterpolation(co,yr,br,Sr,ao,oo,lo,new qe)),r&&(ao.fromBufferAttribute(r,a),oo.fromBufferAttribute(r,l),lo.fromBufferAttribute(r,c),u.uv1=Qn.getInterpolation(co,yr,br,Sr,ao,oo,lo,new qe)),o&&(Nh.fromBufferAttribute(o,a),Oh.fromBufferAttribute(o,l),Fh.fromBufferAttribute(o,c),u.normal=Qn.getInterpolation(co,yr,br,Sr,Nh,Oh,Fh,new G),u.normal.dot(n.direction)>0&&u.normal.multiplyScalar(-1));const h={a,b:l,c,normal:new G,materialIndex:0};Qn.getNormal(yr,br,Sr,h.normal),u.face=h}return u}class Gi extends Xn{constructor(e=1,t=1,n=1,s=1,r=1,o=1){super(),this.type="BoxGeometry",this.parameters={width:e,height:t,depth:n,widthSegments:s,heightSegments:r,depthSegments:o};const a=this;s=Math.floor(s),r=Math.floor(r),o=Math.floor(o);const l=[],c=[],u=[],h=[];let d=0,f=0;v("z","y","x",-1,-1,n,t,e,o,r,0),v("z","y","x",1,-1,n,t,-e,o,r,1),v("x","z","y",1,1,e,n,t,s,o,2),v("x","z","y",1,-1,e,n,-t,s,o,3),v("x","y","z",1,-1,e,t,n,s,r,4),v("x","y","z",-1,-1,e,t,-n,s,r,5),this.setIndex(l),this.setAttribute("position",new Mn(c,3)),this.setAttribute("normal",new Mn(u,3)),this.setAttribute("uv",new Mn(h,2));function v(g,m,p,x,b,w,O,A,L,k,E){const y=w/L,P=O/k,K=w/2,z=O/2,Z=A/2,q=L+1,Q=k+1;let $=0,te=0;const ge=new G;for(let de=0;de<Q;de++){const xe=de*P-z;for(let Ee=0;Ee<q;Ee++){const ye=Ee*y-K;ge[g]=ye*x,ge[m]=xe*b,ge[p]=Z,c.push(ge.x,ge.y,ge.z),ge[g]=0,ge[m]=0,ge[p]=A>0?1:-1,u.push(ge.x,ge.y,ge.z),h.push(Ee/L),h.push(1-de/k),$+=1}}for(let de=0;de<k;de++)for(let xe=0;xe<L;xe++){const Ee=d+xe+q*de,ye=d+xe+q*(de+1),ne=d+(xe+1)+q*(de+1),ce=d+(xe+1)+q*de;l.push(Ee,ye,ce),l.push(ye,ne,ce),te+=6}a.addGroup(f,te,E),f+=te,d+=$}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Gi(e.width,e.height,e.depth,e.widthSegments,e.heightSegments,e.depthSegments)}}function Wr(i){const e={};for(const t in i){e[t]={};for(const n in i[t]){const s=i[t][n];s&&(s.isColor||s.isMatrix3||s.isMatrix4||s.isVector2||s.isVector3||s.isVector4||s.isTexture||s.isQuaternion)?s.isRenderTargetTexture?(console.warn("UniformsUtils: Textures of render targets cannot be cloned via cloneUniforms() or mergeUniforms()."),e[t][n]=null):e[t][n]=s.clone():Array.isArray(s)?e[t][n]=s.slice():e[t][n]=s}}return e}function Rn(i){const e={};for(let t=0;t<i.length;t++){const n=Wr(i[t]);for(const s in n)e[s]=n[s]}return e}function jg(i){const e=[];for(let t=0;t<i.length;t++)e.push(i[t].clone());return e}function Wf(i){const e=i.getRenderTarget();return e===null?i.outputColorSpace:e.isXRRenderTarget===!0?e.texture.colorSpace:wt.workingColorSpace}const Kg={clone:Wr,merge:Rn};var Zg=`void main() {
	gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
}`,Jg=`void main() {
	gl_FragColor = vec4( 1.0, 0.0, 0.0, 1.0 );
}`;class ds extends Ys{constructor(e){super(),this.isShaderMaterial=!0,this.type="ShaderMaterial",this.defines={},this.uniforms={},this.uniformsGroups=[],this.vertexShader=Zg,this.fragmentShader=Jg,this.linewidth=1,this.wireframe=!1,this.wireframeLinewidth=1,this.fog=!1,this.lights=!1,this.clipping=!1,this.forceSinglePass=!0,this.extensions={clipCullDistance:!1,multiDraw:!1},this.defaultAttributeValues={color:[1,1,1],uv:[0,0],uv1:[0,0]},this.index0AttributeName=void 0,this.uniformsNeedUpdate=!1,this.glslVersion=null,e!==void 0&&this.setValues(e)}copy(e){return super.copy(e),this.fragmentShader=e.fragmentShader,this.vertexShader=e.vertexShader,this.uniforms=Wr(e.uniforms),this.uniformsGroups=jg(e.uniformsGroups),this.defines=Object.assign({},e.defines),this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.fog=e.fog,this.lights=e.lights,this.clipping=e.clipping,this.extensions=Object.assign({},e.extensions),this.glslVersion=e.glslVersion,this}toJSON(e){const t=super.toJSON(e);t.glslVersion=this.glslVersion,t.uniforms={};for(const s in this.uniforms){const o=this.uniforms[s].value;o&&o.isTexture?t.uniforms[s]={type:"t",value:o.toJSON(e).uuid}:o&&o.isColor?t.uniforms[s]={type:"c",value:o.getHex()}:o&&o.isVector2?t.uniforms[s]={type:"v2",value:o.toArray()}:o&&o.isVector3?t.uniforms[s]={type:"v3",value:o.toArray()}:o&&o.isVector4?t.uniforms[s]={type:"v4",value:o.toArray()}:o&&o.isMatrix3?t.uniforms[s]={type:"m3",value:o.toArray()}:o&&o.isMatrix4?t.uniforms[s]={type:"m4",value:o.toArray()}:t.uniforms[s]={value:o}}Object.keys(this.defines).length>0&&(t.defines=this.defines),t.vertexShader=this.vertexShader,t.fragmentShader=this.fragmentShader,t.lights=this.lights,t.clipping=this.clipping;const n={};for(const s in this.extensions)this.extensions[s]===!0&&(n[s]=!0);return Object.keys(n).length>0&&(t.extensions=n),t}}class qf extends tn{constructor(){super(),this.isCamera=!0,this.type="Camera",this.matrixWorldInverse=new Gt,this.projectionMatrix=new Gt,this.projectionMatrixInverse=new Gt,this.coordinateSystem=Vi}copy(e,t){return super.copy(e,t),this.matrixWorldInverse.copy(e.matrixWorldInverse),this.projectionMatrix.copy(e.projectionMatrix),this.projectionMatrixInverse.copy(e.projectionMatrixInverse),this.coordinateSystem=e.coordinateSystem,this}getWorldDirection(e){return super.getWorldDirection(e).negate()}updateMatrixWorld(e){super.updateMatrixWorld(e),this.matrixWorldInverse.copy(this.matrixWorld).invert()}updateWorldMatrix(e,t){super.updateWorldMatrix(e,t),this.matrixWorldInverse.copy(this.matrixWorld).invert()}clone(){return new this.constructor().copy(this)}}const ss=new G,kh=new qe,Bh=new qe;class Sn extends qf{constructor(e=50,t=1,n=.1,s=2e3){super(),this.isPerspectiveCamera=!0,this.type="PerspectiveCamera",this.fov=e,this.zoom=1,this.near=n,this.far=s,this.focus=10,this.aspect=t,this.view=null,this.filmGauge=35,this.filmOffset=0,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.fov=e.fov,this.zoom=e.zoom,this.near=e.near,this.far=e.far,this.focus=e.focus,this.aspect=e.aspect,this.view=e.view===null?null:Object.assign({},e.view),this.filmGauge=e.filmGauge,this.filmOffset=e.filmOffset,this}setFocalLength(e){const t=.5*this.getFilmHeight()/e;this.fov=Na*2*Math.atan(t),this.updateProjectionMatrix()}getFocalLength(){const e=Math.tan(Or*.5*this.fov);return .5*this.getFilmHeight()/e}getEffectiveFOV(){return Na*2*Math.atan(Math.tan(Or*.5*this.fov)/this.zoom)}getFilmWidth(){return this.filmGauge*Math.min(this.aspect,1)}getFilmHeight(){return this.filmGauge/Math.max(this.aspect,1)}getViewBounds(e,t,n){ss.set(-1,-1,.5).applyMatrix4(this.projectionMatrixInverse),t.set(ss.x,ss.y).multiplyScalar(-e/ss.z),ss.set(1,1,.5).applyMatrix4(this.projectionMatrixInverse),n.set(ss.x,ss.y).multiplyScalar(-e/ss.z)}getViewSize(e,t){return this.getViewBounds(e,kh,Bh),t.subVectors(Bh,kh)}setViewOffset(e,t,n,s,r,o){this.aspect=e/t,this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=n,this.view.offsetY=s,this.view.width=r,this.view.height=o,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const e=this.near;let t=e*Math.tan(Or*.5*this.fov)/this.zoom,n=2*t,s=this.aspect*n,r=-.5*s;const o=this.view;if(this.view!==null&&this.view.enabled){const l=o.fullWidth,c=o.fullHeight;r+=o.offsetX*s/l,t-=o.offsetY*n/c,s*=o.width/l,n*=o.height/c}const a=this.filmOffset;a!==0&&(r+=e*a/this.getFilmWidth()),this.projectionMatrix.makePerspective(r,r+s,t,t-n,e,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){const t=super.toJSON(e);return t.object.fov=this.fov,t.object.zoom=this.zoom,t.object.near=this.near,t.object.far=this.far,t.object.focus=this.focus,t.object.aspect=this.aspect,this.view!==null&&(t.object.view=Object.assign({},this.view)),t.object.filmGauge=this.filmGauge,t.object.filmOffset=this.filmOffset,t}}const Mr=-90,wr=1;class Qg extends tn{constructor(e,t,n){super(),this.type="CubeCamera",this.renderTarget=n,this.coordinateSystem=null,this.activeMipmapLevel=0;const s=new Sn(Mr,wr,e,t);s.layers=this.layers,this.add(s);const r=new Sn(Mr,wr,e,t);r.layers=this.layers,this.add(r);const o=new Sn(Mr,wr,e,t);o.layers=this.layers,this.add(o);const a=new Sn(Mr,wr,e,t);a.layers=this.layers,this.add(a);const l=new Sn(Mr,wr,e,t);l.layers=this.layers,this.add(l);const c=new Sn(Mr,wr,e,t);c.layers=this.layers,this.add(c)}updateCoordinateSystem(){const e=this.coordinateSystem,t=this.children.concat(),[n,s,r,o,a,l]=t;for(const c of t)this.remove(c);if(e===Vi)n.up.set(0,1,0),n.lookAt(1,0,0),s.up.set(0,1,0),s.lookAt(-1,0,0),r.up.set(0,0,-1),r.lookAt(0,1,0),o.up.set(0,0,1),o.lookAt(0,-1,0),a.up.set(0,1,0),a.lookAt(0,0,1),l.up.set(0,1,0),l.lookAt(0,0,-1);else if(e===Go)n.up.set(0,-1,0),n.lookAt(-1,0,0),s.up.set(0,-1,0),s.lookAt(1,0,0),r.up.set(0,0,1),r.lookAt(0,1,0),o.up.set(0,0,-1),o.lookAt(0,-1,0),a.up.set(0,-1,0),a.lookAt(0,0,1),l.up.set(0,-1,0),l.lookAt(0,0,-1);else throw new Error("THREE.CubeCamera.updateCoordinateSystem(): Invalid coordinate system: "+e);for(const c of t)this.add(c),c.updateMatrixWorld()}update(e,t){this.parent===null&&this.updateMatrixWorld();const{renderTarget:n,activeMipmapLevel:s}=this;this.coordinateSystem!==e.coordinateSystem&&(this.coordinateSystem=e.coordinateSystem,this.updateCoordinateSystem());const[r,o,a,l,c,u]=this.children,h=e.getRenderTarget(),d=e.getActiveCubeFace(),f=e.getActiveMipmapLevel(),v=e.xr.enabled;e.xr.enabled=!1;const g=n.texture.generateMipmaps;n.texture.generateMipmaps=!1,e.setRenderTarget(n,0,s),e.render(t,r),e.setRenderTarget(n,1,s),e.render(t,o),e.setRenderTarget(n,2,s),e.render(t,a),e.setRenderTarget(n,3,s),e.render(t,l),e.setRenderTarget(n,4,s),e.render(t,c),n.texture.generateMipmaps=g,e.setRenderTarget(n,5,s),e.render(t,u),e.setRenderTarget(h,d,f),e.xr.enabled=v,n.texture.needsPMREMUpdate=!0}}class Xf extends Dn{constructor(e,t,n,s,r,o,a,l,c,u){e=e!==void 0?e:[],t=t!==void 0?t:zr,super(e,t,n,s,r,o,a,l,c,u),this.isCubeTexture=!0,this.flipY=!1}get images(){return this.image}set images(e){this.image=e}}class ev extends Gs{constructor(e=1,t={}){super(e,e,t),this.isWebGLCubeRenderTarget=!0;const n={width:e,height:e,depth:1},s=[n,n,n,n,n,n];this.texture=new Xf(s,t.mapping,t.wrapS,t.wrapT,t.magFilter,t.minFilter,t.format,t.type,t.anisotropy,t.colorSpace),this.texture.isRenderTargetTexture=!0,this.texture.generateMipmaps=t.generateMipmaps!==void 0?t.generateMipmaps:!1,this.texture.minFilter=t.minFilter!==void 0?t.minFilter:ui}fromEquirectangularTexture(e,t){this.texture.type=t.type,this.texture.colorSpace=t.colorSpace,this.texture.generateMipmaps=t.generateMipmaps,this.texture.minFilter=t.minFilter,this.texture.magFilter=t.magFilter;const n={uniforms:{tEquirect:{value:null}},vertexShader:`

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
			`},s=new Gi(5,5,5),r=new ds({name:"CubemapFromEquirect",uniforms:Wr(n.uniforms),vertexShader:n.vertexShader,fragmentShader:n.fragmentShader,side:Nn,blending:ls});r.uniforms.tEquirect.value=t;const o=new Pn(s,r),a=t.minFilter;return t.minFilter===Bs&&(t.minFilter=ui),new Qg(1,10,this).update(e,o),t.minFilter=a,o.geometry.dispose(),o.material.dispose(),this}clear(e,t,n,s){const r=e.getRenderTarget();for(let o=0;o<6;o++)e.setRenderTarget(this,o),e.clear(t,n,s);e.setRenderTarget(r)}}const Yl=new G,tv=new G,nv=new at;class rs{constructor(e=new G(1,0,0),t=0){this.isPlane=!0,this.normal=e,this.constant=t}set(e,t){return this.normal.copy(e),this.constant=t,this}setComponents(e,t,n,s){return this.normal.set(e,t,n),this.constant=s,this}setFromNormalAndCoplanarPoint(e,t){return this.normal.copy(e),this.constant=-t.dot(this.normal),this}setFromCoplanarPoints(e,t,n){const s=Yl.subVectors(n,t).cross(tv.subVectors(e,t)).normalize();return this.setFromNormalAndCoplanarPoint(s,e),this}copy(e){return this.normal.copy(e.normal),this.constant=e.constant,this}normalize(){const e=1/this.normal.length();return this.normal.multiplyScalar(e),this.constant*=e,this}negate(){return this.constant*=-1,this.normal.negate(),this}distanceToPoint(e){return this.normal.dot(e)+this.constant}distanceToSphere(e){return this.distanceToPoint(e.center)-e.radius}projectPoint(e,t){return t.copy(e).addScaledVector(this.normal,-this.distanceToPoint(e))}intersectLine(e,t){const n=e.delta(Yl),s=this.normal.dot(n);if(s===0)return this.distanceToPoint(e.start)===0?t.copy(e.start):null;const r=-(e.start.dot(this.normal)+this.constant)/s;return r<0||r>1?null:t.copy(e.start).addScaledVector(n,r)}intersectsLine(e){const t=this.distanceToPoint(e.start),n=this.distanceToPoint(e.end);return t<0&&n>0||n<0&&t>0}intersectsBox(e){return e.intersectsPlane(this)}intersectsSphere(e){return e.intersectsPlane(this)}coplanarPoint(e){return e.copy(this.normal).multiplyScalar(-this.constant)}applyMatrix4(e,t){const n=t||nv.getNormalMatrix(e),s=this.coplanarPoint(Yl).applyMatrix4(e),r=this.normal.applyMatrix3(n).normalize();return this.constant=-s.dot(r),this}translate(e){return this.constant-=e.dot(this.normal),this}equals(e){return e.normal.equals(this.normal)&&e.constant===this.constant}clone(){return new this.constructor().copy(this)}}const Rs=new sl,fo=new G;class Eu{constructor(e=new rs,t=new rs,n=new rs,s=new rs,r=new rs,o=new rs){this.planes=[e,t,n,s,r,o]}set(e,t,n,s,r,o){const a=this.planes;return a[0].copy(e),a[1].copy(t),a[2].copy(n),a[3].copy(s),a[4].copy(r),a[5].copy(o),this}copy(e){const t=this.planes;for(let n=0;n<6;n++)t[n].copy(e.planes[n]);return this}setFromProjectionMatrix(e,t=Vi){const n=this.planes,s=e.elements,r=s[0],o=s[1],a=s[2],l=s[3],c=s[4],u=s[5],h=s[6],d=s[7],f=s[8],v=s[9],g=s[10],m=s[11],p=s[12],x=s[13],b=s[14],w=s[15];if(n[0].setComponents(l-r,d-c,m-f,w-p).normalize(),n[1].setComponents(l+r,d+c,m+f,w+p).normalize(),n[2].setComponents(l+o,d+u,m+v,w+x).normalize(),n[3].setComponents(l-o,d-u,m-v,w-x).normalize(),n[4].setComponents(l-a,d-h,m-g,w-b).normalize(),t===Vi)n[5].setComponents(l+a,d+h,m+g,w+b).normalize();else if(t===Go)n[5].setComponents(a,h,g,b).normalize();else throw new Error("THREE.Frustum.setFromProjectionMatrix(): Invalid coordinate system: "+t);return this}intersectsObject(e){if(e.boundingSphere!==void 0)e.boundingSphere===null&&e.computeBoundingSphere(),Rs.copy(e.boundingSphere).applyMatrix4(e.matrixWorld);else{const t=e.geometry;t.boundingSphere===null&&t.computeBoundingSphere(),Rs.copy(t.boundingSphere).applyMatrix4(e.matrixWorld)}return this.intersectsSphere(Rs)}intersectsSprite(e){return Rs.center.set(0,0,0),Rs.radius=.7071067811865476,Rs.applyMatrix4(e.matrixWorld),this.intersectsSphere(Rs)}intersectsSphere(e){const t=this.planes,n=e.center,s=-e.radius;for(let r=0;r<6;r++)if(t[r].distanceToPoint(n)<s)return!1;return!0}intersectsBox(e){const t=this.planes;for(let n=0;n<6;n++){const s=t[n];if(fo.x=s.normal.x>0?e.max.x:e.min.x,fo.y=s.normal.y>0?e.max.y:e.min.y,fo.z=s.normal.z>0?e.max.z:e.min.z,s.distanceToPoint(fo)<0)return!1}return!0}containsPoint(e){const t=this.planes;for(let n=0;n<6;n++)if(t[n].distanceToPoint(e)<0)return!1;return!0}clone(){return new this.constructor().copy(this)}}function $f(){let i=null,e=!1,t=null,n=null;function s(r,o){t(r,o),n=i.requestAnimationFrame(s)}return{start:function(){e!==!0&&t!==null&&(n=i.requestAnimationFrame(s),e=!0)},stop:function(){i.cancelAnimationFrame(n),e=!1},setAnimationLoop:function(r){t=r},setContext:function(r){i=r}}}function iv(i){const e=new WeakMap;function t(a,l){const c=a.array,u=a.usage,h=c.byteLength,d=i.createBuffer();i.bindBuffer(l,d),i.bufferData(l,c,u),a.onUploadCallback();let f;if(c instanceof Float32Array)f=i.FLOAT;else if(c instanceof Uint16Array)a.isFloat16BufferAttribute?f=i.HALF_FLOAT:f=i.UNSIGNED_SHORT;else if(c instanceof Int16Array)f=i.SHORT;else if(c instanceof Uint32Array)f=i.UNSIGNED_INT;else if(c instanceof Int32Array)f=i.INT;else if(c instanceof Int8Array)f=i.BYTE;else if(c instanceof Uint8Array)f=i.UNSIGNED_BYTE;else if(c instanceof Uint8ClampedArray)f=i.UNSIGNED_BYTE;else throw new Error("THREE.WebGLAttributes: Unsupported buffer data format: "+c);return{buffer:d,type:f,bytesPerElement:c.BYTES_PER_ELEMENT,version:a.version,size:h}}function n(a,l,c){const u=l.array,h=l._updateRange,d=l.updateRanges;if(i.bindBuffer(c,a),h.count===-1&&d.length===0&&i.bufferSubData(c,0,u),d.length!==0){for(let f=0,v=d.length;f<v;f++){const g=d[f];i.bufferSubData(c,g.start*u.BYTES_PER_ELEMENT,u,g.start,g.count)}l.clearUpdateRanges()}h.count!==-1&&(i.bufferSubData(c,h.offset*u.BYTES_PER_ELEMENT,u,h.offset,h.count),h.count=-1),l.onUploadCallback()}function s(a){return a.isInterleavedBufferAttribute&&(a=a.data),e.get(a)}function r(a){a.isInterleavedBufferAttribute&&(a=a.data);const l=e.get(a);l&&(i.deleteBuffer(l.buffer),e.delete(a))}function o(a,l){if(a.isInterleavedBufferAttribute&&(a=a.data),a.isGLBufferAttribute){const u=e.get(a);(!u||u.version<a.version)&&e.set(a,{buffer:a.buffer,type:a.type,bytesPerElement:a.elementSize,version:a.version});return}const c=e.get(a);if(c===void 0)e.set(a,t(a,l));else if(c.version<a.version){if(c.size!==a.array.byteLength)throw new Error("THREE.WebGLAttributes: The size of the buffer attribute's array buffer does not match the original size. Resizing buffer attributes is not supported.");n(c.buffer,a,l),c.version=a.version}}return{get:s,remove:r,update:o}}class al extends Xn{constructor(e=1,t=1,n=1,s=1){super(),this.type="PlaneGeometry",this.parameters={width:e,height:t,widthSegments:n,heightSegments:s};const r=e/2,o=t/2,a=Math.floor(n),l=Math.floor(s),c=a+1,u=l+1,h=e/a,d=t/l,f=[],v=[],g=[],m=[];for(let p=0;p<u;p++){const x=p*d-o;for(let b=0;b<c;b++){const w=b*h-r;v.push(w,-x,0),g.push(0,0,1),m.push(b/a),m.push(1-p/l)}}for(let p=0;p<l;p++)for(let x=0;x<a;x++){const b=x+c*p,w=x+c*(p+1),O=x+1+c*(p+1),A=x+1+c*p;f.push(b,w,A),f.push(w,O,A)}this.setIndex(f),this.setAttribute("position",new Mn(v,3)),this.setAttribute("normal",new Mn(g,3)),this.setAttribute("uv",new Mn(m,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new al(e.width,e.height,e.widthSegments,e.heightSegments)}}var sv=`#ifdef USE_ALPHAHASH
	if ( diffuseColor.a < getAlphaHashThreshold( vPosition ) ) discard;
#endif`,rv=`#ifdef USE_ALPHAHASH
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
#endif`,av=`#ifdef USE_ALPHAMAP
	diffuseColor.a *= texture2D( alphaMap, vAlphaMapUv ).g;
#endif`,ov=`#ifdef USE_ALPHAMAP
	uniform sampler2D alphaMap;
#endif`,lv=`#ifdef USE_ALPHATEST
	#ifdef ALPHA_TO_COVERAGE
	diffuseColor.a = smoothstep( alphaTest, alphaTest + fwidth( diffuseColor.a ), diffuseColor.a );
	if ( diffuseColor.a == 0.0 ) discard;
	#else
	if ( diffuseColor.a < alphaTest ) discard;
	#endif
#endif`,cv=`#ifdef USE_ALPHATEST
	uniform float alphaTest;
#endif`,uv=`#ifdef USE_AOMAP
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
#endif`,hv=`#ifdef USE_AOMAP
	uniform sampler2D aoMap;
	uniform float aoMapIntensity;
#endif`,dv=`#ifdef USE_BATCHING
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
#endif`,fv=`#ifdef USE_BATCHING
	mat4 batchingMatrix = getBatchingMatrix( getIndirectIndex( gl_DrawID ) );
#endif`,pv=`vec3 transformed = vec3( position );
#ifdef USE_ALPHAHASH
	vPosition = vec3( position );
#endif`,mv=`vec3 objectNormal = vec3( normal );
#ifdef USE_TANGENT
	vec3 objectTangent = vec3( tangent.xyz );
#endif`,gv=`float G_BlinnPhong_Implicit( ) {
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
} // validated`,vv=`#ifdef USE_IRIDESCENCE
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
#endif`,_v=`#ifdef USE_BUMPMAP
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
#endif`,xv=`#if NUM_CLIPPING_PLANES > 0
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
#endif`,yv=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
	uniform vec4 clippingPlanes[ NUM_CLIPPING_PLANES ];
#endif`,bv=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
#endif`,Sv=`#if NUM_CLIPPING_PLANES > 0
	vClipPosition = - mvPosition.xyz;
#endif`,Mv=`#if defined( USE_COLOR_ALPHA )
	diffuseColor *= vColor;
#elif defined( USE_COLOR )
	diffuseColor.rgb *= vColor;
#endif`,wv=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR )
	varying vec3 vColor;
#endif`,Ev=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR ) || defined( USE_INSTANCING_COLOR ) || defined( USE_BATCHING_COLOR )
	varying vec3 vColor;
#endif`,Tv=`#if defined( USE_COLOR_ALPHA )
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
#endif`,Av=`#define PI 3.141592653589793
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
} // validated`,Cv=`#ifdef ENVMAP_TYPE_CUBE_UV
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
#endif`,Rv=`vec3 transformedNormal = objectNormal;
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
#endif`,Pv=`#ifdef USE_DISPLACEMENTMAP
	uniform sampler2D displacementMap;
	uniform float displacementScale;
	uniform float displacementBias;
#endif`,Lv=`#ifdef USE_DISPLACEMENTMAP
	transformed += normalize( objectNormal ) * ( texture2D( displacementMap, vDisplacementMapUv ).x * displacementScale + displacementBias );
#endif`,Dv=`#ifdef USE_EMISSIVEMAP
	vec4 emissiveColor = texture2D( emissiveMap, vEmissiveMapUv );
	totalEmissiveRadiance *= emissiveColor.rgb;
#endif`,Iv=`#ifdef USE_EMISSIVEMAP
	uniform sampler2D emissiveMap;
#endif`,Uv="gl_FragColor = linearToOutputTexel( gl_FragColor );",Nv=`
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
}`,Ov=`#ifdef USE_ENVMAP
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
#endif`,Fv=`#ifdef USE_ENVMAP
	uniform float envMapIntensity;
	uniform float flipEnvMap;
	uniform mat3 envMapRotation;
	#ifdef ENVMAP_TYPE_CUBE
		uniform samplerCube envMap;
	#else
		uniform sampler2D envMap;
	#endif
	
#endif`,kv=`#ifdef USE_ENVMAP
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
#endif`,Bv=`#ifdef USE_ENVMAP
	#if defined( USE_BUMPMAP ) || defined( USE_NORMALMAP ) || defined( PHONG ) || defined( LAMBERT )
		#define ENV_WORLDPOS
	#endif
	#ifdef ENV_WORLDPOS
		
		varying vec3 vWorldPosition;
	#else
		varying vec3 vReflect;
		uniform float refractionRatio;
	#endif
#endif`,zv=`#ifdef USE_ENVMAP
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
#endif`,Hv=`#ifdef USE_FOG
	vFogDepth = - mvPosition.z;
#endif`,Vv=`#ifdef USE_FOG
	varying float vFogDepth;
#endif`,Gv=`#ifdef USE_FOG
	#ifdef FOG_EXP2
		float fogFactor = 1.0 - exp( - fogDensity * fogDensity * vFogDepth * vFogDepth );
	#else
		float fogFactor = smoothstep( fogNear, fogFar, vFogDepth );
	#endif
	gl_FragColor.rgb = mix( gl_FragColor.rgb, fogColor, fogFactor );
#endif`,Wv=`#ifdef USE_FOG
	uniform vec3 fogColor;
	varying float vFogDepth;
	#ifdef FOG_EXP2
		uniform float fogDensity;
	#else
		uniform float fogNear;
		uniform float fogFar;
	#endif
#endif`,qv=`#ifdef USE_GRADIENTMAP
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
}`,Xv=`#ifdef USE_LIGHTMAP
	uniform sampler2D lightMap;
	uniform float lightMapIntensity;
#endif`,$v=`LambertMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularStrength = specularStrength;`,Yv=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Lambert`,jv=`uniform bool receiveShadow;
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
#endif`,Kv=`#ifdef USE_ENVMAP
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
#endif`,Zv=`ToonMaterial material;
material.diffuseColor = diffuseColor.rgb;`,Jv=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Toon`,Qv=`BlinnPhongMaterial material;
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
#endif`,s_=`#if defined( RE_IndirectDiffuse )
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
#endif`,r_=`#if defined( RE_IndirectDiffuse )
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
#endif`,v_=`#if defined( USE_MORPHCOLORS )
	vColor *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		#if defined( USE_COLOR_ALPHA )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ) * morphTargetInfluences[ i ];
		#elif defined( USE_COLOR )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ).rgb * morphTargetInfluences[ i ];
		#endif
	}
#endif`,__=`#ifdef USE_MORPHNORMALS
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
#endif`,y_=`#ifdef USE_MORPHTARGETS
	transformed *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) transformed += getMorph( gl_VertexID, i, 0 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,b_=`float faceDirection = gl_FrontFacing ? 1.0 : - 1.0;
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
vec3 nonPerturbedNormal = normal;`,S_=`#ifdef USE_NORMALMAP_OBJECTSPACE
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
#endif`,M_=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,w_=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,E_=`#ifndef FLAT_SHADED
	vNormal = normalize( transformedNormal );
	#ifdef USE_TANGENT
		vTangent = normalize( transformedTangent );
		vBitangent = normalize( cross( vNormal, vTangent ) * tangent.w );
	#endif
#endif`,T_=`#ifdef USE_NORMALMAP
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
#endif`,C_=`#ifdef USE_CLEARCOAT_NORMALMAP
	vec3 clearcoatMapN = texture2D( clearcoatNormalMap, vClearcoatNormalMapUv ).xyz * 2.0 - 1.0;
	clearcoatMapN.xy *= clearcoatNormalScale;
	clearcoatNormal = normalize( tbn2 * clearcoatMapN );
#endif`,R_=`#ifdef USE_CLEARCOATMAP
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
#endif`,O_=`#ifdef DITHERING
	vec3 dithering( vec3 color ) {
		float grid_position = rand( gl_FragCoord.xy );
		vec3 dither_shift_RGB = vec3( 0.25 / 255.0, -0.25 / 255.0, 0.25 / 255.0 );
		dither_shift_RGB = mix( 2.0 * dither_shift_RGB, -2.0 * dither_shift_RGB, grid_position );
		return color + dither_shift_RGB;
	}
#endif`,F_=`float roughnessFactor = roughness;
#ifdef USE_ROUGHNESSMAP
	vec4 texelRoughness = texture2D( roughnessMap, vRoughnessMapUv );
	roughnessFactor *= texelRoughness.g;
#endif`,k_=`#ifdef USE_ROUGHNESSMAP
	uniform sampler2D roughnessMap;
#endif`,B_=`#if NUM_SPOT_LIGHT_COORDS > 0
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
#endif`,z_=`#if NUM_SPOT_LIGHT_COORDS > 0
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
#endif`,q_=`#ifdef USE_SKINNING
	vec4 skinVertex = bindMatrix * vec4( transformed, 1.0 );
	vec4 skinned = vec4( 0.0 );
	skinned += boneMatX * skinVertex * skinWeight.x;
	skinned += boneMatY * skinVertex * skinWeight.y;
	skinned += boneMatZ * skinVertex * skinWeight.z;
	skinned += boneMatW * skinVertex * skinWeight.w;
	transformed = ( bindMatrixInverse * skinned ).xyz;
#endif`,X_=`#ifdef USE_SKINNING
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
#endif`,$_=`float specularStrength;
#ifdef USE_SPECULARMAP
	vec4 texelSpecular = texture2D( specularMap, vSpecularMapUv );
	specularStrength = texelSpecular.r;
#else
	specularStrength = 1.0;
#endif`,Y_=`#ifdef USE_SPECULARMAP
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
}`,s0=`uniform sampler2D t2D;
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
}`,r0=`varying vec3 vWorldDirection;
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
}`,v0=`#include <common>
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
}`,_0=`uniform vec3 diffuse;
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
}`,y0=`#define LAMBERT
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
}`,b0=`#define MATCAP
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
}`,S0=`#define MATCAP
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
}`,M0=`#define NORMAL
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
}`,w0=`#define NORMAL
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
}`,E0=`#define PHONG
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
}`,T0=`#define PHONG
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
}`,C0=`#define STANDARD
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
}`,R0=`#define TOON
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
}`,O0=`uniform vec3 diffuse;
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
}`,rt={alphahash_fragment:sv,alphahash_pars_fragment:rv,alphamap_fragment:av,alphamap_pars_fragment:ov,alphatest_fragment:lv,alphatest_pars_fragment:cv,aomap_fragment:uv,aomap_pars_fragment:hv,batching_pars_vertex:dv,batching_vertex:fv,begin_vertex:pv,beginnormal_vertex:mv,bsdfs:gv,iridescence_fragment:vv,bumpmap_pars_fragment:_v,clipping_planes_fragment:xv,clipping_planes_pars_fragment:yv,clipping_planes_pars_vertex:bv,clipping_planes_vertex:Sv,color_fragment:Mv,color_pars_fragment:wv,color_pars_vertex:Ev,color_vertex:Tv,common:Av,cube_uv_reflection_fragment:Cv,defaultnormal_vertex:Rv,displacementmap_pars_vertex:Pv,displacementmap_vertex:Lv,emissivemap_fragment:Dv,emissivemap_pars_fragment:Iv,colorspace_fragment:Uv,colorspace_pars_fragment:Nv,envmap_fragment:Ov,envmap_common_pars_fragment:Fv,envmap_pars_fragment:kv,envmap_pars_vertex:Bv,envmap_physical_pars_fragment:Kv,envmap_vertex:zv,fog_vertex:Hv,fog_pars_vertex:Vv,fog_fragment:Gv,fog_pars_fragment:Wv,gradientmap_pars_fragment:qv,lightmap_pars_fragment:Xv,lights_lambert_fragment:$v,lights_lambert_pars_fragment:Yv,lights_pars_begin:jv,lights_toon_fragment:Zv,lights_toon_pars_fragment:Jv,lights_phong_fragment:Qv,lights_phong_pars_fragment:e_,lights_physical_fragment:t_,lights_physical_pars_fragment:n_,lights_fragment_begin:i_,lights_fragment_maps:s_,lights_fragment_end:r_,logdepthbuf_fragment:a_,logdepthbuf_pars_fragment:o_,logdepthbuf_pars_vertex:l_,logdepthbuf_vertex:c_,map_fragment:u_,map_pars_fragment:h_,map_particle_fragment:d_,map_particle_pars_fragment:f_,metalnessmap_fragment:p_,metalnessmap_pars_fragment:m_,morphinstance_vertex:g_,morphcolor_vertex:v_,morphnormal_vertex:__,morphtarget_pars_vertex:x_,morphtarget_vertex:y_,normal_fragment_begin:b_,normal_fragment_maps:S_,normal_pars_fragment:M_,normal_pars_vertex:w_,normal_vertex:E_,normalmap_pars_fragment:T_,clearcoat_normal_fragment_begin:A_,clearcoat_normal_fragment_maps:C_,clearcoat_pars_fragment:R_,iridescence_pars_fragment:P_,opaque_fragment:L_,packing:D_,premultiplied_alpha_fragment:I_,project_vertex:U_,dithering_fragment:N_,dithering_pars_fragment:O_,roughnessmap_fragment:F_,roughnessmap_pars_fragment:k_,shadowmap_pars_fragment:B_,shadowmap_pars_vertex:z_,shadowmap_vertex:H_,shadowmask_pars_fragment:V_,skinbase_vertex:G_,skinning_pars_vertex:W_,skinning_vertex:q_,skinnormal_vertex:X_,specularmap_fragment:$_,specularmap_pars_fragment:Y_,tonemapping_fragment:j_,tonemapping_pars_fragment:K_,transmission_fragment:Z_,transmission_pars_fragment:J_,uv_pars_fragment:Q_,uv_pars_vertex:e0,uv_vertex:t0,worldpos_vertex:n0,background_vert:i0,background_frag:s0,backgroundCube_vert:r0,backgroundCube_frag:a0,cube_vert:o0,cube_frag:l0,depth_vert:c0,depth_frag:u0,distanceRGBA_vert:h0,distanceRGBA_frag:d0,equirect_vert:f0,equirect_frag:p0,linedashed_vert:m0,linedashed_frag:g0,meshbasic_vert:v0,meshbasic_frag:_0,meshlambert_vert:x0,meshlambert_frag:y0,meshmatcap_vert:b0,meshmatcap_frag:S0,meshnormal_vert:M0,meshnormal_frag:w0,meshphong_vert:E0,meshphong_frag:T0,meshphysical_vert:A0,meshphysical_frag:C0,meshtoon_vert:R0,meshtoon_frag:P0,points_vert:L0,points_frag:D0,shadow_vert:I0,shadow_frag:U0,sprite_vert:N0,sprite_frag:O0},Ce={common:{diffuse:{value:new st(16777215)},opacity:{value:1},map:{value:null},mapTransform:{value:new at},alphaMap:{value:null},alphaMapTransform:{value:new at},alphaTest:{value:0}},specularmap:{specularMap:{value:null},specularMapTransform:{value:new at}},envmap:{envMap:{value:null},envMapRotation:{value:new at},flipEnvMap:{value:-1},reflectivity:{value:1},ior:{value:1.5},refractionRatio:{value:.98}},aomap:{aoMap:{value:null},aoMapIntensity:{value:1},aoMapTransform:{value:new at}},lightmap:{lightMap:{value:null},lightMapIntensity:{value:1},lightMapTransform:{value:new at}},bumpmap:{bumpMap:{value:null},bumpMapTransform:{value:new at},bumpScale:{value:1}},normalmap:{normalMap:{value:null},normalMapTransform:{value:new at},normalScale:{value:new qe(1,1)}},displacementmap:{displacementMap:{value:null},displacementMapTransform:{value:new at},displacementScale:{value:1},displacementBias:{value:0}},emissivemap:{emissiveMap:{value:null},emissiveMapTransform:{value:new at}},metalnessmap:{metalnessMap:{value:null},metalnessMapTransform:{value:new at}},roughnessmap:{roughnessMap:{value:null},roughnessMapTransform:{value:new at}},gradientmap:{gradientMap:{value:null}},fog:{fogDensity:{value:25e-5},fogNear:{value:1},fogFar:{value:2e3},fogColor:{value:new st(16777215)}},lights:{ambientLightColor:{value:[]},lightProbe:{value:[]},directionalLights:{value:[],properties:{direction:{},color:{}}},directionalLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},directionalShadowMap:{value:[]},directionalShadowMatrix:{value:[]},spotLights:{value:[],properties:{color:{},position:{},direction:{},distance:{},coneCos:{},penumbraCos:{},decay:{}}},spotLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},spotLightMap:{value:[]},spotShadowMap:{value:[]},spotLightMatrix:{value:[]},pointLights:{value:[],properties:{color:{},position:{},decay:{},distance:{}}},pointLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{},shadowCameraNear:{},shadowCameraFar:{}}},pointShadowMap:{value:[]},pointShadowMatrix:{value:[]},hemisphereLights:{value:[],properties:{direction:{},skyColor:{},groundColor:{}}},rectAreaLights:{value:[],properties:{color:{},position:{},width:{},height:{}}},ltc_1:{value:null},ltc_2:{value:null}},points:{diffuse:{value:new st(16777215)},opacity:{value:1},size:{value:1},scale:{value:1},map:{value:null},alphaMap:{value:null},alphaMapTransform:{value:new at},alphaTest:{value:0},uvTransform:{value:new at}},sprite:{diffuse:{value:new st(16777215)},opacity:{value:1},center:{value:new qe(.5,.5)},rotation:{value:0},map:{value:null},mapTransform:{value:new at},alphaMap:{value:null},alphaMapTransform:{value:new at},alphaTest:{value:0}}},wi={basic:{uniforms:Rn([Ce.common,Ce.specularmap,Ce.envmap,Ce.aomap,Ce.lightmap,Ce.fog]),vertexShader:rt.meshbasic_vert,fragmentShader:rt.meshbasic_frag},lambert:{uniforms:Rn([Ce.common,Ce.specularmap,Ce.envmap,Ce.aomap,Ce.lightmap,Ce.emissivemap,Ce.bumpmap,Ce.normalmap,Ce.displacementmap,Ce.fog,Ce.lights,{emissive:{value:new st(0)}}]),vertexShader:rt.meshlambert_vert,fragmentShader:rt.meshlambert_frag},phong:{uniforms:Rn([Ce.common,Ce.specularmap,Ce.envmap,Ce.aomap,Ce.lightmap,Ce.emissivemap,Ce.bumpmap,Ce.normalmap,Ce.displacementmap,Ce.fog,Ce.lights,{emissive:{value:new st(0)},specular:{value:new st(1118481)},shininess:{value:30}}]),vertexShader:rt.meshphong_vert,fragmentShader:rt.meshphong_frag},standard:{uniforms:Rn([Ce.common,Ce.envmap,Ce.aomap,Ce.lightmap,Ce.emissivemap,Ce.bumpmap,Ce.normalmap,Ce.displacementmap,Ce.roughnessmap,Ce.metalnessmap,Ce.fog,Ce.lights,{emissive:{value:new st(0)},roughness:{value:1},metalness:{value:0},envMapIntensity:{value:1}}]),vertexShader:rt.meshphysical_vert,fragmentShader:rt.meshphysical_frag},toon:{uniforms:Rn([Ce.common,Ce.aomap,Ce.lightmap,Ce.emissivemap,Ce.bumpmap,Ce.normalmap,Ce.displacementmap,Ce.gradientmap,Ce.fog,Ce.lights,{emissive:{value:new st(0)}}]),vertexShader:rt.meshtoon_vert,fragmentShader:rt.meshtoon_frag},matcap:{uniforms:Rn([Ce.common,Ce.bumpmap,Ce.normalmap,Ce.displacementmap,Ce.fog,{matcap:{value:null}}]),vertexShader:rt.meshmatcap_vert,fragmentShader:rt.meshmatcap_frag},points:{uniforms:Rn([Ce.points,Ce.fog]),vertexShader:rt.points_vert,fragmentShader:rt.points_frag},dashed:{uniforms:Rn([Ce.common,Ce.fog,{scale:{value:1},dashSize:{value:1},totalSize:{value:2}}]),vertexShader:rt.linedashed_vert,fragmentShader:rt.linedashed_frag},depth:{uniforms:Rn([Ce.common,Ce.displacementmap]),vertexShader:rt.depth_vert,fragmentShader:rt.depth_frag},normal:{uniforms:Rn([Ce.common,Ce.bumpmap,Ce.normalmap,Ce.displacementmap,{opacity:{value:1}}]),vertexShader:rt.meshnormal_vert,fragmentShader:rt.meshnormal_frag},sprite:{uniforms:Rn([Ce.sprite,Ce.fog]),vertexShader:rt.sprite_vert,fragmentShader:rt.sprite_frag},background:{uniforms:{uvTransform:{value:new at},t2D:{value:null},backgroundIntensity:{value:1}},vertexShader:rt.background_vert,fragmentShader:rt.background_frag},backgroundCube:{uniforms:{envMap:{value:null},flipEnvMap:{value:-1},backgroundBlurriness:{value:0},backgroundIntensity:{value:1},backgroundRotation:{value:new at}},vertexShader:rt.backgroundCube_vert,fragmentShader:rt.backgroundCube_frag},cube:{uniforms:{tCube:{value:null},tFlip:{value:-1},opacity:{value:1}},vertexShader:rt.cube_vert,fragmentShader:rt.cube_frag},equirect:{uniforms:{tEquirect:{value:null}},vertexShader:rt.equirect_vert,fragmentShader:rt.equirect_frag},distanceRGBA:{uniforms:Rn([Ce.common,Ce.displacementmap,{referencePosition:{value:new G},nearDistance:{value:1},farDistance:{value:1e3}}]),vertexShader:rt.distanceRGBA_vert,fragmentShader:rt.distanceRGBA_frag},shadow:{uniforms:Rn([Ce.lights,Ce.fog,{color:{value:new st(0)},opacity:{value:1}}]),vertexShader:rt.shadow_vert,fragmentShader:rt.shadow_frag}};wi.physical={uniforms:Rn([wi.standard.uniforms,{clearcoat:{value:0},clearcoatMap:{value:null},clearcoatMapTransform:{value:new at},clearcoatNormalMap:{value:null},clearcoatNormalMapTransform:{value:new at},clearcoatNormalScale:{value:new qe(1,1)},clearcoatRoughness:{value:0},clearcoatRoughnessMap:{value:null},clearcoatRoughnessMapTransform:{value:new at},dispersion:{value:0},iridescence:{value:0},iridescenceMap:{value:null},iridescenceMapTransform:{value:new at},iridescenceIOR:{value:1.3},iridescenceThicknessMinimum:{value:100},iridescenceThicknessMaximum:{value:400},iridescenceThicknessMap:{value:null},iridescenceThicknessMapTransform:{value:new at},sheen:{value:0},sheenColor:{value:new st(0)},sheenColorMap:{value:null},sheenColorMapTransform:{value:new at},sheenRoughness:{value:1},sheenRoughnessMap:{value:null},sheenRoughnessMapTransform:{value:new at},transmission:{value:0},transmissionMap:{value:null},transmissionMapTransform:{value:new at},transmissionSamplerSize:{value:new qe},transmissionSamplerMap:{value:null},thickness:{value:0},thicknessMap:{value:null},thicknessMapTransform:{value:new at},attenuationDistance:{value:0},attenuationColor:{value:new st(0)},specularColor:{value:new st(1,1,1)},specularColorMap:{value:null},specularColorMapTransform:{value:new at},specularIntensity:{value:1},specularIntensityMap:{value:null},specularIntensityMapTransform:{value:new at},anisotropyVector:{value:new qe},anisotropyMap:{value:null},anisotropyMapTransform:{value:new at}}]),vertexShader:rt.meshphysical_vert,fragmentShader:rt.meshphysical_frag};const po={r:0,b:0,g:0},Ps=new Ai,F0=new Gt;function k0(i,e,t,n,s,r,o){const a=new st(0);let l=r===!0?0:1,c,u,h=null,d=0,f=null;function v(x){let b=x.isScene===!0?x.background:null;return b&&b.isTexture&&(b=(x.backgroundBlurriness>0?t:e).get(b)),b}function g(x){let b=!1;const w=v(x);w===null?p(a,l):w&&w.isColor&&(p(w,1),b=!0);const O=i.xr.getEnvironmentBlendMode();O==="additive"?n.buffers.color.setClear(0,0,0,1,o):O==="alpha-blend"&&n.buffers.color.setClear(0,0,0,0,o),(i.autoClear||b)&&(n.buffers.depth.setTest(!0),n.buffers.depth.setMask(!0),n.buffers.color.setMask(!0),i.clear(i.autoClearColor,i.autoClearDepth,i.autoClearStencil))}function m(x,b){const w=v(b);w&&(w.isCubeTexture||w.mapping===nl)?(u===void 0&&(u=new Pn(new Gi(1,1,1),new ds({name:"BackgroundCubeMaterial",uniforms:Wr(wi.backgroundCube.uniforms),vertexShader:wi.backgroundCube.vertexShader,fragmentShader:wi.backgroundCube.fragmentShader,side:Nn,depthTest:!1,depthWrite:!1,fog:!1})),u.geometry.deleteAttribute("normal"),u.geometry.deleteAttribute("uv"),u.onBeforeRender=function(O,A,L){this.matrixWorld.copyPosition(L.matrixWorld)},Object.defineProperty(u.material,"envMap",{get:function(){return this.uniforms.envMap.value}}),s.update(u)),Ps.copy(b.backgroundRotation),Ps.x*=-1,Ps.y*=-1,Ps.z*=-1,w.isCubeTexture&&w.isRenderTargetTexture===!1&&(Ps.y*=-1,Ps.z*=-1),u.material.uniforms.envMap.value=w,u.material.uniforms.flipEnvMap.value=w.isCubeTexture&&w.isRenderTargetTexture===!1?-1:1,u.material.uniforms.backgroundBlurriness.value=b.backgroundBlurriness,u.material.uniforms.backgroundIntensity.value=b.backgroundIntensity,u.material.uniforms.backgroundRotation.value.setFromMatrix4(F0.makeRotationFromEuler(Ps)),u.material.toneMapped=wt.getTransfer(w.colorSpace)!==Bt,(h!==w||d!==w.version||f!==i.toneMapping)&&(u.material.needsUpdate=!0,h=w,d=w.version,f=i.toneMapping),u.layers.enableAll(),x.unshift(u,u.geometry,u.material,0,0,null)):w&&w.isTexture&&(c===void 0&&(c=new Pn(new al(2,2),new ds({name:"BackgroundMaterial",uniforms:Wr(wi.background.uniforms),vertexShader:wi.background.vertexShader,fragmentShader:wi.background.fragmentShader,side:hs,depthTest:!1,depthWrite:!1,fog:!1})),c.geometry.deleteAttribute("normal"),Object.defineProperty(c.material,"map",{get:function(){return this.uniforms.t2D.value}}),s.update(c)),c.material.uniforms.t2D.value=w,c.material.uniforms.backgroundIntensity.value=b.backgroundIntensity,c.material.toneMapped=wt.getTransfer(w.colorSpace)!==Bt,w.matrixAutoUpdate===!0&&w.updateMatrix(),c.material.uniforms.uvTransform.value.copy(w.matrix),(h!==w||d!==w.version||f!==i.toneMapping)&&(c.material.needsUpdate=!0,h=w,d=w.version,f=i.toneMapping),c.layers.enableAll(),x.unshift(c,c.geometry,c.material,0,0,null))}function p(x,b){x.getRGB(po,Wf(i)),n.buffers.color.setClear(po.r,po.g,po.b,b,o)}return{getClearColor:function(){return a},setClearColor:function(x,b=1){a.set(x),l=b,p(a,l)},getClearAlpha:function(){return l},setClearAlpha:function(x){l=x,p(a,l)},render:g,addToRenderList:m}}function B0(i,e){const t=i.getParameter(i.MAX_VERTEX_ATTRIBS),n={},s=d(null);let r=s,o=!1;function a(y,P,K,z,Z){let q=!1;const Q=h(z,K,P);r!==Q&&(r=Q,c(r.object)),q=f(y,z,K,Z),q&&v(y,z,K,Z),Z!==null&&e.update(Z,i.ELEMENT_ARRAY_BUFFER),(q||o)&&(o=!1,w(y,P,K,z),Z!==null&&i.bindBuffer(i.ELEMENT_ARRAY_BUFFER,e.get(Z).buffer))}function l(){return i.createVertexArray()}function c(y){return i.bindVertexArray(y)}function u(y){return i.deleteVertexArray(y)}function h(y,P,K){const z=K.wireframe===!0;let Z=n[y.id];Z===void 0&&(Z={},n[y.id]=Z);let q=Z[P.id];q===void 0&&(q={},Z[P.id]=q);let Q=q[z];return Q===void 0&&(Q=d(l()),q[z]=Q),Q}function d(y){const P=[],K=[],z=[];for(let Z=0;Z<t;Z++)P[Z]=0,K[Z]=0,z[Z]=0;return{geometry:null,program:null,wireframe:!1,newAttributes:P,enabledAttributes:K,attributeDivisors:z,object:y,attributes:{},index:null}}function f(y,P,K,z){const Z=r.attributes,q=P.attributes;let Q=0;const $=K.getAttributes();for(const te in $)if($[te].location>=0){const de=Z[te];let xe=q[te];if(xe===void 0&&(te==="instanceMatrix"&&y.instanceMatrix&&(xe=y.instanceMatrix),te==="instanceColor"&&y.instanceColor&&(xe=y.instanceColor)),de===void 0||de.attribute!==xe||xe&&de.data!==xe.data)return!0;Q++}return r.attributesNum!==Q||r.index!==z}function v(y,P,K,z){const Z={},q=P.attributes;let Q=0;const $=K.getAttributes();for(const te in $)if($[te].location>=0){let de=q[te];de===void 0&&(te==="instanceMatrix"&&y.instanceMatrix&&(de=y.instanceMatrix),te==="instanceColor"&&y.instanceColor&&(de=y.instanceColor));const xe={};xe.attribute=de,de&&de.data&&(xe.data=de.data),Z[te]=xe,Q++}r.attributes=Z,r.attributesNum=Q,r.index=z}function g(){const y=r.newAttributes;for(let P=0,K=y.length;P<K;P++)y[P]=0}function m(y){p(y,0)}function p(y,P){const K=r.newAttributes,z=r.enabledAttributes,Z=r.attributeDivisors;K[y]=1,z[y]===0&&(i.enableVertexAttribArray(y),z[y]=1),Z[y]!==P&&(i.vertexAttribDivisor(y,P),Z[y]=P)}function x(){const y=r.newAttributes,P=r.enabledAttributes;for(let K=0,z=P.length;K<z;K++)P[K]!==y[K]&&(i.disableVertexAttribArray(K),P[K]=0)}function b(y,P,K,z,Z,q,Q){Q===!0?i.vertexAttribIPointer(y,P,K,Z,q):i.vertexAttribPointer(y,P,K,z,Z,q)}function w(y,P,K,z){g();const Z=z.attributes,q=K.getAttributes(),Q=P.defaultAttributeValues;for(const $ in q){const te=q[$];if(te.location>=0){let ge=Z[$];if(ge===void 0&&($==="instanceMatrix"&&y.instanceMatrix&&(ge=y.instanceMatrix),$==="instanceColor"&&y.instanceColor&&(ge=y.instanceColor)),ge!==void 0){const de=ge.normalized,xe=ge.itemSize,Ee=e.get(ge);if(Ee===void 0)continue;const ye=Ee.buffer,ne=Ee.type,ce=Ee.bytesPerElement,be=ne===i.INT||ne===i.UNSIGNED_INT||ge.gpuType===gu;if(ge.isInterleavedBufferAttribute){const fe=ge.data,ke=fe.stride,Ve=ge.offset;if(fe.isInstancedInterleavedBuffer){for(let Ne=0;Ne<te.locationSize;Ne++)p(te.location+Ne,fe.meshPerAttribute);y.isInstancedMesh!==!0&&z._maxInstanceCount===void 0&&(z._maxInstanceCount=fe.meshPerAttribute*fe.count)}else for(let Ne=0;Ne<te.locationSize;Ne++)m(te.location+Ne);i.bindBuffer(i.ARRAY_BUFFER,ye);for(let Ne=0;Ne<te.locationSize;Ne++)b(te.location+Ne,xe/te.locationSize,ne,de,ke*ce,(Ve+xe/te.locationSize*Ne)*ce,be)}else{if(ge.isInstancedBufferAttribute){for(let fe=0;fe<te.locationSize;fe++)p(te.location+fe,ge.meshPerAttribute);y.isInstancedMesh!==!0&&z._maxInstanceCount===void 0&&(z._maxInstanceCount=ge.meshPerAttribute*ge.count)}else for(let fe=0;fe<te.locationSize;fe++)m(te.location+fe);i.bindBuffer(i.ARRAY_BUFFER,ye);for(let fe=0;fe<te.locationSize;fe++)b(te.location+fe,xe/te.locationSize,ne,de,xe*ce,xe/te.locationSize*fe*ce,be)}}else if(Q!==void 0){const de=Q[$];if(de!==void 0)switch(de.length){case 2:i.vertexAttrib2fv(te.location,de);break;case 3:i.vertexAttrib3fv(te.location,de);break;case 4:i.vertexAttrib4fv(te.location,de);break;default:i.vertexAttrib1fv(te.location,de)}}}}x()}function O(){k();for(const y in n){const P=n[y];for(const K in P){const z=P[K];for(const Z in z)u(z[Z].object),delete z[Z];delete P[K]}delete n[y]}}function A(y){if(n[y.id]===void 0)return;const P=n[y.id];for(const K in P){const z=P[K];for(const Z in z)u(z[Z].object),delete z[Z];delete P[K]}delete n[y.id]}function L(y){for(const P in n){const K=n[P];if(K[y.id]===void 0)continue;const z=K[y.id];for(const Z in z)u(z[Z].object),delete z[Z];delete K[y.id]}}function k(){E(),o=!0,r!==s&&(r=s,c(r.object))}function E(){s.geometry=null,s.program=null,s.wireframe=!1}return{setup:a,reset:k,resetDefaultState:E,dispose:O,releaseStatesOfGeometry:A,releaseStatesOfProgram:L,initAttributes:g,enableAttribute:m,disableUnusedAttributes:x}}function z0(i,e,t){let n;function s(c){n=c}function r(c,u){i.drawArrays(n,c,u),t.update(u,n,1)}function o(c,u,h){h!==0&&(i.drawArraysInstanced(n,c,u,h),t.update(u,n,h))}function a(c,u,h){if(h===0)return;e.get("WEBGL_multi_draw").multiDrawArraysWEBGL(n,c,0,u,0,h);let f=0;for(let v=0;v<h;v++)f+=u[v];t.update(f,n,1)}function l(c,u,h,d){if(h===0)return;const f=e.get("WEBGL_multi_draw");if(f===null)for(let v=0;v<c.length;v++)o(c[v],u[v],d[v]);else{f.multiDrawArraysInstancedWEBGL(n,c,0,u,0,d,0,h);let v=0;for(let g=0;g<h;g++)v+=u[g];for(let g=0;g<d.length;g++)t.update(v,n,d[g])}}this.setMode=s,this.render=r,this.renderInstances=o,this.renderMultiDraw=a,this.renderMultiDrawInstances=l}function H0(i,e,t,n){let s;function r(){if(s!==void 0)return s;if(e.has("EXT_texture_filter_anisotropic")===!0){const A=e.get("EXT_texture_filter_anisotropic");s=i.getParameter(A.MAX_TEXTURE_MAX_ANISOTROPY_EXT)}else s=0;return s}function o(A){return!(A!==fi&&n.convert(A)!==i.getParameter(i.IMPLEMENTATION_COLOR_READ_FORMAT))}function a(A){const L=A===ka&&(e.has("EXT_color_buffer_half_float")||e.has("EXT_color_buffer_float"));return!(A!==$i&&n.convert(A)!==i.getParameter(i.IMPLEMENTATION_COLOR_READ_TYPE)&&A!==Hi&&!L)}function l(A){if(A==="highp"){if(i.getShaderPrecisionFormat(i.VERTEX_SHADER,i.HIGH_FLOAT).precision>0&&i.getShaderPrecisionFormat(i.FRAGMENT_SHADER,i.HIGH_FLOAT).precision>0)return"highp";A="mediump"}return A==="mediump"&&i.getShaderPrecisionFormat(i.VERTEX_SHADER,i.MEDIUM_FLOAT).precision>0&&i.getShaderPrecisionFormat(i.FRAGMENT_SHADER,i.MEDIUM_FLOAT).precision>0?"mediump":"lowp"}let c=t.precision!==void 0?t.precision:"highp";const u=l(c);u!==c&&(console.warn("THREE.WebGLRenderer:",c,"not supported, using",u,"instead."),c=u);const h=t.logarithmicDepthBuffer===!0,d=i.getParameter(i.MAX_TEXTURE_IMAGE_UNITS),f=i.getParameter(i.MAX_VERTEX_TEXTURE_IMAGE_UNITS),v=i.getParameter(i.MAX_TEXTURE_SIZE),g=i.getParameter(i.MAX_CUBE_MAP_TEXTURE_SIZE),m=i.getParameter(i.MAX_VERTEX_ATTRIBS),p=i.getParameter(i.MAX_VERTEX_UNIFORM_VECTORS),x=i.getParameter(i.MAX_VARYING_VECTORS),b=i.getParameter(i.MAX_FRAGMENT_UNIFORM_VECTORS),w=f>0,O=i.getParameter(i.MAX_SAMPLES);return{isWebGL2:!0,getMaxAnisotropy:r,getMaxPrecision:l,textureFormatReadable:o,textureTypeReadable:a,precision:c,logarithmicDepthBuffer:h,maxTextures:d,maxVertexTextures:f,maxTextureSize:v,maxCubemapSize:g,maxAttributes:m,maxVertexUniforms:p,maxVaryings:x,maxFragmentUniforms:b,vertexTextures:w,maxSamples:O}}function V0(i){const e=this;let t=null,n=0,s=!1,r=!1;const o=new rs,a=new at,l={value:null,needsUpdate:!1};this.uniform=l,this.numPlanes=0,this.numIntersection=0,this.init=function(h,d){const f=h.length!==0||d||n!==0||s;return s=d,n=h.length,f},this.beginShadows=function(){r=!0,u(null)},this.endShadows=function(){r=!1},this.setGlobalState=function(h,d){t=u(h,d,0)},this.setState=function(h,d,f){const v=h.clippingPlanes,g=h.clipIntersection,m=h.clipShadows,p=i.get(h);if(!s||v===null||v.length===0||r&&!m)r?u(null):c();else{const x=r?0:n,b=x*4;let w=p.clippingState||null;l.value=w,w=u(v,d,b,f);for(let O=0;O!==b;++O)w[O]=t[O];p.clippingState=w,this.numIntersection=g?this.numPlanes:0,this.numPlanes+=x}};function c(){l.value!==t&&(l.value=t,l.needsUpdate=n>0),e.numPlanes=n,e.numIntersection=0}function u(h,d,f,v){const g=h!==null?h.length:0;let m=null;if(g!==0){if(m=l.value,v!==!0||m===null){const p=f+g*4,x=d.matrixWorldInverse;a.getNormalMatrix(x),(m===null||m.length<p)&&(m=new Float32Array(p));for(let b=0,w=f;b!==g;++b,w+=4)o.copy(h[b]).applyMatrix4(x,a),o.normal.toArray(m,w),m[w+3]=o.constant}l.value=m,l.needsUpdate=!0}return e.numPlanes=g,e.numIntersection=0,m}}function G0(i){let e=new WeakMap;function t(o,a){return a===bc?o.mapping=zr:a===Sc&&(o.mapping=Hr),o}function n(o){if(o&&o.isTexture){const a=o.mapping;if(a===bc||a===Sc)if(e.has(o)){const l=e.get(o).texture;return t(l,o.mapping)}else{const l=o.image;if(l&&l.height>0){const c=new ev(l.height);return c.fromEquirectangularTexture(i,o),e.set(o,c),o.addEventListener("dispose",s),t(c.texture,o.mapping)}else return null}}return o}function s(o){const a=o.target;a.removeEventListener("dispose",s);const l=e.get(a);l!==void 0&&(e.delete(a),l.dispose())}function r(){e=new WeakMap}return{get:n,dispose:r}}class Aa extends qf{constructor(e=-1,t=1,n=1,s=-1,r=.1,o=2e3){super(),this.isOrthographicCamera=!0,this.type="OrthographicCamera",this.zoom=1,this.view=null,this.left=e,this.right=t,this.top=n,this.bottom=s,this.near=r,this.far=o,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.left=e.left,this.right=e.right,this.top=e.top,this.bottom=e.bottom,this.near=e.near,this.far=e.far,this.zoom=e.zoom,this.view=e.view===null?null:Object.assign({},e.view),this}setViewOffset(e,t,n,s,r,o){this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=n,this.view.offsetY=s,this.view.width=r,this.view.height=o,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const e=(this.right-this.left)/(2*this.zoom),t=(this.top-this.bottom)/(2*this.zoom),n=(this.right+this.left)/2,s=(this.top+this.bottom)/2;let r=n-e,o=n+e,a=s+t,l=s-t;if(this.view!==null&&this.view.enabled){const c=(this.right-this.left)/this.view.fullWidth/this.zoom,u=(this.top-this.bottom)/this.view.fullHeight/this.zoom;r+=c*this.view.offsetX,o=r+c*this.view.width,a-=u*this.view.offsetY,l=a-u*this.view.height}this.projectionMatrix.makeOrthographic(r,o,a,l,this.near,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){const t=super.toJSON(e);return t.object.zoom=this.zoom,t.object.left=this.left,t.object.right=this.right,t.object.top=this.top,t.object.bottom=this.bottom,t.object.near=this.near,t.object.far=this.far,this.view!==null&&(t.object.view=Object.assign({},this.view)),t}}const Ir=4,zh=[.125,.215,.35,.446,.526,.582],Os=20,jl=new Aa,Hh=new st;let Kl=null,Zl=0,Jl=0,Ql=!1;const Ds=(1+Math.sqrt(5))/2,Er=1/Ds,Vh=[new G(-Ds,Er,0),new G(Ds,Er,0),new G(-Er,0,Ds),new G(Er,0,Ds),new G(0,Ds,-Er),new G(0,Ds,Er),new G(-1,1,-1),new G(1,1,-1),new G(-1,1,1),new G(1,1,1)];class Gh{constructor(e){this._renderer=e,this._pingPongRenderTarget=null,this._lodMax=0,this._cubeSize=0,this._lodPlanes=[],this._sizeLods=[],this._sigmas=[],this._blurMaterial=null,this._cubemapMaterial=null,this._equirectMaterial=null,this._compileMaterial(this._blurMaterial)}fromScene(e,t=0,n=.1,s=100){Kl=this._renderer.getRenderTarget(),Zl=this._renderer.getActiveCubeFace(),Jl=this._renderer.getActiveMipmapLevel(),Ql=this._renderer.xr.enabled,this._renderer.xr.enabled=!1,this._setSize(256);const r=this._allocateTargets();return r.depthBuffer=!0,this._sceneToCubeUV(e,n,s,r),t>0&&this._blur(r,0,0,t),this._applyPMREM(r),this._cleanup(r),r}fromEquirectangular(e,t=null){return this._fromTexture(e,t)}fromCubemap(e,t=null){return this._fromTexture(e,t)}compileCubemapShader(){this._cubemapMaterial===null&&(this._cubemapMaterial=Xh(),this._compileMaterial(this._cubemapMaterial))}compileEquirectangularShader(){this._equirectMaterial===null&&(this._equirectMaterial=qh(),this._compileMaterial(this._equirectMaterial))}dispose(){this._dispose(),this._cubemapMaterial!==null&&this._cubemapMaterial.dispose(),this._equirectMaterial!==null&&this._equirectMaterial.dispose()}_setSize(e){this._lodMax=Math.floor(Math.log2(e)),this._cubeSize=Math.pow(2,this._lodMax)}_dispose(){this._blurMaterial!==null&&this._blurMaterial.dispose(),this._pingPongRenderTarget!==null&&this._pingPongRenderTarget.dispose();for(let e=0;e<this._lodPlanes.length;e++)this._lodPlanes[e].dispose()}_cleanup(e){this._renderer.setRenderTarget(Kl,Zl,Jl),this._renderer.xr.enabled=Ql,e.scissorTest=!1,mo(e,0,0,e.width,e.height)}_fromTexture(e,t){e.mapping===zr||e.mapping===Hr?this._setSize(e.image.length===0?16:e.image[0].width||e.image[0].image.width):this._setSize(e.image.width/4),Kl=this._renderer.getRenderTarget(),Zl=this._renderer.getActiveCubeFace(),Jl=this._renderer.getActiveMipmapLevel(),Ql=this._renderer.xr.enabled,this._renderer.xr.enabled=!1;const n=t||this._allocateTargets();return this._textureToCubeUV(e,n),this._applyPMREM(n),this._cleanup(n),n}_allocateTargets(){const e=3*Math.max(this._cubeSize,112),t=4*this._cubeSize,n={magFilter:ui,minFilter:ui,generateMipmaps:!1,type:ka,format:fi,colorSpace:gs,depthBuffer:!1},s=Wh(e,t,n);if(this._pingPongRenderTarget===null||this._pingPongRenderTarget.width!==e||this._pingPongRenderTarget.height!==t){this._pingPongRenderTarget!==null&&this._dispose(),this._pingPongRenderTarget=Wh(e,t,n);const{_lodMax:r}=this;({sizeLods:this._sizeLods,lodPlanes:this._lodPlanes,sigmas:this._sigmas}=W0(r)),this._blurMaterial=q0(r,e,t)}return s}_compileMaterial(e){const t=new Pn(this._lodPlanes[0],e);this._renderer.compile(t,jl)}_sceneToCubeUV(e,t,n,s){const a=new Sn(90,1,t,n),l=[1,-1,1,1,1,1],c=[1,1,1,-1,-1,-1],u=this._renderer,h=u.autoClear,d=u.toneMapping;u.getClearColor(Hh),u.toneMapping=cs,u.autoClear=!1;const f=new Ta({name:"PMREM.Background",side:Nn,depthWrite:!1,depthTest:!1}),v=new Pn(new Gi,f);let g=!1;const m=e.background;m?m.isColor&&(f.color.copy(m),e.background=null,g=!0):(f.color.copy(Hh),g=!0);for(let p=0;p<6;p++){const x=p%3;x===0?(a.up.set(0,l[p],0),a.lookAt(c[p],0,0)):x===1?(a.up.set(0,0,l[p]),a.lookAt(0,c[p],0)):(a.up.set(0,l[p],0),a.lookAt(0,0,c[p]));const b=this._cubeSize;mo(s,x*b,p>2?b:0,b,b),u.setRenderTarget(s),g&&u.render(v,a),u.render(e,a)}v.geometry.dispose(),v.material.dispose(),u.toneMapping=d,u.autoClear=h,e.background=m}_textureToCubeUV(e,t){const n=this._renderer,s=e.mapping===zr||e.mapping===Hr;s?(this._cubemapMaterial===null&&(this._cubemapMaterial=Xh()),this._cubemapMaterial.uniforms.flipEnvMap.value=e.isRenderTargetTexture===!1?-1:1):this._equirectMaterial===null&&(this._equirectMaterial=qh());const r=s?this._cubemapMaterial:this._equirectMaterial,o=new Pn(this._lodPlanes[0],r),a=r.uniforms;a.envMap.value=e;const l=this._cubeSize;mo(t,0,0,3*l,2*l),n.setRenderTarget(t),n.render(o,jl)}_applyPMREM(e){const t=this._renderer,n=t.autoClear;t.autoClear=!1;const s=this._lodPlanes.length;for(let r=1;r<s;r++){const o=Math.sqrt(this._sigmas[r]*this._sigmas[r]-this._sigmas[r-1]*this._sigmas[r-1]),a=Vh[(s-r-1)%Vh.length];this._blur(e,r-1,r,o,a)}t.autoClear=n}_blur(e,t,n,s,r){const o=this._pingPongRenderTarget;this._halfBlur(e,o,t,n,s,"latitudinal",r),this._halfBlur(o,e,n,n,s,"longitudinal",r)}_halfBlur(e,t,n,s,r,o,a){const l=this._renderer,c=this._blurMaterial;o!=="latitudinal"&&o!=="longitudinal"&&console.error("blur direction must be either latitudinal or longitudinal!");const u=3,h=new Pn(this._lodPlanes[s],c),d=c.uniforms,f=this._sizeLods[n]-1,v=isFinite(r)?Math.PI/(2*f):2*Math.PI/(2*Os-1),g=r/v,m=isFinite(r)?1+Math.floor(u*g):Os;m>Os&&console.warn(`sigmaRadians, ${r}, is too large and will clip, as it requested ${m} samples when the maximum is set to ${Os}`);const p=[];let x=0;for(let L=0;L<Os;++L){const k=L/g,E=Math.exp(-k*k/2);p.push(E),L===0?x+=E:L<m&&(x+=2*E)}for(let L=0;L<p.length;L++)p[L]=p[L]/x;d.envMap.value=e.texture,d.samples.value=m,d.weights.value=p,d.latitudinal.value=o==="latitudinal",a&&(d.poleAxis.value=a);const{_lodMax:b}=this;d.dTheta.value=v,d.mipInt.value=b-n;const w=this._sizeLods[s],O=3*w*(s>b-Ir?s-b+Ir:0),A=4*(this._cubeSize-w);mo(t,O,A,3*w,2*w),l.setRenderTarget(t),l.render(h,jl)}}function W0(i){const e=[],t=[],n=[];let s=i;const r=i-Ir+1+zh.length;for(let o=0;o<r;o++){const a=Math.pow(2,s);t.push(a);let l=1/a;o>i-Ir?l=zh[o-i+Ir-1]:o===0&&(l=0),n.push(l);const c=1/(a-2),u=-c,h=1+c,d=[u,u,h,u,h,h,u,u,h,h,u,h],f=6,v=6,g=3,m=2,p=1,x=new Float32Array(g*v*f),b=new Float32Array(m*v*f),w=new Float32Array(p*v*f);for(let A=0;A<f;A++){const L=A%3*2/3-1,k=A>2?0:-1,E=[L,k,0,L+2/3,k,0,L+2/3,k+1,0,L,k,0,L+2/3,k+1,0,L,k+1,0];x.set(E,g*v*A),b.set(d,m*v*A);const y=[A,A,A,A,A,A];w.set(y,p*v*A)}const O=new Xn;O.setAttribute("position",new pi(x,g)),O.setAttribute("uv",new pi(b,m)),O.setAttribute("faceIndex",new pi(w,p)),e.push(O),s>Ir&&s--}return{lodPlanes:e,sizeLods:t,sigmas:n}}function Wh(i,e,t){const n=new Gs(i,e,t);return n.texture.mapping=nl,n.texture.name="PMREM.cubeUv",n.scissorTest=!0,n}function mo(i,e,t,n,s){i.viewport.set(e,t,n,s),i.scissor.set(e,t,n,s)}function q0(i,e,t){const n=new Float32Array(Os),s=new G(0,1,0);return new ds({name:"SphericalGaussianBlur",defines:{n:Os,CUBEUV_TEXEL_WIDTH:1/e,CUBEUV_TEXEL_HEIGHT:1/t,CUBEUV_MAX_MIP:`${i}.0`},uniforms:{envMap:{value:null},samples:{value:1},weights:{value:n},latitudinal:{value:!1},dTheta:{value:0},mipInt:{value:0},poleAxis:{value:s}},vertexShader:Tu(),fragmentShader:`

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
		`,blending:ls,depthTest:!1,depthWrite:!1})}function qh(){return new ds({name:"EquirectangularToCubeUV",uniforms:{envMap:{value:null}},vertexShader:Tu(),fragmentShader:`

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
		`,blending:ls,depthTest:!1,depthWrite:!1})}function Xh(){return new ds({name:"CubemapToCubeUV",uniforms:{envMap:{value:null},flipEnvMap:{value:-1}},vertexShader:Tu(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			uniform float flipEnvMap;

			varying vec3 vOutputDirection;

			uniform samplerCube envMap;

			void main() {

				gl_FragColor = textureCube( envMap, vec3( flipEnvMap * vOutputDirection.x, vOutputDirection.yz ) );

			}
		`,blending:ls,depthTest:!1,depthWrite:!1})}function Tu(){return`

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
	`}function X0(i){let e=new WeakMap,t=null;function n(a){if(a&&a.isTexture){const l=a.mapping,c=l===bc||l===Sc,u=l===zr||l===Hr;if(c||u){let h=e.get(a);const d=h!==void 0?h.texture.pmremVersion:0;if(a.isRenderTargetTexture&&a.pmremVersion!==d)return t===null&&(t=new Gh(i)),h=c?t.fromEquirectangular(a,h):t.fromCubemap(a,h),h.texture.pmremVersion=a.pmremVersion,e.set(a,h),h.texture;if(h!==void 0)return h.texture;{const f=a.image;return c&&f&&f.height>0||u&&f&&s(f)?(t===null&&(t=new Gh(i)),h=c?t.fromEquirectangular(a):t.fromCubemap(a),h.texture.pmremVersion=a.pmremVersion,e.set(a,h),a.addEventListener("dispose",r),h.texture):null}}}return a}function s(a){let l=0;const c=6;for(let u=0;u<c;u++)a[u]!==void 0&&l++;return l===c}function r(a){const l=a.target;l.removeEventListener("dispose",r);const c=e.get(l);c!==void 0&&(e.delete(l),c.dispose())}function o(){e=new WeakMap,t!==null&&(t.dispose(),t=null)}return{get:n,dispose:o}}function $0(i){const e={};function t(n){if(e[n]!==void 0)return e[n];let s;switch(n){case"WEBGL_depth_texture":s=i.getExtension("WEBGL_depth_texture")||i.getExtension("MOZ_WEBGL_depth_texture")||i.getExtension("WEBKIT_WEBGL_depth_texture");break;case"EXT_texture_filter_anisotropic":s=i.getExtension("EXT_texture_filter_anisotropic")||i.getExtension("MOZ_EXT_texture_filter_anisotropic")||i.getExtension("WEBKIT_EXT_texture_filter_anisotropic");break;case"WEBGL_compressed_texture_s3tc":s=i.getExtension("WEBGL_compressed_texture_s3tc")||i.getExtension("MOZ_WEBGL_compressed_texture_s3tc")||i.getExtension("WEBKIT_WEBGL_compressed_texture_s3tc");break;case"WEBGL_compressed_texture_pvrtc":s=i.getExtension("WEBGL_compressed_texture_pvrtc")||i.getExtension("WEBKIT_WEBGL_compressed_texture_pvrtc");break;default:s=i.getExtension(n)}return e[n]=s,s}return{has:function(n){return t(n)!==null},init:function(){t("EXT_color_buffer_float"),t("WEBGL_clip_cull_distance"),t("OES_texture_float_linear"),t("EXT_color_buffer_half_float"),t("WEBGL_multisampled_render_to_texture"),t("WEBGL_render_shared_exponent")},get:function(n){const s=t(n);return s===null&&Fr("THREE.WebGLRenderer: "+n+" extension not supported."),s}}}function Y0(i,e,t,n){const s={},r=new WeakMap;function o(h){const d=h.target;d.index!==null&&e.remove(d.index);for(const v in d.attributes)e.remove(d.attributes[v]);for(const v in d.morphAttributes){const g=d.morphAttributes[v];for(let m=0,p=g.length;m<p;m++)e.remove(g[m])}d.removeEventListener("dispose",o),delete s[d.id];const f=r.get(d);f&&(e.remove(f),r.delete(d)),n.releaseStatesOfGeometry(d),d.isInstancedBufferGeometry===!0&&delete d._maxInstanceCount,t.memory.geometries--}function a(h,d){return s[d.id]===!0||(d.addEventListener("dispose",o),s[d.id]=!0,t.memory.geometries++),d}function l(h){const d=h.attributes;for(const v in d)e.update(d[v],i.ARRAY_BUFFER);const f=h.morphAttributes;for(const v in f){const g=f[v];for(let m=0,p=g.length;m<p;m++)e.update(g[m],i.ARRAY_BUFFER)}}function c(h){const d=[],f=h.index,v=h.attributes.position;let g=0;if(f!==null){const x=f.array;g=f.version;for(let b=0,w=x.length;b<w;b+=3){const O=x[b+0],A=x[b+1],L=x[b+2];d.push(O,A,A,L,L,O)}}else if(v!==void 0){const x=v.array;g=v.version;for(let b=0,w=x.length/3-1;b<w;b+=3){const O=b+0,A=b+1,L=b+2;d.push(O,A,A,L,L,O)}}else return;const m=new(kf(d)?Gf:Vf)(d,1);m.version=g;const p=r.get(h);p&&e.remove(p),r.set(h,m)}function u(h){const d=r.get(h);if(d){const f=h.index;f!==null&&d.version<f.version&&c(h)}else c(h);return r.get(h)}return{get:a,update:l,getWireframeAttribute:u}}function j0(i,e,t){let n;function s(d){n=d}let r,o;function a(d){r=d.type,o=d.bytesPerElement}function l(d,f){i.drawElements(n,f,r,d*o),t.update(f,n,1)}function c(d,f,v){v!==0&&(i.drawElementsInstanced(n,f,r,d*o,v),t.update(f,n,v))}function u(d,f,v){if(v===0)return;e.get("WEBGL_multi_draw").multiDrawElementsWEBGL(n,f,0,r,d,0,v);let m=0;for(let p=0;p<v;p++)m+=f[p];t.update(m,n,1)}function h(d,f,v,g){if(v===0)return;const m=e.get("WEBGL_multi_draw");if(m===null)for(let p=0;p<d.length;p++)c(d[p]/o,f[p],g[p]);else{m.multiDrawElementsInstancedWEBGL(n,f,0,r,d,0,g,0,v);let p=0;for(let x=0;x<v;x++)p+=f[x];for(let x=0;x<g.length;x++)t.update(p,n,g[x])}}this.setMode=s,this.setIndex=a,this.render=l,this.renderInstances=c,this.renderMultiDraw=u,this.renderMultiDrawInstances=h}function K0(i){const e={geometries:0,textures:0},t={frame:0,calls:0,triangles:0,points:0,lines:0};function n(r,o,a){switch(t.calls++,o){case i.TRIANGLES:t.triangles+=a*(r/3);break;case i.LINES:t.lines+=a*(r/2);break;case i.LINE_STRIP:t.lines+=a*(r-1);break;case i.LINE_LOOP:t.lines+=a*r;break;case i.POINTS:t.points+=a*r;break;default:console.error("THREE.WebGLInfo: Unknown draw mode:",o);break}}function s(){t.calls=0,t.triangles=0,t.points=0,t.lines=0}return{memory:e,render:t,programs:null,autoReset:!0,reset:s,update:n}}function Z0(i,e,t){const n=new WeakMap,s=new en;function r(o,a,l){const c=o.morphTargetInfluences,u=a.morphAttributes.position||a.morphAttributes.normal||a.morphAttributes.color,h=u!==void 0?u.length:0;let d=n.get(a);if(d===void 0||d.count!==h){let y=function(){k.dispose(),n.delete(a),a.removeEventListener("dispose",y)};var f=y;d!==void 0&&d.texture.dispose();const v=a.morphAttributes.position!==void 0,g=a.morphAttributes.normal!==void 0,m=a.morphAttributes.color!==void 0,p=a.morphAttributes.position||[],x=a.morphAttributes.normal||[],b=a.morphAttributes.color||[];let w=0;v===!0&&(w=1),g===!0&&(w=2),m===!0&&(w=3);let O=a.attributes.position.count*w,A=1;O>e.maxTextureSize&&(A=Math.ceil(O/e.maxTextureSize),O=e.maxTextureSize);const L=new Float32Array(O*A*4*h),k=new zf(L,O,A,h);k.type=Hi,k.needsUpdate=!0;const E=w*4;for(let P=0;P<h;P++){const K=p[P],z=x[P],Z=b[P],q=O*A*4*P;for(let Q=0;Q<K.count;Q++){const $=Q*E;v===!0&&(s.fromBufferAttribute(K,Q),L[q+$+0]=s.x,L[q+$+1]=s.y,L[q+$+2]=s.z,L[q+$+3]=0),g===!0&&(s.fromBufferAttribute(z,Q),L[q+$+4]=s.x,L[q+$+5]=s.y,L[q+$+6]=s.z,L[q+$+7]=0),m===!0&&(s.fromBufferAttribute(Z,Q),L[q+$+8]=s.x,L[q+$+9]=s.y,L[q+$+10]=s.z,L[q+$+11]=Z.itemSize===4?s.w:1)}}d={count:h,texture:k,size:new qe(O,A)},n.set(a,d),a.addEventListener("dispose",y)}if(o.isInstancedMesh===!0&&o.morphTexture!==null)l.getUniforms().setValue(i,"morphTexture",o.morphTexture,t);else{let v=0;for(let m=0;m<c.length;m++)v+=c[m];const g=a.morphTargetsRelative?1:1-v;l.getUniforms().setValue(i,"morphTargetBaseInfluence",g),l.getUniforms().setValue(i,"morphTargetInfluences",c)}l.getUniforms().setValue(i,"morphTargetsTexture",d.texture,t),l.getUniforms().setValue(i,"morphTargetsTextureSize",d.size)}return{update:r}}function J0(i,e,t,n){let s=new WeakMap;function r(l){const c=n.render.frame,u=l.geometry,h=e.get(l,u);if(s.get(h)!==c&&(e.update(h),s.set(h,c)),l.isInstancedMesh&&(l.hasEventListener("dispose",a)===!1&&l.addEventListener("dispose",a),s.get(l)!==c&&(t.update(l.instanceMatrix,i.ARRAY_BUFFER),l.instanceColor!==null&&t.update(l.instanceColor,i.ARRAY_BUFFER),s.set(l,c))),l.isSkinnedMesh){const d=l.skeleton;s.get(d)!==c&&(d.update(),s.set(d,c))}return h}function o(){s=new WeakMap}function a(l){const c=l.target;c.removeEventListener("dispose",a),t.remove(c.instanceMatrix),c.instanceColor!==null&&t.remove(c.instanceColor)}return{update:r,dispose:o}}class Yf extends Dn{constructor(e,t,n,s,r,o,a,l,c,u=Nr){if(u!==Nr&&u!==Gr)throw new Error("DepthTexture format must be either THREE.DepthFormat or THREE.DepthStencilFormat");n===void 0&&u===Nr&&(n=Vs),n===void 0&&u===Gr&&(n=Vr),super(null,s,r,o,a,l,u,n,c),this.isDepthTexture=!0,this.image={width:e,height:t},this.magFilter=a!==void 0?a:ei,this.minFilter=l!==void 0?l:ei,this.flipY=!1,this.generateMipmaps=!1,this.compareFunction=null}copy(e){return super.copy(e),this.compareFunction=e.compareFunction,this}toJSON(e){const t=super.toJSON(e);return this.compareFunction!==null&&(t.compareFunction=this.compareFunction),t}}const jf=new Dn,$h=new Yf(1,1),Kf=new zf,Zf=new kg,Jf=new Xf,Yh=[],jh=[],Kh=new Float32Array(16),Zh=new Float32Array(9),Jh=new Float32Array(4);function Zr(i,e,t){const n=i[0];if(n<=0||n>0)return i;const s=e*t;let r=Yh[s];if(r===void 0&&(r=new Float32Array(s),Yh[s]=r),e!==0){n.toArray(r,0);for(let o=1,a=0;o!==e;++o)a+=t,i[o].toArray(r,a)}return r}function nn(i,e){if(i.length!==e.length)return!1;for(let t=0,n=i.length;t<n;t++)if(i[t]!==e[t])return!1;return!0}function sn(i,e){for(let t=0,n=e.length;t<n;t++)i[t]=e[t]}function ol(i,e){let t=jh[e];t===void 0&&(t=new Int32Array(e),jh[e]=t);for(let n=0;n!==e;++n)t[n]=i.allocateTextureUnit();return t}function Q0(i,e){const t=this.cache;t[0]!==e&&(i.uniform1f(this.addr,e),t[0]=e)}function ex(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(i.uniform2f(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(nn(t,e))return;i.uniform2fv(this.addr,e),sn(t,e)}}function tx(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(i.uniform3f(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else if(e.r!==void 0)(t[0]!==e.r||t[1]!==e.g||t[2]!==e.b)&&(i.uniform3f(this.addr,e.r,e.g,e.b),t[0]=e.r,t[1]=e.g,t[2]=e.b);else{if(nn(t,e))return;i.uniform3fv(this.addr,e),sn(t,e)}}function nx(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(i.uniform4f(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(nn(t,e))return;i.uniform4fv(this.addr,e),sn(t,e)}}function ix(i,e){const t=this.cache,n=e.elements;if(n===void 0){if(nn(t,e))return;i.uniformMatrix2fv(this.addr,!1,e),sn(t,e)}else{if(nn(t,n))return;Jh.set(n),i.uniformMatrix2fv(this.addr,!1,Jh),sn(t,n)}}function sx(i,e){const t=this.cache,n=e.elements;if(n===void 0){if(nn(t,e))return;i.uniformMatrix3fv(this.addr,!1,e),sn(t,e)}else{if(nn(t,n))return;Zh.set(n),i.uniformMatrix3fv(this.addr,!1,Zh),sn(t,n)}}function rx(i,e){const t=this.cache,n=e.elements;if(n===void 0){if(nn(t,e))return;i.uniformMatrix4fv(this.addr,!1,e),sn(t,e)}else{if(nn(t,n))return;Kh.set(n),i.uniformMatrix4fv(this.addr,!1,Kh),sn(t,n)}}function ax(i,e){const t=this.cache;t[0]!==e&&(i.uniform1i(this.addr,e),t[0]=e)}function ox(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(i.uniform2i(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(nn(t,e))return;i.uniform2iv(this.addr,e),sn(t,e)}}function lx(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(i.uniform3i(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(nn(t,e))return;i.uniform3iv(this.addr,e),sn(t,e)}}function cx(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(i.uniform4i(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(nn(t,e))return;i.uniform4iv(this.addr,e),sn(t,e)}}function ux(i,e){const t=this.cache;t[0]!==e&&(i.uniform1ui(this.addr,e),t[0]=e)}function hx(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(i.uniform2ui(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(nn(t,e))return;i.uniform2uiv(this.addr,e),sn(t,e)}}function dx(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(i.uniform3ui(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(nn(t,e))return;i.uniform3uiv(this.addr,e),sn(t,e)}}function fx(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(i.uniform4ui(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(nn(t,e))return;i.uniform4uiv(this.addr,e),sn(t,e)}}function px(i,e,t){const n=this.cache,s=t.allocateTextureUnit();n[0]!==s&&(i.uniform1i(this.addr,s),n[0]=s);let r;this.type===i.SAMPLER_2D_SHADOW?($h.compareFunction=Ff,r=$h):r=jf,t.setTexture2D(e||r,s)}function mx(i,e,t){const n=this.cache,s=t.allocateTextureUnit();n[0]!==s&&(i.uniform1i(this.addr,s),n[0]=s),t.setTexture3D(e||Zf,s)}function gx(i,e,t){const n=this.cache,s=t.allocateTextureUnit();n[0]!==s&&(i.uniform1i(this.addr,s),n[0]=s),t.setTextureCube(e||Jf,s)}function vx(i,e,t){const n=this.cache,s=t.allocateTextureUnit();n[0]!==s&&(i.uniform1i(this.addr,s),n[0]=s),t.setTexture2DArray(e||Kf,s)}function _x(i){switch(i){case 5126:return Q0;case 35664:return ex;case 35665:return tx;case 35666:return nx;case 35674:return ix;case 35675:return sx;case 35676:return rx;case 5124:case 35670:return ax;case 35667:case 35671:return ox;case 35668:case 35672:return lx;case 35669:case 35673:return cx;case 5125:return ux;case 36294:return hx;case 36295:return dx;case 36296:return fx;case 35678:case 36198:case 36298:case 36306:case 35682:return px;case 35679:case 36299:case 36307:return mx;case 35680:case 36300:case 36308:case 36293:return gx;case 36289:case 36303:case 36311:case 36292:return vx}}function xx(i,e){i.uniform1fv(this.addr,e)}function yx(i,e){const t=Zr(e,this.size,2);i.uniform2fv(this.addr,t)}function bx(i,e){const t=Zr(e,this.size,3);i.uniform3fv(this.addr,t)}function Sx(i,e){const t=Zr(e,this.size,4);i.uniform4fv(this.addr,t)}function Mx(i,e){const t=Zr(e,this.size,4);i.uniformMatrix2fv(this.addr,!1,t)}function wx(i,e){const t=Zr(e,this.size,9);i.uniformMatrix3fv(this.addr,!1,t)}function Ex(i,e){const t=Zr(e,this.size,16);i.uniformMatrix4fv(this.addr,!1,t)}function Tx(i,e){i.uniform1iv(this.addr,e)}function Ax(i,e){i.uniform2iv(this.addr,e)}function Cx(i,e){i.uniform3iv(this.addr,e)}function Rx(i,e){i.uniform4iv(this.addr,e)}function Px(i,e){i.uniform1uiv(this.addr,e)}function Lx(i,e){i.uniform2uiv(this.addr,e)}function Dx(i,e){i.uniform3uiv(this.addr,e)}function Ix(i,e){i.uniform4uiv(this.addr,e)}function Ux(i,e,t){const n=this.cache,s=e.length,r=ol(t,s);nn(n,r)||(i.uniform1iv(this.addr,r),sn(n,r));for(let o=0;o!==s;++o)t.setTexture2D(e[o]||jf,r[o])}function Nx(i,e,t){const n=this.cache,s=e.length,r=ol(t,s);nn(n,r)||(i.uniform1iv(this.addr,r),sn(n,r));for(let o=0;o!==s;++o)t.setTexture3D(e[o]||Zf,r[o])}function Ox(i,e,t){const n=this.cache,s=e.length,r=ol(t,s);nn(n,r)||(i.uniform1iv(this.addr,r),sn(n,r));for(let o=0;o!==s;++o)t.setTextureCube(e[o]||Jf,r[o])}function Fx(i,e,t){const n=this.cache,s=e.length,r=ol(t,s);nn(n,r)||(i.uniform1iv(this.addr,r),sn(n,r));for(let o=0;o!==s;++o)t.setTexture2DArray(e[o]||Kf,r[o])}function kx(i){switch(i){case 5126:return xx;case 35664:return yx;case 35665:return bx;case 35666:return Sx;case 35674:return Mx;case 35675:return wx;case 35676:return Ex;case 5124:case 35670:return Tx;case 35667:case 35671:return Ax;case 35668:case 35672:return Cx;case 35669:case 35673:return Rx;case 5125:return Px;case 36294:return Lx;case 36295:return Dx;case 36296:return Ix;case 35678:case 36198:case 36298:case 36306:case 35682:return Ux;case 35679:case 36299:case 36307:return Nx;case 35680:case 36300:case 36308:case 36293:return Ox;case 36289:case 36303:case 36311:case 36292:return Fx}}class Bx{constructor(e,t,n){this.id=e,this.addr=n,this.cache=[],this.type=t.type,this.setValue=_x(t.type)}}class zx{constructor(e,t,n){this.id=e,this.addr=n,this.cache=[],this.type=t.type,this.size=t.size,this.setValue=kx(t.type)}}class Hx{constructor(e){this.id=e,this.seq=[],this.map={}}setValue(e,t,n){const s=this.seq;for(let r=0,o=s.length;r!==o;++r){const a=s[r];a.setValue(e,t[a.id],n)}}}const ec=/(\w+)(\])?(\[|\.)?/g;function Qh(i,e){i.seq.push(e),i.map[e.id]=e}function Vx(i,e,t){const n=i.name,s=n.length;for(ec.lastIndex=0;;){const r=ec.exec(n),o=ec.lastIndex;let a=r[1];const l=r[2]==="]",c=r[3];if(l&&(a=a|0),c===void 0||c==="["&&o+2===s){Qh(t,c===void 0?new Bx(a,i,e):new zx(a,i,e));break}else{let h=t.map[a];h===void 0&&(h=new Hx(a),Qh(t,h)),t=h}}}class Oo{constructor(e,t){this.seq=[],this.map={};const n=e.getProgramParameter(t,e.ACTIVE_UNIFORMS);for(let s=0;s<n;++s){const r=e.getActiveUniform(t,s),o=e.getUniformLocation(t,r.name);Vx(r,o,this)}}setValue(e,t,n,s){const r=this.map[t];r!==void 0&&r.setValue(e,n,s)}setOptional(e,t,n){const s=t[n];s!==void 0&&this.setValue(e,n,s)}static upload(e,t,n,s){for(let r=0,o=t.length;r!==o;++r){const a=t[r],l=n[a.id];l.needsUpdate!==!1&&a.setValue(e,l.value,s)}}static seqWithValue(e,t){const n=[];for(let s=0,r=e.length;s!==r;++s){const o=e[s];o.id in t&&n.push(o)}return n}}function ed(i,e,t){const n=i.createShader(e);return i.shaderSource(n,t),i.compileShader(n),n}const Gx=37297;let Wx=0;function qx(i,e){const t=i.split(`
`),n=[],s=Math.max(e-6,0),r=Math.min(e+6,t.length);for(let o=s;o<r;o++){const a=o+1;n.push(`${a===e?">":" "} ${a}: ${t[o]}`)}return n.join(`
`)}function Xx(i){const e=wt.getPrimaries(wt.workingColorSpace),t=wt.getPrimaries(i);let n;switch(e===t?n="":e===Vo&&t===Ho?n="LinearDisplayP3ToLinearSRGB":e===Ho&&t===Vo&&(n="LinearSRGBToLinearDisplayP3"),i){case gs:case il:return[n,"LinearTransferOETF"];case Mi:case Su:return[n,"sRGBTransferOETF"];default:return console.warn("THREE.WebGLProgram: Unsupported color space:",i),[n,"LinearTransferOETF"]}}function td(i,e,t){const n=i.getShaderParameter(e,i.COMPILE_STATUS),s=i.getShaderInfoLog(e).trim();if(n&&s==="")return"";const r=/ERROR: 0:(\d+)/.exec(s);if(r){const o=parseInt(r[1]);return t.toUpperCase()+`

`+s+`

`+qx(i.getShaderSource(e),o)}else return s}function $x(i,e){const t=Xx(e);return`vec4 ${i}( vec4 value ) { return ${t[0]}( ${t[1]}( value ) ); }`}function Yx(i,e){let t;switch(e){case Zm:t="Linear";break;case Jm:t="Reinhard";break;case Qm:t="Cineon";break;case wf:t="ACESFilmic";break;case tg:t="AgX";break;case ng:t="Neutral";break;case eg:t="Custom";break;default:console.warn("THREE.WebGLProgram: Unsupported toneMapping:",e),t="Linear"}return"vec3 "+i+"( vec3 color ) { return "+t+"ToneMapping( color ); }"}const go=new G;function jx(){wt.getLuminanceCoefficients(go);const i=go.x.toFixed(4),e=go.y.toFixed(4),t=go.z.toFixed(4);return["float luminance( const in vec3 rgb ) {",`	const vec3 weights = vec3( ${i}, ${e}, ${t} );`,"	return dot( weights, rgb );","}"].join(`
`)}function Kx(i){return[i.extensionClipCullDistance?"#extension GL_ANGLE_clip_cull_distance : require":"",i.extensionMultiDraw?"#extension GL_ANGLE_multi_draw : require":""].filter(ba).join(`
`)}function Zx(i){const e=[];for(const t in i){const n=i[t];n!==!1&&e.push("#define "+t+" "+n)}return e.join(`
`)}function Jx(i,e){const t={},n=i.getProgramParameter(e,i.ACTIVE_ATTRIBUTES);for(let s=0;s<n;s++){const r=i.getActiveAttrib(e,s),o=r.name;let a=1;r.type===i.FLOAT_MAT2&&(a=2),r.type===i.FLOAT_MAT3&&(a=3),r.type===i.FLOAT_MAT4&&(a=4),t[o]={type:r.type,location:i.getAttribLocation(e,o),locationSize:a}}return t}function ba(i){return i!==""}function nd(i,e){const t=e.numSpotLightShadows+e.numSpotLightMaps-e.numSpotLightShadowsWithMaps;return i.replace(/NUM_DIR_LIGHTS/g,e.numDirLights).replace(/NUM_SPOT_LIGHTS/g,e.numSpotLights).replace(/NUM_SPOT_LIGHT_MAPS/g,e.numSpotLightMaps).replace(/NUM_SPOT_LIGHT_COORDS/g,t).replace(/NUM_RECT_AREA_LIGHTS/g,e.numRectAreaLights).replace(/NUM_POINT_LIGHTS/g,e.numPointLights).replace(/NUM_HEMI_LIGHTS/g,e.numHemiLights).replace(/NUM_DIR_LIGHT_SHADOWS/g,e.numDirLightShadows).replace(/NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS/g,e.numSpotLightShadowsWithMaps).replace(/NUM_SPOT_LIGHT_SHADOWS/g,e.numSpotLightShadows).replace(/NUM_POINT_LIGHT_SHADOWS/g,e.numPointLightShadows)}function id(i,e){return i.replace(/NUM_CLIPPING_PLANES/g,e.numClippingPlanes).replace(/UNION_CLIPPING_PLANES/g,e.numClippingPlanes-e.numClipIntersection)}const Qx=/^[ \t]*#include +<([\w\d./]+)>/gm;function Jc(i){return i.replace(Qx,ty)}const ey=new Map;function ty(i,e){let t=rt[e];if(t===void 0){const n=ey.get(e);if(n!==void 0)t=rt[n],console.warn('THREE.WebGLRenderer: Shader chunk "%s" has been deprecated. Use "%s" instead.',e,n);else throw new Error("Can not resolve #include <"+e+">")}return Jc(t)}const ny=/#pragma unroll_loop_start\s+for\s*\(\s*int\s+i\s*=\s*(\d+)\s*;\s*i\s*<\s*(\d+)\s*;\s*i\s*\+\+\s*\)\s*{([\s\S]+?)}\s+#pragma unroll_loop_end/g;function sd(i){return i.replace(ny,iy)}function iy(i,e,t,n){let s="";for(let r=parseInt(e);r<parseInt(t);r++)s+=n.replace(/\[\s*i\s*\]/g,"[ "+r+" ]").replace(/UNROLLED_LOOP_INDEX/g,r);return s}function rd(i){let e=`precision ${i.precision} float;
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
#define LOW_PRECISION`),e}function sy(i){let e="SHADOWMAP_TYPE_BASIC";return i.shadowMapType===bf?e="SHADOWMAP_TYPE_PCF":i.shadowMapType===Sf?e="SHADOWMAP_TYPE_PCF_SOFT":i.shadowMapType===Bi&&(e="SHADOWMAP_TYPE_VSM"),e}function ry(i){let e="ENVMAP_TYPE_CUBE";if(i.envMap)switch(i.envMapMode){case zr:case Hr:e="ENVMAP_TYPE_CUBE";break;case nl:e="ENVMAP_TYPE_CUBE_UV";break}return e}function ay(i){let e="ENVMAP_MODE_REFLECTION";if(i.envMap)switch(i.envMapMode){case Hr:e="ENVMAP_MODE_REFRACTION";break}return e}function oy(i){let e="ENVMAP_BLENDING_NONE";if(i.envMap)switch(i.combine){case Mf:e="ENVMAP_BLENDING_MULTIPLY";break;case jm:e="ENVMAP_BLENDING_MIX";break;case Km:e="ENVMAP_BLENDING_ADD";break}return e}function ly(i){const e=i.envMapCubeUVHeight;if(e===null)return null;const t=Math.log2(e)-2,n=1/e;return{texelWidth:1/(3*Math.max(Math.pow(2,t),7*16)),texelHeight:n,maxMip:t}}function cy(i,e,t,n){const s=i.getContext(),r=t.defines;let o=t.vertexShader,a=t.fragmentShader;const l=sy(t),c=ry(t),u=ay(t),h=oy(t),d=ly(t),f=Kx(t),v=Zx(r),g=s.createProgram();let m,p,x=t.glslVersion?"#version "+t.glslVersion+`
`:"";t.isRawShaderMaterial?(m=["#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,v].filter(ba).join(`
`),m.length>0&&(m+=`
`),p=["#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,v].filter(ba).join(`
`),p.length>0&&(p+=`
`)):(m=[rd(t),"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,v,t.extensionClipCullDistance?"#define USE_CLIP_DISTANCE":"",t.batching?"#define USE_BATCHING":"",t.batchingColor?"#define USE_BATCHING_COLOR":"",t.instancing?"#define USE_INSTANCING":"",t.instancingColor?"#define USE_INSTANCING_COLOR":"",t.instancingMorph?"#define USE_INSTANCING_MORPH":"",t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.map?"#define USE_MAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+u:"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",t.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",t.displacementMap?"#define USE_DISPLACEMENTMAP":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.anisotropy?"#define USE_ANISOTROPY":"",t.anisotropyMap?"#define USE_ANISOTROPYMAP":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",t.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaHash?"#define USE_ALPHAHASH":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",t.mapUv?"#define MAP_UV "+t.mapUv:"",t.alphaMapUv?"#define ALPHAMAP_UV "+t.alphaMapUv:"",t.lightMapUv?"#define LIGHTMAP_UV "+t.lightMapUv:"",t.aoMapUv?"#define AOMAP_UV "+t.aoMapUv:"",t.emissiveMapUv?"#define EMISSIVEMAP_UV "+t.emissiveMapUv:"",t.bumpMapUv?"#define BUMPMAP_UV "+t.bumpMapUv:"",t.normalMapUv?"#define NORMALMAP_UV "+t.normalMapUv:"",t.displacementMapUv?"#define DISPLACEMENTMAP_UV "+t.displacementMapUv:"",t.metalnessMapUv?"#define METALNESSMAP_UV "+t.metalnessMapUv:"",t.roughnessMapUv?"#define ROUGHNESSMAP_UV "+t.roughnessMapUv:"",t.anisotropyMapUv?"#define ANISOTROPYMAP_UV "+t.anisotropyMapUv:"",t.clearcoatMapUv?"#define CLEARCOATMAP_UV "+t.clearcoatMapUv:"",t.clearcoatNormalMapUv?"#define CLEARCOAT_NORMALMAP_UV "+t.clearcoatNormalMapUv:"",t.clearcoatRoughnessMapUv?"#define CLEARCOAT_ROUGHNESSMAP_UV "+t.clearcoatRoughnessMapUv:"",t.iridescenceMapUv?"#define IRIDESCENCEMAP_UV "+t.iridescenceMapUv:"",t.iridescenceThicknessMapUv?"#define IRIDESCENCE_THICKNESSMAP_UV "+t.iridescenceThicknessMapUv:"",t.sheenColorMapUv?"#define SHEEN_COLORMAP_UV "+t.sheenColorMapUv:"",t.sheenRoughnessMapUv?"#define SHEEN_ROUGHNESSMAP_UV "+t.sheenRoughnessMapUv:"",t.specularMapUv?"#define SPECULARMAP_UV "+t.specularMapUv:"",t.specularColorMapUv?"#define SPECULAR_COLORMAP_UV "+t.specularColorMapUv:"",t.specularIntensityMapUv?"#define SPECULAR_INTENSITYMAP_UV "+t.specularIntensityMapUv:"",t.transmissionMapUv?"#define TRANSMISSIONMAP_UV "+t.transmissionMapUv:"",t.thicknessMapUv?"#define THICKNESSMAP_UV "+t.thicknessMapUv:"",t.vertexTangents&&t.flatShading===!1?"#define USE_TANGENT":"",t.vertexColors?"#define USE_COLOR":"",t.vertexAlphas?"#define USE_COLOR_ALPHA":"",t.vertexUv1s?"#define USE_UV1":"",t.vertexUv2s?"#define USE_UV2":"",t.vertexUv3s?"#define USE_UV3":"",t.pointsUvs?"#define USE_POINTS_UV":"",t.flatShading?"#define FLAT_SHADED":"",t.skinning?"#define USE_SKINNING":"",t.morphTargets?"#define USE_MORPHTARGETS":"",t.morphNormals&&t.flatShading===!1?"#define USE_MORPHNORMALS":"",t.morphColors?"#define USE_MORPHCOLORS":"",t.morphTargetsCount>0?"#define MORPHTARGETS_TEXTURE_STRIDE "+t.morphTextureStride:"",t.morphTargetsCount>0?"#define MORPHTARGETS_COUNT "+t.morphTargetsCount:"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+l:"",t.sizeAttenuation?"#define USE_SIZEATTENUATION":"",t.numLightProbes>0?"#define USE_LIGHT_PROBES":"",t.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"","uniform mat4 modelMatrix;","uniform mat4 modelViewMatrix;","uniform mat4 projectionMatrix;","uniform mat4 viewMatrix;","uniform mat3 normalMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;","#ifdef USE_INSTANCING","	attribute mat4 instanceMatrix;","#endif","#ifdef USE_INSTANCING_COLOR","	attribute vec3 instanceColor;","#endif","#ifdef USE_INSTANCING_MORPH","	uniform sampler2D morphTexture;","#endif","attribute vec3 position;","attribute vec3 normal;","attribute vec2 uv;","#ifdef USE_UV1","	attribute vec2 uv1;","#endif","#ifdef USE_UV2","	attribute vec2 uv2;","#endif","#ifdef USE_UV3","	attribute vec2 uv3;","#endif","#ifdef USE_TANGENT","	attribute vec4 tangent;","#endif","#if defined( USE_COLOR_ALPHA )","	attribute vec4 color;","#elif defined( USE_COLOR )","	attribute vec3 color;","#endif","#ifdef USE_SKINNING","	attribute vec4 skinIndex;","	attribute vec4 skinWeight;","#endif",`
`].filter(ba).join(`
`),p=[rd(t),"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,v,t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.alphaToCoverage?"#define ALPHA_TO_COVERAGE":"",t.map?"#define USE_MAP":"",t.matcap?"#define USE_MATCAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+c:"",t.envMap?"#define "+u:"",t.envMap?"#define "+h:"",d?"#define CUBEUV_TEXEL_WIDTH "+d.texelWidth:"",d?"#define CUBEUV_TEXEL_HEIGHT "+d.texelHeight:"",d?"#define CUBEUV_MAX_MIP "+d.maxMip+".0":"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",t.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.anisotropy?"#define USE_ANISOTROPY":"",t.anisotropyMap?"#define USE_ANISOTROPYMAP":"",t.clearcoat?"#define USE_CLEARCOAT":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.dispersion?"#define USE_DISPERSION":"",t.iridescence?"#define USE_IRIDESCENCE":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",t.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaTest?"#define USE_ALPHATEST":"",t.alphaHash?"#define USE_ALPHAHASH":"",t.sheen?"#define USE_SHEEN":"",t.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.vertexTangents&&t.flatShading===!1?"#define USE_TANGENT":"",t.vertexColors||t.instancingColor||t.batchingColor?"#define USE_COLOR":"",t.vertexAlphas?"#define USE_COLOR_ALPHA":"",t.vertexUv1s?"#define USE_UV1":"",t.vertexUv2s?"#define USE_UV2":"",t.vertexUv3s?"#define USE_UV3":"",t.pointsUvs?"#define USE_POINTS_UV":"",t.gradientMap?"#define USE_GRADIENTMAP":"",t.flatShading?"#define FLAT_SHADED":"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+l:"",t.premultipliedAlpha?"#define PREMULTIPLIED_ALPHA":"",t.numLightProbes>0?"#define USE_LIGHT_PROBES":"",t.decodeVideoTexture?"#define DECODE_VIDEO_TEXTURE":"",t.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"","uniform mat4 viewMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;",t.toneMapping!==cs?"#define TONE_MAPPING":"",t.toneMapping!==cs?rt.tonemapping_pars_fragment:"",t.toneMapping!==cs?Yx("toneMapping",t.toneMapping):"",t.dithering?"#define DITHERING":"",t.opaque?"#define OPAQUE":"",rt.colorspace_pars_fragment,$x("linearToOutputTexel",t.outputColorSpace),jx(),t.useDepthPacking?"#define DEPTH_PACKING "+t.depthPacking:"",`
`].filter(ba).join(`
`)),o=Jc(o),o=nd(o,t),o=id(o,t),a=Jc(a),a=nd(a,t),a=id(a,t),o=sd(o),a=sd(a),t.isRawShaderMaterial!==!0&&(x=`#version 300 es
`,m=[f,"#define attribute in","#define varying out","#define texture2D texture"].join(`
`)+`
`+m,p=["#define varying in",t.glslVersion===xh?"":"layout(location = 0) out highp vec4 pc_fragColor;",t.glslVersion===xh?"":"#define gl_FragColor pc_fragColor","#define gl_FragDepthEXT gl_FragDepth","#define texture2D texture","#define textureCube texture","#define texture2DProj textureProj","#define texture2DLodEXT textureLod","#define texture2DProjLodEXT textureProjLod","#define textureCubeLodEXT textureLod","#define texture2DGradEXT textureGrad","#define texture2DProjGradEXT textureProjGrad","#define textureCubeGradEXT textureGrad"].join(`
`)+`
`+p);const b=x+m+o,w=x+p+a,O=ed(s,s.VERTEX_SHADER,b),A=ed(s,s.FRAGMENT_SHADER,w);s.attachShader(g,O),s.attachShader(g,A),t.index0AttributeName!==void 0?s.bindAttribLocation(g,0,t.index0AttributeName):t.morphTargets===!0&&s.bindAttribLocation(g,0,"position"),s.linkProgram(g);function L(P){if(i.debug.checkShaderErrors){const K=s.getProgramInfoLog(g).trim(),z=s.getShaderInfoLog(O).trim(),Z=s.getShaderInfoLog(A).trim();let q=!0,Q=!0;if(s.getProgramParameter(g,s.LINK_STATUS)===!1)if(q=!1,typeof i.debug.onShaderError=="function")i.debug.onShaderError(s,g,O,A);else{const $=td(s,O,"vertex"),te=td(s,A,"fragment");console.error("THREE.WebGLProgram: Shader Error "+s.getError()+" - VALIDATE_STATUS "+s.getProgramParameter(g,s.VALIDATE_STATUS)+`

Material Name: `+P.name+`
Material Type: `+P.type+`

Program Info Log: `+K+`
`+$+`
`+te)}else K!==""?console.warn("THREE.WebGLProgram: Program Info Log:",K):(z===""||Z==="")&&(Q=!1);Q&&(P.diagnostics={runnable:q,programLog:K,vertexShader:{log:z,prefix:m},fragmentShader:{log:Z,prefix:p}})}s.deleteShader(O),s.deleteShader(A),k=new Oo(s,g),E=Jx(s,g)}let k;this.getUniforms=function(){return k===void 0&&L(this),k};let E;this.getAttributes=function(){return E===void 0&&L(this),E};let y=t.rendererExtensionParallelShaderCompile===!1;return this.isReady=function(){return y===!1&&(y=s.getProgramParameter(g,Gx)),y},this.destroy=function(){n.releaseStatesOfProgram(this),s.deleteProgram(g),this.program=void 0},this.type=t.shaderType,this.name=t.shaderName,this.id=Wx++,this.cacheKey=e,this.usedTimes=1,this.program=g,this.vertexShader=O,this.fragmentShader=A,this}let uy=0;class hy{constructor(){this.shaderCache=new Map,this.materialCache=new Map}update(e){const t=e.vertexShader,n=e.fragmentShader,s=this._getShaderStage(t),r=this._getShaderStage(n),o=this._getShaderCacheForMaterial(e);return o.has(s)===!1&&(o.add(s),s.usedTimes++),o.has(r)===!1&&(o.add(r),r.usedTimes++),this}remove(e){const t=this.materialCache.get(e);for(const n of t)n.usedTimes--,n.usedTimes===0&&this.shaderCache.delete(n.code);return this.materialCache.delete(e),this}getVertexShaderID(e){return this._getShaderStage(e.vertexShader).id}getFragmentShaderID(e){return this._getShaderStage(e.fragmentShader).id}dispose(){this.shaderCache.clear(),this.materialCache.clear()}_getShaderCacheForMaterial(e){const t=this.materialCache;let n=t.get(e);return n===void 0&&(n=new Set,t.set(e,n)),n}_getShaderStage(e){const t=this.shaderCache;let n=t.get(e);return n===void 0&&(n=new dy(e),t.set(e,n)),n}}class dy{constructor(e){this.id=uy++,this.code=e,this.usedTimes=0}}function fy(i,e,t,n,s,r,o){const a=new wu,l=new hy,c=new Set,u=[],h=s.logarithmicDepthBuffer,d=s.vertexTextures;let f=s.precision;const v={MeshDepthMaterial:"depth",MeshDistanceMaterial:"distanceRGBA",MeshNormalMaterial:"normal",MeshBasicMaterial:"basic",MeshLambertMaterial:"lambert",MeshPhongMaterial:"phong",MeshToonMaterial:"toon",MeshStandardMaterial:"physical",MeshPhysicalMaterial:"physical",MeshMatcapMaterial:"matcap",LineBasicMaterial:"basic",LineDashedMaterial:"dashed",PointsMaterial:"points",ShadowMaterial:"shadow",SpriteMaterial:"sprite"};function g(E){return c.add(E),E===0?"uv":`uv${E}`}function m(E,y,P,K,z){const Z=K.fog,q=z.geometry,Q=E.isMeshStandardMaterial?K.environment:null,$=(E.isMeshStandardMaterial?t:e).get(E.envMap||Q),te=$&&$.mapping===nl?$.image.height:null,ge=v[E.type];E.precision!==null&&(f=s.getMaxPrecision(E.precision),f!==E.precision&&console.warn("THREE.WebGLProgram.getParameters:",E.precision,"not supported, using",f,"instead."));const de=q.morphAttributes.position||q.morphAttributes.normal||q.morphAttributes.color,xe=de!==void 0?de.length:0;let Ee=0;q.morphAttributes.position!==void 0&&(Ee=1),q.morphAttributes.normal!==void 0&&(Ee=2),q.morphAttributes.color!==void 0&&(Ee=3);let ye,ne,ce,be;if(ge){const lt=wi[ge];ye=lt.vertexShader,ne=lt.fragmentShader}else ye=E.vertexShader,ne=E.fragmentShader,l.update(E),ce=l.getVertexShaderID(E),be=l.getFragmentShaderID(E);const fe=i.getRenderTarget(),ke=z.isInstancedMesh===!0,Ve=z.isBatchedMesh===!0,Ne=!!E.map,pt=!!E.matcap,N=!!$,dt=!!E.aoMap,it=!!E.lightMap,ct=!!E.bumpMap,Oe=!!E.normalMap,Et=!!E.displacementMap,Xe=!!E.emissiveMap,We=!!E.metalnessMap,I=!!E.roughnessMap,M=E.anisotropy>0,J=E.clearcoat>0,oe=E.dispersion>0,ee=E.iridescence>0,W=E.sheen>0,we=E.transmission>0,ve=M&&!!E.anisotropyMap,Ae=J&&!!E.clearcoatMap,Ke=J&&!!E.clearcoatNormalMap,me=J&&!!E.clearcoatRoughnessMap,Te=ee&&!!E.iridescenceMap,Ze=ee&&!!E.iridescenceThicknessMap,Be=W&&!!E.sheenColorMap,Me=W&&!!E.sheenRoughnessMap,ze=!!E.specularMap,F=!!E.specularColorMap,le=!!E.specularIntensityMap,U=we&&!!E.transmissionMap,re=we&&!!E.thicknessMap,ie=!!E.gradientMap,se=!!E.alphaMap,_e=E.alphaTest>0,je=!!E.alphaHash,ot=!!E.extensions;let vt=cs;E.toneMapped&&(fe===null||fe.isXRRenderTarget===!0)&&(vt=i.toneMapping);const Tt={shaderID:ge,shaderType:E.type,shaderName:E.name,vertexShader:ye,fragmentShader:ne,defines:E.defines,customVertexShaderID:ce,customFragmentShaderID:be,isRawShaderMaterial:E.isRawShaderMaterial===!0,glslVersion:E.glslVersion,precision:f,batching:Ve,batchingColor:Ve&&z._colorsTexture!==null,instancing:ke,instancingColor:ke&&z.instanceColor!==null,instancingMorph:ke&&z.morphTexture!==null,supportsVertexTextures:d,outputColorSpace:fe===null?i.outputColorSpace:fe.isXRRenderTarget===!0?fe.texture.colorSpace:gs,alphaToCoverage:!!E.alphaToCoverage,map:Ne,matcap:pt,envMap:N,envMapMode:N&&$.mapping,envMapCubeUVHeight:te,aoMap:dt,lightMap:it,bumpMap:ct,normalMap:Oe,displacementMap:d&&Et,emissiveMap:Xe,normalMapObjectSpace:Oe&&E.normalMapType===ag,normalMapTangentSpace:Oe&&E.normalMapType===Of,metalnessMap:We,roughnessMap:I,anisotropy:M,anisotropyMap:ve,clearcoat:J,clearcoatMap:Ae,clearcoatNormalMap:Ke,clearcoatRoughnessMap:me,dispersion:oe,iridescence:ee,iridescenceMap:Te,iridescenceThicknessMap:Ze,sheen:W,sheenColorMap:Be,sheenRoughnessMap:Me,specularMap:ze,specularColorMap:F,specularIntensityMap:le,transmission:we,transmissionMap:U,thicknessMap:re,gradientMap:ie,opaque:E.transparent===!1&&E.blending===Ur&&E.alphaToCoverage===!1,alphaMap:se,alphaTest:_e,alphaHash:je,combine:E.combine,mapUv:Ne&&g(E.map.channel),aoMapUv:dt&&g(E.aoMap.channel),lightMapUv:it&&g(E.lightMap.channel),bumpMapUv:ct&&g(E.bumpMap.channel),normalMapUv:Oe&&g(E.normalMap.channel),displacementMapUv:Et&&g(E.displacementMap.channel),emissiveMapUv:Xe&&g(E.emissiveMap.channel),metalnessMapUv:We&&g(E.metalnessMap.channel),roughnessMapUv:I&&g(E.roughnessMap.channel),anisotropyMapUv:ve&&g(E.anisotropyMap.channel),clearcoatMapUv:Ae&&g(E.clearcoatMap.channel),clearcoatNormalMapUv:Ke&&g(E.clearcoatNormalMap.channel),clearcoatRoughnessMapUv:me&&g(E.clearcoatRoughnessMap.channel),iridescenceMapUv:Te&&g(E.iridescenceMap.channel),iridescenceThicknessMapUv:Ze&&g(E.iridescenceThicknessMap.channel),sheenColorMapUv:Be&&g(E.sheenColorMap.channel),sheenRoughnessMapUv:Me&&g(E.sheenRoughnessMap.channel),specularMapUv:ze&&g(E.specularMap.channel),specularColorMapUv:F&&g(E.specularColorMap.channel),specularIntensityMapUv:le&&g(E.specularIntensityMap.channel),transmissionMapUv:U&&g(E.transmissionMap.channel),thicknessMapUv:re&&g(E.thicknessMap.channel),alphaMapUv:se&&g(E.alphaMap.channel),vertexTangents:!!q.attributes.tangent&&(Oe||M),vertexColors:E.vertexColors,vertexAlphas:E.vertexColors===!0&&!!q.attributes.color&&q.attributes.color.itemSize===4,pointsUvs:z.isPoints===!0&&!!q.attributes.uv&&(Ne||se),fog:!!Z,useFog:E.fog===!0,fogExp2:!!Z&&Z.isFogExp2,flatShading:E.flatShading===!0,sizeAttenuation:E.sizeAttenuation===!0,logarithmicDepthBuffer:h,skinning:z.isSkinnedMesh===!0,morphTargets:q.morphAttributes.position!==void 0,morphNormals:q.morphAttributes.normal!==void 0,morphColors:q.morphAttributes.color!==void 0,morphTargetsCount:xe,morphTextureStride:Ee,numDirLights:y.directional.length,numPointLights:y.point.length,numSpotLights:y.spot.length,numSpotLightMaps:y.spotLightMap.length,numRectAreaLights:y.rectArea.length,numHemiLights:y.hemi.length,numDirLightShadows:y.directionalShadowMap.length,numPointLightShadows:y.pointShadowMap.length,numSpotLightShadows:y.spotShadowMap.length,numSpotLightShadowsWithMaps:y.numSpotLightShadowsWithMaps,numLightProbes:y.numLightProbes,numClippingPlanes:o.numPlanes,numClipIntersection:o.numIntersection,dithering:E.dithering,shadowMapEnabled:i.shadowMap.enabled&&P.length>0,shadowMapType:i.shadowMap.type,toneMapping:vt,decodeVideoTexture:Ne&&E.map.isVideoTexture===!0&&wt.getTransfer(E.map.colorSpace)===Bt,premultipliedAlpha:E.premultipliedAlpha,doubleSided:E.side===Ei,flipSided:E.side===Nn,useDepthPacking:E.depthPacking>=0,depthPacking:E.depthPacking||0,index0AttributeName:E.index0AttributeName,extensionClipCullDistance:ot&&E.extensions.clipCullDistance===!0&&n.has("WEBGL_clip_cull_distance"),extensionMultiDraw:(ot&&E.extensions.multiDraw===!0||Ve)&&n.has("WEBGL_multi_draw"),rendererExtensionParallelShaderCompile:n.has("KHR_parallel_shader_compile"),customProgramCacheKey:E.customProgramCacheKey()};return Tt.vertexUv1s=c.has(1),Tt.vertexUv2s=c.has(2),Tt.vertexUv3s=c.has(3),c.clear(),Tt}function p(E){const y=[];if(E.shaderID?y.push(E.shaderID):(y.push(E.customVertexShaderID),y.push(E.customFragmentShaderID)),E.defines!==void 0)for(const P in E.defines)y.push(P),y.push(E.defines[P]);return E.isRawShaderMaterial===!1&&(x(y,E),b(y,E),y.push(i.outputColorSpace)),y.push(E.customProgramCacheKey),y.join()}function x(E,y){E.push(y.precision),E.push(y.outputColorSpace),E.push(y.envMapMode),E.push(y.envMapCubeUVHeight),E.push(y.mapUv),E.push(y.alphaMapUv),E.push(y.lightMapUv),E.push(y.aoMapUv),E.push(y.bumpMapUv),E.push(y.normalMapUv),E.push(y.displacementMapUv),E.push(y.emissiveMapUv),E.push(y.metalnessMapUv),E.push(y.roughnessMapUv),E.push(y.anisotropyMapUv),E.push(y.clearcoatMapUv),E.push(y.clearcoatNormalMapUv),E.push(y.clearcoatRoughnessMapUv),E.push(y.iridescenceMapUv),E.push(y.iridescenceThicknessMapUv),E.push(y.sheenColorMapUv),E.push(y.sheenRoughnessMapUv),E.push(y.specularMapUv),E.push(y.specularColorMapUv),E.push(y.specularIntensityMapUv),E.push(y.transmissionMapUv),E.push(y.thicknessMapUv),E.push(y.combine),E.push(y.fogExp2),E.push(y.sizeAttenuation),E.push(y.morphTargetsCount),E.push(y.morphAttributeCount),E.push(y.numDirLights),E.push(y.numPointLights),E.push(y.numSpotLights),E.push(y.numSpotLightMaps),E.push(y.numHemiLights),E.push(y.numRectAreaLights),E.push(y.numDirLightShadows),E.push(y.numPointLightShadows),E.push(y.numSpotLightShadows),E.push(y.numSpotLightShadowsWithMaps),E.push(y.numLightProbes),E.push(y.shadowMapType),E.push(y.toneMapping),E.push(y.numClippingPlanes),E.push(y.numClipIntersection),E.push(y.depthPacking)}function b(E,y){a.disableAll(),y.supportsVertexTextures&&a.enable(0),y.instancing&&a.enable(1),y.instancingColor&&a.enable(2),y.instancingMorph&&a.enable(3),y.matcap&&a.enable(4),y.envMap&&a.enable(5),y.normalMapObjectSpace&&a.enable(6),y.normalMapTangentSpace&&a.enable(7),y.clearcoat&&a.enable(8),y.iridescence&&a.enable(9),y.alphaTest&&a.enable(10),y.vertexColors&&a.enable(11),y.vertexAlphas&&a.enable(12),y.vertexUv1s&&a.enable(13),y.vertexUv2s&&a.enable(14),y.vertexUv3s&&a.enable(15),y.vertexTangents&&a.enable(16),y.anisotropy&&a.enable(17),y.alphaHash&&a.enable(18),y.batching&&a.enable(19),y.dispersion&&a.enable(20),y.batchingColor&&a.enable(21),E.push(a.mask),a.disableAll(),y.fog&&a.enable(0),y.useFog&&a.enable(1),y.flatShading&&a.enable(2),y.logarithmicDepthBuffer&&a.enable(3),y.skinning&&a.enable(4),y.morphTargets&&a.enable(5),y.morphNormals&&a.enable(6),y.morphColors&&a.enable(7),y.premultipliedAlpha&&a.enable(8),y.shadowMapEnabled&&a.enable(9),y.doubleSided&&a.enable(10),y.flipSided&&a.enable(11),y.useDepthPacking&&a.enable(12),y.dithering&&a.enable(13),y.transmission&&a.enable(14),y.sheen&&a.enable(15),y.opaque&&a.enable(16),y.pointsUvs&&a.enable(17),y.decodeVideoTexture&&a.enable(18),y.alphaToCoverage&&a.enable(19),E.push(a.mask)}function w(E){const y=v[E.type];let P;if(y){const K=wi[y];P=Kg.clone(K.uniforms)}else P=E.uniforms;return P}function O(E,y){let P;for(let K=0,z=u.length;K<z;K++){const Z=u[K];if(Z.cacheKey===y){P=Z,++P.usedTimes;break}}return P===void 0&&(P=new cy(i,y,E,r),u.push(P)),P}function A(E){if(--E.usedTimes===0){const y=u.indexOf(E);u[y]=u[u.length-1],u.pop(),E.destroy()}}function L(E){l.remove(E)}function k(){l.dispose()}return{getParameters:m,getProgramCacheKey:p,getUniforms:w,acquireProgram:O,releaseProgram:A,releaseShaderCache:L,programs:u,dispose:k}}function py(){let i=new WeakMap;function e(o){return i.has(o)}function t(o){let a=i.get(o);return a===void 0&&(a={},i.set(o,a)),a}function n(o){i.delete(o)}function s(o,a,l){i.get(o)[a]=l}function r(){i=new WeakMap}return{has:e,get:t,remove:n,update:s,dispose:r}}function my(i,e){return i.groupOrder!==e.groupOrder?i.groupOrder-e.groupOrder:i.renderOrder!==e.renderOrder?i.renderOrder-e.renderOrder:i.material.id!==e.material.id?i.material.id-e.material.id:i.z!==e.z?i.z-e.z:i.id-e.id}function ad(i,e){return i.groupOrder!==e.groupOrder?i.groupOrder-e.groupOrder:i.renderOrder!==e.renderOrder?i.renderOrder-e.renderOrder:i.z!==e.z?e.z-i.z:i.id-e.id}function od(){const i=[];let e=0;const t=[],n=[],s=[];function r(){e=0,t.length=0,n.length=0,s.length=0}function o(h,d,f,v,g,m){let p=i[e];return p===void 0?(p={id:h.id,object:h,geometry:d,material:f,groupOrder:v,renderOrder:h.renderOrder,z:g,group:m},i[e]=p):(p.id=h.id,p.object=h,p.geometry=d,p.material=f,p.groupOrder=v,p.renderOrder=h.renderOrder,p.z=g,p.group=m),e++,p}function a(h,d,f,v,g,m){const p=o(h,d,f,v,g,m);f.transmission>0?n.push(p):f.transparent===!0?s.push(p):t.push(p)}function l(h,d,f,v,g,m){const p=o(h,d,f,v,g,m);f.transmission>0?n.unshift(p):f.transparent===!0?s.unshift(p):t.unshift(p)}function c(h,d){t.length>1&&t.sort(h||my),n.length>1&&n.sort(d||ad),s.length>1&&s.sort(d||ad)}function u(){for(let h=e,d=i.length;h<d;h++){const f=i[h];if(f.id===null)break;f.id=null,f.object=null,f.geometry=null,f.material=null,f.group=null}}return{opaque:t,transmissive:n,transparent:s,init:r,push:a,unshift:l,finish:u,sort:c}}function gy(){let i=new WeakMap;function e(n,s){const r=i.get(n);let o;return r===void 0?(o=new od,i.set(n,[o])):s>=r.length?(o=new od,r.push(o)):o=r[s],o}function t(){i=new WeakMap}return{get:e,dispose:t}}function vy(){const i={};return{get:function(e){if(i[e.id]!==void 0)return i[e.id];let t;switch(e.type){case"DirectionalLight":t={direction:new G,color:new st};break;case"SpotLight":t={position:new G,direction:new G,color:new st,distance:0,coneCos:0,penumbraCos:0,decay:0};break;case"PointLight":t={position:new G,color:new st,distance:0,decay:0};break;case"HemisphereLight":t={direction:new G,skyColor:new st,groundColor:new st};break;case"RectAreaLight":t={color:new st,position:new G,halfWidth:new G,halfHeight:new G};break}return i[e.id]=t,t}}}function _y(){const i={};return{get:function(e){if(i[e.id]!==void 0)return i[e.id];let t;switch(e.type){case"DirectionalLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new qe};break;case"SpotLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new qe};break;case"PointLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new qe,shadowCameraNear:1,shadowCameraFar:1e3};break}return i[e.id]=t,t}}}let xy=0;function yy(i,e){return(e.castShadow?2:0)-(i.castShadow?2:0)+(e.map?1:0)-(i.map?1:0)}function by(i){const e=new vy,t=_y(),n={version:0,hash:{directionalLength:-1,pointLength:-1,spotLength:-1,rectAreaLength:-1,hemiLength:-1,numDirectionalShadows:-1,numPointShadows:-1,numSpotShadows:-1,numSpotMaps:-1,numLightProbes:-1},ambient:[0,0,0],probe:[],directional:[],directionalShadow:[],directionalShadowMap:[],directionalShadowMatrix:[],spot:[],spotLightMap:[],spotShadow:[],spotShadowMap:[],spotLightMatrix:[],rectArea:[],rectAreaLTC1:null,rectAreaLTC2:null,point:[],pointShadow:[],pointShadowMap:[],pointShadowMatrix:[],hemi:[],numSpotLightShadowsWithMaps:0,numLightProbes:0};for(let c=0;c<9;c++)n.probe.push(new G);const s=new G,r=new Gt,o=new Gt;function a(c){let u=0,h=0,d=0;for(let E=0;E<9;E++)n.probe[E].set(0,0,0);let f=0,v=0,g=0,m=0,p=0,x=0,b=0,w=0,O=0,A=0,L=0;c.sort(yy);for(let E=0,y=c.length;E<y;E++){const P=c[E],K=P.color,z=P.intensity,Z=P.distance,q=P.shadow&&P.shadow.map?P.shadow.map.texture:null;if(P.isAmbientLight)u+=K.r*z,h+=K.g*z,d+=K.b*z;else if(P.isLightProbe){for(let Q=0;Q<9;Q++)n.probe[Q].addScaledVector(P.sh.coefficients[Q],z);L++}else if(P.isDirectionalLight){const Q=e.get(P);if(Q.color.copy(P.color).multiplyScalar(P.intensity),P.castShadow){const $=P.shadow,te=t.get(P);te.shadowIntensity=$.intensity,te.shadowBias=$.bias,te.shadowNormalBias=$.normalBias,te.shadowRadius=$.radius,te.shadowMapSize=$.mapSize,n.directionalShadow[f]=te,n.directionalShadowMap[f]=q,n.directionalShadowMatrix[f]=P.shadow.matrix,x++}n.directional[f]=Q,f++}else if(P.isSpotLight){const Q=e.get(P);Q.position.setFromMatrixPosition(P.matrixWorld),Q.color.copy(K).multiplyScalar(z),Q.distance=Z,Q.coneCos=Math.cos(P.angle),Q.penumbraCos=Math.cos(P.angle*(1-P.penumbra)),Q.decay=P.decay,n.spot[g]=Q;const $=P.shadow;if(P.map&&(n.spotLightMap[O]=P.map,O++,$.updateMatrices(P),P.castShadow&&A++),n.spotLightMatrix[g]=$.matrix,P.castShadow){const te=t.get(P);te.shadowIntensity=$.intensity,te.shadowBias=$.bias,te.shadowNormalBias=$.normalBias,te.shadowRadius=$.radius,te.shadowMapSize=$.mapSize,n.spotShadow[g]=te,n.spotShadowMap[g]=q,w++}g++}else if(P.isRectAreaLight){const Q=e.get(P);Q.color.copy(K).multiplyScalar(z),Q.halfWidth.set(P.width*.5,0,0),Q.halfHeight.set(0,P.height*.5,0),n.rectArea[m]=Q,m++}else if(P.isPointLight){const Q=e.get(P);if(Q.color.copy(P.color).multiplyScalar(P.intensity),Q.distance=P.distance,Q.decay=P.decay,P.castShadow){const $=P.shadow,te=t.get(P);te.shadowIntensity=$.intensity,te.shadowBias=$.bias,te.shadowNormalBias=$.normalBias,te.shadowRadius=$.radius,te.shadowMapSize=$.mapSize,te.shadowCameraNear=$.camera.near,te.shadowCameraFar=$.camera.far,n.pointShadow[v]=te,n.pointShadowMap[v]=q,n.pointShadowMatrix[v]=P.shadow.matrix,b++}n.point[v]=Q,v++}else if(P.isHemisphereLight){const Q=e.get(P);Q.skyColor.copy(P.color).multiplyScalar(z),Q.groundColor.copy(P.groundColor).multiplyScalar(z),n.hemi[p]=Q,p++}}m>0&&(i.has("OES_texture_float_linear")===!0?(n.rectAreaLTC1=Ce.LTC_FLOAT_1,n.rectAreaLTC2=Ce.LTC_FLOAT_2):(n.rectAreaLTC1=Ce.LTC_HALF_1,n.rectAreaLTC2=Ce.LTC_HALF_2)),n.ambient[0]=u,n.ambient[1]=h,n.ambient[2]=d;const k=n.hash;(k.directionalLength!==f||k.pointLength!==v||k.spotLength!==g||k.rectAreaLength!==m||k.hemiLength!==p||k.numDirectionalShadows!==x||k.numPointShadows!==b||k.numSpotShadows!==w||k.numSpotMaps!==O||k.numLightProbes!==L)&&(n.directional.length=f,n.spot.length=g,n.rectArea.length=m,n.point.length=v,n.hemi.length=p,n.directionalShadow.length=x,n.directionalShadowMap.length=x,n.pointShadow.length=b,n.pointShadowMap.length=b,n.spotShadow.length=w,n.spotShadowMap.length=w,n.directionalShadowMatrix.length=x,n.pointShadowMatrix.length=b,n.spotLightMatrix.length=w+O-A,n.spotLightMap.length=O,n.numSpotLightShadowsWithMaps=A,n.numLightProbes=L,k.directionalLength=f,k.pointLength=v,k.spotLength=g,k.rectAreaLength=m,k.hemiLength=p,k.numDirectionalShadows=x,k.numPointShadows=b,k.numSpotShadows=w,k.numSpotMaps=O,k.numLightProbes=L,n.version=xy++)}function l(c,u){let h=0,d=0,f=0,v=0,g=0;const m=u.matrixWorldInverse;for(let p=0,x=c.length;p<x;p++){const b=c[p];if(b.isDirectionalLight){const w=n.directional[h];w.direction.setFromMatrixPosition(b.matrixWorld),s.setFromMatrixPosition(b.target.matrixWorld),w.direction.sub(s),w.direction.transformDirection(m),h++}else if(b.isSpotLight){const w=n.spot[f];w.position.setFromMatrixPosition(b.matrixWorld),w.position.applyMatrix4(m),w.direction.setFromMatrixPosition(b.matrixWorld),s.setFromMatrixPosition(b.target.matrixWorld),w.direction.sub(s),w.direction.transformDirection(m),f++}else if(b.isRectAreaLight){const w=n.rectArea[v];w.position.setFromMatrixPosition(b.matrixWorld),w.position.applyMatrix4(m),o.identity(),r.copy(b.matrixWorld),r.premultiply(m),o.extractRotation(r),w.halfWidth.set(b.width*.5,0,0),w.halfHeight.set(0,b.height*.5,0),w.halfWidth.applyMatrix4(o),w.halfHeight.applyMatrix4(o),v++}else if(b.isPointLight){const w=n.point[d];w.position.setFromMatrixPosition(b.matrixWorld),w.position.applyMatrix4(m),d++}else if(b.isHemisphereLight){const w=n.hemi[g];w.direction.setFromMatrixPosition(b.matrixWorld),w.direction.transformDirection(m),g++}}}return{setup:a,setupView:l,state:n}}function ld(i){const e=new by(i),t=[],n=[];function s(u){c.camera=u,t.length=0,n.length=0}function r(u){t.push(u)}function o(u){n.push(u)}function a(){e.setup(t)}function l(u){e.setupView(t,u)}const c={lightsArray:t,shadowsArray:n,camera:null,lights:e,transmissionRenderTarget:{}};return{init:s,state:c,setupLights:a,setupLightsView:l,pushLight:r,pushShadow:o}}function Sy(i){let e=new WeakMap;function t(s,r=0){const o=e.get(s);let a;return o===void 0?(a=new ld(i),e.set(s,[a])):r>=o.length?(a=new ld(i),o.push(a)):a=o[r],a}function n(){e=new WeakMap}return{get:t,dispose:n}}class My extends Ys{constructor(e){super(),this.isMeshDepthMaterial=!0,this.type="MeshDepthMaterial",this.depthPacking=sg,this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.wireframe=!1,this.wireframeLinewidth=1,this.setValues(e)}copy(e){return super.copy(e),this.depthPacking=e.depthPacking,this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this}}class wy extends Ys{constructor(e){super(),this.isMeshDistanceMaterial=!0,this.type="MeshDistanceMaterial",this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.setValues(e)}copy(e){return super.copy(e),this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this}}const Ey=`void main() {
	gl_Position = vec4( position, 1.0 );
}`,Ty=`uniform sampler2D shadow_pass;
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
}`;function Ay(i,e,t){let n=new Eu;const s=new qe,r=new qe,o=new en,a=new My({depthPacking:rg}),l=new wy,c={},u=t.maxTextureSize,h={[hs]:Nn,[Nn]:hs,[Ei]:Ei},d=new ds({defines:{VSM_SAMPLES:8},uniforms:{shadow_pass:{value:null},resolution:{value:new qe},radius:{value:4}},vertexShader:Ey,fragmentShader:Ty}),f=d.clone();f.defines.HORIZONTAL_PASS=1;const v=new Xn;v.setAttribute("position",new pi(new Float32Array([-1,-1,.5,3,-1,.5,-1,3,.5]),3));const g=new Pn(v,d),m=this;this.enabled=!1,this.autoUpdate=!0,this.needsUpdate=!1,this.type=bf;let p=this.type;this.render=function(A,L,k){if(m.enabled===!1||m.autoUpdate===!1&&m.needsUpdate===!1||A.length===0)return;const E=i.getRenderTarget(),y=i.getActiveCubeFace(),P=i.getActiveMipmapLevel(),K=i.state;K.setBlending(ls),K.buffers.color.setClear(1,1,1,1),K.buffers.depth.setTest(!0),K.setScissorTest(!1);const z=p!==Bi&&this.type===Bi,Z=p===Bi&&this.type!==Bi;for(let q=0,Q=A.length;q<Q;q++){const $=A[q],te=$.shadow;if(te===void 0){console.warn("THREE.WebGLShadowMap:",$,"has no shadow.");continue}if(te.autoUpdate===!1&&te.needsUpdate===!1)continue;s.copy(te.mapSize);const ge=te.getFrameExtents();if(s.multiply(ge),r.copy(te.mapSize),(s.x>u||s.y>u)&&(s.x>u&&(r.x=Math.floor(u/ge.x),s.x=r.x*ge.x,te.mapSize.x=r.x),s.y>u&&(r.y=Math.floor(u/ge.y),s.y=r.y*ge.y,te.mapSize.y=r.y)),te.map===null||z===!0||Z===!0){const xe=this.type!==Bi?{minFilter:ei,magFilter:ei}:{};te.map!==null&&te.map.dispose(),te.map=new Gs(s.x,s.y,xe),te.map.texture.name=$.name+".shadowMap",te.camera.updateProjectionMatrix()}i.setRenderTarget(te.map),i.clear();const de=te.getViewportCount();for(let xe=0;xe<de;xe++){const Ee=te.getViewport(xe);o.set(r.x*Ee.x,r.y*Ee.y,r.x*Ee.z,r.y*Ee.w),K.viewport(o),te.updateMatrices($,xe),n=te.getFrustum(),w(L,k,te.camera,$,this.type)}te.isPointLightShadow!==!0&&this.type===Bi&&x(te,k),te.needsUpdate=!1}p=this.type,m.needsUpdate=!1,i.setRenderTarget(E,y,P)};function x(A,L){const k=e.update(g);d.defines.VSM_SAMPLES!==A.blurSamples&&(d.defines.VSM_SAMPLES=A.blurSamples,f.defines.VSM_SAMPLES=A.blurSamples,d.needsUpdate=!0,f.needsUpdate=!0),A.mapPass===null&&(A.mapPass=new Gs(s.x,s.y)),d.uniforms.shadow_pass.value=A.map.texture,d.uniforms.resolution.value=A.mapSize,d.uniforms.radius.value=A.radius,i.setRenderTarget(A.mapPass),i.clear(),i.renderBufferDirect(L,null,k,d,g,null),f.uniforms.shadow_pass.value=A.mapPass.texture,f.uniforms.resolution.value=A.mapSize,f.uniforms.radius.value=A.radius,i.setRenderTarget(A.map),i.clear(),i.renderBufferDirect(L,null,k,f,g,null)}function b(A,L,k,E){let y=null;const P=k.isPointLight===!0?A.customDistanceMaterial:A.customDepthMaterial;if(P!==void 0)y=P;else if(y=k.isPointLight===!0?l:a,i.localClippingEnabled&&L.clipShadows===!0&&Array.isArray(L.clippingPlanes)&&L.clippingPlanes.length!==0||L.displacementMap&&L.displacementScale!==0||L.alphaMap&&L.alphaTest>0||L.map&&L.alphaTest>0){const K=y.uuid,z=L.uuid;let Z=c[K];Z===void 0&&(Z={},c[K]=Z);let q=Z[z];q===void 0&&(q=y.clone(),Z[z]=q,L.addEventListener("dispose",O)),y=q}if(y.visible=L.visible,y.wireframe=L.wireframe,E===Bi?y.side=L.shadowSide!==null?L.shadowSide:L.side:y.side=L.shadowSide!==null?L.shadowSide:h[L.side],y.alphaMap=L.alphaMap,y.alphaTest=L.alphaTest,y.map=L.map,y.clipShadows=L.clipShadows,y.clippingPlanes=L.clippingPlanes,y.clipIntersection=L.clipIntersection,y.displacementMap=L.displacementMap,y.displacementScale=L.displacementScale,y.displacementBias=L.displacementBias,y.wireframeLinewidth=L.wireframeLinewidth,y.linewidth=L.linewidth,k.isPointLight===!0&&y.isMeshDistanceMaterial===!0){const K=i.properties.get(y);K.light=k}return y}function w(A,L,k,E,y){if(A.visible===!1)return;if(A.layers.test(L.layers)&&(A.isMesh||A.isLine||A.isPoints)&&(A.castShadow||A.receiveShadow&&y===Bi)&&(!A.frustumCulled||n.intersectsObject(A))){A.modelViewMatrix.multiplyMatrices(k.matrixWorldInverse,A.matrixWorld);const z=e.update(A),Z=A.material;if(Array.isArray(Z)){const q=z.groups;for(let Q=0,$=q.length;Q<$;Q++){const te=q[Q],ge=Z[te.materialIndex];if(ge&&ge.visible){const de=b(A,ge,E,y);A.onBeforeShadow(i,A,L,k,z,de,te),i.renderBufferDirect(k,null,z,de,A,te),A.onAfterShadow(i,A,L,k,z,de,te)}}}else if(Z.visible){const q=b(A,Z,E,y);A.onBeforeShadow(i,A,L,k,z,q,null),i.renderBufferDirect(k,null,z,q,A,null),A.onAfterShadow(i,A,L,k,z,q,null)}}const K=A.children;for(let z=0,Z=K.length;z<Z;z++)w(K[z],L,k,E,y)}function O(A){A.target.removeEventListener("dispose",O);for(const k in c){const E=c[k],y=A.target.uuid;y in E&&(E[y].dispose(),delete E[y])}}}function Cy(i){function e(){let U=!1;const re=new en;let ie=null;const se=new en(0,0,0,0);return{setMask:function(_e){ie!==_e&&!U&&(i.colorMask(_e,_e,_e,_e),ie=_e)},setLocked:function(_e){U=_e},setClear:function(_e,je,ot,vt,Tt){Tt===!0&&(_e*=vt,je*=vt,ot*=vt),re.set(_e,je,ot,vt),se.equals(re)===!1&&(i.clearColor(_e,je,ot,vt),se.copy(re))},reset:function(){U=!1,ie=null,se.set(-1,0,0,0)}}}function t(){let U=!1,re=null,ie=null,se=null;return{setTest:function(_e){_e?be(i.DEPTH_TEST):fe(i.DEPTH_TEST)},setMask:function(_e){re!==_e&&!U&&(i.depthMask(_e),re=_e)},setFunc:function(_e){if(ie!==_e){switch(_e){case Vm:i.depthFunc(i.NEVER);break;case Gm:i.depthFunc(i.ALWAYS);break;case Wm:i.depthFunc(i.LESS);break;case Bo:i.depthFunc(i.LEQUAL);break;case qm:i.depthFunc(i.EQUAL);break;case Xm:i.depthFunc(i.GEQUAL);break;case $m:i.depthFunc(i.GREATER);break;case Ym:i.depthFunc(i.NOTEQUAL);break;default:i.depthFunc(i.LEQUAL)}ie=_e}},setLocked:function(_e){U=_e},setClear:function(_e){se!==_e&&(i.clearDepth(_e),se=_e)},reset:function(){U=!1,re=null,ie=null,se=null}}}function n(){let U=!1,re=null,ie=null,se=null,_e=null,je=null,ot=null,vt=null,Tt=null;return{setTest:function(lt){U||(lt?be(i.STENCIL_TEST):fe(i.STENCIL_TEST))},setMask:function(lt){re!==lt&&!U&&(i.stencilMask(lt),re=lt)},setFunc:function(lt,fn,zt){(ie!==lt||se!==fn||_e!==zt)&&(i.stencilFunc(lt,fn,zt),ie=lt,se=fn,_e=zt)},setOp:function(lt,fn,zt){(je!==lt||ot!==fn||vt!==zt)&&(i.stencilOp(lt,fn,zt),je=lt,ot=fn,vt=zt)},setLocked:function(lt){U=lt},setClear:function(lt){Tt!==lt&&(i.clearStencil(lt),Tt=lt)},reset:function(){U=!1,re=null,ie=null,se=null,_e=null,je=null,ot=null,vt=null,Tt=null}}}const s=new e,r=new t,o=new n,a=new WeakMap,l=new WeakMap;let c={},u={},h=new WeakMap,d=[],f=null,v=!1,g=null,m=null,p=null,x=null,b=null,w=null,O=null,A=new st(0,0,0),L=0,k=!1,E=null,y=null,P=null,K=null,z=null;const Z=i.getParameter(i.MAX_COMBINED_TEXTURE_IMAGE_UNITS);let q=!1,Q=0;const $=i.getParameter(i.VERSION);$.indexOf("WebGL")!==-1?(Q=parseFloat(/^WebGL (\d)/.exec($)[1]),q=Q>=1):$.indexOf("OpenGL ES")!==-1&&(Q=parseFloat(/^OpenGL ES (\d)/.exec($)[1]),q=Q>=2);let te=null,ge={};const de=i.getParameter(i.SCISSOR_BOX),xe=i.getParameter(i.VIEWPORT),Ee=new en().fromArray(de),ye=new en().fromArray(xe);function ne(U,re,ie,se){const _e=new Uint8Array(4),je=i.createTexture();i.bindTexture(U,je),i.texParameteri(U,i.TEXTURE_MIN_FILTER,i.NEAREST),i.texParameteri(U,i.TEXTURE_MAG_FILTER,i.NEAREST);for(let ot=0;ot<ie;ot++)U===i.TEXTURE_3D||U===i.TEXTURE_2D_ARRAY?i.texImage3D(re,0,i.RGBA,1,1,se,0,i.RGBA,i.UNSIGNED_BYTE,_e):i.texImage2D(re+ot,0,i.RGBA,1,1,0,i.RGBA,i.UNSIGNED_BYTE,_e);return je}const ce={};ce[i.TEXTURE_2D]=ne(i.TEXTURE_2D,i.TEXTURE_2D,1),ce[i.TEXTURE_CUBE_MAP]=ne(i.TEXTURE_CUBE_MAP,i.TEXTURE_CUBE_MAP_POSITIVE_X,6),ce[i.TEXTURE_2D_ARRAY]=ne(i.TEXTURE_2D_ARRAY,i.TEXTURE_2D_ARRAY,1,1),ce[i.TEXTURE_3D]=ne(i.TEXTURE_3D,i.TEXTURE_3D,1,1),s.setClear(0,0,0,1),r.setClear(1),o.setClear(0),be(i.DEPTH_TEST),r.setFunc(Bo),ct(!1),Oe(ph),be(i.CULL_FACE),dt(ls);function be(U){c[U]!==!0&&(i.enable(U),c[U]=!0)}function fe(U){c[U]!==!1&&(i.disable(U),c[U]=!1)}function ke(U,re){return u[U]!==re?(i.bindFramebuffer(U,re),u[U]=re,U===i.DRAW_FRAMEBUFFER&&(u[i.FRAMEBUFFER]=re),U===i.FRAMEBUFFER&&(u[i.DRAW_FRAMEBUFFER]=re),!0):!1}function Ve(U,re){let ie=d,se=!1;if(U){ie=h.get(re),ie===void 0&&(ie=[],h.set(re,ie));const _e=U.textures;if(ie.length!==_e.length||ie[0]!==i.COLOR_ATTACHMENT0){for(let je=0,ot=_e.length;je<ot;je++)ie[je]=i.COLOR_ATTACHMENT0+je;ie.length=_e.length,se=!0}}else ie[0]!==i.BACK&&(ie[0]=i.BACK,se=!0);se&&i.drawBuffers(ie)}function Ne(U){return f!==U?(i.useProgram(U),f=U,!0):!1}const pt={[Ns]:i.FUNC_ADD,[Em]:i.FUNC_SUBTRACT,[Tm]:i.FUNC_REVERSE_SUBTRACT};pt[Am]=i.MIN,pt[Cm]=i.MAX;const N={[Rm]:i.ZERO,[Pm]:i.ONE,[Lm]:i.SRC_COLOR,[xc]:i.SRC_ALPHA,[Fm]:i.SRC_ALPHA_SATURATE,[Nm]:i.DST_COLOR,[Im]:i.DST_ALPHA,[Dm]:i.ONE_MINUS_SRC_COLOR,[yc]:i.ONE_MINUS_SRC_ALPHA,[Om]:i.ONE_MINUS_DST_COLOR,[Um]:i.ONE_MINUS_DST_ALPHA,[km]:i.CONSTANT_COLOR,[Bm]:i.ONE_MINUS_CONSTANT_COLOR,[zm]:i.CONSTANT_ALPHA,[Hm]:i.ONE_MINUS_CONSTANT_ALPHA};function dt(U,re,ie,se,_e,je,ot,vt,Tt,lt){if(U===ls){v===!0&&(fe(i.BLEND),v=!1);return}if(v===!1&&(be(i.BLEND),v=!0),U!==wm){if(U!==g||lt!==k){if((m!==Ns||b!==Ns)&&(i.blendEquation(i.FUNC_ADD),m=Ns,b=Ns),lt)switch(U){case Ur:i.blendFuncSeparate(i.ONE,i.ONE_MINUS_SRC_ALPHA,i.ONE,i.ONE_MINUS_SRC_ALPHA);break;case mh:i.blendFunc(i.ONE,i.ONE);break;case gh:i.blendFuncSeparate(i.ZERO,i.ONE_MINUS_SRC_COLOR,i.ZERO,i.ONE);break;case vh:i.blendFuncSeparate(i.ZERO,i.SRC_COLOR,i.ZERO,i.SRC_ALPHA);break;default:console.error("THREE.WebGLState: Invalid blending: ",U);break}else switch(U){case Ur:i.blendFuncSeparate(i.SRC_ALPHA,i.ONE_MINUS_SRC_ALPHA,i.ONE,i.ONE_MINUS_SRC_ALPHA);break;case mh:i.blendFunc(i.SRC_ALPHA,i.ONE);break;case gh:i.blendFuncSeparate(i.ZERO,i.ONE_MINUS_SRC_COLOR,i.ZERO,i.ONE);break;case vh:i.blendFunc(i.ZERO,i.SRC_COLOR);break;default:console.error("THREE.WebGLState: Invalid blending: ",U);break}p=null,x=null,w=null,O=null,A.set(0,0,0),L=0,g=U,k=lt}return}_e=_e||re,je=je||ie,ot=ot||se,(re!==m||_e!==b)&&(i.blendEquationSeparate(pt[re],pt[_e]),m=re,b=_e),(ie!==p||se!==x||je!==w||ot!==O)&&(i.blendFuncSeparate(N[ie],N[se],N[je],N[ot]),p=ie,x=se,w=je,O=ot),(vt.equals(A)===!1||Tt!==L)&&(i.blendColor(vt.r,vt.g,vt.b,Tt),A.copy(vt),L=Tt),g=U,k=!1}function it(U,re){U.side===Ei?fe(i.CULL_FACE):be(i.CULL_FACE);let ie=U.side===Nn;re&&(ie=!ie),ct(ie),U.blending===Ur&&U.transparent===!1?dt(ls):dt(U.blending,U.blendEquation,U.blendSrc,U.blendDst,U.blendEquationAlpha,U.blendSrcAlpha,U.blendDstAlpha,U.blendColor,U.blendAlpha,U.premultipliedAlpha),r.setFunc(U.depthFunc),r.setTest(U.depthTest),r.setMask(U.depthWrite),s.setMask(U.colorWrite);const se=U.stencilWrite;o.setTest(se),se&&(o.setMask(U.stencilWriteMask),o.setFunc(U.stencilFunc,U.stencilRef,U.stencilFuncMask),o.setOp(U.stencilFail,U.stencilZFail,U.stencilZPass)),Xe(U.polygonOffset,U.polygonOffsetFactor,U.polygonOffsetUnits),U.alphaToCoverage===!0?be(i.SAMPLE_ALPHA_TO_COVERAGE):fe(i.SAMPLE_ALPHA_TO_COVERAGE)}function ct(U){E!==U&&(U?i.frontFace(i.CW):i.frontFace(i.CCW),E=U)}function Oe(U){U!==Sm?(be(i.CULL_FACE),U!==y&&(U===ph?i.cullFace(i.BACK):U===Mm?i.cullFace(i.FRONT):i.cullFace(i.FRONT_AND_BACK))):fe(i.CULL_FACE),y=U}function Et(U){U!==P&&(q&&i.lineWidth(U),P=U)}function Xe(U,re,ie){U?(be(i.POLYGON_OFFSET_FILL),(K!==re||z!==ie)&&(i.polygonOffset(re,ie),K=re,z=ie)):fe(i.POLYGON_OFFSET_FILL)}function We(U){U?be(i.SCISSOR_TEST):fe(i.SCISSOR_TEST)}function I(U){U===void 0&&(U=i.TEXTURE0+Z-1),te!==U&&(i.activeTexture(U),te=U)}function M(U,re,ie){ie===void 0&&(te===null?ie=i.TEXTURE0+Z-1:ie=te);let se=ge[ie];se===void 0&&(se={type:void 0,texture:void 0},ge[ie]=se),(se.type!==U||se.texture!==re)&&(te!==ie&&(i.activeTexture(ie),te=ie),i.bindTexture(U,re||ce[U]),se.type=U,se.texture=re)}function J(){const U=ge[te];U!==void 0&&U.type!==void 0&&(i.bindTexture(U.type,null),U.type=void 0,U.texture=void 0)}function oe(){try{i.compressedTexImage2D.apply(i,arguments)}catch(U){console.error("THREE.WebGLState:",U)}}function ee(){try{i.compressedTexImage3D.apply(i,arguments)}catch(U){console.error("THREE.WebGLState:",U)}}function W(){try{i.texSubImage2D.apply(i,arguments)}catch(U){console.error("THREE.WebGLState:",U)}}function we(){try{i.texSubImage3D.apply(i,arguments)}catch(U){console.error("THREE.WebGLState:",U)}}function ve(){try{i.compressedTexSubImage2D.apply(i,arguments)}catch(U){console.error("THREE.WebGLState:",U)}}function Ae(){try{i.compressedTexSubImage3D.apply(i,arguments)}catch(U){console.error("THREE.WebGLState:",U)}}function Ke(){try{i.texStorage2D.apply(i,arguments)}catch(U){console.error("THREE.WebGLState:",U)}}function me(){try{i.texStorage3D.apply(i,arguments)}catch(U){console.error("THREE.WebGLState:",U)}}function Te(){try{i.texImage2D.apply(i,arguments)}catch(U){console.error("THREE.WebGLState:",U)}}function Ze(){try{i.texImage3D.apply(i,arguments)}catch(U){console.error("THREE.WebGLState:",U)}}function Be(U){Ee.equals(U)===!1&&(i.scissor(U.x,U.y,U.z,U.w),Ee.copy(U))}function Me(U){ye.equals(U)===!1&&(i.viewport(U.x,U.y,U.z,U.w),ye.copy(U))}function ze(U,re){let ie=l.get(re);ie===void 0&&(ie=new WeakMap,l.set(re,ie));let se=ie.get(U);se===void 0&&(se=i.getUniformBlockIndex(re,U.name),ie.set(U,se))}function F(U,re){const se=l.get(re).get(U);a.get(re)!==se&&(i.uniformBlockBinding(re,se,U.__bindingPointIndex),a.set(re,se))}function le(){i.disable(i.BLEND),i.disable(i.CULL_FACE),i.disable(i.DEPTH_TEST),i.disable(i.POLYGON_OFFSET_FILL),i.disable(i.SCISSOR_TEST),i.disable(i.STENCIL_TEST),i.disable(i.SAMPLE_ALPHA_TO_COVERAGE),i.blendEquation(i.FUNC_ADD),i.blendFunc(i.ONE,i.ZERO),i.blendFuncSeparate(i.ONE,i.ZERO,i.ONE,i.ZERO),i.blendColor(0,0,0,0),i.colorMask(!0,!0,!0,!0),i.clearColor(0,0,0,0),i.depthMask(!0),i.depthFunc(i.LESS),i.clearDepth(1),i.stencilMask(4294967295),i.stencilFunc(i.ALWAYS,0,4294967295),i.stencilOp(i.KEEP,i.KEEP,i.KEEP),i.clearStencil(0),i.cullFace(i.BACK),i.frontFace(i.CCW),i.polygonOffset(0,0),i.activeTexture(i.TEXTURE0),i.bindFramebuffer(i.FRAMEBUFFER,null),i.bindFramebuffer(i.DRAW_FRAMEBUFFER,null),i.bindFramebuffer(i.READ_FRAMEBUFFER,null),i.useProgram(null),i.lineWidth(1),i.scissor(0,0,i.canvas.width,i.canvas.height),i.viewport(0,0,i.canvas.width,i.canvas.height),c={},te=null,ge={},u={},h=new WeakMap,d=[],f=null,v=!1,g=null,m=null,p=null,x=null,b=null,w=null,O=null,A=new st(0,0,0),L=0,k=!1,E=null,y=null,P=null,K=null,z=null,Ee.set(0,0,i.canvas.width,i.canvas.height),ye.set(0,0,i.canvas.width,i.canvas.height),s.reset(),r.reset(),o.reset()}return{buffers:{color:s,depth:r,stencil:o},enable:be,disable:fe,bindFramebuffer:ke,drawBuffers:Ve,useProgram:Ne,setBlending:dt,setMaterial:it,setFlipSided:ct,setCullFace:Oe,setLineWidth:Et,setPolygonOffset:Xe,setScissorTest:We,activeTexture:I,bindTexture:M,unbindTexture:J,compressedTexImage2D:oe,compressedTexImage3D:ee,texImage2D:Te,texImage3D:Ze,updateUBOMapping:ze,uniformBlockBinding:F,texStorage2D:Ke,texStorage3D:me,texSubImage2D:W,texSubImage3D:we,compressedTexSubImage2D:ve,compressedTexSubImage3D:Ae,scissor:Be,viewport:Me,reset:le}}function cd(i,e,t,n){const s=Ry(n);switch(t){case Rf:return i*e;case Lf:return i*e;case Df:return i*e*2;case If:return i*e/s.components*s.byteLength;case xu:return i*e/s.components*s.byteLength;case Uf:return i*e*2/s.components*s.byteLength;case yu:return i*e*2/s.components*s.byteLength;case Pf:return i*e*3/s.components*s.byteLength;case fi:return i*e*4/s.components*s.byteLength;case bu:return i*e*4/s.components*s.byteLength;case Lo:case Do:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*8;case Io:case Uo:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*16;case Tc:case Cc:return Math.max(i,16)*Math.max(e,8)/4;case Ec:case Ac:return Math.max(i,8)*Math.max(e,8)/2;case Rc:case Pc:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*8;case Lc:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*16;case Dc:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*16;case Ic:return Math.floor((i+4)/5)*Math.floor((e+3)/4)*16;case Uc:return Math.floor((i+4)/5)*Math.floor((e+4)/5)*16;case Nc:return Math.floor((i+5)/6)*Math.floor((e+4)/5)*16;case Oc:return Math.floor((i+5)/6)*Math.floor((e+5)/6)*16;case Fc:return Math.floor((i+7)/8)*Math.floor((e+4)/5)*16;case kc:return Math.floor((i+7)/8)*Math.floor((e+5)/6)*16;case Bc:return Math.floor((i+7)/8)*Math.floor((e+7)/8)*16;case zc:return Math.floor((i+9)/10)*Math.floor((e+4)/5)*16;case Hc:return Math.floor((i+9)/10)*Math.floor((e+5)/6)*16;case Vc:return Math.floor((i+9)/10)*Math.floor((e+7)/8)*16;case Gc:return Math.floor((i+9)/10)*Math.floor((e+9)/10)*16;case Wc:return Math.floor((i+11)/12)*Math.floor((e+9)/10)*16;case qc:return Math.floor((i+11)/12)*Math.floor((e+11)/12)*16;case No:case Xc:case $c:return Math.ceil(i/4)*Math.ceil(e/4)*16;case Nf:case Yc:return Math.ceil(i/4)*Math.ceil(e/4)*8;case jc:case Kc:return Math.ceil(i/4)*Math.ceil(e/4)*16}throw new Error(`Unable to determine texture byte length for ${t} format.`)}function Ry(i){switch(i){case $i:case Tf:return{byteLength:1,components:1};case Ua:case Af:case ka:return{byteLength:2,components:1};case vu:case _u:return{byteLength:2,components:4};case Vs:case gu:case Hi:return{byteLength:4,components:1};case Cf:return{byteLength:4,components:3}}throw new Error(`Unknown texture type ${i}.`)}function Py(i,e,t,n,s,r,o){const a=e.has("WEBGL_multisampled_render_to_texture")?e.get("WEBGL_multisampled_render_to_texture"):null,l=typeof navigator>"u"?!1:/OculusBrowser/g.test(navigator.userAgent),c=new qe,u=new WeakMap;let h;const d=new WeakMap;let f=!1;try{f=typeof OffscreenCanvas<"u"&&new OffscreenCanvas(1,1).getContext("2d")!==null}catch{}function v(I,M){return f?new OffscreenCanvas(I,M):Wo("canvas")}function g(I,M,J){let oe=1;const ee=We(I);if((ee.width>J||ee.height>J)&&(oe=J/Math.max(ee.width,ee.height)),oe<1)if(typeof HTMLImageElement<"u"&&I instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&I instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&I instanceof ImageBitmap||typeof VideoFrame<"u"&&I instanceof VideoFrame){const W=Math.floor(oe*ee.width),we=Math.floor(oe*ee.height);h===void 0&&(h=v(W,we));const ve=M?v(W,we):h;return ve.width=W,ve.height=we,ve.getContext("2d").drawImage(I,0,0,W,we),console.warn("THREE.WebGLRenderer: Texture has been resized from ("+ee.width+"x"+ee.height+") to ("+W+"x"+we+")."),ve}else return"data"in I&&console.warn("THREE.WebGLRenderer: Image in DataTexture is too big ("+ee.width+"x"+ee.height+")."),I;return I}function m(I){return I.generateMipmaps&&I.minFilter!==ei&&I.minFilter!==ui}function p(I){i.generateMipmap(I)}function x(I,M,J,oe,ee=!1){if(I!==null){if(i[I]!==void 0)return i[I];console.warn("THREE.WebGLRenderer: Attempt to use non-existing WebGL internal format '"+I+"'")}let W=M;if(M===i.RED&&(J===i.FLOAT&&(W=i.R32F),J===i.HALF_FLOAT&&(W=i.R16F),J===i.UNSIGNED_BYTE&&(W=i.R8)),M===i.RED_INTEGER&&(J===i.UNSIGNED_BYTE&&(W=i.R8UI),J===i.UNSIGNED_SHORT&&(W=i.R16UI),J===i.UNSIGNED_INT&&(W=i.R32UI),J===i.BYTE&&(W=i.R8I),J===i.SHORT&&(W=i.R16I),J===i.INT&&(W=i.R32I)),M===i.RG&&(J===i.FLOAT&&(W=i.RG32F),J===i.HALF_FLOAT&&(W=i.RG16F),J===i.UNSIGNED_BYTE&&(W=i.RG8)),M===i.RG_INTEGER&&(J===i.UNSIGNED_BYTE&&(W=i.RG8UI),J===i.UNSIGNED_SHORT&&(W=i.RG16UI),J===i.UNSIGNED_INT&&(W=i.RG32UI),J===i.BYTE&&(W=i.RG8I),J===i.SHORT&&(W=i.RG16I),J===i.INT&&(W=i.RG32I)),M===i.RGB&&J===i.UNSIGNED_INT_5_9_9_9_REV&&(W=i.RGB9_E5),M===i.RGBA){const we=ee?zo:wt.getTransfer(oe);J===i.FLOAT&&(W=i.RGBA32F),J===i.HALF_FLOAT&&(W=i.RGBA16F),J===i.UNSIGNED_BYTE&&(W=we===Bt?i.SRGB8_ALPHA8:i.RGBA8),J===i.UNSIGNED_SHORT_4_4_4_4&&(W=i.RGBA4),J===i.UNSIGNED_SHORT_5_5_5_1&&(W=i.RGB5_A1)}return(W===i.R16F||W===i.R32F||W===i.RG16F||W===i.RG32F||W===i.RGBA16F||W===i.RGBA32F)&&e.get("EXT_color_buffer_float"),W}function b(I,M){let J;return I?M===null||M===Vs||M===Vr?J=i.DEPTH24_STENCIL8:M===Hi?J=i.DEPTH32F_STENCIL8:M===Ua&&(J=i.DEPTH24_STENCIL8,console.warn("DepthTexture: 16 bit depth attachment is not supported with stencil. Using 24-bit attachment.")):M===null||M===Vs||M===Vr?J=i.DEPTH_COMPONENT24:M===Hi?J=i.DEPTH_COMPONENT32F:M===Ua&&(J=i.DEPTH_COMPONENT16),J}function w(I,M){return m(I)===!0||I.isFramebufferTexture&&I.minFilter!==ei&&I.minFilter!==ui?Math.log2(Math.max(M.width,M.height))+1:I.mipmaps!==void 0&&I.mipmaps.length>0?I.mipmaps.length:I.isCompressedTexture&&Array.isArray(I.image)?M.mipmaps.length:1}function O(I){const M=I.target;M.removeEventListener("dispose",O),L(M),M.isVideoTexture&&u.delete(M)}function A(I){const M=I.target;M.removeEventListener("dispose",A),E(M)}function L(I){const M=n.get(I);if(M.__webglInit===void 0)return;const J=I.source,oe=d.get(J);if(oe){const ee=oe[M.__cacheKey];ee.usedTimes--,ee.usedTimes===0&&k(I),Object.keys(oe).length===0&&d.delete(J)}n.remove(I)}function k(I){const M=n.get(I);i.deleteTexture(M.__webglTexture);const J=I.source,oe=d.get(J);delete oe[M.__cacheKey],o.memory.textures--}function E(I){const M=n.get(I);if(I.depthTexture&&I.depthTexture.dispose(),I.isWebGLCubeRenderTarget)for(let oe=0;oe<6;oe++){if(Array.isArray(M.__webglFramebuffer[oe]))for(let ee=0;ee<M.__webglFramebuffer[oe].length;ee++)i.deleteFramebuffer(M.__webglFramebuffer[oe][ee]);else i.deleteFramebuffer(M.__webglFramebuffer[oe]);M.__webglDepthbuffer&&i.deleteRenderbuffer(M.__webglDepthbuffer[oe])}else{if(Array.isArray(M.__webglFramebuffer))for(let oe=0;oe<M.__webglFramebuffer.length;oe++)i.deleteFramebuffer(M.__webglFramebuffer[oe]);else i.deleteFramebuffer(M.__webglFramebuffer);if(M.__webglDepthbuffer&&i.deleteRenderbuffer(M.__webglDepthbuffer),M.__webglMultisampledFramebuffer&&i.deleteFramebuffer(M.__webglMultisampledFramebuffer),M.__webglColorRenderbuffer)for(let oe=0;oe<M.__webglColorRenderbuffer.length;oe++)M.__webglColorRenderbuffer[oe]&&i.deleteRenderbuffer(M.__webglColorRenderbuffer[oe]);M.__webglDepthRenderbuffer&&i.deleteRenderbuffer(M.__webglDepthRenderbuffer)}const J=I.textures;for(let oe=0,ee=J.length;oe<ee;oe++){const W=n.get(J[oe]);W.__webglTexture&&(i.deleteTexture(W.__webglTexture),o.memory.textures--),n.remove(J[oe])}n.remove(I)}let y=0;function P(){y=0}function K(){const I=y;return I>=s.maxTextures&&console.warn("THREE.WebGLTextures: Trying to use "+I+" texture units while this GPU supports only "+s.maxTextures),y+=1,I}function z(I){const M=[];return M.push(I.wrapS),M.push(I.wrapT),M.push(I.wrapR||0),M.push(I.magFilter),M.push(I.minFilter),M.push(I.anisotropy),M.push(I.internalFormat),M.push(I.format),M.push(I.type),M.push(I.generateMipmaps),M.push(I.premultiplyAlpha),M.push(I.flipY),M.push(I.unpackAlignment),M.push(I.colorSpace),M.join()}function Z(I,M){const J=n.get(I);if(I.isVideoTexture&&Et(I),I.isRenderTargetTexture===!1&&I.version>0&&J.__version!==I.version){const oe=I.image;if(oe===null)console.warn("THREE.WebGLRenderer: Texture marked for update but no image data found.");else if(oe.complete===!1)console.warn("THREE.WebGLRenderer: Texture marked for update but image is incomplete");else{ye(J,I,M);return}}t.bindTexture(i.TEXTURE_2D,J.__webglTexture,i.TEXTURE0+M)}function q(I,M){const J=n.get(I);if(I.version>0&&J.__version!==I.version){ye(J,I,M);return}t.bindTexture(i.TEXTURE_2D_ARRAY,J.__webglTexture,i.TEXTURE0+M)}function Q(I,M){const J=n.get(I);if(I.version>0&&J.__version!==I.version){ye(J,I,M);return}t.bindTexture(i.TEXTURE_3D,J.__webglTexture,i.TEXTURE0+M)}function $(I,M){const J=n.get(I);if(I.version>0&&J.__version!==I.version){ne(J,I,M);return}t.bindTexture(i.TEXTURE_CUBE_MAP,J.__webglTexture,i.TEXTURE0+M)}const te={[Mc]:i.REPEAT,[ks]:i.CLAMP_TO_EDGE,[wc]:i.MIRRORED_REPEAT},ge={[ei]:i.NEAREST,[ig]:i.NEAREST_MIPMAP_NEAREST,[Ya]:i.NEAREST_MIPMAP_LINEAR,[ui]:i.LINEAR,[Pl]:i.LINEAR_MIPMAP_NEAREST,[Bs]:i.LINEAR_MIPMAP_LINEAR},de={[og]:i.NEVER,[fg]:i.ALWAYS,[lg]:i.LESS,[Ff]:i.LEQUAL,[cg]:i.EQUAL,[dg]:i.GEQUAL,[ug]:i.GREATER,[hg]:i.NOTEQUAL};function xe(I,M){if(M.type===Hi&&e.has("OES_texture_float_linear")===!1&&(M.magFilter===ui||M.magFilter===Pl||M.magFilter===Ya||M.magFilter===Bs||M.minFilter===ui||M.minFilter===Pl||M.minFilter===Ya||M.minFilter===Bs)&&console.warn("THREE.WebGLRenderer: Unable to use linear filtering with floating point textures. OES_texture_float_linear not supported on this device."),i.texParameteri(I,i.TEXTURE_WRAP_S,te[M.wrapS]),i.texParameteri(I,i.TEXTURE_WRAP_T,te[M.wrapT]),(I===i.TEXTURE_3D||I===i.TEXTURE_2D_ARRAY)&&i.texParameteri(I,i.TEXTURE_WRAP_R,te[M.wrapR]),i.texParameteri(I,i.TEXTURE_MAG_FILTER,ge[M.magFilter]),i.texParameteri(I,i.TEXTURE_MIN_FILTER,ge[M.minFilter]),M.compareFunction&&(i.texParameteri(I,i.TEXTURE_COMPARE_MODE,i.COMPARE_REF_TO_TEXTURE),i.texParameteri(I,i.TEXTURE_COMPARE_FUNC,de[M.compareFunction])),e.has("EXT_texture_filter_anisotropic")===!0){if(M.magFilter===ei||M.minFilter!==Ya&&M.minFilter!==Bs||M.type===Hi&&e.has("OES_texture_float_linear")===!1)return;if(M.anisotropy>1||n.get(M).__currentAnisotropy){const J=e.get("EXT_texture_filter_anisotropic");i.texParameterf(I,J.TEXTURE_MAX_ANISOTROPY_EXT,Math.min(M.anisotropy,s.getMaxAnisotropy())),n.get(M).__currentAnisotropy=M.anisotropy}}}function Ee(I,M){let J=!1;I.__webglInit===void 0&&(I.__webglInit=!0,M.addEventListener("dispose",O));const oe=M.source;let ee=d.get(oe);ee===void 0&&(ee={},d.set(oe,ee));const W=z(M);if(W!==I.__cacheKey){ee[W]===void 0&&(ee[W]={texture:i.createTexture(),usedTimes:0},o.memory.textures++,J=!0),ee[W].usedTimes++;const we=ee[I.__cacheKey];we!==void 0&&(ee[I.__cacheKey].usedTimes--,we.usedTimes===0&&k(M)),I.__cacheKey=W,I.__webglTexture=ee[W].texture}return J}function ye(I,M,J){let oe=i.TEXTURE_2D;(M.isDataArrayTexture||M.isCompressedArrayTexture)&&(oe=i.TEXTURE_2D_ARRAY),M.isData3DTexture&&(oe=i.TEXTURE_3D);const ee=Ee(I,M),W=M.source;t.bindTexture(oe,I.__webglTexture,i.TEXTURE0+J);const we=n.get(W);if(W.version!==we.__version||ee===!0){t.activeTexture(i.TEXTURE0+J);const ve=wt.getPrimaries(wt.workingColorSpace),Ae=M.colorSpace===os?null:wt.getPrimaries(M.colorSpace),Ke=M.colorSpace===os||ve===Ae?i.NONE:i.BROWSER_DEFAULT_WEBGL;i.pixelStorei(i.UNPACK_FLIP_Y_WEBGL,M.flipY),i.pixelStorei(i.UNPACK_PREMULTIPLY_ALPHA_WEBGL,M.premultiplyAlpha),i.pixelStorei(i.UNPACK_ALIGNMENT,M.unpackAlignment),i.pixelStorei(i.UNPACK_COLORSPACE_CONVERSION_WEBGL,Ke);let me=g(M.image,!1,s.maxTextureSize);me=Xe(M,me);const Te=r.convert(M.format,M.colorSpace),Ze=r.convert(M.type);let Be=x(M.internalFormat,Te,Ze,M.colorSpace,M.isVideoTexture);xe(oe,M);let Me;const ze=M.mipmaps,F=M.isVideoTexture!==!0,le=we.__version===void 0||ee===!0,U=W.dataReady,re=w(M,me);if(M.isDepthTexture)Be=b(M.format===Gr,M.type),le&&(F?t.texStorage2D(i.TEXTURE_2D,1,Be,me.width,me.height):t.texImage2D(i.TEXTURE_2D,0,Be,me.width,me.height,0,Te,Ze,null));else if(M.isDataTexture)if(ze.length>0){F&&le&&t.texStorage2D(i.TEXTURE_2D,re,Be,ze[0].width,ze[0].height);for(let ie=0,se=ze.length;ie<se;ie++)Me=ze[ie],F?U&&t.texSubImage2D(i.TEXTURE_2D,ie,0,0,Me.width,Me.height,Te,Ze,Me.data):t.texImage2D(i.TEXTURE_2D,ie,Be,Me.width,Me.height,0,Te,Ze,Me.data);M.generateMipmaps=!1}else F?(le&&t.texStorage2D(i.TEXTURE_2D,re,Be,me.width,me.height),U&&t.texSubImage2D(i.TEXTURE_2D,0,0,0,me.width,me.height,Te,Ze,me.data)):t.texImage2D(i.TEXTURE_2D,0,Be,me.width,me.height,0,Te,Ze,me.data);else if(M.isCompressedTexture)if(M.isCompressedArrayTexture){F&&le&&t.texStorage3D(i.TEXTURE_2D_ARRAY,re,Be,ze[0].width,ze[0].height,me.depth);for(let ie=0,se=ze.length;ie<se;ie++)if(Me=ze[ie],M.format!==fi)if(Te!==null)if(F){if(U)if(M.layerUpdates.size>0){const _e=cd(Me.width,Me.height,M.format,M.type);for(const je of M.layerUpdates){const ot=Me.data.subarray(je*_e/Me.data.BYTES_PER_ELEMENT,(je+1)*_e/Me.data.BYTES_PER_ELEMENT);t.compressedTexSubImage3D(i.TEXTURE_2D_ARRAY,ie,0,0,je,Me.width,Me.height,1,Te,ot,0,0)}M.clearLayerUpdates()}else t.compressedTexSubImage3D(i.TEXTURE_2D_ARRAY,ie,0,0,0,Me.width,Me.height,me.depth,Te,Me.data,0,0)}else t.compressedTexImage3D(i.TEXTURE_2D_ARRAY,ie,Be,Me.width,Me.height,me.depth,0,Me.data,0,0);else console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()");else F?U&&t.texSubImage3D(i.TEXTURE_2D_ARRAY,ie,0,0,0,Me.width,Me.height,me.depth,Te,Ze,Me.data):t.texImage3D(i.TEXTURE_2D_ARRAY,ie,Be,Me.width,Me.height,me.depth,0,Te,Ze,Me.data)}else{F&&le&&t.texStorage2D(i.TEXTURE_2D,re,Be,ze[0].width,ze[0].height);for(let ie=0,se=ze.length;ie<se;ie++)Me=ze[ie],M.format!==fi?Te!==null?F?U&&t.compressedTexSubImage2D(i.TEXTURE_2D,ie,0,0,Me.width,Me.height,Te,Me.data):t.compressedTexImage2D(i.TEXTURE_2D,ie,Be,Me.width,Me.height,0,Me.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()"):F?U&&t.texSubImage2D(i.TEXTURE_2D,ie,0,0,Me.width,Me.height,Te,Ze,Me.data):t.texImage2D(i.TEXTURE_2D,ie,Be,Me.width,Me.height,0,Te,Ze,Me.data)}else if(M.isDataArrayTexture)if(F){if(le&&t.texStorage3D(i.TEXTURE_2D_ARRAY,re,Be,me.width,me.height,me.depth),U)if(M.layerUpdates.size>0){const ie=cd(me.width,me.height,M.format,M.type);for(const se of M.layerUpdates){const _e=me.data.subarray(se*ie/me.data.BYTES_PER_ELEMENT,(se+1)*ie/me.data.BYTES_PER_ELEMENT);t.texSubImage3D(i.TEXTURE_2D_ARRAY,0,0,0,se,me.width,me.height,1,Te,Ze,_e)}M.clearLayerUpdates()}else t.texSubImage3D(i.TEXTURE_2D_ARRAY,0,0,0,0,me.width,me.height,me.depth,Te,Ze,me.data)}else t.texImage3D(i.TEXTURE_2D_ARRAY,0,Be,me.width,me.height,me.depth,0,Te,Ze,me.data);else if(M.isData3DTexture)F?(le&&t.texStorage3D(i.TEXTURE_3D,re,Be,me.width,me.height,me.depth),U&&t.texSubImage3D(i.TEXTURE_3D,0,0,0,0,me.width,me.height,me.depth,Te,Ze,me.data)):t.texImage3D(i.TEXTURE_3D,0,Be,me.width,me.height,me.depth,0,Te,Ze,me.data);else if(M.isFramebufferTexture){if(le)if(F)t.texStorage2D(i.TEXTURE_2D,re,Be,me.width,me.height);else{let ie=me.width,se=me.height;for(let _e=0;_e<re;_e++)t.texImage2D(i.TEXTURE_2D,_e,Be,ie,se,0,Te,Ze,null),ie>>=1,se>>=1}}else if(ze.length>0){if(F&&le){const ie=We(ze[0]);t.texStorage2D(i.TEXTURE_2D,re,Be,ie.width,ie.height)}for(let ie=0,se=ze.length;ie<se;ie++)Me=ze[ie],F?U&&t.texSubImage2D(i.TEXTURE_2D,ie,0,0,Te,Ze,Me):t.texImage2D(i.TEXTURE_2D,ie,Be,Te,Ze,Me);M.generateMipmaps=!1}else if(F){if(le){const ie=We(me);t.texStorage2D(i.TEXTURE_2D,re,Be,ie.width,ie.height)}U&&t.texSubImage2D(i.TEXTURE_2D,0,0,0,Te,Ze,me)}else t.texImage2D(i.TEXTURE_2D,0,Be,Te,Ze,me);m(M)&&p(oe),we.__version=W.version,M.onUpdate&&M.onUpdate(M)}I.__version=M.version}function ne(I,M,J){if(M.image.length!==6)return;const oe=Ee(I,M),ee=M.source;t.bindTexture(i.TEXTURE_CUBE_MAP,I.__webglTexture,i.TEXTURE0+J);const W=n.get(ee);if(ee.version!==W.__version||oe===!0){t.activeTexture(i.TEXTURE0+J);const we=wt.getPrimaries(wt.workingColorSpace),ve=M.colorSpace===os?null:wt.getPrimaries(M.colorSpace),Ae=M.colorSpace===os||we===ve?i.NONE:i.BROWSER_DEFAULT_WEBGL;i.pixelStorei(i.UNPACK_FLIP_Y_WEBGL,M.flipY),i.pixelStorei(i.UNPACK_PREMULTIPLY_ALPHA_WEBGL,M.premultiplyAlpha),i.pixelStorei(i.UNPACK_ALIGNMENT,M.unpackAlignment),i.pixelStorei(i.UNPACK_COLORSPACE_CONVERSION_WEBGL,Ae);const Ke=M.isCompressedTexture||M.image[0].isCompressedTexture,me=M.image[0]&&M.image[0].isDataTexture,Te=[];for(let se=0;se<6;se++)!Ke&&!me?Te[se]=g(M.image[se],!0,s.maxCubemapSize):Te[se]=me?M.image[se].image:M.image[se],Te[se]=Xe(M,Te[se]);const Ze=Te[0],Be=r.convert(M.format,M.colorSpace),Me=r.convert(M.type),ze=x(M.internalFormat,Be,Me,M.colorSpace),F=M.isVideoTexture!==!0,le=W.__version===void 0||oe===!0,U=ee.dataReady;let re=w(M,Ze);xe(i.TEXTURE_CUBE_MAP,M);let ie;if(Ke){F&&le&&t.texStorage2D(i.TEXTURE_CUBE_MAP,re,ze,Ze.width,Ze.height);for(let se=0;se<6;se++){ie=Te[se].mipmaps;for(let _e=0;_e<ie.length;_e++){const je=ie[_e];M.format!==fi?Be!==null?F?U&&t.compressedTexSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+se,_e,0,0,je.width,je.height,Be,je.data):t.compressedTexImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+se,_e,ze,je.width,je.height,0,je.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .setTextureCube()"):F?U&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+se,_e,0,0,je.width,je.height,Be,Me,je.data):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+se,_e,ze,je.width,je.height,0,Be,Me,je.data)}}}else{if(ie=M.mipmaps,F&&le){ie.length>0&&re++;const se=We(Te[0]);t.texStorage2D(i.TEXTURE_CUBE_MAP,re,ze,se.width,se.height)}for(let se=0;se<6;se++)if(me){F?U&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+se,0,0,0,Te[se].width,Te[se].height,Be,Me,Te[se].data):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+se,0,ze,Te[se].width,Te[se].height,0,Be,Me,Te[se].data);for(let _e=0;_e<ie.length;_e++){const ot=ie[_e].image[se].image;F?U&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+se,_e+1,0,0,ot.width,ot.height,Be,Me,ot.data):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+se,_e+1,ze,ot.width,ot.height,0,Be,Me,ot.data)}}else{F?U&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+se,0,0,0,Be,Me,Te[se]):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+se,0,ze,Be,Me,Te[se]);for(let _e=0;_e<ie.length;_e++){const je=ie[_e];F?U&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+se,_e+1,0,0,Be,Me,je.image[se]):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+se,_e+1,ze,Be,Me,je.image[se])}}}m(M)&&p(i.TEXTURE_CUBE_MAP),W.__version=ee.version,M.onUpdate&&M.onUpdate(M)}I.__version=M.version}function ce(I,M,J,oe,ee,W){const we=r.convert(J.format,J.colorSpace),ve=r.convert(J.type),Ae=x(J.internalFormat,we,ve,J.colorSpace);if(!n.get(M).__hasExternalTextures){const me=Math.max(1,M.width>>W),Te=Math.max(1,M.height>>W);ee===i.TEXTURE_3D||ee===i.TEXTURE_2D_ARRAY?t.texImage3D(ee,W,Ae,me,Te,M.depth,0,we,ve,null):t.texImage2D(ee,W,Ae,me,Te,0,we,ve,null)}t.bindFramebuffer(i.FRAMEBUFFER,I),Oe(M)?a.framebufferTexture2DMultisampleEXT(i.FRAMEBUFFER,oe,ee,n.get(J).__webglTexture,0,ct(M)):(ee===i.TEXTURE_2D||ee>=i.TEXTURE_CUBE_MAP_POSITIVE_X&&ee<=i.TEXTURE_CUBE_MAP_NEGATIVE_Z)&&i.framebufferTexture2D(i.FRAMEBUFFER,oe,ee,n.get(J).__webglTexture,W),t.bindFramebuffer(i.FRAMEBUFFER,null)}function be(I,M,J){if(i.bindRenderbuffer(i.RENDERBUFFER,I),M.depthBuffer){const oe=M.depthTexture,ee=oe&&oe.isDepthTexture?oe.type:null,W=b(M.stencilBuffer,ee),we=M.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,ve=ct(M);Oe(M)?a.renderbufferStorageMultisampleEXT(i.RENDERBUFFER,ve,W,M.width,M.height):J?i.renderbufferStorageMultisample(i.RENDERBUFFER,ve,W,M.width,M.height):i.renderbufferStorage(i.RENDERBUFFER,W,M.width,M.height),i.framebufferRenderbuffer(i.FRAMEBUFFER,we,i.RENDERBUFFER,I)}else{const oe=M.textures;for(let ee=0;ee<oe.length;ee++){const W=oe[ee],we=r.convert(W.format,W.colorSpace),ve=r.convert(W.type),Ae=x(W.internalFormat,we,ve,W.colorSpace),Ke=ct(M);J&&Oe(M)===!1?i.renderbufferStorageMultisample(i.RENDERBUFFER,Ke,Ae,M.width,M.height):Oe(M)?a.renderbufferStorageMultisampleEXT(i.RENDERBUFFER,Ke,Ae,M.width,M.height):i.renderbufferStorage(i.RENDERBUFFER,Ae,M.width,M.height)}}i.bindRenderbuffer(i.RENDERBUFFER,null)}function fe(I,M){if(M&&M.isWebGLCubeRenderTarget)throw new Error("Depth Texture with cube render targets is not supported");if(t.bindFramebuffer(i.FRAMEBUFFER,I),!(M.depthTexture&&M.depthTexture.isDepthTexture))throw new Error("renderTarget.depthTexture must be an instance of THREE.DepthTexture");(!n.get(M.depthTexture).__webglTexture||M.depthTexture.image.width!==M.width||M.depthTexture.image.height!==M.height)&&(M.depthTexture.image.width=M.width,M.depthTexture.image.height=M.height,M.depthTexture.needsUpdate=!0),Z(M.depthTexture,0);const oe=n.get(M.depthTexture).__webglTexture,ee=ct(M);if(M.depthTexture.format===Nr)Oe(M)?a.framebufferTexture2DMultisampleEXT(i.FRAMEBUFFER,i.DEPTH_ATTACHMENT,i.TEXTURE_2D,oe,0,ee):i.framebufferTexture2D(i.FRAMEBUFFER,i.DEPTH_ATTACHMENT,i.TEXTURE_2D,oe,0);else if(M.depthTexture.format===Gr)Oe(M)?a.framebufferTexture2DMultisampleEXT(i.FRAMEBUFFER,i.DEPTH_STENCIL_ATTACHMENT,i.TEXTURE_2D,oe,0,ee):i.framebufferTexture2D(i.FRAMEBUFFER,i.DEPTH_STENCIL_ATTACHMENT,i.TEXTURE_2D,oe,0);else throw new Error("Unknown depthTexture format")}function ke(I){const M=n.get(I),J=I.isWebGLCubeRenderTarget===!0;if(M.__boundDepthTexture!==I.depthTexture){const oe=I.depthTexture;if(M.__depthDisposeCallback&&M.__depthDisposeCallback(),oe){const ee=()=>{delete M.__boundDepthTexture,delete M.__depthDisposeCallback,oe.removeEventListener("dispose",ee)};oe.addEventListener("dispose",ee),M.__depthDisposeCallback=ee}M.__boundDepthTexture=oe}if(I.depthTexture&&!M.__autoAllocateDepthBuffer){if(J)throw new Error("target.depthTexture not supported in Cube render targets");fe(M.__webglFramebuffer,I)}else if(J){M.__webglDepthbuffer=[];for(let oe=0;oe<6;oe++)if(t.bindFramebuffer(i.FRAMEBUFFER,M.__webglFramebuffer[oe]),M.__webglDepthbuffer[oe]===void 0)M.__webglDepthbuffer[oe]=i.createRenderbuffer(),be(M.__webglDepthbuffer[oe],I,!1);else{const ee=I.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,W=M.__webglDepthbuffer[oe];i.bindRenderbuffer(i.RENDERBUFFER,W),i.framebufferRenderbuffer(i.FRAMEBUFFER,ee,i.RENDERBUFFER,W)}}else if(t.bindFramebuffer(i.FRAMEBUFFER,M.__webglFramebuffer),M.__webglDepthbuffer===void 0)M.__webglDepthbuffer=i.createRenderbuffer(),be(M.__webglDepthbuffer,I,!1);else{const oe=I.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,ee=M.__webglDepthbuffer;i.bindRenderbuffer(i.RENDERBUFFER,ee),i.framebufferRenderbuffer(i.FRAMEBUFFER,oe,i.RENDERBUFFER,ee)}t.bindFramebuffer(i.FRAMEBUFFER,null)}function Ve(I,M,J){const oe=n.get(I);M!==void 0&&ce(oe.__webglFramebuffer,I,I.texture,i.COLOR_ATTACHMENT0,i.TEXTURE_2D,0),J!==void 0&&ke(I)}function Ne(I){const M=I.texture,J=n.get(I),oe=n.get(M);I.addEventListener("dispose",A);const ee=I.textures,W=I.isWebGLCubeRenderTarget===!0,we=ee.length>1;if(we||(oe.__webglTexture===void 0&&(oe.__webglTexture=i.createTexture()),oe.__version=M.version,o.memory.textures++),W){J.__webglFramebuffer=[];for(let ve=0;ve<6;ve++)if(M.mipmaps&&M.mipmaps.length>0){J.__webglFramebuffer[ve]=[];for(let Ae=0;Ae<M.mipmaps.length;Ae++)J.__webglFramebuffer[ve][Ae]=i.createFramebuffer()}else J.__webglFramebuffer[ve]=i.createFramebuffer()}else{if(M.mipmaps&&M.mipmaps.length>0){J.__webglFramebuffer=[];for(let ve=0;ve<M.mipmaps.length;ve++)J.__webglFramebuffer[ve]=i.createFramebuffer()}else J.__webglFramebuffer=i.createFramebuffer();if(we)for(let ve=0,Ae=ee.length;ve<Ae;ve++){const Ke=n.get(ee[ve]);Ke.__webglTexture===void 0&&(Ke.__webglTexture=i.createTexture(),o.memory.textures++)}if(I.samples>0&&Oe(I)===!1){J.__webglMultisampledFramebuffer=i.createFramebuffer(),J.__webglColorRenderbuffer=[],t.bindFramebuffer(i.FRAMEBUFFER,J.__webglMultisampledFramebuffer);for(let ve=0;ve<ee.length;ve++){const Ae=ee[ve];J.__webglColorRenderbuffer[ve]=i.createRenderbuffer(),i.bindRenderbuffer(i.RENDERBUFFER,J.__webglColorRenderbuffer[ve]);const Ke=r.convert(Ae.format,Ae.colorSpace),me=r.convert(Ae.type),Te=x(Ae.internalFormat,Ke,me,Ae.colorSpace,I.isXRRenderTarget===!0),Ze=ct(I);i.renderbufferStorageMultisample(i.RENDERBUFFER,Ze,Te,I.width,I.height),i.framebufferRenderbuffer(i.FRAMEBUFFER,i.COLOR_ATTACHMENT0+ve,i.RENDERBUFFER,J.__webglColorRenderbuffer[ve])}i.bindRenderbuffer(i.RENDERBUFFER,null),I.depthBuffer&&(J.__webglDepthRenderbuffer=i.createRenderbuffer(),be(J.__webglDepthRenderbuffer,I,!0)),t.bindFramebuffer(i.FRAMEBUFFER,null)}}if(W){t.bindTexture(i.TEXTURE_CUBE_MAP,oe.__webglTexture),xe(i.TEXTURE_CUBE_MAP,M);for(let ve=0;ve<6;ve++)if(M.mipmaps&&M.mipmaps.length>0)for(let Ae=0;Ae<M.mipmaps.length;Ae++)ce(J.__webglFramebuffer[ve][Ae],I,M,i.COLOR_ATTACHMENT0,i.TEXTURE_CUBE_MAP_POSITIVE_X+ve,Ae);else ce(J.__webglFramebuffer[ve],I,M,i.COLOR_ATTACHMENT0,i.TEXTURE_CUBE_MAP_POSITIVE_X+ve,0);m(M)&&p(i.TEXTURE_CUBE_MAP),t.unbindTexture()}else if(we){for(let ve=0,Ae=ee.length;ve<Ae;ve++){const Ke=ee[ve],me=n.get(Ke);t.bindTexture(i.TEXTURE_2D,me.__webglTexture),xe(i.TEXTURE_2D,Ke),ce(J.__webglFramebuffer,I,Ke,i.COLOR_ATTACHMENT0+ve,i.TEXTURE_2D,0),m(Ke)&&p(i.TEXTURE_2D)}t.unbindTexture()}else{let ve=i.TEXTURE_2D;if((I.isWebGL3DRenderTarget||I.isWebGLArrayRenderTarget)&&(ve=I.isWebGL3DRenderTarget?i.TEXTURE_3D:i.TEXTURE_2D_ARRAY),t.bindTexture(ve,oe.__webglTexture),xe(ve,M),M.mipmaps&&M.mipmaps.length>0)for(let Ae=0;Ae<M.mipmaps.length;Ae++)ce(J.__webglFramebuffer[Ae],I,M,i.COLOR_ATTACHMENT0,ve,Ae);else ce(J.__webglFramebuffer,I,M,i.COLOR_ATTACHMENT0,ve,0);m(M)&&p(ve),t.unbindTexture()}I.depthBuffer&&ke(I)}function pt(I){const M=I.textures;for(let J=0,oe=M.length;J<oe;J++){const ee=M[J];if(m(ee)){const W=I.isWebGLCubeRenderTarget?i.TEXTURE_CUBE_MAP:i.TEXTURE_2D,we=n.get(ee).__webglTexture;t.bindTexture(W,we),p(W),t.unbindTexture()}}}const N=[],dt=[];function it(I){if(I.samples>0){if(Oe(I)===!1){const M=I.textures,J=I.width,oe=I.height;let ee=i.COLOR_BUFFER_BIT;const W=I.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,we=n.get(I),ve=M.length>1;if(ve)for(let Ae=0;Ae<M.length;Ae++)t.bindFramebuffer(i.FRAMEBUFFER,we.__webglMultisampledFramebuffer),i.framebufferRenderbuffer(i.FRAMEBUFFER,i.COLOR_ATTACHMENT0+Ae,i.RENDERBUFFER,null),t.bindFramebuffer(i.FRAMEBUFFER,we.__webglFramebuffer),i.framebufferTexture2D(i.DRAW_FRAMEBUFFER,i.COLOR_ATTACHMENT0+Ae,i.TEXTURE_2D,null,0);t.bindFramebuffer(i.READ_FRAMEBUFFER,we.__webglMultisampledFramebuffer),t.bindFramebuffer(i.DRAW_FRAMEBUFFER,we.__webglFramebuffer);for(let Ae=0;Ae<M.length;Ae++){if(I.resolveDepthBuffer&&(I.depthBuffer&&(ee|=i.DEPTH_BUFFER_BIT),I.stencilBuffer&&I.resolveStencilBuffer&&(ee|=i.STENCIL_BUFFER_BIT)),ve){i.framebufferRenderbuffer(i.READ_FRAMEBUFFER,i.COLOR_ATTACHMENT0,i.RENDERBUFFER,we.__webglColorRenderbuffer[Ae]);const Ke=n.get(M[Ae]).__webglTexture;i.framebufferTexture2D(i.DRAW_FRAMEBUFFER,i.COLOR_ATTACHMENT0,i.TEXTURE_2D,Ke,0)}i.blitFramebuffer(0,0,J,oe,0,0,J,oe,ee,i.NEAREST),l===!0&&(N.length=0,dt.length=0,N.push(i.COLOR_ATTACHMENT0+Ae),I.depthBuffer&&I.resolveDepthBuffer===!1&&(N.push(W),dt.push(W),i.invalidateFramebuffer(i.DRAW_FRAMEBUFFER,dt)),i.invalidateFramebuffer(i.READ_FRAMEBUFFER,N))}if(t.bindFramebuffer(i.READ_FRAMEBUFFER,null),t.bindFramebuffer(i.DRAW_FRAMEBUFFER,null),ve)for(let Ae=0;Ae<M.length;Ae++){t.bindFramebuffer(i.FRAMEBUFFER,we.__webglMultisampledFramebuffer),i.framebufferRenderbuffer(i.FRAMEBUFFER,i.COLOR_ATTACHMENT0+Ae,i.RENDERBUFFER,we.__webglColorRenderbuffer[Ae]);const Ke=n.get(M[Ae]).__webglTexture;t.bindFramebuffer(i.FRAMEBUFFER,we.__webglFramebuffer),i.framebufferTexture2D(i.DRAW_FRAMEBUFFER,i.COLOR_ATTACHMENT0+Ae,i.TEXTURE_2D,Ke,0)}t.bindFramebuffer(i.DRAW_FRAMEBUFFER,we.__webglMultisampledFramebuffer)}else if(I.depthBuffer&&I.resolveDepthBuffer===!1&&l){const M=I.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT;i.invalidateFramebuffer(i.DRAW_FRAMEBUFFER,[M])}}}function ct(I){return Math.min(s.maxSamples,I.samples)}function Oe(I){const M=n.get(I);return I.samples>0&&e.has("WEBGL_multisampled_render_to_texture")===!0&&M.__useRenderToTexture!==!1}function Et(I){const M=o.render.frame;u.get(I)!==M&&(u.set(I,M),I.update())}function Xe(I,M){const J=I.colorSpace,oe=I.format,ee=I.type;return I.isCompressedTexture===!0||I.isVideoTexture===!0||J!==gs&&J!==os&&(wt.getTransfer(J)===Bt?(oe!==fi||ee!==$i)&&console.warn("THREE.WebGLTextures: sRGB encoded textures have to use RGBAFormat and UnsignedByteType."):console.error("THREE.WebGLTextures: Unsupported texture color space:",J)),M}function We(I){return typeof HTMLImageElement<"u"&&I instanceof HTMLImageElement?(c.width=I.naturalWidth||I.width,c.height=I.naturalHeight||I.height):typeof VideoFrame<"u"&&I instanceof VideoFrame?(c.width=I.displayWidth,c.height=I.displayHeight):(c.width=I.width,c.height=I.height),c}this.allocateTextureUnit=K,this.resetTextureUnits=P,this.setTexture2D=Z,this.setTexture2DArray=q,this.setTexture3D=Q,this.setTextureCube=$,this.rebindTextures=Ve,this.setupRenderTarget=Ne,this.updateRenderTargetMipmap=pt,this.updateMultisampleRenderTarget=it,this.setupDepthRenderbuffer=ke,this.setupFrameBufferTexture=ce,this.useMultisampledRTT=Oe}function Ly(i,e){function t(n,s=os){let r;const o=wt.getTransfer(s);if(n===$i)return i.UNSIGNED_BYTE;if(n===vu)return i.UNSIGNED_SHORT_4_4_4_4;if(n===_u)return i.UNSIGNED_SHORT_5_5_5_1;if(n===Cf)return i.UNSIGNED_INT_5_9_9_9_REV;if(n===Tf)return i.BYTE;if(n===Af)return i.SHORT;if(n===Ua)return i.UNSIGNED_SHORT;if(n===gu)return i.INT;if(n===Vs)return i.UNSIGNED_INT;if(n===Hi)return i.FLOAT;if(n===ka)return i.HALF_FLOAT;if(n===Rf)return i.ALPHA;if(n===Pf)return i.RGB;if(n===fi)return i.RGBA;if(n===Lf)return i.LUMINANCE;if(n===Df)return i.LUMINANCE_ALPHA;if(n===Nr)return i.DEPTH_COMPONENT;if(n===Gr)return i.DEPTH_STENCIL;if(n===If)return i.RED;if(n===xu)return i.RED_INTEGER;if(n===Uf)return i.RG;if(n===yu)return i.RG_INTEGER;if(n===bu)return i.RGBA_INTEGER;if(n===Lo||n===Do||n===Io||n===Uo)if(o===Bt)if(r=e.get("WEBGL_compressed_texture_s3tc_srgb"),r!==null){if(n===Lo)return r.COMPRESSED_SRGB_S3TC_DXT1_EXT;if(n===Do)return r.COMPRESSED_SRGB_ALPHA_S3TC_DXT1_EXT;if(n===Io)return r.COMPRESSED_SRGB_ALPHA_S3TC_DXT3_EXT;if(n===Uo)return r.COMPRESSED_SRGB_ALPHA_S3TC_DXT5_EXT}else return null;else if(r=e.get("WEBGL_compressed_texture_s3tc"),r!==null){if(n===Lo)return r.COMPRESSED_RGB_S3TC_DXT1_EXT;if(n===Do)return r.COMPRESSED_RGBA_S3TC_DXT1_EXT;if(n===Io)return r.COMPRESSED_RGBA_S3TC_DXT3_EXT;if(n===Uo)return r.COMPRESSED_RGBA_S3TC_DXT5_EXT}else return null;if(n===Ec||n===Tc||n===Ac||n===Cc)if(r=e.get("WEBGL_compressed_texture_pvrtc"),r!==null){if(n===Ec)return r.COMPRESSED_RGB_PVRTC_4BPPV1_IMG;if(n===Tc)return r.COMPRESSED_RGB_PVRTC_2BPPV1_IMG;if(n===Ac)return r.COMPRESSED_RGBA_PVRTC_4BPPV1_IMG;if(n===Cc)return r.COMPRESSED_RGBA_PVRTC_2BPPV1_IMG}else return null;if(n===Rc||n===Pc||n===Lc)if(r=e.get("WEBGL_compressed_texture_etc"),r!==null){if(n===Rc||n===Pc)return o===Bt?r.COMPRESSED_SRGB8_ETC2:r.COMPRESSED_RGB8_ETC2;if(n===Lc)return o===Bt?r.COMPRESSED_SRGB8_ALPHA8_ETC2_EAC:r.COMPRESSED_RGBA8_ETC2_EAC}else return null;if(n===Dc||n===Ic||n===Uc||n===Nc||n===Oc||n===Fc||n===kc||n===Bc||n===zc||n===Hc||n===Vc||n===Gc||n===Wc||n===qc)if(r=e.get("WEBGL_compressed_texture_astc"),r!==null){if(n===Dc)return o===Bt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_4x4_KHR:r.COMPRESSED_RGBA_ASTC_4x4_KHR;if(n===Ic)return o===Bt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_5x4_KHR:r.COMPRESSED_RGBA_ASTC_5x4_KHR;if(n===Uc)return o===Bt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_5x5_KHR:r.COMPRESSED_RGBA_ASTC_5x5_KHR;if(n===Nc)return o===Bt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_6x5_KHR:r.COMPRESSED_RGBA_ASTC_6x5_KHR;if(n===Oc)return o===Bt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_6x6_KHR:r.COMPRESSED_RGBA_ASTC_6x6_KHR;if(n===Fc)return o===Bt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_8x5_KHR:r.COMPRESSED_RGBA_ASTC_8x5_KHR;if(n===kc)return o===Bt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_8x6_KHR:r.COMPRESSED_RGBA_ASTC_8x6_KHR;if(n===Bc)return o===Bt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_8x8_KHR:r.COMPRESSED_RGBA_ASTC_8x8_KHR;if(n===zc)return o===Bt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_10x5_KHR:r.COMPRESSED_RGBA_ASTC_10x5_KHR;if(n===Hc)return o===Bt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_10x6_KHR:r.COMPRESSED_RGBA_ASTC_10x6_KHR;if(n===Vc)return o===Bt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_10x8_KHR:r.COMPRESSED_RGBA_ASTC_10x8_KHR;if(n===Gc)return o===Bt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_10x10_KHR:r.COMPRESSED_RGBA_ASTC_10x10_KHR;if(n===Wc)return o===Bt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_12x10_KHR:r.COMPRESSED_RGBA_ASTC_12x10_KHR;if(n===qc)return o===Bt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_12x12_KHR:r.COMPRESSED_RGBA_ASTC_12x12_KHR}else return null;if(n===No||n===Xc||n===$c)if(r=e.get("EXT_texture_compression_bptc"),r!==null){if(n===No)return o===Bt?r.COMPRESSED_SRGB_ALPHA_BPTC_UNORM_EXT:r.COMPRESSED_RGBA_BPTC_UNORM_EXT;if(n===Xc)return r.COMPRESSED_RGB_BPTC_SIGNED_FLOAT_EXT;if(n===$c)return r.COMPRESSED_RGB_BPTC_UNSIGNED_FLOAT_EXT}else return null;if(n===Nf||n===Yc||n===jc||n===Kc)if(r=e.get("EXT_texture_compression_rgtc"),r!==null){if(n===No)return r.COMPRESSED_RED_RGTC1_EXT;if(n===Yc)return r.COMPRESSED_SIGNED_RED_RGTC1_EXT;if(n===jc)return r.COMPRESSED_RED_GREEN_RGTC2_EXT;if(n===Kc)return r.COMPRESSED_SIGNED_RED_GREEN_RGTC2_EXT}else return null;return n===Vr?i.UNSIGNED_INT_24_8:i[n]!==void 0?i[n]:null}return{convert:t}}class Dy extends Sn{constructor(e=[]){super(),this.isArrayCamera=!0,this.cameras=e}}class vo extends tn{constructor(){super(),this.isGroup=!0,this.type="Group"}}const Iy={type:"move"};class tc{constructor(){this._targetRay=null,this._grip=null,this._hand=null}getHandSpace(){return this._hand===null&&(this._hand=new vo,this._hand.matrixAutoUpdate=!1,this._hand.visible=!1,this._hand.joints={},this._hand.inputState={pinching:!1}),this._hand}getTargetRaySpace(){return this._targetRay===null&&(this._targetRay=new vo,this._targetRay.matrixAutoUpdate=!1,this._targetRay.visible=!1,this._targetRay.hasLinearVelocity=!1,this._targetRay.linearVelocity=new G,this._targetRay.hasAngularVelocity=!1,this._targetRay.angularVelocity=new G),this._targetRay}getGripSpace(){return this._grip===null&&(this._grip=new vo,this._grip.matrixAutoUpdate=!1,this._grip.visible=!1,this._grip.hasLinearVelocity=!1,this._grip.linearVelocity=new G,this._grip.hasAngularVelocity=!1,this._grip.angularVelocity=new G),this._grip}dispatchEvent(e){return this._targetRay!==null&&this._targetRay.dispatchEvent(e),this._grip!==null&&this._grip.dispatchEvent(e),this._hand!==null&&this._hand.dispatchEvent(e),this}connect(e){if(e&&e.hand){const t=this._hand;if(t)for(const n of e.hand.values())this._getHandJoint(t,n)}return this.dispatchEvent({type:"connected",data:e}),this}disconnect(e){return this.dispatchEvent({type:"disconnected",data:e}),this._targetRay!==null&&(this._targetRay.visible=!1),this._grip!==null&&(this._grip.visible=!1),this._hand!==null&&(this._hand.visible=!1),this}update(e,t,n){let s=null,r=null,o=null;const a=this._targetRay,l=this._grip,c=this._hand;if(e&&t.session.visibilityState!=="visible-blurred"){if(c&&e.hand){o=!0;for(const g of e.hand.values()){const m=t.getJointPose(g,n),p=this._getHandJoint(c,g);m!==null&&(p.matrix.fromArray(m.transform.matrix),p.matrix.decompose(p.position,p.rotation,p.scale),p.matrixWorldNeedsUpdate=!0,p.jointRadius=m.radius),p.visible=m!==null}const u=c.joints["index-finger-tip"],h=c.joints["thumb-tip"],d=u.position.distanceTo(h.position),f=.02,v=.005;c.inputState.pinching&&d>f+v?(c.inputState.pinching=!1,this.dispatchEvent({type:"pinchend",handedness:e.handedness,target:this})):!c.inputState.pinching&&d<=f-v&&(c.inputState.pinching=!0,this.dispatchEvent({type:"pinchstart",handedness:e.handedness,target:this}))}else l!==null&&e.gripSpace&&(r=t.getPose(e.gripSpace,n),r!==null&&(l.matrix.fromArray(r.transform.matrix),l.matrix.decompose(l.position,l.rotation,l.scale),l.matrixWorldNeedsUpdate=!0,r.linearVelocity?(l.hasLinearVelocity=!0,l.linearVelocity.copy(r.linearVelocity)):l.hasLinearVelocity=!1,r.angularVelocity?(l.hasAngularVelocity=!0,l.angularVelocity.copy(r.angularVelocity)):l.hasAngularVelocity=!1));a!==null&&(s=t.getPose(e.targetRaySpace,n),s===null&&r!==null&&(s=r),s!==null&&(a.matrix.fromArray(s.transform.matrix),a.matrix.decompose(a.position,a.rotation,a.scale),a.matrixWorldNeedsUpdate=!0,s.linearVelocity?(a.hasLinearVelocity=!0,a.linearVelocity.copy(s.linearVelocity)):a.hasLinearVelocity=!1,s.angularVelocity?(a.hasAngularVelocity=!0,a.angularVelocity.copy(s.angularVelocity)):a.hasAngularVelocity=!1,this.dispatchEvent(Iy)))}return a!==null&&(a.visible=s!==null),l!==null&&(l.visible=r!==null),c!==null&&(c.visible=o!==null),this}_getHandJoint(e,t){if(e.joints[t.jointName]===void 0){const n=new vo;n.matrixAutoUpdate=!1,n.visible=!1,e.joints[t.jointName]=n,e.add(n)}return e.joints[t.jointName]}}const Uy=`
void main() {

	gl_Position = vec4( position, 1.0 );

}`,Ny=`
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

}`;class Oy{constructor(){this.texture=null,this.mesh=null,this.depthNear=0,this.depthFar=0}init(e,t,n){if(this.texture===null){const s=new Dn,r=e.properties.get(s);r.__webglTexture=t.texture,(t.depthNear!=n.depthNear||t.depthFar!=n.depthFar)&&(this.depthNear=t.depthNear,this.depthFar=t.depthFar),this.texture=s}}getMesh(e){if(this.texture!==null&&this.mesh===null){const t=e.cameras[0].viewport,n=new ds({vertexShader:Uy,fragmentShader:Ny,uniforms:{depthColor:{value:this.texture},depthWidth:{value:t.z},depthHeight:{value:t.w}}});this.mesh=new Pn(new al(20,20),n)}return this.mesh}reset(){this.texture=null,this.mesh=null}getDepthTexture(){return this.texture}}class Fy extends Kr{constructor(e,t){super();const n=this;let s=null,r=1,o=null,a="local-floor",l=1,c=null,u=null,h=null,d=null,f=null,v=null;const g=new Oy,m=t.getContextAttributes();let p=null,x=null;const b=[],w=[],O=new qe;let A=null;const L=new Sn;L.layers.enable(1),L.viewport=new en;const k=new Sn;k.layers.enable(2),k.viewport=new en;const E=[L,k],y=new Dy;y.layers.enable(1),y.layers.enable(2);let P=null,K=null;this.cameraAutoUpdate=!0,this.enabled=!1,this.isPresenting=!1,this.getController=function(ne){let ce=b[ne];return ce===void 0&&(ce=new tc,b[ne]=ce),ce.getTargetRaySpace()},this.getControllerGrip=function(ne){let ce=b[ne];return ce===void 0&&(ce=new tc,b[ne]=ce),ce.getGripSpace()},this.getHand=function(ne){let ce=b[ne];return ce===void 0&&(ce=new tc,b[ne]=ce),ce.getHandSpace()};function z(ne){const ce=w.indexOf(ne.inputSource);if(ce===-1)return;const be=b[ce];be!==void 0&&(be.update(ne.inputSource,ne.frame,c||o),be.dispatchEvent({type:ne.type,data:ne.inputSource}))}function Z(){s.removeEventListener("select",z),s.removeEventListener("selectstart",z),s.removeEventListener("selectend",z),s.removeEventListener("squeeze",z),s.removeEventListener("squeezestart",z),s.removeEventListener("squeezeend",z),s.removeEventListener("end",Z),s.removeEventListener("inputsourceschange",q);for(let ne=0;ne<b.length;ne++){const ce=w[ne];ce!==null&&(w[ne]=null,b[ne].disconnect(ce))}P=null,K=null,g.reset(),e.setRenderTarget(p),f=null,d=null,h=null,s=null,x=null,ye.stop(),n.isPresenting=!1,e.setPixelRatio(A),e.setSize(O.width,O.height,!1),n.dispatchEvent({type:"sessionend"})}this.setFramebufferScaleFactor=function(ne){r=ne,n.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change framebuffer scale while presenting.")},this.setReferenceSpaceType=function(ne){a=ne,n.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change reference space type while presenting.")},this.getReferenceSpace=function(){return c||o},this.setReferenceSpace=function(ne){c=ne},this.getBaseLayer=function(){return d!==null?d:f},this.getBinding=function(){return h},this.getFrame=function(){return v},this.getSession=function(){return s},this.setSession=async function(ne){if(s=ne,s!==null){if(p=e.getRenderTarget(),s.addEventListener("select",z),s.addEventListener("selectstart",z),s.addEventListener("selectend",z),s.addEventListener("squeeze",z),s.addEventListener("squeezestart",z),s.addEventListener("squeezeend",z),s.addEventListener("end",Z),s.addEventListener("inputsourceschange",q),m.xrCompatible!==!0&&await t.makeXRCompatible(),A=e.getPixelRatio(),e.getSize(O),s.renderState.layers===void 0){const ce={antialias:m.antialias,alpha:!0,depth:m.depth,stencil:m.stencil,framebufferScaleFactor:r};f=new XRWebGLLayer(s,t,ce),s.updateRenderState({baseLayer:f}),e.setPixelRatio(1),e.setSize(f.framebufferWidth,f.framebufferHeight,!1),x=new Gs(f.framebufferWidth,f.framebufferHeight,{format:fi,type:$i,colorSpace:e.outputColorSpace,stencilBuffer:m.stencil})}else{let ce=null,be=null,fe=null;m.depth&&(fe=m.stencil?t.DEPTH24_STENCIL8:t.DEPTH_COMPONENT24,ce=m.stencil?Gr:Nr,be=m.stencil?Vr:Vs);const ke={colorFormat:t.RGBA8,depthFormat:fe,scaleFactor:r};h=new XRWebGLBinding(s,t),d=h.createProjectionLayer(ke),s.updateRenderState({layers:[d]}),e.setPixelRatio(1),e.setSize(d.textureWidth,d.textureHeight,!1),x=new Gs(d.textureWidth,d.textureHeight,{format:fi,type:$i,depthTexture:new Yf(d.textureWidth,d.textureHeight,be,void 0,void 0,void 0,void 0,void 0,void 0,ce),stencilBuffer:m.stencil,colorSpace:e.outputColorSpace,samples:m.antialias?4:0,resolveDepthBuffer:d.ignoreDepthValues===!1})}x.isXRRenderTarget=!0,this.setFoveation(l),c=null,o=await s.requestReferenceSpace(a),ye.setContext(s),ye.start(),n.isPresenting=!0,n.dispatchEvent({type:"sessionstart"})}},this.getEnvironmentBlendMode=function(){if(s!==null)return s.environmentBlendMode},this.getDepthTexture=function(){return g.getDepthTexture()};function q(ne){for(let ce=0;ce<ne.removed.length;ce++){const be=ne.removed[ce],fe=w.indexOf(be);fe>=0&&(w[fe]=null,b[fe].disconnect(be))}for(let ce=0;ce<ne.added.length;ce++){const be=ne.added[ce];let fe=w.indexOf(be);if(fe===-1){for(let Ve=0;Ve<b.length;Ve++)if(Ve>=w.length){w.push(be),fe=Ve;break}else if(w[Ve]===null){w[Ve]=be,fe=Ve;break}if(fe===-1)break}const ke=b[fe];ke&&ke.connect(be)}}const Q=new G,$=new G;function te(ne,ce,be){Q.setFromMatrixPosition(ce.matrixWorld),$.setFromMatrixPosition(be.matrixWorld);const fe=Q.distanceTo($),ke=ce.projectionMatrix.elements,Ve=be.projectionMatrix.elements,Ne=ke[14]/(ke[10]-1),pt=ke[14]/(ke[10]+1),N=(ke[9]+1)/ke[5],dt=(ke[9]-1)/ke[5],it=(ke[8]-1)/ke[0],ct=(Ve[8]+1)/Ve[0],Oe=Ne*it,Et=Ne*ct,Xe=fe/(-it+ct),We=Xe*-it;if(ce.matrixWorld.decompose(ne.position,ne.quaternion,ne.scale),ne.translateX(We),ne.translateZ(Xe),ne.matrixWorld.compose(ne.position,ne.quaternion,ne.scale),ne.matrixWorldInverse.copy(ne.matrixWorld).invert(),ke[10]===-1)ne.projectionMatrix.copy(ce.projectionMatrix),ne.projectionMatrixInverse.copy(ce.projectionMatrixInverse);else{const I=Ne+Xe,M=pt+Xe,J=Oe-We,oe=Et+(fe-We),ee=N*pt/M*I,W=dt*pt/M*I;ne.projectionMatrix.makePerspective(J,oe,ee,W,I,M),ne.projectionMatrixInverse.copy(ne.projectionMatrix).invert()}}function ge(ne,ce){ce===null?ne.matrixWorld.copy(ne.matrix):ne.matrixWorld.multiplyMatrices(ce.matrixWorld,ne.matrix),ne.matrixWorldInverse.copy(ne.matrixWorld).invert()}this.updateCamera=function(ne){if(s===null)return;let ce=ne.near,be=ne.far;g.texture!==null&&(g.depthNear>0&&(ce=g.depthNear),g.depthFar>0&&(be=g.depthFar)),y.near=k.near=L.near=ce,y.far=k.far=L.far=be,(P!==y.near||K!==y.far)&&(s.updateRenderState({depthNear:y.near,depthFar:y.far}),P=y.near,K=y.far);const fe=ne.parent,ke=y.cameras;ge(y,fe);for(let Ve=0;Ve<ke.length;Ve++)ge(ke[Ve],fe);ke.length===2?te(y,L,k):y.projectionMatrix.copy(L.projectionMatrix),de(ne,y,fe)};function de(ne,ce,be){be===null?ne.matrix.copy(ce.matrixWorld):(ne.matrix.copy(be.matrixWorld),ne.matrix.invert(),ne.matrix.multiply(ce.matrixWorld)),ne.matrix.decompose(ne.position,ne.quaternion,ne.scale),ne.updateMatrixWorld(!0),ne.projectionMatrix.copy(ce.projectionMatrix),ne.projectionMatrixInverse.copy(ce.projectionMatrixInverse),ne.isPerspectiveCamera&&(ne.fov=Na*2*Math.atan(1/ne.projectionMatrix.elements[5]),ne.zoom=1)}this.getCamera=function(){return y},this.getFoveation=function(){if(!(d===null&&f===null))return l},this.setFoveation=function(ne){l=ne,d!==null&&(d.fixedFoveation=ne),f!==null&&f.fixedFoveation!==void 0&&(f.fixedFoveation=ne)},this.hasDepthSensing=function(){return g.texture!==null},this.getDepthSensingMesh=function(){return g.getMesh(y)};let xe=null;function Ee(ne,ce){if(u=ce.getViewerPose(c||o),v=ce,u!==null){const be=u.views;f!==null&&(e.setRenderTargetFramebuffer(x,f.framebuffer),e.setRenderTarget(x));let fe=!1;be.length!==y.cameras.length&&(y.cameras.length=0,fe=!0);for(let Ve=0;Ve<be.length;Ve++){const Ne=be[Ve];let pt=null;if(f!==null)pt=f.getViewport(Ne);else{const dt=h.getViewSubImage(d,Ne);pt=dt.viewport,Ve===0&&(e.setRenderTargetTextures(x,dt.colorTexture,d.ignoreDepthValues?void 0:dt.depthStencilTexture),e.setRenderTarget(x))}let N=E[Ve];N===void 0&&(N=new Sn,N.layers.enable(Ve),N.viewport=new en,E[Ve]=N),N.matrix.fromArray(Ne.transform.matrix),N.matrix.decompose(N.position,N.quaternion,N.scale),N.projectionMatrix.fromArray(Ne.projectionMatrix),N.projectionMatrixInverse.copy(N.projectionMatrix).invert(),N.viewport.set(pt.x,pt.y,pt.width,pt.height),Ve===0&&(y.matrix.copy(N.matrix),y.matrix.decompose(y.position,y.quaternion,y.scale)),fe===!0&&y.cameras.push(N)}const ke=s.enabledFeatures;if(ke&&ke.includes("depth-sensing")){const Ve=h.getDepthInformation(be[0]);Ve&&Ve.isValid&&Ve.texture&&g.init(e,Ve,s.renderState)}}for(let be=0;be<b.length;be++){const fe=w[be],ke=b[be];fe!==null&&ke!==void 0&&ke.update(fe,ce,c||o)}xe&&xe(ne,ce),ce.detectedPlanes&&n.dispatchEvent({type:"planesdetected",data:ce}),v=null}const ye=new $f;ye.setAnimationLoop(Ee),this.setAnimationLoop=function(ne){xe=ne},this.dispose=function(){}}}const Ls=new Ai,ky=new Gt;function By(i,e){function t(m,p){m.matrixAutoUpdate===!0&&m.updateMatrix(),p.value.copy(m.matrix)}function n(m,p){p.color.getRGB(m.fogColor.value,Wf(i)),p.isFog?(m.fogNear.value=p.near,m.fogFar.value=p.far):p.isFogExp2&&(m.fogDensity.value=p.density)}function s(m,p,x,b,w){p.isMeshBasicMaterial||p.isMeshLambertMaterial?r(m,p):p.isMeshToonMaterial?(r(m,p),h(m,p)):p.isMeshPhongMaterial?(r(m,p),u(m,p)):p.isMeshStandardMaterial?(r(m,p),d(m,p),p.isMeshPhysicalMaterial&&f(m,p,w)):p.isMeshMatcapMaterial?(r(m,p),v(m,p)):p.isMeshDepthMaterial?r(m,p):p.isMeshDistanceMaterial?(r(m,p),g(m,p)):p.isMeshNormalMaterial?r(m,p):p.isLineBasicMaterial?(o(m,p),p.isLineDashedMaterial&&a(m,p)):p.isPointsMaterial?l(m,p,x,b):p.isSpriteMaterial?c(m,p):p.isShadowMaterial?(m.color.value.copy(p.color),m.opacity.value=p.opacity):p.isShaderMaterial&&(p.uniformsNeedUpdate=!1)}function r(m,p){m.opacity.value=p.opacity,p.color&&m.diffuse.value.copy(p.color),p.emissive&&m.emissive.value.copy(p.emissive).multiplyScalar(p.emissiveIntensity),p.map&&(m.map.value=p.map,t(p.map,m.mapTransform)),p.alphaMap&&(m.alphaMap.value=p.alphaMap,t(p.alphaMap,m.alphaMapTransform)),p.bumpMap&&(m.bumpMap.value=p.bumpMap,t(p.bumpMap,m.bumpMapTransform),m.bumpScale.value=p.bumpScale,p.side===Nn&&(m.bumpScale.value*=-1)),p.normalMap&&(m.normalMap.value=p.normalMap,t(p.normalMap,m.normalMapTransform),m.normalScale.value.copy(p.normalScale),p.side===Nn&&m.normalScale.value.negate()),p.displacementMap&&(m.displacementMap.value=p.displacementMap,t(p.displacementMap,m.displacementMapTransform),m.displacementScale.value=p.displacementScale,m.displacementBias.value=p.displacementBias),p.emissiveMap&&(m.emissiveMap.value=p.emissiveMap,t(p.emissiveMap,m.emissiveMapTransform)),p.specularMap&&(m.specularMap.value=p.specularMap,t(p.specularMap,m.specularMapTransform)),p.alphaTest>0&&(m.alphaTest.value=p.alphaTest);const x=e.get(p),b=x.envMap,w=x.envMapRotation;b&&(m.envMap.value=b,Ls.copy(w),Ls.x*=-1,Ls.y*=-1,Ls.z*=-1,b.isCubeTexture&&b.isRenderTargetTexture===!1&&(Ls.y*=-1,Ls.z*=-1),m.envMapRotation.value.setFromMatrix4(ky.makeRotationFromEuler(Ls)),m.flipEnvMap.value=b.isCubeTexture&&b.isRenderTargetTexture===!1?-1:1,m.reflectivity.value=p.reflectivity,m.ior.value=p.ior,m.refractionRatio.value=p.refractionRatio),p.lightMap&&(m.lightMap.value=p.lightMap,m.lightMapIntensity.value=p.lightMapIntensity,t(p.lightMap,m.lightMapTransform)),p.aoMap&&(m.aoMap.value=p.aoMap,m.aoMapIntensity.value=p.aoMapIntensity,t(p.aoMap,m.aoMapTransform))}function o(m,p){m.diffuse.value.copy(p.color),m.opacity.value=p.opacity,p.map&&(m.map.value=p.map,t(p.map,m.mapTransform))}function a(m,p){m.dashSize.value=p.dashSize,m.totalSize.value=p.dashSize+p.gapSize,m.scale.value=p.scale}function l(m,p,x,b){m.diffuse.value.copy(p.color),m.opacity.value=p.opacity,m.size.value=p.size*x,m.scale.value=b*.5,p.map&&(m.map.value=p.map,t(p.map,m.uvTransform)),p.alphaMap&&(m.alphaMap.value=p.alphaMap,t(p.alphaMap,m.alphaMapTransform)),p.alphaTest>0&&(m.alphaTest.value=p.alphaTest)}function c(m,p){m.diffuse.value.copy(p.color),m.opacity.value=p.opacity,m.rotation.value=p.rotation,p.map&&(m.map.value=p.map,t(p.map,m.mapTransform)),p.alphaMap&&(m.alphaMap.value=p.alphaMap,t(p.alphaMap,m.alphaMapTransform)),p.alphaTest>0&&(m.alphaTest.value=p.alphaTest)}function u(m,p){m.specular.value.copy(p.specular),m.shininess.value=Math.max(p.shininess,1e-4)}function h(m,p){p.gradientMap&&(m.gradientMap.value=p.gradientMap)}function d(m,p){m.metalness.value=p.metalness,p.metalnessMap&&(m.metalnessMap.value=p.metalnessMap,t(p.metalnessMap,m.metalnessMapTransform)),m.roughness.value=p.roughness,p.roughnessMap&&(m.roughnessMap.value=p.roughnessMap,t(p.roughnessMap,m.roughnessMapTransform)),p.envMap&&(m.envMapIntensity.value=p.envMapIntensity)}function f(m,p,x){m.ior.value=p.ior,p.sheen>0&&(m.sheenColor.value.copy(p.sheenColor).multiplyScalar(p.sheen),m.sheenRoughness.value=p.sheenRoughness,p.sheenColorMap&&(m.sheenColorMap.value=p.sheenColorMap,t(p.sheenColorMap,m.sheenColorMapTransform)),p.sheenRoughnessMap&&(m.sheenRoughnessMap.value=p.sheenRoughnessMap,t(p.sheenRoughnessMap,m.sheenRoughnessMapTransform))),p.clearcoat>0&&(m.clearcoat.value=p.clearcoat,m.clearcoatRoughness.value=p.clearcoatRoughness,p.clearcoatMap&&(m.clearcoatMap.value=p.clearcoatMap,t(p.clearcoatMap,m.clearcoatMapTransform)),p.clearcoatRoughnessMap&&(m.clearcoatRoughnessMap.value=p.clearcoatRoughnessMap,t(p.clearcoatRoughnessMap,m.clearcoatRoughnessMapTransform)),p.clearcoatNormalMap&&(m.clearcoatNormalMap.value=p.clearcoatNormalMap,t(p.clearcoatNormalMap,m.clearcoatNormalMapTransform),m.clearcoatNormalScale.value.copy(p.clearcoatNormalScale),p.side===Nn&&m.clearcoatNormalScale.value.negate())),p.dispersion>0&&(m.dispersion.value=p.dispersion),p.iridescence>0&&(m.iridescence.value=p.iridescence,m.iridescenceIOR.value=p.iridescenceIOR,m.iridescenceThicknessMinimum.value=p.iridescenceThicknessRange[0],m.iridescenceThicknessMaximum.value=p.iridescenceThicknessRange[1],p.iridescenceMap&&(m.iridescenceMap.value=p.iridescenceMap,t(p.iridescenceMap,m.iridescenceMapTransform)),p.iridescenceThicknessMap&&(m.iridescenceThicknessMap.value=p.iridescenceThicknessMap,t(p.iridescenceThicknessMap,m.iridescenceThicknessMapTransform))),p.transmission>0&&(m.transmission.value=p.transmission,m.transmissionSamplerMap.value=x.texture,m.transmissionSamplerSize.value.set(x.width,x.height),p.transmissionMap&&(m.transmissionMap.value=p.transmissionMap,t(p.transmissionMap,m.transmissionMapTransform)),m.thickness.value=p.thickness,p.thicknessMap&&(m.thicknessMap.value=p.thicknessMap,t(p.thicknessMap,m.thicknessMapTransform)),m.attenuationDistance.value=p.attenuationDistance,m.attenuationColor.value.copy(p.attenuationColor)),p.anisotropy>0&&(m.anisotropyVector.value.set(p.anisotropy*Math.cos(p.anisotropyRotation),p.anisotropy*Math.sin(p.anisotropyRotation)),p.anisotropyMap&&(m.anisotropyMap.value=p.anisotropyMap,t(p.anisotropyMap,m.anisotropyMapTransform))),m.specularIntensity.value=p.specularIntensity,m.specularColor.value.copy(p.specularColor),p.specularColorMap&&(m.specularColorMap.value=p.specularColorMap,t(p.specularColorMap,m.specularColorMapTransform)),p.specularIntensityMap&&(m.specularIntensityMap.value=p.specularIntensityMap,t(p.specularIntensityMap,m.specularIntensityMapTransform))}function v(m,p){p.matcap&&(m.matcap.value=p.matcap)}function g(m,p){const x=e.get(p).light;m.referencePosition.value.setFromMatrixPosition(x.matrixWorld),m.nearDistance.value=x.shadow.camera.near,m.farDistance.value=x.shadow.camera.far}return{refreshFogUniforms:n,refreshMaterialUniforms:s}}function zy(i,e,t,n){let s={},r={},o=[];const a=i.getParameter(i.MAX_UNIFORM_BUFFER_BINDINGS);function l(x,b){const w=b.program;n.uniformBlockBinding(x,w)}function c(x,b){let w=s[x.id];w===void 0&&(v(x),w=u(x),s[x.id]=w,x.addEventListener("dispose",m));const O=b.program;n.updateUBOMapping(x,O);const A=e.render.frame;r[x.id]!==A&&(d(x),r[x.id]=A)}function u(x){const b=h();x.__bindingPointIndex=b;const w=i.createBuffer(),O=x.__size,A=x.usage;return i.bindBuffer(i.UNIFORM_BUFFER,w),i.bufferData(i.UNIFORM_BUFFER,O,A),i.bindBuffer(i.UNIFORM_BUFFER,null),i.bindBufferBase(i.UNIFORM_BUFFER,b,w),w}function h(){for(let x=0;x<a;x++)if(o.indexOf(x)===-1)return o.push(x),x;return console.error("THREE.WebGLRenderer: Maximum number of simultaneously usable uniforms groups reached."),0}function d(x){const b=s[x.id],w=x.uniforms,O=x.__cache;i.bindBuffer(i.UNIFORM_BUFFER,b);for(let A=0,L=w.length;A<L;A++){const k=Array.isArray(w[A])?w[A]:[w[A]];for(let E=0,y=k.length;E<y;E++){const P=k[E];if(f(P,A,E,O)===!0){const K=P.__offset,z=Array.isArray(P.value)?P.value:[P.value];let Z=0;for(let q=0;q<z.length;q++){const Q=z[q],$=g(Q);typeof Q=="number"||typeof Q=="boolean"?(P.__data[0]=Q,i.bufferSubData(i.UNIFORM_BUFFER,K+Z,P.__data)):Q.isMatrix3?(P.__data[0]=Q.elements[0],P.__data[1]=Q.elements[1],P.__data[2]=Q.elements[2],P.__data[3]=0,P.__data[4]=Q.elements[3],P.__data[5]=Q.elements[4],P.__data[6]=Q.elements[5],P.__data[7]=0,P.__data[8]=Q.elements[6],P.__data[9]=Q.elements[7],P.__data[10]=Q.elements[8],P.__data[11]=0):(Q.toArray(P.__data,Z),Z+=$.storage/Float32Array.BYTES_PER_ELEMENT)}i.bufferSubData(i.UNIFORM_BUFFER,K,P.__data)}}}i.bindBuffer(i.UNIFORM_BUFFER,null)}function f(x,b,w,O){const A=x.value,L=b+"_"+w;if(O[L]===void 0)return typeof A=="number"||typeof A=="boolean"?O[L]=A:O[L]=A.clone(),!0;{const k=O[L];if(typeof A=="number"||typeof A=="boolean"){if(k!==A)return O[L]=A,!0}else if(k.equals(A)===!1)return k.copy(A),!0}return!1}function v(x){const b=x.uniforms;let w=0;const O=16;for(let L=0,k=b.length;L<k;L++){const E=Array.isArray(b[L])?b[L]:[b[L]];for(let y=0,P=E.length;y<P;y++){const K=E[y],z=Array.isArray(K.value)?K.value:[K.value];for(let Z=0,q=z.length;Z<q;Z++){const Q=z[Z],$=g(Q),te=w%O,ge=te%$.boundary,de=te+ge;w+=ge,de!==0&&O-de<$.storage&&(w+=O-de),K.__data=new Float32Array($.storage/Float32Array.BYTES_PER_ELEMENT),K.__offset=w,w+=$.storage}}}const A=w%O;return A>0&&(w+=O-A),x.__size=w,x.__cache={},this}function g(x){const b={boundary:0,storage:0};return typeof x=="number"||typeof x=="boolean"?(b.boundary=4,b.storage=4):x.isVector2?(b.boundary=8,b.storage=8):x.isVector3||x.isColor?(b.boundary=16,b.storage=12):x.isVector4?(b.boundary=16,b.storage=16):x.isMatrix3?(b.boundary=48,b.storage=48):x.isMatrix4?(b.boundary=64,b.storage=64):x.isTexture?console.warn("THREE.WebGLRenderer: Texture samplers can not be part of an uniforms group."):console.warn("THREE.WebGLRenderer: Unsupported uniform value type.",x),b}function m(x){const b=x.target;b.removeEventListener("dispose",m);const w=o.indexOf(b.__bindingPointIndex);o.splice(w,1),i.deleteBuffer(s[b.id]),delete s[b.id],delete r[b.id]}function p(){for(const x in s)i.deleteBuffer(s[x]);o=[],s={},r={}}return{bind:l,update:c,dispose:p}}class Hy{constructor(e={}){const{canvas:t=Lg(),context:n=null,depth:s=!0,stencil:r=!1,alpha:o=!1,antialias:a=!1,premultipliedAlpha:l=!0,preserveDrawingBuffer:c=!1,powerPreference:u="default",failIfMajorPerformanceCaveat:h=!1}=e;this.isWebGLRenderer=!0;let d;if(n!==null){if(typeof WebGLRenderingContext<"u"&&n instanceof WebGLRenderingContext)throw new Error("THREE.WebGLRenderer: WebGL 1 is not supported since r163.");d=n.getContextAttributes().alpha}else d=o;const f=new Uint32Array(4),v=new Int32Array(4);let g=null,m=null;const p=[],x=[];this.domElement=t,this.debug={checkShaderErrors:!0,onShaderError:null},this.autoClear=!0,this.autoClearColor=!0,this.autoClearDepth=!0,this.autoClearStencil=!0,this.sortObjects=!0,this.clippingPlanes=[],this.localClippingEnabled=!1,this._outputColorSpace=Mi,this.toneMapping=cs,this.toneMappingExposure=1;const b=this;let w=!1,O=0,A=0,L=null,k=-1,E=null;const y=new en,P=new en;let K=null;const z=new st(0);let Z=0,q=t.width,Q=t.height,$=1,te=null,ge=null;const de=new en(0,0,q,Q),xe=new en(0,0,q,Q);let Ee=!1;const ye=new Eu;let ne=!1,ce=!1;const be=new Gt,fe=new G,ke=new en,Ve={background:null,fog:null,environment:null,overrideMaterial:null,isScene:!0};let Ne=!1;function pt(){return L===null?$:1}let N=n;function dt(T,V){return t.getContext(T,V)}try{const T={alpha:!0,depth:s,stencil:r,antialias:a,premultipliedAlpha:l,preserveDrawingBuffer:c,powerPreference:u,failIfMajorPerformanceCaveat:h};if("setAttribute"in t&&t.setAttribute("data-engine",`three.js r${mu}`),t.addEventListener("webglcontextlost",ie,!1),t.addEventListener("webglcontextrestored",se,!1),t.addEventListener("webglcontextcreationerror",_e,!1),N===null){const V="webgl2";if(N=dt(V,T),N===null)throw dt(V)?new Error("Error creating WebGL context with your selected attributes."):new Error("Error creating WebGL context.")}}catch(T){throw console.error("THREE.WebGLRenderer: "+T.message),T}let it,ct,Oe,Et,Xe,We,I,M,J,oe,ee,W,we,ve,Ae,Ke,me,Te,Ze,Be,Me,ze,F,le;function U(){it=new $0(N),it.init(),ze=new Ly(N,it),ct=new H0(N,it,e,ze),Oe=new Cy(N),Et=new K0(N),Xe=new py,We=new Py(N,it,Oe,Xe,ct,ze,Et),I=new G0(b),M=new X0(b),J=new iv(N),F=new B0(N,J),oe=new Y0(N,J,Et,F),ee=new J0(N,oe,J,Et),Ze=new Z0(N,ct,We),Ke=new V0(Xe),W=new fy(b,I,M,it,ct,F,Ke),we=new By(b,Xe),ve=new gy,Ae=new Sy(it),Te=new k0(b,I,M,Oe,ee,d,l),me=new Ay(b,ee,ct),le=new zy(N,Et,ct,Oe),Be=new z0(N,it,Et),Me=new j0(N,it,Et),Et.programs=W.programs,b.capabilities=ct,b.extensions=it,b.properties=Xe,b.renderLists=ve,b.shadowMap=me,b.state=Oe,b.info=Et}U();const re=new Fy(b,N);this.xr=re,this.getContext=function(){return N},this.getContextAttributes=function(){return N.getContextAttributes()},this.forceContextLoss=function(){const T=it.get("WEBGL_lose_context");T&&T.loseContext()},this.forceContextRestore=function(){const T=it.get("WEBGL_lose_context");T&&T.restoreContext()},this.getPixelRatio=function(){return $},this.setPixelRatio=function(T){T!==void 0&&($=T,this.setSize(q,Q,!1))},this.getSize=function(T){return T.set(q,Q)},this.setSize=function(T,V,j=!0){if(re.isPresenting){console.warn("THREE.WebGLRenderer: Can't change size while VR device is presenting.");return}q=T,Q=V,t.width=Math.floor(T*$),t.height=Math.floor(V*$),j===!0&&(t.style.width=T+"px",t.style.height=V+"px"),this.setViewport(0,0,T,V)},this.getDrawingBufferSize=function(T){return T.set(q*$,Q*$).floor()},this.setDrawingBufferSize=function(T,V,j){q=T,Q=V,$=j,t.width=Math.floor(T*j),t.height=Math.floor(V*j),this.setViewport(0,0,T,V)},this.getCurrentViewport=function(T){return T.copy(y)},this.getViewport=function(T){return T.copy(de)},this.setViewport=function(T,V,j,X){T.isVector4?de.set(T.x,T.y,T.z,T.w):de.set(T,V,j,X),Oe.viewport(y.copy(de).multiplyScalar($).round())},this.getScissor=function(T){return T.copy(xe)},this.setScissor=function(T,V,j,X){T.isVector4?xe.set(T.x,T.y,T.z,T.w):xe.set(T,V,j,X),Oe.scissor(P.copy(xe).multiplyScalar($).round())},this.getScissorTest=function(){return Ee},this.setScissorTest=function(T){Oe.setScissorTest(Ee=T)},this.setOpaqueSort=function(T){te=T},this.setTransparentSort=function(T){ge=T},this.getClearColor=function(T){return T.copy(Te.getClearColor())},this.setClearColor=function(){Te.setClearColor.apply(Te,arguments)},this.getClearAlpha=function(){return Te.getClearAlpha()},this.setClearAlpha=function(){Te.setClearAlpha.apply(Te,arguments)},this.clear=function(T=!0,V=!0,j=!0){let X=0;if(T){let H=!1;if(L!==null){const ue=L.texture.format;H=ue===bu||ue===yu||ue===xu}if(H){const ue=L.texture.type,Re=ue===$i||ue===Vs||ue===Ua||ue===Vr||ue===vu||ue===_u,Pe=Te.getClearColor(),Ie=Te.getClearAlpha(),Je=Pe.r,Qe=Pe.g,Fe=Pe.b;Re?(f[0]=Je,f[1]=Qe,f[2]=Fe,f[3]=Ie,N.clearBufferuiv(N.COLOR,0,f)):(v[0]=Je,v[1]=Qe,v[2]=Fe,v[3]=Ie,N.clearBufferiv(N.COLOR,0,v))}else X|=N.COLOR_BUFFER_BIT}V&&(X|=N.DEPTH_BUFFER_BIT),j&&(X|=N.STENCIL_BUFFER_BIT,this.state.buffers.stencil.setMask(4294967295)),N.clear(X)},this.clearColor=function(){this.clear(!0,!1,!1)},this.clearDepth=function(){this.clear(!1,!0,!1)},this.clearStencil=function(){this.clear(!1,!1,!0)},this.dispose=function(){t.removeEventListener("webglcontextlost",ie,!1),t.removeEventListener("webglcontextrestored",se,!1),t.removeEventListener("webglcontextcreationerror",_e,!1),ve.dispose(),Ae.dispose(),Xe.dispose(),I.dispose(),M.dispose(),ee.dispose(),F.dispose(),le.dispose(),W.dispose(),re.dispose(),re.removeEventListener("sessionstart",zt),re.removeEventListener("sessionend",Ht),an.stop()};function ie(T){T.preventDefault(),console.log("THREE.WebGLRenderer: Context Lost."),w=!0}function se(){console.log("THREE.WebGLRenderer: Context Restored."),w=!1;const T=Et.autoReset,V=me.enabled,j=me.autoUpdate,X=me.needsUpdate,H=me.type;U(),Et.autoReset=T,me.enabled=V,me.autoUpdate=j,me.needsUpdate=X,me.type=H}function _e(T){console.error("THREE.WebGLRenderer: A WebGL context could not be created. Reason: ",T.statusMessage)}function je(T){const V=T.target;V.removeEventListener("dispose",je),ot(V)}function ot(T){vt(T),Xe.remove(T)}function vt(T){const V=Xe.get(T).programs;V!==void 0&&(V.forEach(function(j){W.releaseProgram(j)}),T.isShaderMaterial&&W.releaseShaderCache(T))}this.renderBufferDirect=function(T,V,j,X,H,ue){V===null&&(V=Ve);const Re=H.isMesh&&H.matrixWorld.determinant()<0,Pe=gl(T,V,j,X,H);Oe.setMaterial(X,Re);let Ie=j.index,Je=1;if(X.wireframe===!0){if(Ie=oe.getWireframeAttribute(j),Ie===void 0)return;Je=2}const Qe=j.drawRange,Fe=j.attributes.position;let ut=Qe.start*Je,Dt=(Qe.start+Qe.count)*Je;ue!==null&&(ut=Math.max(ut,ue.start*Je),Dt=Math.min(Dt,(ue.start+ue.count)*Je)),Ie!==null?(ut=Math.max(ut,0),Dt=Math.min(Dt,Ie.count)):Fe!=null&&(ut=Math.max(ut,0),Dt=Math.min(Dt,Fe.count));const It=Dt-ut;if(It<0||It===1/0)return;F.setup(H,X,Pe,j,Ie);let pn,mt=Be;if(Ie!==null&&(pn=J.get(Ie),mt=Me,mt.setIndex(pn)),H.isMesh)X.wireframe===!0?(Oe.setLineWidth(X.wireframeLinewidth*pt()),mt.setMode(N.LINES)):mt.setMode(N.TRIANGLES);else if(H.isLine){let He=X.linewidth;He===void 0&&(He=1),Oe.setLineWidth(He*pt()),H.isLineSegments?mt.setMode(N.LINES):H.isLineLoop?mt.setMode(N.LINE_LOOP):mt.setMode(N.LINE_STRIP)}else H.isPoints?mt.setMode(N.POINTS):H.isSprite&&mt.setMode(N.TRIANGLES);if(H.isBatchedMesh)if(H._multiDrawInstances!==null)mt.renderMultiDrawInstances(H._multiDrawStarts,H._multiDrawCounts,H._multiDrawCount,H._multiDrawInstances);else if(it.get("WEBGL_multi_draw"))mt.renderMultiDraw(H._multiDrawStarts,H._multiDrawCounts,H._multiDrawCount);else{const He=H._multiDrawStarts,$t=H._multiDrawCounts,gt=H._multiDrawCount,Ut=Ie?J.get(Ie).bytesPerElement:1,Di=Xe.get(X).currentProgram.getUniforms();for(let _n=0;_n<gt;_n++)Di.setValue(N,"_gl_DrawID",_n),mt.render(He[_n]/Ut,$t[_n])}else if(H.isInstancedMesh)mt.renderInstances(ut,It,H.count);else if(j.isInstancedBufferGeometry){const He=j._maxInstanceCount!==void 0?j._maxInstanceCount:1/0,$t=Math.min(j.instanceCount,He);mt.renderInstances(ut,It,$t)}else mt.render(ut,It)};function Tt(T,V,j){T.transparent===!0&&T.side===Ei&&T.forceSinglePass===!1?(T.side=Nn,T.needsUpdate=!0,bs(T,V,j),T.side=hs,T.needsUpdate=!0,bs(T,V,j),T.side=Ei):bs(T,V,j)}this.compile=function(T,V,j=null){j===null&&(j=T),m=Ae.get(j),m.init(V),x.push(m),j.traverseVisible(function(H){H.isLight&&H.layers.test(V.layers)&&(m.pushLight(H),H.castShadow&&m.pushShadow(H))}),T!==j&&T.traverseVisible(function(H){H.isLight&&H.layers.test(V.layers)&&(m.pushLight(H),H.castShadow&&m.pushShadow(H))}),m.setupLights();const X=new Set;return T.traverse(function(H){const ue=H.material;if(ue)if(Array.isArray(ue))for(let Re=0;Re<ue.length;Re++){const Pe=ue[Re];Tt(Pe,j,H),X.add(Pe)}else Tt(ue,j,H),X.add(ue)}),x.pop(),m=null,X},this.compileAsync=function(T,V,j=null){const X=this.compile(T,V,j);return new Promise(H=>{function ue(){if(X.forEach(function(Re){Xe.get(Re).currentProgram.isReady()&&X.delete(Re)}),X.size===0){H(T);return}setTimeout(ue,10)}it.get("KHR_parallel_shader_compile")!==null?ue():setTimeout(ue,10)})};let lt=null;function fn(T){lt&&lt(T)}function zt(){an.stop()}function Ht(){an.start()}const an=new $f;an.setAnimationLoop(fn),typeof self<"u"&&an.setContext(self),this.setAnimationLoop=function(T){lt=T,re.setAnimationLoop(T),T===null?an.stop():an.start()},re.addEventListener("sessionstart",zt),re.addEventListener("sessionend",Ht),this.render=function(T,V){if(V!==void 0&&V.isCamera!==!0){console.error("THREE.WebGLRenderer.render: camera is not an instance of THREE.Camera.");return}if(w===!0)return;if(T.matrixWorldAutoUpdate===!0&&T.updateMatrixWorld(),V.parent===null&&V.matrixWorldAutoUpdate===!0&&V.updateMatrixWorld(),re.enabled===!0&&re.isPresenting===!0&&(re.cameraAutoUpdate===!0&&re.updateCamera(V),V=re.getCamera()),T.isScene===!0&&T.onBeforeRender(b,T,V,L),m=Ae.get(T,x.length),m.init(V),x.push(m),be.multiplyMatrices(V.projectionMatrix,V.matrixWorldInverse),ye.setFromProjectionMatrix(be),ce=this.localClippingEnabled,ne=Ke.init(this.clippingPlanes,ce),g=ve.get(T,p.length),g.init(),p.push(g),re.enabled===!0&&re.isPresenting===!0){const ue=b.xr.getDepthSensingMesh();ue!==null&&gi(ue,V,-1/0,b.sortObjects)}gi(T,V,0,b.sortObjects),g.finish(),b.sortObjects===!0&&g.sort(te,ge),Ne=re.enabled===!1||re.isPresenting===!1||re.hasDepthSensing()===!1,Ne&&Te.addToRenderList(g,T),this.info.render.frame++,ne===!0&&Ke.beginShadows();const j=m.state.shadowsArray;me.render(j,T,V),ne===!0&&Ke.endShadows(),this.info.autoReset===!0&&this.info.reset();const X=g.opaque,H=g.transmissive;if(m.setupLights(),V.isArrayCamera){const ue=V.cameras;if(H.length>0)for(let Re=0,Pe=ue.length;Re<Pe;Re++){const Ie=ue[Re];wn(X,H,T,Ie)}Ne&&Te.render(T);for(let Re=0,Pe=ue.length;Re<Pe;Re++){const Ie=ue[Re];Ri(g,T,Ie,Ie.viewport)}}else H.length>0&&wn(X,H,T,V),Ne&&Te.render(T),Ri(g,T,V);L!==null&&(We.updateMultisampleRenderTarget(L),We.updateRenderTargetMipmap(L)),T.isScene===!0&&T.onAfterRender(b,T,V),F.resetDefaultState(),k=-1,E=null,x.pop(),x.length>0?(m=x[x.length-1],ne===!0&&Ke.setGlobalState(b.clippingPlanes,m.state.camera)):m=null,p.pop(),p.length>0?g=p[p.length-1]:g=null};function gi(T,V,j,X){if(T.visible===!1)return;if(T.layers.test(V.layers)){if(T.isGroup)j=T.renderOrder;else if(T.isLOD)T.autoUpdate===!0&&T.update(V);else if(T.isLight)m.pushLight(T),T.castShadow&&m.pushShadow(T);else if(T.isSprite){if(!T.frustumCulled||ye.intersectsSprite(T)){X&&ke.setFromMatrixPosition(T.matrixWorld).applyMatrix4(be);const Re=ee.update(T),Pe=T.material;Pe.visible&&g.push(T,Re,Pe,j,ke.z,null)}}else if((T.isMesh||T.isLine||T.isPoints)&&(!T.frustumCulled||ye.intersectsObject(T))){const Re=ee.update(T),Pe=T.material;if(X&&(T.boundingSphere!==void 0?(T.boundingSphere===null&&T.computeBoundingSphere(),ke.copy(T.boundingSphere.center)):(Re.boundingSphere===null&&Re.computeBoundingSphere(),ke.copy(Re.boundingSphere.center)),ke.applyMatrix4(T.matrixWorld).applyMatrix4(be)),Array.isArray(Pe)){const Ie=Re.groups;for(let Je=0,Qe=Ie.length;Je<Qe;Je++){const Fe=Ie[Je],ut=Pe[Fe.materialIndex];ut&&ut.visible&&g.push(T,Re,ut,j,ke.z,Fe)}}else Pe.visible&&g.push(T,Re,Pe,j,ke.z,null)}}const ue=T.children;for(let Re=0,Pe=ue.length;Re<Pe;Re++)gi(ue[Re],V,j,X)}function Ri(T,V,j,X){const H=T.opaque,ue=T.transmissive,Re=T.transparent;m.setupLightsView(j),ne===!0&&Ke.setGlobalState(b.clippingPlanes,j),X&&Oe.viewport(y.copy(X)),H.length>0&&ni(H,V,j),ue.length>0&&ni(ue,V,j),Re.length>0&&ni(Re,V,j),Oe.buffers.depth.setTest(!0),Oe.buffers.depth.setMask(!0),Oe.buffers.color.setMask(!0),Oe.setPolygonOffset(!1)}function wn(T,V,j,X){if((j.isScene===!0?j.overrideMaterial:null)!==null)return;m.state.transmissionRenderTarget[X.id]===void 0&&(m.state.transmissionRenderTarget[X.id]=new Gs(1,1,{generateMipmaps:!0,type:it.has("EXT_color_buffer_half_float")||it.has("EXT_color_buffer_float")?ka:$i,minFilter:Bs,samples:4,stencilBuffer:r,resolveDepthBuffer:!1,resolveStencilBuffer:!1,colorSpace:wt.workingColorSpace}));const ue=m.state.transmissionRenderTarget[X.id],Re=X.viewport||y;ue.setSize(Re.z,Re.w);const Pe=b.getRenderTarget();b.setRenderTarget(ue),b.getClearColor(z),Z=b.getClearAlpha(),Z<1&&b.setClearColor(16777215,.5),b.clear(),Ne&&Te.render(j);const Ie=b.toneMapping;b.toneMapping=cs;const Je=X.viewport;if(X.viewport!==void 0&&(X.viewport=void 0),m.setupLightsView(X),ne===!0&&Ke.setGlobalState(b.clippingPlanes,X),ni(T,j,X),We.updateMultisampleRenderTarget(ue),We.updateRenderTargetMipmap(ue),it.has("WEBGL_multisampled_render_to_texture")===!1){let Qe=!1;for(let Fe=0,ut=V.length;Fe<ut;Fe++){const Dt=V[Fe],It=Dt.object,pn=Dt.geometry,mt=Dt.material,He=Dt.group;if(mt.side===Ei&&It.layers.test(X.layers)){const $t=mt.side;mt.side=Nn,mt.needsUpdate=!0,Pi(It,j,X,pn,mt,He),mt.side=$t,mt.needsUpdate=!0,Qe=!0}}Qe===!0&&(We.updateMultisampleRenderTarget(ue),We.updateRenderTargetMipmap(ue))}b.setRenderTarget(Pe),b.setClearColor(z,Z),Je!==void 0&&(X.viewport=Je),b.toneMapping=Ie}function ni(T,V,j){const X=V.isScene===!0?V.overrideMaterial:null;for(let H=0,ue=T.length;H<ue;H++){const Re=T[H],Pe=Re.object,Ie=Re.geometry,Je=X===null?Re.material:X,Qe=Re.group;Pe.layers.test(j.layers)&&Pi(Pe,V,j,Ie,Je,Qe)}}function Pi(T,V,j,X,H,ue){T.onBeforeRender(b,V,j,X,H,ue),T.modelViewMatrix.multiplyMatrices(j.matrixWorldInverse,T.matrixWorld),T.normalMatrix.getNormalMatrix(T.modelViewMatrix),H.onBeforeRender(b,V,j,X,T,ue),H.transparent===!0&&H.side===Ei&&H.forceSinglePass===!1?(H.side=Nn,H.needsUpdate=!0,b.renderBufferDirect(j,V,X,H,T,ue),H.side=hs,H.needsUpdate=!0,b.renderBufferDirect(j,V,X,H,T,ue),H.side=Ei):b.renderBufferDirect(j,V,X,H,T,ue),T.onAfterRender(b,V,j,X,H,ue)}function bs(T,V,j){V.isScene!==!0&&(V=Ve);const X=Xe.get(T),H=m.state.lights,ue=m.state.shadowsArray,Re=H.state.version,Pe=W.getParameters(T,H.state,ue,V,j),Ie=W.getProgramCacheKey(Pe);let Je=X.programs;X.environment=T.isMeshStandardMaterial?V.environment:null,X.fog=V.fog,X.envMap=(T.isMeshStandardMaterial?M:I).get(T.envMap||X.environment),X.envMapRotation=X.environment!==null&&T.envMap===null?V.environmentRotation:T.envMapRotation,Je===void 0&&(T.addEventListener("dispose",je),Je=new Map,X.programs=Je);let Qe=Je.get(Ie);if(Qe!==void 0){if(X.currentProgram===Qe&&X.lightsStateVersion===Re)return za(T,Pe),Qe}else Pe.uniforms=W.getUniforms(T),T.onBeforeCompile(Pe,b),Qe=W.acquireProgram(Pe,Ie),Je.set(Ie,Qe),X.uniforms=Pe.uniforms;const Fe=X.uniforms;return(!T.isShaderMaterial&&!T.isRawShaderMaterial||T.clipping===!0)&&(Fe.clippingPlanes=Ke.uniform),za(T,Pe),X.needsLights=vl(T),X.lightsStateVersion=Re,X.needsLights&&(Fe.ambientLightColor.value=H.state.ambient,Fe.lightProbe.value=H.state.probe,Fe.directionalLights.value=H.state.directional,Fe.directionalLightShadows.value=H.state.directionalShadow,Fe.spotLights.value=H.state.spot,Fe.spotLightShadows.value=H.state.spotShadow,Fe.rectAreaLights.value=H.state.rectArea,Fe.ltc_1.value=H.state.rectAreaLTC1,Fe.ltc_2.value=H.state.rectAreaLTC2,Fe.pointLights.value=H.state.point,Fe.pointLightShadows.value=H.state.pointShadow,Fe.hemisphereLights.value=H.state.hemi,Fe.directionalShadowMap.value=H.state.directionalShadowMap,Fe.directionalShadowMatrix.value=H.state.directionalShadowMatrix,Fe.spotShadowMap.value=H.state.spotShadowMap,Fe.spotLightMatrix.value=H.state.spotLightMatrix,Fe.spotLightMap.value=H.state.spotLightMap,Fe.pointShadowMap.value=H.state.pointShadowMap,Fe.pointShadowMatrix.value=H.state.pointShadowMatrix),X.currentProgram=Qe,X.uniformsList=null,Qe}function ia(T){if(T.uniformsList===null){const V=T.currentProgram.getUniforms();T.uniformsList=Oo.seqWithValue(V.seq,T.uniforms)}return T.uniformsList}function za(T,V){const j=Xe.get(T);j.outputColorSpace=V.outputColorSpace,j.batching=V.batching,j.batchingColor=V.batchingColor,j.instancing=V.instancing,j.instancingColor=V.instancingColor,j.instancingMorph=V.instancingMorph,j.skinning=V.skinning,j.morphTargets=V.morphTargets,j.morphNormals=V.morphNormals,j.morphColors=V.morphColors,j.morphTargetsCount=V.morphTargetsCount,j.numClippingPlanes=V.numClippingPlanes,j.numIntersection=V.numClipIntersection,j.vertexAlphas=V.vertexAlphas,j.vertexTangents=V.vertexTangents,j.toneMapping=V.toneMapping}function gl(T,V,j,X,H){V.isScene!==!0&&(V=Ve),We.resetTextureUnits();const ue=V.fog,Re=X.isMeshStandardMaterial?V.environment:null,Pe=L===null?b.outputColorSpace:L.isXRRenderTarget===!0?L.texture.colorSpace:gs,Ie=(X.isMeshStandardMaterial?M:I).get(X.envMap||Re),Je=X.vertexColors===!0&&!!j.attributes.color&&j.attributes.color.itemSize===4,Qe=!!j.attributes.tangent&&(!!X.normalMap||X.anisotropy>0),Fe=!!j.morphAttributes.position,ut=!!j.morphAttributes.normal,Dt=!!j.morphAttributes.color;let It=cs;X.toneMapped&&(L===null||L.isXRRenderTarget===!0)&&(It=b.toneMapping);const pn=j.morphAttributes.position||j.morphAttributes.normal||j.morphAttributes.color,mt=pn!==void 0?pn.length:0,He=Xe.get(X),$t=m.state.lights;if(ne===!0&&(ce===!0||T!==E)){const In=T===E&&X.id===k;Ke.setState(X,T,In)}let gt=!1;X.version===He.__version?(He.needsLights&&He.lightsStateVersion!==$t.state.version||He.outputColorSpace!==Pe||H.isBatchedMesh&&He.batching===!1||!H.isBatchedMesh&&He.batching===!0||H.isBatchedMesh&&He.batchingColor===!0&&H.colorTexture===null||H.isBatchedMesh&&He.batchingColor===!1&&H.colorTexture!==null||H.isInstancedMesh&&He.instancing===!1||!H.isInstancedMesh&&He.instancing===!0||H.isSkinnedMesh&&He.skinning===!1||!H.isSkinnedMesh&&He.skinning===!0||H.isInstancedMesh&&He.instancingColor===!0&&H.instanceColor===null||H.isInstancedMesh&&He.instancingColor===!1&&H.instanceColor!==null||H.isInstancedMesh&&He.instancingMorph===!0&&H.morphTexture===null||H.isInstancedMesh&&He.instancingMorph===!1&&H.morphTexture!==null||He.envMap!==Ie||X.fog===!0&&He.fog!==ue||He.numClippingPlanes!==void 0&&(He.numClippingPlanes!==Ke.numPlanes||He.numIntersection!==Ke.numIntersection)||He.vertexAlphas!==Je||He.vertexTangents!==Qe||He.morphTargets!==Fe||He.morphNormals!==ut||He.morphColors!==Dt||He.toneMapping!==It||He.morphTargetsCount!==mt)&&(gt=!0):(gt=!0,He.__version=X.version);let Ut=He.currentProgram;gt===!0&&(Ut=bs(X,V,H));let Di=!1,_n=!1,Ss=!1;const Wt=Ut.getUniforms(),vi=He.uniforms;if(Oe.useProgram(Ut.program)&&(Di=!0,_n=!0,Ss=!0),X.id!==k&&(k=X.id,_n=!0),Di||E!==T){Wt.setValue(N,"projectionMatrix",T.projectionMatrix),Wt.setValue(N,"viewMatrix",T.matrixWorldInverse);const In=Wt.map.cameraPosition;In!==void 0&&In.setValue(N,fe.setFromMatrixPosition(T.matrixWorld)),ct.logarithmicDepthBuffer&&Wt.setValue(N,"logDepthBufFC",2/(Math.log(T.far+1)/Math.LN2)),(X.isMeshPhongMaterial||X.isMeshToonMaterial||X.isMeshLambertMaterial||X.isMeshBasicMaterial||X.isMeshStandardMaterial||X.isShaderMaterial)&&Wt.setValue(N,"isOrthographic",T.isOrthographicCamera===!0),E!==T&&(E=T,_n=!0,Ss=!0)}if(H.isSkinnedMesh){Wt.setOptional(N,H,"bindMatrix"),Wt.setOptional(N,H,"bindMatrixInverse");const In=H.skeleton;In&&(In.boneTexture===null&&In.computeBoneTexture(),Wt.setValue(N,"boneTexture",In.boneTexture,We))}H.isBatchedMesh&&(Wt.setOptional(N,H,"batchingTexture"),Wt.setValue(N,"batchingTexture",H._matricesTexture,We),Wt.setOptional(N,H,"batchingIdTexture"),Wt.setValue(N,"batchingIdTexture",H._indirectTexture,We),Wt.setOptional(N,H,"batchingColorTexture"),H._colorsTexture!==null&&Wt.setValue(N,"batchingColorTexture",H._colorsTexture,We));const sa=j.morphAttributes;if((sa.position!==void 0||sa.normal!==void 0||sa.color!==void 0)&&Ze.update(H,j,Ut),(_n||He.receiveShadow!==H.receiveShadow)&&(He.receiveShadow=H.receiveShadow,Wt.setValue(N,"receiveShadow",H.receiveShadow)),X.isMeshGouraudMaterial&&X.envMap!==null&&(vi.envMap.value=Ie,vi.flipEnvMap.value=Ie.isCubeTexture&&Ie.isRenderTargetTexture===!1?-1:1),X.isMeshStandardMaterial&&X.envMap===null&&V.environment!==null&&(vi.envMapIntensity.value=V.environmentIntensity),_n&&(Wt.setValue(N,"toneMappingExposure",b.toneMappingExposure),He.needsLights&&Li(vi,Ss),ue&&X.fog===!0&&we.refreshFogUniforms(vi,ue),we.refreshMaterialUniforms(vi,X,$,Q,m.state.transmissionRenderTarget[T.id]),Oo.upload(N,ia(He),vi,We)),X.isShaderMaterial&&X.uniformsNeedUpdate===!0&&(Oo.upload(N,ia(He),vi,We),X.uniformsNeedUpdate=!1),X.isSpriteMaterial&&Wt.setValue(N,"center",H.center),Wt.setValue(N,"modelViewMatrix",H.modelViewMatrix),Wt.setValue(N,"normalMatrix",H.normalMatrix),Wt.setValue(N,"modelMatrix",H.matrixWorld),X.isShaderMaterial||X.isRawShaderMaterial){const In=X.uniformsGroups;for(let Zs=0,Ha=In.length;Zs<Ha;Zs++){const Va=In[Zs];le.update(Va,Ut),le.bind(Va,Ut)}}return Ut}function Li(T,V){T.ambientLightColor.needsUpdate=V,T.lightProbe.needsUpdate=V,T.directionalLights.needsUpdate=V,T.directionalLightShadows.needsUpdate=V,T.pointLights.needsUpdate=V,T.pointLightShadows.needsUpdate=V,T.spotLights.needsUpdate=V,T.spotLightShadows.needsUpdate=V,T.rectAreaLights.needsUpdate=V,T.hemisphereLights.needsUpdate=V}function vl(T){return T.isMeshLambertMaterial||T.isMeshToonMaterial||T.isMeshPhongMaterial||T.isMeshStandardMaterial||T.isShadowMaterial||T.isShaderMaterial&&T.lights===!0}this.getActiveCubeFace=function(){return O},this.getActiveMipmapLevel=function(){return A},this.getRenderTarget=function(){return L},this.setRenderTargetTextures=function(T,V,j){Xe.get(T.texture).__webglTexture=V,Xe.get(T.depthTexture).__webglTexture=j;const X=Xe.get(T);X.__hasExternalTextures=!0,X.__autoAllocateDepthBuffer=j===void 0,X.__autoAllocateDepthBuffer||it.has("WEBGL_multisampled_render_to_texture")===!0&&(console.warn("THREE.WebGLRenderer: Render-to-texture extension was disabled because an external texture was provided"),X.__useRenderToTexture=!1)},this.setRenderTargetFramebuffer=function(T,V){const j=Xe.get(T);j.__webglFramebuffer=V,j.__useDefaultFramebuffer=V===void 0},this.setRenderTarget=function(T,V=0,j=0){L=T,O=V,A=j;let X=!0,H=null,ue=!1,Re=!1;if(T){const Ie=Xe.get(T);if(Ie.__useDefaultFramebuffer!==void 0)Oe.bindFramebuffer(N.FRAMEBUFFER,null),X=!1;else if(Ie.__webglFramebuffer===void 0)We.setupRenderTarget(T);else if(Ie.__hasExternalTextures)We.rebindTextures(T,Xe.get(T.texture).__webglTexture,Xe.get(T.depthTexture).__webglTexture);else if(T.depthBuffer){const Fe=T.depthTexture;if(Ie.__boundDepthTexture!==Fe){if(Fe!==null&&Xe.has(Fe)&&(T.width!==Fe.image.width||T.height!==Fe.image.height))throw new Error("WebGLRenderTarget: Attached DepthTexture is initialized to the incorrect size.");We.setupDepthRenderbuffer(T)}}const Je=T.texture;(Je.isData3DTexture||Je.isDataArrayTexture||Je.isCompressedArrayTexture)&&(Re=!0);const Qe=Xe.get(T).__webglFramebuffer;T.isWebGLCubeRenderTarget?(Array.isArray(Qe[V])?H=Qe[V][j]:H=Qe[V],ue=!0):T.samples>0&&We.useMultisampledRTT(T)===!1?H=Xe.get(T).__webglMultisampledFramebuffer:Array.isArray(Qe)?H=Qe[j]:H=Qe,y.copy(T.viewport),P.copy(T.scissor),K=T.scissorTest}else y.copy(de).multiplyScalar($).floor(),P.copy(xe).multiplyScalar($).floor(),K=Ee;if(Oe.bindFramebuffer(N.FRAMEBUFFER,H)&&X&&Oe.drawBuffers(T,H),Oe.viewport(y),Oe.scissor(P),Oe.setScissorTest(K),ue){const Ie=Xe.get(T.texture);N.framebufferTexture2D(N.FRAMEBUFFER,N.COLOR_ATTACHMENT0,N.TEXTURE_CUBE_MAP_POSITIVE_X+V,Ie.__webglTexture,j)}else if(Re){const Ie=Xe.get(T.texture),Je=V||0;N.framebufferTextureLayer(N.FRAMEBUFFER,N.COLOR_ATTACHMENT0,Ie.__webglTexture,j||0,Je)}k=-1},this.readRenderTargetPixels=function(T,V,j,X,H,ue,Re){if(!(T&&T.isWebGLRenderTarget)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");return}let Pe=Xe.get(T).__webglFramebuffer;if(T.isWebGLCubeRenderTarget&&Re!==void 0&&(Pe=Pe[Re]),Pe){Oe.bindFramebuffer(N.FRAMEBUFFER,Pe);try{const Ie=T.texture,Je=Ie.format,Qe=Ie.type;if(!ct.textureFormatReadable(Je)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in RGBA or implementation defined format.");return}if(!ct.textureTypeReadable(Qe)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in UnsignedByteType or implementation defined type.");return}V>=0&&V<=T.width-X&&j>=0&&j<=T.height-H&&N.readPixels(V,j,X,H,ze.convert(Je),ze.convert(Qe),ue)}finally{const Ie=L!==null?Xe.get(L).__webglFramebuffer:null;Oe.bindFramebuffer(N.FRAMEBUFFER,Ie)}}},this.readRenderTargetPixelsAsync=async function(T,V,j,X,H,ue,Re){if(!(T&&T.isWebGLRenderTarget))throw new Error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");let Pe=Xe.get(T).__webglFramebuffer;if(T.isWebGLCubeRenderTarget&&Re!==void 0&&(Pe=Pe[Re]),Pe){Oe.bindFramebuffer(N.FRAMEBUFFER,Pe);try{const Ie=T.texture,Je=Ie.format,Qe=Ie.type;if(!ct.textureFormatReadable(Je))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in RGBA or implementation defined format.");if(!ct.textureTypeReadable(Qe))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in UnsignedByteType or implementation defined type.");if(V>=0&&V<=T.width-X&&j>=0&&j<=T.height-H){const Fe=N.createBuffer();N.bindBuffer(N.PIXEL_PACK_BUFFER,Fe),N.bufferData(N.PIXEL_PACK_BUFFER,ue.byteLength,N.STREAM_READ),N.readPixels(V,j,X,H,ze.convert(Je),ze.convert(Qe),0),N.flush();const ut=N.fenceSync(N.SYNC_GPU_COMMANDS_COMPLETE,0);await Dg(N,ut,4);try{N.bindBuffer(N.PIXEL_PACK_BUFFER,Fe),N.getBufferSubData(N.PIXEL_PACK_BUFFER,0,ue)}finally{N.deleteBuffer(Fe),N.deleteSync(ut)}return ue}}finally{const Ie=L!==null?Xe.get(L).__webglFramebuffer:null;Oe.bindFramebuffer(N.FRAMEBUFFER,Ie)}}},this.copyFramebufferToTexture=function(T,V=null,j=0){T.isTexture!==!0&&(Fr("WebGLRenderer: copyFramebufferToTexture function signature has changed."),V=arguments[0]||null,T=arguments[1]);const X=Math.pow(2,-j),H=Math.floor(T.image.width*X),ue=Math.floor(T.image.height*X),Re=V!==null?V.x:0,Pe=V!==null?V.y:0;We.setTexture2D(T,0),N.copyTexSubImage2D(N.TEXTURE_2D,j,0,0,Re,Pe,H,ue),Oe.unbindTexture()},this.copyTextureToTexture=function(T,V,j=null,X=null,H=0){T.isTexture!==!0&&(Fr("WebGLRenderer: copyTextureToTexture function signature has changed."),X=arguments[0]||null,T=arguments[1],V=arguments[2],H=arguments[3]||0,j=null);let ue,Re,Pe,Ie,Je,Qe;j!==null?(ue=j.max.x-j.min.x,Re=j.max.y-j.min.y,Pe=j.min.x,Ie=j.min.y):(ue=T.image.width,Re=T.image.height,Pe=0,Ie=0),X!==null?(Je=X.x,Qe=X.y):(Je=0,Qe=0);const Fe=ze.convert(V.format),ut=ze.convert(V.type);We.setTexture2D(V,0),N.pixelStorei(N.UNPACK_FLIP_Y_WEBGL,V.flipY),N.pixelStorei(N.UNPACK_PREMULTIPLY_ALPHA_WEBGL,V.premultiplyAlpha),N.pixelStorei(N.UNPACK_ALIGNMENT,V.unpackAlignment);const Dt=N.getParameter(N.UNPACK_ROW_LENGTH),It=N.getParameter(N.UNPACK_IMAGE_HEIGHT),pn=N.getParameter(N.UNPACK_SKIP_PIXELS),mt=N.getParameter(N.UNPACK_SKIP_ROWS),He=N.getParameter(N.UNPACK_SKIP_IMAGES),$t=T.isCompressedTexture?T.mipmaps[H]:T.image;N.pixelStorei(N.UNPACK_ROW_LENGTH,$t.width),N.pixelStorei(N.UNPACK_IMAGE_HEIGHT,$t.height),N.pixelStorei(N.UNPACK_SKIP_PIXELS,Pe),N.pixelStorei(N.UNPACK_SKIP_ROWS,Ie),T.isDataTexture?N.texSubImage2D(N.TEXTURE_2D,H,Je,Qe,ue,Re,Fe,ut,$t.data):T.isCompressedTexture?N.compressedTexSubImage2D(N.TEXTURE_2D,H,Je,Qe,$t.width,$t.height,Fe,$t.data):N.texSubImage2D(N.TEXTURE_2D,H,Je,Qe,ue,Re,Fe,ut,$t),N.pixelStorei(N.UNPACK_ROW_LENGTH,Dt),N.pixelStorei(N.UNPACK_IMAGE_HEIGHT,It),N.pixelStorei(N.UNPACK_SKIP_PIXELS,pn),N.pixelStorei(N.UNPACK_SKIP_ROWS,mt),N.pixelStorei(N.UNPACK_SKIP_IMAGES,He),H===0&&V.generateMipmaps&&N.generateMipmap(N.TEXTURE_2D),Oe.unbindTexture()},this.copyTextureToTexture3D=function(T,V,j=null,X=null,H=0){T.isTexture!==!0&&(Fr("WebGLRenderer: copyTextureToTexture3D function signature has changed."),j=arguments[0]||null,X=arguments[1]||null,T=arguments[2],V=arguments[3],H=arguments[4]||0);let ue,Re,Pe,Ie,Je,Qe,Fe,ut,Dt;const It=T.isCompressedTexture?T.mipmaps[H]:T.image;j!==null?(ue=j.max.x-j.min.x,Re=j.max.y-j.min.y,Pe=j.max.z-j.min.z,Ie=j.min.x,Je=j.min.y,Qe=j.min.z):(ue=It.width,Re=It.height,Pe=It.depth,Ie=0,Je=0,Qe=0),X!==null?(Fe=X.x,ut=X.y,Dt=X.z):(Fe=0,ut=0,Dt=0);const pn=ze.convert(V.format),mt=ze.convert(V.type);let He;if(V.isData3DTexture)We.setTexture3D(V,0),He=N.TEXTURE_3D;else if(V.isDataArrayTexture||V.isCompressedArrayTexture)We.setTexture2DArray(V,0),He=N.TEXTURE_2D_ARRAY;else{console.warn("THREE.WebGLRenderer.copyTextureToTexture3D: only supports THREE.DataTexture3D and THREE.DataTexture2DArray.");return}N.pixelStorei(N.UNPACK_FLIP_Y_WEBGL,V.flipY),N.pixelStorei(N.UNPACK_PREMULTIPLY_ALPHA_WEBGL,V.premultiplyAlpha),N.pixelStorei(N.UNPACK_ALIGNMENT,V.unpackAlignment);const $t=N.getParameter(N.UNPACK_ROW_LENGTH),gt=N.getParameter(N.UNPACK_IMAGE_HEIGHT),Ut=N.getParameter(N.UNPACK_SKIP_PIXELS),Di=N.getParameter(N.UNPACK_SKIP_ROWS),_n=N.getParameter(N.UNPACK_SKIP_IMAGES);N.pixelStorei(N.UNPACK_ROW_LENGTH,It.width),N.pixelStorei(N.UNPACK_IMAGE_HEIGHT,It.height),N.pixelStorei(N.UNPACK_SKIP_PIXELS,Ie),N.pixelStorei(N.UNPACK_SKIP_ROWS,Je),N.pixelStorei(N.UNPACK_SKIP_IMAGES,Qe),T.isDataTexture||T.isData3DTexture?N.texSubImage3D(He,H,Fe,ut,Dt,ue,Re,Pe,pn,mt,It.data):V.isCompressedArrayTexture?N.compressedTexSubImage3D(He,H,Fe,ut,Dt,ue,Re,Pe,pn,It.data):N.texSubImage3D(He,H,Fe,ut,Dt,ue,Re,Pe,pn,mt,It),N.pixelStorei(N.UNPACK_ROW_LENGTH,$t),N.pixelStorei(N.UNPACK_IMAGE_HEIGHT,gt),N.pixelStorei(N.UNPACK_SKIP_PIXELS,Ut),N.pixelStorei(N.UNPACK_SKIP_ROWS,Di),N.pixelStorei(N.UNPACK_SKIP_IMAGES,_n),H===0&&V.generateMipmaps&&N.generateMipmap(He),Oe.unbindTexture()},this.initRenderTarget=function(T){Xe.get(T).__webglFramebuffer===void 0&&We.setupRenderTarget(T)},this.initTexture=function(T){T.isCubeTexture?We.setTextureCube(T,0):T.isData3DTexture?We.setTexture3D(T,0):T.isDataArrayTexture||T.isCompressedArrayTexture?We.setTexture2DArray(T,0):We.setTexture2D(T,0),Oe.unbindTexture()},this.resetState=function(){O=0,A=0,L=null,Oe.reset(),F.reset()},typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}get coordinateSystem(){return Vi}get outputColorSpace(){return this._outputColorSpace}set outputColorSpace(e){this._outputColorSpace=e;const t=this.getContext();t.drawingBufferColorSpace=e===Su?"display-p3":"srgb",t.unpackColorSpace=wt.workingColorSpace===il?"display-p3":"srgb"}}class Au{constructor(e,t=25e-5){this.isFogExp2=!0,this.name="",this.color=new st(e),this.density=t}clone(){return new Au(this.color,this.density)}toJSON(){return{type:"FogExp2",name:this.name,color:this.color.getHex(),density:this.density}}}class Qf extends tn{constructor(){super(),this.isScene=!0,this.type="Scene",this.background=null,this.environment=null,this.fog=null,this.backgroundBlurriness=0,this.backgroundIntensity=1,this.backgroundRotation=new Ai,this.environmentIntensity=1,this.environmentRotation=new Ai,this.overrideMaterial=null,typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}copy(e,t){return super.copy(e,t),e.background!==null&&(this.background=e.background.clone()),e.environment!==null&&(this.environment=e.environment.clone()),e.fog!==null&&(this.fog=e.fog.clone()),this.backgroundBlurriness=e.backgroundBlurriness,this.backgroundIntensity=e.backgroundIntensity,this.backgroundRotation.copy(e.backgroundRotation),this.environmentIntensity=e.environmentIntensity,this.environmentRotation.copy(e.environmentRotation),e.overrideMaterial!==null&&(this.overrideMaterial=e.overrideMaterial.clone()),this.matrixAutoUpdate=e.matrixAutoUpdate,this}toJSON(e){const t=super.toJSON(e);return this.fog!==null&&(t.object.fog=this.fog.toJSON()),this.backgroundBlurriness>0&&(t.object.backgroundBlurriness=this.backgroundBlurriness),this.backgroundIntensity!==1&&(t.object.backgroundIntensity=this.backgroundIntensity),t.object.backgroundRotation=this.backgroundRotation.toArray(),this.environmentIntensity!==1&&(t.object.environmentIntensity=this.environmentIntensity),t.object.environmentRotation=this.environmentRotation.toArray(),t}}class Vy{constructor(e,t){this.isInterleavedBuffer=!0,this.array=e,this.stride=t,this.count=e!==void 0?e.length/t:0,this.usage=Zc,this._updateRange={offset:0,count:-1},this.updateRanges=[],this.version=0,this.uuid=Wi()}onUploadCallback(){}set needsUpdate(e){e===!0&&this.version++}get updateRange(){return Fr("THREE.InterleavedBuffer: updateRange() is deprecated and will be removed in r169. Use addUpdateRange() instead."),this._updateRange}setUsage(e){return this.usage=e,this}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}copy(e){return this.array=new e.array.constructor(e.array),this.count=e.count,this.stride=e.stride,this.usage=e.usage,this}copyAt(e,t,n){e*=this.stride,n*=t.stride;for(let s=0,r=this.stride;s<r;s++)this.array[e+s]=t.array[n+s];return this}set(e,t=0){return this.array.set(e,t),this}clone(e){e.arrayBuffers===void 0&&(e.arrayBuffers={}),this.array.buffer._uuid===void 0&&(this.array.buffer._uuid=Wi()),e.arrayBuffers[this.array.buffer._uuid]===void 0&&(e.arrayBuffers[this.array.buffer._uuid]=this.array.slice(0).buffer);const t=new this.array.constructor(e.arrayBuffers[this.array.buffer._uuid]),n=new this.constructor(t,this.stride);return n.setUsage(this.usage),n}onUpload(e){return this.onUploadCallback=e,this}toJSON(e){return e.arrayBuffers===void 0&&(e.arrayBuffers={}),this.array.buffer._uuid===void 0&&(this.array.buffer._uuid=Wi()),e.arrayBuffers[this.array.buffer._uuid]===void 0&&(e.arrayBuffers[this.array.buffer._uuid]=Array.from(new Uint32Array(this.array.buffer))),{uuid:this.uuid,buffer:this.array.buffer._uuid,type:this.array.constructor.name,stride:this.stride}}}const Cn=new G;class qo{constructor(e,t,n,s=!1){this.isInterleavedBufferAttribute=!0,this.name="",this.data=e,this.itemSize=t,this.offset=n,this.normalized=s}get count(){return this.data.count}get array(){return this.data.array}set needsUpdate(e){this.data.needsUpdate=e}applyMatrix4(e){for(let t=0,n=this.data.count;t<n;t++)Cn.fromBufferAttribute(this,t),Cn.applyMatrix4(e),this.setXYZ(t,Cn.x,Cn.y,Cn.z);return this}applyNormalMatrix(e){for(let t=0,n=this.count;t<n;t++)Cn.fromBufferAttribute(this,t),Cn.applyNormalMatrix(e),this.setXYZ(t,Cn.x,Cn.y,Cn.z);return this}transformDirection(e){for(let t=0,n=this.count;t<n;t++)Cn.fromBufferAttribute(this,t),Cn.transformDirection(e),this.setXYZ(t,Cn.x,Cn.y,Cn.z);return this}getComponent(e,t){let n=this.array[e*this.data.stride+this.offset+t];return this.normalized&&(n=hi(n,this.array)),n}setComponent(e,t,n){return this.normalized&&(n=At(n,this.array)),this.data.array[e*this.data.stride+this.offset+t]=n,this}setX(e,t){return this.normalized&&(t=At(t,this.array)),this.data.array[e*this.data.stride+this.offset]=t,this}setY(e,t){return this.normalized&&(t=At(t,this.array)),this.data.array[e*this.data.stride+this.offset+1]=t,this}setZ(e,t){return this.normalized&&(t=At(t,this.array)),this.data.array[e*this.data.stride+this.offset+2]=t,this}setW(e,t){return this.normalized&&(t=At(t,this.array)),this.data.array[e*this.data.stride+this.offset+3]=t,this}getX(e){let t=this.data.array[e*this.data.stride+this.offset];return this.normalized&&(t=hi(t,this.array)),t}getY(e){let t=this.data.array[e*this.data.stride+this.offset+1];return this.normalized&&(t=hi(t,this.array)),t}getZ(e){let t=this.data.array[e*this.data.stride+this.offset+2];return this.normalized&&(t=hi(t,this.array)),t}getW(e){let t=this.data.array[e*this.data.stride+this.offset+3];return this.normalized&&(t=hi(t,this.array)),t}setXY(e,t,n){return e=e*this.data.stride+this.offset,this.normalized&&(t=At(t,this.array),n=At(n,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this}setXYZ(e,t,n,s){return e=e*this.data.stride+this.offset,this.normalized&&(t=At(t,this.array),n=At(n,this.array),s=At(s,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this.data.array[e+2]=s,this}setXYZW(e,t,n,s,r){return e=e*this.data.stride+this.offset,this.normalized&&(t=At(t,this.array),n=At(n,this.array),s=At(s,this.array),r=At(r,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this.data.array[e+2]=s,this.data.array[e+3]=r,this}clone(e){if(e===void 0){console.log("THREE.InterleavedBufferAttribute.clone(): Cloning an interleaved buffer attribute will de-interleave buffer data.");const t=[];for(let n=0;n<this.count;n++){const s=n*this.data.stride+this.offset;for(let r=0;r<this.itemSize;r++)t.push(this.data.array[s+r])}return new pi(new this.array.constructor(t),this.itemSize,this.normalized)}else return e.interleavedBuffers===void 0&&(e.interleavedBuffers={}),e.interleavedBuffers[this.data.uuid]===void 0&&(e.interleavedBuffers[this.data.uuid]=this.data.clone(e)),new qo(e.interleavedBuffers[this.data.uuid],this.itemSize,this.offset,this.normalized)}toJSON(e){if(e===void 0){console.log("THREE.InterleavedBufferAttribute.toJSON(): Serializing an interleaved buffer attribute will de-interleave buffer data.");const t=[];for(let n=0;n<this.count;n++){const s=n*this.data.stride+this.offset;for(let r=0;r<this.itemSize;r++)t.push(this.data.array[s+r])}return{itemSize:this.itemSize,type:this.array.constructor.name,array:t,normalized:this.normalized}}else return e.interleavedBuffers===void 0&&(e.interleavedBuffers={}),e.interleavedBuffers[this.data.uuid]===void 0&&(e.interleavedBuffers[this.data.uuid]=this.data.toJSON(e)),{isInterleavedBufferAttribute:!0,itemSize:this.itemSize,data:this.data.uuid,offset:this.offset,normalized:this.normalized}}}class Qc extends Ys{constructor(e){super(),this.isSpriteMaterial=!0,this.type="SpriteMaterial",this.color=new st(16777215),this.map=null,this.alphaMap=null,this.rotation=0,this.sizeAttenuation=!0,this.transparent=!0,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.alphaMap=e.alphaMap,this.rotation=e.rotation,this.sizeAttenuation=e.sizeAttenuation,this.fog=e.fog,this}}let Tr;const ma=new G,Ar=new G,Cr=new G,Rr=new qe,ga=new qe,ep=new Gt,_o=new G,va=new G,xo=new G,ud=new qe,nc=new qe,hd=new qe;class Gy extends tn{constructor(e=new Qc){if(super(),this.isSprite=!0,this.type="Sprite",Tr===void 0){Tr=new Xn;const t=new Float32Array([-.5,-.5,0,0,0,.5,-.5,0,1,0,.5,.5,0,1,1,-.5,.5,0,0,1]),n=new Vy(t,5);Tr.setIndex([0,1,2,0,2,3]),Tr.setAttribute("position",new qo(n,3,0,!1)),Tr.setAttribute("uv",new qo(n,2,3,!1))}this.geometry=Tr,this.material=e,this.center=new qe(.5,.5)}raycast(e,t){e.camera===null&&console.error('THREE.Sprite: "Raycaster.camera" needs to be set in order to raycast against sprites.'),Ar.setFromMatrixScale(this.matrixWorld),ep.copy(e.camera.matrixWorld),this.modelViewMatrix.multiplyMatrices(e.camera.matrixWorldInverse,this.matrixWorld),Cr.setFromMatrixPosition(this.modelViewMatrix),e.camera.isPerspectiveCamera&&this.material.sizeAttenuation===!1&&Ar.multiplyScalar(-Cr.z);const n=this.material.rotation;let s,r;n!==0&&(r=Math.cos(n),s=Math.sin(n));const o=this.center;yo(_o.set(-.5,-.5,0),Cr,o,Ar,s,r),yo(va.set(.5,-.5,0),Cr,o,Ar,s,r),yo(xo.set(.5,.5,0),Cr,o,Ar,s,r),ud.set(0,0),nc.set(1,0),hd.set(1,1);let a=e.ray.intersectTriangle(_o,va,xo,!1,ma);if(a===null&&(yo(va.set(-.5,.5,0),Cr,o,Ar,s,r),nc.set(0,1),a=e.ray.intersectTriangle(_o,xo,va,!1,ma),a===null))return;const l=e.ray.origin.distanceTo(ma);l<e.near||l>e.far||t.push({distance:l,point:ma.clone(),uv:Qn.getInterpolation(ma,_o,va,xo,ud,nc,hd,new qe),face:null,object:this})}copy(e,t){return super.copy(e,t),e.center!==void 0&&this.center.copy(e.center),this.material=e.material,this}}function yo(i,e,t,n,s,r){Rr.subVectors(i,t).addScalar(.5).multiply(n),s!==void 0?(ga.x=r*Rr.x-s*Rr.y,ga.y=s*Rr.x+r*Rr.y):ga.copy(Rr),i.copy(e),i.x+=ga.x,i.y+=ga.y,i.applyMatrix4(ep)}class Ca extends Ys{constructor(e){super(),this.isLineBasicMaterial=!0,this.type="LineBasicMaterial",this.color=new st(16777215),this.map=null,this.linewidth=1,this.linecap="round",this.linejoin="round",this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.linewidth=e.linewidth,this.linecap=e.linecap,this.linejoin=e.linejoin,this.fog=e.fog,this}}const Xo=new G,$o=new G,dd=new Gt,_a=new rl,bo=new sl,ic=new G,fd=new G;class Wy extends tn{constructor(e=new Xn,t=new Ca){super(),this.isLine=!0,this.type="Line",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}computeLineDistances(){const e=this.geometry;if(e.index===null){const t=e.attributes.position,n=[0];for(let s=1,r=t.count;s<r;s++)Xo.fromBufferAttribute(t,s-1),$o.fromBufferAttribute(t,s),n[s]=n[s-1],n[s]+=Xo.distanceTo($o);e.setAttribute("lineDistance",new Mn(n,1))}else console.warn("THREE.Line.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.");return this}raycast(e,t){const n=this.geometry,s=this.matrixWorld,r=e.params.Line.threshold,o=n.drawRange;if(n.boundingSphere===null&&n.computeBoundingSphere(),bo.copy(n.boundingSphere),bo.applyMatrix4(s),bo.radius+=r,e.ray.intersectsSphere(bo)===!1)return;dd.copy(s).invert(),_a.copy(e.ray).applyMatrix4(dd);const a=r/((this.scale.x+this.scale.y+this.scale.z)/3),l=a*a,c=this.isLineSegments?2:1,u=n.index,d=n.attributes.position;if(u!==null){const f=Math.max(0,o.start),v=Math.min(u.count,o.start+o.count);for(let g=f,m=v-1;g<m;g+=c){const p=u.getX(g),x=u.getX(g+1),b=So(this,e,_a,l,p,x);b&&t.push(b)}if(this.isLineLoop){const g=u.getX(v-1),m=u.getX(f),p=So(this,e,_a,l,g,m);p&&t.push(p)}}else{const f=Math.max(0,o.start),v=Math.min(d.count,o.start+o.count);for(let g=f,m=v-1;g<m;g+=c){const p=So(this,e,_a,l,g,g+1);p&&t.push(p)}if(this.isLineLoop){const g=So(this,e,_a,l,v-1,f);g&&t.push(g)}}}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const s=t[n[0]];if(s!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let r=0,o=s.length;r<o;r++){const a=s[r].name||String(r);this.morphTargetInfluences.push(0),this.morphTargetDictionary[a]=r}}}}}function So(i,e,t,n,s,r){const o=i.geometry.attributes.position;if(Xo.fromBufferAttribute(o,s),$o.fromBufferAttribute(o,r),t.distanceSqToSegment(Xo,$o,ic,fd)>n)return;ic.applyMatrix4(i.matrixWorld);const l=e.ray.origin.distanceTo(ic);if(!(l<e.near||l>e.far))return{distance:l,point:fd.clone().applyMatrix4(i.matrixWorld),index:s,face:null,faceIndex:null,object:i}}const pd=new G,md=new G;class Fo extends Wy{constructor(e,t){super(e,t),this.isLineSegments=!0,this.type="LineSegments"}computeLineDistances(){const e=this.geometry;if(e.index===null){const t=e.attributes.position,n=[];for(let s=0,r=t.count;s<r;s+=2)pd.fromBufferAttribute(t,s),md.fromBufferAttribute(t,s+1),n[s]=s===0?0:n[s-1],n[s+1]=n[s]+pd.distanceTo(md);e.setAttribute("lineDistance",new Mn(n,1))}else console.warn("THREE.LineSegments.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.");return this}}class qy extends Dn{constructor(e,t,n,s,r,o,a,l,c){super(e,t,n,s,r,o,a,l,c),this.isCanvasTexture=!0,this.needsUpdate=!0}}const Mo=new G,wo=new G,sc=new G,Eo=new Qn;class Xy extends Xn{constructor(e=null,t=1){if(super(),this.type="EdgesGeometry",this.parameters={geometry:e,thresholdAngle:t},e!==null){const s=Math.pow(10,4),r=Math.cos(Or*t),o=e.getIndex(),a=e.getAttribute("position"),l=o?o.count:a.count,c=[0,0,0],u=["a","b","c"],h=new Array(3),d={},f=[];for(let v=0;v<l;v+=3){o?(c[0]=o.getX(v),c[1]=o.getX(v+1),c[2]=o.getX(v+2)):(c[0]=v,c[1]=v+1,c[2]=v+2);const{a:g,b:m,c:p}=Eo;if(g.fromBufferAttribute(a,c[0]),m.fromBufferAttribute(a,c[1]),p.fromBufferAttribute(a,c[2]),Eo.getNormal(sc),h[0]=`${Math.round(g.x*s)},${Math.round(g.y*s)},${Math.round(g.z*s)}`,h[1]=`${Math.round(m.x*s)},${Math.round(m.y*s)},${Math.round(m.z*s)}`,h[2]=`${Math.round(p.x*s)},${Math.round(p.y*s)},${Math.round(p.z*s)}`,!(h[0]===h[1]||h[1]===h[2]||h[2]===h[0]))for(let x=0;x<3;x++){const b=(x+1)%3,w=h[x],O=h[b],A=Eo[u[x]],L=Eo[u[b]],k=`${w}_${O}`,E=`${O}_${w}`;E in d&&d[E]?(sc.dot(d[E].normal)<=r&&(f.push(A.x,A.y,A.z),f.push(L.x,L.y,L.z)),d[E]=null):k in d||(d[k]={index0:c[x],index1:c[b],normal:sc.clone()})}}for(const v in d)if(d[v]){const{index0:g,index1:m}=d[v];Mo.fromBufferAttribute(a,g),wo.fromBufferAttribute(a,m),f.push(Mo.x,Mo.y,Mo.z),f.push(wo.x,wo.y,wo.z)}this.setAttribute("position",new Mn(f,3))}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}}class Cu extends Xn{constructor(e=.5,t=1,n=32,s=1,r=0,o=Math.PI*2){super(),this.type="RingGeometry",this.parameters={innerRadius:e,outerRadius:t,thetaSegments:n,phiSegments:s,thetaStart:r,thetaLength:o},n=Math.max(3,n),s=Math.max(1,s);const a=[],l=[],c=[],u=[];let h=e;const d=(t-e)/s,f=new G,v=new qe;for(let g=0;g<=s;g++){for(let m=0;m<=n;m++){const p=r+m/n*o;f.x=h*Math.cos(p),f.y=h*Math.sin(p),l.push(f.x,f.y,f.z),c.push(0,0,1),v.x=(f.x/t+1)/2,v.y=(f.y/t+1)/2,u.push(v.x,v.y)}h+=d}for(let g=0;g<s;g++){const m=g*(n+1);for(let p=0;p<n;p++){const x=p+m,b=x,w=x+n+1,O=x+n+2,A=x+1;a.push(b,w,A),a.push(w,O,A)}}this.setIndex(a),this.setAttribute("position",new Mn(l,3)),this.setAttribute("normal",new Mn(c,3)),this.setAttribute("uv",new Mn(u,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Cu(e.innerRadius,e.outerRadius,e.thetaSegments,e.phiSegments,e.thetaStart,e.thetaLength)}}class rc extends Ys{constructor(e){super(),this.isMeshStandardMaterial=!0,this.defines={STANDARD:""},this.type="MeshStandardMaterial",this.color=new st(16777215),this.roughness=1,this.metalness=0,this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.emissive=new st(0),this.emissiveIntensity=1,this.emissiveMap=null,this.bumpMap=null,this.bumpScale=1,this.normalMap=null,this.normalMapType=Of,this.normalScale=new qe(1,1),this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.roughnessMap=null,this.metalnessMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new Ai,this.envMapIntensity=1,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.flatShading=!1,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.defines={STANDARD:""},this.color.copy(e.color),this.roughness=e.roughness,this.metalness=e.metalness,this.map=e.map,this.lightMap=e.lightMap,this.lightMapIntensity=e.lightMapIntensity,this.aoMap=e.aoMap,this.aoMapIntensity=e.aoMapIntensity,this.emissive.copy(e.emissive),this.emissiveMap=e.emissiveMap,this.emissiveIntensity=e.emissiveIntensity,this.bumpMap=e.bumpMap,this.bumpScale=e.bumpScale,this.normalMap=e.normalMap,this.normalMapType=e.normalMapType,this.normalScale.copy(e.normalScale),this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this.roughnessMap=e.roughnessMap,this.metalnessMap=e.metalnessMap,this.alphaMap=e.alphaMap,this.envMap=e.envMap,this.envMapRotation.copy(e.envMapRotation),this.envMapIntensity=e.envMapIntensity,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.wireframeLinecap=e.wireframeLinecap,this.wireframeLinejoin=e.wireframeLinejoin,this.flatShading=e.flatShading,this.fog=e.fog,this}}class Ru extends tn{constructor(e,t=1){super(),this.isLight=!0,this.type="Light",this.color=new st(e),this.intensity=t}dispose(){}copy(e,t){return super.copy(e,t),this.color.copy(e.color),this.intensity=e.intensity,this}toJSON(e){const t=super.toJSON(e);return t.object.color=this.color.getHex(),t.object.intensity=this.intensity,this.groundColor!==void 0&&(t.object.groundColor=this.groundColor.getHex()),this.distance!==void 0&&(t.object.distance=this.distance),this.angle!==void 0&&(t.object.angle=this.angle),this.decay!==void 0&&(t.object.decay=this.decay),this.penumbra!==void 0&&(t.object.penumbra=this.penumbra),this.shadow!==void 0&&(t.object.shadow=this.shadow.toJSON()),this.target!==void 0&&(t.object.target=this.target.uuid),t}}class $y extends Ru{constructor(e,t,n){super(e,n),this.isHemisphereLight=!0,this.type="HemisphereLight",this.position.copy(tn.DEFAULT_UP),this.updateMatrix(),this.groundColor=new st(t)}copy(e,t){return super.copy(e,t),this.groundColor.copy(e.groundColor),this}}const ac=new Gt,gd=new G,vd=new G;class Yy{constructor(e){this.camera=e,this.intensity=1,this.bias=0,this.normalBias=0,this.radius=1,this.blurSamples=8,this.mapSize=new qe(512,512),this.map=null,this.mapPass=null,this.matrix=new Gt,this.autoUpdate=!0,this.needsUpdate=!1,this._frustum=new Eu,this._frameExtents=new qe(1,1),this._viewportCount=1,this._viewports=[new en(0,0,1,1)]}getViewportCount(){return this._viewportCount}getFrustum(){return this._frustum}updateMatrices(e){const t=this.camera,n=this.matrix;gd.setFromMatrixPosition(e.matrixWorld),t.position.copy(gd),vd.setFromMatrixPosition(e.target.matrixWorld),t.lookAt(vd),t.updateMatrixWorld(),ac.multiplyMatrices(t.projectionMatrix,t.matrixWorldInverse),this._frustum.setFromProjectionMatrix(ac),n.set(.5,0,0,.5,0,.5,0,.5,0,0,.5,.5,0,0,0,1),n.multiply(ac)}getViewport(e){return this._viewports[e]}getFrameExtents(){return this._frameExtents}dispose(){this.map&&this.map.dispose(),this.mapPass&&this.mapPass.dispose()}copy(e){return this.camera=e.camera.clone(),this.intensity=e.intensity,this.bias=e.bias,this.radius=e.radius,this.mapSize.copy(e.mapSize),this}clone(){return new this.constructor().copy(this)}toJSON(){const e={};return this.intensity!==1&&(e.intensity=this.intensity),this.bias!==0&&(e.bias=this.bias),this.normalBias!==0&&(e.normalBias=this.normalBias),this.radius!==1&&(e.radius=this.radius),(this.mapSize.x!==512||this.mapSize.y!==512)&&(e.mapSize=this.mapSize.toArray()),e.camera=this.camera.toJSON(!1).object,delete e.camera.matrix,e}}class jy extends Yy{constructor(){super(new Aa(-5,5,5,-5,.5,500)),this.isDirectionalLightShadow=!0}}class Ky extends Ru{constructor(e,t){super(e,t),this.isDirectionalLight=!0,this.type="DirectionalLight",this.position.copy(tn.DEFAULT_UP),this.updateMatrix(),this.target=new tn,this.shadow=new jy}dispose(){this.shadow.dispose()}copy(e){return super.copy(e),this.target=e.target.clone(),this.shadow=e.shadow.clone(),this}}class Zy extends Ru{constructor(e,t){super(e,t),this.isAmbientLight=!0,this.type="AmbientLight"}}const _d=new Gt;class Jy{constructor(e,t,n=0,s=1/0){this.ray=new rl(e,t),this.near=n,this.far=s,this.camera=null,this.layers=new wu,this.params={Mesh:{},Line:{threshold:1},LOD:{},Points:{threshold:1},Sprite:{}}}set(e,t){this.ray.set(e,t)}setFromCamera(e,t){t.isPerspectiveCamera?(this.ray.origin.setFromMatrixPosition(t.matrixWorld),this.ray.direction.set(e.x,e.y,.5).unproject(t).sub(this.ray.origin).normalize(),this.camera=t):t.isOrthographicCamera?(this.ray.origin.set(e.x,e.y,(t.near+t.far)/(t.near-t.far)).unproject(t),this.ray.direction.set(0,0,-1).transformDirection(t.matrixWorld),this.camera=t):console.error("THREE.Raycaster: Unsupported camera type: "+t.type)}setFromXRController(e){return _d.identity().extractRotation(e.matrixWorld),this.ray.origin.setFromMatrixPosition(e.matrixWorld),this.ray.direction.set(0,0,-1).applyMatrix4(_d),this}intersectObject(e,t=!0,n=[]){return eu(e,this,n,t),n.sort(xd),n}intersectObjects(e,t=!0,n=[]){for(let s=0,r=e.length;s<r;s++)eu(e[s],this,n,t);return n.sort(xd),n}}function xd(i,e){return i.distance-e.distance}function eu(i,e,t,n){let s=!0;if(i.layers.test(e.layers)&&i.raycast(e,t)===!1&&(s=!1),s===!0&&n===!0){const r=i.children;for(let o=0,a=r.length;o<a;o++)eu(r[o],e,t,!0)}}class yd{constructor(e=1,t=0,n=0){return this.radius=e,this.phi=t,this.theta=n,this}set(e,t,n){return this.radius=e,this.phi=t,this.theta=n,this}copy(e){return this.radius=e.radius,this.phi=e.phi,this.theta=e.theta,this}makeSafe(){return this.phi=Math.max(1e-6,Math.min(Math.PI-1e-6,this.phi)),this}setFromVector3(e){return this.setFromCartesianCoords(e.x,e.y,e.z)}setFromCartesianCoords(e,t,n){return this.radius=Math.sqrt(e*e+t*t+n*n),this.radius===0?(this.theta=0,this.phi=0):(this.theta=Math.atan2(e,n),this.phi=Math.acos(bn(t/this.radius,-1,1))),this}clone(){return new this.constructor().copy(this)}}class Qy extends Fo{constructor(e=10,t=10,n=4473924,s=8947848){n=new st(n),s=new st(s);const r=t/2,o=e/t,a=e/2,l=[],c=[];for(let d=0,f=0,v=-a;d<=t;d++,v+=o){l.push(-a,0,v,a,0,v),l.push(v,0,-a,v,0,a);const g=d===r?n:s;g.toArray(c,f),f+=3,g.toArray(c,f),f+=3,g.toArray(c,f),f+=3,g.toArray(c,f),f+=3}const u=new Xn;u.setAttribute("position",new Mn(l,3)),u.setAttribute("color",new Mn(c,3));const h=new Ca({vertexColors:!0,toneMapped:!1});super(u,h),this.type="GridHelper"}dispose(){this.geometry.dispose(),this.material.dispose()}}typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("register",{detail:{revision:mu}}));typeof window<"u"&&(window.__THREE__?console.warn("WARNING: Multiple instances of Three.js being imported."):window.__THREE__=mu);var eb=Object.defineProperty,tb=(i,e,t)=>e in i?eb(i,e,{enumerable:!0,configurable:!0,writable:!0,value:t}):i[e]=t,nb=(i,e,t)=>(tb(i,e+"",t),t);class ib{constructor(){nb(this,"_listeners")}addEventListener(e,t){this._listeners===void 0&&(this._listeners={});const n=this._listeners;n[e]===void 0&&(n[e]=[]),n[e].indexOf(t)===-1&&n[e].push(t)}hasEventListener(e,t){if(this._listeners===void 0)return!1;const n=this._listeners;return n[e]!==void 0&&n[e].indexOf(t)!==-1}removeEventListener(e,t){if(this._listeners===void 0)return;const s=this._listeners[e];if(s!==void 0){const r=s.indexOf(t);r!==-1&&s.splice(r,1)}}dispatchEvent(e){if(this._listeners===void 0)return;const n=this._listeners[e.type];if(n!==void 0){e.target=this;const s=n.slice(0);for(let r=0,o=s.length;r<o;r++)s[r].call(this,e);e.target=null}}}var sb=Object.defineProperty,rb=(i,e,t)=>e in i?sb(i,e,{enumerable:!0,configurable:!0,writable:!0,value:t}):i[e]=t,$e=(i,e,t)=>(rb(i,typeof e!="symbol"?e+"":e,t),t);const To=new rl,bd=new rs,ab=Math.cos(70*(Math.PI/180)),Sd=(i,e)=>(i%e+e)%e;class ob extends ib{constructor(e,t){super(),$e(this,"object"),$e(this,"domElement"),$e(this,"enabled",!0),$e(this,"target",new G),$e(this,"minDistance",0),$e(this,"maxDistance",1/0),$e(this,"minZoom",0),$e(this,"maxZoom",1/0),$e(this,"minPolarAngle",0),$e(this,"maxPolarAngle",Math.PI),$e(this,"minAzimuthAngle",-1/0),$e(this,"maxAzimuthAngle",1/0),$e(this,"enableDamping",!1),$e(this,"dampingFactor",.05),$e(this,"enableZoom",!0),$e(this,"zoomSpeed",1),$e(this,"enableRotate",!0),$e(this,"rotateSpeed",1),$e(this,"enablePan",!0),$e(this,"panSpeed",1),$e(this,"screenSpacePanning",!0),$e(this,"keyPanSpeed",7),$e(this,"zoomToCursor",!1),$e(this,"autoRotate",!1),$e(this,"autoRotateSpeed",2),$e(this,"reverseOrbit",!1),$e(this,"reverseHorizontalOrbit",!1),$e(this,"reverseVerticalOrbit",!1),$e(this,"keys",{LEFT:"ArrowLeft",UP:"ArrowUp",RIGHT:"ArrowRight",BOTTOM:"ArrowDown"}),$e(this,"mouseButtons",{LEFT:or.ROTATE,MIDDLE:or.DOLLY,RIGHT:or.PAN}),$e(this,"touches",{ONE:lr.ROTATE,TWO:lr.DOLLY_PAN}),$e(this,"target0"),$e(this,"position0"),$e(this,"zoom0"),$e(this,"_domElementKeyEvents",null),$e(this,"getPolarAngle"),$e(this,"getAzimuthalAngle"),$e(this,"setPolarAngle"),$e(this,"setAzimuthalAngle"),$e(this,"getDistance"),$e(this,"getZoomScale"),$e(this,"listenToKeyEvents"),$e(this,"stopListenToKeyEvents"),$e(this,"saveState"),$e(this,"reset"),$e(this,"update"),$e(this,"connect"),$e(this,"dispose"),$e(this,"dollyIn"),$e(this,"dollyOut"),$e(this,"getScale"),$e(this,"setScale"),this.object=e,this.domElement=t,this.target0=this.target.clone(),this.position0=this.object.position.clone(),this.zoom0=this.object.zoom,this.getPolarAngle=()=>u.phi,this.getAzimuthalAngle=()=>u.theta,this.setPolarAngle=F=>{let le=Sd(F,2*Math.PI),U=u.phi;U<0&&(U+=2*Math.PI),le<0&&(le+=2*Math.PI);let re=Math.abs(le-U);2*Math.PI-re<re&&(le<U?le+=2*Math.PI:U+=2*Math.PI),h.phi=le-U,n.update()},this.setAzimuthalAngle=F=>{let le=Sd(F,2*Math.PI),U=u.theta;U<0&&(U+=2*Math.PI),le<0&&(le+=2*Math.PI);let re=Math.abs(le-U);2*Math.PI-re<re&&(le<U?le+=2*Math.PI:U+=2*Math.PI),h.theta=le-U,n.update()},this.getDistance=()=>n.object.position.distanceTo(n.target),this.listenToKeyEvents=F=>{F.addEventListener("keydown",Ae),this._domElementKeyEvents=F},this.stopListenToKeyEvents=()=>{this._domElementKeyEvents.removeEventListener("keydown",Ae),this._domElementKeyEvents=null},this.saveState=()=>{n.target0.copy(n.target),n.position0.copy(n.object.position),n.zoom0=n.object.zoom},this.reset=()=>{n.target.copy(n.target0),n.object.position.copy(n.position0),n.object.zoom=n.zoom0,n.object.updateProjectionMatrix(),n.dispatchEvent(s),n.update(),l=a.NONE},this.update=(()=>{const F=new G,le=new G(0,1,0),U=new Ws().setFromUnitVectors(e.up,le),re=U.clone().invert(),ie=new G,se=new Ws,_e=2*Math.PI;return function(){const ot=n.object.position;U.setFromUnitVectors(e.up,le),re.copy(U).invert(),F.copy(ot).sub(n.target),F.applyQuaternion(U),u.setFromVector3(F),n.autoRotate&&l===a.NONE&&Z(K()),n.enableDamping?(u.theta+=h.theta*n.dampingFactor,u.phi+=h.phi*n.dampingFactor):(u.theta+=h.theta,u.phi+=h.phi);let vt=n.minAzimuthAngle,Tt=n.maxAzimuthAngle;isFinite(vt)&&isFinite(Tt)&&(vt<-Math.PI?vt+=_e:vt>Math.PI&&(vt-=_e),Tt<-Math.PI?Tt+=_e:Tt>Math.PI&&(Tt-=_e),vt<=Tt?u.theta=Math.max(vt,Math.min(Tt,u.theta)):u.theta=u.theta>(vt+Tt)/2?Math.max(vt,u.theta):Math.min(Tt,u.theta)),u.phi=Math.max(n.minPolarAngle,Math.min(n.maxPolarAngle,u.phi)),u.makeSafe(),n.enableDamping===!0?n.target.addScaledVector(f,n.dampingFactor):n.target.add(f),n.zoomToCursor&&E||n.object.isOrthographicCamera?u.radius=ye(u.radius):u.radius=ye(u.radius*d),F.setFromSpherical(u),F.applyQuaternion(re),ot.copy(n.target).add(F),n.object.matrixAutoUpdate||n.object.updateMatrix(),n.object.lookAt(n.target),n.enableDamping===!0?(h.theta*=1-n.dampingFactor,h.phi*=1-n.dampingFactor,f.multiplyScalar(1-n.dampingFactor)):(h.set(0,0,0),f.set(0,0,0));let lt=!1;if(n.zoomToCursor&&E){let fn=null;if(n.object instanceof Sn&&n.object.isPerspectiveCamera){const zt=F.length();fn=ye(zt*d);const Ht=zt-fn;n.object.position.addScaledVector(L,Ht),n.object.updateMatrixWorld()}else if(n.object.isOrthographicCamera){const zt=new G(k.x,k.y,0);zt.unproject(n.object),n.object.zoom=Math.max(n.minZoom,Math.min(n.maxZoom,n.object.zoom/d)),n.object.updateProjectionMatrix(),lt=!0;const Ht=new G(k.x,k.y,0);Ht.unproject(n.object),n.object.position.sub(Ht).add(zt),n.object.updateMatrixWorld(),fn=F.length()}else console.warn("WARNING: OrbitControls.js encountered an unknown camera type - zoom to cursor disabled."),n.zoomToCursor=!1;fn!==null&&(n.screenSpacePanning?n.target.set(0,0,-1).transformDirection(n.object.matrix).multiplyScalar(fn).add(n.object.position):(To.origin.copy(n.object.position),To.direction.set(0,0,-1).transformDirection(n.object.matrix),Math.abs(n.object.up.dot(To.direction))<ab?e.lookAt(n.target):(bd.setFromNormalAndCoplanarPoint(n.object.up,n.target),To.intersectPlane(bd,n.target))))}else n.object instanceof Aa&&n.object.isOrthographicCamera&&(lt=d!==1,lt&&(n.object.zoom=Math.max(n.minZoom,Math.min(n.maxZoom,n.object.zoom/d)),n.object.updateProjectionMatrix()));return d=1,E=!1,lt||ie.distanceToSquared(n.object.position)>c||8*(1-se.dot(n.object.quaternion))>c?(n.dispatchEvent(s),ie.copy(n.object.position),se.copy(n.object.quaternion),lt=!1,!0):!1}})(),this.connect=F=>{n.domElement=F,n.domElement.style.touchAction="none",n.domElement.addEventListener("contextmenu",Te),n.domElement.addEventListener("pointerdown",J),n.domElement.addEventListener("pointercancel",ee),n.domElement.addEventListener("wheel",ve)},this.dispose=()=>{var F,le,U,re,ie,se;n.domElement&&(n.domElement.style.touchAction="auto"),(F=n.domElement)==null||F.removeEventListener("contextmenu",Te),(le=n.domElement)==null||le.removeEventListener("pointerdown",J),(U=n.domElement)==null||U.removeEventListener("pointercancel",ee),(re=n.domElement)==null||re.removeEventListener("wheel",ve),(ie=n.domElement)==null||ie.ownerDocument.removeEventListener("pointermove",oe),(se=n.domElement)==null||se.ownerDocument.removeEventListener("pointerup",ee),n._domElementKeyEvents!==null&&n._domElementKeyEvents.removeEventListener("keydown",Ae)};const n=this,s={type:"change"},r={type:"start"},o={type:"end"},a={NONE:-1,ROTATE:0,DOLLY:1,PAN:2,TOUCH_ROTATE:3,TOUCH_PAN:4,TOUCH_DOLLY_PAN:5,TOUCH_DOLLY_ROTATE:6};let l=a.NONE;const c=1e-6,u=new yd,h=new yd;let d=1;const f=new G,v=new qe,g=new qe,m=new qe,p=new qe,x=new qe,b=new qe,w=new qe,O=new qe,A=new qe,L=new G,k=new qe;let E=!1;const y=[],P={};function K(){return 2*Math.PI/60/60*n.autoRotateSpeed}function z(){return Math.pow(.95,n.zoomSpeed)}function Z(F){n.reverseOrbit||n.reverseHorizontalOrbit?h.theta+=F:h.theta-=F}function q(F){n.reverseOrbit||n.reverseVerticalOrbit?h.phi+=F:h.phi-=F}const Q=(()=>{const F=new G;return function(U,re){F.setFromMatrixColumn(re,0),F.multiplyScalar(-U),f.add(F)}})(),$=(()=>{const F=new G;return function(U,re){n.screenSpacePanning===!0?F.setFromMatrixColumn(re,1):(F.setFromMatrixColumn(re,0),F.crossVectors(n.object.up,F)),F.multiplyScalar(U),f.add(F)}})(),te=(()=>{const F=new G;return function(U,re){const ie=n.domElement;if(ie&&n.object instanceof Sn&&n.object.isPerspectiveCamera){const se=n.object.position;F.copy(se).sub(n.target);let _e=F.length();_e*=Math.tan(n.object.fov/2*Math.PI/180),Q(2*U*_e/ie.clientHeight,n.object.matrix),$(2*re*_e/ie.clientHeight,n.object.matrix)}else ie&&n.object instanceof Aa&&n.object.isOrthographicCamera?(Q(U*(n.object.right-n.object.left)/n.object.zoom/ie.clientWidth,n.object.matrix),$(re*(n.object.top-n.object.bottom)/n.object.zoom/ie.clientHeight,n.object.matrix)):(console.warn("WARNING: OrbitControls.js encountered an unknown camera type - pan disabled."),n.enablePan=!1)}})();function ge(F){n.object instanceof Sn&&n.object.isPerspectiveCamera||n.object instanceof Aa&&n.object.isOrthographicCamera?d=F:(console.warn("WARNING: OrbitControls.js encountered an unknown camera type - dolly/zoom disabled."),n.enableZoom=!1)}function de(F){ge(d/F)}function xe(F){ge(d*F)}function Ee(F){if(!n.zoomToCursor||!n.domElement)return;E=!0;const le=n.domElement.getBoundingClientRect(),U=F.clientX-le.left,re=F.clientY-le.top,ie=le.width,se=le.height;k.x=U/ie*2-1,k.y=-(re/se)*2+1,L.set(k.x,k.y,1).unproject(n.object).sub(n.object.position).normalize()}function ye(F){return Math.max(n.minDistance,Math.min(n.maxDistance,F))}function ne(F){v.set(F.clientX,F.clientY)}function ce(F){Ee(F),w.set(F.clientX,F.clientY)}function be(F){p.set(F.clientX,F.clientY)}function fe(F){g.set(F.clientX,F.clientY),m.subVectors(g,v).multiplyScalar(n.rotateSpeed);const le=n.domElement;le&&(Z(2*Math.PI*m.x/le.clientHeight),q(2*Math.PI*m.y/le.clientHeight)),v.copy(g),n.update()}function ke(F){O.set(F.clientX,F.clientY),A.subVectors(O,w),A.y>0?de(z()):A.y<0&&xe(z()),w.copy(O),n.update()}function Ve(F){x.set(F.clientX,F.clientY),b.subVectors(x,p).multiplyScalar(n.panSpeed),te(b.x,b.y),p.copy(x),n.update()}function Ne(F){Ee(F),F.deltaY<0?xe(z()):F.deltaY>0&&de(z()),n.update()}function pt(F){let le=!1;switch(F.code){case n.keys.UP:te(0,n.keyPanSpeed),le=!0;break;case n.keys.BOTTOM:te(0,-n.keyPanSpeed),le=!0;break;case n.keys.LEFT:te(n.keyPanSpeed,0),le=!0;break;case n.keys.RIGHT:te(-n.keyPanSpeed,0),le=!0;break}le&&(F.preventDefault(),n.update())}function N(){if(y.length==1)v.set(y[0].pageX,y[0].pageY);else{const F=.5*(y[0].pageX+y[1].pageX),le=.5*(y[0].pageY+y[1].pageY);v.set(F,le)}}function dt(){if(y.length==1)p.set(y[0].pageX,y[0].pageY);else{const F=.5*(y[0].pageX+y[1].pageX),le=.5*(y[0].pageY+y[1].pageY);p.set(F,le)}}function it(){const F=y[0].pageX-y[1].pageX,le=y[0].pageY-y[1].pageY,U=Math.sqrt(F*F+le*le);w.set(0,U)}function ct(){n.enableZoom&&it(),n.enablePan&&dt()}function Oe(){n.enableZoom&&it(),n.enableRotate&&N()}function Et(F){if(y.length==1)g.set(F.pageX,F.pageY);else{const U=ze(F),re=.5*(F.pageX+U.x),ie=.5*(F.pageY+U.y);g.set(re,ie)}m.subVectors(g,v).multiplyScalar(n.rotateSpeed);const le=n.domElement;le&&(Z(2*Math.PI*m.x/le.clientHeight),q(2*Math.PI*m.y/le.clientHeight)),v.copy(g)}function Xe(F){if(y.length==1)x.set(F.pageX,F.pageY);else{const le=ze(F),U=.5*(F.pageX+le.x),re=.5*(F.pageY+le.y);x.set(U,re)}b.subVectors(x,p).multiplyScalar(n.panSpeed),te(b.x,b.y),p.copy(x)}function We(F){const le=ze(F),U=F.pageX-le.x,re=F.pageY-le.y,ie=Math.sqrt(U*U+re*re);O.set(0,ie),A.set(0,Math.pow(O.y/w.y,n.zoomSpeed)),de(A.y),w.copy(O)}function I(F){n.enableZoom&&We(F),n.enablePan&&Xe(F)}function M(F){n.enableZoom&&We(F),n.enableRotate&&Et(F)}function J(F){var le,U;n.enabled!==!1&&(y.length===0&&((le=n.domElement)==null||le.ownerDocument.addEventListener("pointermove",oe),(U=n.domElement)==null||U.ownerDocument.addEventListener("pointerup",ee)),Ze(F),F.pointerType==="touch"?Ke(F):W(F))}function oe(F){n.enabled!==!1&&(F.pointerType==="touch"?me(F):we(F))}function ee(F){var le,U,re;Be(F),y.length===0&&((le=n.domElement)==null||le.releasePointerCapture(F.pointerId),(U=n.domElement)==null||U.ownerDocument.removeEventListener("pointermove",oe),(re=n.domElement)==null||re.ownerDocument.removeEventListener("pointerup",ee)),n.dispatchEvent(o),l=a.NONE}function W(F){let le;switch(F.button){case 0:le=n.mouseButtons.LEFT;break;case 1:le=n.mouseButtons.MIDDLE;break;case 2:le=n.mouseButtons.RIGHT;break;default:le=-1}switch(le){case or.DOLLY:if(n.enableZoom===!1)return;ce(F),l=a.DOLLY;break;case or.ROTATE:if(F.ctrlKey||F.metaKey||F.shiftKey){if(n.enablePan===!1)return;be(F),l=a.PAN}else{if(n.enableRotate===!1)return;ne(F),l=a.ROTATE}break;case or.PAN:if(F.ctrlKey||F.metaKey||F.shiftKey){if(n.enableRotate===!1)return;ne(F),l=a.ROTATE}else{if(n.enablePan===!1)return;be(F),l=a.PAN}break;default:l=a.NONE}l!==a.NONE&&n.dispatchEvent(r)}function we(F){if(n.enabled!==!1)switch(l){case a.ROTATE:if(n.enableRotate===!1)return;fe(F);break;case a.DOLLY:if(n.enableZoom===!1)return;ke(F);break;case a.PAN:if(n.enablePan===!1)return;Ve(F);break}}function ve(F){n.enabled===!1||n.enableZoom===!1||l!==a.NONE&&l!==a.ROTATE||(F.preventDefault(),n.dispatchEvent(r),Ne(F),n.dispatchEvent(o))}function Ae(F){n.enabled===!1||n.enablePan===!1||pt(F)}function Ke(F){switch(Me(F),y.length){case 1:switch(n.touches.ONE){case lr.ROTATE:if(n.enableRotate===!1)return;N(),l=a.TOUCH_ROTATE;break;case lr.PAN:if(n.enablePan===!1)return;dt(),l=a.TOUCH_PAN;break;default:l=a.NONE}break;case 2:switch(n.touches.TWO){case lr.DOLLY_PAN:if(n.enableZoom===!1&&n.enablePan===!1)return;ct(),l=a.TOUCH_DOLLY_PAN;break;case lr.DOLLY_ROTATE:if(n.enableZoom===!1&&n.enableRotate===!1)return;Oe(),l=a.TOUCH_DOLLY_ROTATE;break;default:l=a.NONE}break;default:l=a.NONE}l!==a.NONE&&n.dispatchEvent(r)}function me(F){switch(Me(F),l){case a.TOUCH_ROTATE:if(n.enableRotate===!1)return;Et(F),n.update();break;case a.TOUCH_PAN:if(n.enablePan===!1)return;Xe(F),n.update();break;case a.TOUCH_DOLLY_PAN:if(n.enableZoom===!1&&n.enablePan===!1)return;I(F),n.update();break;case a.TOUCH_DOLLY_ROTATE:if(n.enableZoom===!1&&n.enableRotate===!1)return;M(F),n.update();break;default:l=a.NONE}}function Te(F){n.enabled!==!1&&F.preventDefault()}function Ze(F){y.push(F)}function Be(F){delete P[F.pointerId];for(let le=0;le<y.length;le++)if(y[le].pointerId==F.pointerId){y.splice(le,1);return}}function Me(F){let le=P[F.pointerId];le===void 0&&(le=new qe,P[F.pointerId]=le),le.set(F.pageX,F.pageY)}function ze(F){const le=F.pointerId===y[0].pointerId?y[1]:y[0];return P[le.pointerId]}this.dollyIn=(F=z())=>{xe(F),n.update()},this.dollyOut=(F=z())=>{de(F),n.update()},this.getScale=()=>d,this.setScale=F=>{ge(F),n.update()},this.getZoomScale=()=>z(),t!==void 0&&this.connect(t),this.update()}}class lb{constructor(){R(this,"handlers",new Map);R(this,"onceHandlers",new Map);R(this,"messageBuffer",new Map)}register(e,t){if(!this.handlers.has(e)){this.handlers.set(e,new Set);const n=this.messageBuffer.get(e);n&&(n.forEach(s=>Promise.resolve(t(s))),this.messageBuffer.delete(e))}return this.handlers.get(e).add(t),()=>this.unregister(e,t)}once(e,t){return this.onceHandlers.has(e)||this.onceHandlers.set(e,new Set),this.onceHandlers.get(e).add(t),()=>this.unregisterOnce(e,t)}unregister(e,t){var n;(n=this.handlers.get(e))==null||n.delete(t)}unregisterOnce(e,t){var n;(n=this.onceHandlers.get(e))==null||n.delete(t)}buffer(e){const{type:t}=e;this.messageBuffer.has(t)||this.messageBuffer.set(t,[]),this.messageBuffer.get(t).push(e)}async dispatch(e){const{type:t,...n}=e,s=this.handlers.get(t);if(s&&s.size>0){await Promise.all(Array.from(s).map(o=>Promise.resolve(o(n))));return}const r=this.onceHandlers.get(t);if(r&&r.size>0){await Promise.all(Array.from(r).map(o=>Promise.resolve(o(n)))),this.onceHandlers.delete(t);return}this.buffer(e)}clear(){this.handlers.clear(),this.onceHandlers.clear(),this.messageBuffer.clear()}getBuffered(e){return this.messageBuffer.get(e)??[]}hasHandlers(e){var t;return(((t=this.handlers.get(e))==null?void 0:t.size)??0)>0}}class cb{constructor(e,t){R(this,"ws",null);R(this,"url");R(this,"router");R(this,"reconnectDelay",1e3);R(this,"maxReconnectDelay",3e4);R(this,"reconnectAttempts",0);R(this,"shouldReconnect",!0);R(this,"state","disconnected");R(this,"stateListeners",new Set);R(this,"messageQueue",[]);R(this,"heartbeatInterval",null);R(this,"lastPong",0);R(this,"missedPongs",0);R(this,"maxMissedPongs",3);R(this,"heartbeatIntervalMs",15e3);this.url=e,this.router=t}get connectionState(){return this.state}onStateChange(e){return this.stateListeners.add(e),e(this.state),()=>this.stateListeners.delete(e)}setState(e){if(this.state===e)return;const t=this.state;this.state=e,console.log(`[WS] State: ${t} → ${e}`),this.stateListeners.forEach(n=>n(e))}connect(){var n;if(((n=this.ws)==null?void 0:n.readyState)===WebSocket.OPEN||this.state==="connecting")return;this.setState("connecting");const t=`${window.location.protocol==="https:"?"wss:":"ws:"}//${window.location.host}${this.url}`;this.ws=new WebSocket(t),this.ws.binaryType="arraybuffer",this.ws.onopen=()=>{console.log("[WS] Connected"),this.reconnectAttempts=0,this.reconnectDelay=1e3,this.missedPongs=0,this.lastPong=Date.now(),this.setState("connected"),this.startHeartbeat(),this.flushQueue()},this.ws.onmessage=async s=>{try{const r=JSON.parse(s.data);if(r.type==="pong"){this.lastPong=Date.now(),this.missedPongs=0;return}await this.router.dispatch(r)}catch(r){console.error("[WS] Failed to parse message:",r)}},this.ws.onclose=s=>{console.log("[WS] Disconnected:",s.code,s.reason),this.stopHeartbeat(),this.setState("disconnected"),this.shouldReconnect&&this.scheduleReconnect()},this.ws.onerror=s=>{console.error("[WS] Error:",s)}}startHeartbeat(){this.stopHeartbeat(),this.heartbeatInterval=window.setInterval(()=>{var e;if(((e=this.ws)==null?void 0:e.readyState)===WebSocket.OPEN){if(this.missedPongs++,this.missedPongs>this.maxMissedPongs){console.warn("[WS] Heartbeat failed - closing connection"),this.ws.close(1e3,"Heartbeat timeout");return}this.ws.send(JSON.stringify({type:"ping"}))}},this.heartbeatIntervalMs)}stopHeartbeat(){this.heartbeatInterval!==null&&(clearInterval(this.heartbeatInterval),this.heartbeatInterval=null)}scheduleReconnect(){if(this.state==="reconnecting")return;this.setState("reconnecting");const e=Math.min(this.reconnectDelay*Math.pow(1.5,this.reconnectAttempts),this.maxReconnectDelay),t=e*.25*(Math.random()*2-1),n=Math.max(100,e+t);this.reconnectAttempts++,console.log(`[WS] Reconnecting in ${Math.round(n)}ms (attempt ${this.reconnectAttempts})`),setTimeout(()=>this.connect(),n)}send(e){var t;((t=this.ws)==null?void 0:t.readyState)===WebSocket.OPEN?this.ws.send(JSON.stringify(e)):this.messageQueue.push(e)}flushQueue(){var e;for(;this.messageQueue.length>0&&((e=this.ws)==null?void 0:e.readyState)===WebSocket.OPEN;){const t=this.messageQueue.shift();this.ws.send(JSON.stringify(t))}}async request(e,t=5e3){return new Promise((n,s)=>{const r=`${e.type}_${Date.now()}_${Math.random().toString(36).slice(2,9)}`,o={...e,request_id:r},a=this.router.once(r,c=>{clearTimeout(l),c.error?s(new Error(c.error)):n(c.data)}),l=setTimeout(()=>{a(),s(new Error(`Request timeout: ${e.type}`))},t);this.send(o)})}disconnect(){var e;this.shouldReconnect=!1,this.stopHeartbeat(),(e=this.ws)==null||e.close(1e3,"Client disconnect"),this.ws=null,this.setState("disconnected")}async waitForConnection(e=1e4){return this.state==="connected"?!0:new Promise(t=>{const n=setTimeout(()=>{s(),t(!1)},e),s=this.onStateChange(r=>{r==="connected"&&(clearTimeout(n),s(),t(!0))})})}get isConnected(){var e;return((e=this.ws)==null?void 0:e.readyState)===WebSocket.OPEN}getConnectionQuality(){return{state:this.state,latency:this.lastPong?Date.now()-this.lastPong:-1,missedPongs:this.missedPongs}}}const Yt=new lb,fs=new cb("/ws",Yt);let tp=null;function ub(i){tp=i}function Md(){return tp}class hb{constructor(){R(this,"components",new Map);R(this,"initialized",!1);R(this,"initOrder",[])}register(e){const t=e.name||e.constructor.name;this.components.has(t)&&console.warn(`[ComponentRegistry] Component "${t}" already registered, replacing`),this.components.set(t,e),this.initialized&&e.init().catch(console.error)}unregister(e){const t=this.components.get(e);t&&(t.destroy().catch(console.error),this.components.delete(e))}computeInitOrder(){const e=new Set,t=new Set,n=[],s=r=>{if(e.has(r))return;if(t.has(r)){console.warn(`[ComponentRegistry] Circular dependency detected: ${r}`);return}t.add(r);const o=this.components.get(r);if(o!=null&&o.dependencies)for(const a of o.dependencies)this.components.has(a)&&s(a);t.delete(r),e.add(r),n.push(r)};for(const r of this.components.keys())s(r);return n}async initAll(){if(!this.initialized){this.initOrder=this.computeInitOrder(),this.initialized=!0;for(const e of this.initOrder){const t=this.components.get(e);if(t)try{await t.init(),console.log(`[ComponentRegistry] Initialized: ${e}`)}catch(n){console.error(`[ComponentRegistry] Failed to initialize ${e}:`,n)}}}}async destroyAll(){for(const e of[...this.initOrder].reverse()){const t=this.components.get(e);if(t)try{await t.destroy(),console.log(`[ComponentRegistry] Destroyed: ${e}`)}catch(n){console.error(`[ComponentRegistry] Failed to destroy ${e}:`,n)}}this.components.clear(),this.initialized=!1,this.initOrder=[]}get(e){return this.components.get(e)}list(){return this.initOrder.length>0?this.initOrder:Array.from(this.components.keys())}async healthCheck(){const e={};for(const[t,n]of this.components)if(n.healthCheck)try{e[t]=await Promise.resolve(n.healthCheck())}catch{e[t]=!1}else e[t]=!0;return e}async isHealthy(){const e=await this.healthCheck();return Object.values(e).every(t=>t)}}const qn=new hb;typeof window<"u"&&(document.addEventListener("DOMContentLoaded",()=>{qn.initAll().catch(console.error)}),window.addEventListener("beforeunload",()=>{qn.destroyAll().catch(console.error)}));const Ye={};function gn(i,e){Ye[i]=e}const Ti=[{id:"chart-pareto",label:"Pareto frontier",group:"Charts",key:"p",run:()=>{var i;return(i=Ye["chart-pareto"])==null?void 0:i.call(Ye)}},{id:"chart-ablation",label:"Ablation chart",group:"Charts",key:"a",run:()=>{var i;return(i=Ye["chart-ablation"])==null?void 0:i.call(Ye)}},{id:"chart-variability",label:"Variability chart",group:"Charts",key:"s",run:()=>{var i;return(i=Ye["chart-variability"])==null?void 0:i.call(Ye)}},{id:"control-play",label:"Play / Pause",group:"Run Control",key:" ",run:()=>{var i;return(i=Ye["control-play"])==null?void 0:i.call(Ye)}},{id:"control-step",label:"Step one batch",group:"Run Control",key:"w",run:()=>{var i;return(i=Ye["control-step"])==null?void 0:i.call(Ye)}},{id:"control-stop",label:"Stop run",group:"Run Control",key:"x",run:()=>{var i;return(i=Ye["control-stop"])==null?void 0:i.call(Ye)}},{id:"control-panel",label:"Control panel",group:"Run Control",key:"z",run:()=>{var i;return(i=Ye["control-panel"])==null?void 0:i.call(Ye)}},{id:"panel-hud",label:"Mission Control (HUD)",group:"Panels",key:"h",run:()=>{var i;return(i=Ye["panel-hud"])==null?void 0:i.call(Ye)}},{id:"panel-rail",label:"Live Rail",group:"Panels",key:"r",run:()=>{var i;return(i=Ye["panel-rail"])==null?void 0:i.call(Ye)}},{id:"panel-caption",label:"Caption",group:"Panels",key:"c",run:()=>{var i;return(i=Ye["panel-caption"])==null?void 0:i.call(Ye)}},{id:"panel-legend",label:"Legend",group:"Panels",key:"q",run:()=>{var i;return(i=Ye["panel-legend"])==null?void 0:i.call(Ye)}},{id:"view-cycle",label:"Cycle stage views",group:"Stage",key:"v",run:()=>{var i;return(i=Ye["view-cycle"])==null?void 0:i.call(Ye)}},{id:"cell-replicate",label:"Replicate (queue remaining seeds)",group:"Cell Actions",chord:"shift+r",when:"cell-selected",run:()=>{var i;return(i=Ye["cell-replicate"])==null?void 0:i.call(Ye)}},{id:"cell-preregister",label:"Preregister (confirm protocol)",group:"Cell Actions",chord:"shift+p",when:"cell-selected",run:()=>{var i;return(i=Ye["cell-preregister"])==null?void 0:i.call(Ye)}},{id:"cell-quest",label:"Adopt as Quest (new run)",group:"Cell Actions",chord:"shift+q",when:"cell-selected",run:()=>{var i;return(i=Ye["cell-quest"])==null?void 0:i.call(Ye)}},{id:"help",label:"Show help",group:"General",chord:"shift+/",run:()=>{var i;return(i=Ye.help)==null?void 0:i.call(Ye)}},{id:"escape",label:"Close drawer / dismiss",group:"General",key:"escape",run:()=>{var i;return(i=Ye.escape)==null?void 0:i.call(Ye)}}];function np(){return Ti}function db(){const i=new Set;for(const e of Ti)if(e.key&&i.add(e.key.toLowerCase()),e.chord){const t=e.chord.match(/shift\+(.+)/);t&&i.add(t[1].toLowerCase())}return i}function fb(){const i={};for(const e of Ti)if(e.group==="Panels"&&e.key){const t=e.id.replace("panel-","");i[t]=e.key}return i}function pb(){const i={};for(const e of Ti)if(e.group==="Charts"&&e.key){const t=e.id.replace("chart-","");i[t]=e.key}return i}function mb(){const i={};for(const e of Ti)if(e.group==="Run Control"&&e.key){const t=e.id.replace("control-","");i[t]=e.key}return i}function gb(){const i=Ti.find(e=>e.id==="view-cycle");return(i==null?void 0:i.key)??"v"}const qs=fb(),oc=pb(),wd=mb(),vb=gb(),tu=db();new Set("abcdefghijklmnopqrstuvwxyz".split("").filter(i=>!tu.has(i)));function vs(i){const{id:e,title:t,glyph:n,key:s,body:r,className:o="",dock:a,defaultOpen:l=!1,onToggle:c}=i,u=document.getElementById("ui-overlay");if(!u)throw new Error("ui-overlay not found — panels must init after DOM ready");const h=document.createElement("div");h.id=e,h.className=`panel ${o}`.trim(),h.dataset.dock=a??"floating",h.setAttribute("role","dialog"),h.setAttribute("aria-label",t),h.setAttribute("aria-modal","false"),h.innerHTML=`
    <header class="panel-header">
      <span class="panel-title">${t}</span>
      ${s?`<kbd class="panel-key-hint">${s.toUpperCase()}</kbd>`:'<span class="panel-key-hint"></span>'}
    </header>
    <div class="panel-body">${r}</div>
  `;const d=h.querySelector(".panel-header"),f=rp(()=>{Rt.toggle(e)});f.style.position="absolute",f.style.top="8px",f.style.right="8px",d.appendChild(f),u.appendChild(h),su(h,!l),a&&qr.registerPanel(e,{dock:a,defaultOpen:l});const v=Rt.onChange(()=>{const m=Rt.get(e);if(m){const p=!m.isOpen(),x=h.classList.contains("panel-hidden");p!==x&&(su(h,p),qr.setPanelOpen(e,!p),c==null||c(!p))}});h.__panelShellUnsubscribe=v;const g=new MutationObserver(()=>{h.classList.contains("panel-hidden")||d.focus()});return g.observe(h,{attributes:!0,attributeFilter:["class"]}),h.__panelShellObserver=g,h}const us={gradient:"#58a6ff",pepita:"#d4a843",random_projections:"#f78166",local_goodness:"#a371f7",thermodynamic_contrast:"#3fb950",contrastive:"#ff7b72",hebbian:"#79c0ff",predictive:"#d2a8ff"},he={bg:"#0a0e14",border:"#2a3a4a",text_primary:"#e8ecf0",text_secondary:"#8b98a8",text_muted:"#5a6a7a",gradient:"#58a6ff",thermodynamic_contrast:"#3fb950",measured:"#d4a843",legal_unmeasured:"#58a6ff",void:"#f85149",pareto:"#e8ecf0",chance_line:"#f85149",ok:"#3fb950",warn:"#d29922",error:"#f85149",passed:"#3fb950",insufficient:"#d29922",rejected:"#f85149",ramp_low:"#1f3a5f",ramp_mid:"#58a6ff",ramp_high:"#d4a843"};class _b{constructor(){R(this,"metricsByRun",new Map);R(this,"selectedRunId",null);R(this,"chosenByReader",!1);R(this,"listeners",[])}observe(e,t){this.metricsByRun.set(e,t),this.chosenByReader||(this.selectedRunId=this.newestRunId()),this.notify()}select(e){this.chosenByReader=!0,this.selectedRunId=e,this.notify()}get selectedId(){return this.selectedRunId}get selected(){return this.selectedRunId?this.metricsByRun.get(this.selectedRunId)??null:null}get runs(){return Array.from(this.metricsByRun.entries())}onChange(e){this.listeners.push(e)}notify(){this.listeners.forEach(e=>e(this.selectedRunId,this.selected))}newestRunId(){let e=null,t=-1/0;if(this.metricsByRun.forEach((s,r)=>{var l;const o=(l=s.run)==null?void 0:l.started_at,a=o?Date.parse(o):Number.NaN;Number.isNaN(a)||a>=t&&(t=a,e=r)}),e)return e;const n=this.metricsByRun.keys().next();return n.done?null:n.value}}const Vn=new _b,xb={substrate:{display_name:"Substrate",description:"Physical or computational substrate",primitives:[{name:"digital",summary:"Digital substrate: exact arithmetic, full precision",available:!0},{name:"analog",summary:"Analog substrate: continuous-valued physical state",available:!0},{name:"memristive",summary:"Memristive substrate: conductance, IR-drop, noise",available:!0},{name:"neuromorphic",summary:"Neuromorphic substrate: asynchronous spike events",available:!0},{name:"optical",summary:"Photonic substrate: phase/amplitude modulation",available:!0},{name:"quantum",summary:"Quantum substrate: unitary gate simulation",available:!0},{name:"complex",summary:"Complex-valued substrate",available:!0},{name:"sparse",summary:"Sparse substrate: sparsity-masked state",available:!0},{name:"ternary",summary:"Ternary substrate: weights in {-alpha, 0, +alpha}",available:!0}]},geometry:{display_name:"Geometry",description:"Network architecture and connectivity",primitives:[{name:"feedforward",summary:"Feedforward DAG (MLP/CNN)",available:!0},{name:"recurrent",summary:"Recurrent attractor (Hopfield/EqProp)",available:!0},{name:"causal_transformer",summary:"Causal transformer with KV cache",available:!0},{name:"tile",summary:"TileNet modular tile mesh",available:!0},{name:"tile_mesh",summary:"TileNet mesh topology",available:!0},{name:"conv",summary:"Convolutional geometry",available:!0},{name:"graph",summary:"Arbitrary node-edge fabric (FabricPC)",available:!0},{name:"attention",summary:"Attention geometry",available:!0},{name:"spatial_lattice",summary:"3-D spatial lattice (neural_cube)",available:!0},{name:"nca",summary:"Neural cellular automaton fabric",available:!0},{name:"ntm",summary:"Neural Turing Machine tape",available:!0}]},dynamics:{display_name:"Dynamics",description:"State evolution and settling",primitives:[{name:"energy_minimization",summary:"Equilibrium propagation energy minimization",available:!0},{name:"predictive_settling",summary:"Predictive coding settling",available:!0},{name:"error_predictive_coding",summary:"Error predictive coding",available:!0},{name:"spike_integration",summary:"LIF/Izhikevich spike integration",available:!0},{name:"instantaneous",summary:"Instantaneous pass (FF/Backprop)",available:!0},{name:"diffusion",summary:"Continuous-time diffusion settling",available:!0},{name:"lazy",summary:"Lazy/on-demand state dynamics",available:!0},{name:"pc_alm",summary:"Augmented Lagrangian predictive coding",available:!0}]},plasticity:{display_name:"Plasticity",description:"Local learning and adaptation",primitives:[{name:"null",summary:"Null plasticity (5-D slice)",available:!0},{name:"routing",summary:"Routing plasticity: state-dependent gating",available:!0},{name:"fast_weights",summary:"Fast-weight episode-local memory",available:!0},{name:"substrate_coupled",summary:"Physical substrate-coupled plasticity",available:!0},{name:"rule_state",summary:"Rule-state plasticity (Z3)",available:!0},{name:"temporal_psi",summary:"Trace-decayed supervised psi",available:!0},{name:"conflict_adaptive",summary:"Conflict-adaptive psi",available:!0}]},credit:{display_name:"Credit Assignment",description:"How learning signals reach parameters",primitives:[{name:"thermodynamic_contrast",summary:"EqProp free/nudged contrast (Scellier-Bengio)",available:!0},{name:"random_projections",summary:"Fixed random feedback (FA/DFA)",available:!0},{name:"local_goodness",summary:"Forward-Forward / PEPITA goodness",available:!0},{name:"local_contrastive",summary:"Local contrastive credit",available:!0},{name:"temporal_trace",summary:"Hebbian/STDP temporal trace",available:!0},{name:"target_inversion",summary:"Target propagation inversion",available:!0},{name:"homeostatic",summary:"Autonomous Lipschitz scaling",available:!0},{name:"pepita",summary:"PEPITA input-modulation credit",available:!0},{name:"gradient",summary:"Backprop gradient credit (ruler reference)",available:!0},{name:"pc_alm",summary:"PC-ALM primal-dual credit",available:!0}]},update:{display_name:"Update Rule",description:"How parameters are updated",primitives:[{name:"euclidean",summary:"SGD/Adam Euclidean update",available:!0},{name:"adam",summary:"Adam adaptive moment",available:!0},{name:"local_adam",summary:"Local Adam",available:!0},{name:"ortho_adam",summary:"Orthogonal Adam",available:!0},{name:"riemannian_orthogonal",summary:"Riemannian orthogonal update (Muon-family)",available:!0},{name:"muon",summary:"Muon update",available:!0},{name:"lion",summary:"Lion optimizer",available:!0},{name:"spectral_constrained",summary:"Spectral-norm constrained update",available:!0},{name:"mean_norm",summary:"Mean-norm update",available:!0},{name:"elastic_consolidation",summary:"EWC elastic consolidation",available:!0},{name:"natural_gradient",summary:"Natural gradient (Fisher)",available:!0},{name:"role_split",summary:"Role-split update",available:!0}]}},yb={axes:xb},ip=.72,sp=.86;function bb(i,e,t,n,s){const{camera:r,controls:o}=i,a=r.position.clone().sub(o.target);a.lengthSq()===0&&a.set(.4,.5,.8),a.normalize();const l=a.clone().negate(),c=new G().crossVectors(l,new G(0,1,0)).normalize(),u=new G().crossVectors(c,l).normalize(),h=Math.tan((r.fov??60)*Math.PI/360),d=h*(r.aspect||1),f=h*sp,v=d*ip;let g=0;[e.x,t.x].forEach(m=>{[e.y,t.y].forEach(p=>{[e.z,t.z].forEach(x=>{const b=new G(m,p,x),w=Math.max(Math.abs(b.dot(c))/v,Math.abs(b.dot(u))/f)+b.dot(a);g=Math.max(g,w)})})}),g*=1.06,n.add(c.clone().multiplyScalar(.28*d*g)).add(u.clone().multiplyScalar(-.14*h*g)),o.target.copy(n),r.position.copy(n).add(a.clone().multiplyScalar(g)),o.update()}const Oa=["credit","geometry","dynamics","substrate","plasticity","update"];function Yo(i,e,t){return`${i}|${e}|${t}`}function Ra(i){return i.length===0?0:i.reduce((e,t)=>e+t,0)/i.length}function Sb(i){if(i.length<2)return 0;const e=Ra(i),t=i.reduce((n,s)=>n+(s-e)**2,0)/(i.length-1);return Math.sqrt(t)}function Mb(i){const e=new Map;for(const t of i)for(const n of t){const s=e.get(n.epoch)??[];s.push(n.val_acc),e.set(n.epoch,s)}return Array.from(e.entries()).sort((t,n)=>t[0]-n[0]).map(([t,n])=>({epoch:t,val_acc:Ra(n)}))}function wb(i,e){const t=new Map;return i.cells.forEach(n=>{t.set(Yo(n.coordinate[e.x],n.coordinate[e.y],n.coordinate[e.z]),n)}),t}function Eb(i,e){const t=new Map;return((i==null?void 0:i.records)??[]).forEach((s,r)=>{var u;const o=s==null?void 0:s.coordinate;if(!o)return;const a=Yo(o[e.x],o[e.y],o[e.z]);let l=t.get(a);l||(l={acc:[],walltime:[],params:[],curves:[],pareto:!1,coordinate:{...o},seeds:0},t.set(a,l)),l.seeds+=1;const c=s.payload??{};if(typeof c.val_acc=="number"&&l.acc.push(c.val_acc),typeof c.walltime_s=="number"&&l.walltime.push(c.walltime_s),typeof c.param_count=="number"&&l.params.push(c.param_count),Array.isArray(c.convergence_curve)){const h=c.convergence_curve.filter(d=>typeof(d==null?void 0:d.epoch)=="number"&&typeof(d==null?void 0:d.val_acc)=="number").map(d=>({epoch:d.epoch,val_acc:d.val_acc}));h.length>0&&l.curves.push(h)}(u=i==null?void 0:i.pareto)!=null&&u[r]&&(l.pareto=!0)}),t}function Ed(i){const e={credit:new Set,geometry:new Set,dynamics:new Set,substrate:new Set,plasticity:new Set,update:new Set};i.forEach(n=>{const s=n==null?void 0:n.coordinate;s&&Oa.forEach(r=>{const o=s[r];typeof o=="string"&&o.length>0&&e[r].add(o)})});const t={};return Oa.forEach(n=>{t[n]=Array.from(e[n]).sort()}),t}class Tb{constructor(){R(this,"runId",null);R(this,"metrics",null);R(this,"axes",{x:"credit",y:"geometry",z:"dynamics"});R(this,"space",null);R(this,"spaceCells",new Map);R(this,"aggregates",new Map);R(this,"values",Ed([]));R(this,"chance",.1);R(this,"requiredSeeds",0);R(this,"gate",null);R(this,"timeline",null);R(this,"account",null);R(this,"flow",null);R(this,"attribution",null);R(this,"dynamics",null);R(this,"multirun",null);R(this,"trainedDynamics",null);R(this,"spaceRequest","");R(this,"accountRequest","");R(this,"attributionRequest","");R(this,"flowRequest","");R(this,"dynamicsRun","");R(this,"dynamicsAsking",!1);R(this,"trainedDynamicsRun","");R(this,"trainedDynamicsAsking",!1);R(this,"multirunRequest","");R(this,"multirunAsking",!1);R(this,"timelineRun","");R(this,"timelineStale",!0);R(this,"timelineTimer",null);R(this,"listeners",[]);Vn.onChange((e,t)=>{this.absorb(e,t)}),Yt.register("pipeline_event",()=>this.scheduleTimeline())}onChange(e){this.listeners.push(e)}notify(e){this.listeners.forEach(t=>t(e))}async absorb(e,t){this.runId=e,this.metrics=t,t&&(typeof t.chance=="number"&&(this.chance=t.chance),typeof t.required_seeds=="number"&&(this.requiredSeeds=t.required_seeds),t.gate&&(this.gate=t.gate,typeof t.gate.required_seeds_per_group=="number"&&(this.requiredSeeds=t.gate.required_seeds_per_group)),this.values=Ed(t.records??[])),this.recomputeEvidence(),await this.syncSpace(),this.syncAccount(),this.syncAttribution(),this.syncTimeline(),this.syncDynamics(),this.syncTrainedDynamics()}setAxes(e){this.axes=e,this.notify("axes"),this.recomputeEvidence(),this.syncSpace()}recomputeEvidence(){this.aggregates=Eb(this.metrics,this.axes),this.notify("evidence")}async syncSpace(){if(!this.runId)return;const e=[this.runId,this.axes.x,this.axes.y,this.axes.z,...Oa.map(n=>this.values[n].join(","))].join("|");if(e===this.spaceRequest)return;const t=await this.fetchSpace();t&&(this.spaceRequest=e,this.space=t,this.spaceCells=wb(t,this.axes),this.notify("space"))}async fetchSpace(){try{const e=await fetch(`/api/cells/${this.runId}/space`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({axes:[this.axes.x,this.axes.y,this.axes.z]})});return e.ok?await e.json():(console.warn("[StageState] The space was refused",e.status),null)}catch(e){return console.warn("[StageState] The space could not be read",e),null}}async syncAccount(){var n,s;if(!this.runId){this.account=null,this.accountRequest="";return}const e=((s=(n=this.metrics)==null?void 0:n.records)==null?void 0:s.length)??0,t=`${this.runId}|${e}`;if(t!==this.accountRequest)try{const r=await fetch(`/api/runs/${encodeURIComponent(this.runId)}/account`);if(!r.ok){console.warn("[StageState] The account was refused",r.status);return}this.account=await r.json(),this.accountRequest=t,this.notify("evidence")}catch(r){console.warn("[StageState] The account could not be read",r)}}async syncTimeline(){if(!this.runId){this.timeline=null,this.timelineRun="";return}if(!(!this.timelineStale&&this.timelineRun===this.runId))try{const e=await fetch(`/api/events?run_id=${encodeURIComponent(this.runId)}`);if(!e.ok){console.warn("[StageState] The timeline was refused",e.status);return}this.timeline=await e.json(),this.timelineRun=this.runId,this.timelineStale=!1,this.notify("events"),this.syncFlow()}catch(e){console.warn("[StageState] The timeline could not be read",e)}}async syncFlow(){var n;if(!this.runId){this.flow=null,this.flowRequest="";return}const e=((n=this.timeline)==null?void 0:n.events.length)??0,t=`${this.runId}|${e}`;if(t!==this.flowRequest)try{const s=await fetch(`/api/runs/${encodeURIComponent(this.runId)}/flow`);if(!s.ok){console.warn("[StageState] The flow was refused",s.status);return}this.flow=await s.json(),this.flowRequest=t,this.notify("events")}catch(s){console.warn("[StageState] The flow could not be read",s)}}async syncAttribution(){var n,s;if(!this.runId){this.attribution=null,this.attributionRequest="";return}const e=((s=(n=this.metrics)==null?void 0:n.records)==null?void 0:s.length)??0,t=`${this.runId}|${e}`;if(t!==this.attributionRequest)try{const r=await fetch(`/api/runs/${encodeURIComponent(this.runId)}/attribution`);if(!r.ok){console.warn("[StageState] The attribution was refused",r.status);return}this.attribution=await r.json(),this.attributionRequest=t,this.notify("evidence")}catch(r){console.warn("[StageState] The attribution could not be read",r)}}async syncDynamics(){if(!this.runId){this.dynamics=null,this.dynamicsRun="";return}if(!(this.dynamicsRun===this.runId||this.dynamicsAsking)){this.dynamicsAsking=!0;try{const e=await fetch(`/api/runs/${encodeURIComponent(this.runId)}/dynamics`);if(!e.ok){console.warn("[StageState] The dynamics were refused",e.status);return}const t=await e.json();this.dynamics=t,t.cell&&(this.dynamicsRun=this.runId),this.notify("evidence")}catch(e){console.warn("[StageState] The dynamics could not be read",e)}finally{this.dynamicsAsking=!1}}}async syncTrainedDynamics(){if(!this.runId){this.trainedDynamics=null,this.trainedDynamicsRun="";return}if(!(this.trainedDynamicsRun===this.runId||this.trainedDynamicsAsking)){this.trainedDynamicsAsking=!0;try{const e=await fetch(`/api/runs/${encodeURIComponent(this.runId)}/dynamics/trained`);if(!e.ok){console.warn("[StageState] The trained dynamics were refused",e.status);return}const t=await e.json();this.trainedDynamics=t,t.cell&&(this.trainedDynamicsRun=this.runId),this.notify("evidence")}catch(e){console.warn("[StageState] The trained dynamics could not be read",e)}finally{this.trainedDynamicsAsking=!1}}}scheduleTimeline(){this.timelineStale=!0,this.timelineTimer===null&&(this.timelineTimer=window.setTimeout(()=>{this.timelineTimer=null,this.syncTimeline()},300))}async syncMultirun(e=!1){const t=[this.axes.x,this.axes.y,this.axes.z].join("|");if(!(!e&&(t===this.multirunRequest||this.multirunAsking))){this.multirunAsking=!0;try{const n=await fetch("/api/spaces",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({axes:[this.axes.x,this.axes.y,this.axes.z]})});if(!n.ok){console.warn("[StageState] The runs' space was refused",n.status);return}this.multirun=await n.json(),this.multirunRequest=t,this.notify("evidence")}catch(n){console.warn("[StageState] The runs' space could not be read",n)}finally{this.multirunAsking=!1}}}}const nt=new Tb;function Ab(i,e=10){if(i.length<=e)return[i];const t=[];let n="";for(const s of i.split("_")){const r=n?`${n}_${s}`:s;r.length>e&&n?(t.push(n),n=s):n=r}return n&&t.push(n),t}function Ao(i,e,t,n){const s=Ab(i),r=document.createElement("canvas"),o=r.getContext("2d"),a=64,l=72;o.font=`bold ${a}px "JetBrains Mono", monospace`;const c=Math.max(...s.map(g=>o.measureText(g).width))+16;r.width=Math.max(64,Math.ceil(c)),r.height=s.length*l+16,o.font=`bold ${a}px "JetBrains Mono", monospace`,o.fillStyle="#ffffff",o.textAlign="center",o.textBaseline="middle",s.forEach((g,m)=>{o.fillText(g,r.width/2,l*m+l/2+8)});const u=new qy(r);u.needsUpdate=!0;const h=t.clone();h.map=u,h.transparent=!0;const d=new Gy(h),f=r.width/r.height;let v=e*s.length;return n!==void 0&&(v=Math.min(v,n/f)),d.scale.set(v*f,v,1),d}const Td=yb.axes,Cb={measured:"Measured — the run has evidence here",legal:"Legal — a gap nobody has measured",void:"Void — the system refuses this cell"};class Rb{constructor(){R(this,"name","DiscoveryMap");R(this,"scene",new Qf);R(this,"camera",new Sn);R(this,"renderer",null);R(this,"cells",new Map);R(this,"cellDataMap",new Map);R(this,"cellHeights",new Map);R(this,"xValues",[]);R(this,"yValues",[]);R(this,"zValues",[]);R(this,"cellSize",.8);R(this,"spacing",1.1);R(this,"raycaster",new Jy);R(this,"mouse",new qe);R(this,"selectedCell",null);R(this,"hoveredCell",null);R(this,"legendElement",null);R(this,"readoutElement",null);R(this,"pointerX",0);R(this,"pointerY",0);R(this,"axisLabelMeshes",[]);R(this,"voidMesh",null);R(this,"visible",!1);R(this,"onQueueUpdate",e=>{});R(this,"onCampaignMetrics",e=>{const t=e==null?void 0:e.data;if(!(t!=null&&t.run))return;const n=typeof(e==null?void 0:e.campaign_id)=="string"?e.campaign_id:null;n&&Vn.observe(n,t)});Yt.register("queue_update",this.onQueueUpdate),Yt.register("campaign_metrics",this.onCampaignMetrics)}async init(){const e=Md();e&&(this.scene=e.scene,this.camera=e.camera,this.renderer=e.renderer),this.setupInteraction(),this.createLegend(),this.createReadout(),nt.onChange(()=>this.updateLegend()),Vn.onChange(()=>this.updateRunPicker()),console.log("[DiscoveryMap] Initialized")}async destroy(){var e,t;Yt.unregister("queue_update",this.onQueueUpdate),Yt.unregister("campaign_metrics",this.onCampaignMetrics),this.clearGrid(),(e=this.legendElement)==null||e.remove(),(t=this.readoutElement)==null||t.remove()}show(){this.visible=!0,this.applyAxes()}hide(){this.visible=!1,this.clearGrid()}refreshView(e){if(this.visible){if(e==="space"){this.applyAxes();return}e==="evidence"&&this.applyAggregates()}}hasMeasured(){return this.cellDataMap.size>0&&this.cellHeights.size>0}updateLegend(){var u,h,d,f,v;const e=nt.space,t=!!e,s=nt.values.credit.length>0,r=(u=this.legendElement)==null?void 0:u.querySelector("#legend-empty-state"),o=(h=this.legendElement)==null?void 0:h.querySelector("#legend-view"),a=(d=this.legendElement)==null?void 0:d.querySelector("#legend-arms-block"),l=(f=this.legendElement)==null?void 0:f.querySelector("#legend-axes-block");r&&(r.style.display=t?"none":"flex"),o&&(o.style.display=t?"block":"none"),a&&(a.style.display=s?"block":"none"),l&&(l.style.display=t?"block":"none");const c=(v=this.legendElement)==null?void 0:v.querySelector("#legend-cell-count");if(c&&e){const g={measured:Array.from(nt.aggregates.keys()).filter(m=>nt.spaceCells.has(m)).length,legal:e.counts.legal,void:e.counts.void};c.textContent=`${g.measured+g.legal+g.void} cells`}this.refreshAxisOptions(),this.updateLegendArms(),this.updateLegendAxes()}setupInteraction(){var t;const e=(t=this.renderer)==null?void 0:t.domElement;e&&(this.raycaster.params.Line.threshold=this.cellSize*.2,e.addEventListener("mousemove",n=>{const s=e.getBoundingClientRect();this.mouse.x=(n.clientX-s.left)/s.width*2-1,this.mouse.y=-((n.clientY-s.top)/s.height)*2+1,this.pointerX=n.clientX,this.pointerY=n.clientY}),e.addEventListener("mouseleave",()=>{this.hideReadout()}),e.addEventListener("click",()=>{this.hoveredCell&&this.selectCell(this.hoveredCell)}))}createReadout(){const e=document.getElementById("ui-overlay");e&&(this.readoutElement=document.createElement("div"),this.readoutElement.id="cell-readout",this.readoutElement.style.cssText=`
      position: fixed;
      pointer-events: none;
      background: var(--bg-secondary);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 10px 12px;
      font-size: 11px;
      line-height: 1.5;
      z-index: 300;
      display: none;
      max-width: 360px;
      box-shadow: 0 8px 32px rgba(0,0,0,0.5);
      backdrop-filter: blur(8px);
    `,e.appendChild(this.readoutElement))}showReadout(e){const t=this.readoutElement;if(!t)return;t.innerHTML="";const n=document.createElement("div");n.style.cssText="display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 8px;",Object.entries(e.coordinate).filter(([,d])=>d).forEach(([d,f])=>{const v=d==="credit",g=v?us[f]||he.gradient:"var(--text-secondary)",m=document.createElement("span");m.style.cssText=`
          padding: 2px 8px;
          background: ${v?g+"22":"var(--bg-tertiary)"};
          border: 1px solid ${v?g+"88":"var(--border)"};
          border-radius: 10px;
          font-size: 10px;
          color: ${g};
          font-weight: ${v?"600":"400"};
        `,m.textContent=`${d}=${f}`,n.appendChild(m)}),t.appendChild(n);const s=document.createElement("div");s.style.cssText="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;";const r={measured:he.measured,legal:he.legal_unmeasured,void:he.void},o={measured:"●",legal:"○",void:"✕"},a=document.createElement("span");a.style.cssText=`font-size: 14px; color: ${r[e.status]};`,a.textContent=o[e.status],s.appendChild(a);const l=document.createElement("span");if(l.style.cssText=`font-weight: 600; color: ${r[e.status]}; font-size: 12px;`,l.textContent=Cb[e.status],s.appendChild(l),t.appendChild(s),e.status==="measured"&&e.metrics){const d=e.metrics,f=document.createElement("div");f.style.cssText="display: flex; gap: 16px; font-size: 11px; color: var(--text-secondary);";const v=d.val_acc??0,g=d.val_acc_std??0,m=d.n_seeds??0,p=d.walltime_s;f.innerHTML=`
        <span>acc <strong style="color: var(--text-primary);">${v.toFixed(3)}</strong> ± ${g.toFixed(3)}</span>
        <span>n=<strong style="color: var(--text-primary);">${m}</strong></span>
        <span>${p!==void 0?`${p.toFixed(1)}s`:""}</span>
        ${e.pareto?'<span style="color: var(--pareto);">● PARETO</span>':""}
      `,t.appendChild(f)}if(e.status==="legal"){const d=document.createElement("div");d.style.cssText="margin-top: 6px; padding: 6px 8px; background: var(--bg-tertiary); border-radius: 4px; font-size: 10px; color: var(--text-muted);";const f=e.requiredSeeds??0;d.textContent=`Click to queue ${f} seeds →`,t.appendChild(d)}if(e.voidReason){const d=document.createElement("div");d.style.cssText="margin-top: 6px; padding: 6px 8px; background: var(--void)11; border: 1px solid var(--void)44; border-radius: 4px; font-size: 10px; color: var(--void);",d.textContent=e.voidReason,t.appendChild(d)}t.style.display="block";const c=t.getBoundingClientRect(),u=Math.min(this.pointerX+16,window.innerWidth-c.width-8),h=Math.min(this.pointerY+16,window.innerHeight-c.height-8);t.style.left=`${Math.max(8,u)}px`,t.style.top=`${Math.max(8,h)}px`}hideReadout(){this.readoutElement&&(this.readoutElement.style.display="none")}createLegend(){this.legendElement=vs({id:"discovery-legend",title:"Discovery Map",glyph:"▦",key:qs.legend,body:this.legendBody(),dock:"bottom",defaultOpen:!0}),this.createRunPicker(),this.createAxisPicker(),this.updateLegendArms(),this.updateLegendAxes()}legendBody(){return`
      <div id="legend-title" style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
        <span style="font-weight: 600; color: var(--text-primary);">Discovery Map</span>
        <span id="legend-cell-count" style="font-size: 11px; color: var(--text-muted);"></span>
      </div>
      <div id="legend-empty-state" class="empty-state" style="display: none;">
        <div class="empty-state-icon">▦</div>
        <div class="empty-state-title">No run selected</div>
        <div class="empty-state-message">Pick a run from the dropdown below to see its declared space</div>
      </div>
      <div id="legend-view" style="display: none;"></div>
      <div id="legend-marks" style="display: flex; flex-direction: column; gap: 6px; margin-bottom: 12px;">
        <div class="legend-item">
          <div style="width: 14px; height: 14px; background: var(--measured); border-radius: 3px; box-shadow: 0 0 10px var(--measured);"></div>
          <span style="font-size: 11px;">Measured — glowing pillar</span>
        </div>
        <div class="legend-item">
          <div style="width: 14px; height: 14px; background: transparent; border: 2px solid var(--legal-unmeasured); border-radius: 3px;"></div>
          <span style="font-size: 11px;">Legal gap — click to queue</span>
        </div>
        <div class="legend-item">
          <svg width="14" height="14" viewBox="0 0 14 14"><line x1="2" y1="2" x2="12" y2="12" stroke="var(--void)" stroke-width="2"/><line x1="12" y1="2" x2="2" y2="12" stroke="var(--void)" stroke-width="2"/></svg>
          <span style="font-size: 11px;">Void — system refuses</span>
        </div>
      </div>
      <div id="legend-arms-block" style="margin-top: 10px; padding-top: 10px; border-top: 1px solid var(--border); display: none;">
        <div style="font-weight: 600; margin-bottom: 6px; font-size: 11px;">Credit Arms</div>
        <div id="legend-arms" style="display: flex; flex-wrap: wrap; gap: 5px;"></div>
      </div>
      <div id="legend-run-block" style="margin-top: 10px; padding-top: 10px; border-top: 1px solid var(--border);">
        <div style="font-weight: 600; margin-bottom: 6px; font-size: 11px;">Run</div>
        <select id="legend-run-picker"></select>
        <div id="legend-run" style="font-size: 11px; color: var(--text-secondary); margin-top: 6px; min-height: 16px;"></div>
      </div>
      <div id="legend-axes-block" style="margin-top: 10px; padding-top: 10px; border-top: 1px solid var(--border); display: none;">
        <div style="font-weight: 600; margin-bottom: 6px; font-size: 11px;">Axes (click to change)</div>
        <div id="legend-axis-picker" style="display: flex; flex-direction: column; gap: 5px;"></div>
        <div id="legend-axes" style="font-size: 10px; color: var(--text-muted); margin-top: 6px;"></div>
      </div>
    `}createRunPicker(){var t;const e=(t=this.legendElement)==null?void 0:t.querySelector("#legend-run-picker");e&&e.addEventListener("change",()=>{Vn.select(e.value||null)})}updateRunPicker(){var o,a,l;const e=(o=this.legendElement)==null?void 0:o.querySelector("#legend-run-picker"),t=(a=this.legendElement)==null?void 0:a.querySelector("#legend-run");if(!e)return;const n=Vn.runs;if(e.innerHTML="",n.forEach(([c,u])=>{var v,g;const h=document.createElement("option"),d=((v=u==null?void 0:u.run)==null?void 0:v.profile)??"run",f=((g=u==null?void 0:u.records)==null?void 0:g.length)??0;h.value=c,h.textContent=`${c.slice(0,8)} · ${d} · ${f}`,h.selected=c===Vn.selectedId,e.appendChild(h)}),n.length===0){e.disabled=!0,t&&(t.textContent="No run has reported yet.");return}e.disabled=!1;const s=Vn.selected;if(!t)return;if(!s){t.textContent="";return}const r=s.run??{};t.textContent=[`run ${(Vn.selectedId??"").slice(0,8)}`,r.mode,`${((l=s.records)==null?void 0:l.length)??0} records`].filter(Boolean).join(" · ")}createAxisPicker(){var n;const e=(n=this.legendElement)==null?void 0:n.querySelector("#legend-axis-picker");if(!e)return;["x","y","z"].forEach(s=>{const r=document.createElement("div");r.className="axis-row",r.dataset.dimension=s,r.style.cssText=`
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 3px;
        font-size: 11px;
        margin-bottom: 3px;
      `;const o=document.createElement("span");o.textContent=s.toUpperCase(),o.style.cssText="color: var(--text-secondary); width: 12px;",r.appendChild(o),e.appendChild(r)}),this.refreshAxisOptions()}refreshAxisOptions(){var t;const e=(t=this.legendElement)==null?void 0:t.querySelectorAll("#legend-axis-picker .axis-row");e&&e.forEach(n=>{const s=n.dataset.dimension,r=new Set(["x","y","z"].filter(a=>a!==s).map(a=>nt.axes[a]));n.innerHTML="";const o=document.createElement("span");o.textContent=s.toUpperCase(),o.style.cssText="color: var(--text-secondary); width: 12px;",n.appendChild(o),Oa.forEach(a=>{var u;const l=nt.axes[s]===a,c=document.createElement("button");c.className="axis-button",c.dataset.axis=a,c.textContent=((u=Td[a])==null?void 0:u.display_name)??a,c.disabled=r.has(a),c.style.cssText=`
          flex: 0 0 auto;
          padding: 1px 5px;
          background: ${l?"var(--bg-primary)":"var(--bg-tertiary)"};
          border: 1px solid ${l?"var(--border-bright)":"var(--border)"};
          border-radius: 4px;
          color: ${l?"var(--text-primary)":"var(--text-secondary)"};
          font-size: 10px;
          cursor: pointer;
          opacity: ${r.has(a)?.4:1};
        `,c.addEventListener("click",()=>{nt.setAxes({...nt.axes,[s]:a})}),n.appendChild(c)})})}updateLegendArms(){var n;const e=(n=this.legendElement)==null?void 0:n.querySelector("#legend-arms");if(!e)return;const t=nt.values.credit;if(t.length===0){e.innerHTML='<span style="color: var(--text-muted); font-size: 11px;">No arm measured yet.</span>';return}e.innerHTML=t.map(s=>{const r=us[s]||he.gradient;return`<span style="display: inline-flex; align-items: center; gap: 4px; padding: 2px 8px; background: ${r}22; border: 1px solid ${r}88; border-radius: 12px; color: ${r}; font-size: 11px;">${s}</span>`}).join("")}updateLegendAxes(){var l;const e=(l=this.legendElement)==null?void 0:l.querySelector("#legend-axes");if(!e)return;const t=nt.space;if(!t){e.textContent="Waiting for the run's declared space — the axes come from the ontology.";return}const n=(c,u)=>{var v;const h=t.available[c]??u.length,d=h>u.length?` (${u.length} of ${h})`:"";return`${((v=Td[c])==null?void 0:v.display_name)??c}${d}`},s=Object.entries(t.held).map(([c,u])=>`${c}=${u}`),r={measured:Array.from(nt.aggregates.keys()).filter(c=>nt.spaceCells.has(c)).length,legal:t.counts.legal,void:t.counts.void},o=t.cells.length,a=Object.entries(t.void_rules??{}).sort((c,u)=>u[1]-c[1]).slice(0,2).map(([c,u])=>`${c.replace(/_/g," ")} (${u})`);e.innerHTML=[`<div>X: ${n(nt.axes.x,t.values[nt.axes.x]??[])}</div>`,`<div>Y: ${n(nt.axes.y,t.values[nt.axes.y]??[])}</div>`,`<div>Z: ${n(nt.axes.z,t.values[nt.axes.z]??[])}</div>`,`<div style="margin-top: 6px;">held: ${s.join(" · ")||"—"}</div>`,`<div style="margin-top: 6px;">${r.measured} measured · ${r.legal} legal · ${r.void} void (of ${o})</div>`,a.length>0?`<div style="margin-top: 6px;">refused by: ${a.join(", ")}</div>`:""].join("")}applyAxes(){const e=nt.space,t=nt.axes;this.xValues=(e==null?void 0:e.values[t.x])??[],this.yValues=(e==null?void 0:e.values[t.y])??[],this.zValues=(e==null?void 0:e.values[t.z])??[],this.buildGrid(),this.updateLegend()}buildGrid(){if(this.clearGrid(),!this.visible)return;this.createAxisLabels();const e=[];this.yValues.forEach((t,n)=>{this.zValues.forEach((s,r)=>{this.xValues.forEach((o,a)=>{const l=Yo(o,t,s),c=nt.spaceCells.get(l),u=(c==null?void 0:c.status)??"legal",h={coordinate:this.coordinateFor(o,t,s),status:u,chance:nt.chance,requiredSeeds:nt.requiredSeeds,runId:nt.runId??void 0,voidReason:c==null?void 0:c.reason,inDeclaration:c==null?void 0:c.in_declaration};if(this.cellDataMap.set(l,h),u==="void"){e.push(...this.voidMarkerPositions(a,n,r));return}this.createCell(l,h,a,n,r)})})}),e.length>0&&this.createVoidMarkers(e),this.frameGrid()}coordinateFor(e,t,n){const s={credit:"",geometry:"",dynamics:"",substrate:"",plasticity:"",update:""};return s[nt.axes.x]=e,s[nt.axes.y]=t,s[nt.axes.z]=n,Oa.forEach(r=>{var a,l;if(s[r])return;const o=(l=(a=nt.space)==null?void 0:a.held)==null?void 0:l[r];o&&(s[r]=o)}),s}createAxisLabels(){this.axisLabelMeshes.forEach(u=>this.scene.remove(u)),this.axisLabelMeshes=[];const e=new Qc({color:9148584,sizeAttenuation:!0}),t=new Qc({color:13227232,sizeAttenuation:!0}),n=(this.xValues.length-1)*this.spacing,r=(this.zValues.length-1)*this.spacing/2+1.2,o=-.45;this.xValues.forEach((u,h)=>{const d=(h-(this.xValues.length-1)/2)*this.spacing,f=Ao(u,.3,e,this.spacing*.95);f.position.set(d,o,r),this.scene.add(f),this.axisLabelMeshes.push(f)});const a=Ao(nt.axes.x,.3,t);a.position.set(n/2+1.15,o,r),this.scene.add(a),this.axisLabelMeshes.push(a);const l=Ao(nt.axes.z,.3,t);l.position.set(0,o,r+1.1),this.scene.add(l),this.axisLabelMeshes.push(l);const c=Ao(nt.axes.y,.3,t);c.position.set(-(n/2)-1.5,1.3,0),this.scene.add(c),this.axisLabelMeshes.push(c)}createCell(e,t,n,s,r){const o=(n-(this.xValues.length-1)/2)*this.spacing,a=s*this.spacing,l=(r-(this.zValues.length-1)/2)*this.spacing,c=t.status==="measured"?this.createMeasuredCell(t):this.createLegalCell();c.position.set(o,a,l),c.userData={...c.userData,cellKey:e},this.scene.add(c),this.cells.set(e,c)}createMeasuredCell(e){const t=this.pillarHeight(e),n=us[e.coordinate.credit]||he.gradient,s=new Gi(this.cellSize,t,this.cellSize);s.translate(0,t/2,0);const r=new rc({color:new st(n),emissive:new st(n),emissiveIntensity:.5,transparent:!0,opacity:.9,metalness:.3,roughness:.4}),o=new Pn(s,r);o.castShadow=!0,o.receiveShadow=!0;const a=new Gi(this.cellSize*1.1,t*1.1,this.cellSize*1.1);a.translate(0,t/2,0);const l=new Ta({color:new st(n),transparent:!0,opacity:.15,depthWrite:!1}),c=new Pn(a,l);return o.add(c),o.userData.glow=c,o}createLegalCell(){const e=new Gi(this.cellSize,this.cellSize,this.cellSize),t=new Xy(e);t.translate(0,this.cellSize/2,0);const n=new Ca({color:he.legal_unmeasured,transparent:!0,opacity:.55}),s=new Fo(t,n),r=new Pn(new Gi(this.cellSize,this.cellSize,this.cellSize),new Ta);return r.position.y=this.cellSize/2,r.visible=!1,s.add(r),s}disposeMesh(e){e.traverse(t=>{const n=t.geometry;n&&n.dispose();const s=t.material;Array.isArray(s)?s.forEach(r=>r.dispose()):s&&s.dispose()})}voidMarkerPositions(e,t,n){const s=(e-(this.xValues.length-1)/2)*this.spacing,r=t*this.spacing,o=(n-(this.zValues.length-1)/2)*this.spacing,a=this.cellSize*.6,l=.1;return[s-a,r+l,o-a,s+a,r+l,o+a,s+a,r+l,o-a,s-a,r+l,o+a]}createVoidMarkers(e){const t=new Xn;t.setAttribute("position",new Mn(e,3));const n=new Ca({color:he.void,transparent:!0,opacity:.32});this.voidMesh=new Fo(t,n),this.scene.add(this.voidMesh)}frameGrid(){const e=Md();if(!(e!=null&&e.controls)||this.xValues.length===0||this.zValues.length===0)return;const t=(this.xValues.length-1)*this.spacing/2+this.cellSize,n=(this.zValues.length-1)*this.spacing/2+this.cellSize,s=(this.yValues.length-1)*this.spacing+this.cellSize,r=n+1.8,o=-.8;bb(e,new G(-t,o,-n),new G(t,s,r),new G(0,s/2,0))}clearGrid(){this.cells.forEach(e=>{this.scene.remove(e),this.disposeMesh(e)}),this.cells.clear(),this.cellDataMap.clear(),this.cellHeights.clear(),this.axisLabelMeshes.forEach(e=>{this.scene.remove(e),this.disposeMesh(e)}),this.axisLabelMeshes=[],this.voidMesh&&(this.scene.remove(this.voidMesh),this.voidMesh.geometry.dispose(),Array.isArray(this.voidMesh.material)?this.voidMesh.material.forEach(e=>e.dispose()):this.voidMesh.material.dispose(),this.voidMesh=null)}applyAggregates(){this.visible&&(nt.aggregates.forEach((e,t)=>{const n=this.cellDataMap.get(t);n&&(n.status="measured",n.coordinate={...e.coordinate},n.metrics={val_acc:Ra(e.acc),val_acc_std:Sb(e.acc),walltime_s:Ra(e.walltime),param_count:Ra(e.params),n_seeds:e.acc.length},n.curve=Mb(e.curves),n.pareto=e.pareto,n.chance=nt.chance,n.requiredSeeds=nt.requiredSeeds,n.runId=nt.runId??void 0,this.updateCellVisual(t,n,e.pareto))}),this.updateLegendAxes())}pillarHeight(e){var t;return Pg.lerp(.4,3.4,((t=e.metrics)==null?void 0:t.val_acc)??0)}updateCellVisual(e,t,n){const s=this.cells.get(e);if(!s)return;const r=s.position.clone(),o=s.userData.glow;o&&s.remove(o),this.scene.remove(s),this.disposeMesh(s);const a=this.createMeasuredCell(t);a.position.copy(r),a.userData.cellKey=e;const l=this.pillarHeight(t),c=this.cellHeights.get(e)??0;if(this.cellHeights.set(e,l),a.scale.y=l>0?Math.min(1,Math.max(c/l,.001)):1,n){const u=new Cu(this.cellSize*.6,this.cellSize*.8,32),h=new Ta({color:he.pareto,side:Ei,transparent:!0,opacity:.6}),d=new Pn(u,h);d.rotation.x=-Math.PI/2,d.position.y=.05,a.add(d),a.userData.paretoRing=d}this.scene.add(a),this.cells.set(e,a)}selectCell(e){this.selectedCell=e;const t=this.cellDataMap.get(e);t&&window.dispatchEvent(new CustomEvent("cell-selected",{detail:t}))}update(e){if(!this.visible){this.hideReadout();return}const t=1-Math.exp(-e*8);this.cells.forEach((o,a)=>{const l=this.cellDataMap.get(a);if((l==null?void 0:l.status)==="measured"&&o instanceof Pn&&o.material instanceof rc){o.scale.y<1&&(o.scale.y=Math.min(1,o.scale.y+(1-o.scale.y)*t));const c=o.userData.glow;c&&(c.material.opacity=.1+.1*Math.sin(Date.now()*.003));const u=o.userData.paretoRing;u&&(u.material.opacity=.4+.2*Math.sin(Date.now()*.005))}}),this.raycaster.setFromCamera(this.mouse,this.camera);const n=this.raycaster.intersectObjects(Array.from(this.cells.values()),!0);let s=null;n.length>0&&(s=this.pickCell(n)),s||(s=this.voidCellUnderCursor()),s!==this.hoveredCell&&(this.hoveredCell&&this.highlightCell(this.hoveredCell,!1),this.hoveredCell=s,s&&this.highlightCell(s,!0));const r=s?this.cellDataMap.get(s):void 0;r?this.showReadout(r):this.hideReadout()}pickCell(e){var n,s;let t=null;for(const r of e){const o=r.object.userData.cellKey||((n=r.object.parent)==null?void 0:n.userData.cellKey);if(o&&(t??(t=o),((s=this.cellDataMap.get(o))==null?void 0:s.status)==="measured"))return o}return t}voidCellUnderCursor(){if(!this.voidMesh)return null;const e=this.raycaster.params.Line.threshold;this.raycaster.params.Line.threshold=this.cellSize*.3;try{const t=this.raycaster.intersectObject(this.voidMesh,!1);return t.length===0?null:this.cellAt(t[0].point)}finally{this.raycaster.params.Line.threshold=e}}cellAt(e){const t=Math.round(e.x/this.spacing+(this.xValues.length-1)/2),n=Math.round(e.y/this.spacing),s=Math.round(e.z/this.spacing+(this.zValues.length-1)/2);return t<0||t>=this.xValues.length||n<0||n>=this.yValues.length||s<0||s>=this.zValues.length?null:Yo(this.xValues[t],this.yValues[n],this.zValues[s])}highlightCell(e,t){var r;const n=this.cells.get(e);if(!n)return;const s=(r=this.renderer)==null?void 0:r.domElement;if(s&&(s.style.cursor=t&&this.isCellActionable(e)?"pointer":"grab"),n instanceof Pn&&n.material instanceof rc){t?(n.userData.originalEmissive=n.material.emissiveIntensity,n.userData.originalScale=n.scale.y,n.material.emissiveIntensity=(n.userData.originalEmissive||.5)+.5,n.scale.y=Math.min(1.05,n.scale.y*1.08)):(n.userData.originalEmissive!==void 0&&(n.material.emissiveIntensity=n.userData.originalEmissive),n.userData.originalScale!==void 0&&(n.scale.y=n.userData.originalScale));return}n instanceof Fo&&n.material instanceof Ca&&(t?(n.userData.originalOpacity=n.material.opacity,n.material.opacity=.95,n.material.linewidth=2):n.userData.originalOpacity!==void 0&&(n.material.opacity=n.userData.originalOpacity,n.material.linewidth=1))}isCellActionable(e){const t=this.cellDataMap.get(e);return t?t.status==="legal"||t.status==="measured":!1}}const Pu=new Rb;qn.register(Pu);const Pb={space:{glyph:"▦",kind:"solid"},terrain:{glyph:"▲",kind:"solid"},frontier:{glyph:"◭",kind:"solid"},layers:{glyph:"▤",kind:"solid"},multirun:{glyph:"▣",kind:"solid"},matrix:{glyph:"▩",kind:"mark"},multiples:{glyph:"⊞",kind:"mark"},uncertainty:{glyph:"◌",kind:"mark"},ledger:{glyph:"☰",kind:"mark"},contrast:{glyph:"◐",kind:"mark"},basin:{glyph:"◡",kind:"mark"},"trained-basin":{glyph:"◠",kind:"mark"},cost:{glyph:"▮",kind:"bar"},flow:{glyph:"⇉",kind:"bar"},effect:{glyph:"▯",kind:"bar"},spread:{glyph:"▬",kind:"bar"},convergence:{glyph:"∿",kind:"curve"},timeline:{glyph:"↦",kind:"curve"},trajectory:{glyph:"⟿",kind:"curve"},spectrum:{glyph:"〜",kind:"curve"},landscape:{glyph:"∿",kind:"curve"},"trained-trajectory":{glyph:"⟿",kind:"curve"},"trained-spectrum":{glyph:"〜",kind:"curve"},"trained-landscape":{glyph:"∿",kind:"curve"},slices:{glyph:"⁙",kind:"mark"}};function Lb(i){return Pb[i]??{glyph:"•",kind:"mark"}}const nu=[];function _s(i){if(nu.some(e=>e.id===i.id))throw new Error(`View with id "${i.id}" already registered`);nu.push(i)}function Db(){return[...nu]}class Ib{constructor(e){R(this,"canvas");R(this,"context");R(this,"visible",!1);this.canvas=document.createElement("canvas"),this.canvas.id=e,this.canvas.style.cssText=`
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      z-index: 50;
      display: none;
      background: var(--bg);
      pointer-events: none;
    `,document.body.appendChild(this.canvas),this.context=this.canvas.getContext("2d"),this.resize(),window.addEventListener("resize",()=>{this.resize()})}show(){this.visible=!0,this.canvas.style.display="block",this.resize(),this.begin()}hide(){this.visible=!1,this.canvas.style.display="none"}resize(){const e=Math.min(window.devicePixelRatio||1,2);this.canvas.width=Math.floor(window.innerWidth*e),this.canvas.height=Math.floor(window.innerHeight*e),this.context.setTransform(e,0,0,e,0,0)}begin(){const e=this.context;return e.clearRect(0,0,window.innerWidth,window.innerHeight),e.fillStyle="#0a0e14",e.fillRect(0,0,window.innerWidth,window.innerHeight),e}area(){const e=document.getElementById("discovery-legend"),t=e?e.getBoundingClientRect().right:0,n=Math.max(40,t+24),s=Math.max(200,window.innerWidth*ip-n);return{x:n,y:70,width:s,height:Math.max(200,window.innerHeight*sp-70)}}}const yt=new Ib("stage-2d"),Pr={top:64,right:36,bottom:62,left:78};function Ub(i,e,t,n){i.fillStyle=he.text_primary,i.font="600 22px 'JetBrains Mono', monospace",i.textAlign="left",i.textBaseline="alphabetic",i.fillText(t,e.x,e.y+14),n&&(i.fillStyle=he.text_secondary,i.font="13px 'JetBrains Mono', monospace",i.fillText(n,e.x,e.y+40))}function jo(i,e,t=5){if(!Number.isFinite(i)||!Number.isFinite(e))return[i];if(i===e)return[i];const s=(e-i)/Math.max(1,t),r=10**Math.floor(Math.log10(s)),o=s/r,a=(o>=5?10:o>=2?5:o>=1?2:1)*r,l=Math.ceil(i/a)*a,c=[];for(let u=l;u<=e+a*1e-6;u+=a)c.push(Number(u.toFixed(10)));return c}function Ko(i){const e=Math.abs(i);return e===0?"0":e>=1e3||e>=10?i.toFixed(0):e>=1?i.toFixed(1):e>=.01?i.toFixed(2):i.toExponential(1)}function Gn(i,e){const t=e.xMax-e.xMin;return t===0?e.rect.x:e.rect.x+(i-e.xMin)/t*e.rect.width}function vn(i,e){const t=e.yMax-e.yMin;return t===0?e.rect.y+e.rect.height:e.rect.y+e.rect.height-(i-e.yMin)/t*e.rect.height}function xs(i,e,t){const n={x:e.x+Pr.left,y:e.y+Pr.top,width:Math.max(40,e.width-Pr.left-Pr.right),height:Math.max(40,e.height-Pr.top-Pr.bottom)},s={rect:n,xMin:t.xMin,xMax:t.xMax,yMin:t.yMin,yMax:t.yMax};Ub(i,e,t.title,t.subtitle);const r=t.xTicks??jo(t.xMin,t.xMax,6),o=t.yTicks??jo(t.yMin,t.yMax,5);return i.strokeStyle=he.border,i.lineWidth=1,i.beginPath(),i.rect(n.x,n.y,n.width,n.height),i.stroke(),i.font="12px 'JetBrains Mono', monospace",i.fillStyle=he.text_secondary,r.forEach(a=>{const l=Gn(a,s);l<n.x-1||l>n.x+n.width+1||(i.strokeStyle=he.border,i.beginPath(),i.moveTo(l,n.y),i.lineTo(l,n.y+n.height),i.stroke(),i.textAlign="center",i.fillText(Ko(a),l,n.y+n.height+20))}),o.forEach(a=>{const l=vn(a,s);l<n.y-1||l>n.y+n.height+1||(i.strokeStyle=he.border,i.beginPath(),i.moveTo(n.x,l),i.lineTo(n.x+n.width,l),i.stroke(),i.textAlign="right",i.fillText(Ko(a),n.x-10,l+4))}),i.fillStyle=he.text_secondary,i.font="13px 'JetBrains Mono', monospace",i.textAlign="center",i.fillText(t.xLabel,n.x+n.width/2,n.y+n.height+46),i.save(),i.translate(n.x-56,n.y+n.height/2),i.rotate(-Math.PI/2),i.textAlign="center",i.fillText(t.yLabel,0,0),i.restore(),s}function ys(i,e,t){i.fillStyle=he.text_secondary,i.font="12px 'JetBrains Mono', monospace",i.textAlign="left",i.textBaseline="alphabetic",i.fillText(t,e.x,e.y+e.height+40)}function Lu(i){const e=i.replace("#","");return[parseInt(e.slice(0,2),16),parseInt(e.slice(2,4),16),parseInt(e.slice(4,6),16)]}function Ad(i){return`#${i.map(e=>Math.round(Math.max(0,Math.min(255,e))).toString(16).padStart(2,"0")).join("")}`}function Cd(i,e,t){return[i[0]+(e[0]-i[0])*t,i[1]+(e[1]-i[1])*t,i[2]+(e[2]-i[2])*t]}const Nb=Lu(he.ramp_low),Rd=Lu(he.ramp_mid),Ob=Lu(he.ramp_high);function Jr(i){const e=Math.max(0,Math.min(1,i));return e<=.5?Ad(Cd(Nb,Rd,e*2)):Ad(Cd(Rd,Ob,(e-.5)*2))}function Fb(){const i=nt.dynamics;return!i||!i.stateful?null:i}function kb(i){var t;const e=((t=i.cell)==null?void 0:t.coordinate)??{};return[e.geometry,e.dynamics,e.credit].filter(n=>typeof n=="string"&&n.length>0).join(" · ")}function Bb(i){var n;const e=[],t=kb(i);return t&&e.push(t),((n=i.cell)==null?void 0:n.measured_by_run)===!1&&e.push("a cell of the space, not one the run measured"),i.trained===!1&&e.push("the weights are untrained"),e.join(" · ")}class zb{constructor(){R(this,"id","basin");R(this,"name","The basin");R(this,"group","the system");R(this,"caption","The states near the cell's own: how many come back, and how far the ones that do not stray.");R(this,"key","b");R(this,"visible",!1);R(this,"drawn",!1)}enter(){this.visible=!0,yt.show(),this.draw()}exit(){this.visible=!1,yt.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}draw(){const e=Fb(),t=e==null?void 0:e.basin;if(!e||!t||t.paths.length===0){this.drawn=!1;return}const n=yt.begin(),s=yt.area(),r=t.paths,o=Math.max(...r.flatMap(c=>c.distances),1e-6),a=xs(n,s,{xMin:0,xMax:r[0].distances.length,yMin:0,yMax:o*1.1,xLabel:"steps after the nudge",yLabel:"distance from the attractor",title:"The basin",subtitle:Bb(e)}),l=t.radii;r.forEach(c=>{const u=l.indexOf(c.radius),h=l.length>1?u/(l.length-1):.5;n.strokeStyle=c.returned?he.ok:Jr(h),n.lineWidth=2,n.beginPath(),c.distances.forEach((d,f)=>{const v=Gn(f,a),g=vn(d,a);f===0?n.moveTo(v,g):n.lineTo(v,g)}),n.stroke()}),n.font="12px 'JetBrains Mono', monospace",n.textAlign="center",n.textBaseline="top",t.stability.forEach((c,u)=>{const h=a.rect.x+a.rect.width/l.length*(u+.5);n.fillStyle=c>0?he.ok:he.warn,n.fillText(`${Math.round(c*100)}% back`,h,a.rect.y+12),n.fillStyle=he.text_secondary,n.fillText(`nudge ${l[u]}`,h,a.rect.y+28)}),ys(n,s,e.verdict??""),this.drawn=!0}}_s(new zb);function Hb(){const i=nt.dynamics;return!i||!i.stateful?null:i}function Vb(i){var t;const e=((t=i.cell)==null?void 0:t.coordinate)??{};return[e.geometry,e.dynamics,e.credit].filter(n=>typeof n=="string"&&n.length>0).join(" · ")}function Gb(i){var n;const e=[],t=Vb(i);return t&&e.push(t),((n=i.cell)==null?void 0:n.measured_by_run)===!1&&e.push("a cell of the space, not one the run measured"),i.trained===!1&&e.push("the weights are untrained"),e.join(" · ")}class Wb{constructor(){R(this,"id","landscape");R(this,"name","The landscape");R(this,"group","the system");R(this,"caption","The cell's own energy over the ground its trajectory crossed, and the path it took across it.");R(this,"key","n");R(this,"visible",!1);R(this,"drawn",!1)}enter(){this.visible=!0,yt.show(),this.draw()}exit(){this.visible=!1,yt.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}draw(){const e=Hb(),t=e==null?void 0:e.landscape,n=e==null?void 0:e.trajectory;if(!e||!t||t.grid.length===0){this.drawn=!1;return}const s=yt.begin(),r=yt.area(),o=t.grid,a=o.flat(),l=Math.min(...a),c=Math.max(...a),u=xs(s,r,{xMin:t.x[0],xMax:t.x[t.x.length-1],yMin:t.y[0],yMax:t.y[t.y.length-1],xLabel:"along the trajectory",yLabel:"across it",title:"The landscape",subtitle:Gb(e)}),h=u.rect.width/(t.x.length-1||1),d=u.rect.height/(t.y.length-1||1);s.save(),s.beginPath(),s.rect(u.rect.x,u.rect.y,u.rect.width,u.rect.height),s.clip(),o.forEach((x,b)=>{x.forEach((w,O)=>{const A=(w-l)/(c-l||1);s.fillStyle=Jr(1-A);const L=u.rect.x+h*b,k=u.rect.y+u.rect.height-d*(O+1);s.fillRect(L,k,h+1,d+1)})}),s.restore(),n&&n.path.length>1&&(s.strokeStyle=he.text_primary,s.lineWidth=2,s.beginPath(),n.path.forEach((x,b)=>{const w=Gn(x[0],u),O=vn(x[1],u);b===0?s.moveTo(w,O):s.lineTo(w,O)}),s.stroke());let f=0,v=0,g=Number.POSITIVE_INFINITY;o.forEach((x,b)=>x.forEach((w,O)=>{w<g&&(g=w,f=b,v=O)}));const m=Gn(t.x[f],u),p=vn(t.y[v],u);s.strokeStyle=he.ok,s.lineWidth=2,s.beginPath(),s.arc(m,p,7,0,Math.PI*2),s.stroke(),s.font="12px 'JetBrains Mono', monospace",s.fillStyle=he.ok,s.textAlign="left",s.textBaseline="bottom",s.fillText("the lowest ground",m+11,p-6),ys(s,r,e.verdict??""),this.drawn=!0}}_s(new Wb);new G(.72,.24,.65);new G(.34,.4,.85);function qb(){const i=nt.dynamics;return!i||!i.stateful?null:i}function Xb(i){var t;const e=((t=i.cell)==null?void 0:t.coordinate)??{};return[e.geometry,e.dynamics,e.credit].filter(n=>typeof n=="string"&&n.length>0).join(" · ")}function $b(i){var n;const e=[],t=Xb(i);return t&&e.push(t),((n=i.cell)==null?void 0:n.measured_by_run)===!1&&e.push("a cell of the space, not one the run measured"),i.trained===!1&&e.push("the weights are untrained"),e.join(" · ")}class Yb{constructor(){R(this,"id","spectrum");R(this,"name","The spectrum");R(this,"group","the system");R(this,"caption","How fast a nudge grows along each direction: the exponents that say whether this dynamics settles.");R(this,"key","m");R(this,"visible",!1);R(this,"drawn",!1)}enter(){this.visible=!0,yt.show(),this.draw()}exit(){this.visible=!1,yt.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}draw(){const e=qb(),t=e==null?void 0:e.spectrum;if(!e||!t||t.length===0){this.drawn=!1;return}const n=yt.begin(),s=yt.area(),o=Math.max(...t.map(u=>Math.abs(u)),1e-6)*1.25,a=xs(n,s,{xMin:0,xMax:t.length,yMin:-o,yMax:o,xLabel:"direction",yLabel:"growth per step",title:"The spectrum",subtitle:$b(e),xTicks:jo(0,t.length,6).filter(u=>Number.isInteger(u))}),l=vn(0,a);n.strokeStyle=he.text_muted,n.lineWidth=1.5,n.beginPath(),n.moveTo(a.rect.x,l),n.lineTo(a.rect.x+a.rect.width,l),n.stroke();const c=a.rect.width/t.length;t.forEach((u,h)=>{const d=a.rect.x+c*(h+.5),f=Math.min(46,c*.5),v=vn(u,a),g=u>0;n.fillStyle=g?he.warn:he.ok,n.fillRect(d-f/2,Math.min(v,l),f,Math.abs(v-l)),n.font="11px 'JetBrains Mono', monospace",n.fillStyle=g?he.warn:he.ok,n.textAlign="center",n.textBaseline=g?"bottom":"top",n.fillText(Ko(u),d,g?v-5:v+5)}),ys(n,s,e.verdict??""),this.drawn=!0}}_s(new Yb);new G(.34,.4,.85);function jb(){const i=nt.trainedDynamics;return!i||!i.stateful?null:i}function Kb(i){var t;const e=((t=i.cell)==null?void 0:t.coordinate)??{};return[e.geometry,e.dynamics,e.credit].filter(n=>typeof n=="string"&&n.length>0).join(" · ")}function Zb(i){var n;const e=[],t=Kb(i);return t&&e.push(t),((n=i.cell)==null?void 0:n.measured_by_run)===!1&&e.push("a cell of the space, not one the run measured"),i.trained===!0&&e.push("the weights were trained first"),e.join(" · ")}class Jb{constructor(){R(this,"id","trained-basin");R(this,"name","The trained basin");R(this,"group","the system");R(this,"caption","The states near the trained cell's own: how many come back, and how far the ones that do not stray.");R(this,"key","k");R(this,"visible",!1);R(this,"drawn",!1)}enter(){this.visible=!0,yt.show(),this.draw()}exit(){this.visible=!1,yt.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}draw(){const e=jb(),t=e==null?void 0:e.basin;if(!e||!t||t.paths.length===0){this.drawn=!1;return}const n=yt.begin(),s=yt.area(),r=t.paths,o=Math.max(...r.flatMap(c=>c.distances),1e-6),a=xs(n,s,{xMin:0,xMax:r[0].distances.length,yMin:0,yMax:o*1.1,xLabel:"steps after the nudge",yLabel:"distance from the attractor",title:"The trained basin",subtitle:Zb(e)}),l=t.radii;r.forEach(c=>{const u=l.indexOf(c.radius),h=l.length>1?u/(l.length-1):.5;n.strokeStyle=c.returned?he.ok:Jr(h),n.lineWidth=2,n.beginPath(),c.distances.forEach((d,f)=>{const v=Gn(f,a),g=vn(d,a);f===0?n.moveTo(v,g):n.lineTo(v,g)}),n.stroke()}),n.font="12px 'JetBrains Mono', monospace",n.textAlign="center",n.textBaseline="top",t.stability.forEach((c,u)=>{const h=a.rect.x+a.rect.width/l.length*(u+.5);n.fillStyle=c>0?he.ok:he.warn,n.fillText(`${Math.round(c*100)}% back`,h,a.rect.y+12),n.fillStyle=he.text_secondary,n.fillText(`nudge ${l[u]}`,h,a.rect.y+28)}),ys(n,s,e.verdict??""),this.drawn=!0}}_s(new Jb);function Qb(){const i=nt.trainedDynamics;return!i||!i.stateful?null:i}function eS(i){var t;const e=((t=i.cell)==null?void 0:t.coordinate)??{};return[e.geometry,e.dynamics,e.credit].filter(n=>typeof n=="string"&&n.length>0).join(" · ")}function tS(i){var n;const e=[],t=eS(i);return t&&e.push(t),((n=i.cell)==null?void 0:n.measured_by_run)===!1&&e.push("a cell of the space, not one the run measured"),i.trained===!0&&e.push("the weights were trained first"),e.join(" · ")}class nS{constructor(){R(this,"id","trained-landscape");R(this,"name","The trained landscape");R(this,"group","the system");R(this,"caption","The trained cell's own energy over the ground its trajectory crossed, and the path it took across it.");R(this,"key","o");R(this,"visible",!1);R(this,"drawn",!1)}enter(){this.visible=!0,yt.show(),this.draw()}exit(){this.visible=!1,yt.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}draw(){const e=Qb(),t=e==null?void 0:e.landscape,n=e==null?void 0:e.trajectory;if(!e||!t||t.grid.length===0){this.drawn=!1;return}const s=yt.begin(),r=yt.area(),o=t.grid,a=o.flat(),l=Math.min(...a),c=Math.max(...a),u=xs(s,r,{xMin:t.x[0],xMax:t.x[t.x.length-1],yMin:t.y[0],yMax:t.y[t.y.length-1],xLabel:"along the trajectory",yLabel:"across it",title:"The trained landscape",subtitle:tS(e)}),h=u.rect.width/(t.x.length-1||1),d=u.rect.height/(t.y.length-1||1);s.save(),s.beginPath(),s.rect(u.rect.x,u.rect.y,u.rect.width,u.rect.height),s.clip(),o.forEach((x,b)=>{x.forEach((w,O)=>{const A=(w-l)/(c-l||1);s.fillStyle=Jr(1-A);const L=u.rect.x+h*b,k=u.rect.y+u.rect.height-d*(O+1);s.fillRect(L,k,h+1,d+1)})}),s.restore(),n&&n.path.length>1&&(s.strokeStyle=he.text_primary,s.lineWidth=2,s.beginPath(),n.path.forEach((x,b)=>{const w=Gn(x[0],u),O=vn(x[1],u);b===0?s.moveTo(w,O):s.lineTo(w,O)}),s.stroke());let f=0,v=0,g=Number.POSITIVE_INFINITY;o.forEach((x,b)=>x.forEach((w,O)=>{w<g&&(g=w,f=b,v=O)}));const m=Gn(t.x[f],u),p=vn(t.y[v],u);s.strokeStyle=he.ok,s.lineWidth=2,s.beginPath(),s.arc(m,p,7,0,Math.PI*2),s.stroke(),s.font="12px 'JetBrains Mono', monospace",s.fillStyle=he.ok,s.textAlign="left",s.textBaseline="bottom",s.fillText("the lowest ground",m+11,p-6),ys(s,r,e.verdict??""),this.drawn=!0}}_s(new nS);function iS(){const i=nt.trainedDynamics;return!i||!i.stateful?null:i}function sS(i){var t;const e=((t=i.cell)==null?void 0:t.coordinate)??{};return[e.geometry,e.dynamics,e.credit].filter(n=>typeof n=="string"&&n.length>0).join(" · ")}function rS(i){var n;const e=[],t=sS(i);return t&&e.push(t),((n=i.cell)==null?void 0:n.measured_by_run)===!1&&e.push("a cell of the space, not one the run measured"),i.trained===!0&&e.push("the weights were trained first"),e.join(" · ")}class aS{constructor(){R(this,"id","trained-spectrum");R(this,"name","The trained spectrum");R(this,"group","the system");R(this,"caption","How fast a nudge grows along each direction after training: the exponents that say whether this dynamics settles.");R(this,"key","i");R(this,"visible",!1);R(this,"drawn",!1)}enter(){this.visible=!0,yt.show(),this.draw()}exit(){this.visible=!1,yt.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}draw(){const e=iS(),t=e==null?void 0:e.spectrum;if(!e||!t||t.length===0){this.drawn=!1;return}const n=yt.begin(),s=yt.area(),o=Math.max(...t.map(u=>Math.abs(u)),1e-6)*1.25,a=xs(n,s,{xMin:0,xMax:t.length,yMin:-o,yMax:o,xLabel:"direction",yLabel:"growth per step",title:"The trained spectrum",subtitle:rS(e),xTicks:jo(0,t.length,6).filter(u=>Number.isInteger(u))}),l=vn(0,a);n.strokeStyle=he.text_muted,n.lineWidth=1.5,n.beginPath(),n.moveTo(a.rect.x,l),n.lineTo(a.rect.x+a.rect.width,l),n.stroke();const c=a.rect.width/t.length;t.forEach((u,h)=>{const d=a.rect.x+c*(h+.5),f=Math.min(46,c*.5),v=vn(u,a),g=u>0;n.fillStyle=g?he.warn:he.ok,n.fillRect(d-f/2,Math.min(v,l),f,Math.abs(v-l)),n.font="11px 'JetBrains Mono', monospace",n.fillStyle=g?he.warn:he.ok,n.textAlign="center",n.textBaseline=g?"bottom":"top",n.fillText(Ko(u),d,g?v-5:v+5)}),ys(n,s,e.verdict??""),this.drawn=!0}}_s(new aS);function oS(){const i=nt.trainedDynamics;return!i||!i.stateful?null:i}function lS(i){var t;const e=((t=i.cell)==null?void 0:t.coordinate)??{};return[e.geometry,e.dynamics,e.credit].filter(n=>typeof n=="string"&&n.length>0).join(" · ")}function cS(i){var n;const e=[],t=lS(i);return t&&e.push(t),((n=i.cell)==null?void 0:n.measured_by_run)===!1&&e.push("a cell of the space, not one the run measured"),i.trained===!0&&e.push("the weights were trained first"),e.join(" · ")}class uS{constructor(){R(this,"id","trained-trajectory");R(this,"name","The trained trajectory");R(this,"group","the system");R(this,"caption","Where the trained cell's state went, step by step: the path it took through the space it moves in.");R(this,"key","g");R(this,"visible",!1);R(this,"drawn",!1)}enter(){this.visible=!0,yt.show(),this.draw()}exit(){this.visible=!1,yt.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}draw(){const e=oS(),t=e==null?void 0:e.trajectory;if(!e||!t||t.path.length<2){this.drawn=!1;return}const n=yt.begin(),s=yt.area(),r=t.path,o=r.map(x=>x[0]),a=r.map(x=>x[1]),l=.08,c=Math.min(...o),u=Math.max(...o),h=Math.min(...a),d=Math.max(...a),f=u-c||1,v=d-h||1,g=xs(n,s,{xMin:c-f*l,xMax:u+f*l,yMin:h-v*l,yMax:d+v*l,xLabel:t.axes[0]??"the direction the state moved",yLabel:t.axes[1]??"the direction across it",title:"The trained trajectory",subtitle:cS(e)});for(let x=1;x<r.length;x+=1){const b=x/(r.length-1);n.strokeStyle=Jr(b),n.lineWidth=2.5,n.beginPath(),n.moveTo(Gn(r[x-1][0],g),vn(r[x-1][1],g)),n.lineTo(Gn(r[x][0],g),vn(r[x][1],g)),n.stroke()}const m=(x,b,w)=>{const O=Gn(x[0],g),A=vn(x[1],g);n.fillStyle=b,n.beginPath(),n.arc(O,A,5,0,Math.PI*2),n.fill(),n.font="12px 'JetBrains Mono', monospace",n.textAlign="left",n.textBaseline="middle",n.fillText(w,O+10,A)};m(r[0],he.text_primary,"where it started"),m(r[r.length-1],he.warn,"where it stopped");const p=t.error??[];if(p.length>1){const x=Math.min(...p),b=Math.max(...p),w=g.rect.height*.16,O=g.rect.y+g.rect.height-w*.5,A=L=>O-(L-x)/(b-x||1)*w*.5;n.strokeStyle=he.thermodynamic_contrast,n.lineWidth=1.5,n.beginPath(),p.forEach((L,k)=>{const E=g.rect.x+k/(p.length-1)*g.rect.width;k===0?n.moveTo(E,A(L)):n.lineTo(E,A(L))}),n.stroke(),n.font="11px 'JetBrains Mono', monospace",n.fillStyle=he.thermodynamic_contrast,n.textAlign="right",n.textBaseline="bottom",n.fillText("the prediction error",g.rect.x+g.rect.width,O-w*.6)}ys(n,s,e.verdict??""),this.drawn=!0}}_s(new uS);function hS(){const i=nt.dynamics;return!i||!i.stateful?null:i}function dS(i){var t;const e=((t=i.cell)==null?void 0:t.coordinate)??{};return[e.geometry,e.dynamics,e.credit].filter(n=>typeof n=="string"&&n.length>0).join(" · ")}function fS(i){var n;const e=[],t=dS(i);return t&&e.push(t),((n=i.cell)==null?void 0:n.measured_by_run)===!1&&e.push("a cell of the space, not one the run measured"),i.trained===!1&&e.push("the weights are untrained"),e.join(" · ")}class pS{constructor(){R(this,"id","trajectory");R(this,"name","The trajectory");R(this,"group","the system");R(this,"caption","Where the cell's own state went, step by step: the path it took through the space it moves in.");R(this,"key","j");R(this,"visible",!1);R(this,"drawn",!1)}enter(){this.visible=!0,yt.show(),this.draw()}exit(){this.visible=!1,yt.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}draw(){const e=hS(),t=e==null?void 0:e.trajectory;if(!e||!t||t.path.length<2){this.drawn=!1;return}const n=yt.begin(),s=yt.area(),r=t.path,o=r.map(x=>x[0]),a=r.map(x=>x[1]),l=.08,c=Math.min(...o),u=Math.max(...o),h=Math.min(...a),d=Math.max(...a),f=u-c||1,v=d-h||1,g=xs(n,s,{xMin:c-f*l,xMax:u+f*l,yMin:h-v*l,yMax:d+v*l,xLabel:t.axes[0]??"the direction the state moved",yLabel:t.axes[1]??"the direction across it",title:"The trajectory",subtitle:fS(e)});for(let x=1;x<r.length;x+=1){const b=x/(r.length-1);n.strokeStyle=Jr(b),n.lineWidth=2.5,n.beginPath(),n.moveTo(Gn(r[x-1][0],g),vn(r[x-1][1],g)),n.lineTo(Gn(r[x][0],g),vn(r[x][1],g)),n.stroke()}const m=(x,b,w)=>{const O=Gn(x[0],g),A=vn(x[1],g);n.fillStyle=b,n.beginPath(),n.arc(O,A,5,0,Math.PI*2),n.fill(),n.font="12px 'JetBrains Mono', monospace",n.textAlign="left",n.textBaseline="middle",n.fillText(w,O+10,A)};m(r[0],he.text_primary,"where it started"),m(r[r.length-1],he.warn,"where it stopped");const p=t.error??[];if(p.length>1){const x=Math.min(...p),b=Math.max(...p),w=g.rect.height*.16,O=g.rect.y+g.rect.height-w*.5,A=L=>O-(L-x)/(b-x||1)*w*.5;n.strokeStyle=he.thermodynamic_contrast,n.lineWidth=1.5,n.beginPath(),p.forEach((L,k)=>{const E=g.rect.x+k/(p.length-1)*g.rect.width;k===0?n.moveTo(E,A(L)):n.lineTo(E,A(L))}),n.stroke(),n.font="11px 'JetBrains Mono', monospace",n.fillStyle=he.thermodynamic_contrast,n.textAlign="right",n.textBaseline="bottom",n.fillText("the prediction error",g.rect.x+g.rect.width,O-w*.6)}ys(n,s,e.verdict??""),this.drawn=!0}}_s(new pS);class mS{constructor(){R(this,"name","ViewSwitcher");R(this,"views",[]);R(this,"active",null);R(this,"track",null);R(this,"viewButtons",new Map);R(this,"captionElement",null);R(this,"section",null);R(this,"keys",new Map);R(this,"keyOf",new Map);R(this,"onKeyDown",e=>{if(e.metaKey||e.ctrlKey||e.altKey)return;const t=e.target;if(t&&["INPUT","SELECT","TEXTAREA"].includes(t.tagName))return;const n=e.key.toLowerCase();if(n===vb){this.cycle();return}const s=this.keys.get(n);s&&this.show(s.id)});this.views=Db()}async init(){window.addEventListener("keydown",this.onKeyDown),nt.onChange(e=>{var t;return(t=this.active)==null?void 0:t.refresh(e)}),this.buildKeys(),this.buildSection(),this.attachSection(),this.show(this.views[0].id),console.log("[ViewSwitcher] Initialized")}async destroy(){var e,t;window.removeEventListener("keydown",this.onKeyDown),(e=this.active)==null||e.exit(),this.active=null,(t=this.section)==null||t.remove(),this.section=null}getViews(){return this.views}get activeId(){var e;return((e=this.active)==null?void 0:e.id)??null}isReady(e){const t=this.views.find(n=>n.id===e);return t?t.ready():!1}show(e){var n;const t=this.views.find(s=>s.id===e);!t||t===this.active||((n=this.active)==null||n.exit(),this.active=t,t.enter(),this.updateSelector(),this.updateLegend())}cycle(){if(this.views.length===0)return;const e=this.views.findIndex(n=>n===this.active),t=this.views[(e+1)%this.views.length];this.show(t.id)}buildKeys(){this.keys.clear(),this.keyOf.clear(),this.views.forEach((e,t)=>{const n=t<9?String(t+1):"";n&&(this.keys.set(n,e),this.keyOf.set(e.id,n)),e.key&&!tu.has(e.key)&&(this.keys.set(e.key,e),this.keyOf.set(e.id,e.key))})}optionLabel(e){const t=this.keyOf.get(e.id);return t?`${t.toUpperCase()} · ${e.name}`:e.name}keyHint(){const e=[],t=[],n=[];this.views.forEach((r,o)=>{if(o<9){e.push(String(o+1));return}if(!(!r.key||tu.has(r.key))){if(/^[a-z]$/.test(r.key)){t.push(r.key.toUpperCase());return}n.push(r.key)}});const s=["V cycles"];return e.length>0&&s.push(`${e[0]}–${e[e.length-1]} pick`),t.length>0&&s.push(`${t.join(" ")} pick`),n.length>0&&s.push(`${n.join(" ")} pick`),s.join(" · ")}buildSection(){const e=document.createElement("div");e.id="legend-view-section",e.style.cssText="margin-bottom: 12px;";const t=document.createElement("div");t.textContent="View",t.style.cssText="font-weight: 600; margin-bottom: 8px;",e.appendChild(t);const n=document.createElement("div");n.id="view-strip",n.style.cssText=`
      display: flex;
      align-items: center;
      gap: 4px;
      width: 100%;
    `,n.appendChild(this.stepButton("‹","the previous view",-1));const s=document.createElement("div");s.id="view-track",s.style.cssText=`
      display: flex;
      align-items: center;
      gap: 3px;
      flex: 1;
      overflow-x: auto;
      overflow-y: hidden;
      scrollbar-width: thin;
      padding-bottom: 2px;
    `;const r=[{group:"the space",label:"The space",views:[]},{group:"the run",label:"The run",views:[]},{group:"the evidence",label:"The evidence",views:[]},{group:"the process",label:"The process",views:[]},{group:"the judgement",label:"The judgement",views:[]},{group:"the system",label:"The system",views:[]}];for(const l of this.views){const c=r.find(u=>u.group===l.group);c&&c.views.push(l)}r.forEach((l,c)=>{if(l.views.length===0)return;if(c>0){const h=document.createElement("div");h.style.cssText=`
          width: 1px;
          height: 16px;
          background: var(--border);
          margin: 0 4px;
        `,s.appendChild(h)}const u=document.createElement("span");u.textContent=l.label,u.style.cssText=`
        font-size: 9px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--text-muted);
        margin-right: 4px;
        flex-shrink: 0;
      `,s.appendChild(u);for(const h of l.views)s.appendChild(this.viewButton(h))}),n.appendChild(s),n.appendChild(this.stepButton("›","the next view",1)),e.appendChild(n),this.track=s;const o=document.createElement("div");o.id="view-caption",o.style.cssText="font-size: 11px; color: var(--text-secondary); margin-top: 8px;",e.appendChild(o),this.captionElement=o;const a=document.createElement("div");a.textContent=this.keyHint(),a.style.cssText="font-size: 10px; color: var(--text-muted); margin-top: 6px;",e.appendChild(a),this.section=e}viewButton(e){const t=Lb(e.id),n=this.keyOf.get(e.id),s=document.createElement("button");s.className="view-button",s.dataset.view=e.id,s.textContent=t.glyph,s.title=n?`${n.toUpperCase()} · ${e.name}`:e.name,s.style.cssText=`
      flex: 0 0 auto;
      width: 22px;
      height: 22px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: var(--bg-tertiary);
      border: 1px solid var(--border);
      border-radius: 4px;
      color: var(--text-secondary);
      font-size: 12px;
      cursor: pointer;
      padding: 0;
      transition: all var(--motion-fast) var(--ease-out);
    `;const r={solid:"var(--promoted)",mark:"var(--gradient)",bar:"var(--cpu)",curve:"var(--warn)"};return s.style.borderColor=r[t.kind]+"44",s.addEventListener("mouseenter",()=>{s.classList.contains("active")||(s.style.background="var(--bg-primary)",s.style.borderColor=r[t.kind]+"88",s.style.color="var(--text-primary)")}),s.addEventListener("mouseleave",()=>{s.classList.contains("active")||(s.style.background="var(--bg-tertiary)",s.style.borderColor=r[t.kind]+"44",s.style.color="var(--text-secondary)")}),s.addEventListener("click",()=>this.show(e.id)),this.viewButtons.set(e.id,s),s}stepButton(e,t,n){const s=document.createElement("button");return s.className="view-step",s.textContent=e,s.title=t,s.style.cssText=`
      flex: 0 0 auto;
      width: 20px;
      height: 22px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: var(--bg-tertiary);
      border: 1px solid var(--border);
      border-radius: 4px;
      color: var(--text-secondary);
      font-size: 13px;
      cursor: pointer;
      padding: 0;
    `,s.addEventListener("click",()=>this.step(n)),s}step(e){if(this.views.length===0)return;const t=this.views.findIndex(r=>{var o;return r.id===((o=this.active)==null?void 0:o.id)}),s=((t<0?0:t)+e+this.views.length)%this.views.length;this.show(this.views[s].id)}attachSection(e=0){const t=document.getElementById("legend-view");if(!t){e<50&&window.setTimeout(()=>this.attachSection(e+1),100);return}this.section&&this.section.parentElement!==t&&t.appendChild(this.section),this.updateSelector(),this.updateLegend()}updateSelector(){if(this.active){for(const[e,t]of this.viewButtons){const n=e===this.active.id;t.classList.toggle("active",n),n&&(t.style.color="var(--text-primary)",t.style.borderColor="var(--border-bright)",t.style.background="var(--bg-primary)")}this.scrollToActive()}}scrollToActive(){const e=this.active?this.viewButtons.get(this.active.id):null;!e||!this.track||e.scrollIntoView({block:"nearest",inline:"nearest"})}updateLegend(){if(!this.active)return;const e=document.getElementById("legend-title");e&&(e.textContent=this.active.name);const t=document.getElementById("legend-marks");t&&(t.style.display=this.active.id==="space"?"":"none"),this.captionElement&&(this.captionElement.textContent=this.active.caption)}}const Xs=new mS;qn.register(Xs);const gS={watch:{id:"watch",viewId:"space",placements:[{id:"control-bar",dock:"bottom",order:0,isOpen:!0},{id:"live-rail",dock:"right",order:0,isOpen:!0},{id:"caption",dock:"bottom",order:1,isOpen:!0},{id:"legend",dock:"bottom",order:2,isOpen:!0},{id:"hud",dock:"top",order:0,isOpen:!1},{id:"plotter-pareto",dock:"right",order:1,isOpen:!0},{id:"plotter-ablation",dock:"right",order:2,isOpen:!1},{id:"plotter-variability",dock:"right",order:3,isOpen:!1},{id:"cell-drawer",dock:"floating",order:0,isOpen:!1},{id:"control-panel",dock:"floating",order:1,isOpen:!1},{id:"help-overlay",dock:"floating",order:2,isOpen:!1}]},audit:{id:"audit",viewId:"ledger",placements:[{id:"control-bar",dock:"bottom",order:0,isOpen:!0},{id:"live-rail",dock:"right",order:0,isOpen:!0},{id:"caption",dock:"bottom",order:1,isOpen:!0},{id:"legend",dock:"bottom",order:2,isOpen:!0},{id:"hud",dock:"top",order:0,isOpen:!1},{id:"plotter-pareto",dock:"right",order:1,isOpen:!0},{id:"plotter-ablation",dock:"right",order:2,isOpen:!0},{id:"plotter-variability",dock:"right",order:3,isOpen:!0},{id:"cell-drawer",dock:"floating",order:0,isOpen:!1},{id:"control-panel",dock:"floating",order:1,isOpen:!1},{id:"help-overlay",dock:"floating",order:2,isOpen:!1}]},drive:{id:"drive",viewId:"flow",placements:[{id:"control-bar",dock:"bottom",order:0,isOpen:!0},{id:"live-rail",dock:"right",order:0,isOpen:!0},{id:"caption",dock:"bottom",order:1,isOpen:!0},{id:"legend",dock:"bottom",order:2,isOpen:!0},{id:"hud",dock:"top",order:0,isOpen:!1},{id:"plotter-pareto",dock:"right",order:1,isOpen:!1},{id:"plotter-ablation",dock:"right",order:2,isOpen:!1},{id:"plotter-variability",dock:"right",order:3,isOpen:!1},{id:"cell-drawer",dock:"floating",order:0,isOpen:!1},{id:"control-panel",dock:"floating",order:1,isOpen:!0},{id:"help-overlay",dock:"floating",order:2,isOpen:!1}]},free:{id:"free",viewId:"space",placements:[]}},lc="computronium.layout.v1";class vS{constructor(){R(this,"dockElements",new Map);R(this,"panelPlacements",new Map);R(this,"currentWorkspace","watch");R(this,"isManualOverride",!1);R(this,"listeners",new Set);R(this,"initialized",!1)}async init(){if(this.initialized)return;const e=document.getElementById("ui-overlay");if(!e)throw new Error("ui-overlay not found — layout must init after DOM ready");for(const t of["top","bottom","left","right","floating"]){const n=document.createElement("div");n.id=`dock-${t}`,n.className=`dock dock-${t}`,n.dataset.dock=t,n.style.cssText=this.dockStyles(t),e.appendChild(n),this.dockElements.set(t,n)}this.restoreOrDefault(),this.initialized=!0,console.log("[LayoutManager] Initialized")}dockStyles(e){const t=`
      position: fixed;
      pointer-events: none;
      z-index: 140;
      display: flex;
      flex-direction: column;
      gap: 4px;
    `;switch(e){case"top":return`${t}
          top: 0;
          left: 0;
          right: 0;
          padding: 4px;
          align-items: center;
          justify-content: flex-start;
        `;case"bottom":return`${t}
          bottom: 0;
          left: 0;
          right: 0;
          padding: 4px;
          align-items: center;
          justify-content: flex-end;
        `;case"left":return`${t}
          top: 0;
          bottom: 0;
          left: 0;
          padding: 4px;
          width: 320px;
          align-items: flex-start;
          justify-content: flex-start;
          overflow-y: auto;
        `;case"right":return`${t}
          top: 0;
          bottom: 0;
          right: 0;
          padding: 4px;
          width: 520px;
          align-items: flex-end;
          justify-content: flex-start;
          overflow-y: auto;
        `;case"floating":return`${t}
          inset: 0;
          align-items: flex-start;
          justify-content: flex-start;
          overflow: auto;
        `}}registerPanel(e,t){const n=Rt.get(e);if(!n)return;const s=this.panelPlacements.get(e),r={id:e,dock:t.dock,order:(s==null?void 0:s.order)??0,isOpen:(s==null?void 0:s.isOpen)??t.defaultOpen??!1};this.panelPlacements.set(e,r),this.movePanelToDock(e,t.dock),r.isOpen&&n.toggle(),this.notify()}movePanelToDock(e,t){const n=document.getElementById(e),s=this.dockElements.get(t);if(!n||!s)return;n.style.pointerEvents="auto",n.parentElement&&n.parentElement.removeChild(n);const o=this.getPlacementsInDock(t).findIndex(c=>c.order>this.panelPlacements.get(e).order),a=Array.from(s.children),l=o>=0&&o<a.length?a[o]:null;s.insertBefore(n,l)}getPlacementsInDock(e){return Array.from(this.panelPlacements.values()).filter(t=>t.dock===e).sort((t,n)=>t.order-n.order)}setPanelOpen(e,t){const n=this.panelPlacements.get(e);n&&n.isOpen!==t&&(n.isOpen=t,this.isManualOverride=!0,this.currentWorkspace!=="free"&&(this.currentWorkspace="free"),this.persist(),this.notify())}setPanelOrder(e,t){const n=this.panelPlacements.get(e);n&&(n.order=t,this.isManualOverride=!0,this.currentWorkspace!=="free"&&(this.currentWorkspace="free"),this.movePanelToDock(e,n.dock),this.persist(),this.notify())}setPanelDock(e,t){const n=this.panelPlacements.get(e);n&&n.dock!==t&&(n.dock=t,n.order=this.getPlacementsInDock(t).length,this.isManualOverride=!0,this.currentWorkspace!=="free"&&(this.currentWorkspace="free"),this.movePanelToDock(e,t),this.persist(),this.notify())}applyWorkspace(e){const t=gS[e];if(t){this.currentWorkspace=e,this.isManualOverride=!1,Xs.show(t.viewId);for(const n of t.placements){const s=Rt.get(n.id);if(!s)continue;this.panelPlacements.get(n.id);const r={id:n.id,dock:n.dock,order:n.order,isOpen:n.isOpen};this.panelPlacements.set(n.id,r),this.movePanelToDock(n.id,n.dock),s.isOpen()!==n.isOpen&&s.toggle()}for(const[n,s]of Rt.list().map(r=>[r.id,r]))t.placements.some(r=>r.id===n)||s.isOpen()&&!["cell-drawer","help-overlay"].includes(n)&&s.toggle();this.persist(),this.notify()}}reset(){this.applyWorkspace("watch"),this.clearPersisted()}getCurrentWorkspace(){return this.currentWorkspace}isFree(){return this.currentWorkspace==="free"||this.isManualOverride}getPlacements(){return Array.from(this.panelPlacements.values())}getPlacement(e){return this.panelPlacements.get(e)}onChange(e){return this.listeners.add(e),()=>this.listeners.delete(e)}notify(){for(const e of this.listeners)e()}persist(){try{const e={id:this.currentWorkspace,viewId:Xs.activeId??"space",placements:this.getPlacements(),updatedAt:Date.now()};localStorage.setItem(lc,JSON.stringify(e))}catch{}}restoreOrDefault(){try{const e=localStorage.getItem(lc);if(e){const t=JSON.parse(e);if(t.placements&&Array.isArray(t.placements)){this.applyWorkspace(t.id);return}}}catch{}this.applyWorkspace("watch")}clearPersisted(){try{localStorage.removeItem(lc)}catch{}}buildWorkspaceSwitcher(){const e=document.createElement("div");e.className="workspace-switcher",e.style.cssText=`
      display: flex;
      gap: 2px;
      background: var(--bg-tertiary);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 2px;
    `;const t=[{id:"watch",label:"▦",title:"Watch — campaigns in real time"},{id:"audit",label:"▣",title:"Audit — evidence and judgement"},{id:"drive",label:"▸",title:"Drive — the instrument"}];for(const s of t){const r=document.createElement("button");r.textContent=s.label,r.title=s.title,r.dataset.workspace=s.id,r.style.cssText=`
        flex: 1;
        min-width: 0;
        padding: 4px 8px;
        background: transparent;
        border: none;
        border-radius: 4px;
        color: var(--text-secondary);
        font-size: 12px;
        cursor: pointer;
        transition: all var(--motion-fast) var(--ease-out);
        white-space: nowrap;
      `,this.currentWorkspace===s.id&&(r.style.background="var(--bg-primary)",r.style.color="var(--text-primary)",r.style.border="1px solid var(--border-bright)"),r.addEventListener("click",()=>{this.applyWorkspace(s.id),this.refreshSwitcher(e)}),e.appendChild(r)}const n=document.createElement("button");return n.textContent="↺",n.title="Reset to Watch workspace",n.style.cssText=`
      width: 24px;
      height: 24px;
      background: transparent;
      border: none;
      border-radius: 4px;
      color: var(--text-muted);
      font-size: 12px;
      cursor: pointer;
      transition: all var(--motion-fast) var(--ease-out);
    `,n.addEventListener("click",()=>this.reset()),n.addEventListener("mouseenter",()=>n.style.color="var(--text-primary)"),n.addEventListener("mouseleave",()=>n.style.color="var(--text-muted)"),e.appendChild(n),e}refreshSwitcher(e){for(const t of e.querySelectorAll("button[data-workspace]")){const n=t.dataset.workspace,s=this.currentWorkspace===n;t.style.background=s?"var(--bg-primary)":"transparent",t.style.color=s?"var(--text-primary)":"var(--text-secondary)",t.style.border=s?"1px solid var(--border-bright)":"none"}}}const qr=new vS;function zs(){return qr}class _S{constructor(){R(this,"panels",new Map);R(this,"listeners",new Set)}register(e){this.panels.set(e.id,e),this.notify()}get(e){return this.panels.get(e)}list(){return[...this.panels.values()]}toggle(e){const t=this.panels.get(e);t&&(t.toggle(),qr.setPanelOpen(e,t.isOpen()),this.notify())}isOpen(e){const t=this.panels.get(e);return t?t.isOpen():!1}openIds(){return this.list().filter(e=>e.isOpen()).map(e=>e.id)}byKey(e){return this.list().find(t=>t.key===e)}onChange(e){return this.listeners.add(e),()=>{this.listeners.delete(e)}}notify(){for(const e of this.listeners)e()}}const Rt=new _S,iu="panel-hidden";function su(i,e){i&&i.classList.toggle(iu,e)}function rp(i){const e=document.createElement("button");return e.className="panel-close",e.setAttribute("aria-label","close"),e.textContent="×",e.style.cssText=`
    background: none;
    border: none;
    color: var(--text-secondary);
    font-size: 16px;
    line-height: 1;
    cursor: pointer;
    padding: 2px 4px;
    flex: 0 0 auto;
    pointer-events: auto;
  `,e.addEventListener("click",t=>{t.stopPropagation(),i()}),e}class xS{constructor(){R(this,"name","PanelRail");R(this,"container",null);R(this,"buttons",new Map);R(this,"unsubscribe",null)}async init(){const e=document.getElementById("ui-overlay");e&&(this.container=document.createElement("div"),this.container.id="panel-rail",this.container.style.cssText=`
      position: fixed;
      top: 50%;
      right: 0;
      transform: translateY(-50%);
      display: flex;
      flex-direction: column;
      gap: 4px;
      padding: 6px 4px;
      background: var(--bg-secondary);
      border: 1px solid var(--border);
      border-right: none;
      border-radius: 8px 0 0 8px;
      z-index: 170;
      box-shadow: -4px 0 16px rgba(0, 0, 0, 0.4);
    `,e.appendChild(this.container),this.build(),this.unsubscribe=Rt.onChange(()=>this.refresh()))}async destroy(){var e,t;(e=this.unsubscribe)==null||e.call(this),this.unsubscribe=null,(t=this.container)==null||t.remove(),this.container=null,this.buttons.clear()}build(){if(this.container){this.container.innerHTML="",this.buttons.clear();for(const e of Rt.list()){const t=document.createElement("button");t.className="panel-rail-button",t.textContent=e.glyph,t.title=e.key?`${e.label} (${e.key.toUpperCase()})`:e.label,t.style.cssText=`
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--bg-tertiary);
        border: 1px solid var(--border);
        border-radius: 4px;
        color: var(--text-secondary);
        font-size: 12px;
        cursor: pointer;
        padding: 0;
      `,t.addEventListener("click",()=>Rt.toggle(e.id)),this.container.appendChild(t),this.buttons.set(e.id,t)}this.light()}}refresh(){if(!this.container)return;const e=Rt.list().map(s=>s.id),t=[...this.buttons.keys()];if(e.length!==t.length||e.some((s,r)=>s!==t[r])){this.build();return}this.light()}light(){for(const e of Rt.list()){const t=this.buttons.get(e.id);if(!t)continue;const n=e.isOpen();t.style.color=n?"var(--text-primary)":"var(--text-muted)",t.style.borderColor=n?"var(--border-bright)":"var(--border)",t.style.background=n?"var(--bg-primary)":"var(--bg-tertiary)"}}}const yS=new xS;qn.register(yS);function ap(i,e,t,n,s,r){Rt.register({id:i,label:e,glyph:t,key:r,toggle:n,isOpen:s})}function js(i,e,t,n,s){ap(i,e,t,()=>{const r=n();r&&su(r,!r.classList.contains(iu))},()=>{const r=n();return r?!r.classList.contains(iu):!1},s)}const bS=500,Pd=60;function SS(){return`
    <style>
      .control-bar .verb {
        width: 36px;
        height: 32px;
        font-size: 16px;
        background: var(--bg-tertiary);
        border: 1px solid var(--border);
        border-radius: 6px;
        color: var(--text-primary);
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all var(--motion-fast) var(--ease-out);
      }
      .control-bar .verb:not(:disabled):hover {
        background: var(--border);
        border-color: var(--border-bright);
        transform: translateY(-1px);
      }
      .control-bar .verb:not(:disabled):active {
        transform: translateY(0) scale(0.95);
      }
      .control-bar .verb:disabled {
        opacity: 0.4;
        cursor: not-allowed;
      }
      .control-bar .verb-primary:not(:disabled) {
        background: var(--gradient)22;
        border-color: var(--gradient)66;
        color: var(--gradient);
      }
      .control-bar .verb-primary:not(:disabled):hover {
        background: var(--gradient)33;
        border-color: var(--gradient);
      }
      .control-bar .verb-danger:not(:disabled) {
        background: var(--error)22;
        border-color: var(--error)66;
        color: var(--error);
      }
      .control-bar .verb-danger:not(:disabled):hover {
        background: var(--error)33;
        border-color: var(--error);
      }
      .control-bar .separator {
        width: 1px;
        height: 24px;
        background: var(--border);
      }
      .control-bar .meter-group {
        display: flex;
        flex-direction: column;
        gap: 3px;
        min-width: 150px;
      }
      .control-bar .meter-label-row {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
      }
      .control-bar .meter-label {
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--text-secondary);
      }
      .control-bar .meter-value {
        color: var(--text-primary);
        font-weight: 600;
        font-variant-numeric: tabular-nums;
      }
      .control-bar .meter-bar {
        height: 6px;
        background: var(--bg);
        border-radius: 3px;
        overflow: hidden;
      }
      .control-bar .meter-fill {
        height: 100%;
        width: 0%;
        border-radius: 3px;
        transition: width var(--motion-normal) var(--ease-out), background-color var(--motion-fast);
      }
      .control-bar .ceiling-slider {
        width: 150px;
        accent-color: var(--gradient);
      }
      .control-bar .trace-canvas {
        border: 1px solid var(--border);
        border-radius: 6px;
        background: var(--bg);
      }
      .control-bar .status-text {
        min-width: 120px;
        color: var(--text-secondary);
        font-variant-numeric: tabular-nums;
      }
      .control-bar .door-btn {
        width: 30px;
        height: 30px;
        font-size: 15px;
        background: var(--bg-tertiary);
        border: 1px solid var(--border);
        border-radius: 6px;
        color: var(--text-primary);
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all var(--motion-fast) var(--ease-out);
      }
      .control-bar .door-btn:hover {
        background: var(--border);
        border-color: var(--border-bright);
      }
      .control-bar .workspace-switcher {
        margin-left: 8px;
      }
    </style>
    <button class="verb verb-primary" data-action="play" title="Play — release the run">▶</button>
    <button class="verb" data-action="step" title="Step — release exactly one more batch" disabled>⏭</button>
    <button class="verb verb-danger" data-action="stop" title="Stop — end the run at its next boundary">⏹</button>
    <div class="separator"></div>
    <div class="meter-group">
      <div class="meter-label-row">
        <span class="meter-label">CEILING</span>
        <span class="meter-value ceiling-value">—</span>
      </div>
      <input class="ceiling-slider" type="range" min="1" max="8" value="4" />
    </div>
    <div class="meter-group">
      <div class="meter-label-row">
        <span class="meter-label">CELLS</span>
        <span class="meter-value level-text">—</span>
      </div>
      <div class="meter-bar"><div class="meter-fill level-fill" style="background: var(--promoted);"></div></div>
      <div class="meter-label-row">
        <span class="meter-label">CPU</span>
        <span class="meter-value cpu-text">—</span>
      </div>
      <div class="meter-bar"><div class="meter-fill cpu-fill" style="background: var(--cpu);"></div></div>
    </div>
    <canvas class="trace-canvas" width="130" height="42"></canvas>
    <div class="separator"></div>
    <span class="status-text">no run is reporting</span>
    <div class="workspace-switcher"></div>
    <button class="door-btn" data-action="panel" title="Open control panel">⚙</button>
  `}class MS{constructor(){R(this,"name","ControlBar");R(this,"container",null);R(this,"playButton",null);R(this,"stepButton",null);R(this,"stopButton",null);R(this,"slider",null);R(this,"ceilingValue",null);R(this,"levelFill",null);R(this,"levelText",null);R(this,"cpuFill",null);R(this,"cpuText",null);R(this,"trace",null);R(this,"statusText",null);R(this,"timer",null);R(this,"payload",null);R(this,"samples",[]);R(this,"layoutUnsubscribe",null);R(this,"workspaceSwitcherContainer",null)}async init(){this.container=vs({id:"control-bar",title:"Control Bar",glyph:"⏯",body:SS(),dock:"bottom",defaultOpen:!0,className:"control-bar-panel"}),this.bindElements(),this.bindEvents(),js("control-bar","control bar","⏯",()=>this.container),this.layoutUnsubscribe=zs().onChange(()=>this.refreshWorkspaceSwitcher()),this.timer=window.setInterval(()=>{this.poll()},bS),this.poll()}async destroy(){var e,t;this.timer!==null&&window.clearInterval(this.timer),this.timer=null,(e=this.layoutUnsubscribe)==null||e.call(this),this.layoutUnsubscribe=null,(t=this.container)==null||t.remove()}refreshWorkspaceSwitcher(){if(!this.workspaceSwitcherContainer)return;const e=this.workspaceSwitcherContainer.querySelector(".workspace-switcher");e&&zs().refreshSwitcher(e)}bindElements(){if(!this.container)return;const e=this.container.querySelectorAll(".verb");if(this.playButton=e[0],this.stepButton=e[1],this.stopButton=e[2],this.slider=this.container.querySelector(".ceiling-slider"),this.ceilingValue=this.container.querySelector(".ceiling-value"),this.levelFill=this.container.querySelector(".level-fill"),this.levelText=this.container.querySelector(".level-text"),this.cpuFill=this.container.querySelector(".cpu-fill"),this.cpuText=this.container.querySelector(".cpu-text"),this.trace=this.container.querySelector("canvas.trace-canvas"),this.statusText=this.container.querySelector(".status-text"),this.workspaceSwitcherContainer=this.container.querySelector(".workspace-switcher"),this.workspaceSwitcherContainer){const t=zs().buildWorkspaceSwitcher();this.workspaceSwitcherContainer.appendChild(t)}}bindEvents(){var e,t,n,s,r;this.container&&((e=this.playButton)==null||e.addEventListener("click",()=>this.togglePlay()),(t=this.stepButton)==null||t.addEventListener("click",()=>this.step()),(n=this.stopButton)==null||n.addEventListener("click",()=>this.stop()),(s=this.slider)==null||s.addEventListener("input",o=>{const a=o.target,l=Number(a.value);this.ceilingValue&&(this.ceilingValue.textContent=String(l))}),(r=this.slider)==null||r.addEventListener("change",()=>{var a;const o=Number(((a=this.slider)==null?void 0:a.value)??1);this.command({max_workers:o})}),this.container.querySelector(".door-btn").addEventListener("click",()=>Rt.toggle("control-panel")))}togglePlay(){var e;this.command({paused:!((e=this.payload)!=null&&e.control.paused)})}step(){this.command({step:!0})}stop(){window.confirm("Stop the run? The run ends at its next boundary.")&&this.command({cancel:!0})}async poll(){var e,t;try{const n=await fetch("/api/control");if(!n.ok)return;const s=await n.json();for(this.payload=s,this.samples.push({level:((e=s.status)==null?void 0:e.in_flight)??0,cpu:((t=s.machine)==null?void 0:t.cpu_percent)??0});this.samples.length>Pd;)this.samples.shift();this.render()}catch{}}async command(e){var n;const t=(n=this.payload)==null?void 0:n.control.revision;try{const s=await fetch("/api/control",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({...e,revision:t})});if(!s.ok){const r=await s.json().catch(()=>({}));this.setStatus(r.error??"the control plane refused the command");return}await this.poll()}catch{this.setStatus("the dashboard could not reach the server")}}render(){var l,c;const e=this.payload;if(!e)return;const t=e.control,n=e.status,s=(n==null?void 0:n.in_flight)??0,r=t.max_workers??(n==null?void 0:n.ceiling)??0,o=((l=e.machine)==null?void 0:l.cpu_percent)??0;if(this.playButton){const u=t.paused;this.playButton.textContent=u?"▶":"⏸",this.playButton.classList.toggle("verb-primary",u),this.playButton.classList.toggle("verb-danger",!u),this.playButton.title=u?"Play — release the run":"Pause — hold the run at its next boundary",this.playButton.setAttribute("aria-label",u?"play":"pause")}if(this.stepButton){const u=t.paused&&e.readable;this.stepButton.disabled=!u,this.stepButton.title=u?"Step — release exactly one more batch":t.paused?"Step — control plane not readable":"Step — the run is not paused"}this.stopButton&&(this.stopButton.disabled=!e.readable,this.stopButton.title="Stop — end the run at its next boundary");const a=e.readable?"":e.error??"the control plane could not be read";if(this.playButton&&(this.playButton.disabled=!e.readable),this.playButton&&a&&(this.playButton.title=a),this.slider){const u=Math.max(1,((c=e.machine)==null?void 0:c.cpu_count)??1,r||1);this.slider.max=String(u),this.slider.value=String(Math.max(1,r||1)),this.slider.disabled=!e.readable,this.slider.title=a||`The ceiling on cells in flight — ${r||"the run's own"}`}if(this.ceilingValue&&(this.ceilingValue.textContent=r?String(r):"—"),this.levelFill){const u=r?Math.min(1,s/r):0;this.levelFill.style.width=`${u*100}%`,u===0?this.levelFill.style.background="var(--promoted)":u<.5?this.levelFill.style.background="var(--promoted)":u<.85?this.levelFill.style.background="var(--warn)":this.levelFill.style.background="var(--error)"}if(this.levelText&&(this.levelText.textContent=`${s}${r?` / ${r}`:""}`),this.cpuFill){const u=Math.min(100,Math.max(0,o));this.cpuFill.style.width=`${u}%`,u<30?this.cpuFill.style.background="var(--cpu)":u<70?this.cpuFill.style.background="var(--warn)":this.cpuFill.style.background="var(--error)"}if(this.cpuText&&(this.cpuText.textContent=`${o.toFixed(0)}%`),this.drawTrace(),this.statusText&&!a){const u=n!=null&&n.stage?n.stage.replace("s","S"):"";this.statusText.textContent=n?`${u} · ${n.cells_done} cells`:"no run is reporting"}}drawTrace(){var c,u,h;const e=this.trace;if(!e)return;const t=e.getContext("2d");if(!t)return;const n=e.width,s=e.height;t.clearRect(0,0,n,s);const r=Math.max(1,((c=this.payload)==null?void 0:c.control.max_workers)??((h=(u=this.payload)==null?void 0:u.status)==null?void 0:h.ceiling)??1),o=n/Math.max(1,Pd-1),a=n-(this.samples.length-1)*o;t.strokeStyle="var(--border)",t.lineWidth=.5,[.25,.5,.75].forEach(d=>{const f=s*d;t.beginPath(),t.moveTo(0,f),t.lineTo(n,f),t.stroke()}),t.beginPath(),t.strokeStyle="var(--cpu)",t.globalAlpha=.7,t.lineWidth=1,this.samples.forEach((d,f)=>{const v=a+f*o,g=s-Math.min(100,d.cpu)/100*s;f===0?t.moveTo(v,g):t.lineTo(v,g)}),t.stroke(),t.globalAlpha=1;const l=t.createLinearGradient(0,s,0,0);if(l.addColorStop(0,"var(--promoted)"),l.addColorStop(.5,"var(--warn)"),l.addColorStop(1,"var(--error)"),t.strokeStyle=l,t.lineWidth=1.5,t.lineCap="round",t.lineJoin="round",this.samples.forEach((d,f)=>{const v=a+f*o,g=s-Math.min(1,d.level/r)*s;f===0?t.moveTo(v,g):t.lineTo(v,g)}),t.stroke(),this.samples.length>0){const d=this.samples[this.samples.length-1],f=n-2,v=s-Math.min(100,d.cpu)/100*s;t.fillStyle="var(--cpu)",t.beginPath(),t.arc(f,v,2.5,0,Math.PI*2),t.fill();const g=s-Math.min(1,d.level/r)*s,m=d.level/r;t.fillStyle=m<.5?"var(--promoted)":m<.85?"var(--warn)":"var(--error)",t.beginPath(),t.arc(f-6,g,2.5,0,Math.PI*2),t.fill()}}setStatus(e){this.statusText&&(this.statusText.textContent=e)}}const Pa=new MS;qn.register(Pa);const cc=["substrate","geometry","dynamics","plasticity","credit","update"];function wS(){return`
    <style>
      #control-panel h4 {
        margin: 14px 0 6px;
        font-size: 11px;
        letter-spacing: 0.08em;
        color: var(--text-primary);
      }
      #control-panel table.kv, #control-panel table.list {
        width: 100%;
        border-collapse: collapse;
        font-size: 11px;
      }
      #control-panel table.kv th, #control-panel table.list th {
        text-align: left;
        font-weight: 500;
        color: var(--text-secondary);
        padding: 2px 6px 2px 0;
        vertical-align: top;
      }
      #control-panel table.kv td, #control-panel table.list td {
        color: var(--text-primary);
        padding: 2px 6px 2px 0;
        vertical-align: top;
      }
      #control-panel .note {
        color: var(--text-secondary);
        margin: 4px 0 8px;
        line-height: 1.4;
      }
      #control-panel .row {
        display: flex;
        gap: 8px;
        align-items: center;
        margin: 4px 0;
      }
      #control-panel input, #control-panel select {
        background: var(--bg-tertiary);
        color: var(--text-primary);
        border: 1px solid var(--border);
        border-radius: 4px;
        font-size: 11px;
        padding: 2px 4px;
        min-width: 0;
      }
      #control-panel button.mini {
        background: var(--bg-tertiary);
        border: 1px solid var(--border);
        border-radius: 4px;
        color: var(--text-primary);
        font-size: 11px;
        padding: 2px 8px;
        cursor: pointer;
      }
      #control-panel button.action {
        background: var(--bg-tertiary);
        border: 1px solid var(--border);
        border-radius: 4px;
        color: var(--text-primary);
        font-size: 11px;
        padding: 4px 10px;
        cursor: pointer;
        transition: all 0.1s ease;
      }
      #control-panel button.action:hover:not(:disabled) {
        background: var(--border);
        border-color: var(--border-bright);
      }
      #control-panel button.action:disabled {
        opacity: 0.4;
        cursor: not-allowed;
      }
      #control-panel .cell-row {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        align-items: center;
      }
      #control-panel .cell-row label {
        display: flex;
        flex-direction: column;
        gap: 2px;
        font-size: 10px;
        color: var(--text-secondary);
        white-space: nowrap;
      }
      #control-panel .cell-row select {
        font-size: 10px;
        padding: 2px 6px;
      }
    </style>
    <div id="control-panel-header" style="display: flex; align-items: center; gap: 8px;">
      <span style="font-weight: 600; color: var(--text-primary); letter-spacing: 0.08em;">CONTROL</span>
      <div style="flex: 1;"></div>
    </div>

    <h4>NEW RUN</h4>
    <div class="row">
      <select class="profile"></select>
      <select class="device">
        <option value="auto">auto</option>
        <option value="cpu">cpu</option>
        <option value="cuda">cuda</option>
      </select>
    </div>
    <div class="note profile-note"></div>
    <div class="row">
      <label>seeds</label><input class="seeds" type="number" min="1" />
      <label>epochs</label><input class="epochs" type="number" min="1" />
      <label>budget</label><input class="budget" type="number" min="1" />
      <select class="fidelity">
        <option value="L0">L0</option>
        <option value="L1">L1</option>
        <option value="L2">L2</option>
      </select>
    </div>
    <div class="row">
      <button class="action start">Start run</button>
    </div>
    <div class="note new-run-note"></div>

    <h4>THIS RUN</h4>
    <div class="run-section"></div>

    <h4>THE QUEUE</h4>
    <div class="queue-section"></div>

    <h4>CELLS</h4>
    <div class="row cell-row"></div>
    <div class="row">
      <button class="action replicate">Replicate</button>
      <button class="action preregister">Preregister</button>
      <button class="action quest">Quest</button>
    </div>
    <div class="note cell-note"></div>

    <h4>EXPORTS</h4>
    <div class="row">
      <button class="action export-script">Narration script</button>
      <button class="action export-report">Run report</button>
      <button class="action export-records">Records as JSON</button>
    </div>
    <div class="note export-note"></div>
  `}class ES{constructor(){R(this,"name","ControlPanel");R(this,"container",null);R(this,"profiles",[]);R(this,"axes",[]);R(this,"newRunSection",null);R(this,"runSection",null);R(this,"queueSection",null);R(this,"cellSection",null);R(this,"exportSection",null);R(this,"profileSelect",null);R(this,"seedsInput",null);R(this,"epochsInput",null);R(this,"budgetInput",null);R(this,"deviceSelect",null);R(this,"fidelitySelect",null);R(this,"profileNote",null);R(this,"newRunNote",null);R(this,"cellSelects",new Map);R(this,"cellNote",null);R(this,"exportNote",null)}showSection(e){var n;if(!this.container)return;const t=this.container.querySelectorAll("h4");for(const s of t)if((n=s.textContent)!=null&&n.toLowerCase().includes(e.toLowerCase().replace("-"," "))){s.scrollIntoView({behavior:"smooth",block:"start"}),s.style.transition="background 0.3s ease",s.style.background="var(--gradient)22",setTimeout(()=>s.style.background="",800);break}}async init(){this.container=vs({id:"control-panel",title:"Control Panel",glyph:"⚙",key:wd.panel,body:wS(),dock:"floating",defaultOpen:!1}),this.bindElements(),this.bindEvents(),js("control-panel","control panel","⚙",()=>this.container,wd.panel),await this.loadCatalogue(),this.refresh()}async destroy(){var e;(e=this.container)==null||e.remove()}bindElements(){if(!this.container)return;this.newRunSection=this.container.querySelector(".new-run-note"),this.runSection=this.container.querySelector(".run-section"),this.queueSection=this.container.querySelector(".queue-section"),this.cellSection=this.container.querySelector(".cell-section"),this.exportSection=this.container.querySelector(".export-note"),this.profileSelect=this.container.querySelector(".profile"),this.profileNote=this.container.querySelector(".profile-note"),this.newRunNote=this.container.querySelector(".new-run-note"),this.cellNote=this.container.querySelector(".cell-note"),this.exportNote=this.container.querySelector(".export-note"),this.seedsInput=this.container.querySelector(".seeds"),this.epochsInput=this.container.querySelector(".epochs"),this.budgetInput=this.container.querySelector(".budget"),this.deviceSelect=this.container.querySelector(".device"),this.fidelitySelect=this.container.querySelector(".fidelity");const e=this.container.querySelector(".cell-row");for(const t of cc){const n=document.createElement("label");n.textContent=t;const s=document.createElement("select");s.className=`cell-${t}`,n.appendChild(s),e.appendChild(n),this.cellSelects.set(t,s)}this.container.querySelector("#control-panel-header").appendChild(rp(()=>Rt.toggle("control-panel")))}bindEvents(){var e;this.container&&((e=this.profileSelect)==null||e.addEventListener("change",()=>this.renderProfileNote()),this.container.querySelector(".start").addEventListener("click",()=>void this.startRun()),this.container.querySelector(".replicate").addEventListener("click",()=>void this.cellAction("replicate")),this.container.querySelector(".preregister").addEventListener("click",()=>void this.cellAction("preregister")),this.container.querySelector(".quest").addEventListener("click",()=>void this.cellAction("quest")),this.container.querySelector(".export-script").addEventListener("click",()=>void this.export("script")),this.container.querySelector(".export-report").addEventListener("click",()=>void this.export("report")),this.container.querySelector(".export-records").addEventListener("click",()=>void this.export("records")))}async loadCatalogue(){try{const[e,t]=await Promise.all([fetch("/api/profiles").then(n=>n.json()),fetch("/api/axes").then(n=>n.json())]);this.profiles=e.profiles??[],this.axes=t.axes??[]}catch{this.profiles=[],this.axes=[]}this.renderProfileOptions(),this.renderCellOptions()}async refresh(){await Promise.all([this.refreshRuns(),this.refreshQueue(),this.refreshStatus()])}async refreshRuns(){if(this.runSection)try{const t=await(await fetch("/api/runs")).json(),n=this.currentRunId(),s=(t.runs??[]).find(r=>r.run_id===n);this.runSection.innerHTML=this.renderRun(s)}catch{this.runSection.innerHTML='<div class="note">the store did not answer</div>'}}async refreshQueue(){if(this.queueSection)try{const[e,t]=await Promise.all([fetch("/api/campaigns").then(n=>n.json()),fetch("/api/queue").then(n=>n.json())]);this.queueSection.innerHTML=this.renderQueue(e.campaigns??[],t),this.queueSection.querySelectorAll("[data-cancel]").forEach(n=>n.addEventListener("click",()=>{this.cancelCampaign(n.dataset.cancel??"")})),this.queueSection.querySelectorAll("[data-preempt]").forEach(n=>n.addEventListener("click",()=>{this.preemptCampaign(n.dataset.preempt??"")}))}catch{this.queueSection.innerHTML='<div class="note">the queue did not answer</div>'}}async refreshStatus(){if(this.newRunSection)try{const t=await(await fetch("/api/control")).json();if(!t.readable){this.newRunNote.textContent=t.error??"the control plane could not be read";return}const n=t.status;this.newRunNote.textContent=n?`The run is in ${n.stage} with ${n.cells_done} cells measured.`:"No run is reporting. The panel can still start one."}catch{this.newRunNote.textContent="the server did not answer"}}currentRunId(){return Vn.selectedId??null}renderProfileOptions(){if(this.profileSelect){this.profileSelect.innerHTML="";for(const e of this.profiles){const t=document.createElement("option");t.value=e.name,t.textContent=e.name,this.profileSelect.appendChild(t)}this.renderProfileNote()}}renderProfileNote(){if(!this.profileNote||!this.profileSelect)return;const e=this.profiles.find(t=>t.name===this.profileSelect.value);if(!e){this.profileNote.textContent="";return}this.profileNote.textContent=[e.description,`fidelity ${e.fidelity} · ${e.n_seeds} seeds · ${e.epochs} epochs`,e.budget_seconds?`budget ${e.budget_seconds}s`:"no budget",`policy ${e.policy}`,`axes ${e.axes.map(t=>t.axis).join(", ")||"all"}`].join(" · "),this.seedsInput&&(this.seedsInput.value=String(e.n_seeds)),this.epochsInput&&(this.epochsInput.value=String(e.epochs)),this.budgetInput&&(this.budgetInput.value=e.budget_seconds?String(e.budget_seconds):""),this.fidelitySelect&&(this.fidelitySelect.value=e.fidelity)}renderCellOptions(){for(const e of cc){const t=this.cellSelects.get(e);if(!t)continue;const n=this.axes.find(r=>r.axis===e);t.innerHTML="";for(const r of(n==null?void 0:n.primitives)??[]){const o=document.createElement("option");o.value=r.name,o.textContent=r.available?r.name:`${r.name} (unavailable)`,o.disabled=!r.available,t.appendChild(o)}const s=t.querySelector("option:not([disabled])");s&&(t.value=s.value)}}renderRun(e){if(!e)return'<div class="note">no run is selected</div>';const t=e.declaration??{};return[`<div class="note">A run's declaration is frozen once it has begun; the panel shows it rather than offering an editor that would lie.</div>`,`<table class="kv">${[["run",e.run_id],["status",String(e.status)],["profile",String(t.profile??"—")],["tasks",(t.tasks??[]).join(", ")||"—"],["fidelity",String(t.fidelity??"—")],["objectives",(t.objectives??[]).join(", ")||"—"],["mode",String(t.mode??"—")],["declared cells",String(t.declared_cells??"—")],["records",String(e.records)],["seeds still owed",String(e.seeds_owed??"—")]].map(([s,r])=>`<tr><th>${s}</th><td>${r}</td></tr>`).join("")}</table>`].join("")}renderQueue(e,t){const n=e.map(r=>`<tr>
          <td>${r.campaign_id}</td>
          <td>${r.name}</td>
          <td>${r.status}</td>
          <td>
            <button data-cancel="${r.campaign_id}" class="mini">cancel</button>
            <button data-preempt="${r.campaign_id}" class="mini">preempt</button>
          </td>
        </tr>`).join("");return[`<table class="kv">${[["max concurrent",String(t.max_concurrent??"—")],["max cpus",String(t.max_cpus??"—")],["max gpus",String(t.max_gpus??"—")]].map(([r,o])=>`<tr><th>${r}</th><td>${o}</td></tr>`).join("")}</table>`,n?`<table class="list"><tr><th>id</th><th>name</th><th>status</th><th></th></tr>${n}</table>`:'<div class="note">the queue is empty</div>'].join("")}async startRun(){var t,n,s,r,o;if(!this.profileSelect)return;const e={};(t=this.seedsInput)!=null&&t.value&&(e.n_seeds=Number(this.seedsInput.value)),(n=this.epochsInput)!=null&&n.value&&(e.epochs=Number(this.epochsInput.value)),(s=this.budgetInput)!=null&&s.value&&(e.budget_seconds=Number(this.budgetInput.value)),(r=this.fidelitySelect)!=null&&r.value&&(e.fidelity=this.fidelitySelect.value);try{const l=await(await fetch("/api/runs",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({profile:this.profileSelect.value,overrides:e,device:((o=this.deviceSelect)==null?void 0:o.value)??void 0})})).json();l.started?this.newRunNote.textContent=`The run is queued as ${l.campaign_id}.`:this.newRunNote.textContent=`${l.error??"the run was refused"}. ${l.command??""}`}catch{this.newRunNote.textContent="the dashboard could not reach the server"}}cellCoordinate(){var t;const e={};for(const n of cc)e[n]=((t=this.cellSelects.get(n))==null?void 0:t.value)??"";return e}async cellAction(e){const t=this.currentRunId();if(!t){this.cellNote.textContent="no run is selected";return}try{const s=await(await fetch(`/api/cells/${t}/${e}`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({coordinate:this.cellCoordinate()})})).json();this.cellNote.textContent=s.error??s.message??`${e} was refused`}catch{this.cellNote.textContent="the dashboard could not reach the server"}}async cancelCampaign(e){await fetch(`/api/campaigns/${e}/cancel`,{method:"POST"}),await this.refreshQueue()}async preemptCampaign(e){await fetch(`/api/campaigns/${e}/preempt`,{method:"POST"}),await this.refreshQueue()}async export(e){const t=this.currentRunId();if(!t){this.exportNote.textContent="no run is selected";return}try{if(e==="script"){const o=await fetch("/api/narration").then(a=>a.json());this.download("narration.txt",o.script??""),this.exportNote.textContent="the narration script was taken";return}const n=e==="report"?"report":"records",s=await fetch(`/api/runs/${t}/${n}`).then(o=>o.json());if(s.error){this.exportNote.textContent=s.error;return}const r=e==="report"?s.report??"":JSON.stringify(s.records??[],null,2);this.download(`${t}-${n}.${e==="report"?"txt":"json"}`,r),this.exportNote.textContent=`the ${e} was taken`}catch{this.exportNote.textContent="the dashboard could not reach the server"}}download(e,t){const n=new Blob([t],{type:"text/plain"}),s=document.createElement("a");s.download=e,s.href=URL.createObjectURL(n),s.click(),URL.revokeObjectURL(s.href)}}const Zo=new ES;qn.register(Zo);function TS(){return`
    <div id="drawer-content"></div>
  `}class AS{constructor(){R(this,"name","CellDrawer");R(this,"panel",null);R(this,"content",null);R(this,"sparklineCanvas",null);R(this,"currentData",null);R(this,"changeListeners",new Set);R(this,"onKeyDown",e=>{e.key==="Escape"&&this.currentData&&this.hide()});R(this,"onCellSelected",e=>{this.show(e.detail),this.notifyChange()})}async init(){this.panel=vs({id:"cell-drawer",title:"Cell Details",glyph:"◧",body:TS(),dock:"floating",defaultOpen:!1}),this.content=this.panel.querySelector("#drawer-content"),ap("cell-drawer","cell drawer","◧",()=>this.hide(),()=>this.isOpen()),console.log("[CellDrawer] Initialized")}async destroy(){var e;this.stopSparkline(),(e=this.panel)==null||e.remove(),window.removeEventListener("cell-selected",this.onCellSelected),window.removeEventListener("keydown",this.onKeyDown)}setupEvents(){window.addEventListener("cell-selected",this.onCellSelected),window.addEventListener("keydown",this.onKeyDown)}isOpen(){return this.panel?!this.panel.classList.contains("panel-hidden"):!1}hasCellSelected(){return this.currentData!==null}onChange(e){return this.changeListeners.add(e),()=>this.changeListeners.delete(e)}notifyChange(){for(const e of this.changeListeners)e()}replicateSelected(){this.currentData&&(this.runAction("replicate",this.currentData),this.notifyChange())}preregisterSelected(){this.currentData&&(this.runAction("preregister",this.currentData),this.notifyChange())}adoptQuestSelected(){this.currentData&&(this.runAction("quest",this.currentData),this.notifyChange())}show(e){this.currentData=e,this.renderContent(e),Rt.toggle("cell-drawer"),this.startSparkline(e)}hide(){Rt.toggle("cell-drawer"),this.stopSparkline(),this.currentData=null,this.notifyChange()}renderContent(e){if(!this.content)return;const{coordinate:t,metrics:n,status:s}=e,r=us[t.credit]||he.gradient,o=(n==null?void 0:n.val_acc)??0,a=(n==null?void 0:n.n_seeds)??0,l=e.chance??.1,c=e.requiredSeeds??0;let u="UNMEASURED",h=he.legal_unmeasured;s==="void"&&(u="VOID",h=he.void),s==="measured"&&(o<=l?(u="REJECTED",h=he.rejected):c>0&&a<c?(u="INSUFFICIENT",h=he.insufficient):o>l+.1?(u="PASSED",h=he.passed):(u="INSUFFICIENT",h=he.insufficient));const d=s==="measured"&&c>0?Math.max(0,c-a):"N/A";this.content.innerHTML=`
      <div style="margin-bottom: 20px;">
        <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px;">
          ${Object.entries(t).filter(([,f])=>f).map(([f,v])=>`
              <span class="coord-chip" data-axis="${f}" style="
                background: ${f==="credit"?r+"22":"var(--bg-tertiary)"};
                border: 1px solid ${f==="credit"?r+"88":"var(--border)"};
                border-radius: 12px;
                font-size: 11px;
                color: ${f==="credit"?r:"var(--text-primary)"};
              ">
                ${f}=${v}
              </span>
            `).join("")}
        </div>
      </div>

      ${n?`
        <div style="margin-bottom: 20px;">
          <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 4px;">VALIDATION ACCURACY</div>
          <div class="drawer-metric-value">${o.toFixed(3)}</div>
          <div style="font-size: 11px; color: var(--text-secondary); margin-top: 4px;">
            ± ${(n.val_acc_std??0).toFixed(3)} (n=${a})
          </div>
        </div>
      `:""}

      <div style="margin-bottom: 20px; padding: 12px; background: var(--bg-tertiary); border-radius: 6px;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
          <span class="verdict-badge" style="
            background: ${h}22;
            border: 1px solid ${h}88;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            color: ${h};
            text-transform: uppercase;
            padding: 4px 10px;
          ">${u}</span>
          <span style="font-size: 12px; color: var(--text-secondary);">Chance level: ${l}</span>
        </div>
        ${e.voidReason?`<div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 8px;">${e.voidReason}</div>`:""}
        <div class="progress-bar" style="height: 4px; background: var(--bg); border-radius: 2px; overflow: hidden;">
          <div class="progress-fill" style="
            width: ${Math.min(100,o/(l*2)*100)}%;
            height: 100%;
            background: linear-gradient(90deg, ${he.rejected}, ${he.insufficient}, ${he.passed});
            border-radius: 2px;
          "></div>
        </div>
      </div>

      ${s==="measured"?`
        <div style="margin-bottom: 20px;">
          <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 8px;">SEEDS TO CLAIM</div>
          <div class="drawer-metric-value" style="color: ${he.insufficient};">
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
              <div class="drawer-metric-value" style="font-size: 14px;">${n.walltime_s.toFixed(1)}s</div>
            </div>
            <div>
              <div style="color: var(--text-secondary);">Parameters</div>
              <div class="drawer-metric-value" style="font-size: 14px;">${((n.param_count??0)/1e3).toFixed(1)}K</div>
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
        gap: 10px;
        padding-top: 16px;
        border-top: 1px solid var(--border);
      ">
        <div id="drawer-action-note" style="font-size: 11px; color: var(--text-secondary); line-height: 1.5; min-height: 36px;">
        </div>
        <div style="display: flex; gap: 8px;">
          <button class="drawer-btn drawer-btn-primary" data-action="replicate" style="flex: 1;">Queue Rest</button>
          <button class="drawer-btn" data-action="preregister" style="flex: 1;">Preregister</button>
          <button class="drawer-btn" data-action="quest" style="flex: 1;">Adopt as Quest</button>
        </div>
        <div style="display: flex; gap: 8px; align-items: center;">
          <input id="drawer-threshold" class="drawer-input" type="number" step="0.001"
            placeholder="material effect (auto)" style="flex: 1;" />
          <span id="drawer-threshold-hint" style="font-size: 10px; color: var(--text-muted); white-space: nowrap;">auto = measured − chance</span>
        </div>
        <div id="drawer-status" style="font-size: 11px; color: var(--text-secondary); line-height: 1.5; min-height: 18px;"></div>
      </div>
    `,this.wireActions(e)}actionStates(e){var o;if(e.status==="void")return{replicate:!1,preregister:!1,quest:!1};const t=e.status==="measured",n=((o=e.metrics)==null?void 0:o.n_seeds)??0,s=e.requiredSeeds??0;return{replicate:(s>0?Math.max(0,s-n):0)>0||!t,preregister:t,quest:!t}}wireActions(e){const t=this.content;if(!t)return;const n=this.actionStates(e);t.querySelectorAll(".drawer-btn[data-action]").forEach(a=>{const l=a.dataset.action??"",c=n[l]===!0;a.disabled=!c,a.addEventListener("click",()=>{this.runAction(l,e)})});const r=t.querySelector('.drawer-btn[data-action="replicate"]');r&&(r.textContent=e.status==="measured"?"Queue Rest":"Queue");const o=t.querySelector("#drawer-action-note");o&&(o.textContent=this.actionNote(e))}actionNote(e){var s;if(!e.runId)return"This cell belongs to no run yet — nothing to queue or register.";if(e.status==="void")return`The system refuses this cell.${e.voidReason?` ${e.voidReason}`:""}`;if(e.status==="measured"){const r=((s=e.metrics)==null?void 0:s.n_seeds)??0,o=e.requiredSeeds??0,a=Math.max(0,o-r);return a>0?`Queue Rest adds ${a} more seeds to reach the claim threshold (${o} needed). Preregister locks in this cell's protocol for a confirmatory run.`:"This cell has enough seeds for a claim. Preregister locks in the protocol for a confirmatory run."}const t=e.inDeclaration===!1?" (outside this run's declaration)":"";return`Queue measures this cell (${e.requiredSeeds??0} seeds). Adopt as Quest writes the question first, then queues a new confirming run.${t}`}setStatus(e,t=!1){var s;const n=(s=this.content)==null?void 0:s.querySelector("#drawer-status");n&&(n.textContent=e,n.style.color=t?he.rejected:he.text_secondary)}async runAction(e,t){var a,l;if(!t.runId){this.setStatus("This cell belongs to no run yet.",!0);return}const n=Array.from(((a=this.content)==null?void 0:a.querySelectorAll(".drawer-btn"))??[]);n.forEach(c=>{c.disabled=!0}),this.setStatus("Working…");const s=(l=this.content)==null?void 0:l.querySelector("#drawer-threshold"),r=s!=null&&s.value?Number(s.value):null,o={coordinate:t.coordinate};r!==null&&Number.isFinite(r)&&(o.threshold=r);try{const c=await fetch(`/api/cells/${t.runId}/${e}`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(o)}),u=await c.json();if(!c.ok){this.setStatus((u==null?void 0:u.error)??"The action failed.",!0);return}this.setStatus(this.actionSummary(e,u))}catch(c){this.setStatus(`The action failed: ${String(c)}`,!0)}finally{n.forEach(c=>{c.disabled=!1})}}actionSummary(e,t){if(e==="replicate")return`Queued campaign ${t.campaign_id}: ${t.measurements} measurements in a plan of ${t.plan}.`;const s=`${t.written?"Registered":"Already registered"} ${t.path} — commit it; the run that follows it can be confirmatory.`;return e!=="quest"?s:t.campaign_id?`${s} Queued campaign ${t.campaign_id}: ${t.measurements} measurements in a plan of ${t.plan}, in a new run.`:`${s} No campaign queue is attached, so nothing is scheduled.`}startSparkline(e){const t=document.getElementById("sparkline-container");if(!t)return;this.stopSparkline();const n=e.curve??[];if(n.length===0){t.innerHTML=`
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
      `;return}const s=document.createElement("canvas");s.style.width="100%",s.style.height="100%",t.appendChild(s);const r=s.getContext("2d"),o=Math.min(window.devicePixelRatio,2),a=t.getBoundingClientRect();s.width=a.width*o,s.height=a.height*o,r.scale(o,o);const l=a.width,c=a.height,u=e.chance??.1,h=n.map(A=>A.val_acc),d=Math.min(u,...h),f=Math.max(...h,u),g=(f-d||1)*.1,m=d-g,p=f+g,x=A=>A/(n.length-1||1)*(l-20)+10,b=A=>c-10-(A-m)/(p-m)*(c-20);r.fillStyle=getComputedStyle(document.documentElement).getPropertyValue("--bg").trim()||"#0a0e14",r.fillRect(0,0,l,c);const w=b(u);r.strokeStyle=he.chance_line,r.lineWidth=1,r.setLineDash([4,4]),r.beginPath(),r.moveTo(10,w),r.lineTo(l-10,w),r.stroke(),r.setLineDash([]),r.fillStyle=he.chance_line,r.font="9px 'JetBrains Mono', monospace",r.textAlign="left",r.fillText("chance",12,w-4);const O=us[e.coordinate.credit]||he.gradient;r.strokeStyle=O,r.lineWidth=2,r.lineCap="round",r.lineJoin="round",r.beginPath(),n.forEach((A,L)=>{const k=x(L),E=b(A.val_acc);L===0?r.moveTo(k,E):r.lineTo(k,E)}),r.stroke(),r.fillStyle=O,n.forEach((A,L)=>{const k=x(L),E=b(A.val_acc);r.beginPath(),r.arc(k,E,3,0,Math.PI*2),r.fill()}),r.fillStyle=he.text_muted,r.font="9px 'JetBrains Mono', monospace",r.textAlign="right",r.fillText(p.toFixed(2),8,14),r.fillText(m.toFixed(2),8,c-6),this.sparklineCanvas=s}stopSparkline(){this.sparklineCanvas&&(this.sparklineCanvas.remove(),this.sparklineCanvas=null)}}const Un=new AS;qn.register(Un);const CS=!0,rn="u-",RS="uplot",PS=rn+"hz",LS=rn+"vt",DS=rn+"title",IS=rn+"wrap",US=rn+"under",NS=rn+"over",OS=rn+"axis",Fs=rn+"off",FS=rn+"select",kS=rn+"cursor-x",BS=rn+"cursor-y",zS=rn+"cursor-pt",HS=rn+"legend",VS=rn+"live",GS=rn+"inline",WS=rn+"series",qS=rn+"marker",Ld=rn+"label",XS=rn+"value",Sa="width",Ma="height",xa="top",Dd="bottom",Lr="left",uc="right",Du="#000",Id=Du+"0",hc="mousemove",Ud="mousedown",dc="mouseup",Nd="mouseenter",Od="mouseleave",Fd="dblclick",$S="resize",YS="scroll",kd="change",Jo="dppxchange",Iu="--",Qr=typeof window<"u",ru=Qr?document:null,Br=Qr?window:null,jS=Qr?navigator:null;let St,Co;function au(){let i=devicePixelRatio;St!=i&&(St=i,Co&&lu(kd,Co,au),Co=matchMedia(`(min-resolution: ${St-.001}dppx) and (max-resolution: ${St+.001}dppx)`),Hs(kd,Co,au),Br.dispatchEvent(new CustomEvent(Jo)))}function Hn(i,e){if(e!=null){let t=i.classList;!t.contains(e)&&t.add(e)}}function ou(i,e){let t=i.classList;t.contains(e)&&t.remove(e)}function kt(i,e,t){i.style[e]=t+"px"}function li(i,e,t,n){let s=ru.createElement(i);return e!=null&&Hn(s,e),t!=null&&t.insertBefore(s,n),s}function Zn(i,e){return li("div",i,e)}const Bd=new WeakMap;function Si(i,e,t,n,s){let r="translate("+e+"px,"+t+"px)",o=Bd.get(i);r!=o&&(i.style.transform=r,Bd.set(i,r),e<0||t<0||e>n||t>s?Hn(i,Fs):ou(i,Fs))}const zd=new WeakMap;function Hd(i,e,t){let n=e+t,s=zd.get(i);n!=s&&(zd.set(i,n),i.style.background=e,i.style.borderColor=t)}const Vd=new WeakMap;function Gd(i,e,t,n){let s=e+""+t,r=Vd.get(i);s!=r&&(Vd.set(i,s),i.style.height=t+"px",i.style.width=e+"px",i.style.marginLeft=n?-e/2+"px":0,i.style.marginTop=n?-t/2+"px":0)}const Uu={passive:!0},KS={...Uu,capture:!0};function Hs(i,e,t,n){e.addEventListener(i,t,n?KS:Uu)}function lu(i,e,t,n){e.removeEventListener(i,t,Uu)}Qr&&au();function ci(i,e,t,n){let s;t=t||0,n=n||e.length-1;let r=n<=2147483647;for(;n-t>1;)s=r?t+n>>1:Wn((t+n)/2),e[s]<i?t=s:n=s;return i-e[t]<=e[n]-i?t:n}function op(i){return(t,n,s)=>{let r=-1,o=-1;for(let a=n;a<=s;a++)if(i(t[a])){r=a;break}for(let a=s;a>=n;a--)if(i(t[a])){o=a;break}return[r,o]}}const lp=i=>i!=null,cp=i=>i!=null&&i>0,ll=op(lp),ZS=op(cp);function JS(i,e,t,n=0,s=!1){let r=s?ZS:ll,o=s?cp:lp;[e,t]=r(i,e,t);let a=i[e],l=i[e];if(e>-1)if(n==1)a=i[e],l=i[t];else if(n==-1)a=i[t],l=i[e];else for(let c=e;c<=t;c++){let u=i[c];o(u)&&(u<a?a=u:u>l&&(l=u))}return[a??Pt,l??-Pt]}function cl(i,e,t,n){let s=Xd(i),r=Xd(e);i==e&&(s==-1?(i*=t,e/=t):(i/=t,e*=t));let o=t==10?qi:up,a=s==1?Wn:Jn,l=r==1?Jn:Wn,c=a(o(Qt(i))),u=l(o(Qt(e))),h=Xr(t,c),d=Xr(t,u);return t==10&&(c<0&&(h=Lt(h,-c)),u<0&&(d=Lt(d,-u))),n||t==2?(i=h*s,e=d*r):(i=pp(i,h),e=ul(e,d)),[i,e]}function Nu(i,e,t,n){let s=cl(i,e,t,n);return i==0&&(s[0]=0),e==0&&(s[1]=0),s}const Ou=.1,Wd={mode:3,pad:Ou},La={pad:0,soft:null,mode:0},QS={min:La,max:La};function Qo(i,e,t,n){return hl(t)?qd(i,e,t):(La.pad=t,La.soft=n?0:null,La.mode=n?3:0,qd(i,e,QS))}function xt(i,e){return i??e}function eM(i,e,t){for(e=xt(e,0),t=xt(t,i.length-1);e<=t;){if(i[e]!=null)return!0;e++}return!1}function qd(i,e,t){let n=t.min,s=t.max,r=xt(n.pad,0),o=xt(s.pad,0),a=xt(n.hard,-Pt),l=xt(s.hard,Pt),c=xt(n.soft,Pt),u=xt(s.soft,-Pt),h=xt(n.mode,0),d=xt(s.mode,0),f=e-i,v=qi(f),g=Ln(Qt(i),Qt(e)),m=qi(g),p=Qt(m-v);(f<1e-24||p>10)&&(f=0,(i==0||e==0)&&(f=1e-24,h==2&&c!=Pt&&(r=0),d==2&&u!=-Pt&&(o=0)));let x=f||g||1e3,b=qi(x),w=Xr(10,Wn(b)),O=x*(f==0?i==0?.1:1:r),A=Lt(pp(i-O,w/10),24),L=i>=c&&(h==1||h==3&&A<=c||h==2&&A>=c)?c:Pt,k=Ln(a,A<L&&i>=L?L:di(L,A)),E=x*(f==0?e==0?.1:1:o),y=Lt(ul(e+E,w/10),24),P=e<=u&&(d==1||d==3&&y>=u||d==2&&y<=u)?u:-Pt,K=di(l,y>P&&e<=P?P:Ln(P,y));return k==K&&k==0&&(K=100),[k,K]}const tM=new Intl.NumberFormat(Qr?jS.language:"en-US"),Fu=i=>tM.format(i),$n=Math,ko=$n.PI,Qt=$n.abs,Wn=$n.floor,Jt=$n.round,Jn=$n.ceil,di=$n.min,Ln=$n.max,Xr=$n.pow,Xd=$n.sign,qi=$n.log10,up=$n.log2,nM=(i,e=1)=>$n.sinh(i)*e,fc=(i,e=1)=>$n.asinh(i/e),Pt=1/0;function $d(i){return(qi((i^i>>31)-(i>>31))|0)+1}function cu(i,e,t){return di(Ln(i,e),t)}function hp(i){return typeof i=="function"}function ft(i){return hp(i)?i:()=>i}const iM=()=>{},dp=i=>i,fp=(i,e)=>e,sM=i=>null,Yd=i=>!0,jd=(i,e)=>i==e,rM=/\.\d*?(?=9{6,}|0{6,})/gm,$s=i=>{if(gp(i)||ps.has(i))return i;const e=`${i}`,t=e.match(rM);if(t==null)return i;let n=t[0].length-1;if(e.indexOf("e-")!=-1){let[s,r]=e.split("e");return+`${$s(s)}e${r}`}return Lt(i,n)};function Is(i,e){return $s(Lt($s(i/e))*e)}function ul(i,e){return $s(Jn($s(i/e))*e)}function pp(i,e){return $s(Wn($s(i/e))*e)}function Lt(i,e=0){if(gp(i))return i;let t=10**e,n=i*t*(1+Number.EPSILON);return Jt(n)/t}const ps=new Map;function mp(i){return((""+i).split(".")[1]||"").length}function Fa(i,e,t,n){let s=[],r=n.map(mp);for(let o=e;o<t;o++){let a=Qt(o),l=Lt(Xr(i,o),a);for(let c=0;c<n.length;c++){let u=i==10?+`${n[c]}e${o}`:n[c]*l,h=(o>=0?0:a)+(o>=r[c]?0:r[c]),d=i==10?u:Lt(u,h);s.push(d),ps.set(d,h)}}return s}const Da={},ku=[],$r=[null,null],as=Array.isArray,gp=Number.isInteger,aM=i=>i===void 0;function Kd(i){return typeof i=="string"}function hl(i){let e=!1;if(i!=null){let t=i.constructor;e=t==null||t==Object}return e}function oM(i){return i!=null&&typeof i=="object"}const lM=Object.getPrototypeOf(Uint8Array),vp="__proto__";function Yr(i,e=hl){let t;if(as(i)){let n=i.find(s=>s!=null);if(as(n)||e(n)){t=Array(i.length);for(let s=0;s<i.length;s++)t[s]=Yr(i[s],e)}else t=i.slice()}else if(i instanceof lM)t=i.slice();else if(e(i)){t={};for(let n in i)n!=vp&&(t[n]=Yr(i[n],e))}else t=i;return t}function Zt(i){let e=arguments;for(let t=1;t<e.length;t++){let n=e[t];for(let s in n)s!=vp&&(hl(i[s])?Zt(i[s],Yr(n[s])):i[s]=Yr(n[s]))}return i}const cM=0,uM=1,hM=2;function dM(i,e,t){for(let n=0,s,r=-1;n<e.length;n++){let o=e[n];if(o>r){for(s=o-1;s>=0&&i[s]==null;)i[s--]=null;for(s=o+1;s<t&&i[s]==null;)i[r=s++]=null}}}function fM(i,e){if(gM(i)){let o=i[0].slice();for(let a=1;a<i.length;a++)o.push(...i[a].slice(1));return vM(o[0])||(o=mM(o)),o}let t=new Set;for(let o=0;o<i.length;o++){let l=i[o][0],c=l.length;for(let u=0;u<c;u++)t.add(l[u])}let n=[Array.from(t).sort((o,a)=>o-a)],s=n[0].length,r=new Map;for(let o=0;o<s;o++)r.set(n[0][o],o);for(let o=0;o<i.length;o++){let a=i[o],l=a[0];for(let c=1;c<a.length;c++){let u=a[c],h=Array(s).fill(void 0),d=e?e[o][c]:uM,f=[];for(let v=0;v<u.length;v++){let g=u[v],m=r.get(l[v]);g===null?d!=cM&&(h[m]=g,d==hM&&f.push(m)):h[m]=g}dM(h,f,s),n.push(h)}}return n}const pM=typeof queueMicrotask>"u"?i=>Promise.resolve().then(i):queueMicrotask;function mM(i){let e=i[0],t=e.length,n=Array(t);for(let r=0;r<n.length;r++)n[r]=r;n.sort((r,o)=>e[r]-e[o]);let s=[];for(let r=0;r<i.length;r++){let o=i[r],a=Array(t);for(let l=0;l<t;l++)a[l]=o[n[l]];s.push(a)}return s}function gM(i){let e=i[0][0],t=e.length;for(let n=1;n<i.length;n++){let s=i[n][0];if(s.length!=t)return!1;if(s!=e){for(let r=0;r<t;r++)if(s[r]!=e[r])return!1}}return!0}function vM(i,e=100){const t=i.length;if(t<=1)return!0;let n=0,s=t-1;for(;n<=s&&i[n]==null;)n++;for(;s>=n&&i[s]==null;)s--;if(s<=n)return!0;const r=Ln(1,Wn((s-n+1)/e));for(let o=i[n],a=n+r;a<=s;a+=r){const l=i[a];if(l!=null){if(l<=o)return!1;o=l}}return!0}const _p=["January","February","March","April","May","June","July","August","September","October","November","December"],xp=["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];function yp(i){return i.slice(0,3)}const _M=xp.map(yp),xM=_p.map(yp),yM={MMMM:_p,MMM:xM,WWWW:xp,WWW:_M};function ya(i){return(i<10?"0":"")+i}function bM(i){return(i<10?"00":i<100?"0":"")+i}const SM={YYYY:i=>i.getFullYear(),YY:i=>(i.getFullYear()+"").slice(2),MMMM:(i,e)=>e.MMMM[i.getMonth()],MMM:(i,e)=>e.MMM[i.getMonth()],MM:i=>ya(i.getMonth()+1),M:i=>i.getMonth()+1,DD:i=>ya(i.getDate()),D:i=>i.getDate(),WWWW:(i,e)=>e.WWWW[i.getDay()],WWW:(i,e)=>e.WWW[i.getDay()],HH:i=>ya(i.getHours()),H:i=>i.getHours(),h:i=>{let e=i.getHours();return e==0?12:e>12?e-12:e},AA:i=>i.getHours()>=12?"PM":"AM",aa:i=>i.getHours()>=12?"pm":"am",a:i=>i.getHours()>=12?"p":"a",mm:i=>ya(i.getMinutes()),m:i=>i.getMinutes(),ss:i=>ya(i.getSeconds()),s:i=>i.getSeconds(),fff:i=>bM(i.getMilliseconds())};function Bu(i,e){e=e||yM;let t=[],n=/\{([a-z]+)\}|[^{]+/gi,s;for(;s=n.exec(i);)t.push(s[0][0]=="{"?SM[s[1]]:s[0]);return r=>{let o="";for(let a=0;a<t.length;a++)o+=typeof t[a]=="string"?t[a]:t[a](r,e);return o}}const MM=new Intl.DateTimeFormat().resolvedOptions().timeZone;function wM(i,e){let t;return e=="UTC"||e=="Etc/UTC"?t=new Date(+i+i.getTimezoneOffset()*6e4):e==MM?t=i:(t=new Date(i.toLocaleString("en-US",{timeZone:e})),t.setMilliseconds(i.getMilliseconds())),t}const bp=i=>i%1==0,el=[1,2,2.5,5],EM=Fa(10,-32,0,el),Sp=Fa(10,0,32,el),TM=Sp.filter(bp),Us=EM.concat(Sp),zu=`
`,Mp="{YYYY}",Zd=zu+Mp,wp="{M}/{D}",wa=zu+wp,Ro=wa+"/{YY}",Ep="{aa}",AM="{h}:{mm}",Dr=AM+Ep,Jd=zu+Dr,Qd=":{ss}",Mt=null;function Tp(i){let e=i*1e3,t=e*60,n=t*60,s=n*24,r=s*30,o=s*365,l=(i==1?Fa(10,0,3,el).filter(bp):Fa(10,-3,0,el)).concat([e,e*5,e*10,e*15,e*30,t,t*5,t*10,t*15,t*30,n,n*2,n*3,n*4,n*6,n*8,n*12,s,s*2,s*3,s*4,s*5,s*6,s*7,s*8,s*9,s*10,s*15,r,r*2,r*3,r*4,r*6,o,o*2,o*5,o*10,o*25,o*50,o*100]);const c=[[o,Mp,Mt,Mt,Mt,Mt,Mt,Mt,1],[s*28,"{MMM}",Zd,Mt,Mt,Mt,Mt,Mt,1],[s,wp,Zd,Mt,Mt,Mt,Mt,Mt,1],[n,"{h}"+Ep,Ro,Mt,wa,Mt,Mt,Mt,1],[t,Dr,Ro,Mt,wa,Mt,Mt,Mt,1],[e,Qd,Ro+" "+Dr,Mt,wa+" "+Dr,Mt,Jd,Mt,1],[i,Qd+".{fff}",Ro+" "+Dr,Mt,wa+" "+Dr,Mt,Jd,Mt,1]];function u(h){return(d,f,v,g,m,p)=>{let x=[],b=m>=o,w=m>=r&&m<o,O=h(v),A=Lt(O*i,3),L=pc(O.getFullYear(),b?0:O.getMonth(),w||b?1:O.getDate()),k=Lt(L*i,3);if(w||b){let E=w?m/r:0,y=b?m/o:0,P=A==k?A:Lt(pc(L.getFullYear()+y,L.getMonth()+E,1)*i,3),K=new Date(Jt(P/i)),z=K.getFullYear(),Z=K.getMonth();for(let q=0;P<=g;q++){let Q=pc(z+y*q,Z+E*q,1),$=Q-h(Lt(Q*i,3));P=Lt((+Q+$)*i,3),P<=g&&x.push(P)}}else{let E=m>=s?s:m,y=Wn(v)-Wn(A),P=k+y+ul(A-k,E);x.push(P);let K=h(P),z=K.getHours()+K.getMinutes()/t+K.getSeconds()/n,Z=m/n,q=d.axes[f]._space,Q=p/q;for(;P=Lt(P+m,i==1?0:3),!(P>g);)if(Z>1){let $=Wn(Lt(z+Z,6))%24,de=h(P).getHours()-$;de>1&&(de=-1),P-=de*n,z=(z+Z)%24;let xe=x[x.length-1];Lt((P-xe)/m,3)*Q>=.7&&x.push(P)}else x.push(P)}return x}}return[l,c,u]}const[CM,RM,PM]=Tp(1),[LM,DM,IM]=Tp(.001);Fa(2,-53,53,[1]);function ef(i,e){return i.map(t=>t.map((n,s)=>s==0||s==8||n==null?n:e(s==1||t[8]==0?n:t[1]+n)))}function tf(i,e){return(t,n,s,r,o)=>{let a=e.find(v=>o>=v[0])||e[e.length-1],l,c,u,h,d,f;return n.map(v=>{let g=i(v),m=g.getFullYear(),p=g.getMonth(),x=g.getDate(),b=g.getHours(),w=g.getMinutes(),O=g.getSeconds(),A=m!=l&&a[2]||p!=c&&a[3]||x!=u&&a[4]||b!=h&&a[5]||w!=d&&a[6]||O!=f&&a[7]||a[1];return l=m,c=p,u=x,h=b,d=w,f=O,A(g)})}}function UM(i,e){let t=Bu(e);return(n,s,r,o,a)=>s.map(l=>t(i(l)))}function pc(i,e,t){return new Date(i,e,t)}function nf(i,e){return e(i)}const NM="{YYYY}-{MM}-{DD} {h}:{mm}{aa}";function sf(i,e){return(t,n,s,r)=>r==null?Iu:e(i(n))}function OM(i,e){let t=i.series[e];return t.width?t.stroke(i,e):t.points.width?t.points.stroke(i,e):null}function FM(i,e){return i.series[e].fill(i,e)}const kM={show:!0,live:!0,isolate:!1,mount:iM,markers:{show:!0,width:2,stroke:OM,fill:FM,dash:"solid"},idx:null,idxs:null,values:[]};function BM(i,e){let t=i.cursor.points,n=Zn(),s=t.size(i,e);kt(n,Sa,s),kt(n,Ma,s);let r=s/-2;kt(n,"marginLeft",r),kt(n,"marginTop",r);let o=t.width(i,e,s);return o&&kt(n,"borderWidth",o),n}function zM(i,e){let t=i.series[e].points;return t._fill||t._stroke}function HM(i,e){let t=i.series[e].points;return t._stroke||t._fill}function VM(i,e){return i.series[e].points.size}const mc=[0,0];function GM(i,e,t){return mc[0]=e,mc[1]=t,mc}function Po(i,e,t,n=!0){return s=>{s.button==0&&(!n||s.target==e)&&t(s)}}function gc(i,e,t,n=!0){return s=>{(!n||s.target==e)&&t(s)}}const WM={show:!0,x:!0,y:!0,lock:!1,move:GM,points:{one:!1,show:BM,size:VM,width:0,stroke:HM,fill:zM},bind:{mousedown:Po,mouseup:Po,click:Po,dblclick:Po,mousemove:gc,mouseleave:gc,mouseenter:gc},drag:{setScale:!0,x:!0,y:!1,dist:0,uni:null,click:(i,e)=>{e.stopPropagation(),e.stopImmediatePropagation()},_x:!1,_y:!1},focus:{dist:(i,e,t,n,s)=>n-s,prox:-1,bias:0},hover:{skip:[void 0],prox:null,bias:0},left:-10,top:-10,idx:null,dataIdx:null,idxs:null,event:null},Ap={show:!0,stroke:"rgba(0,0,0,0.07)",width:2},Hu=Zt({},Ap,{filter:fp}),Cp=Zt({},Hu,{size:10}),Rp=Zt({},Ap,{show:!1}),Vu='12px system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji"',Pp="bold "+Vu,Lp=1.5,rf={show:!0,scale:"x",stroke:Du,space:50,gap:5,alignTo:1,size:50,labelGap:0,labelSize:30,labelFont:Pp,side:2,grid:Hu,ticks:Cp,border:Rp,font:Vu,lineGap:Lp,rotate:0},qM="Value",XM="Time",af={show:!0,scale:"x",auto:!1,sorted:1,min:Pt,max:-Pt,idxs:[]};function $M(i,e,t,n,s){return e.map(r=>r==null?"":Fu(r))}function YM(i,e,t,n,s,r,o){let a=[],l=ps.get(s)||0;t=o?t:Lt(ul(t,s),l);for(let c=t;c<=n;c=Lt(c+s,l))a.push(Object.is(c,-0)?0:c);return a}function uu(i,e,t,n,s,r,o){const a=[],l=i.scales[i.axes[e].scale].log,c=l==10?qi:up,u=Wn(c(t));s=Xr(l,u),l==10&&(s=Us[ci(s,Us)]);let h=t,d=s*l;l==10&&(d=Us[ci(d,Us)]);do a.push(h),h=h+s,l==10&&!ps.has(h)&&(h=Lt(h,ps.get(s))),h>=d&&(s=h,d=s*l,l==10&&(d=Us[ci(d,Us)]));while(h<=n);return a}function jM(i,e,t,n,s,r,o){let l=i.scales[i.axes[e].scale].asinh,c=n>l?uu(i,e,Ln(l,t),n,s):[l],u=n>=0&&t<=0?[0]:[];return(t<-l?uu(i,e,Ln(l,-n),-t,s):[l]).reverse().map(d=>-d).concat(u,c)}const Dp=/./,KM=/[12357]/,ZM=/[125]/,of=/1/,hu=(i,e,t,n)=>i.map((s,r)=>e==4&&s==0||r%n==0&&t.test(s.toExponential()[s<0?1:0])?s:null);function JM(i,e,t,n,s){let r=i.axes[t],o=r.scale,a=i.scales[o],l=i.valToPos,c=r._space,u=l(10,o),h=l(9,o)-u>=c?Dp:l(7,o)-u>=c?KM:l(5,o)-u>=c?ZM:of;if(h==of){let d=Qt(l(1,o)-u);if(d<c)return hu(e.slice().reverse(),a.distr,h,Jn(c/d)).reverse()}return hu(e,a.distr,h,1)}function QM(i,e,t,n,s){let r=i.axes[t],o=r.scale,a=r._space,l=i.valToPos,c=Qt(l(1,o)-l(2,o));return c<a?hu(e.slice().reverse(),3,Dp,Jn(a/c)).reverse():e}function ew(i,e,t,n){return n==null?Iu:e==null?"":Fu(e)}const lf={show:!0,scale:"y",stroke:Du,space:30,gap:5,alignTo:1,size:50,labelGap:0,labelSize:30,labelFont:Pp,side:3,grid:Hu,ticks:Cp,border:Rp,font:Vu,lineGap:Lp,rotate:0};function tw(i,e){let t=3+(i||1)*2;return Lt(t*e,3)}function nw(i,e){let{scale:t,idxs:n}=i.series[0],s=i._data[0],r=i.valToPos(s[n[0]],t,!0),o=i.valToPos(s[n[1]],t,!0),a=Qt(o-r),l=i.series[e],c=a/(l.points.space*St);return n[1]-n[0]<=c}const cf={scale:null,auto:!0,sorted:0,min:Pt,max:-Pt},Ip=(i,e,t,n,s)=>s,uf={show:!0,auto:!0,sorted:0,gaps:Ip,alpha:1,facets:[Zt({},cf,{scale:"x"}),Zt({},cf,{scale:"y"})]},hf={scale:"y",auto:!0,sorted:0,show:!0,spanGaps:!1,gaps:Ip,alpha:1,points:{show:nw,filter:null},values:null,min:Pt,max:-Pt,idxs:[],path:null,clip:null};function iw(i,e,t,n,s){return t/10}const Up={time:CS,auto:!0,distr:1,log:10,asinh:1,min:null,max:null,dir:1,ori:0},sw=Zt({},Up,{time:!1,ori:1}),df={};function Np(i,e){let t=df[i];return t||(t={key:i,plots:[],sub(n){t.plots.push(n)},unsub(n){t.plots=t.plots.filter(s=>s!=n)},pub(n,s,r,o,a,l,c){for(let u=0;u<t.plots.length;u++)t.plots[u]!=s&&t.plots[u].pub(n,s,r,o,a,l,c)}},i!=null&&(df[i]=t)),t}const jr=1,du=2;function Ks(i,e,t){const n=i.mode,s=i.series[e],r=n==2?i._data[e]:i._data,o=i.scales,a=i.bbox;let l=r[0],c=n==2?r[1]:r[e],u=n==2?o[s.facets[0].scale]:o[i.series[0].scale],h=n==2?o[s.facets[1].scale]:o[s.scale],d=a.left,f=a.top,v=a.width,g=a.height,m=i.valToPosH,p=i.valToPosV;return u.ori==0?t(s,l,c,u,h,m,p,d,f,v,g,fl,ea,ml,Fp,Bp):t(s,l,c,u,h,p,m,f,d,g,v,pl,ta,qu,kp,zp)}function Gu(i,e){let t=0,n=0,s=xt(i.bands,ku);for(let r=0;r<s.length;r++){let o=s[r];o.series[0]==e?t=o.dir:o.series[1]==e&&(o.dir==1?n|=1:n|=2)}return[t,n==1?-1:n==2?1:n==3?2:0]}function rw(i,e,t,n,s){let r=i.mode,o=i.series[e],a=r==2?o.facets[1].scale:o.scale,l=i.scales[a];return s==-1?l.min:s==1?l.max:l.distr==3?l.dir==1?l.min:l.max:0}function Xi(i,e,t,n,s,r){return Ks(i,e,(o,a,l,c,u,h,d,f,v,g,m)=>{let p=o.pxRound;const x=c.dir*(c.ori==0?1:-1),b=c.ori==0?ea:ta;let w,O;x==1?(w=t,O=n):(w=n,O=t);let A=p(h(a[w],c,g,f)),L=p(d(l[w],u,m,v)),k=p(h(a[O],c,g,f)),E=p(d(r==1?u.max:u.min,u,m,v)),y=new Path2D(s);return b(y,k,E),b(y,A,E),b(y,A,L),y})}function dl(i,e,t,n,s,r){let o=null;if(i.length>0){o=new Path2D;const a=e==0?ml:qu;let l=t;for(let h=0;h<i.length;h++){let d=i[h];if(d[1]>d[0]){let f=d[0]-l;f>0&&a(o,l,n,f,n+r),l=d[1]}}let c=t+s-l,u=10;c>0&&a(o,l,n-u/2,c,n+r+u)}return o}function aw(i,e,t){let n=i[i.length-1];n&&n[0]==e?n[1]=t:i.push([e,t])}function Wu(i,e,t,n,s,r,o){let a=[],l=i.length;for(let c=s==1?t:n;c>=t&&c<=n;c+=s)if(e[c]===null){let h=c,d=c;if(s==1)for(;++c<=n&&e[c]===null;)d=c;else for(;--c>=t&&e[c]===null;)d=c;let f=r(i[h]),v=d==h?f:r(i[d]),g=h-s;f=o<=0&&g>=0&&g<l?r(i[g]):f;let p=d+s;v=o>=0&&p>=0&&p<l?r(i[p]):v,v>=f&&a.push([f,v])}return a}function ff(i){return i==0?dp:i==1?Jt:e=>Is(e,i)}function Op(i){let e=i==0?fl:pl,t=i==0?(s,r,o,a,l,c)=>{s.arcTo(r,o,a,l,c)}:(s,r,o,a,l,c)=>{s.arcTo(o,r,l,a,c)},n=i==0?(s,r,o,a,l)=>{s.rect(r,o,a,l)}:(s,r,o,a,l)=>{s.rect(o,r,l,a)};return(s,r,o,a,l,c=0,u=0)=>{c==0&&u==0?n(s,r,o,a,l):(c=di(c,a/2,l/2),u=di(u,a/2,l/2),e(s,r+c,o),t(s,r+a,o,r+a,o+l,c),t(s,r+a,o+l,r,o+l,u),t(s,r,o+l,r,o,u),t(s,r,o,r+a,o,c),s.closePath())}}const fl=(i,e,t)=>{i.moveTo(e,t)},pl=(i,e,t)=>{i.moveTo(t,e)},ea=(i,e,t)=>{i.lineTo(e,t)},ta=(i,e,t)=>{i.lineTo(t,e)},ml=Op(0),qu=Op(1),Fp=(i,e,t,n,s,r)=>{i.arc(e,t,n,s,r)},kp=(i,e,t,n,s,r)=>{i.arc(t,e,n,s,r)},Bp=(i,e,t,n,s,r,o)=>{i.bezierCurveTo(e,t,n,s,r,o)},zp=(i,e,t,n,s,r,o)=>{i.bezierCurveTo(t,e,s,n,o,r)};function Hp(i){return(e,t,n,s,r)=>Ks(e,t,(o,a,l,c,u,h,d,f,v,g,m)=>{let{pxRound:p,points:x}=o,b,w;c.ori==0?(b=fl,w=Fp):(b=pl,w=kp);const O=Lt(x.width*St,3);let A=(x.size-x.width)/2*St,L=Lt(A*2,3),k=new Path2D,E=new Path2D,{left:y,top:P,width:K,height:z}=e.bbox;ml(E,y-L,P-L,K+L*2,z+L*2);const Z=q=>{if(l[q]!=null){let Q=p(h(a[q],c,g,f)),$=p(d(l[q],u,m,v));b(k,Q+A,$),w(k,Q,$,A,0,ko*2)}};if(r)r.forEach(Z);else for(let q=n;q<=s;q++)Z(q);return{stroke:O>0?k:null,fill:k,clip:E,flags:jr|du}})}function Vp(i){return(e,t,n,s,r,o)=>{n!=s&&(r!=n&&o!=n&&i(e,t,n),r!=s&&o!=s&&i(e,t,s),i(e,t,o))}}const ow=Vp(ea),lw=Vp(ta);function Gp(i){const e=xt(i==null?void 0:i.alignGaps,0);return(t,n,s,r)=>Ks(t,n,(o,a,l,c,u,h,d,f,v,g,m)=>{[s,r]=ll(l,s,r);let p=o.pxRound,x=z=>p(h(z,c,g,f)),b=z=>p(d(z,u,m,v)),w,O;c.ori==0?(w=ea,O=ow):(w=ta,O=lw);const A=c.dir*(c.ori==0?1:-1),L={stroke:new Path2D,fill:null,clip:null,band:null,gaps:null,flags:jr},k=L.stroke;let E=!1;if(r-s>=g*4){let z=ye=>t.posToVal(ye,c.key,!0),Z=null,q=null,Q,$,te,ge=x(a[A==1?s:r]),de=x(a[s]),xe=x(a[r]),Ee=z(A==1?de+1:xe-1);for(let ye=A==1?s:r;ye>=s&&ye<=r;ye+=A){let ne=a[ye],be=(A==1?ne<Ee:ne>Ee)?ge:x(ne),fe=l[ye];be==ge?fe!=null?($=fe,Z==null?(w(k,be,b($)),Q=Z=q=$):$<Z?Z=$:$>q&&(q=$)):fe===null&&(E=!0):(Z!=null&&O(k,ge,b(Z),b(q),b(Q),b($)),fe!=null?($=fe,w(k,be,b($)),Z=q=Q=$):(Z=q=null,fe===null&&(E=!0)),ge=be,Ee=z(ge+A))}Z!=null&&Z!=q&&te!=ge&&O(k,ge,b(Z),b(q),b(Q),b($))}else for(let z=A==1?s:r;z>=s&&z<=r;z+=A){let Z=l[z];Z===null?E=!0:Z!=null&&w(k,x(a[z]),b(Z))}let[P,K]=Gu(t,n);if(o.fill!=null||P!=0){let z=L.fill=new Path2D(k),Z=o.fillTo(t,n,o.min,o.max,P),q=b(Z),Q=x(a[s]),$=x(a[r]);A==-1&&([$,Q]=[Q,$]),w(z,$,q),w(z,Q,q)}if(!o.spanGaps){let z=[];E&&z.push(...Wu(a,l,s,r,A,x,e)),L.gaps=z=o.gaps(t,n,s,r,z),L.clip=dl(z,c.ori,f,v,g,m)}return K!=0&&(L.band=K==2?[Xi(t,n,s,r,k,-1),Xi(t,n,s,r,k,1)]:Xi(t,n,s,r,k,K)),L})}function cw(i){const e=xt(i.align,1),t=xt(i.ascDesc,!1),n=xt(i.alignGaps,0),s=xt(i.extend,!1);return(r,o,a,l)=>Ks(r,o,(c,u,h,d,f,v,g,m,p,x,b)=>{[a,l]=ll(h,a,l);let w=c.pxRound,{left:O,width:A}=r.bbox,L=de=>w(v(de,d,x,m)),k=de=>w(g(de,f,b,p)),E=d.ori==0?ea:ta;const y={stroke:new Path2D,fill:null,clip:null,band:null,gaps:null,flags:jr},P=y.stroke,K=d.dir*(d.ori==0?1:-1);let z=k(h[K==1?a:l]),Z=L(u[K==1?a:l]),q=Z,Q=Z;s&&e==-1&&(Q=O,E(P,Q,z)),E(P,Z,z);for(let de=K==1?a:l;de>=a&&de<=l;de+=K){let xe=h[de];if(xe==null)continue;let Ee=L(u[de]),ye=k(xe);e==1?E(P,Ee,z):E(P,q,ye),E(P,Ee,ye),z=ye,q=Ee}let $=q;s&&e==1&&($=O+A,E(P,$,z));let[te,ge]=Gu(r,o);if(c.fill!=null||te!=0){let de=y.fill=new Path2D(P),xe=c.fillTo(r,o,c.min,c.max,te),Ee=k(xe);E(de,$,Ee),E(de,Q,Ee)}if(!c.spanGaps){let de=[];de.push(...Wu(u,h,a,l,K,L,n));let xe=c.width*St/2,Ee=t||e==1?xe:-xe,ye=t||e==-1?-xe:xe;de.forEach(ne=>{ne[0]+=Ee,ne[1]+=ye}),y.gaps=de=c.gaps(r,o,a,l,de),y.clip=dl(de,d.ori,m,p,x,b)}return ge!=0&&(y.band=ge==2?[Xi(r,o,a,l,P,-1),Xi(r,o,a,l,P,1)]:Xi(r,o,a,l,P,ge)),y})}function pf(i,e,t,n,s,r,o=Pt){if(i.length>1){let a=null;for(let l=0,c=1/0;l<i.length;l++)if(e[l]!==void 0){if(a!=null){let u=Qt(i[l]-i[a]);u<c&&(c=u,o=Qt(t(i[l],n,s,r)-t(i[a],n,s,r)))}a=l}}return o}function uw(i){i=i||Da;const e=xt(i.size,[.6,Pt,1]),t=i.align||0,n=i.gap||0;let s=i.radius;s=s==null?[0,0]:typeof s=="number"?[s,0]:s;const r=ft(s),o=1-e[0],a=xt(e[1],Pt),l=xt(e[2],1),c=xt(i.disp,Da),u=xt(i.each,f=>{}),{fill:h,stroke:d}=c;return(f,v,g,m)=>Ks(f,v,(p,x,b,w,O,A,L,k,E,y,P)=>{let K=p.pxRound,z=t,Z=n*St,q=a*St,Q=l*St,$,te;w.ori==0?[$,te]=r(f,v):[te,$]=r(f,v);const ge=w.dir*(w.ori==0?1:-1);let de=w.ori==0?ml:qu,xe=w.ori==0?u:(W,we,ve,Ae,Ke,me,Te)=>{u(W,we,ve,Ke,Ae,Te,me)},Ee=xt(f.bands,ku).find(W=>W.series[0]==v),ye=Ee!=null?Ee.dir:0,ne=p.fillTo(f,v,p.min,p.max,ye),ce=K(L(ne,O,P,E)),be,fe,ke,Ve=y,Ne=K(p.width*St),pt=!1,N=null,dt=null,it=null,ct=null;h!=null&&(Ne==0||d!=null)&&(pt=!0,N=h.values(f,v,g,m),dt=new Map,new Set(N).forEach(W=>{W!=null&&dt.set(W,new Path2D)}),Ne>0&&(it=d.values(f,v,g,m),ct=new Map,new Set(it).forEach(W=>{W!=null&&ct.set(W,new Path2D)})));let{x0:Oe,size:Et}=c;if(Oe!=null&&Et!=null){z=1,x=Oe.values(f,v,g,m),Oe.unit==2&&(x=x.map(ve=>f.posToVal(k+ve*y,w.key,!0)));let W=Et.values(f,v,g,m);Et.unit==2?fe=W[0]*y:fe=A(W[0],w,y,k)-A(0,w,y,k),Ve=pf(x,b,A,w,y,k,Ve),ke=Ve-fe+Z}else Ve=pf(x,b,A,w,y,k,Ve),ke=Ve*o+Z,fe=Ve-ke;ke<1&&(ke=0),Ne>=fe/2&&(Ne=0),ke<5&&(K=dp);let Xe=ke>0,We=Ve-ke-(Xe?Ne:0);fe=K(cu(We,Q,q)),be=(z==0?fe/2:z==ge?0:fe)-z*ge*((z==0?Z/2:0)+(Xe?Ne/2:0));const I={stroke:null,fill:null,clip:null,band:null,gaps:null,flags:0},M=pt?null:new Path2D;let J=null;if(Ee!=null)J=f.data[Ee.series[1]];else{let{y0:W,y1:we}=c;W!=null&&we!=null&&(b=we.values(f,v,g,m),J=W.values(f,v,g,m))}let oe=$*fe,ee=te*fe;for(let W=ge==1?g:m;W>=g&&W<=m;W+=ge){let we=b[W];if(we==null)continue;if(J!=null){let Me=J[W]??0;if(we-Me==0)continue;ce=L(Me,O,P,E)}let ve=w.distr!=2||c!=null?x[W]:W,Ae=A(ve,w,y,k),Ke=L(xt(we,ne),O,P,E),me=K(Ae-be),Te=K(Ln(Ke,ce)),Ze=K(di(Ke,ce)),Be=Te-Ze;if(we!=null){let Me=we<0?ee:oe,ze=we<0?oe:ee;pt?(Ne>0&&it[W]!=null&&de(ct.get(it[W]),me,Ze+Wn(Ne/2),fe,Ln(0,Be-Ne),Me,ze),N[W]!=null&&de(dt.get(N[W]),me,Ze+Wn(Ne/2),fe,Ln(0,Be-Ne),Me,ze)):de(M,me,Ze+Wn(Ne/2),fe,Ln(0,Be-Ne),Me,ze),xe(f,v,W,me-Ne/2,Ze,fe+Ne,Be)}}return Ne>0?I.stroke=pt?ct:M:pt||(I._fill=p.width==0?p._fill:p._stroke??p._fill,I.width=0),I.fill=pt?dt:M,I})}function hw(i,e){const t=xt(e==null?void 0:e.alignGaps,0);return(n,s,r,o)=>Ks(n,s,(a,l,c,u,h,d,f,v,g,m,p)=>{[r,o]=ll(c,r,o);let x=a.pxRound,b=$=>x(d($,u,m,v)),w=$=>x(f($,h,p,g)),O,A,L;u.ori==0?(O=fl,L=ea,A=Bp):(O=pl,L=ta,A=zp);const k=u.dir*(u.ori==0?1:-1);let E=b(l[k==1?r:o]),y=E,P=[],K=[];for(let $=k==1?r:o;$>=r&&$<=o;$+=k)if(c[$]!=null){let ge=l[$],de=b(ge);P.push(y=de),K.push(w(c[$]))}const z={stroke:i(P,K,O,L,A,x),fill:null,clip:null,band:null,gaps:null,flags:jr},Z=z.stroke;let[q,Q]=Gu(n,s);if(a.fill!=null||q!=0){let $=z.fill=new Path2D(Z),te=a.fillTo(n,s,a.min,a.max,q),ge=w(te);L($,y,ge),L($,E,ge)}if(!a.spanGaps){let $=[];$.push(...Wu(l,c,r,o,k,b,t)),z.gaps=$=a.gaps(n,s,r,o,$),z.clip=dl($,u.ori,v,g,m,p)}return Q!=0&&(z.band=Q==2?[Xi(n,s,r,o,Z,-1),Xi(n,s,r,o,Z,1)]:Xi(n,s,r,o,Z,Q)),z})}function dw(i){return hw(fw,i)}function fw(i,e,t,n,s,r){const o=i.length;if(o<2)return null;const a=new Path2D;if(t(a,i[0],e[0]),o==2)n(a,i[1],e[1]);else{let l=Array(o),c=Array(o-1),u=Array(o-1),h=Array(o-1);for(let d=0;d<o-1;d++)u[d]=e[d+1]-e[d],h[d]=i[d+1]-i[d],c[d]=u[d]/h[d];l[0]=c[0];for(let d=1;d<o-1;d++)c[d]===0||c[d-1]===0||c[d-1]>0!=c[d]>0?l[d]=0:(l[d]=3*(h[d-1]+h[d])/((2*h[d]+h[d-1])/c[d-1]+(h[d]+2*h[d-1])/c[d]),isFinite(l[d])||(l[d]=0));l[o-1]=c[o-2];for(let d=0;d<o-1;d++)s(a,i[d]+h[d]/3,e[d]+l[d]*h[d]/3,i[d+1]-h[d]/3,e[d+1]-l[d+1]*h[d]/3,i[d+1],e[d+1])}return a}const fu=new Set;function mf(){for(let i of fu)i.syncRect(!0)}Qr&&(Hs($S,Br,mf),Hs(YS,Br,mf,!0),Hs(Jo,Br,()=>{dn.pxRatio=St}));const pw=Gp(),mw=Hp();function gf(i,e,t,n){return(n?[i[0],i[1]].concat(i.slice(2)):[i[0]].concat(i.slice(1))).map((r,o)=>pu(r,o,e,t))}function gw(i,e){return i.map((t,n)=>n==0?{}:Zt({},e,t))}function pu(i,e,t,n){return Zt({},e==0?t:n,i)}function Wp(i,e,t){return e==null?$r:[e,t]}const vw=Wp;function _w(i,e,t){return e==null?$r:Qo(e,t,Ou,!0)}function qp(i,e,t,n){return e==null?$r:cl(e,t,i.scales[n].log,!1)}const xw=qp;function Xp(i,e,t,n){return e==null?$r:Nu(e,t,i.scales[n].log,!1)}const yw=Xp;function bw(i,e,t,n,s){let r=Ln($d(i),$d(e)),o=e-i,a=ci(s/n*o,t);do{let l=t[a],c=n*l/o;if(c>=s&&r+(l<5?ps.get(l):0)<=17)return[l,c]}while(++a<t.length);return[0,0]}function vf(i){let e,t;return i=i.replace(/(\d+)px/,(n,s)=>(e=Jt((t=+s)*St))+"px"),[i,e,t]}function Sw(i){i.show&&[i.font,i.labelFont].forEach(e=>{let t=Lt(e[2]*St,1);e[0]=e[0].replace(/[0-9.]+px/,t+"px"),e[1]=t})}function dn(i,e,t){const n={mode:xt(i.mode,1)},s=n.mode;function r(_,S,C,D){let B=S.valToPct(_);return D+C*(S.dir==-1?1-B:B)}function o(_,S,C,D){let B=S.valToPct(_);return D+C*(S.dir==-1?B:1-B)}function a(_,S,C,D){return S.ori==0?r(_,S,C,D):o(_,S,C,D)}n.valToPosH=r,n.valToPosV=o;let l=!1;n.status=0;const c=n.root=Zn(RS);if(i.id!=null&&(c.id=i.id),Hn(c,i.class),i.title){let _=Zn(DS,c);_.textContent=i.title}const u=li("canvas"),h=n.ctx=u.getContext("2d"),d=Zn(IS,c);Hs("click",d,_=>{_.target===v&&(Nt!=nr||Vt!=ir)&&mn.click(n,_)},!0);const f=n.under=Zn(US,d);d.appendChild(u);const v=n.over=Zn(NS,d);i=Yr(i);const g=+xt(i.pxAlign,1),m=ff(g);(i.plugins||[]).forEach(_=>{_.opts&&(i=_.opts(n,i)||i)});const p=i.ms||.001,x=n.series=s==1?gf(i.series||[],af,hf,!1):gw(i.series||[null],uf),b=n.axes=gf(i.axes||[],rf,lf,!0),w=n.scales={},O=n.bands=i.bands||[];O.forEach(_=>{_.fill=ft(_.fill||null),_.dir=xt(_.dir,-1)});const A=s==2?x[1].facets[0].scale:x[0].scale,L={axes:rm,series:In},k=(i.drawOrder||["axes","series"]).map(_=>L[_]);function E(_){const S=_.distr==3?C=>qi(C>0?C:_.clamp(n,C,_.min,_.max,_.key)):_.distr==4?C=>fc(C,_.asinh):_.distr==100?C=>_.fwd(C):C=>C;return C=>{let D=S(C),{_min:B,_max:Y}=_,ae=Y-B;return(D-B)/ae}}function y(_){let S=w[_];if(S==null){let C=(i.scales||Da)[_]||Da;if(C.from!=null){y(C.from);let D=Zt({},w[C.from],C,{key:_});D.valToPct=E(D),w[_]=D}else{S=w[_]=Zt({},_==A?Up:sw,C),S.key=_;let D=S.time,B=S.range,Y=as(B);if((_!=A||s==2&&!D)&&(Y&&(B[0]==null||B[1]==null)&&(B={min:B[0]==null?Wd:{mode:1,hard:B[0],soft:B[0]},max:B[1]==null?Wd:{mode:1,hard:B[1],soft:B[1]}},Y=!1),!Y&&hl(B))){let ae=B;B=(pe,Se,Le)=>Se==null?$r:Qo(Se,Le,ae)}S.range=ft(B||(D?vw:_==A?S.distr==3?xw:S.distr==4?yw:Wp:S.distr==3?qp:S.distr==4?Xp:_w)),S.auto=ft(Y?!1:S.auto),S.clamp=ft(S.clamp||iw),S._min=S._max=null,S.valToPct=E(S)}}}y("x"),y("y"),s==1&&x.forEach(_=>{y(_.scale)}),b.forEach(_=>{y(_.scale)});for(let _ in i.scales)y(_);const P=w[A],K=P.distr;let z,Z;P.ori==0?(Hn(c,PS),z=r,Z=o):(Hn(c,LS),z=o,Z=r);const q={};for(let _ in w){let S=w[_];(S.min!=null||S.max!=null)&&(q[_]={min:S.min,max:S.max},S.min=S.max=null)}const Q=i.tzDate||(_=>new Date(Jt(_/p))),$=i.fmtDate||Bu,te=p==1?PM(Q):IM(Q),ge=tf(Q,ef(p==1?RM:DM,$)),de=sf(Q,nf(NM,$)),xe=[],Ee=n.legend=Zt({},kM,i.legend),ye=n.cursor=Zt({},WM,{drag:{y:s==2}},i.cursor),ne=Ee.show,ce=ye.show,be=Ee.markers;Ee.idxs=xe,be.width=ft(be.width),be.dash=ft(be.dash),be.stroke=ft(be.stroke),be.fill=ft(be.fill);let fe,ke,Ve,Ne=[],pt=[],N,dt=!1,it={};if(Ee.live){const _=x[1]?x[1].values:null;dt=_!=null,N=dt?_(n,1,0):{_:0};for(let S in N)it[S]=Iu}if(ne)if(fe=li("table",HS,c),Ve=li("tbody",null,fe),Ee.mount(n,fe),dt){ke=li("thead",null,fe,Ve);let _=li("tr",null,ke);li("th",null,_);for(var ct in N)li("th",Ld,_).textContent=ct}else Hn(fe,GS),Ee.live&&Hn(fe,VS);const Oe={show:!0},Et={show:!1};function Xe(_,S){if(S==0&&(dt||!Ee.live||s==2))return $r;let C=[],D=li("tr",WS,Ve,Ve.childNodes[S]);Hn(D,_.class),_.show||Hn(D,Fs);let B=li("th",null,D);if(be.show){let pe=Zn(qS,B);if(S>0){let Se=be.width(n,S);Se&&(pe.style.border=Se+"px "+be.dash(n,S)+" "+be.stroke(n,S)),pe.style.background=be.fill(n,S)}}let Y=Zn(Ld,B);_.label instanceof HTMLElement?Y.appendChild(_.label):Y.textContent=_.label,S>0&&(be.show||(Y.style.color=_.width>0?be.stroke(n,S):be.fill(n,S)),I("click",B,pe=>{if(ye._lock)return;zt(pe);let Se=x.indexOf(_);if((pe.ctrlKey||pe.metaKey)!=Ee.isolate){let Le=x.some((De,Ue)=>Ue>0&&Ue!=Se&&De.show);x.forEach((De,Ue)=>{Ue>0&&_i(Ue,Le?Ue==Se?Oe:Et:Oe,!0,jt.setSeries)})}else _i(Se,{show:!_.show},!0,jt.setSeries)},!1),gi&&I(Nd,B,pe=>{ye._lock||(zt(pe),_i(x.indexOf(_),rr,!0,jt.setSeries))},!1));for(var ae in N){let pe=li("td",XS,D);pe.textContent="--",C.push(pe)}return[D,C]}const We=new Map;function I(_,S,C,D=!0){const B=We.get(S)||{},Y=ye.bind[_](n,S,C,D);Y&&(Hs(_,S,B[_]=Y),We.set(S,B))}function M(_,S,C){const D=We.get(S)||{};for(let B in D)(_==null||B==_)&&(lu(B,S,D[B]),delete D[B]);_==null&&We.delete(S)}let J=0,oe=0,ee=0,W=0,we=0,ve=0,Ae=we,Ke=ve,me=ee,Te=W,Ze=0,Be=0,Me=0,ze=0;n.bbox={};let F=!1,le=!1,U=!1,re=!1,ie=!1,se=!1;function _e(_,S,C){(C||_!=n.width||S!=n.height)&&je(_,S),Js(!1),U=!0,le=!0,Qs()}function je(_,S){n.width=J=ee=_,n.height=oe=W=S,we=ve=0,lt(),fn();let C=n.bbox;Ze=C.left=Is(we*St,.5),Be=C.top=Is(ve*St,.5),Me=C.width=Is(ee*St,.5),ze=C.height=Is(W*St,.5)}const ot=3;function vt(){let _=!1,S=0;for(;!_;){S++;let C=im(S),D=sm(S);_=S==ot||C&&D,_||(je(n.width,n.height),le=!0)}}function Tt({width:_,height:S}){_e(_,S)}n.setSize=Tt;function lt(){let _=!1,S=!1,C=!1,D=!1;b.forEach((B,Y)=>{if(B.show&&B._show){let{side:ae,_size:pe}=B,Se=ae%2,Le=B.label!=null?B.labelSize:0,De=pe+Le;De>0&&(Se?(ee-=De,ae==3?(we+=De,D=!0):C=!0):(W-=De,ae==0?(ve+=De,_=!0):S=!0))}}),Li[0]=_,Li[1]=C,Li[2]=S,Li[3]=D,ee-=j[1]+j[3],we+=j[3],W-=j[2]+j[0],ve+=j[0]}function fn(){let _=we+ee,S=ve+W,C=we,D=ve;function B(Y,ae){switch(Y){case 1:return _+=ae,_-ae;case 2:return S+=ae,S-ae;case 3:return C-=ae,C+ae;case 0:return D-=ae,D+ae}}b.forEach((Y,ae)=>{if(Y.show&&Y._show){let pe=Y.side;Y._pos=B(pe,Y._size),Y.label!=null&&(Y._lpos=B(pe,Y.labelSize))}})}if(ye.dataIdx==null){let _=ye.hover,S=_.skip=new Set(_.skip??[]);S.add(void 0);let C=_.prox=ft(_.prox),D=_.bias??(_.bias=0);ye.dataIdx=(B,Y,ae,pe)=>{if(Y==0)return ae;let Se=ae,Le=C(B,Y,ae,pe)??Pt,De=Le>=0&&Le<Pt,Ue=P.ori==0?ee:W,tt=ye.left,bt=e[0],_t=e[Y];if(S.has(_t[ae])){Se=null;let ht=null,et=null,Ge;if(D==0||D==-1)for(Ge=ae;ht==null&&Ge-- >0;)S.has(_t[Ge])||(ht=Ge);if(D==0||D==1)for(Ge=ae;et==null&&Ge++<_t.length;)S.has(_t[Ge])||(et=Ge);if(ht!=null||et!=null)if(De){let Ft=ht==null?-1/0:z(bt[ht],P,Ue,0),qt=et==null?1/0:z(bt[et],P,Ue,0),un=tt-Ft,Ct=qt-tt;un<=Ct?un<=Le&&(Se=ht):Ct<=Le&&(Se=et)}else Se=et==null?ht:ht==null?et:ae-ht<=et-ae?ht:et}else De&&Qt(tt-z(bt[ae],P,Ue,0))>Le&&(Se=null);return Se}}const zt=_=>{ye.event=_};ye.idxs=xe,ye._lock=!1;let Ht=ye.points;Ht.show=ft(Ht.show),Ht.size=ft(Ht.size),Ht.stroke=ft(Ht.stroke),Ht.width=ft(Ht.width),Ht.fill=ft(Ht.fill);const an=n.focus=Zt({},i.focus||{alpha:.3},ye.focus),gi=an.prox>=0,Ri=gi&&Ht.one;let wn=[],ni=[],Pi=[];function bs(_,S){let C=Ht.show(n,S);if(C instanceof HTMLElement)return Hn(C,zS),Hn(C,_.class),Si(C,-10,-10,ee,W),v.insertBefore(C,wn[S]),C}function ia(_,S){if(s==1||S>0){let C=s==1&&w[_.scale].time,D=_.value;_.value=C?Kd(D)?sf(Q,nf(D,$)):D||de:D||ew,_.label=_.label||(C?XM:qM)}if(Ri||S>0){_.width=_.width==null?1:_.width,_.paths=_.paths||pw||sM,_.fillTo=ft(_.fillTo||rw),_.pxAlign=+xt(_.pxAlign,g),_.pxRound=ff(_.pxAlign),_.stroke=ft(_.stroke||null),_.fill=ft(_.fill||null),_._stroke=_._fill=_._paths=_._focus=null;let C=tw(Ln(1,_.width),1),D=_.points=Zt({},{size:C,width:Ln(1,C*.2),stroke:_.stroke,space:C*2,paths:mw,_stroke:null,_fill:null},_.points);D.show=ft(D.show),D.filter=ft(D.filter),D.fill=ft(D.fill),D.stroke=ft(D.stroke),D.paths=ft(D.paths),D.pxAlign=_.pxAlign}if(ne){let C=Xe(_,S);Ne.splice(S,0,C[0]),pt.splice(S,0,C[1]),Ee.values.push(null)}if(ce){xe.splice(S,0,null);let C=null;Ri?S==0&&(C=bs(_,S)):S>0&&(C=bs(_,S)),wn.splice(S,0,C),ni.splice(S,0,0),Pi.splice(S,0,0)}cn("addSeries",S)}function za(_,S){S=S??x.length,_=s==1?pu(_,S,af,hf):pu(_,S,{},uf),x.splice(S,0,_),ia(x[S],S)}n.addSeries=za;function gl(_){if(x.splice(_,1),ne){Ee.values.splice(_,1),pt.splice(_,1);let S=Ne.splice(_,1)[0];M(null,S.firstChild),S.remove()}ce&&(xe.splice(_,1),wn.splice(_,1)[0].remove(),ni.splice(_,1),Pi.splice(_,1)),cn("delSeries",_)}n.delSeries=gl;const Li=[!1,!1,!1,!1];function vl(_,S){if(_._show=_.show,_.show){let C=_.side%2,D=w[_.scale];D==null&&(_.scale=C?x[1].scale:A,D=w[_.scale]);let B=D.time;_.size=ft(_.size),_.space=ft(_.space),_.rotate=ft(_.rotate),as(_.incrs)&&_.incrs.forEach(ae=>{!ps.has(ae)&&ps.set(ae,mp(ae))}),_.incrs=ft(_.incrs||(D.distr==2?TM:B?p==1?CM:LM:Us)),_.splits=ft(_.splits||(B&&D.distr==1?te:D.distr==3?uu:D.distr==4?jM:YM)),_.stroke=ft(_.stroke),_.grid.stroke=ft(_.grid.stroke),_.ticks.stroke=ft(_.ticks.stroke),_.border.stroke=ft(_.border.stroke);let Y=_.values;_.values=as(Y)&&!as(Y[0])?ft(Y):B?as(Y)?tf(Q,ef(Y,$)):Kd(Y)?UM(Q,Y):Y||ge:Y||$M,_.filter=ft(_.filter||(D.distr>=3&&D.log==10?JM:D.distr==3&&D.log==2?QM:fp)),_.font=vf(_.font),_.labelFont=vf(_.labelFont),_._size=_.size(n,null,S,0),_._space=_._rotate=_._incrs=_._found=_._splits=_._values=null,_._size>0&&(Li[S]=!0,_._el=Zn(OS,d))}}function T(_,S,C,D){let[B,Y,ae,pe]=C,Se=S%2,Le=0;return Se==0&&(pe||Y)&&(Le=S==0&&!B||S==2&&!ae?Jt(rf.size/3):0),Se==1&&(B||ae)&&(Le=S==1&&!Y||S==3&&!pe?Jt(lf.size/2):0),Le}const V=n.padding=(i.padding||[T,T,T,T]).map(_=>ft(xt(_,T))),j=n._padding=V.map((_,S)=>_(n,S,Li,0));let X,H=null,ue=null;const Re=s==1?x[0].idxs:null;let Pe=null,Ie=!1;function Je(_,S){if(e=_??[],n.data=n._data=e,s==2){X=0;for(let C=1;C<x.length;C++)X+=e[C][0].length}else{e.length==0&&(n.data=n._data=e=[[]]),Pe=e[0],X=Pe.length;let C=e;if(K==2){C=e.slice();let D=C[0]=Array(X);for(let B=0;B<X;B++)D[B]=B}n._data=e=C}if(Js(!0),cn("setData"),K==2&&(U=!0),S!==!1){let C=P;C.auto(n,Ie)?Qe():Ki(A,C.min,C.max),re=re||ye.left>=0,se=!0,Qs()}}n.setData=Je;function Qe(){Ie=!0;let _,S;s==1&&(X>0?(H=Re[0]=0,ue=Re[1]=X-1,_=e[0][H],S=e[0][ue],K==2?(_=H,S=ue):_==S&&(K==3?[_,S]=cl(_,_,P.log,!1):K==4?[_,S]=Nu(_,_,P.log,!1):P.time?S=_+Jt(86400/p):[_,S]=Qo(_,S,Ou,!0))):(H=Re[0]=_=null,ue=Re[1]=S=null)),Ki(A,_,S)}let Fe,ut,Dt,It,pn,mt,He,$t,gt,Ut;function Di(_,S,C,D,B,Y){_??(_=Id),C??(C=ku),D??(D="butt"),B??(B=Id),Y??(Y="round"),_!=Fe&&(h.strokeStyle=Fe=_),B!=ut&&(h.fillStyle=ut=B),S!=Dt&&(h.lineWidth=Dt=S),Y!=pn&&(h.lineJoin=pn=Y),D!=mt&&(h.lineCap=mt=D),C!=It&&h.setLineDash(It=C)}function _n(_,S,C,D){S!=ut&&(h.fillStyle=ut=S),_!=He&&(h.font=He=_),C!=$t&&(h.textAlign=$t=C),D!=gt&&(h.textBaseline=gt=D)}function Ss(_,S,C,D,B=0){if(D.length>0&&_.auto(n,Ie)&&(S==null||S.min==null)){let Y=xt(H,0),ae=xt(ue,D.length-1),pe=C.min==null?JS(D,Y,ae,B,_.distr==3):[C.min,C.max];_.min=di(_.min,C.min=pe[0]),_.max=Ln(_.max,C.max=pe[1])}}const Wt={min:null,max:null};function vi(){for(let D in w){let B=w[D];q[D]==null&&(B.min==null||q[A]!=null&&B.auto(n,Ie))&&(q[D]=Wt)}for(let D in w){let B=w[D];q[D]==null&&B.from!=null&&q[B.from]!=null&&(q[D]=Wt)}q[A]!=null&&Js(!0);let _={};for(let D in q){let B=q[D];if(B!=null){let Y=_[D]=Yr(w[D],oM);if(B.min!=null)Zt(Y,B);else if(D!=A||s==2)if(X==0&&Y.from==null){let ae=Y.range(n,null,null,D);Y.min=ae[0],Y.max=ae[1]}else Y.min=Pt,Y.max=-Pt}}if(X>0){x.forEach((D,B)=>{if(s==1){let Y=D.scale,ae=q[Y];if(ae==null)return;let pe=_[Y];if(B==0){let Se=pe.range(n,pe.min,pe.max,Y);pe.min=Se[0],pe.max=Se[1],H=ci(pe.min,e[0]),ue=ci(pe.max,e[0]),ue-H>1&&(e[0][H]<pe.min&&H++,e[0][ue]>pe.max&&ue--),D.min=Pe[H],D.max=Pe[ue]}else D.show&&D.auto&&Ss(pe,ae,D,e[B],D.sorted);D.idxs[0]=H,D.idxs[1]=ue}else if(B>0&&D.show&&D.auto){let[Y,ae]=D.facets,pe=Y.scale,Se=ae.scale,[Le,De]=e[B],Ue=_[pe],tt=_[Se];Ue!=null&&Ss(Ue,q[pe],Y,Le,Y.sorted),tt!=null&&Ss(tt,q[Se],ae,De,ae.sorted),D.min=ae.min,D.max=ae.max}});for(let D in _){let B=_[D],Y=q[D];if(B.from==null&&(Y==null||Y.min==null)){let ae=B.range(n,B.min==Pt?null:B.min,B.max==-Pt?null:B.max,D);B.min=ae[0],B.max=ae[1]}}}for(let D in _){let B=_[D];if(B.from!=null){let Y=_[B.from];if(Y.min==null)B.min=B.max=null;else{let ae=B.range(n,Y.min,Y.max,D);B.min=ae[0],B.max=ae[1]}}}let S={},C=!1;for(let D in _){let B=_[D],Y=w[D];if(Y.min!=B.min||Y.max!=B.max){Y.min=B.min,Y.max=B.max;let ae=Y.distr;Y._min=ae==3?qi(Y.min):ae==4?fc(Y.min,Y.asinh):ae==100?Y.fwd(Y.min):Y.min,Y._max=ae==3?qi(Y.max):ae==4?fc(Y.max,Y.asinh):ae==100?Y.fwd(Y.max):Y.max,S[D]=C=!0}}if(C){x.forEach((D,B)=>{s==2?B>0&&S.y&&(D._paths=null):S[D.scale]&&(D._paths=null)});for(let D in S)U=!0,cn("setScale",D);ce&&ye.left>=0&&(re=se=!0)}for(let D in q)q[D]=null}function sa(_){let S=cu(H-1,0,X-1),C=cu(ue+1,0,X-1);for(;_[S]==null&&S>0;)S--;for(;_[C]==null&&C<X-1;)C++;return[S,C]}function In(){if(X>0){let _=x.some(S=>S._focus)&&Ut!=an.alpha;_&&(h.globalAlpha=Ut=an.alpha),x.forEach((S,C)=>{if(C>0&&S.show&&(Zs(C,!1),Zs(C,!0),S._paths==null)){let D=Ut;Ut!=S.alpha&&(h.globalAlpha=Ut=S.alpha);let B=s==2?[0,e[C][0].length-1]:sa(e[C]);S._paths=S.paths(n,C,B[0],B[1]),Ut!=D&&(h.globalAlpha=Ut=D)}}),x.forEach((S,C)=>{if(C>0&&S.show){let D=Ut;Ut!=S.alpha&&(h.globalAlpha=Ut=S.alpha),S._paths!=null&&Ha(C,!1);{let B=S._paths!=null?S._paths.gaps:null,Y=S.points.show(n,C,H,ue,B),ae=S.points.filter(n,C,Y,B);(Y||ae)&&(S.points._paths=S.points.paths(n,C,H,ue,ae),Ha(C,!0))}Ut!=D&&(h.globalAlpha=Ut=D),cn("drawSeries",C)}}),_&&(h.globalAlpha=Ut=1)}}function Zs(_,S){let C=S?x[_].points:x[_];C._stroke=C.stroke(n,_),C._fill=C.fill(n,_)}function Ha(_,S){let C=S?x[_].points:x[_],{stroke:D,fill:B,clip:Y,flags:ae,_stroke:pe=C._stroke,_fill:Se=C._fill,_width:Le=C.width}=C._paths;Le=Lt(Le*St,3);let De=null,Ue=Le%2/2;S&&Se==null&&(Se=Le>0?"#fff":pe);let tt=C.pxAlign==1&&Ue>0;if(tt&&h.translate(Ue,Ue),!S){let bt=Ze-Le/2,_t=Be-Le/2,ht=Me+Le,et=ze+Le;De=new Path2D,De.rect(bt,_t,ht,et)}S?_l(pe,Le,C.dash,C.cap,Se,D,B,ae,Y):Va(_,pe,Le,C.dash,C.cap,Se,D,B,ae,De,Y),tt&&h.translate(-Ue,-Ue)}function Va(_,S,C,D,B,Y,ae,pe,Se,Le,De){let Ue=!1;Se!=0&&O.forEach((tt,bt)=>{if(tt.series[0]==_){let _t=x[tt.series[1]],ht=e[tt.series[1]],et=(_t._paths||Da).band;as(et)&&(et=tt.dir==1?et[0]:et[1]);let Ge,Ft=null;_t.show&&et&&eM(ht,H,ue)?(Ft=tt.fill(n,bt)||Y,Ge=_t._paths.clip):et=null,_l(S,C,D,B,Ft,ae,pe,Se,Le,De,Ge,et),Ue=!0}}),Ue||_l(S,C,D,B,Y,ae,pe,Se,Le,De)}const Yu=jr|du;function _l(_,S,C,D,B,Y,ae,pe,Se,Le,De,Ue){Di(_,S,C,D,B),(Se||Le||Ue)&&(h.save(),Se&&h.clip(Se),Le&&h.clip(Le)),Ue?(pe&Yu)==Yu?(h.clip(Ue),De&&h.clip(De),Wa(B,ae),Ga(_,Y,S)):pe&du?(Wa(B,ae),h.clip(Ue),Ga(_,Y,S)):pe&jr&&(h.save(),h.clip(Ue),De&&h.clip(De),Wa(B,ae),h.restore(),Ga(_,Y,S)):(Wa(B,ae),Ga(_,Y,S)),(Se||Le||Ue)&&h.restore()}function Ga(_,S,C){C>0&&(S instanceof Map?S.forEach((D,B)=>{h.strokeStyle=Fe=B,h.stroke(D)}):S!=null&&_&&h.stroke(S))}function Wa(_,S){S instanceof Map?S.forEach((C,D)=>{h.fillStyle=ut=D,h.fill(C)}):S!=null&&_&&h.fill(S)}function nm(_,S,C,D){let B=b[_],Y;if(D<=0)Y=[0,0];else{let ae=B._space=B.space(n,_,S,C,D),pe=B._incrs=B.incrs(n,_,S,C,D,ae);Y=bw(S,C,pe,D,ae)}return B._found=Y}function xl(_,S,C,D,B,Y,ae,pe,Se,Le){let De=ae%2/2;g==1&&h.translate(De,De),Di(pe,ae,Se,Le,pe),h.beginPath();let Ue,tt,bt,_t,ht=B+(D==0||D==3?-Y:Y);C==0?(tt=B,_t=ht):(Ue=B,bt=ht);for(let et=0;et<_.length;et++)S[et]!=null&&(C==0?Ue=bt=_[et]:tt=_t=_[et],h.moveTo(Ue,tt),h.lineTo(bt,_t));h.stroke(),g==1&&h.translate(-De,-De)}function im(_){let S=!0;return b.forEach((C,D)=>{if(!C.show)return;let B=w[C.scale];if(B.min==null){C._show&&(S=!1,C._show=!1,Js(!1));return}else C._show||(S=!1,C._show=!0,Js(!1));let Y=C.side,ae=Y%2,{min:pe,max:Se}=B,[Le,De]=nm(D,pe,Se,ae==0?ee:W);if(De==0)return;let Ue=B.distr==2,tt=C._splits=C.splits(n,D,pe,Se,Le,De,Ue),bt=B.distr==2?tt.map(Ge=>Pe[Ge]):tt,_t=B.distr==2?Pe[tt[1]]-Pe[tt[0]]:Le,ht=C._values=C.values(n,C.filter(n,bt,D,De,_t),D,De,_t);C._rotate=Y==2?C.rotate(n,ht,D,De):0;let et=C._size;C._size=Jn(C.size(n,ht,D,_)),et!=null&&C._size!=et&&(S=!1)}),S}function sm(_){let S=!0;return V.forEach((C,D)=>{let B=C(n,D,Li,_);B!=j[D]&&(S=!1),j[D]=B}),S}function rm(){for(let _=0;_<b.length;_++){let S=b[_];if(!S.show||!S._show)continue;let C=S.side,D=C%2,B,Y,ae=S.stroke(n,_),pe=C==0||C==3?-1:1,[Se,Le]=S._found;if(S.label!=null){let Tn=S.labelGap*pe,kn=Jt((S._lpos+Tn)*St);_n(S.labelFont[0],ae,"center",C==2?xa:Dd),h.save(),D==1?(B=Y=0,h.translate(kn,Jt(Be+ze/2)),h.rotate((C==3?-ko:ko)/2)):(B=Jt(Ze+Me/2),Y=kn);let Es=hp(S.label)?S.label(n,_,Se,Le):S.label;h.fillText(Es,B,Y),h.restore()}if(Le==0)continue;let De=w[S.scale],Ue=D==0?Me:ze,tt=D==0?Ze:Be,bt=S._splits,_t=De.distr==2?bt.map(Tn=>Pe[Tn]):bt,ht=De.distr==2?Pe[bt[1]]-Pe[bt[0]]:Se,et=S.ticks,Ge=S.border,Ft=et.show?et.size:0,qt=Jt(Ft*St),un=Jt((S.alignTo==2?S._size-Ft-S.gap:S.gap)*St),Ct=S._rotate*-ko/180,Xt=m(S._pos*St),On=(qt+un)*pe,En=Xt+On;Y=D==0?En:0,B=D==1?En:0;let Yn=S.font[0],ii=S.align==1?Lr:S.align==2?uc:Ct>0?Lr:Ct<0?uc:D==0?"center":C==3?uc:Lr,yi=Ct||D==1?"middle":C==2?xa:Dd;_n(Yn,ae,ii,yi);let Fn=S.font[1]*S.lineGap,jn=bt.map(Tn=>m(a(Tn,De,Ue,tt))),si=S._values;for(let Tn=0;Tn<si.length;Tn++){let kn=si[Tn];if(kn!=null){D==0?B=jn[Tn]:Y=jn[Tn],kn=""+kn;let Es=kn.indexOf(`
`)==-1?[kn]:kn.split(/\n/gm);for(let An=0;An<Es.length;An++){let fh=Es[An];Ct?(h.save(),h.translate(B,Y+An*Fn),h.rotate(Ct),h.fillText(fh,0,0),h.restore()):h.fillText(fh,B,Y+An*Fn)}}}et.show&&xl(jn,et.filter(n,_t,_,Le,ht),D,C,Xt,qt,Lt(et.width*St,3),et.stroke(n,_),et.dash,et.cap);let bi=S.grid;bi.show&&xl(jn,bi.filter(n,_t,_,Le,ht),D,D==0?2:1,D==0?Be:Ze,D==0?ze:Me,Lt(bi.width*St,3),bi.stroke(n,_),bi.dash,bi.cap),Ge.show&&xl([Xt],[1],D==0?1:0,D==0?1:2,D==1?Be:Ze,D==1?ze:Me,Lt(Ge.width*St,3),Ge.stroke(n,_),Ge.dash,Ge.cap)}cn("drawAxes")}function Js(_){x.forEach((S,C)=>{C>0&&(S._paths=null,_&&(s==1?(S.min=null,S.max=null):S.facets.forEach(D=>{D.min=null,D.max=null})))})}let qa=!1,yl=!1,ra=[];function am(){yl=!1;for(let _=0;_<ra.length;_++)cn(...ra[_]);ra.length=0}function Qs(){qa||(pM(ju),qa=!0)}function om(_,S=!1){qa=!0,yl=S,_(n),ju(),S&&ra.length>0&&queueMicrotask(am)}n.batch=om;function ju(){if(F&&(vi(),F=!1),U&&(vt(),U=!1),le){if(kt(f,Lr,we),kt(f,xa,ve),kt(f,Sa,ee),kt(f,Ma,W),kt(v,Lr,we),kt(v,xa,ve),kt(v,Sa,ee),kt(v,Ma,W),kt(d,Sa,J),kt(d,Ma,oe),u.width=Jt(J*St),u.height=Jt(oe*St),b.forEach(({_el:_,_show:S,_size:C,_pos:D,side:B})=>{if(_!=null)if(S){let Y=B===3||B===0?C:0,ae=B%2==1;kt(_,ae?"left":"top",D-Y),kt(_,ae?"width":"height",C),kt(_,ae?"top":"left",ae?ve:we),kt(_,ae?"height":"width",ae?W:ee),ou(_,Fs)}else Hn(_,Fs)}),Fe=ut=Dt=pn=mt=He=$t=gt=It=null,Ut=1,la(!0),we!=Ae||ve!=Ke||ee!=me||W!=Te){Js(!1);let _=ee/me,S=W/Te;if(ce&&!re&&ye.left>=0){ye.left*=_,ye.top*=S,er&&Si(er,Jt(ye.left),0,ee,W),tr&&Si(tr,0,Jt(ye.top),ee,W);for(let C=0;C<wn.length;C++){let D=wn[C];D!=null&&(ni[C]*=_,Pi[C]*=S,Si(D,Jn(ni[C]),Jn(Pi[C]),ee,W))}}if(Ot.show&&!ie&&Ot.left>=0&&Ot.width>0){Ot.left*=_,Ot.width*=_,Ot.top*=S,Ot.height*=S;for(let C in Tl)kt(sr,C,Ot[C])}Ae=we,Ke=ve,me=ee,Te=W}cn("setSize"),le=!1}J>0&&oe>0&&(h.clearRect(0,0,u.width,u.height),cn("drawClear"),k.forEach(_=>_()),cn("draw")),Ot.show&&ie&&(Xa(Ot),ie=!1),ce&&re&&(ws(null,!0,!1),re=!1),Ee.show&&Ee.live&&se&&(wl(),se=!1),l||(l=!0,n.status=1,cn("ready")),Ie=!1,qa=!1}n.redraw=(_,S)=>{U=S||!1,_!==!1?Ki(A,P.min,P.max):Qs()};function bl(_,S){let C=w[_];if(C.from==null){if(X==0){let D=C.range(n,S.min,S.max,_);S.min=D[0],S.max=D[1]}if(S.min>S.max){let D=S.min;S.min=S.max,S.max=D}if(X>1&&S.min!=null&&S.max!=null&&S.max-S.min<1e-16)return;_==A&&C.distr==2&&X>0&&(S.min=ci(S.min,e[0]),S.max=ci(S.max,e[0]),S.min==S.max&&S.max++),q[_]=S,F=!0,Qs()}}n.setScale=bl;let Sl,Ml,er,tr,Ku,Zu,nr,ir,Ju,Qu,Nt,Vt,ji=!1;const mn=ye.drag;let on=mn.x,ln=mn.y;ce&&(ye.x&&(Sl=Zn(kS,v)),ye.y&&(Ml=Zn(BS,v)),P.ori==0?(er=Sl,tr=Ml):(er=Ml,tr=Sl),Nt=ye.left,Vt=ye.top);const Ot=n.select=Zt({show:!0,over:!0,left:0,width:0,top:0,height:0},i.select),sr=Ot.show?Zn(FS,Ot.over?v:f):null;function Xa(_,S){if(Ot.show){for(let C in _)Ot[C]=_[C],C in Tl&&kt(sr,C,_[C]);S!==!1&&cn("setSelect")}}n.setSelect=Xa;function lm(_){if(x[_].show)ne&&ou(Ne[_],Fs);else if(ne&&Hn(Ne[_],Fs),ce){let C=Ri?wn[0]:wn[_];C!=null&&Si(C,-10,-10,ee,W)}}function Ki(_,S,C){bl(_,{min:S,max:C})}function _i(_,S,C,D){S.focus!=null&&fm(_),S.show!=null&&x.forEach((B,Y)=>{Y>0&&(_==Y||_==null)&&(B.show=S.show,lm(Y),s==2?(Ki(B.facets[0].scale,null,null),Ki(B.facets[1].scale,null,null)):Ki(B.scale,null,null),Qs())}),C!==!1&&cn("setSeries",_,S),D&&ca("setSeries",n,_,S)}n.setSeries=_i;function cm(_,S){Zt(O[_],S)}function um(_,S){_.fill=ft(_.fill||null),_.dir=xt(_.dir,-1),S=S??O.length,O.splice(S,0,_)}function hm(_){_==null?O.length=0:O.splice(_,1)}n.addBand=um,n.setBand=cm,n.delBand=hm;function dm(_,S){x[_].alpha=S,ce&&wn[_]!=null&&(wn[_].style.opacity=S),ne&&Ne[_]&&(Ne[_].style.opacity=S)}let Ii,Zi,Ms;const rr={focus:!0};function fm(_){if(_!=Ms){let S=_==null,C=an.alpha!=1;x.forEach((D,B)=>{if(s==1||B>0){let Y=S||B==0||B==_;D._focus=S?null:Y,C&&dm(B,Y?1:an.alpha)}}),Ms=_,C&&Qs()}}ne&&gi&&I(Od,fe,_=>{ye._lock||(zt(_),Ms!=null&&_i(null,rr,!0,jt.setSeries))});function xi(_,S,C){let D=w[S];C&&(_=_/St-(D.ori==1?ve:we));let B=ee;D.ori==1&&(B=W,_=B-_),D.dir==-1&&(_=B-_);let Y=D._min,ae=D._max,pe=_/B,Se=Y+(ae-Y)*pe,Le=D.distr;return Le==3?Xr(10,Se):Le==4?nM(Se,D.asinh):Le==100?D.bwd(Se):Se}function pm(_,S){let C=xi(_,A,S);return ci(C,e[0],H,ue)}n.valToIdx=_=>ci(_,e[0]),n.posToIdx=pm,n.posToVal=xi,n.valToPos=(_,S,C)=>w[S].ori==0?r(_,w[S],C?Me:ee,C?Ze:0):o(_,w[S],C?ze:W,C?Be:0),n.setCursor=(_,S,C)=>{Nt=_.left,Vt=_.top,ws(null,S,C)};function eh(_,S){kt(sr,Lr,Ot.left=_),kt(sr,Sa,Ot.width=S)}function th(_,S){kt(sr,xa,Ot.top=_),kt(sr,Ma,Ot.height=S)}let aa=P.ori==0?eh:th,oa=P.ori==1?eh:th;function mm(){if(ne&&Ee.live)for(let _=s==2?1:0;_<x.length;_++){if(_==0&&dt)continue;let S=Ee.values[_],C=0;for(let D in S)pt[_][C++].firstChild.nodeValue=S[D]}}function wl(_,S){if(_!=null&&(_.idxs?_.idxs.forEach((C,D)=>{xe[D]=C}):aM(_.idx)||xe.fill(_.idx),Ee.idx=xe[0]),ne&&Ee.live){for(let C=0;C<x.length;C++)(C>0||s==1&&!dt)&&gm(C,xe[C]);mm()}se=!1,S!==!1&&cn("setLegend")}n.setLegend=wl;function gm(_,S){let C=x[_],D=_==0&&K==2?Pe:e[_],B;dt?B=C.values(n,_,S)??it:(B=C.value(n,S==null?null:D[S],_,S),B=B==null?it:{_:B}),Ee.values[_]=B}function ws(_,S,C){Ju=Nt,Qu=Vt,[Nt,Vt]=ye.move(n,Nt,Vt),ye.left=Nt,ye.top=Vt,ce&&(er&&Si(er,Jt(Nt),0,ee,W),tr&&Si(tr,0,Jt(Vt),ee,W));let D,B=H>ue;Ii=Pt,Zi=null;let Y=P.ori==0?ee:W,ae=P.ori==1?ee:W;if(Nt<0||X==0||B){D=ye.idx=null;for(let pe=0;pe<x.length;pe++){let Se=wn[pe];Se!=null&&Si(Se,-10,-10,ee,W)}gi&&_i(null,rr,!0,_==null&&jt.setSeries),Ee.live&&(xe.fill(D),se=!0)}else{let pe,Se,Le;s==1&&(pe=P.ori==0?Nt:Vt,Se=xi(pe,A),D=ye.idx=ci(Se,e[0],H,ue),Le=z(e[0][D],P,Y,0));let De=-10,Ue=-10,tt=0,bt=0,_t=!0,ht="",et="";for(let Ge=s==2?1:0;Ge<x.length;Ge++){let Ft=x[Ge],qt=xe[Ge],un=qt==null?null:s==1?e[Ge][qt]:e[Ge][1][qt],Ct=ye.dataIdx(n,Ge,D,Se),Xt=Ct==null?null:s==1?e[Ge][Ct]:e[Ge][1][Ct];if(se=se||Xt!=un||Ct!=qt,xe[Ge]=Ct,Ge>0&&Ft.show){let On=Ct==null?-10:Ct==D?Le:z(s==1?e[0][Ct]:e[Ge][0][Ct],P,Y,0),En=Xt==null?-10:Z(Xt,s==1?w[Ft.scale]:w[Ft.facets[1].scale],ae,0);if(gi&&Xt!=null){let Yn=P.ori==1?Nt:Vt,ii=Qt(an.dist(n,Ge,Ct,En,Yn));if(ii<Ii){let yi=an.bias;if(yi!=0){let Fn=xi(Yn,Ft.scale),jn=Xt>=0?1:-1,si=Fn>=0?1:-1;si==jn&&(si==1?yi==1?Xt>=Fn:Xt<=Fn:yi==1?Xt<=Fn:Xt>=Fn)&&(Ii=ii,Zi=Ge)}else Ii=ii,Zi=Ge}}if(se||Ri){let Yn,ii;P.ori==0?(Yn=On,ii=En):(Yn=En,ii=On);let yi,Fn,jn,si,bi,Tn,kn=!0,Es=Ht.bbox;if(Es!=null){kn=!1;let An=Es(n,Ge);jn=An.left,si=An.top,yi=An.width,Fn=An.height}else jn=Yn,si=ii,yi=Fn=Ht.size(n,Ge);if(Tn=Ht.fill(n,Ge),bi=Ht.stroke(n,Ge),Ri)Ge==Zi&&Ii<=an.prox&&(De=jn,Ue=si,tt=yi,bt=Fn,_t=kn,ht=Tn,et=bi);else{let An=wn[Ge];An!=null&&(ni[Ge]=jn,Pi[Ge]=si,Gd(An,yi,Fn,kn),Hd(An,Tn,bi),Si(An,Jn(jn),Jn(si),ee,W))}}}}if(Ri){let Ge=an.prox,Ft=Ms==null?Ii<=Ge:Ii>Ge||Zi!=Ms;if(se||Ft){let qt=wn[0];qt!=null&&(ni[0]=De,Pi[0]=Ue,Gd(qt,tt,bt,_t),Hd(qt,ht,et),Si(qt,Jn(De),Jn(Ue),ee,W))}}}if(Ot.show&&ji)if(_!=null){let[pe,Se]=jt.scales,[Le,De]=jt.match,[Ue,tt]=_.cursor.sync.scales,bt=_.cursor.drag;if(on=bt._x,ln=bt._y,on||ln){let{left:_t,top:ht,width:et,height:Ge}=_.select,Ft=_.scales[Ue].ori,qt=_.posToVal,un,Ct,Xt,On,En,Yn=pe!=null&&Le(pe,Ue),ii=Se!=null&&De(Se,tt);Yn&&on?(Ft==0?(un=_t,Ct=et):(un=ht,Ct=Ge),Xt=w[pe],On=z(qt(un,Ue),Xt,Y,0),En=z(qt(un+Ct,Ue),Xt,Y,0),aa(di(On,En),Qt(En-On))):aa(0,Y),ii&&ln?(Ft==1?(un=_t,Ct=et):(un=ht,Ct=Ge),Xt=w[Se],On=Z(qt(un,tt),Xt,ae,0),En=Z(qt(un+Ct,tt),Xt,ae,0),oa(di(On,En),Qt(En-On))):oa(0,ae)}else Al()}else{let pe=Qt(Ju-Ku),Se=Qt(Qu-Zu);if(P.ori==1){let tt=pe;pe=Se,Se=tt}on=mn.x&&pe>=mn.dist,ln=mn.y&&Se>=mn.dist;let Le=mn.uni;Le!=null?on&&ln&&(on=pe>=Le,ln=Se>=Le,!on&&!ln&&(Se>pe?ln=!0:on=!0)):mn.x&&mn.y&&(on||ln)&&(on=ln=!0);let De,Ue;on&&(P.ori==0?(De=nr,Ue=Nt):(De=ir,Ue=Vt),aa(di(De,Ue),Qt(Ue-De)),ln||oa(0,ae)),ln&&(P.ori==1?(De=nr,Ue=Nt):(De=ir,Ue=Vt),oa(di(De,Ue),Qt(Ue-De)),on||aa(0,Y)),!on&&!ln&&(aa(0,0),oa(0,0))}if(mn._x=on,mn._y=ln,_==null){if(C){if(dh!=null){let[pe,Se]=jt.scales;jt.values[0]=pe!=null?xi(P.ori==0?Nt:Vt,pe):null,jt.values[1]=Se!=null?xi(P.ori==1?Nt:Vt,Se):null}ca(hc,n,Nt,Vt,ee,W,D)}if(gi){let pe=C&&jt.setSeries,Se=an.prox;Ms==null?Ii<=Se&&_i(Zi,rr,!0,pe):Ii>Se?_i(null,rr,!0,pe):Zi!=Ms&&_i(Zi,rr,!0,pe)}}se&&(Ee.idx=D,wl()),S!==!1&&cn("setCursor")}let Ji=null;Object.defineProperty(n,"rect",{get(){return Ji==null&&la(!1),Ji}});function la(_=!1){_?Ji=null:(Ji=v.getBoundingClientRect(),cn("syncRect",Ji))}function nh(_,S,C,D,B,Y,ae){ye._lock||ji&&_!=null&&_.movementX==0&&_.movementY==0||(El(_,S,C,D,B,Y,ae,!1,_!=null),_!=null?ws(null,!0,!0):ws(S,!0,!1))}function El(_,S,C,D,B,Y,ae,pe,Se){if(Ji==null&&la(!1),zt(_),_!=null)C=_.clientX-Ji.left,D=_.clientY-Ji.top;else{if(C<0||D<0){Nt=-10,Vt=-10;return}let[Le,De]=jt.scales,Ue=S.cursor.sync,[tt,bt]=Ue.values,[_t,ht]=Ue.scales,[et,Ge]=jt.match,Ft=S.axes[0].side%2==1,qt=P.ori==0?ee:W,un=P.ori==1?ee:W,Ct=Ft?Y:B,Xt=Ft?B:Y,On=Ft?D:C,En=Ft?C:D;if(_t!=null?C=et(Le,_t)?a(tt,w[Le],qt,0):-10:C=qt*(On/Ct),ht!=null?D=Ge(De,ht)?a(bt,w[De],un,0):-10:D=un*(En/Xt),P.ori==1){let Yn=C;C=D,D=Yn}}Se&&(S==null||S.cursor.event.type==hc)&&((C<=1||C>=ee-1)&&(C=Is(C,ee)),(D<=1||D>=W-1)&&(D=Is(D,W))),pe?(Ku=C,Zu=D,[nr,ir]=ye.move(n,C,D)):(Nt=C,Vt=D)}const Tl={width:0,height:0,left:0,top:0};function Al(){Xa(Tl,!1)}let ih,sh,rh,ah;function oh(_,S,C,D,B,Y,ae){ji=!0,on=ln=mn._x=mn._y=!1,El(_,S,C,D,B,Y,ae,!0,!1),_!=null&&(I(dc,ru,lh,!1),ca(Ud,n,nr,ir,ee,W,null));let{left:pe,top:Se,width:Le,height:De}=Ot;ih=pe,sh=Se,rh=Le,ah=De}function lh(_,S,C,D,B,Y,ae){ji=mn._x=mn._y=!1,El(_,S,C,D,B,Y,ae,!1,!0);let{left:pe,top:Se,width:Le,height:De}=Ot,Ue=Le>0||De>0,tt=ih!=pe||sh!=Se||rh!=Le||ah!=De;if(Ue&&tt&&Xa(Ot),mn.setScale&&Ue&&tt){let bt=pe,_t=Le,ht=Se,et=De;if(P.ori==1&&(bt=Se,_t=De,ht=pe,et=Le),on&&Ki(A,xi(bt,A),xi(bt+_t,A)),ln)for(let Ge in w){let Ft=w[Ge];Ge!=A&&Ft.from==null&&Ft.min!=Pt&&Ki(Ge,xi(ht+et,Ge),xi(ht,Ge))}Al()}else ye.lock&&(ye._lock=!ye._lock,ws(S,!0,_!=null));_!=null&&(M(dc,ru),ca(dc,n,Nt,Vt,ee,W,null))}function vm(_,S,C,D,B,Y,ae){if(ye._lock)return;zt(_);let pe=ji;if(ji){let Se=!0,Le=!0,De=10,Ue,tt;P.ori==0?(Ue=on,tt=ln):(Ue=ln,tt=on),Ue&&tt&&(Se=Nt<=De||Nt>=ee-De,Le=Vt<=De||Vt>=W-De),Ue&&Se&&(Nt=Nt<nr?0:ee),tt&&Le&&(Vt=Vt<ir?0:W),ws(null,!0,!0),ji=!1}Nt=-10,Vt=-10,xe.fill(null),ws(null,!0,!0),pe&&(ji=pe)}function ch(_,S,C,D,B,Y,ae){ye._lock||(zt(_),Qe(),Al(),_!=null&&ca(Fd,n,Nt,Vt,ee,W,null))}function uh(){b.forEach(Sw),_e(n.width,n.height,!0)}Hs(Jo,Br,uh);const ar={};ar.mousedown=oh,ar.mousemove=nh,ar.mouseup=lh,ar.dblclick=ch,ar.setSeries=(_,S,C,D)=>{let B=jt.match[2];C=B(n,S,C),C!=-1&&_i(C,D,!0,!1)},ce&&(I(Ud,v,oh),I(hc,v,nh),I(Nd,v,_=>{zt(_),la(!1)}),I(Od,v,vm),I(Fd,v,ch),fu.add(n),n.syncRect=la);const $a=n.hooks=i.hooks||{};function cn(_,S,C){yl?ra.push([_,S,C]):_ in $a&&$a[_].forEach(D=>{D.call(null,n,S,C)})}(i.plugins||[]).forEach(_=>{for(let S in _.hooks)$a[S]=($a[S]||[]).concat(_.hooks[S])});const hh=(_,S,C)=>C,jt=Zt({key:null,setSeries:!1,filters:{pub:Yd,sub:Yd},scales:[A,x[1]?x[1].scale:null],match:[jd,jd,hh],values:[null,null]},ye.sync);jt.match.length==2&&jt.match.push(hh),ye.sync=jt;const dh=jt.key,Cl=Np(dh);function ca(_,S,C,D,B,Y,ae){jt.filters.pub(_,S,C,D,B,Y,ae)&&Cl.pub(_,S,C,D,B,Y,ae)}Cl.sub(n);function _m(_,S,C,D,B,Y,ae){jt.filters.sub(_,S,C,D,B,Y,ae)&&ar[_](null,S,C,D,B,Y,ae)}n.pub=_m;function xm(){Cl.unsub(n),fu.delete(n),We.clear(),lu(Jo,Br,uh),c.remove(),fe==null||fe.remove(),cn("destroy")}n.destroy=xm;function Rl(){cn("init",i,e),Je(e||i.data,!1),q[A]?bl(A,q[A]):Qe(),ie=Ot.show&&(Ot.width>0||Ot.height>0),re=se=!0,_e(i.width,i.height)}return x.forEach(ia),b.forEach(vl),t?t instanceof HTMLElement?(t.appendChild(c),Rl()):t(n,Rl):Rl(),n}dn.assign=Zt;dn.fmtNum=Fu;dn.rangeNum=Qo;dn.rangeLog=cl;dn.rangeAsinh=Nu;dn.orient=Ks;dn.pxRatio=St;dn.join=fM;dn.fmtDate=Bu,dn.tzDate=wM;dn.sync=Np;{dn.addGap=aw,dn.clipGaps=dl;let i=dn.paths={points:Hp};i.linear=Gp,i.stepped=cw,i.bars=uw,i.spline=dw}function vc(i){return Math.max(120,i.clientHeight-30)}const _f=[{id:"pareto",panelId:"plotter-pareto",hostId:"plotter-pareto-chart",title:"Pareto frontier",glyph:"◭",key:oc.pareto},{id:"ablation",panelId:"plotter-ablation",hostId:"plotter-ablation-chart",title:"Ablation",glyph:"▥",key:oc.ablation},{id:"variability",panelId:"plotter-variability",hostId:"plotter-variability-chart",title:"Variability",glyph:"◇",key:oc.variability}];function Mw(i){return`
    <div id="${i.hostId}" style="flex: 1; position: relative; overflow: hidden;"></div>
    <div class="chart-empty-state">
      <div class="empty-icon">${i.glyph}</div>
      <div style="font-size: 13px; font-weight: 600; color: var(--text-primary);">${i.title}</div>
      <div style="font-size: 11px; color: var(--text-secondary); max-width: 280px; line-height: 1.5;">${ww(i.id)}</div>
    </div>
    <div class="chart-toolbar">
      <span class="chart-status">No data</span>
    </div>
  `}function ww(i){switch(i){case"pareto":return"Shows validation accuracy vs. speed for each measured cell. Pareto frontier cells are not dominated on both axes.";case"ablation":return"Shows how each credit arm performs when other axes are held fixed. Error bars = ±1 std dev. Dashed line = chance level.";case"variability":return"Shows seed-to-seed spread per credit arm. Box = IQR, line = median, whiskers = 1.5×IQR, dots = outliers. Dashed line = chance level.";default:return"Select a run from the legend to populate this chart."}}class Ew{constructor(){R(this,"name","Plotter");R(this,"container",null);R(this,"chartPanels",new Map);R(this,"tooltip",null);R(this,"paretoPlot",null);R(this,"ablationPlot",null);R(this,"variabilityPlot",null);R(this,"records",[]);R(this,"ablationGroups",[]);R(this,"paretoFlags",[]);R(this,"chance",.1);R(this,"paretoRecordIndices",[]);R(this,"paretoXData",[]);R(this,"paretoYData",[]);R(this,"categoryLabels",[]);R(this,"ablationFixedAxes","");R(this,"onCampaignMetrics",e=>{const{data:t}=e;t!=null&&t.records&&Vn.observe(e==null?void 0:e.campaign_id,t)});R(this,"onRunChanged",(e,t)=>{t&&(this.records=t.records??[],this.paretoFlags=t.pareto??[],this.ablationGroups=t.ablation_groups??[],typeof t.chance=="number"&&(this.chance=t.chance),this.updatePlots(),this.updateStatus())});Yt.register("campaign_metrics",this.onCampaignMetrics),Vn.onChange(this.onRunChanged)}async init(){this.createUI(),console.log("[Plotter] Initialized")}async destroy(){var e,t,n,s;Yt.unregister("campaign_metrics",this.onCampaignMetrics),(e=this.paretoPlot)==null||e.destroy(),(t=this.ablationPlot)==null||t.destroy(),(n=this.variabilityPlot)==null||n.destroy(),(s=this.tooltip)==null||s.remove(),this.tooltip=null}createUI(){const e=document.getElementById("ui-overlay");if(!e)return;for(const n of _f){const s=vs({id:n.panelId,title:n.title,glyph:n.glyph,key:n.key,body:Mw(n),dock:"right",defaultOpen:n.id==="pareto",className:"chart-panel",onToggle:r=>{r&&this.initPlot(n.id)}});this.chartPanels.set(n.id,s),s.querySelector(".chart-download").addEventListener("click",()=>this.download(n.id)),s.querySelector(".chart-empty-hint"),js(n.panelId,n.title.toLowerCase(),n.glyph,()=>this.chartPanels.get(n.id)??null,n.key)}const t=this.chartPanels.get("pareto")??this.chartPanels.values().next().value;this.tooltip=document.createElement("div"),this.tooltip.id="plotter-tooltip",this.tooltip.style.cssText=`
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
    `,t?t.appendChild(this.tooltip):e.appendChild(this.tooltip)}showTab(e){var n;const t=_f.find(s=>s.id===e);t&&(Rt.toggle(t.panelId),(n=this.chartPanels.get(t.id))==null||n.scrollIntoView({block:"nearest"}))}initPlot(e){e==="pareto"&&!this.paretoPlot&&this.initParetoPlot(),e==="ablation"&&!this.ablationPlot&&this.initAblationPlot(),e==="variability"&&!this.variabilityPlot&&this.initVariabilityPlot(),this.updatePlots()}updateStatus(){const e=this.records.length>0,t=`${this.records.length} records | ${this.paretoFlags.filter(s=>s).length} Pareto`,n=this.ablationFixedAxes?` | fixed: ${this.ablationFixedAxes}`:"";for(const s of this.chartPanels.values()){const r=s.querySelector(".chart-status"),o=s.querySelector(".chart-empty-state"),a=s.querySelector(".chart-empty-hint");r&&(r.textContent=e?t+n:"No run selected",r.title=r.textContent),o&&(o.style.display=e?"none":"flex"),a&&(a.style.display=e?"none":"flex")}}updatePlots(){const e=this.records.length>0;for(const t of this.chartPanels.values()){const n=t.querySelector(".chart-empty-state"),s=t.querySelector(".chart-empty-hint");n&&(n.style.display=e?"none":"flex"),s&&(s.style.display=e?"none":"flex")}this.paretoPlot&&this.updateParetoPlot(),this.ablationPlot&&this.updateAblationPlot(),this.variabilityPlot&&this.updateVariabilityPlot()}initParetoPlot(){const e=document.getElementById("plotter-pareto-chart");if(!e)return;const t={width:e.clientWidth,height:vc(e),title:"Pareto Frontier: validation accuracy vs speed",axes:[{label:"1 / walltime_s   (faster →)",grid:{stroke:he.border}},{label:"accuracy",grid:{stroke:he.border},side:1}],scales:{x:{time:!1},y:{time:!1}},series:[{},{label:"val_acc",stroke:he.gradient,width:0,points:{show:!0,size:8,stroke:"white",width:1,fill:(n,s)=>{var a;const r=this.paretoRecordIndices[s],o=r===void 0?void 0:this.records[r];return o&&us[(a=o.coordinate)==null?void 0:a.credit]||he.gradient}}}],hooks:{draw:[n=>{const s=n.ctx;if(this.paretoFlags.some(o=>o)){const o=[];this.records.forEach((a,l)=>{this.paretoFlags[l]&&a.payload.walltime_s&&a.payload.val_acc&&o.push([1/a.payload.walltime_s,a.payload.val_acc])}),o.sort((a,l)=>a[0]-l[0]),o.length>1&&(s.beginPath(),s.strokeStyle=he.pareto,s.lineWidth=2,s.setLineDash([5,5]),o.forEach((a,l)=>{const c=n.valToPos(a[0],"x"),u=n.valToPos(a[1],"y");l===0?s.moveTo(c,u):s.lineTo(c,u)}),s.stroke(),s.setLineDash([])),o.forEach(a=>{const l=n.valToPos(a[0],"x"),c=n.valToPos(a[1],"y");s.beginPath(),s.arc(l,c,7,0,Math.PI*2),s.strokeStyle=he.pareto,s.lineWidth=1.5,s.stroke()})}const r=n.valToPos(this.chance,"y");s.strokeStyle=he.chance_line,s.lineWidth=1.5,s.setLineDash([4,4]),s.beginPath(),s.moveTo(n.bbox.left,r),s.lineTo(n.bbox.width,r),s.stroke(),s.setLineDash([])}],setCursor:[n=>{this.showScatterTooltip(n)}]},cursor:{show:!0,drag:{setScale:!0},focus:{prox:16}}};this.paretoPlot=new dn(t,[[],[]],e)}recordAt(e){const t=this.paretoRecordIndices[e];return t===void 0?void 0:this.records[t]}updateParetoPlot(){if(!this.paretoPlot||this.records.length===0)return;const e=[],t=[];this.paretoRecordIndices=[],this.records.forEach((r,o)=>{const a=r.payload.walltime_s,l=r.payload.val_acc;this.paretoRecordIndices.push(o),a&&l?(e.push(1/a),t.push(l)):(e.push(NaN),t.push(NaN))}),this.paretoPlot.setData([e,t]),this.paretoXData=e,this.paretoYData=t;const n=e.filter(Number.isFinite),s=t.filter(Number.isFinite);n.length>0&&this.fitScale(this.paretoPlot,"x",Math.min(...n),Math.max(...n)),s.length>0&&this.fitScale(this.paretoPlot,"y",Math.min(Math.min(...s),this.chance),Math.max(...s))}fitScale(e,t,n,s){if(!Number.isFinite(n)||!Number.isFinite(s))return;n===s&&(n-=.01,s+=.01);const r=(s-n)*.05;e.setScale(t,{min:n-r,max:s+r})}initAblationPlot(){const e=document.getElementById("plotter-ablation-chart");if(!e)return;const t={width:e.clientWidth,height:vc(e),title:"Ablation: credit arm → validation accuracy",axes:[{label:"credit arm",splits:()=>this.categoryIndices(),values:(n,s)=>s.map(r=>this.categoryLabels[r]??String(r)),grid:{stroke:he.border}},{label:"accuracy",grid:{stroke:he.border},side:1}],scales:{x:{time:!1},y:{time:!1}},series:[{},{label:"val_acc",width:0,points:{show:!1}}],hooks:{draw:[n=>{if(!this.ablationGroups.length)return;const s=n.ctx,r=this.ablationGroups.find(u=>u.axis==="credit");if(!r)return;const o=r.metrics.find(u=>u.metric==="val_acc");if(!o)return;const a=o.arms,l=n.bbox.width/(a.length*1.5);n.bbox.left,a.forEach((u,h)=>{const d=n.valToPos(h,"x"),f=n.valToPos(0,"y"),v=n.valToPos(u.mean,"y"),g=f-v;if(s.fillStyle=us[u.value]||he.gradient,s.fillRect(d-l/2,v,l,g),u.std>0){const m=n.valToPos(u.mean+u.std,"y");s.strokeStyle=he.text_muted,s.lineWidth=1,s.beginPath(),s.moveTo(d,m),s.lineTo(d,f),s.stroke(),s.moveTo(d-3,m),s.lineTo(d+3,m),s.stroke()}});const c=n.valToPos(this.chance,"y");s.strokeStyle=he.chance_line,s.lineWidth=2,s.setLineDash([5,5]),s.beginPath(),s.moveTo(n.bbox.left,c),s.lineTo(n.bbox.width,c),s.stroke(),s.setLineDash([])}],setCursor:[n=>{this.showCategoryTooltip(n,"ablation")}]},cursor:{show:!0,drag:{setScale:!0}}};this.ablationPlot=new dn(t,[[],[]],e)}updateAblationPlot(){if(!this.ablationPlot||!this.ablationGroups.length)return;const e=this.ablationGroups.find(a=>a.axis==="credit");if(!e)return;const t=e.metrics.find(a=>a.metric==="val_acc");if(!t)return;const n=t.arms.map((a,l)=>l),s=t.arms.map(a=>a.mean);this.categoryLabels=t.arms.map(a=>a.value),this.ablationFixedAxes=e.fixed_axes.split(",").map(a=>a.split("=").pop()??a).join(", "),this.ablationPlot.setData([n,s]),this.fitScale(this.ablationPlot,"x",-.5,Math.max(n.length-.5,.5));const r=t.arms.flatMap(a=>[a.mean-a.std,a.mean+a.std]);r.length>0&&this.fitScale(this.ablationPlot,"y",Math.min(Math.min(...r),this.chance),Math.max(...r));const o=this.ablationPlot.root.querySelector(".u-title");o&&(o.textContent=`Ablation: ${e.axis} vs val_acc`)}initVariabilityPlot(){const e=document.getElementById("plotter-variability-chart");if(!e)return;const t={width:e.clientWidth,height:vc(e),title:"Seed variability: validation accuracy per arm",axes:[{label:"credit arm",splits:()=>this.categoryIndices(),values:(n,s)=>s.map(r=>this.categoryLabels[r]??String(r)),grid:{stroke:he.border}},{label:"accuracy",grid:{stroke:he.border},side:1}],scales:{x:{time:!1},y:{time:!1}},series:[{},{label:"val_acc",width:0,points:{show:!1}}],hooks:{draw:[n=>{if(!this.records.length)return;const s=n.ctx,r={};this.records.forEach(c=>{const u=c.coordinate.credit,h=c.payload.val_acc;h!==void 0&&(r[u]||(r[u]=[])).push(h)});const o=Object.keys(r).sort(),a=n.bbox.width/(o.length*2);o.forEach((c,u)=>{const h=r[c].sort((y,P)=>y-P),d=h.length;if(d===0)return;const f=h[Math.floor(d*.25)],v=h[Math.floor(d*.5)],g=h[Math.floor(d*.75)],m=g-f,p=Math.max(h[0],f-1.5*m),x=Math.min(h[d-1],g+1.5*m),b=n.valToPos(u,"x"),w=n.valToPos(p,"y"),O=n.valToPos(f,"y"),A=n.valToPos(v,"y"),L=n.valToPos(g,"y"),k=n.valToPos(x,"y"),E=us[c]||he.gradient;s.strokeStyle=E,s.lineWidth=1.5,s.beginPath(),s.moveTo(b,w),s.lineTo(b,O),s.moveTo(b,L),s.lineTo(b,k),s.stroke(),s.fillStyle=E+"44",s.strokeStyle=E,s.lineWidth=1.5,s.fillRect(b-a/2,L,a,O-L),s.strokeRect(b-a/2,L,a,O-L),s.strokeStyle="white",s.lineWidth=2,s.beginPath(),s.moveTo(b-a/2,A),s.lineTo(b+a/2,A),s.stroke(),h.forEach(y=>{if(y<p||y>x){const P=n.valToPos(y,"y");s.fillStyle=E,s.beginPath(),s.arc(b,P,2,0,Math.PI*2),s.fill()}})});const l=n.valToPos(this.chance,"y");s.strokeStyle=he.chance_line,s.lineWidth=2,s.setLineDash([5,5]),s.beginPath(),s.moveTo(n.bbox.left,l),s.lineTo(n.bbox.width,l),s.stroke(),s.setLineDash([])}],setCursor:[n=>{this.showCategoryTooltip(n,"variability")}]},cursor:{show:!0,drag:{setScale:!0}}};this.variabilityPlot=new dn(t,[[],[]],e)}updateVariabilityPlot(){if(!this.variabilityPlot||!this.records.length)return;const e=Array.from(new Set(this.records.map(r=>r.coordinate.credit))).sort(),t=e.map((r,o)=>o),n=e.map(()=>0);this.categoryLabels=e,this.variabilityPlot.setData([t,n]),this.fitScale(this.variabilityPlot,"x",-.5,Math.max(e.length-.5,.5));const s=this.records.map(r=>r.payload.val_acc).filter(r=>typeof r=="number");s.length>0&&this.fitScale(this.variabilityPlot,"y",Math.min(Math.min(...s),this.chance),Math.max(...s))}categoryIndices(){return this.categoryLabels.map((e,t)=>t)}showTooltip(e,t){if(!this.tooltip)return;const n=e.cursor;if(!n||n.left==null||n.top==null){this.hideTooltip();return}const s=e.ctx.canvas.getBoundingClientRect(),r=this.chartPanels.get("pareto")??this.chartPanels.values().next().value,o=r==null?void 0:r.getBoundingClientRect();if(!o){this.hideTooltip();return}this.tooltip.innerHTML=t,this.tooltip.style.display="block",this.tooltip.style.left=`${s.left-o.left+e.bbox.left+n.left+14}px`,this.tooltip.style.top=`${s.top-o.top+e.bbox.top+n.top+14}px`}hideTooltip(){this.tooltip&&(this.tooltip.style.display="none")}showScatterTooltip(e){var d,f;const t=e.cursor;if(!t||t.left==null||t.top==null){this.hideTooltip();return}let n=-1,s=1/0;if(this.paretoXData.forEach((v,g)=>{const m=this.paretoYData[g];if(!Number.isFinite(v)||!Number.isFinite(m))return;const p=e.valToPos(v,"x"),x=e.valToPos(m,"y");if(!Number.isFinite(p)||!Number.isFinite(x))return;const b=(p-t.left)**2+(x-t.top)**2;b<s&&(s=b,n=g)}),n<0||s>400){this.hideTooltip();return}const r=this.recordAt(n);if(!r){this.hideTooltip();return}const o=this.paretoRecordIndices[n],a=((d=r.coordinate)==null?void 0:d.credit)??"?",l=r.payload.val_acc??0,c=r.payload.walltime_s??0,u=((f=r.schedule)==null?void 0:f.seed)??"?",h=this.paretoFlags[o]?" · PARETO":"";this.showTooltip(e,`${a} · val_acc ${l.toFixed(3)} · ${c.toFixed(1)}s · seed ${u}${h}`)}showCategoryTooltip(e,t){const n=e.cursor;if(!n||n.left==null||n.top==null){this.hideTooltip();return}const s=Math.round(e.posToVal(n.left,"x"));if(s<0||s>=this.categoryLabels.length){this.hideTooltip();return}const r=this.categoryLabels[s];if(t==="ablation"){const u=this.ablationGroups.find(f=>f.axis==="credit"),h=u==null?void 0:u.metrics.find(f=>f.metric==="val_acc"),d=h==null?void 0:h.arms[s];if(!d){this.hideTooltip();return}this.showTooltip(e,`${r} · ${d.mean.toFixed(3)} ± ${d.std.toFixed(3)} (n=${d.count})${d.at_chance?" · at chance":""}`);return}const o=this.records.filter(u=>u.coordinate.credit===r).map(u=>u.payload.val_acc).filter(u=>typeof u=="number").sort((u,h)=>u-h);if(o.length===0){this.hideTooltip();return}const a=o[Math.floor(o.length*.5)],l=o[Math.floor(o.length*.25)],c=o[Math.floor(o.length*.75)];this.showTooltip(e,`${r} · median ${a.toFixed(3)} · IQR ${(c-l).toFixed(3)} · n=${o.length}`)}download(e){const n={pareto:this.paretoPlot,ablation:this.ablationPlot,variability:this.variabilityPlot}[e];if(!n)return;const s=document.createElement("a");s.download=`computronium-${e}-${Date.now()}.png`,s.href=this.exportImage(n),s.click()}exportImage(e){const t=Array.from(e.root.querySelectorAll("canvas")),n=e.root.getBoundingClientRect(),s=Math.max(...t.map(l=>l.width),1),r=Math.max(...t.map(l=>l.height),1),o=document.createElement("canvas");o.width=s,o.height=r;const a=o.getContext("2d");return a?(a.fillStyle=he.bg,a.fillRect(0,0,s,r),t.forEach(l=>{const c=l.getBoundingClientRect();if(c.width===0||c.height===0)return;const u=l.width/c.width;a.drawImage(l,(c.left-n.left)*u,(c.top-n.top)*u,l.width,l.height)}),o.toDataURL("image/png")):e.ctx.canvas.toDataURL("image/png")}}const Ia=new Ew;qn.register(Ia);function Tw(){return`
    <div id="rail-header" class="rail-header-inner">
      <span class="rail-connection" id="rail-connection">
        <span class="dot"></span>
        <span class="rail-label">Disconnected</span>
      </span>
      <div style="flex: 1;"></div>
      <span id="rail-queue" class="rail-queue">0 running · 0 queued</span>
      <span id="rail-count" class="rail-count">0 events</span>
    </div>
    <div id="rail-log"></div>
    <!-- Scroll hint -->
    <div id="rail-scroll-hint"></div>
  `}class Aw{constructor(){R(this,"name","LiveRail");R(this,"container",null);R(this,"logContainer",null);R(this,"scrollHint",null);R(this,"events",[]);R(this,"maxEvents",50);R(this,"onPipelineEvent",e=>{this.events.unshift(e),this.events.length>this.maxEvents&&this.events.pop(),this.render()});R(this,"onStatusUpdate",e=>{var r,o,a;const t=((r=e==null?void 0:e.data)==null?void 0:r.running_campaigns)??0,n=((o=e==null?void 0:e.data)==null?void 0:o.queued_campaigns)??0,s=(a=this.container)==null?void 0:a.querySelector("#rail-queue");s&&(s.textContent=`${t} running · ${n} queued`)});Yt.register("pipeline_event",this.onPipelineEvent),Yt.register("status_update",this.onStatusUpdate)}async init(){this.container=vs({id:"live-rail",title:"LIVE RAIL",glyph:"≡",key:qs.rail,body:Tw(),dock:"bottom",defaultOpen:!0,className:"live-rail-panel"}),this.logContainer=this.container.querySelector("#rail-log"),this.scrollHint=this.container.querySelector("#rail-scroll-hint"),js("live-rail","live rail","≡",()=>this.container,qs.rail),fs.onStateChange(e=>this.setConnected(e==="connected")),console.log("[LiveRail] Initialized")}async destroy(){var e;Yt.unregister("pipeline_event",this.onPipelineEvent),Yt.unregister("status_update",this.onStatusUpdate),(e=this.container)==null||e.remove()}setConnected(e){var o;const t=(o=this.container)==null?void 0:o.querySelector("#rail-connection");if(!t)return;const n=t.querySelector(".dot"),s=t.querySelector(".rail-label");if(!n||!s)return;const r=e?he.ok:he.error;n.style.background=r,t.style.background=r+"22",t.style.borderColor=r+"88",t.style.color=r,s.textContent=e?"Connected":"Disconnected"}render(){var t;if(!this.logContainer)return;this.logContainer.innerHTML=this.events.map((n,s)=>{const r=new Date(n.timestamp).toLocaleTimeString(),a={ok:he.ok,warn:he.warn,error:he.error}[n.level]||he.text_secondary;return`
          <span class="rail-event ${s===0?"latest":""}">
            <span class="rail-time">${r}</span>
            <span class="rail-icon" style="color: ${a};">${{ok:"✓",warn:"⚠",error:"✗"}[n.level]??"•"}</span>
            <span class="rail-stage">${n.stage}</span>
            <span class="rail-message">${n.message}</span>
          </span>
        `}).join("");const e=(t=this.container)==null?void 0:t.querySelector("#rail-count");if(e&&(e.textContent=`${this.events.length} events`),this.logContainer.scrollLeft=0,this.scrollHint){const n=this.logContainer.scrollWidth>this.logContainer.clientWidth;this.scrollHint.style.opacity=n?"1":"0"}}}const $p=new Aw;qn.register($p);const Cw=4e3,Rw={ok:he.text_primary,warn:he.warn,error:he.error};function Pw(){return`
    <div id="caption-headline">The dashboard is starting.</div>
    <div id="caption-context"></div>
  `}class Lw{constructor(){R(this,"name","Caption");R(this,"container",null);R(this,"headline",null);R(this,"context",null);R(this,"state",[]);R(this,"spoken",null);R(this,"last",null);R(this,"holdTimer",null);R(this,"onNarration",e=>{this.state=(e==null?void 0:e.state)??[],this.render()});R(this,"onEvent",e=>{e!=null&&e.sentence&&this.say(e.sentence,e.level??"ok")});Yt.register("narration",this.onNarration),Yt.register("pipeline_event",this.onEvent)}async init(){this.container=vs({id:"caption",title:"Caption",glyph:"▤",key:qs.caption,body:Pw(),dock:"bottom",defaultOpen:!0,className:"caption-panel"}),this.headline=this.container.querySelector("#caption-headline"),this.context=this.container.querySelector("#caption-context"),js("caption","caption","▤",()=>this.container,qs.caption),this.render()}async destroy(){var e;Yt.unregister("narration",this.onNarration),Yt.unregister("pipeline_event",this.onEvent),this.holdTimer!==null&&window.clearTimeout(this.holdTimer),(e=this.container)==null||e.remove()}say(e,t="ok"){e&&(this.spoken={text:e,level:t},this.last={text:e,level:t},this.render(),this.holdTimer!==null&&window.clearTimeout(this.holdTimer),this.holdTimer=window.setTimeout(()=>{this.spoken=null,this.holdTimer=null,this.render()},Cw))}render(){if(!(!this.headline||!this.context)){if(this.spoken){this.headline.textContent=this.spoken.text,this.headline.style.color=this.colorOf(this.spoken.level),this.context.textContent=this.state.join(" · ");return}if(this.state.length>0){this.headline.textContent=this.state[0],this.headline.style.color=he.text_primary,this.context.textContent=this.state.slice(1).join(" · ");return}if(this.last){this.headline.textContent=this.last.text,this.headline.style.color=this.colorOf(this.last.level),this.context.textContent="";return}this.headline.textContent="The dashboard is starting.",this.headline.style.color=he.text_primary,this.context.textContent=""}}colorOf(e){return Rw[e]??he.text_primary}}const Yp=new Lw;qn.register(Yp);function Dw(){return`
    <div id="hud-meters"></div>
    <div class="hud-source-row">
      <div class="meter-label-row">
        <span class="meter-label">PICTURE</span>
        <span id="hud-source" class="meter-value hud-source-value">—</span>
      </div>
      <div id="hud-claim-row">
        <div class="meter-label-row">
          <span class="meter-label">SEEDS TO CLAIM</span>
          <span id="hud-claim" class="meter-value hud-claim-value">—</span>
        </div>
        <div class="meter-bar"><div id="hud-claim-fill" class="meter-fill hud-claim-fill"></div></div>
      </div>
    </div>
  `}class Iw{constructor(){R(this,"name","HUD");R(this,"panel",null);R(this,"modeChip",null);R(this,"connectionPill",null);R(this,"rows",new Map);R(this,"rowElements",new Map);R(this,"claimValue",null);R(this,"claimFill",null);R(this,"sourceValue",null);R(this,"statusData",{});R(this,"resources",{});R(this,"requiredSeeds",0);R(this,"measuredSeeds",0);R(this,"connected",!1);R(this,"animationTime",0);R(this,"onStatusUpdate",e=>{const t=(e==null?void 0:e.data)??e;t&&(this.statusData=t,this.updateQueueRows())});R(this,"onCampaignMetrics",e=>{const t=e==null?void 0:e.data;t&&Vn.observe(e==null?void 0:e.campaign_id,t)});R(this,"onRunChanged",(e,t)=>{var n;t&&(this.resources=t.resources??{},typeof t.required_seeds=="number"&&(this.requiredSeeds=t.required_seeds),this.measuredSeeds=this.resources.seeds_per_arm??((n=t.records)==null?void 0:n.length)??0,this.updateModeChip(t.run),this.updateSource(t.store),this.updateResourceRows(),this.updateClaim())});Yt.register("status_update",this.onStatusUpdate),Yt.register("campaign_metrics",this.onCampaignMetrics),Vn.onChange(this.onRunChanged)}async init(){this.panel=vs({id:"hud",title:"MISSION CONTROL",glyph:"◱",key:qs.hud,body:Dw(),dock:"top",defaultOpen:!0}),this.createModeChip(),this.setupMeters(),js("hud","mission control","◱",()=>this.panel,qs.hud),fs.onStateChange(e=>{this.connected=e==="connected",this.updateConnection()}),console.log("[HUD] Initialized")}async destroy(){var e,t;Yt.unregister("status_update",this.onStatusUpdate),Yt.unregister("campaign_metrics",this.onCampaignMetrics),(e=this.panel)==null||e.remove(),(t=this.modeChip)==null||t.remove()}setupMeters(){if(!this.panel)return;const e=this.panel.querySelector("#hud-meters");this.addMeter(e,"device","DEVICE","var(--gradient)"),this.addMeter(e,"memory","MEMORY","var(--memory)"),this.addMeter(e,"walltime","WALLTIME","var(--cpu)"),this.addMeter(e,"gpu","GPU","var(--gpu)"),this.addMeter(e,"cpu","CPU","var(--cpu)"),this.addMeter(e,"records","RECORDS","var(--promoted)"),this.claimValue=this.panel.querySelector("#hud-claim"),this.claimFill=this.panel.querySelector("#hud-claim-fill"),this.connectionPill=this.panel.querySelector("#hud-connection"),this.sourceValue=this.panel.querySelector("#hud-source")}addMeter(e,t,n,s){const r=document.createElement("div");r.className="meter-row",r.innerHTML=`
      <div class="meter-label-row">
        <span class="meter-label">${n}</span>
        <span class="meter-value hud-value">—</span>
      </div>
      <div class="meter-bar"><div class="meter-fill hud-fill" style="background: ${s};"></div></div>
    `,e.appendChild(r),this.rows.set(t,{key:t,label:n,value:"",fraction:0,color:s}),this.rowElements.set(t,{fill:r.querySelector(".hud-fill"),value:r.querySelector(".hud-value")})}createModeChip(){const e=document.getElementById("ui-overlay");e&&(this.modeChip=document.createElement("div"),this.modeChip.id="mode-chip",this.modeChip.className="mode-chip",this.modeChip.innerHTML=`
      <div class="mode-label">NO RUN</div>
      <div class="mode-detail"></div>
    `,e.appendChild(this.modeChip))}updateModeChip(e){if(!this.modeChip)return;const t=(e==null?void 0:e.mode)??"NO RUN",n=t==="PREREGISTERED"?he.passed:t==="EXPLORATORY"?he.insufficient:he.text_muted;this.modeChip.style.background=`${n}22`,this.modeChip.style.borderColor=`${n}88`,this.modeChip.style.color=n;const s=this.modeChip.querySelector(".mode-label");s&&(s.textContent=t);const r=this.modeChip.querySelector(".mode-detail");r&&(r.textContent=[e==null?void 0:e.profile,((e==null?void 0:e.tasks)??[]).join(", "),e==null?void 0:e.fidelity].filter(Boolean).join(" · ")),this.modeChip.title=e?`run ${e.run_id??"?"} · objectives: ${(e.objectives??[]).join(", ")||"none"}`:"No run has reported yet"}setMeter(e,t,n){const s=this.rows.get(e),r=this.rowElements.get(e);!s||!r||(s.value=t,s.fraction=Math.max(0,Math.min(1,n)),r.value.textContent=t,r.fill.style.width=`${(s.fraction*100).toFixed(1)}%`)}updateSource(e){if(!this.sourceValue)return;const t=e==null?void 0:e.source;if(!t){this.sourceValue.textContent="—",this.sourceValue.style.color="var(--text-secondary)";return}if(t==="snapshot"){const n=e!=null&&e.published_at?new Date(e.published_at).toLocaleTimeString():"";this.sourceValue.textContent=n?`snapshot ${n}`:"snapshot",this.sourceValue.style.color="var(--insufficient)",this.sourceValue.title="The writer published this copy; it is as fresh as its last publish.";return}this.sourceValue.textContent="live",this.sourceValue.style.color="var(--passed)",this.sourceValue.title="The store itself, read as it is written."}updateQueueRows(){const e=this.statusData;this.setMeter("gpu",e.max_gpus?`${e.used_gpus??0} / ${e.max_gpus}`:"—",e.max_gpus?(e.used_gpus??0)/e.max_gpus:0),this.setMeter("cpu",e.max_cpus?`${e.used_cpus??0} / ${e.max_cpus}`:"—",e.max_cpus?(e.used_cpus??0)/e.max_cpus:0)}updateResourceRows(){const e=this.resources;this.setMeter("device",e.device??"—",e.device?1:0),this.setMeter("memory",e.memory_mb!==void 0?`${e.memory_mb.toFixed(1)} MB`:"—",e.memory_mb!==void 0?Math.min(1,e.memory_mb/2048):0),this.setMeter("walltime",e.walltime_s!==void 0?`${e.walltime_s.toFixed(1)} s`:"—",e.walltime_s!==void 0?Math.min(1,e.walltime_s/120):0),this.setMeter("records",e.records!==void 0?`${e.records}`:"—",e.records!==void 0?Math.min(1,e.records/20):0)}updateClaim(){if(!this.claimValue||!this.claimFill)return;if(this.requiredSeeds<=0){this.claimValue.textContent="—",this.claimFill.style.width="0%";return}const e=Math.max(0,this.requiredSeeds-this.measuredSeeds),t=this.requiredSeeds>0?this.measuredSeeds/this.requiredSeeds:0;this.claimValue.textContent=e>0?`${e} more (${this.requiredSeeds} needed)`:`Ready (${this.requiredSeeds} met)`,this.claimValue.style.color=e>0?"var(--insufficient)":"var(--passed)",this.claimFill.style.width=`${Math.min(100,t*100)}%`,this.claimFill.style.background=e>0?"var(--insufficient)":"var(--passed)"}updateConnection(){if(!this.connectionPill)return;const e=this.connectionPill.querySelector(".dot"),t=this.connectionPill.querySelector("span:last-child"),n=this.connected?"var(--ok)":"var(--error)";e.style.background=n,this.connectionPill.style.background=`${n}22`,this.connectionPill.style.borderColor=`${n}88`,this.connectionPill.style.color=n,t.textContent=this.connected?"live":"offline"}update(e){var n;this.animationTime+=e;const t=.5+.5*Math.sin(this.animationTime*2);(n=this.connectionPill)==null||n.style.setProperty("opacity",`${.75+.25*t}`)}}const Xu=new Iw;qn.register(Xu);function Uw(){const i=np(),e=new Map;for(const n of i){const s=n.chord?n.chord.replace("shift+","Shift + ").toUpperCase():n.key?n.key.toUpperCase():"";if(!s)continue;const r=n.group;e.has(r)||e.set(r,[]),e.get(r).push({key:s,description:n.label})}return["Navigation","Panels","Charts","Run Control","Cell Actions","Stage","General"].map(n=>({title:n,items:e.get(n)??[]})).filter(n=>n.items.length>0)}const Nw=Uw();class Ow{constructor(){R(this,"name","HelpOverlay");R(this,"container",null);R(this,"dialog",null);R(this,"isOpen",!1);R(this,"lastFocused",null);R(this,"onKeyDown",e=>{const t=e.target;t&&["INPUT","SELECT","TEXTAREA"].includes(t.tagName)||(e.key==="?"&&!e.shiftKey&&!e.ctrlKey&&!e.metaKey&&!e.altKey&&(e.preventDefault(),this.toggle()),e.key==="Escape"&&this.isOpen&&this.hide())});window.addEventListener("keydown",this.onKeyDown)}async init(){this.createOverlay(),js("help-overlay","help","?",()=>this.container),console.log("[HelpOverlay] Initialized")}async destroy(){var e;window.removeEventListener("keydown",this.onKeyDown),(e=this.container)==null||e.remove()}createOverlay(){if(!document.getElementById("ui-overlay"))return;this.container=document.createElement("div"),this.container.id="help-overlay",this.container.setAttribute("role","dialog"),this.container.setAttribute("aria-modal","true"),this.container.setAttribute("aria-labelledby","help-title"),this.container.style.cssText=`
      position: fixed;
      inset: 0;
      background: rgba(10, 14, 20, 0.92);
      z-index: 1000;
      display: none;
      align-items: center;
      justify-content: center;
      opacity: 0;
      transition: opacity 0.2s ease;
    `;const t=Nw.map(n=>`
      <div style="margin-bottom: 24px;">
        <div style="font-size: 11px; font-weight: 600; letter-spacing: 0.08em; color: var(--text-secondary); margin-bottom: 12px; text-transform: uppercase;">${n.title}</div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 8px;">
          ${n.items.map(s=>`
            <div style="display: flex; align-items: center; gap: 12px; padding: 8px 12px; background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: 6px;">
              <kbd style="
                font-family: 'JetBrains Mono', monospace;
                font-size: 11px;
                padding: 2px 8px;
                background: var(--bg);
                border: 1px solid var(--border-bright);
                border-radius: 4px;
                color: var(--text-primary);
                min-width: 48px;
                text-align: center;
                box-shadow: 0 1px 2px rgba(0,0,0,0.3);
              ">${s.key}</kbd>
              <span style="font-size: 12px; color: var(--text-primary);">${s.description}</span>
            </div>
          `).join("")}
        </div>
      </div>
    `).join("");this.container.innerHTML=`
      <div style="
        width: 90%;
        max-width: 800px;
        max-height: 85vh;
        overflow-y: auto;
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 32px;
        box-shadow: 0 24px 64px rgba(0,0,0,0.6);
        transform: scale(0.95);
        transition: transform 0.2s ease;
      ">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid var(--border);">
          <h2 id="help-title" style="margin: 0; font-size: 18px; font-weight: 600; letter-spacing: 0.02em;">Keyboard Shortcuts</h2>
          <span style="font-size: 11px; color: var(--text-muted);">Press <kbd style="font-family: 'JetBrains Mono', monospace; padding: 1px 6px; background: var(--bg); border: 1px solid var(--border); border-radius: 3px;">?</kbd> again or <kbd style="font-family: 'JetBrains Mono', monospace; padding: 1px 6px; background: var(--bg); border: 1px solid var(--border); border-radius: 3px;">Esc</kbd> to close</span>
        </div>
        ${t}
      </div>
    `,this.dialog=this.container.querySelector("div"),this.container.addEventListener("click",n=>{n.target===this.container&&this.hide()})}toggle(){this.isOpen?this.hide():this.show()}show(){!this.container||!this.dialog||(this.lastFocused=document.activeElement,this.container.style.display="flex",this.trapFocus(),requestAnimationFrame(()=>{this.container.style.opacity="1",this.dialog&&(this.dialog.style.transform="scale(1)")}),this.isOpen=!0,document.body.style.overflow="hidden")}hide(){!this.container||!this.dialog||(this.container.style.opacity="0",this.dialog.style.transform="scale(0.95)",setTimeout(()=>{this.container&&(this.container.style.display="none")},200),this.isOpen=!1,document.body.style.overflow="",this.lastFocused&&this.lastFocused.focus())}trapFocus(){var o;if(!this.dialog)return;const e=this.dialog.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');if(e.length===0)return;const t=e[0],n=e[e.length-1],s=a=>{a.key==="Tab"&&(a.shiftKey?document.activeElement===t&&(a.preventDefault(),n.focus()):document.activeElement===n&&(a.preventDefault(),t.focus()))};this.dialog.addEventListener("keydown",s);const r=()=>{var a;(a=this.dialog)==null||a.removeEventListener("keydown",s)};(o=this.container)==null||o.addEventListener("transitionend",r,{once:!0}),t.focus()}}const tl=new Ow;qn.register(tl);const xf=["the next question","workspaces","views","panels","verbs","general"];class Fw{constructor(){R(this,"container",null);R(this,"input",null);R(this,"list",null);R(this,"entries",[]);R(this,"filtered",[]);R(this,"selectedIndex",0);R(this,"isOpen",!1);R(this,"previousFocus",null);R(this,"focusTrapCleanup",null);R(this,"unsubscribeLayout",null);R(this,"unsubscribePanels",null);R(this,"unsubscribeCellDrawer",null);R(this,"onGlobalKeyDown",e=>{e.shiftKey&&e.key===";"&&(e.preventDefault(),this.open())});R(this,"onInputKeyDown",e=>{switch(e.key){case"ArrowDown":e.preventDefault(),this.selectedIndex=Math.min(this.selectedIndex+1,this.filtered.length-1),this.render();break;case"ArrowUp":e.preventDefault(),this.selectedIndex=Math.max(this.selectedIndex-1,0),this.render();break;case"Enter":e.preventDefault();const t=this.filtered[this.selectedIndex];t!=null&&t.enabled&&t.run();break;case"Escape":e.preventDefault(),this.close();break}})}async init(){var e;this.buildContainer(),document.body.appendChild(this.container),this.unsubscribeLayout=zs().onChange(()=>this.rebuildEntries()),this.unsubscribePanels=Rt.onChange(()=>this.rebuildEntries()),this.unsubscribeCellDrawer=(e=Un.onChange)==null?void 0:e.call(Un,()=>this.rebuildEntries()),this.rebuildEntries(),document.addEventListener("keydown",this.onGlobalKeyDown),console.log("[CommandPalette] Initialized")}buildContainer(){this.container=document.createElement("div"),this.container.id="command-palette",this.container.className="command-palette",this.container.setAttribute("role","dialog"),this.container.setAttribute("aria-modal","true"),this.container.setAttribute("aria-label","Command palette"),this.container.style.cssText=`
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      z-index: 10000;
      display: none;
      align-items: flex-start;
      justify-content: center;
      padding-top: 12vh;
      pointer-events: none;
    `,this.container.innerHTML=`
      <div class="palette-backdrop" style="
        position: absolute;
        inset: 0;
        background: rgba(0,0,0,0.6);
        backdrop-filter: blur(4px);
      "></div>
      <div class="palette-window" style="
        position: relative;
        width: min(720px, 90vw);
        max-height: 70vh;
        background: var(--bg-secondary);
        border: 1px solid var(--border-bright);
        border-radius: 12px;
        box-shadow: 0 24px 48px rgba(0,0,0,0.6), 0 0 0 1px var(--border);
        overflow: hidden;
        display: flex;
        flex-direction: column;
        pointer-events: auto;
      ">
        <div class="palette-header" style="
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 12px 16px;
          border-bottom: 1px solid var(--border);
          background: var(--bg-tertiary);
        ">
          <kbd class="palette-trigger-hint" style="
            font-size: 11px;
            padding: 2px 6px;
            background: var(--bg);
            border: 1px solid var(--border);
            border-radius: 4px;
            color: var(--text-muted);
            font-family: 'JetBrains Mono', monospace;
          ">⇧;</kbd>
          <input
            class="palette-input"
            type="text"
            placeholder="Type a command…"
            autocomplete="off"
            spellcheck="false"
            style="
              flex: 1;
              background: var(--bg);
              border: 1px solid var(--border);
              border-radius: 6px;
              padding: 8px 12px;
              font-size: 14px;
              color: var(--text-primary);
              font-family: inherit;
              outline: none;
            "
            aria-label="Search commands"
          />
          <kbd class="palette-close-hint" style="
            font-size: 11px;
            padding: 2px 6px;
            background: var(--bg);
            border: 1px solid var(--border);
            border-radius: 4px;
            color: var(--text-muted);
            font-family: 'JetBrains Mono', monospace;
          ">Esc</kbd>
        </div>
        <div class="palette-list" style="
          flex: 1;
          overflow-y: auto;
          padding: 8px;
        "></div>
        <div class="palette-footer" style="
          padding: 8px 16px;
          border-top: 1px solid var(--border);
          background: var(--bg-tertiary);
          font-size: 11px;
          color: var(--text-muted);
          display: flex;
          justify-content: space-between;
        ">
          <span class="palette-count"></span>
          <span>↑↓ navigate · ⏎ run · Esc close</span>
        </div>
      </div>
    `,this.input=this.container.querySelector(".palette-input"),this.list=this.container.querySelector(".palette-list"),this.input.addEventListener("input",()=>this.filter()),this.input.addEventListener("keydown",this.onInputKeyDown),this.container.querySelector(".palette-backdrop").addEventListener("click",()=>this.close())}rebuildEntries(){const e=[];let t=0;const n=fs.isConnected,s=Un.hasCellSelected();e.push({id:"start-run",label:n?"Start a new run":"Start a run",group:"the next question",hint:"z",enabled:!0,sortOrder:t++,run:()=>{this.close(),Zo.showSection("new-run"),Rt.toggle("control-panel")}}),e.push({id:"replicate-cell",label:"Replicate selected cell",group:"the next question",hint:"⇧R",enabled:s,disabledReason:s?void 0:"No cell selected — click a cell on the map",sortOrder:t++,run:()=>{this.close(),Un.replicateSelected()}}),e.push({id:"preregister-claim",label:"Preregister claim",group:"the next question",hint:"⇧P",enabled:s,disabledReason:s?void 0:"No cell selected — click a cell on the map",sortOrder:t++,run:()=>{this.close(),Un.preregisterSelected()}}),e.push({id:"adopt-quest",label:"Adopt as quest (new run)",group:"the next question",hint:"⇧Q",enabled:s,disabledReason:s?void 0:"No cell selected — click a cell on the map",sortOrder:t++,run:()=>{this.close(),Un.adoptQuestSelected()}}),e.push({id:"show-queue",label:"Show run queue",group:"the next question",hint:"z → Queue",enabled:!0,sortOrder:t++,run:()=>{this.close(),Zo.showSection("queue"),Rt.toggle("control-panel")}});const r=zs().getCurrentWorkspace();for(const[a,l,c]of[["watch","Watch — campaigns in real time",""],["audit","Audit — evidence and judgement",""],["drive","Drive — the instrument",""],["free","Free — your arrangement",""],["reset","Reset to Watch workspace","↺"]]){const u=a==="reset",h=!u&&r===a;e.push({id:`workspace-${a}`,label:l,group:"workspaces",hint:c,enabled:u||!h,disabledReason:h?"Already active":void 0,sortOrder:t++,run:()=>{this.close(),u?zs().reset():zs().applyWorkspace(a)}})}const o=Xs.getViews();for(const a of o){const l=Ti.find(c=>c.id===`view-${a.id}`);e.push({id:`view-${a.id}`,label:a.name,group:"views",hint:(l==null?void 0:l.key)??(l==null?void 0:l.chord)??"",enabled:!0,sortOrder:t++,run:()=>{this.close(),Xs.show(a.id)}})}for(const a of Rt.list()){const l=Ti.find(c=>c.id===`panel-${a.id.replace("panel-","")}`);e.push({id:`panel-${a.id}`,label:a.label,group:"panels",hint:(l==null?void 0:l.key)??"",enabled:!0,sortOrder:t++,run:()=>{this.close(),Rt.toggle(a.id)}})}for(const a of Ti)(a.group==="Run Control"||a.group==="General")&&e.push({id:a.id,label:a.label,group:a.group==="Run Control"?"verbs":"general",hint:a.key?a.key===" "?"Space":a.key:a.chord??"",enabled:a.when?this.checkWhen(a.when):!0,disabledReason:a.when&&!this.checkWhen(a.when)?this.whenReason(a.when):void 0,sortOrder:t++,run:()=>{this.close(),a.run()}});this.entries=e.sort((a,l)=>{const c=xf.indexOf(a.group),u=xf.indexOf(l.group);return c!==u?c-u:(a.sortOrder??0)-(l.sortOrder??0)}),this.isOpen&&this.filter()}checkWhen(e){switch(e){case"always":return!0;case"cell-selected":return Un.hasCellSelected();case"run-active":return fs.isConnected;default:return!0}}whenReason(e){switch(e){case"always":return"";case"cell-selected":return"No cell selected — click a cell on the map";case"run-active":return"No active run";default:return""}}filter(){const e=this.input.value.toLowerCase().trim();e?this.filtered=this.entries.map(t=>({entry:t,score:this.fuzzyScore(t.label.toLowerCase(),e)})).filter(t=>t.score>0).sort((t,n)=>n.score-t.score).map(t=>t.entry):this.filtered=[...this.entries],this.selectedIndex=0,this.render()}fuzzyScore(e,t){if(e===t)return 1e3;if(e.startsWith(t))return 800;if(e.includes(t))return 600;let n=0,s=0,r=0;for(;n<e.length&&s<t.length;)e[n]===t[s]&&(r+=10,s++),n++;return s===t.length?r+100:0}render(){if(!this.list)return;if(this.list.innerHTML="",this.filtered.length===0){const n=document.createElement("div");n.className="palette-empty",n.style.cssText=`
        padding: 24px;
        text-align: center;
        color: var(--text-muted);
        font-size: 13px;
      `,n.textContent=this.input.value?"No matches":"No commands available",this.list.appendChild(n),this.updateCount(0);return}let e="";for(let n=0;n<this.filtered.length;n++){const s=this.filtered[n];if(s.group!==e){e=s.group;const o=document.createElement("div");o.className="palette-group-header",o.style.cssText=`
          padding: 8px 12px 4px;
          font-size: 10px;
          text-transform: uppercase;
          letter-spacing: 0.08em;
          color: var(--text-muted);
          font-weight: 600;
        `,o.textContent=s.group,this.list.appendChild(o)}const r=document.createElement("div");r.className="palette-item"+(s.enabled?"":" palette-item-disabled")+(n===this.selectedIndex?" palette-item-selected":""),r.style.cssText=`
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 8px 12px;
        border-radius: 6px;
        cursor: ${s.enabled?"pointer":"not-allowed"};
        transition: background var(--motion-fast);
        ${s.enabled?"":"opacity: 0.5;"}
      `,r.dataset.id=s.id,n===this.selectedIndex&&(r.style.background="var(--gradient)1a"),r.innerHTML=`
        <span class="palette-item-label" style="flex: 1; min-width: 0; font-size: 13px; color: var(--text-primary);">${this.highlightMatch(s.label)}</span>
        ${s.hint?`<kbd class="palette-item-hint" style="
          font-size: 10px;
          padding: 2px 6px;
          background: var(--bg);
          border: 1px solid var(--border);
          border-radius: 4px;
          color: var(--text-secondary);
          font-family: 'JetBrains Mono', monospace;
          white-space: nowrap;
          flex-shrink: 0;
        ">${this.escapeHtml(s.hint)}</kbd>`:""}
        ${s.disabledReason?`<span class="palette-item-reason" style="
          font-size: 11px;
          color: var(--text-muted);
          flex-shrink: 0;
        ">${this.escapeHtml(s.disabledReason)}</span>`:""}
      `,s.enabled&&(r.addEventListener("click",()=>{this.selectedIndex=n,s.run()}),r.addEventListener("mouseenter",()=>this.selectedIndex=n)),this.list.appendChild(r)}const t=this.list.querySelector(".palette-item-selected");t==null||t.scrollIntoView({block:"nearest"}),this.updateCount(this.filtered.length)}highlightMatch(e){const t=this.input.value.toLowerCase().trim();if(!t)return this.escapeHtml(e);const s=e.toLowerCase().indexOf(t);if(s===-1)return this.escapeHtml(e);const r=e.slice(0,s),o=e.slice(s,s+t.length),a=e.slice(s+t.length);return`${this.escapeHtml(r)}<mark style="background: var(--gradient)33; color: var(--gradient); padding: 0 2px; border-radius: 2px;">${this.escapeHtml(o)}</mark>${this.escapeHtml(a)}`}escapeHtml(e){return e.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&#39;")}updateCount(e){const t=this.container.querySelector(".palette-count");t&&(t.textContent=`${e} command${e===1?"":"s"}`)}open(){this.isOpen||(this.previousFocus=document.activeElement,this.isOpen=!0,this.container.style.display="flex",this.rebuildEntries(),this.filter(),requestAnimationFrame(()=>{this.input.focus(),this.setupFocusTrap()}),this.announce("Command palette opened"))}close(){this.isOpen&&(this.isOpen=!1,this.container.style.display="none",this.input.value="",this.teardownFocusTrap(),this.previousFocus&&(this.previousFocus.focus(),this.previousFocus=null),this.announce("Command palette closed"))}setupFocusTrap(){const e=this.container.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"]), .palette-item:not(.palette-item-disabled)'),t=e[0],n=e[e.length-1],s=r=>{r.key==="Tab"&&(r.shiftKey?document.activeElement===t&&(r.preventDefault(),n==null||n.focus()):document.activeElement===n&&(r.preventDefault(),t==null||t.focus()))};this.container.addEventListener("keydown",s),this.focusTrapCleanup=()=>this.container.removeEventListener("keydown",s)}teardownFocusTrap(){var e;(e=this.focusTrapCleanup)==null||e.call(this),this.focusTrapCleanup=null}announce(e){const t=document.createElement("div");t.setAttribute("role","status"),t.setAttribute("aria-live","polite"),t.style.cssText="position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; border: 0;",t.textContent=e,document.body.appendChild(t),setTimeout(()=>t.remove(),1e3)}isOpenState(){return this.isOpen}destroy(){var e,t,n,s;document.removeEventListener("keydown",this.onGlobalKeyDown),(e=this.unsubscribeLayout)==null||e.call(this),(t=this.unsubscribePanels)==null||t.call(this),(n=this.unsubscribeCellDrawer)==null||n.call(this),(s=this.container)==null||s.remove()}}const jp=new Fw;async function kw(){await jp.init()}const Bw=/swiftshader|llvmpipe|software|basic render/i;function zw(){const i=Hw();return{software:i,fps:i?12:60,shadows:!i,antialias:!i}}function Hw(){try{const i=document.createElement("canvas"),e=i.getContext("webgl2")??i.getContext("webgl");if(!e)return!0;const t=e.getExtension("WEBGL_debug_renderer_info"),n=String(t?e.getParameter(t.UNMASKED_RENDERER_WEBGL):e.getParameter(e.RENDERER));return Bw.test(n)}catch{return!0}}window.addEventListener("error",i=>{var e;console.error("[Global Error]",i.error),Zp(((e=i.error)==null?void 0:e.message)||"Unknown error")});window.addEventListener("unhandledrejection",i=>{var e;console.error("[Unhandled Rejection]",i.reason),Zp(((e=i.reason)==null?void 0:e.message)||"Unhandled promise rejection")});let zi=null;function Kp(i="Initializing dashboard..."){const e=document.getElementById("ui-overlay");e&&(zi=document.createElement("div"),zi.id="global-loading",zi.className="global-loading",zi.innerHTML=`
    <div class="global-loading-spinner"></div>
    <div class="global-loading-text">${i}</div>
  `,e.appendChild(zi))}function yf(){zi==null||zi.remove(),zi=null}function Zp(i){var n;const e=document.getElementById("ui-overlay");if(!e)return;const t=document.createElement("div");t.id="global-error",t.className="global-error",t.innerHTML=`
    <span>✗</span>
    <span>${i}</span>
    <button class="global-error-close">&times;</button>
  `,(n=t.querySelector(".global-error-close"))==null||n.addEventListener("click",()=>{t.remove()}),e.appendChild(t),setTimeout(()=>t==null?void 0:t.remove(),1e4)}fs.connect();Kp("Connecting to dashboard...");fs.waitForConnection(15e3).then(i=>{i?yf():(Kp("Connection timeout — retrying..."),fs.onStateChange(e=>{e==="connected"&&yf()}))});document.addEventListener("DOMContentLoaded",async()=>{await qr.init(),await kw(),gn("chart-pareto",()=>Ia.showTab("pareto")),gn("chart-ablation",()=>Ia.showTab("ablation")),gn("chart-variability",()=>Ia.showTab("variability")),gn("control-play",()=>Pa.togglePlay()),gn("control-step",()=>Pa.step()),gn("control-stop",()=>Pa.stop()),gn("control-panel",()=>Rt.toggle("control-panel")),gn("panel-hud",()=>Rt.toggle("hud")),gn("panel-rail",()=>Rt.toggle("live-rail")),gn("panel-caption",()=>Rt.toggle("caption")),gn("panel-legend",()=>Rt.toggle("legend")),gn("view-cycle",()=>Xs.cycle()),gn("cell-replicate",()=>window.dispatchEvent(new CustomEvent("cell-action-replicate"))),gn("cell-preregister",()=>window.dispatchEvent(new CustomEvent("cell-action-preregister"))),gn("cell-quest",()=>window.dispatchEvent(new CustomEvent("cell-action-quest"))),gn("help",()=>tl.toggle()),gn("escape",()=>{Un.hasCellSelected()?Un.hide():tl.hide()})});const Jp=new Map,Qp=new Map;for(const i of Ti)i.key&&Jp.set(i.key.toLowerCase(),i),i.chord&&Qp.set(i.chord.toLowerCase(),i);window.addEventListener("keydown",i=>{if(i.metaKey||i.ctrlKey||i.altKey)return;const e=i.target;if(e&&["INPUT","SELECT","TEXTAREA"].includes(e.tagName))return;const t=i.key.toLowerCase();if(i.shiftKey){const s=`shift+${t}`,r=Qp.get(s);if(r){if(r.when==="cell-selected"&&!Un.hasCellSelected())return;r.run();return}}const n=Jp.get(t);if(n){if(n.when==="cell-selected"&&!Un.hasCellSelected())return;n.run();return}});const Vw=document.getElementById("dashboard-canvas"),na=zw(),ti=new Hy({canvas:Vw,antialias:na.antialias,alpha:!0,powerPreference:"high-performance"});ti.setSize(window.innerWidth,window.innerHeight);ti.setPixelRatio(na.software?1:Math.min(window.devicePixelRatio,2));ti.shadowMap.enabled=na.shadows;ti.shadowMap.type=Sf;ti.toneMapping=wf;ti.toneMappingExposure=1.2;const Yi=new Qf;Yi.background=new st(658964);Yi.fog=new Au(658964,.015);const ms=new Sn(60,window.innerWidth/window.innerHeight,.1,200);ms.position.set(3.3,4.4,8.8);ms.lookAt(0,1,.1);const Ci=new ob(ms,ti.domElement);Ci.target.set(0,1,.1);Ci.enableDamping=!0;Ci.dampingFactor=.05;Ci.enablePan=!0;Ci.minDistance=5;Ci.maxDistance=80;Ci.maxPolarAngle=Math.PI/2-.05;ub({scene:Yi,camera:ms,renderer:ti,controls:Ci});const Gw=new Zy(4473958,.6);Yi.add(Gw);const mi=new Ky(16777215,1.2);mi.position.set(10,20,10);mi.castShadow=na.shadows;mi.shadow.mapSize.width=2048;mi.shadow.mapSize.height=2048;mi.shadow.camera.near=1;mi.shadow.camera.far=50;mi.shadow.camera.left=-20;mi.shadow.camera.right=20;mi.shadow.camera.top=20;mi.shadow.camera.bottom=-20;Yi.add(mi);const Ww=new $y(8956671,2236979,.5);Yi.add(Ww);const $u=new Qy(8,8,2371648,1449256);$u.position.y=-.01;const em=$u.material;em.transparent=!0;em.opacity=.35;Yi.add($u);function qw(){ms.aspect=window.innerWidth/window.innerHeight,ms.updateProjectionMatrix(),ti.setSize(window.innerWidth,window.innerHeight),ti.setPixelRatio(na.software?1:Math.min(window.devicePixelRatio,2))}window.addEventListener("resize",qw);const Xw=1e3/na.fps;let _c=0;function tm(i){if(requestAnimationFrame(tm),i-_c<Xw)return;const e=(i-_c)/1e3;_c=i,Ci.update(),Pu.update(e),Xu.update(e),ti.render(Yi,ms)}requestAnimationFrame(tm);window.__DASHBOARD__={scene:Yi,camera:ms,renderer:ti,controls:Ci,discoveryMap:Pu,cellDrawer:Un,plotter:Ia,liveRail:$p,caption:Yp,hud:Xu,helpOverlay:tl,viewSwitcher:Xs,controlBar:Pa,controlPanel:Zo,panels:Rt,layout:qr,palette:jp,wsClient:fs,router:Yt,bindings:{list:()=>np().map(i=>({id:i.id,label:i.label,group:i.group,key:i.key}))}};console.log("🚀 Computronium Dashboard initialized");
//# sourceMappingURL=dashboard.js.map
