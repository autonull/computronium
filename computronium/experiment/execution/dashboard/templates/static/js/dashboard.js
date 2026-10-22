var Ym=Object.defineProperty;var jm=(s,e,t)=>e in s?Ym(s,e,{enumerable:!0,configurable:!0,writable:!0,value:t}):s[e]=t;var T=(s,e,t)=>jm(s,typeof e!="symbol"?e+"":e,t);/**
 * @license
 * Copyright 2010-2024 Three.js Authors
 * SPDX-License-Identifier: MIT
 */const Nh="168",mr={ROTATE:0,DOLLY:1,PAN:2},gr={ROTATE:0,PAN:1,DOLLY_PAN:2,DOLLY_ROTATE:3},Km=0,Od=1,Jm=2,qf=1,Xf=2,Yi=3,Es=0,zn=1,Nn=2,bs=0,Wr=1,kd=2,Bd=3,zd=4,Zm=5,qs=100,Qm=101,eg=102,tg=103,ng=104,ig=200,sg=201,rg=202,ag=203,zc=204,Hc=205,og=206,lg=207,cg=208,hg=209,dg=210,ug=211,fg=212,pg=213,mg=214,gg=0,xg=1,vg=2,rl=3,_g=4,yg=5,bg=6,Sg=7,Yf=0,Mg=1,wg=2,Ss=0,Eg=1,Tg=2,Ag=3,jf=4,Cg=5,Rg=6,Pg=7,Kf=300,Zr=301,Qr=302,Vc=303,Gc=304,vl=306,Wc=1e3,js=1001,$c=1002,si=1003,Lg=1004,mo=1005,mi=1006,Jl=1007,Ks=1008,ss=1009,Jf=1010,Zf=1011,ja=1012,Fh=1013,Qs=1014,Ki=1015,eo=1016,Oh=1017,kh=1018,ea=1020,Qf=35902,ep=1021,tp=1022,vi=1023,np=1024,ip=1025,$r=1026,ta=1027,sp=1028,Bh=1029,rp=1030,zh=1031,Hh=1033,Zo=33776,Qo=33777,el=33778,tl=33779,qc=35840,Xc=35841,Yc=35842,jc=35843,Kc=36196,Jc=37492,Zc=37496,Qc=37808,eh=37809,th=37810,nh=37811,ih=37812,sh=37813,rh=37814,ah=37815,oh=37816,lh=37817,ch=37818,hh=37819,dh=37820,uh=37821,nl=36492,fh=36494,ph=36495,ap=36283,mh=36284,gh=36285,xh=36286,Dg=3200,Ig=3201,op=0,Ug=1,ys="",Di="srgb",Ps="srgb-linear",Vh="display-p3",_l="display-p3-linear",al="linear",kt="srgb",ol="rec709",ll="p3",xr=7680,Hd=519,Ng=512,Fg=513,Og=514,lp=515,kg=516,Bg=517,zg=518,Hg=519,vh=35044,Vd="300 es",Ji=2e3,cl=2001;let da=class{addEventListener(e,t){this._listeners===void 0&&(this._listeners={});const n=this._listeners;n[e]===void 0&&(n[e]=[]),n[e].indexOf(t)===-1&&n[e].push(t)}hasEventListener(e,t){if(this._listeners===void 0)return!1;const n=this._listeners;return n[e]!==void 0&&n[e].indexOf(t)!==-1}removeEventListener(e,t){if(this._listeners===void 0)return;const i=this._listeners[e];if(i!==void 0){const r=i.indexOf(t);r!==-1&&i.splice(r,1)}}dispatchEvent(e){if(this._listeners===void 0)return;const n=this._listeners[e.type];if(n!==void 0){e.target=this;const i=n.slice(0);for(let r=0,a=i.length;r<a;r++)i[r].call(this,e);e.target=null}}};const wn=["00","01","02","03","04","05","06","07","08","09","0a","0b","0c","0d","0e","0f","10","11","12","13","14","15","16","17","18","19","1a","1b","1c","1d","1e","1f","20","21","22","23","24","25","26","27","28","29","2a","2b","2c","2d","2e","2f","30","31","32","33","34","35","36","37","38","39","3a","3b","3c","3d","3e","3f","40","41","42","43","44","45","46","47","48","49","4a","4b","4c","4d","4e","4f","50","51","52","53","54","55","56","57","58","59","5a","5b","5c","5d","5e","5f","60","61","62","63","64","65","66","67","68","69","6a","6b","6c","6d","6e","6f","70","71","72","73","74","75","76","77","78","79","7a","7b","7c","7d","7e","7f","80","81","82","83","84","85","86","87","88","89","8a","8b","8c","8d","8e","8f","90","91","92","93","94","95","96","97","98","99","9a","9b","9c","9d","9e","9f","a0","a1","a2","a3","a4","a5","a6","a7","a8","a9","aa","ab","ac","ad","ae","af","b0","b1","b2","b3","b4","b5","b6","b7","b8","b9","ba","bb","bc","bd","be","bf","c0","c1","c2","c3","c4","c5","c6","c7","c8","c9","ca","cb","cc","cd","ce","cf","d0","d1","d2","d3","d4","d5","d6","d7","d8","d9","da","db","dc","dd","de","df","e0","e1","e2","e3","e4","e5","e6","e7","e8","e9","ea","eb","ec","ed","ee","ef","f0","f1","f2","f3","f4","f5","f6","f7","f8","f9","fa","fb","fc","fd","fe","ff"];let Gd=1234567;const qr=Math.PI/180,Ka=180/Math.PI;function Qi(){const s=Math.random()*4294967295|0,e=Math.random()*4294967295|0,t=Math.random()*4294967295|0,n=Math.random()*4294967295|0;return(wn[s&255]+wn[s>>8&255]+wn[s>>16&255]+wn[s>>24&255]+"-"+wn[e&255]+wn[e>>8&255]+"-"+wn[e>>16&15|64]+wn[e>>24&255]+"-"+wn[t&63|128]+wn[t>>8&255]+"-"+wn[t>>16&255]+wn[t>>24&255]+wn[n&255]+wn[n>>8&255]+wn[n>>16&255]+wn[n>>24&255]).toLowerCase()}function Tn(s,e,t){return Math.max(e,Math.min(t,s))}function Gh(s,e){return(s%e+e)%e}function Vg(s,e,t,n,i){return n+(s-e)*(i-n)/(t-e)}function Gg(s,e,t){return s!==e?(t-s)/(e-s):0}function Wa(s,e,t){return(1-t)*s+t*e}function Wg(s,e,t,n){return Wa(s,e,1-Math.exp(-t*n))}function $g(s,e=1){return e-Math.abs(Gh(s,e*2)-e)}function qg(s,e,t){return s<=e?0:s>=t?1:(s=(s-e)/(t-e),s*s*(3-2*s))}function Xg(s,e,t){return s<=e?0:s>=t?1:(s=(s-e)/(t-e),s*s*s*(s*(s*6-15)+10))}function Yg(s,e){return s+Math.floor(Math.random()*(e-s+1))}function jg(s,e){return s+Math.random()*(e-s)}function Kg(s){return s*(.5-Math.random())}function Jg(s){s!==void 0&&(Gd=s);let e=Gd+=1831565813;return e=Math.imul(e^e>>>15,e|1),e^=e+Math.imul(e^e>>>7,e|61),((e^e>>>14)>>>0)/4294967296}function Zg(s){return s*qr}function Qg(s){return s*Ka}function ex(s){return(s&s-1)===0&&s!==0}function tx(s){return Math.pow(2,Math.ceil(Math.log(s)/Math.LN2))}function nx(s){return Math.pow(2,Math.floor(Math.log(s)/Math.LN2))}function ix(s,e,t,n,i){const r=Math.cos,a=Math.sin,o=r(t/2),l=a(t/2),c=r((e+n)/2),h=a((e+n)/2),d=r((e-n)/2),u=a((e-n)/2),f=r((n-e)/2),g=a((n-e)/2);switch(i){case"XYX":s.set(o*h,l*d,l*u,o*c);break;case"YZY":s.set(l*u,o*h,l*d,o*c);break;case"ZXZ":s.set(l*d,l*u,o*h,o*c);break;case"XZX":s.set(o*h,l*g,l*f,o*c);break;case"YXY":s.set(l*f,o*h,l*g,o*c);break;case"ZYZ":s.set(l*g,l*f,o*h,o*c);break;default:console.warn("THREE.MathUtils: .setQuaternionFromProperEuler() encountered an unknown order: "+i)}}function gi(s,e){switch(e.constructor){case Float32Array:return s;case Uint32Array:return s/4294967295;case Uint16Array:return s/65535;case Uint8Array:return s/255;case Int32Array:return Math.max(s/2147483647,-1);case Int16Array:return Math.max(s/32767,-1);case Int8Array:return Math.max(s/127,-1);default:throw new Error("Invalid component type.")}}function Tt(s,e){switch(e.constructor){case Float32Array:return s;case Uint32Array:return Math.round(s*4294967295);case Uint16Array:return Math.round(s*65535);case Uint8Array:return Math.round(s*255);case Int32Array:return Math.round(s*2147483647);case Int16Array:return Math.round(s*32767);case Int8Array:return Math.round(s*127);default:throw new Error("Invalid component type.")}}const sx={DEG2RAD:qr,RAD2DEG:Ka,generateUUID:Qi,clamp:Tn,euclideanModulo:Gh,mapLinear:Vg,inverseLerp:Gg,lerp:Wa,damp:Wg,pingpong:$g,smoothstep:qg,smootherstep:Xg,randInt:Yg,randFloat:jg,randFloatSpread:Kg,seededRandom:Jg,degToRad:Zg,radToDeg:Qg,isPowerOfTwo:ex,ceilPowerOfTwo:tx,floorPowerOfTwo:nx,setQuaternionFromProperEuler:ix,normalize:Tt,denormalize:gi};class Xe{constructor(e=0,t=0){Xe.prototype.isVector2=!0,this.x=e,this.y=t}get width(){return this.x}set width(e){this.x=e}get height(){return this.y}set height(e){this.y=e}set(e,t){return this.x=e,this.y=t,this}setScalar(e){return this.x=e,this.y=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y)}copy(e){return this.x=e.x,this.y=e.y,this}add(e){return this.x+=e.x,this.y+=e.y,this}addScalar(e){return this.x+=e,this.y+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this}subScalar(e){return this.x-=e,this.y-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this}multiply(e){return this.x*=e.x,this.y*=e.y,this}multiplyScalar(e){return this.x*=e,this.y*=e,this}divide(e){return this.x/=e.x,this.y/=e.y,this}divideScalar(e){return this.multiplyScalar(1/e)}applyMatrix3(e){const t=this.x,n=this.y,i=e.elements;return this.x=i[0]*t+i[3]*n+i[6],this.y=i[1]*t+i[4]*n+i[7],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this}negate(){return this.x=-this.x,this.y=-this.y,this}dot(e){return this.x*e.x+this.y*e.y}cross(e){return this.x*e.y-this.y*e.x}lengthSq(){return this.x*this.x+this.y*this.y}length(){return Math.sqrt(this.x*this.x+this.y*this.y)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)}normalize(){return this.divideScalar(this.length()||1)}angle(){return Math.atan2(-this.y,-this.x)+Math.PI}angleTo(e){const t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;const n=this.dot(e)/t;return Math.acos(Tn(n,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){const t=this.x-e.x,n=this.y-e.y;return t*t+n*n}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this}equals(e){return e.x===this.x&&e.y===this.y}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this}rotateAround(e,t){const n=Math.cos(t),i=Math.sin(t),r=this.x-e.x,a=this.y-e.y;return this.x=r*n-a*i+e.x,this.y=r*i+a*n+e.y,this}random(){return this.x=Math.random(),this.y=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y}}class at{constructor(e,t,n,i,r,a,o,l,c){at.prototype.isMatrix3=!0,this.elements=[1,0,0,0,1,0,0,0,1],e!==void 0&&this.set(e,t,n,i,r,a,o,l,c)}set(e,t,n,i,r,a,o,l,c){const h=this.elements;return h[0]=e,h[1]=i,h[2]=o,h[3]=t,h[4]=r,h[5]=l,h[6]=n,h[7]=a,h[8]=c,this}identity(){return this.set(1,0,0,0,1,0,0,0,1),this}copy(e){const t=this.elements,n=e.elements;return t[0]=n[0],t[1]=n[1],t[2]=n[2],t[3]=n[3],t[4]=n[4],t[5]=n[5],t[6]=n[6],t[7]=n[7],t[8]=n[8],this}extractBasis(e,t,n){return e.setFromMatrix3Column(this,0),t.setFromMatrix3Column(this,1),n.setFromMatrix3Column(this,2),this}setFromMatrix4(e){const t=e.elements;return this.set(t[0],t[4],t[8],t[1],t[5],t[9],t[2],t[6],t[10]),this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){const n=e.elements,i=t.elements,r=this.elements,a=n[0],o=n[3],l=n[6],c=n[1],h=n[4],d=n[7],u=n[2],f=n[5],g=n[8],x=i[0],p=i[3],m=i[6],b=i[1],_=i[4],S=i[7],I=i[2],A=i[5],R=i[8];return r[0]=a*x+o*b+l*I,r[3]=a*p+o*_+l*A,r[6]=a*m+o*S+l*R,r[1]=c*x+h*b+d*I,r[4]=c*p+h*_+d*A,r[7]=c*m+h*S+d*R,r[2]=u*x+f*b+g*I,r[5]=u*p+f*_+g*A,r[8]=u*m+f*S+g*R,this}multiplyScalar(e){const t=this.elements;return t[0]*=e,t[3]*=e,t[6]*=e,t[1]*=e,t[4]*=e,t[7]*=e,t[2]*=e,t[5]*=e,t[8]*=e,this}determinant(){const e=this.elements,t=e[0],n=e[1],i=e[2],r=e[3],a=e[4],o=e[5],l=e[6],c=e[7],h=e[8];return t*a*h-t*o*c-n*r*h+n*o*l+i*r*c-i*a*l}invert(){const e=this.elements,t=e[0],n=e[1],i=e[2],r=e[3],a=e[4],o=e[5],l=e[6],c=e[7],h=e[8],d=h*a-o*c,u=o*l-h*r,f=c*r-a*l,g=t*d+n*u+i*f;if(g===0)return this.set(0,0,0,0,0,0,0,0,0);const x=1/g;return e[0]=d*x,e[1]=(i*c-h*n)*x,e[2]=(o*n-i*a)*x,e[3]=u*x,e[4]=(h*t-i*l)*x,e[5]=(i*r-o*t)*x,e[6]=f*x,e[7]=(n*l-c*t)*x,e[8]=(a*t-n*r)*x,this}transpose(){let e;const t=this.elements;return e=t[1],t[1]=t[3],t[3]=e,e=t[2],t[2]=t[6],t[6]=e,e=t[5],t[5]=t[7],t[7]=e,this}getNormalMatrix(e){return this.setFromMatrix4(e).invert().transpose()}transposeIntoArray(e){const t=this.elements;return e[0]=t[0],e[1]=t[3],e[2]=t[6],e[3]=t[1],e[4]=t[4],e[5]=t[7],e[6]=t[2],e[7]=t[5],e[8]=t[8],this}setUvTransform(e,t,n,i,r,a,o){const l=Math.cos(r),c=Math.sin(r);return this.set(n*l,n*c,-n*(l*a+c*o)+a+e,-i*c,i*l,-i*(-c*a+l*o)+o+t,0,0,1),this}scale(e,t){return this.premultiply(Zl.makeScale(e,t)),this}rotate(e){return this.premultiply(Zl.makeRotation(-e)),this}translate(e,t){return this.premultiply(Zl.makeTranslation(e,t)),this}makeTranslation(e,t){return e.isVector2?this.set(1,0,e.x,0,1,e.y,0,0,1):this.set(1,0,e,0,1,t,0,0,1),this}makeRotation(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,-n,0,n,t,0,0,0,1),this}makeScale(e,t){return this.set(e,0,0,0,t,0,0,0,1),this}equals(e){const t=this.elements,n=e.elements;for(let i=0;i<9;i++)if(t[i]!==n[i])return!1;return!0}fromArray(e,t=0){for(let n=0;n<9;n++)this.elements[n]=e[n+t];return this}toArray(e=[],t=0){const n=this.elements;return e[t]=n[0],e[t+1]=n[1],e[t+2]=n[2],e[t+3]=n[3],e[t+4]=n[4],e[t+5]=n[5],e[t+6]=n[6],e[t+7]=n[7],e[t+8]=n[8],e}clone(){return new this.constructor().fromArray(this.elements)}}const Zl=new at;function cp(s){for(let e=s.length-1;e>=0;--e)if(s[e]>=65535)return!0;return!1}function hl(s){return document.createElementNS("http://www.w3.org/1999/xhtml",s)}function rx(){const s=hl("canvas");return s.style.display="block",s}const Wd={};function Xr(s){s in Wd||(Wd[s]=!0,console.warn(s))}function ax(s,e,t){return new Promise(function(n,i){function r(){switch(s.clientWaitSync(e,s.SYNC_FLUSH_COMMANDS_BIT,0)){case s.WAIT_FAILED:i();break;case s.TIMEOUT_EXPIRED:setTimeout(r,t);break;default:n()}}setTimeout(r,t)})}const $d=new at().set(.8224621,.177538,0,.0331941,.9668058,0,.0170827,.0723974,.9105199),qd=new at().set(1.2249401,-.2249404,0,-.0420569,1.0420571,0,-.0196376,-.0786361,1.0982735),Ta={[Ps]:{transfer:al,primaries:ol,luminanceCoefficients:[.2126,.7152,.0722],toReference:s=>s,fromReference:s=>s},[Di]:{transfer:kt,primaries:ol,luminanceCoefficients:[.2126,.7152,.0722],toReference:s=>s.convertSRGBToLinear(),fromReference:s=>s.convertLinearToSRGB()},[_l]:{transfer:al,primaries:ll,luminanceCoefficients:[.2289,.6917,.0793],toReference:s=>s.applyMatrix3(qd),fromReference:s=>s.applyMatrix3($d)},[Vh]:{transfer:kt,primaries:ll,luminanceCoefficients:[.2289,.6917,.0793],toReference:s=>s.convertSRGBToLinear().applyMatrix3(qd),fromReference:s=>s.applyMatrix3($d).convertLinearToSRGB()}},ox=new Set([Ps,_l]),Mt={enabled:!0,_workingColorSpace:Ps,get workingColorSpace(){return this._workingColorSpace},set workingColorSpace(s){if(!ox.has(s))throw new Error(`Unsupported working color space, "${s}".`);this._workingColorSpace=s},convert:function(s,e,t){if(this.enabled===!1||e===t||!e||!t)return s;const n=Ta[e].toReference,i=Ta[t].fromReference;return i(n(s))},fromWorkingColorSpace:function(s,e){return this.convert(s,this._workingColorSpace,e)},toWorkingColorSpace:function(s,e){return this.convert(s,e,this._workingColorSpace)},getPrimaries:function(s){return Ta[s].primaries},getTransfer:function(s){return s===ys?al:Ta[s].transfer},getLuminanceCoefficients:function(s,e=this._workingColorSpace){return s.fromArray(Ta[e].luminanceCoefficients)}};function Yr(s){return s<.04045?s*.0773993808:Math.pow(s*.9478672986+.0521327014,2.4)}function Ql(s){return s<.0031308?s*12.92:1.055*Math.pow(s,.41666)-.055}let vr;class lx{static getDataURL(e){if(/^data:/i.test(e.src)||typeof HTMLCanvasElement>"u")return e.src;let t;if(e instanceof HTMLCanvasElement)t=e;else{vr===void 0&&(vr=hl("canvas")),vr.width=e.width,vr.height=e.height;const n=vr.getContext("2d");e instanceof ImageData?n.putImageData(e,0,0):n.drawImage(e,0,0,e.width,e.height),t=vr}return t.width>2048||t.height>2048?(console.warn("THREE.ImageUtils.getDataURL: Image converted to jpg for performance reasons",e),t.toDataURL("image/jpeg",.6)):t.toDataURL("image/png")}static sRGBToLinear(e){if(typeof HTMLImageElement<"u"&&e instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&e instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&e instanceof ImageBitmap){const t=hl("canvas");t.width=e.width,t.height=e.height;const n=t.getContext("2d");n.drawImage(e,0,0,e.width,e.height);const i=n.getImageData(0,0,e.width,e.height),r=i.data;for(let a=0;a<r.length;a++)r[a]=Yr(r[a]/255)*255;return n.putImageData(i,0,0),t}else if(e.data){const t=e.data.slice(0);for(let n=0;n<t.length;n++)t instanceof Uint8Array||t instanceof Uint8ClampedArray?t[n]=Math.floor(Yr(t[n]/255)*255):t[n]=Yr(t[n]);return{data:t,width:e.width,height:e.height}}else return console.warn("THREE.ImageUtils.sRGBToLinear(): Unsupported image type. No color space conversion applied."),e}}let cx=0;class hp{constructor(e=null){this.isSource=!0,Object.defineProperty(this,"id",{value:cx++}),this.uuid=Qi(),this.data=e,this.dataReady=!0,this.version=0}set needsUpdate(e){e===!0&&this.version++}toJSON(e){const t=e===void 0||typeof e=="string";if(!t&&e.images[this.uuid]!==void 0)return e.images[this.uuid];const n={uuid:this.uuid,url:""},i=this.data;if(i!==null){let r;if(Array.isArray(i)){r=[];for(let a=0,o=i.length;a<o;a++)i[a].isDataTexture?r.push(ec(i[a].image)):r.push(ec(i[a]))}else r=ec(i);n.url=r}return t||(e.images[this.uuid]=n),n}}function ec(s){return typeof HTMLImageElement<"u"&&s instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&s instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&s instanceof ImageBitmap?lx.getDataURL(s):s.data?{data:Array.from(s.data),width:s.width,height:s.height,type:s.data.constructor.name}:(console.warn("THREE.Texture: Unable to serialize Texture."),{})}let hx=0;class On extends da{constructor(e=On.DEFAULT_IMAGE,t=On.DEFAULT_MAPPING,n=js,i=js,r=mi,a=Ks,o=vi,l=ss,c=On.DEFAULT_ANISOTROPY,h=ys){super(),this.isTexture=!0,Object.defineProperty(this,"id",{value:hx++}),this.uuid=Qi(),this.name="",this.source=new hp(e),this.mipmaps=[],this.mapping=t,this.channel=0,this.wrapS=n,this.wrapT=i,this.magFilter=r,this.minFilter=a,this.anisotropy=c,this.format=o,this.internalFormat=null,this.type=l,this.offset=new Xe(0,0),this.repeat=new Xe(1,1),this.center=new Xe(0,0),this.rotation=0,this.matrixAutoUpdate=!0,this.matrix=new at,this.generateMipmaps=!0,this.premultiplyAlpha=!1,this.flipY=!0,this.unpackAlignment=4,this.colorSpace=h,this.userData={},this.version=0,this.onUpdate=null,this.isRenderTargetTexture=!1,this.pmremVersion=0}get image(){return this.source.data}set image(e=null){this.source.data=e}updateMatrix(){this.matrix.setUvTransform(this.offset.x,this.offset.y,this.repeat.x,this.repeat.y,this.rotation,this.center.x,this.center.y)}clone(){return new this.constructor().copy(this)}copy(e){return this.name=e.name,this.source=e.source,this.mipmaps=e.mipmaps.slice(0),this.mapping=e.mapping,this.channel=e.channel,this.wrapS=e.wrapS,this.wrapT=e.wrapT,this.magFilter=e.magFilter,this.minFilter=e.minFilter,this.anisotropy=e.anisotropy,this.format=e.format,this.internalFormat=e.internalFormat,this.type=e.type,this.offset.copy(e.offset),this.repeat.copy(e.repeat),this.center.copy(e.center),this.rotation=e.rotation,this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrix.copy(e.matrix),this.generateMipmaps=e.generateMipmaps,this.premultiplyAlpha=e.premultiplyAlpha,this.flipY=e.flipY,this.unpackAlignment=e.unpackAlignment,this.colorSpace=e.colorSpace,this.userData=JSON.parse(JSON.stringify(e.userData)),this.needsUpdate=!0,this}toJSON(e){const t=e===void 0||typeof e=="string";if(!t&&e.textures[this.uuid]!==void 0)return e.textures[this.uuid];const n={metadata:{version:4.6,type:"Texture",generator:"Texture.toJSON"},uuid:this.uuid,name:this.name,image:this.source.toJSON(e).uuid,mapping:this.mapping,channel:this.channel,repeat:[this.repeat.x,this.repeat.y],offset:[this.offset.x,this.offset.y],center:[this.center.x,this.center.y],rotation:this.rotation,wrap:[this.wrapS,this.wrapT],format:this.format,internalFormat:this.internalFormat,type:this.type,colorSpace:this.colorSpace,minFilter:this.minFilter,magFilter:this.magFilter,anisotropy:this.anisotropy,flipY:this.flipY,generateMipmaps:this.generateMipmaps,premultiplyAlpha:this.premultiplyAlpha,unpackAlignment:this.unpackAlignment};return Object.keys(this.userData).length>0&&(n.userData=this.userData),t||(e.textures[this.uuid]=n),n}dispose(){this.dispatchEvent({type:"dispose"})}transformUv(e){if(this.mapping!==Kf)return e;if(e.applyMatrix3(this.matrix),e.x<0||e.x>1)switch(this.wrapS){case Wc:e.x=e.x-Math.floor(e.x);break;case js:e.x=e.x<0?0:1;break;case $c:Math.abs(Math.floor(e.x)%2)===1?e.x=Math.ceil(e.x)-e.x:e.x=e.x-Math.floor(e.x);break}if(e.y<0||e.y>1)switch(this.wrapT){case Wc:e.y=e.y-Math.floor(e.y);break;case js:e.y=e.y<0?0:1;break;case $c:Math.abs(Math.floor(e.y)%2)===1?e.y=Math.ceil(e.y)-e.y:e.y=e.y-Math.floor(e.y);break}return this.flipY&&(e.y=1-e.y),e}set needsUpdate(e){e===!0&&(this.version++,this.source.needsUpdate=!0)}set needsPMREMUpdate(e){e===!0&&this.pmremVersion++}}On.DEFAULT_IMAGE=null;On.DEFAULT_MAPPING=Kf;On.DEFAULT_ANISOTROPY=1;class rn{constructor(e=0,t=0,n=0,i=1){rn.prototype.isVector4=!0,this.x=e,this.y=t,this.z=n,this.w=i}get width(){return this.z}set width(e){this.z=e}get height(){return this.w}set height(e){this.w=e}set(e,t,n,i){return this.x=e,this.y=t,this.z=n,this.w=i,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this.w=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setW(e){return this.w=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;case 3:this.w=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;case 3:return this.w;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z,this.w)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this.w=e.w!==void 0?e.w:1,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this.w+=e.w,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this.w+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this.w=e.w+t.w,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this.w+=e.w*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this.w-=e.w,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this.w-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this.w=e.w-t.w,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this.w*=e.w,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this.w*=e,this}applyMatrix4(e){const t=this.x,n=this.y,i=this.z,r=this.w,a=e.elements;return this.x=a[0]*t+a[4]*n+a[8]*i+a[12]*r,this.y=a[1]*t+a[5]*n+a[9]*i+a[13]*r,this.z=a[2]*t+a[6]*n+a[10]*i+a[14]*r,this.w=a[3]*t+a[7]*n+a[11]*i+a[15]*r,this}divideScalar(e){return this.multiplyScalar(1/e)}setAxisAngleFromQuaternion(e){this.w=2*Math.acos(e.w);const t=Math.sqrt(1-e.w*e.w);return t<1e-4?(this.x=1,this.y=0,this.z=0):(this.x=e.x/t,this.y=e.y/t,this.z=e.z/t),this}setAxisAngleFromRotationMatrix(e){let t,n,i,r;const l=e.elements,c=l[0],h=l[4],d=l[8],u=l[1],f=l[5],g=l[9],x=l[2],p=l[6],m=l[10];if(Math.abs(h-u)<.01&&Math.abs(d-x)<.01&&Math.abs(g-p)<.01){if(Math.abs(h+u)<.1&&Math.abs(d+x)<.1&&Math.abs(g+p)<.1&&Math.abs(c+f+m-3)<.1)return this.set(1,0,0,0),this;t=Math.PI;const _=(c+1)/2,S=(f+1)/2,I=(m+1)/2,A=(h+u)/4,R=(d+x)/4,N=(g+p)/4;return _>S&&_>I?_<.01?(n=0,i=.707106781,r=.707106781):(n=Math.sqrt(_),i=A/n,r=R/n):S>I?S<.01?(n=.707106781,i=0,r=.707106781):(i=Math.sqrt(S),n=A/i,r=N/i):I<.01?(n=.707106781,i=.707106781,r=0):(r=Math.sqrt(I),n=R/r,i=N/r),this.set(n,i,r,t),this}let b=Math.sqrt((p-g)*(p-g)+(d-x)*(d-x)+(u-h)*(u-h));return Math.abs(b)<.001&&(b=1),this.x=(p-g)/b,this.y=(d-x)/b,this.z=(u-h)/b,this.w=Math.acos((c+f+m-1)/2),this}setFromMatrixPosition(e){const t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this.w=t[15],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this.w=Math.min(this.w,e.w),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this.w=Math.max(this.w,e.w),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this.z=Math.max(e.z,Math.min(t.z,this.z)),this.w=Math.max(e.w,Math.min(t.w,this.w)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this.z=Math.max(e,Math.min(t,this.z)),this.w=Math.max(e,Math.min(t,this.w)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this.w=Math.floor(this.w),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this.w=Math.ceil(this.w),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this.w=Math.round(this.w),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this.w=Math.trunc(this.w),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this.w=-this.w,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z+this.w*e.w}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)+Math.abs(this.w)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this.w+=(e.w-this.w)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this.z=e.z+(t.z-e.z)*n,this.w=e.w+(t.w-e.w)*n,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z&&e.w===this.w}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this.w=e[t+3],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e[t+3]=this.w,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this.w=e.getW(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this.w=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z,yield this.w}}class dx extends da{constructor(e=1,t=1,n={}){super(),this.isRenderTarget=!0,this.width=e,this.height=t,this.depth=1,this.scissor=new rn(0,0,e,t),this.scissorTest=!1,this.viewport=new rn(0,0,e,t);const i={width:e,height:t,depth:1};n=Object.assign({generateMipmaps:!1,internalFormat:null,minFilter:mi,depthBuffer:!0,stencilBuffer:!1,resolveDepthBuffer:!0,resolveStencilBuffer:!0,depthTexture:null,samples:0,count:1},n);const r=new On(i,n.mapping,n.wrapS,n.wrapT,n.magFilter,n.minFilter,n.format,n.type,n.anisotropy,n.colorSpace);r.flipY=!1,r.generateMipmaps=n.generateMipmaps,r.internalFormat=n.internalFormat,this.textures=[];const a=n.count;for(let o=0;o<a;o++)this.textures[o]=r.clone(),this.textures[o].isRenderTargetTexture=!0;this.depthBuffer=n.depthBuffer,this.stencilBuffer=n.stencilBuffer,this.resolveDepthBuffer=n.resolveDepthBuffer,this.resolveStencilBuffer=n.resolveStencilBuffer,this.depthTexture=n.depthTexture,this.samples=n.samples}get texture(){return this.textures[0]}set texture(e){this.textures[0]=e}setSize(e,t,n=1){if(this.width!==e||this.height!==t||this.depth!==n){this.width=e,this.height=t,this.depth=n;for(let i=0,r=this.textures.length;i<r;i++)this.textures[i].image.width=e,this.textures[i].image.height=t,this.textures[i].image.depth=n;this.dispose()}this.viewport.set(0,0,e,t),this.scissor.set(0,0,e,t)}clone(){return new this.constructor().copy(this)}copy(e){this.width=e.width,this.height=e.height,this.depth=e.depth,this.scissor.copy(e.scissor),this.scissorTest=e.scissorTest,this.viewport.copy(e.viewport),this.textures.length=0;for(let n=0,i=e.textures.length;n<i;n++)this.textures[n]=e.textures[n].clone(),this.textures[n].isRenderTargetTexture=!0;const t=Object.assign({},e.texture.image);return this.texture.source=new hp(t),this.depthBuffer=e.depthBuffer,this.stencilBuffer=e.stencilBuffer,this.resolveDepthBuffer=e.resolveDepthBuffer,this.resolveStencilBuffer=e.resolveStencilBuffer,e.depthTexture!==null&&(this.depthTexture=e.depthTexture.clone()),this.samples=e.samples,this}dispose(){this.dispatchEvent({type:"dispose"})}}class er extends dx{constructor(e=1,t=1,n={}){super(e,t,n),this.isWebGLRenderTarget=!0}}class dp extends On{constructor(e=null,t=1,n=1,i=1){super(null),this.isDataArrayTexture=!0,this.image={data:e,width:t,height:n,depth:i},this.magFilter=si,this.minFilter=si,this.wrapR=js,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1,this.layerUpdates=new Set}addLayerUpdate(e){this.layerUpdates.add(e)}clearLayerUpdates(){this.layerUpdates.clear()}}class ux extends On{constructor(e=null,t=1,n=1,i=1){super(null),this.isData3DTexture=!0,this.image={data:e,width:t,height:n,depth:i},this.magFilter=si,this.minFilter=si,this.wrapR=js,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}}class tr{constructor(e=0,t=0,n=0,i=1){this.isQuaternion=!0,this._x=e,this._y=t,this._z=n,this._w=i}static slerpFlat(e,t,n,i,r,a,o){let l=n[i+0],c=n[i+1],h=n[i+2],d=n[i+3];const u=r[a+0],f=r[a+1],g=r[a+2],x=r[a+3];if(o===0){e[t+0]=l,e[t+1]=c,e[t+2]=h,e[t+3]=d;return}if(o===1){e[t+0]=u,e[t+1]=f,e[t+2]=g,e[t+3]=x;return}if(d!==x||l!==u||c!==f||h!==g){let p=1-o;const m=l*u+c*f+h*g+d*x,b=m>=0?1:-1,_=1-m*m;if(_>Number.EPSILON){const I=Math.sqrt(_),A=Math.atan2(I,m*b);p=Math.sin(p*A)/I,o=Math.sin(o*A)/I}const S=o*b;if(l=l*p+u*S,c=c*p+f*S,h=h*p+g*S,d=d*p+x*S,p===1-o){const I=1/Math.sqrt(l*l+c*c+h*h+d*d);l*=I,c*=I,h*=I,d*=I}}e[t]=l,e[t+1]=c,e[t+2]=h,e[t+3]=d}static multiplyQuaternionsFlat(e,t,n,i,r,a){const o=n[i],l=n[i+1],c=n[i+2],h=n[i+3],d=r[a],u=r[a+1],f=r[a+2],g=r[a+3];return e[t]=o*g+h*d+l*f-c*u,e[t+1]=l*g+h*u+c*d-o*f,e[t+2]=c*g+h*f+o*u-l*d,e[t+3]=h*g-o*d-l*u-c*f,e}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get w(){return this._w}set w(e){this._w=e,this._onChangeCallback()}set(e,t,n,i){return this._x=e,this._y=t,this._z=n,this._w=i,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._w)}copy(e){return this._x=e.x,this._y=e.y,this._z=e.z,this._w=e.w,this._onChangeCallback(),this}setFromEuler(e,t=!0){const n=e._x,i=e._y,r=e._z,a=e._order,o=Math.cos,l=Math.sin,c=o(n/2),h=o(i/2),d=o(r/2),u=l(n/2),f=l(i/2),g=l(r/2);switch(a){case"XYZ":this._x=u*h*d+c*f*g,this._y=c*f*d-u*h*g,this._z=c*h*g+u*f*d,this._w=c*h*d-u*f*g;break;case"YXZ":this._x=u*h*d+c*f*g,this._y=c*f*d-u*h*g,this._z=c*h*g-u*f*d,this._w=c*h*d+u*f*g;break;case"ZXY":this._x=u*h*d-c*f*g,this._y=c*f*d+u*h*g,this._z=c*h*g+u*f*d,this._w=c*h*d-u*f*g;break;case"ZYX":this._x=u*h*d-c*f*g,this._y=c*f*d+u*h*g,this._z=c*h*g-u*f*d,this._w=c*h*d+u*f*g;break;case"YZX":this._x=u*h*d+c*f*g,this._y=c*f*d+u*h*g,this._z=c*h*g-u*f*d,this._w=c*h*d-u*f*g;break;case"XZY":this._x=u*h*d-c*f*g,this._y=c*f*d-u*h*g,this._z=c*h*g+u*f*d,this._w=c*h*d+u*f*g;break;default:console.warn("THREE.Quaternion: .setFromEuler() encountered an unknown order: "+a)}return t===!0&&this._onChangeCallback(),this}setFromAxisAngle(e,t){const n=t/2,i=Math.sin(n);return this._x=e.x*i,this._y=e.y*i,this._z=e.z*i,this._w=Math.cos(n),this._onChangeCallback(),this}setFromRotationMatrix(e){const t=e.elements,n=t[0],i=t[4],r=t[8],a=t[1],o=t[5],l=t[9],c=t[2],h=t[6],d=t[10],u=n+o+d;if(u>0){const f=.5/Math.sqrt(u+1);this._w=.25/f,this._x=(h-l)*f,this._y=(r-c)*f,this._z=(a-i)*f}else if(n>o&&n>d){const f=2*Math.sqrt(1+n-o-d);this._w=(h-l)/f,this._x=.25*f,this._y=(i+a)/f,this._z=(r+c)/f}else if(o>d){const f=2*Math.sqrt(1+o-n-d);this._w=(r-c)/f,this._x=(i+a)/f,this._y=.25*f,this._z=(l+h)/f}else{const f=2*Math.sqrt(1+d-n-o);this._w=(a-i)/f,this._x=(r+c)/f,this._y=(l+h)/f,this._z=.25*f}return this._onChangeCallback(),this}setFromUnitVectors(e,t){let n=e.dot(t)+1;return n<Number.EPSILON?(n=0,Math.abs(e.x)>Math.abs(e.z)?(this._x=-e.y,this._y=e.x,this._z=0,this._w=n):(this._x=0,this._y=-e.z,this._z=e.y,this._w=n)):(this._x=e.y*t.z-e.z*t.y,this._y=e.z*t.x-e.x*t.z,this._z=e.x*t.y-e.y*t.x,this._w=n),this.normalize()}angleTo(e){return 2*Math.acos(Math.abs(Tn(this.dot(e),-1,1)))}rotateTowards(e,t){const n=this.angleTo(e);if(n===0)return this;const i=Math.min(1,t/n);return this.slerp(e,i),this}identity(){return this.set(0,0,0,1)}invert(){return this.conjugate()}conjugate(){return this._x*=-1,this._y*=-1,this._z*=-1,this._onChangeCallback(),this}dot(e){return this._x*e._x+this._y*e._y+this._z*e._z+this._w*e._w}lengthSq(){return this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w}length(){return Math.sqrt(this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w)}normalize(){let e=this.length();return e===0?(this._x=0,this._y=0,this._z=0,this._w=1):(e=1/e,this._x=this._x*e,this._y=this._y*e,this._z=this._z*e,this._w=this._w*e),this._onChangeCallback(),this}multiply(e){return this.multiplyQuaternions(this,e)}premultiply(e){return this.multiplyQuaternions(e,this)}multiplyQuaternions(e,t){const n=e._x,i=e._y,r=e._z,a=e._w,o=t._x,l=t._y,c=t._z,h=t._w;return this._x=n*h+a*o+i*c-r*l,this._y=i*h+a*l+r*o-n*c,this._z=r*h+a*c+n*l-i*o,this._w=a*h-n*o-i*l-r*c,this._onChangeCallback(),this}slerp(e,t){if(t===0)return this;if(t===1)return this.copy(e);const n=this._x,i=this._y,r=this._z,a=this._w;let o=a*e._w+n*e._x+i*e._y+r*e._z;if(o<0?(this._w=-e._w,this._x=-e._x,this._y=-e._y,this._z=-e._z,o=-o):this.copy(e),o>=1)return this._w=a,this._x=n,this._y=i,this._z=r,this;const l=1-o*o;if(l<=Number.EPSILON){const f=1-t;return this._w=f*a+t*this._w,this._x=f*n+t*this._x,this._y=f*i+t*this._y,this._z=f*r+t*this._z,this.normalize(),this}const c=Math.sqrt(l),h=Math.atan2(c,o),d=Math.sin((1-t)*h)/c,u=Math.sin(t*h)/c;return this._w=a*d+this._w*u,this._x=n*d+this._x*u,this._y=i*d+this._y*u,this._z=r*d+this._z*u,this._onChangeCallback(),this}slerpQuaternions(e,t,n){return this.copy(e).slerp(t,n)}random(){const e=2*Math.PI*Math.random(),t=2*Math.PI*Math.random(),n=Math.random(),i=Math.sqrt(1-n),r=Math.sqrt(n);return this.set(i*Math.sin(e),i*Math.cos(e),r*Math.sin(t),r*Math.cos(t))}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._w===this._w}fromArray(e,t=0){return this._x=e[t],this._y=e[t+1],this._z=e[t+2],this._w=e[t+3],this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._w,e}fromBufferAttribute(e,t){return this._x=e.getX(t),this._y=e.getY(t),this._z=e.getZ(t),this._w=e.getW(t),this._onChangeCallback(),this}toJSON(){return this.toArray()}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._w}}class V{constructor(e=0,t=0,n=0){V.prototype.isVector3=!0,this.x=e,this.y=t,this.z=n}set(e,t,n){return n===void 0&&(n=this.z),this.x=e,this.y=t,this.z=n,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this}multiplyVectors(e,t){return this.x=e.x*t.x,this.y=e.y*t.y,this.z=e.z*t.z,this}applyEuler(e){return this.applyQuaternion(Xd.setFromEuler(e))}applyAxisAngle(e,t){return this.applyQuaternion(Xd.setFromAxisAngle(e,t))}applyMatrix3(e){const t=this.x,n=this.y,i=this.z,r=e.elements;return this.x=r[0]*t+r[3]*n+r[6]*i,this.y=r[1]*t+r[4]*n+r[7]*i,this.z=r[2]*t+r[5]*n+r[8]*i,this}applyNormalMatrix(e){return this.applyMatrix3(e).normalize()}applyMatrix4(e){const t=this.x,n=this.y,i=this.z,r=e.elements,a=1/(r[3]*t+r[7]*n+r[11]*i+r[15]);return this.x=(r[0]*t+r[4]*n+r[8]*i+r[12])*a,this.y=(r[1]*t+r[5]*n+r[9]*i+r[13])*a,this.z=(r[2]*t+r[6]*n+r[10]*i+r[14])*a,this}applyQuaternion(e){const t=this.x,n=this.y,i=this.z,r=e.x,a=e.y,o=e.z,l=e.w,c=2*(a*i-o*n),h=2*(o*t-r*i),d=2*(r*n-a*t);return this.x=t+l*c+a*d-o*h,this.y=n+l*h+o*c-r*d,this.z=i+l*d+r*h-a*c,this}project(e){return this.applyMatrix4(e.matrixWorldInverse).applyMatrix4(e.projectionMatrix)}unproject(e){return this.applyMatrix4(e.projectionMatrixInverse).applyMatrix4(e.matrixWorld)}transformDirection(e){const t=this.x,n=this.y,i=this.z,r=e.elements;return this.x=r[0]*t+r[4]*n+r[8]*i,this.y=r[1]*t+r[5]*n+r[9]*i,this.z=r[2]*t+r[6]*n+r[10]*i,this.normalize()}divide(e){return this.x/=e.x,this.y/=e.y,this.z/=e.z,this}divideScalar(e){return this.multiplyScalar(1/e)}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this.z=Math.max(e.z,Math.min(t.z,this.z)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this.z=Math.max(e,Math.min(t,this.z)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this.z=e.z+(t.z-e.z)*n,this}cross(e){return this.crossVectors(this,e)}crossVectors(e,t){const n=e.x,i=e.y,r=e.z,a=t.x,o=t.y,l=t.z;return this.x=i*l-r*o,this.y=r*a-n*l,this.z=n*o-i*a,this}projectOnVector(e){const t=e.lengthSq();if(t===0)return this.set(0,0,0);const n=e.dot(this)/t;return this.copy(e).multiplyScalar(n)}projectOnPlane(e){return tc.copy(this).projectOnVector(e),this.sub(tc)}reflect(e){return this.sub(tc.copy(e).multiplyScalar(2*this.dot(e)))}angleTo(e){const t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;const n=this.dot(e)/t;return Math.acos(Tn(n,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){const t=this.x-e.x,n=this.y-e.y,i=this.z-e.z;return t*t+n*n+i*i}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)+Math.abs(this.z-e.z)}setFromSpherical(e){return this.setFromSphericalCoords(e.radius,e.phi,e.theta)}setFromSphericalCoords(e,t,n){const i=Math.sin(t)*e;return this.x=i*Math.sin(n),this.y=Math.cos(t)*e,this.z=i*Math.cos(n),this}setFromCylindrical(e){return this.setFromCylindricalCoords(e.radius,e.theta,e.y)}setFromCylindricalCoords(e,t,n){return this.x=e*Math.sin(t),this.y=n,this.z=e*Math.cos(t),this}setFromMatrixPosition(e){const t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this}setFromMatrixScale(e){const t=this.setFromMatrixColumn(e,0).length(),n=this.setFromMatrixColumn(e,1).length(),i=this.setFromMatrixColumn(e,2).length();return this.x=t,this.y=n,this.z=i,this}setFromMatrixColumn(e,t){return this.fromArray(e.elements,t*4)}setFromMatrix3Column(e,t){return this.fromArray(e.elements,t*3)}setFromEuler(e){return this.x=e._x,this.y=e._y,this.z=e._z,this}setFromColor(e){return this.x=e.r,this.y=e.g,this.z=e.b,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this}randomDirection(){const e=Math.random()*Math.PI*2,t=Math.random()*2-1,n=Math.sqrt(1-t*t);return this.x=n*Math.cos(e),this.y=t,this.z=n*Math.sin(e),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z}}const tc=new V,Xd=new tr;class to{constructor(e=new V(1/0,1/0,1/0),t=new V(-1/0,-1/0,-1/0)){this.isBox3=!0,this.min=e,this.max=t}set(e,t){return this.min.copy(e),this.max.copy(t),this}setFromArray(e){this.makeEmpty();for(let t=0,n=e.length;t<n;t+=3)this.expandByPoint(hi.fromArray(e,t));return this}setFromBufferAttribute(e){this.makeEmpty();for(let t=0,n=e.count;t<n;t++)this.expandByPoint(hi.fromBufferAttribute(e,t));return this}setFromPoints(e){this.makeEmpty();for(let t=0,n=e.length;t<n;t++)this.expandByPoint(e[t]);return this}setFromCenterAndSize(e,t){const n=hi.copy(t).multiplyScalar(.5);return this.min.copy(e).sub(n),this.max.copy(e).add(n),this}setFromObject(e,t=!1){return this.makeEmpty(),this.expandByObject(e,t)}clone(){return new this.constructor().copy(this)}copy(e){return this.min.copy(e.min),this.max.copy(e.max),this}makeEmpty(){return this.min.x=this.min.y=this.min.z=1/0,this.max.x=this.max.y=this.max.z=-1/0,this}isEmpty(){return this.max.x<this.min.x||this.max.y<this.min.y||this.max.z<this.min.z}getCenter(e){return this.isEmpty()?e.set(0,0,0):e.addVectors(this.min,this.max).multiplyScalar(.5)}getSize(e){return this.isEmpty()?e.set(0,0,0):e.subVectors(this.max,this.min)}expandByPoint(e){return this.min.min(e),this.max.max(e),this}expandByVector(e){return this.min.sub(e),this.max.add(e),this}expandByScalar(e){return this.min.addScalar(-e),this.max.addScalar(e),this}expandByObject(e,t=!1){e.updateWorldMatrix(!1,!1);const n=e.geometry;if(n!==void 0){const r=n.getAttribute("position");if(t===!0&&r!==void 0&&e.isInstancedMesh!==!0)for(let a=0,o=r.count;a<o;a++)e.isMesh===!0?e.getVertexPosition(a,hi):hi.fromBufferAttribute(r,a),hi.applyMatrix4(e.matrixWorld),this.expandByPoint(hi);else e.boundingBox!==void 0?(e.boundingBox===null&&e.computeBoundingBox(),go.copy(e.boundingBox)):(n.boundingBox===null&&n.computeBoundingBox(),go.copy(n.boundingBox)),go.applyMatrix4(e.matrixWorld),this.union(go)}const i=e.children;for(let r=0,a=i.length;r<a;r++)this.expandByObject(i[r],t);return this}containsPoint(e){return e.x>=this.min.x&&e.x<=this.max.x&&e.y>=this.min.y&&e.y<=this.max.y&&e.z>=this.min.z&&e.z<=this.max.z}containsBox(e){return this.min.x<=e.min.x&&e.max.x<=this.max.x&&this.min.y<=e.min.y&&e.max.y<=this.max.y&&this.min.z<=e.min.z&&e.max.z<=this.max.z}getParameter(e,t){return t.set((e.x-this.min.x)/(this.max.x-this.min.x),(e.y-this.min.y)/(this.max.y-this.min.y),(e.z-this.min.z)/(this.max.z-this.min.z))}intersectsBox(e){return e.max.x>=this.min.x&&e.min.x<=this.max.x&&e.max.y>=this.min.y&&e.min.y<=this.max.y&&e.max.z>=this.min.z&&e.min.z<=this.max.z}intersectsSphere(e){return this.clampPoint(e.center,hi),hi.distanceToSquared(e.center)<=e.radius*e.radius}intersectsPlane(e){let t,n;return e.normal.x>0?(t=e.normal.x*this.min.x,n=e.normal.x*this.max.x):(t=e.normal.x*this.max.x,n=e.normal.x*this.min.x),e.normal.y>0?(t+=e.normal.y*this.min.y,n+=e.normal.y*this.max.y):(t+=e.normal.y*this.max.y,n+=e.normal.y*this.min.y),e.normal.z>0?(t+=e.normal.z*this.min.z,n+=e.normal.z*this.max.z):(t+=e.normal.z*this.max.z,n+=e.normal.z*this.min.z),t<=-e.constant&&n>=-e.constant}intersectsTriangle(e){if(this.isEmpty())return!1;this.getCenter(Aa),xo.subVectors(this.max,Aa),_r.subVectors(e.a,Aa),yr.subVectors(e.b,Aa),br.subVectors(e.c,Aa),ds.subVectors(yr,_r),us.subVectors(br,yr),Os.subVectors(_r,br);let t=[0,-ds.z,ds.y,0,-us.z,us.y,0,-Os.z,Os.y,ds.z,0,-ds.x,us.z,0,-us.x,Os.z,0,-Os.x,-ds.y,ds.x,0,-us.y,us.x,0,-Os.y,Os.x,0];return!nc(t,_r,yr,br,xo)||(t=[1,0,0,0,1,0,0,0,1],!nc(t,_r,yr,br,xo))?!1:(vo.crossVectors(ds,us),t=[vo.x,vo.y,vo.z],nc(t,_r,yr,br,xo))}clampPoint(e,t){return t.copy(e).clamp(this.min,this.max)}distanceToPoint(e){return this.clampPoint(e,hi).distanceTo(e)}getBoundingSphere(e){return this.isEmpty()?e.makeEmpty():(this.getCenter(e.center),e.radius=this.getSize(hi).length()*.5),e}intersect(e){return this.min.max(e.min),this.max.min(e.max),this.isEmpty()&&this.makeEmpty(),this}union(e){return this.min.min(e.min),this.max.max(e.max),this}applyMatrix4(e){return this.isEmpty()?this:(Gi[0].set(this.min.x,this.min.y,this.min.z).applyMatrix4(e),Gi[1].set(this.min.x,this.min.y,this.max.z).applyMatrix4(e),Gi[2].set(this.min.x,this.max.y,this.min.z).applyMatrix4(e),Gi[3].set(this.min.x,this.max.y,this.max.z).applyMatrix4(e),Gi[4].set(this.max.x,this.min.y,this.min.z).applyMatrix4(e),Gi[5].set(this.max.x,this.min.y,this.max.z).applyMatrix4(e),Gi[6].set(this.max.x,this.max.y,this.min.z).applyMatrix4(e),Gi[7].set(this.max.x,this.max.y,this.max.z).applyMatrix4(e),this.setFromPoints(Gi),this)}translate(e){return this.min.add(e),this.max.add(e),this}equals(e){return e.min.equals(this.min)&&e.max.equals(this.max)}}const Gi=[new V,new V,new V,new V,new V,new V,new V,new V],hi=new V,go=new to,_r=new V,yr=new V,br=new V,ds=new V,us=new V,Os=new V,Aa=new V,xo=new V,vo=new V,ks=new V;function nc(s,e,t,n,i){for(let r=0,a=s.length-3;r<=a;r+=3){ks.fromArray(s,r);const o=i.x*Math.abs(ks.x)+i.y*Math.abs(ks.y)+i.z*Math.abs(ks.z),l=e.dot(ks),c=t.dot(ks),h=n.dot(ks);if(Math.max(-Math.max(l,c,h),Math.min(l,c,h))>o)return!1}return!0}const fx=new to,Ca=new V,ic=new V;class no{constructor(e=new V,t=-1){this.isSphere=!0,this.center=e,this.radius=t}set(e,t){return this.center.copy(e),this.radius=t,this}setFromPoints(e,t){const n=this.center;t!==void 0?n.copy(t):fx.setFromPoints(e).getCenter(n);let i=0;for(let r=0,a=e.length;r<a;r++)i=Math.max(i,n.distanceToSquared(e[r]));return this.radius=Math.sqrt(i),this}copy(e){return this.center.copy(e.center),this.radius=e.radius,this}isEmpty(){return this.radius<0}makeEmpty(){return this.center.set(0,0,0),this.radius=-1,this}containsPoint(e){return e.distanceToSquared(this.center)<=this.radius*this.radius}distanceToPoint(e){return e.distanceTo(this.center)-this.radius}intersectsSphere(e){const t=this.radius+e.radius;return e.center.distanceToSquared(this.center)<=t*t}intersectsBox(e){return e.intersectsSphere(this)}intersectsPlane(e){return Math.abs(e.distanceToPoint(this.center))<=this.radius}clampPoint(e,t){const n=this.center.distanceToSquared(e);return t.copy(e),n>this.radius*this.radius&&(t.sub(this.center).normalize(),t.multiplyScalar(this.radius).add(this.center)),t}getBoundingBox(e){return this.isEmpty()?(e.makeEmpty(),e):(e.set(this.center,this.center),e.expandByScalar(this.radius),e)}applyMatrix4(e){return this.center.applyMatrix4(e),this.radius=this.radius*e.getMaxScaleOnAxis(),this}translate(e){return this.center.add(e),this}expandByPoint(e){if(this.isEmpty())return this.center.copy(e),this.radius=0,this;Ca.subVectors(e,this.center);const t=Ca.lengthSq();if(t>this.radius*this.radius){const n=Math.sqrt(t),i=(n-this.radius)*.5;this.center.addScaledVector(Ca,i/n),this.radius+=i}return this}union(e){return e.isEmpty()?this:this.isEmpty()?(this.copy(e),this):(this.center.equals(e.center)===!0?this.radius=Math.max(this.radius,e.radius):(ic.subVectors(e.center,this.center).setLength(e.radius),this.expandByPoint(Ca.copy(e.center).add(ic)),this.expandByPoint(Ca.copy(e.center).sub(ic))),this)}equals(e){return e.center.equals(this.center)&&e.radius===this.radius}clone(){return new this.constructor().copy(this)}}const Wi=new V,sc=new V,_o=new V,fs=new V,rc=new V,yo=new V,ac=new V;class io{constructor(e=new V,t=new V(0,0,-1)){this.origin=e,this.direction=t}set(e,t){return this.origin.copy(e),this.direction.copy(t),this}copy(e){return this.origin.copy(e.origin),this.direction.copy(e.direction),this}at(e,t){return t.copy(this.origin).addScaledVector(this.direction,e)}lookAt(e){return this.direction.copy(e).sub(this.origin).normalize(),this}recast(e){return this.origin.copy(this.at(e,Wi)),this}closestPointToPoint(e,t){t.subVectors(e,this.origin);const n=t.dot(this.direction);return n<0?t.copy(this.origin):t.copy(this.origin).addScaledVector(this.direction,n)}distanceToPoint(e){return Math.sqrt(this.distanceSqToPoint(e))}distanceSqToPoint(e){const t=Wi.subVectors(e,this.origin).dot(this.direction);return t<0?this.origin.distanceToSquared(e):(Wi.copy(this.origin).addScaledVector(this.direction,t),Wi.distanceToSquared(e))}distanceSqToSegment(e,t,n,i){sc.copy(e).add(t).multiplyScalar(.5),_o.copy(t).sub(e).normalize(),fs.copy(this.origin).sub(sc);const r=e.distanceTo(t)*.5,a=-this.direction.dot(_o),o=fs.dot(this.direction),l=-fs.dot(_o),c=fs.lengthSq(),h=Math.abs(1-a*a);let d,u,f,g;if(h>0)if(d=a*l-o,u=a*o-l,g=r*h,d>=0)if(u>=-g)if(u<=g){const x=1/h;d*=x,u*=x,f=d*(d+a*u+2*o)+u*(a*d+u+2*l)+c}else u=r,d=Math.max(0,-(a*u+o)),f=-d*d+u*(u+2*l)+c;else u=-r,d=Math.max(0,-(a*u+o)),f=-d*d+u*(u+2*l)+c;else u<=-g?(d=Math.max(0,-(-a*r+o)),u=d>0?-r:Math.min(Math.max(-r,-l),r),f=-d*d+u*(u+2*l)+c):u<=g?(d=0,u=Math.min(Math.max(-r,-l),r),f=u*(u+2*l)+c):(d=Math.max(0,-(a*r+o)),u=d>0?r:Math.min(Math.max(-r,-l),r),f=-d*d+u*(u+2*l)+c);else u=a>0?-r:r,d=Math.max(0,-(a*u+o)),f=-d*d+u*(u+2*l)+c;return n&&n.copy(this.origin).addScaledVector(this.direction,d),i&&i.copy(sc).addScaledVector(_o,u),f}intersectSphere(e,t){Wi.subVectors(e.center,this.origin);const n=Wi.dot(this.direction),i=Wi.dot(Wi)-n*n,r=e.radius*e.radius;if(i>r)return null;const a=Math.sqrt(r-i),o=n-a,l=n+a;return l<0?null:o<0?this.at(l,t):this.at(o,t)}intersectsSphere(e){return this.distanceSqToPoint(e.center)<=e.radius*e.radius}distanceToPlane(e){const t=e.normal.dot(this.direction);if(t===0)return e.distanceToPoint(this.origin)===0?0:null;const n=-(this.origin.dot(e.normal)+e.constant)/t;return n>=0?n:null}intersectPlane(e,t){const n=this.distanceToPlane(e);return n===null?null:this.at(n,t)}intersectsPlane(e){const t=e.distanceToPoint(this.origin);return t===0||e.normal.dot(this.direction)*t<0}intersectBox(e,t){let n,i,r,a,o,l;const c=1/this.direction.x,h=1/this.direction.y,d=1/this.direction.z,u=this.origin;return c>=0?(n=(e.min.x-u.x)*c,i=(e.max.x-u.x)*c):(n=(e.max.x-u.x)*c,i=(e.min.x-u.x)*c),h>=0?(r=(e.min.y-u.y)*h,a=(e.max.y-u.y)*h):(r=(e.max.y-u.y)*h,a=(e.min.y-u.y)*h),n>a||r>i||((r>n||isNaN(n))&&(n=r),(a<i||isNaN(i))&&(i=a),d>=0?(o=(e.min.z-u.z)*d,l=(e.max.z-u.z)*d):(o=(e.max.z-u.z)*d,l=(e.min.z-u.z)*d),n>l||o>i)||((o>n||n!==n)&&(n=o),(l<i||i!==i)&&(i=l),i<0)?null:this.at(n>=0?n:i,t)}intersectsBox(e){return this.intersectBox(e,Wi)!==null}intersectTriangle(e,t,n,i,r){rc.subVectors(t,e),yo.subVectors(n,e),ac.crossVectors(rc,yo);let a=this.direction.dot(ac),o;if(a>0){if(i)return null;o=1}else if(a<0)o=-1,a=-a;else return null;fs.subVectors(this.origin,e);const l=o*this.direction.dot(yo.crossVectors(fs,yo));if(l<0)return null;const c=o*this.direction.dot(rc.cross(fs));if(c<0||l+c>a)return null;const h=-o*fs.dot(ac);return h<0?null:this.at(h/a,r)}applyMatrix4(e){return this.origin.applyMatrix4(e),this.direction.transformDirection(e),this}equals(e){return e.origin.equals(this.origin)&&e.direction.equals(this.direction)}clone(){return new this.constructor().copy(this)}}class Bt{constructor(e,t,n,i,r,a,o,l,c,h,d,u,f,g,x,p){Bt.prototype.isMatrix4=!0,this.elements=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],e!==void 0&&this.set(e,t,n,i,r,a,o,l,c,h,d,u,f,g,x,p)}set(e,t,n,i,r,a,o,l,c,h,d,u,f,g,x,p){const m=this.elements;return m[0]=e,m[4]=t,m[8]=n,m[12]=i,m[1]=r,m[5]=a,m[9]=o,m[13]=l,m[2]=c,m[6]=h,m[10]=d,m[14]=u,m[3]=f,m[7]=g,m[11]=x,m[15]=p,this}identity(){return this.set(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1),this}clone(){return new Bt().fromArray(this.elements)}copy(e){const t=this.elements,n=e.elements;return t[0]=n[0],t[1]=n[1],t[2]=n[2],t[3]=n[3],t[4]=n[4],t[5]=n[5],t[6]=n[6],t[7]=n[7],t[8]=n[8],t[9]=n[9],t[10]=n[10],t[11]=n[11],t[12]=n[12],t[13]=n[13],t[14]=n[14],t[15]=n[15],this}copyPosition(e){const t=this.elements,n=e.elements;return t[12]=n[12],t[13]=n[13],t[14]=n[14],this}setFromMatrix3(e){const t=e.elements;return this.set(t[0],t[3],t[6],0,t[1],t[4],t[7],0,t[2],t[5],t[8],0,0,0,0,1),this}extractBasis(e,t,n){return e.setFromMatrixColumn(this,0),t.setFromMatrixColumn(this,1),n.setFromMatrixColumn(this,2),this}makeBasis(e,t,n){return this.set(e.x,t.x,n.x,0,e.y,t.y,n.y,0,e.z,t.z,n.z,0,0,0,0,1),this}extractRotation(e){const t=this.elements,n=e.elements,i=1/Sr.setFromMatrixColumn(e,0).length(),r=1/Sr.setFromMatrixColumn(e,1).length(),a=1/Sr.setFromMatrixColumn(e,2).length();return t[0]=n[0]*i,t[1]=n[1]*i,t[2]=n[2]*i,t[3]=0,t[4]=n[4]*r,t[5]=n[5]*r,t[6]=n[6]*r,t[7]=0,t[8]=n[8]*a,t[9]=n[9]*a,t[10]=n[10]*a,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromEuler(e){const t=this.elements,n=e.x,i=e.y,r=e.z,a=Math.cos(n),o=Math.sin(n),l=Math.cos(i),c=Math.sin(i),h=Math.cos(r),d=Math.sin(r);if(e.order==="XYZ"){const u=a*h,f=a*d,g=o*h,x=o*d;t[0]=l*h,t[4]=-l*d,t[8]=c,t[1]=f+g*c,t[5]=u-x*c,t[9]=-o*l,t[2]=x-u*c,t[6]=g+f*c,t[10]=a*l}else if(e.order==="YXZ"){const u=l*h,f=l*d,g=c*h,x=c*d;t[0]=u+x*o,t[4]=g*o-f,t[8]=a*c,t[1]=a*d,t[5]=a*h,t[9]=-o,t[2]=f*o-g,t[6]=x+u*o,t[10]=a*l}else if(e.order==="ZXY"){const u=l*h,f=l*d,g=c*h,x=c*d;t[0]=u-x*o,t[4]=-a*d,t[8]=g+f*o,t[1]=f+g*o,t[5]=a*h,t[9]=x-u*o,t[2]=-a*c,t[6]=o,t[10]=a*l}else if(e.order==="ZYX"){const u=a*h,f=a*d,g=o*h,x=o*d;t[0]=l*h,t[4]=g*c-f,t[8]=u*c+x,t[1]=l*d,t[5]=x*c+u,t[9]=f*c-g,t[2]=-c,t[6]=o*l,t[10]=a*l}else if(e.order==="YZX"){const u=a*l,f=a*c,g=o*l,x=o*c;t[0]=l*h,t[4]=x-u*d,t[8]=g*d+f,t[1]=d,t[5]=a*h,t[9]=-o*h,t[2]=-c*h,t[6]=f*d+g,t[10]=u-x*d}else if(e.order==="XZY"){const u=a*l,f=a*c,g=o*l,x=o*c;t[0]=l*h,t[4]=-d,t[8]=c*h,t[1]=u*d+x,t[5]=a*h,t[9]=f*d-g,t[2]=g*d-f,t[6]=o*h,t[10]=x*d+u}return t[3]=0,t[7]=0,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromQuaternion(e){return this.compose(px,e,mx)}lookAt(e,t,n){const i=this.elements;return Wn.subVectors(e,t),Wn.lengthSq()===0&&(Wn.z=1),Wn.normalize(),ps.crossVectors(n,Wn),ps.lengthSq()===0&&(Math.abs(n.z)===1?Wn.x+=1e-4:Wn.z+=1e-4,Wn.normalize(),ps.crossVectors(n,Wn)),ps.normalize(),bo.crossVectors(Wn,ps),i[0]=ps.x,i[4]=bo.x,i[8]=Wn.x,i[1]=ps.y,i[5]=bo.y,i[9]=Wn.y,i[2]=ps.z,i[6]=bo.z,i[10]=Wn.z,this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){const n=e.elements,i=t.elements,r=this.elements,a=n[0],o=n[4],l=n[8],c=n[12],h=n[1],d=n[5],u=n[9],f=n[13],g=n[2],x=n[6],p=n[10],m=n[14],b=n[3],_=n[7],S=n[11],I=n[15],A=i[0],R=i[4],N=i[8],M=i[12],y=i[1],P=i[5],X=i[9],H=i[13],J=i[2],q=i[6],ee=i[10],j=i[14],ne=i[3],ge=i[7],ue=i[11],ye=i[15];return r[0]=a*A+o*y+l*J+c*ne,r[4]=a*R+o*P+l*q+c*ge,r[8]=a*N+o*X+l*ee+c*ue,r[12]=a*M+o*H+l*j+c*ye,r[1]=h*A+d*y+u*J+f*ne,r[5]=h*R+d*P+u*q+f*ge,r[9]=h*N+d*X+u*ee+f*ue,r[13]=h*M+d*H+u*j+f*ye,r[2]=g*A+x*y+p*J+m*ne,r[6]=g*R+x*P+p*q+m*ge,r[10]=g*N+x*X+p*ee+m*ue,r[14]=g*M+x*H+p*j+m*ye,r[3]=b*A+_*y+S*J+I*ne,r[7]=b*R+_*P+S*q+I*ge,r[11]=b*N+_*X+S*ee+I*ue,r[15]=b*M+_*H+S*j+I*ye,this}multiplyScalar(e){const t=this.elements;return t[0]*=e,t[4]*=e,t[8]*=e,t[12]*=e,t[1]*=e,t[5]*=e,t[9]*=e,t[13]*=e,t[2]*=e,t[6]*=e,t[10]*=e,t[14]*=e,t[3]*=e,t[7]*=e,t[11]*=e,t[15]*=e,this}determinant(){const e=this.elements,t=e[0],n=e[4],i=e[8],r=e[12],a=e[1],o=e[5],l=e[9],c=e[13],h=e[2],d=e[6],u=e[10],f=e[14],g=e[3],x=e[7],p=e[11],m=e[15];return g*(+r*l*d-i*c*d-r*o*u+n*c*u+i*o*f-n*l*f)+x*(+t*l*f-t*c*u+r*a*u-i*a*f+i*c*h-r*l*h)+p*(+t*c*d-t*o*f-r*a*d+n*a*f+r*o*h-n*c*h)+m*(-i*o*h-t*l*d+t*o*u+i*a*d-n*a*u+n*l*h)}transpose(){const e=this.elements;let t;return t=e[1],e[1]=e[4],e[4]=t,t=e[2],e[2]=e[8],e[8]=t,t=e[6],e[6]=e[9],e[9]=t,t=e[3],e[3]=e[12],e[12]=t,t=e[7],e[7]=e[13],e[13]=t,t=e[11],e[11]=e[14],e[14]=t,this}setPosition(e,t,n){const i=this.elements;return e.isVector3?(i[12]=e.x,i[13]=e.y,i[14]=e.z):(i[12]=e,i[13]=t,i[14]=n),this}invert(){const e=this.elements,t=e[0],n=e[1],i=e[2],r=e[3],a=e[4],o=e[5],l=e[6],c=e[7],h=e[8],d=e[9],u=e[10],f=e[11],g=e[12],x=e[13],p=e[14],m=e[15],b=d*p*c-x*u*c+x*l*f-o*p*f-d*l*m+o*u*m,_=g*u*c-h*p*c-g*l*f+a*p*f+h*l*m-a*u*m,S=h*x*c-g*d*c+g*o*f-a*x*f-h*o*m+a*d*m,I=g*d*l-h*x*l-g*o*u+a*x*u+h*o*p-a*d*p,A=t*b+n*_+i*S+r*I;if(A===0)return this.set(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);const R=1/A;return e[0]=b*R,e[1]=(x*u*r-d*p*r-x*i*f+n*p*f+d*i*m-n*u*m)*R,e[2]=(o*p*r-x*l*r+x*i*c-n*p*c-o*i*m+n*l*m)*R,e[3]=(d*l*r-o*u*r-d*i*c+n*u*c+o*i*f-n*l*f)*R,e[4]=_*R,e[5]=(h*p*r-g*u*r+g*i*f-t*p*f-h*i*m+t*u*m)*R,e[6]=(g*l*r-a*p*r-g*i*c+t*p*c+a*i*m-t*l*m)*R,e[7]=(a*u*r-h*l*r+h*i*c-t*u*c-a*i*f+t*l*f)*R,e[8]=S*R,e[9]=(g*d*r-h*x*r-g*n*f+t*x*f+h*n*m-t*d*m)*R,e[10]=(a*x*r-g*o*r+g*n*c-t*x*c-a*n*m+t*o*m)*R,e[11]=(h*o*r-a*d*r-h*n*c+t*d*c+a*n*f-t*o*f)*R,e[12]=I*R,e[13]=(h*x*i-g*d*i+g*n*u-t*x*u-h*n*p+t*d*p)*R,e[14]=(g*o*i-a*x*i-g*n*l+t*x*l+a*n*p-t*o*p)*R,e[15]=(a*d*i-h*o*i+h*n*l-t*d*l-a*n*u+t*o*u)*R,this}scale(e){const t=this.elements,n=e.x,i=e.y,r=e.z;return t[0]*=n,t[4]*=i,t[8]*=r,t[1]*=n,t[5]*=i,t[9]*=r,t[2]*=n,t[6]*=i,t[10]*=r,t[3]*=n,t[7]*=i,t[11]*=r,this}getMaxScaleOnAxis(){const e=this.elements,t=e[0]*e[0]+e[1]*e[1]+e[2]*e[2],n=e[4]*e[4]+e[5]*e[5]+e[6]*e[6],i=e[8]*e[8]+e[9]*e[9]+e[10]*e[10];return Math.sqrt(Math.max(t,n,i))}makeTranslation(e,t,n){return e.isVector3?this.set(1,0,0,e.x,0,1,0,e.y,0,0,1,e.z,0,0,0,1):this.set(1,0,0,e,0,1,0,t,0,0,1,n,0,0,0,1),this}makeRotationX(e){const t=Math.cos(e),n=Math.sin(e);return this.set(1,0,0,0,0,t,-n,0,0,n,t,0,0,0,0,1),this}makeRotationY(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,0,n,0,0,1,0,0,-n,0,t,0,0,0,0,1),this}makeRotationZ(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,-n,0,0,n,t,0,0,0,0,1,0,0,0,0,1),this}makeRotationAxis(e,t){const n=Math.cos(t),i=Math.sin(t),r=1-n,a=e.x,o=e.y,l=e.z,c=r*a,h=r*o;return this.set(c*a+n,c*o-i*l,c*l+i*o,0,c*o+i*l,h*o+n,h*l-i*a,0,c*l-i*o,h*l+i*a,r*l*l+n,0,0,0,0,1),this}makeScale(e,t,n){return this.set(e,0,0,0,0,t,0,0,0,0,n,0,0,0,0,1),this}makeShear(e,t,n,i,r,a){return this.set(1,n,r,0,e,1,a,0,t,i,1,0,0,0,0,1),this}compose(e,t,n){const i=this.elements,r=t._x,a=t._y,o=t._z,l=t._w,c=r+r,h=a+a,d=o+o,u=r*c,f=r*h,g=r*d,x=a*h,p=a*d,m=o*d,b=l*c,_=l*h,S=l*d,I=n.x,A=n.y,R=n.z;return i[0]=(1-(x+m))*I,i[1]=(f+S)*I,i[2]=(g-_)*I,i[3]=0,i[4]=(f-S)*A,i[5]=(1-(u+m))*A,i[6]=(p+b)*A,i[7]=0,i[8]=(g+_)*R,i[9]=(p-b)*R,i[10]=(1-(u+x))*R,i[11]=0,i[12]=e.x,i[13]=e.y,i[14]=e.z,i[15]=1,this}decompose(e,t,n){const i=this.elements;let r=Sr.set(i[0],i[1],i[2]).length();const a=Sr.set(i[4],i[5],i[6]).length(),o=Sr.set(i[8],i[9],i[10]).length();this.determinant()<0&&(r=-r),e.x=i[12],e.y=i[13],e.z=i[14],di.copy(this);const c=1/r,h=1/a,d=1/o;return di.elements[0]*=c,di.elements[1]*=c,di.elements[2]*=c,di.elements[4]*=h,di.elements[5]*=h,di.elements[6]*=h,di.elements[8]*=d,di.elements[9]*=d,di.elements[10]*=d,t.setFromRotationMatrix(di),n.x=r,n.y=a,n.z=o,this}makePerspective(e,t,n,i,r,a,o=Ji){const l=this.elements,c=2*r/(t-e),h=2*r/(n-i),d=(t+e)/(t-e),u=(n+i)/(n-i);let f,g;if(o===Ji)f=-(a+r)/(a-r),g=-2*a*r/(a-r);else if(o===cl)f=-a/(a-r),g=-a*r/(a-r);else throw new Error("THREE.Matrix4.makePerspective(): Invalid coordinate system: "+o);return l[0]=c,l[4]=0,l[8]=d,l[12]=0,l[1]=0,l[5]=h,l[9]=u,l[13]=0,l[2]=0,l[6]=0,l[10]=f,l[14]=g,l[3]=0,l[7]=0,l[11]=-1,l[15]=0,this}makeOrthographic(e,t,n,i,r,a,o=Ji){const l=this.elements,c=1/(t-e),h=1/(n-i),d=1/(a-r),u=(t+e)*c,f=(n+i)*h;let g,x;if(o===Ji)g=(a+r)*d,x=-2*d;else if(o===cl)g=r*d,x=-1*d;else throw new Error("THREE.Matrix4.makeOrthographic(): Invalid coordinate system: "+o);return l[0]=2*c,l[4]=0,l[8]=0,l[12]=-u,l[1]=0,l[5]=2*h,l[9]=0,l[13]=-f,l[2]=0,l[6]=0,l[10]=x,l[14]=-g,l[3]=0,l[7]=0,l[11]=0,l[15]=1,this}equals(e){const t=this.elements,n=e.elements;for(let i=0;i<16;i++)if(t[i]!==n[i])return!1;return!0}fromArray(e,t=0){for(let n=0;n<16;n++)this.elements[n]=e[n+t];return this}toArray(e=[],t=0){const n=this.elements;return e[t]=n[0],e[t+1]=n[1],e[t+2]=n[2],e[t+3]=n[3],e[t+4]=n[4],e[t+5]=n[5],e[t+6]=n[6],e[t+7]=n[7],e[t+8]=n[8],e[t+9]=n[9],e[t+10]=n[10],e[t+11]=n[11],e[t+12]=n[12],e[t+13]=n[13],e[t+14]=n[14],e[t+15]=n[15],e}}const Sr=new V,di=new Bt,px=new V(0,0,0),mx=new V(1,1,1),ps=new V,bo=new V,Wn=new V,Yd=new Bt,jd=new tr;class Ni{constructor(e=0,t=0,n=0,i=Ni.DEFAULT_ORDER){this.isEuler=!0,this._x=e,this._y=t,this._z=n,this._order=i}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get order(){return this._order}set order(e){this._order=e,this._onChangeCallback()}set(e,t,n,i=this._order){return this._x=e,this._y=t,this._z=n,this._order=i,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._order)}copy(e){return this._x=e._x,this._y=e._y,this._z=e._z,this._order=e._order,this._onChangeCallback(),this}setFromRotationMatrix(e,t=this._order,n=!0){const i=e.elements,r=i[0],a=i[4],o=i[8],l=i[1],c=i[5],h=i[9],d=i[2],u=i[6],f=i[10];switch(t){case"XYZ":this._y=Math.asin(Tn(o,-1,1)),Math.abs(o)<.9999999?(this._x=Math.atan2(-h,f),this._z=Math.atan2(-a,r)):(this._x=Math.atan2(u,c),this._z=0);break;case"YXZ":this._x=Math.asin(-Tn(h,-1,1)),Math.abs(h)<.9999999?(this._y=Math.atan2(o,f),this._z=Math.atan2(l,c)):(this._y=Math.atan2(-d,r),this._z=0);break;case"ZXY":this._x=Math.asin(Tn(u,-1,1)),Math.abs(u)<.9999999?(this._y=Math.atan2(-d,f),this._z=Math.atan2(-a,c)):(this._y=0,this._z=Math.atan2(l,r));break;case"ZYX":this._y=Math.asin(-Tn(d,-1,1)),Math.abs(d)<.9999999?(this._x=Math.atan2(u,f),this._z=Math.atan2(l,r)):(this._x=0,this._z=Math.atan2(-a,c));break;case"YZX":this._z=Math.asin(Tn(l,-1,1)),Math.abs(l)<.9999999?(this._x=Math.atan2(-h,c),this._y=Math.atan2(-d,r)):(this._x=0,this._y=Math.atan2(o,f));break;case"XZY":this._z=Math.asin(-Tn(a,-1,1)),Math.abs(a)<.9999999?(this._x=Math.atan2(u,c),this._y=Math.atan2(o,r)):(this._x=Math.atan2(-h,f),this._y=0);break;default:console.warn("THREE.Euler: .setFromRotationMatrix() encountered an unknown order: "+t)}return this._order=t,n===!0&&this._onChangeCallback(),this}setFromQuaternion(e,t,n){return Yd.makeRotationFromQuaternion(e),this.setFromRotationMatrix(Yd,t,n)}setFromVector3(e,t=this._order){return this.set(e.x,e.y,e.z,t)}reorder(e){return jd.setFromEuler(this),this.setFromQuaternion(jd,e)}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._order===this._order}fromArray(e){return this._x=e[0],this._y=e[1],this._z=e[2],e[3]!==void 0&&(this._order=e[3]),this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._order,e}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._order}}Ni.DEFAULT_ORDER="XYZ";class Wh{constructor(){this.mask=1}set(e){this.mask=(1<<e|0)>>>0}enable(e){this.mask|=1<<e|0}enableAll(){this.mask=-1}toggle(e){this.mask^=1<<e|0}disable(e){this.mask&=~(1<<e|0)}disableAll(){this.mask=0}test(e){return(this.mask&e.mask)!==0}isEnabled(e){return(this.mask&(1<<e|0))!==0}}let gx=0;const Kd=new V,Mr=new tr,$i=new Bt,So=new V,Ra=new V,xx=new V,vx=new tr,Jd=new V(1,0,0),Zd=new V(0,1,0),Qd=new V(0,0,1),eu={type:"added"},_x={type:"removed"},wr={type:"childadded",child:null},oc={type:"childremoved",child:null};class tn extends da{constructor(){super(),this.isObject3D=!0,Object.defineProperty(this,"id",{value:gx++}),this.uuid=Qi(),this.name="",this.type="Object3D",this.parent=null,this.children=[],this.up=tn.DEFAULT_UP.clone();const e=new V,t=new Ni,n=new tr,i=new V(1,1,1);function r(){n.setFromEuler(t,!1)}function a(){t.setFromQuaternion(n,void 0,!1)}t._onChange(r),n._onChange(a),Object.defineProperties(this,{position:{configurable:!0,enumerable:!0,value:e},rotation:{configurable:!0,enumerable:!0,value:t},quaternion:{configurable:!0,enumerable:!0,value:n},scale:{configurable:!0,enumerable:!0,value:i},modelViewMatrix:{value:new Bt},normalMatrix:{value:new at}}),this.matrix=new Bt,this.matrixWorld=new Bt,this.matrixAutoUpdate=tn.DEFAULT_MATRIX_AUTO_UPDATE,this.matrixWorldAutoUpdate=tn.DEFAULT_MATRIX_WORLD_AUTO_UPDATE,this.matrixWorldNeedsUpdate=!1,this.layers=new Wh,this.visible=!0,this.castShadow=!1,this.receiveShadow=!1,this.frustumCulled=!0,this.renderOrder=0,this.animations=[],this.userData={}}onBeforeShadow(){}onAfterShadow(){}onBeforeRender(){}onAfterRender(){}applyMatrix4(e){this.matrixAutoUpdate&&this.updateMatrix(),this.matrix.premultiply(e),this.matrix.decompose(this.position,this.quaternion,this.scale)}applyQuaternion(e){return this.quaternion.premultiply(e),this}setRotationFromAxisAngle(e,t){this.quaternion.setFromAxisAngle(e,t)}setRotationFromEuler(e){this.quaternion.setFromEuler(e,!0)}setRotationFromMatrix(e){this.quaternion.setFromRotationMatrix(e)}setRotationFromQuaternion(e){this.quaternion.copy(e)}rotateOnAxis(e,t){return Mr.setFromAxisAngle(e,t),this.quaternion.multiply(Mr),this}rotateOnWorldAxis(e,t){return Mr.setFromAxisAngle(e,t),this.quaternion.premultiply(Mr),this}rotateX(e){return this.rotateOnAxis(Jd,e)}rotateY(e){return this.rotateOnAxis(Zd,e)}rotateZ(e){return this.rotateOnAxis(Qd,e)}translateOnAxis(e,t){return Kd.copy(e).applyQuaternion(this.quaternion),this.position.add(Kd.multiplyScalar(t)),this}translateX(e){return this.translateOnAxis(Jd,e)}translateY(e){return this.translateOnAxis(Zd,e)}translateZ(e){return this.translateOnAxis(Qd,e)}localToWorld(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(this.matrixWorld)}worldToLocal(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4($i.copy(this.matrixWorld).invert())}lookAt(e,t,n){e.isVector3?So.copy(e):So.set(e,t,n);const i=this.parent;this.updateWorldMatrix(!0,!1),Ra.setFromMatrixPosition(this.matrixWorld),this.isCamera||this.isLight?$i.lookAt(Ra,So,this.up):$i.lookAt(So,Ra,this.up),this.quaternion.setFromRotationMatrix($i),i&&($i.extractRotation(i.matrixWorld),Mr.setFromRotationMatrix($i),this.quaternion.premultiply(Mr.invert()))}add(e){if(arguments.length>1){for(let t=0;t<arguments.length;t++)this.add(arguments[t]);return this}return e===this?(console.error("THREE.Object3D.add: object can't be added as a child of itself.",e),this):(e&&e.isObject3D?(e.removeFromParent(),e.parent=this,this.children.push(e),e.dispatchEvent(eu),wr.child=e,this.dispatchEvent(wr),wr.child=null):console.error("THREE.Object3D.add: object not an instance of THREE.Object3D.",e),this)}remove(e){if(arguments.length>1){for(let n=0;n<arguments.length;n++)this.remove(arguments[n]);return this}const t=this.children.indexOf(e);return t!==-1&&(e.parent=null,this.children.splice(t,1),e.dispatchEvent(_x),oc.child=e,this.dispatchEvent(oc),oc.child=null),this}removeFromParent(){const e=this.parent;return e!==null&&e.remove(this),this}clear(){return this.remove(...this.children)}attach(e){return this.updateWorldMatrix(!0,!1),$i.copy(this.matrixWorld).invert(),e.parent!==null&&(e.parent.updateWorldMatrix(!0,!1),$i.multiply(e.parent.matrixWorld)),e.applyMatrix4($i),e.removeFromParent(),e.parent=this,this.children.push(e),e.updateWorldMatrix(!1,!0),e.dispatchEvent(eu),wr.child=e,this.dispatchEvent(wr),wr.child=null,this}getObjectById(e){return this.getObjectByProperty("id",e)}getObjectByName(e){return this.getObjectByProperty("name",e)}getObjectByProperty(e,t){if(this[e]===t)return this;for(let n=0,i=this.children.length;n<i;n++){const a=this.children[n].getObjectByProperty(e,t);if(a!==void 0)return a}}getObjectsByProperty(e,t,n=[]){this[e]===t&&n.push(this);const i=this.children;for(let r=0,a=i.length;r<a;r++)i[r].getObjectsByProperty(e,t,n);return n}getWorldPosition(e){return this.updateWorldMatrix(!0,!1),e.setFromMatrixPosition(this.matrixWorld)}getWorldQuaternion(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(Ra,e,xx),e}getWorldScale(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(Ra,vx,e),e}getWorldDirection(e){this.updateWorldMatrix(!0,!1);const t=this.matrixWorld.elements;return e.set(t[8],t[9],t[10]).normalize()}raycast(){}traverse(e){e(this);const t=this.children;for(let n=0,i=t.length;n<i;n++)t[n].traverse(e)}traverseVisible(e){if(this.visible===!1)return;e(this);const t=this.children;for(let n=0,i=t.length;n<i;n++)t[n].traverseVisible(e)}traverseAncestors(e){const t=this.parent;t!==null&&(e(t),t.traverseAncestors(e))}updateMatrix(){this.matrix.compose(this.position,this.quaternion,this.scale),this.matrixWorldNeedsUpdate=!0}updateMatrixWorld(e){this.matrixAutoUpdate&&this.updateMatrix(),(this.matrixWorldNeedsUpdate||e)&&(this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),this.matrixWorldNeedsUpdate=!1,e=!0);const t=this.children;for(let n=0,i=t.length;n<i;n++)t[n].updateMatrixWorld(e)}updateWorldMatrix(e,t){const n=this.parent;if(e===!0&&n!==null&&n.updateWorldMatrix(!0,!1),this.matrixAutoUpdate&&this.updateMatrix(),this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),t===!0){const i=this.children;for(let r=0,a=i.length;r<a;r++)i[r].updateWorldMatrix(!1,!0)}}toJSON(e){const t=e===void 0||typeof e=="string",n={};t&&(e={geometries:{},materials:{},textures:{},images:{},shapes:{},skeletons:{},animations:{},nodes:{}},n.metadata={version:4.6,type:"Object",generator:"Object3D.toJSON"});const i={};i.uuid=this.uuid,i.type=this.type,this.name!==""&&(i.name=this.name),this.castShadow===!0&&(i.castShadow=!0),this.receiveShadow===!0&&(i.receiveShadow=!0),this.visible===!1&&(i.visible=!1),this.frustumCulled===!1&&(i.frustumCulled=!1),this.renderOrder!==0&&(i.renderOrder=this.renderOrder),Object.keys(this.userData).length>0&&(i.userData=this.userData),i.layers=this.layers.mask,i.matrix=this.matrix.toArray(),i.up=this.up.toArray(),this.matrixAutoUpdate===!1&&(i.matrixAutoUpdate=!1),this.isInstancedMesh&&(i.type="InstancedMesh",i.count=this.count,i.instanceMatrix=this.instanceMatrix.toJSON(),this.instanceColor!==null&&(i.instanceColor=this.instanceColor.toJSON())),this.isBatchedMesh&&(i.type="BatchedMesh",i.perObjectFrustumCulled=this.perObjectFrustumCulled,i.sortObjects=this.sortObjects,i.drawRanges=this._drawRanges,i.reservedRanges=this._reservedRanges,i.visibility=this._visibility,i.active=this._active,i.bounds=this._bounds.map(o=>({boxInitialized:o.boxInitialized,boxMin:o.box.min.toArray(),boxMax:o.box.max.toArray(),sphereInitialized:o.sphereInitialized,sphereRadius:o.sphere.radius,sphereCenter:o.sphere.center.toArray()})),i.maxInstanceCount=this._maxInstanceCount,i.maxVertexCount=this._maxVertexCount,i.maxIndexCount=this._maxIndexCount,i.geometryInitialized=this._geometryInitialized,i.geometryCount=this._geometryCount,i.matricesTexture=this._matricesTexture.toJSON(e),this._colorsTexture!==null&&(i.colorsTexture=this._colorsTexture.toJSON(e)),this.boundingSphere!==null&&(i.boundingSphere={center:i.boundingSphere.center.toArray(),radius:i.boundingSphere.radius}),this.boundingBox!==null&&(i.boundingBox={min:i.boundingBox.min.toArray(),max:i.boundingBox.max.toArray()}));function r(o,l){return o[l.uuid]===void 0&&(o[l.uuid]=l.toJSON(e)),l.uuid}if(this.isScene)this.background&&(this.background.isColor?i.background=this.background.toJSON():this.background.isTexture&&(i.background=this.background.toJSON(e).uuid)),this.environment&&this.environment.isTexture&&this.environment.isRenderTargetTexture!==!0&&(i.environment=this.environment.toJSON(e).uuid);else if(this.isMesh||this.isLine||this.isPoints){i.geometry=r(e.geometries,this.geometry);const o=this.geometry.parameters;if(o!==void 0&&o.shapes!==void 0){const l=o.shapes;if(Array.isArray(l))for(let c=0,h=l.length;c<h;c++){const d=l[c];r(e.shapes,d)}else r(e.shapes,l)}}if(this.isSkinnedMesh&&(i.bindMode=this.bindMode,i.bindMatrix=this.bindMatrix.toArray(),this.skeleton!==void 0&&(r(e.skeletons,this.skeleton),i.skeleton=this.skeleton.uuid)),this.material!==void 0)if(Array.isArray(this.material)){const o=[];for(let l=0,c=this.material.length;l<c;l++)o.push(r(e.materials,this.material[l]));i.material=o}else i.material=r(e.materials,this.material);if(this.children.length>0){i.children=[];for(let o=0;o<this.children.length;o++)i.children.push(this.children[o].toJSON(e).object)}if(this.animations.length>0){i.animations=[];for(let o=0;o<this.animations.length;o++){const l=this.animations[o];i.animations.push(r(e.animations,l))}}if(t){const o=a(e.geometries),l=a(e.materials),c=a(e.textures),h=a(e.images),d=a(e.shapes),u=a(e.skeletons),f=a(e.animations),g=a(e.nodes);o.length>0&&(n.geometries=o),l.length>0&&(n.materials=l),c.length>0&&(n.textures=c),h.length>0&&(n.images=h),d.length>0&&(n.shapes=d),u.length>0&&(n.skeletons=u),f.length>0&&(n.animations=f),g.length>0&&(n.nodes=g)}return n.object=i,n;function a(o){const l=[];for(const c in o){const h=o[c];delete h.metadata,l.push(h)}return l}}clone(e){return new this.constructor().copy(this,e)}copy(e,t=!0){if(this.name=e.name,this.up.copy(e.up),this.position.copy(e.position),this.rotation.order=e.rotation.order,this.quaternion.copy(e.quaternion),this.scale.copy(e.scale),this.matrix.copy(e.matrix),this.matrixWorld.copy(e.matrixWorld),this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrixWorldAutoUpdate=e.matrixWorldAutoUpdate,this.matrixWorldNeedsUpdate=e.matrixWorldNeedsUpdate,this.layers.mask=e.layers.mask,this.visible=e.visible,this.castShadow=e.castShadow,this.receiveShadow=e.receiveShadow,this.frustumCulled=e.frustumCulled,this.renderOrder=e.renderOrder,this.animations=e.animations.slice(),this.userData=JSON.parse(JSON.stringify(e.userData)),t===!0)for(let n=0;n<e.children.length;n++){const i=e.children[n];this.add(i.clone())}return this}}tn.DEFAULT_UP=new V(0,1,0);tn.DEFAULT_MATRIX_AUTO_UPDATE=!0;tn.DEFAULT_MATRIX_WORLD_AUTO_UPDATE=!0;const ui=new V,qi=new V,lc=new V,Xi=new V,Er=new V,Tr=new V,tu=new V,cc=new V,hc=new V,dc=new V;class ii{constructor(e=new V,t=new V,n=new V){this.a=e,this.b=t,this.c=n}static getNormal(e,t,n,i){i.subVectors(n,t),ui.subVectors(e,t),i.cross(ui);const r=i.lengthSq();return r>0?i.multiplyScalar(1/Math.sqrt(r)):i.set(0,0,0)}static getBarycoord(e,t,n,i,r){ui.subVectors(i,t),qi.subVectors(n,t),lc.subVectors(e,t);const a=ui.dot(ui),o=ui.dot(qi),l=ui.dot(lc),c=qi.dot(qi),h=qi.dot(lc),d=a*c-o*o;if(d===0)return r.set(0,0,0),null;const u=1/d,f=(c*l-o*h)*u,g=(a*h-o*l)*u;return r.set(1-f-g,g,f)}static containsPoint(e,t,n,i){return this.getBarycoord(e,t,n,i,Xi)===null?!1:Xi.x>=0&&Xi.y>=0&&Xi.x+Xi.y<=1}static getInterpolation(e,t,n,i,r,a,o,l){return this.getBarycoord(e,t,n,i,Xi)===null?(l.x=0,l.y=0,"z"in l&&(l.z=0),"w"in l&&(l.w=0),null):(l.setScalar(0),l.addScaledVector(r,Xi.x),l.addScaledVector(a,Xi.y),l.addScaledVector(o,Xi.z),l)}static isFrontFacing(e,t,n,i){return ui.subVectors(n,t),qi.subVectors(e,t),ui.cross(qi).dot(i)<0}set(e,t,n){return this.a.copy(e),this.b.copy(t),this.c.copy(n),this}setFromPointsAndIndices(e,t,n,i){return this.a.copy(e[t]),this.b.copy(e[n]),this.c.copy(e[i]),this}setFromAttributeAndIndices(e,t,n,i){return this.a.fromBufferAttribute(e,t),this.b.fromBufferAttribute(e,n),this.c.fromBufferAttribute(e,i),this}clone(){return new this.constructor().copy(this)}copy(e){return this.a.copy(e.a),this.b.copy(e.b),this.c.copy(e.c),this}getArea(){return ui.subVectors(this.c,this.b),qi.subVectors(this.a,this.b),ui.cross(qi).length()*.5}getMidpoint(e){return e.addVectors(this.a,this.b).add(this.c).multiplyScalar(1/3)}getNormal(e){return ii.getNormal(this.a,this.b,this.c,e)}getPlane(e){return e.setFromCoplanarPoints(this.a,this.b,this.c)}getBarycoord(e,t){return ii.getBarycoord(e,this.a,this.b,this.c,t)}getInterpolation(e,t,n,i,r){return ii.getInterpolation(e,this.a,this.b,this.c,t,n,i,r)}containsPoint(e){return ii.containsPoint(e,this.a,this.b,this.c)}isFrontFacing(e){return ii.isFrontFacing(this.a,this.b,this.c,e)}intersectsBox(e){return e.intersectsTriangle(this)}closestPointToPoint(e,t){const n=this.a,i=this.b,r=this.c;let a,o;Er.subVectors(i,n),Tr.subVectors(r,n),cc.subVectors(e,n);const l=Er.dot(cc),c=Tr.dot(cc);if(l<=0&&c<=0)return t.copy(n);hc.subVectors(e,i);const h=Er.dot(hc),d=Tr.dot(hc);if(h>=0&&d<=h)return t.copy(i);const u=l*d-h*c;if(u<=0&&l>=0&&h<=0)return a=l/(l-h),t.copy(n).addScaledVector(Er,a);dc.subVectors(e,r);const f=Er.dot(dc),g=Tr.dot(dc);if(g>=0&&f<=g)return t.copy(r);const x=f*c-l*g;if(x<=0&&c>=0&&g<=0)return o=c/(c-g),t.copy(n).addScaledVector(Tr,o);const p=h*g-f*d;if(p<=0&&d-h>=0&&f-g>=0)return tu.subVectors(r,i),o=(d-h)/(d-h+(f-g)),t.copy(i).addScaledVector(tu,o);const m=1/(p+x+u);return a=x*m,o=u*m,t.copy(n).addScaledVector(Er,a).addScaledVector(Tr,o)}equals(e){return e.a.equals(this.a)&&e.b.equals(this.b)&&e.c.equals(this.c)}}const up={aliceblue:15792383,antiquewhite:16444375,aqua:65535,aquamarine:8388564,azure:15794175,beige:16119260,bisque:16770244,black:0,blanchedalmond:16772045,blue:255,blueviolet:9055202,brown:10824234,burlywood:14596231,cadetblue:6266528,chartreuse:8388352,chocolate:13789470,coral:16744272,cornflowerblue:6591981,cornsilk:16775388,crimson:14423100,cyan:65535,darkblue:139,darkcyan:35723,darkgoldenrod:12092939,darkgray:11119017,darkgreen:25600,darkgrey:11119017,darkkhaki:12433259,darkmagenta:9109643,darkolivegreen:5597999,darkorange:16747520,darkorchid:10040012,darkred:9109504,darksalmon:15308410,darkseagreen:9419919,darkslateblue:4734347,darkslategray:3100495,darkslategrey:3100495,darkturquoise:52945,darkviolet:9699539,deeppink:16716947,deepskyblue:49151,dimgray:6908265,dimgrey:6908265,dodgerblue:2003199,firebrick:11674146,floralwhite:16775920,forestgreen:2263842,fuchsia:16711935,gainsboro:14474460,ghostwhite:16316671,gold:16766720,goldenrod:14329120,gray:8421504,green:32768,greenyellow:11403055,grey:8421504,honeydew:15794160,hotpink:16738740,indianred:13458524,indigo:4915330,ivory:16777200,khaki:15787660,lavender:15132410,lavenderblush:16773365,lawngreen:8190976,lemonchiffon:16775885,lightblue:11393254,lightcoral:15761536,lightcyan:14745599,lightgoldenrodyellow:16448210,lightgray:13882323,lightgreen:9498256,lightgrey:13882323,lightpink:16758465,lightsalmon:16752762,lightseagreen:2142890,lightskyblue:8900346,lightslategray:7833753,lightslategrey:7833753,lightsteelblue:11584734,lightyellow:16777184,lime:65280,limegreen:3329330,linen:16445670,magenta:16711935,maroon:8388608,mediumaquamarine:6737322,mediumblue:205,mediumorchid:12211667,mediumpurple:9662683,mediumseagreen:3978097,mediumslateblue:8087790,mediumspringgreen:64154,mediumturquoise:4772300,mediumvioletred:13047173,midnightblue:1644912,mintcream:16121850,mistyrose:16770273,moccasin:16770229,navajowhite:16768685,navy:128,oldlace:16643558,olive:8421376,olivedrab:7048739,orange:16753920,orangered:16729344,orchid:14315734,palegoldenrod:15657130,palegreen:10025880,paleturquoise:11529966,palevioletred:14381203,papayawhip:16773077,peachpuff:16767673,peru:13468991,pink:16761035,plum:14524637,powderblue:11591910,purple:8388736,rebeccapurple:6697881,red:16711680,rosybrown:12357519,royalblue:4286945,saddlebrown:9127187,salmon:16416882,sandybrown:16032864,seagreen:3050327,seashell:16774638,sienna:10506797,silver:12632256,skyblue:8900331,slateblue:6970061,slategray:7372944,slategrey:7372944,snow:16775930,springgreen:65407,steelblue:4620980,tan:13808780,teal:32896,thistle:14204888,tomato:16737095,turquoise:4251856,violet:15631086,wheat:16113331,white:16777215,whitesmoke:16119285,yellow:16776960,yellowgreen:10145074},ms={h:0,s:0,l:0},Mo={h:0,s:0,l:0};function uc(s,e,t){return t<0&&(t+=1),t>1&&(t-=1),t<1/6?s+(e-s)*6*t:t<1/2?e:t<2/3?s+(e-s)*6*(2/3-t):s}class nt{constructor(e,t,n){return this.isColor=!0,this.r=1,this.g=1,this.b=1,this.set(e,t,n)}set(e,t,n){if(t===void 0&&n===void 0){const i=e;i&&i.isColor?this.copy(i):typeof i=="number"?this.setHex(i):typeof i=="string"&&this.setStyle(i)}else this.setRGB(e,t,n);return this}setScalar(e){return this.r=e,this.g=e,this.b=e,this}setHex(e,t=Di){return e=Math.floor(e),this.r=(e>>16&255)/255,this.g=(e>>8&255)/255,this.b=(e&255)/255,Mt.toWorkingColorSpace(this,t),this}setRGB(e,t,n,i=Mt.workingColorSpace){return this.r=e,this.g=t,this.b=n,Mt.toWorkingColorSpace(this,i),this}setHSL(e,t,n,i=Mt.workingColorSpace){if(e=Gh(e,1),t=Tn(t,0,1),n=Tn(n,0,1),t===0)this.r=this.g=this.b=n;else{const r=n<=.5?n*(1+t):n+t-n*t,a=2*n-r;this.r=uc(a,r,e+1/3),this.g=uc(a,r,e),this.b=uc(a,r,e-1/3)}return Mt.toWorkingColorSpace(this,i),this}setStyle(e,t=Di){function n(r){r!==void 0&&parseFloat(r)<1&&console.warn("THREE.Color: Alpha component of "+e+" will be ignored.")}let i;if(i=/^(\w+)\(([^\)]*)\)/.exec(e)){let r;const a=i[1],o=i[2];switch(a){case"rgb":case"rgba":if(r=/^\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(o))return n(r[4]),this.setRGB(Math.min(255,parseInt(r[1],10))/255,Math.min(255,parseInt(r[2],10))/255,Math.min(255,parseInt(r[3],10))/255,t);if(r=/^\s*(\d+)\%\s*,\s*(\d+)\%\s*,\s*(\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(o))return n(r[4]),this.setRGB(Math.min(100,parseInt(r[1],10))/100,Math.min(100,parseInt(r[2],10))/100,Math.min(100,parseInt(r[3],10))/100,t);break;case"hsl":case"hsla":if(r=/^\s*(\d*\.?\d+)\s*,\s*(\d*\.?\d+)\%\s*,\s*(\d*\.?\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(o))return n(r[4]),this.setHSL(parseFloat(r[1])/360,parseFloat(r[2])/100,parseFloat(r[3])/100,t);break;default:console.warn("THREE.Color: Unknown color model "+e)}}else if(i=/^\#([A-Fa-f\d]+)$/.exec(e)){const r=i[1],a=r.length;if(a===3)return this.setRGB(parseInt(r.charAt(0),16)/15,parseInt(r.charAt(1),16)/15,parseInt(r.charAt(2),16)/15,t);if(a===6)return this.setHex(parseInt(r,16),t);console.warn("THREE.Color: Invalid hex color "+e)}else if(e&&e.length>0)return this.setColorName(e,t);return this}setColorName(e,t=Di){const n=up[e.toLowerCase()];return n!==void 0?this.setHex(n,t):console.warn("THREE.Color: Unknown color "+e),this}clone(){return new this.constructor(this.r,this.g,this.b)}copy(e){return this.r=e.r,this.g=e.g,this.b=e.b,this}copySRGBToLinear(e){return this.r=Yr(e.r),this.g=Yr(e.g),this.b=Yr(e.b),this}copyLinearToSRGB(e){return this.r=Ql(e.r),this.g=Ql(e.g),this.b=Ql(e.b),this}convertSRGBToLinear(){return this.copySRGBToLinear(this),this}convertLinearToSRGB(){return this.copyLinearToSRGB(this),this}getHex(e=Di){return Mt.fromWorkingColorSpace(En.copy(this),e),Math.round(Tn(En.r*255,0,255))*65536+Math.round(Tn(En.g*255,0,255))*256+Math.round(Tn(En.b*255,0,255))}getHexString(e=Di){return("000000"+this.getHex(e).toString(16)).slice(-6)}getHSL(e,t=Mt.workingColorSpace){Mt.fromWorkingColorSpace(En.copy(this),t);const n=En.r,i=En.g,r=En.b,a=Math.max(n,i,r),o=Math.min(n,i,r);let l,c;const h=(o+a)/2;if(o===a)l=0,c=0;else{const d=a-o;switch(c=h<=.5?d/(a+o):d/(2-a-o),a){case n:l=(i-r)/d+(i<r?6:0);break;case i:l=(r-n)/d+2;break;case r:l=(n-i)/d+4;break}l/=6}return e.h=l,e.s=c,e.l=h,e}getRGB(e,t=Mt.workingColorSpace){return Mt.fromWorkingColorSpace(En.copy(this),t),e.r=En.r,e.g=En.g,e.b=En.b,e}getStyle(e=Di){Mt.fromWorkingColorSpace(En.copy(this),e);const t=En.r,n=En.g,i=En.b;return e!==Di?`color(${e} ${t.toFixed(3)} ${n.toFixed(3)} ${i.toFixed(3)})`:`rgb(${Math.round(t*255)},${Math.round(n*255)},${Math.round(i*255)})`}offsetHSL(e,t,n){return this.getHSL(ms),this.setHSL(ms.h+e,ms.s+t,ms.l+n)}add(e){return this.r+=e.r,this.g+=e.g,this.b+=e.b,this}addColors(e,t){return this.r=e.r+t.r,this.g=e.g+t.g,this.b=e.b+t.b,this}addScalar(e){return this.r+=e,this.g+=e,this.b+=e,this}sub(e){return this.r=Math.max(0,this.r-e.r),this.g=Math.max(0,this.g-e.g),this.b=Math.max(0,this.b-e.b),this}multiply(e){return this.r*=e.r,this.g*=e.g,this.b*=e.b,this}multiplyScalar(e){return this.r*=e,this.g*=e,this.b*=e,this}lerp(e,t){return this.r+=(e.r-this.r)*t,this.g+=(e.g-this.g)*t,this.b+=(e.b-this.b)*t,this}lerpColors(e,t,n){return this.r=e.r+(t.r-e.r)*n,this.g=e.g+(t.g-e.g)*n,this.b=e.b+(t.b-e.b)*n,this}lerpHSL(e,t){this.getHSL(ms),e.getHSL(Mo);const n=Wa(ms.h,Mo.h,t),i=Wa(ms.s,Mo.s,t),r=Wa(ms.l,Mo.l,t);return this.setHSL(n,i,r),this}setFromVector3(e){return this.r=e.x,this.g=e.y,this.b=e.z,this}applyMatrix3(e){const t=this.r,n=this.g,i=this.b,r=e.elements;return this.r=r[0]*t+r[3]*n+r[6]*i,this.g=r[1]*t+r[4]*n+r[7]*i,this.b=r[2]*t+r[5]*n+r[8]*i,this}equals(e){return e.r===this.r&&e.g===this.g&&e.b===this.b}fromArray(e,t=0){return this.r=e[t],this.g=e[t+1],this.b=e[t+2],this}toArray(e=[],t=0){return e[t]=this.r,e[t+1]=this.g,e[t+2]=this.b,e}fromBufferAttribute(e,t){return this.r=e.getX(t),this.g=e.getY(t),this.b=e.getZ(t),this}toJSON(){return this.getHex()}*[Symbol.iterator](){yield this.r,yield this.g,yield this.b}}const En=new nt;nt.NAMES=up;let yx=0;class Ls extends da{constructor(){super(),this.isMaterial=!0,Object.defineProperty(this,"id",{value:yx++}),this.uuid=Qi(),this.name="",this.type="Material",this.blending=Wr,this.side=Es,this.vertexColors=!1,this.opacity=1,this.transparent=!1,this.alphaHash=!1,this.blendSrc=zc,this.blendDst=Hc,this.blendEquation=qs,this.blendSrcAlpha=null,this.blendDstAlpha=null,this.blendEquationAlpha=null,this.blendColor=new nt(0,0,0),this.blendAlpha=0,this.depthFunc=rl,this.depthTest=!0,this.depthWrite=!0,this.stencilWriteMask=255,this.stencilFunc=Hd,this.stencilRef=0,this.stencilFuncMask=255,this.stencilFail=xr,this.stencilZFail=xr,this.stencilZPass=xr,this.stencilWrite=!1,this.clippingPlanes=null,this.clipIntersection=!1,this.clipShadows=!1,this.shadowSide=null,this.colorWrite=!0,this.precision=null,this.polygonOffset=!1,this.polygonOffsetFactor=0,this.polygonOffsetUnits=0,this.dithering=!1,this.alphaToCoverage=!1,this.premultipliedAlpha=!1,this.forceSinglePass=!1,this.visible=!0,this.toneMapped=!0,this.userData={},this.version=0,this._alphaTest=0}get alphaTest(){return this._alphaTest}set alphaTest(e){this._alphaTest>0!=e>0&&this.version++,this._alphaTest=e}onBeforeRender(){}onBeforeCompile(){}customProgramCacheKey(){return this.onBeforeCompile.toString()}setValues(e){if(e!==void 0)for(const t in e){const n=e[t];if(n===void 0){console.warn(`THREE.Material: parameter '${t}' has value of undefined.`);continue}const i=this[t];if(i===void 0){console.warn(`THREE.Material: '${t}' is not a property of THREE.${this.type}.`);continue}i&&i.isColor?i.set(n):i&&i.isVector3&&n&&n.isVector3?i.copy(n):this[t]=n}}toJSON(e){const t=e===void 0||typeof e=="string";t&&(e={textures:{},images:{}});const n={metadata:{version:4.6,type:"Material",generator:"Material.toJSON"}};n.uuid=this.uuid,n.type=this.type,this.name!==""&&(n.name=this.name),this.color&&this.color.isColor&&(n.color=this.color.getHex()),this.roughness!==void 0&&(n.roughness=this.roughness),this.metalness!==void 0&&(n.metalness=this.metalness),this.sheen!==void 0&&(n.sheen=this.sheen),this.sheenColor&&this.sheenColor.isColor&&(n.sheenColor=this.sheenColor.getHex()),this.sheenRoughness!==void 0&&(n.sheenRoughness=this.sheenRoughness),this.emissive&&this.emissive.isColor&&(n.emissive=this.emissive.getHex()),this.emissiveIntensity!==void 0&&this.emissiveIntensity!==1&&(n.emissiveIntensity=this.emissiveIntensity),this.specular&&this.specular.isColor&&(n.specular=this.specular.getHex()),this.specularIntensity!==void 0&&(n.specularIntensity=this.specularIntensity),this.specularColor&&this.specularColor.isColor&&(n.specularColor=this.specularColor.getHex()),this.shininess!==void 0&&(n.shininess=this.shininess),this.clearcoat!==void 0&&(n.clearcoat=this.clearcoat),this.clearcoatRoughness!==void 0&&(n.clearcoatRoughness=this.clearcoatRoughness),this.clearcoatMap&&this.clearcoatMap.isTexture&&(n.clearcoatMap=this.clearcoatMap.toJSON(e).uuid),this.clearcoatRoughnessMap&&this.clearcoatRoughnessMap.isTexture&&(n.clearcoatRoughnessMap=this.clearcoatRoughnessMap.toJSON(e).uuid),this.clearcoatNormalMap&&this.clearcoatNormalMap.isTexture&&(n.clearcoatNormalMap=this.clearcoatNormalMap.toJSON(e).uuid,n.clearcoatNormalScale=this.clearcoatNormalScale.toArray()),this.dispersion!==void 0&&(n.dispersion=this.dispersion),this.iridescence!==void 0&&(n.iridescence=this.iridescence),this.iridescenceIOR!==void 0&&(n.iridescenceIOR=this.iridescenceIOR),this.iridescenceThicknessRange!==void 0&&(n.iridescenceThicknessRange=this.iridescenceThicknessRange),this.iridescenceMap&&this.iridescenceMap.isTexture&&(n.iridescenceMap=this.iridescenceMap.toJSON(e).uuid),this.iridescenceThicknessMap&&this.iridescenceThicknessMap.isTexture&&(n.iridescenceThicknessMap=this.iridescenceThicknessMap.toJSON(e).uuid),this.anisotropy!==void 0&&(n.anisotropy=this.anisotropy),this.anisotropyRotation!==void 0&&(n.anisotropyRotation=this.anisotropyRotation),this.anisotropyMap&&this.anisotropyMap.isTexture&&(n.anisotropyMap=this.anisotropyMap.toJSON(e).uuid),this.map&&this.map.isTexture&&(n.map=this.map.toJSON(e).uuid),this.matcap&&this.matcap.isTexture&&(n.matcap=this.matcap.toJSON(e).uuid),this.alphaMap&&this.alphaMap.isTexture&&(n.alphaMap=this.alphaMap.toJSON(e).uuid),this.lightMap&&this.lightMap.isTexture&&(n.lightMap=this.lightMap.toJSON(e).uuid,n.lightMapIntensity=this.lightMapIntensity),this.aoMap&&this.aoMap.isTexture&&(n.aoMap=this.aoMap.toJSON(e).uuid,n.aoMapIntensity=this.aoMapIntensity),this.bumpMap&&this.bumpMap.isTexture&&(n.bumpMap=this.bumpMap.toJSON(e).uuid,n.bumpScale=this.bumpScale),this.normalMap&&this.normalMap.isTexture&&(n.normalMap=this.normalMap.toJSON(e).uuid,n.normalMapType=this.normalMapType,n.normalScale=this.normalScale.toArray()),this.displacementMap&&this.displacementMap.isTexture&&(n.displacementMap=this.displacementMap.toJSON(e).uuid,n.displacementScale=this.displacementScale,n.displacementBias=this.displacementBias),this.roughnessMap&&this.roughnessMap.isTexture&&(n.roughnessMap=this.roughnessMap.toJSON(e).uuid),this.metalnessMap&&this.metalnessMap.isTexture&&(n.metalnessMap=this.metalnessMap.toJSON(e).uuid),this.emissiveMap&&this.emissiveMap.isTexture&&(n.emissiveMap=this.emissiveMap.toJSON(e).uuid),this.specularMap&&this.specularMap.isTexture&&(n.specularMap=this.specularMap.toJSON(e).uuid),this.specularIntensityMap&&this.specularIntensityMap.isTexture&&(n.specularIntensityMap=this.specularIntensityMap.toJSON(e).uuid),this.specularColorMap&&this.specularColorMap.isTexture&&(n.specularColorMap=this.specularColorMap.toJSON(e).uuid),this.envMap&&this.envMap.isTexture&&(n.envMap=this.envMap.toJSON(e).uuid,this.combine!==void 0&&(n.combine=this.combine)),this.envMapRotation!==void 0&&(n.envMapRotation=this.envMapRotation.toArray()),this.envMapIntensity!==void 0&&(n.envMapIntensity=this.envMapIntensity),this.reflectivity!==void 0&&(n.reflectivity=this.reflectivity),this.refractionRatio!==void 0&&(n.refractionRatio=this.refractionRatio),this.gradientMap&&this.gradientMap.isTexture&&(n.gradientMap=this.gradientMap.toJSON(e).uuid),this.transmission!==void 0&&(n.transmission=this.transmission),this.transmissionMap&&this.transmissionMap.isTexture&&(n.transmissionMap=this.transmissionMap.toJSON(e).uuid),this.thickness!==void 0&&(n.thickness=this.thickness),this.thicknessMap&&this.thicknessMap.isTexture&&(n.thicknessMap=this.thicknessMap.toJSON(e).uuid),this.attenuationDistance!==void 0&&this.attenuationDistance!==1/0&&(n.attenuationDistance=this.attenuationDistance),this.attenuationColor!==void 0&&(n.attenuationColor=this.attenuationColor.getHex()),this.size!==void 0&&(n.size=this.size),this.shadowSide!==null&&(n.shadowSide=this.shadowSide),this.sizeAttenuation!==void 0&&(n.sizeAttenuation=this.sizeAttenuation),this.blending!==Wr&&(n.blending=this.blending),this.side!==Es&&(n.side=this.side),this.vertexColors===!0&&(n.vertexColors=!0),this.opacity<1&&(n.opacity=this.opacity),this.transparent===!0&&(n.transparent=!0),this.blendSrc!==zc&&(n.blendSrc=this.blendSrc),this.blendDst!==Hc&&(n.blendDst=this.blendDst),this.blendEquation!==qs&&(n.blendEquation=this.blendEquation),this.blendSrcAlpha!==null&&(n.blendSrcAlpha=this.blendSrcAlpha),this.blendDstAlpha!==null&&(n.blendDstAlpha=this.blendDstAlpha),this.blendEquationAlpha!==null&&(n.blendEquationAlpha=this.blendEquationAlpha),this.blendColor&&this.blendColor.isColor&&(n.blendColor=this.blendColor.getHex()),this.blendAlpha!==0&&(n.blendAlpha=this.blendAlpha),this.depthFunc!==rl&&(n.depthFunc=this.depthFunc),this.depthTest===!1&&(n.depthTest=this.depthTest),this.depthWrite===!1&&(n.depthWrite=this.depthWrite),this.colorWrite===!1&&(n.colorWrite=this.colorWrite),this.stencilWriteMask!==255&&(n.stencilWriteMask=this.stencilWriteMask),this.stencilFunc!==Hd&&(n.stencilFunc=this.stencilFunc),this.stencilRef!==0&&(n.stencilRef=this.stencilRef),this.stencilFuncMask!==255&&(n.stencilFuncMask=this.stencilFuncMask),this.stencilFail!==xr&&(n.stencilFail=this.stencilFail),this.stencilZFail!==xr&&(n.stencilZFail=this.stencilZFail),this.stencilZPass!==xr&&(n.stencilZPass=this.stencilZPass),this.stencilWrite===!0&&(n.stencilWrite=this.stencilWrite),this.rotation!==void 0&&this.rotation!==0&&(n.rotation=this.rotation),this.polygonOffset===!0&&(n.polygonOffset=!0),this.polygonOffsetFactor!==0&&(n.polygonOffsetFactor=this.polygonOffsetFactor),this.polygonOffsetUnits!==0&&(n.polygonOffsetUnits=this.polygonOffsetUnits),this.linewidth!==void 0&&this.linewidth!==1&&(n.linewidth=this.linewidth),this.dashSize!==void 0&&(n.dashSize=this.dashSize),this.gapSize!==void 0&&(n.gapSize=this.gapSize),this.scale!==void 0&&(n.scale=this.scale),this.dithering===!0&&(n.dithering=!0),this.alphaTest>0&&(n.alphaTest=this.alphaTest),this.alphaHash===!0&&(n.alphaHash=!0),this.alphaToCoverage===!0&&(n.alphaToCoverage=!0),this.premultipliedAlpha===!0&&(n.premultipliedAlpha=!0),this.forceSinglePass===!0&&(n.forceSinglePass=!0),this.wireframe===!0&&(n.wireframe=!0),this.wireframeLinewidth>1&&(n.wireframeLinewidth=this.wireframeLinewidth),this.wireframeLinecap!=="round"&&(n.wireframeLinecap=this.wireframeLinecap),this.wireframeLinejoin!=="round"&&(n.wireframeLinejoin=this.wireframeLinejoin),this.flatShading===!0&&(n.flatShading=!0),this.visible===!1&&(n.visible=!1),this.toneMapped===!1&&(n.toneMapped=!1),this.fog===!1&&(n.fog=!1),Object.keys(this.userData).length>0&&(n.userData=this.userData);function i(r){const a=[];for(const o in r){const l=r[o];delete l.metadata,a.push(l)}return a}if(t){const r=i(e.textures),a=i(e.images);r.length>0&&(n.textures=r),a.length>0&&(n.images=a)}return n}clone(){return new this.constructor().copy(this)}copy(e){this.name=e.name,this.blending=e.blending,this.side=e.side,this.vertexColors=e.vertexColors,this.opacity=e.opacity,this.transparent=e.transparent,this.blendSrc=e.blendSrc,this.blendDst=e.blendDst,this.blendEquation=e.blendEquation,this.blendSrcAlpha=e.blendSrcAlpha,this.blendDstAlpha=e.blendDstAlpha,this.blendEquationAlpha=e.blendEquationAlpha,this.blendColor.copy(e.blendColor),this.blendAlpha=e.blendAlpha,this.depthFunc=e.depthFunc,this.depthTest=e.depthTest,this.depthWrite=e.depthWrite,this.stencilWriteMask=e.stencilWriteMask,this.stencilFunc=e.stencilFunc,this.stencilRef=e.stencilRef,this.stencilFuncMask=e.stencilFuncMask,this.stencilFail=e.stencilFail,this.stencilZFail=e.stencilZFail,this.stencilZPass=e.stencilZPass,this.stencilWrite=e.stencilWrite;const t=e.clippingPlanes;let n=null;if(t!==null){const i=t.length;n=new Array(i);for(let r=0;r!==i;++r)n[r]=t[r].clone()}return this.clippingPlanes=n,this.clipIntersection=e.clipIntersection,this.clipShadows=e.clipShadows,this.shadowSide=e.shadowSide,this.colorWrite=e.colorWrite,this.precision=e.precision,this.polygonOffset=e.polygonOffset,this.polygonOffsetFactor=e.polygonOffsetFactor,this.polygonOffsetUnits=e.polygonOffsetUnits,this.dithering=e.dithering,this.alphaTest=e.alphaTest,this.alphaHash=e.alphaHash,this.alphaToCoverage=e.alphaToCoverage,this.premultipliedAlpha=e.premultipliedAlpha,this.forceSinglePass=e.forceSinglePass,this.visible=e.visible,this.toneMapped=e.toneMapped,this.userData=JSON.parse(JSON.stringify(e.userData)),this}dispose(){this.dispatchEvent({type:"dispose"})}set needsUpdate(e){e===!0&&this.version++}onBuild(){console.warn("Material: onBuild() has been removed.")}}class es extends Ls{constructor(e){super(),this.isMeshBasicMaterial=!0,this.type="MeshBasicMaterial",this.color=new nt(16777215),this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.specularMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new Ni,this.combine=Yf,this.reflectivity=1,this.refractionRatio=.98,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.lightMap=e.lightMap,this.lightMapIntensity=e.lightMapIntensity,this.aoMap=e.aoMap,this.aoMapIntensity=e.aoMapIntensity,this.specularMap=e.specularMap,this.alphaMap=e.alphaMap,this.envMap=e.envMap,this.envMapRotation.copy(e.envMapRotation),this.combine=e.combine,this.reflectivity=e.reflectivity,this.refractionRatio=e.refractionRatio,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.wireframeLinecap=e.wireframeLinecap,this.wireframeLinejoin=e.wireframeLinejoin,this.fog=e.fog,this}}const Qt=new V,wo=new Xe;class bi{constructor(e,t,n=!1){if(Array.isArray(e))throw new TypeError("THREE.BufferAttribute: array should be a Typed Array.");this.isBufferAttribute=!0,this.name="",this.array=e,this.itemSize=t,this.count=e!==void 0?e.length/t:0,this.normalized=n,this.usage=vh,this._updateRange={offset:0,count:-1},this.updateRanges=[],this.gpuType=Ki,this.version=0}onUploadCallback(){}set needsUpdate(e){e===!0&&this.version++}get updateRange(){return Xr("THREE.BufferAttribute: updateRange() is deprecated and will be removed in r169. Use addUpdateRange() instead."),this._updateRange}setUsage(e){return this.usage=e,this}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}copy(e){return this.name=e.name,this.array=new e.array.constructor(e.array),this.itemSize=e.itemSize,this.count=e.count,this.normalized=e.normalized,this.usage=e.usage,this.gpuType=e.gpuType,this}copyAt(e,t,n){e*=this.itemSize,n*=t.itemSize;for(let i=0,r=this.itemSize;i<r;i++)this.array[e+i]=t.array[n+i];return this}copyArray(e){return this.array.set(e),this}applyMatrix3(e){if(this.itemSize===2)for(let t=0,n=this.count;t<n;t++)wo.fromBufferAttribute(this,t),wo.applyMatrix3(e),this.setXY(t,wo.x,wo.y);else if(this.itemSize===3)for(let t=0,n=this.count;t<n;t++)Qt.fromBufferAttribute(this,t),Qt.applyMatrix3(e),this.setXYZ(t,Qt.x,Qt.y,Qt.z);return this}applyMatrix4(e){for(let t=0,n=this.count;t<n;t++)Qt.fromBufferAttribute(this,t),Qt.applyMatrix4(e),this.setXYZ(t,Qt.x,Qt.y,Qt.z);return this}applyNormalMatrix(e){for(let t=0,n=this.count;t<n;t++)Qt.fromBufferAttribute(this,t),Qt.applyNormalMatrix(e),this.setXYZ(t,Qt.x,Qt.y,Qt.z);return this}transformDirection(e){for(let t=0,n=this.count;t<n;t++)Qt.fromBufferAttribute(this,t),Qt.transformDirection(e),this.setXYZ(t,Qt.x,Qt.y,Qt.z);return this}set(e,t=0){return this.array.set(e,t),this}getComponent(e,t){let n=this.array[e*this.itemSize+t];return this.normalized&&(n=gi(n,this.array)),n}setComponent(e,t,n){return this.normalized&&(n=Tt(n,this.array)),this.array[e*this.itemSize+t]=n,this}getX(e){let t=this.array[e*this.itemSize];return this.normalized&&(t=gi(t,this.array)),t}setX(e,t){return this.normalized&&(t=Tt(t,this.array)),this.array[e*this.itemSize]=t,this}getY(e){let t=this.array[e*this.itemSize+1];return this.normalized&&(t=gi(t,this.array)),t}setY(e,t){return this.normalized&&(t=Tt(t,this.array)),this.array[e*this.itemSize+1]=t,this}getZ(e){let t=this.array[e*this.itemSize+2];return this.normalized&&(t=gi(t,this.array)),t}setZ(e,t){return this.normalized&&(t=Tt(t,this.array)),this.array[e*this.itemSize+2]=t,this}getW(e){let t=this.array[e*this.itemSize+3];return this.normalized&&(t=gi(t,this.array)),t}setW(e,t){return this.normalized&&(t=Tt(t,this.array)),this.array[e*this.itemSize+3]=t,this}setXY(e,t,n){return e*=this.itemSize,this.normalized&&(t=Tt(t,this.array),n=Tt(n,this.array)),this.array[e+0]=t,this.array[e+1]=n,this}setXYZ(e,t,n,i){return e*=this.itemSize,this.normalized&&(t=Tt(t,this.array),n=Tt(n,this.array),i=Tt(i,this.array)),this.array[e+0]=t,this.array[e+1]=n,this.array[e+2]=i,this}setXYZW(e,t,n,i,r){return e*=this.itemSize,this.normalized&&(t=Tt(t,this.array),n=Tt(n,this.array),i=Tt(i,this.array),r=Tt(r,this.array)),this.array[e+0]=t,this.array[e+1]=n,this.array[e+2]=i,this.array[e+3]=r,this}onUpload(e){return this.onUploadCallback=e,this}clone(){return new this.constructor(this.array,this.itemSize).copy(this)}toJSON(){const e={itemSize:this.itemSize,type:this.array.constructor.name,array:Array.from(this.array),normalized:this.normalized};return this.name!==""&&(e.name=this.name),this.usage!==vh&&(e.usage=this.usage),e}}class fp extends bi{constructor(e,t,n){super(new Uint16Array(e),t,n)}}class pp extends bi{constructor(e,t,n){super(new Uint32Array(e),t,n)}}class It extends bi{constructor(e,t,n){super(new Float32Array(e),t,n)}}let bx=0;const ei=new Bt,fc=new tn,Ar=new V,$n=new to,Pa=new to,pn=new V;class Jt extends da{constructor(){super(),this.isBufferGeometry=!0,Object.defineProperty(this,"id",{value:bx++}),this.uuid=Qi(),this.name="",this.type="BufferGeometry",this.index=null,this.attributes={},this.morphAttributes={},this.morphTargetsRelative=!1,this.groups=[],this.boundingBox=null,this.boundingSphere=null,this.drawRange={start:0,count:1/0},this.userData={}}getIndex(){return this.index}setIndex(e){return Array.isArray(e)?this.index=new(cp(e)?pp:fp)(e,1):this.index=e,this}getAttribute(e){return this.attributes[e]}setAttribute(e,t){return this.attributes[e]=t,this}deleteAttribute(e){return delete this.attributes[e],this}hasAttribute(e){return this.attributes[e]!==void 0}addGroup(e,t,n=0){this.groups.push({start:e,count:t,materialIndex:n})}clearGroups(){this.groups=[]}setDrawRange(e,t){this.drawRange.start=e,this.drawRange.count=t}applyMatrix4(e){const t=this.attributes.position;t!==void 0&&(t.applyMatrix4(e),t.needsUpdate=!0);const n=this.attributes.normal;if(n!==void 0){const r=new at().getNormalMatrix(e);n.applyNormalMatrix(r),n.needsUpdate=!0}const i=this.attributes.tangent;return i!==void 0&&(i.transformDirection(e),i.needsUpdate=!0),this.boundingBox!==null&&this.computeBoundingBox(),this.boundingSphere!==null&&this.computeBoundingSphere(),this}applyQuaternion(e){return ei.makeRotationFromQuaternion(e),this.applyMatrix4(ei),this}rotateX(e){return ei.makeRotationX(e),this.applyMatrix4(ei),this}rotateY(e){return ei.makeRotationY(e),this.applyMatrix4(ei),this}rotateZ(e){return ei.makeRotationZ(e),this.applyMatrix4(ei),this}translate(e,t,n){return ei.makeTranslation(e,t,n),this.applyMatrix4(ei),this}scale(e,t,n){return ei.makeScale(e,t,n),this.applyMatrix4(ei),this}lookAt(e){return fc.lookAt(e),fc.updateMatrix(),this.applyMatrix4(fc.matrix),this}center(){return this.computeBoundingBox(),this.boundingBox.getCenter(Ar).negate(),this.translate(Ar.x,Ar.y,Ar.z),this}setFromPoints(e){const t=[];for(let n=0,i=e.length;n<i;n++){const r=e[n];t.push(r.x,r.y,r.z||0)}return this.setAttribute("position",new It(t,3)),this}computeBoundingBox(){this.boundingBox===null&&(this.boundingBox=new to);const e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingBox(): GLBufferAttribute requires a manual bounding box.",this),this.boundingBox.set(new V(-1/0,-1/0,-1/0),new V(1/0,1/0,1/0));return}if(e!==void 0){if(this.boundingBox.setFromBufferAttribute(e),t)for(let n=0,i=t.length;n<i;n++){const r=t[n];$n.setFromBufferAttribute(r),this.morphTargetsRelative?(pn.addVectors(this.boundingBox.min,$n.min),this.boundingBox.expandByPoint(pn),pn.addVectors(this.boundingBox.max,$n.max),this.boundingBox.expandByPoint(pn)):(this.boundingBox.expandByPoint($n.min),this.boundingBox.expandByPoint($n.max))}}else this.boundingBox.makeEmpty();(isNaN(this.boundingBox.min.x)||isNaN(this.boundingBox.min.y)||isNaN(this.boundingBox.min.z))&&console.error('THREE.BufferGeometry.computeBoundingBox(): Computed min/max have NaN values. The "position" attribute is likely to have NaN values.',this)}computeBoundingSphere(){this.boundingSphere===null&&(this.boundingSphere=new no);const e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingSphere(): GLBufferAttribute requires a manual bounding sphere.",this),this.boundingSphere.set(new V,1/0);return}if(e){const n=this.boundingSphere.center;if($n.setFromBufferAttribute(e),t)for(let r=0,a=t.length;r<a;r++){const o=t[r];Pa.setFromBufferAttribute(o),this.morphTargetsRelative?(pn.addVectors($n.min,Pa.min),$n.expandByPoint(pn),pn.addVectors($n.max,Pa.max),$n.expandByPoint(pn)):($n.expandByPoint(Pa.min),$n.expandByPoint(Pa.max))}$n.getCenter(n);let i=0;for(let r=0,a=e.count;r<a;r++)pn.fromBufferAttribute(e,r),i=Math.max(i,n.distanceToSquared(pn));if(t)for(let r=0,a=t.length;r<a;r++){const o=t[r],l=this.morphTargetsRelative;for(let c=0,h=o.count;c<h;c++)pn.fromBufferAttribute(o,c),l&&(Ar.fromBufferAttribute(e,c),pn.add(Ar)),i=Math.max(i,n.distanceToSquared(pn))}this.boundingSphere.radius=Math.sqrt(i),isNaN(this.boundingSphere.radius)&&console.error('THREE.BufferGeometry.computeBoundingSphere(): Computed radius is NaN. The "position" attribute is likely to have NaN values.',this)}}computeTangents(){const e=this.index,t=this.attributes;if(e===null||t.position===void 0||t.normal===void 0||t.uv===void 0){console.error("THREE.BufferGeometry: .computeTangents() failed. Missing required attributes (index, position, normal or uv)");return}const n=t.position,i=t.normal,r=t.uv;this.hasAttribute("tangent")===!1&&this.setAttribute("tangent",new bi(new Float32Array(4*n.count),4));const a=this.getAttribute("tangent"),o=[],l=[];for(let N=0;N<n.count;N++)o[N]=new V,l[N]=new V;const c=new V,h=new V,d=new V,u=new Xe,f=new Xe,g=new Xe,x=new V,p=new V;function m(N,M,y){c.fromBufferAttribute(n,N),h.fromBufferAttribute(n,M),d.fromBufferAttribute(n,y),u.fromBufferAttribute(r,N),f.fromBufferAttribute(r,M),g.fromBufferAttribute(r,y),h.sub(c),d.sub(c),f.sub(u),g.sub(u);const P=1/(f.x*g.y-g.x*f.y);isFinite(P)&&(x.copy(h).multiplyScalar(g.y).addScaledVector(d,-f.y).multiplyScalar(P),p.copy(d).multiplyScalar(f.x).addScaledVector(h,-g.x).multiplyScalar(P),o[N].add(x),o[M].add(x),o[y].add(x),l[N].add(p),l[M].add(p),l[y].add(p))}let b=this.groups;b.length===0&&(b=[{start:0,count:e.count}]);for(let N=0,M=b.length;N<M;++N){const y=b[N],P=y.start,X=y.count;for(let H=P,J=P+X;H<J;H+=3)m(e.getX(H+0),e.getX(H+1),e.getX(H+2))}const _=new V,S=new V,I=new V,A=new V;function R(N){I.fromBufferAttribute(i,N),A.copy(I);const M=o[N];_.copy(M),_.sub(I.multiplyScalar(I.dot(M))).normalize(),S.crossVectors(A,M);const P=S.dot(l[N])<0?-1:1;a.setXYZW(N,_.x,_.y,_.z,P)}for(let N=0,M=b.length;N<M;++N){const y=b[N],P=y.start,X=y.count;for(let H=P,J=P+X;H<J;H+=3)R(e.getX(H+0)),R(e.getX(H+1)),R(e.getX(H+2))}}computeVertexNormals(){const e=this.index,t=this.getAttribute("position");if(t!==void 0){let n=this.getAttribute("normal");if(n===void 0)n=new bi(new Float32Array(t.count*3),3),this.setAttribute("normal",n);else for(let u=0,f=n.count;u<f;u++)n.setXYZ(u,0,0,0);const i=new V,r=new V,a=new V,o=new V,l=new V,c=new V,h=new V,d=new V;if(e)for(let u=0,f=e.count;u<f;u+=3){const g=e.getX(u+0),x=e.getX(u+1),p=e.getX(u+2);i.fromBufferAttribute(t,g),r.fromBufferAttribute(t,x),a.fromBufferAttribute(t,p),h.subVectors(a,r),d.subVectors(i,r),h.cross(d),o.fromBufferAttribute(n,g),l.fromBufferAttribute(n,x),c.fromBufferAttribute(n,p),o.add(h),l.add(h),c.add(h),n.setXYZ(g,o.x,o.y,o.z),n.setXYZ(x,l.x,l.y,l.z),n.setXYZ(p,c.x,c.y,c.z)}else for(let u=0,f=t.count;u<f;u+=3)i.fromBufferAttribute(t,u+0),r.fromBufferAttribute(t,u+1),a.fromBufferAttribute(t,u+2),h.subVectors(a,r),d.subVectors(i,r),h.cross(d),n.setXYZ(u+0,h.x,h.y,h.z),n.setXYZ(u+1,h.x,h.y,h.z),n.setXYZ(u+2,h.x,h.y,h.z);this.normalizeNormals(),n.needsUpdate=!0}}normalizeNormals(){const e=this.attributes.normal;for(let t=0,n=e.count;t<n;t++)pn.fromBufferAttribute(e,t),pn.normalize(),e.setXYZ(t,pn.x,pn.y,pn.z)}toNonIndexed(){function e(o,l){const c=o.array,h=o.itemSize,d=o.normalized,u=new c.constructor(l.length*h);let f=0,g=0;for(let x=0,p=l.length;x<p;x++){o.isInterleavedBufferAttribute?f=l[x]*o.data.stride+o.offset:f=l[x]*h;for(let m=0;m<h;m++)u[g++]=c[f++]}return new bi(u,h,d)}if(this.index===null)return console.warn("THREE.BufferGeometry.toNonIndexed(): BufferGeometry is already non-indexed."),this;const t=new Jt,n=this.index.array,i=this.attributes;for(const o in i){const l=i[o],c=e(l,n);t.setAttribute(o,c)}const r=this.morphAttributes;for(const o in r){const l=[],c=r[o];for(let h=0,d=c.length;h<d;h++){const u=c[h],f=e(u,n);l.push(f)}t.morphAttributes[o]=l}t.morphTargetsRelative=this.morphTargetsRelative;const a=this.groups;for(let o=0,l=a.length;o<l;o++){const c=a[o];t.addGroup(c.start,c.count,c.materialIndex)}return t}toJSON(){const e={metadata:{version:4.6,type:"BufferGeometry",generator:"BufferGeometry.toJSON"}};if(e.uuid=this.uuid,e.type=this.type,this.name!==""&&(e.name=this.name),Object.keys(this.userData).length>0&&(e.userData=this.userData),this.parameters!==void 0){const l=this.parameters;for(const c in l)l[c]!==void 0&&(e[c]=l[c]);return e}e.data={attributes:{}};const t=this.index;t!==null&&(e.data.index={type:t.array.constructor.name,array:Array.prototype.slice.call(t.array)});const n=this.attributes;for(const l in n){const c=n[l];e.data.attributes[l]=c.toJSON(e.data)}const i={};let r=!1;for(const l in this.morphAttributes){const c=this.morphAttributes[l],h=[];for(let d=0,u=c.length;d<u;d++){const f=c[d];h.push(f.toJSON(e.data))}h.length>0&&(i[l]=h,r=!0)}r&&(e.data.morphAttributes=i,e.data.morphTargetsRelative=this.morphTargetsRelative);const a=this.groups;a.length>0&&(e.data.groups=JSON.parse(JSON.stringify(a)));const o=this.boundingSphere;return o!==null&&(e.data.boundingSphere={center:o.center.toArray(),radius:o.radius}),e}clone(){return new this.constructor().copy(this)}copy(e){this.index=null,this.attributes={},this.morphAttributes={},this.groups=[],this.boundingBox=null,this.boundingSphere=null;const t={};this.name=e.name;const n=e.index;n!==null&&this.setIndex(n.clone(t));const i=e.attributes;for(const c in i){const h=i[c];this.setAttribute(c,h.clone(t))}const r=e.morphAttributes;for(const c in r){const h=[],d=r[c];for(let u=0,f=d.length;u<f;u++)h.push(d[u].clone(t));this.morphAttributes[c]=h}this.morphTargetsRelative=e.morphTargetsRelative;const a=e.groups;for(let c=0,h=a.length;c<h;c++){const d=a[c];this.addGroup(d.start,d.count,d.materialIndex)}const o=e.boundingBox;o!==null&&(this.boundingBox=o.clone());const l=e.boundingSphere;return l!==null&&(this.boundingSphere=l.clone()),this.drawRange.start=e.drawRange.start,this.drawRange.count=e.drawRange.count,this.userData=e.userData,this}dispose(){this.dispatchEvent({type:"dispose"})}}const nu=new Bt,Bs=new io,Eo=new no,iu=new V,Cr=new V,Rr=new V,Pr=new V,pc=new V,To=new V,Ao=new Xe,Co=new Xe,Ro=new Xe,su=new V,ru=new V,au=new V,Po=new V,Lo=new V;class Xt extends tn{constructor(e=new Jt,t=new es){super(),this.isMesh=!0,this.type="Mesh",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),e.morphTargetInfluences!==void 0&&(this.morphTargetInfluences=e.morphTargetInfluences.slice()),e.morphTargetDictionary!==void 0&&(this.morphTargetDictionary=Object.assign({},e.morphTargetDictionary)),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const i=t[n[0]];if(i!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let r=0,a=i.length;r<a;r++){const o=i[r].name||String(r);this.morphTargetInfluences.push(0),this.morphTargetDictionary[o]=r}}}}getVertexPosition(e,t){const n=this.geometry,i=n.attributes.position,r=n.morphAttributes.position,a=n.morphTargetsRelative;t.fromBufferAttribute(i,e);const o=this.morphTargetInfluences;if(r&&o){To.set(0,0,0);for(let l=0,c=r.length;l<c;l++){const h=o[l],d=r[l];h!==0&&(pc.fromBufferAttribute(d,e),a?To.addScaledVector(pc,h):To.addScaledVector(pc.sub(t),h))}t.add(To)}return t}raycast(e,t){const n=this.geometry,i=this.material,r=this.matrixWorld;i!==void 0&&(n.boundingSphere===null&&n.computeBoundingSphere(),Eo.copy(n.boundingSphere),Eo.applyMatrix4(r),Bs.copy(e.ray).recast(e.near),!(Eo.containsPoint(Bs.origin)===!1&&(Bs.intersectSphere(Eo,iu)===null||Bs.origin.distanceToSquared(iu)>(e.far-e.near)**2))&&(nu.copy(r).invert(),Bs.copy(e.ray).applyMatrix4(nu),!(n.boundingBox!==null&&Bs.intersectsBox(n.boundingBox)===!1)&&this._computeIntersections(e,t,Bs)))}_computeIntersections(e,t,n){let i;const r=this.geometry,a=this.material,o=r.index,l=r.attributes.position,c=r.attributes.uv,h=r.attributes.uv1,d=r.attributes.normal,u=r.groups,f=r.drawRange;if(o!==null)if(Array.isArray(a))for(let g=0,x=u.length;g<x;g++){const p=u[g],m=a[p.materialIndex],b=Math.max(p.start,f.start),_=Math.min(o.count,Math.min(p.start+p.count,f.start+f.count));for(let S=b,I=_;S<I;S+=3){const A=o.getX(S),R=o.getX(S+1),N=o.getX(S+2);i=Do(this,m,e,n,c,h,d,A,R,N),i&&(i.faceIndex=Math.floor(S/3),i.face.materialIndex=p.materialIndex,t.push(i))}}else{const g=Math.max(0,f.start),x=Math.min(o.count,f.start+f.count);for(let p=g,m=x;p<m;p+=3){const b=o.getX(p),_=o.getX(p+1),S=o.getX(p+2);i=Do(this,a,e,n,c,h,d,b,_,S),i&&(i.faceIndex=Math.floor(p/3),t.push(i))}}else if(l!==void 0)if(Array.isArray(a))for(let g=0,x=u.length;g<x;g++){const p=u[g],m=a[p.materialIndex],b=Math.max(p.start,f.start),_=Math.min(l.count,Math.min(p.start+p.count,f.start+f.count));for(let S=b,I=_;S<I;S+=3){const A=S,R=S+1,N=S+2;i=Do(this,m,e,n,c,h,d,A,R,N),i&&(i.faceIndex=Math.floor(S/3),i.face.materialIndex=p.materialIndex,t.push(i))}}else{const g=Math.max(0,f.start),x=Math.min(l.count,f.start+f.count);for(let p=g,m=x;p<m;p+=3){const b=p,_=p+1,S=p+2;i=Do(this,a,e,n,c,h,d,b,_,S),i&&(i.faceIndex=Math.floor(p/3),t.push(i))}}}}function Sx(s,e,t,n,i,r,a,o){let l;if(e.side===zn?l=n.intersectTriangle(a,r,i,!0,o):l=n.intersectTriangle(i,r,a,e.side===Es,o),l===null)return null;Lo.copy(o),Lo.applyMatrix4(s.matrixWorld);const c=t.ray.origin.distanceTo(Lo);return c<t.near||c>t.far?null:{distance:c,point:Lo.clone(),object:s}}function Do(s,e,t,n,i,r,a,o,l,c){s.getVertexPosition(o,Cr),s.getVertexPosition(l,Rr),s.getVertexPosition(c,Pr);const h=Sx(s,e,t,n,Cr,Rr,Pr,Po);if(h){i&&(Ao.fromBufferAttribute(i,o),Co.fromBufferAttribute(i,l),Ro.fromBufferAttribute(i,c),h.uv=ii.getInterpolation(Po,Cr,Rr,Pr,Ao,Co,Ro,new Xe)),r&&(Ao.fromBufferAttribute(r,o),Co.fromBufferAttribute(r,l),Ro.fromBufferAttribute(r,c),h.uv1=ii.getInterpolation(Po,Cr,Rr,Pr,Ao,Co,Ro,new Xe)),a&&(su.fromBufferAttribute(a,o),ru.fromBufferAttribute(a,l),au.fromBufferAttribute(a,c),h.normal=ii.getInterpolation(Po,Cr,Rr,Pr,su,ru,au,new V),h.normal.dot(n.direction)>0&&h.normal.multiplyScalar(-1));const d={a:o,b:l,c,normal:new V,materialIndex:0};ii.getNormal(Cr,Rr,Pr,d.normal),h.face=d}return h}class _i extends Jt{constructor(e=1,t=1,n=1,i=1,r=1,a=1){super(),this.type="BoxGeometry",this.parameters={width:e,height:t,depth:n,widthSegments:i,heightSegments:r,depthSegments:a};const o=this;i=Math.floor(i),r=Math.floor(r),a=Math.floor(a);const l=[],c=[],h=[],d=[];let u=0,f=0;g("z","y","x",-1,-1,n,t,e,a,r,0),g("z","y","x",1,-1,n,t,-e,a,r,1),g("x","z","y",1,1,e,n,t,i,a,2),g("x","z","y",1,-1,e,n,-t,i,a,3),g("x","y","z",1,-1,e,t,n,i,r,4),g("x","y","z",-1,-1,e,t,-n,i,r,5),this.setIndex(l),this.setAttribute("position",new It(c,3)),this.setAttribute("normal",new It(h,3)),this.setAttribute("uv",new It(d,2));function g(x,p,m,b,_,S,I,A,R,N,M){const y=S/R,P=I/N,X=S/2,H=I/2,J=A/2,q=R+1,ee=N+1;let j=0,ne=0;const ge=new V;for(let ue=0;ue<ee;ue++){const ye=ue*P-H;for(let Te=0;Te<q;Te++){const be=Te*y-X;ge[x]=be*b,ge[p]=ye*_,ge[m]=J,c.push(ge.x,ge.y,ge.z),ge[x]=0,ge[p]=0,ge[m]=A>0?1:-1,h.push(ge.x,ge.y,ge.z),d.push(Te/R),d.push(1-ue/N),j+=1}}for(let ue=0;ue<N;ue++)for(let ye=0;ye<R;ye++){const Te=u+ye+q*ue,be=u+ye+q*(ue+1),ie=u+(ye+1)+q*(ue+1),he=u+(ye+1)+q*ue;l.push(Te,be,he),l.push(be,ie,he),ne+=6}o.addGroup(f,ne,M),f+=ne,u+=j}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new _i(e.width,e.height,e.depth,e.widthSegments,e.heightSegments,e.depthSegments)}}function na(s){const e={};for(const t in s){e[t]={};for(const n in s[t]){const i=s[t][n];i&&(i.isColor||i.isMatrix3||i.isMatrix4||i.isVector2||i.isVector3||i.isVector4||i.isTexture||i.isQuaternion)?i.isRenderTargetTexture?(console.warn("UniformsUtils: Textures of render targets cannot be cloned via cloneUniforms() or mergeUniforms()."),e[t][n]=null):e[t][n]=i.clone():Array.isArray(i)?e[t][n]=i.slice():e[t][n]=i}}return e}function Un(s){const e={};for(let t=0;t<s.length;t++){const n=na(s[t]);for(const i in n)e[i]=n[i]}return e}function Mx(s){const e=[];for(let t=0;t<s.length;t++)e.push(s[t].clone());return e}function mp(s){const e=s.getRenderTarget();return e===null?s.outputColorSpace:e.isXRRenderTarget===!0?e.texture.colorSpace:Mt.workingColorSpace}const wx={clone:na,merge:Un};var Ex=`void main() {
	gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
}`,Tx=`void main() {
	gl_FragColor = vec4( 1.0, 0.0, 0.0, 1.0 );
}`;class Ts extends Ls{constructor(e){super(),this.isShaderMaterial=!0,this.type="ShaderMaterial",this.defines={},this.uniforms={},this.uniformsGroups=[],this.vertexShader=Ex,this.fragmentShader=Tx,this.linewidth=1,this.wireframe=!1,this.wireframeLinewidth=1,this.fog=!1,this.lights=!1,this.clipping=!1,this.forceSinglePass=!0,this.extensions={clipCullDistance:!1,multiDraw:!1},this.defaultAttributeValues={color:[1,1,1],uv:[0,0],uv1:[0,0]},this.index0AttributeName=void 0,this.uniformsNeedUpdate=!1,this.glslVersion=null,e!==void 0&&this.setValues(e)}copy(e){return super.copy(e),this.fragmentShader=e.fragmentShader,this.vertexShader=e.vertexShader,this.uniforms=na(e.uniforms),this.uniformsGroups=Mx(e.uniformsGroups),this.defines=Object.assign({},e.defines),this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.fog=e.fog,this.lights=e.lights,this.clipping=e.clipping,this.extensions=Object.assign({},e.extensions),this.glslVersion=e.glslVersion,this}toJSON(e){const t=super.toJSON(e);t.glslVersion=this.glslVersion,t.uniforms={};for(const i in this.uniforms){const a=this.uniforms[i].value;a&&a.isTexture?t.uniforms[i]={type:"t",value:a.toJSON(e).uuid}:a&&a.isColor?t.uniforms[i]={type:"c",value:a.getHex()}:a&&a.isVector2?t.uniforms[i]={type:"v2",value:a.toArray()}:a&&a.isVector3?t.uniforms[i]={type:"v3",value:a.toArray()}:a&&a.isVector4?t.uniforms[i]={type:"v4",value:a.toArray()}:a&&a.isMatrix3?t.uniforms[i]={type:"m3",value:a.toArray()}:a&&a.isMatrix4?t.uniforms[i]={type:"m4",value:a.toArray()}:t.uniforms[i]={value:a}}Object.keys(this.defines).length>0&&(t.defines=this.defines),t.vertexShader=this.vertexShader,t.fragmentShader=this.fragmentShader,t.lights=this.lights,t.clipping=this.clipping;const n={};for(const i in this.extensions)this.extensions[i]===!0&&(n[i]=!0);return Object.keys(n).length>0&&(t.extensions=n),t}}class gp extends tn{constructor(){super(),this.isCamera=!0,this.type="Camera",this.matrixWorldInverse=new Bt,this.projectionMatrix=new Bt,this.projectionMatrixInverse=new Bt,this.coordinateSystem=Ji}copy(e,t){return super.copy(e,t),this.matrixWorldInverse.copy(e.matrixWorldInverse),this.projectionMatrix.copy(e.projectionMatrix),this.projectionMatrixInverse.copy(e.projectionMatrixInverse),this.coordinateSystem=e.coordinateSystem,this}getWorldDirection(e){return super.getWorldDirection(e).negate()}updateMatrixWorld(e){super.updateMatrixWorld(e),this.matrixWorldInverse.copy(this.matrixWorld).invert()}updateWorldMatrix(e,t){super.updateWorldMatrix(e,t),this.matrixWorldInverse.copy(this.matrixWorld).invert()}clone(){return new this.constructor().copy(this)}}const gs=new V,ou=new Xe,lu=new Xe;class An extends gp{constructor(e=50,t=1,n=.1,i=2e3){super(),this.isPerspectiveCamera=!0,this.type="PerspectiveCamera",this.fov=e,this.zoom=1,this.near=n,this.far=i,this.focus=10,this.aspect=t,this.view=null,this.filmGauge=35,this.filmOffset=0,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.fov=e.fov,this.zoom=e.zoom,this.near=e.near,this.far=e.far,this.focus=e.focus,this.aspect=e.aspect,this.view=e.view===null?null:Object.assign({},e.view),this.filmGauge=e.filmGauge,this.filmOffset=e.filmOffset,this}setFocalLength(e){const t=.5*this.getFilmHeight()/e;this.fov=Ka*2*Math.atan(t),this.updateProjectionMatrix()}getFocalLength(){const e=Math.tan(qr*.5*this.fov);return .5*this.getFilmHeight()/e}getEffectiveFOV(){return Ka*2*Math.atan(Math.tan(qr*.5*this.fov)/this.zoom)}getFilmWidth(){return this.filmGauge*Math.min(this.aspect,1)}getFilmHeight(){return this.filmGauge/Math.max(this.aspect,1)}getViewBounds(e,t,n){gs.set(-1,-1,.5).applyMatrix4(this.projectionMatrixInverse),t.set(gs.x,gs.y).multiplyScalar(-e/gs.z),gs.set(1,1,.5).applyMatrix4(this.projectionMatrixInverse),n.set(gs.x,gs.y).multiplyScalar(-e/gs.z)}getViewSize(e,t){return this.getViewBounds(e,ou,lu),t.subVectors(lu,ou)}setViewOffset(e,t,n,i,r,a){this.aspect=e/t,this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=n,this.view.offsetY=i,this.view.width=r,this.view.height=a,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const e=this.near;let t=e*Math.tan(qr*.5*this.fov)/this.zoom,n=2*t,i=this.aspect*n,r=-.5*i;const a=this.view;if(this.view!==null&&this.view.enabled){const l=a.fullWidth,c=a.fullHeight;r+=a.offsetX*i/l,t-=a.offsetY*n/c,i*=a.width/l,n*=a.height/c}const o=this.filmOffset;o!==0&&(r+=e*o/this.getFilmWidth()),this.projectionMatrix.makePerspective(r,r+i,t,t-n,e,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){const t=super.toJSON(e);return t.object.fov=this.fov,t.object.zoom=this.zoom,t.object.near=this.near,t.object.far=this.far,t.object.focus=this.focus,t.object.aspect=this.aspect,this.view!==null&&(t.object.view=Object.assign({},this.view)),t.object.filmGauge=this.filmGauge,t.object.filmOffset=this.filmOffset,t}}const Lr=-90,Dr=1;class Ax extends tn{constructor(e,t,n){super(),this.type="CubeCamera",this.renderTarget=n,this.coordinateSystem=null,this.activeMipmapLevel=0;const i=new An(Lr,Dr,e,t);i.layers=this.layers,this.add(i);const r=new An(Lr,Dr,e,t);r.layers=this.layers,this.add(r);const a=new An(Lr,Dr,e,t);a.layers=this.layers,this.add(a);const o=new An(Lr,Dr,e,t);o.layers=this.layers,this.add(o);const l=new An(Lr,Dr,e,t);l.layers=this.layers,this.add(l);const c=new An(Lr,Dr,e,t);c.layers=this.layers,this.add(c)}updateCoordinateSystem(){const e=this.coordinateSystem,t=this.children.concat(),[n,i,r,a,o,l]=t;for(const c of t)this.remove(c);if(e===Ji)n.up.set(0,1,0),n.lookAt(1,0,0),i.up.set(0,1,0),i.lookAt(-1,0,0),r.up.set(0,0,-1),r.lookAt(0,1,0),a.up.set(0,0,1),a.lookAt(0,-1,0),o.up.set(0,1,0),o.lookAt(0,0,1),l.up.set(0,1,0),l.lookAt(0,0,-1);else if(e===cl)n.up.set(0,-1,0),n.lookAt(-1,0,0),i.up.set(0,-1,0),i.lookAt(1,0,0),r.up.set(0,0,1),r.lookAt(0,1,0),a.up.set(0,0,-1),a.lookAt(0,-1,0),o.up.set(0,-1,0),o.lookAt(0,0,1),l.up.set(0,-1,0),l.lookAt(0,0,-1);else throw new Error("THREE.CubeCamera.updateCoordinateSystem(): Invalid coordinate system: "+e);for(const c of t)this.add(c),c.updateMatrixWorld()}update(e,t){this.parent===null&&this.updateMatrixWorld();const{renderTarget:n,activeMipmapLevel:i}=this;this.coordinateSystem!==e.coordinateSystem&&(this.coordinateSystem=e.coordinateSystem,this.updateCoordinateSystem());const[r,a,o,l,c,h]=this.children,d=e.getRenderTarget(),u=e.getActiveCubeFace(),f=e.getActiveMipmapLevel(),g=e.xr.enabled;e.xr.enabled=!1;const x=n.texture.generateMipmaps;n.texture.generateMipmaps=!1,e.setRenderTarget(n,0,i),e.render(t,r),e.setRenderTarget(n,1,i),e.render(t,a),e.setRenderTarget(n,2,i),e.render(t,o),e.setRenderTarget(n,3,i),e.render(t,l),e.setRenderTarget(n,4,i),e.render(t,c),n.texture.generateMipmaps=x,e.setRenderTarget(n,5,i),e.render(t,h),e.setRenderTarget(d,u,f),e.xr.enabled=g,n.texture.needsPMREMUpdate=!0}}class xp extends On{constructor(e,t,n,i,r,a,o,l,c,h){e=e!==void 0?e:[],t=t!==void 0?t:Zr,super(e,t,n,i,r,a,o,l,c,h),this.isCubeTexture=!0,this.flipY=!1}get images(){return this.image}set images(e){this.image=e}}class Cx extends er{constructor(e=1,t={}){super(e,e,t),this.isWebGLCubeRenderTarget=!0;const n={width:e,height:e,depth:1},i=[n,n,n,n,n,n];this.texture=new xp(i,t.mapping,t.wrapS,t.wrapT,t.magFilter,t.minFilter,t.format,t.type,t.anisotropy,t.colorSpace),this.texture.isRenderTargetTexture=!0,this.texture.generateMipmaps=t.generateMipmaps!==void 0?t.generateMipmaps:!1,this.texture.minFilter=t.minFilter!==void 0?t.minFilter:mi}fromEquirectangularTexture(e,t){this.texture.type=t.type,this.texture.colorSpace=t.colorSpace,this.texture.generateMipmaps=t.generateMipmaps,this.texture.minFilter=t.minFilter,this.texture.magFilter=t.magFilter;const n={uniforms:{tEquirect:{value:null}},vertexShader:`

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
			`},i=new _i(5,5,5),r=new Ts({name:"CubemapFromEquirect",uniforms:na(n.uniforms),vertexShader:n.vertexShader,fragmentShader:n.fragmentShader,side:zn,blending:bs});r.uniforms.tEquirect.value=t;const a=new Xt(i,r),o=t.minFilter;return t.minFilter===Ks&&(t.minFilter=mi),new Ax(1,10,this).update(e,a),t.minFilter=o,a.geometry.dispose(),a.material.dispose(),this}clear(e,t,n,i){const r=e.getRenderTarget();for(let a=0;a<6;a++)e.setRenderTarget(this,a),e.clear(t,n,i);e.setRenderTarget(r)}}const mc=new V,Rx=new V,Px=new at;class vs{constructor(e=new V(1,0,0),t=0){this.isPlane=!0,this.normal=e,this.constant=t}set(e,t){return this.normal.copy(e),this.constant=t,this}setComponents(e,t,n,i){return this.normal.set(e,t,n),this.constant=i,this}setFromNormalAndCoplanarPoint(e,t){return this.normal.copy(e),this.constant=-t.dot(this.normal),this}setFromCoplanarPoints(e,t,n){const i=mc.subVectors(n,t).cross(Rx.subVectors(e,t)).normalize();return this.setFromNormalAndCoplanarPoint(i,e),this}copy(e){return this.normal.copy(e.normal),this.constant=e.constant,this}normalize(){const e=1/this.normal.length();return this.normal.multiplyScalar(e),this.constant*=e,this}negate(){return this.constant*=-1,this.normal.negate(),this}distanceToPoint(e){return this.normal.dot(e)+this.constant}distanceToSphere(e){return this.distanceToPoint(e.center)-e.radius}projectPoint(e,t){return t.copy(e).addScaledVector(this.normal,-this.distanceToPoint(e))}intersectLine(e,t){const n=e.delta(mc),i=this.normal.dot(n);if(i===0)return this.distanceToPoint(e.start)===0?t.copy(e.start):null;const r=-(e.start.dot(this.normal)+this.constant)/i;return r<0||r>1?null:t.copy(e.start).addScaledVector(n,r)}intersectsLine(e){const t=this.distanceToPoint(e.start),n=this.distanceToPoint(e.end);return t<0&&n>0||n<0&&t>0}intersectsBox(e){return e.intersectsPlane(this)}intersectsSphere(e){return e.intersectsPlane(this)}coplanarPoint(e){return e.copy(this.normal).multiplyScalar(-this.constant)}applyMatrix4(e,t){const n=t||Px.getNormalMatrix(e),i=this.coplanarPoint(mc).applyMatrix4(e),r=this.normal.applyMatrix3(n).normalize();return this.constant=-i.dot(r),this}translate(e){return this.constant-=e.dot(this.normal),this}equals(e){return e.normal.equals(this.normal)&&e.constant===this.constant}clone(){return new this.constructor().copy(this)}}const zs=new no,Io=new V;class $h{constructor(e=new vs,t=new vs,n=new vs,i=new vs,r=new vs,a=new vs){this.planes=[e,t,n,i,r,a]}set(e,t,n,i,r,a){const o=this.planes;return o[0].copy(e),o[1].copy(t),o[2].copy(n),o[3].copy(i),o[4].copy(r),o[5].copy(a),this}copy(e){const t=this.planes;for(let n=0;n<6;n++)t[n].copy(e.planes[n]);return this}setFromProjectionMatrix(e,t=Ji){const n=this.planes,i=e.elements,r=i[0],a=i[1],o=i[2],l=i[3],c=i[4],h=i[5],d=i[6],u=i[7],f=i[8],g=i[9],x=i[10],p=i[11],m=i[12],b=i[13],_=i[14],S=i[15];if(n[0].setComponents(l-r,u-c,p-f,S-m).normalize(),n[1].setComponents(l+r,u+c,p+f,S+m).normalize(),n[2].setComponents(l+a,u+h,p+g,S+b).normalize(),n[3].setComponents(l-a,u-h,p-g,S-b).normalize(),n[4].setComponents(l-o,u-d,p-x,S-_).normalize(),t===Ji)n[5].setComponents(l+o,u+d,p+x,S+_).normalize();else if(t===cl)n[5].setComponents(o,d,x,_).normalize();else throw new Error("THREE.Frustum.setFromProjectionMatrix(): Invalid coordinate system: "+t);return this}intersectsObject(e){if(e.boundingSphere!==void 0)e.boundingSphere===null&&e.computeBoundingSphere(),zs.copy(e.boundingSphere).applyMatrix4(e.matrixWorld);else{const t=e.geometry;t.boundingSphere===null&&t.computeBoundingSphere(),zs.copy(t.boundingSphere).applyMatrix4(e.matrixWorld)}return this.intersectsSphere(zs)}intersectsSprite(e){return zs.center.set(0,0,0),zs.radius=.7071067811865476,zs.applyMatrix4(e.matrixWorld),this.intersectsSphere(zs)}intersectsSphere(e){const t=this.planes,n=e.center,i=-e.radius;for(let r=0;r<6;r++)if(t[r].distanceToPoint(n)<i)return!1;return!0}intersectsBox(e){const t=this.planes;for(let n=0;n<6;n++){const i=t[n];if(Io.x=i.normal.x>0?e.max.x:e.min.x,Io.y=i.normal.y>0?e.max.y:e.min.y,Io.z=i.normal.z>0?e.max.z:e.min.z,i.distanceToPoint(Io)<0)return!1}return!0}containsPoint(e){const t=this.planes;for(let n=0;n<6;n++)if(t[n].distanceToPoint(e)<0)return!1;return!0}clone(){return new this.constructor().copy(this)}}function vp(){let s=null,e=!1,t=null,n=null;function i(r,a){t(r,a),n=s.requestAnimationFrame(i)}return{start:function(){e!==!0&&t!==null&&(n=s.requestAnimationFrame(i),e=!0)},stop:function(){s.cancelAnimationFrame(n),e=!1},setAnimationLoop:function(r){t=r},setContext:function(r){s=r}}}function Lx(s){const e=new WeakMap;function t(o,l){const c=o.array,h=o.usage,d=c.byteLength,u=s.createBuffer();s.bindBuffer(l,u),s.bufferData(l,c,h),o.onUploadCallback();let f;if(c instanceof Float32Array)f=s.FLOAT;else if(c instanceof Uint16Array)o.isFloat16BufferAttribute?f=s.HALF_FLOAT:f=s.UNSIGNED_SHORT;else if(c instanceof Int16Array)f=s.SHORT;else if(c instanceof Uint32Array)f=s.UNSIGNED_INT;else if(c instanceof Int32Array)f=s.INT;else if(c instanceof Int8Array)f=s.BYTE;else if(c instanceof Uint8Array)f=s.UNSIGNED_BYTE;else if(c instanceof Uint8ClampedArray)f=s.UNSIGNED_BYTE;else throw new Error("THREE.WebGLAttributes: Unsupported buffer data format: "+c);return{buffer:u,type:f,bytesPerElement:c.BYTES_PER_ELEMENT,version:o.version,size:d}}function n(o,l,c){const h=l.array,d=l._updateRange,u=l.updateRanges;if(s.bindBuffer(c,o),d.count===-1&&u.length===0&&s.bufferSubData(c,0,h),u.length!==0){for(let f=0,g=u.length;f<g;f++){const x=u[f];s.bufferSubData(c,x.start*h.BYTES_PER_ELEMENT,h,x.start,x.count)}l.clearUpdateRanges()}d.count!==-1&&(s.bufferSubData(c,d.offset*h.BYTES_PER_ELEMENT,h,d.offset,d.count),d.count=-1),l.onUploadCallback()}function i(o){return o.isInterleavedBufferAttribute&&(o=o.data),e.get(o)}function r(o){o.isInterleavedBufferAttribute&&(o=o.data);const l=e.get(o);l&&(s.deleteBuffer(l.buffer),e.delete(o))}function a(o,l){if(o.isInterleavedBufferAttribute&&(o=o.data),o.isGLBufferAttribute){const h=e.get(o);(!h||h.version<o.version)&&e.set(o,{buffer:o.buffer,type:o.type,bytesPerElement:o.elementSize,version:o.version});return}const c=e.get(o);if(c===void 0)e.set(o,t(o,l));else if(c.version<o.version){if(c.size!==o.array.byteLength)throw new Error("THREE.WebGLAttributes: The size of the buffer attribute's array buffer does not match the original size. Resizing buffer attributes is not supported.");n(c.buffer,o,l),c.version=o.version}}return{get:i,remove:r,update:a}}class so extends Jt{constructor(e=1,t=1,n=1,i=1){super(),this.type="PlaneGeometry",this.parameters={width:e,height:t,widthSegments:n,heightSegments:i};const r=e/2,a=t/2,o=Math.floor(n),l=Math.floor(i),c=o+1,h=l+1,d=e/o,u=t/l,f=[],g=[],x=[],p=[];for(let m=0;m<h;m++){const b=m*u-a;for(let _=0;_<c;_++){const S=_*d-r;g.push(S,-b,0),x.push(0,0,1),p.push(_/o),p.push(1-m/l)}}for(let m=0;m<l;m++)for(let b=0;b<o;b++){const _=b+c*m,S=b+c*(m+1),I=b+1+c*(m+1),A=b+1+c*m;f.push(_,S,A),f.push(S,I,A)}this.setIndex(f),this.setAttribute("position",new It(g,3)),this.setAttribute("normal",new It(x,3)),this.setAttribute("uv",new It(p,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new so(e.width,e.height,e.widthSegments,e.heightSegments)}}var Dx=`#ifdef USE_ALPHAHASH
	if ( diffuseColor.a < getAlphaHashThreshold( vPosition ) ) discard;
#endif`,Ix=`#ifdef USE_ALPHAHASH
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
#endif`,Ux=`#ifdef USE_ALPHAMAP
	diffuseColor.a *= texture2D( alphaMap, vAlphaMapUv ).g;
#endif`,Nx=`#ifdef USE_ALPHAMAP
	uniform sampler2D alphaMap;
#endif`,Fx=`#ifdef USE_ALPHATEST
	#ifdef ALPHA_TO_COVERAGE
	diffuseColor.a = smoothstep( alphaTest, alphaTest + fwidth( diffuseColor.a ), diffuseColor.a );
	if ( diffuseColor.a == 0.0 ) discard;
	#else
	if ( diffuseColor.a < alphaTest ) discard;
	#endif
#endif`,Ox=`#ifdef USE_ALPHATEST
	uniform float alphaTest;
#endif`,kx=`#ifdef USE_AOMAP
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
#endif`,Bx=`#ifdef USE_AOMAP
	uniform sampler2D aoMap;
	uniform float aoMapIntensity;
#endif`,zx=`#ifdef USE_BATCHING
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
#endif`,Hx=`#ifdef USE_BATCHING
	mat4 batchingMatrix = getBatchingMatrix( getIndirectIndex( gl_DrawID ) );
#endif`,Vx=`vec3 transformed = vec3( position );
#ifdef USE_ALPHAHASH
	vPosition = vec3( position );
#endif`,Gx=`vec3 objectNormal = vec3( normal );
#ifdef USE_TANGENT
	vec3 objectTangent = vec3( tangent.xyz );
#endif`,Wx=`float G_BlinnPhong_Implicit( ) {
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
} // validated`,$x=`#ifdef USE_IRIDESCENCE
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
#endif`,qx=`#ifdef USE_BUMPMAP
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
#endif`,Xx=`#if NUM_CLIPPING_PLANES > 0
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
#endif`,Yx=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
	uniform vec4 clippingPlanes[ NUM_CLIPPING_PLANES ];
#endif`,jx=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
#endif`,Kx=`#if NUM_CLIPPING_PLANES > 0
	vClipPosition = - mvPosition.xyz;
#endif`,Jx=`#if defined( USE_COLOR_ALPHA )
	diffuseColor *= vColor;
#elif defined( USE_COLOR )
	diffuseColor.rgb *= vColor;
#endif`,Zx=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR )
	varying vec3 vColor;
#endif`,Qx=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR ) || defined( USE_INSTANCING_COLOR ) || defined( USE_BATCHING_COLOR )
	varying vec3 vColor;
#endif`,e0=`#if defined( USE_COLOR_ALPHA )
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
#endif`,t0=`#define PI 3.141592653589793
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
} // validated`,n0=`#ifdef ENVMAP_TYPE_CUBE_UV
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
#endif`,i0=`vec3 transformedNormal = objectNormal;
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
#endif`,s0=`#ifdef USE_DISPLACEMENTMAP
	uniform sampler2D displacementMap;
	uniform float displacementScale;
	uniform float displacementBias;
#endif`,r0=`#ifdef USE_DISPLACEMENTMAP
	transformed += normalize( objectNormal ) * ( texture2D( displacementMap, vDisplacementMapUv ).x * displacementScale + displacementBias );
#endif`,a0=`#ifdef USE_EMISSIVEMAP
	vec4 emissiveColor = texture2D( emissiveMap, vEmissiveMapUv );
	totalEmissiveRadiance *= emissiveColor.rgb;
#endif`,o0=`#ifdef USE_EMISSIVEMAP
	uniform sampler2D emissiveMap;
#endif`,l0="gl_FragColor = linearToOutputTexel( gl_FragColor );",c0=`
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
}`,h0=`#ifdef USE_ENVMAP
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
#endif`,d0=`#ifdef USE_ENVMAP
	uniform float envMapIntensity;
	uniform float flipEnvMap;
	uniform mat3 envMapRotation;
	#ifdef ENVMAP_TYPE_CUBE
		uniform samplerCube envMap;
	#else
		uniform sampler2D envMap;
	#endif
	
#endif`,u0=`#ifdef USE_ENVMAP
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
#endif`,f0=`#ifdef USE_ENVMAP
	#if defined( USE_BUMPMAP ) || defined( USE_NORMALMAP ) || defined( PHONG ) || defined( LAMBERT )
		#define ENV_WORLDPOS
	#endif
	#ifdef ENV_WORLDPOS
		
		varying vec3 vWorldPosition;
	#else
		varying vec3 vReflect;
		uniform float refractionRatio;
	#endif
#endif`,p0=`#ifdef USE_ENVMAP
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
#endif`,m0=`#ifdef USE_FOG
	vFogDepth = - mvPosition.z;
#endif`,g0=`#ifdef USE_FOG
	varying float vFogDepth;
#endif`,x0=`#ifdef USE_FOG
	#ifdef FOG_EXP2
		float fogFactor = 1.0 - exp( - fogDensity * fogDensity * vFogDepth * vFogDepth );
	#else
		float fogFactor = smoothstep( fogNear, fogFar, vFogDepth );
	#endif
	gl_FragColor.rgb = mix( gl_FragColor.rgb, fogColor, fogFactor );
#endif`,v0=`#ifdef USE_FOG
	uniform vec3 fogColor;
	varying float vFogDepth;
	#ifdef FOG_EXP2
		uniform float fogDensity;
	#else
		uniform float fogNear;
		uniform float fogFar;
	#endif
#endif`,_0=`#ifdef USE_GRADIENTMAP
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
}`,y0=`#ifdef USE_LIGHTMAP
	uniform sampler2D lightMap;
	uniform float lightMapIntensity;
#endif`,b0=`LambertMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularStrength = specularStrength;`,S0=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Lambert`,M0=`uniform bool receiveShadow;
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
#endif`,w0=`#ifdef USE_ENVMAP
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
#endif`,E0=`ToonMaterial material;
material.diffuseColor = diffuseColor.rgb;`,T0=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Toon`,A0=`BlinnPhongMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularColor = specular;
material.specularShininess = shininess;
material.specularStrength = specularStrength;`,C0=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_BlinnPhong`,R0=`PhysicalMaterial material;
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
#endif`,P0=`struct PhysicalMaterial {
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
}`,L0=`
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
#endif`,D0=`#if defined( RE_IndirectDiffuse )
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
#endif`,I0=`#if defined( RE_IndirectDiffuse )
	RE_IndirectDiffuse( irradiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif
#if defined( RE_IndirectSpecular )
	RE_IndirectSpecular( radiance, iblIrradiance, clearcoatRadiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif`,U0=`#if defined( USE_LOGDEPTHBUF )
	gl_FragDepth = vIsPerspective == 0.0 ? gl_FragCoord.z : log2( vFragDepth ) * logDepthBufFC * 0.5;
#endif`,N0=`#if defined( USE_LOGDEPTHBUF )
	uniform float logDepthBufFC;
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,F0=`#ifdef USE_LOGDEPTHBUF
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,O0=`#ifdef USE_LOGDEPTHBUF
	vFragDepth = 1.0 + gl_Position.w;
	vIsPerspective = float( isPerspectiveMatrix( projectionMatrix ) );
#endif`,k0=`#ifdef USE_MAP
	vec4 sampledDiffuseColor = texture2D( map, vMapUv );
	#ifdef DECODE_VIDEO_TEXTURE
		sampledDiffuseColor = vec4( mix( pow( sampledDiffuseColor.rgb * 0.9478672986 + vec3( 0.0521327014 ), vec3( 2.4 ) ), sampledDiffuseColor.rgb * 0.0773993808, vec3( lessThanEqual( sampledDiffuseColor.rgb, vec3( 0.04045 ) ) ) ), sampledDiffuseColor.w );
	
	#endif
	diffuseColor *= sampledDiffuseColor;
#endif`,B0=`#ifdef USE_MAP
	uniform sampler2D map;
#endif`,z0=`#if defined( USE_MAP ) || defined( USE_ALPHAMAP )
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
#endif`,H0=`#if defined( USE_POINTS_UV )
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
#endif`,V0=`float metalnessFactor = metalness;
#ifdef USE_METALNESSMAP
	vec4 texelMetalness = texture2D( metalnessMap, vMetalnessMapUv );
	metalnessFactor *= texelMetalness.b;
#endif`,G0=`#ifdef USE_METALNESSMAP
	uniform sampler2D metalnessMap;
#endif`,W0=`#ifdef USE_INSTANCING_MORPH
	float morphTargetInfluences[ MORPHTARGETS_COUNT ];
	float morphTargetBaseInfluence = texelFetch( morphTexture, ivec2( 0, gl_InstanceID ), 0 ).r;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		morphTargetInfluences[i] =  texelFetch( morphTexture, ivec2( i + 1, gl_InstanceID ), 0 ).r;
	}
#endif`,$0=`#if defined( USE_MORPHCOLORS )
	vColor *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		#if defined( USE_COLOR_ALPHA )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ) * morphTargetInfluences[ i ];
		#elif defined( USE_COLOR )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ).rgb * morphTargetInfluences[ i ];
		#endif
	}
#endif`,q0=`#ifdef USE_MORPHNORMALS
	objectNormal *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) objectNormal += getMorph( gl_VertexID, i, 1 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,X0=`#ifdef USE_MORPHTARGETS
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
#endif`,Y0=`#ifdef USE_MORPHTARGETS
	transformed *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) transformed += getMorph( gl_VertexID, i, 0 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,j0=`float faceDirection = gl_FrontFacing ? 1.0 : - 1.0;
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
vec3 nonPerturbedNormal = normal;`,K0=`#ifdef USE_NORMALMAP_OBJECTSPACE
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
#endif`,J0=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,Z0=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,Q0=`#ifndef FLAT_SHADED
	vNormal = normalize( transformedNormal );
	#ifdef USE_TANGENT
		vTangent = normalize( transformedTangent );
		vBitangent = normalize( cross( vNormal, vTangent ) * tangent.w );
	#endif
#endif`,ev=`#ifdef USE_NORMALMAP
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
#endif`,tv=`#ifdef USE_CLEARCOAT
	vec3 clearcoatNormal = nonPerturbedNormal;
#endif`,nv=`#ifdef USE_CLEARCOAT_NORMALMAP
	vec3 clearcoatMapN = texture2D( clearcoatNormalMap, vClearcoatNormalMapUv ).xyz * 2.0 - 1.0;
	clearcoatMapN.xy *= clearcoatNormalScale;
	clearcoatNormal = normalize( tbn2 * clearcoatMapN );
#endif`,iv=`#ifdef USE_CLEARCOATMAP
	uniform sampler2D clearcoatMap;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	uniform sampler2D clearcoatNormalMap;
	uniform vec2 clearcoatNormalScale;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	uniform sampler2D clearcoatRoughnessMap;
#endif`,sv=`#ifdef USE_IRIDESCENCEMAP
	uniform sampler2D iridescenceMap;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	uniform sampler2D iridescenceThicknessMap;
#endif`,rv=`#ifdef OPAQUE
diffuseColor.a = 1.0;
#endif
#ifdef USE_TRANSMISSION
diffuseColor.a *= material.transmissionAlpha;
#endif
gl_FragColor = vec4( outgoingLight, diffuseColor.a );`,av=`vec3 packNormalToRGB( const in vec3 normal ) {
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
}`,ov=`#ifdef PREMULTIPLIED_ALPHA
	gl_FragColor.rgb *= gl_FragColor.a;
#endif`,lv=`vec4 mvPosition = vec4( transformed, 1.0 );
#ifdef USE_BATCHING
	mvPosition = batchingMatrix * mvPosition;
#endif
#ifdef USE_INSTANCING
	mvPosition = instanceMatrix * mvPosition;
#endif
mvPosition = modelViewMatrix * mvPosition;
gl_Position = projectionMatrix * mvPosition;`,cv=`#ifdef DITHERING
	gl_FragColor.rgb = dithering( gl_FragColor.rgb );
#endif`,hv=`#ifdef DITHERING
	vec3 dithering( vec3 color ) {
		float grid_position = rand( gl_FragCoord.xy );
		vec3 dither_shift_RGB = vec3( 0.25 / 255.0, -0.25 / 255.0, 0.25 / 255.0 );
		dither_shift_RGB = mix( 2.0 * dither_shift_RGB, -2.0 * dither_shift_RGB, grid_position );
		return color + dither_shift_RGB;
	}
#endif`,dv=`float roughnessFactor = roughness;
#ifdef USE_ROUGHNESSMAP
	vec4 texelRoughness = texture2D( roughnessMap, vRoughnessMapUv );
	roughnessFactor *= texelRoughness.g;
#endif`,uv=`#ifdef USE_ROUGHNESSMAP
	uniform sampler2D roughnessMap;
#endif`,fv=`#if NUM_SPOT_LIGHT_COORDS > 0
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
#endif`,pv=`#if NUM_SPOT_LIGHT_COORDS > 0
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
#endif`,mv=`#if ( defined( USE_SHADOWMAP ) && ( NUM_DIR_LIGHT_SHADOWS > 0 || NUM_POINT_LIGHT_SHADOWS > 0 ) ) || ( NUM_SPOT_LIGHT_COORDS > 0 )
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
#endif`,gv=`float getShadowMask() {
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
}`,xv=`#ifdef USE_SKINNING
	mat4 boneMatX = getBoneMatrix( skinIndex.x );
	mat4 boneMatY = getBoneMatrix( skinIndex.y );
	mat4 boneMatZ = getBoneMatrix( skinIndex.z );
	mat4 boneMatW = getBoneMatrix( skinIndex.w );
#endif`,vv=`#ifdef USE_SKINNING
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
#endif`,_v=`#ifdef USE_SKINNING
	vec4 skinVertex = bindMatrix * vec4( transformed, 1.0 );
	vec4 skinned = vec4( 0.0 );
	skinned += boneMatX * skinVertex * skinWeight.x;
	skinned += boneMatY * skinVertex * skinWeight.y;
	skinned += boneMatZ * skinVertex * skinWeight.z;
	skinned += boneMatW * skinVertex * skinWeight.w;
	transformed = ( bindMatrixInverse * skinned ).xyz;
#endif`,yv=`#ifdef USE_SKINNING
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
#endif`,bv=`float specularStrength;
#ifdef USE_SPECULARMAP
	vec4 texelSpecular = texture2D( specularMap, vSpecularMapUv );
	specularStrength = texelSpecular.r;
#else
	specularStrength = 1.0;
#endif`,Sv=`#ifdef USE_SPECULARMAP
	uniform sampler2D specularMap;
#endif`,Mv=`#if defined( TONE_MAPPING )
	gl_FragColor.rgb = toneMapping( gl_FragColor.rgb );
#endif`,wv=`#ifndef saturate
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
vec3 CustomToneMapping( vec3 color ) { return color; }`,Ev=`#ifdef USE_TRANSMISSION
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
#endif`,Tv=`#ifdef USE_TRANSMISSION
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
#endif`,Av=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
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
#endif`,Cv=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
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
#endif`,Rv=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
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
#endif`,Pv=`#if defined( USE_ENVMAP ) || defined( DISTANCE ) || defined ( USE_SHADOWMAP ) || defined ( USE_TRANSMISSION ) || NUM_SPOT_LIGHT_COORDS > 0
	vec4 worldPosition = vec4( transformed, 1.0 );
	#ifdef USE_BATCHING
		worldPosition = batchingMatrix * worldPosition;
	#endif
	#ifdef USE_INSTANCING
		worldPosition = instanceMatrix * worldPosition;
	#endif
	worldPosition = modelMatrix * worldPosition;
#endif`;const Lv=`varying vec2 vUv;
uniform mat3 uvTransform;
void main() {
	vUv = ( uvTransform * vec3( uv, 1 ) ).xy;
	gl_Position = vec4( position.xy, 1.0, 1.0 );
}`,Dv=`uniform sampler2D t2D;
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
}`,Iv=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,Uv=`#ifdef ENVMAP_TYPE_CUBE
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
}`,Nv=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,Fv=`uniform samplerCube tCube;
uniform float tFlip;
uniform float opacity;
varying vec3 vWorldDirection;
void main() {
	vec4 texColor = textureCube( tCube, vec3( tFlip * vWorldDirection.x, vWorldDirection.yz ) );
	gl_FragColor = texColor;
	gl_FragColor.a *= opacity;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,Ov=`#include <common>
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
}`,kv=`#if DEPTH_PACKING == 3200
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
}`,Bv=`#define DISTANCE
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
}`,zv=`#define DISTANCE
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
}`,Hv=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
}`,Vv=`uniform sampler2D tEquirect;
varying vec3 vWorldDirection;
#include <common>
void main() {
	vec3 direction = normalize( vWorldDirection );
	vec2 sampleUV = equirectUv( direction );
	gl_FragColor = texture2D( tEquirect, sampleUV );
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,Gv=`uniform float scale;
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
}`,Wv=`uniform vec3 diffuse;
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
}`,$v=`#include <common>
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
}`,qv=`uniform vec3 diffuse;
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
}`,Xv=`#define LAMBERT
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
}`,Yv=`#define LAMBERT
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
}`,jv=`#define MATCAP
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
}`,Kv=`#define MATCAP
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
}`,Jv=`#define NORMAL
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
}`,Zv=`#define NORMAL
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
}`,Qv=`#define PHONG
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
}`,e_=`#define PHONG
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
}`,t_=`#define STANDARD
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
}`,n_=`#define STANDARD
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
}`,i_=`#define TOON
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
}`,s_=`#define TOON
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
}`,r_=`uniform float size;
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
}`,a_=`uniform vec3 diffuse;
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
}`,o_=`#include <common>
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
}`,l_=`uniform vec3 color;
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
}`,c_=`uniform float rotation;
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
}`,h_=`uniform vec3 diffuse;
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
}`,rt={alphahash_fragment:Dx,alphahash_pars_fragment:Ix,alphamap_fragment:Ux,alphamap_pars_fragment:Nx,alphatest_fragment:Fx,alphatest_pars_fragment:Ox,aomap_fragment:kx,aomap_pars_fragment:Bx,batching_pars_vertex:zx,batching_vertex:Hx,begin_vertex:Vx,beginnormal_vertex:Gx,bsdfs:Wx,iridescence_fragment:$x,bumpmap_pars_fragment:qx,clipping_planes_fragment:Xx,clipping_planes_pars_fragment:Yx,clipping_planes_pars_vertex:jx,clipping_planes_vertex:Kx,color_fragment:Jx,color_pars_fragment:Zx,color_pars_vertex:Qx,color_vertex:e0,common:t0,cube_uv_reflection_fragment:n0,defaultnormal_vertex:i0,displacementmap_pars_vertex:s0,displacementmap_vertex:r0,emissivemap_fragment:a0,emissivemap_pars_fragment:o0,colorspace_fragment:l0,colorspace_pars_fragment:c0,envmap_fragment:h0,envmap_common_pars_fragment:d0,envmap_pars_fragment:u0,envmap_pars_vertex:f0,envmap_physical_pars_fragment:w0,envmap_vertex:p0,fog_vertex:m0,fog_pars_vertex:g0,fog_fragment:x0,fog_pars_fragment:v0,gradientmap_pars_fragment:_0,lightmap_pars_fragment:y0,lights_lambert_fragment:b0,lights_lambert_pars_fragment:S0,lights_pars_begin:M0,lights_toon_fragment:E0,lights_toon_pars_fragment:T0,lights_phong_fragment:A0,lights_phong_pars_fragment:C0,lights_physical_fragment:R0,lights_physical_pars_fragment:P0,lights_fragment_begin:L0,lights_fragment_maps:D0,lights_fragment_end:I0,logdepthbuf_fragment:U0,logdepthbuf_pars_fragment:N0,logdepthbuf_pars_vertex:F0,logdepthbuf_vertex:O0,map_fragment:k0,map_pars_fragment:B0,map_particle_fragment:z0,map_particle_pars_fragment:H0,metalnessmap_fragment:V0,metalnessmap_pars_fragment:G0,morphinstance_vertex:W0,morphcolor_vertex:$0,morphnormal_vertex:q0,morphtarget_pars_vertex:X0,morphtarget_vertex:Y0,normal_fragment_begin:j0,normal_fragment_maps:K0,normal_pars_fragment:J0,normal_pars_vertex:Z0,normal_vertex:Q0,normalmap_pars_fragment:ev,clearcoat_normal_fragment_begin:tv,clearcoat_normal_fragment_maps:nv,clearcoat_pars_fragment:iv,iridescence_pars_fragment:sv,opaque_fragment:rv,packing:av,premultiplied_alpha_fragment:ov,project_vertex:lv,dithering_fragment:cv,dithering_pars_fragment:hv,roughnessmap_fragment:dv,roughnessmap_pars_fragment:uv,shadowmap_pars_fragment:fv,shadowmap_pars_vertex:pv,shadowmap_vertex:mv,shadowmask_pars_fragment:gv,skinbase_vertex:xv,skinning_pars_vertex:vv,skinning_vertex:_v,skinnormal_vertex:yv,specularmap_fragment:bv,specularmap_pars_fragment:Sv,tonemapping_fragment:Mv,tonemapping_pars_fragment:wv,transmission_fragment:Ev,transmission_pars_fragment:Tv,uv_pars_fragment:Av,uv_pars_vertex:Cv,uv_vertex:Rv,worldpos_vertex:Pv,background_vert:Lv,background_frag:Dv,backgroundCube_vert:Iv,backgroundCube_frag:Uv,cube_vert:Nv,cube_frag:Fv,depth_vert:Ov,depth_frag:kv,distanceRGBA_vert:Bv,distanceRGBA_frag:zv,equirect_vert:Hv,equirect_frag:Vv,linedashed_vert:Gv,linedashed_frag:Wv,meshbasic_vert:$v,meshbasic_frag:qv,meshlambert_vert:Xv,meshlambert_frag:Yv,meshmatcap_vert:jv,meshmatcap_frag:Kv,meshnormal_vert:Jv,meshnormal_frag:Zv,meshphong_vert:Qv,meshphong_frag:e_,meshphysical_vert:t_,meshphysical_frag:n_,meshtoon_vert:i_,meshtoon_frag:s_,points_vert:r_,points_frag:a_,shadow_vert:o_,shadow_frag:l_,sprite_vert:c_,sprite_frag:h_},Re={common:{diffuse:{value:new nt(16777215)},opacity:{value:1},map:{value:null},mapTransform:{value:new at},alphaMap:{value:null},alphaMapTransform:{value:new at},alphaTest:{value:0}},specularmap:{specularMap:{value:null},specularMapTransform:{value:new at}},envmap:{envMap:{value:null},envMapRotation:{value:new at},flipEnvMap:{value:-1},reflectivity:{value:1},ior:{value:1.5},refractionRatio:{value:.98}},aomap:{aoMap:{value:null},aoMapIntensity:{value:1},aoMapTransform:{value:new at}},lightmap:{lightMap:{value:null},lightMapIntensity:{value:1},lightMapTransform:{value:new at}},bumpmap:{bumpMap:{value:null},bumpMapTransform:{value:new at},bumpScale:{value:1}},normalmap:{normalMap:{value:null},normalMapTransform:{value:new at},normalScale:{value:new Xe(1,1)}},displacementmap:{displacementMap:{value:null},displacementMapTransform:{value:new at},displacementScale:{value:1},displacementBias:{value:0}},emissivemap:{emissiveMap:{value:null},emissiveMapTransform:{value:new at}},metalnessmap:{metalnessMap:{value:null},metalnessMapTransform:{value:new at}},roughnessmap:{roughnessMap:{value:null},roughnessMapTransform:{value:new at}},gradientmap:{gradientMap:{value:null}},fog:{fogDensity:{value:25e-5},fogNear:{value:1},fogFar:{value:2e3},fogColor:{value:new nt(16777215)}},lights:{ambientLightColor:{value:[]},lightProbe:{value:[]},directionalLights:{value:[],properties:{direction:{},color:{}}},directionalLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},directionalShadowMap:{value:[]},directionalShadowMatrix:{value:[]},spotLights:{value:[],properties:{color:{},position:{},direction:{},distance:{},coneCos:{},penumbraCos:{},decay:{}}},spotLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},spotLightMap:{value:[]},spotShadowMap:{value:[]},spotLightMatrix:{value:[]},pointLights:{value:[],properties:{color:{},position:{},decay:{},distance:{}}},pointLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{},shadowCameraNear:{},shadowCameraFar:{}}},pointShadowMap:{value:[]},pointShadowMatrix:{value:[]},hemisphereLights:{value:[],properties:{direction:{},skyColor:{},groundColor:{}}},rectAreaLights:{value:[],properties:{color:{},position:{},width:{},height:{}}},ltc_1:{value:null},ltc_2:{value:null}},points:{diffuse:{value:new nt(16777215)},opacity:{value:1},size:{value:1},scale:{value:1},map:{value:null},alphaMap:{value:null},alphaMapTransform:{value:new at},alphaTest:{value:0},uvTransform:{value:new at}},sprite:{diffuse:{value:new nt(16777215)},opacity:{value:1},center:{value:new Xe(.5,.5)},rotation:{value:0},map:{value:null},mapTransform:{value:new at},alphaMap:{value:null},alphaMapTransform:{value:new at},alphaTest:{value:0}}},Ii={basic:{uniforms:Un([Re.common,Re.specularmap,Re.envmap,Re.aomap,Re.lightmap,Re.fog]),vertexShader:rt.meshbasic_vert,fragmentShader:rt.meshbasic_frag},lambert:{uniforms:Un([Re.common,Re.specularmap,Re.envmap,Re.aomap,Re.lightmap,Re.emissivemap,Re.bumpmap,Re.normalmap,Re.displacementmap,Re.fog,Re.lights,{emissive:{value:new nt(0)}}]),vertexShader:rt.meshlambert_vert,fragmentShader:rt.meshlambert_frag},phong:{uniforms:Un([Re.common,Re.specularmap,Re.envmap,Re.aomap,Re.lightmap,Re.emissivemap,Re.bumpmap,Re.normalmap,Re.displacementmap,Re.fog,Re.lights,{emissive:{value:new nt(0)},specular:{value:new nt(1118481)},shininess:{value:30}}]),vertexShader:rt.meshphong_vert,fragmentShader:rt.meshphong_frag},standard:{uniforms:Un([Re.common,Re.envmap,Re.aomap,Re.lightmap,Re.emissivemap,Re.bumpmap,Re.normalmap,Re.displacementmap,Re.roughnessmap,Re.metalnessmap,Re.fog,Re.lights,{emissive:{value:new nt(0)},roughness:{value:1},metalness:{value:0},envMapIntensity:{value:1}}]),vertexShader:rt.meshphysical_vert,fragmentShader:rt.meshphysical_frag},toon:{uniforms:Un([Re.common,Re.aomap,Re.lightmap,Re.emissivemap,Re.bumpmap,Re.normalmap,Re.displacementmap,Re.gradientmap,Re.fog,Re.lights,{emissive:{value:new nt(0)}}]),vertexShader:rt.meshtoon_vert,fragmentShader:rt.meshtoon_frag},matcap:{uniforms:Un([Re.common,Re.bumpmap,Re.normalmap,Re.displacementmap,Re.fog,{matcap:{value:null}}]),vertexShader:rt.meshmatcap_vert,fragmentShader:rt.meshmatcap_frag},points:{uniforms:Un([Re.points,Re.fog]),vertexShader:rt.points_vert,fragmentShader:rt.points_frag},dashed:{uniforms:Un([Re.common,Re.fog,{scale:{value:1},dashSize:{value:1},totalSize:{value:2}}]),vertexShader:rt.linedashed_vert,fragmentShader:rt.linedashed_frag},depth:{uniforms:Un([Re.common,Re.displacementmap]),vertexShader:rt.depth_vert,fragmentShader:rt.depth_frag},normal:{uniforms:Un([Re.common,Re.bumpmap,Re.normalmap,Re.displacementmap,{opacity:{value:1}}]),vertexShader:rt.meshnormal_vert,fragmentShader:rt.meshnormal_frag},sprite:{uniforms:Un([Re.sprite,Re.fog]),vertexShader:rt.sprite_vert,fragmentShader:rt.sprite_frag},background:{uniforms:{uvTransform:{value:new at},t2D:{value:null},backgroundIntensity:{value:1}},vertexShader:rt.background_vert,fragmentShader:rt.background_frag},backgroundCube:{uniforms:{envMap:{value:null},flipEnvMap:{value:-1},backgroundBlurriness:{value:0},backgroundIntensity:{value:1},backgroundRotation:{value:new at}},vertexShader:rt.backgroundCube_vert,fragmentShader:rt.backgroundCube_frag},cube:{uniforms:{tCube:{value:null},tFlip:{value:-1},opacity:{value:1}},vertexShader:rt.cube_vert,fragmentShader:rt.cube_frag},equirect:{uniforms:{tEquirect:{value:null}},vertexShader:rt.equirect_vert,fragmentShader:rt.equirect_frag},distanceRGBA:{uniforms:Un([Re.common,Re.displacementmap,{referencePosition:{value:new V},nearDistance:{value:1},farDistance:{value:1e3}}]),vertexShader:rt.distanceRGBA_vert,fragmentShader:rt.distanceRGBA_frag},shadow:{uniforms:Un([Re.lights,Re.fog,{color:{value:new nt(0)},opacity:{value:1}}]),vertexShader:rt.shadow_vert,fragmentShader:rt.shadow_frag}};Ii.physical={uniforms:Un([Ii.standard.uniforms,{clearcoat:{value:0},clearcoatMap:{value:null},clearcoatMapTransform:{value:new at},clearcoatNormalMap:{value:null},clearcoatNormalMapTransform:{value:new at},clearcoatNormalScale:{value:new Xe(1,1)},clearcoatRoughness:{value:0},clearcoatRoughnessMap:{value:null},clearcoatRoughnessMapTransform:{value:new at},dispersion:{value:0},iridescence:{value:0},iridescenceMap:{value:null},iridescenceMapTransform:{value:new at},iridescenceIOR:{value:1.3},iridescenceThicknessMinimum:{value:100},iridescenceThicknessMaximum:{value:400},iridescenceThicknessMap:{value:null},iridescenceThicknessMapTransform:{value:new at},sheen:{value:0},sheenColor:{value:new nt(0)},sheenColorMap:{value:null},sheenColorMapTransform:{value:new at},sheenRoughness:{value:1},sheenRoughnessMap:{value:null},sheenRoughnessMapTransform:{value:new at},transmission:{value:0},transmissionMap:{value:null},transmissionMapTransform:{value:new at},transmissionSamplerSize:{value:new Xe},transmissionSamplerMap:{value:null},thickness:{value:0},thicknessMap:{value:null},thicknessMapTransform:{value:new at},attenuationDistance:{value:0},attenuationColor:{value:new nt(0)},specularColor:{value:new nt(1,1,1)},specularColorMap:{value:null},specularColorMapTransform:{value:new at},specularIntensity:{value:1},specularIntensityMap:{value:null},specularIntensityMapTransform:{value:new at},anisotropyVector:{value:new Xe},anisotropyMap:{value:null},anisotropyMapTransform:{value:new at}}]),vertexShader:rt.meshphysical_vert,fragmentShader:rt.meshphysical_frag};const Uo={r:0,b:0,g:0},Hs=new Ni,d_=new Bt;function u_(s,e,t,n,i,r,a){const o=new nt(0);let l=r===!0?0:1,c,h,d=null,u=0,f=null;function g(b){let _=b.isScene===!0?b.background:null;return _&&_.isTexture&&(_=(b.backgroundBlurriness>0?t:e).get(_)),_}function x(b){let _=!1;const S=g(b);S===null?m(o,l):S&&S.isColor&&(m(S,1),_=!0);const I=s.xr.getEnvironmentBlendMode();I==="additive"?n.buffers.color.setClear(0,0,0,1,a):I==="alpha-blend"&&n.buffers.color.setClear(0,0,0,0,a),(s.autoClear||_)&&(n.buffers.depth.setTest(!0),n.buffers.depth.setMask(!0),n.buffers.color.setMask(!0),s.clear(s.autoClearColor,s.autoClearDepth,s.autoClearStencil))}function p(b,_){const S=g(_);S&&(S.isCubeTexture||S.mapping===vl)?(h===void 0&&(h=new Xt(new _i(1,1,1),new Ts({name:"BackgroundCubeMaterial",uniforms:na(Ii.backgroundCube.uniforms),vertexShader:Ii.backgroundCube.vertexShader,fragmentShader:Ii.backgroundCube.fragmentShader,side:zn,depthTest:!1,depthWrite:!1,fog:!1})),h.geometry.deleteAttribute("normal"),h.geometry.deleteAttribute("uv"),h.onBeforeRender=function(I,A,R){this.matrixWorld.copyPosition(R.matrixWorld)},Object.defineProperty(h.material,"envMap",{get:function(){return this.uniforms.envMap.value}}),i.update(h)),Hs.copy(_.backgroundRotation),Hs.x*=-1,Hs.y*=-1,Hs.z*=-1,S.isCubeTexture&&S.isRenderTargetTexture===!1&&(Hs.y*=-1,Hs.z*=-1),h.material.uniforms.envMap.value=S,h.material.uniforms.flipEnvMap.value=S.isCubeTexture&&S.isRenderTargetTexture===!1?-1:1,h.material.uniforms.backgroundBlurriness.value=_.backgroundBlurriness,h.material.uniforms.backgroundIntensity.value=_.backgroundIntensity,h.material.uniforms.backgroundRotation.value.setFromMatrix4(d_.makeRotationFromEuler(Hs)),h.material.toneMapped=Mt.getTransfer(S.colorSpace)!==kt,(d!==S||u!==S.version||f!==s.toneMapping)&&(h.material.needsUpdate=!0,d=S,u=S.version,f=s.toneMapping),h.layers.enableAll(),b.unshift(h,h.geometry,h.material,0,0,null)):S&&S.isTexture&&(c===void 0&&(c=new Xt(new so(2,2),new Ts({name:"BackgroundMaterial",uniforms:na(Ii.background.uniforms),vertexShader:Ii.background.vertexShader,fragmentShader:Ii.background.fragmentShader,side:Es,depthTest:!1,depthWrite:!1,fog:!1})),c.geometry.deleteAttribute("normal"),Object.defineProperty(c.material,"map",{get:function(){return this.uniforms.t2D.value}}),i.update(c)),c.material.uniforms.t2D.value=S,c.material.uniforms.backgroundIntensity.value=_.backgroundIntensity,c.material.toneMapped=Mt.getTransfer(S.colorSpace)!==kt,S.matrixAutoUpdate===!0&&S.updateMatrix(),c.material.uniforms.uvTransform.value.copy(S.matrix),(d!==S||u!==S.version||f!==s.toneMapping)&&(c.material.needsUpdate=!0,d=S,u=S.version,f=s.toneMapping),c.layers.enableAll(),b.unshift(c,c.geometry,c.material,0,0,null))}function m(b,_){b.getRGB(Uo,mp(s)),n.buffers.color.setClear(Uo.r,Uo.g,Uo.b,_,a)}return{getClearColor:function(){return o},setClearColor:function(b,_=1){o.set(b),l=_,m(o,l)},getClearAlpha:function(){return l},setClearAlpha:function(b){l=b,m(o,l)},render:x,addToRenderList:p}}function f_(s,e){const t=s.getParameter(s.MAX_VERTEX_ATTRIBS),n={},i=u(null);let r=i,a=!1;function o(y,P,X,H,J){let q=!1;const ee=d(H,X,P);r!==ee&&(r=ee,c(r.object)),q=f(y,H,X,J),q&&g(y,H,X,J),J!==null&&e.update(J,s.ELEMENT_ARRAY_BUFFER),(q||a)&&(a=!1,S(y,P,X,H),J!==null&&s.bindBuffer(s.ELEMENT_ARRAY_BUFFER,e.get(J).buffer))}function l(){return s.createVertexArray()}function c(y){return s.bindVertexArray(y)}function h(y){return s.deleteVertexArray(y)}function d(y,P,X){const H=X.wireframe===!0;let J=n[y.id];J===void 0&&(J={},n[y.id]=J);let q=J[P.id];q===void 0&&(q={},J[P.id]=q);let ee=q[H];return ee===void 0&&(ee=u(l()),q[H]=ee),ee}function u(y){const P=[],X=[],H=[];for(let J=0;J<t;J++)P[J]=0,X[J]=0,H[J]=0;return{geometry:null,program:null,wireframe:!1,newAttributes:P,enabledAttributes:X,attributeDivisors:H,object:y,attributes:{},index:null}}function f(y,P,X,H){const J=r.attributes,q=P.attributes;let ee=0;const j=X.getAttributes();for(const ne in j)if(j[ne].location>=0){const ue=J[ne];let ye=q[ne];if(ye===void 0&&(ne==="instanceMatrix"&&y.instanceMatrix&&(ye=y.instanceMatrix),ne==="instanceColor"&&y.instanceColor&&(ye=y.instanceColor)),ue===void 0||ue.attribute!==ye||ye&&ue.data!==ye.data)return!0;ee++}return r.attributesNum!==ee||r.index!==H}function g(y,P,X,H){const J={},q=P.attributes;let ee=0;const j=X.getAttributes();for(const ne in j)if(j[ne].location>=0){let ue=q[ne];ue===void 0&&(ne==="instanceMatrix"&&y.instanceMatrix&&(ue=y.instanceMatrix),ne==="instanceColor"&&y.instanceColor&&(ue=y.instanceColor));const ye={};ye.attribute=ue,ue&&ue.data&&(ye.data=ue.data),J[ne]=ye,ee++}r.attributes=J,r.attributesNum=ee,r.index=H}function x(){const y=r.newAttributes;for(let P=0,X=y.length;P<X;P++)y[P]=0}function p(y){m(y,0)}function m(y,P){const X=r.newAttributes,H=r.enabledAttributes,J=r.attributeDivisors;X[y]=1,H[y]===0&&(s.enableVertexAttribArray(y),H[y]=1),J[y]!==P&&(s.vertexAttribDivisor(y,P),J[y]=P)}function b(){const y=r.newAttributes,P=r.enabledAttributes;for(let X=0,H=P.length;X<H;X++)P[X]!==y[X]&&(s.disableVertexAttribArray(X),P[X]=0)}function _(y,P,X,H,J,q,ee){ee===!0?s.vertexAttribIPointer(y,P,X,J,q):s.vertexAttribPointer(y,P,X,H,J,q)}function S(y,P,X,H){x();const J=H.attributes,q=X.getAttributes(),ee=P.defaultAttributeValues;for(const j in q){const ne=q[j];if(ne.location>=0){let ge=J[j];if(ge===void 0&&(j==="instanceMatrix"&&y.instanceMatrix&&(ge=y.instanceMatrix),j==="instanceColor"&&y.instanceColor&&(ge=y.instanceColor)),ge!==void 0){const ue=ge.normalized,ye=ge.itemSize,Te=e.get(ge);if(Te===void 0)continue;const be=Te.buffer,ie=Te.type,he=Te.bytesPerElement,Se=ie===s.INT||ie===s.UNSIGNED_INT||ge.gpuType===Fh;if(ge.isInterleavedBufferAttribute){const fe=ge.data,ze=fe.stride,We=ge.offset;if(fe.isInstancedInterleavedBuffer){for(let Oe=0;Oe<ne.locationSize;Oe++)m(ne.location+Oe,fe.meshPerAttribute);y.isInstancedMesh!==!0&&H._maxInstanceCount===void 0&&(H._maxInstanceCount=fe.meshPerAttribute*fe.count)}else for(let Oe=0;Oe<ne.locationSize;Oe++)p(ne.location+Oe);s.bindBuffer(s.ARRAY_BUFFER,be);for(let Oe=0;Oe<ne.locationSize;Oe++)_(ne.location+Oe,ye/ne.locationSize,ie,ue,ze*he,(We+ye/ne.locationSize*Oe)*he,Se)}else{if(ge.isInstancedBufferAttribute){for(let fe=0;fe<ne.locationSize;fe++)m(ne.location+fe,ge.meshPerAttribute);y.isInstancedMesh!==!0&&H._maxInstanceCount===void 0&&(H._maxInstanceCount=ge.meshPerAttribute*ge.count)}else for(let fe=0;fe<ne.locationSize;fe++)p(ne.location+fe);s.bindBuffer(s.ARRAY_BUFFER,be);for(let fe=0;fe<ne.locationSize;fe++)_(ne.location+fe,ye/ne.locationSize,ie,ue,ye*he,ye/ne.locationSize*fe*he,Se)}}else if(ee!==void 0){const ue=ee[j];if(ue!==void 0)switch(ue.length){case 2:s.vertexAttrib2fv(ne.location,ue);break;case 3:s.vertexAttrib3fv(ne.location,ue);break;case 4:s.vertexAttrib4fv(ne.location,ue);break;default:s.vertexAttrib1fv(ne.location,ue)}}}}b()}function I(){N();for(const y in n){const P=n[y];for(const X in P){const H=P[X];for(const J in H)h(H[J].object),delete H[J];delete P[X]}delete n[y]}}function A(y){if(n[y.id]===void 0)return;const P=n[y.id];for(const X in P){const H=P[X];for(const J in H)h(H[J].object),delete H[J];delete P[X]}delete n[y.id]}function R(y){for(const P in n){const X=n[P];if(X[y.id]===void 0)continue;const H=X[y.id];for(const J in H)h(H[J].object),delete H[J];delete X[y.id]}}function N(){M(),a=!0,r!==i&&(r=i,c(r.object))}function M(){i.geometry=null,i.program=null,i.wireframe=!1}return{setup:o,reset:N,resetDefaultState:M,dispose:I,releaseStatesOfGeometry:A,releaseStatesOfProgram:R,initAttributes:x,enableAttribute:p,disableUnusedAttributes:b}}function p_(s,e,t){let n;function i(c){n=c}function r(c,h){s.drawArrays(n,c,h),t.update(h,n,1)}function a(c,h,d){d!==0&&(s.drawArraysInstanced(n,c,h,d),t.update(h,n,d))}function o(c,h,d){if(d===0)return;e.get("WEBGL_multi_draw").multiDrawArraysWEBGL(n,c,0,h,0,d);let f=0;for(let g=0;g<d;g++)f+=h[g];t.update(f,n,1)}function l(c,h,d,u){if(d===0)return;const f=e.get("WEBGL_multi_draw");if(f===null)for(let g=0;g<c.length;g++)a(c[g],h[g],u[g]);else{f.multiDrawArraysInstancedWEBGL(n,c,0,h,0,u,0,d);let g=0;for(let x=0;x<d;x++)g+=h[x];for(let x=0;x<u.length;x++)t.update(g,n,u[x])}}this.setMode=i,this.render=r,this.renderInstances=a,this.renderMultiDraw=o,this.renderMultiDrawInstances=l}function m_(s,e,t,n){let i;function r(){if(i!==void 0)return i;if(e.has("EXT_texture_filter_anisotropic")===!0){const A=e.get("EXT_texture_filter_anisotropic");i=s.getParameter(A.MAX_TEXTURE_MAX_ANISOTROPY_EXT)}else i=0;return i}function a(A){return!(A!==vi&&n.convert(A)!==s.getParameter(s.IMPLEMENTATION_COLOR_READ_FORMAT))}function o(A){const R=A===eo&&(e.has("EXT_color_buffer_half_float")||e.has("EXT_color_buffer_float"));return!(A!==ss&&n.convert(A)!==s.getParameter(s.IMPLEMENTATION_COLOR_READ_TYPE)&&A!==Ki&&!R)}function l(A){if(A==="highp"){if(s.getShaderPrecisionFormat(s.VERTEX_SHADER,s.HIGH_FLOAT).precision>0&&s.getShaderPrecisionFormat(s.FRAGMENT_SHADER,s.HIGH_FLOAT).precision>0)return"highp";A="mediump"}return A==="mediump"&&s.getShaderPrecisionFormat(s.VERTEX_SHADER,s.MEDIUM_FLOAT).precision>0&&s.getShaderPrecisionFormat(s.FRAGMENT_SHADER,s.MEDIUM_FLOAT).precision>0?"mediump":"lowp"}let c=t.precision!==void 0?t.precision:"highp";const h=l(c);h!==c&&(console.warn("THREE.WebGLRenderer:",c,"not supported, using",h,"instead."),c=h);const d=t.logarithmicDepthBuffer===!0,u=s.getParameter(s.MAX_TEXTURE_IMAGE_UNITS),f=s.getParameter(s.MAX_VERTEX_TEXTURE_IMAGE_UNITS),g=s.getParameter(s.MAX_TEXTURE_SIZE),x=s.getParameter(s.MAX_CUBE_MAP_TEXTURE_SIZE),p=s.getParameter(s.MAX_VERTEX_ATTRIBS),m=s.getParameter(s.MAX_VERTEX_UNIFORM_VECTORS),b=s.getParameter(s.MAX_VARYING_VECTORS),_=s.getParameter(s.MAX_FRAGMENT_UNIFORM_VECTORS),S=f>0,I=s.getParameter(s.MAX_SAMPLES);return{isWebGL2:!0,getMaxAnisotropy:r,getMaxPrecision:l,textureFormatReadable:a,textureTypeReadable:o,precision:c,logarithmicDepthBuffer:d,maxTextures:u,maxVertexTextures:f,maxTextureSize:g,maxCubemapSize:x,maxAttributes:p,maxVertexUniforms:m,maxVaryings:b,maxFragmentUniforms:_,vertexTextures:S,maxSamples:I}}function g_(s){const e=this;let t=null,n=0,i=!1,r=!1;const a=new vs,o=new at,l={value:null,needsUpdate:!1};this.uniform=l,this.numPlanes=0,this.numIntersection=0,this.init=function(d,u){const f=d.length!==0||u||n!==0||i;return i=u,n=d.length,f},this.beginShadows=function(){r=!0,h(null)},this.endShadows=function(){r=!1},this.setGlobalState=function(d,u){t=h(d,u,0)},this.setState=function(d,u,f){const g=d.clippingPlanes,x=d.clipIntersection,p=d.clipShadows,m=s.get(d);if(!i||g===null||g.length===0||r&&!p)r?h(null):c();else{const b=r?0:n,_=b*4;let S=m.clippingState||null;l.value=S,S=h(g,u,_,f);for(let I=0;I!==_;++I)S[I]=t[I];m.clippingState=S,this.numIntersection=x?this.numPlanes:0,this.numPlanes+=b}};function c(){l.value!==t&&(l.value=t,l.needsUpdate=n>0),e.numPlanes=n,e.numIntersection=0}function h(d,u,f,g){const x=d!==null?d.length:0;let p=null;if(x!==0){if(p=l.value,g!==!0||p===null){const m=f+x*4,b=u.matrixWorldInverse;o.getNormalMatrix(b),(p===null||p.length<m)&&(p=new Float32Array(m));for(let _=0,S=f;_!==x;++_,S+=4)a.copy(d[_]).applyMatrix4(b,o),a.normal.toArray(p,S),p[S+3]=a.constant}l.value=p,l.needsUpdate=!0}return e.numPlanes=x,e.numIntersection=0,p}}function x_(s){let e=new WeakMap;function t(a,o){return o===Vc?a.mapping=Zr:o===Gc&&(a.mapping=Qr),a}function n(a){if(a&&a.isTexture){const o=a.mapping;if(o===Vc||o===Gc)if(e.has(a)){const l=e.get(a).texture;return t(l,a.mapping)}else{const l=a.image;if(l&&l.height>0){const c=new Cx(l.height);return c.fromEquirectangularTexture(s,a),e.set(a,c),a.addEventListener("dispose",i),t(c.texture,a.mapping)}else return null}}return a}function i(a){const o=a.target;o.removeEventListener("dispose",i);const l=e.get(o);l!==void 0&&(e.delete(o),l.dispose())}function r(){e=new WeakMap}return{get:n,dispose:r}}class $a extends gp{constructor(e=-1,t=1,n=1,i=-1,r=.1,a=2e3){super(),this.isOrthographicCamera=!0,this.type="OrthographicCamera",this.zoom=1,this.view=null,this.left=e,this.right=t,this.top=n,this.bottom=i,this.near=r,this.far=a,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.left=e.left,this.right=e.right,this.top=e.top,this.bottom=e.bottom,this.near=e.near,this.far=e.far,this.zoom=e.zoom,this.view=e.view===null?null:Object.assign({},e.view),this}setViewOffset(e,t,n,i,r,a){this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=n,this.view.offsetY=i,this.view.width=r,this.view.height=a,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const e=(this.right-this.left)/(2*this.zoom),t=(this.top-this.bottom)/(2*this.zoom),n=(this.right+this.left)/2,i=(this.top+this.bottom)/2;let r=n-e,a=n+e,o=i+t,l=i-t;if(this.view!==null&&this.view.enabled){const c=(this.right-this.left)/this.view.fullWidth/this.zoom,h=(this.top-this.bottom)/this.view.fullHeight/this.zoom;r+=c*this.view.offsetX,a=r+c*this.view.width,o-=h*this.view.offsetY,l=o-h*this.view.height}this.projectionMatrix.makeOrthographic(r,a,o,l,this.near,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){const t=super.toJSON(e);return t.object.zoom=this.zoom,t.object.left=this.left,t.object.right=this.right,t.object.top=this.top,t.object.bottom=this.bottom,t.object.near=this.near,t.object.far=this.far,this.view!==null&&(t.object.view=Object.assign({},this.view)),t}}const Gr=4,cu=[.125,.215,.35,.446,.526,.582],Xs=20,gc=new $a,hu=new nt;let xc=null,vc=0,_c=0,yc=!1;const Gs=(1+Math.sqrt(5))/2,Ir=1/Gs,du=[new V(-Gs,Ir,0),new V(Gs,Ir,0),new V(-Ir,0,Gs),new V(Ir,0,Gs),new V(0,Gs,-Ir),new V(0,Gs,Ir),new V(-1,1,-1),new V(1,1,-1),new V(-1,1,1),new V(1,1,1)];class uu{constructor(e){this._renderer=e,this._pingPongRenderTarget=null,this._lodMax=0,this._cubeSize=0,this._lodPlanes=[],this._sizeLods=[],this._sigmas=[],this._blurMaterial=null,this._cubemapMaterial=null,this._equirectMaterial=null,this._compileMaterial(this._blurMaterial)}fromScene(e,t=0,n=.1,i=100){xc=this._renderer.getRenderTarget(),vc=this._renderer.getActiveCubeFace(),_c=this._renderer.getActiveMipmapLevel(),yc=this._renderer.xr.enabled,this._renderer.xr.enabled=!1,this._setSize(256);const r=this._allocateTargets();return r.depthBuffer=!0,this._sceneToCubeUV(e,n,i,r),t>0&&this._blur(r,0,0,t),this._applyPMREM(r),this._cleanup(r),r}fromEquirectangular(e,t=null){return this._fromTexture(e,t)}fromCubemap(e,t=null){return this._fromTexture(e,t)}compileCubemapShader(){this._cubemapMaterial===null&&(this._cubemapMaterial=mu(),this._compileMaterial(this._cubemapMaterial))}compileEquirectangularShader(){this._equirectMaterial===null&&(this._equirectMaterial=pu(),this._compileMaterial(this._equirectMaterial))}dispose(){this._dispose(),this._cubemapMaterial!==null&&this._cubemapMaterial.dispose(),this._equirectMaterial!==null&&this._equirectMaterial.dispose()}_setSize(e){this._lodMax=Math.floor(Math.log2(e)),this._cubeSize=Math.pow(2,this._lodMax)}_dispose(){this._blurMaterial!==null&&this._blurMaterial.dispose(),this._pingPongRenderTarget!==null&&this._pingPongRenderTarget.dispose();for(let e=0;e<this._lodPlanes.length;e++)this._lodPlanes[e].dispose()}_cleanup(e){this._renderer.setRenderTarget(xc,vc,_c),this._renderer.xr.enabled=yc,e.scissorTest=!1,No(e,0,0,e.width,e.height)}_fromTexture(e,t){e.mapping===Zr||e.mapping===Qr?this._setSize(e.image.length===0?16:e.image[0].width||e.image[0].image.width):this._setSize(e.image.width/4),xc=this._renderer.getRenderTarget(),vc=this._renderer.getActiveCubeFace(),_c=this._renderer.getActiveMipmapLevel(),yc=this._renderer.xr.enabled,this._renderer.xr.enabled=!1;const n=t||this._allocateTargets();return this._textureToCubeUV(e,n),this._applyPMREM(n),this._cleanup(n),n}_allocateTargets(){const e=3*Math.max(this._cubeSize,112),t=4*this._cubeSize,n={magFilter:mi,minFilter:mi,generateMipmaps:!1,type:eo,format:vi,colorSpace:Ps,depthBuffer:!1},i=fu(e,t,n);if(this._pingPongRenderTarget===null||this._pingPongRenderTarget.width!==e||this._pingPongRenderTarget.height!==t){this._pingPongRenderTarget!==null&&this._dispose(),this._pingPongRenderTarget=fu(e,t,n);const{_lodMax:r}=this;({sizeLods:this._sizeLods,lodPlanes:this._lodPlanes,sigmas:this._sigmas}=v_(r)),this._blurMaterial=__(r,e,t)}return i}_compileMaterial(e){const t=new Xt(this._lodPlanes[0],e);this._renderer.compile(t,gc)}_sceneToCubeUV(e,t,n,i){const o=new An(90,1,t,n),l=[1,-1,1,1,1,1],c=[1,1,1,-1,-1,-1],h=this._renderer,d=h.autoClear,u=h.toneMapping;h.getClearColor(hu),h.toneMapping=Ss,h.autoClear=!1;const f=new es({name:"PMREM.Background",side:zn,depthWrite:!1,depthTest:!1}),g=new Xt(new _i,f);let x=!1;const p=e.background;p?p.isColor&&(f.color.copy(p),e.background=null,x=!0):(f.color.copy(hu),x=!0);for(let m=0;m<6;m++){const b=m%3;b===0?(o.up.set(0,l[m],0),o.lookAt(c[m],0,0)):b===1?(o.up.set(0,0,l[m]),o.lookAt(0,c[m],0)):(o.up.set(0,l[m],0),o.lookAt(0,0,c[m]));const _=this._cubeSize;No(i,b*_,m>2?_:0,_,_),h.setRenderTarget(i),x&&h.render(g,o),h.render(e,o)}g.geometry.dispose(),g.material.dispose(),h.toneMapping=u,h.autoClear=d,e.background=p}_textureToCubeUV(e,t){const n=this._renderer,i=e.mapping===Zr||e.mapping===Qr;i?(this._cubemapMaterial===null&&(this._cubemapMaterial=mu()),this._cubemapMaterial.uniforms.flipEnvMap.value=e.isRenderTargetTexture===!1?-1:1):this._equirectMaterial===null&&(this._equirectMaterial=pu());const r=i?this._cubemapMaterial:this._equirectMaterial,a=new Xt(this._lodPlanes[0],r),o=r.uniforms;o.envMap.value=e;const l=this._cubeSize;No(t,0,0,3*l,2*l),n.setRenderTarget(t),n.render(a,gc)}_applyPMREM(e){const t=this._renderer,n=t.autoClear;t.autoClear=!1;const i=this._lodPlanes.length;for(let r=1;r<i;r++){const a=Math.sqrt(this._sigmas[r]*this._sigmas[r]-this._sigmas[r-1]*this._sigmas[r-1]),o=du[(i-r-1)%du.length];this._blur(e,r-1,r,a,o)}t.autoClear=n}_blur(e,t,n,i,r){const a=this._pingPongRenderTarget;this._halfBlur(e,a,t,n,i,"latitudinal",r),this._halfBlur(a,e,n,n,i,"longitudinal",r)}_halfBlur(e,t,n,i,r,a,o){const l=this._renderer,c=this._blurMaterial;a!=="latitudinal"&&a!=="longitudinal"&&console.error("blur direction must be either latitudinal or longitudinal!");const h=3,d=new Xt(this._lodPlanes[i],c),u=c.uniforms,f=this._sizeLods[n]-1,g=isFinite(r)?Math.PI/(2*f):2*Math.PI/(2*Xs-1),x=r/g,p=isFinite(r)?1+Math.floor(h*x):Xs;p>Xs&&console.warn(`sigmaRadians, ${r}, is too large and will clip, as it requested ${p} samples when the maximum is set to ${Xs}`);const m=[];let b=0;for(let R=0;R<Xs;++R){const N=R/x,M=Math.exp(-N*N/2);m.push(M),R===0?b+=M:R<p&&(b+=2*M)}for(let R=0;R<m.length;R++)m[R]=m[R]/b;u.envMap.value=e.texture,u.samples.value=p,u.weights.value=m,u.latitudinal.value=a==="latitudinal",o&&(u.poleAxis.value=o);const{_lodMax:_}=this;u.dTheta.value=g,u.mipInt.value=_-n;const S=this._sizeLods[i],I=3*S*(i>_-Gr?i-_+Gr:0),A=4*(this._cubeSize-S);No(t,I,A,3*S,2*S),l.setRenderTarget(t),l.render(d,gc)}}function v_(s){const e=[],t=[],n=[];let i=s;const r=s-Gr+1+cu.length;for(let a=0;a<r;a++){const o=Math.pow(2,i);t.push(o);let l=1/o;a>s-Gr?l=cu[a-s+Gr-1]:a===0&&(l=0),n.push(l);const c=1/(o-2),h=-c,d=1+c,u=[h,h,d,h,d,d,h,h,d,d,h,d],f=6,g=6,x=3,p=2,m=1,b=new Float32Array(x*g*f),_=new Float32Array(p*g*f),S=new Float32Array(m*g*f);for(let A=0;A<f;A++){const R=A%3*2/3-1,N=A>2?0:-1,M=[R,N,0,R+2/3,N,0,R+2/3,N+1,0,R,N,0,R+2/3,N+1,0,R,N+1,0];b.set(M,x*g*A),_.set(u,p*g*A);const y=[A,A,A,A,A,A];S.set(y,m*g*A)}const I=new Jt;I.setAttribute("position",new bi(b,x)),I.setAttribute("uv",new bi(_,p)),I.setAttribute("faceIndex",new bi(S,m)),e.push(I),i>Gr&&i--}return{lodPlanes:e,sizeLods:t,sigmas:n}}function fu(s,e,t){const n=new er(s,e,t);return n.texture.mapping=vl,n.texture.name="PMREM.cubeUv",n.scissorTest=!0,n}function No(s,e,t,n,i){s.viewport.set(e,t,n,i),s.scissor.set(e,t,n,i)}function __(s,e,t){const n=new Float32Array(Xs),i=new V(0,1,0);return new Ts({name:"SphericalGaussianBlur",defines:{n:Xs,CUBEUV_TEXEL_WIDTH:1/e,CUBEUV_TEXEL_HEIGHT:1/t,CUBEUV_MAX_MIP:`${s}.0`},uniforms:{envMap:{value:null},samples:{value:1},weights:{value:n},latitudinal:{value:!1},dTheta:{value:0},mipInt:{value:0},poleAxis:{value:i}},vertexShader:qh(),fragmentShader:`

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
		`,blending:bs,depthTest:!1,depthWrite:!1})}function pu(){return new Ts({name:"EquirectangularToCubeUV",uniforms:{envMap:{value:null}},vertexShader:qh(),fragmentShader:`

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
		`,blending:bs,depthTest:!1,depthWrite:!1})}function mu(){return new Ts({name:"CubemapToCubeUV",uniforms:{envMap:{value:null},flipEnvMap:{value:-1}},vertexShader:qh(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			uniform float flipEnvMap;

			varying vec3 vOutputDirection;

			uniform samplerCube envMap;

			void main() {

				gl_FragColor = textureCube( envMap, vec3( flipEnvMap * vOutputDirection.x, vOutputDirection.yz ) );

			}
		`,blending:bs,depthTest:!1,depthWrite:!1})}function qh(){return`

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
	`}function y_(s){let e=new WeakMap,t=null;function n(o){if(o&&o.isTexture){const l=o.mapping,c=l===Vc||l===Gc,h=l===Zr||l===Qr;if(c||h){let d=e.get(o);const u=d!==void 0?d.texture.pmremVersion:0;if(o.isRenderTargetTexture&&o.pmremVersion!==u)return t===null&&(t=new uu(s)),d=c?t.fromEquirectangular(o,d):t.fromCubemap(o,d),d.texture.pmremVersion=o.pmremVersion,e.set(o,d),d.texture;if(d!==void 0)return d.texture;{const f=o.image;return c&&f&&f.height>0||h&&f&&i(f)?(t===null&&(t=new uu(s)),d=c?t.fromEquirectangular(o):t.fromCubemap(o),d.texture.pmremVersion=o.pmremVersion,e.set(o,d),o.addEventListener("dispose",r),d.texture):null}}}return o}function i(o){let l=0;const c=6;for(let h=0;h<c;h++)o[h]!==void 0&&l++;return l===c}function r(o){const l=o.target;l.removeEventListener("dispose",r);const c=e.get(l);c!==void 0&&(e.delete(l),c.dispose())}function a(){e=new WeakMap,t!==null&&(t.dispose(),t=null)}return{get:n,dispose:a}}function b_(s){const e={};function t(n){if(e[n]!==void 0)return e[n];let i;switch(n){case"WEBGL_depth_texture":i=s.getExtension("WEBGL_depth_texture")||s.getExtension("MOZ_WEBGL_depth_texture")||s.getExtension("WEBKIT_WEBGL_depth_texture");break;case"EXT_texture_filter_anisotropic":i=s.getExtension("EXT_texture_filter_anisotropic")||s.getExtension("MOZ_EXT_texture_filter_anisotropic")||s.getExtension("WEBKIT_EXT_texture_filter_anisotropic");break;case"WEBGL_compressed_texture_s3tc":i=s.getExtension("WEBGL_compressed_texture_s3tc")||s.getExtension("MOZ_WEBGL_compressed_texture_s3tc")||s.getExtension("WEBKIT_WEBGL_compressed_texture_s3tc");break;case"WEBGL_compressed_texture_pvrtc":i=s.getExtension("WEBGL_compressed_texture_pvrtc")||s.getExtension("WEBKIT_WEBGL_compressed_texture_pvrtc");break;default:i=s.getExtension(n)}return e[n]=i,i}return{has:function(n){return t(n)!==null},init:function(){t("EXT_color_buffer_float"),t("WEBGL_clip_cull_distance"),t("OES_texture_float_linear"),t("EXT_color_buffer_half_float"),t("WEBGL_multisampled_render_to_texture"),t("WEBGL_render_shared_exponent")},get:function(n){const i=t(n);return i===null&&Xr("THREE.WebGLRenderer: "+n+" extension not supported."),i}}}function S_(s,e,t,n){const i={},r=new WeakMap;function a(d){const u=d.target;u.index!==null&&e.remove(u.index);for(const g in u.attributes)e.remove(u.attributes[g]);for(const g in u.morphAttributes){const x=u.morphAttributes[g];for(let p=0,m=x.length;p<m;p++)e.remove(x[p])}u.removeEventListener("dispose",a),delete i[u.id];const f=r.get(u);f&&(e.remove(f),r.delete(u)),n.releaseStatesOfGeometry(u),u.isInstancedBufferGeometry===!0&&delete u._maxInstanceCount,t.memory.geometries--}function o(d,u){return i[u.id]===!0||(u.addEventListener("dispose",a),i[u.id]=!0,t.memory.geometries++),u}function l(d){const u=d.attributes;for(const g in u)e.update(u[g],s.ARRAY_BUFFER);const f=d.morphAttributes;for(const g in f){const x=f[g];for(let p=0,m=x.length;p<m;p++)e.update(x[p],s.ARRAY_BUFFER)}}function c(d){const u=[],f=d.index,g=d.attributes.position;let x=0;if(f!==null){const b=f.array;x=f.version;for(let _=0,S=b.length;_<S;_+=3){const I=b[_+0],A=b[_+1],R=b[_+2];u.push(I,A,A,R,R,I)}}else if(g!==void 0){const b=g.array;x=g.version;for(let _=0,S=b.length/3-1;_<S;_+=3){const I=_+0,A=_+1,R=_+2;u.push(I,A,A,R,R,I)}}else return;const p=new(cp(u)?pp:fp)(u,1);p.version=x;const m=r.get(d);m&&e.remove(m),r.set(d,p)}function h(d){const u=r.get(d);if(u){const f=d.index;f!==null&&u.version<f.version&&c(d)}else c(d);return r.get(d)}return{get:o,update:l,getWireframeAttribute:h}}function M_(s,e,t){let n;function i(u){n=u}let r,a;function o(u){r=u.type,a=u.bytesPerElement}function l(u,f){s.drawElements(n,f,r,u*a),t.update(f,n,1)}function c(u,f,g){g!==0&&(s.drawElementsInstanced(n,f,r,u*a,g),t.update(f,n,g))}function h(u,f,g){if(g===0)return;e.get("WEBGL_multi_draw").multiDrawElementsWEBGL(n,f,0,r,u,0,g);let p=0;for(let m=0;m<g;m++)p+=f[m];t.update(p,n,1)}function d(u,f,g,x){if(g===0)return;const p=e.get("WEBGL_multi_draw");if(p===null)for(let m=0;m<u.length;m++)c(u[m]/a,f[m],x[m]);else{p.multiDrawElementsInstancedWEBGL(n,f,0,r,u,0,x,0,g);let m=0;for(let b=0;b<g;b++)m+=f[b];for(let b=0;b<x.length;b++)t.update(m,n,x[b])}}this.setMode=i,this.setIndex=o,this.render=l,this.renderInstances=c,this.renderMultiDraw=h,this.renderMultiDrawInstances=d}function w_(s){const e={geometries:0,textures:0},t={frame:0,calls:0,triangles:0,points:0,lines:0};function n(r,a,o){switch(t.calls++,a){case s.TRIANGLES:t.triangles+=o*(r/3);break;case s.LINES:t.lines+=o*(r/2);break;case s.LINE_STRIP:t.lines+=o*(r-1);break;case s.LINE_LOOP:t.lines+=o*r;break;case s.POINTS:t.points+=o*r;break;default:console.error("THREE.WebGLInfo: Unknown draw mode:",a);break}}function i(){t.calls=0,t.triangles=0,t.points=0,t.lines=0}return{memory:e,render:t,programs:null,autoReset:!0,reset:i,update:n}}function E_(s,e,t){const n=new WeakMap,i=new rn;function r(a,o,l){const c=a.morphTargetInfluences,h=o.morphAttributes.position||o.morphAttributes.normal||o.morphAttributes.color,d=h!==void 0?h.length:0;let u=n.get(o);if(u===void 0||u.count!==d){let y=function(){N.dispose(),n.delete(o),o.removeEventListener("dispose",y)};var f=y;u!==void 0&&u.texture.dispose();const g=o.morphAttributes.position!==void 0,x=o.morphAttributes.normal!==void 0,p=o.morphAttributes.color!==void 0,m=o.morphAttributes.position||[],b=o.morphAttributes.normal||[],_=o.morphAttributes.color||[];let S=0;g===!0&&(S=1),x===!0&&(S=2),p===!0&&(S=3);let I=o.attributes.position.count*S,A=1;I>e.maxTextureSize&&(A=Math.ceil(I/e.maxTextureSize),I=e.maxTextureSize);const R=new Float32Array(I*A*4*d),N=new dp(R,I,A,d);N.type=Ki,N.needsUpdate=!0;const M=S*4;for(let P=0;P<d;P++){const X=m[P],H=b[P],J=_[P],q=I*A*4*P;for(let ee=0;ee<X.count;ee++){const j=ee*M;g===!0&&(i.fromBufferAttribute(X,ee),R[q+j+0]=i.x,R[q+j+1]=i.y,R[q+j+2]=i.z,R[q+j+3]=0),x===!0&&(i.fromBufferAttribute(H,ee),R[q+j+4]=i.x,R[q+j+5]=i.y,R[q+j+6]=i.z,R[q+j+7]=0),p===!0&&(i.fromBufferAttribute(J,ee),R[q+j+8]=i.x,R[q+j+9]=i.y,R[q+j+10]=i.z,R[q+j+11]=J.itemSize===4?i.w:1)}}u={count:d,texture:N,size:new Xe(I,A)},n.set(o,u),o.addEventListener("dispose",y)}if(a.isInstancedMesh===!0&&a.morphTexture!==null)l.getUniforms().setValue(s,"morphTexture",a.morphTexture,t);else{let g=0;for(let p=0;p<c.length;p++)g+=c[p];const x=o.morphTargetsRelative?1:1-g;l.getUniforms().setValue(s,"morphTargetBaseInfluence",x),l.getUniforms().setValue(s,"morphTargetInfluences",c)}l.getUniforms().setValue(s,"morphTargetsTexture",u.texture,t),l.getUniforms().setValue(s,"morphTargetsTextureSize",u.size)}return{update:r}}function T_(s,e,t,n){let i=new WeakMap;function r(l){const c=n.render.frame,h=l.geometry,d=e.get(l,h);if(i.get(d)!==c&&(e.update(d),i.set(d,c)),l.isInstancedMesh&&(l.hasEventListener("dispose",o)===!1&&l.addEventListener("dispose",o),i.get(l)!==c&&(t.update(l.instanceMatrix,s.ARRAY_BUFFER),l.instanceColor!==null&&t.update(l.instanceColor,s.ARRAY_BUFFER),i.set(l,c))),l.isSkinnedMesh){const u=l.skeleton;i.get(u)!==c&&(u.update(),i.set(u,c))}return d}function a(){i=new WeakMap}function o(l){const c=l.target;c.removeEventListener("dispose",o),t.remove(c.instanceMatrix),c.instanceColor!==null&&t.remove(c.instanceColor)}return{update:r,dispose:a}}class _p extends On{constructor(e,t,n,i,r,a,o,l,c,h=$r){if(h!==$r&&h!==ta)throw new Error("DepthTexture format must be either THREE.DepthFormat or THREE.DepthStencilFormat");n===void 0&&h===$r&&(n=Qs),n===void 0&&h===ta&&(n=ea),super(null,i,r,a,o,l,h,n,c),this.isDepthTexture=!0,this.image={width:e,height:t},this.magFilter=o!==void 0?o:si,this.minFilter=l!==void 0?l:si,this.flipY=!1,this.generateMipmaps=!1,this.compareFunction=null}copy(e){return super.copy(e),this.compareFunction=e.compareFunction,this}toJSON(e){const t=super.toJSON(e);return this.compareFunction!==null&&(t.compareFunction=this.compareFunction),t}}const yp=new On,gu=new _p(1,1),bp=new dp,Sp=new ux,Mp=new xp,xu=[],vu=[],_u=new Float32Array(16),yu=new Float32Array(9),bu=new Float32Array(4);function ua(s,e,t){const n=s[0];if(n<=0||n>0)return s;const i=e*t;let r=xu[i];if(r===void 0&&(r=new Float32Array(i),xu[i]=r),e!==0){n.toArray(r,0);for(let a=1,o=0;a!==e;++a)o+=t,s[a].toArray(r,o)}return r}function an(s,e){if(s.length!==e.length)return!1;for(let t=0,n=s.length;t<n;t++)if(s[t]!==e[t])return!1;return!0}function on(s,e){for(let t=0,n=e.length;t<n;t++)s[t]=e[t]}function yl(s,e){let t=vu[e];t===void 0&&(t=new Int32Array(e),vu[e]=t);for(let n=0;n!==e;++n)t[n]=s.allocateTextureUnit();return t}function A_(s,e){const t=this.cache;t[0]!==e&&(s.uniform1f(this.addr,e),t[0]=e)}function C_(s,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(s.uniform2f(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(an(t,e))return;s.uniform2fv(this.addr,e),on(t,e)}}function R_(s,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(s.uniform3f(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else if(e.r!==void 0)(t[0]!==e.r||t[1]!==e.g||t[2]!==e.b)&&(s.uniform3f(this.addr,e.r,e.g,e.b),t[0]=e.r,t[1]=e.g,t[2]=e.b);else{if(an(t,e))return;s.uniform3fv(this.addr,e),on(t,e)}}function P_(s,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(s.uniform4f(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(an(t,e))return;s.uniform4fv(this.addr,e),on(t,e)}}function L_(s,e){const t=this.cache,n=e.elements;if(n===void 0){if(an(t,e))return;s.uniformMatrix2fv(this.addr,!1,e),on(t,e)}else{if(an(t,n))return;bu.set(n),s.uniformMatrix2fv(this.addr,!1,bu),on(t,n)}}function D_(s,e){const t=this.cache,n=e.elements;if(n===void 0){if(an(t,e))return;s.uniformMatrix3fv(this.addr,!1,e),on(t,e)}else{if(an(t,n))return;yu.set(n),s.uniformMatrix3fv(this.addr,!1,yu),on(t,n)}}function I_(s,e){const t=this.cache,n=e.elements;if(n===void 0){if(an(t,e))return;s.uniformMatrix4fv(this.addr,!1,e),on(t,e)}else{if(an(t,n))return;_u.set(n),s.uniformMatrix4fv(this.addr,!1,_u),on(t,n)}}function U_(s,e){const t=this.cache;t[0]!==e&&(s.uniform1i(this.addr,e),t[0]=e)}function N_(s,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(s.uniform2i(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(an(t,e))return;s.uniform2iv(this.addr,e),on(t,e)}}function F_(s,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(s.uniform3i(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(an(t,e))return;s.uniform3iv(this.addr,e),on(t,e)}}function O_(s,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(s.uniform4i(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(an(t,e))return;s.uniform4iv(this.addr,e),on(t,e)}}function k_(s,e){const t=this.cache;t[0]!==e&&(s.uniform1ui(this.addr,e),t[0]=e)}function B_(s,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(s.uniform2ui(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(an(t,e))return;s.uniform2uiv(this.addr,e),on(t,e)}}function z_(s,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(s.uniform3ui(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(an(t,e))return;s.uniform3uiv(this.addr,e),on(t,e)}}function H_(s,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(s.uniform4ui(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(an(t,e))return;s.uniform4uiv(this.addr,e),on(t,e)}}function V_(s,e,t){const n=this.cache,i=t.allocateTextureUnit();n[0]!==i&&(s.uniform1i(this.addr,i),n[0]=i);let r;this.type===s.SAMPLER_2D_SHADOW?(gu.compareFunction=lp,r=gu):r=yp,t.setTexture2D(e||r,i)}function G_(s,e,t){const n=this.cache,i=t.allocateTextureUnit();n[0]!==i&&(s.uniform1i(this.addr,i),n[0]=i),t.setTexture3D(e||Sp,i)}function W_(s,e,t){const n=this.cache,i=t.allocateTextureUnit();n[0]!==i&&(s.uniform1i(this.addr,i),n[0]=i),t.setTextureCube(e||Mp,i)}function $_(s,e,t){const n=this.cache,i=t.allocateTextureUnit();n[0]!==i&&(s.uniform1i(this.addr,i),n[0]=i),t.setTexture2DArray(e||bp,i)}function q_(s){switch(s){case 5126:return A_;case 35664:return C_;case 35665:return R_;case 35666:return P_;case 35674:return L_;case 35675:return D_;case 35676:return I_;case 5124:case 35670:return U_;case 35667:case 35671:return N_;case 35668:case 35672:return F_;case 35669:case 35673:return O_;case 5125:return k_;case 36294:return B_;case 36295:return z_;case 36296:return H_;case 35678:case 36198:case 36298:case 36306:case 35682:return V_;case 35679:case 36299:case 36307:return G_;case 35680:case 36300:case 36308:case 36293:return W_;case 36289:case 36303:case 36311:case 36292:return $_}}function X_(s,e){s.uniform1fv(this.addr,e)}function Y_(s,e){const t=ua(e,this.size,2);s.uniform2fv(this.addr,t)}function j_(s,e){const t=ua(e,this.size,3);s.uniform3fv(this.addr,t)}function K_(s,e){const t=ua(e,this.size,4);s.uniform4fv(this.addr,t)}function J_(s,e){const t=ua(e,this.size,4);s.uniformMatrix2fv(this.addr,!1,t)}function Z_(s,e){const t=ua(e,this.size,9);s.uniformMatrix3fv(this.addr,!1,t)}function Q_(s,e){const t=ua(e,this.size,16);s.uniformMatrix4fv(this.addr,!1,t)}function ey(s,e){s.uniform1iv(this.addr,e)}function ty(s,e){s.uniform2iv(this.addr,e)}function ny(s,e){s.uniform3iv(this.addr,e)}function iy(s,e){s.uniform4iv(this.addr,e)}function sy(s,e){s.uniform1uiv(this.addr,e)}function ry(s,e){s.uniform2uiv(this.addr,e)}function ay(s,e){s.uniform3uiv(this.addr,e)}function oy(s,e){s.uniform4uiv(this.addr,e)}function ly(s,e,t){const n=this.cache,i=e.length,r=yl(t,i);an(n,r)||(s.uniform1iv(this.addr,r),on(n,r));for(let a=0;a!==i;++a)t.setTexture2D(e[a]||yp,r[a])}function cy(s,e,t){const n=this.cache,i=e.length,r=yl(t,i);an(n,r)||(s.uniform1iv(this.addr,r),on(n,r));for(let a=0;a!==i;++a)t.setTexture3D(e[a]||Sp,r[a])}function hy(s,e,t){const n=this.cache,i=e.length,r=yl(t,i);an(n,r)||(s.uniform1iv(this.addr,r),on(n,r));for(let a=0;a!==i;++a)t.setTextureCube(e[a]||Mp,r[a])}function dy(s,e,t){const n=this.cache,i=e.length,r=yl(t,i);an(n,r)||(s.uniform1iv(this.addr,r),on(n,r));for(let a=0;a!==i;++a)t.setTexture2DArray(e[a]||bp,r[a])}function uy(s){switch(s){case 5126:return X_;case 35664:return Y_;case 35665:return j_;case 35666:return K_;case 35674:return J_;case 35675:return Z_;case 35676:return Q_;case 5124:case 35670:return ey;case 35667:case 35671:return ty;case 35668:case 35672:return ny;case 35669:case 35673:return iy;case 5125:return sy;case 36294:return ry;case 36295:return ay;case 36296:return oy;case 35678:case 36198:case 36298:case 36306:case 35682:return ly;case 35679:case 36299:case 36307:return cy;case 35680:case 36300:case 36308:case 36293:return hy;case 36289:case 36303:case 36311:case 36292:return dy}}class fy{constructor(e,t,n){this.id=e,this.addr=n,this.cache=[],this.type=t.type,this.setValue=q_(t.type)}}class py{constructor(e,t,n){this.id=e,this.addr=n,this.cache=[],this.type=t.type,this.size=t.size,this.setValue=uy(t.type)}}class my{constructor(e){this.id=e,this.seq=[],this.map={}}setValue(e,t,n){const i=this.seq;for(let r=0,a=i.length;r!==a;++r){const o=i[r];o.setValue(e,t[o.id],n)}}}const bc=/(\w+)(\])?(\[|\.)?/g;function Su(s,e){s.seq.push(e),s.map[e.id]=e}function gy(s,e,t){const n=s.name,i=n.length;for(bc.lastIndex=0;;){const r=bc.exec(n),a=bc.lastIndex;let o=r[1];const l=r[2]==="]",c=r[3];if(l&&(o=o|0),c===void 0||c==="["&&a+2===i){Su(t,c===void 0?new fy(o,s,e):new py(o,s,e));break}else{let d=t.map[o];d===void 0&&(d=new my(o),Su(t,d)),t=d}}}class il{constructor(e,t){this.seq=[],this.map={};const n=e.getProgramParameter(t,e.ACTIVE_UNIFORMS);for(let i=0;i<n;++i){const r=e.getActiveUniform(t,i),a=e.getUniformLocation(t,r.name);gy(r,a,this)}}setValue(e,t,n,i){const r=this.map[t];r!==void 0&&r.setValue(e,n,i)}setOptional(e,t,n){const i=t[n];i!==void 0&&this.setValue(e,n,i)}static upload(e,t,n,i){for(let r=0,a=t.length;r!==a;++r){const o=t[r],l=n[o.id];l.needsUpdate!==!1&&o.setValue(e,l.value,i)}}static seqWithValue(e,t){const n=[];for(let i=0,r=e.length;i!==r;++i){const a=e[i];a.id in t&&n.push(a)}return n}}function Mu(s,e,t){const n=s.createShader(e);return s.shaderSource(n,t),s.compileShader(n),n}const xy=37297;let vy=0;function _y(s,e){const t=s.split(`
`),n=[],i=Math.max(e-6,0),r=Math.min(e+6,t.length);for(let a=i;a<r;a++){const o=a+1;n.push(`${o===e?">":" "} ${o}: ${t[a]}`)}return n.join(`
`)}function yy(s){const e=Mt.getPrimaries(Mt.workingColorSpace),t=Mt.getPrimaries(s);let n;switch(e===t?n="":e===ll&&t===ol?n="LinearDisplayP3ToLinearSRGB":e===ol&&t===ll&&(n="LinearSRGBToLinearDisplayP3"),s){case Ps:case _l:return[n,"LinearTransferOETF"];case Di:case Vh:return[n,"sRGBTransferOETF"];default:return console.warn("THREE.WebGLProgram: Unsupported color space:",s),[n,"LinearTransferOETF"]}}function wu(s,e,t){const n=s.getShaderParameter(e,s.COMPILE_STATUS),i=s.getShaderInfoLog(e).trim();if(n&&i==="")return"";const r=/ERROR: 0:(\d+)/.exec(i);if(r){const a=parseInt(r[1]);return t.toUpperCase()+`

`+i+`

`+_y(s.getShaderSource(e),a)}else return i}function by(s,e){const t=yy(e);return`vec4 ${s}( vec4 value ) { return ${t[0]}( ${t[1]}( value ) ); }`}function Sy(s,e){let t;switch(e){case Eg:t="Linear";break;case Tg:t="Reinhard";break;case Ag:t="Cineon";break;case jf:t="ACESFilmic";break;case Rg:t="AgX";break;case Pg:t="Neutral";break;case Cg:t="Custom";break;default:console.warn("THREE.WebGLProgram: Unsupported toneMapping:",e),t="Linear"}return"vec3 "+s+"( vec3 color ) { return "+t+"ToneMapping( color ); }"}const Fo=new V;function My(){Mt.getLuminanceCoefficients(Fo);const s=Fo.x.toFixed(4),e=Fo.y.toFixed(4),t=Fo.z.toFixed(4);return["float luminance( const in vec3 rgb ) {",`	const vec3 weights = vec3( ${s}, ${e}, ${t} );`,"	return dot( weights, rgb );","}"].join(`
`)}function wy(s){return[s.extensionClipCullDistance?"#extension GL_ANGLE_clip_cull_distance : require":"",s.extensionMultiDraw?"#extension GL_ANGLE_multi_draw : require":""].filter(za).join(`
`)}function Ey(s){const e=[];for(const t in s){const n=s[t];n!==!1&&e.push("#define "+t+" "+n)}return e.join(`
`)}function Ty(s,e){const t={},n=s.getProgramParameter(e,s.ACTIVE_ATTRIBUTES);for(let i=0;i<n;i++){const r=s.getActiveAttrib(e,i),a=r.name;let o=1;r.type===s.FLOAT_MAT2&&(o=2),r.type===s.FLOAT_MAT3&&(o=3),r.type===s.FLOAT_MAT4&&(o=4),t[a]={type:r.type,location:s.getAttribLocation(e,a),locationSize:o}}return t}function za(s){return s!==""}function Eu(s,e){const t=e.numSpotLightShadows+e.numSpotLightMaps-e.numSpotLightShadowsWithMaps;return s.replace(/NUM_DIR_LIGHTS/g,e.numDirLights).replace(/NUM_SPOT_LIGHTS/g,e.numSpotLights).replace(/NUM_SPOT_LIGHT_MAPS/g,e.numSpotLightMaps).replace(/NUM_SPOT_LIGHT_COORDS/g,t).replace(/NUM_RECT_AREA_LIGHTS/g,e.numRectAreaLights).replace(/NUM_POINT_LIGHTS/g,e.numPointLights).replace(/NUM_HEMI_LIGHTS/g,e.numHemiLights).replace(/NUM_DIR_LIGHT_SHADOWS/g,e.numDirLightShadows).replace(/NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS/g,e.numSpotLightShadowsWithMaps).replace(/NUM_SPOT_LIGHT_SHADOWS/g,e.numSpotLightShadows).replace(/NUM_POINT_LIGHT_SHADOWS/g,e.numPointLightShadows)}function Tu(s,e){return s.replace(/NUM_CLIPPING_PLANES/g,e.numClippingPlanes).replace(/UNION_CLIPPING_PLANES/g,e.numClippingPlanes-e.numClipIntersection)}const Ay=/^[ \t]*#include +<([\w\d./]+)>/gm;function _h(s){return s.replace(Ay,Ry)}const Cy=new Map;function Ry(s,e){let t=rt[e];if(t===void 0){const n=Cy.get(e);if(n!==void 0)t=rt[n],console.warn('THREE.WebGLRenderer: Shader chunk "%s" has been deprecated. Use "%s" instead.',e,n);else throw new Error("Can not resolve #include <"+e+">")}return _h(t)}const Py=/#pragma unroll_loop_start\s+for\s*\(\s*int\s+i\s*=\s*(\d+)\s*;\s*i\s*<\s*(\d+)\s*;\s*i\s*\+\+\s*\)\s*{([\s\S]+?)}\s+#pragma unroll_loop_end/g;function Au(s){return s.replace(Py,Ly)}function Ly(s,e,t,n){let i="";for(let r=parseInt(e);r<parseInt(t);r++)i+=n.replace(/\[\s*i\s*\]/g,"[ "+r+" ]").replace(/UNROLLED_LOOP_INDEX/g,r);return i}function Cu(s){let e=`precision ${s.precision} float;
	precision ${s.precision} int;
	precision ${s.precision} sampler2D;
	precision ${s.precision} samplerCube;
	precision ${s.precision} sampler3D;
	precision ${s.precision} sampler2DArray;
	precision ${s.precision} sampler2DShadow;
	precision ${s.precision} samplerCubeShadow;
	precision ${s.precision} sampler2DArrayShadow;
	precision ${s.precision} isampler2D;
	precision ${s.precision} isampler3D;
	precision ${s.precision} isamplerCube;
	precision ${s.precision} isampler2DArray;
	precision ${s.precision} usampler2D;
	precision ${s.precision} usampler3D;
	precision ${s.precision} usamplerCube;
	precision ${s.precision} usampler2DArray;
	`;return s.precision==="highp"?e+=`
#define HIGH_PRECISION`:s.precision==="mediump"?e+=`
#define MEDIUM_PRECISION`:s.precision==="lowp"&&(e+=`
#define LOW_PRECISION`),e}function Dy(s){let e="SHADOWMAP_TYPE_BASIC";return s.shadowMapType===qf?e="SHADOWMAP_TYPE_PCF":s.shadowMapType===Xf?e="SHADOWMAP_TYPE_PCF_SOFT":s.shadowMapType===Yi&&(e="SHADOWMAP_TYPE_VSM"),e}function Iy(s){let e="ENVMAP_TYPE_CUBE";if(s.envMap)switch(s.envMapMode){case Zr:case Qr:e="ENVMAP_TYPE_CUBE";break;case vl:e="ENVMAP_TYPE_CUBE_UV";break}return e}function Uy(s){let e="ENVMAP_MODE_REFLECTION";if(s.envMap)switch(s.envMapMode){case Qr:e="ENVMAP_MODE_REFRACTION";break}return e}function Ny(s){let e="ENVMAP_BLENDING_NONE";if(s.envMap)switch(s.combine){case Yf:e="ENVMAP_BLENDING_MULTIPLY";break;case Mg:e="ENVMAP_BLENDING_MIX";break;case wg:e="ENVMAP_BLENDING_ADD";break}return e}function Fy(s){const e=s.envMapCubeUVHeight;if(e===null)return null;const t=Math.log2(e)-2,n=1/e;return{texelWidth:1/(3*Math.max(Math.pow(2,t),7*16)),texelHeight:n,maxMip:t}}function Oy(s,e,t,n){const i=s.getContext(),r=t.defines;let a=t.vertexShader,o=t.fragmentShader;const l=Dy(t),c=Iy(t),h=Uy(t),d=Ny(t),u=Fy(t),f=wy(t),g=Ey(r),x=i.createProgram();let p,m,b=t.glslVersion?"#version "+t.glslVersion+`
`:"";t.isRawShaderMaterial?(p=["#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,g].filter(za).join(`
`),p.length>0&&(p+=`
`),m=["#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,g].filter(za).join(`
`),m.length>0&&(m+=`
`)):(p=[Cu(t),"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,g,t.extensionClipCullDistance?"#define USE_CLIP_DISTANCE":"",t.batching?"#define USE_BATCHING":"",t.batchingColor?"#define USE_BATCHING_COLOR":"",t.instancing?"#define USE_INSTANCING":"",t.instancingColor?"#define USE_INSTANCING_COLOR":"",t.instancingMorph?"#define USE_INSTANCING_MORPH":"",t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.map?"#define USE_MAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+h:"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",t.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",t.displacementMap?"#define USE_DISPLACEMENTMAP":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.anisotropy?"#define USE_ANISOTROPY":"",t.anisotropyMap?"#define USE_ANISOTROPYMAP":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",t.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaHash?"#define USE_ALPHAHASH":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",t.mapUv?"#define MAP_UV "+t.mapUv:"",t.alphaMapUv?"#define ALPHAMAP_UV "+t.alphaMapUv:"",t.lightMapUv?"#define LIGHTMAP_UV "+t.lightMapUv:"",t.aoMapUv?"#define AOMAP_UV "+t.aoMapUv:"",t.emissiveMapUv?"#define EMISSIVEMAP_UV "+t.emissiveMapUv:"",t.bumpMapUv?"#define BUMPMAP_UV "+t.bumpMapUv:"",t.normalMapUv?"#define NORMALMAP_UV "+t.normalMapUv:"",t.displacementMapUv?"#define DISPLACEMENTMAP_UV "+t.displacementMapUv:"",t.metalnessMapUv?"#define METALNESSMAP_UV "+t.metalnessMapUv:"",t.roughnessMapUv?"#define ROUGHNESSMAP_UV "+t.roughnessMapUv:"",t.anisotropyMapUv?"#define ANISOTROPYMAP_UV "+t.anisotropyMapUv:"",t.clearcoatMapUv?"#define CLEARCOATMAP_UV "+t.clearcoatMapUv:"",t.clearcoatNormalMapUv?"#define CLEARCOAT_NORMALMAP_UV "+t.clearcoatNormalMapUv:"",t.clearcoatRoughnessMapUv?"#define CLEARCOAT_ROUGHNESSMAP_UV "+t.clearcoatRoughnessMapUv:"",t.iridescenceMapUv?"#define IRIDESCENCEMAP_UV "+t.iridescenceMapUv:"",t.iridescenceThicknessMapUv?"#define IRIDESCENCE_THICKNESSMAP_UV "+t.iridescenceThicknessMapUv:"",t.sheenColorMapUv?"#define SHEEN_COLORMAP_UV "+t.sheenColorMapUv:"",t.sheenRoughnessMapUv?"#define SHEEN_ROUGHNESSMAP_UV "+t.sheenRoughnessMapUv:"",t.specularMapUv?"#define SPECULARMAP_UV "+t.specularMapUv:"",t.specularColorMapUv?"#define SPECULAR_COLORMAP_UV "+t.specularColorMapUv:"",t.specularIntensityMapUv?"#define SPECULAR_INTENSITYMAP_UV "+t.specularIntensityMapUv:"",t.transmissionMapUv?"#define TRANSMISSIONMAP_UV "+t.transmissionMapUv:"",t.thicknessMapUv?"#define THICKNESSMAP_UV "+t.thicknessMapUv:"",t.vertexTangents&&t.flatShading===!1?"#define USE_TANGENT":"",t.vertexColors?"#define USE_COLOR":"",t.vertexAlphas?"#define USE_COLOR_ALPHA":"",t.vertexUv1s?"#define USE_UV1":"",t.vertexUv2s?"#define USE_UV2":"",t.vertexUv3s?"#define USE_UV3":"",t.pointsUvs?"#define USE_POINTS_UV":"",t.flatShading?"#define FLAT_SHADED":"",t.skinning?"#define USE_SKINNING":"",t.morphTargets?"#define USE_MORPHTARGETS":"",t.morphNormals&&t.flatShading===!1?"#define USE_MORPHNORMALS":"",t.morphColors?"#define USE_MORPHCOLORS":"",t.morphTargetsCount>0?"#define MORPHTARGETS_TEXTURE_STRIDE "+t.morphTextureStride:"",t.morphTargetsCount>0?"#define MORPHTARGETS_COUNT "+t.morphTargetsCount:"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+l:"",t.sizeAttenuation?"#define USE_SIZEATTENUATION":"",t.numLightProbes>0?"#define USE_LIGHT_PROBES":"",t.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"","uniform mat4 modelMatrix;","uniform mat4 modelViewMatrix;","uniform mat4 projectionMatrix;","uniform mat4 viewMatrix;","uniform mat3 normalMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;","#ifdef USE_INSTANCING","	attribute mat4 instanceMatrix;","#endif","#ifdef USE_INSTANCING_COLOR","	attribute vec3 instanceColor;","#endif","#ifdef USE_INSTANCING_MORPH","	uniform sampler2D morphTexture;","#endif","attribute vec3 position;","attribute vec3 normal;","attribute vec2 uv;","#ifdef USE_UV1","	attribute vec2 uv1;","#endif","#ifdef USE_UV2","	attribute vec2 uv2;","#endif","#ifdef USE_UV3","	attribute vec2 uv3;","#endif","#ifdef USE_TANGENT","	attribute vec4 tangent;","#endif","#if defined( USE_COLOR_ALPHA )","	attribute vec4 color;","#elif defined( USE_COLOR )","	attribute vec3 color;","#endif","#ifdef USE_SKINNING","	attribute vec4 skinIndex;","	attribute vec4 skinWeight;","#endif",`
`].filter(za).join(`
`),m=[Cu(t),"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,g,t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.alphaToCoverage?"#define ALPHA_TO_COVERAGE":"",t.map?"#define USE_MAP":"",t.matcap?"#define USE_MATCAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+c:"",t.envMap?"#define "+h:"",t.envMap?"#define "+d:"",u?"#define CUBEUV_TEXEL_WIDTH "+u.texelWidth:"",u?"#define CUBEUV_TEXEL_HEIGHT "+u.texelHeight:"",u?"#define CUBEUV_MAX_MIP "+u.maxMip+".0":"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",t.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.anisotropy?"#define USE_ANISOTROPY":"",t.anisotropyMap?"#define USE_ANISOTROPYMAP":"",t.clearcoat?"#define USE_CLEARCOAT":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.dispersion?"#define USE_DISPERSION":"",t.iridescence?"#define USE_IRIDESCENCE":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",t.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaTest?"#define USE_ALPHATEST":"",t.alphaHash?"#define USE_ALPHAHASH":"",t.sheen?"#define USE_SHEEN":"",t.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.vertexTangents&&t.flatShading===!1?"#define USE_TANGENT":"",t.vertexColors||t.instancingColor||t.batchingColor?"#define USE_COLOR":"",t.vertexAlphas?"#define USE_COLOR_ALPHA":"",t.vertexUv1s?"#define USE_UV1":"",t.vertexUv2s?"#define USE_UV2":"",t.vertexUv3s?"#define USE_UV3":"",t.pointsUvs?"#define USE_POINTS_UV":"",t.gradientMap?"#define USE_GRADIENTMAP":"",t.flatShading?"#define FLAT_SHADED":"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+l:"",t.premultipliedAlpha?"#define PREMULTIPLIED_ALPHA":"",t.numLightProbes>0?"#define USE_LIGHT_PROBES":"",t.decodeVideoTexture?"#define DECODE_VIDEO_TEXTURE":"",t.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"","uniform mat4 viewMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;",t.toneMapping!==Ss?"#define TONE_MAPPING":"",t.toneMapping!==Ss?rt.tonemapping_pars_fragment:"",t.toneMapping!==Ss?Sy("toneMapping",t.toneMapping):"",t.dithering?"#define DITHERING":"",t.opaque?"#define OPAQUE":"",rt.colorspace_pars_fragment,by("linearToOutputTexel",t.outputColorSpace),My(),t.useDepthPacking?"#define DEPTH_PACKING "+t.depthPacking:"",`
`].filter(za).join(`
`)),a=_h(a),a=Eu(a,t),a=Tu(a,t),o=_h(o),o=Eu(o,t),o=Tu(o,t),a=Au(a),o=Au(o),t.isRawShaderMaterial!==!0&&(b=`#version 300 es
`,p=[f,"#define attribute in","#define varying out","#define texture2D texture"].join(`
`)+`
`+p,m=["#define varying in",t.glslVersion===Vd?"":"layout(location = 0) out highp vec4 pc_fragColor;",t.glslVersion===Vd?"":"#define gl_FragColor pc_fragColor","#define gl_FragDepthEXT gl_FragDepth","#define texture2D texture","#define textureCube texture","#define texture2DProj textureProj","#define texture2DLodEXT textureLod","#define texture2DProjLodEXT textureProjLod","#define textureCubeLodEXT textureLod","#define texture2DGradEXT textureGrad","#define texture2DProjGradEXT textureProjGrad","#define textureCubeGradEXT textureGrad"].join(`
`)+`
`+m);const _=b+p+a,S=b+m+o,I=Mu(i,i.VERTEX_SHADER,_),A=Mu(i,i.FRAGMENT_SHADER,S);i.attachShader(x,I),i.attachShader(x,A),t.index0AttributeName!==void 0?i.bindAttribLocation(x,0,t.index0AttributeName):t.morphTargets===!0&&i.bindAttribLocation(x,0,"position"),i.linkProgram(x);function R(P){if(s.debug.checkShaderErrors){const X=i.getProgramInfoLog(x).trim(),H=i.getShaderInfoLog(I).trim(),J=i.getShaderInfoLog(A).trim();let q=!0,ee=!0;if(i.getProgramParameter(x,i.LINK_STATUS)===!1)if(q=!1,typeof s.debug.onShaderError=="function")s.debug.onShaderError(i,x,I,A);else{const j=wu(i,I,"vertex"),ne=wu(i,A,"fragment");console.error("THREE.WebGLProgram: Shader Error "+i.getError()+" - VALIDATE_STATUS "+i.getProgramParameter(x,i.VALIDATE_STATUS)+`

Material Name: `+P.name+`
Material Type: `+P.type+`

Program Info Log: `+X+`
`+j+`
`+ne)}else X!==""?console.warn("THREE.WebGLProgram: Program Info Log:",X):(H===""||J==="")&&(ee=!1);ee&&(P.diagnostics={runnable:q,programLog:X,vertexShader:{log:H,prefix:p},fragmentShader:{log:J,prefix:m}})}i.deleteShader(I),i.deleteShader(A),N=new il(i,x),M=Ty(i,x)}let N;this.getUniforms=function(){return N===void 0&&R(this),N};let M;this.getAttributes=function(){return M===void 0&&R(this),M};let y=t.rendererExtensionParallelShaderCompile===!1;return this.isReady=function(){return y===!1&&(y=i.getProgramParameter(x,xy)),y},this.destroy=function(){n.releaseStatesOfProgram(this),i.deleteProgram(x),this.program=void 0},this.type=t.shaderType,this.name=t.shaderName,this.id=vy++,this.cacheKey=e,this.usedTimes=1,this.program=x,this.vertexShader=I,this.fragmentShader=A,this}let ky=0;class By{constructor(){this.shaderCache=new Map,this.materialCache=new Map}update(e){const t=e.vertexShader,n=e.fragmentShader,i=this._getShaderStage(t),r=this._getShaderStage(n),a=this._getShaderCacheForMaterial(e);return a.has(i)===!1&&(a.add(i),i.usedTimes++),a.has(r)===!1&&(a.add(r),r.usedTimes++),this}remove(e){const t=this.materialCache.get(e);for(const n of t)n.usedTimes--,n.usedTimes===0&&this.shaderCache.delete(n.code);return this.materialCache.delete(e),this}getVertexShaderID(e){return this._getShaderStage(e.vertexShader).id}getFragmentShaderID(e){return this._getShaderStage(e.fragmentShader).id}dispose(){this.shaderCache.clear(),this.materialCache.clear()}_getShaderCacheForMaterial(e){const t=this.materialCache;let n=t.get(e);return n===void 0&&(n=new Set,t.set(e,n)),n}_getShaderStage(e){const t=this.shaderCache;let n=t.get(e);return n===void 0&&(n=new zy(e),t.set(e,n)),n}}class zy{constructor(e){this.id=ky++,this.code=e,this.usedTimes=0}}function Hy(s,e,t,n,i,r,a){const o=new Wh,l=new By,c=new Set,h=[],d=i.logarithmicDepthBuffer,u=i.vertexTextures;let f=i.precision;const g={MeshDepthMaterial:"depth",MeshDistanceMaterial:"distanceRGBA",MeshNormalMaterial:"normal",MeshBasicMaterial:"basic",MeshLambertMaterial:"lambert",MeshPhongMaterial:"phong",MeshToonMaterial:"toon",MeshStandardMaterial:"physical",MeshPhysicalMaterial:"physical",MeshMatcapMaterial:"matcap",LineBasicMaterial:"basic",LineDashedMaterial:"dashed",PointsMaterial:"points",ShadowMaterial:"shadow",SpriteMaterial:"sprite"};function x(M){return c.add(M),M===0?"uv":`uv${M}`}function p(M,y,P,X,H){const J=X.fog,q=H.geometry,ee=M.isMeshStandardMaterial?X.environment:null,j=(M.isMeshStandardMaterial?t:e).get(M.envMap||ee),ne=j&&j.mapping===vl?j.image.height:null,ge=g[M.type];M.precision!==null&&(f=i.getMaxPrecision(M.precision),f!==M.precision&&console.warn("THREE.WebGLProgram.getParameters:",M.precision,"not supported, using",f,"instead."));const ue=q.morphAttributes.position||q.morphAttributes.normal||q.morphAttributes.color,ye=ue!==void 0?ue.length:0;let Te=0;q.morphAttributes.position!==void 0&&(Te=1),q.morphAttributes.normal!==void 0&&(Te=2),q.morphAttributes.color!==void 0&&(Te=3);let be,ie,he,Se;if(ge){const lt=Ii[ge];be=lt.vertexShader,ie=lt.fragmentShader}else be=M.vertexShader,ie=M.fragmentShader,l.update(M),he=l.getVertexShaderID(M),Se=l.getFragmentShaderID(M);const fe=s.getRenderTarget(),ze=H.isInstancedMesh===!0,We=H.isBatchedMesh===!0,Oe=!!M.map,pt=!!M.matcap,k=!!j,ut=!!M.aoMap,st=!!M.lightMap,ct=!!M.bumpMap,ke=!!M.normalMap,wt=!!M.displacementMap,Ye=!!M.emissiveMap,qe=!!M.metalnessMap,U=!!M.roughnessMap,E=M.anisotropy>0,Q=M.clearcoat>0,le=M.dispersion>0,te=M.iridescence>0,$=M.sheen>0,Ee=M.transmission>0,xe=E&&!!M.anisotropyMap,Ce=Q&&!!M.clearcoatMap,Je=Q&&!!M.clearcoatNormalMap,me=Q&&!!M.clearcoatRoughnessMap,Ae=te&&!!M.iridescenceMap,Ze=te&&!!M.iridescenceThicknessMap,He=$&&!!M.sheenColorMap,we=$&&!!M.sheenRoughnessMap,Ve=!!M.specularMap,B=!!M.specularColorMap,ce=!!M.specularIntensityMap,O=Ee&&!!M.transmissionMap,ae=Ee&&!!M.thicknessMap,se=!!M.gradientMap,re=!!M.alphaMap,_e=M.alphaTest>0,Ke=!!M.alphaHash,ot=!!M.extensions;let xt=Ss;M.toneMapped&&(fe===null||fe.isXRRenderTarget===!0)&&(xt=s.toneMapping);const Et={shaderID:ge,shaderType:M.type,shaderName:M.name,vertexShader:be,fragmentShader:ie,defines:M.defines,customVertexShaderID:he,customFragmentShaderID:Se,isRawShaderMaterial:M.isRawShaderMaterial===!0,glslVersion:M.glslVersion,precision:f,batching:We,batchingColor:We&&H._colorsTexture!==null,instancing:ze,instancingColor:ze&&H.instanceColor!==null,instancingMorph:ze&&H.morphTexture!==null,supportsVertexTextures:u,outputColorSpace:fe===null?s.outputColorSpace:fe.isXRRenderTarget===!0?fe.texture.colorSpace:Ps,alphaToCoverage:!!M.alphaToCoverage,map:Oe,matcap:pt,envMap:k,envMapMode:k&&j.mapping,envMapCubeUVHeight:ne,aoMap:ut,lightMap:st,bumpMap:ct,normalMap:ke,displacementMap:u&&wt,emissiveMap:Ye,normalMapObjectSpace:ke&&M.normalMapType===Ug,normalMapTangentSpace:ke&&M.normalMapType===op,metalnessMap:qe,roughnessMap:U,anisotropy:E,anisotropyMap:xe,clearcoat:Q,clearcoatMap:Ce,clearcoatNormalMap:Je,clearcoatRoughnessMap:me,dispersion:le,iridescence:te,iridescenceMap:Ae,iridescenceThicknessMap:Ze,sheen:$,sheenColorMap:He,sheenRoughnessMap:we,specularMap:Ve,specularColorMap:B,specularIntensityMap:ce,transmission:Ee,transmissionMap:O,thicknessMap:ae,gradientMap:se,opaque:M.transparent===!1&&M.blending===Wr&&M.alphaToCoverage===!1,alphaMap:re,alphaTest:_e,alphaHash:Ke,combine:M.combine,mapUv:Oe&&x(M.map.channel),aoMapUv:ut&&x(M.aoMap.channel),lightMapUv:st&&x(M.lightMap.channel),bumpMapUv:ct&&x(M.bumpMap.channel),normalMapUv:ke&&x(M.normalMap.channel),displacementMapUv:wt&&x(M.displacementMap.channel),emissiveMapUv:Ye&&x(M.emissiveMap.channel),metalnessMapUv:qe&&x(M.metalnessMap.channel),roughnessMapUv:U&&x(M.roughnessMap.channel),anisotropyMapUv:xe&&x(M.anisotropyMap.channel),clearcoatMapUv:Ce&&x(M.clearcoatMap.channel),clearcoatNormalMapUv:Je&&x(M.clearcoatNormalMap.channel),clearcoatRoughnessMapUv:me&&x(M.clearcoatRoughnessMap.channel),iridescenceMapUv:Ae&&x(M.iridescenceMap.channel),iridescenceThicknessMapUv:Ze&&x(M.iridescenceThicknessMap.channel),sheenColorMapUv:He&&x(M.sheenColorMap.channel),sheenRoughnessMapUv:we&&x(M.sheenRoughnessMap.channel),specularMapUv:Ve&&x(M.specularMap.channel),specularColorMapUv:B&&x(M.specularColorMap.channel),specularIntensityMapUv:ce&&x(M.specularIntensityMap.channel),transmissionMapUv:O&&x(M.transmissionMap.channel),thicknessMapUv:ae&&x(M.thicknessMap.channel),alphaMapUv:re&&x(M.alphaMap.channel),vertexTangents:!!q.attributes.tangent&&(ke||E),vertexColors:M.vertexColors,vertexAlphas:M.vertexColors===!0&&!!q.attributes.color&&q.attributes.color.itemSize===4,pointsUvs:H.isPoints===!0&&!!q.attributes.uv&&(Oe||re),fog:!!J,useFog:M.fog===!0,fogExp2:!!J&&J.isFogExp2,flatShading:M.flatShading===!0,sizeAttenuation:M.sizeAttenuation===!0,logarithmicDepthBuffer:d,skinning:H.isSkinnedMesh===!0,morphTargets:q.morphAttributes.position!==void 0,morphNormals:q.morphAttributes.normal!==void 0,morphColors:q.morphAttributes.color!==void 0,morphTargetsCount:ye,morphTextureStride:Te,numDirLights:y.directional.length,numPointLights:y.point.length,numSpotLights:y.spot.length,numSpotLightMaps:y.spotLightMap.length,numRectAreaLights:y.rectArea.length,numHemiLights:y.hemi.length,numDirLightShadows:y.directionalShadowMap.length,numPointLightShadows:y.pointShadowMap.length,numSpotLightShadows:y.spotShadowMap.length,numSpotLightShadowsWithMaps:y.numSpotLightShadowsWithMaps,numLightProbes:y.numLightProbes,numClippingPlanes:a.numPlanes,numClipIntersection:a.numIntersection,dithering:M.dithering,shadowMapEnabled:s.shadowMap.enabled&&P.length>0,shadowMapType:s.shadowMap.type,toneMapping:xt,decodeVideoTexture:Oe&&M.map.isVideoTexture===!0&&Mt.getTransfer(M.map.colorSpace)===kt,premultipliedAlpha:M.premultipliedAlpha,doubleSided:M.side===Nn,flipSided:M.side===zn,useDepthPacking:M.depthPacking>=0,depthPacking:M.depthPacking||0,index0AttributeName:M.index0AttributeName,extensionClipCullDistance:ot&&M.extensions.clipCullDistance===!0&&n.has("WEBGL_clip_cull_distance"),extensionMultiDraw:(ot&&M.extensions.multiDraw===!0||We)&&n.has("WEBGL_multi_draw"),rendererExtensionParallelShaderCompile:n.has("KHR_parallel_shader_compile"),customProgramCacheKey:M.customProgramCacheKey()};return Et.vertexUv1s=c.has(1),Et.vertexUv2s=c.has(2),Et.vertexUv3s=c.has(3),c.clear(),Et}function m(M){const y=[];if(M.shaderID?y.push(M.shaderID):(y.push(M.customVertexShaderID),y.push(M.customFragmentShaderID)),M.defines!==void 0)for(const P in M.defines)y.push(P),y.push(M.defines[P]);return M.isRawShaderMaterial===!1&&(b(y,M),_(y,M),y.push(s.outputColorSpace)),y.push(M.customProgramCacheKey),y.join()}function b(M,y){M.push(y.precision),M.push(y.outputColorSpace),M.push(y.envMapMode),M.push(y.envMapCubeUVHeight),M.push(y.mapUv),M.push(y.alphaMapUv),M.push(y.lightMapUv),M.push(y.aoMapUv),M.push(y.bumpMapUv),M.push(y.normalMapUv),M.push(y.displacementMapUv),M.push(y.emissiveMapUv),M.push(y.metalnessMapUv),M.push(y.roughnessMapUv),M.push(y.anisotropyMapUv),M.push(y.clearcoatMapUv),M.push(y.clearcoatNormalMapUv),M.push(y.clearcoatRoughnessMapUv),M.push(y.iridescenceMapUv),M.push(y.iridescenceThicknessMapUv),M.push(y.sheenColorMapUv),M.push(y.sheenRoughnessMapUv),M.push(y.specularMapUv),M.push(y.specularColorMapUv),M.push(y.specularIntensityMapUv),M.push(y.transmissionMapUv),M.push(y.thicknessMapUv),M.push(y.combine),M.push(y.fogExp2),M.push(y.sizeAttenuation),M.push(y.morphTargetsCount),M.push(y.morphAttributeCount),M.push(y.numDirLights),M.push(y.numPointLights),M.push(y.numSpotLights),M.push(y.numSpotLightMaps),M.push(y.numHemiLights),M.push(y.numRectAreaLights),M.push(y.numDirLightShadows),M.push(y.numPointLightShadows),M.push(y.numSpotLightShadows),M.push(y.numSpotLightShadowsWithMaps),M.push(y.numLightProbes),M.push(y.shadowMapType),M.push(y.toneMapping),M.push(y.numClippingPlanes),M.push(y.numClipIntersection),M.push(y.depthPacking)}function _(M,y){o.disableAll(),y.supportsVertexTextures&&o.enable(0),y.instancing&&o.enable(1),y.instancingColor&&o.enable(2),y.instancingMorph&&o.enable(3),y.matcap&&o.enable(4),y.envMap&&o.enable(5),y.normalMapObjectSpace&&o.enable(6),y.normalMapTangentSpace&&o.enable(7),y.clearcoat&&o.enable(8),y.iridescence&&o.enable(9),y.alphaTest&&o.enable(10),y.vertexColors&&o.enable(11),y.vertexAlphas&&o.enable(12),y.vertexUv1s&&o.enable(13),y.vertexUv2s&&o.enable(14),y.vertexUv3s&&o.enable(15),y.vertexTangents&&o.enable(16),y.anisotropy&&o.enable(17),y.alphaHash&&o.enable(18),y.batching&&o.enable(19),y.dispersion&&o.enable(20),y.batchingColor&&o.enable(21),M.push(o.mask),o.disableAll(),y.fog&&o.enable(0),y.useFog&&o.enable(1),y.flatShading&&o.enable(2),y.logarithmicDepthBuffer&&o.enable(3),y.skinning&&o.enable(4),y.morphTargets&&o.enable(5),y.morphNormals&&o.enable(6),y.morphColors&&o.enable(7),y.premultipliedAlpha&&o.enable(8),y.shadowMapEnabled&&o.enable(9),y.doubleSided&&o.enable(10),y.flipSided&&o.enable(11),y.useDepthPacking&&o.enable(12),y.dithering&&o.enable(13),y.transmission&&o.enable(14),y.sheen&&o.enable(15),y.opaque&&o.enable(16),y.pointsUvs&&o.enable(17),y.decodeVideoTexture&&o.enable(18),y.alphaToCoverage&&o.enable(19),M.push(o.mask)}function S(M){const y=g[M.type];let P;if(y){const X=Ii[y];P=wx.clone(X.uniforms)}else P=M.uniforms;return P}function I(M,y){let P;for(let X=0,H=h.length;X<H;X++){const J=h[X];if(J.cacheKey===y){P=J,++P.usedTimes;break}}return P===void 0&&(P=new Oy(s,y,M,r),h.push(P)),P}function A(M){if(--M.usedTimes===0){const y=h.indexOf(M);h[y]=h[h.length-1],h.pop(),M.destroy()}}function R(M){l.remove(M)}function N(){l.dispose()}return{getParameters:p,getProgramCacheKey:m,getUniforms:S,acquireProgram:I,releaseProgram:A,releaseShaderCache:R,programs:h,dispose:N}}function Vy(){let s=new WeakMap;function e(a){return s.has(a)}function t(a){let o=s.get(a);return o===void 0&&(o={},s.set(a,o)),o}function n(a){s.delete(a)}function i(a,o,l){s.get(a)[o]=l}function r(){s=new WeakMap}return{has:e,get:t,remove:n,update:i,dispose:r}}function Gy(s,e){return s.groupOrder!==e.groupOrder?s.groupOrder-e.groupOrder:s.renderOrder!==e.renderOrder?s.renderOrder-e.renderOrder:s.material.id!==e.material.id?s.material.id-e.material.id:s.z!==e.z?s.z-e.z:s.id-e.id}function Ru(s,e){return s.groupOrder!==e.groupOrder?s.groupOrder-e.groupOrder:s.renderOrder!==e.renderOrder?s.renderOrder-e.renderOrder:s.z!==e.z?e.z-s.z:s.id-e.id}function Pu(){const s=[];let e=0;const t=[],n=[],i=[];function r(){e=0,t.length=0,n.length=0,i.length=0}function a(d,u,f,g,x,p){let m=s[e];return m===void 0?(m={id:d.id,object:d,geometry:u,material:f,groupOrder:g,renderOrder:d.renderOrder,z:x,group:p},s[e]=m):(m.id=d.id,m.object=d,m.geometry=u,m.material=f,m.groupOrder=g,m.renderOrder=d.renderOrder,m.z=x,m.group=p),e++,m}function o(d,u,f,g,x,p){const m=a(d,u,f,g,x,p);f.transmission>0?n.push(m):f.transparent===!0?i.push(m):t.push(m)}function l(d,u,f,g,x,p){const m=a(d,u,f,g,x,p);f.transmission>0?n.unshift(m):f.transparent===!0?i.unshift(m):t.unshift(m)}function c(d,u){t.length>1&&t.sort(d||Gy),n.length>1&&n.sort(u||Ru),i.length>1&&i.sort(u||Ru)}function h(){for(let d=e,u=s.length;d<u;d++){const f=s[d];if(f.id===null)break;f.id=null,f.object=null,f.geometry=null,f.material=null,f.group=null}}return{opaque:t,transmissive:n,transparent:i,init:r,push:o,unshift:l,finish:h,sort:c}}function Wy(){let s=new WeakMap;function e(n,i){const r=s.get(n);let a;return r===void 0?(a=new Pu,s.set(n,[a])):i>=r.length?(a=new Pu,r.push(a)):a=r[i],a}function t(){s=new WeakMap}return{get:e,dispose:t}}function $y(){const s={};return{get:function(e){if(s[e.id]!==void 0)return s[e.id];let t;switch(e.type){case"DirectionalLight":t={direction:new V,color:new nt};break;case"SpotLight":t={position:new V,direction:new V,color:new nt,distance:0,coneCos:0,penumbraCos:0,decay:0};break;case"PointLight":t={position:new V,color:new nt,distance:0,decay:0};break;case"HemisphereLight":t={direction:new V,skyColor:new nt,groundColor:new nt};break;case"RectAreaLight":t={color:new nt,position:new V,halfWidth:new V,halfHeight:new V};break}return s[e.id]=t,t}}}function qy(){const s={};return{get:function(e){if(s[e.id]!==void 0)return s[e.id];let t;switch(e.type){case"DirectionalLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new Xe};break;case"SpotLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new Xe};break;case"PointLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new Xe,shadowCameraNear:1,shadowCameraFar:1e3};break}return s[e.id]=t,t}}}let Xy=0;function Yy(s,e){return(e.castShadow?2:0)-(s.castShadow?2:0)+(e.map?1:0)-(s.map?1:0)}function jy(s){const e=new $y,t=qy(),n={version:0,hash:{directionalLength:-1,pointLength:-1,spotLength:-1,rectAreaLength:-1,hemiLength:-1,numDirectionalShadows:-1,numPointShadows:-1,numSpotShadows:-1,numSpotMaps:-1,numLightProbes:-1},ambient:[0,0,0],probe:[],directional:[],directionalShadow:[],directionalShadowMap:[],directionalShadowMatrix:[],spot:[],spotLightMap:[],spotShadow:[],spotShadowMap:[],spotLightMatrix:[],rectArea:[],rectAreaLTC1:null,rectAreaLTC2:null,point:[],pointShadow:[],pointShadowMap:[],pointShadowMatrix:[],hemi:[],numSpotLightShadowsWithMaps:0,numLightProbes:0};for(let c=0;c<9;c++)n.probe.push(new V);const i=new V,r=new Bt,a=new Bt;function o(c){let h=0,d=0,u=0;for(let M=0;M<9;M++)n.probe[M].set(0,0,0);let f=0,g=0,x=0,p=0,m=0,b=0,_=0,S=0,I=0,A=0,R=0;c.sort(Yy);for(let M=0,y=c.length;M<y;M++){const P=c[M],X=P.color,H=P.intensity,J=P.distance,q=P.shadow&&P.shadow.map?P.shadow.map.texture:null;if(P.isAmbientLight)h+=X.r*H,d+=X.g*H,u+=X.b*H;else if(P.isLightProbe){for(let ee=0;ee<9;ee++)n.probe[ee].addScaledVector(P.sh.coefficients[ee],H);R++}else if(P.isDirectionalLight){const ee=e.get(P);if(ee.color.copy(P.color).multiplyScalar(P.intensity),P.castShadow){const j=P.shadow,ne=t.get(P);ne.shadowIntensity=j.intensity,ne.shadowBias=j.bias,ne.shadowNormalBias=j.normalBias,ne.shadowRadius=j.radius,ne.shadowMapSize=j.mapSize,n.directionalShadow[f]=ne,n.directionalShadowMap[f]=q,n.directionalShadowMatrix[f]=P.shadow.matrix,b++}n.directional[f]=ee,f++}else if(P.isSpotLight){const ee=e.get(P);ee.position.setFromMatrixPosition(P.matrixWorld),ee.color.copy(X).multiplyScalar(H),ee.distance=J,ee.coneCos=Math.cos(P.angle),ee.penumbraCos=Math.cos(P.angle*(1-P.penumbra)),ee.decay=P.decay,n.spot[x]=ee;const j=P.shadow;if(P.map&&(n.spotLightMap[I]=P.map,I++,j.updateMatrices(P),P.castShadow&&A++),n.spotLightMatrix[x]=j.matrix,P.castShadow){const ne=t.get(P);ne.shadowIntensity=j.intensity,ne.shadowBias=j.bias,ne.shadowNormalBias=j.normalBias,ne.shadowRadius=j.radius,ne.shadowMapSize=j.mapSize,n.spotShadow[x]=ne,n.spotShadowMap[x]=q,S++}x++}else if(P.isRectAreaLight){const ee=e.get(P);ee.color.copy(X).multiplyScalar(H),ee.halfWidth.set(P.width*.5,0,0),ee.halfHeight.set(0,P.height*.5,0),n.rectArea[p]=ee,p++}else if(P.isPointLight){const ee=e.get(P);if(ee.color.copy(P.color).multiplyScalar(P.intensity),ee.distance=P.distance,ee.decay=P.decay,P.castShadow){const j=P.shadow,ne=t.get(P);ne.shadowIntensity=j.intensity,ne.shadowBias=j.bias,ne.shadowNormalBias=j.normalBias,ne.shadowRadius=j.radius,ne.shadowMapSize=j.mapSize,ne.shadowCameraNear=j.camera.near,ne.shadowCameraFar=j.camera.far,n.pointShadow[g]=ne,n.pointShadowMap[g]=q,n.pointShadowMatrix[g]=P.shadow.matrix,_++}n.point[g]=ee,g++}else if(P.isHemisphereLight){const ee=e.get(P);ee.skyColor.copy(P.color).multiplyScalar(H),ee.groundColor.copy(P.groundColor).multiplyScalar(H),n.hemi[m]=ee,m++}}p>0&&(s.has("OES_texture_float_linear")===!0?(n.rectAreaLTC1=Re.LTC_FLOAT_1,n.rectAreaLTC2=Re.LTC_FLOAT_2):(n.rectAreaLTC1=Re.LTC_HALF_1,n.rectAreaLTC2=Re.LTC_HALF_2)),n.ambient[0]=h,n.ambient[1]=d,n.ambient[2]=u;const N=n.hash;(N.directionalLength!==f||N.pointLength!==g||N.spotLength!==x||N.rectAreaLength!==p||N.hemiLength!==m||N.numDirectionalShadows!==b||N.numPointShadows!==_||N.numSpotShadows!==S||N.numSpotMaps!==I||N.numLightProbes!==R)&&(n.directional.length=f,n.spot.length=x,n.rectArea.length=p,n.point.length=g,n.hemi.length=m,n.directionalShadow.length=b,n.directionalShadowMap.length=b,n.pointShadow.length=_,n.pointShadowMap.length=_,n.spotShadow.length=S,n.spotShadowMap.length=S,n.directionalShadowMatrix.length=b,n.pointShadowMatrix.length=_,n.spotLightMatrix.length=S+I-A,n.spotLightMap.length=I,n.numSpotLightShadowsWithMaps=A,n.numLightProbes=R,N.directionalLength=f,N.pointLength=g,N.spotLength=x,N.rectAreaLength=p,N.hemiLength=m,N.numDirectionalShadows=b,N.numPointShadows=_,N.numSpotShadows=S,N.numSpotMaps=I,N.numLightProbes=R,n.version=Xy++)}function l(c,h){let d=0,u=0,f=0,g=0,x=0;const p=h.matrixWorldInverse;for(let m=0,b=c.length;m<b;m++){const _=c[m];if(_.isDirectionalLight){const S=n.directional[d];S.direction.setFromMatrixPosition(_.matrixWorld),i.setFromMatrixPosition(_.target.matrixWorld),S.direction.sub(i),S.direction.transformDirection(p),d++}else if(_.isSpotLight){const S=n.spot[f];S.position.setFromMatrixPosition(_.matrixWorld),S.position.applyMatrix4(p),S.direction.setFromMatrixPosition(_.matrixWorld),i.setFromMatrixPosition(_.target.matrixWorld),S.direction.sub(i),S.direction.transformDirection(p),f++}else if(_.isRectAreaLight){const S=n.rectArea[g];S.position.setFromMatrixPosition(_.matrixWorld),S.position.applyMatrix4(p),a.identity(),r.copy(_.matrixWorld),r.premultiply(p),a.extractRotation(r),S.halfWidth.set(_.width*.5,0,0),S.halfHeight.set(0,_.height*.5,0),S.halfWidth.applyMatrix4(a),S.halfHeight.applyMatrix4(a),g++}else if(_.isPointLight){const S=n.point[u];S.position.setFromMatrixPosition(_.matrixWorld),S.position.applyMatrix4(p),u++}else if(_.isHemisphereLight){const S=n.hemi[x];S.direction.setFromMatrixPosition(_.matrixWorld),S.direction.transformDirection(p),x++}}}return{setup:o,setupView:l,state:n}}function Lu(s){const e=new jy(s),t=[],n=[];function i(h){c.camera=h,t.length=0,n.length=0}function r(h){t.push(h)}function a(h){n.push(h)}function o(){e.setup(t)}function l(h){e.setupView(t,h)}const c={lightsArray:t,shadowsArray:n,camera:null,lights:e,transmissionRenderTarget:{}};return{init:i,state:c,setupLights:o,setupLightsView:l,pushLight:r,pushShadow:a}}function Ky(s){let e=new WeakMap;function t(i,r=0){const a=e.get(i);let o;return a===void 0?(o=new Lu(s),e.set(i,[o])):r>=a.length?(o=new Lu(s),a.push(o)):o=a[r],o}function n(){e=new WeakMap}return{get:t,dispose:n}}class Jy extends Ls{constructor(e){super(),this.isMeshDepthMaterial=!0,this.type="MeshDepthMaterial",this.depthPacking=Dg,this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.wireframe=!1,this.wireframeLinewidth=1,this.setValues(e)}copy(e){return super.copy(e),this.depthPacking=e.depthPacking,this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this}}class Zy extends Ls{constructor(e){super(),this.isMeshDistanceMaterial=!0,this.type="MeshDistanceMaterial",this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.setValues(e)}copy(e){return super.copy(e),this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this}}const Qy=`void main() {
	gl_Position = vec4( position, 1.0 );
}`,eb=`uniform sampler2D shadow_pass;
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
}`;function tb(s,e,t){let n=new $h;const i=new Xe,r=new Xe,a=new rn,o=new Jy({depthPacking:Ig}),l=new Zy,c={},h=t.maxTextureSize,d={[Es]:zn,[zn]:Es,[Nn]:Nn},u=new Ts({defines:{VSM_SAMPLES:8},uniforms:{shadow_pass:{value:null},resolution:{value:new Xe},radius:{value:4}},vertexShader:Qy,fragmentShader:eb}),f=u.clone();f.defines.HORIZONTAL_PASS=1;const g=new Jt;g.setAttribute("position",new bi(new Float32Array([-1,-1,.5,3,-1,.5,-1,3,.5]),3));const x=new Xt(g,u),p=this;this.enabled=!1,this.autoUpdate=!0,this.needsUpdate=!1,this.type=qf;let m=this.type;this.render=function(A,R,N){if(p.enabled===!1||p.autoUpdate===!1&&p.needsUpdate===!1||A.length===0)return;const M=s.getRenderTarget(),y=s.getActiveCubeFace(),P=s.getActiveMipmapLevel(),X=s.state;X.setBlending(bs),X.buffers.color.setClear(1,1,1,1),X.buffers.depth.setTest(!0),X.setScissorTest(!1);const H=m!==Yi&&this.type===Yi,J=m===Yi&&this.type!==Yi;for(let q=0,ee=A.length;q<ee;q++){const j=A[q],ne=j.shadow;if(ne===void 0){console.warn("THREE.WebGLShadowMap:",j,"has no shadow.");continue}if(ne.autoUpdate===!1&&ne.needsUpdate===!1)continue;i.copy(ne.mapSize);const ge=ne.getFrameExtents();if(i.multiply(ge),r.copy(ne.mapSize),(i.x>h||i.y>h)&&(i.x>h&&(r.x=Math.floor(h/ge.x),i.x=r.x*ge.x,ne.mapSize.x=r.x),i.y>h&&(r.y=Math.floor(h/ge.y),i.y=r.y*ge.y,ne.mapSize.y=r.y)),ne.map===null||H===!0||J===!0){const ye=this.type!==Yi?{minFilter:si,magFilter:si}:{};ne.map!==null&&ne.map.dispose(),ne.map=new er(i.x,i.y,ye),ne.map.texture.name=j.name+".shadowMap",ne.camera.updateProjectionMatrix()}s.setRenderTarget(ne.map),s.clear();const ue=ne.getViewportCount();for(let ye=0;ye<ue;ye++){const Te=ne.getViewport(ye);a.set(r.x*Te.x,r.y*Te.y,r.x*Te.z,r.y*Te.w),X.viewport(a),ne.updateMatrices(j,ye),n=ne.getFrustum(),S(R,N,ne.camera,j,this.type)}ne.isPointLightShadow!==!0&&this.type===Yi&&b(ne,N),ne.needsUpdate=!1}m=this.type,p.needsUpdate=!1,s.setRenderTarget(M,y,P)};function b(A,R){const N=e.update(x);u.defines.VSM_SAMPLES!==A.blurSamples&&(u.defines.VSM_SAMPLES=A.blurSamples,f.defines.VSM_SAMPLES=A.blurSamples,u.needsUpdate=!0,f.needsUpdate=!0),A.mapPass===null&&(A.mapPass=new er(i.x,i.y)),u.uniforms.shadow_pass.value=A.map.texture,u.uniforms.resolution.value=A.mapSize,u.uniforms.radius.value=A.radius,s.setRenderTarget(A.mapPass),s.clear(),s.renderBufferDirect(R,null,N,u,x,null),f.uniforms.shadow_pass.value=A.mapPass.texture,f.uniforms.resolution.value=A.mapSize,f.uniforms.radius.value=A.radius,s.setRenderTarget(A.map),s.clear(),s.renderBufferDirect(R,null,N,f,x,null)}function _(A,R,N,M){let y=null;const P=N.isPointLight===!0?A.customDistanceMaterial:A.customDepthMaterial;if(P!==void 0)y=P;else if(y=N.isPointLight===!0?l:o,s.localClippingEnabled&&R.clipShadows===!0&&Array.isArray(R.clippingPlanes)&&R.clippingPlanes.length!==0||R.displacementMap&&R.displacementScale!==0||R.alphaMap&&R.alphaTest>0||R.map&&R.alphaTest>0){const X=y.uuid,H=R.uuid;let J=c[X];J===void 0&&(J={},c[X]=J);let q=J[H];q===void 0&&(q=y.clone(),J[H]=q,R.addEventListener("dispose",I)),y=q}if(y.visible=R.visible,y.wireframe=R.wireframe,M===Yi?y.side=R.shadowSide!==null?R.shadowSide:R.side:y.side=R.shadowSide!==null?R.shadowSide:d[R.side],y.alphaMap=R.alphaMap,y.alphaTest=R.alphaTest,y.map=R.map,y.clipShadows=R.clipShadows,y.clippingPlanes=R.clippingPlanes,y.clipIntersection=R.clipIntersection,y.displacementMap=R.displacementMap,y.displacementScale=R.displacementScale,y.displacementBias=R.displacementBias,y.wireframeLinewidth=R.wireframeLinewidth,y.linewidth=R.linewidth,N.isPointLight===!0&&y.isMeshDistanceMaterial===!0){const X=s.properties.get(y);X.light=N}return y}function S(A,R,N,M,y){if(A.visible===!1)return;if(A.layers.test(R.layers)&&(A.isMesh||A.isLine||A.isPoints)&&(A.castShadow||A.receiveShadow&&y===Yi)&&(!A.frustumCulled||n.intersectsObject(A))){A.modelViewMatrix.multiplyMatrices(N.matrixWorldInverse,A.matrixWorld);const H=e.update(A),J=A.material;if(Array.isArray(J)){const q=H.groups;for(let ee=0,j=q.length;ee<j;ee++){const ne=q[ee],ge=J[ne.materialIndex];if(ge&&ge.visible){const ue=_(A,ge,M,y);A.onBeforeShadow(s,A,R,N,H,ue,ne),s.renderBufferDirect(N,null,H,ue,A,ne),A.onAfterShadow(s,A,R,N,H,ue,ne)}}}else if(J.visible){const q=_(A,J,M,y);A.onBeforeShadow(s,A,R,N,H,q,null),s.renderBufferDirect(N,null,H,q,A,null),A.onAfterShadow(s,A,R,N,H,q,null)}}const X=A.children;for(let H=0,J=X.length;H<J;H++)S(X[H],R,N,M,y)}function I(A){A.target.removeEventListener("dispose",I);for(const N in c){const M=c[N],y=A.target.uuid;y in M&&(M[y].dispose(),delete M[y])}}}function nb(s){function e(){let O=!1;const ae=new rn;let se=null;const re=new rn(0,0,0,0);return{setMask:function(_e){se!==_e&&!O&&(s.colorMask(_e,_e,_e,_e),se=_e)},setLocked:function(_e){O=_e},setClear:function(_e,Ke,ot,xt,Et){Et===!0&&(_e*=xt,Ke*=xt,ot*=xt),ae.set(_e,Ke,ot,xt),re.equals(ae)===!1&&(s.clearColor(_e,Ke,ot,xt),re.copy(ae))},reset:function(){O=!1,se=null,re.set(-1,0,0,0)}}}function t(){let O=!1,ae=null,se=null,re=null;return{setTest:function(_e){_e?Se(s.DEPTH_TEST):fe(s.DEPTH_TEST)},setMask:function(_e){ae!==_e&&!O&&(s.depthMask(_e),ae=_e)},setFunc:function(_e){if(se!==_e){switch(_e){case gg:s.depthFunc(s.NEVER);break;case xg:s.depthFunc(s.ALWAYS);break;case vg:s.depthFunc(s.LESS);break;case rl:s.depthFunc(s.LEQUAL);break;case _g:s.depthFunc(s.EQUAL);break;case yg:s.depthFunc(s.GEQUAL);break;case bg:s.depthFunc(s.GREATER);break;case Sg:s.depthFunc(s.NOTEQUAL);break;default:s.depthFunc(s.LEQUAL)}se=_e}},setLocked:function(_e){O=_e},setClear:function(_e){re!==_e&&(s.clearDepth(_e),re=_e)},reset:function(){O=!1,ae=null,se=null,re=null}}}function n(){let O=!1,ae=null,se=null,re=null,_e=null,Ke=null,ot=null,xt=null,Et=null;return{setTest:function(lt){O||(lt?Se(s.STENCIL_TEST):fe(s.STENCIL_TEST))},setMask:function(lt){ae!==lt&&!O&&(s.stencilMask(lt),ae=lt)},setFunc:function(lt,vn,zt){(se!==lt||re!==vn||_e!==zt)&&(s.stencilFunc(lt,vn,zt),se=lt,re=vn,_e=zt)},setOp:function(lt,vn,zt){(Ke!==lt||ot!==vn||xt!==zt)&&(s.stencilOp(lt,vn,zt),Ke=lt,ot=vn,xt=zt)},setLocked:function(lt){O=lt},setClear:function(lt){Et!==lt&&(s.clearStencil(lt),Et=lt)},reset:function(){O=!1,ae=null,se=null,re=null,_e=null,Ke=null,ot=null,xt=null,Et=null}}}const i=new e,r=new t,a=new n,o=new WeakMap,l=new WeakMap;let c={},h={},d=new WeakMap,u=[],f=null,g=!1,x=null,p=null,m=null,b=null,_=null,S=null,I=null,A=new nt(0,0,0),R=0,N=!1,M=null,y=null,P=null,X=null,H=null;const J=s.getParameter(s.MAX_COMBINED_TEXTURE_IMAGE_UNITS);let q=!1,ee=0;const j=s.getParameter(s.VERSION);j.indexOf("WebGL")!==-1?(ee=parseFloat(/^WebGL (\d)/.exec(j)[1]),q=ee>=1):j.indexOf("OpenGL ES")!==-1&&(ee=parseFloat(/^OpenGL ES (\d)/.exec(j)[1]),q=ee>=2);let ne=null,ge={};const ue=s.getParameter(s.SCISSOR_BOX),ye=s.getParameter(s.VIEWPORT),Te=new rn().fromArray(ue),be=new rn().fromArray(ye);function ie(O,ae,se,re){const _e=new Uint8Array(4),Ke=s.createTexture();s.bindTexture(O,Ke),s.texParameteri(O,s.TEXTURE_MIN_FILTER,s.NEAREST),s.texParameteri(O,s.TEXTURE_MAG_FILTER,s.NEAREST);for(let ot=0;ot<se;ot++)O===s.TEXTURE_3D||O===s.TEXTURE_2D_ARRAY?s.texImage3D(ae,0,s.RGBA,1,1,re,0,s.RGBA,s.UNSIGNED_BYTE,_e):s.texImage2D(ae+ot,0,s.RGBA,1,1,0,s.RGBA,s.UNSIGNED_BYTE,_e);return Ke}const he={};he[s.TEXTURE_2D]=ie(s.TEXTURE_2D,s.TEXTURE_2D,1),he[s.TEXTURE_CUBE_MAP]=ie(s.TEXTURE_CUBE_MAP,s.TEXTURE_CUBE_MAP_POSITIVE_X,6),he[s.TEXTURE_2D_ARRAY]=ie(s.TEXTURE_2D_ARRAY,s.TEXTURE_2D_ARRAY,1,1),he[s.TEXTURE_3D]=ie(s.TEXTURE_3D,s.TEXTURE_3D,1,1),i.setClear(0,0,0,1),r.setClear(1),a.setClear(0),Se(s.DEPTH_TEST),r.setFunc(rl),ct(!1),ke(Od),Se(s.CULL_FACE),ut(bs);function Se(O){c[O]!==!0&&(s.enable(O),c[O]=!0)}function fe(O){c[O]!==!1&&(s.disable(O),c[O]=!1)}function ze(O,ae){return h[O]!==ae?(s.bindFramebuffer(O,ae),h[O]=ae,O===s.DRAW_FRAMEBUFFER&&(h[s.FRAMEBUFFER]=ae),O===s.FRAMEBUFFER&&(h[s.DRAW_FRAMEBUFFER]=ae),!0):!1}function We(O,ae){let se=u,re=!1;if(O){se=d.get(ae),se===void 0&&(se=[],d.set(ae,se));const _e=O.textures;if(se.length!==_e.length||se[0]!==s.COLOR_ATTACHMENT0){for(let Ke=0,ot=_e.length;Ke<ot;Ke++)se[Ke]=s.COLOR_ATTACHMENT0+Ke;se.length=_e.length,re=!0}}else se[0]!==s.BACK&&(se[0]=s.BACK,re=!0);re&&s.drawBuffers(se)}function Oe(O){return f!==O?(s.useProgram(O),f=O,!0):!1}const pt={[qs]:s.FUNC_ADD,[Qm]:s.FUNC_SUBTRACT,[eg]:s.FUNC_REVERSE_SUBTRACT};pt[tg]=s.MIN,pt[ng]=s.MAX;const k={[ig]:s.ZERO,[sg]:s.ONE,[rg]:s.SRC_COLOR,[zc]:s.SRC_ALPHA,[dg]:s.SRC_ALPHA_SATURATE,[cg]:s.DST_COLOR,[og]:s.DST_ALPHA,[ag]:s.ONE_MINUS_SRC_COLOR,[Hc]:s.ONE_MINUS_SRC_ALPHA,[hg]:s.ONE_MINUS_DST_COLOR,[lg]:s.ONE_MINUS_DST_ALPHA,[ug]:s.CONSTANT_COLOR,[fg]:s.ONE_MINUS_CONSTANT_COLOR,[pg]:s.CONSTANT_ALPHA,[mg]:s.ONE_MINUS_CONSTANT_ALPHA};function ut(O,ae,se,re,_e,Ke,ot,xt,Et,lt){if(O===bs){g===!0&&(fe(s.BLEND),g=!1);return}if(g===!1&&(Se(s.BLEND),g=!0),O!==Zm){if(O!==x||lt!==N){if((p!==qs||_!==qs)&&(s.blendEquation(s.FUNC_ADD),p=qs,_=qs),lt)switch(O){case Wr:s.blendFuncSeparate(s.ONE,s.ONE_MINUS_SRC_ALPHA,s.ONE,s.ONE_MINUS_SRC_ALPHA);break;case kd:s.blendFunc(s.ONE,s.ONE);break;case Bd:s.blendFuncSeparate(s.ZERO,s.ONE_MINUS_SRC_COLOR,s.ZERO,s.ONE);break;case zd:s.blendFuncSeparate(s.ZERO,s.SRC_COLOR,s.ZERO,s.SRC_ALPHA);break;default:console.error("THREE.WebGLState: Invalid blending: ",O);break}else switch(O){case Wr:s.blendFuncSeparate(s.SRC_ALPHA,s.ONE_MINUS_SRC_ALPHA,s.ONE,s.ONE_MINUS_SRC_ALPHA);break;case kd:s.blendFunc(s.SRC_ALPHA,s.ONE);break;case Bd:s.blendFuncSeparate(s.ZERO,s.ONE_MINUS_SRC_COLOR,s.ZERO,s.ONE);break;case zd:s.blendFunc(s.ZERO,s.SRC_COLOR);break;default:console.error("THREE.WebGLState: Invalid blending: ",O);break}m=null,b=null,S=null,I=null,A.set(0,0,0),R=0,x=O,N=lt}return}_e=_e||ae,Ke=Ke||se,ot=ot||re,(ae!==p||_e!==_)&&(s.blendEquationSeparate(pt[ae],pt[_e]),p=ae,_=_e),(se!==m||re!==b||Ke!==S||ot!==I)&&(s.blendFuncSeparate(k[se],k[re],k[Ke],k[ot]),m=se,b=re,S=Ke,I=ot),(xt.equals(A)===!1||Et!==R)&&(s.blendColor(xt.r,xt.g,xt.b,Et),A.copy(xt),R=Et),x=O,N=!1}function st(O,ae){O.side===Nn?fe(s.CULL_FACE):Se(s.CULL_FACE);let se=O.side===zn;ae&&(se=!se),ct(se),O.blending===Wr&&O.transparent===!1?ut(bs):ut(O.blending,O.blendEquation,O.blendSrc,O.blendDst,O.blendEquationAlpha,O.blendSrcAlpha,O.blendDstAlpha,O.blendColor,O.blendAlpha,O.premultipliedAlpha),r.setFunc(O.depthFunc),r.setTest(O.depthTest),r.setMask(O.depthWrite),i.setMask(O.colorWrite);const re=O.stencilWrite;a.setTest(re),re&&(a.setMask(O.stencilWriteMask),a.setFunc(O.stencilFunc,O.stencilRef,O.stencilFuncMask),a.setOp(O.stencilFail,O.stencilZFail,O.stencilZPass)),Ye(O.polygonOffset,O.polygonOffsetFactor,O.polygonOffsetUnits),O.alphaToCoverage===!0?Se(s.SAMPLE_ALPHA_TO_COVERAGE):fe(s.SAMPLE_ALPHA_TO_COVERAGE)}function ct(O){M!==O&&(O?s.frontFace(s.CW):s.frontFace(s.CCW),M=O)}function ke(O){O!==Km?(Se(s.CULL_FACE),O!==y&&(O===Od?s.cullFace(s.BACK):O===Jm?s.cullFace(s.FRONT):s.cullFace(s.FRONT_AND_BACK))):fe(s.CULL_FACE),y=O}function wt(O){O!==P&&(q&&s.lineWidth(O),P=O)}function Ye(O,ae,se){O?(Se(s.POLYGON_OFFSET_FILL),(X!==ae||H!==se)&&(s.polygonOffset(ae,se),X=ae,H=se)):fe(s.POLYGON_OFFSET_FILL)}function qe(O){O?Se(s.SCISSOR_TEST):fe(s.SCISSOR_TEST)}function U(O){O===void 0&&(O=s.TEXTURE0+J-1),ne!==O&&(s.activeTexture(O),ne=O)}function E(O,ae,se){se===void 0&&(ne===null?se=s.TEXTURE0+J-1:se=ne);let re=ge[se];re===void 0&&(re={type:void 0,texture:void 0},ge[se]=re),(re.type!==O||re.texture!==ae)&&(ne!==se&&(s.activeTexture(se),ne=se),s.bindTexture(O,ae||he[O]),re.type=O,re.texture=ae)}function Q(){const O=ge[ne];O!==void 0&&O.type!==void 0&&(s.bindTexture(O.type,null),O.type=void 0,O.texture=void 0)}function le(){try{s.compressedTexImage2D.apply(s,arguments)}catch(O){console.error("THREE.WebGLState:",O)}}function te(){try{s.compressedTexImage3D.apply(s,arguments)}catch(O){console.error("THREE.WebGLState:",O)}}function $(){try{s.texSubImage2D.apply(s,arguments)}catch(O){console.error("THREE.WebGLState:",O)}}function Ee(){try{s.texSubImage3D.apply(s,arguments)}catch(O){console.error("THREE.WebGLState:",O)}}function xe(){try{s.compressedTexSubImage2D.apply(s,arguments)}catch(O){console.error("THREE.WebGLState:",O)}}function Ce(){try{s.compressedTexSubImage3D.apply(s,arguments)}catch(O){console.error("THREE.WebGLState:",O)}}function Je(){try{s.texStorage2D.apply(s,arguments)}catch(O){console.error("THREE.WebGLState:",O)}}function me(){try{s.texStorage3D.apply(s,arguments)}catch(O){console.error("THREE.WebGLState:",O)}}function Ae(){try{s.texImage2D.apply(s,arguments)}catch(O){console.error("THREE.WebGLState:",O)}}function Ze(){try{s.texImage3D.apply(s,arguments)}catch(O){console.error("THREE.WebGLState:",O)}}function He(O){Te.equals(O)===!1&&(s.scissor(O.x,O.y,O.z,O.w),Te.copy(O))}function we(O){be.equals(O)===!1&&(s.viewport(O.x,O.y,O.z,O.w),be.copy(O))}function Ve(O,ae){let se=l.get(ae);se===void 0&&(se=new WeakMap,l.set(ae,se));let re=se.get(O);re===void 0&&(re=s.getUniformBlockIndex(ae,O.name),se.set(O,re))}function B(O,ae){const re=l.get(ae).get(O);o.get(ae)!==re&&(s.uniformBlockBinding(ae,re,O.__bindingPointIndex),o.set(ae,re))}function ce(){s.disable(s.BLEND),s.disable(s.CULL_FACE),s.disable(s.DEPTH_TEST),s.disable(s.POLYGON_OFFSET_FILL),s.disable(s.SCISSOR_TEST),s.disable(s.STENCIL_TEST),s.disable(s.SAMPLE_ALPHA_TO_COVERAGE),s.blendEquation(s.FUNC_ADD),s.blendFunc(s.ONE,s.ZERO),s.blendFuncSeparate(s.ONE,s.ZERO,s.ONE,s.ZERO),s.blendColor(0,0,0,0),s.colorMask(!0,!0,!0,!0),s.clearColor(0,0,0,0),s.depthMask(!0),s.depthFunc(s.LESS),s.clearDepth(1),s.stencilMask(4294967295),s.stencilFunc(s.ALWAYS,0,4294967295),s.stencilOp(s.KEEP,s.KEEP,s.KEEP),s.clearStencil(0),s.cullFace(s.BACK),s.frontFace(s.CCW),s.polygonOffset(0,0),s.activeTexture(s.TEXTURE0),s.bindFramebuffer(s.FRAMEBUFFER,null),s.bindFramebuffer(s.DRAW_FRAMEBUFFER,null),s.bindFramebuffer(s.READ_FRAMEBUFFER,null),s.useProgram(null),s.lineWidth(1),s.scissor(0,0,s.canvas.width,s.canvas.height),s.viewport(0,0,s.canvas.width,s.canvas.height),c={},ne=null,ge={},h={},d=new WeakMap,u=[],f=null,g=!1,x=null,p=null,m=null,b=null,_=null,S=null,I=null,A=new nt(0,0,0),R=0,N=!1,M=null,y=null,P=null,X=null,H=null,Te.set(0,0,s.canvas.width,s.canvas.height),be.set(0,0,s.canvas.width,s.canvas.height),i.reset(),r.reset(),a.reset()}return{buffers:{color:i,depth:r,stencil:a},enable:Se,disable:fe,bindFramebuffer:ze,drawBuffers:We,useProgram:Oe,setBlending:ut,setMaterial:st,setFlipSided:ct,setCullFace:ke,setLineWidth:wt,setPolygonOffset:Ye,setScissorTest:qe,activeTexture:U,bindTexture:E,unbindTexture:Q,compressedTexImage2D:le,compressedTexImage3D:te,texImage2D:Ae,texImage3D:Ze,updateUBOMapping:Ve,uniformBlockBinding:B,texStorage2D:Je,texStorage3D:me,texSubImage2D:$,texSubImage3D:Ee,compressedTexSubImage2D:xe,compressedTexSubImage3D:Ce,scissor:He,viewport:we,reset:ce}}function Du(s,e,t,n){const i=ib(n);switch(t){case ep:return s*e;case np:return s*e;case ip:return s*e*2;case sp:return s*e/i.components*i.byteLength;case Bh:return s*e/i.components*i.byteLength;case rp:return s*e*2/i.components*i.byteLength;case zh:return s*e*2/i.components*i.byteLength;case tp:return s*e*3/i.components*i.byteLength;case vi:return s*e*4/i.components*i.byteLength;case Hh:return s*e*4/i.components*i.byteLength;case Zo:case Qo:return Math.floor((s+3)/4)*Math.floor((e+3)/4)*8;case el:case tl:return Math.floor((s+3)/4)*Math.floor((e+3)/4)*16;case Xc:case jc:return Math.max(s,16)*Math.max(e,8)/4;case qc:case Yc:return Math.max(s,8)*Math.max(e,8)/2;case Kc:case Jc:return Math.floor((s+3)/4)*Math.floor((e+3)/4)*8;case Zc:return Math.floor((s+3)/4)*Math.floor((e+3)/4)*16;case Qc:return Math.floor((s+3)/4)*Math.floor((e+3)/4)*16;case eh:return Math.floor((s+4)/5)*Math.floor((e+3)/4)*16;case th:return Math.floor((s+4)/5)*Math.floor((e+4)/5)*16;case nh:return Math.floor((s+5)/6)*Math.floor((e+4)/5)*16;case ih:return Math.floor((s+5)/6)*Math.floor((e+5)/6)*16;case sh:return Math.floor((s+7)/8)*Math.floor((e+4)/5)*16;case rh:return Math.floor((s+7)/8)*Math.floor((e+5)/6)*16;case ah:return Math.floor((s+7)/8)*Math.floor((e+7)/8)*16;case oh:return Math.floor((s+9)/10)*Math.floor((e+4)/5)*16;case lh:return Math.floor((s+9)/10)*Math.floor((e+5)/6)*16;case ch:return Math.floor((s+9)/10)*Math.floor((e+7)/8)*16;case hh:return Math.floor((s+9)/10)*Math.floor((e+9)/10)*16;case dh:return Math.floor((s+11)/12)*Math.floor((e+9)/10)*16;case uh:return Math.floor((s+11)/12)*Math.floor((e+11)/12)*16;case nl:case fh:case ph:return Math.ceil(s/4)*Math.ceil(e/4)*16;case ap:case mh:return Math.ceil(s/4)*Math.ceil(e/4)*8;case gh:case xh:return Math.ceil(s/4)*Math.ceil(e/4)*16}throw new Error(`Unable to determine texture byte length for ${t} format.`)}function ib(s){switch(s){case ss:case Jf:return{byteLength:1,components:1};case ja:case Zf:case eo:return{byteLength:2,components:1};case Oh:case kh:return{byteLength:2,components:4};case Qs:case Fh:case Ki:return{byteLength:4,components:1};case Qf:return{byteLength:4,components:3}}throw new Error(`Unknown texture type ${s}.`)}function sb(s,e,t,n,i,r,a){const o=e.has("WEBGL_multisampled_render_to_texture")?e.get("WEBGL_multisampled_render_to_texture"):null,l=typeof navigator>"u"?!1:/OculusBrowser/g.test(navigator.userAgent),c=new Xe,h=new WeakMap;let d;const u=new WeakMap;let f=!1;try{f=typeof OffscreenCanvas<"u"&&new OffscreenCanvas(1,1).getContext("2d")!==null}catch{}function g(U,E){return f?new OffscreenCanvas(U,E):hl("canvas")}function x(U,E,Q){let le=1;const te=qe(U);if((te.width>Q||te.height>Q)&&(le=Q/Math.max(te.width,te.height)),le<1)if(typeof HTMLImageElement<"u"&&U instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&U instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&U instanceof ImageBitmap||typeof VideoFrame<"u"&&U instanceof VideoFrame){const $=Math.floor(le*te.width),Ee=Math.floor(le*te.height);d===void 0&&(d=g($,Ee));const xe=E?g($,Ee):d;return xe.width=$,xe.height=Ee,xe.getContext("2d").drawImage(U,0,0,$,Ee),console.warn("THREE.WebGLRenderer: Texture has been resized from ("+te.width+"x"+te.height+") to ("+$+"x"+Ee+")."),xe}else return"data"in U&&console.warn("THREE.WebGLRenderer: Image in DataTexture is too big ("+te.width+"x"+te.height+")."),U;return U}function p(U){return U.generateMipmaps&&U.minFilter!==si&&U.minFilter!==mi}function m(U){s.generateMipmap(U)}function b(U,E,Q,le,te=!1){if(U!==null){if(s[U]!==void 0)return s[U];console.warn("THREE.WebGLRenderer: Attempt to use non-existing WebGL internal format '"+U+"'")}let $=E;if(E===s.RED&&(Q===s.FLOAT&&($=s.R32F),Q===s.HALF_FLOAT&&($=s.R16F),Q===s.UNSIGNED_BYTE&&($=s.R8)),E===s.RED_INTEGER&&(Q===s.UNSIGNED_BYTE&&($=s.R8UI),Q===s.UNSIGNED_SHORT&&($=s.R16UI),Q===s.UNSIGNED_INT&&($=s.R32UI),Q===s.BYTE&&($=s.R8I),Q===s.SHORT&&($=s.R16I),Q===s.INT&&($=s.R32I)),E===s.RG&&(Q===s.FLOAT&&($=s.RG32F),Q===s.HALF_FLOAT&&($=s.RG16F),Q===s.UNSIGNED_BYTE&&($=s.RG8)),E===s.RG_INTEGER&&(Q===s.UNSIGNED_BYTE&&($=s.RG8UI),Q===s.UNSIGNED_SHORT&&($=s.RG16UI),Q===s.UNSIGNED_INT&&($=s.RG32UI),Q===s.BYTE&&($=s.RG8I),Q===s.SHORT&&($=s.RG16I),Q===s.INT&&($=s.RG32I)),E===s.RGB&&Q===s.UNSIGNED_INT_5_9_9_9_REV&&($=s.RGB9_E5),E===s.RGBA){const Ee=te?al:Mt.getTransfer(le);Q===s.FLOAT&&($=s.RGBA32F),Q===s.HALF_FLOAT&&($=s.RGBA16F),Q===s.UNSIGNED_BYTE&&($=Ee===kt?s.SRGB8_ALPHA8:s.RGBA8),Q===s.UNSIGNED_SHORT_4_4_4_4&&($=s.RGBA4),Q===s.UNSIGNED_SHORT_5_5_5_1&&($=s.RGB5_A1)}return($===s.R16F||$===s.R32F||$===s.RG16F||$===s.RG32F||$===s.RGBA16F||$===s.RGBA32F)&&e.get("EXT_color_buffer_float"),$}function _(U,E){let Q;return U?E===null||E===Qs||E===ea?Q=s.DEPTH24_STENCIL8:E===Ki?Q=s.DEPTH32F_STENCIL8:E===ja&&(Q=s.DEPTH24_STENCIL8,console.warn("DepthTexture: 16 bit depth attachment is not supported with stencil. Using 24-bit attachment.")):E===null||E===Qs||E===ea?Q=s.DEPTH_COMPONENT24:E===Ki?Q=s.DEPTH_COMPONENT32F:E===ja&&(Q=s.DEPTH_COMPONENT16),Q}function S(U,E){return p(U)===!0||U.isFramebufferTexture&&U.minFilter!==si&&U.minFilter!==mi?Math.log2(Math.max(E.width,E.height))+1:U.mipmaps!==void 0&&U.mipmaps.length>0?U.mipmaps.length:U.isCompressedTexture&&Array.isArray(U.image)?E.mipmaps.length:1}function I(U){const E=U.target;E.removeEventListener("dispose",I),R(E),E.isVideoTexture&&h.delete(E)}function A(U){const E=U.target;E.removeEventListener("dispose",A),M(E)}function R(U){const E=n.get(U);if(E.__webglInit===void 0)return;const Q=U.source,le=u.get(Q);if(le){const te=le[E.__cacheKey];te.usedTimes--,te.usedTimes===0&&N(U),Object.keys(le).length===0&&u.delete(Q)}n.remove(U)}function N(U){const E=n.get(U);s.deleteTexture(E.__webglTexture);const Q=U.source,le=u.get(Q);delete le[E.__cacheKey],a.memory.textures--}function M(U){const E=n.get(U);if(U.depthTexture&&U.depthTexture.dispose(),U.isWebGLCubeRenderTarget)for(let le=0;le<6;le++){if(Array.isArray(E.__webglFramebuffer[le]))for(let te=0;te<E.__webglFramebuffer[le].length;te++)s.deleteFramebuffer(E.__webglFramebuffer[le][te]);else s.deleteFramebuffer(E.__webglFramebuffer[le]);E.__webglDepthbuffer&&s.deleteRenderbuffer(E.__webglDepthbuffer[le])}else{if(Array.isArray(E.__webglFramebuffer))for(let le=0;le<E.__webglFramebuffer.length;le++)s.deleteFramebuffer(E.__webglFramebuffer[le]);else s.deleteFramebuffer(E.__webglFramebuffer);if(E.__webglDepthbuffer&&s.deleteRenderbuffer(E.__webglDepthbuffer),E.__webglMultisampledFramebuffer&&s.deleteFramebuffer(E.__webglMultisampledFramebuffer),E.__webglColorRenderbuffer)for(let le=0;le<E.__webglColorRenderbuffer.length;le++)E.__webglColorRenderbuffer[le]&&s.deleteRenderbuffer(E.__webglColorRenderbuffer[le]);E.__webglDepthRenderbuffer&&s.deleteRenderbuffer(E.__webglDepthRenderbuffer)}const Q=U.textures;for(let le=0,te=Q.length;le<te;le++){const $=n.get(Q[le]);$.__webglTexture&&(s.deleteTexture($.__webglTexture),a.memory.textures--),n.remove(Q[le])}n.remove(U)}let y=0;function P(){y=0}function X(){const U=y;return U>=i.maxTextures&&console.warn("THREE.WebGLTextures: Trying to use "+U+" texture units while this GPU supports only "+i.maxTextures),y+=1,U}function H(U){const E=[];return E.push(U.wrapS),E.push(U.wrapT),E.push(U.wrapR||0),E.push(U.magFilter),E.push(U.minFilter),E.push(U.anisotropy),E.push(U.internalFormat),E.push(U.format),E.push(U.type),E.push(U.generateMipmaps),E.push(U.premultiplyAlpha),E.push(U.flipY),E.push(U.unpackAlignment),E.push(U.colorSpace),E.join()}function J(U,E){const Q=n.get(U);if(U.isVideoTexture&&wt(U),U.isRenderTargetTexture===!1&&U.version>0&&Q.__version!==U.version){const le=U.image;if(le===null)console.warn("THREE.WebGLRenderer: Texture marked for update but no image data found.");else if(le.complete===!1)console.warn("THREE.WebGLRenderer: Texture marked for update but image is incomplete");else{be(Q,U,E);return}}t.bindTexture(s.TEXTURE_2D,Q.__webglTexture,s.TEXTURE0+E)}function q(U,E){const Q=n.get(U);if(U.version>0&&Q.__version!==U.version){be(Q,U,E);return}t.bindTexture(s.TEXTURE_2D_ARRAY,Q.__webglTexture,s.TEXTURE0+E)}function ee(U,E){const Q=n.get(U);if(U.version>0&&Q.__version!==U.version){be(Q,U,E);return}t.bindTexture(s.TEXTURE_3D,Q.__webglTexture,s.TEXTURE0+E)}function j(U,E){const Q=n.get(U);if(U.version>0&&Q.__version!==U.version){ie(Q,U,E);return}t.bindTexture(s.TEXTURE_CUBE_MAP,Q.__webglTexture,s.TEXTURE0+E)}const ne={[Wc]:s.REPEAT,[js]:s.CLAMP_TO_EDGE,[$c]:s.MIRRORED_REPEAT},ge={[si]:s.NEAREST,[Lg]:s.NEAREST_MIPMAP_NEAREST,[mo]:s.NEAREST_MIPMAP_LINEAR,[mi]:s.LINEAR,[Jl]:s.LINEAR_MIPMAP_NEAREST,[Ks]:s.LINEAR_MIPMAP_LINEAR},ue={[Ng]:s.NEVER,[Hg]:s.ALWAYS,[Fg]:s.LESS,[lp]:s.LEQUAL,[Og]:s.EQUAL,[zg]:s.GEQUAL,[kg]:s.GREATER,[Bg]:s.NOTEQUAL};function ye(U,E){if(E.type===Ki&&e.has("OES_texture_float_linear")===!1&&(E.magFilter===mi||E.magFilter===Jl||E.magFilter===mo||E.magFilter===Ks||E.minFilter===mi||E.minFilter===Jl||E.minFilter===mo||E.minFilter===Ks)&&console.warn("THREE.WebGLRenderer: Unable to use linear filtering with floating point textures. OES_texture_float_linear not supported on this device."),s.texParameteri(U,s.TEXTURE_WRAP_S,ne[E.wrapS]),s.texParameteri(U,s.TEXTURE_WRAP_T,ne[E.wrapT]),(U===s.TEXTURE_3D||U===s.TEXTURE_2D_ARRAY)&&s.texParameteri(U,s.TEXTURE_WRAP_R,ne[E.wrapR]),s.texParameteri(U,s.TEXTURE_MAG_FILTER,ge[E.magFilter]),s.texParameteri(U,s.TEXTURE_MIN_FILTER,ge[E.minFilter]),E.compareFunction&&(s.texParameteri(U,s.TEXTURE_COMPARE_MODE,s.COMPARE_REF_TO_TEXTURE),s.texParameteri(U,s.TEXTURE_COMPARE_FUNC,ue[E.compareFunction])),e.has("EXT_texture_filter_anisotropic")===!0){if(E.magFilter===si||E.minFilter!==mo&&E.minFilter!==Ks||E.type===Ki&&e.has("OES_texture_float_linear")===!1)return;if(E.anisotropy>1||n.get(E).__currentAnisotropy){const Q=e.get("EXT_texture_filter_anisotropic");s.texParameterf(U,Q.TEXTURE_MAX_ANISOTROPY_EXT,Math.min(E.anisotropy,i.getMaxAnisotropy())),n.get(E).__currentAnisotropy=E.anisotropy}}}function Te(U,E){let Q=!1;U.__webglInit===void 0&&(U.__webglInit=!0,E.addEventListener("dispose",I));const le=E.source;let te=u.get(le);te===void 0&&(te={},u.set(le,te));const $=H(E);if($!==U.__cacheKey){te[$]===void 0&&(te[$]={texture:s.createTexture(),usedTimes:0},a.memory.textures++,Q=!0),te[$].usedTimes++;const Ee=te[U.__cacheKey];Ee!==void 0&&(te[U.__cacheKey].usedTimes--,Ee.usedTimes===0&&N(E)),U.__cacheKey=$,U.__webglTexture=te[$].texture}return Q}function be(U,E,Q){let le=s.TEXTURE_2D;(E.isDataArrayTexture||E.isCompressedArrayTexture)&&(le=s.TEXTURE_2D_ARRAY),E.isData3DTexture&&(le=s.TEXTURE_3D);const te=Te(U,E),$=E.source;t.bindTexture(le,U.__webglTexture,s.TEXTURE0+Q);const Ee=n.get($);if($.version!==Ee.__version||te===!0){t.activeTexture(s.TEXTURE0+Q);const xe=Mt.getPrimaries(Mt.workingColorSpace),Ce=E.colorSpace===ys?null:Mt.getPrimaries(E.colorSpace),Je=E.colorSpace===ys||xe===Ce?s.NONE:s.BROWSER_DEFAULT_WEBGL;s.pixelStorei(s.UNPACK_FLIP_Y_WEBGL,E.flipY),s.pixelStorei(s.UNPACK_PREMULTIPLY_ALPHA_WEBGL,E.premultiplyAlpha),s.pixelStorei(s.UNPACK_ALIGNMENT,E.unpackAlignment),s.pixelStorei(s.UNPACK_COLORSPACE_CONVERSION_WEBGL,Je);let me=x(E.image,!1,i.maxTextureSize);me=Ye(E,me);const Ae=r.convert(E.format,E.colorSpace),Ze=r.convert(E.type);let He=b(E.internalFormat,Ae,Ze,E.colorSpace,E.isVideoTexture);ye(le,E);let we;const Ve=E.mipmaps,B=E.isVideoTexture!==!0,ce=Ee.__version===void 0||te===!0,O=$.dataReady,ae=S(E,me);if(E.isDepthTexture)He=_(E.format===ta,E.type),ce&&(B?t.texStorage2D(s.TEXTURE_2D,1,He,me.width,me.height):t.texImage2D(s.TEXTURE_2D,0,He,me.width,me.height,0,Ae,Ze,null));else if(E.isDataTexture)if(Ve.length>0){B&&ce&&t.texStorage2D(s.TEXTURE_2D,ae,He,Ve[0].width,Ve[0].height);for(let se=0,re=Ve.length;se<re;se++)we=Ve[se],B?O&&t.texSubImage2D(s.TEXTURE_2D,se,0,0,we.width,we.height,Ae,Ze,we.data):t.texImage2D(s.TEXTURE_2D,se,He,we.width,we.height,0,Ae,Ze,we.data);E.generateMipmaps=!1}else B?(ce&&t.texStorage2D(s.TEXTURE_2D,ae,He,me.width,me.height),O&&t.texSubImage2D(s.TEXTURE_2D,0,0,0,me.width,me.height,Ae,Ze,me.data)):t.texImage2D(s.TEXTURE_2D,0,He,me.width,me.height,0,Ae,Ze,me.data);else if(E.isCompressedTexture)if(E.isCompressedArrayTexture){B&&ce&&t.texStorage3D(s.TEXTURE_2D_ARRAY,ae,He,Ve[0].width,Ve[0].height,me.depth);for(let se=0,re=Ve.length;se<re;se++)if(we=Ve[se],E.format!==vi)if(Ae!==null)if(B){if(O)if(E.layerUpdates.size>0){const _e=Du(we.width,we.height,E.format,E.type);for(const Ke of E.layerUpdates){const ot=we.data.subarray(Ke*_e/we.data.BYTES_PER_ELEMENT,(Ke+1)*_e/we.data.BYTES_PER_ELEMENT);t.compressedTexSubImage3D(s.TEXTURE_2D_ARRAY,se,0,0,Ke,we.width,we.height,1,Ae,ot,0,0)}E.clearLayerUpdates()}else t.compressedTexSubImage3D(s.TEXTURE_2D_ARRAY,se,0,0,0,we.width,we.height,me.depth,Ae,we.data,0,0)}else t.compressedTexImage3D(s.TEXTURE_2D_ARRAY,se,He,we.width,we.height,me.depth,0,we.data,0,0);else console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()");else B?O&&t.texSubImage3D(s.TEXTURE_2D_ARRAY,se,0,0,0,we.width,we.height,me.depth,Ae,Ze,we.data):t.texImage3D(s.TEXTURE_2D_ARRAY,se,He,we.width,we.height,me.depth,0,Ae,Ze,we.data)}else{B&&ce&&t.texStorage2D(s.TEXTURE_2D,ae,He,Ve[0].width,Ve[0].height);for(let se=0,re=Ve.length;se<re;se++)we=Ve[se],E.format!==vi?Ae!==null?B?O&&t.compressedTexSubImage2D(s.TEXTURE_2D,se,0,0,we.width,we.height,Ae,we.data):t.compressedTexImage2D(s.TEXTURE_2D,se,He,we.width,we.height,0,we.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()"):B?O&&t.texSubImage2D(s.TEXTURE_2D,se,0,0,we.width,we.height,Ae,Ze,we.data):t.texImage2D(s.TEXTURE_2D,se,He,we.width,we.height,0,Ae,Ze,we.data)}else if(E.isDataArrayTexture)if(B){if(ce&&t.texStorage3D(s.TEXTURE_2D_ARRAY,ae,He,me.width,me.height,me.depth),O)if(E.layerUpdates.size>0){const se=Du(me.width,me.height,E.format,E.type);for(const re of E.layerUpdates){const _e=me.data.subarray(re*se/me.data.BYTES_PER_ELEMENT,(re+1)*se/me.data.BYTES_PER_ELEMENT);t.texSubImage3D(s.TEXTURE_2D_ARRAY,0,0,0,re,me.width,me.height,1,Ae,Ze,_e)}E.clearLayerUpdates()}else t.texSubImage3D(s.TEXTURE_2D_ARRAY,0,0,0,0,me.width,me.height,me.depth,Ae,Ze,me.data)}else t.texImage3D(s.TEXTURE_2D_ARRAY,0,He,me.width,me.height,me.depth,0,Ae,Ze,me.data);else if(E.isData3DTexture)B?(ce&&t.texStorage3D(s.TEXTURE_3D,ae,He,me.width,me.height,me.depth),O&&t.texSubImage3D(s.TEXTURE_3D,0,0,0,0,me.width,me.height,me.depth,Ae,Ze,me.data)):t.texImage3D(s.TEXTURE_3D,0,He,me.width,me.height,me.depth,0,Ae,Ze,me.data);else if(E.isFramebufferTexture){if(ce)if(B)t.texStorage2D(s.TEXTURE_2D,ae,He,me.width,me.height);else{let se=me.width,re=me.height;for(let _e=0;_e<ae;_e++)t.texImage2D(s.TEXTURE_2D,_e,He,se,re,0,Ae,Ze,null),se>>=1,re>>=1}}else if(Ve.length>0){if(B&&ce){const se=qe(Ve[0]);t.texStorage2D(s.TEXTURE_2D,ae,He,se.width,se.height)}for(let se=0,re=Ve.length;se<re;se++)we=Ve[se],B?O&&t.texSubImage2D(s.TEXTURE_2D,se,0,0,Ae,Ze,we):t.texImage2D(s.TEXTURE_2D,se,He,Ae,Ze,we);E.generateMipmaps=!1}else if(B){if(ce){const se=qe(me);t.texStorage2D(s.TEXTURE_2D,ae,He,se.width,se.height)}O&&t.texSubImage2D(s.TEXTURE_2D,0,0,0,Ae,Ze,me)}else t.texImage2D(s.TEXTURE_2D,0,He,Ae,Ze,me);p(E)&&m(le),Ee.__version=$.version,E.onUpdate&&E.onUpdate(E)}U.__version=E.version}function ie(U,E,Q){if(E.image.length!==6)return;const le=Te(U,E),te=E.source;t.bindTexture(s.TEXTURE_CUBE_MAP,U.__webglTexture,s.TEXTURE0+Q);const $=n.get(te);if(te.version!==$.__version||le===!0){t.activeTexture(s.TEXTURE0+Q);const Ee=Mt.getPrimaries(Mt.workingColorSpace),xe=E.colorSpace===ys?null:Mt.getPrimaries(E.colorSpace),Ce=E.colorSpace===ys||Ee===xe?s.NONE:s.BROWSER_DEFAULT_WEBGL;s.pixelStorei(s.UNPACK_FLIP_Y_WEBGL,E.flipY),s.pixelStorei(s.UNPACK_PREMULTIPLY_ALPHA_WEBGL,E.premultiplyAlpha),s.pixelStorei(s.UNPACK_ALIGNMENT,E.unpackAlignment),s.pixelStorei(s.UNPACK_COLORSPACE_CONVERSION_WEBGL,Ce);const Je=E.isCompressedTexture||E.image[0].isCompressedTexture,me=E.image[0]&&E.image[0].isDataTexture,Ae=[];for(let re=0;re<6;re++)!Je&&!me?Ae[re]=x(E.image[re],!0,i.maxCubemapSize):Ae[re]=me?E.image[re].image:E.image[re],Ae[re]=Ye(E,Ae[re]);const Ze=Ae[0],He=r.convert(E.format,E.colorSpace),we=r.convert(E.type),Ve=b(E.internalFormat,He,we,E.colorSpace),B=E.isVideoTexture!==!0,ce=$.__version===void 0||le===!0,O=te.dataReady;let ae=S(E,Ze);ye(s.TEXTURE_CUBE_MAP,E);let se;if(Je){B&&ce&&t.texStorage2D(s.TEXTURE_CUBE_MAP,ae,Ve,Ze.width,Ze.height);for(let re=0;re<6;re++){se=Ae[re].mipmaps;for(let _e=0;_e<se.length;_e++){const Ke=se[_e];E.format!==vi?He!==null?B?O&&t.compressedTexSubImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+re,_e,0,0,Ke.width,Ke.height,He,Ke.data):t.compressedTexImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+re,_e,Ve,Ke.width,Ke.height,0,Ke.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .setTextureCube()"):B?O&&t.texSubImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+re,_e,0,0,Ke.width,Ke.height,He,we,Ke.data):t.texImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+re,_e,Ve,Ke.width,Ke.height,0,He,we,Ke.data)}}}else{if(se=E.mipmaps,B&&ce){se.length>0&&ae++;const re=qe(Ae[0]);t.texStorage2D(s.TEXTURE_CUBE_MAP,ae,Ve,re.width,re.height)}for(let re=0;re<6;re++)if(me){B?O&&t.texSubImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+re,0,0,0,Ae[re].width,Ae[re].height,He,we,Ae[re].data):t.texImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+re,0,Ve,Ae[re].width,Ae[re].height,0,He,we,Ae[re].data);for(let _e=0;_e<se.length;_e++){const ot=se[_e].image[re].image;B?O&&t.texSubImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+re,_e+1,0,0,ot.width,ot.height,He,we,ot.data):t.texImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+re,_e+1,Ve,ot.width,ot.height,0,He,we,ot.data)}}else{B?O&&t.texSubImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+re,0,0,0,He,we,Ae[re]):t.texImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+re,0,Ve,He,we,Ae[re]);for(let _e=0;_e<se.length;_e++){const Ke=se[_e];B?O&&t.texSubImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+re,_e+1,0,0,He,we,Ke.image[re]):t.texImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+re,_e+1,Ve,He,we,Ke.image[re])}}}p(E)&&m(s.TEXTURE_CUBE_MAP),$.__version=te.version,E.onUpdate&&E.onUpdate(E)}U.__version=E.version}function he(U,E,Q,le,te,$){const Ee=r.convert(Q.format,Q.colorSpace),xe=r.convert(Q.type),Ce=b(Q.internalFormat,Ee,xe,Q.colorSpace);if(!n.get(E).__hasExternalTextures){const me=Math.max(1,E.width>>$),Ae=Math.max(1,E.height>>$);te===s.TEXTURE_3D||te===s.TEXTURE_2D_ARRAY?t.texImage3D(te,$,Ce,me,Ae,E.depth,0,Ee,xe,null):t.texImage2D(te,$,Ce,me,Ae,0,Ee,xe,null)}t.bindFramebuffer(s.FRAMEBUFFER,U),ke(E)?o.framebufferTexture2DMultisampleEXT(s.FRAMEBUFFER,le,te,n.get(Q).__webglTexture,0,ct(E)):(te===s.TEXTURE_2D||te>=s.TEXTURE_CUBE_MAP_POSITIVE_X&&te<=s.TEXTURE_CUBE_MAP_NEGATIVE_Z)&&s.framebufferTexture2D(s.FRAMEBUFFER,le,te,n.get(Q).__webglTexture,$),t.bindFramebuffer(s.FRAMEBUFFER,null)}function Se(U,E,Q){if(s.bindRenderbuffer(s.RENDERBUFFER,U),E.depthBuffer){const le=E.depthTexture,te=le&&le.isDepthTexture?le.type:null,$=_(E.stencilBuffer,te),Ee=E.stencilBuffer?s.DEPTH_STENCIL_ATTACHMENT:s.DEPTH_ATTACHMENT,xe=ct(E);ke(E)?o.renderbufferStorageMultisampleEXT(s.RENDERBUFFER,xe,$,E.width,E.height):Q?s.renderbufferStorageMultisample(s.RENDERBUFFER,xe,$,E.width,E.height):s.renderbufferStorage(s.RENDERBUFFER,$,E.width,E.height),s.framebufferRenderbuffer(s.FRAMEBUFFER,Ee,s.RENDERBUFFER,U)}else{const le=E.textures;for(let te=0;te<le.length;te++){const $=le[te],Ee=r.convert($.format,$.colorSpace),xe=r.convert($.type),Ce=b($.internalFormat,Ee,xe,$.colorSpace),Je=ct(E);Q&&ke(E)===!1?s.renderbufferStorageMultisample(s.RENDERBUFFER,Je,Ce,E.width,E.height):ke(E)?o.renderbufferStorageMultisampleEXT(s.RENDERBUFFER,Je,Ce,E.width,E.height):s.renderbufferStorage(s.RENDERBUFFER,Ce,E.width,E.height)}}s.bindRenderbuffer(s.RENDERBUFFER,null)}function fe(U,E){if(E&&E.isWebGLCubeRenderTarget)throw new Error("Depth Texture with cube render targets is not supported");if(t.bindFramebuffer(s.FRAMEBUFFER,U),!(E.depthTexture&&E.depthTexture.isDepthTexture))throw new Error("renderTarget.depthTexture must be an instance of THREE.DepthTexture");(!n.get(E.depthTexture).__webglTexture||E.depthTexture.image.width!==E.width||E.depthTexture.image.height!==E.height)&&(E.depthTexture.image.width=E.width,E.depthTexture.image.height=E.height,E.depthTexture.needsUpdate=!0),J(E.depthTexture,0);const le=n.get(E.depthTexture).__webglTexture,te=ct(E);if(E.depthTexture.format===$r)ke(E)?o.framebufferTexture2DMultisampleEXT(s.FRAMEBUFFER,s.DEPTH_ATTACHMENT,s.TEXTURE_2D,le,0,te):s.framebufferTexture2D(s.FRAMEBUFFER,s.DEPTH_ATTACHMENT,s.TEXTURE_2D,le,0);else if(E.depthTexture.format===ta)ke(E)?o.framebufferTexture2DMultisampleEXT(s.FRAMEBUFFER,s.DEPTH_STENCIL_ATTACHMENT,s.TEXTURE_2D,le,0,te):s.framebufferTexture2D(s.FRAMEBUFFER,s.DEPTH_STENCIL_ATTACHMENT,s.TEXTURE_2D,le,0);else throw new Error("Unknown depthTexture format")}function ze(U){const E=n.get(U),Q=U.isWebGLCubeRenderTarget===!0;if(E.__boundDepthTexture!==U.depthTexture){const le=U.depthTexture;if(E.__depthDisposeCallback&&E.__depthDisposeCallback(),le){const te=()=>{delete E.__boundDepthTexture,delete E.__depthDisposeCallback,le.removeEventListener("dispose",te)};le.addEventListener("dispose",te),E.__depthDisposeCallback=te}E.__boundDepthTexture=le}if(U.depthTexture&&!E.__autoAllocateDepthBuffer){if(Q)throw new Error("target.depthTexture not supported in Cube render targets");fe(E.__webglFramebuffer,U)}else if(Q){E.__webglDepthbuffer=[];for(let le=0;le<6;le++)if(t.bindFramebuffer(s.FRAMEBUFFER,E.__webglFramebuffer[le]),E.__webglDepthbuffer[le]===void 0)E.__webglDepthbuffer[le]=s.createRenderbuffer(),Se(E.__webglDepthbuffer[le],U,!1);else{const te=U.stencilBuffer?s.DEPTH_STENCIL_ATTACHMENT:s.DEPTH_ATTACHMENT,$=E.__webglDepthbuffer[le];s.bindRenderbuffer(s.RENDERBUFFER,$),s.framebufferRenderbuffer(s.FRAMEBUFFER,te,s.RENDERBUFFER,$)}}else if(t.bindFramebuffer(s.FRAMEBUFFER,E.__webglFramebuffer),E.__webglDepthbuffer===void 0)E.__webglDepthbuffer=s.createRenderbuffer(),Se(E.__webglDepthbuffer,U,!1);else{const le=U.stencilBuffer?s.DEPTH_STENCIL_ATTACHMENT:s.DEPTH_ATTACHMENT,te=E.__webglDepthbuffer;s.bindRenderbuffer(s.RENDERBUFFER,te),s.framebufferRenderbuffer(s.FRAMEBUFFER,le,s.RENDERBUFFER,te)}t.bindFramebuffer(s.FRAMEBUFFER,null)}function We(U,E,Q){const le=n.get(U);E!==void 0&&he(le.__webglFramebuffer,U,U.texture,s.COLOR_ATTACHMENT0,s.TEXTURE_2D,0),Q!==void 0&&ze(U)}function Oe(U){const E=U.texture,Q=n.get(U),le=n.get(E);U.addEventListener("dispose",A);const te=U.textures,$=U.isWebGLCubeRenderTarget===!0,Ee=te.length>1;if(Ee||(le.__webglTexture===void 0&&(le.__webglTexture=s.createTexture()),le.__version=E.version,a.memory.textures++),$){Q.__webglFramebuffer=[];for(let xe=0;xe<6;xe++)if(E.mipmaps&&E.mipmaps.length>0){Q.__webglFramebuffer[xe]=[];for(let Ce=0;Ce<E.mipmaps.length;Ce++)Q.__webglFramebuffer[xe][Ce]=s.createFramebuffer()}else Q.__webglFramebuffer[xe]=s.createFramebuffer()}else{if(E.mipmaps&&E.mipmaps.length>0){Q.__webglFramebuffer=[];for(let xe=0;xe<E.mipmaps.length;xe++)Q.__webglFramebuffer[xe]=s.createFramebuffer()}else Q.__webglFramebuffer=s.createFramebuffer();if(Ee)for(let xe=0,Ce=te.length;xe<Ce;xe++){const Je=n.get(te[xe]);Je.__webglTexture===void 0&&(Je.__webglTexture=s.createTexture(),a.memory.textures++)}if(U.samples>0&&ke(U)===!1){Q.__webglMultisampledFramebuffer=s.createFramebuffer(),Q.__webglColorRenderbuffer=[],t.bindFramebuffer(s.FRAMEBUFFER,Q.__webglMultisampledFramebuffer);for(let xe=0;xe<te.length;xe++){const Ce=te[xe];Q.__webglColorRenderbuffer[xe]=s.createRenderbuffer(),s.bindRenderbuffer(s.RENDERBUFFER,Q.__webglColorRenderbuffer[xe]);const Je=r.convert(Ce.format,Ce.colorSpace),me=r.convert(Ce.type),Ae=b(Ce.internalFormat,Je,me,Ce.colorSpace,U.isXRRenderTarget===!0),Ze=ct(U);s.renderbufferStorageMultisample(s.RENDERBUFFER,Ze,Ae,U.width,U.height),s.framebufferRenderbuffer(s.FRAMEBUFFER,s.COLOR_ATTACHMENT0+xe,s.RENDERBUFFER,Q.__webglColorRenderbuffer[xe])}s.bindRenderbuffer(s.RENDERBUFFER,null),U.depthBuffer&&(Q.__webglDepthRenderbuffer=s.createRenderbuffer(),Se(Q.__webglDepthRenderbuffer,U,!0)),t.bindFramebuffer(s.FRAMEBUFFER,null)}}if($){t.bindTexture(s.TEXTURE_CUBE_MAP,le.__webglTexture),ye(s.TEXTURE_CUBE_MAP,E);for(let xe=0;xe<6;xe++)if(E.mipmaps&&E.mipmaps.length>0)for(let Ce=0;Ce<E.mipmaps.length;Ce++)he(Q.__webglFramebuffer[xe][Ce],U,E,s.COLOR_ATTACHMENT0,s.TEXTURE_CUBE_MAP_POSITIVE_X+xe,Ce);else he(Q.__webglFramebuffer[xe],U,E,s.COLOR_ATTACHMENT0,s.TEXTURE_CUBE_MAP_POSITIVE_X+xe,0);p(E)&&m(s.TEXTURE_CUBE_MAP),t.unbindTexture()}else if(Ee){for(let xe=0,Ce=te.length;xe<Ce;xe++){const Je=te[xe],me=n.get(Je);t.bindTexture(s.TEXTURE_2D,me.__webglTexture),ye(s.TEXTURE_2D,Je),he(Q.__webglFramebuffer,U,Je,s.COLOR_ATTACHMENT0+xe,s.TEXTURE_2D,0),p(Je)&&m(s.TEXTURE_2D)}t.unbindTexture()}else{let xe=s.TEXTURE_2D;if((U.isWebGL3DRenderTarget||U.isWebGLArrayRenderTarget)&&(xe=U.isWebGL3DRenderTarget?s.TEXTURE_3D:s.TEXTURE_2D_ARRAY),t.bindTexture(xe,le.__webglTexture),ye(xe,E),E.mipmaps&&E.mipmaps.length>0)for(let Ce=0;Ce<E.mipmaps.length;Ce++)he(Q.__webglFramebuffer[Ce],U,E,s.COLOR_ATTACHMENT0,xe,Ce);else he(Q.__webglFramebuffer,U,E,s.COLOR_ATTACHMENT0,xe,0);p(E)&&m(xe),t.unbindTexture()}U.depthBuffer&&ze(U)}function pt(U){const E=U.textures;for(let Q=0,le=E.length;Q<le;Q++){const te=E[Q];if(p(te)){const $=U.isWebGLCubeRenderTarget?s.TEXTURE_CUBE_MAP:s.TEXTURE_2D,Ee=n.get(te).__webglTexture;t.bindTexture($,Ee),m($),t.unbindTexture()}}}const k=[],ut=[];function st(U){if(U.samples>0){if(ke(U)===!1){const E=U.textures,Q=U.width,le=U.height;let te=s.COLOR_BUFFER_BIT;const $=U.stencilBuffer?s.DEPTH_STENCIL_ATTACHMENT:s.DEPTH_ATTACHMENT,Ee=n.get(U),xe=E.length>1;if(xe)for(let Ce=0;Ce<E.length;Ce++)t.bindFramebuffer(s.FRAMEBUFFER,Ee.__webglMultisampledFramebuffer),s.framebufferRenderbuffer(s.FRAMEBUFFER,s.COLOR_ATTACHMENT0+Ce,s.RENDERBUFFER,null),t.bindFramebuffer(s.FRAMEBUFFER,Ee.__webglFramebuffer),s.framebufferTexture2D(s.DRAW_FRAMEBUFFER,s.COLOR_ATTACHMENT0+Ce,s.TEXTURE_2D,null,0);t.bindFramebuffer(s.READ_FRAMEBUFFER,Ee.__webglMultisampledFramebuffer),t.bindFramebuffer(s.DRAW_FRAMEBUFFER,Ee.__webglFramebuffer);for(let Ce=0;Ce<E.length;Ce++){if(U.resolveDepthBuffer&&(U.depthBuffer&&(te|=s.DEPTH_BUFFER_BIT),U.stencilBuffer&&U.resolveStencilBuffer&&(te|=s.STENCIL_BUFFER_BIT)),xe){s.framebufferRenderbuffer(s.READ_FRAMEBUFFER,s.COLOR_ATTACHMENT0,s.RENDERBUFFER,Ee.__webglColorRenderbuffer[Ce]);const Je=n.get(E[Ce]).__webglTexture;s.framebufferTexture2D(s.DRAW_FRAMEBUFFER,s.COLOR_ATTACHMENT0,s.TEXTURE_2D,Je,0)}s.blitFramebuffer(0,0,Q,le,0,0,Q,le,te,s.NEAREST),l===!0&&(k.length=0,ut.length=0,k.push(s.COLOR_ATTACHMENT0+Ce),U.depthBuffer&&U.resolveDepthBuffer===!1&&(k.push($),ut.push($),s.invalidateFramebuffer(s.DRAW_FRAMEBUFFER,ut)),s.invalidateFramebuffer(s.READ_FRAMEBUFFER,k))}if(t.bindFramebuffer(s.READ_FRAMEBUFFER,null),t.bindFramebuffer(s.DRAW_FRAMEBUFFER,null),xe)for(let Ce=0;Ce<E.length;Ce++){t.bindFramebuffer(s.FRAMEBUFFER,Ee.__webglMultisampledFramebuffer),s.framebufferRenderbuffer(s.FRAMEBUFFER,s.COLOR_ATTACHMENT0+Ce,s.RENDERBUFFER,Ee.__webglColorRenderbuffer[Ce]);const Je=n.get(E[Ce]).__webglTexture;t.bindFramebuffer(s.FRAMEBUFFER,Ee.__webglFramebuffer),s.framebufferTexture2D(s.DRAW_FRAMEBUFFER,s.COLOR_ATTACHMENT0+Ce,s.TEXTURE_2D,Je,0)}t.bindFramebuffer(s.DRAW_FRAMEBUFFER,Ee.__webglMultisampledFramebuffer)}else if(U.depthBuffer&&U.resolveDepthBuffer===!1&&l){const E=U.stencilBuffer?s.DEPTH_STENCIL_ATTACHMENT:s.DEPTH_ATTACHMENT;s.invalidateFramebuffer(s.DRAW_FRAMEBUFFER,[E])}}}function ct(U){return Math.min(i.maxSamples,U.samples)}function ke(U){const E=n.get(U);return U.samples>0&&e.has("WEBGL_multisampled_render_to_texture")===!0&&E.__useRenderToTexture!==!1}function wt(U){const E=a.render.frame;h.get(U)!==E&&(h.set(U,E),U.update())}function Ye(U,E){const Q=U.colorSpace,le=U.format,te=U.type;return U.isCompressedTexture===!0||U.isVideoTexture===!0||Q!==Ps&&Q!==ys&&(Mt.getTransfer(Q)===kt?(le!==vi||te!==ss)&&console.warn("THREE.WebGLTextures: sRGB encoded textures have to use RGBAFormat and UnsignedByteType."):console.error("THREE.WebGLTextures: Unsupported texture color space:",Q)),E}function qe(U){return typeof HTMLImageElement<"u"&&U instanceof HTMLImageElement?(c.width=U.naturalWidth||U.width,c.height=U.naturalHeight||U.height):typeof VideoFrame<"u"&&U instanceof VideoFrame?(c.width=U.displayWidth,c.height=U.displayHeight):(c.width=U.width,c.height=U.height),c}this.allocateTextureUnit=X,this.resetTextureUnits=P,this.setTexture2D=J,this.setTexture2DArray=q,this.setTexture3D=ee,this.setTextureCube=j,this.rebindTextures=We,this.setupRenderTarget=Oe,this.updateRenderTargetMipmap=pt,this.updateMultisampleRenderTarget=st,this.setupDepthRenderbuffer=ze,this.setupFrameBufferTexture=he,this.useMultisampledRTT=ke}function rb(s,e){function t(n,i=ys){let r;const a=Mt.getTransfer(i);if(n===ss)return s.UNSIGNED_BYTE;if(n===Oh)return s.UNSIGNED_SHORT_4_4_4_4;if(n===kh)return s.UNSIGNED_SHORT_5_5_5_1;if(n===Qf)return s.UNSIGNED_INT_5_9_9_9_REV;if(n===Jf)return s.BYTE;if(n===Zf)return s.SHORT;if(n===ja)return s.UNSIGNED_SHORT;if(n===Fh)return s.INT;if(n===Qs)return s.UNSIGNED_INT;if(n===Ki)return s.FLOAT;if(n===eo)return s.HALF_FLOAT;if(n===ep)return s.ALPHA;if(n===tp)return s.RGB;if(n===vi)return s.RGBA;if(n===np)return s.LUMINANCE;if(n===ip)return s.LUMINANCE_ALPHA;if(n===$r)return s.DEPTH_COMPONENT;if(n===ta)return s.DEPTH_STENCIL;if(n===sp)return s.RED;if(n===Bh)return s.RED_INTEGER;if(n===rp)return s.RG;if(n===zh)return s.RG_INTEGER;if(n===Hh)return s.RGBA_INTEGER;if(n===Zo||n===Qo||n===el||n===tl)if(a===kt)if(r=e.get("WEBGL_compressed_texture_s3tc_srgb"),r!==null){if(n===Zo)return r.COMPRESSED_SRGB_S3TC_DXT1_EXT;if(n===Qo)return r.COMPRESSED_SRGB_ALPHA_S3TC_DXT1_EXT;if(n===el)return r.COMPRESSED_SRGB_ALPHA_S3TC_DXT3_EXT;if(n===tl)return r.COMPRESSED_SRGB_ALPHA_S3TC_DXT5_EXT}else return null;else if(r=e.get("WEBGL_compressed_texture_s3tc"),r!==null){if(n===Zo)return r.COMPRESSED_RGB_S3TC_DXT1_EXT;if(n===Qo)return r.COMPRESSED_RGBA_S3TC_DXT1_EXT;if(n===el)return r.COMPRESSED_RGBA_S3TC_DXT3_EXT;if(n===tl)return r.COMPRESSED_RGBA_S3TC_DXT5_EXT}else return null;if(n===qc||n===Xc||n===Yc||n===jc)if(r=e.get("WEBGL_compressed_texture_pvrtc"),r!==null){if(n===qc)return r.COMPRESSED_RGB_PVRTC_4BPPV1_IMG;if(n===Xc)return r.COMPRESSED_RGB_PVRTC_2BPPV1_IMG;if(n===Yc)return r.COMPRESSED_RGBA_PVRTC_4BPPV1_IMG;if(n===jc)return r.COMPRESSED_RGBA_PVRTC_2BPPV1_IMG}else return null;if(n===Kc||n===Jc||n===Zc)if(r=e.get("WEBGL_compressed_texture_etc"),r!==null){if(n===Kc||n===Jc)return a===kt?r.COMPRESSED_SRGB8_ETC2:r.COMPRESSED_RGB8_ETC2;if(n===Zc)return a===kt?r.COMPRESSED_SRGB8_ALPHA8_ETC2_EAC:r.COMPRESSED_RGBA8_ETC2_EAC}else return null;if(n===Qc||n===eh||n===th||n===nh||n===ih||n===sh||n===rh||n===ah||n===oh||n===lh||n===ch||n===hh||n===dh||n===uh)if(r=e.get("WEBGL_compressed_texture_astc"),r!==null){if(n===Qc)return a===kt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_4x4_KHR:r.COMPRESSED_RGBA_ASTC_4x4_KHR;if(n===eh)return a===kt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_5x4_KHR:r.COMPRESSED_RGBA_ASTC_5x4_KHR;if(n===th)return a===kt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_5x5_KHR:r.COMPRESSED_RGBA_ASTC_5x5_KHR;if(n===nh)return a===kt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_6x5_KHR:r.COMPRESSED_RGBA_ASTC_6x5_KHR;if(n===ih)return a===kt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_6x6_KHR:r.COMPRESSED_RGBA_ASTC_6x6_KHR;if(n===sh)return a===kt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_8x5_KHR:r.COMPRESSED_RGBA_ASTC_8x5_KHR;if(n===rh)return a===kt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_8x6_KHR:r.COMPRESSED_RGBA_ASTC_8x6_KHR;if(n===ah)return a===kt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_8x8_KHR:r.COMPRESSED_RGBA_ASTC_8x8_KHR;if(n===oh)return a===kt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_10x5_KHR:r.COMPRESSED_RGBA_ASTC_10x5_KHR;if(n===lh)return a===kt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_10x6_KHR:r.COMPRESSED_RGBA_ASTC_10x6_KHR;if(n===ch)return a===kt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_10x8_KHR:r.COMPRESSED_RGBA_ASTC_10x8_KHR;if(n===hh)return a===kt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_10x10_KHR:r.COMPRESSED_RGBA_ASTC_10x10_KHR;if(n===dh)return a===kt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_12x10_KHR:r.COMPRESSED_RGBA_ASTC_12x10_KHR;if(n===uh)return a===kt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_12x12_KHR:r.COMPRESSED_RGBA_ASTC_12x12_KHR}else return null;if(n===nl||n===fh||n===ph)if(r=e.get("EXT_texture_compression_bptc"),r!==null){if(n===nl)return a===kt?r.COMPRESSED_SRGB_ALPHA_BPTC_UNORM_EXT:r.COMPRESSED_RGBA_BPTC_UNORM_EXT;if(n===fh)return r.COMPRESSED_RGB_BPTC_SIGNED_FLOAT_EXT;if(n===ph)return r.COMPRESSED_RGB_BPTC_UNSIGNED_FLOAT_EXT}else return null;if(n===ap||n===mh||n===gh||n===xh)if(r=e.get("EXT_texture_compression_rgtc"),r!==null){if(n===nl)return r.COMPRESSED_RED_RGTC1_EXT;if(n===mh)return r.COMPRESSED_SIGNED_RED_RGTC1_EXT;if(n===gh)return r.COMPRESSED_RED_GREEN_RGTC2_EXT;if(n===xh)return r.COMPRESSED_SIGNED_RED_GREEN_RGTC2_EXT}else return null;return n===ea?s.UNSIGNED_INT_24_8:s[n]!==void 0?s[n]:null}return{convert:t}}class ab extends An{constructor(e=[]){super(),this.isArrayCamera=!0,this.cameras=e}}class ri extends tn{constructor(){super(),this.isGroup=!0,this.type="Group"}}const ob={type:"move"};class Sc{constructor(){this._targetRay=null,this._grip=null,this._hand=null}getHandSpace(){return this._hand===null&&(this._hand=new ri,this._hand.matrixAutoUpdate=!1,this._hand.visible=!1,this._hand.joints={},this._hand.inputState={pinching:!1}),this._hand}getTargetRaySpace(){return this._targetRay===null&&(this._targetRay=new ri,this._targetRay.matrixAutoUpdate=!1,this._targetRay.visible=!1,this._targetRay.hasLinearVelocity=!1,this._targetRay.linearVelocity=new V,this._targetRay.hasAngularVelocity=!1,this._targetRay.angularVelocity=new V),this._targetRay}getGripSpace(){return this._grip===null&&(this._grip=new ri,this._grip.matrixAutoUpdate=!1,this._grip.visible=!1,this._grip.hasLinearVelocity=!1,this._grip.linearVelocity=new V,this._grip.hasAngularVelocity=!1,this._grip.angularVelocity=new V),this._grip}dispatchEvent(e){return this._targetRay!==null&&this._targetRay.dispatchEvent(e),this._grip!==null&&this._grip.dispatchEvent(e),this._hand!==null&&this._hand.dispatchEvent(e),this}connect(e){if(e&&e.hand){const t=this._hand;if(t)for(const n of e.hand.values())this._getHandJoint(t,n)}return this.dispatchEvent({type:"connected",data:e}),this}disconnect(e){return this.dispatchEvent({type:"disconnected",data:e}),this._targetRay!==null&&(this._targetRay.visible=!1),this._grip!==null&&(this._grip.visible=!1),this._hand!==null&&(this._hand.visible=!1),this}update(e,t,n){let i=null,r=null,a=null;const o=this._targetRay,l=this._grip,c=this._hand;if(e&&t.session.visibilityState!=="visible-blurred"){if(c&&e.hand){a=!0;for(const x of e.hand.values()){const p=t.getJointPose(x,n),m=this._getHandJoint(c,x);p!==null&&(m.matrix.fromArray(p.transform.matrix),m.matrix.decompose(m.position,m.rotation,m.scale),m.matrixWorldNeedsUpdate=!0,m.jointRadius=p.radius),m.visible=p!==null}const h=c.joints["index-finger-tip"],d=c.joints["thumb-tip"],u=h.position.distanceTo(d.position),f=.02,g=.005;c.inputState.pinching&&u>f+g?(c.inputState.pinching=!1,this.dispatchEvent({type:"pinchend",handedness:e.handedness,target:this})):!c.inputState.pinching&&u<=f-g&&(c.inputState.pinching=!0,this.dispatchEvent({type:"pinchstart",handedness:e.handedness,target:this}))}else l!==null&&e.gripSpace&&(r=t.getPose(e.gripSpace,n),r!==null&&(l.matrix.fromArray(r.transform.matrix),l.matrix.decompose(l.position,l.rotation,l.scale),l.matrixWorldNeedsUpdate=!0,r.linearVelocity?(l.hasLinearVelocity=!0,l.linearVelocity.copy(r.linearVelocity)):l.hasLinearVelocity=!1,r.angularVelocity?(l.hasAngularVelocity=!0,l.angularVelocity.copy(r.angularVelocity)):l.hasAngularVelocity=!1));o!==null&&(i=t.getPose(e.targetRaySpace,n),i===null&&r!==null&&(i=r),i!==null&&(o.matrix.fromArray(i.transform.matrix),o.matrix.decompose(o.position,o.rotation,o.scale),o.matrixWorldNeedsUpdate=!0,i.linearVelocity?(o.hasLinearVelocity=!0,o.linearVelocity.copy(i.linearVelocity)):o.hasLinearVelocity=!1,i.angularVelocity?(o.hasAngularVelocity=!0,o.angularVelocity.copy(i.angularVelocity)):o.hasAngularVelocity=!1,this.dispatchEvent(ob)))}return o!==null&&(o.visible=i!==null),l!==null&&(l.visible=r!==null),c!==null&&(c.visible=a!==null),this}_getHandJoint(e,t){if(e.joints[t.jointName]===void 0){const n=new ri;n.matrixAutoUpdate=!1,n.visible=!1,e.joints[t.jointName]=n,e.add(n)}return e.joints[t.jointName]}}const lb=`
void main() {

	gl_Position = vec4( position, 1.0 );

}`,cb=`
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

}`;class hb{constructor(){this.texture=null,this.mesh=null,this.depthNear=0,this.depthFar=0}init(e,t,n){if(this.texture===null){const i=new On,r=e.properties.get(i);r.__webglTexture=t.texture,(t.depthNear!=n.depthNear||t.depthFar!=n.depthFar)&&(this.depthNear=t.depthNear,this.depthFar=t.depthFar),this.texture=i}}getMesh(e){if(this.texture!==null&&this.mesh===null){const t=e.cameras[0].viewport,n=new Ts({vertexShader:lb,fragmentShader:cb,uniforms:{depthColor:{value:this.texture},depthWidth:{value:t.z},depthHeight:{value:t.w}}});this.mesh=new Xt(new so(20,20),n)}return this.mesh}reset(){this.texture=null,this.mesh=null}getDepthTexture(){return this.texture}}class db extends da{constructor(e,t){super();const n=this;let i=null,r=1,a=null,o="local-floor",l=1,c=null,h=null,d=null,u=null,f=null,g=null;const x=new hb,p=t.getContextAttributes();let m=null,b=null;const _=[],S=[],I=new Xe;let A=null;const R=new An;R.layers.enable(1),R.viewport=new rn;const N=new An;N.layers.enable(2),N.viewport=new rn;const M=[R,N],y=new ab;y.layers.enable(1),y.layers.enable(2);let P=null,X=null;this.cameraAutoUpdate=!0,this.enabled=!1,this.isPresenting=!1,this.getController=function(ie){let he=_[ie];return he===void 0&&(he=new Sc,_[ie]=he),he.getTargetRaySpace()},this.getControllerGrip=function(ie){let he=_[ie];return he===void 0&&(he=new Sc,_[ie]=he),he.getGripSpace()},this.getHand=function(ie){let he=_[ie];return he===void 0&&(he=new Sc,_[ie]=he),he.getHandSpace()};function H(ie){const he=S.indexOf(ie.inputSource);if(he===-1)return;const Se=_[he];Se!==void 0&&(Se.update(ie.inputSource,ie.frame,c||a),Se.dispatchEvent({type:ie.type,data:ie.inputSource}))}function J(){i.removeEventListener("select",H),i.removeEventListener("selectstart",H),i.removeEventListener("selectend",H),i.removeEventListener("squeeze",H),i.removeEventListener("squeezestart",H),i.removeEventListener("squeezeend",H),i.removeEventListener("end",J),i.removeEventListener("inputsourceschange",q);for(let ie=0;ie<_.length;ie++){const he=S[ie];he!==null&&(S[ie]=null,_[ie].disconnect(he))}P=null,X=null,x.reset(),e.setRenderTarget(m),f=null,u=null,d=null,i=null,b=null,be.stop(),n.isPresenting=!1,e.setPixelRatio(A),e.setSize(I.width,I.height,!1),n.dispatchEvent({type:"sessionend"})}this.setFramebufferScaleFactor=function(ie){r=ie,n.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change framebuffer scale while presenting.")},this.setReferenceSpaceType=function(ie){o=ie,n.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change reference space type while presenting.")},this.getReferenceSpace=function(){return c||a},this.setReferenceSpace=function(ie){c=ie},this.getBaseLayer=function(){return u!==null?u:f},this.getBinding=function(){return d},this.getFrame=function(){return g},this.getSession=function(){return i},this.setSession=async function(ie){if(i=ie,i!==null){if(m=e.getRenderTarget(),i.addEventListener("select",H),i.addEventListener("selectstart",H),i.addEventListener("selectend",H),i.addEventListener("squeeze",H),i.addEventListener("squeezestart",H),i.addEventListener("squeezeend",H),i.addEventListener("end",J),i.addEventListener("inputsourceschange",q),p.xrCompatible!==!0&&await t.makeXRCompatible(),A=e.getPixelRatio(),e.getSize(I),i.renderState.layers===void 0){const he={antialias:p.antialias,alpha:!0,depth:p.depth,stencil:p.stencil,framebufferScaleFactor:r};f=new XRWebGLLayer(i,t,he),i.updateRenderState({baseLayer:f}),e.setPixelRatio(1),e.setSize(f.framebufferWidth,f.framebufferHeight,!1),b=new er(f.framebufferWidth,f.framebufferHeight,{format:vi,type:ss,colorSpace:e.outputColorSpace,stencilBuffer:p.stencil})}else{let he=null,Se=null,fe=null;p.depth&&(fe=p.stencil?t.DEPTH24_STENCIL8:t.DEPTH_COMPONENT24,he=p.stencil?ta:$r,Se=p.stencil?ea:Qs);const ze={colorFormat:t.RGBA8,depthFormat:fe,scaleFactor:r};d=new XRWebGLBinding(i,t),u=d.createProjectionLayer(ze),i.updateRenderState({layers:[u]}),e.setPixelRatio(1),e.setSize(u.textureWidth,u.textureHeight,!1),b=new er(u.textureWidth,u.textureHeight,{format:vi,type:ss,depthTexture:new _p(u.textureWidth,u.textureHeight,Se,void 0,void 0,void 0,void 0,void 0,void 0,he),stencilBuffer:p.stencil,colorSpace:e.outputColorSpace,samples:p.antialias?4:0,resolveDepthBuffer:u.ignoreDepthValues===!1})}b.isXRRenderTarget=!0,this.setFoveation(l),c=null,a=await i.requestReferenceSpace(o),be.setContext(i),be.start(),n.isPresenting=!0,n.dispatchEvent({type:"sessionstart"})}},this.getEnvironmentBlendMode=function(){if(i!==null)return i.environmentBlendMode},this.getDepthTexture=function(){return x.getDepthTexture()};function q(ie){for(let he=0;he<ie.removed.length;he++){const Se=ie.removed[he],fe=S.indexOf(Se);fe>=0&&(S[fe]=null,_[fe].disconnect(Se))}for(let he=0;he<ie.added.length;he++){const Se=ie.added[he];let fe=S.indexOf(Se);if(fe===-1){for(let We=0;We<_.length;We++)if(We>=S.length){S.push(Se),fe=We;break}else if(S[We]===null){S[We]=Se,fe=We;break}if(fe===-1)break}const ze=_[fe];ze&&ze.connect(Se)}}const ee=new V,j=new V;function ne(ie,he,Se){ee.setFromMatrixPosition(he.matrixWorld),j.setFromMatrixPosition(Se.matrixWorld);const fe=ee.distanceTo(j),ze=he.projectionMatrix.elements,We=Se.projectionMatrix.elements,Oe=ze[14]/(ze[10]-1),pt=ze[14]/(ze[10]+1),k=(ze[9]+1)/ze[5],ut=(ze[9]-1)/ze[5],st=(ze[8]-1)/ze[0],ct=(We[8]+1)/We[0],ke=Oe*st,wt=Oe*ct,Ye=fe/(-st+ct),qe=Ye*-st;if(he.matrixWorld.decompose(ie.position,ie.quaternion,ie.scale),ie.translateX(qe),ie.translateZ(Ye),ie.matrixWorld.compose(ie.position,ie.quaternion,ie.scale),ie.matrixWorldInverse.copy(ie.matrixWorld).invert(),ze[10]===-1)ie.projectionMatrix.copy(he.projectionMatrix),ie.projectionMatrixInverse.copy(he.projectionMatrixInverse);else{const U=Oe+Ye,E=pt+Ye,Q=ke-qe,le=wt+(fe-qe),te=k*pt/E*U,$=ut*pt/E*U;ie.projectionMatrix.makePerspective(Q,le,te,$,U,E),ie.projectionMatrixInverse.copy(ie.projectionMatrix).invert()}}function ge(ie,he){he===null?ie.matrixWorld.copy(ie.matrix):ie.matrixWorld.multiplyMatrices(he.matrixWorld,ie.matrix),ie.matrixWorldInverse.copy(ie.matrixWorld).invert()}this.updateCamera=function(ie){if(i===null)return;let he=ie.near,Se=ie.far;x.texture!==null&&(x.depthNear>0&&(he=x.depthNear),x.depthFar>0&&(Se=x.depthFar)),y.near=N.near=R.near=he,y.far=N.far=R.far=Se,(P!==y.near||X!==y.far)&&(i.updateRenderState({depthNear:y.near,depthFar:y.far}),P=y.near,X=y.far);const fe=ie.parent,ze=y.cameras;ge(y,fe);for(let We=0;We<ze.length;We++)ge(ze[We],fe);ze.length===2?ne(y,R,N):y.projectionMatrix.copy(R.projectionMatrix),ue(ie,y,fe)};function ue(ie,he,Se){Se===null?ie.matrix.copy(he.matrixWorld):(ie.matrix.copy(Se.matrixWorld),ie.matrix.invert(),ie.matrix.multiply(he.matrixWorld)),ie.matrix.decompose(ie.position,ie.quaternion,ie.scale),ie.updateMatrixWorld(!0),ie.projectionMatrix.copy(he.projectionMatrix),ie.projectionMatrixInverse.copy(he.projectionMatrixInverse),ie.isPerspectiveCamera&&(ie.fov=Ka*2*Math.atan(1/ie.projectionMatrix.elements[5]),ie.zoom=1)}this.getCamera=function(){return y},this.getFoveation=function(){if(!(u===null&&f===null))return l},this.setFoveation=function(ie){l=ie,u!==null&&(u.fixedFoveation=ie),f!==null&&f.fixedFoveation!==void 0&&(f.fixedFoveation=ie)},this.hasDepthSensing=function(){return x.texture!==null},this.getDepthSensingMesh=function(){return x.getMesh(y)};let ye=null;function Te(ie,he){if(h=he.getViewerPose(c||a),g=he,h!==null){const Se=h.views;f!==null&&(e.setRenderTargetFramebuffer(b,f.framebuffer),e.setRenderTarget(b));let fe=!1;Se.length!==y.cameras.length&&(y.cameras.length=0,fe=!0);for(let We=0;We<Se.length;We++){const Oe=Se[We];let pt=null;if(f!==null)pt=f.getViewport(Oe);else{const ut=d.getViewSubImage(u,Oe);pt=ut.viewport,We===0&&(e.setRenderTargetTextures(b,ut.colorTexture,u.ignoreDepthValues?void 0:ut.depthStencilTexture),e.setRenderTarget(b))}let k=M[We];k===void 0&&(k=new An,k.layers.enable(We),k.viewport=new rn,M[We]=k),k.matrix.fromArray(Oe.transform.matrix),k.matrix.decompose(k.position,k.quaternion,k.scale),k.projectionMatrix.fromArray(Oe.projectionMatrix),k.projectionMatrixInverse.copy(k.projectionMatrix).invert(),k.viewport.set(pt.x,pt.y,pt.width,pt.height),We===0&&(y.matrix.copy(k.matrix),y.matrix.decompose(y.position,y.quaternion,y.scale)),fe===!0&&y.cameras.push(k)}const ze=i.enabledFeatures;if(ze&&ze.includes("depth-sensing")){const We=d.getDepthInformation(Se[0]);We&&We.isValid&&We.texture&&x.init(e,We,i.renderState)}}for(let Se=0;Se<_.length;Se++){const fe=S[Se],ze=_[Se];fe!==null&&ze!==void 0&&ze.update(fe,he,c||a)}ye&&ye(ie,he),he.detectedPlanes&&n.dispatchEvent({type:"planesdetected",data:he}),g=null}const be=new vp;be.setAnimationLoop(Te),this.setAnimationLoop=function(ie){ye=ie},this.dispose=function(){}}}const Vs=new Ni,ub=new Bt;function fb(s,e){function t(p,m){p.matrixAutoUpdate===!0&&p.updateMatrix(),m.value.copy(p.matrix)}function n(p,m){m.color.getRGB(p.fogColor.value,mp(s)),m.isFog?(p.fogNear.value=m.near,p.fogFar.value=m.far):m.isFogExp2&&(p.fogDensity.value=m.density)}function i(p,m,b,_,S){m.isMeshBasicMaterial||m.isMeshLambertMaterial?r(p,m):m.isMeshToonMaterial?(r(p,m),d(p,m)):m.isMeshPhongMaterial?(r(p,m),h(p,m)):m.isMeshStandardMaterial?(r(p,m),u(p,m),m.isMeshPhysicalMaterial&&f(p,m,S)):m.isMeshMatcapMaterial?(r(p,m),g(p,m)):m.isMeshDepthMaterial?r(p,m):m.isMeshDistanceMaterial?(r(p,m),x(p,m)):m.isMeshNormalMaterial?r(p,m):m.isLineBasicMaterial?(a(p,m),m.isLineDashedMaterial&&o(p,m)):m.isPointsMaterial?l(p,m,b,_):m.isSpriteMaterial?c(p,m):m.isShadowMaterial?(p.color.value.copy(m.color),p.opacity.value=m.opacity):m.isShaderMaterial&&(m.uniformsNeedUpdate=!1)}function r(p,m){p.opacity.value=m.opacity,m.color&&p.diffuse.value.copy(m.color),m.emissive&&p.emissive.value.copy(m.emissive).multiplyScalar(m.emissiveIntensity),m.map&&(p.map.value=m.map,t(m.map,p.mapTransform)),m.alphaMap&&(p.alphaMap.value=m.alphaMap,t(m.alphaMap,p.alphaMapTransform)),m.bumpMap&&(p.bumpMap.value=m.bumpMap,t(m.bumpMap,p.bumpMapTransform),p.bumpScale.value=m.bumpScale,m.side===zn&&(p.bumpScale.value*=-1)),m.normalMap&&(p.normalMap.value=m.normalMap,t(m.normalMap,p.normalMapTransform),p.normalScale.value.copy(m.normalScale),m.side===zn&&p.normalScale.value.negate()),m.displacementMap&&(p.displacementMap.value=m.displacementMap,t(m.displacementMap,p.displacementMapTransform),p.displacementScale.value=m.displacementScale,p.displacementBias.value=m.displacementBias),m.emissiveMap&&(p.emissiveMap.value=m.emissiveMap,t(m.emissiveMap,p.emissiveMapTransform)),m.specularMap&&(p.specularMap.value=m.specularMap,t(m.specularMap,p.specularMapTransform)),m.alphaTest>0&&(p.alphaTest.value=m.alphaTest);const b=e.get(m),_=b.envMap,S=b.envMapRotation;_&&(p.envMap.value=_,Vs.copy(S),Vs.x*=-1,Vs.y*=-1,Vs.z*=-1,_.isCubeTexture&&_.isRenderTargetTexture===!1&&(Vs.y*=-1,Vs.z*=-1),p.envMapRotation.value.setFromMatrix4(ub.makeRotationFromEuler(Vs)),p.flipEnvMap.value=_.isCubeTexture&&_.isRenderTargetTexture===!1?-1:1,p.reflectivity.value=m.reflectivity,p.ior.value=m.ior,p.refractionRatio.value=m.refractionRatio),m.lightMap&&(p.lightMap.value=m.lightMap,p.lightMapIntensity.value=m.lightMapIntensity,t(m.lightMap,p.lightMapTransform)),m.aoMap&&(p.aoMap.value=m.aoMap,p.aoMapIntensity.value=m.aoMapIntensity,t(m.aoMap,p.aoMapTransform))}function a(p,m){p.diffuse.value.copy(m.color),p.opacity.value=m.opacity,m.map&&(p.map.value=m.map,t(m.map,p.mapTransform))}function o(p,m){p.dashSize.value=m.dashSize,p.totalSize.value=m.dashSize+m.gapSize,p.scale.value=m.scale}function l(p,m,b,_){p.diffuse.value.copy(m.color),p.opacity.value=m.opacity,p.size.value=m.size*b,p.scale.value=_*.5,m.map&&(p.map.value=m.map,t(m.map,p.uvTransform)),m.alphaMap&&(p.alphaMap.value=m.alphaMap,t(m.alphaMap,p.alphaMapTransform)),m.alphaTest>0&&(p.alphaTest.value=m.alphaTest)}function c(p,m){p.diffuse.value.copy(m.color),p.opacity.value=m.opacity,p.rotation.value=m.rotation,m.map&&(p.map.value=m.map,t(m.map,p.mapTransform)),m.alphaMap&&(p.alphaMap.value=m.alphaMap,t(m.alphaMap,p.alphaMapTransform)),m.alphaTest>0&&(p.alphaTest.value=m.alphaTest)}function h(p,m){p.specular.value.copy(m.specular),p.shininess.value=Math.max(m.shininess,1e-4)}function d(p,m){m.gradientMap&&(p.gradientMap.value=m.gradientMap)}function u(p,m){p.metalness.value=m.metalness,m.metalnessMap&&(p.metalnessMap.value=m.metalnessMap,t(m.metalnessMap,p.metalnessMapTransform)),p.roughness.value=m.roughness,m.roughnessMap&&(p.roughnessMap.value=m.roughnessMap,t(m.roughnessMap,p.roughnessMapTransform)),m.envMap&&(p.envMapIntensity.value=m.envMapIntensity)}function f(p,m,b){p.ior.value=m.ior,m.sheen>0&&(p.sheenColor.value.copy(m.sheenColor).multiplyScalar(m.sheen),p.sheenRoughness.value=m.sheenRoughness,m.sheenColorMap&&(p.sheenColorMap.value=m.sheenColorMap,t(m.sheenColorMap,p.sheenColorMapTransform)),m.sheenRoughnessMap&&(p.sheenRoughnessMap.value=m.sheenRoughnessMap,t(m.sheenRoughnessMap,p.sheenRoughnessMapTransform))),m.clearcoat>0&&(p.clearcoat.value=m.clearcoat,p.clearcoatRoughness.value=m.clearcoatRoughness,m.clearcoatMap&&(p.clearcoatMap.value=m.clearcoatMap,t(m.clearcoatMap,p.clearcoatMapTransform)),m.clearcoatRoughnessMap&&(p.clearcoatRoughnessMap.value=m.clearcoatRoughnessMap,t(m.clearcoatRoughnessMap,p.clearcoatRoughnessMapTransform)),m.clearcoatNormalMap&&(p.clearcoatNormalMap.value=m.clearcoatNormalMap,t(m.clearcoatNormalMap,p.clearcoatNormalMapTransform),p.clearcoatNormalScale.value.copy(m.clearcoatNormalScale),m.side===zn&&p.clearcoatNormalScale.value.negate())),m.dispersion>0&&(p.dispersion.value=m.dispersion),m.iridescence>0&&(p.iridescence.value=m.iridescence,p.iridescenceIOR.value=m.iridescenceIOR,p.iridescenceThicknessMinimum.value=m.iridescenceThicknessRange[0],p.iridescenceThicknessMaximum.value=m.iridescenceThicknessRange[1],m.iridescenceMap&&(p.iridescenceMap.value=m.iridescenceMap,t(m.iridescenceMap,p.iridescenceMapTransform)),m.iridescenceThicknessMap&&(p.iridescenceThicknessMap.value=m.iridescenceThicknessMap,t(m.iridescenceThicknessMap,p.iridescenceThicknessMapTransform))),m.transmission>0&&(p.transmission.value=m.transmission,p.transmissionSamplerMap.value=b.texture,p.transmissionSamplerSize.value.set(b.width,b.height),m.transmissionMap&&(p.transmissionMap.value=m.transmissionMap,t(m.transmissionMap,p.transmissionMapTransform)),p.thickness.value=m.thickness,m.thicknessMap&&(p.thicknessMap.value=m.thicknessMap,t(m.thicknessMap,p.thicknessMapTransform)),p.attenuationDistance.value=m.attenuationDistance,p.attenuationColor.value.copy(m.attenuationColor)),m.anisotropy>0&&(p.anisotropyVector.value.set(m.anisotropy*Math.cos(m.anisotropyRotation),m.anisotropy*Math.sin(m.anisotropyRotation)),m.anisotropyMap&&(p.anisotropyMap.value=m.anisotropyMap,t(m.anisotropyMap,p.anisotropyMapTransform))),p.specularIntensity.value=m.specularIntensity,p.specularColor.value.copy(m.specularColor),m.specularColorMap&&(p.specularColorMap.value=m.specularColorMap,t(m.specularColorMap,p.specularColorMapTransform)),m.specularIntensityMap&&(p.specularIntensityMap.value=m.specularIntensityMap,t(m.specularIntensityMap,p.specularIntensityMapTransform))}function g(p,m){m.matcap&&(p.matcap.value=m.matcap)}function x(p,m){const b=e.get(m).light;p.referencePosition.value.setFromMatrixPosition(b.matrixWorld),p.nearDistance.value=b.shadow.camera.near,p.farDistance.value=b.shadow.camera.far}return{refreshFogUniforms:n,refreshMaterialUniforms:i}}function pb(s,e,t,n){let i={},r={},a=[];const o=s.getParameter(s.MAX_UNIFORM_BUFFER_BINDINGS);function l(b,_){const S=_.program;n.uniformBlockBinding(b,S)}function c(b,_){let S=i[b.id];S===void 0&&(g(b),S=h(b),i[b.id]=S,b.addEventListener("dispose",p));const I=_.program;n.updateUBOMapping(b,I);const A=e.render.frame;r[b.id]!==A&&(u(b),r[b.id]=A)}function h(b){const _=d();b.__bindingPointIndex=_;const S=s.createBuffer(),I=b.__size,A=b.usage;return s.bindBuffer(s.UNIFORM_BUFFER,S),s.bufferData(s.UNIFORM_BUFFER,I,A),s.bindBuffer(s.UNIFORM_BUFFER,null),s.bindBufferBase(s.UNIFORM_BUFFER,_,S),S}function d(){for(let b=0;b<o;b++)if(a.indexOf(b)===-1)return a.push(b),b;return console.error("THREE.WebGLRenderer: Maximum number of simultaneously usable uniforms groups reached."),0}function u(b){const _=i[b.id],S=b.uniforms,I=b.__cache;s.bindBuffer(s.UNIFORM_BUFFER,_);for(let A=0,R=S.length;A<R;A++){const N=Array.isArray(S[A])?S[A]:[S[A]];for(let M=0,y=N.length;M<y;M++){const P=N[M];if(f(P,A,M,I)===!0){const X=P.__offset,H=Array.isArray(P.value)?P.value:[P.value];let J=0;for(let q=0;q<H.length;q++){const ee=H[q],j=x(ee);typeof ee=="number"||typeof ee=="boolean"?(P.__data[0]=ee,s.bufferSubData(s.UNIFORM_BUFFER,X+J,P.__data)):ee.isMatrix3?(P.__data[0]=ee.elements[0],P.__data[1]=ee.elements[1],P.__data[2]=ee.elements[2],P.__data[3]=0,P.__data[4]=ee.elements[3],P.__data[5]=ee.elements[4],P.__data[6]=ee.elements[5],P.__data[7]=0,P.__data[8]=ee.elements[6],P.__data[9]=ee.elements[7],P.__data[10]=ee.elements[8],P.__data[11]=0):(ee.toArray(P.__data,J),J+=j.storage/Float32Array.BYTES_PER_ELEMENT)}s.bufferSubData(s.UNIFORM_BUFFER,X,P.__data)}}}s.bindBuffer(s.UNIFORM_BUFFER,null)}function f(b,_,S,I){const A=b.value,R=_+"_"+S;if(I[R]===void 0)return typeof A=="number"||typeof A=="boolean"?I[R]=A:I[R]=A.clone(),!0;{const N=I[R];if(typeof A=="number"||typeof A=="boolean"){if(N!==A)return I[R]=A,!0}else if(N.equals(A)===!1)return N.copy(A),!0}return!1}function g(b){const _=b.uniforms;let S=0;const I=16;for(let R=0,N=_.length;R<N;R++){const M=Array.isArray(_[R])?_[R]:[_[R]];for(let y=0,P=M.length;y<P;y++){const X=M[y],H=Array.isArray(X.value)?X.value:[X.value];for(let J=0,q=H.length;J<q;J++){const ee=H[J],j=x(ee),ne=S%I,ge=ne%j.boundary,ue=ne+ge;S+=ge,ue!==0&&I-ue<j.storage&&(S+=I-ue),X.__data=new Float32Array(j.storage/Float32Array.BYTES_PER_ELEMENT),X.__offset=S,S+=j.storage}}}const A=S%I;return A>0&&(S+=I-A),b.__size=S,b.__cache={},this}function x(b){const _={boundary:0,storage:0};return typeof b=="number"||typeof b=="boolean"?(_.boundary=4,_.storage=4):b.isVector2?(_.boundary=8,_.storage=8):b.isVector3||b.isColor?(_.boundary=16,_.storage=12):b.isVector4?(_.boundary=16,_.storage=16):b.isMatrix3?(_.boundary=48,_.storage=48):b.isMatrix4?(_.boundary=64,_.storage=64):b.isTexture?console.warn("THREE.WebGLRenderer: Texture samplers can not be part of an uniforms group."):console.warn("THREE.WebGLRenderer: Unsupported uniform value type.",b),_}function p(b){const _=b.target;_.removeEventListener("dispose",p);const S=a.indexOf(_.__bindingPointIndex);a.splice(S,1),s.deleteBuffer(i[_.id]),delete i[_.id],delete r[_.id]}function m(){for(const b in i)s.deleteBuffer(i[b]);a=[],i={},r={}}return{bind:l,update:c,dispose:m}}class mb{constructor(e={}){const{canvas:t=rx(),context:n=null,depth:i=!0,stencil:r=!1,alpha:a=!1,antialias:o=!1,premultipliedAlpha:l=!0,preserveDrawingBuffer:c=!1,powerPreference:h="default",failIfMajorPerformanceCaveat:d=!1}=e;this.isWebGLRenderer=!0;let u;if(n!==null){if(typeof WebGLRenderingContext<"u"&&n instanceof WebGLRenderingContext)throw new Error("THREE.WebGLRenderer: WebGL 1 is not supported since r163.");u=n.getContextAttributes().alpha}else u=a;const f=new Uint32Array(4),g=new Int32Array(4);let x=null,p=null;const m=[],b=[];this.domElement=t,this.debug={checkShaderErrors:!0,onShaderError:null},this.autoClear=!0,this.autoClearColor=!0,this.autoClearDepth=!0,this.autoClearStencil=!0,this.sortObjects=!0,this.clippingPlanes=[],this.localClippingEnabled=!1,this._outputColorSpace=Di,this.toneMapping=Ss,this.toneMappingExposure=1;const _=this;let S=!1,I=0,A=0,R=null,N=-1,M=null;const y=new rn,P=new rn;let X=null;const H=new nt(0);let J=0,q=t.width,ee=t.height,j=1,ne=null,ge=null;const ue=new rn(0,0,q,ee),ye=new rn(0,0,q,ee);let Te=!1;const be=new $h;let ie=!1,he=!1;const Se=new Bt,fe=new V,ze=new rn,We={background:null,fog:null,environment:null,overrideMaterial:null,isScene:!0};let Oe=!1;function pt(){return R===null?j:1}let k=n;function ut(C,W){return t.getContext(C,W)}try{const C={alpha:!0,depth:i,stencil:r,antialias:o,premultipliedAlpha:l,preserveDrawingBuffer:c,powerPreference:h,failIfMajorPerformanceCaveat:d};if("setAttribute"in t&&t.setAttribute("data-engine",`three.js r${Nh}`),t.addEventListener("webglcontextlost",se,!1),t.addEventListener("webglcontextrestored",re,!1),t.addEventListener("webglcontextcreationerror",_e,!1),k===null){const W="webgl2";if(k=ut(W,C),k===null)throw ut(W)?new Error("Error creating WebGL context with your selected attributes."):new Error("Error creating WebGL context.")}}catch(C){throw console.error("THREE.WebGLRenderer: "+C.message),C}let st,ct,ke,wt,Ye,qe,U,E,Q,le,te,$,Ee,xe,Ce,Je,me,Ae,Ze,He,we,Ve,B,ce;function O(){st=new b_(k),st.init(),Ve=new rb(k,st),ct=new m_(k,st,e,Ve),ke=new nb(k),wt=new w_(k),Ye=new Vy,qe=new sb(k,st,ke,Ye,ct,Ve,wt),U=new x_(_),E=new y_(_),Q=new Lx(k),B=new f_(k,Q),le=new S_(k,Q,wt,B),te=new T_(k,le,Q,wt),Ze=new E_(k,ct,qe),Je=new g_(Ye),$=new Hy(_,U,E,st,ct,B,Je),Ee=new fb(_,Ye),xe=new Wy,Ce=new Ky(st),Ae=new u_(_,U,E,ke,te,u,l),me=new tb(_,te,ct),ce=new pb(k,wt,ct,ke),He=new p_(k,st,wt),we=new M_(k,st,wt),wt.programs=$.programs,_.capabilities=ct,_.extensions=st,_.properties=Ye,_.renderLists=xe,_.shadowMap=me,_.state=ke,_.info=wt}O();const ae=new db(_,k);this.xr=ae,this.getContext=function(){return k},this.getContextAttributes=function(){return k.getContextAttributes()},this.forceContextLoss=function(){const C=st.get("WEBGL_lose_context");C&&C.loseContext()},this.forceContextRestore=function(){const C=st.get("WEBGL_lose_context");C&&C.restoreContext()},this.getPixelRatio=function(){return j},this.setPixelRatio=function(C){C!==void 0&&(j=C,this.setSize(q,ee,!1))},this.getSize=function(C){return C.set(q,ee)},this.setSize=function(C,W,Z=!0){if(ae.isPresenting){console.warn("THREE.WebGLRenderer: Can't change size while VR device is presenting.");return}q=C,ee=W,t.width=Math.floor(C*j),t.height=Math.floor(W*j),Z===!0&&(t.style.width=C+"px",t.style.height=W+"px"),this.setViewport(0,0,C,W)},this.getDrawingBufferSize=function(C){return C.set(q*j,ee*j).floor()},this.setDrawingBufferSize=function(C,W,Z){q=C,ee=W,j=Z,t.width=Math.floor(C*Z),t.height=Math.floor(W*Z),this.setViewport(0,0,C,W)},this.getCurrentViewport=function(C){return C.copy(y)},this.getViewport=function(C){return C.copy(ue)},this.setViewport=function(C,W,Z,Y){C.isVector4?ue.set(C.x,C.y,C.z,C.w):ue.set(C,W,Z,Y),ke.viewport(y.copy(ue).multiplyScalar(j).round())},this.getScissor=function(C){return C.copy(ye)},this.setScissor=function(C,W,Z,Y){C.isVector4?ye.set(C.x,C.y,C.z,C.w):ye.set(C,W,Z,Y),ke.scissor(P.copy(ye).multiplyScalar(j).round())},this.getScissorTest=function(){return Te},this.setScissorTest=function(C){ke.setScissorTest(Te=C)},this.setOpaqueSort=function(C){ne=C},this.setTransparentSort=function(C){ge=C},this.getClearColor=function(C){return C.copy(Ae.getClearColor())},this.setClearColor=function(){Ae.setClearColor.apply(Ae,arguments)},this.getClearAlpha=function(){return Ae.getClearAlpha()},this.setClearAlpha=function(){Ae.setClearAlpha.apply(Ae,arguments)},this.clear=function(C=!0,W=!0,Z=!0){let Y=0;if(C){let G=!1;if(R!==null){const de=R.texture.format;G=de===Hh||de===zh||de===Bh}if(G){const de=R.texture.type,Pe=de===ss||de===Qs||de===ja||de===ea||de===Oh||de===kh,Le=Ae.getClearColor(),Ne=Ae.getClearAlpha(),Qe=Le.r,et=Le.g,Be=Le.b;Pe?(f[0]=Qe,f[1]=et,f[2]=Be,f[3]=Ne,k.clearBufferuiv(k.COLOR,0,f)):(g[0]=Qe,g[1]=et,g[2]=Be,g[3]=Ne,k.clearBufferiv(k.COLOR,0,g))}else Y|=k.COLOR_BUFFER_BIT}W&&(Y|=k.DEPTH_BUFFER_BIT),Z&&(Y|=k.STENCIL_BUFFER_BIT,this.state.buffers.stencil.setMask(4294967295)),k.clear(Y)},this.clearColor=function(){this.clear(!0,!1,!1)},this.clearDepth=function(){this.clear(!1,!0,!1)},this.clearStencil=function(){this.clear(!1,!1,!0)},this.dispose=function(){t.removeEventListener("webglcontextlost",se,!1),t.removeEventListener("webglcontextrestored",re,!1),t.removeEventListener("webglcontextcreationerror",_e,!1),xe.dispose(),Ce.dispose(),Ye.dispose(),U.dispose(),E.dispose(),te.dispose(),B.dispose(),ce.dispose(),$.dispose(),ae.dispose(),ae.removeEventListener("sessionstart",zt),ae.removeEventListener("sessionend",Ht),cn.stop()};function se(C){C.preventDefault(),console.log("THREE.WebGLRenderer: Context Lost."),S=!0}function re(){console.log("THREE.WebGLRenderer: Context Restored."),S=!1;const C=wt.autoReset,W=me.enabled,Z=me.autoUpdate,Y=me.needsUpdate,G=me.type;O(),wt.autoReset=C,me.enabled=W,me.autoUpdate=Z,me.needsUpdate=Y,me.type=G}function _e(C){console.error("THREE.WebGLRenderer: A WebGL context could not be created. Reason: ",C.statusMessage)}function Ke(C){const W=C.target;W.removeEventListener("dispose",Ke),ot(W)}function ot(C){xt(C),Ye.remove(C)}function xt(C){const W=Ye.get(C).programs;W!==void 0&&(W.forEach(function(Z){$.releaseProgram(Z)}),C.isShaderMaterial&&$.releaseShaderCache(C))}this.renderBufferDirect=function(C,W,Z,Y,G,de){W===null&&(W=We);const Pe=G.isMesh&&G.matrixWorld.determinant()<0,Le=Ol(C,W,Z,Y,G);ke.setMaterial(Y,Pe);let Ne=Z.index,Qe=1;if(Y.wireframe===!0){if(Ne=le.getWireframeAttribute(Z),Ne===void 0)return;Qe=2}const et=Z.drawRange,Be=Z.attributes.position;let ht=et.start*Qe,Pt=(et.start+et.count)*Qe;de!==null&&(ht=Math.max(ht,de.start*Qe),Pt=Math.min(Pt,(de.start+de.count)*Qe)),Ne!==null?(ht=Math.max(ht,0),Pt=Math.min(Pt,Ne.count)):Be!=null&&(ht=Math.max(ht,0),Pt=Math.min(Pt,Be.count));const Lt=Pt-ht;if(Lt<0||Lt===1/0)return;B.setup(G,Y,Le,Z,Ne);let _n,mt=He;if(Ne!==null&&(_n=Q.get(Ne),mt=we,mt.setIndex(_n)),G.isMesh)Y.wireframe===!0?(ke.setLineWidth(Y.wireframeLinewidth*pt()),mt.setMode(k.LINES)):mt.setMode(k.TRIANGLES);else if(G.isLine){let Ge=Y.linewidth;Ge===void 0&&(Ge=1),ke.setLineWidth(Ge*pt()),G.isLineSegments?mt.setMode(k.LINES):G.isLineLoop?mt.setMode(k.LINE_LOOP):mt.setMode(k.LINE_STRIP)}else G.isPoints?mt.setMode(k.POINTS):G.isSprite&&mt.setMode(k.TRIANGLES);if(G.isBatchedMesh)if(G._multiDrawInstances!==null)mt.renderMultiDrawInstances(G._multiDrawStarts,G._multiDrawCounts,G._multiDrawCount,G._multiDrawInstances);else if(st.get("WEBGL_multi_draw"))mt.renderMultiDraw(G._multiDrawStarts,G._multiDrawCounts,G._multiDrawCount);else{const Ge=G._multiDrawStarts,Yt=G._multiDrawCounts,gt=G._multiDrawCount,Dt=Ne?Q.get(Ne).bytesPerElement:1,Hi=Ye.get(Y).currentProgram.getUniforms();for(let Mn=0;Mn<gt;Mn++)Hi.setValue(k,"_gl_DrawID",Mn),mt.render(Ge[Mn]/Dt,Yt[Mn])}else if(G.isInstancedMesh)mt.renderInstances(ht,Lt,G.count);else if(Z.isInstancedBufferGeometry){const Ge=Z._maxInstanceCount!==void 0?Z._maxInstanceCount:1/0,Yt=Math.min(Z.instanceCount,Ge);mt.renderInstances(ht,Lt,Yt)}else mt.render(ht,Lt)};function Et(C,W,Z){C.transparent===!0&&C.side===Nn&&C.forceSinglePass===!1?(C.side=zn,C.needsUpdate=!0,Ds(C,W,Z),C.side=Es,C.needsUpdate=!0,Ds(C,W,Z),C.side=Nn):Ds(C,W,Z)}this.compile=function(C,W,Z=null){Z===null&&(Z=C),p=Ce.get(Z),p.init(W),b.push(p),Z.traverseVisible(function(G){G.isLight&&G.layers.test(W.layers)&&(p.pushLight(G),G.castShadow&&p.pushShadow(G))}),C!==Z&&C.traverseVisible(function(G){G.isLight&&G.layers.test(W.layers)&&(p.pushLight(G),G.castShadow&&p.pushShadow(G))}),p.setupLights();const Y=new Set;return C.traverse(function(G){const de=G.material;if(de)if(Array.isArray(de))for(let Pe=0;Pe<de.length;Pe++){const Le=de[Pe];Et(Le,Z,G),Y.add(Le)}else Et(de,Z,G),Y.add(de)}),b.pop(),p=null,Y},this.compileAsync=function(C,W,Z=null){const Y=this.compile(C,W,Z);return new Promise(G=>{function de(){if(Y.forEach(function(Pe){Ye.get(Pe).currentProgram.isReady()&&Y.delete(Pe)}),Y.size===0){G(C);return}setTimeout(de,10)}st.get("KHR_parallel_shader_compile")!==null?de():setTimeout(de,10)})};let lt=null;function vn(C){lt&&lt(C)}function zt(){cn.stop()}function Ht(){cn.start()}const cn=new vp;cn.setAnimationLoop(vn),typeof self<"u"&&cn.setContext(self),this.setAnimationLoop=function(C){lt=C,ae.setAnimationLoop(C),C===null?cn.stop():cn.start()},ae.addEventListener("sessionstart",zt),ae.addEventListener("sessionend",Ht),this.render=function(C,W){if(W!==void 0&&W.isCamera!==!0){console.error("THREE.WebGLRenderer.render: camera is not an instance of THREE.Camera.");return}if(S===!0)return;if(C.matrixWorldAutoUpdate===!0&&C.updateMatrixWorld(),W.parent===null&&W.matrixWorldAutoUpdate===!0&&W.updateMatrixWorld(),ae.enabled===!0&&ae.isPresenting===!0&&(ae.cameraAutoUpdate===!0&&ae.updateCamera(W),W=ae.getCamera()),C.isScene===!0&&C.onBeforeRender(_,C,W,R),p=Ce.get(C,b.length),p.init(W),b.push(p),Se.multiplyMatrices(W.projectionMatrix,W.matrixWorldInverse),be.setFromProjectionMatrix(Se),he=this.localClippingEnabled,ie=Je.init(this.clippingPlanes,he),x=xe.get(C,m.length),x.init(),m.push(x),ae.enabled===!0&&ae.isPresenting===!0){const de=_.xr.getDepthSensingMesh();de!==null&&Ei(de,W,-1/0,_.sortObjects)}Ei(C,W,0,_.sortObjects),x.finish(),_.sortObjects===!0&&x.sort(ne,ge),Oe=ae.enabled===!1||ae.isPresenting===!1||ae.hasDepthSensing()===!1,Oe&&Ae.addToRenderList(x,C),this.info.render.frame++,ie===!0&&Je.beginShadows();const Z=p.state.shadowsArray;me.render(Z,C,W),ie===!0&&Je.endShadows(),this.info.autoReset===!0&&this.info.reset();const Y=x.opaque,G=x.transmissive;if(p.setupLights(),W.isArrayCamera){const de=W.cameras;if(G.length>0)for(let Pe=0,Le=de.length;Pe<Le;Pe++){const Ne=de[Pe];Rn(Y,G,C,Ne)}Oe&&Ae.render(C);for(let Pe=0,Le=de.length;Pe<Le;Pe++){const Ne=de[Pe];ki(x,C,Ne,Ne.viewport)}}else G.length>0&&Rn(Y,G,C,W),Oe&&Ae.render(C),ki(x,C,W);R!==null&&(qe.updateMultisampleRenderTarget(R),qe.updateRenderTargetMipmap(R)),C.isScene===!0&&C.onAfterRender(_,C,W),B.resetDefaultState(),N=-1,M=null,b.pop(),b.length>0?(p=b[b.length-1],ie===!0&&Je.setGlobalState(_.clippingPlanes,p.state.camera)):p=null,m.pop(),m.length>0?x=m[m.length-1]:x=null};function Ei(C,W,Z,Y){if(C.visible===!1)return;if(C.layers.test(W.layers)){if(C.isGroup)Z=C.renderOrder;else if(C.isLOD)C.autoUpdate===!0&&C.update(W);else if(C.isLight)p.pushLight(C),C.castShadow&&p.pushShadow(C);else if(C.isSprite){if(!C.frustumCulled||be.intersectsSprite(C)){Y&&ze.setFromMatrixPosition(C.matrixWorld).applyMatrix4(Se);const Pe=te.update(C),Le=C.material;Le.visible&&x.push(C,Pe,Le,Z,ze.z,null)}}else if((C.isMesh||C.isLine||C.isPoints)&&(!C.frustumCulled||be.intersectsObject(C))){const Pe=te.update(C),Le=C.material;if(Y&&(C.boundingSphere!==void 0?(C.boundingSphere===null&&C.computeBoundingSphere(),ze.copy(C.boundingSphere.center)):(Pe.boundingSphere===null&&Pe.computeBoundingSphere(),ze.copy(Pe.boundingSphere.center)),ze.applyMatrix4(C.matrixWorld).applyMatrix4(Se)),Array.isArray(Le)){const Ne=Pe.groups;for(let Qe=0,et=Ne.length;Qe<et;Qe++){const Be=Ne[Qe],ht=Le[Be.materialIndex];ht&&ht.visible&&x.push(C,Pe,ht,Z,ze.z,Be)}}else Le.visible&&x.push(C,Pe,Le,Z,ze.z,null)}}const de=C.children;for(let Pe=0,Le=de.length;Pe<Le;Pe++)Ei(de[Pe],W,Z,Y)}function ki(C,W,Z,Y){const G=C.opaque,de=C.transmissive,Pe=C.transparent;p.setupLightsView(Z),ie===!0&&Je.setGlobalState(_.clippingPlanes,Z),Y&&ke.viewport(y.copy(Y)),G.length>0&&oi(G,W,Z),de.length>0&&oi(de,W,Z),Pe.length>0&&oi(Pe,W,Z),ke.buffers.depth.setTest(!0),ke.buffers.depth.setMask(!0),ke.buffers.color.setMask(!0),ke.setPolygonOffset(!1)}function Rn(C,W,Z,Y){if((Z.isScene===!0?Z.overrideMaterial:null)!==null)return;p.state.transmissionRenderTarget[Y.id]===void 0&&(p.state.transmissionRenderTarget[Y.id]=new er(1,1,{generateMipmaps:!0,type:st.has("EXT_color_buffer_half_float")||st.has("EXT_color_buffer_float")?eo:ss,minFilter:Ks,samples:4,stencilBuffer:r,resolveDepthBuffer:!1,resolveStencilBuffer:!1,colorSpace:Mt.workingColorSpace}));const de=p.state.transmissionRenderTarget[Y.id],Pe=Y.viewport||y;de.setSize(Pe.z,Pe.w);const Le=_.getRenderTarget();_.setRenderTarget(de),_.getClearColor(H),J=_.getClearAlpha(),J<1&&_.setClearColor(16777215,.5),_.clear(),Oe&&Ae.render(Z);const Ne=_.toneMapping;_.toneMapping=Ss;const Qe=Y.viewport;if(Y.viewport!==void 0&&(Y.viewport=void 0),p.setupLightsView(Y),ie===!0&&Je.setGlobalState(_.clippingPlanes,Y),oi(C,Z,Y),qe.updateMultisampleRenderTarget(de),qe.updateRenderTargetMipmap(de),st.has("WEBGL_multisampled_render_to_texture")===!1){let et=!1;for(let Be=0,ht=W.length;Be<ht;Be++){const Pt=W[Be],Lt=Pt.object,_n=Pt.geometry,mt=Pt.material,Ge=Pt.group;if(mt.side===Nn&&Lt.layers.test(Y.layers)){const Yt=mt.side;mt.side=zn,mt.needsUpdate=!0,Bi(Lt,Z,Y,_n,mt,Ge),mt.side=Yt,mt.needsUpdate=!0,et=!0}}et===!0&&(qe.updateMultisampleRenderTarget(de),qe.updateRenderTargetMipmap(de))}_.setRenderTarget(Le),_.setClearColor(H,J),Qe!==void 0&&(Y.viewport=Qe),_.toneMapping=Ne}function oi(C,W,Z){const Y=W.isScene===!0?W.overrideMaterial:null;for(let G=0,de=C.length;G<de;G++){const Pe=C[G],Le=Pe.object,Ne=Pe.geometry,Qe=Y===null?Pe.material:Y,et=Pe.group;Le.layers.test(Z.layers)&&Bi(Le,W,Z,Ne,Qe,et)}}function Bi(C,W,Z,Y,G,de){C.onBeforeRender(_,W,Z,Y,G,de),C.modelViewMatrix.multiplyMatrices(Z.matrixWorldInverse,C.matrixWorld),C.normalMatrix.getNormalMatrix(C.modelViewMatrix),G.onBeforeRender(_,W,Z,Y,C,de),G.transparent===!0&&G.side===Nn&&G.forceSinglePass===!1?(G.side=zn,G.needsUpdate=!0,_.renderBufferDirect(Z,W,Y,G,C,de),G.side=Es,G.needsUpdate=!0,_.renderBufferDirect(Z,W,Y,G,C,de),G.side=Nn):_.renderBufferDirect(Z,W,Y,G,C,de),C.onAfterRender(_,W,Z,Y,G,de)}function Ds(C,W,Z){W.isScene!==!0&&(W=We);const Y=Ye.get(C),G=p.state.lights,de=p.state.shadowsArray,Pe=G.state.version,Le=$.getParameters(C,G.state,de,W,Z),Ne=$.getProgramCacheKey(Le);let Qe=Y.programs;Y.environment=C.isMeshStandardMaterial?W.environment:null,Y.fog=W.fog,Y.envMap=(C.isMeshStandardMaterial?E:U).get(C.envMap||Y.environment),Y.envMapRotation=Y.environment!==null&&C.envMap===null?W.environmentRotation:C.envMapRotation,Qe===void 0&&(C.addEventListener("dispose",Ke),Qe=new Map,Y.programs=Qe);let et=Qe.get(Ne);if(et!==void 0){if(Y.currentProgram===et&&Y.lightsStateVersion===Pe)return ao(C,Le),et}else Le.uniforms=$.getUniforms(C),C.onBeforeCompile(Le,_),et=$.acquireProgram(Le,Ne),Qe.set(Ne,et),Y.uniforms=Le.uniforms;const Be=Y.uniforms;return(!C.isShaderMaterial&&!C.isRawShaderMaterial||C.clipping===!0)&&(Be.clippingPlanes=Je.uniform),ao(C,Le),Y.needsLights=kl(C),Y.lightsStateVersion=Pe,Y.needsLights&&(Be.ambientLightColor.value=G.state.ambient,Be.lightProbe.value=G.state.probe,Be.directionalLights.value=G.state.directional,Be.directionalLightShadows.value=G.state.directionalShadow,Be.spotLights.value=G.state.spot,Be.spotLightShadows.value=G.state.spotShadow,Be.rectAreaLights.value=G.state.rectArea,Be.ltc_1.value=G.state.rectAreaLTC1,Be.ltc_2.value=G.state.rectAreaLTC2,Be.pointLights.value=G.state.point,Be.pointLightShadows.value=G.state.pointShadow,Be.hemisphereLights.value=G.state.hemi,Be.directionalShadowMap.value=G.state.directionalShadowMap,Be.directionalShadowMatrix.value=G.state.directionalShadowMatrix,Be.spotShadowMap.value=G.state.spotShadowMap,Be.spotLightMatrix.value=G.state.spotLightMatrix,Be.spotLightMap.value=G.state.spotLightMap,Be.pointShadowMap.value=G.state.pointShadowMap,Be.pointShadowMatrix.value=G.state.pointShadowMatrix),Y.currentProgram=et,Y.uniformsList=null,et}function _a(C){if(C.uniformsList===null){const W=C.currentProgram.getUniforms();C.uniformsList=il.seqWithValue(W.seq,C.uniforms)}return C.uniformsList}function ao(C,W){const Z=Ye.get(C);Z.outputColorSpace=W.outputColorSpace,Z.batching=W.batching,Z.batchingColor=W.batchingColor,Z.instancing=W.instancing,Z.instancingColor=W.instancingColor,Z.instancingMorph=W.instancingMorph,Z.skinning=W.skinning,Z.morphTargets=W.morphTargets,Z.morphNormals=W.morphNormals,Z.morphColors=W.morphColors,Z.morphTargetsCount=W.morphTargetsCount,Z.numClippingPlanes=W.numClippingPlanes,Z.numIntersection=W.numClipIntersection,Z.vertexAlphas=W.vertexAlphas,Z.vertexTangents=W.vertexTangents,Z.toneMapping=W.toneMapping}function Ol(C,W,Z,Y,G){W.isScene!==!0&&(W=We),qe.resetTextureUnits();const de=W.fog,Pe=Y.isMeshStandardMaterial?W.environment:null,Le=R===null?_.outputColorSpace:R.isXRRenderTarget===!0?R.texture.colorSpace:Ps,Ne=(Y.isMeshStandardMaterial?E:U).get(Y.envMap||Pe),Qe=Y.vertexColors===!0&&!!Z.attributes.color&&Z.attributes.color.itemSize===4,et=!!Z.attributes.tangent&&(!!Y.normalMap||Y.anisotropy>0),Be=!!Z.morphAttributes.position,ht=!!Z.morphAttributes.normal,Pt=!!Z.morphAttributes.color;let Lt=Ss;Y.toneMapped&&(R===null||R.isXRRenderTarget===!0)&&(Lt=_.toneMapping);const _n=Z.morphAttributes.position||Z.morphAttributes.normal||Z.morphAttributes.color,mt=_n!==void 0?_n.length:0,Ge=Ye.get(Y),Yt=p.state.lights;if(ie===!0&&(he===!0||C!==M)){const kn=C===M&&Y.id===N;Je.setState(Y,C,kn)}let gt=!1;Y.version===Ge.__version?(Ge.needsLights&&Ge.lightsStateVersion!==Yt.state.version||Ge.outputColorSpace!==Le||G.isBatchedMesh&&Ge.batching===!1||!G.isBatchedMesh&&Ge.batching===!0||G.isBatchedMesh&&Ge.batchingColor===!0&&G.colorTexture===null||G.isBatchedMesh&&Ge.batchingColor===!1&&G.colorTexture!==null||G.isInstancedMesh&&Ge.instancing===!1||!G.isInstancedMesh&&Ge.instancing===!0||G.isSkinnedMesh&&Ge.skinning===!1||!G.isSkinnedMesh&&Ge.skinning===!0||G.isInstancedMesh&&Ge.instancingColor===!0&&G.instanceColor===null||G.isInstancedMesh&&Ge.instancingColor===!1&&G.instanceColor!==null||G.isInstancedMesh&&Ge.instancingMorph===!0&&G.morphTexture===null||G.isInstancedMesh&&Ge.instancingMorph===!1&&G.morphTexture!==null||Ge.envMap!==Ne||Y.fog===!0&&Ge.fog!==de||Ge.numClippingPlanes!==void 0&&(Ge.numClippingPlanes!==Je.numPlanes||Ge.numIntersection!==Je.numIntersection)||Ge.vertexAlphas!==Qe||Ge.vertexTangents!==et||Ge.morphTargets!==Be||Ge.morphNormals!==ht||Ge.morphColors!==Pt||Ge.toneMapping!==Lt||Ge.morphTargetsCount!==mt)&&(gt=!0):(gt=!0,Ge.__version=Y.version);let Dt=Ge.currentProgram;gt===!0&&(Dt=Ds(Y,W,G));let Hi=!1,Mn=!1,Is=!1;const Gt=Dt.getUniforms(),Ti=Ge.uniforms;if(ke.useProgram(Dt.program)&&(Hi=!0,Mn=!0,Is=!0),Y.id!==N&&(N=Y.id,Mn=!0),Hi||M!==C){Gt.setValue(k,"projectionMatrix",C.projectionMatrix),Gt.setValue(k,"viewMatrix",C.matrixWorldInverse);const kn=Gt.map.cameraPosition;kn!==void 0&&kn.setValue(k,fe.setFromMatrixPosition(C.matrixWorld)),ct.logarithmicDepthBuffer&&Gt.setValue(k,"logDepthBufFC",2/(Math.log(C.far+1)/Math.LN2)),(Y.isMeshPhongMaterial||Y.isMeshToonMaterial||Y.isMeshLambertMaterial||Y.isMeshBasicMaterial||Y.isMeshStandardMaterial||Y.isShaderMaterial)&&Gt.setValue(k,"isOrthographic",C.isOrthographicCamera===!0),M!==C&&(M=C,Mn=!0,Is=!0)}if(G.isSkinnedMesh){Gt.setOptional(k,G,"bindMatrix"),Gt.setOptional(k,G,"bindMatrixInverse");const kn=G.skeleton;kn&&(kn.boneTexture===null&&kn.computeBoneTexture(),Gt.setValue(k,"boneTexture",kn.boneTexture,qe))}G.isBatchedMesh&&(Gt.setOptional(k,G,"batchingTexture"),Gt.setValue(k,"batchingTexture",G._matricesTexture,qe),Gt.setOptional(k,G,"batchingIdTexture"),Gt.setValue(k,"batchingIdTexture",G._indirectTexture,qe),Gt.setOptional(k,G,"batchingColorTexture"),G._colorsTexture!==null&&Gt.setValue(k,"batchingColorTexture",G._colorsTexture,qe));const ya=Z.morphAttributes;if((ya.position!==void 0||ya.normal!==void 0||ya.color!==void 0)&&Ze.update(G,Z,Dt),(Mn||Ge.receiveShadow!==G.receiveShadow)&&(Ge.receiveShadow=G.receiveShadow,Gt.setValue(k,"receiveShadow",G.receiveShadow)),Y.isMeshGouraudMaterial&&Y.envMap!==null&&(Ti.envMap.value=Ne,Ti.flipEnvMap.value=Ne.isCubeTexture&&Ne.isRenderTargetTexture===!1?-1:1),Y.isMeshStandardMaterial&&Y.envMap===null&&W.environment!==null&&(Ti.envMapIntensity.value=W.environmentIntensity),Mn&&(Gt.setValue(k,"toneMappingExposure",_.toneMappingExposure),Ge.needsLights&&zi(Ti,Is),de&&Y.fog===!0&&Ee.refreshFogUniforms(Ti,de),Ee.refreshMaterialUniforms(Ti,Y,j,ee,p.state.transmissionRenderTarget[C.id]),il.upload(k,_a(Ge),Ti,qe)),Y.isShaderMaterial&&Y.uniformsNeedUpdate===!0&&(il.upload(k,_a(Ge),Ti,qe),Y.uniformsNeedUpdate=!1),Y.isSpriteMaterial&&Gt.setValue(k,"center",G.center),Gt.setValue(k,"modelViewMatrix",G.modelViewMatrix),Gt.setValue(k,"normalMatrix",G.normalMatrix),Gt.setValue(k,"modelMatrix",G.matrixWorld),Y.isShaderMaterial||Y.isRawShaderMaterial){const kn=Y.uniformsGroups;for(let rr=0,oo=kn.length;rr<oo;rr++){const lo=kn[rr];ce.update(lo,Dt),ce.bind(lo,Dt)}}return Dt}function zi(C,W){C.ambientLightColor.needsUpdate=W,C.lightProbe.needsUpdate=W,C.directionalLights.needsUpdate=W,C.directionalLightShadows.needsUpdate=W,C.pointLights.needsUpdate=W,C.pointLightShadows.needsUpdate=W,C.spotLights.needsUpdate=W,C.spotLightShadows.needsUpdate=W,C.rectAreaLights.needsUpdate=W,C.hemisphereLights.needsUpdate=W}function kl(C){return C.isMeshLambertMaterial||C.isMeshToonMaterial||C.isMeshPhongMaterial||C.isMeshStandardMaterial||C.isShadowMaterial||C.isShaderMaterial&&C.lights===!0}this.getActiveCubeFace=function(){return I},this.getActiveMipmapLevel=function(){return A},this.getRenderTarget=function(){return R},this.setRenderTargetTextures=function(C,W,Z){Ye.get(C.texture).__webglTexture=W,Ye.get(C.depthTexture).__webglTexture=Z;const Y=Ye.get(C);Y.__hasExternalTextures=!0,Y.__autoAllocateDepthBuffer=Z===void 0,Y.__autoAllocateDepthBuffer||st.has("WEBGL_multisampled_render_to_texture")===!0&&(console.warn("THREE.WebGLRenderer: Render-to-texture extension was disabled because an external texture was provided"),Y.__useRenderToTexture=!1)},this.setRenderTargetFramebuffer=function(C,W){const Z=Ye.get(C);Z.__webglFramebuffer=W,Z.__useDefaultFramebuffer=W===void 0},this.setRenderTarget=function(C,W=0,Z=0){R=C,I=W,A=Z;let Y=!0,G=null,de=!1,Pe=!1;if(C){const Ne=Ye.get(C);if(Ne.__useDefaultFramebuffer!==void 0)ke.bindFramebuffer(k.FRAMEBUFFER,null),Y=!1;else if(Ne.__webglFramebuffer===void 0)qe.setupRenderTarget(C);else if(Ne.__hasExternalTextures)qe.rebindTextures(C,Ye.get(C.texture).__webglTexture,Ye.get(C.depthTexture).__webglTexture);else if(C.depthBuffer){const Be=C.depthTexture;if(Ne.__boundDepthTexture!==Be){if(Be!==null&&Ye.has(Be)&&(C.width!==Be.image.width||C.height!==Be.image.height))throw new Error("WebGLRenderTarget: Attached DepthTexture is initialized to the incorrect size.");qe.setupDepthRenderbuffer(C)}}const Qe=C.texture;(Qe.isData3DTexture||Qe.isDataArrayTexture||Qe.isCompressedArrayTexture)&&(Pe=!0);const et=Ye.get(C).__webglFramebuffer;C.isWebGLCubeRenderTarget?(Array.isArray(et[W])?G=et[W][Z]:G=et[W],de=!0):C.samples>0&&qe.useMultisampledRTT(C)===!1?G=Ye.get(C).__webglMultisampledFramebuffer:Array.isArray(et)?G=et[Z]:G=et,y.copy(C.viewport),P.copy(C.scissor),X=C.scissorTest}else y.copy(ue).multiplyScalar(j).floor(),P.copy(ye).multiplyScalar(j).floor(),X=Te;if(ke.bindFramebuffer(k.FRAMEBUFFER,G)&&Y&&ke.drawBuffers(C,G),ke.viewport(y),ke.scissor(P),ke.setScissorTest(X),de){const Ne=Ye.get(C.texture);k.framebufferTexture2D(k.FRAMEBUFFER,k.COLOR_ATTACHMENT0,k.TEXTURE_CUBE_MAP_POSITIVE_X+W,Ne.__webglTexture,Z)}else if(Pe){const Ne=Ye.get(C.texture),Qe=W||0;k.framebufferTextureLayer(k.FRAMEBUFFER,k.COLOR_ATTACHMENT0,Ne.__webglTexture,Z||0,Qe)}N=-1},this.readRenderTargetPixels=function(C,W,Z,Y,G,de,Pe){if(!(C&&C.isWebGLRenderTarget)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");return}let Le=Ye.get(C).__webglFramebuffer;if(C.isWebGLCubeRenderTarget&&Pe!==void 0&&(Le=Le[Pe]),Le){ke.bindFramebuffer(k.FRAMEBUFFER,Le);try{const Ne=C.texture,Qe=Ne.format,et=Ne.type;if(!ct.textureFormatReadable(Qe)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in RGBA or implementation defined format.");return}if(!ct.textureTypeReadable(et)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in UnsignedByteType or implementation defined type.");return}W>=0&&W<=C.width-Y&&Z>=0&&Z<=C.height-G&&k.readPixels(W,Z,Y,G,Ve.convert(Qe),Ve.convert(et),de)}finally{const Ne=R!==null?Ye.get(R).__webglFramebuffer:null;ke.bindFramebuffer(k.FRAMEBUFFER,Ne)}}},this.readRenderTargetPixelsAsync=async function(C,W,Z,Y,G,de,Pe){if(!(C&&C.isWebGLRenderTarget))throw new Error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");let Le=Ye.get(C).__webglFramebuffer;if(C.isWebGLCubeRenderTarget&&Pe!==void 0&&(Le=Le[Pe]),Le){ke.bindFramebuffer(k.FRAMEBUFFER,Le);try{const Ne=C.texture,Qe=Ne.format,et=Ne.type;if(!ct.textureFormatReadable(Qe))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in RGBA or implementation defined format.");if(!ct.textureTypeReadable(et))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in UnsignedByteType or implementation defined type.");if(W>=0&&W<=C.width-Y&&Z>=0&&Z<=C.height-G){const Be=k.createBuffer();k.bindBuffer(k.PIXEL_PACK_BUFFER,Be),k.bufferData(k.PIXEL_PACK_BUFFER,de.byteLength,k.STREAM_READ),k.readPixels(W,Z,Y,G,Ve.convert(Qe),Ve.convert(et),0),k.flush();const ht=k.fenceSync(k.SYNC_GPU_COMMANDS_COMPLETE,0);await ax(k,ht,4);try{k.bindBuffer(k.PIXEL_PACK_BUFFER,Be),k.getBufferSubData(k.PIXEL_PACK_BUFFER,0,de)}finally{k.deleteBuffer(Be),k.deleteSync(ht)}return de}}finally{const Ne=R!==null?Ye.get(R).__webglFramebuffer:null;ke.bindFramebuffer(k.FRAMEBUFFER,Ne)}}},this.copyFramebufferToTexture=function(C,W=null,Z=0){C.isTexture!==!0&&(Xr("WebGLRenderer: copyFramebufferToTexture function signature has changed."),W=arguments[0]||null,C=arguments[1]);const Y=Math.pow(2,-Z),G=Math.floor(C.image.width*Y),de=Math.floor(C.image.height*Y),Pe=W!==null?W.x:0,Le=W!==null?W.y:0;qe.setTexture2D(C,0),k.copyTexSubImage2D(k.TEXTURE_2D,Z,0,0,Pe,Le,G,de),ke.unbindTexture()},this.copyTextureToTexture=function(C,W,Z=null,Y=null,G=0){C.isTexture!==!0&&(Xr("WebGLRenderer: copyTextureToTexture function signature has changed."),Y=arguments[0]||null,C=arguments[1],W=arguments[2],G=arguments[3]||0,Z=null);let de,Pe,Le,Ne,Qe,et;Z!==null?(de=Z.max.x-Z.min.x,Pe=Z.max.y-Z.min.y,Le=Z.min.x,Ne=Z.min.y):(de=C.image.width,Pe=C.image.height,Le=0,Ne=0),Y!==null?(Qe=Y.x,et=Y.y):(Qe=0,et=0);const Be=Ve.convert(W.format),ht=Ve.convert(W.type);qe.setTexture2D(W,0),k.pixelStorei(k.UNPACK_FLIP_Y_WEBGL,W.flipY),k.pixelStorei(k.UNPACK_PREMULTIPLY_ALPHA_WEBGL,W.premultiplyAlpha),k.pixelStorei(k.UNPACK_ALIGNMENT,W.unpackAlignment);const Pt=k.getParameter(k.UNPACK_ROW_LENGTH),Lt=k.getParameter(k.UNPACK_IMAGE_HEIGHT),_n=k.getParameter(k.UNPACK_SKIP_PIXELS),mt=k.getParameter(k.UNPACK_SKIP_ROWS),Ge=k.getParameter(k.UNPACK_SKIP_IMAGES),Yt=C.isCompressedTexture?C.mipmaps[G]:C.image;k.pixelStorei(k.UNPACK_ROW_LENGTH,Yt.width),k.pixelStorei(k.UNPACK_IMAGE_HEIGHT,Yt.height),k.pixelStorei(k.UNPACK_SKIP_PIXELS,Le),k.pixelStorei(k.UNPACK_SKIP_ROWS,Ne),C.isDataTexture?k.texSubImage2D(k.TEXTURE_2D,G,Qe,et,de,Pe,Be,ht,Yt.data):C.isCompressedTexture?k.compressedTexSubImage2D(k.TEXTURE_2D,G,Qe,et,Yt.width,Yt.height,Be,Yt.data):k.texSubImage2D(k.TEXTURE_2D,G,Qe,et,de,Pe,Be,ht,Yt),k.pixelStorei(k.UNPACK_ROW_LENGTH,Pt),k.pixelStorei(k.UNPACK_IMAGE_HEIGHT,Lt),k.pixelStorei(k.UNPACK_SKIP_PIXELS,_n),k.pixelStorei(k.UNPACK_SKIP_ROWS,mt),k.pixelStorei(k.UNPACK_SKIP_IMAGES,Ge),G===0&&W.generateMipmaps&&k.generateMipmap(k.TEXTURE_2D),ke.unbindTexture()},this.copyTextureToTexture3D=function(C,W,Z=null,Y=null,G=0){C.isTexture!==!0&&(Xr("WebGLRenderer: copyTextureToTexture3D function signature has changed."),Z=arguments[0]||null,Y=arguments[1]||null,C=arguments[2],W=arguments[3],G=arguments[4]||0);let de,Pe,Le,Ne,Qe,et,Be,ht,Pt;const Lt=C.isCompressedTexture?C.mipmaps[G]:C.image;Z!==null?(de=Z.max.x-Z.min.x,Pe=Z.max.y-Z.min.y,Le=Z.max.z-Z.min.z,Ne=Z.min.x,Qe=Z.min.y,et=Z.min.z):(de=Lt.width,Pe=Lt.height,Le=Lt.depth,Ne=0,Qe=0,et=0),Y!==null?(Be=Y.x,ht=Y.y,Pt=Y.z):(Be=0,ht=0,Pt=0);const _n=Ve.convert(W.format),mt=Ve.convert(W.type);let Ge;if(W.isData3DTexture)qe.setTexture3D(W,0),Ge=k.TEXTURE_3D;else if(W.isDataArrayTexture||W.isCompressedArrayTexture)qe.setTexture2DArray(W,0),Ge=k.TEXTURE_2D_ARRAY;else{console.warn("THREE.WebGLRenderer.copyTextureToTexture3D: only supports THREE.DataTexture3D and THREE.DataTexture2DArray.");return}k.pixelStorei(k.UNPACK_FLIP_Y_WEBGL,W.flipY),k.pixelStorei(k.UNPACK_PREMULTIPLY_ALPHA_WEBGL,W.premultiplyAlpha),k.pixelStorei(k.UNPACK_ALIGNMENT,W.unpackAlignment);const Yt=k.getParameter(k.UNPACK_ROW_LENGTH),gt=k.getParameter(k.UNPACK_IMAGE_HEIGHT),Dt=k.getParameter(k.UNPACK_SKIP_PIXELS),Hi=k.getParameter(k.UNPACK_SKIP_ROWS),Mn=k.getParameter(k.UNPACK_SKIP_IMAGES);k.pixelStorei(k.UNPACK_ROW_LENGTH,Lt.width),k.pixelStorei(k.UNPACK_IMAGE_HEIGHT,Lt.height),k.pixelStorei(k.UNPACK_SKIP_PIXELS,Ne),k.pixelStorei(k.UNPACK_SKIP_ROWS,Qe),k.pixelStorei(k.UNPACK_SKIP_IMAGES,et),C.isDataTexture||C.isData3DTexture?k.texSubImage3D(Ge,G,Be,ht,Pt,de,Pe,Le,_n,mt,Lt.data):W.isCompressedArrayTexture?k.compressedTexSubImage3D(Ge,G,Be,ht,Pt,de,Pe,Le,_n,Lt.data):k.texSubImage3D(Ge,G,Be,ht,Pt,de,Pe,Le,_n,mt,Lt),k.pixelStorei(k.UNPACK_ROW_LENGTH,Yt),k.pixelStorei(k.UNPACK_IMAGE_HEIGHT,gt),k.pixelStorei(k.UNPACK_SKIP_PIXELS,Dt),k.pixelStorei(k.UNPACK_SKIP_ROWS,Hi),k.pixelStorei(k.UNPACK_SKIP_IMAGES,Mn),G===0&&W.generateMipmaps&&k.generateMipmap(Ge),ke.unbindTexture()},this.initRenderTarget=function(C){Ye.get(C).__webglFramebuffer===void 0&&qe.setupRenderTarget(C)},this.initTexture=function(C){C.isCubeTexture?qe.setTextureCube(C,0):C.isData3DTexture?qe.setTexture3D(C,0):C.isDataArrayTexture||C.isCompressedArrayTexture?qe.setTexture2DArray(C,0):qe.setTexture2D(C,0),ke.unbindTexture()},this.resetState=function(){I=0,A=0,R=null,ke.reset(),B.reset()},typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}get coordinateSystem(){return Ji}get outputColorSpace(){return this._outputColorSpace}set outputColorSpace(e){this._outputColorSpace=e;const t=this.getContext();t.drawingBufferColorSpace=e===Vh?"display-p3":"srgb",t.unpackColorSpace=Mt.workingColorSpace===_l?"display-p3":"srgb"}}class Xh{constructor(e,t=25e-5){this.isFogExp2=!0,this.name="",this.color=new nt(e),this.density=t}clone(){return new Xh(this.color,this.density)}toJSON(){return{type:"FogExp2",name:this.name,color:this.color.getHex(),density:this.density}}}class wp extends tn{constructor(){super(),this.isScene=!0,this.type="Scene",this.background=null,this.environment=null,this.fog=null,this.backgroundBlurriness=0,this.backgroundIntensity=1,this.backgroundRotation=new Ni,this.environmentIntensity=1,this.environmentRotation=new Ni,this.overrideMaterial=null,typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}copy(e,t){return super.copy(e,t),e.background!==null&&(this.background=e.background.clone()),e.environment!==null&&(this.environment=e.environment.clone()),e.fog!==null&&(this.fog=e.fog.clone()),this.backgroundBlurriness=e.backgroundBlurriness,this.backgroundIntensity=e.backgroundIntensity,this.backgroundRotation.copy(e.backgroundRotation),this.environmentIntensity=e.environmentIntensity,this.environmentRotation.copy(e.environmentRotation),e.overrideMaterial!==null&&(this.overrideMaterial=e.overrideMaterial.clone()),this.matrixAutoUpdate=e.matrixAutoUpdate,this}toJSON(e){const t=super.toJSON(e);return this.fog!==null&&(t.object.fog=this.fog.toJSON()),this.backgroundBlurriness>0&&(t.object.backgroundBlurriness=this.backgroundBlurriness),this.backgroundIntensity!==1&&(t.object.backgroundIntensity=this.backgroundIntensity),t.object.backgroundRotation=this.backgroundRotation.toArray(),this.environmentIntensity!==1&&(t.object.environmentIntensity=this.environmentIntensity),t.object.environmentRotation=this.environmentRotation.toArray(),t}}class gb{constructor(e,t){this.isInterleavedBuffer=!0,this.array=e,this.stride=t,this.count=e!==void 0?e.length/t:0,this.usage=vh,this._updateRange={offset:0,count:-1},this.updateRanges=[],this.version=0,this.uuid=Qi()}onUploadCallback(){}set needsUpdate(e){e===!0&&this.version++}get updateRange(){return Xr("THREE.InterleavedBuffer: updateRange() is deprecated and will be removed in r169. Use addUpdateRange() instead."),this._updateRange}setUsage(e){return this.usage=e,this}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}copy(e){return this.array=new e.array.constructor(e.array),this.count=e.count,this.stride=e.stride,this.usage=e.usage,this}copyAt(e,t,n){e*=this.stride,n*=t.stride;for(let i=0,r=this.stride;i<r;i++)this.array[e+i]=t.array[n+i];return this}set(e,t=0){return this.array.set(e,t),this}clone(e){e.arrayBuffers===void 0&&(e.arrayBuffers={}),this.array.buffer._uuid===void 0&&(this.array.buffer._uuid=Qi()),e.arrayBuffers[this.array.buffer._uuid]===void 0&&(e.arrayBuffers[this.array.buffer._uuid]=this.array.slice(0).buffer);const t=new this.array.constructor(e.arrayBuffers[this.array.buffer._uuid]),n=new this.constructor(t,this.stride);return n.setUsage(this.usage),n}onUpload(e){return this.onUploadCallback=e,this}toJSON(e){return e.arrayBuffers===void 0&&(e.arrayBuffers={}),this.array.buffer._uuid===void 0&&(this.array.buffer._uuid=Qi()),e.arrayBuffers[this.array.buffer._uuid]===void 0&&(e.arrayBuffers[this.array.buffer._uuid]=Array.from(new Uint32Array(this.array.buffer))),{uuid:this.uuid,buffer:this.array.buffer._uuid,type:this.array.constructor.name,stride:this.stride}}}const In=new V;class dl{constructor(e,t,n,i=!1){this.isInterleavedBufferAttribute=!0,this.name="",this.data=e,this.itemSize=t,this.offset=n,this.normalized=i}get count(){return this.data.count}get array(){return this.data.array}set needsUpdate(e){this.data.needsUpdate=e}applyMatrix4(e){for(let t=0,n=this.data.count;t<n;t++)In.fromBufferAttribute(this,t),In.applyMatrix4(e),this.setXYZ(t,In.x,In.y,In.z);return this}applyNormalMatrix(e){for(let t=0,n=this.count;t<n;t++)In.fromBufferAttribute(this,t),In.applyNormalMatrix(e),this.setXYZ(t,In.x,In.y,In.z);return this}transformDirection(e){for(let t=0,n=this.count;t<n;t++)In.fromBufferAttribute(this,t),In.transformDirection(e),this.setXYZ(t,In.x,In.y,In.z);return this}getComponent(e,t){let n=this.array[e*this.data.stride+this.offset+t];return this.normalized&&(n=gi(n,this.array)),n}setComponent(e,t,n){return this.normalized&&(n=Tt(n,this.array)),this.data.array[e*this.data.stride+this.offset+t]=n,this}setX(e,t){return this.normalized&&(t=Tt(t,this.array)),this.data.array[e*this.data.stride+this.offset]=t,this}setY(e,t){return this.normalized&&(t=Tt(t,this.array)),this.data.array[e*this.data.stride+this.offset+1]=t,this}setZ(e,t){return this.normalized&&(t=Tt(t,this.array)),this.data.array[e*this.data.stride+this.offset+2]=t,this}setW(e,t){return this.normalized&&(t=Tt(t,this.array)),this.data.array[e*this.data.stride+this.offset+3]=t,this}getX(e){let t=this.data.array[e*this.data.stride+this.offset];return this.normalized&&(t=gi(t,this.array)),t}getY(e){let t=this.data.array[e*this.data.stride+this.offset+1];return this.normalized&&(t=gi(t,this.array)),t}getZ(e){let t=this.data.array[e*this.data.stride+this.offset+2];return this.normalized&&(t=gi(t,this.array)),t}getW(e){let t=this.data.array[e*this.data.stride+this.offset+3];return this.normalized&&(t=gi(t,this.array)),t}setXY(e,t,n){return e=e*this.data.stride+this.offset,this.normalized&&(t=Tt(t,this.array),n=Tt(n,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this}setXYZ(e,t,n,i){return e=e*this.data.stride+this.offset,this.normalized&&(t=Tt(t,this.array),n=Tt(n,this.array),i=Tt(i,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this.data.array[e+2]=i,this}setXYZW(e,t,n,i,r){return e=e*this.data.stride+this.offset,this.normalized&&(t=Tt(t,this.array),n=Tt(n,this.array),i=Tt(i,this.array),r=Tt(r,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this.data.array[e+2]=i,this.data.array[e+3]=r,this}clone(e){if(e===void 0){console.log("THREE.InterleavedBufferAttribute.clone(): Cloning an interleaved buffer attribute will de-interleave buffer data.");const t=[];for(let n=0;n<this.count;n++){const i=n*this.data.stride+this.offset;for(let r=0;r<this.itemSize;r++)t.push(this.data.array[i+r])}return new bi(new this.array.constructor(t),this.itemSize,this.normalized)}else return e.interleavedBuffers===void 0&&(e.interleavedBuffers={}),e.interleavedBuffers[this.data.uuid]===void 0&&(e.interleavedBuffers[this.data.uuid]=this.data.clone(e)),new dl(e.interleavedBuffers[this.data.uuid],this.itemSize,this.offset,this.normalized)}toJSON(e){if(e===void 0){console.log("THREE.InterleavedBufferAttribute.toJSON(): Serializing an interleaved buffer attribute will de-interleave buffer data.");const t=[];for(let n=0;n<this.count;n++){const i=n*this.data.stride+this.offset;for(let r=0;r<this.itemSize;r++)t.push(this.data.array[i+r])}return{itemSize:this.itemSize,type:this.array.constructor.name,array:t,normalized:this.normalized}}else return e.interleavedBuffers===void 0&&(e.interleavedBuffers={}),e.interleavedBuffers[this.data.uuid]===void 0&&(e.interleavedBuffers[this.data.uuid]=this.data.toJSON(e)),{isInterleavedBufferAttribute:!0,itemSize:this.itemSize,data:this.data.uuid,offset:this.offset,normalized:this.normalized}}}class Mi extends Ls{constructor(e){super(),this.isSpriteMaterial=!0,this.type="SpriteMaterial",this.color=new nt(16777215),this.map=null,this.alphaMap=null,this.rotation=0,this.sizeAttenuation=!0,this.transparent=!0,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.alphaMap=e.alphaMap,this.rotation=e.rotation,this.sizeAttenuation=e.sizeAttenuation,this.fog=e.fog,this}}let Ur;const La=new V,Nr=new V,Fr=new V,Or=new Xe,Da=new Xe,Ep=new Bt,Oo=new V,Ia=new V,ko=new V,Iu=new Xe,Mc=new Xe,Uu=new Xe;class Tp extends tn{constructor(e=new Mi){if(super(),this.isSprite=!0,this.type="Sprite",Ur===void 0){Ur=new Jt;const t=new Float32Array([-.5,-.5,0,0,0,.5,-.5,0,1,0,.5,.5,0,1,1,-.5,.5,0,0,1]),n=new gb(t,5);Ur.setIndex([0,1,2,0,2,3]),Ur.setAttribute("position",new dl(n,3,0,!1)),Ur.setAttribute("uv",new dl(n,2,3,!1))}this.geometry=Ur,this.material=e,this.center=new Xe(.5,.5)}raycast(e,t){e.camera===null&&console.error('THREE.Sprite: "Raycaster.camera" needs to be set in order to raycast against sprites.'),Nr.setFromMatrixScale(this.matrixWorld),Ep.copy(e.camera.matrixWorld),this.modelViewMatrix.multiplyMatrices(e.camera.matrixWorldInverse,this.matrixWorld),Fr.setFromMatrixPosition(this.modelViewMatrix),e.camera.isPerspectiveCamera&&this.material.sizeAttenuation===!1&&Nr.multiplyScalar(-Fr.z);const n=this.material.rotation;let i,r;n!==0&&(r=Math.cos(n),i=Math.sin(n));const a=this.center;Bo(Oo.set(-.5,-.5,0),Fr,a,Nr,i,r),Bo(Ia.set(.5,-.5,0),Fr,a,Nr,i,r),Bo(ko.set(.5,.5,0),Fr,a,Nr,i,r),Iu.set(0,0),Mc.set(1,0),Uu.set(1,1);let o=e.ray.intersectTriangle(Oo,Ia,ko,!1,La);if(o===null&&(Bo(Ia.set(-.5,.5,0),Fr,a,Nr,i,r),Mc.set(0,1),o=e.ray.intersectTriangle(Oo,ko,Ia,!1,La),o===null))return;const l=e.ray.origin.distanceTo(La);l<e.near||l>e.far||t.push({distance:l,point:La.clone(),uv:ii.getInterpolation(La,Oo,Ia,ko,Iu,Mc,Uu,new Xe),face:null,object:this})}copy(e,t){return super.copy(e,t),e.center!==void 0&&this.center.copy(e.center),this.material=e.material,this}}function Bo(s,e,t,n,i,r){Or.subVectors(s,t).addScalar(.5).multiply(n),i!==void 0?(Da.x=r*Or.x-i*Or.y,Da.y=i*Or.x+r*Or.y):Da.copy(Or),s.copy(e),s.x+=Da.x,s.y+=Da.y,s.applyMatrix4(Ep)}class Ms extends Ls{constructor(e){super(),this.isLineBasicMaterial=!0,this.type="LineBasicMaterial",this.color=new nt(16777215),this.map=null,this.linewidth=1,this.linecap="round",this.linejoin="round",this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.linewidth=e.linewidth,this.linecap=e.linecap,this.linejoin=e.linejoin,this.fog=e.fog,this}}const ul=new V,fl=new V,Nu=new Bt,Ua=new io,zo=new no,wc=new V,Fu=new V;class Ap extends tn{constructor(e=new Jt,t=new Ms){super(),this.isLine=!0,this.type="Line",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}computeLineDistances(){const e=this.geometry;if(e.index===null){const t=e.attributes.position,n=[0];for(let i=1,r=t.count;i<r;i++)ul.fromBufferAttribute(t,i-1),fl.fromBufferAttribute(t,i),n[i]=n[i-1],n[i]+=ul.distanceTo(fl);e.setAttribute("lineDistance",new It(n,1))}else console.warn("THREE.Line.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.");return this}raycast(e,t){const n=this.geometry,i=this.matrixWorld,r=e.params.Line.threshold,a=n.drawRange;if(n.boundingSphere===null&&n.computeBoundingSphere(),zo.copy(n.boundingSphere),zo.applyMatrix4(i),zo.radius+=r,e.ray.intersectsSphere(zo)===!1)return;Nu.copy(i).invert(),Ua.copy(e.ray).applyMatrix4(Nu);const o=r/((this.scale.x+this.scale.y+this.scale.z)/3),l=o*o,c=this.isLineSegments?2:1,h=n.index,u=n.attributes.position;if(h!==null){const f=Math.max(0,a.start),g=Math.min(h.count,a.start+a.count);for(let x=f,p=g-1;x<p;x+=c){const m=h.getX(x),b=h.getX(x+1),_=Ho(this,e,Ua,l,m,b);_&&t.push(_)}if(this.isLineLoop){const x=h.getX(g-1),p=h.getX(f),m=Ho(this,e,Ua,l,x,p);m&&t.push(m)}}else{const f=Math.max(0,a.start),g=Math.min(u.count,a.start+a.count);for(let x=f,p=g-1;x<p;x+=c){const m=Ho(this,e,Ua,l,x,x+1);m&&t.push(m)}if(this.isLineLoop){const x=Ho(this,e,Ua,l,g-1,f);x&&t.push(x)}}}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const i=t[n[0]];if(i!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let r=0,a=i.length;r<a;r++){const o=i[r].name||String(r);this.morphTargetInfluences.push(0),this.morphTargetDictionary[o]=r}}}}}function Ho(s,e,t,n,i,r){const a=s.geometry.attributes.position;if(ul.fromBufferAttribute(a,i),fl.fromBufferAttribute(a,r),t.distanceSqToSegment(ul,fl,wc,Fu)>n)return;wc.applyMatrix4(s.matrixWorld);const l=e.ray.origin.distanceTo(wc);if(!(l<e.near||l>e.far))return{distance:l,point:Fu.clone().applyMatrix4(s.matrixWorld),index:i,face:null,faceIndex:null,object:s}}const Ou=new V,ku=new V;class jr extends Ap{constructor(e,t){super(e,t),this.isLineSegments=!0,this.type="LineSegments"}computeLineDistances(){const e=this.geometry;if(e.index===null){const t=e.attributes.position,n=[];for(let i=0,r=t.count;i<r;i+=2)Ou.fromBufferAttribute(t,i),ku.fromBufferAttribute(t,i+1),n[i]=i===0?0:n[i-1],n[i+1]=n[i]+Ou.distanceTo(ku);e.setAttribute("lineDistance",new It(n,1))}else console.warn("THREE.LineSegments.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.");return this}}class Cp extends Ls{constructor(e){super(),this.isPointsMaterial=!0,this.type="PointsMaterial",this.color=new nt(16777215),this.map=null,this.alphaMap=null,this.size=1,this.sizeAttenuation=!0,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.alphaMap=e.alphaMap,this.size=e.size,this.sizeAttenuation=e.sizeAttenuation,this.fog=e.fog,this}}const Bu=new Bt,yh=new io,Vo=new no,Go=new V;class xb extends tn{constructor(e=new Jt,t=new Cp){super(),this.isPoints=!0,this.type="Points",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}raycast(e,t){const n=this.geometry,i=this.matrixWorld,r=e.params.Points.threshold,a=n.drawRange;if(n.boundingSphere===null&&n.computeBoundingSphere(),Vo.copy(n.boundingSphere),Vo.applyMatrix4(i),Vo.radius+=r,e.ray.intersectsSphere(Vo)===!1)return;Bu.copy(i).invert(),yh.copy(e.ray).applyMatrix4(Bu);const o=r/((this.scale.x+this.scale.y+this.scale.z)/3),l=o*o,c=n.index,d=n.attributes.position;if(c!==null){const u=Math.max(0,a.start),f=Math.min(c.count,a.start+a.count);for(let g=u,x=f;g<x;g++){const p=c.getX(g);Go.fromBufferAttribute(d,p),zu(Go,p,l,i,e,t,this)}}else{const u=Math.max(0,a.start),f=Math.min(d.count,a.start+a.count);for(let g=u,x=f;g<x;g++)Go.fromBufferAttribute(d,g),zu(Go,g,l,i,e,t,this)}}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const i=t[n[0]];if(i!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let r=0,a=i.length;r<a;r++){const o=i[r].name||String(r);this.morphTargetInfluences.push(0),this.morphTargetDictionary[o]=r}}}}}function zu(s,e,t,n,i,r,a){const o=yh.distanceSqToPoint(s);if(o<t){const l=new V;yh.closestPointToPoint(s,l),l.applyMatrix4(n);const c=i.ray.origin.distanceTo(l);if(c<i.near||c>i.far)return;r.push({distance:c,distanceToRay:Math.sqrt(o),point:l,index:e,face:null,object:a})}}class Yh extends On{constructor(e,t,n,i,r,a,o,l,c){super(e,t,n,i,r,a,o,l,c),this.isCanvasTexture=!0,this.needsUpdate=!0}}const Wo=new V,$o=new V,Ec=new V,qo=new ii;class vb extends Jt{constructor(e=null,t=1){if(super(),this.type="EdgesGeometry",this.parameters={geometry:e,thresholdAngle:t},e!==null){const i=Math.pow(10,4),r=Math.cos(qr*t),a=e.getIndex(),o=e.getAttribute("position"),l=a?a.count:o.count,c=[0,0,0],h=["a","b","c"],d=new Array(3),u={},f=[];for(let g=0;g<l;g+=3){a?(c[0]=a.getX(g),c[1]=a.getX(g+1),c[2]=a.getX(g+2)):(c[0]=g,c[1]=g+1,c[2]=g+2);const{a:x,b:p,c:m}=qo;if(x.fromBufferAttribute(o,c[0]),p.fromBufferAttribute(o,c[1]),m.fromBufferAttribute(o,c[2]),qo.getNormal(Ec),d[0]=`${Math.round(x.x*i)},${Math.round(x.y*i)},${Math.round(x.z*i)}`,d[1]=`${Math.round(p.x*i)},${Math.round(p.y*i)},${Math.round(p.z*i)}`,d[2]=`${Math.round(m.x*i)},${Math.round(m.y*i)},${Math.round(m.z*i)}`,!(d[0]===d[1]||d[1]===d[2]||d[2]===d[0]))for(let b=0;b<3;b++){const _=(b+1)%3,S=d[b],I=d[_],A=qo[h[b]],R=qo[h[_]],N=`${S}_${I}`,M=`${I}_${S}`;M in u&&u[M]?(Ec.dot(u[M].normal)<=r&&(f.push(A.x,A.y,A.z),f.push(R.x,R.y,R.z)),u[M]=null):N in u||(u[N]={index0:c[b],index1:c[_],normal:Ec.clone()})}}for(const g in u)if(u[g]){const{index0:x,index1:p}=u[g];Wo.fromBufferAttribute(o,x),$o.fromBufferAttribute(o,p),f.push(Wo.x,Wo.y,Wo.z),f.push($o.x,$o.y,$o.z)}this.setAttribute("position",new It(f,3))}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}}class jh extends Jt{constructor(e=.5,t=1,n=32,i=1,r=0,a=Math.PI*2){super(),this.type="RingGeometry",this.parameters={innerRadius:e,outerRadius:t,thetaSegments:n,phiSegments:i,thetaStart:r,thetaLength:a},n=Math.max(3,n),i=Math.max(1,i);const o=[],l=[],c=[],h=[];let d=e;const u=(t-e)/i,f=new V,g=new Xe;for(let x=0;x<=i;x++){for(let p=0;p<=n;p++){const m=r+p/n*a;f.x=d*Math.cos(m),f.y=d*Math.sin(m),l.push(f.x,f.y,f.z),c.push(0,0,1),g.x=(f.x/t+1)/2,g.y=(f.y/t+1)/2,h.push(g.x,g.y)}d+=u}for(let x=0;x<i;x++){const p=x*(n+1);for(let m=0;m<n;m++){const b=m+p,_=b,S=b+n+1,I=b+n+2,A=b+1;o.push(_,S,A),o.push(S,I,A)}}this.setIndex(o),this.setAttribute("position",new It(l,3)),this.setAttribute("normal",new It(c,3)),this.setAttribute("uv",new It(h,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new jh(e.innerRadius,e.outerRadius,e.thetaSegments,e.phiSegments,e.thetaStart,e.thetaLength)}}class Kr extends Ls{constructor(e){super(),this.isMeshStandardMaterial=!0,this.defines={STANDARD:""},this.type="MeshStandardMaterial",this.color=new nt(16777215),this.roughness=1,this.metalness=0,this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.emissive=new nt(0),this.emissiveIntensity=1,this.emissiveMap=null,this.bumpMap=null,this.bumpScale=1,this.normalMap=null,this.normalMapType=op,this.normalScale=new Xe(1,1),this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.roughnessMap=null,this.metalnessMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new Ni,this.envMapIntensity=1,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.flatShading=!1,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.defines={STANDARD:""},this.color.copy(e.color),this.roughness=e.roughness,this.metalness=e.metalness,this.map=e.map,this.lightMap=e.lightMap,this.lightMapIntensity=e.lightMapIntensity,this.aoMap=e.aoMap,this.aoMapIntensity=e.aoMapIntensity,this.emissive.copy(e.emissive),this.emissiveMap=e.emissiveMap,this.emissiveIntensity=e.emissiveIntensity,this.bumpMap=e.bumpMap,this.bumpScale=e.bumpScale,this.normalMap=e.normalMap,this.normalMapType=e.normalMapType,this.normalScale.copy(e.normalScale),this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this.roughnessMap=e.roughnessMap,this.metalnessMap=e.metalnessMap,this.alphaMap=e.alphaMap,this.envMap=e.envMap,this.envMapRotation.copy(e.envMapRotation),this.envMapIntensity=e.envMapIntensity,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.wireframeLinecap=e.wireframeLinecap,this.wireframeLinejoin=e.wireframeLinejoin,this.flatShading=e.flatShading,this.fog=e.fog,this}}class _b extends Ms{constructor(e){super(),this.isLineDashedMaterial=!0,this.type="LineDashedMaterial",this.scale=1,this.dashSize=3,this.gapSize=1,this.setValues(e)}copy(e){return super.copy(e),this.scale=e.scale,this.dashSize=e.dashSize,this.gapSize=e.gapSize,this}}class Kh extends tn{constructor(e,t=1){super(),this.isLight=!0,this.type="Light",this.color=new nt(e),this.intensity=t}dispose(){}copy(e,t){return super.copy(e,t),this.color.copy(e.color),this.intensity=e.intensity,this}toJSON(e){const t=super.toJSON(e);return t.object.color=this.color.getHex(),t.object.intensity=this.intensity,this.groundColor!==void 0&&(t.object.groundColor=this.groundColor.getHex()),this.distance!==void 0&&(t.object.distance=this.distance),this.angle!==void 0&&(t.object.angle=this.angle),this.decay!==void 0&&(t.object.decay=this.decay),this.penumbra!==void 0&&(t.object.penumbra=this.penumbra),this.shadow!==void 0&&(t.object.shadow=this.shadow.toJSON()),this.target!==void 0&&(t.object.target=this.target.uuid),t}}class yb extends Kh{constructor(e,t,n){super(e,n),this.isHemisphereLight=!0,this.type="HemisphereLight",this.position.copy(tn.DEFAULT_UP),this.updateMatrix(),this.groundColor=new nt(t)}copy(e,t){return super.copy(e,t),this.groundColor.copy(e.groundColor),this}}const Tc=new Bt,Hu=new V,Vu=new V;class bb{constructor(e){this.camera=e,this.intensity=1,this.bias=0,this.normalBias=0,this.radius=1,this.blurSamples=8,this.mapSize=new Xe(512,512),this.map=null,this.mapPass=null,this.matrix=new Bt,this.autoUpdate=!0,this.needsUpdate=!1,this._frustum=new $h,this._frameExtents=new Xe(1,1),this._viewportCount=1,this._viewports=[new rn(0,0,1,1)]}getViewportCount(){return this._viewportCount}getFrustum(){return this._frustum}updateMatrices(e){const t=this.camera,n=this.matrix;Hu.setFromMatrixPosition(e.matrixWorld),t.position.copy(Hu),Vu.setFromMatrixPosition(e.target.matrixWorld),t.lookAt(Vu),t.updateMatrixWorld(),Tc.multiplyMatrices(t.projectionMatrix,t.matrixWorldInverse),this._frustum.setFromProjectionMatrix(Tc),n.set(.5,0,0,.5,0,.5,0,.5,0,0,.5,.5,0,0,0,1),n.multiply(Tc)}getViewport(e){return this._viewports[e]}getFrameExtents(){return this._frameExtents}dispose(){this.map&&this.map.dispose(),this.mapPass&&this.mapPass.dispose()}copy(e){return this.camera=e.camera.clone(),this.intensity=e.intensity,this.bias=e.bias,this.radius=e.radius,this.mapSize.copy(e.mapSize),this}clone(){return new this.constructor().copy(this)}toJSON(){const e={};return this.intensity!==1&&(e.intensity=this.intensity),this.bias!==0&&(e.bias=this.bias),this.normalBias!==0&&(e.normalBias=this.normalBias),this.radius!==1&&(e.radius=this.radius),(this.mapSize.x!==512||this.mapSize.y!==512)&&(e.mapSize=this.mapSize.toArray()),e.camera=this.camera.toJSON(!1).object,delete e.camera.matrix,e}}class Sb extends bb{constructor(){super(new $a(-5,5,5,-5,.5,500)),this.isDirectionalLightShadow=!0}}class Mb extends Kh{constructor(e,t){super(e,t),this.isDirectionalLight=!0,this.type="DirectionalLight",this.position.copy(tn.DEFAULT_UP),this.updateMatrix(),this.target=new tn,this.shadow=new Sb}dispose(){this.shadow.dispose()}copy(e){return super.copy(e),this.target=e.target.clone(),this.shadow=e.shadow.clone(),this}}class wb extends Kh{constructor(e,t){super(e,t),this.isAmbientLight=!0,this.type="AmbientLight"}}const Gu=new Bt;class Eb{constructor(e,t,n=0,i=1/0){this.ray=new io(e,t),this.near=n,this.far=i,this.camera=null,this.layers=new Wh,this.params={Mesh:{},Line:{threshold:1},LOD:{},Points:{threshold:1},Sprite:{}}}set(e,t){this.ray.set(e,t)}setFromCamera(e,t){t.isPerspectiveCamera?(this.ray.origin.setFromMatrixPosition(t.matrixWorld),this.ray.direction.set(e.x,e.y,.5).unproject(t).sub(this.ray.origin).normalize(),this.camera=t):t.isOrthographicCamera?(this.ray.origin.set(e.x,e.y,(t.near+t.far)/(t.near-t.far)).unproject(t),this.ray.direction.set(0,0,-1).transformDirection(t.matrixWorld),this.camera=t):console.error("THREE.Raycaster: Unsupported camera type: "+t.type)}setFromXRController(e){return Gu.identity().extractRotation(e.matrixWorld),this.ray.origin.setFromMatrixPosition(e.matrixWorld),this.ray.direction.set(0,0,-1).applyMatrix4(Gu),this}intersectObject(e,t=!0,n=[]){return bh(e,this,n,t),n.sort(Wu),n}intersectObjects(e,t=!0,n=[]){for(let i=0,r=e.length;i<r;i++)bh(e[i],this,n,t);return n.sort(Wu),n}}function Wu(s,e){return s.distance-e.distance}function bh(s,e,t,n){let i=!0;if(s.layers.test(e.layers)&&s.raycast(e,t)===!1&&(i=!1),i===!0&&n===!0){const r=s.children;for(let a=0,o=r.length;a<o;a++)bh(r[a],e,t,!0)}}class $u{constructor(e=1,t=0,n=0){return this.radius=e,this.phi=t,this.theta=n,this}set(e,t,n){return this.radius=e,this.phi=t,this.theta=n,this}copy(e){return this.radius=e.radius,this.phi=e.phi,this.theta=e.theta,this}makeSafe(){return this.phi=Math.max(1e-6,Math.min(Math.PI-1e-6,this.phi)),this}setFromVector3(e){return this.setFromCartesianCoords(e.x,e.y,e.z)}setFromCartesianCoords(e,t,n){return this.radius=Math.sqrt(e*e+t*t+n*n),this.radius===0?(this.theta=0,this.phi=0):(this.theta=Math.atan2(e,n),this.phi=Math.acos(Tn(t/this.radius,-1,1))),this}clone(){return new this.constructor().copy(this)}}class Tb extends jr{constructor(e=10,t=10,n=4473924,i=8947848){n=new nt(n),i=new nt(i);const r=t/2,a=e/t,o=e/2,l=[],c=[];for(let u=0,f=0,g=-o;u<=t;u++,g+=a){l.push(-o,0,g,o,0,g),l.push(g,0,-o,g,0,o);const x=u===r?n:i;x.toArray(c,f),f+=3,x.toArray(c,f),f+=3,x.toArray(c,f),f+=3,x.toArray(c,f),f+=3}const h=new Jt;h.setAttribute("position",new It(l,3)),h.setAttribute("color",new It(c,3));const d=new Ms({vertexColors:!0,toneMapped:!1});super(h,d),this.type="GridHelper"}dispose(){this.geometry.dispose(),this.material.dispose()}}typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("register",{detail:{revision:Nh}}));typeof window<"u"&&(window.__THREE__?console.warn("WARNING: Multiple instances of Three.js being imported."):window.__THREE__=Nh);var Ab=Object.defineProperty,Cb=(s,e,t)=>e in s?Ab(s,e,{enumerable:!0,configurable:!0,writable:!0,value:t}):s[e]=t,Rb=(s,e,t)=>(Cb(s,e+"",t),t);class Pb{constructor(){Rb(this,"_listeners")}addEventListener(e,t){this._listeners===void 0&&(this._listeners={});const n=this._listeners;n[e]===void 0&&(n[e]=[]),n[e].indexOf(t)===-1&&n[e].push(t)}hasEventListener(e,t){if(this._listeners===void 0)return!1;const n=this._listeners;return n[e]!==void 0&&n[e].indexOf(t)!==-1}removeEventListener(e,t){if(this._listeners===void 0)return;const i=this._listeners[e];if(i!==void 0){const r=i.indexOf(t);r!==-1&&i.splice(r,1)}}dispatchEvent(e){if(this._listeners===void 0)return;const n=this._listeners[e.type];if(n!==void 0){e.target=this;const i=n.slice(0);for(let r=0,a=i.length;r<a;r++)i[r].call(this,e);e.target=null}}}var Lb=Object.defineProperty,Db=(s,e,t)=>e in s?Lb(s,e,{enumerable:!0,configurable:!0,writable:!0,value:t}):s[e]=t,je=(s,e,t)=>(Db(s,typeof e!="symbol"?e+"":e,t),t);const Xo=new io,qu=new vs,Ib=Math.cos(70*(Math.PI/180)),Xu=(s,e)=>(s%e+e)%e;class Ub extends Pb{constructor(e,t){super(),je(this,"object"),je(this,"domElement"),je(this,"enabled",!0),je(this,"target",new V),je(this,"minDistance",0),je(this,"maxDistance",1/0),je(this,"minZoom",0),je(this,"maxZoom",1/0),je(this,"minPolarAngle",0),je(this,"maxPolarAngle",Math.PI),je(this,"minAzimuthAngle",-1/0),je(this,"maxAzimuthAngle",1/0),je(this,"enableDamping",!1),je(this,"dampingFactor",.05),je(this,"enableZoom",!0),je(this,"zoomSpeed",1),je(this,"enableRotate",!0),je(this,"rotateSpeed",1),je(this,"enablePan",!0),je(this,"panSpeed",1),je(this,"screenSpacePanning",!0),je(this,"keyPanSpeed",7),je(this,"zoomToCursor",!1),je(this,"autoRotate",!1),je(this,"autoRotateSpeed",2),je(this,"reverseOrbit",!1),je(this,"reverseHorizontalOrbit",!1),je(this,"reverseVerticalOrbit",!1),je(this,"keys",{LEFT:"ArrowLeft",UP:"ArrowUp",RIGHT:"ArrowRight",BOTTOM:"ArrowDown"}),je(this,"mouseButtons",{LEFT:mr.ROTATE,MIDDLE:mr.DOLLY,RIGHT:mr.PAN}),je(this,"touches",{ONE:gr.ROTATE,TWO:gr.DOLLY_PAN}),je(this,"target0"),je(this,"position0"),je(this,"zoom0"),je(this,"_domElementKeyEvents",null),je(this,"getPolarAngle"),je(this,"getAzimuthalAngle"),je(this,"setPolarAngle"),je(this,"setAzimuthalAngle"),je(this,"getDistance"),je(this,"getZoomScale"),je(this,"listenToKeyEvents"),je(this,"stopListenToKeyEvents"),je(this,"saveState"),je(this,"reset"),je(this,"update"),je(this,"connect"),je(this,"dispose"),je(this,"dollyIn"),je(this,"dollyOut"),je(this,"getScale"),je(this,"setScale"),this.object=e,this.domElement=t,this.target0=this.target.clone(),this.position0=this.object.position.clone(),this.zoom0=this.object.zoom,this.getPolarAngle=()=>h.phi,this.getAzimuthalAngle=()=>h.theta,this.setPolarAngle=B=>{let ce=Xu(B,2*Math.PI),O=h.phi;O<0&&(O+=2*Math.PI),ce<0&&(ce+=2*Math.PI);let ae=Math.abs(ce-O);2*Math.PI-ae<ae&&(ce<O?ce+=2*Math.PI:O+=2*Math.PI),d.phi=ce-O,n.update()},this.setAzimuthalAngle=B=>{let ce=Xu(B,2*Math.PI),O=h.theta;O<0&&(O+=2*Math.PI),ce<0&&(ce+=2*Math.PI);let ae=Math.abs(ce-O);2*Math.PI-ae<ae&&(ce<O?ce+=2*Math.PI:O+=2*Math.PI),d.theta=ce-O,n.update()},this.getDistance=()=>n.object.position.distanceTo(n.target),this.listenToKeyEvents=B=>{B.addEventListener("keydown",Ce),this._domElementKeyEvents=B},this.stopListenToKeyEvents=()=>{this._domElementKeyEvents.removeEventListener("keydown",Ce),this._domElementKeyEvents=null},this.saveState=()=>{n.target0.copy(n.target),n.position0.copy(n.object.position),n.zoom0=n.object.zoom},this.reset=()=>{n.target.copy(n.target0),n.object.position.copy(n.position0),n.object.zoom=n.zoom0,n.object.updateProjectionMatrix(),n.dispatchEvent(i),n.update(),l=o.NONE},this.update=(()=>{const B=new V,ce=new V(0,1,0),O=new tr().setFromUnitVectors(e.up,ce),ae=O.clone().invert(),se=new V,re=new tr,_e=2*Math.PI;return function(){const ot=n.object.position;O.setFromUnitVectors(e.up,ce),ae.copy(O).invert(),B.copy(ot).sub(n.target),B.applyQuaternion(O),h.setFromVector3(B),n.autoRotate&&l===o.NONE&&J(X()),n.enableDamping?(h.theta+=d.theta*n.dampingFactor,h.phi+=d.phi*n.dampingFactor):(h.theta+=d.theta,h.phi+=d.phi);let xt=n.minAzimuthAngle,Et=n.maxAzimuthAngle;isFinite(xt)&&isFinite(Et)&&(xt<-Math.PI?xt+=_e:xt>Math.PI&&(xt-=_e),Et<-Math.PI?Et+=_e:Et>Math.PI&&(Et-=_e),xt<=Et?h.theta=Math.max(xt,Math.min(Et,h.theta)):h.theta=h.theta>(xt+Et)/2?Math.max(xt,h.theta):Math.min(Et,h.theta)),h.phi=Math.max(n.minPolarAngle,Math.min(n.maxPolarAngle,h.phi)),h.makeSafe(),n.enableDamping===!0?n.target.addScaledVector(f,n.dampingFactor):n.target.add(f),n.zoomToCursor&&M||n.object.isOrthographicCamera?h.radius=be(h.radius):h.radius=be(h.radius*u),B.setFromSpherical(h),B.applyQuaternion(ae),ot.copy(n.target).add(B),n.object.matrixAutoUpdate||n.object.updateMatrix(),n.object.lookAt(n.target),n.enableDamping===!0?(d.theta*=1-n.dampingFactor,d.phi*=1-n.dampingFactor,f.multiplyScalar(1-n.dampingFactor)):(d.set(0,0,0),f.set(0,0,0));let lt=!1;if(n.zoomToCursor&&M){let vn=null;if(n.object instanceof An&&n.object.isPerspectiveCamera){const zt=B.length();vn=be(zt*u);const Ht=zt-vn;n.object.position.addScaledVector(R,Ht),n.object.updateMatrixWorld()}else if(n.object.isOrthographicCamera){const zt=new V(N.x,N.y,0);zt.unproject(n.object),n.object.zoom=Math.max(n.minZoom,Math.min(n.maxZoom,n.object.zoom/u)),n.object.updateProjectionMatrix(),lt=!0;const Ht=new V(N.x,N.y,0);Ht.unproject(n.object),n.object.position.sub(Ht).add(zt),n.object.updateMatrixWorld(),vn=B.length()}else console.warn("WARNING: OrbitControls.js encountered an unknown camera type - zoom to cursor disabled."),n.zoomToCursor=!1;vn!==null&&(n.screenSpacePanning?n.target.set(0,0,-1).transformDirection(n.object.matrix).multiplyScalar(vn).add(n.object.position):(Xo.origin.copy(n.object.position),Xo.direction.set(0,0,-1).transformDirection(n.object.matrix),Math.abs(n.object.up.dot(Xo.direction))<Ib?e.lookAt(n.target):(qu.setFromNormalAndCoplanarPoint(n.object.up,n.target),Xo.intersectPlane(qu,n.target))))}else n.object instanceof $a&&n.object.isOrthographicCamera&&(lt=u!==1,lt&&(n.object.zoom=Math.max(n.minZoom,Math.min(n.maxZoom,n.object.zoom/u)),n.object.updateProjectionMatrix()));return u=1,M=!1,lt||se.distanceToSquared(n.object.position)>c||8*(1-re.dot(n.object.quaternion))>c?(n.dispatchEvent(i),se.copy(n.object.position),re.copy(n.object.quaternion),lt=!1,!0):!1}})(),this.connect=B=>{n.domElement=B,n.domElement.style.touchAction="none",n.domElement.addEventListener("contextmenu",Ae),n.domElement.addEventListener("pointerdown",Q),n.domElement.addEventListener("pointercancel",te),n.domElement.addEventListener("wheel",xe)},this.dispose=()=>{var B,ce,O,ae,se,re;n.domElement&&(n.domElement.style.touchAction="auto"),(B=n.domElement)==null||B.removeEventListener("contextmenu",Ae),(ce=n.domElement)==null||ce.removeEventListener("pointerdown",Q),(O=n.domElement)==null||O.removeEventListener("pointercancel",te),(ae=n.domElement)==null||ae.removeEventListener("wheel",xe),(se=n.domElement)==null||se.ownerDocument.removeEventListener("pointermove",le),(re=n.domElement)==null||re.ownerDocument.removeEventListener("pointerup",te),n._domElementKeyEvents!==null&&n._domElementKeyEvents.removeEventListener("keydown",Ce)};const n=this,i={type:"change"},r={type:"start"},a={type:"end"},o={NONE:-1,ROTATE:0,DOLLY:1,PAN:2,TOUCH_ROTATE:3,TOUCH_PAN:4,TOUCH_DOLLY_PAN:5,TOUCH_DOLLY_ROTATE:6};let l=o.NONE;const c=1e-6,h=new $u,d=new $u;let u=1;const f=new V,g=new Xe,x=new Xe,p=new Xe,m=new Xe,b=new Xe,_=new Xe,S=new Xe,I=new Xe,A=new Xe,R=new V,N=new Xe;let M=!1;const y=[],P={};function X(){return 2*Math.PI/60/60*n.autoRotateSpeed}function H(){return Math.pow(.95,n.zoomSpeed)}function J(B){n.reverseOrbit||n.reverseHorizontalOrbit?d.theta+=B:d.theta-=B}function q(B){n.reverseOrbit||n.reverseVerticalOrbit?d.phi+=B:d.phi-=B}const ee=(()=>{const B=new V;return function(O,ae){B.setFromMatrixColumn(ae,0),B.multiplyScalar(-O),f.add(B)}})(),j=(()=>{const B=new V;return function(O,ae){n.screenSpacePanning===!0?B.setFromMatrixColumn(ae,1):(B.setFromMatrixColumn(ae,0),B.crossVectors(n.object.up,B)),B.multiplyScalar(O),f.add(B)}})(),ne=(()=>{const B=new V;return function(O,ae){const se=n.domElement;if(se&&n.object instanceof An&&n.object.isPerspectiveCamera){const re=n.object.position;B.copy(re).sub(n.target);let _e=B.length();_e*=Math.tan(n.object.fov/2*Math.PI/180),ee(2*O*_e/se.clientHeight,n.object.matrix),j(2*ae*_e/se.clientHeight,n.object.matrix)}else se&&n.object instanceof $a&&n.object.isOrthographicCamera?(ee(O*(n.object.right-n.object.left)/n.object.zoom/se.clientWidth,n.object.matrix),j(ae*(n.object.top-n.object.bottom)/n.object.zoom/se.clientHeight,n.object.matrix)):(console.warn("WARNING: OrbitControls.js encountered an unknown camera type - pan disabled."),n.enablePan=!1)}})();function ge(B){n.object instanceof An&&n.object.isPerspectiveCamera||n.object instanceof $a&&n.object.isOrthographicCamera?u=B:(console.warn("WARNING: OrbitControls.js encountered an unknown camera type - dolly/zoom disabled."),n.enableZoom=!1)}function ue(B){ge(u/B)}function ye(B){ge(u*B)}function Te(B){if(!n.zoomToCursor||!n.domElement)return;M=!0;const ce=n.domElement.getBoundingClientRect(),O=B.clientX-ce.left,ae=B.clientY-ce.top,se=ce.width,re=ce.height;N.x=O/se*2-1,N.y=-(ae/re)*2+1,R.set(N.x,N.y,1).unproject(n.object).sub(n.object.position).normalize()}function be(B){return Math.max(n.minDistance,Math.min(n.maxDistance,B))}function ie(B){g.set(B.clientX,B.clientY)}function he(B){Te(B),S.set(B.clientX,B.clientY)}function Se(B){m.set(B.clientX,B.clientY)}function fe(B){x.set(B.clientX,B.clientY),p.subVectors(x,g).multiplyScalar(n.rotateSpeed);const ce=n.domElement;ce&&(J(2*Math.PI*p.x/ce.clientHeight),q(2*Math.PI*p.y/ce.clientHeight)),g.copy(x),n.update()}function ze(B){I.set(B.clientX,B.clientY),A.subVectors(I,S),A.y>0?ue(H()):A.y<0&&ye(H()),S.copy(I),n.update()}function We(B){b.set(B.clientX,B.clientY),_.subVectors(b,m).multiplyScalar(n.panSpeed),ne(_.x,_.y),m.copy(b),n.update()}function Oe(B){Te(B),B.deltaY<0?ye(H()):B.deltaY>0&&ue(H()),n.update()}function pt(B){let ce=!1;switch(B.code){case n.keys.UP:ne(0,n.keyPanSpeed),ce=!0;break;case n.keys.BOTTOM:ne(0,-n.keyPanSpeed),ce=!0;break;case n.keys.LEFT:ne(n.keyPanSpeed,0),ce=!0;break;case n.keys.RIGHT:ne(-n.keyPanSpeed,0),ce=!0;break}ce&&(B.preventDefault(),n.update())}function k(){if(y.length==1)g.set(y[0].pageX,y[0].pageY);else{const B=.5*(y[0].pageX+y[1].pageX),ce=.5*(y[0].pageY+y[1].pageY);g.set(B,ce)}}function ut(){if(y.length==1)m.set(y[0].pageX,y[0].pageY);else{const B=.5*(y[0].pageX+y[1].pageX),ce=.5*(y[0].pageY+y[1].pageY);m.set(B,ce)}}function st(){const B=y[0].pageX-y[1].pageX,ce=y[0].pageY-y[1].pageY,O=Math.sqrt(B*B+ce*ce);S.set(0,O)}function ct(){n.enableZoom&&st(),n.enablePan&&ut()}function ke(){n.enableZoom&&st(),n.enableRotate&&k()}function wt(B){if(y.length==1)x.set(B.pageX,B.pageY);else{const O=Ve(B),ae=.5*(B.pageX+O.x),se=.5*(B.pageY+O.y);x.set(ae,se)}p.subVectors(x,g).multiplyScalar(n.rotateSpeed);const ce=n.domElement;ce&&(J(2*Math.PI*p.x/ce.clientHeight),q(2*Math.PI*p.y/ce.clientHeight)),g.copy(x)}function Ye(B){if(y.length==1)b.set(B.pageX,B.pageY);else{const ce=Ve(B),O=.5*(B.pageX+ce.x),ae=.5*(B.pageY+ce.y);b.set(O,ae)}_.subVectors(b,m).multiplyScalar(n.panSpeed),ne(_.x,_.y),m.copy(b)}function qe(B){const ce=Ve(B),O=B.pageX-ce.x,ae=B.pageY-ce.y,se=Math.sqrt(O*O+ae*ae);I.set(0,se),A.set(0,Math.pow(I.y/S.y,n.zoomSpeed)),ue(A.y),S.copy(I)}function U(B){n.enableZoom&&qe(B),n.enablePan&&Ye(B)}function E(B){n.enableZoom&&qe(B),n.enableRotate&&wt(B)}function Q(B){var ce,O;n.enabled!==!1&&(y.length===0&&((ce=n.domElement)==null||ce.ownerDocument.addEventListener("pointermove",le),(O=n.domElement)==null||O.ownerDocument.addEventListener("pointerup",te)),Ze(B),B.pointerType==="touch"?Je(B):$(B))}function le(B){n.enabled!==!1&&(B.pointerType==="touch"?me(B):Ee(B))}function te(B){var ce,O,ae;He(B),y.length===0&&((ce=n.domElement)==null||ce.releasePointerCapture(B.pointerId),(O=n.domElement)==null||O.ownerDocument.removeEventListener("pointermove",le),(ae=n.domElement)==null||ae.ownerDocument.removeEventListener("pointerup",te)),n.dispatchEvent(a),l=o.NONE}function $(B){let ce;switch(B.button){case 0:ce=n.mouseButtons.LEFT;break;case 1:ce=n.mouseButtons.MIDDLE;break;case 2:ce=n.mouseButtons.RIGHT;break;default:ce=-1}switch(ce){case mr.DOLLY:if(n.enableZoom===!1)return;he(B),l=o.DOLLY;break;case mr.ROTATE:if(B.ctrlKey||B.metaKey||B.shiftKey){if(n.enablePan===!1)return;Se(B),l=o.PAN}else{if(n.enableRotate===!1)return;ie(B),l=o.ROTATE}break;case mr.PAN:if(B.ctrlKey||B.metaKey||B.shiftKey){if(n.enableRotate===!1)return;ie(B),l=o.ROTATE}else{if(n.enablePan===!1)return;Se(B),l=o.PAN}break;default:l=o.NONE}l!==o.NONE&&n.dispatchEvent(r)}function Ee(B){if(n.enabled!==!1)switch(l){case o.ROTATE:if(n.enableRotate===!1)return;fe(B);break;case o.DOLLY:if(n.enableZoom===!1)return;ze(B);break;case o.PAN:if(n.enablePan===!1)return;We(B);break}}function xe(B){n.enabled===!1||n.enableZoom===!1||l!==o.NONE&&l!==o.ROTATE||(B.preventDefault(),n.dispatchEvent(r),Oe(B),n.dispatchEvent(a))}function Ce(B){n.enabled===!1||n.enablePan===!1||pt(B)}function Je(B){switch(we(B),y.length){case 1:switch(n.touches.ONE){case gr.ROTATE:if(n.enableRotate===!1)return;k(),l=o.TOUCH_ROTATE;break;case gr.PAN:if(n.enablePan===!1)return;ut(),l=o.TOUCH_PAN;break;default:l=o.NONE}break;case 2:switch(n.touches.TWO){case gr.DOLLY_PAN:if(n.enableZoom===!1&&n.enablePan===!1)return;ct(),l=o.TOUCH_DOLLY_PAN;break;case gr.DOLLY_ROTATE:if(n.enableZoom===!1&&n.enableRotate===!1)return;ke(),l=o.TOUCH_DOLLY_ROTATE;break;default:l=o.NONE}break;default:l=o.NONE}l!==o.NONE&&n.dispatchEvent(r)}function me(B){switch(we(B),l){case o.TOUCH_ROTATE:if(n.enableRotate===!1)return;wt(B),n.update();break;case o.TOUCH_PAN:if(n.enablePan===!1)return;Ye(B),n.update();break;case o.TOUCH_DOLLY_PAN:if(n.enableZoom===!1&&n.enablePan===!1)return;U(B),n.update();break;case o.TOUCH_DOLLY_ROTATE:if(n.enableZoom===!1&&n.enableRotate===!1)return;E(B),n.update();break;default:l=o.NONE}}function Ae(B){n.enabled!==!1&&B.preventDefault()}function Ze(B){y.push(B)}function He(B){delete P[B.pointerId];for(let ce=0;ce<y.length;ce++)if(y[ce].pointerId==B.pointerId){y.splice(ce,1);return}}function we(B){let ce=P[B.pointerId];ce===void 0&&(ce=new Xe,P[B.pointerId]=ce),ce.set(B.pageX,B.pageY)}function Ve(B){const ce=B.pointerId===y[0].pointerId?y[1]:y[0];return P[ce.pointerId]}this.dollyIn=(B=H())=>{ye(B),n.update()},this.dollyOut=(B=H())=>{ue(B),n.update()},this.getScale=()=>u,this.setScale=B=>{ge(B),n.update()},this.getZoomScale=()=>H(),t!==void 0&&this.connect(t),this.update()}}class Nb{constructor(){T(this,"handlers",new Map);T(this,"onceHandlers",new Map);T(this,"messageBuffer",new Map)}register(e,t){if(!this.handlers.has(e)){this.handlers.set(e,new Set);const n=this.messageBuffer.get(e);n&&(n.forEach(i=>Promise.resolve(t(i))),this.messageBuffer.delete(e))}return this.handlers.get(e).add(t),()=>this.unregister(e,t)}once(e,t){return this.onceHandlers.has(e)||this.onceHandlers.set(e,new Set),this.onceHandlers.get(e).add(t),()=>this.unregisterOnce(e,t)}unregister(e,t){var n;(n=this.handlers.get(e))==null||n.delete(t)}unregisterOnce(e,t){var n;(n=this.onceHandlers.get(e))==null||n.delete(t)}buffer(e){const{type:t}=e;this.messageBuffer.has(t)||this.messageBuffer.set(t,[]),this.messageBuffer.get(t).push(e)}async dispatch(e){const{type:t,...n}=e,i=this.handlers.get(t);if(i&&i.size>0){await Promise.all(Array.from(i).map(a=>Promise.resolve(a(n))));return}const r=this.onceHandlers.get(t);if(r&&r.size>0){await Promise.all(Array.from(r).map(a=>Promise.resolve(a(n)))),this.onceHandlers.delete(t);return}this.buffer(e)}clear(){this.handlers.clear(),this.onceHandlers.clear(),this.messageBuffer.clear()}getBuffered(e){return this.messageBuffer.get(e)??[]}hasHandlers(e){var t;return(((t=this.handlers.get(e))==null?void 0:t.size)??0)>0}}class Fb{constructor(e,t){T(this,"ws",null);T(this,"url");T(this,"router");T(this,"reconnectDelay",1e3);T(this,"maxReconnectDelay",3e4);T(this,"reconnectAttempts",0);T(this,"shouldReconnect",!0);T(this,"state","disconnected");T(this,"stateListeners",new Set);T(this,"messageQueue",[]);this.url=e,this.router=t}get connectionState(){return this.state}onStateChange(e){return this.stateListeners.add(e),e(this.state),()=>this.stateListeners.delete(e)}setState(e){this.state!==e&&(this.state=e,this.stateListeners.forEach(t=>t(e)))}connect(){var n;if(((n=this.ws)==null?void 0:n.readyState)===WebSocket.OPEN||this.state==="connecting")return;this.setState("connecting");const t=`${window.location.protocol==="https:"?"wss:":"ws:"}//${window.location.host}${this.url}`;this.ws=new WebSocket(t),this.ws.binaryType="arraybuffer",this.ws.onopen=()=>{console.log("[WS] Connected"),this.reconnectAttempts=0,this.reconnectDelay=1e3,this.setState("connected"),this.flushQueue()},this.ws.onmessage=async i=>{try{const r=JSON.parse(i.data);await this.router.dispatch(r)}catch(r){console.error("[WS] Failed to parse message:",r)}},this.ws.onclose=()=>{console.log("[WS] Disconnected"),this.setState("disconnected"),this.shouldReconnect&&this.scheduleReconnect()},this.ws.onerror=i=>{console.error("[WS] Error:",i)}}scheduleReconnect(){if(this.state==="reconnecting")return;this.setState("reconnecting");const e=Math.min(this.reconnectDelay*Math.pow(1.5,this.reconnectAttempts),this.maxReconnectDelay);this.reconnectAttempts++,console.log(`[WS] Reconnecting in ${e}ms (attempt ${this.reconnectAttempts})`),setTimeout(()=>this.connect(),e)}send(e){var t;((t=this.ws)==null?void 0:t.readyState)===WebSocket.OPEN?this.ws.send(JSON.stringify(e)):this.messageQueue.push(e)}flushQueue(){var e;for(;this.messageQueue.length>0&&((e=this.ws)==null?void 0:e.readyState)===WebSocket.OPEN;){const t=this.messageQueue.shift();this.ws.send(JSON.stringify(t))}}disconnect(){var e;this.shouldReconnect=!1,(e=this.ws)==null||e.close(),this.ws=null,this.setState("disconnected")}async waitForConnection(e=1e4){return this.state==="connected"?!0:new Promise(t=>{const n=setTimeout(()=>{i(),t(!1)},e),i=this.onStateChange(r=>{r==="connected"&&(clearTimeout(n),i(),t(!0))})})}get isConnected(){var e;return((e=this.ws)==null?void 0:e.readyState)===WebSocket.OPEN}}const jt=new Nb,ia=new Fb("/ws",jt);let Rp=null;function Ob(s){Rp=s}function Fi(){return Rp}class kb{constructor(){T(this,"components",new Map);T(this,"initialized",!1)}register(e){const t=e.name||e.constructor.name;this.components.has(t)&&console.warn(`[ComponentRegistry] Component "${t}" already registered, replacing`),this.components.set(t,e),this.initialized&&e.init().catch(console.error)}unregister(e){const t=this.components.get(e);t&&(t.destroy().catch(console.error),this.components.delete(e))}async initAll(){this.initialized=!0;for(const[e,t]of this.components)try{await t.init(),console.log(`[ComponentRegistry] Initialized: ${e}`)}catch(n){console.error(`[ComponentRegistry] Failed to initialize ${e}:`,n)}}async destroyAll(){for(const[e,t]of this.components)try{await t.destroy(),console.log(`[ComponentRegistry] Destroyed: ${e}`)}catch(n){console.error(`[ComponentRegistry] Failed to destroy ${e}:`,n)}this.components.clear(),this.initialized=!1}get(e){return this.components.get(e)}list(){return Array.from(this.components.keys())}}const Kn=new kb;typeof window<"u"&&(document.addEventListener("DOMContentLoaded",()=>{Kn.initAll().catch(console.error)}),window.addEventListener("beforeunload",()=>{Kn.destroyAll().catch(console.error)}));class Bb{constructor(){T(this,"panels",new Map);T(this,"listeners",new Set)}register(e){this.panels.set(e.id,e),this.notify()}get(e){return this.panels.get(e)}list(){return[...this.panels.values()]}toggle(e){const t=this.panels.get(e);t&&(t.toggle(),this.notify())}isOpen(e){const t=this.panels.get(e);return t?t.isOpen():!1}openIds(){return this.list().filter(e=>e.isOpen()).map(e=>e.id)}byKey(e){return this.list().find(t=>t.key===e)}onChange(e){return this.listeners.add(e),()=>{this.listeners.delete(e)}}notify(){for(const e of this.listeners)e()}}const Sn=new Bb,Sh="panel-hidden";function pl(s,e){s&&s.classList.toggle(Sh,e)}function fa(s){const e=document.createElement("button");return e.className="panel-close",e.setAttribute("aria-label","close"),e.textContent="×",e.style.cssText=`
    background: none;
    border: none;
    color: var(--text-secondary);
    font-size: 16px;
    line-height: 1;
    cursor: pointer;
    padding: 2px 4px;
    flex: 0 0 auto;
    pointer-events: auto;
  `,e.addEventListener("click",t=>{t.stopPropagation(),s()}),e}class zb{constructor(){T(this,"name","PanelRail");T(this,"container",null);T(this,"buttons",new Map);T(this,"unsubscribe",null)}async init(){const e=document.getElementById("ui-overlay");e&&(this.container=document.createElement("div"),this.container.id="panel-rail",this.container.style.cssText=`
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
    `,e.appendChild(this.container),this.build(),this.unsubscribe=Sn.onChange(()=>this.refresh()))}async destroy(){var e,t;(e=this.unsubscribe)==null||e.call(this),this.unsubscribe=null,(t=this.container)==null||t.remove(),this.container=null,this.buttons.clear()}build(){if(this.container){this.container.innerHTML="",this.buttons.clear();for(const e of Sn.list()){const t=document.createElement("button");t.className="panel-rail-button",t.textContent=e.glyph,t.title=e.key?`${e.label} (${e.key.toUpperCase()})`:e.label,t.style.cssText=`
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
      `,t.addEventListener("click",()=>Sn.toggle(e.id)),this.container.appendChild(t),this.buttons.set(e.id,t)}this.light()}}refresh(){if(!this.container)return;const e=Sn.list().map(i=>i.id),t=[...this.buttons.keys()];if(e.length!==t.length||e.some((i,r)=>i!==t[r])){this.build();return}this.light()}light(){for(const e of Sn.list()){const t=this.buttons.get(e.id);if(!t)continue;const n=e.isOpen();t.style.color=n?"var(--text-primary)":"var(--text-muted)",t.style.borderColor=n?"var(--border-bright)":"var(--border)",t.style.background=n?"var(--bg-primary)":"var(--bg-tertiary)"}}}const Hb=new zb;Kn.register(Hb);function Pp(s,e,t,n,i,r){Sn.register({id:s,label:e,glyph:t,key:r,toggle:n,isOpen:i})}function ir(s,e,t,n,i){Pp(s,e,t,()=>{const r=n();r&&pl(r,!r.classList.contains(Sh))},()=>{const r=n();return r?!r.classList.contains(Sh):!1},i)}const Vb=500,Yu=60;class Gb{constructor(){T(this,"name","ControlBar");T(this,"container",null);T(this,"playButton",null);T(this,"stepButton",null);T(this,"stopButton",null);T(this,"slider",null);T(this,"ceilingValue",null);T(this,"levelFill",null);T(this,"levelText",null);T(this,"cpuFill",null);T(this,"cpuText",null);T(this,"trace",null);T(this,"statusText",null);T(this,"timer",null);T(this,"payload",null);T(this,"samples",[])}async init(){this.createBar(),ir("control-bar","control bar","⏯",()=>this.container),this.timer=window.setInterval(()=>{this.poll()},Vb),this.poll()}async destroy(){var e;this.timer!==null&&window.clearInterval(this.timer),this.timer=null,(e=this.container)==null||e.remove()}togglePlay(){var e;this.command({paused:!((e=this.payload)!=null&&e.control.paused)})}step(){this.command({step:!0})}stop(){window.confirm("Stop the run? The run ends at its next boundary.")&&this.command({cancel:!0})}async poll(){var e,t;try{const n=await fetch("/api/control");if(!n.ok)return;const i=await n.json();for(this.payload=i,this.samples.push({level:((e=i.status)==null?void 0:e.in_flight)??0,cpu:((t=i.machine)==null?void 0:t.cpu_percent)??0});this.samples.length>Yu;)this.samples.shift();this.render()}catch{}}async command(e){var n;const t=(n=this.payload)==null?void 0:n.control.revision;try{const i=await fetch("/api/control",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({...e,revision:t})});if(!i.ok){const r=await i.json().catch(()=>({}));this.setStatus(r.error??"the control plane refused the command");return}await this.poll()}catch{this.setStatus("the dashboard could not reach the server")}}render(){var l,c;const e=this.payload;if(!e)return;const t=e.control,n=e.status,i=(n==null?void 0:n.in_flight)??0,r=t.max_workers??(n==null?void 0:n.ceiling)??0,a=((l=e.machine)==null?void 0:l.cpu_percent)??0;if(this.playButton){const h=t.paused;this.playButton.textContent=h?"▶":"⏸",this.playButton.classList.toggle("verb-primary",h),this.playButton.classList.toggle("verb-danger",!h),this.playButton.title=h?"Play — release the run":"Pause — hold the run at its next boundary",this.playButton.setAttribute("aria-label",h?"play":"pause")}if(this.stepButton){const h=t.paused&&e.readable;this.stepButton.disabled=!h,this.stepButton.title=h?"Step — release exactly one more batch":t.paused?"Step — control plane not readable":"Step — the run is not paused"}this.stopButton&&(this.stopButton.disabled=!e.readable,this.stopButton.title="Stop — end the run at its next boundary");const o=e.readable?"":e.error??"the control plane could not be read";if(this.playButton&&(this.playButton.disabled=!e.readable),this.playButton&&o&&(this.playButton.title=o),this.slider){const h=Math.max(1,((c=e.machine)==null?void 0:c.cpu_count)??1,r||1);this.slider.max=String(h),this.slider.value=String(Math.max(1,r||1)),this.slider.disabled=!e.readable,this.slider.title=o||`The ceiling on cells in flight — ${r||"the run's own"}`}if(this.ceilingValue&&(this.ceilingValue.textContent=r?String(r):"—"),this.levelFill){const h=r?Math.min(1,i/r):0;this.levelFill.style.width=`${h*100}%`,h===0?this.levelFill.style.background="var(--promoted)":h<.5?this.levelFill.style.background="var(--promoted)":h<.85?this.levelFill.style.background="var(--warn)":this.levelFill.style.background="var(--error)"}if(this.levelText&&(this.levelText.textContent=`${i}${r?` / ${r}`:""}`),this.cpuFill){const h=Math.min(100,Math.max(0,a));this.cpuFill.style.width=`${h}%`,h<30?this.cpuFill.style.background="var(--cpu)":h<70?this.cpuFill.style.background="var(--warn)":this.cpuFill.style.background="var(--error)"}if(this.cpuText&&(this.cpuText.textContent=`${a.toFixed(0)}%`),this.drawTrace(),this.statusText&&!o){const h=n!=null&&n.stage?n.stage.replace("s","S"):"";this.statusText.textContent=n?`${h} · ${n.cells_done} cells`:"no run is reporting"}}drawTrace(){var c,h,d;const e=this.trace;if(!e)return;const t=e.getContext("2d");if(!t)return;const n=e.width,i=e.height;t.clearRect(0,0,n,i);const r=Math.max(1,((c=this.payload)==null?void 0:c.control.max_workers)??((d=(h=this.payload)==null?void 0:h.status)==null?void 0:d.ceiling)??1),a=n/Math.max(1,Yu-1),o=n-(this.samples.length-1)*a;t.strokeStyle="var(--border)",t.lineWidth=.5,[.25,.5,.75].forEach(u=>{const f=i*u;t.beginPath(),t.moveTo(0,f),t.lineTo(n,f),t.stroke()}),t.beginPath(),t.strokeStyle="var(--cpu)",t.globalAlpha=.7,t.lineWidth=1,this.samples.forEach((u,f)=>{const g=o+f*a,x=i-Math.min(100,u.cpu)/100*i;f===0?t.moveTo(g,x):t.lineTo(g,x)}),t.stroke(),t.globalAlpha=1;const l=t.createLinearGradient(0,i,0,0);if(l.addColorStop(0,"var(--promoted)"),l.addColorStop(.5,"var(--warn)"),l.addColorStop(1,"var(--error)"),t.strokeStyle=l,t.lineWidth=1.5,t.lineCap="round",t.lineJoin="round",this.samples.forEach((u,f)=>{const g=o+f*a,x=i-Math.min(1,u.level/r)*i;f===0?t.moveTo(g,x):t.lineTo(g,x)}),t.stroke(),this.samples.length>0){const u=this.samples[this.samples.length-1],f=n-2,g=i-Math.min(100,u.cpu)/100*i;t.fillStyle="var(--cpu)",t.beginPath(),t.arc(f,g,2.5,0,Math.PI*2),t.fill();const x=i-Math.min(1,u.level/r)*i,p=u.level/r;t.fillStyle=p<.5?"var(--promoted)":p<.85?"var(--warn)":"var(--error)",t.beginPath(),t.arc(f-6,x,2.5,0,Math.PI*2),t.fill()}}setStatus(e){this.statusText&&(this.statusText.textContent=e)}createBar(){var i,r;const e=document.getElementById("ui-overlay");if(!e)return;this.container=document.createElement("div"),this.container.id="control-bar",this.container.style.cssText=`
      position: fixed;
      bottom: 126px;
      left: 50%;
      transform: translateX(-50%);
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 8px 14px;
      background: var(--bg-secondary);
      border: 1px solid var(--border);
      border-radius: 10px;
      font-size: 11px;
      color: var(--text-secondary);
      z-index: 165;
      box-shadow: 0 8px 32px rgba(0,0,0,0.45);
      transition: box-shadow var(--motion-fast), border-color var(--motion-fast);
    `,this.container.innerHTML=`
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
      <button class="door-btn" data-action="panel" title="Open control panel">⚙</button>
    `,e.appendChild(this.container);const t=this.container.querySelectorAll(".verb");this.playButton=t[0],this.stepButton=t[1],this.stopButton=t[2],this.playButton.addEventListener("click",()=>this.togglePlay()),this.stepButton.addEventListener("click",()=>this.step()),this.stopButton.addEventListener("click",()=>this.stop()),this.slider=this.container.querySelector(".ceiling-slider"),(i=this.slider)==null||i.addEventListener("input",a=>{const o=a.target,l=Number(o.value);this.ceilingValue.textContent=String(l)}),(r=this.slider)==null||r.addEventListener("change",()=>{var o;const a=Number(((o=this.slider)==null?void 0:o.value)??1);this.command({max_workers:a})}),this.ceilingValue=this.container.querySelector(".ceiling-value"),this.levelFill=this.container.querySelector(".level-fill"),this.levelText=this.container.querySelector(".level-text"),this.cpuFill=this.container.querySelector(".cpu-fill"),this.cpuText=this.container.querySelector(".cpu-text"),this.trace=this.container.querySelector("canvas.trace-canvas"),this.statusText=this.container.querySelector(".status-text"),this.container.querySelector(".door-btn").addEventListener("click",()=>Sn.toggle("control-panel"));const n=fa(()=>Sn.toggle("control-bar"));n.style.position="absolute",n.style.top="-10px",n.style.right="-8px",this.container.appendChild(n)}}const qa=new Gb;Kn.register(qa);const Zi={hud:"h",rail:"r",caption:"c",legend:"q"},ws={pareto:"p",ablation:"a",variability:"s"},Ui={play:" ",stop:"x",step:"w",panel:"z"},Jh="v",Mh=new Set([...Object.values(Zi),...Object.values(ws),...Object.values(Ui),Jh]);new Set("abcdefghijklmnopqrstuvwxyz".split("").filter(s=>!Mh.has(s)));class Wb{constructor(){T(this,"metricsByRun",new Map);T(this,"selectedRunId",null);T(this,"chosenByReader",!1);T(this,"listeners",[])}observe(e,t){this.metricsByRun.set(e,t),this.chosenByReader||(this.selectedRunId=this.newestRunId()),this.notify()}select(e){this.chosenByReader=!0,this.selectedRunId=e,this.notify()}get selectedId(){return this.selectedRunId}get selected(){return this.selectedRunId?this.metricsByRun.get(this.selectedRunId)??null:null}get runs(){return Array.from(this.metricsByRun.entries())}onChange(e){this.listeners.push(e)}notify(){this.listeners.forEach(e=>e(this.selectedRunId,this.selected))}newestRunId(){let e=null,t=-1/0;if(this.metricsByRun.forEach((i,r)=>{var l;const a=(l=i.run)==null?void 0:l.started_at,o=a?Date.parse(a):Number.NaN;Number.isNaN(o)||o>=t&&(t=o,e=r)}),e)return e;const n=this.metricsByRun.keys().next();return n.done?null:n.value}}const Yn=new Wb,Ac=["substrate","geometry","dynamics","plasticity","credit","update"];class $b{constructor(){T(this,"name","ControlPanel");T(this,"container",null);T(this,"profiles",[]);T(this,"axes",[]);T(this,"newRunSection",null);T(this,"runSection",null);T(this,"queueSection",null);T(this,"cellSection",null);T(this,"exportSection",null);T(this,"profileSelect",null);T(this,"seedsInput",null);T(this,"epochsInput",null);T(this,"budgetInput",null);T(this,"deviceSelect",null);T(this,"fidelitySelect",null);T(this,"profileNote",null);T(this,"newRunNote",null);T(this,"cellSelects",new Map);T(this,"cellNote",null);T(this,"exportNote",null)}async init(){this.createPanel(),ir("control-panel","control panel","⚙",()=>this.container,Ui.panel),await this.loadCatalogue(),this.refresh()}async destroy(){var e;(e=this.container)==null||e.remove()}async loadCatalogue(){try{const[e,t]=await Promise.all([fetch("/api/profiles").then(n=>n.json()),fetch("/api/axes").then(n=>n.json())]);this.profiles=e.profiles??[],this.axes=t.axes??[]}catch{this.profiles=[],this.axes=[]}this.renderProfileOptions(),this.renderCellOptions()}async refresh(){await Promise.all([this.refreshRuns(),this.refreshQueue(),this.refreshStatus()])}async refreshRuns(){if(this.runSection)try{const t=await(await fetch("/api/runs")).json(),n=this.currentRunId(),i=(t.runs??[]).find(r=>r.run_id===n);this.runSection.innerHTML=this.renderRun(i)}catch{this.runSection.innerHTML='<div class="note">the store did not answer</div>'}}async refreshQueue(){if(this.queueSection)try{const[e,t]=await Promise.all([fetch("/api/campaigns").then(n=>n.json()),fetch("/api/queue").then(n=>n.json())]);this.queueSection.innerHTML=this.renderQueue(e.campaigns??[],t),this.queueSection.querySelectorAll("[data-cancel]").forEach(n=>n.addEventListener("click",()=>{this.cancelCampaign(n.dataset.cancel??"")})),this.queueSection.querySelectorAll("[data-preempt]").forEach(n=>n.addEventListener("click",()=>{this.preemptCampaign(n.dataset.preempt??"")}))}catch{this.queueSection.innerHTML='<div class="note">the queue did not answer</div>'}}async refreshStatus(){if(this.newRunSection)try{const t=await(await fetch("/api/control")).json();if(!t.readable){this.newRunNote.textContent=t.error??"the control plane could not be read";return}const n=t.status;this.newRunNote.textContent=n?`The run is in ${n.stage} with ${n.cells_done} cells measured.`:"No run is reporting. The panel can still start one."}catch{this.newRunNote.textContent="the server did not answer"}}currentRunId(){return Yn.selectedId??null}renderProfileOptions(){if(this.profileSelect){this.profileSelect.innerHTML="";for(const e of this.profiles){const t=document.createElement("option");t.value=e.name,t.textContent=e.name,this.profileSelect.appendChild(t)}this.renderProfileNote()}}renderProfileNote(){if(!this.profileNote||!this.profileSelect)return;const e=this.profiles.find(t=>t.name===this.profileSelect.value);if(!e){this.profileNote.textContent="";return}this.profileNote.textContent=[e.description,`fidelity ${e.fidelity} · ${e.n_seeds} seeds · ${e.epochs} epochs`,e.budget_seconds?`budget ${e.budget_seconds}s`:"no budget",`policy ${e.policy}`,`axes ${e.axes.map(t=>t.axis).join(", ")||"all"}`].join(" · "),this.seedsInput&&(this.seedsInput.value=String(e.n_seeds)),this.epochsInput&&(this.epochsInput.value=String(e.epochs)),this.budgetInput&&(this.budgetInput.value=e.budget_seconds?String(e.budget_seconds):""),this.fidelitySelect&&(this.fidelitySelect.value=e.fidelity)}renderCellOptions(){for(const e of Ac){const t=this.cellSelects.get(e);if(!t)continue;const n=this.axes.find(r=>r.axis===e);t.innerHTML="";for(const r of(n==null?void 0:n.primitives)??[]){const a=document.createElement("option");a.value=r.name,a.textContent=r.available?r.name:`${r.name} (unavailable)`,a.disabled=!r.available,t.appendChild(a)}const i=t.querySelector("option:not([disabled])");i&&(t.value=i.value)}}renderRun(e){if(!e)return'<div class="note">no run is selected</div>';const t=e.declaration??{};return[`<div class="note">A run's declaration is frozen once it has begun; the panel shows it rather than offering an editor that would lie.</div>`,`<table class="kv">${[["run",e.run_id],["status",String(e.status)],["profile",String(t.profile??"—")],["tasks",(t.tasks??[]).join(", ")||"—"],["fidelity",String(t.fidelity??"—")],["objectives",(t.objectives??[]).join(", ")||"—"],["mode",String(t.mode??"—")],["declared cells",String(t.declared_cells??"—")],["records",String(e.records)],["seeds still owed",String(e.seeds_owed??"—")]].map(([i,r])=>`<tr><th>${i}</th><td>${r}</td></tr>`).join("")}</table>`].join("")}renderQueue(e,t){const n=e.map(r=>`<tr>
          <td>${r.campaign_id}</td>
          <td>${r.name}</td>
          <td>${r.status}</td>
          <td>
            <button data-cancel="${r.campaign_id}" class="mini">cancel</button>
            <button data-preempt="${r.campaign_id}" class="mini">preempt</button>
          </td>
        </tr>`).join("");return[`<table class="kv">${[["max concurrent",String(t.max_concurrent??"—")],["max cpus",String(t.max_cpus??"—")],["max gpus",String(t.max_gpus??"—")]].map(([r,a])=>`<tr><th>${r}</th><td>${a}</td></tr>`).join("")}</table>`,n?`<table class="list"><tr><th>id</th><th>name</th><th>status</th><th></th></tr>${n}</table>`:'<div class="note">the queue is empty</div>'].join("")}async startRun(){var t,n,i,r,a;if(!this.profileSelect)return;const e={};(t=this.seedsInput)!=null&&t.value&&(e.n_seeds=Number(this.seedsInput.value)),(n=this.epochsInput)!=null&&n.value&&(e.epochs=Number(this.epochsInput.value)),(i=this.budgetInput)!=null&&i.value&&(e.budget_seconds=Number(this.budgetInput.value)),(r=this.fidelitySelect)!=null&&r.value&&(e.fidelity=this.fidelitySelect.value);try{const l=await(await fetch("/api/runs",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({profile:this.profileSelect.value,overrides:e,device:((a=this.deviceSelect)==null?void 0:a.value)??void 0})})).json();l.started?this.newRunNote.textContent=`The run is queued as ${l.campaign_id}.`:this.newRunNote.textContent=`${l.error??"the run was refused"}. ${l.command??""}`}catch{this.newRunNote.textContent="the dashboard could not reach the server"}}cellCoordinate(){var t;const e={};for(const n of Ac)e[n]=((t=this.cellSelects.get(n))==null?void 0:t.value)??"";return e}async cellAction(e){const t=this.currentRunId();if(!t){this.cellNote.textContent="no run is selected";return}try{const i=await(await fetch(`/api/cells/${t}/${e}`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({coordinate:this.cellCoordinate()})})).json();this.cellNote.textContent=i.error??i.message??`${e} was refused`}catch{this.cellNote.textContent="the dashboard could not reach the server"}}async cancelCampaign(e){await fetch(`/api/campaigns/${e}/cancel`,{method:"POST"}),await this.refreshQueue()}async preemptCampaign(e){await fetch(`/api/campaigns/${e}/preempt`,{method:"POST"}),await this.refreshQueue()}async export(e){const t=this.currentRunId();if(!t){this.exportNote.textContent="no run is selected";return}try{if(e==="script"){const a=await fetch("/api/narration").then(o=>o.json());this.download("narration.txt",a.script??""),this.exportNote.textContent="the narration script was taken";return}const n=e==="report"?"report":"records",i=await fetch(`/api/runs/${t}/${n}`).then(a=>a.json());if(i.error){this.exportNote.textContent=i.error;return}const r=e==="report"?i.report??"":JSON.stringify(i.records??[],null,2);this.download(`${t}-${n}.${e==="report"?"txt":"json"}`,r),this.exportNote.textContent=`the ${e} was taken`}catch{this.exportNote.textContent="the dashboard could not reach the server"}}download(e,t){const n=new Blob([t],{type:"text/plain"}),i=document.createElement("a");i.download=e,i.href=URL.createObjectURL(n),i.click(),URL.revokeObjectURL(i.href)}createPanel(){var n;const e=document.getElementById("ui-overlay");if(!e)return;this.container=document.createElement("div"),this.container.id="control-panel",this.container.style.cssText=`
      position: fixed;
      top: 20px;
      left: 20px;
      width: 430px;
      max-height: calc(100vh - 340px);
      overflow-y: auto;
      background: var(--bg-secondary);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 14px 16px;
      font-size: 11px;
      color: var(--text-secondary);
      z-index: 165;
      box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    `,this.container.innerHTML=`
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
    `,e.appendChild(this.container),pl(this.container,!0),this.container.querySelector("#control-panel-header").appendChild(fa(()=>Sn.toggle("control-panel"))),this.newRunSection=this.container.querySelector(".new-run-note"),this.runSection=this.container.querySelector(".run-section"),this.queueSection=this.container.querySelector(".queue-section"),this.cellSection=this.container.querySelector(".cell-section"),this.exportSection=this.container.querySelector(".export-note"),this.profileSelect=this.container.querySelector(".profile"),this.profileNote=this.container.querySelector(".profile-note"),this.newRunNote=this.container.querySelector(".new-run-note"),this.cellNote=this.container.querySelector(".cell-note"),this.exportNote=this.container.querySelector(".export-note"),this.seedsInput=this.container.querySelector(".seeds"),this.epochsInput=this.container.querySelector(".epochs"),this.budgetInput=this.container.querySelector(".budget"),this.deviceSelect=this.container.querySelector(".device"),this.fidelitySelect=this.container.querySelector(".fidelity"),(n=this.profileSelect)==null||n.addEventListener("change",()=>this.renderProfileNote());const t=this.container.querySelector(".cell-row");for(const i of Ac){const r=document.createElement("label");r.textContent=i;const a=document.createElement("select");a.className=`cell-${i}`,r.appendChild(a),t.appendChild(r),this.cellSelects.set(i,a)}this.container.querySelector(".start").addEventListener("click",()=>void this.startRun()),this.container.querySelector(".replicate").addEventListener("click",()=>void this.cellAction("replicate")),this.container.querySelector(".preregister").addEventListener("click",()=>void this.cellAction("preregister")),this.container.querySelector(".quest").addEventListener("click",()=>void this.cellAction("quest")),this.container.querySelector(".export-script").addEventListener("click",()=>void this.export("script")),this.container.querySelector(".export-report").addEventListener("click",()=>void this.export("report")),this.container.querySelector(".export-records").addEventListener("click",()=>void this.export("records"))}}const Lp=new $b;Kn.register(Lp);const Wt={gradient:"#58a6ff",pepita:"#d4a843",random_projections:"#f78166",local_goodness:"#a371f7",thermodynamic_contrast:"#3fb950",contrastive:"#ff7b72",hebbian:"#79c0ff",predictive:"#d2a8ff"},F={bg:"#0a0e14",bg_tertiary:"#1a2330",border:"#2a3a4a",border_bright:"#3a4a5a",text_primary:"#e8ecf0",text_secondary:"#8b98a8",text_muted:"#5a6a7a",gradient:"#58a6ff",thermodynamic_contrast:"#3fb950",measured:"#d4a843",legal_unmeasured:"#58a6ff",void:"#f85149",pareto:"#e8ecf0",chance_line:"#f85149",gpu:"#58a6ff",cpu:"#3fb950",memory:"#d29922",ok:"#3fb950",warn:"#d29922",error:"#f85149",passed:"#3fb950",insufficient:"#d29922",rejected:"#f85149",promoted:"#a371f7",ramp_low:"#1f3a5f",ramp_mid:"#58a6ff",ramp_high:"#d4a843"},qb={substrate:{display_name:"Substrate",description:"Physical or computational substrate",primitives:[{name:"digital",summary:"Digital substrate: exact arithmetic, full precision",available:!0},{name:"analog",summary:"Analog substrate: continuous-valued physical state",available:!0},{name:"memristive",summary:"Memristive substrate: conductance, IR-drop, noise",available:!0},{name:"neuromorphic",summary:"Neuromorphic substrate: asynchronous spike events",available:!0},{name:"optical",summary:"Photonic substrate: phase/amplitude modulation",available:!0},{name:"quantum",summary:"Quantum substrate: unitary gate simulation",available:!0},{name:"complex",summary:"Complex-valued substrate",available:!0},{name:"sparse",summary:"Sparse substrate: sparsity-masked state",available:!0},{name:"ternary",summary:"Ternary substrate: weights in {-alpha, 0, +alpha}",available:!0}]},geometry:{display_name:"Geometry",description:"Network architecture and connectivity",primitives:[{name:"feedforward",summary:"Feedforward DAG (MLP/CNN)",available:!0},{name:"recurrent",summary:"Recurrent attractor (Hopfield/EqProp)",available:!0},{name:"causal_transformer",summary:"Causal transformer with KV cache",available:!0},{name:"tile",summary:"TileNet modular tile mesh",available:!0},{name:"tile_mesh",summary:"TileNet mesh topology",available:!0},{name:"conv",summary:"Convolutional geometry",available:!0},{name:"graph",summary:"Arbitrary node-edge fabric (FabricPC)",available:!0},{name:"attention",summary:"Attention geometry",available:!0},{name:"spatial_lattice",summary:"3-D spatial lattice (neural_cube)",available:!0},{name:"nca",summary:"Neural cellular automaton fabric",available:!0},{name:"ntm",summary:"Neural Turing Machine tape",available:!0}]},dynamics:{display_name:"Dynamics",description:"State evolution and settling",primitives:[{name:"energy_minimization",summary:"Equilibrium propagation energy minimization",available:!0},{name:"predictive_settling",summary:"Predictive coding settling",available:!0},{name:"error_predictive_coding",summary:"Error predictive coding",available:!0},{name:"spike_integration",summary:"LIF/Izhikevich spike integration",available:!0},{name:"instantaneous",summary:"Instantaneous pass (FF/Backprop)",available:!0},{name:"diffusion",summary:"Continuous-time diffusion settling",available:!0},{name:"lazy",summary:"Lazy/on-demand state dynamics",available:!0},{name:"pc_alm",summary:"Augmented Lagrangian predictive coding",available:!0}]},plasticity:{display_name:"Plasticity",description:"Local learning and adaptation",primitives:[{name:"null",summary:"Null plasticity (5-D slice)",available:!0},{name:"routing",summary:"Routing plasticity: state-dependent gating",available:!0},{name:"fast_weights",summary:"Fast-weight episode-local memory",available:!0},{name:"substrate_coupled",summary:"Physical substrate-coupled plasticity",available:!0},{name:"rule_state",summary:"Rule-state plasticity (Z3)",available:!0},{name:"temporal_psi",summary:"Trace-decayed supervised psi",available:!0},{name:"conflict_adaptive",summary:"Conflict-adaptive psi",available:!0}]},credit:{display_name:"Credit Assignment",description:"How learning signals reach parameters",primitives:[{name:"thermodynamic_contrast",summary:"EqProp free/nudged contrast (Scellier-Bengio)",available:!0},{name:"random_projections",summary:"Fixed random feedback (FA/DFA)",available:!0},{name:"local_goodness",summary:"Forward-Forward / PEPITA goodness",available:!0},{name:"local_contrastive",summary:"Local contrastive credit",available:!0},{name:"temporal_trace",summary:"Hebbian/STDP temporal trace",available:!0},{name:"target_inversion",summary:"Target propagation inversion",available:!0},{name:"homeostatic",summary:"Autonomous Lipschitz scaling",available:!0},{name:"pepita",summary:"PEPITA input-modulation credit",available:!0},{name:"gradient",summary:"Backprop gradient credit (ruler reference)",available:!0},{name:"pc_alm",summary:"PC-ALM primal-dual credit",available:!0}]},update:{display_name:"Update Rule",description:"How parameters are updated",primitives:[{name:"euclidean",summary:"SGD/Adam Euclidean update",available:!0},{name:"adam",summary:"Adam adaptive moment",available:!0},{name:"local_adam",summary:"Local Adam",available:!0},{name:"ortho_adam",summary:"Orthogonal Adam",available:!0},{name:"riemannian_orthogonal",summary:"Riemannian orthogonal update (Muon-family)",available:!0},{name:"muon",summary:"Muon update",available:!0},{name:"lion",summary:"Lion optimizer",available:!0},{name:"spectral_constrained",summary:"Spectral-norm constrained update",available:!0},{name:"mean_norm",summary:"Mean-norm update",available:!0},{name:"elastic_consolidation",summary:"EWC elastic consolidation",available:!0},{name:"natural_gradient",summary:"Natural gradient (Fisher)",available:!0},{name:"role_split",summary:"Role-split update",available:!0}]}},Xb={axes:qb},Dp=.72,Ip=.86;function ro(s,e,t,n,i){const{camera:r,controls:a}=s,o=(i==null?void 0:i.clone())??r.position.clone().sub(a.target);o.lengthSq()===0&&o.set(.4,.5,.8),o.normalize();const l=o.clone().negate(),c=new V().crossVectors(l,new V(0,1,0)).normalize(),h=new V().crossVectors(c,l).normalize(),d=Math.tan((r.fov??60)*Math.PI/360),u=d*(r.aspect||1),f=d*Ip,g=u*Dp;let x=0;[e.x,t.x].forEach(p=>{[e.y,t.y].forEach(m=>{[e.z,t.z].forEach(b=>{const _=new V(p,m,b),S=Math.max(Math.abs(_.dot(c))/g,Math.abs(_.dot(h))/f)+_.dot(o);x=Math.max(x,S)})})}),x*=1.06,n.add(c.clone().multiplyScalar(.28*u*x)).add(h.clone().multiplyScalar(-.14*d*x)),a.target.copy(n),r.position.copy(n).add(o.clone().multiplyScalar(x)),a.update()}const Ja=["credit","geometry","dynamics","substrate","plasticity","update"];function Si(s,e,t){return`${s}|${e}|${t}`}function ts(s){return s.length===0?0:s.reduce((e,t)=>e+t,0)/s.length}function Yb(s){if(s.length<2)return 0;const e=ts(s),t=s.reduce((n,i)=>n+(i-e)**2,0)/(s.length-1);return Math.sqrt(t)}function jb(s){const e=new Map;for(const t of s)for(const n of t){const i=e.get(n.epoch)??[];i.push(n.val_acc),e.set(n.epoch,i)}return Array.from(e.entries()).sort((t,n)=>t[0]-n[0]).map(([t,n])=>({epoch:t,val_acc:ts(n)}))}function Kb(s,e){const t=new Map;return s.cells.forEach(n=>{t.set(Si(n.coordinate[e.x],n.coordinate[e.y],n.coordinate[e.z]),n)}),t}function Jb(s,e){const t=new Map;return((s==null?void 0:s.records)??[]).forEach((i,r)=>{var h;const a=i==null?void 0:i.coordinate;if(!a)return;const o=Si(a[e.x],a[e.y],a[e.z]);let l=t.get(o);l||(l={acc:[],walltime:[],params:[],curves:[],pareto:!1,coordinate:{...a},seeds:0},t.set(o,l)),l.seeds+=1;const c=i.payload??{};if(typeof c.val_acc=="number"&&l.acc.push(c.val_acc),typeof c.walltime_s=="number"&&l.walltime.push(c.walltime_s),typeof c.param_count=="number"&&l.params.push(c.param_count),Array.isArray(c.convergence_curve)){const d=c.convergence_curve.filter(u=>typeof(u==null?void 0:u.epoch)=="number"&&typeof(u==null?void 0:u.val_acc)=="number").map(u=>({epoch:u.epoch,val_acc:u.val_acc}));d.length>0&&l.curves.push(d)}(h=s==null?void 0:s.pareto)!=null&&h[r]&&(l.pareto=!0)}),t}function Zh(s,e){const t=Array.from(s.values()),n=bl(t,e);return t.sort((i,r)=>Za(i,e,n).localeCompare(Za(r,e,n)))}function bl(s,e){return[e.x,e.y,e.z].filter(n=>new Set(s.map(r=>r.coordinate[n])).size>1)}function Za(s,e,t){return(t.length>0?t:[e.x,e.y,e.z]).map(i=>s.coordinate[i]??"").join(" · ")}function ju(s){const e={credit:new Set,geometry:new Set,dynamics:new Set,substrate:new Set,plasticity:new Set,update:new Set};s.forEach(n=>{const i=n==null?void 0:n.coordinate;i&&Ja.forEach(r=>{const a=i[r];typeof a=="string"&&a.length>0&&e[r].add(a)})});const t={};return Ja.forEach(n=>{t[n]=Array.from(e[n]).sort()}),t}class Zb{constructor(){T(this,"runId",null);T(this,"metrics",null);T(this,"axes",{x:"credit",y:"geometry",z:"dynamics"});T(this,"space",null);T(this,"spaceCells",new Map);T(this,"aggregates",new Map);T(this,"values",ju([]));T(this,"chance",.1);T(this,"requiredSeeds",0);T(this,"gate",null);T(this,"timeline",null);T(this,"account",null);T(this,"flow",null);T(this,"attribution",null);T(this,"dynamics",null);T(this,"multirun",null);T(this,"trainedDynamics",null);T(this,"spaceRequest","");T(this,"accountRequest","");T(this,"attributionRequest","");T(this,"flowRequest","");T(this,"dynamicsRun","");T(this,"dynamicsAsking",!1);T(this,"trainedDynamicsRun","");T(this,"trainedDynamicsAsking",!1);T(this,"multirunRequest","");T(this,"multirunAsking",!1);T(this,"timelineRun","");T(this,"timelineStale",!0);T(this,"timelineTimer",null);T(this,"listeners",[]);Yn.onChange((e,t)=>{this.absorb(e,t)}),jt.register("pipeline_event",()=>this.scheduleTimeline())}onChange(e){this.listeners.push(e)}notify(e){this.listeners.forEach(t=>t(e))}async absorb(e,t){this.runId=e,this.metrics=t,t&&(typeof t.chance=="number"&&(this.chance=t.chance),typeof t.required_seeds=="number"&&(this.requiredSeeds=t.required_seeds),t.gate&&(this.gate=t.gate,typeof t.gate.required_seeds_per_group=="number"&&(this.requiredSeeds=t.gate.required_seeds_per_group)),this.values=ju(t.records??[])),this.recomputeEvidence(),await this.syncSpace(),this.syncAccount(),this.syncAttribution(),this.syncTimeline(),this.syncDynamics(),this.syncTrainedDynamics()}setAxes(e){this.axes=e,this.notify("axes"),this.recomputeEvidence(),this.syncSpace()}recomputeEvidence(){this.aggregates=Jb(this.metrics,this.axes),this.notify("evidence")}async syncSpace(){if(!this.runId)return;const e=[this.runId,this.axes.x,this.axes.y,this.axes.z,...Ja.map(n=>this.values[n].join(","))].join("|");if(e===this.spaceRequest)return;const t=await this.fetchSpace();t&&(this.spaceRequest=e,this.space=t,this.spaceCells=Kb(t,this.axes),this.notify("space"))}async fetchSpace(){try{const e=await fetch(`/api/cells/${this.runId}/space`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({axes:[this.axes.x,this.axes.y,this.axes.z]})});return e.ok?await e.json():(console.warn("[StageState] The space was refused",e.status),null)}catch(e){return console.warn("[StageState] The space could not be read",e),null}}async syncAccount(){var n,i;if(!this.runId){this.account=null,this.accountRequest="";return}const e=((i=(n=this.metrics)==null?void 0:n.records)==null?void 0:i.length)??0,t=`${this.runId}|${e}`;if(t!==this.accountRequest)try{const r=await fetch(`/api/runs/${encodeURIComponent(this.runId)}/account`);if(!r.ok){console.warn("[StageState] The account was refused",r.status);return}this.account=await r.json(),this.accountRequest=t,this.notify("evidence")}catch(r){console.warn("[StageState] The account could not be read",r)}}async syncTimeline(){if(!this.runId){this.timeline=null,this.timelineRun="";return}if(!(!this.timelineStale&&this.timelineRun===this.runId))try{const e=await fetch(`/api/events?run_id=${encodeURIComponent(this.runId)}`);if(!e.ok){console.warn("[StageState] The timeline was refused",e.status);return}this.timeline=await e.json(),this.timelineRun=this.runId,this.timelineStale=!1,this.notify("events"),this.syncFlow()}catch(e){console.warn("[StageState] The timeline could not be read",e)}}async syncFlow(){var n;if(!this.runId){this.flow=null,this.flowRequest="";return}const e=((n=this.timeline)==null?void 0:n.events.length)??0,t=`${this.runId}|${e}`;if(t!==this.flowRequest)try{const i=await fetch(`/api/runs/${encodeURIComponent(this.runId)}/flow`);if(!i.ok){console.warn("[StageState] The flow was refused",i.status);return}this.flow=await i.json(),this.flowRequest=t,this.notify("events")}catch(i){console.warn("[StageState] The flow could not be read",i)}}async syncAttribution(){var n,i;if(!this.runId){this.attribution=null,this.attributionRequest="";return}const e=((i=(n=this.metrics)==null?void 0:n.records)==null?void 0:i.length)??0,t=`${this.runId}|${e}`;if(t!==this.attributionRequest)try{const r=await fetch(`/api/runs/${encodeURIComponent(this.runId)}/attribution`);if(!r.ok){console.warn("[StageState] The attribution was refused",r.status);return}this.attribution=await r.json(),this.attributionRequest=t,this.notify("evidence")}catch(r){console.warn("[StageState] The attribution could not be read",r)}}async syncDynamics(){if(!this.runId){this.dynamics=null,this.dynamicsRun="";return}if(!(this.dynamicsRun===this.runId||this.dynamicsAsking)){this.dynamicsAsking=!0;try{const e=await fetch(`/api/runs/${encodeURIComponent(this.runId)}/dynamics`);if(!e.ok){console.warn("[StageState] The dynamics were refused",e.status);return}const t=await e.json();this.dynamics=t,t.cell&&(this.dynamicsRun=this.runId),this.notify("evidence")}catch(e){console.warn("[StageState] The dynamics could not be read",e)}finally{this.dynamicsAsking=!1}}}async syncTrainedDynamics(){if(!this.runId){this.trainedDynamics=null,this.trainedDynamicsRun="";return}if(!(this.trainedDynamicsRun===this.runId||this.trainedDynamicsAsking)){this.trainedDynamicsAsking=!0;try{const e=await fetch(`/api/runs/${encodeURIComponent(this.runId)}/dynamics/trained`);if(!e.ok){console.warn("[StageState] The trained dynamics were refused",e.status);return}const t=await e.json();this.trainedDynamics=t,t.cell&&(this.trainedDynamicsRun=this.runId),this.notify("evidence")}catch(e){console.warn("[StageState] The trained dynamics could not be read",e)}finally{this.trainedDynamicsAsking=!1}}}scheduleTimeline(){this.timelineStale=!0,this.timelineTimer===null&&(this.timelineTimer=window.setTimeout(()=>{this.timelineTimer=null,this.syncTimeline()},300))}async syncMultirun(e=!1){const t=[this.axes.x,this.axes.y,this.axes.z].join("|");if(!(!e&&(t===this.multirunRequest||this.multirunAsking))){this.multirunAsking=!0;try{const n=await fetch("/api/spaces",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({axes:[this.axes.x,this.axes.y,this.axes.z]})});if(!n.ok){console.warn("[StageState] The runs' space was refused",n.status);return}this.multirun=await n.json(),this.multirunRequest=t,this.notify("evidence")}catch(n){console.warn("[StageState] The runs' space could not be read",n)}finally{this.multirunAsking=!1}}}}const ve=new Zb;function sa(s,e=10){if(s.length<=e)return[s];const t=[];let n="";for(const i of s.split("_")){const r=n?`${n}_${i}`:i;r.length>e&&n?(t.push(n),n=i):n=r}return n&&t.push(n),t}function mn(s,e,t,n){const i=sa(s),r=document.createElement("canvas"),a=r.getContext("2d"),o=64,l=72;a.font=`bold ${o}px "JetBrains Mono", monospace`;const c=Math.max(...i.map(x=>a.measureText(x).width))+16;r.width=Math.max(64,Math.ceil(c)),r.height=i.length*l+16,a.font=`bold ${o}px "JetBrains Mono", monospace`,a.fillStyle="#ffffff",a.textAlign="center",a.textBaseline="middle",i.forEach((x,p)=>{a.fillText(x,r.width/2,l*p+l/2+8)});const h=new Yh(r);h.needsUpdate=!0;const d=t.clone();d.map=h,d.transparent=!0;const u=new Tp(d),f=r.width/r.height;let g=e*i.length;return n!==void 0&&(g=Math.min(g,n/f)),u.scale.set(g*f,g,1),u}function Qb(){const e=document.createElement("canvas");e.width=64,e.height=64;const t=e.getContext("2d");t.fillStyle="#ffffff",t.beginPath(),t.arc(64/2,64/2,64/2-2,0,Math.PI*2),t.fill();const n=new Yh(e);return n.needsUpdate=!0,n}function eS(s,e,t=.14){const i=document.createElement("canvas");i.width=128,i.height=128;const r=i.getContext("2d");r.strokeStyle=s,r.lineWidth=128*t,r.beginPath(),r.arc(128/2,128/2,128/2-r.lineWidth,0,Math.PI*2),r.stroke();const a=new Yh(i);a.needsUpdate=!0;const o=new Mi({map:a,transparent:!0,depthWrite:!1}),l=new Tp(o);return l.scale.set(e*2,e*2,1),l}const Ku=Xb.axes,tS={measured:"Measured — the run has evidence here",legal:"Legal — a gap nobody has measured",void:"Void — the system refuses this cell"};class nS{constructor(){T(this,"name","DiscoveryMap");T(this,"scene",new wp);T(this,"camera",new An);T(this,"renderer",null);T(this,"cells",new Map);T(this,"cellDataMap",new Map);T(this,"cellHeights",new Map);T(this,"xValues",[]);T(this,"yValues",[]);T(this,"zValues",[]);T(this,"cellSize",.8);T(this,"spacing",1.1);T(this,"raycaster",new Eb);T(this,"mouse",new Xe);T(this,"selectedCell",null);T(this,"hoveredCell",null);T(this,"legendElement",null);T(this,"readoutElement",null);T(this,"pointerX",0);T(this,"pointerY",0);T(this,"axisLabelMeshes",[]);T(this,"voidMesh",null);T(this,"visible",!1);T(this,"onQueueUpdate",e=>{});T(this,"onCampaignMetrics",e=>{const t=e==null?void 0:e.data;if(!(t!=null&&t.run))return;const n=typeof(e==null?void 0:e.campaign_id)=="string"?e.campaign_id:null;n&&Yn.observe(n,t)});jt.register("queue_update",this.onQueueUpdate),jt.register("campaign_metrics",this.onCampaignMetrics)}async init(){const e=Fi();e&&(this.scene=e.scene,this.camera=e.camera,this.renderer=e.renderer),this.setupInteraction(),this.createLegend(),this.createReadout(),ir("discovery-legend","legend","▦",()=>this.legendElement,Zi.legend),ve.onChange(()=>this.updateLegend()),Yn.onChange(()=>this.updateRunPicker()),console.log("[DiscoveryMap] Initialized")}async destroy(){var e,t;jt.unregister("queue_update",this.onQueueUpdate),jt.unregister("campaign_metrics",this.onCampaignMetrics),this.clearGrid(),(e=this.legendElement)==null||e.remove(),(t=this.readoutElement)==null||t.remove()}show(){this.visible=!0,this.applyAxes()}hide(){this.visible=!1,this.clearGrid()}refreshView(e){if(this.visible){if(e==="space"){this.applyAxes();return}e==="evidence"&&this.applyAggregates()}}hasMeasured(){return this.cellDataMap.size>0&&this.cellHeights.size>0}updateLegend(){var h,d,u,f,g;const e=ve.space,t=!!e,i=ve.values.credit.length>0,r=(h=this.legendElement)==null?void 0:h.querySelector("#legend-empty-state"),a=(d=this.legendElement)==null?void 0:d.querySelector("#legend-view"),o=(u=this.legendElement)==null?void 0:u.querySelector("#legend-arms-block"),l=(f=this.legendElement)==null?void 0:f.querySelector("#legend-axes-block");r&&(r.style.display=t?"none":"flex"),a&&(a.style.display=t?"block":"none"),o&&(o.style.display=i?"block":"none"),l&&(l.style.display=t?"block":"none");const c=(g=this.legendElement)==null?void 0:g.querySelector("#legend-cell-count");if(c&&e){const x={measured:Array.from(ve.aggregates.keys()).filter(p=>ve.spaceCells.has(p)).length,legal:e.counts.legal,void:e.counts.void};c.textContent=`${x.measured+x.legal+x.void} cells`}this.refreshAxisOptions(),this.updateLegendArms(),this.updateLegendAxes()}setupInteraction(){var t;const e=(t=this.renderer)==null?void 0:t.domElement;e&&(this.raycaster.params.Line.threshold=this.cellSize*.2,e.addEventListener("mousemove",n=>{const i=e.getBoundingClientRect();this.mouse.x=(n.clientX-i.left)/i.width*2-1,this.mouse.y=-((n.clientY-i.top)/i.height)*2+1,this.pointerX=n.clientX,this.pointerY=n.clientY}),e.addEventListener("mouseleave",()=>{this.hideReadout()}),e.addEventListener("click",()=>{this.hoveredCell&&this.selectCell(this.hoveredCell)}))}createReadout(){const e=document.getElementById("ui-overlay");e&&(this.readoutElement=document.createElement("div"),this.readoutElement.id="cell-readout",this.readoutElement.style.cssText=`
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
    `,e.appendChild(this.readoutElement))}showReadout(e){const t=this.readoutElement;if(!t)return;t.innerHTML="";const n=document.createElement("div");n.style.cssText="display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 8px;",Object.entries(e.coordinate).filter(([,u])=>u).forEach(([u,f])=>{const g=u==="credit",x=g?Wt[f]||F.gradient:"var(--text-secondary)",p=document.createElement("span");p.style.cssText=`
          padding: 2px 8px;
          background: ${g?x+"22":"var(--bg-tertiary)"};
          border: 1px solid ${g?x+"88":"var(--border)"};
          border-radius: 10px;
          font-size: 10px;
          color: ${x};
          font-weight: ${g?"600":"400"};
        `,p.textContent=`${u}=${f}`,n.appendChild(p)}),t.appendChild(n);const i=document.createElement("div");i.style.cssText="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;";const r={measured:F.measured,legal:F.legal_unmeasured,void:F.void},a={measured:"●",legal:"○",void:"✕"},o=document.createElement("span");o.style.cssText=`font-size: 14px; color: ${r[e.status]};`,o.textContent=a[e.status],i.appendChild(o);const l=document.createElement("span");if(l.style.cssText=`font-weight: 600; color: ${r[e.status]}; font-size: 12px;`,l.textContent=tS[e.status],i.appendChild(l),t.appendChild(i),e.status==="measured"&&e.metrics){const u=e.metrics,f=document.createElement("div");f.style.cssText="display: flex; gap: 16px; font-size: 11px; color: var(--text-secondary);";const g=u.val_acc??0,x=u.val_acc_std??0,p=u.n_seeds??0,m=u.walltime_s;f.innerHTML=`
        <span>acc <strong style="color: var(--text-primary);">${g.toFixed(3)}</strong> ± ${x.toFixed(3)}</span>
        <span>n=<strong style="color: var(--text-primary);">${p}</strong></span>
        <span>${m!==void 0?`${m.toFixed(1)}s`:""}</span>
        ${e.pareto?'<span style="color: var(--pareto);">● PARETO</span>':""}
      `,t.appendChild(f)}if(e.status==="legal"){const u=document.createElement("div");u.style.cssText="margin-top: 6px; padding: 6px 8px; background: var(--bg-tertiary); border-radius: 4px; font-size: 10px; color: var(--text-muted);";const f=e.requiredSeeds??0;u.textContent=`Click to queue ${f} seeds →`,t.appendChild(u)}if(e.voidReason){const u=document.createElement("div");u.style.cssText="margin-top: 6px; padding: 6px 8px; background: var(--void)11; border: 1px solid var(--void)44; border-radius: 4px; font-size: 10px; color: var(--void);",u.textContent=e.voidReason,t.appendChild(u)}t.style.display="block";const c=t.getBoundingClientRect(),h=Math.min(this.pointerX+16,window.innerWidth-c.width-8),d=Math.min(this.pointerY+16,window.innerHeight-c.height-8);t.style.left=`${Math.max(8,h)}px`,t.style.top=`${Math.max(8,d)}px`}hideReadout(){this.readoutElement&&(this.readoutElement.style.display="none")}createLegend(){const e=document.getElementById("ui-overlay");e&&(this.legendElement=document.createElement("div"),this.legendElement.id="discovery-legend",this.legendElement.style.cssText=`
      position: fixed;
      bottom: 140px;
      left: 20px;
      background: var(--bg-secondary);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 16px;
      font-size: 12px;
      z-index: 100;
      min-width: 240px;
      max-width: 360px;
      box-shadow: 0 8px 32px rgba(0,0,0,0.4);
      backdrop-filter: blur(8px);
    `,this.legendElement.innerHTML=`
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
        <div class="legend-item" style="display: flex; align-items: center; gap: 8px;">
          <div style="width: 14px; height: 14px; background: var(--measured); border-radius: 3px; box-shadow: 0 0 10px var(--measured);"></div>
          <span style="font-size: 11px;">Measured — glowing pillar</span>
        </div>
        <div class="legend-item" style="display: flex; align-items: center; gap: 8px;">
          <div style="width: 14px; height: 14px; background: transparent; border: 2px solid var(--legal-unmeasured); border-radius: 3px;"></div>
          <span style="font-size: 11px;">Legal gap — click to queue</span>
        </div>
        <div class="legend-item" style="display: flex; align-items: center; gap: 8px;">
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
        <select id="legend-run-picker" style="
          width: 100%;
          background: var(--bg-tertiary);
          color: var(--text-primary);
          border: 1px solid var(--border);
          border-radius: 6px;
          font-size: 11px;
          padding: 6px 10px;
        "></select>
        <div id="legend-run" style="font-size: 11px; color: var(--text-secondary); margin-top: 6px; min-height: 16px;"></div>
      </div>
      <div id="legend-axes-block" style="margin-top: 10px; padding-top: 10px; border-top: 1px solid var(--border); display: none;">
        <div style="font-weight: 600; margin-bottom: 6px; font-size: 11px;">Axes (click to change)</div>
        <div id="legend-axis-picker" style="display: flex; flex-direction: column; gap: 5px;"></div>
        <div id="legend-axes" style="font-size: 10px; color: var(--text-muted); margin-top: 6px;"></div>
      </div>
    `,e.appendChild(this.legendElement),this.createRunPicker(),this.createAxisPicker(),this.updateLegendArms(),this.updateLegendAxes())}createRunPicker(){var t;const e=(t=this.legendElement)==null?void 0:t.querySelector("#legend-run-picker");e&&e.addEventListener("change",()=>{Yn.select(e.value||null)})}updateRunPicker(){var a,o,l;const e=(a=this.legendElement)==null?void 0:a.querySelector("#legend-run-picker"),t=(o=this.legendElement)==null?void 0:o.querySelector("#legend-run");if(!e)return;const n=Yn.runs;if(e.innerHTML="",n.forEach(([c,h])=>{var g,x;const d=document.createElement("option"),u=((g=h==null?void 0:h.run)==null?void 0:g.profile)??"run",f=((x=h==null?void 0:h.records)==null?void 0:x.length)??0;d.value=c,d.textContent=`${c.slice(0,8)} · ${u} · ${f}`,d.selected=c===Yn.selectedId,e.appendChild(d)}),n.length===0){e.disabled=!0,t&&(t.textContent="No run has reported yet.");return}e.disabled=!1;const i=Yn.selected;if(!t)return;if(!i){t.textContent="";return}const r=i.run??{};t.textContent=[`run ${(Yn.selectedId??"").slice(0,8)}`,r.mode,`${((l=i.records)==null?void 0:l.length)??0} records`].filter(Boolean).join(" · ")}createAxisPicker(){var n;const e=(n=this.legendElement)==null?void 0:n.querySelector("#legend-axis-picker");if(!e)return;["x","y","z"].forEach(i=>{const r=document.createElement("div");r.className="axis-row",r.dataset.dimension=i,r.style.cssText=`
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 3px;
        font-size: 11px;
        margin-bottom: 3px;
      `;const a=document.createElement("span");a.textContent=i.toUpperCase(),a.style.cssText="color: var(--text-secondary); width: 12px;",r.appendChild(a),e.appendChild(r)}),this.refreshAxisOptions()}refreshAxisOptions(){var t;const e=(t=this.legendElement)==null?void 0:t.querySelectorAll("#legend-axis-picker .axis-row");e&&e.forEach(n=>{const i=n.dataset.dimension,r=new Set(["x","y","z"].filter(o=>o!==i).map(o=>ve.axes[o]));n.innerHTML="";const a=document.createElement("span");a.textContent=i.toUpperCase(),a.style.cssText="color: var(--text-secondary); width: 12px;",n.appendChild(a),Ja.forEach(o=>{var h;const l=ve.axes[i]===o,c=document.createElement("button");c.className="axis-button",c.dataset.axis=o,c.textContent=((h=Ku[o])==null?void 0:h.display_name)??o,c.disabled=r.has(o),c.style.cssText=`
          flex: 0 0 auto;
          padding: 1px 5px;
          background: ${l?"var(--bg-primary)":"var(--bg-tertiary)"};
          border: 1px solid ${l?"var(--border-bright)":"var(--border)"};
          border-radius: 4px;
          color: ${l?"var(--text-primary)":"var(--text-secondary)"};
          font-size: 10px;
          cursor: pointer;
          opacity: ${r.has(o)?.4:1};
        `,c.addEventListener("click",()=>{ve.setAxes({...ve.axes,[i]:o})}),n.appendChild(c)})})}updateLegendArms(){var n;const e=(n=this.legendElement)==null?void 0:n.querySelector("#legend-arms");if(!e)return;const t=ve.values.credit;if(t.length===0){e.innerHTML='<span style="color: var(--text-muted); font-size: 11px;">No arm measured yet.</span>';return}e.innerHTML=t.map(i=>{const r=Wt[i]||F.gradient;return`<span style="display: inline-flex; align-items: center; gap: 4px; padding: 2px 8px; background: ${r}22; border: 1px solid ${r}88; border-radius: 12px; color: ${r}; font-size: 11px;">${i}</span>`}).join("")}updateLegendAxes(){var l;const e=(l=this.legendElement)==null?void 0:l.querySelector("#legend-axes");if(!e)return;const t=ve.space;if(!t){e.textContent="Waiting for the run's declared space — the axes come from the ontology.";return}const n=(c,h)=>{var g;const d=t.available[c]??h.length,u=d>h.length?` (${h.length} of ${d})`:"";return`${((g=Ku[c])==null?void 0:g.display_name)??c}${u}`},i=Object.entries(t.held).map(([c,h])=>`${c}=${h}`),r={measured:Array.from(ve.aggregates.keys()).filter(c=>ve.spaceCells.has(c)).length,legal:t.counts.legal,void:t.counts.void},a=t.cells.length,o=Object.entries(t.void_rules??{}).sort((c,h)=>h[1]-c[1]).slice(0,2).map(([c,h])=>`${c.replace(/_/g," ")} (${h})`);e.innerHTML=[`<div>X: ${n(ve.axes.x,t.values[ve.axes.x]??[])}</div>`,`<div>Y: ${n(ve.axes.y,t.values[ve.axes.y]??[])}</div>`,`<div>Z: ${n(ve.axes.z,t.values[ve.axes.z]??[])}</div>`,`<div style="margin-top: 6px;">held: ${i.join(" · ")||"—"}</div>`,`<div style="margin-top: 6px;">${r.measured} measured · ${r.legal} legal · ${r.void} void (of ${a})</div>`,o.length>0?`<div style="margin-top: 6px;">refused by: ${o.join(", ")}</div>`:""].join("")}applyAxes(){const e=ve.space,t=ve.axes;this.xValues=(e==null?void 0:e.values[t.x])??[],this.yValues=(e==null?void 0:e.values[t.y])??[],this.zValues=(e==null?void 0:e.values[t.z])??[],this.buildGrid(),this.updateLegend()}buildGrid(){if(this.clearGrid(),!this.visible)return;this.createAxisLabels();const e=[];this.yValues.forEach((t,n)=>{this.zValues.forEach((i,r)=>{this.xValues.forEach((a,o)=>{const l=Si(a,t,i),c=ve.spaceCells.get(l),h=(c==null?void 0:c.status)??"legal",d={coordinate:this.coordinateFor(a,t,i),status:h,chance:ve.chance,requiredSeeds:ve.requiredSeeds,runId:ve.runId??void 0,voidReason:c==null?void 0:c.reason,inDeclaration:c==null?void 0:c.in_declaration};if(this.cellDataMap.set(l,d),h==="void"){e.push(...this.voidMarkerPositions(o,n,r));return}this.createCell(l,d,o,n,r)})})}),e.length>0&&this.createVoidMarkers(e),this.frameGrid()}coordinateFor(e,t,n){const i={credit:"",geometry:"",dynamics:"",substrate:"",plasticity:"",update:""};return i[ve.axes.x]=e,i[ve.axes.y]=t,i[ve.axes.z]=n,Ja.forEach(r=>{var o,l;if(i[r])return;const a=(l=(o=ve.space)==null?void 0:o.held)==null?void 0:l[r];a&&(i[r]=a)}),i}createAxisLabels(){this.axisLabelMeshes.forEach(h=>this.scene.remove(h)),this.axisLabelMeshes=[];const e=new Mi({color:9148584,sizeAttenuation:!0}),t=new Mi({color:13227232,sizeAttenuation:!0}),n=(this.xValues.length-1)*this.spacing,r=(this.zValues.length-1)*this.spacing/2+1.2,a=-.45;this.xValues.forEach((h,d)=>{const u=(d-(this.xValues.length-1)/2)*this.spacing,f=mn(h,.3,e,this.spacing*.95);f.position.set(u,a,r),this.scene.add(f),this.axisLabelMeshes.push(f)});const o=mn(ve.axes.x,.3,t);o.position.set(n/2+1.15,a,r),this.scene.add(o),this.axisLabelMeshes.push(o);const l=mn(ve.axes.z,.3,t);l.position.set(0,a,r+1.1),this.scene.add(l),this.axisLabelMeshes.push(l);const c=mn(ve.axes.y,.3,t);c.position.set(-(n/2)-1.5,1.3,0),this.scene.add(c),this.axisLabelMeshes.push(c)}createCell(e,t,n,i,r){const a=(n-(this.xValues.length-1)/2)*this.spacing,o=i*this.spacing,l=(r-(this.zValues.length-1)/2)*this.spacing,c=t.status==="measured"?this.createMeasuredCell(t):this.createLegalCell();c.position.set(a,o,l),c.userData={...c.userData,cellKey:e},this.scene.add(c),this.cells.set(e,c)}createMeasuredCell(e){const t=this.pillarHeight(e),n=Wt[e.coordinate.credit]||F.gradient,i=new _i(this.cellSize,t,this.cellSize);i.translate(0,t/2,0);const r=new Kr({color:new nt(n),emissive:new nt(n),emissiveIntensity:.5,transparent:!0,opacity:.9,metalness:.3,roughness:.4}),a=new Xt(i,r);a.castShadow=!0,a.receiveShadow=!0;const o=new _i(this.cellSize*1.1,t*1.1,this.cellSize*1.1);o.translate(0,t/2,0);const l=new es({color:new nt(n),transparent:!0,opacity:.15,depthWrite:!1}),c=new Xt(o,l);return a.add(c),a.userData.glow=c,a}createLegalCell(){const e=new _i(this.cellSize,this.cellSize,this.cellSize),t=new vb(e);t.translate(0,this.cellSize/2,0);const n=new Ms({color:F.legal_unmeasured,transparent:!0,opacity:.55}),i=new jr(t,n),r=new Xt(new _i(this.cellSize,this.cellSize,this.cellSize),new es);return r.position.y=this.cellSize/2,r.visible=!1,i.add(r),i}disposeMesh(e){e.traverse(t=>{const n=t.geometry;n&&n.dispose();const i=t.material;Array.isArray(i)?i.forEach(r=>r.dispose()):i&&i.dispose()})}voidMarkerPositions(e,t,n){const i=(e-(this.xValues.length-1)/2)*this.spacing,r=t*this.spacing,a=(n-(this.zValues.length-1)/2)*this.spacing,o=this.cellSize*.6,l=.1;return[i-o,r+l,a-o,i+o,r+l,a+o,i+o,r+l,a-o,i-o,r+l,a+o]}createVoidMarkers(e){const t=new Jt;t.setAttribute("position",new It(e,3));const n=new Ms({color:F.void,transparent:!0,opacity:.32});this.voidMesh=new jr(t,n),this.scene.add(this.voidMesh)}frameGrid(){const e=Fi();if(!(e!=null&&e.controls)||this.xValues.length===0||this.zValues.length===0)return;const t=(this.xValues.length-1)*this.spacing/2+this.cellSize,n=(this.zValues.length-1)*this.spacing/2+this.cellSize,i=(this.yValues.length-1)*this.spacing+this.cellSize,r=n+1.8,a=-.8;ro(e,new V(-t,a,-n),new V(t,i,r),new V(0,i/2,0))}clearGrid(){this.cells.forEach(e=>{this.scene.remove(e),this.disposeMesh(e)}),this.cells.clear(),this.cellDataMap.clear(),this.cellHeights.clear(),this.axisLabelMeshes.forEach(e=>{this.scene.remove(e),this.disposeMesh(e)}),this.axisLabelMeshes=[],this.voidMesh&&(this.scene.remove(this.voidMesh),this.voidMesh.geometry.dispose(),Array.isArray(this.voidMesh.material)?this.voidMesh.material.forEach(e=>e.dispose()):this.voidMesh.material.dispose(),this.voidMesh=null)}applyAggregates(){this.visible&&(ve.aggregates.forEach((e,t)=>{const n=this.cellDataMap.get(t);n&&(n.status="measured",n.coordinate={...e.coordinate},n.metrics={val_acc:ts(e.acc),val_acc_std:Yb(e.acc),walltime_s:ts(e.walltime),param_count:ts(e.params),n_seeds:e.acc.length},n.curve=jb(e.curves),n.pareto=e.pareto,n.chance=ve.chance,n.requiredSeeds=ve.requiredSeeds,n.runId=ve.runId??void 0,this.updateCellVisual(t,n,e.pareto))}),this.updateLegendAxes())}pillarHeight(e){var t;return sx.lerp(.4,3.4,((t=e.metrics)==null?void 0:t.val_acc)??0)}updateCellVisual(e,t,n){const i=this.cells.get(e);if(!i)return;const r=i.position.clone(),a=i.userData.glow;a&&i.remove(a),this.scene.remove(i),this.disposeMesh(i);const o=this.createMeasuredCell(t);o.position.copy(r),o.userData.cellKey=e;const l=this.pillarHeight(t),c=this.cellHeights.get(e)??0;if(this.cellHeights.set(e,l),o.scale.y=l>0?Math.min(1,Math.max(c/l,.001)):1,n){const h=new jh(this.cellSize*.6,this.cellSize*.8,32),d=new es({color:F.pareto,side:Nn,transparent:!0,opacity:.6}),u=new Xt(h,d);u.rotation.x=-Math.PI/2,u.position.y=.05,o.add(u),o.userData.paretoRing=u}this.scene.add(o),this.cells.set(e,o)}selectCell(e){this.selectedCell=e;const t=this.cellDataMap.get(e);t&&window.dispatchEvent(new CustomEvent("cell-selected",{detail:t}))}update(e){if(!this.visible){this.hideReadout();return}const t=1-Math.exp(-e*8);this.cells.forEach((a,o)=>{const l=this.cellDataMap.get(o);if((l==null?void 0:l.status)==="measured"&&a instanceof Xt&&a.material instanceof Kr){a.scale.y<1&&(a.scale.y=Math.min(1,a.scale.y+(1-a.scale.y)*t));const c=a.userData.glow;c&&(c.material.opacity=.1+.1*Math.sin(Date.now()*.003));const h=a.userData.paretoRing;h&&(h.material.opacity=.4+.2*Math.sin(Date.now()*.005))}}),this.raycaster.setFromCamera(this.mouse,this.camera);const n=this.raycaster.intersectObjects(Array.from(this.cells.values()),!0);let i=null;n.length>0&&(i=this.pickCell(n)),i||(i=this.voidCellUnderCursor()),i!==this.hoveredCell&&(this.hoveredCell&&this.highlightCell(this.hoveredCell,!1),this.hoveredCell=i,i&&this.highlightCell(i,!0));const r=i?this.cellDataMap.get(i):void 0;r?this.showReadout(r):this.hideReadout()}pickCell(e){var n,i;let t=null;for(const r of e){const a=r.object.userData.cellKey||((n=r.object.parent)==null?void 0:n.userData.cellKey);if(a&&(t??(t=a),((i=this.cellDataMap.get(a))==null?void 0:i.status)==="measured"))return a}return t}voidCellUnderCursor(){if(!this.voidMesh)return null;const e=this.raycaster.params.Line.threshold;this.raycaster.params.Line.threshold=this.cellSize*.3;try{const t=this.raycaster.intersectObject(this.voidMesh,!1);return t.length===0?null:this.cellAt(t[0].point)}finally{this.raycaster.params.Line.threshold=e}}cellAt(e){const t=Math.round(e.x/this.spacing+(this.xValues.length-1)/2),n=Math.round(e.y/this.spacing),i=Math.round(e.z/this.spacing+(this.zValues.length-1)/2);return t<0||t>=this.xValues.length||n<0||n>=this.yValues.length||i<0||i>=this.zValues.length?null:Si(this.xValues[t],this.yValues[n],this.zValues[i])}highlightCell(e,t){var r;const n=this.cells.get(e);if(!n)return;const i=(r=this.renderer)==null?void 0:r.domElement;if(i&&(i.style.cursor=t&&this.isCellActionable(e)?"pointer":"grab"),n instanceof Xt&&n.material instanceof Kr){t?(n.userData.originalEmissive=n.material.emissiveIntensity,n.userData.originalScale=n.scale.y,n.material.emissiveIntensity=(n.userData.originalEmissive||.5)+.5,n.scale.y=Math.min(1.05,n.scale.y*1.08)):(n.userData.originalEmissive!==void 0&&(n.material.emissiveIntensity=n.userData.originalEmissive),n.userData.originalScale!==void 0&&(n.scale.y=n.userData.originalScale));return}n instanceof jr&&n.material instanceof Ms&&(t?(n.userData.originalOpacity=n.material.opacity,n.material.opacity=.95,n.material.linewidth=2):n.userData.originalOpacity!==void 0&&(n.material.opacity=n.userData.originalOpacity,n.material.linewidth=1))}isCellActionable(e){const t=this.cellDataMap.get(e);return t?t.status==="legal"||t.status==="measured":!1}}const Js=new nS;Kn.register(Js);class iS{constructor(){T(this,"name","CellDrawer");T(this,"panel",null);T(this,"content",null);T(this,"sparklineCanvas",null);T(this,"currentData",null);T(this,"onKeyDown",e=>{e.key==="Escape"&&this.currentData&&this.hide()});T(this,"onCellSelected",e=>{this.show(e.detail)})}async init(){this.createPanel(),this.setupEvents(),Pp("cell-drawer","cell drawer","◧",()=>this.hide(),()=>this.isOpen()),console.log("[CellDrawer] Initialized")}async destroy(){var e;this.stopSparkline(),(e=this.panel)==null||e.remove(),window.removeEventListener("cell-selected",this.onCellSelected),window.removeEventListener("keydown",this.onKeyDown)}createPanel(){const e=document.getElementById("ui-overlay");e&&(this.panel=document.createElement("div"),this.panel.id="cell-drawer",this.panel.style.cssText=`
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
    `,e.appendChild(this.panel),this.content=this.panel.querySelector("#drawer-content"),this.panel.querySelector("#drawer-close").addEventListener("click",()=>this.hide()))}setupEvents(){window.addEventListener("cell-selected",this.onCellSelected),window.addEventListener("keydown",this.onKeyDown)}shiftPanels(e){const t=e?400:44;["hud","chart-column"].forEach(n=>{var i;(i=document.getElementById(n))==null||i.style.setProperty("right",`${t}px`)})}isOpen(){return this.panel?this.panel.style.transform==="translateX(0)":!1}show(e){this.currentData=e,this.renderContent(e),this.panel.style.transform="translateX(0)",this.shiftPanels(!0),this.startSparkline(e)}hide(){this.panel.style.transform="translateX(100%)",this.shiftPanels(!1),this.stopSparkline(),this.currentData=null}renderContent(e){if(!this.content)return;const{coordinate:t,metrics:n,status:i}=e,r=Wt[t.credit]||F.gradient,a=(n==null?void 0:n.val_acc)??0,o=(n==null?void 0:n.n_seeds)??0,l=e.chance??.1,c=e.requiredSeeds??0;let h="UNMEASURED",d=F.legal_unmeasured;i==="void"&&(h="VOID",d=F.void),i==="measured"&&(a<=l?(h="REJECTED",d=F.rejected):c>0&&o<c?(h="INSUFFICIENT",d=F.insufficient):a>l+.1?(h="PASSED",d=F.passed):(h="INSUFFICIENT",d=F.insufficient));const u=i==="measured"&&c>0?Math.max(0,c-o):"N/A";this.content.innerHTML=`
      <div style="margin-bottom: 20px;">
        <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px;">
          ${Object.entries(t).filter(([,g])=>g).map(([g,x])=>`
              <span style="
                padding: 4px 10px;
                background: ${g==="credit"?r+"22":"var(--bg-tertiary)"};
                border: 1px solid ${g==="credit"?r+"88":"var(--border)"};
                border-radius: 12px;
                font-size: 11px;
                color: ${g==="credit"?r:"var(--text-primary)"};
              ">
                ${g}=${x}
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
            background: ${d}22;
            border: 1px solid ${d}88;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            color: ${d};
            text-transform: uppercase;
          ">${h}</span>
          <span style="font-size: 12px; color: var(--text-secondary);">Chance level: ${l}</span>
        </div>
        ${e.voidReason?`<div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 8px;">${e.voidReason}</div>`:""}
        <div style="height: 4px; background: var(--bg); border-radius: 2px; overflow: hidden;">
          <div style="
            width: ${Math.min(100,a/(l*2)*100)}%;
            height: 100%;
            background: linear-gradient(90deg, ${F.rejected}, ${F.insufficient}, ${F.passed});
            border-radius: 2px;
          "></div>
        </div>
      </div>

      ${i==="measured"?`
        <div style="margin-bottom: 20px;">
          <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 8px;">SEEDS TO CLAIM</div>
          <div style="font-size: 24px; font-weight: 700; font-family: 'JetBrains Mono', monospace; color: ${F.insufficient};">
            ${u}
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
    `;const f=document.createElement("style");f.textContent=`
      .drawer-btn {
        padding: 10px 12px;
        background: var(--bg-tertiary);
        border: 1px solid var(--border);
        border-radius: 6px;
        color: var(--text-secondary);
        font-size: 11px;
        font-weight: 500;
        cursor: not-allowed;
        transition: all var(--motion-fast) var(--ease-out);
        white-space: nowrap;
      }
      .drawer-btn:not(:disabled):hover {
        background: var(--border);
        color: var(--text-primary);
        border-color: var(--border-bright);
        transform: translateY(-1px);
      }
      .drawer-btn:not(:disabled):active {
        transform: translateY(0) scale(0.98);
      }
      .drawer-btn:not(:disabled) {
        cursor: pointer;
        color: var(--text-primary);
      }
      .drawer-btn:disabled {
        opacity: 0.4;
      }
      .drawer-btn-primary:not(:disabled) {
        background: var(--gradient)22;
        border-color: var(--gradient)66;
        color: var(--gradient);
      }
      .drawer-btn-primary:not(:disabled):hover {
        background: var(--gradient)33;
        border-color: var(--gradient);
        color: var(--gradient);
      }
      .drawer-input {
        padding: 8px 10px;
        background: var(--bg-tertiary);
        border: 1px solid var(--border);
        border-radius: 6px;
        color: var(--text-primary);
        font-size: 11px;
        font-family: 'JetBrains Mono', monospace;
        transition: border-color var(--motion-fast), box-shadow var(--motion-fast);
      }
      .drawer-input:focus-visible {
        outline: none;
        border-color: var(--gradient);
        box-shadow: 0 0 0 2px var(--gradient)33;
      }
    `,this.content.appendChild(f),this.wireActions(e)}actionStates(e){var a;if(e.status==="void")return{replicate:!1,preregister:!1,quest:!1};const t=e.status==="measured",n=((a=e.metrics)==null?void 0:a.n_seeds)??0,i=e.requiredSeeds??0;return{replicate:(i>0?Math.max(0,i-n):0)>0||!t,preregister:t,quest:!t}}wireActions(e){const t=this.content;if(!t)return;const n=this.actionStates(e);t.querySelectorAll(".drawer-btn[data-action]").forEach(o=>{const l=o.dataset.action??"",c=n[l]===!0;o.disabled=!c,o.addEventListener("click",()=>{this.runAction(l,e)})});const r=t.querySelector('.drawer-btn[data-action="replicate"]');r&&(r.textContent=e.status==="measured"?"Queue Rest":"Queue");const a=t.querySelector("#drawer-action-note");a&&(a.textContent=this.actionNote(e))}actionNote(e){var i;if(!e.runId)return"This cell belongs to no run yet — nothing to queue or register.";if(e.status==="void")return`The system refuses this cell.${e.voidReason?` ${e.voidReason}`:""}`;if(e.status==="measured"){const r=((i=e.metrics)==null?void 0:i.n_seeds)??0,a=e.requiredSeeds??0,o=Math.max(0,a-r);return o>0?`Queue Rest adds ${o} more seeds to reach the claim threshold (${a} needed). Preregister locks in this cell's protocol for a confirmatory run.`:"This cell has enough seeds for a claim. Preregister locks in the protocol for a confirmatory run."}const t=e.inDeclaration===!1?" (outside this run's declaration)":"";return`Queue measures this cell (${e.requiredSeeds??0} seeds). Adopt as Quest writes the question first, then queues a new confirming run.${t}`}setStatus(e,t=!1){var i;const n=(i=this.content)==null?void 0:i.querySelector("#drawer-status");n&&(n.textContent=e,n.style.color=t?F.rejected:F.text_secondary)}async runAction(e,t){var o,l;if(!t.runId){this.setStatus("This cell belongs to no run yet.",!0);return}const n=Array.from(((o=this.content)==null?void 0:o.querySelectorAll(".drawer-btn"))??[]);n.forEach(c=>{c.disabled=!0}),this.setStatus("Working…");const i=(l=this.content)==null?void 0:l.querySelector("#drawer-threshold"),r=i!=null&&i.value?Number(i.value):null,a={coordinate:t.coordinate};r!==null&&Number.isFinite(r)&&(a.threshold=r);try{const c=await fetch(`/api/cells/${t.runId}/${e}`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(a)}),h=await c.json();if(!c.ok){this.setStatus((h==null?void 0:h.error)??"The action failed.",!0);return}this.setStatus(this.actionSummary(e,h))}catch(c){this.setStatus(`The action failed: ${String(c)}`,!0)}finally{n.forEach(c=>{c.disabled=!1})}}actionSummary(e,t){if(e==="replicate")return`Queued campaign ${t.campaign_id}: ${t.measurements} measurements in a plan of ${t.plan}.`;const i=`${t.written?"Registered":"Already registered"} ${t.path} — commit it; the run that follows it can be confirmatory.`;return e!=="quest"?i:t.campaign_id?`${i} Queued campaign ${t.campaign_id}: ${t.measurements} measurements in a plan of ${t.plan}, in a new run.`:`${i} No campaign queue is attached, so nothing is scheduled.`}startSparkline(e){const t=document.getElementById("sparkline-container");if(!t)return;this.stopSparkline();const n=e.curve??[];if(n.length===0){t.innerHTML=`
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
      `;return}const i=document.createElement("canvas");i.style.width="100%",i.style.height="100%",t.appendChild(i);const r=i.getContext("2d"),a=Math.min(window.devicePixelRatio,2),o=t.getBoundingClientRect();i.width=o.width*a,i.height=o.height*a,r.scale(a,a);const l=o.width,c=o.height,h=e.chance??.1,d=n.map(A=>A.val_acc),u=Math.min(h,...d),f=Math.max(...d,h),x=(f-u||1)*.1,p=u-x,m=f+x,b=A=>A/(n.length-1||1)*(l-20)+10,_=A=>c-10-(A-p)/(m-p)*(c-20);r.fillStyle=getComputedStyle(document.documentElement).getPropertyValue("--bg").trim()||"#0a0e14",r.fillRect(0,0,l,c);const S=_(h);r.strokeStyle=F.chance_line,r.lineWidth=1,r.setLineDash([4,4]),r.beginPath(),r.moveTo(10,S),r.lineTo(l-10,S),r.stroke(),r.setLineDash([]),r.fillStyle=F.chance_line,r.font="9px 'JetBrains Mono', monospace",r.textAlign="left",r.fillText("chance",12,S-4);const I=Wt[e.coordinate.credit]||F.gradient;r.strokeStyle=I,r.lineWidth=2,r.lineCap="round",r.lineJoin="round",r.beginPath(),n.forEach((A,R)=>{const N=b(R),M=_(A.val_acc);R===0?r.moveTo(N,M):r.lineTo(N,M)}),r.stroke(),r.fillStyle=I,n.forEach((A,R)=>{const N=b(R),M=_(A.val_acc);r.beginPath(),r.arc(N,M,3,0,Math.PI*2),r.fill()}),r.fillStyle=F.text_muted,r.font="9px 'JetBrains Mono', monospace",r.textAlign="right",r.fillText(m.toFixed(2),8,14),r.fillText(p.toFixed(2),8,c-6),this.sparklineCanvas=i}stopSparkline(){this.sparklineCanvas&&(this.sparklineCanvas.remove(),this.sparklineCanvas=null)}}const Up=new iS;Kn.register(Up);const sS=!0,ln="u-",rS="uplot",aS=ln+"hz",oS=ln+"vt",lS=ln+"title",cS=ln+"wrap",hS=ln+"under",dS=ln+"over",uS=ln+"axis",Ys=ln+"off",fS=ln+"select",pS=ln+"cursor-x",mS=ln+"cursor-y",gS=ln+"cursor-pt",xS=ln+"legend",vS=ln+"live",_S=ln+"inline",yS=ln+"series",bS=ln+"marker",Ju=ln+"label",SS=ln+"value",Ha="width",Va="height",Na="top",Zu="bottom",kr="left",Cc="right",Qh="#000",Qu=Qh+"0",Rc="mousemove",ef="mousedown",Pc="mouseup",tf="mouseenter",nf="mouseleave",sf="dblclick",MS="resize",wS="scroll",rf="change",ml="dppxchange",ed="--",pa=typeof window<"u",wh=pa?document:null,Jr=pa?window:null,ES=pa?navigator:null;let bt,Yo;function Eh(){let s=devicePixelRatio;bt!=s&&(bt=s,Yo&&Ah(rf,Yo,Eh),Yo=matchMedia(`(min-resolution: ${bt-.001}dppx) and (max-resolution: ${bt+.001}dppx)`),Zs(rf,Yo,Eh),Jr.dispatchEvent(new CustomEvent(ml)))}function Xn(s,e){if(e!=null){let t=s.classList;!t.contains(e)&&t.add(e)}}function Th(s,e){let t=s.classList;t.contains(e)&&t.remove(e)}function Ot(s,e,t){s.style[e]=t+"px"}function fi(s,e,t,n){let i=wh.createElement(s);return e!=null&&Xn(i,e),t!=null&&t.insertBefore(i,n),i}function ti(s,e){return fi("div",s,e)}const af=new WeakMap;function Li(s,e,t,n,i){let r="translate("+e+"px,"+t+"px)",a=af.get(s);r!=a&&(s.style.transform=r,af.set(s,r),e<0||t<0||e>n||t>i?Xn(s,Ys):Th(s,Ys))}const of=new WeakMap;function lf(s,e,t){let n=e+t,i=of.get(s);n!=i&&(of.set(s,n),s.style.background=e,s.style.borderColor=t)}const cf=new WeakMap;function hf(s,e,t,n){let i=e+""+t,r=cf.get(s);i!=r&&(cf.set(s,i),s.style.height=t+"px",s.style.width=e+"px",s.style.marginLeft=n?-e/2+"px":0,s.style.marginTop=n?-t/2+"px":0)}const td={passive:!0},TS={...td,capture:!0};function Zs(s,e,t,n){e.addEventListener(s,t,n?TS:td)}function Ah(s,e,t,n){e.removeEventListener(s,t,td)}pa&&Eh();function pi(s,e,t,n){let i;t=t||0,n=n||e.length-1;let r=n<=2147483647;for(;n-t>1;)i=r?t+n>>1:jn((t+n)/2),e[i]<s?t=i:n=i;return s-e[t]<=e[n]-s?t:n}function Np(s){return(t,n,i)=>{let r=-1,a=-1;for(let o=n;o<=i;o++)if(s(t[o])){r=o;break}for(let o=i;o>=n;o--)if(s(t[o])){a=o;break}return[r,a]}}const Fp=s=>s!=null,Op=s=>s!=null&&s>0,Sl=Np(Fp),AS=Np(Op);function CS(s,e,t,n=0,i=!1){let r=i?AS:Sl,a=i?Op:Fp;[e,t]=r(s,e,t);let o=s[e],l=s[e];if(e>-1)if(n==1)o=s[e],l=s[t];else if(n==-1)o=s[t],l=s[e];else for(let c=e;c<=t;c++){let h=s[c];a(h)&&(h<o?o=h:h>l&&(l=h))}return[o??Ct,l??-Ct]}function Ml(s,e,t,n){let i=ff(s),r=ff(e);s==e&&(i==-1?(s*=t,e/=t):(s/=t,e*=t));let a=t==10?ns:kp,o=i==1?jn:ni,l=r==1?ni:jn,c=o(a(sn(s))),h=l(a(sn(e))),d=ra(t,c),u=ra(t,h);return t==10&&(c<0&&(d=Rt(d,-c)),h<0&&(u=Rt(u,-h))),n||t==2?(s=d*i,e=u*r):(s=Vp(s,d),e=wl(e,u)),[s,e]}function nd(s,e,t,n){let i=Ml(s,e,t,n);return s==0&&(i[0]=0),e==0&&(i[1]=0),i}const id=.1,df={mode:3,pad:id},Xa={pad:0,soft:null,mode:0},RS={min:Xa,max:Xa};function gl(s,e,t,n){return El(t)?uf(s,e,t):(Xa.pad=t,Xa.soft=n?0:null,Xa.mode=n?3:0,uf(s,e,RS))}function _t(s,e){return s??e}function PS(s,e,t){for(e=_t(e,0),t=_t(t,s.length-1);e<=t;){if(s[e]!=null)return!0;e++}return!1}function uf(s,e,t){let n=t.min,i=t.max,r=_t(n.pad,0),a=_t(i.pad,0),o=_t(n.hard,-Ct),l=_t(i.hard,Ct),c=_t(n.soft,Ct),h=_t(i.soft,-Ct),d=_t(n.mode,0),u=_t(i.mode,0),f=e-s,g=ns(f),x=Fn(sn(s),sn(e)),p=ns(x),m=sn(p-g);(f<1e-24||m>10)&&(f=0,(s==0||e==0)&&(f=1e-24,d==2&&c!=Ct&&(r=0),u==2&&h!=-Ct&&(a=0)));let b=f||x||1e3,_=ns(b),S=ra(10,jn(_)),I=b*(f==0?s==0?.1:1:r),A=Rt(Vp(s-I,S/10),24),R=s>=c&&(d==1||d==3&&A<=c||d==2&&A>=c)?c:Ct,N=Fn(o,A<R&&s>=R?R:xi(R,A)),M=b*(f==0?e==0?.1:1:a),y=Rt(wl(e+M,S/10),24),P=e<=h&&(u==1||u==3&&y>=h||u==2&&y<=h)?h:-Ct,X=xi(l,y>P&&e<=P?P:Fn(P,y));return N==X&&N==0&&(X=100),[N,X]}const LS=new Intl.NumberFormat(pa?ES.language:"en-US"),sd=s=>LS.format(s),Jn=Math,sl=Jn.PI,sn=Jn.abs,jn=Jn.floor,nn=Jn.round,ni=Jn.ceil,xi=Jn.min,Fn=Jn.max,ra=Jn.pow,ff=Jn.sign,ns=Jn.log10,kp=Jn.log2,DS=(s,e=1)=>Jn.sinh(s)*e,Lc=(s,e=1)=>Jn.asinh(s/e),Ct=1/0;function pf(s){return(ns((s^s>>31)-(s>>31))|0)+1}function Ch(s,e,t){return xi(Fn(s,e),t)}function Bp(s){return typeof s=="function"}function ft(s){return Bp(s)?s:()=>s}const IS=()=>{},zp=s=>s,Hp=(s,e)=>e,US=s=>null,mf=s=>!0,gf=(s,e)=>s==e,NS=/\.\d*?(?=9{6,}|0{6,})/gm,nr=s=>{if(Wp(s)||As.has(s))return s;const e=`${s}`,t=e.match(NS);if(t==null)return s;let n=t[0].length-1;if(e.indexOf("e-")!=-1){let[i,r]=e.split("e");return+`${nr(i)}e${r}`}return Rt(s,n)};function Ws(s,e){return nr(Rt(nr(s/e))*e)}function wl(s,e){return nr(ni(nr(s/e))*e)}function Vp(s,e){return nr(jn(nr(s/e))*e)}function Rt(s,e=0){if(Wp(s))return s;let t=10**e,n=s*t*(1+Number.EPSILON);return nn(n)/t}const As=new Map;function Gp(s){return((""+s).split(".")[1]||"").length}function Qa(s,e,t,n){let i=[],r=n.map(Gp);for(let a=e;a<t;a++){let o=sn(a),l=Rt(ra(s,a),o);for(let c=0;c<n.length;c++){let h=s==10?+`${n[c]}e${a}`:n[c]*l,d=(a>=0?0:o)+(a>=r[c]?0:r[c]),u=s==10?h:Rt(h,d);i.push(u),As.set(u,d)}}return i}const Ya={},rd=[],aa=[null,null],_s=Array.isArray,Wp=Number.isInteger,FS=s=>s===void 0;function xf(s){return typeof s=="string"}function El(s){let e=!1;if(s!=null){let t=s.constructor;e=t==null||t==Object}return e}function OS(s){return s!=null&&typeof s=="object"}const kS=Object.getPrototypeOf(Uint8Array),$p="__proto__";function oa(s,e=El){let t;if(_s(s)){let n=s.find(i=>i!=null);if(_s(n)||e(n)){t=Array(s.length);for(let i=0;i<s.length;i++)t[i]=oa(s[i],e)}else t=s.slice()}else if(s instanceof kS)t=s.slice();else if(e(s)){t={};for(let n in s)n!=$p&&(t[n]=oa(s[n],e))}else t=s;return t}function en(s){let e=arguments;for(let t=1;t<e.length;t++){let n=e[t];for(let i in n)i!=$p&&(El(s[i])?en(s[i],oa(n[i])):s[i]=oa(n[i]))}return s}const BS=0,zS=1,HS=2;function VS(s,e,t){for(let n=0,i,r=-1;n<e.length;n++){let a=e[n];if(a>r){for(i=a-1;i>=0&&s[i]==null;)s[i--]=null;for(i=a+1;i<t&&s[i]==null;)s[r=i++]=null}}}function GS(s,e){if(qS(s)){let a=s[0].slice();for(let o=1;o<s.length;o++)a.push(...s[o].slice(1));return XS(a[0])||(a=$S(a)),a}let t=new Set;for(let a=0;a<s.length;a++){let l=s[a][0],c=l.length;for(let h=0;h<c;h++)t.add(l[h])}let n=[Array.from(t).sort((a,o)=>a-o)],i=n[0].length,r=new Map;for(let a=0;a<i;a++)r.set(n[0][a],a);for(let a=0;a<s.length;a++){let o=s[a],l=o[0];for(let c=1;c<o.length;c++){let h=o[c],d=Array(i).fill(void 0),u=e?e[a][c]:zS,f=[];for(let g=0;g<h.length;g++){let x=h[g],p=r.get(l[g]);x===null?u!=BS&&(d[p]=x,u==HS&&f.push(p)):d[p]=x}VS(d,f,i),n.push(d)}}return n}const WS=typeof queueMicrotask>"u"?s=>Promise.resolve().then(s):queueMicrotask;function $S(s){let e=s[0],t=e.length,n=Array(t);for(let r=0;r<n.length;r++)n[r]=r;n.sort((r,a)=>e[r]-e[a]);let i=[];for(let r=0;r<s.length;r++){let a=s[r],o=Array(t);for(let l=0;l<t;l++)o[l]=a[n[l]];i.push(o)}return i}function qS(s){let e=s[0][0],t=e.length;for(let n=1;n<s.length;n++){let i=s[n][0];if(i.length!=t)return!1;if(i!=e){for(let r=0;r<t;r++)if(i[r]!=e[r])return!1}}return!0}function XS(s,e=100){const t=s.length;if(t<=1)return!0;let n=0,i=t-1;for(;n<=i&&s[n]==null;)n++;for(;i>=n&&s[i]==null;)i--;if(i<=n)return!0;const r=Fn(1,jn((i-n+1)/e));for(let a=s[n],o=n+r;o<=i;o+=r){const l=s[o];if(l!=null){if(l<=a)return!1;a=l}}return!0}const qp=["January","February","March","April","May","June","July","August","September","October","November","December"],Xp=["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];function Yp(s){return s.slice(0,3)}const YS=Xp.map(Yp),jS=qp.map(Yp),KS={MMMM:qp,MMM:jS,WWWW:Xp,WWW:YS};function Fa(s){return(s<10?"0":"")+s}function JS(s){return(s<10?"00":s<100?"0":"")+s}const ZS={YYYY:s=>s.getFullYear(),YY:s=>(s.getFullYear()+"").slice(2),MMMM:(s,e)=>e.MMMM[s.getMonth()],MMM:(s,e)=>e.MMM[s.getMonth()],MM:s=>Fa(s.getMonth()+1),M:s=>s.getMonth()+1,DD:s=>Fa(s.getDate()),D:s=>s.getDate(),WWWW:(s,e)=>e.WWWW[s.getDay()],WWW:(s,e)=>e.WWW[s.getDay()],HH:s=>Fa(s.getHours()),H:s=>s.getHours(),h:s=>{let e=s.getHours();return e==0?12:e>12?e-12:e},AA:s=>s.getHours()>=12?"PM":"AM",aa:s=>s.getHours()>=12?"pm":"am",a:s=>s.getHours()>=12?"p":"a",mm:s=>Fa(s.getMinutes()),m:s=>s.getMinutes(),ss:s=>Fa(s.getSeconds()),s:s=>s.getSeconds(),fff:s=>JS(s.getMilliseconds())};function ad(s,e){e=e||KS;let t=[],n=/\{([a-z]+)\}|[^{]+/gi,i;for(;i=n.exec(s);)t.push(i[0][0]=="{"?ZS[i[1]]:i[0]);return r=>{let a="";for(let o=0;o<t.length;o++)a+=typeof t[o]=="string"?t[o]:t[o](r,e);return a}}const QS=new Intl.DateTimeFormat().resolvedOptions().timeZone;function eM(s,e){let t;return e=="UTC"||e=="Etc/UTC"?t=new Date(+s+s.getTimezoneOffset()*6e4):e==QS?t=s:(t=new Date(s.toLocaleString("en-US",{timeZone:e})),t.setMilliseconds(s.getMilliseconds())),t}const jp=s=>s%1==0,xl=[1,2,2.5,5],tM=Qa(10,-32,0,xl),Kp=Qa(10,0,32,xl),nM=Kp.filter(jp),$s=tM.concat(Kp),od=`
`,Jp="{YYYY}",vf=od+Jp,Zp="{M}/{D}",Ga=od+Zp,jo=Ga+"/{YY}",Qp="{aa}",iM="{h}:{mm}",Vr=iM+Qp,_f=od+Vr,yf=":{ss}",St=null;function em(s){let e=s*1e3,t=e*60,n=t*60,i=n*24,r=i*30,a=i*365,l=(s==1?Qa(10,0,3,xl).filter(jp):Qa(10,-3,0,xl)).concat([e,e*5,e*10,e*15,e*30,t,t*5,t*10,t*15,t*30,n,n*2,n*3,n*4,n*6,n*8,n*12,i,i*2,i*3,i*4,i*5,i*6,i*7,i*8,i*9,i*10,i*15,r,r*2,r*3,r*4,r*6,a,a*2,a*5,a*10,a*25,a*50,a*100]);const c=[[a,Jp,St,St,St,St,St,St,1],[i*28,"{MMM}",vf,St,St,St,St,St,1],[i,Zp,vf,St,St,St,St,St,1],[n,"{h}"+Qp,jo,St,Ga,St,St,St,1],[t,Vr,jo,St,Ga,St,St,St,1],[e,yf,jo+" "+Vr,St,Ga+" "+Vr,St,_f,St,1],[s,yf+".{fff}",jo+" "+Vr,St,Ga+" "+Vr,St,_f,St,1]];function h(d){return(u,f,g,x,p,m)=>{let b=[],_=p>=a,S=p>=r&&p<a,I=d(g),A=Rt(I*s,3),R=Dc(I.getFullYear(),_?0:I.getMonth(),S||_?1:I.getDate()),N=Rt(R*s,3);if(S||_){let M=S?p/r:0,y=_?p/a:0,P=A==N?A:Rt(Dc(R.getFullYear()+y,R.getMonth()+M,1)*s,3),X=new Date(nn(P/s)),H=X.getFullYear(),J=X.getMonth();for(let q=0;P<=x;q++){let ee=Dc(H+y*q,J+M*q,1),j=ee-d(Rt(ee*s,3));P=Rt((+ee+j)*s,3),P<=x&&b.push(P)}}else{let M=p>=i?i:p,y=jn(g)-jn(A),P=N+y+wl(A-N,M);b.push(P);let X=d(P),H=X.getHours()+X.getMinutes()/t+X.getSeconds()/n,J=p/n,q=u.axes[f]._space,ee=m/q;for(;P=Rt(P+p,s==1?0:3),!(P>x);)if(J>1){let j=jn(Rt(H+J,6))%24,ue=d(P).getHours()-j;ue>1&&(ue=-1),P-=ue*n,H=(H+J)%24;let ye=b[b.length-1];Rt((P-ye)/p,3)*ee>=.7&&b.push(P)}else b.push(P)}return b}}return[l,c,h]}const[sM,rM,aM]=em(1),[oM,lM,cM]=em(.001);Qa(2,-53,53,[1]);function bf(s,e){return s.map(t=>t.map((n,i)=>i==0||i==8||n==null?n:e(i==1||t[8]==0?n:t[1]+n)))}function Sf(s,e){return(t,n,i,r,a)=>{let o=e.find(g=>a>=g[0])||e[e.length-1],l,c,h,d,u,f;return n.map(g=>{let x=s(g),p=x.getFullYear(),m=x.getMonth(),b=x.getDate(),_=x.getHours(),S=x.getMinutes(),I=x.getSeconds(),A=p!=l&&o[2]||m!=c&&o[3]||b!=h&&o[4]||_!=d&&o[5]||S!=u&&o[6]||I!=f&&o[7]||o[1];return l=p,c=m,h=b,d=_,u=S,f=I,A(x)})}}function hM(s,e){let t=ad(e);return(n,i,r,a,o)=>i.map(l=>t(s(l)))}function Dc(s,e,t){return new Date(s,e,t)}function Mf(s,e){return e(s)}const dM="{YYYY}-{MM}-{DD} {h}:{mm}{aa}";function wf(s,e){return(t,n,i,r)=>r==null?ed:e(s(n))}function uM(s,e){let t=s.series[e];return t.width?t.stroke(s,e):t.points.width?t.points.stroke(s,e):null}function fM(s,e){return s.series[e].fill(s,e)}const pM={show:!0,live:!0,isolate:!1,mount:IS,markers:{show:!0,width:2,stroke:uM,fill:fM,dash:"solid"},idx:null,idxs:null,values:[]};function mM(s,e){let t=s.cursor.points,n=ti(),i=t.size(s,e);Ot(n,Ha,i),Ot(n,Va,i);let r=i/-2;Ot(n,"marginLeft",r),Ot(n,"marginTop",r);let a=t.width(s,e,i);return a&&Ot(n,"borderWidth",a),n}function gM(s,e){let t=s.series[e].points;return t._fill||t._stroke}function xM(s,e){let t=s.series[e].points;return t._stroke||t._fill}function vM(s,e){return s.series[e].points.size}const Ic=[0,0];function _M(s,e,t){return Ic[0]=e,Ic[1]=t,Ic}function Ko(s,e,t,n=!0){return i=>{i.button==0&&(!n||i.target==e)&&t(i)}}function Uc(s,e,t,n=!0){return i=>{(!n||i.target==e)&&t(i)}}const yM={show:!0,x:!0,y:!0,lock:!1,move:_M,points:{one:!1,show:mM,size:vM,width:0,stroke:xM,fill:gM},bind:{mousedown:Ko,mouseup:Ko,click:Ko,dblclick:Ko,mousemove:Uc,mouseleave:Uc,mouseenter:Uc},drag:{setScale:!0,x:!0,y:!1,dist:0,uni:null,click:(s,e)=>{e.stopPropagation(),e.stopImmediatePropagation()},_x:!1,_y:!1},focus:{dist:(s,e,t,n,i)=>n-i,prox:-1,bias:0},hover:{skip:[void 0],prox:null,bias:0},left:-10,top:-10,idx:null,dataIdx:null,idxs:null,event:null},tm={show:!0,stroke:"rgba(0,0,0,0.07)",width:2},ld=en({},tm,{filter:Hp}),nm=en({},ld,{size:10}),im=en({},tm,{show:!1}),cd='12px system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji"',sm="bold "+cd,rm=1.5,Ef={show:!0,scale:"x",stroke:Qh,space:50,gap:5,alignTo:1,size:50,labelGap:0,labelSize:30,labelFont:sm,side:2,grid:ld,ticks:nm,border:im,font:cd,lineGap:rm,rotate:0},bM="Value",SM="Time",Tf={show:!0,scale:"x",auto:!1,sorted:1,min:Ct,max:-Ct,idxs:[]};function MM(s,e,t,n,i){return e.map(r=>r==null?"":sd(r))}function wM(s,e,t,n,i,r,a){let o=[],l=As.get(i)||0;t=a?t:Rt(wl(t,i),l);for(let c=t;c<=n;c=Rt(c+i,l))o.push(Object.is(c,-0)?0:c);return o}function Rh(s,e,t,n,i,r,a){const o=[],l=s.scales[s.axes[e].scale].log,c=l==10?ns:kp,h=jn(c(t));i=ra(l,h),l==10&&(i=$s[pi(i,$s)]);let d=t,u=i*l;l==10&&(u=$s[pi(u,$s)]);do o.push(d),d=d+i,l==10&&!As.has(d)&&(d=Rt(d,As.get(i))),d>=u&&(i=d,u=i*l,l==10&&(u=$s[pi(u,$s)]));while(d<=n);return o}function EM(s,e,t,n,i,r,a){let l=s.scales[s.axes[e].scale].asinh,c=n>l?Rh(s,e,Fn(l,t),n,i):[l],h=n>=0&&t<=0?[0]:[];return(t<-l?Rh(s,e,Fn(l,-n),-t,i):[l]).reverse().map(u=>-u).concat(h,c)}const am=/./,TM=/[12357]/,AM=/[125]/,Af=/1/,Ph=(s,e,t,n)=>s.map((i,r)=>e==4&&i==0||r%n==0&&t.test(i.toExponential()[i<0?1:0])?i:null);function CM(s,e,t,n,i){let r=s.axes[t],a=r.scale,o=s.scales[a],l=s.valToPos,c=r._space,h=l(10,a),d=l(9,a)-h>=c?am:l(7,a)-h>=c?TM:l(5,a)-h>=c?AM:Af;if(d==Af){let u=sn(l(1,a)-h);if(u<c)return Ph(e.slice().reverse(),o.distr,d,ni(c/u)).reverse()}return Ph(e,o.distr,d,1)}function RM(s,e,t,n,i){let r=s.axes[t],a=r.scale,o=r._space,l=s.valToPos,c=sn(l(1,a)-l(2,a));return c<o?Ph(e.slice().reverse(),3,am,ni(o/c)).reverse():e}function PM(s,e,t,n){return n==null?ed:e==null?"":sd(e)}const Cf={show:!0,scale:"y",stroke:Qh,space:30,gap:5,alignTo:1,size:50,labelGap:0,labelSize:30,labelFont:sm,side:3,grid:ld,ticks:nm,border:im,font:cd,lineGap:rm,rotate:0};function LM(s,e){let t=3+(s||1)*2;return Rt(t*e,3)}function DM(s,e){let{scale:t,idxs:n}=s.series[0],i=s._data[0],r=s.valToPos(i[n[0]],t,!0),a=s.valToPos(i[n[1]],t,!0),o=sn(a-r),l=s.series[e],c=o/(l.points.space*bt);return n[1]-n[0]<=c}const Rf={scale:null,auto:!0,sorted:0,min:Ct,max:-Ct},om=(s,e,t,n,i)=>i,Pf={show:!0,auto:!0,sorted:0,gaps:om,alpha:1,facets:[en({},Rf,{scale:"x"}),en({},Rf,{scale:"y"})]},Lf={scale:"y",auto:!0,sorted:0,show:!0,spanGaps:!1,gaps:om,alpha:1,points:{show:DM,filter:null},values:null,min:Ct,max:-Ct,idxs:[],path:null,clip:null};function IM(s,e,t,n,i){return t/10}const lm={time:sS,auto:!0,distr:1,log:10,asinh:1,min:null,max:null,dir:1,ori:0},UM=en({},lm,{time:!1,ori:1}),Df={};function cm(s,e){let t=Df[s];return t||(t={key:s,plots:[],sub(n){t.plots.push(n)},unsub(n){t.plots=t.plots.filter(i=>i!=n)},pub(n,i,r,a,o,l,c){for(let h=0;h<t.plots.length;h++)t.plots[h]!=i&&t.plots[h].pub(n,i,r,a,o,l,c)}},s!=null&&(Df[s]=t)),t}const la=1,Lh=2;function sr(s,e,t){const n=s.mode,i=s.series[e],r=n==2?s._data[e]:s._data,a=s.scales,o=s.bbox;let l=r[0],c=n==2?r[1]:r[e],h=n==2?a[i.facets[0].scale]:a[s.series[0].scale],d=n==2?a[i.facets[1].scale]:a[i.scale],u=o.left,f=o.top,g=o.width,x=o.height,p=s.valToPosH,m=s.valToPosV;return h.ori==0?t(i,l,c,h,d,p,m,u,f,g,x,Al,ma,Rl,dm,fm):t(i,l,c,h,d,m,p,f,u,x,g,Cl,ga,ud,um,pm)}function hd(s,e){let t=0,n=0,i=_t(s.bands,rd);for(let r=0;r<i.length;r++){let a=i[r];a.series[0]==e?t=a.dir:a.series[1]==e&&(a.dir==1?n|=1:n|=2)}return[t,n==1?-1:n==2?1:n==3?2:0]}function NM(s,e,t,n,i){let r=s.mode,a=s.series[e],o=r==2?a.facets[1].scale:a.scale,l=s.scales[o];return i==-1?l.min:i==1?l.max:l.distr==3?l.dir==1?l.min:l.max:0}function is(s,e,t,n,i,r){return sr(s,e,(a,o,l,c,h,d,u,f,g,x,p)=>{let m=a.pxRound;const b=c.dir*(c.ori==0?1:-1),_=c.ori==0?ma:ga;let S,I;b==1?(S=t,I=n):(S=n,I=t);let A=m(d(o[S],c,x,f)),R=m(u(l[S],h,p,g)),N=m(d(o[I],c,x,f)),M=m(u(r==1?h.max:h.min,h,p,g)),y=new Path2D(i);return _(y,N,M),_(y,A,M),_(y,A,R),y})}function Tl(s,e,t,n,i,r){let a=null;if(s.length>0){a=new Path2D;const o=e==0?Rl:ud;let l=t;for(let d=0;d<s.length;d++){let u=s[d];if(u[1]>u[0]){let f=u[0]-l;f>0&&o(a,l,n,f,n+r),l=u[1]}}let c=t+i-l,h=10;c>0&&o(a,l,n-h/2,c,n+r+h)}return a}function FM(s,e,t){let n=s[s.length-1];n&&n[0]==e?n[1]=t:s.push([e,t])}function dd(s,e,t,n,i,r,a){let o=[],l=s.length;for(let c=i==1?t:n;c>=t&&c<=n;c+=i)if(e[c]===null){let d=c,u=c;if(i==1)for(;++c<=n&&e[c]===null;)u=c;else for(;--c>=t&&e[c]===null;)u=c;let f=r(s[d]),g=u==d?f:r(s[u]),x=d-i;f=a<=0&&x>=0&&x<l?r(s[x]):f;let m=u+i;g=a>=0&&m>=0&&m<l?r(s[m]):g,g>=f&&o.push([f,g])}return o}function If(s){return s==0?zp:s==1?nn:e=>Ws(e,s)}function hm(s){let e=s==0?Al:Cl,t=s==0?(i,r,a,o,l,c)=>{i.arcTo(r,a,o,l,c)}:(i,r,a,o,l,c)=>{i.arcTo(a,r,l,o,c)},n=s==0?(i,r,a,o,l)=>{i.rect(r,a,o,l)}:(i,r,a,o,l)=>{i.rect(a,r,l,o)};return(i,r,a,o,l,c=0,h=0)=>{c==0&&h==0?n(i,r,a,o,l):(c=xi(c,o/2,l/2),h=xi(h,o/2,l/2),e(i,r+c,a),t(i,r+o,a,r+o,a+l,c),t(i,r+o,a+l,r,a+l,h),t(i,r,a+l,r,a,h),t(i,r,a,r+o,a,c),i.closePath())}}const Al=(s,e,t)=>{s.moveTo(e,t)},Cl=(s,e,t)=>{s.moveTo(t,e)},ma=(s,e,t)=>{s.lineTo(e,t)},ga=(s,e,t)=>{s.lineTo(t,e)},Rl=hm(0),ud=hm(1),dm=(s,e,t,n,i,r)=>{s.arc(e,t,n,i,r)},um=(s,e,t,n,i,r)=>{s.arc(t,e,n,i,r)},fm=(s,e,t,n,i,r,a)=>{s.bezierCurveTo(e,t,n,i,r,a)},pm=(s,e,t,n,i,r,a)=>{s.bezierCurveTo(t,e,i,n,a,r)};function mm(s){return(e,t,n,i,r)=>sr(e,t,(a,o,l,c,h,d,u,f,g,x,p)=>{let{pxRound:m,points:b}=a,_,S;c.ori==0?(_=Al,S=dm):(_=Cl,S=um);const I=Rt(b.width*bt,3);let A=(b.size-b.width)/2*bt,R=Rt(A*2,3),N=new Path2D,M=new Path2D,{left:y,top:P,width:X,height:H}=e.bbox;Rl(M,y-R,P-R,X+R*2,H+R*2);const J=q=>{if(l[q]!=null){let ee=m(d(o[q],c,x,f)),j=m(u(l[q],h,p,g));_(N,ee+A,j),S(N,ee,j,A,0,sl*2)}};if(r)r.forEach(J);else for(let q=n;q<=i;q++)J(q);return{stroke:I>0?N:null,fill:N,clip:M,flags:la|Lh}})}function gm(s){return(e,t,n,i,r,a)=>{n!=i&&(r!=n&&a!=n&&s(e,t,n),r!=i&&a!=i&&s(e,t,i),s(e,t,a))}}const OM=gm(ma),kM=gm(ga);function xm(s){const e=_t(s==null?void 0:s.alignGaps,0);return(t,n,i,r)=>sr(t,n,(a,o,l,c,h,d,u,f,g,x,p)=>{[i,r]=Sl(l,i,r);let m=a.pxRound,b=H=>m(d(H,c,x,f)),_=H=>m(u(H,h,p,g)),S,I;c.ori==0?(S=ma,I=OM):(S=ga,I=kM);const A=c.dir*(c.ori==0?1:-1),R={stroke:new Path2D,fill:null,clip:null,band:null,gaps:null,flags:la},N=R.stroke;let M=!1;if(r-i>=x*4){let H=be=>t.posToVal(be,c.key,!0),J=null,q=null,ee,j,ne,ge=b(o[A==1?i:r]),ue=b(o[i]),ye=b(o[r]),Te=H(A==1?ue+1:ye-1);for(let be=A==1?i:r;be>=i&&be<=r;be+=A){let ie=o[be],Se=(A==1?ie<Te:ie>Te)?ge:b(ie),fe=l[be];Se==ge?fe!=null?(j=fe,J==null?(S(N,Se,_(j)),ee=J=q=j):j<J?J=j:j>q&&(q=j)):fe===null&&(M=!0):(J!=null&&I(N,ge,_(J),_(q),_(ee),_(j)),fe!=null?(j=fe,S(N,Se,_(j)),J=q=ee=j):(J=q=null,fe===null&&(M=!0)),ge=Se,Te=H(ge+A))}J!=null&&J!=q&&ne!=ge&&I(N,ge,_(J),_(q),_(ee),_(j))}else for(let H=A==1?i:r;H>=i&&H<=r;H+=A){let J=l[H];J===null?M=!0:J!=null&&S(N,b(o[H]),_(J))}let[P,X]=hd(t,n);if(a.fill!=null||P!=0){let H=R.fill=new Path2D(N),J=a.fillTo(t,n,a.min,a.max,P),q=_(J),ee=b(o[i]),j=b(o[r]);A==-1&&([j,ee]=[ee,j]),S(H,j,q),S(H,ee,q)}if(!a.spanGaps){let H=[];M&&H.push(...dd(o,l,i,r,A,b,e)),R.gaps=H=a.gaps(t,n,i,r,H),R.clip=Tl(H,c.ori,f,g,x,p)}return X!=0&&(R.band=X==2?[is(t,n,i,r,N,-1),is(t,n,i,r,N,1)]:is(t,n,i,r,N,X)),R})}function BM(s){const e=_t(s.align,1),t=_t(s.ascDesc,!1),n=_t(s.alignGaps,0),i=_t(s.extend,!1);return(r,a,o,l)=>sr(r,a,(c,h,d,u,f,g,x,p,m,b,_)=>{[o,l]=Sl(d,o,l);let S=c.pxRound,{left:I,width:A}=r.bbox,R=ue=>S(g(ue,u,b,p)),N=ue=>S(x(ue,f,_,m)),M=u.ori==0?ma:ga;const y={stroke:new Path2D,fill:null,clip:null,band:null,gaps:null,flags:la},P=y.stroke,X=u.dir*(u.ori==0?1:-1);let H=N(d[X==1?o:l]),J=R(h[X==1?o:l]),q=J,ee=J;i&&e==-1&&(ee=I,M(P,ee,H)),M(P,J,H);for(let ue=X==1?o:l;ue>=o&&ue<=l;ue+=X){let ye=d[ue];if(ye==null)continue;let Te=R(h[ue]),be=N(ye);e==1?M(P,Te,H):M(P,q,be),M(P,Te,be),H=be,q=Te}let j=q;i&&e==1&&(j=I+A,M(P,j,H));let[ne,ge]=hd(r,a);if(c.fill!=null||ne!=0){let ue=y.fill=new Path2D(P),ye=c.fillTo(r,a,c.min,c.max,ne),Te=N(ye);M(ue,j,Te),M(ue,ee,Te)}if(!c.spanGaps){let ue=[];ue.push(...dd(h,d,o,l,X,R,n));let ye=c.width*bt/2,Te=t||e==1?ye:-ye,be=t||e==-1?-ye:ye;ue.forEach(ie=>{ie[0]+=Te,ie[1]+=be}),y.gaps=ue=c.gaps(r,a,o,l,ue),y.clip=Tl(ue,u.ori,p,m,b,_)}return ge!=0&&(y.band=ge==2?[is(r,a,o,l,P,-1),is(r,a,o,l,P,1)]:is(r,a,o,l,P,ge)),y})}function Uf(s,e,t,n,i,r,a=Ct){if(s.length>1){let o=null;for(let l=0,c=1/0;l<s.length;l++)if(e[l]!==void 0){if(o!=null){let h=sn(s[l]-s[o]);h<c&&(c=h,a=sn(t(s[l],n,i,r)-t(s[o],n,i,r)))}o=l}}return a}function zM(s){s=s||Ya;const e=_t(s.size,[.6,Ct,1]),t=s.align||0,n=s.gap||0;let i=s.radius;i=i==null?[0,0]:typeof i=="number"?[i,0]:i;const r=ft(i),a=1-e[0],o=_t(e[1],Ct),l=_t(e[2],1),c=_t(s.disp,Ya),h=_t(s.each,f=>{}),{fill:d,stroke:u}=c;return(f,g,x,p)=>sr(f,g,(m,b,_,S,I,A,R,N,M,y,P)=>{let X=m.pxRound,H=t,J=n*bt,q=o*bt,ee=l*bt,j,ne;S.ori==0?[j,ne]=r(f,g):[ne,j]=r(f,g);const ge=S.dir*(S.ori==0?1:-1);let ue=S.ori==0?Rl:ud,ye=S.ori==0?h:($,Ee,xe,Ce,Je,me,Ae)=>{h($,Ee,xe,Je,Ce,Ae,me)},Te=_t(f.bands,rd).find($=>$.series[0]==g),be=Te!=null?Te.dir:0,ie=m.fillTo(f,g,m.min,m.max,be),he=X(R(ie,I,P,M)),Se,fe,ze,We=y,Oe=X(m.width*bt),pt=!1,k=null,ut=null,st=null,ct=null;d!=null&&(Oe==0||u!=null)&&(pt=!0,k=d.values(f,g,x,p),ut=new Map,new Set(k).forEach($=>{$!=null&&ut.set($,new Path2D)}),Oe>0&&(st=u.values(f,g,x,p),ct=new Map,new Set(st).forEach($=>{$!=null&&ct.set($,new Path2D)})));let{x0:ke,size:wt}=c;if(ke!=null&&wt!=null){H=1,b=ke.values(f,g,x,p),ke.unit==2&&(b=b.map(xe=>f.posToVal(N+xe*y,S.key,!0)));let $=wt.values(f,g,x,p);wt.unit==2?fe=$[0]*y:fe=A($[0],S,y,N)-A(0,S,y,N),We=Uf(b,_,A,S,y,N,We),ze=We-fe+J}else We=Uf(b,_,A,S,y,N,We),ze=We*a+J,fe=We-ze;ze<1&&(ze=0),Oe>=fe/2&&(Oe=0),ze<5&&(X=zp);let Ye=ze>0,qe=We-ze-(Ye?Oe:0);fe=X(Ch(qe,ee,q)),Se=(H==0?fe/2:H==ge?0:fe)-H*ge*((H==0?J/2:0)+(Ye?Oe/2:0));const U={stroke:null,fill:null,clip:null,band:null,gaps:null,flags:0},E=pt?null:new Path2D;let Q=null;if(Te!=null)Q=f.data[Te.series[1]];else{let{y0:$,y1:Ee}=c;$!=null&&Ee!=null&&(_=Ee.values(f,g,x,p),Q=$.values(f,g,x,p))}let le=j*fe,te=ne*fe;for(let $=ge==1?x:p;$>=x&&$<=p;$+=ge){let Ee=_[$];if(Ee==null)continue;if(Q!=null){let we=Q[$]??0;if(Ee-we==0)continue;he=R(we,I,P,M)}let xe=S.distr!=2||c!=null?b[$]:$,Ce=A(xe,S,y,N),Je=R(_t(Ee,ie),I,P,M),me=X(Ce-Se),Ae=X(Fn(Je,he)),Ze=X(xi(Je,he)),He=Ae-Ze;if(Ee!=null){let we=Ee<0?te:le,Ve=Ee<0?le:te;pt?(Oe>0&&st[$]!=null&&ue(ct.get(st[$]),me,Ze+jn(Oe/2),fe,Fn(0,He-Oe),we,Ve),k[$]!=null&&ue(ut.get(k[$]),me,Ze+jn(Oe/2),fe,Fn(0,He-Oe),we,Ve)):ue(E,me,Ze+jn(Oe/2),fe,Fn(0,He-Oe),we,Ve),ye(f,g,$,me-Oe/2,Ze,fe+Oe,He)}}return Oe>0?U.stroke=pt?ct:E:pt||(U._fill=m.width==0?m._fill:m._stroke??m._fill,U.width=0),U.fill=pt?ut:E,U})}function HM(s,e){const t=_t(e==null?void 0:e.alignGaps,0);return(n,i,r,a)=>sr(n,i,(o,l,c,h,d,u,f,g,x,p,m)=>{[r,a]=Sl(c,r,a);let b=o.pxRound,_=j=>b(u(j,h,p,g)),S=j=>b(f(j,d,m,x)),I,A,R;h.ori==0?(I=Al,R=ma,A=fm):(I=Cl,R=ga,A=pm);const N=h.dir*(h.ori==0?1:-1);let M=_(l[N==1?r:a]),y=M,P=[],X=[];for(let j=N==1?r:a;j>=r&&j<=a;j+=N)if(c[j]!=null){let ge=l[j],ue=_(ge);P.push(y=ue),X.push(S(c[j]))}const H={stroke:s(P,X,I,R,A,b),fill:null,clip:null,band:null,gaps:null,flags:la},J=H.stroke;let[q,ee]=hd(n,i);if(o.fill!=null||q!=0){let j=H.fill=new Path2D(J),ne=o.fillTo(n,i,o.min,o.max,q),ge=S(ne);R(j,y,ge),R(j,M,ge)}if(!o.spanGaps){let j=[];j.push(...dd(l,c,r,a,N,_,t)),H.gaps=j=o.gaps(n,i,r,a,j),H.clip=Tl(j,h.ori,g,x,p,m)}return ee!=0&&(H.band=ee==2?[is(n,i,r,a,J,-1),is(n,i,r,a,J,1)]:is(n,i,r,a,J,ee)),H})}function VM(s){return HM(GM,s)}function GM(s,e,t,n,i,r){const a=s.length;if(a<2)return null;const o=new Path2D;if(t(o,s[0],e[0]),a==2)n(o,s[1],e[1]);else{let l=Array(a),c=Array(a-1),h=Array(a-1),d=Array(a-1);for(let u=0;u<a-1;u++)h[u]=e[u+1]-e[u],d[u]=s[u+1]-s[u],c[u]=h[u]/d[u];l[0]=c[0];for(let u=1;u<a-1;u++)c[u]===0||c[u-1]===0||c[u-1]>0!=c[u]>0?l[u]=0:(l[u]=3*(d[u-1]+d[u])/((2*d[u]+d[u-1])/c[u-1]+(d[u]+2*d[u-1])/c[u]),isFinite(l[u])||(l[u]=0));l[a-1]=c[a-2];for(let u=0;u<a-1;u++)i(o,s[u]+d[u]/3,e[u]+l[u]*d[u]/3,s[u+1]-d[u]/3,e[u+1]-l[u+1]*d[u]/3,s[u+1],e[u+1])}return o}const Dh=new Set;function Nf(){for(let s of Dh)s.syncRect(!0)}pa&&(Zs(MS,Jr,Nf),Zs(wS,Jr,Nf,!0),Zs(ml,Jr,()=>{gn.pxRatio=bt}));const WM=xm(),$M=mm();function Ff(s,e,t,n){return(n?[s[0],s[1]].concat(s.slice(2)):[s[0]].concat(s.slice(1))).map((r,a)=>Ih(r,a,e,t))}function qM(s,e){return s.map((t,n)=>n==0?{}:en({},e,t))}function Ih(s,e,t,n){return en({},e==0?t:n,s)}function vm(s,e,t){return e==null?aa:[e,t]}const XM=vm;function YM(s,e,t){return e==null?aa:gl(e,t,id,!0)}function _m(s,e,t,n){return e==null?aa:Ml(e,t,s.scales[n].log,!1)}const jM=_m;function ym(s,e,t,n){return e==null?aa:nd(e,t,s.scales[n].log,!1)}const KM=ym;function JM(s,e,t,n,i){let r=Fn(pf(s),pf(e)),a=e-s,o=pi(i/n*a,t);do{let l=t[o],c=n*l/a;if(c>=i&&r+(l<5?As.get(l):0)<=17)return[l,c]}while(++o<t.length);return[0,0]}function Of(s){let e,t;return s=s.replace(/(\d+)px/,(n,i)=>(e=nn((t=+i)*bt))+"px"),[s,e,t]}function ZM(s){s.show&&[s.font,s.labelFont].forEach(e=>{let t=Rt(e[2]*bt,1);e[0]=e[0].replace(/[0-9.]+px/,t+"px"),e[1]=t})}function gn(s,e,t){const n={mode:_t(s.mode,1)},i=n.mode;function r(v,w,L,D){let z=w.valToPct(v);return D+L*(w.dir==-1?1-z:z)}function a(v,w,L,D){let z=w.valToPct(v);return D+L*(w.dir==-1?z:1-z)}function o(v,w,L,D){return w.ori==0?r(v,w,L,D):a(v,w,L,D)}n.valToPosH=r,n.valToPosV=a;let l=!1;n.status=0;const c=n.root=ti(rS);if(s.id!=null&&(c.id=s.id),Xn(c,s.class),s.title){let v=ti(lS,c);v.textContent=s.title}const h=fi("canvas"),d=n.ctx=h.getContext("2d"),u=ti(cS,c);Zs("click",u,v=>{v.target===g&&(Ut!=hr||Vt!=dr)&&yn.click(n,v)},!0);const f=n.under=ti(hS,u);u.appendChild(h);const g=n.over=ti(dS,u);s=oa(s);const x=+_t(s.pxAlign,1),p=If(x);(s.plugins||[]).forEach(v=>{v.opts&&(s=v.opts(n,s)||s)});const m=s.ms||.001,b=n.series=i==1?Ff(s.series||[],Tf,Lf,!1):qM(s.series||[null],Pf),_=n.axes=Ff(s.axes||[],Ef,Cf,!0),S=n.scales={},I=n.bands=s.bands||[];I.forEach(v=>{v.fill=ft(v.fill||null),v.dir=_t(v.dir,-1)});const A=i==2?b[1].facets[0].scale:b[0].scale,R={axes:Im,series:kn},N=(s.drawOrder||["axes","series"]).map(v=>R[v]);function M(v){const w=v.distr==3?L=>ns(L>0?L:v.clamp(n,L,v.min,v.max,v.key)):v.distr==4?L=>Lc(L,v.asinh):v.distr==100?L=>v.fwd(L):L=>L;return L=>{let D=w(L),{_min:z,_max:K}=v,oe=K-z;return(D-z)/oe}}function y(v){let w=S[v];if(w==null){let L=(s.scales||Ya)[v]||Ya;if(L.from!=null){y(L.from);let D=en({},S[L.from],L,{key:v});D.valToPct=M(D),S[v]=D}else{w=S[v]=en({},v==A?lm:UM,L),w.key=v;let D=w.time,z=w.range,K=_s(z);if((v!=A||i==2&&!D)&&(K&&(z[0]==null||z[1]==null)&&(z={min:z[0]==null?df:{mode:1,hard:z[0],soft:z[0]},max:z[1]==null?df:{mode:1,hard:z[1],soft:z[1]}},K=!1),!K&&El(z))){let oe=z;z=(pe,Me,De)=>Me==null?aa:gl(Me,De,oe)}w.range=ft(z||(D?XM:v==A?w.distr==3?jM:w.distr==4?KM:vm:w.distr==3?_m:w.distr==4?ym:YM)),w.auto=ft(K?!1:w.auto),w.clamp=ft(w.clamp||IM),w._min=w._max=null,w.valToPct=M(w)}}}y("x"),y("y"),i==1&&b.forEach(v=>{y(v.scale)}),_.forEach(v=>{y(v.scale)});for(let v in s.scales)y(v);const P=S[A],X=P.distr;let H,J;P.ori==0?(Xn(c,aS),H=r,J=a):(Xn(c,oS),H=a,J=r);const q={};for(let v in S){let w=S[v];(w.min!=null||w.max!=null)&&(q[v]={min:w.min,max:w.max},w.min=w.max=null)}const ee=s.tzDate||(v=>new Date(nn(v/m))),j=s.fmtDate||ad,ne=m==1?aM(ee):cM(ee),ge=Sf(ee,bf(m==1?rM:lM,j)),ue=wf(ee,Mf(dM,j)),ye=[],Te=n.legend=en({},pM,s.legend),be=n.cursor=en({},yM,{drag:{y:i==2}},s.cursor),ie=Te.show,he=be.show,Se=Te.markers;Te.idxs=ye,Se.width=ft(Se.width),Se.dash=ft(Se.dash),Se.stroke=ft(Se.stroke),Se.fill=ft(Se.fill);let fe,ze,We,Oe=[],pt=[],k,ut=!1,st={};if(Te.live){const v=b[1]?b[1].values:null;ut=v!=null,k=ut?v(n,1,0):{_:0};for(let w in k)st[w]=ed}if(ie)if(fe=fi("table",xS,c),We=fi("tbody",null,fe),Te.mount(n,fe),ut){ze=fi("thead",null,fe,We);let v=fi("tr",null,ze);fi("th",null,v);for(var ct in k)fi("th",Ju,v).textContent=ct}else Xn(fe,_S),Te.live&&Xn(fe,vS);const ke={show:!0},wt={show:!1};function Ye(v,w){if(w==0&&(ut||!Te.live||i==2))return aa;let L=[],D=fi("tr",yS,We,We.childNodes[w]);Xn(D,v.class),v.show||Xn(D,Ys);let z=fi("th",null,D);if(Se.show){let pe=ti(bS,z);if(w>0){let Me=Se.width(n,w);Me&&(pe.style.border=Me+"px "+Se.dash(n,w)+" "+Se.stroke(n,w)),pe.style.background=Se.fill(n,w)}}let K=ti(Ju,z);v.label instanceof HTMLElement?K.appendChild(v.label):K.textContent=v.label,w>0&&(Se.show||(K.style.color=v.width>0?Se.stroke(n,w):Se.fill(n,w)),U("click",z,pe=>{if(be._lock)return;zt(pe);let Me=b.indexOf(v);if((pe.ctrlKey||pe.metaKey)!=Te.isolate){let De=b.some((Ie,Fe)=>Fe>0&&Fe!=Me&&Ie.show);b.forEach((Ie,Fe)=>{Fe>0&&Ai(Fe,De?Fe==Me?ke:wt:ke,!0,Zt.setSeries)})}else Ai(Me,{show:!v.show},!0,Zt.setSeries)},!1),Ei&&U(tf,z,pe=>{be._lock||(zt(pe),Ai(b.indexOf(v),fr,!0,Zt.setSeries))},!1));for(var oe in k){let pe=fi("td",SS,D);pe.textContent="--",L.push(pe)}return[D,L]}const qe=new Map;function U(v,w,L,D=!0){const z=qe.get(w)||{},K=be.bind[v](n,w,L,D);K&&(Zs(v,w,z[v]=K),qe.set(w,z))}function E(v,w,L){const D=qe.get(w)||{};for(let z in D)(v==null||z==v)&&(Ah(z,w,D[z]),delete D[z]);v==null&&qe.delete(w)}let Q=0,le=0,te=0,$=0,Ee=0,xe=0,Ce=Ee,Je=xe,me=te,Ae=$,Ze=0,He=0,we=0,Ve=0;n.bbox={};let B=!1,ce=!1,O=!1,ae=!1,se=!1,re=!1;function _e(v,w,L){(L||v!=n.width||w!=n.height)&&Ke(v,w),ar(!1),O=!0,ce=!0,or()}function Ke(v,w){n.width=Q=te=v,n.height=le=$=w,Ee=xe=0,lt(),vn();let L=n.bbox;Ze=L.left=Ws(Ee*bt,.5),He=L.top=Ws(xe*bt,.5),we=L.width=Ws(te*bt,.5),Ve=L.height=Ws($*bt,.5)}const ot=3;function xt(){let v=!1,w=0;for(;!v;){w++;let L=Lm(w),D=Dm(w);v=w==ot||L&&D,v||(Ke(n.width,n.height),ce=!0)}}function Et({width:v,height:w}){_e(v,w)}n.setSize=Et;function lt(){let v=!1,w=!1,L=!1,D=!1;_.forEach((z,K)=>{if(z.show&&z._show){let{side:oe,_size:pe}=z,Me=oe%2,De=z.label!=null?z.labelSize:0,Ie=pe+De;Ie>0&&(Me?(te-=Ie,oe==3?(Ee+=Ie,D=!0):L=!0):($-=Ie,oe==0?(xe+=Ie,v=!0):w=!0))}}),zi[0]=v,zi[1]=L,zi[2]=w,zi[3]=D,te-=Z[1]+Z[3],Ee+=Z[3],$-=Z[2]+Z[0],xe+=Z[0]}function vn(){let v=Ee+te,w=xe+$,L=Ee,D=xe;function z(K,oe){switch(K){case 1:return v+=oe,v-oe;case 2:return w+=oe,w-oe;case 3:return L-=oe,L+oe;case 0:return D-=oe,D+oe}}_.forEach((K,oe)=>{if(K.show&&K._show){let pe=K.side;K._pos=z(pe,K._size),K.label!=null&&(K._lpos=z(pe,K.labelSize))}})}if(be.dataIdx==null){let v=be.hover,w=v.skip=new Set(v.skip??[]);w.add(void 0);let L=v.prox=ft(v.prox),D=v.bias??(v.bias=0);be.dataIdx=(z,K,oe,pe)=>{if(K==0)return oe;let Me=oe,De=L(z,K,oe,pe)??Ct,Ie=De>=0&&De<Ct,Fe=P.ori==0?te:$,it=be.left,yt=e[0],vt=e[K];if(w.has(vt[oe])){Me=null;let dt=null,tt=null,$e;if(D==0||D==-1)for($e=oe;dt==null&&$e-- >0;)w.has(vt[$e])||(dt=$e);if(D==0||D==1)for($e=oe;tt==null&&$e++<vt.length;)w.has(vt[$e])||(tt=$e);if(dt!=null||tt!=null)if(Ie){let Ft=dt==null?-1/0:H(yt[dt],P,Fe,0),$t=tt==null?1/0:H(yt[tt],P,Fe,0),fn=it-Ft,At=$t-it;fn<=At?fn<=De&&(Me=dt):At<=De&&(Me=tt)}else Me=tt==null?dt:dt==null?tt:oe-dt<=tt-oe?dt:tt}else Ie&&sn(it-H(yt[oe],P,Fe,0))>De&&(Me=null);return Me}}const zt=v=>{be.event=v};be.idxs=ye,be._lock=!1;let Ht=be.points;Ht.show=ft(Ht.show),Ht.size=ft(Ht.size),Ht.stroke=ft(Ht.stroke),Ht.width=ft(Ht.width),Ht.fill=ft(Ht.fill);const cn=n.focus=en({},s.focus||{alpha:.3},be.focus),Ei=cn.prox>=0,ki=Ei&&Ht.one;let Rn=[],oi=[],Bi=[];function Ds(v,w){let L=Ht.show(n,w);if(L instanceof HTMLElement)return Xn(L,gS),Xn(L,v.class),Li(L,-10,-10,te,$),g.insertBefore(L,Rn[w]),L}function _a(v,w){if(i==1||w>0){let L=i==1&&S[v.scale].time,D=v.value;v.value=L?xf(D)?wf(ee,Mf(D,j)):D||ue:D||PM,v.label=v.label||(L?SM:bM)}if(ki||w>0){v.width=v.width==null?1:v.width,v.paths=v.paths||WM||US,v.fillTo=ft(v.fillTo||NM),v.pxAlign=+_t(v.pxAlign,x),v.pxRound=If(v.pxAlign),v.stroke=ft(v.stroke||null),v.fill=ft(v.fill||null),v._stroke=v._fill=v._paths=v._focus=null;let L=LM(Fn(1,v.width),1),D=v.points=en({},{size:L,width:Fn(1,L*.2),stroke:v.stroke,space:L*2,paths:$M,_stroke:null,_fill:null},v.points);D.show=ft(D.show),D.filter=ft(D.filter),D.fill=ft(D.fill),D.stroke=ft(D.stroke),D.paths=ft(D.paths),D.pxAlign=v.pxAlign}if(ie){let L=Ye(v,w);Oe.splice(w,0,L[0]),pt.splice(w,0,L[1]),Te.values.push(null)}if(he){ye.splice(w,0,null);let L=null;ki?w==0&&(L=Ds(v,w)):w>0&&(L=Ds(v,w)),Rn.splice(w,0,L),oi.splice(w,0,0),Bi.splice(w,0,0)}un("addSeries",w)}function ao(v,w){w=w??b.length,v=i==1?Ih(v,w,Tf,Lf):Ih(v,w,{},Pf),b.splice(w,0,v),_a(b[w],w)}n.addSeries=ao;function Ol(v){if(b.splice(v,1),ie){Te.values.splice(v,1),pt.splice(v,1);let w=Oe.splice(v,1)[0];E(null,w.firstChild),w.remove()}he&&(ye.splice(v,1),Rn.splice(v,1)[0].remove(),oi.splice(v,1),Bi.splice(v,1)),un("delSeries",v)}n.delSeries=Ol;const zi=[!1,!1,!1,!1];function kl(v,w){if(v._show=v.show,v.show){let L=v.side%2,D=S[v.scale];D==null&&(v.scale=L?b[1].scale:A,D=S[v.scale]);let z=D.time;v.size=ft(v.size),v.space=ft(v.space),v.rotate=ft(v.rotate),_s(v.incrs)&&v.incrs.forEach(oe=>{!As.has(oe)&&As.set(oe,Gp(oe))}),v.incrs=ft(v.incrs||(D.distr==2?nM:z?m==1?sM:oM:$s)),v.splits=ft(v.splits||(z&&D.distr==1?ne:D.distr==3?Rh:D.distr==4?EM:wM)),v.stroke=ft(v.stroke),v.grid.stroke=ft(v.grid.stroke),v.ticks.stroke=ft(v.ticks.stroke),v.border.stroke=ft(v.border.stroke);let K=v.values;v.values=_s(K)&&!_s(K[0])?ft(K):z?_s(K)?Sf(ee,bf(K,j)):xf(K)?hM(ee,K):K||ge:K||MM,v.filter=ft(v.filter||(D.distr>=3&&D.log==10?CM:D.distr==3&&D.log==2?RM:Hp)),v.font=Of(v.font),v.labelFont=Of(v.labelFont),v._size=v.size(n,null,w,0),v._space=v._rotate=v._incrs=v._found=v._splits=v._values=null,v._size>0&&(zi[w]=!0,v._el=ti(uS,u))}}function C(v,w,L,D){let[z,K,oe,pe]=L,Me=w%2,De=0;return Me==0&&(pe||K)&&(De=w==0&&!z||w==2&&!oe?nn(Ef.size/3):0),Me==1&&(z||oe)&&(De=w==1&&!K||w==3&&!pe?nn(Cf.size/2):0),De}const W=n.padding=(s.padding||[C,C,C,C]).map(v=>ft(_t(v,C))),Z=n._padding=W.map((v,w)=>v(n,w,zi,0));let Y,G=null,de=null;const Pe=i==1?b[0].idxs:null;let Le=null,Ne=!1;function Qe(v,w){if(e=v??[],n.data=n._data=e,i==2){Y=0;for(let L=1;L<b.length;L++)Y+=e[L][0].length}else{e.length==0&&(n.data=n._data=e=[[]]),Le=e[0],Y=Le.length;let L=e;if(X==2){L=e.slice();let D=L[0]=Array(Y);for(let z=0;z<Y;z++)D[z]=z}n._data=e=L}if(ar(!0),un("setData"),X==2&&(O=!0),w!==!1){let L=P;L.auto(n,Ne)?et():ls(A,L.min,L.max),ae=ae||be.left>=0,re=!0,or()}}n.setData=Qe;function et(){Ne=!0;let v,w;i==1&&(Y>0?(G=Pe[0]=0,de=Pe[1]=Y-1,v=e[0][G],w=e[0][de],X==2?(v=G,w=de):v==w&&(X==3?[v,w]=Ml(v,v,P.log,!1):X==4?[v,w]=nd(v,v,P.log,!1):P.time?w=v+nn(86400/m):[v,w]=gl(v,w,id,!0))):(G=Pe[0]=v=null,de=Pe[1]=w=null)),ls(A,v,w)}let Be,ht,Pt,Lt,_n,mt,Ge,Yt,gt,Dt;function Hi(v,w,L,D,z,K){v??(v=Qu),L??(L=rd),D??(D="butt"),z??(z=Qu),K??(K="round"),v!=Be&&(d.strokeStyle=Be=v),z!=ht&&(d.fillStyle=ht=z),w!=Pt&&(d.lineWidth=Pt=w),K!=_n&&(d.lineJoin=_n=K),D!=mt&&(d.lineCap=mt=D),L!=Lt&&d.setLineDash(Lt=L)}function Mn(v,w,L,D){w!=ht&&(d.fillStyle=ht=w),v!=Ge&&(d.font=Ge=v),L!=Yt&&(d.textAlign=Yt=L),D!=gt&&(d.textBaseline=gt=D)}function Is(v,w,L,D,z=0){if(D.length>0&&v.auto(n,Ne)&&(w==null||w.min==null)){let K=_t(G,0),oe=_t(de,D.length-1),pe=L.min==null?CS(D,K,oe,z,v.distr==3):[L.min,L.max];v.min=xi(v.min,L.min=pe[0]),v.max=Fn(v.max,L.max=pe[1])}}const Gt={min:null,max:null};function Ti(){for(let D in S){let z=S[D];q[D]==null&&(z.min==null||q[A]!=null&&z.auto(n,Ne))&&(q[D]=Gt)}for(let D in S){let z=S[D];q[D]==null&&z.from!=null&&q[z.from]!=null&&(q[D]=Gt)}q[A]!=null&&ar(!0);let v={};for(let D in q){let z=q[D];if(z!=null){let K=v[D]=oa(S[D],OS);if(z.min!=null)en(K,z);else if(D!=A||i==2)if(Y==0&&K.from==null){let oe=K.range(n,null,null,D);K.min=oe[0],K.max=oe[1]}else K.min=Ct,K.max=-Ct}}if(Y>0){b.forEach((D,z)=>{if(i==1){let K=D.scale,oe=q[K];if(oe==null)return;let pe=v[K];if(z==0){let Me=pe.range(n,pe.min,pe.max,K);pe.min=Me[0],pe.max=Me[1],G=pi(pe.min,e[0]),de=pi(pe.max,e[0]),de-G>1&&(e[0][G]<pe.min&&G++,e[0][de]>pe.max&&de--),D.min=Le[G],D.max=Le[de]}else D.show&&D.auto&&Is(pe,oe,D,e[z],D.sorted);D.idxs[0]=G,D.idxs[1]=de}else if(z>0&&D.show&&D.auto){let[K,oe]=D.facets,pe=K.scale,Me=oe.scale,[De,Ie]=e[z],Fe=v[pe],it=v[Me];Fe!=null&&Is(Fe,q[pe],K,De,K.sorted),it!=null&&Is(it,q[Me],oe,Ie,oe.sorted),D.min=oe.min,D.max=oe.max}});for(let D in v){let z=v[D],K=q[D];if(z.from==null&&(K==null||K.min==null)){let oe=z.range(n,z.min==Ct?null:z.min,z.max==-Ct?null:z.max,D);z.min=oe[0],z.max=oe[1]}}}for(let D in v){let z=v[D];if(z.from!=null){let K=v[z.from];if(K.min==null)z.min=z.max=null;else{let oe=z.range(n,K.min,K.max,D);z.min=oe[0],z.max=oe[1]}}}let w={},L=!1;for(let D in v){let z=v[D],K=S[D];if(K.min!=z.min||K.max!=z.max){K.min=z.min,K.max=z.max;let oe=K.distr;K._min=oe==3?ns(K.min):oe==4?Lc(K.min,K.asinh):oe==100?K.fwd(K.min):K.min,K._max=oe==3?ns(K.max):oe==4?Lc(K.max,K.asinh):oe==100?K.fwd(K.max):K.max,w[D]=L=!0}}if(L){b.forEach((D,z)=>{i==2?z>0&&w.y&&(D._paths=null):w[D.scale]&&(D._paths=null)});for(let D in w)O=!0,un("setScale",D);he&&be.left>=0&&(ae=re=!0)}for(let D in q)q[D]=null}function ya(v){let w=Ch(G-1,0,Y-1),L=Ch(de+1,0,Y-1);for(;v[w]==null&&w>0;)w--;for(;v[L]==null&&L<Y-1;)L++;return[w,L]}function kn(){if(Y>0){let v=b.some(w=>w._focus)&&Dt!=cn.alpha;v&&(d.globalAlpha=Dt=cn.alpha),b.forEach((w,L)=>{if(L>0&&w.show&&(rr(L,!1),rr(L,!0),w._paths==null)){let D=Dt;Dt!=w.alpha&&(d.globalAlpha=Dt=w.alpha);let z=i==2?[0,e[L][0].length-1]:ya(e[L]);w._paths=w.paths(n,L,z[0],z[1]),Dt!=D&&(d.globalAlpha=Dt=D)}}),b.forEach((w,L)=>{if(L>0&&w.show){let D=Dt;Dt!=w.alpha&&(d.globalAlpha=Dt=w.alpha),w._paths!=null&&oo(L,!1);{let z=w._paths!=null?w._paths.gaps:null,K=w.points.show(n,L,G,de,z),oe=w.points.filter(n,L,K,z);(K||oe)&&(w.points._paths=w.points.paths(n,L,G,de,oe),oo(L,!0))}Dt!=D&&(d.globalAlpha=Dt=D),un("drawSeries",L)}}),v&&(d.globalAlpha=Dt=1)}}function rr(v,w){let L=w?b[v].points:b[v];L._stroke=L.stroke(n,v),L._fill=L.fill(n,v)}function oo(v,w){let L=w?b[v].points:b[v],{stroke:D,fill:z,clip:K,flags:oe,_stroke:pe=L._stroke,_fill:Me=L._fill,_width:De=L.width}=L._paths;De=Rt(De*bt,3);let Ie=null,Fe=De%2/2;w&&Me==null&&(Me=De>0?"#fff":pe);let it=L.pxAlign==1&&Fe>0;if(it&&d.translate(Fe,Fe),!w){let yt=Ze-De/2,vt=He-De/2,dt=we+De,tt=Ve+De;Ie=new Path2D,Ie.rect(yt,vt,dt,tt)}w?Bl(pe,De,L.dash,L.cap,Me,D,z,oe,K):lo(v,pe,De,L.dash,L.cap,Me,D,z,oe,Ie,K),it&&d.translate(-Fe,-Fe)}function lo(v,w,L,D,z,K,oe,pe,Me,De,Ie){let Fe=!1;Me!=0&&I.forEach((it,yt)=>{if(it.series[0]==v){let vt=b[it.series[1]],dt=e[it.series[1]],tt=(vt._paths||Ya).band;_s(tt)&&(tt=it.dir==1?tt[0]:tt[1]);let $e,Ft=null;vt.show&&tt&&PS(dt,G,de)?(Ft=it.fill(n,yt)||K,$e=vt._paths.clip):tt=null,Bl(w,L,D,z,Ft,oe,pe,Me,De,Ie,$e,tt),Fe=!0}}),Fe||Bl(w,L,D,z,K,oe,pe,Me,De,Ie)}const xd=la|Lh;function Bl(v,w,L,D,z,K,oe,pe,Me,De,Ie,Fe){Hi(v,w,L,D,z),(Me||De||Fe)&&(d.save(),Me&&d.clip(Me),De&&d.clip(De)),Fe?(pe&xd)==xd?(d.clip(Fe),Ie&&d.clip(Ie),ho(z,oe),co(v,K,w)):pe&Lh?(ho(z,oe),d.clip(Fe),co(v,K,w)):pe&la&&(d.save(),d.clip(Fe),Ie&&d.clip(Ie),ho(z,oe),d.restore(),co(v,K,w)):(ho(z,oe),co(v,K,w)),(Me||De||Fe)&&d.restore()}function co(v,w,L){L>0&&(w instanceof Map?w.forEach((D,z)=>{d.strokeStyle=Be=z,d.stroke(D)}):w!=null&&v&&d.stroke(w))}function ho(v,w){w instanceof Map?w.forEach((L,D)=>{d.fillStyle=ht=D,d.fill(L)}):w!=null&&v&&d.fill(w)}function Pm(v,w,L,D){let z=_[v],K;if(D<=0)K=[0,0];else{let oe=z._space=z.space(n,v,w,L,D),pe=z._incrs=z.incrs(n,v,w,L,D,oe);K=JM(w,L,pe,D,oe)}return z._found=K}function zl(v,w,L,D,z,K,oe,pe,Me,De){let Ie=oe%2/2;x==1&&d.translate(Ie,Ie),Hi(pe,oe,Me,De,pe),d.beginPath();let Fe,it,yt,vt,dt=z+(D==0||D==3?-K:K);L==0?(it=z,vt=dt):(Fe=z,yt=dt);for(let tt=0;tt<v.length;tt++)w[tt]!=null&&(L==0?Fe=yt=v[tt]:it=vt=v[tt],d.moveTo(Fe,it),d.lineTo(yt,vt));d.stroke(),x==1&&d.translate(-Ie,-Ie)}function Lm(v){let w=!0;return _.forEach((L,D)=>{if(!L.show)return;let z=S[L.scale];if(z.min==null){L._show&&(w=!1,L._show=!1,ar(!1));return}else L._show||(w=!1,L._show=!0,ar(!1));let K=L.side,oe=K%2,{min:pe,max:Me}=z,[De,Ie]=Pm(D,pe,Me,oe==0?te:$);if(Ie==0)return;let Fe=z.distr==2,it=L._splits=L.splits(n,D,pe,Me,De,Ie,Fe),yt=z.distr==2?it.map($e=>Le[$e]):it,vt=z.distr==2?Le[it[1]]-Le[it[0]]:De,dt=L._values=L.values(n,L.filter(n,yt,D,Ie,vt),D,Ie,vt);L._rotate=K==2?L.rotate(n,dt,D,Ie):0;let tt=L._size;L._size=ni(L.size(n,dt,D,v)),tt!=null&&L._size!=tt&&(w=!1)}),w}function Dm(v){let w=!0;return W.forEach((L,D)=>{let z=L(n,D,zi,v);z!=Z[D]&&(w=!1),Z[D]=z}),w}function Im(){for(let v=0;v<_.length;v++){let w=_[v];if(!w.show||!w._show)continue;let L=w.side,D=L%2,z,K,oe=w.stroke(n,v),pe=L==0||L==3?-1:1,[Me,De]=w._found;if(w.label!=null){let Ln=w.labelGap*pe,Gn=nn((w._lpos+Ln)*bt);Mn(w.labelFont[0],oe,"center",L==2?Na:Zu),d.save(),D==1?(z=K=0,d.translate(Gn,nn(He+Ve/2)),d.rotate((L==3?-sl:sl)/2)):(z=nn(Ze+we/2),K=Gn);let Fs=Bp(w.label)?w.label(n,v,Me,De):w.label;d.fillText(Fs,z,K),d.restore()}if(De==0)continue;let Ie=S[w.scale],Fe=D==0?we:Ve,it=D==0?Ze:He,yt=w._splits,vt=Ie.distr==2?yt.map(Ln=>Le[Ln]):yt,dt=Ie.distr==2?Le[yt[1]]-Le[yt[0]]:Me,tt=w.ticks,$e=w.border,Ft=tt.show?tt.size:0,$t=nn(Ft*bt),fn=nn((w.alignTo==2?w._size-Ft-w.gap:w.gap)*bt),At=w._rotate*-sl/180,qt=p(w._pos*bt),Hn=($t+fn)*pe,Pn=qt+Hn;K=D==0?Pn:0,z=D==1?Pn:0;let Zn=w.font[0],li=w.align==1?kr:w.align==2?Cc:At>0?kr:At<0?Cc:D==0?"center":L==3?Cc:kr,Ri=At||D==1?"middle":L==2?Na:Zu;Mn(Zn,oe,li,Ri);let Vn=w.font[1]*w.lineGap,Qn=yt.map(Ln=>p(o(Ln,Ie,Fe,it))),ci=w._values;for(let Ln=0;Ln<ci.length;Ln++){let Gn=ci[Ln];if(Gn!=null){D==0?z=Qn[Ln]:K=Qn[Ln],Gn=""+Gn;let Fs=Gn.indexOf(`
`)==-1?[Gn]:Gn.split(/\n/gm);for(let Dn=0;Dn<Fs.length;Dn++){let Fd=Fs[Dn];At?(d.save(),d.translate(z,K+Dn*Vn),d.rotate(At),d.fillText(Fd,0,0),d.restore()):d.fillText(Fd,z,K+Dn*Vn)}}}tt.show&&zl(Qn,tt.filter(n,vt,v,De,dt),D,L,qt,$t,Rt(tt.width*bt,3),tt.stroke(n,v),tt.dash,tt.cap);let Pi=w.grid;Pi.show&&zl(Qn,Pi.filter(n,vt,v,De,dt),D,D==0?2:1,D==0?He:Ze,D==0?Ve:we,Rt(Pi.width*bt,3),Pi.stroke(n,v),Pi.dash,Pi.cap),$e.show&&zl([qt],[1],D==0?1:0,D==0?1:2,D==1?He:Ze,D==1?Ve:we,Rt($e.width*bt,3),$e.stroke(n,v),$e.dash,$e.cap)}un("drawAxes")}function ar(v){b.forEach((w,L)=>{L>0&&(w._paths=null,v&&(i==1?(w.min=null,w.max=null):w.facets.forEach(D=>{D.min=null,D.max=null})))})}let uo=!1,Hl=!1,ba=[];function Um(){Hl=!1;for(let v=0;v<ba.length;v++)un(...ba[v]);ba.length=0}function or(){uo||(WS(vd),uo=!0)}function Nm(v,w=!1){uo=!0,Hl=w,v(n),vd(),w&&ba.length>0&&queueMicrotask(Um)}n.batch=Nm;function vd(){if(B&&(Ti(),B=!1),O&&(xt(),O=!1),ce){if(Ot(f,kr,Ee),Ot(f,Na,xe),Ot(f,Ha,te),Ot(f,Va,$),Ot(g,kr,Ee),Ot(g,Na,xe),Ot(g,Ha,te),Ot(g,Va,$),Ot(u,Ha,Q),Ot(u,Va,le),h.width=nn(Q*bt),h.height=nn(le*bt),_.forEach(({_el:v,_show:w,_size:L,_pos:D,side:z})=>{if(v!=null)if(w){let K=z===3||z===0?L:0,oe=z%2==1;Ot(v,oe?"left":"top",D-K),Ot(v,oe?"width":"height",L),Ot(v,oe?"top":"left",oe?xe:Ee),Ot(v,oe?"height":"width",oe?$:te),Th(v,Ys)}else Xn(v,Ys)}),Be=ht=Pt=_n=mt=Ge=Yt=gt=Lt=null,Dt=1,wa(!0),Ee!=Ce||xe!=Je||te!=me||$!=Ae){ar(!1);let v=te/me,w=$/Ae;if(he&&!ae&&be.left>=0){be.left*=v,be.top*=w,lr&&Li(lr,nn(be.left),0,te,$),cr&&Li(cr,0,nn(be.top),te,$);for(let L=0;L<Rn.length;L++){let D=Rn[L];D!=null&&(oi[L]*=v,Bi[L]*=w,Li(D,ni(oi[L]),ni(Bi[L]),te,$))}}if(Nt.show&&!se&&Nt.left>=0&&Nt.width>0){Nt.left*=v,Nt.width*=v,Nt.top*=w,Nt.height*=w;for(let L in Xl)Ot(ur,L,Nt[L])}Ce=Ee,Je=xe,me=te,Ae=$}un("setSize"),ce=!1}Q>0&&le>0&&(d.clearRect(0,0,h.width,h.height),un("drawClear"),N.forEach(v=>v()),un("draw")),Nt.show&&se&&(fo(Nt),se=!1),he&&ae&&(Ns(null,!0,!1),ae=!1),Te.show&&Te.live&&re&&($l(),re=!1),l||(l=!0,n.status=1,un("ready")),Ne=!1,uo=!1}n.redraw=(v,w)=>{O=w||!1,v!==!1?ls(A,P.min,P.max):or()};function Vl(v,w){let L=S[v];if(L.from==null){if(Y==0){let D=L.range(n,w.min,w.max,v);w.min=D[0],w.max=D[1]}if(w.min>w.max){let D=w.min;w.min=w.max,w.max=D}if(Y>1&&w.min!=null&&w.max!=null&&w.max-w.min<1e-16)return;v==A&&L.distr==2&&Y>0&&(w.min=pi(w.min,e[0]),w.max=pi(w.max,e[0]),w.min==w.max&&w.max++),q[v]=w,B=!0,or()}}n.setScale=Vl;let Gl,Wl,lr,cr,_d,yd,hr,dr,bd,Sd,Ut,Vt,os=!1;const yn=be.drag;let hn=yn.x,dn=yn.y;he&&(be.x&&(Gl=ti(pS,g)),be.y&&(Wl=ti(mS,g)),P.ori==0?(lr=Gl,cr=Wl):(lr=Wl,cr=Gl),Ut=be.left,Vt=be.top);const Nt=n.select=en({show:!0,over:!0,left:0,width:0,top:0,height:0},s.select),ur=Nt.show?ti(fS,Nt.over?g:f):null;function fo(v,w){if(Nt.show){for(let L in v)Nt[L]=v[L],L in Xl&&Ot(ur,L,v[L]);w!==!1&&un("setSelect")}}n.setSelect=fo;function Fm(v){if(b[v].show)ie&&Th(Oe[v],Ys);else if(ie&&Xn(Oe[v],Ys),he){let L=ki?Rn[0]:Rn[v];L!=null&&Li(L,-10,-10,te,$)}}function ls(v,w,L){Vl(v,{min:w,max:L})}function Ai(v,w,L,D){w.focus!=null&&Hm(v),w.show!=null&&b.forEach((z,K)=>{K>0&&(v==K||v==null)&&(z.show=w.show,Fm(K),i==2?(ls(z.facets[0].scale,null,null),ls(z.facets[1].scale,null,null)):ls(z.scale,null,null),or())}),L!==!1&&un("setSeries",v,w),D&&Ea("setSeries",n,v,w)}n.setSeries=Ai;function Om(v,w){en(I[v],w)}function km(v,w){v.fill=ft(v.fill||null),v.dir=_t(v.dir,-1),w=w??I.length,I.splice(w,0,v)}function Bm(v){v==null?I.length=0:I.splice(v,1)}n.addBand=km,n.setBand=Om,n.delBand=Bm;function zm(v,w){b[v].alpha=w,he&&Rn[v]!=null&&(Rn[v].style.opacity=w),ie&&Oe[v]&&(Oe[v].style.opacity=w)}let Vi,cs,Us;const fr={focus:!0};function Hm(v){if(v!=Us){let w=v==null,L=cn.alpha!=1;b.forEach((D,z)=>{if(i==1||z>0){let K=w||z==0||z==v;D._focus=w?null:K,L&&zm(z,K?1:cn.alpha)}}),Us=v,L&&or()}}ie&&Ei&&U(nf,fe,v=>{be._lock||(zt(v),Us!=null&&Ai(null,fr,!0,Zt.setSeries))});function Ci(v,w,L){let D=S[w];L&&(v=v/bt-(D.ori==1?xe:Ee));let z=te;D.ori==1&&(z=$,v=z-v),D.dir==-1&&(v=z-v);let K=D._min,oe=D._max,pe=v/z,Me=K+(oe-K)*pe,De=D.distr;return De==3?ra(10,Me):De==4?DS(Me,D.asinh):De==100?D.bwd(Me):Me}function Vm(v,w){let L=Ci(v,A,w);return pi(L,e[0],G,de)}n.valToIdx=v=>pi(v,e[0]),n.posToIdx=Vm,n.posToVal=Ci,n.valToPos=(v,w,L)=>S[w].ori==0?r(v,S[w],L?we:te,L?Ze:0):a(v,S[w],L?Ve:$,L?He:0),n.setCursor=(v,w,L)=>{Ut=v.left,Vt=v.top,Ns(null,w,L)};function Md(v,w){Ot(ur,kr,Nt.left=v),Ot(ur,Ha,Nt.width=w)}function wd(v,w){Ot(ur,Na,Nt.top=v),Ot(ur,Va,Nt.height=w)}let Sa=P.ori==0?Md:wd,Ma=P.ori==1?Md:wd;function Gm(){if(ie&&Te.live)for(let v=i==2?1:0;v<b.length;v++){if(v==0&&ut)continue;let w=Te.values[v],L=0;for(let D in w)pt[v][L++].firstChild.nodeValue=w[D]}}function $l(v,w){if(v!=null&&(v.idxs?v.idxs.forEach((L,D)=>{ye[D]=L}):FS(v.idx)||ye.fill(v.idx),Te.idx=ye[0]),ie&&Te.live){for(let L=0;L<b.length;L++)(L>0||i==1&&!ut)&&Wm(L,ye[L]);Gm()}re=!1,w!==!1&&un("setLegend")}n.setLegend=$l;function Wm(v,w){let L=b[v],D=v==0&&X==2?Le:e[v],z;ut?z=L.values(n,v,w)??st:(z=L.value(n,w==null?null:D[w],v,w),z=z==null?st:{_:z}),Te.values[v]=z}function Ns(v,w,L){bd=Ut,Sd=Vt,[Ut,Vt]=be.move(n,Ut,Vt),be.left=Ut,be.top=Vt,he&&(lr&&Li(lr,nn(Ut),0,te,$),cr&&Li(cr,0,nn(Vt),te,$));let D,z=G>de;Vi=Ct,cs=null;let K=P.ori==0?te:$,oe=P.ori==1?te:$;if(Ut<0||Y==0||z){D=be.idx=null;for(let pe=0;pe<b.length;pe++){let Me=Rn[pe];Me!=null&&Li(Me,-10,-10,te,$)}Ei&&Ai(null,fr,!0,v==null&&Zt.setSeries),Te.live&&(ye.fill(D),re=!0)}else{let pe,Me,De;i==1&&(pe=P.ori==0?Ut:Vt,Me=Ci(pe,A),D=be.idx=pi(Me,e[0],G,de),De=H(e[0][D],P,K,0));let Ie=-10,Fe=-10,it=0,yt=0,vt=!0,dt="",tt="";for(let $e=i==2?1:0;$e<b.length;$e++){let Ft=b[$e],$t=ye[$e],fn=$t==null?null:i==1?e[$e][$t]:e[$e][1][$t],At=be.dataIdx(n,$e,D,Me),qt=At==null?null:i==1?e[$e][At]:e[$e][1][At];if(re=re||qt!=fn||At!=$t,ye[$e]=At,$e>0&&Ft.show){let Hn=At==null?-10:At==D?De:H(i==1?e[0][At]:e[$e][0][At],P,K,0),Pn=qt==null?-10:J(qt,i==1?S[Ft.scale]:S[Ft.facets[1].scale],oe,0);if(Ei&&qt!=null){let Zn=P.ori==1?Ut:Vt,li=sn(cn.dist(n,$e,At,Pn,Zn));if(li<Vi){let Ri=cn.bias;if(Ri!=0){let Vn=Ci(Zn,Ft.scale),Qn=qt>=0?1:-1,ci=Vn>=0?1:-1;ci==Qn&&(ci==1?Ri==1?qt>=Vn:qt<=Vn:Ri==1?qt<=Vn:qt>=Vn)&&(Vi=li,cs=$e)}else Vi=li,cs=$e}}if(re||ki){let Zn,li;P.ori==0?(Zn=Hn,li=Pn):(Zn=Pn,li=Hn);let Ri,Vn,Qn,ci,Pi,Ln,Gn=!0,Fs=Ht.bbox;if(Fs!=null){Gn=!1;let Dn=Fs(n,$e);Qn=Dn.left,ci=Dn.top,Ri=Dn.width,Vn=Dn.height}else Qn=Zn,ci=li,Ri=Vn=Ht.size(n,$e);if(Ln=Ht.fill(n,$e),Pi=Ht.stroke(n,$e),ki)$e==cs&&Vi<=cn.prox&&(Ie=Qn,Fe=ci,it=Ri,yt=Vn,vt=Gn,dt=Ln,tt=Pi);else{let Dn=Rn[$e];Dn!=null&&(oi[$e]=Qn,Bi[$e]=ci,hf(Dn,Ri,Vn,Gn),lf(Dn,Ln,Pi),Li(Dn,ni(Qn),ni(ci),te,$))}}}}if(ki){let $e=cn.prox,Ft=Us==null?Vi<=$e:Vi>$e||cs!=Us;if(re||Ft){let $t=Rn[0];$t!=null&&(oi[0]=Ie,Bi[0]=Fe,hf($t,it,yt,vt),lf($t,dt,tt),Li($t,ni(Ie),ni(Fe),te,$))}}}if(Nt.show&&os)if(v!=null){let[pe,Me]=Zt.scales,[De,Ie]=Zt.match,[Fe,it]=v.cursor.sync.scales,yt=v.cursor.drag;if(hn=yt._x,dn=yt._y,hn||dn){let{left:vt,top:dt,width:tt,height:$e}=v.select,Ft=v.scales[Fe].ori,$t=v.posToVal,fn,At,qt,Hn,Pn,Zn=pe!=null&&De(pe,Fe),li=Me!=null&&Ie(Me,it);Zn&&hn?(Ft==0?(fn=vt,At=tt):(fn=dt,At=$e),qt=S[pe],Hn=H($t(fn,Fe),qt,K,0),Pn=H($t(fn+At,Fe),qt,K,0),Sa(xi(Hn,Pn),sn(Pn-Hn))):Sa(0,K),li&&dn?(Ft==1?(fn=vt,At=tt):(fn=dt,At=$e),qt=S[Me],Hn=J($t(fn,it),qt,oe,0),Pn=J($t(fn+At,it),qt,oe,0),Ma(xi(Hn,Pn),sn(Pn-Hn))):Ma(0,oe)}else Yl()}else{let pe=sn(bd-_d),Me=sn(Sd-yd);if(P.ori==1){let it=pe;pe=Me,Me=it}hn=yn.x&&pe>=yn.dist,dn=yn.y&&Me>=yn.dist;let De=yn.uni;De!=null?hn&&dn&&(hn=pe>=De,dn=Me>=De,!hn&&!dn&&(Me>pe?dn=!0:hn=!0)):yn.x&&yn.y&&(hn||dn)&&(hn=dn=!0);let Ie,Fe;hn&&(P.ori==0?(Ie=hr,Fe=Ut):(Ie=dr,Fe=Vt),Sa(xi(Ie,Fe),sn(Fe-Ie)),dn||Ma(0,oe)),dn&&(P.ori==1?(Ie=hr,Fe=Ut):(Ie=dr,Fe=Vt),Ma(xi(Ie,Fe),sn(Fe-Ie)),hn||Sa(0,K)),!hn&&!dn&&(Sa(0,0),Ma(0,0))}if(yn._x=hn,yn._y=dn,v==null){if(L){if(Nd!=null){let[pe,Me]=Zt.scales;Zt.values[0]=pe!=null?Ci(P.ori==0?Ut:Vt,pe):null,Zt.values[1]=Me!=null?Ci(P.ori==1?Ut:Vt,Me):null}Ea(Rc,n,Ut,Vt,te,$,D)}if(Ei){let pe=L&&Zt.setSeries,Me=cn.prox;Us==null?Vi<=Me&&Ai(cs,fr,!0,pe):Vi>Me?Ai(null,fr,!0,pe):cs!=Us&&Ai(cs,fr,!0,pe)}}re&&(Te.idx=D,$l()),w!==!1&&un("setCursor")}let hs=null;Object.defineProperty(n,"rect",{get(){return hs==null&&wa(!1),hs}});function wa(v=!1){v?hs=null:(hs=g.getBoundingClientRect(),un("syncRect",hs))}function Ed(v,w,L,D,z,K,oe){be._lock||os&&v!=null&&v.movementX==0&&v.movementY==0||(ql(v,w,L,D,z,K,oe,!1,v!=null),v!=null?Ns(null,!0,!0):Ns(w,!0,!1))}function ql(v,w,L,D,z,K,oe,pe,Me){if(hs==null&&wa(!1),zt(v),v!=null)L=v.clientX-hs.left,D=v.clientY-hs.top;else{if(L<0||D<0){Ut=-10,Vt=-10;return}let[De,Ie]=Zt.scales,Fe=w.cursor.sync,[it,yt]=Fe.values,[vt,dt]=Fe.scales,[tt,$e]=Zt.match,Ft=w.axes[0].side%2==1,$t=P.ori==0?te:$,fn=P.ori==1?te:$,At=Ft?K:z,qt=Ft?z:K,Hn=Ft?D:L,Pn=Ft?L:D;if(vt!=null?L=tt(De,vt)?o(it,S[De],$t,0):-10:L=$t*(Hn/At),dt!=null?D=$e(Ie,dt)?o(yt,S[Ie],fn,0):-10:D=fn*(Pn/qt),P.ori==1){let Zn=L;L=D,D=Zn}}Me&&(w==null||w.cursor.event.type==Rc)&&((L<=1||L>=te-1)&&(L=Ws(L,te)),(D<=1||D>=$-1)&&(D=Ws(D,$))),pe?(_d=L,yd=D,[hr,dr]=be.move(n,L,D)):(Ut=L,Vt=D)}const Xl={width:0,height:0,left:0,top:0};function Yl(){fo(Xl,!1)}let Td,Ad,Cd,Rd;function Pd(v,w,L,D,z,K,oe){os=!0,hn=dn=yn._x=yn._y=!1,ql(v,w,L,D,z,K,oe,!0,!1),v!=null&&(U(Pc,wh,Ld,!1),Ea(ef,n,hr,dr,te,$,null));let{left:pe,top:Me,width:De,height:Ie}=Nt;Td=pe,Ad=Me,Cd=De,Rd=Ie}function Ld(v,w,L,D,z,K,oe){os=yn._x=yn._y=!1,ql(v,w,L,D,z,K,oe,!1,!0);let{left:pe,top:Me,width:De,height:Ie}=Nt,Fe=De>0||Ie>0,it=Td!=pe||Ad!=Me||Cd!=De||Rd!=Ie;if(Fe&&it&&fo(Nt),yn.setScale&&Fe&&it){let yt=pe,vt=De,dt=Me,tt=Ie;if(P.ori==1&&(yt=Me,vt=Ie,dt=pe,tt=De),hn&&ls(A,Ci(yt,A),Ci(yt+vt,A)),dn)for(let $e in S){let Ft=S[$e];$e!=A&&Ft.from==null&&Ft.min!=Ct&&ls($e,Ci(dt+tt,$e),Ci(dt,$e))}Yl()}else be.lock&&(be._lock=!be._lock,Ns(w,!0,v!=null));v!=null&&(E(Pc,wh),Ea(Pc,n,Ut,Vt,te,$,null))}function $m(v,w,L,D,z,K,oe){if(be._lock)return;zt(v);let pe=os;if(os){let Me=!0,De=!0,Ie=10,Fe,it;P.ori==0?(Fe=hn,it=dn):(Fe=dn,it=hn),Fe&&it&&(Me=Ut<=Ie||Ut>=te-Ie,De=Vt<=Ie||Vt>=$-Ie),Fe&&Me&&(Ut=Ut<hr?0:te),it&&De&&(Vt=Vt<dr?0:$),Ns(null,!0,!0),os=!1}Ut=-10,Vt=-10,ye.fill(null),Ns(null,!0,!0),pe&&(os=pe)}function Dd(v,w,L,D,z,K,oe){be._lock||(zt(v),et(),Yl(),v!=null&&Ea(sf,n,Ut,Vt,te,$,null))}function Id(){_.forEach(ZM),_e(n.width,n.height,!0)}Zs(ml,Jr,Id);const pr={};pr.mousedown=Pd,pr.mousemove=Ed,pr.mouseup=Ld,pr.dblclick=Dd,pr.setSeries=(v,w,L,D)=>{let z=Zt.match[2];L=z(n,w,L),L!=-1&&Ai(L,D,!0,!1)},he&&(U(ef,g,Pd),U(Rc,g,Ed),U(tf,g,v=>{zt(v),wa(!1)}),U(nf,g,$m),U(sf,g,Dd),Dh.add(n),n.syncRect=wa);const po=n.hooks=s.hooks||{};function un(v,w,L){Hl?ba.push([v,w,L]):v in po&&po[v].forEach(D=>{D.call(null,n,w,L)})}(s.plugins||[]).forEach(v=>{for(let w in v.hooks)po[w]=(po[w]||[]).concat(v.hooks[w])});const Ud=(v,w,L)=>L,Zt=en({key:null,setSeries:!1,filters:{pub:mf,sub:mf},scales:[A,b[1]?b[1].scale:null],match:[gf,gf,Ud],values:[null,null]},be.sync);Zt.match.length==2&&Zt.match.push(Ud),be.sync=Zt;const Nd=Zt.key,jl=cm(Nd);function Ea(v,w,L,D,z,K,oe){Zt.filters.pub(v,w,L,D,z,K,oe)&&jl.pub(v,w,L,D,z,K,oe)}jl.sub(n);function qm(v,w,L,D,z,K,oe){Zt.filters.sub(v,w,L,D,z,K,oe)&&pr[v](null,w,L,D,z,K,oe)}n.pub=qm;function Xm(){jl.unsub(n),Dh.delete(n),qe.clear(),Ah(ml,Jr,Id),c.remove(),fe==null||fe.remove(),un("destroy")}n.destroy=Xm;function Kl(){un("init",s,e),Qe(e||s.data,!1),q[A]?Vl(A,q[A]):et(),se=Nt.show&&(Nt.width>0||Nt.height>0),ae=re=!0,_e(s.width,s.height)}return b.forEach(_a),_.forEach(kl),t?t instanceof HTMLElement?(t.appendChild(c),Kl()):t(n,Kl):Kl(),n}gn.assign=en;gn.fmtNum=sd;gn.rangeNum=gl;gn.rangeLog=Ml;gn.rangeAsinh=nd;gn.orient=sr;gn.pxRatio=bt;gn.join=GS;gn.fmtDate=ad,gn.tzDate=eM;gn.sync=cm;{gn.addGap=FM,gn.clipGaps=Tl;let s=gn.paths={points:mm};s.linear=xm,s.stepped=BM,s.bars=zM,s.spline=VM}function Nc(s){return Math.max(120,s.clientHeight-30)}const Fc=[{id:"pareto",panelId:"plotter-pareto",hostId:"plotter-pareto-chart",title:"Pareto frontier",glyph:"◭",key:ws.pareto},{id:"ablation",panelId:"plotter-ablation",hostId:"plotter-ablation-chart",title:"Ablation",glyph:"▥",key:ws.ablation},{id:"variability",panelId:"plotter-variability",hostId:"plotter-variability-chart",title:"Variability",glyph:"◇",key:ws.variability}];class QM{constructor(){T(this,"name","Plotter");T(this,"container",null);T(this,"chartPanels",new Map);T(this,"tooltip",null);T(this,"paretoPlot",null);T(this,"ablationPlot",null);T(this,"variabilityPlot",null);T(this,"records",[]);T(this,"ablationGroups",[]);T(this,"paretoFlags",[]);T(this,"chance",.1);T(this,"paretoRecordIndices",[]);T(this,"paretoXData",[]);T(this,"paretoYData",[]);T(this,"categoryLabels",[]);T(this,"ablationFixedAxes","");T(this,"onCampaignMetrics",e=>{const{data:t}=e;t!=null&&t.records&&Yn.observe(e==null?void 0:e.campaign_id,t)});T(this,"onRunChanged",(e,t)=>{t&&(this.records=t.records??[],this.paretoFlags=t.pareto??[],this.ablationGroups=t.ablation_groups??[],typeof t.chance=="number"&&(this.chance=t.chance),this.updatePlots(),this.updateStatus())});jt.register("campaign_metrics",this.onCampaignMetrics),Yn.onChange(this.onRunChanged)}async init(){this.createUI(),console.log("[Plotter] Initialized")}async destroy(){var e,t,n,i;jt.unregister("campaign_metrics",this.onCampaignMetrics),(e=this.paretoPlot)==null||e.destroy(),(t=this.ablationPlot)==null||t.destroy(),(n=this.variabilityPlot)==null||n.destroy(),(i=this.container)==null||i.remove()}createUI(){const e=document.getElementById("ui-overlay");if(e){this.container=document.createElement("div"),this.container.id="chart-column",this.container.style.cssText=`
      position: fixed;
      top: 330px;
      bottom: 130px;
      right: 44px;
      width: 520px;
      display: flex;
      flex-direction: column;
      gap: 8px;
      overflow-y: auto;
      z-index: 150;
      pointer-events: none;
    `;for(const t of Fc)this.container.appendChild(this.createChartPanel(t));e.appendChild(this.container),this.tooltip=document.createElement("div"),this.tooltip.id="plotter-tooltip",this.tooltip.style.cssText=`
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
    `,this.container.appendChild(this.tooltip),this.setPanelOpen(Fc[0].id,!0)}}createChartPanel(e){const t=document.createElement("div");return t.id=e.panelId,t.className="chart-panel",t.style.cssText=`
      position: relative;
      flex: 0 0 auto;
      height: 300px;
      background: var(--bg-secondary);
      border: 1px solid var(--border);
      border-radius: 8px;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      pointer-events: auto;
      box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    `,t.innerHTML=`
      <div class="chart-header" style="
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 12px;
        border-bottom: 1px solid var(--border);
        background: var(--bg-tertiary);
        font-size: 12px;
        font-weight: 600;
        color: var(--text-primary);
      ">
        <span class="chart-title">${e.title}</span>
        <div style="flex: 1;"></div>
        <div class="chart-empty-hint" style="
          display: none;
          align-items: center;
          gap: 6px;
          padding: 4px 10px;
          background: var(--bg);
          border: 1px solid var(--border);
          border-radius: 4px;
          font-size: 10px;
          color: var(--text-muted);
        ">
          <span>No data yet</span>
          <span style="color: var(--text-secondary);">→</span>
          <span>Select a run from the legend</span>
        </div>
        <button class="chart-download" style="
          padding: 3px 8px;
          background: var(--bg-secondary);
          border: 1px solid var(--border);
          border-radius: 4px;
          color: var(--text-primary);
          font-size: 11px;
          cursor: pointer;
        ">PNG</button>
      </div>
      <div id="${e.hostId}" style="flex: 1; position: relative; overflow: hidden;"></div>
      <div class="chart-empty-state" style="
        display: none;
        position: absolute;
        inset: 0;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        gap: 12px;
        padding: 24px;
        text-align: center;
        background: var(--bg-secondary);
        border-radius: 0 0 8px 8px;
      ">
        <div class="empty-icon" style="font-size: 48px; opacity: 0.2;">${e.glyph}</div>
        <div style="font-size: 13px; font-weight: 600; color: var(--text-primary);">${e.title}</div>
        <div style="font-size: 11px; color: var(--text-secondary); max-width: 280px; line-height: 1.5;">${this.getEmptyHint(e.id)}</div>
      </div>
      <div class="chart-toolbar" style="
        padding: 6px 12px;
        border-top: 1px solid var(--border);
        display: flex;
        gap: 8px;
        align-items: center;
        font-size: 11px;
        color: var(--text-secondary);
      ">
        <span class="chart-status" style="
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        ">No data</span>
      </div>
    `,pl(t,!0),t.querySelector(".chart-header").appendChild(fa(()=>Sn.toggle(e.panelId))),t.querySelector(".chart-download").addEventListener("click",()=>this.download(e.id)),this.chartPanels.set(e.id,t),ir(e.panelId,e.title.toLowerCase(),e.glyph,()=>this.chartPanels.get(e.id)??null,e.key),t}getEmptyHint(e){switch(e){case"pareto":return"Shows validation accuracy vs. speed for each measured cell. Pareto frontier cells are not dominated on both axes.";case"ablation":return"Shows how each credit arm performs when other axes are held fixed. Error bars = ±1 std dev. Dashed line = chance level.";case"variability":return"Shows seed-to-seed spread per credit arm. Box = IQR, line = median, whiskers = 1.5×IQR, dots = outliers. Dashed line = chance level.";default:return"Select a run from the legend to populate this chart."}}showTab(e){var n;const t=Fc.find(i=>i.id===e);t&&(this.setPanelOpen(t.id,!0),(n=this.chartPanels.get(t.id))==null||n.scrollIntoView({block:"nearest"}))}setPanelOpen(e,t){const n=this.chartPanels.get(e);n&&(pl(n,!t),t&&this.initPlot(e))}initPlot(e){e==="pareto"&&!this.paretoPlot&&this.initParetoPlot(),e==="ablation"&&!this.ablationPlot&&this.initAblationPlot(),e==="variability"&&!this.variabilityPlot&&this.initVariabilityPlot(),this.updatePlots()}updateStatus(){const e=this.records.length>0,t=`${this.records.length} records | ${this.paretoFlags.filter(i=>i).length} Pareto`,n=this.ablationFixedAxes?` | fixed: ${this.ablationFixedAxes}`:"";for(const i of this.chartPanels.values()){const r=i.querySelector(".chart-status"),a=i.querySelector(".chart-empty-state"),o=i.querySelector(".chart-empty-hint");r&&(r.textContent=e?t+n:"No run selected",r.title=r.textContent),a&&(a.style.display=e?"none":"flex"),o&&(o.style.display=e?"none":"flex")}}updatePlots(){const e=this.records.length>0;for(const t of this.chartPanels.values()){const n=t.querySelector(".chart-empty-state"),i=t.querySelector(".chart-empty-hint");n&&(n.style.display=e?"none":"flex"),i&&(i.style.display=e?"none":"flex")}this.paretoPlot&&this.updateParetoPlot(),this.ablationPlot&&this.updateAblationPlot(),this.variabilityPlot&&this.updateVariabilityPlot()}initParetoPlot(){const e=document.getElementById("plotter-pareto-chart");if(!e)return;const t={width:e.clientWidth,height:Nc(e),title:"Pareto Frontier: validation accuracy vs speed",axes:[{label:"1 / walltime_s   (faster →)",grid:{stroke:F.border}},{label:"accuracy",grid:{stroke:F.border},side:1}],scales:{x:{time:!1},y:{time:!1}},series:[{},{label:"val_acc",stroke:F.gradient,width:0,points:{show:!0,size:8,stroke:"white",width:1,fill:(n,i)=>{var o;const r=this.paretoRecordIndices[i],a=r===void 0?void 0:this.records[r];return a&&Wt[(o=a.coordinate)==null?void 0:o.credit]||F.gradient}}}],hooks:{draw:[n=>{const i=n.ctx;if(this.paretoFlags.some(a=>a)){const a=[];this.records.forEach((o,l)=>{this.paretoFlags[l]&&o.payload.walltime_s&&o.payload.val_acc&&a.push([1/o.payload.walltime_s,o.payload.val_acc])}),a.sort((o,l)=>o[0]-l[0]),a.length>1&&(i.beginPath(),i.strokeStyle=F.pareto,i.lineWidth=2,i.setLineDash([5,5]),a.forEach((o,l)=>{const c=n.valToPos(o[0],"x"),h=n.valToPos(o[1],"y");l===0?i.moveTo(c,h):i.lineTo(c,h)}),i.stroke(),i.setLineDash([])),a.forEach(o=>{const l=n.valToPos(o[0],"x"),c=n.valToPos(o[1],"y");i.beginPath(),i.arc(l,c,7,0,Math.PI*2),i.strokeStyle=F.pareto,i.lineWidth=1.5,i.stroke()})}const r=n.valToPos(this.chance,"y");i.strokeStyle=F.chance_line,i.lineWidth=1.5,i.setLineDash([4,4]),i.beginPath(),i.moveTo(n.bbox.left,r),i.lineTo(n.bbox.width,r),i.stroke(),i.setLineDash([])}],setCursor:[n=>{this.showScatterTooltip(n)}]},cursor:{show:!0,drag:{setScale:!0},focus:{prox:16}}};this.paretoPlot=new gn(t,[[],[]],e)}recordAt(e){const t=this.paretoRecordIndices[e];return t===void 0?void 0:this.records[t]}updateParetoPlot(){if(!this.paretoPlot||this.records.length===0)return;const e=[],t=[];this.paretoRecordIndices=[],this.records.forEach((r,a)=>{const o=r.payload.walltime_s,l=r.payload.val_acc;this.paretoRecordIndices.push(a),o&&l?(e.push(1/o),t.push(l)):(e.push(NaN),t.push(NaN))}),this.paretoPlot.setData([e,t]),this.paretoXData=e,this.paretoYData=t;const n=e.filter(Number.isFinite),i=t.filter(Number.isFinite);n.length>0&&this.fitScale(this.paretoPlot,"x",Math.min(...n),Math.max(...n)),i.length>0&&this.fitScale(this.paretoPlot,"y",Math.min(Math.min(...i),this.chance),Math.max(...i))}fitScale(e,t,n,i){if(!Number.isFinite(n)||!Number.isFinite(i))return;n===i&&(n-=.01,i+=.01);const r=(i-n)*.05;e.setScale(t,{min:n-r,max:i+r})}initAblationPlot(){const e=document.getElementById("plotter-ablation-chart");if(!e)return;const t={width:e.clientWidth,height:Nc(e),title:"Ablation: credit arm → validation accuracy",axes:[{label:"credit arm",splits:()=>this.categoryIndices(),values:(n,i)=>i.map(r=>this.categoryLabels[r]??String(r)),grid:{stroke:F.border}},{label:"accuracy",grid:{stroke:F.border},side:1}],scales:{x:{time:!1},y:{time:!1}},series:[{},{label:"val_acc",width:0,points:{show:!1}}],hooks:{draw:[n=>{if(!this.ablationGroups.length)return;const i=n.ctx,r=this.ablationGroups.find(h=>h.axis==="credit");if(!r)return;const a=r.metrics.find(h=>h.metric==="val_acc");if(!a)return;const o=a.arms,l=n.bbox.width/(o.length*1.5);n.bbox.left,o.forEach((h,d)=>{const u=n.valToPos(d,"x"),f=n.valToPos(0,"y"),g=n.valToPos(h.mean,"y"),x=f-g;if(i.fillStyle=Wt[h.value]||F.gradient,i.fillRect(u-l/2,g,l,x),h.std>0){const p=n.valToPos(h.mean+h.std,"y");i.strokeStyle=F.text_muted,i.lineWidth=1,i.beginPath(),i.moveTo(u,p),i.lineTo(u,f),i.stroke(),i.moveTo(u-3,p),i.lineTo(u+3,p),i.stroke()}});const c=n.valToPos(this.chance,"y");i.strokeStyle=F.chance_line,i.lineWidth=2,i.setLineDash([5,5]),i.beginPath(),i.moveTo(n.bbox.left,c),i.lineTo(n.bbox.width,c),i.stroke(),i.setLineDash([])}],setCursor:[n=>{this.showCategoryTooltip(n,"ablation")}]},cursor:{show:!0,drag:{setScale:!0}}};this.ablationPlot=new gn(t,[[],[]],e)}updateAblationPlot(){if(!this.ablationPlot||!this.ablationGroups.length)return;const e=this.ablationGroups.find(o=>o.axis==="credit");if(!e)return;const t=e.metrics.find(o=>o.metric==="val_acc");if(!t)return;const n=t.arms.map((o,l)=>l),i=t.arms.map(o=>o.mean);this.categoryLabels=t.arms.map(o=>o.value),this.ablationFixedAxes=e.fixed_axes.split(",").map(o=>o.split("=").pop()??o).join(", "),this.ablationPlot.setData([n,i]),this.fitScale(this.ablationPlot,"x",-.5,Math.max(n.length-.5,.5));const r=t.arms.flatMap(o=>[o.mean-o.std,o.mean+o.std]);r.length>0&&this.fitScale(this.ablationPlot,"y",Math.min(Math.min(...r),this.chance),Math.max(...r));const a=this.ablationPlot.root.querySelector(".u-title");a&&(a.textContent=`Ablation: ${e.axis} vs val_acc`)}initVariabilityPlot(){const e=document.getElementById("plotter-variability-chart");if(!e)return;const t={width:e.clientWidth,height:Nc(e),title:"Seed variability: validation accuracy per arm",axes:[{label:"credit arm",splits:()=>this.categoryIndices(),values:(n,i)=>i.map(r=>this.categoryLabels[r]??String(r)),grid:{stroke:F.border}},{label:"accuracy",grid:{stroke:F.border},side:1}],scales:{x:{time:!1},y:{time:!1}},series:[{},{label:"val_acc",width:0,points:{show:!1}}],hooks:{draw:[n=>{if(!this.records.length)return;const i=n.ctx,r={};this.records.forEach(c=>{const h=c.coordinate.credit,d=c.payload.val_acc;d!==void 0&&(r[h]||(r[h]=[])).push(d)});const a=Object.keys(r).sort(),o=n.bbox.width/(a.length*2);a.forEach((c,h)=>{const d=r[c].sort((y,P)=>y-P),u=d.length;if(u===0)return;const f=d[Math.floor(u*.25)],g=d[Math.floor(u*.5)],x=d[Math.floor(u*.75)],p=x-f,m=Math.max(d[0],f-1.5*p),b=Math.min(d[u-1],x+1.5*p),_=n.valToPos(h,"x"),S=n.valToPos(m,"y"),I=n.valToPos(f,"y"),A=n.valToPos(g,"y"),R=n.valToPos(x,"y"),N=n.valToPos(b,"y"),M=Wt[c]||F.gradient;i.strokeStyle=M,i.lineWidth=1.5,i.beginPath(),i.moveTo(_,S),i.lineTo(_,I),i.moveTo(_,R),i.lineTo(_,N),i.stroke(),i.fillStyle=M+"44",i.strokeStyle=M,i.lineWidth=1.5,i.fillRect(_-o/2,R,o,I-R),i.strokeRect(_-o/2,R,o,I-R),i.strokeStyle="white",i.lineWidth=2,i.beginPath(),i.moveTo(_-o/2,A),i.lineTo(_+o/2,A),i.stroke(),d.forEach(y=>{if(y<m||y>b){const P=n.valToPos(y,"y");i.fillStyle=M,i.beginPath(),i.arc(_,P,2,0,Math.PI*2),i.fill()}})});const l=n.valToPos(this.chance,"y");i.strokeStyle=F.chance_line,i.lineWidth=2,i.setLineDash([5,5]),i.beginPath(),i.moveTo(n.bbox.left,l),i.lineTo(n.bbox.width,l),i.stroke(),i.setLineDash([])}],setCursor:[n=>{this.showCategoryTooltip(n,"variability")}]},cursor:{show:!0,drag:{setScale:!0}}};this.variabilityPlot=new gn(t,[[],[]],e)}updateVariabilityPlot(){if(!this.variabilityPlot||!this.records.length)return;const e=Array.from(new Set(this.records.map(r=>r.coordinate.credit))).sort(),t=e.map((r,a)=>a),n=e.map(()=>0);this.categoryLabels=e,this.variabilityPlot.setData([t,n]),this.fitScale(this.variabilityPlot,"x",-.5,Math.max(e.length-.5,.5));const i=this.records.map(r=>r.payload.val_acc).filter(r=>typeof r=="number");i.length>0&&this.fitScale(this.variabilityPlot,"y",Math.min(Math.min(...i),this.chance),Math.max(...i))}categoryIndices(){return this.categoryLabels.map((e,t)=>t)}showTooltip(e,t){if(!this.tooltip||!this.container)return;const n=e.cursor;if(!n||n.left==null||n.top==null){this.hideTooltip();return}const i=e.ctx.canvas.getBoundingClientRect(),r=this.container.getBoundingClientRect();this.tooltip.innerHTML=t,this.tooltip.style.display="block",this.tooltip.style.left=`${i.left-r.left+e.bbox.left+n.left+14}px`,this.tooltip.style.top=`${i.top-r.top+e.bbox.top+n.top+14}px`}hideTooltip(){this.tooltip&&(this.tooltip.style.display="none")}showScatterTooltip(e){var u,f;const t=e.cursor;if(!t||t.left==null||t.top==null){this.hideTooltip();return}let n=-1,i=1/0;if(this.paretoXData.forEach((g,x)=>{const p=this.paretoYData[x];if(!Number.isFinite(g)||!Number.isFinite(p))return;const m=e.valToPos(g,"x"),b=e.valToPos(p,"y");if(!Number.isFinite(m)||!Number.isFinite(b))return;const _=(m-t.left)**2+(b-t.top)**2;_<i&&(i=_,n=x)}),n<0||i>400){this.hideTooltip();return}const r=this.recordAt(n);if(!r){this.hideTooltip();return}const a=this.paretoRecordIndices[n],o=((u=r.coordinate)==null?void 0:u.credit)??"?",l=r.payload.val_acc??0,c=r.payload.walltime_s??0,h=((f=r.schedule)==null?void 0:f.seed)??"?",d=this.paretoFlags[a]?" · PARETO":"";this.showTooltip(e,`${o} · val_acc ${l.toFixed(3)} · ${c.toFixed(1)}s · seed ${h}${d}`)}showCategoryTooltip(e,t){const n=e.cursor;if(!n||n.left==null||n.top==null){this.hideTooltip();return}const i=Math.round(e.posToVal(n.left,"x"));if(i<0||i>=this.categoryLabels.length){this.hideTooltip();return}const r=this.categoryLabels[i];if(t==="ablation"){const h=this.ablationGroups.find(f=>f.axis==="credit"),d=h==null?void 0:h.metrics.find(f=>f.metric==="val_acc"),u=d==null?void 0:d.arms[i];if(!u){this.hideTooltip();return}this.showTooltip(e,`${r} · ${u.mean.toFixed(3)} ± ${u.std.toFixed(3)} (n=${u.count})${u.at_chance?" · at chance":""}`);return}const a=this.records.filter(h=>h.coordinate.credit===r).map(h=>h.payload.val_acc).filter(h=>typeof h=="number").sort((h,d)=>h-d);if(a.length===0){this.hideTooltip();return}const o=a[Math.floor(a.length*.5)],l=a[Math.floor(a.length*.25)],c=a[Math.floor(a.length*.75)];this.showTooltip(e,`${r} · median ${o.toFixed(3)} · IQR ${(c-l).toFixed(3)} · n=${a.length}`)}download(e){const n={pareto:this.paretoPlot,ablation:this.ablationPlot,variability:this.variabilityPlot}[e];if(!n)return;const i=document.createElement("a");i.download=`computronium-${e}-${Date.now()}.png`,i.href=this.exportImage(n),i.click()}exportImage(e){const t=Array.from(e.root.querySelectorAll("canvas")),n=e.root.getBoundingClientRect(),i=Math.max(...t.map(l=>l.width),1),r=Math.max(...t.map(l=>l.height),1),a=document.createElement("canvas");a.width=i,a.height=r;const o=a.getContext("2d");return o?(o.fillStyle=F.bg,o.fillRect(0,0,i,r),t.forEach(l=>{const c=l.getBoundingClientRect();if(c.width===0||c.height===0)return;const h=l.width/c.width;o.drawImage(l,(c.left-n.left)*h,(c.top-n.top)*h,l.width,l.height)}),a.toDataURL("image/png")):e.ctx.canvas.toDataURL("image/png")}}const fd=new QM;Kn.register(fd);class ew{constructor(){T(this,"name","LiveRail");T(this,"container",null);T(this,"logContainer",null);T(this,"scrollHint",null);T(this,"events",[]);T(this,"maxEvents",50);T(this,"onPipelineEvent",e=>{this.events.unshift(e),this.events.length>this.maxEvents&&this.events.pop(),this.render()});T(this,"onStatusUpdate",e=>{var r,a,o;const t=((r=e==null?void 0:e.data)==null?void 0:r.running_campaigns)??0,n=((a=e==null?void 0:e.data)==null?void 0:a.queued_campaigns)??0,i=(o=this.container)==null?void 0:o.querySelector("#rail-queue");i&&(i.textContent=`${t} running · ${n} queued`)});jt.register("pipeline_event",this.onPipelineEvent),jt.register("status_update",this.onStatusUpdate)}async init(){this.createUI(),ir("live-rail","live rail","≡",()=>this.container,Zi.rail),ia.onStateChange(e=>this.setConnected(e==="connected")),console.log("[LiveRail] Initialized")}async destroy(){var e;jt.unregister("pipeline_event",this.onPipelineEvent),jt.unregister("status_update",this.onStatusUpdate),(e=this.container)==null||e.remove()}createUI(){const e=document.getElementById("ui-overlay");e&&(this.container=document.createElement("div"),this.container.id="live-rail",this.container.style.cssText=`
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
      <div id="rail-header" style="
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
        <span id="rail-queue" style="color: var(--text-secondary); font-variant-numeric: tabular-nums;">0 running · 0 queued</span>
        <span id="rail-count" style="color: var(--text-muted);">0 events</span>
      </div>
      <div id="rail-log" style="
        flex: 1;
        overflow-x: auto;
        overflow-y: hidden;
        display: flex;
        gap: 16px;
        padding: 8px 16px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        white-space: nowrap;
        scrollbar-width: thin;
        scrollbar-color: var(--border) transparent;
      "></div>
      <!-- Scroll hint -->
      <div id="rail-scroll-hint" style="
        position: absolute;
        right: 0;
        bottom: 0;
        width: 60px;
        height: 100%;
        pointer-events: none;
        background: linear-gradient(to left, var(--bg), transparent);
        opacity: 0;
        transition: opacity var(--motion-fast);
      "></div>
    `,e.appendChild(this.container),this.container.querySelector("#rail-header").appendChild(fa(()=>Sn.toggle("live-rail"))),this.logContainer=this.container.querySelector("#rail-log"),this.scrollHint=this.container.querySelector("#rail-scroll-hint"),this.logContainer.addEventListener("scroll",()=>{if(this.scrollHint){const t=this.logContainer.scrollLeft===0,n=this.logContainer.scrollWidth>this.logContainer.clientWidth;this.scrollHint.style.opacity=t&&n?"1":"0"}}))}setConnected(e){var a;const t=(a=this.container)==null?void 0:a.querySelector("#rail-connection");if(!t)return;const n=t.querySelector(".dot"),i=t.querySelector(".rail-label");if(!n||!i)return;const r=e?F.ok:F.error;n.style.background=r,t.style.background=r+"22",t.style.borderColor=r+"88",t.style.color=r,i.textContent=e?"Connected":"Disconnected"}render(){var t;if(!this.logContainer)return;this.logContainer.innerHTML=this.events.map((n,i)=>{const r=new Date(n.timestamp).toLocaleTimeString(),o={ok:F.ok,warn:F.warn,error:F.error}[n.level]||F.text_secondary,l={ok:"✓",warn:"⚠",error:"✗"},c=i===0;return`
          <span style="
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 6px 14px;
            background: ${c?"var(--bg-primary)":"var(--bg-secondary)"};
            border: 1px solid ${c?"var(--border-bright)":"var(--border)"};
            border-radius: 18px;
            color: var(--text-primary);
            font-weight: ${c?"500":"400"};
            box-shadow: ${c?"0 2px 8px rgba(0,0,0,0.3)":"none"};
          ">
            <span style="color: var(--text-secondary); font-variant-numeric: tabular-nums;">${r}</span>
            <span style="color: ${o}; font-size: 12px;">${l[n.level]??"•"}</span>
            <span style="color: var(--text-muted); font-size: 10px; text-transform: uppercase; letter-spacing: 0.05em;">${n.stage}</span>
            <span>${n.message}</span>
          </span>
        `}).join("");const e=(t=this.container)==null?void 0:t.querySelector("#rail-count");if(e&&(e.textContent=`${this.events.length} events`),this.logContainer.scrollLeft=0,this.scrollHint){const n=this.logContainer.scrollWidth>this.logContainer.clientWidth;this.scrollHint.style.opacity=n?"1":"0"}}}const bm=new ew;Kn.register(bm);const tw=4e3,nw={ok:F.text_primary,warn:F.warn,error:F.error};class iw{constructor(){T(this,"name","Caption");T(this,"container",null);T(this,"headline",null);T(this,"context",null);T(this,"state",[]);T(this,"spoken",null);T(this,"last",null);T(this,"holdTimer",null);T(this,"onNarration",e=>{this.state=(e==null?void 0:e.state)??[],this.render()});T(this,"onEvent",e=>{e!=null&&e.sentence&&this.say(e.sentence,e.level??"ok")});jt.register("narration",this.onNarration),jt.register("pipeline_event",this.onEvent)}async init(){this.createUI(),this.render(),ir("caption","caption","▤",()=>this.container,Zi.caption)}async destroy(){var e;jt.unregister("narration",this.onNarration),jt.unregister("pipeline_event",this.onEvent),this.holdTimer!==null&&window.clearTimeout(this.holdTimer),(e=this.container)==null||e.remove()}say(e,t="ok"){e&&(this.spoken={text:e,level:t},this.last={text:e,level:t},this.render(),this.holdTimer!==null&&window.clearTimeout(this.holdTimer),this.holdTimer=window.setTimeout(()=>{this.spoken=null,this.holdTimer=null,this.render()},tw))}createUI(){const e=document.getElementById("ui-overlay");if(!e)return;this.container=document.createElement("div"),this.container.id="caption",this.container.style.cssText=`
      position: fixed;
      bottom: 200px;
      left: 50%;
      transform: translateX(-50%);
      width: 820px;
      max-width: calc(100vw - 80px);
      padding: 12px 20px;
      background: rgba(10, 14, 20, 0.92);
      border: 1px solid var(--border);
      border-radius: 10px;
      text-align: center;
      z-index: 160;
      pointer-events: none;
      box-shadow: 0 8px 32px rgba(0,0,0,0.45);
      backdrop-filter: blur(8px);
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
    `,e.appendChild(this.container);const t=fa(()=>Sn.toggle("caption"));t.style.position="absolute",t.style.top="4px",t.style.right="8px",this.container.appendChild(t),this.headline=this.container.querySelector("#caption-headline"),this.context=this.container.querySelector("#caption-context")}render(){if(!(!this.headline||!this.context)){if(this.spoken){this.headline.textContent=this.spoken.text,this.headline.style.color=this.colorOf(this.spoken.level),this.context.textContent=this.state.join(" · ");return}if(this.state.length>0){this.headline.textContent=this.state[0],this.headline.style.color=F.text_primary,this.context.textContent=this.state.slice(1).join(" · ");return}if(this.last){this.headline.textContent=this.last.text,this.headline.style.color=this.colorOf(this.last.level),this.context.textContent="";return}this.headline.textContent="The dashboard is starting.",this.headline.style.color=F.text_primary,this.context.textContent=""}}colorOf(e){return nw[e]??F.text_primary}}const Sm=new iw;Kn.register(Sm);class sw{constructor(){T(this,"name","HUD");T(this,"panel",null);T(this,"modeChip",null);T(this,"connectionPill",null);T(this,"rows",new Map);T(this,"rowElements",new Map);T(this,"claimValue",null);T(this,"sourceValue",null);T(this,"statusData",{});T(this,"resources",{});T(this,"requiredSeeds",0);T(this,"measuredSeeds",0);T(this,"connected",!1);T(this,"animationTime",0);T(this,"onStatusUpdate",e=>{const t=(e==null?void 0:e.data)??e;t&&(this.statusData=t,this.updateQueueRows())});T(this,"onCampaignMetrics",e=>{const t=e==null?void 0:e.data;t&&Yn.observe(e==null?void 0:e.campaign_id,t)});T(this,"onRunChanged",(e,t)=>{var n;t&&(this.resources=t.resources??{},typeof t.required_seeds=="number"&&(this.requiredSeeds=t.required_seeds),this.measuredSeeds=this.resources.seeds_per_arm??((n=t.records)==null?void 0:n.length)??0,this.updateModeChip(t.run),this.updateSource(t.store),this.updateResourceRows(),this.updateClaim())});jt.register("status_update",this.onStatusUpdate),jt.register("campaign_metrics",this.onCampaignMetrics),Yn.onChange(this.onRunChanged)}async init(){this.createPanel(),this.createModeChip(),ir("hud","mission control","◱",()=>this.panel,Zi.hud),ia.onStateChange(e=>{this.connected=e==="connected",this.updateConnection()}),console.log("[HUD] Initialized")}async destroy(){var e,t;jt.unregister("status_update",this.onStatusUpdate),jt.unregister("campaign_metrics",this.onCampaignMetrics),(e=this.panel)==null||e.remove(),(t=this.modeChip)==null||t.remove()}createPanel(){const e=document.getElementById("ui-overlay");if(!e)return;this.panel=document.createElement("div"),this.panel.id="hud",this.panel.style.cssText=`
      position: fixed;
      top: 20px;
      right: 44px;
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
      <div id="hud-header" style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
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
      <div style="margin-top: 12px; padding-top: 10px; border-top: 1px solid var(--border);">
        <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 6px;">
          <span style="color: var(--text-secondary);">PICTURE</span>
          <span id="hud-source" style="font-weight: 600; color: ${F.text_secondary};">—</span>
        </div>
        <div id="hud-claim-row" style="display: flex; flex-direction: column; gap: 4px;">
          <div style="display: flex; justify-content: space-between; align-items: baseline;">
            <span style="color: var(--text-secondary);">SEEDS TO CLAIM</span>
            <span id="hud-claim" style="font-weight: 700; color: ${F.insufficient};">—</span>
          </div>
          <div style="height: 4px; background: var(--bg); border-radius: 2px; overflow: hidden;">
            <div id="hud-claim-fill" style="height: 100%; width: 0%; background: var(--insufficient); border-radius: 2px; transition: width var(--motion-normal) var(--ease-out), background-color var(--motion-fast);"></div>
          </div>
        </div>
      </div>
    `,e.appendChild(this.panel),this.panel.querySelector("#hud-header").appendChild(fa(()=>Sn.toggle("hud")));const n=this.panel.querySelector("#hud-meters");this.addMeter(n,"device","DEVICE",F.gradient),this.addMeter(n,"memory","MEMORY",F.memory),this.addMeter(n,"walltime","WALLTIME",F.cpu),this.addMeter(n,"gpu","GPU",F.gpu),this.addMeter(n,"cpu","CPU",F.cpu),this.addMeter(n,"records","RECORDS",F.promoted),this.claimValue=this.panel.querySelector("#hud-claim"),this.connectionPill=this.panel.querySelector("#hud-connection"),this.sourceValue=this.panel.querySelector("#hud-source")}addMeter(e,t,n,i){const r=document.createElement("div");r.style.cssText="display: flex; flex-direction: column; gap: 3px;",r.innerHTML=`
      <div style="display: flex; justify-content: space-between;">
        <span style="color: var(--text-secondary);">${n}</span>
        <span class="hud-value" style="color: var(--text-primary);">—</span>
      </div>
      <div style="height: 4px; background: var(--bg); border-radius: 2px; overflow: hidden;">
        <div class="hud-fill" style="height: 100%; width: 0%; background: ${i}; border-radius: 2px; transition: width 0.4s ease;"></div>
      </div>
    `,e.appendChild(r),this.rows.set(t,{key:t,label:n,value:"",fraction:0,color:i}),this.rowElements.set(t,{fill:r.querySelector(".hud-fill"),value:r.querySelector(".hud-value")})}createModeChip(){const e=document.getElementById("ui-overlay");e&&(this.modeChip=document.createElement("div"),this.modeChip.id="mode-chip",this.modeChip.style.cssText=`
      position: fixed;
      top: 20px;
      left: 20px;
      padding: 6px 14px;
      border-radius: 16px;
      background: ${F.text_muted}22;
      border: 1px solid ${F.text_muted}88;
      color: ${F.text_muted};
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
    `,e.appendChild(this.modeChip))}updateModeChip(e){if(!this.modeChip)return;const t=(e==null?void 0:e.mode)??"NO RUN",n=t==="PREREGISTERED"?F.passed:t==="EXPLORATORY"?F.insufficient:F.text_muted;this.modeChip.style.background=`${n}22`,this.modeChip.style.borderColor=`${n}88`,this.modeChip.style.color=n;const i=this.modeChip.querySelector(".mode-label");i&&(i.textContent=t);const r=this.modeChip.querySelector(".mode-detail");r&&(r.textContent=[e==null?void 0:e.profile,((e==null?void 0:e.tasks)??[]).join(", "),e==null?void 0:e.fidelity].filter(Boolean).join(" · ")),this.modeChip.title=e?`run ${e.run_id??"?"} · objectives: ${(e.objectives??[]).join(", ")||"none"}`:"No run has reported yet"}setMeter(e,t,n){const i=this.rows.get(e),r=this.rowElements.get(e);!i||!r||(i.value=t,i.fraction=Math.max(0,Math.min(1,n)),r.value.textContent=t,r.fill.style.width=`${(i.fraction*100).toFixed(1)}%`)}updateSource(e){if(!this.sourceValue)return;const t=e==null?void 0:e.source;if(!t){this.sourceValue.textContent="—",this.sourceValue.style.color=F.text_secondary;return}if(t==="snapshot"){const n=e!=null&&e.published_at?new Date(e.published_at).toLocaleTimeString():"";this.sourceValue.textContent=n?`snapshot ${n}`:"snapshot",this.sourceValue.style.color=F.insufficient,this.sourceValue.title="The writer published this copy; it is as fresh as its last publish.";return}this.sourceValue.textContent="live",this.sourceValue.style.color=F.passed,this.sourceValue.title="The store itself, read as it is written."}updateQueueRows(){const e=this.statusData;this.setMeter("gpu",e.max_gpus?`${e.used_gpus??0} / ${e.max_gpus}`:"—",e.max_gpus?(e.used_gpus??0)/e.max_gpus:0),this.setMeter("cpu",e.max_cpus?`${e.used_cpus??0} / ${e.max_cpus}`:"—",e.max_cpus?(e.used_cpus??0)/e.max_cpus:0)}updateResourceRows(){const e=this.resources;this.setMeter("device",e.device??"—",e.device?1:0),this.setMeter("memory",e.memory_mb!==void 0?`${e.memory_mb.toFixed(1)} MB`:"—",e.memory_mb!==void 0?Math.min(1,e.memory_mb/2048):0),this.setMeter("walltime",e.walltime_s!==void 0?`${e.walltime_s.toFixed(1)} s`:"—",e.walltime_s!==void 0?Math.min(1,e.walltime_s/120):0),this.setMeter("records",e.records!==void 0?`${e.records}`:"—",e.records!==void 0?Math.min(1,e.records/20):0)}updateClaim(){var i;if(!this.claimValue)return;const e=(i=this.panel)==null?void 0:i.querySelector("#hud-claim-fill");if(this.requiredSeeds<=0){this.claimValue.textContent="—",e&&(e.style.width="0%");return}const t=Math.max(0,this.requiredSeeds-this.measuredSeeds),n=this.requiredSeeds>0?this.measuredSeeds/this.requiredSeeds:0;this.claimValue.textContent=t>0?`${t} more (${this.requiredSeeds} needed)`:`Ready (${this.requiredSeeds} met)`,this.claimValue.style.color=t>0?F.insufficient:F.passed,e&&(e.style.width=`${Math.min(100,n*100)}%`,e.style.background=t>0?"var(--insufficient)":"var(--passed)")}updateConnection(){if(!this.connectionPill)return;const e=this.connectionPill.querySelector(".dot"),t=this.connectionPill.querySelector("span:last-child"),n=this.connected?F.ok:F.error;e.style.background=n,this.connectionPill.style.background=`${n}22`,this.connectionPill.style.borderColor=`${n}88`,this.connectionPill.style.color=n,t.textContent=this.connected?"live":"offline"}update(e){var n;this.animationTime+=e;const t=.5+.5*Math.sin(this.animationTime*2);(n=this.connectionPill)==null||n.style.setProperty("opacity",`${.75+.25*t}`)}}const pd=new sw;Kn.register(pd);const rw={space:{glyph:"▦",kind:"solid"},terrain:{glyph:"▲",kind:"solid"},frontier:{glyph:"◭",kind:"solid"},layers:{glyph:"▤",kind:"solid"},multirun:{glyph:"▣",kind:"solid"},matrix:{glyph:"▩",kind:"mark"},multiples:{glyph:"⊞",kind:"mark"},uncertainty:{glyph:"◌",kind:"mark"},ledger:{glyph:"☰",kind:"mark"},contrast:{glyph:"◐",kind:"mark"},basin:{glyph:"◡",kind:"mark"},"trained-basin":{glyph:"◠",kind:"mark"},cost:{glyph:"▮",kind:"bar"},flow:{glyph:"⇉",kind:"bar"},effect:{glyph:"▯",kind:"bar"},spread:{glyph:"▬",kind:"bar"},convergence:{glyph:"∿",kind:"curve"},timeline:{glyph:"↦",kind:"curve"},trajectory:{glyph:"⟿",kind:"curve"},spectrum:{glyph:"〜",kind:"curve"},landscape:{glyph:"∿",kind:"curve"},"trained-trajectory":{glyph:"⟿",kind:"curve"},"trained-spectrum":{glyph:"〜",kind:"curve"},"trained-landscape":{glyph:"∿",kind:"curve"},slices:{glyph:"⁙",kind:"mark"}};function aw(s){return rw[s]??{glyph:"•",kind:"mark"}}class ow{constructor(e){T(this,"canvas");T(this,"context");T(this,"visible",!1);this.canvas=document.createElement("canvas"),this.canvas.id=e,this.canvas.style.cssText=`
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      z-index: 50;
      display: none;
      background: var(--bg);
      pointer-events: none;
    `,document.body.appendChild(this.canvas),this.context=this.canvas.getContext("2d"),this.resize(),window.addEventListener("resize",()=>{this.resize()})}show(){this.visible=!0,this.canvas.style.display="block",this.resize(),this.begin()}hide(){this.visible=!1,this.canvas.style.display="none"}resize(){const e=Math.min(window.devicePixelRatio||1,2);this.canvas.width=Math.floor(window.innerWidth*e),this.canvas.height=Math.floor(window.innerHeight*e),this.context.setTransform(e,0,0,e,0,0)}begin(){const e=this.context;return e.clearRect(0,0,window.innerWidth,window.innerHeight),e.fillStyle="#0a0e14",e.fillRect(0,0,window.innerWidth,window.innerHeight),e}area(){const e=document.getElementById("discovery-legend"),t=e?e.getBoundingClientRect().right:0,n=Math.max(40,t+24),i=Math.max(200,window.innerWidth*Dp-n);return{x:n,y:70,width:i,height:Math.max(200,window.innerHeight*Ip-70)}}}const Ue=new ow("stage-2d"),bn={top:64,right:36,bottom:62,left:78};function xa(s,e,t,n){s.fillStyle=F.text_primary,s.font="600 22px 'JetBrains Mono', monospace",s.textAlign="left",s.textBaseline="alphabetic",s.fillText(t,e.x,e.y+14),n&&(s.fillStyle=F.text_secondary,s.font="13px 'JetBrains Mono', monospace",s.fillText(n,e.x,e.y+40))}function ca(s,e,t=5){if(!Number.isFinite(s)||!Number.isFinite(e))return[s];if(s===e)return[s];const i=(e-s)/Math.max(1,t),r=10**Math.floor(Math.log10(i)),a=i/r,o=(a>=5?10:a>=2?5:a>=1?2:1)*r,l=Math.ceil(s/o)*o,c=[];for(let h=l;h<=e+o*1e-6;h+=o)c.push(Number(h.toFixed(10)));return c}function ha(s){const e=Math.abs(s);return e===0?"0":e>=1e3||e>=10?s.toFixed(0):e>=1?s.toFixed(1):e>=.01?s.toFixed(2):s.toExponential(1)}function Cn(s,e){const t=e.xMax-e.xMin;return t===0?e.rect.x:e.rect.x+(s-e.xMin)/t*e.rect.width}function Kt(s,e){const t=e.yMax-e.yMin;return t===0?e.rect.y+e.rect.height:e.rect.y+e.rect.height-(s-e.yMin)/t*e.rect.height}function rs(s,e,t){const n={x:e.x+bn.left,y:e.y+bn.top,width:Math.max(40,e.width-bn.left-bn.right),height:Math.max(40,e.height-bn.top-bn.bottom)},i={rect:n,xMin:t.xMin,xMax:t.xMax,yMin:t.yMin,yMax:t.yMax};xa(s,e,t.title,t.subtitle);const r=t.xTicks??ca(t.xMin,t.xMax,6),a=t.yTicks??ca(t.yMin,t.yMax,5);return s.strokeStyle=F.border,s.lineWidth=1,s.beginPath(),s.rect(n.x,n.y,n.width,n.height),s.stroke(),s.font="12px 'JetBrains Mono', monospace",s.fillStyle=F.text_secondary,r.forEach(o=>{const l=Cn(o,i);l<n.x-1||l>n.x+n.width+1||(s.strokeStyle=F.border,s.beginPath(),s.moveTo(l,n.y),s.lineTo(l,n.y+n.height),s.stroke(),s.textAlign="center",s.fillText(ha(o),l,n.y+n.height+20))}),a.forEach(o=>{const l=Kt(o,i);l<n.y-1||l>n.y+n.height+1||(s.strokeStyle=F.border,s.beginPath(),s.moveTo(n.x,l),s.lineTo(n.x+n.width,l),s.stroke(),s.textAlign="right",s.fillText(ha(o),n.x-10,l+4))}),s.fillStyle=F.text_secondary,s.font="13px 'JetBrains Mono', monospace",s.textAlign="center",s.fillText(t.xLabel,n.x+n.width/2,n.y+n.height+46),s.save(),s.translate(n.x-56,n.y+n.height/2),s.rotate(-Math.PI/2),s.textAlign="center",s.fillText(t.yLabel,0,0),s.restore(),i}function Uh(s,e,t){const n=e.split(/\s+/).filter(a=>a.length>0),i=[];let r="";return n.forEach(a=>{const o=r?`${r} ${a}`:a;if(r&&s.measureText(o).width>t){i.push(r),r=a;return}r=o}),r&&i.push(r),i}function xn(s,e,t){s.fillStyle=F.text_secondary,s.font="12px 'JetBrains Mono', monospace",s.textAlign="left",s.textBaseline="alphabetic",s.fillText(t,e.x,e.y+e.height+40)}function Mm(s,e,t){const n={x:e.x+bn.left,y:e.y+bn.top,width:Math.max(40,e.width-bn.left-bn.right),height:Math.max(40,e.height-bn.top-bn.bottom)},i=n.width/Math.max(1,t.categories.length),r={rect:n,yMin:t.yMin,yMax:t.yMax,categories:t.categories,bandWidth:i,band:l=>n.x+i*(l+.5)},a={rect:n,yMin:t.yMin,yMax:t.yMax};return xa(s,e,t.title,t.subtitle),s.strokeStyle=F.border,s.lineWidth=1,s.strokeRect(n.x+.5,n.y+.5,n.width-1,n.height-1),s.font="12px 'JetBrains Mono', monospace",s.fillStyle=F.text_secondary,(t.yTicks??ca(t.yMin,t.yMax,5)).forEach(l=>{const c=Kt(l,a);c<n.y-1||c>n.y+n.height+1||(s.strokeStyle=F.border,s.beginPath(),s.moveTo(n.x,c),s.lineTo(n.x+n.width,c),s.stroke(),s.textAlign="right",s.fillText(ha(l),n.x-10,c+4))}),s.textAlign="center",s.textBaseline="top",t.categories.forEach((l,c)=>{sa(l,14).forEach((h,d)=>{s.fillText(h,r.band(c),n.y+n.height+12+d*16)})}),s.fillStyle=F.text_secondary,s.font="13px 'JetBrains Mono', monospace",s.save(),s.translate(n.x-56,n.y+n.height/2),s.rotate(-Math.PI/2),s.textAlign="center",s.textBaseline="alphabetic",s.fillText(t.yLabel,0,0),s.restore(),r}function Pl(s,e,t){s.font="12px 'JetBrains Mono', monospace";const n=t.rows.reduce((h,d)=>Math.max(h,s.measureText(d).width),0),i=Math.min(e.width*.45,Math.max(bn.left,n+24)),r={x:e.x+i,y:e.y+bn.top,width:Math.max(40,e.width-i-bn.right),height:Math.max(40,e.height-bn.top-bn.bottom)},a=r.height/Math.max(1,t.rows.length),o={rect:r,xMin:t.xMin,xMax:t.xMax,rows:t.rows,rowHeight:a,rowY:h=>r.y+a*(h+.5)},l={rect:r,xMin:t.xMin,xMax:t.xMax};return xa(s,e,t.title,t.subtitle),s.strokeStyle=F.border,s.lineWidth=1,s.strokeRect(r.x+.5,r.y+.5,r.width-1,r.height-1),s.font="12px 'JetBrains Mono', monospace",s.fillStyle=F.text_secondary,(t.xTicks??ca(t.xMin,t.xMax,6)).forEach(h=>{const d=Cn(h,l);d<r.x-1||d>r.x+r.width+1||(s.strokeStyle=F.border,s.beginPath(),s.moveTo(d,r.y),s.lineTo(d,r.y+r.height),s.stroke(),s.textAlign="center",s.textBaseline="alphabetic",s.fillText(ha(h),d,r.y+r.height+20))}),s.textAlign="right",s.textBaseline="middle",t.rows.forEach((h,d)=>{s.fillText(h,r.x-12,o.rowY(d))}),s.fillStyle=F.text_secondary,s.font="13px 'JetBrains Mono', monospace",s.textAlign="center",s.textBaseline="alphabetic",s.fillText(t.xLabel,r.x+r.width/2,r.y+r.height+46),o}class lw{constructor(){T(this,"id","cost");T(this,"name","The claim's cost");T(this,"caption","The seeds each cell measured, against the seeds a claim is measured against.");T(this,"visible",!1);T(this,"drawn",!1)}enter(){this.visible=!0,Ue.show(),this.draw()}exit(){this.visible=!1,Ue.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}costs(){const e=ve.axes,t=ve.requiredSeeds,n=Zh(ve.aggregates,e),i=bl(n,e);return n.map(r=>({cell:r,label:Za(r,e,i),color:Wt[r.coordinate.credit]??F.gradient,measured:r.seeds,required:t})).sort((r,a)=>a.required-a.measured-(r.required-r.measured))}draw(){const e=this.costs();if(e.length===0){this.drawn=!1;return}const t=Ue.begin(),n=Ue.area(),i=Math.max(ve.requiredSeeds,...e.map(c=>c.measured)),r=Pl(t,n,{xMin:0,xMax:i,rows:e.map(c=>c.label),title:"The claim's cost",subtitle:"the seeds measured, and the seeds a claim still needs",xLabel:"seeds"}),a=c=>r.rect.x+c/(r.xMax||1)*r.rect.width;e.forEach((c,h)=>{const d=r.rowY(h),u=Math.min(26,r.rowHeight*.5);t.fillStyle=F.bg_tertiary,t.fillRect(r.rect.x,d-u/2,a(c.required)-r.rect.x,u);const f=a(c.measured)-r.rect.x;t.fillStyle=c.color,t.fillRect(r.rect.x,d-u/2,f,u);const g=Math.max(0,c.required-c.measured);g>0&&(t.strokeStyle=F.warn,t.lineWidth=2,t.setLineDash([5,4]),t.beginPath(),t.moveTo(a(c.measured)+4,d),t.lineTo(a(c.required)-4,d),t.stroke(),t.setLineDash([])),t.strokeStyle=F.border,t.lineWidth=1,t.strokeRect(r.rect.x+.5,d-u/2,a(c.required)-r.rect.x-1,u-1),t.font="12px 'JetBrains Mono', monospace",t.textAlign="left",t.textBaseline="middle",t.fillStyle=F.text_secondary,t.fillText(`${c.measured} of ${c.required}`,r.rect.x+r.rect.width+12,d-8),g>0&&(t.fillStyle=F.warn,t.fillText(`${g} short`,r.rect.x+r.rect.width+12,d+9))});const o=a(ve.requiredSeeds);o>r.rect.x&&o<r.rect.x+r.rect.width&&(t.strokeStyle=F.text_secondary,t.lineWidth=1,t.setLineDash([3,4]),t.beginPath(),t.moveTo(o,r.rect.y),t.lineTo(o,r.rect.y+r.rect.height),t.stroke(),t.setLineDash([]));const l=e.reduce((c,h)=>c+Math.max(0,h.required-h.measured),0);xn(t,n,`the claim is ${l} seeds short over ${e.length} cells`),this.drawn=!0}}class cw{constructor(){T(this,"id","contrast");T(this,"name","The contrast");T(this,"caption","The run's arms against one another, and whether the test could be run.");T(this,"key","d");T(this,"visible",!1);T(this,"drawn",!1)}enter(){this.visible=!0,Ue.show(),this.draw()}exit(){this.visible=!1,Ue.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}draw(){var h,d,u;const e=(h=ve.account)==null?void 0:h.contrast;if(!e||e.pairs.length===0){this.drawn=!1;return}const t=new Map,n=new Map;e.arms.forEach(f=>{t.set(f.value,f.mean),n.set(f.value,f.sd)});const i=Math.max(...e.arms.map(f=>f.mean),.001),r=Ue.begin(),a=Ue.area(),o=Pl(r,a,{xMin:0,xMax:i*1.15,rows:e.pairs.map(f=>`${f.a} vs ${f.b}`),title:"The contrast",subtitle:`the ${e.axis} arms on ${e.metric}, and what separates them`,xLabel:e.metric}),l=f=>o.rect.x+f/(o.xMax||1)*o.rect.width;e.pairs.forEach((f,g)=>{const x=o.rowY(g),p=l(t.get(f.a)??0),m=l(t.get(f.b)??0);r.fillStyle=`${F.gradient}33`,r.fillRect(Math.min(p,m),x-11,Math.abs(m-p),22),r.strokeStyle=F.border_bright,r.lineWidth=2,r.beginPath(),r.moveTo(p,x),r.lineTo(m,x),r.stroke(),[f.a,f.b].forEach(_=>{const S=l(t.get(_)??0);n.get(_),r.strokeStyle=Wt[_]??F.gradient,r.lineWidth=1,r.beginPath(),r.moveTo(S,x-16),r.lineTo(S,x+16),r.stroke(),r.fillStyle=Wt[_]??F.gradient,r.beginPath(),r.arc(S,x,6,0,Math.PI*2),r.fill(),r.font="11px 'JetBrains Mono', monospace",r.textAlign="center",r.textBaseline="bottom",r.fillStyle=Wt[_]??F.gradient,r.fillText(_,S,x-18)}),r.font="12px 'JetBrains Mono', monospace",r.textAlign="left",r.textBaseline="middle",r.fillStyle=F.text_primary;const b=f.difference??0;r.fillText(`${b>=0?"+":"−"}${Math.abs(b).toFixed(3)}`,o.rect.x+o.rect.width+12,x-9),r.fillStyle=F.text_secondary,r.fillText(`${f.shared_cells} shared cell${f.shared_cells===1?"":"s"}`,o.rect.x+o.rect.width+12,x+9)});const c=e.test;xn(r,a,c.tested?`the test ran: p=${(d=c.p_value)==null?void 0:d.toFixed(4)} (alpha=${c.alpha}) · dz=${(u=c.cohens_dz)==null?void 0:u.toFixed(2)} · ${c.shared_cells} shared cells`:`no test ran: ${c.shared_cells} shared cell${c.shared_cells===1?"":"s"}, ${c.required_cells} required`),this.drawn=!0}}class hw{constructor(){T(this,"id","convergence");T(this,"name","Convergence");T(this,"caption","Accuracy against epoch, one curve per arm, with the chance level under them.");T(this,"visible",!1);T(this,"drawn",!1)}enter(){this.visible=!0,Ue.show(),this.draw()}exit(){this.visible=!1,Ue.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}curves(){var n;const e=((n=ve.metrics)==null?void 0:n.records)??[],t=new Map;return e.forEach(i=>{var l,c;const r=(l=i==null?void 0:i.payload)==null?void 0:l.convergence_curve;if(!Array.isArray(r)||r.length===0)return;const a=((c=i==null?void 0:i.coordinate)==null?void 0:c.credit)??"",o=t.get(a)??new Map;r.forEach(h=>{if(typeof(h==null?void 0:h.epoch)!="number"||typeof(h==null?void 0:h.val_acc)!="number")return;const d=o.get(h.epoch)??[];d.push(h.val_acc),o.set(h.epoch,d)}),t.set(a,o)}),Array.from(t.entries()).map(([i,r])=>({arm:i,points:Array.from(r.entries()).sort((a,o)=>a[0]-o[0]).map(([a,o])=>({epoch:a,val_acc:o.reduce((l,c)=>l+c,0)/o.length}))}))}draw(){const e=this.curves();if(e.length===0){this.drawn=!1;return}const t=Ue.begin(),n=Ue.area(),i=ve.chance,r=Math.max(...e.flatMap(h=>h.points.map(d=>d.epoch))),a=Math.max(i,...e.flatMap(h=>h.points.map(d=>d.val_acc))),o=rs(t,n,{xMin:0,xMax:r,yMin:0,yMax:a,xLabel:"epoch",yLabel:"accuracy",title:"Convergence",subtitle:"the mean accuracy of each arm, epoch by epoch",xTicks:void 0,yTicks:void 0}),l=Kt(i,o);t.strokeStyle=F.chance_line,t.lineWidth=1.5,t.setLineDash([6,5]),t.beginPath(),t.moveTo(o.rect.x,l),t.lineTo(o.rect.x+o.rect.width,l),t.stroke(),t.setLineDash([]),e.forEach(h=>{const d=Wt[h.arm]||F.gradient;t.strokeStyle=d,t.lineWidth=2.5,t.beginPath(),h.points.forEach((u,f)=>{const g=Cn(u.epoch,o),x=Kt(u.val_acc,o);f===0?t.moveTo(g,x):t.lineTo(g,x)}),t.stroke(),h.points.forEach(u=>{t.fillStyle=d,t.beginPath(),t.arc(Cn(u.epoch,o),Kt(u.val_acc,o),3,0,Math.PI*2),t.fill()})}),t.font="12px 'JetBrains Mono', monospace",t.textAlign="left",t.textBaseline="middle";let c=o.rect.y+10;e.forEach(h=>{const d=Wt[h.arm]||F.gradient;t.fillStyle=d,t.fillRect(o.rect.x+o.rect.width+18,c-5,10,10),t.fillStyle=F.text_secondary,t.fillText(h.arm,o.rect.x+o.rect.width+34,c),c+=20}),xn(t,n,`${e.length} arms · the dashed line is the chance level (${i.toFixed(2)})`),this.drawn=!0}}function md(s){const e=s.replace("#","");return[parseInt(e.slice(0,2),16),parseInt(e.slice(2,4),16),parseInt(e.slice(4,6),16)]}function kf(s){return`#${s.map(e=>Math.round(Math.max(0,Math.min(255,e))).toString(16).padStart(2,"0")).join("")}`}function Bf(s,e,t){return[s[0]+(e[0]-s[0])*t,s[1]+(e[1]-s[1])*t,s[2]+(e[2]-s[2])*t]}const dw=md(F.ramp_low),zf=md(F.ramp_mid),uw=md(F.ramp_high);function yi(s){const e=Math.max(0,Math.min(1,s));return e<=.5?kf(Bf(dw,zf,e*2)):kf(Bf(zf,uw,(e-.5)*2))}function Ll(){const s=ve.dynamics;return!s||!s.stateful?null:s}function fw(s){var t;const e=((t=s.cell)==null?void 0:t.coordinate)??{};return[e.geometry,e.dynamics,e.credit].filter(n=>typeof n=="string"&&n.length>0).join(" · ")}function Dl(s){var n;const e=[],t=fw(s);return t&&e.push(t),((n=s.cell)==null?void 0:n.measured_by_run)===!1&&e.push("a cell of the space, not one the run measured"),s.trained===!1&&e.push("the weights are untrained"),e.join(" · ")}class Il{constructor(){T(this,"key");T(this,"visible",!1);T(this,"drawn",!1)}enter(){this.visible=!0,Ue.show(),this.draw()}exit(){this.visible=!1,Ue.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}}class pw extends Il{constructor(){super(...arguments);T(this,"id","trajectory");T(this,"name","The trajectory");T(this,"caption","Where the cell's own state went, step by step: the path it took through the space it moves in.");T(this,"key","j")}draw(){const t=Ll(),n=t==null?void 0:t.trajectory;if(!t||!n||n.path.length<2){this.drawn=!1;return}const i=Ue.begin(),r=Ue.area(),a=n.path,o=a.map(_=>_[0]),l=a.map(_=>_[1]),c=.08,h=Math.min(...o),d=Math.max(...o),u=Math.min(...l),f=Math.max(...l),g=d-h||1,x=f-u||1,p=rs(i,r,{xMin:h-g*c,xMax:d+g*c,yMin:u-x*c,yMax:f+x*c,xLabel:n.axes[0]??"the direction the state moved",yLabel:n.axes[1]??"the direction across it",title:"The trajectory",subtitle:Dl(t)});for(let _=1;_<a.length;_+=1){const S=_/(a.length-1);i.strokeStyle=yi(S),i.lineWidth=2.5,i.beginPath(),i.moveTo(Cn(a[_-1][0],p),Kt(a[_-1][1],p)),i.lineTo(Cn(a[_][0],p),Kt(a[_][1],p)),i.stroke()}const m=(_,S,I)=>{const A=Cn(_[0],p),R=Kt(_[1],p);i.fillStyle=S,i.beginPath(),i.arc(A,R,5,0,Math.PI*2),i.fill(),i.font="12px 'JetBrains Mono', monospace",i.textAlign="left",i.textBaseline="middle",i.fillText(I,A+10,R)};m(a[0],F.text_primary,"where it started"),m(a[a.length-1],F.warn,"where it stopped");const b=n.error??[];if(b.length>1){const _=Math.min(...b),S=Math.max(...b),I=p.rect.height*.16,A=p.rect.y+p.rect.height-I*.5,R=N=>A-(N-_)/(S-_||1)*I*.5;i.strokeStyle=F.thermodynamic_contrast,i.lineWidth=1.5,i.beginPath(),b.forEach((N,M)=>{const y=p.rect.x+M/(b.length-1)*p.rect.width;M===0?i.moveTo(y,R(N)):i.lineTo(y,R(N))}),i.stroke(),i.font="11px 'JetBrains Mono', monospace",i.fillStyle=F.thermodynamic_contrast,i.textAlign="right",i.textBaseline="bottom",i.fillText("the prediction error",p.rect.x+p.rect.width,A-I*.6)}xn(i,r,t.verdict??""),this.drawn=!0}}class mw extends Il{constructor(){super(...arguments);T(this,"id","spectrum");T(this,"name","The spectrum");T(this,"caption","How fast a nudge grows along each direction: the exponents that say whether this dynamics settles.");T(this,"key","m")}draw(){const t=Ll(),n=t==null?void 0:t.spectrum;if(!t||!n||n.length===0){this.drawn=!1;return}const i=Ue.begin(),r=Ue.area(),o=Math.max(...n.map(d=>Math.abs(d)),1e-6)*1.25,l=rs(i,r,{xMin:0,xMax:n.length,yMin:-o,yMax:o,xLabel:"direction",yLabel:"growth per step",title:"The spectrum",subtitle:Dl(t),xTicks:ca(0,n.length,6).filter(d=>Number.isInteger(d))}),c=Kt(0,l);i.strokeStyle=F.text_muted,i.lineWidth=1.5,i.beginPath(),i.moveTo(l.rect.x,c),i.lineTo(l.rect.x+l.rect.width,c),i.stroke();const h=l.rect.width/n.length;n.forEach((d,u)=>{const f=l.rect.x+h*(u+.5),g=Math.min(46,h*.5),x=Kt(d,l),p=d>0;i.fillStyle=p?F.warn:F.ok,i.fillRect(f-g/2,Math.min(x,c),g,Math.abs(x-c)),i.font="11px 'JetBrains Mono', monospace",i.fillStyle=p?F.warn:F.ok,i.textAlign="center",i.textBaseline=p?"bottom":"top",i.fillText(ha(d),f,p?x-5:x+5)}),xn(i,r,t.verdict??""),this.drawn=!0}}class gw extends Il{constructor(){super(...arguments);T(this,"id","basin");T(this,"name","The basin");T(this,"caption","The states near the cell's own: how many come back, and how far the ones that do not stray.");T(this,"key","b")}draw(){const t=Ll(),n=t==null?void 0:t.basin;if(!t||!n||n.paths.length===0){this.drawn=!1;return}const i=Ue.begin(),r=Ue.area(),a=n.paths,o=Math.max(...a.flatMap(h=>h.distances),1e-6),l=rs(i,r,{xMin:0,xMax:a[0].distances.length,yMin:0,yMax:o*1.1,xLabel:"steps after the nudge",yLabel:"distance from the attractor",title:"The basin",subtitle:Dl(t)}),c=n.radii;a.forEach(h=>{const d=c.indexOf(h.radius),u=c.length>1?d/(c.length-1):.5;i.strokeStyle=h.returned?F.ok:yi(u),i.lineWidth=2,i.beginPath(),h.distances.forEach((f,g)=>{const x=Cn(g,l),p=Kt(f,l);g===0?i.moveTo(x,p):i.lineTo(x,p)}),i.stroke()}),i.font="12px 'JetBrains Mono', monospace",i.textAlign="center",i.textBaseline="top",n.stability.forEach((h,d)=>{const u=l.rect.x+l.rect.width/c.length*(d+.5);i.fillStyle=h>0?F.ok:F.warn,i.fillText(`${Math.round(h*100)}% back`,u,l.rect.y+12),i.fillStyle=F.text_secondary,i.fillText(`nudge ${c[d]}`,u,l.rect.y+28)}),xn(i,r,t.verdict??""),this.drawn=!0}}class xw extends Il{constructor(){super(...arguments);T(this,"id","landscape");T(this,"name","The landscape");T(this,"caption","The cell's own energy over the ground its trajectory crossed, and the path it took across it.");T(this,"key","n")}draw(){const t=Ll(),n=t==null?void 0:t.landscape,i=t==null?void 0:t.trajectory;if(!t||!n||n.grid.length===0){this.drawn=!1;return}const r=Ue.begin(),a=Ue.area(),o=n.grid,l=o.flat(),c=Math.min(...l),h=Math.max(...l),d=rs(r,a,{xMin:n.x[0],xMax:n.x[n.x.length-1],yMin:n.y[0],yMax:n.y[n.y.length-1],xLabel:"along the trajectory",yLabel:"across it",title:"The landscape",subtitle:Dl(t)}),u=d.rect.width/(n.x.length-1||1),f=d.rect.height/(n.y.length-1||1);r.save(),r.beginPath(),r.rect(d.rect.x,d.rect.y,d.rect.width,d.rect.height),r.clip(),o.forEach((_,S)=>{_.forEach((I,A)=>{const R=(I-c)/(h-c||1);r.fillStyle=yi(1-R);const N=d.rect.x+u*S,M=d.rect.y+d.rect.height-f*(A+1);r.fillRect(N,M,u+1,f+1)})}),r.restore(),i&&i.path.length>1&&(r.strokeStyle=F.text_primary,r.lineWidth=2,r.beginPath(),i.path.forEach((_,S)=>{const I=Cn(_[0],d),A=Kt(_[1],d);S===0?r.moveTo(I,A):r.lineTo(I,A)}),r.stroke());let g=0,x=0,p=Number.POSITIVE_INFINITY;o.forEach((_,S)=>_.forEach((I,A)=>{I<p&&(p=I,g=S,x=A)}));const m=Cn(n.x[g],d),b=Kt(n.y[x],d);r.strokeStyle=F.ok,r.lineWidth=2,r.beginPath(),r.arc(m,b,7,0,Math.PI*2),r.stroke(),r.font="12px 'JetBrains Mono', monospace",r.fillStyle=F.ok,r.textAlign="left",r.textBaseline="bottom",r.fillText("the lowest ground",m+11,b-6),xn(r,a,t.verdict??""),this.drawn=!0}}function Ul(){const s=ve.trainedDynamics;return!s||!s.stateful?null:s}function vw(s){var t;const e=((t=s.cell)==null?void 0:t.coordinate)??{};return[e.geometry,e.dynamics,e.credit].filter(n=>typeof n=="string"&&n.length>0).join(" · ")}function Nl(s){var n;const e=[],t=vw(s);return t&&e.push(t),((n=s.cell)==null?void 0:n.measured_by_run)===!1&&e.push("a cell of the space, not one the run measured"),s.trained===!0&&e.push("the weights were trained first"),e.join(" · ")}class Fl{constructor(){T(this,"key");T(this,"visible",!1);T(this,"drawn",!1)}enter(){this.visible=!0,Ue.show(),this.draw()}exit(){this.visible=!1,Ue.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}}class _w extends Fl{constructor(){super(...arguments);T(this,"id","trained-trajectory");T(this,"name","The trained trajectory");T(this,"caption","Where the trained cell's state went, step by step: the path it took through the space it moves in.");T(this,"key","g")}draw(){const t=Ul(),n=t==null?void 0:t.trajectory;if(!t||!n||n.path.length<2){this.drawn=!1;return}const i=Ue.begin(),r=Ue.area(),a=n.path,o=a.map(_=>_[0]),l=a.map(_=>_[1]),c=.08,h=Math.min(...o),d=Math.max(...o),u=Math.min(...l),f=Math.max(...l),g=d-h||1,x=f-u||1,p=rs(i,r,{xMin:h-g*c,xMax:d+g*c,yMin:u-x*c,yMax:f+x*c,xLabel:n.axes[0]??"the direction the state moved",yLabel:n.axes[1]??"the direction across it",title:"The trained trajectory",subtitle:Nl(t)});for(let _=1;_<a.length;_+=1){const S=_/(a.length-1);i.strokeStyle=yi(S),i.lineWidth=2.5,i.beginPath(),i.moveTo(Cn(a[_-1][0],p),Kt(a[_-1][1],p)),i.lineTo(Cn(a[_][0],p),Kt(a[_][1],p)),i.stroke()}const m=(_,S,I)=>{const A=Cn(_[0],p),R=Kt(_[1],p);i.fillStyle=S,i.beginPath(),i.arc(A,R,5,0,Math.PI*2),i.fill(),i.font="12px 'JetBrains Mono', monospace",i.textAlign="left",i.textBaseline="middle",i.fillText(I,A+10,R)};m(a[0],F.text_primary,"where it started"),m(a[a.length-1],F.warn,"where it stopped");const b=n.error??[];if(b.length>1){const _=Math.min(...b),S=Math.max(...b),I=p.rect.height*.16,A=p.rect.y+p.rect.height-I*.5,R=N=>A-(N-_)/(S-_||1)*I*.5;i.strokeStyle=F.thermodynamic_contrast,i.lineWidth=1.5,i.beginPath(),b.forEach((N,M)=>{const y=p.rect.x+M/(b.length-1)*p.rect.width;M===0?i.moveTo(y,R(N)):i.lineTo(y,R(N))}),i.stroke(),i.font="11px 'JetBrains Mono', monospace",i.fillStyle=F.thermodynamic_contrast,i.textAlign="right",i.textBaseline="bottom",i.fillText("the prediction error",p.rect.x+p.rect.width,A-I*.6)}xn(i,r,t.verdict??""),this.drawn=!0}}class yw extends Fl{constructor(){super(...arguments);T(this,"id","trained-spectrum");T(this,"name","The trained spectrum");T(this,"caption","How fast a nudge grows along each direction after training: the exponents that say whether this dynamics settles.");T(this,"key","i")}draw(){const t=Ul(),n=t==null?void 0:t.spectrum;if(!t||!n||n.length===0){this.drawn=!1;return}const i=Ue.begin(),r=Ue.area(),o=Math.max(...n.map(d=>Math.abs(d)),1e-6)*1.25,l=rs(i,r,{xMin:0,xMax:n.length,yMin:-o,yMax:o,xLabel:"direction",yLabel:"growth per step",title:"The trained spectrum",subtitle:Nl(t),xTicks:ca(0,n.length,6).filter(d=>Number.isInteger(d))}),c=Kt(0,l);i.strokeStyle=F.text_muted,i.lineWidth=1.5,i.beginPath(),i.moveTo(l.rect.x,c),i.lineTo(l.rect.x+l.rect.width,c),i.stroke();const h=l.rect.width/n.length;n.forEach((d,u)=>{const f=l.rect.x+h*(u+.5),g=Math.min(46,h*.5),x=Kt(d,l),p=d>0;i.fillStyle=p?F.warn:F.ok,i.fillRect(f-g/2,Math.min(x,c),g,Math.abs(x-c)),i.font="11px 'JetBrains Mono', monospace",i.fillStyle=p?F.warn:F.ok,i.textAlign="center",i.textBaseline=p?"bottom":"top",i.fillText(ha(d),f,p?x-5:x+5)}),xn(i,r,t.verdict??""),this.drawn=!0}}class bw extends Fl{constructor(){super(...arguments);T(this,"id","trained-basin");T(this,"name","The trained basin");T(this,"caption","The states near the trained cell's own: how many come back, and how far the ones that do not stray.");T(this,"key","k")}draw(){const t=Ul(),n=t==null?void 0:t.basin;if(!t||!n||n.paths.length===0){this.drawn=!1;return}const i=Ue.begin(),r=Ue.area(),a=n.paths,o=Math.max(...a.flatMap(h=>h.distances),1e-6),l=rs(i,r,{xMin:0,xMax:a[0].distances.length,yMin:0,yMax:o*1.1,xLabel:"steps after the nudge",yLabel:"distance from the attractor",title:"The trained basin",subtitle:Nl(t)}),c=n.radii;a.forEach(h=>{const d=c.indexOf(h.radius),u=c.length>1?d/(c.length-1):.5;i.strokeStyle=h.returned?F.ok:yi(u),i.lineWidth=2,i.beginPath(),h.distances.forEach((f,g)=>{const x=Cn(g,l),p=Kt(f,l);g===0?i.moveTo(x,p):i.lineTo(x,p)}),i.stroke()}),i.font="12px 'JetBrains Mono', monospace",i.textAlign="center",i.textBaseline="top",n.stability.forEach((h,d)=>{const u=l.rect.x+l.rect.width/c.length*(d+.5);i.fillStyle=h>0?F.ok:F.warn,i.fillText(`${Math.round(h*100)}% back`,u,l.rect.y+12),i.fillStyle=F.text_secondary,i.fillText(`nudge ${c[d]}`,u,l.rect.y+28)}),xn(i,r,t.verdict??""),this.drawn=!0}}class Sw extends Fl{constructor(){super(...arguments);T(this,"id","trained-landscape");T(this,"name","The trained landscape");T(this,"caption","The trained cell's own energy over the ground its trajectory crossed, and the path it took across it.");T(this,"key","o")}draw(){const t=Ul(),n=t==null?void 0:t.landscape,i=t==null?void 0:t.trajectory;if(!t||!n||n.grid.length===0){this.drawn=!1;return}const r=Ue.begin(),a=Ue.area(),o=n.grid,l=o.flat(),c=Math.min(...l),h=Math.max(...l),d=rs(r,a,{xMin:n.x[0],xMax:n.x[n.x.length-1],yMin:n.y[0],yMax:n.y[n.y.length-1],xLabel:"along the trajectory",yLabel:"across it",title:"The trained landscape",subtitle:Nl(t)}),u=d.rect.width/(n.x.length-1||1),f=d.rect.height/(n.y.length-1||1);r.save(),r.beginPath(),r.rect(d.rect.x,d.rect.y,d.rect.width,d.rect.height),r.clip(),o.forEach((_,S)=>{_.forEach((I,A)=>{const R=(I-c)/(h-c||1);r.fillStyle=yi(1-R);const N=d.rect.x+u*S,M=d.rect.y+d.rect.height-f*(A+1);r.fillRect(N,M,u+1,f+1)})}),r.restore(),i&&i.path.length>1&&(r.strokeStyle=F.text_primary,r.lineWidth=2,r.beginPath(),i.path.forEach((_,S)=>{const I=Cn(_[0],d),A=Kt(_[1],d);S===0?r.moveTo(I,A):r.lineTo(I,A)}),r.stroke());let g=0,x=0,p=Number.POSITIVE_INFINITY;o.forEach((_,S)=>_.forEach((I,A)=>{I<p&&(p=I,g=S,x=A)}));const m=Cn(n.x[g],d),b=Kt(n.y[x],d);r.strokeStyle=F.ok,r.lineWidth=2,r.beginPath(),r.arc(m,b,7,0,Math.PI*2),r.stroke(),r.font="12px 'JetBrains Mono', monospace",r.fillStyle=F.ok,r.textAlign="left",r.textBaseline="bottom",r.fillText("the lowest ground",m+11,b-6),xn(r,a,t.verdict??""),this.drawn=!0}}class Mw{constructor(){T(this,"id","effect");T(this,"name","The effect");T(this,"caption","Which axis moved the objective, and which the run held fixed: the run's attribution, and its limits.");T(this,"key","e");T(this,"visible",!1);T(this,"drawn",!1)}enter(){this.visible=!0,Ue.show(),this.draw()}exit(){this.visible=!1,Ue.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}draw(){const e=ve.attribution,t=(e==null?void 0:e.axes)??[];if(!e||t.length===0){this.drawn=!1;return}const n=Ue.begin(),i=Ue.area(),r=t.flatMap(c=>c.values.map(h=>h.mean)),a=Math.max(...r,.1),o=Mm(n,i,{yMin:0,yMax:a*1.15,categories:t.map(c=>c.axis),title:"The effect",subtitle:e.summary,yLabel:e.metric||"the objective"}),l=c=>o.rect.y+o.rect.height-c/(o.yMax||1)*o.rect.height;t.forEach((c,h)=>{const d=o.band(h),u=Math.min(46,o.bandWidth*.4);if(c.varied&&c.values.length>1){const x=Math.min(...c.values.map(S=>S.mean)),p=Math.max(...c.values.map(S=>S.mean)),m=l(p),b=l(x);n.fillStyle=`${F.gradient}33`,n.fillRect(d-u/2,m,u,b-m),n.strokeStyle=F.gradient,n.lineWidth=1,n.strokeRect(d-u/2,m,u,b-m);const _=[];c.values.forEach(S=>{const I=l(S.mean),A=Wt[S.value]??F.gradient;n.fillStyle=A,n.beginPath(),n.arc(d,I,5,0,Math.PI*2),n.fill();let R=I;for(;_.some(N=>Math.abs(N-R)<14);)R+=14;_.push(R),n.font="12px 'JetBrains Mono', monospace",n.textAlign="left",n.textBaseline="middle",n.fillStyle=A,n.fillText(S.value,d+u/2+10,R)});return}const f=c.values[0];if(!f)return;const g=l(f.mean);n.strokeStyle=F.text_muted,n.lineWidth=2,n.beginPath(),n.moveTo(d-7,g),n.lineTo(d+7,g),n.stroke(),n.font="12px 'JetBrains Mono', monospace",n.textAlign="center",n.textBaseline="top",n.fillStyle=F.text_muted,n.fillText(f.value,d,g+10)}),xn(n,i,e.reason),this.drawn=!0}}const ww=84,Ew=92;class Tw{constructor(){T(this,"id","flow");T(this,"name","The flow");T(this,"caption","The run's cells, stage by stage: what each one handled, and what the gate refused.");T(this,"key","f");T(this,"visible",!1);T(this,"drawn",!1)}enter(){this.visible=!0,Ue.show(),this.draw()}exit(){this.visible=!1,Ue.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}draw(){const e=ve.flow,t=(e==null?void 0:e.stages)??[];if(!e||t.length===0){this.drawn=!1;return}const n=Ue.begin(),i=Ue.area();xa(n,i,"The flow","the run's cells, from the space to the evidence");const r=i.y+i.height-Ew,a=Math.max(120,r-(i.y+ww)),o=Math.max(1,...t.map(c=>c.count+c.refused)),l=i.width/t.length;n.strokeStyle=F.border,n.lineWidth=1,n.beginPath(),n.moveTo(i.x,r+.5),n.lineTo(i.x+i.width,r+.5),n.stroke(),t.forEach((c,h)=>{const d=i.x+l*(h+.5),u=l*.56,f=p=>p/o*a,g=f(c.count),x=r-g;if(n.fillStyle=c.kind==="records"?F.measured:F.gradient,n.fillRect(d-u/2,x,u,Math.max(g,2)),c.refused>0){const p=f(c.refused);n.fillStyle=F.void,n.fillRect(d-u/2,x-p,u,p),n.font="12px 'JetBrains Mono', monospace",n.textAlign="center",n.textBaseline="bottom",n.fillStyle=F.void,n.fillText(`${c.refused} refused`,d,x-p-6)}c.count>0&&(n.font="600 15px 'JetBrains Mono', monospace",n.textAlign="center",n.textBaseline="bottom",n.fillStyle=F.text_primary,n.fillText(`${c.count}`,d,x-6)),n.font="12px 'JetBrains Mono', monospace",n.textAlign="center",n.textBaseline="top",n.fillStyle=c.count>0?F.text_secondary:F.text_muted,Uh(n,c.action,l-8).slice(0,2).forEach((p,m)=>{n.fillText(p,d,r+10+m*16)})}),this.drawRefusals(n,i),xn(n,i,e.summary),this.drawn=!0}drawRefusals(e,t){const n=ve.space,i=(n==null?void 0:n.void_rules)??{},r=Object.keys(i),a=t.x;if(e.textAlign="left",e.textBaseline="alphabetic",e.font="600 13px 'JetBrains Mono', monospace",e.fillStyle=F.text_secondary,e.fillText("the rules that refuse",a,t.y+80),r.length===0){e.font="12px 'JetBrains Mono', monospace",e.fillStyle=F.text_muted,e.fillText("no cell of this slice is refused",a,t.y+102);return}e.font="12px 'JetBrains Mono', monospace",r.slice(0,6).forEach((o,l)=>{const c=t.y+102+l*18;e.fillStyle=F.void,e.fillText(o,a,c),e.fillStyle=F.text_secondary,e.textAlign="right",e.fillText(`${i[o]} cells`,a+280,c),e.textAlign="left"})}}function Cs(s){s.traverse(e=>{var i;const t=e;(i=t.geometry)==null||i.dispose();const n=t.material;Array.isArray(n)?n.forEach(r=>r.dispose()):n==null||n.dispose()})}const Br=6.4,Oa=4,zr=5;class Aw{constructor(){T(this,"id","frontier");T(this,"name","Frontier");T(this,"caption","Every measured cell in accuracy, speed and parameters; the frontier is the line nothing beat.");T(this,"group",new ri);T(this,"visible",!1);T(this,"drawn",!1);T(this,"framed",!1);T(this,"accuracy",{min:0,max:0,span:0})}enter(){this.visible=!0;const e=Fi();e&&e.scene.add(this.group),this.draw(!0)}exit(){var e;this.visible=!1,(e=this.group.parent)==null||e.remove(this.group),Cs(this.group),this.group=new ri,this.drawn=!1,this.framed=!1}refresh(){this.visible&&this.draw(!1)}ready(){return this.drawn}points(){var d,u;const e=((d=ve.metrics)==null?void 0:d.records)??[],t=((u=ve.metrics)==null?void 0:u.pareto)??[],n=ve.chance,i=[],r=[],a=[];e.forEach(f=>{const g=(f==null?void 0:f.payload)??{};typeof g.val_acc=="number"&&i.push(g.val_acc),typeof g.walltime_s=="number"&&g.walltime_s>0&&r.push(1/g.walltime_s),typeof g.param_count=="number"&&g.param_count>0&&a.push(Math.log10(g.param_count))});const o=Oc([...i,n]);this.accuracy=o;const l=Oc(r),c=Oc(a),h=[];return e.forEach((f,g)=>{var b;const x=(f==null?void 0:f.payload)??{};if(typeof x.val_acc!="number")return;const p=typeof x.walltime_s=="number"&&x.walltime_s>0?1/x.walltime_s:null,m=typeof x.param_count=="number"&&x.param_count>0?Math.log10(x.param_count):null;h.push({x:p===null||l.span===0?0:((p-l.min)/l.span-.5)*Br,y:o.span===0?0:(x.val_acc-o.min)/o.span*Oa,z:m===null||c.span===0?0:((m-c.min)/c.span-.5)*zr,arm:((b=f==null?void 0:f.coordinate)==null?void 0:b.credit)??"",pareto:t[g]===!0})}),h}draw(e){const t=this.points();if(t.length===0){this.drawn=!1;return}this.clear(),this.addPoints(t),this.addFront(t),this.addChanceFloor(),this.addLabels(),this.drawn=!0,(e||!this.framed)&&(this.frame(),this.framed=!0)}clear(){[...this.group.children].forEach(e=>{this.group.remove(e),Cs(e)})}addPoints(e){const t=[],n=[];e.forEach(o=>{t.push(o.x,o.y,o.z);const l=new nt(Wt[o.arm]||F.gradient);n.push(l.r,l.g,l.b)});const i=new Jt;i.setAttribute("position",new It(t,3)),i.setAttribute("color",new It(n,3));const r=new Cp({size:.26,sizeAttenuation:!0,vertexColors:!0,map:Qb(),alphaTest:.4,transparent:!0,opacity:.95});this.group.add(new xb(i,r));const a=e.filter(o=>o.pareto);a.length!==0&&a.forEach(o=>{const l=eS(F.pareto,.26);l.position.set(o.x,o.y,o.z),this.group.add(l)})}addFront(e){const t=e.filter(a=>a.pareto).sort((a,o)=>a.y-o.y);if(t.length<2)return;const n=[];t.forEach(a=>n.push(a.x,a.y,a.z));const i=new Jt;i.setAttribute("position",new It(n,3));const r=new Ap(i,new _b({color:F.pareto,dashSize:.22,gapSize:.16,transparent:!0,opacity:.85}));r.computeLineDistances(),this.group.add(r)}addChanceFloor(){const e=ve.chance,t=this.accuracy;if(t.span===0)return;const n=(e-t.min)/t.span*Oa,i=new so(Br*1.02,zr*1.02);i.rotateX(-Math.PI/2);const r=new Xt(i,new es({color:F.chance_line,transparent:!0,opacity:.07,side:Nn,depthWrite:!1}));r.position.y=n,this.group.add(r);const a=mn("chance",.24,new Mi({color:F.chance_line,sizeAttenuation:!0}));a.position.set(Br/2+.3,n,zr/2+.3),this.group.add(a)}addLabels(){const e=new Mi({color:13227232,sizeAttenuation:!0}),t=mn("speed 1/s",.26,e);t.position.set(Br/2+.6,.1,0),this.group.add(t);const n=mn("accuracy",.26,e);n.position.set(0,Oa+.4,0),this.group.add(n);const i=mn("parameters",.26,e);i.position.set(0,.1,zr/2+.7),this.group.add(i)}frame(){const e=Fi();e&&ro(e,new V(-Br/2-.6,-.2,-zr/2-.6),new V(Br/2+.6,Oa+.6,zr/2+.6),new V(0,Oa/2,0))}}function Oc(s){const e=s.filter(i=>Number.isFinite(i));if(e.length===0)return{min:0,max:0,span:0};const t=Math.min(...e),n=Math.max(...e);return{min:t,max:n,span:n-t}}const ka=1.7,qn=1,Hf=.9,Cw=new V(.72,.24,.65);class Rw{constructor(){T(this,"id","layers");T(this,"name","Layers");T(this,"key","y");T(this,"caption","The space cut into sheets: the lit ones are the cells the run measured.");T(this,"group",new ri);T(this,"visible",!1);T(this,"drawn",!1);T(this,"framed",!1)}enter(){this.visible=!0;const e=Fi();e&&e.scene.add(this.group),this.draw(!0)}exit(){var e;this.visible=!1,(e=this.group.parent)==null||e.remove(this.group),Cs(this.group),this.group=new ri,this.drawn=!1,this.framed=!1}refresh(){this.visible&&this.draw(!1)}ready(){return this.drawn}sheets(){const e=ve.space;if(!e)return{sheets:[],nx:0,ny:0};const t=ve.axes,n=e.values[t.x]??[],i=e.values[t.y]??[],r=e.values[t.z]??[];return{sheets:r.map((o,l)=>{const c=[];let h=0;return n.forEach((d,u)=>{i.forEach((f,g)=>{const x=Si(d,f,o),p=ve.spaceCells.get(x),m=ve.aggregates.get(x),b=m&&m.acc.length>0?ts(m.acc):0;if((p==null?void 0:p.status)==="void"){c.push({status:"void",accuracy:0,arm:"",x:(u-(n.length-1)/2)*qn,y:(g-(i.length-1)/2)*qn});return}if(b>0){h+=1,c.push({status:"measured",accuracy:b,arm:(m==null?void 0:m.coordinate.credit)??"",x:(u-(n.length-1)/2)*qn,y:(g-(i.length-1)/2)*qn});return}c.push({status:"gap",accuracy:0,arm:"",x:(u-(n.length-1)/2)*qn,y:(g-(i.length-1)/2)*qn})})}),{value:o,height:(l-(r.length-1)/2)*ka,cells:c,measured:h}}),nx:n.length,ny:i.length}}draw(e){const{sheets:t,nx:n,ny:i}=this.sheets();if(t.length===0){this.drawn=!1;return}this.clear();const r=[],a=[],o=[],l=[];let c=0;t.forEach(d=>{d.cells.forEach(u=>{u.status==="measured"&&(c=Math.max(c,u.accuracy))})});const h=c>0?c:1;t.forEach(d=>{d.cells.forEach(u=>{const f=new nt(u.status==="measured"?Wt[u.arm]||F.gradient:u.status==="void"?F.void:F.border_bright);u.status==="measured"?f.multiplyScalar(.65+.35*(u.accuracy/h)):f.multiplyScalar(.3);const g=u.status==="measured"?o:r,x=u.status==="measured"?l:a,p=qn/2;g.push(u.x-p,d.height,u.y-p,u.x+p,d.height,u.y-p,u.x+p,d.height,u.y+p,u.x-p,d.height,u.y+p);for(let m=0;m<4;m+=1)x.push(f.r,f.g,f.b)})}),r.length>0&&this.group.add(new Xt(Vf(r,a),new es({vertexColors:!0,transparent:!0,opacity:.11,side:Nn,depthWrite:!1}))),o.length>0&&this.group.add(new Xt(Vf(o,l),new es({vertexColors:!0,side:Nn}))),this.addPins(t),this.addSheetEdges(t,n,i),this.addLabels(t,n,i),this.drawn=t.some(d=>d.measured>0),(e||!this.framed)&&(this.frame(t,n,i),this.framed=!0)}addPins(e){e.forEach(t=>{t.cells.forEach(n=>{if(n.status!=="measured")return;const i=new nt(Wt[n.arm]||F.gradient),r=new _i(.22,Hf,.22);r.translate(0,Hf/2,0);const a=new Kr({color:i,emissive:i,emissiveIntensity:.55,roughness:.4,metalness:.2}),o=new Xt(r,a);o.position.set(n.x,t.height,n.y),this.group.add(o)})})}addSheetEdges(e,t,n){const i=[],r=t*qn/2,a=n*qn/2;if(e.forEach(l=>{const c=[[-r,-a],[r,-a],[r,a],[-r,a]];c.forEach((h,d)=>{const u=c[(d+1)%c.length];i.push(h[0],l.height,h[1],u[0],l.height,u[1])})}),i.length===0)return;const o=new Jt;o.setAttribute("position",new It(i,3)),this.group.add(new jr(o,new Ms({color:F.border_bright,transparent:!0,opacity:.65})))}addLabels(e,t,n){const i=ve.axes,r=new Mi({color:13227232,sizeAttenuation:!0}),a=new Mi({color:9148584,sizeAttenuation:!0}),o=t*qn/2,l=n*qn/2;e.forEach(u=>{const f=mn(u.value,.26,a);f.position.set(-o-.85,u.height,l),this.group.add(f)});const c=mn(i.z,.28,r);c.position.set(-o-.85,e.length*ka*.5,-l),this.group.add(c);const h=mn(i.x,.28,r);h.position.set(o+.9,-ka,l),this.group.add(h);const d=mn(i.y,.28,r);d.position.set(o+.9,-ka,-l-.6),this.group.add(d)}frame(e,t,n){const i=Fi();if(!i||e.length===0)return;const r=t*qn/2,a=n*qn/2,o=e.length*ka/2;ro(i,new V(-r-1.4,-o-.4,-a-.6),new V(r+1.4,o+.4,a+.6),new V(0,0,0),Cw)}clear(){[...this.group.children].forEach(e=>{this.group.remove(e),Cs(e)})}}function Vf(s,e){const t=new Jt;return t.setAttribute("position",new It(s,3)),t.setAttribute("color",new It(e,3)),t}const Gf={PASSED:F.passed,INSUFFICIENT:F.insufficient,REJECTED:F.rejected};class Pw{constructor(){T(this,"id","ledger");T(this,"name","The ledger");T(this,"caption","Every arm the run measured, its evidence, and the gate's standing on it.");T(this,"key","l");T(this,"visible",!1);T(this,"drawn",!1)}enter(){this.visible=!0,Ue.show(),this.draw()}exit(){this.visible=!1,Ue.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}chip(e,t,n,i){const r=Gf[i]??F.text_secondary;e.font="11px 'JetBrains Mono', monospace";const a=e.measureText(i).width+18;e.fillStyle=`${r}22`,e.strokeStyle=`${r}88`,e.lineWidth=1,e.beginPath(),e.roundRect(t,n-9,a,18,9),e.fill(),e.stroke(),e.fillStyle=r,e.textAlign="center",e.textBaseline="middle",e.fillText(i,t+a/2,n)}standingBar(e,t,n,i,r,a){const o=Object.values(r).reduce((h,d)=>h+d,0);if(o===0)return;const l=18;let c=t;Object.entries(r).forEach(([h,d])=>{if(d<=0)return;const u=d/o*i;e.fillStyle=Gf[h]??F.text_secondary,e.fillRect(c,n,Math.max(2,u-2),l),u>52&&(e.fillStyle=F.bg,e.font="11px 'JetBrains Mono', monospace",e.textAlign="center",e.textBaseline="middle",e.fillText(`${d}`,c+(u-2)/2,n+l/2)),c+=u}),e.font="12px 'JetBrains Mono', monospace",e.textAlign="left",e.textBaseline="alphabetic",e.fillStyle=F.text_secondary,e.fillText(`${a} arm${a===1?"":"s"}, and where each one stands`,t,n-10)}draw(){var r;const e=(r=ve.account)==null?void 0:r.ledger;if(!e||e.claims.length===0){this.drawn=!1;return}const t=Ue.begin(),n=Ue.area();xa(t,n,"The ledger","every arm the run measured, its evidence, and the gate's standing on it");let i=n.y+96;this.standingBar(t,n.x,i,Math.min(560,n.width*.55),e.standings,e.claims.length),i+=66,e.claims.forEach(a=>{const o=Wt[a.value]??F.gradient;t.font="14px 'JetBrains Mono', monospace",t.textAlign="left",t.textBaseline="middle",t.fillStyle=o,t.fillText(`${a.axis} = ${a.value}`,n.x,i),t.font="13px 'JetBrains Mono', monospace",t.fillStyle=F.text_primary,t.fillText(`${a.mean.toFixed(3)} ± ${a.sd.toFixed(3)}`,n.x+300,i),t.font="12px 'JetBrains Mono', monospace",t.fillStyle=F.text_secondary,t.fillText(`${a.n} seeds · ${a.cells} cell${a.cells===1?"":"s"}`,n.x+460,i),this.chip(t,n.x+640,i,a.verdict),i+=42}),e.fixed.length>0&&(i+=22,t.font="600 14px 'JetBrains Mono', monospace",t.textAlign="left",t.textBaseline="alphabetic",t.fillStyle=F.text_primary,t.fillText("What was held fixed",n.x,i),i+=24,t.font="12px 'JetBrains Mono', monospace",e.fixed.forEach(a=>{t.textAlign="left",t.textBaseline="middle",t.fillStyle=F.text_secondary,t.fillText(`${a.axis} = ${a.value}`,n.x,i),t.fillText(`${a.mean.toFixed(3)}`,n.x+300,i),t.fillText(`${a.n} measurements · ${a.cells} cells`,n.x+460,i),i+=26})),i+=22,t.font="600 14px 'JetBrains Mono', monospace",t.textAlign="left",t.textBaseline="alphabetic",t.fillStyle=F.text_primary,t.fillText("What holds it back",n.x,i),i+=24,t.font="13px 'JetBrains Mono', monospace",e.limitations.forEach(a=>{Uh(t,`· ${a.detail}`,n.width).forEach(o=>{t.fillStyle=F.text_secondary,t.fillText(o,n.x,i),i+=20})}),e.significance&&(i+=14,Uh(t,`the report's test — ${e.significance}`,n.width).forEach(a=>{t.fillStyle=F.text_secondary,t.fillText(a,n.x,i),i+=20})),xn(t,n,`a claim needs ${e.min_seeds} seeds per cell`+(e.chance!==null?` · the chance level is ${e.chance.toFixed(3)}`:"")),this.drawn=!0}}class Lw{constructor(){T(this,"id","matrix");T(this,"name","Evidence matrix");T(this,"caption","The space seen from above: one axis against another, every column a number, the refusals in the void colour.");T(this,"visible",!1);T(this,"drawn",!1)}enter(){this.visible=!0,Ue.show(),this.draw()}exit(){this.visible=!1,Ue.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}columns(){const e=ve.space;if(!e)return{columns:[],xValues:[],yValues:[]};const t=ve.axes,n=e.values[t.x]??[],i=e.values[t.y]??[],r=e.values[t.z]??[],a=[];return n.forEach(o=>{i.forEach(l=>{let c=0,h=0,d=-1/0,u="";r.forEach(g=>{const x=Si(o,l,g),p=ve.spaceCells.get(x);if((p==null?void 0:p.status)==="void"){c+=1;return}h+=1;const m=ve.aggregates.get(x);if(!m||m.acc.length===0)return;const b=ts(m.acc);b>d&&(d=b,u=m.coordinate.credit??"")});const f=c>0&&h===0?"void":d>-1/0?"measured":"gap";a.push({status:f,accuracy:d>-1/0?d:0,arm:u})})}),{columns:a,xValues:n,yValues:i}}draw(){const{columns:e,xValues:t,yValues:n}=this.columns();if(e.length===0){this.drawn=!1;return}const i=Ue.begin(),r=Ue.area(),a=ve.axes,o=t.length,l=n.length,c=150,d={x:r.x+c,y:r.y+70,width:Math.max(80,r.width-c-40),height:Math.max(80,r.height-70-96)},u=d.width/o,f=d.height/l,g=Math.max(...e.map(A=>A.accuracy),1e-4);i.fillStyle=F.text_primary,i.font="600 22px 'JetBrains Mono', monospace",i.textAlign="left",i.textBaseline="alphabetic",i.fillText("Evidence matrix",r.x,r.y+14),i.fillStyle=F.text_secondary,i.font="13px 'JetBrains Mono', monospace",i.fillText(`${a.x} against ${a.y} — the best cell of each column`,r.x,r.y+40);let x=0,p=0,m=0;e.forEach((A,R)=>{const N=Math.floor(R/l),M=R%l,y=d.x+N*u,P=d.y+M*f;A.status==="void"?(m+=1,i.fillStyle=`${F.void}22`,i.fillRect(y,P,u,f),this.drawCross(i,y,P,u,f)):A.status==="gap"?(p+=1,i.fillStyle=F.bg_tertiary,i.fillRect(y,P,u,f)):(x+=1,i.fillStyle=yi(A.accuracy/g),i.fillRect(y,P,u,f),u>44&&f>26&&(i.fillStyle=Dw(A.accuracy/g),i.font="600 15px 'JetBrains Mono', monospace",i.textAlign="center",i.textBaseline="middle",i.fillText(A.accuracy.toFixed(2),y+u/2,P+f/2))),i.strokeStyle=F.bg,i.lineWidth=1,i.strokeRect(y+.5,P+.5,u-1,f-1)}),i.fillStyle=F.text_secondary,i.font="12px 'JetBrains Mono', monospace",t.forEach((A,R)=>{const N=sa(A,14);i.textAlign="center",i.textBaseline="top",N.forEach((M,y)=>{i.fillText(M,d.x+R*u+u/2,d.y+d.height+12+y*16)})}),n.forEach((A,R)=>{const N=sa(A,16);i.textAlign="right",i.textBaseline="middle",N.forEach((M,y)=>{i.fillText(M,d.x-12,d.y+R*f+f/2-(N.length-1)*8+y*16)})});const b=180,_=d.x+d.width-b,S=r.y+16,I=i.createLinearGradient(_,0,_+b,0);I.addColorStop(0,yi(0)),I.addColorStop(.5,yi(.5)),I.addColorStop(1,yi(1)),i.fillStyle=I,i.fillRect(_,S,b,12),i.strokeStyle=F.border,i.strokeRect(_+.5,S+.5,b-1,11),i.fillStyle=F.text_secondary,i.font="11px 'JetBrains Mono', monospace",i.textAlign="left",i.textBaseline="top",i.fillText("0",_,S+18),i.textAlign="right",i.fillText(g.toFixed(2),_+b,S+18),i.textAlign="left",i.fillText(`${x} measured · ${p} gaps · ${m} refused`,r.x,r.y+r.height+30),this.drawn=x>0}drawCross(e,t,n,i,r){const a=Math.min(i,r)*.28,o=t+i/2,l=n+r/2;e.strokeStyle=F.void,e.lineWidth=2,e.beginPath(),e.moveTo(o-a,l-a),e.lineTo(o+a,l+a),e.moveTo(o+a,l-a),e.lineTo(o-a,l+a),e.stroke()}}function Dw(s){return s>.62?F.bg:F.text_primary}const Jo=["#58a6ff","#d4a843","#3fb950","#f78166"],Bn=1.15,Ba=1,Iw=1.5,Uw=new V(.34,.4,.85);class Nw{constructor(){T(this,"id","multirun");T(this,"name","The multi-run space");T(this,"key","u");T(this,"caption","Several runs' evidence in one space: each run's cells stand in the run's own colour.");T(this,"group",new ri);T(this,"visible",!1);T(this,"drawn",!1);T(this,"framed",!1);T(this,"legend",null)}enter(){this.visible=!0;const e=Fi();e&&e.scene.add(this.group),this.load()}exit(){var t,n;this.visible=!1,(t=this.group.parent)==null||t.remove(this.group),Cs(this.group),this.group=new ri,this.drawn=!1,this.framed=!1,(n=this.legend)==null||n.remove(),this.legend=null;const e=document.getElementById("legend-arms-block");e&&(e.style.display="")}refresh(e){if(this.visible){if(e==="axes"){this.load();return}this.draw(!1)}}ready(){return this.drawn}async load(){await ve.syncMultirun(!0),this.visible&&this.draw(!0)}cells(e){const[t,n,i]=e.axes,r=e.values[t]??[],a=e.values[n]??[],o=e.values[i]??[],l=[],c=new Set;let h=1e-4;e.runs.forEach((p,m)=>{Object.entries(p.measured).forEach(([b,_])=>{const[S,I,A]=b.split("|"),R=r.indexOf(S),N=a.indexOf(I),M=o.indexOf(A);R<0||N<0||M<0||(l.push({xi:R,yi:N,zi:M,runIndex:m,accuracy:_.accuracy}),c.add(S),_.accuracy>h&&(h=_.accuracy))})});const d=new Map;l.forEach(p=>{const m=`${p.xi}|${p.yi}|${p.zi}`;d.set(m,(d.get(m)??0)+1)});const u=new Map,f=l.map(p=>{const m=`${p.xi}|${p.yi}|${p.zi}`,b=u.get(m)??0;u.set(m,b+1);const _=d.get(m)??1,S=(b-(_-1)/2)*(Ba*.5);return{x:(p.xi-(r.length-1)/2)*Bn+S,y:p.yi*Bn,z:(p.zi-(o.length-1)/2)*Bn,color:Jo[p.runIndex%Jo.length],height:p.accuracy/h*Iw}}),g=new Set;e.runs.forEach(p=>{const m=[t,n,i].map(_=>p.values[_]??[]),b=new Set(p.refused);r.forEach(_=>{m[0].includes(_)&&m[1].forEach(S=>{m[2].forEach(I=>{b.has(Si(_,S,I))||g.add(Si(_,S,I))})})})});const x=[];return r.forEach((p,m)=>{a.forEach((b,_)=>{o.forEach((S,I)=>{g.has(Si(p,b,S))&&x.push({x:(m-(r.length-1)/2)*Bn,y:_*Bn,z:(I-(o.length-1)/2)*Bn})})})}),{tiles:x,blocks:f,xValues:r,yValues:a,zValues:o,labelled:c}}draw(e){var c;const t=ve.multirun;if(!t||t.runs.length===0){this.drawn=!1,(c=this.legend)==null||c.remove(),this.legend=null;return}this.clear();const{tiles:n,blocks:i,xValues:r,yValues:a,zValues:o,labelled:l}=this.cells(t);this.addGround(n),this.addBlocks(i),this.addLabels(r,a.length,o.length,l),this.drawn=i.length>0,this.buildLegend(t),(e||!this.framed)&&(this.frame(r.length,a.length,o.length),this.framed=!0)}clear(){[...this.group.children].forEach(e=>{this.group.remove(e),Cs(e)})}addGround(e){if(e.length===0)return;const t=Ba/2,n=[],i=[];e.forEach((a,o)=>{n.push(a.x-t,a.y,a.z-t,a.x+t,a.y,a.z-t,a.x+t,a.y,a.z+t,a.x-t,a.y,a.z+t);const l=o*4;i.push(l,l+2,l+1,l,l+3,l+2)});const r=new Jt;r.setAttribute("position",new It(n,3)),r.setIndex(i),r.computeVertexNormals(),this.group.add(new Xt(r,new es({color:new nt(F.border),side:Nn})))}addBlocks(e){const t=new Map;e.forEach(n=>{const i=`${n.x}|${n.y}|${n.z}`,r=t.get(i)??0;t.set(i,r+1);const a=(r-(t.size-1)/2)*(Ba*.5),o=Math.max(n.height,.12),l=new _i(Ba*.45,o,Ba*.45);l.translate(0,o/2,0);const c=new Kr({color:new nt(n.color),emissive:new nt(n.color),emissiveIntensity:.45,transparent:!0,opacity:.95,metalness:.2,roughness:.4}),h=new Xt(l,c);h.position.set(n.x+a,n.y,n.z),this.group.add(h)})}addLabels(e,t,n,i){const r=new Mi({color:13227232,sizeAttenuation:!0}),a=new Mi({color:9148584,sizeAttenuation:!0}),o=(e.length-1)*Bn/2,l=(n-1)*Bn/2;e.forEach((p,m)=>{if(!i.has(p))return;const b=mn(p,.26,a,Bn*.9);b.position.set((m-(e.length-1)/2)*Bn,-.45,l+1.1),this.group.add(b)});const c=ve.multirun,[h,d,u]=(c==null?void 0:c.axes)??["","",""],f=mn(h,.24,r);f.position.set(o+1,-.4,l+1.1),this.group.add(f);const g=mn(u,.24,r);g.position.set(0,-.4,l+2),this.group.add(g);const x=mn(d,.24,r);x.position.set(-o-1.3,(t-1)*Bn*.5,0),this.group.add(x)}buildLegend(e){var o;const t=document.getElementById("discovery-legend");if(!t)return;(o=this.legend)==null||o.remove();const n=document.getElementById("legend-arms-block");n&&(n.style.display="none");const i=document.createElement("div");i.id="legend-runs",i.style.cssText="margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--border);";const r=document.createElement("div");r.textContent="Runs",r.style.cssText="font-weight: 600; margin-bottom: 8px;",i.appendChild(r),e.runs.forEach((l,c)=>{const h=Jo[c%Jo.length],d=Object.keys(l.measured).length,u=document.createElement("div");u.style.cssText="display: flex; align-items: center; gap: 8px; margin-bottom: 6px; font-size: 11px;";const f=document.createElement("span");f.style.cssText=`width: 14px; height: 14px; background: ${h}; border-radius: 3px;`;const g=document.createElement("span");g.style.color="var(--text-secondary)",g.textContent=`${l.profile??l.run_id.slice(0,8)} · ${d} cells · ${l.records} records`,u.appendChild(f),u.appendChild(g),i.appendChild(u)});const a=document.createElement("div");a.textContent=e.summary,a.style.cssText="font-size: 11px; color: var(--text-muted); margin-top: 6px;",i.appendChild(a),t.appendChild(i),this.legend=i}frame(e,t,n){const i=Fi();if(!i||e===0)return;const r=(e-1)*Bn/2+.6,a=(n-1)*Bn/2+.6,o=(t-1)*Bn+.8;ro(i,new V(-r,-.8,-a),new V(r,o,a+1.8),new V(0,o/3,0),Uw)}}const Fw=[{across:"x",down:"y",held:"z"},{across:"x",down:"z",held:"y"},{across:"y",down:"z",held:"x"}];class Ow{constructor(){T(this,"id","slices");T(this,"name","The slices");T(this,"key",",");T(this,"caption","The same space, cut three ways: three pairs of axes, side by side, so the space is not one picture.");T(this,"visible",!1);T(this,"drawn",!1)}enter(){this.visible=!0,Ue.show(),this.draw()}exit(){this.visible=!1,Ue.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}cut(e){const t=ve.space;if(!t)return{cells:[],across:[],down:[]};const n=ve.axes,i=t.values[n[e.across]]??[],r=t.values[n[e.down]]??[],a=t.values[n[e.held]]??[],o=[];return i.forEach(l=>{r.forEach(c=>{let h=0,d=0,u=-1/0;a.forEach(f=>{const g=this.keyOf(n,e,l,c,f),x=ve.spaceCells.get(g);if((x==null?void 0:x.status)==="void"){h+=1;return}d+=1;const p=ve.aggregates.get(g);!p||p.acc.length===0||(u=Math.max(u,ts(p.acc)))}),o.push({status:h>0&&d===0?"void":u>-1/0?"measured":"gap",accuracy:u>-1/0?u:0})})}),{cells:o,across:i,down:r}}keyOf(e,t,n,i,r){const a={x:"",y:"",z:""};return a[t.across]=n,a[t.down]=i,a[t.held]=r,Si(a.x,a.y,a.z)}draw(){if(!ve.space){this.drawn=!1;return}const t=Ue.begin(),n=Ue.area(),i=ve.axes;t.fillStyle=F.text_primary,t.font="600 22px 'JetBrains Mono', monospace",t.textAlign="left",t.textBaseline="alphabetic",t.fillText("The slices",n.x,n.y+14),t.fillStyle=F.text_secondary,t.font="13px 'JetBrains Mono', monospace",t.fillText("One space, three cuts: the axes a reader sees are a choice, and every choice hides an axis.",n.x,n.y+40);const r=28,a=(n.width-r*2)/3;let o=0,l=0,c=0;Fw.forEach((h,d)=>{const{cells:u,across:f,down:g}=this.cut(h),x=n.x+d*(a+r),p=n.y+70,m=96,_={x:x+m,y:p,width:Math.max(60,a-m-12),height:Math.max(60,n.height-70-54)},S=f.length?_.width/f.length:0,I=g.length?_.height/g.length:0,A=Math.max(...u.map(R=>R.accuracy),1e-4);t.fillStyle=F.text_primary,t.font="600 13px 'JetBrains Mono', monospace",t.textAlign="left",t.textBaseline="alphabetic",t.fillText(`${i[h.across]} × ${i[h.down]}`,x,p-12),t.fillStyle=F.text_muted,t.font="11px 'JetBrains Mono', monospace",t.fillText(`${i[h.held]} collapsed`,x,p-30),u.forEach((R,N)=>{const M=Math.floor(N/g.length),y=N%g.length,P=_.x+M*S,X=_.y+y*I;R.status==="void"?(c+=1,t.fillStyle=`${F.void}22`,t.fillRect(P,X,S,I)):R.status==="gap"?(l+=1,t.fillStyle=F.bg_tertiary,t.fillRect(P,X,S,I)):(o+=1,t.fillStyle=yi(R.accuracy/A),t.fillRect(P,X,S,I)),t.strokeStyle=F.bg,t.lineWidth=1,t.strokeRect(P+.5,X+.5,S-1,I-1)}),t.fillStyle=F.text_secondary,t.font="11px 'JetBrains Mono', monospace",f.forEach((R,N)=>{const M=sa(R,12);t.textAlign="center",t.textBaseline="top",M.forEach((y,P)=>{t.fillText(y,_.x+N*S+S/2,_.y+_.height+8+P*14)})}),g.forEach((R,N)=>{const M=sa(R,14);t.textAlign="right",t.textBaseline="middle",M.forEach((y,P)=>{t.fillText(y,_.x-8,_.y+N*I+I/2-(M.length-1)*7+P*14)})})}),t.fillStyle=F.text_secondary,t.font="12px 'JetBrains Mono', monospace",t.textAlign="left",t.textBaseline="alphabetic",t.fillText(`${o} measured · ${l} gaps · ${c} refused`,n.x,n.y+n.height+24),this.drawn=o>0}}class kw{constructor(){T(this,"id","multiples");T(this,"name","Small multiples");T(this,"caption","One panel per cell: every seed's own curve, on the same accuracy scale.");T(this,"visible",!1);T(this,"drawn",!1)}enter(){this.visible=!0,Ue.show(),this.draw()}exit(){this.visible=!1,Ue.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}panels(){const e=ve.axes,t=Zh(ve.aggregates,e),n=bl(t,e);return t.filter(i=>i.curves.length>0).map(i=>({cell:i,label:Za(i,e,n),color:Wt[i.coordinate.credit]??F.gradient,curves:i.curves}))}draw(){const e=this.panels();if(e.length===0){this.drawn=!1;return}const t=Ue.begin(),n=Ue.area(),i=ve.chance,r=e.flatMap(_=>_.curves.flatMap(S=>S.map(I=>I.val_acc))),a=e.flatMap(_=>_.curves.flatMap(S=>S.map(I=>I.epoch)));let o=Math.min(i,...r),l=Math.max(i,...r);l-o<1e-6&&(o-=.05,l+=.05);const c=(l-o)*.14;o-=c,l+=c;const h=Math.max(1,...a),d=Math.ceil(Math.sqrt(e.length)),u=Math.ceil(e.length/d),f=18,g=n.width-f*(d-1),x=n.height-64-44-f*(u-1),p=g/d,m=x/u;xa(t,n,"Small multiples","every seed of every cell, on one accuracy scale"),e.forEach((_,S)=>{const I=S%d,A=Math.floor(S/d),R=n.x+I*(p+f),N=n.y+64+A*(m+f);t.fillStyle=_.color,t.font="600 13px 'JetBrains Mono', monospace",t.textAlign="left",t.textBaseline="alphabetic",t.fillText(_.label,R,N+12);const M={x:R+(I===0?44:10),y:N+30,width:p-(I===0?54:20),height:m-56};t.strokeStyle=F.border,t.lineWidth=1,t.strokeRect(M.x+.5,M.y+.5,M.width-1,M.height-1);const y=M.y+M.height*(1-(i-o)/(l-o));t.strokeStyle=F.chance_line,t.lineWidth=1,t.setLineDash([4,4]),t.beginPath(),t.moveTo(M.x,y),t.lineTo(M.x+M.width,y),t.stroke(),t.setLineDash([]),_.curves.forEach(P=>{t.strokeStyle=_.color,t.lineWidth=1.8,t.beginPath(),P.forEach((X,H)=>{const J=M.x+X.epoch/h*M.width,q=M.y+M.height*(1-(X.val_acc-o)/(l-o));H===0?t.moveTo(J,q):t.lineTo(J,q)}),t.stroke()}),t.fillStyle=F.text_muted,t.font="9px 'JetBrains Mono', monospace",I===0&&(t.textAlign="right",t.textBaseline="middle",[l,(l+o)/2,o].forEach(P=>{const X=M.y+M.height*(1-(P-o)/(l-o));t.fillText(P.toFixed(2),M.x-6,X)})),A===u-1&&(t.textAlign="left",t.textBaseline="top",t.fillText("epoch 0",M.x,M.y+M.height+6),t.textAlign="right",t.fillText(`epoch ${h}`,M.x+M.width,M.y+M.height+6))});const b=e.reduce((_,S)=>_+S.curves.length,0);xn(t,n,`${e.length} cells · ${b} seeds · the dashed line is the chance level (${i.toFixed(2)})`),this.drawn=!0}}function Bw(s,e,t){let n=0;return s.forEach(i=>{const r=(e-i)/t;n+=Math.exp(-.5*r*r)}),n/(s.length*t*Math.sqrt(2*Math.PI))}function Wf(s){if(s.length<2)return .02;const e=s.reduce((r,a)=>r+a,0)/s.length,t=s.reduce((r,a)=>r+(a-e)**2,0)/(s.length-1),i=1.06*Math.sqrt(t)*s.length**-.2;return Math.max(i,.01)}class zw{constructor(){T(this,"id","spread");T(this,"name","The spread");T(this,"caption","One violin per arm, across its seeds: the width is the spread, not the mean.");T(this,"visible",!1);T(this,"drawn",!1)}enter(){this.visible=!0,Ue.show(),this.draw()}exit(){this.visible=!1,Ue.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}arms(){var n;const e=((n=ve.metrics)==null?void 0:n.records)??[],t=new Map;return e.forEach(i=>{var l,c;const r=(l=i==null?void 0:i.payload)==null?void 0:l.val_acc,a=(c=i==null?void 0:i.coordinate)==null?void 0:c.credit;if(typeof r!="number"||!a)return;const o=t.get(a)??[];o.push(r),t.set(a,o)}),Array.from(t.entries()).map(([i,r])=>({name:i,values:r.slice().sort((a,o)=>a-o),color:Wt[i]??F.gradient})).sort((i,r)=>i.name.localeCompare(r.name))}draw(){const e=this.arms();if(e.length===0){this.drawn=!1;return}const t=Ue.begin(),n=Ue.area(),i=ve.chance,r=ve.requiredSeeds,a=e.map(h=>{const d=Wf(h.values);return{high:h.values[h.values.length-1]+1.5*d,low:h.values[0]-1.5*d}}),o=Math.max(i,...a.map(h=>h.high))*1.03,l=Mm(t,n,{yMin:0,yMax:o,categories:e.map(h=>h.name),title:"The spread",subtitle:"every seed of every arm, as a distribution",yLabel:"accuracy"}),c=l.rect.y+l.rect.height*(1-i/l.yMax);t.strokeStyle=F.chance_line,t.lineWidth=1.5,t.setLineDash([6,5]),t.beginPath(),t.moveTo(l.rect.x,c),t.lineTo(l.rect.x+l.rect.width,c),t.stroke(),t.setLineDash([]),t.save(),t.beginPath(),t.rect(l.rect.x,l.rect.y,l.rect.width,l.rect.height),t.clip(),e.forEach((h,d)=>{const u=l.band(d),f=Math.min(l.bandWidth*.36,90),g=Wf(h.values),x=h.values[0]-1.5*g,p=h.values[h.values.length-1]+1.5*g,m=48,b=[];let _=0;for(let R=0;R<=m;R+=1){const N=x+(p-x)*R/m,M=Bw(h.values,N,g);b.push(M),_=Math.max(_,M)}const S=_>0?1/_:0,I=R=>l.rect.y+l.rect.height*(1-R/l.yMax);t.beginPath(),b.forEach((R,N)=>{const M=x+(p-x)*N/m,y=u+R*S*f,P=I(M);N===0?t.moveTo(y,P):t.lineTo(y,P)});for(let R=b.length-1;R>=0;R-=1){const N=x+(p-x)*R/m,M=u-b[R]*S*f;t.lineTo(M,I(N))}t.closePath(),t.fillStyle=`${h.color}33`,t.fill(),t.strokeStyle=h.color,t.lineWidth=1.5,t.stroke(),h.values.forEach((R,N)=>{const M=(N-(h.values.length-1)/2)*7;t.fillStyle=h.color,t.beginPath(),t.arc(u+M,I(R),3,0,Math.PI*2),t.fill()});const A=h.values.reduce((R,N)=>R+N,0)/h.values.length;t.strokeStyle=F.text_primary,t.lineWidth=1.5,t.beginPath(),t.moveTo(u-f,I(A)),t.lineTo(u+f,I(A)),t.stroke()}),t.restore(),e.forEach((h,d)=>{const u=Math.max(0,r-h.values.length);t.font="11px 'JetBrains Mono', monospace",t.textAlign="center",t.textBaseline="top",t.fillStyle=F.text_secondary,t.fillText(`${h.values.length} of ${r} seeds`,l.band(d),l.rect.y+l.rect.height+46),u>0&&(t.fillStyle=F.warn,t.fillText(`${u} short`,l.band(d),l.rect.y+l.rect.height+62))}),xn(t,n,`the white line is each arm's mean · a claim needs ${r} seeds per group`),this.drawn=!0}}const kc=3.4,Hr=1.15,Hw=new V(.34,.4,.85);class Vw{constructor(){T(this,"id","terrain");T(this,"name","Terrain");T(this,"caption","The space as a heightfield: accuracy is the height, the gaps are flat, the refusals are craters.");T(this,"group",new ri);T(this,"visible",!1);T(this,"drawn",!1);T(this,"framed",!1)}enter(){this.visible=!0;const e=Fi();e&&e.scene.add(this.group),this.draw(!0)}exit(){var e;this.visible=!1,(e=this.group.parent)==null||e.remove(this.group),Cs(this.group),this.group=new ri,this.drawn=!1,this.framed=!1}refresh(){this.visible&&this.draw(!1)}ready(){return this.drawn}columns(){const e=ve.space;if(!e)return{columns:[],xValues:[],yValues:[]};const t=ve.axes,n=e.values[t.x]??[],i=e.values[t.y]??[],r=e.values[t.z]??[],a=[];return n.forEach((o,l)=>{i.forEach((c,h)=>{let d=0,u=0,f=-1/0,g="";r.forEach(p=>{const m=Si(o,c,p),b=ve.spaceCells.get(m);if((b==null?void 0:b.status)==="void"){d+=1;return}u+=1;const _=ve.aggregates.get(m);if(!_||_.acc.length===0)return;const S=ts(_.acc);S>f&&(f=S,g=_.coordinate.credit??"")});const x=d>0&&u===0?"void":f>-1/0?"measured":"gap";a.push({status:x,accuracy:f>-1/0?f:0,arm:g,x:(l-(n.length-1)/2)*Hr,y:(h-(i.length-1)/2)*Hr})})}),{columns:a,xValues:n,yValues:i}}draw(e){const{columns:t,xValues:n,yValues:i}=this.columns();if(t.length===0){this.drawn=!1;return}this.clear();const r=Math.max(...t.map(f=>f.accuracy),1e-4),a=[],o=[],l=[];t.forEach(f=>{const g=f.status==="measured"?f.accuracy/r*kc:f.status==="void"?-1.1:0;a.push(f.x,g,f.y);const x=new nt(f.status==="measured"?Wt[f.arm]||F.gradient:f.status==="void"?F.void:F.border_bright);if(f.status==="measured"){const p=.6+.4*(f.accuracy/r);x.multiplyScalar(p)}else f.status==="void"&&x.multiplyScalar(.55);o.push(x.r,x.g,x.b)});const c=n.length,h=i.length;for(let f=0;f<c-1;f+=1)for(let g=0;g<h-1;g+=1){const x=f*h+g,p=(f+1)*h+g,m=(f+1)*h+g+1,b=f*h+g+1;l.push(x,b,p,p,b,m)}const d=new Jt;d.setAttribute("position",new It(a,3)),d.setAttribute("color",new It(o,3)),d.setIndex(l),d.computeVertexNormals();const u=new Xt(d,new Kr({vertexColors:!0,roughness:.7,metalness:.1,side:Nn}));this.group.add(u),this.addVoidMarkers(t),this.addLabels(n,i),this.drawn=t.some(f=>f.status==="measured"),(e||!this.framed)&&(this.frame(t,n,i),this.framed=!0)}clear(){[...this.group.children].forEach(e=>{this.group.remove(e),Cs(e)})}addVoidMarkers(e){const t=[];if(e.forEach(r=>{r.status==="void"&&t.push(r.x-.22,-1.1+.02,r.y-.22,r.x+.22,-1.1+.02,r.y+.22,r.x+.22,-1.1+.02,r.y-.22,r.x-.22,-1.1+.02,r.y+.22)}),t.length===0)return;const i=new Jt;i.setAttribute("position",new It(t,3)),this.group.add(new jr(i,new Ms({color:F.void,transparent:!0,opacity:.75})))}addLabels(e,t){const n=new Mi({color:13227232,sizeAttenuation:!0}),i=(e.length-1)*Hr/2,r=(t.length-1)*Hr/2,a=mn(ve.axes.x,.22,n);a.position.set(i+1,-.2,r+.9),this.group.add(a);const o=mn(ve.axes.y,.22,n);o.position.set(-i-1,.2,-r),this.group.add(o)}frame(e,t,n){const i=Fi();if(!i||e.length===0)return;const r=(t.length-1)*Hr/2,a=(n.length-1)*Hr/2;ro(i,new V(-r-1.2,-1.1-.3,-a),new V(r+1.2,kc,a+1.4),new V(0,kc/3,0),Hw)}}class Gw{constructor(){T(this,"id","timeline");T(this,"name","The timeline");T(this,"caption","The run's stages, in the order it reached them, and the time each held it.");T(this,"key","t");T(this,"visible",!1);T(this,"drawn",!1)}enter(){this.visible=!0,Ue.show(),this.draw()}exit(){this.visible=!1,Ue.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}draw(){const e=ve.timeline,t=(e==null?void 0:e.stages)??[];if(!e||t.length===0){this.drawn=!1;return}const n=Ue.begin(),i=Ue.area(),r=Math.max(e.seconds,.001),a=Pl(n,i,{xMin:0,xMax:r,rows:t.map(u=>u.action),title:"The timeline",subtitle:"the run's stages, and the time each of them held it",xLabel:"seconds"}),o=u=>a.rect.x+u/r*a.rect.width,l=new Map;e.events.forEach(u=>{const f=l.get(u.stage)??[];f.push(u.at-e.start),l.set(u.stage,f)});const c=t.slice(0,-1).map((u,f)=>{const g=t[f+1],x=(l.get(u.stage)??[]).filter(m=>m<=g.offset),p=x.length>0?x[x.length-1]:u.offset;return{index:f,from:p,to:g.offset,seconds:g.offset-p}}),h=c.reduce((u,f)=>f.seconds>u.seconds?f:u,{index:-1,from:0,to:0,seconds:0}),d=h.seconds>.5?h:null;if(d){const u=o(d.from),f=o(d.to);n.fillStyle=`${F.warn}18`,n.fillRect(u,a.rect.y,Math.max(2,f-u),a.rect.height)}c.forEach(u=>{const f=u.index===h.index;n.strokeStyle=f?F.warn:F.border,n.lineWidth=f?2:1,n.beginPath(),n.moveTo(o(u.from),a.rowY(u.index)),n.lineTo(o(u.to),a.rowY(u.index+1)),n.stroke()}),t.forEach((u,f)=>{const g=a.rowY(f);n.fillStyle=F.gradient,(l.get(u.stage)??[]).forEach(x=>{const p=o(x);n.fillRect(p-1.5,g-9,3,18)}),n.font="12px 'JetBrains Mono', monospace",n.textAlign="left",n.textBaseline="middle",n.fillStyle=F.text_secondary,n.fillText(`${u.events}`,a.rect.x+a.rect.width+12,g)}),d&&(n.font="13px 'JetBrains Mono', monospace",n.textAlign="center",n.textBaseline="alphabetic",n.fillStyle=F.warn,n.fillText(`${d.seconds.toFixed(1)} s of silence`,(o(d.from)+o(d.to))/2,a.rect.y+22)),xn(n,i,`${t.length} stages · ${e.events.length} events · ${r.toFixed(1)} s from the first word to the last`),this.drawn=!0}}class Ww{constructor(){T(this,"id","uncertainty");T(this,"name","The uncertainty");T(this,"caption","Each cell's mean and the margin the gate asks for, against the chance level.");T(this,"visible",!1);T(this,"drawn",!1)}enter(){this.visible=!0,Ue.show(),this.draw()}exit(){this.visible=!1,Ue.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}sigma(){const e=ve.gate;return e&&typeof e.superiority_margin_sigma=="number"?e.superiority_margin_sigma:2}intervals(){const e=ve.axes,t=ve.chance,n=this.sigma(),i=Zh(ve.aggregates,e),r=bl(i,e);return i.filter(a=>a.acc.length>0).map(a=>{const o=a.acc.length,l=a.acc.reduce((u,f)=>u+f,0)/o,c=a.acc.reduce((u,f)=>u+(f-l)**2,0)/Math.max(1,o-1),h=o>1?Math.sqrt(c/o):0,d=n*h;return{cell:a,label:Za(a,e,r),color:Wt[a.coordinate.credit]??F.gradient,mean:l,margin:d,lower:l-d,upper:l+d,threshold:t+d}}).sort((a,o)=>o.mean-a.mean)}draw(){const e=this.intervals();if(e.length===0){this.drawn=!1;return}const t=Ue.begin(),n=Ue.area(),i=ve.chance,r=this.sigma(),a=Math.max(i,...e.map(h=>Math.max(h.upper,h.threshold))),o=Pl(t,n,{xMin:0,xMax:a*1.12,rows:e.map(h=>h.label),title:"The uncertainty",subtitle:"each cell's mean, and the margin the gate asks for",xLabel:"accuracy"}),l=h=>o.rect.x+h/(o.xMax||1)*o.rect.width,c=l(i);t.strokeStyle=F.chance_line,t.lineWidth=1.5,t.setLineDash([6,5]),t.beginPath(),t.moveTo(c,o.rect.y),t.lineTo(c,o.rect.y+o.rect.height),t.stroke(),t.setLineDash([]),t.font="11px 'JetBrains Mono', monospace",t.textAlign="left",t.textBaseline="alphabetic",t.fillStyle=F.chance_line,t.fillText("chance",c+6,o.rect.y+14),e.forEach((h,d)=>{const u=o.rowY(d),f=h.lower>i;t.strokeStyle=h.color,t.lineWidth=3,t.beginPath(),t.moveTo(l(h.lower),u),t.lineTo(l(h.upper),u),t.stroke(),t.strokeStyle=f?F.ok:F.warn,t.lineWidth=2,t.beginPath(),t.moveTo(l(h.threshold),u-11),t.lineTo(l(h.threshold),u+11),t.stroke(),t.fillStyle=h.color,t.beginPath(),t.arc(l(h.mean),u,5,0,Math.PI*2),t.fill(),t.textAlign="left",t.textBaseline="middle",t.font="12px 'JetBrains Mono', monospace",t.fillStyle=f?F.ok:F.warn,t.fillText(f?"clears chance":"not yet separable",o.rect.x+o.rect.width+12,u)}),xn(t,n,`the bar is ±${r}·SE · the tick is the threshold each cell has to clear · a claim needs ${ve.requiredSeeds} seeds per cell`),this.drawn=!0}}class $w{constructor(){T(this,"id","space");T(this,"name","Space");T(this,"caption","The declared space: the gaps as cages, the measured cells as pillars, the refusals as crosses.")}enter(){Js.show()}exit(){Js.hide()}refresh(e){Js.refreshView(e)}ready(){return Js.hasMeasured()}}class qw{constructor(){T(this,"name","ViewSwitcher");T(this,"views",[]);T(this,"active",null);T(this,"track",null);T(this,"viewButtons",new Map);T(this,"captionElement",null);T(this,"section",null);T(this,"keys",new Map);T(this,"keyOf",new Map);T(this,"onKeyDown",e=>{if(e.metaKey||e.ctrlKey||e.altKey)return;const t=e.target;if(t&&["INPUT","SELECT","TEXTAREA"].includes(t.tagName))return;const n=e.key.toLowerCase();if(n===Jh){this.cycle();return}const i=this.keys.get(n);i&&this.show(i.id)});this.views=[new $w,new Vw,new Aw,new Lw,new hw,new kw,new zw,new lw,new Ww,new Gw,new Pw,new cw,new Tw,new Mw,new Rw,new pw,new mw,new gw,new xw,new _w,new yw,new bw,new Sw,new Nw,new Ow]}async init(){window.addEventListener("keydown",this.onKeyDown),ve.onChange(e=>{var t;return(t=this.active)==null?void 0:t.refresh(e)}),this.buildKeys(),this.buildSection(),this.attachSection(),this.show(this.views[0].id),console.log("[ViewSwitcher] Initialized")}async destroy(){var e,t;window.removeEventListener("keydown",this.onKeyDown),(e=this.active)==null||e.exit(),this.active=null,(t=this.section)==null||t.remove(),this.section=null}get activeId(){var e;return((e=this.active)==null?void 0:e.id)??null}isReady(e){const t=this.views.find(n=>n.id===e);return t?t.ready():!1}show(e){var n;const t=this.views.find(i=>i.id===e);!t||t===this.active||((n=this.active)==null||n.exit(),this.active=t,t.enter(),this.updateSelector(),this.updateLegend())}cycle(){if(this.views.length===0)return;const e=this.views.findIndex(n=>n===this.active),t=this.views[(e+1)%this.views.length];this.show(t.id)}buildKeys(){this.keys.clear(),this.keyOf.clear(),this.views.forEach((e,t)=>{const n=t<9?String(t+1):"";n&&(this.keys.set(n,e),this.keyOf.set(e.id,n)),e.key&&!Mh.has(e.key)&&(this.keys.set(e.key,e),this.keyOf.set(e.id,e.key))})}optionLabel(e){const t=this.keyOf.get(e.id);return t?`${t.toUpperCase()} · ${e.name}`:e.name}keyHint(){const e=[],t=[],n=[];this.views.forEach((r,a)=>{if(a<9){e.push(String(a+1));return}if(!(!r.key||Mh.has(r.key))){if(/^[a-z]$/.test(r.key)){t.push(r.key.toUpperCase());return}n.push(r.key)}});const i=["V cycles"];return e.length>0&&i.push(`${e[0]}–${e[e.length-1]} pick`),t.length>0&&i.push(`${t.join(" ")} pick`),n.length>0&&i.push(`${n.join(" ")} pick`),i.join(" · ")}buildSection(){const e=document.createElement("div");e.id="legend-view-section",e.style.cssText="margin-bottom: 12px;";const t=document.createElement("div");t.textContent="View",t.style.cssText="font-weight: 600; margin-bottom: 8px;",e.appendChild(t);const n=document.createElement("div");n.id="view-strip",n.style.cssText=`
      display: flex;
      align-items: center;
      gap: 4px;
      width: 100%;
    `,n.appendChild(this.stepButton("‹","the previous view",-1));const i=document.createElement("div");i.id="view-track",i.style.cssText=`
      display: flex;
      align-items: center;
      gap: 3px;
      flex: 1;
      overflow-x: auto;
      overflow-y: hidden;
      scrollbar-width: thin;
      padding-bottom: 2px;
    `;for(const o of this.views)i.appendChild(this.viewButton(o));n.appendChild(i),n.appendChild(this.stepButton("›","the next view",1)),e.appendChild(n),this.track=i;const r=document.createElement("div");r.id="view-caption",r.style.cssText="font-size: 11px; color: var(--text-secondary); margin-top: 8px;",e.appendChild(r),this.captionElement=r;const a=document.createElement("div");a.textContent=this.keyHint(),a.style.cssText="font-size: 10px; color: var(--text-muted); margin-top: 6px;",e.appendChild(a),this.section=e}viewButton(e){const t=aw(e.id),n=document.createElement("button");return n.className="view-button",n.dataset.view=e.id,n.textContent=t.glyph,n.title=this.optionLabel(e),n.style.cssText=`
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
    `,n.addEventListener("click",()=>this.show(e.id)),this.viewButtons.set(e.id,n),n}stepButton(e,t,n){const i=document.createElement("button");return i.className="view-step",i.textContent=e,i.title=t,i.style.cssText=`
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
    `,i.addEventListener("click",()=>this.step(n)),i}step(e){if(this.views.length===0)return;const t=this.views.findIndex(r=>{var a;return r.id===((a=this.active)==null?void 0:a.id)}),i=((t<0?0:t)+e+this.views.length)%this.views.length;this.show(this.views[i].id)}attachSection(e=0){const t=document.getElementById("legend-view");if(!t){e<50&&window.setTimeout(()=>this.attachSection(e+1),100);return}this.section&&this.section.parentElement!==t&&t.appendChild(this.section),this.updateSelector(),this.updateLegend()}updateSelector(){if(this.active){for(const[e,t]of this.viewButtons){const n=e===this.active.id;t.style.color=n?"var(--text-primary)":"var(--text-secondary)",t.style.borderColor=n?"var(--border-bright)":"var(--border)",t.style.background=n?"var(--bg-primary)":"var(--bg-tertiary)"}this.scrollToActive()}}scrollToActive(){const e=this.active?this.viewButtons.get(this.active.id):null;!e||!this.track||e.scrollIntoView({block:"nearest",inline:"nearest"})}updateLegend(){if(!this.active)return;const e=document.getElementById("legend-title");e&&(e.textContent=this.active.name);const t=document.getElementById("legend-marks");t&&(t.style.display=this.active.id==="space"?"":"none"),this.captionElement&&(this.captionElement.textContent=this.active.caption)}}const wm=new qw;Kn.register(wm);const Xw=[{title:"Navigation",items:[{key:Jh,description:"Cycle stage views"},{key:"Mouse drag",description:"Orbit camera"},{key:"Scroll",description:"Zoom camera"},{key:"Shift + drag",description:"Pan camera"}]},{title:"Panels",items:[{key:Zi.hud,description:"Toggle Mission Control (HUD)"},{key:Zi.rail,description:"Toggle Live Rail"},{key:Zi.caption,description:"Toggle Caption"},{key:Zi.legend,description:"Toggle Legend"},{key:Ui.panel,description:"Toggle Control Panel"}]},{title:"Charts",items:[{key:ws.pareto,description:"Show Pareto frontier"},{key:ws.ablation,description:"Show Ablation chart"},{key:ws.variability,description:"Show Variability chart"}]},{title:"Run Control",items:[{key:Ui.play,description:"Play / Pause run"},{key:Ui.step,description:"Step one batch"},{key:Ui.stop,description:"Stop run"}]},{title:"Cell Actions (click a cell first)",items:[{key:"R",description:"Replicate (queue remaining seeds)"},{key:"P",description:"Preregister (confirm protocol)"},{key:"Q",description:"Adopt as Quest (new run)"}]},{title:"General",items:[{key:"?",description:"Show this help"},{key:"Esc",description:"Close drawer / dismiss"}]}];class Yw{constructor(){T(this,"name","HelpOverlay");T(this,"container",null);T(this,"isOpen",!1);T(this,"onKeyDown",e=>{if(e.key==="?"&&!e.shiftKey&&!e.ctrlKey&&!e.metaKey&&!e.altKey){const t=e.target;if(t&&["INPUT","SELECT","TEXTAREA"].includes(t.tagName))return;e.preventDefault(),this.toggle()}e.key==="Escape"&&this.isOpen&&this.hide()});window.addEventListener("keydown",this.onKeyDown)}async init(){this.createOverlay(),console.log("[HelpOverlay] Initialized")}async destroy(){var e;window.removeEventListener("keydown",this.onKeyDown),(e=this.container)==null||e.remove()}createOverlay(){const e=document.getElementById("ui-overlay");if(!e)return;this.container=document.createElement("div"),this.container.id="help-overlay",this.container.style.cssText=`
      position: fixed;
      inset: 0;
      background: rgba(10, 14, 20, 0.92);
      z-index: 1000;
      display: none;
      align-items: center;
      justify-content: center;
      opacity: 0;
      transition: opacity 0.2s ease;
    `;const t=Xw.map(n=>`
      <div style="margin-bottom: 24px;">
        <div style="font-size: 11px; font-weight: 600; letter-spacing: 0.08em; color: var(--text-secondary); margin-bottom: 12px; text-transform: uppercase;">${n.title}</div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 8px;">
          ${n.items.map(i=>`
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
              ">${i.key}</kbd>
              <span style="font-size: 12px; color: var(--text-primary);">${i.description}</span>
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
          <h2 style="margin: 0; font-size: 18px; font-weight: 600; letter-spacing: 0.02em;">Keyboard Shortcuts</h2>
          <span style="font-size: 11px; color: var(--text-muted);">Press <kbd style="font-family: 'JetBrains Mono', monospace; padding: 1px 6px; background: var(--bg); border: 1px solid var(--border); border-radius: 3px;">?</kbd> again to close</span>
        </div>
        ${t}
      </div>
    `,e.appendChild(this.container),this.container.addEventListener("click",n=>{n.target===this.container&&this.hide()})}toggle(){this.isOpen?this.hide():this.show()}show(){this.container&&(this.container.style.display="flex",requestAnimationFrame(()=>{this.container.style.opacity="1";const e=this.container.querySelector("div");e&&(e.style.transform="scale(1)")}),this.isOpen=!0,document.body.style.overflow="hidden")}hide(){if(!this.container)return;this.container.style.opacity="0";const e=this.container.querySelector("div");e&&(e.style.transform="scale(0.95)"),setTimeout(()=>{this.container&&(this.container.style.display="none")},200),this.isOpen=!1,document.body.style.overflow=""}}const Em=new Yw;Kn.register(Em);const jw=/swiftshader|llvmpipe|software|basic render/i;function Kw(){const s=Jw();return{software:s,fps:s?12:60,shadows:!s,antialias:!s}}function Jw(){try{const s=document.createElement("canvas"),e=s.getContext("webgl2")??s.getContext("webgl");if(!e)return!0;const t=e.getExtension("WEBGL_debug_renderer_info"),n=String(t?e.getParameter(t.UNMASKED_RENDERER_WEBGL):e.getParameter(e.RENDERER));return jw.test(n)}catch{return!0}}window.addEventListener("error",s=>{var e;console.error("[Global Error]",s.error),Am(((e=s.error)==null?void 0:e.message)||"Unknown error")});window.addEventListener("unhandledrejection",s=>{var e;console.error("[Unhandled Rejection]",s.reason),Am(((e=s.reason)==null?void 0:e.message)||"Unhandled promise rejection")});let ji=null,xs=null;function Tm(s="Initializing dashboard..."){const e=document.getElementById("ui-overlay");e&&(ji=document.createElement("div"),ji.id="global-loading",ji.style.cssText=`
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
  `,ji.innerHTML=`
    <div style="
      width: 48px;
      height: 48px;
      border: 3px solid var(--border);
      border-top-color: ${F.gradient};
      border-radius: 50%;
      animation: spin 1s linear infinite;
    "></div>
    <div style="font-size: 14px; color: var(--text-primary);">${s}</div>
    <style>
      @keyframes spin { to { transform: rotate(360deg); } }
    </style>
  `,e.appendChild(ji))}function $f(){ji==null||ji.remove(),ji=null}function Am(s){const e=document.getElementById("ui-overlay");e&&(xs=document.createElement("div"),xs.id="global-error",xs.style.cssText=`
    position: fixed;
    top: 20px;
    right: 20px;
    background: ${F.error}22;
    border: 1px solid ${F.error}88;
    border-radius: 8px;
    padding: 16px 24px;
    color: ${F.error};
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    z-index: 1000;
    max-width: 400px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    display: flex;
    align-items: center;
    gap: 12px;
  `,xs.innerHTML=`
    <span>✗</span>
    <span>${s}</span>
    <button onclick="this.parentElement.remove()" style="
      background: none;
      border: none;
      color: ${F.error};
      font-size: 18px;
      cursor: pointer;
      line-height: 1;
      padding: 0 4px;
    ">&times;</button>
  `,e.appendChild(xs),setTimeout(()=>xs==null?void 0:xs.remove(),1e4))}ia.connect();Tm("Connecting to dashboard...");ia.waitForConnection(15e3).then(s=>{s?$f():(Tm("Connection timeout — retrying..."),ia.onStateChange(e=>{e==="connected"&&$f()}))});const Zw=new Map(Object.entries(ws).map(([s,e])=>[e,s]));window.addEventListener("keydown",s=>{if(s.metaKey||s.ctrlKey||s.altKey)return;const e=s.target;if(e&&["INPUT","SELECT","TEXTAREA"].includes(e.tagName))return;const t=s.key.toLowerCase(),n=Zw.get(t);if(n){fd.showTab(n);return}if(t===Ui.play){qa.togglePlay();return}if(t===Ui.step){qa.step();return}if(t===Ui.stop){qa.stop();return}if(t===Ui.panel){Sn.toggle("control-panel");return}const i=Sn.byKey(t);i&&Sn.toggle(i.id)});const Qw=document.getElementById("dashboard-canvas"),va=Kw(),ai=new mb({canvas:Qw,antialias:va.antialias,alpha:!0,powerPreference:"high-performance"});ai.setSize(window.innerWidth,window.innerHeight);ai.setPixelRatio(va.software?1:Math.min(window.devicePixelRatio,2));ai.shadowMap.enabled=va.shadows;ai.shadowMap.type=Xf;ai.toneMapping=jf;ai.toneMappingExposure=1.2;const as=new wp;as.background=new nt(658964);as.fog=new Xh(658964,.015);const Rs=new An(60,window.innerWidth/window.innerHeight,.1,200);Rs.position.set(3.3,4.4,8.8);Rs.lookAt(0,1,.1);const Oi=new Ub(Rs,ai.domElement);Oi.target.set(0,1,.1);Oi.enableDamping=!0;Oi.dampingFactor=.05;Oi.enablePan=!0;Oi.minDistance=5;Oi.maxDistance=80;Oi.maxPolarAngle=Math.PI/2-.05;Ob({scene:as,camera:Rs,renderer:ai,controls:Oi});const eE=new wb(4473958,.6);as.add(eE);const wi=new Mb(16777215,1.2);wi.position.set(10,20,10);wi.castShadow=va.shadows;wi.shadow.mapSize.width=2048;wi.shadow.mapSize.height=2048;wi.shadow.camera.near=1;wi.shadow.camera.far=50;wi.shadow.camera.left=-20;wi.shadow.camera.right=20;wi.shadow.camera.top=20;wi.shadow.camera.bottom=-20;as.add(wi);const tE=new yb(8956671,2236979,.5);as.add(tE);const gd=new Tb(8,8,2371648,1449256);gd.position.y=-.01;const Cm=gd.material;Cm.transparent=!0;Cm.opacity=.35;as.add(gd);function nE(){Rs.aspect=window.innerWidth/window.innerHeight,Rs.updateProjectionMatrix(),ai.setSize(window.innerWidth,window.innerHeight),ai.setPixelRatio(va.software?1:Math.min(window.devicePixelRatio,2))}window.addEventListener("resize",nE);const iE=1e3/va.fps;let Bc=0;function Rm(s){if(requestAnimationFrame(Rm),s-Bc<iE)return;const e=(s-Bc)/1e3;Bc=s,Oi.update(),Js.update(e),pd.update(e),ai.render(as,Rs)}requestAnimationFrame(Rm);window.__DASHBOARD__={scene:as,camera:Rs,renderer:ai,controls:Oi,discoveryMap:Js,cellDrawer:Up,plotter:fd,liveRail:bm,caption:Sm,hud:pd,helpOverlay:Em,viewSwitcher:wm,controlBar:qa,controlPanel:Lp,panels:Sn,wsClient:ia,router:jt};console.log("🚀 Computronium Dashboard initialized");
//# sourceMappingURL=dashboard.js.map
