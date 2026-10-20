var wm=Object.defineProperty;var Tm=(i,e,t)=>e in i?wm(i,e,{enumerable:!0,configurable:!0,writable:!0,value:t}):i[e]=t;var U=(i,e,t)=>Tm(i,typeof e!="symbol"?e+"":e,t);/**
 * @license
 * Copyright 2010-2024 Three.js Authors
 * SPDX-License-Identifier: MIT
 */const ph="168",er={ROTATE:0,DOLLY:1,PAN:2},tr={ROTATE:0,PAN:1,DOLLY_PAN:2,DOLLY_ROTATE:3},Am=0,xu=1,Rm=2,Tf=1,Af=2,Ni=3,hs=0,In=1,Yn=2,ls=0,Cr=1,yu=2,Mu=3,Su=4,Cm=5,Ps=100,Pm=101,Lm=102,Dm=103,Im=104,Um=200,Nm=201,Fm=202,Om=203,yc=204,Mc=205,Bm=206,zm=207,km=208,Hm=209,Vm=210,Gm=211,Wm=212,Xm=213,qm=214,$m=0,Ym=1,jm=2,Ho=3,Km=4,Zm=5,Jm=6,Qm=7,Rf=0,eg=1,tg=2,cs=0,ng=1,ig=2,sg=3,Cf=4,rg=5,ag=6,og=7,Pf=300,Br=301,zr=302,Sc=303,bc=304,rl=306,Ec=1e3,Is=1001,wc=1002,Kn=1003,lg=1004,Ya=1005,ai=1006,Il=1007,Us=1008,Wi=1009,Lf=1010,Df=1011,Pa=1012,mh=1013,Bs=1014,Oi=1015,Na=1016,gh=1017,_h=1018,kr=1020,If=35902,Uf=1021,Nf=1022,ci=1023,Ff=1024,Of=1025,Pr=1026,Hr=1027,Bf=1028,vh=1029,zf=1030,xh=1031,yh=1033,Do=33776,Io=33777,Uo=33778,No=33779,Tc=35840,Ac=35841,Rc=35842,Cc=35843,Pc=36196,Lc=37492,Dc=37496,Ic=37808,Uc=37809,Nc=37810,Fc=37811,Oc=37812,Bc=37813,zc=37814,kc=37815,Hc=37816,Vc=37817,Gc=37818,Wc=37819,Xc=37820,qc=37821,Fo=36492,$c=36494,Yc=36495,kf=36283,jc=36284,Kc=36285,Zc=36286,cg=3200,hg=3201,Hf=0,ug=1,as="",xi="srgb",ps="srgb-linear",Mh="display-p3",al="display-p3-linear",Vo="linear",Ot="srgb",Go="rec709",Wo="p3",nr=7680,bu=519,dg=512,fg=513,pg=514,Vf=515,mg=516,gg=517,_g=518,vg=519,Jc=35044,Eu="300 es",Bi=2e3,Xo=2001;let Kr=class{addEventListener(e,t){this._listeners===void 0&&(this._listeners={});const n=this._listeners;n[e]===void 0&&(n[e]=[]),n[e].indexOf(t)===-1&&n[e].push(t)}hasEventListener(e,t){if(this._listeners===void 0)return!1;const n=this._listeners;return n[e]!==void 0&&n[e].indexOf(t)!==-1}removeEventListener(e,t){if(this._listeners===void 0)return;const s=this._listeners[e];if(s!==void 0){const r=s.indexOf(t);r!==-1&&s.splice(r,1)}}dispatchEvent(e){if(this._listeners===void 0)return;const n=this._listeners[e.type];if(n!==void 0){e.target=this;const s=n.slice(0);for(let r=0,a=s.length;r<a;r++)s[r].call(this,e);e.target=null}}};const yn=["00","01","02","03","04","05","06","07","08","09","0a","0b","0c","0d","0e","0f","10","11","12","13","14","15","16","17","18","19","1a","1b","1c","1d","1e","1f","20","21","22","23","24","25","26","27","28","29","2a","2b","2c","2d","2e","2f","30","31","32","33","34","35","36","37","38","39","3a","3b","3c","3d","3e","3f","40","41","42","43","44","45","46","47","48","49","4a","4b","4c","4d","4e","4f","50","51","52","53","54","55","56","57","58","59","5a","5b","5c","5d","5e","5f","60","61","62","63","64","65","66","67","68","69","6a","6b","6c","6d","6e","6f","70","71","72","73","74","75","76","77","78","79","7a","7b","7c","7d","7e","7f","80","81","82","83","84","85","86","87","88","89","8a","8b","8c","8d","8e","8f","90","91","92","93","94","95","96","97","98","99","9a","9b","9c","9d","9e","9f","a0","a1","a2","a3","a4","a5","a6","a7","a8","a9","aa","ab","ac","ad","ae","af","b0","b1","b2","b3","b4","b5","b6","b7","b8","b9","ba","bb","bc","bd","be","bf","c0","c1","c2","c3","c4","c5","c6","c7","c8","c9","ca","cb","cc","cd","ce","cf","d0","d1","d2","d3","d4","d5","d6","d7","d8","d9","da","db","dc","dd","de","df","e0","e1","e2","e3","e4","e5","e6","e7","e8","e9","ea","eb","ec","ed","ee","ef","f0","f1","f2","f3","f4","f5","f6","f7","f8","f9","fa","fb","fc","fd","fe","ff"];let wu=1234567;const Lr=Math.PI/180,La=180/Math.PI;function ki(){const i=Math.random()*4294967295|0,e=Math.random()*4294967295|0,t=Math.random()*4294967295|0,n=Math.random()*4294967295|0;return(yn[i&255]+yn[i>>8&255]+yn[i>>16&255]+yn[i>>24&255]+"-"+yn[e&255]+yn[e>>8&255]+"-"+yn[e>>16&15|64]+yn[e>>24&255]+"-"+yn[t&63|128]+yn[t>>8&255]+"-"+yn[t>>16&255]+yn[t>>24&255]+yn[n&255]+yn[n>>8&255]+yn[n>>16&255]+yn[n>>24&255]).toLowerCase()}function Sn(i,e,t){return Math.max(e,Math.min(t,i))}function Sh(i,e){return(i%e+e)%e}function xg(i,e,t,n,s){return n+(i-e)*(s-n)/(t-e)}function yg(i,e,t){return i!==e?(t-i)/(e-i):0}function Ta(i,e,t){return(1-t)*i+t*e}function Mg(i,e,t,n){return Ta(i,e,1-Math.exp(-t*n))}function Sg(i,e=1){return e-Math.abs(Sh(i,e*2)-e)}function bg(i,e,t){return i<=e?0:i>=t?1:(i=(i-e)/(t-e),i*i*(3-2*i))}function Eg(i,e,t){return i<=e?0:i>=t?1:(i=(i-e)/(t-e),i*i*i*(i*(i*6-15)+10))}function wg(i,e){return i+Math.floor(Math.random()*(e-i+1))}function Tg(i,e){return i+Math.random()*(e-i)}function Ag(i){return i*(.5-Math.random())}function Rg(i){i!==void 0&&(wu=i);let e=wu+=1831565813;return e=Math.imul(e^e>>>15,e|1),e^=e+Math.imul(e^e>>>7,e|61),((e^e>>>14)>>>0)/4294967296}function Cg(i){return i*Lr}function Pg(i){return i*La}function Lg(i){return(i&i-1)===0&&i!==0}function Dg(i){return Math.pow(2,Math.ceil(Math.log(i)/Math.LN2))}function Ig(i){return Math.pow(2,Math.floor(Math.log(i)/Math.LN2))}function Ug(i,e,t,n,s){const r=Math.cos,a=Math.sin,o=r(t/2),l=a(t/2),c=r((e+n)/2),h=a((e+n)/2),u=r((e-n)/2),d=a((e-n)/2),f=r((n-e)/2),g=a((n-e)/2);switch(s){case"XYX":i.set(o*h,l*u,l*d,o*c);break;case"YZY":i.set(l*d,o*h,l*u,o*c);break;case"ZXZ":i.set(l*u,l*d,o*h,o*c);break;case"XZX":i.set(o*h,l*g,l*f,o*c);break;case"YXY":i.set(l*f,o*h,l*g,o*c);break;case"ZYZ":i.set(l*g,l*f,o*h,o*c);break;default:console.warn("THREE.MathUtils: .setQuaternionFromProperEuler() encountered an unknown order: "+s)}}function oi(i,e){switch(e.constructor){case Float32Array:return i;case Uint32Array:return i/4294967295;case Uint16Array:return i/65535;case Uint8Array:return i/255;case Int32Array:return Math.max(i/2147483647,-1);case Int16Array:return Math.max(i/32767,-1);case Int8Array:return Math.max(i/127,-1);default:throw new Error("Invalid component type.")}}function Tt(i,e){switch(e.constructor){case Float32Array:return i;case Uint32Array:return Math.round(i*4294967295);case Uint16Array:return Math.round(i*65535);case Uint8Array:return Math.round(i*255);case Int32Array:return Math.round(i*2147483647);case Int16Array:return Math.round(i*32767);case Int8Array:return Math.round(i*127);default:throw new Error("Invalid component type.")}}const Qc={DEG2RAD:Lr,RAD2DEG:La,generateUUID:ki,clamp:Sn,euclideanModulo:Sh,mapLinear:xg,inverseLerp:yg,lerp:Ta,damp:Mg,pingpong:Sg,smoothstep:bg,smootherstep:Eg,randInt:wg,randFloat:Tg,randFloatSpread:Ag,seededRandom:Rg,degToRad:Cg,radToDeg:Pg,isPowerOfTwo:Lg,ceilPowerOfTwo:Dg,floorPowerOfTwo:Ig,setQuaternionFromProperEuler:Ug,normalize:Tt,denormalize:oi};class qe{constructor(e=0,t=0){qe.prototype.isVector2=!0,this.x=e,this.y=t}get width(){return this.x}set width(e){this.x=e}get height(){return this.y}set height(e){this.y=e}set(e,t){return this.x=e,this.y=t,this}setScalar(e){return this.x=e,this.y=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y)}copy(e){return this.x=e.x,this.y=e.y,this}add(e){return this.x+=e.x,this.y+=e.y,this}addScalar(e){return this.x+=e,this.y+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this}subScalar(e){return this.x-=e,this.y-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this}multiply(e){return this.x*=e.x,this.y*=e.y,this}multiplyScalar(e){return this.x*=e,this.y*=e,this}divide(e){return this.x/=e.x,this.y/=e.y,this}divideScalar(e){return this.multiplyScalar(1/e)}applyMatrix3(e){const t=this.x,n=this.y,s=e.elements;return this.x=s[0]*t+s[3]*n+s[6],this.y=s[1]*t+s[4]*n+s[7],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this}negate(){return this.x=-this.x,this.y=-this.y,this}dot(e){return this.x*e.x+this.y*e.y}cross(e){return this.x*e.y-this.y*e.x}lengthSq(){return this.x*this.x+this.y*this.y}length(){return Math.sqrt(this.x*this.x+this.y*this.y)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)}normalize(){return this.divideScalar(this.length()||1)}angle(){return Math.atan2(-this.y,-this.x)+Math.PI}angleTo(e){const t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;const n=this.dot(e)/t;return Math.acos(Sn(n,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){const t=this.x-e.x,n=this.y-e.y;return t*t+n*n}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this}equals(e){return e.x===this.x&&e.y===this.y}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this}rotateAround(e,t){const n=Math.cos(t),s=Math.sin(t),r=this.x-e.x,a=this.y-e.y;return this.x=r*n-a*s+e.x,this.y=r*s+a*n+e.y,this}random(){return this.x=Math.random(),this.y=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y}}class at{constructor(e,t,n,s,r,a,o,l,c){at.prototype.isMatrix3=!0,this.elements=[1,0,0,0,1,0,0,0,1],e!==void 0&&this.set(e,t,n,s,r,a,o,l,c)}set(e,t,n,s,r,a,o,l,c){const h=this.elements;return h[0]=e,h[1]=s,h[2]=o,h[3]=t,h[4]=r,h[5]=l,h[6]=n,h[7]=a,h[8]=c,this}identity(){return this.set(1,0,0,0,1,0,0,0,1),this}copy(e){const t=this.elements,n=e.elements;return t[0]=n[0],t[1]=n[1],t[2]=n[2],t[3]=n[3],t[4]=n[4],t[5]=n[5],t[6]=n[6],t[7]=n[7],t[8]=n[8],this}extractBasis(e,t,n){return e.setFromMatrix3Column(this,0),t.setFromMatrix3Column(this,1),n.setFromMatrix3Column(this,2),this}setFromMatrix4(e){const t=e.elements;return this.set(t[0],t[4],t[8],t[1],t[5],t[9],t[2],t[6],t[10]),this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){const n=e.elements,s=t.elements,r=this.elements,a=n[0],o=n[3],l=n[6],c=n[1],h=n[4],u=n[7],d=n[2],f=n[5],g=n[8],_=s[0],m=s[3],p=s[6],S=s[1],y=s[4],w=s[7],O=s[2],A=s[5],C=s[8];return r[0]=a*_+o*S+l*O,r[3]=a*m+o*y+l*A,r[6]=a*p+o*w+l*C,r[1]=c*_+h*S+u*O,r[4]=c*m+h*y+u*A,r[7]=c*p+h*w+u*C,r[2]=d*_+f*S+g*O,r[5]=d*m+f*y+g*A,r[8]=d*p+f*w+g*C,this}multiplyScalar(e){const t=this.elements;return t[0]*=e,t[3]*=e,t[6]*=e,t[1]*=e,t[4]*=e,t[7]*=e,t[2]*=e,t[5]*=e,t[8]*=e,this}determinant(){const e=this.elements,t=e[0],n=e[1],s=e[2],r=e[3],a=e[4],o=e[5],l=e[6],c=e[7],h=e[8];return t*a*h-t*o*c-n*r*h+n*o*l+s*r*c-s*a*l}invert(){const e=this.elements,t=e[0],n=e[1],s=e[2],r=e[3],a=e[4],o=e[5],l=e[6],c=e[7],h=e[8],u=h*a-o*c,d=o*l-h*r,f=c*r-a*l,g=t*u+n*d+s*f;if(g===0)return this.set(0,0,0,0,0,0,0,0,0);const _=1/g;return e[0]=u*_,e[1]=(s*c-h*n)*_,e[2]=(o*n-s*a)*_,e[3]=d*_,e[4]=(h*t-s*l)*_,e[5]=(s*r-o*t)*_,e[6]=f*_,e[7]=(n*l-c*t)*_,e[8]=(a*t-n*r)*_,this}transpose(){let e;const t=this.elements;return e=t[1],t[1]=t[3],t[3]=e,e=t[2],t[2]=t[6],t[6]=e,e=t[5],t[5]=t[7],t[7]=e,this}getNormalMatrix(e){return this.setFromMatrix4(e).invert().transpose()}transposeIntoArray(e){const t=this.elements;return e[0]=t[0],e[1]=t[3],e[2]=t[6],e[3]=t[1],e[4]=t[4],e[5]=t[7],e[6]=t[2],e[7]=t[5],e[8]=t[8],this}setUvTransform(e,t,n,s,r,a,o){const l=Math.cos(r),c=Math.sin(r);return this.set(n*l,n*c,-n*(l*a+c*o)+a+e,-s*c,s*l,-s*(-c*a+l*o)+o+t,0,0,1),this}scale(e,t){return this.premultiply(Ul.makeScale(e,t)),this}rotate(e){return this.premultiply(Ul.makeRotation(-e)),this}translate(e,t){return this.premultiply(Ul.makeTranslation(e,t)),this}makeTranslation(e,t){return e.isVector2?this.set(1,0,e.x,0,1,e.y,0,0,1):this.set(1,0,e,0,1,t,0,0,1),this}makeRotation(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,-n,0,n,t,0,0,0,1),this}makeScale(e,t){return this.set(e,0,0,0,t,0,0,0,1),this}equals(e){const t=this.elements,n=e.elements;for(let s=0;s<9;s++)if(t[s]!==n[s])return!1;return!0}fromArray(e,t=0){for(let n=0;n<9;n++)this.elements[n]=e[n+t];return this}toArray(e=[],t=0){const n=this.elements;return e[t]=n[0],e[t+1]=n[1],e[t+2]=n[2],e[t+3]=n[3],e[t+4]=n[4],e[t+5]=n[5],e[t+6]=n[6],e[t+7]=n[7],e[t+8]=n[8],e}clone(){return new this.constructor().fromArray(this.elements)}}const Ul=new at;function Gf(i){for(let e=i.length-1;e>=0;--e)if(i[e]>=65535)return!0;return!1}function qo(i){return document.createElementNS("http://www.w3.org/1999/xhtml",i)}function Ng(){const i=qo("canvas");return i.style.display="block",i}const Tu={};function Dr(i){i in Tu||(Tu[i]=!0,console.warn(i))}function Fg(i,e,t){return new Promise(function(n,s){function r(){switch(i.clientWaitSync(e,i.SYNC_FLUSH_COMMANDS_BIT,0)){case i.WAIT_FAILED:s();break;case i.TIMEOUT_EXPIRED:setTimeout(r,t);break;default:n()}}setTimeout(r,t)})}const Au=new at().set(.8224621,.177538,0,.0331941,.9668058,0,.0170827,.0723974,.9105199),Ru=new at().set(1.2249401,-.2249404,0,-.0420569,1.0420571,0,-.0196376,-.0786361,1.0982735),ha={[ps]:{transfer:Vo,primaries:Go,luminanceCoefficients:[.2126,.7152,.0722],toReference:i=>i,fromReference:i=>i},[xi]:{transfer:Ot,primaries:Go,luminanceCoefficients:[.2126,.7152,.0722],toReference:i=>i.convertSRGBToLinear(),fromReference:i=>i.convertLinearToSRGB()},[al]:{transfer:Vo,primaries:Wo,luminanceCoefficients:[.2289,.6917,.0793],toReference:i=>i.applyMatrix3(Ru),fromReference:i=>i.applyMatrix3(Au)},[Mh]:{transfer:Ot,primaries:Wo,luminanceCoefficients:[.2289,.6917,.0793],toReference:i=>i.convertSRGBToLinear().applyMatrix3(Ru),fromReference:i=>i.applyMatrix3(Au).convertLinearToSRGB()}},Og=new Set([ps,al]),bt={enabled:!0,_workingColorSpace:ps,get workingColorSpace(){return this._workingColorSpace},set workingColorSpace(i){if(!Og.has(i))throw new Error(`Unsupported working color space, "${i}".`);this._workingColorSpace=i},convert:function(i,e,t){if(this.enabled===!1||e===t||!e||!t)return i;const n=ha[e].toReference,s=ha[t].fromReference;return s(n(i))},fromWorkingColorSpace:function(i,e){return this.convert(i,this._workingColorSpace,e)},toWorkingColorSpace:function(i,e){return this.convert(i,e,this._workingColorSpace)},getPrimaries:function(i){return ha[i].primaries},getTransfer:function(i){return i===as?Vo:ha[i].transfer},getLuminanceCoefficients:function(i,e=this._workingColorSpace){return i.fromArray(ha[e].luminanceCoefficients)}};function Ir(i){return i<.04045?i*.0773993808:Math.pow(i*.9478672986+.0521327014,2.4)}function Nl(i){return i<.0031308?i*12.92:1.055*Math.pow(i,.41666)-.055}let ir;class Bg{static getDataURL(e){if(/^data:/i.test(e.src)||typeof HTMLCanvasElement>"u")return e.src;let t;if(e instanceof HTMLCanvasElement)t=e;else{ir===void 0&&(ir=qo("canvas")),ir.width=e.width,ir.height=e.height;const n=ir.getContext("2d");e instanceof ImageData?n.putImageData(e,0,0):n.drawImage(e,0,0,e.width,e.height),t=ir}return t.width>2048||t.height>2048?(console.warn("THREE.ImageUtils.getDataURL: Image converted to jpg for performance reasons",e),t.toDataURL("image/jpeg",.6)):t.toDataURL("image/png")}static sRGBToLinear(e){if(typeof HTMLImageElement<"u"&&e instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&e instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&e instanceof ImageBitmap){const t=qo("canvas");t.width=e.width,t.height=e.height;const n=t.getContext("2d");n.drawImage(e,0,0,e.width,e.height);const s=n.getImageData(0,0,e.width,e.height),r=s.data;for(let a=0;a<r.length;a++)r[a]=Ir(r[a]/255)*255;return n.putImageData(s,0,0),t}else if(e.data){const t=e.data.slice(0);for(let n=0;n<t.length;n++)t instanceof Uint8Array||t instanceof Uint8ClampedArray?t[n]=Math.floor(Ir(t[n]/255)*255):t[n]=Ir(t[n]);return{data:t,width:e.width,height:e.height}}else return console.warn("THREE.ImageUtils.sRGBToLinear(): Unsupported image type. No color space conversion applied."),e}}let zg=0;class Wf{constructor(e=null){this.isSource=!0,Object.defineProperty(this,"id",{value:zg++}),this.uuid=ki(),this.data=e,this.dataReady=!0,this.version=0}set needsUpdate(e){e===!0&&this.version++}toJSON(e){const t=e===void 0||typeof e=="string";if(!t&&e.images[this.uuid]!==void 0)return e.images[this.uuid];const n={uuid:this.uuid,url:""},s=this.data;if(s!==null){let r;if(Array.isArray(s)){r=[];for(let a=0,o=s.length;a<o;a++)s[a].isDataTexture?r.push(Fl(s[a].image)):r.push(Fl(s[a]))}else r=Fl(s);n.url=r}return t||(e.images[this.uuid]=n),n}}function Fl(i){return typeof HTMLImageElement<"u"&&i instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&i instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&i instanceof ImageBitmap?Bg.getDataURL(i):i.data?{data:Array.from(i.data),width:i.width,height:i.height,type:i.data.constructor.name}:(console.warn("THREE.Texture: Unable to serialize Texture."),{})}let kg=0;class Ln extends Kr{constructor(e=Ln.DEFAULT_IMAGE,t=Ln.DEFAULT_MAPPING,n=Is,s=Is,r=ai,a=Us,o=ci,l=Wi,c=Ln.DEFAULT_ANISOTROPY,h=as){super(),this.isTexture=!0,Object.defineProperty(this,"id",{value:kg++}),this.uuid=ki(),this.name="",this.source=new Wf(e),this.mipmaps=[],this.mapping=t,this.channel=0,this.wrapS=n,this.wrapT=s,this.magFilter=r,this.minFilter=a,this.anisotropy=c,this.format=o,this.internalFormat=null,this.type=l,this.offset=new qe(0,0),this.repeat=new qe(1,1),this.center=new qe(0,0),this.rotation=0,this.matrixAutoUpdate=!0,this.matrix=new at,this.generateMipmaps=!0,this.premultiplyAlpha=!1,this.flipY=!0,this.unpackAlignment=4,this.colorSpace=h,this.userData={},this.version=0,this.onUpdate=null,this.isRenderTargetTexture=!1,this.pmremVersion=0}get image(){return this.source.data}set image(e=null){this.source.data=e}updateMatrix(){this.matrix.setUvTransform(this.offset.x,this.offset.y,this.repeat.x,this.repeat.y,this.rotation,this.center.x,this.center.y)}clone(){return new this.constructor().copy(this)}copy(e){return this.name=e.name,this.source=e.source,this.mipmaps=e.mipmaps.slice(0),this.mapping=e.mapping,this.channel=e.channel,this.wrapS=e.wrapS,this.wrapT=e.wrapT,this.magFilter=e.magFilter,this.minFilter=e.minFilter,this.anisotropy=e.anisotropy,this.format=e.format,this.internalFormat=e.internalFormat,this.type=e.type,this.offset.copy(e.offset),this.repeat.copy(e.repeat),this.center.copy(e.center),this.rotation=e.rotation,this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrix.copy(e.matrix),this.generateMipmaps=e.generateMipmaps,this.premultiplyAlpha=e.premultiplyAlpha,this.flipY=e.flipY,this.unpackAlignment=e.unpackAlignment,this.colorSpace=e.colorSpace,this.userData=JSON.parse(JSON.stringify(e.userData)),this.needsUpdate=!0,this}toJSON(e){const t=e===void 0||typeof e=="string";if(!t&&e.textures[this.uuid]!==void 0)return e.textures[this.uuid];const n={metadata:{version:4.6,type:"Texture",generator:"Texture.toJSON"},uuid:this.uuid,name:this.name,image:this.source.toJSON(e).uuid,mapping:this.mapping,channel:this.channel,repeat:[this.repeat.x,this.repeat.y],offset:[this.offset.x,this.offset.y],center:[this.center.x,this.center.y],rotation:this.rotation,wrap:[this.wrapS,this.wrapT],format:this.format,internalFormat:this.internalFormat,type:this.type,colorSpace:this.colorSpace,minFilter:this.minFilter,magFilter:this.magFilter,anisotropy:this.anisotropy,flipY:this.flipY,generateMipmaps:this.generateMipmaps,premultiplyAlpha:this.premultiplyAlpha,unpackAlignment:this.unpackAlignment};return Object.keys(this.userData).length>0&&(n.userData=this.userData),t||(e.textures[this.uuid]=n),n}dispose(){this.dispatchEvent({type:"dispose"})}transformUv(e){if(this.mapping!==Pf)return e;if(e.applyMatrix3(this.matrix),e.x<0||e.x>1)switch(this.wrapS){case Ec:e.x=e.x-Math.floor(e.x);break;case Is:e.x=e.x<0?0:1;break;case wc:Math.abs(Math.floor(e.x)%2)===1?e.x=Math.ceil(e.x)-e.x:e.x=e.x-Math.floor(e.x);break}if(e.y<0||e.y>1)switch(this.wrapT){case Ec:e.y=e.y-Math.floor(e.y);break;case Is:e.y=e.y<0?0:1;break;case wc:Math.abs(Math.floor(e.y)%2)===1?e.y=Math.ceil(e.y)-e.y:e.y=e.y-Math.floor(e.y);break}return this.flipY&&(e.y=1-e.y),e}set needsUpdate(e){e===!0&&(this.version++,this.source.needsUpdate=!0)}set needsPMREMUpdate(e){e===!0&&this.pmremVersion++}}Ln.DEFAULT_IMAGE=null;Ln.DEFAULT_MAPPING=Pf;Ln.DEFAULT_ANISOTROPY=1;class nn{constructor(e=0,t=0,n=0,s=1){nn.prototype.isVector4=!0,this.x=e,this.y=t,this.z=n,this.w=s}get width(){return this.z}set width(e){this.z=e}get height(){return this.w}set height(e){this.w=e}set(e,t,n,s){return this.x=e,this.y=t,this.z=n,this.w=s,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this.w=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setW(e){return this.w=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;case 3:this.w=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;case 3:return this.w;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z,this.w)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this.w=e.w!==void 0?e.w:1,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this.w+=e.w,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this.w+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this.w=e.w+t.w,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this.w+=e.w*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this.w-=e.w,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this.w-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this.w=e.w-t.w,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this.w*=e.w,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this.w*=e,this}applyMatrix4(e){const t=this.x,n=this.y,s=this.z,r=this.w,a=e.elements;return this.x=a[0]*t+a[4]*n+a[8]*s+a[12]*r,this.y=a[1]*t+a[5]*n+a[9]*s+a[13]*r,this.z=a[2]*t+a[6]*n+a[10]*s+a[14]*r,this.w=a[3]*t+a[7]*n+a[11]*s+a[15]*r,this}divideScalar(e){return this.multiplyScalar(1/e)}setAxisAngleFromQuaternion(e){this.w=2*Math.acos(e.w);const t=Math.sqrt(1-e.w*e.w);return t<1e-4?(this.x=1,this.y=0,this.z=0):(this.x=e.x/t,this.y=e.y/t,this.z=e.z/t),this}setAxisAngleFromRotationMatrix(e){let t,n,s,r;const l=e.elements,c=l[0],h=l[4],u=l[8],d=l[1],f=l[5],g=l[9],_=l[2],m=l[6],p=l[10];if(Math.abs(h-d)<.01&&Math.abs(u-_)<.01&&Math.abs(g-m)<.01){if(Math.abs(h+d)<.1&&Math.abs(u+_)<.1&&Math.abs(g+m)<.1&&Math.abs(c+f+p-3)<.1)return this.set(1,0,0,0),this;t=Math.PI;const y=(c+1)/2,w=(f+1)/2,O=(p+1)/2,A=(h+d)/4,C=(u+_)/4,F=(g+m)/4;return y>w&&y>O?y<.01?(n=0,s=.707106781,r=.707106781):(n=Math.sqrt(y),s=A/n,r=C/n):w>O?w<.01?(n=.707106781,s=0,r=.707106781):(s=Math.sqrt(w),n=A/s,r=F/s):O<.01?(n=.707106781,s=.707106781,r=0):(r=Math.sqrt(O),n=C/r,s=F/r),this.set(n,s,r,t),this}let S=Math.sqrt((m-g)*(m-g)+(u-_)*(u-_)+(d-h)*(d-h));return Math.abs(S)<.001&&(S=1),this.x=(m-g)/S,this.y=(u-_)/S,this.z=(d-h)/S,this.w=Math.acos((c+f+p-1)/2),this}setFromMatrixPosition(e){const t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this.w=t[15],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this.w=Math.min(this.w,e.w),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this.w=Math.max(this.w,e.w),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this.z=Math.max(e.z,Math.min(t.z,this.z)),this.w=Math.max(e.w,Math.min(t.w,this.w)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this.z=Math.max(e,Math.min(t,this.z)),this.w=Math.max(e,Math.min(t,this.w)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this.w=Math.floor(this.w),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this.w=Math.ceil(this.w),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this.w=Math.round(this.w),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this.w=Math.trunc(this.w),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this.w=-this.w,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z+this.w*e.w}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)+Math.abs(this.w)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this.w+=(e.w-this.w)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this.z=e.z+(t.z-e.z)*n,this.w=e.w+(t.w-e.w)*n,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z&&e.w===this.w}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this.w=e[t+3],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e[t+3]=this.w,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this.w=e.getW(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this.w=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z,yield this.w}}class Hg extends Kr{constructor(e=1,t=1,n={}){super(),this.isRenderTarget=!0,this.width=e,this.height=t,this.depth=1,this.scissor=new nn(0,0,e,t),this.scissorTest=!1,this.viewport=new nn(0,0,e,t);const s={width:e,height:t,depth:1};n=Object.assign({generateMipmaps:!1,internalFormat:null,minFilter:ai,depthBuffer:!0,stencilBuffer:!1,resolveDepthBuffer:!0,resolveStencilBuffer:!0,depthTexture:null,samples:0,count:1},n);const r=new Ln(s,n.mapping,n.wrapS,n.wrapT,n.magFilter,n.minFilter,n.format,n.type,n.anisotropy,n.colorSpace);r.flipY=!1,r.generateMipmaps=n.generateMipmaps,r.internalFormat=n.internalFormat,this.textures=[];const a=n.count;for(let o=0;o<a;o++)this.textures[o]=r.clone(),this.textures[o].isRenderTargetTexture=!0;this.depthBuffer=n.depthBuffer,this.stencilBuffer=n.stencilBuffer,this.resolveDepthBuffer=n.resolveDepthBuffer,this.resolveStencilBuffer=n.resolveStencilBuffer,this.depthTexture=n.depthTexture,this.samples=n.samples}get texture(){return this.textures[0]}set texture(e){this.textures[0]=e}setSize(e,t,n=1){if(this.width!==e||this.height!==t||this.depth!==n){this.width=e,this.height=t,this.depth=n;for(let s=0,r=this.textures.length;s<r;s++)this.textures[s].image.width=e,this.textures[s].image.height=t,this.textures[s].image.depth=n;this.dispose()}this.viewport.set(0,0,e,t),this.scissor.set(0,0,e,t)}clone(){return new this.constructor().copy(this)}copy(e){this.width=e.width,this.height=e.height,this.depth=e.depth,this.scissor.copy(e.scissor),this.scissorTest=e.scissorTest,this.viewport.copy(e.viewport),this.textures.length=0;for(let n=0,s=e.textures.length;n<s;n++)this.textures[n]=e.textures[n].clone(),this.textures[n].isRenderTargetTexture=!0;const t=Object.assign({},e.texture.image);return this.texture.source=new Wf(t),this.depthBuffer=e.depthBuffer,this.stencilBuffer=e.stencilBuffer,this.resolveDepthBuffer=e.resolveDepthBuffer,this.resolveStencilBuffer=e.resolveStencilBuffer,e.depthTexture!==null&&(this.depthTexture=e.depthTexture.clone()),this.samples=e.samples,this}dispose(){this.dispatchEvent({type:"dispose"})}}class zs extends Hg{constructor(e=1,t=1,n={}){super(e,t,n),this.isWebGLRenderTarget=!0}}class Xf extends Ln{constructor(e=null,t=1,n=1,s=1){super(null),this.isDataArrayTexture=!0,this.image={data:e,width:t,height:n,depth:s},this.magFilter=Kn,this.minFilter=Kn,this.wrapR=Is,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1,this.layerUpdates=new Set}addLayerUpdate(e){this.layerUpdates.add(e)}clearLayerUpdates(){this.layerUpdates.clear()}}class Vg extends Ln{constructor(e=null,t=1,n=1,s=1){super(null),this.isData3DTexture=!0,this.image={data:e,width:t,height:n,depth:s},this.magFilter=Kn,this.minFilter=Kn,this.wrapR=Is,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}}class ks{constructor(e=0,t=0,n=0,s=1){this.isQuaternion=!0,this._x=e,this._y=t,this._z=n,this._w=s}static slerpFlat(e,t,n,s,r,a,o){let l=n[s+0],c=n[s+1],h=n[s+2],u=n[s+3];const d=r[a+0],f=r[a+1],g=r[a+2],_=r[a+3];if(o===0){e[t+0]=l,e[t+1]=c,e[t+2]=h,e[t+3]=u;return}if(o===1){e[t+0]=d,e[t+1]=f,e[t+2]=g,e[t+3]=_;return}if(u!==_||l!==d||c!==f||h!==g){let m=1-o;const p=l*d+c*f+h*g+u*_,S=p>=0?1:-1,y=1-p*p;if(y>Number.EPSILON){const O=Math.sqrt(y),A=Math.atan2(O,p*S);m=Math.sin(m*A)/O,o=Math.sin(o*A)/O}const w=o*S;if(l=l*m+d*w,c=c*m+f*w,h=h*m+g*w,u=u*m+_*w,m===1-o){const O=1/Math.sqrt(l*l+c*c+h*h+u*u);l*=O,c*=O,h*=O,u*=O}}e[t]=l,e[t+1]=c,e[t+2]=h,e[t+3]=u}static multiplyQuaternionsFlat(e,t,n,s,r,a){const o=n[s],l=n[s+1],c=n[s+2],h=n[s+3],u=r[a],d=r[a+1],f=r[a+2],g=r[a+3];return e[t]=o*g+h*u+l*f-c*d,e[t+1]=l*g+h*d+c*u-o*f,e[t+2]=c*g+h*f+o*d-l*u,e[t+3]=h*g-o*u-l*d-c*f,e}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get w(){return this._w}set w(e){this._w=e,this._onChangeCallback()}set(e,t,n,s){return this._x=e,this._y=t,this._z=n,this._w=s,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._w)}copy(e){return this._x=e.x,this._y=e.y,this._z=e.z,this._w=e.w,this._onChangeCallback(),this}setFromEuler(e,t=!0){const n=e._x,s=e._y,r=e._z,a=e._order,o=Math.cos,l=Math.sin,c=o(n/2),h=o(s/2),u=o(r/2),d=l(n/2),f=l(s/2),g=l(r/2);switch(a){case"XYZ":this._x=d*h*u+c*f*g,this._y=c*f*u-d*h*g,this._z=c*h*g+d*f*u,this._w=c*h*u-d*f*g;break;case"YXZ":this._x=d*h*u+c*f*g,this._y=c*f*u-d*h*g,this._z=c*h*g-d*f*u,this._w=c*h*u+d*f*g;break;case"ZXY":this._x=d*h*u-c*f*g,this._y=c*f*u+d*h*g,this._z=c*h*g+d*f*u,this._w=c*h*u-d*f*g;break;case"ZYX":this._x=d*h*u-c*f*g,this._y=c*f*u+d*h*g,this._z=c*h*g-d*f*u,this._w=c*h*u+d*f*g;break;case"YZX":this._x=d*h*u+c*f*g,this._y=c*f*u+d*h*g,this._z=c*h*g-d*f*u,this._w=c*h*u-d*f*g;break;case"XZY":this._x=d*h*u-c*f*g,this._y=c*f*u-d*h*g,this._z=c*h*g+d*f*u,this._w=c*h*u+d*f*g;break;default:console.warn("THREE.Quaternion: .setFromEuler() encountered an unknown order: "+a)}return t===!0&&this._onChangeCallback(),this}setFromAxisAngle(e,t){const n=t/2,s=Math.sin(n);return this._x=e.x*s,this._y=e.y*s,this._z=e.z*s,this._w=Math.cos(n),this._onChangeCallback(),this}setFromRotationMatrix(e){const t=e.elements,n=t[0],s=t[4],r=t[8],a=t[1],o=t[5],l=t[9],c=t[2],h=t[6],u=t[10],d=n+o+u;if(d>0){const f=.5/Math.sqrt(d+1);this._w=.25/f,this._x=(h-l)*f,this._y=(r-c)*f,this._z=(a-s)*f}else if(n>o&&n>u){const f=2*Math.sqrt(1+n-o-u);this._w=(h-l)/f,this._x=.25*f,this._y=(s+a)/f,this._z=(r+c)/f}else if(o>u){const f=2*Math.sqrt(1+o-n-u);this._w=(r-c)/f,this._x=(s+a)/f,this._y=.25*f,this._z=(l+h)/f}else{const f=2*Math.sqrt(1+u-n-o);this._w=(a-s)/f,this._x=(r+c)/f,this._y=(l+h)/f,this._z=.25*f}return this._onChangeCallback(),this}setFromUnitVectors(e,t){let n=e.dot(t)+1;return n<Number.EPSILON?(n=0,Math.abs(e.x)>Math.abs(e.z)?(this._x=-e.y,this._y=e.x,this._z=0,this._w=n):(this._x=0,this._y=-e.z,this._z=e.y,this._w=n)):(this._x=e.y*t.z-e.z*t.y,this._y=e.z*t.x-e.x*t.z,this._z=e.x*t.y-e.y*t.x,this._w=n),this.normalize()}angleTo(e){return 2*Math.acos(Math.abs(Sn(this.dot(e),-1,1)))}rotateTowards(e,t){const n=this.angleTo(e);if(n===0)return this;const s=Math.min(1,t/n);return this.slerp(e,s),this}identity(){return this.set(0,0,0,1)}invert(){return this.conjugate()}conjugate(){return this._x*=-1,this._y*=-1,this._z*=-1,this._onChangeCallback(),this}dot(e){return this._x*e._x+this._y*e._y+this._z*e._z+this._w*e._w}lengthSq(){return this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w}length(){return Math.sqrt(this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w)}normalize(){let e=this.length();return e===0?(this._x=0,this._y=0,this._z=0,this._w=1):(e=1/e,this._x=this._x*e,this._y=this._y*e,this._z=this._z*e,this._w=this._w*e),this._onChangeCallback(),this}multiply(e){return this.multiplyQuaternions(this,e)}premultiply(e){return this.multiplyQuaternions(e,this)}multiplyQuaternions(e,t){const n=e._x,s=e._y,r=e._z,a=e._w,o=t._x,l=t._y,c=t._z,h=t._w;return this._x=n*h+a*o+s*c-r*l,this._y=s*h+a*l+r*o-n*c,this._z=r*h+a*c+n*l-s*o,this._w=a*h-n*o-s*l-r*c,this._onChangeCallback(),this}slerp(e,t){if(t===0)return this;if(t===1)return this.copy(e);const n=this._x,s=this._y,r=this._z,a=this._w;let o=a*e._w+n*e._x+s*e._y+r*e._z;if(o<0?(this._w=-e._w,this._x=-e._x,this._y=-e._y,this._z=-e._z,o=-o):this.copy(e),o>=1)return this._w=a,this._x=n,this._y=s,this._z=r,this;const l=1-o*o;if(l<=Number.EPSILON){const f=1-t;return this._w=f*a+t*this._w,this._x=f*n+t*this._x,this._y=f*s+t*this._y,this._z=f*r+t*this._z,this.normalize(),this}const c=Math.sqrt(l),h=Math.atan2(c,o),u=Math.sin((1-t)*h)/c,d=Math.sin(t*h)/c;return this._w=a*u+this._w*d,this._x=n*u+this._x*d,this._y=s*u+this._y*d,this._z=r*u+this._z*d,this._onChangeCallback(),this}slerpQuaternions(e,t,n){return this.copy(e).slerp(t,n)}random(){const e=2*Math.PI*Math.random(),t=2*Math.PI*Math.random(),n=Math.random(),s=Math.sqrt(1-n),r=Math.sqrt(n);return this.set(s*Math.sin(e),s*Math.cos(e),r*Math.sin(t),r*Math.cos(t))}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._w===this._w}fromArray(e,t=0){return this._x=e[t],this._y=e[t+1],this._z=e[t+2],this._w=e[t+3],this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._w,e}fromBufferAttribute(e,t){return this._x=e.getX(t),this._y=e.getY(t),this._z=e.getZ(t),this._w=e.getW(t),this._onChangeCallback(),this}toJSON(){return this.toArray()}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._w}}class H{constructor(e=0,t=0,n=0){H.prototype.isVector3=!0,this.x=e,this.y=t,this.z=n}set(e,t,n){return n===void 0&&(n=this.z),this.x=e,this.y=t,this.z=n,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this}multiplyVectors(e,t){return this.x=e.x*t.x,this.y=e.y*t.y,this.z=e.z*t.z,this}applyEuler(e){return this.applyQuaternion(Cu.setFromEuler(e))}applyAxisAngle(e,t){return this.applyQuaternion(Cu.setFromAxisAngle(e,t))}applyMatrix3(e){const t=this.x,n=this.y,s=this.z,r=e.elements;return this.x=r[0]*t+r[3]*n+r[6]*s,this.y=r[1]*t+r[4]*n+r[7]*s,this.z=r[2]*t+r[5]*n+r[8]*s,this}applyNormalMatrix(e){return this.applyMatrix3(e).normalize()}applyMatrix4(e){const t=this.x,n=this.y,s=this.z,r=e.elements,a=1/(r[3]*t+r[7]*n+r[11]*s+r[15]);return this.x=(r[0]*t+r[4]*n+r[8]*s+r[12])*a,this.y=(r[1]*t+r[5]*n+r[9]*s+r[13])*a,this.z=(r[2]*t+r[6]*n+r[10]*s+r[14])*a,this}applyQuaternion(e){const t=this.x,n=this.y,s=this.z,r=e.x,a=e.y,o=e.z,l=e.w,c=2*(a*s-o*n),h=2*(o*t-r*s),u=2*(r*n-a*t);return this.x=t+l*c+a*u-o*h,this.y=n+l*h+o*c-r*u,this.z=s+l*u+r*h-a*c,this}project(e){return this.applyMatrix4(e.matrixWorldInverse).applyMatrix4(e.projectionMatrix)}unproject(e){return this.applyMatrix4(e.projectionMatrixInverse).applyMatrix4(e.matrixWorld)}transformDirection(e){const t=this.x,n=this.y,s=this.z,r=e.elements;return this.x=r[0]*t+r[4]*n+r[8]*s,this.y=r[1]*t+r[5]*n+r[9]*s,this.z=r[2]*t+r[6]*n+r[10]*s,this.normalize()}divide(e){return this.x/=e.x,this.y/=e.y,this.z/=e.z,this}divideScalar(e){return this.multiplyScalar(1/e)}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this.z=Math.max(e.z,Math.min(t.z,this.z)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this.z=Math.max(e,Math.min(t,this.z)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this.z=e.z+(t.z-e.z)*n,this}cross(e){return this.crossVectors(this,e)}crossVectors(e,t){const n=e.x,s=e.y,r=e.z,a=t.x,o=t.y,l=t.z;return this.x=s*l-r*o,this.y=r*a-n*l,this.z=n*o-s*a,this}projectOnVector(e){const t=e.lengthSq();if(t===0)return this.set(0,0,0);const n=e.dot(this)/t;return this.copy(e).multiplyScalar(n)}projectOnPlane(e){return Ol.copy(this).projectOnVector(e),this.sub(Ol)}reflect(e){return this.sub(Ol.copy(e).multiplyScalar(2*this.dot(e)))}angleTo(e){const t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;const n=this.dot(e)/t;return Math.acos(Sn(n,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){const t=this.x-e.x,n=this.y-e.y,s=this.z-e.z;return t*t+n*n+s*s}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)+Math.abs(this.z-e.z)}setFromSpherical(e){return this.setFromSphericalCoords(e.radius,e.phi,e.theta)}setFromSphericalCoords(e,t,n){const s=Math.sin(t)*e;return this.x=s*Math.sin(n),this.y=Math.cos(t)*e,this.z=s*Math.cos(n),this}setFromCylindrical(e){return this.setFromCylindricalCoords(e.radius,e.theta,e.y)}setFromCylindricalCoords(e,t,n){return this.x=e*Math.sin(t),this.y=n,this.z=e*Math.cos(t),this}setFromMatrixPosition(e){const t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this}setFromMatrixScale(e){const t=this.setFromMatrixColumn(e,0).length(),n=this.setFromMatrixColumn(e,1).length(),s=this.setFromMatrixColumn(e,2).length();return this.x=t,this.y=n,this.z=s,this}setFromMatrixColumn(e,t){return this.fromArray(e.elements,t*4)}setFromMatrix3Column(e,t){return this.fromArray(e.elements,t*3)}setFromEuler(e){return this.x=e._x,this.y=e._y,this.z=e._z,this}setFromColor(e){return this.x=e.r,this.y=e.g,this.z=e.b,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this}randomDirection(){const e=Math.random()*Math.PI*2,t=Math.random()*2-1,n=Math.sqrt(1-t*t);return this.x=n*Math.cos(e),this.y=t,this.z=n*Math.sin(e),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z}}const Ol=new H,Cu=new ks;class Fa{constructor(e=new H(1/0,1/0,1/0),t=new H(-1/0,-1/0,-1/0)){this.isBox3=!0,this.min=e,this.max=t}set(e,t){return this.min.copy(e),this.max.copy(t),this}setFromArray(e){this.makeEmpty();for(let t=0,n=e.length;t<n;t+=3)this.expandByPoint(ti.fromArray(e,t));return this}setFromBufferAttribute(e){this.makeEmpty();for(let t=0,n=e.count;t<n;t++)this.expandByPoint(ti.fromBufferAttribute(e,t));return this}setFromPoints(e){this.makeEmpty();for(let t=0,n=e.length;t<n;t++)this.expandByPoint(e[t]);return this}setFromCenterAndSize(e,t){const n=ti.copy(t).multiplyScalar(.5);return this.min.copy(e).sub(n),this.max.copy(e).add(n),this}setFromObject(e,t=!1){return this.makeEmpty(),this.expandByObject(e,t)}clone(){return new this.constructor().copy(this)}copy(e){return this.min.copy(e.min),this.max.copy(e.max),this}makeEmpty(){return this.min.x=this.min.y=this.min.z=1/0,this.max.x=this.max.y=this.max.z=-1/0,this}isEmpty(){return this.max.x<this.min.x||this.max.y<this.min.y||this.max.z<this.min.z}getCenter(e){return this.isEmpty()?e.set(0,0,0):e.addVectors(this.min,this.max).multiplyScalar(.5)}getSize(e){return this.isEmpty()?e.set(0,0,0):e.subVectors(this.max,this.min)}expandByPoint(e){return this.min.min(e),this.max.max(e),this}expandByVector(e){return this.min.sub(e),this.max.add(e),this}expandByScalar(e){return this.min.addScalar(-e),this.max.addScalar(e),this}expandByObject(e,t=!1){e.updateWorldMatrix(!1,!1);const n=e.geometry;if(n!==void 0){const r=n.getAttribute("position");if(t===!0&&r!==void 0&&e.isInstancedMesh!==!0)for(let a=0,o=r.count;a<o;a++)e.isMesh===!0?e.getVertexPosition(a,ti):ti.fromBufferAttribute(r,a),ti.applyMatrix4(e.matrixWorld),this.expandByPoint(ti);else e.boundingBox!==void 0?(e.boundingBox===null&&e.computeBoundingBox(),ja.copy(e.boundingBox)):(n.boundingBox===null&&n.computeBoundingBox(),ja.copy(n.boundingBox)),ja.applyMatrix4(e.matrixWorld),this.union(ja)}const s=e.children;for(let r=0,a=s.length;r<a;r++)this.expandByObject(s[r],t);return this}containsPoint(e){return e.x>=this.min.x&&e.x<=this.max.x&&e.y>=this.min.y&&e.y<=this.max.y&&e.z>=this.min.z&&e.z<=this.max.z}containsBox(e){return this.min.x<=e.min.x&&e.max.x<=this.max.x&&this.min.y<=e.min.y&&e.max.y<=this.max.y&&this.min.z<=e.min.z&&e.max.z<=this.max.z}getParameter(e,t){return t.set((e.x-this.min.x)/(this.max.x-this.min.x),(e.y-this.min.y)/(this.max.y-this.min.y),(e.z-this.min.z)/(this.max.z-this.min.z))}intersectsBox(e){return e.max.x>=this.min.x&&e.min.x<=this.max.x&&e.max.y>=this.min.y&&e.min.y<=this.max.y&&e.max.z>=this.min.z&&e.min.z<=this.max.z}intersectsSphere(e){return this.clampPoint(e.center,ti),ti.distanceToSquared(e.center)<=e.radius*e.radius}intersectsPlane(e){let t,n;return e.normal.x>0?(t=e.normal.x*this.min.x,n=e.normal.x*this.max.x):(t=e.normal.x*this.max.x,n=e.normal.x*this.min.x),e.normal.y>0?(t+=e.normal.y*this.min.y,n+=e.normal.y*this.max.y):(t+=e.normal.y*this.max.y,n+=e.normal.y*this.min.y),e.normal.z>0?(t+=e.normal.z*this.min.z,n+=e.normal.z*this.max.z):(t+=e.normal.z*this.max.z,n+=e.normal.z*this.min.z),t<=-e.constant&&n>=-e.constant}intersectsTriangle(e){if(this.isEmpty())return!1;this.getCenter(ua),Ka.subVectors(this.max,ua),sr.subVectors(e.a,ua),rr.subVectors(e.b,ua),ar.subVectors(e.c,ua),Zi.subVectors(rr,sr),Ji.subVectors(ar,rr),Ms.subVectors(sr,ar);let t=[0,-Zi.z,Zi.y,0,-Ji.z,Ji.y,0,-Ms.z,Ms.y,Zi.z,0,-Zi.x,Ji.z,0,-Ji.x,Ms.z,0,-Ms.x,-Zi.y,Zi.x,0,-Ji.y,Ji.x,0,-Ms.y,Ms.x,0];return!Bl(t,sr,rr,ar,Ka)||(t=[1,0,0,0,1,0,0,0,1],!Bl(t,sr,rr,ar,Ka))?!1:(Za.crossVectors(Zi,Ji),t=[Za.x,Za.y,Za.z],Bl(t,sr,rr,ar,Ka))}clampPoint(e,t){return t.copy(e).clamp(this.min,this.max)}distanceToPoint(e){return this.clampPoint(e,ti).distanceTo(e)}getBoundingSphere(e){return this.isEmpty()?e.makeEmpty():(this.getCenter(e.center),e.radius=this.getSize(ti).length()*.5),e}intersect(e){return this.min.max(e.min),this.max.min(e.max),this.isEmpty()&&this.makeEmpty(),this}union(e){return this.min.min(e.min),this.max.max(e.max),this}applyMatrix4(e){return this.isEmpty()?this:(Pi[0].set(this.min.x,this.min.y,this.min.z).applyMatrix4(e),Pi[1].set(this.min.x,this.min.y,this.max.z).applyMatrix4(e),Pi[2].set(this.min.x,this.max.y,this.min.z).applyMatrix4(e),Pi[3].set(this.min.x,this.max.y,this.max.z).applyMatrix4(e),Pi[4].set(this.max.x,this.min.y,this.min.z).applyMatrix4(e),Pi[5].set(this.max.x,this.min.y,this.max.z).applyMatrix4(e),Pi[6].set(this.max.x,this.max.y,this.min.z).applyMatrix4(e),Pi[7].set(this.max.x,this.max.y,this.max.z).applyMatrix4(e),this.setFromPoints(Pi),this)}translate(e){return this.min.add(e),this.max.add(e),this}equals(e){return e.min.equals(this.min)&&e.max.equals(this.max)}}const Pi=[new H,new H,new H,new H,new H,new H,new H,new H],ti=new H,ja=new Fa,sr=new H,rr=new H,ar=new H,Zi=new H,Ji=new H,Ms=new H,ua=new H,Ka=new H,Za=new H,Ss=new H;function Bl(i,e,t,n,s){for(let r=0,a=i.length-3;r<=a;r+=3){Ss.fromArray(i,r);const o=s.x*Math.abs(Ss.x)+s.y*Math.abs(Ss.y)+s.z*Math.abs(Ss.z),l=e.dot(Ss),c=t.dot(Ss),h=n.dot(Ss);if(Math.max(-Math.max(l,c,h),Math.min(l,c,h))>o)return!1}return!0}const Gg=new Fa,da=new H,zl=new H;class Oa{constructor(e=new H,t=-1){this.isSphere=!0,this.center=e,this.radius=t}set(e,t){return this.center.copy(e),this.radius=t,this}setFromPoints(e,t){const n=this.center;t!==void 0?n.copy(t):Gg.setFromPoints(e).getCenter(n);let s=0;for(let r=0,a=e.length;r<a;r++)s=Math.max(s,n.distanceToSquared(e[r]));return this.radius=Math.sqrt(s),this}copy(e){return this.center.copy(e.center),this.radius=e.radius,this}isEmpty(){return this.radius<0}makeEmpty(){return this.center.set(0,0,0),this.radius=-1,this}containsPoint(e){return e.distanceToSquared(this.center)<=this.radius*this.radius}distanceToPoint(e){return e.distanceTo(this.center)-this.radius}intersectsSphere(e){const t=this.radius+e.radius;return e.center.distanceToSquared(this.center)<=t*t}intersectsBox(e){return e.intersectsSphere(this)}intersectsPlane(e){return Math.abs(e.distanceToPoint(this.center))<=this.radius}clampPoint(e,t){const n=this.center.distanceToSquared(e);return t.copy(e),n>this.radius*this.radius&&(t.sub(this.center).normalize(),t.multiplyScalar(this.radius).add(this.center)),t}getBoundingBox(e){return this.isEmpty()?(e.makeEmpty(),e):(e.set(this.center,this.center),e.expandByScalar(this.radius),e)}applyMatrix4(e){return this.center.applyMatrix4(e),this.radius=this.radius*e.getMaxScaleOnAxis(),this}translate(e){return this.center.add(e),this}expandByPoint(e){if(this.isEmpty())return this.center.copy(e),this.radius=0,this;da.subVectors(e,this.center);const t=da.lengthSq();if(t>this.radius*this.radius){const n=Math.sqrt(t),s=(n-this.radius)*.5;this.center.addScaledVector(da,s/n),this.radius+=s}return this}union(e){return e.isEmpty()?this:this.isEmpty()?(this.copy(e),this):(this.center.equals(e.center)===!0?this.radius=Math.max(this.radius,e.radius):(zl.subVectors(e.center,this.center).setLength(e.radius),this.expandByPoint(da.copy(e.center).add(zl)),this.expandByPoint(da.copy(e.center).sub(zl))),this)}equals(e){return e.center.equals(this.center)&&e.radius===this.radius}clone(){return new this.constructor().copy(this)}}const Li=new H,kl=new H,Ja=new H,Qi=new H,Hl=new H,Qa=new H,Vl=new H;class Ba{constructor(e=new H,t=new H(0,0,-1)){this.origin=e,this.direction=t}set(e,t){return this.origin.copy(e),this.direction.copy(t),this}copy(e){return this.origin.copy(e.origin),this.direction.copy(e.direction),this}at(e,t){return t.copy(this.origin).addScaledVector(this.direction,e)}lookAt(e){return this.direction.copy(e).sub(this.origin).normalize(),this}recast(e){return this.origin.copy(this.at(e,Li)),this}closestPointToPoint(e,t){t.subVectors(e,this.origin);const n=t.dot(this.direction);return n<0?t.copy(this.origin):t.copy(this.origin).addScaledVector(this.direction,n)}distanceToPoint(e){return Math.sqrt(this.distanceSqToPoint(e))}distanceSqToPoint(e){const t=Li.subVectors(e,this.origin).dot(this.direction);return t<0?this.origin.distanceToSquared(e):(Li.copy(this.origin).addScaledVector(this.direction,t),Li.distanceToSquared(e))}distanceSqToSegment(e,t,n,s){kl.copy(e).add(t).multiplyScalar(.5),Ja.copy(t).sub(e).normalize(),Qi.copy(this.origin).sub(kl);const r=e.distanceTo(t)*.5,a=-this.direction.dot(Ja),o=Qi.dot(this.direction),l=-Qi.dot(Ja),c=Qi.lengthSq(),h=Math.abs(1-a*a);let u,d,f,g;if(h>0)if(u=a*l-o,d=a*o-l,g=r*h,u>=0)if(d>=-g)if(d<=g){const _=1/h;u*=_,d*=_,f=u*(u+a*d+2*o)+d*(a*u+d+2*l)+c}else d=r,u=Math.max(0,-(a*d+o)),f=-u*u+d*(d+2*l)+c;else d=-r,u=Math.max(0,-(a*d+o)),f=-u*u+d*(d+2*l)+c;else d<=-g?(u=Math.max(0,-(-a*r+o)),d=u>0?-r:Math.min(Math.max(-r,-l),r),f=-u*u+d*(d+2*l)+c):d<=g?(u=0,d=Math.min(Math.max(-r,-l),r),f=d*(d+2*l)+c):(u=Math.max(0,-(a*r+o)),d=u>0?r:Math.min(Math.max(-r,-l),r),f=-u*u+d*(d+2*l)+c);else d=a>0?-r:r,u=Math.max(0,-(a*d+o)),f=-u*u+d*(d+2*l)+c;return n&&n.copy(this.origin).addScaledVector(this.direction,u),s&&s.copy(kl).addScaledVector(Ja,d),f}intersectSphere(e,t){Li.subVectors(e.center,this.origin);const n=Li.dot(this.direction),s=Li.dot(Li)-n*n,r=e.radius*e.radius;if(s>r)return null;const a=Math.sqrt(r-s),o=n-a,l=n+a;return l<0?null:o<0?this.at(l,t):this.at(o,t)}intersectsSphere(e){return this.distanceSqToPoint(e.center)<=e.radius*e.radius}distanceToPlane(e){const t=e.normal.dot(this.direction);if(t===0)return e.distanceToPoint(this.origin)===0?0:null;const n=-(this.origin.dot(e.normal)+e.constant)/t;return n>=0?n:null}intersectPlane(e,t){const n=this.distanceToPlane(e);return n===null?null:this.at(n,t)}intersectsPlane(e){const t=e.distanceToPoint(this.origin);return t===0||e.normal.dot(this.direction)*t<0}intersectBox(e,t){let n,s,r,a,o,l;const c=1/this.direction.x,h=1/this.direction.y,u=1/this.direction.z,d=this.origin;return c>=0?(n=(e.min.x-d.x)*c,s=(e.max.x-d.x)*c):(n=(e.max.x-d.x)*c,s=(e.min.x-d.x)*c),h>=0?(r=(e.min.y-d.y)*h,a=(e.max.y-d.y)*h):(r=(e.max.y-d.y)*h,a=(e.min.y-d.y)*h),n>a||r>s||((r>n||isNaN(n))&&(n=r),(a<s||isNaN(s))&&(s=a),u>=0?(o=(e.min.z-d.z)*u,l=(e.max.z-d.z)*u):(o=(e.max.z-d.z)*u,l=(e.min.z-d.z)*u),n>l||o>s)||((o>n||n!==n)&&(n=o),(l<s||s!==s)&&(s=l),s<0)?null:this.at(n>=0?n:s,t)}intersectsBox(e){return this.intersectBox(e,Li)!==null}intersectTriangle(e,t,n,s,r){Hl.subVectors(t,e),Qa.subVectors(n,e),Vl.crossVectors(Hl,Qa);let a=this.direction.dot(Vl),o;if(a>0){if(s)return null;o=1}else if(a<0)o=-1,a=-a;else return null;Qi.subVectors(this.origin,e);const l=o*this.direction.dot(Qa.crossVectors(Qi,Qa));if(l<0)return null;const c=o*this.direction.dot(Hl.cross(Qi));if(c<0||l+c>a)return null;const h=-o*Qi.dot(Vl);return h<0?null:this.at(h/a,r)}applyMatrix4(e){return this.origin.applyMatrix4(e),this.direction.transformDirection(e),this}equals(e){return e.origin.equals(this.origin)&&e.direction.equals(this.direction)}clone(){return new this.constructor().copy(this)}}class Bt{constructor(e,t,n,s,r,a,o,l,c,h,u,d,f,g,_,m){Bt.prototype.isMatrix4=!0,this.elements=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],e!==void 0&&this.set(e,t,n,s,r,a,o,l,c,h,u,d,f,g,_,m)}set(e,t,n,s,r,a,o,l,c,h,u,d,f,g,_,m){const p=this.elements;return p[0]=e,p[4]=t,p[8]=n,p[12]=s,p[1]=r,p[5]=a,p[9]=o,p[13]=l,p[2]=c,p[6]=h,p[10]=u,p[14]=d,p[3]=f,p[7]=g,p[11]=_,p[15]=m,this}identity(){return this.set(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1),this}clone(){return new Bt().fromArray(this.elements)}copy(e){const t=this.elements,n=e.elements;return t[0]=n[0],t[1]=n[1],t[2]=n[2],t[3]=n[3],t[4]=n[4],t[5]=n[5],t[6]=n[6],t[7]=n[7],t[8]=n[8],t[9]=n[9],t[10]=n[10],t[11]=n[11],t[12]=n[12],t[13]=n[13],t[14]=n[14],t[15]=n[15],this}copyPosition(e){const t=this.elements,n=e.elements;return t[12]=n[12],t[13]=n[13],t[14]=n[14],this}setFromMatrix3(e){const t=e.elements;return this.set(t[0],t[3],t[6],0,t[1],t[4],t[7],0,t[2],t[5],t[8],0,0,0,0,1),this}extractBasis(e,t,n){return e.setFromMatrixColumn(this,0),t.setFromMatrixColumn(this,1),n.setFromMatrixColumn(this,2),this}makeBasis(e,t,n){return this.set(e.x,t.x,n.x,0,e.y,t.y,n.y,0,e.z,t.z,n.z,0,0,0,0,1),this}extractRotation(e){const t=this.elements,n=e.elements,s=1/or.setFromMatrixColumn(e,0).length(),r=1/or.setFromMatrixColumn(e,1).length(),a=1/or.setFromMatrixColumn(e,2).length();return t[0]=n[0]*s,t[1]=n[1]*s,t[2]=n[2]*s,t[3]=0,t[4]=n[4]*r,t[5]=n[5]*r,t[6]=n[6]*r,t[7]=0,t[8]=n[8]*a,t[9]=n[9]*a,t[10]=n[10]*a,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromEuler(e){const t=this.elements,n=e.x,s=e.y,r=e.z,a=Math.cos(n),o=Math.sin(n),l=Math.cos(s),c=Math.sin(s),h=Math.cos(r),u=Math.sin(r);if(e.order==="XYZ"){const d=a*h,f=a*u,g=o*h,_=o*u;t[0]=l*h,t[4]=-l*u,t[8]=c,t[1]=f+g*c,t[5]=d-_*c,t[9]=-o*l,t[2]=_-d*c,t[6]=g+f*c,t[10]=a*l}else if(e.order==="YXZ"){const d=l*h,f=l*u,g=c*h,_=c*u;t[0]=d+_*o,t[4]=g*o-f,t[8]=a*c,t[1]=a*u,t[5]=a*h,t[9]=-o,t[2]=f*o-g,t[6]=_+d*o,t[10]=a*l}else if(e.order==="ZXY"){const d=l*h,f=l*u,g=c*h,_=c*u;t[0]=d-_*o,t[4]=-a*u,t[8]=g+f*o,t[1]=f+g*o,t[5]=a*h,t[9]=_-d*o,t[2]=-a*c,t[6]=o,t[10]=a*l}else if(e.order==="ZYX"){const d=a*h,f=a*u,g=o*h,_=o*u;t[0]=l*h,t[4]=g*c-f,t[8]=d*c+_,t[1]=l*u,t[5]=_*c+d,t[9]=f*c-g,t[2]=-c,t[6]=o*l,t[10]=a*l}else if(e.order==="YZX"){const d=a*l,f=a*c,g=o*l,_=o*c;t[0]=l*h,t[4]=_-d*u,t[8]=g*u+f,t[1]=u,t[5]=a*h,t[9]=-o*h,t[2]=-c*h,t[6]=f*u+g,t[10]=d-_*u}else if(e.order==="XZY"){const d=a*l,f=a*c,g=o*l,_=o*c;t[0]=l*h,t[4]=-u,t[8]=c*h,t[1]=d*u+_,t[5]=a*h,t[9]=f*u-g,t[2]=g*u-f,t[6]=o*h,t[10]=_*u+d}return t[3]=0,t[7]=0,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromQuaternion(e){return this.compose(Wg,e,Xg)}lookAt(e,t,n){const s=this.elements;return On.subVectors(e,t),On.lengthSq()===0&&(On.z=1),On.normalize(),es.crossVectors(n,On),es.lengthSq()===0&&(Math.abs(n.z)===1?On.x+=1e-4:On.z+=1e-4,On.normalize(),es.crossVectors(n,On)),es.normalize(),eo.crossVectors(On,es),s[0]=es.x,s[4]=eo.x,s[8]=On.x,s[1]=es.y,s[5]=eo.y,s[9]=On.y,s[2]=es.z,s[6]=eo.z,s[10]=On.z,this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){const n=e.elements,s=t.elements,r=this.elements,a=n[0],o=n[4],l=n[8],c=n[12],h=n[1],u=n[5],d=n[9],f=n[13],g=n[2],_=n[6],m=n[10],p=n[14],S=n[3],y=n[7],w=n[11],O=n[15],A=s[0],C=s[4],F=s[8],b=s[12],x=s[1],P=s[5],K=s[9],k=s[13],Z=s[2],q=s[6],ee=s[10],Y=s[14],ne=s[3],ge=s[7],de=s[11],xe=s[15];return r[0]=a*A+o*x+l*Z+c*ne,r[4]=a*C+o*P+l*q+c*ge,r[8]=a*F+o*K+l*ee+c*de,r[12]=a*b+o*k+l*Y+c*xe,r[1]=h*A+u*x+d*Z+f*ne,r[5]=h*C+u*P+d*q+f*ge,r[9]=h*F+u*K+d*ee+f*de,r[13]=h*b+u*k+d*Y+f*xe,r[2]=g*A+_*x+m*Z+p*ne,r[6]=g*C+_*P+m*q+p*ge,r[10]=g*F+_*K+m*ee+p*de,r[14]=g*b+_*k+m*Y+p*xe,r[3]=S*A+y*x+w*Z+O*ne,r[7]=S*C+y*P+w*q+O*ge,r[11]=S*F+y*K+w*ee+O*de,r[15]=S*b+y*k+w*Y+O*xe,this}multiplyScalar(e){const t=this.elements;return t[0]*=e,t[4]*=e,t[8]*=e,t[12]*=e,t[1]*=e,t[5]*=e,t[9]*=e,t[13]*=e,t[2]*=e,t[6]*=e,t[10]*=e,t[14]*=e,t[3]*=e,t[7]*=e,t[11]*=e,t[15]*=e,this}determinant(){const e=this.elements,t=e[0],n=e[4],s=e[8],r=e[12],a=e[1],o=e[5],l=e[9],c=e[13],h=e[2],u=e[6],d=e[10],f=e[14],g=e[3],_=e[7],m=e[11],p=e[15];return g*(+r*l*u-s*c*u-r*o*d+n*c*d+s*o*f-n*l*f)+_*(+t*l*f-t*c*d+r*a*d-s*a*f+s*c*h-r*l*h)+m*(+t*c*u-t*o*f-r*a*u+n*a*f+r*o*h-n*c*h)+p*(-s*o*h-t*l*u+t*o*d+s*a*u-n*a*d+n*l*h)}transpose(){const e=this.elements;let t;return t=e[1],e[1]=e[4],e[4]=t,t=e[2],e[2]=e[8],e[8]=t,t=e[6],e[6]=e[9],e[9]=t,t=e[3],e[3]=e[12],e[12]=t,t=e[7],e[7]=e[13],e[13]=t,t=e[11],e[11]=e[14],e[14]=t,this}setPosition(e,t,n){const s=this.elements;return e.isVector3?(s[12]=e.x,s[13]=e.y,s[14]=e.z):(s[12]=e,s[13]=t,s[14]=n),this}invert(){const e=this.elements,t=e[0],n=e[1],s=e[2],r=e[3],a=e[4],o=e[5],l=e[6],c=e[7],h=e[8],u=e[9],d=e[10],f=e[11],g=e[12],_=e[13],m=e[14],p=e[15],S=u*m*c-_*d*c+_*l*f-o*m*f-u*l*p+o*d*p,y=g*d*c-h*m*c-g*l*f+a*m*f+h*l*p-a*d*p,w=h*_*c-g*u*c+g*o*f-a*_*f-h*o*p+a*u*p,O=g*u*l-h*_*l-g*o*d+a*_*d+h*o*m-a*u*m,A=t*S+n*y+s*w+r*O;if(A===0)return this.set(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);const C=1/A;return e[0]=S*C,e[1]=(_*d*r-u*m*r-_*s*f+n*m*f+u*s*p-n*d*p)*C,e[2]=(o*m*r-_*l*r+_*s*c-n*m*c-o*s*p+n*l*p)*C,e[3]=(u*l*r-o*d*r-u*s*c+n*d*c+o*s*f-n*l*f)*C,e[4]=y*C,e[5]=(h*m*r-g*d*r+g*s*f-t*m*f-h*s*p+t*d*p)*C,e[6]=(g*l*r-a*m*r-g*s*c+t*m*c+a*s*p-t*l*p)*C,e[7]=(a*d*r-h*l*r+h*s*c-t*d*c-a*s*f+t*l*f)*C,e[8]=w*C,e[9]=(g*u*r-h*_*r-g*n*f+t*_*f+h*n*p-t*u*p)*C,e[10]=(a*_*r-g*o*r+g*n*c-t*_*c-a*n*p+t*o*p)*C,e[11]=(h*o*r-a*u*r-h*n*c+t*u*c+a*n*f-t*o*f)*C,e[12]=O*C,e[13]=(h*_*s-g*u*s+g*n*d-t*_*d-h*n*m+t*u*m)*C,e[14]=(g*o*s-a*_*s-g*n*l+t*_*l+a*n*m-t*o*m)*C,e[15]=(a*u*s-h*o*s+h*n*l-t*u*l-a*n*d+t*o*d)*C,this}scale(e){const t=this.elements,n=e.x,s=e.y,r=e.z;return t[0]*=n,t[4]*=s,t[8]*=r,t[1]*=n,t[5]*=s,t[9]*=r,t[2]*=n,t[6]*=s,t[10]*=r,t[3]*=n,t[7]*=s,t[11]*=r,this}getMaxScaleOnAxis(){const e=this.elements,t=e[0]*e[0]+e[1]*e[1]+e[2]*e[2],n=e[4]*e[4]+e[5]*e[5]+e[6]*e[6],s=e[8]*e[8]+e[9]*e[9]+e[10]*e[10];return Math.sqrt(Math.max(t,n,s))}makeTranslation(e,t,n){return e.isVector3?this.set(1,0,0,e.x,0,1,0,e.y,0,0,1,e.z,0,0,0,1):this.set(1,0,0,e,0,1,0,t,0,0,1,n,0,0,0,1),this}makeRotationX(e){const t=Math.cos(e),n=Math.sin(e);return this.set(1,0,0,0,0,t,-n,0,0,n,t,0,0,0,0,1),this}makeRotationY(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,0,n,0,0,1,0,0,-n,0,t,0,0,0,0,1),this}makeRotationZ(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,-n,0,0,n,t,0,0,0,0,1,0,0,0,0,1),this}makeRotationAxis(e,t){const n=Math.cos(t),s=Math.sin(t),r=1-n,a=e.x,o=e.y,l=e.z,c=r*a,h=r*o;return this.set(c*a+n,c*o-s*l,c*l+s*o,0,c*o+s*l,h*o+n,h*l-s*a,0,c*l-s*o,h*l+s*a,r*l*l+n,0,0,0,0,1),this}makeScale(e,t,n){return this.set(e,0,0,0,0,t,0,0,0,0,n,0,0,0,0,1),this}makeShear(e,t,n,s,r,a){return this.set(1,n,r,0,e,1,a,0,t,s,1,0,0,0,0,1),this}compose(e,t,n){const s=this.elements,r=t._x,a=t._y,o=t._z,l=t._w,c=r+r,h=a+a,u=o+o,d=r*c,f=r*h,g=r*u,_=a*h,m=a*u,p=o*u,S=l*c,y=l*h,w=l*u,O=n.x,A=n.y,C=n.z;return s[0]=(1-(_+p))*O,s[1]=(f+w)*O,s[2]=(g-y)*O,s[3]=0,s[4]=(f-w)*A,s[5]=(1-(d+p))*A,s[6]=(m+S)*A,s[7]=0,s[8]=(g+y)*C,s[9]=(m-S)*C,s[10]=(1-(d+_))*C,s[11]=0,s[12]=e.x,s[13]=e.y,s[14]=e.z,s[15]=1,this}decompose(e,t,n){const s=this.elements;let r=or.set(s[0],s[1],s[2]).length();const a=or.set(s[4],s[5],s[6]).length(),o=or.set(s[8],s[9],s[10]).length();this.determinant()<0&&(r=-r),e.x=s[12],e.y=s[13],e.z=s[14],ni.copy(this);const c=1/r,h=1/a,u=1/o;return ni.elements[0]*=c,ni.elements[1]*=c,ni.elements[2]*=c,ni.elements[4]*=h,ni.elements[5]*=h,ni.elements[6]*=h,ni.elements[8]*=u,ni.elements[9]*=u,ni.elements[10]*=u,t.setFromRotationMatrix(ni),n.x=r,n.y=a,n.z=o,this}makePerspective(e,t,n,s,r,a,o=Bi){const l=this.elements,c=2*r/(t-e),h=2*r/(n-s),u=(t+e)/(t-e),d=(n+s)/(n-s);let f,g;if(o===Bi)f=-(a+r)/(a-r),g=-2*a*r/(a-r);else if(o===Xo)f=-a/(a-r),g=-a*r/(a-r);else throw new Error("THREE.Matrix4.makePerspective(): Invalid coordinate system: "+o);return l[0]=c,l[4]=0,l[8]=u,l[12]=0,l[1]=0,l[5]=h,l[9]=d,l[13]=0,l[2]=0,l[6]=0,l[10]=f,l[14]=g,l[3]=0,l[7]=0,l[11]=-1,l[15]=0,this}makeOrthographic(e,t,n,s,r,a,o=Bi){const l=this.elements,c=1/(t-e),h=1/(n-s),u=1/(a-r),d=(t+e)*c,f=(n+s)*h;let g,_;if(o===Bi)g=(a+r)*u,_=-2*u;else if(o===Xo)g=r*u,_=-1*u;else throw new Error("THREE.Matrix4.makeOrthographic(): Invalid coordinate system: "+o);return l[0]=2*c,l[4]=0,l[8]=0,l[12]=-d,l[1]=0,l[5]=2*h,l[9]=0,l[13]=-f,l[2]=0,l[6]=0,l[10]=_,l[14]=-g,l[3]=0,l[7]=0,l[11]=0,l[15]=1,this}equals(e){const t=this.elements,n=e.elements;for(let s=0;s<16;s++)if(t[s]!==n[s])return!1;return!0}fromArray(e,t=0){for(let n=0;n<16;n++)this.elements[n]=e[n+t];return this}toArray(e=[],t=0){const n=this.elements;return e[t]=n[0],e[t+1]=n[1],e[t+2]=n[2],e[t+3]=n[3],e[t+4]=n[4],e[t+5]=n[5],e[t+6]=n[6],e[t+7]=n[7],e[t+8]=n[8],e[t+9]=n[9],e[t+10]=n[10],e[t+11]=n[11],e[t+12]=n[12],e[t+13]=n[13],e[t+14]=n[14],e[t+15]=n[15],e}}const or=new H,ni=new Bt,Wg=new H(0,0,0),Xg=new H(1,1,1),es=new H,eo=new H,On=new H,Pu=new Bt,Lu=new ks;class Si{constructor(e=0,t=0,n=0,s=Si.DEFAULT_ORDER){this.isEuler=!0,this._x=e,this._y=t,this._z=n,this._order=s}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get order(){return this._order}set order(e){this._order=e,this._onChangeCallback()}set(e,t,n,s=this._order){return this._x=e,this._y=t,this._z=n,this._order=s,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._order)}copy(e){return this._x=e._x,this._y=e._y,this._z=e._z,this._order=e._order,this._onChangeCallback(),this}setFromRotationMatrix(e,t=this._order,n=!0){const s=e.elements,r=s[0],a=s[4],o=s[8],l=s[1],c=s[5],h=s[9],u=s[2],d=s[6],f=s[10];switch(t){case"XYZ":this._y=Math.asin(Sn(o,-1,1)),Math.abs(o)<.9999999?(this._x=Math.atan2(-h,f),this._z=Math.atan2(-a,r)):(this._x=Math.atan2(d,c),this._z=0);break;case"YXZ":this._x=Math.asin(-Sn(h,-1,1)),Math.abs(h)<.9999999?(this._y=Math.atan2(o,f),this._z=Math.atan2(l,c)):(this._y=Math.atan2(-u,r),this._z=0);break;case"ZXY":this._x=Math.asin(Sn(d,-1,1)),Math.abs(d)<.9999999?(this._y=Math.atan2(-u,f),this._z=Math.atan2(-a,c)):(this._y=0,this._z=Math.atan2(l,r));break;case"ZYX":this._y=Math.asin(-Sn(u,-1,1)),Math.abs(u)<.9999999?(this._x=Math.atan2(d,f),this._z=Math.atan2(l,r)):(this._x=0,this._z=Math.atan2(-a,c));break;case"YZX":this._z=Math.asin(Sn(l,-1,1)),Math.abs(l)<.9999999?(this._x=Math.atan2(-h,c),this._y=Math.atan2(-u,r)):(this._x=0,this._y=Math.atan2(o,f));break;case"XZY":this._z=Math.asin(-Sn(a,-1,1)),Math.abs(a)<.9999999?(this._x=Math.atan2(d,c),this._y=Math.atan2(o,r)):(this._x=Math.atan2(-h,f),this._y=0);break;default:console.warn("THREE.Euler: .setFromRotationMatrix() encountered an unknown order: "+t)}return this._order=t,n===!0&&this._onChangeCallback(),this}setFromQuaternion(e,t,n){return Pu.makeRotationFromQuaternion(e),this.setFromRotationMatrix(Pu,t,n)}setFromVector3(e,t=this._order){return this.set(e.x,e.y,e.z,t)}reorder(e){return Lu.setFromEuler(this),this.setFromQuaternion(Lu,e)}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._order===this._order}fromArray(e){return this._x=e[0],this._y=e[1],this._z=e[2],e[3]!==void 0&&(this._order=e[3]),this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._order,e}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._order}}Si.DEFAULT_ORDER="XYZ";class bh{constructor(){this.mask=1}set(e){this.mask=(1<<e|0)>>>0}enable(e){this.mask|=1<<e|0}enableAll(){this.mask=-1}toggle(e){this.mask^=1<<e|0}disable(e){this.mask&=~(1<<e|0)}disableAll(){this.mask=0}test(e){return(this.mask&e.mask)!==0}isEnabled(e){return(this.mask&(1<<e|0))!==0}}let qg=0;const Du=new H,lr=new ks,Di=new Bt,to=new H,fa=new H,$g=new H,Yg=new ks,Iu=new H(1,0,0),Uu=new H(0,1,0),Nu=new H(0,0,1),Fu={type:"added"},jg={type:"removed"},cr={type:"childadded",child:null},Gl={type:"childremoved",child:null};class Qt extends Kr{constructor(){super(),this.isObject3D=!0,Object.defineProperty(this,"id",{value:qg++}),this.uuid=ki(),this.name="",this.type="Object3D",this.parent=null,this.children=[],this.up=Qt.DEFAULT_UP.clone();const e=new H,t=new Si,n=new ks,s=new H(1,1,1);function r(){n.setFromEuler(t,!1)}function a(){t.setFromQuaternion(n,void 0,!1)}t._onChange(r),n._onChange(a),Object.defineProperties(this,{position:{configurable:!0,enumerable:!0,value:e},rotation:{configurable:!0,enumerable:!0,value:t},quaternion:{configurable:!0,enumerable:!0,value:n},scale:{configurable:!0,enumerable:!0,value:s},modelViewMatrix:{value:new Bt},normalMatrix:{value:new at}}),this.matrix=new Bt,this.matrixWorld=new Bt,this.matrixAutoUpdate=Qt.DEFAULT_MATRIX_AUTO_UPDATE,this.matrixWorldAutoUpdate=Qt.DEFAULT_MATRIX_WORLD_AUTO_UPDATE,this.matrixWorldNeedsUpdate=!1,this.layers=new bh,this.visible=!0,this.castShadow=!1,this.receiveShadow=!1,this.frustumCulled=!0,this.renderOrder=0,this.animations=[],this.userData={}}onBeforeShadow(){}onAfterShadow(){}onBeforeRender(){}onAfterRender(){}applyMatrix4(e){this.matrixAutoUpdate&&this.updateMatrix(),this.matrix.premultiply(e),this.matrix.decompose(this.position,this.quaternion,this.scale)}applyQuaternion(e){return this.quaternion.premultiply(e),this}setRotationFromAxisAngle(e,t){this.quaternion.setFromAxisAngle(e,t)}setRotationFromEuler(e){this.quaternion.setFromEuler(e,!0)}setRotationFromMatrix(e){this.quaternion.setFromRotationMatrix(e)}setRotationFromQuaternion(e){this.quaternion.copy(e)}rotateOnAxis(e,t){return lr.setFromAxisAngle(e,t),this.quaternion.multiply(lr),this}rotateOnWorldAxis(e,t){return lr.setFromAxisAngle(e,t),this.quaternion.premultiply(lr),this}rotateX(e){return this.rotateOnAxis(Iu,e)}rotateY(e){return this.rotateOnAxis(Uu,e)}rotateZ(e){return this.rotateOnAxis(Nu,e)}translateOnAxis(e,t){return Du.copy(e).applyQuaternion(this.quaternion),this.position.add(Du.multiplyScalar(t)),this}translateX(e){return this.translateOnAxis(Iu,e)}translateY(e){return this.translateOnAxis(Uu,e)}translateZ(e){return this.translateOnAxis(Nu,e)}localToWorld(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(this.matrixWorld)}worldToLocal(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(Di.copy(this.matrixWorld).invert())}lookAt(e,t,n){e.isVector3?to.copy(e):to.set(e,t,n);const s=this.parent;this.updateWorldMatrix(!0,!1),fa.setFromMatrixPosition(this.matrixWorld),this.isCamera||this.isLight?Di.lookAt(fa,to,this.up):Di.lookAt(to,fa,this.up),this.quaternion.setFromRotationMatrix(Di),s&&(Di.extractRotation(s.matrixWorld),lr.setFromRotationMatrix(Di),this.quaternion.premultiply(lr.invert()))}add(e){if(arguments.length>1){for(let t=0;t<arguments.length;t++)this.add(arguments[t]);return this}return e===this?(console.error("THREE.Object3D.add: object can't be added as a child of itself.",e),this):(e&&e.isObject3D?(e.removeFromParent(),e.parent=this,this.children.push(e),e.dispatchEvent(Fu),cr.child=e,this.dispatchEvent(cr),cr.child=null):console.error("THREE.Object3D.add: object not an instance of THREE.Object3D.",e),this)}remove(e){if(arguments.length>1){for(let n=0;n<arguments.length;n++)this.remove(arguments[n]);return this}const t=this.children.indexOf(e);return t!==-1&&(e.parent=null,this.children.splice(t,1),e.dispatchEvent(jg),Gl.child=e,this.dispatchEvent(Gl),Gl.child=null),this}removeFromParent(){const e=this.parent;return e!==null&&e.remove(this),this}clear(){return this.remove(...this.children)}attach(e){return this.updateWorldMatrix(!0,!1),Di.copy(this.matrixWorld).invert(),e.parent!==null&&(e.parent.updateWorldMatrix(!0,!1),Di.multiply(e.parent.matrixWorld)),e.applyMatrix4(Di),e.removeFromParent(),e.parent=this,this.children.push(e),e.updateWorldMatrix(!1,!0),e.dispatchEvent(Fu),cr.child=e,this.dispatchEvent(cr),cr.child=null,this}getObjectById(e){return this.getObjectByProperty("id",e)}getObjectByName(e){return this.getObjectByProperty("name",e)}getObjectByProperty(e,t){if(this[e]===t)return this;for(let n=0,s=this.children.length;n<s;n++){const a=this.children[n].getObjectByProperty(e,t);if(a!==void 0)return a}}getObjectsByProperty(e,t,n=[]){this[e]===t&&n.push(this);const s=this.children;for(let r=0,a=s.length;r<a;r++)s[r].getObjectsByProperty(e,t,n);return n}getWorldPosition(e){return this.updateWorldMatrix(!0,!1),e.setFromMatrixPosition(this.matrixWorld)}getWorldQuaternion(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(fa,e,$g),e}getWorldScale(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(fa,Yg,e),e}getWorldDirection(e){this.updateWorldMatrix(!0,!1);const t=this.matrixWorld.elements;return e.set(t[8],t[9],t[10]).normalize()}raycast(){}traverse(e){e(this);const t=this.children;for(let n=0,s=t.length;n<s;n++)t[n].traverse(e)}traverseVisible(e){if(this.visible===!1)return;e(this);const t=this.children;for(let n=0,s=t.length;n<s;n++)t[n].traverseVisible(e)}traverseAncestors(e){const t=this.parent;t!==null&&(e(t),t.traverseAncestors(e))}updateMatrix(){this.matrix.compose(this.position,this.quaternion,this.scale),this.matrixWorldNeedsUpdate=!0}updateMatrixWorld(e){this.matrixAutoUpdate&&this.updateMatrix(),(this.matrixWorldNeedsUpdate||e)&&(this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),this.matrixWorldNeedsUpdate=!1,e=!0);const t=this.children;for(let n=0,s=t.length;n<s;n++)t[n].updateMatrixWorld(e)}updateWorldMatrix(e,t){const n=this.parent;if(e===!0&&n!==null&&n.updateWorldMatrix(!0,!1),this.matrixAutoUpdate&&this.updateMatrix(),this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),t===!0){const s=this.children;for(let r=0,a=s.length;r<a;r++)s[r].updateWorldMatrix(!1,!0)}}toJSON(e){const t=e===void 0||typeof e=="string",n={};t&&(e={geometries:{},materials:{},textures:{},images:{},shapes:{},skeletons:{},animations:{},nodes:{}},n.metadata={version:4.6,type:"Object",generator:"Object3D.toJSON"});const s={};s.uuid=this.uuid,s.type=this.type,this.name!==""&&(s.name=this.name),this.castShadow===!0&&(s.castShadow=!0),this.receiveShadow===!0&&(s.receiveShadow=!0),this.visible===!1&&(s.visible=!1),this.frustumCulled===!1&&(s.frustumCulled=!1),this.renderOrder!==0&&(s.renderOrder=this.renderOrder),Object.keys(this.userData).length>0&&(s.userData=this.userData),s.layers=this.layers.mask,s.matrix=this.matrix.toArray(),s.up=this.up.toArray(),this.matrixAutoUpdate===!1&&(s.matrixAutoUpdate=!1),this.isInstancedMesh&&(s.type="InstancedMesh",s.count=this.count,s.instanceMatrix=this.instanceMatrix.toJSON(),this.instanceColor!==null&&(s.instanceColor=this.instanceColor.toJSON())),this.isBatchedMesh&&(s.type="BatchedMesh",s.perObjectFrustumCulled=this.perObjectFrustumCulled,s.sortObjects=this.sortObjects,s.drawRanges=this._drawRanges,s.reservedRanges=this._reservedRanges,s.visibility=this._visibility,s.active=this._active,s.bounds=this._bounds.map(o=>({boxInitialized:o.boxInitialized,boxMin:o.box.min.toArray(),boxMax:o.box.max.toArray(),sphereInitialized:o.sphereInitialized,sphereRadius:o.sphere.radius,sphereCenter:o.sphere.center.toArray()})),s.maxInstanceCount=this._maxInstanceCount,s.maxVertexCount=this._maxVertexCount,s.maxIndexCount=this._maxIndexCount,s.geometryInitialized=this._geometryInitialized,s.geometryCount=this._geometryCount,s.matricesTexture=this._matricesTexture.toJSON(e),this._colorsTexture!==null&&(s.colorsTexture=this._colorsTexture.toJSON(e)),this.boundingSphere!==null&&(s.boundingSphere={center:s.boundingSphere.center.toArray(),radius:s.boundingSphere.radius}),this.boundingBox!==null&&(s.boundingBox={min:s.boundingBox.min.toArray(),max:s.boundingBox.max.toArray()}));function r(o,l){return o[l.uuid]===void 0&&(o[l.uuid]=l.toJSON(e)),l.uuid}if(this.isScene)this.background&&(this.background.isColor?s.background=this.background.toJSON():this.background.isTexture&&(s.background=this.background.toJSON(e).uuid)),this.environment&&this.environment.isTexture&&this.environment.isRenderTargetTexture!==!0&&(s.environment=this.environment.toJSON(e).uuid);else if(this.isMesh||this.isLine||this.isPoints){s.geometry=r(e.geometries,this.geometry);const o=this.geometry.parameters;if(o!==void 0&&o.shapes!==void 0){const l=o.shapes;if(Array.isArray(l))for(let c=0,h=l.length;c<h;c++){const u=l[c];r(e.shapes,u)}else r(e.shapes,l)}}if(this.isSkinnedMesh&&(s.bindMode=this.bindMode,s.bindMatrix=this.bindMatrix.toArray(),this.skeleton!==void 0&&(r(e.skeletons,this.skeleton),s.skeleton=this.skeleton.uuid)),this.material!==void 0)if(Array.isArray(this.material)){const o=[];for(let l=0,c=this.material.length;l<c;l++)o.push(r(e.materials,this.material[l]));s.material=o}else s.material=r(e.materials,this.material);if(this.children.length>0){s.children=[];for(let o=0;o<this.children.length;o++)s.children.push(this.children[o].toJSON(e).object)}if(this.animations.length>0){s.animations=[];for(let o=0;o<this.animations.length;o++){const l=this.animations[o];s.animations.push(r(e.animations,l))}}if(t){const o=a(e.geometries),l=a(e.materials),c=a(e.textures),h=a(e.images),u=a(e.shapes),d=a(e.skeletons),f=a(e.animations),g=a(e.nodes);o.length>0&&(n.geometries=o),l.length>0&&(n.materials=l),c.length>0&&(n.textures=c),h.length>0&&(n.images=h),u.length>0&&(n.shapes=u),d.length>0&&(n.skeletons=d),f.length>0&&(n.animations=f),g.length>0&&(n.nodes=g)}return n.object=s,n;function a(o){const l=[];for(const c in o){const h=o[c];delete h.metadata,l.push(h)}return l}}clone(e){return new this.constructor().copy(this,e)}copy(e,t=!0){if(this.name=e.name,this.up.copy(e.up),this.position.copy(e.position),this.rotation.order=e.rotation.order,this.quaternion.copy(e.quaternion),this.scale.copy(e.scale),this.matrix.copy(e.matrix),this.matrixWorld.copy(e.matrixWorld),this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrixWorldAutoUpdate=e.matrixWorldAutoUpdate,this.matrixWorldNeedsUpdate=e.matrixWorldNeedsUpdate,this.layers.mask=e.layers.mask,this.visible=e.visible,this.castShadow=e.castShadow,this.receiveShadow=e.receiveShadow,this.frustumCulled=e.frustumCulled,this.renderOrder=e.renderOrder,this.animations=e.animations.slice(),this.userData=JSON.parse(JSON.stringify(e.userData)),t===!0)for(let n=0;n<e.children.length;n++){const s=e.children[n];this.add(s.clone())}return this}}Qt.DEFAULT_UP=new H(0,1,0);Qt.DEFAULT_MATRIX_AUTO_UPDATE=!0;Qt.DEFAULT_MATRIX_WORLD_AUTO_UPDATE=!0;const ii=new H,Ii=new H,Wl=new H,Ui=new H,hr=new H,ur=new H,Ou=new H,Xl=new H,ql=new H,$l=new H;class jn{constructor(e=new H,t=new H,n=new H){this.a=e,this.b=t,this.c=n}static getNormal(e,t,n,s){s.subVectors(n,t),ii.subVectors(e,t),s.cross(ii);const r=s.lengthSq();return r>0?s.multiplyScalar(1/Math.sqrt(r)):s.set(0,0,0)}static getBarycoord(e,t,n,s,r){ii.subVectors(s,t),Ii.subVectors(n,t),Wl.subVectors(e,t);const a=ii.dot(ii),o=ii.dot(Ii),l=ii.dot(Wl),c=Ii.dot(Ii),h=Ii.dot(Wl),u=a*c-o*o;if(u===0)return r.set(0,0,0),null;const d=1/u,f=(c*l-o*h)*d,g=(a*h-o*l)*d;return r.set(1-f-g,g,f)}static containsPoint(e,t,n,s){return this.getBarycoord(e,t,n,s,Ui)===null?!1:Ui.x>=0&&Ui.y>=0&&Ui.x+Ui.y<=1}static getInterpolation(e,t,n,s,r,a,o,l){return this.getBarycoord(e,t,n,s,Ui)===null?(l.x=0,l.y=0,"z"in l&&(l.z=0),"w"in l&&(l.w=0),null):(l.setScalar(0),l.addScaledVector(r,Ui.x),l.addScaledVector(a,Ui.y),l.addScaledVector(o,Ui.z),l)}static isFrontFacing(e,t,n,s){return ii.subVectors(n,t),Ii.subVectors(e,t),ii.cross(Ii).dot(s)<0}set(e,t,n){return this.a.copy(e),this.b.copy(t),this.c.copy(n),this}setFromPointsAndIndices(e,t,n,s){return this.a.copy(e[t]),this.b.copy(e[n]),this.c.copy(e[s]),this}setFromAttributeAndIndices(e,t,n,s){return this.a.fromBufferAttribute(e,t),this.b.fromBufferAttribute(e,n),this.c.fromBufferAttribute(e,s),this}clone(){return new this.constructor().copy(this)}copy(e){return this.a.copy(e.a),this.b.copy(e.b),this.c.copy(e.c),this}getArea(){return ii.subVectors(this.c,this.b),Ii.subVectors(this.a,this.b),ii.cross(Ii).length()*.5}getMidpoint(e){return e.addVectors(this.a,this.b).add(this.c).multiplyScalar(1/3)}getNormal(e){return jn.getNormal(this.a,this.b,this.c,e)}getPlane(e){return e.setFromCoplanarPoints(this.a,this.b,this.c)}getBarycoord(e,t){return jn.getBarycoord(e,this.a,this.b,this.c,t)}getInterpolation(e,t,n,s,r){return jn.getInterpolation(e,this.a,this.b,this.c,t,n,s,r)}containsPoint(e){return jn.containsPoint(e,this.a,this.b,this.c)}isFrontFacing(e){return jn.isFrontFacing(this.a,this.b,this.c,e)}intersectsBox(e){return e.intersectsTriangle(this)}closestPointToPoint(e,t){const n=this.a,s=this.b,r=this.c;let a,o;hr.subVectors(s,n),ur.subVectors(r,n),Xl.subVectors(e,n);const l=hr.dot(Xl),c=ur.dot(Xl);if(l<=0&&c<=0)return t.copy(n);ql.subVectors(e,s);const h=hr.dot(ql),u=ur.dot(ql);if(h>=0&&u<=h)return t.copy(s);const d=l*u-h*c;if(d<=0&&l>=0&&h<=0)return a=l/(l-h),t.copy(n).addScaledVector(hr,a);$l.subVectors(e,r);const f=hr.dot($l),g=ur.dot($l);if(g>=0&&f<=g)return t.copy(r);const _=f*c-l*g;if(_<=0&&c>=0&&g<=0)return o=c/(c-g),t.copy(n).addScaledVector(ur,o);const m=h*g-f*u;if(m<=0&&u-h>=0&&f-g>=0)return Ou.subVectors(r,s),o=(u-h)/(u-h+(f-g)),t.copy(s).addScaledVector(Ou,o);const p=1/(m+_+d);return a=_*p,o=d*p,t.copy(n).addScaledVector(hr,a).addScaledVector(ur,o)}equals(e){return e.a.equals(this.a)&&e.b.equals(this.b)&&e.c.equals(this.c)}}const qf={aliceblue:15792383,antiquewhite:16444375,aqua:65535,aquamarine:8388564,azure:15794175,beige:16119260,bisque:16770244,black:0,blanchedalmond:16772045,blue:255,blueviolet:9055202,brown:10824234,burlywood:14596231,cadetblue:6266528,chartreuse:8388352,chocolate:13789470,coral:16744272,cornflowerblue:6591981,cornsilk:16775388,crimson:14423100,cyan:65535,darkblue:139,darkcyan:35723,darkgoldenrod:12092939,darkgray:11119017,darkgreen:25600,darkgrey:11119017,darkkhaki:12433259,darkmagenta:9109643,darkolivegreen:5597999,darkorange:16747520,darkorchid:10040012,darkred:9109504,darksalmon:15308410,darkseagreen:9419919,darkslateblue:4734347,darkslategray:3100495,darkslategrey:3100495,darkturquoise:52945,darkviolet:9699539,deeppink:16716947,deepskyblue:49151,dimgray:6908265,dimgrey:6908265,dodgerblue:2003199,firebrick:11674146,floralwhite:16775920,forestgreen:2263842,fuchsia:16711935,gainsboro:14474460,ghostwhite:16316671,gold:16766720,goldenrod:14329120,gray:8421504,green:32768,greenyellow:11403055,grey:8421504,honeydew:15794160,hotpink:16738740,indianred:13458524,indigo:4915330,ivory:16777200,khaki:15787660,lavender:15132410,lavenderblush:16773365,lawngreen:8190976,lemonchiffon:16775885,lightblue:11393254,lightcoral:15761536,lightcyan:14745599,lightgoldenrodyellow:16448210,lightgray:13882323,lightgreen:9498256,lightgrey:13882323,lightpink:16758465,lightsalmon:16752762,lightseagreen:2142890,lightskyblue:8900346,lightslategray:7833753,lightslategrey:7833753,lightsteelblue:11584734,lightyellow:16777184,lime:65280,limegreen:3329330,linen:16445670,magenta:16711935,maroon:8388608,mediumaquamarine:6737322,mediumblue:205,mediumorchid:12211667,mediumpurple:9662683,mediumseagreen:3978097,mediumslateblue:8087790,mediumspringgreen:64154,mediumturquoise:4772300,mediumvioletred:13047173,midnightblue:1644912,mintcream:16121850,mistyrose:16770273,moccasin:16770229,navajowhite:16768685,navy:128,oldlace:16643558,olive:8421376,olivedrab:7048739,orange:16753920,orangered:16729344,orchid:14315734,palegoldenrod:15657130,palegreen:10025880,paleturquoise:11529966,palevioletred:14381203,papayawhip:16773077,peachpuff:16767673,peru:13468991,pink:16761035,plum:14524637,powderblue:11591910,purple:8388736,rebeccapurple:6697881,red:16711680,rosybrown:12357519,royalblue:4286945,saddlebrown:9127187,salmon:16416882,sandybrown:16032864,seagreen:3050327,seashell:16774638,sienna:10506797,silver:12632256,skyblue:8900331,slateblue:6970061,slategray:7372944,slategrey:7372944,snow:16775930,springgreen:65407,steelblue:4620980,tan:13808780,teal:32896,thistle:14204888,tomato:16737095,turquoise:4251856,violet:15631086,wheat:16113331,white:16777215,whitesmoke:16119285,yellow:16776960,yellowgreen:10145074},ts={h:0,s:0,l:0},no={h:0,s:0,l:0};function Yl(i,e,t){return t<0&&(t+=1),t>1&&(t-=1),t<1/6?i+(e-i)*6*t:t<1/2?e:t<2/3?i+(e-i)*6*(2/3-t):i}class nt{constructor(e,t,n){return this.isColor=!0,this.r=1,this.g=1,this.b=1,this.set(e,t,n)}set(e,t,n){if(t===void 0&&n===void 0){const s=e;s&&s.isColor?this.copy(s):typeof s=="number"?this.setHex(s):typeof s=="string"&&this.setStyle(s)}else this.setRGB(e,t,n);return this}setScalar(e){return this.r=e,this.g=e,this.b=e,this}setHex(e,t=xi){return e=Math.floor(e),this.r=(e>>16&255)/255,this.g=(e>>8&255)/255,this.b=(e&255)/255,bt.toWorkingColorSpace(this,t),this}setRGB(e,t,n,s=bt.workingColorSpace){return this.r=e,this.g=t,this.b=n,bt.toWorkingColorSpace(this,s),this}setHSL(e,t,n,s=bt.workingColorSpace){if(e=Sh(e,1),t=Sn(t,0,1),n=Sn(n,0,1),t===0)this.r=this.g=this.b=n;else{const r=n<=.5?n*(1+t):n+t-n*t,a=2*n-r;this.r=Yl(a,r,e+1/3),this.g=Yl(a,r,e),this.b=Yl(a,r,e-1/3)}return bt.toWorkingColorSpace(this,s),this}setStyle(e,t=xi){function n(r){r!==void 0&&parseFloat(r)<1&&console.warn("THREE.Color: Alpha component of "+e+" will be ignored.")}let s;if(s=/^(\w+)\(([^\)]*)\)/.exec(e)){let r;const a=s[1],o=s[2];switch(a){case"rgb":case"rgba":if(r=/^\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(o))return n(r[4]),this.setRGB(Math.min(255,parseInt(r[1],10))/255,Math.min(255,parseInt(r[2],10))/255,Math.min(255,parseInt(r[3],10))/255,t);if(r=/^\s*(\d+)\%\s*,\s*(\d+)\%\s*,\s*(\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(o))return n(r[4]),this.setRGB(Math.min(100,parseInt(r[1],10))/100,Math.min(100,parseInt(r[2],10))/100,Math.min(100,parseInt(r[3],10))/100,t);break;case"hsl":case"hsla":if(r=/^\s*(\d*\.?\d+)\s*,\s*(\d*\.?\d+)\%\s*,\s*(\d*\.?\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(o))return n(r[4]),this.setHSL(parseFloat(r[1])/360,parseFloat(r[2])/100,parseFloat(r[3])/100,t);break;default:console.warn("THREE.Color: Unknown color model "+e)}}else if(s=/^\#([A-Fa-f\d]+)$/.exec(e)){const r=s[1],a=r.length;if(a===3)return this.setRGB(parseInt(r.charAt(0),16)/15,parseInt(r.charAt(1),16)/15,parseInt(r.charAt(2),16)/15,t);if(a===6)return this.setHex(parseInt(r,16),t);console.warn("THREE.Color: Invalid hex color "+e)}else if(e&&e.length>0)return this.setColorName(e,t);return this}setColorName(e,t=xi){const n=qf[e.toLowerCase()];return n!==void 0?this.setHex(n,t):console.warn("THREE.Color: Unknown color "+e),this}clone(){return new this.constructor(this.r,this.g,this.b)}copy(e){return this.r=e.r,this.g=e.g,this.b=e.b,this}copySRGBToLinear(e){return this.r=Ir(e.r),this.g=Ir(e.g),this.b=Ir(e.b),this}copyLinearToSRGB(e){return this.r=Nl(e.r),this.g=Nl(e.g),this.b=Nl(e.b),this}convertSRGBToLinear(){return this.copySRGBToLinear(this),this}convertLinearToSRGB(){return this.copyLinearToSRGB(this),this}getHex(e=xi){return bt.fromWorkingColorSpace(Mn.copy(this),e),Math.round(Sn(Mn.r*255,0,255))*65536+Math.round(Sn(Mn.g*255,0,255))*256+Math.round(Sn(Mn.b*255,0,255))}getHexString(e=xi){return("000000"+this.getHex(e).toString(16)).slice(-6)}getHSL(e,t=bt.workingColorSpace){bt.fromWorkingColorSpace(Mn.copy(this),t);const n=Mn.r,s=Mn.g,r=Mn.b,a=Math.max(n,s,r),o=Math.min(n,s,r);let l,c;const h=(o+a)/2;if(o===a)l=0,c=0;else{const u=a-o;switch(c=h<=.5?u/(a+o):u/(2-a-o),a){case n:l=(s-r)/u+(s<r?6:0);break;case s:l=(r-n)/u+2;break;case r:l=(n-s)/u+4;break}l/=6}return e.h=l,e.s=c,e.l=h,e}getRGB(e,t=bt.workingColorSpace){return bt.fromWorkingColorSpace(Mn.copy(this),t),e.r=Mn.r,e.g=Mn.g,e.b=Mn.b,e}getStyle(e=xi){bt.fromWorkingColorSpace(Mn.copy(this),e);const t=Mn.r,n=Mn.g,s=Mn.b;return e!==xi?`color(${e} ${t.toFixed(3)} ${n.toFixed(3)} ${s.toFixed(3)})`:`rgb(${Math.round(t*255)},${Math.round(n*255)},${Math.round(s*255)})`}offsetHSL(e,t,n){return this.getHSL(ts),this.setHSL(ts.h+e,ts.s+t,ts.l+n)}add(e){return this.r+=e.r,this.g+=e.g,this.b+=e.b,this}addColors(e,t){return this.r=e.r+t.r,this.g=e.g+t.g,this.b=e.b+t.b,this}addScalar(e){return this.r+=e,this.g+=e,this.b+=e,this}sub(e){return this.r=Math.max(0,this.r-e.r),this.g=Math.max(0,this.g-e.g),this.b=Math.max(0,this.b-e.b),this}multiply(e){return this.r*=e.r,this.g*=e.g,this.b*=e.b,this}multiplyScalar(e){return this.r*=e,this.g*=e,this.b*=e,this}lerp(e,t){return this.r+=(e.r-this.r)*t,this.g+=(e.g-this.g)*t,this.b+=(e.b-this.b)*t,this}lerpColors(e,t,n){return this.r=e.r+(t.r-e.r)*n,this.g=e.g+(t.g-e.g)*n,this.b=e.b+(t.b-e.b)*n,this}lerpHSL(e,t){this.getHSL(ts),e.getHSL(no);const n=Ta(ts.h,no.h,t),s=Ta(ts.s,no.s,t),r=Ta(ts.l,no.l,t);return this.setHSL(n,s,r),this}setFromVector3(e){return this.r=e.x,this.g=e.y,this.b=e.z,this}applyMatrix3(e){const t=this.r,n=this.g,s=this.b,r=e.elements;return this.r=r[0]*t+r[3]*n+r[6]*s,this.g=r[1]*t+r[4]*n+r[7]*s,this.b=r[2]*t+r[5]*n+r[8]*s,this}equals(e){return e.r===this.r&&e.g===this.g&&e.b===this.b}fromArray(e,t=0){return this.r=e[t],this.g=e[t+1],this.b=e[t+2],this}toArray(e=[],t=0){return e[t]=this.r,e[t+1]=this.g,e[t+2]=this.b,e}fromBufferAttribute(e,t){return this.r=e.getX(t),this.g=e.getY(t),this.b=e.getZ(t),this}toJSON(){return this.getHex()}*[Symbol.iterator](){yield this.r,yield this.g,yield this.b}}const Mn=new nt;nt.NAMES=qf;let Kg=0;class ms extends Kr{constructor(){super(),this.isMaterial=!0,Object.defineProperty(this,"id",{value:Kg++}),this.uuid=ki(),this.name="",this.type="Material",this.blending=Cr,this.side=hs,this.vertexColors=!1,this.opacity=1,this.transparent=!1,this.alphaHash=!1,this.blendSrc=yc,this.blendDst=Mc,this.blendEquation=Ps,this.blendSrcAlpha=null,this.blendDstAlpha=null,this.blendEquationAlpha=null,this.blendColor=new nt(0,0,0),this.blendAlpha=0,this.depthFunc=Ho,this.depthTest=!0,this.depthWrite=!0,this.stencilWriteMask=255,this.stencilFunc=bu,this.stencilRef=0,this.stencilFuncMask=255,this.stencilFail=nr,this.stencilZFail=nr,this.stencilZPass=nr,this.stencilWrite=!1,this.clippingPlanes=null,this.clipIntersection=!1,this.clipShadows=!1,this.shadowSide=null,this.colorWrite=!0,this.precision=null,this.polygonOffset=!1,this.polygonOffsetFactor=0,this.polygonOffsetUnits=0,this.dithering=!1,this.alphaToCoverage=!1,this.premultipliedAlpha=!1,this.forceSinglePass=!1,this.visible=!0,this.toneMapped=!0,this.userData={},this.version=0,this._alphaTest=0}get alphaTest(){return this._alphaTest}set alphaTest(e){this._alphaTest>0!=e>0&&this.version++,this._alphaTest=e}onBeforeRender(){}onBeforeCompile(){}customProgramCacheKey(){return this.onBeforeCompile.toString()}setValues(e){if(e!==void 0)for(const t in e){const n=e[t];if(n===void 0){console.warn(`THREE.Material: parameter '${t}' has value of undefined.`);continue}const s=this[t];if(s===void 0){console.warn(`THREE.Material: '${t}' is not a property of THREE.${this.type}.`);continue}s&&s.isColor?s.set(n):s&&s.isVector3&&n&&n.isVector3?s.copy(n):this[t]=n}}toJSON(e){const t=e===void 0||typeof e=="string";t&&(e={textures:{},images:{}});const n={metadata:{version:4.6,type:"Material",generator:"Material.toJSON"}};n.uuid=this.uuid,n.type=this.type,this.name!==""&&(n.name=this.name),this.color&&this.color.isColor&&(n.color=this.color.getHex()),this.roughness!==void 0&&(n.roughness=this.roughness),this.metalness!==void 0&&(n.metalness=this.metalness),this.sheen!==void 0&&(n.sheen=this.sheen),this.sheenColor&&this.sheenColor.isColor&&(n.sheenColor=this.sheenColor.getHex()),this.sheenRoughness!==void 0&&(n.sheenRoughness=this.sheenRoughness),this.emissive&&this.emissive.isColor&&(n.emissive=this.emissive.getHex()),this.emissiveIntensity!==void 0&&this.emissiveIntensity!==1&&(n.emissiveIntensity=this.emissiveIntensity),this.specular&&this.specular.isColor&&(n.specular=this.specular.getHex()),this.specularIntensity!==void 0&&(n.specularIntensity=this.specularIntensity),this.specularColor&&this.specularColor.isColor&&(n.specularColor=this.specularColor.getHex()),this.shininess!==void 0&&(n.shininess=this.shininess),this.clearcoat!==void 0&&(n.clearcoat=this.clearcoat),this.clearcoatRoughness!==void 0&&(n.clearcoatRoughness=this.clearcoatRoughness),this.clearcoatMap&&this.clearcoatMap.isTexture&&(n.clearcoatMap=this.clearcoatMap.toJSON(e).uuid),this.clearcoatRoughnessMap&&this.clearcoatRoughnessMap.isTexture&&(n.clearcoatRoughnessMap=this.clearcoatRoughnessMap.toJSON(e).uuid),this.clearcoatNormalMap&&this.clearcoatNormalMap.isTexture&&(n.clearcoatNormalMap=this.clearcoatNormalMap.toJSON(e).uuid,n.clearcoatNormalScale=this.clearcoatNormalScale.toArray()),this.dispersion!==void 0&&(n.dispersion=this.dispersion),this.iridescence!==void 0&&(n.iridescence=this.iridescence),this.iridescenceIOR!==void 0&&(n.iridescenceIOR=this.iridescenceIOR),this.iridescenceThicknessRange!==void 0&&(n.iridescenceThicknessRange=this.iridescenceThicknessRange),this.iridescenceMap&&this.iridescenceMap.isTexture&&(n.iridescenceMap=this.iridescenceMap.toJSON(e).uuid),this.iridescenceThicknessMap&&this.iridescenceThicknessMap.isTexture&&(n.iridescenceThicknessMap=this.iridescenceThicknessMap.toJSON(e).uuid),this.anisotropy!==void 0&&(n.anisotropy=this.anisotropy),this.anisotropyRotation!==void 0&&(n.anisotropyRotation=this.anisotropyRotation),this.anisotropyMap&&this.anisotropyMap.isTexture&&(n.anisotropyMap=this.anisotropyMap.toJSON(e).uuid),this.map&&this.map.isTexture&&(n.map=this.map.toJSON(e).uuid),this.matcap&&this.matcap.isTexture&&(n.matcap=this.matcap.toJSON(e).uuid),this.alphaMap&&this.alphaMap.isTexture&&(n.alphaMap=this.alphaMap.toJSON(e).uuid),this.lightMap&&this.lightMap.isTexture&&(n.lightMap=this.lightMap.toJSON(e).uuid,n.lightMapIntensity=this.lightMapIntensity),this.aoMap&&this.aoMap.isTexture&&(n.aoMap=this.aoMap.toJSON(e).uuid,n.aoMapIntensity=this.aoMapIntensity),this.bumpMap&&this.bumpMap.isTexture&&(n.bumpMap=this.bumpMap.toJSON(e).uuid,n.bumpScale=this.bumpScale),this.normalMap&&this.normalMap.isTexture&&(n.normalMap=this.normalMap.toJSON(e).uuid,n.normalMapType=this.normalMapType,n.normalScale=this.normalScale.toArray()),this.displacementMap&&this.displacementMap.isTexture&&(n.displacementMap=this.displacementMap.toJSON(e).uuid,n.displacementScale=this.displacementScale,n.displacementBias=this.displacementBias),this.roughnessMap&&this.roughnessMap.isTexture&&(n.roughnessMap=this.roughnessMap.toJSON(e).uuid),this.metalnessMap&&this.metalnessMap.isTexture&&(n.metalnessMap=this.metalnessMap.toJSON(e).uuid),this.emissiveMap&&this.emissiveMap.isTexture&&(n.emissiveMap=this.emissiveMap.toJSON(e).uuid),this.specularMap&&this.specularMap.isTexture&&(n.specularMap=this.specularMap.toJSON(e).uuid),this.specularIntensityMap&&this.specularIntensityMap.isTexture&&(n.specularIntensityMap=this.specularIntensityMap.toJSON(e).uuid),this.specularColorMap&&this.specularColorMap.isTexture&&(n.specularColorMap=this.specularColorMap.toJSON(e).uuid),this.envMap&&this.envMap.isTexture&&(n.envMap=this.envMap.toJSON(e).uuid,this.combine!==void 0&&(n.combine=this.combine)),this.envMapRotation!==void 0&&(n.envMapRotation=this.envMapRotation.toArray()),this.envMapIntensity!==void 0&&(n.envMapIntensity=this.envMapIntensity),this.reflectivity!==void 0&&(n.reflectivity=this.reflectivity),this.refractionRatio!==void 0&&(n.refractionRatio=this.refractionRatio),this.gradientMap&&this.gradientMap.isTexture&&(n.gradientMap=this.gradientMap.toJSON(e).uuid),this.transmission!==void 0&&(n.transmission=this.transmission),this.transmissionMap&&this.transmissionMap.isTexture&&(n.transmissionMap=this.transmissionMap.toJSON(e).uuid),this.thickness!==void 0&&(n.thickness=this.thickness),this.thicknessMap&&this.thicknessMap.isTexture&&(n.thicknessMap=this.thicknessMap.toJSON(e).uuid),this.attenuationDistance!==void 0&&this.attenuationDistance!==1/0&&(n.attenuationDistance=this.attenuationDistance),this.attenuationColor!==void 0&&(n.attenuationColor=this.attenuationColor.getHex()),this.size!==void 0&&(n.size=this.size),this.shadowSide!==null&&(n.shadowSide=this.shadowSide),this.sizeAttenuation!==void 0&&(n.sizeAttenuation=this.sizeAttenuation),this.blending!==Cr&&(n.blending=this.blending),this.side!==hs&&(n.side=this.side),this.vertexColors===!0&&(n.vertexColors=!0),this.opacity<1&&(n.opacity=this.opacity),this.transparent===!0&&(n.transparent=!0),this.blendSrc!==yc&&(n.blendSrc=this.blendSrc),this.blendDst!==Mc&&(n.blendDst=this.blendDst),this.blendEquation!==Ps&&(n.blendEquation=this.blendEquation),this.blendSrcAlpha!==null&&(n.blendSrcAlpha=this.blendSrcAlpha),this.blendDstAlpha!==null&&(n.blendDstAlpha=this.blendDstAlpha),this.blendEquationAlpha!==null&&(n.blendEquationAlpha=this.blendEquationAlpha),this.blendColor&&this.blendColor.isColor&&(n.blendColor=this.blendColor.getHex()),this.blendAlpha!==0&&(n.blendAlpha=this.blendAlpha),this.depthFunc!==Ho&&(n.depthFunc=this.depthFunc),this.depthTest===!1&&(n.depthTest=this.depthTest),this.depthWrite===!1&&(n.depthWrite=this.depthWrite),this.colorWrite===!1&&(n.colorWrite=this.colorWrite),this.stencilWriteMask!==255&&(n.stencilWriteMask=this.stencilWriteMask),this.stencilFunc!==bu&&(n.stencilFunc=this.stencilFunc),this.stencilRef!==0&&(n.stencilRef=this.stencilRef),this.stencilFuncMask!==255&&(n.stencilFuncMask=this.stencilFuncMask),this.stencilFail!==nr&&(n.stencilFail=this.stencilFail),this.stencilZFail!==nr&&(n.stencilZFail=this.stencilZFail),this.stencilZPass!==nr&&(n.stencilZPass=this.stencilZPass),this.stencilWrite===!0&&(n.stencilWrite=this.stencilWrite),this.rotation!==void 0&&this.rotation!==0&&(n.rotation=this.rotation),this.polygonOffset===!0&&(n.polygonOffset=!0),this.polygonOffsetFactor!==0&&(n.polygonOffsetFactor=this.polygonOffsetFactor),this.polygonOffsetUnits!==0&&(n.polygonOffsetUnits=this.polygonOffsetUnits),this.linewidth!==void 0&&this.linewidth!==1&&(n.linewidth=this.linewidth),this.dashSize!==void 0&&(n.dashSize=this.dashSize),this.gapSize!==void 0&&(n.gapSize=this.gapSize),this.scale!==void 0&&(n.scale=this.scale),this.dithering===!0&&(n.dithering=!0),this.alphaTest>0&&(n.alphaTest=this.alphaTest),this.alphaHash===!0&&(n.alphaHash=!0),this.alphaToCoverage===!0&&(n.alphaToCoverage=!0),this.premultipliedAlpha===!0&&(n.premultipliedAlpha=!0),this.forceSinglePass===!0&&(n.forceSinglePass=!0),this.wireframe===!0&&(n.wireframe=!0),this.wireframeLinewidth>1&&(n.wireframeLinewidth=this.wireframeLinewidth),this.wireframeLinecap!=="round"&&(n.wireframeLinecap=this.wireframeLinecap),this.wireframeLinejoin!=="round"&&(n.wireframeLinejoin=this.wireframeLinejoin),this.flatShading===!0&&(n.flatShading=!0),this.visible===!1&&(n.visible=!1),this.toneMapped===!1&&(n.toneMapped=!1),this.fog===!1&&(n.fog=!1),Object.keys(this.userData).length>0&&(n.userData=this.userData);function s(r){const a=[];for(const o in r){const l=r[o];delete l.metadata,a.push(l)}return a}if(t){const r=s(e.textures),a=s(e.images);r.length>0&&(n.textures=r),a.length>0&&(n.images=a)}return n}clone(){return new this.constructor().copy(this)}copy(e){this.name=e.name,this.blending=e.blending,this.side=e.side,this.vertexColors=e.vertexColors,this.opacity=e.opacity,this.transparent=e.transparent,this.blendSrc=e.blendSrc,this.blendDst=e.blendDst,this.blendEquation=e.blendEquation,this.blendSrcAlpha=e.blendSrcAlpha,this.blendDstAlpha=e.blendDstAlpha,this.blendEquationAlpha=e.blendEquationAlpha,this.blendColor.copy(e.blendColor),this.blendAlpha=e.blendAlpha,this.depthFunc=e.depthFunc,this.depthTest=e.depthTest,this.depthWrite=e.depthWrite,this.stencilWriteMask=e.stencilWriteMask,this.stencilFunc=e.stencilFunc,this.stencilRef=e.stencilRef,this.stencilFuncMask=e.stencilFuncMask,this.stencilFail=e.stencilFail,this.stencilZFail=e.stencilZFail,this.stencilZPass=e.stencilZPass,this.stencilWrite=e.stencilWrite;const t=e.clippingPlanes;let n=null;if(t!==null){const s=t.length;n=new Array(s);for(let r=0;r!==s;++r)n[r]=t[r].clone()}return this.clippingPlanes=n,this.clipIntersection=e.clipIntersection,this.clipShadows=e.clipShadows,this.shadowSide=e.shadowSide,this.colorWrite=e.colorWrite,this.precision=e.precision,this.polygonOffset=e.polygonOffset,this.polygonOffsetFactor=e.polygonOffsetFactor,this.polygonOffsetUnits=e.polygonOffsetUnits,this.dithering=e.dithering,this.alphaTest=e.alphaTest,this.alphaHash=e.alphaHash,this.alphaToCoverage=e.alphaToCoverage,this.premultipliedAlpha=e.premultipliedAlpha,this.forceSinglePass=e.forceSinglePass,this.visible=e.visible,this.toneMapped=e.toneMapped,this.userData=JSON.parse(JSON.stringify(e.userData)),this}dispose(){this.dispatchEvent({type:"dispose"})}set needsUpdate(e){e===!0&&this.version++}onBuild(){console.warn("Material: onBuild() has been removed.")}}class Ur extends ms{constructor(e){super(),this.isMeshBasicMaterial=!0,this.type="MeshBasicMaterial",this.color=new nt(16777215),this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.specularMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new Si,this.combine=Rf,this.reflectivity=1,this.refractionRatio=.98,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.lightMap=e.lightMap,this.lightMapIntensity=e.lightMapIntensity,this.aoMap=e.aoMap,this.aoMapIntensity=e.aoMapIntensity,this.specularMap=e.specularMap,this.alphaMap=e.alphaMap,this.envMap=e.envMap,this.envMapRotation.copy(e.envMapRotation),this.combine=e.combine,this.reflectivity=e.reflectivity,this.refractionRatio=e.refractionRatio,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.wireframeLinecap=e.wireframeLinecap,this.wireframeLinejoin=e.wireframeLinejoin,this.fog=e.fog,this}}const Zt=new H,io=new qe;class hi{constructor(e,t,n=!1){if(Array.isArray(e))throw new TypeError("THREE.BufferAttribute: array should be a Typed Array.");this.isBufferAttribute=!0,this.name="",this.array=e,this.itemSize=t,this.count=e!==void 0?e.length/t:0,this.normalized=n,this.usage=Jc,this._updateRange={offset:0,count:-1},this.updateRanges=[],this.gpuType=Oi,this.version=0}onUploadCallback(){}set needsUpdate(e){e===!0&&this.version++}get updateRange(){return Dr("THREE.BufferAttribute: updateRange() is deprecated and will be removed in r169. Use addUpdateRange() instead."),this._updateRange}setUsage(e){return this.usage=e,this}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}copy(e){return this.name=e.name,this.array=new e.array.constructor(e.array),this.itemSize=e.itemSize,this.count=e.count,this.normalized=e.normalized,this.usage=e.usage,this.gpuType=e.gpuType,this}copyAt(e,t,n){e*=this.itemSize,n*=t.itemSize;for(let s=0,r=this.itemSize;s<r;s++)this.array[e+s]=t.array[n+s];return this}copyArray(e){return this.array.set(e),this}applyMatrix3(e){if(this.itemSize===2)for(let t=0,n=this.count;t<n;t++)io.fromBufferAttribute(this,t),io.applyMatrix3(e),this.setXY(t,io.x,io.y);else if(this.itemSize===3)for(let t=0,n=this.count;t<n;t++)Zt.fromBufferAttribute(this,t),Zt.applyMatrix3(e),this.setXYZ(t,Zt.x,Zt.y,Zt.z);return this}applyMatrix4(e){for(let t=0,n=this.count;t<n;t++)Zt.fromBufferAttribute(this,t),Zt.applyMatrix4(e),this.setXYZ(t,Zt.x,Zt.y,Zt.z);return this}applyNormalMatrix(e){for(let t=0,n=this.count;t<n;t++)Zt.fromBufferAttribute(this,t),Zt.applyNormalMatrix(e),this.setXYZ(t,Zt.x,Zt.y,Zt.z);return this}transformDirection(e){for(let t=0,n=this.count;t<n;t++)Zt.fromBufferAttribute(this,t),Zt.transformDirection(e),this.setXYZ(t,Zt.x,Zt.y,Zt.z);return this}set(e,t=0){return this.array.set(e,t),this}getComponent(e,t){let n=this.array[e*this.itemSize+t];return this.normalized&&(n=oi(n,this.array)),n}setComponent(e,t,n){return this.normalized&&(n=Tt(n,this.array)),this.array[e*this.itemSize+t]=n,this}getX(e){let t=this.array[e*this.itemSize];return this.normalized&&(t=oi(t,this.array)),t}setX(e,t){return this.normalized&&(t=Tt(t,this.array)),this.array[e*this.itemSize]=t,this}getY(e){let t=this.array[e*this.itemSize+1];return this.normalized&&(t=oi(t,this.array)),t}setY(e,t){return this.normalized&&(t=Tt(t,this.array)),this.array[e*this.itemSize+1]=t,this}getZ(e){let t=this.array[e*this.itemSize+2];return this.normalized&&(t=oi(t,this.array)),t}setZ(e,t){return this.normalized&&(t=Tt(t,this.array)),this.array[e*this.itemSize+2]=t,this}getW(e){let t=this.array[e*this.itemSize+3];return this.normalized&&(t=oi(t,this.array)),t}setW(e,t){return this.normalized&&(t=Tt(t,this.array)),this.array[e*this.itemSize+3]=t,this}setXY(e,t,n){return e*=this.itemSize,this.normalized&&(t=Tt(t,this.array),n=Tt(n,this.array)),this.array[e+0]=t,this.array[e+1]=n,this}setXYZ(e,t,n,s){return e*=this.itemSize,this.normalized&&(t=Tt(t,this.array),n=Tt(n,this.array),s=Tt(s,this.array)),this.array[e+0]=t,this.array[e+1]=n,this.array[e+2]=s,this}setXYZW(e,t,n,s,r){return e*=this.itemSize,this.normalized&&(t=Tt(t,this.array),n=Tt(n,this.array),s=Tt(s,this.array),r=Tt(r,this.array)),this.array[e+0]=t,this.array[e+1]=n,this.array[e+2]=s,this.array[e+3]=r,this}onUpload(e){return this.onUploadCallback=e,this}clone(){return new this.constructor(this.array,this.itemSize).copy(this)}toJSON(){const e={itemSize:this.itemSize,type:this.array.constructor.name,array:Array.from(this.array),normalized:this.normalized};return this.name!==""&&(e.name=this.name),this.usage!==Jc&&(e.usage=this.usage),e}}class $f extends hi{constructor(e,t,n){super(new Uint16Array(e),t,n)}}class Yf extends hi{constructor(e,t,n){super(new Uint32Array(e),t,n)}}class qt extends hi{constructor(e,t,n){super(new Float32Array(e),t,n)}}let Zg=0;const Wn=new Bt,jl=new Qt,dr=new H,Bn=new Fa,pa=new Fa,dn=new H;class Xt extends Kr{constructor(){super(),this.isBufferGeometry=!0,Object.defineProperty(this,"id",{value:Zg++}),this.uuid=ki(),this.name="",this.type="BufferGeometry",this.index=null,this.attributes={},this.morphAttributes={},this.morphTargetsRelative=!1,this.groups=[],this.boundingBox=null,this.boundingSphere=null,this.drawRange={start:0,count:1/0},this.userData={}}getIndex(){return this.index}setIndex(e){return Array.isArray(e)?this.index=new(Gf(e)?Yf:$f)(e,1):this.index=e,this}getAttribute(e){return this.attributes[e]}setAttribute(e,t){return this.attributes[e]=t,this}deleteAttribute(e){return delete this.attributes[e],this}hasAttribute(e){return this.attributes[e]!==void 0}addGroup(e,t,n=0){this.groups.push({start:e,count:t,materialIndex:n})}clearGroups(){this.groups=[]}setDrawRange(e,t){this.drawRange.start=e,this.drawRange.count=t}applyMatrix4(e){const t=this.attributes.position;t!==void 0&&(t.applyMatrix4(e),t.needsUpdate=!0);const n=this.attributes.normal;if(n!==void 0){const r=new at().getNormalMatrix(e);n.applyNormalMatrix(r),n.needsUpdate=!0}const s=this.attributes.tangent;return s!==void 0&&(s.transformDirection(e),s.needsUpdate=!0),this.boundingBox!==null&&this.computeBoundingBox(),this.boundingSphere!==null&&this.computeBoundingSphere(),this}applyQuaternion(e){return Wn.makeRotationFromQuaternion(e),this.applyMatrix4(Wn),this}rotateX(e){return Wn.makeRotationX(e),this.applyMatrix4(Wn),this}rotateY(e){return Wn.makeRotationY(e),this.applyMatrix4(Wn),this}rotateZ(e){return Wn.makeRotationZ(e),this.applyMatrix4(Wn),this}translate(e,t,n){return Wn.makeTranslation(e,t,n),this.applyMatrix4(Wn),this}scale(e,t,n){return Wn.makeScale(e,t,n),this.applyMatrix4(Wn),this}lookAt(e){return jl.lookAt(e),jl.updateMatrix(),this.applyMatrix4(jl.matrix),this}center(){return this.computeBoundingBox(),this.boundingBox.getCenter(dr).negate(),this.translate(dr.x,dr.y,dr.z),this}setFromPoints(e){const t=[];for(let n=0,s=e.length;n<s;n++){const r=e[n];t.push(r.x,r.y,r.z||0)}return this.setAttribute("position",new qt(t,3)),this}computeBoundingBox(){this.boundingBox===null&&(this.boundingBox=new Fa);const e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingBox(): GLBufferAttribute requires a manual bounding box.",this),this.boundingBox.set(new H(-1/0,-1/0,-1/0),new H(1/0,1/0,1/0));return}if(e!==void 0){if(this.boundingBox.setFromBufferAttribute(e),t)for(let n=0,s=t.length;n<s;n++){const r=t[n];Bn.setFromBufferAttribute(r),this.morphTargetsRelative?(dn.addVectors(this.boundingBox.min,Bn.min),this.boundingBox.expandByPoint(dn),dn.addVectors(this.boundingBox.max,Bn.max),this.boundingBox.expandByPoint(dn)):(this.boundingBox.expandByPoint(Bn.min),this.boundingBox.expandByPoint(Bn.max))}}else this.boundingBox.makeEmpty();(isNaN(this.boundingBox.min.x)||isNaN(this.boundingBox.min.y)||isNaN(this.boundingBox.min.z))&&console.error('THREE.BufferGeometry.computeBoundingBox(): Computed min/max have NaN values. The "position" attribute is likely to have NaN values.',this)}computeBoundingSphere(){this.boundingSphere===null&&(this.boundingSphere=new Oa);const e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingSphere(): GLBufferAttribute requires a manual bounding sphere.",this),this.boundingSphere.set(new H,1/0);return}if(e){const n=this.boundingSphere.center;if(Bn.setFromBufferAttribute(e),t)for(let r=0,a=t.length;r<a;r++){const o=t[r];pa.setFromBufferAttribute(o),this.morphTargetsRelative?(dn.addVectors(Bn.min,pa.min),Bn.expandByPoint(dn),dn.addVectors(Bn.max,pa.max),Bn.expandByPoint(dn)):(Bn.expandByPoint(pa.min),Bn.expandByPoint(pa.max))}Bn.getCenter(n);let s=0;for(let r=0,a=e.count;r<a;r++)dn.fromBufferAttribute(e,r),s=Math.max(s,n.distanceToSquared(dn));if(t)for(let r=0,a=t.length;r<a;r++){const o=t[r],l=this.morphTargetsRelative;for(let c=0,h=o.count;c<h;c++)dn.fromBufferAttribute(o,c),l&&(dr.fromBufferAttribute(e,c),dn.add(dr)),s=Math.max(s,n.distanceToSquared(dn))}this.boundingSphere.radius=Math.sqrt(s),isNaN(this.boundingSphere.radius)&&console.error('THREE.BufferGeometry.computeBoundingSphere(): Computed radius is NaN. The "position" attribute is likely to have NaN values.',this)}}computeTangents(){const e=this.index,t=this.attributes;if(e===null||t.position===void 0||t.normal===void 0||t.uv===void 0){console.error("THREE.BufferGeometry: .computeTangents() failed. Missing required attributes (index, position, normal or uv)");return}const n=t.position,s=t.normal,r=t.uv;this.hasAttribute("tangent")===!1&&this.setAttribute("tangent",new hi(new Float32Array(4*n.count),4));const a=this.getAttribute("tangent"),o=[],l=[];for(let F=0;F<n.count;F++)o[F]=new H,l[F]=new H;const c=new H,h=new H,u=new H,d=new qe,f=new qe,g=new qe,_=new H,m=new H;function p(F,b,x){c.fromBufferAttribute(n,F),h.fromBufferAttribute(n,b),u.fromBufferAttribute(n,x),d.fromBufferAttribute(r,F),f.fromBufferAttribute(r,b),g.fromBufferAttribute(r,x),h.sub(c),u.sub(c),f.sub(d),g.sub(d);const P=1/(f.x*g.y-g.x*f.y);isFinite(P)&&(_.copy(h).multiplyScalar(g.y).addScaledVector(u,-f.y).multiplyScalar(P),m.copy(u).multiplyScalar(f.x).addScaledVector(h,-g.x).multiplyScalar(P),o[F].add(_),o[b].add(_),o[x].add(_),l[F].add(m),l[b].add(m),l[x].add(m))}let S=this.groups;S.length===0&&(S=[{start:0,count:e.count}]);for(let F=0,b=S.length;F<b;++F){const x=S[F],P=x.start,K=x.count;for(let k=P,Z=P+K;k<Z;k+=3)p(e.getX(k+0),e.getX(k+1),e.getX(k+2))}const y=new H,w=new H,O=new H,A=new H;function C(F){O.fromBufferAttribute(s,F),A.copy(O);const b=o[F];y.copy(b),y.sub(O.multiplyScalar(O.dot(b))).normalize(),w.crossVectors(A,b);const P=w.dot(l[F])<0?-1:1;a.setXYZW(F,y.x,y.y,y.z,P)}for(let F=0,b=S.length;F<b;++F){const x=S[F],P=x.start,K=x.count;for(let k=P,Z=P+K;k<Z;k+=3)C(e.getX(k+0)),C(e.getX(k+1)),C(e.getX(k+2))}}computeVertexNormals(){const e=this.index,t=this.getAttribute("position");if(t!==void 0){let n=this.getAttribute("normal");if(n===void 0)n=new hi(new Float32Array(t.count*3),3),this.setAttribute("normal",n);else for(let d=0,f=n.count;d<f;d++)n.setXYZ(d,0,0,0);const s=new H,r=new H,a=new H,o=new H,l=new H,c=new H,h=new H,u=new H;if(e)for(let d=0,f=e.count;d<f;d+=3){const g=e.getX(d+0),_=e.getX(d+1),m=e.getX(d+2);s.fromBufferAttribute(t,g),r.fromBufferAttribute(t,_),a.fromBufferAttribute(t,m),h.subVectors(a,r),u.subVectors(s,r),h.cross(u),o.fromBufferAttribute(n,g),l.fromBufferAttribute(n,_),c.fromBufferAttribute(n,m),o.add(h),l.add(h),c.add(h),n.setXYZ(g,o.x,o.y,o.z),n.setXYZ(_,l.x,l.y,l.z),n.setXYZ(m,c.x,c.y,c.z)}else for(let d=0,f=t.count;d<f;d+=3)s.fromBufferAttribute(t,d+0),r.fromBufferAttribute(t,d+1),a.fromBufferAttribute(t,d+2),h.subVectors(a,r),u.subVectors(s,r),h.cross(u),n.setXYZ(d+0,h.x,h.y,h.z),n.setXYZ(d+1,h.x,h.y,h.z),n.setXYZ(d+2,h.x,h.y,h.z);this.normalizeNormals(),n.needsUpdate=!0}}normalizeNormals(){const e=this.attributes.normal;for(let t=0,n=e.count;t<n;t++)dn.fromBufferAttribute(e,t),dn.normalize(),e.setXYZ(t,dn.x,dn.y,dn.z)}toNonIndexed(){function e(o,l){const c=o.array,h=o.itemSize,u=o.normalized,d=new c.constructor(l.length*h);let f=0,g=0;for(let _=0,m=l.length;_<m;_++){o.isInterleavedBufferAttribute?f=l[_]*o.data.stride+o.offset:f=l[_]*h;for(let p=0;p<h;p++)d[g++]=c[f++]}return new hi(d,h,u)}if(this.index===null)return console.warn("THREE.BufferGeometry.toNonIndexed(): BufferGeometry is already non-indexed."),this;const t=new Xt,n=this.index.array,s=this.attributes;for(const o in s){const l=s[o],c=e(l,n);t.setAttribute(o,c)}const r=this.morphAttributes;for(const o in r){const l=[],c=r[o];for(let h=0,u=c.length;h<u;h++){const d=c[h],f=e(d,n);l.push(f)}t.morphAttributes[o]=l}t.morphTargetsRelative=this.morphTargetsRelative;const a=this.groups;for(let o=0,l=a.length;o<l;o++){const c=a[o];t.addGroup(c.start,c.count,c.materialIndex)}return t}toJSON(){const e={metadata:{version:4.6,type:"BufferGeometry",generator:"BufferGeometry.toJSON"}};if(e.uuid=this.uuid,e.type=this.type,this.name!==""&&(e.name=this.name),Object.keys(this.userData).length>0&&(e.userData=this.userData),this.parameters!==void 0){const l=this.parameters;for(const c in l)l[c]!==void 0&&(e[c]=l[c]);return e}e.data={attributes:{}};const t=this.index;t!==null&&(e.data.index={type:t.array.constructor.name,array:Array.prototype.slice.call(t.array)});const n=this.attributes;for(const l in n){const c=n[l];e.data.attributes[l]=c.toJSON(e.data)}const s={};let r=!1;for(const l in this.morphAttributes){const c=this.morphAttributes[l],h=[];for(let u=0,d=c.length;u<d;u++){const f=c[u];h.push(f.toJSON(e.data))}h.length>0&&(s[l]=h,r=!0)}r&&(e.data.morphAttributes=s,e.data.morphTargetsRelative=this.morphTargetsRelative);const a=this.groups;a.length>0&&(e.data.groups=JSON.parse(JSON.stringify(a)));const o=this.boundingSphere;return o!==null&&(e.data.boundingSphere={center:o.center.toArray(),radius:o.radius}),e}clone(){return new this.constructor().copy(this)}copy(e){this.index=null,this.attributes={},this.morphAttributes={},this.groups=[],this.boundingBox=null,this.boundingSphere=null;const t={};this.name=e.name;const n=e.index;n!==null&&this.setIndex(n.clone(t));const s=e.attributes;for(const c in s){const h=s[c];this.setAttribute(c,h.clone(t))}const r=e.morphAttributes;for(const c in r){const h=[],u=r[c];for(let d=0,f=u.length;d<f;d++)h.push(u[d].clone(t));this.morphAttributes[c]=h}this.morphTargetsRelative=e.morphTargetsRelative;const a=e.groups;for(let c=0,h=a.length;c<h;c++){const u=a[c];this.addGroup(u.start,u.count,u.materialIndex)}const o=e.boundingBox;o!==null&&(this.boundingBox=o.clone());const l=e.boundingSphere;return l!==null&&(this.boundingSphere=l.clone()),this.drawRange.start=e.drawRange.start,this.drawRange.count=e.drawRange.count,this.userData=e.userData,this}dispose(){this.dispatchEvent({type:"dispose"})}}const Bu=new Bt,bs=new Ba,so=new Oa,zu=new H,fr=new H,pr=new H,mr=new H,Kl=new H,ro=new H,ao=new qe,oo=new qe,lo=new qe,ku=new H,Hu=new H,Vu=new H,co=new H,ho=new H;class _n extends Qt{constructor(e=new Xt,t=new Ur){super(),this.isMesh=!0,this.type="Mesh",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),e.morphTargetInfluences!==void 0&&(this.morphTargetInfluences=e.morphTargetInfluences.slice()),e.morphTargetDictionary!==void 0&&(this.morphTargetDictionary=Object.assign({},e.morphTargetDictionary)),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const s=t[n[0]];if(s!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let r=0,a=s.length;r<a;r++){const o=s[r].name||String(r);this.morphTargetInfluences.push(0),this.morphTargetDictionary[o]=r}}}}getVertexPosition(e,t){const n=this.geometry,s=n.attributes.position,r=n.morphAttributes.position,a=n.morphTargetsRelative;t.fromBufferAttribute(s,e);const o=this.morphTargetInfluences;if(r&&o){ro.set(0,0,0);for(let l=0,c=r.length;l<c;l++){const h=o[l],u=r[l];h!==0&&(Kl.fromBufferAttribute(u,e),a?ro.addScaledVector(Kl,h):ro.addScaledVector(Kl.sub(t),h))}t.add(ro)}return t}raycast(e,t){const n=this.geometry,s=this.material,r=this.matrixWorld;s!==void 0&&(n.boundingSphere===null&&n.computeBoundingSphere(),so.copy(n.boundingSphere),so.applyMatrix4(r),bs.copy(e.ray).recast(e.near),!(so.containsPoint(bs.origin)===!1&&(bs.intersectSphere(so,zu)===null||bs.origin.distanceToSquared(zu)>(e.far-e.near)**2))&&(Bu.copy(r).invert(),bs.copy(e.ray).applyMatrix4(Bu),!(n.boundingBox!==null&&bs.intersectsBox(n.boundingBox)===!1)&&this._computeIntersections(e,t,bs)))}_computeIntersections(e,t,n){let s;const r=this.geometry,a=this.material,o=r.index,l=r.attributes.position,c=r.attributes.uv,h=r.attributes.uv1,u=r.attributes.normal,d=r.groups,f=r.drawRange;if(o!==null)if(Array.isArray(a))for(let g=0,_=d.length;g<_;g++){const m=d[g],p=a[m.materialIndex],S=Math.max(m.start,f.start),y=Math.min(o.count,Math.min(m.start+m.count,f.start+f.count));for(let w=S,O=y;w<O;w+=3){const A=o.getX(w),C=o.getX(w+1),F=o.getX(w+2);s=uo(this,p,e,n,c,h,u,A,C,F),s&&(s.faceIndex=Math.floor(w/3),s.face.materialIndex=m.materialIndex,t.push(s))}}else{const g=Math.max(0,f.start),_=Math.min(o.count,f.start+f.count);for(let m=g,p=_;m<p;m+=3){const S=o.getX(m),y=o.getX(m+1),w=o.getX(m+2);s=uo(this,a,e,n,c,h,u,S,y,w),s&&(s.faceIndex=Math.floor(m/3),t.push(s))}}else if(l!==void 0)if(Array.isArray(a))for(let g=0,_=d.length;g<_;g++){const m=d[g],p=a[m.materialIndex],S=Math.max(m.start,f.start),y=Math.min(l.count,Math.min(m.start+m.count,f.start+f.count));for(let w=S,O=y;w<O;w+=3){const A=w,C=w+1,F=w+2;s=uo(this,p,e,n,c,h,u,A,C,F),s&&(s.faceIndex=Math.floor(w/3),s.face.materialIndex=m.materialIndex,t.push(s))}}else{const g=Math.max(0,f.start),_=Math.min(l.count,f.start+f.count);for(let m=g,p=_;m<p;m+=3){const S=m,y=m+1,w=m+2;s=uo(this,a,e,n,c,h,u,S,y,w),s&&(s.faceIndex=Math.floor(m/3),t.push(s))}}}}function Jg(i,e,t,n,s,r,a,o){let l;if(e.side===In?l=n.intersectTriangle(a,r,s,!0,o):l=n.intersectTriangle(s,r,a,e.side===hs,o),l===null)return null;ho.copy(o),ho.applyMatrix4(i.matrixWorld);const c=t.ray.origin.distanceTo(ho);return c<t.near||c>t.far?null:{distance:c,point:ho.clone(),object:i}}function uo(i,e,t,n,s,r,a,o,l,c){i.getVertexPosition(o,fr),i.getVertexPosition(l,pr),i.getVertexPosition(c,mr);const h=Jg(i,e,t,n,fr,pr,mr,co);if(h){s&&(ao.fromBufferAttribute(s,o),oo.fromBufferAttribute(s,l),lo.fromBufferAttribute(s,c),h.uv=jn.getInterpolation(co,fr,pr,mr,ao,oo,lo,new qe)),r&&(ao.fromBufferAttribute(r,o),oo.fromBufferAttribute(r,l),lo.fromBufferAttribute(r,c),h.uv1=jn.getInterpolation(co,fr,pr,mr,ao,oo,lo,new qe)),a&&(ku.fromBufferAttribute(a,o),Hu.fromBufferAttribute(a,l),Vu.fromBufferAttribute(a,c),h.normal=jn.getInterpolation(co,fr,pr,mr,ku,Hu,Vu,new H),h.normal.dot(n.direction)>0&&h.normal.multiplyScalar(-1));const u={a:o,b:l,c,normal:new H,materialIndex:0};jn.getNormal(fr,pr,mr,u.normal),h.face=u}return h}class zi extends Xt{constructor(e=1,t=1,n=1,s=1,r=1,a=1){super(),this.type="BoxGeometry",this.parameters={width:e,height:t,depth:n,widthSegments:s,heightSegments:r,depthSegments:a};const o=this;s=Math.floor(s),r=Math.floor(r),a=Math.floor(a);const l=[],c=[],h=[],u=[];let d=0,f=0;g("z","y","x",-1,-1,n,t,e,a,r,0),g("z","y","x",1,-1,n,t,-e,a,r,1),g("x","z","y",1,1,e,n,t,s,a,2),g("x","z","y",1,-1,e,n,-t,s,a,3),g("x","y","z",1,-1,e,t,n,s,r,4),g("x","y","z",-1,-1,e,t,-n,s,r,5),this.setIndex(l),this.setAttribute("position",new qt(c,3)),this.setAttribute("normal",new qt(h,3)),this.setAttribute("uv",new qt(u,2));function g(_,m,p,S,y,w,O,A,C,F,b){const x=w/C,P=O/F,K=w/2,k=O/2,Z=A/2,q=C+1,ee=F+1;let Y=0,ne=0;const ge=new H;for(let de=0;de<ee;de++){const xe=de*P-k;for(let we=0;we<q;we++){const ye=we*x-K;ge[_]=ye*S,ge[m]=xe*y,ge[p]=Z,c.push(ge.x,ge.y,ge.z),ge[_]=0,ge[m]=0,ge[p]=A>0?1:-1,h.push(ge.x,ge.y,ge.z),u.push(we/C),u.push(1-de/F),Y+=1}}for(let de=0;de<F;de++)for(let xe=0;xe<C;xe++){const we=d+xe+q*de,ye=d+xe+q*(de+1),ie=d+(xe+1)+q*(de+1),he=d+(xe+1)+q*de;l.push(we,ye,he),l.push(ye,ie,he),ne+=6}o.addGroup(f,ne,b),f+=ne,d+=Y}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new zi(e.width,e.height,e.depth,e.widthSegments,e.heightSegments,e.depthSegments)}}function Vr(i){const e={};for(const t in i){e[t]={};for(const n in i[t]){const s=i[t][n];s&&(s.isColor||s.isMatrix3||s.isMatrix4||s.isVector2||s.isVector3||s.isVector4||s.isTexture||s.isQuaternion)?s.isRenderTargetTexture?(console.warn("UniformsUtils: Textures of render targets cannot be cloned via cloneUniforms() or mergeUniforms()."),e[t][n]=null):e[t][n]=s.clone():Array.isArray(s)?e[t][n]=s.slice():e[t][n]=s}}return e}function Cn(i){const e={};for(let t=0;t<i.length;t++){const n=Vr(i[t]);for(const s in n)e[s]=n[s]}return e}function Qg(i){const e=[];for(let t=0;t<i.length;t++)e.push(i[t].clone());return e}function jf(i){const e=i.getRenderTarget();return e===null?i.outputColorSpace:e.isXRRenderTarget===!0?e.texture.colorSpace:bt.workingColorSpace}const e_={clone:Vr,merge:Cn};var t_=`void main() {
	gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
}`,n_=`void main() {
	gl_FragColor = vec4( 1.0, 0.0, 0.0, 1.0 );
}`;class us extends ms{constructor(e){super(),this.isShaderMaterial=!0,this.type="ShaderMaterial",this.defines={},this.uniforms={},this.uniformsGroups=[],this.vertexShader=t_,this.fragmentShader=n_,this.linewidth=1,this.wireframe=!1,this.wireframeLinewidth=1,this.fog=!1,this.lights=!1,this.clipping=!1,this.forceSinglePass=!0,this.extensions={clipCullDistance:!1,multiDraw:!1},this.defaultAttributeValues={color:[1,1,1],uv:[0,0],uv1:[0,0]},this.index0AttributeName=void 0,this.uniformsNeedUpdate=!1,this.glslVersion=null,e!==void 0&&this.setValues(e)}copy(e){return super.copy(e),this.fragmentShader=e.fragmentShader,this.vertexShader=e.vertexShader,this.uniforms=Vr(e.uniforms),this.uniformsGroups=Qg(e.uniformsGroups),this.defines=Object.assign({},e.defines),this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.fog=e.fog,this.lights=e.lights,this.clipping=e.clipping,this.extensions=Object.assign({},e.extensions),this.glslVersion=e.glslVersion,this}toJSON(e){const t=super.toJSON(e);t.glslVersion=this.glslVersion,t.uniforms={};for(const s in this.uniforms){const a=this.uniforms[s].value;a&&a.isTexture?t.uniforms[s]={type:"t",value:a.toJSON(e).uuid}:a&&a.isColor?t.uniforms[s]={type:"c",value:a.getHex()}:a&&a.isVector2?t.uniforms[s]={type:"v2",value:a.toArray()}:a&&a.isVector3?t.uniforms[s]={type:"v3",value:a.toArray()}:a&&a.isVector4?t.uniforms[s]={type:"v4",value:a.toArray()}:a&&a.isMatrix3?t.uniforms[s]={type:"m3",value:a.toArray()}:a&&a.isMatrix4?t.uniforms[s]={type:"m4",value:a.toArray()}:t.uniforms[s]={value:a}}Object.keys(this.defines).length>0&&(t.defines=this.defines),t.vertexShader=this.vertexShader,t.fragmentShader=this.fragmentShader,t.lights=this.lights,t.clipping=this.clipping;const n={};for(const s in this.extensions)this.extensions[s]===!0&&(n[s]=!0);return Object.keys(n).length>0&&(t.extensions=n),t}}class Kf extends Qt{constructor(){super(),this.isCamera=!0,this.type="Camera",this.matrixWorldInverse=new Bt,this.projectionMatrix=new Bt,this.projectionMatrixInverse=new Bt,this.coordinateSystem=Bi}copy(e,t){return super.copy(e,t),this.matrixWorldInverse.copy(e.matrixWorldInverse),this.projectionMatrix.copy(e.projectionMatrix),this.projectionMatrixInverse.copy(e.projectionMatrixInverse),this.coordinateSystem=e.coordinateSystem,this}getWorldDirection(e){return super.getWorldDirection(e).negate()}updateMatrixWorld(e){super.updateMatrixWorld(e),this.matrixWorldInverse.copy(this.matrixWorld).invert()}updateWorldMatrix(e,t){super.updateWorldMatrix(e,t),this.matrixWorldInverse.copy(this.matrixWorld).invert()}clone(){return new this.constructor().copy(this)}}const ns=new H,Gu=new qe,Wu=new qe;class bn extends Kf{constructor(e=50,t=1,n=.1,s=2e3){super(),this.isPerspectiveCamera=!0,this.type="PerspectiveCamera",this.fov=e,this.zoom=1,this.near=n,this.far=s,this.focus=10,this.aspect=t,this.view=null,this.filmGauge=35,this.filmOffset=0,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.fov=e.fov,this.zoom=e.zoom,this.near=e.near,this.far=e.far,this.focus=e.focus,this.aspect=e.aspect,this.view=e.view===null?null:Object.assign({},e.view),this.filmGauge=e.filmGauge,this.filmOffset=e.filmOffset,this}setFocalLength(e){const t=.5*this.getFilmHeight()/e;this.fov=La*2*Math.atan(t),this.updateProjectionMatrix()}getFocalLength(){const e=Math.tan(Lr*.5*this.fov);return .5*this.getFilmHeight()/e}getEffectiveFOV(){return La*2*Math.atan(Math.tan(Lr*.5*this.fov)/this.zoom)}getFilmWidth(){return this.filmGauge*Math.min(this.aspect,1)}getFilmHeight(){return this.filmGauge/Math.max(this.aspect,1)}getViewBounds(e,t,n){ns.set(-1,-1,.5).applyMatrix4(this.projectionMatrixInverse),t.set(ns.x,ns.y).multiplyScalar(-e/ns.z),ns.set(1,1,.5).applyMatrix4(this.projectionMatrixInverse),n.set(ns.x,ns.y).multiplyScalar(-e/ns.z)}getViewSize(e,t){return this.getViewBounds(e,Gu,Wu),t.subVectors(Wu,Gu)}setViewOffset(e,t,n,s,r,a){this.aspect=e/t,this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=n,this.view.offsetY=s,this.view.width=r,this.view.height=a,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const e=this.near;let t=e*Math.tan(Lr*.5*this.fov)/this.zoom,n=2*t,s=this.aspect*n,r=-.5*s;const a=this.view;if(this.view!==null&&this.view.enabled){const l=a.fullWidth,c=a.fullHeight;r+=a.offsetX*s/l,t-=a.offsetY*n/c,s*=a.width/l,n*=a.height/c}const o=this.filmOffset;o!==0&&(r+=e*o/this.getFilmWidth()),this.projectionMatrix.makePerspective(r,r+s,t,t-n,e,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){const t=super.toJSON(e);return t.object.fov=this.fov,t.object.zoom=this.zoom,t.object.near=this.near,t.object.far=this.far,t.object.focus=this.focus,t.object.aspect=this.aspect,this.view!==null&&(t.object.view=Object.assign({},this.view)),t.object.filmGauge=this.filmGauge,t.object.filmOffset=this.filmOffset,t}}const gr=-90,_r=1;class i_ extends Qt{constructor(e,t,n){super(),this.type="CubeCamera",this.renderTarget=n,this.coordinateSystem=null,this.activeMipmapLevel=0;const s=new bn(gr,_r,e,t);s.layers=this.layers,this.add(s);const r=new bn(gr,_r,e,t);r.layers=this.layers,this.add(r);const a=new bn(gr,_r,e,t);a.layers=this.layers,this.add(a);const o=new bn(gr,_r,e,t);o.layers=this.layers,this.add(o);const l=new bn(gr,_r,e,t);l.layers=this.layers,this.add(l);const c=new bn(gr,_r,e,t);c.layers=this.layers,this.add(c)}updateCoordinateSystem(){const e=this.coordinateSystem,t=this.children.concat(),[n,s,r,a,o,l]=t;for(const c of t)this.remove(c);if(e===Bi)n.up.set(0,1,0),n.lookAt(1,0,0),s.up.set(0,1,0),s.lookAt(-1,0,0),r.up.set(0,0,-1),r.lookAt(0,1,0),a.up.set(0,0,1),a.lookAt(0,-1,0),o.up.set(0,1,0),o.lookAt(0,0,1),l.up.set(0,1,0),l.lookAt(0,0,-1);else if(e===Xo)n.up.set(0,-1,0),n.lookAt(-1,0,0),s.up.set(0,-1,0),s.lookAt(1,0,0),r.up.set(0,0,1),r.lookAt(0,1,0),a.up.set(0,0,-1),a.lookAt(0,-1,0),o.up.set(0,-1,0),o.lookAt(0,0,1),l.up.set(0,-1,0),l.lookAt(0,0,-1);else throw new Error("THREE.CubeCamera.updateCoordinateSystem(): Invalid coordinate system: "+e);for(const c of t)this.add(c),c.updateMatrixWorld()}update(e,t){this.parent===null&&this.updateMatrixWorld();const{renderTarget:n,activeMipmapLevel:s}=this;this.coordinateSystem!==e.coordinateSystem&&(this.coordinateSystem=e.coordinateSystem,this.updateCoordinateSystem());const[r,a,o,l,c,h]=this.children,u=e.getRenderTarget(),d=e.getActiveCubeFace(),f=e.getActiveMipmapLevel(),g=e.xr.enabled;e.xr.enabled=!1;const _=n.texture.generateMipmaps;n.texture.generateMipmaps=!1,e.setRenderTarget(n,0,s),e.render(t,r),e.setRenderTarget(n,1,s),e.render(t,a),e.setRenderTarget(n,2,s),e.render(t,o),e.setRenderTarget(n,3,s),e.render(t,l),e.setRenderTarget(n,4,s),e.render(t,c),n.texture.generateMipmaps=_,e.setRenderTarget(n,5,s),e.render(t,h),e.setRenderTarget(u,d,f),e.xr.enabled=g,n.texture.needsPMREMUpdate=!0}}class Zf extends Ln{constructor(e,t,n,s,r,a,o,l,c,h){e=e!==void 0?e:[],t=t!==void 0?t:Br,super(e,t,n,s,r,a,o,l,c,h),this.isCubeTexture=!0,this.flipY=!1}get images(){return this.image}set images(e){this.image=e}}class s_ extends zs{constructor(e=1,t={}){super(e,e,t),this.isWebGLCubeRenderTarget=!0;const n={width:e,height:e,depth:1},s=[n,n,n,n,n,n];this.texture=new Zf(s,t.mapping,t.wrapS,t.wrapT,t.magFilter,t.minFilter,t.format,t.type,t.anisotropy,t.colorSpace),this.texture.isRenderTargetTexture=!0,this.texture.generateMipmaps=t.generateMipmaps!==void 0?t.generateMipmaps:!1,this.texture.minFilter=t.minFilter!==void 0?t.minFilter:ai}fromEquirectangularTexture(e,t){this.texture.type=t.type,this.texture.colorSpace=t.colorSpace,this.texture.generateMipmaps=t.generateMipmaps,this.texture.minFilter=t.minFilter,this.texture.magFilter=t.magFilter;const n={uniforms:{tEquirect:{value:null}},vertexShader:`

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
			`},s=new zi(5,5,5),r=new us({name:"CubemapFromEquirect",uniforms:Vr(n.uniforms),vertexShader:n.vertexShader,fragmentShader:n.fragmentShader,side:In,blending:ls});r.uniforms.tEquirect.value=t;const a=new _n(s,r),o=t.minFilter;return t.minFilter===Us&&(t.minFilter=ai),new i_(1,10,this).update(e,a),t.minFilter=o,a.geometry.dispose(),a.material.dispose(),this}clear(e,t,n,s){const r=e.getRenderTarget();for(let a=0;a<6;a++)e.setRenderTarget(this,a),e.clear(t,n,s);e.setRenderTarget(r)}}const Zl=new H,r_=new H,a_=new at;class ss{constructor(e=new H(1,0,0),t=0){this.isPlane=!0,this.normal=e,this.constant=t}set(e,t){return this.normal.copy(e),this.constant=t,this}setComponents(e,t,n,s){return this.normal.set(e,t,n),this.constant=s,this}setFromNormalAndCoplanarPoint(e,t){return this.normal.copy(e),this.constant=-t.dot(this.normal),this}setFromCoplanarPoints(e,t,n){const s=Zl.subVectors(n,t).cross(r_.subVectors(e,t)).normalize();return this.setFromNormalAndCoplanarPoint(s,e),this}copy(e){return this.normal.copy(e.normal),this.constant=e.constant,this}normalize(){const e=1/this.normal.length();return this.normal.multiplyScalar(e),this.constant*=e,this}negate(){return this.constant*=-1,this.normal.negate(),this}distanceToPoint(e){return this.normal.dot(e)+this.constant}distanceToSphere(e){return this.distanceToPoint(e.center)-e.radius}projectPoint(e,t){return t.copy(e).addScaledVector(this.normal,-this.distanceToPoint(e))}intersectLine(e,t){const n=e.delta(Zl),s=this.normal.dot(n);if(s===0)return this.distanceToPoint(e.start)===0?t.copy(e.start):null;const r=-(e.start.dot(this.normal)+this.constant)/s;return r<0||r>1?null:t.copy(e.start).addScaledVector(n,r)}intersectsLine(e){const t=this.distanceToPoint(e.start),n=this.distanceToPoint(e.end);return t<0&&n>0||n<0&&t>0}intersectsBox(e){return e.intersectsPlane(this)}intersectsSphere(e){return e.intersectsPlane(this)}coplanarPoint(e){return e.copy(this.normal).multiplyScalar(-this.constant)}applyMatrix4(e,t){const n=t||a_.getNormalMatrix(e),s=this.coplanarPoint(Zl).applyMatrix4(e),r=this.normal.applyMatrix3(n).normalize();return this.constant=-s.dot(r),this}translate(e){return this.constant-=e.dot(this.normal),this}equals(e){return e.normal.equals(this.normal)&&e.constant===this.constant}clone(){return new this.constructor().copy(this)}}const Es=new Oa,fo=new H;class Eh{constructor(e=new ss,t=new ss,n=new ss,s=new ss,r=new ss,a=new ss){this.planes=[e,t,n,s,r,a]}set(e,t,n,s,r,a){const o=this.planes;return o[0].copy(e),o[1].copy(t),o[2].copy(n),o[3].copy(s),o[4].copy(r),o[5].copy(a),this}copy(e){const t=this.planes;for(let n=0;n<6;n++)t[n].copy(e.planes[n]);return this}setFromProjectionMatrix(e,t=Bi){const n=this.planes,s=e.elements,r=s[0],a=s[1],o=s[2],l=s[3],c=s[4],h=s[5],u=s[6],d=s[7],f=s[8],g=s[9],_=s[10],m=s[11],p=s[12],S=s[13],y=s[14],w=s[15];if(n[0].setComponents(l-r,d-c,m-f,w-p).normalize(),n[1].setComponents(l+r,d+c,m+f,w+p).normalize(),n[2].setComponents(l+a,d+h,m+g,w+S).normalize(),n[3].setComponents(l-a,d-h,m-g,w-S).normalize(),n[4].setComponents(l-o,d-u,m-_,w-y).normalize(),t===Bi)n[5].setComponents(l+o,d+u,m+_,w+y).normalize();else if(t===Xo)n[5].setComponents(o,u,_,y).normalize();else throw new Error("THREE.Frustum.setFromProjectionMatrix(): Invalid coordinate system: "+t);return this}intersectsObject(e){if(e.boundingSphere!==void 0)e.boundingSphere===null&&e.computeBoundingSphere(),Es.copy(e.boundingSphere).applyMatrix4(e.matrixWorld);else{const t=e.geometry;t.boundingSphere===null&&t.computeBoundingSphere(),Es.copy(t.boundingSphere).applyMatrix4(e.matrixWorld)}return this.intersectsSphere(Es)}intersectsSprite(e){return Es.center.set(0,0,0),Es.radius=.7071067811865476,Es.applyMatrix4(e.matrixWorld),this.intersectsSphere(Es)}intersectsSphere(e){const t=this.planes,n=e.center,s=-e.radius;for(let r=0;r<6;r++)if(t[r].distanceToPoint(n)<s)return!1;return!0}intersectsBox(e){const t=this.planes;for(let n=0;n<6;n++){const s=t[n];if(fo.x=s.normal.x>0?e.max.x:e.min.x,fo.y=s.normal.y>0?e.max.y:e.min.y,fo.z=s.normal.z>0?e.max.z:e.min.z,s.distanceToPoint(fo)<0)return!1}return!0}containsPoint(e){const t=this.planes;for(let n=0;n<6;n++)if(t[n].distanceToPoint(e)<0)return!1;return!0}clone(){return new this.constructor().copy(this)}}function Jf(){let i=null,e=!1,t=null,n=null;function s(r,a){t(r,a),n=i.requestAnimationFrame(s)}return{start:function(){e!==!0&&t!==null&&(n=i.requestAnimationFrame(s),e=!0)},stop:function(){i.cancelAnimationFrame(n),e=!1},setAnimationLoop:function(r){t=r},setContext:function(r){i=r}}}function o_(i){const e=new WeakMap;function t(o,l){const c=o.array,h=o.usage,u=c.byteLength,d=i.createBuffer();i.bindBuffer(l,d),i.bufferData(l,c,h),o.onUploadCallback();let f;if(c instanceof Float32Array)f=i.FLOAT;else if(c instanceof Uint16Array)o.isFloat16BufferAttribute?f=i.HALF_FLOAT:f=i.UNSIGNED_SHORT;else if(c instanceof Int16Array)f=i.SHORT;else if(c instanceof Uint32Array)f=i.UNSIGNED_INT;else if(c instanceof Int32Array)f=i.INT;else if(c instanceof Int8Array)f=i.BYTE;else if(c instanceof Uint8Array)f=i.UNSIGNED_BYTE;else if(c instanceof Uint8ClampedArray)f=i.UNSIGNED_BYTE;else throw new Error("THREE.WebGLAttributes: Unsupported buffer data format: "+c);return{buffer:d,type:f,bytesPerElement:c.BYTES_PER_ELEMENT,version:o.version,size:u}}function n(o,l,c){const h=l.array,u=l._updateRange,d=l.updateRanges;if(i.bindBuffer(c,o),u.count===-1&&d.length===0&&i.bufferSubData(c,0,h),d.length!==0){for(let f=0,g=d.length;f<g;f++){const _=d[f];i.bufferSubData(c,_.start*h.BYTES_PER_ELEMENT,h,_.start,_.count)}l.clearUpdateRanges()}u.count!==-1&&(i.bufferSubData(c,u.offset*h.BYTES_PER_ELEMENT,h,u.offset,u.count),u.count=-1),l.onUploadCallback()}function s(o){return o.isInterleavedBufferAttribute&&(o=o.data),e.get(o)}function r(o){o.isInterleavedBufferAttribute&&(o=o.data);const l=e.get(o);l&&(i.deleteBuffer(l.buffer),e.delete(o))}function a(o,l){if(o.isInterleavedBufferAttribute&&(o=o.data),o.isGLBufferAttribute){const h=e.get(o);(!h||h.version<o.version)&&e.set(o,{buffer:o.buffer,type:o.type,bytesPerElement:o.elementSize,version:o.version});return}const c=e.get(o);if(c===void 0)e.set(o,t(o,l));else if(c.version<o.version){if(c.size!==o.array.byteLength)throw new Error("THREE.WebGLAttributes: The size of the buffer attribute's array buffer does not match the original size. Resizing buffer attributes is not supported.");n(c.buffer,o,l),c.version=o.version}}return{get:s,remove:r,update:a}}class za extends Xt{constructor(e=1,t=1,n=1,s=1){super(),this.type="PlaneGeometry",this.parameters={width:e,height:t,widthSegments:n,heightSegments:s};const r=e/2,a=t/2,o=Math.floor(n),l=Math.floor(s),c=o+1,h=l+1,u=e/o,d=t/l,f=[],g=[],_=[],m=[];for(let p=0;p<h;p++){const S=p*d-a;for(let y=0;y<c;y++){const w=y*u-r;g.push(w,-S,0),_.push(0,0,1),m.push(y/o),m.push(1-p/l)}}for(let p=0;p<l;p++)for(let S=0;S<o;S++){const y=S+c*p,w=S+c*(p+1),O=S+1+c*(p+1),A=S+1+c*p;f.push(y,w,A),f.push(w,O,A)}this.setIndex(f),this.setAttribute("position",new qt(g,3)),this.setAttribute("normal",new qt(_,3)),this.setAttribute("uv",new qt(m,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new za(e.width,e.height,e.widthSegments,e.heightSegments)}}var l_=`#ifdef USE_ALPHAHASH
	if ( diffuseColor.a < getAlphaHashThreshold( vPosition ) ) discard;
#endif`,c_=`#ifdef USE_ALPHAHASH
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
#endif`,h_=`#ifdef USE_ALPHAMAP
	diffuseColor.a *= texture2D( alphaMap, vAlphaMapUv ).g;
#endif`,u_=`#ifdef USE_ALPHAMAP
	uniform sampler2D alphaMap;
#endif`,d_=`#ifdef USE_ALPHATEST
	#ifdef ALPHA_TO_COVERAGE
	diffuseColor.a = smoothstep( alphaTest, alphaTest + fwidth( diffuseColor.a ), diffuseColor.a );
	if ( diffuseColor.a == 0.0 ) discard;
	#else
	if ( diffuseColor.a < alphaTest ) discard;
	#endif
#endif`,f_=`#ifdef USE_ALPHATEST
	uniform float alphaTest;
#endif`,p_=`#ifdef USE_AOMAP
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
#endif`,m_=`#ifdef USE_AOMAP
	uniform sampler2D aoMap;
	uniform float aoMapIntensity;
#endif`,g_=`#ifdef USE_BATCHING
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
#endif`,__=`#ifdef USE_BATCHING
	mat4 batchingMatrix = getBatchingMatrix( getIndirectIndex( gl_DrawID ) );
#endif`,v_=`vec3 transformed = vec3( position );
#ifdef USE_ALPHAHASH
	vPosition = vec3( position );
#endif`,x_=`vec3 objectNormal = vec3( normal );
#ifdef USE_TANGENT
	vec3 objectTangent = vec3( tangent.xyz );
#endif`,y_=`float G_BlinnPhong_Implicit( ) {
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
} // validated`,M_=`#ifdef USE_IRIDESCENCE
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
#endif`,S_=`#ifdef USE_BUMPMAP
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
#endif`,b_=`#if NUM_CLIPPING_PLANES > 0
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
#endif`,E_=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
	uniform vec4 clippingPlanes[ NUM_CLIPPING_PLANES ];
#endif`,w_=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
#endif`,T_=`#if NUM_CLIPPING_PLANES > 0
	vClipPosition = - mvPosition.xyz;
#endif`,A_=`#if defined( USE_COLOR_ALPHA )
	diffuseColor *= vColor;
#elif defined( USE_COLOR )
	diffuseColor.rgb *= vColor;
#endif`,R_=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR )
	varying vec3 vColor;
#endif`,C_=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR ) || defined( USE_INSTANCING_COLOR ) || defined( USE_BATCHING_COLOR )
	varying vec3 vColor;
#endif`,P_=`#if defined( USE_COLOR_ALPHA )
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
#endif`,L_=`#define PI 3.141592653589793
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
} // validated`,D_=`#ifdef ENVMAP_TYPE_CUBE_UV
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
#endif`,I_=`vec3 transformedNormal = objectNormal;
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
#endif`,U_=`#ifdef USE_DISPLACEMENTMAP
	uniform sampler2D displacementMap;
	uniform float displacementScale;
	uniform float displacementBias;
#endif`,N_=`#ifdef USE_DISPLACEMENTMAP
	transformed += normalize( objectNormal ) * ( texture2D( displacementMap, vDisplacementMapUv ).x * displacementScale + displacementBias );
#endif`,F_=`#ifdef USE_EMISSIVEMAP
	vec4 emissiveColor = texture2D( emissiveMap, vEmissiveMapUv );
	totalEmissiveRadiance *= emissiveColor.rgb;
#endif`,O_=`#ifdef USE_EMISSIVEMAP
	uniform sampler2D emissiveMap;
#endif`,B_="gl_FragColor = linearToOutputTexel( gl_FragColor );",z_=`
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
}`,k_=`#ifdef USE_ENVMAP
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
#endif`,H_=`#ifdef USE_ENVMAP
	uniform float envMapIntensity;
	uniform float flipEnvMap;
	uniform mat3 envMapRotation;
	#ifdef ENVMAP_TYPE_CUBE
		uniform samplerCube envMap;
	#else
		uniform sampler2D envMap;
	#endif
	
#endif`,V_=`#ifdef USE_ENVMAP
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
#endif`,G_=`#ifdef USE_ENVMAP
	#if defined( USE_BUMPMAP ) || defined( USE_NORMALMAP ) || defined( PHONG ) || defined( LAMBERT )
		#define ENV_WORLDPOS
	#endif
	#ifdef ENV_WORLDPOS
		
		varying vec3 vWorldPosition;
	#else
		varying vec3 vReflect;
		uniform float refractionRatio;
	#endif
#endif`,W_=`#ifdef USE_ENVMAP
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
#endif`,X_=`#ifdef USE_FOG
	vFogDepth = - mvPosition.z;
#endif`,q_=`#ifdef USE_FOG
	varying float vFogDepth;
#endif`,$_=`#ifdef USE_FOG
	#ifdef FOG_EXP2
		float fogFactor = 1.0 - exp( - fogDensity * fogDensity * vFogDepth * vFogDepth );
	#else
		float fogFactor = smoothstep( fogNear, fogFar, vFogDepth );
	#endif
	gl_FragColor.rgb = mix( gl_FragColor.rgb, fogColor, fogFactor );
#endif`,Y_=`#ifdef USE_FOG
	uniform vec3 fogColor;
	varying float vFogDepth;
	#ifdef FOG_EXP2
		uniform float fogDensity;
	#else
		uniform float fogNear;
		uniform float fogFar;
	#endif
#endif`,j_=`#ifdef USE_GRADIENTMAP
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
}`,K_=`#ifdef USE_LIGHTMAP
	uniform sampler2D lightMap;
	uniform float lightMapIntensity;
#endif`,Z_=`LambertMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularStrength = specularStrength;`,J_=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Lambert`,Q_=`uniform bool receiveShadow;
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
#endif`,e0=`#ifdef USE_ENVMAP
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
#endif`,t0=`ToonMaterial material;
material.diffuseColor = diffuseColor.rgb;`,n0=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Toon`,i0=`BlinnPhongMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularColor = specular;
material.specularShininess = shininess;
material.specularStrength = specularStrength;`,s0=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_BlinnPhong`,r0=`PhysicalMaterial material;
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
#endif`,a0=`struct PhysicalMaterial {
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
}`,o0=`
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
#endif`,l0=`#if defined( RE_IndirectDiffuse )
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
#endif`,c0=`#if defined( RE_IndirectDiffuse )
	RE_IndirectDiffuse( irradiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif
#if defined( RE_IndirectSpecular )
	RE_IndirectSpecular( radiance, iblIrradiance, clearcoatRadiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif`,h0=`#if defined( USE_LOGDEPTHBUF )
	gl_FragDepth = vIsPerspective == 0.0 ? gl_FragCoord.z : log2( vFragDepth ) * logDepthBufFC * 0.5;
#endif`,u0=`#if defined( USE_LOGDEPTHBUF )
	uniform float logDepthBufFC;
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,d0=`#ifdef USE_LOGDEPTHBUF
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,f0=`#ifdef USE_LOGDEPTHBUF
	vFragDepth = 1.0 + gl_Position.w;
	vIsPerspective = float( isPerspectiveMatrix( projectionMatrix ) );
#endif`,p0=`#ifdef USE_MAP
	vec4 sampledDiffuseColor = texture2D( map, vMapUv );
	#ifdef DECODE_VIDEO_TEXTURE
		sampledDiffuseColor = vec4( mix( pow( sampledDiffuseColor.rgb * 0.9478672986 + vec3( 0.0521327014 ), vec3( 2.4 ) ), sampledDiffuseColor.rgb * 0.0773993808, vec3( lessThanEqual( sampledDiffuseColor.rgb, vec3( 0.04045 ) ) ) ), sampledDiffuseColor.w );
	
	#endif
	diffuseColor *= sampledDiffuseColor;
#endif`,m0=`#ifdef USE_MAP
	uniform sampler2D map;
#endif`,g0=`#if defined( USE_MAP ) || defined( USE_ALPHAMAP )
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
#endif`,_0=`#if defined( USE_POINTS_UV )
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
#endif`,v0=`float metalnessFactor = metalness;
#ifdef USE_METALNESSMAP
	vec4 texelMetalness = texture2D( metalnessMap, vMetalnessMapUv );
	metalnessFactor *= texelMetalness.b;
#endif`,x0=`#ifdef USE_METALNESSMAP
	uniform sampler2D metalnessMap;
#endif`,y0=`#ifdef USE_INSTANCING_MORPH
	float morphTargetInfluences[ MORPHTARGETS_COUNT ];
	float morphTargetBaseInfluence = texelFetch( morphTexture, ivec2( 0, gl_InstanceID ), 0 ).r;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		morphTargetInfluences[i] =  texelFetch( morphTexture, ivec2( i + 1, gl_InstanceID ), 0 ).r;
	}
#endif`,M0=`#if defined( USE_MORPHCOLORS )
	vColor *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		#if defined( USE_COLOR_ALPHA )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ) * morphTargetInfluences[ i ];
		#elif defined( USE_COLOR )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ).rgb * morphTargetInfluences[ i ];
		#endif
	}
#endif`,S0=`#ifdef USE_MORPHNORMALS
	objectNormal *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) objectNormal += getMorph( gl_VertexID, i, 1 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,b0=`#ifdef USE_MORPHTARGETS
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
#endif`,E0=`#ifdef USE_MORPHTARGETS
	transformed *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) transformed += getMorph( gl_VertexID, i, 0 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,w0=`float faceDirection = gl_FrontFacing ? 1.0 : - 1.0;
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
vec3 nonPerturbedNormal = normal;`,T0=`#ifdef USE_NORMALMAP_OBJECTSPACE
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
#endif`,A0=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,R0=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,C0=`#ifndef FLAT_SHADED
	vNormal = normalize( transformedNormal );
	#ifdef USE_TANGENT
		vTangent = normalize( transformedTangent );
		vBitangent = normalize( cross( vNormal, vTangent ) * tangent.w );
	#endif
#endif`,P0=`#ifdef USE_NORMALMAP
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
#endif`,L0=`#ifdef USE_CLEARCOAT
	vec3 clearcoatNormal = nonPerturbedNormal;
#endif`,D0=`#ifdef USE_CLEARCOAT_NORMALMAP
	vec3 clearcoatMapN = texture2D( clearcoatNormalMap, vClearcoatNormalMapUv ).xyz * 2.0 - 1.0;
	clearcoatMapN.xy *= clearcoatNormalScale;
	clearcoatNormal = normalize( tbn2 * clearcoatMapN );
#endif`,I0=`#ifdef USE_CLEARCOATMAP
	uniform sampler2D clearcoatMap;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	uniform sampler2D clearcoatNormalMap;
	uniform vec2 clearcoatNormalScale;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	uniform sampler2D clearcoatRoughnessMap;
#endif`,U0=`#ifdef USE_IRIDESCENCEMAP
	uniform sampler2D iridescenceMap;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	uniform sampler2D iridescenceThicknessMap;
#endif`,N0=`#ifdef OPAQUE
diffuseColor.a = 1.0;
#endif
#ifdef USE_TRANSMISSION
diffuseColor.a *= material.transmissionAlpha;
#endif
gl_FragColor = vec4( outgoingLight, diffuseColor.a );`,F0=`vec3 packNormalToRGB( const in vec3 normal ) {
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
}`,O0=`#ifdef PREMULTIPLIED_ALPHA
	gl_FragColor.rgb *= gl_FragColor.a;
#endif`,B0=`vec4 mvPosition = vec4( transformed, 1.0 );
#ifdef USE_BATCHING
	mvPosition = batchingMatrix * mvPosition;
#endif
#ifdef USE_INSTANCING
	mvPosition = instanceMatrix * mvPosition;
#endif
mvPosition = modelViewMatrix * mvPosition;
gl_Position = projectionMatrix * mvPosition;`,z0=`#ifdef DITHERING
	gl_FragColor.rgb = dithering( gl_FragColor.rgb );
#endif`,k0=`#ifdef DITHERING
	vec3 dithering( vec3 color ) {
		float grid_position = rand( gl_FragCoord.xy );
		vec3 dither_shift_RGB = vec3( 0.25 / 255.0, -0.25 / 255.0, 0.25 / 255.0 );
		dither_shift_RGB = mix( 2.0 * dither_shift_RGB, -2.0 * dither_shift_RGB, grid_position );
		return color + dither_shift_RGB;
	}
#endif`,H0=`float roughnessFactor = roughness;
#ifdef USE_ROUGHNESSMAP
	vec4 texelRoughness = texture2D( roughnessMap, vRoughnessMapUv );
	roughnessFactor *= texelRoughness.g;
#endif`,V0=`#ifdef USE_ROUGHNESSMAP
	uniform sampler2D roughnessMap;
#endif`,G0=`#if NUM_SPOT_LIGHT_COORDS > 0
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
#endif`,W0=`#if NUM_SPOT_LIGHT_COORDS > 0
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
#endif`,X0=`#if ( defined( USE_SHADOWMAP ) && ( NUM_DIR_LIGHT_SHADOWS > 0 || NUM_POINT_LIGHT_SHADOWS > 0 ) ) || ( NUM_SPOT_LIGHT_COORDS > 0 )
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
#endif`,q0=`float getShadowMask() {
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
}`,$0=`#ifdef USE_SKINNING
	mat4 boneMatX = getBoneMatrix( skinIndex.x );
	mat4 boneMatY = getBoneMatrix( skinIndex.y );
	mat4 boneMatZ = getBoneMatrix( skinIndex.z );
	mat4 boneMatW = getBoneMatrix( skinIndex.w );
#endif`,Y0=`#ifdef USE_SKINNING
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
#endif`,j0=`#ifdef USE_SKINNING
	vec4 skinVertex = bindMatrix * vec4( transformed, 1.0 );
	vec4 skinned = vec4( 0.0 );
	skinned += boneMatX * skinVertex * skinWeight.x;
	skinned += boneMatY * skinVertex * skinWeight.y;
	skinned += boneMatZ * skinVertex * skinWeight.z;
	skinned += boneMatW * skinVertex * skinWeight.w;
	transformed = ( bindMatrixInverse * skinned ).xyz;
#endif`,K0=`#ifdef USE_SKINNING
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
#endif`,Z0=`float specularStrength;
#ifdef USE_SPECULARMAP
	vec4 texelSpecular = texture2D( specularMap, vSpecularMapUv );
	specularStrength = texelSpecular.r;
#else
	specularStrength = 1.0;
#endif`,J0=`#ifdef USE_SPECULARMAP
	uniform sampler2D specularMap;
#endif`,Q0=`#if defined( TONE_MAPPING )
	gl_FragColor.rgb = toneMapping( gl_FragColor.rgb );
#endif`,ev=`#ifndef saturate
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
vec3 CustomToneMapping( vec3 color ) { return color; }`,tv=`#ifdef USE_TRANSMISSION
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
#endif`,nv=`#ifdef USE_TRANSMISSION
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
#endif`,iv=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
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
#endif`,sv=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
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
#endif`,rv=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
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
#endif`,av=`#if defined( USE_ENVMAP ) || defined( DISTANCE ) || defined ( USE_SHADOWMAP ) || defined ( USE_TRANSMISSION ) || NUM_SPOT_LIGHT_COORDS > 0
	vec4 worldPosition = vec4( transformed, 1.0 );
	#ifdef USE_BATCHING
		worldPosition = batchingMatrix * worldPosition;
	#endif
	#ifdef USE_INSTANCING
		worldPosition = instanceMatrix * worldPosition;
	#endif
	worldPosition = modelMatrix * worldPosition;
#endif`;const ov=`varying vec2 vUv;
uniform mat3 uvTransform;
void main() {
	vUv = ( uvTransform * vec3( uv, 1 ) ).xy;
	gl_Position = vec4( position.xy, 1.0, 1.0 );
}`,lv=`uniform sampler2D t2D;
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
}`,cv=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,hv=`#ifdef ENVMAP_TYPE_CUBE
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
}`,uv=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,dv=`uniform samplerCube tCube;
uniform float tFlip;
uniform float opacity;
varying vec3 vWorldDirection;
void main() {
	vec4 texColor = textureCube( tCube, vec3( tFlip * vWorldDirection.x, vWorldDirection.yz ) );
	gl_FragColor = texColor;
	gl_FragColor.a *= opacity;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,fv=`#include <common>
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
}`,pv=`#if DEPTH_PACKING == 3200
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
}`,mv=`#define DISTANCE
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
}`,gv=`#define DISTANCE
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
}`,_v=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
}`,vv=`uniform sampler2D tEquirect;
varying vec3 vWorldDirection;
#include <common>
void main() {
	vec3 direction = normalize( vWorldDirection );
	vec2 sampleUV = equirectUv( direction );
	gl_FragColor = texture2D( tEquirect, sampleUV );
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,xv=`uniform float scale;
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
}`,yv=`uniform vec3 diffuse;
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
}`,Mv=`#include <common>
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
}`,Sv=`uniform vec3 diffuse;
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
}`,bv=`#define LAMBERT
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
}`,Ev=`#define LAMBERT
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
}`,wv=`#define MATCAP
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
}`,Tv=`#define MATCAP
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
}`,Av=`#define NORMAL
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
}`,Rv=`#define NORMAL
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
}`,Cv=`#define PHONG
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
}`,Pv=`#define PHONG
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
}`,Lv=`#define STANDARD
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
}`,Dv=`#define STANDARD
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
}`,Iv=`#define TOON
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
}`,Uv=`#define TOON
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
}`,Nv=`uniform float size;
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
}`,Fv=`uniform vec3 diffuse;
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
}`,Ov=`#include <common>
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
}`,Bv=`uniform vec3 color;
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
}`,zv=`uniform float rotation;
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
}`,kv=`uniform vec3 diffuse;
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
}`,rt={alphahash_fragment:l_,alphahash_pars_fragment:c_,alphamap_fragment:h_,alphamap_pars_fragment:u_,alphatest_fragment:d_,alphatest_pars_fragment:f_,aomap_fragment:p_,aomap_pars_fragment:m_,batching_pars_vertex:g_,batching_vertex:__,begin_vertex:v_,beginnormal_vertex:x_,bsdfs:y_,iridescence_fragment:M_,bumpmap_pars_fragment:S_,clipping_planes_fragment:b_,clipping_planes_pars_fragment:E_,clipping_planes_pars_vertex:w_,clipping_planes_vertex:T_,color_fragment:A_,color_pars_fragment:R_,color_pars_vertex:C_,color_vertex:P_,common:L_,cube_uv_reflection_fragment:D_,defaultnormal_vertex:I_,displacementmap_pars_vertex:U_,displacementmap_vertex:N_,emissivemap_fragment:F_,emissivemap_pars_fragment:O_,colorspace_fragment:B_,colorspace_pars_fragment:z_,envmap_fragment:k_,envmap_common_pars_fragment:H_,envmap_pars_fragment:V_,envmap_pars_vertex:G_,envmap_physical_pars_fragment:e0,envmap_vertex:W_,fog_vertex:X_,fog_pars_vertex:q_,fog_fragment:$_,fog_pars_fragment:Y_,gradientmap_pars_fragment:j_,lightmap_pars_fragment:K_,lights_lambert_fragment:Z_,lights_lambert_pars_fragment:J_,lights_pars_begin:Q_,lights_toon_fragment:t0,lights_toon_pars_fragment:n0,lights_phong_fragment:i0,lights_phong_pars_fragment:s0,lights_physical_fragment:r0,lights_physical_pars_fragment:a0,lights_fragment_begin:o0,lights_fragment_maps:l0,lights_fragment_end:c0,logdepthbuf_fragment:h0,logdepthbuf_pars_fragment:u0,logdepthbuf_pars_vertex:d0,logdepthbuf_vertex:f0,map_fragment:p0,map_pars_fragment:m0,map_particle_fragment:g0,map_particle_pars_fragment:_0,metalnessmap_fragment:v0,metalnessmap_pars_fragment:x0,morphinstance_vertex:y0,morphcolor_vertex:M0,morphnormal_vertex:S0,morphtarget_pars_vertex:b0,morphtarget_vertex:E0,normal_fragment_begin:w0,normal_fragment_maps:T0,normal_pars_fragment:A0,normal_pars_vertex:R0,normal_vertex:C0,normalmap_pars_fragment:P0,clearcoat_normal_fragment_begin:L0,clearcoat_normal_fragment_maps:D0,clearcoat_pars_fragment:I0,iridescence_pars_fragment:U0,opaque_fragment:N0,packing:F0,premultiplied_alpha_fragment:O0,project_vertex:B0,dithering_fragment:z0,dithering_pars_fragment:k0,roughnessmap_fragment:H0,roughnessmap_pars_fragment:V0,shadowmap_pars_fragment:G0,shadowmap_pars_vertex:W0,shadowmap_vertex:X0,shadowmask_pars_fragment:q0,skinbase_vertex:$0,skinning_pars_vertex:Y0,skinning_vertex:j0,skinnormal_vertex:K0,specularmap_fragment:Z0,specularmap_pars_fragment:J0,tonemapping_fragment:Q0,tonemapping_pars_fragment:ev,transmission_fragment:tv,transmission_pars_fragment:nv,uv_pars_fragment:iv,uv_pars_vertex:sv,uv_vertex:rv,worldpos_vertex:av,background_vert:ov,background_frag:lv,backgroundCube_vert:cv,backgroundCube_frag:hv,cube_vert:uv,cube_frag:dv,depth_vert:fv,depth_frag:pv,distanceRGBA_vert:mv,distanceRGBA_frag:gv,equirect_vert:_v,equirect_frag:vv,linedashed_vert:xv,linedashed_frag:yv,meshbasic_vert:Mv,meshbasic_frag:Sv,meshlambert_vert:bv,meshlambert_frag:Ev,meshmatcap_vert:wv,meshmatcap_frag:Tv,meshnormal_vert:Av,meshnormal_frag:Rv,meshphong_vert:Cv,meshphong_frag:Pv,meshphysical_vert:Lv,meshphysical_frag:Dv,meshtoon_vert:Iv,meshtoon_frag:Uv,points_vert:Nv,points_frag:Fv,shadow_vert:Ov,shadow_frag:Bv,sprite_vert:zv,sprite_frag:kv},Re={common:{diffuse:{value:new nt(16777215)},opacity:{value:1},map:{value:null},mapTransform:{value:new at},alphaMap:{value:null},alphaMapTransform:{value:new at},alphaTest:{value:0}},specularmap:{specularMap:{value:null},specularMapTransform:{value:new at}},envmap:{envMap:{value:null},envMapRotation:{value:new at},flipEnvMap:{value:-1},reflectivity:{value:1},ior:{value:1.5},refractionRatio:{value:.98}},aomap:{aoMap:{value:null},aoMapIntensity:{value:1},aoMapTransform:{value:new at}},lightmap:{lightMap:{value:null},lightMapIntensity:{value:1},lightMapTransform:{value:new at}},bumpmap:{bumpMap:{value:null},bumpMapTransform:{value:new at},bumpScale:{value:1}},normalmap:{normalMap:{value:null},normalMapTransform:{value:new at},normalScale:{value:new qe(1,1)}},displacementmap:{displacementMap:{value:null},displacementMapTransform:{value:new at},displacementScale:{value:1},displacementBias:{value:0}},emissivemap:{emissiveMap:{value:null},emissiveMapTransform:{value:new at}},metalnessmap:{metalnessMap:{value:null},metalnessMapTransform:{value:new at}},roughnessmap:{roughnessMap:{value:null},roughnessMapTransform:{value:new at}},gradientmap:{gradientMap:{value:null}},fog:{fogDensity:{value:25e-5},fogNear:{value:1},fogFar:{value:2e3},fogColor:{value:new nt(16777215)}},lights:{ambientLightColor:{value:[]},lightProbe:{value:[]},directionalLights:{value:[],properties:{direction:{},color:{}}},directionalLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},directionalShadowMap:{value:[]},directionalShadowMatrix:{value:[]},spotLights:{value:[],properties:{color:{},position:{},direction:{},distance:{},coneCos:{},penumbraCos:{},decay:{}}},spotLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},spotLightMap:{value:[]},spotShadowMap:{value:[]},spotLightMatrix:{value:[]},pointLights:{value:[],properties:{color:{},position:{},decay:{},distance:{}}},pointLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{},shadowCameraNear:{},shadowCameraFar:{}}},pointShadowMap:{value:[]},pointShadowMatrix:{value:[]},hemisphereLights:{value:[],properties:{direction:{},skyColor:{},groundColor:{}}},rectAreaLights:{value:[],properties:{color:{},position:{},width:{},height:{}}},ltc_1:{value:null},ltc_2:{value:null}},points:{diffuse:{value:new nt(16777215)},opacity:{value:1},size:{value:1},scale:{value:1},map:{value:null},alphaMap:{value:null},alphaMapTransform:{value:new at},alphaTest:{value:0},uvTransform:{value:new at}},sprite:{diffuse:{value:new nt(16777215)},opacity:{value:1},center:{value:new qe(.5,.5)},rotation:{value:0},map:{value:null},mapTransform:{value:new at},alphaMap:{value:null},alphaMapTransform:{value:new at},alphaTest:{value:0}}},yi={basic:{uniforms:Cn([Re.common,Re.specularmap,Re.envmap,Re.aomap,Re.lightmap,Re.fog]),vertexShader:rt.meshbasic_vert,fragmentShader:rt.meshbasic_frag},lambert:{uniforms:Cn([Re.common,Re.specularmap,Re.envmap,Re.aomap,Re.lightmap,Re.emissivemap,Re.bumpmap,Re.normalmap,Re.displacementmap,Re.fog,Re.lights,{emissive:{value:new nt(0)}}]),vertexShader:rt.meshlambert_vert,fragmentShader:rt.meshlambert_frag},phong:{uniforms:Cn([Re.common,Re.specularmap,Re.envmap,Re.aomap,Re.lightmap,Re.emissivemap,Re.bumpmap,Re.normalmap,Re.displacementmap,Re.fog,Re.lights,{emissive:{value:new nt(0)},specular:{value:new nt(1118481)},shininess:{value:30}}]),vertexShader:rt.meshphong_vert,fragmentShader:rt.meshphong_frag},standard:{uniforms:Cn([Re.common,Re.envmap,Re.aomap,Re.lightmap,Re.emissivemap,Re.bumpmap,Re.normalmap,Re.displacementmap,Re.roughnessmap,Re.metalnessmap,Re.fog,Re.lights,{emissive:{value:new nt(0)},roughness:{value:1},metalness:{value:0},envMapIntensity:{value:1}}]),vertexShader:rt.meshphysical_vert,fragmentShader:rt.meshphysical_frag},toon:{uniforms:Cn([Re.common,Re.aomap,Re.lightmap,Re.emissivemap,Re.bumpmap,Re.normalmap,Re.displacementmap,Re.gradientmap,Re.fog,Re.lights,{emissive:{value:new nt(0)}}]),vertexShader:rt.meshtoon_vert,fragmentShader:rt.meshtoon_frag},matcap:{uniforms:Cn([Re.common,Re.bumpmap,Re.normalmap,Re.displacementmap,Re.fog,{matcap:{value:null}}]),vertexShader:rt.meshmatcap_vert,fragmentShader:rt.meshmatcap_frag},points:{uniforms:Cn([Re.points,Re.fog]),vertexShader:rt.points_vert,fragmentShader:rt.points_frag},dashed:{uniforms:Cn([Re.common,Re.fog,{scale:{value:1},dashSize:{value:1},totalSize:{value:2}}]),vertexShader:rt.linedashed_vert,fragmentShader:rt.linedashed_frag},depth:{uniforms:Cn([Re.common,Re.displacementmap]),vertexShader:rt.depth_vert,fragmentShader:rt.depth_frag},normal:{uniforms:Cn([Re.common,Re.bumpmap,Re.normalmap,Re.displacementmap,{opacity:{value:1}}]),vertexShader:rt.meshnormal_vert,fragmentShader:rt.meshnormal_frag},sprite:{uniforms:Cn([Re.sprite,Re.fog]),vertexShader:rt.sprite_vert,fragmentShader:rt.sprite_frag},background:{uniforms:{uvTransform:{value:new at},t2D:{value:null},backgroundIntensity:{value:1}},vertexShader:rt.background_vert,fragmentShader:rt.background_frag},backgroundCube:{uniforms:{envMap:{value:null},flipEnvMap:{value:-1},backgroundBlurriness:{value:0},backgroundIntensity:{value:1},backgroundRotation:{value:new at}},vertexShader:rt.backgroundCube_vert,fragmentShader:rt.backgroundCube_frag},cube:{uniforms:{tCube:{value:null},tFlip:{value:-1},opacity:{value:1}},vertexShader:rt.cube_vert,fragmentShader:rt.cube_frag},equirect:{uniforms:{tEquirect:{value:null}},vertexShader:rt.equirect_vert,fragmentShader:rt.equirect_frag},distanceRGBA:{uniforms:Cn([Re.common,Re.displacementmap,{referencePosition:{value:new H},nearDistance:{value:1},farDistance:{value:1e3}}]),vertexShader:rt.distanceRGBA_vert,fragmentShader:rt.distanceRGBA_frag},shadow:{uniforms:Cn([Re.lights,Re.fog,{color:{value:new nt(0)},opacity:{value:1}}]),vertexShader:rt.shadow_vert,fragmentShader:rt.shadow_frag}};yi.physical={uniforms:Cn([yi.standard.uniforms,{clearcoat:{value:0},clearcoatMap:{value:null},clearcoatMapTransform:{value:new at},clearcoatNormalMap:{value:null},clearcoatNormalMapTransform:{value:new at},clearcoatNormalScale:{value:new qe(1,1)},clearcoatRoughness:{value:0},clearcoatRoughnessMap:{value:null},clearcoatRoughnessMapTransform:{value:new at},dispersion:{value:0},iridescence:{value:0},iridescenceMap:{value:null},iridescenceMapTransform:{value:new at},iridescenceIOR:{value:1.3},iridescenceThicknessMinimum:{value:100},iridescenceThicknessMaximum:{value:400},iridescenceThicknessMap:{value:null},iridescenceThicknessMapTransform:{value:new at},sheen:{value:0},sheenColor:{value:new nt(0)},sheenColorMap:{value:null},sheenColorMapTransform:{value:new at},sheenRoughness:{value:1},sheenRoughnessMap:{value:null},sheenRoughnessMapTransform:{value:new at},transmission:{value:0},transmissionMap:{value:null},transmissionMapTransform:{value:new at},transmissionSamplerSize:{value:new qe},transmissionSamplerMap:{value:null},thickness:{value:0},thicknessMap:{value:null},thicknessMapTransform:{value:new at},attenuationDistance:{value:0},attenuationColor:{value:new nt(0)},specularColor:{value:new nt(1,1,1)},specularColorMap:{value:null},specularColorMapTransform:{value:new at},specularIntensity:{value:1},specularIntensityMap:{value:null},specularIntensityMapTransform:{value:new at},anisotropyVector:{value:new qe},anisotropyMap:{value:null},anisotropyMapTransform:{value:new at}}]),vertexShader:rt.meshphysical_vert,fragmentShader:rt.meshphysical_frag};const po={r:0,b:0,g:0},ws=new Si,Hv=new Bt;function Vv(i,e,t,n,s,r,a){const o=new nt(0);let l=r===!0?0:1,c,h,u=null,d=0,f=null;function g(S){let y=S.isScene===!0?S.background:null;return y&&y.isTexture&&(y=(S.backgroundBlurriness>0?t:e).get(y)),y}function _(S){let y=!1;const w=g(S);w===null?p(o,l):w&&w.isColor&&(p(w,1),y=!0);const O=i.xr.getEnvironmentBlendMode();O==="additive"?n.buffers.color.setClear(0,0,0,1,a):O==="alpha-blend"&&n.buffers.color.setClear(0,0,0,0,a),(i.autoClear||y)&&(n.buffers.depth.setTest(!0),n.buffers.depth.setMask(!0),n.buffers.color.setMask(!0),i.clear(i.autoClearColor,i.autoClearDepth,i.autoClearStencil))}function m(S,y){const w=g(y);w&&(w.isCubeTexture||w.mapping===rl)?(h===void 0&&(h=new _n(new zi(1,1,1),new us({name:"BackgroundCubeMaterial",uniforms:Vr(yi.backgroundCube.uniforms),vertexShader:yi.backgroundCube.vertexShader,fragmentShader:yi.backgroundCube.fragmentShader,side:In,depthTest:!1,depthWrite:!1,fog:!1})),h.geometry.deleteAttribute("normal"),h.geometry.deleteAttribute("uv"),h.onBeforeRender=function(O,A,C){this.matrixWorld.copyPosition(C.matrixWorld)},Object.defineProperty(h.material,"envMap",{get:function(){return this.uniforms.envMap.value}}),s.update(h)),ws.copy(y.backgroundRotation),ws.x*=-1,ws.y*=-1,ws.z*=-1,w.isCubeTexture&&w.isRenderTargetTexture===!1&&(ws.y*=-1,ws.z*=-1),h.material.uniforms.envMap.value=w,h.material.uniforms.flipEnvMap.value=w.isCubeTexture&&w.isRenderTargetTexture===!1?-1:1,h.material.uniforms.backgroundBlurriness.value=y.backgroundBlurriness,h.material.uniforms.backgroundIntensity.value=y.backgroundIntensity,h.material.uniforms.backgroundRotation.value.setFromMatrix4(Hv.makeRotationFromEuler(ws)),h.material.toneMapped=bt.getTransfer(w.colorSpace)!==Ot,(u!==w||d!==w.version||f!==i.toneMapping)&&(h.material.needsUpdate=!0,u=w,d=w.version,f=i.toneMapping),h.layers.enableAll(),S.unshift(h,h.geometry,h.material,0,0,null)):w&&w.isTexture&&(c===void 0&&(c=new _n(new za(2,2),new us({name:"BackgroundMaterial",uniforms:Vr(yi.background.uniforms),vertexShader:yi.background.vertexShader,fragmentShader:yi.background.fragmentShader,side:hs,depthTest:!1,depthWrite:!1,fog:!1})),c.geometry.deleteAttribute("normal"),Object.defineProperty(c.material,"map",{get:function(){return this.uniforms.t2D.value}}),s.update(c)),c.material.uniforms.t2D.value=w,c.material.uniforms.backgroundIntensity.value=y.backgroundIntensity,c.material.toneMapped=bt.getTransfer(w.colorSpace)!==Ot,w.matrixAutoUpdate===!0&&w.updateMatrix(),c.material.uniforms.uvTransform.value.copy(w.matrix),(u!==w||d!==w.version||f!==i.toneMapping)&&(c.material.needsUpdate=!0,u=w,d=w.version,f=i.toneMapping),c.layers.enableAll(),S.unshift(c,c.geometry,c.material,0,0,null))}function p(S,y){S.getRGB(po,jf(i)),n.buffers.color.setClear(po.r,po.g,po.b,y,a)}return{getClearColor:function(){return o},setClearColor:function(S,y=1){o.set(S),l=y,p(o,l)},getClearAlpha:function(){return l},setClearAlpha:function(S){l=S,p(o,l)},render:_,addToRenderList:m}}function Gv(i,e){const t=i.getParameter(i.MAX_VERTEX_ATTRIBS),n={},s=d(null);let r=s,a=!1;function o(x,P,K,k,Z){let q=!1;const ee=u(k,K,P);r!==ee&&(r=ee,c(r.object)),q=f(x,k,K,Z),q&&g(x,k,K,Z),Z!==null&&e.update(Z,i.ELEMENT_ARRAY_BUFFER),(q||a)&&(a=!1,w(x,P,K,k),Z!==null&&i.bindBuffer(i.ELEMENT_ARRAY_BUFFER,e.get(Z).buffer))}function l(){return i.createVertexArray()}function c(x){return i.bindVertexArray(x)}function h(x){return i.deleteVertexArray(x)}function u(x,P,K){const k=K.wireframe===!0;let Z=n[x.id];Z===void 0&&(Z={},n[x.id]=Z);let q=Z[P.id];q===void 0&&(q={},Z[P.id]=q);let ee=q[k];return ee===void 0&&(ee=d(l()),q[k]=ee),ee}function d(x){const P=[],K=[],k=[];for(let Z=0;Z<t;Z++)P[Z]=0,K[Z]=0,k[Z]=0;return{geometry:null,program:null,wireframe:!1,newAttributes:P,enabledAttributes:K,attributeDivisors:k,object:x,attributes:{},index:null}}function f(x,P,K,k){const Z=r.attributes,q=P.attributes;let ee=0;const Y=K.getAttributes();for(const ne in Y)if(Y[ne].location>=0){const de=Z[ne];let xe=q[ne];if(xe===void 0&&(ne==="instanceMatrix"&&x.instanceMatrix&&(xe=x.instanceMatrix),ne==="instanceColor"&&x.instanceColor&&(xe=x.instanceColor)),de===void 0||de.attribute!==xe||xe&&de.data!==xe.data)return!0;ee++}return r.attributesNum!==ee||r.index!==k}function g(x,P,K,k){const Z={},q=P.attributes;let ee=0;const Y=K.getAttributes();for(const ne in Y)if(Y[ne].location>=0){let de=q[ne];de===void 0&&(ne==="instanceMatrix"&&x.instanceMatrix&&(de=x.instanceMatrix),ne==="instanceColor"&&x.instanceColor&&(de=x.instanceColor));const xe={};xe.attribute=de,de&&de.data&&(xe.data=de.data),Z[ne]=xe,ee++}r.attributes=Z,r.attributesNum=ee,r.index=k}function _(){const x=r.newAttributes;for(let P=0,K=x.length;P<K;P++)x[P]=0}function m(x){p(x,0)}function p(x,P){const K=r.newAttributes,k=r.enabledAttributes,Z=r.attributeDivisors;K[x]=1,k[x]===0&&(i.enableVertexAttribArray(x),k[x]=1),Z[x]!==P&&(i.vertexAttribDivisor(x,P),Z[x]=P)}function S(){const x=r.newAttributes,P=r.enabledAttributes;for(let K=0,k=P.length;K<k;K++)P[K]!==x[K]&&(i.disableVertexAttribArray(K),P[K]=0)}function y(x,P,K,k,Z,q,ee){ee===!0?i.vertexAttribIPointer(x,P,K,Z,q):i.vertexAttribPointer(x,P,K,k,Z,q)}function w(x,P,K,k){_();const Z=k.attributes,q=K.getAttributes(),ee=P.defaultAttributeValues;for(const Y in q){const ne=q[Y];if(ne.location>=0){let ge=Z[Y];if(ge===void 0&&(Y==="instanceMatrix"&&x.instanceMatrix&&(ge=x.instanceMatrix),Y==="instanceColor"&&x.instanceColor&&(ge=x.instanceColor)),ge!==void 0){const de=ge.normalized,xe=ge.itemSize,we=e.get(ge);if(we===void 0)continue;const ye=we.buffer,ie=we.type,he=we.bytesPerElement,Me=ie===i.INT||ie===i.UNSIGNED_INT||ge.gpuType===mh;if(ge.isInterleavedBufferAttribute){const fe=ge.data,ze=fe.stride,Ge=ge.offset;if(fe.isInstancedInterleavedBuffer){for(let Fe=0;Fe<ne.locationSize;Fe++)p(ne.location+Fe,fe.meshPerAttribute);x.isInstancedMesh!==!0&&k._maxInstanceCount===void 0&&(k._maxInstanceCount=fe.meshPerAttribute*fe.count)}else for(let Fe=0;Fe<ne.locationSize;Fe++)m(ne.location+Fe);i.bindBuffer(i.ARRAY_BUFFER,ye);for(let Fe=0;Fe<ne.locationSize;Fe++)y(ne.location+Fe,xe/ne.locationSize,ie,de,ze*he,(Ge+xe/ne.locationSize*Fe)*he,Me)}else{if(ge.isInstancedBufferAttribute){for(let fe=0;fe<ne.locationSize;fe++)p(ne.location+fe,ge.meshPerAttribute);x.isInstancedMesh!==!0&&k._maxInstanceCount===void 0&&(k._maxInstanceCount=ge.meshPerAttribute*ge.count)}else for(let fe=0;fe<ne.locationSize;fe++)m(ne.location+fe);i.bindBuffer(i.ARRAY_BUFFER,ye);for(let fe=0;fe<ne.locationSize;fe++)y(ne.location+fe,xe/ne.locationSize,ie,de,xe*he,xe/ne.locationSize*fe*he,Me)}}else if(ee!==void 0){const de=ee[Y];if(de!==void 0)switch(de.length){case 2:i.vertexAttrib2fv(ne.location,de);break;case 3:i.vertexAttrib3fv(ne.location,de);break;case 4:i.vertexAttrib4fv(ne.location,de);break;default:i.vertexAttrib1fv(ne.location,de)}}}}S()}function O(){F();for(const x in n){const P=n[x];for(const K in P){const k=P[K];for(const Z in k)h(k[Z].object),delete k[Z];delete P[K]}delete n[x]}}function A(x){if(n[x.id]===void 0)return;const P=n[x.id];for(const K in P){const k=P[K];for(const Z in k)h(k[Z].object),delete k[Z];delete P[K]}delete n[x.id]}function C(x){for(const P in n){const K=n[P];if(K[x.id]===void 0)continue;const k=K[x.id];for(const Z in k)h(k[Z].object),delete k[Z];delete K[x.id]}}function F(){b(),a=!0,r!==s&&(r=s,c(r.object))}function b(){s.geometry=null,s.program=null,s.wireframe=!1}return{setup:o,reset:F,resetDefaultState:b,dispose:O,releaseStatesOfGeometry:A,releaseStatesOfProgram:C,initAttributes:_,enableAttribute:m,disableUnusedAttributes:S}}function Wv(i,e,t){let n;function s(c){n=c}function r(c,h){i.drawArrays(n,c,h),t.update(h,n,1)}function a(c,h,u){u!==0&&(i.drawArraysInstanced(n,c,h,u),t.update(h,n,u))}function o(c,h,u){if(u===0)return;e.get("WEBGL_multi_draw").multiDrawArraysWEBGL(n,c,0,h,0,u);let f=0;for(let g=0;g<u;g++)f+=h[g];t.update(f,n,1)}function l(c,h,u,d){if(u===0)return;const f=e.get("WEBGL_multi_draw");if(f===null)for(let g=0;g<c.length;g++)a(c[g],h[g],d[g]);else{f.multiDrawArraysInstancedWEBGL(n,c,0,h,0,d,0,u);let g=0;for(let _=0;_<u;_++)g+=h[_];for(let _=0;_<d.length;_++)t.update(g,n,d[_])}}this.setMode=s,this.render=r,this.renderInstances=a,this.renderMultiDraw=o,this.renderMultiDrawInstances=l}function Xv(i,e,t,n){let s;function r(){if(s!==void 0)return s;if(e.has("EXT_texture_filter_anisotropic")===!0){const A=e.get("EXT_texture_filter_anisotropic");s=i.getParameter(A.MAX_TEXTURE_MAX_ANISOTROPY_EXT)}else s=0;return s}function a(A){return!(A!==ci&&n.convert(A)!==i.getParameter(i.IMPLEMENTATION_COLOR_READ_FORMAT))}function o(A){const C=A===Na&&(e.has("EXT_color_buffer_half_float")||e.has("EXT_color_buffer_float"));return!(A!==Wi&&n.convert(A)!==i.getParameter(i.IMPLEMENTATION_COLOR_READ_TYPE)&&A!==Oi&&!C)}function l(A){if(A==="highp"){if(i.getShaderPrecisionFormat(i.VERTEX_SHADER,i.HIGH_FLOAT).precision>0&&i.getShaderPrecisionFormat(i.FRAGMENT_SHADER,i.HIGH_FLOAT).precision>0)return"highp";A="mediump"}return A==="mediump"&&i.getShaderPrecisionFormat(i.VERTEX_SHADER,i.MEDIUM_FLOAT).precision>0&&i.getShaderPrecisionFormat(i.FRAGMENT_SHADER,i.MEDIUM_FLOAT).precision>0?"mediump":"lowp"}let c=t.precision!==void 0?t.precision:"highp";const h=l(c);h!==c&&(console.warn("THREE.WebGLRenderer:",c,"not supported, using",h,"instead."),c=h);const u=t.logarithmicDepthBuffer===!0,d=i.getParameter(i.MAX_TEXTURE_IMAGE_UNITS),f=i.getParameter(i.MAX_VERTEX_TEXTURE_IMAGE_UNITS),g=i.getParameter(i.MAX_TEXTURE_SIZE),_=i.getParameter(i.MAX_CUBE_MAP_TEXTURE_SIZE),m=i.getParameter(i.MAX_VERTEX_ATTRIBS),p=i.getParameter(i.MAX_VERTEX_UNIFORM_VECTORS),S=i.getParameter(i.MAX_VARYING_VECTORS),y=i.getParameter(i.MAX_FRAGMENT_UNIFORM_VECTORS),w=f>0,O=i.getParameter(i.MAX_SAMPLES);return{isWebGL2:!0,getMaxAnisotropy:r,getMaxPrecision:l,textureFormatReadable:a,textureTypeReadable:o,precision:c,logarithmicDepthBuffer:u,maxTextures:d,maxVertexTextures:f,maxTextureSize:g,maxCubemapSize:_,maxAttributes:m,maxVertexUniforms:p,maxVaryings:S,maxFragmentUniforms:y,vertexTextures:w,maxSamples:O}}function qv(i){const e=this;let t=null,n=0,s=!1,r=!1;const a=new ss,o=new at,l={value:null,needsUpdate:!1};this.uniform=l,this.numPlanes=0,this.numIntersection=0,this.init=function(u,d){const f=u.length!==0||d||n!==0||s;return s=d,n=u.length,f},this.beginShadows=function(){r=!0,h(null)},this.endShadows=function(){r=!1},this.setGlobalState=function(u,d){t=h(u,d,0)},this.setState=function(u,d,f){const g=u.clippingPlanes,_=u.clipIntersection,m=u.clipShadows,p=i.get(u);if(!s||g===null||g.length===0||r&&!m)r?h(null):c();else{const S=r?0:n,y=S*4;let w=p.clippingState||null;l.value=w,w=h(g,d,y,f);for(let O=0;O!==y;++O)w[O]=t[O];p.clippingState=w,this.numIntersection=_?this.numPlanes:0,this.numPlanes+=S}};function c(){l.value!==t&&(l.value=t,l.needsUpdate=n>0),e.numPlanes=n,e.numIntersection=0}function h(u,d,f,g){const _=u!==null?u.length:0;let m=null;if(_!==0){if(m=l.value,g!==!0||m===null){const p=f+_*4,S=d.matrixWorldInverse;o.getNormalMatrix(S),(m===null||m.length<p)&&(m=new Float32Array(p));for(let y=0,w=f;y!==_;++y,w+=4)a.copy(u[y]).applyMatrix4(S,o),a.normal.toArray(m,w),m[w+3]=a.constant}l.value=m,l.needsUpdate=!0}return e.numPlanes=_,e.numIntersection=0,m}}function $v(i){let e=new WeakMap;function t(a,o){return o===Sc?a.mapping=Br:o===bc&&(a.mapping=zr),a}function n(a){if(a&&a.isTexture){const o=a.mapping;if(o===Sc||o===bc)if(e.has(a)){const l=e.get(a).texture;return t(l,a.mapping)}else{const l=a.image;if(l&&l.height>0){const c=new s_(l.height);return c.fromEquirectangularTexture(i,a),e.set(a,c),a.addEventListener("dispose",s),t(c.texture,a.mapping)}else return null}}return a}function s(a){const o=a.target;o.removeEventListener("dispose",s);const l=e.get(o);l!==void 0&&(e.delete(o),l.dispose())}function r(){e=new WeakMap}return{get:n,dispose:r}}class Nr extends Kf{constructor(e=-1,t=1,n=1,s=-1,r=.1,a=2e3){super(),this.isOrthographicCamera=!0,this.type="OrthographicCamera",this.zoom=1,this.view=null,this.left=e,this.right=t,this.top=n,this.bottom=s,this.near=r,this.far=a,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.left=e.left,this.right=e.right,this.top=e.top,this.bottom=e.bottom,this.near=e.near,this.far=e.far,this.zoom=e.zoom,this.view=e.view===null?null:Object.assign({},e.view),this}setViewOffset(e,t,n,s,r,a){this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=n,this.view.offsetY=s,this.view.width=r,this.view.height=a,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const e=(this.right-this.left)/(2*this.zoom),t=(this.top-this.bottom)/(2*this.zoom),n=(this.right+this.left)/2,s=(this.top+this.bottom)/2;let r=n-e,a=n+e,o=s+t,l=s-t;if(this.view!==null&&this.view.enabled){const c=(this.right-this.left)/this.view.fullWidth/this.zoom,h=(this.top-this.bottom)/this.view.fullHeight/this.zoom;r+=c*this.view.offsetX,a=r+c*this.view.width,o-=h*this.view.offsetY,l=o-h*this.view.height}this.projectionMatrix.makeOrthographic(r,a,o,l,this.near,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){const t=super.toJSON(e);return t.object.zoom=this.zoom,t.object.left=this.left,t.object.right=this.right,t.object.top=this.top,t.object.bottom=this.bottom,t.object.near=this.near,t.object.far=this.far,this.view!==null&&(t.object.view=Object.assign({},this.view)),t}}const Rr=4,Xu=[.125,.215,.35,.446,.526,.582],Ls=20,Jl=new Nr,qu=new nt;let Ql=null,ec=0,tc=0,nc=!1;const As=(1+Math.sqrt(5))/2,vr=1/As,$u=[new H(-As,vr,0),new H(As,vr,0),new H(-vr,0,As),new H(vr,0,As),new H(0,As,-vr),new H(0,As,vr),new H(-1,1,-1),new H(1,1,-1),new H(-1,1,1),new H(1,1,1)];class Yu{constructor(e){this._renderer=e,this._pingPongRenderTarget=null,this._lodMax=0,this._cubeSize=0,this._lodPlanes=[],this._sizeLods=[],this._sigmas=[],this._blurMaterial=null,this._cubemapMaterial=null,this._equirectMaterial=null,this._compileMaterial(this._blurMaterial)}fromScene(e,t=0,n=.1,s=100){Ql=this._renderer.getRenderTarget(),ec=this._renderer.getActiveCubeFace(),tc=this._renderer.getActiveMipmapLevel(),nc=this._renderer.xr.enabled,this._renderer.xr.enabled=!1,this._setSize(256);const r=this._allocateTargets();return r.depthBuffer=!0,this._sceneToCubeUV(e,n,s,r),t>0&&this._blur(r,0,0,t),this._applyPMREM(r),this._cleanup(r),r}fromEquirectangular(e,t=null){return this._fromTexture(e,t)}fromCubemap(e,t=null){return this._fromTexture(e,t)}compileCubemapShader(){this._cubemapMaterial===null&&(this._cubemapMaterial=Zu(),this._compileMaterial(this._cubemapMaterial))}compileEquirectangularShader(){this._equirectMaterial===null&&(this._equirectMaterial=Ku(),this._compileMaterial(this._equirectMaterial))}dispose(){this._dispose(),this._cubemapMaterial!==null&&this._cubemapMaterial.dispose(),this._equirectMaterial!==null&&this._equirectMaterial.dispose()}_setSize(e){this._lodMax=Math.floor(Math.log2(e)),this._cubeSize=Math.pow(2,this._lodMax)}_dispose(){this._blurMaterial!==null&&this._blurMaterial.dispose(),this._pingPongRenderTarget!==null&&this._pingPongRenderTarget.dispose();for(let e=0;e<this._lodPlanes.length;e++)this._lodPlanes[e].dispose()}_cleanup(e){this._renderer.setRenderTarget(Ql,ec,tc),this._renderer.xr.enabled=nc,e.scissorTest=!1,mo(e,0,0,e.width,e.height)}_fromTexture(e,t){e.mapping===Br||e.mapping===zr?this._setSize(e.image.length===0?16:e.image[0].width||e.image[0].image.width):this._setSize(e.image.width/4),Ql=this._renderer.getRenderTarget(),ec=this._renderer.getActiveCubeFace(),tc=this._renderer.getActiveMipmapLevel(),nc=this._renderer.xr.enabled,this._renderer.xr.enabled=!1;const n=t||this._allocateTargets();return this._textureToCubeUV(e,n),this._applyPMREM(n),this._cleanup(n),n}_allocateTargets(){const e=3*Math.max(this._cubeSize,112),t=4*this._cubeSize,n={magFilter:ai,minFilter:ai,generateMipmaps:!1,type:Na,format:ci,colorSpace:ps,depthBuffer:!1},s=ju(e,t,n);if(this._pingPongRenderTarget===null||this._pingPongRenderTarget.width!==e||this._pingPongRenderTarget.height!==t){this._pingPongRenderTarget!==null&&this._dispose(),this._pingPongRenderTarget=ju(e,t,n);const{_lodMax:r}=this;({sizeLods:this._sizeLods,lodPlanes:this._lodPlanes,sigmas:this._sigmas}=Yv(r)),this._blurMaterial=jv(r,e,t)}return s}_compileMaterial(e){const t=new _n(this._lodPlanes[0],e);this._renderer.compile(t,Jl)}_sceneToCubeUV(e,t,n,s){const o=new bn(90,1,t,n),l=[1,-1,1,1,1,1],c=[1,1,1,-1,-1,-1],h=this._renderer,u=h.autoClear,d=h.toneMapping;h.getClearColor(qu),h.toneMapping=cs,h.autoClear=!1;const f=new Ur({name:"PMREM.Background",side:In,depthWrite:!1,depthTest:!1}),g=new _n(new zi,f);let _=!1;const m=e.background;m?m.isColor&&(f.color.copy(m),e.background=null,_=!0):(f.color.copy(qu),_=!0);for(let p=0;p<6;p++){const S=p%3;S===0?(o.up.set(0,l[p],0),o.lookAt(c[p],0,0)):S===1?(o.up.set(0,0,l[p]),o.lookAt(0,c[p],0)):(o.up.set(0,l[p],0),o.lookAt(0,0,c[p]));const y=this._cubeSize;mo(s,S*y,p>2?y:0,y,y),h.setRenderTarget(s),_&&h.render(g,o),h.render(e,o)}g.geometry.dispose(),g.material.dispose(),h.toneMapping=d,h.autoClear=u,e.background=m}_textureToCubeUV(e,t){const n=this._renderer,s=e.mapping===Br||e.mapping===zr;s?(this._cubemapMaterial===null&&(this._cubemapMaterial=Zu()),this._cubemapMaterial.uniforms.flipEnvMap.value=e.isRenderTargetTexture===!1?-1:1):this._equirectMaterial===null&&(this._equirectMaterial=Ku());const r=s?this._cubemapMaterial:this._equirectMaterial,a=new _n(this._lodPlanes[0],r),o=r.uniforms;o.envMap.value=e;const l=this._cubeSize;mo(t,0,0,3*l,2*l),n.setRenderTarget(t),n.render(a,Jl)}_applyPMREM(e){const t=this._renderer,n=t.autoClear;t.autoClear=!1;const s=this._lodPlanes.length;for(let r=1;r<s;r++){const a=Math.sqrt(this._sigmas[r]*this._sigmas[r]-this._sigmas[r-1]*this._sigmas[r-1]),o=$u[(s-r-1)%$u.length];this._blur(e,r-1,r,a,o)}t.autoClear=n}_blur(e,t,n,s,r){const a=this._pingPongRenderTarget;this._halfBlur(e,a,t,n,s,"latitudinal",r),this._halfBlur(a,e,n,n,s,"longitudinal",r)}_halfBlur(e,t,n,s,r,a,o){const l=this._renderer,c=this._blurMaterial;a!=="latitudinal"&&a!=="longitudinal"&&console.error("blur direction must be either latitudinal or longitudinal!");const h=3,u=new _n(this._lodPlanes[s],c),d=c.uniforms,f=this._sizeLods[n]-1,g=isFinite(r)?Math.PI/(2*f):2*Math.PI/(2*Ls-1),_=r/g,m=isFinite(r)?1+Math.floor(h*_):Ls;m>Ls&&console.warn(`sigmaRadians, ${r}, is too large and will clip, as it requested ${m} samples when the maximum is set to ${Ls}`);const p=[];let S=0;for(let C=0;C<Ls;++C){const F=C/_,b=Math.exp(-F*F/2);p.push(b),C===0?S+=b:C<m&&(S+=2*b)}for(let C=0;C<p.length;C++)p[C]=p[C]/S;d.envMap.value=e.texture,d.samples.value=m,d.weights.value=p,d.latitudinal.value=a==="latitudinal",o&&(d.poleAxis.value=o);const{_lodMax:y}=this;d.dTheta.value=g,d.mipInt.value=y-n;const w=this._sizeLods[s],O=3*w*(s>y-Rr?s-y+Rr:0),A=4*(this._cubeSize-w);mo(t,O,A,3*w,2*w),l.setRenderTarget(t),l.render(u,Jl)}}function Yv(i){const e=[],t=[],n=[];let s=i;const r=i-Rr+1+Xu.length;for(let a=0;a<r;a++){const o=Math.pow(2,s);t.push(o);let l=1/o;a>i-Rr?l=Xu[a-i+Rr-1]:a===0&&(l=0),n.push(l);const c=1/(o-2),h=-c,u=1+c,d=[h,h,u,h,u,u,h,h,u,u,h,u],f=6,g=6,_=3,m=2,p=1,S=new Float32Array(_*g*f),y=new Float32Array(m*g*f),w=new Float32Array(p*g*f);for(let A=0;A<f;A++){const C=A%3*2/3-1,F=A>2?0:-1,b=[C,F,0,C+2/3,F,0,C+2/3,F+1,0,C,F,0,C+2/3,F+1,0,C,F+1,0];S.set(b,_*g*A),y.set(d,m*g*A);const x=[A,A,A,A,A,A];w.set(x,p*g*A)}const O=new Xt;O.setAttribute("position",new hi(S,_)),O.setAttribute("uv",new hi(y,m)),O.setAttribute("faceIndex",new hi(w,p)),e.push(O),s>Rr&&s--}return{lodPlanes:e,sizeLods:t,sigmas:n}}function ju(i,e,t){const n=new zs(i,e,t);return n.texture.mapping=rl,n.texture.name="PMREM.cubeUv",n.scissorTest=!0,n}function mo(i,e,t,n,s){i.viewport.set(e,t,n,s),i.scissor.set(e,t,n,s)}function jv(i,e,t){const n=new Float32Array(Ls),s=new H(0,1,0);return new us({name:"SphericalGaussianBlur",defines:{n:Ls,CUBEUV_TEXEL_WIDTH:1/e,CUBEUV_TEXEL_HEIGHT:1/t,CUBEUV_MAX_MIP:`${i}.0`},uniforms:{envMap:{value:null},samples:{value:1},weights:{value:n},latitudinal:{value:!1},dTheta:{value:0},mipInt:{value:0},poleAxis:{value:s}},vertexShader:wh(),fragmentShader:`

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
		`,blending:ls,depthTest:!1,depthWrite:!1})}function Ku(){return new us({name:"EquirectangularToCubeUV",uniforms:{envMap:{value:null}},vertexShader:wh(),fragmentShader:`

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
		`,blending:ls,depthTest:!1,depthWrite:!1})}function Zu(){return new us({name:"CubemapToCubeUV",uniforms:{envMap:{value:null},flipEnvMap:{value:-1}},vertexShader:wh(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			uniform float flipEnvMap;

			varying vec3 vOutputDirection;

			uniform samplerCube envMap;

			void main() {

				gl_FragColor = textureCube( envMap, vec3( flipEnvMap * vOutputDirection.x, vOutputDirection.yz ) );

			}
		`,blending:ls,depthTest:!1,depthWrite:!1})}function wh(){return`

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
	`}function Kv(i){let e=new WeakMap,t=null;function n(o){if(o&&o.isTexture){const l=o.mapping,c=l===Sc||l===bc,h=l===Br||l===zr;if(c||h){let u=e.get(o);const d=u!==void 0?u.texture.pmremVersion:0;if(o.isRenderTargetTexture&&o.pmremVersion!==d)return t===null&&(t=new Yu(i)),u=c?t.fromEquirectangular(o,u):t.fromCubemap(o,u),u.texture.pmremVersion=o.pmremVersion,e.set(o,u),u.texture;if(u!==void 0)return u.texture;{const f=o.image;return c&&f&&f.height>0||h&&f&&s(f)?(t===null&&(t=new Yu(i)),u=c?t.fromEquirectangular(o):t.fromCubemap(o),u.texture.pmremVersion=o.pmremVersion,e.set(o,u),o.addEventListener("dispose",r),u.texture):null}}}return o}function s(o){let l=0;const c=6;for(let h=0;h<c;h++)o[h]!==void 0&&l++;return l===c}function r(o){const l=o.target;l.removeEventListener("dispose",r);const c=e.get(l);c!==void 0&&(e.delete(l),c.dispose())}function a(){e=new WeakMap,t!==null&&(t.dispose(),t=null)}return{get:n,dispose:a}}function Zv(i){const e={};function t(n){if(e[n]!==void 0)return e[n];let s;switch(n){case"WEBGL_depth_texture":s=i.getExtension("WEBGL_depth_texture")||i.getExtension("MOZ_WEBGL_depth_texture")||i.getExtension("WEBKIT_WEBGL_depth_texture");break;case"EXT_texture_filter_anisotropic":s=i.getExtension("EXT_texture_filter_anisotropic")||i.getExtension("MOZ_EXT_texture_filter_anisotropic")||i.getExtension("WEBKIT_EXT_texture_filter_anisotropic");break;case"WEBGL_compressed_texture_s3tc":s=i.getExtension("WEBGL_compressed_texture_s3tc")||i.getExtension("MOZ_WEBGL_compressed_texture_s3tc")||i.getExtension("WEBKIT_WEBGL_compressed_texture_s3tc");break;case"WEBGL_compressed_texture_pvrtc":s=i.getExtension("WEBGL_compressed_texture_pvrtc")||i.getExtension("WEBKIT_WEBGL_compressed_texture_pvrtc");break;default:s=i.getExtension(n)}return e[n]=s,s}return{has:function(n){return t(n)!==null},init:function(){t("EXT_color_buffer_float"),t("WEBGL_clip_cull_distance"),t("OES_texture_float_linear"),t("EXT_color_buffer_half_float"),t("WEBGL_multisampled_render_to_texture"),t("WEBGL_render_shared_exponent")},get:function(n){const s=t(n);return s===null&&Dr("THREE.WebGLRenderer: "+n+" extension not supported."),s}}}function Jv(i,e,t,n){const s={},r=new WeakMap;function a(u){const d=u.target;d.index!==null&&e.remove(d.index);for(const g in d.attributes)e.remove(d.attributes[g]);for(const g in d.morphAttributes){const _=d.morphAttributes[g];for(let m=0,p=_.length;m<p;m++)e.remove(_[m])}d.removeEventListener("dispose",a),delete s[d.id];const f=r.get(d);f&&(e.remove(f),r.delete(d)),n.releaseStatesOfGeometry(d),d.isInstancedBufferGeometry===!0&&delete d._maxInstanceCount,t.memory.geometries--}function o(u,d){return s[d.id]===!0||(d.addEventListener("dispose",a),s[d.id]=!0,t.memory.geometries++),d}function l(u){const d=u.attributes;for(const g in d)e.update(d[g],i.ARRAY_BUFFER);const f=u.morphAttributes;for(const g in f){const _=f[g];for(let m=0,p=_.length;m<p;m++)e.update(_[m],i.ARRAY_BUFFER)}}function c(u){const d=[],f=u.index,g=u.attributes.position;let _=0;if(f!==null){const S=f.array;_=f.version;for(let y=0,w=S.length;y<w;y+=3){const O=S[y+0],A=S[y+1],C=S[y+2];d.push(O,A,A,C,C,O)}}else if(g!==void 0){const S=g.array;_=g.version;for(let y=0,w=S.length/3-1;y<w;y+=3){const O=y+0,A=y+1,C=y+2;d.push(O,A,A,C,C,O)}}else return;const m=new(Gf(d)?Yf:$f)(d,1);m.version=_;const p=r.get(u);p&&e.remove(p),r.set(u,m)}function h(u){const d=r.get(u);if(d){const f=u.index;f!==null&&d.version<f.version&&c(u)}else c(u);return r.get(u)}return{get:o,update:l,getWireframeAttribute:h}}function Qv(i,e,t){let n;function s(d){n=d}let r,a;function o(d){r=d.type,a=d.bytesPerElement}function l(d,f){i.drawElements(n,f,r,d*a),t.update(f,n,1)}function c(d,f,g){g!==0&&(i.drawElementsInstanced(n,f,r,d*a,g),t.update(f,n,g))}function h(d,f,g){if(g===0)return;e.get("WEBGL_multi_draw").multiDrawElementsWEBGL(n,f,0,r,d,0,g);let m=0;for(let p=0;p<g;p++)m+=f[p];t.update(m,n,1)}function u(d,f,g,_){if(g===0)return;const m=e.get("WEBGL_multi_draw");if(m===null)for(let p=0;p<d.length;p++)c(d[p]/a,f[p],_[p]);else{m.multiDrawElementsInstancedWEBGL(n,f,0,r,d,0,_,0,g);let p=0;for(let S=0;S<g;S++)p+=f[S];for(let S=0;S<_.length;S++)t.update(p,n,_[S])}}this.setMode=s,this.setIndex=o,this.render=l,this.renderInstances=c,this.renderMultiDraw=h,this.renderMultiDrawInstances=u}function ex(i){const e={geometries:0,textures:0},t={frame:0,calls:0,triangles:0,points:0,lines:0};function n(r,a,o){switch(t.calls++,a){case i.TRIANGLES:t.triangles+=o*(r/3);break;case i.LINES:t.lines+=o*(r/2);break;case i.LINE_STRIP:t.lines+=o*(r-1);break;case i.LINE_LOOP:t.lines+=o*r;break;case i.POINTS:t.points+=o*r;break;default:console.error("THREE.WebGLInfo: Unknown draw mode:",a);break}}function s(){t.calls=0,t.triangles=0,t.points=0,t.lines=0}return{memory:e,render:t,programs:null,autoReset:!0,reset:s,update:n}}function tx(i,e,t){const n=new WeakMap,s=new nn;function r(a,o,l){const c=a.morphTargetInfluences,h=o.morphAttributes.position||o.morphAttributes.normal||o.morphAttributes.color,u=h!==void 0?h.length:0;let d=n.get(o);if(d===void 0||d.count!==u){let x=function(){F.dispose(),n.delete(o),o.removeEventListener("dispose",x)};var f=x;d!==void 0&&d.texture.dispose();const g=o.morphAttributes.position!==void 0,_=o.morphAttributes.normal!==void 0,m=o.morphAttributes.color!==void 0,p=o.morphAttributes.position||[],S=o.morphAttributes.normal||[],y=o.morphAttributes.color||[];let w=0;g===!0&&(w=1),_===!0&&(w=2),m===!0&&(w=3);let O=o.attributes.position.count*w,A=1;O>e.maxTextureSize&&(A=Math.ceil(O/e.maxTextureSize),O=e.maxTextureSize);const C=new Float32Array(O*A*4*u),F=new Xf(C,O,A,u);F.type=Oi,F.needsUpdate=!0;const b=w*4;for(let P=0;P<u;P++){const K=p[P],k=S[P],Z=y[P],q=O*A*4*P;for(let ee=0;ee<K.count;ee++){const Y=ee*b;g===!0&&(s.fromBufferAttribute(K,ee),C[q+Y+0]=s.x,C[q+Y+1]=s.y,C[q+Y+2]=s.z,C[q+Y+3]=0),_===!0&&(s.fromBufferAttribute(k,ee),C[q+Y+4]=s.x,C[q+Y+5]=s.y,C[q+Y+6]=s.z,C[q+Y+7]=0),m===!0&&(s.fromBufferAttribute(Z,ee),C[q+Y+8]=s.x,C[q+Y+9]=s.y,C[q+Y+10]=s.z,C[q+Y+11]=Z.itemSize===4?s.w:1)}}d={count:u,texture:F,size:new qe(O,A)},n.set(o,d),o.addEventListener("dispose",x)}if(a.isInstancedMesh===!0&&a.morphTexture!==null)l.getUniforms().setValue(i,"morphTexture",a.morphTexture,t);else{let g=0;for(let m=0;m<c.length;m++)g+=c[m];const _=o.morphTargetsRelative?1:1-g;l.getUniforms().setValue(i,"morphTargetBaseInfluence",_),l.getUniforms().setValue(i,"morphTargetInfluences",c)}l.getUniforms().setValue(i,"morphTargetsTexture",d.texture,t),l.getUniforms().setValue(i,"morphTargetsTextureSize",d.size)}return{update:r}}function nx(i,e,t,n){let s=new WeakMap;function r(l){const c=n.render.frame,h=l.geometry,u=e.get(l,h);if(s.get(u)!==c&&(e.update(u),s.set(u,c)),l.isInstancedMesh&&(l.hasEventListener("dispose",o)===!1&&l.addEventListener("dispose",o),s.get(l)!==c&&(t.update(l.instanceMatrix,i.ARRAY_BUFFER),l.instanceColor!==null&&t.update(l.instanceColor,i.ARRAY_BUFFER),s.set(l,c))),l.isSkinnedMesh){const d=l.skeleton;s.get(d)!==c&&(d.update(),s.set(d,c))}return u}function a(){s=new WeakMap}function o(l){const c=l.target;c.removeEventListener("dispose",o),t.remove(c.instanceMatrix),c.instanceColor!==null&&t.remove(c.instanceColor)}return{update:r,dispose:a}}class Qf extends Ln{constructor(e,t,n,s,r,a,o,l,c,h=Pr){if(h!==Pr&&h!==Hr)throw new Error("DepthTexture format must be either THREE.DepthFormat or THREE.DepthStencilFormat");n===void 0&&h===Pr&&(n=Bs),n===void 0&&h===Hr&&(n=kr),super(null,s,r,a,o,l,h,n,c),this.isDepthTexture=!0,this.image={width:e,height:t},this.magFilter=o!==void 0?o:Kn,this.minFilter=l!==void 0?l:Kn,this.flipY=!1,this.generateMipmaps=!1,this.compareFunction=null}copy(e){return super.copy(e),this.compareFunction=e.compareFunction,this}toJSON(e){const t=super.toJSON(e);return this.compareFunction!==null&&(t.compareFunction=this.compareFunction),t}}const ep=new Ln,Ju=new Qf(1,1),tp=new Xf,np=new Vg,ip=new Zf,Qu=[],ed=[],td=new Float32Array(16),nd=new Float32Array(9),id=new Float32Array(4);function Zr(i,e,t){const n=i[0];if(n<=0||n>0)return i;const s=e*t;let r=Qu[s];if(r===void 0&&(r=new Float32Array(s),Qu[s]=r),e!==0){n.toArray(r,0);for(let a=1,o=0;a!==e;++a)o+=t,i[a].toArray(r,o)}return r}function sn(i,e){if(i.length!==e.length)return!1;for(let t=0,n=i.length;t<n;t++)if(i[t]!==e[t])return!1;return!0}function rn(i,e){for(let t=0,n=e.length;t<n;t++)i[t]=e[t]}function ol(i,e){let t=ed[e];t===void 0&&(t=new Int32Array(e),ed[e]=t);for(let n=0;n!==e;++n)t[n]=i.allocateTextureUnit();return t}function ix(i,e){const t=this.cache;t[0]!==e&&(i.uniform1f(this.addr,e),t[0]=e)}function sx(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(i.uniform2f(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(sn(t,e))return;i.uniform2fv(this.addr,e),rn(t,e)}}function rx(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(i.uniform3f(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else if(e.r!==void 0)(t[0]!==e.r||t[1]!==e.g||t[2]!==e.b)&&(i.uniform3f(this.addr,e.r,e.g,e.b),t[0]=e.r,t[1]=e.g,t[2]=e.b);else{if(sn(t,e))return;i.uniform3fv(this.addr,e),rn(t,e)}}function ax(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(i.uniform4f(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(sn(t,e))return;i.uniform4fv(this.addr,e),rn(t,e)}}function ox(i,e){const t=this.cache,n=e.elements;if(n===void 0){if(sn(t,e))return;i.uniformMatrix2fv(this.addr,!1,e),rn(t,e)}else{if(sn(t,n))return;id.set(n),i.uniformMatrix2fv(this.addr,!1,id),rn(t,n)}}function lx(i,e){const t=this.cache,n=e.elements;if(n===void 0){if(sn(t,e))return;i.uniformMatrix3fv(this.addr,!1,e),rn(t,e)}else{if(sn(t,n))return;nd.set(n),i.uniformMatrix3fv(this.addr,!1,nd),rn(t,n)}}function cx(i,e){const t=this.cache,n=e.elements;if(n===void 0){if(sn(t,e))return;i.uniformMatrix4fv(this.addr,!1,e),rn(t,e)}else{if(sn(t,n))return;td.set(n),i.uniformMatrix4fv(this.addr,!1,td),rn(t,n)}}function hx(i,e){const t=this.cache;t[0]!==e&&(i.uniform1i(this.addr,e),t[0]=e)}function ux(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(i.uniform2i(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(sn(t,e))return;i.uniform2iv(this.addr,e),rn(t,e)}}function dx(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(i.uniform3i(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(sn(t,e))return;i.uniform3iv(this.addr,e),rn(t,e)}}function fx(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(i.uniform4i(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(sn(t,e))return;i.uniform4iv(this.addr,e),rn(t,e)}}function px(i,e){const t=this.cache;t[0]!==e&&(i.uniform1ui(this.addr,e),t[0]=e)}function mx(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(i.uniform2ui(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(sn(t,e))return;i.uniform2uiv(this.addr,e),rn(t,e)}}function gx(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(i.uniform3ui(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(sn(t,e))return;i.uniform3uiv(this.addr,e),rn(t,e)}}function _x(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(i.uniform4ui(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(sn(t,e))return;i.uniform4uiv(this.addr,e),rn(t,e)}}function vx(i,e,t){const n=this.cache,s=t.allocateTextureUnit();n[0]!==s&&(i.uniform1i(this.addr,s),n[0]=s);let r;this.type===i.SAMPLER_2D_SHADOW?(Ju.compareFunction=Vf,r=Ju):r=ep,t.setTexture2D(e||r,s)}function xx(i,e,t){const n=this.cache,s=t.allocateTextureUnit();n[0]!==s&&(i.uniform1i(this.addr,s),n[0]=s),t.setTexture3D(e||np,s)}function yx(i,e,t){const n=this.cache,s=t.allocateTextureUnit();n[0]!==s&&(i.uniform1i(this.addr,s),n[0]=s),t.setTextureCube(e||ip,s)}function Mx(i,e,t){const n=this.cache,s=t.allocateTextureUnit();n[0]!==s&&(i.uniform1i(this.addr,s),n[0]=s),t.setTexture2DArray(e||tp,s)}function Sx(i){switch(i){case 5126:return ix;case 35664:return sx;case 35665:return rx;case 35666:return ax;case 35674:return ox;case 35675:return lx;case 35676:return cx;case 5124:case 35670:return hx;case 35667:case 35671:return ux;case 35668:case 35672:return dx;case 35669:case 35673:return fx;case 5125:return px;case 36294:return mx;case 36295:return gx;case 36296:return _x;case 35678:case 36198:case 36298:case 36306:case 35682:return vx;case 35679:case 36299:case 36307:return xx;case 35680:case 36300:case 36308:case 36293:return yx;case 36289:case 36303:case 36311:case 36292:return Mx}}function bx(i,e){i.uniform1fv(this.addr,e)}function Ex(i,e){const t=Zr(e,this.size,2);i.uniform2fv(this.addr,t)}function wx(i,e){const t=Zr(e,this.size,3);i.uniform3fv(this.addr,t)}function Tx(i,e){const t=Zr(e,this.size,4);i.uniform4fv(this.addr,t)}function Ax(i,e){const t=Zr(e,this.size,4);i.uniformMatrix2fv(this.addr,!1,t)}function Rx(i,e){const t=Zr(e,this.size,9);i.uniformMatrix3fv(this.addr,!1,t)}function Cx(i,e){const t=Zr(e,this.size,16);i.uniformMatrix4fv(this.addr,!1,t)}function Px(i,e){i.uniform1iv(this.addr,e)}function Lx(i,e){i.uniform2iv(this.addr,e)}function Dx(i,e){i.uniform3iv(this.addr,e)}function Ix(i,e){i.uniform4iv(this.addr,e)}function Ux(i,e){i.uniform1uiv(this.addr,e)}function Nx(i,e){i.uniform2uiv(this.addr,e)}function Fx(i,e){i.uniform3uiv(this.addr,e)}function Ox(i,e){i.uniform4uiv(this.addr,e)}function Bx(i,e,t){const n=this.cache,s=e.length,r=ol(t,s);sn(n,r)||(i.uniform1iv(this.addr,r),rn(n,r));for(let a=0;a!==s;++a)t.setTexture2D(e[a]||ep,r[a])}function zx(i,e,t){const n=this.cache,s=e.length,r=ol(t,s);sn(n,r)||(i.uniform1iv(this.addr,r),rn(n,r));for(let a=0;a!==s;++a)t.setTexture3D(e[a]||np,r[a])}function kx(i,e,t){const n=this.cache,s=e.length,r=ol(t,s);sn(n,r)||(i.uniform1iv(this.addr,r),rn(n,r));for(let a=0;a!==s;++a)t.setTextureCube(e[a]||ip,r[a])}function Hx(i,e,t){const n=this.cache,s=e.length,r=ol(t,s);sn(n,r)||(i.uniform1iv(this.addr,r),rn(n,r));for(let a=0;a!==s;++a)t.setTexture2DArray(e[a]||tp,r[a])}function Vx(i){switch(i){case 5126:return bx;case 35664:return Ex;case 35665:return wx;case 35666:return Tx;case 35674:return Ax;case 35675:return Rx;case 35676:return Cx;case 5124:case 35670:return Px;case 35667:case 35671:return Lx;case 35668:case 35672:return Dx;case 35669:case 35673:return Ix;case 5125:return Ux;case 36294:return Nx;case 36295:return Fx;case 36296:return Ox;case 35678:case 36198:case 36298:case 36306:case 35682:return Bx;case 35679:case 36299:case 36307:return zx;case 35680:case 36300:case 36308:case 36293:return kx;case 36289:case 36303:case 36311:case 36292:return Hx}}class Gx{constructor(e,t,n){this.id=e,this.addr=n,this.cache=[],this.type=t.type,this.setValue=Sx(t.type)}}class Wx{constructor(e,t,n){this.id=e,this.addr=n,this.cache=[],this.type=t.type,this.size=t.size,this.setValue=Vx(t.type)}}class Xx{constructor(e){this.id=e,this.seq=[],this.map={}}setValue(e,t,n){const s=this.seq;for(let r=0,a=s.length;r!==a;++r){const o=s[r];o.setValue(e,t[o.id],n)}}}const ic=/(\w+)(\])?(\[|\.)?/g;function sd(i,e){i.seq.push(e),i.map[e.id]=e}function qx(i,e,t){const n=i.name,s=n.length;for(ic.lastIndex=0;;){const r=ic.exec(n),a=ic.lastIndex;let o=r[1];const l=r[2]==="]",c=r[3];if(l&&(o=o|0),c===void 0||c==="["&&a+2===s){sd(t,c===void 0?new Gx(o,i,e):new Wx(o,i,e));break}else{let u=t.map[o];u===void 0&&(u=new Xx(o),sd(t,u)),t=u}}}class Oo{constructor(e,t){this.seq=[],this.map={};const n=e.getProgramParameter(t,e.ACTIVE_UNIFORMS);for(let s=0;s<n;++s){const r=e.getActiveUniform(t,s),a=e.getUniformLocation(t,r.name);qx(r,a,this)}}setValue(e,t,n,s){const r=this.map[t];r!==void 0&&r.setValue(e,n,s)}setOptional(e,t,n){const s=t[n];s!==void 0&&this.setValue(e,n,s)}static upload(e,t,n,s){for(let r=0,a=t.length;r!==a;++r){const o=t[r],l=n[o.id];l.needsUpdate!==!1&&o.setValue(e,l.value,s)}}static seqWithValue(e,t){const n=[];for(let s=0,r=e.length;s!==r;++s){const a=e[s];a.id in t&&n.push(a)}return n}}function rd(i,e,t){const n=i.createShader(e);return i.shaderSource(n,t),i.compileShader(n),n}const $x=37297;let Yx=0;function jx(i,e){const t=i.split(`
`),n=[],s=Math.max(e-6,0),r=Math.min(e+6,t.length);for(let a=s;a<r;a++){const o=a+1;n.push(`${o===e?">":" "} ${o}: ${t[a]}`)}return n.join(`
`)}function Kx(i){const e=bt.getPrimaries(bt.workingColorSpace),t=bt.getPrimaries(i);let n;switch(e===t?n="":e===Wo&&t===Go?n="LinearDisplayP3ToLinearSRGB":e===Go&&t===Wo&&(n="LinearSRGBToLinearDisplayP3"),i){case ps:case al:return[n,"LinearTransferOETF"];case xi:case Mh:return[n,"sRGBTransferOETF"];default:return console.warn("THREE.WebGLProgram: Unsupported color space:",i),[n,"LinearTransferOETF"]}}function ad(i,e,t){const n=i.getShaderParameter(e,i.COMPILE_STATUS),s=i.getShaderInfoLog(e).trim();if(n&&s==="")return"";const r=/ERROR: 0:(\d+)/.exec(s);if(r){const a=parseInt(r[1]);return t.toUpperCase()+`

`+s+`

`+jx(i.getShaderSource(e),a)}else return s}function Zx(i,e){const t=Kx(e);return`vec4 ${i}( vec4 value ) { return ${t[0]}( ${t[1]}( value ) ); }`}function Jx(i,e){let t;switch(e){case ng:t="Linear";break;case ig:t="Reinhard";break;case sg:t="Cineon";break;case Cf:t="ACESFilmic";break;case ag:t="AgX";break;case og:t="Neutral";break;case rg:t="Custom";break;default:console.warn("THREE.WebGLProgram: Unsupported toneMapping:",e),t="Linear"}return"vec3 "+i+"( vec3 color ) { return "+t+"ToneMapping( color ); }"}const go=new H;function Qx(){bt.getLuminanceCoefficients(go);const i=go.x.toFixed(4),e=go.y.toFixed(4),t=go.z.toFixed(4);return["float luminance( const in vec3 rgb ) {",`	const vec3 weights = vec3( ${i}, ${e}, ${t} );`,"	return dot( weights, rgb );","}"].join(`
`)}function ey(i){return[i.extensionClipCullDistance?"#extension GL_ANGLE_clip_cull_distance : require":"",i.extensionMultiDraw?"#extension GL_ANGLE_multi_draw : require":""].filter(Sa).join(`
`)}function ty(i){const e=[];for(const t in i){const n=i[t];n!==!1&&e.push("#define "+t+" "+n)}return e.join(`
`)}function ny(i,e){const t={},n=i.getProgramParameter(e,i.ACTIVE_ATTRIBUTES);for(let s=0;s<n;s++){const r=i.getActiveAttrib(e,s),a=r.name;let o=1;r.type===i.FLOAT_MAT2&&(o=2),r.type===i.FLOAT_MAT3&&(o=3),r.type===i.FLOAT_MAT4&&(o=4),t[a]={type:r.type,location:i.getAttribLocation(e,a),locationSize:o}}return t}function Sa(i){return i!==""}function od(i,e){const t=e.numSpotLightShadows+e.numSpotLightMaps-e.numSpotLightShadowsWithMaps;return i.replace(/NUM_DIR_LIGHTS/g,e.numDirLights).replace(/NUM_SPOT_LIGHTS/g,e.numSpotLights).replace(/NUM_SPOT_LIGHT_MAPS/g,e.numSpotLightMaps).replace(/NUM_SPOT_LIGHT_COORDS/g,t).replace(/NUM_RECT_AREA_LIGHTS/g,e.numRectAreaLights).replace(/NUM_POINT_LIGHTS/g,e.numPointLights).replace(/NUM_HEMI_LIGHTS/g,e.numHemiLights).replace(/NUM_DIR_LIGHT_SHADOWS/g,e.numDirLightShadows).replace(/NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS/g,e.numSpotLightShadowsWithMaps).replace(/NUM_SPOT_LIGHT_SHADOWS/g,e.numSpotLightShadows).replace(/NUM_POINT_LIGHT_SHADOWS/g,e.numPointLightShadows)}function ld(i,e){return i.replace(/NUM_CLIPPING_PLANES/g,e.numClippingPlanes).replace(/UNION_CLIPPING_PLANES/g,e.numClippingPlanes-e.numClipIntersection)}const iy=/^[ \t]*#include +<([\w\d./]+)>/gm;function eh(i){return i.replace(iy,ry)}const sy=new Map;function ry(i,e){let t=rt[e];if(t===void 0){const n=sy.get(e);if(n!==void 0)t=rt[n],console.warn('THREE.WebGLRenderer: Shader chunk "%s" has been deprecated. Use "%s" instead.',e,n);else throw new Error("Can not resolve #include <"+e+">")}return eh(t)}const ay=/#pragma unroll_loop_start\s+for\s*\(\s*int\s+i\s*=\s*(\d+)\s*;\s*i\s*<\s*(\d+)\s*;\s*i\s*\+\+\s*\)\s*{([\s\S]+?)}\s+#pragma unroll_loop_end/g;function cd(i){return i.replace(ay,oy)}function oy(i,e,t,n){let s="";for(let r=parseInt(e);r<parseInt(t);r++)s+=n.replace(/\[\s*i\s*\]/g,"[ "+r+" ]").replace(/UNROLLED_LOOP_INDEX/g,r);return s}function hd(i){let e=`precision ${i.precision} float;
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
#define LOW_PRECISION`),e}function ly(i){let e="SHADOWMAP_TYPE_BASIC";return i.shadowMapType===Tf?e="SHADOWMAP_TYPE_PCF":i.shadowMapType===Af?e="SHADOWMAP_TYPE_PCF_SOFT":i.shadowMapType===Ni&&(e="SHADOWMAP_TYPE_VSM"),e}function cy(i){let e="ENVMAP_TYPE_CUBE";if(i.envMap)switch(i.envMapMode){case Br:case zr:e="ENVMAP_TYPE_CUBE";break;case rl:e="ENVMAP_TYPE_CUBE_UV";break}return e}function hy(i){let e="ENVMAP_MODE_REFLECTION";if(i.envMap)switch(i.envMapMode){case zr:e="ENVMAP_MODE_REFRACTION";break}return e}function uy(i){let e="ENVMAP_BLENDING_NONE";if(i.envMap)switch(i.combine){case Rf:e="ENVMAP_BLENDING_MULTIPLY";break;case eg:e="ENVMAP_BLENDING_MIX";break;case tg:e="ENVMAP_BLENDING_ADD";break}return e}function dy(i){const e=i.envMapCubeUVHeight;if(e===null)return null;const t=Math.log2(e)-2,n=1/e;return{texelWidth:1/(3*Math.max(Math.pow(2,t),7*16)),texelHeight:n,maxMip:t}}function fy(i,e,t,n){const s=i.getContext(),r=t.defines;let a=t.vertexShader,o=t.fragmentShader;const l=ly(t),c=cy(t),h=hy(t),u=uy(t),d=dy(t),f=ey(t),g=ty(r),_=s.createProgram();let m,p,S=t.glslVersion?"#version "+t.glslVersion+`
`:"";t.isRawShaderMaterial?(m=["#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,g].filter(Sa).join(`
`),m.length>0&&(m+=`
`),p=["#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,g].filter(Sa).join(`
`),p.length>0&&(p+=`
`)):(m=[hd(t),"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,g,t.extensionClipCullDistance?"#define USE_CLIP_DISTANCE":"",t.batching?"#define USE_BATCHING":"",t.batchingColor?"#define USE_BATCHING_COLOR":"",t.instancing?"#define USE_INSTANCING":"",t.instancingColor?"#define USE_INSTANCING_COLOR":"",t.instancingMorph?"#define USE_INSTANCING_MORPH":"",t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.map?"#define USE_MAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+h:"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",t.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",t.displacementMap?"#define USE_DISPLACEMENTMAP":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.anisotropy?"#define USE_ANISOTROPY":"",t.anisotropyMap?"#define USE_ANISOTROPYMAP":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",t.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaHash?"#define USE_ALPHAHASH":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",t.mapUv?"#define MAP_UV "+t.mapUv:"",t.alphaMapUv?"#define ALPHAMAP_UV "+t.alphaMapUv:"",t.lightMapUv?"#define LIGHTMAP_UV "+t.lightMapUv:"",t.aoMapUv?"#define AOMAP_UV "+t.aoMapUv:"",t.emissiveMapUv?"#define EMISSIVEMAP_UV "+t.emissiveMapUv:"",t.bumpMapUv?"#define BUMPMAP_UV "+t.bumpMapUv:"",t.normalMapUv?"#define NORMALMAP_UV "+t.normalMapUv:"",t.displacementMapUv?"#define DISPLACEMENTMAP_UV "+t.displacementMapUv:"",t.metalnessMapUv?"#define METALNESSMAP_UV "+t.metalnessMapUv:"",t.roughnessMapUv?"#define ROUGHNESSMAP_UV "+t.roughnessMapUv:"",t.anisotropyMapUv?"#define ANISOTROPYMAP_UV "+t.anisotropyMapUv:"",t.clearcoatMapUv?"#define CLEARCOATMAP_UV "+t.clearcoatMapUv:"",t.clearcoatNormalMapUv?"#define CLEARCOAT_NORMALMAP_UV "+t.clearcoatNormalMapUv:"",t.clearcoatRoughnessMapUv?"#define CLEARCOAT_ROUGHNESSMAP_UV "+t.clearcoatRoughnessMapUv:"",t.iridescenceMapUv?"#define IRIDESCENCEMAP_UV "+t.iridescenceMapUv:"",t.iridescenceThicknessMapUv?"#define IRIDESCENCE_THICKNESSMAP_UV "+t.iridescenceThicknessMapUv:"",t.sheenColorMapUv?"#define SHEEN_COLORMAP_UV "+t.sheenColorMapUv:"",t.sheenRoughnessMapUv?"#define SHEEN_ROUGHNESSMAP_UV "+t.sheenRoughnessMapUv:"",t.specularMapUv?"#define SPECULARMAP_UV "+t.specularMapUv:"",t.specularColorMapUv?"#define SPECULAR_COLORMAP_UV "+t.specularColorMapUv:"",t.specularIntensityMapUv?"#define SPECULAR_INTENSITYMAP_UV "+t.specularIntensityMapUv:"",t.transmissionMapUv?"#define TRANSMISSIONMAP_UV "+t.transmissionMapUv:"",t.thicknessMapUv?"#define THICKNESSMAP_UV "+t.thicknessMapUv:"",t.vertexTangents&&t.flatShading===!1?"#define USE_TANGENT":"",t.vertexColors?"#define USE_COLOR":"",t.vertexAlphas?"#define USE_COLOR_ALPHA":"",t.vertexUv1s?"#define USE_UV1":"",t.vertexUv2s?"#define USE_UV2":"",t.vertexUv3s?"#define USE_UV3":"",t.pointsUvs?"#define USE_POINTS_UV":"",t.flatShading?"#define FLAT_SHADED":"",t.skinning?"#define USE_SKINNING":"",t.morphTargets?"#define USE_MORPHTARGETS":"",t.morphNormals&&t.flatShading===!1?"#define USE_MORPHNORMALS":"",t.morphColors?"#define USE_MORPHCOLORS":"",t.morphTargetsCount>0?"#define MORPHTARGETS_TEXTURE_STRIDE "+t.morphTextureStride:"",t.morphTargetsCount>0?"#define MORPHTARGETS_COUNT "+t.morphTargetsCount:"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+l:"",t.sizeAttenuation?"#define USE_SIZEATTENUATION":"",t.numLightProbes>0?"#define USE_LIGHT_PROBES":"",t.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"","uniform mat4 modelMatrix;","uniform mat4 modelViewMatrix;","uniform mat4 projectionMatrix;","uniform mat4 viewMatrix;","uniform mat3 normalMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;","#ifdef USE_INSTANCING","	attribute mat4 instanceMatrix;","#endif","#ifdef USE_INSTANCING_COLOR","	attribute vec3 instanceColor;","#endif","#ifdef USE_INSTANCING_MORPH","	uniform sampler2D morphTexture;","#endif","attribute vec3 position;","attribute vec3 normal;","attribute vec2 uv;","#ifdef USE_UV1","	attribute vec2 uv1;","#endif","#ifdef USE_UV2","	attribute vec2 uv2;","#endif","#ifdef USE_UV3","	attribute vec2 uv3;","#endif","#ifdef USE_TANGENT","	attribute vec4 tangent;","#endif","#if defined( USE_COLOR_ALPHA )","	attribute vec4 color;","#elif defined( USE_COLOR )","	attribute vec3 color;","#endif","#ifdef USE_SKINNING","	attribute vec4 skinIndex;","	attribute vec4 skinWeight;","#endif",`
`].filter(Sa).join(`
`),p=[hd(t),"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,g,t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.alphaToCoverage?"#define ALPHA_TO_COVERAGE":"",t.map?"#define USE_MAP":"",t.matcap?"#define USE_MATCAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+c:"",t.envMap?"#define "+h:"",t.envMap?"#define "+u:"",d?"#define CUBEUV_TEXEL_WIDTH "+d.texelWidth:"",d?"#define CUBEUV_TEXEL_HEIGHT "+d.texelHeight:"",d?"#define CUBEUV_MAX_MIP "+d.maxMip+".0":"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",t.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.anisotropy?"#define USE_ANISOTROPY":"",t.anisotropyMap?"#define USE_ANISOTROPYMAP":"",t.clearcoat?"#define USE_CLEARCOAT":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.dispersion?"#define USE_DISPERSION":"",t.iridescence?"#define USE_IRIDESCENCE":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",t.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaTest?"#define USE_ALPHATEST":"",t.alphaHash?"#define USE_ALPHAHASH":"",t.sheen?"#define USE_SHEEN":"",t.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.vertexTangents&&t.flatShading===!1?"#define USE_TANGENT":"",t.vertexColors||t.instancingColor||t.batchingColor?"#define USE_COLOR":"",t.vertexAlphas?"#define USE_COLOR_ALPHA":"",t.vertexUv1s?"#define USE_UV1":"",t.vertexUv2s?"#define USE_UV2":"",t.vertexUv3s?"#define USE_UV3":"",t.pointsUvs?"#define USE_POINTS_UV":"",t.gradientMap?"#define USE_GRADIENTMAP":"",t.flatShading?"#define FLAT_SHADED":"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+l:"",t.premultipliedAlpha?"#define PREMULTIPLIED_ALPHA":"",t.numLightProbes>0?"#define USE_LIGHT_PROBES":"",t.decodeVideoTexture?"#define DECODE_VIDEO_TEXTURE":"",t.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"","uniform mat4 viewMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;",t.toneMapping!==cs?"#define TONE_MAPPING":"",t.toneMapping!==cs?rt.tonemapping_pars_fragment:"",t.toneMapping!==cs?Jx("toneMapping",t.toneMapping):"",t.dithering?"#define DITHERING":"",t.opaque?"#define OPAQUE":"",rt.colorspace_pars_fragment,Zx("linearToOutputTexel",t.outputColorSpace),Qx(),t.useDepthPacking?"#define DEPTH_PACKING "+t.depthPacking:"",`
`].filter(Sa).join(`
`)),a=eh(a),a=od(a,t),a=ld(a,t),o=eh(o),o=od(o,t),o=ld(o,t),a=cd(a),o=cd(o),t.isRawShaderMaterial!==!0&&(S=`#version 300 es
`,m=[f,"#define attribute in","#define varying out","#define texture2D texture"].join(`
`)+`
`+m,p=["#define varying in",t.glslVersion===Eu?"":"layout(location = 0) out highp vec4 pc_fragColor;",t.glslVersion===Eu?"":"#define gl_FragColor pc_fragColor","#define gl_FragDepthEXT gl_FragDepth","#define texture2D texture","#define textureCube texture","#define texture2DProj textureProj","#define texture2DLodEXT textureLod","#define texture2DProjLodEXT textureProjLod","#define textureCubeLodEXT textureLod","#define texture2DGradEXT textureGrad","#define texture2DProjGradEXT textureProjGrad","#define textureCubeGradEXT textureGrad"].join(`
`)+`
`+p);const y=S+m+a,w=S+p+o,O=rd(s,s.VERTEX_SHADER,y),A=rd(s,s.FRAGMENT_SHADER,w);s.attachShader(_,O),s.attachShader(_,A),t.index0AttributeName!==void 0?s.bindAttribLocation(_,0,t.index0AttributeName):t.morphTargets===!0&&s.bindAttribLocation(_,0,"position"),s.linkProgram(_);function C(P){if(i.debug.checkShaderErrors){const K=s.getProgramInfoLog(_).trim(),k=s.getShaderInfoLog(O).trim(),Z=s.getShaderInfoLog(A).trim();let q=!0,ee=!0;if(s.getProgramParameter(_,s.LINK_STATUS)===!1)if(q=!1,typeof i.debug.onShaderError=="function")i.debug.onShaderError(s,_,O,A);else{const Y=ad(s,O,"vertex"),ne=ad(s,A,"fragment");console.error("THREE.WebGLProgram: Shader Error "+s.getError()+" - VALIDATE_STATUS "+s.getProgramParameter(_,s.VALIDATE_STATUS)+`

Material Name: `+P.name+`
Material Type: `+P.type+`

Program Info Log: `+K+`
`+Y+`
`+ne)}else K!==""?console.warn("THREE.WebGLProgram: Program Info Log:",K):(k===""||Z==="")&&(ee=!1);ee&&(P.diagnostics={runnable:q,programLog:K,vertexShader:{log:k,prefix:m},fragmentShader:{log:Z,prefix:p}})}s.deleteShader(O),s.deleteShader(A),F=new Oo(s,_),b=ny(s,_)}let F;this.getUniforms=function(){return F===void 0&&C(this),F};let b;this.getAttributes=function(){return b===void 0&&C(this),b};let x=t.rendererExtensionParallelShaderCompile===!1;return this.isReady=function(){return x===!1&&(x=s.getProgramParameter(_,$x)),x},this.destroy=function(){n.releaseStatesOfProgram(this),s.deleteProgram(_),this.program=void 0},this.type=t.shaderType,this.name=t.shaderName,this.id=Yx++,this.cacheKey=e,this.usedTimes=1,this.program=_,this.vertexShader=O,this.fragmentShader=A,this}let py=0;class my{constructor(){this.shaderCache=new Map,this.materialCache=new Map}update(e){const t=e.vertexShader,n=e.fragmentShader,s=this._getShaderStage(t),r=this._getShaderStage(n),a=this._getShaderCacheForMaterial(e);return a.has(s)===!1&&(a.add(s),s.usedTimes++),a.has(r)===!1&&(a.add(r),r.usedTimes++),this}remove(e){const t=this.materialCache.get(e);for(const n of t)n.usedTimes--,n.usedTimes===0&&this.shaderCache.delete(n.code);return this.materialCache.delete(e),this}getVertexShaderID(e){return this._getShaderStage(e.vertexShader).id}getFragmentShaderID(e){return this._getShaderStage(e.fragmentShader).id}dispose(){this.shaderCache.clear(),this.materialCache.clear()}_getShaderCacheForMaterial(e){const t=this.materialCache;let n=t.get(e);return n===void 0&&(n=new Set,t.set(e,n)),n}_getShaderStage(e){const t=this.shaderCache;let n=t.get(e);return n===void 0&&(n=new gy(e),t.set(e,n)),n}}class gy{constructor(e){this.id=py++,this.code=e,this.usedTimes=0}}function _y(i,e,t,n,s,r,a){const o=new bh,l=new my,c=new Set,h=[],u=s.logarithmicDepthBuffer,d=s.vertexTextures;let f=s.precision;const g={MeshDepthMaterial:"depth",MeshDistanceMaterial:"distanceRGBA",MeshNormalMaterial:"normal",MeshBasicMaterial:"basic",MeshLambertMaterial:"lambert",MeshPhongMaterial:"phong",MeshToonMaterial:"toon",MeshStandardMaterial:"physical",MeshPhysicalMaterial:"physical",MeshMatcapMaterial:"matcap",LineBasicMaterial:"basic",LineDashedMaterial:"dashed",PointsMaterial:"points",ShadowMaterial:"shadow",SpriteMaterial:"sprite"};function _(b){return c.add(b),b===0?"uv":`uv${b}`}function m(b,x,P,K,k){const Z=K.fog,q=k.geometry,ee=b.isMeshStandardMaterial?K.environment:null,Y=(b.isMeshStandardMaterial?t:e).get(b.envMap||ee),ne=Y&&Y.mapping===rl?Y.image.height:null,ge=g[b.type];b.precision!==null&&(f=s.getMaxPrecision(b.precision),f!==b.precision&&console.warn("THREE.WebGLProgram.getParameters:",b.precision,"not supported, using",f,"instead."));const de=q.morphAttributes.position||q.morphAttributes.normal||q.morphAttributes.color,xe=de!==void 0?de.length:0;let we=0;q.morphAttributes.position!==void 0&&(we=1),q.morphAttributes.normal!==void 0&&(we=2),q.morphAttributes.color!==void 0&&(we=3);let ye,ie,he,Me;if(ge){const lt=yi[ge];ye=lt.vertexShader,ie=lt.fragmentShader}else ye=b.vertexShader,ie=b.fragmentShader,l.update(b),he=l.getVertexShaderID(b),Me=l.getFragmentShaderID(b);const fe=i.getRenderTarget(),ze=k.isInstancedMesh===!0,Ge=k.isBatchedMesh===!0,Fe=!!b.map,pt=!!b.matcap,N=!!Y,dt=!!b.aoMap,st=!!b.lightMap,ct=!!b.bumpMap,Oe=!!b.normalMap,Et=!!b.displacementMap,$e=!!b.emissiveMap,Xe=!!b.metalnessMap,D=!!b.roughnessMap,E=b.anisotropy>0,Q=b.clearcoat>0,le=b.dispersion>0,te=b.iridescence>0,X=b.sheen>0,Ee=b.transmission>0,_e=E&&!!b.anisotropyMap,Ae=Q&&!!b.clearcoatMap,Ke=Q&&!!b.clearcoatNormalMap,me=Q&&!!b.clearcoatRoughnessMap,Te=te&&!!b.iridescenceMap,Ze=te&&!!b.iridescenceThicknessMap,ke=X&&!!b.sheenColorMap,be=X&&!!b.sheenRoughnessMap,He=!!b.specularMap,B=!!b.specularColorMap,ce=!!b.specularIntensityMap,I=Ee&&!!b.transmissionMap,ae=Ee&&!!b.thicknessMap,se=!!b.gradientMap,re=!!b.alphaMap,ve=b.alphaTest>0,je=!!b.alphaHash,ot=!!b.extensions;let _t=cs;b.toneMapped&&(fe===null||fe.isXRRenderTarget===!0)&&(_t=i.toneMapping);const wt={shaderID:ge,shaderType:b.type,shaderName:b.name,vertexShader:ye,fragmentShader:ie,defines:b.defines,customVertexShaderID:he,customFragmentShaderID:Me,isRawShaderMaterial:b.isRawShaderMaterial===!0,glslVersion:b.glslVersion,precision:f,batching:Ge,batchingColor:Ge&&k._colorsTexture!==null,instancing:ze,instancingColor:ze&&k.instanceColor!==null,instancingMorph:ze&&k.morphTexture!==null,supportsVertexTextures:d,outputColorSpace:fe===null?i.outputColorSpace:fe.isXRRenderTarget===!0?fe.texture.colorSpace:ps,alphaToCoverage:!!b.alphaToCoverage,map:Fe,matcap:pt,envMap:N,envMapMode:N&&Y.mapping,envMapCubeUVHeight:ne,aoMap:dt,lightMap:st,bumpMap:ct,normalMap:Oe,displacementMap:d&&Et,emissiveMap:$e,normalMapObjectSpace:Oe&&b.normalMapType===ug,normalMapTangentSpace:Oe&&b.normalMapType===Hf,metalnessMap:Xe,roughnessMap:D,anisotropy:E,anisotropyMap:_e,clearcoat:Q,clearcoatMap:Ae,clearcoatNormalMap:Ke,clearcoatRoughnessMap:me,dispersion:le,iridescence:te,iridescenceMap:Te,iridescenceThicknessMap:Ze,sheen:X,sheenColorMap:ke,sheenRoughnessMap:be,specularMap:He,specularColorMap:B,specularIntensityMap:ce,transmission:Ee,transmissionMap:I,thicknessMap:ae,gradientMap:se,opaque:b.transparent===!1&&b.blending===Cr&&b.alphaToCoverage===!1,alphaMap:re,alphaTest:ve,alphaHash:je,combine:b.combine,mapUv:Fe&&_(b.map.channel),aoMapUv:dt&&_(b.aoMap.channel),lightMapUv:st&&_(b.lightMap.channel),bumpMapUv:ct&&_(b.bumpMap.channel),normalMapUv:Oe&&_(b.normalMap.channel),displacementMapUv:Et&&_(b.displacementMap.channel),emissiveMapUv:$e&&_(b.emissiveMap.channel),metalnessMapUv:Xe&&_(b.metalnessMap.channel),roughnessMapUv:D&&_(b.roughnessMap.channel),anisotropyMapUv:_e&&_(b.anisotropyMap.channel),clearcoatMapUv:Ae&&_(b.clearcoatMap.channel),clearcoatNormalMapUv:Ke&&_(b.clearcoatNormalMap.channel),clearcoatRoughnessMapUv:me&&_(b.clearcoatRoughnessMap.channel),iridescenceMapUv:Te&&_(b.iridescenceMap.channel),iridescenceThicknessMapUv:Ze&&_(b.iridescenceThicknessMap.channel),sheenColorMapUv:ke&&_(b.sheenColorMap.channel),sheenRoughnessMapUv:be&&_(b.sheenRoughnessMap.channel),specularMapUv:He&&_(b.specularMap.channel),specularColorMapUv:B&&_(b.specularColorMap.channel),specularIntensityMapUv:ce&&_(b.specularIntensityMap.channel),transmissionMapUv:I&&_(b.transmissionMap.channel),thicknessMapUv:ae&&_(b.thicknessMap.channel),alphaMapUv:re&&_(b.alphaMap.channel),vertexTangents:!!q.attributes.tangent&&(Oe||E),vertexColors:b.vertexColors,vertexAlphas:b.vertexColors===!0&&!!q.attributes.color&&q.attributes.color.itemSize===4,pointsUvs:k.isPoints===!0&&!!q.attributes.uv&&(Fe||re),fog:!!Z,useFog:b.fog===!0,fogExp2:!!Z&&Z.isFogExp2,flatShading:b.flatShading===!0,sizeAttenuation:b.sizeAttenuation===!0,logarithmicDepthBuffer:u,skinning:k.isSkinnedMesh===!0,morphTargets:q.morphAttributes.position!==void 0,morphNormals:q.morphAttributes.normal!==void 0,morphColors:q.morphAttributes.color!==void 0,morphTargetsCount:xe,morphTextureStride:we,numDirLights:x.directional.length,numPointLights:x.point.length,numSpotLights:x.spot.length,numSpotLightMaps:x.spotLightMap.length,numRectAreaLights:x.rectArea.length,numHemiLights:x.hemi.length,numDirLightShadows:x.directionalShadowMap.length,numPointLightShadows:x.pointShadowMap.length,numSpotLightShadows:x.spotShadowMap.length,numSpotLightShadowsWithMaps:x.numSpotLightShadowsWithMaps,numLightProbes:x.numLightProbes,numClippingPlanes:a.numPlanes,numClipIntersection:a.numIntersection,dithering:b.dithering,shadowMapEnabled:i.shadowMap.enabled&&P.length>0,shadowMapType:i.shadowMap.type,toneMapping:_t,decodeVideoTexture:Fe&&b.map.isVideoTexture===!0&&bt.getTransfer(b.map.colorSpace)===Ot,premultipliedAlpha:b.premultipliedAlpha,doubleSided:b.side===Yn,flipSided:b.side===In,useDepthPacking:b.depthPacking>=0,depthPacking:b.depthPacking||0,index0AttributeName:b.index0AttributeName,extensionClipCullDistance:ot&&b.extensions.clipCullDistance===!0&&n.has("WEBGL_clip_cull_distance"),extensionMultiDraw:(ot&&b.extensions.multiDraw===!0||Ge)&&n.has("WEBGL_multi_draw"),rendererExtensionParallelShaderCompile:n.has("KHR_parallel_shader_compile"),customProgramCacheKey:b.customProgramCacheKey()};return wt.vertexUv1s=c.has(1),wt.vertexUv2s=c.has(2),wt.vertexUv3s=c.has(3),c.clear(),wt}function p(b){const x=[];if(b.shaderID?x.push(b.shaderID):(x.push(b.customVertexShaderID),x.push(b.customFragmentShaderID)),b.defines!==void 0)for(const P in b.defines)x.push(P),x.push(b.defines[P]);return b.isRawShaderMaterial===!1&&(S(x,b),y(x,b),x.push(i.outputColorSpace)),x.push(b.customProgramCacheKey),x.join()}function S(b,x){b.push(x.precision),b.push(x.outputColorSpace),b.push(x.envMapMode),b.push(x.envMapCubeUVHeight),b.push(x.mapUv),b.push(x.alphaMapUv),b.push(x.lightMapUv),b.push(x.aoMapUv),b.push(x.bumpMapUv),b.push(x.normalMapUv),b.push(x.displacementMapUv),b.push(x.emissiveMapUv),b.push(x.metalnessMapUv),b.push(x.roughnessMapUv),b.push(x.anisotropyMapUv),b.push(x.clearcoatMapUv),b.push(x.clearcoatNormalMapUv),b.push(x.clearcoatRoughnessMapUv),b.push(x.iridescenceMapUv),b.push(x.iridescenceThicknessMapUv),b.push(x.sheenColorMapUv),b.push(x.sheenRoughnessMapUv),b.push(x.specularMapUv),b.push(x.specularColorMapUv),b.push(x.specularIntensityMapUv),b.push(x.transmissionMapUv),b.push(x.thicknessMapUv),b.push(x.combine),b.push(x.fogExp2),b.push(x.sizeAttenuation),b.push(x.morphTargetsCount),b.push(x.morphAttributeCount),b.push(x.numDirLights),b.push(x.numPointLights),b.push(x.numSpotLights),b.push(x.numSpotLightMaps),b.push(x.numHemiLights),b.push(x.numRectAreaLights),b.push(x.numDirLightShadows),b.push(x.numPointLightShadows),b.push(x.numSpotLightShadows),b.push(x.numSpotLightShadowsWithMaps),b.push(x.numLightProbes),b.push(x.shadowMapType),b.push(x.toneMapping),b.push(x.numClippingPlanes),b.push(x.numClipIntersection),b.push(x.depthPacking)}function y(b,x){o.disableAll(),x.supportsVertexTextures&&o.enable(0),x.instancing&&o.enable(1),x.instancingColor&&o.enable(2),x.instancingMorph&&o.enable(3),x.matcap&&o.enable(4),x.envMap&&o.enable(5),x.normalMapObjectSpace&&o.enable(6),x.normalMapTangentSpace&&o.enable(7),x.clearcoat&&o.enable(8),x.iridescence&&o.enable(9),x.alphaTest&&o.enable(10),x.vertexColors&&o.enable(11),x.vertexAlphas&&o.enable(12),x.vertexUv1s&&o.enable(13),x.vertexUv2s&&o.enable(14),x.vertexUv3s&&o.enable(15),x.vertexTangents&&o.enable(16),x.anisotropy&&o.enable(17),x.alphaHash&&o.enable(18),x.batching&&o.enable(19),x.dispersion&&o.enable(20),x.batchingColor&&o.enable(21),b.push(o.mask),o.disableAll(),x.fog&&o.enable(0),x.useFog&&o.enable(1),x.flatShading&&o.enable(2),x.logarithmicDepthBuffer&&o.enable(3),x.skinning&&o.enable(4),x.morphTargets&&o.enable(5),x.morphNormals&&o.enable(6),x.morphColors&&o.enable(7),x.premultipliedAlpha&&o.enable(8),x.shadowMapEnabled&&o.enable(9),x.doubleSided&&o.enable(10),x.flipSided&&o.enable(11),x.useDepthPacking&&o.enable(12),x.dithering&&o.enable(13),x.transmission&&o.enable(14),x.sheen&&o.enable(15),x.opaque&&o.enable(16),x.pointsUvs&&o.enable(17),x.decodeVideoTexture&&o.enable(18),x.alphaToCoverage&&o.enable(19),b.push(o.mask)}function w(b){const x=g[b.type];let P;if(x){const K=yi[x];P=e_.clone(K.uniforms)}else P=b.uniforms;return P}function O(b,x){let P;for(let K=0,k=h.length;K<k;K++){const Z=h[K];if(Z.cacheKey===x){P=Z,++P.usedTimes;break}}return P===void 0&&(P=new fy(i,x,b,r),h.push(P)),P}function A(b){if(--b.usedTimes===0){const x=h.indexOf(b);h[x]=h[h.length-1],h.pop(),b.destroy()}}function C(b){l.remove(b)}function F(){l.dispose()}return{getParameters:m,getProgramCacheKey:p,getUniforms:w,acquireProgram:O,releaseProgram:A,releaseShaderCache:C,programs:h,dispose:F}}function vy(){let i=new WeakMap;function e(a){return i.has(a)}function t(a){let o=i.get(a);return o===void 0&&(o={},i.set(a,o)),o}function n(a){i.delete(a)}function s(a,o,l){i.get(a)[o]=l}function r(){i=new WeakMap}return{has:e,get:t,remove:n,update:s,dispose:r}}function xy(i,e){return i.groupOrder!==e.groupOrder?i.groupOrder-e.groupOrder:i.renderOrder!==e.renderOrder?i.renderOrder-e.renderOrder:i.material.id!==e.material.id?i.material.id-e.material.id:i.z!==e.z?i.z-e.z:i.id-e.id}function ud(i,e){return i.groupOrder!==e.groupOrder?i.groupOrder-e.groupOrder:i.renderOrder!==e.renderOrder?i.renderOrder-e.renderOrder:i.z!==e.z?e.z-i.z:i.id-e.id}function dd(){const i=[];let e=0;const t=[],n=[],s=[];function r(){e=0,t.length=0,n.length=0,s.length=0}function a(u,d,f,g,_,m){let p=i[e];return p===void 0?(p={id:u.id,object:u,geometry:d,material:f,groupOrder:g,renderOrder:u.renderOrder,z:_,group:m},i[e]=p):(p.id=u.id,p.object=u,p.geometry=d,p.material=f,p.groupOrder=g,p.renderOrder=u.renderOrder,p.z=_,p.group=m),e++,p}function o(u,d,f,g,_,m){const p=a(u,d,f,g,_,m);f.transmission>0?n.push(p):f.transparent===!0?s.push(p):t.push(p)}function l(u,d,f,g,_,m){const p=a(u,d,f,g,_,m);f.transmission>0?n.unshift(p):f.transparent===!0?s.unshift(p):t.unshift(p)}function c(u,d){t.length>1&&t.sort(u||xy),n.length>1&&n.sort(d||ud),s.length>1&&s.sort(d||ud)}function h(){for(let u=e,d=i.length;u<d;u++){const f=i[u];if(f.id===null)break;f.id=null,f.object=null,f.geometry=null,f.material=null,f.group=null}}return{opaque:t,transmissive:n,transparent:s,init:r,push:o,unshift:l,finish:h,sort:c}}function yy(){let i=new WeakMap;function e(n,s){const r=i.get(n);let a;return r===void 0?(a=new dd,i.set(n,[a])):s>=r.length?(a=new dd,r.push(a)):a=r[s],a}function t(){i=new WeakMap}return{get:e,dispose:t}}function My(){const i={};return{get:function(e){if(i[e.id]!==void 0)return i[e.id];let t;switch(e.type){case"DirectionalLight":t={direction:new H,color:new nt};break;case"SpotLight":t={position:new H,direction:new H,color:new nt,distance:0,coneCos:0,penumbraCos:0,decay:0};break;case"PointLight":t={position:new H,color:new nt,distance:0,decay:0};break;case"HemisphereLight":t={direction:new H,skyColor:new nt,groundColor:new nt};break;case"RectAreaLight":t={color:new nt,position:new H,halfWidth:new H,halfHeight:new H};break}return i[e.id]=t,t}}}function Sy(){const i={};return{get:function(e){if(i[e.id]!==void 0)return i[e.id];let t;switch(e.type){case"DirectionalLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new qe};break;case"SpotLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new qe};break;case"PointLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new qe,shadowCameraNear:1,shadowCameraFar:1e3};break}return i[e.id]=t,t}}}let by=0;function Ey(i,e){return(e.castShadow?2:0)-(i.castShadow?2:0)+(e.map?1:0)-(i.map?1:0)}function wy(i){const e=new My,t=Sy(),n={version:0,hash:{directionalLength:-1,pointLength:-1,spotLength:-1,rectAreaLength:-1,hemiLength:-1,numDirectionalShadows:-1,numPointShadows:-1,numSpotShadows:-1,numSpotMaps:-1,numLightProbes:-1},ambient:[0,0,0],probe:[],directional:[],directionalShadow:[],directionalShadowMap:[],directionalShadowMatrix:[],spot:[],spotLightMap:[],spotShadow:[],spotShadowMap:[],spotLightMatrix:[],rectArea:[],rectAreaLTC1:null,rectAreaLTC2:null,point:[],pointShadow:[],pointShadowMap:[],pointShadowMatrix:[],hemi:[],numSpotLightShadowsWithMaps:0,numLightProbes:0};for(let c=0;c<9;c++)n.probe.push(new H);const s=new H,r=new Bt,a=new Bt;function o(c){let h=0,u=0,d=0;for(let b=0;b<9;b++)n.probe[b].set(0,0,0);let f=0,g=0,_=0,m=0,p=0,S=0,y=0,w=0,O=0,A=0,C=0;c.sort(Ey);for(let b=0,x=c.length;b<x;b++){const P=c[b],K=P.color,k=P.intensity,Z=P.distance,q=P.shadow&&P.shadow.map?P.shadow.map.texture:null;if(P.isAmbientLight)h+=K.r*k,u+=K.g*k,d+=K.b*k;else if(P.isLightProbe){for(let ee=0;ee<9;ee++)n.probe[ee].addScaledVector(P.sh.coefficients[ee],k);C++}else if(P.isDirectionalLight){const ee=e.get(P);if(ee.color.copy(P.color).multiplyScalar(P.intensity),P.castShadow){const Y=P.shadow,ne=t.get(P);ne.shadowIntensity=Y.intensity,ne.shadowBias=Y.bias,ne.shadowNormalBias=Y.normalBias,ne.shadowRadius=Y.radius,ne.shadowMapSize=Y.mapSize,n.directionalShadow[f]=ne,n.directionalShadowMap[f]=q,n.directionalShadowMatrix[f]=P.shadow.matrix,S++}n.directional[f]=ee,f++}else if(P.isSpotLight){const ee=e.get(P);ee.position.setFromMatrixPosition(P.matrixWorld),ee.color.copy(K).multiplyScalar(k),ee.distance=Z,ee.coneCos=Math.cos(P.angle),ee.penumbraCos=Math.cos(P.angle*(1-P.penumbra)),ee.decay=P.decay,n.spot[_]=ee;const Y=P.shadow;if(P.map&&(n.spotLightMap[O]=P.map,O++,Y.updateMatrices(P),P.castShadow&&A++),n.spotLightMatrix[_]=Y.matrix,P.castShadow){const ne=t.get(P);ne.shadowIntensity=Y.intensity,ne.shadowBias=Y.bias,ne.shadowNormalBias=Y.normalBias,ne.shadowRadius=Y.radius,ne.shadowMapSize=Y.mapSize,n.spotShadow[_]=ne,n.spotShadowMap[_]=q,w++}_++}else if(P.isRectAreaLight){const ee=e.get(P);ee.color.copy(K).multiplyScalar(k),ee.halfWidth.set(P.width*.5,0,0),ee.halfHeight.set(0,P.height*.5,0),n.rectArea[m]=ee,m++}else if(P.isPointLight){const ee=e.get(P);if(ee.color.copy(P.color).multiplyScalar(P.intensity),ee.distance=P.distance,ee.decay=P.decay,P.castShadow){const Y=P.shadow,ne=t.get(P);ne.shadowIntensity=Y.intensity,ne.shadowBias=Y.bias,ne.shadowNormalBias=Y.normalBias,ne.shadowRadius=Y.radius,ne.shadowMapSize=Y.mapSize,ne.shadowCameraNear=Y.camera.near,ne.shadowCameraFar=Y.camera.far,n.pointShadow[g]=ne,n.pointShadowMap[g]=q,n.pointShadowMatrix[g]=P.shadow.matrix,y++}n.point[g]=ee,g++}else if(P.isHemisphereLight){const ee=e.get(P);ee.skyColor.copy(P.color).multiplyScalar(k),ee.groundColor.copy(P.groundColor).multiplyScalar(k),n.hemi[p]=ee,p++}}m>0&&(i.has("OES_texture_float_linear")===!0?(n.rectAreaLTC1=Re.LTC_FLOAT_1,n.rectAreaLTC2=Re.LTC_FLOAT_2):(n.rectAreaLTC1=Re.LTC_HALF_1,n.rectAreaLTC2=Re.LTC_HALF_2)),n.ambient[0]=h,n.ambient[1]=u,n.ambient[2]=d;const F=n.hash;(F.directionalLength!==f||F.pointLength!==g||F.spotLength!==_||F.rectAreaLength!==m||F.hemiLength!==p||F.numDirectionalShadows!==S||F.numPointShadows!==y||F.numSpotShadows!==w||F.numSpotMaps!==O||F.numLightProbes!==C)&&(n.directional.length=f,n.spot.length=_,n.rectArea.length=m,n.point.length=g,n.hemi.length=p,n.directionalShadow.length=S,n.directionalShadowMap.length=S,n.pointShadow.length=y,n.pointShadowMap.length=y,n.spotShadow.length=w,n.spotShadowMap.length=w,n.directionalShadowMatrix.length=S,n.pointShadowMatrix.length=y,n.spotLightMatrix.length=w+O-A,n.spotLightMap.length=O,n.numSpotLightShadowsWithMaps=A,n.numLightProbes=C,F.directionalLength=f,F.pointLength=g,F.spotLength=_,F.rectAreaLength=m,F.hemiLength=p,F.numDirectionalShadows=S,F.numPointShadows=y,F.numSpotShadows=w,F.numSpotMaps=O,F.numLightProbes=C,n.version=by++)}function l(c,h){let u=0,d=0,f=0,g=0,_=0;const m=h.matrixWorldInverse;for(let p=0,S=c.length;p<S;p++){const y=c[p];if(y.isDirectionalLight){const w=n.directional[u];w.direction.setFromMatrixPosition(y.matrixWorld),s.setFromMatrixPosition(y.target.matrixWorld),w.direction.sub(s),w.direction.transformDirection(m),u++}else if(y.isSpotLight){const w=n.spot[f];w.position.setFromMatrixPosition(y.matrixWorld),w.position.applyMatrix4(m),w.direction.setFromMatrixPosition(y.matrixWorld),s.setFromMatrixPosition(y.target.matrixWorld),w.direction.sub(s),w.direction.transformDirection(m),f++}else if(y.isRectAreaLight){const w=n.rectArea[g];w.position.setFromMatrixPosition(y.matrixWorld),w.position.applyMatrix4(m),a.identity(),r.copy(y.matrixWorld),r.premultiply(m),a.extractRotation(r),w.halfWidth.set(y.width*.5,0,0),w.halfHeight.set(0,y.height*.5,0),w.halfWidth.applyMatrix4(a),w.halfHeight.applyMatrix4(a),g++}else if(y.isPointLight){const w=n.point[d];w.position.setFromMatrixPosition(y.matrixWorld),w.position.applyMatrix4(m),d++}else if(y.isHemisphereLight){const w=n.hemi[_];w.direction.setFromMatrixPosition(y.matrixWorld),w.direction.transformDirection(m),_++}}}return{setup:o,setupView:l,state:n}}function fd(i){const e=new wy(i),t=[],n=[];function s(h){c.camera=h,t.length=0,n.length=0}function r(h){t.push(h)}function a(h){n.push(h)}function o(){e.setup(t)}function l(h){e.setupView(t,h)}const c={lightsArray:t,shadowsArray:n,camera:null,lights:e,transmissionRenderTarget:{}};return{init:s,state:c,setupLights:o,setupLightsView:l,pushLight:r,pushShadow:a}}function Ty(i){let e=new WeakMap;function t(s,r=0){const a=e.get(s);let o;return a===void 0?(o=new fd(i),e.set(s,[o])):r>=a.length?(o=new fd(i),a.push(o)):o=a[r],o}function n(){e=new WeakMap}return{get:t,dispose:n}}class Ay extends ms{constructor(e){super(),this.isMeshDepthMaterial=!0,this.type="MeshDepthMaterial",this.depthPacking=cg,this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.wireframe=!1,this.wireframeLinewidth=1,this.setValues(e)}copy(e){return super.copy(e),this.depthPacking=e.depthPacking,this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this}}class Ry extends ms{constructor(e){super(),this.isMeshDistanceMaterial=!0,this.type="MeshDistanceMaterial",this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.setValues(e)}copy(e){return super.copy(e),this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this}}const Cy=`void main() {
	gl_Position = vec4( position, 1.0 );
}`,Py=`uniform sampler2D shadow_pass;
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
}`;function Ly(i,e,t){let n=new Eh;const s=new qe,r=new qe,a=new nn,o=new Ay({depthPacking:hg}),l=new Ry,c={},h=t.maxTextureSize,u={[hs]:In,[In]:hs,[Yn]:Yn},d=new us({defines:{VSM_SAMPLES:8},uniforms:{shadow_pass:{value:null},resolution:{value:new qe},radius:{value:4}},vertexShader:Cy,fragmentShader:Py}),f=d.clone();f.defines.HORIZONTAL_PASS=1;const g=new Xt;g.setAttribute("position",new hi(new Float32Array([-1,-1,.5,3,-1,.5,-1,3,.5]),3));const _=new _n(g,d),m=this;this.enabled=!1,this.autoUpdate=!0,this.needsUpdate=!1,this.type=Tf;let p=this.type;this.render=function(A,C,F){if(m.enabled===!1||m.autoUpdate===!1&&m.needsUpdate===!1||A.length===0)return;const b=i.getRenderTarget(),x=i.getActiveCubeFace(),P=i.getActiveMipmapLevel(),K=i.state;K.setBlending(ls),K.buffers.color.setClear(1,1,1,1),K.buffers.depth.setTest(!0),K.setScissorTest(!1);const k=p!==Ni&&this.type===Ni,Z=p===Ni&&this.type!==Ni;for(let q=0,ee=A.length;q<ee;q++){const Y=A[q],ne=Y.shadow;if(ne===void 0){console.warn("THREE.WebGLShadowMap:",Y,"has no shadow.");continue}if(ne.autoUpdate===!1&&ne.needsUpdate===!1)continue;s.copy(ne.mapSize);const ge=ne.getFrameExtents();if(s.multiply(ge),r.copy(ne.mapSize),(s.x>h||s.y>h)&&(s.x>h&&(r.x=Math.floor(h/ge.x),s.x=r.x*ge.x,ne.mapSize.x=r.x),s.y>h&&(r.y=Math.floor(h/ge.y),s.y=r.y*ge.y,ne.mapSize.y=r.y)),ne.map===null||k===!0||Z===!0){const xe=this.type!==Ni?{minFilter:Kn,magFilter:Kn}:{};ne.map!==null&&ne.map.dispose(),ne.map=new zs(s.x,s.y,xe),ne.map.texture.name=Y.name+".shadowMap",ne.camera.updateProjectionMatrix()}i.setRenderTarget(ne.map),i.clear();const de=ne.getViewportCount();for(let xe=0;xe<de;xe++){const we=ne.getViewport(xe);a.set(r.x*we.x,r.y*we.y,r.x*we.z,r.y*we.w),K.viewport(a),ne.updateMatrices(Y,xe),n=ne.getFrustum(),w(C,F,ne.camera,Y,this.type)}ne.isPointLightShadow!==!0&&this.type===Ni&&S(ne,F),ne.needsUpdate=!1}p=this.type,m.needsUpdate=!1,i.setRenderTarget(b,x,P)};function S(A,C){const F=e.update(_);d.defines.VSM_SAMPLES!==A.blurSamples&&(d.defines.VSM_SAMPLES=A.blurSamples,f.defines.VSM_SAMPLES=A.blurSamples,d.needsUpdate=!0,f.needsUpdate=!0),A.mapPass===null&&(A.mapPass=new zs(s.x,s.y)),d.uniforms.shadow_pass.value=A.map.texture,d.uniforms.resolution.value=A.mapSize,d.uniforms.radius.value=A.radius,i.setRenderTarget(A.mapPass),i.clear(),i.renderBufferDirect(C,null,F,d,_,null),f.uniforms.shadow_pass.value=A.mapPass.texture,f.uniforms.resolution.value=A.mapSize,f.uniforms.radius.value=A.radius,i.setRenderTarget(A.map),i.clear(),i.renderBufferDirect(C,null,F,f,_,null)}function y(A,C,F,b){let x=null;const P=F.isPointLight===!0?A.customDistanceMaterial:A.customDepthMaterial;if(P!==void 0)x=P;else if(x=F.isPointLight===!0?l:o,i.localClippingEnabled&&C.clipShadows===!0&&Array.isArray(C.clippingPlanes)&&C.clippingPlanes.length!==0||C.displacementMap&&C.displacementScale!==0||C.alphaMap&&C.alphaTest>0||C.map&&C.alphaTest>0){const K=x.uuid,k=C.uuid;let Z=c[K];Z===void 0&&(Z={},c[K]=Z);let q=Z[k];q===void 0&&(q=x.clone(),Z[k]=q,C.addEventListener("dispose",O)),x=q}if(x.visible=C.visible,x.wireframe=C.wireframe,b===Ni?x.side=C.shadowSide!==null?C.shadowSide:C.side:x.side=C.shadowSide!==null?C.shadowSide:u[C.side],x.alphaMap=C.alphaMap,x.alphaTest=C.alphaTest,x.map=C.map,x.clipShadows=C.clipShadows,x.clippingPlanes=C.clippingPlanes,x.clipIntersection=C.clipIntersection,x.displacementMap=C.displacementMap,x.displacementScale=C.displacementScale,x.displacementBias=C.displacementBias,x.wireframeLinewidth=C.wireframeLinewidth,x.linewidth=C.linewidth,F.isPointLight===!0&&x.isMeshDistanceMaterial===!0){const K=i.properties.get(x);K.light=F}return x}function w(A,C,F,b,x){if(A.visible===!1)return;if(A.layers.test(C.layers)&&(A.isMesh||A.isLine||A.isPoints)&&(A.castShadow||A.receiveShadow&&x===Ni)&&(!A.frustumCulled||n.intersectsObject(A))){A.modelViewMatrix.multiplyMatrices(F.matrixWorldInverse,A.matrixWorld);const k=e.update(A),Z=A.material;if(Array.isArray(Z)){const q=k.groups;for(let ee=0,Y=q.length;ee<Y;ee++){const ne=q[ee],ge=Z[ne.materialIndex];if(ge&&ge.visible){const de=y(A,ge,b,x);A.onBeforeShadow(i,A,C,F,k,de,ne),i.renderBufferDirect(F,null,k,de,A,ne),A.onAfterShadow(i,A,C,F,k,de,ne)}}}else if(Z.visible){const q=y(A,Z,b,x);A.onBeforeShadow(i,A,C,F,k,q,null),i.renderBufferDirect(F,null,k,q,A,null),A.onAfterShadow(i,A,C,F,k,q,null)}}const K=A.children;for(let k=0,Z=K.length;k<Z;k++)w(K[k],C,F,b,x)}function O(A){A.target.removeEventListener("dispose",O);for(const F in c){const b=c[F],x=A.target.uuid;x in b&&(b[x].dispose(),delete b[x])}}}function Dy(i){function e(){let I=!1;const ae=new nn;let se=null;const re=new nn(0,0,0,0);return{setMask:function(ve){se!==ve&&!I&&(i.colorMask(ve,ve,ve,ve),se=ve)},setLocked:function(ve){I=ve},setClear:function(ve,je,ot,_t,wt){wt===!0&&(ve*=_t,je*=_t,ot*=_t),ae.set(ve,je,ot,_t),re.equals(ae)===!1&&(i.clearColor(ve,je,ot,_t),re.copy(ae))},reset:function(){I=!1,se=null,re.set(-1,0,0,0)}}}function t(){let I=!1,ae=null,se=null,re=null;return{setTest:function(ve){ve?Me(i.DEPTH_TEST):fe(i.DEPTH_TEST)},setMask:function(ve){ae!==ve&&!I&&(i.depthMask(ve),ae=ve)},setFunc:function(ve){if(se!==ve){switch(ve){case $m:i.depthFunc(i.NEVER);break;case Ym:i.depthFunc(i.ALWAYS);break;case jm:i.depthFunc(i.LESS);break;case Ho:i.depthFunc(i.LEQUAL);break;case Km:i.depthFunc(i.EQUAL);break;case Zm:i.depthFunc(i.GEQUAL);break;case Jm:i.depthFunc(i.GREATER);break;case Qm:i.depthFunc(i.NOTEQUAL);break;default:i.depthFunc(i.LEQUAL)}se=ve}},setLocked:function(ve){I=ve},setClear:function(ve){re!==ve&&(i.clearDepth(ve),re=ve)},reset:function(){I=!1,ae=null,se=null,re=null}}}function n(){let I=!1,ae=null,se=null,re=null,ve=null,je=null,ot=null,_t=null,wt=null;return{setTest:function(lt){I||(lt?Me(i.STENCIL_TEST):fe(i.STENCIL_TEST))},setMask:function(lt){ae!==lt&&!I&&(i.stencilMask(lt),ae=lt)},setFunc:function(lt,pn,zt){(se!==lt||re!==pn||ve!==zt)&&(i.stencilFunc(lt,pn,zt),se=lt,re=pn,ve=zt)},setOp:function(lt,pn,zt){(je!==lt||ot!==pn||_t!==zt)&&(i.stencilOp(lt,pn,zt),je=lt,ot=pn,_t=zt)},setLocked:function(lt){I=lt},setClear:function(lt){wt!==lt&&(i.clearStencil(lt),wt=lt)},reset:function(){I=!1,ae=null,se=null,re=null,ve=null,je=null,ot=null,_t=null,wt=null}}}const s=new e,r=new t,a=new n,o=new WeakMap,l=new WeakMap;let c={},h={},u=new WeakMap,d=[],f=null,g=!1,_=null,m=null,p=null,S=null,y=null,w=null,O=null,A=new nt(0,0,0),C=0,F=!1,b=null,x=null,P=null,K=null,k=null;const Z=i.getParameter(i.MAX_COMBINED_TEXTURE_IMAGE_UNITS);let q=!1,ee=0;const Y=i.getParameter(i.VERSION);Y.indexOf("WebGL")!==-1?(ee=parseFloat(/^WebGL (\d)/.exec(Y)[1]),q=ee>=1):Y.indexOf("OpenGL ES")!==-1&&(ee=parseFloat(/^OpenGL ES (\d)/.exec(Y)[1]),q=ee>=2);let ne=null,ge={};const de=i.getParameter(i.SCISSOR_BOX),xe=i.getParameter(i.VIEWPORT),we=new nn().fromArray(de),ye=new nn().fromArray(xe);function ie(I,ae,se,re){const ve=new Uint8Array(4),je=i.createTexture();i.bindTexture(I,je),i.texParameteri(I,i.TEXTURE_MIN_FILTER,i.NEAREST),i.texParameteri(I,i.TEXTURE_MAG_FILTER,i.NEAREST);for(let ot=0;ot<se;ot++)I===i.TEXTURE_3D||I===i.TEXTURE_2D_ARRAY?i.texImage3D(ae,0,i.RGBA,1,1,re,0,i.RGBA,i.UNSIGNED_BYTE,ve):i.texImage2D(ae+ot,0,i.RGBA,1,1,0,i.RGBA,i.UNSIGNED_BYTE,ve);return je}const he={};he[i.TEXTURE_2D]=ie(i.TEXTURE_2D,i.TEXTURE_2D,1),he[i.TEXTURE_CUBE_MAP]=ie(i.TEXTURE_CUBE_MAP,i.TEXTURE_CUBE_MAP_POSITIVE_X,6),he[i.TEXTURE_2D_ARRAY]=ie(i.TEXTURE_2D_ARRAY,i.TEXTURE_2D_ARRAY,1,1),he[i.TEXTURE_3D]=ie(i.TEXTURE_3D,i.TEXTURE_3D,1,1),s.setClear(0,0,0,1),r.setClear(1),a.setClear(0),Me(i.DEPTH_TEST),r.setFunc(Ho),ct(!1),Oe(xu),Me(i.CULL_FACE),dt(ls);function Me(I){c[I]!==!0&&(i.enable(I),c[I]=!0)}function fe(I){c[I]!==!1&&(i.disable(I),c[I]=!1)}function ze(I,ae){return h[I]!==ae?(i.bindFramebuffer(I,ae),h[I]=ae,I===i.DRAW_FRAMEBUFFER&&(h[i.FRAMEBUFFER]=ae),I===i.FRAMEBUFFER&&(h[i.DRAW_FRAMEBUFFER]=ae),!0):!1}function Ge(I,ae){let se=d,re=!1;if(I){se=u.get(ae),se===void 0&&(se=[],u.set(ae,se));const ve=I.textures;if(se.length!==ve.length||se[0]!==i.COLOR_ATTACHMENT0){for(let je=0,ot=ve.length;je<ot;je++)se[je]=i.COLOR_ATTACHMENT0+je;se.length=ve.length,re=!0}}else se[0]!==i.BACK&&(se[0]=i.BACK,re=!0);re&&i.drawBuffers(se)}function Fe(I){return f!==I?(i.useProgram(I),f=I,!0):!1}const pt={[Ps]:i.FUNC_ADD,[Pm]:i.FUNC_SUBTRACT,[Lm]:i.FUNC_REVERSE_SUBTRACT};pt[Dm]=i.MIN,pt[Im]=i.MAX;const N={[Um]:i.ZERO,[Nm]:i.ONE,[Fm]:i.SRC_COLOR,[yc]:i.SRC_ALPHA,[Vm]:i.SRC_ALPHA_SATURATE,[km]:i.DST_COLOR,[Bm]:i.DST_ALPHA,[Om]:i.ONE_MINUS_SRC_COLOR,[Mc]:i.ONE_MINUS_SRC_ALPHA,[Hm]:i.ONE_MINUS_DST_COLOR,[zm]:i.ONE_MINUS_DST_ALPHA,[Gm]:i.CONSTANT_COLOR,[Wm]:i.ONE_MINUS_CONSTANT_COLOR,[Xm]:i.CONSTANT_ALPHA,[qm]:i.ONE_MINUS_CONSTANT_ALPHA};function dt(I,ae,se,re,ve,je,ot,_t,wt,lt){if(I===ls){g===!0&&(fe(i.BLEND),g=!1);return}if(g===!1&&(Me(i.BLEND),g=!0),I!==Cm){if(I!==_||lt!==F){if((m!==Ps||y!==Ps)&&(i.blendEquation(i.FUNC_ADD),m=Ps,y=Ps),lt)switch(I){case Cr:i.blendFuncSeparate(i.ONE,i.ONE_MINUS_SRC_ALPHA,i.ONE,i.ONE_MINUS_SRC_ALPHA);break;case yu:i.blendFunc(i.ONE,i.ONE);break;case Mu:i.blendFuncSeparate(i.ZERO,i.ONE_MINUS_SRC_COLOR,i.ZERO,i.ONE);break;case Su:i.blendFuncSeparate(i.ZERO,i.SRC_COLOR,i.ZERO,i.SRC_ALPHA);break;default:console.error("THREE.WebGLState: Invalid blending: ",I);break}else switch(I){case Cr:i.blendFuncSeparate(i.SRC_ALPHA,i.ONE_MINUS_SRC_ALPHA,i.ONE,i.ONE_MINUS_SRC_ALPHA);break;case yu:i.blendFunc(i.SRC_ALPHA,i.ONE);break;case Mu:i.blendFuncSeparate(i.ZERO,i.ONE_MINUS_SRC_COLOR,i.ZERO,i.ONE);break;case Su:i.blendFunc(i.ZERO,i.SRC_COLOR);break;default:console.error("THREE.WebGLState: Invalid blending: ",I);break}p=null,S=null,w=null,O=null,A.set(0,0,0),C=0,_=I,F=lt}return}ve=ve||ae,je=je||se,ot=ot||re,(ae!==m||ve!==y)&&(i.blendEquationSeparate(pt[ae],pt[ve]),m=ae,y=ve),(se!==p||re!==S||je!==w||ot!==O)&&(i.blendFuncSeparate(N[se],N[re],N[je],N[ot]),p=se,S=re,w=je,O=ot),(_t.equals(A)===!1||wt!==C)&&(i.blendColor(_t.r,_t.g,_t.b,wt),A.copy(_t),C=wt),_=I,F=!1}function st(I,ae){I.side===Yn?fe(i.CULL_FACE):Me(i.CULL_FACE);let se=I.side===In;ae&&(se=!se),ct(se),I.blending===Cr&&I.transparent===!1?dt(ls):dt(I.blending,I.blendEquation,I.blendSrc,I.blendDst,I.blendEquationAlpha,I.blendSrcAlpha,I.blendDstAlpha,I.blendColor,I.blendAlpha,I.premultipliedAlpha),r.setFunc(I.depthFunc),r.setTest(I.depthTest),r.setMask(I.depthWrite),s.setMask(I.colorWrite);const re=I.stencilWrite;a.setTest(re),re&&(a.setMask(I.stencilWriteMask),a.setFunc(I.stencilFunc,I.stencilRef,I.stencilFuncMask),a.setOp(I.stencilFail,I.stencilZFail,I.stencilZPass)),$e(I.polygonOffset,I.polygonOffsetFactor,I.polygonOffsetUnits),I.alphaToCoverage===!0?Me(i.SAMPLE_ALPHA_TO_COVERAGE):fe(i.SAMPLE_ALPHA_TO_COVERAGE)}function ct(I){b!==I&&(I?i.frontFace(i.CW):i.frontFace(i.CCW),b=I)}function Oe(I){I!==Am?(Me(i.CULL_FACE),I!==x&&(I===xu?i.cullFace(i.BACK):I===Rm?i.cullFace(i.FRONT):i.cullFace(i.FRONT_AND_BACK))):fe(i.CULL_FACE),x=I}function Et(I){I!==P&&(q&&i.lineWidth(I),P=I)}function $e(I,ae,se){I?(Me(i.POLYGON_OFFSET_FILL),(K!==ae||k!==se)&&(i.polygonOffset(ae,se),K=ae,k=se)):fe(i.POLYGON_OFFSET_FILL)}function Xe(I){I?Me(i.SCISSOR_TEST):fe(i.SCISSOR_TEST)}function D(I){I===void 0&&(I=i.TEXTURE0+Z-1),ne!==I&&(i.activeTexture(I),ne=I)}function E(I,ae,se){se===void 0&&(ne===null?se=i.TEXTURE0+Z-1:se=ne);let re=ge[se];re===void 0&&(re={type:void 0,texture:void 0},ge[se]=re),(re.type!==I||re.texture!==ae)&&(ne!==se&&(i.activeTexture(se),ne=se),i.bindTexture(I,ae||he[I]),re.type=I,re.texture=ae)}function Q(){const I=ge[ne];I!==void 0&&I.type!==void 0&&(i.bindTexture(I.type,null),I.type=void 0,I.texture=void 0)}function le(){try{i.compressedTexImage2D.apply(i,arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function te(){try{i.compressedTexImage3D.apply(i,arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function X(){try{i.texSubImage2D.apply(i,arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function Ee(){try{i.texSubImage3D.apply(i,arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function _e(){try{i.compressedTexSubImage2D.apply(i,arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function Ae(){try{i.compressedTexSubImage3D.apply(i,arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function Ke(){try{i.texStorage2D.apply(i,arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function me(){try{i.texStorage3D.apply(i,arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function Te(){try{i.texImage2D.apply(i,arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function Ze(){try{i.texImage3D.apply(i,arguments)}catch(I){console.error("THREE.WebGLState:",I)}}function ke(I){we.equals(I)===!1&&(i.scissor(I.x,I.y,I.z,I.w),we.copy(I))}function be(I){ye.equals(I)===!1&&(i.viewport(I.x,I.y,I.z,I.w),ye.copy(I))}function He(I,ae){let se=l.get(ae);se===void 0&&(se=new WeakMap,l.set(ae,se));let re=se.get(I);re===void 0&&(re=i.getUniformBlockIndex(ae,I.name),se.set(I,re))}function B(I,ae){const re=l.get(ae).get(I);o.get(ae)!==re&&(i.uniformBlockBinding(ae,re,I.__bindingPointIndex),o.set(ae,re))}function ce(){i.disable(i.BLEND),i.disable(i.CULL_FACE),i.disable(i.DEPTH_TEST),i.disable(i.POLYGON_OFFSET_FILL),i.disable(i.SCISSOR_TEST),i.disable(i.STENCIL_TEST),i.disable(i.SAMPLE_ALPHA_TO_COVERAGE),i.blendEquation(i.FUNC_ADD),i.blendFunc(i.ONE,i.ZERO),i.blendFuncSeparate(i.ONE,i.ZERO,i.ONE,i.ZERO),i.blendColor(0,0,0,0),i.colorMask(!0,!0,!0,!0),i.clearColor(0,0,0,0),i.depthMask(!0),i.depthFunc(i.LESS),i.clearDepth(1),i.stencilMask(4294967295),i.stencilFunc(i.ALWAYS,0,4294967295),i.stencilOp(i.KEEP,i.KEEP,i.KEEP),i.clearStencil(0),i.cullFace(i.BACK),i.frontFace(i.CCW),i.polygonOffset(0,0),i.activeTexture(i.TEXTURE0),i.bindFramebuffer(i.FRAMEBUFFER,null),i.bindFramebuffer(i.DRAW_FRAMEBUFFER,null),i.bindFramebuffer(i.READ_FRAMEBUFFER,null),i.useProgram(null),i.lineWidth(1),i.scissor(0,0,i.canvas.width,i.canvas.height),i.viewport(0,0,i.canvas.width,i.canvas.height),c={},ne=null,ge={},h={},u=new WeakMap,d=[],f=null,g=!1,_=null,m=null,p=null,S=null,y=null,w=null,O=null,A=new nt(0,0,0),C=0,F=!1,b=null,x=null,P=null,K=null,k=null,we.set(0,0,i.canvas.width,i.canvas.height),ye.set(0,0,i.canvas.width,i.canvas.height),s.reset(),r.reset(),a.reset()}return{buffers:{color:s,depth:r,stencil:a},enable:Me,disable:fe,bindFramebuffer:ze,drawBuffers:Ge,useProgram:Fe,setBlending:dt,setMaterial:st,setFlipSided:ct,setCullFace:Oe,setLineWidth:Et,setPolygonOffset:$e,setScissorTest:Xe,activeTexture:D,bindTexture:E,unbindTexture:Q,compressedTexImage2D:le,compressedTexImage3D:te,texImage2D:Te,texImage3D:Ze,updateUBOMapping:He,uniformBlockBinding:B,texStorage2D:Ke,texStorage3D:me,texSubImage2D:X,texSubImage3D:Ee,compressedTexSubImage2D:_e,compressedTexSubImage3D:Ae,scissor:ke,viewport:be,reset:ce}}function pd(i,e,t,n){const s=Iy(n);switch(t){case Uf:return i*e;case Ff:return i*e;case Of:return i*e*2;case Bf:return i*e/s.components*s.byteLength;case vh:return i*e/s.components*s.byteLength;case zf:return i*e*2/s.components*s.byteLength;case xh:return i*e*2/s.components*s.byteLength;case Nf:return i*e*3/s.components*s.byteLength;case ci:return i*e*4/s.components*s.byteLength;case yh:return i*e*4/s.components*s.byteLength;case Do:case Io:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*8;case Uo:case No:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*16;case Ac:case Cc:return Math.max(i,16)*Math.max(e,8)/4;case Tc:case Rc:return Math.max(i,8)*Math.max(e,8)/2;case Pc:case Lc:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*8;case Dc:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*16;case Ic:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*16;case Uc:return Math.floor((i+4)/5)*Math.floor((e+3)/4)*16;case Nc:return Math.floor((i+4)/5)*Math.floor((e+4)/5)*16;case Fc:return Math.floor((i+5)/6)*Math.floor((e+4)/5)*16;case Oc:return Math.floor((i+5)/6)*Math.floor((e+5)/6)*16;case Bc:return Math.floor((i+7)/8)*Math.floor((e+4)/5)*16;case zc:return Math.floor((i+7)/8)*Math.floor((e+5)/6)*16;case kc:return Math.floor((i+7)/8)*Math.floor((e+7)/8)*16;case Hc:return Math.floor((i+9)/10)*Math.floor((e+4)/5)*16;case Vc:return Math.floor((i+9)/10)*Math.floor((e+5)/6)*16;case Gc:return Math.floor((i+9)/10)*Math.floor((e+7)/8)*16;case Wc:return Math.floor((i+9)/10)*Math.floor((e+9)/10)*16;case Xc:return Math.floor((i+11)/12)*Math.floor((e+9)/10)*16;case qc:return Math.floor((i+11)/12)*Math.floor((e+11)/12)*16;case Fo:case $c:case Yc:return Math.ceil(i/4)*Math.ceil(e/4)*16;case kf:case jc:return Math.ceil(i/4)*Math.ceil(e/4)*8;case Kc:case Zc:return Math.ceil(i/4)*Math.ceil(e/4)*16}throw new Error(`Unable to determine texture byte length for ${t} format.`)}function Iy(i){switch(i){case Wi:case Lf:return{byteLength:1,components:1};case Pa:case Df:case Na:return{byteLength:2,components:1};case gh:case _h:return{byteLength:2,components:4};case Bs:case mh:case Oi:return{byteLength:4,components:1};case If:return{byteLength:4,components:3}}throw new Error(`Unknown texture type ${i}.`)}function Uy(i,e,t,n,s,r,a){const o=e.has("WEBGL_multisampled_render_to_texture")?e.get("WEBGL_multisampled_render_to_texture"):null,l=typeof navigator>"u"?!1:/OculusBrowser/g.test(navigator.userAgent),c=new qe,h=new WeakMap;let u;const d=new WeakMap;let f=!1;try{f=typeof OffscreenCanvas<"u"&&new OffscreenCanvas(1,1).getContext("2d")!==null}catch{}function g(D,E){return f?new OffscreenCanvas(D,E):qo("canvas")}function _(D,E,Q){let le=1;const te=Xe(D);if((te.width>Q||te.height>Q)&&(le=Q/Math.max(te.width,te.height)),le<1)if(typeof HTMLImageElement<"u"&&D instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&D instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&D instanceof ImageBitmap||typeof VideoFrame<"u"&&D instanceof VideoFrame){const X=Math.floor(le*te.width),Ee=Math.floor(le*te.height);u===void 0&&(u=g(X,Ee));const _e=E?g(X,Ee):u;return _e.width=X,_e.height=Ee,_e.getContext("2d").drawImage(D,0,0,X,Ee),console.warn("THREE.WebGLRenderer: Texture has been resized from ("+te.width+"x"+te.height+") to ("+X+"x"+Ee+")."),_e}else return"data"in D&&console.warn("THREE.WebGLRenderer: Image in DataTexture is too big ("+te.width+"x"+te.height+")."),D;return D}function m(D){return D.generateMipmaps&&D.minFilter!==Kn&&D.minFilter!==ai}function p(D){i.generateMipmap(D)}function S(D,E,Q,le,te=!1){if(D!==null){if(i[D]!==void 0)return i[D];console.warn("THREE.WebGLRenderer: Attempt to use non-existing WebGL internal format '"+D+"'")}let X=E;if(E===i.RED&&(Q===i.FLOAT&&(X=i.R32F),Q===i.HALF_FLOAT&&(X=i.R16F),Q===i.UNSIGNED_BYTE&&(X=i.R8)),E===i.RED_INTEGER&&(Q===i.UNSIGNED_BYTE&&(X=i.R8UI),Q===i.UNSIGNED_SHORT&&(X=i.R16UI),Q===i.UNSIGNED_INT&&(X=i.R32UI),Q===i.BYTE&&(X=i.R8I),Q===i.SHORT&&(X=i.R16I),Q===i.INT&&(X=i.R32I)),E===i.RG&&(Q===i.FLOAT&&(X=i.RG32F),Q===i.HALF_FLOAT&&(X=i.RG16F),Q===i.UNSIGNED_BYTE&&(X=i.RG8)),E===i.RG_INTEGER&&(Q===i.UNSIGNED_BYTE&&(X=i.RG8UI),Q===i.UNSIGNED_SHORT&&(X=i.RG16UI),Q===i.UNSIGNED_INT&&(X=i.RG32UI),Q===i.BYTE&&(X=i.RG8I),Q===i.SHORT&&(X=i.RG16I),Q===i.INT&&(X=i.RG32I)),E===i.RGB&&Q===i.UNSIGNED_INT_5_9_9_9_REV&&(X=i.RGB9_E5),E===i.RGBA){const Ee=te?Vo:bt.getTransfer(le);Q===i.FLOAT&&(X=i.RGBA32F),Q===i.HALF_FLOAT&&(X=i.RGBA16F),Q===i.UNSIGNED_BYTE&&(X=Ee===Ot?i.SRGB8_ALPHA8:i.RGBA8),Q===i.UNSIGNED_SHORT_4_4_4_4&&(X=i.RGBA4),Q===i.UNSIGNED_SHORT_5_5_5_1&&(X=i.RGB5_A1)}return(X===i.R16F||X===i.R32F||X===i.RG16F||X===i.RG32F||X===i.RGBA16F||X===i.RGBA32F)&&e.get("EXT_color_buffer_float"),X}function y(D,E){let Q;return D?E===null||E===Bs||E===kr?Q=i.DEPTH24_STENCIL8:E===Oi?Q=i.DEPTH32F_STENCIL8:E===Pa&&(Q=i.DEPTH24_STENCIL8,console.warn("DepthTexture: 16 bit depth attachment is not supported with stencil. Using 24-bit attachment.")):E===null||E===Bs||E===kr?Q=i.DEPTH_COMPONENT24:E===Oi?Q=i.DEPTH_COMPONENT32F:E===Pa&&(Q=i.DEPTH_COMPONENT16),Q}function w(D,E){return m(D)===!0||D.isFramebufferTexture&&D.minFilter!==Kn&&D.minFilter!==ai?Math.log2(Math.max(E.width,E.height))+1:D.mipmaps!==void 0&&D.mipmaps.length>0?D.mipmaps.length:D.isCompressedTexture&&Array.isArray(D.image)?E.mipmaps.length:1}function O(D){const E=D.target;E.removeEventListener("dispose",O),C(E),E.isVideoTexture&&h.delete(E)}function A(D){const E=D.target;E.removeEventListener("dispose",A),b(E)}function C(D){const E=n.get(D);if(E.__webglInit===void 0)return;const Q=D.source,le=d.get(Q);if(le){const te=le[E.__cacheKey];te.usedTimes--,te.usedTimes===0&&F(D),Object.keys(le).length===0&&d.delete(Q)}n.remove(D)}function F(D){const E=n.get(D);i.deleteTexture(E.__webglTexture);const Q=D.source,le=d.get(Q);delete le[E.__cacheKey],a.memory.textures--}function b(D){const E=n.get(D);if(D.depthTexture&&D.depthTexture.dispose(),D.isWebGLCubeRenderTarget)for(let le=0;le<6;le++){if(Array.isArray(E.__webglFramebuffer[le]))for(let te=0;te<E.__webglFramebuffer[le].length;te++)i.deleteFramebuffer(E.__webglFramebuffer[le][te]);else i.deleteFramebuffer(E.__webglFramebuffer[le]);E.__webglDepthbuffer&&i.deleteRenderbuffer(E.__webglDepthbuffer[le])}else{if(Array.isArray(E.__webglFramebuffer))for(let le=0;le<E.__webglFramebuffer.length;le++)i.deleteFramebuffer(E.__webglFramebuffer[le]);else i.deleteFramebuffer(E.__webglFramebuffer);if(E.__webglDepthbuffer&&i.deleteRenderbuffer(E.__webglDepthbuffer),E.__webglMultisampledFramebuffer&&i.deleteFramebuffer(E.__webglMultisampledFramebuffer),E.__webglColorRenderbuffer)for(let le=0;le<E.__webglColorRenderbuffer.length;le++)E.__webglColorRenderbuffer[le]&&i.deleteRenderbuffer(E.__webglColorRenderbuffer[le]);E.__webglDepthRenderbuffer&&i.deleteRenderbuffer(E.__webglDepthRenderbuffer)}const Q=D.textures;for(let le=0,te=Q.length;le<te;le++){const X=n.get(Q[le]);X.__webglTexture&&(i.deleteTexture(X.__webglTexture),a.memory.textures--),n.remove(Q[le])}n.remove(D)}let x=0;function P(){x=0}function K(){const D=x;return D>=s.maxTextures&&console.warn("THREE.WebGLTextures: Trying to use "+D+" texture units while this GPU supports only "+s.maxTextures),x+=1,D}function k(D){const E=[];return E.push(D.wrapS),E.push(D.wrapT),E.push(D.wrapR||0),E.push(D.magFilter),E.push(D.minFilter),E.push(D.anisotropy),E.push(D.internalFormat),E.push(D.format),E.push(D.type),E.push(D.generateMipmaps),E.push(D.premultiplyAlpha),E.push(D.flipY),E.push(D.unpackAlignment),E.push(D.colorSpace),E.join()}function Z(D,E){const Q=n.get(D);if(D.isVideoTexture&&Et(D),D.isRenderTargetTexture===!1&&D.version>0&&Q.__version!==D.version){const le=D.image;if(le===null)console.warn("THREE.WebGLRenderer: Texture marked for update but no image data found.");else if(le.complete===!1)console.warn("THREE.WebGLRenderer: Texture marked for update but image is incomplete");else{ye(Q,D,E);return}}t.bindTexture(i.TEXTURE_2D,Q.__webglTexture,i.TEXTURE0+E)}function q(D,E){const Q=n.get(D);if(D.version>0&&Q.__version!==D.version){ye(Q,D,E);return}t.bindTexture(i.TEXTURE_2D_ARRAY,Q.__webglTexture,i.TEXTURE0+E)}function ee(D,E){const Q=n.get(D);if(D.version>0&&Q.__version!==D.version){ye(Q,D,E);return}t.bindTexture(i.TEXTURE_3D,Q.__webglTexture,i.TEXTURE0+E)}function Y(D,E){const Q=n.get(D);if(D.version>0&&Q.__version!==D.version){ie(Q,D,E);return}t.bindTexture(i.TEXTURE_CUBE_MAP,Q.__webglTexture,i.TEXTURE0+E)}const ne={[Ec]:i.REPEAT,[Is]:i.CLAMP_TO_EDGE,[wc]:i.MIRRORED_REPEAT},ge={[Kn]:i.NEAREST,[lg]:i.NEAREST_MIPMAP_NEAREST,[Ya]:i.NEAREST_MIPMAP_LINEAR,[ai]:i.LINEAR,[Il]:i.LINEAR_MIPMAP_NEAREST,[Us]:i.LINEAR_MIPMAP_LINEAR},de={[dg]:i.NEVER,[vg]:i.ALWAYS,[fg]:i.LESS,[Vf]:i.LEQUAL,[pg]:i.EQUAL,[_g]:i.GEQUAL,[mg]:i.GREATER,[gg]:i.NOTEQUAL};function xe(D,E){if(E.type===Oi&&e.has("OES_texture_float_linear")===!1&&(E.magFilter===ai||E.magFilter===Il||E.magFilter===Ya||E.magFilter===Us||E.minFilter===ai||E.minFilter===Il||E.minFilter===Ya||E.minFilter===Us)&&console.warn("THREE.WebGLRenderer: Unable to use linear filtering with floating point textures. OES_texture_float_linear not supported on this device."),i.texParameteri(D,i.TEXTURE_WRAP_S,ne[E.wrapS]),i.texParameteri(D,i.TEXTURE_WRAP_T,ne[E.wrapT]),(D===i.TEXTURE_3D||D===i.TEXTURE_2D_ARRAY)&&i.texParameteri(D,i.TEXTURE_WRAP_R,ne[E.wrapR]),i.texParameteri(D,i.TEXTURE_MAG_FILTER,ge[E.magFilter]),i.texParameteri(D,i.TEXTURE_MIN_FILTER,ge[E.minFilter]),E.compareFunction&&(i.texParameteri(D,i.TEXTURE_COMPARE_MODE,i.COMPARE_REF_TO_TEXTURE),i.texParameteri(D,i.TEXTURE_COMPARE_FUNC,de[E.compareFunction])),e.has("EXT_texture_filter_anisotropic")===!0){if(E.magFilter===Kn||E.minFilter!==Ya&&E.minFilter!==Us||E.type===Oi&&e.has("OES_texture_float_linear")===!1)return;if(E.anisotropy>1||n.get(E).__currentAnisotropy){const Q=e.get("EXT_texture_filter_anisotropic");i.texParameterf(D,Q.TEXTURE_MAX_ANISOTROPY_EXT,Math.min(E.anisotropy,s.getMaxAnisotropy())),n.get(E).__currentAnisotropy=E.anisotropy}}}function we(D,E){let Q=!1;D.__webglInit===void 0&&(D.__webglInit=!0,E.addEventListener("dispose",O));const le=E.source;let te=d.get(le);te===void 0&&(te={},d.set(le,te));const X=k(E);if(X!==D.__cacheKey){te[X]===void 0&&(te[X]={texture:i.createTexture(),usedTimes:0},a.memory.textures++,Q=!0),te[X].usedTimes++;const Ee=te[D.__cacheKey];Ee!==void 0&&(te[D.__cacheKey].usedTimes--,Ee.usedTimes===0&&F(E)),D.__cacheKey=X,D.__webglTexture=te[X].texture}return Q}function ye(D,E,Q){let le=i.TEXTURE_2D;(E.isDataArrayTexture||E.isCompressedArrayTexture)&&(le=i.TEXTURE_2D_ARRAY),E.isData3DTexture&&(le=i.TEXTURE_3D);const te=we(D,E),X=E.source;t.bindTexture(le,D.__webglTexture,i.TEXTURE0+Q);const Ee=n.get(X);if(X.version!==Ee.__version||te===!0){t.activeTexture(i.TEXTURE0+Q);const _e=bt.getPrimaries(bt.workingColorSpace),Ae=E.colorSpace===as?null:bt.getPrimaries(E.colorSpace),Ke=E.colorSpace===as||_e===Ae?i.NONE:i.BROWSER_DEFAULT_WEBGL;i.pixelStorei(i.UNPACK_FLIP_Y_WEBGL,E.flipY),i.pixelStorei(i.UNPACK_PREMULTIPLY_ALPHA_WEBGL,E.premultiplyAlpha),i.pixelStorei(i.UNPACK_ALIGNMENT,E.unpackAlignment),i.pixelStorei(i.UNPACK_COLORSPACE_CONVERSION_WEBGL,Ke);let me=_(E.image,!1,s.maxTextureSize);me=$e(E,me);const Te=r.convert(E.format,E.colorSpace),Ze=r.convert(E.type);let ke=S(E.internalFormat,Te,Ze,E.colorSpace,E.isVideoTexture);xe(le,E);let be;const He=E.mipmaps,B=E.isVideoTexture!==!0,ce=Ee.__version===void 0||te===!0,I=X.dataReady,ae=w(E,me);if(E.isDepthTexture)ke=y(E.format===Hr,E.type),ce&&(B?t.texStorage2D(i.TEXTURE_2D,1,ke,me.width,me.height):t.texImage2D(i.TEXTURE_2D,0,ke,me.width,me.height,0,Te,Ze,null));else if(E.isDataTexture)if(He.length>0){B&&ce&&t.texStorage2D(i.TEXTURE_2D,ae,ke,He[0].width,He[0].height);for(let se=0,re=He.length;se<re;se++)be=He[se],B?I&&t.texSubImage2D(i.TEXTURE_2D,se,0,0,be.width,be.height,Te,Ze,be.data):t.texImage2D(i.TEXTURE_2D,se,ke,be.width,be.height,0,Te,Ze,be.data);E.generateMipmaps=!1}else B?(ce&&t.texStorage2D(i.TEXTURE_2D,ae,ke,me.width,me.height),I&&t.texSubImage2D(i.TEXTURE_2D,0,0,0,me.width,me.height,Te,Ze,me.data)):t.texImage2D(i.TEXTURE_2D,0,ke,me.width,me.height,0,Te,Ze,me.data);else if(E.isCompressedTexture)if(E.isCompressedArrayTexture){B&&ce&&t.texStorage3D(i.TEXTURE_2D_ARRAY,ae,ke,He[0].width,He[0].height,me.depth);for(let se=0,re=He.length;se<re;se++)if(be=He[se],E.format!==ci)if(Te!==null)if(B){if(I)if(E.layerUpdates.size>0){const ve=pd(be.width,be.height,E.format,E.type);for(const je of E.layerUpdates){const ot=be.data.subarray(je*ve/be.data.BYTES_PER_ELEMENT,(je+1)*ve/be.data.BYTES_PER_ELEMENT);t.compressedTexSubImage3D(i.TEXTURE_2D_ARRAY,se,0,0,je,be.width,be.height,1,Te,ot,0,0)}E.clearLayerUpdates()}else t.compressedTexSubImage3D(i.TEXTURE_2D_ARRAY,se,0,0,0,be.width,be.height,me.depth,Te,be.data,0,0)}else t.compressedTexImage3D(i.TEXTURE_2D_ARRAY,se,ke,be.width,be.height,me.depth,0,be.data,0,0);else console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()");else B?I&&t.texSubImage3D(i.TEXTURE_2D_ARRAY,se,0,0,0,be.width,be.height,me.depth,Te,Ze,be.data):t.texImage3D(i.TEXTURE_2D_ARRAY,se,ke,be.width,be.height,me.depth,0,Te,Ze,be.data)}else{B&&ce&&t.texStorage2D(i.TEXTURE_2D,ae,ke,He[0].width,He[0].height);for(let se=0,re=He.length;se<re;se++)be=He[se],E.format!==ci?Te!==null?B?I&&t.compressedTexSubImage2D(i.TEXTURE_2D,se,0,0,be.width,be.height,Te,be.data):t.compressedTexImage2D(i.TEXTURE_2D,se,ke,be.width,be.height,0,be.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()"):B?I&&t.texSubImage2D(i.TEXTURE_2D,se,0,0,be.width,be.height,Te,Ze,be.data):t.texImage2D(i.TEXTURE_2D,se,ke,be.width,be.height,0,Te,Ze,be.data)}else if(E.isDataArrayTexture)if(B){if(ce&&t.texStorage3D(i.TEXTURE_2D_ARRAY,ae,ke,me.width,me.height,me.depth),I)if(E.layerUpdates.size>0){const se=pd(me.width,me.height,E.format,E.type);for(const re of E.layerUpdates){const ve=me.data.subarray(re*se/me.data.BYTES_PER_ELEMENT,(re+1)*se/me.data.BYTES_PER_ELEMENT);t.texSubImage3D(i.TEXTURE_2D_ARRAY,0,0,0,re,me.width,me.height,1,Te,Ze,ve)}E.clearLayerUpdates()}else t.texSubImage3D(i.TEXTURE_2D_ARRAY,0,0,0,0,me.width,me.height,me.depth,Te,Ze,me.data)}else t.texImage3D(i.TEXTURE_2D_ARRAY,0,ke,me.width,me.height,me.depth,0,Te,Ze,me.data);else if(E.isData3DTexture)B?(ce&&t.texStorage3D(i.TEXTURE_3D,ae,ke,me.width,me.height,me.depth),I&&t.texSubImage3D(i.TEXTURE_3D,0,0,0,0,me.width,me.height,me.depth,Te,Ze,me.data)):t.texImage3D(i.TEXTURE_3D,0,ke,me.width,me.height,me.depth,0,Te,Ze,me.data);else if(E.isFramebufferTexture){if(ce)if(B)t.texStorage2D(i.TEXTURE_2D,ae,ke,me.width,me.height);else{let se=me.width,re=me.height;for(let ve=0;ve<ae;ve++)t.texImage2D(i.TEXTURE_2D,ve,ke,se,re,0,Te,Ze,null),se>>=1,re>>=1}}else if(He.length>0){if(B&&ce){const se=Xe(He[0]);t.texStorage2D(i.TEXTURE_2D,ae,ke,se.width,se.height)}for(let se=0,re=He.length;se<re;se++)be=He[se],B?I&&t.texSubImage2D(i.TEXTURE_2D,se,0,0,Te,Ze,be):t.texImage2D(i.TEXTURE_2D,se,ke,Te,Ze,be);E.generateMipmaps=!1}else if(B){if(ce){const se=Xe(me);t.texStorage2D(i.TEXTURE_2D,ae,ke,se.width,se.height)}I&&t.texSubImage2D(i.TEXTURE_2D,0,0,0,Te,Ze,me)}else t.texImage2D(i.TEXTURE_2D,0,ke,Te,Ze,me);m(E)&&p(le),Ee.__version=X.version,E.onUpdate&&E.onUpdate(E)}D.__version=E.version}function ie(D,E,Q){if(E.image.length!==6)return;const le=we(D,E),te=E.source;t.bindTexture(i.TEXTURE_CUBE_MAP,D.__webglTexture,i.TEXTURE0+Q);const X=n.get(te);if(te.version!==X.__version||le===!0){t.activeTexture(i.TEXTURE0+Q);const Ee=bt.getPrimaries(bt.workingColorSpace),_e=E.colorSpace===as?null:bt.getPrimaries(E.colorSpace),Ae=E.colorSpace===as||Ee===_e?i.NONE:i.BROWSER_DEFAULT_WEBGL;i.pixelStorei(i.UNPACK_FLIP_Y_WEBGL,E.flipY),i.pixelStorei(i.UNPACK_PREMULTIPLY_ALPHA_WEBGL,E.premultiplyAlpha),i.pixelStorei(i.UNPACK_ALIGNMENT,E.unpackAlignment),i.pixelStorei(i.UNPACK_COLORSPACE_CONVERSION_WEBGL,Ae);const Ke=E.isCompressedTexture||E.image[0].isCompressedTexture,me=E.image[0]&&E.image[0].isDataTexture,Te=[];for(let re=0;re<6;re++)!Ke&&!me?Te[re]=_(E.image[re],!0,s.maxCubemapSize):Te[re]=me?E.image[re].image:E.image[re],Te[re]=$e(E,Te[re]);const Ze=Te[0],ke=r.convert(E.format,E.colorSpace),be=r.convert(E.type),He=S(E.internalFormat,ke,be,E.colorSpace),B=E.isVideoTexture!==!0,ce=X.__version===void 0||le===!0,I=te.dataReady;let ae=w(E,Ze);xe(i.TEXTURE_CUBE_MAP,E);let se;if(Ke){B&&ce&&t.texStorage2D(i.TEXTURE_CUBE_MAP,ae,He,Ze.width,Ze.height);for(let re=0;re<6;re++){se=Te[re].mipmaps;for(let ve=0;ve<se.length;ve++){const je=se[ve];E.format!==ci?ke!==null?B?I&&t.compressedTexSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,ve,0,0,je.width,je.height,ke,je.data):t.compressedTexImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,ve,He,je.width,je.height,0,je.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .setTextureCube()"):B?I&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,ve,0,0,je.width,je.height,ke,be,je.data):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,ve,He,je.width,je.height,0,ke,be,je.data)}}}else{if(se=E.mipmaps,B&&ce){se.length>0&&ae++;const re=Xe(Te[0]);t.texStorage2D(i.TEXTURE_CUBE_MAP,ae,He,re.width,re.height)}for(let re=0;re<6;re++)if(me){B?I&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,0,0,0,Te[re].width,Te[re].height,ke,be,Te[re].data):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,0,He,Te[re].width,Te[re].height,0,ke,be,Te[re].data);for(let ve=0;ve<se.length;ve++){const ot=se[ve].image[re].image;B?I&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,ve+1,0,0,ot.width,ot.height,ke,be,ot.data):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,ve+1,He,ot.width,ot.height,0,ke,be,ot.data)}}else{B?I&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,0,0,0,ke,be,Te[re]):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,0,He,ke,be,Te[re]);for(let ve=0;ve<se.length;ve++){const je=se[ve];B?I&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,ve+1,0,0,ke,be,je.image[re]):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,ve+1,He,ke,be,je.image[re])}}}m(E)&&p(i.TEXTURE_CUBE_MAP),X.__version=te.version,E.onUpdate&&E.onUpdate(E)}D.__version=E.version}function he(D,E,Q,le,te,X){const Ee=r.convert(Q.format,Q.colorSpace),_e=r.convert(Q.type),Ae=S(Q.internalFormat,Ee,_e,Q.colorSpace);if(!n.get(E).__hasExternalTextures){const me=Math.max(1,E.width>>X),Te=Math.max(1,E.height>>X);te===i.TEXTURE_3D||te===i.TEXTURE_2D_ARRAY?t.texImage3D(te,X,Ae,me,Te,E.depth,0,Ee,_e,null):t.texImage2D(te,X,Ae,me,Te,0,Ee,_e,null)}t.bindFramebuffer(i.FRAMEBUFFER,D),Oe(E)?o.framebufferTexture2DMultisampleEXT(i.FRAMEBUFFER,le,te,n.get(Q).__webglTexture,0,ct(E)):(te===i.TEXTURE_2D||te>=i.TEXTURE_CUBE_MAP_POSITIVE_X&&te<=i.TEXTURE_CUBE_MAP_NEGATIVE_Z)&&i.framebufferTexture2D(i.FRAMEBUFFER,le,te,n.get(Q).__webglTexture,X),t.bindFramebuffer(i.FRAMEBUFFER,null)}function Me(D,E,Q){if(i.bindRenderbuffer(i.RENDERBUFFER,D),E.depthBuffer){const le=E.depthTexture,te=le&&le.isDepthTexture?le.type:null,X=y(E.stencilBuffer,te),Ee=E.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,_e=ct(E);Oe(E)?o.renderbufferStorageMultisampleEXT(i.RENDERBUFFER,_e,X,E.width,E.height):Q?i.renderbufferStorageMultisample(i.RENDERBUFFER,_e,X,E.width,E.height):i.renderbufferStorage(i.RENDERBUFFER,X,E.width,E.height),i.framebufferRenderbuffer(i.FRAMEBUFFER,Ee,i.RENDERBUFFER,D)}else{const le=E.textures;for(let te=0;te<le.length;te++){const X=le[te],Ee=r.convert(X.format,X.colorSpace),_e=r.convert(X.type),Ae=S(X.internalFormat,Ee,_e,X.colorSpace),Ke=ct(E);Q&&Oe(E)===!1?i.renderbufferStorageMultisample(i.RENDERBUFFER,Ke,Ae,E.width,E.height):Oe(E)?o.renderbufferStorageMultisampleEXT(i.RENDERBUFFER,Ke,Ae,E.width,E.height):i.renderbufferStorage(i.RENDERBUFFER,Ae,E.width,E.height)}}i.bindRenderbuffer(i.RENDERBUFFER,null)}function fe(D,E){if(E&&E.isWebGLCubeRenderTarget)throw new Error("Depth Texture with cube render targets is not supported");if(t.bindFramebuffer(i.FRAMEBUFFER,D),!(E.depthTexture&&E.depthTexture.isDepthTexture))throw new Error("renderTarget.depthTexture must be an instance of THREE.DepthTexture");(!n.get(E.depthTexture).__webglTexture||E.depthTexture.image.width!==E.width||E.depthTexture.image.height!==E.height)&&(E.depthTexture.image.width=E.width,E.depthTexture.image.height=E.height,E.depthTexture.needsUpdate=!0),Z(E.depthTexture,0);const le=n.get(E.depthTexture).__webglTexture,te=ct(E);if(E.depthTexture.format===Pr)Oe(E)?o.framebufferTexture2DMultisampleEXT(i.FRAMEBUFFER,i.DEPTH_ATTACHMENT,i.TEXTURE_2D,le,0,te):i.framebufferTexture2D(i.FRAMEBUFFER,i.DEPTH_ATTACHMENT,i.TEXTURE_2D,le,0);else if(E.depthTexture.format===Hr)Oe(E)?o.framebufferTexture2DMultisampleEXT(i.FRAMEBUFFER,i.DEPTH_STENCIL_ATTACHMENT,i.TEXTURE_2D,le,0,te):i.framebufferTexture2D(i.FRAMEBUFFER,i.DEPTH_STENCIL_ATTACHMENT,i.TEXTURE_2D,le,0);else throw new Error("Unknown depthTexture format")}function ze(D){const E=n.get(D),Q=D.isWebGLCubeRenderTarget===!0;if(E.__boundDepthTexture!==D.depthTexture){const le=D.depthTexture;if(E.__depthDisposeCallback&&E.__depthDisposeCallback(),le){const te=()=>{delete E.__boundDepthTexture,delete E.__depthDisposeCallback,le.removeEventListener("dispose",te)};le.addEventListener("dispose",te),E.__depthDisposeCallback=te}E.__boundDepthTexture=le}if(D.depthTexture&&!E.__autoAllocateDepthBuffer){if(Q)throw new Error("target.depthTexture not supported in Cube render targets");fe(E.__webglFramebuffer,D)}else if(Q){E.__webglDepthbuffer=[];for(let le=0;le<6;le++)if(t.bindFramebuffer(i.FRAMEBUFFER,E.__webglFramebuffer[le]),E.__webglDepthbuffer[le]===void 0)E.__webglDepthbuffer[le]=i.createRenderbuffer(),Me(E.__webglDepthbuffer[le],D,!1);else{const te=D.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,X=E.__webglDepthbuffer[le];i.bindRenderbuffer(i.RENDERBUFFER,X),i.framebufferRenderbuffer(i.FRAMEBUFFER,te,i.RENDERBUFFER,X)}}else if(t.bindFramebuffer(i.FRAMEBUFFER,E.__webglFramebuffer),E.__webglDepthbuffer===void 0)E.__webglDepthbuffer=i.createRenderbuffer(),Me(E.__webglDepthbuffer,D,!1);else{const le=D.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,te=E.__webglDepthbuffer;i.bindRenderbuffer(i.RENDERBUFFER,te),i.framebufferRenderbuffer(i.FRAMEBUFFER,le,i.RENDERBUFFER,te)}t.bindFramebuffer(i.FRAMEBUFFER,null)}function Ge(D,E,Q){const le=n.get(D);E!==void 0&&he(le.__webglFramebuffer,D,D.texture,i.COLOR_ATTACHMENT0,i.TEXTURE_2D,0),Q!==void 0&&ze(D)}function Fe(D){const E=D.texture,Q=n.get(D),le=n.get(E);D.addEventListener("dispose",A);const te=D.textures,X=D.isWebGLCubeRenderTarget===!0,Ee=te.length>1;if(Ee||(le.__webglTexture===void 0&&(le.__webglTexture=i.createTexture()),le.__version=E.version,a.memory.textures++),X){Q.__webglFramebuffer=[];for(let _e=0;_e<6;_e++)if(E.mipmaps&&E.mipmaps.length>0){Q.__webglFramebuffer[_e]=[];for(let Ae=0;Ae<E.mipmaps.length;Ae++)Q.__webglFramebuffer[_e][Ae]=i.createFramebuffer()}else Q.__webglFramebuffer[_e]=i.createFramebuffer()}else{if(E.mipmaps&&E.mipmaps.length>0){Q.__webglFramebuffer=[];for(let _e=0;_e<E.mipmaps.length;_e++)Q.__webglFramebuffer[_e]=i.createFramebuffer()}else Q.__webglFramebuffer=i.createFramebuffer();if(Ee)for(let _e=0,Ae=te.length;_e<Ae;_e++){const Ke=n.get(te[_e]);Ke.__webglTexture===void 0&&(Ke.__webglTexture=i.createTexture(),a.memory.textures++)}if(D.samples>0&&Oe(D)===!1){Q.__webglMultisampledFramebuffer=i.createFramebuffer(),Q.__webglColorRenderbuffer=[],t.bindFramebuffer(i.FRAMEBUFFER,Q.__webglMultisampledFramebuffer);for(let _e=0;_e<te.length;_e++){const Ae=te[_e];Q.__webglColorRenderbuffer[_e]=i.createRenderbuffer(),i.bindRenderbuffer(i.RENDERBUFFER,Q.__webglColorRenderbuffer[_e]);const Ke=r.convert(Ae.format,Ae.colorSpace),me=r.convert(Ae.type),Te=S(Ae.internalFormat,Ke,me,Ae.colorSpace,D.isXRRenderTarget===!0),Ze=ct(D);i.renderbufferStorageMultisample(i.RENDERBUFFER,Ze,Te,D.width,D.height),i.framebufferRenderbuffer(i.FRAMEBUFFER,i.COLOR_ATTACHMENT0+_e,i.RENDERBUFFER,Q.__webglColorRenderbuffer[_e])}i.bindRenderbuffer(i.RENDERBUFFER,null),D.depthBuffer&&(Q.__webglDepthRenderbuffer=i.createRenderbuffer(),Me(Q.__webglDepthRenderbuffer,D,!0)),t.bindFramebuffer(i.FRAMEBUFFER,null)}}if(X){t.bindTexture(i.TEXTURE_CUBE_MAP,le.__webglTexture),xe(i.TEXTURE_CUBE_MAP,E);for(let _e=0;_e<6;_e++)if(E.mipmaps&&E.mipmaps.length>0)for(let Ae=0;Ae<E.mipmaps.length;Ae++)he(Q.__webglFramebuffer[_e][Ae],D,E,i.COLOR_ATTACHMENT0,i.TEXTURE_CUBE_MAP_POSITIVE_X+_e,Ae);else he(Q.__webglFramebuffer[_e],D,E,i.COLOR_ATTACHMENT0,i.TEXTURE_CUBE_MAP_POSITIVE_X+_e,0);m(E)&&p(i.TEXTURE_CUBE_MAP),t.unbindTexture()}else if(Ee){for(let _e=0,Ae=te.length;_e<Ae;_e++){const Ke=te[_e],me=n.get(Ke);t.bindTexture(i.TEXTURE_2D,me.__webglTexture),xe(i.TEXTURE_2D,Ke),he(Q.__webglFramebuffer,D,Ke,i.COLOR_ATTACHMENT0+_e,i.TEXTURE_2D,0),m(Ke)&&p(i.TEXTURE_2D)}t.unbindTexture()}else{let _e=i.TEXTURE_2D;if((D.isWebGL3DRenderTarget||D.isWebGLArrayRenderTarget)&&(_e=D.isWebGL3DRenderTarget?i.TEXTURE_3D:i.TEXTURE_2D_ARRAY),t.bindTexture(_e,le.__webglTexture),xe(_e,E),E.mipmaps&&E.mipmaps.length>0)for(let Ae=0;Ae<E.mipmaps.length;Ae++)he(Q.__webglFramebuffer[Ae],D,E,i.COLOR_ATTACHMENT0,_e,Ae);else he(Q.__webglFramebuffer,D,E,i.COLOR_ATTACHMENT0,_e,0);m(E)&&p(_e),t.unbindTexture()}D.depthBuffer&&ze(D)}function pt(D){const E=D.textures;for(let Q=0,le=E.length;Q<le;Q++){const te=E[Q];if(m(te)){const X=D.isWebGLCubeRenderTarget?i.TEXTURE_CUBE_MAP:i.TEXTURE_2D,Ee=n.get(te).__webglTexture;t.bindTexture(X,Ee),p(X),t.unbindTexture()}}}const N=[],dt=[];function st(D){if(D.samples>0){if(Oe(D)===!1){const E=D.textures,Q=D.width,le=D.height;let te=i.COLOR_BUFFER_BIT;const X=D.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,Ee=n.get(D),_e=E.length>1;if(_e)for(let Ae=0;Ae<E.length;Ae++)t.bindFramebuffer(i.FRAMEBUFFER,Ee.__webglMultisampledFramebuffer),i.framebufferRenderbuffer(i.FRAMEBUFFER,i.COLOR_ATTACHMENT0+Ae,i.RENDERBUFFER,null),t.bindFramebuffer(i.FRAMEBUFFER,Ee.__webglFramebuffer),i.framebufferTexture2D(i.DRAW_FRAMEBUFFER,i.COLOR_ATTACHMENT0+Ae,i.TEXTURE_2D,null,0);t.bindFramebuffer(i.READ_FRAMEBUFFER,Ee.__webglMultisampledFramebuffer),t.bindFramebuffer(i.DRAW_FRAMEBUFFER,Ee.__webglFramebuffer);for(let Ae=0;Ae<E.length;Ae++){if(D.resolveDepthBuffer&&(D.depthBuffer&&(te|=i.DEPTH_BUFFER_BIT),D.stencilBuffer&&D.resolveStencilBuffer&&(te|=i.STENCIL_BUFFER_BIT)),_e){i.framebufferRenderbuffer(i.READ_FRAMEBUFFER,i.COLOR_ATTACHMENT0,i.RENDERBUFFER,Ee.__webglColorRenderbuffer[Ae]);const Ke=n.get(E[Ae]).__webglTexture;i.framebufferTexture2D(i.DRAW_FRAMEBUFFER,i.COLOR_ATTACHMENT0,i.TEXTURE_2D,Ke,0)}i.blitFramebuffer(0,0,Q,le,0,0,Q,le,te,i.NEAREST),l===!0&&(N.length=0,dt.length=0,N.push(i.COLOR_ATTACHMENT0+Ae),D.depthBuffer&&D.resolveDepthBuffer===!1&&(N.push(X),dt.push(X),i.invalidateFramebuffer(i.DRAW_FRAMEBUFFER,dt)),i.invalidateFramebuffer(i.READ_FRAMEBUFFER,N))}if(t.bindFramebuffer(i.READ_FRAMEBUFFER,null),t.bindFramebuffer(i.DRAW_FRAMEBUFFER,null),_e)for(let Ae=0;Ae<E.length;Ae++){t.bindFramebuffer(i.FRAMEBUFFER,Ee.__webglMultisampledFramebuffer),i.framebufferRenderbuffer(i.FRAMEBUFFER,i.COLOR_ATTACHMENT0+Ae,i.RENDERBUFFER,Ee.__webglColorRenderbuffer[Ae]);const Ke=n.get(E[Ae]).__webglTexture;t.bindFramebuffer(i.FRAMEBUFFER,Ee.__webglFramebuffer),i.framebufferTexture2D(i.DRAW_FRAMEBUFFER,i.COLOR_ATTACHMENT0+Ae,i.TEXTURE_2D,Ke,0)}t.bindFramebuffer(i.DRAW_FRAMEBUFFER,Ee.__webglMultisampledFramebuffer)}else if(D.depthBuffer&&D.resolveDepthBuffer===!1&&l){const E=D.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT;i.invalidateFramebuffer(i.DRAW_FRAMEBUFFER,[E])}}}function ct(D){return Math.min(s.maxSamples,D.samples)}function Oe(D){const E=n.get(D);return D.samples>0&&e.has("WEBGL_multisampled_render_to_texture")===!0&&E.__useRenderToTexture!==!1}function Et(D){const E=a.render.frame;h.get(D)!==E&&(h.set(D,E),D.update())}function $e(D,E){const Q=D.colorSpace,le=D.format,te=D.type;return D.isCompressedTexture===!0||D.isVideoTexture===!0||Q!==ps&&Q!==as&&(bt.getTransfer(Q)===Ot?(le!==ci||te!==Wi)&&console.warn("THREE.WebGLTextures: sRGB encoded textures have to use RGBAFormat and UnsignedByteType."):console.error("THREE.WebGLTextures: Unsupported texture color space:",Q)),E}function Xe(D){return typeof HTMLImageElement<"u"&&D instanceof HTMLImageElement?(c.width=D.naturalWidth||D.width,c.height=D.naturalHeight||D.height):typeof VideoFrame<"u"&&D instanceof VideoFrame?(c.width=D.displayWidth,c.height=D.displayHeight):(c.width=D.width,c.height=D.height),c}this.allocateTextureUnit=K,this.resetTextureUnits=P,this.setTexture2D=Z,this.setTexture2DArray=q,this.setTexture3D=ee,this.setTextureCube=Y,this.rebindTextures=Ge,this.setupRenderTarget=Fe,this.updateRenderTargetMipmap=pt,this.updateMultisampleRenderTarget=st,this.setupDepthRenderbuffer=ze,this.setupFrameBufferTexture=he,this.useMultisampledRTT=Oe}function Ny(i,e){function t(n,s=as){let r;const a=bt.getTransfer(s);if(n===Wi)return i.UNSIGNED_BYTE;if(n===gh)return i.UNSIGNED_SHORT_4_4_4_4;if(n===_h)return i.UNSIGNED_SHORT_5_5_5_1;if(n===If)return i.UNSIGNED_INT_5_9_9_9_REV;if(n===Lf)return i.BYTE;if(n===Df)return i.SHORT;if(n===Pa)return i.UNSIGNED_SHORT;if(n===mh)return i.INT;if(n===Bs)return i.UNSIGNED_INT;if(n===Oi)return i.FLOAT;if(n===Na)return i.HALF_FLOAT;if(n===Uf)return i.ALPHA;if(n===Nf)return i.RGB;if(n===ci)return i.RGBA;if(n===Ff)return i.LUMINANCE;if(n===Of)return i.LUMINANCE_ALPHA;if(n===Pr)return i.DEPTH_COMPONENT;if(n===Hr)return i.DEPTH_STENCIL;if(n===Bf)return i.RED;if(n===vh)return i.RED_INTEGER;if(n===zf)return i.RG;if(n===xh)return i.RG_INTEGER;if(n===yh)return i.RGBA_INTEGER;if(n===Do||n===Io||n===Uo||n===No)if(a===Ot)if(r=e.get("WEBGL_compressed_texture_s3tc_srgb"),r!==null){if(n===Do)return r.COMPRESSED_SRGB_S3TC_DXT1_EXT;if(n===Io)return r.COMPRESSED_SRGB_ALPHA_S3TC_DXT1_EXT;if(n===Uo)return r.COMPRESSED_SRGB_ALPHA_S3TC_DXT3_EXT;if(n===No)return r.COMPRESSED_SRGB_ALPHA_S3TC_DXT5_EXT}else return null;else if(r=e.get("WEBGL_compressed_texture_s3tc"),r!==null){if(n===Do)return r.COMPRESSED_RGB_S3TC_DXT1_EXT;if(n===Io)return r.COMPRESSED_RGBA_S3TC_DXT1_EXT;if(n===Uo)return r.COMPRESSED_RGBA_S3TC_DXT3_EXT;if(n===No)return r.COMPRESSED_RGBA_S3TC_DXT5_EXT}else return null;if(n===Tc||n===Ac||n===Rc||n===Cc)if(r=e.get("WEBGL_compressed_texture_pvrtc"),r!==null){if(n===Tc)return r.COMPRESSED_RGB_PVRTC_4BPPV1_IMG;if(n===Ac)return r.COMPRESSED_RGB_PVRTC_2BPPV1_IMG;if(n===Rc)return r.COMPRESSED_RGBA_PVRTC_4BPPV1_IMG;if(n===Cc)return r.COMPRESSED_RGBA_PVRTC_2BPPV1_IMG}else return null;if(n===Pc||n===Lc||n===Dc)if(r=e.get("WEBGL_compressed_texture_etc"),r!==null){if(n===Pc||n===Lc)return a===Ot?r.COMPRESSED_SRGB8_ETC2:r.COMPRESSED_RGB8_ETC2;if(n===Dc)return a===Ot?r.COMPRESSED_SRGB8_ALPHA8_ETC2_EAC:r.COMPRESSED_RGBA8_ETC2_EAC}else return null;if(n===Ic||n===Uc||n===Nc||n===Fc||n===Oc||n===Bc||n===zc||n===kc||n===Hc||n===Vc||n===Gc||n===Wc||n===Xc||n===qc)if(r=e.get("WEBGL_compressed_texture_astc"),r!==null){if(n===Ic)return a===Ot?r.COMPRESSED_SRGB8_ALPHA8_ASTC_4x4_KHR:r.COMPRESSED_RGBA_ASTC_4x4_KHR;if(n===Uc)return a===Ot?r.COMPRESSED_SRGB8_ALPHA8_ASTC_5x4_KHR:r.COMPRESSED_RGBA_ASTC_5x4_KHR;if(n===Nc)return a===Ot?r.COMPRESSED_SRGB8_ALPHA8_ASTC_5x5_KHR:r.COMPRESSED_RGBA_ASTC_5x5_KHR;if(n===Fc)return a===Ot?r.COMPRESSED_SRGB8_ALPHA8_ASTC_6x5_KHR:r.COMPRESSED_RGBA_ASTC_6x5_KHR;if(n===Oc)return a===Ot?r.COMPRESSED_SRGB8_ALPHA8_ASTC_6x6_KHR:r.COMPRESSED_RGBA_ASTC_6x6_KHR;if(n===Bc)return a===Ot?r.COMPRESSED_SRGB8_ALPHA8_ASTC_8x5_KHR:r.COMPRESSED_RGBA_ASTC_8x5_KHR;if(n===zc)return a===Ot?r.COMPRESSED_SRGB8_ALPHA8_ASTC_8x6_KHR:r.COMPRESSED_RGBA_ASTC_8x6_KHR;if(n===kc)return a===Ot?r.COMPRESSED_SRGB8_ALPHA8_ASTC_8x8_KHR:r.COMPRESSED_RGBA_ASTC_8x8_KHR;if(n===Hc)return a===Ot?r.COMPRESSED_SRGB8_ALPHA8_ASTC_10x5_KHR:r.COMPRESSED_RGBA_ASTC_10x5_KHR;if(n===Vc)return a===Ot?r.COMPRESSED_SRGB8_ALPHA8_ASTC_10x6_KHR:r.COMPRESSED_RGBA_ASTC_10x6_KHR;if(n===Gc)return a===Ot?r.COMPRESSED_SRGB8_ALPHA8_ASTC_10x8_KHR:r.COMPRESSED_RGBA_ASTC_10x8_KHR;if(n===Wc)return a===Ot?r.COMPRESSED_SRGB8_ALPHA8_ASTC_10x10_KHR:r.COMPRESSED_RGBA_ASTC_10x10_KHR;if(n===Xc)return a===Ot?r.COMPRESSED_SRGB8_ALPHA8_ASTC_12x10_KHR:r.COMPRESSED_RGBA_ASTC_12x10_KHR;if(n===qc)return a===Ot?r.COMPRESSED_SRGB8_ALPHA8_ASTC_12x12_KHR:r.COMPRESSED_RGBA_ASTC_12x12_KHR}else return null;if(n===Fo||n===$c||n===Yc)if(r=e.get("EXT_texture_compression_bptc"),r!==null){if(n===Fo)return a===Ot?r.COMPRESSED_SRGB_ALPHA_BPTC_UNORM_EXT:r.COMPRESSED_RGBA_BPTC_UNORM_EXT;if(n===$c)return r.COMPRESSED_RGB_BPTC_SIGNED_FLOAT_EXT;if(n===Yc)return r.COMPRESSED_RGB_BPTC_UNSIGNED_FLOAT_EXT}else return null;if(n===kf||n===jc||n===Kc||n===Zc)if(r=e.get("EXT_texture_compression_rgtc"),r!==null){if(n===Fo)return r.COMPRESSED_RED_RGTC1_EXT;if(n===jc)return r.COMPRESSED_SIGNED_RED_RGTC1_EXT;if(n===Kc)return r.COMPRESSED_RED_GREEN_RGTC2_EXT;if(n===Zc)return r.COMPRESSED_SIGNED_RED_GREEN_RGTC2_EXT}else return null;return n===kr?i.UNSIGNED_INT_24_8:i[n]!==void 0?i[n]:null}return{convert:t}}class Fy extends bn{constructor(e=[]){super(),this.isArrayCamera=!0,this.cameras=e}}class os extends Qt{constructor(){super(),this.isGroup=!0,this.type="Group"}}const Oy={type:"move"};class sc{constructor(){this._targetRay=null,this._grip=null,this._hand=null}getHandSpace(){return this._hand===null&&(this._hand=new os,this._hand.matrixAutoUpdate=!1,this._hand.visible=!1,this._hand.joints={},this._hand.inputState={pinching:!1}),this._hand}getTargetRaySpace(){return this._targetRay===null&&(this._targetRay=new os,this._targetRay.matrixAutoUpdate=!1,this._targetRay.visible=!1,this._targetRay.hasLinearVelocity=!1,this._targetRay.linearVelocity=new H,this._targetRay.hasAngularVelocity=!1,this._targetRay.angularVelocity=new H),this._targetRay}getGripSpace(){return this._grip===null&&(this._grip=new os,this._grip.matrixAutoUpdate=!1,this._grip.visible=!1,this._grip.hasLinearVelocity=!1,this._grip.linearVelocity=new H,this._grip.hasAngularVelocity=!1,this._grip.angularVelocity=new H),this._grip}dispatchEvent(e){return this._targetRay!==null&&this._targetRay.dispatchEvent(e),this._grip!==null&&this._grip.dispatchEvent(e),this._hand!==null&&this._hand.dispatchEvent(e),this}connect(e){if(e&&e.hand){const t=this._hand;if(t)for(const n of e.hand.values())this._getHandJoint(t,n)}return this.dispatchEvent({type:"connected",data:e}),this}disconnect(e){return this.dispatchEvent({type:"disconnected",data:e}),this._targetRay!==null&&(this._targetRay.visible=!1),this._grip!==null&&(this._grip.visible=!1),this._hand!==null&&(this._hand.visible=!1),this}update(e,t,n){let s=null,r=null,a=null;const o=this._targetRay,l=this._grip,c=this._hand;if(e&&t.session.visibilityState!=="visible-blurred"){if(c&&e.hand){a=!0;for(const _ of e.hand.values()){const m=t.getJointPose(_,n),p=this._getHandJoint(c,_);m!==null&&(p.matrix.fromArray(m.transform.matrix),p.matrix.decompose(p.position,p.rotation,p.scale),p.matrixWorldNeedsUpdate=!0,p.jointRadius=m.radius),p.visible=m!==null}const h=c.joints["index-finger-tip"],u=c.joints["thumb-tip"],d=h.position.distanceTo(u.position),f=.02,g=.005;c.inputState.pinching&&d>f+g?(c.inputState.pinching=!1,this.dispatchEvent({type:"pinchend",handedness:e.handedness,target:this})):!c.inputState.pinching&&d<=f-g&&(c.inputState.pinching=!0,this.dispatchEvent({type:"pinchstart",handedness:e.handedness,target:this}))}else l!==null&&e.gripSpace&&(r=t.getPose(e.gripSpace,n),r!==null&&(l.matrix.fromArray(r.transform.matrix),l.matrix.decompose(l.position,l.rotation,l.scale),l.matrixWorldNeedsUpdate=!0,r.linearVelocity?(l.hasLinearVelocity=!0,l.linearVelocity.copy(r.linearVelocity)):l.hasLinearVelocity=!1,r.angularVelocity?(l.hasAngularVelocity=!0,l.angularVelocity.copy(r.angularVelocity)):l.hasAngularVelocity=!1));o!==null&&(s=t.getPose(e.targetRaySpace,n),s===null&&r!==null&&(s=r),s!==null&&(o.matrix.fromArray(s.transform.matrix),o.matrix.decompose(o.position,o.rotation,o.scale),o.matrixWorldNeedsUpdate=!0,s.linearVelocity?(o.hasLinearVelocity=!0,o.linearVelocity.copy(s.linearVelocity)):o.hasLinearVelocity=!1,s.angularVelocity?(o.hasAngularVelocity=!0,o.angularVelocity.copy(s.angularVelocity)):o.hasAngularVelocity=!1,this.dispatchEvent(Oy)))}return o!==null&&(o.visible=s!==null),l!==null&&(l.visible=r!==null),c!==null&&(c.visible=a!==null),this}_getHandJoint(e,t){if(e.joints[t.jointName]===void 0){const n=new os;n.matrixAutoUpdate=!1,n.visible=!1,e.joints[t.jointName]=n,e.add(n)}return e.joints[t.jointName]}}const By=`
void main() {

	gl_Position = vec4( position, 1.0 );

}`,zy=`
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

}`;class ky{constructor(){this.texture=null,this.mesh=null,this.depthNear=0,this.depthFar=0}init(e,t,n){if(this.texture===null){const s=new Ln,r=e.properties.get(s);r.__webglTexture=t.texture,(t.depthNear!=n.depthNear||t.depthFar!=n.depthFar)&&(this.depthNear=t.depthNear,this.depthFar=t.depthFar),this.texture=s}}getMesh(e){if(this.texture!==null&&this.mesh===null){const t=e.cameras[0].viewport,n=new us({vertexShader:By,fragmentShader:zy,uniforms:{depthColor:{value:this.texture},depthWidth:{value:t.z},depthHeight:{value:t.w}}});this.mesh=new _n(new za(20,20),n)}return this.mesh}reset(){this.texture=null,this.mesh=null}getDepthTexture(){return this.texture}}class Hy extends Kr{constructor(e,t){super();const n=this;let s=null,r=1,a=null,o="local-floor",l=1,c=null,h=null,u=null,d=null,f=null,g=null;const _=new ky,m=t.getContextAttributes();let p=null,S=null;const y=[],w=[],O=new qe;let A=null;const C=new bn;C.layers.enable(1),C.viewport=new nn;const F=new bn;F.layers.enable(2),F.viewport=new nn;const b=[C,F],x=new Fy;x.layers.enable(1),x.layers.enable(2);let P=null,K=null;this.cameraAutoUpdate=!0,this.enabled=!1,this.isPresenting=!1,this.getController=function(ie){let he=y[ie];return he===void 0&&(he=new sc,y[ie]=he),he.getTargetRaySpace()},this.getControllerGrip=function(ie){let he=y[ie];return he===void 0&&(he=new sc,y[ie]=he),he.getGripSpace()},this.getHand=function(ie){let he=y[ie];return he===void 0&&(he=new sc,y[ie]=he),he.getHandSpace()};function k(ie){const he=w.indexOf(ie.inputSource);if(he===-1)return;const Me=y[he];Me!==void 0&&(Me.update(ie.inputSource,ie.frame,c||a),Me.dispatchEvent({type:ie.type,data:ie.inputSource}))}function Z(){s.removeEventListener("select",k),s.removeEventListener("selectstart",k),s.removeEventListener("selectend",k),s.removeEventListener("squeeze",k),s.removeEventListener("squeezestart",k),s.removeEventListener("squeezeend",k),s.removeEventListener("end",Z),s.removeEventListener("inputsourceschange",q);for(let ie=0;ie<y.length;ie++){const he=w[ie];he!==null&&(w[ie]=null,y[ie].disconnect(he))}P=null,K=null,_.reset(),e.setRenderTarget(p),f=null,d=null,u=null,s=null,S=null,ye.stop(),n.isPresenting=!1,e.setPixelRatio(A),e.setSize(O.width,O.height,!1),n.dispatchEvent({type:"sessionend"})}this.setFramebufferScaleFactor=function(ie){r=ie,n.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change framebuffer scale while presenting.")},this.setReferenceSpaceType=function(ie){o=ie,n.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change reference space type while presenting.")},this.getReferenceSpace=function(){return c||a},this.setReferenceSpace=function(ie){c=ie},this.getBaseLayer=function(){return d!==null?d:f},this.getBinding=function(){return u},this.getFrame=function(){return g},this.getSession=function(){return s},this.setSession=async function(ie){if(s=ie,s!==null){if(p=e.getRenderTarget(),s.addEventListener("select",k),s.addEventListener("selectstart",k),s.addEventListener("selectend",k),s.addEventListener("squeeze",k),s.addEventListener("squeezestart",k),s.addEventListener("squeezeend",k),s.addEventListener("end",Z),s.addEventListener("inputsourceschange",q),m.xrCompatible!==!0&&await t.makeXRCompatible(),A=e.getPixelRatio(),e.getSize(O),s.renderState.layers===void 0){const he={antialias:m.antialias,alpha:!0,depth:m.depth,stencil:m.stencil,framebufferScaleFactor:r};f=new XRWebGLLayer(s,t,he),s.updateRenderState({baseLayer:f}),e.setPixelRatio(1),e.setSize(f.framebufferWidth,f.framebufferHeight,!1),S=new zs(f.framebufferWidth,f.framebufferHeight,{format:ci,type:Wi,colorSpace:e.outputColorSpace,stencilBuffer:m.stencil})}else{let he=null,Me=null,fe=null;m.depth&&(fe=m.stencil?t.DEPTH24_STENCIL8:t.DEPTH_COMPONENT24,he=m.stencil?Hr:Pr,Me=m.stencil?kr:Bs);const ze={colorFormat:t.RGBA8,depthFormat:fe,scaleFactor:r};u=new XRWebGLBinding(s,t),d=u.createProjectionLayer(ze),s.updateRenderState({layers:[d]}),e.setPixelRatio(1),e.setSize(d.textureWidth,d.textureHeight,!1),S=new zs(d.textureWidth,d.textureHeight,{format:ci,type:Wi,depthTexture:new Qf(d.textureWidth,d.textureHeight,Me,void 0,void 0,void 0,void 0,void 0,void 0,he),stencilBuffer:m.stencil,colorSpace:e.outputColorSpace,samples:m.antialias?4:0,resolveDepthBuffer:d.ignoreDepthValues===!1})}S.isXRRenderTarget=!0,this.setFoveation(l),c=null,a=await s.requestReferenceSpace(o),ye.setContext(s),ye.start(),n.isPresenting=!0,n.dispatchEvent({type:"sessionstart"})}},this.getEnvironmentBlendMode=function(){if(s!==null)return s.environmentBlendMode},this.getDepthTexture=function(){return _.getDepthTexture()};function q(ie){for(let he=0;he<ie.removed.length;he++){const Me=ie.removed[he],fe=w.indexOf(Me);fe>=0&&(w[fe]=null,y[fe].disconnect(Me))}for(let he=0;he<ie.added.length;he++){const Me=ie.added[he];let fe=w.indexOf(Me);if(fe===-1){for(let Ge=0;Ge<y.length;Ge++)if(Ge>=w.length){w.push(Me),fe=Ge;break}else if(w[Ge]===null){w[Ge]=Me,fe=Ge;break}if(fe===-1)break}const ze=y[fe];ze&&ze.connect(Me)}}const ee=new H,Y=new H;function ne(ie,he,Me){ee.setFromMatrixPosition(he.matrixWorld),Y.setFromMatrixPosition(Me.matrixWorld);const fe=ee.distanceTo(Y),ze=he.projectionMatrix.elements,Ge=Me.projectionMatrix.elements,Fe=ze[14]/(ze[10]-1),pt=ze[14]/(ze[10]+1),N=(ze[9]+1)/ze[5],dt=(ze[9]-1)/ze[5],st=(ze[8]-1)/ze[0],ct=(Ge[8]+1)/Ge[0],Oe=Fe*st,Et=Fe*ct,$e=fe/(-st+ct),Xe=$e*-st;if(he.matrixWorld.decompose(ie.position,ie.quaternion,ie.scale),ie.translateX(Xe),ie.translateZ($e),ie.matrixWorld.compose(ie.position,ie.quaternion,ie.scale),ie.matrixWorldInverse.copy(ie.matrixWorld).invert(),ze[10]===-1)ie.projectionMatrix.copy(he.projectionMatrix),ie.projectionMatrixInverse.copy(he.projectionMatrixInverse);else{const D=Fe+$e,E=pt+$e,Q=Oe-Xe,le=Et+(fe-Xe),te=N*pt/E*D,X=dt*pt/E*D;ie.projectionMatrix.makePerspective(Q,le,te,X,D,E),ie.projectionMatrixInverse.copy(ie.projectionMatrix).invert()}}function ge(ie,he){he===null?ie.matrixWorld.copy(ie.matrix):ie.matrixWorld.multiplyMatrices(he.matrixWorld,ie.matrix),ie.matrixWorldInverse.copy(ie.matrixWorld).invert()}this.updateCamera=function(ie){if(s===null)return;let he=ie.near,Me=ie.far;_.texture!==null&&(_.depthNear>0&&(he=_.depthNear),_.depthFar>0&&(Me=_.depthFar)),x.near=F.near=C.near=he,x.far=F.far=C.far=Me,(P!==x.near||K!==x.far)&&(s.updateRenderState({depthNear:x.near,depthFar:x.far}),P=x.near,K=x.far);const fe=ie.parent,ze=x.cameras;ge(x,fe);for(let Ge=0;Ge<ze.length;Ge++)ge(ze[Ge],fe);ze.length===2?ne(x,C,F):x.projectionMatrix.copy(C.projectionMatrix),de(ie,x,fe)};function de(ie,he,Me){Me===null?ie.matrix.copy(he.matrixWorld):(ie.matrix.copy(Me.matrixWorld),ie.matrix.invert(),ie.matrix.multiply(he.matrixWorld)),ie.matrix.decompose(ie.position,ie.quaternion,ie.scale),ie.updateMatrixWorld(!0),ie.projectionMatrix.copy(he.projectionMatrix),ie.projectionMatrixInverse.copy(he.projectionMatrixInverse),ie.isPerspectiveCamera&&(ie.fov=La*2*Math.atan(1/ie.projectionMatrix.elements[5]),ie.zoom=1)}this.getCamera=function(){return x},this.getFoveation=function(){if(!(d===null&&f===null))return l},this.setFoveation=function(ie){l=ie,d!==null&&(d.fixedFoveation=ie),f!==null&&f.fixedFoveation!==void 0&&(f.fixedFoveation=ie)},this.hasDepthSensing=function(){return _.texture!==null},this.getDepthSensingMesh=function(){return _.getMesh(x)};let xe=null;function we(ie,he){if(h=he.getViewerPose(c||a),g=he,h!==null){const Me=h.views;f!==null&&(e.setRenderTargetFramebuffer(S,f.framebuffer),e.setRenderTarget(S));let fe=!1;Me.length!==x.cameras.length&&(x.cameras.length=0,fe=!0);for(let Ge=0;Ge<Me.length;Ge++){const Fe=Me[Ge];let pt=null;if(f!==null)pt=f.getViewport(Fe);else{const dt=u.getViewSubImage(d,Fe);pt=dt.viewport,Ge===0&&(e.setRenderTargetTextures(S,dt.colorTexture,d.ignoreDepthValues?void 0:dt.depthStencilTexture),e.setRenderTarget(S))}let N=b[Ge];N===void 0&&(N=new bn,N.layers.enable(Ge),N.viewport=new nn,b[Ge]=N),N.matrix.fromArray(Fe.transform.matrix),N.matrix.decompose(N.position,N.quaternion,N.scale),N.projectionMatrix.fromArray(Fe.projectionMatrix),N.projectionMatrixInverse.copy(N.projectionMatrix).invert(),N.viewport.set(pt.x,pt.y,pt.width,pt.height),Ge===0&&(x.matrix.copy(N.matrix),x.matrix.decompose(x.position,x.quaternion,x.scale)),fe===!0&&x.cameras.push(N)}const ze=s.enabledFeatures;if(ze&&ze.includes("depth-sensing")){const Ge=u.getDepthInformation(Me[0]);Ge&&Ge.isValid&&Ge.texture&&_.init(e,Ge,s.renderState)}}for(let Me=0;Me<y.length;Me++){const fe=w[Me],ze=y[Me];fe!==null&&ze!==void 0&&ze.update(fe,he,c||a)}xe&&xe(ie,he),he.detectedPlanes&&n.dispatchEvent({type:"planesdetected",data:he}),g=null}const ye=new Jf;ye.setAnimationLoop(we),this.setAnimationLoop=function(ie){xe=ie},this.dispose=function(){}}}const Ts=new Si,Vy=new Bt;function Gy(i,e){function t(m,p){m.matrixAutoUpdate===!0&&m.updateMatrix(),p.value.copy(m.matrix)}function n(m,p){p.color.getRGB(m.fogColor.value,jf(i)),p.isFog?(m.fogNear.value=p.near,m.fogFar.value=p.far):p.isFogExp2&&(m.fogDensity.value=p.density)}function s(m,p,S,y,w){p.isMeshBasicMaterial||p.isMeshLambertMaterial?r(m,p):p.isMeshToonMaterial?(r(m,p),u(m,p)):p.isMeshPhongMaterial?(r(m,p),h(m,p)):p.isMeshStandardMaterial?(r(m,p),d(m,p),p.isMeshPhysicalMaterial&&f(m,p,w)):p.isMeshMatcapMaterial?(r(m,p),g(m,p)):p.isMeshDepthMaterial?r(m,p):p.isMeshDistanceMaterial?(r(m,p),_(m,p)):p.isMeshNormalMaterial?r(m,p):p.isLineBasicMaterial?(a(m,p),p.isLineDashedMaterial&&o(m,p)):p.isPointsMaterial?l(m,p,S,y):p.isSpriteMaterial?c(m,p):p.isShadowMaterial?(m.color.value.copy(p.color),m.opacity.value=p.opacity):p.isShaderMaterial&&(p.uniformsNeedUpdate=!1)}function r(m,p){m.opacity.value=p.opacity,p.color&&m.diffuse.value.copy(p.color),p.emissive&&m.emissive.value.copy(p.emissive).multiplyScalar(p.emissiveIntensity),p.map&&(m.map.value=p.map,t(p.map,m.mapTransform)),p.alphaMap&&(m.alphaMap.value=p.alphaMap,t(p.alphaMap,m.alphaMapTransform)),p.bumpMap&&(m.bumpMap.value=p.bumpMap,t(p.bumpMap,m.bumpMapTransform),m.bumpScale.value=p.bumpScale,p.side===In&&(m.bumpScale.value*=-1)),p.normalMap&&(m.normalMap.value=p.normalMap,t(p.normalMap,m.normalMapTransform),m.normalScale.value.copy(p.normalScale),p.side===In&&m.normalScale.value.negate()),p.displacementMap&&(m.displacementMap.value=p.displacementMap,t(p.displacementMap,m.displacementMapTransform),m.displacementScale.value=p.displacementScale,m.displacementBias.value=p.displacementBias),p.emissiveMap&&(m.emissiveMap.value=p.emissiveMap,t(p.emissiveMap,m.emissiveMapTransform)),p.specularMap&&(m.specularMap.value=p.specularMap,t(p.specularMap,m.specularMapTransform)),p.alphaTest>0&&(m.alphaTest.value=p.alphaTest);const S=e.get(p),y=S.envMap,w=S.envMapRotation;y&&(m.envMap.value=y,Ts.copy(w),Ts.x*=-1,Ts.y*=-1,Ts.z*=-1,y.isCubeTexture&&y.isRenderTargetTexture===!1&&(Ts.y*=-1,Ts.z*=-1),m.envMapRotation.value.setFromMatrix4(Vy.makeRotationFromEuler(Ts)),m.flipEnvMap.value=y.isCubeTexture&&y.isRenderTargetTexture===!1?-1:1,m.reflectivity.value=p.reflectivity,m.ior.value=p.ior,m.refractionRatio.value=p.refractionRatio),p.lightMap&&(m.lightMap.value=p.lightMap,m.lightMapIntensity.value=p.lightMapIntensity,t(p.lightMap,m.lightMapTransform)),p.aoMap&&(m.aoMap.value=p.aoMap,m.aoMapIntensity.value=p.aoMapIntensity,t(p.aoMap,m.aoMapTransform))}function a(m,p){m.diffuse.value.copy(p.color),m.opacity.value=p.opacity,p.map&&(m.map.value=p.map,t(p.map,m.mapTransform))}function o(m,p){m.dashSize.value=p.dashSize,m.totalSize.value=p.dashSize+p.gapSize,m.scale.value=p.scale}function l(m,p,S,y){m.diffuse.value.copy(p.color),m.opacity.value=p.opacity,m.size.value=p.size*S,m.scale.value=y*.5,p.map&&(m.map.value=p.map,t(p.map,m.uvTransform)),p.alphaMap&&(m.alphaMap.value=p.alphaMap,t(p.alphaMap,m.alphaMapTransform)),p.alphaTest>0&&(m.alphaTest.value=p.alphaTest)}function c(m,p){m.diffuse.value.copy(p.color),m.opacity.value=p.opacity,m.rotation.value=p.rotation,p.map&&(m.map.value=p.map,t(p.map,m.mapTransform)),p.alphaMap&&(m.alphaMap.value=p.alphaMap,t(p.alphaMap,m.alphaMapTransform)),p.alphaTest>0&&(m.alphaTest.value=p.alphaTest)}function h(m,p){m.specular.value.copy(p.specular),m.shininess.value=Math.max(p.shininess,1e-4)}function u(m,p){p.gradientMap&&(m.gradientMap.value=p.gradientMap)}function d(m,p){m.metalness.value=p.metalness,p.metalnessMap&&(m.metalnessMap.value=p.metalnessMap,t(p.metalnessMap,m.metalnessMapTransform)),m.roughness.value=p.roughness,p.roughnessMap&&(m.roughnessMap.value=p.roughnessMap,t(p.roughnessMap,m.roughnessMapTransform)),p.envMap&&(m.envMapIntensity.value=p.envMapIntensity)}function f(m,p,S){m.ior.value=p.ior,p.sheen>0&&(m.sheenColor.value.copy(p.sheenColor).multiplyScalar(p.sheen),m.sheenRoughness.value=p.sheenRoughness,p.sheenColorMap&&(m.sheenColorMap.value=p.sheenColorMap,t(p.sheenColorMap,m.sheenColorMapTransform)),p.sheenRoughnessMap&&(m.sheenRoughnessMap.value=p.sheenRoughnessMap,t(p.sheenRoughnessMap,m.sheenRoughnessMapTransform))),p.clearcoat>0&&(m.clearcoat.value=p.clearcoat,m.clearcoatRoughness.value=p.clearcoatRoughness,p.clearcoatMap&&(m.clearcoatMap.value=p.clearcoatMap,t(p.clearcoatMap,m.clearcoatMapTransform)),p.clearcoatRoughnessMap&&(m.clearcoatRoughnessMap.value=p.clearcoatRoughnessMap,t(p.clearcoatRoughnessMap,m.clearcoatRoughnessMapTransform)),p.clearcoatNormalMap&&(m.clearcoatNormalMap.value=p.clearcoatNormalMap,t(p.clearcoatNormalMap,m.clearcoatNormalMapTransform),m.clearcoatNormalScale.value.copy(p.clearcoatNormalScale),p.side===In&&m.clearcoatNormalScale.value.negate())),p.dispersion>0&&(m.dispersion.value=p.dispersion),p.iridescence>0&&(m.iridescence.value=p.iridescence,m.iridescenceIOR.value=p.iridescenceIOR,m.iridescenceThicknessMinimum.value=p.iridescenceThicknessRange[0],m.iridescenceThicknessMaximum.value=p.iridescenceThicknessRange[1],p.iridescenceMap&&(m.iridescenceMap.value=p.iridescenceMap,t(p.iridescenceMap,m.iridescenceMapTransform)),p.iridescenceThicknessMap&&(m.iridescenceThicknessMap.value=p.iridescenceThicknessMap,t(p.iridescenceThicknessMap,m.iridescenceThicknessMapTransform))),p.transmission>0&&(m.transmission.value=p.transmission,m.transmissionSamplerMap.value=S.texture,m.transmissionSamplerSize.value.set(S.width,S.height),p.transmissionMap&&(m.transmissionMap.value=p.transmissionMap,t(p.transmissionMap,m.transmissionMapTransform)),m.thickness.value=p.thickness,p.thicknessMap&&(m.thicknessMap.value=p.thicknessMap,t(p.thicknessMap,m.thicknessMapTransform)),m.attenuationDistance.value=p.attenuationDistance,m.attenuationColor.value.copy(p.attenuationColor)),p.anisotropy>0&&(m.anisotropyVector.value.set(p.anisotropy*Math.cos(p.anisotropyRotation),p.anisotropy*Math.sin(p.anisotropyRotation)),p.anisotropyMap&&(m.anisotropyMap.value=p.anisotropyMap,t(p.anisotropyMap,m.anisotropyMapTransform))),m.specularIntensity.value=p.specularIntensity,m.specularColor.value.copy(p.specularColor),p.specularColorMap&&(m.specularColorMap.value=p.specularColorMap,t(p.specularColorMap,m.specularColorMapTransform)),p.specularIntensityMap&&(m.specularIntensityMap.value=p.specularIntensityMap,t(p.specularIntensityMap,m.specularIntensityMapTransform))}function g(m,p){p.matcap&&(m.matcap.value=p.matcap)}function _(m,p){const S=e.get(p).light;m.referencePosition.value.setFromMatrixPosition(S.matrixWorld),m.nearDistance.value=S.shadow.camera.near,m.farDistance.value=S.shadow.camera.far}return{refreshFogUniforms:n,refreshMaterialUniforms:s}}function Wy(i,e,t,n){let s={},r={},a=[];const o=i.getParameter(i.MAX_UNIFORM_BUFFER_BINDINGS);function l(S,y){const w=y.program;n.uniformBlockBinding(S,w)}function c(S,y){let w=s[S.id];w===void 0&&(g(S),w=h(S),s[S.id]=w,S.addEventListener("dispose",m));const O=y.program;n.updateUBOMapping(S,O);const A=e.render.frame;r[S.id]!==A&&(d(S),r[S.id]=A)}function h(S){const y=u();S.__bindingPointIndex=y;const w=i.createBuffer(),O=S.__size,A=S.usage;return i.bindBuffer(i.UNIFORM_BUFFER,w),i.bufferData(i.UNIFORM_BUFFER,O,A),i.bindBuffer(i.UNIFORM_BUFFER,null),i.bindBufferBase(i.UNIFORM_BUFFER,y,w),w}function u(){for(let S=0;S<o;S++)if(a.indexOf(S)===-1)return a.push(S),S;return console.error("THREE.WebGLRenderer: Maximum number of simultaneously usable uniforms groups reached."),0}function d(S){const y=s[S.id],w=S.uniforms,O=S.__cache;i.bindBuffer(i.UNIFORM_BUFFER,y);for(let A=0,C=w.length;A<C;A++){const F=Array.isArray(w[A])?w[A]:[w[A]];for(let b=0,x=F.length;b<x;b++){const P=F[b];if(f(P,A,b,O)===!0){const K=P.__offset,k=Array.isArray(P.value)?P.value:[P.value];let Z=0;for(let q=0;q<k.length;q++){const ee=k[q],Y=_(ee);typeof ee=="number"||typeof ee=="boolean"?(P.__data[0]=ee,i.bufferSubData(i.UNIFORM_BUFFER,K+Z,P.__data)):ee.isMatrix3?(P.__data[0]=ee.elements[0],P.__data[1]=ee.elements[1],P.__data[2]=ee.elements[2],P.__data[3]=0,P.__data[4]=ee.elements[3],P.__data[5]=ee.elements[4],P.__data[6]=ee.elements[5],P.__data[7]=0,P.__data[8]=ee.elements[6],P.__data[9]=ee.elements[7],P.__data[10]=ee.elements[8],P.__data[11]=0):(ee.toArray(P.__data,Z),Z+=Y.storage/Float32Array.BYTES_PER_ELEMENT)}i.bufferSubData(i.UNIFORM_BUFFER,K,P.__data)}}}i.bindBuffer(i.UNIFORM_BUFFER,null)}function f(S,y,w,O){const A=S.value,C=y+"_"+w;if(O[C]===void 0)return typeof A=="number"||typeof A=="boolean"?O[C]=A:O[C]=A.clone(),!0;{const F=O[C];if(typeof A=="number"||typeof A=="boolean"){if(F!==A)return O[C]=A,!0}else if(F.equals(A)===!1)return F.copy(A),!0}return!1}function g(S){const y=S.uniforms;let w=0;const O=16;for(let C=0,F=y.length;C<F;C++){const b=Array.isArray(y[C])?y[C]:[y[C]];for(let x=0,P=b.length;x<P;x++){const K=b[x],k=Array.isArray(K.value)?K.value:[K.value];for(let Z=0,q=k.length;Z<q;Z++){const ee=k[Z],Y=_(ee),ne=w%O,ge=ne%Y.boundary,de=ne+ge;w+=ge,de!==0&&O-de<Y.storage&&(w+=O-de),K.__data=new Float32Array(Y.storage/Float32Array.BYTES_PER_ELEMENT),K.__offset=w,w+=Y.storage}}}const A=w%O;return A>0&&(w+=O-A),S.__size=w,S.__cache={},this}function _(S){const y={boundary:0,storage:0};return typeof S=="number"||typeof S=="boolean"?(y.boundary=4,y.storage=4):S.isVector2?(y.boundary=8,y.storage=8):S.isVector3||S.isColor?(y.boundary=16,y.storage=12):S.isVector4?(y.boundary=16,y.storage=16):S.isMatrix3?(y.boundary=48,y.storage=48):S.isMatrix4?(y.boundary=64,y.storage=64):S.isTexture?console.warn("THREE.WebGLRenderer: Texture samplers can not be part of an uniforms group."):console.warn("THREE.WebGLRenderer: Unsupported uniform value type.",S),y}function m(S){const y=S.target;y.removeEventListener("dispose",m);const w=a.indexOf(y.__bindingPointIndex);a.splice(w,1),i.deleteBuffer(s[y.id]),delete s[y.id],delete r[y.id]}function p(){for(const S in s)i.deleteBuffer(s[S]);a=[],s={},r={}}return{bind:l,update:c,dispose:p}}class sp{constructor(e={}){const{canvas:t=Ng(),context:n=null,depth:s=!0,stencil:r=!1,alpha:a=!1,antialias:o=!1,premultipliedAlpha:l=!0,preserveDrawingBuffer:c=!1,powerPreference:h="default",failIfMajorPerformanceCaveat:u=!1}=e;this.isWebGLRenderer=!0;let d;if(n!==null){if(typeof WebGLRenderingContext<"u"&&n instanceof WebGLRenderingContext)throw new Error("THREE.WebGLRenderer: WebGL 1 is not supported since r163.");d=n.getContextAttributes().alpha}else d=a;const f=new Uint32Array(4),g=new Int32Array(4);let _=null,m=null;const p=[],S=[];this.domElement=t,this.debug={checkShaderErrors:!0,onShaderError:null},this.autoClear=!0,this.autoClearColor=!0,this.autoClearDepth=!0,this.autoClearStencil=!0,this.sortObjects=!0,this.clippingPlanes=[],this.localClippingEnabled=!1,this._outputColorSpace=xi,this.toneMapping=cs,this.toneMappingExposure=1;const y=this;let w=!1,O=0,A=0,C=null,F=-1,b=null;const x=new nn,P=new nn;let K=null;const k=new nt(0);let Z=0,q=t.width,ee=t.height,Y=1,ne=null,ge=null;const de=new nn(0,0,q,ee),xe=new nn(0,0,q,ee);let we=!1;const ye=new Eh;let ie=!1,he=!1;const Me=new Bt,fe=new H,ze=new nn,Ge={background:null,fog:null,environment:null,overrideMaterial:null,isScene:!0};let Fe=!1;function pt(){return C===null?Y:1}let N=n;function dt(T,W){return t.getContext(T,W)}try{const T={alpha:!0,depth:s,stencil:r,antialias:o,premultipliedAlpha:l,preserveDrawingBuffer:c,powerPreference:h,failIfMajorPerformanceCaveat:u};if("setAttribute"in t&&t.setAttribute("data-engine",`three.js r${ph}`),t.addEventListener("webglcontextlost",se,!1),t.addEventListener("webglcontextrestored",re,!1),t.addEventListener("webglcontextcreationerror",ve,!1),N===null){const W="webgl2";if(N=dt(W,T),N===null)throw dt(W)?new Error("Error creating WebGL context with your selected attributes."):new Error("Error creating WebGL context.")}}catch(T){throw console.error("THREE.WebGLRenderer: "+T.message),T}let st,ct,Oe,Et,$e,Xe,D,E,Q,le,te,X,Ee,_e,Ae,Ke,me,Te,Ze,ke,be,He,B,ce;function I(){st=new Zv(N),st.init(),He=new Ny(N,st),ct=new Xv(N,st,e,He),Oe=new Dy(N),Et=new ex(N),$e=new vy,Xe=new Uy(N,st,Oe,$e,ct,He,Et),D=new $v(y),E=new Kv(y),Q=new o_(N),B=new Gv(N,Q),le=new Jv(N,Q,Et,B),te=new nx(N,le,Q,Et),Ze=new tx(N,ct,Xe),Ke=new qv($e),X=new _y(y,D,E,st,ct,B,Ke),Ee=new Gy(y,$e),_e=new yy,Ae=new Ty(st),Te=new Vv(y,D,E,Oe,te,d,l),me=new Ly(y,te,ct),ce=new Wy(N,Et,ct,Oe),ke=new Wv(N,st,Et),be=new Qv(N,st,Et),Et.programs=X.programs,y.capabilities=ct,y.extensions=st,y.properties=$e,y.renderLists=_e,y.shadowMap=me,y.state=Oe,y.info=Et}I();const ae=new Hy(y,N);this.xr=ae,this.getContext=function(){return N},this.getContextAttributes=function(){return N.getContextAttributes()},this.forceContextLoss=function(){const T=st.get("WEBGL_lose_context");T&&T.loseContext()},this.forceContextRestore=function(){const T=st.get("WEBGL_lose_context");T&&T.restoreContext()},this.getPixelRatio=function(){return Y},this.setPixelRatio=function(T){T!==void 0&&(Y=T,this.setSize(q,ee,!1))},this.getSize=function(T){return T.set(q,ee)},this.setSize=function(T,W,J=!0){if(ae.isPresenting){console.warn("THREE.WebGLRenderer: Can't change size while VR device is presenting.");return}q=T,ee=W,t.width=Math.floor(T*Y),t.height=Math.floor(W*Y),J===!0&&(t.style.width=T+"px",t.style.height=W+"px"),this.setViewport(0,0,T,W)},this.getDrawingBufferSize=function(T){return T.set(q*Y,ee*Y).floor()},this.setDrawingBufferSize=function(T,W,J){q=T,ee=W,Y=J,t.width=Math.floor(T*J),t.height=Math.floor(W*J),this.setViewport(0,0,T,W)},this.getCurrentViewport=function(T){return T.copy(x)},this.getViewport=function(T){return T.copy(de)},this.setViewport=function(T,W,J,$){T.isVector4?de.set(T.x,T.y,T.z,T.w):de.set(T,W,J,$),Oe.viewport(x.copy(de).multiplyScalar(Y).round())},this.getScissor=function(T){return T.copy(xe)},this.setScissor=function(T,W,J,$){T.isVector4?xe.set(T.x,T.y,T.z,T.w):xe.set(T,W,J,$),Oe.scissor(P.copy(xe).multiplyScalar(Y).round())},this.getScissorTest=function(){return we},this.setScissorTest=function(T){Oe.setScissorTest(we=T)},this.setOpaqueSort=function(T){ne=T},this.setTransparentSort=function(T){ge=T},this.getClearColor=function(T){return T.copy(Te.getClearColor())},this.setClearColor=function(){Te.setClearColor.apply(Te,arguments)},this.getClearAlpha=function(){return Te.getClearAlpha()},this.setClearAlpha=function(){Te.setClearAlpha.apply(Te,arguments)},this.clear=function(T=!0,W=!0,J=!0){let $=0;if(T){let G=!1;if(C!==null){const ue=C.texture.format;G=ue===yh||ue===xh||ue===vh}if(G){const ue=C.texture.type,Ce=ue===Wi||ue===Bs||ue===Pa||ue===kr||ue===gh||ue===_h,Pe=Te.getClearColor(),Ue=Te.getClearAlpha(),Je=Pe.r,Qe=Pe.g,Be=Pe.b;Ce?(f[0]=Je,f[1]=Qe,f[2]=Be,f[3]=Ue,N.clearBufferuiv(N.COLOR,0,f)):(g[0]=Je,g[1]=Qe,g[2]=Be,g[3]=Ue,N.clearBufferiv(N.COLOR,0,g))}else $|=N.COLOR_BUFFER_BIT}W&&($|=N.DEPTH_BUFFER_BIT),J&&($|=N.STENCIL_BUFFER_BIT,this.state.buffers.stencil.setMask(4294967295)),N.clear($)},this.clearColor=function(){this.clear(!0,!1,!1)},this.clearDepth=function(){this.clear(!1,!0,!1)},this.clearStencil=function(){this.clear(!1,!1,!0)},this.dispose=function(){t.removeEventListener("webglcontextlost",se,!1),t.removeEventListener("webglcontextrestored",re,!1),t.removeEventListener("webglcontextcreationerror",ve,!1),_e.dispose(),Ae.dispose(),$e.dispose(),D.dispose(),E.dispose(),te.dispose(),B.dispose(),ce.dispose(),X.dispose(),ae.dispose(),ae.removeEventListener("sessionstart",zt),ae.removeEventListener("sessionend",kt),on.stop()};function se(T){T.preventDefault(),console.log("THREE.WebGLRenderer: Context Lost."),w=!0}function re(){console.log("THREE.WebGLRenderer: Context Restored."),w=!1;const T=Et.autoReset,W=me.enabled,J=me.autoUpdate,$=me.needsUpdate,G=me.type;I(),Et.autoReset=T,me.enabled=W,me.autoUpdate=J,me.needsUpdate=$,me.type=G}function ve(T){console.error("THREE.WebGLRenderer: A WebGL context could not be created. Reason: ",T.statusMessage)}function je(T){const W=T.target;W.removeEventListener("dispose",je),ot(W)}function ot(T){_t(T),$e.remove(T)}function _t(T){const W=$e.get(T).programs;W!==void 0&&(W.forEach(function(J){X.releaseProgram(J)}),T.isShaderMaterial&&X.releaseShaderCache(T))}this.renderBufferDirect=function(T,W,J,$,G,ue){W===null&&(W=Ge);const Ce=G.isMesh&&G.matrixWorld.determinant()<0,Pe=xl(T,W,J,$,G);Oe.setMaterial($,Ce);let Ue=J.index,Je=1;if($.wireframe===!0){if(Ue=le.getWireframeAttribute(J),Ue===void 0)return;Je=2}const Qe=J.drawRange,Be=J.attributes.position;let ht=Qe.start*Je,Pt=(Qe.start+Qe.count)*Je;ue!==null&&(ht=Math.max(ht,ue.start*Je),Pt=Math.min(Pt,(ue.start+ue.count)*Je)),Ue!==null?(ht=Math.max(ht,0),Pt=Math.min(Pt,Ue.count)):Be!=null&&(ht=Math.max(ht,0),Pt=Math.min(Pt,Be.count));const Lt=Pt-ht;if(Lt<0||Lt===1/0)return;B.setup(G,$,Pe,J,Ue);let mn,mt=ke;if(Ue!==null&&(mn=Q.get(Ue),mt=be,mt.setIndex(mn)),G.isMesh)$.wireframe===!0?(Oe.setLineWidth($.wireframeLinewidth*pt()),mt.setMode(N.LINES)):mt.setMode(N.TRIANGLES);else if(G.isLine){let Ve=$.linewidth;Ve===void 0&&(Ve=1),Oe.setLineWidth(Ve*pt()),G.isLineSegments?mt.setMode(N.LINES):G.isLineLoop?mt.setMode(N.LINE_LOOP):mt.setMode(N.LINE_STRIP)}else G.isPoints?mt.setMode(N.POINTS):G.isSprite&&mt.setMode(N.TRIANGLES);if(G.isBatchedMesh)if(G._multiDrawInstances!==null)mt.renderMultiDrawInstances(G._multiDrawStarts,G._multiDrawCounts,G._multiDrawCount,G._multiDrawInstances);else if(st.get("WEBGL_multi_draw"))mt.renderMultiDraw(G._multiDrawStarts,G._multiDrawCounts,G._multiDrawCount);else{const Ve=G._multiDrawStarts,$t=G._multiDrawCounts,gt=G._multiDrawCount,Dt=Ue?Q.get(Ue).bytesPerElement:1,Ri=$e.get($).currentProgram.getUniforms();for(let xn=0;xn<gt;xn++)Ri.setValue(N,"_gl_DrawID",xn),mt.render(Ve[xn]/Dt,$t[xn])}else if(G.isInstancedMesh)mt.renderInstances(ht,Lt,G.count);else if(J.isInstancedBufferGeometry){const Ve=J._maxInstanceCount!==void 0?J._maxInstanceCount:1/0,$t=Math.min(J.instanceCount,Ve);mt.renderInstances(ht,Lt,$t)}else mt.render(ht,Lt)};function wt(T,W,J){T.transparent===!0&&T.side===Yn&&T.forceSinglePass===!1?(T.side=In,T.needsUpdate=!0,gs(T,W,J),T.side=hs,T.needsUpdate=!0,gs(T,W,J),T.side=Yn):gs(T,W,J)}this.compile=function(T,W,J=null){J===null&&(J=T),m=Ae.get(J),m.init(W),S.push(m),J.traverseVisible(function(G){G.isLight&&G.layers.test(W.layers)&&(m.pushLight(G),G.castShadow&&m.pushShadow(G))}),T!==J&&T.traverseVisible(function(G){G.isLight&&G.layers.test(W.layers)&&(m.pushLight(G),G.castShadow&&m.pushShadow(G))}),m.setupLights();const $=new Set;return T.traverse(function(G){const ue=G.material;if(ue)if(Array.isArray(ue))for(let Ce=0;Ce<ue.length;Ce++){const Pe=ue[Ce];wt(Pe,J,G),$.add(Pe)}else wt(ue,J,G),$.add(ue)}),S.pop(),m=null,$},this.compileAsync=function(T,W,J=null){const $=this.compile(T,W,J);return new Promise(G=>{function ue(){if($.forEach(function(Ce){$e.get(Ce).currentProgram.isReady()&&$.delete(Ce)}),$.size===0){G(T);return}setTimeout(ue,10)}st.get("KHR_parallel_shader_compile")!==null?ue():setTimeout(ue,10)})};let lt=null;function pn(T){lt&&lt(T)}function zt(){on.stop()}function kt(){on.start()}const on=new Jf;on.setAnimationLoop(pn),typeof self<"u"&&on.setContext(self),this.setAnimationLoop=function(T){lt=T,ae.setAnimationLoop(T),T===null?on.stop():on.start()},ae.addEventListener("sessionstart",zt),ae.addEventListener("sessionend",kt),this.render=function(T,W){if(W!==void 0&&W.isCamera!==!0){console.error("THREE.WebGLRenderer.render: camera is not an instance of THREE.Camera.");return}if(w===!0)return;if(T.matrixWorldAutoUpdate===!0&&T.updateMatrixWorld(),W.parent===null&&W.matrixWorldAutoUpdate===!0&&W.updateMatrixWorld(),ae.enabled===!0&&ae.isPresenting===!0&&(ae.cameraAutoUpdate===!0&&ae.updateCamera(W),W=ae.getCamera()),T.isScene===!0&&T.onBeforeRender(y,T,W,C),m=Ae.get(T,S.length),m.init(W),S.push(m),Me.multiplyMatrices(W.projectionMatrix,W.matrixWorldInverse),ye.setFromProjectionMatrix(Me),he=this.localClippingEnabled,ie=Ke.init(this.clippingPlanes,he),_=_e.get(T,p.length),_.init(),p.push(_),ae.enabled===!0&&ae.isPresenting===!0){const ue=y.xr.getDepthSensingMesh();ue!==null&&di(ue,W,-1/0,y.sortObjects)}di(T,W,0,y.sortObjects),_.finish(),y.sortObjects===!0&&_.sort(ne,ge),Fe=ae.enabled===!1||ae.isPresenting===!1||ae.hasDepthSensing()===!1,Fe&&Te.addToRenderList(_,T),this.info.render.frame++,ie===!0&&Ke.beginShadows();const J=m.state.shadowsArray;me.render(J,T,W),ie===!0&&Ke.endShadows(),this.info.autoReset===!0&&this.info.reset();const $=_.opaque,G=_.transmissive;if(m.setupLights(),W.isArrayCamera){const ue=W.cameras;if(G.length>0)for(let Ce=0,Pe=ue.length;Ce<Pe;Ce++){const Ue=ue[Ce];En($,G,T,Ue)}Fe&&Te.render(T);for(let Ce=0,Pe=ue.length;Ce<Pe;Ce++){const Ue=ue[Ce];wi(_,T,Ue,Ue.viewport)}}else G.length>0&&En($,G,T,W),Fe&&Te.render(T),wi(_,T,W);C!==null&&(Xe.updateMultisampleRenderTarget(C),Xe.updateRenderTargetMipmap(C)),T.isScene===!0&&T.onAfterRender(y,T,W),B.resetDefaultState(),F=-1,b=null,S.pop(),S.length>0?(m=S[S.length-1],ie===!0&&Ke.setGlobalState(y.clippingPlanes,m.state.camera)):m=null,p.pop(),p.length>0?_=p[p.length-1]:_=null};function di(T,W,J,$){if(T.visible===!1)return;if(T.layers.test(W.layers)){if(T.isGroup)J=T.renderOrder;else if(T.isLOD)T.autoUpdate===!0&&T.update(W);else if(T.isLight)m.pushLight(T),T.castShadow&&m.pushShadow(T);else if(T.isSprite){if(!T.frustumCulled||ye.intersectsSprite(T)){$&&ze.setFromMatrixPosition(T.matrixWorld).applyMatrix4(Me);const Ce=te.update(T),Pe=T.material;Pe.visible&&_.push(T,Ce,Pe,J,ze.z,null)}}else if((T.isMesh||T.isLine||T.isPoints)&&(!T.frustumCulled||ye.intersectsObject(T))){const Ce=te.update(T),Pe=T.material;if($&&(T.boundingSphere!==void 0?(T.boundingSphere===null&&T.computeBoundingSphere(),ze.copy(T.boundingSphere.center)):(Ce.boundingSphere===null&&Ce.computeBoundingSphere(),ze.copy(Ce.boundingSphere.center)),ze.applyMatrix4(T.matrixWorld).applyMatrix4(Me)),Array.isArray(Pe)){const Ue=Ce.groups;for(let Je=0,Qe=Ue.length;Je<Qe;Je++){const Be=Ue[Je],ht=Pe[Be.materialIndex];ht&&ht.visible&&_.push(T,Ce,ht,J,ze.z,Be)}}else Pe.visible&&_.push(T,Ce,Pe,J,ze.z,null)}}const ue=T.children;for(let Ce=0,Pe=ue.length;Ce<Pe;Ce++)di(ue[Ce],W,J,$)}function wi(T,W,J,$){const G=T.opaque,ue=T.transmissive,Ce=T.transparent;m.setupLightsView(J),ie===!0&&Ke.setGlobalState(y.clippingPlanes,J),$&&Oe.viewport(x.copy($)),G.length>0&&Jn(G,W,J),ue.length>0&&Jn(ue,W,J),Ce.length>0&&Jn(Ce,W,J),Oe.buffers.depth.setTest(!0),Oe.buffers.depth.setMask(!0),Oe.buffers.color.setMask(!0),Oe.setPolygonOffset(!1)}function En(T,W,J,$){if((J.isScene===!0?J.overrideMaterial:null)!==null)return;m.state.transmissionRenderTarget[$.id]===void 0&&(m.state.transmissionRenderTarget[$.id]=new zs(1,1,{generateMipmaps:!0,type:st.has("EXT_color_buffer_half_float")||st.has("EXT_color_buffer_float")?Na:Wi,minFilter:Us,samples:4,stencilBuffer:r,resolveDepthBuffer:!1,resolveStencilBuffer:!1,colorSpace:bt.workingColorSpace}));const ue=m.state.transmissionRenderTarget[$.id],Ce=$.viewport||x;ue.setSize(Ce.z,Ce.w);const Pe=y.getRenderTarget();y.setRenderTarget(ue),y.getClearColor(k),Z=y.getClearAlpha(),Z<1&&y.setClearColor(16777215,.5),y.clear(),Fe&&Te.render(J);const Ue=y.toneMapping;y.toneMapping=cs;const Je=$.viewport;if($.viewport!==void 0&&($.viewport=void 0),m.setupLightsView($),ie===!0&&Ke.setGlobalState(y.clippingPlanes,$),Jn(T,J,$),Xe.updateMultisampleRenderTarget(ue),Xe.updateRenderTargetMipmap(ue),st.has("WEBGL_multisampled_render_to_texture")===!1){let Qe=!1;for(let Be=0,ht=W.length;Be<ht;Be++){const Pt=W[Be],Lt=Pt.object,mn=Pt.geometry,mt=Pt.material,Ve=Pt.group;if(mt.side===Yn&&Lt.layers.test($.layers)){const $t=mt.side;mt.side=In,mt.needsUpdate=!0,Ti(Lt,J,$,mn,mt,Ve),mt.side=$t,mt.needsUpdate=!0,Qe=!0}}Qe===!0&&(Xe.updateMultisampleRenderTarget(ue),Xe.updateRenderTargetMipmap(ue))}y.setRenderTarget(Pe),y.setClearColor(k,Z),Je!==void 0&&($.viewport=Je),y.toneMapping=Ue}function Jn(T,W,J){const $=W.isScene===!0?W.overrideMaterial:null;for(let G=0,ue=T.length;G<ue;G++){const Ce=T[G],Pe=Ce.object,Ue=Ce.geometry,Je=$===null?Ce.material:$,Qe=Ce.group;Pe.layers.test(J.layers)&&Ti(Pe,W,J,Ue,Je,Qe)}}function Ti(T,W,J,$,G,ue){T.onBeforeRender(y,W,J,$,G,ue),T.modelViewMatrix.multiplyMatrices(J.matrixWorldInverse,T.matrixWorld),T.normalMatrix.getNormalMatrix(T.modelViewMatrix),G.onBeforeRender(y,W,J,$,T,ue),G.transparent===!0&&G.side===Yn&&G.forceSinglePass===!1?(G.side=In,G.needsUpdate=!0,y.renderBufferDirect(J,W,$,G,T,ue),G.side=hs,G.needsUpdate=!0,y.renderBufferDirect(J,W,$,G,T,ue),G.side=Yn):y.renderBufferDirect(J,W,$,G,T,ue),T.onAfterRender(y,W,J,$,G,ue)}function gs(T,W,J){W.isScene!==!0&&(W=Ge);const $=$e.get(T),G=m.state.lights,ue=m.state.shadowsArray,Ce=G.state.version,Pe=X.getParameters(T,G.state,ue,W,J),Ue=X.getProgramCacheKey(Pe);let Je=$.programs;$.environment=T.isMeshStandardMaterial?W.environment:null,$.fog=W.fog,$.envMap=(T.isMeshStandardMaterial?E:D).get(T.envMap||$.environment),$.envMapRotation=$.environment!==null&&T.envMap===null?W.environmentRotation:T.envMapRotation,Je===void 0&&(T.addEventListener("dispose",je),Je=new Map,$.programs=Je);let Qe=Je.get(Ue);if(Qe!==void 0){if($.currentProgram===Qe&&$.lightsStateVersion===Ce)return ka(T,Pe),Qe}else Pe.uniforms=X.getUniforms(T),T.onBeforeCompile(Pe,y),Qe=X.acquireProgram(Pe,Ue),Je.set(Ue,Qe),$.uniforms=Pe.uniforms;const Be=$.uniforms;return(!T.isShaderMaterial&&!T.isRawShaderMaterial||T.clipping===!0)&&(Be.clippingPlanes=Ke.uniform),ka(T,Pe),$.needsLights=yl(T),$.lightsStateVersion=Ce,$.needsLights&&(Be.ambientLightColor.value=G.state.ambient,Be.lightProbe.value=G.state.probe,Be.directionalLights.value=G.state.directional,Be.directionalLightShadows.value=G.state.directionalShadow,Be.spotLights.value=G.state.spot,Be.spotLightShadows.value=G.state.spotShadow,Be.rectAreaLights.value=G.state.rectArea,Be.ltc_1.value=G.state.rectAreaLTC1,Be.ltc_2.value=G.state.rectAreaLTC2,Be.pointLights.value=G.state.point,Be.pointLightShadows.value=G.state.pointShadow,Be.hemisphereLights.value=G.state.hemi,Be.directionalShadowMap.value=G.state.directionalShadowMap,Be.directionalShadowMatrix.value=G.state.directionalShadowMatrix,Be.spotShadowMap.value=G.state.spotShadowMap,Be.spotLightMatrix.value=G.state.spotLightMatrix,Be.spotLightMap.value=G.state.spotLightMap,Be.pointShadowMap.value=G.state.pointShadowMap,Be.pointShadowMatrix.value=G.state.pointShadowMatrix),$.currentProgram=Qe,$.uniformsList=null,Qe}function ia(T){if(T.uniformsList===null){const W=T.currentProgram.getUniforms();T.uniformsList=Oo.seqWithValue(W.seq,T.uniforms)}return T.uniformsList}function ka(T,W){const J=$e.get(T);J.outputColorSpace=W.outputColorSpace,J.batching=W.batching,J.batchingColor=W.batchingColor,J.instancing=W.instancing,J.instancingColor=W.instancingColor,J.instancingMorph=W.instancingMorph,J.skinning=W.skinning,J.morphTargets=W.morphTargets,J.morphNormals=W.morphNormals,J.morphColors=W.morphColors,J.morphTargetsCount=W.morphTargetsCount,J.numClippingPlanes=W.numClippingPlanes,J.numIntersection=W.numClipIntersection,J.vertexAlphas=W.vertexAlphas,J.vertexTangents=W.vertexTangents,J.toneMapping=W.toneMapping}function xl(T,W,J,$,G){W.isScene!==!0&&(W=Ge),Xe.resetTextureUnits();const ue=W.fog,Ce=$.isMeshStandardMaterial?W.environment:null,Pe=C===null?y.outputColorSpace:C.isXRRenderTarget===!0?C.texture.colorSpace:ps,Ue=($.isMeshStandardMaterial?E:D).get($.envMap||Ce),Je=$.vertexColors===!0&&!!J.attributes.color&&J.attributes.color.itemSize===4,Qe=!!J.attributes.tangent&&(!!$.normalMap||$.anisotropy>0),Be=!!J.morphAttributes.position,ht=!!J.morphAttributes.normal,Pt=!!J.morphAttributes.color;let Lt=cs;$.toneMapped&&(C===null||C.isXRRenderTarget===!0)&&(Lt=y.toneMapping);const mn=J.morphAttributes.position||J.morphAttributes.normal||J.morphAttributes.color,mt=mn!==void 0?mn.length:0,Ve=$e.get($),$t=m.state.lights;if(ie===!0&&(he===!0||T!==b)){const Dn=T===b&&$.id===F;Ke.setState($,T,Dn)}let gt=!1;$.version===Ve.__version?(Ve.needsLights&&Ve.lightsStateVersion!==$t.state.version||Ve.outputColorSpace!==Pe||G.isBatchedMesh&&Ve.batching===!1||!G.isBatchedMesh&&Ve.batching===!0||G.isBatchedMesh&&Ve.batchingColor===!0&&G.colorTexture===null||G.isBatchedMesh&&Ve.batchingColor===!1&&G.colorTexture!==null||G.isInstancedMesh&&Ve.instancing===!1||!G.isInstancedMesh&&Ve.instancing===!0||G.isSkinnedMesh&&Ve.skinning===!1||!G.isSkinnedMesh&&Ve.skinning===!0||G.isInstancedMesh&&Ve.instancingColor===!0&&G.instanceColor===null||G.isInstancedMesh&&Ve.instancingColor===!1&&G.instanceColor!==null||G.isInstancedMesh&&Ve.instancingMorph===!0&&G.morphTexture===null||G.isInstancedMesh&&Ve.instancingMorph===!1&&G.morphTexture!==null||Ve.envMap!==Ue||$.fog===!0&&Ve.fog!==ue||Ve.numClippingPlanes!==void 0&&(Ve.numClippingPlanes!==Ke.numPlanes||Ve.numIntersection!==Ke.numIntersection)||Ve.vertexAlphas!==Je||Ve.vertexTangents!==Qe||Ve.morphTargets!==Be||Ve.morphNormals!==ht||Ve.morphColors!==Pt||Ve.toneMapping!==Lt||Ve.morphTargetsCount!==mt)&&(gt=!0):(gt=!0,Ve.__version=$.version);let Dt=Ve.currentProgram;gt===!0&&(Dt=gs($,W,G));let Ri=!1,xn=!1,_s=!1;const Vt=Dt.getUniforms(),fi=Ve.uniforms;if(Oe.useProgram(Dt.program)&&(Ri=!0,xn=!0,_s=!0),$.id!==F&&(F=$.id,xn=!0),Ri||b!==T){Vt.setValue(N,"projectionMatrix",T.projectionMatrix),Vt.setValue(N,"viewMatrix",T.matrixWorldInverse);const Dn=Vt.map.cameraPosition;Dn!==void 0&&Dn.setValue(N,fe.setFromMatrixPosition(T.matrixWorld)),ct.logarithmicDepthBuffer&&Vt.setValue(N,"logDepthBufFC",2/(Math.log(T.far+1)/Math.LN2)),($.isMeshPhongMaterial||$.isMeshToonMaterial||$.isMeshLambertMaterial||$.isMeshBasicMaterial||$.isMeshStandardMaterial||$.isShaderMaterial)&&Vt.setValue(N,"isOrthographic",T.isOrthographicCamera===!0),b!==T&&(b=T,xn=!0,_s=!0)}if(G.isSkinnedMesh){Vt.setOptional(N,G,"bindMatrix"),Vt.setOptional(N,G,"bindMatrixInverse");const Dn=G.skeleton;Dn&&(Dn.boneTexture===null&&Dn.computeBoneTexture(),Vt.setValue(N,"boneTexture",Dn.boneTexture,Xe))}G.isBatchedMesh&&(Vt.setOptional(N,G,"batchingTexture"),Vt.setValue(N,"batchingTexture",G._matricesTexture,Xe),Vt.setOptional(N,G,"batchingIdTexture"),Vt.setValue(N,"batchingIdTexture",G._indirectTexture,Xe),Vt.setOptional(N,G,"batchingColorTexture"),G._colorsTexture!==null&&Vt.setValue(N,"batchingColorTexture",G._colorsTexture,Xe));const sa=J.morphAttributes;if((sa.position!==void 0||sa.normal!==void 0||sa.color!==void 0)&&Ze.update(G,J,Dt),(xn||Ve.receiveShadow!==G.receiveShadow)&&(Ve.receiveShadow=G.receiveShadow,Vt.setValue(N,"receiveShadow",G.receiveShadow)),$.isMeshGouraudMaterial&&$.envMap!==null&&(fi.envMap.value=Ue,fi.flipEnvMap.value=Ue.isCubeTexture&&Ue.isRenderTargetTexture===!1?-1:1),$.isMeshStandardMaterial&&$.envMap===null&&W.environment!==null&&(fi.envMapIntensity.value=W.environmentIntensity),xn&&(Vt.setValue(N,"toneMappingExposure",y.toneMappingExposure),Ve.needsLights&&Ai(fi,_s),ue&&$.fog===!0&&Ee.refreshFogUniforms(fi,ue),Ee.refreshMaterialUniforms(fi,$,Y,ee,m.state.transmissionRenderTarget[T.id]),Oo.upload(N,ia(Ve),fi,Xe)),$.isShaderMaterial&&$.uniformsNeedUpdate===!0&&(Oo.upload(N,ia(Ve),fi,Xe),$.uniformsNeedUpdate=!1),$.isSpriteMaterial&&Vt.setValue(N,"center",G.center),Vt.setValue(N,"modelViewMatrix",G.modelViewMatrix),Vt.setValue(N,"normalMatrix",G.normalMatrix),Vt.setValue(N,"modelMatrix",G.matrixWorld),$.isShaderMaterial||$.isRawShaderMaterial){const Dn=$.uniformsGroups;for(let Ws=0,Ha=Dn.length;Ws<Ha;Ws++){const Va=Dn[Ws];ce.update(Va,Dt),ce.bind(Va,Dt)}}return Dt}function Ai(T,W){T.ambientLightColor.needsUpdate=W,T.lightProbe.needsUpdate=W,T.directionalLights.needsUpdate=W,T.directionalLightShadows.needsUpdate=W,T.pointLights.needsUpdate=W,T.pointLightShadows.needsUpdate=W,T.spotLights.needsUpdate=W,T.spotLightShadows.needsUpdate=W,T.rectAreaLights.needsUpdate=W,T.hemisphereLights.needsUpdate=W}function yl(T){return T.isMeshLambertMaterial||T.isMeshToonMaterial||T.isMeshPhongMaterial||T.isMeshStandardMaterial||T.isShadowMaterial||T.isShaderMaterial&&T.lights===!0}this.getActiveCubeFace=function(){return O},this.getActiveMipmapLevel=function(){return A},this.getRenderTarget=function(){return C},this.setRenderTargetTextures=function(T,W,J){$e.get(T.texture).__webglTexture=W,$e.get(T.depthTexture).__webglTexture=J;const $=$e.get(T);$.__hasExternalTextures=!0,$.__autoAllocateDepthBuffer=J===void 0,$.__autoAllocateDepthBuffer||st.has("WEBGL_multisampled_render_to_texture")===!0&&(console.warn("THREE.WebGLRenderer: Render-to-texture extension was disabled because an external texture was provided"),$.__useRenderToTexture=!1)},this.setRenderTargetFramebuffer=function(T,W){const J=$e.get(T);J.__webglFramebuffer=W,J.__useDefaultFramebuffer=W===void 0},this.setRenderTarget=function(T,W=0,J=0){C=T,O=W,A=J;let $=!0,G=null,ue=!1,Ce=!1;if(T){const Ue=$e.get(T);if(Ue.__useDefaultFramebuffer!==void 0)Oe.bindFramebuffer(N.FRAMEBUFFER,null),$=!1;else if(Ue.__webglFramebuffer===void 0)Xe.setupRenderTarget(T);else if(Ue.__hasExternalTextures)Xe.rebindTextures(T,$e.get(T.texture).__webglTexture,$e.get(T.depthTexture).__webglTexture);else if(T.depthBuffer){const Be=T.depthTexture;if(Ue.__boundDepthTexture!==Be){if(Be!==null&&$e.has(Be)&&(T.width!==Be.image.width||T.height!==Be.image.height))throw new Error("WebGLRenderTarget: Attached DepthTexture is initialized to the incorrect size.");Xe.setupDepthRenderbuffer(T)}}const Je=T.texture;(Je.isData3DTexture||Je.isDataArrayTexture||Je.isCompressedArrayTexture)&&(Ce=!0);const Qe=$e.get(T).__webglFramebuffer;T.isWebGLCubeRenderTarget?(Array.isArray(Qe[W])?G=Qe[W][J]:G=Qe[W],ue=!0):T.samples>0&&Xe.useMultisampledRTT(T)===!1?G=$e.get(T).__webglMultisampledFramebuffer:Array.isArray(Qe)?G=Qe[J]:G=Qe,x.copy(T.viewport),P.copy(T.scissor),K=T.scissorTest}else x.copy(de).multiplyScalar(Y).floor(),P.copy(xe).multiplyScalar(Y).floor(),K=we;if(Oe.bindFramebuffer(N.FRAMEBUFFER,G)&&$&&Oe.drawBuffers(T,G),Oe.viewport(x),Oe.scissor(P),Oe.setScissorTest(K),ue){const Ue=$e.get(T.texture);N.framebufferTexture2D(N.FRAMEBUFFER,N.COLOR_ATTACHMENT0,N.TEXTURE_CUBE_MAP_POSITIVE_X+W,Ue.__webglTexture,J)}else if(Ce){const Ue=$e.get(T.texture),Je=W||0;N.framebufferTextureLayer(N.FRAMEBUFFER,N.COLOR_ATTACHMENT0,Ue.__webglTexture,J||0,Je)}F=-1},this.readRenderTargetPixels=function(T,W,J,$,G,ue,Ce){if(!(T&&T.isWebGLRenderTarget)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");return}let Pe=$e.get(T).__webglFramebuffer;if(T.isWebGLCubeRenderTarget&&Ce!==void 0&&(Pe=Pe[Ce]),Pe){Oe.bindFramebuffer(N.FRAMEBUFFER,Pe);try{const Ue=T.texture,Je=Ue.format,Qe=Ue.type;if(!ct.textureFormatReadable(Je)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in RGBA or implementation defined format.");return}if(!ct.textureTypeReadable(Qe)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in UnsignedByteType or implementation defined type.");return}W>=0&&W<=T.width-$&&J>=0&&J<=T.height-G&&N.readPixels(W,J,$,G,He.convert(Je),He.convert(Qe),ue)}finally{const Ue=C!==null?$e.get(C).__webglFramebuffer:null;Oe.bindFramebuffer(N.FRAMEBUFFER,Ue)}}},this.readRenderTargetPixelsAsync=async function(T,W,J,$,G,ue,Ce){if(!(T&&T.isWebGLRenderTarget))throw new Error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");let Pe=$e.get(T).__webglFramebuffer;if(T.isWebGLCubeRenderTarget&&Ce!==void 0&&(Pe=Pe[Ce]),Pe){Oe.bindFramebuffer(N.FRAMEBUFFER,Pe);try{const Ue=T.texture,Je=Ue.format,Qe=Ue.type;if(!ct.textureFormatReadable(Je))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in RGBA or implementation defined format.");if(!ct.textureTypeReadable(Qe))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in UnsignedByteType or implementation defined type.");if(W>=0&&W<=T.width-$&&J>=0&&J<=T.height-G){const Be=N.createBuffer();N.bindBuffer(N.PIXEL_PACK_BUFFER,Be),N.bufferData(N.PIXEL_PACK_BUFFER,ue.byteLength,N.STREAM_READ),N.readPixels(W,J,$,G,He.convert(Je),He.convert(Qe),0),N.flush();const ht=N.fenceSync(N.SYNC_GPU_COMMANDS_COMPLETE,0);await Fg(N,ht,4);try{N.bindBuffer(N.PIXEL_PACK_BUFFER,Be),N.getBufferSubData(N.PIXEL_PACK_BUFFER,0,ue)}finally{N.deleteBuffer(Be),N.deleteSync(ht)}return ue}}finally{const Ue=C!==null?$e.get(C).__webglFramebuffer:null;Oe.bindFramebuffer(N.FRAMEBUFFER,Ue)}}},this.copyFramebufferToTexture=function(T,W=null,J=0){T.isTexture!==!0&&(Dr("WebGLRenderer: copyFramebufferToTexture function signature has changed."),W=arguments[0]||null,T=arguments[1]);const $=Math.pow(2,-J),G=Math.floor(T.image.width*$),ue=Math.floor(T.image.height*$),Ce=W!==null?W.x:0,Pe=W!==null?W.y:0;Xe.setTexture2D(T,0),N.copyTexSubImage2D(N.TEXTURE_2D,J,0,0,Ce,Pe,G,ue),Oe.unbindTexture()},this.copyTextureToTexture=function(T,W,J=null,$=null,G=0){T.isTexture!==!0&&(Dr("WebGLRenderer: copyTextureToTexture function signature has changed."),$=arguments[0]||null,T=arguments[1],W=arguments[2],G=arguments[3]||0,J=null);let ue,Ce,Pe,Ue,Je,Qe;J!==null?(ue=J.max.x-J.min.x,Ce=J.max.y-J.min.y,Pe=J.min.x,Ue=J.min.y):(ue=T.image.width,Ce=T.image.height,Pe=0,Ue=0),$!==null?(Je=$.x,Qe=$.y):(Je=0,Qe=0);const Be=He.convert(W.format),ht=He.convert(W.type);Xe.setTexture2D(W,0),N.pixelStorei(N.UNPACK_FLIP_Y_WEBGL,W.flipY),N.pixelStorei(N.UNPACK_PREMULTIPLY_ALPHA_WEBGL,W.premultiplyAlpha),N.pixelStorei(N.UNPACK_ALIGNMENT,W.unpackAlignment);const Pt=N.getParameter(N.UNPACK_ROW_LENGTH),Lt=N.getParameter(N.UNPACK_IMAGE_HEIGHT),mn=N.getParameter(N.UNPACK_SKIP_PIXELS),mt=N.getParameter(N.UNPACK_SKIP_ROWS),Ve=N.getParameter(N.UNPACK_SKIP_IMAGES),$t=T.isCompressedTexture?T.mipmaps[G]:T.image;N.pixelStorei(N.UNPACK_ROW_LENGTH,$t.width),N.pixelStorei(N.UNPACK_IMAGE_HEIGHT,$t.height),N.pixelStorei(N.UNPACK_SKIP_PIXELS,Pe),N.pixelStorei(N.UNPACK_SKIP_ROWS,Ue),T.isDataTexture?N.texSubImage2D(N.TEXTURE_2D,G,Je,Qe,ue,Ce,Be,ht,$t.data):T.isCompressedTexture?N.compressedTexSubImage2D(N.TEXTURE_2D,G,Je,Qe,$t.width,$t.height,Be,$t.data):N.texSubImage2D(N.TEXTURE_2D,G,Je,Qe,ue,Ce,Be,ht,$t),N.pixelStorei(N.UNPACK_ROW_LENGTH,Pt),N.pixelStorei(N.UNPACK_IMAGE_HEIGHT,Lt),N.pixelStorei(N.UNPACK_SKIP_PIXELS,mn),N.pixelStorei(N.UNPACK_SKIP_ROWS,mt),N.pixelStorei(N.UNPACK_SKIP_IMAGES,Ve),G===0&&W.generateMipmaps&&N.generateMipmap(N.TEXTURE_2D),Oe.unbindTexture()},this.copyTextureToTexture3D=function(T,W,J=null,$=null,G=0){T.isTexture!==!0&&(Dr("WebGLRenderer: copyTextureToTexture3D function signature has changed."),J=arguments[0]||null,$=arguments[1]||null,T=arguments[2],W=arguments[3],G=arguments[4]||0);let ue,Ce,Pe,Ue,Je,Qe,Be,ht,Pt;const Lt=T.isCompressedTexture?T.mipmaps[G]:T.image;J!==null?(ue=J.max.x-J.min.x,Ce=J.max.y-J.min.y,Pe=J.max.z-J.min.z,Ue=J.min.x,Je=J.min.y,Qe=J.min.z):(ue=Lt.width,Ce=Lt.height,Pe=Lt.depth,Ue=0,Je=0,Qe=0),$!==null?(Be=$.x,ht=$.y,Pt=$.z):(Be=0,ht=0,Pt=0);const mn=He.convert(W.format),mt=He.convert(W.type);let Ve;if(W.isData3DTexture)Xe.setTexture3D(W,0),Ve=N.TEXTURE_3D;else if(W.isDataArrayTexture||W.isCompressedArrayTexture)Xe.setTexture2DArray(W,0),Ve=N.TEXTURE_2D_ARRAY;else{console.warn("THREE.WebGLRenderer.copyTextureToTexture3D: only supports THREE.DataTexture3D and THREE.DataTexture2DArray.");return}N.pixelStorei(N.UNPACK_FLIP_Y_WEBGL,W.flipY),N.pixelStorei(N.UNPACK_PREMULTIPLY_ALPHA_WEBGL,W.premultiplyAlpha),N.pixelStorei(N.UNPACK_ALIGNMENT,W.unpackAlignment);const $t=N.getParameter(N.UNPACK_ROW_LENGTH),gt=N.getParameter(N.UNPACK_IMAGE_HEIGHT),Dt=N.getParameter(N.UNPACK_SKIP_PIXELS),Ri=N.getParameter(N.UNPACK_SKIP_ROWS),xn=N.getParameter(N.UNPACK_SKIP_IMAGES);N.pixelStorei(N.UNPACK_ROW_LENGTH,Lt.width),N.pixelStorei(N.UNPACK_IMAGE_HEIGHT,Lt.height),N.pixelStorei(N.UNPACK_SKIP_PIXELS,Ue),N.pixelStorei(N.UNPACK_SKIP_ROWS,Je),N.pixelStorei(N.UNPACK_SKIP_IMAGES,Qe),T.isDataTexture||T.isData3DTexture?N.texSubImage3D(Ve,G,Be,ht,Pt,ue,Ce,Pe,mn,mt,Lt.data):W.isCompressedArrayTexture?N.compressedTexSubImage3D(Ve,G,Be,ht,Pt,ue,Ce,Pe,mn,Lt.data):N.texSubImage3D(Ve,G,Be,ht,Pt,ue,Ce,Pe,mn,mt,Lt),N.pixelStorei(N.UNPACK_ROW_LENGTH,$t),N.pixelStorei(N.UNPACK_IMAGE_HEIGHT,gt),N.pixelStorei(N.UNPACK_SKIP_PIXELS,Dt),N.pixelStorei(N.UNPACK_SKIP_ROWS,Ri),N.pixelStorei(N.UNPACK_SKIP_IMAGES,xn),G===0&&W.generateMipmaps&&N.generateMipmap(Ve),Oe.unbindTexture()},this.initRenderTarget=function(T){$e.get(T).__webglFramebuffer===void 0&&Xe.setupRenderTarget(T)},this.initTexture=function(T){T.isCubeTexture?Xe.setTextureCube(T,0):T.isData3DTexture?Xe.setTexture3D(T,0):T.isDataArrayTexture||T.isCompressedArrayTexture?Xe.setTexture2DArray(T,0):Xe.setTexture2D(T,0),Oe.unbindTexture()},this.resetState=function(){O=0,A=0,C=null,Oe.reset(),B.reset()},typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}get coordinateSystem(){return Bi}get outputColorSpace(){return this._outputColorSpace}set outputColorSpace(e){this._outputColorSpace=e;const t=this.getContext();t.drawingBufferColorSpace=e===Mh?"display-p3":"srgb",t.unpackColorSpace=bt.workingColorSpace===al?"display-p3":"srgb"}}class Th{constructor(e,t=25e-5){this.isFogExp2=!0,this.name="",this.color=new nt(e),this.density=t}clone(){return new Th(this.color,this.density)}toJSON(){return{type:"FogExp2",name:this.name,color:this.color.getHex(),density:this.density}}}class Ah extends Qt{constructor(){super(),this.isScene=!0,this.type="Scene",this.background=null,this.environment=null,this.fog=null,this.backgroundBlurriness=0,this.backgroundIntensity=1,this.backgroundRotation=new Si,this.environmentIntensity=1,this.environmentRotation=new Si,this.overrideMaterial=null,typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}copy(e,t){return super.copy(e,t),e.background!==null&&(this.background=e.background.clone()),e.environment!==null&&(this.environment=e.environment.clone()),e.fog!==null&&(this.fog=e.fog.clone()),this.backgroundBlurriness=e.backgroundBlurriness,this.backgroundIntensity=e.backgroundIntensity,this.backgroundRotation.copy(e.backgroundRotation),this.environmentIntensity=e.environmentIntensity,this.environmentRotation.copy(e.environmentRotation),e.overrideMaterial!==null&&(this.overrideMaterial=e.overrideMaterial.clone()),this.matrixAutoUpdate=e.matrixAutoUpdate,this}toJSON(e){const t=super.toJSON(e);return this.fog!==null&&(t.object.fog=this.fog.toJSON()),this.backgroundBlurriness>0&&(t.object.backgroundBlurriness=this.backgroundBlurriness),this.backgroundIntensity!==1&&(t.object.backgroundIntensity=this.backgroundIntensity),t.object.backgroundRotation=this.backgroundRotation.toArray(),this.environmentIntensity!==1&&(t.object.environmentIntensity=this.environmentIntensity),t.object.environmentRotation=this.environmentRotation.toArray(),t}}class Xy{constructor(e,t){this.isInterleavedBuffer=!0,this.array=e,this.stride=t,this.count=e!==void 0?e.length/t:0,this.usage=Jc,this._updateRange={offset:0,count:-1},this.updateRanges=[],this.version=0,this.uuid=ki()}onUploadCallback(){}set needsUpdate(e){e===!0&&this.version++}get updateRange(){return Dr("THREE.InterleavedBuffer: updateRange() is deprecated and will be removed in r169. Use addUpdateRange() instead."),this._updateRange}setUsage(e){return this.usage=e,this}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}copy(e){return this.array=new e.array.constructor(e.array),this.count=e.count,this.stride=e.stride,this.usage=e.usage,this}copyAt(e,t,n){e*=this.stride,n*=t.stride;for(let s=0,r=this.stride;s<r;s++)this.array[e+s]=t.array[n+s];return this}set(e,t=0){return this.array.set(e,t),this}clone(e){e.arrayBuffers===void 0&&(e.arrayBuffers={}),this.array.buffer._uuid===void 0&&(this.array.buffer._uuid=ki()),e.arrayBuffers[this.array.buffer._uuid]===void 0&&(e.arrayBuffers[this.array.buffer._uuid]=this.array.slice(0).buffer);const t=new this.array.constructor(e.arrayBuffers[this.array.buffer._uuid]),n=new this.constructor(t,this.stride);return n.setUsage(this.usage),n}onUpload(e){return this.onUploadCallback=e,this}toJSON(e){return e.arrayBuffers===void 0&&(e.arrayBuffers={}),this.array.buffer._uuid===void 0&&(this.array.buffer._uuid=ki()),e.arrayBuffers[this.array.buffer._uuid]===void 0&&(e.arrayBuffers[this.array.buffer._uuid]=Array.from(new Uint32Array(this.array.buffer))),{uuid:this.uuid,buffer:this.array.buffer._uuid,type:this.array.constructor.name,stride:this.stride}}}const Rn=new H;class $o{constructor(e,t,n,s=!1){this.isInterleavedBufferAttribute=!0,this.name="",this.data=e,this.itemSize=t,this.offset=n,this.normalized=s}get count(){return this.data.count}get array(){return this.data.array}set needsUpdate(e){this.data.needsUpdate=e}applyMatrix4(e){for(let t=0,n=this.data.count;t<n;t++)Rn.fromBufferAttribute(this,t),Rn.applyMatrix4(e),this.setXYZ(t,Rn.x,Rn.y,Rn.z);return this}applyNormalMatrix(e){for(let t=0,n=this.count;t<n;t++)Rn.fromBufferAttribute(this,t),Rn.applyNormalMatrix(e),this.setXYZ(t,Rn.x,Rn.y,Rn.z);return this}transformDirection(e){for(let t=0,n=this.count;t<n;t++)Rn.fromBufferAttribute(this,t),Rn.transformDirection(e),this.setXYZ(t,Rn.x,Rn.y,Rn.z);return this}getComponent(e,t){let n=this.array[e*this.data.stride+this.offset+t];return this.normalized&&(n=oi(n,this.array)),n}setComponent(e,t,n){return this.normalized&&(n=Tt(n,this.array)),this.data.array[e*this.data.stride+this.offset+t]=n,this}setX(e,t){return this.normalized&&(t=Tt(t,this.array)),this.data.array[e*this.data.stride+this.offset]=t,this}setY(e,t){return this.normalized&&(t=Tt(t,this.array)),this.data.array[e*this.data.stride+this.offset+1]=t,this}setZ(e,t){return this.normalized&&(t=Tt(t,this.array)),this.data.array[e*this.data.stride+this.offset+2]=t,this}setW(e,t){return this.normalized&&(t=Tt(t,this.array)),this.data.array[e*this.data.stride+this.offset+3]=t,this}getX(e){let t=this.data.array[e*this.data.stride+this.offset];return this.normalized&&(t=oi(t,this.array)),t}getY(e){let t=this.data.array[e*this.data.stride+this.offset+1];return this.normalized&&(t=oi(t,this.array)),t}getZ(e){let t=this.data.array[e*this.data.stride+this.offset+2];return this.normalized&&(t=oi(t,this.array)),t}getW(e){let t=this.data.array[e*this.data.stride+this.offset+3];return this.normalized&&(t=oi(t,this.array)),t}setXY(e,t,n){return e=e*this.data.stride+this.offset,this.normalized&&(t=Tt(t,this.array),n=Tt(n,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this}setXYZ(e,t,n,s){return e=e*this.data.stride+this.offset,this.normalized&&(t=Tt(t,this.array),n=Tt(n,this.array),s=Tt(s,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this.data.array[e+2]=s,this}setXYZW(e,t,n,s,r){return e=e*this.data.stride+this.offset,this.normalized&&(t=Tt(t,this.array),n=Tt(n,this.array),s=Tt(s,this.array),r=Tt(r,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this.data.array[e+2]=s,this.data.array[e+3]=r,this}clone(e){if(e===void 0){console.log("THREE.InterleavedBufferAttribute.clone(): Cloning an interleaved buffer attribute will de-interleave buffer data.");const t=[];for(let n=0;n<this.count;n++){const s=n*this.data.stride+this.offset;for(let r=0;r<this.itemSize;r++)t.push(this.data.array[s+r])}return new hi(new this.array.constructor(t),this.itemSize,this.normalized)}else return e.interleavedBuffers===void 0&&(e.interleavedBuffers={}),e.interleavedBuffers[this.data.uuid]===void 0&&(e.interleavedBuffers[this.data.uuid]=this.data.clone(e)),new $o(e.interleavedBuffers[this.data.uuid],this.itemSize,this.offset,this.normalized)}toJSON(e){if(e===void 0){console.log("THREE.InterleavedBufferAttribute.toJSON(): Serializing an interleaved buffer attribute will de-interleave buffer data.");const t=[];for(let n=0;n<this.count;n++){const s=n*this.data.stride+this.offset;for(let r=0;r<this.itemSize;r++)t.push(this.data.array[s+r])}return{itemSize:this.itemSize,type:this.array.constructor.name,array:t,normalized:this.normalized}}else return e.interleavedBuffers===void 0&&(e.interleavedBuffers={}),e.interleavedBuffers[this.data.uuid]===void 0&&(e.interleavedBuffers[this.data.uuid]=this.data.toJSON(e)),{isInterleavedBufferAttribute:!0,itemSize:this.itemSize,data:this.data.uuid,offset:this.offset,normalized:this.normalized}}}class Hs extends ms{constructor(e){super(),this.isSpriteMaterial=!0,this.type="SpriteMaterial",this.color=new nt(16777215),this.map=null,this.alphaMap=null,this.rotation=0,this.sizeAttenuation=!0,this.transparent=!0,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.alphaMap=e.alphaMap,this.rotation=e.rotation,this.sizeAttenuation=e.sizeAttenuation,this.fog=e.fog,this}}let xr;const ma=new H,yr=new H,Mr=new H,Sr=new qe,ga=new qe,rp=new Bt,_o=new H,_a=new H,vo=new H,md=new qe,rc=new qe,gd=new qe;class ap extends Qt{constructor(e=new Hs){if(super(),this.isSprite=!0,this.type="Sprite",xr===void 0){xr=new Xt;const t=new Float32Array([-.5,-.5,0,0,0,.5,-.5,0,1,0,.5,.5,0,1,1,-.5,.5,0,0,1]),n=new Xy(t,5);xr.setIndex([0,1,2,0,2,3]),xr.setAttribute("position",new $o(n,3,0,!1)),xr.setAttribute("uv",new $o(n,2,3,!1))}this.geometry=xr,this.material=e,this.center=new qe(.5,.5)}raycast(e,t){e.camera===null&&console.error('THREE.Sprite: "Raycaster.camera" needs to be set in order to raycast against sprites.'),yr.setFromMatrixScale(this.matrixWorld),rp.copy(e.camera.matrixWorld),this.modelViewMatrix.multiplyMatrices(e.camera.matrixWorldInverse,this.matrixWorld),Mr.setFromMatrixPosition(this.modelViewMatrix),e.camera.isPerspectiveCamera&&this.material.sizeAttenuation===!1&&yr.multiplyScalar(-Mr.z);const n=this.material.rotation;let s,r;n!==0&&(r=Math.cos(n),s=Math.sin(n));const a=this.center;xo(_o.set(-.5,-.5,0),Mr,a,yr,s,r),xo(_a.set(.5,-.5,0),Mr,a,yr,s,r),xo(vo.set(.5,.5,0),Mr,a,yr,s,r),md.set(0,0),rc.set(1,0),gd.set(1,1);let o=e.ray.intersectTriangle(_o,_a,vo,!1,ma);if(o===null&&(xo(_a.set(-.5,.5,0),Mr,a,yr,s,r),rc.set(0,1),o=e.ray.intersectTriangle(_o,vo,_a,!1,ma),o===null))return;const l=e.ray.origin.distanceTo(ma);l<e.near||l>e.far||t.push({distance:l,point:ma.clone(),uv:jn.getInterpolation(ma,_o,_a,vo,md,rc,gd,new qe),face:null,object:this})}copy(e,t){return super.copy(e,t),e.center!==void 0&&this.center.copy(e.center),this.material=e.material,this}}function xo(i,e,t,n,s,r){Sr.subVectors(i,t).addScalar(.5).multiply(n),s!==void 0?(ga.x=r*Sr.x-s*Sr.y,ga.y=s*Sr.x+r*Sr.y):ga.copy(Sr),i.copy(e),i.x+=ga.x,i.y+=ga.y,i.applyMatrix4(rp)}class Hi extends ms{constructor(e){super(),this.isLineBasicMaterial=!0,this.type="LineBasicMaterial",this.color=new nt(16777215),this.map=null,this.linewidth=1,this.linecap="round",this.linejoin="round",this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.linewidth=e.linewidth,this.linecap=e.linecap,this.linejoin=e.linejoin,this.fog=e.fog,this}}const Yo=new H,jo=new H,_d=new Bt,va=new Ba,yo=new Oa,ac=new H,vd=new H;class Ko extends Qt{constructor(e=new Xt,t=new Hi){super(),this.isLine=!0,this.type="Line",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}computeLineDistances(){const e=this.geometry;if(e.index===null){const t=e.attributes.position,n=[0];for(let s=1,r=t.count;s<r;s++)Yo.fromBufferAttribute(t,s-1),jo.fromBufferAttribute(t,s),n[s]=n[s-1],n[s]+=Yo.distanceTo(jo);e.setAttribute("lineDistance",new qt(n,1))}else console.warn("THREE.Line.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.");return this}raycast(e,t){const n=this.geometry,s=this.matrixWorld,r=e.params.Line.threshold,a=n.drawRange;if(n.boundingSphere===null&&n.computeBoundingSphere(),yo.copy(n.boundingSphere),yo.applyMatrix4(s),yo.radius+=r,e.ray.intersectsSphere(yo)===!1)return;_d.copy(s).invert(),va.copy(e.ray).applyMatrix4(_d);const o=r/((this.scale.x+this.scale.y+this.scale.z)/3),l=o*o,c=this.isLineSegments?2:1,h=n.index,d=n.attributes.position;if(h!==null){const f=Math.max(0,a.start),g=Math.min(h.count,a.start+a.count);for(let _=f,m=g-1;_<m;_+=c){const p=h.getX(_),S=h.getX(_+1),y=Mo(this,e,va,l,p,S);y&&t.push(y)}if(this.isLineLoop){const _=h.getX(g-1),m=h.getX(f),p=Mo(this,e,va,l,_,m);p&&t.push(p)}}else{const f=Math.max(0,a.start),g=Math.min(d.count,a.start+a.count);for(let _=f,m=g-1;_<m;_+=c){const p=Mo(this,e,va,l,_,_+1);p&&t.push(p)}if(this.isLineLoop){const _=Mo(this,e,va,l,g-1,f);_&&t.push(_)}}}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const s=t[n[0]];if(s!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let r=0,a=s.length;r<a;r++){const o=s[r].name||String(r);this.morphTargetInfluences.push(0),this.morphTargetDictionary[o]=r}}}}}function Mo(i,e,t,n,s,r){const a=i.geometry.attributes.position;if(Yo.fromBufferAttribute(a,s),jo.fromBufferAttribute(a,r),t.distanceSqToSegment(Yo,jo,ac,vd)>n)return;ac.applyMatrix4(i.matrixWorld);const l=e.ray.origin.distanceTo(ac);if(!(l<e.near||l>e.far))return{distance:l,point:vd.clone().applyMatrix4(i.matrixWorld),index:s,face:null,faceIndex:null,object:i}}const xd=new H,yd=new H;class Fr extends Ko{constructor(e,t){super(e,t),this.isLineSegments=!0,this.type="LineSegments"}computeLineDistances(){const e=this.geometry;if(e.index===null){const t=e.attributes.position,n=[];for(let s=0,r=t.count;s<r;s+=2)xd.fromBufferAttribute(t,s),yd.fromBufferAttribute(t,s+1),n[s]=s===0?0:n[s-1],n[s+1]=n[s]+xd.distanceTo(yd);e.setAttribute("lineDistance",new qt(n,1))}else console.warn("THREE.LineSegments.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.");return this}}class Rh extends ms{constructor(e){super(),this.isPointsMaterial=!0,this.type="PointsMaterial",this.color=new nt(16777215),this.map=null,this.alphaMap=null,this.size=1,this.sizeAttenuation=!0,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.alphaMap=e.alphaMap,this.size=e.size,this.sizeAttenuation=e.sizeAttenuation,this.fog=e.fog,this}}const Md=new Bt,th=new Ba,So=new Oa,bo=new H;class op extends Qt{constructor(e=new Xt,t=new Rh){super(),this.isPoints=!0,this.type="Points",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}raycast(e,t){const n=this.geometry,s=this.matrixWorld,r=e.params.Points.threshold,a=n.drawRange;if(n.boundingSphere===null&&n.computeBoundingSphere(),So.copy(n.boundingSphere),So.applyMatrix4(s),So.radius+=r,e.ray.intersectsSphere(So)===!1)return;Md.copy(s).invert(),th.copy(e.ray).applyMatrix4(Md);const o=r/((this.scale.x+this.scale.y+this.scale.z)/3),l=o*o,c=n.index,u=n.attributes.position;if(c!==null){const d=Math.max(0,a.start),f=Math.min(c.count,a.start+a.count);for(let g=d,_=f;g<_;g++){const m=c.getX(g);bo.fromBufferAttribute(u,m),Sd(bo,m,l,s,e,t,this)}}else{const d=Math.max(0,a.start),f=Math.min(u.count,a.start+a.count);for(let g=d,_=f;g<_;g++)bo.fromBufferAttribute(u,g),Sd(bo,g,l,s,e,t,this)}}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const s=t[n[0]];if(s!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let r=0,a=s.length;r<a;r++){const o=s[r].name||String(r);this.morphTargetInfluences.push(0),this.morphTargetDictionary[o]=r}}}}}function Sd(i,e,t,n,s,r,a){const o=th.distanceSqToPoint(i);if(o<t){const l=new H;th.closestPointToPoint(i,l),l.applyMatrix4(n);const c=s.ray.origin.distanceTo(l);if(c<s.near||c>s.far)return;r.push({distance:c,distanceToRay:Math.sqrt(o),point:l,index:e,face:null,object:a})}}class Ch extends Ln{constructor(e,t,n,s,r,a,o,l,c){super(e,t,n,s,r,a,o,l,c),this.isCanvasTexture=!0,this.needsUpdate=!0}}const Eo=new H,wo=new H,oc=new H,To=new jn;class qy extends Xt{constructor(e=null,t=1){if(super(),this.type="EdgesGeometry",this.parameters={geometry:e,thresholdAngle:t},e!==null){const s=Math.pow(10,4),r=Math.cos(Lr*t),a=e.getIndex(),o=e.getAttribute("position"),l=a?a.count:o.count,c=[0,0,0],h=["a","b","c"],u=new Array(3),d={},f=[];for(let g=0;g<l;g+=3){a?(c[0]=a.getX(g),c[1]=a.getX(g+1),c[2]=a.getX(g+2)):(c[0]=g,c[1]=g+1,c[2]=g+2);const{a:_,b:m,c:p}=To;if(_.fromBufferAttribute(o,c[0]),m.fromBufferAttribute(o,c[1]),p.fromBufferAttribute(o,c[2]),To.getNormal(oc),u[0]=`${Math.round(_.x*s)},${Math.round(_.y*s)},${Math.round(_.z*s)}`,u[1]=`${Math.round(m.x*s)},${Math.round(m.y*s)},${Math.round(m.z*s)}`,u[2]=`${Math.round(p.x*s)},${Math.round(p.y*s)},${Math.round(p.z*s)}`,!(u[0]===u[1]||u[1]===u[2]||u[2]===u[0]))for(let S=0;S<3;S++){const y=(S+1)%3,w=u[S],O=u[y],A=To[h[S]],C=To[h[y]],F=`${w}_${O}`,b=`${O}_${w}`;b in d&&d[b]?(oc.dot(d[b].normal)<=r&&(f.push(A.x,A.y,A.z),f.push(C.x,C.y,C.z)),d[b]=null):F in d||(d[F]={index0:c[S],index1:c[y],normal:oc.clone()})}}for(const g in d)if(d[g]){const{index0:_,index1:m}=d[g];Eo.fromBufferAttribute(o,_),wo.fromBufferAttribute(o,m),f.push(Eo.x,Eo.y,Eo.z),f.push(wo.x,wo.y,wo.z)}this.setAttribute("position",new qt(f,3))}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}}class Ph extends Xt{constructor(e=.5,t=1,n=32,s=1,r=0,a=Math.PI*2){super(),this.type="RingGeometry",this.parameters={innerRadius:e,outerRadius:t,thetaSegments:n,phiSegments:s,thetaStart:r,thetaLength:a},n=Math.max(3,n),s=Math.max(1,s);const o=[],l=[],c=[],h=[];let u=e;const d=(t-e)/s,f=new H,g=new qe;for(let _=0;_<=s;_++){for(let m=0;m<=n;m++){const p=r+m/n*a;f.x=u*Math.cos(p),f.y=u*Math.sin(p),l.push(f.x,f.y,f.z),c.push(0,0,1),g.x=(f.x/t+1)/2,g.y=(f.y/t+1)/2,h.push(g.x,g.y)}u+=d}for(let _=0;_<s;_++){const m=_*(n+1);for(let p=0;p<n;p++){const S=p+m,y=S,w=S+n+1,O=S+n+2,A=S+1;o.push(y,w,A),o.push(w,O,A)}}this.setIndex(o),this.setAttribute("position",new qt(l,3)),this.setAttribute("normal",new qt(c,3)),this.setAttribute("uv",new qt(h,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Ph(e.innerRadius,e.outerRadius,e.thetaSegments,e.phiSegments,e.thetaStart,e.thetaLength)}}class Bo extends ms{constructor(e){super(),this.isMeshStandardMaterial=!0,this.defines={STANDARD:""},this.type="MeshStandardMaterial",this.color=new nt(16777215),this.roughness=1,this.metalness=0,this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.emissive=new nt(0),this.emissiveIntensity=1,this.emissiveMap=null,this.bumpMap=null,this.bumpScale=1,this.normalMap=null,this.normalMapType=Hf,this.normalScale=new qe(1,1),this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.roughnessMap=null,this.metalnessMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new Si,this.envMapIntensity=1,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.flatShading=!1,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.defines={STANDARD:""},this.color.copy(e.color),this.roughness=e.roughness,this.metalness=e.metalness,this.map=e.map,this.lightMap=e.lightMap,this.lightMapIntensity=e.lightMapIntensity,this.aoMap=e.aoMap,this.aoMapIntensity=e.aoMapIntensity,this.emissive.copy(e.emissive),this.emissiveMap=e.emissiveMap,this.emissiveIntensity=e.emissiveIntensity,this.bumpMap=e.bumpMap,this.bumpScale=e.bumpScale,this.normalMap=e.normalMap,this.normalMapType=e.normalMapType,this.normalScale.copy(e.normalScale),this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this.roughnessMap=e.roughnessMap,this.metalnessMap=e.metalnessMap,this.alphaMap=e.alphaMap,this.envMap=e.envMap,this.envMapRotation.copy(e.envMapRotation),this.envMapIntensity=e.envMapIntensity,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.wireframeLinecap=e.wireframeLinecap,this.wireframeLinejoin=e.wireframeLinejoin,this.flatShading=e.flatShading,this.fog=e.fog,this}}class lp extends Hi{constructor(e){super(),this.isLineDashedMaterial=!0,this.type="LineDashedMaterial",this.scale=1,this.dashSize=3,this.gapSize=1,this.setValues(e)}copy(e){return super.copy(e),this.scale=e.scale,this.dashSize=e.dashSize,this.gapSize=e.gapSize,this}}class Lh extends Qt{constructor(e,t=1){super(),this.isLight=!0,this.type="Light",this.color=new nt(e),this.intensity=t}dispose(){}copy(e,t){return super.copy(e,t),this.color.copy(e.color),this.intensity=e.intensity,this}toJSON(e){const t=super.toJSON(e);return t.object.color=this.color.getHex(),t.object.intensity=this.intensity,this.groundColor!==void 0&&(t.object.groundColor=this.groundColor.getHex()),this.distance!==void 0&&(t.object.distance=this.distance),this.angle!==void 0&&(t.object.angle=this.angle),this.decay!==void 0&&(t.object.decay=this.decay),this.penumbra!==void 0&&(t.object.penumbra=this.penumbra),this.shadow!==void 0&&(t.object.shadow=this.shadow.toJSON()),this.target!==void 0&&(t.object.target=this.target.uuid),t}}class $y extends Lh{constructor(e,t,n){super(e,n),this.isHemisphereLight=!0,this.type="HemisphereLight",this.position.copy(Qt.DEFAULT_UP),this.updateMatrix(),this.groundColor=new nt(t)}copy(e,t){return super.copy(e,t),this.groundColor.copy(e.groundColor),this}}const lc=new Bt,bd=new H,Ed=new H;class Yy{constructor(e){this.camera=e,this.intensity=1,this.bias=0,this.normalBias=0,this.radius=1,this.blurSamples=8,this.mapSize=new qe(512,512),this.map=null,this.mapPass=null,this.matrix=new Bt,this.autoUpdate=!0,this.needsUpdate=!1,this._frustum=new Eh,this._frameExtents=new qe(1,1),this._viewportCount=1,this._viewports=[new nn(0,0,1,1)]}getViewportCount(){return this._viewportCount}getFrustum(){return this._frustum}updateMatrices(e){const t=this.camera,n=this.matrix;bd.setFromMatrixPosition(e.matrixWorld),t.position.copy(bd),Ed.setFromMatrixPosition(e.target.matrixWorld),t.lookAt(Ed),t.updateMatrixWorld(),lc.multiplyMatrices(t.projectionMatrix,t.matrixWorldInverse),this._frustum.setFromProjectionMatrix(lc),n.set(.5,0,0,.5,0,.5,0,.5,0,0,.5,.5,0,0,0,1),n.multiply(lc)}getViewport(e){return this._viewports[e]}getFrameExtents(){return this._frameExtents}dispose(){this.map&&this.map.dispose(),this.mapPass&&this.mapPass.dispose()}copy(e){return this.camera=e.camera.clone(),this.intensity=e.intensity,this.bias=e.bias,this.radius=e.radius,this.mapSize.copy(e.mapSize),this}clone(){return new this.constructor().copy(this)}toJSON(){const e={};return this.intensity!==1&&(e.intensity=this.intensity),this.bias!==0&&(e.bias=this.bias),this.normalBias!==0&&(e.normalBias=this.normalBias),this.radius!==1&&(e.radius=this.radius),(this.mapSize.x!==512||this.mapSize.y!==512)&&(e.mapSize=this.mapSize.toArray()),e.camera=this.camera.toJSON(!1).object,delete e.camera.matrix,e}}class jy extends Yy{constructor(){super(new Nr(-5,5,5,-5,.5,500)),this.isDirectionalLightShadow=!0}}class Ky extends Lh{constructor(e,t){super(e,t),this.isDirectionalLight=!0,this.type="DirectionalLight",this.position.copy(Qt.DEFAULT_UP),this.updateMatrix(),this.target=new Qt,this.shadow=new jy}dispose(){this.shadow.dispose()}copy(e){return super.copy(e),this.target=e.target.clone(),this.shadow=e.shadow.clone(),this}}class Zy extends Lh{constructor(e,t){super(e,t),this.isAmbientLight=!0,this.type="AmbientLight"}}const wd=new Bt;class Jy{constructor(e,t,n=0,s=1/0){this.ray=new Ba(e,t),this.near=n,this.far=s,this.camera=null,this.layers=new bh,this.params={Mesh:{},Line:{threshold:1},LOD:{},Points:{threshold:1},Sprite:{}}}set(e,t){this.ray.set(e,t)}setFromCamera(e,t){t.isPerspectiveCamera?(this.ray.origin.setFromMatrixPosition(t.matrixWorld),this.ray.direction.set(e.x,e.y,.5).unproject(t).sub(this.ray.origin).normalize(),this.camera=t):t.isOrthographicCamera?(this.ray.origin.set(e.x,e.y,(t.near+t.far)/(t.near-t.far)).unproject(t),this.ray.direction.set(0,0,-1).transformDirection(t.matrixWorld),this.camera=t):console.error("THREE.Raycaster: Unsupported camera type: "+t.type)}setFromXRController(e){return wd.identity().extractRotation(e.matrixWorld),this.ray.origin.setFromMatrixPosition(e.matrixWorld),this.ray.direction.set(0,0,-1).applyMatrix4(wd),this}intersectObject(e,t=!0,n=[]){return nh(e,this,n,t),n.sort(Td),n}intersectObjects(e,t=!0,n=[]){for(let s=0,r=e.length;s<r;s++)nh(e[s],this,n,t);return n.sort(Td),n}}function Td(i,e){return i.distance-e.distance}function nh(i,e,t,n){let s=!0;if(i.layers.test(e.layers)&&i.raycast(e,t)===!1&&(s=!1),s===!0&&n===!0){const r=i.children;for(let a=0,o=r.length;a<o;a++)nh(r[a],e,t,!0)}}class Ad{constructor(e=1,t=0,n=0){return this.radius=e,this.phi=t,this.theta=n,this}set(e,t,n){return this.radius=e,this.phi=t,this.theta=n,this}copy(e){return this.radius=e.radius,this.phi=e.phi,this.theta=e.theta,this}makeSafe(){return this.phi=Math.max(1e-6,Math.min(Math.PI-1e-6,this.phi)),this}setFromVector3(e){return this.setFromCartesianCoords(e.x,e.y,e.z)}setFromCartesianCoords(e,t,n){return this.radius=Math.sqrt(e*e+t*t+n*n),this.radius===0?(this.theta=0,this.phi=0):(this.theta=Math.atan2(e,n),this.phi=Math.acos(Sn(t/this.radius,-1,1))),this}clone(){return new this.constructor().copy(this)}}class Qy extends Fr{constructor(e=10,t=10,n=4473924,s=8947848){n=new nt(n),s=new nt(s);const r=t/2,a=e/t,o=e/2,l=[],c=[];for(let d=0,f=0,g=-o;d<=t;d++,g+=a){l.push(-o,0,g,o,0,g),l.push(g,0,-o,g,0,o);const _=d===r?n:s;_.toArray(c,f),f+=3,_.toArray(c,f),f+=3,_.toArray(c,f),f+=3,_.toArray(c,f),f+=3}const h=new Xt;h.setAttribute("position",new qt(l,3)),h.setAttribute("color",new qt(c,3));const u=new Hi({vertexColors:!0,toneMapped:!1});super(h,u),this.type="GridHelper"}dispose(){this.geometry.dispose(),this.material.dispose()}}typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("register",{detail:{revision:ph}}));typeof window<"u"&&(window.__THREE__?console.warn("WARNING: Multiple instances of Three.js being imported."):window.__THREE__=ph);var eM=Object.defineProperty,tM=(i,e,t)=>e in i?eM(i,e,{enumerable:!0,configurable:!0,writable:!0,value:t}):i[e]=t,nM=(i,e,t)=>(tM(i,e+"",t),t);class iM{constructor(){nM(this,"_listeners")}addEventListener(e,t){this._listeners===void 0&&(this._listeners={});const n=this._listeners;n[e]===void 0&&(n[e]=[]),n[e].indexOf(t)===-1&&n[e].push(t)}hasEventListener(e,t){if(this._listeners===void 0)return!1;const n=this._listeners;return n[e]!==void 0&&n[e].indexOf(t)!==-1}removeEventListener(e,t){if(this._listeners===void 0)return;const s=this._listeners[e];if(s!==void 0){const r=s.indexOf(t);r!==-1&&s.splice(r,1)}}dispatchEvent(e){if(this._listeners===void 0)return;const n=this._listeners[e.type];if(n!==void 0){e.target=this;const s=n.slice(0);for(let r=0,a=s.length;r<a;r++)s[r].call(this,e);e.target=null}}}var sM=Object.defineProperty,rM=(i,e,t)=>e in i?sM(i,e,{enumerable:!0,configurable:!0,writable:!0,value:t}):i[e]=t,Ye=(i,e,t)=>(rM(i,typeof e!="symbol"?e+"":e,t),t);const Ao=new Ba,Rd=new ss,aM=Math.cos(70*(Math.PI/180)),Cd=(i,e)=>(i%e+e)%e;class oM extends iM{constructor(e,t){super(),Ye(this,"object"),Ye(this,"domElement"),Ye(this,"enabled",!0),Ye(this,"target",new H),Ye(this,"minDistance",0),Ye(this,"maxDistance",1/0),Ye(this,"minZoom",0),Ye(this,"maxZoom",1/0),Ye(this,"minPolarAngle",0),Ye(this,"maxPolarAngle",Math.PI),Ye(this,"minAzimuthAngle",-1/0),Ye(this,"maxAzimuthAngle",1/0),Ye(this,"enableDamping",!1),Ye(this,"dampingFactor",.05),Ye(this,"enableZoom",!0),Ye(this,"zoomSpeed",1),Ye(this,"enableRotate",!0),Ye(this,"rotateSpeed",1),Ye(this,"enablePan",!0),Ye(this,"panSpeed",1),Ye(this,"screenSpacePanning",!0),Ye(this,"keyPanSpeed",7),Ye(this,"zoomToCursor",!1),Ye(this,"autoRotate",!1),Ye(this,"autoRotateSpeed",2),Ye(this,"reverseOrbit",!1),Ye(this,"reverseHorizontalOrbit",!1),Ye(this,"reverseVerticalOrbit",!1),Ye(this,"keys",{LEFT:"ArrowLeft",UP:"ArrowUp",RIGHT:"ArrowRight",BOTTOM:"ArrowDown"}),Ye(this,"mouseButtons",{LEFT:er.ROTATE,MIDDLE:er.DOLLY,RIGHT:er.PAN}),Ye(this,"touches",{ONE:tr.ROTATE,TWO:tr.DOLLY_PAN}),Ye(this,"target0"),Ye(this,"position0"),Ye(this,"zoom0"),Ye(this,"_domElementKeyEvents",null),Ye(this,"getPolarAngle"),Ye(this,"getAzimuthalAngle"),Ye(this,"setPolarAngle"),Ye(this,"setAzimuthalAngle"),Ye(this,"getDistance"),Ye(this,"getZoomScale"),Ye(this,"listenToKeyEvents"),Ye(this,"stopListenToKeyEvents"),Ye(this,"saveState"),Ye(this,"reset"),Ye(this,"update"),Ye(this,"connect"),Ye(this,"dispose"),Ye(this,"dollyIn"),Ye(this,"dollyOut"),Ye(this,"getScale"),Ye(this,"setScale"),this.object=e,this.domElement=t,this.target0=this.target.clone(),this.position0=this.object.position.clone(),this.zoom0=this.object.zoom,this.getPolarAngle=()=>h.phi,this.getAzimuthalAngle=()=>h.theta,this.setPolarAngle=B=>{let ce=Cd(B,2*Math.PI),I=h.phi;I<0&&(I+=2*Math.PI),ce<0&&(ce+=2*Math.PI);let ae=Math.abs(ce-I);2*Math.PI-ae<ae&&(ce<I?ce+=2*Math.PI:I+=2*Math.PI),u.phi=ce-I,n.update()},this.setAzimuthalAngle=B=>{let ce=Cd(B,2*Math.PI),I=h.theta;I<0&&(I+=2*Math.PI),ce<0&&(ce+=2*Math.PI);let ae=Math.abs(ce-I);2*Math.PI-ae<ae&&(ce<I?ce+=2*Math.PI:I+=2*Math.PI),u.theta=ce-I,n.update()},this.getDistance=()=>n.object.position.distanceTo(n.target),this.listenToKeyEvents=B=>{B.addEventListener("keydown",Ae),this._domElementKeyEvents=B},this.stopListenToKeyEvents=()=>{this._domElementKeyEvents.removeEventListener("keydown",Ae),this._domElementKeyEvents=null},this.saveState=()=>{n.target0.copy(n.target),n.position0.copy(n.object.position),n.zoom0=n.object.zoom},this.reset=()=>{n.target.copy(n.target0),n.object.position.copy(n.position0),n.object.zoom=n.zoom0,n.object.updateProjectionMatrix(),n.dispatchEvent(s),n.update(),l=o.NONE},this.update=(()=>{const B=new H,ce=new H(0,1,0),I=new ks().setFromUnitVectors(e.up,ce),ae=I.clone().invert(),se=new H,re=new ks,ve=2*Math.PI;return function(){const ot=n.object.position;I.setFromUnitVectors(e.up,ce),ae.copy(I).invert(),B.copy(ot).sub(n.target),B.applyQuaternion(I),h.setFromVector3(B),n.autoRotate&&l===o.NONE&&Z(K()),n.enableDamping?(h.theta+=u.theta*n.dampingFactor,h.phi+=u.phi*n.dampingFactor):(h.theta+=u.theta,h.phi+=u.phi);let _t=n.minAzimuthAngle,wt=n.maxAzimuthAngle;isFinite(_t)&&isFinite(wt)&&(_t<-Math.PI?_t+=ve:_t>Math.PI&&(_t-=ve),wt<-Math.PI?wt+=ve:wt>Math.PI&&(wt-=ve),_t<=wt?h.theta=Math.max(_t,Math.min(wt,h.theta)):h.theta=h.theta>(_t+wt)/2?Math.max(_t,h.theta):Math.min(wt,h.theta)),h.phi=Math.max(n.minPolarAngle,Math.min(n.maxPolarAngle,h.phi)),h.makeSafe(),n.enableDamping===!0?n.target.addScaledVector(f,n.dampingFactor):n.target.add(f),n.zoomToCursor&&b||n.object.isOrthographicCamera?h.radius=ye(h.radius):h.radius=ye(h.radius*d),B.setFromSpherical(h),B.applyQuaternion(ae),ot.copy(n.target).add(B),n.object.matrixAutoUpdate||n.object.updateMatrix(),n.object.lookAt(n.target),n.enableDamping===!0?(u.theta*=1-n.dampingFactor,u.phi*=1-n.dampingFactor,f.multiplyScalar(1-n.dampingFactor)):(u.set(0,0,0),f.set(0,0,0));let lt=!1;if(n.zoomToCursor&&b){let pn=null;if(n.object instanceof bn&&n.object.isPerspectiveCamera){const zt=B.length();pn=ye(zt*d);const kt=zt-pn;n.object.position.addScaledVector(C,kt),n.object.updateMatrixWorld()}else if(n.object.isOrthographicCamera){const zt=new H(F.x,F.y,0);zt.unproject(n.object),n.object.zoom=Math.max(n.minZoom,Math.min(n.maxZoom,n.object.zoom/d)),n.object.updateProjectionMatrix(),lt=!0;const kt=new H(F.x,F.y,0);kt.unproject(n.object),n.object.position.sub(kt).add(zt),n.object.updateMatrixWorld(),pn=B.length()}else console.warn("WARNING: OrbitControls.js encountered an unknown camera type - zoom to cursor disabled."),n.zoomToCursor=!1;pn!==null&&(n.screenSpacePanning?n.target.set(0,0,-1).transformDirection(n.object.matrix).multiplyScalar(pn).add(n.object.position):(Ao.origin.copy(n.object.position),Ao.direction.set(0,0,-1).transformDirection(n.object.matrix),Math.abs(n.object.up.dot(Ao.direction))<aM?e.lookAt(n.target):(Rd.setFromNormalAndCoplanarPoint(n.object.up,n.target),Ao.intersectPlane(Rd,n.target))))}else n.object instanceof Nr&&n.object.isOrthographicCamera&&(lt=d!==1,lt&&(n.object.zoom=Math.max(n.minZoom,Math.min(n.maxZoom,n.object.zoom/d)),n.object.updateProjectionMatrix()));return d=1,b=!1,lt||se.distanceToSquared(n.object.position)>c||8*(1-re.dot(n.object.quaternion))>c?(n.dispatchEvent(s),se.copy(n.object.position),re.copy(n.object.quaternion),lt=!1,!0):!1}})(),this.connect=B=>{n.domElement=B,n.domElement.style.touchAction="none",n.domElement.addEventListener("contextmenu",Te),n.domElement.addEventListener("pointerdown",Q),n.domElement.addEventListener("pointercancel",te),n.domElement.addEventListener("wheel",_e)},this.dispose=()=>{var B,ce,I,ae,se,re;n.domElement&&(n.domElement.style.touchAction="auto"),(B=n.domElement)==null||B.removeEventListener("contextmenu",Te),(ce=n.domElement)==null||ce.removeEventListener("pointerdown",Q),(I=n.domElement)==null||I.removeEventListener("pointercancel",te),(ae=n.domElement)==null||ae.removeEventListener("wheel",_e),(se=n.domElement)==null||se.ownerDocument.removeEventListener("pointermove",le),(re=n.domElement)==null||re.ownerDocument.removeEventListener("pointerup",te),n._domElementKeyEvents!==null&&n._domElementKeyEvents.removeEventListener("keydown",Ae)};const n=this,s={type:"change"},r={type:"start"},a={type:"end"},o={NONE:-1,ROTATE:0,DOLLY:1,PAN:2,TOUCH_ROTATE:3,TOUCH_PAN:4,TOUCH_DOLLY_PAN:5,TOUCH_DOLLY_ROTATE:6};let l=o.NONE;const c=1e-6,h=new Ad,u=new Ad;let d=1;const f=new H,g=new qe,_=new qe,m=new qe,p=new qe,S=new qe,y=new qe,w=new qe,O=new qe,A=new qe,C=new H,F=new qe;let b=!1;const x=[],P={};function K(){return 2*Math.PI/60/60*n.autoRotateSpeed}function k(){return Math.pow(.95,n.zoomSpeed)}function Z(B){n.reverseOrbit||n.reverseHorizontalOrbit?u.theta+=B:u.theta-=B}function q(B){n.reverseOrbit||n.reverseVerticalOrbit?u.phi+=B:u.phi-=B}const ee=(()=>{const B=new H;return function(I,ae){B.setFromMatrixColumn(ae,0),B.multiplyScalar(-I),f.add(B)}})(),Y=(()=>{const B=new H;return function(I,ae){n.screenSpacePanning===!0?B.setFromMatrixColumn(ae,1):(B.setFromMatrixColumn(ae,0),B.crossVectors(n.object.up,B)),B.multiplyScalar(I),f.add(B)}})(),ne=(()=>{const B=new H;return function(I,ae){const se=n.domElement;if(se&&n.object instanceof bn&&n.object.isPerspectiveCamera){const re=n.object.position;B.copy(re).sub(n.target);let ve=B.length();ve*=Math.tan(n.object.fov/2*Math.PI/180),ee(2*I*ve/se.clientHeight,n.object.matrix),Y(2*ae*ve/se.clientHeight,n.object.matrix)}else se&&n.object instanceof Nr&&n.object.isOrthographicCamera?(ee(I*(n.object.right-n.object.left)/n.object.zoom/se.clientWidth,n.object.matrix),Y(ae*(n.object.top-n.object.bottom)/n.object.zoom/se.clientHeight,n.object.matrix)):(console.warn("WARNING: OrbitControls.js encountered an unknown camera type - pan disabled."),n.enablePan=!1)}})();function ge(B){n.object instanceof bn&&n.object.isPerspectiveCamera||n.object instanceof Nr&&n.object.isOrthographicCamera?d=B:(console.warn("WARNING: OrbitControls.js encountered an unknown camera type - dolly/zoom disabled."),n.enableZoom=!1)}function de(B){ge(d/B)}function xe(B){ge(d*B)}function we(B){if(!n.zoomToCursor||!n.domElement)return;b=!0;const ce=n.domElement.getBoundingClientRect(),I=B.clientX-ce.left,ae=B.clientY-ce.top,se=ce.width,re=ce.height;F.x=I/se*2-1,F.y=-(ae/re)*2+1,C.set(F.x,F.y,1).unproject(n.object).sub(n.object.position).normalize()}function ye(B){return Math.max(n.minDistance,Math.min(n.maxDistance,B))}function ie(B){g.set(B.clientX,B.clientY)}function he(B){we(B),w.set(B.clientX,B.clientY)}function Me(B){p.set(B.clientX,B.clientY)}function fe(B){_.set(B.clientX,B.clientY),m.subVectors(_,g).multiplyScalar(n.rotateSpeed);const ce=n.domElement;ce&&(Z(2*Math.PI*m.x/ce.clientHeight),q(2*Math.PI*m.y/ce.clientHeight)),g.copy(_),n.update()}function ze(B){O.set(B.clientX,B.clientY),A.subVectors(O,w),A.y>0?de(k()):A.y<0&&xe(k()),w.copy(O),n.update()}function Ge(B){S.set(B.clientX,B.clientY),y.subVectors(S,p).multiplyScalar(n.panSpeed),ne(y.x,y.y),p.copy(S),n.update()}function Fe(B){we(B),B.deltaY<0?xe(k()):B.deltaY>0&&de(k()),n.update()}function pt(B){let ce=!1;switch(B.code){case n.keys.UP:ne(0,n.keyPanSpeed),ce=!0;break;case n.keys.BOTTOM:ne(0,-n.keyPanSpeed),ce=!0;break;case n.keys.LEFT:ne(n.keyPanSpeed,0),ce=!0;break;case n.keys.RIGHT:ne(-n.keyPanSpeed,0),ce=!0;break}ce&&(B.preventDefault(),n.update())}function N(){if(x.length==1)g.set(x[0].pageX,x[0].pageY);else{const B=.5*(x[0].pageX+x[1].pageX),ce=.5*(x[0].pageY+x[1].pageY);g.set(B,ce)}}function dt(){if(x.length==1)p.set(x[0].pageX,x[0].pageY);else{const B=.5*(x[0].pageX+x[1].pageX),ce=.5*(x[0].pageY+x[1].pageY);p.set(B,ce)}}function st(){const B=x[0].pageX-x[1].pageX,ce=x[0].pageY-x[1].pageY,I=Math.sqrt(B*B+ce*ce);w.set(0,I)}function ct(){n.enableZoom&&st(),n.enablePan&&dt()}function Oe(){n.enableZoom&&st(),n.enableRotate&&N()}function Et(B){if(x.length==1)_.set(B.pageX,B.pageY);else{const I=He(B),ae=.5*(B.pageX+I.x),se=.5*(B.pageY+I.y);_.set(ae,se)}m.subVectors(_,g).multiplyScalar(n.rotateSpeed);const ce=n.domElement;ce&&(Z(2*Math.PI*m.x/ce.clientHeight),q(2*Math.PI*m.y/ce.clientHeight)),g.copy(_)}function $e(B){if(x.length==1)S.set(B.pageX,B.pageY);else{const ce=He(B),I=.5*(B.pageX+ce.x),ae=.5*(B.pageY+ce.y);S.set(I,ae)}y.subVectors(S,p).multiplyScalar(n.panSpeed),ne(y.x,y.y),p.copy(S)}function Xe(B){const ce=He(B),I=B.pageX-ce.x,ae=B.pageY-ce.y,se=Math.sqrt(I*I+ae*ae);O.set(0,se),A.set(0,Math.pow(O.y/w.y,n.zoomSpeed)),de(A.y),w.copy(O)}function D(B){n.enableZoom&&Xe(B),n.enablePan&&$e(B)}function E(B){n.enableZoom&&Xe(B),n.enableRotate&&Et(B)}function Q(B){var ce,I;n.enabled!==!1&&(x.length===0&&((ce=n.domElement)==null||ce.ownerDocument.addEventListener("pointermove",le),(I=n.domElement)==null||I.ownerDocument.addEventListener("pointerup",te)),Ze(B),B.pointerType==="touch"?Ke(B):X(B))}function le(B){n.enabled!==!1&&(B.pointerType==="touch"?me(B):Ee(B))}function te(B){var ce,I,ae;ke(B),x.length===0&&((ce=n.domElement)==null||ce.releasePointerCapture(B.pointerId),(I=n.domElement)==null||I.ownerDocument.removeEventListener("pointermove",le),(ae=n.domElement)==null||ae.ownerDocument.removeEventListener("pointerup",te)),n.dispatchEvent(a),l=o.NONE}function X(B){let ce;switch(B.button){case 0:ce=n.mouseButtons.LEFT;break;case 1:ce=n.mouseButtons.MIDDLE;break;case 2:ce=n.mouseButtons.RIGHT;break;default:ce=-1}switch(ce){case er.DOLLY:if(n.enableZoom===!1)return;he(B),l=o.DOLLY;break;case er.ROTATE:if(B.ctrlKey||B.metaKey||B.shiftKey){if(n.enablePan===!1)return;Me(B),l=o.PAN}else{if(n.enableRotate===!1)return;ie(B),l=o.ROTATE}break;case er.PAN:if(B.ctrlKey||B.metaKey||B.shiftKey){if(n.enableRotate===!1)return;ie(B),l=o.ROTATE}else{if(n.enablePan===!1)return;Me(B),l=o.PAN}break;default:l=o.NONE}l!==o.NONE&&n.dispatchEvent(r)}function Ee(B){if(n.enabled!==!1)switch(l){case o.ROTATE:if(n.enableRotate===!1)return;fe(B);break;case o.DOLLY:if(n.enableZoom===!1)return;ze(B);break;case o.PAN:if(n.enablePan===!1)return;Ge(B);break}}function _e(B){n.enabled===!1||n.enableZoom===!1||l!==o.NONE&&l!==o.ROTATE||(B.preventDefault(),n.dispatchEvent(r),Fe(B),n.dispatchEvent(a))}function Ae(B){n.enabled===!1||n.enablePan===!1||pt(B)}function Ke(B){switch(be(B),x.length){case 1:switch(n.touches.ONE){case tr.ROTATE:if(n.enableRotate===!1)return;N(),l=o.TOUCH_ROTATE;break;case tr.PAN:if(n.enablePan===!1)return;dt(),l=o.TOUCH_PAN;break;default:l=o.NONE}break;case 2:switch(n.touches.TWO){case tr.DOLLY_PAN:if(n.enableZoom===!1&&n.enablePan===!1)return;ct(),l=o.TOUCH_DOLLY_PAN;break;case tr.DOLLY_ROTATE:if(n.enableZoom===!1&&n.enableRotate===!1)return;Oe(),l=o.TOUCH_DOLLY_ROTATE;break;default:l=o.NONE}break;default:l=o.NONE}l!==o.NONE&&n.dispatchEvent(r)}function me(B){switch(be(B),l){case o.TOUCH_ROTATE:if(n.enableRotate===!1)return;Et(B),n.update();break;case o.TOUCH_PAN:if(n.enablePan===!1)return;$e(B),n.update();break;case o.TOUCH_DOLLY_PAN:if(n.enableZoom===!1&&n.enablePan===!1)return;D(B),n.update();break;case o.TOUCH_DOLLY_ROTATE:if(n.enableZoom===!1&&n.enableRotate===!1)return;E(B),n.update();break;default:l=o.NONE}}function Te(B){n.enabled!==!1&&B.preventDefault()}function Ze(B){x.push(B)}function ke(B){delete P[B.pointerId];for(let ce=0;ce<x.length;ce++)if(x[ce].pointerId==B.pointerId){x.splice(ce,1);return}}function be(B){let ce=P[B.pointerId];ce===void 0&&(ce=new qe,P[B.pointerId]=ce),ce.set(B.pageX,B.pageY)}function He(B){const ce=B.pointerId===x[0].pointerId?x[1]:x[0];return P[ce.pointerId]}this.dollyIn=(B=k())=>{xe(B),n.update()},this.dollyOut=(B=k())=>{de(B),n.update()},this.getScale=()=>d,this.setScale=B=>{ge(B),n.update()},this.getZoomScale=()=>k(),t!==void 0&&this.connect(t),this.update()}}class lM{constructor(){U(this,"handlers",new Map);U(this,"onceHandlers",new Map);U(this,"messageBuffer",new Map)}register(e,t){if(!this.handlers.has(e)){this.handlers.set(e,new Set);const n=this.messageBuffer.get(e);n&&(n.forEach(s=>Promise.resolve(t(s))),this.messageBuffer.delete(e))}return this.handlers.get(e).add(t),()=>this.unregister(e,t)}once(e,t){return this.onceHandlers.has(e)||this.onceHandlers.set(e,new Set),this.onceHandlers.get(e).add(t),()=>this.unregisterOnce(e,t)}unregister(e,t){var n;(n=this.handlers.get(e))==null||n.delete(t)}unregisterOnce(e,t){var n;(n=this.onceHandlers.get(e))==null||n.delete(t)}buffer(e){const{type:t}=e;this.messageBuffer.has(t)||this.messageBuffer.set(t,[]),this.messageBuffer.get(t).push(e)}async dispatch(e){const{type:t,...n}=e,s=this.handlers.get(t);if(s&&s.size>0){await Promise.all(Array.from(s).map(a=>Promise.resolve(a(n))));return}const r=this.onceHandlers.get(t);if(r&&r.size>0){await Promise.all(Array.from(r).map(a=>Promise.resolve(a(n)))),this.onceHandlers.delete(t);return}this.buffer(e)}clear(){this.handlers.clear(),this.onceHandlers.clear(),this.messageBuffer.clear()}getBuffered(e){return this.messageBuffer.get(e)??[]}hasHandlers(e){var t;return(((t=this.handlers.get(e))==null?void 0:t.size)??0)>0}}class cM{constructor(e,t){U(this,"ws",null);U(this,"url");U(this,"router");U(this,"reconnectDelay",1e3);U(this,"maxReconnectDelay",3e4);U(this,"reconnectAttempts",0);U(this,"shouldReconnect",!0);U(this,"state","disconnected");U(this,"stateListeners",new Set);U(this,"messageQueue",[]);this.url=e,this.router=t}get connectionState(){return this.state}onStateChange(e){return this.stateListeners.add(e),e(this.state),()=>this.stateListeners.delete(e)}setState(e){this.state!==e&&(this.state=e,this.stateListeners.forEach(t=>t(e)))}connect(){var n;if(((n=this.ws)==null?void 0:n.readyState)===WebSocket.OPEN||this.state==="connecting")return;this.setState("connecting");const t=`${window.location.protocol==="https:"?"wss:":"ws:"}//${window.location.host}${this.url}`;this.ws=new WebSocket(t),this.ws.binaryType="arraybuffer",this.ws.onopen=()=>{console.log("[WS] Connected"),this.reconnectAttempts=0,this.reconnectDelay=1e3,this.setState("connected"),this.flushQueue()},this.ws.onmessage=async s=>{try{const r=JSON.parse(s.data);await this.router.dispatch(r)}catch(r){console.error("[WS] Failed to parse message:",r)}},this.ws.onclose=()=>{console.log("[WS] Disconnected"),this.setState("disconnected"),this.shouldReconnect&&this.scheduleReconnect()},this.ws.onerror=s=>{console.error("[WS] Error:",s)}}scheduleReconnect(){if(this.state==="reconnecting")return;this.setState("reconnecting");const e=Math.min(this.reconnectDelay*Math.pow(1.5,this.reconnectAttempts),this.maxReconnectDelay);this.reconnectAttempts++,console.log(`[WS] Reconnecting in ${e}ms (attempt ${this.reconnectAttempts})`),setTimeout(()=>this.connect(),e)}send(e){var t;((t=this.ws)==null?void 0:t.readyState)===WebSocket.OPEN?this.ws.send(JSON.stringify(e)):this.messageQueue.push(e)}flushQueue(){var e;for(;this.messageQueue.length>0&&((e=this.ws)==null?void 0:e.readyState)===WebSocket.OPEN;){const t=this.messageQueue.shift();this.ws.send(JSON.stringify(t))}}disconnect(){var e;this.shouldReconnect=!1,(e=this.ws)==null||e.close(),this.ws=null,this.setState("disconnected")}async waitForConnection(e=1e4){return this.state==="connected"?!0:new Promise(t=>{const n=setTimeout(()=>{s(),t(!1)},e),s=this.onStateChange(r=>{r==="connected"&&(clearTimeout(n),s(),t(!0))})})}get isConnected(){var e;return((e=this.ws)==null?void 0:e.readyState)===WebSocket.OPEN}}const Yt=new lM,Gr=new cM("/ws",Yt);let cp=null;function hM(i){cp=i}function Wr(){return cp}class uM{constructor(){U(this,"components",new Map);U(this,"initialized",!1)}register(e){const t=e.name||e.constructor.name;this.components.has(t)&&console.warn(`[ComponentRegistry] Component "${t}" already registered, replacing`),this.components.set(t,e),this.initialized&&e.init().catch(console.error)}unregister(e){const t=this.components.get(e);t&&(t.destroy().catch(console.error),this.components.delete(e))}async initAll(){this.initialized=!0;for(const[e,t]of this.components)try{await t.init(),console.log(`[ComponentRegistry] Initialized: ${e}`)}catch(n){console.error(`[ComponentRegistry] Failed to initialize ${e}:`,n)}}async destroyAll(){for(const[e,t]of this.components)try{await t.destroy(),console.log(`[ComponentRegistry] Destroyed: ${e}`)}catch(n){console.error(`[ComponentRegistry] Failed to destroy ${e}:`,n)}this.components.clear(),this.initialized=!1}get(e){return this.components.get(e)}list(){return Array.from(this.components.keys())}}const Xi=new uM;typeof window<"u"&&(document.addEventListener("DOMContentLoaded",()=>{Xi.initAll().catch(console.error)}),window.addEventListener("beforeunload",()=>{Xi.destroyAll().catch(console.error)}));const jt={gradient:"#58a6ff",pepita:"#d4a843",random_projections:"#f78166",local_goodness:"#a371f7",thermodynamic_contrast:"#3fb950",contrastive:"#ff7b72",hebbian:"#79c0ff",predictive:"#d2a8ff"},V={bg:"#0a0e14",bg_tertiary:"#1a2330",border:"#2a3a4a",border_bright:"#3a4a5a",text_primary:"#e8ecf0",text_secondary:"#8b98a8",text_muted:"#5a6a7a",gradient:"#58a6ff",measured:"#d4a843",legal_unmeasured:"#58a6ff",void:"#f85149",pareto:"#e8ecf0",chance_line:"#f85149",gpu:"#58a6ff",cpu:"#3fb950",memory:"#d29922",ok:"#3fb950",warn:"#d29922",error:"#f85149",passed:"#3fb950",insufficient:"#d29922",rejected:"#f85149",promoted:"#a371f7",ramp_low:"#1f3a5f",ramp_mid:"#58a6ff",ramp_high:"#d4a843"};class dM{constructor(){U(this,"metricsByRun",new Map);U(this,"selectedRunId",null);U(this,"chosenByReader",!1);U(this,"listeners",[])}observe(e,t){this.metricsByRun.set(e,t),this.chosenByReader||(this.selectedRunId=this.newestRunId()),this.notify()}select(e){this.chosenByReader=!0,this.selectedRunId=e,this.notify()}get selectedId(){return this.selectedRunId}get selected(){return this.selectedRunId?this.metricsByRun.get(this.selectedRunId)??null:null}get runs(){return Array.from(this.metricsByRun.entries())}onChange(e){this.listeners.push(e)}notify(){this.listeners.forEach(e=>e(this.selectedRunId,this.selected))}newestRunId(){let e=null,t=-1/0;if(this.metricsByRun.forEach((s,r)=>{var l;const a=(l=s.run)==null?void 0:l.started_at,o=a?Date.parse(a):Number.NaN;Number.isNaN(o)||o>=t&&(t=o,e=r)}),e)return e;const n=this.metricsByRun.keys().next();return n.done?null:n.value}}const qn=new dM,fM={substrate:{display_name:"Substrate",description:"Physical or computational substrate",primitives:[{name:"digital",summary:"Digital substrate: exact arithmetic, full precision",available:!0},{name:"analog",summary:"Analog substrate: continuous-valued physical state",available:!0},{name:"memristive",summary:"Memristive substrate: conductance, IR-drop, noise",available:!0},{name:"neuromorphic",summary:"Neuromorphic substrate: asynchronous spike events",available:!0},{name:"optical",summary:"Photonic substrate: phase/amplitude modulation",available:!0},{name:"quantum",summary:"Quantum substrate: unitary gate simulation",available:!0},{name:"complex",summary:"Complex-valued substrate",available:!0},{name:"sparse",summary:"Sparse substrate: sparsity-masked state",available:!0},{name:"ternary",summary:"Ternary substrate: weights in {-alpha, 0, +alpha}",available:!0}]},geometry:{display_name:"Geometry",description:"Network architecture and connectivity",primitives:[{name:"feedforward",summary:"Feedforward DAG (MLP/CNN)",available:!0},{name:"recurrent",summary:"Recurrent attractor (Hopfield/EqProp)",available:!0},{name:"causal_transformer",summary:"Causal transformer with KV cache",available:!0},{name:"tile",summary:"TileNet modular tile mesh",available:!0},{name:"tile_mesh",summary:"TileNet mesh topology",available:!0},{name:"conv",summary:"Convolutional geometry",available:!0},{name:"graph",summary:"Arbitrary node-edge fabric (FabricPC)",available:!0},{name:"attention",summary:"Attention geometry",available:!0},{name:"spatial_lattice",summary:"3-D spatial lattice (neural_cube)",available:!0},{name:"nca",summary:"Neural cellular automaton fabric",available:!0},{name:"ntm",summary:"Neural Turing Machine tape",available:!0}]},dynamics:{display_name:"Dynamics",description:"State evolution and settling",primitives:[{name:"energy_minimization",summary:"Equilibrium propagation energy minimization",available:!0},{name:"predictive_settling",summary:"Predictive coding settling",available:!0},{name:"error_predictive_coding",summary:"Error predictive coding",available:!0},{name:"spike_integration",summary:"LIF/Izhikevich spike integration",available:!0},{name:"instantaneous",summary:"Instantaneous pass (FF/Backprop)",available:!0},{name:"diffusion",summary:"Continuous-time diffusion settling",available:!0},{name:"lazy",summary:"Lazy/on-demand state dynamics",available:!0},{name:"pc_alm",summary:"Augmented Lagrangian predictive coding",available:!0}]},plasticity:{display_name:"Plasticity",description:"Local learning and adaptation",primitives:[{name:"null",summary:"Null plasticity (5-D slice)",available:!0},{name:"routing",summary:"Routing plasticity: state-dependent gating",available:!0},{name:"fast_weights",summary:"Fast-weight episode-local memory",available:!0},{name:"substrate_coupled",summary:"Physical substrate-coupled plasticity",available:!0},{name:"rule_state",summary:"Rule-state plasticity (Z3)",available:!0},{name:"temporal_psi",summary:"Trace-decayed supervised psi",available:!0},{name:"conflict_adaptive",summary:"Conflict-adaptive psi",available:!0}]},credit:{display_name:"Credit Assignment",description:"How learning signals reach parameters",primitives:[{name:"thermodynamic_contrast",summary:"EqProp free/nudged contrast (Scellier-Bengio)",available:!0},{name:"random_projections",summary:"Fixed random feedback (FA/DFA)",available:!0},{name:"local_goodness",summary:"Forward-Forward / PEPITA goodness",available:!0},{name:"local_contrastive",summary:"Local contrastive credit",available:!0},{name:"temporal_trace",summary:"Hebbian/STDP temporal trace",available:!0},{name:"target_inversion",summary:"Target propagation inversion",available:!0},{name:"homeostatic",summary:"Autonomous Lipschitz scaling",available:!0},{name:"pepita",summary:"PEPITA input-modulation credit",available:!0},{name:"gradient",summary:"Backprop gradient credit (ruler reference)",available:!0},{name:"pc_alm",summary:"PC-ALM primal-dual credit",available:!0}]},update:{display_name:"Update Rule",description:"How parameters are updated",primitives:[{name:"euclidean",summary:"SGD/Adam Euclidean update",available:!0},{name:"adam",summary:"Adam adaptive moment",available:!0},{name:"local_adam",summary:"Local Adam",available:!0},{name:"ortho_adam",summary:"Orthogonal Adam",available:!0},{name:"riemannian_orthogonal",summary:"Riemannian orthogonal update (Muon-family)",available:!0},{name:"muon",summary:"Muon update",available:!0},{name:"lion",summary:"Lion optimizer",available:!0},{name:"spectral_constrained",summary:"Spectral-norm constrained update",available:!0},{name:"mean_norm",summary:"Mean-norm update",available:!0},{name:"elastic_consolidation",summary:"EWC elastic consolidation",available:!0},{name:"natural_gradient",summary:"Natural gradient (Fisher)",available:!0},{name:"role_split",summary:"Role-split update",available:!0}]}},pM={axes:fM},hp=.72,up=.86;function Dh(i,e,t,n,s){const{camera:r,controls:a}=i,o=(s==null?void 0:s.clone())??r.position.clone().sub(a.target);o.lengthSq()===0&&o.set(.4,.5,.8),o.normalize();const l=o.clone().negate(),c=new H().crossVectors(l,new H(0,1,0)).normalize(),h=new H().crossVectors(c,l).normalize(),u=Math.tan((r.fov??60)*Math.PI/360),d=u*(r.aspect||1),f=u*up,g=d*hp;let _=0;[e.x,t.x].forEach(m=>{[e.y,t.y].forEach(p=>{[e.z,t.z].forEach(S=>{const y=new H(m,p,S),w=Math.max(Math.abs(y.dot(c))/g,Math.abs(y.dot(h))/f)+y.dot(o);_=Math.max(_,w)})})}),_*=1.06,n.add(c.clone().multiplyScalar(.28*d*_)).add(h.clone().multiplyScalar(-.14*u*_)),a.target.copy(n),r.position.copy(n).add(o.clone().multiplyScalar(_)),a.update()}const Da=["credit","geometry","dynamics","substrate","plasticity","update"];function Xr(i,e,t){return`${i}|${e}|${t}`}function Fs(i){return i.length===0?0:i.reduce((e,t)=>e+t,0)/i.length}function mM(i){if(i.length<2)return 0;const e=Fs(i),t=i.reduce((n,s)=>n+(s-e)**2,0)/(i.length-1);return Math.sqrt(t)}function gM(i){const e=new Map;for(const t of i)for(const n of t){const s=e.get(n.epoch)??[];s.push(n.val_acc),e.set(n.epoch,s)}return Array.from(e.entries()).sort((t,n)=>t[0]-n[0]).map(([t,n])=>({epoch:t,val_acc:Fs(n)}))}function _M(i,e){const t=new Map;return i.cells.forEach(n=>{t.set(Xr(n.coordinate[e.x],n.coordinate[e.y],n.coordinate[e.z]),n)}),t}function vM(i,e){const t=new Map;return((i==null?void 0:i.records)??[]).forEach((s,r)=>{var h;const a=s==null?void 0:s.coordinate;if(!a)return;const o=Xr(a[e.x],a[e.y],a[e.z]);let l=t.get(o);l||(l={acc:[],walltime:[],params:[],curves:[],pareto:!1,coordinate:{...a},seeds:0},t.set(o,l)),l.seeds+=1;const c=s.payload??{};if(typeof c.val_acc=="number"&&l.acc.push(c.val_acc),typeof c.walltime_s=="number"&&l.walltime.push(c.walltime_s),typeof c.param_count=="number"&&l.params.push(c.param_count),Array.isArray(c.convergence_curve)){const u=c.convergence_curve.filter(d=>typeof(d==null?void 0:d.epoch)=="number"&&typeof(d==null?void 0:d.val_acc)=="number").map(d=>({epoch:d.epoch,val_acc:d.val_acc}));u.length>0&&l.curves.push(u)}(h=i==null?void 0:i.pareto)!=null&&h[r]&&(l.pareto=!0)}),t}function Ih(i,e){const t=Array.from(i.values()),n=ll(t,e);return t.sort((s,r)=>Ia(s,e,n).localeCompare(Ia(r,e,n)))}function ll(i,e){return[e.x,e.y,e.z].filter(n=>new Set(i.map(r=>r.coordinate[n])).size>1)}function Ia(i,e,t){return(t.length>0?t:[e.x,e.y,e.z]).map(s=>i.coordinate[s]??"").join(" · ")}function Pd(i){const e={credit:new Set,geometry:new Set,dynamics:new Set,substrate:new Set,plasticity:new Set,update:new Set};i.forEach(n=>{const s=n==null?void 0:n.coordinate;s&&Da.forEach(r=>{const a=s[r];typeof a=="string"&&a.length>0&&e[r].add(a)})});const t={};return Da.forEach(n=>{t[n]=Array.from(e[n]).sort()}),t}class xM{constructor(){U(this,"runId",null);U(this,"metrics",null);U(this,"axes",{x:"credit",y:"geometry",z:"dynamics"});U(this,"space",null);U(this,"spaceCells",new Map);U(this,"aggregates",new Map);U(this,"values",Pd([]));U(this,"chance",.1);U(this,"requiredSeeds",0);U(this,"gate",null);U(this,"timeline",null);U(this,"account",null);U(this,"flow",null);U(this,"attribution",null);U(this,"spaceRequest","");U(this,"accountRequest","");U(this,"attributionRequest","");U(this,"flowRequest","");U(this,"timelineRun","");U(this,"timelineStale",!0);U(this,"timelineTimer",null);U(this,"listeners",[]);qn.onChange((e,t)=>{this.absorb(e,t)}),Yt.register("pipeline_event",()=>this.scheduleTimeline())}onChange(e){this.listeners.push(e)}notify(e){this.listeners.forEach(t=>t(e))}async absorb(e,t){this.runId=e,this.metrics=t,t&&(typeof t.chance=="number"&&(this.chance=t.chance),typeof t.required_seeds=="number"&&(this.requiredSeeds=t.required_seeds),t.gate&&(this.gate=t.gate,typeof t.gate.required_seeds_per_group=="number"&&(this.requiredSeeds=t.gate.required_seeds_per_group)),this.values=Pd(t.records??[])),this.recomputeEvidence(),await this.syncSpace(),this.syncAccount(),this.syncAttribution(),this.syncTimeline()}setAxes(e){this.axes=e,this.notify("axes"),this.recomputeEvidence(),this.syncSpace()}recomputeEvidence(){this.aggregates=vM(this.metrics,this.axes),this.notify("evidence")}async syncSpace(){if(!this.runId)return;const e=[this.runId,this.axes.x,this.axes.y,this.axes.z,...Da.map(n=>this.values[n].join(","))].join("|");if(e===this.spaceRequest)return;const t=await this.fetchSpace();t&&(this.spaceRequest=e,this.space=t,this.spaceCells=_M(t,this.axes),this.notify("space"))}async fetchSpace(){try{const e=await fetch(`/api/cells/${this.runId}/space`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({axes:[this.axes.x,this.axes.y,this.axes.z]})});return e.ok?await e.json():(console.warn("[StageState] The space was refused",e.status),null)}catch(e){return console.warn("[StageState] The space could not be read",e),null}}async syncAccount(){var n,s;if(!this.runId){this.account=null,this.accountRequest="";return}const e=((s=(n=this.metrics)==null?void 0:n.records)==null?void 0:s.length)??0,t=`${this.runId}|${e}`;if(t!==this.accountRequest)try{const r=await fetch(`/api/runs/${encodeURIComponent(this.runId)}/account`);if(!r.ok){console.warn("[StageState] The account was refused",r.status);return}this.account=await r.json(),this.accountRequest=t,this.notify("evidence")}catch(r){console.warn("[StageState] The account could not be read",r)}}async syncTimeline(){if(!this.runId){this.timeline=null,this.timelineRun="";return}if(!(!this.timelineStale&&this.timelineRun===this.runId))try{const e=await fetch(`/api/events?run_id=${encodeURIComponent(this.runId)}`);if(!e.ok){console.warn("[StageState] The timeline was refused",e.status);return}this.timeline=await e.json(),this.timelineRun=this.runId,this.timelineStale=!1,this.notify("events"),this.syncFlow()}catch(e){console.warn("[StageState] The timeline could not be read",e)}}async syncFlow(){var n;if(!this.runId){this.flow=null,this.flowRequest="";return}const e=((n=this.timeline)==null?void 0:n.events.length)??0,t=`${this.runId}|${e}`;if(t!==this.flowRequest)try{const s=await fetch(`/api/runs/${encodeURIComponent(this.runId)}/flow`);if(!s.ok){console.warn("[StageState] The flow was refused",s.status);return}this.flow=await s.json(),this.flowRequest=t,this.notify("events")}catch(s){console.warn("[StageState] The flow could not be read",s)}}async syncAttribution(){var n,s;if(!this.runId){this.attribution=null,this.attributionRequest="";return}const e=((s=(n=this.metrics)==null?void 0:n.records)==null?void 0:s.length)??0,t=`${this.runId}|${e}`;if(t!==this.attributionRequest)try{const r=await fetch(`/api/runs/${encodeURIComponent(this.runId)}/attribution`);if(!r.ok){console.warn("[StageState] The attribution was refused",r.status);return}this.attribution=await r.json(),this.attributionRequest=t,this.notify("evidence")}catch(r){console.warn("[StageState] The attribution could not be read",r)}}scheduleTimeline(){this.timelineStale=!0,this.timelineTimer===null&&(this.timelineTimer=window.setTimeout(()=>{this.timelineTimer=null,this.syncTimeline()},300))}}const Le=new xM;function Zo(i,e=10){if(i.length<=e)return[i];const t=[];let n="";for(const s of i.split("_")){const r=n?`${n}_${s}`:s;r.length>e&&n?(t.push(n),n=s):n=r}return n&&t.push(n),t}function Mi(i,e,t,n){const s=Zo(i),r=document.createElement("canvas"),a=r.getContext("2d"),o=64,l=72;a.font=`bold ${o}px "JetBrains Mono", monospace`;const c=Math.max(...s.map(_=>a.measureText(_).width))+16;r.width=Math.max(64,Math.ceil(c)),r.height=s.length*l+16,a.font=`bold ${o}px "JetBrains Mono", monospace`,a.fillStyle="#ffffff",a.textAlign="center",a.textBaseline="middle",s.forEach((_,m)=>{a.fillText(_,r.width/2,l*m+l/2+8)});const h=new Ch(r);h.needsUpdate=!0;const u=t.clone();u.map=h,u.transparent=!0;const d=new ap(u),f=r.width/r.height;let g=e*s.length;return n!==void 0&&(g=Math.min(g,n/f)),d.scale.set(g*f,g,1),d}function yM(){const e=document.createElement("canvas");e.width=64,e.height=64;const t=e.getContext("2d");t.fillStyle="#ffffff",t.beginPath(),t.arc(64/2,64/2,64/2-2,0,Math.PI*2),t.fill();const n=new Ch(e);return n.needsUpdate=!0,n}function MM(i,e,t=.14){const s=document.createElement("canvas");s.width=128,s.height=128;const r=s.getContext("2d");r.strokeStyle=i,r.lineWidth=128*t,r.beginPath(),r.arc(128/2,128/2,128/2-r.lineWidth,0,Math.PI*2),r.stroke();const a=new Ch(s);a.needsUpdate=!0;const o=new Hs({map:a,transparent:!0,depthWrite:!1}),l=new ap(o);return l.scale.set(e*2,e*2,1),l}const Ld=pM.axes,SM={measured:"Measured — the run has evidence here",legal:"Legal — a gap nobody has measured",void:"Void — the system refuses this cell"};class bM{constructor(){U(this,"name","DiscoveryMap");U(this,"scene",new Ah);U(this,"camera",new bn);U(this,"renderer",null);U(this,"cells",new Map);U(this,"cellDataMap",new Map);U(this,"cellHeights",new Map);U(this,"xValues",[]);U(this,"yValues",[]);U(this,"zValues",[]);U(this,"cellSize",.8);U(this,"spacing",1.1);U(this,"raycaster",new Jy);U(this,"mouse",new qe);U(this,"selectedCell",null);U(this,"hoveredCell",null);U(this,"legendElement",null);U(this,"readoutElement",null);U(this,"pointerX",0);U(this,"pointerY",0);U(this,"axisLabelMeshes",[]);U(this,"voidMesh",null);U(this,"visible",!1);U(this,"onQueueUpdate",e=>{});U(this,"onCampaignMetrics",e=>{const t=e==null?void 0:e.data;if(!(t!=null&&t.run))return;const n=typeof(e==null?void 0:e.campaign_id)=="string"?e.campaign_id:null;n&&qn.observe(n,t)});Yt.register("queue_update",this.onQueueUpdate),Yt.register("campaign_metrics",this.onCampaignMetrics)}async init(){const e=Wr();e&&(this.scene=e.scene,this.camera=e.camera,this.renderer=e.renderer),this.setupInteraction(),this.createLegend(),this.createReadout(),Le.onChange(()=>this.updateLegend()),qn.onChange(()=>this.updateRunPicker()),console.log("[DiscoveryMap] Initialized")}async destroy(){var e,t;Yt.unregister("queue_update",this.onQueueUpdate),Yt.unregister("campaign_metrics",this.onCampaignMetrics),this.clearGrid(),(e=this.legendElement)==null||e.remove(),(t=this.readoutElement)==null||t.remove()}show(){this.visible=!0,this.applyAxes()}hide(){this.visible=!1,this.clearGrid()}refreshView(e){if(this.visible){if(e==="space"){this.applyAxes();return}e==="evidence"&&this.applyAggregates()}}hasMeasured(){return this.cellDataMap.size>0&&this.cellHeights.size>0}updateLegend(){this.refreshAxisOptions(),this.updateLegendArms(),this.updateLegendAxes()}setupInteraction(){var t;const e=(t=this.renderer)==null?void 0:t.domElement;e&&(this.raycaster.params.Line.threshold=this.cellSize*.2,e.addEventListener("mousemove",n=>{const s=e.getBoundingClientRect();this.mouse.x=(n.clientX-s.left)/s.width*2-1,this.mouse.y=-((n.clientY-s.top)/s.height)*2+1,this.pointerX=n.clientX,this.pointerY=n.clientY}),e.addEventListener("mouseleave",()=>{this.hideReadout()}),e.addEventListener("click",()=>{this.hoveredCell&&this.selectCell(this.hoveredCell)}))}createReadout(){const e=document.getElementById("ui-overlay");e&&(this.readoutElement=document.createElement("div"),this.readoutElement.id="cell-readout",this.readoutElement.style.cssText=`
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
    `,e.appendChild(this.readoutElement))}showReadout(e){const t=this.readoutElement;if(!t)return;const n=document.createElement("div");n.style.color="var(--text-secondary)",n.textContent=Object.entries(e.coordinate).filter(([,l])=>l).map(([l,c])=>`${l}=${c}`).join("  "),t.replaceChildren(n);const s=document.createElement("div");if(s.style.marginTop="4px",s.style.fontWeight="600",s.style.color=e.status==="void"?V.void:e.status==="measured"?V.measured:V.legal_unmeasured,s.textContent=SM[e.status],t.appendChild(s),e.voidReason){const l=document.createElement("div");l.style.marginTop="4px",l.style.color="var(--text-secondary)",l.textContent=e.voidReason,t.appendChild(l)}t.style.display="block";const r=t.getBoundingClientRect(),a=Math.min(this.pointerX+16,window.innerWidth-r.width-8),o=Math.min(this.pointerY+16,window.innerHeight-r.height-8);t.style.left=`${Math.max(8,a)}px`,t.style.top=`${Math.max(8,o)}px`}hideReadout(){this.readoutElement&&(this.readoutElement.style.display="none")}createLegend(){const e=document.getElementById("ui-overlay");e&&(this.legendElement=document.createElement("div"),this.legendElement.id="discovery-legend",this.legendElement.style.cssText=`
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
    `,e.appendChild(this.legendElement),this.createRunPicker(),this.createAxisPicker(),this.updateLegendArms(),this.updateLegendAxes())}createRunPicker(){var t;const e=(t=this.legendElement)==null?void 0:t.querySelector("#legend-run-picker");e&&e.addEventListener("change",()=>{qn.select(e.value||null)})}updateRunPicker(){var a,o,l;const e=(a=this.legendElement)==null?void 0:a.querySelector("#legend-run-picker"),t=(o=this.legendElement)==null?void 0:o.querySelector("#legend-run");if(!e)return;const n=qn.runs;if(e.innerHTML="",n.forEach(([c,h])=>{var g,_;const u=document.createElement("option"),d=((g=h==null?void 0:h.run)==null?void 0:g.profile)??"run",f=((_=h==null?void 0:h.records)==null?void 0:_.length)??0;u.value=c,u.textContent=`${c.slice(0,8)} · ${d} · ${f}`,u.selected=c===qn.selectedId,e.appendChild(u)}),n.length===0){e.disabled=!0,t&&(t.textContent="No run has reported yet.");return}e.disabled=!1;const s=qn.selected;if(!t)return;if(!s){t.textContent="";return}const r=s.run??{};t.textContent=[`run ${(qn.selectedId??"").slice(0,8)}`,r.mode,`${((l=s.records)==null?void 0:l.length)??0} records`].filter(Boolean).join(" · ")}createAxisPicker(){var n;const e=(n=this.legendElement)==null?void 0:n.querySelector("#legend-axis-picker");if(!e)return;["x","y","z"].forEach(s=>{const r=document.createElement("div");r.style.cssText="display: flex; align-items: center; gap: 6px; font-size: 11px;";const a=document.createElement("span");a.textContent=s.toUpperCase(),a.style.cssText="color: var(--text-secondary); width: 12px;";const o=document.createElement("select");o.dataset.dimension=s,o.style.cssText=`
        flex: 1;
        background: var(--bg-tertiary);
        color: var(--text-primary);
        border: 1px solid var(--border);
        border-radius: 4px;
        font-size: 11px;
        padding: 2px 4px;
      `,o.addEventListener("change",()=>{Le.setAxes({...Le.axes,[s]:o.value})}),r.appendChild(a),r.appendChild(o),e.appendChild(r)}),this.refreshAxisOptions()}refreshAxisOptions(){var t;const e=(t=this.legendElement)==null?void 0:t.querySelectorAll("#legend-axis-picker select");e&&e.forEach(n=>{const s=n.dataset.dimension,r=new Set(["x","y","z"].filter(a=>a!==s).map(a=>Le.axes[a]));n.innerHTML="",Da.forEach(a=>{var l;const o=document.createElement("option");o.value=a,o.textContent=((l=Ld[a])==null?void 0:l.display_name)??a,o.disabled=r.has(a),o.selected=Le.axes[s]===a,n.appendChild(o)})})}updateLegendArms(){var n;const e=(n=this.legendElement)==null?void 0:n.querySelector("#legend-arms");if(!e)return;const t=Le.values.credit;if(t.length===0){e.innerHTML='<span style="color: var(--text-muted); font-size: 11px;">No arm measured yet.</span>';return}e.innerHTML=t.map(s=>{const r=jt[s]||V.gradient;return`<span style="display: inline-flex; align-items: center; gap: 4px; padding: 2px 8px; background: ${r}22; border: 1px solid ${r}88; border-radius: 12px; color: ${r}; font-size: 11px;">${s}</span>`}).join("")}updateLegendAxes(){var l;const e=(l=this.legendElement)==null?void 0:l.querySelector("#legend-axes");if(!e)return;const t=Le.space;if(!t){e.textContent="Waiting for the run's declared space — the axes come from the ontology.";return}const n=(c,h)=>{var g;const u=t.available[c]??h.length,d=u>h.length?` (${h.length} of ${u})`:"";return`${((g=Ld[c])==null?void 0:g.display_name)??c}${d}`},s=Object.entries(t.held).map(([c,h])=>`${c}=${h}`),r={measured:Array.from(Le.aggregates.keys()).filter(c=>Le.spaceCells.has(c)).length,legal:t.counts.legal,void:t.counts.void},a=t.cells.length,o=Object.entries(t.void_rules??{}).sort((c,h)=>h[1]-c[1]).slice(0,2).map(([c,h])=>`${c.replace(/_/g," ")} (${h})`);e.innerHTML=[`<div>X: ${n(Le.axes.x,t.values[Le.axes.x]??[])}</div>`,`<div>Y: ${n(Le.axes.y,t.values[Le.axes.y]??[])}</div>`,`<div>Z: ${n(Le.axes.z,t.values[Le.axes.z]??[])}</div>`,`<div style="margin-top: 6px;">held: ${s.join(" · ")||"—"}</div>`,`<div style="margin-top: 6px;">${r.measured} measured · ${r.legal} legal · ${r.void} void (of ${a})</div>`,o.length>0?`<div style="margin-top: 6px;">refused by: ${o.join(", ")}</div>`:""].join("")}applyAxes(){const e=Le.space,t=Le.axes;this.xValues=(e==null?void 0:e.values[t.x])??[],this.yValues=(e==null?void 0:e.values[t.y])??[],this.zValues=(e==null?void 0:e.values[t.z])??[],this.buildGrid(),this.updateLegend()}buildGrid(){if(this.clearGrid(),!this.visible)return;this.createAxisLabels();const e=[];this.yValues.forEach((t,n)=>{this.zValues.forEach((s,r)=>{this.xValues.forEach((a,o)=>{const l=Xr(a,t,s),c=Le.spaceCells.get(l),h=(c==null?void 0:c.status)??"legal",u={coordinate:this.coordinateFor(a,t,s),status:h,chance:Le.chance,requiredSeeds:Le.requiredSeeds,runId:Le.runId??void 0,voidReason:c==null?void 0:c.reason,inDeclaration:c==null?void 0:c.in_declaration};if(this.cellDataMap.set(l,u),h==="void"){e.push(...this.voidMarkerPositions(o,n,r));return}this.createCell(l,u,o,n,r)})})}),e.length>0&&this.createVoidMarkers(e),this.frameGrid()}coordinateFor(e,t,n){const s={credit:"",geometry:"",dynamics:"",substrate:"",plasticity:"",update:""};return s[Le.axes.x]=e,s[Le.axes.y]=t,s[Le.axes.z]=n,Da.forEach(r=>{var o,l;if(s[r])return;const a=(l=(o=Le.space)==null?void 0:o.held)==null?void 0:l[r];a&&(s[r]=a)}),s}createAxisLabels(){this.axisLabelMeshes.forEach(h=>this.scene.remove(h)),this.axisLabelMeshes=[];const e=new Hs({color:9148584,sizeAttenuation:!0}),t=new Hs({color:13227232,sizeAttenuation:!0}),n=(this.xValues.length-1)*this.spacing,r=(this.zValues.length-1)*this.spacing/2+1.2,a=-.45;this.xValues.forEach((h,u)=>{const d=(u-(this.xValues.length-1)/2)*this.spacing,f=Mi(h,.3,e,this.spacing*.95);f.position.set(d,a,r),this.scene.add(f),this.axisLabelMeshes.push(f)});const o=Mi(Le.axes.x,.3,t);o.position.set(n/2+1.15,a,r),this.scene.add(o),this.axisLabelMeshes.push(o);const l=Mi(Le.axes.z,.3,t);l.position.set(0,a,r+1.1),this.scene.add(l),this.axisLabelMeshes.push(l);const c=Mi(Le.axes.y,.3,t);c.position.set(-(n/2)-1.5,1.3,0),this.scene.add(c),this.axisLabelMeshes.push(c)}createCell(e,t,n,s,r){const a=(n-(this.xValues.length-1)/2)*this.spacing,o=s*this.spacing,l=(r-(this.zValues.length-1)/2)*this.spacing,c=t.status==="measured"?this.createMeasuredCell(t):this.createLegalCell();c.position.set(a,o,l),c.userData={...c.userData,cellKey:e},this.scene.add(c),this.cells.set(e,c)}createMeasuredCell(e){const t=this.pillarHeight(e),n=jt[e.coordinate.credit]||V.gradient,s=new zi(this.cellSize,t,this.cellSize);s.translate(0,t/2,0);const r=new Bo({color:new nt(n),emissive:new nt(n),emissiveIntensity:.5,transparent:!0,opacity:.9,metalness:.3,roughness:.4}),a=new _n(s,r);a.castShadow=!0,a.receiveShadow=!0;const o=new zi(this.cellSize*1.1,t*1.1,this.cellSize*1.1);o.translate(0,t/2,0);const l=new Ur({color:new nt(n),transparent:!0,opacity:.15,depthWrite:!1}),c=new _n(o,l);return a.add(c),a.userData.glow=c,a}createLegalCell(){const e=new zi(this.cellSize,this.cellSize,this.cellSize),t=new qy(e);t.translate(0,this.cellSize/2,0);const n=new Hi({color:V.legal_unmeasured,transparent:!0,opacity:.55}),s=new Fr(t,n),r=new _n(new zi(this.cellSize,this.cellSize,this.cellSize),new Ur);return r.position.y=this.cellSize/2,r.visible=!1,s.add(r),s}disposeMesh(e){e.traverse(t=>{const n=t.geometry;n&&n.dispose();const s=t.material;Array.isArray(s)?s.forEach(r=>r.dispose()):s&&s.dispose()})}voidMarkerPositions(e,t,n){const s=(e-(this.xValues.length-1)/2)*this.spacing,r=t*this.spacing,a=(n-(this.zValues.length-1)/2)*this.spacing,o=this.cellSize*.6,l=.1;return[s-o,r+l,a-o,s+o,r+l,a+o,s+o,r+l,a-o,s-o,r+l,a+o]}createVoidMarkers(e){const t=new Xt;t.setAttribute("position",new qt(e,3));const n=new Hi({color:V.void,transparent:!0,opacity:.32});this.voidMesh=new Fr(t,n),this.scene.add(this.voidMesh)}frameGrid(){const e=Wr();if(!(e!=null&&e.controls)||this.xValues.length===0||this.zValues.length===0)return;const t=(this.xValues.length-1)*this.spacing/2+this.cellSize,n=(this.zValues.length-1)*this.spacing/2+this.cellSize,s=(this.yValues.length-1)*this.spacing+this.cellSize,r=n+1.8,a=-.8;Dh(e,new H(-t,a,-n),new H(t,s,r),new H(0,s/2,0))}clearGrid(){this.cells.forEach(e=>{this.scene.remove(e),this.disposeMesh(e)}),this.cells.clear(),this.cellDataMap.clear(),this.cellHeights.clear(),this.axisLabelMeshes.forEach(e=>{this.scene.remove(e),this.disposeMesh(e)}),this.axisLabelMeshes=[],this.voidMesh&&(this.scene.remove(this.voidMesh),this.voidMesh.geometry.dispose(),Array.isArray(this.voidMesh.material)?this.voidMesh.material.forEach(e=>e.dispose()):this.voidMesh.material.dispose(),this.voidMesh=null)}applyAggregates(){this.visible&&(Le.aggregates.forEach((e,t)=>{const n=this.cellDataMap.get(t);n&&(n.status="measured",n.coordinate={...e.coordinate},n.metrics={val_acc:Fs(e.acc),val_acc_std:mM(e.acc),walltime_s:Fs(e.walltime),param_count:Fs(e.params),n_seeds:e.acc.length},n.curve=gM(e.curves),n.pareto=e.pareto,n.chance=Le.chance,n.requiredSeeds=Le.requiredSeeds,n.runId=Le.runId??void 0,this.updateCellVisual(t,n,e.pareto))}),this.updateLegendAxes())}pillarHeight(e){var t;return Qc.lerp(.4,3.4,((t=e.metrics)==null?void 0:t.val_acc)??0)}updateCellVisual(e,t,n){const s=this.cells.get(e);if(!s)return;const r=s.position.clone(),a=s.userData.glow;a&&s.remove(a),this.scene.remove(s),this.disposeMesh(s);const o=this.createMeasuredCell(t);o.position.copy(r),o.userData.cellKey=e;const l=this.pillarHeight(t),c=this.cellHeights.get(e)??0;if(this.cellHeights.set(e,l),o.scale.y=l>0?Math.min(1,Math.max(c/l,.001)):1,n){const h=new Ph(this.cellSize*.6,this.cellSize*.8,32),u=new Ur({color:V.pareto,side:Yn,transparent:!0,opacity:.6}),d=new _n(h,u);d.rotation.x=-Math.PI/2,d.position.y=.05,o.add(d),o.userData.paretoRing=d}this.scene.add(o),this.cells.set(e,o)}selectCell(e){this.selectedCell=e;const t=this.cellDataMap.get(e);t&&window.dispatchEvent(new CustomEvent("cell-selected",{detail:t}))}update(e){if(!this.visible){this.hideReadout();return}const t=1-Math.exp(-e*8);this.cells.forEach((a,o)=>{const l=this.cellDataMap.get(o);if((l==null?void 0:l.status)==="measured"&&a instanceof _n&&a.material instanceof Bo){a.scale.y<1&&(a.scale.y=Math.min(1,a.scale.y+(1-a.scale.y)*t));const c=a.userData.glow;c&&(c.material.opacity=.1+.1*Math.sin(Date.now()*.003));const h=a.userData.paretoRing;h&&(h.material.opacity=.4+.2*Math.sin(Date.now()*.005))}}),this.raycaster.setFromCamera(this.mouse,this.camera);const n=this.raycaster.intersectObjects(Array.from(this.cells.values()),!0);let s=null;n.length>0&&(s=this.pickCell(n)),s||(s=this.voidCellUnderCursor()),s!==this.hoveredCell&&(this.hoveredCell&&this.highlightCell(this.hoveredCell,!1),this.hoveredCell=s,s&&this.highlightCell(s,!0));const r=s?this.cellDataMap.get(s):void 0;r?this.showReadout(r):this.hideReadout()}pickCell(e){var n,s;let t=null;for(const r of e){const a=r.object.userData.cellKey||((n=r.object.parent)==null?void 0:n.userData.cellKey);if(a&&(t??(t=a),((s=this.cellDataMap.get(a))==null?void 0:s.status)==="measured"))return a}return t}voidCellUnderCursor(){if(!this.voidMesh)return null;const e=this.raycaster.params.Line.threshold;this.raycaster.params.Line.threshold=this.cellSize*.3;try{const t=this.raycaster.intersectObject(this.voidMesh,!1);return t.length===0?null:this.cellAt(t[0].point)}finally{this.raycaster.params.Line.threshold=e}}cellAt(e){const t=Math.round(e.x/this.spacing+(this.xValues.length-1)/2),n=Math.round(e.y/this.spacing),s=Math.round(e.z/this.spacing+(this.zValues.length-1)/2);return t<0||t>=this.xValues.length||n<0||n>=this.yValues.length||s<0||s>=this.zValues.length?null:Xr(this.xValues[t],this.yValues[n],this.zValues[s])}highlightCell(e,t){const n=this.cells.get(e);if(n){if(n instanceof _n&&n.material instanceof Bo){t?(n.userData.originalEmissive=n.material.emissiveIntensity,n.material.emissiveIntensity=(n.userData.originalEmissive||.5)+.5):n.userData.originalEmissive!==void 0&&(n.material.emissiveIntensity=n.userData.originalEmissive);return}n instanceof Fr&&n.material instanceof Hi&&(t?(n.userData.originalOpacity=n.material.opacity,n.material.opacity=.95):n.userData.originalOpacity!==void 0&&(n.material.opacity=n.userData.originalOpacity))}}}const Ns=new bM;Xi.register(Ns);class EM{constructor(){U(this,"name","CellDrawer");U(this,"panel",null);U(this,"content",null);U(this,"sparklineScene",null);U(this,"sparklineRenderer",null);U(this,"sparklineCamera",null);U(this,"sparklineAnimationId",null);U(this,"currentData",null);U(this,"onKeyDown",e=>{e.key==="Escape"&&this.currentData&&this.hide()});U(this,"onCellSelected",e=>{this.show(e.detail)})}async init(){this.createPanel(),this.setupEvents(),console.log("[CellDrawer] Initialized")}async destroy(){var e;this.stopSparkline(),(e=this.panel)==null||e.remove(),window.removeEventListener("cell-selected",this.onCellSelected),window.removeEventListener("keydown",this.onKeyDown)}createPanel(){const e=document.getElementById("ui-overlay");e&&(this.panel=document.createElement("div"),this.panel.id="cell-drawer",this.panel.style.cssText=`
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
    `,e.appendChild(this.panel),this.content=this.panel.querySelector("#drawer-content"),this.panel.querySelector("#drawer-close").addEventListener("click",()=>this.hide()))}setupEvents(){window.addEventListener("cell-selected",this.onCellSelected),window.addEventListener("keydown",this.onKeyDown)}shiftPanels(e){const t=e?400:20;["hud","plotter"].forEach(n=>{var s;(s=document.getElementById(n))==null||s.style.setProperty("right",`${t}px`)})}show(e){this.currentData=e,this.renderContent(e),this.panel.style.transform="translateX(0)",this.shiftPanels(!0),this.startSparkline(e)}hide(){this.panel.style.transform="translateX(100%)",this.shiftPanels(!1),this.stopSparkline(),this.currentData=null}renderContent(e){if(!this.content)return;const{coordinate:t,metrics:n,status:s}=e,r=jt[t.credit]||V.gradient,a=(n==null?void 0:n.val_acc)??0,o=(n==null?void 0:n.n_seeds)??0,l=e.chance??.1,c=e.requiredSeeds??0;let h="UNMEASURED",u=V.legal_unmeasured;s==="void"&&(h="VOID",u=V.void),s==="measured"&&(a<=l?(h="REJECTED",u=V.rejected):c>0&&o<c?(h="INSUFFICIENT",u=V.insufficient):a>l+.1?(h="PASSED",u=V.passed):(h="INSUFFICIENT",u=V.insufficient));const d=s==="measured"&&c>0?Math.max(0,c-o):"N/A";this.content.innerHTML=`
      <div style="margin-bottom: 20px;">
        <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px;">
          ${Object.entries(t).filter(([,g])=>g).map(([g,_])=>`
              <span style="
                padding: 4px 10px;
                background: ${g==="credit"?r+"22":"var(--bg-tertiary)"};
                border: 1px solid ${g==="credit"?r+"88":"var(--border)"};
                border-radius: 12px;
                font-size: 11px;
                color: ${g==="credit"?r:"var(--text-primary)"};
              ">
                ${g}=${_}
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
            background: ${u}22;
            border: 1px solid ${u}88;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            color: ${u};
            text-transform: uppercase;
          ">${h}</span>
          <span style="font-size: 12px; color: var(--text-secondary);">Chance level: ${l}</span>
        </div>
        ${e.voidReason?`<div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 8px;">${e.voidReason}</div>`:""}
        <div style="height: 4px; background: var(--bg); border-radius: 2px; overflow: hidden;">
          <div style="
            width: ${Math.min(100,a/(l*2)*100)}%;
            height: 100%;
            background: linear-gradient(90deg, ${V.rejected}, ${V.insufficient}, ${V.passed});
            border-radius: 2px;
          "></div>
        </div>
      </div>

      ${s==="measured"?`
        <div style="margin-bottom: 20px;">
          <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 8px;">SEEDS TO CLAIM</div>
          <div style="font-size: 24px; font-weight: 700; font-family: 'JetBrains Mono', monospace; color: ${V.insufficient};">
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
    `,this.content.appendChild(f),this.wireActions(e)}actionStates(e){var a;if(e.status==="void")return{replicate:!1,preregister:!1,quest:!1};const t=e.status==="measured",n=((a=e.metrics)==null?void 0:a.n_seeds)??0,s=e.requiredSeeds??0;return{replicate:(s>0?Math.max(0,s-n):0)>0||!t,preregister:t,quest:!t}}wireActions(e){const t=this.content;if(!t)return;const n=this.actionStates(e);t.querySelectorAll(".drawer-btn[data-action]").forEach(o=>{const l=o.dataset.action??"",c=n[l]===!0;o.disabled=!c,o.addEventListener("click",()=>{this.runAction(l,e)})});const r=t.querySelector('.drawer-btn[data-action="replicate"]');r&&(r.textContent=e.status==="measured"?"Queue Rest":"Queue");const a=t.querySelector("#drawer-action-note");a&&(a.textContent=this.actionNote(e))}actionNote(e){var s;if(!e.runId)return"This cell belongs to no run yet, so there is nothing to queue or register.";if(e.status==="void")return`The system refuses this cell, so nothing can be measured here.${e.voidReason?` ${e.voidReason}.`:""}`;if(e.status==="measured"){const r=((s=e.metrics)==null?void 0:s.n_seeds)??0,a=e.requiredSeeds??0;return`Queue Rest measures the ${Math.max(0,a-r)} seeds this cell still owes. Preregister writes down the protocol a confirming run must meet.`}const t=e.inDeclaration===!1?" It lies outside this run's declaration, so the run did not set out to measure it.":"";return`The system would measure this cell and nobody has. Queue measures it (${e.requiredSeeds??0} seeds). Adopt as Quest writes the question down first and then queues the run that would answer it — a new run, because a threshold written now cannot confirm a run that has already begun.${t}`}setStatus(e,t=!1){var s;const n=(s=this.content)==null?void 0:s.querySelector("#drawer-status");n&&(n.textContent=e,n.style.color=t?V.rejected:V.text_secondary)}async runAction(e,t){var o,l;if(!t.runId){this.setStatus("This cell belongs to no run yet.",!0);return}const n=Array.from(((o=this.content)==null?void 0:o.querySelectorAll(".drawer-btn"))??[]);n.forEach(c=>{c.disabled=!0}),this.setStatus("Working…");const s=(l=this.content)==null?void 0:l.querySelector("#drawer-threshold"),r=s!=null&&s.value?Number(s.value):null,a={coordinate:t.coordinate};r!==null&&Number.isFinite(r)&&(a.threshold=r);try{const c=await fetch(`/api/cells/${t.runId}/${e}`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(a)}),h=await c.json();if(!c.ok){this.setStatus((h==null?void 0:h.error)??"The action failed.",!0);return}this.setStatus(this.actionSummary(e,h))}catch(c){this.setStatus(`The action failed: ${String(c)}`,!0)}finally{n.forEach(c=>{c.disabled=!1})}}actionSummary(e,t){if(e==="replicate")return`Queued campaign ${t.campaign_id}: ${t.measurements} measurements in a plan of ${t.plan}.`;const s=`${t.written?"Registered":"Already registered"} ${t.path} — commit it; the run that follows it can be confirmatory.`;return e!=="quest"?s:t.campaign_id?`${s} Queued campaign ${t.campaign_id}: ${t.measurements} measurements in a plan of ${t.plan}, in a new run.`:`${s} No campaign queue is attached, so nothing is scheduled.`}startSparkline(e){const t=document.getElementById("sparkline-container");if(!t)return;this.stopSparkline();const n=e.curve??[];if(n.length===0){t.innerHTML=`
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
      `;return}this.sparklineScene=new Ah,this.sparklineCamera=new Nr(-1,1,1,-1,.1,10),this.sparklineCamera.position.z=2,this.sparklineRenderer=new sp({alpha:!0,antialias:!0}),this.sparklineRenderer.setSize(t.clientWidth,t.clientHeight),this.sparklineRenderer.setPixelRatio(Math.min(window.devicePixelRatio,2)),t.appendChild(this.sparklineRenderer.domElement);const s=e.chance??.1,r=n.map(C=>C.val_acc),a=Math.min(s,...r),l=Math.max(...r,s)-a||1,c=C=>Qc.lerp(-.7,.7,(C-a)/l),h=n.map((C,F)=>{const b=Qc.lerp(-.9,.9,F/(n.length-1||1));return new H(b,c(C.val_acc),0)}),u=new Xt().setFromPoints(h),d=new Hi({color:jt[e.coordinate.credit]||V.gradient,linewidth:2}),f=new Ko(u,d);this.sparklineScene.add(f);const g=new op(new Xt().setFromPoints(h),new Rh({color:jt[e.coordinate.credit]||V.gradient,size:6,sizeAttenuation:!1}));this.sparklineScene.add(g);const _=c(s),m=new Xt().setFromPoints([new H(-.9,_,0),new H(.9,_,0)]),p=new lp({color:V.chance_line,dashSize:.05,gapSize:.03,linewidth:1}),S=new Ko(m,p);S.computeLineDistances(),this.sparklineScene.add(S);const y=new Xt().setFromPoints([new H(-.9,-.7,0),new H(.9,-.7,0),new H(-.9,-.7,0),new H(-.9,.7,0)]),w=new Hi({color:V.border,linewidth:1}),O=new Fr(y,w);this.sparklineScene.add(O);const A=()=>{!this.sparklineRenderer||!this.sparklineScene||!this.sparklineCamera||(this.sparklineRenderer.render(this.sparklineScene,this.sparklineCamera),this.sparklineAnimationId=requestAnimationFrame(A))};A()}stopSparkline(){this.sparklineAnimationId&&(cancelAnimationFrame(this.sparklineAnimationId),this.sparklineAnimationId=null),this.sparklineRenderer&&(this.sparklineRenderer.dispose(),this.sparklineRenderer=null),this.sparklineScene=null,this.sparklineCamera=null}}const dp=new EM;Xi.register(dp);const wM=!0,an="u-",TM="uplot",AM=an+"hz",RM=an+"vt",CM=an+"title",PM=an+"wrap",LM=an+"under",DM=an+"over",IM=an+"axis",Ds=an+"off",UM=an+"select",NM=an+"cursor-x",FM=an+"cursor-y",OM=an+"cursor-pt",BM=an+"legend",zM=an+"live",kM=an+"inline",HM=an+"series",VM=an+"marker",Dd=an+"label",GM=an+"value",ba="width",Ea="height",xa="top",Id="bottom",br="left",cc="right",Uh="#000",Ud=Uh+"0",hc="mousemove",Nd="mousedown",uc="mouseup",Fd="mouseenter",Od="mouseleave",Bd="dblclick",WM="resize",XM="scroll",zd="change",Jo="dppxchange",Nh="--",Jr=typeof window<"u",ih=Jr?document:null,Or=Jr?window:null,qM=Jr?navigator:null;let Mt,Ro;function sh(){let i=devicePixelRatio;Mt!=i&&(Mt=i,Ro&&ah(zd,Ro,sh),Ro=matchMedia(`(min-resolution: ${Mt-.001}dppx) and (max-resolution: ${Mt+.001}dppx)`),Os(zd,Ro,sh),Or.dispatchEvent(new CustomEvent(Jo)))}function zn(i,e){if(e!=null){let t=i.classList;!t.contains(e)&&t.add(e)}}function rh(i,e){let t=i.classList;t.contains(e)&&t.remove(e)}function Ft(i,e,t){i.style[e]=t+"px"}function si(i,e,t,n){let s=ih.createElement(i);return e!=null&&zn(s,e),t!=null&&t.insertBefore(s,n),s}function Xn(i,e){return si("div",i,e)}const kd=new WeakMap;function vi(i,e,t,n,s){let r="translate("+e+"px,"+t+"px)",a=kd.get(i);r!=a&&(i.style.transform=r,kd.set(i,r),e<0||t<0||e>n||t>s?zn(i,Ds):rh(i,Ds))}const Hd=new WeakMap;function Vd(i,e,t){let n=e+t,s=Hd.get(i);n!=s&&(Hd.set(i,n),i.style.background=e,i.style.borderColor=t)}const Gd=new WeakMap;function Wd(i,e,t,n){let s=e+""+t,r=Gd.get(i);s!=r&&(Gd.set(i,s),i.style.height=t+"px",i.style.width=e+"px",i.style.marginLeft=n?-e/2+"px":0,i.style.marginTop=n?-t/2+"px":0)}const Fh={passive:!0},$M={...Fh,capture:!0};function Os(i,e,t,n){e.addEventListener(i,t,n?$M:Fh)}function ah(i,e,t,n){e.removeEventListener(i,t,Fh)}Jr&&sh();function ri(i,e,t,n){let s;t=t||0,n=n||e.length-1;let r=n<=2147483647;for(;n-t>1;)s=r?t+n>>1:kn((t+n)/2),e[s]<i?t=s:n=s;return i-e[t]<=e[n]-i?t:n}function fp(i){return(t,n,s)=>{let r=-1,a=-1;for(let o=n;o<=s;o++)if(i(t[o])){r=o;break}for(let o=s;o>=n;o--)if(i(t[o])){a=o;break}return[r,a]}}const pp=i=>i!=null,mp=i=>i!=null&&i>0,cl=fp(pp),YM=fp(mp);function jM(i,e,t,n=0,s=!1){let r=s?YM:cl,a=s?mp:pp;[e,t]=r(i,e,t);let o=i[e],l=i[e];if(e>-1)if(n==1)o=i[e],l=i[t];else if(n==-1)o=i[t],l=i[e];else for(let c=e;c<=t;c++){let h=i[c];a(h)&&(h<o?o=h:h>l&&(l=h))}return[o??Rt,l??-Rt]}function hl(i,e,t,n){let s=$d(i),r=$d(e);i==e&&(s==-1?(i*=t,e/=t):(i/=t,e*=t));let a=t==10?Vi:gp,o=s==1?kn:$n,l=r==1?$n:kn,c=o(a(tn(i))),h=l(a(tn(e))),u=qr(t,c),d=qr(t,h);return t==10&&(c<0&&(u=Ct(u,-c)),h<0&&(d=Ct(d,-h))),n||t==2?(i=u*s,e=d*r):(i=yp(i,u),e=ul(e,d)),[i,e]}function Oh(i,e,t,n){let s=hl(i,e,t,n);return i==0&&(s[0]=0),e==0&&(s[1]=0),s}const Bh=.1,Xd={mode:3,pad:Bh},Aa={pad:0,soft:null,mode:0},KM={min:Aa,max:Aa};function Qo(i,e,t,n){return dl(t)?qd(i,e,t):(Aa.pad=t,Aa.soft=n?0:null,Aa.mode=n?3:0,qd(i,e,KM))}function xt(i,e){return i??e}function ZM(i,e,t){for(e=xt(e,0),t=xt(t,i.length-1);e<=t;){if(i[e]!=null)return!0;e++}return!1}function qd(i,e,t){let n=t.min,s=t.max,r=xt(n.pad,0),a=xt(s.pad,0),o=xt(n.hard,-Rt),l=xt(s.hard,Rt),c=xt(n.soft,Rt),h=xt(s.soft,-Rt),u=xt(n.mode,0),d=xt(s.mode,0),f=e-i,g=Vi(f),_=Pn(tn(i),tn(e)),m=Vi(_),p=tn(m-g);(f<1e-24||p>10)&&(f=0,(i==0||e==0)&&(f=1e-24,u==2&&c!=Rt&&(r=0),d==2&&h!=-Rt&&(a=0)));let S=f||_||1e3,y=Vi(S),w=qr(10,kn(y)),O=S*(f==0?i==0?.1:1:r),A=Ct(yp(i-O,w/10),24),C=i>=c&&(u==1||u==3&&A<=c||u==2&&A>=c)?c:Rt,F=Pn(o,A<C&&i>=C?C:li(C,A)),b=S*(f==0?e==0?.1:1:a),x=Ct(ul(e+b,w/10),24),P=e<=h&&(d==1||d==3&&x>=h||d==2&&x<=h)?h:-Rt,K=li(l,x>P&&e<=P?P:Pn(P,x));return F==K&&F==0&&(K=100),[F,K]}const JM=new Intl.NumberFormat(Jr?qM.language:"en-US"),zh=i=>JM.format(i),Hn=Math,zo=Hn.PI,tn=Hn.abs,kn=Hn.floor,en=Hn.round,$n=Hn.ceil,li=Hn.min,Pn=Hn.max,qr=Hn.pow,$d=Hn.sign,Vi=Hn.log10,gp=Hn.log2,QM=(i,e=1)=>Hn.sinh(i)*e,dc=(i,e=1)=>Hn.asinh(i/e),Rt=1/0;function Yd(i){return(Vi((i^i>>31)-(i>>31))|0)+1}function oh(i,e,t){return li(Pn(i,e),t)}function _p(i){return typeof i=="function"}function ft(i){return _p(i)?i:()=>i}const eS=()=>{},vp=i=>i,xp=(i,e)=>e,tS=i=>null,jd=i=>!0,Kd=(i,e)=>i==e,nS=/\.\d*?(?=9{6,}|0{6,})/gm,Vs=i=>{if(Sp(i)||ds.has(i))return i;const e=`${i}`,t=e.match(nS);if(t==null)return i;let n=t[0].length-1;if(e.indexOf("e-")!=-1){let[s,r]=e.split("e");return+`${Vs(s)}e${r}`}return Ct(i,n)};function Rs(i,e){return Vs(Ct(Vs(i/e))*e)}function ul(i,e){return Vs($n(Vs(i/e))*e)}function yp(i,e){return Vs(kn(Vs(i/e))*e)}function Ct(i,e=0){if(Sp(i))return i;let t=10**e,n=i*t*(1+Number.EPSILON);return en(n)/t}const ds=new Map;function Mp(i){return((""+i).split(".")[1]||"").length}function Ua(i,e,t,n){let s=[],r=n.map(Mp);for(let a=e;a<t;a++){let o=tn(a),l=Ct(qr(i,a),o);for(let c=0;c<n.length;c++){let h=i==10?+`${n[c]}e${a}`:n[c]*l,u=(a>=0?0:o)+(a>=r[c]?0:r[c]),d=i==10?h:Ct(h,u);s.push(d),ds.set(d,u)}}return s}const Ra={},kh=[],$r=[null,null],rs=Array.isArray,Sp=Number.isInteger,iS=i=>i===void 0;function Zd(i){return typeof i=="string"}function dl(i){let e=!1;if(i!=null){let t=i.constructor;e=t==null||t==Object}return e}function sS(i){return i!=null&&typeof i=="object"}const rS=Object.getPrototypeOf(Uint8Array),bp="__proto__";function Yr(i,e=dl){let t;if(rs(i)){let n=i.find(s=>s!=null);if(rs(n)||e(n)){t=Array(i.length);for(let s=0;s<i.length;s++)t[s]=Yr(i[s],e)}else t=i.slice()}else if(i instanceof rS)t=i.slice();else if(e(i)){t={};for(let n in i)n!=bp&&(t[n]=Yr(i[n],e))}else t=i;return t}function Jt(i){let e=arguments;for(let t=1;t<e.length;t++){let n=e[t];for(let s in n)s!=bp&&(dl(i[s])?Jt(i[s],Yr(n[s])):i[s]=Yr(n[s]))}return i}const aS=0,oS=1,lS=2;function cS(i,e,t){for(let n=0,s,r=-1;n<e.length;n++){let a=e[n];if(a>r){for(s=a-1;s>=0&&i[s]==null;)i[s--]=null;for(s=a+1;s<t&&i[s]==null;)i[r=s++]=null}}}function hS(i,e){if(fS(i)){let a=i[0].slice();for(let o=1;o<i.length;o++)a.push(...i[o].slice(1));return pS(a[0])||(a=dS(a)),a}let t=new Set;for(let a=0;a<i.length;a++){let l=i[a][0],c=l.length;for(let h=0;h<c;h++)t.add(l[h])}let n=[Array.from(t).sort((a,o)=>a-o)],s=n[0].length,r=new Map;for(let a=0;a<s;a++)r.set(n[0][a],a);for(let a=0;a<i.length;a++){let o=i[a],l=o[0];for(let c=1;c<o.length;c++){let h=o[c],u=Array(s).fill(void 0),d=e?e[a][c]:oS,f=[];for(let g=0;g<h.length;g++){let _=h[g],m=r.get(l[g]);_===null?d!=aS&&(u[m]=_,d==lS&&f.push(m)):u[m]=_}cS(u,f,s),n.push(u)}}return n}const uS=typeof queueMicrotask>"u"?i=>Promise.resolve().then(i):queueMicrotask;function dS(i){let e=i[0],t=e.length,n=Array(t);for(let r=0;r<n.length;r++)n[r]=r;n.sort((r,a)=>e[r]-e[a]);let s=[];for(let r=0;r<i.length;r++){let a=i[r],o=Array(t);for(let l=0;l<t;l++)o[l]=a[n[l]];s.push(o)}return s}function fS(i){let e=i[0][0],t=e.length;for(let n=1;n<i.length;n++){let s=i[n][0];if(s.length!=t)return!1;if(s!=e){for(let r=0;r<t;r++)if(s[r]!=e[r])return!1}}return!0}function pS(i,e=100){const t=i.length;if(t<=1)return!0;let n=0,s=t-1;for(;n<=s&&i[n]==null;)n++;for(;s>=n&&i[s]==null;)s--;if(s<=n)return!0;const r=Pn(1,kn((s-n+1)/e));for(let a=i[n],o=n+r;o<=s;o+=r){const l=i[o];if(l!=null){if(l<=a)return!1;a=l}}return!0}const Ep=["January","February","March","April","May","June","July","August","September","October","November","December"],wp=["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];function Tp(i){return i.slice(0,3)}const mS=wp.map(Tp),gS=Ep.map(Tp),_S={MMMM:Ep,MMM:gS,WWWW:wp,WWW:mS};function ya(i){return(i<10?"0":"")+i}function vS(i){return(i<10?"00":i<100?"0":"")+i}const xS={YYYY:i=>i.getFullYear(),YY:i=>(i.getFullYear()+"").slice(2),MMMM:(i,e)=>e.MMMM[i.getMonth()],MMM:(i,e)=>e.MMM[i.getMonth()],MM:i=>ya(i.getMonth()+1),M:i=>i.getMonth()+1,DD:i=>ya(i.getDate()),D:i=>i.getDate(),WWWW:(i,e)=>e.WWWW[i.getDay()],WWW:(i,e)=>e.WWW[i.getDay()],HH:i=>ya(i.getHours()),H:i=>i.getHours(),h:i=>{let e=i.getHours();return e==0?12:e>12?e-12:e},AA:i=>i.getHours()>=12?"PM":"AM",aa:i=>i.getHours()>=12?"pm":"am",a:i=>i.getHours()>=12?"p":"a",mm:i=>ya(i.getMinutes()),m:i=>i.getMinutes(),ss:i=>ya(i.getSeconds()),s:i=>i.getSeconds(),fff:i=>vS(i.getMilliseconds())};function Hh(i,e){e=e||_S;let t=[],n=/\{([a-z]+)\}|[^{]+/gi,s;for(;s=n.exec(i);)t.push(s[0][0]=="{"?xS[s[1]]:s[0]);return r=>{let a="";for(let o=0;o<t.length;o++)a+=typeof t[o]=="string"?t[o]:t[o](r,e);return a}}const yS=new Intl.DateTimeFormat().resolvedOptions().timeZone;function MS(i,e){let t;return e=="UTC"||e=="Etc/UTC"?t=new Date(+i+i.getTimezoneOffset()*6e4):e==yS?t=i:(t=new Date(i.toLocaleString("en-US",{timeZone:e})),t.setMilliseconds(i.getMilliseconds())),t}const Ap=i=>i%1==0,el=[1,2,2.5,5],SS=Ua(10,-32,0,el),Rp=Ua(10,0,32,el),bS=Rp.filter(Ap),Cs=SS.concat(Rp),Vh=`
`,Cp="{YYYY}",Jd=Vh+Cp,Pp="{M}/{D}",wa=Vh+Pp,Co=wa+"/{YY}",Lp="{aa}",ES="{h}:{mm}",Ar=ES+Lp,Qd=Vh+Ar,ef=":{ss}",St=null;function Dp(i){let e=i*1e3,t=e*60,n=t*60,s=n*24,r=s*30,a=s*365,l=(i==1?Ua(10,0,3,el).filter(Ap):Ua(10,-3,0,el)).concat([e,e*5,e*10,e*15,e*30,t,t*5,t*10,t*15,t*30,n,n*2,n*3,n*4,n*6,n*8,n*12,s,s*2,s*3,s*4,s*5,s*6,s*7,s*8,s*9,s*10,s*15,r,r*2,r*3,r*4,r*6,a,a*2,a*5,a*10,a*25,a*50,a*100]);const c=[[a,Cp,St,St,St,St,St,St,1],[s*28,"{MMM}",Jd,St,St,St,St,St,1],[s,Pp,Jd,St,St,St,St,St,1],[n,"{h}"+Lp,Co,St,wa,St,St,St,1],[t,Ar,Co,St,wa,St,St,St,1],[e,ef,Co+" "+Ar,St,wa+" "+Ar,St,Qd,St,1],[i,ef+".{fff}",Co+" "+Ar,St,wa+" "+Ar,St,Qd,St,1]];function h(u){return(d,f,g,_,m,p)=>{let S=[],y=m>=a,w=m>=r&&m<a,O=u(g),A=Ct(O*i,3),C=fc(O.getFullYear(),y?0:O.getMonth(),w||y?1:O.getDate()),F=Ct(C*i,3);if(w||y){let b=w?m/r:0,x=y?m/a:0,P=A==F?A:Ct(fc(C.getFullYear()+x,C.getMonth()+b,1)*i,3),K=new Date(en(P/i)),k=K.getFullYear(),Z=K.getMonth();for(let q=0;P<=_;q++){let ee=fc(k+x*q,Z+b*q,1),Y=ee-u(Ct(ee*i,3));P=Ct((+ee+Y)*i,3),P<=_&&S.push(P)}}else{let b=m>=s?s:m,x=kn(g)-kn(A),P=F+x+ul(A-F,b);S.push(P);let K=u(P),k=K.getHours()+K.getMinutes()/t+K.getSeconds()/n,Z=m/n,q=d.axes[f]._space,ee=p/q;for(;P=Ct(P+m,i==1?0:3),!(P>_);)if(Z>1){let Y=kn(Ct(k+Z,6))%24,de=u(P).getHours()-Y;de>1&&(de=-1),P-=de*n,k=(k+Z)%24;let xe=S[S.length-1];Ct((P-xe)/m,3)*ee>=.7&&S.push(P)}else S.push(P)}return S}}return[l,c,h]}const[wS,TS,AS]=Dp(1),[RS,CS,PS]=Dp(.001);Ua(2,-53,53,[1]);function tf(i,e){return i.map(t=>t.map((n,s)=>s==0||s==8||n==null?n:e(s==1||t[8]==0?n:t[1]+n)))}function nf(i,e){return(t,n,s,r,a)=>{let o=e.find(g=>a>=g[0])||e[e.length-1],l,c,h,u,d,f;return n.map(g=>{let _=i(g),m=_.getFullYear(),p=_.getMonth(),S=_.getDate(),y=_.getHours(),w=_.getMinutes(),O=_.getSeconds(),A=m!=l&&o[2]||p!=c&&o[3]||S!=h&&o[4]||y!=u&&o[5]||w!=d&&o[6]||O!=f&&o[7]||o[1];return l=m,c=p,h=S,u=y,d=w,f=O,A(_)})}}function LS(i,e){let t=Hh(e);return(n,s,r,a,o)=>s.map(l=>t(i(l)))}function fc(i,e,t){return new Date(i,e,t)}function sf(i,e){return e(i)}const DS="{YYYY}-{MM}-{DD} {h}:{mm}{aa}";function rf(i,e){return(t,n,s,r)=>r==null?Nh:e(i(n))}function IS(i,e){let t=i.series[e];return t.width?t.stroke(i,e):t.points.width?t.points.stroke(i,e):null}function US(i,e){return i.series[e].fill(i,e)}const NS={show:!0,live:!0,isolate:!1,mount:eS,markers:{show:!0,width:2,stroke:IS,fill:US,dash:"solid"},idx:null,idxs:null,values:[]};function FS(i,e){let t=i.cursor.points,n=Xn(),s=t.size(i,e);Ft(n,ba,s),Ft(n,Ea,s);let r=s/-2;Ft(n,"marginLeft",r),Ft(n,"marginTop",r);let a=t.width(i,e,s);return a&&Ft(n,"borderWidth",a),n}function OS(i,e){let t=i.series[e].points;return t._fill||t._stroke}function BS(i,e){let t=i.series[e].points;return t._stroke||t._fill}function zS(i,e){return i.series[e].points.size}const pc=[0,0];function kS(i,e,t){return pc[0]=e,pc[1]=t,pc}function Po(i,e,t,n=!0){return s=>{s.button==0&&(!n||s.target==e)&&t(s)}}function mc(i,e,t,n=!0){return s=>{(!n||s.target==e)&&t(s)}}const HS={show:!0,x:!0,y:!0,lock:!1,move:kS,points:{one:!1,show:FS,size:zS,width:0,stroke:BS,fill:OS},bind:{mousedown:Po,mouseup:Po,click:Po,dblclick:Po,mousemove:mc,mouseleave:mc,mouseenter:mc},drag:{setScale:!0,x:!0,y:!1,dist:0,uni:null,click:(i,e)=>{e.stopPropagation(),e.stopImmediatePropagation()},_x:!1,_y:!1},focus:{dist:(i,e,t,n,s)=>n-s,prox:-1,bias:0},hover:{skip:[void 0],prox:null,bias:0},left:-10,top:-10,idx:null,dataIdx:null,idxs:null,event:null},Ip={show:!0,stroke:"rgba(0,0,0,0.07)",width:2},Gh=Jt({},Ip,{filter:xp}),Up=Jt({},Gh,{size:10}),Np=Jt({},Ip,{show:!1}),Wh='12px system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji"',Fp="bold "+Wh,Op=1.5,af={show:!0,scale:"x",stroke:Uh,space:50,gap:5,alignTo:1,size:50,labelGap:0,labelSize:30,labelFont:Fp,side:2,grid:Gh,ticks:Up,border:Np,font:Wh,lineGap:Op,rotate:0},VS="Value",GS="Time",of={show:!0,scale:"x",auto:!1,sorted:1,min:Rt,max:-Rt,idxs:[]};function WS(i,e,t,n,s){return e.map(r=>r==null?"":zh(r))}function XS(i,e,t,n,s,r,a){let o=[],l=ds.get(s)||0;t=a?t:Ct(ul(t,s),l);for(let c=t;c<=n;c=Ct(c+s,l))o.push(Object.is(c,-0)?0:c);return o}function lh(i,e,t,n,s,r,a){const o=[],l=i.scales[i.axes[e].scale].log,c=l==10?Vi:gp,h=kn(c(t));s=qr(l,h),l==10&&(s=Cs[ri(s,Cs)]);let u=t,d=s*l;l==10&&(d=Cs[ri(d,Cs)]);do o.push(u),u=u+s,l==10&&!ds.has(u)&&(u=Ct(u,ds.get(s))),u>=d&&(s=u,d=s*l,l==10&&(d=Cs[ri(d,Cs)]));while(u<=n);return o}function qS(i,e,t,n,s,r,a){let l=i.scales[i.axes[e].scale].asinh,c=n>l?lh(i,e,Pn(l,t),n,s):[l],h=n>=0&&t<=0?[0]:[];return(t<-l?lh(i,e,Pn(l,-n),-t,s):[l]).reverse().map(d=>-d).concat(h,c)}const Bp=/./,$S=/[12357]/,YS=/[125]/,lf=/1/,ch=(i,e,t,n)=>i.map((s,r)=>e==4&&s==0||r%n==0&&t.test(s.toExponential()[s<0?1:0])?s:null);function jS(i,e,t,n,s){let r=i.axes[t],a=r.scale,o=i.scales[a],l=i.valToPos,c=r._space,h=l(10,a),u=l(9,a)-h>=c?Bp:l(7,a)-h>=c?$S:l(5,a)-h>=c?YS:lf;if(u==lf){let d=tn(l(1,a)-h);if(d<c)return ch(e.slice().reverse(),o.distr,u,$n(c/d)).reverse()}return ch(e,o.distr,u,1)}function KS(i,e,t,n,s){let r=i.axes[t],a=r.scale,o=r._space,l=i.valToPos,c=tn(l(1,a)-l(2,a));return c<o?ch(e.slice().reverse(),3,Bp,$n(o/c)).reverse():e}function ZS(i,e,t,n){return n==null?Nh:e==null?"":zh(e)}const cf={show:!0,scale:"y",stroke:Uh,space:30,gap:5,alignTo:1,size:50,labelGap:0,labelSize:30,labelFont:Fp,side:3,grid:Gh,ticks:Up,border:Np,font:Wh,lineGap:Op,rotate:0};function JS(i,e){let t=3+(i||1)*2;return Ct(t*e,3)}function QS(i,e){let{scale:t,idxs:n}=i.series[0],s=i._data[0],r=i.valToPos(s[n[0]],t,!0),a=i.valToPos(s[n[1]],t,!0),o=tn(a-r),l=i.series[e],c=o/(l.points.space*Mt);return n[1]-n[0]<=c}const hf={scale:null,auto:!0,sorted:0,min:Rt,max:-Rt},zp=(i,e,t,n,s)=>s,uf={show:!0,auto:!0,sorted:0,gaps:zp,alpha:1,facets:[Jt({},hf,{scale:"x"}),Jt({},hf,{scale:"y"})]},df={scale:"y",auto:!0,sorted:0,show:!0,spanGaps:!1,gaps:zp,alpha:1,points:{show:QS,filter:null},values:null,min:Rt,max:-Rt,idxs:[],path:null,clip:null};function eb(i,e,t,n,s){return t/10}const kp={time:wM,auto:!0,distr:1,log:10,asinh:1,min:null,max:null,dir:1,ori:0},tb=Jt({},kp,{time:!1,ori:1}),ff={};function Hp(i,e){let t=ff[i];return t||(t={key:i,plots:[],sub(n){t.plots.push(n)},unsub(n){t.plots=t.plots.filter(s=>s!=n)},pub(n,s,r,a,o,l,c){for(let h=0;h<t.plots.length;h++)t.plots[h]!=s&&t.plots[h].pub(n,s,r,a,o,l,c)}},i!=null&&(ff[i]=t)),t}const jr=1,hh=2;function Gs(i,e,t){const n=i.mode,s=i.series[e],r=n==2?i._data[e]:i._data,a=i.scales,o=i.bbox;let l=r[0],c=n==2?r[1]:r[e],h=n==2?a[s.facets[0].scale]:a[i.series[0].scale],u=n==2?a[s.facets[1].scale]:a[s.scale],d=o.left,f=o.top,g=o.width,_=o.height,m=i.valToPosH,p=i.valToPosV;return h.ori==0?t(s,l,c,h,u,m,p,d,f,g,_,pl,Qr,gl,Gp,Xp):t(s,l,c,h,u,p,m,f,d,_,g,ml,ea,$h,Wp,qp)}function Xh(i,e){let t=0,n=0,s=xt(i.bands,kh);for(let r=0;r<s.length;r++){let a=s[r];a.series[0]==e?t=a.dir:a.series[1]==e&&(a.dir==1?n|=1:n|=2)}return[t,n==1?-1:n==2?1:n==3?2:0]}function nb(i,e,t,n,s){let r=i.mode,a=i.series[e],o=r==2?a.facets[1].scale:a.scale,l=i.scales[o];return s==-1?l.min:s==1?l.max:l.distr==3?l.dir==1?l.min:l.max:0}function Gi(i,e,t,n,s,r){return Gs(i,e,(a,o,l,c,h,u,d,f,g,_,m)=>{let p=a.pxRound;const S=c.dir*(c.ori==0?1:-1),y=c.ori==0?Qr:ea;let w,O;S==1?(w=t,O=n):(w=n,O=t);let A=p(u(o[w],c,_,f)),C=p(d(l[w],h,m,g)),F=p(u(o[O],c,_,f)),b=p(d(r==1?h.max:h.min,h,m,g)),x=new Path2D(s);return y(x,F,b),y(x,A,b),y(x,A,C),x})}function fl(i,e,t,n,s,r){let a=null;if(i.length>0){a=new Path2D;const o=e==0?gl:$h;let l=t;for(let u=0;u<i.length;u++){let d=i[u];if(d[1]>d[0]){let f=d[0]-l;f>0&&o(a,l,n,f,n+r),l=d[1]}}let c=t+s-l,h=10;c>0&&o(a,l,n-h/2,c,n+r+h)}return a}function ib(i,e,t){let n=i[i.length-1];n&&n[0]==e?n[1]=t:i.push([e,t])}function qh(i,e,t,n,s,r,a){let o=[],l=i.length;for(let c=s==1?t:n;c>=t&&c<=n;c+=s)if(e[c]===null){let u=c,d=c;if(s==1)for(;++c<=n&&e[c]===null;)d=c;else for(;--c>=t&&e[c]===null;)d=c;let f=r(i[u]),g=d==u?f:r(i[d]),_=u-s;f=a<=0&&_>=0&&_<l?r(i[_]):f;let p=d+s;g=a>=0&&p>=0&&p<l?r(i[p]):g,g>=f&&o.push([f,g])}return o}function pf(i){return i==0?vp:i==1?en:e=>Rs(e,i)}function Vp(i){let e=i==0?pl:ml,t=i==0?(s,r,a,o,l,c)=>{s.arcTo(r,a,o,l,c)}:(s,r,a,o,l,c)=>{s.arcTo(a,r,l,o,c)},n=i==0?(s,r,a,o,l)=>{s.rect(r,a,o,l)}:(s,r,a,o,l)=>{s.rect(a,r,l,o)};return(s,r,a,o,l,c=0,h=0)=>{c==0&&h==0?n(s,r,a,o,l):(c=li(c,o/2,l/2),h=li(h,o/2,l/2),e(s,r+c,a),t(s,r+o,a,r+o,a+l,c),t(s,r+o,a+l,r,a+l,h),t(s,r,a+l,r,a,h),t(s,r,a,r+o,a,c),s.closePath())}}const pl=(i,e,t)=>{i.moveTo(e,t)},ml=(i,e,t)=>{i.moveTo(t,e)},Qr=(i,e,t)=>{i.lineTo(e,t)},ea=(i,e,t)=>{i.lineTo(t,e)},gl=Vp(0),$h=Vp(1),Gp=(i,e,t,n,s,r)=>{i.arc(e,t,n,s,r)},Wp=(i,e,t,n,s,r)=>{i.arc(t,e,n,s,r)},Xp=(i,e,t,n,s,r,a)=>{i.bezierCurveTo(e,t,n,s,r,a)},qp=(i,e,t,n,s,r,a)=>{i.bezierCurveTo(t,e,s,n,a,r)};function $p(i){return(e,t,n,s,r)=>Gs(e,t,(a,o,l,c,h,u,d,f,g,_,m)=>{let{pxRound:p,points:S}=a,y,w;c.ori==0?(y=pl,w=Gp):(y=ml,w=Wp);const O=Ct(S.width*Mt,3);let A=(S.size-S.width)/2*Mt,C=Ct(A*2,3),F=new Path2D,b=new Path2D,{left:x,top:P,width:K,height:k}=e.bbox;gl(b,x-C,P-C,K+C*2,k+C*2);const Z=q=>{if(l[q]!=null){let ee=p(u(o[q],c,_,f)),Y=p(d(l[q],h,m,g));y(F,ee+A,Y),w(F,ee,Y,A,0,zo*2)}};if(r)r.forEach(Z);else for(let q=n;q<=s;q++)Z(q);return{stroke:O>0?F:null,fill:F,clip:b,flags:jr|hh}})}function Yp(i){return(e,t,n,s,r,a)=>{n!=s&&(r!=n&&a!=n&&i(e,t,n),r!=s&&a!=s&&i(e,t,s),i(e,t,a))}}const sb=Yp(Qr),rb=Yp(ea);function jp(i){const e=xt(i==null?void 0:i.alignGaps,0);return(t,n,s,r)=>Gs(t,n,(a,o,l,c,h,u,d,f,g,_,m)=>{[s,r]=cl(l,s,r);let p=a.pxRound,S=k=>p(u(k,c,_,f)),y=k=>p(d(k,h,m,g)),w,O;c.ori==0?(w=Qr,O=sb):(w=ea,O=rb);const A=c.dir*(c.ori==0?1:-1),C={stroke:new Path2D,fill:null,clip:null,band:null,gaps:null,flags:jr},F=C.stroke;let b=!1;if(r-s>=_*4){let k=ye=>t.posToVal(ye,c.key,!0),Z=null,q=null,ee,Y,ne,ge=S(o[A==1?s:r]),de=S(o[s]),xe=S(o[r]),we=k(A==1?de+1:xe-1);for(let ye=A==1?s:r;ye>=s&&ye<=r;ye+=A){let ie=o[ye],Me=(A==1?ie<we:ie>we)?ge:S(ie),fe=l[ye];Me==ge?fe!=null?(Y=fe,Z==null?(w(F,Me,y(Y)),ee=Z=q=Y):Y<Z?Z=Y:Y>q&&(q=Y)):fe===null&&(b=!0):(Z!=null&&O(F,ge,y(Z),y(q),y(ee),y(Y)),fe!=null?(Y=fe,w(F,Me,y(Y)),Z=q=ee=Y):(Z=q=null,fe===null&&(b=!0)),ge=Me,we=k(ge+A))}Z!=null&&Z!=q&&ne!=ge&&O(F,ge,y(Z),y(q),y(ee),y(Y))}else for(let k=A==1?s:r;k>=s&&k<=r;k+=A){let Z=l[k];Z===null?b=!0:Z!=null&&w(F,S(o[k]),y(Z))}let[P,K]=Xh(t,n);if(a.fill!=null||P!=0){let k=C.fill=new Path2D(F),Z=a.fillTo(t,n,a.min,a.max,P),q=y(Z),ee=S(o[s]),Y=S(o[r]);A==-1&&([Y,ee]=[ee,Y]),w(k,Y,q),w(k,ee,q)}if(!a.spanGaps){let k=[];b&&k.push(...qh(o,l,s,r,A,S,e)),C.gaps=k=a.gaps(t,n,s,r,k),C.clip=fl(k,c.ori,f,g,_,m)}return K!=0&&(C.band=K==2?[Gi(t,n,s,r,F,-1),Gi(t,n,s,r,F,1)]:Gi(t,n,s,r,F,K)),C})}function ab(i){const e=xt(i.align,1),t=xt(i.ascDesc,!1),n=xt(i.alignGaps,0),s=xt(i.extend,!1);return(r,a,o,l)=>Gs(r,a,(c,h,u,d,f,g,_,m,p,S,y)=>{[o,l]=cl(u,o,l);let w=c.pxRound,{left:O,width:A}=r.bbox,C=de=>w(g(de,d,S,m)),F=de=>w(_(de,f,y,p)),b=d.ori==0?Qr:ea;const x={stroke:new Path2D,fill:null,clip:null,band:null,gaps:null,flags:jr},P=x.stroke,K=d.dir*(d.ori==0?1:-1);let k=F(u[K==1?o:l]),Z=C(h[K==1?o:l]),q=Z,ee=Z;s&&e==-1&&(ee=O,b(P,ee,k)),b(P,Z,k);for(let de=K==1?o:l;de>=o&&de<=l;de+=K){let xe=u[de];if(xe==null)continue;let we=C(h[de]),ye=F(xe);e==1?b(P,we,k):b(P,q,ye),b(P,we,ye),k=ye,q=we}let Y=q;s&&e==1&&(Y=O+A,b(P,Y,k));let[ne,ge]=Xh(r,a);if(c.fill!=null||ne!=0){let de=x.fill=new Path2D(P),xe=c.fillTo(r,a,c.min,c.max,ne),we=F(xe);b(de,Y,we),b(de,ee,we)}if(!c.spanGaps){let de=[];de.push(...qh(h,u,o,l,K,C,n));let xe=c.width*Mt/2,we=t||e==1?xe:-xe,ye=t||e==-1?-xe:xe;de.forEach(ie=>{ie[0]+=we,ie[1]+=ye}),x.gaps=de=c.gaps(r,a,o,l,de),x.clip=fl(de,d.ori,m,p,S,y)}return ge!=0&&(x.band=ge==2?[Gi(r,a,o,l,P,-1),Gi(r,a,o,l,P,1)]:Gi(r,a,o,l,P,ge)),x})}function mf(i,e,t,n,s,r,a=Rt){if(i.length>1){let o=null;for(let l=0,c=1/0;l<i.length;l++)if(e[l]!==void 0){if(o!=null){let h=tn(i[l]-i[o]);h<c&&(c=h,a=tn(t(i[l],n,s,r)-t(i[o],n,s,r)))}o=l}}return a}function ob(i){i=i||Ra;const e=xt(i.size,[.6,Rt,1]),t=i.align||0,n=i.gap||0;let s=i.radius;s=s==null?[0,0]:typeof s=="number"?[s,0]:s;const r=ft(s),a=1-e[0],o=xt(e[1],Rt),l=xt(e[2],1),c=xt(i.disp,Ra),h=xt(i.each,f=>{}),{fill:u,stroke:d}=c;return(f,g,_,m)=>Gs(f,g,(p,S,y,w,O,A,C,F,b,x,P)=>{let K=p.pxRound,k=t,Z=n*Mt,q=o*Mt,ee=l*Mt,Y,ne;w.ori==0?[Y,ne]=r(f,g):[ne,Y]=r(f,g);const ge=w.dir*(w.ori==0?1:-1);let de=w.ori==0?gl:$h,xe=w.ori==0?h:(X,Ee,_e,Ae,Ke,me,Te)=>{h(X,Ee,_e,Ke,Ae,Te,me)},we=xt(f.bands,kh).find(X=>X.series[0]==g),ye=we!=null?we.dir:0,ie=p.fillTo(f,g,p.min,p.max,ye),he=K(C(ie,O,P,b)),Me,fe,ze,Ge=x,Fe=K(p.width*Mt),pt=!1,N=null,dt=null,st=null,ct=null;u!=null&&(Fe==0||d!=null)&&(pt=!0,N=u.values(f,g,_,m),dt=new Map,new Set(N).forEach(X=>{X!=null&&dt.set(X,new Path2D)}),Fe>0&&(st=d.values(f,g,_,m),ct=new Map,new Set(st).forEach(X=>{X!=null&&ct.set(X,new Path2D)})));let{x0:Oe,size:Et}=c;if(Oe!=null&&Et!=null){k=1,S=Oe.values(f,g,_,m),Oe.unit==2&&(S=S.map(_e=>f.posToVal(F+_e*x,w.key,!0)));let X=Et.values(f,g,_,m);Et.unit==2?fe=X[0]*x:fe=A(X[0],w,x,F)-A(0,w,x,F),Ge=mf(S,y,A,w,x,F,Ge),ze=Ge-fe+Z}else Ge=mf(S,y,A,w,x,F,Ge),ze=Ge*a+Z,fe=Ge-ze;ze<1&&(ze=0),Fe>=fe/2&&(Fe=0),ze<5&&(K=vp);let $e=ze>0,Xe=Ge-ze-($e?Fe:0);fe=K(oh(Xe,ee,q)),Me=(k==0?fe/2:k==ge?0:fe)-k*ge*((k==0?Z/2:0)+($e?Fe/2:0));const D={stroke:null,fill:null,clip:null,band:null,gaps:null,flags:0},E=pt?null:new Path2D;let Q=null;if(we!=null)Q=f.data[we.series[1]];else{let{y0:X,y1:Ee}=c;X!=null&&Ee!=null&&(y=Ee.values(f,g,_,m),Q=X.values(f,g,_,m))}let le=Y*fe,te=ne*fe;for(let X=ge==1?_:m;X>=_&&X<=m;X+=ge){let Ee=y[X];if(Ee==null)continue;if(Q!=null){let be=Q[X]??0;if(Ee-be==0)continue;he=C(be,O,P,b)}let _e=w.distr!=2||c!=null?S[X]:X,Ae=A(_e,w,x,F),Ke=C(xt(Ee,ie),O,P,b),me=K(Ae-Me),Te=K(Pn(Ke,he)),Ze=K(li(Ke,he)),ke=Te-Ze;if(Ee!=null){let be=Ee<0?te:le,He=Ee<0?le:te;pt?(Fe>0&&st[X]!=null&&de(ct.get(st[X]),me,Ze+kn(Fe/2),fe,Pn(0,ke-Fe),be,He),N[X]!=null&&de(dt.get(N[X]),me,Ze+kn(Fe/2),fe,Pn(0,ke-Fe),be,He)):de(E,me,Ze+kn(Fe/2),fe,Pn(0,ke-Fe),be,He),xe(f,g,X,me-Fe/2,Ze,fe+Fe,ke)}}return Fe>0?D.stroke=pt?ct:E:pt||(D._fill=p.width==0?p._fill:p._stroke??p._fill,D.width=0),D.fill=pt?dt:E,D})}function lb(i,e){const t=xt(e==null?void 0:e.alignGaps,0);return(n,s,r,a)=>Gs(n,s,(o,l,c,h,u,d,f,g,_,m,p)=>{[r,a]=cl(c,r,a);let S=o.pxRound,y=Y=>S(d(Y,h,m,g)),w=Y=>S(f(Y,u,p,_)),O,A,C;h.ori==0?(O=pl,C=Qr,A=Xp):(O=ml,C=ea,A=qp);const F=h.dir*(h.ori==0?1:-1);let b=y(l[F==1?r:a]),x=b,P=[],K=[];for(let Y=F==1?r:a;Y>=r&&Y<=a;Y+=F)if(c[Y]!=null){let ge=l[Y],de=y(ge);P.push(x=de),K.push(w(c[Y]))}const k={stroke:i(P,K,O,C,A,S),fill:null,clip:null,band:null,gaps:null,flags:jr},Z=k.stroke;let[q,ee]=Xh(n,s);if(o.fill!=null||q!=0){let Y=k.fill=new Path2D(Z),ne=o.fillTo(n,s,o.min,o.max,q),ge=w(ne);C(Y,x,ge),C(Y,b,ge)}if(!o.spanGaps){let Y=[];Y.push(...qh(l,c,r,a,F,y,t)),k.gaps=Y=o.gaps(n,s,r,a,Y),k.clip=fl(Y,h.ori,g,_,m,p)}return ee!=0&&(k.band=ee==2?[Gi(n,s,r,a,Z,-1),Gi(n,s,r,a,Z,1)]:Gi(n,s,r,a,Z,ee)),k})}function cb(i){return lb(hb,i)}function hb(i,e,t,n,s,r){const a=i.length;if(a<2)return null;const o=new Path2D;if(t(o,i[0],e[0]),a==2)n(o,i[1],e[1]);else{let l=Array(a),c=Array(a-1),h=Array(a-1),u=Array(a-1);for(let d=0;d<a-1;d++)h[d]=e[d+1]-e[d],u[d]=i[d+1]-i[d],c[d]=h[d]/u[d];l[0]=c[0];for(let d=1;d<a-1;d++)c[d]===0||c[d-1]===0||c[d-1]>0!=c[d]>0?l[d]=0:(l[d]=3*(u[d-1]+u[d])/((2*u[d]+u[d-1])/c[d-1]+(u[d]+2*u[d-1])/c[d]),isFinite(l[d])||(l[d]=0));l[a-1]=c[a-2];for(let d=0;d<a-1;d++)s(o,i[d]+u[d]/3,e[d]+l[d]*u[d]/3,i[d+1]-u[d]/3,e[d+1]-l[d+1]*u[d]/3,i[d+1],e[d+1])}return o}const uh=new Set;function gf(){for(let i of uh)i.syncRect(!0)}Jr&&(Os(WM,Or,gf),Os(XM,Or,gf,!0),Os(Jo,Or,()=>{fn.pxRatio=Mt}));const ub=jp(),db=$p();function _f(i,e,t,n){return(n?[i[0],i[1]].concat(i.slice(2)):[i[0]].concat(i.slice(1))).map((r,a)=>dh(r,a,e,t))}function fb(i,e){return i.map((t,n)=>n==0?{}:Jt({},e,t))}function dh(i,e,t,n){return Jt({},e==0?t:n,i)}function Kp(i,e,t){return e==null?$r:[e,t]}const pb=Kp;function mb(i,e,t){return e==null?$r:Qo(e,t,Bh,!0)}function Zp(i,e,t,n){return e==null?$r:hl(e,t,i.scales[n].log,!1)}const gb=Zp;function Jp(i,e,t,n){return e==null?$r:Oh(e,t,i.scales[n].log,!1)}const _b=Jp;function vb(i,e,t,n,s){let r=Pn(Yd(i),Yd(e)),a=e-i,o=ri(s/n*a,t);do{let l=t[o],c=n*l/a;if(c>=s&&r+(l<5?ds.get(l):0)<=17)return[l,c]}while(++o<t.length);return[0,0]}function vf(i){let e,t;return i=i.replace(/(\d+)px/,(n,s)=>(e=en((t=+s)*Mt))+"px"),[i,e,t]}function xb(i){i.show&&[i.font,i.labelFont].forEach(e=>{let t=Ct(e[2]*Mt,1);e[0]=e[0].replace(/[0-9.]+px/,t+"px"),e[1]=t})}function fn(i,e,t){const n={mode:xt(i.mode,1)},s=n.mode;function r(v,M,R,L){let z=M.valToPct(v);return L+R*(M.dir==-1?1-z:z)}function a(v,M,R,L){let z=M.valToPct(v);return L+R*(M.dir==-1?z:1-z)}function o(v,M,R,L){return M.ori==0?r(v,M,R,L):a(v,M,R,L)}n.valToPosH=r,n.valToPosV=a;let l=!1;n.status=0;const c=n.root=Xn(TM);if(i.id!=null&&(c.id=i.id),zn(c,i.class),i.title){let v=Xn(CM,c);v.textContent=i.title}const h=si("canvas"),u=n.ctx=h.getContext("2d"),d=Xn(PM,c);Os("click",d,v=>{v.target===g&&(It!=js||Ht!=Ks)&&gn.click(n,v)},!0);const f=n.under=Xn(LM,d);d.appendChild(h);const g=n.over=Xn(DM,d);i=Yr(i);const _=+xt(i.pxAlign,1),m=pf(_);(i.plugins||[]).forEach(v=>{v.opts&&(i=v.opts(n,i)||i)});const p=i.ms||.001,S=n.series=s==1?_f(i.series||[],of,df,!1):fb(i.series||[null],uf),y=n.axes=_f(i.axes||[],af,cf,!0),w=n.scales={},O=n.bands=i.bands||[];O.forEach(v=>{v.fill=ft(v.fill||null),v.dir=xt(v.dir,-1)});const A=s==2?S[1].facets[0].scale:S[0].scale,C={axes:hm,series:Dn},F=(i.drawOrder||["axes","series"]).map(v=>C[v]);function b(v){const M=v.distr==3?R=>Vi(R>0?R:v.clamp(n,R,v.min,v.max,v.key)):v.distr==4?R=>dc(R,v.asinh):v.distr==100?R=>v.fwd(R):R=>R;return R=>{let L=M(R),{_min:z,_max:j}=v,oe=j-z;return(L-z)/oe}}function x(v){let M=w[v];if(M==null){let R=(i.scales||Ra)[v]||Ra;if(R.from!=null){x(R.from);let L=Jt({},w[R.from],R,{key:v});L.valToPct=b(L),w[v]=L}else{M=w[v]=Jt({},v==A?kp:tb,R),M.key=v;let L=M.time,z=M.range,j=rs(z);if((v!=A||s==2&&!L)&&(j&&(z[0]==null||z[1]==null)&&(z={min:z[0]==null?Xd:{mode:1,hard:z[0],soft:z[0]},max:z[1]==null?Xd:{mode:1,hard:z[1],soft:z[1]}},j=!1),!j&&dl(z))){let oe=z;z=(pe,Se,De)=>Se==null?$r:Qo(Se,De,oe)}M.range=ft(z||(L?pb:v==A?M.distr==3?gb:M.distr==4?_b:Kp:M.distr==3?Zp:M.distr==4?Jp:mb)),M.auto=ft(j?!1:M.auto),M.clamp=ft(M.clamp||eb),M._min=M._max=null,M.valToPct=b(M)}}}x("x"),x("y"),s==1&&S.forEach(v=>{x(v.scale)}),y.forEach(v=>{x(v.scale)});for(let v in i.scales)x(v);const P=w[A],K=P.distr;let k,Z;P.ori==0?(zn(c,AM),k=r,Z=a):(zn(c,RM),k=a,Z=r);const q={};for(let v in w){let M=w[v];(M.min!=null||M.max!=null)&&(q[v]={min:M.min,max:M.max},M.min=M.max=null)}const ee=i.tzDate||(v=>new Date(en(v/p))),Y=i.fmtDate||Hh,ne=p==1?AS(ee):PS(ee),ge=nf(ee,tf(p==1?TS:CS,Y)),de=rf(ee,sf(DS,Y)),xe=[],we=n.legend=Jt({},NS,i.legend),ye=n.cursor=Jt({},HS,{drag:{y:s==2}},i.cursor),ie=we.show,he=ye.show,Me=we.markers;we.idxs=xe,Me.width=ft(Me.width),Me.dash=ft(Me.dash),Me.stroke=ft(Me.stroke),Me.fill=ft(Me.fill);let fe,ze,Ge,Fe=[],pt=[],N,dt=!1,st={};if(we.live){const v=S[1]?S[1].values:null;dt=v!=null,N=dt?v(n,1,0):{_:0};for(let M in N)st[M]=Nh}if(ie)if(fe=si("table",BM,c),Ge=si("tbody",null,fe),we.mount(n,fe),dt){ze=si("thead",null,fe,Ge);let v=si("tr",null,ze);si("th",null,v);for(var ct in N)si("th",Dd,v).textContent=ct}else zn(fe,kM),we.live&&zn(fe,zM);const Oe={show:!0},Et={show:!1};function $e(v,M){if(M==0&&(dt||!we.live||s==2))return $r;let R=[],L=si("tr",HM,Ge,Ge.childNodes[M]);zn(L,v.class),v.show||zn(L,Ds);let z=si("th",null,L);if(Me.show){let pe=Xn(VM,z);if(M>0){let Se=Me.width(n,M);Se&&(pe.style.border=Se+"px "+Me.dash(n,M)+" "+Me.stroke(n,M)),pe.style.background=Me.fill(n,M)}}let j=Xn(Dd,z);v.label instanceof HTMLElement?j.appendChild(v.label):j.textContent=v.label,M>0&&(Me.show||(j.style.color=v.width>0?Me.stroke(n,M):Me.fill(n,M)),D("click",z,pe=>{if(ye._lock)return;zt(pe);let Se=S.indexOf(v);if((pe.ctrlKey||pe.metaKey)!=we.isolate){let De=S.some((Ie,Ne)=>Ne>0&&Ne!=Se&&Ie.show);S.forEach((Ie,Ne)=>{Ne>0&&pi(Ne,De?Ne==Se?Oe:Et:Oe,!0,Kt.setSeries)})}else pi(Se,{show:!v.show},!0,Kt.setSeries)},!1),di&&D(Fd,z,pe=>{ye._lock||(zt(pe),pi(S.indexOf(v),Js,!0,Kt.setSeries))},!1));for(var oe in N){let pe=si("td",GM,L);pe.textContent="--",R.push(pe)}return[L,R]}const Xe=new Map;function D(v,M,R,L=!0){const z=Xe.get(M)||{},j=ye.bind[v](n,M,R,L);j&&(Os(v,M,z[v]=j),Xe.set(M,z))}function E(v,M,R){const L=Xe.get(M)||{};for(let z in L)(v==null||z==v)&&(ah(z,M,L[z]),delete L[z]);v==null&&Xe.delete(M)}let Q=0,le=0,te=0,X=0,Ee=0,_e=0,Ae=Ee,Ke=_e,me=te,Te=X,Ze=0,ke=0,be=0,He=0;n.bbox={};let B=!1,ce=!1,I=!1,ae=!1,se=!1,re=!1;function ve(v,M,R){(R||v!=n.width||M!=n.height)&&je(v,M),Xs(!1),I=!0,ce=!0,qs()}function je(v,M){n.width=Q=te=v,n.height=le=X=M,Ee=_e=0,lt(),pn();let R=n.bbox;Ze=R.left=Rs(Ee*Mt,.5),ke=R.top=Rs(_e*Mt,.5),be=R.width=Rs(te*Mt,.5),He=R.height=Rs(X*Mt,.5)}const ot=3;function _t(){let v=!1,M=0;for(;!v;){M++;let R=lm(M),L=cm(M);v=M==ot||R&&L,v||(je(n.width,n.height),ce=!0)}}function wt({width:v,height:M}){ve(v,M)}n.setSize=wt;function lt(){let v=!1,M=!1,R=!1,L=!1;y.forEach((z,j)=>{if(z.show&&z._show){let{side:oe,_size:pe}=z,Se=oe%2,De=z.label!=null?z.labelSize:0,Ie=pe+De;Ie>0&&(Se?(te-=Ie,oe==3?(Ee+=Ie,L=!0):R=!0):(X-=Ie,oe==0?(_e+=Ie,v=!0):M=!0))}}),Ai[0]=v,Ai[1]=R,Ai[2]=M,Ai[3]=L,te-=J[1]+J[3],Ee+=J[3],X-=J[2]+J[0],_e+=J[0]}function pn(){let v=Ee+te,M=_e+X,R=Ee,L=_e;function z(j,oe){switch(j){case 1:return v+=oe,v-oe;case 2:return M+=oe,M-oe;case 3:return R-=oe,R+oe;case 0:return L-=oe,L+oe}}y.forEach((j,oe)=>{if(j.show&&j._show){let pe=j.side;j._pos=z(pe,j._size),j.label!=null&&(j._lpos=z(pe,j.labelSize))}})}if(ye.dataIdx==null){let v=ye.hover,M=v.skip=new Set(v.skip??[]);M.add(void 0);let R=v.prox=ft(v.prox),L=v.bias??(v.bias=0);ye.dataIdx=(z,j,oe,pe)=>{if(j==0)return oe;let Se=oe,De=R(z,j,oe,pe)??Rt,Ie=De>=0&&De<Rt,Ne=P.ori==0?te:X,tt=ye.left,yt=e[0],vt=e[j];if(M.has(vt[oe])){Se=null;let ut=null,et=null,We;if(L==0||L==-1)for(We=oe;ut==null&&We-- >0;)M.has(vt[We])||(ut=We);if(L==0||L==1)for(We=oe;et==null&&We++<vt.length;)M.has(vt[We])||(et=We);if(ut!=null||et!=null)if(Ie){let Nt=ut==null?-1/0:k(yt[ut],P,Ne,0),Gt=et==null?1/0:k(yt[et],P,Ne,0),un=tt-Nt,At=Gt-tt;un<=At?un<=De&&(Se=ut):At<=De&&(Se=et)}else Se=et==null?ut:ut==null?et:oe-ut<=et-oe?ut:et}else Ie&&tn(tt-k(yt[oe],P,Ne,0))>De&&(Se=null);return Se}}const zt=v=>{ye.event=v};ye.idxs=xe,ye._lock=!1;let kt=ye.points;kt.show=ft(kt.show),kt.size=ft(kt.size),kt.stroke=ft(kt.stroke),kt.width=ft(kt.width),kt.fill=ft(kt.fill);const on=n.focus=Jt({},i.focus||{alpha:.3},ye.focus),di=on.prox>=0,wi=di&&kt.one;let En=[],Jn=[],Ti=[];function gs(v,M){let R=kt.show(n,M);if(R instanceof HTMLElement)return zn(R,OM),zn(R,v.class),vi(R,-10,-10,te,X),g.insertBefore(R,En[M]),R}function ia(v,M){if(s==1||M>0){let R=s==1&&w[v.scale].time,L=v.value;v.value=R?Zd(L)?rf(ee,sf(L,Y)):L||de:L||ZS,v.label=v.label||(R?GS:VS)}if(wi||M>0){v.width=v.width==null?1:v.width,v.paths=v.paths||ub||tS,v.fillTo=ft(v.fillTo||nb),v.pxAlign=+xt(v.pxAlign,_),v.pxRound=pf(v.pxAlign),v.stroke=ft(v.stroke||null),v.fill=ft(v.fill||null),v._stroke=v._fill=v._paths=v._focus=null;let R=JS(Pn(1,v.width),1),L=v.points=Jt({},{size:R,width:Pn(1,R*.2),stroke:v.stroke,space:R*2,paths:db,_stroke:null,_fill:null},v.points);L.show=ft(L.show),L.filter=ft(L.filter),L.fill=ft(L.fill),L.stroke=ft(L.stroke),L.paths=ft(L.paths),L.pxAlign=v.pxAlign}if(ie){let R=$e(v,M);Fe.splice(M,0,R[0]),pt.splice(M,0,R[1]),we.values.push(null)}if(he){xe.splice(M,0,null);let R=null;wi?M==0&&(R=gs(v,M)):M>0&&(R=gs(v,M)),En.splice(M,0,R),Jn.splice(M,0,0),Ti.splice(M,0,0)}hn("addSeries",M)}function ka(v,M){M=M??S.length,v=s==1?dh(v,M,of,df):dh(v,M,{},uf),S.splice(M,0,v),ia(S[M],M)}n.addSeries=ka;function xl(v){if(S.splice(v,1),ie){we.values.splice(v,1),pt.splice(v,1);let M=Fe.splice(v,1)[0];E(null,M.firstChild),M.remove()}he&&(xe.splice(v,1),En.splice(v,1)[0].remove(),Jn.splice(v,1),Ti.splice(v,1)),hn("delSeries",v)}n.delSeries=xl;const Ai=[!1,!1,!1,!1];function yl(v,M){if(v._show=v.show,v.show){let R=v.side%2,L=w[v.scale];L==null&&(v.scale=R?S[1].scale:A,L=w[v.scale]);let z=L.time;v.size=ft(v.size),v.space=ft(v.space),v.rotate=ft(v.rotate),rs(v.incrs)&&v.incrs.forEach(oe=>{!ds.has(oe)&&ds.set(oe,Mp(oe))}),v.incrs=ft(v.incrs||(L.distr==2?bS:z?p==1?wS:RS:Cs)),v.splits=ft(v.splits||(z&&L.distr==1?ne:L.distr==3?lh:L.distr==4?qS:XS)),v.stroke=ft(v.stroke),v.grid.stroke=ft(v.grid.stroke),v.ticks.stroke=ft(v.ticks.stroke),v.border.stroke=ft(v.border.stroke);let j=v.values;v.values=rs(j)&&!rs(j[0])?ft(j):z?rs(j)?nf(ee,tf(j,Y)):Zd(j)?LS(ee,j):j||ge:j||WS,v.filter=ft(v.filter||(L.distr>=3&&L.log==10?jS:L.distr==3&&L.log==2?KS:xp)),v.font=vf(v.font),v.labelFont=vf(v.labelFont),v._size=v.size(n,null,M,0),v._space=v._rotate=v._incrs=v._found=v._splits=v._values=null,v._size>0&&(Ai[M]=!0,v._el=Xn(IM,d))}}function T(v,M,R,L){let[z,j,oe,pe]=R,Se=M%2,De=0;return Se==0&&(pe||j)&&(De=M==0&&!z||M==2&&!oe?en(af.size/3):0),Se==1&&(z||oe)&&(De=M==1&&!j||M==3&&!pe?en(cf.size/2):0),De}const W=n.padding=(i.padding||[T,T,T,T]).map(v=>ft(xt(v,T))),J=n._padding=W.map((v,M)=>v(n,M,Ai,0));let $,G=null,ue=null;const Ce=s==1?S[0].idxs:null;let Pe=null,Ue=!1;function Je(v,M){if(e=v??[],n.data=n._data=e,s==2){$=0;for(let R=1;R<S.length;R++)$+=e[R][0].length}else{e.length==0&&(n.data=n._data=e=[[]]),Pe=e[0],$=Pe.length;let R=e;if(K==2){R=e.slice();let L=R[0]=Array($);for(let z=0;z<$;z++)L[z]=z}n._data=e=R}if(Xs(!0),hn("setData"),K==2&&(I=!0),M!==!1){let R=P;R.auto(n,Ue)?Qe():Yi(A,R.min,R.max),ae=ae||ye.left>=0,re=!0,qs()}}n.setData=Je;function Qe(){Ue=!0;let v,M;s==1&&($>0?(G=Ce[0]=0,ue=Ce[1]=$-1,v=e[0][G],M=e[0][ue],K==2?(v=G,M=ue):v==M&&(K==3?[v,M]=hl(v,v,P.log,!1):K==4?[v,M]=Oh(v,v,P.log,!1):P.time?M=v+en(86400/p):[v,M]=Qo(v,M,Bh,!0))):(G=Ce[0]=v=null,ue=Ce[1]=M=null)),Yi(A,v,M)}let Be,ht,Pt,Lt,mn,mt,Ve,$t,gt,Dt;function Ri(v,M,R,L,z,j){v??(v=Ud),R??(R=kh),L??(L="butt"),z??(z=Ud),j??(j="round"),v!=Be&&(u.strokeStyle=Be=v),z!=ht&&(u.fillStyle=ht=z),M!=Pt&&(u.lineWidth=Pt=M),j!=mn&&(u.lineJoin=mn=j),L!=mt&&(u.lineCap=mt=L),R!=Lt&&u.setLineDash(Lt=R)}function xn(v,M,R,L){M!=ht&&(u.fillStyle=ht=M),v!=Ve&&(u.font=Ve=v),R!=$t&&(u.textAlign=$t=R),L!=gt&&(u.textBaseline=gt=L)}function _s(v,M,R,L,z=0){if(L.length>0&&v.auto(n,Ue)&&(M==null||M.min==null)){let j=xt(G,0),oe=xt(ue,L.length-1),pe=R.min==null?jM(L,j,oe,z,v.distr==3):[R.min,R.max];v.min=li(v.min,R.min=pe[0]),v.max=Pn(v.max,R.max=pe[1])}}const Vt={min:null,max:null};function fi(){for(let L in w){let z=w[L];q[L]==null&&(z.min==null||q[A]!=null&&z.auto(n,Ue))&&(q[L]=Vt)}for(let L in w){let z=w[L];q[L]==null&&z.from!=null&&q[z.from]!=null&&(q[L]=Vt)}q[A]!=null&&Xs(!0);let v={};for(let L in q){let z=q[L];if(z!=null){let j=v[L]=Yr(w[L],sS);if(z.min!=null)Jt(j,z);else if(L!=A||s==2)if($==0&&j.from==null){let oe=j.range(n,null,null,L);j.min=oe[0],j.max=oe[1]}else j.min=Rt,j.max=-Rt}}if($>0){S.forEach((L,z)=>{if(s==1){let j=L.scale,oe=q[j];if(oe==null)return;let pe=v[j];if(z==0){let Se=pe.range(n,pe.min,pe.max,j);pe.min=Se[0],pe.max=Se[1],G=ri(pe.min,e[0]),ue=ri(pe.max,e[0]),ue-G>1&&(e[0][G]<pe.min&&G++,e[0][ue]>pe.max&&ue--),L.min=Pe[G],L.max=Pe[ue]}else L.show&&L.auto&&_s(pe,oe,L,e[z],L.sorted);L.idxs[0]=G,L.idxs[1]=ue}else if(z>0&&L.show&&L.auto){let[j,oe]=L.facets,pe=j.scale,Se=oe.scale,[De,Ie]=e[z],Ne=v[pe],tt=v[Se];Ne!=null&&_s(Ne,q[pe],j,De,j.sorted),tt!=null&&_s(tt,q[Se],oe,Ie,oe.sorted),L.min=oe.min,L.max=oe.max}});for(let L in v){let z=v[L],j=q[L];if(z.from==null&&(j==null||j.min==null)){let oe=z.range(n,z.min==Rt?null:z.min,z.max==-Rt?null:z.max,L);z.min=oe[0],z.max=oe[1]}}}for(let L in v){let z=v[L];if(z.from!=null){let j=v[z.from];if(j.min==null)z.min=z.max=null;else{let oe=z.range(n,j.min,j.max,L);z.min=oe[0],z.max=oe[1]}}}let M={},R=!1;for(let L in v){let z=v[L],j=w[L];if(j.min!=z.min||j.max!=z.max){j.min=z.min,j.max=z.max;let oe=j.distr;j._min=oe==3?Vi(j.min):oe==4?dc(j.min,j.asinh):oe==100?j.fwd(j.min):j.min,j._max=oe==3?Vi(j.max):oe==4?dc(j.max,j.asinh):oe==100?j.fwd(j.max):j.max,M[L]=R=!0}}if(R){S.forEach((L,z)=>{s==2?z>0&&M.y&&(L._paths=null):M[L.scale]&&(L._paths=null)});for(let L in M)I=!0,hn("setScale",L);he&&ye.left>=0&&(ae=re=!0)}for(let L in q)q[L]=null}function sa(v){let M=oh(G-1,0,$-1),R=oh(ue+1,0,$-1);for(;v[M]==null&&M>0;)M--;for(;v[R]==null&&R<$-1;)R++;return[M,R]}function Dn(){if($>0){let v=S.some(M=>M._focus)&&Dt!=on.alpha;v&&(u.globalAlpha=Dt=on.alpha),S.forEach((M,R)=>{if(R>0&&M.show&&(Ws(R,!1),Ws(R,!0),M._paths==null)){let L=Dt;Dt!=M.alpha&&(u.globalAlpha=Dt=M.alpha);let z=s==2?[0,e[R][0].length-1]:sa(e[R]);M._paths=M.paths(n,R,z[0],z[1]),Dt!=L&&(u.globalAlpha=Dt=L)}}),S.forEach((M,R)=>{if(R>0&&M.show){let L=Dt;Dt!=M.alpha&&(u.globalAlpha=Dt=M.alpha),M._paths!=null&&Ha(R,!1);{let z=M._paths!=null?M._paths.gaps:null,j=M.points.show(n,R,G,ue,z),oe=M.points.filter(n,R,j,z);(j||oe)&&(M.points._paths=M.points.paths(n,R,G,ue,oe),Ha(R,!0))}Dt!=L&&(u.globalAlpha=Dt=L),hn("drawSeries",R)}}),v&&(u.globalAlpha=Dt=1)}}function Ws(v,M){let R=M?S[v].points:S[v];R._stroke=R.stroke(n,v),R._fill=R.fill(n,v)}function Ha(v,M){let R=M?S[v].points:S[v],{stroke:L,fill:z,clip:j,flags:oe,_stroke:pe=R._stroke,_fill:Se=R._fill,_width:De=R.width}=R._paths;De=Ct(De*Mt,3);let Ie=null,Ne=De%2/2;M&&Se==null&&(Se=De>0?"#fff":pe);let tt=R.pxAlign==1&&Ne>0;if(tt&&u.translate(Ne,Ne),!M){let yt=Ze-De/2,vt=ke-De/2,ut=be+De,et=He+De;Ie=new Path2D,Ie.rect(yt,vt,ut,et)}M?Ml(pe,De,R.dash,R.cap,Se,L,z,oe,j):Va(v,pe,De,R.dash,R.cap,Se,L,z,oe,Ie,j),tt&&u.translate(-Ne,-Ne)}function Va(v,M,R,L,z,j,oe,pe,Se,De,Ie){let Ne=!1;Se!=0&&O.forEach((tt,yt)=>{if(tt.series[0]==v){let vt=S[tt.series[1]],ut=e[tt.series[1]],et=(vt._paths||Ra).band;rs(et)&&(et=tt.dir==1?et[0]:et[1]);let We,Nt=null;vt.show&&et&&ZM(ut,G,ue)?(Nt=tt.fill(n,yt)||j,We=vt._paths.clip):et=null,Ml(M,R,L,z,Nt,oe,pe,Se,De,Ie,We,et),Ne=!0}}),Ne||Ml(M,R,L,z,j,oe,pe,Se,De,Ie)}const Qh=jr|hh;function Ml(v,M,R,L,z,j,oe,pe,Se,De,Ie,Ne){Ri(v,M,R,L,z),(Se||De||Ne)&&(u.save(),Se&&u.clip(Se),De&&u.clip(De)),Ne?(pe&Qh)==Qh?(u.clip(Ne),Ie&&u.clip(Ie),Wa(z,oe),Ga(v,j,M)):pe&hh?(Wa(z,oe),u.clip(Ne),Ga(v,j,M)):pe&jr&&(u.save(),u.clip(Ne),Ie&&u.clip(Ie),Wa(z,oe),u.restore(),Ga(v,j,M)):(Wa(z,oe),Ga(v,j,M)),(Se||De||Ne)&&u.restore()}function Ga(v,M,R){R>0&&(M instanceof Map?M.forEach((L,z)=>{u.strokeStyle=Be=z,u.stroke(L)}):M!=null&&v&&u.stroke(M))}function Wa(v,M){M instanceof Map?M.forEach((R,L)=>{u.fillStyle=ht=L,u.fill(R)}):M!=null&&v&&u.fill(M)}function om(v,M,R,L){let z=y[v],j;if(L<=0)j=[0,0];else{let oe=z._space=z.space(n,v,M,R,L),pe=z._incrs=z.incrs(n,v,M,R,L,oe);j=vb(M,R,pe,L,oe)}return z._found=j}function Sl(v,M,R,L,z,j,oe,pe,Se,De){let Ie=oe%2/2;_==1&&u.translate(Ie,Ie),Ri(pe,oe,Se,De,pe),u.beginPath();let Ne,tt,yt,vt,ut=z+(L==0||L==3?-j:j);R==0?(tt=z,vt=ut):(Ne=z,yt=ut);for(let et=0;et<v.length;et++)M[et]!=null&&(R==0?Ne=yt=v[et]:tt=vt=v[et],u.moveTo(Ne,tt),u.lineTo(yt,vt));u.stroke(),_==1&&u.translate(-Ie,-Ie)}function lm(v){let M=!0;return y.forEach((R,L)=>{if(!R.show)return;let z=w[R.scale];if(z.min==null){R._show&&(M=!1,R._show=!1,Xs(!1));return}else R._show||(M=!1,R._show=!0,Xs(!1));let j=R.side,oe=j%2,{min:pe,max:Se}=z,[De,Ie]=om(L,pe,Se,oe==0?te:X);if(Ie==0)return;let Ne=z.distr==2,tt=R._splits=R.splits(n,L,pe,Se,De,Ie,Ne),yt=z.distr==2?tt.map(We=>Pe[We]):tt,vt=z.distr==2?Pe[tt[1]]-Pe[tt[0]]:De,ut=R._values=R.values(n,R.filter(n,yt,L,Ie,vt),L,Ie,vt);R._rotate=j==2?R.rotate(n,ut,L,Ie):0;let et=R._size;R._size=$n(R.size(n,ut,L,v)),et!=null&&R._size!=et&&(M=!1)}),M}function cm(v){let M=!0;return W.forEach((R,L)=>{let z=R(n,L,Ai,v);z!=J[L]&&(M=!1),J[L]=z}),M}function hm(){for(let v=0;v<y.length;v++){let M=y[v];if(!M.show||!M._show)continue;let R=M.side,L=R%2,z,j,oe=M.stroke(n,v),pe=R==0||R==3?-1:1,[Se,De]=M._found;if(M.label!=null){let Tn=M.labelGap*pe,Fn=en((M._lpos+Tn)*Mt);xn(M.labelFont[0],oe,"center",R==2?xa:Id),u.save(),L==1?(z=j=0,u.translate(Fn,en(ke+He/2)),u.rotate((R==3?-zo:zo)/2)):(z=en(Ze+be/2),j=Fn);let ys=_p(M.label)?M.label(n,v,Se,De):M.label;u.fillText(ys,z,j),u.restore()}if(De==0)continue;let Ie=w[M.scale],Ne=L==0?be:He,tt=L==0?Ze:ke,yt=M._splits,vt=Ie.distr==2?yt.map(Tn=>Pe[Tn]):yt,ut=Ie.distr==2?Pe[yt[1]]-Pe[yt[0]]:Se,et=M.ticks,We=M.border,Nt=et.show?et.size:0,Gt=en(Nt*Mt),un=en((M.alignTo==2?M._size-Nt-M.gap:M.gap)*Mt),At=M._rotate*-zo/180,Wt=m(M._pos*Mt),Un=(Gt+un)*pe,wn=Wt+Un;j=L==0?wn:0,z=L==1?wn:0;let Vn=M.font[0],Qn=M.align==1?br:M.align==2?cc:At>0?br:At<0?cc:L==0?"center":R==3?cc:br,gi=At||L==1?"middle":R==2?xa:Id;xn(Vn,oe,Qn,gi);let Nn=M.font[1]*M.lineGap,Gn=yt.map(Tn=>m(o(Tn,Ie,Ne,tt))),ei=M._values;for(let Tn=0;Tn<ei.length;Tn++){let Fn=ei[Tn];if(Fn!=null){L==0?z=Gn[Tn]:j=Gn[Tn],Fn=""+Fn;let ys=Fn.indexOf(`
`)==-1?[Fn]:Fn.split(/\n/gm);for(let An=0;An<ys.length;An++){let vu=ys[An];At?(u.save(),u.translate(z,j+An*Nn),u.rotate(At),u.fillText(vu,0,0),u.restore()):u.fillText(vu,z,j+An*Nn)}}}et.show&&Sl(Gn,et.filter(n,vt,v,De,ut),L,R,Wt,Gt,Ct(et.width*Mt,3),et.stroke(n,v),et.dash,et.cap);let _i=M.grid;_i.show&&Sl(Gn,_i.filter(n,vt,v,De,ut),L,L==0?2:1,L==0?ke:Ze,L==0?He:be,Ct(_i.width*Mt,3),_i.stroke(n,v),_i.dash,_i.cap),We.show&&Sl([Wt],[1],L==0?1:0,L==0?1:2,L==1?ke:Ze,L==1?He:be,Ct(We.width*Mt,3),We.stroke(n,v),We.dash,We.cap)}hn("drawAxes")}function Xs(v){S.forEach((M,R)=>{R>0&&(M._paths=null,v&&(s==1?(M.min=null,M.max=null):M.facets.forEach(L=>{L.min=null,L.max=null})))})}let Xa=!1,bl=!1,ra=[];function um(){bl=!1;for(let v=0;v<ra.length;v++)hn(...ra[v]);ra.length=0}function qs(){Xa||(uS(eu),Xa=!0)}function dm(v,M=!1){Xa=!0,bl=M,v(n),eu(),M&&ra.length>0&&queueMicrotask(um)}n.batch=dm;function eu(){if(B&&(fi(),B=!1),I&&(_t(),I=!1),ce){if(Ft(f,br,Ee),Ft(f,xa,_e),Ft(f,ba,te),Ft(f,Ea,X),Ft(g,br,Ee),Ft(g,xa,_e),Ft(g,ba,te),Ft(g,Ea,X),Ft(d,ba,Q),Ft(d,Ea,le),h.width=en(Q*Mt),h.height=en(le*Mt),y.forEach(({_el:v,_show:M,_size:R,_pos:L,side:z})=>{if(v!=null)if(M){let j=z===3||z===0?R:0,oe=z%2==1;Ft(v,oe?"left":"top",L-j),Ft(v,oe?"width":"height",R),Ft(v,oe?"top":"left",oe?_e:Ee),Ft(v,oe?"height":"width",oe?X:te),rh(v,Ds)}else zn(v,Ds)}),Be=ht=Pt=mn=mt=Ve=$t=gt=Lt=null,Dt=1,la(!0),Ee!=Ae||_e!=Ke||te!=me||X!=Te){Xs(!1);let v=te/me,M=X/Te;if(he&&!ae&&ye.left>=0){ye.left*=v,ye.top*=M,$s&&vi($s,en(ye.left),0,te,X),Ys&&vi(Ys,0,en(ye.top),te,X);for(let R=0;R<En.length;R++){let L=En[R];L!=null&&(Jn[R]*=v,Ti[R]*=M,vi(L,$n(Jn[R]),$n(Ti[R]),te,X))}}if(Ut.show&&!se&&Ut.left>=0&&Ut.width>0){Ut.left*=v,Ut.width*=v,Ut.top*=M,Ut.height*=M;for(let R in Cl)Ft(Zs,R,Ut[R])}Ae=Ee,Ke=_e,me=te,Te=X}hn("setSize"),ce=!1}Q>0&&le>0&&(u.clearRect(0,0,h.width,h.height),hn("drawClear"),F.forEach(v=>v()),hn("draw")),Ut.show&&se&&(qa(Ut),se=!1),he&&ae&&(xs(null,!0,!1),ae=!1),we.show&&we.live&&re&&(Al(),re=!1),l||(l=!0,n.status=1,hn("ready")),Ue=!1,Xa=!1}n.redraw=(v,M)=>{I=M||!1,v!==!1?Yi(A,P.min,P.max):qs()};function El(v,M){let R=w[v];if(R.from==null){if($==0){let L=R.range(n,M.min,M.max,v);M.min=L[0],M.max=L[1]}if(M.min>M.max){let L=M.min;M.min=M.max,M.max=L}if($>1&&M.min!=null&&M.max!=null&&M.max-M.min<1e-16)return;v==A&&R.distr==2&&$>0&&(M.min=ri(M.min,e[0]),M.max=ri(M.max,e[0]),M.min==M.max&&M.max++),q[v]=M,B=!0,qs()}}n.setScale=El;let wl,Tl,$s,Ys,tu,nu,js,Ks,iu,su,It,Ht,$i=!1;const gn=ye.drag;let ln=gn.x,cn=gn.y;he&&(ye.x&&(wl=Xn(NM,g)),ye.y&&(Tl=Xn(FM,g)),P.ori==0?($s=wl,Ys=Tl):($s=Tl,Ys=wl),It=ye.left,Ht=ye.top);const Ut=n.select=Jt({show:!0,over:!0,left:0,width:0,top:0,height:0},i.select),Zs=Ut.show?Xn(UM,Ut.over?g:f):null;function qa(v,M){if(Ut.show){for(let R in v)Ut[R]=v[R],R in Cl&&Ft(Zs,R,v[R]);M!==!1&&hn("setSelect")}}n.setSelect=qa;function fm(v){if(S[v].show)ie&&rh(Fe[v],Ds);else if(ie&&zn(Fe[v],Ds),he){let R=wi?En[0]:En[v];R!=null&&vi(R,-10,-10,te,X)}}function Yi(v,M,R){El(v,{min:M,max:R})}function pi(v,M,R,L){M.focus!=null&&vm(v),M.show!=null&&S.forEach((z,j)=>{j>0&&(v==j||v==null)&&(z.show=M.show,fm(j),s==2?(Yi(z.facets[0].scale,null,null),Yi(z.facets[1].scale,null,null)):Yi(z.scale,null,null),qs())}),R!==!1&&hn("setSeries",v,M),L&&ca("setSeries",n,v,M)}n.setSeries=pi;function pm(v,M){Jt(O[v],M)}function mm(v,M){v.fill=ft(v.fill||null),v.dir=xt(v.dir,-1),M=M??O.length,O.splice(M,0,v)}function gm(v){v==null?O.length=0:O.splice(v,1)}n.addBand=mm,n.setBand=pm,n.delBand=gm;function _m(v,M){S[v].alpha=M,he&&En[v]!=null&&(En[v].style.opacity=M),ie&&Fe[v]&&(Fe[v].style.opacity=M)}let Ci,ji,vs;const Js={focus:!0};function vm(v){if(v!=vs){let M=v==null,R=on.alpha!=1;S.forEach((L,z)=>{if(s==1||z>0){let j=M||z==0||z==v;L._focus=M?null:j,R&&_m(z,j?1:on.alpha)}}),vs=v,R&&qs()}}ie&&di&&D(Od,fe,v=>{ye._lock||(zt(v),vs!=null&&pi(null,Js,!0,Kt.setSeries))});function mi(v,M,R){let L=w[M];R&&(v=v/Mt-(L.ori==1?_e:Ee));let z=te;L.ori==1&&(z=X,v=z-v),L.dir==-1&&(v=z-v);let j=L._min,oe=L._max,pe=v/z,Se=j+(oe-j)*pe,De=L.distr;return De==3?qr(10,Se):De==4?QM(Se,L.asinh):De==100?L.bwd(Se):Se}function xm(v,M){let R=mi(v,A,M);return ri(R,e[0],G,ue)}n.valToIdx=v=>ri(v,e[0]),n.posToIdx=xm,n.posToVal=mi,n.valToPos=(v,M,R)=>w[M].ori==0?r(v,w[M],R?be:te,R?Ze:0):a(v,w[M],R?He:X,R?ke:0),n.setCursor=(v,M,R)=>{It=v.left,Ht=v.top,xs(null,M,R)};function ru(v,M){Ft(Zs,br,Ut.left=v),Ft(Zs,ba,Ut.width=M)}function au(v,M){Ft(Zs,xa,Ut.top=v),Ft(Zs,Ea,Ut.height=M)}let aa=P.ori==0?ru:au,oa=P.ori==1?ru:au;function ym(){if(ie&&we.live)for(let v=s==2?1:0;v<S.length;v++){if(v==0&&dt)continue;let M=we.values[v],R=0;for(let L in M)pt[v][R++].firstChild.nodeValue=M[L]}}function Al(v,M){if(v!=null&&(v.idxs?v.idxs.forEach((R,L)=>{xe[L]=R}):iS(v.idx)||xe.fill(v.idx),we.idx=xe[0]),ie&&we.live){for(let R=0;R<S.length;R++)(R>0||s==1&&!dt)&&Mm(R,xe[R]);ym()}re=!1,M!==!1&&hn("setLegend")}n.setLegend=Al;function Mm(v,M){let R=S[v],L=v==0&&K==2?Pe:e[v],z;dt?z=R.values(n,v,M)??st:(z=R.value(n,M==null?null:L[M],v,M),z=z==null?st:{_:z}),we.values[v]=z}function xs(v,M,R){iu=It,su=Ht,[It,Ht]=ye.move(n,It,Ht),ye.left=It,ye.top=Ht,he&&($s&&vi($s,en(It),0,te,X),Ys&&vi(Ys,0,en(Ht),te,X));let L,z=G>ue;Ci=Rt,ji=null;let j=P.ori==0?te:X,oe=P.ori==1?te:X;if(It<0||$==0||z){L=ye.idx=null;for(let pe=0;pe<S.length;pe++){let Se=En[pe];Se!=null&&vi(Se,-10,-10,te,X)}di&&pi(null,Js,!0,v==null&&Kt.setSeries),we.live&&(xe.fill(L),re=!0)}else{let pe,Se,De;s==1&&(pe=P.ori==0?It:Ht,Se=mi(pe,A),L=ye.idx=ri(Se,e[0],G,ue),De=k(e[0][L],P,j,0));let Ie=-10,Ne=-10,tt=0,yt=0,vt=!0,ut="",et="";for(let We=s==2?1:0;We<S.length;We++){let Nt=S[We],Gt=xe[We],un=Gt==null?null:s==1?e[We][Gt]:e[We][1][Gt],At=ye.dataIdx(n,We,L,Se),Wt=At==null?null:s==1?e[We][At]:e[We][1][At];if(re=re||Wt!=un||At!=Gt,xe[We]=At,We>0&&Nt.show){let Un=At==null?-10:At==L?De:k(s==1?e[0][At]:e[We][0][At],P,j,0),wn=Wt==null?-10:Z(Wt,s==1?w[Nt.scale]:w[Nt.facets[1].scale],oe,0);if(di&&Wt!=null){let Vn=P.ori==1?It:Ht,Qn=tn(on.dist(n,We,At,wn,Vn));if(Qn<Ci){let gi=on.bias;if(gi!=0){let Nn=mi(Vn,Nt.scale),Gn=Wt>=0?1:-1,ei=Nn>=0?1:-1;ei==Gn&&(ei==1?gi==1?Wt>=Nn:Wt<=Nn:gi==1?Wt<=Nn:Wt>=Nn)&&(Ci=Qn,ji=We)}else Ci=Qn,ji=We}}if(re||wi){let Vn,Qn;P.ori==0?(Vn=Un,Qn=wn):(Vn=wn,Qn=Un);let gi,Nn,Gn,ei,_i,Tn,Fn=!0,ys=kt.bbox;if(ys!=null){Fn=!1;let An=ys(n,We);Gn=An.left,ei=An.top,gi=An.width,Nn=An.height}else Gn=Vn,ei=Qn,gi=Nn=kt.size(n,We);if(Tn=kt.fill(n,We),_i=kt.stroke(n,We),wi)We==ji&&Ci<=on.prox&&(Ie=Gn,Ne=ei,tt=gi,yt=Nn,vt=Fn,ut=Tn,et=_i);else{let An=En[We];An!=null&&(Jn[We]=Gn,Ti[We]=ei,Wd(An,gi,Nn,Fn),Vd(An,Tn,_i),vi(An,$n(Gn),$n(ei),te,X))}}}}if(wi){let We=on.prox,Nt=vs==null?Ci<=We:Ci>We||ji!=vs;if(re||Nt){let Gt=En[0];Gt!=null&&(Jn[0]=Ie,Ti[0]=Ne,Wd(Gt,tt,yt,vt),Vd(Gt,ut,et),vi(Gt,$n(Ie),$n(Ne),te,X))}}}if(Ut.show&&$i)if(v!=null){let[pe,Se]=Kt.scales,[De,Ie]=Kt.match,[Ne,tt]=v.cursor.sync.scales,yt=v.cursor.drag;if(ln=yt._x,cn=yt._y,ln||cn){let{left:vt,top:ut,width:et,height:We}=v.select,Nt=v.scales[Ne].ori,Gt=v.posToVal,un,At,Wt,Un,wn,Vn=pe!=null&&De(pe,Ne),Qn=Se!=null&&Ie(Se,tt);Vn&&ln?(Nt==0?(un=vt,At=et):(un=ut,At=We),Wt=w[pe],Un=k(Gt(un,Ne),Wt,j,0),wn=k(Gt(un+At,Ne),Wt,j,0),aa(li(Un,wn),tn(wn-Un))):aa(0,j),Qn&&cn?(Nt==1?(un=vt,At=et):(un=ut,At=We),Wt=w[Se],Un=Z(Gt(un,tt),Wt,oe,0),wn=Z(Gt(un+At,tt),Wt,oe,0),oa(li(Un,wn),tn(wn-Un))):oa(0,oe)}else Pl()}else{let pe=tn(iu-tu),Se=tn(su-nu);if(P.ori==1){let tt=pe;pe=Se,Se=tt}ln=gn.x&&pe>=gn.dist,cn=gn.y&&Se>=gn.dist;let De=gn.uni;De!=null?ln&&cn&&(ln=pe>=De,cn=Se>=De,!ln&&!cn&&(Se>pe?cn=!0:ln=!0)):gn.x&&gn.y&&(ln||cn)&&(ln=cn=!0);let Ie,Ne;ln&&(P.ori==0?(Ie=js,Ne=It):(Ie=Ks,Ne=Ht),aa(li(Ie,Ne),tn(Ne-Ie)),cn||oa(0,oe)),cn&&(P.ori==1?(Ie=js,Ne=It):(Ie=Ks,Ne=Ht),oa(li(Ie,Ne),tn(Ne-Ie)),ln||aa(0,j)),!ln&&!cn&&(aa(0,0),oa(0,0))}if(gn._x=ln,gn._y=cn,v==null){if(R){if(_u!=null){let[pe,Se]=Kt.scales;Kt.values[0]=pe!=null?mi(P.ori==0?It:Ht,pe):null,Kt.values[1]=Se!=null?mi(P.ori==1?It:Ht,Se):null}ca(hc,n,It,Ht,te,X,L)}if(di){let pe=R&&Kt.setSeries,Se=on.prox;vs==null?Ci<=Se&&pi(ji,Js,!0,pe):Ci>Se?pi(null,Js,!0,pe):ji!=vs&&pi(ji,Js,!0,pe)}}re&&(we.idx=L,Al()),M!==!1&&hn("setCursor")}let Ki=null;Object.defineProperty(n,"rect",{get(){return Ki==null&&la(!1),Ki}});function la(v=!1){v?Ki=null:(Ki=g.getBoundingClientRect(),hn("syncRect",Ki))}function ou(v,M,R,L,z,j,oe){ye._lock||$i&&v!=null&&v.movementX==0&&v.movementY==0||(Rl(v,M,R,L,z,j,oe,!1,v!=null),v!=null?xs(null,!0,!0):xs(M,!0,!1))}function Rl(v,M,R,L,z,j,oe,pe,Se){if(Ki==null&&la(!1),zt(v),v!=null)R=v.clientX-Ki.left,L=v.clientY-Ki.top;else{if(R<0||L<0){It=-10,Ht=-10;return}let[De,Ie]=Kt.scales,Ne=M.cursor.sync,[tt,yt]=Ne.values,[vt,ut]=Ne.scales,[et,We]=Kt.match,Nt=M.axes[0].side%2==1,Gt=P.ori==0?te:X,un=P.ori==1?te:X,At=Nt?j:z,Wt=Nt?z:j,Un=Nt?L:R,wn=Nt?R:L;if(vt!=null?R=et(De,vt)?o(tt,w[De],Gt,0):-10:R=Gt*(Un/At),ut!=null?L=We(Ie,ut)?o(yt,w[Ie],un,0):-10:L=un*(wn/Wt),P.ori==1){let Vn=R;R=L,L=Vn}}Se&&(M==null||M.cursor.event.type==hc)&&((R<=1||R>=te-1)&&(R=Rs(R,te)),(L<=1||L>=X-1)&&(L=Rs(L,X))),pe?(tu=R,nu=L,[js,Ks]=ye.move(n,R,L)):(It=R,Ht=L)}const Cl={width:0,height:0,left:0,top:0};function Pl(){qa(Cl,!1)}let lu,cu,hu,uu;function du(v,M,R,L,z,j,oe){$i=!0,ln=cn=gn._x=gn._y=!1,Rl(v,M,R,L,z,j,oe,!0,!1),v!=null&&(D(uc,ih,fu,!1),ca(Nd,n,js,Ks,te,X,null));let{left:pe,top:Se,width:De,height:Ie}=Ut;lu=pe,cu=Se,hu=De,uu=Ie}function fu(v,M,R,L,z,j,oe){$i=gn._x=gn._y=!1,Rl(v,M,R,L,z,j,oe,!1,!0);let{left:pe,top:Se,width:De,height:Ie}=Ut,Ne=De>0||Ie>0,tt=lu!=pe||cu!=Se||hu!=De||uu!=Ie;if(Ne&&tt&&qa(Ut),gn.setScale&&Ne&&tt){let yt=pe,vt=De,ut=Se,et=Ie;if(P.ori==1&&(yt=Se,vt=Ie,ut=pe,et=De),ln&&Yi(A,mi(yt,A),mi(yt+vt,A)),cn)for(let We in w){let Nt=w[We];We!=A&&Nt.from==null&&Nt.min!=Rt&&Yi(We,mi(ut+et,We),mi(ut,We))}Pl()}else ye.lock&&(ye._lock=!ye._lock,xs(M,!0,v!=null));v!=null&&(E(uc,ih),ca(uc,n,It,Ht,te,X,null))}function Sm(v,M,R,L,z,j,oe){if(ye._lock)return;zt(v);let pe=$i;if($i){let Se=!0,De=!0,Ie=10,Ne,tt;P.ori==0?(Ne=ln,tt=cn):(Ne=cn,tt=ln),Ne&&tt&&(Se=It<=Ie||It>=te-Ie,De=Ht<=Ie||Ht>=X-Ie),Ne&&Se&&(It=It<js?0:te),tt&&De&&(Ht=Ht<Ks?0:X),xs(null,!0,!0),$i=!1}It=-10,Ht=-10,xe.fill(null),xs(null,!0,!0),pe&&($i=pe)}function pu(v,M,R,L,z,j,oe){ye._lock||(zt(v),Qe(),Pl(),v!=null&&ca(Bd,n,It,Ht,te,X,null))}function mu(){y.forEach(xb),ve(n.width,n.height,!0)}Os(Jo,Or,mu);const Qs={};Qs.mousedown=du,Qs.mousemove=ou,Qs.mouseup=fu,Qs.dblclick=pu,Qs.setSeries=(v,M,R,L)=>{let z=Kt.match[2];R=z(n,M,R),R!=-1&&pi(R,L,!0,!1)},he&&(D(Nd,g,du),D(hc,g,ou),D(Fd,g,v=>{zt(v),la(!1)}),D(Od,g,Sm),D(Bd,g,pu),uh.add(n),n.syncRect=la);const $a=n.hooks=i.hooks||{};function hn(v,M,R){bl?ra.push([v,M,R]):v in $a&&$a[v].forEach(L=>{L.call(null,n,M,R)})}(i.plugins||[]).forEach(v=>{for(let M in v.hooks)$a[M]=($a[M]||[]).concat(v.hooks[M])});const gu=(v,M,R)=>R,Kt=Jt({key:null,setSeries:!1,filters:{pub:jd,sub:jd},scales:[A,S[1]?S[1].scale:null],match:[Kd,Kd,gu],values:[null,null]},ye.sync);Kt.match.length==2&&Kt.match.push(gu),ye.sync=Kt;const _u=Kt.key,Ll=Hp(_u);function ca(v,M,R,L,z,j,oe){Kt.filters.pub(v,M,R,L,z,j,oe)&&Ll.pub(v,M,R,L,z,j,oe)}Ll.sub(n);function bm(v,M,R,L,z,j,oe){Kt.filters.sub(v,M,R,L,z,j,oe)&&Qs[v](null,M,R,L,z,j,oe)}n.pub=bm;function Em(){Ll.unsub(n),uh.delete(n),Xe.clear(),ah(Jo,Or,mu),c.remove(),fe==null||fe.remove(),hn("destroy")}n.destroy=Em;function Dl(){hn("init",i,e),Je(e||i.data,!1),q[A]?El(A,q[A]):Qe(),se=Ut.show&&(Ut.width>0||Ut.height>0),ae=re=!0,ve(i.width,i.height)}return S.forEach(ia),y.forEach(yl),t?t instanceof HTMLElement?(t.appendChild(c),Dl()):t(n,Dl):Dl(),n}fn.assign=Jt;fn.fmtNum=zh;fn.rangeNum=Qo;fn.rangeLog=hl;fn.rangeAsinh=Oh;fn.orient=Gs;fn.pxRatio=Mt;fn.join=hS;fn.fmtDate=Hh,fn.tzDate=MS;fn.sync=Hp;{fn.addGap=ib,fn.clipGaps=fl;let i=fn.paths={points:$p};i.linear=jp,i.stepped=ab,i.bars=ob,i.spline=cb}function gc(i){return Math.max(120,i.clientHeight-30)}class yb{constructor(){U(this,"name","Plotter");U(this,"container",null);U(this,"tabsContainer",null);U(this,"contentContainer",null);U(this,"tooltip",null);U(this,"paretoPlot",null);U(this,"ablationPlot",null);U(this,"variabilityPlot",null);U(this,"currentTab","pareto");U(this,"records",[]);U(this,"ablationGroups",[]);U(this,"paretoFlags",[]);U(this,"chance",.1);U(this,"paretoRecordIndices",[]);U(this,"paretoXData",[]);U(this,"paretoYData",[]);U(this,"categoryLabels",[]);U(this,"ablationFixedAxes","");U(this,"onCampaignMetrics",e=>{const{data:t}=e;t!=null&&t.records&&qn.observe(e==null?void 0:e.campaign_id,t)});U(this,"onRunChanged",(e,t)=>{t&&(this.records=t.records??[],this.paretoFlags=t.pareto??[],this.ablationGroups=t.ablation_groups??[],typeof t.chance=="number"&&(this.chance=t.chance),this.updatePlots(),this.updateStatus())});Yt.register("campaign_metrics",this.onCampaignMetrics),qn.onChange(this.onRunChanged)}async init(){this.createUI(),console.log("[Plotter] Initialized")}async destroy(){var e,t,n,s;Yt.unregister("campaign_metrics",this.onCampaignMetrics),(e=this.paretoPlot)==null||e.destroy(),(t=this.ablationPlot)==null||t.destroy(),(n=this.variabilityPlot)==null||n.destroy(),(s=this.container)==null||s.remove()}createUI(){const e=document.getElementById("ui-overlay");e&&(this.container=document.createElement("div"),this.container.id="plotter",this.container.style.cssText=`
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
    `,this.container.appendChild(this.tooltip),this.tabsContainer.querySelectorAll(".plotter-tab").forEach(t=>{t.addEventListener("click",()=>this.switchTab(t.getAttribute("data-tab")))}),this.container.querySelector("#plotter-download").addEventListener("click",()=>this.downloadCurrent()),this.switchTab(this.currentTab))}showTab(e){e!==this.currentTab&&this.switchTab(e)}switchTab(e){this.currentTab=e,this.tabsContainer.querySelectorAll(".plotter-tab").forEach(n=>{n.classList.toggle("active",n.getAttribute("data-tab")===e)}),Object.entries({pareto:"plotter-pareto",ablation:"plotter-ablation",variability:"plotter-variability"}).forEach(([n,s])=>{const r=document.getElementById(s);r&&(r.style.display=n===e?"block":"none")}),e==="pareto"&&!this.paretoPlot&&this.initParetoPlot(),e==="ablation"&&!this.ablationPlot&&this.initAblationPlot(),e==="variability"&&!this.variabilityPlot&&this.initVariabilityPlot(),this.updatePlots()}updateStatus(){var s;const e=(s=this.container)==null?void 0:s.querySelector("#plotter-status");if(!e)return;const t=`${this.records.length} records | ${this.paretoFlags.filter(r=>r).length} Pareto`,n=this.ablationFixedAxes?` | fixed: ${this.ablationFixedAxes}`:"";e.textContent=t+n,e.title=e.textContent}updatePlots(){this.currentTab==="pareto"&&this.paretoPlot&&this.updateParetoPlot(),this.currentTab==="ablation"&&this.ablationPlot&&this.updateAblationPlot(),this.currentTab==="variability"&&this.variabilityPlot&&this.updateVariabilityPlot()}initParetoPlot(){const e=document.getElementById("plotter-pareto");if(!e)return;const t={width:e.clientWidth,height:gc(e),title:"Pareto Frontier: validation accuracy vs speed",axes:[{label:"1 / walltime_s   (faster →)",grid:{stroke:V.border}},{label:"accuracy",grid:{stroke:V.border},side:1}],scales:{x:{time:!1},y:{time:!1}},series:[{},{label:"val_acc",stroke:V.gradient,width:0,points:{show:!0,size:8,stroke:"white",width:1,fill:(n,s)=>{var o;const r=this.paretoRecordIndices[s],a=r===void 0?void 0:this.records[r];return a&&jt[(o=a.coordinate)==null?void 0:o.credit]||V.gradient}}}],hooks:{draw:[n=>{const s=n.ctx;if(this.paretoFlags.some(a=>a)){const a=[];this.records.forEach((o,l)=>{this.paretoFlags[l]&&o.payload.walltime_s&&o.payload.val_acc&&a.push([1/o.payload.walltime_s,o.payload.val_acc])}),a.sort((o,l)=>o[0]-l[0]),a.length>1&&(s.beginPath(),s.strokeStyle=V.pareto,s.lineWidth=2,s.setLineDash([5,5]),a.forEach((o,l)=>{const c=n.valToPos(o[0],"x"),h=n.valToPos(o[1],"y");l===0?s.moveTo(c,h):s.lineTo(c,h)}),s.stroke(),s.setLineDash([])),a.forEach(o=>{const l=n.valToPos(o[0],"x"),c=n.valToPos(o[1],"y");s.beginPath(),s.arc(l,c,7,0,Math.PI*2),s.strokeStyle=V.pareto,s.lineWidth=1.5,s.stroke()})}const r=n.valToPos(this.chance,"y");s.strokeStyle=V.chance_line,s.lineWidth=1.5,s.setLineDash([4,4]),s.beginPath(),s.moveTo(n.bbox.left,r),s.lineTo(n.bbox.width,r),s.stroke(),s.setLineDash([])}],setCursor:[n=>{this.showScatterTooltip(n)}]},cursor:{show:!0,drag:{setScale:!0},focus:{prox:16}}};this.paretoPlot=new fn(t,[[],[]],e)}recordAt(e){const t=this.paretoRecordIndices[e];return t===void 0?void 0:this.records[t]}updateParetoPlot(){if(!this.paretoPlot||this.records.length===0)return;const e=[],t=[];this.paretoRecordIndices=[],this.records.forEach((r,a)=>{const o=r.payload.walltime_s,l=r.payload.val_acc;this.paretoRecordIndices.push(a),o&&l?(e.push(1/o),t.push(l)):(e.push(NaN),t.push(NaN))}),this.paretoPlot.setData([e,t]),this.paretoXData=e,this.paretoYData=t;const n=e.filter(Number.isFinite),s=t.filter(Number.isFinite);n.length>0&&this.fitScale(this.paretoPlot,"x",Math.min(...n),Math.max(...n)),s.length>0&&this.fitScale(this.paretoPlot,"y",Math.min(Math.min(...s),this.chance),Math.max(...s))}fitScale(e,t,n,s){if(!Number.isFinite(n)||!Number.isFinite(s))return;n===s&&(n-=.01,s+=.01);const r=(s-n)*.05;e.setScale(t,{min:n-r,max:s+r})}initAblationPlot(){const e=document.getElementById("plotter-ablation");if(!e)return;const t={width:e.clientWidth,height:gc(e),title:"Ablation: credit arm → validation accuracy",axes:[{label:"credit arm",splits:()=>this.categoryIndices(),values:(n,s)=>s.map(r=>this.categoryLabels[r]??String(r)),grid:{stroke:V.border}},{label:"accuracy",grid:{stroke:V.border},side:1}],scales:{x:{time:!1},y:{time:!1}},series:[{},{label:"val_acc",width:0,points:{show:!1}}],hooks:{draw:[n=>{if(!this.ablationGroups.length)return;const s=n.ctx,r=this.ablationGroups.find(h=>h.axis==="credit");if(!r)return;const a=r.metrics.find(h=>h.metric==="val_acc");if(!a)return;const o=a.arms,l=n.bbox.width/(o.length*1.5);n.bbox.left,o.forEach((h,u)=>{const d=n.valToPos(u,"x"),f=n.valToPos(0,"y"),g=n.valToPos(h.mean,"y"),_=f-g;if(s.fillStyle=jt[h.value]||V.gradient,s.fillRect(d-l/2,g,l,_),h.std>0){const m=n.valToPos(h.mean+h.std,"y");s.strokeStyle=V.text_muted,s.lineWidth=1,s.beginPath(),s.moveTo(d,m),s.lineTo(d,f),s.stroke(),s.moveTo(d-3,m),s.lineTo(d+3,m),s.stroke()}});const c=n.valToPos(this.chance,"y");s.strokeStyle=V.chance_line,s.lineWidth=2,s.setLineDash([5,5]),s.beginPath(),s.moveTo(n.bbox.left,c),s.lineTo(n.bbox.width,c),s.stroke(),s.setLineDash([])}],setCursor:[n=>{this.showCategoryTooltip(n,"ablation")}]},cursor:{show:!0,drag:{setScale:!0}}};this.ablationPlot=new fn(t,[[],[]],e)}updateAblationPlot(){if(!this.ablationPlot||!this.ablationGroups.length)return;const e=this.ablationGroups.find(o=>o.axis==="credit");if(!e)return;const t=e.metrics.find(o=>o.metric==="val_acc");if(!t)return;const n=t.arms.map((o,l)=>l),s=t.arms.map(o=>o.mean);this.categoryLabels=t.arms.map(o=>o.value),this.ablationFixedAxes=e.fixed_axes.split(",").map(o=>o.split("=").pop()??o).join(", "),this.ablationPlot.setData([n,s]),this.fitScale(this.ablationPlot,"x",-.5,Math.max(n.length-.5,.5));const r=t.arms.flatMap(o=>[o.mean-o.std,o.mean+o.std]);r.length>0&&this.fitScale(this.ablationPlot,"y",Math.min(Math.min(...r),this.chance),Math.max(...r));const a=this.ablationPlot.root.querySelector(".u-title");a&&(a.textContent=`Ablation: ${e.axis} vs val_acc`)}initVariabilityPlot(){const e=document.getElementById("plotter-variability");if(!e)return;const t={width:e.clientWidth,height:gc(e),title:"Seed variability: validation accuracy per arm",axes:[{label:"credit arm",splits:()=>this.categoryIndices(),values:(n,s)=>s.map(r=>this.categoryLabels[r]??String(r)),grid:{stroke:V.border}},{label:"accuracy",grid:{stroke:V.border},side:1}],scales:{x:{time:!1},y:{time:!1}},series:[{},{label:"val_acc",width:0,points:{show:!1}}],hooks:{draw:[n=>{if(!this.records.length)return;const s=n.ctx,r={};this.records.forEach(c=>{const h=c.coordinate.credit,u=c.payload.val_acc;u!==void 0&&(r[h]||(r[h]=[])).push(u)});const a=Object.keys(r).sort(),o=n.bbox.width/(a.length*2);a.forEach((c,h)=>{const u=r[c].sort((x,P)=>x-P),d=u.length;if(d===0)return;const f=u[Math.floor(d*.25)],g=u[Math.floor(d*.5)],_=u[Math.floor(d*.75)],m=_-f,p=Math.max(u[0],f-1.5*m),S=Math.min(u[d-1],_+1.5*m),y=n.valToPos(h,"x"),w=n.valToPos(p,"y"),O=n.valToPos(f,"y"),A=n.valToPos(g,"y"),C=n.valToPos(_,"y"),F=n.valToPos(S,"y"),b=jt[c]||V.gradient;s.strokeStyle=b,s.lineWidth=1.5,s.beginPath(),s.moveTo(y,w),s.lineTo(y,O),s.moveTo(y,C),s.lineTo(y,F),s.stroke(),s.fillStyle=b+"44",s.strokeStyle=b,s.lineWidth=1.5,s.fillRect(y-o/2,C,o,O-C),s.strokeRect(y-o/2,C,o,O-C),s.strokeStyle="white",s.lineWidth=2,s.beginPath(),s.moveTo(y-o/2,A),s.lineTo(y+o/2,A),s.stroke(),u.forEach(x=>{if(x<p||x>S){const P=n.valToPos(x,"y");s.fillStyle=b,s.beginPath(),s.arc(y,P,2,0,Math.PI*2),s.fill()}})});const l=n.valToPos(this.chance,"y");s.strokeStyle=V.chance_line,s.lineWidth=2,s.setLineDash([5,5]),s.beginPath(),s.moveTo(n.bbox.left,l),s.lineTo(n.bbox.width,l),s.stroke(),s.setLineDash([])}],setCursor:[n=>{this.showCategoryTooltip(n,"variability")}]},cursor:{show:!0,drag:{setScale:!0}}};this.variabilityPlot=new fn(t,[[],[]],e)}updateVariabilityPlot(){if(!this.variabilityPlot||!this.records.length)return;const e=Array.from(new Set(this.records.map(r=>r.coordinate.credit))).sort(),t=e.map((r,a)=>a),n=e.map(()=>0);this.categoryLabels=e,this.variabilityPlot.setData([t,n]),this.fitScale(this.variabilityPlot,"x",-.5,Math.max(e.length-.5,.5));const s=this.records.map(r=>r.payload.val_acc).filter(r=>typeof r=="number");s.length>0&&this.fitScale(this.variabilityPlot,"y",Math.min(Math.min(...s),this.chance),Math.max(...s))}categoryIndices(){return this.categoryLabels.map((e,t)=>t)}showTooltip(e,t){if(!this.tooltip||!this.container)return;const n=e.cursor;if(!n||n.left==null||n.top==null){this.hideTooltip();return}const s=e.ctx.canvas.getBoundingClientRect(),r=this.container.getBoundingClientRect();this.tooltip.innerHTML=t,this.tooltip.style.display="block",this.tooltip.style.left=`${s.left-r.left+e.bbox.left+n.left+14}px`,this.tooltip.style.top=`${s.top-r.top+e.bbox.top+n.top+14}px`}hideTooltip(){this.tooltip&&(this.tooltip.style.display="none")}showScatterTooltip(e){var d,f;const t=e.cursor;if(!t||t.left==null||t.top==null){this.hideTooltip();return}let n=-1,s=1/0;if(this.paretoXData.forEach((g,_)=>{const m=this.paretoYData[_];if(!Number.isFinite(g)||!Number.isFinite(m))return;const p=e.valToPos(g,"x"),S=e.valToPos(m,"y");if(!Number.isFinite(p)||!Number.isFinite(S))return;const y=(p-t.left)**2+(S-t.top)**2;y<s&&(s=y,n=_)}),n<0||s>400){this.hideTooltip();return}const r=this.recordAt(n);if(!r){this.hideTooltip();return}const a=this.paretoRecordIndices[n],o=((d=r.coordinate)==null?void 0:d.credit)??"?",l=r.payload.val_acc??0,c=r.payload.walltime_s??0,h=((f=r.schedule)==null?void 0:f.seed)??"?",u=this.paretoFlags[a]?" · PARETO":"";this.showTooltip(e,`${o} · val_acc ${l.toFixed(3)} · ${c.toFixed(1)}s · seed ${h}${u}`)}showCategoryTooltip(e,t){const n=e.cursor;if(!n||n.left==null||n.top==null){this.hideTooltip();return}const s=Math.round(e.posToVal(n.left,"x"));if(s<0||s>=this.categoryLabels.length){this.hideTooltip();return}const r=this.categoryLabels[s];if(t==="ablation"){const h=this.ablationGroups.find(f=>f.axis==="credit"),u=h==null?void 0:h.metrics.find(f=>f.metric==="val_acc"),d=u==null?void 0:u.arms[s];if(!d){this.hideTooltip();return}this.showTooltip(e,`${r} · ${d.mean.toFixed(3)} ± ${d.std.toFixed(3)} (n=${d.count})${d.at_chance?" · at chance":""}`);return}const a=this.records.filter(h=>h.coordinate.credit===r).map(h=>h.payload.val_acc).filter(h=>typeof h=="number").sort((h,u)=>h-u);if(a.length===0){this.hideTooltip();return}const o=a[Math.floor(a.length*.5)],l=a[Math.floor(a.length*.25)],c=a[Math.floor(a.length*.75)];this.showTooltip(e,`${r} · median ${o.toFixed(3)} · IQR ${(c-l).toFixed(3)} · n=${a.length}`)}downloadCurrent(){const t={pareto:this.paretoPlot,ablation:this.ablationPlot,variability:this.variabilityPlot}[this.currentTab];if(!t)return;const n=document.createElement("a");n.download=`computronium-${this.currentTab}-${Date.now()}.png`,n.href=this.exportImage(t),n.click()}exportImage(e){const t=Array.from(e.root.querySelectorAll("canvas")),n=e.root.getBoundingClientRect(),s=Math.max(...t.map(l=>l.width),1),r=Math.max(...t.map(l=>l.height),1),a=document.createElement("canvas");a.width=s,a.height=r;const o=a.getContext("2d");return o?(o.fillStyle=V.bg,o.fillRect(0,0,s,r),t.forEach(l=>{const c=l.getBoundingClientRect();if(c.width===0||c.height===0)return;const h=l.width/c.width;o.drawImage(l,(c.left-n.left)*h,(c.top-n.top)*h,l.width,l.height)}),a.toDataURL("image/png")):e.ctx.canvas.toDataURL("image/png")}}const Yh=new yb;Xi.register(Yh);class Mb{constructor(){U(this,"name","LiveRail");U(this,"container",null);U(this,"logContainer",null);U(this,"events",[]);U(this,"maxEvents",50);U(this,"onPipelineEvent",e=>{this.events.unshift(e),this.events.length>this.maxEvents&&this.events.pop(),this.render()});U(this,"onStatusUpdate",e=>{var r,a,o;const t=((r=e==null?void 0:e.data)==null?void 0:r.running_campaigns)??0,n=((a=e==null?void 0:e.data)==null?void 0:a.queued_campaigns)??0,s=(o=this.container)==null?void 0:o.querySelector("#rail-queue");s&&(s.textContent=`${t} running · ${n} queued`)});Yt.register("pipeline_event",this.onPipelineEvent),Yt.register("status_update",this.onStatusUpdate)}async init(){this.createUI(),Gr.onStateChange(e=>this.setConnected(e==="connected")),console.log("[LiveRail] Initialized")}async destroy(){var e;Yt.unregister("pipeline_event",this.onPipelineEvent),Yt.unregister("status_update",this.onStatusUpdate),(e=this.container)==null||e.remove()}createUI(){const e=document.getElementById("ui-overlay");e&&(this.container=document.createElement("div"),this.container.id="live-rail",this.container.style.cssText=`
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
    `,e.appendChild(this.container),this.logContainer=this.container.querySelector("#rail-log"))}toggle(){this.container&&(this.container.style.display=this.container.style.display==="none"?"":"none")}setConnected(e){var a;const t=(a=this.container)==null?void 0:a.querySelector("#rail-connection");if(!t)return;const n=t.querySelector(".dot"),s=t.querySelector(".rail-label");if(!n||!s)return;const r=e?V.ok:V.error;n.style.background=r,t.style.background=r+"22",t.style.borderColor=r+"88",t.style.color=r,s.textContent=e?"Connected":"Disconnected"}render(){var t;if(!this.logContainer)return;this.logContainer.innerHTML=this.events.map(n=>{const s=new Date(n.timestamp).toLocaleTimeString(),a={ok:V.ok,warn:V.warn,error:V.error}[n.level]||V.text_secondary,o=n.level==="ok"?"✓":n.level==="warn"?"⚠":"✗";return`
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
        `}).join("");const e=(t=this.container)==null?void 0:t.querySelector("#rail-count");e&&(e.textContent=`${this.events.length} events`),this.logContainer.scrollLeft=0}}const jh=new Mb;Xi.register(jh);const Sb=4e3,bb={ok:V.text_primary,warn:V.warn,error:V.error};class Eb{constructor(){U(this,"name","Caption");U(this,"container",null);U(this,"headline",null);U(this,"context",null);U(this,"state",[]);U(this,"spoken",null);U(this,"last",null);U(this,"holdTimer",null);U(this,"onNarration",e=>{this.state=(e==null?void 0:e.state)??[],this.render()});U(this,"onEvent",e=>{e!=null&&e.sentence&&this.say(e.sentence,e.level??"ok")});Yt.register("narration",this.onNarration),Yt.register("pipeline_event",this.onEvent)}async init(){this.createUI(),this.render()}async destroy(){var e;Yt.unregister("narration",this.onNarration),Yt.unregister("pipeline_event",this.onEvent),this.holdTimer!==null&&window.clearTimeout(this.holdTimer),(e=this.container)==null||e.remove()}toggle(){this.container&&(this.container.style.display=this.container.style.display==="none"?"":"none")}say(e,t="ok"){e&&(this.spoken={text:e,level:t},this.last={text:e,level:t},this.render(),this.holdTimer!==null&&window.clearTimeout(this.holdTimer),this.holdTimer=window.setTimeout(()=>{this.spoken=null,this.holdTimer=null,this.render()},Sb))}createUI(){const e=document.getElementById("ui-overlay");e&&(this.container=document.createElement("div"),this.container.id="caption",this.container.style.cssText=`
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
    `,e.appendChild(this.container),this.headline=this.container.querySelector("#caption-headline"),this.context=this.container.querySelector("#caption-context"))}render(){if(!(!this.headline||!this.context)){if(this.spoken){this.headline.textContent=this.spoken.text,this.headline.style.color=this.colorOf(this.spoken.level),this.context.textContent=this.state.join(" ");return}if(this.state.length>0){this.headline.textContent=this.state[0],this.headline.style.color=V.text_primary,this.context.textContent=this.state.slice(1).join(" ");return}if(this.last){this.headline.textContent=this.last.text,this.headline.style.color=this.colorOf(this.last.level),this.context.textContent="";return}this.headline.textContent="The dashboard is starting.",this.headline.style.color=V.text_primary,this.context.textContent=""}}colorOf(e){return bb[e]??V.text_primary}}const Kh=new Eb;Xi.register(Kh);class wb{constructor(){U(this,"name","HUD");U(this,"panel",null);U(this,"modeChip",null);U(this,"connectionPill",null);U(this,"rows",new Map);U(this,"rowElements",new Map);U(this,"claimValue",null);U(this,"sourceValue",null);U(this,"statusData",{});U(this,"resources",{});U(this,"requiredSeeds",0);U(this,"measuredSeeds",0);U(this,"connected",!1);U(this,"animationTime",0);U(this,"onStatusUpdate",e=>{const t=(e==null?void 0:e.data)??e;t&&(this.statusData=t,this.updateQueueRows())});U(this,"onCampaignMetrics",e=>{const t=e==null?void 0:e.data;t&&qn.observe(e==null?void 0:e.campaign_id,t)});U(this,"onRunChanged",(e,t)=>{var n;t&&(this.resources=t.resources??{},typeof t.required_seeds=="number"&&(this.requiredSeeds=t.required_seeds),this.measuredSeeds=this.resources.seeds_per_arm??((n=t.records)==null?void 0:n.length)??0,this.updateModeChip(t.run),this.updateSource(t.store),this.updateResourceRows(),this.updateClaim())});Yt.register("status_update",this.onStatusUpdate),Yt.register("campaign_metrics",this.onCampaignMetrics),qn.onChange(this.onRunChanged)}async init(){this.createPanel(),this.createModeChip(),Gr.onStateChange(e=>{this.connected=e==="connected",this.updateConnection()}),console.log("[HUD] Initialized")}async destroy(){var e,t;Yt.unregister("status_update",this.onStatusUpdate),Yt.unregister("campaign_metrics",this.onCampaignMetrics),(e=this.panel)==null||e.remove(),(t=this.modeChip)==null||t.remove()}createPanel(){const e=document.getElementById("ui-overlay");if(!e)return;this.panel=document.createElement("div"),this.panel.id="hud",this.panel.style.cssText=`
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
        <span id="hud-source" style="font-weight: 600; color: ${V.text_secondary};">—</span>
      </div>
      <div style="margin-top: 12px; padding-top: 10px; border-top: 1px solid var(--border); display: flex; justify-content: space-between; align-items: baseline;">
        <span style="color: var(--text-secondary);">SEEDS TO CLAIM</span>
        <span id="hud-claim" style="font-weight: 700; color: ${V.insufficient};">—</span>
      </div>
    `,e.appendChild(this.panel);const t=this.panel.querySelector("#hud-meters");this.addMeter(t,"device","DEVICE",V.gradient),this.addMeter(t,"memory","MEMORY",V.memory),this.addMeter(t,"walltime","WALLTIME",V.cpu),this.addMeter(t,"gpu","GPU",V.gpu),this.addMeter(t,"cpu","CPU",V.cpu),this.addMeter(t,"records","RECORDS",V.promoted),this.claimValue=this.panel.querySelector("#hud-claim"),this.connectionPill=this.panel.querySelector("#hud-connection"),this.sourceValue=this.panel.querySelector("#hud-source")}addMeter(e,t,n,s){const r=document.createElement("div");r.style.cssText="display: flex; flex-direction: column; gap: 3px;",r.innerHTML=`
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
      background: ${V.text_muted}22;
      border: 1px solid ${V.text_muted}88;
      color: ${V.text_muted};
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
    `,e.appendChild(this.modeChip))}updateModeChip(e){if(!this.modeChip)return;const t=(e==null?void 0:e.mode)??"NO RUN",n=t==="PREREGISTERED"?V.passed:t==="EXPLORATORY"?V.insufficient:V.text_muted;this.modeChip.style.background=`${n}22`,this.modeChip.style.borderColor=`${n}88`,this.modeChip.style.color=n;const s=this.modeChip.querySelector(".mode-label");s&&(s.textContent=t);const r=this.modeChip.querySelector(".mode-detail");r&&(r.textContent=[e==null?void 0:e.profile,((e==null?void 0:e.tasks)??[]).join(", "),e==null?void 0:e.fidelity].filter(Boolean).join(" · ")),this.modeChip.title=e?`run ${e.run_id??"?"} · objectives: ${(e.objectives??[]).join(", ")||"none"}`:"No run has reported yet"}setMeter(e,t,n){const s=this.rows.get(e),r=this.rowElements.get(e);!s||!r||(s.value=t,s.fraction=Math.max(0,Math.min(1,n)),r.value.textContent=t,r.fill.style.width=`${(s.fraction*100).toFixed(1)}%`)}updateSource(e){if(!this.sourceValue)return;const t=e==null?void 0:e.source;if(!t){this.sourceValue.textContent="—",this.sourceValue.style.color=V.text_secondary;return}if(t==="snapshot"){const n=e!=null&&e.published_at?new Date(e.published_at).toLocaleTimeString():"";this.sourceValue.textContent=n?`snapshot ${n}`:"snapshot",this.sourceValue.style.color=V.insufficient,this.sourceValue.title="The writer published this copy; it is as fresh as its last publish.";return}this.sourceValue.textContent="live",this.sourceValue.style.color=V.passed,this.sourceValue.title="The store itself, read as it is written."}updateQueueRows(){const e=this.statusData;this.setMeter("gpu",e.max_gpus?`${e.used_gpus??0} / ${e.max_gpus}`:"—",e.max_gpus?(e.used_gpus??0)/e.max_gpus:0),this.setMeter("cpu",e.max_cpus?`${e.used_cpus??0} / ${e.max_cpus}`:"—",e.max_cpus?(e.used_cpus??0)/e.max_cpus:0)}updateResourceRows(){const e=this.resources;this.setMeter("device",e.device??"—",e.device?1:0),this.setMeter("memory",e.memory_mb!==void 0?`${e.memory_mb.toFixed(1)} MB`:"—",e.memory_mb!==void 0?Math.min(1,e.memory_mb/2048):0),this.setMeter("walltime",e.walltime_s!==void 0?`${e.walltime_s.toFixed(1)} s`:"—",e.walltime_s!==void 0?Math.min(1,e.walltime_s/120):0),this.setMeter("records",e.records!==void 0?`${e.records}`:"—",e.records!==void 0?Math.min(1,e.records/20):0)}updateClaim(){if(!this.claimValue)return;if(this.requiredSeeds<=0){this.claimValue.textContent="—";return}const e=Math.max(0,this.requiredSeeds-this.measuredSeeds);this.claimValue.textContent=`${e} more (${this.requiredSeeds} needed)`}updateConnection(){if(!this.connectionPill)return;const e=this.connectionPill.querySelector(".dot"),t=this.connectionPill.querySelector("span:last-child"),n=this.connected?V.ok:V.error;e.style.background=n,this.connectionPill.style.background=`${n}22`,this.connectionPill.style.borderColor=`${n}88`,this.connectionPill.style.color=n,t.textContent=this.connected?"live":"offline"}toggle(){this.panel&&(this.panel.style.display=this.panel.style.display==="none"?"":"none")}update(e){var n;this.animationTime+=e;const t=.5+.5*Math.sin(this.animationTime*2);(n=this.connectionPill)==null||n.style.setProperty("opacity",`${.75+.25*t}`)}}const _l=new wb;Xi.register(_l);const ko={hud:"h",rail:"r",caption:"c"},Qp={pareto:"p",ablation:"a",variability:"s"},em="v",xf=new Set([...Object.values(ko),...Object.values(Qp),em]);class Tb{constructor(e){U(this,"canvas");U(this,"context");U(this,"visible",!1);this.canvas=document.createElement("canvas"),this.canvas.id=e,this.canvas.style.cssText=`
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      z-index: 50;
      display: none;
      background: var(--bg);
      pointer-events: none;
    `,document.body.appendChild(this.canvas),this.context=this.canvas.getContext("2d"),this.resize(),window.addEventListener("resize",()=>{this.resize()})}show(){this.visible=!0,this.canvas.style.display="block",this.resize(),this.begin()}hide(){this.visible=!1,this.canvas.style.display="none"}resize(){const e=Math.min(window.devicePixelRatio||1,2);this.canvas.width=Math.floor(window.innerWidth*e),this.canvas.height=Math.floor(window.innerHeight*e),this.context.setTransform(e,0,0,e,0,0)}begin(){const e=this.context;return e.clearRect(0,0,window.innerWidth,window.innerHeight),e.fillStyle="#0a0e14",e.fillRect(0,0,window.innerWidth,window.innerHeight),e}area(){const e=document.getElementById("discovery-legend"),t=e?e.getBoundingClientRect().right:0,n=Math.max(40,t+24),s=Math.max(200,window.innerWidth*hp-n);return{x:n,y:70,width:s,height:Math.max(200,window.innerHeight*up-70)}}}const it=new Tb("stage-2d"),vn={top:64,right:36,bottom:62,left:78};function ta(i,e,t,n){i.fillStyle=V.text_primary,i.font="600 22px 'JetBrains Mono', monospace",i.textAlign="left",i.textBaseline="alphabetic",i.fillText(t,e.x,e.y+14),n&&(i.fillStyle=V.text_secondary,i.font="13px 'JetBrains Mono', monospace",i.fillText(n,e.x,e.y+40))}function tl(i,e,t=5){if(!Number.isFinite(i)||!Number.isFinite(e))return[i];if(i===e)return[i];const s=(e-i)/Math.max(1,t),r=10**Math.floor(Math.log10(s)),a=s/r,o=(a>=5?10:a>=2?5:a>=1?2:1)*r,l=Math.ceil(i/o)*o,c=[];for(let h=l;h<=e+o*1e-6;h+=o)c.push(Number(h.toFixed(10)));return c}function nl(i){const e=Math.abs(i);return e===0?"0":e>=1e3||e>=10?i.toFixed(0):e>=1?i.toFixed(1):e>=.01?i.toFixed(2):i.toExponential(1)}function il(i,e){const t=e.xMax-e.xMin;return t===0?e.rect.x:e.rect.x+(i-e.xMin)/t*e.rect.width}function Ca(i,e){const t=e.yMax-e.yMin;return t===0?e.rect.y+e.rect.height:e.rect.y+e.rect.height-(i-e.yMin)/t*e.rect.height}function Ab(i,e,t){const n={x:e.x+vn.left,y:e.y+vn.top,width:Math.max(40,e.width-vn.left-vn.right),height:Math.max(40,e.height-vn.top-vn.bottom)},s={rect:n,xMin:t.xMin,xMax:t.xMax,yMin:t.yMin,yMax:t.yMax};ta(i,e,t.title,t.subtitle);const r=tl(t.xMin,t.xMax,6),a=tl(t.yMin,t.yMax,5);return i.strokeStyle=V.border,i.lineWidth=1,i.beginPath(),i.rect(n.x,n.y,n.width,n.height),i.stroke(),i.font="12px 'JetBrains Mono', monospace",i.fillStyle=V.text_secondary,r.forEach(o=>{const l=il(o,s);l<n.x-1||l>n.x+n.width+1||(i.strokeStyle=V.border,i.beginPath(),i.moveTo(l,n.y),i.lineTo(l,n.y+n.height),i.stroke(),i.textAlign="center",i.fillText(nl(o),l,n.y+n.height+20))}),a.forEach(o=>{const l=Ca(o,s);l<n.y-1||l>n.y+n.height+1||(i.strokeStyle=V.border,i.beginPath(),i.moveTo(n.x,l),i.lineTo(n.x+n.width,l),i.stroke(),i.textAlign="right",i.fillText(nl(o),n.x-10,l+4))}),i.fillStyle=V.text_secondary,i.font="13px 'JetBrains Mono', monospace",i.textAlign="center",i.fillText(t.xLabel,n.x+n.width/2,n.y+n.height+46),i.save(),i.translate(n.x-56,n.y+n.height/2),i.rotate(-Math.PI/2),i.textAlign="center",i.fillText(t.yLabel,0,0),i.restore(),s}function fh(i,e,t){const n=e.split(/\s+/).filter(a=>a.length>0),s=[];let r="";return n.forEach(a=>{const o=r?`${r} ${a}`:a;if(r&&i.measureText(o).width>t){s.push(r),r=a;return}r=o}),r&&s.push(r),s}function bi(i,e,t){i.fillStyle=V.text_secondary,i.font="12px 'JetBrains Mono', monospace",i.textAlign="left",i.textBaseline="alphabetic",i.fillText(t,e.x,e.y+e.height+40)}function tm(i,e,t){const n={x:e.x+vn.left,y:e.y+vn.top,width:Math.max(40,e.width-vn.left-vn.right),height:Math.max(40,e.height-vn.top-vn.bottom)},s=n.width/Math.max(1,t.categories.length),r={rect:n,yMin:t.yMin,yMax:t.yMax,categories:t.categories,bandWidth:s,band:l=>n.x+s*(l+.5)},a={rect:n,yMin:t.yMin,yMax:t.yMax};return ta(i,e,t.title,t.subtitle),i.strokeStyle=V.border,i.lineWidth=1,i.strokeRect(n.x+.5,n.y+.5,n.width-1,n.height-1),i.font="12px 'JetBrains Mono', monospace",i.fillStyle=V.text_secondary,(t.yTicks??tl(t.yMin,t.yMax,5)).forEach(l=>{const c=Ca(l,a);c<n.y-1||c>n.y+n.height+1||(i.strokeStyle=V.border,i.beginPath(),i.moveTo(n.x,c),i.lineTo(n.x+n.width,c),i.stroke(),i.textAlign="right",i.fillText(nl(l),n.x-10,c+4))}),i.textAlign="center",i.textBaseline="top",t.categories.forEach((l,c)=>{Zo(l,14).forEach((h,u)=>{i.fillText(h,r.band(c),n.y+n.height+12+u*16)})}),i.fillStyle=V.text_secondary,i.font="13px 'JetBrains Mono', monospace",i.save(),i.translate(n.x-56,n.y+n.height/2),i.rotate(-Math.PI/2),i.textAlign="center",i.textBaseline="alphabetic",i.fillText(t.yLabel,0,0),i.restore(),r}function vl(i,e,t){i.font="12px 'JetBrains Mono', monospace";const n=t.rows.reduce((h,u)=>Math.max(h,i.measureText(u).width),0),s=Math.min(e.width*.45,Math.max(vn.left,n+24)),r={x:e.x+s,y:e.y+vn.top,width:Math.max(40,e.width-s-vn.right),height:Math.max(40,e.height-vn.top-vn.bottom)},a=r.height/Math.max(1,t.rows.length),o={rect:r,xMin:t.xMin,xMax:t.xMax,rows:t.rows,rowHeight:a,rowY:h=>r.y+a*(h+.5)},l={rect:r,xMin:t.xMin,xMax:t.xMax};return ta(i,e,t.title,t.subtitle),i.strokeStyle=V.border,i.lineWidth=1,i.strokeRect(r.x+.5,r.y+.5,r.width-1,r.height-1),i.font="12px 'JetBrains Mono', monospace",i.fillStyle=V.text_secondary,(t.xTicks??tl(t.xMin,t.xMax,6)).forEach(h=>{const u=il(h,l);u<r.x-1||u>r.x+r.width+1||(i.strokeStyle=V.border,i.beginPath(),i.moveTo(u,r.y),i.lineTo(u,r.y+r.height),i.stroke(),i.textAlign="center",i.textBaseline="alphabetic",i.fillText(nl(h),u,r.y+r.height+20))}),i.textAlign="right",i.textBaseline="middle",t.rows.forEach((h,u)=>{i.fillText(h,r.x-12,o.rowY(u))}),i.fillStyle=V.text_secondary,i.font="13px 'JetBrains Mono', monospace",i.textAlign="center",i.textBaseline="alphabetic",i.fillText(t.xLabel,r.x+r.width/2,r.y+r.height+46),o}class Rb{constructor(){U(this,"id","cost");U(this,"name","The claim's cost");U(this,"caption","The seeds each cell measured, against the seeds a claim is measured against.");U(this,"visible",!1);U(this,"drawn",!1)}enter(){this.visible=!0,it.show(),this.draw()}exit(){this.visible=!1,it.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}costs(){const e=Le.axes,t=Le.requiredSeeds,n=Ih(Le.aggregates,e),s=ll(n,e);return n.map(r=>({cell:r,label:Ia(r,e,s),color:jt[r.coordinate.credit]??V.gradient,measured:r.seeds,required:t})).sort((r,a)=>a.required-a.measured-(r.required-r.measured))}draw(){const e=this.costs();if(e.length===0){this.drawn=!1;return}const t=it.begin(),n=it.area(),s=Math.max(Le.requiredSeeds,...e.map(c=>c.measured)),r=vl(t,n,{xMin:0,xMax:s,rows:e.map(c=>c.label),title:"The claim's cost",subtitle:"the seeds measured, and the seeds a claim still needs",xLabel:"seeds"}),a=c=>r.rect.x+c/(r.xMax||1)*r.rect.width;e.forEach((c,h)=>{const u=r.rowY(h),d=Math.min(26,r.rowHeight*.5);t.fillStyle=V.bg_tertiary,t.fillRect(r.rect.x,u-d/2,a(c.required)-r.rect.x,d);const f=a(c.measured)-r.rect.x;t.fillStyle=c.color,t.fillRect(r.rect.x,u-d/2,f,d);const g=Math.max(0,c.required-c.measured);g>0&&(t.strokeStyle=V.warn,t.lineWidth=2,t.setLineDash([5,4]),t.beginPath(),t.moveTo(a(c.measured)+4,u),t.lineTo(a(c.required)-4,u),t.stroke(),t.setLineDash([])),t.strokeStyle=V.border,t.lineWidth=1,t.strokeRect(r.rect.x+.5,u-d/2,a(c.required)-r.rect.x-1,d-1),t.font="12px 'JetBrains Mono', monospace",t.textAlign="left",t.textBaseline="middle",t.fillStyle=V.text_secondary,t.fillText(`${c.measured} of ${c.required}`,r.rect.x+r.rect.width+12,u-8),g>0&&(t.fillStyle=V.warn,t.fillText(`${g} short`,r.rect.x+r.rect.width+12,u+9))});const o=a(Le.requiredSeeds);o>r.rect.x&&o<r.rect.x+r.rect.width&&(t.strokeStyle=V.text_secondary,t.lineWidth=1,t.setLineDash([3,4]),t.beginPath(),t.moveTo(o,r.rect.y),t.lineTo(o,r.rect.y+r.rect.height),t.stroke(),t.setLineDash([]));const l=e.reduce((c,h)=>c+Math.max(0,h.required-h.measured),0);bi(t,n,`the claim is ${l} seeds short over ${e.length} cells`),this.drawn=!0}}class Cb{constructor(){U(this,"id","contrast");U(this,"name","The contrast");U(this,"caption","The run's arms against one another, and whether the test could be run.");U(this,"key","d");U(this,"visible",!1);U(this,"drawn",!1)}enter(){this.visible=!0,it.show(),this.draw()}exit(){this.visible=!1,it.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}draw(){var h,u,d;const e=(h=Le.account)==null?void 0:h.contrast;if(!e||e.pairs.length===0){this.drawn=!1;return}const t=new Map,n=new Map;e.arms.forEach(f=>{t.set(f.value,f.mean),n.set(f.value,f.sd)});const s=Math.max(...e.arms.map(f=>f.mean),.001),r=it.begin(),a=it.area(),o=vl(r,a,{xMin:0,xMax:s*1.15,rows:e.pairs.map(f=>`${f.a} vs ${f.b}`),title:"The contrast",subtitle:`the ${e.axis} arms on ${e.metric}, and what separates them`,xLabel:e.metric}),l=f=>o.rect.x+f/(o.xMax||1)*o.rect.width;e.pairs.forEach((f,g)=>{const _=o.rowY(g),m=l(t.get(f.a)??0),p=l(t.get(f.b)??0);r.fillStyle=`${V.gradient}33`,r.fillRect(Math.min(m,p),_-11,Math.abs(p-m),22),r.strokeStyle=V.border_bright,r.lineWidth=2,r.beginPath(),r.moveTo(m,_),r.lineTo(p,_),r.stroke(),[f.a,f.b].forEach(y=>{const w=l(t.get(y)??0);n.get(y),r.strokeStyle=jt[y]??V.gradient,r.lineWidth=1,r.beginPath(),r.moveTo(w,_-16),r.lineTo(w,_+16),r.stroke(),r.fillStyle=jt[y]??V.gradient,r.beginPath(),r.arc(w,_,6,0,Math.PI*2),r.fill(),r.font="11px 'JetBrains Mono', monospace",r.textAlign="center",r.textBaseline="bottom",r.fillStyle=jt[y]??V.gradient,r.fillText(y,w,_-18)}),r.font="12px 'JetBrains Mono', monospace",r.textAlign="left",r.textBaseline="middle",r.fillStyle=V.text_primary;const S=f.difference??0;r.fillText(`${S>=0?"+":"−"}${Math.abs(S).toFixed(3)}`,o.rect.x+o.rect.width+12,_-9),r.fillStyle=V.text_secondary,r.fillText(`${f.shared_cells} shared cell${f.shared_cells===1?"":"s"}`,o.rect.x+o.rect.width+12,_+9)});const c=e.test;bi(r,a,c.tested?`the test ran: p=${(u=c.p_value)==null?void 0:u.toFixed(4)} (alpha=${c.alpha}) · dz=${(d=c.cohens_dz)==null?void 0:d.toFixed(2)} · ${c.shared_cells} shared cells`:`no test ran: ${c.shared_cells} shared cell${c.shared_cells===1?"":"s"}, ${c.required_cells} required`),this.drawn=!0}}class Pb{constructor(){U(this,"id","convergence");U(this,"name","Convergence");U(this,"caption","Accuracy against epoch, one curve per arm, with the chance level under them.");U(this,"visible",!1);U(this,"drawn",!1)}enter(){this.visible=!0,it.show(),this.draw()}exit(){this.visible=!1,it.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}curves(){var n;const e=((n=Le.metrics)==null?void 0:n.records)??[],t=new Map;return e.forEach(s=>{var l,c;const r=(l=s==null?void 0:s.payload)==null?void 0:l.convergence_curve;if(!Array.isArray(r)||r.length===0)return;const a=((c=s==null?void 0:s.coordinate)==null?void 0:c.credit)??"",o=t.get(a)??new Map;r.forEach(h=>{if(typeof(h==null?void 0:h.epoch)!="number"||typeof(h==null?void 0:h.val_acc)!="number")return;const u=o.get(h.epoch)??[];u.push(h.val_acc),o.set(h.epoch,u)}),t.set(a,o)}),Array.from(t.entries()).map(([s,r])=>({arm:s,points:Array.from(r.entries()).sort((a,o)=>a[0]-o[0]).map(([a,o])=>({epoch:a,val_acc:o.reduce((l,c)=>l+c,0)/o.length}))}))}draw(){const e=this.curves();if(e.length===0){this.drawn=!1;return}const t=it.begin(),n=it.area(),s=Le.chance,r=Math.max(...e.flatMap(h=>h.points.map(u=>u.epoch))),a=Math.max(s,...e.flatMap(h=>h.points.map(u=>u.val_acc))),o=Ab(t,n,{xMin:0,xMax:r,yMin:0,yMax:a,xLabel:"epoch",yLabel:"accuracy",title:"Convergence",subtitle:"the mean accuracy of each arm, epoch by epoch"}),l=Ca(s,o);t.strokeStyle=V.chance_line,t.lineWidth=1.5,t.setLineDash([6,5]),t.beginPath(),t.moveTo(o.rect.x,l),t.lineTo(o.rect.x+o.rect.width,l),t.stroke(),t.setLineDash([]),e.forEach(h=>{const u=jt[h.arm]||V.gradient;t.strokeStyle=u,t.lineWidth=2.5,t.beginPath(),h.points.forEach((d,f)=>{const g=il(d.epoch,o),_=Ca(d.val_acc,o);f===0?t.moveTo(g,_):t.lineTo(g,_)}),t.stroke(),h.points.forEach(d=>{t.fillStyle=u,t.beginPath(),t.arc(il(d.epoch,o),Ca(d.val_acc,o),3,0,Math.PI*2),t.fill()})}),t.font="12px 'JetBrains Mono', monospace",t.textAlign="left",t.textBaseline="middle";let c=o.rect.y+10;e.forEach(h=>{const u=jt[h.arm]||V.gradient;t.fillStyle=u,t.fillRect(o.rect.x+o.rect.width+18,c-5,10,10),t.fillStyle=V.text_secondary,t.fillText(h.arm,o.rect.x+o.rect.width+34,c),c+=20}),bi(t,n,`${e.length} arms · the dashed line is the chance level (${s.toFixed(2)})`),this.drawn=!0}}class Lb{constructor(){U(this,"id","effect");U(this,"name","The effect");U(this,"caption","Which axis moved the objective, and which the run held fixed: the run's attribution, and its limits.");U(this,"key","e");U(this,"visible",!1);U(this,"drawn",!1)}enter(){this.visible=!0,it.show(),this.draw()}exit(){this.visible=!1,it.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}draw(){const e=Le.attribution,t=(e==null?void 0:e.axes)??[];if(!e||t.length===0){this.drawn=!1;return}const n=it.begin(),s=it.area(),r=t.flatMap(c=>c.values.map(h=>h.mean)),a=Math.max(...r,.1),o=tm(n,s,{yMin:0,yMax:a*1.15,categories:t.map(c=>c.axis),title:"The effect",subtitle:e.summary,yLabel:e.metric||"the objective"}),l=c=>o.rect.y+o.rect.height-c/(o.yMax||1)*o.rect.height;t.forEach((c,h)=>{const u=o.band(h),d=Math.min(46,o.bandWidth*.4);if(c.varied&&c.values.length>1){const _=Math.min(...c.values.map(w=>w.mean)),m=Math.max(...c.values.map(w=>w.mean)),p=l(m),S=l(_);n.fillStyle=`${V.gradient}33`,n.fillRect(u-d/2,p,d,S-p),n.strokeStyle=V.gradient,n.lineWidth=1,n.strokeRect(u-d/2,p,d,S-p);const y=[];c.values.forEach(w=>{const O=l(w.mean),A=jt[w.value]??V.gradient;n.fillStyle=A,n.beginPath(),n.arc(u,O,5,0,Math.PI*2),n.fill();let C=O;for(;y.some(F=>Math.abs(F-C)<14);)C+=14;y.push(C),n.font="12px 'JetBrains Mono', monospace",n.textAlign="left",n.textBaseline="middle",n.fillStyle=A,n.fillText(w.value,u+d/2+10,C)});return}const f=c.values[0];if(!f)return;const g=l(f.mean);n.strokeStyle=V.text_muted,n.lineWidth=2,n.beginPath(),n.moveTo(u-7,g),n.lineTo(u+7,g),n.stroke(),n.font="12px 'JetBrains Mono', monospace",n.textAlign="center",n.textBaseline="top",n.fillStyle=V.text_muted,n.fillText(f.value,u,g+10)}),bi(n,s,e.reason),this.drawn=!0}}const Db=84,Ib=92;class Ub{constructor(){U(this,"id","flow");U(this,"name","The flow");U(this,"caption","The run's cells, stage by stage: what each one handled, and what the gate refused.");U(this,"key","f");U(this,"visible",!1);U(this,"drawn",!1)}enter(){this.visible=!0,it.show(),this.draw()}exit(){this.visible=!1,it.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}draw(){const e=Le.flow,t=(e==null?void 0:e.stages)??[];if(!e||t.length===0){this.drawn=!1;return}const n=it.begin(),s=it.area();ta(n,s,"The flow","the run's cells, from the space to the evidence");const r=s.y+s.height-Ib,a=Math.max(120,r-(s.y+Db)),o=Math.max(1,...t.map(c=>c.count+c.refused)),l=s.width/t.length;n.strokeStyle=V.border,n.lineWidth=1,n.beginPath(),n.moveTo(s.x,r+.5),n.lineTo(s.x+s.width,r+.5),n.stroke(),t.forEach((c,h)=>{const u=s.x+l*(h+.5),d=l*.56,f=m=>m/o*a,g=f(c.count),_=r-g;if(n.fillStyle=c.kind==="records"?V.measured:V.gradient,n.fillRect(u-d/2,_,d,Math.max(g,2)),c.refused>0){const m=f(c.refused);n.fillStyle=V.void,n.fillRect(u-d/2,_-m,d,m),n.font="12px 'JetBrains Mono', monospace",n.textAlign="center",n.textBaseline="bottom",n.fillStyle=V.void,n.fillText(`${c.refused} refused`,u,_-m-6)}c.count>0&&(n.font="600 15px 'JetBrains Mono', monospace",n.textAlign="center",n.textBaseline="bottom",n.fillStyle=V.text_primary,n.fillText(`${c.count}`,u,_-6)),n.font="12px 'JetBrains Mono', monospace",n.textAlign="center",n.textBaseline="top",n.fillStyle=c.count>0?V.text_secondary:V.text_muted,fh(n,c.action,l-8).slice(0,2).forEach((m,p)=>{n.fillText(m,u,r+10+p*16)})}),this.drawRefusals(n,s),bi(n,s,e.summary),this.drawn=!0}drawRefusals(e,t){const n=Le.space,s=(n==null?void 0:n.void_rules)??{},r=Object.keys(s),a=t.x;if(e.textAlign="left",e.textBaseline="alphabetic",e.font="600 13px 'JetBrains Mono', monospace",e.fillStyle=V.text_secondary,e.fillText("the rules that refuse",a,t.y+80),r.length===0){e.font="12px 'JetBrains Mono', monospace",e.fillStyle=V.text_muted,e.fillText("no cell of this slice is refused",a,t.y+102);return}e.font="12px 'JetBrains Mono', monospace",r.slice(0,6).forEach((o,l)=>{const c=t.y+102+l*18;e.fillStyle=V.void,e.fillText(o,a,c),e.fillStyle=V.text_secondary,e.textAlign="right",e.fillText(`${s[o]} cells`,a+280,c),e.textAlign="left"})}}function sl(i){i.traverse(e=>{var s;const t=e;(s=t.geometry)==null||s.dispose();const n=t.material;Array.isArray(n)?n.forEach(r=>r.dispose()):n==null||n.dispose()})}const Er=6.4,Ma=4,wr=5;class Nb{constructor(){U(this,"id","frontier");U(this,"name","Frontier");U(this,"caption","Every measured cell in accuracy, speed and parameters; the frontier is the line nothing beat.");U(this,"group",new os);U(this,"visible",!1);U(this,"drawn",!1);U(this,"framed",!1);U(this,"accuracy",{min:0,max:0,span:0})}enter(){this.visible=!0;const e=Wr();e&&e.scene.add(this.group),this.draw(!0)}exit(){var e;this.visible=!1,(e=this.group.parent)==null||e.remove(this.group),sl(this.group),this.group=new os,this.drawn=!1,this.framed=!1}refresh(){this.visible&&this.draw(!1)}ready(){return this.drawn}points(){var u,d;const e=((u=Le.metrics)==null?void 0:u.records)??[],t=((d=Le.metrics)==null?void 0:d.pareto)??[],n=Le.chance,s=[],r=[],a=[];e.forEach(f=>{const g=(f==null?void 0:f.payload)??{};typeof g.val_acc=="number"&&s.push(g.val_acc),typeof g.walltime_s=="number"&&g.walltime_s>0&&r.push(1/g.walltime_s),typeof g.param_count=="number"&&g.param_count>0&&a.push(Math.log10(g.param_count))});const o=_c([...s,n]);this.accuracy=o;const l=_c(r),c=_c(a),h=[];return e.forEach((f,g)=>{var S;const _=(f==null?void 0:f.payload)??{};if(typeof _.val_acc!="number")return;const m=typeof _.walltime_s=="number"&&_.walltime_s>0?1/_.walltime_s:null,p=typeof _.param_count=="number"&&_.param_count>0?Math.log10(_.param_count):null;h.push({x:m===null||l.span===0?0:((m-l.min)/l.span-.5)*Er,y:o.span===0?0:(_.val_acc-o.min)/o.span*Ma,z:p===null||c.span===0?0:((p-c.min)/c.span-.5)*wr,arm:((S=f==null?void 0:f.coordinate)==null?void 0:S.credit)??"",pareto:t[g]===!0})}),h}draw(e){const t=this.points();if(t.length===0){this.drawn=!1;return}this.clear(),this.addPoints(t),this.addFront(t),this.addChanceFloor(),this.addLabels(),this.drawn=!0,(e||!this.framed)&&(this.frame(),this.framed=!0)}clear(){[...this.group.children].forEach(e=>{this.group.remove(e),sl(e)})}addPoints(e){const t=[],n=[];e.forEach(o=>{t.push(o.x,o.y,o.z);const l=new nt(jt[o.arm]||V.gradient);n.push(l.r,l.g,l.b)});const s=new Xt;s.setAttribute("position",new qt(t,3)),s.setAttribute("color",new qt(n,3));const r=new Rh({size:.26,sizeAttenuation:!0,vertexColors:!0,map:yM(),alphaTest:.4,transparent:!0,opacity:.95});this.group.add(new op(s,r));const a=e.filter(o=>o.pareto);a.length!==0&&a.forEach(o=>{const l=MM(V.pareto,.26);l.position.set(o.x,o.y,o.z),this.group.add(l)})}addFront(e){const t=e.filter(a=>a.pareto).sort((a,o)=>a.y-o.y);if(t.length<2)return;const n=[];t.forEach(a=>n.push(a.x,a.y,a.z));const s=new Xt;s.setAttribute("position",new qt(n,3));const r=new Ko(s,new lp({color:V.pareto,dashSize:.22,gapSize:.16,transparent:!0,opacity:.85}));r.computeLineDistances(),this.group.add(r)}addChanceFloor(){const e=Le.chance,t=this.accuracy;if(t.span===0)return;const n=(e-t.min)/t.span*Ma,s=new za(Er*1.02,wr*1.02);s.rotateX(-Math.PI/2);const r=new _n(s,new Ur({color:V.chance_line,transparent:!0,opacity:.07,side:Yn,depthWrite:!1}));r.position.y=n,this.group.add(r);const a=Mi("chance",.24,new Hs({color:V.chance_line,sizeAttenuation:!0}));a.position.set(Er/2+.3,n,wr/2+.3),this.group.add(a)}addLabels(){const e=new Hs({color:13227232,sizeAttenuation:!0}),t=Mi("speed 1/s",.26,e);t.position.set(Er/2+.6,.1,0),this.group.add(t);const n=Mi("accuracy",.26,e);n.position.set(0,Ma+.4,0),this.group.add(n);const s=Mi("parameters",.26,e);s.position.set(0,.1,wr/2+.7),this.group.add(s)}frame(){const e=Wr();e&&Dh(e,new H(-Er/2-.6,-.2,-wr/2-.6),new H(Er/2+.6,Ma+.6,wr/2+.6),new H(0,Ma/2,0))}}function _c(i){const e=i.filter(s=>Number.isFinite(s));if(e.length===0)return{min:0,max:0,span:0};const t=Math.min(...e),n=Math.max(...e);return{min:t,max:n,span:n-t}}const yf={PASSED:V.passed,INSUFFICIENT:V.insufficient,REJECTED:V.rejected};class Fb{constructor(){U(this,"id","ledger");U(this,"name","The ledger");U(this,"caption","Every arm the run measured, its evidence, and the gate's standing on it.");U(this,"key","l");U(this,"visible",!1);U(this,"drawn",!1)}enter(){this.visible=!0,it.show(),this.draw()}exit(){this.visible=!1,it.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}chip(e,t,n,s){const r=yf[s]??V.text_secondary;e.font="11px 'JetBrains Mono', monospace";const a=e.measureText(s).width+18;e.fillStyle=`${r}22`,e.strokeStyle=`${r}88`,e.lineWidth=1,e.beginPath(),e.roundRect(t,n-9,a,18,9),e.fill(),e.stroke(),e.fillStyle=r,e.textAlign="center",e.textBaseline="middle",e.fillText(s,t+a/2,n)}standingBar(e,t,n,s,r,a){const o=Object.values(r).reduce((h,u)=>h+u,0);if(o===0)return;const l=18;let c=t;Object.entries(r).forEach(([h,u])=>{if(u<=0)return;const d=u/o*s;e.fillStyle=yf[h]??V.text_secondary,e.fillRect(c,n,Math.max(2,d-2),l),d>52&&(e.fillStyle=V.bg,e.font="11px 'JetBrains Mono', monospace",e.textAlign="center",e.textBaseline="middle",e.fillText(`${u}`,c+(d-2)/2,n+l/2)),c+=d}),e.font="12px 'JetBrains Mono', monospace",e.textAlign="left",e.textBaseline="alphabetic",e.fillStyle=V.text_secondary,e.fillText(`${a} arm${a===1?"":"s"}, and where each one stands`,t,n-10)}draw(){var r;const e=(r=Le.account)==null?void 0:r.ledger;if(!e||e.claims.length===0){this.drawn=!1;return}const t=it.begin(),n=it.area();ta(t,n,"The ledger","every arm the run measured, its evidence, and the gate's standing on it");let s=n.y+96;this.standingBar(t,n.x,s,Math.min(560,n.width*.55),e.standings,e.claims.length),s+=66,e.claims.forEach(a=>{const o=jt[a.value]??V.gradient;t.font="14px 'JetBrains Mono', monospace",t.textAlign="left",t.textBaseline="middle",t.fillStyle=o,t.fillText(`${a.axis} = ${a.value}`,n.x,s),t.font="13px 'JetBrains Mono', monospace",t.fillStyle=V.text_primary,t.fillText(`${a.mean.toFixed(3)} ± ${a.sd.toFixed(3)}`,n.x+300,s),t.font="12px 'JetBrains Mono', monospace",t.fillStyle=V.text_secondary,t.fillText(`${a.n} seeds · ${a.cells} cell${a.cells===1?"":"s"}`,n.x+460,s),this.chip(t,n.x+640,s,a.verdict),s+=42}),e.fixed.length>0&&(s+=22,t.font="600 14px 'JetBrains Mono', monospace",t.textAlign="left",t.textBaseline="alphabetic",t.fillStyle=V.text_primary,t.fillText("What was held fixed",n.x,s),s+=24,t.font="12px 'JetBrains Mono', monospace",e.fixed.forEach(a=>{t.textAlign="left",t.textBaseline="middle",t.fillStyle=V.text_secondary,t.fillText(`${a.axis} = ${a.value}`,n.x,s),t.fillText(`${a.mean.toFixed(3)}`,n.x+300,s),t.fillText(`${a.n} measurements · ${a.cells} cells`,n.x+460,s),s+=26})),s+=22,t.font="600 14px 'JetBrains Mono', monospace",t.textAlign="left",t.textBaseline="alphabetic",t.fillStyle=V.text_primary,t.fillText("What holds it back",n.x,s),s+=24,t.font="13px 'JetBrains Mono', monospace",e.limitations.forEach(a=>{fh(t,`· ${a.detail}`,n.width).forEach(o=>{t.fillStyle=V.text_secondary,t.fillText(o,n.x,s),s+=20})}),e.significance&&(s+=14,fh(t,`the report's test — ${e.significance}`,n.width).forEach(a=>{t.fillStyle=V.text_secondary,t.fillText(a,n.x,s),s+=20})),bi(t,n,`a claim needs ${e.min_seeds} seeds per cell`+(e.chance!==null?` · the chance level is ${e.chance.toFixed(3)}`:"")),this.drawn=!0}}function Zh(i){const e=i.replace("#","");return[parseInt(e.slice(0,2),16),parseInt(e.slice(2,4),16),parseInt(e.slice(4,6),16)]}function Mf(i){return`#${i.map(e=>Math.round(Math.max(0,Math.min(255,e))).toString(16).padStart(2,"0")).join("")}`}function Sf(i,e,t){return[i[0]+(e[0]-i[0])*t,i[1]+(e[1]-i[1])*t,i[2]+(e[2]-i[2])*t]}const Ob=Zh(V.ramp_low),bf=Zh(V.ramp_mid),Bb=Zh(V.ramp_high);function Lo(i){const e=Math.max(0,Math.min(1,i));return e<=.5?Mf(Sf(Ob,bf,e*2)):Mf(Sf(bf,Bb,(e-.5)*2))}class zb{constructor(){U(this,"id","matrix");U(this,"name","Evidence matrix");U(this,"caption","The space seen from above: one axis against another, every column a number, the refusals in the void colour.");U(this,"visible",!1);U(this,"drawn",!1)}enter(){this.visible=!0,it.show(),this.draw()}exit(){this.visible=!1,it.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}columns(){const e=Le.space;if(!e)return{columns:[],xValues:[],yValues:[]};const t=Le.axes,n=e.values[t.x]??[],s=e.values[t.y]??[],r=e.values[t.z]??[],a=[];return n.forEach(o=>{s.forEach(l=>{let c=0,h=0,u=-1/0,d="";r.forEach(g=>{const _=Xr(o,l,g),m=Le.spaceCells.get(_);if((m==null?void 0:m.status)==="void"){c+=1;return}h+=1;const p=Le.aggregates.get(_);if(!p||p.acc.length===0)return;const S=Fs(p.acc);S>u&&(u=S,d=p.coordinate.credit??"")});const f=c>0&&h===0?"void":u>-1/0?"measured":"gap";a.push({status:f,accuracy:u>-1/0?u:0,arm:d})})}),{columns:a,xValues:n,yValues:s}}draw(){const{columns:e,xValues:t,yValues:n}=this.columns();if(e.length===0){this.drawn=!1;return}const s=it.begin(),r=it.area(),a=Le.axes,o=t.length,l=n.length,c=150,u={x:r.x+c,y:r.y+70,width:Math.max(80,r.width-c-40),height:Math.max(80,r.height-70-96)},d=u.width/o,f=u.height/l,g=Math.max(...e.map(A=>A.accuracy),1e-4);s.fillStyle=V.text_primary,s.font="600 22px 'JetBrains Mono', monospace",s.textAlign="left",s.textBaseline="alphabetic",s.fillText("Evidence matrix",r.x,r.y+14),s.fillStyle=V.text_secondary,s.font="13px 'JetBrains Mono', monospace",s.fillText(`${a.x} against ${a.y} — the best cell of each column`,r.x,r.y+40);let _=0,m=0,p=0;e.forEach((A,C)=>{const F=Math.floor(C/l),b=C%l,x=u.x+F*d,P=u.y+b*f;A.status==="void"?(p+=1,s.fillStyle=`${V.void}22`,s.fillRect(x,P,d,f),this.drawCross(s,x,P,d,f)):A.status==="gap"?(m+=1,s.fillStyle=V.bg_tertiary,s.fillRect(x,P,d,f)):(_+=1,s.fillStyle=Lo(A.accuracy/g),s.fillRect(x,P,d,f),d>44&&f>26&&(s.fillStyle=kb(A.accuracy/g),s.font="600 15px 'JetBrains Mono', monospace",s.textAlign="center",s.textBaseline="middle",s.fillText(A.accuracy.toFixed(2),x+d/2,P+f/2))),s.strokeStyle=V.bg,s.lineWidth=1,s.strokeRect(x+.5,P+.5,d-1,f-1)}),s.fillStyle=V.text_secondary,s.font="12px 'JetBrains Mono', monospace",t.forEach((A,C)=>{const F=Zo(A,14);s.textAlign="center",s.textBaseline="top",F.forEach((b,x)=>{s.fillText(b,u.x+C*d+d/2,u.y+u.height+12+x*16)})}),n.forEach((A,C)=>{const F=Zo(A,16);s.textAlign="right",s.textBaseline="middle",F.forEach((b,x)=>{s.fillText(b,u.x-12,u.y+C*f+f/2-(F.length-1)*8+x*16)})});const S=180,y=u.x+u.width-S,w=r.y+16,O=s.createLinearGradient(y,0,y+S,0);O.addColorStop(0,Lo(0)),O.addColorStop(.5,Lo(.5)),O.addColorStop(1,Lo(1)),s.fillStyle=O,s.fillRect(y,w,S,12),s.strokeStyle=V.border,s.strokeRect(y+.5,w+.5,S-1,11),s.fillStyle=V.text_secondary,s.font="11px 'JetBrains Mono', monospace",s.textAlign="left",s.textBaseline="top",s.fillText("0",y,w+18),s.textAlign="right",s.fillText(g.toFixed(2),y+S,w+18),s.textAlign="left",s.fillText(`${_} measured · ${m} gaps · ${p} refused`,r.x,r.y+r.height+30),this.drawn=_>0}drawCross(e,t,n,s,r){const a=Math.min(s,r)*.28,o=t+s/2,l=n+r/2;e.strokeStyle=V.void,e.lineWidth=2,e.beginPath(),e.moveTo(o-a,l-a),e.lineTo(o+a,l+a),e.moveTo(o+a,l-a),e.lineTo(o-a,l+a),e.stroke()}}function kb(i){return i>.62?V.bg:V.text_primary}class Hb{constructor(){U(this,"id","multiples");U(this,"name","Small multiples");U(this,"caption","One panel per cell: every seed's own curve, on the same accuracy scale.");U(this,"visible",!1);U(this,"drawn",!1)}enter(){this.visible=!0,it.show(),this.draw()}exit(){this.visible=!1,it.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}panels(){const e=Le.axes,t=Ih(Le.aggregates,e),n=ll(t,e);return t.filter(s=>s.curves.length>0).map(s=>({cell:s,label:Ia(s,e,n),color:jt[s.coordinate.credit]??V.gradient,curves:s.curves}))}draw(){const e=this.panels();if(e.length===0){this.drawn=!1;return}const t=it.begin(),n=it.area(),s=Le.chance,r=e.flatMap(y=>y.curves.flatMap(w=>w.map(O=>O.val_acc))),a=e.flatMap(y=>y.curves.flatMap(w=>w.map(O=>O.epoch)));let o=Math.min(s,...r),l=Math.max(s,...r);l-o<1e-6&&(o-=.05,l+=.05);const c=(l-o)*.14;o-=c,l+=c;const h=Math.max(1,...a),u=Math.ceil(Math.sqrt(e.length)),d=Math.ceil(e.length/u),f=18,g=n.width-f*(u-1),_=n.height-64-44-f*(d-1),m=g/u,p=_/d;ta(t,n,"Small multiples","every seed of every cell, on one accuracy scale"),e.forEach((y,w)=>{const O=w%u,A=Math.floor(w/u),C=n.x+O*(m+f),F=n.y+64+A*(p+f);t.fillStyle=y.color,t.font="600 13px 'JetBrains Mono', monospace",t.textAlign="left",t.textBaseline="alphabetic",t.fillText(y.label,C,F+12);const b={x:C+(O===0?44:10),y:F+30,width:m-(O===0?54:20),height:p-56};t.strokeStyle=V.border,t.lineWidth=1,t.strokeRect(b.x+.5,b.y+.5,b.width-1,b.height-1);const x=b.y+b.height*(1-(s-o)/(l-o));t.strokeStyle=V.chance_line,t.lineWidth=1,t.setLineDash([4,4]),t.beginPath(),t.moveTo(b.x,x),t.lineTo(b.x+b.width,x),t.stroke(),t.setLineDash([]),y.curves.forEach(P=>{t.strokeStyle=y.color,t.lineWidth=1.8,t.beginPath(),P.forEach((K,k)=>{const Z=b.x+K.epoch/h*b.width,q=b.y+b.height*(1-(K.val_acc-o)/(l-o));k===0?t.moveTo(Z,q):t.lineTo(Z,q)}),t.stroke()}),t.fillStyle=V.text_muted,t.font="9px 'JetBrains Mono', monospace",O===0&&(t.textAlign="right",t.textBaseline="middle",[l,(l+o)/2,o].forEach(P=>{const K=b.y+b.height*(1-(P-o)/(l-o));t.fillText(P.toFixed(2),b.x-6,K)})),A===d-1&&(t.textAlign="left",t.textBaseline="top",t.fillText("epoch 0",b.x,b.y+b.height+6),t.textAlign="right",t.fillText(`epoch ${h}`,b.x+b.width,b.y+b.height+6))});const S=e.reduce((y,w)=>y+w.curves.length,0);bi(t,n,`${e.length} cells · ${S} seeds · the dashed line is the chance level (${s.toFixed(2)})`),this.drawn=!0}}function Vb(i,e,t){let n=0;return i.forEach(s=>{const r=(e-s)/t;n+=Math.exp(-.5*r*r)}),n/(i.length*t*Math.sqrt(2*Math.PI))}function Ef(i){if(i.length<2)return .02;const e=i.reduce((r,a)=>r+a,0)/i.length,t=i.reduce((r,a)=>r+(a-e)**2,0)/(i.length-1),s=1.06*Math.sqrt(t)*i.length**-.2;return Math.max(s,.01)}class Gb{constructor(){U(this,"id","spread");U(this,"name","The spread");U(this,"caption","One violin per arm, across its seeds: the width is the spread, not the mean.");U(this,"visible",!1);U(this,"drawn",!1)}enter(){this.visible=!0,it.show(),this.draw()}exit(){this.visible=!1,it.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}arms(){var n;const e=((n=Le.metrics)==null?void 0:n.records)??[],t=new Map;return e.forEach(s=>{var l,c;const r=(l=s==null?void 0:s.payload)==null?void 0:l.val_acc,a=(c=s==null?void 0:s.coordinate)==null?void 0:c.credit;if(typeof r!="number"||!a)return;const o=t.get(a)??[];o.push(r),t.set(a,o)}),Array.from(t.entries()).map(([s,r])=>({name:s,values:r.slice().sort((a,o)=>a-o),color:jt[s]??V.gradient})).sort((s,r)=>s.name.localeCompare(r.name))}draw(){const e=this.arms();if(e.length===0){this.drawn=!1;return}const t=it.begin(),n=it.area(),s=Le.chance,r=Le.requiredSeeds,a=e.map(h=>{const u=Ef(h.values);return{high:h.values[h.values.length-1]+1.5*u,low:h.values[0]-1.5*u}}),o=Math.max(s,...a.map(h=>h.high))*1.03,l=tm(t,n,{yMin:0,yMax:o,categories:e.map(h=>h.name),title:"The spread",subtitle:"every seed of every arm, as a distribution",yLabel:"accuracy"}),c=l.rect.y+l.rect.height*(1-s/l.yMax);t.strokeStyle=V.chance_line,t.lineWidth=1.5,t.setLineDash([6,5]),t.beginPath(),t.moveTo(l.rect.x,c),t.lineTo(l.rect.x+l.rect.width,c),t.stroke(),t.setLineDash([]),t.save(),t.beginPath(),t.rect(l.rect.x,l.rect.y,l.rect.width,l.rect.height),t.clip(),e.forEach((h,u)=>{const d=l.band(u),f=Math.min(l.bandWidth*.36,90),g=Ef(h.values),_=h.values[0]-1.5*g,m=h.values[h.values.length-1]+1.5*g,p=48,S=[];let y=0;for(let C=0;C<=p;C+=1){const F=_+(m-_)*C/p,b=Vb(h.values,F,g);S.push(b),y=Math.max(y,b)}const w=y>0?1/y:0,O=C=>l.rect.y+l.rect.height*(1-C/l.yMax);t.beginPath(),S.forEach((C,F)=>{const b=_+(m-_)*F/p,x=d+C*w*f,P=O(b);F===0?t.moveTo(x,P):t.lineTo(x,P)});for(let C=S.length-1;C>=0;C-=1){const F=_+(m-_)*C/p,b=d-S[C]*w*f;t.lineTo(b,O(F))}t.closePath(),t.fillStyle=`${h.color}33`,t.fill(),t.strokeStyle=h.color,t.lineWidth=1.5,t.stroke(),h.values.forEach((C,F)=>{const b=(F-(h.values.length-1)/2)*7;t.fillStyle=h.color,t.beginPath(),t.arc(d+b,O(C),3,0,Math.PI*2),t.fill()});const A=h.values.reduce((C,F)=>C+F,0)/h.values.length;t.strokeStyle=V.text_primary,t.lineWidth=1.5,t.beginPath(),t.moveTo(d-f,O(A)),t.lineTo(d+f,O(A)),t.stroke()}),t.restore(),e.forEach((h,u)=>{const d=Math.max(0,r-h.values.length);t.font="11px 'JetBrains Mono', monospace",t.textAlign="center",t.textBaseline="top",t.fillStyle=V.text_secondary,t.fillText(`${h.values.length} of ${r} seeds`,l.band(u),l.rect.y+l.rect.height+46),d>0&&(t.fillStyle=V.warn,t.fillText(`${d} short`,l.band(u),l.rect.y+l.rect.height+62))}),bi(t,n,`the white line is each arm's mean · a claim needs ${r} seeds per group`),this.drawn=!0}}const vc=3.4,Tr=1.15,Wb=new H(.34,.4,.85);class Xb{constructor(){U(this,"id","terrain");U(this,"name","Terrain");U(this,"caption","The space as a heightfield: accuracy is the height, the gaps are flat, the refusals are craters.");U(this,"group",new os);U(this,"visible",!1);U(this,"drawn",!1);U(this,"framed",!1)}enter(){this.visible=!0;const e=Wr();e&&e.scene.add(this.group),this.draw(!0)}exit(){var e;this.visible=!1,(e=this.group.parent)==null||e.remove(this.group),sl(this.group),this.group=new os,this.drawn=!1,this.framed=!1}refresh(){this.visible&&this.draw(!1)}ready(){return this.drawn}columns(){const e=Le.space;if(!e)return{columns:[],xValues:[],yValues:[]};const t=Le.axes,n=e.values[t.x]??[],s=e.values[t.y]??[],r=e.values[t.z]??[],a=[];return n.forEach((o,l)=>{s.forEach((c,h)=>{let u=0,d=0,f=-1/0,g="";r.forEach(m=>{const p=Xr(o,c,m),S=Le.spaceCells.get(p);if((S==null?void 0:S.status)==="void"){u+=1;return}d+=1;const y=Le.aggregates.get(p);if(!y||y.acc.length===0)return;const w=Fs(y.acc);w>f&&(f=w,g=y.coordinate.credit??"")});const _=u>0&&d===0?"void":f>-1/0?"measured":"gap";a.push({status:_,accuracy:f>-1/0?f:0,arm:g,x:(l-(n.length-1)/2)*Tr,y:(h-(s.length-1)/2)*Tr})})}),{columns:a,xValues:n,yValues:s}}draw(e){const{columns:t,xValues:n,yValues:s}=this.columns();if(t.length===0){this.drawn=!1;return}this.clear();const r=Math.max(...t.map(f=>f.accuracy),1e-4),a=[],o=[],l=[];t.forEach(f=>{const g=f.status==="measured"?f.accuracy/r*vc:f.status==="void"?-1.1:0;a.push(f.x,g,f.y);const _=new nt(f.status==="measured"?jt[f.arm]||V.gradient:f.status==="void"?V.void:V.border_bright);if(f.status==="measured"){const m=.6+.4*(f.accuracy/r);_.multiplyScalar(m)}else f.status==="void"&&_.multiplyScalar(.55);o.push(_.r,_.g,_.b)});const c=n.length,h=s.length;for(let f=0;f<c-1;f+=1)for(let g=0;g<h-1;g+=1){const _=f*h+g,m=(f+1)*h+g,p=(f+1)*h+g+1,S=f*h+g+1;l.push(_,S,m,m,S,p)}const u=new Xt;u.setAttribute("position",new qt(a,3)),u.setAttribute("color",new qt(o,3)),u.setIndex(l),u.computeVertexNormals();const d=new _n(u,new Bo({vertexColors:!0,roughness:.7,metalness:.1,side:Yn}));this.group.add(d),this.addVoidMarkers(t),this.addLabels(n,s),this.drawn=t.some(f=>f.status==="measured"),(e||!this.framed)&&(this.frame(t,n,s),this.framed=!0)}clear(){[...this.group.children].forEach(e=>{this.group.remove(e),sl(e)})}addVoidMarkers(e){const t=[];if(e.forEach(r=>{r.status==="void"&&t.push(r.x-.22,-1.1+.02,r.y-.22,r.x+.22,-1.1+.02,r.y+.22,r.x+.22,-1.1+.02,r.y-.22,r.x-.22,-1.1+.02,r.y+.22)}),t.length===0)return;const s=new Xt;s.setAttribute("position",new qt(t,3)),this.group.add(new Fr(s,new Hi({color:V.void,transparent:!0,opacity:.75})))}addLabels(e,t){const n=new Hs({color:13227232,sizeAttenuation:!0}),s=(e.length-1)*Tr/2,r=(t.length-1)*Tr/2,a=Mi(Le.axes.x,.22,n);a.position.set(s+1,-.2,r+.9),this.group.add(a);const o=Mi(Le.axes.y,.22,n);o.position.set(-s-1,.2,-r),this.group.add(o)}frame(e,t,n){const s=Wr();if(!s||e.length===0)return;const r=(t.length-1)*Tr/2,a=(n.length-1)*Tr/2;Dh(s,new H(-r-1.2,-1.1-.3,-a),new H(r+1.2,vc,a+1.4),new H(0,vc/3,0),Wb)}}class qb{constructor(){U(this,"id","timeline");U(this,"name","The timeline");U(this,"caption","The run's stages, in the order it reached them, and the time each held it.");U(this,"key","t");U(this,"visible",!1);U(this,"drawn",!1)}enter(){this.visible=!0,it.show(),this.draw()}exit(){this.visible=!1,it.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}draw(){const e=Le.timeline,t=(e==null?void 0:e.stages)??[];if(!e||t.length===0){this.drawn=!1;return}const n=it.begin(),s=it.area(),r=Math.max(e.seconds,.001),a=vl(n,s,{xMin:0,xMax:r,rows:t.map(d=>d.action),title:"The timeline",subtitle:"the run's stages, and the time each of them held it",xLabel:"seconds"}),o=d=>a.rect.x+d/r*a.rect.width,l=new Map;e.events.forEach(d=>{const f=l.get(d.stage)??[];f.push(d.at-e.start),l.set(d.stage,f)});const c=t.slice(0,-1).map((d,f)=>{const g=t[f+1],_=(l.get(d.stage)??[]).filter(p=>p<=g.offset),m=_.length>0?_[_.length-1]:d.offset;return{index:f,from:m,to:g.offset,seconds:g.offset-m}}),h=c.reduce((d,f)=>f.seconds>d.seconds?f:d,{index:-1,from:0,to:0,seconds:0}),u=h.seconds>.5?h:null;if(u){const d=o(u.from),f=o(u.to);n.fillStyle=`${V.warn}18`,n.fillRect(d,a.rect.y,Math.max(2,f-d),a.rect.height)}c.forEach(d=>{const f=d.index===h.index;n.strokeStyle=f?V.warn:V.border,n.lineWidth=f?2:1,n.beginPath(),n.moveTo(o(d.from),a.rowY(d.index)),n.lineTo(o(d.to),a.rowY(d.index+1)),n.stroke()}),t.forEach((d,f)=>{const g=a.rowY(f);n.fillStyle=V.gradient,(l.get(d.stage)??[]).forEach(_=>{const m=o(_);n.fillRect(m-1.5,g-9,3,18)}),n.font="12px 'JetBrains Mono', monospace",n.textAlign="left",n.textBaseline="middle",n.fillStyle=V.text_secondary,n.fillText(`${d.events}`,a.rect.x+a.rect.width+12,g)}),u&&(n.font="13px 'JetBrains Mono', monospace",n.textAlign="center",n.textBaseline="alphabetic",n.fillStyle=V.warn,n.fillText(`${u.seconds.toFixed(1)} s of silence`,(o(u.from)+o(u.to))/2,a.rect.y+22)),bi(n,s,`${t.length} stages · ${e.events.length} events · ${r.toFixed(1)} s from the first word to the last`),this.drawn=!0}}class $b{constructor(){U(this,"id","uncertainty");U(this,"name","The uncertainty");U(this,"caption","Each cell's mean and the margin the gate asks for, against the chance level.");U(this,"visible",!1);U(this,"drawn",!1)}enter(){this.visible=!0,it.show(),this.draw()}exit(){this.visible=!1,it.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}sigma(){const e=Le.gate;return e&&typeof e.superiority_margin_sigma=="number"?e.superiority_margin_sigma:2}intervals(){const e=Le.axes,t=Le.chance,n=this.sigma(),s=Ih(Le.aggregates,e),r=ll(s,e);return s.filter(a=>a.acc.length>0).map(a=>{const o=a.acc.length,l=a.acc.reduce((d,f)=>d+f,0)/o,c=a.acc.reduce((d,f)=>d+(f-l)**2,0)/Math.max(1,o-1),h=o>1?Math.sqrt(c/o):0,u=n*h;return{cell:a,label:Ia(a,e,r),color:jt[a.coordinate.credit]??V.gradient,mean:l,margin:u,lower:l-u,upper:l+u,threshold:t+u}}).sort((a,o)=>o.mean-a.mean)}draw(){const e=this.intervals();if(e.length===0){this.drawn=!1;return}const t=it.begin(),n=it.area(),s=Le.chance,r=this.sigma(),a=Math.max(s,...e.map(h=>Math.max(h.upper,h.threshold))),o=vl(t,n,{xMin:0,xMax:a*1.12,rows:e.map(h=>h.label),title:"The uncertainty",subtitle:"each cell's mean, and the margin the gate asks for",xLabel:"accuracy"}),l=h=>o.rect.x+h/(o.xMax||1)*o.rect.width,c=l(s);t.strokeStyle=V.chance_line,t.lineWidth=1.5,t.setLineDash([6,5]),t.beginPath(),t.moveTo(c,o.rect.y),t.lineTo(c,o.rect.y+o.rect.height),t.stroke(),t.setLineDash([]),t.font="11px 'JetBrains Mono', monospace",t.textAlign="left",t.textBaseline="alphabetic",t.fillStyle=V.chance_line,t.fillText("chance",c+6,o.rect.y+14),e.forEach((h,u)=>{const d=o.rowY(u),f=h.lower>s;t.strokeStyle=h.color,t.lineWidth=3,t.beginPath(),t.moveTo(l(h.lower),d),t.lineTo(l(h.upper),d),t.stroke(),t.strokeStyle=f?V.ok:V.warn,t.lineWidth=2,t.beginPath(),t.moveTo(l(h.threshold),d-11),t.lineTo(l(h.threshold),d+11),t.stroke(),t.fillStyle=h.color,t.beginPath(),t.arc(l(h.mean),d,5,0,Math.PI*2),t.fill(),t.textAlign="left",t.textBaseline="middle",t.font="12px 'JetBrains Mono', monospace",t.fillStyle=f?V.ok:V.warn,t.fillText(f?"clears chance":"not yet separable",o.rect.x+o.rect.width+12,d)}),bi(t,n,`the bar is ±${r}·SE · the tick is the threshold each cell has to clear · a claim needs ${Le.requiredSeeds} seeds per cell`),this.drawn=!0}}class Yb{constructor(){U(this,"id","space");U(this,"name","Space");U(this,"caption","The declared space: the gaps as cages, the measured cells as pillars, the refusals as crosses.")}enter(){Ns.show()}exit(){Ns.hide()}refresh(e){Ns.refreshView(e)}ready(){return Ns.hasMeasured()}}class jb{constructor(){U(this,"name","ViewSwitcher");U(this,"views",[]);U(this,"active",null);U(this,"selector",null);U(this,"captionElement",null);U(this,"section",null);U(this,"keys",new Map);U(this,"keyOf",new Map);U(this,"onKeyDown",e=>{if(e.metaKey||e.ctrlKey||e.altKey)return;const t=e.target;if(t&&["INPUT","SELECT","TEXTAREA"].includes(t.tagName))return;const n=e.key.toLowerCase();if(n===em){this.cycle();return}const s=this.keys.get(n);s&&this.show(s.id)});this.views=[new Yb,new Xb,new Nb,new zb,new Pb,new Hb,new Gb,new Rb,new $b,new qb,new Fb,new Cb,new Ub,new Lb]}async init(){window.addEventListener("keydown",this.onKeyDown),Le.onChange(e=>{var t;return(t=this.active)==null?void 0:t.refresh(e)}),this.buildKeys(),this.buildSection(),this.attachSection(),this.show(this.views[0].id),console.log("[ViewSwitcher] Initialized")}async destroy(){var e,t;window.removeEventListener("keydown",this.onKeyDown),(e=this.active)==null||e.exit(),this.active=null,(t=this.section)==null||t.remove(),this.section=null}get activeId(){var e;return((e=this.active)==null?void 0:e.id)??null}isReady(e){const t=this.views.find(n=>n.id===e);return t?t.ready():!1}show(e){var n;const t=this.views.find(s=>s.id===e);!t||t===this.active||((n=this.active)==null||n.exit(),this.active=t,t.enter(),this.updateSelector(),this.updateLegend())}cycle(){if(this.views.length===0)return;const e=this.views.findIndex(n=>n===this.active),t=this.views[(e+1)%this.views.length];this.show(t.id)}buildKeys(){this.keys.clear(),this.keyOf.clear(),this.views.forEach((e,t)=>{const n=t<9?String(t+1):"";n&&(this.keys.set(n,e),this.keyOf.set(e.id,n)),e.key&&!xf.has(e.key)&&(this.keys.set(e.key,e),this.keyOf.set(e.id,e.key))})}optionLabel(e){const t=this.keyOf.get(e.id);return t?`${t.toUpperCase()} · ${e.name}`:e.name}keyHint(){const e=[],t=[];this.views.forEach((s,r)=>{if(r<9){e.push(String(r+1));return}s.key&&!xf.has(s.key)&&t.push(s.key.toUpperCase())});const n=["V cycles"];return e.length>0&&n.push(`${e[0]}–${e[e.length-1]} pick`),t.length>0&&n.push(`${t.join(" ")} pick`),n.join(" · ")}buildSection(){const e=document.createElement("div");e.id="legend-view-section",e.style.cssText="margin-bottom: 12px;";const t=document.createElement("div");t.textContent="View",t.style.cssText="font-weight: 600; margin-bottom: 8px;",e.appendChild(t);const n=document.createElement("select");n.id="view-picker",n.style.cssText=`
      width: 100%;
      background: var(--bg-tertiary);
      color: var(--text-primary);
      border: 1px solid var(--border);
      border-radius: 4px;
      font-size: 11px;
      padding: 2px 4px;
    `,this.views.forEach(a=>{const o=document.createElement("option");o.value=a.id,o.textContent=this.optionLabel(a),n.appendChild(o)}),n.addEventListener("change",()=>this.show(n.value)),e.appendChild(n),this.selector=n;const s=document.createElement("div");s.id="view-caption",s.style.cssText="font-size: 11px; color: var(--text-secondary); margin-top: 8px;",e.appendChild(s),this.captionElement=s;const r=document.createElement("div");r.textContent=this.keyHint(),r.style.cssText="font-size: 10px; color: var(--text-muted); margin-top: 6px;",e.appendChild(r),this.section=e}attachSection(e=0){const t=document.getElementById("legend-view");if(!t){e<50&&window.setTimeout(()=>this.attachSection(e+1),100);return}this.section&&this.section.parentElement!==t&&t.appendChild(this.section),this.updateSelector(),this.updateLegend()}updateSelector(){!this.selector||!this.active||(this.selector.value=this.active.id)}updateLegend(){if(!this.active)return;const e=document.getElementById("legend-title");e&&(e.textContent=this.active.name);const t=document.getElementById("legend-marks");t&&(t.style.display=this.active.id==="space"?"":"none"),this.captionElement&&(this.captionElement.textContent=this.active.caption)}}const nm=new jb;Xi.register(nm);const Kb=/swiftshader|llvmpipe|software|basic render/i;function Zb(){const i=Jb();return{software:i,fps:i?12:60,shadows:!i,antialias:!i}}function Jb(){try{const i=document.createElement("canvas"),e=i.getContext("webgl2")??i.getContext("webgl");if(!e)return!0;const t=e.getExtension("WEBGL_debug_renderer_info"),n=String(t?e.getParameter(t.UNMASKED_RENDERER_WEBGL):e.getParameter(e.RENDERER));return Kb.test(n)}catch{return!0}}window.addEventListener("error",i=>{var e;console.error("[Global Error]",i.error),sm(((e=i.error)==null?void 0:e.message)||"Unknown error")});window.addEventListener("unhandledrejection",i=>{var e;console.error("[Unhandled Rejection]",i.reason),sm(((e=i.reason)==null?void 0:e.message)||"Unhandled promise rejection")});let Fi=null,is=null;function im(i="Initializing dashboard..."){const e=document.getElementById("ui-overlay");e&&(Fi=document.createElement("div"),Fi.id="global-loading",Fi.style.cssText=`
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
  `,Fi.innerHTML=`
    <div style="
      width: 48px;
      height: 48px;
      border: 3px solid var(--border);
      border-top-color: ${V.gradient};
      border-radius: 50%;
      animation: spin 1s linear infinite;
    "></div>
    <div style="font-size: 14px; color: var(--text-primary);">${i}</div>
    <style>
      @keyframes spin { to { transform: rotate(360deg); } }
    </style>
  `,e.appendChild(Fi))}function wf(){Fi==null||Fi.remove(),Fi=null}function sm(i){const e=document.getElementById("ui-overlay");e&&(is=document.createElement("div"),is.id="global-error",is.style.cssText=`
    position: fixed;
    top: 20px;
    right: 20px;
    background: ${V.error}22;
    border: 1px solid ${V.error}88;
    border-radius: 8px;
    padding: 16px 24px;
    color: ${V.error};
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    z-index: 1000;
    max-width: 400px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    display: flex;
    align-items: center;
    gap: 12px;
  `,is.innerHTML=`
    <span>✗</span>
    <span>${i}</span>
    <button onclick="this.parentElement.remove()" style="
      background: none;
      border: none;
      color: ${V.error};
      font-size: 18px;
      cursor: pointer;
      line-height: 1;
      padding: 0 4px;
    ">&times;</button>
  `,e.appendChild(is),setTimeout(()=>is==null?void 0:is.remove(),1e4))}Gr.connect();im("Connecting to dashboard...");Gr.waitForConnection(15e3).then(i=>{i?wf():(im("Connection timeout — retrying..."),Gr.onStateChange(e=>{e==="connected"&&wf()}))});const Qb=new Map(Object.entries(Qp).map(([i,e])=>[e,i]));window.addEventListener("keydown",i=>{if(i.metaKey||i.ctrlKey||i.altKey)return;const e=i.key.toLowerCase(),t=Qb.get(e);if(t){Yh.showTab(t);return}e===ko.hud&&_l.toggle(),e===ko.rail&&jh.toggle(),e===ko.caption&&Kh.toggle()});const eE=document.getElementById("dashboard-canvas"),na=Zb(),Zn=new sp({canvas:eE,antialias:na.antialias,alpha:!0,powerPreference:"high-performance"});Zn.setSize(window.innerWidth,window.innerHeight);Zn.setPixelRatio(na.software?1:Math.min(window.devicePixelRatio,2));Zn.shadowMap.enabled=na.shadows;Zn.shadowMap.type=Af;Zn.toneMapping=Cf;Zn.toneMappingExposure=1.2;const qi=new Ah;qi.background=new nt(658964);qi.fog=new Th(658964,.015);const fs=new bn(60,window.innerWidth/window.innerHeight,.1,200);fs.position.set(3.3,4.4,8.8);fs.lookAt(0,1,.1);const Ei=new oM(fs,Zn.domElement);Ei.target.set(0,1,.1);Ei.enableDamping=!0;Ei.dampingFactor=.05;Ei.enablePan=!0;Ei.minDistance=5;Ei.maxDistance=80;Ei.maxPolarAngle=Math.PI/2-.05;hM({scene:qi,camera:fs,renderer:Zn,controls:Ei});const tE=new Zy(4473958,.6);qi.add(tE);const ui=new Ky(16777215,1.2);ui.position.set(10,20,10);ui.castShadow=na.shadows;ui.shadow.mapSize.width=2048;ui.shadow.mapSize.height=2048;ui.shadow.camera.near=1;ui.shadow.camera.far=50;ui.shadow.camera.left=-20;ui.shadow.camera.right=20;ui.shadow.camera.top=20;ui.shadow.camera.bottom=-20;qi.add(ui);const nE=new $y(8956671,2236979,.5);qi.add(nE);const Jh=new Qy(8,8,2371648,1449256);Jh.position.y=-.01;const rm=Jh.material;rm.transparent=!0;rm.opacity=.35;qi.add(Jh);function iE(){fs.aspect=window.innerWidth/window.innerHeight,fs.updateProjectionMatrix(),Zn.setSize(window.innerWidth,window.innerHeight),Zn.setPixelRatio(na.software?1:Math.min(window.devicePixelRatio,2))}window.addEventListener("resize",iE);const sE=1e3/na.fps;let xc=0;function am(i){if(requestAnimationFrame(am),i-xc<sE)return;const e=(i-xc)/1e3;xc=i,Ei.update(),Ns.update(e),_l.update(e),Zn.render(qi,fs)}requestAnimationFrame(am);window.__DASHBOARD__={scene:qi,camera:fs,renderer:Zn,controls:Ei,discoveryMap:Ns,cellDrawer:dp,plotter:Yh,liveRail:jh,caption:Kh,hud:_l,viewSwitcher:nm,wsClient:Gr,router:Yt};console.log("🚀 Computronium Dashboard initialized");
//# sourceMappingURL=dashboard.js.map
