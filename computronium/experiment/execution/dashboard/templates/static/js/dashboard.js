var Im=Object.defineProperty;var Um=(i,e,t)=>e in i?Im(i,e,{enumerable:!0,configurable:!0,writable:!0,value:t}):i[e]=t;var I=(i,e,t)=>Um(i,typeof e!="symbol"?e+"":e,t);/**
 * @license
 * Copyright 2010-2024 Three.js Authors
 * SPDX-License-Identifier: MIT
 */const Mh="168",lr={ROTATE:0,DOLLY:1,PAN:2},cr={ROTATE:0,PAN:1,DOLLY_PAN:2,DOLLY_ROTATE:3},Nm=0,Eu=1,Fm=2,Uf=1,Nf=2,Hi=3,gs=0,Nn=1,In=2,ds=0,Or=1,Tu=2,Au=3,Ru=4,Om=5,Os=100,Bm=101,zm=102,km=103,Hm=104,Vm=200,Gm=201,Wm=202,Xm=203,Ac=204,Rc=205,qm=206,$m=207,Ym=208,jm=209,Km=210,Zm=211,Jm=212,Qm=213,eg=214,tg=0,ng=1,ig=2,Yo=3,sg=4,rg=5,ag=6,og=7,Ff=0,lg=1,cg=2,fs=0,hg=1,ug=2,dg=3,Of=4,fg=5,pg=6,mg=7,Bf=300,Wr=301,Xr=302,Cc=303,Pc=304,ll=306,Lc=1e3,ks=1001,Dc=1002,ei=1003,gg=1004,io=1005,hi=1006,kl=1007,Hs=1008,Yi=1009,zf=1010,kf=1011,Fa=1012,Sh=1013,qs=1014,Gi=1015,Ga=1016,bh=1017,wh=1018,qr=1020,Hf=35902,Vf=1021,Gf=1022,fi=1023,Wf=1024,Xf=1025,Br=1026,$r=1027,qf=1028,Eh=1029,$f=1030,Th=1031,Ah=1033,ko=33776,Ho=33777,Vo=33778,Go=33779,Ic=35840,Uc=35841,Nc=35842,Fc=35843,Oc=36196,Bc=37492,zc=37496,kc=37808,Hc=37809,Vc=37810,Gc=37811,Wc=37812,Xc=37813,qc=37814,$c=37815,Yc=37816,jc=37817,Kc=37818,Zc=37819,Jc=37820,Qc=37821,Wo=36492,eh=36494,th=36495,Yf=36283,nh=36284,ih=36285,sh=36286,_g=3200,xg=3201,jf=0,vg=1,us="",bi="srgb",Ms="srgb-linear",Rh="display-p3",cl="display-p3-linear",jo="linear",Ot="srgb",Ko="rec709",Zo="p3",hr=7680,Cu=519,yg=512,Mg=513,Sg=514,Kf=515,bg=516,wg=517,Eg=518,Tg=519,rh=35044,Pu="300 es",Wi=2e3,Jo=2001;let ta=class{addEventListener(e,t){this._listeners===void 0&&(this._listeners={});const n=this._listeners;n[e]===void 0&&(n[e]=[]),n[e].indexOf(t)===-1&&n[e].push(t)}hasEventListener(e,t){if(this._listeners===void 0)return!1;const n=this._listeners;return n[e]!==void 0&&n[e].indexOf(t)!==-1}removeEventListener(e,t){if(this._listeners===void 0)return;const s=this._listeners[e];if(s!==void 0){const r=s.indexOf(t);r!==-1&&s.splice(r,1)}}dispatchEvent(e){if(this._listeners===void 0)return;const n=this._listeners[e.type];if(n!==void 0){e.target=this;const s=n.slice(0);for(let r=0,a=s.length;r<a;r++)s[r].call(this,e);e.target=null}}};const yn=["00","01","02","03","04","05","06","07","08","09","0a","0b","0c","0d","0e","0f","10","11","12","13","14","15","16","17","18","19","1a","1b","1c","1d","1e","1f","20","21","22","23","24","25","26","27","28","29","2a","2b","2c","2d","2e","2f","30","31","32","33","34","35","36","37","38","39","3a","3b","3c","3d","3e","3f","40","41","42","43","44","45","46","47","48","49","4a","4b","4c","4d","4e","4f","50","51","52","53","54","55","56","57","58","59","5a","5b","5c","5d","5e","5f","60","61","62","63","64","65","66","67","68","69","6a","6b","6c","6d","6e","6f","70","71","72","73","74","75","76","77","78","79","7a","7b","7c","7d","7e","7f","80","81","82","83","84","85","86","87","88","89","8a","8b","8c","8d","8e","8f","90","91","92","93","94","95","96","97","98","99","9a","9b","9c","9d","9e","9f","a0","a1","a2","a3","a4","a5","a6","a7","a8","a9","aa","ab","ac","ad","ae","af","b0","b1","b2","b3","b4","b5","b6","b7","b8","b9","ba","bb","bc","bd","be","bf","c0","c1","c2","c3","c4","c5","c6","c7","c8","c9","ca","cb","cc","cd","ce","cf","d0","d1","d2","d3","d4","d5","d6","d7","d8","d9","da","db","dc","dd","de","df","e0","e1","e2","e3","e4","e5","e6","e7","e8","e9","ea","eb","ec","ed","ee","ef","f0","f1","f2","f3","f4","f5","f6","f7","f8","f9","fa","fb","fc","fd","fe","ff"];let Lu=1234567;const zr=Math.PI/180,Oa=180/Math.PI;function Xi(){const i=Math.random()*4294967295|0,e=Math.random()*4294967295|0,t=Math.random()*4294967295|0,n=Math.random()*4294967295|0;return(yn[i&255]+yn[i>>8&255]+yn[i>>16&255]+yn[i>>24&255]+"-"+yn[e&255]+yn[e>>8&255]+"-"+yn[e>>16&15|64]+yn[e>>24&255]+"-"+yn[t&63|128]+yn[t>>8&255]+"-"+yn[t>>16&255]+yn[t>>24&255]+yn[n&255]+yn[n>>8&255]+yn[n>>16&255]+yn[n>>24&255]).toLowerCase()}function Sn(i,e,t){return Math.max(e,Math.min(t,i))}function Ch(i,e){return(i%e+e)%e}function Ag(i,e,t,n,s){return n+(i-e)*(s-n)/(t-e)}function Rg(i,e,t){return i!==e?(t-i)/(e-i):0}function Da(i,e,t){return(1-t)*i+t*e}function Cg(i,e,t,n){return Da(i,e,1-Math.exp(-t*n))}function Pg(i,e=1){return e-Math.abs(Ch(i,e*2)-e)}function Lg(i,e,t){return i<=e?0:i>=t?1:(i=(i-e)/(t-e),i*i*(3-2*i))}function Dg(i,e,t){return i<=e?0:i>=t?1:(i=(i-e)/(t-e),i*i*i*(i*(i*6-15)+10))}function Ig(i,e){return i+Math.floor(Math.random()*(e-i+1))}function Ug(i,e){return i+Math.random()*(e-i)}function Ng(i){return i*(.5-Math.random())}function Fg(i){i!==void 0&&(Lu=i);let e=Lu+=1831565813;return e=Math.imul(e^e>>>15,e|1),e^=e+Math.imul(e^e>>>7,e|61),((e^e>>>14)>>>0)/4294967296}function Og(i){return i*zr}function Bg(i){return i*Oa}function zg(i){return(i&i-1)===0&&i!==0}function kg(i){return Math.pow(2,Math.ceil(Math.log(i)/Math.LN2))}function Hg(i){return Math.pow(2,Math.floor(Math.log(i)/Math.LN2))}function Vg(i,e,t,n,s){const r=Math.cos,a=Math.sin,o=r(t/2),l=a(t/2),c=r((e+n)/2),h=a((e+n)/2),u=r((e-n)/2),d=a((e-n)/2),f=r((n-e)/2),g=a((n-e)/2);switch(s){case"XYX":i.set(o*h,l*u,l*d,o*c);break;case"YZY":i.set(l*d,o*h,l*u,o*c);break;case"ZXZ":i.set(l*u,l*d,o*h,o*c);break;case"XZX":i.set(o*h,l*g,l*f,o*c);break;case"YXY":i.set(l*f,o*h,l*g,o*c);break;case"ZYZ":i.set(l*g,l*f,o*h,o*c);break;default:console.warn("THREE.MathUtils: .setQuaternionFromProperEuler() encountered an unknown order: "+s)}}function ui(i,e){switch(e.constructor){case Float32Array:return i;case Uint32Array:return i/4294967295;case Uint16Array:return i/65535;case Uint8Array:return i/255;case Int32Array:return Math.max(i/2147483647,-1);case Int16Array:return Math.max(i/32767,-1);case Int8Array:return Math.max(i/127,-1);default:throw new Error("Invalid component type.")}}function Tt(i,e){switch(e.constructor){case Float32Array:return i;case Uint32Array:return Math.round(i*4294967295);case Uint16Array:return Math.round(i*65535);case Uint8Array:return Math.round(i*255);case Int32Array:return Math.round(i*2147483647);case Int16Array:return Math.round(i*32767);case Int8Array:return Math.round(i*127);default:throw new Error("Invalid component type.")}}const ah={DEG2RAD:zr,RAD2DEG:Oa,generateUUID:Xi,clamp:Sn,euclideanModulo:Ch,mapLinear:Ag,inverseLerp:Rg,lerp:Da,damp:Cg,pingpong:Pg,smoothstep:Lg,smootherstep:Dg,randInt:Ig,randFloat:Ug,randFloatSpread:Ng,seededRandom:Fg,degToRad:Og,radToDeg:Bg,isPowerOfTwo:zg,ceilPowerOfTwo:kg,floorPowerOfTwo:Hg,setQuaternionFromProperEuler:Vg,normalize:Tt,denormalize:ui};class $e{constructor(e=0,t=0){$e.prototype.isVector2=!0,this.x=e,this.y=t}get width(){return this.x}set width(e){this.x=e}get height(){return this.y}set height(e){this.y=e}set(e,t){return this.x=e,this.y=t,this}setScalar(e){return this.x=e,this.y=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y)}copy(e){return this.x=e.x,this.y=e.y,this}add(e){return this.x+=e.x,this.y+=e.y,this}addScalar(e){return this.x+=e,this.y+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this}subScalar(e){return this.x-=e,this.y-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this}multiply(e){return this.x*=e.x,this.y*=e.y,this}multiplyScalar(e){return this.x*=e,this.y*=e,this}divide(e){return this.x/=e.x,this.y/=e.y,this}divideScalar(e){return this.multiplyScalar(1/e)}applyMatrix3(e){const t=this.x,n=this.y,s=e.elements;return this.x=s[0]*t+s[3]*n+s[6],this.y=s[1]*t+s[4]*n+s[7],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this}negate(){return this.x=-this.x,this.y=-this.y,this}dot(e){return this.x*e.x+this.y*e.y}cross(e){return this.x*e.y-this.y*e.x}lengthSq(){return this.x*this.x+this.y*this.y}length(){return Math.sqrt(this.x*this.x+this.y*this.y)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)}normalize(){return this.divideScalar(this.length()||1)}angle(){return Math.atan2(-this.y,-this.x)+Math.PI}angleTo(e){const t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;const n=this.dot(e)/t;return Math.acos(Sn(n,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){const t=this.x-e.x,n=this.y-e.y;return t*t+n*n}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this}equals(e){return e.x===this.x&&e.y===this.y}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this}rotateAround(e,t){const n=Math.cos(t),s=Math.sin(t),r=this.x-e.x,a=this.y-e.y;return this.x=r*n-a*s+e.x,this.y=r*s+a*n+e.y,this}random(){return this.x=Math.random(),this.y=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y}}class at{constructor(e,t,n,s,r,a,o,l,c){at.prototype.isMatrix3=!0,this.elements=[1,0,0,0,1,0,0,0,1],e!==void 0&&this.set(e,t,n,s,r,a,o,l,c)}set(e,t,n,s,r,a,o,l,c){const h=this.elements;return h[0]=e,h[1]=s,h[2]=o,h[3]=t,h[4]=r,h[5]=l,h[6]=n,h[7]=a,h[8]=c,this}identity(){return this.set(1,0,0,0,1,0,0,0,1),this}copy(e){const t=this.elements,n=e.elements;return t[0]=n[0],t[1]=n[1],t[2]=n[2],t[3]=n[3],t[4]=n[4],t[5]=n[5],t[6]=n[6],t[7]=n[7],t[8]=n[8],this}extractBasis(e,t,n){return e.setFromMatrix3Column(this,0),t.setFromMatrix3Column(this,1),n.setFromMatrix3Column(this,2),this}setFromMatrix4(e){const t=e.elements;return this.set(t[0],t[4],t[8],t[1],t[5],t[9],t[2],t[6],t[10]),this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){const n=e.elements,s=t.elements,r=this.elements,a=n[0],o=n[3],l=n[6],c=n[1],h=n[4],u=n[7],d=n[2],f=n[5],g=n[8],_=s[0],p=s[3],m=s[6],M=s[1],v=s[4],b=s[7],N=s[2],A=s[5],R=s[8];return r[0]=a*_+o*M+l*N,r[3]=a*p+o*v+l*A,r[6]=a*m+o*b+l*R,r[1]=c*_+h*M+u*N,r[4]=c*p+h*v+u*A,r[7]=c*m+h*b+u*R,r[2]=d*_+f*M+g*N,r[5]=d*p+f*v+g*A,r[8]=d*m+f*b+g*R,this}multiplyScalar(e){const t=this.elements;return t[0]*=e,t[3]*=e,t[6]*=e,t[1]*=e,t[4]*=e,t[7]*=e,t[2]*=e,t[5]*=e,t[8]*=e,this}determinant(){const e=this.elements,t=e[0],n=e[1],s=e[2],r=e[3],a=e[4],o=e[5],l=e[6],c=e[7],h=e[8];return t*a*h-t*o*c-n*r*h+n*o*l+s*r*c-s*a*l}invert(){const e=this.elements,t=e[0],n=e[1],s=e[2],r=e[3],a=e[4],o=e[5],l=e[6],c=e[7],h=e[8],u=h*a-o*c,d=o*l-h*r,f=c*r-a*l,g=t*u+n*d+s*f;if(g===0)return this.set(0,0,0,0,0,0,0,0,0);const _=1/g;return e[0]=u*_,e[1]=(s*c-h*n)*_,e[2]=(o*n-s*a)*_,e[3]=d*_,e[4]=(h*t-s*l)*_,e[5]=(s*r-o*t)*_,e[6]=f*_,e[7]=(n*l-c*t)*_,e[8]=(a*t-n*r)*_,this}transpose(){let e;const t=this.elements;return e=t[1],t[1]=t[3],t[3]=e,e=t[2],t[2]=t[6],t[6]=e,e=t[5],t[5]=t[7],t[7]=e,this}getNormalMatrix(e){return this.setFromMatrix4(e).invert().transpose()}transposeIntoArray(e){const t=this.elements;return e[0]=t[0],e[1]=t[3],e[2]=t[6],e[3]=t[1],e[4]=t[4],e[5]=t[7],e[6]=t[2],e[7]=t[5],e[8]=t[8],this}setUvTransform(e,t,n,s,r,a,o){const l=Math.cos(r),c=Math.sin(r);return this.set(n*l,n*c,-n*(l*a+c*o)+a+e,-s*c,s*l,-s*(-c*a+l*o)+o+t,0,0,1),this}scale(e,t){return this.premultiply(Hl.makeScale(e,t)),this}rotate(e){return this.premultiply(Hl.makeRotation(-e)),this}translate(e,t){return this.premultiply(Hl.makeTranslation(e,t)),this}makeTranslation(e,t){return e.isVector2?this.set(1,0,e.x,0,1,e.y,0,0,1):this.set(1,0,e,0,1,t,0,0,1),this}makeRotation(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,-n,0,n,t,0,0,0,1),this}makeScale(e,t){return this.set(e,0,0,0,t,0,0,0,1),this}equals(e){const t=this.elements,n=e.elements;for(let s=0;s<9;s++)if(t[s]!==n[s])return!1;return!0}fromArray(e,t=0){for(let n=0;n<9;n++)this.elements[n]=e[n+t];return this}toArray(e=[],t=0){const n=this.elements;return e[t]=n[0],e[t+1]=n[1],e[t+2]=n[2],e[t+3]=n[3],e[t+4]=n[4],e[t+5]=n[5],e[t+6]=n[6],e[t+7]=n[7],e[t+8]=n[8],e}clone(){return new this.constructor().fromArray(this.elements)}}const Hl=new at;function Zf(i){for(let e=i.length-1;e>=0;--e)if(i[e]>=65535)return!0;return!1}function Qo(i){return document.createElementNS("http://www.w3.org/1999/xhtml",i)}function Gg(){const i=Qo("canvas");return i.style.display="block",i}const Du={};function kr(i){i in Du||(Du[i]=!0,console.warn(i))}function Wg(i,e,t){return new Promise(function(n,s){function r(){switch(i.clientWaitSync(e,i.SYNC_FLUSH_COMMANDS_BIT,0)){case i.WAIT_FAILED:s();break;case i.TIMEOUT_EXPIRED:setTimeout(r,t);break;default:n()}}setTimeout(r,t)})}const Iu=new at().set(.8224621,.177538,0,.0331941,.9668058,0,.0170827,.0723974,.9105199),Uu=new at().set(1.2249401,-.2249404,0,-.0420569,1.0420571,0,-.0196376,-.0786361,1.0982735),ma={[Ms]:{transfer:jo,primaries:Ko,luminanceCoefficients:[.2126,.7152,.0722],toReference:i=>i,fromReference:i=>i},[bi]:{transfer:Ot,primaries:Ko,luminanceCoefficients:[.2126,.7152,.0722],toReference:i=>i.convertSRGBToLinear(),fromReference:i=>i.convertLinearToSRGB()},[cl]:{transfer:jo,primaries:Zo,luminanceCoefficients:[.2289,.6917,.0793],toReference:i=>i.applyMatrix3(Uu),fromReference:i=>i.applyMatrix3(Iu)},[Rh]:{transfer:Ot,primaries:Zo,luminanceCoefficients:[.2289,.6917,.0793],toReference:i=>i.convertSRGBToLinear().applyMatrix3(Uu),fromReference:i=>i.applyMatrix3(Iu).convertLinearToSRGB()}},Xg=new Set([Ms,cl]),bt={enabled:!0,_workingColorSpace:Ms,get workingColorSpace(){return this._workingColorSpace},set workingColorSpace(i){if(!Xg.has(i))throw new Error(`Unsupported working color space, "${i}".`);this._workingColorSpace=i},convert:function(i,e,t){if(this.enabled===!1||e===t||!e||!t)return i;const n=ma[e].toReference,s=ma[t].fromReference;return s(n(i))},fromWorkingColorSpace:function(i,e){return this.convert(i,this._workingColorSpace,e)},toWorkingColorSpace:function(i,e){return this.convert(i,e,this._workingColorSpace)},getPrimaries:function(i){return ma[i].primaries},getTransfer:function(i){return i===us?jo:ma[i].transfer},getLuminanceCoefficients:function(i,e=this._workingColorSpace){return i.fromArray(ma[e].luminanceCoefficients)}};function Hr(i){return i<.04045?i*.0773993808:Math.pow(i*.9478672986+.0521327014,2.4)}function Vl(i){return i<.0031308?i*12.92:1.055*Math.pow(i,.41666)-.055}let ur;class qg{static getDataURL(e){if(/^data:/i.test(e.src)||typeof HTMLCanvasElement>"u")return e.src;let t;if(e instanceof HTMLCanvasElement)t=e;else{ur===void 0&&(ur=Qo("canvas")),ur.width=e.width,ur.height=e.height;const n=ur.getContext("2d");e instanceof ImageData?n.putImageData(e,0,0):n.drawImage(e,0,0,e.width,e.height),t=ur}return t.width>2048||t.height>2048?(console.warn("THREE.ImageUtils.getDataURL: Image converted to jpg for performance reasons",e),t.toDataURL("image/jpeg",.6)):t.toDataURL("image/png")}static sRGBToLinear(e){if(typeof HTMLImageElement<"u"&&e instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&e instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&e instanceof ImageBitmap){const t=Qo("canvas");t.width=e.width,t.height=e.height;const n=t.getContext("2d");n.drawImage(e,0,0,e.width,e.height);const s=n.getImageData(0,0,e.width,e.height),r=s.data;for(let a=0;a<r.length;a++)r[a]=Hr(r[a]/255)*255;return n.putImageData(s,0,0),t}else if(e.data){const t=e.data.slice(0);for(let n=0;n<t.length;n++)t instanceof Uint8Array||t instanceof Uint8ClampedArray?t[n]=Math.floor(Hr(t[n]/255)*255):t[n]=Hr(t[n]);return{data:t,width:e.width,height:e.height}}else return console.warn("THREE.ImageUtils.sRGBToLinear(): Unsupported image type. No color space conversion applied."),e}}let $g=0;class Jf{constructor(e=null){this.isSource=!0,Object.defineProperty(this,"id",{value:$g++}),this.uuid=Xi(),this.data=e,this.dataReady=!0,this.version=0}set needsUpdate(e){e===!0&&this.version++}toJSON(e){const t=e===void 0||typeof e=="string";if(!t&&e.images[this.uuid]!==void 0)return e.images[this.uuid];const n={uuid:this.uuid,url:""},s=this.data;if(s!==null){let r;if(Array.isArray(s)){r=[];for(let a=0,o=s.length;a<o;a++)s[a].isDataTexture?r.push(Gl(s[a].image)):r.push(Gl(s[a]))}else r=Gl(s);n.url=r}return t||(e.images[this.uuid]=n),n}}function Gl(i){return typeof HTMLImageElement<"u"&&i instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&i instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&i instanceof ImageBitmap?qg.getDataURL(i):i.data?{data:Array.from(i.data),width:i.width,height:i.height,type:i.data.constructor.name}:(console.warn("THREE.Texture: Unable to serialize Texture."),{})}let Yg=0;class Ln extends ta{constructor(e=Ln.DEFAULT_IMAGE,t=Ln.DEFAULT_MAPPING,n=ks,s=ks,r=hi,a=Hs,o=fi,l=Yi,c=Ln.DEFAULT_ANISOTROPY,h=us){super(),this.isTexture=!0,Object.defineProperty(this,"id",{value:Yg++}),this.uuid=Xi(),this.name="",this.source=new Jf(e),this.mipmaps=[],this.mapping=t,this.channel=0,this.wrapS=n,this.wrapT=s,this.magFilter=r,this.minFilter=a,this.anisotropy=c,this.format=o,this.internalFormat=null,this.type=l,this.offset=new $e(0,0),this.repeat=new $e(1,1),this.center=new $e(0,0),this.rotation=0,this.matrixAutoUpdate=!0,this.matrix=new at,this.generateMipmaps=!0,this.premultiplyAlpha=!1,this.flipY=!0,this.unpackAlignment=4,this.colorSpace=h,this.userData={},this.version=0,this.onUpdate=null,this.isRenderTargetTexture=!1,this.pmremVersion=0}get image(){return this.source.data}set image(e=null){this.source.data=e}updateMatrix(){this.matrix.setUvTransform(this.offset.x,this.offset.y,this.repeat.x,this.repeat.y,this.rotation,this.center.x,this.center.y)}clone(){return new this.constructor().copy(this)}copy(e){return this.name=e.name,this.source=e.source,this.mipmaps=e.mipmaps.slice(0),this.mapping=e.mapping,this.channel=e.channel,this.wrapS=e.wrapS,this.wrapT=e.wrapT,this.magFilter=e.magFilter,this.minFilter=e.minFilter,this.anisotropy=e.anisotropy,this.format=e.format,this.internalFormat=e.internalFormat,this.type=e.type,this.offset.copy(e.offset),this.repeat.copy(e.repeat),this.center.copy(e.center),this.rotation=e.rotation,this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrix.copy(e.matrix),this.generateMipmaps=e.generateMipmaps,this.premultiplyAlpha=e.premultiplyAlpha,this.flipY=e.flipY,this.unpackAlignment=e.unpackAlignment,this.colorSpace=e.colorSpace,this.userData=JSON.parse(JSON.stringify(e.userData)),this.needsUpdate=!0,this}toJSON(e){const t=e===void 0||typeof e=="string";if(!t&&e.textures[this.uuid]!==void 0)return e.textures[this.uuid];const n={metadata:{version:4.6,type:"Texture",generator:"Texture.toJSON"},uuid:this.uuid,name:this.name,image:this.source.toJSON(e).uuid,mapping:this.mapping,channel:this.channel,repeat:[this.repeat.x,this.repeat.y],offset:[this.offset.x,this.offset.y],center:[this.center.x,this.center.y],rotation:this.rotation,wrap:[this.wrapS,this.wrapT],format:this.format,internalFormat:this.internalFormat,type:this.type,colorSpace:this.colorSpace,minFilter:this.minFilter,magFilter:this.magFilter,anisotropy:this.anisotropy,flipY:this.flipY,generateMipmaps:this.generateMipmaps,premultiplyAlpha:this.premultiplyAlpha,unpackAlignment:this.unpackAlignment};return Object.keys(this.userData).length>0&&(n.userData=this.userData),t||(e.textures[this.uuid]=n),n}dispose(){this.dispatchEvent({type:"dispose"})}transformUv(e){if(this.mapping!==Bf)return e;if(e.applyMatrix3(this.matrix),e.x<0||e.x>1)switch(this.wrapS){case Lc:e.x=e.x-Math.floor(e.x);break;case ks:e.x=e.x<0?0:1;break;case Dc:Math.abs(Math.floor(e.x)%2)===1?e.x=Math.ceil(e.x)-e.x:e.x=e.x-Math.floor(e.x);break}if(e.y<0||e.y>1)switch(this.wrapT){case Lc:e.y=e.y-Math.floor(e.y);break;case ks:e.y=e.y<0?0:1;break;case Dc:Math.abs(Math.floor(e.y)%2)===1?e.y=Math.ceil(e.y)-e.y:e.y=e.y-Math.floor(e.y);break}return this.flipY&&(e.y=1-e.y),e}set needsUpdate(e){e===!0&&(this.version++,this.source.needsUpdate=!0)}set needsPMREMUpdate(e){e===!0&&this.pmremVersion++}}Ln.DEFAULT_IMAGE=null;Ln.DEFAULT_MAPPING=Bf;Ln.DEFAULT_ANISOTROPY=1;class sn{constructor(e=0,t=0,n=0,s=1){sn.prototype.isVector4=!0,this.x=e,this.y=t,this.z=n,this.w=s}get width(){return this.z}set width(e){this.z=e}get height(){return this.w}set height(e){this.w=e}set(e,t,n,s){return this.x=e,this.y=t,this.z=n,this.w=s,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this.w=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setW(e){return this.w=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;case 3:this.w=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;case 3:return this.w;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z,this.w)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this.w=e.w!==void 0?e.w:1,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this.w+=e.w,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this.w+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this.w=e.w+t.w,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this.w+=e.w*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this.w-=e.w,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this.w-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this.w=e.w-t.w,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this.w*=e.w,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this.w*=e,this}applyMatrix4(e){const t=this.x,n=this.y,s=this.z,r=this.w,a=e.elements;return this.x=a[0]*t+a[4]*n+a[8]*s+a[12]*r,this.y=a[1]*t+a[5]*n+a[9]*s+a[13]*r,this.z=a[2]*t+a[6]*n+a[10]*s+a[14]*r,this.w=a[3]*t+a[7]*n+a[11]*s+a[15]*r,this}divideScalar(e){return this.multiplyScalar(1/e)}setAxisAngleFromQuaternion(e){this.w=2*Math.acos(e.w);const t=Math.sqrt(1-e.w*e.w);return t<1e-4?(this.x=1,this.y=0,this.z=0):(this.x=e.x/t,this.y=e.y/t,this.z=e.z/t),this}setAxisAngleFromRotationMatrix(e){let t,n,s,r;const l=e.elements,c=l[0],h=l[4],u=l[8],d=l[1],f=l[5],g=l[9],_=l[2],p=l[6],m=l[10];if(Math.abs(h-d)<.01&&Math.abs(u-_)<.01&&Math.abs(g-p)<.01){if(Math.abs(h+d)<.1&&Math.abs(u+_)<.1&&Math.abs(g+p)<.1&&Math.abs(c+f+m-3)<.1)return this.set(1,0,0,0),this;t=Math.PI;const v=(c+1)/2,b=(f+1)/2,N=(m+1)/2,A=(h+d)/4,R=(u+_)/4,F=(g+p)/4;return v>b&&v>N?v<.01?(n=0,s=.707106781,r=.707106781):(n=Math.sqrt(v),s=A/n,r=R/n):b>N?b<.01?(n=.707106781,s=0,r=.707106781):(s=Math.sqrt(b),n=A/s,r=F/s):N<.01?(n=.707106781,s=.707106781,r=0):(r=Math.sqrt(N),n=R/r,s=F/r),this.set(n,s,r,t),this}let M=Math.sqrt((p-g)*(p-g)+(u-_)*(u-_)+(d-h)*(d-h));return Math.abs(M)<.001&&(M=1),this.x=(p-g)/M,this.y=(u-_)/M,this.z=(d-h)/M,this.w=Math.acos((c+f+m-1)/2),this}setFromMatrixPosition(e){const t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this.w=t[15],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this.w=Math.min(this.w,e.w),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this.w=Math.max(this.w,e.w),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this.z=Math.max(e.z,Math.min(t.z,this.z)),this.w=Math.max(e.w,Math.min(t.w,this.w)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this.z=Math.max(e,Math.min(t,this.z)),this.w=Math.max(e,Math.min(t,this.w)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this.w=Math.floor(this.w),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this.w=Math.ceil(this.w),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this.w=Math.round(this.w),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this.w=Math.trunc(this.w),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this.w=-this.w,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z+this.w*e.w}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)+Math.abs(this.w)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this.w+=(e.w-this.w)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this.z=e.z+(t.z-e.z)*n,this.w=e.w+(t.w-e.w)*n,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z&&e.w===this.w}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this.w=e[t+3],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e[t+3]=this.w,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this.w=e.getW(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this.w=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z,yield this.w}}class jg extends ta{constructor(e=1,t=1,n={}){super(),this.isRenderTarget=!0,this.width=e,this.height=t,this.depth=1,this.scissor=new sn(0,0,e,t),this.scissorTest=!1,this.viewport=new sn(0,0,e,t);const s={width:e,height:t,depth:1};n=Object.assign({generateMipmaps:!1,internalFormat:null,minFilter:hi,depthBuffer:!0,stencilBuffer:!1,resolveDepthBuffer:!0,resolveStencilBuffer:!0,depthTexture:null,samples:0,count:1},n);const r=new Ln(s,n.mapping,n.wrapS,n.wrapT,n.magFilter,n.minFilter,n.format,n.type,n.anisotropy,n.colorSpace);r.flipY=!1,r.generateMipmaps=n.generateMipmaps,r.internalFormat=n.internalFormat,this.textures=[];const a=n.count;for(let o=0;o<a;o++)this.textures[o]=r.clone(),this.textures[o].isRenderTargetTexture=!0;this.depthBuffer=n.depthBuffer,this.stencilBuffer=n.stencilBuffer,this.resolveDepthBuffer=n.resolveDepthBuffer,this.resolveStencilBuffer=n.resolveStencilBuffer,this.depthTexture=n.depthTexture,this.samples=n.samples}get texture(){return this.textures[0]}set texture(e){this.textures[0]=e}setSize(e,t,n=1){if(this.width!==e||this.height!==t||this.depth!==n){this.width=e,this.height=t,this.depth=n;for(let s=0,r=this.textures.length;s<r;s++)this.textures[s].image.width=e,this.textures[s].image.height=t,this.textures[s].image.depth=n;this.dispose()}this.viewport.set(0,0,e,t),this.scissor.set(0,0,e,t)}clone(){return new this.constructor().copy(this)}copy(e){this.width=e.width,this.height=e.height,this.depth=e.depth,this.scissor.copy(e.scissor),this.scissorTest=e.scissorTest,this.viewport.copy(e.viewport),this.textures.length=0;for(let n=0,s=e.textures.length;n<s;n++)this.textures[n]=e.textures[n].clone(),this.textures[n].isRenderTargetTexture=!0;const t=Object.assign({},e.texture.image);return this.texture.source=new Jf(t),this.depthBuffer=e.depthBuffer,this.stencilBuffer=e.stencilBuffer,this.resolveDepthBuffer=e.resolveDepthBuffer,this.resolveStencilBuffer=e.resolveStencilBuffer,e.depthTexture!==null&&(this.depthTexture=e.depthTexture.clone()),this.samples=e.samples,this}dispose(){this.dispatchEvent({type:"dispose"})}}class $s extends jg{constructor(e=1,t=1,n={}){super(e,t,n),this.isWebGLRenderTarget=!0}}class Qf extends Ln{constructor(e=null,t=1,n=1,s=1){super(null),this.isDataArrayTexture=!0,this.image={data:e,width:t,height:n,depth:s},this.magFilter=ei,this.minFilter=ei,this.wrapR=ks,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1,this.layerUpdates=new Set}addLayerUpdate(e){this.layerUpdates.add(e)}clearLayerUpdates(){this.layerUpdates.clear()}}class Kg extends Ln{constructor(e=null,t=1,n=1,s=1){super(null),this.isData3DTexture=!0,this.image={data:e,width:t,height:n,depth:s},this.magFilter=ei,this.minFilter=ei,this.wrapR=ks,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}}class Ys{constructor(e=0,t=0,n=0,s=1){this.isQuaternion=!0,this._x=e,this._y=t,this._z=n,this._w=s}static slerpFlat(e,t,n,s,r,a,o){let l=n[s+0],c=n[s+1],h=n[s+2],u=n[s+3];const d=r[a+0],f=r[a+1],g=r[a+2],_=r[a+3];if(o===0){e[t+0]=l,e[t+1]=c,e[t+2]=h,e[t+3]=u;return}if(o===1){e[t+0]=d,e[t+1]=f,e[t+2]=g,e[t+3]=_;return}if(u!==_||l!==d||c!==f||h!==g){let p=1-o;const m=l*d+c*f+h*g+u*_,M=m>=0?1:-1,v=1-m*m;if(v>Number.EPSILON){const N=Math.sqrt(v),A=Math.atan2(N,m*M);p=Math.sin(p*A)/N,o=Math.sin(o*A)/N}const b=o*M;if(l=l*p+d*b,c=c*p+f*b,h=h*p+g*b,u=u*p+_*b,p===1-o){const N=1/Math.sqrt(l*l+c*c+h*h+u*u);l*=N,c*=N,h*=N,u*=N}}e[t]=l,e[t+1]=c,e[t+2]=h,e[t+3]=u}static multiplyQuaternionsFlat(e,t,n,s,r,a){const o=n[s],l=n[s+1],c=n[s+2],h=n[s+3],u=r[a],d=r[a+1],f=r[a+2],g=r[a+3];return e[t]=o*g+h*u+l*f-c*d,e[t+1]=l*g+h*d+c*u-o*f,e[t+2]=c*g+h*f+o*d-l*u,e[t+3]=h*g-o*u-l*d-c*f,e}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get w(){return this._w}set w(e){this._w=e,this._onChangeCallback()}set(e,t,n,s){return this._x=e,this._y=t,this._z=n,this._w=s,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._w)}copy(e){return this._x=e.x,this._y=e.y,this._z=e.z,this._w=e.w,this._onChangeCallback(),this}setFromEuler(e,t=!0){const n=e._x,s=e._y,r=e._z,a=e._order,o=Math.cos,l=Math.sin,c=o(n/2),h=o(s/2),u=o(r/2),d=l(n/2),f=l(s/2),g=l(r/2);switch(a){case"XYZ":this._x=d*h*u+c*f*g,this._y=c*f*u-d*h*g,this._z=c*h*g+d*f*u,this._w=c*h*u-d*f*g;break;case"YXZ":this._x=d*h*u+c*f*g,this._y=c*f*u-d*h*g,this._z=c*h*g-d*f*u,this._w=c*h*u+d*f*g;break;case"ZXY":this._x=d*h*u-c*f*g,this._y=c*f*u+d*h*g,this._z=c*h*g+d*f*u,this._w=c*h*u-d*f*g;break;case"ZYX":this._x=d*h*u-c*f*g,this._y=c*f*u+d*h*g,this._z=c*h*g-d*f*u,this._w=c*h*u+d*f*g;break;case"YZX":this._x=d*h*u+c*f*g,this._y=c*f*u+d*h*g,this._z=c*h*g-d*f*u,this._w=c*h*u-d*f*g;break;case"XZY":this._x=d*h*u-c*f*g,this._y=c*f*u-d*h*g,this._z=c*h*g+d*f*u,this._w=c*h*u+d*f*g;break;default:console.warn("THREE.Quaternion: .setFromEuler() encountered an unknown order: "+a)}return t===!0&&this._onChangeCallback(),this}setFromAxisAngle(e,t){const n=t/2,s=Math.sin(n);return this._x=e.x*s,this._y=e.y*s,this._z=e.z*s,this._w=Math.cos(n),this._onChangeCallback(),this}setFromRotationMatrix(e){const t=e.elements,n=t[0],s=t[4],r=t[8],a=t[1],o=t[5],l=t[9],c=t[2],h=t[6],u=t[10],d=n+o+u;if(d>0){const f=.5/Math.sqrt(d+1);this._w=.25/f,this._x=(h-l)*f,this._y=(r-c)*f,this._z=(a-s)*f}else if(n>o&&n>u){const f=2*Math.sqrt(1+n-o-u);this._w=(h-l)/f,this._x=.25*f,this._y=(s+a)/f,this._z=(r+c)/f}else if(o>u){const f=2*Math.sqrt(1+o-n-u);this._w=(r-c)/f,this._x=(s+a)/f,this._y=.25*f,this._z=(l+h)/f}else{const f=2*Math.sqrt(1+u-n-o);this._w=(a-s)/f,this._x=(r+c)/f,this._y=(l+h)/f,this._z=.25*f}return this._onChangeCallback(),this}setFromUnitVectors(e,t){let n=e.dot(t)+1;return n<Number.EPSILON?(n=0,Math.abs(e.x)>Math.abs(e.z)?(this._x=-e.y,this._y=e.x,this._z=0,this._w=n):(this._x=0,this._y=-e.z,this._z=e.y,this._w=n)):(this._x=e.y*t.z-e.z*t.y,this._y=e.z*t.x-e.x*t.z,this._z=e.x*t.y-e.y*t.x,this._w=n),this.normalize()}angleTo(e){return 2*Math.acos(Math.abs(Sn(this.dot(e),-1,1)))}rotateTowards(e,t){const n=this.angleTo(e);if(n===0)return this;const s=Math.min(1,t/n);return this.slerp(e,s),this}identity(){return this.set(0,0,0,1)}invert(){return this.conjugate()}conjugate(){return this._x*=-1,this._y*=-1,this._z*=-1,this._onChangeCallback(),this}dot(e){return this._x*e._x+this._y*e._y+this._z*e._z+this._w*e._w}lengthSq(){return this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w}length(){return Math.sqrt(this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w)}normalize(){let e=this.length();return e===0?(this._x=0,this._y=0,this._z=0,this._w=1):(e=1/e,this._x=this._x*e,this._y=this._y*e,this._z=this._z*e,this._w=this._w*e),this._onChangeCallback(),this}multiply(e){return this.multiplyQuaternions(this,e)}premultiply(e){return this.multiplyQuaternions(e,this)}multiplyQuaternions(e,t){const n=e._x,s=e._y,r=e._z,a=e._w,o=t._x,l=t._y,c=t._z,h=t._w;return this._x=n*h+a*o+s*c-r*l,this._y=s*h+a*l+r*o-n*c,this._z=r*h+a*c+n*l-s*o,this._w=a*h-n*o-s*l-r*c,this._onChangeCallback(),this}slerp(e,t){if(t===0)return this;if(t===1)return this.copy(e);const n=this._x,s=this._y,r=this._z,a=this._w;let o=a*e._w+n*e._x+s*e._y+r*e._z;if(o<0?(this._w=-e._w,this._x=-e._x,this._y=-e._y,this._z=-e._z,o=-o):this.copy(e),o>=1)return this._w=a,this._x=n,this._y=s,this._z=r,this;const l=1-o*o;if(l<=Number.EPSILON){const f=1-t;return this._w=f*a+t*this._w,this._x=f*n+t*this._x,this._y=f*s+t*this._y,this._z=f*r+t*this._z,this.normalize(),this}const c=Math.sqrt(l),h=Math.atan2(c,o),u=Math.sin((1-t)*h)/c,d=Math.sin(t*h)/c;return this._w=a*u+this._w*d,this._x=n*u+this._x*d,this._y=s*u+this._y*d,this._z=r*u+this._z*d,this._onChangeCallback(),this}slerpQuaternions(e,t,n){return this.copy(e).slerp(t,n)}random(){const e=2*Math.PI*Math.random(),t=2*Math.PI*Math.random(),n=Math.random(),s=Math.sqrt(1-n),r=Math.sqrt(n);return this.set(s*Math.sin(e),s*Math.cos(e),r*Math.sin(t),r*Math.cos(t))}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._w===this._w}fromArray(e,t=0){return this._x=e[t],this._y=e[t+1],this._z=e[t+2],this._w=e[t+3],this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._w,e}fromBufferAttribute(e,t){return this._x=e.getX(t),this._y=e.getY(t),this._z=e.getZ(t),this._w=e.getW(t),this._onChangeCallback(),this}toJSON(){return this.toArray()}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._w}}class V{constructor(e=0,t=0,n=0){V.prototype.isVector3=!0,this.x=e,this.y=t,this.z=n}set(e,t,n){return n===void 0&&(n=this.z),this.x=e,this.y=t,this.z=n,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this}multiplyVectors(e,t){return this.x=e.x*t.x,this.y=e.y*t.y,this.z=e.z*t.z,this}applyEuler(e){return this.applyQuaternion(Nu.setFromEuler(e))}applyAxisAngle(e,t){return this.applyQuaternion(Nu.setFromAxisAngle(e,t))}applyMatrix3(e){const t=this.x,n=this.y,s=this.z,r=e.elements;return this.x=r[0]*t+r[3]*n+r[6]*s,this.y=r[1]*t+r[4]*n+r[7]*s,this.z=r[2]*t+r[5]*n+r[8]*s,this}applyNormalMatrix(e){return this.applyMatrix3(e).normalize()}applyMatrix4(e){const t=this.x,n=this.y,s=this.z,r=e.elements,a=1/(r[3]*t+r[7]*n+r[11]*s+r[15]);return this.x=(r[0]*t+r[4]*n+r[8]*s+r[12])*a,this.y=(r[1]*t+r[5]*n+r[9]*s+r[13])*a,this.z=(r[2]*t+r[6]*n+r[10]*s+r[14])*a,this}applyQuaternion(e){const t=this.x,n=this.y,s=this.z,r=e.x,a=e.y,o=e.z,l=e.w,c=2*(a*s-o*n),h=2*(o*t-r*s),u=2*(r*n-a*t);return this.x=t+l*c+a*u-o*h,this.y=n+l*h+o*c-r*u,this.z=s+l*u+r*h-a*c,this}project(e){return this.applyMatrix4(e.matrixWorldInverse).applyMatrix4(e.projectionMatrix)}unproject(e){return this.applyMatrix4(e.projectionMatrixInverse).applyMatrix4(e.matrixWorld)}transformDirection(e){const t=this.x,n=this.y,s=this.z,r=e.elements;return this.x=r[0]*t+r[4]*n+r[8]*s,this.y=r[1]*t+r[5]*n+r[9]*s,this.z=r[2]*t+r[6]*n+r[10]*s,this.normalize()}divide(e){return this.x/=e.x,this.y/=e.y,this.z/=e.z,this}divideScalar(e){return this.multiplyScalar(1/e)}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this.z=Math.max(e.z,Math.min(t.z,this.z)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this.z=Math.max(e,Math.min(t,this.z)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this.z=e.z+(t.z-e.z)*n,this}cross(e){return this.crossVectors(this,e)}crossVectors(e,t){const n=e.x,s=e.y,r=e.z,a=t.x,o=t.y,l=t.z;return this.x=s*l-r*o,this.y=r*a-n*l,this.z=n*o-s*a,this}projectOnVector(e){const t=e.lengthSq();if(t===0)return this.set(0,0,0);const n=e.dot(this)/t;return this.copy(e).multiplyScalar(n)}projectOnPlane(e){return Wl.copy(this).projectOnVector(e),this.sub(Wl)}reflect(e){return this.sub(Wl.copy(e).multiplyScalar(2*this.dot(e)))}angleTo(e){const t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;const n=this.dot(e)/t;return Math.acos(Sn(n,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){const t=this.x-e.x,n=this.y-e.y,s=this.z-e.z;return t*t+n*n+s*s}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)+Math.abs(this.z-e.z)}setFromSpherical(e){return this.setFromSphericalCoords(e.radius,e.phi,e.theta)}setFromSphericalCoords(e,t,n){const s=Math.sin(t)*e;return this.x=s*Math.sin(n),this.y=Math.cos(t)*e,this.z=s*Math.cos(n),this}setFromCylindrical(e){return this.setFromCylindricalCoords(e.radius,e.theta,e.y)}setFromCylindricalCoords(e,t,n){return this.x=e*Math.sin(t),this.y=n,this.z=e*Math.cos(t),this}setFromMatrixPosition(e){const t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this}setFromMatrixScale(e){const t=this.setFromMatrixColumn(e,0).length(),n=this.setFromMatrixColumn(e,1).length(),s=this.setFromMatrixColumn(e,2).length();return this.x=t,this.y=n,this.z=s,this}setFromMatrixColumn(e,t){return this.fromArray(e.elements,t*4)}setFromMatrix3Column(e,t){return this.fromArray(e.elements,t*3)}setFromEuler(e){return this.x=e._x,this.y=e._y,this.z=e._z,this}setFromColor(e){return this.x=e.r,this.y=e.g,this.z=e.b,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this}randomDirection(){const e=Math.random()*Math.PI*2,t=Math.random()*2-1,n=Math.sqrt(1-t*t);return this.x=n*Math.cos(e),this.y=t,this.z=n*Math.sin(e),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z}}const Wl=new V,Nu=new Ys;class Wa{constructor(e=new V(1/0,1/0,1/0),t=new V(-1/0,-1/0,-1/0)){this.isBox3=!0,this.min=e,this.max=t}set(e,t){return this.min.copy(e),this.max.copy(t),this}setFromArray(e){this.makeEmpty();for(let t=0,n=e.length;t<n;t+=3)this.expandByPoint(ri.fromArray(e,t));return this}setFromBufferAttribute(e){this.makeEmpty();for(let t=0,n=e.count;t<n;t++)this.expandByPoint(ri.fromBufferAttribute(e,t));return this}setFromPoints(e){this.makeEmpty();for(let t=0,n=e.length;t<n;t++)this.expandByPoint(e[t]);return this}setFromCenterAndSize(e,t){const n=ri.copy(t).multiplyScalar(.5);return this.min.copy(e).sub(n),this.max.copy(e).add(n),this}setFromObject(e,t=!1){return this.makeEmpty(),this.expandByObject(e,t)}clone(){return new this.constructor().copy(this)}copy(e){return this.min.copy(e.min),this.max.copy(e.max),this}makeEmpty(){return this.min.x=this.min.y=this.min.z=1/0,this.max.x=this.max.y=this.max.z=-1/0,this}isEmpty(){return this.max.x<this.min.x||this.max.y<this.min.y||this.max.z<this.min.z}getCenter(e){return this.isEmpty()?e.set(0,0,0):e.addVectors(this.min,this.max).multiplyScalar(.5)}getSize(e){return this.isEmpty()?e.set(0,0,0):e.subVectors(this.max,this.min)}expandByPoint(e){return this.min.min(e),this.max.max(e),this}expandByVector(e){return this.min.sub(e),this.max.add(e),this}expandByScalar(e){return this.min.addScalar(-e),this.max.addScalar(e),this}expandByObject(e,t=!1){e.updateWorldMatrix(!1,!1);const n=e.geometry;if(n!==void 0){const r=n.getAttribute("position");if(t===!0&&r!==void 0&&e.isInstancedMesh!==!0)for(let a=0,o=r.count;a<o;a++)e.isMesh===!0?e.getVertexPosition(a,ri):ri.fromBufferAttribute(r,a),ri.applyMatrix4(e.matrixWorld),this.expandByPoint(ri);else e.boundingBox!==void 0?(e.boundingBox===null&&e.computeBoundingBox(),so.copy(e.boundingBox)):(n.boundingBox===null&&n.computeBoundingBox(),so.copy(n.boundingBox)),so.applyMatrix4(e.matrixWorld),this.union(so)}const s=e.children;for(let r=0,a=s.length;r<a;r++)this.expandByObject(s[r],t);return this}containsPoint(e){return e.x>=this.min.x&&e.x<=this.max.x&&e.y>=this.min.y&&e.y<=this.max.y&&e.z>=this.min.z&&e.z<=this.max.z}containsBox(e){return this.min.x<=e.min.x&&e.max.x<=this.max.x&&this.min.y<=e.min.y&&e.max.y<=this.max.y&&this.min.z<=e.min.z&&e.max.z<=this.max.z}getParameter(e,t){return t.set((e.x-this.min.x)/(this.max.x-this.min.x),(e.y-this.min.y)/(this.max.y-this.min.y),(e.z-this.min.z)/(this.max.z-this.min.z))}intersectsBox(e){return e.max.x>=this.min.x&&e.min.x<=this.max.x&&e.max.y>=this.min.y&&e.min.y<=this.max.y&&e.max.z>=this.min.z&&e.min.z<=this.max.z}intersectsSphere(e){return this.clampPoint(e.center,ri),ri.distanceToSquared(e.center)<=e.radius*e.radius}intersectsPlane(e){let t,n;return e.normal.x>0?(t=e.normal.x*this.min.x,n=e.normal.x*this.max.x):(t=e.normal.x*this.max.x,n=e.normal.x*this.min.x),e.normal.y>0?(t+=e.normal.y*this.min.y,n+=e.normal.y*this.max.y):(t+=e.normal.y*this.max.y,n+=e.normal.y*this.min.y),e.normal.z>0?(t+=e.normal.z*this.min.z,n+=e.normal.z*this.max.z):(t+=e.normal.z*this.max.z,n+=e.normal.z*this.min.z),t<=-e.constant&&n>=-e.constant}intersectsTriangle(e){if(this.isEmpty())return!1;this.getCenter(ga),ro.subVectors(this.max,ga),dr.subVectors(e.a,ga),fr.subVectors(e.b,ga),pr.subVectors(e.c,ga),ns.subVectors(fr,dr),is.subVectors(pr,fr),Rs.subVectors(dr,pr);let t=[0,-ns.z,ns.y,0,-is.z,is.y,0,-Rs.z,Rs.y,ns.z,0,-ns.x,is.z,0,-is.x,Rs.z,0,-Rs.x,-ns.y,ns.x,0,-is.y,is.x,0,-Rs.y,Rs.x,0];return!Xl(t,dr,fr,pr,ro)||(t=[1,0,0,0,1,0,0,0,1],!Xl(t,dr,fr,pr,ro))?!1:(ao.crossVectors(ns,is),t=[ao.x,ao.y,ao.z],Xl(t,dr,fr,pr,ro))}clampPoint(e,t){return t.copy(e).clamp(this.min,this.max)}distanceToPoint(e){return this.clampPoint(e,ri).distanceTo(e)}getBoundingSphere(e){return this.isEmpty()?e.makeEmpty():(this.getCenter(e.center),e.radius=this.getSize(ri).length()*.5),e}intersect(e){return this.min.max(e.min),this.max.min(e.max),this.isEmpty()&&this.makeEmpty(),this}union(e){return this.min.min(e.min),this.max.max(e.max),this}applyMatrix4(e){return this.isEmpty()?this:(Fi[0].set(this.min.x,this.min.y,this.min.z).applyMatrix4(e),Fi[1].set(this.min.x,this.min.y,this.max.z).applyMatrix4(e),Fi[2].set(this.min.x,this.max.y,this.min.z).applyMatrix4(e),Fi[3].set(this.min.x,this.max.y,this.max.z).applyMatrix4(e),Fi[4].set(this.max.x,this.min.y,this.min.z).applyMatrix4(e),Fi[5].set(this.max.x,this.min.y,this.max.z).applyMatrix4(e),Fi[6].set(this.max.x,this.max.y,this.min.z).applyMatrix4(e),Fi[7].set(this.max.x,this.max.y,this.max.z).applyMatrix4(e),this.setFromPoints(Fi),this)}translate(e){return this.min.add(e),this.max.add(e),this}equals(e){return e.min.equals(this.min)&&e.max.equals(this.max)}}const Fi=[new V,new V,new V,new V,new V,new V,new V,new V],ri=new V,so=new Wa,dr=new V,fr=new V,pr=new V,ns=new V,is=new V,Rs=new V,ga=new V,ro=new V,ao=new V,Cs=new V;function Xl(i,e,t,n,s){for(let r=0,a=i.length-3;r<=a;r+=3){Cs.fromArray(i,r);const o=s.x*Math.abs(Cs.x)+s.y*Math.abs(Cs.y)+s.z*Math.abs(Cs.z),l=e.dot(Cs),c=t.dot(Cs),h=n.dot(Cs);if(Math.max(-Math.max(l,c,h),Math.min(l,c,h))>o)return!1}return!0}const Zg=new Wa,_a=new V,ql=new V;class Xa{constructor(e=new V,t=-1){this.isSphere=!0,this.center=e,this.radius=t}set(e,t){return this.center.copy(e),this.radius=t,this}setFromPoints(e,t){const n=this.center;t!==void 0?n.copy(t):Zg.setFromPoints(e).getCenter(n);let s=0;for(let r=0,a=e.length;r<a;r++)s=Math.max(s,n.distanceToSquared(e[r]));return this.radius=Math.sqrt(s),this}copy(e){return this.center.copy(e.center),this.radius=e.radius,this}isEmpty(){return this.radius<0}makeEmpty(){return this.center.set(0,0,0),this.radius=-1,this}containsPoint(e){return e.distanceToSquared(this.center)<=this.radius*this.radius}distanceToPoint(e){return e.distanceTo(this.center)-this.radius}intersectsSphere(e){const t=this.radius+e.radius;return e.center.distanceToSquared(this.center)<=t*t}intersectsBox(e){return e.intersectsSphere(this)}intersectsPlane(e){return Math.abs(e.distanceToPoint(this.center))<=this.radius}clampPoint(e,t){const n=this.center.distanceToSquared(e);return t.copy(e),n>this.radius*this.radius&&(t.sub(this.center).normalize(),t.multiplyScalar(this.radius).add(this.center)),t}getBoundingBox(e){return this.isEmpty()?(e.makeEmpty(),e):(e.set(this.center,this.center),e.expandByScalar(this.radius),e)}applyMatrix4(e){return this.center.applyMatrix4(e),this.radius=this.radius*e.getMaxScaleOnAxis(),this}translate(e){return this.center.add(e),this}expandByPoint(e){if(this.isEmpty())return this.center.copy(e),this.radius=0,this;_a.subVectors(e,this.center);const t=_a.lengthSq();if(t>this.radius*this.radius){const n=Math.sqrt(t),s=(n-this.radius)*.5;this.center.addScaledVector(_a,s/n),this.radius+=s}return this}union(e){return e.isEmpty()?this:this.isEmpty()?(this.copy(e),this):(this.center.equals(e.center)===!0?this.radius=Math.max(this.radius,e.radius):(ql.subVectors(e.center,this.center).setLength(e.radius),this.expandByPoint(_a.copy(e.center).add(ql)),this.expandByPoint(_a.copy(e.center).sub(ql))),this)}equals(e){return e.center.equals(this.center)&&e.radius===this.radius}clone(){return new this.constructor().copy(this)}}const Oi=new V,$l=new V,oo=new V,ss=new V,Yl=new V,lo=new V,jl=new V;class qa{constructor(e=new V,t=new V(0,0,-1)){this.origin=e,this.direction=t}set(e,t){return this.origin.copy(e),this.direction.copy(t),this}copy(e){return this.origin.copy(e.origin),this.direction.copy(e.direction),this}at(e,t){return t.copy(this.origin).addScaledVector(this.direction,e)}lookAt(e){return this.direction.copy(e).sub(this.origin).normalize(),this}recast(e){return this.origin.copy(this.at(e,Oi)),this}closestPointToPoint(e,t){t.subVectors(e,this.origin);const n=t.dot(this.direction);return n<0?t.copy(this.origin):t.copy(this.origin).addScaledVector(this.direction,n)}distanceToPoint(e){return Math.sqrt(this.distanceSqToPoint(e))}distanceSqToPoint(e){const t=Oi.subVectors(e,this.origin).dot(this.direction);return t<0?this.origin.distanceToSquared(e):(Oi.copy(this.origin).addScaledVector(this.direction,t),Oi.distanceToSquared(e))}distanceSqToSegment(e,t,n,s){$l.copy(e).add(t).multiplyScalar(.5),oo.copy(t).sub(e).normalize(),ss.copy(this.origin).sub($l);const r=e.distanceTo(t)*.5,a=-this.direction.dot(oo),o=ss.dot(this.direction),l=-ss.dot(oo),c=ss.lengthSq(),h=Math.abs(1-a*a);let u,d,f,g;if(h>0)if(u=a*l-o,d=a*o-l,g=r*h,u>=0)if(d>=-g)if(d<=g){const _=1/h;u*=_,d*=_,f=u*(u+a*d+2*o)+d*(a*u+d+2*l)+c}else d=r,u=Math.max(0,-(a*d+o)),f=-u*u+d*(d+2*l)+c;else d=-r,u=Math.max(0,-(a*d+o)),f=-u*u+d*(d+2*l)+c;else d<=-g?(u=Math.max(0,-(-a*r+o)),d=u>0?-r:Math.min(Math.max(-r,-l),r),f=-u*u+d*(d+2*l)+c):d<=g?(u=0,d=Math.min(Math.max(-r,-l),r),f=d*(d+2*l)+c):(u=Math.max(0,-(a*r+o)),d=u>0?r:Math.min(Math.max(-r,-l),r),f=-u*u+d*(d+2*l)+c);else d=a>0?-r:r,u=Math.max(0,-(a*d+o)),f=-u*u+d*(d+2*l)+c;return n&&n.copy(this.origin).addScaledVector(this.direction,u),s&&s.copy($l).addScaledVector(oo,d),f}intersectSphere(e,t){Oi.subVectors(e.center,this.origin);const n=Oi.dot(this.direction),s=Oi.dot(Oi)-n*n,r=e.radius*e.radius;if(s>r)return null;const a=Math.sqrt(r-s),o=n-a,l=n+a;return l<0?null:o<0?this.at(l,t):this.at(o,t)}intersectsSphere(e){return this.distanceSqToPoint(e.center)<=e.radius*e.radius}distanceToPlane(e){const t=e.normal.dot(this.direction);if(t===0)return e.distanceToPoint(this.origin)===0?0:null;const n=-(this.origin.dot(e.normal)+e.constant)/t;return n>=0?n:null}intersectPlane(e,t){const n=this.distanceToPlane(e);return n===null?null:this.at(n,t)}intersectsPlane(e){const t=e.distanceToPoint(this.origin);return t===0||e.normal.dot(this.direction)*t<0}intersectBox(e,t){let n,s,r,a,o,l;const c=1/this.direction.x,h=1/this.direction.y,u=1/this.direction.z,d=this.origin;return c>=0?(n=(e.min.x-d.x)*c,s=(e.max.x-d.x)*c):(n=(e.max.x-d.x)*c,s=(e.min.x-d.x)*c),h>=0?(r=(e.min.y-d.y)*h,a=(e.max.y-d.y)*h):(r=(e.max.y-d.y)*h,a=(e.min.y-d.y)*h),n>a||r>s||((r>n||isNaN(n))&&(n=r),(a<s||isNaN(s))&&(s=a),u>=0?(o=(e.min.z-d.z)*u,l=(e.max.z-d.z)*u):(o=(e.max.z-d.z)*u,l=(e.min.z-d.z)*u),n>l||o>s)||((o>n||n!==n)&&(n=o),(l<s||s!==s)&&(s=l),s<0)?null:this.at(n>=0?n:s,t)}intersectsBox(e){return this.intersectBox(e,Oi)!==null}intersectTriangle(e,t,n,s,r){Yl.subVectors(t,e),lo.subVectors(n,e),jl.crossVectors(Yl,lo);let a=this.direction.dot(jl),o;if(a>0){if(s)return null;o=1}else if(a<0)o=-1,a=-a;else return null;ss.subVectors(this.origin,e);const l=o*this.direction.dot(lo.crossVectors(ss,lo));if(l<0)return null;const c=o*this.direction.dot(Yl.cross(ss));if(c<0||l+c>a)return null;const h=-o*ss.dot(jl);return h<0?null:this.at(h/a,r)}applyMatrix4(e){return this.origin.applyMatrix4(e),this.direction.transformDirection(e),this}equals(e){return e.origin.equals(this.origin)&&e.direction.equals(this.direction)}clone(){return new this.constructor().copy(this)}}class Bt{constructor(e,t,n,s,r,a,o,l,c,h,u,d,f,g,_,p){Bt.prototype.isMatrix4=!0,this.elements=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],e!==void 0&&this.set(e,t,n,s,r,a,o,l,c,h,u,d,f,g,_,p)}set(e,t,n,s,r,a,o,l,c,h,u,d,f,g,_,p){const m=this.elements;return m[0]=e,m[4]=t,m[8]=n,m[12]=s,m[1]=r,m[5]=a,m[9]=o,m[13]=l,m[2]=c,m[6]=h,m[10]=u,m[14]=d,m[3]=f,m[7]=g,m[11]=_,m[15]=p,this}identity(){return this.set(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1),this}clone(){return new Bt().fromArray(this.elements)}copy(e){const t=this.elements,n=e.elements;return t[0]=n[0],t[1]=n[1],t[2]=n[2],t[3]=n[3],t[4]=n[4],t[5]=n[5],t[6]=n[6],t[7]=n[7],t[8]=n[8],t[9]=n[9],t[10]=n[10],t[11]=n[11],t[12]=n[12],t[13]=n[13],t[14]=n[14],t[15]=n[15],this}copyPosition(e){const t=this.elements,n=e.elements;return t[12]=n[12],t[13]=n[13],t[14]=n[14],this}setFromMatrix3(e){const t=e.elements;return this.set(t[0],t[3],t[6],0,t[1],t[4],t[7],0,t[2],t[5],t[8],0,0,0,0,1),this}extractBasis(e,t,n){return e.setFromMatrixColumn(this,0),t.setFromMatrixColumn(this,1),n.setFromMatrixColumn(this,2),this}makeBasis(e,t,n){return this.set(e.x,t.x,n.x,0,e.y,t.y,n.y,0,e.z,t.z,n.z,0,0,0,0,1),this}extractRotation(e){const t=this.elements,n=e.elements,s=1/mr.setFromMatrixColumn(e,0).length(),r=1/mr.setFromMatrixColumn(e,1).length(),a=1/mr.setFromMatrixColumn(e,2).length();return t[0]=n[0]*s,t[1]=n[1]*s,t[2]=n[2]*s,t[3]=0,t[4]=n[4]*r,t[5]=n[5]*r,t[6]=n[6]*r,t[7]=0,t[8]=n[8]*a,t[9]=n[9]*a,t[10]=n[10]*a,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromEuler(e){const t=this.elements,n=e.x,s=e.y,r=e.z,a=Math.cos(n),o=Math.sin(n),l=Math.cos(s),c=Math.sin(s),h=Math.cos(r),u=Math.sin(r);if(e.order==="XYZ"){const d=a*h,f=a*u,g=o*h,_=o*u;t[0]=l*h,t[4]=-l*u,t[8]=c,t[1]=f+g*c,t[5]=d-_*c,t[9]=-o*l,t[2]=_-d*c,t[6]=g+f*c,t[10]=a*l}else if(e.order==="YXZ"){const d=l*h,f=l*u,g=c*h,_=c*u;t[0]=d+_*o,t[4]=g*o-f,t[8]=a*c,t[1]=a*u,t[5]=a*h,t[9]=-o,t[2]=f*o-g,t[6]=_+d*o,t[10]=a*l}else if(e.order==="ZXY"){const d=l*h,f=l*u,g=c*h,_=c*u;t[0]=d-_*o,t[4]=-a*u,t[8]=g+f*o,t[1]=f+g*o,t[5]=a*h,t[9]=_-d*o,t[2]=-a*c,t[6]=o,t[10]=a*l}else if(e.order==="ZYX"){const d=a*h,f=a*u,g=o*h,_=o*u;t[0]=l*h,t[4]=g*c-f,t[8]=d*c+_,t[1]=l*u,t[5]=_*c+d,t[9]=f*c-g,t[2]=-c,t[6]=o*l,t[10]=a*l}else if(e.order==="YZX"){const d=a*l,f=a*c,g=o*l,_=o*c;t[0]=l*h,t[4]=_-d*u,t[8]=g*u+f,t[1]=u,t[5]=a*h,t[9]=-o*h,t[2]=-c*h,t[6]=f*u+g,t[10]=d-_*u}else if(e.order==="XZY"){const d=a*l,f=a*c,g=o*l,_=o*c;t[0]=l*h,t[4]=-u,t[8]=c*h,t[1]=d*u+_,t[5]=a*h,t[9]=f*u-g,t[2]=g*u-f,t[6]=o*h,t[10]=_*u+d}return t[3]=0,t[7]=0,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromQuaternion(e){return this.compose(Jg,e,Qg)}lookAt(e,t,n){const s=this.elements;return kn.subVectors(e,t),kn.lengthSq()===0&&(kn.z=1),kn.normalize(),rs.crossVectors(n,kn),rs.lengthSq()===0&&(Math.abs(n.z)===1?kn.x+=1e-4:kn.z+=1e-4,kn.normalize(),rs.crossVectors(n,kn)),rs.normalize(),co.crossVectors(kn,rs),s[0]=rs.x,s[4]=co.x,s[8]=kn.x,s[1]=rs.y,s[5]=co.y,s[9]=kn.y,s[2]=rs.z,s[6]=co.z,s[10]=kn.z,this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){const n=e.elements,s=t.elements,r=this.elements,a=n[0],o=n[4],l=n[8],c=n[12],h=n[1],u=n[5],d=n[9],f=n[13],g=n[2],_=n[6],p=n[10],m=n[14],M=n[3],v=n[7],b=n[11],N=n[15],A=s[0],R=s[4],F=s[8],w=s[12],y=s[1],P=s[5],K=s[9],H=s[13],Z=s[2],q=s[6],ee=s[10],Y=s[14],ne=s[3],ge=s[7],de=s[11],ve=s[15];return r[0]=a*A+o*y+l*Z+c*ne,r[4]=a*R+o*P+l*q+c*ge,r[8]=a*F+o*K+l*ee+c*de,r[12]=a*w+o*H+l*Y+c*ve,r[1]=h*A+u*y+d*Z+f*ne,r[5]=h*R+u*P+d*q+f*ge,r[9]=h*F+u*K+d*ee+f*de,r[13]=h*w+u*H+d*Y+f*ve,r[2]=g*A+_*y+p*Z+m*ne,r[6]=g*R+_*P+p*q+m*ge,r[10]=g*F+_*K+p*ee+m*de,r[14]=g*w+_*H+p*Y+m*ve,r[3]=M*A+v*y+b*Z+N*ne,r[7]=M*R+v*P+b*q+N*ge,r[11]=M*F+v*K+b*ee+N*de,r[15]=M*w+v*H+b*Y+N*ve,this}multiplyScalar(e){const t=this.elements;return t[0]*=e,t[4]*=e,t[8]*=e,t[12]*=e,t[1]*=e,t[5]*=e,t[9]*=e,t[13]*=e,t[2]*=e,t[6]*=e,t[10]*=e,t[14]*=e,t[3]*=e,t[7]*=e,t[11]*=e,t[15]*=e,this}determinant(){const e=this.elements,t=e[0],n=e[4],s=e[8],r=e[12],a=e[1],o=e[5],l=e[9],c=e[13],h=e[2],u=e[6],d=e[10],f=e[14],g=e[3],_=e[7],p=e[11],m=e[15];return g*(+r*l*u-s*c*u-r*o*d+n*c*d+s*o*f-n*l*f)+_*(+t*l*f-t*c*d+r*a*d-s*a*f+s*c*h-r*l*h)+p*(+t*c*u-t*o*f-r*a*u+n*a*f+r*o*h-n*c*h)+m*(-s*o*h-t*l*u+t*o*d+s*a*u-n*a*d+n*l*h)}transpose(){const e=this.elements;let t;return t=e[1],e[1]=e[4],e[4]=t,t=e[2],e[2]=e[8],e[8]=t,t=e[6],e[6]=e[9],e[9]=t,t=e[3],e[3]=e[12],e[12]=t,t=e[7],e[7]=e[13],e[13]=t,t=e[11],e[11]=e[14],e[14]=t,this}setPosition(e,t,n){const s=this.elements;return e.isVector3?(s[12]=e.x,s[13]=e.y,s[14]=e.z):(s[12]=e,s[13]=t,s[14]=n),this}invert(){const e=this.elements,t=e[0],n=e[1],s=e[2],r=e[3],a=e[4],o=e[5],l=e[6],c=e[7],h=e[8],u=e[9],d=e[10],f=e[11],g=e[12],_=e[13],p=e[14],m=e[15],M=u*p*c-_*d*c+_*l*f-o*p*f-u*l*m+o*d*m,v=g*d*c-h*p*c-g*l*f+a*p*f+h*l*m-a*d*m,b=h*_*c-g*u*c+g*o*f-a*_*f-h*o*m+a*u*m,N=g*u*l-h*_*l-g*o*d+a*_*d+h*o*p-a*u*p,A=t*M+n*v+s*b+r*N;if(A===0)return this.set(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);const R=1/A;return e[0]=M*R,e[1]=(_*d*r-u*p*r-_*s*f+n*p*f+u*s*m-n*d*m)*R,e[2]=(o*p*r-_*l*r+_*s*c-n*p*c-o*s*m+n*l*m)*R,e[3]=(u*l*r-o*d*r-u*s*c+n*d*c+o*s*f-n*l*f)*R,e[4]=v*R,e[5]=(h*p*r-g*d*r+g*s*f-t*p*f-h*s*m+t*d*m)*R,e[6]=(g*l*r-a*p*r-g*s*c+t*p*c+a*s*m-t*l*m)*R,e[7]=(a*d*r-h*l*r+h*s*c-t*d*c-a*s*f+t*l*f)*R,e[8]=b*R,e[9]=(g*u*r-h*_*r-g*n*f+t*_*f+h*n*m-t*u*m)*R,e[10]=(a*_*r-g*o*r+g*n*c-t*_*c-a*n*m+t*o*m)*R,e[11]=(h*o*r-a*u*r-h*n*c+t*u*c+a*n*f-t*o*f)*R,e[12]=N*R,e[13]=(h*_*s-g*u*s+g*n*d-t*_*d-h*n*p+t*u*p)*R,e[14]=(g*o*s-a*_*s-g*n*l+t*_*l+a*n*p-t*o*p)*R,e[15]=(a*u*s-h*o*s+h*n*l-t*u*l-a*n*d+t*o*d)*R,this}scale(e){const t=this.elements,n=e.x,s=e.y,r=e.z;return t[0]*=n,t[4]*=s,t[8]*=r,t[1]*=n,t[5]*=s,t[9]*=r,t[2]*=n,t[6]*=s,t[10]*=r,t[3]*=n,t[7]*=s,t[11]*=r,this}getMaxScaleOnAxis(){const e=this.elements,t=e[0]*e[0]+e[1]*e[1]+e[2]*e[2],n=e[4]*e[4]+e[5]*e[5]+e[6]*e[6],s=e[8]*e[8]+e[9]*e[9]+e[10]*e[10];return Math.sqrt(Math.max(t,n,s))}makeTranslation(e,t,n){return e.isVector3?this.set(1,0,0,e.x,0,1,0,e.y,0,0,1,e.z,0,0,0,1):this.set(1,0,0,e,0,1,0,t,0,0,1,n,0,0,0,1),this}makeRotationX(e){const t=Math.cos(e),n=Math.sin(e);return this.set(1,0,0,0,0,t,-n,0,0,n,t,0,0,0,0,1),this}makeRotationY(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,0,n,0,0,1,0,0,-n,0,t,0,0,0,0,1),this}makeRotationZ(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,-n,0,0,n,t,0,0,0,0,1,0,0,0,0,1),this}makeRotationAxis(e,t){const n=Math.cos(t),s=Math.sin(t),r=1-n,a=e.x,o=e.y,l=e.z,c=r*a,h=r*o;return this.set(c*a+n,c*o-s*l,c*l+s*o,0,c*o+s*l,h*o+n,h*l-s*a,0,c*l-s*o,h*l+s*a,r*l*l+n,0,0,0,0,1),this}makeScale(e,t,n){return this.set(e,0,0,0,0,t,0,0,0,0,n,0,0,0,0,1),this}makeShear(e,t,n,s,r,a){return this.set(1,n,r,0,e,1,a,0,t,s,1,0,0,0,0,1),this}compose(e,t,n){const s=this.elements,r=t._x,a=t._y,o=t._z,l=t._w,c=r+r,h=a+a,u=o+o,d=r*c,f=r*h,g=r*u,_=a*h,p=a*u,m=o*u,M=l*c,v=l*h,b=l*u,N=n.x,A=n.y,R=n.z;return s[0]=(1-(_+m))*N,s[1]=(f+b)*N,s[2]=(g-v)*N,s[3]=0,s[4]=(f-b)*A,s[5]=(1-(d+m))*A,s[6]=(p+M)*A,s[7]=0,s[8]=(g+v)*R,s[9]=(p-M)*R,s[10]=(1-(d+_))*R,s[11]=0,s[12]=e.x,s[13]=e.y,s[14]=e.z,s[15]=1,this}decompose(e,t,n){const s=this.elements;let r=mr.set(s[0],s[1],s[2]).length();const a=mr.set(s[4],s[5],s[6]).length(),o=mr.set(s[8],s[9],s[10]).length();this.determinant()<0&&(r=-r),e.x=s[12],e.y=s[13],e.z=s[14],ai.copy(this);const c=1/r,h=1/a,u=1/o;return ai.elements[0]*=c,ai.elements[1]*=c,ai.elements[2]*=c,ai.elements[4]*=h,ai.elements[5]*=h,ai.elements[6]*=h,ai.elements[8]*=u,ai.elements[9]*=u,ai.elements[10]*=u,t.setFromRotationMatrix(ai),n.x=r,n.y=a,n.z=o,this}makePerspective(e,t,n,s,r,a,o=Wi){const l=this.elements,c=2*r/(t-e),h=2*r/(n-s),u=(t+e)/(t-e),d=(n+s)/(n-s);let f,g;if(o===Wi)f=-(a+r)/(a-r),g=-2*a*r/(a-r);else if(o===Jo)f=-a/(a-r),g=-a*r/(a-r);else throw new Error("THREE.Matrix4.makePerspective(): Invalid coordinate system: "+o);return l[0]=c,l[4]=0,l[8]=u,l[12]=0,l[1]=0,l[5]=h,l[9]=d,l[13]=0,l[2]=0,l[6]=0,l[10]=f,l[14]=g,l[3]=0,l[7]=0,l[11]=-1,l[15]=0,this}makeOrthographic(e,t,n,s,r,a,o=Wi){const l=this.elements,c=1/(t-e),h=1/(n-s),u=1/(a-r),d=(t+e)*c,f=(n+s)*h;let g,_;if(o===Wi)g=(a+r)*u,_=-2*u;else if(o===Jo)g=r*u,_=-1*u;else throw new Error("THREE.Matrix4.makeOrthographic(): Invalid coordinate system: "+o);return l[0]=2*c,l[4]=0,l[8]=0,l[12]=-d,l[1]=0,l[5]=2*h,l[9]=0,l[13]=-f,l[2]=0,l[6]=0,l[10]=_,l[14]=-g,l[3]=0,l[7]=0,l[11]=0,l[15]=1,this}equals(e){const t=this.elements,n=e.elements;for(let s=0;s<16;s++)if(t[s]!==n[s])return!1;return!0}fromArray(e,t=0){for(let n=0;n<16;n++)this.elements[n]=e[n+t];return this}toArray(e=[],t=0){const n=this.elements;return e[t]=n[0],e[t+1]=n[1],e[t+2]=n[2],e[t+3]=n[3],e[t+4]=n[4],e[t+5]=n[5],e[t+6]=n[6],e[t+7]=n[7],e[t+8]=n[8],e[t+9]=n[9],e[t+10]=n[10],e[t+11]=n[11],e[t+12]=n[12],e[t+13]=n[13],e[t+14]=n[14],e[t+15]=n[15],e}}const mr=new V,ai=new Bt,Jg=new V(0,0,0),Qg=new V(1,1,1),rs=new V,co=new V,kn=new V,Fu=new Bt,Ou=new Ys;class Ci{constructor(e=0,t=0,n=0,s=Ci.DEFAULT_ORDER){this.isEuler=!0,this._x=e,this._y=t,this._z=n,this._order=s}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get order(){return this._order}set order(e){this._order=e,this._onChangeCallback()}set(e,t,n,s=this._order){return this._x=e,this._y=t,this._z=n,this._order=s,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._order)}copy(e){return this._x=e._x,this._y=e._y,this._z=e._z,this._order=e._order,this._onChangeCallback(),this}setFromRotationMatrix(e,t=this._order,n=!0){const s=e.elements,r=s[0],a=s[4],o=s[8],l=s[1],c=s[5],h=s[9],u=s[2],d=s[6],f=s[10];switch(t){case"XYZ":this._y=Math.asin(Sn(o,-1,1)),Math.abs(o)<.9999999?(this._x=Math.atan2(-h,f),this._z=Math.atan2(-a,r)):(this._x=Math.atan2(d,c),this._z=0);break;case"YXZ":this._x=Math.asin(-Sn(h,-1,1)),Math.abs(h)<.9999999?(this._y=Math.atan2(o,f),this._z=Math.atan2(l,c)):(this._y=Math.atan2(-u,r),this._z=0);break;case"ZXY":this._x=Math.asin(Sn(d,-1,1)),Math.abs(d)<.9999999?(this._y=Math.atan2(-u,f),this._z=Math.atan2(-a,c)):(this._y=0,this._z=Math.atan2(l,r));break;case"ZYX":this._y=Math.asin(-Sn(u,-1,1)),Math.abs(u)<.9999999?(this._x=Math.atan2(d,f),this._z=Math.atan2(l,r)):(this._x=0,this._z=Math.atan2(-a,c));break;case"YZX":this._z=Math.asin(Sn(l,-1,1)),Math.abs(l)<.9999999?(this._x=Math.atan2(-h,c),this._y=Math.atan2(-u,r)):(this._x=0,this._y=Math.atan2(o,f));break;case"XZY":this._z=Math.asin(-Sn(a,-1,1)),Math.abs(a)<.9999999?(this._x=Math.atan2(d,c),this._y=Math.atan2(o,r)):(this._x=Math.atan2(-h,f),this._y=0);break;default:console.warn("THREE.Euler: .setFromRotationMatrix() encountered an unknown order: "+t)}return this._order=t,n===!0&&this._onChangeCallback(),this}setFromQuaternion(e,t,n){return Fu.makeRotationFromQuaternion(e),this.setFromRotationMatrix(Fu,t,n)}setFromVector3(e,t=this._order){return this.set(e.x,e.y,e.z,t)}reorder(e){return Ou.setFromEuler(this),this.setFromQuaternion(Ou,e)}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._order===this._order}fromArray(e){return this._x=e[0],this._y=e[1],this._z=e[2],e[3]!==void 0&&(this._order=e[3]),this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._order,e}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._order}}Ci.DEFAULT_ORDER="XYZ";class Ph{constructor(){this.mask=1}set(e){this.mask=(1<<e|0)>>>0}enable(e){this.mask|=1<<e|0}enableAll(){this.mask=-1}toggle(e){this.mask^=1<<e|0}disable(e){this.mask&=~(1<<e|0)}disableAll(){this.mask=0}test(e){return(this.mask&e.mask)!==0}isEnabled(e){return(this.mask&(1<<e|0))!==0}}let e_=0;const Bu=new V,gr=new Ys,Bi=new Bt,ho=new V,xa=new V,t_=new V,n_=new Ys,zu=new V(1,0,0),ku=new V(0,1,0),Hu=new V(0,0,1),Vu={type:"added"},i_={type:"removed"},_r={type:"childadded",child:null},Kl={type:"childremoved",child:null};class en extends ta{constructor(){super(),this.isObject3D=!0,Object.defineProperty(this,"id",{value:e_++}),this.uuid=Xi(),this.name="",this.type="Object3D",this.parent=null,this.children=[],this.up=en.DEFAULT_UP.clone();const e=new V,t=new Ci,n=new Ys,s=new V(1,1,1);function r(){n.setFromEuler(t,!1)}function a(){t.setFromQuaternion(n,void 0,!1)}t._onChange(r),n._onChange(a),Object.defineProperties(this,{position:{configurable:!0,enumerable:!0,value:e},rotation:{configurable:!0,enumerable:!0,value:t},quaternion:{configurable:!0,enumerable:!0,value:n},scale:{configurable:!0,enumerable:!0,value:s},modelViewMatrix:{value:new Bt},normalMatrix:{value:new at}}),this.matrix=new Bt,this.matrixWorld=new Bt,this.matrixAutoUpdate=en.DEFAULT_MATRIX_AUTO_UPDATE,this.matrixWorldAutoUpdate=en.DEFAULT_MATRIX_WORLD_AUTO_UPDATE,this.matrixWorldNeedsUpdate=!1,this.layers=new Ph,this.visible=!0,this.castShadow=!1,this.receiveShadow=!1,this.frustumCulled=!0,this.renderOrder=0,this.animations=[],this.userData={}}onBeforeShadow(){}onAfterShadow(){}onBeforeRender(){}onAfterRender(){}applyMatrix4(e){this.matrixAutoUpdate&&this.updateMatrix(),this.matrix.premultiply(e),this.matrix.decompose(this.position,this.quaternion,this.scale)}applyQuaternion(e){return this.quaternion.premultiply(e),this}setRotationFromAxisAngle(e,t){this.quaternion.setFromAxisAngle(e,t)}setRotationFromEuler(e){this.quaternion.setFromEuler(e,!0)}setRotationFromMatrix(e){this.quaternion.setFromRotationMatrix(e)}setRotationFromQuaternion(e){this.quaternion.copy(e)}rotateOnAxis(e,t){return gr.setFromAxisAngle(e,t),this.quaternion.multiply(gr),this}rotateOnWorldAxis(e,t){return gr.setFromAxisAngle(e,t),this.quaternion.premultiply(gr),this}rotateX(e){return this.rotateOnAxis(zu,e)}rotateY(e){return this.rotateOnAxis(ku,e)}rotateZ(e){return this.rotateOnAxis(Hu,e)}translateOnAxis(e,t){return Bu.copy(e).applyQuaternion(this.quaternion),this.position.add(Bu.multiplyScalar(t)),this}translateX(e){return this.translateOnAxis(zu,e)}translateY(e){return this.translateOnAxis(ku,e)}translateZ(e){return this.translateOnAxis(Hu,e)}localToWorld(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(this.matrixWorld)}worldToLocal(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(Bi.copy(this.matrixWorld).invert())}lookAt(e,t,n){e.isVector3?ho.copy(e):ho.set(e,t,n);const s=this.parent;this.updateWorldMatrix(!0,!1),xa.setFromMatrixPosition(this.matrixWorld),this.isCamera||this.isLight?Bi.lookAt(xa,ho,this.up):Bi.lookAt(ho,xa,this.up),this.quaternion.setFromRotationMatrix(Bi),s&&(Bi.extractRotation(s.matrixWorld),gr.setFromRotationMatrix(Bi),this.quaternion.premultiply(gr.invert()))}add(e){if(arguments.length>1){for(let t=0;t<arguments.length;t++)this.add(arguments[t]);return this}return e===this?(console.error("THREE.Object3D.add: object can't be added as a child of itself.",e),this):(e&&e.isObject3D?(e.removeFromParent(),e.parent=this,this.children.push(e),e.dispatchEvent(Vu),_r.child=e,this.dispatchEvent(_r),_r.child=null):console.error("THREE.Object3D.add: object not an instance of THREE.Object3D.",e),this)}remove(e){if(arguments.length>1){for(let n=0;n<arguments.length;n++)this.remove(arguments[n]);return this}const t=this.children.indexOf(e);return t!==-1&&(e.parent=null,this.children.splice(t,1),e.dispatchEvent(i_),Kl.child=e,this.dispatchEvent(Kl),Kl.child=null),this}removeFromParent(){const e=this.parent;return e!==null&&e.remove(this),this}clear(){return this.remove(...this.children)}attach(e){return this.updateWorldMatrix(!0,!1),Bi.copy(this.matrixWorld).invert(),e.parent!==null&&(e.parent.updateWorldMatrix(!0,!1),Bi.multiply(e.parent.matrixWorld)),e.applyMatrix4(Bi),e.removeFromParent(),e.parent=this,this.children.push(e),e.updateWorldMatrix(!1,!0),e.dispatchEvent(Vu),_r.child=e,this.dispatchEvent(_r),_r.child=null,this}getObjectById(e){return this.getObjectByProperty("id",e)}getObjectByName(e){return this.getObjectByProperty("name",e)}getObjectByProperty(e,t){if(this[e]===t)return this;for(let n=0,s=this.children.length;n<s;n++){const a=this.children[n].getObjectByProperty(e,t);if(a!==void 0)return a}}getObjectsByProperty(e,t,n=[]){this[e]===t&&n.push(this);const s=this.children;for(let r=0,a=s.length;r<a;r++)s[r].getObjectsByProperty(e,t,n);return n}getWorldPosition(e){return this.updateWorldMatrix(!0,!1),e.setFromMatrixPosition(this.matrixWorld)}getWorldQuaternion(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(xa,e,t_),e}getWorldScale(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(xa,n_,e),e}getWorldDirection(e){this.updateWorldMatrix(!0,!1);const t=this.matrixWorld.elements;return e.set(t[8],t[9],t[10]).normalize()}raycast(){}traverse(e){e(this);const t=this.children;for(let n=0,s=t.length;n<s;n++)t[n].traverse(e)}traverseVisible(e){if(this.visible===!1)return;e(this);const t=this.children;for(let n=0,s=t.length;n<s;n++)t[n].traverseVisible(e)}traverseAncestors(e){const t=this.parent;t!==null&&(e(t),t.traverseAncestors(e))}updateMatrix(){this.matrix.compose(this.position,this.quaternion,this.scale),this.matrixWorldNeedsUpdate=!0}updateMatrixWorld(e){this.matrixAutoUpdate&&this.updateMatrix(),(this.matrixWorldNeedsUpdate||e)&&(this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),this.matrixWorldNeedsUpdate=!1,e=!0);const t=this.children;for(let n=0,s=t.length;n<s;n++)t[n].updateMatrixWorld(e)}updateWorldMatrix(e,t){const n=this.parent;if(e===!0&&n!==null&&n.updateWorldMatrix(!0,!1),this.matrixAutoUpdate&&this.updateMatrix(),this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),t===!0){const s=this.children;for(let r=0,a=s.length;r<a;r++)s[r].updateWorldMatrix(!1,!0)}}toJSON(e){const t=e===void 0||typeof e=="string",n={};t&&(e={geometries:{},materials:{},textures:{},images:{},shapes:{},skeletons:{},animations:{},nodes:{}},n.metadata={version:4.6,type:"Object",generator:"Object3D.toJSON"});const s={};s.uuid=this.uuid,s.type=this.type,this.name!==""&&(s.name=this.name),this.castShadow===!0&&(s.castShadow=!0),this.receiveShadow===!0&&(s.receiveShadow=!0),this.visible===!1&&(s.visible=!1),this.frustumCulled===!1&&(s.frustumCulled=!1),this.renderOrder!==0&&(s.renderOrder=this.renderOrder),Object.keys(this.userData).length>0&&(s.userData=this.userData),s.layers=this.layers.mask,s.matrix=this.matrix.toArray(),s.up=this.up.toArray(),this.matrixAutoUpdate===!1&&(s.matrixAutoUpdate=!1),this.isInstancedMesh&&(s.type="InstancedMesh",s.count=this.count,s.instanceMatrix=this.instanceMatrix.toJSON(),this.instanceColor!==null&&(s.instanceColor=this.instanceColor.toJSON())),this.isBatchedMesh&&(s.type="BatchedMesh",s.perObjectFrustumCulled=this.perObjectFrustumCulled,s.sortObjects=this.sortObjects,s.drawRanges=this._drawRanges,s.reservedRanges=this._reservedRanges,s.visibility=this._visibility,s.active=this._active,s.bounds=this._bounds.map(o=>({boxInitialized:o.boxInitialized,boxMin:o.box.min.toArray(),boxMax:o.box.max.toArray(),sphereInitialized:o.sphereInitialized,sphereRadius:o.sphere.radius,sphereCenter:o.sphere.center.toArray()})),s.maxInstanceCount=this._maxInstanceCount,s.maxVertexCount=this._maxVertexCount,s.maxIndexCount=this._maxIndexCount,s.geometryInitialized=this._geometryInitialized,s.geometryCount=this._geometryCount,s.matricesTexture=this._matricesTexture.toJSON(e),this._colorsTexture!==null&&(s.colorsTexture=this._colorsTexture.toJSON(e)),this.boundingSphere!==null&&(s.boundingSphere={center:s.boundingSphere.center.toArray(),radius:s.boundingSphere.radius}),this.boundingBox!==null&&(s.boundingBox={min:s.boundingBox.min.toArray(),max:s.boundingBox.max.toArray()}));function r(o,l){return o[l.uuid]===void 0&&(o[l.uuid]=l.toJSON(e)),l.uuid}if(this.isScene)this.background&&(this.background.isColor?s.background=this.background.toJSON():this.background.isTexture&&(s.background=this.background.toJSON(e).uuid)),this.environment&&this.environment.isTexture&&this.environment.isRenderTargetTexture!==!0&&(s.environment=this.environment.toJSON(e).uuid);else if(this.isMesh||this.isLine||this.isPoints){s.geometry=r(e.geometries,this.geometry);const o=this.geometry.parameters;if(o!==void 0&&o.shapes!==void 0){const l=o.shapes;if(Array.isArray(l))for(let c=0,h=l.length;c<h;c++){const u=l[c];r(e.shapes,u)}else r(e.shapes,l)}}if(this.isSkinnedMesh&&(s.bindMode=this.bindMode,s.bindMatrix=this.bindMatrix.toArray(),this.skeleton!==void 0&&(r(e.skeletons,this.skeleton),s.skeleton=this.skeleton.uuid)),this.material!==void 0)if(Array.isArray(this.material)){const o=[];for(let l=0,c=this.material.length;l<c;l++)o.push(r(e.materials,this.material[l]));s.material=o}else s.material=r(e.materials,this.material);if(this.children.length>0){s.children=[];for(let o=0;o<this.children.length;o++)s.children.push(this.children[o].toJSON(e).object)}if(this.animations.length>0){s.animations=[];for(let o=0;o<this.animations.length;o++){const l=this.animations[o];s.animations.push(r(e.animations,l))}}if(t){const o=a(e.geometries),l=a(e.materials),c=a(e.textures),h=a(e.images),u=a(e.shapes),d=a(e.skeletons),f=a(e.animations),g=a(e.nodes);o.length>0&&(n.geometries=o),l.length>0&&(n.materials=l),c.length>0&&(n.textures=c),h.length>0&&(n.images=h),u.length>0&&(n.shapes=u),d.length>0&&(n.skeletons=d),f.length>0&&(n.animations=f),g.length>0&&(n.nodes=g)}return n.object=s,n;function a(o){const l=[];for(const c in o){const h=o[c];delete h.metadata,l.push(h)}return l}}clone(e){return new this.constructor().copy(this,e)}copy(e,t=!0){if(this.name=e.name,this.up.copy(e.up),this.position.copy(e.position),this.rotation.order=e.rotation.order,this.quaternion.copy(e.quaternion),this.scale.copy(e.scale),this.matrix.copy(e.matrix),this.matrixWorld.copy(e.matrixWorld),this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrixWorldAutoUpdate=e.matrixWorldAutoUpdate,this.matrixWorldNeedsUpdate=e.matrixWorldNeedsUpdate,this.layers.mask=e.layers.mask,this.visible=e.visible,this.castShadow=e.castShadow,this.receiveShadow=e.receiveShadow,this.frustumCulled=e.frustumCulled,this.renderOrder=e.renderOrder,this.animations=e.animations.slice(),this.userData=JSON.parse(JSON.stringify(e.userData)),t===!0)for(let n=0;n<e.children.length;n++){const s=e.children[n];this.add(s.clone())}return this}}en.DEFAULT_UP=new V(0,1,0);en.DEFAULT_MATRIX_AUTO_UPDATE=!0;en.DEFAULT_MATRIX_WORLD_AUTO_UPDATE=!0;const oi=new V,zi=new V,Zl=new V,ki=new V,xr=new V,vr=new V,Gu=new V,Jl=new V,Ql=new V,ec=new V;class Qn{constructor(e=new V,t=new V,n=new V){this.a=e,this.b=t,this.c=n}static getNormal(e,t,n,s){s.subVectors(n,t),oi.subVectors(e,t),s.cross(oi);const r=s.lengthSq();return r>0?s.multiplyScalar(1/Math.sqrt(r)):s.set(0,0,0)}static getBarycoord(e,t,n,s,r){oi.subVectors(s,t),zi.subVectors(n,t),Zl.subVectors(e,t);const a=oi.dot(oi),o=oi.dot(zi),l=oi.dot(Zl),c=zi.dot(zi),h=zi.dot(Zl),u=a*c-o*o;if(u===0)return r.set(0,0,0),null;const d=1/u,f=(c*l-o*h)*d,g=(a*h-o*l)*d;return r.set(1-f-g,g,f)}static containsPoint(e,t,n,s){return this.getBarycoord(e,t,n,s,ki)===null?!1:ki.x>=0&&ki.y>=0&&ki.x+ki.y<=1}static getInterpolation(e,t,n,s,r,a,o,l){return this.getBarycoord(e,t,n,s,ki)===null?(l.x=0,l.y=0,"z"in l&&(l.z=0),"w"in l&&(l.w=0),null):(l.setScalar(0),l.addScaledVector(r,ki.x),l.addScaledVector(a,ki.y),l.addScaledVector(o,ki.z),l)}static isFrontFacing(e,t,n,s){return oi.subVectors(n,t),zi.subVectors(e,t),oi.cross(zi).dot(s)<0}set(e,t,n){return this.a.copy(e),this.b.copy(t),this.c.copy(n),this}setFromPointsAndIndices(e,t,n,s){return this.a.copy(e[t]),this.b.copy(e[n]),this.c.copy(e[s]),this}setFromAttributeAndIndices(e,t,n,s){return this.a.fromBufferAttribute(e,t),this.b.fromBufferAttribute(e,n),this.c.fromBufferAttribute(e,s),this}clone(){return new this.constructor().copy(this)}copy(e){return this.a.copy(e.a),this.b.copy(e.b),this.c.copy(e.c),this}getArea(){return oi.subVectors(this.c,this.b),zi.subVectors(this.a,this.b),oi.cross(zi).length()*.5}getMidpoint(e){return e.addVectors(this.a,this.b).add(this.c).multiplyScalar(1/3)}getNormal(e){return Qn.getNormal(this.a,this.b,this.c,e)}getPlane(e){return e.setFromCoplanarPoints(this.a,this.b,this.c)}getBarycoord(e,t){return Qn.getBarycoord(e,this.a,this.b,this.c,t)}getInterpolation(e,t,n,s,r){return Qn.getInterpolation(e,this.a,this.b,this.c,t,n,s,r)}containsPoint(e){return Qn.containsPoint(e,this.a,this.b,this.c)}isFrontFacing(e){return Qn.isFrontFacing(this.a,this.b,this.c,e)}intersectsBox(e){return e.intersectsTriangle(this)}closestPointToPoint(e,t){const n=this.a,s=this.b,r=this.c;let a,o;xr.subVectors(s,n),vr.subVectors(r,n),Jl.subVectors(e,n);const l=xr.dot(Jl),c=vr.dot(Jl);if(l<=0&&c<=0)return t.copy(n);Ql.subVectors(e,s);const h=xr.dot(Ql),u=vr.dot(Ql);if(h>=0&&u<=h)return t.copy(s);const d=l*u-h*c;if(d<=0&&l>=0&&h<=0)return a=l/(l-h),t.copy(n).addScaledVector(xr,a);ec.subVectors(e,r);const f=xr.dot(ec),g=vr.dot(ec);if(g>=0&&f<=g)return t.copy(r);const _=f*c-l*g;if(_<=0&&c>=0&&g<=0)return o=c/(c-g),t.copy(n).addScaledVector(vr,o);const p=h*g-f*u;if(p<=0&&u-h>=0&&f-g>=0)return Gu.subVectors(r,s),o=(u-h)/(u-h+(f-g)),t.copy(s).addScaledVector(Gu,o);const m=1/(p+_+d);return a=_*m,o=d*m,t.copy(n).addScaledVector(xr,a).addScaledVector(vr,o)}equals(e){return e.a.equals(this.a)&&e.b.equals(this.b)&&e.c.equals(this.c)}}const ep={aliceblue:15792383,antiquewhite:16444375,aqua:65535,aquamarine:8388564,azure:15794175,beige:16119260,bisque:16770244,black:0,blanchedalmond:16772045,blue:255,blueviolet:9055202,brown:10824234,burlywood:14596231,cadetblue:6266528,chartreuse:8388352,chocolate:13789470,coral:16744272,cornflowerblue:6591981,cornsilk:16775388,crimson:14423100,cyan:65535,darkblue:139,darkcyan:35723,darkgoldenrod:12092939,darkgray:11119017,darkgreen:25600,darkgrey:11119017,darkkhaki:12433259,darkmagenta:9109643,darkolivegreen:5597999,darkorange:16747520,darkorchid:10040012,darkred:9109504,darksalmon:15308410,darkseagreen:9419919,darkslateblue:4734347,darkslategray:3100495,darkslategrey:3100495,darkturquoise:52945,darkviolet:9699539,deeppink:16716947,deepskyblue:49151,dimgray:6908265,dimgrey:6908265,dodgerblue:2003199,firebrick:11674146,floralwhite:16775920,forestgreen:2263842,fuchsia:16711935,gainsboro:14474460,ghostwhite:16316671,gold:16766720,goldenrod:14329120,gray:8421504,green:32768,greenyellow:11403055,grey:8421504,honeydew:15794160,hotpink:16738740,indianred:13458524,indigo:4915330,ivory:16777200,khaki:15787660,lavender:15132410,lavenderblush:16773365,lawngreen:8190976,lemonchiffon:16775885,lightblue:11393254,lightcoral:15761536,lightcyan:14745599,lightgoldenrodyellow:16448210,lightgray:13882323,lightgreen:9498256,lightgrey:13882323,lightpink:16758465,lightsalmon:16752762,lightseagreen:2142890,lightskyblue:8900346,lightslategray:7833753,lightslategrey:7833753,lightsteelblue:11584734,lightyellow:16777184,lime:65280,limegreen:3329330,linen:16445670,magenta:16711935,maroon:8388608,mediumaquamarine:6737322,mediumblue:205,mediumorchid:12211667,mediumpurple:9662683,mediumseagreen:3978097,mediumslateblue:8087790,mediumspringgreen:64154,mediumturquoise:4772300,mediumvioletred:13047173,midnightblue:1644912,mintcream:16121850,mistyrose:16770273,moccasin:16770229,navajowhite:16768685,navy:128,oldlace:16643558,olive:8421376,olivedrab:7048739,orange:16753920,orangered:16729344,orchid:14315734,palegoldenrod:15657130,palegreen:10025880,paleturquoise:11529966,palevioletred:14381203,papayawhip:16773077,peachpuff:16767673,peru:13468991,pink:16761035,plum:14524637,powderblue:11591910,purple:8388736,rebeccapurple:6697881,red:16711680,rosybrown:12357519,royalblue:4286945,saddlebrown:9127187,salmon:16416882,sandybrown:16032864,seagreen:3050327,seashell:16774638,sienna:10506797,silver:12632256,skyblue:8900331,slateblue:6970061,slategray:7372944,slategrey:7372944,snow:16775930,springgreen:65407,steelblue:4620980,tan:13808780,teal:32896,thistle:14204888,tomato:16737095,turquoise:4251856,violet:15631086,wheat:16113331,white:16777215,whitesmoke:16119285,yellow:16776960,yellowgreen:10145074},as={h:0,s:0,l:0},uo={h:0,s:0,l:0};function tc(i,e,t){return t<0&&(t+=1),t>1&&(t-=1),t<1/6?i+(e-i)*6*t:t<1/2?e:t<2/3?i+(e-i)*6*(2/3-t):i}class nt{constructor(e,t,n){return this.isColor=!0,this.r=1,this.g=1,this.b=1,this.set(e,t,n)}set(e,t,n){if(t===void 0&&n===void 0){const s=e;s&&s.isColor?this.copy(s):typeof s=="number"?this.setHex(s):typeof s=="string"&&this.setStyle(s)}else this.setRGB(e,t,n);return this}setScalar(e){return this.r=e,this.g=e,this.b=e,this}setHex(e,t=bi){return e=Math.floor(e),this.r=(e>>16&255)/255,this.g=(e>>8&255)/255,this.b=(e&255)/255,bt.toWorkingColorSpace(this,t),this}setRGB(e,t,n,s=bt.workingColorSpace){return this.r=e,this.g=t,this.b=n,bt.toWorkingColorSpace(this,s),this}setHSL(e,t,n,s=bt.workingColorSpace){if(e=Ch(e,1),t=Sn(t,0,1),n=Sn(n,0,1),t===0)this.r=this.g=this.b=n;else{const r=n<=.5?n*(1+t):n+t-n*t,a=2*n-r;this.r=tc(a,r,e+1/3),this.g=tc(a,r,e),this.b=tc(a,r,e-1/3)}return bt.toWorkingColorSpace(this,s),this}setStyle(e,t=bi){function n(r){r!==void 0&&parseFloat(r)<1&&console.warn("THREE.Color: Alpha component of "+e+" will be ignored.")}let s;if(s=/^(\w+)\(([^\)]*)\)/.exec(e)){let r;const a=s[1],o=s[2];switch(a){case"rgb":case"rgba":if(r=/^\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(o))return n(r[4]),this.setRGB(Math.min(255,parseInt(r[1],10))/255,Math.min(255,parseInt(r[2],10))/255,Math.min(255,parseInt(r[3],10))/255,t);if(r=/^\s*(\d+)\%\s*,\s*(\d+)\%\s*,\s*(\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(o))return n(r[4]),this.setRGB(Math.min(100,parseInt(r[1],10))/100,Math.min(100,parseInt(r[2],10))/100,Math.min(100,parseInt(r[3],10))/100,t);break;case"hsl":case"hsla":if(r=/^\s*(\d*\.?\d+)\s*,\s*(\d*\.?\d+)\%\s*,\s*(\d*\.?\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(o))return n(r[4]),this.setHSL(parseFloat(r[1])/360,parseFloat(r[2])/100,parseFloat(r[3])/100,t);break;default:console.warn("THREE.Color: Unknown color model "+e)}}else if(s=/^\#([A-Fa-f\d]+)$/.exec(e)){const r=s[1],a=r.length;if(a===3)return this.setRGB(parseInt(r.charAt(0),16)/15,parseInt(r.charAt(1),16)/15,parseInt(r.charAt(2),16)/15,t);if(a===6)return this.setHex(parseInt(r,16),t);console.warn("THREE.Color: Invalid hex color "+e)}else if(e&&e.length>0)return this.setColorName(e,t);return this}setColorName(e,t=bi){const n=ep[e.toLowerCase()];return n!==void 0?this.setHex(n,t):console.warn("THREE.Color: Unknown color "+e),this}clone(){return new this.constructor(this.r,this.g,this.b)}copy(e){return this.r=e.r,this.g=e.g,this.b=e.b,this}copySRGBToLinear(e){return this.r=Hr(e.r),this.g=Hr(e.g),this.b=Hr(e.b),this}copyLinearToSRGB(e){return this.r=Vl(e.r),this.g=Vl(e.g),this.b=Vl(e.b),this}convertSRGBToLinear(){return this.copySRGBToLinear(this),this}convertLinearToSRGB(){return this.copyLinearToSRGB(this),this}getHex(e=bi){return bt.fromWorkingColorSpace(Mn.copy(this),e),Math.round(Sn(Mn.r*255,0,255))*65536+Math.round(Sn(Mn.g*255,0,255))*256+Math.round(Sn(Mn.b*255,0,255))}getHexString(e=bi){return("000000"+this.getHex(e).toString(16)).slice(-6)}getHSL(e,t=bt.workingColorSpace){bt.fromWorkingColorSpace(Mn.copy(this),t);const n=Mn.r,s=Mn.g,r=Mn.b,a=Math.max(n,s,r),o=Math.min(n,s,r);let l,c;const h=(o+a)/2;if(o===a)l=0,c=0;else{const u=a-o;switch(c=h<=.5?u/(a+o):u/(2-a-o),a){case n:l=(s-r)/u+(s<r?6:0);break;case s:l=(r-n)/u+2;break;case r:l=(n-s)/u+4;break}l/=6}return e.h=l,e.s=c,e.l=h,e}getRGB(e,t=bt.workingColorSpace){return bt.fromWorkingColorSpace(Mn.copy(this),t),e.r=Mn.r,e.g=Mn.g,e.b=Mn.b,e}getStyle(e=bi){bt.fromWorkingColorSpace(Mn.copy(this),e);const t=Mn.r,n=Mn.g,s=Mn.b;return e!==bi?`color(${e} ${t.toFixed(3)} ${n.toFixed(3)} ${s.toFixed(3)})`:`rgb(${Math.round(t*255)},${Math.round(n*255)},${Math.round(s*255)})`}offsetHSL(e,t,n){return this.getHSL(as),this.setHSL(as.h+e,as.s+t,as.l+n)}add(e){return this.r+=e.r,this.g+=e.g,this.b+=e.b,this}addColors(e,t){return this.r=e.r+t.r,this.g=e.g+t.g,this.b=e.b+t.b,this}addScalar(e){return this.r+=e,this.g+=e,this.b+=e,this}sub(e){return this.r=Math.max(0,this.r-e.r),this.g=Math.max(0,this.g-e.g),this.b=Math.max(0,this.b-e.b),this}multiply(e){return this.r*=e.r,this.g*=e.g,this.b*=e.b,this}multiplyScalar(e){return this.r*=e,this.g*=e,this.b*=e,this}lerp(e,t){return this.r+=(e.r-this.r)*t,this.g+=(e.g-this.g)*t,this.b+=(e.b-this.b)*t,this}lerpColors(e,t,n){return this.r=e.r+(t.r-e.r)*n,this.g=e.g+(t.g-e.g)*n,this.b=e.b+(t.b-e.b)*n,this}lerpHSL(e,t){this.getHSL(as),e.getHSL(uo);const n=Da(as.h,uo.h,t),s=Da(as.s,uo.s,t),r=Da(as.l,uo.l,t);return this.setHSL(n,s,r),this}setFromVector3(e){return this.r=e.x,this.g=e.y,this.b=e.z,this}applyMatrix3(e){const t=this.r,n=this.g,s=this.b,r=e.elements;return this.r=r[0]*t+r[3]*n+r[6]*s,this.g=r[1]*t+r[4]*n+r[7]*s,this.b=r[2]*t+r[5]*n+r[8]*s,this}equals(e){return e.r===this.r&&e.g===this.g&&e.b===this.b}fromArray(e,t=0){return this.r=e[t],this.g=e[t+1],this.b=e[t+2],this}toArray(e=[],t=0){return e[t]=this.r,e[t+1]=this.g,e[t+2]=this.b,e}fromBufferAttribute(e,t){return this.r=e.getX(t),this.g=e.getY(t),this.b=e.getZ(t),this}toJSON(){return this.getHex()}*[Symbol.iterator](){yield this.r,yield this.g,yield this.b}}const Mn=new nt;nt.NAMES=ep;let s_=0;class Ss extends ta{constructor(){super(),this.isMaterial=!0,Object.defineProperty(this,"id",{value:s_++}),this.uuid=Xi(),this.name="",this.type="Material",this.blending=Or,this.side=gs,this.vertexColors=!1,this.opacity=1,this.transparent=!1,this.alphaHash=!1,this.blendSrc=Ac,this.blendDst=Rc,this.blendEquation=Os,this.blendSrcAlpha=null,this.blendDstAlpha=null,this.blendEquationAlpha=null,this.blendColor=new nt(0,0,0),this.blendAlpha=0,this.depthFunc=Yo,this.depthTest=!0,this.depthWrite=!0,this.stencilWriteMask=255,this.stencilFunc=Cu,this.stencilRef=0,this.stencilFuncMask=255,this.stencilFail=hr,this.stencilZFail=hr,this.stencilZPass=hr,this.stencilWrite=!1,this.clippingPlanes=null,this.clipIntersection=!1,this.clipShadows=!1,this.shadowSide=null,this.colorWrite=!0,this.precision=null,this.polygonOffset=!1,this.polygonOffsetFactor=0,this.polygonOffsetUnits=0,this.dithering=!1,this.alphaToCoverage=!1,this.premultipliedAlpha=!1,this.forceSinglePass=!1,this.visible=!0,this.toneMapped=!0,this.userData={},this.version=0,this._alphaTest=0}get alphaTest(){return this._alphaTest}set alphaTest(e){this._alphaTest>0!=e>0&&this.version++,this._alphaTest=e}onBeforeRender(){}onBeforeCompile(){}customProgramCacheKey(){return this.onBeforeCompile.toString()}setValues(e){if(e!==void 0)for(const t in e){const n=e[t];if(n===void 0){console.warn(`THREE.Material: parameter '${t}' has value of undefined.`);continue}const s=this[t];if(s===void 0){console.warn(`THREE.Material: '${t}' is not a property of THREE.${this.type}.`);continue}s&&s.isColor?s.set(n):s&&s.isVector3&&n&&n.isVector3?s.copy(n):this[t]=n}}toJSON(e){const t=e===void 0||typeof e=="string";t&&(e={textures:{},images:{}});const n={metadata:{version:4.6,type:"Material",generator:"Material.toJSON"}};n.uuid=this.uuid,n.type=this.type,this.name!==""&&(n.name=this.name),this.color&&this.color.isColor&&(n.color=this.color.getHex()),this.roughness!==void 0&&(n.roughness=this.roughness),this.metalness!==void 0&&(n.metalness=this.metalness),this.sheen!==void 0&&(n.sheen=this.sheen),this.sheenColor&&this.sheenColor.isColor&&(n.sheenColor=this.sheenColor.getHex()),this.sheenRoughness!==void 0&&(n.sheenRoughness=this.sheenRoughness),this.emissive&&this.emissive.isColor&&(n.emissive=this.emissive.getHex()),this.emissiveIntensity!==void 0&&this.emissiveIntensity!==1&&(n.emissiveIntensity=this.emissiveIntensity),this.specular&&this.specular.isColor&&(n.specular=this.specular.getHex()),this.specularIntensity!==void 0&&(n.specularIntensity=this.specularIntensity),this.specularColor&&this.specularColor.isColor&&(n.specularColor=this.specularColor.getHex()),this.shininess!==void 0&&(n.shininess=this.shininess),this.clearcoat!==void 0&&(n.clearcoat=this.clearcoat),this.clearcoatRoughness!==void 0&&(n.clearcoatRoughness=this.clearcoatRoughness),this.clearcoatMap&&this.clearcoatMap.isTexture&&(n.clearcoatMap=this.clearcoatMap.toJSON(e).uuid),this.clearcoatRoughnessMap&&this.clearcoatRoughnessMap.isTexture&&(n.clearcoatRoughnessMap=this.clearcoatRoughnessMap.toJSON(e).uuid),this.clearcoatNormalMap&&this.clearcoatNormalMap.isTexture&&(n.clearcoatNormalMap=this.clearcoatNormalMap.toJSON(e).uuid,n.clearcoatNormalScale=this.clearcoatNormalScale.toArray()),this.dispersion!==void 0&&(n.dispersion=this.dispersion),this.iridescence!==void 0&&(n.iridescence=this.iridescence),this.iridescenceIOR!==void 0&&(n.iridescenceIOR=this.iridescenceIOR),this.iridescenceThicknessRange!==void 0&&(n.iridescenceThicknessRange=this.iridescenceThicknessRange),this.iridescenceMap&&this.iridescenceMap.isTexture&&(n.iridescenceMap=this.iridescenceMap.toJSON(e).uuid),this.iridescenceThicknessMap&&this.iridescenceThicknessMap.isTexture&&(n.iridescenceThicknessMap=this.iridescenceThicknessMap.toJSON(e).uuid),this.anisotropy!==void 0&&(n.anisotropy=this.anisotropy),this.anisotropyRotation!==void 0&&(n.anisotropyRotation=this.anisotropyRotation),this.anisotropyMap&&this.anisotropyMap.isTexture&&(n.anisotropyMap=this.anisotropyMap.toJSON(e).uuid),this.map&&this.map.isTexture&&(n.map=this.map.toJSON(e).uuid),this.matcap&&this.matcap.isTexture&&(n.matcap=this.matcap.toJSON(e).uuid),this.alphaMap&&this.alphaMap.isTexture&&(n.alphaMap=this.alphaMap.toJSON(e).uuid),this.lightMap&&this.lightMap.isTexture&&(n.lightMap=this.lightMap.toJSON(e).uuid,n.lightMapIntensity=this.lightMapIntensity),this.aoMap&&this.aoMap.isTexture&&(n.aoMap=this.aoMap.toJSON(e).uuid,n.aoMapIntensity=this.aoMapIntensity),this.bumpMap&&this.bumpMap.isTexture&&(n.bumpMap=this.bumpMap.toJSON(e).uuid,n.bumpScale=this.bumpScale),this.normalMap&&this.normalMap.isTexture&&(n.normalMap=this.normalMap.toJSON(e).uuid,n.normalMapType=this.normalMapType,n.normalScale=this.normalScale.toArray()),this.displacementMap&&this.displacementMap.isTexture&&(n.displacementMap=this.displacementMap.toJSON(e).uuid,n.displacementScale=this.displacementScale,n.displacementBias=this.displacementBias),this.roughnessMap&&this.roughnessMap.isTexture&&(n.roughnessMap=this.roughnessMap.toJSON(e).uuid),this.metalnessMap&&this.metalnessMap.isTexture&&(n.metalnessMap=this.metalnessMap.toJSON(e).uuid),this.emissiveMap&&this.emissiveMap.isTexture&&(n.emissiveMap=this.emissiveMap.toJSON(e).uuid),this.specularMap&&this.specularMap.isTexture&&(n.specularMap=this.specularMap.toJSON(e).uuid),this.specularIntensityMap&&this.specularIntensityMap.isTexture&&(n.specularIntensityMap=this.specularIntensityMap.toJSON(e).uuid),this.specularColorMap&&this.specularColorMap.isTexture&&(n.specularColorMap=this.specularColorMap.toJSON(e).uuid),this.envMap&&this.envMap.isTexture&&(n.envMap=this.envMap.toJSON(e).uuid,this.combine!==void 0&&(n.combine=this.combine)),this.envMapRotation!==void 0&&(n.envMapRotation=this.envMapRotation.toArray()),this.envMapIntensity!==void 0&&(n.envMapIntensity=this.envMapIntensity),this.reflectivity!==void 0&&(n.reflectivity=this.reflectivity),this.refractionRatio!==void 0&&(n.refractionRatio=this.refractionRatio),this.gradientMap&&this.gradientMap.isTexture&&(n.gradientMap=this.gradientMap.toJSON(e).uuid),this.transmission!==void 0&&(n.transmission=this.transmission),this.transmissionMap&&this.transmissionMap.isTexture&&(n.transmissionMap=this.transmissionMap.toJSON(e).uuid),this.thickness!==void 0&&(n.thickness=this.thickness),this.thicknessMap&&this.thicknessMap.isTexture&&(n.thicknessMap=this.thicknessMap.toJSON(e).uuid),this.attenuationDistance!==void 0&&this.attenuationDistance!==1/0&&(n.attenuationDistance=this.attenuationDistance),this.attenuationColor!==void 0&&(n.attenuationColor=this.attenuationColor.getHex()),this.size!==void 0&&(n.size=this.size),this.shadowSide!==null&&(n.shadowSide=this.shadowSide),this.sizeAttenuation!==void 0&&(n.sizeAttenuation=this.sizeAttenuation),this.blending!==Or&&(n.blending=this.blending),this.side!==gs&&(n.side=this.side),this.vertexColors===!0&&(n.vertexColors=!0),this.opacity<1&&(n.opacity=this.opacity),this.transparent===!0&&(n.transparent=!0),this.blendSrc!==Ac&&(n.blendSrc=this.blendSrc),this.blendDst!==Rc&&(n.blendDst=this.blendDst),this.blendEquation!==Os&&(n.blendEquation=this.blendEquation),this.blendSrcAlpha!==null&&(n.blendSrcAlpha=this.blendSrcAlpha),this.blendDstAlpha!==null&&(n.blendDstAlpha=this.blendDstAlpha),this.blendEquationAlpha!==null&&(n.blendEquationAlpha=this.blendEquationAlpha),this.blendColor&&this.blendColor.isColor&&(n.blendColor=this.blendColor.getHex()),this.blendAlpha!==0&&(n.blendAlpha=this.blendAlpha),this.depthFunc!==Yo&&(n.depthFunc=this.depthFunc),this.depthTest===!1&&(n.depthTest=this.depthTest),this.depthWrite===!1&&(n.depthWrite=this.depthWrite),this.colorWrite===!1&&(n.colorWrite=this.colorWrite),this.stencilWriteMask!==255&&(n.stencilWriteMask=this.stencilWriteMask),this.stencilFunc!==Cu&&(n.stencilFunc=this.stencilFunc),this.stencilRef!==0&&(n.stencilRef=this.stencilRef),this.stencilFuncMask!==255&&(n.stencilFuncMask=this.stencilFuncMask),this.stencilFail!==hr&&(n.stencilFail=this.stencilFail),this.stencilZFail!==hr&&(n.stencilZFail=this.stencilZFail),this.stencilZPass!==hr&&(n.stencilZPass=this.stencilZPass),this.stencilWrite===!0&&(n.stencilWrite=this.stencilWrite),this.rotation!==void 0&&this.rotation!==0&&(n.rotation=this.rotation),this.polygonOffset===!0&&(n.polygonOffset=!0),this.polygonOffsetFactor!==0&&(n.polygonOffsetFactor=this.polygonOffsetFactor),this.polygonOffsetUnits!==0&&(n.polygonOffsetUnits=this.polygonOffsetUnits),this.linewidth!==void 0&&this.linewidth!==1&&(n.linewidth=this.linewidth),this.dashSize!==void 0&&(n.dashSize=this.dashSize),this.gapSize!==void 0&&(n.gapSize=this.gapSize),this.scale!==void 0&&(n.scale=this.scale),this.dithering===!0&&(n.dithering=!0),this.alphaTest>0&&(n.alphaTest=this.alphaTest),this.alphaHash===!0&&(n.alphaHash=!0),this.alphaToCoverage===!0&&(n.alphaToCoverage=!0),this.premultipliedAlpha===!0&&(n.premultipliedAlpha=!0),this.forceSinglePass===!0&&(n.forceSinglePass=!0),this.wireframe===!0&&(n.wireframe=!0),this.wireframeLinewidth>1&&(n.wireframeLinewidth=this.wireframeLinewidth),this.wireframeLinecap!=="round"&&(n.wireframeLinecap=this.wireframeLinecap),this.wireframeLinejoin!=="round"&&(n.wireframeLinejoin=this.wireframeLinejoin),this.flatShading===!0&&(n.flatShading=!0),this.visible===!1&&(n.visible=!1),this.toneMapped===!1&&(n.toneMapped=!1),this.fog===!1&&(n.fog=!1),Object.keys(this.userData).length>0&&(n.userData=this.userData);function s(r){const a=[];for(const o in r){const l=r[o];delete l.metadata,a.push(l)}return a}if(t){const r=s(e.textures),a=s(e.images);r.length>0&&(n.textures=r),a.length>0&&(n.images=a)}return n}clone(){return new this.constructor().copy(this)}copy(e){this.name=e.name,this.blending=e.blending,this.side=e.side,this.vertexColors=e.vertexColors,this.opacity=e.opacity,this.transparent=e.transparent,this.blendSrc=e.blendSrc,this.blendDst=e.blendDst,this.blendEquation=e.blendEquation,this.blendSrcAlpha=e.blendSrcAlpha,this.blendDstAlpha=e.blendDstAlpha,this.blendEquationAlpha=e.blendEquationAlpha,this.blendColor.copy(e.blendColor),this.blendAlpha=e.blendAlpha,this.depthFunc=e.depthFunc,this.depthTest=e.depthTest,this.depthWrite=e.depthWrite,this.stencilWriteMask=e.stencilWriteMask,this.stencilFunc=e.stencilFunc,this.stencilRef=e.stencilRef,this.stencilFuncMask=e.stencilFuncMask,this.stencilFail=e.stencilFail,this.stencilZFail=e.stencilZFail,this.stencilZPass=e.stencilZPass,this.stencilWrite=e.stencilWrite;const t=e.clippingPlanes;let n=null;if(t!==null){const s=t.length;n=new Array(s);for(let r=0;r!==s;++r)n[r]=t[r].clone()}return this.clippingPlanes=n,this.clipIntersection=e.clipIntersection,this.clipShadows=e.clipShadows,this.shadowSide=e.shadowSide,this.colorWrite=e.colorWrite,this.precision=e.precision,this.polygonOffset=e.polygonOffset,this.polygonOffsetFactor=e.polygonOffsetFactor,this.polygonOffsetUnits=e.polygonOffsetUnits,this.dithering=e.dithering,this.alphaTest=e.alphaTest,this.alphaHash=e.alphaHash,this.alphaToCoverage=e.alphaToCoverage,this.premultipliedAlpha=e.premultipliedAlpha,this.forceSinglePass=e.forceSinglePass,this.visible=e.visible,this.toneMapped=e.toneMapped,this.userData=JSON.parse(JSON.stringify(e.userData)),this}dispose(){this.dispatchEvent({type:"dispose"})}set needsUpdate(e){e===!0&&this.version++}onBuild(){console.warn("Material: onBuild() has been removed.")}}class ps extends Ss{constructor(e){super(),this.isMeshBasicMaterial=!0,this.type="MeshBasicMaterial",this.color=new nt(16777215),this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.specularMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new Ci,this.combine=Ff,this.reflectivity=1,this.refractionRatio=.98,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.lightMap=e.lightMap,this.lightMapIntensity=e.lightMapIntensity,this.aoMap=e.aoMap,this.aoMapIntensity=e.aoMapIntensity,this.specularMap=e.specularMap,this.alphaMap=e.alphaMap,this.envMap=e.envMap,this.envMapRotation.copy(e.envMapRotation),this.combine=e.combine,this.reflectivity=e.reflectivity,this.refractionRatio=e.refractionRatio,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.wireframeLinecap=e.wireframeLinecap,this.wireframeLinejoin=e.wireframeLinejoin,this.fog=e.fog,this}}const Zt=new V,fo=new $e;class pi{constructor(e,t,n=!1){if(Array.isArray(e))throw new TypeError("THREE.BufferAttribute: array should be a Typed Array.");this.isBufferAttribute=!0,this.name="",this.array=e,this.itemSize=t,this.count=e!==void 0?e.length/t:0,this.normalized=n,this.usage=rh,this._updateRange={offset:0,count:-1},this.updateRanges=[],this.gpuType=Gi,this.version=0}onUploadCallback(){}set needsUpdate(e){e===!0&&this.version++}get updateRange(){return kr("THREE.BufferAttribute: updateRange() is deprecated and will be removed in r169. Use addUpdateRange() instead."),this._updateRange}setUsage(e){return this.usage=e,this}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}copy(e){return this.name=e.name,this.array=new e.array.constructor(e.array),this.itemSize=e.itemSize,this.count=e.count,this.normalized=e.normalized,this.usage=e.usage,this.gpuType=e.gpuType,this}copyAt(e,t,n){e*=this.itemSize,n*=t.itemSize;for(let s=0,r=this.itemSize;s<r;s++)this.array[e+s]=t.array[n+s];return this}copyArray(e){return this.array.set(e),this}applyMatrix3(e){if(this.itemSize===2)for(let t=0,n=this.count;t<n;t++)fo.fromBufferAttribute(this,t),fo.applyMatrix3(e),this.setXY(t,fo.x,fo.y);else if(this.itemSize===3)for(let t=0,n=this.count;t<n;t++)Zt.fromBufferAttribute(this,t),Zt.applyMatrix3(e),this.setXYZ(t,Zt.x,Zt.y,Zt.z);return this}applyMatrix4(e){for(let t=0,n=this.count;t<n;t++)Zt.fromBufferAttribute(this,t),Zt.applyMatrix4(e),this.setXYZ(t,Zt.x,Zt.y,Zt.z);return this}applyNormalMatrix(e){for(let t=0,n=this.count;t<n;t++)Zt.fromBufferAttribute(this,t),Zt.applyNormalMatrix(e),this.setXYZ(t,Zt.x,Zt.y,Zt.z);return this}transformDirection(e){for(let t=0,n=this.count;t<n;t++)Zt.fromBufferAttribute(this,t),Zt.transformDirection(e),this.setXYZ(t,Zt.x,Zt.y,Zt.z);return this}set(e,t=0){return this.array.set(e,t),this}getComponent(e,t){let n=this.array[e*this.itemSize+t];return this.normalized&&(n=ui(n,this.array)),n}setComponent(e,t,n){return this.normalized&&(n=Tt(n,this.array)),this.array[e*this.itemSize+t]=n,this}getX(e){let t=this.array[e*this.itemSize];return this.normalized&&(t=ui(t,this.array)),t}setX(e,t){return this.normalized&&(t=Tt(t,this.array)),this.array[e*this.itemSize]=t,this}getY(e){let t=this.array[e*this.itemSize+1];return this.normalized&&(t=ui(t,this.array)),t}setY(e,t){return this.normalized&&(t=Tt(t,this.array)),this.array[e*this.itemSize+1]=t,this}getZ(e){let t=this.array[e*this.itemSize+2];return this.normalized&&(t=ui(t,this.array)),t}setZ(e,t){return this.normalized&&(t=Tt(t,this.array)),this.array[e*this.itemSize+2]=t,this}getW(e){let t=this.array[e*this.itemSize+3];return this.normalized&&(t=ui(t,this.array)),t}setW(e,t){return this.normalized&&(t=Tt(t,this.array)),this.array[e*this.itemSize+3]=t,this}setXY(e,t,n){return e*=this.itemSize,this.normalized&&(t=Tt(t,this.array),n=Tt(n,this.array)),this.array[e+0]=t,this.array[e+1]=n,this}setXYZ(e,t,n,s){return e*=this.itemSize,this.normalized&&(t=Tt(t,this.array),n=Tt(n,this.array),s=Tt(s,this.array)),this.array[e+0]=t,this.array[e+1]=n,this.array[e+2]=s,this}setXYZW(e,t,n,s,r){return e*=this.itemSize,this.normalized&&(t=Tt(t,this.array),n=Tt(n,this.array),s=Tt(s,this.array),r=Tt(r,this.array)),this.array[e+0]=t,this.array[e+1]=n,this.array[e+2]=s,this.array[e+3]=r,this}onUpload(e){return this.onUploadCallback=e,this}clone(){return new this.constructor(this.array,this.itemSize).copy(this)}toJSON(){const e={itemSize:this.itemSize,type:this.array.constructor.name,array:Array.from(this.array),normalized:this.normalized};return this.name!==""&&(e.name=this.name),this.usage!==rh&&(e.usage=this.usage),e}}class tp extends pi{constructor(e,t,n){super(new Uint16Array(e),t,n)}}class np extends pi{constructor(e,t,n){super(new Uint32Array(e),t,n)}}class zt extends pi{constructor(e,t,n){super(new Float32Array(e),t,n)}}let r_=0;const jn=new Bt,nc=new en,yr=new V,Hn=new Wa,va=new Wa,fn=new V;class Gt extends ta{constructor(){super(),this.isBufferGeometry=!0,Object.defineProperty(this,"id",{value:r_++}),this.uuid=Xi(),this.name="",this.type="BufferGeometry",this.index=null,this.attributes={},this.morphAttributes={},this.morphTargetsRelative=!1,this.groups=[],this.boundingBox=null,this.boundingSphere=null,this.drawRange={start:0,count:1/0},this.userData={}}getIndex(){return this.index}setIndex(e){return Array.isArray(e)?this.index=new(Zf(e)?np:tp)(e,1):this.index=e,this}getAttribute(e){return this.attributes[e]}setAttribute(e,t){return this.attributes[e]=t,this}deleteAttribute(e){return delete this.attributes[e],this}hasAttribute(e){return this.attributes[e]!==void 0}addGroup(e,t,n=0){this.groups.push({start:e,count:t,materialIndex:n})}clearGroups(){this.groups=[]}setDrawRange(e,t){this.drawRange.start=e,this.drawRange.count=t}applyMatrix4(e){const t=this.attributes.position;t!==void 0&&(t.applyMatrix4(e),t.needsUpdate=!0);const n=this.attributes.normal;if(n!==void 0){const r=new at().getNormalMatrix(e);n.applyNormalMatrix(r),n.needsUpdate=!0}const s=this.attributes.tangent;return s!==void 0&&(s.transformDirection(e),s.needsUpdate=!0),this.boundingBox!==null&&this.computeBoundingBox(),this.boundingSphere!==null&&this.computeBoundingSphere(),this}applyQuaternion(e){return jn.makeRotationFromQuaternion(e),this.applyMatrix4(jn),this}rotateX(e){return jn.makeRotationX(e),this.applyMatrix4(jn),this}rotateY(e){return jn.makeRotationY(e),this.applyMatrix4(jn),this}rotateZ(e){return jn.makeRotationZ(e),this.applyMatrix4(jn),this}translate(e,t,n){return jn.makeTranslation(e,t,n),this.applyMatrix4(jn),this}scale(e,t,n){return jn.makeScale(e,t,n),this.applyMatrix4(jn),this}lookAt(e){return nc.lookAt(e),nc.updateMatrix(),this.applyMatrix4(nc.matrix),this}center(){return this.computeBoundingBox(),this.boundingBox.getCenter(yr).negate(),this.translate(yr.x,yr.y,yr.z),this}setFromPoints(e){const t=[];for(let n=0,s=e.length;n<s;n++){const r=e[n];t.push(r.x,r.y,r.z||0)}return this.setAttribute("position",new zt(t,3)),this}computeBoundingBox(){this.boundingBox===null&&(this.boundingBox=new Wa);const e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingBox(): GLBufferAttribute requires a manual bounding box.",this),this.boundingBox.set(new V(-1/0,-1/0,-1/0),new V(1/0,1/0,1/0));return}if(e!==void 0){if(this.boundingBox.setFromBufferAttribute(e),t)for(let n=0,s=t.length;n<s;n++){const r=t[n];Hn.setFromBufferAttribute(r),this.morphTargetsRelative?(fn.addVectors(this.boundingBox.min,Hn.min),this.boundingBox.expandByPoint(fn),fn.addVectors(this.boundingBox.max,Hn.max),this.boundingBox.expandByPoint(fn)):(this.boundingBox.expandByPoint(Hn.min),this.boundingBox.expandByPoint(Hn.max))}}else this.boundingBox.makeEmpty();(isNaN(this.boundingBox.min.x)||isNaN(this.boundingBox.min.y)||isNaN(this.boundingBox.min.z))&&console.error('THREE.BufferGeometry.computeBoundingBox(): Computed min/max have NaN values. The "position" attribute is likely to have NaN values.',this)}computeBoundingSphere(){this.boundingSphere===null&&(this.boundingSphere=new Xa);const e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingSphere(): GLBufferAttribute requires a manual bounding sphere.",this),this.boundingSphere.set(new V,1/0);return}if(e){const n=this.boundingSphere.center;if(Hn.setFromBufferAttribute(e),t)for(let r=0,a=t.length;r<a;r++){const o=t[r];va.setFromBufferAttribute(o),this.morphTargetsRelative?(fn.addVectors(Hn.min,va.min),Hn.expandByPoint(fn),fn.addVectors(Hn.max,va.max),Hn.expandByPoint(fn)):(Hn.expandByPoint(va.min),Hn.expandByPoint(va.max))}Hn.getCenter(n);let s=0;for(let r=0,a=e.count;r<a;r++)fn.fromBufferAttribute(e,r),s=Math.max(s,n.distanceToSquared(fn));if(t)for(let r=0,a=t.length;r<a;r++){const o=t[r],l=this.morphTargetsRelative;for(let c=0,h=o.count;c<h;c++)fn.fromBufferAttribute(o,c),l&&(yr.fromBufferAttribute(e,c),fn.add(yr)),s=Math.max(s,n.distanceToSquared(fn))}this.boundingSphere.radius=Math.sqrt(s),isNaN(this.boundingSphere.radius)&&console.error('THREE.BufferGeometry.computeBoundingSphere(): Computed radius is NaN. The "position" attribute is likely to have NaN values.',this)}}computeTangents(){const e=this.index,t=this.attributes;if(e===null||t.position===void 0||t.normal===void 0||t.uv===void 0){console.error("THREE.BufferGeometry: .computeTangents() failed. Missing required attributes (index, position, normal or uv)");return}const n=t.position,s=t.normal,r=t.uv;this.hasAttribute("tangent")===!1&&this.setAttribute("tangent",new pi(new Float32Array(4*n.count),4));const a=this.getAttribute("tangent"),o=[],l=[];for(let F=0;F<n.count;F++)o[F]=new V,l[F]=new V;const c=new V,h=new V,u=new V,d=new $e,f=new $e,g=new $e,_=new V,p=new V;function m(F,w,y){c.fromBufferAttribute(n,F),h.fromBufferAttribute(n,w),u.fromBufferAttribute(n,y),d.fromBufferAttribute(r,F),f.fromBufferAttribute(r,w),g.fromBufferAttribute(r,y),h.sub(c),u.sub(c),f.sub(d),g.sub(d);const P=1/(f.x*g.y-g.x*f.y);isFinite(P)&&(_.copy(h).multiplyScalar(g.y).addScaledVector(u,-f.y).multiplyScalar(P),p.copy(u).multiplyScalar(f.x).addScaledVector(h,-g.x).multiplyScalar(P),o[F].add(_),o[w].add(_),o[y].add(_),l[F].add(p),l[w].add(p),l[y].add(p))}let M=this.groups;M.length===0&&(M=[{start:0,count:e.count}]);for(let F=0,w=M.length;F<w;++F){const y=M[F],P=y.start,K=y.count;for(let H=P,Z=P+K;H<Z;H+=3)m(e.getX(H+0),e.getX(H+1),e.getX(H+2))}const v=new V,b=new V,N=new V,A=new V;function R(F){N.fromBufferAttribute(s,F),A.copy(N);const w=o[F];v.copy(w),v.sub(N.multiplyScalar(N.dot(w))).normalize(),b.crossVectors(A,w);const P=b.dot(l[F])<0?-1:1;a.setXYZW(F,v.x,v.y,v.z,P)}for(let F=0,w=M.length;F<w;++F){const y=M[F],P=y.start,K=y.count;for(let H=P,Z=P+K;H<Z;H+=3)R(e.getX(H+0)),R(e.getX(H+1)),R(e.getX(H+2))}}computeVertexNormals(){const e=this.index,t=this.getAttribute("position");if(t!==void 0){let n=this.getAttribute("normal");if(n===void 0)n=new pi(new Float32Array(t.count*3),3),this.setAttribute("normal",n);else for(let d=0,f=n.count;d<f;d++)n.setXYZ(d,0,0,0);const s=new V,r=new V,a=new V,o=new V,l=new V,c=new V,h=new V,u=new V;if(e)for(let d=0,f=e.count;d<f;d+=3){const g=e.getX(d+0),_=e.getX(d+1),p=e.getX(d+2);s.fromBufferAttribute(t,g),r.fromBufferAttribute(t,_),a.fromBufferAttribute(t,p),h.subVectors(a,r),u.subVectors(s,r),h.cross(u),o.fromBufferAttribute(n,g),l.fromBufferAttribute(n,_),c.fromBufferAttribute(n,p),o.add(h),l.add(h),c.add(h),n.setXYZ(g,o.x,o.y,o.z),n.setXYZ(_,l.x,l.y,l.z),n.setXYZ(p,c.x,c.y,c.z)}else for(let d=0,f=t.count;d<f;d+=3)s.fromBufferAttribute(t,d+0),r.fromBufferAttribute(t,d+1),a.fromBufferAttribute(t,d+2),h.subVectors(a,r),u.subVectors(s,r),h.cross(u),n.setXYZ(d+0,h.x,h.y,h.z),n.setXYZ(d+1,h.x,h.y,h.z),n.setXYZ(d+2,h.x,h.y,h.z);this.normalizeNormals(),n.needsUpdate=!0}}normalizeNormals(){const e=this.attributes.normal;for(let t=0,n=e.count;t<n;t++)fn.fromBufferAttribute(e,t),fn.normalize(),e.setXYZ(t,fn.x,fn.y,fn.z)}toNonIndexed(){function e(o,l){const c=o.array,h=o.itemSize,u=o.normalized,d=new c.constructor(l.length*h);let f=0,g=0;for(let _=0,p=l.length;_<p;_++){o.isInterleavedBufferAttribute?f=l[_]*o.data.stride+o.offset:f=l[_]*h;for(let m=0;m<h;m++)d[g++]=c[f++]}return new pi(d,h,u)}if(this.index===null)return console.warn("THREE.BufferGeometry.toNonIndexed(): BufferGeometry is already non-indexed."),this;const t=new Gt,n=this.index.array,s=this.attributes;for(const o in s){const l=s[o],c=e(l,n);t.setAttribute(o,c)}const r=this.morphAttributes;for(const o in r){const l=[],c=r[o];for(let h=0,u=c.length;h<u;h++){const d=c[h],f=e(d,n);l.push(f)}t.morphAttributes[o]=l}t.morphTargetsRelative=this.morphTargetsRelative;const a=this.groups;for(let o=0,l=a.length;o<l;o++){const c=a[o];t.addGroup(c.start,c.count,c.materialIndex)}return t}toJSON(){const e={metadata:{version:4.6,type:"BufferGeometry",generator:"BufferGeometry.toJSON"}};if(e.uuid=this.uuid,e.type=this.type,this.name!==""&&(e.name=this.name),Object.keys(this.userData).length>0&&(e.userData=this.userData),this.parameters!==void 0){const l=this.parameters;for(const c in l)l[c]!==void 0&&(e[c]=l[c]);return e}e.data={attributes:{}};const t=this.index;t!==null&&(e.data.index={type:t.array.constructor.name,array:Array.prototype.slice.call(t.array)});const n=this.attributes;for(const l in n){const c=n[l];e.data.attributes[l]=c.toJSON(e.data)}const s={};let r=!1;for(const l in this.morphAttributes){const c=this.morphAttributes[l],h=[];for(let u=0,d=c.length;u<d;u++){const f=c[u];h.push(f.toJSON(e.data))}h.length>0&&(s[l]=h,r=!0)}r&&(e.data.morphAttributes=s,e.data.morphTargetsRelative=this.morphTargetsRelative);const a=this.groups;a.length>0&&(e.data.groups=JSON.parse(JSON.stringify(a)));const o=this.boundingSphere;return o!==null&&(e.data.boundingSphere={center:o.center.toArray(),radius:o.radius}),e}clone(){return new this.constructor().copy(this)}copy(e){this.index=null,this.attributes={},this.morphAttributes={},this.groups=[],this.boundingBox=null,this.boundingSphere=null;const t={};this.name=e.name;const n=e.index;n!==null&&this.setIndex(n.clone(t));const s=e.attributes;for(const c in s){const h=s[c];this.setAttribute(c,h.clone(t))}const r=e.morphAttributes;for(const c in r){const h=[],u=r[c];for(let d=0,f=u.length;d<f;d++)h.push(u[d].clone(t));this.morphAttributes[c]=h}this.morphTargetsRelative=e.morphTargetsRelative;const a=e.groups;for(let c=0,h=a.length;c<h;c++){const u=a[c];this.addGroup(u.start,u.count,u.materialIndex)}const o=e.boundingBox;o!==null&&(this.boundingBox=o.clone());const l=e.boundingSphere;return l!==null&&(this.boundingSphere=l.clone()),this.drawRange.start=e.drawRange.start,this.drawRange.count=e.drawRange.count,this.userData=e.userData,this}dispose(){this.dispatchEvent({type:"dispose"})}}const Wu=new Bt,Ps=new qa,po=new Xa,Xu=new V,Mr=new V,Sr=new V,br=new V,ic=new V,mo=new V,go=new $e,_o=new $e,xo=new $e,qu=new V,$u=new V,Yu=new V,vo=new V,yo=new V;class Qt extends en{constructor(e=new Gt,t=new ps){super(),this.isMesh=!0,this.type="Mesh",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),e.morphTargetInfluences!==void 0&&(this.morphTargetInfluences=e.morphTargetInfluences.slice()),e.morphTargetDictionary!==void 0&&(this.morphTargetDictionary=Object.assign({},e.morphTargetDictionary)),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const s=t[n[0]];if(s!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let r=0,a=s.length;r<a;r++){const o=s[r].name||String(r);this.morphTargetInfluences.push(0),this.morphTargetDictionary[o]=r}}}}getVertexPosition(e,t){const n=this.geometry,s=n.attributes.position,r=n.morphAttributes.position,a=n.morphTargetsRelative;t.fromBufferAttribute(s,e);const o=this.morphTargetInfluences;if(r&&o){mo.set(0,0,0);for(let l=0,c=r.length;l<c;l++){const h=o[l],u=r[l];h!==0&&(ic.fromBufferAttribute(u,e),a?mo.addScaledVector(ic,h):mo.addScaledVector(ic.sub(t),h))}t.add(mo)}return t}raycast(e,t){const n=this.geometry,s=this.material,r=this.matrixWorld;s!==void 0&&(n.boundingSphere===null&&n.computeBoundingSphere(),po.copy(n.boundingSphere),po.applyMatrix4(r),Ps.copy(e.ray).recast(e.near),!(po.containsPoint(Ps.origin)===!1&&(Ps.intersectSphere(po,Xu)===null||Ps.origin.distanceToSquared(Xu)>(e.far-e.near)**2))&&(Wu.copy(r).invert(),Ps.copy(e.ray).applyMatrix4(Wu),!(n.boundingBox!==null&&Ps.intersectsBox(n.boundingBox)===!1)&&this._computeIntersections(e,t,Ps)))}_computeIntersections(e,t,n){let s;const r=this.geometry,a=this.material,o=r.index,l=r.attributes.position,c=r.attributes.uv,h=r.attributes.uv1,u=r.attributes.normal,d=r.groups,f=r.drawRange;if(o!==null)if(Array.isArray(a))for(let g=0,_=d.length;g<_;g++){const p=d[g],m=a[p.materialIndex],M=Math.max(p.start,f.start),v=Math.min(o.count,Math.min(p.start+p.count,f.start+f.count));for(let b=M,N=v;b<N;b+=3){const A=o.getX(b),R=o.getX(b+1),F=o.getX(b+2);s=Mo(this,m,e,n,c,h,u,A,R,F),s&&(s.faceIndex=Math.floor(b/3),s.face.materialIndex=p.materialIndex,t.push(s))}}else{const g=Math.max(0,f.start),_=Math.min(o.count,f.start+f.count);for(let p=g,m=_;p<m;p+=3){const M=o.getX(p),v=o.getX(p+1),b=o.getX(p+2);s=Mo(this,a,e,n,c,h,u,M,v,b),s&&(s.faceIndex=Math.floor(p/3),t.push(s))}}else if(l!==void 0)if(Array.isArray(a))for(let g=0,_=d.length;g<_;g++){const p=d[g],m=a[p.materialIndex],M=Math.max(p.start,f.start),v=Math.min(l.count,Math.min(p.start+p.count,f.start+f.count));for(let b=M,N=v;b<N;b+=3){const A=b,R=b+1,F=b+2;s=Mo(this,m,e,n,c,h,u,A,R,F),s&&(s.faceIndex=Math.floor(b/3),s.face.materialIndex=p.materialIndex,t.push(s))}}else{const g=Math.max(0,f.start),_=Math.min(l.count,f.start+f.count);for(let p=g,m=_;p<m;p+=3){const M=p,v=p+1,b=p+2;s=Mo(this,a,e,n,c,h,u,M,v,b),s&&(s.faceIndex=Math.floor(p/3),t.push(s))}}}}function a_(i,e,t,n,s,r,a,o){let l;if(e.side===Nn?l=n.intersectTriangle(a,r,s,!0,o):l=n.intersectTriangle(s,r,a,e.side===gs,o),l===null)return null;yo.copy(o),yo.applyMatrix4(i.matrixWorld);const c=t.ray.origin.distanceTo(yo);return c<t.near||c>t.far?null:{distance:c,point:yo.clone(),object:i}}function Mo(i,e,t,n,s,r,a,o,l,c){i.getVertexPosition(o,Mr),i.getVertexPosition(l,Sr),i.getVertexPosition(c,br);const h=a_(i,e,t,n,Mr,Sr,br,vo);if(h){s&&(go.fromBufferAttribute(s,o),_o.fromBufferAttribute(s,l),xo.fromBufferAttribute(s,c),h.uv=Qn.getInterpolation(vo,Mr,Sr,br,go,_o,xo,new $e)),r&&(go.fromBufferAttribute(r,o),_o.fromBufferAttribute(r,l),xo.fromBufferAttribute(r,c),h.uv1=Qn.getInterpolation(vo,Mr,Sr,br,go,_o,xo,new $e)),a&&(qu.fromBufferAttribute(a,o),$u.fromBufferAttribute(a,l),Yu.fromBufferAttribute(a,c),h.normal=Qn.getInterpolation(vo,Mr,Sr,br,qu,$u,Yu,new V),h.normal.dot(n.direction)>0&&h.normal.multiplyScalar(-1));const u={a:o,b:l,c,normal:new V,materialIndex:0};Qn.getNormal(Mr,Sr,br,u.normal),h.face=u}return h}class Ei extends Gt{constructor(e=1,t=1,n=1,s=1,r=1,a=1){super(),this.type="BoxGeometry",this.parameters={width:e,height:t,depth:n,widthSegments:s,heightSegments:r,depthSegments:a};const o=this;s=Math.floor(s),r=Math.floor(r),a=Math.floor(a);const l=[],c=[],h=[],u=[];let d=0,f=0;g("z","y","x",-1,-1,n,t,e,a,r,0),g("z","y","x",1,-1,n,t,-e,a,r,1),g("x","z","y",1,1,e,n,t,s,a,2),g("x","z","y",1,-1,e,n,-t,s,a,3),g("x","y","z",1,-1,e,t,n,s,r,4),g("x","y","z",-1,-1,e,t,-n,s,r,5),this.setIndex(l),this.setAttribute("position",new zt(c,3)),this.setAttribute("normal",new zt(h,3)),this.setAttribute("uv",new zt(u,2));function g(_,p,m,M,v,b,N,A,R,F,w){const y=b/R,P=N/F,K=b/2,H=N/2,Z=A/2,q=R+1,ee=F+1;let Y=0,ne=0;const ge=new V;for(let de=0;de<ee;de++){const ve=de*P-H;for(let Te=0;Te<q;Te++){const ye=Te*y-K;ge[_]=ye*M,ge[p]=ve*v,ge[m]=Z,c.push(ge.x,ge.y,ge.z),ge[_]=0,ge[p]=0,ge[m]=A>0?1:-1,h.push(ge.x,ge.y,ge.z),u.push(Te/R),u.push(1-de/F),Y+=1}}for(let de=0;de<F;de++)for(let ve=0;ve<R;ve++){const Te=d+ve+q*de,ye=d+ve+q*(de+1),ie=d+(ve+1)+q*(de+1),he=d+(ve+1)+q*de;l.push(Te,ye,he),l.push(ye,ie,he),ne+=6}o.addGroup(f,ne,w),f+=ne,d+=Y}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Ei(e.width,e.height,e.depth,e.widthSegments,e.heightSegments,e.depthSegments)}}function Yr(i){const e={};for(const t in i){e[t]={};for(const n in i[t]){const s=i[t][n];s&&(s.isColor||s.isMatrix3||s.isMatrix4||s.isVector2||s.isVector3||s.isVector4||s.isTexture||s.isQuaternion)?s.isRenderTargetTexture?(console.warn("UniformsUtils: Textures of render targets cannot be cloned via cloneUniforms() or mergeUniforms()."),e[t][n]=null):e[t][n]=s.clone():Array.isArray(s)?e[t][n]=s.slice():e[t][n]=s}}return e}function Cn(i){const e={};for(let t=0;t<i.length;t++){const n=Yr(i[t]);for(const s in n)e[s]=n[s]}return e}function o_(i){const e=[];for(let t=0;t<i.length;t++)e.push(i[t].clone());return e}function ip(i){const e=i.getRenderTarget();return e===null?i.outputColorSpace:e.isXRRenderTarget===!0?e.texture.colorSpace:bt.workingColorSpace}const l_={clone:Yr,merge:Cn};var c_=`void main() {
	gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
}`,h_=`void main() {
	gl_FragColor = vec4( 1.0, 0.0, 0.0, 1.0 );
}`;class _s extends Ss{constructor(e){super(),this.isShaderMaterial=!0,this.type="ShaderMaterial",this.defines={},this.uniforms={},this.uniformsGroups=[],this.vertexShader=c_,this.fragmentShader=h_,this.linewidth=1,this.wireframe=!1,this.wireframeLinewidth=1,this.fog=!1,this.lights=!1,this.clipping=!1,this.forceSinglePass=!0,this.extensions={clipCullDistance:!1,multiDraw:!1},this.defaultAttributeValues={color:[1,1,1],uv:[0,0],uv1:[0,0]},this.index0AttributeName=void 0,this.uniformsNeedUpdate=!1,this.glslVersion=null,e!==void 0&&this.setValues(e)}copy(e){return super.copy(e),this.fragmentShader=e.fragmentShader,this.vertexShader=e.vertexShader,this.uniforms=Yr(e.uniforms),this.uniformsGroups=o_(e.uniformsGroups),this.defines=Object.assign({},e.defines),this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.fog=e.fog,this.lights=e.lights,this.clipping=e.clipping,this.extensions=Object.assign({},e.extensions),this.glslVersion=e.glslVersion,this}toJSON(e){const t=super.toJSON(e);t.glslVersion=this.glslVersion,t.uniforms={};for(const s in this.uniforms){const a=this.uniforms[s].value;a&&a.isTexture?t.uniforms[s]={type:"t",value:a.toJSON(e).uuid}:a&&a.isColor?t.uniforms[s]={type:"c",value:a.getHex()}:a&&a.isVector2?t.uniforms[s]={type:"v2",value:a.toArray()}:a&&a.isVector3?t.uniforms[s]={type:"v3",value:a.toArray()}:a&&a.isVector4?t.uniforms[s]={type:"v4",value:a.toArray()}:a&&a.isMatrix3?t.uniforms[s]={type:"m3",value:a.toArray()}:a&&a.isMatrix4?t.uniforms[s]={type:"m4",value:a.toArray()}:t.uniforms[s]={value:a}}Object.keys(this.defines).length>0&&(t.defines=this.defines),t.vertexShader=this.vertexShader,t.fragmentShader=this.fragmentShader,t.lights=this.lights,t.clipping=this.clipping;const n={};for(const s in this.extensions)this.extensions[s]===!0&&(n[s]=!0);return Object.keys(n).length>0&&(t.extensions=n),t}}class sp extends en{constructor(){super(),this.isCamera=!0,this.type="Camera",this.matrixWorldInverse=new Bt,this.projectionMatrix=new Bt,this.projectionMatrixInverse=new Bt,this.coordinateSystem=Wi}copy(e,t){return super.copy(e,t),this.matrixWorldInverse.copy(e.matrixWorldInverse),this.projectionMatrix.copy(e.projectionMatrix),this.projectionMatrixInverse.copy(e.projectionMatrixInverse),this.coordinateSystem=e.coordinateSystem,this}getWorldDirection(e){return super.getWorldDirection(e).negate()}updateMatrixWorld(e){super.updateMatrixWorld(e),this.matrixWorldInverse.copy(this.matrixWorld).invert()}updateWorldMatrix(e,t){super.updateWorldMatrix(e,t),this.matrixWorldInverse.copy(this.matrixWorld).invert()}clone(){return new this.constructor().copy(this)}}const os=new V,ju=new $e,Ku=new $e;class bn extends sp{constructor(e=50,t=1,n=.1,s=2e3){super(),this.isPerspectiveCamera=!0,this.type="PerspectiveCamera",this.fov=e,this.zoom=1,this.near=n,this.far=s,this.focus=10,this.aspect=t,this.view=null,this.filmGauge=35,this.filmOffset=0,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.fov=e.fov,this.zoom=e.zoom,this.near=e.near,this.far=e.far,this.focus=e.focus,this.aspect=e.aspect,this.view=e.view===null?null:Object.assign({},e.view),this.filmGauge=e.filmGauge,this.filmOffset=e.filmOffset,this}setFocalLength(e){const t=.5*this.getFilmHeight()/e;this.fov=Oa*2*Math.atan(t),this.updateProjectionMatrix()}getFocalLength(){const e=Math.tan(zr*.5*this.fov);return .5*this.getFilmHeight()/e}getEffectiveFOV(){return Oa*2*Math.atan(Math.tan(zr*.5*this.fov)/this.zoom)}getFilmWidth(){return this.filmGauge*Math.min(this.aspect,1)}getFilmHeight(){return this.filmGauge/Math.max(this.aspect,1)}getViewBounds(e,t,n){os.set(-1,-1,.5).applyMatrix4(this.projectionMatrixInverse),t.set(os.x,os.y).multiplyScalar(-e/os.z),os.set(1,1,.5).applyMatrix4(this.projectionMatrixInverse),n.set(os.x,os.y).multiplyScalar(-e/os.z)}getViewSize(e,t){return this.getViewBounds(e,ju,Ku),t.subVectors(Ku,ju)}setViewOffset(e,t,n,s,r,a){this.aspect=e/t,this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=n,this.view.offsetY=s,this.view.width=r,this.view.height=a,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const e=this.near;let t=e*Math.tan(zr*.5*this.fov)/this.zoom,n=2*t,s=this.aspect*n,r=-.5*s;const a=this.view;if(this.view!==null&&this.view.enabled){const l=a.fullWidth,c=a.fullHeight;r+=a.offsetX*s/l,t-=a.offsetY*n/c,s*=a.width/l,n*=a.height/c}const o=this.filmOffset;o!==0&&(r+=e*o/this.getFilmWidth()),this.projectionMatrix.makePerspective(r,r+s,t,t-n,e,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){const t=super.toJSON(e);return t.object.fov=this.fov,t.object.zoom=this.zoom,t.object.near=this.near,t.object.far=this.far,t.object.focus=this.focus,t.object.aspect=this.aspect,this.view!==null&&(t.object.view=Object.assign({},this.view)),t.object.filmGauge=this.filmGauge,t.object.filmOffset=this.filmOffset,t}}const wr=-90,Er=1;class u_ extends en{constructor(e,t,n){super(),this.type="CubeCamera",this.renderTarget=n,this.coordinateSystem=null,this.activeMipmapLevel=0;const s=new bn(wr,Er,e,t);s.layers=this.layers,this.add(s);const r=new bn(wr,Er,e,t);r.layers=this.layers,this.add(r);const a=new bn(wr,Er,e,t);a.layers=this.layers,this.add(a);const o=new bn(wr,Er,e,t);o.layers=this.layers,this.add(o);const l=new bn(wr,Er,e,t);l.layers=this.layers,this.add(l);const c=new bn(wr,Er,e,t);c.layers=this.layers,this.add(c)}updateCoordinateSystem(){const e=this.coordinateSystem,t=this.children.concat(),[n,s,r,a,o,l]=t;for(const c of t)this.remove(c);if(e===Wi)n.up.set(0,1,0),n.lookAt(1,0,0),s.up.set(0,1,0),s.lookAt(-1,0,0),r.up.set(0,0,-1),r.lookAt(0,1,0),a.up.set(0,0,1),a.lookAt(0,-1,0),o.up.set(0,1,0),o.lookAt(0,0,1),l.up.set(0,1,0),l.lookAt(0,0,-1);else if(e===Jo)n.up.set(0,-1,0),n.lookAt(-1,0,0),s.up.set(0,-1,0),s.lookAt(1,0,0),r.up.set(0,0,1),r.lookAt(0,1,0),a.up.set(0,0,-1),a.lookAt(0,-1,0),o.up.set(0,-1,0),o.lookAt(0,0,1),l.up.set(0,-1,0),l.lookAt(0,0,-1);else throw new Error("THREE.CubeCamera.updateCoordinateSystem(): Invalid coordinate system: "+e);for(const c of t)this.add(c),c.updateMatrixWorld()}update(e,t){this.parent===null&&this.updateMatrixWorld();const{renderTarget:n,activeMipmapLevel:s}=this;this.coordinateSystem!==e.coordinateSystem&&(this.coordinateSystem=e.coordinateSystem,this.updateCoordinateSystem());const[r,a,o,l,c,h]=this.children,u=e.getRenderTarget(),d=e.getActiveCubeFace(),f=e.getActiveMipmapLevel(),g=e.xr.enabled;e.xr.enabled=!1;const _=n.texture.generateMipmaps;n.texture.generateMipmaps=!1,e.setRenderTarget(n,0,s),e.render(t,r),e.setRenderTarget(n,1,s),e.render(t,a),e.setRenderTarget(n,2,s),e.render(t,o),e.setRenderTarget(n,3,s),e.render(t,l),e.setRenderTarget(n,4,s),e.render(t,c),n.texture.generateMipmaps=_,e.setRenderTarget(n,5,s),e.render(t,h),e.setRenderTarget(u,d,f),e.xr.enabled=g,n.texture.needsPMREMUpdate=!0}}class rp extends Ln{constructor(e,t,n,s,r,a,o,l,c,h){e=e!==void 0?e:[],t=t!==void 0?t:Wr,super(e,t,n,s,r,a,o,l,c,h),this.isCubeTexture=!0,this.flipY=!1}get images(){return this.image}set images(e){this.image=e}}class d_ extends $s{constructor(e=1,t={}){super(e,e,t),this.isWebGLCubeRenderTarget=!0;const n={width:e,height:e,depth:1},s=[n,n,n,n,n,n];this.texture=new rp(s,t.mapping,t.wrapS,t.wrapT,t.magFilter,t.minFilter,t.format,t.type,t.anisotropy,t.colorSpace),this.texture.isRenderTargetTexture=!0,this.texture.generateMipmaps=t.generateMipmaps!==void 0?t.generateMipmaps:!1,this.texture.minFilter=t.minFilter!==void 0?t.minFilter:hi}fromEquirectangularTexture(e,t){this.texture.type=t.type,this.texture.colorSpace=t.colorSpace,this.texture.generateMipmaps=t.generateMipmaps,this.texture.minFilter=t.minFilter,this.texture.magFilter=t.magFilter;const n={uniforms:{tEquirect:{value:null}},vertexShader:`

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
			`},s=new Ei(5,5,5),r=new _s({name:"CubemapFromEquirect",uniforms:Yr(n.uniforms),vertexShader:n.vertexShader,fragmentShader:n.fragmentShader,side:Nn,blending:ds});r.uniforms.tEquirect.value=t;const a=new Qt(s,r),o=t.minFilter;return t.minFilter===Hs&&(t.minFilter=hi),new u_(1,10,this).update(e,a),t.minFilter=o,a.geometry.dispose(),a.material.dispose(),this}clear(e,t,n,s){const r=e.getRenderTarget();for(let a=0;a<6;a++)e.setRenderTarget(this,a),e.clear(t,n,s);e.setRenderTarget(r)}}const sc=new V,f_=new V,p_=new at;class cs{constructor(e=new V(1,0,0),t=0){this.isPlane=!0,this.normal=e,this.constant=t}set(e,t){return this.normal.copy(e),this.constant=t,this}setComponents(e,t,n,s){return this.normal.set(e,t,n),this.constant=s,this}setFromNormalAndCoplanarPoint(e,t){return this.normal.copy(e),this.constant=-t.dot(this.normal),this}setFromCoplanarPoints(e,t,n){const s=sc.subVectors(n,t).cross(f_.subVectors(e,t)).normalize();return this.setFromNormalAndCoplanarPoint(s,e),this}copy(e){return this.normal.copy(e.normal),this.constant=e.constant,this}normalize(){const e=1/this.normal.length();return this.normal.multiplyScalar(e),this.constant*=e,this}negate(){return this.constant*=-1,this.normal.negate(),this}distanceToPoint(e){return this.normal.dot(e)+this.constant}distanceToSphere(e){return this.distanceToPoint(e.center)-e.radius}projectPoint(e,t){return t.copy(e).addScaledVector(this.normal,-this.distanceToPoint(e))}intersectLine(e,t){const n=e.delta(sc),s=this.normal.dot(n);if(s===0)return this.distanceToPoint(e.start)===0?t.copy(e.start):null;const r=-(e.start.dot(this.normal)+this.constant)/s;return r<0||r>1?null:t.copy(e.start).addScaledVector(n,r)}intersectsLine(e){const t=this.distanceToPoint(e.start),n=this.distanceToPoint(e.end);return t<0&&n>0||n<0&&t>0}intersectsBox(e){return e.intersectsPlane(this)}intersectsSphere(e){return e.intersectsPlane(this)}coplanarPoint(e){return e.copy(this.normal).multiplyScalar(-this.constant)}applyMatrix4(e,t){const n=t||p_.getNormalMatrix(e),s=this.coplanarPoint(sc).applyMatrix4(e),r=this.normal.applyMatrix3(n).normalize();return this.constant=-s.dot(r),this}translate(e){return this.constant-=e.dot(this.normal),this}equals(e){return e.normal.equals(this.normal)&&e.constant===this.constant}clone(){return new this.constructor().copy(this)}}const Ls=new Xa,So=new V;class Lh{constructor(e=new cs,t=new cs,n=new cs,s=new cs,r=new cs,a=new cs){this.planes=[e,t,n,s,r,a]}set(e,t,n,s,r,a){const o=this.planes;return o[0].copy(e),o[1].copy(t),o[2].copy(n),o[3].copy(s),o[4].copy(r),o[5].copy(a),this}copy(e){const t=this.planes;for(let n=0;n<6;n++)t[n].copy(e.planes[n]);return this}setFromProjectionMatrix(e,t=Wi){const n=this.planes,s=e.elements,r=s[0],a=s[1],o=s[2],l=s[3],c=s[4],h=s[5],u=s[6],d=s[7],f=s[8],g=s[9],_=s[10],p=s[11],m=s[12],M=s[13],v=s[14],b=s[15];if(n[0].setComponents(l-r,d-c,p-f,b-m).normalize(),n[1].setComponents(l+r,d+c,p+f,b+m).normalize(),n[2].setComponents(l+a,d+h,p+g,b+M).normalize(),n[3].setComponents(l-a,d-h,p-g,b-M).normalize(),n[4].setComponents(l-o,d-u,p-_,b-v).normalize(),t===Wi)n[5].setComponents(l+o,d+u,p+_,b+v).normalize();else if(t===Jo)n[5].setComponents(o,u,_,v).normalize();else throw new Error("THREE.Frustum.setFromProjectionMatrix(): Invalid coordinate system: "+t);return this}intersectsObject(e){if(e.boundingSphere!==void 0)e.boundingSphere===null&&e.computeBoundingSphere(),Ls.copy(e.boundingSphere).applyMatrix4(e.matrixWorld);else{const t=e.geometry;t.boundingSphere===null&&t.computeBoundingSphere(),Ls.copy(t.boundingSphere).applyMatrix4(e.matrixWorld)}return this.intersectsSphere(Ls)}intersectsSprite(e){return Ls.center.set(0,0,0),Ls.radius=.7071067811865476,Ls.applyMatrix4(e.matrixWorld),this.intersectsSphere(Ls)}intersectsSphere(e){const t=this.planes,n=e.center,s=-e.radius;for(let r=0;r<6;r++)if(t[r].distanceToPoint(n)<s)return!1;return!0}intersectsBox(e){const t=this.planes;for(let n=0;n<6;n++){const s=t[n];if(So.x=s.normal.x>0?e.max.x:e.min.x,So.y=s.normal.y>0?e.max.y:e.min.y,So.z=s.normal.z>0?e.max.z:e.min.z,s.distanceToPoint(So)<0)return!1}return!0}containsPoint(e){const t=this.planes;for(let n=0;n<6;n++)if(t[n].distanceToPoint(e)<0)return!1;return!0}clone(){return new this.constructor().copy(this)}}function ap(){let i=null,e=!1,t=null,n=null;function s(r,a){t(r,a),n=i.requestAnimationFrame(s)}return{start:function(){e!==!0&&t!==null&&(n=i.requestAnimationFrame(s),e=!0)},stop:function(){i.cancelAnimationFrame(n),e=!1},setAnimationLoop:function(r){t=r},setContext:function(r){i=r}}}function m_(i){const e=new WeakMap;function t(o,l){const c=o.array,h=o.usage,u=c.byteLength,d=i.createBuffer();i.bindBuffer(l,d),i.bufferData(l,c,h),o.onUploadCallback();let f;if(c instanceof Float32Array)f=i.FLOAT;else if(c instanceof Uint16Array)o.isFloat16BufferAttribute?f=i.HALF_FLOAT:f=i.UNSIGNED_SHORT;else if(c instanceof Int16Array)f=i.SHORT;else if(c instanceof Uint32Array)f=i.UNSIGNED_INT;else if(c instanceof Int32Array)f=i.INT;else if(c instanceof Int8Array)f=i.BYTE;else if(c instanceof Uint8Array)f=i.UNSIGNED_BYTE;else if(c instanceof Uint8ClampedArray)f=i.UNSIGNED_BYTE;else throw new Error("THREE.WebGLAttributes: Unsupported buffer data format: "+c);return{buffer:d,type:f,bytesPerElement:c.BYTES_PER_ELEMENT,version:o.version,size:u}}function n(o,l,c){const h=l.array,u=l._updateRange,d=l.updateRanges;if(i.bindBuffer(c,o),u.count===-1&&d.length===0&&i.bufferSubData(c,0,h),d.length!==0){for(let f=0,g=d.length;f<g;f++){const _=d[f];i.bufferSubData(c,_.start*h.BYTES_PER_ELEMENT,h,_.start,_.count)}l.clearUpdateRanges()}u.count!==-1&&(i.bufferSubData(c,u.offset*h.BYTES_PER_ELEMENT,h,u.offset,u.count),u.count=-1),l.onUploadCallback()}function s(o){return o.isInterleavedBufferAttribute&&(o=o.data),e.get(o)}function r(o){o.isInterleavedBufferAttribute&&(o=o.data);const l=e.get(o);l&&(i.deleteBuffer(l.buffer),e.delete(o))}function a(o,l){if(o.isInterleavedBufferAttribute&&(o=o.data),o.isGLBufferAttribute){const h=e.get(o);(!h||h.version<o.version)&&e.set(o,{buffer:o.buffer,type:o.type,bytesPerElement:o.elementSize,version:o.version});return}const c=e.get(o);if(c===void 0)e.set(o,t(o,l));else if(c.version<o.version){if(c.size!==o.array.byteLength)throw new Error("THREE.WebGLAttributes: The size of the buffer attribute's array buffer does not match the original size. Resizing buffer attributes is not supported.");n(c.buffer,o,l),c.version=o.version}}return{get:s,remove:r,update:a}}class $a extends Gt{constructor(e=1,t=1,n=1,s=1){super(),this.type="PlaneGeometry",this.parameters={width:e,height:t,widthSegments:n,heightSegments:s};const r=e/2,a=t/2,o=Math.floor(n),l=Math.floor(s),c=o+1,h=l+1,u=e/o,d=t/l,f=[],g=[],_=[],p=[];for(let m=0;m<h;m++){const M=m*d-a;for(let v=0;v<c;v++){const b=v*u-r;g.push(b,-M,0),_.push(0,0,1),p.push(v/o),p.push(1-m/l)}}for(let m=0;m<l;m++)for(let M=0;M<o;M++){const v=M+c*m,b=M+c*(m+1),N=M+1+c*(m+1),A=M+1+c*m;f.push(v,b,A),f.push(b,N,A)}this.setIndex(f),this.setAttribute("position",new zt(g,3)),this.setAttribute("normal",new zt(_,3)),this.setAttribute("uv",new zt(p,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new $a(e.width,e.height,e.widthSegments,e.heightSegments)}}var g_=`#ifdef USE_ALPHAHASH
	if ( diffuseColor.a < getAlphaHashThreshold( vPosition ) ) discard;
#endif`,__=`#ifdef USE_ALPHAHASH
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
#endif`,x_=`#ifdef USE_ALPHAMAP
	diffuseColor.a *= texture2D( alphaMap, vAlphaMapUv ).g;
#endif`,v_=`#ifdef USE_ALPHAMAP
	uniform sampler2D alphaMap;
#endif`,y_=`#ifdef USE_ALPHATEST
	#ifdef ALPHA_TO_COVERAGE
	diffuseColor.a = smoothstep( alphaTest, alphaTest + fwidth( diffuseColor.a ), diffuseColor.a );
	if ( diffuseColor.a == 0.0 ) discard;
	#else
	if ( diffuseColor.a < alphaTest ) discard;
	#endif
#endif`,M_=`#ifdef USE_ALPHATEST
	uniform float alphaTest;
#endif`,S_=`#ifdef USE_AOMAP
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
#endif`,b_=`#ifdef USE_AOMAP
	uniform sampler2D aoMap;
	uniform float aoMapIntensity;
#endif`,w_=`#ifdef USE_BATCHING
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
#endif`,E_=`#ifdef USE_BATCHING
	mat4 batchingMatrix = getBatchingMatrix( getIndirectIndex( gl_DrawID ) );
#endif`,T_=`vec3 transformed = vec3( position );
#ifdef USE_ALPHAHASH
	vPosition = vec3( position );
#endif`,A_=`vec3 objectNormal = vec3( normal );
#ifdef USE_TANGENT
	vec3 objectTangent = vec3( tangent.xyz );
#endif`,R_=`float G_BlinnPhong_Implicit( ) {
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
} // validated`,C_=`#ifdef USE_IRIDESCENCE
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
#endif`,P_=`#ifdef USE_BUMPMAP
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
#endif`,L_=`#if NUM_CLIPPING_PLANES > 0
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
#endif`,D_=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
	uniform vec4 clippingPlanes[ NUM_CLIPPING_PLANES ];
#endif`,I_=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
#endif`,U_=`#if NUM_CLIPPING_PLANES > 0
	vClipPosition = - mvPosition.xyz;
#endif`,N_=`#if defined( USE_COLOR_ALPHA )
	diffuseColor *= vColor;
#elif defined( USE_COLOR )
	diffuseColor.rgb *= vColor;
#endif`,F_=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR )
	varying vec3 vColor;
#endif`,O_=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR ) || defined( USE_INSTANCING_COLOR ) || defined( USE_BATCHING_COLOR )
	varying vec3 vColor;
#endif`,B_=`#if defined( USE_COLOR_ALPHA )
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
#endif`,z_=`#define PI 3.141592653589793
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
} // validated`,k_=`#ifdef ENVMAP_TYPE_CUBE_UV
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
#endif`,H_=`vec3 transformedNormal = objectNormal;
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
#endif`,V_=`#ifdef USE_DISPLACEMENTMAP
	uniform sampler2D displacementMap;
	uniform float displacementScale;
	uniform float displacementBias;
#endif`,G_=`#ifdef USE_DISPLACEMENTMAP
	transformed += normalize( objectNormal ) * ( texture2D( displacementMap, vDisplacementMapUv ).x * displacementScale + displacementBias );
#endif`,W_=`#ifdef USE_EMISSIVEMAP
	vec4 emissiveColor = texture2D( emissiveMap, vEmissiveMapUv );
	totalEmissiveRadiance *= emissiveColor.rgb;
#endif`,X_=`#ifdef USE_EMISSIVEMAP
	uniform sampler2D emissiveMap;
#endif`,q_="gl_FragColor = linearToOutputTexel( gl_FragColor );",$_=`
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
}`,Y_=`#ifdef USE_ENVMAP
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
#endif`,j_=`#ifdef USE_ENVMAP
	uniform float envMapIntensity;
	uniform float flipEnvMap;
	uniform mat3 envMapRotation;
	#ifdef ENVMAP_TYPE_CUBE
		uniform samplerCube envMap;
	#else
		uniform sampler2D envMap;
	#endif
	
#endif`,K_=`#ifdef USE_ENVMAP
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
#endif`,Z_=`#ifdef USE_ENVMAP
	#if defined( USE_BUMPMAP ) || defined( USE_NORMALMAP ) || defined( PHONG ) || defined( LAMBERT )
		#define ENV_WORLDPOS
	#endif
	#ifdef ENV_WORLDPOS
		
		varying vec3 vWorldPosition;
	#else
		varying vec3 vReflect;
		uniform float refractionRatio;
	#endif
#endif`,J_=`#ifdef USE_ENVMAP
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
#endif`,Q_=`#ifdef USE_FOG
	vFogDepth = - mvPosition.z;
#endif`,e0=`#ifdef USE_FOG
	varying float vFogDepth;
#endif`,t0=`#ifdef USE_FOG
	#ifdef FOG_EXP2
		float fogFactor = 1.0 - exp( - fogDensity * fogDensity * vFogDepth * vFogDepth );
	#else
		float fogFactor = smoothstep( fogNear, fogFar, vFogDepth );
	#endif
	gl_FragColor.rgb = mix( gl_FragColor.rgb, fogColor, fogFactor );
#endif`,n0=`#ifdef USE_FOG
	uniform vec3 fogColor;
	varying float vFogDepth;
	#ifdef FOG_EXP2
		uniform float fogDensity;
	#else
		uniform float fogNear;
		uniform float fogFar;
	#endif
#endif`,i0=`#ifdef USE_GRADIENTMAP
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
}`,s0=`#ifdef USE_LIGHTMAP
	uniform sampler2D lightMap;
	uniform float lightMapIntensity;
#endif`,r0=`LambertMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularStrength = specularStrength;`,a0=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Lambert`,o0=`uniform bool receiveShadow;
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
#endif`,l0=`#ifdef USE_ENVMAP
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
#endif`,c0=`ToonMaterial material;
material.diffuseColor = diffuseColor.rgb;`,h0=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Toon`,u0=`BlinnPhongMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularColor = specular;
material.specularShininess = shininess;
material.specularStrength = specularStrength;`,d0=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_BlinnPhong`,f0=`PhysicalMaterial material;
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
#endif`,p0=`struct PhysicalMaterial {
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
}`,m0=`
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
#endif`,g0=`#if defined( RE_IndirectDiffuse )
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
#endif`,_0=`#if defined( RE_IndirectDiffuse )
	RE_IndirectDiffuse( irradiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif
#if defined( RE_IndirectSpecular )
	RE_IndirectSpecular( radiance, iblIrradiance, clearcoatRadiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif`,x0=`#if defined( USE_LOGDEPTHBUF )
	gl_FragDepth = vIsPerspective == 0.0 ? gl_FragCoord.z : log2( vFragDepth ) * logDepthBufFC * 0.5;
#endif`,v0=`#if defined( USE_LOGDEPTHBUF )
	uniform float logDepthBufFC;
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,y0=`#ifdef USE_LOGDEPTHBUF
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,M0=`#ifdef USE_LOGDEPTHBUF
	vFragDepth = 1.0 + gl_Position.w;
	vIsPerspective = float( isPerspectiveMatrix( projectionMatrix ) );
#endif`,S0=`#ifdef USE_MAP
	vec4 sampledDiffuseColor = texture2D( map, vMapUv );
	#ifdef DECODE_VIDEO_TEXTURE
		sampledDiffuseColor = vec4( mix( pow( sampledDiffuseColor.rgb * 0.9478672986 + vec3( 0.0521327014 ), vec3( 2.4 ) ), sampledDiffuseColor.rgb * 0.0773993808, vec3( lessThanEqual( sampledDiffuseColor.rgb, vec3( 0.04045 ) ) ) ), sampledDiffuseColor.w );
	
	#endif
	diffuseColor *= sampledDiffuseColor;
#endif`,b0=`#ifdef USE_MAP
	uniform sampler2D map;
#endif`,w0=`#if defined( USE_MAP ) || defined( USE_ALPHAMAP )
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
#endif`,E0=`#if defined( USE_POINTS_UV )
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
#endif`,T0=`float metalnessFactor = metalness;
#ifdef USE_METALNESSMAP
	vec4 texelMetalness = texture2D( metalnessMap, vMetalnessMapUv );
	metalnessFactor *= texelMetalness.b;
#endif`,A0=`#ifdef USE_METALNESSMAP
	uniform sampler2D metalnessMap;
#endif`,R0=`#ifdef USE_INSTANCING_MORPH
	float morphTargetInfluences[ MORPHTARGETS_COUNT ];
	float morphTargetBaseInfluence = texelFetch( morphTexture, ivec2( 0, gl_InstanceID ), 0 ).r;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		morphTargetInfluences[i] =  texelFetch( morphTexture, ivec2( i + 1, gl_InstanceID ), 0 ).r;
	}
#endif`,C0=`#if defined( USE_MORPHCOLORS )
	vColor *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		#if defined( USE_COLOR_ALPHA )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ) * morphTargetInfluences[ i ];
		#elif defined( USE_COLOR )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ).rgb * morphTargetInfluences[ i ];
		#endif
	}
#endif`,P0=`#ifdef USE_MORPHNORMALS
	objectNormal *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) objectNormal += getMorph( gl_VertexID, i, 1 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,L0=`#ifdef USE_MORPHTARGETS
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
#endif`,D0=`#ifdef USE_MORPHTARGETS
	transformed *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) transformed += getMorph( gl_VertexID, i, 0 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,I0=`float faceDirection = gl_FrontFacing ? 1.0 : - 1.0;
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
vec3 nonPerturbedNormal = normal;`,U0=`#ifdef USE_NORMALMAP_OBJECTSPACE
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
#endif`,N0=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,F0=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,O0=`#ifndef FLAT_SHADED
	vNormal = normalize( transformedNormal );
	#ifdef USE_TANGENT
		vTangent = normalize( transformedTangent );
		vBitangent = normalize( cross( vNormal, vTangent ) * tangent.w );
	#endif
#endif`,B0=`#ifdef USE_NORMALMAP
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
#endif`,z0=`#ifdef USE_CLEARCOAT
	vec3 clearcoatNormal = nonPerturbedNormal;
#endif`,k0=`#ifdef USE_CLEARCOAT_NORMALMAP
	vec3 clearcoatMapN = texture2D( clearcoatNormalMap, vClearcoatNormalMapUv ).xyz * 2.0 - 1.0;
	clearcoatMapN.xy *= clearcoatNormalScale;
	clearcoatNormal = normalize( tbn2 * clearcoatMapN );
#endif`,H0=`#ifdef USE_CLEARCOATMAP
	uniform sampler2D clearcoatMap;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	uniform sampler2D clearcoatNormalMap;
	uniform vec2 clearcoatNormalScale;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	uniform sampler2D clearcoatRoughnessMap;
#endif`,V0=`#ifdef USE_IRIDESCENCEMAP
	uniform sampler2D iridescenceMap;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	uniform sampler2D iridescenceThicknessMap;
#endif`,G0=`#ifdef OPAQUE
diffuseColor.a = 1.0;
#endif
#ifdef USE_TRANSMISSION
diffuseColor.a *= material.transmissionAlpha;
#endif
gl_FragColor = vec4( outgoingLight, diffuseColor.a );`,W0=`vec3 packNormalToRGB( const in vec3 normal ) {
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
}`,X0=`#ifdef PREMULTIPLIED_ALPHA
	gl_FragColor.rgb *= gl_FragColor.a;
#endif`,q0=`vec4 mvPosition = vec4( transformed, 1.0 );
#ifdef USE_BATCHING
	mvPosition = batchingMatrix * mvPosition;
#endif
#ifdef USE_INSTANCING
	mvPosition = instanceMatrix * mvPosition;
#endif
mvPosition = modelViewMatrix * mvPosition;
gl_Position = projectionMatrix * mvPosition;`,$0=`#ifdef DITHERING
	gl_FragColor.rgb = dithering( gl_FragColor.rgb );
#endif`,Y0=`#ifdef DITHERING
	vec3 dithering( vec3 color ) {
		float grid_position = rand( gl_FragCoord.xy );
		vec3 dither_shift_RGB = vec3( 0.25 / 255.0, -0.25 / 255.0, 0.25 / 255.0 );
		dither_shift_RGB = mix( 2.0 * dither_shift_RGB, -2.0 * dither_shift_RGB, grid_position );
		return color + dither_shift_RGB;
	}
#endif`,j0=`float roughnessFactor = roughness;
#ifdef USE_ROUGHNESSMAP
	vec4 texelRoughness = texture2D( roughnessMap, vRoughnessMapUv );
	roughnessFactor *= texelRoughness.g;
#endif`,K0=`#ifdef USE_ROUGHNESSMAP
	uniform sampler2D roughnessMap;
#endif`,Z0=`#if NUM_SPOT_LIGHT_COORDS > 0
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
#endif`,J0=`#if NUM_SPOT_LIGHT_COORDS > 0
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
#endif`,Q0=`#if ( defined( USE_SHADOWMAP ) && ( NUM_DIR_LIGHT_SHADOWS > 0 || NUM_POINT_LIGHT_SHADOWS > 0 ) ) || ( NUM_SPOT_LIGHT_COORDS > 0 )
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
#endif`,ex=`float getShadowMask() {
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
}`,tx=`#ifdef USE_SKINNING
	mat4 boneMatX = getBoneMatrix( skinIndex.x );
	mat4 boneMatY = getBoneMatrix( skinIndex.y );
	mat4 boneMatZ = getBoneMatrix( skinIndex.z );
	mat4 boneMatW = getBoneMatrix( skinIndex.w );
#endif`,nx=`#ifdef USE_SKINNING
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
#endif`,ix=`#ifdef USE_SKINNING
	vec4 skinVertex = bindMatrix * vec4( transformed, 1.0 );
	vec4 skinned = vec4( 0.0 );
	skinned += boneMatX * skinVertex * skinWeight.x;
	skinned += boneMatY * skinVertex * skinWeight.y;
	skinned += boneMatZ * skinVertex * skinWeight.z;
	skinned += boneMatW * skinVertex * skinWeight.w;
	transformed = ( bindMatrixInverse * skinned ).xyz;
#endif`,sx=`#ifdef USE_SKINNING
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
#endif`,rx=`float specularStrength;
#ifdef USE_SPECULARMAP
	vec4 texelSpecular = texture2D( specularMap, vSpecularMapUv );
	specularStrength = texelSpecular.r;
#else
	specularStrength = 1.0;
#endif`,ax=`#ifdef USE_SPECULARMAP
	uniform sampler2D specularMap;
#endif`,ox=`#if defined( TONE_MAPPING )
	gl_FragColor.rgb = toneMapping( gl_FragColor.rgb );
#endif`,lx=`#ifndef saturate
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
vec3 CustomToneMapping( vec3 color ) { return color; }`,cx=`#ifdef USE_TRANSMISSION
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
#endif`,hx=`#ifdef USE_TRANSMISSION
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
#endif`,ux=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
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
#endif`,dx=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
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
#endif`,fx=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
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
#endif`,px=`#if defined( USE_ENVMAP ) || defined( DISTANCE ) || defined ( USE_SHADOWMAP ) || defined ( USE_TRANSMISSION ) || NUM_SPOT_LIGHT_COORDS > 0
	vec4 worldPosition = vec4( transformed, 1.0 );
	#ifdef USE_BATCHING
		worldPosition = batchingMatrix * worldPosition;
	#endif
	#ifdef USE_INSTANCING
		worldPosition = instanceMatrix * worldPosition;
	#endif
	worldPosition = modelMatrix * worldPosition;
#endif`;const mx=`varying vec2 vUv;
uniform mat3 uvTransform;
void main() {
	vUv = ( uvTransform * vec3( uv, 1 ) ).xy;
	gl_Position = vec4( position.xy, 1.0, 1.0 );
}`,gx=`uniform sampler2D t2D;
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
}`,_x=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,xx=`#ifdef ENVMAP_TYPE_CUBE
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
}`,vx=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,yx=`uniform samplerCube tCube;
uniform float tFlip;
uniform float opacity;
varying vec3 vWorldDirection;
void main() {
	vec4 texColor = textureCube( tCube, vec3( tFlip * vWorldDirection.x, vWorldDirection.yz ) );
	gl_FragColor = texColor;
	gl_FragColor.a *= opacity;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,Mx=`#include <common>
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
}`,Sx=`#if DEPTH_PACKING == 3200
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
}`,bx=`#define DISTANCE
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
}`,wx=`#define DISTANCE
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
}`,Ex=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
}`,Tx=`uniform sampler2D tEquirect;
varying vec3 vWorldDirection;
#include <common>
void main() {
	vec3 direction = normalize( vWorldDirection );
	vec2 sampleUV = equirectUv( direction );
	gl_FragColor = texture2D( tEquirect, sampleUV );
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,Ax=`uniform float scale;
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
}`,Rx=`uniform vec3 diffuse;
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
}`,Cx=`#include <common>
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
}`,Px=`uniform vec3 diffuse;
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
}`,Lx=`#define LAMBERT
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
}`,Dx=`#define LAMBERT
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
}`,Ix=`#define MATCAP
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
}`,Ux=`#define MATCAP
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
}`,Nx=`#define NORMAL
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
}`,Fx=`#define NORMAL
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
}`,Ox=`#define PHONG
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
}`,Bx=`#define PHONG
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
}`,zx=`#define STANDARD
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
}`,kx=`#define STANDARD
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
}`,Hx=`#define TOON
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
}`,Vx=`#define TOON
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
}`,Gx=`uniform float size;
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
}`,Wx=`uniform vec3 diffuse;
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
}`,Xx=`#include <common>
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
}`,qx=`uniform vec3 color;
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
}`,$x=`uniform float rotation;
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
}`,Yx=`uniform vec3 diffuse;
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
}`,rt={alphahash_fragment:g_,alphahash_pars_fragment:__,alphamap_fragment:x_,alphamap_pars_fragment:v_,alphatest_fragment:y_,alphatest_pars_fragment:M_,aomap_fragment:S_,aomap_pars_fragment:b_,batching_pars_vertex:w_,batching_vertex:E_,begin_vertex:T_,beginnormal_vertex:A_,bsdfs:R_,iridescence_fragment:C_,bumpmap_pars_fragment:P_,clipping_planes_fragment:L_,clipping_planes_pars_fragment:D_,clipping_planes_pars_vertex:I_,clipping_planes_vertex:U_,color_fragment:N_,color_pars_fragment:F_,color_pars_vertex:O_,color_vertex:B_,common:z_,cube_uv_reflection_fragment:k_,defaultnormal_vertex:H_,displacementmap_pars_vertex:V_,displacementmap_vertex:G_,emissivemap_fragment:W_,emissivemap_pars_fragment:X_,colorspace_fragment:q_,colorspace_pars_fragment:$_,envmap_fragment:Y_,envmap_common_pars_fragment:j_,envmap_pars_fragment:K_,envmap_pars_vertex:Z_,envmap_physical_pars_fragment:l0,envmap_vertex:J_,fog_vertex:Q_,fog_pars_vertex:e0,fog_fragment:t0,fog_pars_fragment:n0,gradientmap_pars_fragment:i0,lightmap_pars_fragment:s0,lights_lambert_fragment:r0,lights_lambert_pars_fragment:a0,lights_pars_begin:o0,lights_toon_fragment:c0,lights_toon_pars_fragment:h0,lights_phong_fragment:u0,lights_phong_pars_fragment:d0,lights_physical_fragment:f0,lights_physical_pars_fragment:p0,lights_fragment_begin:m0,lights_fragment_maps:g0,lights_fragment_end:_0,logdepthbuf_fragment:x0,logdepthbuf_pars_fragment:v0,logdepthbuf_pars_vertex:y0,logdepthbuf_vertex:M0,map_fragment:S0,map_pars_fragment:b0,map_particle_fragment:w0,map_particle_pars_fragment:E0,metalnessmap_fragment:T0,metalnessmap_pars_fragment:A0,morphinstance_vertex:R0,morphcolor_vertex:C0,morphnormal_vertex:P0,morphtarget_pars_vertex:L0,morphtarget_vertex:D0,normal_fragment_begin:I0,normal_fragment_maps:U0,normal_pars_fragment:N0,normal_pars_vertex:F0,normal_vertex:O0,normalmap_pars_fragment:B0,clearcoat_normal_fragment_begin:z0,clearcoat_normal_fragment_maps:k0,clearcoat_pars_fragment:H0,iridescence_pars_fragment:V0,opaque_fragment:G0,packing:W0,premultiplied_alpha_fragment:X0,project_vertex:q0,dithering_fragment:$0,dithering_pars_fragment:Y0,roughnessmap_fragment:j0,roughnessmap_pars_fragment:K0,shadowmap_pars_fragment:Z0,shadowmap_pars_vertex:J0,shadowmap_vertex:Q0,shadowmask_pars_fragment:ex,skinbase_vertex:tx,skinning_pars_vertex:nx,skinning_vertex:ix,skinnormal_vertex:sx,specularmap_fragment:rx,specularmap_pars_fragment:ax,tonemapping_fragment:ox,tonemapping_pars_fragment:lx,transmission_fragment:cx,transmission_pars_fragment:hx,uv_pars_fragment:ux,uv_pars_vertex:dx,uv_vertex:fx,worldpos_vertex:px,background_vert:mx,background_frag:gx,backgroundCube_vert:_x,backgroundCube_frag:xx,cube_vert:vx,cube_frag:yx,depth_vert:Mx,depth_frag:Sx,distanceRGBA_vert:bx,distanceRGBA_frag:wx,equirect_vert:Ex,equirect_frag:Tx,linedashed_vert:Ax,linedashed_frag:Rx,meshbasic_vert:Cx,meshbasic_frag:Px,meshlambert_vert:Lx,meshlambert_frag:Dx,meshmatcap_vert:Ix,meshmatcap_frag:Ux,meshnormal_vert:Nx,meshnormal_frag:Fx,meshphong_vert:Ox,meshphong_frag:Bx,meshphysical_vert:zx,meshphysical_frag:kx,meshtoon_vert:Hx,meshtoon_frag:Vx,points_vert:Gx,points_frag:Wx,shadow_vert:Xx,shadow_frag:qx,sprite_vert:$x,sprite_frag:Yx},Ce={common:{diffuse:{value:new nt(16777215)},opacity:{value:1},map:{value:null},mapTransform:{value:new at},alphaMap:{value:null},alphaMapTransform:{value:new at},alphaTest:{value:0}},specularmap:{specularMap:{value:null},specularMapTransform:{value:new at}},envmap:{envMap:{value:null},envMapRotation:{value:new at},flipEnvMap:{value:-1},reflectivity:{value:1},ior:{value:1.5},refractionRatio:{value:.98}},aomap:{aoMap:{value:null},aoMapIntensity:{value:1},aoMapTransform:{value:new at}},lightmap:{lightMap:{value:null},lightMapIntensity:{value:1},lightMapTransform:{value:new at}},bumpmap:{bumpMap:{value:null},bumpMapTransform:{value:new at},bumpScale:{value:1}},normalmap:{normalMap:{value:null},normalMapTransform:{value:new at},normalScale:{value:new $e(1,1)}},displacementmap:{displacementMap:{value:null},displacementMapTransform:{value:new at},displacementScale:{value:1},displacementBias:{value:0}},emissivemap:{emissiveMap:{value:null},emissiveMapTransform:{value:new at}},metalnessmap:{metalnessMap:{value:null},metalnessMapTransform:{value:new at}},roughnessmap:{roughnessMap:{value:null},roughnessMapTransform:{value:new at}},gradientmap:{gradientMap:{value:null}},fog:{fogDensity:{value:25e-5},fogNear:{value:1},fogFar:{value:2e3},fogColor:{value:new nt(16777215)}},lights:{ambientLightColor:{value:[]},lightProbe:{value:[]},directionalLights:{value:[],properties:{direction:{},color:{}}},directionalLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},directionalShadowMap:{value:[]},directionalShadowMatrix:{value:[]},spotLights:{value:[],properties:{color:{},position:{},direction:{},distance:{},coneCos:{},penumbraCos:{},decay:{}}},spotLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},spotLightMap:{value:[]},spotShadowMap:{value:[]},spotLightMatrix:{value:[]},pointLights:{value:[],properties:{color:{},position:{},decay:{},distance:{}}},pointLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{},shadowCameraNear:{},shadowCameraFar:{}}},pointShadowMap:{value:[]},pointShadowMatrix:{value:[]},hemisphereLights:{value:[],properties:{direction:{},skyColor:{},groundColor:{}}},rectAreaLights:{value:[],properties:{color:{},position:{},width:{},height:{}}},ltc_1:{value:null},ltc_2:{value:null}},points:{diffuse:{value:new nt(16777215)},opacity:{value:1},size:{value:1},scale:{value:1},map:{value:null},alphaMap:{value:null},alphaMapTransform:{value:new at},alphaTest:{value:0},uvTransform:{value:new at}},sprite:{diffuse:{value:new nt(16777215)},opacity:{value:1},center:{value:new $e(.5,.5)},rotation:{value:0},map:{value:null},mapTransform:{value:new at},alphaMap:{value:null},alphaMapTransform:{value:new at},alphaTest:{value:0}}},wi={basic:{uniforms:Cn([Ce.common,Ce.specularmap,Ce.envmap,Ce.aomap,Ce.lightmap,Ce.fog]),vertexShader:rt.meshbasic_vert,fragmentShader:rt.meshbasic_frag},lambert:{uniforms:Cn([Ce.common,Ce.specularmap,Ce.envmap,Ce.aomap,Ce.lightmap,Ce.emissivemap,Ce.bumpmap,Ce.normalmap,Ce.displacementmap,Ce.fog,Ce.lights,{emissive:{value:new nt(0)}}]),vertexShader:rt.meshlambert_vert,fragmentShader:rt.meshlambert_frag},phong:{uniforms:Cn([Ce.common,Ce.specularmap,Ce.envmap,Ce.aomap,Ce.lightmap,Ce.emissivemap,Ce.bumpmap,Ce.normalmap,Ce.displacementmap,Ce.fog,Ce.lights,{emissive:{value:new nt(0)},specular:{value:new nt(1118481)},shininess:{value:30}}]),vertexShader:rt.meshphong_vert,fragmentShader:rt.meshphong_frag},standard:{uniforms:Cn([Ce.common,Ce.envmap,Ce.aomap,Ce.lightmap,Ce.emissivemap,Ce.bumpmap,Ce.normalmap,Ce.displacementmap,Ce.roughnessmap,Ce.metalnessmap,Ce.fog,Ce.lights,{emissive:{value:new nt(0)},roughness:{value:1},metalness:{value:0},envMapIntensity:{value:1}}]),vertexShader:rt.meshphysical_vert,fragmentShader:rt.meshphysical_frag},toon:{uniforms:Cn([Ce.common,Ce.aomap,Ce.lightmap,Ce.emissivemap,Ce.bumpmap,Ce.normalmap,Ce.displacementmap,Ce.gradientmap,Ce.fog,Ce.lights,{emissive:{value:new nt(0)}}]),vertexShader:rt.meshtoon_vert,fragmentShader:rt.meshtoon_frag},matcap:{uniforms:Cn([Ce.common,Ce.bumpmap,Ce.normalmap,Ce.displacementmap,Ce.fog,{matcap:{value:null}}]),vertexShader:rt.meshmatcap_vert,fragmentShader:rt.meshmatcap_frag},points:{uniforms:Cn([Ce.points,Ce.fog]),vertexShader:rt.points_vert,fragmentShader:rt.points_frag},dashed:{uniforms:Cn([Ce.common,Ce.fog,{scale:{value:1},dashSize:{value:1},totalSize:{value:2}}]),vertexShader:rt.linedashed_vert,fragmentShader:rt.linedashed_frag},depth:{uniforms:Cn([Ce.common,Ce.displacementmap]),vertexShader:rt.depth_vert,fragmentShader:rt.depth_frag},normal:{uniforms:Cn([Ce.common,Ce.bumpmap,Ce.normalmap,Ce.displacementmap,{opacity:{value:1}}]),vertexShader:rt.meshnormal_vert,fragmentShader:rt.meshnormal_frag},sprite:{uniforms:Cn([Ce.sprite,Ce.fog]),vertexShader:rt.sprite_vert,fragmentShader:rt.sprite_frag},background:{uniforms:{uvTransform:{value:new at},t2D:{value:null},backgroundIntensity:{value:1}},vertexShader:rt.background_vert,fragmentShader:rt.background_frag},backgroundCube:{uniforms:{envMap:{value:null},flipEnvMap:{value:-1},backgroundBlurriness:{value:0},backgroundIntensity:{value:1},backgroundRotation:{value:new at}},vertexShader:rt.backgroundCube_vert,fragmentShader:rt.backgroundCube_frag},cube:{uniforms:{tCube:{value:null},tFlip:{value:-1},opacity:{value:1}},vertexShader:rt.cube_vert,fragmentShader:rt.cube_frag},equirect:{uniforms:{tEquirect:{value:null}},vertexShader:rt.equirect_vert,fragmentShader:rt.equirect_frag},distanceRGBA:{uniforms:Cn([Ce.common,Ce.displacementmap,{referencePosition:{value:new V},nearDistance:{value:1},farDistance:{value:1e3}}]),vertexShader:rt.distanceRGBA_vert,fragmentShader:rt.distanceRGBA_frag},shadow:{uniforms:Cn([Ce.lights,Ce.fog,{color:{value:new nt(0)},opacity:{value:1}}]),vertexShader:rt.shadow_vert,fragmentShader:rt.shadow_frag}};wi.physical={uniforms:Cn([wi.standard.uniforms,{clearcoat:{value:0},clearcoatMap:{value:null},clearcoatMapTransform:{value:new at},clearcoatNormalMap:{value:null},clearcoatNormalMapTransform:{value:new at},clearcoatNormalScale:{value:new $e(1,1)},clearcoatRoughness:{value:0},clearcoatRoughnessMap:{value:null},clearcoatRoughnessMapTransform:{value:new at},dispersion:{value:0},iridescence:{value:0},iridescenceMap:{value:null},iridescenceMapTransform:{value:new at},iridescenceIOR:{value:1.3},iridescenceThicknessMinimum:{value:100},iridescenceThicknessMaximum:{value:400},iridescenceThicknessMap:{value:null},iridescenceThicknessMapTransform:{value:new at},sheen:{value:0},sheenColor:{value:new nt(0)},sheenColorMap:{value:null},sheenColorMapTransform:{value:new at},sheenRoughness:{value:1},sheenRoughnessMap:{value:null},sheenRoughnessMapTransform:{value:new at},transmission:{value:0},transmissionMap:{value:null},transmissionMapTransform:{value:new at},transmissionSamplerSize:{value:new $e},transmissionSamplerMap:{value:null},thickness:{value:0},thicknessMap:{value:null},thicknessMapTransform:{value:new at},attenuationDistance:{value:0},attenuationColor:{value:new nt(0)},specularColor:{value:new nt(1,1,1)},specularColorMap:{value:null},specularColorMapTransform:{value:new at},specularIntensity:{value:1},specularIntensityMap:{value:null},specularIntensityMapTransform:{value:new at},anisotropyVector:{value:new $e},anisotropyMap:{value:null},anisotropyMapTransform:{value:new at}}]),vertexShader:rt.meshphysical_vert,fragmentShader:rt.meshphysical_frag};const bo={r:0,b:0,g:0},Ds=new Ci,jx=new Bt;function Kx(i,e,t,n,s,r,a){const o=new nt(0);let l=r===!0?0:1,c,h,u=null,d=0,f=null;function g(M){let v=M.isScene===!0?M.background:null;return v&&v.isTexture&&(v=(M.backgroundBlurriness>0?t:e).get(v)),v}function _(M){let v=!1;const b=g(M);b===null?m(o,l):b&&b.isColor&&(m(b,1),v=!0);const N=i.xr.getEnvironmentBlendMode();N==="additive"?n.buffers.color.setClear(0,0,0,1,a):N==="alpha-blend"&&n.buffers.color.setClear(0,0,0,0,a),(i.autoClear||v)&&(n.buffers.depth.setTest(!0),n.buffers.depth.setMask(!0),n.buffers.color.setMask(!0),i.clear(i.autoClearColor,i.autoClearDepth,i.autoClearStencil))}function p(M,v){const b=g(v);b&&(b.isCubeTexture||b.mapping===ll)?(h===void 0&&(h=new Qt(new Ei(1,1,1),new _s({name:"BackgroundCubeMaterial",uniforms:Yr(wi.backgroundCube.uniforms),vertexShader:wi.backgroundCube.vertexShader,fragmentShader:wi.backgroundCube.fragmentShader,side:Nn,depthTest:!1,depthWrite:!1,fog:!1})),h.geometry.deleteAttribute("normal"),h.geometry.deleteAttribute("uv"),h.onBeforeRender=function(N,A,R){this.matrixWorld.copyPosition(R.matrixWorld)},Object.defineProperty(h.material,"envMap",{get:function(){return this.uniforms.envMap.value}}),s.update(h)),Ds.copy(v.backgroundRotation),Ds.x*=-1,Ds.y*=-1,Ds.z*=-1,b.isCubeTexture&&b.isRenderTargetTexture===!1&&(Ds.y*=-1,Ds.z*=-1),h.material.uniforms.envMap.value=b,h.material.uniforms.flipEnvMap.value=b.isCubeTexture&&b.isRenderTargetTexture===!1?-1:1,h.material.uniforms.backgroundBlurriness.value=v.backgroundBlurriness,h.material.uniforms.backgroundIntensity.value=v.backgroundIntensity,h.material.uniforms.backgroundRotation.value.setFromMatrix4(jx.makeRotationFromEuler(Ds)),h.material.toneMapped=bt.getTransfer(b.colorSpace)!==Ot,(u!==b||d!==b.version||f!==i.toneMapping)&&(h.material.needsUpdate=!0,u=b,d=b.version,f=i.toneMapping),h.layers.enableAll(),M.unshift(h,h.geometry,h.material,0,0,null)):b&&b.isTexture&&(c===void 0&&(c=new Qt(new $a(2,2),new _s({name:"BackgroundMaterial",uniforms:Yr(wi.background.uniforms),vertexShader:wi.background.vertexShader,fragmentShader:wi.background.fragmentShader,side:gs,depthTest:!1,depthWrite:!1,fog:!1})),c.geometry.deleteAttribute("normal"),Object.defineProperty(c.material,"map",{get:function(){return this.uniforms.t2D.value}}),s.update(c)),c.material.uniforms.t2D.value=b,c.material.uniforms.backgroundIntensity.value=v.backgroundIntensity,c.material.toneMapped=bt.getTransfer(b.colorSpace)!==Ot,b.matrixAutoUpdate===!0&&b.updateMatrix(),c.material.uniforms.uvTransform.value.copy(b.matrix),(u!==b||d!==b.version||f!==i.toneMapping)&&(c.material.needsUpdate=!0,u=b,d=b.version,f=i.toneMapping),c.layers.enableAll(),M.unshift(c,c.geometry,c.material,0,0,null))}function m(M,v){M.getRGB(bo,ip(i)),n.buffers.color.setClear(bo.r,bo.g,bo.b,v,a)}return{getClearColor:function(){return o},setClearColor:function(M,v=1){o.set(M),l=v,m(o,l)},getClearAlpha:function(){return l},setClearAlpha:function(M){l=M,m(o,l)},render:_,addToRenderList:p}}function Zx(i,e){const t=i.getParameter(i.MAX_VERTEX_ATTRIBS),n={},s=d(null);let r=s,a=!1;function o(y,P,K,H,Z){let q=!1;const ee=u(H,K,P);r!==ee&&(r=ee,c(r.object)),q=f(y,H,K,Z),q&&g(y,H,K,Z),Z!==null&&e.update(Z,i.ELEMENT_ARRAY_BUFFER),(q||a)&&(a=!1,b(y,P,K,H),Z!==null&&i.bindBuffer(i.ELEMENT_ARRAY_BUFFER,e.get(Z).buffer))}function l(){return i.createVertexArray()}function c(y){return i.bindVertexArray(y)}function h(y){return i.deleteVertexArray(y)}function u(y,P,K){const H=K.wireframe===!0;let Z=n[y.id];Z===void 0&&(Z={},n[y.id]=Z);let q=Z[P.id];q===void 0&&(q={},Z[P.id]=q);let ee=q[H];return ee===void 0&&(ee=d(l()),q[H]=ee),ee}function d(y){const P=[],K=[],H=[];for(let Z=0;Z<t;Z++)P[Z]=0,K[Z]=0,H[Z]=0;return{geometry:null,program:null,wireframe:!1,newAttributes:P,enabledAttributes:K,attributeDivisors:H,object:y,attributes:{},index:null}}function f(y,P,K,H){const Z=r.attributes,q=P.attributes;let ee=0;const Y=K.getAttributes();for(const ne in Y)if(Y[ne].location>=0){const de=Z[ne];let ve=q[ne];if(ve===void 0&&(ne==="instanceMatrix"&&y.instanceMatrix&&(ve=y.instanceMatrix),ne==="instanceColor"&&y.instanceColor&&(ve=y.instanceColor)),de===void 0||de.attribute!==ve||ve&&de.data!==ve.data)return!0;ee++}return r.attributesNum!==ee||r.index!==H}function g(y,P,K,H){const Z={},q=P.attributes;let ee=0;const Y=K.getAttributes();for(const ne in Y)if(Y[ne].location>=0){let de=q[ne];de===void 0&&(ne==="instanceMatrix"&&y.instanceMatrix&&(de=y.instanceMatrix),ne==="instanceColor"&&y.instanceColor&&(de=y.instanceColor));const ve={};ve.attribute=de,de&&de.data&&(ve.data=de.data),Z[ne]=ve,ee++}r.attributes=Z,r.attributesNum=ee,r.index=H}function _(){const y=r.newAttributes;for(let P=0,K=y.length;P<K;P++)y[P]=0}function p(y){m(y,0)}function m(y,P){const K=r.newAttributes,H=r.enabledAttributes,Z=r.attributeDivisors;K[y]=1,H[y]===0&&(i.enableVertexAttribArray(y),H[y]=1),Z[y]!==P&&(i.vertexAttribDivisor(y,P),Z[y]=P)}function M(){const y=r.newAttributes,P=r.enabledAttributes;for(let K=0,H=P.length;K<H;K++)P[K]!==y[K]&&(i.disableVertexAttribArray(K),P[K]=0)}function v(y,P,K,H,Z,q,ee){ee===!0?i.vertexAttribIPointer(y,P,K,Z,q):i.vertexAttribPointer(y,P,K,H,Z,q)}function b(y,P,K,H){_();const Z=H.attributes,q=K.getAttributes(),ee=P.defaultAttributeValues;for(const Y in q){const ne=q[Y];if(ne.location>=0){let ge=Z[Y];if(ge===void 0&&(Y==="instanceMatrix"&&y.instanceMatrix&&(ge=y.instanceMatrix),Y==="instanceColor"&&y.instanceColor&&(ge=y.instanceColor)),ge!==void 0){const de=ge.normalized,ve=ge.itemSize,Te=e.get(ge);if(Te===void 0)continue;const ye=Te.buffer,ie=Te.type,he=Te.bytesPerElement,Me=ie===i.INT||ie===i.UNSIGNED_INT||ge.gpuType===Sh;if(ge.isInterleavedBufferAttribute){const fe=ge.data,ze=fe.stride,Ge=ge.offset;if(fe.isInstancedInterleavedBuffer){for(let Fe=0;Fe<ne.locationSize;Fe++)m(ne.location+Fe,fe.meshPerAttribute);y.isInstancedMesh!==!0&&H._maxInstanceCount===void 0&&(H._maxInstanceCount=fe.meshPerAttribute*fe.count)}else for(let Fe=0;Fe<ne.locationSize;Fe++)p(ne.location+Fe);i.bindBuffer(i.ARRAY_BUFFER,ye);for(let Fe=0;Fe<ne.locationSize;Fe++)v(ne.location+Fe,ve/ne.locationSize,ie,de,ze*he,(Ge+ve/ne.locationSize*Fe)*he,Me)}else{if(ge.isInstancedBufferAttribute){for(let fe=0;fe<ne.locationSize;fe++)m(ne.location+fe,ge.meshPerAttribute);y.isInstancedMesh!==!0&&H._maxInstanceCount===void 0&&(H._maxInstanceCount=ge.meshPerAttribute*ge.count)}else for(let fe=0;fe<ne.locationSize;fe++)p(ne.location+fe);i.bindBuffer(i.ARRAY_BUFFER,ye);for(let fe=0;fe<ne.locationSize;fe++)v(ne.location+fe,ve/ne.locationSize,ie,de,ve*he,ve/ne.locationSize*fe*he,Me)}}else if(ee!==void 0){const de=ee[Y];if(de!==void 0)switch(de.length){case 2:i.vertexAttrib2fv(ne.location,de);break;case 3:i.vertexAttrib3fv(ne.location,de);break;case 4:i.vertexAttrib4fv(ne.location,de);break;default:i.vertexAttrib1fv(ne.location,de)}}}}M()}function N(){F();for(const y in n){const P=n[y];for(const K in P){const H=P[K];for(const Z in H)h(H[Z].object),delete H[Z];delete P[K]}delete n[y]}}function A(y){if(n[y.id]===void 0)return;const P=n[y.id];for(const K in P){const H=P[K];for(const Z in H)h(H[Z].object),delete H[Z];delete P[K]}delete n[y.id]}function R(y){for(const P in n){const K=n[P];if(K[y.id]===void 0)continue;const H=K[y.id];for(const Z in H)h(H[Z].object),delete H[Z];delete K[y.id]}}function F(){w(),a=!0,r!==s&&(r=s,c(r.object))}function w(){s.geometry=null,s.program=null,s.wireframe=!1}return{setup:o,reset:F,resetDefaultState:w,dispose:N,releaseStatesOfGeometry:A,releaseStatesOfProgram:R,initAttributes:_,enableAttribute:p,disableUnusedAttributes:M}}function Jx(i,e,t){let n;function s(c){n=c}function r(c,h){i.drawArrays(n,c,h),t.update(h,n,1)}function a(c,h,u){u!==0&&(i.drawArraysInstanced(n,c,h,u),t.update(h,n,u))}function o(c,h,u){if(u===0)return;e.get("WEBGL_multi_draw").multiDrawArraysWEBGL(n,c,0,h,0,u);let f=0;for(let g=0;g<u;g++)f+=h[g];t.update(f,n,1)}function l(c,h,u,d){if(u===0)return;const f=e.get("WEBGL_multi_draw");if(f===null)for(let g=0;g<c.length;g++)a(c[g],h[g],d[g]);else{f.multiDrawArraysInstancedWEBGL(n,c,0,h,0,d,0,u);let g=0;for(let _=0;_<u;_++)g+=h[_];for(let _=0;_<d.length;_++)t.update(g,n,d[_])}}this.setMode=s,this.render=r,this.renderInstances=a,this.renderMultiDraw=o,this.renderMultiDrawInstances=l}function Qx(i,e,t,n){let s;function r(){if(s!==void 0)return s;if(e.has("EXT_texture_filter_anisotropic")===!0){const A=e.get("EXT_texture_filter_anisotropic");s=i.getParameter(A.MAX_TEXTURE_MAX_ANISOTROPY_EXT)}else s=0;return s}function a(A){return!(A!==fi&&n.convert(A)!==i.getParameter(i.IMPLEMENTATION_COLOR_READ_FORMAT))}function o(A){const R=A===Ga&&(e.has("EXT_color_buffer_half_float")||e.has("EXT_color_buffer_float"));return!(A!==Yi&&n.convert(A)!==i.getParameter(i.IMPLEMENTATION_COLOR_READ_TYPE)&&A!==Gi&&!R)}function l(A){if(A==="highp"){if(i.getShaderPrecisionFormat(i.VERTEX_SHADER,i.HIGH_FLOAT).precision>0&&i.getShaderPrecisionFormat(i.FRAGMENT_SHADER,i.HIGH_FLOAT).precision>0)return"highp";A="mediump"}return A==="mediump"&&i.getShaderPrecisionFormat(i.VERTEX_SHADER,i.MEDIUM_FLOAT).precision>0&&i.getShaderPrecisionFormat(i.FRAGMENT_SHADER,i.MEDIUM_FLOAT).precision>0?"mediump":"lowp"}let c=t.precision!==void 0?t.precision:"highp";const h=l(c);h!==c&&(console.warn("THREE.WebGLRenderer:",c,"not supported, using",h,"instead."),c=h);const u=t.logarithmicDepthBuffer===!0,d=i.getParameter(i.MAX_TEXTURE_IMAGE_UNITS),f=i.getParameter(i.MAX_VERTEX_TEXTURE_IMAGE_UNITS),g=i.getParameter(i.MAX_TEXTURE_SIZE),_=i.getParameter(i.MAX_CUBE_MAP_TEXTURE_SIZE),p=i.getParameter(i.MAX_VERTEX_ATTRIBS),m=i.getParameter(i.MAX_VERTEX_UNIFORM_VECTORS),M=i.getParameter(i.MAX_VARYING_VECTORS),v=i.getParameter(i.MAX_FRAGMENT_UNIFORM_VECTORS),b=f>0,N=i.getParameter(i.MAX_SAMPLES);return{isWebGL2:!0,getMaxAnisotropy:r,getMaxPrecision:l,textureFormatReadable:a,textureTypeReadable:o,precision:c,logarithmicDepthBuffer:u,maxTextures:d,maxVertexTextures:f,maxTextureSize:g,maxCubemapSize:_,maxAttributes:p,maxVertexUniforms:m,maxVaryings:M,maxFragmentUniforms:v,vertexTextures:b,maxSamples:N}}function ev(i){const e=this;let t=null,n=0,s=!1,r=!1;const a=new cs,o=new at,l={value:null,needsUpdate:!1};this.uniform=l,this.numPlanes=0,this.numIntersection=0,this.init=function(u,d){const f=u.length!==0||d||n!==0||s;return s=d,n=u.length,f},this.beginShadows=function(){r=!0,h(null)},this.endShadows=function(){r=!1},this.setGlobalState=function(u,d){t=h(u,d,0)},this.setState=function(u,d,f){const g=u.clippingPlanes,_=u.clipIntersection,p=u.clipShadows,m=i.get(u);if(!s||g===null||g.length===0||r&&!p)r?h(null):c();else{const M=r?0:n,v=M*4;let b=m.clippingState||null;l.value=b,b=h(g,d,v,f);for(let N=0;N!==v;++N)b[N]=t[N];m.clippingState=b,this.numIntersection=_?this.numPlanes:0,this.numPlanes+=M}};function c(){l.value!==t&&(l.value=t,l.needsUpdate=n>0),e.numPlanes=n,e.numIntersection=0}function h(u,d,f,g){const _=u!==null?u.length:0;let p=null;if(_!==0){if(p=l.value,g!==!0||p===null){const m=f+_*4,M=d.matrixWorldInverse;o.getNormalMatrix(M),(p===null||p.length<m)&&(p=new Float32Array(m));for(let v=0,b=f;v!==_;++v,b+=4)a.copy(u[v]).applyMatrix4(M,o),a.normal.toArray(p,b),p[b+3]=a.constant}l.value=p,l.needsUpdate=!0}return e.numPlanes=_,e.numIntersection=0,p}}function tv(i){let e=new WeakMap;function t(a,o){return o===Cc?a.mapping=Wr:o===Pc&&(a.mapping=Xr),a}function n(a){if(a&&a.isTexture){const o=a.mapping;if(o===Cc||o===Pc)if(e.has(a)){const l=e.get(a).texture;return t(l,a.mapping)}else{const l=a.image;if(l&&l.height>0){const c=new d_(l.height);return c.fromEquirectangularTexture(i,a),e.set(a,c),a.addEventListener("dispose",s),t(c.texture,a.mapping)}else return null}}return a}function s(a){const o=a.target;o.removeEventListener("dispose",s);const l=e.get(o);l!==void 0&&(e.delete(o),l.dispose())}function r(){e=new WeakMap}return{get:n,dispose:r}}class Vr extends sp{constructor(e=-1,t=1,n=1,s=-1,r=.1,a=2e3){super(),this.isOrthographicCamera=!0,this.type="OrthographicCamera",this.zoom=1,this.view=null,this.left=e,this.right=t,this.top=n,this.bottom=s,this.near=r,this.far=a,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.left=e.left,this.right=e.right,this.top=e.top,this.bottom=e.bottom,this.near=e.near,this.far=e.far,this.zoom=e.zoom,this.view=e.view===null?null:Object.assign({},e.view),this}setViewOffset(e,t,n,s,r,a){this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=n,this.view.offsetY=s,this.view.width=r,this.view.height=a,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const e=(this.right-this.left)/(2*this.zoom),t=(this.top-this.bottom)/(2*this.zoom),n=(this.right+this.left)/2,s=(this.top+this.bottom)/2;let r=n-e,a=n+e,o=s+t,l=s-t;if(this.view!==null&&this.view.enabled){const c=(this.right-this.left)/this.view.fullWidth/this.zoom,h=(this.top-this.bottom)/this.view.fullHeight/this.zoom;r+=c*this.view.offsetX,a=r+c*this.view.width,o-=h*this.view.offsetY,l=o-h*this.view.height}this.projectionMatrix.makeOrthographic(r,a,o,l,this.near,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){const t=super.toJSON(e);return t.object.zoom=this.zoom,t.object.left=this.left,t.object.right=this.right,t.object.top=this.top,t.object.bottom=this.bottom,t.object.near=this.near,t.object.far=this.far,this.view!==null&&(t.object.view=Object.assign({},this.view)),t}}const Fr=4,Zu=[.125,.215,.35,.446,.526,.582],Bs=20,rc=new Vr,Ju=new nt;let ac=null,oc=0,lc=0,cc=!1;const Us=(1+Math.sqrt(5))/2,Tr=1/Us,Qu=[new V(-Us,Tr,0),new V(Us,Tr,0),new V(-Tr,0,Us),new V(Tr,0,Us),new V(0,Us,-Tr),new V(0,Us,Tr),new V(-1,1,-1),new V(1,1,-1),new V(-1,1,1),new V(1,1,1)];class ed{constructor(e){this._renderer=e,this._pingPongRenderTarget=null,this._lodMax=0,this._cubeSize=0,this._lodPlanes=[],this._sizeLods=[],this._sigmas=[],this._blurMaterial=null,this._cubemapMaterial=null,this._equirectMaterial=null,this._compileMaterial(this._blurMaterial)}fromScene(e,t=0,n=.1,s=100){ac=this._renderer.getRenderTarget(),oc=this._renderer.getActiveCubeFace(),lc=this._renderer.getActiveMipmapLevel(),cc=this._renderer.xr.enabled,this._renderer.xr.enabled=!1,this._setSize(256);const r=this._allocateTargets();return r.depthBuffer=!0,this._sceneToCubeUV(e,n,s,r),t>0&&this._blur(r,0,0,t),this._applyPMREM(r),this._cleanup(r),r}fromEquirectangular(e,t=null){return this._fromTexture(e,t)}fromCubemap(e,t=null){return this._fromTexture(e,t)}compileCubemapShader(){this._cubemapMaterial===null&&(this._cubemapMaterial=id(),this._compileMaterial(this._cubemapMaterial))}compileEquirectangularShader(){this._equirectMaterial===null&&(this._equirectMaterial=nd(),this._compileMaterial(this._equirectMaterial))}dispose(){this._dispose(),this._cubemapMaterial!==null&&this._cubemapMaterial.dispose(),this._equirectMaterial!==null&&this._equirectMaterial.dispose()}_setSize(e){this._lodMax=Math.floor(Math.log2(e)),this._cubeSize=Math.pow(2,this._lodMax)}_dispose(){this._blurMaterial!==null&&this._blurMaterial.dispose(),this._pingPongRenderTarget!==null&&this._pingPongRenderTarget.dispose();for(let e=0;e<this._lodPlanes.length;e++)this._lodPlanes[e].dispose()}_cleanup(e){this._renderer.setRenderTarget(ac,oc,lc),this._renderer.xr.enabled=cc,e.scissorTest=!1,wo(e,0,0,e.width,e.height)}_fromTexture(e,t){e.mapping===Wr||e.mapping===Xr?this._setSize(e.image.length===0?16:e.image[0].width||e.image[0].image.width):this._setSize(e.image.width/4),ac=this._renderer.getRenderTarget(),oc=this._renderer.getActiveCubeFace(),lc=this._renderer.getActiveMipmapLevel(),cc=this._renderer.xr.enabled,this._renderer.xr.enabled=!1;const n=t||this._allocateTargets();return this._textureToCubeUV(e,n),this._applyPMREM(n),this._cleanup(n),n}_allocateTargets(){const e=3*Math.max(this._cubeSize,112),t=4*this._cubeSize,n={magFilter:hi,minFilter:hi,generateMipmaps:!1,type:Ga,format:fi,colorSpace:Ms,depthBuffer:!1},s=td(e,t,n);if(this._pingPongRenderTarget===null||this._pingPongRenderTarget.width!==e||this._pingPongRenderTarget.height!==t){this._pingPongRenderTarget!==null&&this._dispose(),this._pingPongRenderTarget=td(e,t,n);const{_lodMax:r}=this;({sizeLods:this._sizeLods,lodPlanes:this._lodPlanes,sigmas:this._sigmas}=nv(r)),this._blurMaterial=iv(r,e,t)}return s}_compileMaterial(e){const t=new Qt(this._lodPlanes[0],e);this._renderer.compile(t,rc)}_sceneToCubeUV(e,t,n,s){const o=new bn(90,1,t,n),l=[1,-1,1,1,1,1],c=[1,1,1,-1,-1,-1],h=this._renderer,u=h.autoClear,d=h.toneMapping;h.getClearColor(Ju),h.toneMapping=fs,h.autoClear=!1;const f=new ps({name:"PMREM.Background",side:Nn,depthWrite:!1,depthTest:!1}),g=new Qt(new Ei,f);let _=!1;const p=e.background;p?p.isColor&&(f.color.copy(p),e.background=null,_=!0):(f.color.copy(Ju),_=!0);for(let m=0;m<6;m++){const M=m%3;M===0?(o.up.set(0,l[m],0),o.lookAt(c[m],0,0)):M===1?(o.up.set(0,0,l[m]),o.lookAt(0,c[m],0)):(o.up.set(0,l[m],0),o.lookAt(0,0,c[m]));const v=this._cubeSize;wo(s,M*v,m>2?v:0,v,v),h.setRenderTarget(s),_&&h.render(g,o),h.render(e,o)}g.geometry.dispose(),g.material.dispose(),h.toneMapping=d,h.autoClear=u,e.background=p}_textureToCubeUV(e,t){const n=this._renderer,s=e.mapping===Wr||e.mapping===Xr;s?(this._cubemapMaterial===null&&(this._cubemapMaterial=id()),this._cubemapMaterial.uniforms.flipEnvMap.value=e.isRenderTargetTexture===!1?-1:1):this._equirectMaterial===null&&(this._equirectMaterial=nd());const r=s?this._cubemapMaterial:this._equirectMaterial,a=new Qt(this._lodPlanes[0],r),o=r.uniforms;o.envMap.value=e;const l=this._cubeSize;wo(t,0,0,3*l,2*l),n.setRenderTarget(t),n.render(a,rc)}_applyPMREM(e){const t=this._renderer,n=t.autoClear;t.autoClear=!1;const s=this._lodPlanes.length;for(let r=1;r<s;r++){const a=Math.sqrt(this._sigmas[r]*this._sigmas[r]-this._sigmas[r-1]*this._sigmas[r-1]),o=Qu[(s-r-1)%Qu.length];this._blur(e,r-1,r,a,o)}t.autoClear=n}_blur(e,t,n,s,r){const a=this._pingPongRenderTarget;this._halfBlur(e,a,t,n,s,"latitudinal",r),this._halfBlur(a,e,n,n,s,"longitudinal",r)}_halfBlur(e,t,n,s,r,a,o){const l=this._renderer,c=this._blurMaterial;a!=="latitudinal"&&a!=="longitudinal"&&console.error("blur direction must be either latitudinal or longitudinal!");const h=3,u=new Qt(this._lodPlanes[s],c),d=c.uniforms,f=this._sizeLods[n]-1,g=isFinite(r)?Math.PI/(2*f):2*Math.PI/(2*Bs-1),_=r/g,p=isFinite(r)?1+Math.floor(h*_):Bs;p>Bs&&console.warn(`sigmaRadians, ${r}, is too large and will clip, as it requested ${p} samples when the maximum is set to ${Bs}`);const m=[];let M=0;for(let R=0;R<Bs;++R){const F=R/_,w=Math.exp(-F*F/2);m.push(w),R===0?M+=w:R<p&&(M+=2*w)}for(let R=0;R<m.length;R++)m[R]=m[R]/M;d.envMap.value=e.texture,d.samples.value=p,d.weights.value=m,d.latitudinal.value=a==="latitudinal",o&&(d.poleAxis.value=o);const{_lodMax:v}=this;d.dTheta.value=g,d.mipInt.value=v-n;const b=this._sizeLods[s],N=3*b*(s>v-Fr?s-v+Fr:0),A=4*(this._cubeSize-b);wo(t,N,A,3*b,2*b),l.setRenderTarget(t),l.render(u,rc)}}function nv(i){const e=[],t=[],n=[];let s=i;const r=i-Fr+1+Zu.length;for(let a=0;a<r;a++){const o=Math.pow(2,s);t.push(o);let l=1/o;a>i-Fr?l=Zu[a-i+Fr-1]:a===0&&(l=0),n.push(l);const c=1/(o-2),h=-c,u=1+c,d=[h,h,u,h,u,u,h,h,u,u,h,u],f=6,g=6,_=3,p=2,m=1,M=new Float32Array(_*g*f),v=new Float32Array(p*g*f),b=new Float32Array(m*g*f);for(let A=0;A<f;A++){const R=A%3*2/3-1,F=A>2?0:-1,w=[R,F,0,R+2/3,F,0,R+2/3,F+1,0,R,F,0,R+2/3,F+1,0,R,F+1,0];M.set(w,_*g*A),v.set(d,p*g*A);const y=[A,A,A,A,A,A];b.set(y,m*g*A)}const N=new Gt;N.setAttribute("position",new pi(M,_)),N.setAttribute("uv",new pi(v,p)),N.setAttribute("faceIndex",new pi(b,m)),e.push(N),s>Fr&&s--}return{lodPlanes:e,sizeLods:t,sigmas:n}}function td(i,e,t){const n=new $s(i,e,t);return n.texture.mapping=ll,n.texture.name="PMREM.cubeUv",n.scissorTest=!0,n}function wo(i,e,t,n,s){i.viewport.set(e,t,n,s),i.scissor.set(e,t,n,s)}function iv(i,e,t){const n=new Float32Array(Bs),s=new V(0,1,0);return new _s({name:"SphericalGaussianBlur",defines:{n:Bs,CUBEUV_TEXEL_WIDTH:1/e,CUBEUV_TEXEL_HEIGHT:1/t,CUBEUV_MAX_MIP:`${i}.0`},uniforms:{envMap:{value:null},samples:{value:1},weights:{value:n},latitudinal:{value:!1},dTheta:{value:0},mipInt:{value:0},poleAxis:{value:s}},vertexShader:Dh(),fragmentShader:`

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
		`,blending:ds,depthTest:!1,depthWrite:!1})}function nd(){return new _s({name:"EquirectangularToCubeUV",uniforms:{envMap:{value:null}},vertexShader:Dh(),fragmentShader:`

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
		`,blending:ds,depthTest:!1,depthWrite:!1})}function id(){return new _s({name:"CubemapToCubeUV",uniforms:{envMap:{value:null},flipEnvMap:{value:-1}},vertexShader:Dh(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			uniform float flipEnvMap;

			varying vec3 vOutputDirection;

			uniform samplerCube envMap;

			void main() {

				gl_FragColor = textureCube( envMap, vec3( flipEnvMap * vOutputDirection.x, vOutputDirection.yz ) );

			}
		`,blending:ds,depthTest:!1,depthWrite:!1})}function Dh(){return`

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
	`}function sv(i){let e=new WeakMap,t=null;function n(o){if(o&&o.isTexture){const l=o.mapping,c=l===Cc||l===Pc,h=l===Wr||l===Xr;if(c||h){let u=e.get(o);const d=u!==void 0?u.texture.pmremVersion:0;if(o.isRenderTargetTexture&&o.pmremVersion!==d)return t===null&&(t=new ed(i)),u=c?t.fromEquirectangular(o,u):t.fromCubemap(o,u),u.texture.pmremVersion=o.pmremVersion,e.set(o,u),u.texture;if(u!==void 0)return u.texture;{const f=o.image;return c&&f&&f.height>0||h&&f&&s(f)?(t===null&&(t=new ed(i)),u=c?t.fromEquirectangular(o):t.fromCubemap(o),u.texture.pmremVersion=o.pmremVersion,e.set(o,u),o.addEventListener("dispose",r),u.texture):null}}}return o}function s(o){let l=0;const c=6;for(let h=0;h<c;h++)o[h]!==void 0&&l++;return l===c}function r(o){const l=o.target;l.removeEventListener("dispose",r);const c=e.get(l);c!==void 0&&(e.delete(l),c.dispose())}function a(){e=new WeakMap,t!==null&&(t.dispose(),t=null)}return{get:n,dispose:a}}function rv(i){const e={};function t(n){if(e[n]!==void 0)return e[n];let s;switch(n){case"WEBGL_depth_texture":s=i.getExtension("WEBGL_depth_texture")||i.getExtension("MOZ_WEBGL_depth_texture")||i.getExtension("WEBKIT_WEBGL_depth_texture");break;case"EXT_texture_filter_anisotropic":s=i.getExtension("EXT_texture_filter_anisotropic")||i.getExtension("MOZ_EXT_texture_filter_anisotropic")||i.getExtension("WEBKIT_EXT_texture_filter_anisotropic");break;case"WEBGL_compressed_texture_s3tc":s=i.getExtension("WEBGL_compressed_texture_s3tc")||i.getExtension("MOZ_WEBGL_compressed_texture_s3tc")||i.getExtension("WEBKIT_WEBGL_compressed_texture_s3tc");break;case"WEBGL_compressed_texture_pvrtc":s=i.getExtension("WEBGL_compressed_texture_pvrtc")||i.getExtension("WEBKIT_WEBGL_compressed_texture_pvrtc");break;default:s=i.getExtension(n)}return e[n]=s,s}return{has:function(n){return t(n)!==null},init:function(){t("EXT_color_buffer_float"),t("WEBGL_clip_cull_distance"),t("OES_texture_float_linear"),t("EXT_color_buffer_half_float"),t("WEBGL_multisampled_render_to_texture"),t("WEBGL_render_shared_exponent")},get:function(n){const s=t(n);return s===null&&kr("THREE.WebGLRenderer: "+n+" extension not supported."),s}}}function av(i,e,t,n){const s={},r=new WeakMap;function a(u){const d=u.target;d.index!==null&&e.remove(d.index);for(const g in d.attributes)e.remove(d.attributes[g]);for(const g in d.morphAttributes){const _=d.morphAttributes[g];for(let p=0,m=_.length;p<m;p++)e.remove(_[p])}d.removeEventListener("dispose",a),delete s[d.id];const f=r.get(d);f&&(e.remove(f),r.delete(d)),n.releaseStatesOfGeometry(d),d.isInstancedBufferGeometry===!0&&delete d._maxInstanceCount,t.memory.geometries--}function o(u,d){return s[d.id]===!0||(d.addEventListener("dispose",a),s[d.id]=!0,t.memory.geometries++),d}function l(u){const d=u.attributes;for(const g in d)e.update(d[g],i.ARRAY_BUFFER);const f=u.morphAttributes;for(const g in f){const _=f[g];for(let p=0,m=_.length;p<m;p++)e.update(_[p],i.ARRAY_BUFFER)}}function c(u){const d=[],f=u.index,g=u.attributes.position;let _=0;if(f!==null){const M=f.array;_=f.version;for(let v=0,b=M.length;v<b;v+=3){const N=M[v+0],A=M[v+1],R=M[v+2];d.push(N,A,A,R,R,N)}}else if(g!==void 0){const M=g.array;_=g.version;for(let v=0,b=M.length/3-1;v<b;v+=3){const N=v+0,A=v+1,R=v+2;d.push(N,A,A,R,R,N)}}else return;const p=new(Zf(d)?np:tp)(d,1);p.version=_;const m=r.get(u);m&&e.remove(m),r.set(u,p)}function h(u){const d=r.get(u);if(d){const f=u.index;f!==null&&d.version<f.version&&c(u)}else c(u);return r.get(u)}return{get:o,update:l,getWireframeAttribute:h}}function ov(i,e,t){let n;function s(d){n=d}let r,a;function o(d){r=d.type,a=d.bytesPerElement}function l(d,f){i.drawElements(n,f,r,d*a),t.update(f,n,1)}function c(d,f,g){g!==0&&(i.drawElementsInstanced(n,f,r,d*a,g),t.update(f,n,g))}function h(d,f,g){if(g===0)return;e.get("WEBGL_multi_draw").multiDrawElementsWEBGL(n,f,0,r,d,0,g);let p=0;for(let m=0;m<g;m++)p+=f[m];t.update(p,n,1)}function u(d,f,g,_){if(g===0)return;const p=e.get("WEBGL_multi_draw");if(p===null)for(let m=0;m<d.length;m++)c(d[m]/a,f[m],_[m]);else{p.multiDrawElementsInstancedWEBGL(n,f,0,r,d,0,_,0,g);let m=0;for(let M=0;M<g;M++)m+=f[M];for(let M=0;M<_.length;M++)t.update(m,n,_[M])}}this.setMode=s,this.setIndex=o,this.render=l,this.renderInstances=c,this.renderMultiDraw=h,this.renderMultiDrawInstances=u}function lv(i){const e={geometries:0,textures:0},t={frame:0,calls:0,triangles:0,points:0,lines:0};function n(r,a,o){switch(t.calls++,a){case i.TRIANGLES:t.triangles+=o*(r/3);break;case i.LINES:t.lines+=o*(r/2);break;case i.LINE_STRIP:t.lines+=o*(r-1);break;case i.LINE_LOOP:t.lines+=o*r;break;case i.POINTS:t.points+=o*r;break;default:console.error("THREE.WebGLInfo: Unknown draw mode:",a);break}}function s(){t.calls=0,t.triangles=0,t.points=0,t.lines=0}return{memory:e,render:t,programs:null,autoReset:!0,reset:s,update:n}}function cv(i,e,t){const n=new WeakMap,s=new sn;function r(a,o,l){const c=a.morphTargetInfluences,h=o.morphAttributes.position||o.morphAttributes.normal||o.morphAttributes.color,u=h!==void 0?h.length:0;let d=n.get(o);if(d===void 0||d.count!==u){let y=function(){F.dispose(),n.delete(o),o.removeEventListener("dispose",y)};var f=y;d!==void 0&&d.texture.dispose();const g=o.morphAttributes.position!==void 0,_=o.morphAttributes.normal!==void 0,p=o.morphAttributes.color!==void 0,m=o.morphAttributes.position||[],M=o.morphAttributes.normal||[],v=o.morphAttributes.color||[];let b=0;g===!0&&(b=1),_===!0&&(b=2),p===!0&&(b=3);let N=o.attributes.position.count*b,A=1;N>e.maxTextureSize&&(A=Math.ceil(N/e.maxTextureSize),N=e.maxTextureSize);const R=new Float32Array(N*A*4*u),F=new Qf(R,N,A,u);F.type=Gi,F.needsUpdate=!0;const w=b*4;for(let P=0;P<u;P++){const K=m[P],H=M[P],Z=v[P],q=N*A*4*P;for(let ee=0;ee<K.count;ee++){const Y=ee*w;g===!0&&(s.fromBufferAttribute(K,ee),R[q+Y+0]=s.x,R[q+Y+1]=s.y,R[q+Y+2]=s.z,R[q+Y+3]=0),_===!0&&(s.fromBufferAttribute(H,ee),R[q+Y+4]=s.x,R[q+Y+5]=s.y,R[q+Y+6]=s.z,R[q+Y+7]=0),p===!0&&(s.fromBufferAttribute(Z,ee),R[q+Y+8]=s.x,R[q+Y+9]=s.y,R[q+Y+10]=s.z,R[q+Y+11]=Z.itemSize===4?s.w:1)}}d={count:u,texture:F,size:new $e(N,A)},n.set(o,d),o.addEventListener("dispose",y)}if(a.isInstancedMesh===!0&&a.morphTexture!==null)l.getUniforms().setValue(i,"morphTexture",a.morphTexture,t);else{let g=0;for(let p=0;p<c.length;p++)g+=c[p];const _=o.morphTargetsRelative?1:1-g;l.getUniforms().setValue(i,"morphTargetBaseInfluence",_),l.getUniforms().setValue(i,"morphTargetInfluences",c)}l.getUniforms().setValue(i,"morphTargetsTexture",d.texture,t),l.getUniforms().setValue(i,"morphTargetsTextureSize",d.size)}return{update:r}}function hv(i,e,t,n){let s=new WeakMap;function r(l){const c=n.render.frame,h=l.geometry,u=e.get(l,h);if(s.get(u)!==c&&(e.update(u),s.set(u,c)),l.isInstancedMesh&&(l.hasEventListener("dispose",o)===!1&&l.addEventListener("dispose",o),s.get(l)!==c&&(t.update(l.instanceMatrix,i.ARRAY_BUFFER),l.instanceColor!==null&&t.update(l.instanceColor,i.ARRAY_BUFFER),s.set(l,c))),l.isSkinnedMesh){const d=l.skeleton;s.get(d)!==c&&(d.update(),s.set(d,c))}return u}function a(){s=new WeakMap}function o(l){const c=l.target;c.removeEventListener("dispose",o),t.remove(c.instanceMatrix),c.instanceColor!==null&&t.remove(c.instanceColor)}return{update:r,dispose:a}}class op extends Ln{constructor(e,t,n,s,r,a,o,l,c,h=Br){if(h!==Br&&h!==$r)throw new Error("DepthTexture format must be either THREE.DepthFormat or THREE.DepthStencilFormat");n===void 0&&h===Br&&(n=qs),n===void 0&&h===$r&&(n=qr),super(null,s,r,a,o,l,h,n,c),this.isDepthTexture=!0,this.image={width:e,height:t},this.magFilter=o!==void 0?o:ei,this.minFilter=l!==void 0?l:ei,this.flipY=!1,this.generateMipmaps=!1,this.compareFunction=null}copy(e){return super.copy(e),this.compareFunction=e.compareFunction,this}toJSON(e){const t=super.toJSON(e);return this.compareFunction!==null&&(t.compareFunction=this.compareFunction),t}}const lp=new Ln,sd=new op(1,1),cp=new Qf,hp=new Kg,up=new rp,rd=[],ad=[],od=new Float32Array(16),ld=new Float32Array(9),cd=new Float32Array(4);function na(i,e,t){const n=i[0];if(n<=0||n>0)return i;const s=e*t;let r=rd[s];if(r===void 0&&(r=new Float32Array(s),rd[s]=r),e!==0){n.toArray(r,0);for(let a=1,o=0;a!==e;++a)o+=t,i[a].toArray(r,o)}return r}function rn(i,e){if(i.length!==e.length)return!1;for(let t=0,n=i.length;t<n;t++)if(i[t]!==e[t])return!1;return!0}function an(i,e){for(let t=0,n=e.length;t<n;t++)i[t]=e[t]}function hl(i,e){let t=ad[e];t===void 0&&(t=new Int32Array(e),ad[e]=t);for(let n=0;n!==e;++n)t[n]=i.allocateTextureUnit();return t}function uv(i,e){const t=this.cache;t[0]!==e&&(i.uniform1f(this.addr,e),t[0]=e)}function dv(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(i.uniform2f(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(rn(t,e))return;i.uniform2fv(this.addr,e),an(t,e)}}function fv(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(i.uniform3f(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else if(e.r!==void 0)(t[0]!==e.r||t[1]!==e.g||t[2]!==e.b)&&(i.uniform3f(this.addr,e.r,e.g,e.b),t[0]=e.r,t[1]=e.g,t[2]=e.b);else{if(rn(t,e))return;i.uniform3fv(this.addr,e),an(t,e)}}function pv(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(i.uniform4f(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(rn(t,e))return;i.uniform4fv(this.addr,e),an(t,e)}}function mv(i,e){const t=this.cache,n=e.elements;if(n===void 0){if(rn(t,e))return;i.uniformMatrix2fv(this.addr,!1,e),an(t,e)}else{if(rn(t,n))return;cd.set(n),i.uniformMatrix2fv(this.addr,!1,cd),an(t,n)}}function gv(i,e){const t=this.cache,n=e.elements;if(n===void 0){if(rn(t,e))return;i.uniformMatrix3fv(this.addr,!1,e),an(t,e)}else{if(rn(t,n))return;ld.set(n),i.uniformMatrix3fv(this.addr,!1,ld),an(t,n)}}function _v(i,e){const t=this.cache,n=e.elements;if(n===void 0){if(rn(t,e))return;i.uniformMatrix4fv(this.addr,!1,e),an(t,e)}else{if(rn(t,n))return;od.set(n),i.uniformMatrix4fv(this.addr,!1,od),an(t,n)}}function xv(i,e){const t=this.cache;t[0]!==e&&(i.uniform1i(this.addr,e),t[0]=e)}function vv(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(i.uniform2i(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(rn(t,e))return;i.uniform2iv(this.addr,e),an(t,e)}}function yv(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(i.uniform3i(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(rn(t,e))return;i.uniform3iv(this.addr,e),an(t,e)}}function Mv(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(i.uniform4i(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(rn(t,e))return;i.uniform4iv(this.addr,e),an(t,e)}}function Sv(i,e){const t=this.cache;t[0]!==e&&(i.uniform1ui(this.addr,e),t[0]=e)}function bv(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(i.uniform2ui(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(rn(t,e))return;i.uniform2uiv(this.addr,e),an(t,e)}}function wv(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(i.uniform3ui(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(rn(t,e))return;i.uniform3uiv(this.addr,e),an(t,e)}}function Ev(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(i.uniform4ui(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(rn(t,e))return;i.uniform4uiv(this.addr,e),an(t,e)}}function Tv(i,e,t){const n=this.cache,s=t.allocateTextureUnit();n[0]!==s&&(i.uniform1i(this.addr,s),n[0]=s);let r;this.type===i.SAMPLER_2D_SHADOW?(sd.compareFunction=Kf,r=sd):r=lp,t.setTexture2D(e||r,s)}function Av(i,e,t){const n=this.cache,s=t.allocateTextureUnit();n[0]!==s&&(i.uniform1i(this.addr,s),n[0]=s),t.setTexture3D(e||hp,s)}function Rv(i,e,t){const n=this.cache,s=t.allocateTextureUnit();n[0]!==s&&(i.uniform1i(this.addr,s),n[0]=s),t.setTextureCube(e||up,s)}function Cv(i,e,t){const n=this.cache,s=t.allocateTextureUnit();n[0]!==s&&(i.uniform1i(this.addr,s),n[0]=s),t.setTexture2DArray(e||cp,s)}function Pv(i){switch(i){case 5126:return uv;case 35664:return dv;case 35665:return fv;case 35666:return pv;case 35674:return mv;case 35675:return gv;case 35676:return _v;case 5124:case 35670:return xv;case 35667:case 35671:return vv;case 35668:case 35672:return yv;case 35669:case 35673:return Mv;case 5125:return Sv;case 36294:return bv;case 36295:return wv;case 36296:return Ev;case 35678:case 36198:case 36298:case 36306:case 35682:return Tv;case 35679:case 36299:case 36307:return Av;case 35680:case 36300:case 36308:case 36293:return Rv;case 36289:case 36303:case 36311:case 36292:return Cv}}function Lv(i,e){i.uniform1fv(this.addr,e)}function Dv(i,e){const t=na(e,this.size,2);i.uniform2fv(this.addr,t)}function Iv(i,e){const t=na(e,this.size,3);i.uniform3fv(this.addr,t)}function Uv(i,e){const t=na(e,this.size,4);i.uniform4fv(this.addr,t)}function Nv(i,e){const t=na(e,this.size,4);i.uniformMatrix2fv(this.addr,!1,t)}function Fv(i,e){const t=na(e,this.size,9);i.uniformMatrix3fv(this.addr,!1,t)}function Ov(i,e){const t=na(e,this.size,16);i.uniformMatrix4fv(this.addr,!1,t)}function Bv(i,e){i.uniform1iv(this.addr,e)}function zv(i,e){i.uniform2iv(this.addr,e)}function kv(i,e){i.uniform3iv(this.addr,e)}function Hv(i,e){i.uniform4iv(this.addr,e)}function Vv(i,e){i.uniform1uiv(this.addr,e)}function Gv(i,e){i.uniform2uiv(this.addr,e)}function Wv(i,e){i.uniform3uiv(this.addr,e)}function Xv(i,e){i.uniform4uiv(this.addr,e)}function qv(i,e,t){const n=this.cache,s=e.length,r=hl(t,s);rn(n,r)||(i.uniform1iv(this.addr,r),an(n,r));for(let a=0;a!==s;++a)t.setTexture2D(e[a]||lp,r[a])}function $v(i,e,t){const n=this.cache,s=e.length,r=hl(t,s);rn(n,r)||(i.uniform1iv(this.addr,r),an(n,r));for(let a=0;a!==s;++a)t.setTexture3D(e[a]||hp,r[a])}function Yv(i,e,t){const n=this.cache,s=e.length,r=hl(t,s);rn(n,r)||(i.uniform1iv(this.addr,r),an(n,r));for(let a=0;a!==s;++a)t.setTextureCube(e[a]||up,r[a])}function jv(i,e,t){const n=this.cache,s=e.length,r=hl(t,s);rn(n,r)||(i.uniform1iv(this.addr,r),an(n,r));for(let a=0;a!==s;++a)t.setTexture2DArray(e[a]||cp,r[a])}function Kv(i){switch(i){case 5126:return Lv;case 35664:return Dv;case 35665:return Iv;case 35666:return Uv;case 35674:return Nv;case 35675:return Fv;case 35676:return Ov;case 5124:case 35670:return Bv;case 35667:case 35671:return zv;case 35668:case 35672:return kv;case 35669:case 35673:return Hv;case 5125:return Vv;case 36294:return Gv;case 36295:return Wv;case 36296:return Xv;case 35678:case 36198:case 36298:case 36306:case 35682:return qv;case 35679:case 36299:case 36307:return $v;case 35680:case 36300:case 36308:case 36293:return Yv;case 36289:case 36303:case 36311:case 36292:return jv}}class Zv{constructor(e,t,n){this.id=e,this.addr=n,this.cache=[],this.type=t.type,this.setValue=Pv(t.type)}}class Jv{constructor(e,t,n){this.id=e,this.addr=n,this.cache=[],this.type=t.type,this.size=t.size,this.setValue=Kv(t.type)}}class Qv{constructor(e){this.id=e,this.seq=[],this.map={}}setValue(e,t,n){const s=this.seq;for(let r=0,a=s.length;r!==a;++r){const o=s[r];o.setValue(e,t[o.id],n)}}}const hc=/(\w+)(\])?(\[|\.)?/g;function hd(i,e){i.seq.push(e),i.map[e.id]=e}function ey(i,e,t){const n=i.name,s=n.length;for(hc.lastIndex=0;;){const r=hc.exec(n),a=hc.lastIndex;let o=r[1];const l=r[2]==="]",c=r[3];if(l&&(o=o|0),c===void 0||c==="["&&a+2===s){hd(t,c===void 0?new Zv(o,i,e):new Jv(o,i,e));break}else{let u=t.map[o];u===void 0&&(u=new Qv(o),hd(t,u)),t=u}}}class Xo{constructor(e,t){this.seq=[],this.map={};const n=e.getProgramParameter(t,e.ACTIVE_UNIFORMS);for(let s=0;s<n;++s){const r=e.getActiveUniform(t,s),a=e.getUniformLocation(t,r.name);ey(r,a,this)}}setValue(e,t,n,s){const r=this.map[t];r!==void 0&&r.setValue(e,n,s)}setOptional(e,t,n){const s=t[n];s!==void 0&&this.setValue(e,n,s)}static upload(e,t,n,s){for(let r=0,a=t.length;r!==a;++r){const o=t[r],l=n[o.id];l.needsUpdate!==!1&&o.setValue(e,l.value,s)}}static seqWithValue(e,t){const n=[];for(let s=0,r=e.length;s!==r;++s){const a=e[s];a.id in t&&n.push(a)}return n}}function ud(i,e,t){const n=i.createShader(e);return i.shaderSource(n,t),i.compileShader(n),n}const ty=37297;let ny=0;function iy(i,e){const t=i.split(`
`),n=[],s=Math.max(e-6,0),r=Math.min(e+6,t.length);for(let a=s;a<r;a++){const o=a+1;n.push(`${o===e?">":" "} ${o}: ${t[a]}`)}return n.join(`
`)}function sy(i){const e=bt.getPrimaries(bt.workingColorSpace),t=bt.getPrimaries(i);let n;switch(e===t?n="":e===Zo&&t===Ko?n="LinearDisplayP3ToLinearSRGB":e===Ko&&t===Zo&&(n="LinearSRGBToLinearDisplayP3"),i){case Ms:case cl:return[n,"LinearTransferOETF"];case bi:case Rh:return[n,"sRGBTransferOETF"];default:return console.warn("THREE.WebGLProgram: Unsupported color space:",i),[n,"LinearTransferOETF"]}}function dd(i,e,t){const n=i.getShaderParameter(e,i.COMPILE_STATUS),s=i.getShaderInfoLog(e).trim();if(n&&s==="")return"";const r=/ERROR: 0:(\d+)/.exec(s);if(r){const a=parseInt(r[1]);return t.toUpperCase()+`

`+s+`

`+iy(i.getShaderSource(e),a)}else return s}function ry(i,e){const t=sy(e);return`vec4 ${i}( vec4 value ) { return ${t[0]}( ${t[1]}( value ) ); }`}function ay(i,e){let t;switch(e){case hg:t="Linear";break;case ug:t="Reinhard";break;case dg:t="Cineon";break;case Of:t="ACESFilmic";break;case pg:t="AgX";break;case mg:t="Neutral";break;case fg:t="Custom";break;default:console.warn("THREE.WebGLProgram: Unsupported toneMapping:",e),t="Linear"}return"vec3 "+i+"( vec3 color ) { return "+t+"ToneMapping( color ); }"}const Eo=new V;function oy(){bt.getLuminanceCoefficients(Eo);const i=Eo.x.toFixed(4),e=Eo.y.toFixed(4),t=Eo.z.toFixed(4);return["float luminance( const in vec3 rgb ) {",`	const vec3 weights = vec3( ${i}, ${e}, ${t} );`,"	return dot( weights, rgb );","}"].join(`
`)}function ly(i){return[i.extensionClipCullDistance?"#extension GL_ANGLE_clip_cull_distance : require":"",i.extensionMultiDraw?"#extension GL_ANGLE_multi_draw : require":""].filter(Ra).join(`
`)}function cy(i){const e=[];for(const t in i){const n=i[t];n!==!1&&e.push("#define "+t+" "+n)}return e.join(`
`)}function hy(i,e){const t={},n=i.getProgramParameter(e,i.ACTIVE_ATTRIBUTES);for(let s=0;s<n;s++){const r=i.getActiveAttrib(e,s),a=r.name;let o=1;r.type===i.FLOAT_MAT2&&(o=2),r.type===i.FLOAT_MAT3&&(o=3),r.type===i.FLOAT_MAT4&&(o=4),t[a]={type:r.type,location:i.getAttribLocation(e,a),locationSize:o}}return t}function Ra(i){return i!==""}function fd(i,e){const t=e.numSpotLightShadows+e.numSpotLightMaps-e.numSpotLightShadowsWithMaps;return i.replace(/NUM_DIR_LIGHTS/g,e.numDirLights).replace(/NUM_SPOT_LIGHTS/g,e.numSpotLights).replace(/NUM_SPOT_LIGHT_MAPS/g,e.numSpotLightMaps).replace(/NUM_SPOT_LIGHT_COORDS/g,t).replace(/NUM_RECT_AREA_LIGHTS/g,e.numRectAreaLights).replace(/NUM_POINT_LIGHTS/g,e.numPointLights).replace(/NUM_HEMI_LIGHTS/g,e.numHemiLights).replace(/NUM_DIR_LIGHT_SHADOWS/g,e.numDirLightShadows).replace(/NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS/g,e.numSpotLightShadowsWithMaps).replace(/NUM_SPOT_LIGHT_SHADOWS/g,e.numSpotLightShadows).replace(/NUM_POINT_LIGHT_SHADOWS/g,e.numPointLightShadows)}function pd(i,e){return i.replace(/NUM_CLIPPING_PLANES/g,e.numClippingPlanes).replace(/UNION_CLIPPING_PLANES/g,e.numClippingPlanes-e.numClipIntersection)}const uy=/^[ \t]*#include +<([\w\d./]+)>/gm;function oh(i){return i.replace(uy,fy)}const dy=new Map;function fy(i,e){let t=rt[e];if(t===void 0){const n=dy.get(e);if(n!==void 0)t=rt[n],console.warn('THREE.WebGLRenderer: Shader chunk "%s" has been deprecated. Use "%s" instead.',e,n);else throw new Error("Can not resolve #include <"+e+">")}return oh(t)}const py=/#pragma unroll_loop_start\s+for\s*\(\s*int\s+i\s*=\s*(\d+)\s*;\s*i\s*<\s*(\d+)\s*;\s*i\s*\+\+\s*\)\s*{([\s\S]+?)}\s+#pragma unroll_loop_end/g;function md(i){return i.replace(py,my)}function my(i,e,t,n){let s="";for(let r=parseInt(e);r<parseInt(t);r++)s+=n.replace(/\[\s*i\s*\]/g,"[ "+r+" ]").replace(/UNROLLED_LOOP_INDEX/g,r);return s}function gd(i){let e=`precision ${i.precision} float;
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
#define LOW_PRECISION`),e}function gy(i){let e="SHADOWMAP_TYPE_BASIC";return i.shadowMapType===Uf?e="SHADOWMAP_TYPE_PCF":i.shadowMapType===Nf?e="SHADOWMAP_TYPE_PCF_SOFT":i.shadowMapType===Hi&&(e="SHADOWMAP_TYPE_VSM"),e}function _y(i){let e="ENVMAP_TYPE_CUBE";if(i.envMap)switch(i.envMapMode){case Wr:case Xr:e="ENVMAP_TYPE_CUBE";break;case ll:e="ENVMAP_TYPE_CUBE_UV";break}return e}function xy(i){let e="ENVMAP_MODE_REFLECTION";if(i.envMap)switch(i.envMapMode){case Xr:e="ENVMAP_MODE_REFRACTION";break}return e}function vy(i){let e="ENVMAP_BLENDING_NONE";if(i.envMap)switch(i.combine){case Ff:e="ENVMAP_BLENDING_MULTIPLY";break;case lg:e="ENVMAP_BLENDING_MIX";break;case cg:e="ENVMAP_BLENDING_ADD";break}return e}function yy(i){const e=i.envMapCubeUVHeight;if(e===null)return null;const t=Math.log2(e)-2,n=1/e;return{texelWidth:1/(3*Math.max(Math.pow(2,t),7*16)),texelHeight:n,maxMip:t}}function My(i,e,t,n){const s=i.getContext(),r=t.defines;let a=t.vertexShader,o=t.fragmentShader;const l=gy(t),c=_y(t),h=xy(t),u=vy(t),d=yy(t),f=ly(t),g=cy(r),_=s.createProgram();let p,m,M=t.glslVersion?"#version "+t.glslVersion+`
`:"";t.isRawShaderMaterial?(p=["#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,g].filter(Ra).join(`
`),p.length>0&&(p+=`
`),m=["#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,g].filter(Ra).join(`
`),m.length>0&&(m+=`
`)):(p=[gd(t),"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,g,t.extensionClipCullDistance?"#define USE_CLIP_DISTANCE":"",t.batching?"#define USE_BATCHING":"",t.batchingColor?"#define USE_BATCHING_COLOR":"",t.instancing?"#define USE_INSTANCING":"",t.instancingColor?"#define USE_INSTANCING_COLOR":"",t.instancingMorph?"#define USE_INSTANCING_MORPH":"",t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.map?"#define USE_MAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+h:"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",t.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",t.displacementMap?"#define USE_DISPLACEMENTMAP":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.anisotropy?"#define USE_ANISOTROPY":"",t.anisotropyMap?"#define USE_ANISOTROPYMAP":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",t.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaHash?"#define USE_ALPHAHASH":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",t.mapUv?"#define MAP_UV "+t.mapUv:"",t.alphaMapUv?"#define ALPHAMAP_UV "+t.alphaMapUv:"",t.lightMapUv?"#define LIGHTMAP_UV "+t.lightMapUv:"",t.aoMapUv?"#define AOMAP_UV "+t.aoMapUv:"",t.emissiveMapUv?"#define EMISSIVEMAP_UV "+t.emissiveMapUv:"",t.bumpMapUv?"#define BUMPMAP_UV "+t.bumpMapUv:"",t.normalMapUv?"#define NORMALMAP_UV "+t.normalMapUv:"",t.displacementMapUv?"#define DISPLACEMENTMAP_UV "+t.displacementMapUv:"",t.metalnessMapUv?"#define METALNESSMAP_UV "+t.metalnessMapUv:"",t.roughnessMapUv?"#define ROUGHNESSMAP_UV "+t.roughnessMapUv:"",t.anisotropyMapUv?"#define ANISOTROPYMAP_UV "+t.anisotropyMapUv:"",t.clearcoatMapUv?"#define CLEARCOATMAP_UV "+t.clearcoatMapUv:"",t.clearcoatNormalMapUv?"#define CLEARCOAT_NORMALMAP_UV "+t.clearcoatNormalMapUv:"",t.clearcoatRoughnessMapUv?"#define CLEARCOAT_ROUGHNESSMAP_UV "+t.clearcoatRoughnessMapUv:"",t.iridescenceMapUv?"#define IRIDESCENCEMAP_UV "+t.iridescenceMapUv:"",t.iridescenceThicknessMapUv?"#define IRIDESCENCE_THICKNESSMAP_UV "+t.iridescenceThicknessMapUv:"",t.sheenColorMapUv?"#define SHEEN_COLORMAP_UV "+t.sheenColorMapUv:"",t.sheenRoughnessMapUv?"#define SHEEN_ROUGHNESSMAP_UV "+t.sheenRoughnessMapUv:"",t.specularMapUv?"#define SPECULARMAP_UV "+t.specularMapUv:"",t.specularColorMapUv?"#define SPECULAR_COLORMAP_UV "+t.specularColorMapUv:"",t.specularIntensityMapUv?"#define SPECULAR_INTENSITYMAP_UV "+t.specularIntensityMapUv:"",t.transmissionMapUv?"#define TRANSMISSIONMAP_UV "+t.transmissionMapUv:"",t.thicknessMapUv?"#define THICKNESSMAP_UV "+t.thicknessMapUv:"",t.vertexTangents&&t.flatShading===!1?"#define USE_TANGENT":"",t.vertexColors?"#define USE_COLOR":"",t.vertexAlphas?"#define USE_COLOR_ALPHA":"",t.vertexUv1s?"#define USE_UV1":"",t.vertexUv2s?"#define USE_UV2":"",t.vertexUv3s?"#define USE_UV3":"",t.pointsUvs?"#define USE_POINTS_UV":"",t.flatShading?"#define FLAT_SHADED":"",t.skinning?"#define USE_SKINNING":"",t.morphTargets?"#define USE_MORPHTARGETS":"",t.morphNormals&&t.flatShading===!1?"#define USE_MORPHNORMALS":"",t.morphColors?"#define USE_MORPHCOLORS":"",t.morphTargetsCount>0?"#define MORPHTARGETS_TEXTURE_STRIDE "+t.morphTextureStride:"",t.morphTargetsCount>0?"#define MORPHTARGETS_COUNT "+t.morphTargetsCount:"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+l:"",t.sizeAttenuation?"#define USE_SIZEATTENUATION":"",t.numLightProbes>0?"#define USE_LIGHT_PROBES":"",t.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"","uniform mat4 modelMatrix;","uniform mat4 modelViewMatrix;","uniform mat4 projectionMatrix;","uniform mat4 viewMatrix;","uniform mat3 normalMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;","#ifdef USE_INSTANCING","	attribute mat4 instanceMatrix;","#endif","#ifdef USE_INSTANCING_COLOR","	attribute vec3 instanceColor;","#endif","#ifdef USE_INSTANCING_MORPH","	uniform sampler2D morphTexture;","#endif","attribute vec3 position;","attribute vec3 normal;","attribute vec2 uv;","#ifdef USE_UV1","	attribute vec2 uv1;","#endif","#ifdef USE_UV2","	attribute vec2 uv2;","#endif","#ifdef USE_UV3","	attribute vec2 uv3;","#endif","#ifdef USE_TANGENT","	attribute vec4 tangent;","#endif","#if defined( USE_COLOR_ALPHA )","	attribute vec4 color;","#elif defined( USE_COLOR )","	attribute vec3 color;","#endif","#ifdef USE_SKINNING","	attribute vec4 skinIndex;","	attribute vec4 skinWeight;","#endif",`
`].filter(Ra).join(`
`),m=[gd(t),"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,g,t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.alphaToCoverage?"#define ALPHA_TO_COVERAGE":"",t.map?"#define USE_MAP":"",t.matcap?"#define USE_MATCAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+c:"",t.envMap?"#define "+h:"",t.envMap?"#define "+u:"",d?"#define CUBEUV_TEXEL_WIDTH "+d.texelWidth:"",d?"#define CUBEUV_TEXEL_HEIGHT "+d.texelHeight:"",d?"#define CUBEUV_MAX_MIP "+d.maxMip+".0":"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",t.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.anisotropy?"#define USE_ANISOTROPY":"",t.anisotropyMap?"#define USE_ANISOTROPYMAP":"",t.clearcoat?"#define USE_CLEARCOAT":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.dispersion?"#define USE_DISPERSION":"",t.iridescence?"#define USE_IRIDESCENCE":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",t.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaTest?"#define USE_ALPHATEST":"",t.alphaHash?"#define USE_ALPHAHASH":"",t.sheen?"#define USE_SHEEN":"",t.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.vertexTangents&&t.flatShading===!1?"#define USE_TANGENT":"",t.vertexColors||t.instancingColor||t.batchingColor?"#define USE_COLOR":"",t.vertexAlphas?"#define USE_COLOR_ALPHA":"",t.vertexUv1s?"#define USE_UV1":"",t.vertexUv2s?"#define USE_UV2":"",t.vertexUv3s?"#define USE_UV3":"",t.pointsUvs?"#define USE_POINTS_UV":"",t.gradientMap?"#define USE_GRADIENTMAP":"",t.flatShading?"#define FLAT_SHADED":"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+l:"",t.premultipliedAlpha?"#define PREMULTIPLIED_ALPHA":"",t.numLightProbes>0?"#define USE_LIGHT_PROBES":"",t.decodeVideoTexture?"#define DECODE_VIDEO_TEXTURE":"",t.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"","uniform mat4 viewMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;",t.toneMapping!==fs?"#define TONE_MAPPING":"",t.toneMapping!==fs?rt.tonemapping_pars_fragment:"",t.toneMapping!==fs?ay("toneMapping",t.toneMapping):"",t.dithering?"#define DITHERING":"",t.opaque?"#define OPAQUE":"",rt.colorspace_pars_fragment,ry("linearToOutputTexel",t.outputColorSpace),oy(),t.useDepthPacking?"#define DEPTH_PACKING "+t.depthPacking:"",`
`].filter(Ra).join(`
`)),a=oh(a),a=fd(a,t),a=pd(a,t),o=oh(o),o=fd(o,t),o=pd(o,t),a=md(a),o=md(o),t.isRawShaderMaterial!==!0&&(M=`#version 300 es
`,p=[f,"#define attribute in","#define varying out","#define texture2D texture"].join(`
`)+`
`+p,m=["#define varying in",t.glslVersion===Pu?"":"layout(location = 0) out highp vec4 pc_fragColor;",t.glslVersion===Pu?"":"#define gl_FragColor pc_fragColor","#define gl_FragDepthEXT gl_FragDepth","#define texture2D texture","#define textureCube texture","#define texture2DProj textureProj","#define texture2DLodEXT textureLod","#define texture2DProjLodEXT textureProjLod","#define textureCubeLodEXT textureLod","#define texture2DGradEXT textureGrad","#define texture2DProjGradEXT textureProjGrad","#define textureCubeGradEXT textureGrad"].join(`
`)+`
`+m);const v=M+p+a,b=M+m+o,N=ud(s,s.VERTEX_SHADER,v),A=ud(s,s.FRAGMENT_SHADER,b);s.attachShader(_,N),s.attachShader(_,A),t.index0AttributeName!==void 0?s.bindAttribLocation(_,0,t.index0AttributeName):t.morphTargets===!0&&s.bindAttribLocation(_,0,"position"),s.linkProgram(_);function R(P){if(i.debug.checkShaderErrors){const K=s.getProgramInfoLog(_).trim(),H=s.getShaderInfoLog(N).trim(),Z=s.getShaderInfoLog(A).trim();let q=!0,ee=!0;if(s.getProgramParameter(_,s.LINK_STATUS)===!1)if(q=!1,typeof i.debug.onShaderError=="function")i.debug.onShaderError(s,_,N,A);else{const Y=dd(s,N,"vertex"),ne=dd(s,A,"fragment");console.error("THREE.WebGLProgram: Shader Error "+s.getError()+" - VALIDATE_STATUS "+s.getProgramParameter(_,s.VALIDATE_STATUS)+`

Material Name: `+P.name+`
Material Type: `+P.type+`

Program Info Log: `+K+`
`+Y+`
`+ne)}else K!==""?console.warn("THREE.WebGLProgram: Program Info Log:",K):(H===""||Z==="")&&(ee=!1);ee&&(P.diagnostics={runnable:q,programLog:K,vertexShader:{log:H,prefix:p},fragmentShader:{log:Z,prefix:m}})}s.deleteShader(N),s.deleteShader(A),F=new Xo(s,_),w=hy(s,_)}let F;this.getUniforms=function(){return F===void 0&&R(this),F};let w;this.getAttributes=function(){return w===void 0&&R(this),w};let y=t.rendererExtensionParallelShaderCompile===!1;return this.isReady=function(){return y===!1&&(y=s.getProgramParameter(_,ty)),y},this.destroy=function(){n.releaseStatesOfProgram(this),s.deleteProgram(_),this.program=void 0},this.type=t.shaderType,this.name=t.shaderName,this.id=ny++,this.cacheKey=e,this.usedTimes=1,this.program=_,this.vertexShader=N,this.fragmentShader=A,this}let Sy=0;class by{constructor(){this.shaderCache=new Map,this.materialCache=new Map}update(e){const t=e.vertexShader,n=e.fragmentShader,s=this._getShaderStage(t),r=this._getShaderStage(n),a=this._getShaderCacheForMaterial(e);return a.has(s)===!1&&(a.add(s),s.usedTimes++),a.has(r)===!1&&(a.add(r),r.usedTimes++),this}remove(e){const t=this.materialCache.get(e);for(const n of t)n.usedTimes--,n.usedTimes===0&&this.shaderCache.delete(n.code);return this.materialCache.delete(e),this}getVertexShaderID(e){return this._getShaderStage(e.vertexShader).id}getFragmentShaderID(e){return this._getShaderStage(e.fragmentShader).id}dispose(){this.shaderCache.clear(),this.materialCache.clear()}_getShaderCacheForMaterial(e){const t=this.materialCache;let n=t.get(e);return n===void 0&&(n=new Set,t.set(e,n)),n}_getShaderStage(e){const t=this.shaderCache;let n=t.get(e);return n===void 0&&(n=new wy(e),t.set(e,n)),n}}class wy{constructor(e){this.id=Sy++,this.code=e,this.usedTimes=0}}function Ey(i,e,t,n,s,r,a){const o=new Ph,l=new by,c=new Set,h=[],u=s.logarithmicDepthBuffer,d=s.vertexTextures;let f=s.precision;const g={MeshDepthMaterial:"depth",MeshDistanceMaterial:"distanceRGBA",MeshNormalMaterial:"normal",MeshBasicMaterial:"basic",MeshLambertMaterial:"lambert",MeshPhongMaterial:"phong",MeshToonMaterial:"toon",MeshStandardMaterial:"physical",MeshPhysicalMaterial:"physical",MeshMatcapMaterial:"matcap",LineBasicMaterial:"basic",LineDashedMaterial:"dashed",PointsMaterial:"points",ShadowMaterial:"shadow",SpriteMaterial:"sprite"};function _(w){return c.add(w),w===0?"uv":`uv${w}`}function p(w,y,P,K,H){const Z=K.fog,q=H.geometry,ee=w.isMeshStandardMaterial?K.environment:null,Y=(w.isMeshStandardMaterial?t:e).get(w.envMap||ee),ne=Y&&Y.mapping===ll?Y.image.height:null,ge=g[w.type];w.precision!==null&&(f=s.getMaxPrecision(w.precision),f!==w.precision&&console.warn("THREE.WebGLProgram.getParameters:",w.precision,"not supported, using",f,"instead."));const de=q.morphAttributes.position||q.morphAttributes.normal||q.morphAttributes.color,ve=de!==void 0?de.length:0;let Te=0;q.morphAttributes.position!==void 0&&(Te=1),q.morphAttributes.normal!==void 0&&(Te=2),q.morphAttributes.color!==void 0&&(Te=3);let ye,ie,he,Me;if(ge){const lt=wi[ge];ye=lt.vertexShader,ie=lt.fragmentShader}else ye=w.vertexShader,ie=w.fragmentShader,l.update(w),he=l.getVertexShaderID(w),Me=l.getFragmentShaderID(w);const fe=i.getRenderTarget(),ze=H.isInstancedMesh===!0,Ge=H.isBatchedMesh===!0,Fe=!!w.map,pt=!!w.matcap,O=!!Y,dt=!!w.aoMap,st=!!w.lightMap,ct=!!w.bumpMap,Oe=!!w.normalMap,wt=!!w.displacementMap,Ye=!!w.emissiveMap,qe=!!w.metalnessMap,D=!!w.roughnessMap,E=w.anisotropy>0,Q=w.clearcoat>0,le=w.dispersion>0,te=w.iridescence>0,X=w.sheen>0,we=w.transmission>0,_e=E&&!!w.anisotropyMap,Re=Q&&!!w.clearcoatMap,Ze=Q&&!!w.clearcoatNormalMap,me=Q&&!!w.clearcoatRoughnessMap,Ae=te&&!!w.iridescenceMap,Je=te&&!!w.iridescenceThicknessMap,ke=X&&!!w.sheenColorMap,be=X&&!!w.sheenRoughnessMap,He=!!w.specularMap,B=!!w.specularColorMap,ce=!!w.specularIntensityMap,U=we&&!!w.transmissionMap,ae=we&&!!w.thicknessMap,se=!!w.gradientMap,re=!!w.alphaMap,xe=w.alphaTest>0,Ke=!!w.alphaHash,ot=!!w.extensions;let _t=fs;w.toneMapped&&(fe===null||fe.isXRRenderTarget===!0)&&(_t=i.toneMapping);const Et={shaderID:ge,shaderType:w.type,shaderName:w.name,vertexShader:ye,fragmentShader:ie,defines:w.defines,customVertexShaderID:he,customFragmentShaderID:Me,isRawShaderMaterial:w.isRawShaderMaterial===!0,glslVersion:w.glslVersion,precision:f,batching:Ge,batchingColor:Ge&&H._colorsTexture!==null,instancing:ze,instancingColor:ze&&H.instanceColor!==null,instancingMorph:ze&&H.morphTexture!==null,supportsVertexTextures:d,outputColorSpace:fe===null?i.outputColorSpace:fe.isXRRenderTarget===!0?fe.texture.colorSpace:Ms,alphaToCoverage:!!w.alphaToCoverage,map:Fe,matcap:pt,envMap:O,envMapMode:O&&Y.mapping,envMapCubeUVHeight:ne,aoMap:dt,lightMap:st,bumpMap:ct,normalMap:Oe,displacementMap:d&&wt,emissiveMap:Ye,normalMapObjectSpace:Oe&&w.normalMapType===vg,normalMapTangentSpace:Oe&&w.normalMapType===jf,metalnessMap:qe,roughnessMap:D,anisotropy:E,anisotropyMap:_e,clearcoat:Q,clearcoatMap:Re,clearcoatNormalMap:Ze,clearcoatRoughnessMap:me,dispersion:le,iridescence:te,iridescenceMap:Ae,iridescenceThicknessMap:Je,sheen:X,sheenColorMap:ke,sheenRoughnessMap:be,specularMap:He,specularColorMap:B,specularIntensityMap:ce,transmission:we,transmissionMap:U,thicknessMap:ae,gradientMap:se,opaque:w.transparent===!1&&w.blending===Or&&w.alphaToCoverage===!1,alphaMap:re,alphaTest:xe,alphaHash:Ke,combine:w.combine,mapUv:Fe&&_(w.map.channel),aoMapUv:dt&&_(w.aoMap.channel),lightMapUv:st&&_(w.lightMap.channel),bumpMapUv:ct&&_(w.bumpMap.channel),normalMapUv:Oe&&_(w.normalMap.channel),displacementMapUv:wt&&_(w.displacementMap.channel),emissiveMapUv:Ye&&_(w.emissiveMap.channel),metalnessMapUv:qe&&_(w.metalnessMap.channel),roughnessMapUv:D&&_(w.roughnessMap.channel),anisotropyMapUv:_e&&_(w.anisotropyMap.channel),clearcoatMapUv:Re&&_(w.clearcoatMap.channel),clearcoatNormalMapUv:Ze&&_(w.clearcoatNormalMap.channel),clearcoatRoughnessMapUv:me&&_(w.clearcoatRoughnessMap.channel),iridescenceMapUv:Ae&&_(w.iridescenceMap.channel),iridescenceThicknessMapUv:Je&&_(w.iridescenceThicknessMap.channel),sheenColorMapUv:ke&&_(w.sheenColorMap.channel),sheenRoughnessMapUv:be&&_(w.sheenRoughnessMap.channel),specularMapUv:He&&_(w.specularMap.channel),specularColorMapUv:B&&_(w.specularColorMap.channel),specularIntensityMapUv:ce&&_(w.specularIntensityMap.channel),transmissionMapUv:U&&_(w.transmissionMap.channel),thicknessMapUv:ae&&_(w.thicknessMap.channel),alphaMapUv:re&&_(w.alphaMap.channel),vertexTangents:!!q.attributes.tangent&&(Oe||E),vertexColors:w.vertexColors,vertexAlphas:w.vertexColors===!0&&!!q.attributes.color&&q.attributes.color.itemSize===4,pointsUvs:H.isPoints===!0&&!!q.attributes.uv&&(Fe||re),fog:!!Z,useFog:w.fog===!0,fogExp2:!!Z&&Z.isFogExp2,flatShading:w.flatShading===!0,sizeAttenuation:w.sizeAttenuation===!0,logarithmicDepthBuffer:u,skinning:H.isSkinnedMesh===!0,morphTargets:q.morphAttributes.position!==void 0,morphNormals:q.morphAttributes.normal!==void 0,morphColors:q.morphAttributes.color!==void 0,morphTargetsCount:ve,morphTextureStride:Te,numDirLights:y.directional.length,numPointLights:y.point.length,numSpotLights:y.spot.length,numSpotLightMaps:y.spotLightMap.length,numRectAreaLights:y.rectArea.length,numHemiLights:y.hemi.length,numDirLightShadows:y.directionalShadowMap.length,numPointLightShadows:y.pointShadowMap.length,numSpotLightShadows:y.spotShadowMap.length,numSpotLightShadowsWithMaps:y.numSpotLightShadowsWithMaps,numLightProbes:y.numLightProbes,numClippingPlanes:a.numPlanes,numClipIntersection:a.numIntersection,dithering:w.dithering,shadowMapEnabled:i.shadowMap.enabled&&P.length>0,shadowMapType:i.shadowMap.type,toneMapping:_t,decodeVideoTexture:Fe&&w.map.isVideoTexture===!0&&bt.getTransfer(w.map.colorSpace)===Ot,premultipliedAlpha:w.premultipliedAlpha,doubleSided:w.side===In,flipSided:w.side===Nn,useDepthPacking:w.depthPacking>=0,depthPacking:w.depthPacking||0,index0AttributeName:w.index0AttributeName,extensionClipCullDistance:ot&&w.extensions.clipCullDistance===!0&&n.has("WEBGL_clip_cull_distance"),extensionMultiDraw:(ot&&w.extensions.multiDraw===!0||Ge)&&n.has("WEBGL_multi_draw"),rendererExtensionParallelShaderCompile:n.has("KHR_parallel_shader_compile"),customProgramCacheKey:w.customProgramCacheKey()};return Et.vertexUv1s=c.has(1),Et.vertexUv2s=c.has(2),Et.vertexUv3s=c.has(3),c.clear(),Et}function m(w){const y=[];if(w.shaderID?y.push(w.shaderID):(y.push(w.customVertexShaderID),y.push(w.customFragmentShaderID)),w.defines!==void 0)for(const P in w.defines)y.push(P),y.push(w.defines[P]);return w.isRawShaderMaterial===!1&&(M(y,w),v(y,w),y.push(i.outputColorSpace)),y.push(w.customProgramCacheKey),y.join()}function M(w,y){w.push(y.precision),w.push(y.outputColorSpace),w.push(y.envMapMode),w.push(y.envMapCubeUVHeight),w.push(y.mapUv),w.push(y.alphaMapUv),w.push(y.lightMapUv),w.push(y.aoMapUv),w.push(y.bumpMapUv),w.push(y.normalMapUv),w.push(y.displacementMapUv),w.push(y.emissiveMapUv),w.push(y.metalnessMapUv),w.push(y.roughnessMapUv),w.push(y.anisotropyMapUv),w.push(y.clearcoatMapUv),w.push(y.clearcoatNormalMapUv),w.push(y.clearcoatRoughnessMapUv),w.push(y.iridescenceMapUv),w.push(y.iridescenceThicknessMapUv),w.push(y.sheenColorMapUv),w.push(y.sheenRoughnessMapUv),w.push(y.specularMapUv),w.push(y.specularColorMapUv),w.push(y.specularIntensityMapUv),w.push(y.transmissionMapUv),w.push(y.thicknessMapUv),w.push(y.combine),w.push(y.fogExp2),w.push(y.sizeAttenuation),w.push(y.morphTargetsCount),w.push(y.morphAttributeCount),w.push(y.numDirLights),w.push(y.numPointLights),w.push(y.numSpotLights),w.push(y.numSpotLightMaps),w.push(y.numHemiLights),w.push(y.numRectAreaLights),w.push(y.numDirLightShadows),w.push(y.numPointLightShadows),w.push(y.numSpotLightShadows),w.push(y.numSpotLightShadowsWithMaps),w.push(y.numLightProbes),w.push(y.shadowMapType),w.push(y.toneMapping),w.push(y.numClippingPlanes),w.push(y.numClipIntersection),w.push(y.depthPacking)}function v(w,y){o.disableAll(),y.supportsVertexTextures&&o.enable(0),y.instancing&&o.enable(1),y.instancingColor&&o.enable(2),y.instancingMorph&&o.enable(3),y.matcap&&o.enable(4),y.envMap&&o.enable(5),y.normalMapObjectSpace&&o.enable(6),y.normalMapTangentSpace&&o.enable(7),y.clearcoat&&o.enable(8),y.iridescence&&o.enable(9),y.alphaTest&&o.enable(10),y.vertexColors&&o.enable(11),y.vertexAlphas&&o.enable(12),y.vertexUv1s&&o.enable(13),y.vertexUv2s&&o.enable(14),y.vertexUv3s&&o.enable(15),y.vertexTangents&&o.enable(16),y.anisotropy&&o.enable(17),y.alphaHash&&o.enable(18),y.batching&&o.enable(19),y.dispersion&&o.enable(20),y.batchingColor&&o.enable(21),w.push(o.mask),o.disableAll(),y.fog&&o.enable(0),y.useFog&&o.enable(1),y.flatShading&&o.enable(2),y.logarithmicDepthBuffer&&o.enable(3),y.skinning&&o.enable(4),y.morphTargets&&o.enable(5),y.morphNormals&&o.enable(6),y.morphColors&&o.enable(7),y.premultipliedAlpha&&o.enable(8),y.shadowMapEnabled&&o.enable(9),y.doubleSided&&o.enable(10),y.flipSided&&o.enable(11),y.useDepthPacking&&o.enable(12),y.dithering&&o.enable(13),y.transmission&&o.enable(14),y.sheen&&o.enable(15),y.opaque&&o.enable(16),y.pointsUvs&&o.enable(17),y.decodeVideoTexture&&o.enable(18),y.alphaToCoverage&&o.enable(19),w.push(o.mask)}function b(w){const y=g[w.type];let P;if(y){const K=wi[y];P=l_.clone(K.uniforms)}else P=w.uniforms;return P}function N(w,y){let P;for(let K=0,H=h.length;K<H;K++){const Z=h[K];if(Z.cacheKey===y){P=Z,++P.usedTimes;break}}return P===void 0&&(P=new My(i,y,w,r),h.push(P)),P}function A(w){if(--w.usedTimes===0){const y=h.indexOf(w);h[y]=h[h.length-1],h.pop(),w.destroy()}}function R(w){l.remove(w)}function F(){l.dispose()}return{getParameters:p,getProgramCacheKey:m,getUniforms:b,acquireProgram:N,releaseProgram:A,releaseShaderCache:R,programs:h,dispose:F}}function Ty(){let i=new WeakMap;function e(a){return i.has(a)}function t(a){let o=i.get(a);return o===void 0&&(o={},i.set(a,o)),o}function n(a){i.delete(a)}function s(a,o,l){i.get(a)[o]=l}function r(){i=new WeakMap}return{has:e,get:t,remove:n,update:s,dispose:r}}function Ay(i,e){return i.groupOrder!==e.groupOrder?i.groupOrder-e.groupOrder:i.renderOrder!==e.renderOrder?i.renderOrder-e.renderOrder:i.material.id!==e.material.id?i.material.id-e.material.id:i.z!==e.z?i.z-e.z:i.id-e.id}function _d(i,e){return i.groupOrder!==e.groupOrder?i.groupOrder-e.groupOrder:i.renderOrder!==e.renderOrder?i.renderOrder-e.renderOrder:i.z!==e.z?e.z-i.z:i.id-e.id}function xd(){const i=[];let e=0;const t=[],n=[],s=[];function r(){e=0,t.length=0,n.length=0,s.length=0}function a(u,d,f,g,_,p){let m=i[e];return m===void 0?(m={id:u.id,object:u,geometry:d,material:f,groupOrder:g,renderOrder:u.renderOrder,z:_,group:p},i[e]=m):(m.id=u.id,m.object=u,m.geometry=d,m.material=f,m.groupOrder=g,m.renderOrder=u.renderOrder,m.z=_,m.group=p),e++,m}function o(u,d,f,g,_,p){const m=a(u,d,f,g,_,p);f.transmission>0?n.push(m):f.transparent===!0?s.push(m):t.push(m)}function l(u,d,f,g,_,p){const m=a(u,d,f,g,_,p);f.transmission>0?n.unshift(m):f.transparent===!0?s.unshift(m):t.unshift(m)}function c(u,d){t.length>1&&t.sort(u||Ay),n.length>1&&n.sort(d||_d),s.length>1&&s.sort(d||_d)}function h(){for(let u=e,d=i.length;u<d;u++){const f=i[u];if(f.id===null)break;f.id=null,f.object=null,f.geometry=null,f.material=null,f.group=null}}return{opaque:t,transmissive:n,transparent:s,init:r,push:o,unshift:l,finish:h,sort:c}}function Ry(){let i=new WeakMap;function e(n,s){const r=i.get(n);let a;return r===void 0?(a=new xd,i.set(n,[a])):s>=r.length?(a=new xd,r.push(a)):a=r[s],a}function t(){i=new WeakMap}return{get:e,dispose:t}}function Cy(){const i={};return{get:function(e){if(i[e.id]!==void 0)return i[e.id];let t;switch(e.type){case"DirectionalLight":t={direction:new V,color:new nt};break;case"SpotLight":t={position:new V,direction:new V,color:new nt,distance:0,coneCos:0,penumbraCos:0,decay:0};break;case"PointLight":t={position:new V,color:new nt,distance:0,decay:0};break;case"HemisphereLight":t={direction:new V,skyColor:new nt,groundColor:new nt};break;case"RectAreaLight":t={color:new nt,position:new V,halfWidth:new V,halfHeight:new V};break}return i[e.id]=t,t}}}function Py(){const i={};return{get:function(e){if(i[e.id]!==void 0)return i[e.id];let t;switch(e.type){case"DirectionalLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new $e};break;case"SpotLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new $e};break;case"PointLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new $e,shadowCameraNear:1,shadowCameraFar:1e3};break}return i[e.id]=t,t}}}let Ly=0;function Dy(i,e){return(e.castShadow?2:0)-(i.castShadow?2:0)+(e.map?1:0)-(i.map?1:0)}function Iy(i){const e=new Cy,t=Py(),n={version:0,hash:{directionalLength:-1,pointLength:-1,spotLength:-1,rectAreaLength:-1,hemiLength:-1,numDirectionalShadows:-1,numPointShadows:-1,numSpotShadows:-1,numSpotMaps:-1,numLightProbes:-1},ambient:[0,0,0],probe:[],directional:[],directionalShadow:[],directionalShadowMap:[],directionalShadowMatrix:[],spot:[],spotLightMap:[],spotShadow:[],spotShadowMap:[],spotLightMatrix:[],rectArea:[],rectAreaLTC1:null,rectAreaLTC2:null,point:[],pointShadow:[],pointShadowMap:[],pointShadowMatrix:[],hemi:[],numSpotLightShadowsWithMaps:0,numLightProbes:0};for(let c=0;c<9;c++)n.probe.push(new V);const s=new V,r=new Bt,a=new Bt;function o(c){let h=0,u=0,d=0;for(let w=0;w<9;w++)n.probe[w].set(0,0,0);let f=0,g=0,_=0,p=0,m=0,M=0,v=0,b=0,N=0,A=0,R=0;c.sort(Dy);for(let w=0,y=c.length;w<y;w++){const P=c[w],K=P.color,H=P.intensity,Z=P.distance,q=P.shadow&&P.shadow.map?P.shadow.map.texture:null;if(P.isAmbientLight)h+=K.r*H,u+=K.g*H,d+=K.b*H;else if(P.isLightProbe){for(let ee=0;ee<9;ee++)n.probe[ee].addScaledVector(P.sh.coefficients[ee],H);R++}else if(P.isDirectionalLight){const ee=e.get(P);if(ee.color.copy(P.color).multiplyScalar(P.intensity),P.castShadow){const Y=P.shadow,ne=t.get(P);ne.shadowIntensity=Y.intensity,ne.shadowBias=Y.bias,ne.shadowNormalBias=Y.normalBias,ne.shadowRadius=Y.radius,ne.shadowMapSize=Y.mapSize,n.directionalShadow[f]=ne,n.directionalShadowMap[f]=q,n.directionalShadowMatrix[f]=P.shadow.matrix,M++}n.directional[f]=ee,f++}else if(P.isSpotLight){const ee=e.get(P);ee.position.setFromMatrixPosition(P.matrixWorld),ee.color.copy(K).multiplyScalar(H),ee.distance=Z,ee.coneCos=Math.cos(P.angle),ee.penumbraCos=Math.cos(P.angle*(1-P.penumbra)),ee.decay=P.decay,n.spot[_]=ee;const Y=P.shadow;if(P.map&&(n.spotLightMap[N]=P.map,N++,Y.updateMatrices(P),P.castShadow&&A++),n.spotLightMatrix[_]=Y.matrix,P.castShadow){const ne=t.get(P);ne.shadowIntensity=Y.intensity,ne.shadowBias=Y.bias,ne.shadowNormalBias=Y.normalBias,ne.shadowRadius=Y.radius,ne.shadowMapSize=Y.mapSize,n.spotShadow[_]=ne,n.spotShadowMap[_]=q,b++}_++}else if(P.isRectAreaLight){const ee=e.get(P);ee.color.copy(K).multiplyScalar(H),ee.halfWidth.set(P.width*.5,0,0),ee.halfHeight.set(0,P.height*.5,0),n.rectArea[p]=ee,p++}else if(P.isPointLight){const ee=e.get(P);if(ee.color.copy(P.color).multiplyScalar(P.intensity),ee.distance=P.distance,ee.decay=P.decay,P.castShadow){const Y=P.shadow,ne=t.get(P);ne.shadowIntensity=Y.intensity,ne.shadowBias=Y.bias,ne.shadowNormalBias=Y.normalBias,ne.shadowRadius=Y.radius,ne.shadowMapSize=Y.mapSize,ne.shadowCameraNear=Y.camera.near,ne.shadowCameraFar=Y.camera.far,n.pointShadow[g]=ne,n.pointShadowMap[g]=q,n.pointShadowMatrix[g]=P.shadow.matrix,v++}n.point[g]=ee,g++}else if(P.isHemisphereLight){const ee=e.get(P);ee.skyColor.copy(P.color).multiplyScalar(H),ee.groundColor.copy(P.groundColor).multiplyScalar(H),n.hemi[m]=ee,m++}}p>0&&(i.has("OES_texture_float_linear")===!0?(n.rectAreaLTC1=Ce.LTC_FLOAT_1,n.rectAreaLTC2=Ce.LTC_FLOAT_2):(n.rectAreaLTC1=Ce.LTC_HALF_1,n.rectAreaLTC2=Ce.LTC_HALF_2)),n.ambient[0]=h,n.ambient[1]=u,n.ambient[2]=d;const F=n.hash;(F.directionalLength!==f||F.pointLength!==g||F.spotLength!==_||F.rectAreaLength!==p||F.hemiLength!==m||F.numDirectionalShadows!==M||F.numPointShadows!==v||F.numSpotShadows!==b||F.numSpotMaps!==N||F.numLightProbes!==R)&&(n.directional.length=f,n.spot.length=_,n.rectArea.length=p,n.point.length=g,n.hemi.length=m,n.directionalShadow.length=M,n.directionalShadowMap.length=M,n.pointShadow.length=v,n.pointShadowMap.length=v,n.spotShadow.length=b,n.spotShadowMap.length=b,n.directionalShadowMatrix.length=M,n.pointShadowMatrix.length=v,n.spotLightMatrix.length=b+N-A,n.spotLightMap.length=N,n.numSpotLightShadowsWithMaps=A,n.numLightProbes=R,F.directionalLength=f,F.pointLength=g,F.spotLength=_,F.rectAreaLength=p,F.hemiLength=m,F.numDirectionalShadows=M,F.numPointShadows=v,F.numSpotShadows=b,F.numSpotMaps=N,F.numLightProbes=R,n.version=Ly++)}function l(c,h){let u=0,d=0,f=0,g=0,_=0;const p=h.matrixWorldInverse;for(let m=0,M=c.length;m<M;m++){const v=c[m];if(v.isDirectionalLight){const b=n.directional[u];b.direction.setFromMatrixPosition(v.matrixWorld),s.setFromMatrixPosition(v.target.matrixWorld),b.direction.sub(s),b.direction.transformDirection(p),u++}else if(v.isSpotLight){const b=n.spot[f];b.position.setFromMatrixPosition(v.matrixWorld),b.position.applyMatrix4(p),b.direction.setFromMatrixPosition(v.matrixWorld),s.setFromMatrixPosition(v.target.matrixWorld),b.direction.sub(s),b.direction.transformDirection(p),f++}else if(v.isRectAreaLight){const b=n.rectArea[g];b.position.setFromMatrixPosition(v.matrixWorld),b.position.applyMatrix4(p),a.identity(),r.copy(v.matrixWorld),r.premultiply(p),a.extractRotation(r),b.halfWidth.set(v.width*.5,0,0),b.halfHeight.set(0,v.height*.5,0),b.halfWidth.applyMatrix4(a),b.halfHeight.applyMatrix4(a),g++}else if(v.isPointLight){const b=n.point[d];b.position.setFromMatrixPosition(v.matrixWorld),b.position.applyMatrix4(p),d++}else if(v.isHemisphereLight){const b=n.hemi[_];b.direction.setFromMatrixPosition(v.matrixWorld),b.direction.transformDirection(p),_++}}}return{setup:o,setupView:l,state:n}}function vd(i){const e=new Iy(i),t=[],n=[];function s(h){c.camera=h,t.length=0,n.length=0}function r(h){t.push(h)}function a(h){n.push(h)}function o(){e.setup(t)}function l(h){e.setupView(t,h)}const c={lightsArray:t,shadowsArray:n,camera:null,lights:e,transmissionRenderTarget:{}};return{init:s,state:c,setupLights:o,setupLightsView:l,pushLight:r,pushShadow:a}}function Uy(i){let e=new WeakMap;function t(s,r=0){const a=e.get(s);let o;return a===void 0?(o=new vd(i),e.set(s,[o])):r>=a.length?(o=new vd(i),a.push(o)):o=a[r],o}function n(){e=new WeakMap}return{get:t,dispose:n}}class Ny extends Ss{constructor(e){super(),this.isMeshDepthMaterial=!0,this.type="MeshDepthMaterial",this.depthPacking=_g,this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.wireframe=!1,this.wireframeLinewidth=1,this.setValues(e)}copy(e){return super.copy(e),this.depthPacking=e.depthPacking,this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this}}class Fy extends Ss{constructor(e){super(),this.isMeshDistanceMaterial=!0,this.type="MeshDistanceMaterial",this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.setValues(e)}copy(e){return super.copy(e),this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this}}const Oy=`void main() {
	gl_Position = vec4( position, 1.0 );
}`,By=`uniform sampler2D shadow_pass;
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
}`;function zy(i,e,t){let n=new Lh;const s=new $e,r=new $e,a=new sn,o=new Ny({depthPacking:xg}),l=new Fy,c={},h=t.maxTextureSize,u={[gs]:Nn,[Nn]:gs,[In]:In},d=new _s({defines:{VSM_SAMPLES:8},uniforms:{shadow_pass:{value:null},resolution:{value:new $e},radius:{value:4}},vertexShader:Oy,fragmentShader:By}),f=d.clone();f.defines.HORIZONTAL_PASS=1;const g=new Gt;g.setAttribute("position",new pi(new Float32Array([-1,-1,.5,3,-1,.5,-1,3,.5]),3));const _=new Qt(g,d),p=this;this.enabled=!1,this.autoUpdate=!0,this.needsUpdate=!1,this.type=Uf;let m=this.type;this.render=function(A,R,F){if(p.enabled===!1||p.autoUpdate===!1&&p.needsUpdate===!1||A.length===0)return;const w=i.getRenderTarget(),y=i.getActiveCubeFace(),P=i.getActiveMipmapLevel(),K=i.state;K.setBlending(ds),K.buffers.color.setClear(1,1,1,1),K.buffers.depth.setTest(!0),K.setScissorTest(!1);const H=m!==Hi&&this.type===Hi,Z=m===Hi&&this.type!==Hi;for(let q=0,ee=A.length;q<ee;q++){const Y=A[q],ne=Y.shadow;if(ne===void 0){console.warn("THREE.WebGLShadowMap:",Y,"has no shadow.");continue}if(ne.autoUpdate===!1&&ne.needsUpdate===!1)continue;s.copy(ne.mapSize);const ge=ne.getFrameExtents();if(s.multiply(ge),r.copy(ne.mapSize),(s.x>h||s.y>h)&&(s.x>h&&(r.x=Math.floor(h/ge.x),s.x=r.x*ge.x,ne.mapSize.x=r.x),s.y>h&&(r.y=Math.floor(h/ge.y),s.y=r.y*ge.y,ne.mapSize.y=r.y)),ne.map===null||H===!0||Z===!0){const ve=this.type!==Hi?{minFilter:ei,magFilter:ei}:{};ne.map!==null&&ne.map.dispose(),ne.map=new $s(s.x,s.y,ve),ne.map.texture.name=Y.name+".shadowMap",ne.camera.updateProjectionMatrix()}i.setRenderTarget(ne.map),i.clear();const de=ne.getViewportCount();for(let ve=0;ve<de;ve++){const Te=ne.getViewport(ve);a.set(r.x*Te.x,r.y*Te.y,r.x*Te.z,r.y*Te.w),K.viewport(a),ne.updateMatrices(Y,ve),n=ne.getFrustum(),b(R,F,ne.camera,Y,this.type)}ne.isPointLightShadow!==!0&&this.type===Hi&&M(ne,F),ne.needsUpdate=!1}m=this.type,p.needsUpdate=!1,i.setRenderTarget(w,y,P)};function M(A,R){const F=e.update(_);d.defines.VSM_SAMPLES!==A.blurSamples&&(d.defines.VSM_SAMPLES=A.blurSamples,f.defines.VSM_SAMPLES=A.blurSamples,d.needsUpdate=!0,f.needsUpdate=!0),A.mapPass===null&&(A.mapPass=new $s(s.x,s.y)),d.uniforms.shadow_pass.value=A.map.texture,d.uniforms.resolution.value=A.mapSize,d.uniforms.radius.value=A.radius,i.setRenderTarget(A.mapPass),i.clear(),i.renderBufferDirect(R,null,F,d,_,null),f.uniforms.shadow_pass.value=A.mapPass.texture,f.uniforms.resolution.value=A.mapSize,f.uniforms.radius.value=A.radius,i.setRenderTarget(A.map),i.clear(),i.renderBufferDirect(R,null,F,f,_,null)}function v(A,R,F,w){let y=null;const P=F.isPointLight===!0?A.customDistanceMaterial:A.customDepthMaterial;if(P!==void 0)y=P;else if(y=F.isPointLight===!0?l:o,i.localClippingEnabled&&R.clipShadows===!0&&Array.isArray(R.clippingPlanes)&&R.clippingPlanes.length!==0||R.displacementMap&&R.displacementScale!==0||R.alphaMap&&R.alphaTest>0||R.map&&R.alphaTest>0){const K=y.uuid,H=R.uuid;let Z=c[K];Z===void 0&&(Z={},c[K]=Z);let q=Z[H];q===void 0&&(q=y.clone(),Z[H]=q,R.addEventListener("dispose",N)),y=q}if(y.visible=R.visible,y.wireframe=R.wireframe,w===Hi?y.side=R.shadowSide!==null?R.shadowSide:R.side:y.side=R.shadowSide!==null?R.shadowSide:u[R.side],y.alphaMap=R.alphaMap,y.alphaTest=R.alphaTest,y.map=R.map,y.clipShadows=R.clipShadows,y.clippingPlanes=R.clippingPlanes,y.clipIntersection=R.clipIntersection,y.displacementMap=R.displacementMap,y.displacementScale=R.displacementScale,y.displacementBias=R.displacementBias,y.wireframeLinewidth=R.wireframeLinewidth,y.linewidth=R.linewidth,F.isPointLight===!0&&y.isMeshDistanceMaterial===!0){const K=i.properties.get(y);K.light=F}return y}function b(A,R,F,w,y){if(A.visible===!1)return;if(A.layers.test(R.layers)&&(A.isMesh||A.isLine||A.isPoints)&&(A.castShadow||A.receiveShadow&&y===Hi)&&(!A.frustumCulled||n.intersectsObject(A))){A.modelViewMatrix.multiplyMatrices(F.matrixWorldInverse,A.matrixWorld);const H=e.update(A),Z=A.material;if(Array.isArray(Z)){const q=H.groups;for(let ee=0,Y=q.length;ee<Y;ee++){const ne=q[ee],ge=Z[ne.materialIndex];if(ge&&ge.visible){const de=v(A,ge,w,y);A.onBeforeShadow(i,A,R,F,H,de,ne),i.renderBufferDirect(F,null,H,de,A,ne),A.onAfterShadow(i,A,R,F,H,de,ne)}}}else if(Z.visible){const q=v(A,Z,w,y);A.onBeforeShadow(i,A,R,F,H,q,null),i.renderBufferDirect(F,null,H,q,A,null),A.onAfterShadow(i,A,R,F,H,q,null)}}const K=A.children;for(let H=0,Z=K.length;H<Z;H++)b(K[H],R,F,w,y)}function N(A){A.target.removeEventListener("dispose",N);for(const F in c){const w=c[F],y=A.target.uuid;y in w&&(w[y].dispose(),delete w[y])}}}function ky(i){function e(){let U=!1;const ae=new sn;let se=null;const re=new sn(0,0,0,0);return{setMask:function(xe){se!==xe&&!U&&(i.colorMask(xe,xe,xe,xe),se=xe)},setLocked:function(xe){U=xe},setClear:function(xe,Ke,ot,_t,Et){Et===!0&&(xe*=_t,Ke*=_t,ot*=_t),ae.set(xe,Ke,ot,_t),re.equals(ae)===!1&&(i.clearColor(xe,Ke,ot,_t),re.copy(ae))},reset:function(){U=!1,se=null,re.set(-1,0,0,0)}}}function t(){let U=!1,ae=null,se=null,re=null;return{setTest:function(xe){xe?Me(i.DEPTH_TEST):fe(i.DEPTH_TEST)},setMask:function(xe){ae!==xe&&!U&&(i.depthMask(xe),ae=xe)},setFunc:function(xe){if(se!==xe){switch(xe){case tg:i.depthFunc(i.NEVER);break;case ng:i.depthFunc(i.ALWAYS);break;case ig:i.depthFunc(i.LESS);break;case Yo:i.depthFunc(i.LEQUAL);break;case sg:i.depthFunc(i.EQUAL);break;case rg:i.depthFunc(i.GEQUAL);break;case ag:i.depthFunc(i.GREATER);break;case og:i.depthFunc(i.NOTEQUAL);break;default:i.depthFunc(i.LEQUAL)}se=xe}},setLocked:function(xe){U=xe},setClear:function(xe){re!==xe&&(i.clearDepth(xe),re=xe)},reset:function(){U=!1,ae=null,se=null,re=null}}}function n(){let U=!1,ae=null,se=null,re=null,xe=null,Ke=null,ot=null,_t=null,Et=null;return{setTest:function(lt){U||(lt?Me(i.STENCIL_TEST):fe(i.STENCIL_TEST))},setMask:function(lt){ae!==lt&&!U&&(i.stencilMask(lt),ae=lt)},setFunc:function(lt,mn,kt){(se!==lt||re!==mn||xe!==kt)&&(i.stencilFunc(lt,mn,kt),se=lt,re=mn,xe=kt)},setOp:function(lt,mn,kt){(Ke!==lt||ot!==mn||_t!==kt)&&(i.stencilOp(lt,mn,kt),Ke=lt,ot=mn,_t=kt)},setLocked:function(lt){U=lt},setClear:function(lt){Et!==lt&&(i.clearStencil(lt),Et=lt)},reset:function(){U=!1,ae=null,se=null,re=null,xe=null,Ke=null,ot=null,_t=null,Et=null}}}const s=new e,r=new t,a=new n,o=new WeakMap,l=new WeakMap;let c={},h={},u=new WeakMap,d=[],f=null,g=!1,_=null,p=null,m=null,M=null,v=null,b=null,N=null,A=new nt(0,0,0),R=0,F=!1,w=null,y=null,P=null,K=null,H=null;const Z=i.getParameter(i.MAX_COMBINED_TEXTURE_IMAGE_UNITS);let q=!1,ee=0;const Y=i.getParameter(i.VERSION);Y.indexOf("WebGL")!==-1?(ee=parseFloat(/^WebGL (\d)/.exec(Y)[1]),q=ee>=1):Y.indexOf("OpenGL ES")!==-1&&(ee=parseFloat(/^OpenGL ES (\d)/.exec(Y)[1]),q=ee>=2);let ne=null,ge={};const de=i.getParameter(i.SCISSOR_BOX),ve=i.getParameter(i.VIEWPORT),Te=new sn().fromArray(de),ye=new sn().fromArray(ve);function ie(U,ae,se,re){const xe=new Uint8Array(4),Ke=i.createTexture();i.bindTexture(U,Ke),i.texParameteri(U,i.TEXTURE_MIN_FILTER,i.NEAREST),i.texParameteri(U,i.TEXTURE_MAG_FILTER,i.NEAREST);for(let ot=0;ot<se;ot++)U===i.TEXTURE_3D||U===i.TEXTURE_2D_ARRAY?i.texImage3D(ae,0,i.RGBA,1,1,re,0,i.RGBA,i.UNSIGNED_BYTE,xe):i.texImage2D(ae+ot,0,i.RGBA,1,1,0,i.RGBA,i.UNSIGNED_BYTE,xe);return Ke}const he={};he[i.TEXTURE_2D]=ie(i.TEXTURE_2D,i.TEXTURE_2D,1),he[i.TEXTURE_CUBE_MAP]=ie(i.TEXTURE_CUBE_MAP,i.TEXTURE_CUBE_MAP_POSITIVE_X,6),he[i.TEXTURE_2D_ARRAY]=ie(i.TEXTURE_2D_ARRAY,i.TEXTURE_2D_ARRAY,1,1),he[i.TEXTURE_3D]=ie(i.TEXTURE_3D,i.TEXTURE_3D,1,1),s.setClear(0,0,0,1),r.setClear(1),a.setClear(0),Me(i.DEPTH_TEST),r.setFunc(Yo),ct(!1),Oe(Eu),Me(i.CULL_FACE),dt(ds);function Me(U){c[U]!==!0&&(i.enable(U),c[U]=!0)}function fe(U){c[U]!==!1&&(i.disable(U),c[U]=!1)}function ze(U,ae){return h[U]!==ae?(i.bindFramebuffer(U,ae),h[U]=ae,U===i.DRAW_FRAMEBUFFER&&(h[i.FRAMEBUFFER]=ae),U===i.FRAMEBUFFER&&(h[i.DRAW_FRAMEBUFFER]=ae),!0):!1}function Ge(U,ae){let se=d,re=!1;if(U){se=u.get(ae),se===void 0&&(se=[],u.set(ae,se));const xe=U.textures;if(se.length!==xe.length||se[0]!==i.COLOR_ATTACHMENT0){for(let Ke=0,ot=xe.length;Ke<ot;Ke++)se[Ke]=i.COLOR_ATTACHMENT0+Ke;se.length=xe.length,re=!0}}else se[0]!==i.BACK&&(se[0]=i.BACK,re=!0);re&&i.drawBuffers(se)}function Fe(U){return f!==U?(i.useProgram(U),f=U,!0):!1}const pt={[Os]:i.FUNC_ADD,[Bm]:i.FUNC_SUBTRACT,[zm]:i.FUNC_REVERSE_SUBTRACT};pt[km]=i.MIN,pt[Hm]=i.MAX;const O={[Vm]:i.ZERO,[Gm]:i.ONE,[Wm]:i.SRC_COLOR,[Ac]:i.SRC_ALPHA,[Km]:i.SRC_ALPHA_SATURATE,[Ym]:i.DST_COLOR,[qm]:i.DST_ALPHA,[Xm]:i.ONE_MINUS_SRC_COLOR,[Rc]:i.ONE_MINUS_SRC_ALPHA,[jm]:i.ONE_MINUS_DST_COLOR,[$m]:i.ONE_MINUS_DST_ALPHA,[Zm]:i.CONSTANT_COLOR,[Jm]:i.ONE_MINUS_CONSTANT_COLOR,[Qm]:i.CONSTANT_ALPHA,[eg]:i.ONE_MINUS_CONSTANT_ALPHA};function dt(U,ae,se,re,xe,Ke,ot,_t,Et,lt){if(U===ds){g===!0&&(fe(i.BLEND),g=!1);return}if(g===!1&&(Me(i.BLEND),g=!0),U!==Om){if(U!==_||lt!==F){if((p!==Os||v!==Os)&&(i.blendEquation(i.FUNC_ADD),p=Os,v=Os),lt)switch(U){case Or:i.blendFuncSeparate(i.ONE,i.ONE_MINUS_SRC_ALPHA,i.ONE,i.ONE_MINUS_SRC_ALPHA);break;case Tu:i.blendFunc(i.ONE,i.ONE);break;case Au:i.blendFuncSeparate(i.ZERO,i.ONE_MINUS_SRC_COLOR,i.ZERO,i.ONE);break;case Ru:i.blendFuncSeparate(i.ZERO,i.SRC_COLOR,i.ZERO,i.SRC_ALPHA);break;default:console.error("THREE.WebGLState: Invalid blending: ",U);break}else switch(U){case Or:i.blendFuncSeparate(i.SRC_ALPHA,i.ONE_MINUS_SRC_ALPHA,i.ONE,i.ONE_MINUS_SRC_ALPHA);break;case Tu:i.blendFunc(i.SRC_ALPHA,i.ONE);break;case Au:i.blendFuncSeparate(i.ZERO,i.ONE_MINUS_SRC_COLOR,i.ZERO,i.ONE);break;case Ru:i.blendFunc(i.ZERO,i.SRC_COLOR);break;default:console.error("THREE.WebGLState: Invalid blending: ",U);break}m=null,M=null,b=null,N=null,A.set(0,0,0),R=0,_=U,F=lt}return}xe=xe||ae,Ke=Ke||se,ot=ot||re,(ae!==p||xe!==v)&&(i.blendEquationSeparate(pt[ae],pt[xe]),p=ae,v=xe),(se!==m||re!==M||Ke!==b||ot!==N)&&(i.blendFuncSeparate(O[se],O[re],O[Ke],O[ot]),m=se,M=re,b=Ke,N=ot),(_t.equals(A)===!1||Et!==R)&&(i.blendColor(_t.r,_t.g,_t.b,Et),A.copy(_t),R=Et),_=U,F=!1}function st(U,ae){U.side===In?fe(i.CULL_FACE):Me(i.CULL_FACE);let se=U.side===Nn;ae&&(se=!se),ct(se),U.blending===Or&&U.transparent===!1?dt(ds):dt(U.blending,U.blendEquation,U.blendSrc,U.blendDst,U.blendEquationAlpha,U.blendSrcAlpha,U.blendDstAlpha,U.blendColor,U.blendAlpha,U.premultipliedAlpha),r.setFunc(U.depthFunc),r.setTest(U.depthTest),r.setMask(U.depthWrite),s.setMask(U.colorWrite);const re=U.stencilWrite;a.setTest(re),re&&(a.setMask(U.stencilWriteMask),a.setFunc(U.stencilFunc,U.stencilRef,U.stencilFuncMask),a.setOp(U.stencilFail,U.stencilZFail,U.stencilZPass)),Ye(U.polygonOffset,U.polygonOffsetFactor,U.polygonOffsetUnits),U.alphaToCoverage===!0?Me(i.SAMPLE_ALPHA_TO_COVERAGE):fe(i.SAMPLE_ALPHA_TO_COVERAGE)}function ct(U){w!==U&&(U?i.frontFace(i.CW):i.frontFace(i.CCW),w=U)}function Oe(U){U!==Nm?(Me(i.CULL_FACE),U!==y&&(U===Eu?i.cullFace(i.BACK):U===Fm?i.cullFace(i.FRONT):i.cullFace(i.FRONT_AND_BACK))):fe(i.CULL_FACE),y=U}function wt(U){U!==P&&(q&&i.lineWidth(U),P=U)}function Ye(U,ae,se){U?(Me(i.POLYGON_OFFSET_FILL),(K!==ae||H!==se)&&(i.polygonOffset(ae,se),K=ae,H=se)):fe(i.POLYGON_OFFSET_FILL)}function qe(U){U?Me(i.SCISSOR_TEST):fe(i.SCISSOR_TEST)}function D(U){U===void 0&&(U=i.TEXTURE0+Z-1),ne!==U&&(i.activeTexture(U),ne=U)}function E(U,ae,se){se===void 0&&(ne===null?se=i.TEXTURE0+Z-1:se=ne);let re=ge[se];re===void 0&&(re={type:void 0,texture:void 0},ge[se]=re),(re.type!==U||re.texture!==ae)&&(ne!==se&&(i.activeTexture(se),ne=se),i.bindTexture(U,ae||he[U]),re.type=U,re.texture=ae)}function Q(){const U=ge[ne];U!==void 0&&U.type!==void 0&&(i.bindTexture(U.type,null),U.type=void 0,U.texture=void 0)}function le(){try{i.compressedTexImage2D.apply(i,arguments)}catch(U){console.error("THREE.WebGLState:",U)}}function te(){try{i.compressedTexImage3D.apply(i,arguments)}catch(U){console.error("THREE.WebGLState:",U)}}function X(){try{i.texSubImage2D.apply(i,arguments)}catch(U){console.error("THREE.WebGLState:",U)}}function we(){try{i.texSubImage3D.apply(i,arguments)}catch(U){console.error("THREE.WebGLState:",U)}}function _e(){try{i.compressedTexSubImage2D.apply(i,arguments)}catch(U){console.error("THREE.WebGLState:",U)}}function Re(){try{i.compressedTexSubImage3D.apply(i,arguments)}catch(U){console.error("THREE.WebGLState:",U)}}function Ze(){try{i.texStorage2D.apply(i,arguments)}catch(U){console.error("THREE.WebGLState:",U)}}function me(){try{i.texStorage3D.apply(i,arguments)}catch(U){console.error("THREE.WebGLState:",U)}}function Ae(){try{i.texImage2D.apply(i,arguments)}catch(U){console.error("THREE.WebGLState:",U)}}function Je(){try{i.texImage3D.apply(i,arguments)}catch(U){console.error("THREE.WebGLState:",U)}}function ke(U){Te.equals(U)===!1&&(i.scissor(U.x,U.y,U.z,U.w),Te.copy(U))}function be(U){ye.equals(U)===!1&&(i.viewport(U.x,U.y,U.z,U.w),ye.copy(U))}function He(U,ae){let se=l.get(ae);se===void 0&&(se=new WeakMap,l.set(ae,se));let re=se.get(U);re===void 0&&(re=i.getUniformBlockIndex(ae,U.name),se.set(U,re))}function B(U,ae){const re=l.get(ae).get(U);o.get(ae)!==re&&(i.uniformBlockBinding(ae,re,U.__bindingPointIndex),o.set(ae,re))}function ce(){i.disable(i.BLEND),i.disable(i.CULL_FACE),i.disable(i.DEPTH_TEST),i.disable(i.POLYGON_OFFSET_FILL),i.disable(i.SCISSOR_TEST),i.disable(i.STENCIL_TEST),i.disable(i.SAMPLE_ALPHA_TO_COVERAGE),i.blendEquation(i.FUNC_ADD),i.blendFunc(i.ONE,i.ZERO),i.blendFuncSeparate(i.ONE,i.ZERO,i.ONE,i.ZERO),i.blendColor(0,0,0,0),i.colorMask(!0,!0,!0,!0),i.clearColor(0,0,0,0),i.depthMask(!0),i.depthFunc(i.LESS),i.clearDepth(1),i.stencilMask(4294967295),i.stencilFunc(i.ALWAYS,0,4294967295),i.stencilOp(i.KEEP,i.KEEP,i.KEEP),i.clearStencil(0),i.cullFace(i.BACK),i.frontFace(i.CCW),i.polygonOffset(0,0),i.activeTexture(i.TEXTURE0),i.bindFramebuffer(i.FRAMEBUFFER,null),i.bindFramebuffer(i.DRAW_FRAMEBUFFER,null),i.bindFramebuffer(i.READ_FRAMEBUFFER,null),i.useProgram(null),i.lineWidth(1),i.scissor(0,0,i.canvas.width,i.canvas.height),i.viewport(0,0,i.canvas.width,i.canvas.height),c={},ne=null,ge={},h={},u=new WeakMap,d=[],f=null,g=!1,_=null,p=null,m=null,M=null,v=null,b=null,N=null,A=new nt(0,0,0),R=0,F=!1,w=null,y=null,P=null,K=null,H=null,Te.set(0,0,i.canvas.width,i.canvas.height),ye.set(0,0,i.canvas.width,i.canvas.height),s.reset(),r.reset(),a.reset()}return{buffers:{color:s,depth:r,stencil:a},enable:Me,disable:fe,bindFramebuffer:ze,drawBuffers:Ge,useProgram:Fe,setBlending:dt,setMaterial:st,setFlipSided:ct,setCullFace:Oe,setLineWidth:wt,setPolygonOffset:Ye,setScissorTest:qe,activeTexture:D,bindTexture:E,unbindTexture:Q,compressedTexImage2D:le,compressedTexImage3D:te,texImage2D:Ae,texImage3D:Je,updateUBOMapping:He,uniformBlockBinding:B,texStorage2D:Ze,texStorage3D:me,texSubImage2D:X,texSubImage3D:we,compressedTexSubImage2D:_e,compressedTexSubImage3D:Re,scissor:ke,viewport:be,reset:ce}}function yd(i,e,t,n){const s=Hy(n);switch(t){case Vf:return i*e;case Wf:return i*e;case Xf:return i*e*2;case qf:return i*e/s.components*s.byteLength;case Eh:return i*e/s.components*s.byteLength;case $f:return i*e*2/s.components*s.byteLength;case Th:return i*e*2/s.components*s.byteLength;case Gf:return i*e*3/s.components*s.byteLength;case fi:return i*e*4/s.components*s.byteLength;case Ah:return i*e*4/s.components*s.byteLength;case ko:case Ho:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*8;case Vo:case Go:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*16;case Uc:case Fc:return Math.max(i,16)*Math.max(e,8)/4;case Ic:case Nc:return Math.max(i,8)*Math.max(e,8)/2;case Oc:case Bc:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*8;case zc:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*16;case kc:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*16;case Hc:return Math.floor((i+4)/5)*Math.floor((e+3)/4)*16;case Vc:return Math.floor((i+4)/5)*Math.floor((e+4)/5)*16;case Gc:return Math.floor((i+5)/6)*Math.floor((e+4)/5)*16;case Wc:return Math.floor((i+5)/6)*Math.floor((e+5)/6)*16;case Xc:return Math.floor((i+7)/8)*Math.floor((e+4)/5)*16;case qc:return Math.floor((i+7)/8)*Math.floor((e+5)/6)*16;case $c:return Math.floor((i+7)/8)*Math.floor((e+7)/8)*16;case Yc:return Math.floor((i+9)/10)*Math.floor((e+4)/5)*16;case jc:return Math.floor((i+9)/10)*Math.floor((e+5)/6)*16;case Kc:return Math.floor((i+9)/10)*Math.floor((e+7)/8)*16;case Zc:return Math.floor((i+9)/10)*Math.floor((e+9)/10)*16;case Jc:return Math.floor((i+11)/12)*Math.floor((e+9)/10)*16;case Qc:return Math.floor((i+11)/12)*Math.floor((e+11)/12)*16;case Wo:case eh:case th:return Math.ceil(i/4)*Math.ceil(e/4)*16;case Yf:case nh:return Math.ceil(i/4)*Math.ceil(e/4)*8;case ih:case sh:return Math.ceil(i/4)*Math.ceil(e/4)*16}throw new Error(`Unable to determine texture byte length for ${t} format.`)}function Hy(i){switch(i){case Yi:case zf:return{byteLength:1,components:1};case Fa:case kf:case Ga:return{byteLength:2,components:1};case bh:case wh:return{byteLength:2,components:4};case qs:case Sh:case Gi:return{byteLength:4,components:1};case Hf:return{byteLength:4,components:3}}throw new Error(`Unknown texture type ${i}.`)}function Vy(i,e,t,n,s,r,a){const o=e.has("WEBGL_multisampled_render_to_texture")?e.get("WEBGL_multisampled_render_to_texture"):null,l=typeof navigator>"u"?!1:/OculusBrowser/g.test(navigator.userAgent),c=new $e,h=new WeakMap;let u;const d=new WeakMap;let f=!1;try{f=typeof OffscreenCanvas<"u"&&new OffscreenCanvas(1,1).getContext("2d")!==null}catch{}function g(D,E){return f?new OffscreenCanvas(D,E):Qo("canvas")}function _(D,E,Q){let le=1;const te=qe(D);if((te.width>Q||te.height>Q)&&(le=Q/Math.max(te.width,te.height)),le<1)if(typeof HTMLImageElement<"u"&&D instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&D instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&D instanceof ImageBitmap||typeof VideoFrame<"u"&&D instanceof VideoFrame){const X=Math.floor(le*te.width),we=Math.floor(le*te.height);u===void 0&&(u=g(X,we));const _e=E?g(X,we):u;return _e.width=X,_e.height=we,_e.getContext("2d").drawImage(D,0,0,X,we),console.warn("THREE.WebGLRenderer: Texture has been resized from ("+te.width+"x"+te.height+") to ("+X+"x"+we+")."),_e}else return"data"in D&&console.warn("THREE.WebGLRenderer: Image in DataTexture is too big ("+te.width+"x"+te.height+")."),D;return D}function p(D){return D.generateMipmaps&&D.minFilter!==ei&&D.minFilter!==hi}function m(D){i.generateMipmap(D)}function M(D,E,Q,le,te=!1){if(D!==null){if(i[D]!==void 0)return i[D];console.warn("THREE.WebGLRenderer: Attempt to use non-existing WebGL internal format '"+D+"'")}let X=E;if(E===i.RED&&(Q===i.FLOAT&&(X=i.R32F),Q===i.HALF_FLOAT&&(X=i.R16F),Q===i.UNSIGNED_BYTE&&(X=i.R8)),E===i.RED_INTEGER&&(Q===i.UNSIGNED_BYTE&&(X=i.R8UI),Q===i.UNSIGNED_SHORT&&(X=i.R16UI),Q===i.UNSIGNED_INT&&(X=i.R32UI),Q===i.BYTE&&(X=i.R8I),Q===i.SHORT&&(X=i.R16I),Q===i.INT&&(X=i.R32I)),E===i.RG&&(Q===i.FLOAT&&(X=i.RG32F),Q===i.HALF_FLOAT&&(X=i.RG16F),Q===i.UNSIGNED_BYTE&&(X=i.RG8)),E===i.RG_INTEGER&&(Q===i.UNSIGNED_BYTE&&(X=i.RG8UI),Q===i.UNSIGNED_SHORT&&(X=i.RG16UI),Q===i.UNSIGNED_INT&&(X=i.RG32UI),Q===i.BYTE&&(X=i.RG8I),Q===i.SHORT&&(X=i.RG16I),Q===i.INT&&(X=i.RG32I)),E===i.RGB&&Q===i.UNSIGNED_INT_5_9_9_9_REV&&(X=i.RGB9_E5),E===i.RGBA){const we=te?jo:bt.getTransfer(le);Q===i.FLOAT&&(X=i.RGBA32F),Q===i.HALF_FLOAT&&(X=i.RGBA16F),Q===i.UNSIGNED_BYTE&&(X=we===Ot?i.SRGB8_ALPHA8:i.RGBA8),Q===i.UNSIGNED_SHORT_4_4_4_4&&(X=i.RGBA4),Q===i.UNSIGNED_SHORT_5_5_5_1&&(X=i.RGB5_A1)}return(X===i.R16F||X===i.R32F||X===i.RG16F||X===i.RG32F||X===i.RGBA16F||X===i.RGBA32F)&&e.get("EXT_color_buffer_float"),X}function v(D,E){let Q;return D?E===null||E===qs||E===qr?Q=i.DEPTH24_STENCIL8:E===Gi?Q=i.DEPTH32F_STENCIL8:E===Fa&&(Q=i.DEPTH24_STENCIL8,console.warn("DepthTexture: 16 bit depth attachment is not supported with stencil. Using 24-bit attachment.")):E===null||E===qs||E===qr?Q=i.DEPTH_COMPONENT24:E===Gi?Q=i.DEPTH_COMPONENT32F:E===Fa&&(Q=i.DEPTH_COMPONENT16),Q}function b(D,E){return p(D)===!0||D.isFramebufferTexture&&D.minFilter!==ei&&D.minFilter!==hi?Math.log2(Math.max(E.width,E.height))+1:D.mipmaps!==void 0&&D.mipmaps.length>0?D.mipmaps.length:D.isCompressedTexture&&Array.isArray(D.image)?E.mipmaps.length:1}function N(D){const E=D.target;E.removeEventListener("dispose",N),R(E),E.isVideoTexture&&h.delete(E)}function A(D){const E=D.target;E.removeEventListener("dispose",A),w(E)}function R(D){const E=n.get(D);if(E.__webglInit===void 0)return;const Q=D.source,le=d.get(Q);if(le){const te=le[E.__cacheKey];te.usedTimes--,te.usedTimes===0&&F(D),Object.keys(le).length===0&&d.delete(Q)}n.remove(D)}function F(D){const E=n.get(D);i.deleteTexture(E.__webglTexture);const Q=D.source,le=d.get(Q);delete le[E.__cacheKey],a.memory.textures--}function w(D){const E=n.get(D);if(D.depthTexture&&D.depthTexture.dispose(),D.isWebGLCubeRenderTarget)for(let le=0;le<6;le++){if(Array.isArray(E.__webglFramebuffer[le]))for(let te=0;te<E.__webglFramebuffer[le].length;te++)i.deleteFramebuffer(E.__webglFramebuffer[le][te]);else i.deleteFramebuffer(E.__webglFramebuffer[le]);E.__webglDepthbuffer&&i.deleteRenderbuffer(E.__webglDepthbuffer[le])}else{if(Array.isArray(E.__webglFramebuffer))for(let le=0;le<E.__webglFramebuffer.length;le++)i.deleteFramebuffer(E.__webglFramebuffer[le]);else i.deleteFramebuffer(E.__webglFramebuffer);if(E.__webglDepthbuffer&&i.deleteRenderbuffer(E.__webglDepthbuffer),E.__webglMultisampledFramebuffer&&i.deleteFramebuffer(E.__webglMultisampledFramebuffer),E.__webglColorRenderbuffer)for(let le=0;le<E.__webglColorRenderbuffer.length;le++)E.__webglColorRenderbuffer[le]&&i.deleteRenderbuffer(E.__webglColorRenderbuffer[le]);E.__webglDepthRenderbuffer&&i.deleteRenderbuffer(E.__webglDepthRenderbuffer)}const Q=D.textures;for(let le=0,te=Q.length;le<te;le++){const X=n.get(Q[le]);X.__webglTexture&&(i.deleteTexture(X.__webglTexture),a.memory.textures--),n.remove(Q[le])}n.remove(D)}let y=0;function P(){y=0}function K(){const D=y;return D>=s.maxTextures&&console.warn("THREE.WebGLTextures: Trying to use "+D+" texture units while this GPU supports only "+s.maxTextures),y+=1,D}function H(D){const E=[];return E.push(D.wrapS),E.push(D.wrapT),E.push(D.wrapR||0),E.push(D.magFilter),E.push(D.minFilter),E.push(D.anisotropy),E.push(D.internalFormat),E.push(D.format),E.push(D.type),E.push(D.generateMipmaps),E.push(D.premultiplyAlpha),E.push(D.flipY),E.push(D.unpackAlignment),E.push(D.colorSpace),E.join()}function Z(D,E){const Q=n.get(D);if(D.isVideoTexture&&wt(D),D.isRenderTargetTexture===!1&&D.version>0&&Q.__version!==D.version){const le=D.image;if(le===null)console.warn("THREE.WebGLRenderer: Texture marked for update but no image data found.");else if(le.complete===!1)console.warn("THREE.WebGLRenderer: Texture marked for update but image is incomplete");else{ye(Q,D,E);return}}t.bindTexture(i.TEXTURE_2D,Q.__webglTexture,i.TEXTURE0+E)}function q(D,E){const Q=n.get(D);if(D.version>0&&Q.__version!==D.version){ye(Q,D,E);return}t.bindTexture(i.TEXTURE_2D_ARRAY,Q.__webglTexture,i.TEXTURE0+E)}function ee(D,E){const Q=n.get(D);if(D.version>0&&Q.__version!==D.version){ye(Q,D,E);return}t.bindTexture(i.TEXTURE_3D,Q.__webglTexture,i.TEXTURE0+E)}function Y(D,E){const Q=n.get(D);if(D.version>0&&Q.__version!==D.version){ie(Q,D,E);return}t.bindTexture(i.TEXTURE_CUBE_MAP,Q.__webglTexture,i.TEXTURE0+E)}const ne={[Lc]:i.REPEAT,[ks]:i.CLAMP_TO_EDGE,[Dc]:i.MIRRORED_REPEAT},ge={[ei]:i.NEAREST,[gg]:i.NEAREST_MIPMAP_NEAREST,[io]:i.NEAREST_MIPMAP_LINEAR,[hi]:i.LINEAR,[kl]:i.LINEAR_MIPMAP_NEAREST,[Hs]:i.LINEAR_MIPMAP_LINEAR},de={[yg]:i.NEVER,[Tg]:i.ALWAYS,[Mg]:i.LESS,[Kf]:i.LEQUAL,[Sg]:i.EQUAL,[Eg]:i.GEQUAL,[bg]:i.GREATER,[wg]:i.NOTEQUAL};function ve(D,E){if(E.type===Gi&&e.has("OES_texture_float_linear")===!1&&(E.magFilter===hi||E.magFilter===kl||E.magFilter===io||E.magFilter===Hs||E.minFilter===hi||E.minFilter===kl||E.minFilter===io||E.minFilter===Hs)&&console.warn("THREE.WebGLRenderer: Unable to use linear filtering with floating point textures. OES_texture_float_linear not supported on this device."),i.texParameteri(D,i.TEXTURE_WRAP_S,ne[E.wrapS]),i.texParameteri(D,i.TEXTURE_WRAP_T,ne[E.wrapT]),(D===i.TEXTURE_3D||D===i.TEXTURE_2D_ARRAY)&&i.texParameteri(D,i.TEXTURE_WRAP_R,ne[E.wrapR]),i.texParameteri(D,i.TEXTURE_MAG_FILTER,ge[E.magFilter]),i.texParameteri(D,i.TEXTURE_MIN_FILTER,ge[E.minFilter]),E.compareFunction&&(i.texParameteri(D,i.TEXTURE_COMPARE_MODE,i.COMPARE_REF_TO_TEXTURE),i.texParameteri(D,i.TEXTURE_COMPARE_FUNC,de[E.compareFunction])),e.has("EXT_texture_filter_anisotropic")===!0){if(E.magFilter===ei||E.minFilter!==io&&E.minFilter!==Hs||E.type===Gi&&e.has("OES_texture_float_linear")===!1)return;if(E.anisotropy>1||n.get(E).__currentAnisotropy){const Q=e.get("EXT_texture_filter_anisotropic");i.texParameterf(D,Q.TEXTURE_MAX_ANISOTROPY_EXT,Math.min(E.anisotropy,s.getMaxAnisotropy())),n.get(E).__currentAnisotropy=E.anisotropy}}}function Te(D,E){let Q=!1;D.__webglInit===void 0&&(D.__webglInit=!0,E.addEventListener("dispose",N));const le=E.source;let te=d.get(le);te===void 0&&(te={},d.set(le,te));const X=H(E);if(X!==D.__cacheKey){te[X]===void 0&&(te[X]={texture:i.createTexture(),usedTimes:0},a.memory.textures++,Q=!0),te[X].usedTimes++;const we=te[D.__cacheKey];we!==void 0&&(te[D.__cacheKey].usedTimes--,we.usedTimes===0&&F(E)),D.__cacheKey=X,D.__webglTexture=te[X].texture}return Q}function ye(D,E,Q){let le=i.TEXTURE_2D;(E.isDataArrayTexture||E.isCompressedArrayTexture)&&(le=i.TEXTURE_2D_ARRAY),E.isData3DTexture&&(le=i.TEXTURE_3D);const te=Te(D,E),X=E.source;t.bindTexture(le,D.__webglTexture,i.TEXTURE0+Q);const we=n.get(X);if(X.version!==we.__version||te===!0){t.activeTexture(i.TEXTURE0+Q);const _e=bt.getPrimaries(bt.workingColorSpace),Re=E.colorSpace===us?null:bt.getPrimaries(E.colorSpace),Ze=E.colorSpace===us||_e===Re?i.NONE:i.BROWSER_DEFAULT_WEBGL;i.pixelStorei(i.UNPACK_FLIP_Y_WEBGL,E.flipY),i.pixelStorei(i.UNPACK_PREMULTIPLY_ALPHA_WEBGL,E.premultiplyAlpha),i.pixelStorei(i.UNPACK_ALIGNMENT,E.unpackAlignment),i.pixelStorei(i.UNPACK_COLORSPACE_CONVERSION_WEBGL,Ze);let me=_(E.image,!1,s.maxTextureSize);me=Ye(E,me);const Ae=r.convert(E.format,E.colorSpace),Je=r.convert(E.type);let ke=M(E.internalFormat,Ae,Je,E.colorSpace,E.isVideoTexture);ve(le,E);let be;const He=E.mipmaps,B=E.isVideoTexture!==!0,ce=we.__version===void 0||te===!0,U=X.dataReady,ae=b(E,me);if(E.isDepthTexture)ke=v(E.format===$r,E.type),ce&&(B?t.texStorage2D(i.TEXTURE_2D,1,ke,me.width,me.height):t.texImage2D(i.TEXTURE_2D,0,ke,me.width,me.height,0,Ae,Je,null));else if(E.isDataTexture)if(He.length>0){B&&ce&&t.texStorage2D(i.TEXTURE_2D,ae,ke,He[0].width,He[0].height);for(let se=0,re=He.length;se<re;se++)be=He[se],B?U&&t.texSubImage2D(i.TEXTURE_2D,se,0,0,be.width,be.height,Ae,Je,be.data):t.texImage2D(i.TEXTURE_2D,se,ke,be.width,be.height,0,Ae,Je,be.data);E.generateMipmaps=!1}else B?(ce&&t.texStorage2D(i.TEXTURE_2D,ae,ke,me.width,me.height),U&&t.texSubImage2D(i.TEXTURE_2D,0,0,0,me.width,me.height,Ae,Je,me.data)):t.texImage2D(i.TEXTURE_2D,0,ke,me.width,me.height,0,Ae,Je,me.data);else if(E.isCompressedTexture)if(E.isCompressedArrayTexture){B&&ce&&t.texStorage3D(i.TEXTURE_2D_ARRAY,ae,ke,He[0].width,He[0].height,me.depth);for(let se=0,re=He.length;se<re;se++)if(be=He[se],E.format!==fi)if(Ae!==null)if(B){if(U)if(E.layerUpdates.size>0){const xe=yd(be.width,be.height,E.format,E.type);for(const Ke of E.layerUpdates){const ot=be.data.subarray(Ke*xe/be.data.BYTES_PER_ELEMENT,(Ke+1)*xe/be.data.BYTES_PER_ELEMENT);t.compressedTexSubImage3D(i.TEXTURE_2D_ARRAY,se,0,0,Ke,be.width,be.height,1,Ae,ot,0,0)}E.clearLayerUpdates()}else t.compressedTexSubImage3D(i.TEXTURE_2D_ARRAY,se,0,0,0,be.width,be.height,me.depth,Ae,be.data,0,0)}else t.compressedTexImage3D(i.TEXTURE_2D_ARRAY,se,ke,be.width,be.height,me.depth,0,be.data,0,0);else console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()");else B?U&&t.texSubImage3D(i.TEXTURE_2D_ARRAY,se,0,0,0,be.width,be.height,me.depth,Ae,Je,be.data):t.texImage3D(i.TEXTURE_2D_ARRAY,se,ke,be.width,be.height,me.depth,0,Ae,Je,be.data)}else{B&&ce&&t.texStorage2D(i.TEXTURE_2D,ae,ke,He[0].width,He[0].height);for(let se=0,re=He.length;se<re;se++)be=He[se],E.format!==fi?Ae!==null?B?U&&t.compressedTexSubImage2D(i.TEXTURE_2D,se,0,0,be.width,be.height,Ae,be.data):t.compressedTexImage2D(i.TEXTURE_2D,se,ke,be.width,be.height,0,be.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()"):B?U&&t.texSubImage2D(i.TEXTURE_2D,se,0,0,be.width,be.height,Ae,Je,be.data):t.texImage2D(i.TEXTURE_2D,se,ke,be.width,be.height,0,Ae,Je,be.data)}else if(E.isDataArrayTexture)if(B){if(ce&&t.texStorage3D(i.TEXTURE_2D_ARRAY,ae,ke,me.width,me.height,me.depth),U)if(E.layerUpdates.size>0){const se=yd(me.width,me.height,E.format,E.type);for(const re of E.layerUpdates){const xe=me.data.subarray(re*se/me.data.BYTES_PER_ELEMENT,(re+1)*se/me.data.BYTES_PER_ELEMENT);t.texSubImage3D(i.TEXTURE_2D_ARRAY,0,0,0,re,me.width,me.height,1,Ae,Je,xe)}E.clearLayerUpdates()}else t.texSubImage3D(i.TEXTURE_2D_ARRAY,0,0,0,0,me.width,me.height,me.depth,Ae,Je,me.data)}else t.texImage3D(i.TEXTURE_2D_ARRAY,0,ke,me.width,me.height,me.depth,0,Ae,Je,me.data);else if(E.isData3DTexture)B?(ce&&t.texStorage3D(i.TEXTURE_3D,ae,ke,me.width,me.height,me.depth),U&&t.texSubImage3D(i.TEXTURE_3D,0,0,0,0,me.width,me.height,me.depth,Ae,Je,me.data)):t.texImage3D(i.TEXTURE_3D,0,ke,me.width,me.height,me.depth,0,Ae,Je,me.data);else if(E.isFramebufferTexture){if(ce)if(B)t.texStorage2D(i.TEXTURE_2D,ae,ke,me.width,me.height);else{let se=me.width,re=me.height;for(let xe=0;xe<ae;xe++)t.texImage2D(i.TEXTURE_2D,xe,ke,se,re,0,Ae,Je,null),se>>=1,re>>=1}}else if(He.length>0){if(B&&ce){const se=qe(He[0]);t.texStorage2D(i.TEXTURE_2D,ae,ke,se.width,se.height)}for(let se=0,re=He.length;se<re;se++)be=He[se],B?U&&t.texSubImage2D(i.TEXTURE_2D,se,0,0,Ae,Je,be):t.texImage2D(i.TEXTURE_2D,se,ke,Ae,Je,be);E.generateMipmaps=!1}else if(B){if(ce){const se=qe(me);t.texStorage2D(i.TEXTURE_2D,ae,ke,se.width,se.height)}U&&t.texSubImage2D(i.TEXTURE_2D,0,0,0,Ae,Je,me)}else t.texImage2D(i.TEXTURE_2D,0,ke,Ae,Je,me);p(E)&&m(le),we.__version=X.version,E.onUpdate&&E.onUpdate(E)}D.__version=E.version}function ie(D,E,Q){if(E.image.length!==6)return;const le=Te(D,E),te=E.source;t.bindTexture(i.TEXTURE_CUBE_MAP,D.__webglTexture,i.TEXTURE0+Q);const X=n.get(te);if(te.version!==X.__version||le===!0){t.activeTexture(i.TEXTURE0+Q);const we=bt.getPrimaries(bt.workingColorSpace),_e=E.colorSpace===us?null:bt.getPrimaries(E.colorSpace),Re=E.colorSpace===us||we===_e?i.NONE:i.BROWSER_DEFAULT_WEBGL;i.pixelStorei(i.UNPACK_FLIP_Y_WEBGL,E.flipY),i.pixelStorei(i.UNPACK_PREMULTIPLY_ALPHA_WEBGL,E.premultiplyAlpha),i.pixelStorei(i.UNPACK_ALIGNMENT,E.unpackAlignment),i.pixelStorei(i.UNPACK_COLORSPACE_CONVERSION_WEBGL,Re);const Ze=E.isCompressedTexture||E.image[0].isCompressedTexture,me=E.image[0]&&E.image[0].isDataTexture,Ae=[];for(let re=0;re<6;re++)!Ze&&!me?Ae[re]=_(E.image[re],!0,s.maxCubemapSize):Ae[re]=me?E.image[re].image:E.image[re],Ae[re]=Ye(E,Ae[re]);const Je=Ae[0],ke=r.convert(E.format,E.colorSpace),be=r.convert(E.type),He=M(E.internalFormat,ke,be,E.colorSpace),B=E.isVideoTexture!==!0,ce=X.__version===void 0||le===!0,U=te.dataReady;let ae=b(E,Je);ve(i.TEXTURE_CUBE_MAP,E);let se;if(Ze){B&&ce&&t.texStorage2D(i.TEXTURE_CUBE_MAP,ae,He,Je.width,Je.height);for(let re=0;re<6;re++){se=Ae[re].mipmaps;for(let xe=0;xe<se.length;xe++){const Ke=se[xe];E.format!==fi?ke!==null?B?U&&t.compressedTexSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,xe,0,0,Ke.width,Ke.height,ke,Ke.data):t.compressedTexImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,xe,He,Ke.width,Ke.height,0,Ke.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .setTextureCube()"):B?U&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,xe,0,0,Ke.width,Ke.height,ke,be,Ke.data):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,xe,He,Ke.width,Ke.height,0,ke,be,Ke.data)}}}else{if(se=E.mipmaps,B&&ce){se.length>0&&ae++;const re=qe(Ae[0]);t.texStorage2D(i.TEXTURE_CUBE_MAP,ae,He,re.width,re.height)}for(let re=0;re<6;re++)if(me){B?U&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,0,0,0,Ae[re].width,Ae[re].height,ke,be,Ae[re].data):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,0,He,Ae[re].width,Ae[re].height,0,ke,be,Ae[re].data);for(let xe=0;xe<se.length;xe++){const ot=se[xe].image[re].image;B?U&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,xe+1,0,0,ot.width,ot.height,ke,be,ot.data):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,xe+1,He,ot.width,ot.height,0,ke,be,ot.data)}}else{B?U&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,0,0,0,ke,be,Ae[re]):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,0,He,ke,be,Ae[re]);for(let xe=0;xe<se.length;xe++){const Ke=se[xe];B?U&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,xe+1,0,0,ke,be,Ke.image[re]):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,xe+1,He,ke,be,Ke.image[re])}}}p(E)&&m(i.TEXTURE_CUBE_MAP),X.__version=te.version,E.onUpdate&&E.onUpdate(E)}D.__version=E.version}function he(D,E,Q,le,te,X){const we=r.convert(Q.format,Q.colorSpace),_e=r.convert(Q.type),Re=M(Q.internalFormat,we,_e,Q.colorSpace);if(!n.get(E).__hasExternalTextures){const me=Math.max(1,E.width>>X),Ae=Math.max(1,E.height>>X);te===i.TEXTURE_3D||te===i.TEXTURE_2D_ARRAY?t.texImage3D(te,X,Re,me,Ae,E.depth,0,we,_e,null):t.texImage2D(te,X,Re,me,Ae,0,we,_e,null)}t.bindFramebuffer(i.FRAMEBUFFER,D),Oe(E)?o.framebufferTexture2DMultisampleEXT(i.FRAMEBUFFER,le,te,n.get(Q).__webglTexture,0,ct(E)):(te===i.TEXTURE_2D||te>=i.TEXTURE_CUBE_MAP_POSITIVE_X&&te<=i.TEXTURE_CUBE_MAP_NEGATIVE_Z)&&i.framebufferTexture2D(i.FRAMEBUFFER,le,te,n.get(Q).__webglTexture,X),t.bindFramebuffer(i.FRAMEBUFFER,null)}function Me(D,E,Q){if(i.bindRenderbuffer(i.RENDERBUFFER,D),E.depthBuffer){const le=E.depthTexture,te=le&&le.isDepthTexture?le.type:null,X=v(E.stencilBuffer,te),we=E.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,_e=ct(E);Oe(E)?o.renderbufferStorageMultisampleEXT(i.RENDERBUFFER,_e,X,E.width,E.height):Q?i.renderbufferStorageMultisample(i.RENDERBUFFER,_e,X,E.width,E.height):i.renderbufferStorage(i.RENDERBUFFER,X,E.width,E.height),i.framebufferRenderbuffer(i.FRAMEBUFFER,we,i.RENDERBUFFER,D)}else{const le=E.textures;for(let te=0;te<le.length;te++){const X=le[te],we=r.convert(X.format,X.colorSpace),_e=r.convert(X.type),Re=M(X.internalFormat,we,_e,X.colorSpace),Ze=ct(E);Q&&Oe(E)===!1?i.renderbufferStorageMultisample(i.RENDERBUFFER,Ze,Re,E.width,E.height):Oe(E)?o.renderbufferStorageMultisampleEXT(i.RENDERBUFFER,Ze,Re,E.width,E.height):i.renderbufferStorage(i.RENDERBUFFER,Re,E.width,E.height)}}i.bindRenderbuffer(i.RENDERBUFFER,null)}function fe(D,E){if(E&&E.isWebGLCubeRenderTarget)throw new Error("Depth Texture with cube render targets is not supported");if(t.bindFramebuffer(i.FRAMEBUFFER,D),!(E.depthTexture&&E.depthTexture.isDepthTexture))throw new Error("renderTarget.depthTexture must be an instance of THREE.DepthTexture");(!n.get(E.depthTexture).__webglTexture||E.depthTexture.image.width!==E.width||E.depthTexture.image.height!==E.height)&&(E.depthTexture.image.width=E.width,E.depthTexture.image.height=E.height,E.depthTexture.needsUpdate=!0),Z(E.depthTexture,0);const le=n.get(E.depthTexture).__webglTexture,te=ct(E);if(E.depthTexture.format===Br)Oe(E)?o.framebufferTexture2DMultisampleEXT(i.FRAMEBUFFER,i.DEPTH_ATTACHMENT,i.TEXTURE_2D,le,0,te):i.framebufferTexture2D(i.FRAMEBUFFER,i.DEPTH_ATTACHMENT,i.TEXTURE_2D,le,0);else if(E.depthTexture.format===$r)Oe(E)?o.framebufferTexture2DMultisampleEXT(i.FRAMEBUFFER,i.DEPTH_STENCIL_ATTACHMENT,i.TEXTURE_2D,le,0,te):i.framebufferTexture2D(i.FRAMEBUFFER,i.DEPTH_STENCIL_ATTACHMENT,i.TEXTURE_2D,le,0);else throw new Error("Unknown depthTexture format")}function ze(D){const E=n.get(D),Q=D.isWebGLCubeRenderTarget===!0;if(E.__boundDepthTexture!==D.depthTexture){const le=D.depthTexture;if(E.__depthDisposeCallback&&E.__depthDisposeCallback(),le){const te=()=>{delete E.__boundDepthTexture,delete E.__depthDisposeCallback,le.removeEventListener("dispose",te)};le.addEventListener("dispose",te),E.__depthDisposeCallback=te}E.__boundDepthTexture=le}if(D.depthTexture&&!E.__autoAllocateDepthBuffer){if(Q)throw new Error("target.depthTexture not supported in Cube render targets");fe(E.__webglFramebuffer,D)}else if(Q){E.__webglDepthbuffer=[];for(let le=0;le<6;le++)if(t.bindFramebuffer(i.FRAMEBUFFER,E.__webglFramebuffer[le]),E.__webglDepthbuffer[le]===void 0)E.__webglDepthbuffer[le]=i.createRenderbuffer(),Me(E.__webglDepthbuffer[le],D,!1);else{const te=D.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,X=E.__webglDepthbuffer[le];i.bindRenderbuffer(i.RENDERBUFFER,X),i.framebufferRenderbuffer(i.FRAMEBUFFER,te,i.RENDERBUFFER,X)}}else if(t.bindFramebuffer(i.FRAMEBUFFER,E.__webglFramebuffer),E.__webglDepthbuffer===void 0)E.__webglDepthbuffer=i.createRenderbuffer(),Me(E.__webglDepthbuffer,D,!1);else{const le=D.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,te=E.__webglDepthbuffer;i.bindRenderbuffer(i.RENDERBUFFER,te),i.framebufferRenderbuffer(i.FRAMEBUFFER,le,i.RENDERBUFFER,te)}t.bindFramebuffer(i.FRAMEBUFFER,null)}function Ge(D,E,Q){const le=n.get(D);E!==void 0&&he(le.__webglFramebuffer,D,D.texture,i.COLOR_ATTACHMENT0,i.TEXTURE_2D,0),Q!==void 0&&ze(D)}function Fe(D){const E=D.texture,Q=n.get(D),le=n.get(E);D.addEventListener("dispose",A);const te=D.textures,X=D.isWebGLCubeRenderTarget===!0,we=te.length>1;if(we||(le.__webglTexture===void 0&&(le.__webglTexture=i.createTexture()),le.__version=E.version,a.memory.textures++),X){Q.__webglFramebuffer=[];for(let _e=0;_e<6;_e++)if(E.mipmaps&&E.mipmaps.length>0){Q.__webglFramebuffer[_e]=[];for(let Re=0;Re<E.mipmaps.length;Re++)Q.__webglFramebuffer[_e][Re]=i.createFramebuffer()}else Q.__webglFramebuffer[_e]=i.createFramebuffer()}else{if(E.mipmaps&&E.mipmaps.length>0){Q.__webglFramebuffer=[];for(let _e=0;_e<E.mipmaps.length;_e++)Q.__webglFramebuffer[_e]=i.createFramebuffer()}else Q.__webglFramebuffer=i.createFramebuffer();if(we)for(let _e=0,Re=te.length;_e<Re;_e++){const Ze=n.get(te[_e]);Ze.__webglTexture===void 0&&(Ze.__webglTexture=i.createTexture(),a.memory.textures++)}if(D.samples>0&&Oe(D)===!1){Q.__webglMultisampledFramebuffer=i.createFramebuffer(),Q.__webglColorRenderbuffer=[],t.bindFramebuffer(i.FRAMEBUFFER,Q.__webglMultisampledFramebuffer);for(let _e=0;_e<te.length;_e++){const Re=te[_e];Q.__webglColorRenderbuffer[_e]=i.createRenderbuffer(),i.bindRenderbuffer(i.RENDERBUFFER,Q.__webglColorRenderbuffer[_e]);const Ze=r.convert(Re.format,Re.colorSpace),me=r.convert(Re.type),Ae=M(Re.internalFormat,Ze,me,Re.colorSpace,D.isXRRenderTarget===!0),Je=ct(D);i.renderbufferStorageMultisample(i.RENDERBUFFER,Je,Ae,D.width,D.height),i.framebufferRenderbuffer(i.FRAMEBUFFER,i.COLOR_ATTACHMENT0+_e,i.RENDERBUFFER,Q.__webglColorRenderbuffer[_e])}i.bindRenderbuffer(i.RENDERBUFFER,null),D.depthBuffer&&(Q.__webglDepthRenderbuffer=i.createRenderbuffer(),Me(Q.__webglDepthRenderbuffer,D,!0)),t.bindFramebuffer(i.FRAMEBUFFER,null)}}if(X){t.bindTexture(i.TEXTURE_CUBE_MAP,le.__webglTexture),ve(i.TEXTURE_CUBE_MAP,E);for(let _e=0;_e<6;_e++)if(E.mipmaps&&E.mipmaps.length>0)for(let Re=0;Re<E.mipmaps.length;Re++)he(Q.__webglFramebuffer[_e][Re],D,E,i.COLOR_ATTACHMENT0,i.TEXTURE_CUBE_MAP_POSITIVE_X+_e,Re);else he(Q.__webglFramebuffer[_e],D,E,i.COLOR_ATTACHMENT0,i.TEXTURE_CUBE_MAP_POSITIVE_X+_e,0);p(E)&&m(i.TEXTURE_CUBE_MAP),t.unbindTexture()}else if(we){for(let _e=0,Re=te.length;_e<Re;_e++){const Ze=te[_e],me=n.get(Ze);t.bindTexture(i.TEXTURE_2D,me.__webglTexture),ve(i.TEXTURE_2D,Ze),he(Q.__webglFramebuffer,D,Ze,i.COLOR_ATTACHMENT0+_e,i.TEXTURE_2D,0),p(Ze)&&m(i.TEXTURE_2D)}t.unbindTexture()}else{let _e=i.TEXTURE_2D;if((D.isWebGL3DRenderTarget||D.isWebGLArrayRenderTarget)&&(_e=D.isWebGL3DRenderTarget?i.TEXTURE_3D:i.TEXTURE_2D_ARRAY),t.bindTexture(_e,le.__webglTexture),ve(_e,E),E.mipmaps&&E.mipmaps.length>0)for(let Re=0;Re<E.mipmaps.length;Re++)he(Q.__webglFramebuffer[Re],D,E,i.COLOR_ATTACHMENT0,_e,Re);else he(Q.__webglFramebuffer,D,E,i.COLOR_ATTACHMENT0,_e,0);p(E)&&m(_e),t.unbindTexture()}D.depthBuffer&&ze(D)}function pt(D){const E=D.textures;for(let Q=0,le=E.length;Q<le;Q++){const te=E[Q];if(p(te)){const X=D.isWebGLCubeRenderTarget?i.TEXTURE_CUBE_MAP:i.TEXTURE_2D,we=n.get(te).__webglTexture;t.bindTexture(X,we),m(X),t.unbindTexture()}}}const O=[],dt=[];function st(D){if(D.samples>0){if(Oe(D)===!1){const E=D.textures,Q=D.width,le=D.height;let te=i.COLOR_BUFFER_BIT;const X=D.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,we=n.get(D),_e=E.length>1;if(_e)for(let Re=0;Re<E.length;Re++)t.bindFramebuffer(i.FRAMEBUFFER,we.__webglMultisampledFramebuffer),i.framebufferRenderbuffer(i.FRAMEBUFFER,i.COLOR_ATTACHMENT0+Re,i.RENDERBUFFER,null),t.bindFramebuffer(i.FRAMEBUFFER,we.__webglFramebuffer),i.framebufferTexture2D(i.DRAW_FRAMEBUFFER,i.COLOR_ATTACHMENT0+Re,i.TEXTURE_2D,null,0);t.bindFramebuffer(i.READ_FRAMEBUFFER,we.__webglMultisampledFramebuffer),t.bindFramebuffer(i.DRAW_FRAMEBUFFER,we.__webglFramebuffer);for(let Re=0;Re<E.length;Re++){if(D.resolveDepthBuffer&&(D.depthBuffer&&(te|=i.DEPTH_BUFFER_BIT),D.stencilBuffer&&D.resolveStencilBuffer&&(te|=i.STENCIL_BUFFER_BIT)),_e){i.framebufferRenderbuffer(i.READ_FRAMEBUFFER,i.COLOR_ATTACHMENT0,i.RENDERBUFFER,we.__webglColorRenderbuffer[Re]);const Ze=n.get(E[Re]).__webglTexture;i.framebufferTexture2D(i.DRAW_FRAMEBUFFER,i.COLOR_ATTACHMENT0,i.TEXTURE_2D,Ze,0)}i.blitFramebuffer(0,0,Q,le,0,0,Q,le,te,i.NEAREST),l===!0&&(O.length=0,dt.length=0,O.push(i.COLOR_ATTACHMENT0+Re),D.depthBuffer&&D.resolveDepthBuffer===!1&&(O.push(X),dt.push(X),i.invalidateFramebuffer(i.DRAW_FRAMEBUFFER,dt)),i.invalidateFramebuffer(i.READ_FRAMEBUFFER,O))}if(t.bindFramebuffer(i.READ_FRAMEBUFFER,null),t.bindFramebuffer(i.DRAW_FRAMEBUFFER,null),_e)for(let Re=0;Re<E.length;Re++){t.bindFramebuffer(i.FRAMEBUFFER,we.__webglMultisampledFramebuffer),i.framebufferRenderbuffer(i.FRAMEBUFFER,i.COLOR_ATTACHMENT0+Re,i.RENDERBUFFER,we.__webglColorRenderbuffer[Re]);const Ze=n.get(E[Re]).__webglTexture;t.bindFramebuffer(i.FRAMEBUFFER,we.__webglFramebuffer),i.framebufferTexture2D(i.DRAW_FRAMEBUFFER,i.COLOR_ATTACHMENT0+Re,i.TEXTURE_2D,Ze,0)}t.bindFramebuffer(i.DRAW_FRAMEBUFFER,we.__webglMultisampledFramebuffer)}else if(D.depthBuffer&&D.resolveDepthBuffer===!1&&l){const E=D.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT;i.invalidateFramebuffer(i.DRAW_FRAMEBUFFER,[E])}}}function ct(D){return Math.min(s.maxSamples,D.samples)}function Oe(D){const E=n.get(D);return D.samples>0&&e.has("WEBGL_multisampled_render_to_texture")===!0&&E.__useRenderToTexture!==!1}function wt(D){const E=a.render.frame;h.get(D)!==E&&(h.set(D,E),D.update())}function Ye(D,E){const Q=D.colorSpace,le=D.format,te=D.type;return D.isCompressedTexture===!0||D.isVideoTexture===!0||Q!==Ms&&Q!==us&&(bt.getTransfer(Q)===Ot?(le!==fi||te!==Yi)&&console.warn("THREE.WebGLTextures: sRGB encoded textures have to use RGBAFormat and UnsignedByteType."):console.error("THREE.WebGLTextures: Unsupported texture color space:",Q)),E}function qe(D){return typeof HTMLImageElement<"u"&&D instanceof HTMLImageElement?(c.width=D.naturalWidth||D.width,c.height=D.naturalHeight||D.height):typeof VideoFrame<"u"&&D instanceof VideoFrame?(c.width=D.displayWidth,c.height=D.displayHeight):(c.width=D.width,c.height=D.height),c}this.allocateTextureUnit=K,this.resetTextureUnits=P,this.setTexture2D=Z,this.setTexture2DArray=q,this.setTexture3D=ee,this.setTextureCube=Y,this.rebindTextures=Ge,this.setupRenderTarget=Fe,this.updateRenderTargetMipmap=pt,this.updateMultisampleRenderTarget=st,this.setupDepthRenderbuffer=ze,this.setupFrameBufferTexture=he,this.useMultisampledRTT=Oe}function Gy(i,e){function t(n,s=us){let r;const a=bt.getTransfer(s);if(n===Yi)return i.UNSIGNED_BYTE;if(n===bh)return i.UNSIGNED_SHORT_4_4_4_4;if(n===wh)return i.UNSIGNED_SHORT_5_5_5_1;if(n===Hf)return i.UNSIGNED_INT_5_9_9_9_REV;if(n===zf)return i.BYTE;if(n===kf)return i.SHORT;if(n===Fa)return i.UNSIGNED_SHORT;if(n===Sh)return i.INT;if(n===qs)return i.UNSIGNED_INT;if(n===Gi)return i.FLOAT;if(n===Ga)return i.HALF_FLOAT;if(n===Vf)return i.ALPHA;if(n===Gf)return i.RGB;if(n===fi)return i.RGBA;if(n===Wf)return i.LUMINANCE;if(n===Xf)return i.LUMINANCE_ALPHA;if(n===Br)return i.DEPTH_COMPONENT;if(n===$r)return i.DEPTH_STENCIL;if(n===qf)return i.RED;if(n===Eh)return i.RED_INTEGER;if(n===$f)return i.RG;if(n===Th)return i.RG_INTEGER;if(n===Ah)return i.RGBA_INTEGER;if(n===ko||n===Ho||n===Vo||n===Go)if(a===Ot)if(r=e.get("WEBGL_compressed_texture_s3tc_srgb"),r!==null){if(n===ko)return r.COMPRESSED_SRGB_S3TC_DXT1_EXT;if(n===Ho)return r.COMPRESSED_SRGB_ALPHA_S3TC_DXT1_EXT;if(n===Vo)return r.COMPRESSED_SRGB_ALPHA_S3TC_DXT3_EXT;if(n===Go)return r.COMPRESSED_SRGB_ALPHA_S3TC_DXT5_EXT}else return null;else if(r=e.get("WEBGL_compressed_texture_s3tc"),r!==null){if(n===ko)return r.COMPRESSED_RGB_S3TC_DXT1_EXT;if(n===Ho)return r.COMPRESSED_RGBA_S3TC_DXT1_EXT;if(n===Vo)return r.COMPRESSED_RGBA_S3TC_DXT3_EXT;if(n===Go)return r.COMPRESSED_RGBA_S3TC_DXT5_EXT}else return null;if(n===Ic||n===Uc||n===Nc||n===Fc)if(r=e.get("WEBGL_compressed_texture_pvrtc"),r!==null){if(n===Ic)return r.COMPRESSED_RGB_PVRTC_4BPPV1_IMG;if(n===Uc)return r.COMPRESSED_RGB_PVRTC_2BPPV1_IMG;if(n===Nc)return r.COMPRESSED_RGBA_PVRTC_4BPPV1_IMG;if(n===Fc)return r.COMPRESSED_RGBA_PVRTC_2BPPV1_IMG}else return null;if(n===Oc||n===Bc||n===zc)if(r=e.get("WEBGL_compressed_texture_etc"),r!==null){if(n===Oc||n===Bc)return a===Ot?r.COMPRESSED_SRGB8_ETC2:r.COMPRESSED_RGB8_ETC2;if(n===zc)return a===Ot?r.COMPRESSED_SRGB8_ALPHA8_ETC2_EAC:r.COMPRESSED_RGBA8_ETC2_EAC}else return null;if(n===kc||n===Hc||n===Vc||n===Gc||n===Wc||n===Xc||n===qc||n===$c||n===Yc||n===jc||n===Kc||n===Zc||n===Jc||n===Qc)if(r=e.get("WEBGL_compressed_texture_astc"),r!==null){if(n===kc)return a===Ot?r.COMPRESSED_SRGB8_ALPHA8_ASTC_4x4_KHR:r.COMPRESSED_RGBA_ASTC_4x4_KHR;if(n===Hc)return a===Ot?r.COMPRESSED_SRGB8_ALPHA8_ASTC_5x4_KHR:r.COMPRESSED_RGBA_ASTC_5x4_KHR;if(n===Vc)return a===Ot?r.COMPRESSED_SRGB8_ALPHA8_ASTC_5x5_KHR:r.COMPRESSED_RGBA_ASTC_5x5_KHR;if(n===Gc)return a===Ot?r.COMPRESSED_SRGB8_ALPHA8_ASTC_6x5_KHR:r.COMPRESSED_RGBA_ASTC_6x5_KHR;if(n===Wc)return a===Ot?r.COMPRESSED_SRGB8_ALPHA8_ASTC_6x6_KHR:r.COMPRESSED_RGBA_ASTC_6x6_KHR;if(n===Xc)return a===Ot?r.COMPRESSED_SRGB8_ALPHA8_ASTC_8x5_KHR:r.COMPRESSED_RGBA_ASTC_8x5_KHR;if(n===qc)return a===Ot?r.COMPRESSED_SRGB8_ALPHA8_ASTC_8x6_KHR:r.COMPRESSED_RGBA_ASTC_8x6_KHR;if(n===$c)return a===Ot?r.COMPRESSED_SRGB8_ALPHA8_ASTC_8x8_KHR:r.COMPRESSED_RGBA_ASTC_8x8_KHR;if(n===Yc)return a===Ot?r.COMPRESSED_SRGB8_ALPHA8_ASTC_10x5_KHR:r.COMPRESSED_RGBA_ASTC_10x5_KHR;if(n===jc)return a===Ot?r.COMPRESSED_SRGB8_ALPHA8_ASTC_10x6_KHR:r.COMPRESSED_RGBA_ASTC_10x6_KHR;if(n===Kc)return a===Ot?r.COMPRESSED_SRGB8_ALPHA8_ASTC_10x8_KHR:r.COMPRESSED_RGBA_ASTC_10x8_KHR;if(n===Zc)return a===Ot?r.COMPRESSED_SRGB8_ALPHA8_ASTC_10x10_KHR:r.COMPRESSED_RGBA_ASTC_10x10_KHR;if(n===Jc)return a===Ot?r.COMPRESSED_SRGB8_ALPHA8_ASTC_12x10_KHR:r.COMPRESSED_RGBA_ASTC_12x10_KHR;if(n===Qc)return a===Ot?r.COMPRESSED_SRGB8_ALPHA8_ASTC_12x12_KHR:r.COMPRESSED_RGBA_ASTC_12x12_KHR}else return null;if(n===Wo||n===eh||n===th)if(r=e.get("EXT_texture_compression_bptc"),r!==null){if(n===Wo)return a===Ot?r.COMPRESSED_SRGB_ALPHA_BPTC_UNORM_EXT:r.COMPRESSED_RGBA_BPTC_UNORM_EXT;if(n===eh)return r.COMPRESSED_RGB_BPTC_SIGNED_FLOAT_EXT;if(n===th)return r.COMPRESSED_RGB_BPTC_UNSIGNED_FLOAT_EXT}else return null;if(n===Yf||n===nh||n===ih||n===sh)if(r=e.get("EXT_texture_compression_rgtc"),r!==null){if(n===Wo)return r.COMPRESSED_RED_RGTC1_EXT;if(n===nh)return r.COMPRESSED_SIGNED_RED_RGTC1_EXT;if(n===ih)return r.COMPRESSED_RED_GREEN_RGTC2_EXT;if(n===sh)return r.COMPRESSED_SIGNED_RED_GREEN_RGTC2_EXT}else return null;return n===qr?i.UNSIGNED_INT_24_8:i[n]!==void 0?i[n]:null}return{convert:t}}class Wy extends bn{constructor(e=[]){super(),this.isArrayCamera=!0,this.cameras=e}}class Ti extends en{constructor(){super(),this.isGroup=!0,this.type="Group"}}const Xy={type:"move"};class uc{constructor(){this._targetRay=null,this._grip=null,this._hand=null}getHandSpace(){return this._hand===null&&(this._hand=new Ti,this._hand.matrixAutoUpdate=!1,this._hand.visible=!1,this._hand.joints={},this._hand.inputState={pinching:!1}),this._hand}getTargetRaySpace(){return this._targetRay===null&&(this._targetRay=new Ti,this._targetRay.matrixAutoUpdate=!1,this._targetRay.visible=!1,this._targetRay.hasLinearVelocity=!1,this._targetRay.linearVelocity=new V,this._targetRay.hasAngularVelocity=!1,this._targetRay.angularVelocity=new V),this._targetRay}getGripSpace(){return this._grip===null&&(this._grip=new Ti,this._grip.matrixAutoUpdate=!1,this._grip.visible=!1,this._grip.hasLinearVelocity=!1,this._grip.linearVelocity=new V,this._grip.hasAngularVelocity=!1,this._grip.angularVelocity=new V),this._grip}dispatchEvent(e){return this._targetRay!==null&&this._targetRay.dispatchEvent(e),this._grip!==null&&this._grip.dispatchEvent(e),this._hand!==null&&this._hand.dispatchEvent(e),this}connect(e){if(e&&e.hand){const t=this._hand;if(t)for(const n of e.hand.values())this._getHandJoint(t,n)}return this.dispatchEvent({type:"connected",data:e}),this}disconnect(e){return this.dispatchEvent({type:"disconnected",data:e}),this._targetRay!==null&&(this._targetRay.visible=!1),this._grip!==null&&(this._grip.visible=!1),this._hand!==null&&(this._hand.visible=!1),this}update(e,t,n){let s=null,r=null,a=null;const o=this._targetRay,l=this._grip,c=this._hand;if(e&&t.session.visibilityState!=="visible-blurred"){if(c&&e.hand){a=!0;for(const _ of e.hand.values()){const p=t.getJointPose(_,n),m=this._getHandJoint(c,_);p!==null&&(m.matrix.fromArray(p.transform.matrix),m.matrix.decompose(m.position,m.rotation,m.scale),m.matrixWorldNeedsUpdate=!0,m.jointRadius=p.radius),m.visible=p!==null}const h=c.joints["index-finger-tip"],u=c.joints["thumb-tip"],d=h.position.distanceTo(u.position),f=.02,g=.005;c.inputState.pinching&&d>f+g?(c.inputState.pinching=!1,this.dispatchEvent({type:"pinchend",handedness:e.handedness,target:this})):!c.inputState.pinching&&d<=f-g&&(c.inputState.pinching=!0,this.dispatchEvent({type:"pinchstart",handedness:e.handedness,target:this}))}else l!==null&&e.gripSpace&&(r=t.getPose(e.gripSpace,n),r!==null&&(l.matrix.fromArray(r.transform.matrix),l.matrix.decompose(l.position,l.rotation,l.scale),l.matrixWorldNeedsUpdate=!0,r.linearVelocity?(l.hasLinearVelocity=!0,l.linearVelocity.copy(r.linearVelocity)):l.hasLinearVelocity=!1,r.angularVelocity?(l.hasAngularVelocity=!0,l.angularVelocity.copy(r.angularVelocity)):l.hasAngularVelocity=!1));o!==null&&(s=t.getPose(e.targetRaySpace,n),s===null&&r!==null&&(s=r),s!==null&&(o.matrix.fromArray(s.transform.matrix),o.matrix.decompose(o.position,o.rotation,o.scale),o.matrixWorldNeedsUpdate=!0,s.linearVelocity?(o.hasLinearVelocity=!0,o.linearVelocity.copy(s.linearVelocity)):o.hasLinearVelocity=!1,s.angularVelocity?(o.hasAngularVelocity=!0,o.angularVelocity.copy(s.angularVelocity)):o.hasAngularVelocity=!1,this.dispatchEvent(Xy)))}return o!==null&&(o.visible=s!==null),l!==null&&(l.visible=r!==null),c!==null&&(c.visible=a!==null),this}_getHandJoint(e,t){if(e.joints[t.jointName]===void 0){const n=new Ti;n.matrixAutoUpdate=!1,n.visible=!1,e.joints[t.jointName]=n,e.add(n)}return e.joints[t.jointName]}}const qy=`
void main() {

	gl_Position = vec4( position, 1.0 );

}`,$y=`
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

}`;class Yy{constructor(){this.texture=null,this.mesh=null,this.depthNear=0,this.depthFar=0}init(e,t,n){if(this.texture===null){const s=new Ln,r=e.properties.get(s);r.__webglTexture=t.texture,(t.depthNear!=n.depthNear||t.depthFar!=n.depthFar)&&(this.depthNear=t.depthNear,this.depthFar=t.depthFar),this.texture=s}}getMesh(e){if(this.texture!==null&&this.mesh===null){const t=e.cameras[0].viewport,n=new _s({vertexShader:qy,fragmentShader:$y,uniforms:{depthColor:{value:this.texture},depthWidth:{value:t.z},depthHeight:{value:t.w}}});this.mesh=new Qt(new $a(20,20),n)}return this.mesh}reset(){this.texture=null,this.mesh=null}getDepthTexture(){return this.texture}}class jy extends ta{constructor(e,t){super();const n=this;let s=null,r=1,a=null,o="local-floor",l=1,c=null,h=null,u=null,d=null,f=null,g=null;const _=new Yy,p=t.getContextAttributes();let m=null,M=null;const v=[],b=[],N=new $e;let A=null;const R=new bn;R.layers.enable(1),R.viewport=new sn;const F=new bn;F.layers.enable(2),F.viewport=new sn;const w=[R,F],y=new Wy;y.layers.enable(1),y.layers.enable(2);let P=null,K=null;this.cameraAutoUpdate=!0,this.enabled=!1,this.isPresenting=!1,this.getController=function(ie){let he=v[ie];return he===void 0&&(he=new uc,v[ie]=he),he.getTargetRaySpace()},this.getControllerGrip=function(ie){let he=v[ie];return he===void 0&&(he=new uc,v[ie]=he),he.getGripSpace()},this.getHand=function(ie){let he=v[ie];return he===void 0&&(he=new uc,v[ie]=he),he.getHandSpace()};function H(ie){const he=b.indexOf(ie.inputSource);if(he===-1)return;const Me=v[he];Me!==void 0&&(Me.update(ie.inputSource,ie.frame,c||a),Me.dispatchEvent({type:ie.type,data:ie.inputSource}))}function Z(){s.removeEventListener("select",H),s.removeEventListener("selectstart",H),s.removeEventListener("selectend",H),s.removeEventListener("squeeze",H),s.removeEventListener("squeezestart",H),s.removeEventListener("squeezeend",H),s.removeEventListener("end",Z),s.removeEventListener("inputsourceschange",q);for(let ie=0;ie<v.length;ie++){const he=b[ie];he!==null&&(b[ie]=null,v[ie].disconnect(he))}P=null,K=null,_.reset(),e.setRenderTarget(m),f=null,d=null,u=null,s=null,M=null,ye.stop(),n.isPresenting=!1,e.setPixelRatio(A),e.setSize(N.width,N.height,!1),n.dispatchEvent({type:"sessionend"})}this.setFramebufferScaleFactor=function(ie){r=ie,n.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change framebuffer scale while presenting.")},this.setReferenceSpaceType=function(ie){o=ie,n.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change reference space type while presenting.")},this.getReferenceSpace=function(){return c||a},this.setReferenceSpace=function(ie){c=ie},this.getBaseLayer=function(){return d!==null?d:f},this.getBinding=function(){return u},this.getFrame=function(){return g},this.getSession=function(){return s},this.setSession=async function(ie){if(s=ie,s!==null){if(m=e.getRenderTarget(),s.addEventListener("select",H),s.addEventListener("selectstart",H),s.addEventListener("selectend",H),s.addEventListener("squeeze",H),s.addEventListener("squeezestart",H),s.addEventListener("squeezeend",H),s.addEventListener("end",Z),s.addEventListener("inputsourceschange",q),p.xrCompatible!==!0&&await t.makeXRCompatible(),A=e.getPixelRatio(),e.getSize(N),s.renderState.layers===void 0){const he={antialias:p.antialias,alpha:!0,depth:p.depth,stencil:p.stencil,framebufferScaleFactor:r};f=new XRWebGLLayer(s,t,he),s.updateRenderState({baseLayer:f}),e.setPixelRatio(1),e.setSize(f.framebufferWidth,f.framebufferHeight,!1),M=new $s(f.framebufferWidth,f.framebufferHeight,{format:fi,type:Yi,colorSpace:e.outputColorSpace,stencilBuffer:p.stencil})}else{let he=null,Me=null,fe=null;p.depth&&(fe=p.stencil?t.DEPTH24_STENCIL8:t.DEPTH_COMPONENT24,he=p.stencil?$r:Br,Me=p.stencil?qr:qs);const ze={colorFormat:t.RGBA8,depthFormat:fe,scaleFactor:r};u=new XRWebGLBinding(s,t),d=u.createProjectionLayer(ze),s.updateRenderState({layers:[d]}),e.setPixelRatio(1),e.setSize(d.textureWidth,d.textureHeight,!1),M=new $s(d.textureWidth,d.textureHeight,{format:fi,type:Yi,depthTexture:new op(d.textureWidth,d.textureHeight,Me,void 0,void 0,void 0,void 0,void 0,void 0,he),stencilBuffer:p.stencil,colorSpace:e.outputColorSpace,samples:p.antialias?4:0,resolveDepthBuffer:d.ignoreDepthValues===!1})}M.isXRRenderTarget=!0,this.setFoveation(l),c=null,a=await s.requestReferenceSpace(o),ye.setContext(s),ye.start(),n.isPresenting=!0,n.dispatchEvent({type:"sessionstart"})}},this.getEnvironmentBlendMode=function(){if(s!==null)return s.environmentBlendMode},this.getDepthTexture=function(){return _.getDepthTexture()};function q(ie){for(let he=0;he<ie.removed.length;he++){const Me=ie.removed[he],fe=b.indexOf(Me);fe>=0&&(b[fe]=null,v[fe].disconnect(Me))}for(let he=0;he<ie.added.length;he++){const Me=ie.added[he];let fe=b.indexOf(Me);if(fe===-1){for(let Ge=0;Ge<v.length;Ge++)if(Ge>=b.length){b.push(Me),fe=Ge;break}else if(b[Ge]===null){b[Ge]=Me,fe=Ge;break}if(fe===-1)break}const ze=v[fe];ze&&ze.connect(Me)}}const ee=new V,Y=new V;function ne(ie,he,Me){ee.setFromMatrixPosition(he.matrixWorld),Y.setFromMatrixPosition(Me.matrixWorld);const fe=ee.distanceTo(Y),ze=he.projectionMatrix.elements,Ge=Me.projectionMatrix.elements,Fe=ze[14]/(ze[10]-1),pt=ze[14]/(ze[10]+1),O=(ze[9]+1)/ze[5],dt=(ze[9]-1)/ze[5],st=(ze[8]-1)/ze[0],ct=(Ge[8]+1)/Ge[0],Oe=Fe*st,wt=Fe*ct,Ye=fe/(-st+ct),qe=Ye*-st;if(he.matrixWorld.decompose(ie.position,ie.quaternion,ie.scale),ie.translateX(qe),ie.translateZ(Ye),ie.matrixWorld.compose(ie.position,ie.quaternion,ie.scale),ie.matrixWorldInverse.copy(ie.matrixWorld).invert(),ze[10]===-1)ie.projectionMatrix.copy(he.projectionMatrix),ie.projectionMatrixInverse.copy(he.projectionMatrixInverse);else{const D=Fe+Ye,E=pt+Ye,Q=Oe-qe,le=wt+(fe-qe),te=O*pt/E*D,X=dt*pt/E*D;ie.projectionMatrix.makePerspective(Q,le,te,X,D,E),ie.projectionMatrixInverse.copy(ie.projectionMatrix).invert()}}function ge(ie,he){he===null?ie.matrixWorld.copy(ie.matrix):ie.matrixWorld.multiplyMatrices(he.matrixWorld,ie.matrix),ie.matrixWorldInverse.copy(ie.matrixWorld).invert()}this.updateCamera=function(ie){if(s===null)return;let he=ie.near,Me=ie.far;_.texture!==null&&(_.depthNear>0&&(he=_.depthNear),_.depthFar>0&&(Me=_.depthFar)),y.near=F.near=R.near=he,y.far=F.far=R.far=Me,(P!==y.near||K!==y.far)&&(s.updateRenderState({depthNear:y.near,depthFar:y.far}),P=y.near,K=y.far);const fe=ie.parent,ze=y.cameras;ge(y,fe);for(let Ge=0;Ge<ze.length;Ge++)ge(ze[Ge],fe);ze.length===2?ne(y,R,F):y.projectionMatrix.copy(R.projectionMatrix),de(ie,y,fe)};function de(ie,he,Me){Me===null?ie.matrix.copy(he.matrixWorld):(ie.matrix.copy(Me.matrixWorld),ie.matrix.invert(),ie.matrix.multiply(he.matrixWorld)),ie.matrix.decompose(ie.position,ie.quaternion,ie.scale),ie.updateMatrixWorld(!0),ie.projectionMatrix.copy(he.projectionMatrix),ie.projectionMatrixInverse.copy(he.projectionMatrixInverse),ie.isPerspectiveCamera&&(ie.fov=Oa*2*Math.atan(1/ie.projectionMatrix.elements[5]),ie.zoom=1)}this.getCamera=function(){return y},this.getFoveation=function(){if(!(d===null&&f===null))return l},this.setFoveation=function(ie){l=ie,d!==null&&(d.fixedFoveation=ie),f!==null&&f.fixedFoveation!==void 0&&(f.fixedFoveation=ie)},this.hasDepthSensing=function(){return _.texture!==null},this.getDepthSensingMesh=function(){return _.getMesh(y)};let ve=null;function Te(ie,he){if(h=he.getViewerPose(c||a),g=he,h!==null){const Me=h.views;f!==null&&(e.setRenderTargetFramebuffer(M,f.framebuffer),e.setRenderTarget(M));let fe=!1;Me.length!==y.cameras.length&&(y.cameras.length=0,fe=!0);for(let Ge=0;Ge<Me.length;Ge++){const Fe=Me[Ge];let pt=null;if(f!==null)pt=f.getViewport(Fe);else{const dt=u.getViewSubImage(d,Fe);pt=dt.viewport,Ge===0&&(e.setRenderTargetTextures(M,dt.colorTexture,d.ignoreDepthValues?void 0:dt.depthStencilTexture),e.setRenderTarget(M))}let O=w[Ge];O===void 0&&(O=new bn,O.layers.enable(Ge),O.viewport=new sn,w[Ge]=O),O.matrix.fromArray(Fe.transform.matrix),O.matrix.decompose(O.position,O.quaternion,O.scale),O.projectionMatrix.fromArray(Fe.projectionMatrix),O.projectionMatrixInverse.copy(O.projectionMatrix).invert(),O.viewport.set(pt.x,pt.y,pt.width,pt.height),Ge===0&&(y.matrix.copy(O.matrix),y.matrix.decompose(y.position,y.quaternion,y.scale)),fe===!0&&y.cameras.push(O)}const ze=s.enabledFeatures;if(ze&&ze.includes("depth-sensing")){const Ge=u.getDepthInformation(Me[0]);Ge&&Ge.isValid&&Ge.texture&&_.init(e,Ge,s.renderState)}}for(let Me=0;Me<v.length;Me++){const fe=b[Me],ze=v[Me];fe!==null&&ze!==void 0&&ze.update(fe,he,c||a)}ve&&ve(ie,he),he.detectedPlanes&&n.dispatchEvent({type:"planesdetected",data:he}),g=null}const ye=new ap;ye.setAnimationLoop(Te),this.setAnimationLoop=function(ie){ve=ie},this.dispose=function(){}}}const Is=new Ci,Ky=new Bt;function Zy(i,e){function t(p,m){p.matrixAutoUpdate===!0&&p.updateMatrix(),m.value.copy(p.matrix)}function n(p,m){m.color.getRGB(p.fogColor.value,ip(i)),m.isFog?(p.fogNear.value=m.near,p.fogFar.value=m.far):m.isFogExp2&&(p.fogDensity.value=m.density)}function s(p,m,M,v,b){m.isMeshBasicMaterial||m.isMeshLambertMaterial?r(p,m):m.isMeshToonMaterial?(r(p,m),u(p,m)):m.isMeshPhongMaterial?(r(p,m),h(p,m)):m.isMeshStandardMaterial?(r(p,m),d(p,m),m.isMeshPhysicalMaterial&&f(p,m,b)):m.isMeshMatcapMaterial?(r(p,m),g(p,m)):m.isMeshDepthMaterial?r(p,m):m.isMeshDistanceMaterial?(r(p,m),_(p,m)):m.isMeshNormalMaterial?r(p,m):m.isLineBasicMaterial?(a(p,m),m.isLineDashedMaterial&&o(p,m)):m.isPointsMaterial?l(p,m,M,v):m.isSpriteMaterial?c(p,m):m.isShadowMaterial?(p.color.value.copy(m.color),p.opacity.value=m.opacity):m.isShaderMaterial&&(m.uniformsNeedUpdate=!1)}function r(p,m){p.opacity.value=m.opacity,m.color&&p.diffuse.value.copy(m.color),m.emissive&&p.emissive.value.copy(m.emissive).multiplyScalar(m.emissiveIntensity),m.map&&(p.map.value=m.map,t(m.map,p.mapTransform)),m.alphaMap&&(p.alphaMap.value=m.alphaMap,t(m.alphaMap,p.alphaMapTransform)),m.bumpMap&&(p.bumpMap.value=m.bumpMap,t(m.bumpMap,p.bumpMapTransform),p.bumpScale.value=m.bumpScale,m.side===Nn&&(p.bumpScale.value*=-1)),m.normalMap&&(p.normalMap.value=m.normalMap,t(m.normalMap,p.normalMapTransform),p.normalScale.value.copy(m.normalScale),m.side===Nn&&p.normalScale.value.negate()),m.displacementMap&&(p.displacementMap.value=m.displacementMap,t(m.displacementMap,p.displacementMapTransform),p.displacementScale.value=m.displacementScale,p.displacementBias.value=m.displacementBias),m.emissiveMap&&(p.emissiveMap.value=m.emissiveMap,t(m.emissiveMap,p.emissiveMapTransform)),m.specularMap&&(p.specularMap.value=m.specularMap,t(m.specularMap,p.specularMapTransform)),m.alphaTest>0&&(p.alphaTest.value=m.alphaTest);const M=e.get(m),v=M.envMap,b=M.envMapRotation;v&&(p.envMap.value=v,Is.copy(b),Is.x*=-1,Is.y*=-1,Is.z*=-1,v.isCubeTexture&&v.isRenderTargetTexture===!1&&(Is.y*=-1,Is.z*=-1),p.envMapRotation.value.setFromMatrix4(Ky.makeRotationFromEuler(Is)),p.flipEnvMap.value=v.isCubeTexture&&v.isRenderTargetTexture===!1?-1:1,p.reflectivity.value=m.reflectivity,p.ior.value=m.ior,p.refractionRatio.value=m.refractionRatio),m.lightMap&&(p.lightMap.value=m.lightMap,p.lightMapIntensity.value=m.lightMapIntensity,t(m.lightMap,p.lightMapTransform)),m.aoMap&&(p.aoMap.value=m.aoMap,p.aoMapIntensity.value=m.aoMapIntensity,t(m.aoMap,p.aoMapTransform))}function a(p,m){p.diffuse.value.copy(m.color),p.opacity.value=m.opacity,m.map&&(p.map.value=m.map,t(m.map,p.mapTransform))}function o(p,m){p.dashSize.value=m.dashSize,p.totalSize.value=m.dashSize+m.gapSize,p.scale.value=m.scale}function l(p,m,M,v){p.diffuse.value.copy(m.color),p.opacity.value=m.opacity,p.size.value=m.size*M,p.scale.value=v*.5,m.map&&(p.map.value=m.map,t(m.map,p.uvTransform)),m.alphaMap&&(p.alphaMap.value=m.alphaMap,t(m.alphaMap,p.alphaMapTransform)),m.alphaTest>0&&(p.alphaTest.value=m.alphaTest)}function c(p,m){p.diffuse.value.copy(m.color),p.opacity.value=m.opacity,p.rotation.value=m.rotation,m.map&&(p.map.value=m.map,t(m.map,p.mapTransform)),m.alphaMap&&(p.alphaMap.value=m.alphaMap,t(m.alphaMap,p.alphaMapTransform)),m.alphaTest>0&&(p.alphaTest.value=m.alphaTest)}function h(p,m){p.specular.value.copy(m.specular),p.shininess.value=Math.max(m.shininess,1e-4)}function u(p,m){m.gradientMap&&(p.gradientMap.value=m.gradientMap)}function d(p,m){p.metalness.value=m.metalness,m.metalnessMap&&(p.metalnessMap.value=m.metalnessMap,t(m.metalnessMap,p.metalnessMapTransform)),p.roughness.value=m.roughness,m.roughnessMap&&(p.roughnessMap.value=m.roughnessMap,t(m.roughnessMap,p.roughnessMapTransform)),m.envMap&&(p.envMapIntensity.value=m.envMapIntensity)}function f(p,m,M){p.ior.value=m.ior,m.sheen>0&&(p.sheenColor.value.copy(m.sheenColor).multiplyScalar(m.sheen),p.sheenRoughness.value=m.sheenRoughness,m.sheenColorMap&&(p.sheenColorMap.value=m.sheenColorMap,t(m.sheenColorMap,p.sheenColorMapTransform)),m.sheenRoughnessMap&&(p.sheenRoughnessMap.value=m.sheenRoughnessMap,t(m.sheenRoughnessMap,p.sheenRoughnessMapTransform))),m.clearcoat>0&&(p.clearcoat.value=m.clearcoat,p.clearcoatRoughness.value=m.clearcoatRoughness,m.clearcoatMap&&(p.clearcoatMap.value=m.clearcoatMap,t(m.clearcoatMap,p.clearcoatMapTransform)),m.clearcoatRoughnessMap&&(p.clearcoatRoughnessMap.value=m.clearcoatRoughnessMap,t(m.clearcoatRoughnessMap,p.clearcoatRoughnessMapTransform)),m.clearcoatNormalMap&&(p.clearcoatNormalMap.value=m.clearcoatNormalMap,t(m.clearcoatNormalMap,p.clearcoatNormalMapTransform),p.clearcoatNormalScale.value.copy(m.clearcoatNormalScale),m.side===Nn&&p.clearcoatNormalScale.value.negate())),m.dispersion>0&&(p.dispersion.value=m.dispersion),m.iridescence>0&&(p.iridescence.value=m.iridescence,p.iridescenceIOR.value=m.iridescenceIOR,p.iridescenceThicknessMinimum.value=m.iridescenceThicknessRange[0],p.iridescenceThicknessMaximum.value=m.iridescenceThicknessRange[1],m.iridescenceMap&&(p.iridescenceMap.value=m.iridescenceMap,t(m.iridescenceMap,p.iridescenceMapTransform)),m.iridescenceThicknessMap&&(p.iridescenceThicknessMap.value=m.iridescenceThicknessMap,t(m.iridescenceThicknessMap,p.iridescenceThicknessMapTransform))),m.transmission>0&&(p.transmission.value=m.transmission,p.transmissionSamplerMap.value=M.texture,p.transmissionSamplerSize.value.set(M.width,M.height),m.transmissionMap&&(p.transmissionMap.value=m.transmissionMap,t(m.transmissionMap,p.transmissionMapTransform)),p.thickness.value=m.thickness,m.thicknessMap&&(p.thicknessMap.value=m.thicknessMap,t(m.thicknessMap,p.thicknessMapTransform)),p.attenuationDistance.value=m.attenuationDistance,p.attenuationColor.value.copy(m.attenuationColor)),m.anisotropy>0&&(p.anisotropyVector.value.set(m.anisotropy*Math.cos(m.anisotropyRotation),m.anisotropy*Math.sin(m.anisotropyRotation)),m.anisotropyMap&&(p.anisotropyMap.value=m.anisotropyMap,t(m.anisotropyMap,p.anisotropyMapTransform))),p.specularIntensity.value=m.specularIntensity,p.specularColor.value.copy(m.specularColor),m.specularColorMap&&(p.specularColorMap.value=m.specularColorMap,t(m.specularColorMap,p.specularColorMapTransform)),m.specularIntensityMap&&(p.specularIntensityMap.value=m.specularIntensityMap,t(m.specularIntensityMap,p.specularIntensityMapTransform))}function g(p,m){m.matcap&&(p.matcap.value=m.matcap)}function _(p,m){const M=e.get(m).light;p.referencePosition.value.setFromMatrixPosition(M.matrixWorld),p.nearDistance.value=M.shadow.camera.near,p.farDistance.value=M.shadow.camera.far}return{refreshFogUniforms:n,refreshMaterialUniforms:s}}function Jy(i,e,t,n){let s={},r={},a=[];const o=i.getParameter(i.MAX_UNIFORM_BUFFER_BINDINGS);function l(M,v){const b=v.program;n.uniformBlockBinding(M,b)}function c(M,v){let b=s[M.id];b===void 0&&(g(M),b=h(M),s[M.id]=b,M.addEventListener("dispose",p));const N=v.program;n.updateUBOMapping(M,N);const A=e.render.frame;r[M.id]!==A&&(d(M),r[M.id]=A)}function h(M){const v=u();M.__bindingPointIndex=v;const b=i.createBuffer(),N=M.__size,A=M.usage;return i.bindBuffer(i.UNIFORM_BUFFER,b),i.bufferData(i.UNIFORM_BUFFER,N,A),i.bindBuffer(i.UNIFORM_BUFFER,null),i.bindBufferBase(i.UNIFORM_BUFFER,v,b),b}function u(){for(let M=0;M<o;M++)if(a.indexOf(M)===-1)return a.push(M),M;return console.error("THREE.WebGLRenderer: Maximum number of simultaneously usable uniforms groups reached."),0}function d(M){const v=s[M.id],b=M.uniforms,N=M.__cache;i.bindBuffer(i.UNIFORM_BUFFER,v);for(let A=0,R=b.length;A<R;A++){const F=Array.isArray(b[A])?b[A]:[b[A]];for(let w=0,y=F.length;w<y;w++){const P=F[w];if(f(P,A,w,N)===!0){const K=P.__offset,H=Array.isArray(P.value)?P.value:[P.value];let Z=0;for(let q=0;q<H.length;q++){const ee=H[q],Y=_(ee);typeof ee=="number"||typeof ee=="boolean"?(P.__data[0]=ee,i.bufferSubData(i.UNIFORM_BUFFER,K+Z,P.__data)):ee.isMatrix3?(P.__data[0]=ee.elements[0],P.__data[1]=ee.elements[1],P.__data[2]=ee.elements[2],P.__data[3]=0,P.__data[4]=ee.elements[3],P.__data[5]=ee.elements[4],P.__data[6]=ee.elements[5],P.__data[7]=0,P.__data[8]=ee.elements[6],P.__data[9]=ee.elements[7],P.__data[10]=ee.elements[8],P.__data[11]=0):(ee.toArray(P.__data,Z),Z+=Y.storage/Float32Array.BYTES_PER_ELEMENT)}i.bufferSubData(i.UNIFORM_BUFFER,K,P.__data)}}}i.bindBuffer(i.UNIFORM_BUFFER,null)}function f(M,v,b,N){const A=M.value,R=v+"_"+b;if(N[R]===void 0)return typeof A=="number"||typeof A=="boolean"?N[R]=A:N[R]=A.clone(),!0;{const F=N[R];if(typeof A=="number"||typeof A=="boolean"){if(F!==A)return N[R]=A,!0}else if(F.equals(A)===!1)return F.copy(A),!0}return!1}function g(M){const v=M.uniforms;let b=0;const N=16;for(let R=0,F=v.length;R<F;R++){const w=Array.isArray(v[R])?v[R]:[v[R]];for(let y=0,P=w.length;y<P;y++){const K=w[y],H=Array.isArray(K.value)?K.value:[K.value];for(let Z=0,q=H.length;Z<q;Z++){const ee=H[Z],Y=_(ee),ne=b%N,ge=ne%Y.boundary,de=ne+ge;b+=ge,de!==0&&N-de<Y.storage&&(b+=N-de),K.__data=new Float32Array(Y.storage/Float32Array.BYTES_PER_ELEMENT),K.__offset=b,b+=Y.storage}}}const A=b%N;return A>0&&(b+=N-A),M.__size=b,M.__cache={},this}function _(M){const v={boundary:0,storage:0};return typeof M=="number"||typeof M=="boolean"?(v.boundary=4,v.storage=4):M.isVector2?(v.boundary=8,v.storage=8):M.isVector3||M.isColor?(v.boundary=16,v.storage=12):M.isVector4?(v.boundary=16,v.storage=16):M.isMatrix3?(v.boundary=48,v.storage=48):M.isMatrix4?(v.boundary=64,v.storage=64):M.isTexture?console.warn("THREE.WebGLRenderer: Texture samplers can not be part of an uniforms group."):console.warn("THREE.WebGLRenderer: Unsupported uniform value type.",M),v}function p(M){const v=M.target;v.removeEventListener("dispose",p);const b=a.indexOf(v.__bindingPointIndex);a.splice(b,1),i.deleteBuffer(s[v.id]),delete s[v.id],delete r[v.id]}function m(){for(const M in s)i.deleteBuffer(s[M]);a=[],s={},r={}}return{bind:l,update:c,dispose:m}}class dp{constructor(e={}){const{canvas:t=Gg(),context:n=null,depth:s=!0,stencil:r=!1,alpha:a=!1,antialias:o=!1,premultipliedAlpha:l=!0,preserveDrawingBuffer:c=!1,powerPreference:h="default",failIfMajorPerformanceCaveat:u=!1}=e;this.isWebGLRenderer=!0;let d;if(n!==null){if(typeof WebGLRenderingContext<"u"&&n instanceof WebGLRenderingContext)throw new Error("THREE.WebGLRenderer: WebGL 1 is not supported since r163.");d=n.getContextAttributes().alpha}else d=a;const f=new Uint32Array(4),g=new Int32Array(4);let _=null,p=null;const m=[],M=[];this.domElement=t,this.debug={checkShaderErrors:!0,onShaderError:null},this.autoClear=!0,this.autoClearColor=!0,this.autoClearDepth=!0,this.autoClearStencil=!0,this.sortObjects=!0,this.clippingPlanes=[],this.localClippingEnabled=!1,this._outputColorSpace=bi,this.toneMapping=fs,this.toneMappingExposure=1;const v=this;let b=!1,N=0,A=0,R=null,F=-1,w=null;const y=new sn,P=new sn;let K=null;const H=new nt(0);let Z=0,q=t.width,ee=t.height,Y=1,ne=null,ge=null;const de=new sn(0,0,q,ee),ve=new sn(0,0,q,ee);let Te=!1;const ye=new Lh;let ie=!1,he=!1;const Me=new Bt,fe=new V,ze=new sn,Ge={background:null,fog:null,environment:null,overrideMaterial:null,isScene:!0};let Fe=!1;function pt(){return R===null?Y:1}let O=n;function dt(T,W){return t.getContext(T,W)}try{const T={alpha:!0,depth:s,stencil:r,antialias:o,premultipliedAlpha:l,preserveDrawingBuffer:c,powerPreference:h,failIfMajorPerformanceCaveat:u};if("setAttribute"in t&&t.setAttribute("data-engine",`three.js r${Mh}`),t.addEventListener("webglcontextlost",se,!1),t.addEventListener("webglcontextrestored",re,!1),t.addEventListener("webglcontextcreationerror",xe,!1),O===null){const W="webgl2";if(O=dt(W,T),O===null)throw dt(W)?new Error("Error creating WebGL context with your selected attributes."):new Error("Error creating WebGL context.")}}catch(T){throw console.error("THREE.WebGLRenderer: "+T.message),T}let st,ct,Oe,wt,Ye,qe,D,E,Q,le,te,X,we,_e,Re,Ze,me,Ae,Je,ke,be,He,B,ce;function U(){st=new rv(O),st.init(),He=new Gy(O,st),ct=new Qx(O,st,e,He),Oe=new ky(O),wt=new lv(O),Ye=new Ty,qe=new Vy(O,st,Oe,Ye,ct,He,wt),D=new tv(v),E=new sv(v),Q=new m_(O),B=new Zx(O,Q),le=new av(O,Q,wt,B),te=new hv(O,le,Q,wt),Je=new cv(O,ct,qe),Ze=new ev(Ye),X=new Ey(v,D,E,st,ct,B,Ze),we=new Zy(v,Ye),_e=new Ry,Re=new Uy(st),Ae=new Kx(v,D,E,Oe,te,d,l),me=new zy(v,te,ct),ce=new Jy(O,wt,ct,Oe),ke=new Jx(O,st,wt),be=new ov(O,st,wt),wt.programs=X.programs,v.capabilities=ct,v.extensions=st,v.properties=Ye,v.renderLists=_e,v.shadowMap=me,v.state=Oe,v.info=wt}U();const ae=new jy(v,O);this.xr=ae,this.getContext=function(){return O},this.getContextAttributes=function(){return O.getContextAttributes()},this.forceContextLoss=function(){const T=st.get("WEBGL_lose_context");T&&T.loseContext()},this.forceContextRestore=function(){const T=st.get("WEBGL_lose_context");T&&T.restoreContext()},this.getPixelRatio=function(){return Y},this.setPixelRatio=function(T){T!==void 0&&(Y=T,this.setSize(q,ee,!1))},this.getSize=function(T){return T.set(q,ee)},this.setSize=function(T,W,J=!0){if(ae.isPresenting){console.warn("THREE.WebGLRenderer: Can't change size while VR device is presenting.");return}q=T,ee=W,t.width=Math.floor(T*Y),t.height=Math.floor(W*Y),J===!0&&(t.style.width=T+"px",t.style.height=W+"px"),this.setViewport(0,0,T,W)},this.getDrawingBufferSize=function(T){return T.set(q*Y,ee*Y).floor()},this.setDrawingBufferSize=function(T,W,J){q=T,ee=W,Y=J,t.width=Math.floor(T*J),t.height=Math.floor(W*J),this.setViewport(0,0,T,W)},this.getCurrentViewport=function(T){return T.copy(y)},this.getViewport=function(T){return T.copy(de)},this.setViewport=function(T,W,J,$){T.isVector4?de.set(T.x,T.y,T.z,T.w):de.set(T,W,J,$),Oe.viewport(y.copy(de).multiplyScalar(Y).round())},this.getScissor=function(T){return T.copy(ve)},this.setScissor=function(T,W,J,$){T.isVector4?ve.set(T.x,T.y,T.z,T.w):ve.set(T,W,J,$),Oe.scissor(P.copy(ve).multiplyScalar(Y).round())},this.getScissorTest=function(){return Te},this.setScissorTest=function(T){Oe.setScissorTest(Te=T)},this.setOpaqueSort=function(T){ne=T},this.setTransparentSort=function(T){ge=T},this.getClearColor=function(T){return T.copy(Ae.getClearColor())},this.setClearColor=function(){Ae.setClearColor.apply(Ae,arguments)},this.getClearAlpha=function(){return Ae.getClearAlpha()},this.setClearAlpha=function(){Ae.setClearAlpha.apply(Ae,arguments)},this.clear=function(T=!0,W=!0,J=!0){let $=0;if(T){let G=!1;if(R!==null){const ue=R.texture.format;G=ue===Ah||ue===Th||ue===Eh}if(G){const ue=R.texture.type,Pe=ue===Yi||ue===qs||ue===Fa||ue===qr||ue===bh||ue===wh,Le=Ae.getClearColor(),Ue=Ae.getClearAlpha(),Qe=Le.r,et=Le.g,Be=Le.b;Pe?(f[0]=Qe,f[1]=et,f[2]=Be,f[3]=Ue,O.clearBufferuiv(O.COLOR,0,f)):(g[0]=Qe,g[1]=et,g[2]=Be,g[3]=Ue,O.clearBufferiv(O.COLOR,0,g))}else $|=O.COLOR_BUFFER_BIT}W&&($|=O.DEPTH_BUFFER_BIT),J&&($|=O.STENCIL_BUFFER_BIT,this.state.buffers.stencil.setMask(4294967295)),O.clear($)},this.clearColor=function(){this.clear(!0,!1,!1)},this.clearDepth=function(){this.clear(!1,!0,!1)},this.clearStencil=function(){this.clear(!1,!1,!0)},this.dispose=function(){t.removeEventListener("webglcontextlost",se,!1),t.removeEventListener("webglcontextrestored",re,!1),t.removeEventListener("webglcontextcreationerror",xe,!1),_e.dispose(),Re.dispose(),Ye.dispose(),D.dispose(),E.dispose(),te.dispose(),B.dispose(),ce.dispose(),X.dispose(),ae.dispose(),ae.removeEventListener("sessionstart",kt),ae.removeEventListener("sessionend",Ht),ln.stop()};function se(T){T.preventDefault(),console.log("THREE.WebGLRenderer: Context Lost."),b=!0}function re(){console.log("THREE.WebGLRenderer: Context Restored."),b=!1;const T=wt.autoReset,W=me.enabled,J=me.autoUpdate,$=me.needsUpdate,G=me.type;U(),wt.autoReset=T,me.enabled=W,me.autoUpdate=J,me.needsUpdate=$,me.type=G}function xe(T){console.error("THREE.WebGLRenderer: A WebGL context could not be created. Reason: ",T.statusMessage)}function Ke(T){const W=T.target;W.removeEventListener("dispose",Ke),ot(W)}function ot(T){_t(T),Ye.remove(T)}function _t(T){const W=Ye.get(T).programs;W!==void 0&&(W.forEach(function(J){X.releaseProgram(J)}),T.isShaderMaterial&&X.releaseShaderCache(T))}this.renderBufferDirect=function(T,W,J,$,G,ue){W===null&&(W=Ge);const Pe=G.isMesh&&G.matrixWorld.determinant()<0,Le=Tl(T,W,J,$,G);Oe.setMaterial($,Pe);let Ue=J.index,Qe=1;if($.wireframe===!0){if(Ue=le.getWireframeAttribute(J),Ue===void 0)return;Qe=2}const et=J.drawRange,Be=J.attributes.position;let ht=et.start*Qe,Pt=(et.start+et.count)*Qe;ue!==null&&(ht=Math.max(ht,ue.start*Qe),Pt=Math.min(Pt,(ue.start+ue.count)*Qe)),Ue!==null?(ht=Math.max(ht,0),Pt=Math.min(Pt,Ue.count)):Be!=null&&(ht=Math.max(ht,0),Pt=Math.min(Pt,Be.count));const Lt=Pt-ht;if(Lt<0||Lt===1/0)return;B.setup(G,$,Le,J,Ue);let gn,mt=ke;if(Ue!==null&&(gn=Q.get(Ue),mt=be,mt.setIndex(gn)),G.isMesh)$.wireframe===!0?(Oe.setLineWidth($.wireframeLinewidth*pt()),mt.setMode(O.LINES)):mt.setMode(O.TRIANGLES);else if(G.isLine){let Ve=$.linewidth;Ve===void 0&&(Ve=1),Oe.setLineWidth(Ve*pt()),G.isLineSegments?mt.setMode(O.LINES):G.isLineLoop?mt.setMode(O.LINE_LOOP):mt.setMode(O.LINE_STRIP)}else G.isPoints?mt.setMode(O.POINTS):G.isSprite&&mt.setMode(O.TRIANGLES);if(G.isBatchedMesh)if(G._multiDrawInstances!==null)mt.renderMultiDrawInstances(G._multiDrawStarts,G._multiDrawCounts,G._multiDrawCount,G._multiDrawInstances);else if(st.get("WEBGL_multi_draw"))mt.renderMultiDraw(G._multiDrawStarts,G._multiDrawCounts,G._multiDrawCount);else{const Ve=G._multiDrawStarts,Yt=G._multiDrawCounts,gt=G._multiDrawCount,Dt=Ue?Q.get(Ue).bytesPerElement:1,Ui=Ye.get($).currentProgram.getUniforms();for(let vn=0;vn<gt;vn++)Ui.setValue(O,"_gl_DrawID",vn),mt.render(Ve[vn]/Dt,Yt[vn])}else if(G.isInstancedMesh)mt.renderInstances(ht,Lt,G.count);else if(J.isInstancedBufferGeometry){const Ve=J._maxInstanceCount!==void 0?J._maxInstanceCount:1/0,Yt=Math.min(J.instanceCount,Ve);mt.renderInstances(ht,Lt,Yt)}else mt.render(ht,Lt)};function Et(T,W,J){T.transparent===!0&&T.side===In&&T.forceSinglePass===!1?(T.side=Nn,T.needsUpdate=!0,bs(T,W,J),T.side=gs,T.needsUpdate=!0,bs(T,W,J),T.side=In):bs(T,W,J)}this.compile=function(T,W,J=null){J===null&&(J=T),p=Re.get(J),p.init(W),M.push(p),J.traverseVisible(function(G){G.isLight&&G.layers.test(W.layers)&&(p.pushLight(G),G.castShadow&&p.pushShadow(G))}),T!==J&&T.traverseVisible(function(G){G.isLight&&G.layers.test(W.layers)&&(p.pushLight(G),G.castShadow&&p.pushShadow(G))}),p.setupLights();const $=new Set;return T.traverse(function(G){const ue=G.material;if(ue)if(Array.isArray(ue))for(let Pe=0;Pe<ue.length;Pe++){const Le=ue[Pe];Et(Le,J,G),$.add(Le)}else Et(ue,J,G),$.add(ue)}),M.pop(),p=null,$},this.compileAsync=function(T,W,J=null){const $=this.compile(T,W,J);return new Promise(G=>{function ue(){if($.forEach(function(Pe){Ye.get(Pe).currentProgram.isReady()&&$.delete(Pe)}),$.size===0){G(T);return}setTimeout(ue,10)}st.get("KHR_parallel_shader_compile")!==null?ue():setTimeout(ue,10)})};let lt=null;function mn(T){lt&&lt(T)}function kt(){ln.stop()}function Ht(){ln.start()}const ln=new ap;ln.setAnimationLoop(mn),typeof self<"u"&&ln.setContext(self),this.setAnimationLoop=function(T){lt=T,ae.setAnimationLoop(T),T===null?ln.stop():ln.start()},ae.addEventListener("sessionstart",kt),ae.addEventListener("sessionend",Ht),this.render=function(T,W){if(W!==void 0&&W.isCamera!==!0){console.error("THREE.WebGLRenderer.render: camera is not an instance of THREE.Camera.");return}if(b===!0)return;if(T.matrixWorldAutoUpdate===!0&&T.updateMatrixWorld(),W.parent===null&&W.matrixWorldAutoUpdate===!0&&W.updateMatrixWorld(),ae.enabled===!0&&ae.isPresenting===!0&&(ae.cameraAutoUpdate===!0&&ae.updateCamera(W),W=ae.getCamera()),T.isScene===!0&&T.onBeforeRender(v,T,W,R),p=Re.get(T,M.length),p.init(W),M.push(p),Me.multiplyMatrices(W.projectionMatrix,W.matrixWorldInverse),ye.setFromProjectionMatrix(Me),he=this.localClippingEnabled,ie=Ze.init(this.clippingPlanes,he),_=_e.get(T,m.length),_.init(),m.push(_),ae.enabled===!0&&ae.isPresenting===!0){const ue=v.xr.getDepthSensingMesh();ue!==null&&gi(ue,W,-1/0,v.sortObjects)}gi(T,W,0,v.sortObjects),_.finish(),v.sortObjects===!0&&_.sort(ne,ge),Fe=ae.enabled===!1||ae.isPresenting===!1||ae.hasDepthSensing()===!1,Fe&&Ae.addToRenderList(_,T),this.info.render.frame++,ie===!0&&Ze.beginShadows();const J=p.state.shadowsArray;me.render(J,T,W),ie===!0&&Ze.endShadows(),this.info.autoReset===!0&&this.info.reset();const $=_.opaque,G=_.transmissive;if(p.setupLights(),W.isArrayCamera){const ue=W.cameras;if(G.length>0)for(let Pe=0,Le=ue.length;Pe<Le;Pe++){const Ue=ue[Pe];wn($,G,T,Ue)}Fe&&Ae.render(T);for(let Pe=0,Le=ue.length;Pe<Le;Pe++){const Ue=ue[Pe];Li(_,T,Ue,Ue.viewport)}}else G.length>0&&wn($,G,T,W),Fe&&Ae.render(T),Li(_,T,W);R!==null&&(qe.updateMultisampleRenderTarget(R),qe.updateRenderTargetMipmap(R)),T.isScene===!0&&T.onAfterRender(v,T,W),B.resetDefaultState(),F=-1,w=null,M.pop(),M.length>0?(p=M[M.length-1],ie===!0&&Ze.setGlobalState(v.clippingPlanes,p.state.camera)):p=null,m.pop(),m.length>0?_=m[m.length-1]:_=null};function gi(T,W,J,$){if(T.visible===!1)return;if(T.layers.test(W.layers)){if(T.isGroup)J=T.renderOrder;else if(T.isLOD)T.autoUpdate===!0&&T.update(W);else if(T.isLight)p.pushLight(T),T.castShadow&&p.pushShadow(T);else if(T.isSprite){if(!T.frustumCulled||ye.intersectsSprite(T)){$&&ze.setFromMatrixPosition(T.matrixWorld).applyMatrix4(Me);const Pe=te.update(T),Le=T.material;Le.visible&&_.push(T,Pe,Le,J,ze.z,null)}}else if((T.isMesh||T.isLine||T.isPoints)&&(!T.frustumCulled||ye.intersectsObject(T))){const Pe=te.update(T),Le=T.material;if($&&(T.boundingSphere!==void 0?(T.boundingSphere===null&&T.computeBoundingSphere(),ze.copy(T.boundingSphere.center)):(Pe.boundingSphere===null&&Pe.computeBoundingSphere(),ze.copy(Pe.boundingSphere.center)),ze.applyMatrix4(T.matrixWorld).applyMatrix4(Me)),Array.isArray(Le)){const Ue=Pe.groups;for(let Qe=0,et=Ue.length;Qe<et;Qe++){const Be=Ue[Qe],ht=Le[Be.materialIndex];ht&&ht.visible&&_.push(T,Pe,ht,J,ze.z,Be)}}else Le.visible&&_.push(T,Pe,Le,J,ze.z,null)}}const ue=T.children;for(let Pe=0,Le=ue.length;Pe<Le;Pe++)gi(ue[Pe],W,J,$)}function Li(T,W,J,$){const G=T.opaque,ue=T.transmissive,Pe=T.transparent;p.setupLightsView(J),ie===!0&&Ze.setGlobalState(v.clippingPlanes,J),$&&Oe.viewport(y.copy($)),G.length>0&&ni(G,W,J),ue.length>0&&ni(ue,W,J),Pe.length>0&&ni(Pe,W,J),Oe.buffers.depth.setTest(!0),Oe.buffers.depth.setMask(!0),Oe.buffers.color.setMask(!0),Oe.setPolygonOffset(!1)}function wn(T,W,J,$){if((J.isScene===!0?J.overrideMaterial:null)!==null)return;p.state.transmissionRenderTarget[$.id]===void 0&&(p.state.transmissionRenderTarget[$.id]=new $s(1,1,{generateMipmaps:!0,type:st.has("EXT_color_buffer_half_float")||st.has("EXT_color_buffer_float")?Ga:Yi,minFilter:Hs,samples:4,stencilBuffer:r,resolveDepthBuffer:!1,resolveStencilBuffer:!1,colorSpace:bt.workingColorSpace}));const ue=p.state.transmissionRenderTarget[$.id],Pe=$.viewport||y;ue.setSize(Pe.z,Pe.w);const Le=v.getRenderTarget();v.setRenderTarget(ue),v.getClearColor(H),Z=v.getClearAlpha(),Z<1&&v.setClearColor(16777215,.5),v.clear(),Fe&&Ae.render(J);const Ue=v.toneMapping;v.toneMapping=fs;const Qe=$.viewport;if($.viewport!==void 0&&($.viewport=void 0),p.setupLightsView($),ie===!0&&Ze.setGlobalState(v.clippingPlanes,$),ni(T,J,$),qe.updateMultisampleRenderTarget(ue),qe.updateRenderTargetMipmap(ue),st.has("WEBGL_multisampled_render_to_texture")===!1){let et=!1;for(let Be=0,ht=W.length;Be<ht;Be++){const Pt=W[Be],Lt=Pt.object,gn=Pt.geometry,mt=Pt.material,Ve=Pt.group;if(mt.side===In&&Lt.layers.test($.layers)){const Yt=mt.side;mt.side=Nn,mt.needsUpdate=!0,Di(Lt,J,$,gn,mt,Ve),mt.side=Yt,mt.needsUpdate=!0,et=!0}}et===!0&&(qe.updateMultisampleRenderTarget(ue),qe.updateRenderTargetMipmap(ue))}v.setRenderTarget(Le),v.setClearColor(H,Z),Qe!==void 0&&($.viewport=Qe),v.toneMapping=Ue}function ni(T,W,J){const $=W.isScene===!0?W.overrideMaterial:null;for(let G=0,ue=T.length;G<ue;G++){const Pe=T[G],Le=Pe.object,Ue=Pe.geometry,Qe=$===null?Pe.material:$,et=Pe.group;Le.layers.test(J.layers)&&Di(Le,W,J,Ue,Qe,et)}}function Di(T,W,J,$,G,ue){T.onBeforeRender(v,W,J,$,G,ue),T.modelViewMatrix.multiplyMatrices(J.matrixWorldInverse,T.matrixWorld),T.normalMatrix.getNormalMatrix(T.modelViewMatrix),G.onBeforeRender(v,W,J,$,T,ue),G.transparent===!0&&G.side===In&&G.forceSinglePass===!1?(G.side=Nn,G.needsUpdate=!0,v.renderBufferDirect(J,W,$,G,T,ue),G.side=gs,G.needsUpdate=!0,v.renderBufferDirect(J,W,$,G,T,ue),G.side=In):v.renderBufferDirect(J,W,$,G,T,ue),T.onAfterRender(v,W,J,$,G,ue)}function bs(T,W,J){W.isScene!==!0&&(W=Ge);const $=Ye.get(T),G=p.state.lights,ue=p.state.shadowsArray,Pe=G.state.version,Le=X.getParameters(T,G.state,ue,W,J),Ue=X.getProgramCacheKey(Le);let Qe=$.programs;$.environment=T.isMeshStandardMaterial?W.environment:null,$.fog=W.fog,$.envMap=(T.isMeshStandardMaterial?E:D).get(T.envMap||$.environment),$.envMapRotation=$.environment!==null&&T.envMap===null?W.environmentRotation:T.envMapRotation,Qe===void 0&&(T.addEventListener("dispose",Ke),Qe=new Map,$.programs=Qe);let et=Qe.get(Ue);if(et!==void 0){if($.currentProgram===et&&$.lightsStateVersion===Pe)return ja(T,Le),et}else Le.uniforms=X.getUniforms(T),T.onBeforeCompile(Le,v),et=X.acquireProgram(Le,Ue),Qe.set(Ue,et),$.uniforms=Le.uniforms;const Be=$.uniforms;return(!T.isShaderMaterial&&!T.isRawShaderMaterial||T.clipping===!0)&&(Be.clippingPlanes=Ze.uniform),ja(T,Le),$.needsLights=Al(T),$.lightsStateVersion=Pe,$.needsLights&&(Be.ambientLightColor.value=G.state.ambient,Be.lightProbe.value=G.state.probe,Be.directionalLights.value=G.state.directional,Be.directionalLightShadows.value=G.state.directionalShadow,Be.spotLights.value=G.state.spot,Be.spotLightShadows.value=G.state.spotShadow,Be.rectAreaLights.value=G.state.rectArea,Be.ltc_1.value=G.state.rectAreaLTC1,Be.ltc_2.value=G.state.rectAreaLTC2,Be.pointLights.value=G.state.point,Be.pointLightShadows.value=G.state.pointShadow,Be.hemisphereLights.value=G.state.hemi,Be.directionalShadowMap.value=G.state.directionalShadowMap,Be.directionalShadowMatrix.value=G.state.directionalShadowMatrix,Be.spotShadowMap.value=G.state.spotShadowMap,Be.spotLightMatrix.value=G.state.spotLightMatrix,Be.spotLightMap.value=G.state.spotLightMap,Be.pointShadowMap.value=G.state.pointShadowMap,Be.pointShadowMatrix.value=G.state.pointShadowMatrix),$.currentProgram=et,$.uniformsList=null,et}function la(T){if(T.uniformsList===null){const W=T.currentProgram.getUniforms();T.uniformsList=Xo.seqWithValue(W.seq,T.uniforms)}return T.uniformsList}function ja(T,W){const J=Ye.get(T);J.outputColorSpace=W.outputColorSpace,J.batching=W.batching,J.batchingColor=W.batchingColor,J.instancing=W.instancing,J.instancingColor=W.instancingColor,J.instancingMorph=W.instancingMorph,J.skinning=W.skinning,J.morphTargets=W.morphTargets,J.morphNormals=W.morphNormals,J.morphColors=W.morphColors,J.morphTargetsCount=W.morphTargetsCount,J.numClippingPlanes=W.numClippingPlanes,J.numIntersection=W.numClipIntersection,J.vertexAlphas=W.vertexAlphas,J.vertexTangents=W.vertexTangents,J.toneMapping=W.toneMapping}function Tl(T,W,J,$,G){W.isScene!==!0&&(W=Ge),qe.resetTextureUnits();const ue=W.fog,Pe=$.isMeshStandardMaterial?W.environment:null,Le=R===null?v.outputColorSpace:R.isXRRenderTarget===!0?R.texture.colorSpace:Ms,Ue=($.isMeshStandardMaterial?E:D).get($.envMap||Pe),Qe=$.vertexColors===!0&&!!J.attributes.color&&J.attributes.color.itemSize===4,et=!!J.attributes.tangent&&(!!$.normalMap||$.anisotropy>0),Be=!!J.morphAttributes.position,ht=!!J.morphAttributes.normal,Pt=!!J.morphAttributes.color;let Lt=fs;$.toneMapped&&(R===null||R.isXRRenderTarget===!0)&&(Lt=v.toneMapping);const gn=J.morphAttributes.position||J.morphAttributes.normal||J.morphAttributes.color,mt=gn!==void 0?gn.length:0,Ve=Ye.get($),Yt=p.state.lights;if(ie===!0&&(he===!0||T!==w)){const Dn=T===w&&$.id===F;Ze.setState($,T,Dn)}let gt=!1;$.version===Ve.__version?(Ve.needsLights&&Ve.lightsStateVersion!==Yt.state.version||Ve.outputColorSpace!==Le||G.isBatchedMesh&&Ve.batching===!1||!G.isBatchedMesh&&Ve.batching===!0||G.isBatchedMesh&&Ve.batchingColor===!0&&G.colorTexture===null||G.isBatchedMesh&&Ve.batchingColor===!1&&G.colorTexture!==null||G.isInstancedMesh&&Ve.instancing===!1||!G.isInstancedMesh&&Ve.instancing===!0||G.isSkinnedMesh&&Ve.skinning===!1||!G.isSkinnedMesh&&Ve.skinning===!0||G.isInstancedMesh&&Ve.instancingColor===!0&&G.instanceColor===null||G.isInstancedMesh&&Ve.instancingColor===!1&&G.instanceColor!==null||G.isInstancedMesh&&Ve.instancingMorph===!0&&G.morphTexture===null||G.isInstancedMesh&&Ve.instancingMorph===!1&&G.morphTexture!==null||Ve.envMap!==Ue||$.fog===!0&&Ve.fog!==ue||Ve.numClippingPlanes!==void 0&&(Ve.numClippingPlanes!==Ze.numPlanes||Ve.numIntersection!==Ze.numIntersection)||Ve.vertexAlphas!==Qe||Ve.vertexTangents!==et||Ve.morphTargets!==Be||Ve.morphNormals!==ht||Ve.morphColors!==Pt||Ve.toneMapping!==Lt||Ve.morphTargetsCount!==mt)&&(gt=!0):(gt=!0,Ve.__version=$.version);let Dt=Ve.currentProgram;gt===!0&&(Dt=bs($,W,G));let Ui=!1,vn=!1,ws=!1;const Wt=Dt.getUniforms(),_i=Ve.uniforms;if(Oe.useProgram(Dt.program)&&(Ui=!0,vn=!0,ws=!0),$.id!==F&&(F=$.id,vn=!0),Ui||w!==T){Wt.setValue(O,"projectionMatrix",T.projectionMatrix),Wt.setValue(O,"viewMatrix",T.matrixWorldInverse);const Dn=Wt.map.cameraPosition;Dn!==void 0&&Dn.setValue(O,fe.setFromMatrixPosition(T.matrixWorld)),ct.logarithmicDepthBuffer&&Wt.setValue(O,"logDepthBufFC",2/(Math.log(T.far+1)/Math.LN2)),($.isMeshPhongMaterial||$.isMeshToonMaterial||$.isMeshLambertMaterial||$.isMeshBasicMaterial||$.isMeshStandardMaterial||$.isShaderMaterial)&&Wt.setValue(O,"isOrthographic",T.isOrthographicCamera===!0),w!==T&&(w=T,vn=!0,ws=!0)}if(G.isSkinnedMesh){Wt.setOptional(O,G,"bindMatrix"),Wt.setOptional(O,G,"bindMatrixInverse");const Dn=G.skeleton;Dn&&(Dn.boneTexture===null&&Dn.computeBoneTexture(),Wt.setValue(O,"boneTexture",Dn.boneTexture,qe))}G.isBatchedMesh&&(Wt.setOptional(O,G,"batchingTexture"),Wt.setValue(O,"batchingTexture",G._matricesTexture,qe),Wt.setOptional(O,G,"batchingIdTexture"),Wt.setValue(O,"batchingIdTexture",G._indirectTexture,qe),Wt.setOptional(O,G,"batchingColorTexture"),G._colorsTexture!==null&&Wt.setValue(O,"batchingColorTexture",G._colorsTexture,qe));const ca=J.morphAttributes;if((ca.position!==void 0||ca.normal!==void 0||ca.color!==void 0)&&Je.update(G,J,Dt),(vn||Ve.receiveShadow!==G.receiveShadow)&&(Ve.receiveShadow=G.receiveShadow,Wt.setValue(O,"receiveShadow",G.receiveShadow)),$.isMeshGouraudMaterial&&$.envMap!==null&&(_i.envMap.value=Ue,_i.flipEnvMap.value=Ue.isCubeTexture&&Ue.isRenderTargetTexture===!1?-1:1),$.isMeshStandardMaterial&&$.envMap===null&&W.environment!==null&&(_i.envMapIntensity.value=W.environmentIntensity),vn&&(Wt.setValue(O,"toneMappingExposure",v.toneMappingExposure),Ve.needsLights&&Ii(_i,ws),ue&&$.fog===!0&&we.refreshFogUniforms(_i,ue),we.refreshMaterialUniforms(_i,$,Y,ee,p.state.transmissionRenderTarget[T.id]),Xo.upload(O,la(Ve),_i,qe)),$.isShaderMaterial&&$.uniformsNeedUpdate===!0&&(Xo.upload(O,la(Ve),_i,qe),$.uniformsNeedUpdate=!1),$.isSpriteMaterial&&Wt.setValue(O,"center",G.center),Wt.setValue(O,"modelViewMatrix",G.modelViewMatrix),Wt.setValue(O,"normalMatrix",G.normalMatrix),Wt.setValue(O,"modelMatrix",G.matrixWorld),$.isShaderMaterial||$.isRawShaderMaterial){const Dn=$.uniformsGroups;for(let Js=0,Ka=Dn.length;Js<Ka;Js++){const Za=Dn[Js];ce.update(Za,Dt),ce.bind(Za,Dt)}}return Dt}function Ii(T,W){T.ambientLightColor.needsUpdate=W,T.lightProbe.needsUpdate=W,T.directionalLights.needsUpdate=W,T.directionalLightShadows.needsUpdate=W,T.pointLights.needsUpdate=W,T.pointLightShadows.needsUpdate=W,T.spotLights.needsUpdate=W,T.spotLightShadows.needsUpdate=W,T.rectAreaLights.needsUpdate=W,T.hemisphereLights.needsUpdate=W}function Al(T){return T.isMeshLambertMaterial||T.isMeshToonMaterial||T.isMeshPhongMaterial||T.isMeshStandardMaterial||T.isShadowMaterial||T.isShaderMaterial&&T.lights===!0}this.getActiveCubeFace=function(){return N},this.getActiveMipmapLevel=function(){return A},this.getRenderTarget=function(){return R},this.setRenderTargetTextures=function(T,W,J){Ye.get(T.texture).__webglTexture=W,Ye.get(T.depthTexture).__webglTexture=J;const $=Ye.get(T);$.__hasExternalTextures=!0,$.__autoAllocateDepthBuffer=J===void 0,$.__autoAllocateDepthBuffer||st.has("WEBGL_multisampled_render_to_texture")===!0&&(console.warn("THREE.WebGLRenderer: Render-to-texture extension was disabled because an external texture was provided"),$.__useRenderToTexture=!1)},this.setRenderTargetFramebuffer=function(T,W){const J=Ye.get(T);J.__webglFramebuffer=W,J.__useDefaultFramebuffer=W===void 0},this.setRenderTarget=function(T,W=0,J=0){R=T,N=W,A=J;let $=!0,G=null,ue=!1,Pe=!1;if(T){const Ue=Ye.get(T);if(Ue.__useDefaultFramebuffer!==void 0)Oe.bindFramebuffer(O.FRAMEBUFFER,null),$=!1;else if(Ue.__webglFramebuffer===void 0)qe.setupRenderTarget(T);else if(Ue.__hasExternalTextures)qe.rebindTextures(T,Ye.get(T.texture).__webglTexture,Ye.get(T.depthTexture).__webglTexture);else if(T.depthBuffer){const Be=T.depthTexture;if(Ue.__boundDepthTexture!==Be){if(Be!==null&&Ye.has(Be)&&(T.width!==Be.image.width||T.height!==Be.image.height))throw new Error("WebGLRenderTarget: Attached DepthTexture is initialized to the incorrect size.");qe.setupDepthRenderbuffer(T)}}const Qe=T.texture;(Qe.isData3DTexture||Qe.isDataArrayTexture||Qe.isCompressedArrayTexture)&&(Pe=!0);const et=Ye.get(T).__webglFramebuffer;T.isWebGLCubeRenderTarget?(Array.isArray(et[W])?G=et[W][J]:G=et[W],ue=!0):T.samples>0&&qe.useMultisampledRTT(T)===!1?G=Ye.get(T).__webglMultisampledFramebuffer:Array.isArray(et)?G=et[J]:G=et,y.copy(T.viewport),P.copy(T.scissor),K=T.scissorTest}else y.copy(de).multiplyScalar(Y).floor(),P.copy(ve).multiplyScalar(Y).floor(),K=Te;if(Oe.bindFramebuffer(O.FRAMEBUFFER,G)&&$&&Oe.drawBuffers(T,G),Oe.viewport(y),Oe.scissor(P),Oe.setScissorTest(K),ue){const Ue=Ye.get(T.texture);O.framebufferTexture2D(O.FRAMEBUFFER,O.COLOR_ATTACHMENT0,O.TEXTURE_CUBE_MAP_POSITIVE_X+W,Ue.__webglTexture,J)}else if(Pe){const Ue=Ye.get(T.texture),Qe=W||0;O.framebufferTextureLayer(O.FRAMEBUFFER,O.COLOR_ATTACHMENT0,Ue.__webglTexture,J||0,Qe)}F=-1},this.readRenderTargetPixels=function(T,W,J,$,G,ue,Pe){if(!(T&&T.isWebGLRenderTarget)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");return}let Le=Ye.get(T).__webglFramebuffer;if(T.isWebGLCubeRenderTarget&&Pe!==void 0&&(Le=Le[Pe]),Le){Oe.bindFramebuffer(O.FRAMEBUFFER,Le);try{const Ue=T.texture,Qe=Ue.format,et=Ue.type;if(!ct.textureFormatReadable(Qe)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in RGBA or implementation defined format.");return}if(!ct.textureTypeReadable(et)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in UnsignedByteType or implementation defined type.");return}W>=0&&W<=T.width-$&&J>=0&&J<=T.height-G&&O.readPixels(W,J,$,G,He.convert(Qe),He.convert(et),ue)}finally{const Ue=R!==null?Ye.get(R).__webglFramebuffer:null;Oe.bindFramebuffer(O.FRAMEBUFFER,Ue)}}},this.readRenderTargetPixelsAsync=async function(T,W,J,$,G,ue,Pe){if(!(T&&T.isWebGLRenderTarget))throw new Error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");let Le=Ye.get(T).__webglFramebuffer;if(T.isWebGLCubeRenderTarget&&Pe!==void 0&&(Le=Le[Pe]),Le){Oe.bindFramebuffer(O.FRAMEBUFFER,Le);try{const Ue=T.texture,Qe=Ue.format,et=Ue.type;if(!ct.textureFormatReadable(Qe))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in RGBA or implementation defined format.");if(!ct.textureTypeReadable(et))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in UnsignedByteType or implementation defined type.");if(W>=0&&W<=T.width-$&&J>=0&&J<=T.height-G){const Be=O.createBuffer();O.bindBuffer(O.PIXEL_PACK_BUFFER,Be),O.bufferData(O.PIXEL_PACK_BUFFER,ue.byteLength,O.STREAM_READ),O.readPixels(W,J,$,G,He.convert(Qe),He.convert(et),0),O.flush();const ht=O.fenceSync(O.SYNC_GPU_COMMANDS_COMPLETE,0);await Wg(O,ht,4);try{O.bindBuffer(O.PIXEL_PACK_BUFFER,Be),O.getBufferSubData(O.PIXEL_PACK_BUFFER,0,ue)}finally{O.deleteBuffer(Be),O.deleteSync(ht)}return ue}}finally{const Ue=R!==null?Ye.get(R).__webglFramebuffer:null;Oe.bindFramebuffer(O.FRAMEBUFFER,Ue)}}},this.copyFramebufferToTexture=function(T,W=null,J=0){T.isTexture!==!0&&(kr("WebGLRenderer: copyFramebufferToTexture function signature has changed."),W=arguments[0]||null,T=arguments[1]);const $=Math.pow(2,-J),G=Math.floor(T.image.width*$),ue=Math.floor(T.image.height*$),Pe=W!==null?W.x:0,Le=W!==null?W.y:0;qe.setTexture2D(T,0),O.copyTexSubImage2D(O.TEXTURE_2D,J,0,0,Pe,Le,G,ue),Oe.unbindTexture()},this.copyTextureToTexture=function(T,W,J=null,$=null,G=0){T.isTexture!==!0&&(kr("WebGLRenderer: copyTextureToTexture function signature has changed."),$=arguments[0]||null,T=arguments[1],W=arguments[2],G=arguments[3]||0,J=null);let ue,Pe,Le,Ue,Qe,et;J!==null?(ue=J.max.x-J.min.x,Pe=J.max.y-J.min.y,Le=J.min.x,Ue=J.min.y):(ue=T.image.width,Pe=T.image.height,Le=0,Ue=0),$!==null?(Qe=$.x,et=$.y):(Qe=0,et=0);const Be=He.convert(W.format),ht=He.convert(W.type);qe.setTexture2D(W,0),O.pixelStorei(O.UNPACK_FLIP_Y_WEBGL,W.flipY),O.pixelStorei(O.UNPACK_PREMULTIPLY_ALPHA_WEBGL,W.premultiplyAlpha),O.pixelStorei(O.UNPACK_ALIGNMENT,W.unpackAlignment);const Pt=O.getParameter(O.UNPACK_ROW_LENGTH),Lt=O.getParameter(O.UNPACK_IMAGE_HEIGHT),gn=O.getParameter(O.UNPACK_SKIP_PIXELS),mt=O.getParameter(O.UNPACK_SKIP_ROWS),Ve=O.getParameter(O.UNPACK_SKIP_IMAGES),Yt=T.isCompressedTexture?T.mipmaps[G]:T.image;O.pixelStorei(O.UNPACK_ROW_LENGTH,Yt.width),O.pixelStorei(O.UNPACK_IMAGE_HEIGHT,Yt.height),O.pixelStorei(O.UNPACK_SKIP_PIXELS,Le),O.pixelStorei(O.UNPACK_SKIP_ROWS,Ue),T.isDataTexture?O.texSubImage2D(O.TEXTURE_2D,G,Qe,et,ue,Pe,Be,ht,Yt.data):T.isCompressedTexture?O.compressedTexSubImage2D(O.TEXTURE_2D,G,Qe,et,Yt.width,Yt.height,Be,Yt.data):O.texSubImage2D(O.TEXTURE_2D,G,Qe,et,ue,Pe,Be,ht,Yt),O.pixelStorei(O.UNPACK_ROW_LENGTH,Pt),O.pixelStorei(O.UNPACK_IMAGE_HEIGHT,Lt),O.pixelStorei(O.UNPACK_SKIP_PIXELS,gn),O.pixelStorei(O.UNPACK_SKIP_ROWS,mt),O.pixelStorei(O.UNPACK_SKIP_IMAGES,Ve),G===0&&W.generateMipmaps&&O.generateMipmap(O.TEXTURE_2D),Oe.unbindTexture()},this.copyTextureToTexture3D=function(T,W,J=null,$=null,G=0){T.isTexture!==!0&&(kr("WebGLRenderer: copyTextureToTexture3D function signature has changed."),J=arguments[0]||null,$=arguments[1]||null,T=arguments[2],W=arguments[3],G=arguments[4]||0);let ue,Pe,Le,Ue,Qe,et,Be,ht,Pt;const Lt=T.isCompressedTexture?T.mipmaps[G]:T.image;J!==null?(ue=J.max.x-J.min.x,Pe=J.max.y-J.min.y,Le=J.max.z-J.min.z,Ue=J.min.x,Qe=J.min.y,et=J.min.z):(ue=Lt.width,Pe=Lt.height,Le=Lt.depth,Ue=0,Qe=0,et=0),$!==null?(Be=$.x,ht=$.y,Pt=$.z):(Be=0,ht=0,Pt=0);const gn=He.convert(W.format),mt=He.convert(W.type);let Ve;if(W.isData3DTexture)qe.setTexture3D(W,0),Ve=O.TEXTURE_3D;else if(W.isDataArrayTexture||W.isCompressedArrayTexture)qe.setTexture2DArray(W,0),Ve=O.TEXTURE_2D_ARRAY;else{console.warn("THREE.WebGLRenderer.copyTextureToTexture3D: only supports THREE.DataTexture3D and THREE.DataTexture2DArray.");return}O.pixelStorei(O.UNPACK_FLIP_Y_WEBGL,W.flipY),O.pixelStorei(O.UNPACK_PREMULTIPLY_ALPHA_WEBGL,W.premultiplyAlpha),O.pixelStorei(O.UNPACK_ALIGNMENT,W.unpackAlignment);const Yt=O.getParameter(O.UNPACK_ROW_LENGTH),gt=O.getParameter(O.UNPACK_IMAGE_HEIGHT),Dt=O.getParameter(O.UNPACK_SKIP_PIXELS),Ui=O.getParameter(O.UNPACK_SKIP_ROWS),vn=O.getParameter(O.UNPACK_SKIP_IMAGES);O.pixelStorei(O.UNPACK_ROW_LENGTH,Lt.width),O.pixelStorei(O.UNPACK_IMAGE_HEIGHT,Lt.height),O.pixelStorei(O.UNPACK_SKIP_PIXELS,Ue),O.pixelStorei(O.UNPACK_SKIP_ROWS,Qe),O.pixelStorei(O.UNPACK_SKIP_IMAGES,et),T.isDataTexture||T.isData3DTexture?O.texSubImage3D(Ve,G,Be,ht,Pt,ue,Pe,Le,gn,mt,Lt.data):W.isCompressedArrayTexture?O.compressedTexSubImage3D(Ve,G,Be,ht,Pt,ue,Pe,Le,gn,Lt.data):O.texSubImage3D(Ve,G,Be,ht,Pt,ue,Pe,Le,gn,mt,Lt),O.pixelStorei(O.UNPACK_ROW_LENGTH,Yt),O.pixelStorei(O.UNPACK_IMAGE_HEIGHT,gt),O.pixelStorei(O.UNPACK_SKIP_PIXELS,Dt),O.pixelStorei(O.UNPACK_SKIP_ROWS,Ui),O.pixelStorei(O.UNPACK_SKIP_IMAGES,vn),G===0&&W.generateMipmaps&&O.generateMipmap(Ve),Oe.unbindTexture()},this.initRenderTarget=function(T){Ye.get(T).__webglFramebuffer===void 0&&qe.setupRenderTarget(T)},this.initTexture=function(T){T.isCubeTexture?qe.setTextureCube(T,0):T.isData3DTexture?qe.setTexture3D(T,0):T.isDataArrayTexture||T.isCompressedArrayTexture?qe.setTexture2DArray(T,0):qe.setTexture2D(T,0),Oe.unbindTexture()},this.resetState=function(){N=0,A=0,R=null,Oe.reset(),B.reset()},typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}get coordinateSystem(){return Wi}get outputColorSpace(){return this._outputColorSpace}set outputColorSpace(e){this._outputColorSpace=e;const t=this.getContext();t.drawingBufferColorSpace=e===Rh?"display-p3":"srgb",t.unpackColorSpace=bt.workingColorSpace===cl?"display-p3":"srgb"}}class Ih{constructor(e,t=25e-5){this.isFogExp2=!0,this.name="",this.color=new nt(e),this.density=t}clone(){return new Ih(this.color,this.density)}toJSON(){return{type:"FogExp2",name:this.name,color:this.color.getHex(),density:this.density}}}class Uh extends en{constructor(){super(),this.isScene=!0,this.type="Scene",this.background=null,this.environment=null,this.fog=null,this.backgroundBlurriness=0,this.backgroundIntensity=1,this.backgroundRotation=new Ci,this.environmentIntensity=1,this.environmentRotation=new Ci,this.overrideMaterial=null,typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}copy(e,t){return super.copy(e,t),e.background!==null&&(this.background=e.background.clone()),e.environment!==null&&(this.environment=e.environment.clone()),e.fog!==null&&(this.fog=e.fog.clone()),this.backgroundBlurriness=e.backgroundBlurriness,this.backgroundIntensity=e.backgroundIntensity,this.backgroundRotation.copy(e.backgroundRotation),this.environmentIntensity=e.environmentIntensity,this.environmentRotation.copy(e.environmentRotation),e.overrideMaterial!==null&&(this.overrideMaterial=e.overrideMaterial.clone()),this.matrixAutoUpdate=e.matrixAutoUpdate,this}toJSON(e){const t=super.toJSON(e);return this.fog!==null&&(t.object.fog=this.fog.toJSON()),this.backgroundBlurriness>0&&(t.object.backgroundBlurriness=this.backgroundBlurriness),this.backgroundIntensity!==1&&(t.object.backgroundIntensity=this.backgroundIntensity),t.object.backgroundRotation=this.backgroundRotation.toArray(),this.environmentIntensity!==1&&(t.object.environmentIntensity=this.environmentIntensity),t.object.environmentRotation=this.environmentRotation.toArray(),t}}class Qy{constructor(e,t){this.isInterleavedBuffer=!0,this.array=e,this.stride=t,this.count=e!==void 0?e.length/t:0,this.usage=rh,this._updateRange={offset:0,count:-1},this.updateRanges=[],this.version=0,this.uuid=Xi()}onUploadCallback(){}set needsUpdate(e){e===!0&&this.version++}get updateRange(){return kr("THREE.InterleavedBuffer: updateRange() is deprecated and will be removed in r169. Use addUpdateRange() instead."),this._updateRange}setUsage(e){return this.usage=e,this}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}copy(e){return this.array=new e.array.constructor(e.array),this.count=e.count,this.stride=e.stride,this.usage=e.usage,this}copyAt(e,t,n){e*=this.stride,n*=t.stride;for(let s=0,r=this.stride;s<r;s++)this.array[e+s]=t.array[n+s];return this}set(e,t=0){return this.array.set(e,t),this}clone(e){e.arrayBuffers===void 0&&(e.arrayBuffers={}),this.array.buffer._uuid===void 0&&(this.array.buffer._uuid=Xi()),e.arrayBuffers[this.array.buffer._uuid]===void 0&&(e.arrayBuffers[this.array.buffer._uuid]=this.array.slice(0).buffer);const t=new this.array.constructor(e.arrayBuffers[this.array.buffer._uuid]),n=new this.constructor(t,this.stride);return n.setUsage(this.usage),n}onUpload(e){return this.onUploadCallback=e,this}toJSON(e){return e.arrayBuffers===void 0&&(e.arrayBuffers={}),this.array.buffer._uuid===void 0&&(this.array.buffer._uuid=Xi()),e.arrayBuffers[this.array.buffer._uuid]===void 0&&(e.arrayBuffers[this.array.buffer._uuid]=Array.from(new Uint32Array(this.array.buffer))),{uuid:this.uuid,buffer:this.array.buffer._uuid,type:this.array.constructor.name,stride:this.stride}}}const Rn=new V;class el{constructor(e,t,n,s=!1){this.isInterleavedBufferAttribute=!0,this.name="",this.data=e,this.itemSize=t,this.offset=n,this.normalized=s}get count(){return this.data.count}get array(){return this.data.array}set needsUpdate(e){this.data.needsUpdate=e}applyMatrix4(e){for(let t=0,n=this.data.count;t<n;t++)Rn.fromBufferAttribute(this,t),Rn.applyMatrix4(e),this.setXYZ(t,Rn.x,Rn.y,Rn.z);return this}applyNormalMatrix(e){for(let t=0,n=this.count;t<n;t++)Rn.fromBufferAttribute(this,t),Rn.applyNormalMatrix(e),this.setXYZ(t,Rn.x,Rn.y,Rn.z);return this}transformDirection(e){for(let t=0,n=this.count;t<n;t++)Rn.fromBufferAttribute(this,t),Rn.transformDirection(e),this.setXYZ(t,Rn.x,Rn.y,Rn.z);return this}getComponent(e,t){let n=this.array[e*this.data.stride+this.offset+t];return this.normalized&&(n=ui(n,this.array)),n}setComponent(e,t,n){return this.normalized&&(n=Tt(n,this.array)),this.data.array[e*this.data.stride+this.offset+t]=n,this}setX(e,t){return this.normalized&&(t=Tt(t,this.array)),this.data.array[e*this.data.stride+this.offset]=t,this}setY(e,t){return this.normalized&&(t=Tt(t,this.array)),this.data.array[e*this.data.stride+this.offset+1]=t,this}setZ(e,t){return this.normalized&&(t=Tt(t,this.array)),this.data.array[e*this.data.stride+this.offset+2]=t,this}setW(e,t){return this.normalized&&(t=Tt(t,this.array)),this.data.array[e*this.data.stride+this.offset+3]=t,this}getX(e){let t=this.data.array[e*this.data.stride+this.offset];return this.normalized&&(t=ui(t,this.array)),t}getY(e){let t=this.data.array[e*this.data.stride+this.offset+1];return this.normalized&&(t=ui(t,this.array)),t}getZ(e){let t=this.data.array[e*this.data.stride+this.offset+2];return this.normalized&&(t=ui(t,this.array)),t}getW(e){let t=this.data.array[e*this.data.stride+this.offset+3];return this.normalized&&(t=ui(t,this.array)),t}setXY(e,t,n){return e=e*this.data.stride+this.offset,this.normalized&&(t=Tt(t,this.array),n=Tt(n,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this}setXYZ(e,t,n,s){return e=e*this.data.stride+this.offset,this.normalized&&(t=Tt(t,this.array),n=Tt(n,this.array),s=Tt(s,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this.data.array[e+2]=s,this}setXYZW(e,t,n,s,r){return e=e*this.data.stride+this.offset,this.normalized&&(t=Tt(t,this.array),n=Tt(n,this.array),s=Tt(s,this.array),r=Tt(r,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this.data.array[e+2]=s,this.data.array[e+3]=r,this}clone(e){if(e===void 0){console.log("THREE.InterleavedBufferAttribute.clone(): Cloning an interleaved buffer attribute will de-interleave buffer data.");const t=[];for(let n=0;n<this.count;n++){const s=n*this.data.stride+this.offset;for(let r=0;r<this.itemSize;r++)t.push(this.data.array[s+r])}return new pi(new this.array.constructor(t),this.itemSize,this.normalized)}else return e.interleavedBuffers===void 0&&(e.interleavedBuffers={}),e.interleavedBuffers[this.data.uuid]===void 0&&(e.interleavedBuffers[this.data.uuid]=this.data.clone(e)),new el(e.interleavedBuffers[this.data.uuid],this.itemSize,this.offset,this.normalized)}toJSON(e){if(e===void 0){console.log("THREE.InterleavedBufferAttribute.toJSON(): Serializing an interleaved buffer attribute will de-interleave buffer data.");const t=[];for(let n=0;n<this.count;n++){const s=n*this.data.stride+this.offset;for(let r=0;r<this.itemSize;r++)t.push(this.data.array[s+r])}return{itemSize:this.itemSize,type:this.array.constructor.name,array:t,normalized:this.normalized}}else return e.interleavedBuffers===void 0&&(e.interleavedBuffers={}),e.interleavedBuffers[this.data.uuid]===void 0&&(e.interleavedBuffers[this.data.uuid]=this.data.toJSON(e)),{isInterleavedBufferAttribute:!0,itemSize:this.itemSize,data:this.data.uuid,offset:this.offset,normalized:this.normalized}}}class ji extends Ss{constructor(e){super(),this.isSpriteMaterial=!0,this.type="SpriteMaterial",this.color=new nt(16777215),this.map=null,this.alphaMap=null,this.rotation=0,this.sizeAttenuation=!0,this.transparent=!0,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.alphaMap=e.alphaMap,this.rotation=e.rotation,this.sizeAttenuation=e.sizeAttenuation,this.fog=e.fog,this}}let Ar;const ya=new V,Rr=new V,Cr=new V,Pr=new $e,Ma=new $e,fp=new Bt,To=new V,Sa=new V,Ao=new V,Md=new $e,dc=new $e,Sd=new $e;class pp extends en{constructor(e=new ji){if(super(),this.isSprite=!0,this.type="Sprite",Ar===void 0){Ar=new Gt;const t=new Float32Array([-.5,-.5,0,0,0,.5,-.5,0,1,0,.5,.5,0,1,1,-.5,.5,0,0,1]),n=new Qy(t,5);Ar.setIndex([0,1,2,0,2,3]),Ar.setAttribute("position",new el(n,3,0,!1)),Ar.setAttribute("uv",new el(n,2,3,!1))}this.geometry=Ar,this.material=e,this.center=new $e(.5,.5)}raycast(e,t){e.camera===null&&console.error('THREE.Sprite: "Raycaster.camera" needs to be set in order to raycast against sprites.'),Rr.setFromMatrixScale(this.matrixWorld),fp.copy(e.camera.matrixWorld),this.modelViewMatrix.multiplyMatrices(e.camera.matrixWorldInverse,this.matrixWorld),Cr.setFromMatrixPosition(this.modelViewMatrix),e.camera.isPerspectiveCamera&&this.material.sizeAttenuation===!1&&Rr.multiplyScalar(-Cr.z);const n=this.material.rotation;let s,r;n!==0&&(r=Math.cos(n),s=Math.sin(n));const a=this.center;Ro(To.set(-.5,-.5,0),Cr,a,Rr,s,r),Ro(Sa.set(.5,-.5,0),Cr,a,Rr,s,r),Ro(Ao.set(.5,.5,0),Cr,a,Rr,s,r),Md.set(0,0),dc.set(1,0),Sd.set(1,1);let o=e.ray.intersectTriangle(To,Sa,Ao,!1,ya);if(o===null&&(Ro(Sa.set(-.5,.5,0),Cr,a,Rr,s,r),dc.set(0,1),o=e.ray.intersectTriangle(To,Ao,Sa,!1,ya),o===null))return;const l=e.ray.origin.distanceTo(ya);l<e.near||l>e.far||t.push({distance:l,point:ya.clone(),uv:Qn.getInterpolation(ya,To,Sa,Ao,Md,dc,Sd,new $e),face:null,object:this})}copy(e,t){return super.copy(e,t),e.center!==void 0&&this.center.copy(e.center),this.material=e.material,this}}function Ro(i,e,t,n,s,r){Pr.subVectors(i,t).addScalar(.5).multiply(n),s!==void 0?(Ma.x=r*Pr.x-s*Pr.y,Ma.y=s*Pr.x+r*Pr.y):Ma.copy(Pr),i.copy(e),i.x+=Ma.x,i.y+=Ma.y,i.applyMatrix4(fp)}class Ai extends Ss{constructor(e){super(),this.isLineBasicMaterial=!0,this.type="LineBasicMaterial",this.color=new nt(16777215),this.map=null,this.linewidth=1,this.linecap="round",this.linejoin="round",this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.linewidth=e.linewidth,this.linecap=e.linecap,this.linejoin=e.linejoin,this.fog=e.fog,this}}const tl=new V,nl=new V,bd=new Bt,ba=new qa,Co=new Xa,fc=new V,wd=new V;class il extends en{constructor(e=new Gt,t=new Ai){super(),this.isLine=!0,this.type="Line",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}computeLineDistances(){const e=this.geometry;if(e.index===null){const t=e.attributes.position,n=[0];for(let s=1,r=t.count;s<r;s++)tl.fromBufferAttribute(t,s-1),nl.fromBufferAttribute(t,s),n[s]=n[s-1],n[s]+=tl.distanceTo(nl);e.setAttribute("lineDistance",new zt(n,1))}else console.warn("THREE.Line.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.");return this}raycast(e,t){const n=this.geometry,s=this.matrixWorld,r=e.params.Line.threshold,a=n.drawRange;if(n.boundingSphere===null&&n.computeBoundingSphere(),Co.copy(n.boundingSphere),Co.applyMatrix4(s),Co.radius+=r,e.ray.intersectsSphere(Co)===!1)return;bd.copy(s).invert(),ba.copy(e.ray).applyMatrix4(bd);const o=r/((this.scale.x+this.scale.y+this.scale.z)/3),l=o*o,c=this.isLineSegments?2:1,h=n.index,d=n.attributes.position;if(h!==null){const f=Math.max(0,a.start),g=Math.min(h.count,a.start+a.count);for(let _=f,p=g-1;_<p;_+=c){const m=h.getX(_),M=h.getX(_+1),v=Po(this,e,ba,l,m,M);v&&t.push(v)}if(this.isLineLoop){const _=h.getX(g-1),p=h.getX(f),m=Po(this,e,ba,l,_,p);m&&t.push(m)}}else{const f=Math.max(0,a.start),g=Math.min(d.count,a.start+a.count);for(let _=f,p=g-1;_<p;_+=c){const m=Po(this,e,ba,l,_,_+1);m&&t.push(m)}if(this.isLineLoop){const _=Po(this,e,ba,l,g-1,f);_&&t.push(_)}}}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const s=t[n[0]];if(s!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let r=0,a=s.length;r<a;r++){const o=s[r].name||String(r);this.morphTargetInfluences.push(0),this.morphTargetDictionary[o]=r}}}}}function Po(i,e,t,n,s,r){const a=i.geometry.attributes.position;if(tl.fromBufferAttribute(a,s),nl.fromBufferAttribute(a,r),t.distanceSqToSegment(tl,nl,fc,wd)>n)return;fc.applyMatrix4(i.matrixWorld);const l=e.ray.origin.distanceTo(fc);if(!(l<e.near||l>e.far))return{distance:l,point:wd.clone().applyMatrix4(i.matrixWorld),index:s,face:null,faceIndex:null,object:i}}const Ed=new V,Td=new V;class Ws extends il{constructor(e,t){super(e,t),this.isLineSegments=!0,this.type="LineSegments"}computeLineDistances(){const e=this.geometry;if(e.index===null){const t=e.attributes.position,n=[];for(let s=0,r=t.count;s<r;s+=2)Ed.fromBufferAttribute(t,s),Td.fromBufferAttribute(t,s+1),n[s]=s===0?0:n[s-1],n[s+1]=n[s]+Ed.distanceTo(Td);e.setAttribute("lineDistance",new zt(n,1))}else console.warn("THREE.LineSegments.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.");return this}}class Nh extends Ss{constructor(e){super(),this.isPointsMaterial=!0,this.type="PointsMaterial",this.color=new nt(16777215),this.map=null,this.alphaMap=null,this.size=1,this.sizeAttenuation=!0,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.alphaMap=e.alphaMap,this.size=e.size,this.sizeAttenuation=e.sizeAttenuation,this.fog=e.fog,this}}const Ad=new Bt,lh=new qa,Lo=new Xa,Do=new V;class mp extends en{constructor(e=new Gt,t=new Nh){super(),this.isPoints=!0,this.type="Points",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}raycast(e,t){const n=this.geometry,s=this.matrixWorld,r=e.params.Points.threshold,a=n.drawRange;if(n.boundingSphere===null&&n.computeBoundingSphere(),Lo.copy(n.boundingSphere),Lo.applyMatrix4(s),Lo.radius+=r,e.ray.intersectsSphere(Lo)===!1)return;Ad.copy(s).invert(),lh.copy(e.ray).applyMatrix4(Ad);const o=r/((this.scale.x+this.scale.y+this.scale.z)/3),l=o*o,c=n.index,u=n.attributes.position;if(c!==null){const d=Math.max(0,a.start),f=Math.min(c.count,a.start+a.count);for(let g=d,_=f;g<_;g++){const p=c.getX(g);Do.fromBufferAttribute(u,p),Rd(Do,p,l,s,e,t,this)}}else{const d=Math.max(0,a.start),f=Math.min(u.count,a.start+a.count);for(let g=d,_=f;g<_;g++)Do.fromBufferAttribute(u,g),Rd(Do,g,l,s,e,t,this)}}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const s=t[n[0]];if(s!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let r=0,a=s.length;r<a;r++){const o=s[r].name||String(r);this.morphTargetInfluences.push(0),this.morphTargetDictionary[o]=r}}}}}function Rd(i,e,t,n,s,r,a){const o=lh.distanceSqToPoint(i);if(o<t){const l=new V;lh.closestPointToPoint(i,l),l.applyMatrix4(n);const c=s.ray.origin.distanceTo(l);if(c<s.near||c>s.far)return;r.push({distance:c,distanceToRay:Math.sqrt(o),point:l,index:e,face:null,object:a})}}class Fh extends Ln{constructor(e,t,n,s,r,a,o,l,c){super(e,t,n,s,r,a,o,l,c),this.isCanvasTexture=!0,this.needsUpdate=!0}}const Io=new V,Uo=new V,pc=new V,No=new Qn;class eM extends Gt{constructor(e=null,t=1){if(super(),this.type="EdgesGeometry",this.parameters={geometry:e,thresholdAngle:t},e!==null){const s=Math.pow(10,4),r=Math.cos(zr*t),a=e.getIndex(),o=e.getAttribute("position"),l=a?a.count:o.count,c=[0,0,0],h=["a","b","c"],u=new Array(3),d={},f=[];for(let g=0;g<l;g+=3){a?(c[0]=a.getX(g),c[1]=a.getX(g+1),c[2]=a.getX(g+2)):(c[0]=g,c[1]=g+1,c[2]=g+2);const{a:_,b:p,c:m}=No;if(_.fromBufferAttribute(o,c[0]),p.fromBufferAttribute(o,c[1]),m.fromBufferAttribute(o,c[2]),No.getNormal(pc),u[0]=`${Math.round(_.x*s)},${Math.round(_.y*s)},${Math.round(_.z*s)}`,u[1]=`${Math.round(p.x*s)},${Math.round(p.y*s)},${Math.round(p.z*s)}`,u[2]=`${Math.round(m.x*s)},${Math.round(m.y*s)},${Math.round(m.z*s)}`,!(u[0]===u[1]||u[1]===u[2]||u[2]===u[0]))for(let M=0;M<3;M++){const v=(M+1)%3,b=u[M],N=u[v],A=No[h[M]],R=No[h[v]],F=`${b}_${N}`,w=`${N}_${b}`;w in d&&d[w]?(pc.dot(d[w].normal)<=r&&(f.push(A.x,A.y,A.z),f.push(R.x,R.y,R.z)),d[w]=null):F in d||(d[F]={index0:c[M],index1:c[v],normal:pc.clone()})}}for(const g in d)if(d[g]){const{index0:_,index1:p}=d[g];Io.fromBufferAttribute(o,_),Uo.fromBufferAttribute(o,p),f.push(Io.x,Io.y,Io.z),f.push(Uo.x,Uo.y,Uo.z)}this.setAttribute("position",new zt(f,3))}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}}class Oh extends Gt{constructor(e=.5,t=1,n=32,s=1,r=0,a=Math.PI*2){super(),this.type="RingGeometry",this.parameters={innerRadius:e,outerRadius:t,thetaSegments:n,phiSegments:s,thetaStart:r,thetaLength:a},n=Math.max(3,n),s=Math.max(1,s);const o=[],l=[],c=[],h=[];let u=e;const d=(t-e)/s,f=new V,g=new $e;for(let _=0;_<=s;_++){for(let p=0;p<=n;p++){const m=r+p/n*a;f.x=u*Math.cos(m),f.y=u*Math.sin(m),l.push(f.x,f.y,f.z),c.push(0,0,1),g.x=(f.x/t+1)/2,g.y=(f.y/t+1)/2,h.push(g.x,g.y)}u+=d}for(let _=0;_<s;_++){const p=_*(n+1);for(let m=0;m<n;m++){const M=m+p,v=M,b=M+n+1,N=M+n+2,A=M+1;o.push(v,b,A),o.push(b,N,A)}}this.setIndex(o),this.setAttribute("position",new zt(l,3)),this.setAttribute("normal",new zt(c,3)),this.setAttribute("uv",new zt(h,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Oh(e.innerRadius,e.outerRadius,e.thetaSegments,e.phiSegments,e.thetaStart,e.thetaLength)}}class Ia extends Ss{constructor(e){super(),this.isMeshStandardMaterial=!0,this.defines={STANDARD:""},this.type="MeshStandardMaterial",this.color=new nt(16777215),this.roughness=1,this.metalness=0,this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.emissive=new nt(0),this.emissiveIntensity=1,this.emissiveMap=null,this.bumpMap=null,this.bumpScale=1,this.normalMap=null,this.normalMapType=jf,this.normalScale=new $e(1,1),this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.roughnessMap=null,this.metalnessMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new Ci,this.envMapIntensity=1,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.flatShading=!1,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.defines={STANDARD:""},this.color.copy(e.color),this.roughness=e.roughness,this.metalness=e.metalness,this.map=e.map,this.lightMap=e.lightMap,this.lightMapIntensity=e.lightMapIntensity,this.aoMap=e.aoMap,this.aoMapIntensity=e.aoMapIntensity,this.emissive.copy(e.emissive),this.emissiveMap=e.emissiveMap,this.emissiveIntensity=e.emissiveIntensity,this.bumpMap=e.bumpMap,this.bumpScale=e.bumpScale,this.normalMap=e.normalMap,this.normalMapType=e.normalMapType,this.normalScale.copy(e.normalScale),this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this.roughnessMap=e.roughnessMap,this.metalnessMap=e.metalnessMap,this.alphaMap=e.alphaMap,this.envMap=e.envMap,this.envMapRotation.copy(e.envMapRotation),this.envMapIntensity=e.envMapIntensity,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.wireframeLinecap=e.wireframeLinecap,this.wireframeLinejoin=e.wireframeLinejoin,this.flatShading=e.flatShading,this.fog=e.fog,this}}class gp extends Ai{constructor(e){super(),this.isLineDashedMaterial=!0,this.type="LineDashedMaterial",this.scale=1,this.dashSize=3,this.gapSize=1,this.setValues(e)}copy(e){return super.copy(e),this.scale=e.scale,this.dashSize=e.dashSize,this.gapSize=e.gapSize,this}}class Bh extends en{constructor(e,t=1){super(),this.isLight=!0,this.type="Light",this.color=new nt(e),this.intensity=t}dispose(){}copy(e,t){return super.copy(e,t),this.color.copy(e.color),this.intensity=e.intensity,this}toJSON(e){const t=super.toJSON(e);return t.object.color=this.color.getHex(),t.object.intensity=this.intensity,this.groundColor!==void 0&&(t.object.groundColor=this.groundColor.getHex()),this.distance!==void 0&&(t.object.distance=this.distance),this.angle!==void 0&&(t.object.angle=this.angle),this.decay!==void 0&&(t.object.decay=this.decay),this.penumbra!==void 0&&(t.object.penumbra=this.penumbra),this.shadow!==void 0&&(t.object.shadow=this.shadow.toJSON()),this.target!==void 0&&(t.object.target=this.target.uuid),t}}class tM extends Bh{constructor(e,t,n){super(e,n),this.isHemisphereLight=!0,this.type="HemisphereLight",this.position.copy(en.DEFAULT_UP),this.updateMatrix(),this.groundColor=new nt(t)}copy(e,t){return super.copy(e,t),this.groundColor.copy(e.groundColor),this}}const mc=new Bt,Cd=new V,Pd=new V;class nM{constructor(e){this.camera=e,this.intensity=1,this.bias=0,this.normalBias=0,this.radius=1,this.blurSamples=8,this.mapSize=new $e(512,512),this.map=null,this.mapPass=null,this.matrix=new Bt,this.autoUpdate=!0,this.needsUpdate=!1,this._frustum=new Lh,this._frameExtents=new $e(1,1),this._viewportCount=1,this._viewports=[new sn(0,0,1,1)]}getViewportCount(){return this._viewportCount}getFrustum(){return this._frustum}updateMatrices(e){const t=this.camera,n=this.matrix;Cd.setFromMatrixPosition(e.matrixWorld),t.position.copy(Cd),Pd.setFromMatrixPosition(e.target.matrixWorld),t.lookAt(Pd),t.updateMatrixWorld(),mc.multiplyMatrices(t.projectionMatrix,t.matrixWorldInverse),this._frustum.setFromProjectionMatrix(mc),n.set(.5,0,0,.5,0,.5,0,.5,0,0,.5,.5,0,0,0,1),n.multiply(mc)}getViewport(e){return this._viewports[e]}getFrameExtents(){return this._frameExtents}dispose(){this.map&&this.map.dispose(),this.mapPass&&this.mapPass.dispose()}copy(e){return this.camera=e.camera.clone(),this.intensity=e.intensity,this.bias=e.bias,this.radius=e.radius,this.mapSize.copy(e.mapSize),this}clone(){return new this.constructor().copy(this)}toJSON(){const e={};return this.intensity!==1&&(e.intensity=this.intensity),this.bias!==0&&(e.bias=this.bias),this.normalBias!==0&&(e.normalBias=this.normalBias),this.radius!==1&&(e.radius=this.radius),(this.mapSize.x!==512||this.mapSize.y!==512)&&(e.mapSize=this.mapSize.toArray()),e.camera=this.camera.toJSON(!1).object,delete e.camera.matrix,e}}class iM extends nM{constructor(){super(new Vr(-5,5,5,-5,.5,500)),this.isDirectionalLightShadow=!0}}class sM extends Bh{constructor(e,t){super(e,t),this.isDirectionalLight=!0,this.type="DirectionalLight",this.position.copy(en.DEFAULT_UP),this.updateMatrix(),this.target=new en,this.shadow=new iM}dispose(){this.shadow.dispose()}copy(e){return super.copy(e),this.target=e.target.clone(),this.shadow=e.shadow.clone(),this}}class rM extends Bh{constructor(e,t){super(e,t),this.isAmbientLight=!0,this.type="AmbientLight"}}const Ld=new Bt;class aM{constructor(e,t,n=0,s=1/0){this.ray=new qa(e,t),this.near=n,this.far=s,this.camera=null,this.layers=new Ph,this.params={Mesh:{},Line:{threshold:1},LOD:{},Points:{threshold:1},Sprite:{}}}set(e,t){this.ray.set(e,t)}setFromCamera(e,t){t.isPerspectiveCamera?(this.ray.origin.setFromMatrixPosition(t.matrixWorld),this.ray.direction.set(e.x,e.y,.5).unproject(t).sub(this.ray.origin).normalize(),this.camera=t):t.isOrthographicCamera?(this.ray.origin.set(e.x,e.y,(t.near+t.far)/(t.near-t.far)).unproject(t),this.ray.direction.set(0,0,-1).transformDirection(t.matrixWorld),this.camera=t):console.error("THREE.Raycaster: Unsupported camera type: "+t.type)}setFromXRController(e){return Ld.identity().extractRotation(e.matrixWorld),this.ray.origin.setFromMatrixPosition(e.matrixWorld),this.ray.direction.set(0,0,-1).applyMatrix4(Ld),this}intersectObject(e,t=!0,n=[]){return ch(e,this,n,t),n.sort(Dd),n}intersectObjects(e,t=!0,n=[]){for(let s=0,r=e.length;s<r;s++)ch(e[s],this,n,t);return n.sort(Dd),n}}function Dd(i,e){return i.distance-e.distance}function ch(i,e,t,n){let s=!0;if(i.layers.test(e.layers)&&i.raycast(e,t)===!1&&(s=!1),s===!0&&n===!0){const r=i.children;for(let a=0,o=r.length;a<o;a++)ch(r[a],e,t,!0)}}class Id{constructor(e=1,t=0,n=0){return this.radius=e,this.phi=t,this.theta=n,this}set(e,t,n){return this.radius=e,this.phi=t,this.theta=n,this}copy(e){return this.radius=e.radius,this.phi=e.phi,this.theta=e.theta,this}makeSafe(){return this.phi=Math.max(1e-6,Math.min(Math.PI-1e-6,this.phi)),this}setFromVector3(e){return this.setFromCartesianCoords(e.x,e.y,e.z)}setFromCartesianCoords(e,t,n){return this.radius=Math.sqrt(e*e+t*t+n*n),this.radius===0?(this.theta=0,this.phi=0):(this.theta=Math.atan2(e,n),this.phi=Math.acos(Sn(t/this.radius,-1,1))),this}clone(){return new this.constructor().copy(this)}}class oM extends Ws{constructor(e=10,t=10,n=4473924,s=8947848){n=new nt(n),s=new nt(s);const r=t/2,a=e/t,o=e/2,l=[],c=[];for(let d=0,f=0,g=-o;d<=t;d++,g+=a){l.push(-o,0,g,o,0,g),l.push(g,0,-o,g,0,o);const _=d===r?n:s;_.toArray(c,f),f+=3,_.toArray(c,f),f+=3,_.toArray(c,f),f+=3,_.toArray(c,f),f+=3}const h=new Gt;h.setAttribute("position",new zt(l,3)),h.setAttribute("color",new zt(c,3));const u=new Ai({vertexColors:!0,toneMapped:!1});super(h,u),this.type="GridHelper"}dispose(){this.geometry.dispose(),this.material.dispose()}}typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("register",{detail:{revision:Mh}}));typeof window<"u"&&(window.__THREE__?console.warn("WARNING: Multiple instances of Three.js being imported."):window.__THREE__=Mh);var lM=Object.defineProperty,cM=(i,e,t)=>e in i?lM(i,e,{enumerable:!0,configurable:!0,writable:!0,value:t}):i[e]=t,hM=(i,e,t)=>(cM(i,e+"",t),t);class uM{constructor(){hM(this,"_listeners")}addEventListener(e,t){this._listeners===void 0&&(this._listeners={});const n=this._listeners;n[e]===void 0&&(n[e]=[]),n[e].indexOf(t)===-1&&n[e].push(t)}hasEventListener(e,t){if(this._listeners===void 0)return!1;const n=this._listeners;return n[e]!==void 0&&n[e].indexOf(t)!==-1}removeEventListener(e,t){if(this._listeners===void 0)return;const s=this._listeners[e];if(s!==void 0){const r=s.indexOf(t);r!==-1&&s.splice(r,1)}}dispatchEvent(e){if(this._listeners===void 0)return;const n=this._listeners[e.type];if(n!==void 0){e.target=this;const s=n.slice(0);for(let r=0,a=s.length;r<a;r++)s[r].call(this,e);e.target=null}}}var dM=Object.defineProperty,fM=(i,e,t)=>e in i?dM(i,e,{enumerable:!0,configurable:!0,writable:!0,value:t}):i[e]=t,je=(i,e,t)=>(fM(i,typeof e!="symbol"?e+"":e,t),t);const Fo=new qa,Ud=new cs,pM=Math.cos(70*(Math.PI/180)),Nd=(i,e)=>(i%e+e)%e;class mM extends uM{constructor(e,t){super(),je(this,"object"),je(this,"domElement"),je(this,"enabled",!0),je(this,"target",new V),je(this,"minDistance",0),je(this,"maxDistance",1/0),je(this,"minZoom",0),je(this,"maxZoom",1/0),je(this,"minPolarAngle",0),je(this,"maxPolarAngle",Math.PI),je(this,"minAzimuthAngle",-1/0),je(this,"maxAzimuthAngle",1/0),je(this,"enableDamping",!1),je(this,"dampingFactor",.05),je(this,"enableZoom",!0),je(this,"zoomSpeed",1),je(this,"enableRotate",!0),je(this,"rotateSpeed",1),je(this,"enablePan",!0),je(this,"panSpeed",1),je(this,"screenSpacePanning",!0),je(this,"keyPanSpeed",7),je(this,"zoomToCursor",!1),je(this,"autoRotate",!1),je(this,"autoRotateSpeed",2),je(this,"reverseOrbit",!1),je(this,"reverseHorizontalOrbit",!1),je(this,"reverseVerticalOrbit",!1),je(this,"keys",{LEFT:"ArrowLeft",UP:"ArrowUp",RIGHT:"ArrowRight",BOTTOM:"ArrowDown"}),je(this,"mouseButtons",{LEFT:lr.ROTATE,MIDDLE:lr.DOLLY,RIGHT:lr.PAN}),je(this,"touches",{ONE:cr.ROTATE,TWO:cr.DOLLY_PAN}),je(this,"target0"),je(this,"position0"),je(this,"zoom0"),je(this,"_domElementKeyEvents",null),je(this,"getPolarAngle"),je(this,"getAzimuthalAngle"),je(this,"setPolarAngle"),je(this,"setAzimuthalAngle"),je(this,"getDistance"),je(this,"getZoomScale"),je(this,"listenToKeyEvents"),je(this,"stopListenToKeyEvents"),je(this,"saveState"),je(this,"reset"),je(this,"update"),je(this,"connect"),je(this,"dispose"),je(this,"dollyIn"),je(this,"dollyOut"),je(this,"getScale"),je(this,"setScale"),this.object=e,this.domElement=t,this.target0=this.target.clone(),this.position0=this.object.position.clone(),this.zoom0=this.object.zoom,this.getPolarAngle=()=>h.phi,this.getAzimuthalAngle=()=>h.theta,this.setPolarAngle=B=>{let ce=Nd(B,2*Math.PI),U=h.phi;U<0&&(U+=2*Math.PI),ce<0&&(ce+=2*Math.PI);let ae=Math.abs(ce-U);2*Math.PI-ae<ae&&(ce<U?ce+=2*Math.PI:U+=2*Math.PI),u.phi=ce-U,n.update()},this.setAzimuthalAngle=B=>{let ce=Nd(B,2*Math.PI),U=h.theta;U<0&&(U+=2*Math.PI),ce<0&&(ce+=2*Math.PI);let ae=Math.abs(ce-U);2*Math.PI-ae<ae&&(ce<U?ce+=2*Math.PI:U+=2*Math.PI),u.theta=ce-U,n.update()},this.getDistance=()=>n.object.position.distanceTo(n.target),this.listenToKeyEvents=B=>{B.addEventListener("keydown",Re),this._domElementKeyEvents=B},this.stopListenToKeyEvents=()=>{this._domElementKeyEvents.removeEventListener("keydown",Re),this._domElementKeyEvents=null},this.saveState=()=>{n.target0.copy(n.target),n.position0.copy(n.object.position),n.zoom0=n.object.zoom},this.reset=()=>{n.target.copy(n.target0),n.object.position.copy(n.position0),n.object.zoom=n.zoom0,n.object.updateProjectionMatrix(),n.dispatchEvent(s),n.update(),l=o.NONE},this.update=(()=>{const B=new V,ce=new V(0,1,0),U=new Ys().setFromUnitVectors(e.up,ce),ae=U.clone().invert(),se=new V,re=new Ys,xe=2*Math.PI;return function(){const ot=n.object.position;U.setFromUnitVectors(e.up,ce),ae.copy(U).invert(),B.copy(ot).sub(n.target),B.applyQuaternion(U),h.setFromVector3(B),n.autoRotate&&l===o.NONE&&Z(K()),n.enableDamping?(h.theta+=u.theta*n.dampingFactor,h.phi+=u.phi*n.dampingFactor):(h.theta+=u.theta,h.phi+=u.phi);let _t=n.minAzimuthAngle,Et=n.maxAzimuthAngle;isFinite(_t)&&isFinite(Et)&&(_t<-Math.PI?_t+=xe:_t>Math.PI&&(_t-=xe),Et<-Math.PI?Et+=xe:Et>Math.PI&&(Et-=xe),_t<=Et?h.theta=Math.max(_t,Math.min(Et,h.theta)):h.theta=h.theta>(_t+Et)/2?Math.max(_t,h.theta):Math.min(Et,h.theta)),h.phi=Math.max(n.minPolarAngle,Math.min(n.maxPolarAngle,h.phi)),h.makeSafe(),n.enableDamping===!0?n.target.addScaledVector(f,n.dampingFactor):n.target.add(f),n.zoomToCursor&&w||n.object.isOrthographicCamera?h.radius=ye(h.radius):h.radius=ye(h.radius*d),B.setFromSpherical(h),B.applyQuaternion(ae),ot.copy(n.target).add(B),n.object.matrixAutoUpdate||n.object.updateMatrix(),n.object.lookAt(n.target),n.enableDamping===!0?(u.theta*=1-n.dampingFactor,u.phi*=1-n.dampingFactor,f.multiplyScalar(1-n.dampingFactor)):(u.set(0,0,0),f.set(0,0,0));let lt=!1;if(n.zoomToCursor&&w){let mn=null;if(n.object instanceof bn&&n.object.isPerspectiveCamera){const kt=B.length();mn=ye(kt*d);const Ht=kt-mn;n.object.position.addScaledVector(R,Ht),n.object.updateMatrixWorld()}else if(n.object.isOrthographicCamera){const kt=new V(F.x,F.y,0);kt.unproject(n.object),n.object.zoom=Math.max(n.minZoom,Math.min(n.maxZoom,n.object.zoom/d)),n.object.updateProjectionMatrix(),lt=!0;const Ht=new V(F.x,F.y,0);Ht.unproject(n.object),n.object.position.sub(Ht).add(kt),n.object.updateMatrixWorld(),mn=B.length()}else console.warn("WARNING: OrbitControls.js encountered an unknown camera type - zoom to cursor disabled."),n.zoomToCursor=!1;mn!==null&&(n.screenSpacePanning?n.target.set(0,0,-1).transformDirection(n.object.matrix).multiplyScalar(mn).add(n.object.position):(Fo.origin.copy(n.object.position),Fo.direction.set(0,0,-1).transformDirection(n.object.matrix),Math.abs(n.object.up.dot(Fo.direction))<pM?e.lookAt(n.target):(Ud.setFromNormalAndCoplanarPoint(n.object.up,n.target),Fo.intersectPlane(Ud,n.target))))}else n.object instanceof Vr&&n.object.isOrthographicCamera&&(lt=d!==1,lt&&(n.object.zoom=Math.max(n.minZoom,Math.min(n.maxZoom,n.object.zoom/d)),n.object.updateProjectionMatrix()));return d=1,w=!1,lt||se.distanceToSquared(n.object.position)>c||8*(1-re.dot(n.object.quaternion))>c?(n.dispatchEvent(s),se.copy(n.object.position),re.copy(n.object.quaternion),lt=!1,!0):!1}})(),this.connect=B=>{n.domElement=B,n.domElement.style.touchAction="none",n.domElement.addEventListener("contextmenu",Ae),n.domElement.addEventListener("pointerdown",Q),n.domElement.addEventListener("pointercancel",te),n.domElement.addEventListener("wheel",_e)},this.dispose=()=>{var B,ce,U,ae,se,re;n.domElement&&(n.domElement.style.touchAction="auto"),(B=n.domElement)==null||B.removeEventListener("contextmenu",Ae),(ce=n.domElement)==null||ce.removeEventListener("pointerdown",Q),(U=n.domElement)==null||U.removeEventListener("pointercancel",te),(ae=n.domElement)==null||ae.removeEventListener("wheel",_e),(se=n.domElement)==null||se.ownerDocument.removeEventListener("pointermove",le),(re=n.domElement)==null||re.ownerDocument.removeEventListener("pointerup",te),n._domElementKeyEvents!==null&&n._domElementKeyEvents.removeEventListener("keydown",Re)};const n=this,s={type:"change"},r={type:"start"},a={type:"end"},o={NONE:-1,ROTATE:0,DOLLY:1,PAN:2,TOUCH_ROTATE:3,TOUCH_PAN:4,TOUCH_DOLLY_PAN:5,TOUCH_DOLLY_ROTATE:6};let l=o.NONE;const c=1e-6,h=new Id,u=new Id;let d=1;const f=new V,g=new $e,_=new $e,p=new $e,m=new $e,M=new $e,v=new $e,b=new $e,N=new $e,A=new $e,R=new V,F=new $e;let w=!1;const y=[],P={};function K(){return 2*Math.PI/60/60*n.autoRotateSpeed}function H(){return Math.pow(.95,n.zoomSpeed)}function Z(B){n.reverseOrbit||n.reverseHorizontalOrbit?u.theta+=B:u.theta-=B}function q(B){n.reverseOrbit||n.reverseVerticalOrbit?u.phi+=B:u.phi-=B}const ee=(()=>{const B=new V;return function(U,ae){B.setFromMatrixColumn(ae,0),B.multiplyScalar(-U),f.add(B)}})(),Y=(()=>{const B=new V;return function(U,ae){n.screenSpacePanning===!0?B.setFromMatrixColumn(ae,1):(B.setFromMatrixColumn(ae,0),B.crossVectors(n.object.up,B)),B.multiplyScalar(U),f.add(B)}})(),ne=(()=>{const B=new V;return function(U,ae){const se=n.domElement;if(se&&n.object instanceof bn&&n.object.isPerspectiveCamera){const re=n.object.position;B.copy(re).sub(n.target);let xe=B.length();xe*=Math.tan(n.object.fov/2*Math.PI/180),ee(2*U*xe/se.clientHeight,n.object.matrix),Y(2*ae*xe/se.clientHeight,n.object.matrix)}else se&&n.object instanceof Vr&&n.object.isOrthographicCamera?(ee(U*(n.object.right-n.object.left)/n.object.zoom/se.clientWidth,n.object.matrix),Y(ae*(n.object.top-n.object.bottom)/n.object.zoom/se.clientHeight,n.object.matrix)):(console.warn("WARNING: OrbitControls.js encountered an unknown camera type - pan disabled."),n.enablePan=!1)}})();function ge(B){n.object instanceof bn&&n.object.isPerspectiveCamera||n.object instanceof Vr&&n.object.isOrthographicCamera?d=B:(console.warn("WARNING: OrbitControls.js encountered an unknown camera type - dolly/zoom disabled."),n.enableZoom=!1)}function de(B){ge(d/B)}function ve(B){ge(d*B)}function Te(B){if(!n.zoomToCursor||!n.domElement)return;w=!0;const ce=n.domElement.getBoundingClientRect(),U=B.clientX-ce.left,ae=B.clientY-ce.top,se=ce.width,re=ce.height;F.x=U/se*2-1,F.y=-(ae/re)*2+1,R.set(F.x,F.y,1).unproject(n.object).sub(n.object.position).normalize()}function ye(B){return Math.max(n.minDistance,Math.min(n.maxDistance,B))}function ie(B){g.set(B.clientX,B.clientY)}function he(B){Te(B),b.set(B.clientX,B.clientY)}function Me(B){m.set(B.clientX,B.clientY)}function fe(B){_.set(B.clientX,B.clientY),p.subVectors(_,g).multiplyScalar(n.rotateSpeed);const ce=n.domElement;ce&&(Z(2*Math.PI*p.x/ce.clientHeight),q(2*Math.PI*p.y/ce.clientHeight)),g.copy(_),n.update()}function ze(B){N.set(B.clientX,B.clientY),A.subVectors(N,b),A.y>0?de(H()):A.y<0&&ve(H()),b.copy(N),n.update()}function Ge(B){M.set(B.clientX,B.clientY),v.subVectors(M,m).multiplyScalar(n.panSpeed),ne(v.x,v.y),m.copy(M),n.update()}function Fe(B){Te(B),B.deltaY<0?ve(H()):B.deltaY>0&&de(H()),n.update()}function pt(B){let ce=!1;switch(B.code){case n.keys.UP:ne(0,n.keyPanSpeed),ce=!0;break;case n.keys.BOTTOM:ne(0,-n.keyPanSpeed),ce=!0;break;case n.keys.LEFT:ne(n.keyPanSpeed,0),ce=!0;break;case n.keys.RIGHT:ne(-n.keyPanSpeed,0),ce=!0;break}ce&&(B.preventDefault(),n.update())}function O(){if(y.length==1)g.set(y[0].pageX,y[0].pageY);else{const B=.5*(y[0].pageX+y[1].pageX),ce=.5*(y[0].pageY+y[1].pageY);g.set(B,ce)}}function dt(){if(y.length==1)m.set(y[0].pageX,y[0].pageY);else{const B=.5*(y[0].pageX+y[1].pageX),ce=.5*(y[0].pageY+y[1].pageY);m.set(B,ce)}}function st(){const B=y[0].pageX-y[1].pageX,ce=y[0].pageY-y[1].pageY,U=Math.sqrt(B*B+ce*ce);b.set(0,U)}function ct(){n.enableZoom&&st(),n.enablePan&&dt()}function Oe(){n.enableZoom&&st(),n.enableRotate&&O()}function wt(B){if(y.length==1)_.set(B.pageX,B.pageY);else{const U=He(B),ae=.5*(B.pageX+U.x),se=.5*(B.pageY+U.y);_.set(ae,se)}p.subVectors(_,g).multiplyScalar(n.rotateSpeed);const ce=n.domElement;ce&&(Z(2*Math.PI*p.x/ce.clientHeight),q(2*Math.PI*p.y/ce.clientHeight)),g.copy(_)}function Ye(B){if(y.length==1)M.set(B.pageX,B.pageY);else{const ce=He(B),U=.5*(B.pageX+ce.x),ae=.5*(B.pageY+ce.y);M.set(U,ae)}v.subVectors(M,m).multiplyScalar(n.panSpeed),ne(v.x,v.y),m.copy(M)}function qe(B){const ce=He(B),U=B.pageX-ce.x,ae=B.pageY-ce.y,se=Math.sqrt(U*U+ae*ae);N.set(0,se),A.set(0,Math.pow(N.y/b.y,n.zoomSpeed)),de(A.y),b.copy(N)}function D(B){n.enableZoom&&qe(B),n.enablePan&&Ye(B)}function E(B){n.enableZoom&&qe(B),n.enableRotate&&wt(B)}function Q(B){var ce,U;n.enabled!==!1&&(y.length===0&&((ce=n.domElement)==null||ce.ownerDocument.addEventListener("pointermove",le),(U=n.domElement)==null||U.ownerDocument.addEventListener("pointerup",te)),Je(B),B.pointerType==="touch"?Ze(B):X(B))}function le(B){n.enabled!==!1&&(B.pointerType==="touch"?me(B):we(B))}function te(B){var ce,U,ae;ke(B),y.length===0&&((ce=n.domElement)==null||ce.releasePointerCapture(B.pointerId),(U=n.domElement)==null||U.ownerDocument.removeEventListener("pointermove",le),(ae=n.domElement)==null||ae.ownerDocument.removeEventListener("pointerup",te)),n.dispatchEvent(a),l=o.NONE}function X(B){let ce;switch(B.button){case 0:ce=n.mouseButtons.LEFT;break;case 1:ce=n.mouseButtons.MIDDLE;break;case 2:ce=n.mouseButtons.RIGHT;break;default:ce=-1}switch(ce){case lr.DOLLY:if(n.enableZoom===!1)return;he(B),l=o.DOLLY;break;case lr.ROTATE:if(B.ctrlKey||B.metaKey||B.shiftKey){if(n.enablePan===!1)return;Me(B),l=o.PAN}else{if(n.enableRotate===!1)return;ie(B),l=o.ROTATE}break;case lr.PAN:if(B.ctrlKey||B.metaKey||B.shiftKey){if(n.enableRotate===!1)return;ie(B),l=o.ROTATE}else{if(n.enablePan===!1)return;Me(B),l=o.PAN}break;default:l=o.NONE}l!==o.NONE&&n.dispatchEvent(r)}function we(B){if(n.enabled!==!1)switch(l){case o.ROTATE:if(n.enableRotate===!1)return;fe(B);break;case o.DOLLY:if(n.enableZoom===!1)return;ze(B);break;case o.PAN:if(n.enablePan===!1)return;Ge(B);break}}function _e(B){n.enabled===!1||n.enableZoom===!1||l!==o.NONE&&l!==o.ROTATE||(B.preventDefault(),n.dispatchEvent(r),Fe(B),n.dispatchEvent(a))}function Re(B){n.enabled===!1||n.enablePan===!1||pt(B)}function Ze(B){switch(be(B),y.length){case 1:switch(n.touches.ONE){case cr.ROTATE:if(n.enableRotate===!1)return;O(),l=o.TOUCH_ROTATE;break;case cr.PAN:if(n.enablePan===!1)return;dt(),l=o.TOUCH_PAN;break;default:l=o.NONE}break;case 2:switch(n.touches.TWO){case cr.DOLLY_PAN:if(n.enableZoom===!1&&n.enablePan===!1)return;ct(),l=o.TOUCH_DOLLY_PAN;break;case cr.DOLLY_ROTATE:if(n.enableZoom===!1&&n.enableRotate===!1)return;Oe(),l=o.TOUCH_DOLLY_ROTATE;break;default:l=o.NONE}break;default:l=o.NONE}l!==o.NONE&&n.dispatchEvent(r)}function me(B){switch(be(B),l){case o.TOUCH_ROTATE:if(n.enableRotate===!1)return;wt(B),n.update();break;case o.TOUCH_PAN:if(n.enablePan===!1)return;Ye(B),n.update();break;case o.TOUCH_DOLLY_PAN:if(n.enableZoom===!1&&n.enablePan===!1)return;D(B),n.update();break;case o.TOUCH_DOLLY_ROTATE:if(n.enableZoom===!1&&n.enableRotate===!1)return;E(B),n.update();break;default:l=o.NONE}}function Ae(B){n.enabled!==!1&&B.preventDefault()}function Je(B){y.push(B)}function ke(B){delete P[B.pointerId];for(let ce=0;ce<y.length;ce++)if(y[ce].pointerId==B.pointerId){y.splice(ce,1);return}}function be(B){let ce=P[B.pointerId];ce===void 0&&(ce=new $e,P[B.pointerId]=ce),ce.set(B.pageX,B.pageY)}function He(B){const ce=B.pointerId===y[0].pointerId?y[1]:y[0];return P[ce.pointerId]}this.dollyIn=(B=H())=>{ve(B),n.update()},this.dollyOut=(B=H())=>{de(B),n.update()},this.getScale=()=>d,this.setScale=B=>{ge(B),n.update()},this.getZoomScale=()=>H(),t!==void 0&&this.connect(t),this.update()}}class gM{constructor(){I(this,"handlers",new Map);I(this,"onceHandlers",new Map);I(this,"messageBuffer",new Map)}register(e,t){if(!this.handlers.has(e)){this.handlers.set(e,new Set);const n=this.messageBuffer.get(e);n&&(n.forEach(s=>Promise.resolve(t(s))),this.messageBuffer.delete(e))}return this.handlers.get(e).add(t),()=>this.unregister(e,t)}once(e,t){return this.onceHandlers.has(e)||this.onceHandlers.set(e,new Set),this.onceHandlers.get(e).add(t),()=>this.unregisterOnce(e,t)}unregister(e,t){var n;(n=this.handlers.get(e))==null||n.delete(t)}unregisterOnce(e,t){var n;(n=this.onceHandlers.get(e))==null||n.delete(t)}buffer(e){const{type:t}=e;this.messageBuffer.has(t)||this.messageBuffer.set(t,[]),this.messageBuffer.get(t).push(e)}async dispatch(e){const{type:t,...n}=e,s=this.handlers.get(t);if(s&&s.size>0){await Promise.all(Array.from(s).map(a=>Promise.resolve(a(n))));return}const r=this.onceHandlers.get(t);if(r&&r.size>0){await Promise.all(Array.from(r).map(a=>Promise.resolve(a(n)))),this.onceHandlers.delete(t);return}this.buffer(e)}clear(){this.handlers.clear(),this.onceHandlers.clear(),this.messageBuffer.clear()}getBuffered(e){return this.messageBuffer.get(e)??[]}hasHandlers(e){var t;return(((t=this.handlers.get(e))==null?void 0:t.size)??0)>0}}class _M{constructor(e,t){I(this,"ws",null);I(this,"url");I(this,"router");I(this,"reconnectDelay",1e3);I(this,"maxReconnectDelay",3e4);I(this,"reconnectAttempts",0);I(this,"shouldReconnect",!0);I(this,"state","disconnected");I(this,"stateListeners",new Set);I(this,"messageQueue",[]);this.url=e,this.router=t}get connectionState(){return this.state}onStateChange(e){return this.stateListeners.add(e),e(this.state),()=>this.stateListeners.delete(e)}setState(e){this.state!==e&&(this.state=e,this.stateListeners.forEach(t=>t(e)))}connect(){var n;if(((n=this.ws)==null?void 0:n.readyState)===WebSocket.OPEN||this.state==="connecting")return;this.setState("connecting");const t=`${window.location.protocol==="https:"?"wss:":"ws:"}//${window.location.host}${this.url}`;this.ws=new WebSocket(t),this.ws.binaryType="arraybuffer",this.ws.onopen=()=>{console.log("[WS] Connected"),this.reconnectAttempts=0,this.reconnectDelay=1e3,this.setState("connected"),this.flushQueue()},this.ws.onmessage=async s=>{try{const r=JSON.parse(s.data);await this.router.dispatch(r)}catch(r){console.error("[WS] Failed to parse message:",r)}},this.ws.onclose=()=>{console.log("[WS] Disconnected"),this.setState("disconnected"),this.shouldReconnect&&this.scheduleReconnect()},this.ws.onerror=s=>{console.error("[WS] Error:",s)}}scheduleReconnect(){if(this.state==="reconnecting")return;this.setState("reconnecting");const e=Math.min(this.reconnectDelay*Math.pow(1.5,this.reconnectAttempts),this.maxReconnectDelay);this.reconnectAttempts++,console.log(`[WS] Reconnecting in ${e}ms (attempt ${this.reconnectAttempts})`),setTimeout(()=>this.connect(),e)}send(e){var t;((t=this.ws)==null?void 0:t.readyState)===WebSocket.OPEN?this.ws.send(JSON.stringify(e)):this.messageQueue.push(e)}flushQueue(){var e;for(;this.messageQueue.length>0&&((e=this.ws)==null?void 0:e.readyState)===WebSocket.OPEN;){const t=this.messageQueue.shift();this.ws.send(JSON.stringify(t))}}disconnect(){var e;this.shouldReconnect=!1,(e=this.ws)==null||e.close(),this.ws=null,this.setState("disconnected")}async waitForConnection(e=1e4){return this.state==="connected"?!0:new Promise(t=>{const n=setTimeout(()=>{s(),t(!1)},e),s=this.onStateChange(r=>{r==="connected"&&(clearTimeout(n),s(),t(!0))})})}get isConnected(){var e;return((e=this.ws)==null?void 0:e.readyState)===WebSocket.OPEN}}const jt=new gM,jr=new _M("/ws",jt);let _p=null;function xM(i){_p=i}function xs(){return _p}class vM{constructor(){I(this,"components",new Map);I(this,"initialized",!1)}register(e){const t=e.name||e.constructor.name;this.components.has(t)&&console.warn(`[ComponentRegistry] Component "${t}" already registered, replacing`),this.components.set(t,e),this.initialized&&e.init().catch(console.error)}unregister(e){const t=this.components.get(e);t&&(t.destroy().catch(console.error),this.components.delete(e))}async initAll(){this.initialized=!0;for(const[e,t]of this.components)try{await t.init(),console.log(`[ComponentRegistry] Initialized: ${e}`)}catch(n){console.error(`[ComponentRegistry] Failed to initialize ${e}:`,n)}}async destroyAll(){for(const[e,t]of this.components)try{await t.destroy(),console.log(`[ComponentRegistry] Destroyed: ${e}`)}catch(n){console.error(`[ComponentRegistry] Failed to destroy ${e}:`,n)}this.components.clear(),this.initialized=!1}get(e){return this.components.get(e)}list(){return Array.from(this.components.keys())}}const Ki=new vM;typeof window<"u"&&(document.addEventListener("DOMContentLoaded",()=>{Ki.initAll().catch(console.error)}),window.addEventListener("beforeunload",()=>{Ki.destroyAll().catch(console.error)}));const Xt={gradient:"#58a6ff",pepita:"#d4a843",random_projections:"#f78166",local_goodness:"#a371f7",thermodynamic_contrast:"#3fb950",contrastive:"#ff7b72",hebbian:"#79c0ff",predictive:"#d2a8ff"},z={bg:"#0a0e14",bg_tertiary:"#1a2330",border:"#2a3a4a",border_bright:"#3a4a5a",text_primary:"#e8ecf0",text_secondary:"#8b98a8",text_muted:"#5a6a7a",gradient:"#58a6ff",thermodynamic_contrast:"#3fb950",measured:"#d4a843",legal_unmeasured:"#58a6ff",void:"#f85149",pareto:"#e8ecf0",chance_line:"#f85149",gpu:"#58a6ff",cpu:"#3fb950",memory:"#d29922",ok:"#3fb950",warn:"#d29922",error:"#f85149",passed:"#3fb950",insufficient:"#d29922",rejected:"#f85149",promoted:"#a371f7",ramp_low:"#1f3a5f",ramp_mid:"#58a6ff",ramp_high:"#d4a843"};class yM{constructor(){I(this,"metricsByRun",new Map);I(this,"selectedRunId",null);I(this,"chosenByReader",!1);I(this,"listeners",[])}observe(e,t){this.metricsByRun.set(e,t),this.chosenByReader||(this.selectedRunId=this.newestRunId()),this.notify()}select(e){this.chosenByReader=!0,this.selectedRunId=e,this.notify()}get selectedId(){return this.selectedRunId}get selected(){return this.selectedRunId?this.metricsByRun.get(this.selectedRunId)??null:null}get runs(){return Array.from(this.metricsByRun.entries())}onChange(e){this.listeners.push(e)}notify(){this.listeners.forEach(e=>e(this.selectedRunId,this.selected))}newestRunId(){let e=null,t=-1/0;if(this.metricsByRun.forEach((s,r)=>{var l;const a=(l=s.run)==null?void 0:l.started_at,o=a?Date.parse(a):Number.NaN;Number.isNaN(o)||o>=t&&(t=o,e=r)}),e)return e;const n=this.metricsByRun.keys().next();return n.done?null:n.value}}const Zn=new yM,MM={substrate:{display_name:"Substrate",description:"Physical or computational substrate",primitives:[{name:"digital",summary:"Digital substrate: exact arithmetic, full precision",available:!0},{name:"analog",summary:"Analog substrate: continuous-valued physical state",available:!0},{name:"memristive",summary:"Memristive substrate: conductance, IR-drop, noise",available:!0},{name:"neuromorphic",summary:"Neuromorphic substrate: asynchronous spike events",available:!0},{name:"optical",summary:"Photonic substrate: phase/amplitude modulation",available:!0},{name:"quantum",summary:"Quantum substrate: unitary gate simulation",available:!0},{name:"complex",summary:"Complex-valued substrate",available:!0},{name:"sparse",summary:"Sparse substrate: sparsity-masked state",available:!0},{name:"ternary",summary:"Ternary substrate: weights in {-alpha, 0, +alpha}",available:!0}]},geometry:{display_name:"Geometry",description:"Network architecture and connectivity",primitives:[{name:"feedforward",summary:"Feedforward DAG (MLP/CNN)",available:!0},{name:"recurrent",summary:"Recurrent attractor (Hopfield/EqProp)",available:!0},{name:"causal_transformer",summary:"Causal transformer with KV cache",available:!0},{name:"tile",summary:"TileNet modular tile mesh",available:!0},{name:"tile_mesh",summary:"TileNet mesh topology",available:!0},{name:"conv",summary:"Convolutional geometry",available:!0},{name:"graph",summary:"Arbitrary node-edge fabric (FabricPC)",available:!0},{name:"attention",summary:"Attention geometry",available:!0},{name:"spatial_lattice",summary:"3-D spatial lattice (neural_cube)",available:!0},{name:"nca",summary:"Neural cellular automaton fabric",available:!0},{name:"ntm",summary:"Neural Turing Machine tape",available:!0}]},dynamics:{display_name:"Dynamics",description:"State evolution and settling",primitives:[{name:"energy_minimization",summary:"Equilibrium propagation energy minimization",available:!0},{name:"predictive_settling",summary:"Predictive coding settling",available:!0},{name:"error_predictive_coding",summary:"Error predictive coding",available:!0},{name:"spike_integration",summary:"LIF/Izhikevich spike integration",available:!0},{name:"instantaneous",summary:"Instantaneous pass (FF/Backprop)",available:!0},{name:"diffusion",summary:"Continuous-time diffusion settling",available:!0},{name:"lazy",summary:"Lazy/on-demand state dynamics",available:!0},{name:"pc_alm",summary:"Augmented Lagrangian predictive coding",available:!0}]},plasticity:{display_name:"Plasticity",description:"Local learning and adaptation",primitives:[{name:"null",summary:"Null plasticity (5-D slice)",available:!0},{name:"routing",summary:"Routing plasticity: state-dependent gating",available:!0},{name:"fast_weights",summary:"Fast-weight episode-local memory",available:!0},{name:"substrate_coupled",summary:"Physical substrate-coupled plasticity",available:!0},{name:"rule_state",summary:"Rule-state plasticity (Z3)",available:!0},{name:"temporal_psi",summary:"Trace-decayed supervised psi",available:!0},{name:"conflict_adaptive",summary:"Conflict-adaptive psi",available:!0}]},credit:{display_name:"Credit Assignment",description:"How learning signals reach parameters",primitives:[{name:"thermodynamic_contrast",summary:"EqProp free/nudged contrast (Scellier-Bengio)",available:!0},{name:"random_projections",summary:"Fixed random feedback (FA/DFA)",available:!0},{name:"local_goodness",summary:"Forward-Forward / PEPITA goodness",available:!0},{name:"local_contrastive",summary:"Local contrastive credit",available:!0},{name:"temporal_trace",summary:"Hebbian/STDP temporal trace",available:!0},{name:"target_inversion",summary:"Target propagation inversion",available:!0},{name:"homeostatic",summary:"Autonomous Lipschitz scaling",available:!0},{name:"pepita",summary:"PEPITA input-modulation credit",available:!0},{name:"gradient",summary:"Backprop gradient credit (ruler reference)",available:!0},{name:"pc_alm",summary:"PC-ALM primal-dual credit",available:!0}]},update:{display_name:"Update Rule",description:"How parameters are updated",primitives:[{name:"euclidean",summary:"SGD/Adam Euclidean update",available:!0},{name:"adam",summary:"Adam adaptive moment",available:!0},{name:"local_adam",summary:"Local Adam",available:!0},{name:"ortho_adam",summary:"Orthogonal Adam",available:!0},{name:"riemannian_orthogonal",summary:"Riemannian orthogonal update (Muon-family)",available:!0},{name:"muon",summary:"Muon update",available:!0},{name:"lion",summary:"Lion optimizer",available:!0},{name:"spectral_constrained",summary:"Spectral-norm constrained update",available:!0},{name:"mean_norm",summary:"Mean-norm update",available:!0},{name:"elastic_consolidation",summary:"EWC elastic consolidation",available:!0},{name:"natural_gradient",summary:"Natural gradient (Fisher)",available:!0},{name:"role_split",summary:"Role-split update",available:!0}]}},SM={axes:MM},xp=.72,vp=.86;function ul(i,e,t,n,s){const{camera:r,controls:a}=i,o=(s==null?void 0:s.clone())??r.position.clone().sub(a.target);o.lengthSq()===0&&o.set(.4,.5,.8),o.normalize();const l=o.clone().negate(),c=new V().crossVectors(l,new V(0,1,0)).normalize(),h=new V().crossVectors(c,l).normalize(),u=Math.tan((r.fov??60)*Math.PI/360),d=u*(r.aspect||1),f=u*vp,g=d*xp;let _=0;[e.x,t.x].forEach(p=>{[e.y,t.y].forEach(m=>{[e.z,t.z].forEach(M=>{const v=new V(p,m,M),b=Math.max(Math.abs(v.dot(c))/g,Math.abs(v.dot(h))/f)+v.dot(o);_=Math.max(_,b)})})}),_*=1.06,n.add(c.clone().multiplyScalar(.28*d*_)).add(h.clone().multiplyScalar(-.14*u*_)),a.target.copy(n),r.position.copy(n).add(o.clone().multiplyScalar(_)),a.update()}const Ba=["credit","geometry","dynamics","substrate","plasticity","update"];function js(i,e,t){return`${i}|${e}|${t}`}function ms(i){return i.length===0?0:i.reduce((e,t)=>e+t,0)/i.length}function bM(i){if(i.length<2)return 0;const e=ms(i),t=i.reduce((n,s)=>n+(s-e)**2,0)/(i.length-1);return Math.sqrt(t)}function wM(i){const e=new Map;for(const t of i)for(const n of t){const s=e.get(n.epoch)??[];s.push(n.val_acc),e.set(n.epoch,s)}return Array.from(e.entries()).sort((t,n)=>t[0]-n[0]).map(([t,n])=>({epoch:t,val_acc:ms(n)}))}function EM(i,e){const t=new Map;return i.cells.forEach(n=>{t.set(js(n.coordinate[e.x],n.coordinate[e.y],n.coordinate[e.z]),n)}),t}function TM(i,e){const t=new Map;return((i==null?void 0:i.records)??[]).forEach((s,r)=>{var h;const a=s==null?void 0:s.coordinate;if(!a)return;const o=js(a[e.x],a[e.y],a[e.z]);let l=t.get(o);l||(l={acc:[],walltime:[],params:[],curves:[],pareto:!1,coordinate:{...a},seeds:0},t.set(o,l)),l.seeds+=1;const c=s.payload??{};if(typeof c.val_acc=="number"&&l.acc.push(c.val_acc),typeof c.walltime_s=="number"&&l.walltime.push(c.walltime_s),typeof c.param_count=="number"&&l.params.push(c.param_count),Array.isArray(c.convergence_curve)){const u=c.convergence_curve.filter(d=>typeof(d==null?void 0:d.epoch)=="number"&&typeof(d==null?void 0:d.val_acc)=="number").map(d=>({epoch:d.epoch,val_acc:d.val_acc}));u.length>0&&l.curves.push(u)}(h=i==null?void 0:i.pareto)!=null&&h[r]&&(l.pareto=!0)}),t}function zh(i,e){const t=Array.from(i.values()),n=dl(t,e);return t.sort((s,r)=>za(s,e,n).localeCompare(za(r,e,n)))}function dl(i,e){return[e.x,e.y,e.z].filter(n=>new Set(i.map(r=>r.coordinate[n])).size>1)}function za(i,e,t){return(t.length>0?t:[e.x,e.y,e.z]).map(s=>i.coordinate[s]??"").join(" · ")}function Fd(i){const e={credit:new Set,geometry:new Set,dynamics:new Set,substrate:new Set,plasticity:new Set,update:new Set};i.forEach(n=>{const s=n==null?void 0:n.coordinate;s&&Ba.forEach(r=>{const a=s[r];typeof a=="string"&&a.length>0&&e[r].add(a)})});const t={};return Ba.forEach(n=>{t[n]=Array.from(e[n]).sort()}),t}class AM{constructor(){I(this,"runId",null);I(this,"metrics",null);I(this,"axes",{x:"credit",y:"geometry",z:"dynamics"});I(this,"space",null);I(this,"spaceCells",new Map);I(this,"aggregates",new Map);I(this,"values",Fd([]));I(this,"chance",.1);I(this,"requiredSeeds",0);I(this,"gate",null);I(this,"timeline",null);I(this,"account",null);I(this,"flow",null);I(this,"attribution",null);I(this,"dynamics",null);I(this,"spaceRequest","");I(this,"accountRequest","");I(this,"attributionRequest","");I(this,"flowRequest","");I(this,"dynamicsRun","");I(this,"dynamicsAsking",!1);I(this,"timelineRun","");I(this,"timelineStale",!0);I(this,"timelineTimer",null);I(this,"listeners",[]);Zn.onChange((e,t)=>{this.absorb(e,t)}),jt.register("pipeline_event",()=>this.scheduleTimeline())}onChange(e){this.listeners.push(e)}notify(e){this.listeners.forEach(t=>t(e))}async absorb(e,t){this.runId=e,this.metrics=t,t&&(typeof t.chance=="number"&&(this.chance=t.chance),typeof t.required_seeds=="number"&&(this.requiredSeeds=t.required_seeds),t.gate&&(this.gate=t.gate,typeof t.gate.required_seeds_per_group=="number"&&(this.requiredSeeds=t.gate.required_seeds_per_group)),this.values=Fd(t.records??[])),this.recomputeEvidence(),await this.syncSpace(),this.syncAccount(),this.syncAttribution(),this.syncTimeline(),this.syncDynamics()}setAxes(e){this.axes=e,this.notify("axes"),this.recomputeEvidence(),this.syncSpace()}recomputeEvidence(){this.aggregates=TM(this.metrics,this.axes),this.notify("evidence")}async syncSpace(){if(!this.runId)return;const e=[this.runId,this.axes.x,this.axes.y,this.axes.z,...Ba.map(n=>this.values[n].join(","))].join("|");if(e===this.spaceRequest)return;const t=await this.fetchSpace();t&&(this.spaceRequest=e,this.space=t,this.spaceCells=EM(t,this.axes),this.notify("space"))}async fetchSpace(){try{const e=await fetch(`/api/cells/${this.runId}/space`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({axes:[this.axes.x,this.axes.y,this.axes.z]})});return e.ok?await e.json():(console.warn("[StageState] The space was refused",e.status),null)}catch(e){return console.warn("[StageState] The space could not be read",e),null}}async syncAccount(){var n,s;if(!this.runId){this.account=null,this.accountRequest="";return}const e=((s=(n=this.metrics)==null?void 0:n.records)==null?void 0:s.length)??0,t=`${this.runId}|${e}`;if(t!==this.accountRequest)try{const r=await fetch(`/api/runs/${encodeURIComponent(this.runId)}/account`);if(!r.ok){console.warn("[StageState] The account was refused",r.status);return}this.account=await r.json(),this.accountRequest=t,this.notify("evidence")}catch(r){console.warn("[StageState] The account could not be read",r)}}async syncTimeline(){if(!this.runId){this.timeline=null,this.timelineRun="";return}if(!(!this.timelineStale&&this.timelineRun===this.runId))try{const e=await fetch(`/api/events?run_id=${encodeURIComponent(this.runId)}`);if(!e.ok){console.warn("[StageState] The timeline was refused",e.status);return}this.timeline=await e.json(),this.timelineRun=this.runId,this.timelineStale=!1,this.notify("events"),this.syncFlow()}catch(e){console.warn("[StageState] The timeline could not be read",e)}}async syncFlow(){var n;if(!this.runId){this.flow=null,this.flowRequest="";return}const e=((n=this.timeline)==null?void 0:n.events.length)??0,t=`${this.runId}|${e}`;if(t!==this.flowRequest)try{const s=await fetch(`/api/runs/${encodeURIComponent(this.runId)}/flow`);if(!s.ok){console.warn("[StageState] The flow was refused",s.status);return}this.flow=await s.json(),this.flowRequest=t,this.notify("events")}catch(s){console.warn("[StageState] The flow could not be read",s)}}async syncAttribution(){var n,s;if(!this.runId){this.attribution=null,this.attributionRequest="";return}const e=((s=(n=this.metrics)==null?void 0:n.records)==null?void 0:s.length)??0,t=`${this.runId}|${e}`;if(t!==this.attributionRequest)try{const r=await fetch(`/api/runs/${encodeURIComponent(this.runId)}/attribution`);if(!r.ok){console.warn("[StageState] The attribution was refused",r.status);return}this.attribution=await r.json(),this.attributionRequest=t,this.notify("evidence")}catch(r){console.warn("[StageState] The attribution could not be read",r)}}async syncDynamics(){if(!this.runId){this.dynamics=null,this.dynamicsRun="";return}if(!(this.dynamicsRun===this.runId||this.dynamicsAsking)){this.dynamicsAsking=!0;try{const e=await fetch(`/api/runs/${encodeURIComponent(this.runId)}/dynamics`);if(!e.ok){console.warn("[StageState] The dynamics were refused",e.status);return}const t=await e.json();this.dynamics=t,t.cell&&(this.dynamicsRun=this.runId),this.notify("evidence")}catch(e){console.warn("[StageState] The dynamics could not be read",e)}finally{this.dynamicsAsking=!1}}}scheduleTimeline(){this.timelineStale=!0,this.timelineTimer===null&&(this.timelineTimer=window.setTimeout(()=>{this.timelineTimer=null,this.syncTimeline()},300))}}const Ee=new AM;function sl(i,e=10){if(i.length<=e)return[i];const t=[];let n="";for(const s of i.split("_")){const r=n?`${n}_${s}`:s;r.length>e&&n?(t.push(n),n=s):n=r}return n&&t.push(n),t}function Un(i,e,t,n){const s=sl(i),r=document.createElement("canvas"),a=r.getContext("2d"),o=64,l=72;a.font=`bold ${o}px "JetBrains Mono", monospace`;const c=Math.max(...s.map(_=>a.measureText(_).width))+16;r.width=Math.max(64,Math.ceil(c)),r.height=s.length*l+16,a.font=`bold ${o}px "JetBrains Mono", monospace`,a.fillStyle="#ffffff",a.textAlign="center",a.textBaseline="middle",s.forEach((_,p)=>{a.fillText(_,r.width/2,l*p+l/2+8)});const h=new Fh(r);h.needsUpdate=!0;const u=t.clone();u.map=h,u.transparent=!0;const d=new pp(u),f=r.width/r.height;let g=e*s.length;return n!==void 0&&(g=Math.min(g,n/f)),d.scale.set(g*f,g,1),d}function RM(){const e=document.createElement("canvas");e.width=64,e.height=64;const t=e.getContext("2d");t.fillStyle="#ffffff",t.beginPath(),t.arc(64/2,64/2,64/2-2,0,Math.PI*2),t.fill();const n=new Fh(e);return n.needsUpdate=!0,n}function CM(i,e,t=.14){const s=document.createElement("canvas");s.width=128,s.height=128;const r=s.getContext("2d");r.strokeStyle=i,r.lineWidth=128*t,r.beginPath(),r.arc(128/2,128/2,128/2-r.lineWidth,0,Math.PI*2),r.stroke();const a=new Fh(s);a.needsUpdate=!0;const o=new ji({map:a,transparent:!0,depthWrite:!1}),l=new pp(o);return l.scale.set(e*2,e*2,1),l}const Od=SM.axes,PM={measured:"Measured — the run has evidence here",legal:"Legal — a gap nobody has measured",void:"Void — the system refuses this cell"};class LM{constructor(){I(this,"name","DiscoveryMap");I(this,"scene",new Uh);I(this,"camera",new bn);I(this,"renderer",null);I(this,"cells",new Map);I(this,"cellDataMap",new Map);I(this,"cellHeights",new Map);I(this,"xValues",[]);I(this,"yValues",[]);I(this,"zValues",[]);I(this,"cellSize",.8);I(this,"spacing",1.1);I(this,"raycaster",new aM);I(this,"mouse",new $e);I(this,"selectedCell",null);I(this,"hoveredCell",null);I(this,"legendElement",null);I(this,"readoutElement",null);I(this,"pointerX",0);I(this,"pointerY",0);I(this,"axisLabelMeshes",[]);I(this,"voidMesh",null);I(this,"visible",!1);I(this,"onQueueUpdate",e=>{});I(this,"onCampaignMetrics",e=>{const t=e==null?void 0:e.data;if(!(t!=null&&t.run))return;const n=typeof(e==null?void 0:e.campaign_id)=="string"?e.campaign_id:null;n&&Zn.observe(n,t)});jt.register("queue_update",this.onQueueUpdate),jt.register("campaign_metrics",this.onCampaignMetrics)}async init(){const e=xs();e&&(this.scene=e.scene,this.camera=e.camera,this.renderer=e.renderer),this.setupInteraction(),this.createLegend(),this.createReadout(),Ee.onChange(()=>this.updateLegend()),Zn.onChange(()=>this.updateRunPicker()),console.log("[DiscoveryMap] Initialized")}async destroy(){var e,t;jt.unregister("queue_update",this.onQueueUpdate),jt.unregister("campaign_metrics",this.onCampaignMetrics),this.clearGrid(),(e=this.legendElement)==null||e.remove(),(t=this.readoutElement)==null||t.remove()}show(){this.visible=!0,this.applyAxes()}hide(){this.visible=!1,this.clearGrid()}refreshView(e){if(this.visible){if(e==="space"){this.applyAxes();return}e==="evidence"&&this.applyAggregates()}}hasMeasured(){return this.cellDataMap.size>0&&this.cellHeights.size>0}updateLegend(){this.refreshAxisOptions(),this.updateLegendArms(),this.updateLegendAxes()}setupInteraction(){var t;const e=(t=this.renderer)==null?void 0:t.domElement;e&&(this.raycaster.params.Line.threshold=this.cellSize*.2,e.addEventListener("mousemove",n=>{const s=e.getBoundingClientRect();this.mouse.x=(n.clientX-s.left)/s.width*2-1,this.mouse.y=-((n.clientY-s.top)/s.height)*2+1,this.pointerX=n.clientX,this.pointerY=n.clientY}),e.addEventListener("mouseleave",()=>{this.hideReadout()}),e.addEventListener("click",()=>{this.hoveredCell&&this.selectCell(this.hoveredCell)}))}createReadout(){const e=document.getElementById("ui-overlay");e&&(this.readoutElement=document.createElement("div"),this.readoutElement.id="cell-readout",this.readoutElement.style.cssText=`
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
    `,e.appendChild(this.readoutElement))}showReadout(e){const t=this.readoutElement;if(!t)return;const n=document.createElement("div");n.style.color="var(--text-secondary)",n.textContent=Object.entries(e.coordinate).filter(([,l])=>l).map(([l,c])=>`${l}=${c}`).join("  "),t.replaceChildren(n);const s=document.createElement("div");if(s.style.marginTop="4px",s.style.fontWeight="600",s.style.color=e.status==="void"?z.void:e.status==="measured"?z.measured:z.legal_unmeasured,s.textContent=PM[e.status],t.appendChild(s),e.voidReason){const l=document.createElement("div");l.style.marginTop="4px",l.style.color="var(--text-secondary)",l.textContent=e.voidReason,t.appendChild(l)}t.style.display="block";const r=t.getBoundingClientRect(),a=Math.min(this.pointerX+16,window.innerWidth-r.width-8),o=Math.min(this.pointerY+16,window.innerHeight-r.height-8);t.style.left=`${Math.max(8,a)}px`,t.style.top=`${Math.max(8,o)}px`}hideReadout(){this.readoutElement&&(this.readoutElement.style.display="none")}createLegend(){const e=document.getElementById("ui-overlay");e&&(this.legendElement=document.createElement("div"),this.legendElement.id="discovery-legend",this.legendElement.style.cssText=`
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
    `,e.appendChild(this.legendElement),this.createRunPicker(),this.createAxisPicker(),this.updateLegendArms(),this.updateLegendAxes())}createRunPicker(){var t;const e=(t=this.legendElement)==null?void 0:t.querySelector("#legend-run-picker");e&&e.addEventListener("change",()=>{Zn.select(e.value||null)})}updateRunPicker(){var a,o,l;const e=(a=this.legendElement)==null?void 0:a.querySelector("#legend-run-picker"),t=(o=this.legendElement)==null?void 0:o.querySelector("#legend-run");if(!e)return;const n=Zn.runs;if(e.innerHTML="",n.forEach(([c,h])=>{var g,_;const u=document.createElement("option"),d=((g=h==null?void 0:h.run)==null?void 0:g.profile)??"run",f=((_=h==null?void 0:h.records)==null?void 0:_.length)??0;u.value=c,u.textContent=`${c.slice(0,8)} · ${d} · ${f}`,u.selected=c===Zn.selectedId,e.appendChild(u)}),n.length===0){e.disabled=!0,t&&(t.textContent="No run has reported yet.");return}e.disabled=!1;const s=Zn.selected;if(!t)return;if(!s){t.textContent="";return}const r=s.run??{};t.textContent=[`run ${(Zn.selectedId??"").slice(0,8)}`,r.mode,`${((l=s.records)==null?void 0:l.length)??0} records`].filter(Boolean).join(" · ")}createAxisPicker(){var n;const e=(n=this.legendElement)==null?void 0:n.querySelector("#legend-axis-picker");if(!e)return;["x","y","z"].forEach(s=>{const r=document.createElement("div");r.style.cssText="display: flex; align-items: center; gap: 6px; font-size: 11px;";const a=document.createElement("span");a.textContent=s.toUpperCase(),a.style.cssText="color: var(--text-secondary); width: 12px;";const o=document.createElement("select");o.dataset.dimension=s,o.style.cssText=`
        flex: 1;
        background: var(--bg-tertiary);
        color: var(--text-primary);
        border: 1px solid var(--border);
        border-radius: 4px;
        font-size: 11px;
        padding: 2px 4px;
      `,o.addEventListener("change",()=>{Ee.setAxes({...Ee.axes,[s]:o.value})}),r.appendChild(a),r.appendChild(o),e.appendChild(r)}),this.refreshAxisOptions()}refreshAxisOptions(){var t;const e=(t=this.legendElement)==null?void 0:t.querySelectorAll("#legend-axis-picker select");e&&e.forEach(n=>{const s=n.dataset.dimension,r=new Set(["x","y","z"].filter(a=>a!==s).map(a=>Ee.axes[a]));n.innerHTML="",Ba.forEach(a=>{var l;const o=document.createElement("option");o.value=a,o.textContent=((l=Od[a])==null?void 0:l.display_name)??a,o.disabled=r.has(a),o.selected=Ee.axes[s]===a,n.appendChild(o)})})}updateLegendArms(){var n;const e=(n=this.legendElement)==null?void 0:n.querySelector("#legend-arms");if(!e)return;const t=Ee.values.credit;if(t.length===0){e.innerHTML='<span style="color: var(--text-muted); font-size: 11px;">No arm measured yet.</span>';return}e.innerHTML=t.map(s=>{const r=Xt[s]||z.gradient;return`<span style="display: inline-flex; align-items: center; gap: 4px; padding: 2px 8px; background: ${r}22; border: 1px solid ${r}88; border-radius: 12px; color: ${r}; font-size: 11px;">${s}</span>`}).join("")}updateLegendAxes(){var l;const e=(l=this.legendElement)==null?void 0:l.querySelector("#legend-axes");if(!e)return;const t=Ee.space;if(!t){e.textContent="Waiting for the run's declared space — the axes come from the ontology.";return}const n=(c,h)=>{var g;const u=t.available[c]??h.length,d=u>h.length?` (${h.length} of ${u})`:"";return`${((g=Od[c])==null?void 0:g.display_name)??c}${d}`},s=Object.entries(t.held).map(([c,h])=>`${c}=${h}`),r={measured:Array.from(Ee.aggregates.keys()).filter(c=>Ee.spaceCells.has(c)).length,legal:t.counts.legal,void:t.counts.void},a=t.cells.length,o=Object.entries(t.void_rules??{}).sort((c,h)=>h[1]-c[1]).slice(0,2).map(([c,h])=>`${c.replace(/_/g," ")} (${h})`);e.innerHTML=[`<div>X: ${n(Ee.axes.x,t.values[Ee.axes.x]??[])}</div>`,`<div>Y: ${n(Ee.axes.y,t.values[Ee.axes.y]??[])}</div>`,`<div>Z: ${n(Ee.axes.z,t.values[Ee.axes.z]??[])}</div>`,`<div style="margin-top: 6px;">held: ${s.join(" · ")||"—"}</div>`,`<div style="margin-top: 6px;">${r.measured} measured · ${r.legal} legal · ${r.void} void (of ${a})</div>`,o.length>0?`<div style="margin-top: 6px;">refused by: ${o.join(", ")}</div>`:""].join("")}applyAxes(){const e=Ee.space,t=Ee.axes;this.xValues=(e==null?void 0:e.values[t.x])??[],this.yValues=(e==null?void 0:e.values[t.y])??[],this.zValues=(e==null?void 0:e.values[t.z])??[],this.buildGrid(),this.updateLegend()}buildGrid(){if(this.clearGrid(),!this.visible)return;this.createAxisLabels();const e=[];this.yValues.forEach((t,n)=>{this.zValues.forEach((s,r)=>{this.xValues.forEach((a,o)=>{const l=js(a,t,s),c=Ee.spaceCells.get(l),h=(c==null?void 0:c.status)??"legal",u={coordinate:this.coordinateFor(a,t,s),status:h,chance:Ee.chance,requiredSeeds:Ee.requiredSeeds,runId:Ee.runId??void 0,voidReason:c==null?void 0:c.reason,inDeclaration:c==null?void 0:c.in_declaration};if(this.cellDataMap.set(l,u),h==="void"){e.push(...this.voidMarkerPositions(o,n,r));return}this.createCell(l,u,o,n,r)})})}),e.length>0&&this.createVoidMarkers(e),this.frameGrid()}coordinateFor(e,t,n){const s={credit:"",geometry:"",dynamics:"",substrate:"",plasticity:"",update:""};return s[Ee.axes.x]=e,s[Ee.axes.y]=t,s[Ee.axes.z]=n,Ba.forEach(r=>{var o,l;if(s[r])return;const a=(l=(o=Ee.space)==null?void 0:o.held)==null?void 0:l[r];a&&(s[r]=a)}),s}createAxisLabels(){this.axisLabelMeshes.forEach(h=>this.scene.remove(h)),this.axisLabelMeshes=[];const e=new ji({color:9148584,sizeAttenuation:!0}),t=new ji({color:13227232,sizeAttenuation:!0}),n=(this.xValues.length-1)*this.spacing,r=(this.zValues.length-1)*this.spacing/2+1.2,a=-.45;this.xValues.forEach((h,u)=>{const d=(u-(this.xValues.length-1)/2)*this.spacing,f=Un(h,.3,e,this.spacing*.95);f.position.set(d,a,r),this.scene.add(f),this.axisLabelMeshes.push(f)});const o=Un(Ee.axes.x,.3,t);o.position.set(n/2+1.15,a,r),this.scene.add(o),this.axisLabelMeshes.push(o);const l=Un(Ee.axes.z,.3,t);l.position.set(0,a,r+1.1),this.scene.add(l),this.axisLabelMeshes.push(l);const c=Un(Ee.axes.y,.3,t);c.position.set(-(n/2)-1.5,1.3,0),this.scene.add(c),this.axisLabelMeshes.push(c)}createCell(e,t,n,s,r){const a=(n-(this.xValues.length-1)/2)*this.spacing,o=s*this.spacing,l=(r-(this.zValues.length-1)/2)*this.spacing,c=t.status==="measured"?this.createMeasuredCell(t):this.createLegalCell();c.position.set(a,o,l),c.userData={...c.userData,cellKey:e},this.scene.add(c),this.cells.set(e,c)}createMeasuredCell(e){const t=this.pillarHeight(e),n=Xt[e.coordinate.credit]||z.gradient,s=new Ei(this.cellSize,t,this.cellSize);s.translate(0,t/2,0);const r=new Ia({color:new nt(n),emissive:new nt(n),emissiveIntensity:.5,transparent:!0,opacity:.9,metalness:.3,roughness:.4}),a=new Qt(s,r);a.castShadow=!0,a.receiveShadow=!0;const o=new Ei(this.cellSize*1.1,t*1.1,this.cellSize*1.1);o.translate(0,t/2,0);const l=new ps({color:new nt(n),transparent:!0,opacity:.15,depthWrite:!1}),c=new Qt(o,l);return a.add(c),a.userData.glow=c,a}createLegalCell(){const e=new Ei(this.cellSize,this.cellSize,this.cellSize),t=new eM(e);t.translate(0,this.cellSize/2,0);const n=new Ai({color:z.legal_unmeasured,transparent:!0,opacity:.55}),s=new Ws(t,n),r=new Qt(new Ei(this.cellSize,this.cellSize,this.cellSize),new ps);return r.position.y=this.cellSize/2,r.visible=!1,s.add(r),s}disposeMesh(e){e.traverse(t=>{const n=t.geometry;n&&n.dispose();const s=t.material;Array.isArray(s)?s.forEach(r=>r.dispose()):s&&s.dispose()})}voidMarkerPositions(e,t,n){const s=(e-(this.xValues.length-1)/2)*this.spacing,r=t*this.spacing,a=(n-(this.zValues.length-1)/2)*this.spacing,o=this.cellSize*.6,l=.1;return[s-o,r+l,a-o,s+o,r+l,a+o,s+o,r+l,a-o,s-o,r+l,a+o]}createVoidMarkers(e){const t=new Gt;t.setAttribute("position",new zt(e,3));const n=new Ai({color:z.void,transparent:!0,opacity:.32});this.voidMesh=new Ws(t,n),this.scene.add(this.voidMesh)}frameGrid(){const e=xs();if(!(e!=null&&e.controls)||this.xValues.length===0||this.zValues.length===0)return;const t=(this.xValues.length-1)*this.spacing/2+this.cellSize,n=(this.zValues.length-1)*this.spacing/2+this.cellSize,s=(this.yValues.length-1)*this.spacing+this.cellSize,r=n+1.8,a=-.8;ul(e,new V(-t,a,-n),new V(t,s,r),new V(0,s/2,0))}clearGrid(){this.cells.forEach(e=>{this.scene.remove(e),this.disposeMesh(e)}),this.cells.clear(),this.cellDataMap.clear(),this.cellHeights.clear(),this.axisLabelMeshes.forEach(e=>{this.scene.remove(e),this.disposeMesh(e)}),this.axisLabelMeshes=[],this.voidMesh&&(this.scene.remove(this.voidMesh),this.voidMesh.geometry.dispose(),Array.isArray(this.voidMesh.material)?this.voidMesh.material.forEach(e=>e.dispose()):this.voidMesh.material.dispose(),this.voidMesh=null)}applyAggregates(){this.visible&&(Ee.aggregates.forEach((e,t)=>{const n=this.cellDataMap.get(t);n&&(n.status="measured",n.coordinate={...e.coordinate},n.metrics={val_acc:ms(e.acc),val_acc_std:bM(e.acc),walltime_s:ms(e.walltime),param_count:ms(e.params),n_seeds:e.acc.length},n.curve=wM(e.curves),n.pareto=e.pareto,n.chance=Ee.chance,n.requiredSeeds=Ee.requiredSeeds,n.runId=Ee.runId??void 0,this.updateCellVisual(t,n,e.pareto))}),this.updateLegendAxes())}pillarHeight(e){var t;return ah.lerp(.4,3.4,((t=e.metrics)==null?void 0:t.val_acc)??0)}updateCellVisual(e,t,n){const s=this.cells.get(e);if(!s)return;const r=s.position.clone(),a=s.userData.glow;a&&s.remove(a),this.scene.remove(s),this.disposeMesh(s);const o=this.createMeasuredCell(t);o.position.copy(r),o.userData.cellKey=e;const l=this.pillarHeight(t),c=this.cellHeights.get(e)??0;if(this.cellHeights.set(e,l),o.scale.y=l>0?Math.min(1,Math.max(c/l,.001)):1,n){const h=new Oh(this.cellSize*.6,this.cellSize*.8,32),u=new ps({color:z.pareto,side:In,transparent:!0,opacity:.6}),d=new Qt(h,u);d.rotation.x=-Math.PI/2,d.position.y=.05,o.add(d),o.userData.paretoRing=d}this.scene.add(o),this.cells.set(e,o)}selectCell(e){this.selectedCell=e;const t=this.cellDataMap.get(e);t&&window.dispatchEvent(new CustomEvent("cell-selected",{detail:t}))}update(e){if(!this.visible){this.hideReadout();return}const t=1-Math.exp(-e*8);this.cells.forEach((a,o)=>{const l=this.cellDataMap.get(o);if((l==null?void 0:l.status)==="measured"&&a instanceof Qt&&a.material instanceof Ia){a.scale.y<1&&(a.scale.y=Math.min(1,a.scale.y+(1-a.scale.y)*t));const c=a.userData.glow;c&&(c.material.opacity=.1+.1*Math.sin(Date.now()*.003));const h=a.userData.paretoRing;h&&(h.material.opacity=.4+.2*Math.sin(Date.now()*.005))}}),this.raycaster.setFromCamera(this.mouse,this.camera);const n=this.raycaster.intersectObjects(Array.from(this.cells.values()),!0);let s=null;n.length>0&&(s=this.pickCell(n)),s||(s=this.voidCellUnderCursor()),s!==this.hoveredCell&&(this.hoveredCell&&this.highlightCell(this.hoveredCell,!1),this.hoveredCell=s,s&&this.highlightCell(s,!0));const r=s?this.cellDataMap.get(s):void 0;r?this.showReadout(r):this.hideReadout()}pickCell(e){var n,s;let t=null;for(const r of e){const a=r.object.userData.cellKey||((n=r.object.parent)==null?void 0:n.userData.cellKey);if(a&&(t??(t=a),((s=this.cellDataMap.get(a))==null?void 0:s.status)==="measured"))return a}return t}voidCellUnderCursor(){if(!this.voidMesh)return null;const e=this.raycaster.params.Line.threshold;this.raycaster.params.Line.threshold=this.cellSize*.3;try{const t=this.raycaster.intersectObject(this.voidMesh,!1);return t.length===0?null:this.cellAt(t[0].point)}finally{this.raycaster.params.Line.threshold=e}}cellAt(e){const t=Math.round(e.x/this.spacing+(this.xValues.length-1)/2),n=Math.round(e.y/this.spacing),s=Math.round(e.z/this.spacing+(this.zValues.length-1)/2);return t<0||t>=this.xValues.length||n<0||n>=this.yValues.length||s<0||s>=this.zValues.length?null:js(this.xValues[t],this.yValues[n],this.zValues[s])}highlightCell(e,t){const n=this.cells.get(e);if(n){if(n instanceof Qt&&n.material instanceof Ia){t?(n.userData.originalEmissive=n.material.emissiveIntensity,n.material.emissiveIntensity=(n.userData.originalEmissive||.5)+.5):n.userData.originalEmissive!==void 0&&(n.material.emissiveIntensity=n.userData.originalEmissive);return}n instanceof Ws&&n.material instanceof Ai&&(t?(n.userData.originalOpacity=n.material.opacity,n.material.opacity=.95):n.userData.originalOpacity!==void 0&&(n.material.opacity=n.userData.originalOpacity))}}}const Vs=new LM;Ki.register(Vs);class DM{constructor(){I(this,"name","CellDrawer");I(this,"panel",null);I(this,"content",null);I(this,"sparklineScene",null);I(this,"sparklineRenderer",null);I(this,"sparklineCamera",null);I(this,"sparklineAnimationId",null);I(this,"currentData",null);I(this,"onKeyDown",e=>{e.key==="Escape"&&this.currentData&&this.hide()});I(this,"onCellSelected",e=>{this.show(e.detail)})}async init(){this.createPanel(),this.setupEvents(),console.log("[CellDrawer] Initialized")}async destroy(){var e;this.stopSparkline(),(e=this.panel)==null||e.remove(),window.removeEventListener("cell-selected",this.onCellSelected),window.removeEventListener("keydown",this.onKeyDown)}createPanel(){const e=document.getElementById("ui-overlay");e&&(this.panel=document.createElement("div"),this.panel.id="cell-drawer",this.panel.style.cssText=`
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
    `,e.appendChild(this.panel),this.content=this.panel.querySelector("#drawer-content"),this.panel.querySelector("#drawer-close").addEventListener("click",()=>this.hide()))}setupEvents(){window.addEventListener("cell-selected",this.onCellSelected),window.addEventListener("keydown",this.onKeyDown)}shiftPanels(e){const t=e?400:20;["hud","plotter"].forEach(n=>{var s;(s=document.getElementById(n))==null||s.style.setProperty("right",`${t}px`)})}show(e){this.currentData=e,this.renderContent(e),this.panel.style.transform="translateX(0)",this.shiftPanels(!0),this.startSparkline(e)}hide(){this.panel.style.transform="translateX(100%)",this.shiftPanels(!1),this.stopSparkline(),this.currentData=null}renderContent(e){if(!this.content)return;const{coordinate:t,metrics:n,status:s}=e,r=Xt[t.credit]||z.gradient,a=(n==null?void 0:n.val_acc)??0,o=(n==null?void 0:n.n_seeds)??0,l=e.chance??.1,c=e.requiredSeeds??0;let h="UNMEASURED",u=z.legal_unmeasured;s==="void"&&(h="VOID",u=z.void),s==="measured"&&(a<=l?(h="REJECTED",u=z.rejected):c>0&&o<c?(h="INSUFFICIENT",u=z.insufficient):a>l+.1?(h="PASSED",u=z.passed):(h="INSUFFICIENT",u=z.insufficient));const d=s==="measured"&&c>0?Math.max(0,c-o):"N/A";this.content.innerHTML=`
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
            background: linear-gradient(90deg, ${z.rejected}, ${z.insufficient}, ${z.passed});
            border-radius: 2px;
          "></div>
        </div>
      </div>

      ${s==="measured"?`
        <div style="margin-bottom: 20px;">
          <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 8px;">SEEDS TO CLAIM</div>
          <div style="font-size: 24px; font-weight: 700; font-family: 'JetBrains Mono', monospace; color: ${z.insufficient};">
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
    `,this.content.appendChild(f),this.wireActions(e)}actionStates(e){var a;if(e.status==="void")return{replicate:!1,preregister:!1,quest:!1};const t=e.status==="measured",n=((a=e.metrics)==null?void 0:a.n_seeds)??0,s=e.requiredSeeds??0;return{replicate:(s>0?Math.max(0,s-n):0)>0||!t,preregister:t,quest:!t}}wireActions(e){const t=this.content;if(!t)return;const n=this.actionStates(e);t.querySelectorAll(".drawer-btn[data-action]").forEach(o=>{const l=o.dataset.action??"",c=n[l]===!0;o.disabled=!c,o.addEventListener("click",()=>{this.runAction(l,e)})});const r=t.querySelector('.drawer-btn[data-action="replicate"]');r&&(r.textContent=e.status==="measured"?"Queue Rest":"Queue");const a=t.querySelector("#drawer-action-note");a&&(a.textContent=this.actionNote(e))}actionNote(e){var s;if(!e.runId)return"This cell belongs to no run yet, so there is nothing to queue or register.";if(e.status==="void")return`The system refuses this cell, so nothing can be measured here.${e.voidReason?` ${e.voidReason}.`:""}`;if(e.status==="measured"){const r=((s=e.metrics)==null?void 0:s.n_seeds)??0,a=e.requiredSeeds??0;return`Queue Rest measures the ${Math.max(0,a-r)} seeds this cell still owes. Preregister writes down the protocol a confirming run must meet.`}const t=e.inDeclaration===!1?" It lies outside this run's declaration, so the run did not set out to measure it.":"";return`The system would measure this cell and nobody has. Queue measures it (${e.requiredSeeds??0} seeds). Adopt as Quest writes the question down first and then queues the run that would answer it — a new run, because a threshold written now cannot confirm a run that has already begun.${t}`}setStatus(e,t=!1){var s;const n=(s=this.content)==null?void 0:s.querySelector("#drawer-status");n&&(n.textContent=e,n.style.color=t?z.rejected:z.text_secondary)}async runAction(e,t){var o,l;if(!t.runId){this.setStatus("This cell belongs to no run yet.",!0);return}const n=Array.from(((o=this.content)==null?void 0:o.querySelectorAll(".drawer-btn"))??[]);n.forEach(c=>{c.disabled=!0}),this.setStatus("Working…");const s=(l=this.content)==null?void 0:l.querySelector("#drawer-threshold"),r=s!=null&&s.value?Number(s.value):null,a={coordinate:t.coordinate};r!==null&&Number.isFinite(r)&&(a.threshold=r);try{const c=await fetch(`/api/cells/${t.runId}/${e}`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(a)}),h=await c.json();if(!c.ok){this.setStatus((h==null?void 0:h.error)??"The action failed.",!0);return}this.setStatus(this.actionSummary(e,h))}catch(c){this.setStatus(`The action failed: ${String(c)}`,!0)}finally{n.forEach(c=>{c.disabled=!1})}}actionSummary(e,t){if(e==="replicate")return`Queued campaign ${t.campaign_id}: ${t.measurements} measurements in a plan of ${t.plan}.`;const s=`${t.written?"Registered":"Already registered"} ${t.path} — commit it; the run that follows it can be confirmatory.`;return e!=="quest"?s:t.campaign_id?`${s} Queued campaign ${t.campaign_id}: ${t.measurements} measurements in a plan of ${t.plan}, in a new run.`:`${s} No campaign queue is attached, so nothing is scheduled.`}startSparkline(e){const t=document.getElementById("sparkline-container");if(!t)return;this.stopSparkline();const n=e.curve??[];if(n.length===0){t.innerHTML=`
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
      `;return}this.sparklineScene=new Uh,this.sparklineCamera=new Vr(-1,1,1,-1,.1,10),this.sparklineCamera.position.z=2,this.sparklineRenderer=new dp({alpha:!0,antialias:!0}),this.sparklineRenderer.setSize(t.clientWidth,t.clientHeight),this.sparklineRenderer.setPixelRatio(Math.min(window.devicePixelRatio,2)),t.appendChild(this.sparklineRenderer.domElement);const s=e.chance??.1,r=n.map(R=>R.val_acc),a=Math.min(s,...r),l=Math.max(...r,s)-a||1,c=R=>ah.lerp(-.7,.7,(R-a)/l),h=n.map((R,F)=>{const w=ah.lerp(-.9,.9,F/(n.length-1||1));return new V(w,c(R.val_acc),0)}),u=new Gt().setFromPoints(h),d=new Ai({color:Xt[e.coordinate.credit]||z.gradient,linewidth:2}),f=new il(u,d);this.sparklineScene.add(f);const g=new mp(new Gt().setFromPoints(h),new Nh({color:Xt[e.coordinate.credit]||z.gradient,size:6,sizeAttenuation:!1}));this.sparklineScene.add(g);const _=c(s),p=new Gt().setFromPoints([new V(-.9,_,0),new V(.9,_,0)]),m=new gp({color:z.chance_line,dashSize:.05,gapSize:.03,linewidth:1}),M=new il(p,m);M.computeLineDistances(),this.sparklineScene.add(M);const v=new Gt().setFromPoints([new V(-.9,-.7,0),new V(.9,-.7,0),new V(-.9,-.7,0),new V(-.9,.7,0)]),b=new Ai({color:z.border,linewidth:1}),N=new Ws(v,b);this.sparklineScene.add(N);const A=()=>{!this.sparklineRenderer||!this.sparklineScene||!this.sparklineCamera||(this.sparklineRenderer.render(this.sparklineScene,this.sparklineCamera),this.sparklineAnimationId=requestAnimationFrame(A))};A()}stopSparkline(){this.sparklineAnimationId&&(cancelAnimationFrame(this.sparklineAnimationId),this.sparklineAnimationId=null),this.sparklineRenderer&&(this.sparklineRenderer.dispose(),this.sparklineRenderer=null),this.sparklineScene=null,this.sparklineCamera=null}}const yp=new DM;Ki.register(yp);const IM=!0,on="u-",UM="uplot",NM=on+"hz",FM=on+"vt",OM=on+"title",BM=on+"wrap",zM=on+"under",kM=on+"over",HM=on+"axis",zs=on+"off",VM=on+"select",GM=on+"cursor-x",WM=on+"cursor-y",XM=on+"cursor-pt",qM=on+"legend",$M=on+"live",YM=on+"inline",jM=on+"series",KM=on+"marker",Bd=on+"label",ZM=on+"value",Ca="width",Pa="height",wa="top",zd="bottom",Lr="left",gc="right",kh="#000",kd=kh+"0",_c="mousemove",Hd="mousedown",xc="mouseup",Vd="mouseenter",Gd="mouseleave",Wd="dblclick",JM="resize",QM="scroll",Xd="change",rl="dppxchange",Hh="--",ia=typeof window<"u",hh=ia?document:null,Gr=ia?window:null,eS=ia?navigator:null;let Mt,Oo;function uh(){let i=devicePixelRatio;Mt!=i&&(Mt=i,Oo&&fh(Xd,Oo,uh),Oo=matchMedia(`(min-resolution: ${Mt-.001}dppx) and (max-resolution: ${Mt+.001}dppx)`),Xs(Xd,Oo,uh),Gr.dispatchEvent(new CustomEvent(rl)))}function Gn(i,e){if(e!=null){let t=i.classList;!t.contains(e)&&t.add(e)}}function dh(i,e){let t=i.classList;t.contains(e)&&t.remove(e)}function Ft(i,e,t){i.style[e]=t+"px"}function li(i,e,t,n){let s=hh.createElement(i);return e!=null&&Gn(s,e),t!=null&&t.insertBefore(s,n),s}function Kn(i,e){return li("div",i,e)}const qd=new WeakMap;function Si(i,e,t,n,s){let r="translate("+e+"px,"+t+"px)",a=qd.get(i);r!=a&&(i.style.transform=r,qd.set(i,r),e<0||t<0||e>n||t>s?Gn(i,zs):dh(i,zs))}const $d=new WeakMap;function Yd(i,e,t){let n=e+t,s=$d.get(i);n!=s&&($d.set(i,n),i.style.background=e,i.style.borderColor=t)}const jd=new WeakMap;function Kd(i,e,t,n){let s=e+""+t,r=jd.get(i);s!=r&&(jd.set(i,s),i.style.height=t+"px",i.style.width=e+"px",i.style.marginLeft=n?-e/2+"px":0,i.style.marginTop=n?-t/2+"px":0)}const Vh={passive:!0},tS={...Vh,capture:!0};function Xs(i,e,t,n){e.addEventListener(i,t,n?tS:Vh)}function fh(i,e,t,n){e.removeEventListener(i,t,Vh)}ia&&uh();function ci(i,e,t,n){let s;t=t||0,n=n||e.length-1;let r=n<=2147483647;for(;n-t>1;)s=r?t+n>>1:Wn((t+n)/2),e[s]<i?t=s:n=s;return i-e[t]<=e[n]-i?t:n}function Mp(i){return(t,n,s)=>{let r=-1,a=-1;for(let o=n;o<=s;o++)if(i(t[o])){r=o;break}for(let o=s;o>=n;o--)if(i(t[o])){a=o;break}return[r,a]}}const Sp=i=>i!=null,bp=i=>i!=null&&i>0,fl=Mp(Sp),nS=Mp(bp);function iS(i,e,t,n=0,s=!1){let r=s?nS:fl,a=s?bp:Sp;[e,t]=r(i,e,t);let o=i[e],l=i[e];if(e>-1)if(n==1)o=i[e],l=i[t];else if(n==-1)o=i[t],l=i[e];else for(let c=e;c<=t;c++){let h=i[c];a(h)&&(h<o?o=h:h>l&&(l=h))}return[o??Rt,l??-Rt]}function pl(i,e,t,n){let s=Qd(i),r=Qd(e);i==e&&(s==-1?(i*=t,e/=t):(i/=t,e*=t));let a=t==10?qi:wp,o=s==1?Wn:Jn,l=r==1?Jn:Wn,c=o(a(nn(i))),h=l(a(nn(e))),u=Kr(t,c),d=Kr(t,h);return t==10&&(c<0&&(u=Ct(u,-c)),h<0&&(d=Ct(d,-h))),n||t==2?(i=u*s,e=d*r):(i=Rp(i,u),e=ml(e,d)),[i,e]}function Gh(i,e,t,n){let s=pl(i,e,t,n);return i==0&&(s[0]=0),e==0&&(s[1]=0),s}const Wh=.1,Zd={mode:3,pad:Wh},Ua={pad:0,soft:null,mode:0},sS={min:Ua,max:Ua};function al(i,e,t,n){return gl(t)?Jd(i,e,t):(Ua.pad=t,Ua.soft=n?0:null,Ua.mode=n?3:0,Jd(i,e,sS))}function vt(i,e){return i??e}function rS(i,e,t){for(e=vt(e,0),t=vt(t,i.length-1);e<=t;){if(i[e]!=null)return!0;e++}return!1}function Jd(i,e,t){let n=t.min,s=t.max,r=vt(n.pad,0),a=vt(s.pad,0),o=vt(n.hard,-Rt),l=vt(s.hard,Rt),c=vt(n.soft,Rt),h=vt(s.soft,-Rt),u=vt(n.mode,0),d=vt(s.mode,0),f=e-i,g=qi(f),_=Pn(nn(i),nn(e)),p=qi(_),m=nn(p-g);(f<1e-24||m>10)&&(f=0,(i==0||e==0)&&(f=1e-24,u==2&&c!=Rt&&(r=0),d==2&&h!=-Rt&&(a=0)));let M=f||_||1e3,v=qi(M),b=Kr(10,Wn(v)),N=M*(f==0?i==0?.1:1:r),A=Ct(Rp(i-N,b/10),24),R=i>=c&&(u==1||u==3&&A<=c||u==2&&A>=c)?c:Rt,F=Pn(o,A<R&&i>=R?R:di(R,A)),w=M*(f==0?e==0?.1:1:a),y=Ct(ml(e+w,b/10),24),P=e<=h&&(d==1||d==3&&y>=h||d==2&&y<=h)?h:-Rt,K=di(l,y>P&&e<=P?P:Pn(P,y));return F==K&&F==0&&(K=100),[F,K]}const aS=new Intl.NumberFormat(ia?eS.language:"en-US"),Xh=i=>aS.format(i),qn=Math,qo=qn.PI,nn=qn.abs,Wn=qn.floor,tn=qn.round,Jn=qn.ceil,di=qn.min,Pn=qn.max,Kr=qn.pow,Qd=qn.sign,qi=qn.log10,wp=qn.log2,oS=(i,e=1)=>qn.sinh(i)*e,vc=(i,e=1)=>qn.asinh(i/e),Rt=1/0;function ef(i){return(qi((i^i>>31)-(i>>31))|0)+1}function ph(i,e,t){return di(Pn(i,e),t)}function Ep(i){return typeof i=="function"}function ft(i){return Ep(i)?i:()=>i}const lS=()=>{},Tp=i=>i,Ap=(i,e)=>e,cS=i=>null,tf=i=>!0,nf=(i,e)=>i==e,hS=/\.\d*?(?=9{6,}|0{6,})/gm,Ks=i=>{if(Pp(i)||vs.has(i))return i;const e=`${i}`,t=e.match(hS);if(t==null)return i;let n=t[0].length-1;if(e.indexOf("e-")!=-1){let[s,r]=e.split("e");return+`${Ks(s)}e${r}`}return Ct(i,n)};function Ns(i,e){return Ks(Ct(Ks(i/e))*e)}function ml(i,e){return Ks(Jn(Ks(i/e))*e)}function Rp(i,e){return Ks(Wn(Ks(i/e))*e)}function Ct(i,e=0){if(Pp(i))return i;let t=10**e,n=i*t*(1+Number.EPSILON);return tn(n)/t}const vs=new Map;function Cp(i){return((""+i).split(".")[1]||"").length}function ka(i,e,t,n){let s=[],r=n.map(Cp);for(let a=e;a<t;a++){let o=nn(a),l=Ct(Kr(i,a),o);for(let c=0;c<n.length;c++){let h=i==10?+`${n[c]}e${a}`:n[c]*l,u=(a>=0?0:o)+(a>=r[c]?0:r[c]),d=i==10?h:Ct(h,u);s.push(d),vs.set(d,u)}}return s}const Na={},qh=[],Zr=[null,null],hs=Array.isArray,Pp=Number.isInteger,uS=i=>i===void 0;function sf(i){return typeof i=="string"}function gl(i){let e=!1;if(i!=null){let t=i.constructor;e=t==null||t==Object}return e}function dS(i){return i!=null&&typeof i=="object"}const fS=Object.getPrototypeOf(Uint8Array),Lp="__proto__";function Jr(i,e=gl){let t;if(hs(i)){let n=i.find(s=>s!=null);if(hs(n)||e(n)){t=Array(i.length);for(let s=0;s<i.length;s++)t[s]=Jr(i[s],e)}else t=i.slice()}else if(i instanceof fS)t=i.slice();else if(e(i)){t={};for(let n in i)n!=Lp&&(t[n]=Jr(i[n],e))}else t=i;return t}function Jt(i){let e=arguments;for(let t=1;t<e.length;t++){let n=e[t];for(let s in n)s!=Lp&&(gl(i[s])?Jt(i[s],Jr(n[s])):i[s]=Jr(n[s]))}return i}const pS=0,mS=1,gS=2;function _S(i,e,t){for(let n=0,s,r=-1;n<e.length;n++){let a=e[n];if(a>r){for(s=a-1;s>=0&&i[s]==null;)i[s--]=null;for(s=a+1;s<t&&i[s]==null;)i[r=s++]=null}}}function xS(i,e){if(MS(i)){let a=i[0].slice();for(let o=1;o<i.length;o++)a.push(...i[o].slice(1));return SS(a[0])||(a=yS(a)),a}let t=new Set;for(let a=0;a<i.length;a++){let l=i[a][0],c=l.length;for(let h=0;h<c;h++)t.add(l[h])}let n=[Array.from(t).sort((a,o)=>a-o)],s=n[0].length,r=new Map;for(let a=0;a<s;a++)r.set(n[0][a],a);for(let a=0;a<i.length;a++){let o=i[a],l=o[0];for(let c=1;c<o.length;c++){let h=o[c],u=Array(s).fill(void 0),d=e?e[a][c]:mS,f=[];for(let g=0;g<h.length;g++){let _=h[g],p=r.get(l[g]);_===null?d!=pS&&(u[p]=_,d==gS&&f.push(p)):u[p]=_}_S(u,f,s),n.push(u)}}return n}const vS=typeof queueMicrotask>"u"?i=>Promise.resolve().then(i):queueMicrotask;function yS(i){let e=i[0],t=e.length,n=Array(t);for(let r=0;r<n.length;r++)n[r]=r;n.sort((r,a)=>e[r]-e[a]);let s=[];for(let r=0;r<i.length;r++){let a=i[r],o=Array(t);for(let l=0;l<t;l++)o[l]=a[n[l]];s.push(o)}return s}function MS(i){let e=i[0][0],t=e.length;for(let n=1;n<i.length;n++){let s=i[n][0];if(s.length!=t)return!1;if(s!=e){for(let r=0;r<t;r++)if(s[r]!=e[r])return!1}}return!0}function SS(i,e=100){const t=i.length;if(t<=1)return!0;let n=0,s=t-1;for(;n<=s&&i[n]==null;)n++;for(;s>=n&&i[s]==null;)s--;if(s<=n)return!0;const r=Pn(1,Wn((s-n+1)/e));for(let a=i[n],o=n+r;o<=s;o+=r){const l=i[o];if(l!=null){if(l<=a)return!1;a=l}}return!0}const Dp=["January","February","March","April","May","June","July","August","September","October","November","December"],Ip=["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];function Up(i){return i.slice(0,3)}const bS=Ip.map(Up),wS=Dp.map(Up),ES={MMMM:Dp,MMM:wS,WWWW:Ip,WWW:bS};function Ea(i){return(i<10?"0":"")+i}function TS(i){return(i<10?"00":i<100?"0":"")+i}const AS={YYYY:i=>i.getFullYear(),YY:i=>(i.getFullYear()+"").slice(2),MMMM:(i,e)=>e.MMMM[i.getMonth()],MMM:(i,e)=>e.MMM[i.getMonth()],MM:i=>Ea(i.getMonth()+1),M:i=>i.getMonth()+1,DD:i=>Ea(i.getDate()),D:i=>i.getDate(),WWWW:(i,e)=>e.WWWW[i.getDay()],WWW:(i,e)=>e.WWW[i.getDay()],HH:i=>Ea(i.getHours()),H:i=>i.getHours(),h:i=>{let e=i.getHours();return e==0?12:e>12?e-12:e},AA:i=>i.getHours()>=12?"PM":"AM",aa:i=>i.getHours()>=12?"pm":"am",a:i=>i.getHours()>=12?"p":"a",mm:i=>Ea(i.getMinutes()),m:i=>i.getMinutes(),ss:i=>Ea(i.getSeconds()),s:i=>i.getSeconds(),fff:i=>TS(i.getMilliseconds())};function $h(i,e){e=e||ES;let t=[],n=/\{([a-z]+)\}|[^{]+/gi,s;for(;s=n.exec(i);)t.push(s[0][0]=="{"?AS[s[1]]:s[0]);return r=>{let a="";for(let o=0;o<t.length;o++)a+=typeof t[o]=="string"?t[o]:t[o](r,e);return a}}const RS=new Intl.DateTimeFormat().resolvedOptions().timeZone;function CS(i,e){let t;return e=="UTC"||e=="Etc/UTC"?t=new Date(+i+i.getTimezoneOffset()*6e4):e==RS?t=i:(t=new Date(i.toLocaleString("en-US",{timeZone:e})),t.setMilliseconds(i.getMilliseconds())),t}const Np=i=>i%1==0,ol=[1,2,2.5,5],PS=ka(10,-32,0,ol),Fp=ka(10,0,32,ol),LS=Fp.filter(Np),Fs=PS.concat(Fp),Yh=`
`,Op="{YYYY}",rf=Yh+Op,Bp="{M}/{D}",La=Yh+Bp,Bo=La+"/{YY}",zp="{aa}",DS="{h}:{mm}",Nr=DS+zp,af=Yh+Nr,of=":{ss}",St=null;function kp(i){let e=i*1e3,t=e*60,n=t*60,s=n*24,r=s*30,a=s*365,l=(i==1?ka(10,0,3,ol).filter(Np):ka(10,-3,0,ol)).concat([e,e*5,e*10,e*15,e*30,t,t*5,t*10,t*15,t*30,n,n*2,n*3,n*4,n*6,n*8,n*12,s,s*2,s*3,s*4,s*5,s*6,s*7,s*8,s*9,s*10,s*15,r,r*2,r*3,r*4,r*6,a,a*2,a*5,a*10,a*25,a*50,a*100]);const c=[[a,Op,St,St,St,St,St,St,1],[s*28,"{MMM}",rf,St,St,St,St,St,1],[s,Bp,rf,St,St,St,St,St,1],[n,"{h}"+zp,Bo,St,La,St,St,St,1],[t,Nr,Bo,St,La,St,St,St,1],[e,of,Bo+" "+Nr,St,La+" "+Nr,St,af,St,1],[i,of+".{fff}",Bo+" "+Nr,St,La+" "+Nr,St,af,St,1]];function h(u){return(d,f,g,_,p,m)=>{let M=[],v=p>=a,b=p>=r&&p<a,N=u(g),A=Ct(N*i,3),R=yc(N.getFullYear(),v?0:N.getMonth(),b||v?1:N.getDate()),F=Ct(R*i,3);if(b||v){let w=b?p/r:0,y=v?p/a:0,P=A==F?A:Ct(yc(R.getFullYear()+y,R.getMonth()+w,1)*i,3),K=new Date(tn(P/i)),H=K.getFullYear(),Z=K.getMonth();for(let q=0;P<=_;q++){let ee=yc(H+y*q,Z+w*q,1),Y=ee-u(Ct(ee*i,3));P=Ct((+ee+Y)*i,3),P<=_&&M.push(P)}}else{let w=p>=s?s:p,y=Wn(g)-Wn(A),P=F+y+ml(A-F,w);M.push(P);let K=u(P),H=K.getHours()+K.getMinutes()/t+K.getSeconds()/n,Z=p/n,q=d.axes[f]._space,ee=m/q;for(;P=Ct(P+p,i==1?0:3),!(P>_);)if(Z>1){let Y=Wn(Ct(H+Z,6))%24,de=u(P).getHours()-Y;de>1&&(de=-1),P-=de*n,H=(H+Z)%24;let ve=M[M.length-1];Ct((P-ve)/p,3)*ee>=.7&&M.push(P)}else M.push(P)}return M}}return[l,c,h]}const[IS,US,NS]=kp(1),[FS,OS,BS]=kp(.001);ka(2,-53,53,[1]);function lf(i,e){return i.map(t=>t.map((n,s)=>s==0||s==8||n==null?n:e(s==1||t[8]==0?n:t[1]+n)))}function cf(i,e){return(t,n,s,r,a)=>{let o=e.find(g=>a>=g[0])||e[e.length-1],l,c,h,u,d,f;return n.map(g=>{let _=i(g),p=_.getFullYear(),m=_.getMonth(),M=_.getDate(),v=_.getHours(),b=_.getMinutes(),N=_.getSeconds(),A=p!=l&&o[2]||m!=c&&o[3]||M!=h&&o[4]||v!=u&&o[5]||b!=d&&o[6]||N!=f&&o[7]||o[1];return l=p,c=m,h=M,u=v,d=b,f=N,A(_)})}}function zS(i,e){let t=$h(e);return(n,s,r,a,o)=>s.map(l=>t(i(l)))}function yc(i,e,t){return new Date(i,e,t)}function hf(i,e){return e(i)}const kS="{YYYY}-{MM}-{DD} {h}:{mm}{aa}";function uf(i,e){return(t,n,s,r)=>r==null?Hh:e(i(n))}function HS(i,e){let t=i.series[e];return t.width?t.stroke(i,e):t.points.width?t.points.stroke(i,e):null}function VS(i,e){return i.series[e].fill(i,e)}const GS={show:!0,live:!0,isolate:!1,mount:lS,markers:{show:!0,width:2,stroke:HS,fill:VS,dash:"solid"},idx:null,idxs:null,values:[]};function WS(i,e){let t=i.cursor.points,n=Kn(),s=t.size(i,e);Ft(n,Ca,s),Ft(n,Pa,s);let r=s/-2;Ft(n,"marginLeft",r),Ft(n,"marginTop",r);let a=t.width(i,e,s);return a&&Ft(n,"borderWidth",a),n}function XS(i,e){let t=i.series[e].points;return t._fill||t._stroke}function qS(i,e){let t=i.series[e].points;return t._stroke||t._fill}function $S(i,e){return i.series[e].points.size}const Mc=[0,0];function YS(i,e,t){return Mc[0]=e,Mc[1]=t,Mc}function zo(i,e,t,n=!0){return s=>{s.button==0&&(!n||s.target==e)&&t(s)}}function Sc(i,e,t,n=!0){return s=>{(!n||s.target==e)&&t(s)}}const jS={show:!0,x:!0,y:!0,lock:!1,move:YS,points:{one:!1,show:WS,size:$S,width:0,stroke:qS,fill:XS},bind:{mousedown:zo,mouseup:zo,click:zo,dblclick:zo,mousemove:Sc,mouseleave:Sc,mouseenter:Sc},drag:{setScale:!0,x:!0,y:!1,dist:0,uni:null,click:(i,e)=>{e.stopPropagation(),e.stopImmediatePropagation()},_x:!1,_y:!1},focus:{dist:(i,e,t,n,s)=>n-s,prox:-1,bias:0},hover:{skip:[void 0],prox:null,bias:0},left:-10,top:-10,idx:null,dataIdx:null,idxs:null,event:null},Hp={show:!0,stroke:"rgba(0,0,0,0.07)",width:2},jh=Jt({},Hp,{filter:Ap}),Vp=Jt({},jh,{size:10}),Gp=Jt({},Hp,{show:!1}),Kh='12px system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji"',Wp="bold "+Kh,Xp=1.5,df={show:!0,scale:"x",stroke:kh,space:50,gap:5,alignTo:1,size:50,labelGap:0,labelSize:30,labelFont:Wp,side:2,grid:jh,ticks:Vp,border:Gp,font:Kh,lineGap:Xp,rotate:0},KS="Value",ZS="Time",ff={show:!0,scale:"x",auto:!1,sorted:1,min:Rt,max:-Rt,idxs:[]};function JS(i,e,t,n,s){return e.map(r=>r==null?"":Xh(r))}function QS(i,e,t,n,s,r,a){let o=[],l=vs.get(s)||0;t=a?t:Ct(ml(t,s),l);for(let c=t;c<=n;c=Ct(c+s,l))o.push(Object.is(c,-0)?0:c);return o}function mh(i,e,t,n,s,r,a){const o=[],l=i.scales[i.axes[e].scale].log,c=l==10?qi:wp,h=Wn(c(t));s=Kr(l,h),l==10&&(s=Fs[ci(s,Fs)]);let u=t,d=s*l;l==10&&(d=Fs[ci(d,Fs)]);do o.push(u),u=u+s,l==10&&!vs.has(u)&&(u=Ct(u,vs.get(s))),u>=d&&(s=u,d=s*l,l==10&&(d=Fs[ci(d,Fs)]));while(u<=n);return o}function eb(i,e,t,n,s,r,a){let l=i.scales[i.axes[e].scale].asinh,c=n>l?mh(i,e,Pn(l,t),n,s):[l],h=n>=0&&t<=0?[0]:[];return(t<-l?mh(i,e,Pn(l,-n),-t,s):[l]).reverse().map(d=>-d).concat(h,c)}const qp=/./,tb=/[12357]/,nb=/[125]/,pf=/1/,gh=(i,e,t,n)=>i.map((s,r)=>e==4&&s==0||r%n==0&&t.test(s.toExponential()[s<0?1:0])?s:null);function ib(i,e,t,n,s){let r=i.axes[t],a=r.scale,o=i.scales[a],l=i.valToPos,c=r._space,h=l(10,a),u=l(9,a)-h>=c?qp:l(7,a)-h>=c?tb:l(5,a)-h>=c?nb:pf;if(u==pf){let d=nn(l(1,a)-h);if(d<c)return gh(e.slice().reverse(),o.distr,u,Jn(c/d)).reverse()}return gh(e,o.distr,u,1)}function sb(i,e,t,n,s){let r=i.axes[t],a=r.scale,o=r._space,l=i.valToPos,c=nn(l(1,a)-l(2,a));return c<o?gh(e.slice().reverse(),3,qp,Jn(o/c)).reverse():e}function rb(i,e,t,n){return n==null?Hh:e==null?"":Xh(e)}const mf={show:!0,scale:"y",stroke:kh,space:30,gap:5,alignTo:1,size:50,labelGap:0,labelSize:30,labelFont:Wp,side:3,grid:jh,ticks:Vp,border:Gp,font:Kh,lineGap:Xp,rotate:0};function ab(i,e){let t=3+(i||1)*2;return Ct(t*e,3)}function ob(i,e){let{scale:t,idxs:n}=i.series[0],s=i._data[0],r=i.valToPos(s[n[0]],t,!0),a=i.valToPos(s[n[1]],t,!0),o=nn(a-r),l=i.series[e],c=o/(l.points.space*Mt);return n[1]-n[0]<=c}const gf={scale:null,auto:!0,sorted:0,min:Rt,max:-Rt},$p=(i,e,t,n,s)=>s,_f={show:!0,auto:!0,sorted:0,gaps:$p,alpha:1,facets:[Jt({},gf,{scale:"x"}),Jt({},gf,{scale:"y"})]},xf={scale:"y",auto:!0,sorted:0,show:!0,spanGaps:!1,gaps:$p,alpha:1,points:{show:ob,filter:null},values:null,min:Rt,max:-Rt,idxs:[],path:null,clip:null};function lb(i,e,t,n,s){return t/10}const Yp={time:IM,auto:!0,distr:1,log:10,asinh:1,min:null,max:null,dir:1,ori:0},cb=Jt({},Yp,{time:!1,ori:1}),vf={};function jp(i,e){let t=vf[i];return t||(t={key:i,plots:[],sub(n){t.plots.push(n)},unsub(n){t.plots=t.plots.filter(s=>s!=n)},pub(n,s,r,a,o,l,c){for(let h=0;h<t.plots.length;h++)t.plots[h]!=s&&t.plots[h].pub(n,s,r,a,o,l,c)}},i!=null&&(vf[i]=t)),t}const Qr=1,_h=2;function Zs(i,e,t){const n=i.mode,s=i.series[e],r=n==2?i._data[e]:i._data,a=i.scales,o=i.bbox;let l=r[0],c=n==2?r[1]:r[e],h=n==2?a[s.facets[0].scale]:a[i.series[0].scale],u=n==2?a[s.facets[1].scale]:a[s.scale],d=o.left,f=o.top,g=o.width,_=o.height,p=i.valToPosH,m=i.valToPosV;return h.ori==0?t(s,l,c,h,u,p,m,d,f,g,_,xl,sa,yl,Zp,Qp):t(s,l,c,h,u,m,p,f,d,_,g,vl,ra,Qh,Jp,em)}function Zh(i,e){let t=0,n=0,s=vt(i.bands,qh);for(let r=0;r<s.length;r++){let a=s[r];a.series[0]==e?t=a.dir:a.series[1]==e&&(a.dir==1?n|=1:n|=2)}return[t,n==1?-1:n==2?1:n==3?2:0]}function hb(i,e,t,n,s){let r=i.mode,a=i.series[e],o=r==2?a.facets[1].scale:a.scale,l=i.scales[o];return s==-1?l.min:s==1?l.max:l.distr==3?l.dir==1?l.min:l.max:0}function $i(i,e,t,n,s,r){return Zs(i,e,(a,o,l,c,h,u,d,f,g,_,p)=>{let m=a.pxRound;const M=c.dir*(c.ori==0?1:-1),v=c.ori==0?sa:ra;let b,N;M==1?(b=t,N=n):(b=n,N=t);let A=m(u(o[b],c,_,f)),R=m(d(l[b],h,p,g)),F=m(u(o[N],c,_,f)),w=m(d(r==1?h.max:h.min,h,p,g)),y=new Path2D(s);return v(y,F,w),v(y,A,w),v(y,A,R),y})}function _l(i,e,t,n,s,r){let a=null;if(i.length>0){a=new Path2D;const o=e==0?yl:Qh;let l=t;for(let u=0;u<i.length;u++){let d=i[u];if(d[1]>d[0]){let f=d[0]-l;f>0&&o(a,l,n,f,n+r),l=d[1]}}let c=t+s-l,h=10;c>0&&o(a,l,n-h/2,c,n+r+h)}return a}function ub(i,e,t){let n=i[i.length-1];n&&n[0]==e?n[1]=t:i.push([e,t])}function Jh(i,e,t,n,s,r,a){let o=[],l=i.length;for(let c=s==1?t:n;c>=t&&c<=n;c+=s)if(e[c]===null){let u=c,d=c;if(s==1)for(;++c<=n&&e[c]===null;)d=c;else for(;--c>=t&&e[c]===null;)d=c;let f=r(i[u]),g=d==u?f:r(i[d]),_=u-s;f=a<=0&&_>=0&&_<l?r(i[_]):f;let m=d+s;g=a>=0&&m>=0&&m<l?r(i[m]):g,g>=f&&o.push([f,g])}return o}function yf(i){return i==0?Tp:i==1?tn:e=>Ns(e,i)}function Kp(i){let e=i==0?xl:vl,t=i==0?(s,r,a,o,l,c)=>{s.arcTo(r,a,o,l,c)}:(s,r,a,o,l,c)=>{s.arcTo(a,r,l,o,c)},n=i==0?(s,r,a,o,l)=>{s.rect(r,a,o,l)}:(s,r,a,o,l)=>{s.rect(a,r,l,o)};return(s,r,a,o,l,c=0,h=0)=>{c==0&&h==0?n(s,r,a,o,l):(c=di(c,o/2,l/2),h=di(h,o/2,l/2),e(s,r+c,a),t(s,r+o,a,r+o,a+l,c),t(s,r+o,a+l,r,a+l,h),t(s,r,a+l,r,a,h),t(s,r,a,r+o,a,c),s.closePath())}}const xl=(i,e,t)=>{i.moveTo(e,t)},vl=(i,e,t)=>{i.moveTo(t,e)},sa=(i,e,t)=>{i.lineTo(e,t)},ra=(i,e,t)=>{i.lineTo(t,e)},yl=Kp(0),Qh=Kp(1),Zp=(i,e,t,n,s,r)=>{i.arc(e,t,n,s,r)},Jp=(i,e,t,n,s,r)=>{i.arc(t,e,n,s,r)},Qp=(i,e,t,n,s,r,a)=>{i.bezierCurveTo(e,t,n,s,r,a)},em=(i,e,t,n,s,r,a)=>{i.bezierCurveTo(t,e,s,n,a,r)};function tm(i){return(e,t,n,s,r)=>Zs(e,t,(a,o,l,c,h,u,d,f,g,_,p)=>{let{pxRound:m,points:M}=a,v,b;c.ori==0?(v=xl,b=Zp):(v=vl,b=Jp);const N=Ct(M.width*Mt,3);let A=(M.size-M.width)/2*Mt,R=Ct(A*2,3),F=new Path2D,w=new Path2D,{left:y,top:P,width:K,height:H}=e.bbox;yl(w,y-R,P-R,K+R*2,H+R*2);const Z=q=>{if(l[q]!=null){let ee=m(u(o[q],c,_,f)),Y=m(d(l[q],h,p,g));v(F,ee+A,Y),b(F,ee,Y,A,0,qo*2)}};if(r)r.forEach(Z);else for(let q=n;q<=s;q++)Z(q);return{stroke:N>0?F:null,fill:F,clip:w,flags:Qr|_h}})}function nm(i){return(e,t,n,s,r,a)=>{n!=s&&(r!=n&&a!=n&&i(e,t,n),r!=s&&a!=s&&i(e,t,s),i(e,t,a))}}const db=nm(sa),fb=nm(ra);function im(i){const e=vt(i==null?void 0:i.alignGaps,0);return(t,n,s,r)=>Zs(t,n,(a,o,l,c,h,u,d,f,g,_,p)=>{[s,r]=fl(l,s,r);let m=a.pxRound,M=H=>m(u(H,c,_,f)),v=H=>m(d(H,h,p,g)),b,N;c.ori==0?(b=sa,N=db):(b=ra,N=fb);const A=c.dir*(c.ori==0?1:-1),R={stroke:new Path2D,fill:null,clip:null,band:null,gaps:null,flags:Qr},F=R.stroke;let w=!1;if(r-s>=_*4){let H=ye=>t.posToVal(ye,c.key,!0),Z=null,q=null,ee,Y,ne,ge=M(o[A==1?s:r]),de=M(o[s]),ve=M(o[r]),Te=H(A==1?de+1:ve-1);for(let ye=A==1?s:r;ye>=s&&ye<=r;ye+=A){let ie=o[ye],Me=(A==1?ie<Te:ie>Te)?ge:M(ie),fe=l[ye];Me==ge?fe!=null?(Y=fe,Z==null?(b(F,Me,v(Y)),ee=Z=q=Y):Y<Z?Z=Y:Y>q&&(q=Y)):fe===null&&(w=!0):(Z!=null&&N(F,ge,v(Z),v(q),v(ee),v(Y)),fe!=null?(Y=fe,b(F,Me,v(Y)),Z=q=ee=Y):(Z=q=null,fe===null&&(w=!0)),ge=Me,Te=H(ge+A))}Z!=null&&Z!=q&&ne!=ge&&N(F,ge,v(Z),v(q),v(ee),v(Y))}else for(let H=A==1?s:r;H>=s&&H<=r;H+=A){let Z=l[H];Z===null?w=!0:Z!=null&&b(F,M(o[H]),v(Z))}let[P,K]=Zh(t,n);if(a.fill!=null||P!=0){let H=R.fill=new Path2D(F),Z=a.fillTo(t,n,a.min,a.max,P),q=v(Z),ee=M(o[s]),Y=M(o[r]);A==-1&&([Y,ee]=[ee,Y]),b(H,Y,q),b(H,ee,q)}if(!a.spanGaps){let H=[];w&&H.push(...Jh(o,l,s,r,A,M,e)),R.gaps=H=a.gaps(t,n,s,r,H),R.clip=_l(H,c.ori,f,g,_,p)}return K!=0&&(R.band=K==2?[$i(t,n,s,r,F,-1),$i(t,n,s,r,F,1)]:$i(t,n,s,r,F,K)),R})}function pb(i){const e=vt(i.align,1),t=vt(i.ascDesc,!1),n=vt(i.alignGaps,0),s=vt(i.extend,!1);return(r,a,o,l)=>Zs(r,a,(c,h,u,d,f,g,_,p,m,M,v)=>{[o,l]=fl(u,o,l);let b=c.pxRound,{left:N,width:A}=r.bbox,R=de=>b(g(de,d,M,p)),F=de=>b(_(de,f,v,m)),w=d.ori==0?sa:ra;const y={stroke:new Path2D,fill:null,clip:null,band:null,gaps:null,flags:Qr},P=y.stroke,K=d.dir*(d.ori==0?1:-1);let H=F(u[K==1?o:l]),Z=R(h[K==1?o:l]),q=Z,ee=Z;s&&e==-1&&(ee=N,w(P,ee,H)),w(P,Z,H);for(let de=K==1?o:l;de>=o&&de<=l;de+=K){let ve=u[de];if(ve==null)continue;let Te=R(h[de]),ye=F(ve);e==1?w(P,Te,H):w(P,q,ye),w(P,Te,ye),H=ye,q=Te}let Y=q;s&&e==1&&(Y=N+A,w(P,Y,H));let[ne,ge]=Zh(r,a);if(c.fill!=null||ne!=0){let de=y.fill=new Path2D(P),ve=c.fillTo(r,a,c.min,c.max,ne),Te=F(ve);w(de,Y,Te),w(de,ee,Te)}if(!c.spanGaps){let de=[];de.push(...Jh(h,u,o,l,K,R,n));let ve=c.width*Mt/2,Te=t||e==1?ve:-ve,ye=t||e==-1?-ve:ve;de.forEach(ie=>{ie[0]+=Te,ie[1]+=ye}),y.gaps=de=c.gaps(r,a,o,l,de),y.clip=_l(de,d.ori,p,m,M,v)}return ge!=0&&(y.band=ge==2?[$i(r,a,o,l,P,-1),$i(r,a,o,l,P,1)]:$i(r,a,o,l,P,ge)),y})}function Mf(i,e,t,n,s,r,a=Rt){if(i.length>1){let o=null;for(let l=0,c=1/0;l<i.length;l++)if(e[l]!==void 0){if(o!=null){let h=nn(i[l]-i[o]);h<c&&(c=h,a=nn(t(i[l],n,s,r)-t(i[o],n,s,r)))}o=l}}return a}function mb(i){i=i||Na;const e=vt(i.size,[.6,Rt,1]),t=i.align||0,n=i.gap||0;let s=i.radius;s=s==null?[0,0]:typeof s=="number"?[s,0]:s;const r=ft(s),a=1-e[0],o=vt(e[1],Rt),l=vt(e[2],1),c=vt(i.disp,Na),h=vt(i.each,f=>{}),{fill:u,stroke:d}=c;return(f,g,_,p)=>Zs(f,g,(m,M,v,b,N,A,R,F,w,y,P)=>{let K=m.pxRound,H=t,Z=n*Mt,q=o*Mt,ee=l*Mt,Y,ne;b.ori==0?[Y,ne]=r(f,g):[ne,Y]=r(f,g);const ge=b.dir*(b.ori==0?1:-1);let de=b.ori==0?yl:Qh,ve=b.ori==0?h:(X,we,_e,Re,Ze,me,Ae)=>{h(X,we,_e,Ze,Re,Ae,me)},Te=vt(f.bands,qh).find(X=>X.series[0]==g),ye=Te!=null?Te.dir:0,ie=m.fillTo(f,g,m.min,m.max,ye),he=K(R(ie,N,P,w)),Me,fe,ze,Ge=y,Fe=K(m.width*Mt),pt=!1,O=null,dt=null,st=null,ct=null;u!=null&&(Fe==0||d!=null)&&(pt=!0,O=u.values(f,g,_,p),dt=new Map,new Set(O).forEach(X=>{X!=null&&dt.set(X,new Path2D)}),Fe>0&&(st=d.values(f,g,_,p),ct=new Map,new Set(st).forEach(X=>{X!=null&&ct.set(X,new Path2D)})));let{x0:Oe,size:wt}=c;if(Oe!=null&&wt!=null){H=1,M=Oe.values(f,g,_,p),Oe.unit==2&&(M=M.map(_e=>f.posToVal(F+_e*y,b.key,!0)));let X=wt.values(f,g,_,p);wt.unit==2?fe=X[0]*y:fe=A(X[0],b,y,F)-A(0,b,y,F),Ge=Mf(M,v,A,b,y,F,Ge),ze=Ge-fe+Z}else Ge=Mf(M,v,A,b,y,F,Ge),ze=Ge*a+Z,fe=Ge-ze;ze<1&&(ze=0),Fe>=fe/2&&(Fe=0),ze<5&&(K=Tp);let Ye=ze>0,qe=Ge-ze-(Ye?Fe:0);fe=K(ph(qe,ee,q)),Me=(H==0?fe/2:H==ge?0:fe)-H*ge*((H==0?Z/2:0)+(Ye?Fe/2:0));const D={stroke:null,fill:null,clip:null,band:null,gaps:null,flags:0},E=pt?null:new Path2D;let Q=null;if(Te!=null)Q=f.data[Te.series[1]];else{let{y0:X,y1:we}=c;X!=null&&we!=null&&(v=we.values(f,g,_,p),Q=X.values(f,g,_,p))}let le=Y*fe,te=ne*fe;for(let X=ge==1?_:p;X>=_&&X<=p;X+=ge){let we=v[X];if(we==null)continue;if(Q!=null){let be=Q[X]??0;if(we-be==0)continue;he=R(be,N,P,w)}let _e=b.distr!=2||c!=null?M[X]:X,Re=A(_e,b,y,F),Ze=R(vt(we,ie),N,P,w),me=K(Re-Me),Ae=K(Pn(Ze,he)),Je=K(di(Ze,he)),ke=Ae-Je;if(we!=null){let be=we<0?te:le,He=we<0?le:te;pt?(Fe>0&&st[X]!=null&&de(ct.get(st[X]),me,Je+Wn(Fe/2),fe,Pn(0,ke-Fe),be,He),O[X]!=null&&de(dt.get(O[X]),me,Je+Wn(Fe/2),fe,Pn(0,ke-Fe),be,He)):de(E,me,Je+Wn(Fe/2),fe,Pn(0,ke-Fe),be,He),ve(f,g,X,me-Fe/2,Je,fe+Fe,ke)}}return Fe>0?D.stroke=pt?ct:E:pt||(D._fill=m.width==0?m._fill:m._stroke??m._fill,D.width=0),D.fill=pt?dt:E,D})}function gb(i,e){const t=vt(e==null?void 0:e.alignGaps,0);return(n,s,r,a)=>Zs(n,s,(o,l,c,h,u,d,f,g,_,p,m)=>{[r,a]=fl(c,r,a);let M=o.pxRound,v=Y=>M(d(Y,h,p,g)),b=Y=>M(f(Y,u,m,_)),N,A,R;h.ori==0?(N=xl,R=sa,A=Qp):(N=vl,R=ra,A=em);const F=h.dir*(h.ori==0?1:-1);let w=v(l[F==1?r:a]),y=w,P=[],K=[];for(let Y=F==1?r:a;Y>=r&&Y<=a;Y+=F)if(c[Y]!=null){let ge=l[Y],de=v(ge);P.push(y=de),K.push(b(c[Y]))}const H={stroke:i(P,K,N,R,A,M),fill:null,clip:null,band:null,gaps:null,flags:Qr},Z=H.stroke;let[q,ee]=Zh(n,s);if(o.fill!=null||q!=0){let Y=H.fill=new Path2D(Z),ne=o.fillTo(n,s,o.min,o.max,q),ge=b(ne);R(Y,y,ge),R(Y,w,ge)}if(!o.spanGaps){let Y=[];Y.push(...Jh(l,c,r,a,F,v,t)),H.gaps=Y=o.gaps(n,s,r,a,Y),H.clip=_l(Y,h.ori,g,_,p,m)}return ee!=0&&(H.band=ee==2?[$i(n,s,r,a,Z,-1),$i(n,s,r,a,Z,1)]:$i(n,s,r,a,Z,ee)),H})}function _b(i){return gb(xb,i)}function xb(i,e,t,n,s,r){const a=i.length;if(a<2)return null;const o=new Path2D;if(t(o,i[0],e[0]),a==2)n(o,i[1],e[1]);else{let l=Array(a),c=Array(a-1),h=Array(a-1),u=Array(a-1);for(let d=0;d<a-1;d++)h[d]=e[d+1]-e[d],u[d]=i[d+1]-i[d],c[d]=h[d]/u[d];l[0]=c[0];for(let d=1;d<a-1;d++)c[d]===0||c[d-1]===0||c[d-1]>0!=c[d]>0?l[d]=0:(l[d]=3*(u[d-1]+u[d])/((2*u[d]+u[d-1])/c[d-1]+(u[d]+2*u[d-1])/c[d]),isFinite(l[d])||(l[d]=0));l[a-1]=c[a-2];for(let d=0;d<a-1;d++)s(o,i[d]+u[d]/3,e[d]+l[d]*u[d]/3,i[d+1]-u[d]/3,e[d+1]-l[d+1]*u[d]/3,i[d+1],e[d+1])}return o}const xh=new Set;function Sf(){for(let i of xh)i.syncRect(!0)}ia&&(Xs(JM,Gr,Sf),Xs(QM,Gr,Sf,!0),Xs(rl,Gr,()=>{pn.pxRatio=Mt}));const vb=im(),yb=tm();function bf(i,e,t,n){return(n?[i[0],i[1]].concat(i.slice(2)):[i[0]].concat(i.slice(1))).map((r,a)=>vh(r,a,e,t))}function Mb(i,e){return i.map((t,n)=>n==0?{}:Jt({},e,t))}function vh(i,e,t,n){return Jt({},e==0?t:n,i)}function sm(i,e,t){return e==null?Zr:[e,t]}const Sb=sm;function bb(i,e,t){return e==null?Zr:al(e,t,Wh,!0)}function rm(i,e,t,n){return e==null?Zr:pl(e,t,i.scales[n].log,!1)}const wb=rm;function am(i,e,t,n){return e==null?Zr:Gh(e,t,i.scales[n].log,!1)}const Eb=am;function Tb(i,e,t,n,s){let r=Pn(ef(i),ef(e)),a=e-i,o=ci(s/n*a,t);do{let l=t[o],c=n*l/a;if(c>=s&&r+(l<5?vs.get(l):0)<=17)return[l,c]}while(++o<t.length);return[0,0]}function wf(i){let e,t;return i=i.replace(/(\d+)px/,(n,s)=>(e=tn((t=+s)*Mt))+"px"),[i,e,t]}function Ab(i){i.show&&[i.font,i.labelFont].forEach(e=>{let t=Ct(e[2]*Mt,1);e[0]=e[0].replace(/[0-9.]+px/,t+"px"),e[1]=t})}function pn(i,e,t){const n={mode:vt(i.mode,1)},s=n.mode;function r(x,S,C,L){let k=S.valToPct(x);return L+C*(S.dir==-1?1-k:k)}function a(x,S,C,L){let k=S.valToPct(x);return L+C*(S.dir==-1?k:1-k)}function o(x,S,C,L){return S.ori==0?r(x,S,C,L):a(x,S,C,L)}n.valToPosH=r,n.valToPosV=a;let l=!1;n.status=0;const c=n.root=Kn(UM);if(i.id!=null&&(c.id=i.id),Gn(c,i.class),i.title){let x=Kn(OM,c);x.textContent=i.title}const h=li("canvas"),u=n.ctx=h.getContext("2d"),d=Kn(BM,c);Xs("click",d,x=>{x.target===g&&(It!=ir||Vt!=sr)&&_n.click(n,x)},!0);const f=n.under=Kn(zM,d);d.appendChild(h);const g=n.over=Kn(kM,d);i=Jr(i);const _=+vt(i.pxAlign,1),p=yf(_);(i.plugins||[]).forEach(x=>{x.opts&&(i=x.opts(n,i)||i)});const m=i.ms||.001,M=n.series=s==1?bf(i.series||[],ff,xf,!1):Mb(i.series||[null],_f),v=n.axes=bf(i.axes||[],df,mf,!0),b=n.scales={},N=n.bands=i.bands||[];N.forEach(x=>{x.fill=ft(x.fill||null),x.dir=vt(x.dir,-1)});const A=s==2?M[1].facets[0].scale:M[0].scale,R={axes:xm,series:Dn},F=(i.drawOrder||["axes","series"]).map(x=>R[x]);function w(x){const S=x.distr==3?C=>qi(C>0?C:x.clamp(n,C,x.min,x.max,x.key)):x.distr==4?C=>vc(C,x.asinh):x.distr==100?C=>x.fwd(C):C=>C;return C=>{let L=S(C),{_min:k,_max:j}=x,oe=j-k;return(L-k)/oe}}function y(x){let S=b[x];if(S==null){let C=(i.scales||Na)[x]||Na;if(C.from!=null){y(C.from);let L=Jt({},b[C.from],C,{key:x});L.valToPct=w(L),b[x]=L}else{S=b[x]=Jt({},x==A?Yp:cb,C),S.key=x;let L=S.time,k=S.range,j=hs(k);if((x!=A||s==2&&!L)&&(j&&(k[0]==null||k[1]==null)&&(k={min:k[0]==null?Zd:{mode:1,hard:k[0],soft:k[0]},max:k[1]==null?Zd:{mode:1,hard:k[1],soft:k[1]}},j=!1),!j&&gl(k))){let oe=k;k=(pe,Se,De)=>Se==null?Zr:al(Se,De,oe)}S.range=ft(k||(L?Sb:x==A?S.distr==3?wb:S.distr==4?Eb:sm:S.distr==3?rm:S.distr==4?am:bb)),S.auto=ft(j?!1:S.auto),S.clamp=ft(S.clamp||lb),S._min=S._max=null,S.valToPct=w(S)}}}y("x"),y("y"),s==1&&M.forEach(x=>{y(x.scale)}),v.forEach(x=>{y(x.scale)});for(let x in i.scales)y(x);const P=b[A],K=P.distr;let H,Z;P.ori==0?(Gn(c,NM),H=r,Z=a):(Gn(c,FM),H=a,Z=r);const q={};for(let x in b){let S=b[x];(S.min!=null||S.max!=null)&&(q[x]={min:S.min,max:S.max},S.min=S.max=null)}const ee=i.tzDate||(x=>new Date(tn(x/m))),Y=i.fmtDate||$h,ne=m==1?NS(ee):BS(ee),ge=cf(ee,lf(m==1?US:OS,Y)),de=uf(ee,hf(kS,Y)),ve=[],Te=n.legend=Jt({},GS,i.legend),ye=n.cursor=Jt({},jS,{drag:{y:s==2}},i.cursor),ie=Te.show,he=ye.show,Me=Te.markers;Te.idxs=ve,Me.width=ft(Me.width),Me.dash=ft(Me.dash),Me.stroke=ft(Me.stroke),Me.fill=ft(Me.fill);let fe,ze,Ge,Fe=[],pt=[],O,dt=!1,st={};if(Te.live){const x=M[1]?M[1].values:null;dt=x!=null,O=dt?x(n,1,0):{_:0};for(let S in O)st[S]=Hh}if(ie)if(fe=li("table",qM,c),Ge=li("tbody",null,fe),Te.mount(n,fe),dt){ze=li("thead",null,fe,Ge);let x=li("tr",null,ze);li("th",null,x);for(var ct in O)li("th",Bd,x).textContent=ct}else Gn(fe,YM),Te.live&&Gn(fe,$M);const Oe={show:!0},wt={show:!1};function Ye(x,S){if(S==0&&(dt||!Te.live||s==2))return Zr;let C=[],L=li("tr",jM,Ge,Ge.childNodes[S]);Gn(L,x.class),x.show||Gn(L,zs);let k=li("th",null,L);if(Me.show){let pe=Kn(KM,k);if(S>0){let Se=Me.width(n,S);Se&&(pe.style.border=Se+"px "+Me.dash(n,S)+" "+Me.stroke(n,S)),pe.style.background=Me.fill(n,S)}}let j=Kn(Bd,k);x.label instanceof HTMLElement?j.appendChild(x.label):j.textContent=x.label,S>0&&(Me.show||(j.style.color=x.width>0?Me.stroke(n,S):Me.fill(n,S)),D("click",k,pe=>{if(ye._lock)return;kt(pe);let Se=M.indexOf(x);if((pe.ctrlKey||pe.metaKey)!=Te.isolate){let De=M.some((Ie,Ne)=>Ne>0&&Ne!=Se&&Ie.show);M.forEach((Ie,Ne)=>{Ne>0&&xi(Ne,De?Ne==Se?Oe:wt:Oe,!0,Kt.setSeries)})}else xi(Se,{show:!x.show},!0,Kt.setSeries)},!1),gi&&D(Vd,k,pe=>{ye._lock||(kt(pe),xi(M.indexOf(x),ar,!0,Kt.setSeries))},!1));for(var oe in O){let pe=li("td",ZM,L);pe.textContent="--",C.push(pe)}return[L,C]}const qe=new Map;function D(x,S,C,L=!0){const k=qe.get(S)||{},j=ye.bind[x](n,S,C,L);j&&(Xs(x,S,k[x]=j),qe.set(S,k))}function E(x,S,C){const L=qe.get(S)||{};for(let k in L)(x==null||k==x)&&(fh(k,S,L[k]),delete L[k]);x==null&&qe.delete(S)}let Q=0,le=0,te=0,X=0,we=0,_e=0,Re=we,Ze=_e,me=te,Ae=X,Je=0,ke=0,be=0,He=0;n.bbox={};let B=!1,ce=!1,U=!1,ae=!1,se=!1,re=!1;function xe(x,S,C){(C||x!=n.width||S!=n.height)&&Ke(x,S),Qs(!1),U=!0,ce=!0,er()}function Ke(x,S){n.width=Q=te=x,n.height=le=X=S,we=_e=0,lt(),mn();let C=n.bbox;Je=C.left=Ns(we*Mt,.5),ke=C.top=Ns(_e*Mt,.5),be=C.width=Ns(te*Mt,.5),He=C.height=Ns(X*Mt,.5)}const ot=3;function _t(){let x=!1,S=0;for(;!x;){S++;let C=gm(S),L=_m(S);x=S==ot||C&&L,x||(Ke(n.width,n.height),ce=!0)}}function Et({width:x,height:S}){xe(x,S)}n.setSize=Et;function lt(){let x=!1,S=!1,C=!1,L=!1;v.forEach((k,j)=>{if(k.show&&k._show){let{side:oe,_size:pe}=k,Se=oe%2,De=k.label!=null?k.labelSize:0,Ie=pe+De;Ie>0&&(Se?(te-=Ie,oe==3?(we+=Ie,L=!0):C=!0):(X-=Ie,oe==0?(_e+=Ie,x=!0):S=!0))}}),Ii[0]=x,Ii[1]=C,Ii[2]=S,Ii[3]=L,te-=J[1]+J[3],we+=J[3],X-=J[2]+J[0],_e+=J[0]}function mn(){let x=we+te,S=_e+X,C=we,L=_e;function k(j,oe){switch(j){case 1:return x+=oe,x-oe;case 2:return S+=oe,S-oe;case 3:return C-=oe,C+oe;case 0:return L-=oe,L+oe}}v.forEach((j,oe)=>{if(j.show&&j._show){let pe=j.side;j._pos=k(pe,j._size),j.label!=null&&(j._lpos=k(pe,j.labelSize))}})}if(ye.dataIdx==null){let x=ye.hover,S=x.skip=new Set(x.skip??[]);S.add(void 0);let C=x.prox=ft(x.prox),L=x.bias??(x.bias=0);ye.dataIdx=(k,j,oe,pe)=>{if(j==0)return oe;let Se=oe,De=C(k,j,oe,pe)??Rt,Ie=De>=0&&De<Rt,Ne=P.ori==0?te:X,it=ye.left,yt=e[0],xt=e[j];if(S.has(xt[oe])){Se=null;let ut=null,tt=null,We;if(L==0||L==-1)for(We=oe;ut==null&&We-- >0;)S.has(xt[We])||(ut=We);if(L==0||L==1)for(We=oe;tt==null&&We++<xt.length;)S.has(xt[We])||(tt=We);if(ut!=null||tt!=null)if(Ie){let Nt=ut==null?-1/0:H(yt[ut],P,Ne,0),qt=tt==null?1/0:H(yt[tt],P,Ne,0),dn=it-Nt,At=qt-it;dn<=At?dn<=De&&(Se=ut):At<=De&&(Se=tt)}else Se=tt==null?ut:ut==null?tt:oe-ut<=tt-oe?ut:tt}else Ie&&nn(it-H(yt[oe],P,Ne,0))>De&&(Se=null);return Se}}const kt=x=>{ye.event=x};ye.idxs=ve,ye._lock=!1;let Ht=ye.points;Ht.show=ft(Ht.show),Ht.size=ft(Ht.size),Ht.stroke=ft(Ht.stroke),Ht.width=ft(Ht.width),Ht.fill=ft(Ht.fill);const ln=n.focus=Jt({},i.focus||{alpha:.3},ye.focus),gi=ln.prox>=0,Li=gi&&Ht.one;let wn=[],ni=[],Di=[];function bs(x,S){let C=Ht.show(n,S);if(C instanceof HTMLElement)return Gn(C,XM),Gn(C,x.class),Si(C,-10,-10,te,X),g.insertBefore(C,wn[S]),C}function la(x,S){if(s==1||S>0){let C=s==1&&b[x.scale].time,L=x.value;x.value=C?sf(L)?uf(ee,hf(L,Y)):L||de:L||rb,x.label=x.label||(C?ZS:KS)}if(Li||S>0){x.width=x.width==null?1:x.width,x.paths=x.paths||vb||cS,x.fillTo=ft(x.fillTo||hb),x.pxAlign=+vt(x.pxAlign,_),x.pxRound=yf(x.pxAlign),x.stroke=ft(x.stroke||null),x.fill=ft(x.fill||null),x._stroke=x._fill=x._paths=x._focus=null;let C=ab(Pn(1,x.width),1),L=x.points=Jt({},{size:C,width:Pn(1,C*.2),stroke:x.stroke,space:C*2,paths:yb,_stroke:null,_fill:null},x.points);L.show=ft(L.show),L.filter=ft(L.filter),L.fill=ft(L.fill),L.stroke=ft(L.stroke),L.paths=ft(L.paths),L.pxAlign=x.pxAlign}if(ie){let C=Ye(x,S);Fe.splice(S,0,C[0]),pt.splice(S,0,C[1]),Te.values.push(null)}if(he){ve.splice(S,0,null);let C=null;Li?S==0&&(C=bs(x,S)):S>0&&(C=bs(x,S)),wn.splice(S,0,C),ni.splice(S,0,0),Di.splice(S,0,0)}un("addSeries",S)}function ja(x,S){S=S??M.length,x=s==1?vh(x,S,ff,xf):vh(x,S,{},_f),M.splice(S,0,x),la(M[S],S)}n.addSeries=ja;function Tl(x){if(M.splice(x,1),ie){Te.values.splice(x,1),pt.splice(x,1);let S=Fe.splice(x,1)[0];E(null,S.firstChild),S.remove()}he&&(ve.splice(x,1),wn.splice(x,1)[0].remove(),ni.splice(x,1),Di.splice(x,1)),un("delSeries",x)}n.delSeries=Tl;const Ii=[!1,!1,!1,!1];function Al(x,S){if(x._show=x.show,x.show){let C=x.side%2,L=b[x.scale];L==null&&(x.scale=C?M[1].scale:A,L=b[x.scale]);let k=L.time;x.size=ft(x.size),x.space=ft(x.space),x.rotate=ft(x.rotate),hs(x.incrs)&&x.incrs.forEach(oe=>{!vs.has(oe)&&vs.set(oe,Cp(oe))}),x.incrs=ft(x.incrs||(L.distr==2?LS:k?m==1?IS:FS:Fs)),x.splits=ft(x.splits||(k&&L.distr==1?ne:L.distr==3?mh:L.distr==4?eb:QS)),x.stroke=ft(x.stroke),x.grid.stroke=ft(x.grid.stroke),x.ticks.stroke=ft(x.ticks.stroke),x.border.stroke=ft(x.border.stroke);let j=x.values;x.values=hs(j)&&!hs(j[0])?ft(j):k?hs(j)?cf(ee,lf(j,Y)):sf(j)?zS(ee,j):j||ge:j||JS,x.filter=ft(x.filter||(L.distr>=3&&L.log==10?ib:L.distr==3&&L.log==2?sb:Ap)),x.font=wf(x.font),x.labelFont=wf(x.labelFont),x._size=x.size(n,null,S,0),x._space=x._rotate=x._incrs=x._found=x._splits=x._values=null,x._size>0&&(Ii[S]=!0,x._el=Kn(HM,d))}}function T(x,S,C,L){let[k,j,oe,pe]=C,Se=S%2,De=0;return Se==0&&(pe||j)&&(De=S==0&&!k||S==2&&!oe?tn(df.size/3):0),Se==1&&(k||oe)&&(De=S==1&&!j||S==3&&!pe?tn(mf.size/2):0),De}const W=n.padding=(i.padding||[T,T,T,T]).map(x=>ft(vt(x,T))),J=n._padding=W.map((x,S)=>x(n,S,Ii,0));let $,G=null,ue=null;const Pe=s==1?M[0].idxs:null;let Le=null,Ue=!1;function Qe(x,S){if(e=x??[],n.data=n._data=e,s==2){$=0;for(let C=1;C<M.length;C++)$+=e[C][0].length}else{e.length==0&&(n.data=n._data=e=[[]]),Le=e[0],$=Le.length;let C=e;if(K==2){C=e.slice();let L=C[0]=Array($);for(let k=0;k<$;k++)L[k]=k}n._data=e=C}if(Qs(!0),un("setData"),K==2&&(U=!0),S!==!1){let C=P;C.auto(n,Ue)?et():Qi(A,C.min,C.max),ae=ae||ye.left>=0,re=!0,er()}}n.setData=Qe;function et(){Ue=!0;let x,S;s==1&&($>0?(G=Pe[0]=0,ue=Pe[1]=$-1,x=e[0][G],S=e[0][ue],K==2?(x=G,S=ue):x==S&&(K==3?[x,S]=pl(x,x,P.log,!1):K==4?[x,S]=Gh(x,x,P.log,!1):P.time?S=x+tn(86400/m):[x,S]=al(x,S,Wh,!0))):(G=Pe[0]=x=null,ue=Pe[1]=S=null)),Qi(A,x,S)}let Be,ht,Pt,Lt,gn,mt,Ve,Yt,gt,Dt;function Ui(x,S,C,L,k,j){x??(x=kd),C??(C=qh),L??(L="butt"),k??(k=kd),j??(j="round"),x!=Be&&(u.strokeStyle=Be=x),k!=ht&&(u.fillStyle=ht=k),S!=Pt&&(u.lineWidth=Pt=S),j!=gn&&(u.lineJoin=gn=j),L!=mt&&(u.lineCap=mt=L),C!=Lt&&u.setLineDash(Lt=C)}function vn(x,S,C,L){S!=ht&&(u.fillStyle=ht=S),x!=Ve&&(u.font=Ve=x),C!=Yt&&(u.textAlign=Yt=C),L!=gt&&(u.textBaseline=gt=L)}function ws(x,S,C,L,k=0){if(L.length>0&&x.auto(n,Ue)&&(S==null||S.min==null)){let j=vt(G,0),oe=vt(ue,L.length-1),pe=C.min==null?iS(L,j,oe,k,x.distr==3):[C.min,C.max];x.min=di(x.min,C.min=pe[0]),x.max=Pn(x.max,C.max=pe[1])}}const Wt={min:null,max:null};function _i(){for(let L in b){let k=b[L];q[L]==null&&(k.min==null||q[A]!=null&&k.auto(n,Ue))&&(q[L]=Wt)}for(let L in b){let k=b[L];q[L]==null&&k.from!=null&&q[k.from]!=null&&(q[L]=Wt)}q[A]!=null&&Qs(!0);let x={};for(let L in q){let k=q[L];if(k!=null){let j=x[L]=Jr(b[L],dS);if(k.min!=null)Jt(j,k);else if(L!=A||s==2)if($==0&&j.from==null){let oe=j.range(n,null,null,L);j.min=oe[0],j.max=oe[1]}else j.min=Rt,j.max=-Rt}}if($>0){M.forEach((L,k)=>{if(s==1){let j=L.scale,oe=q[j];if(oe==null)return;let pe=x[j];if(k==0){let Se=pe.range(n,pe.min,pe.max,j);pe.min=Se[0],pe.max=Se[1],G=ci(pe.min,e[0]),ue=ci(pe.max,e[0]),ue-G>1&&(e[0][G]<pe.min&&G++,e[0][ue]>pe.max&&ue--),L.min=Le[G],L.max=Le[ue]}else L.show&&L.auto&&ws(pe,oe,L,e[k],L.sorted);L.idxs[0]=G,L.idxs[1]=ue}else if(k>0&&L.show&&L.auto){let[j,oe]=L.facets,pe=j.scale,Se=oe.scale,[De,Ie]=e[k],Ne=x[pe],it=x[Se];Ne!=null&&ws(Ne,q[pe],j,De,j.sorted),it!=null&&ws(it,q[Se],oe,Ie,oe.sorted),L.min=oe.min,L.max=oe.max}});for(let L in x){let k=x[L],j=q[L];if(k.from==null&&(j==null||j.min==null)){let oe=k.range(n,k.min==Rt?null:k.min,k.max==-Rt?null:k.max,L);k.min=oe[0],k.max=oe[1]}}}for(let L in x){let k=x[L];if(k.from!=null){let j=x[k.from];if(j.min==null)k.min=k.max=null;else{let oe=k.range(n,j.min,j.max,L);k.min=oe[0],k.max=oe[1]}}}let S={},C=!1;for(let L in x){let k=x[L],j=b[L];if(j.min!=k.min||j.max!=k.max){j.min=k.min,j.max=k.max;let oe=j.distr;j._min=oe==3?qi(j.min):oe==4?vc(j.min,j.asinh):oe==100?j.fwd(j.min):j.min,j._max=oe==3?qi(j.max):oe==4?vc(j.max,j.asinh):oe==100?j.fwd(j.max):j.max,S[L]=C=!0}}if(C){M.forEach((L,k)=>{s==2?k>0&&S.y&&(L._paths=null):S[L.scale]&&(L._paths=null)});for(let L in S)U=!0,un("setScale",L);he&&ye.left>=0&&(ae=re=!0)}for(let L in q)q[L]=null}function ca(x){let S=ph(G-1,0,$-1),C=ph(ue+1,0,$-1);for(;x[S]==null&&S>0;)S--;for(;x[C]==null&&C<$-1;)C++;return[S,C]}function Dn(){if($>0){let x=M.some(S=>S._focus)&&Dt!=ln.alpha;x&&(u.globalAlpha=Dt=ln.alpha),M.forEach((S,C)=>{if(C>0&&S.show&&(Js(C,!1),Js(C,!0),S._paths==null)){let L=Dt;Dt!=S.alpha&&(u.globalAlpha=Dt=S.alpha);let k=s==2?[0,e[C][0].length-1]:ca(e[C]);S._paths=S.paths(n,C,k[0],k[1]),Dt!=L&&(u.globalAlpha=Dt=L)}}),M.forEach((S,C)=>{if(C>0&&S.show){let L=Dt;Dt!=S.alpha&&(u.globalAlpha=Dt=S.alpha),S._paths!=null&&Ka(C,!1);{let k=S._paths!=null?S._paths.gaps:null,j=S.points.show(n,C,G,ue,k),oe=S.points.filter(n,C,j,k);(j||oe)&&(S.points._paths=S.points.paths(n,C,G,ue,oe),Ka(C,!0))}Dt!=L&&(u.globalAlpha=Dt=L),un("drawSeries",C)}}),x&&(u.globalAlpha=Dt=1)}}function Js(x,S){let C=S?M[x].points:M[x];C._stroke=C.stroke(n,x),C._fill=C.fill(n,x)}function Ka(x,S){let C=S?M[x].points:M[x],{stroke:L,fill:k,clip:j,flags:oe,_stroke:pe=C._stroke,_fill:Se=C._fill,_width:De=C.width}=C._paths;De=Ct(De*Mt,3);let Ie=null,Ne=De%2/2;S&&Se==null&&(Se=De>0?"#fff":pe);let it=C.pxAlign==1&&Ne>0;if(it&&u.translate(Ne,Ne),!S){let yt=Je-De/2,xt=ke-De/2,ut=be+De,tt=He+De;Ie=new Path2D,Ie.rect(yt,xt,ut,tt)}S?Rl(pe,De,C.dash,C.cap,Se,L,k,oe,j):Za(x,pe,De,C.dash,C.cap,Se,L,k,oe,Ie,j),it&&u.translate(-Ne,-Ne)}function Za(x,S,C,L,k,j,oe,pe,Se,De,Ie){let Ne=!1;Se!=0&&N.forEach((it,yt)=>{if(it.series[0]==x){let xt=M[it.series[1]],ut=e[it.series[1]],tt=(xt._paths||Na).band;hs(tt)&&(tt=it.dir==1?tt[0]:tt[1]);let We,Nt=null;xt.show&&tt&&rS(ut,G,ue)?(Nt=it.fill(n,yt)||j,We=xt._paths.clip):tt=null,Rl(S,C,L,k,Nt,oe,pe,Se,De,Ie,We,tt),Ne=!0}}),Ne||Rl(S,C,L,k,j,oe,pe,Se,De,Ie)}const ru=Qr|_h;function Rl(x,S,C,L,k,j,oe,pe,Se,De,Ie,Ne){Ui(x,S,C,L,k),(Se||De||Ne)&&(u.save(),Se&&u.clip(Se),De&&u.clip(De)),Ne?(pe&ru)==ru?(u.clip(Ne),Ie&&u.clip(Ie),Qa(k,oe),Ja(x,j,S)):pe&_h?(Qa(k,oe),u.clip(Ne),Ja(x,j,S)):pe&Qr&&(u.save(),u.clip(Ne),Ie&&u.clip(Ie),Qa(k,oe),u.restore(),Ja(x,j,S)):(Qa(k,oe),Ja(x,j,S)),(Se||De||Ne)&&u.restore()}function Ja(x,S,C){C>0&&(S instanceof Map?S.forEach((L,k)=>{u.strokeStyle=Be=k,u.stroke(L)}):S!=null&&x&&u.stroke(S))}function Qa(x,S){S instanceof Map?S.forEach((C,L)=>{u.fillStyle=ht=L,u.fill(C)}):S!=null&&x&&u.fill(S)}function mm(x,S,C,L){let k=v[x],j;if(L<=0)j=[0,0];else{let oe=k._space=k.space(n,x,S,C,L),pe=k._incrs=k.incrs(n,x,S,C,L,oe);j=Tb(S,C,pe,L,oe)}return k._found=j}function Cl(x,S,C,L,k,j,oe,pe,Se,De){let Ie=oe%2/2;_==1&&u.translate(Ie,Ie),Ui(pe,oe,Se,De,pe),u.beginPath();let Ne,it,yt,xt,ut=k+(L==0||L==3?-j:j);C==0?(it=k,xt=ut):(Ne=k,yt=ut);for(let tt=0;tt<x.length;tt++)S[tt]!=null&&(C==0?Ne=yt=x[tt]:it=xt=x[tt],u.moveTo(Ne,it),u.lineTo(yt,xt));u.stroke(),_==1&&u.translate(-Ie,-Ie)}function gm(x){let S=!0;return v.forEach((C,L)=>{if(!C.show)return;let k=b[C.scale];if(k.min==null){C._show&&(S=!1,C._show=!1,Qs(!1));return}else C._show||(S=!1,C._show=!0,Qs(!1));let j=C.side,oe=j%2,{min:pe,max:Se}=k,[De,Ie]=mm(L,pe,Se,oe==0?te:X);if(Ie==0)return;let Ne=k.distr==2,it=C._splits=C.splits(n,L,pe,Se,De,Ie,Ne),yt=k.distr==2?it.map(We=>Le[We]):it,xt=k.distr==2?Le[it[1]]-Le[it[0]]:De,ut=C._values=C.values(n,C.filter(n,yt,L,Ie,xt),L,Ie,xt);C._rotate=j==2?C.rotate(n,ut,L,Ie):0;let tt=C._size;C._size=Jn(C.size(n,ut,L,x)),tt!=null&&C._size!=tt&&(S=!1)}),S}function _m(x){let S=!0;return W.forEach((C,L)=>{let k=C(n,L,Ii,x);k!=J[L]&&(S=!1),J[L]=k}),S}function xm(){for(let x=0;x<v.length;x++){let S=v[x];if(!S.show||!S._show)continue;let C=S.side,L=C%2,k,j,oe=S.stroke(n,x),pe=C==0||C==3?-1:1,[Se,De]=S._found;if(S.label!=null){let Tn=S.labelGap*pe,zn=tn((S._lpos+Tn)*Mt);vn(S.labelFont[0],oe,"center",C==2?wa:zd),u.save(),L==1?(k=j=0,u.translate(zn,tn(ke+He/2)),u.rotate((C==3?-qo:qo)/2)):(k=tn(Je+be/2),j=zn);let As=Ep(S.label)?S.label(n,x,Se,De):S.label;u.fillText(As,k,j),u.restore()}if(De==0)continue;let Ie=b[S.scale],Ne=L==0?be:He,it=L==0?Je:ke,yt=S._splits,xt=Ie.distr==2?yt.map(Tn=>Le[Tn]):yt,ut=Ie.distr==2?Le[yt[1]]-Le[yt[0]]:Se,tt=S.ticks,We=S.border,Nt=tt.show?tt.size:0,qt=tn(Nt*Mt),dn=tn((S.alignTo==2?S._size-Nt-S.gap:S.gap)*Mt),At=S._rotate*-qo/180,$t=p(S._pos*Mt),On=(qt+dn)*pe,En=$t+On;j=L==0?En:0,k=L==1?En:0;let $n=S.font[0],ii=S.align==1?Lr:S.align==2?gc:At>0?Lr:At<0?gc:L==0?"center":C==3?gc:Lr,yi=At||L==1?"middle":C==2?wa:zd;vn($n,oe,ii,yi);let Bn=S.font[1]*S.lineGap,Yn=yt.map(Tn=>p(o(Tn,Ie,Ne,it))),si=S._values;for(let Tn=0;Tn<si.length;Tn++){let zn=si[Tn];if(zn!=null){L==0?k=Yn[Tn]:j=Yn[Tn],zn=""+zn;let As=zn.indexOf(`
`)==-1?[zn]:zn.split(/\n/gm);for(let An=0;An<As.length;An++){let wu=As[An];At?(u.save(),u.translate(k,j+An*Bn),u.rotate(At),u.fillText(wu,0,0),u.restore()):u.fillText(wu,k,j+An*Bn)}}}tt.show&&Cl(Yn,tt.filter(n,xt,x,De,ut),L,C,$t,qt,Ct(tt.width*Mt,3),tt.stroke(n,x),tt.dash,tt.cap);let Mi=S.grid;Mi.show&&Cl(Yn,Mi.filter(n,xt,x,De,ut),L,L==0?2:1,L==0?ke:Je,L==0?He:be,Ct(Mi.width*Mt,3),Mi.stroke(n,x),Mi.dash,Mi.cap),We.show&&Cl([$t],[1],L==0?1:0,L==0?1:2,L==1?ke:Je,L==1?He:be,Ct(We.width*Mt,3),We.stroke(n,x),We.dash,We.cap)}un("drawAxes")}function Qs(x){M.forEach((S,C)=>{C>0&&(S._paths=null,x&&(s==1?(S.min=null,S.max=null):S.facets.forEach(L=>{L.min=null,L.max=null})))})}let eo=!1,Pl=!1,ha=[];function vm(){Pl=!1;for(let x=0;x<ha.length;x++)un(...ha[x]);ha.length=0}function er(){eo||(vS(au),eo=!0)}function ym(x,S=!1){eo=!0,Pl=S,x(n),au(),S&&ha.length>0&&queueMicrotask(vm)}n.batch=ym;function au(){if(B&&(_i(),B=!1),U&&(_t(),U=!1),ce){if(Ft(f,Lr,we),Ft(f,wa,_e),Ft(f,Ca,te),Ft(f,Pa,X),Ft(g,Lr,we),Ft(g,wa,_e),Ft(g,Ca,te),Ft(g,Pa,X),Ft(d,Ca,Q),Ft(d,Pa,le),h.width=tn(Q*Mt),h.height=tn(le*Mt),v.forEach(({_el:x,_show:S,_size:C,_pos:L,side:k})=>{if(x!=null)if(S){let j=k===3||k===0?C:0,oe=k%2==1;Ft(x,oe?"left":"top",L-j),Ft(x,oe?"width":"height",C),Ft(x,oe?"top":"left",oe?_e:we),Ft(x,oe?"height":"width",oe?X:te),dh(x,zs)}else Gn(x,zs)}),Be=ht=Pt=gn=mt=Ve=Yt=gt=Lt=null,Dt=1,fa(!0),we!=Re||_e!=Ze||te!=me||X!=Ae){Qs(!1);let x=te/me,S=X/Ae;if(he&&!ae&&ye.left>=0){ye.left*=x,ye.top*=S,tr&&Si(tr,tn(ye.left),0,te,X),nr&&Si(nr,0,tn(ye.top),te,X);for(let C=0;C<wn.length;C++){let L=wn[C];L!=null&&(ni[C]*=x,Di[C]*=S,Si(L,Jn(ni[C]),Jn(Di[C]),te,X))}}if(Ut.show&&!se&&Ut.left>=0&&Ut.width>0){Ut.left*=x,Ut.width*=x,Ut.top*=S,Ut.height*=S;for(let C in Fl)Ft(rr,C,Ut[C])}Re=we,Ze=_e,me=te,Ae=X}un("setSize"),ce=!1}Q>0&&le>0&&(u.clearRect(0,0,h.width,h.height),un("drawClear"),F.forEach(x=>x()),un("draw")),Ut.show&&se&&(to(Ut),se=!1),he&&ae&&(Ts(null,!0,!1),ae=!1),Te.show&&Te.live&&re&&(Ul(),re=!1),l||(l=!0,n.status=1,un("ready")),Ue=!1,eo=!1}n.redraw=(x,S)=>{U=S||!1,x!==!1?Qi(A,P.min,P.max):er()};function Ll(x,S){let C=b[x];if(C.from==null){if($==0){let L=C.range(n,S.min,S.max,x);S.min=L[0],S.max=L[1]}if(S.min>S.max){let L=S.min;S.min=S.max,S.max=L}if($>1&&S.min!=null&&S.max!=null&&S.max-S.min<1e-16)return;x==A&&C.distr==2&&$>0&&(S.min=ci(S.min,e[0]),S.max=ci(S.max,e[0]),S.min==S.max&&S.max++),q[x]=S,B=!0,er()}}n.setScale=Ll;let Dl,Il,tr,nr,ou,lu,ir,sr,cu,hu,It,Vt,Ji=!1;const _n=ye.drag;let cn=_n.x,hn=_n.y;he&&(ye.x&&(Dl=Kn(GM,g)),ye.y&&(Il=Kn(WM,g)),P.ori==0?(tr=Dl,nr=Il):(tr=Il,nr=Dl),It=ye.left,Vt=ye.top);const Ut=n.select=Jt({show:!0,over:!0,left:0,width:0,top:0,height:0},i.select),rr=Ut.show?Kn(VM,Ut.over?g:f):null;function to(x,S){if(Ut.show){for(let C in x)Ut[C]=x[C],C in Fl&&Ft(rr,C,x[C]);S!==!1&&un("setSelect")}}n.setSelect=to;function Mm(x){if(M[x].show)ie&&dh(Fe[x],zs);else if(ie&&Gn(Fe[x],zs),he){let C=Li?wn[0]:wn[x];C!=null&&Si(C,-10,-10,te,X)}}function Qi(x,S,C){Ll(x,{min:S,max:C})}function xi(x,S,C,L){S.focus!=null&&Tm(x),S.show!=null&&M.forEach((k,j)=>{j>0&&(x==j||x==null)&&(k.show=S.show,Mm(j),s==2?(Qi(k.facets[0].scale,null,null),Qi(k.facets[1].scale,null,null)):Qi(k.scale,null,null),er())}),C!==!1&&un("setSeries",x,S),L&&pa("setSeries",n,x,S)}n.setSeries=xi;function Sm(x,S){Jt(N[x],S)}function bm(x,S){x.fill=ft(x.fill||null),x.dir=vt(x.dir,-1),S=S??N.length,N.splice(S,0,x)}function wm(x){x==null?N.length=0:N.splice(x,1)}n.addBand=bm,n.setBand=Sm,n.delBand=wm;function Em(x,S){M[x].alpha=S,he&&wn[x]!=null&&(wn[x].style.opacity=S),ie&&Fe[x]&&(Fe[x].style.opacity=S)}let Ni,es,Es;const ar={focus:!0};function Tm(x){if(x!=Es){let S=x==null,C=ln.alpha!=1;M.forEach((L,k)=>{if(s==1||k>0){let j=S||k==0||k==x;L._focus=S?null:j,C&&Em(k,j?1:ln.alpha)}}),Es=x,C&&er()}}ie&&gi&&D(Gd,fe,x=>{ye._lock||(kt(x),Es!=null&&xi(null,ar,!0,Kt.setSeries))});function vi(x,S,C){let L=b[S];C&&(x=x/Mt-(L.ori==1?_e:we));let k=te;L.ori==1&&(k=X,x=k-x),L.dir==-1&&(x=k-x);let j=L._min,oe=L._max,pe=x/k,Se=j+(oe-j)*pe,De=L.distr;return De==3?Kr(10,Se):De==4?oS(Se,L.asinh):De==100?L.bwd(Se):Se}function Am(x,S){let C=vi(x,A,S);return ci(C,e[0],G,ue)}n.valToIdx=x=>ci(x,e[0]),n.posToIdx=Am,n.posToVal=vi,n.valToPos=(x,S,C)=>b[S].ori==0?r(x,b[S],C?be:te,C?Je:0):a(x,b[S],C?He:X,C?ke:0),n.setCursor=(x,S,C)=>{It=x.left,Vt=x.top,Ts(null,S,C)};function uu(x,S){Ft(rr,Lr,Ut.left=x),Ft(rr,Ca,Ut.width=S)}function du(x,S){Ft(rr,wa,Ut.top=x),Ft(rr,Pa,Ut.height=S)}let ua=P.ori==0?uu:du,da=P.ori==1?uu:du;function Rm(){if(ie&&Te.live)for(let x=s==2?1:0;x<M.length;x++){if(x==0&&dt)continue;let S=Te.values[x],C=0;for(let L in S)pt[x][C++].firstChild.nodeValue=S[L]}}function Ul(x,S){if(x!=null&&(x.idxs?x.idxs.forEach((C,L)=>{ve[L]=C}):uS(x.idx)||ve.fill(x.idx),Te.idx=ve[0]),ie&&Te.live){for(let C=0;C<M.length;C++)(C>0||s==1&&!dt)&&Cm(C,ve[C]);Rm()}re=!1,S!==!1&&un("setLegend")}n.setLegend=Ul;function Cm(x,S){let C=M[x],L=x==0&&K==2?Le:e[x],k;dt?k=C.values(n,x,S)??st:(k=C.value(n,S==null?null:L[S],x,S),k=k==null?st:{_:k}),Te.values[x]=k}function Ts(x,S,C){cu=It,hu=Vt,[It,Vt]=ye.move(n,It,Vt),ye.left=It,ye.top=Vt,he&&(tr&&Si(tr,tn(It),0,te,X),nr&&Si(nr,0,tn(Vt),te,X));let L,k=G>ue;Ni=Rt,es=null;let j=P.ori==0?te:X,oe=P.ori==1?te:X;if(It<0||$==0||k){L=ye.idx=null;for(let pe=0;pe<M.length;pe++){let Se=wn[pe];Se!=null&&Si(Se,-10,-10,te,X)}gi&&xi(null,ar,!0,x==null&&Kt.setSeries),Te.live&&(ve.fill(L),re=!0)}else{let pe,Se,De;s==1&&(pe=P.ori==0?It:Vt,Se=vi(pe,A),L=ye.idx=ci(Se,e[0],G,ue),De=H(e[0][L],P,j,0));let Ie=-10,Ne=-10,it=0,yt=0,xt=!0,ut="",tt="";for(let We=s==2?1:0;We<M.length;We++){let Nt=M[We],qt=ve[We],dn=qt==null?null:s==1?e[We][qt]:e[We][1][qt],At=ye.dataIdx(n,We,L,Se),$t=At==null?null:s==1?e[We][At]:e[We][1][At];if(re=re||$t!=dn||At!=qt,ve[We]=At,We>0&&Nt.show){let On=At==null?-10:At==L?De:H(s==1?e[0][At]:e[We][0][At],P,j,0),En=$t==null?-10:Z($t,s==1?b[Nt.scale]:b[Nt.facets[1].scale],oe,0);if(gi&&$t!=null){let $n=P.ori==1?It:Vt,ii=nn(ln.dist(n,We,At,En,$n));if(ii<Ni){let yi=ln.bias;if(yi!=0){let Bn=vi($n,Nt.scale),Yn=$t>=0?1:-1,si=Bn>=0?1:-1;si==Yn&&(si==1?yi==1?$t>=Bn:$t<=Bn:yi==1?$t<=Bn:$t>=Bn)&&(Ni=ii,es=We)}else Ni=ii,es=We}}if(re||Li){let $n,ii;P.ori==0?($n=On,ii=En):($n=En,ii=On);let yi,Bn,Yn,si,Mi,Tn,zn=!0,As=Ht.bbox;if(As!=null){zn=!1;let An=As(n,We);Yn=An.left,si=An.top,yi=An.width,Bn=An.height}else Yn=$n,si=ii,yi=Bn=Ht.size(n,We);if(Tn=Ht.fill(n,We),Mi=Ht.stroke(n,We),Li)We==es&&Ni<=ln.prox&&(Ie=Yn,Ne=si,it=yi,yt=Bn,xt=zn,ut=Tn,tt=Mi);else{let An=wn[We];An!=null&&(ni[We]=Yn,Di[We]=si,Kd(An,yi,Bn,zn),Yd(An,Tn,Mi),Si(An,Jn(Yn),Jn(si),te,X))}}}}if(Li){let We=ln.prox,Nt=Es==null?Ni<=We:Ni>We||es!=Es;if(re||Nt){let qt=wn[0];qt!=null&&(ni[0]=Ie,Di[0]=Ne,Kd(qt,it,yt,xt),Yd(qt,ut,tt),Si(qt,Jn(Ie),Jn(Ne),te,X))}}}if(Ut.show&&Ji)if(x!=null){let[pe,Se]=Kt.scales,[De,Ie]=Kt.match,[Ne,it]=x.cursor.sync.scales,yt=x.cursor.drag;if(cn=yt._x,hn=yt._y,cn||hn){let{left:xt,top:ut,width:tt,height:We}=x.select,Nt=x.scales[Ne].ori,qt=x.posToVal,dn,At,$t,On,En,$n=pe!=null&&De(pe,Ne),ii=Se!=null&&Ie(Se,it);$n&&cn?(Nt==0?(dn=xt,At=tt):(dn=ut,At=We),$t=b[pe],On=H(qt(dn,Ne),$t,j,0),En=H(qt(dn+At,Ne),$t,j,0),ua(di(On,En),nn(En-On))):ua(0,j),ii&&hn?(Nt==1?(dn=xt,At=tt):(dn=ut,At=We),$t=b[Se],On=Z(qt(dn,it),$t,oe,0),En=Z(qt(dn+At,it),$t,oe,0),da(di(On,En),nn(En-On))):da(0,oe)}else Ol()}else{let pe=nn(cu-ou),Se=nn(hu-lu);if(P.ori==1){let it=pe;pe=Se,Se=it}cn=_n.x&&pe>=_n.dist,hn=_n.y&&Se>=_n.dist;let De=_n.uni;De!=null?cn&&hn&&(cn=pe>=De,hn=Se>=De,!cn&&!hn&&(Se>pe?hn=!0:cn=!0)):_n.x&&_n.y&&(cn||hn)&&(cn=hn=!0);let Ie,Ne;cn&&(P.ori==0?(Ie=ir,Ne=It):(Ie=sr,Ne=Vt),ua(di(Ie,Ne),nn(Ne-Ie)),hn||da(0,oe)),hn&&(P.ori==1?(Ie=ir,Ne=It):(Ie=sr,Ne=Vt),da(di(Ie,Ne),nn(Ne-Ie)),cn||ua(0,j)),!cn&&!hn&&(ua(0,0),da(0,0))}if(_n._x=cn,_n._y=hn,x==null){if(C){if(bu!=null){let[pe,Se]=Kt.scales;Kt.values[0]=pe!=null?vi(P.ori==0?It:Vt,pe):null,Kt.values[1]=Se!=null?vi(P.ori==1?It:Vt,Se):null}pa(_c,n,It,Vt,te,X,L)}if(gi){let pe=C&&Kt.setSeries,Se=ln.prox;Es==null?Ni<=Se&&xi(es,ar,!0,pe):Ni>Se?xi(null,ar,!0,pe):es!=Es&&xi(es,ar,!0,pe)}}re&&(Te.idx=L,Ul()),S!==!1&&un("setCursor")}let ts=null;Object.defineProperty(n,"rect",{get(){return ts==null&&fa(!1),ts}});function fa(x=!1){x?ts=null:(ts=g.getBoundingClientRect(),un("syncRect",ts))}function fu(x,S,C,L,k,j,oe){ye._lock||Ji&&x!=null&&x.movementX==0&&x.movementY==0||(Nl(x,S,C,L,k,j,oe,!1,x!=null),x!=null?Ts(null,!0,!0):Ts(S,!0,!1))}function Nl(x,S,C,L,k,j,oe,pe,Se){if(ts==null&&fa(!1),kt(x),x!=null)C=x.clientX-ts.left,L=x.clientY-ts.top;else{if(C<0||L<0){It=-10,Vt=-10;return}let[De,Ie]=Kt.scales,Ne=S.cursor.sync,[it,yt]=Ne.values,[xt,ut]=Ne.scales,[tt,We]=Kt.match,Nt=S.axes[0].side%2==1,qt=P.ori==0?te:X,dn=P.ori==1?te:X,At=Nt?j:k,$t=Nt?k:j,On=Nt?L:C,En=Nt?C:L;if(xt!=null?C=tt(De,xt)?o(it,b[De],qt,0):-10:C=qt*(On/At),ut!=null?L=We(Ie,ut)?o(yt,b[Ie],dn,0):-10:L=dn*(En/$t),P.ori==1){let $n=C;C=L,L=$n}}Se&&(S==null||S.cursor.event.type==_c)&&((C<=1||C>=te-1)&&(C=Ns(C,te)),(L<=1||L>=X-1)&&(L=Ns(L,X))),pe?(ou=C,lu=L,[ir,sr]=ye.move(n,C,L)):(It=C,Vt=L)}const Fl={width:0,height:0,left:0,top:0};function Ol(){to(Fl,!1)}let pu,mu,gu,_u;function xu(x,S,C,L,k,j,oe){Ji=!0,cn=hn=_n._x=_n._y=!1,Nl(x,S,C,L,k,j,oe,!0,!1),x!=null&&(D(xc,hh,vu,!1),pa(Hd,n,ir,sr,te,X,null));let{left:pe,top:Se,width:De,height:Ie}=Ut;pu=pe,mu=Se,gu=De,_u=Ie}function vu(x,S,C,L,k,j,oe){Ji=_n._x=_n._y=!1,Nl(x,S,C,L,k,j,oe,!1,!0);let{left:pe,top:Se,width:De,height:Ie}=Ut,Ne=De>0||Ie>0,it=pu!=pe||mu!=Se||gu!=De||_u!=Ie;if(Ne&&it&&to(Ut),_n.setScale&&Ne&&it){let yt=pe,xt=De,ut=Se,tt=Ie;if(P.ori==1&&(yt=Se,xt=Ie,ut=pe,tt=De),cn&&Qi(A,vi(yt,A),vi(yt+xt,A)),hn)for(let We in b){let Nt=b[We];We!=A&&Nt.from==null&&Nt.min!=Rt&&Qi(We,vi(ut+tt,We),vi(ut,We))}Ol()}else ye.lock&&(ye._lock=!ye._lock,Ts(S,!0,x!=null));x!=null&&(E(xc,hh),pa(xc,n,It,Vt,te,X,null))}function Pm(x,S,C,L,k,j,oe){if(ye._lock)return;kt(x);let pe=Ji;if(Ji){let Se=!0,De=!0,Ie=10,Ne,it;P.ori==0?(Ne=cn,it=hn):(Ne=hn,it=cn),Ne&&it&&(Se=It<=Ie||It>=te-Ie,De=Vt<=Ie||Vt>=X-Ie),Ne&&Se&&(It=It<ir?0:te),it&&De&&(Vt=Vt<sr?0:X),Ts(null,!0,!0),Ji=!1}It=-10,Vt=-10,ve.fill(null),Ts(null,!0,!0),pe&&(Ji=pe)}function yu(x,S,C,L,k,j,oe){ye._lock||(kt(x),et(),Ol(),x!=null&&pa(Wd,n,It,Vt,te,X,null))}function Mu(){v.forEach(Ab),xe(n.width,n.height,!0)}Xs(rl,Gr,Mu);const or={};or.mousedown=xu,or.mousemove=fu,or.mouseup=vu,or.dblclick=yu,or.setSeries=(x,S,C,L)=>{let k=Kt.match[2];C=k(n,S,C),C!=-1&&xi(C,L,!0,!1)},he&&(D(Hd,g,xu),D(_c,g,fu),D(Vd,g,x=>{kt(x),fa(!1)}),D(Gd,g,Pm),D(Wd,g,yu),xh.add(n),n.syncRect=fa);const no=n.hooks=i.hooks||{};function un(x,S,C){Pl?ha.push([x,S,C]):x in no&&no[x].forEach(L=>{L.call(null,n,S,C)})}(i.plugins||[]).forEach(x=>{for(let S in x.hooks)no[S]=(no[S]||[]).concat(x.hooks[S])});const Su=(x,S,C)=>C,Kt=Jt({key:null,setSeries:!1,filters:{pub:tf,sub:tf},scales:[A,M[1]?M[1].scale:null],match:[nf,nf,Su],values:[null,null]},ye.sync);Kt.match.length==2&&Kt.match.push(Su),ye.sync=Kt;const bu=Kt.key,Bl=jp(bu);function pa(x,S,C,L,k,j,oe){Kt.filters.pub(x,S,C,L,k,j,oe)&&Bl.pub(x,S,C,L,k,j,oe)}Bl.sub(n);function Lm(x,S,C,L,k,j,oe){Kt.filters.sub(x,S,C,L,k,j,oe)&&or[x](null,S,C,L,k,j,oe)}n.pub=Lm;function Dm(){Bl.unsub(n),xh.delete(n),qe.clear(),fh(rl,Gr,Mu),c.remove(),fe==null||fe.remove(),un("destroy")}n.destroy=Dm;function zl(){un("init",i,e),Qe(e||i.data,!1),q[A]?Ll(A,q[A]):et(),se=Ut.show&&(Ut.width>0||Ut.height>0),ae=re=!0,xe(i.width,i.height)}return M.forEach(la),v.forEach(Al),t?t instanceof HTMLElement?(t.appendChild(c),zl()):t(n,zl):zl(),n}pn.assign=Jt;pn.fmtNum=Xh;pn.rangeNum=al;pn.rangeLog=pl;pn.rangeAsinh=Gh;pn.orient=Zs;pn.pxRatio=Mt;pn.join=xS;pn.fmtDate=$h,pn.tzDate=CS;pn.sync=jp;{pn.addGap=ub,pn.clipGaps=_l;let i=pn.paths={points:tm};i.linear=im,i.stepped=pb,i.bars=mb,i.spline=_b}function bc(i){return Math.max(120,i.clientHeight-30)}class Rb{constructor(){I(this,"name","Plotter");I(this,"container",null);I(this,"tabsContainer",null);I(this,"contentContainer",null);I(this,"tooltip",null);I(this,"paretoPlot",null);I(this,"ablationPlot",null);I(this,"variabilityPlot",null);I(this,"currentTab","pareto");I(this,"records",[]);I(this,"ablationGroups",[]);I(this,"paretoFlags",[]);I(this,"chance",.1);I(this,"paretoRecordIndices",[]);I(this,"paretoXData",[]);I(this,"paretoYData",[]);I(this,"categoryLabels",[]);I(this,"ablationFixedAxes","");I(this,"onCampaignMetrics",e=>{const{data:t}=e;t!=null&&t.records&&Zn.observe(e==null?void 0:e.campaign_id,t)});I(this,"onRunChanged",(e,t)=>{t&&(this.records=t.records??[],this.paretoFlags=t.pareto??[],this.ablationGroups=t.ablation_groups??[],typeof t.chance=="number"&&(this.chance=t.chance),this.updatePlots(),this.updateStatus())});jt.register("campaign_metrics",this.onCampaignMetrics),Zn.onChange(this.onRunChanged)}async init(){this.createUI(),console.log("[Plotter] Initialized")}async destroy(){var e,t,n,s;jt.unregister("campaign_metrics",this.onCampaignMetrics),(e=this.paretoPlot)==null||e.destroy(),(t=this.ablationPlot)==null||t.destroy(),(n=this.variabilityPlot)==null||n.destroy(),(s=this.container)==null||s.remove()}createUI(){const e=document.getElementById("ui-overlay");e&&(this.container=document.createElement("div"),this.container.id="plotter",this.container.style.cssText=`
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
    `,this.container.appendChild(this.tooltip),this.tabsContainer.querySelectorAll(".plotter-tab").forEach(t=>{t.addEventListener("click",()=>this.switchTab(t.getAttribute("data-tab")))}),this.container.querySelector("#plotter-download").addEventListener("click",()=>this.downloadCurrent()),this.switchTab(this.currentTab))}showTab(e){e!==this.currentTab&&this.switchTab(e)}switchTab(e){this.currentTab=e,this.tabsContainer.querySelectorAll(".plotter-tab").forEach(n=>{n.classList.toggle("active",n.getAttribute("data-tab")===e)}),Object.entries({pareto:"plotter-pareto",ablation:"plotter-ablation",variability:"plotter-variability"}).forEach(([n,s])=>{const r=document.getElementById(s);r&&(r.style.display=n===e?"block":"none")}),e==="pareto"&&!this.paretoPlot&&this.initParetoPlot(),e==="ablation"&&!this.ablationPlot&&this.initAblationPlot(),e==="variability"&&!this.variabilityPlot&&this.initVariabilityPlot(),this.updatePlots()}updateStatus(){var s;const e=(s=this.container)==null?void 0:s.querySelector("#plotter-status");if(!e)return;const t=`${this.records.length} records | ${this.paretoFlags.filter(r=>r).length} Pareto`,n=this.ablationFixedAxes?` | fixed: ${this.ablationFixedAxes}`:"";e.textContent=t+n,e.title=e.textContent}updatePlots(){this.currentTab==="pareto"&&this.paretoPlot&&this.updateParetoPlot(),this.currentTab==="ablation"&&this.ablationPlot&&this.updateAblationPlot(),this.currentTab==="variability"&&this.variabilityPlot&&this.updateVariabilityPlot()}initParetoPlot(){const e=document.getElementById("plotter-pareto");if(!e)return;const t={width:e.clientWidth,height:bc(e),title:"Pareto Frontier: validation accuracy vs speed",axes:[{label:"1 / walltime_s   (faster →)",grid:{stroke:z.border}},{label:"accuracy",grid:{stroke:z.border},side:1}],scales:{x:{time:!1},y:{time:!1}},series:[{},{label:"val_acc",stroke:z.gradient,width:0,points:{show:!0,size:8,stroke:"white",width:1,fill:(n,s)=>{var o;const r=this.paretoRecordIndices[s],a=r===void 0?void 0:this.records[r];return a&&Xt[(o=a.coordinate)==null?void 0:o.credit]||z.gradient}}}],hooks:{draw:[n=>{const s=n.ctx;if(this.paretoFlags.some(a=>a)){const a=[];this.records.forEach((o,l)=>{this.paretoFlags[l]&&o.payload.walltime_s&&o.payload.val_acc&&a.push([1/o.payload.walltime_s,o.payload.val_acc])}),a.sort((o,l)=>o[0]-l[0]),a.length>1&&(s.beginPath(),s.strokeStyle=z.pareto,s.lineWidth=2,s.setLineDash([5,5]),a.forEach((o,l)=>{const c=n.valToPos(o[0],"x"),h=n.valToPos(o[1],"y");l===0?s.moveTo(c,h):s.lineTo(c,h)}),s.stroke(),s.setLineDash([])),a.forEach(o=>{const l=n.valToPos(o[0],"x"),c=n.valToPos(o[1],"y");s.beginPath(),s.arc(l,c,7,0,Math.PI*2),s.strokeStyle=z.pareto,s.lineWidth=1.5,s.stroke()})}const r=n.valToPos(this.chance,"y");s.strokeStyle=z.chance_line,s.lineWidth=1.5,s.setLineDash([4,4]),s.beginPath(),s.moveTo(n.bbox.left,r),s.lineTo(n.bbox.width,r),s.stroke(),s.setLineDash([])}],setCursor:[n=>{this.showScatterTooltip(n)}]},cursor:{show:!0,drag:{setScale:!0},focus:{prox:16}}};this.paretoPlot=new pn(t,[[],[]],e)}recordAt(e){const t=this.paretoRecordIndices[e];return t===void 0?void 0:this.records[t]}updateParetoPlot(){if(!this.paretoPlot||this.records.length===0)return;const e=[],t=[];this.paretoRecordIndices=[],this.records.forEach((r,a)=>{const o=r.payload.walltime_s,l=r.payload.val_acc;this.paretoRecordIndices.push(a),o&&l?(e.push(1/o),t.push(l)):(e.push(NaN),t.push(NaN))}),this.paretoPlot.setData([e,t]),this.paretoXData=e,this.paretoYData=t;const n=e.filter(Number.isFinite),s=t.filter(Number.isFinite);n.length>0&&this.fitScale(this.paretoPlot,"x",Math.min(...n),Math.max(...n)),s.length>0&&this.fitScale(this.paretoPlot,"y",Math.min(Math.min(...s),this.chance),Math.max(...s))}fitScale(e,t,n,s){if(!Number.isFinite(n)||!Number.isFinite(s))return;n===s&&(n-=.01,s+=.01);const r=(s-n)*.05;e.setScale(t,{min:n-r,max:s+r})}initAblationPlot(){const e=document.getElementById("plotter-ablation");if(!e)return;const t={width:e.clientWidth,height:bc(e),title:"Ablation: credit arm → validation accuracy",axes:[{label:"credit arm",splits:()=>this.categoryIndices(),values:(n,s)=>s.map(r=>this.categoryLabels[r]??String(r)),grid:{stroke:z.border}},{label:"accuracy",grid:{stroke:z.border},side:1}],scales:{x:{time:!1},y:{time:!1}},series:[{},{label:"val_acc",width:0,points:{show:!1}}],hooks:{draw:[n=>{if(!this.ablationGroups.length)return;const s=n.ctx,r=this.ablationGroups.find(h=>h.axis==="credit");if(!r)return;const a=r.metrics.find(h=>h.metric==="val_acc");if(!a)return;const o=a.arms,l=n.bbox.width/(o.length*1.5);n.bbox.left,o.forEach((h,u)=>{const d=n.valToPos(u,"x"),f=n.valToPos(0,"y"),g=n.valToPos(h.mean,"y"),_=f-g;if(s.fillStyle=Xt[h.value]||z.gradient,s.fillRect(d-l/2,g,l,_),h.std>0){const p=n.valToPos(h.mean+h.std,"y");s.strokeStyle=z.text_muted,s.lineWidth=1,s.beginPath(),s.moveTo(d,p),s.lineTo(d,f),s.stroke(),s.moveTo(d-3,p),s.lineTo(d+3,p),s.stroke()}});const c=n.valToPos(this.chance,"y");s.strokeStyle=z.chance_line,s.lineWidth=2,s.setLineDash([5,5]),s.beginPath(),s.moveTo(n.bbox.left,c),s.lineTo(n.bbox.width,c),s.stroke(),s.setLineDash([])}],setCursor:[n=>{this.showCategoryTooltip(n,"ablation")}]},cursor:{show:!0,drag:{setScale:!0}}};this.ablationPlot=new pn(t,[[],[]],e)}updateAblationPlot(){if(!this.ablationPlot||!this.ablationGroups.length)return;const e=this.ablationGroups.find(o=>o.axis==="credit");if(!e)return;const t=e.metrics.find(o=>o.metric==="val_acc");if(!t)return;const n=t.arms.map((o,l)=>l),s=t.arms.map(o=>o.mean);this.categoryLabels=t.arms.map(o=>o.value),this.ablationFixedAxes=e.fixed_axes.split(",").map(o=>o.split("=").pop()??o).join(", "),this.ablationPlot.setData([n,s]),this.fitScale(this.ablationPlot,"x",-.5,Math.max(n.length-.5,.5));const r=t.arms.flatMap(o=>[o.mean-o.std,o.mean+o.std]);r.length>0&&this.fitScale(this.ablationPlot,"y",Math.min(Math.min(...r),this.chance),Math.max(...r));const a=this.ablationPlot.root.querySelector(".u-title");a&&(a.textContent=`Ablation: ${e.axis} vs val_acc`)}initVariabilityPlot(){const e=document.getElementById("plotter-variability");if(!e)return;const t={width:e.clientWidth,height:bc(e),title:"Seed variability: validation accuracy per arm",axes:[{label:"credit arm",splits:()=>this.categoryIndices(),values:(n,s)=>s.map(r=>this.categoryLabels[r]??String(r)),grid:{stroke:z.border}},{label:"accuracy",grid:{stroke:z.border},side:1}],scales:{x:{time:!1},y:{time:!1}},series:[{},{label:"val_acc",width:0,points:{show:!1}}],hooks:{draw:[n=>{if(!this.records.length)return;const s=n.ctx,r={};this.records.forEach(c=>{const h=c.coordinate.credit,u=c.payload.val_acc;u!==void 0&&(r[h]||(r[h]=[])).push(u)});const a=Object.keys(r).sort(),o=n.bbox.width/(a.length*2);a.forEach((c,h)=>{const u=r[c].sort((y,P)=>y-P),d=u.length;if(d===0)return;const f=u[Math.floor(d*.25)],g=u[Math.floor(d*.5)],_=u[Math.floor(d*.75)],p=_-f,m=Math.max(u[0],f-1.5*p),M=Math.min(u[d-1],_+1.5*p),v=n.valToPos(h,"x"),b=n.valToPos(m,"y"),N=n.valToPos(f,"y"),A=n.valToPos(g,"y"),R=n.valToPos(_,"y"),F=n.valToPos(M,"y"),w=Xt[c]||z.gradient;s.strokeStyle=w,s.lineWidth=1.5,s.beginPath(),s.moveTo(v,b),s.lineTo(v,N),s.moveTo(v,R),s.lineTo(v,F),s.stroke(),s.fillStyle=w+"44",s.strokeStyle=w,s.lineWidth=1.5,s.fillRect(v-o/2,R,o,N-R),s.strokeRect(v-o/2,R,o,N-R),s.strokeStyle="white",s.lineWidth=2,s.beginPath(),s.moveTo(v-o/2,A),s.lineTo(v+o/2,A),s.stroke(),u.forEach(y=>{if(y<m||y>M){const P=n.valToPos(y,"y");s.fillStyle=w,s.beginPath(),s.arc(v,P,2,0,Math.PI*2),s.fill()}})});const l=n.valToPos(this.chance,"y");s.strokeStyle=z.chance_line,s.lineWidth=2,s.setLineDash([5,5]),s.beginPath(),s.moveTo(n.bbox.left,l),s.lineTo(n.bbox.width,l),s.stroke(),s.setLineDash([])}],setCursor:[n=>{this.showCategoryTooltip(n,"variability")}]},cursor:{show:!0,drag:{setScale:!0}}};this.variabilityPlot=new pn(t,[[],[]],e)}updateVariabilityPlot(){if(!this.variabilityPlot||!this.records.length)return;const e=Array.from(new Set(this.records.map(r=>r.coordinate.credit))).sort(),t=e.map((r,a)=>a),n=e.map(()=>0);this.categoryLabels=e,this.variabilityPlot.setData([t,n]),this.fitScale(this.variabilityPlot,"x",-.5,Math.max(e.length-.5,.5));const s=this.records.map(r=>r.payload.val_acc).filter(r=>typeof r=="number");s.length>0&&this.fitScale(this.variabilityPlot,"y",Math.min(Math.min(...s),this.chance),Math.max(...s))}categoryIndices(){return this.categoryLabels.map((e,t)=>t)}showTooltip(e,t){if(!this.tooltip||!this.container)return;const n=e.cursor;if(!n||n.left==null||n.top==null){this.hideTooltip();return}const s=e.ctx.canvas.getBoundingClientRect(),r=this.container.getBoundingClientRect();this.tooltip.innerHTML=t,this.tooltip.style.display="block",this.tooltip.style.left=`${s.left-r.left+e.bbox.left+n.left+14}px`,this.tooltip.style.top=`${s.top-r.top+e.bbox.top+n.top+14}px`}hideTooltip(){this.tooltip&&(this.tooltip.style.display="none")}showScatterTooltip(e){var d,f;const t=e.cursor;if(!t||t.left==null||t.top==null){this.hideTooltip();return}let n=-1,s=1/0;if(this.paretoXData.forEach((g,_)=>{const p=this.paretoYData[_];if(!Number.isFinite(g)||!Number.isFinite(p))return;const m=e.valToPos(g,"x"),M=e.valToPos(p,"y");if(!Number.isFinite(m)||!Number.isFinite(M))return;const v=(m-t.left)**2+(M-t.top)**2;v<s&&(s=v,n=_)}),n<0||s>400){this.hideTooltip();return}const r=this.recordAt(n);if(!r){this.hideTooltip();return}const a=this.paretoRecordIndices[n],o=((d=r.coordinate)==null?void 0:d.credit)??"?",l=r.payload.val_acc??0,c=r.payload.walltime_s??0,h=((f=r.schedule)==null?void 0:f.seed)??"?",u=this.paretoFlags[a]?" · PARETO":"";this.showTooltip(e,`${o} · val_acc ${l.toFixed(3)} · ${c.toFixed(1)}s · seed ${h}${u}`)}showCategoryTooltip(e,t){const n=e.cursor;if(!n||n.left==null||n.top==null){this.hideTooltip();return}const s=Math.round(e.posToVal(n.left,"x"));if(s<0||s>=this.categoryLabels.length){this.hideTooltip();return}const r=this.categoryLabels[s];if(t==="ablation"){const h=this.ablationGroups.find(f=>f.axis==="credit"),u=h==null?void 0:h.metrics.find(f=>f.metric==="val_acc"),d=u==null?void 0:u.arms[s];if(!d){this.hideTooltip();return}this.showTooltip(e,`${r} · ${d.mean.toFixed(3)} ± ${d.std.toFixed(3)} (n=${d.count})${d.at_chance?" · at chance":""}`);return}const a=this.records.filter(h=>h.coordinate.credit===r).map(h=>h.payload.val_acc).filter(h=>typeof h=="number").sort((h,u)=>h-u);if(a.length===0){this.hideTooltip();return}const o=a[Math.floor(a.length*.5)],l=a[Math.floor(a.length*.25)],c=a[Math.floor(a.length*.75)];this.showTooltip(e,`${r} · median ${o.toFixed(3)} · IQR ${(c-l).toFixed(3)} · n=${a.length}`)}downloadCurrent(){const t={pareto:this.paretoPlot,ablation:this.ablationPlot,variability:this.variabilityPlot}[this.currentTab];if(!t)return;const n=document.createElement("a");n.download=`computronium-${this.currentTab}-${Date.now()}.png`,n.href=this.exportImage(t),n.click()}exportImage(e){const t=Array.from(e.root.querySelectorAll("canvas")),n=e.root.getBoundingClientRect(),s=Math.max(...t.map(l=>l.width),1),r=Math.max(...t.map(l=>l.height),1),a=document.createElement("canvas");a.width=s,a.height=r;const o=a.getContext("2d");return o?(o.fillStyle=z.bg,o.fillRect(0,0,s,r),t.forEach(l=>{const c=l.getBoundingClientRect();if(c.width===0||c.height===0)return;const h=l.width/c.width;o.drawImage(l,(c.left-n.left)*h,(c.top-n.top)*h,l.width,l.height)}),a.toDataURL("image/png")):e.ctx.canvas.toDataURL("image/png")}}const eu=new Rb;Ki.register(eu);class Cb{constructor(){I(this,"name","LiveRail");I(this,"container",null);I(this,"logContainer",null);I(this,"events",[]);I(this,"maxEvents",50);I(this,"onPipelineEvent",e=>{this.events.unshift(e),this.events.length>this.maxEvents&&this.events.pop(),this.render()});I(this,"onStatusUpdate",e=>{var r,a,o;const t=((r=e==null?void 0:e.data)==null?void 0:r.running_campaigns)??0,n=((a=e==null?void 0:e.data)==null?void 0:a.queued_campaigns)??0,s=(o=this.container)==null?void 0:o.querySelector("#rail-queue");s&&(s.textContent=`${t} running · ${n} queued`)});jt.register("pipeline_event",this.onPipelineEvent),jt.register("status_update",this.onStatusUpdate)}async init(){this.createUI(),jr.onStateChange(e=>this.setConnected(e==="connected")),console.log("[LiveRail] Initialized")}async destroy(){var e;jt.unregister("pipeline_event",this.onPipelineEvent),jt.unregister("status_update",this.onStatusUpdate),(e=this.container)==null||e.remove()}createUI(){const e=document.getElementById("ui-overlay");e&&(this.container=document.createElement("div"),this.container.id="live-rail",this.container.style.cssText=`
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
    `,e.appendChild(this.container),this.logContainer=this.container.querySelector("#rail-log"))}toggle(){this.container&&(this.container.style.display=this.container.style.display==="none"?"":"none")}setConnected(e){var a;const t=(a=this.container)==null?void 0:a.querySelector("#rail-connection");if(!t)return;const n=t.querySelector(".dot"),s=t.querySelector(".rail-label");if(!n||!s)return;const r=e?z.ok:z.error;n.style.background=r,t.style.background=r+"22",t.style.borderColor=r+"88",t.style.color=r,s.textContent=e?"Connected":"Disconnected"}render(){var t;if(!this.logContainer)return;this.logContainer.innerHTML=this.events.map(n=>{const s=new Date(n.timestamp).toLocaleTimeString(),a={ok:z.ok,warn:z.warn,error:z.error}[n.level]||z.text_secondary,o=n.level==="ok"?"✓":n.level==="warn"?"⚠":"✗";return`
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
        `}).join("");const e=(t=this.container)==null?void 0:t.querySelector("#rail-count");e&&(e.textContent=`${this.events.length} events`),this.logContainer.scrollLeft=0}}const tu=new Cb;Ki.register(tu);const Pb=4e3,Lb={ok:z.text_primary,warn:z.warn,error:z.error};class Db{constructor(){I(this,"name","Caption");I(this,"container",null);I(this,"headline",null);I(this,"context",null);I(this,"state",[]);I(this,"spoken",null);I(this,"last",null);I(this,"holdTimer",null);I(this,"onNarration",e=>{this.state=(e==null?void 0:e.state)??[],this.render()});I(this,"onEvent",e=>{e!=null&&e.sentence&&this.say(e.sentence,e.level??"ok")});jt.register("narration",this.onNarration),jt.register("pipeline_event",this.onEvent)}async init(){this.createUI(),this.render()}async destroy(){var e;jt.unregister("narration",this.onNarration),jt.unregister("pipeline_event",this.onEvent),this.holdTimer!==null&&window.clearTimeout(this.holdTimer),(e=this.container)==null||e.remove()}toggle(){this.container&&(this.container.style.display=this.container.style.display==="none"?"":"none")}say(e,t="ok"){e&&(this.spoken={text:e,level:t},this.last={text:e,level:t},this.render(),this.holdTimer!==null&&window.clearTimeout(this.holdTimer),this.holdTimer=window.setTimeout(()=>{this.spoken=null,this.holdTimer=null,this.render()},Pb))}createUI(){const e=document.getElementById("ui-overlay");e&&(this.container=document.createElement("div"),this.container.id="caption",this.container.style.cssText=`
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
    `,e.appendChild(this.container),this.headline=this.container.querySelector("#caption-headline"),this.context=this.container.querySelector("#caption-context"))}render(){if(!(!this.headline||!this.context)){if(this.spoken){this.headline.textContent=this.spoken.text,this.headline.style.color=this.colorOf(this.spoken.level),this.context.textContent=this.state.join(" ");return}if(this.state.length>0){this.headline.textContent=this.state[0],this.headline.style.color=z.text_primary,this.context.textContent=this.state.slice(1).join(" ");return}if(this.last){this.headline.textContent=this.last.text,this.headline.style.color=this.colorOf(this.last.level),this.context.textContent="";return}this.headline.textContent="The dashboard is starting.",this.headline.style.color=z.text_primary,this.context.textContent=""}}colorOf(e){return Lb[e]??z.text_primary}}const nu=new Db;Ki.register(nu);class Ib{constructor(){I(this,"name","HUD");I(this,"panel",null);I(this,"modeChip",null);I(this,"connectionPill",null);I(this,"rows",new Map);I(this,"rowElements",new Map);I(this,"claimValue",null);I(this,"sourceValue",null);I(this,"statusData",{});I(this,"resources",{});I(this,"requiredSeeds",0);I(this,"measuredSeeds",0);I(this,"connected",!1);I(this,"animationTime",0);I(this,"onStatusUpdate",e=>{const t=(e==null?void 0:e.data)??e;t&&(this.statusData=t,this.updateQueueRows())});I(this,"onCampaignMetrics",e=>{const t=e==null?void 0:e.data;t&&Zn.observe(e==null?void 0:e.campaign_id,t)});I(this,"onRunChanged",(e,t)=>{var n;t&&(this.resources=t.resources??{},typeof t.required_seeds=="number"&&(this.requiredSeeds=t.required_seeds),this.measuredSeeds=this.resources.seeds_per_arm??((n=t.records)==null?void 0:n.length)??0,this.updateModeChip(t.run),this.updateSource(t.store),this.updateResourceRows(),this.updateClaim())});jt.register("status_update",this.onStatusUpdate),jt.register("campaign_metrics",this.onCampaignMetrics),Zn.onChange(this.onRunChanged)}async init(){this.createPanel(),this.createModeChip(),jr.onStateChange(e=>{this.connected=e==="connected",this.updateConnection()}),console.log("[HUD] Initialized")}async destroy(){var e,t;jt.unregister("status_update",this.onStatusUpdate),jt.unregister("campaign_metrics",this.onCampaignMetrics),(e=this.panel)==null||e.remove(),(t=this.modeChip)==null||t.remove()}createPanel(){const e=document.getElementById("ui-overlay");if(!e)return;this.panel=document.createElement("div"),this.panel.id="hud",this.panel.style.cssText=`
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
        <span id="hud-source" style="font-weight: 600; color: ${z.text_secondary};">—</span>
      </div>
      <div style="margin-top: 12px; padding-top: 10px; border-top: 1px solid var(--border); display: flex; justify-content: space-between; align-items: baseline;">
        <span style="color: var(--text-secondary);">SEEDS TO CLAIM</span>
        <span id="hud-claim" style="font-weight: 700; color: ${z.insufficient};">—</span>
      </div>
    `,e.appendChild(this.panel);const t=this.panel.querySelector("#hud-meters");this.addMeter(t,"device","DEVICE",z.gradient),this.addMeter(t,"memory","MEMORY",z.memory),this.addMeter(t,"walltime","WALLTIME",z.cpu),this.addMeter(t,"gpu","GPU",z.gpu),this.addMeter(t,"cpu","CPU",z.cpu),this.addMeter(t,"records","RECORDS",z.promoted),this.claimValue=this.panel.querySelector("#hud-claim"),this.connectionPill=this.panel.querySelector("#hud-connection"),this.sourceValue=this.panel.querySelector("#hud-source")}addMeter(e,t,n,s){const r=document.createElement("div");r.style.cssText="display: flex; flex-direction: column; gap: 3px;",r.innerHTML=`
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
      background: ${z.text_muted}22;
      border: 1px solid ${z.text_muted}88;
      color: ${z.text_muted};
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
    `,e.appendChild(this.modeChip))}updateModeChip(e){if(!this.modeChip)return;const t=(e==null?void 0:e.mode)??"NO RUN",n=t==="PREREGISTERED"?z.passed:t==="EXPLORATORY"?z.insufficient:z.text_muted;this.modeChip.style.background=`${n}22`,this.modeChip.style.borderColor=`${n}88`,this.modeChip.style.color=n;const s=this.modeChip.querySelector(".mode-label");s&&(s.textContent=t);const r=this.modeChip.querySelector(".mode-detail");r&&(r.textContent=[e==null?void 0:e.profile,((e==null?void 0:e.tasks)??[]).join(", "),e==null?void 0:e.fidelity].filter(Boolean).join(" · ")),this.modeChip.title=e?`run ${e.run_id??"?"} · objectives: ${(e.objectives??[]).join(", ")||"none"}`:"No run has reported yet"}setMeter(e,t,n){const s=this.rows.get(e),r=this.rowElements.get(e);!s||!r||(s.value=t,s.fraction=Math.max(0,Math.min(1,n)),r.value.textContent=t,r.fill.style.width=`${(s.fraction*100).toFixed(1)}%`)}updateSource(e){if(!this.sourceValue)return;const t=e==null?void 0:e.source;if(!t){this.sourceValue.textContent="—",this.sourceValue.style.color=z.text_secondary;return}if(t==="snapshot"){const n=e!=null&&e.published_at?new Date(e.published_at).toLocaleTimeString():"";this.sourceValue.textContent=n?`snapshot ${n}`:"snapshot",this.sourceValue.style.color=z.insufficient,this.sourceValue.title="The writer published this copy; it is as fresh as its last publish.";return}this.sourceValue.textContent="live",this.sourceValue.style.color=z.passed,this.sourceValue.title="The store itself, read as it is written."}updateQueueRows(){const e=this.statusData;this.setMeter("gpu",e.max_gpus?`${e.used_gpus??0} / ${e.max_gpus}`:"—",e.max_gpus?(e.used_gpus??0)/e.max_gpus:0),this.setMeter("cpu",e.max_cpus?`${e.used_cpus??0} / ${e.max_cpus}`:"—",e.max_cpus?(e.used_cpus??0)/e.max_cpus:0)}updateResourceRows(){const e=this.resources;this.setMeter("device",e.device??"—",e.device?1:0),this.setMeter("memory",e.memory_mb!==void 0?`${e.memory_mb.toFixed(1)} MB`:"—",e.memory_mb!==void 0?Math.min(1,e.memory_mb/2048):0),this.setMeter("walltime",e.walltime_s!==void 0?`${e.walltime_s.toFixed(1)} s`:"—",e.walltime_s!==void 0?Math.min(1,e.walltime_s/120):0),this.setMeter("records",e.records!==void 0?`${e.records}`:"—",e.records!==void 0?Math.min(1,e.records/20):0)}updateClaim(){if(!this.claimValue)return;if(this.requiredSeeds<=0){this.claimValue.textContent="—";return}const e=Math.max(0,this.requiredSeeds-this.measuredSeeds);this.claimValue.textContent=`${e} more (${this.requiredSeeds} needed)`}updateConnection(){if(!this.connectionPill)return;const e=this.connectionPill.querySelector(".dot"),t=this.connectionPill.querySelector("span:last-child"),n=this.connected?z.ok:z.error;e.style.background=n,this.connectionPill.style.background=`${n}22`,this.connectionPill.style.borderColor=`${n}88`,this.connectionPill.style.color=n,t.textContent=this.connected?"live":"offline"}toggle(){this.panel&&(this.panel.style.display=this.panel.style.display==="none"?"":"none")}update(e){var n;this.animationTime+=e;const t=.5+.5*Math.sin(this.animationTime*2);(n=this.connectionPill)==null||n.style.setProperty("opacity",`${.75+.25*t}`)}}const Ml=new Ib;Ki.register(Ml);const $o={hud:"h",rail:"r",caption:"c"},om={pareto:"p",ablation:"a",variability:"s"},lm="v",Ef=new Set([...Object.values($o),...Object.values(om),lm]);class Ub{constructor(e){I(this,"canvas");I(this,"context");I(this,"visible",!1);this.canvas=document.createElement("canvas"),this.canvas.id=e,this.canvas.style.cssText=`
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      z-index: 50;
      display: none;
      background: var(--bg);
      pointer-events: none;
    `,document.body.appendChild(this.canvas),this.context=this.canvas.getContext("2d"),this.resize(),window.addEventListener("resize",()=>{this.resize()})}show(){this.visible=!0,this.canvas.style.display="block",this.resize(),this.begin()}hide(){this.visible=!1,this.canvas.style.display="none"}resize(){const e=Math.min(window.devicePixelRatio||1,2);this.canvas.width=Math.floor(window.innerWidth*e),this.canvas.height=Math.floor(window.innerHeight*e),this.context.setTransform(e,0,0,e,0,0)}begin(){const e=this.context;return e.clearRect(0,0,window.innerWidth,window.innerHeight),e.fillStyle="#0a0e14",e.fillRect(0,0,window.innerWidth,window.innerHeight),e}area(){const e=document.getElementById("discovery-legend"),t=e?e.getBoundingClientRect().right:0,n=Math.max(40,t+24),s=Math.max(200,window.innerWidth*xp-n);return{x:n,y:70,width:s,height:Math.max(200,window.innerHeight*vp-70)}}}const Xe=new Ub("stage-2d"),xn={top:64,right:36,bottom:62,left:78};function aa(i,e,t,n){i.fillStyle=z.text_primary,i.font="600 22px 'JetBrains Mono', monospace",i.textAlign="left",i.textBaseline="alphabetic",i.fillText(t,e.x,e.y+14),n&&(i.fillStyle=z.text_secondary,i.font="13px 'JetBrains Mono', monospace",i.fillText(n,e.x,e.y+40))}function Ha(i,e,t=5){if(!Number.isFinite(i)||!Number.isFinite(e))return[i];if(i===e)return[i];const s=(e-i)/Math.max(1,t),r=10**Math.floor(Math.log10(s)),a=s/r,o=(a>=5?10:a>=2?5:a>=1?2:1)*r,l=Math.ceil(i/o)*o,c=[];for(let h=l;h<=e+o*1e-6;h+=o)c.push(Number(h.toFixed(10)));return c}function Va(i){const e=Math.abs(i);return e===0?"0":e>=1e3||e>=10?i.toFixed(0):e>=1?i.toFixed(1):e>=.01?i.toFixed(2):i.toExponential(1)}function Ri(i,e){const t=e.xMax-e.xMin;return t===0?e.rect.x:e.rect.x+(i-e.xMin)/t*e.rect.width}function Xn(i,e){const t=e.yMax-e.yMin;return t===0?e.rect.y+e.rect.height:e.rect.y+e.rect.height-(i-e.yMin)/t*e.rect.height}function Ya(i,e,t){const n={x:e.x+xn.left,y:e.y+xn.top,width:Math.max(40,e.width-xn.left-xn.right),height:Math.max(40,e.height-xn.top-xn.bottom)},s={rect:n,xMin:t.xMin,xMax:t.xMax,yMin:t.yMin,yMax:t.yMax};aa(i,e,t.title,t.subtitle);const r=t.xTicks??Ha(t.xMin,t.xMax,6),a=t.yTicks??Ha(t.yMin,t.yMax,5);return i.strokeStyle=z.border,i.lineWidth=1,i.beginPath(),i.rect(n.x,n.y,n.width,n.height),i.stroke(),i.font="12px 'JetBrains Mono', monospace",i.fillStyle=z.text_secondary,r.forEach(o=>{const l=Ri(o,s);l<n.x-1||l>n.x+n.width+1||(i.strokeStyle=z.border,i.beginPath(),i.moveTo(l,n.y),i.lineTo(l,n.y+n.height),i.stroke(),i.textAlign="center",i.fillText(Va(o),l,n.y+n.height+20))}),a.forEach(o=>{const l=Xn(o,s);l<n.y-1||l>n.y+n.height+1||(i.strokeStyle=z.border,i.beginPath(),i.moveTo(n.x,l),i.lineTo(n.x+n.width,l),i.stroke(),i.textAlign="right",i.fillText(Va(o),n.x-10,l+4))}),i.fillStyle=z.text_secondary,i.font="13px 'JetBrains Mono', monospace",i.textAlign="center",i.fillText(t.xLabel,n.x+n.width/2,n.y+n.height+46),i.save(),i.translate(n.x-56,n.y+n.height/2),i.rotate(-Math.PI/2),i.textAlign="center",i.fillText(t.yLabel,0,0),i.restore(),s}function yh(i,e,t){const n=e.split(/\s+/).filter(a=>a.length>0),s=[];let r="";return n.forEach(a=>{const o=r?`${r} ${a}`:a;if(r&&i.measureText(o).width>t){s.push(r),r=a;return}r=o}),r&&s.push(r),s}function Fn(i,e,t){i.fillStyle=z.text_secondary,i.font="12px 'JetBrains Mono', monospace",i.textAlign="left",i.textBaseline="alphabetic",i.fillText(t,e.x,e.y+e.height+40)}function cm(i,e,t){const n={x:e.x+xn.left,y:e.y+xn.top,width:Math.max(40,e.width-xn.left-xn.right),height:Math.max(40,e.height-xn.top-xn.bottom)},s=n.width/Math.max(1,t.categories.length),r={rect:n,yMin:t.yMin,yMax:t.yMax,categories:t.categories,bandWidth:s,band:l=>n.x+s*(l+.5)},a={rect:n,yMin:t.yMin,yMax:t.yMax};return aa(i,e,t.title,t.subtitle),i.strokeStyle=z.border,i.lineWidth=1,i.strokeRect(n.x+.5,n.y+.5,n.width-1,n.height-1),i.font="12px 'JetBrains Mono', monospace",i.fillStyle=z.text_secondary,(t.yTicks??Ha(t.yMin,t.yMax,5)).forEach(l=>{const c=Xn(l,a);c<n.y-1||c>n.y+n.height+1||(i.strokeStyle=z.border,i.beginPath(),i.moveTo(n.x,c),i.lineTo(n.x+n.width,c),i.stroke(),i.textAlign="right",i.fillText(Va(l),n.x-10,c+4))}),i.textAlign="center",i.textBaseline="top",t.categories.forEach((l,c)=>{sl(l,14).forEach((h,u)=>{i.fillText(h,r.band(c),n.y+n.height+12+u*16)})}),i.fillStyle=z.text_secondary,i.font="13px 'JetBrains Mono', monospace",i.save(),i.translate(n.x-56,n.y+n.height/2),i.rotate(-Math.PI/2),i.textAlign="center",i.textBaseline="alphabetic",i.fillText(t.yLabel,0,0),i.restore(),r}function Sl(i,e,t){i.font="12px 'JetBrains Mono', monospace";const n=t.rows.reduce((h,u)=>Math.max(h,i.measureText(u).width),0),s=Math.min(e.width*.45,Math.max(xn.left,n+24)),r={x:e.x+s,y:e.y+xn.top,width:Math.max(40,e.width-s-xn.right),height:Math.max(40,e.height-xn.top-xn.bottom)},a=r.height/Math.max(1,t.rows.length),o={rect:r,xMin:t.xMin,xMax:t.xMax,rows:t.rows,rowHeight:a,rowY:h=>r.y+a*(h+.5)},l={rect:r,xMin:t.xMin,xMax:t.xMax};return aa(i,e,t.title,t.subtitle),i.strokeStyle=z.border,i.lineWidth=1,i.strokeRect(r.x+.5,r.y+.5,r.width-1,r.height-1),i.font="12px 'JetBrains Mono', monospace",i.fillStyle=z.text_secondary,(t.xTicks??Ha(t.xMin,t.xMax,6)).forEach(h=>{const u=Ri(h,l);u<r.x-1||u>r.x+r.width+1||(i.strokeStyle=z.border,i.beginPath(),i.moveTo(u,r.y),i.lineTo(u,r.y+r.height),i.stroke(),i.textAlign="center",i.textBaseline="alphabetic",i.fillText(Va(h),u,r.y+r.height+20))}),i.textAlign="right",i.textBaseline="middle",t.rows.forEach((h,u)=>{i.fillText(h,r.x-12,o.rowY(u))}),i.fillStyle=z.text_secondary,i.font="13px 'JetBrains Mono', monospace",i.textAlign="center",i.textBaseline="alphabetic",i.fillText(t.xLabel,r.x+r.width/2,r.y+r.height+46),o}class Nb{constructor(){I(this,"id","cost");I(this,"name","The claim's cost");I(this,"caption","The seeds each cell measured, against the seeds a claim is measured against.");I(this,"visible",!1);I(this,"drawn",!1)}enter(){this.visible=!0,Xe.show(),this.draw()}exit(){this.visible=!1,Xe.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}costs(){const e=Ee.axes,t=Ee.requiredSeeds,n=zh(Ee.aggregates,e),s=dl(n,e);return n.map(r=>({cell:r,label:za(r,e,s),color:Xt[r.coordinate.credit]??z.gradient,measured:r.seeds,required:t})).sort((r,a)=>a.required-a.measured-(r.required-r.measured))}draw(){const e=this.costs();if(e.length===0){this.drawn=!1;return}const t=Xe.begin(),n=Xe.area(),s=Math.max(Ee.requiredSeeds,...e.map(c=>c.measured)),r=Sl(t,n,{xMin:0,xMax:s,rows:e.map(c=>c.label),title:"The claim's cost",subtitle:"the seeds measured, and the seeds a claim still needs",xLabel:"seeds"}),a=c=>r.rect.x+c/(r.xMax||1)*r.rect.width;e.forEach((c,h)=>{const u=r.rowY(h),d=Math.min(26,r.rowHeight*.5);t.fillStyle=z.bg_tertiary,t.fillRect(r.rect.x,u-d/2,a(c.required)-r.rect.x,d);const f=a(c.measured)-r.rect.x;t.fillStyle=c.color,t.fillRect(r.rect.x,u-d/2,f,d);const g=Math.max(0,c.required-c.measured);g>0&&(t.strokeStyle=z.warn,t.lineWidth=2,t.setLineDash([5,4]),t.beginPath(),t.moveTo(a(c.measured)+4,u),t.lineTo(a(c.required)-4,u),t.stroke(),t.setLineDash([])),t.strokeStyle=z.border,t.lineWidth=1,t.strokeRect(r.rect.x+.5,u-d/2,a(c.required)-r.rect.x-1,d-1),t.font="12px 'JetBrains Mono', monospace",t.textAlign="left",t.textBaseline="middle",t.fillStyle=z.text_secondary,t.fillText(`${c.measured} of ${c.required}`,r.rect.x+r.rect.width+12,u-8),g>0&&(t.fillStyle=z.warn,t.fillText(`${g} short`,r.rect.x+r.rect.width+12,u+9))});const o=a(Ee.requiredSeeds);o>r.rect.x&&o<r.rect.x+r.rect.width&&(t.strokeStyle=z.text_secondary,t.lineWidth=1,t.setLineDash([3,4]),t.beginPath(),t.moveTo(o,r.rect.y),t.lineTo(o,r.rect.y+r.rect.height),t.stroke(),t.setLineDash([]));const l=e.reduce((c,h)=>c+Math.max(0,h.required-h.measured),0);Fn(t,n,`the claim is ${l} seeds short over ${e.length} cells`),this.drawn=!0}}class Fb{constructor(){I(this,"id","contrast");I(this,"name","The contrast");I(this,"caption","The run's arms against one another, and whether the test could be run.");I(this,"key","d");I(this,"visible",!1);I(this,"drawn",!1)}enter(){this.visible=!0,Xe.show(),this.draw()}exit(){this.visible=!1,Xe.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}draw(){var h,u,d;const e=(h=Ee.account)==null?void 0:h.contrast;if(!e||e.pairs.length===0){this.drawn=!1;return}const t=new Map,n=new Map;e.arms.forEach(f=>{t.set(f.value,f.mean),n.set(f.value,f.sd)});const s=Math.max(...e.arms.map(f=>f.mean),.001),r=Xe.begin(),a=Xe.area(),o=Sl(r,a,{xMin:0,xMax:s*1.15,rows:e.pairs.map(f=>`${f.a} vs ${f.b}`),title:"The contrast",subtitle:`the ${e.axis} arms on ${e.metric}, and what separates them`,xLabel:e.metric}),l=f=>o.rect.x+f/(o.xMax||1)*o.rect.width;e.pairs.forEach((f,g)=>{const _=o.rowY(g),p=l(t.get(f.a)??0),m=l(t.get(f.b)??0);r.fillStyle=`${z.gradient}33`,r.fillRect(Math.min(p,m),_-11,Math.abs(m-p),22),r.strokeStyle=z.border_bright,r.lineWidth=2,r.beginPath(),r.moveTo(p,_),r.lineTo(m,_),r.stroke(),[f.a,f.b].forEach(v=>{const b=l(t.get(v)??0);n.get(v),r.strokeStyle=Xt[v]??z.gradient,r.lineWidth=1,r.beginPath(),r.moveTo(b,_-16),r.lineTo(b,_+16),r.stroke(),r.fillStyle=Xt[v]??z.gradient,r.beginPath(),r.arc(b,_,6,0,Math.PI*2),r.fill(),r.font="11px 'JetBrains Mono', monospace",r.textAlign="center",r.textBaseline="bottom",r.fillStyle=Xt[v]??z.gradient,r.fillText(v,b,_-18)}),r.font="12px 'JetBrains Mono', monospace",r.textAlign="left",r.textBaseline="middle",r.fillStyle=z.text_primary;const M=f.difference??0;r.fillText(`${M>=0?"+":"−"}${Math.abs(M).toFixed(3)}`,o.rect.x+o.rect.width+12,_-9),r.fillStyle=z.text_secondary,r.fillText(`${f.shared_cells} shared cell${f.shared_cells===1?"":"s"}`,o.rect.x+o.rect.width+12,_+9)});const c=e.test;Fn(r,a,c.tested?`the test ran: p=${(u=c.p_value)==null?void 0:u.toFixed(4)} (alpha=${c.alpha}) · dz=${(d=c.cohens_dz)==null?void 0:d.toFixed(2)} · ${c.shared_cells} shared cells`:`no test ran: ${c.shared_cells} shared cell${c.shared_cells===1?"":"s"}, ${c.required_cells} required`),this.drawn=!0}}class Ob{constructor(){I(this,"id","convergence");I(this,"name","Convergence");I(this,"caption","Accuracy against epoch, one curve per arm, with the chance level under them.");I(this,"visible",!1);I(this,"drawn",!1)}enter(){this.visible=!0,Xe.show(),this.draw()}exit(){this.visible=!1,Xe.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}curves(){var n;const e=((n=Ee.metrics)==null?void 0:n.records)??[],t=new Map;return e.forEach(s=>{var l,c;const r=(l=s==null?void 0:s.payload)==null?void 0:l.convergence_curve;if(!Array.isArray(r)||r.length===0)return;const a=((c=s==null?void 0:s.coordinate)==null?void 0:c.credit)??"",o=t.get(a)??new Map;r.forEach(h=>{if(typeof(h==null?void 0:h.epoch)!="number"||typeof(h==null?void 0:h.val_acc)!="number")return;const u=o.get(h.epoch)??[];u.push(h.val_acc),o.set(h.epoch,u)}),t.set(a,o)}),Array.from(t.entries()).map(([s,r])=>({arm:s,points:Array.from(r.entries()).sort((a,o)=>a[0]-o[0]).map(([a,o])=>({epoch:a,val_acc:o.reduce((l,c)=>l+c,0)/o.length}))}))}draw(){const e=this.curves();if(e.length===0){this.drawn=!1;return}const t=Xe.begin(),n=Xe.area(),s=Ee.chance,r=Math.max(...e.flatMap(h=>h.points.map(u=>u.epoch))),a=Math.max(s,...e.flatMap(h=>h.points.map(u=>u.val_acc))),o=Ya(t,n,{xMin:0,xMax:r,yMin:0,yMax:a,xLabel:"epoch",yLabel:"accuracy",title:"Convergence",subtitle:"the mean accuracy of each arm, epoch by epoch",xTicks:void 0,yTicks:void 0}),l=Xn(s,o);t.strokeStyle=z.chance_line,t.lineWidth=1.5,t.setLineDash([6,5]),t.beginPath(),t.moveTo(o.rect.x,l),t.lineTo(o.rect.x+o.rect.width,l),t.stroke(),t.setLineDash([]),e.forEach(h=>{const u=Xt[h.arm]||z.gradient;t.strokeStyle=u,t.lineWidth=2.5,t.beginPath(),h.points.forEach((d,f)=>{const g=Ri(d.epoch,o),_=Xn(d.val_acc,o);f===0?t.moveTo(g,_):t.lineTo(g,_)}),t.stroke(),h.points.forEach(d=>{t.fillStyle=u,t.beginPath(),t.arc(Ri(d.epoch,o),Xn(d.val_acc,o),3,0,Math.PI*2),t.fill()})}),t.font="12px 'JetBrains Mono', monospace",t.textAlign="left",t.textBaseline="middle";let c=o.rect.y+10;e.forEach(h=>{const u=Xt[h.arm]||z.gradient;t.fillStyle=u,t.fillRect(o.rect.x+o.rect.width+18,c-5,10,10),t.fillStyle=z.text_secondary,t.fillText(h.arm,o.rect.x+o.rect.width+34,c),c+=20}),Fn(t,n,`${e.length} arms · the dashed line is the chance level (${s.toFixed(2)})`),this.drawn=!0}}function iu(i){const e=i.replace("#","");return[parseInt(e.slice(0,2),16),parseInt(e.slice(2,4),16),parseInt(e.slice(4,6),16)]}function Tf(i){return`#${i.map(e=>Math.round(Math.max(0,Math.min(255,e))).toString(16).padStart(2,"0")).join("")}`}function Af(i,e,t){return[i[0]+(e[0]-i[0])*t,i[1]+(e[1]-i[1])*t,i[2]+(e[2]-i[2])*t]}const Bb=iu(z.ramp_low),Rf=iu(z.ramp_mid),zb=iu(z.ramp_high);function Gs(i){const e=Math.max(0,Math.min(1,i));return e<=.5?Tf(Af(Bb,Rf,e*2)):Tf(Af(Rf,zb,(e-.5)*2))}function bl(){const i=Ee.dynamics;return!i||!i.stateful?null:i}function kb(i){var t;const e=((t=i.cell)==null?void 0:t.coordinate)??{};return[e.geometry,e.dynamics,e.credit].filter(n=>typeof n=="string"&&n.length>0).join(" · ")}function wl(i){var n;const e=[],t=kb(i);return t&&e.push(t),((n=i.cell)==null?void 0:n.measured_by_run)===!1&&e.push("a cell of the space, not one the run measured"),i.trained===!1&&e.push("the weights are untrained"),e.join(" · ")}class El{constructor(){I(this,"key");I(this,"visible",!1);I(this,"drawn",!1)}enter(){this.visible=!0,Xe.show(),this.draw()}exit(){this.visible=!1,Xe.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}}class Hb extends El{constructor(){super(...arguments);I(this,"id","trajectory");I(this,"name","The trajectory");I(this,"caption","Where the cell's own state went, step by step: the path it took through the space it moves in.");I(this,"key","j")}draw(){const t=bl(),n=t==null?void 0:t.trajectory;if(!t||!n||n.path.length<2){this.drawn=!1;return}const s=Xe.begin(),r=Xe.area(),a=n.path,o=a.map(v=>v[0]),l=a.map(v=>v[1]),c=.08,h=Math.min(...o),u=Math.max(...o),d=Math.min(...l),f=Math.max(...l),g=u-h||1,_=f-d||1,p=Ya(s,r,{xMin:h-g*c,xMax:u+g*c,yMin:d-_*c,yMax:f+_*c,xLabel:n.axes[0]??"the direction the state moved",yLabel:n.axes[1]??"the direction across it",title:"The trajectory",subtitle:wl(t)});for(let v=1;v<a.length;v+=1){const b=v/(a.length-1);s.strokeStyle=Gs(b),s.lineWidth=2.5,s.beginPath(),s.moveTo(Ri(a[v-1][0],p),Xn(a[v-1][1],p)),s.lineTo(Ri(a[v][0],p),Xn(a[v][1],p)),s.stroke()}const m=(v,b,N)=>{const A=Ri(v[0],p),R=Xn(v[1],p);s.fillStyle=b,s.beginPath(),s.arc(A,R,5,0,Math.PI*2),s.fill(),s.font="12px 'JetBrains Mono', monospace",s.textAlign="left",s.textBaseline="middle",s.fillText(N,A+10,R)};m(a[0],z.text_primary,"where it started"),m(a[a.length-1],z.warn,"where it stopped");const M=n.error??[];if(M.length>1){const v=Math.min(...M),b=Math.max(...M),N=p.rect.height*.16,A=p.rect.y+p.rect.height-N*.5,R=F=>A-(F-v)/(b-v||1)*N*.5;s.strokeStyle=z.thermodynamic_contrast,s.lineWidth=1.5,s.beginPath(),M.forEach((F,w)=>{const y=p.rect.x+w/(M.length-1)*p.rect.width;w===0?s.moveTo(y,R(F)):s.lineTo(y,R(F))}),s.stroke(),s.font="11px 'JetBrains Mono', monospace",s.fillStyle=z.thermodynamic_contrast,s.textAlign="right",s.textBaseline="bottom",s.fillText("the prediction error",p.rect.x+p.rect.width,A-N*.6)}Fn(s,r,t.verdict??""),this.drawn=!0}}class Vb extends El{constructor(){super(...arguments);I(this,"id","spectrum");I(this,"name","The spectrum");I(this,"caption","How fast a nudge grows along each direction: the exponents that say whether this dynamics settles.");I(this,"key","m")}draw(){const t=bl(),n=t==null?void 0:t.spectrum;if(!t||!n||n.length===0){this.drawn=!1;return}const s=Xe.begin(),r=Xe.area(),o=Math.max(...n.map(u=>Math.abs(u)),1e-6)*1.25,l=Ya(s,r,{xMin:0,xMax:n.length,yMin:-o,yMax:o,xLabel:"direction",yLabel:"growth per step",title:"The spectrum",subtitle:wl(t),xTicks:Ha(0,n.length,6).filter(u=>Number.isInteger(u))}),c=Xn(0,l);s.strokeStyle=z.text_muted,s.lineWidth=1.5,s.beginPath(),s.moveTo(l.rect.x,c),s.lineTo(l.rect.x+l.rect.width,c),s.stroke();const h=l.rect.width/n.length;n.forEach((u,d)=>{const f=l.rect.x+h*(d+.5),g=Math.min(46,h*.5),_=Xn(u,l),p=u>0;s.fillStyle=p?z.warn:z.ok,s.fillRect(f-g/2,Math.min(_,c),g,Math.abs(_-c)),s.font="11px 'JetBrains Mono', monospace",s.fillStyle=p?z.warn:z.ok,s.textAlign="center",s.textBaseline=p?"bottom":"top",s.fillText(Va(u),f,p?_-5:_+5)}),Fn(s,r,t.verdict??""),this.drawn=!0}}class Gb extends El{constructor(){super(...arguments);I(this,"id","basin");I(this,"name","The basin");I(this,"caption","The states near the cell's own: how many come back, and how far the ones that do not stray.");I(this,"key","b")}draw(){const t=bl(),n=t==null?void 0:t.basin;if(!t||!n||n.paths.length===0){this.drawn=!1;return}const s=Xe.begin(),r=Xe.area(),a=n.paths,o=Math.max(...a.flatMap(h=>h.distances),1e-6),l=Ya(s,r,{xMin:0,xMax:a[0].distances.length,yMin:0,yMax:o*1.1,xLabel:"steps after the nudge",yLabel:"distance from the attractor",title:"The basin",subtitle:wl(t)}),c=n.radii;a.forEach(h=>{const u=c.indexOf(h.radius),d=c.length>1?u/(c.length-1):.5;s.strokeStyle=h.returned?z.ok:Gs(d),s.lineWidth=2,s.beginPath(),h.distances.forEach((f,g)=>{const _=Ri(g,l),p=Xn(f,l);g===0?s.moveTo(_,p):s.lineTo(_,p)}),s.stroke()}),s.font="12px 'JetBrains Mono', monospace",s.textAlign="center",s.textBaseline="top",n.stability.forEach((h,u)=>{const d=l.rect.x+l.rect.width/c.length*(u+.5);s.fillStyle=h>0?z.ok:z.warn,s.fillText(`${Math.round(h*100)}% back`,d,l.rect.y+12),s.fillStyle=z.text_secondary,s.fillText(`nudge ${c[u]}`,d,l.rect.y+28)}),Fn(s,r,t.verdict??""),this.drawn=!0}}class Wb extends El{constructor(){super(...arguments);I(this,"id","landscape");I(this,"name","The landscape");I(this,"caption","The cell's own energy over the ground its trajectory crossed, and the path it took across it.");I(this,"key","n")}draw(){const t=bl(),n=t==null?void 0:t.landscape,s=t==null?void 0:t.trajectory;if(!t||!n||n.grid.length===0){this.drawn=!1;return}const r=Xe.begin(),a=Xe.area(),o=n.grid,l=o.flat(),c=Math.min(...l),h=Math.max(...l),u=Ya(r,a,{xMin:n.x[0],xMax:n.x[n.x.length-1],yMin:n.y[0],yMax:n.y[n.y.length-1],xLabel:"along the trajectory",yLabel:"across it",title:"The landscape",subtitle:wl(t)}),d=u.rect.width/(n.x.length-1||1),f=u.rect.height/(n.y.length-1||1);r.save(),r.beginPath(),r.rect(u.rect.x,u.rect.y,u.rect.width,u.rect.height),r.clip(),o.forEach((v,b)=>{v.forEach((N,A)=>{const R=(N-c)/(h-c||1);r.fillStyle=Gs(1-R);const F=u.rect.x+d*b,w=u.rect.y+u.rect.height-f*(A+1);r.fillRect(F,w,d+1,f+1)})}),r.restore(),s&&s.path.length>1&&(r.strokeStyle=z.text_primary,r.lineWidth=2,r.beginPath(),s.path.forEach((v,b)=>{const N=Ri(v[0],u),A=Xn(v[1],u);b===0?r.moveTo(N,A):r.lineTo(N,A)}),r.stroke());let g=0,_=0,p=Number.POSITIVE_INFINITY;o.forEach((v,b)=>v.forEach((N,A)=>{N<p&&(p=N,g=b,_=A)}));const m=Ri(n.x[g],u),M=Xn(n.y[_],u);r.strokeStyle=z.ok,r.lineWidth=2,r.beginPath(),r.arc(m,M,7,0,Math.PI*2),r.stroke(),r.font="12px 'JetBrains Mono', monospace",r.fillStyle=z.ok,r.textAlign="left",r.textBaseline="bottom",r.fillText("the lowest ground",m+11,M-6),Fn(r,a,t.verdict??""),this.drawn=!0}}class Xb{constructor(){I(this,"id","effect");I(this,"name","The effect");I(this,"caption","Which axis moved the objective, and which the run held fixed: the run's attribution, and its limits.");I(this,"key","e");I(this,"visible",!1);I(this,"drawn",!1)}enter(){this.visible=!0,Xe.show(),this.draw()}exit(){this.visible=!1,Xe.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}draw(){const e=Ee.attribution,t=(e==null?void 0:e.axes)??[];if(!e||t.length===0){this.drawn=!1;return}const n=Xe.begin(),s=Xe.area(),r=t.flatMap(c=>c.values.map(h=>h.mean)),a=Math.max(...r,.1),o=cm(n,s,{yMin:0,yMax:a*1.15,categories:t.map(c=>c.axis),title:"The effect",subtitle:e.summary,yLabel:e.metric||"the objective"}),l=c=>o.rect.y+o.rect.height-c/(o.yMax||1)*o.rect.height;t.forEach((c,h)=>{const u=o.band(h),d=Math.min(46,o.bandWidth*.4);if(c.varied&&c.values.length>1){const _=Math.min(...c.values.map(b=>b.mean)),p=Math.max(...c.values.map(b=>b.mean)),m=l(p),M=l(_);n.fillStyle=`${z.gradient}33`,n.fillRect(u-d/2,m,d,M-m),n.strokeStyle=z.gradient,n.lineWidth=1,n.strokeRect(u-d/2,m,d,M-m);const v=[];c.values.forEach(b=>{const N=l(b.mean),A=Xt[b.value]??z.gradient;n.fillStyle=A,n.beginPath(),n.arc(u,N,5,0,Math.PI*2),n.fill();let R=N;for(;v.some(F=>Math.abs(F-R)<14);)R+=14;v.push(R),n.font="12px 'JetBrains Mono', monospace",n.textAlign="left",n.textBaseline="middle",n.fillStyle=A,n.fillText(b.value,u+d/2+10,R)});return}const f=c.values[0];if(!f)return;const g=l(f.mean);n.strokeStyle=z.text_muted,n.lineWidth=2,n.beginPath(),n.moveTo(u-7,g),n.lineTo(u+7,g),n.stroke(),n.font="12px 'JetBrains Mono', monospace",n.textAlign="center",n.textBaseline="top",n.fillStyle=z.text_muted,n.fillText(f.value,u,g+10)}),Fn(n,s,e.reason),this.drawn=!0}}const qb=84,$b=92;class Yb{constructor(){I(this,"id","flow");I(this,"name","The flow");I(this,"caption","The run's cells, stage by stage: what each one handled, and what the gate refused.");I(this,"key","f");I(this,"visible",!1);I(this,"drawn",!1)}enter(){this.visible=!0,Xe.show(),this.draw()}exit(){this.visible=!1,Xe.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}draw(){const e=Ee.flow,t=(e==null?void 0:e.stages)??[];if(!e||t.length===0){this.drawn=!1;return}const n=Xe.begin(),s=Xe.area();aa(n,s,"The flow","the run's cells, from the space to the evidence");const r=s.y+s.height-$b,a=Math.max(120,r-(s.y+qb)),o=Math.max(1,...t.map(c=>c.count+c.refused)),l=s.width/t.length;n.strokeStyle=z.border,n.lineWidth=1,n.beginPath(),n.moveTo(s.x,r+.5),n.lineTo(s.x+s.width,r+.5),n.stroke(),t.forEach((c,h)=>{const u=s.x+l*(h+.5),d=l*.56,f=p=>p/o*a,g=f(c.count),_=r-g;if(n.fillStyle=c.kind==="records"?z.measured:z.gradient,n.fillRect(u-d/2,_,d,Math.max(g,2)),c.refused>0){const p=f(c.refused);n.fillStyle=z.void,n.fillRect(u-d/2,_-p,d,p),n.font="12px 'JetBrains Mono', monospace",n.textAlign="center",n.textBaseline="bottom",n.fillStyle=z.void,n.fillText(`${c.refused} refused`,u,_-p-6)}c.count>0&&(n.font="600 15px 'JetBrains Mono', monospace",n.textAlign="center",n.textBaseline="bottom",n.fillStyle=z.text_primary,n.fillText(`${c.count}`,u,_-6)),n.font="12px 'JetBrains Mono', monospace",n.textAlign="center",n.textBaseline="top",n.fillStyle=c.count>0?z.text_secondary:z.text_muted,yh(n,c.action,l-8).slice(0,2).forEach((p,m)=>{n.fillText(p,u,r+10+m*16)})}),this.drawRefusals(n,s),Fn(n,s,e.summary),this.drawn=!0}drawRefusals(e,t){const n=Ee.space,s=(n==null?void 0:n.void_rules)??{},r=Object.keys(s),a=t.x;if(e.textAlign="left",e.textBaseline="alphabetic",e.font="600 13px 'JetBrains Mono', monospace",e.fillStyle=z.text_secondary,e.fillText("the rules that refuse",a,t.y+80),r.length===0){e.font="12px 'JetBrains Mono', monospace",e.fillStyle=z.text_muted,e.fillText("no cell of this slice is refused",a,t.y+102);return}e.font="12px 'JetBrains Mono', monospace",r.slice(0,6).forEach((o,l)=>{const c=t.y+102+l*18;e.fillStyle=z.void,e.fillText(o,a,c),e.fillStyle=z.text_secondary,e.textAlign="right",e.fillText(`${s[o]} cells`,a+280,c),e.textAlign="left"})}}function ea(i){i.traverse(e=>{var s;const t=e;(s=t.geometry)==null||s.dispose();const n=t.material;Array.isArray(n)?n.forEach(r=>r.dispose()):n==null||n.dispose()})}const Dr=6.4,Ta=4,Ir=5;class jb{constructor(){I(this,"id","frontier");I(this,"name","Frontier");I(this,"caption","Every measured cell in accuracy, speed and parameters; the frontier is the line nothing beat.");I(this,"group",new Ti);I(this,"visible",!1);I(this,"drawn",!1);I(this,"framed",!1);I(this,"accuracy",{min:0,max:0,span:0})}enter(){this.visible=!0;const e=xs();e&&e.scene.add(this.group),this.draw(!0)}exit(){var e;this.visible=!1,(e=this.group.parent)==null||e.remove(this.group),ea(this.group),this.group=new Ti,this.drawn=!1,this.framed=!1}refresh(){this.visible&&this.draw(!1)}ready(){return this.drawn}points(){var u,d;const e=((u=Ee.metrics)==null?void 0:u.records)??[],t=((d=Ee.metrics)==null?void 0:d.pareto)??[],n=Ee.chance,s=[],r=[],a=[];e.forEach(f=>{const g=(f==null?void 0:f.payload)??{};typeof g.val_acc=="number"&&s.push(g.val_acc),typeof g.walltime_s=="number"&&g.walltime_s>0&&r.push(1/g.walltime_s),typeof g.param_count=="number"&&g.param_count>0&&a.push(Math.log10(g.param_count))});const o=wc([...s,n]);this.accuracy=o;const l=wc(r),c=wc(a),h=[];return e.forEach((f,g)=>{var M;const _=(f==null?void 0:f.payload)??{};if(typeof _.val_acc!="number")return;const p=typeof _.walltime_s=="number"&&_.walltime_s>0?1/_.walltime_s:null,m=typeof _.param_count=="number"&&_.param_count>0?Math.log10(_.param_count):null;h.push({x:p===null||l.span===0?0:((p-l.min)/l.span-.5)*Dr,y:o.span===0?0:(_.val_acc-o.min)/o.span*Ta,z:m===null||c.span===0?0:((m-c.min)/c.span-.5)*Ir,arm:((M=f==null?void 0:f.coordinate)==null?void 0:M.credit)??"",pareto:t[g]===!0})}),h}draw(e){const t=this.points();if(t.length===0){this.drawn=!1;return}this.clear(),this.addPoints(t),this.addFront(t),this.addChanceFloor(),this.addLabels(),this.drawn=!0,(e||!this.framed)&&(this.frame(),this.framed=!0)}clear(){[...this.group.children].forEach(e=>{this.group.remove(e),ea(e)})}addPoints(e){const t=[],n=[];e.forEach(o=>{t.push(o.x,o.y,o.z);const l=new nt(Xt[o.arm]||z.gradient);n.push(l.r,l.g,l.b)});const s=new Gt;s.setAttribute("position",new zt(t,3)),s.setAttribute("color",new zt(n,3));const r=new Nh({size:.26,sizeAttenuation:!0,vertexColors:!0,map:RM(),alphaTest:.4,transparent:!0,opacity:.95});this.group.add(new mp(s,r));const a=e.filter(o=>o.pareto);a.length!==0&&a.forEach(o=>{const l=CM(z.pareto,.26);l.position.set(o.x,o.y,o.z),this.group.add(l)})}addFront(e){const t=e.filter(a=>a.pareto).sort((a,o)=>a.y-o.y);if(t.length<2)return;const n=[];t.forEach(a=>n.push(a.x,a.y,a.z));const s=new Gt;s.setAttribute("position",new zt(n,3));const r=new il(s,new gp({color:z.pareto,dashSize:.22,gapSize:.16,transparent:!0,opacity:.85}));r.computeLineDistances(),this.group.add(r)}addChanceFloor(){const e=Ee.chance,t=this.accuracy;if(t.span===0)return;const n=(e-t.min)/t.span*Ta,s=new $a(Dr*1.02,Ir*1.02);s.rotateX(-Math.PI/2);const r=new Qt(s,new ps({color:z.chance_line,transparent:!0,opacity:.07,side:In,depthWrite:!1}));r.position.y=n,this.group.add(r);const a=Un("chance",.24,new ji({color:z.chance_line,sizeAttenuation:!0}));a.position.set(Dr/2+.3,n,Ir/2+.3),this.group.add(a)}addLabels(){const e=new ji({color:13227232,sizeAttenuation:!0}),t=Un("speed 1/s",.26,e);t.position.set(Dr/2+.6,.1,0),this.group.add(t);const n=Un("accuracy",.26,e);n.position.set(0,Ta+.4,0),this.group.add(n);const s=Un("parameters",.26,e);s.position.set(0,.1,Ir/2+.7),this.group.add(s)}frame(){const e=xs();e&&ul(e,new V(-Dr/2-.6,-.2,-Ir/2-.6),new V(Dr/2+.6,Ta+.6,Ir/2+.6),new V(0,Ta/2,0))}}function wc(i){const e=i.filter(s=>Number.isFinite(s));if(e.length===0)return{min:0,max:0,span:0};const t=Math.min(...e),n=Math.max(...e);return{min:t,max:n,span:n-t}}const Aa=1.7,Vn=1,Cf=.9,Kb=new V(.72,.24,.65);class Zb{constructor(){I(this,"id","layers");I(this,"name","Layers");I(this,"key","y");I(this,"caption","The space cut into sheets: the lit ones are the cells the run measured.");I(this,"group",new Ti);I(this,"visible",!1);I(this,"drawn",!1);I(this,"framed",!1)}enter(){this.visible=!0;const e=xs();e&&e.scene.add(this.group),this.draw(!0)}exit(){var e;this.visible=!1,(e=this.group.parent)==null||e.remove(this.group),ea(this.group),this.group=new Ti,this.drawn=!1,this.framed=!1}refresh(){this.visible&&this.draw(!1)}ready(){return this.drawn}sheets(){const e=Ee.space;if(!e)return{sheets:[],nx:0,ny:0};const t=Ee.axes,n=e.values[t.x]??[],s=e.values[t.y]??[],r=e.values[t.z]??[];return{sheets:r.map((o,l)=>{const c=[];let h=0;return n.forEach((u,d)=>{s.forEach((f,g)=>{const _=js(u,f,o),p=Ee.spaceCells.get(_),m=Ee.aggregates.get(_),M=m&&m.acc.length>0?ms(m.acc):0;if((p==null?void 0:p.status)==="void"){c.push({status:"void",accuracy:0,arm:"",x:(d-(n.length-1)/2)*Vn,y:(g-(s.length-1)/2)*Vn});return}if(M>0){h+=1,c.push({status:"measured",accuracy:M,arm:(m==null?void 0:m.coordinate.credit)??"",x:(d-(n.length-1)/2)*Vn,y:(g-(s.length-1)/2)*Vn});return}c.push({status:"gap",accuracy:0,arm:"",x:(d-(n.length-1)/2)*Vn,y:(g-(s.length-1)/2)*Vn})})}),{value:o,height:(l-(r.length-1)/2)*Aa,cells:c,measured:h}}),nx:n.length,ny:s.length}}draw(e){const{sheets:t,nx:n,ny:s}=this.sheets();if(t.length===0){this.drawn=!1;return}this.clear();const r=[],a=[],o=[],l=[];let c=0;t.forEach(u=>{u.cells.forEach(d=>{d.status==="measured"&&(c=Math.max(c,d.accuracy))})});const h=c>0?c:1;t.forEach(u=>{u.cells.forEach(d=>{const f=new nt(d.status==="measured"?Xt[d.arm]||z.gradient:d.status==="void"?z.void:z.border_bright);d.status==="measured"?f.multiplyScalar(.65+.35*(d.accuracy/h)):f.multiplyScalar(.3);const g=d.status==="measured"?o:r,_=d.status==="measured"?l:a,p=Vn/2;g.push(d.x-p,u.height,d.y-p,d.x+p,u.height,d.y-p,d.x+p,u.height,d.y+p,d.x-p,u.height,d.y+p);for(let m=0;m<4;m+=1)_.push(f.r,f.g,f.b)})}),r.length>0&&this.group.add(new Qt(Pf(r,a),new ps({vertexColors:!0,transparent:!0,opacity:.11,side:In,depthWrite:!1}))),o.length>0&&this.group.add(new Qt(Pf(o,l),new ps({vertexColors:!0,side:In}))),this.addPins(t),this.addSheetEdges(t,n,s),this.addLabels(t,n,s),this.drawn=t.some(u=>u.measured>0),(e||!this.framed)&&(this.frame(t,n,s),this.framed=!0)}addPins(e){e.forEach(t=>{t.cells.forEach(n=>{if(n.status!=="measured")return;const s=new nt(Xt[n.arm]||z.gradient),r=new Ei(.22,Cf,.22);r.translate(0,Cf/2,0);const a=new Ia({color:s,emissive:s,emissiveIntensity:.55,roughness:.4,metalness:.2}),o=new Qt(r,a);o.position.set(n.x,t.height,n.y),this.group.add(o)})})}addSheetEdges(e,t,n){const s=[],r=t*Vn/2,a=n*Vn/2;if(e.forEach(l=>{const c=[[-r,-a],[r,-a],[r,a],[-r,a]];c.forEach((h,u)=>{const d=c[(u+1)%c.length];s.push(h[0],l.height,h[1],d[0],l.height,d[1])})}),s.length===0)return;const o=new Gt;o.setAttribute("position",new zt(s,3)),this.group.add(new Ws(o,new Ai({color:z.border_bright,transparent:!0,opacity:.65})))}addLabels(e,t,n){const s=Ee.axes,r=new ji({color:13227232,sizeAttenuation:!0}),a=new ji({color:9148584,sizeAttenuation:!0}),o=t*Vn/2,l=n*Vn/2;e.forEach(d=>{const f=Un(d.value,.26,a);f.position.set(-o-.85,d.height,l),this.group.add(f)});const c=Un(s.z,.28,r);c.position.set(-o-.85,e.length*Aa*.5,-l),this.group.add(c);const h=Un(s.x,.28,r);h.position.set(o+.9,-Aa,l),this.group.add(h);const u=Un(s.y,.28,r);u.position.set(o+.9,-Aa,-l-.6),this.group.add(u)}frame(e,t,n){const s=xs();if(!s||e.length===0)return;const r=t*Vn/2,a=n*Vn/2,o=e.length*Aa/2;ul(s,new V(-r-1.4,-o-.4,-a-.6),new V(r+1.4,o+.4,a+.6),new V(0,0,0),Kb)}clear(){[...this.group.children].forEach(e=>{this.group.remove(e),ea(e)})}}function Pf(i,e){const t=new Gt;return t.setAttribute("position",new zt(i,3)),t.setAttribute("color",new zt(e,3)),t}const Lf={PASSED:z.passed,INSUFFICIENT:z.insufficient,REJECTED:z.rejected};class Jb{constructor(){I(this,"id","ledger");I(this,"name","The ledger");I(this,"caption","Every arm the run measured, its evidence, and the gate's standing on it.");I(this,"key","l");I(this,"visible",!1);I(this,"drawn",!1)}enter(){this.visible=!0,Xe.show(),this.draw()}exit(){this.visible=!1,Xe.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}chip(e,t,n,s){const r=Lf[s]??z.text_secondary;e.font="11px 'JetBrains Mono', monospace";const a=e.measureText(s).width+18;e.fillStyle=`${r}22`,e.strokeStyle=`${r}88`,e.lineWidth=1,e.beginPath(),e.roundRect(t,n-9,a,18,9),e.fill(),e.stroke(),e.fillStyle=r,e.textAlign="center",e.textBaseline="middle",e.fillText(s,t+a/2,n)}standingBar(e,t,n,s,r,a){const o=Object.values(r).reduce((h,u)=>h+u,0);if(o===0)return;const l=18;let c=t;Object.entries(r).forEach(([h,u])=>{if(u<=0)return;const d=u/o*s;e.fillStyle=Lf[h]??z.text_secondary,e.fillRect(c,n,Math.max(2,d-2),l),d>52&&(e.fillStyle=z.bg,e.font="11px 'JetBrains Mono', monospace",e.textAlign="center",e.textBaseline="middle",e.fillText(`${u}`,c+(d-2)/2,n+l/2)),c+=d}),e.font="12px 'JetBrains Mono', monospace",e.textAlign="left",e.textBaseline="alphabetic",e.fillStyle=z.text_secondary,e.fillText(`${a} arm${a===1?"":"s"}, and where each one stands`,t,n-10)}draw(){var r;const e=(r=Ee.account)==null?void 0:r.ledger;if(!e||e.claims.length===0){this.drawn=!1;return}const t=Xe.begin(),n=Xe.area();aa(t,n,"The ledger","every arm the run measured, its evidence, and the gate's standing on it");let s=n.y+96;this.standingBar(t,n.x,s,Math.min(560,n.width*.55),e.standings,e.claims.length),s+=66,e.claims.forEach(a=>{const o=Xt[a.value]??z.gradient;t.font="14px 'JetBrains Mono', monospace",t.textAlign="left",t.textBaseline="middle",t.fillStyle=o,t.fillText(`${a.axis} = ${a.value}`,n.x,s),t.font="13px 'JetBrains Mono', monospace",t.fillStyle=z.text_primary,t.fillText(`${a.mean.toFixed(3)} ± ${a.sd.toFixed(3)}`,n.x+300,s),t.font="12px 'JetBrains Mono', monospace",t.fillStyle=z.text_secondary,t.fillText(`${a.n} seeds · ${a.cells} cell${a.cells===1?"":"s"}`,n.x+460,s),this.chip(t,n.x+640,s,a.verdict),s+=42}),e.fixed.length>0&&(s+=22,t.font="600 14px 'JetBrains Mono', monospace",t.textAlign="left",t.textBaseline="alphabetic",t.fillStyle=z.text_primary,t.fillText("What was held fixed",n.x,s),s+=24,t.font="12px 'JetBrains Mono', monospace",e.fixed.forEach(a=>{t.textAlign="left",t.textBaseline="middle",t.fillStyle=z.text_secondary,t.fillText(`${a.axis} = ${a.value}`,n.x,s),t.fillText(`${a.mean.toFixed(3)}`,n.x+300,s),t.fillText(`${a.n} measurements · ${a.cells} cells`,n.x+460,s),s+=26})),s+=22,t.font="600 14px 'JetBrains Mono', monospace",t.textAlign="left",t.textBaseline="alphabetic",t.fillStyle=z.text_primary,t.fillText("What holds it back",n.x,s),s+=24,t.font="13px 'JetBrains Mono', monospace",e.limitations.forEach(a=>{yh(t,`· ${a.detail}`,n.width).forEach(o=>{t.fillStyle=z.text_secondary,t.fillText(o,n.x,s),s+=20})}),e.significance&&(s+=14,yh(t,`the report's test — ${e.significance}`,n.width).forEach(a=>{t.fillStyle=z.text_secondary,t.fillText(a,n.x,s),s+=20})),Fn(t,n,`a claim needs ${e.min_seeds} seeds per cell`+(e.chance!==null?` · the chance level is ${e.chance.toFixed(3)}`:"")),this.drawn=!0}}class Qb{constructor(){I(this,"id","matrix");I(this,"name","Evidence matrix");I(this,"caption","The space seen from above: one axis against another, every column a number, the refusals in the void colour.");I(this,"visible",!1);I(this,"drawn",!1)}enter(){this.visible=!0,Xe.show(),this.draw()}exit(){this.visible=!1,Xe.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}columns(){const e=Ee.space;if(!e)return{columns:[],xValues:[],yValues:[]};const t=Ee.axes,n=e.values[t.x]??[],s=e.values[t.y]??[],r=e.values[t.z]??[],a=[];return n.forEach(o=>{s.forEach(l=>{let c=0,h=0,u=-1/0,d="";r.forEach(g=>{const _=js(o,l,g),p=Ee.spaceCells.get(_);if((p==null?void 0:p.status)==="void"){c+=1;return}h+=1;const m=Ee.aggregates.get(_);if(!m||m.acc.length===0)return;const M=ms(m.acc);M>u&&(u=M,d=m.coordinate.credit??"")});const f=c>0&&h===0?"void":u>-1/0?"measured":"gap";a.push({status:f,accuracy:u>-1/0?u:0,arm:d})})}),{columns:a,xValues:n,yValues:s}}draw(){const{columns:e,xValues:t,yValues:n}=this.columns();if(e.length===0){this.drawn=!1;return}const s=Xe.begin(),r=Xe.area(),a=Ee.axes,o=t.length,l=n.length,c=150,u={x:r.x+c,y:r.y+70,width:Math.max(80,r.width-c-40),height:Math.max(80,r.height-70-96)},d=u.width/o,f=u.height/l,g=Math.max(...e.map(A=>A.accuracy),1e-4);s.fillStyle=z.text_primary,s.font="600 22px 'JetBrains Mono', monospace",s.textAlign="left",s.textBaseline="alphabetic",s.fillText("Evidence matrix",r.x,r.y+14),s.fillStyle=z.text_secondary,s.font="13px 'JetBrains Mono', monospace",s.fillText(`${a.x} against ${a.y} — the best cell of each column`,r.x,r.y+40);let _=0,p=0,m=0;e.forEach((A,R)=>{const F=Math.floor(R/l),w=R%l,y=u.x+F*d,P=u.y+w*f;A.status==="void"?(m+=1,s.fillStyle=`${z.void}22`,s.fillRect(y,P,d,f),this.drawCross(s,y,P,d,f)):A.status==="gap"?(p+=1,s.fillStyle=z.bg_tertiary,s.fillRect(y,P,d,f)):(_+=1,s.fillStyle=Gs(A.accuracy/g),s.fillRect(y,P,d,f),d>44&&f>26&&(s.fillStyle=ew(A.accuracy/g),s.font="600 15px 'JetBrains Mono', monospace",s.textAlign="center",s.textBaseline="middle",s.fillText(A.accuracy.toFixed(2),y+d/2,P+f/2))),s.strokeStyle=z.bg,s.lineWidth=1,s.strokeRect(y+.5,P+.5,d-1,f-1)}),s.fillStyle=z.text_secondary,s.font="12px 'JetBrains Mono', monospace",t.forEach((A,R)=>{const F=sl(A,14);s.textAlign="center",s.textBaseline="top",F.forEach((w,y)=>{s.fillText(w,u.x+R*d+d/2,u.y+u.height+12+y*16)})}),n.forEach((A,R)=>{const F=sl(A,16);s.textAlign="right",s.textBaseline="middle",F.forEach((w,y)=>{s.fillText(w,u.x-12,u.y+R*f+f/2-(F.length-1)*8+y*16)})});const M=180,v=u.x+u.width-M,b=r.y+16,N=s.createLinearGradient(v,0,v+M,0);N.addColorStop(0,Gs(0)),N.addColorStop(.5,Gs(.5)),N.addColorStop(1,Gs(1)),s.fillStyle=N,s.fillRect(v,b,M,12),s.strokeStyle=z.border,s.strokeRect(v+.5,b+.5,M-1,11),s.fillStyle=z.text_secondary,s.font="11px 'JetBrains Mono', monospace",s.textAlign="left",s.textBaseline="top",s.fillText("0",v,b+18),s.textAlign="right",s.fillText(g.toFixed(2),v+M,b+18),s.textAlign="left",s.fillText(`${_} measured · ${p} gaps · ${m} refused`,r.x,r.y+r.height+30),this.drawn=_>0}drawCross(e,t,n,s,r){const a=Math.min(s,r)*.28,o=t+s/2,l=n+r/2;e.strokeStyle=z.void,e.lineWidth=2,e.beginPath(),e.moveTo(o-a,l-a),e.lineTo(o+a,l+a),e.moveTo(o+a,l-a),e.lineTo(o-a,l+a),e.stroke()}}function ew(i){return i>.62?z.bg:z.text_primary}class tw{constructor(){I(this,"id","multiples");I(this,"name","Small multiples");I(this,"caption","One panel per cell: every seed's own curve, on the same accuracy scale.");I(this,"visible",!1);I(this,"drawn",!1)}enter(){this.visible=!0,Xe.show(),this.draw()}exit(){this.visible=!1,Xe.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}panels(){const e=Ee.axes,t=zh(Ee.aggregates,e),n=dl(t,e);return t.filter(s=>s.curves.length>0).map(s=>({cell:s,label:za(s,e,n),color:Xt[s.coordinate.credit]??z.gradient,curves:s.curves}))}draw(){const e=this.panels();if(e.length===0){this.drawn=!1;return}const t=Xe.begin(),n=Xe.area(),s=Ee.chance,r=e.flatMap(v=>v.curves.flatMap(b=>b.map(N=>N.val_acc))),a=e.flatMap(v=>v.curves.flatMap(b=>b.map(N=>N.epoch)));let o=Math.min(s,...r),l=Math.max(s,...r);l-o<1e-6&&(o-=.05,l+=.05);const c=(l-o)*.14;o-=c,l+=c;const h=Math.max(1,...a),u=Math.ceil(Math.sqrt(e.length)),d=Math.ceil(e.length/u),f=18,g=n.width-f*(u-1),_=n.height-64-44-f*(d-1),p=g/u,m=_/d;aa(t,n,"Small multiples","every seed of every cell, on one accuracy scale"),e.forEach((v,b)=>{const N=b%u,A=Math.floor(b/u),R=n.x+N*(p+f),F=n.y+64+A*(m+f);t.fillStyle=v.color,t.font="600 13px 'JetBrains Mono', monospace",t.textAlign="left",t.textBaseline="alphabetic",t.fillText(v.label,R,F+12);const w={x:R+(N===0?44:10),y:F+30,width:p-(N===0?54:20),height:m-56};t.strokeStyle=z.border,t.lineWidth=1,t.strokeRect(w.x+.5,w.y+.5,w.width-1,w.height-1);const y=w.y+w.height*(1-(s-o)/(l-o));t.strokeStyle=z.chance_line,t.lineWidth=1,t.setLineDash([4,4]),t.beginPath(),t.moveTo(w.x,y),t.lineTo(w.x+w.width,y),t.stroke(),t.setLineDash([]),v.curves.forEach(P=>{t.strokeStyle=v.color,t.lineWidth=1.8,t.beginPath(),P.forEach((K,H)=>{const Z=w.x+K.epoch/h*w.width,q=w.y+w.height*(1-(K.val_acc-o)/(l-o));H===0?t.moveTo(Z,q):t.lineTo(Z,q)}),t.stroke()}),t.fillStyle=z.text_muted,t.font="9px 'JetBrains Mono', monospace",N===0&&(t.textAlign="right",t.textBaseline="middle",[l,(l+o)/2,o].forEach(P=>{const K=w.y+w.height*(1-(P-o)/(l-o));t.fillText(P.toFixed(2),w.x-6,K)})),A===d-1&&(t.textAlign="left",t.textBaseline="top",t.fillText("epoch 0",w.x,w.y+w.height+6),t.textAlign="right",t.fillText(`epoch ${h}`,w.x+w.width,w.y+w.height+6))});const M=e.reduce((v,b)=>v+b.curves.length,0);Fn(t,n,`${e.length} cells · ${M} seeds · the dashed line is the chance level (${s.toFixed(2)})`),this.drawn=!0}}function nw(i,e,t){let n=0;return i.forEach(s=>{const r=(e-s)/t;n+=Math.exp(-.5*r*r)}),n/(i.length*t*Math.sqrt(2*Math.PI))}function Df(i){if(i.length<2)return .02;const e=i.reduce((r,a)=>r+a,0)/i.length,t=i.reduce((r,a)=>r+(a-e)**2,0)/(i.length-1),s=1.06*Math.sqrt(t)*i.length**-.2;return Math.max(s,.01)}class iw{constructor(){I(this,"id","spread");I(this,"name","The spread");I(this,"caption","One violin per arm, across its seeds: the width is the spread, not the mean.");I(this,"visible",!1);I(this,"drawn",!1)}enter(){this.visible=!0,Xe.show(),this.draw()}exit(){this.visible=!1,Xe.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}arms(){var n;const e=((n=Ee.metrics)==null?void 0:n.records)??[],t=new Map;return e.forEach(s=>{var l,c;const r=(l=s==null?void 0:s.payload)==null?void 0:l.val_acc,a=(c=s==null?void 0:s.coordinate)==null?void 0:c.credit;if(typeof r!="number"||!a)return;const o=t.get(a)??[];o.push(r),t.set(a,o)}),Array.from(t.entries()).map(([s,r])=>({name:s,values:r.slice().sort((a,o)=>a-o),color:Xt[s]??z.gradient})).sort((s,r)=>s.name.localeCompare(r.name))}draw(){const e=this.arms();if(e.length===0){this.drawn=!1;return}const t=Xe.begin(),n=Xe.area(),s=Ee.chance,r=Ee.requiredSeeds,a=e.map(h=>{const u=Df(h.values);return{high:h.values[h.values.length-1]+1.5*u,low:h.values[0]-1.5*u}}),o=Math.max(s,...a.map(h=>h.high))*1.03,l=cm(t,n,{yMin:0,yMax:o,categories:e.map(h=>h.name),title:"The spread",subtitle:"every seed of every arm, as a distribution",yLabel:"accuracy"}),c=l.rect.y+l.rect.height*(1-s/l.yMax);t.strokeStyle=z.chance_line,t.lineWidth=1.5,t.setLineDash([6,5]),t.beginPath(),t.moveTo(l.rect.x,c),t.lineTo(l.rect.x+l.rect.width,c),t.stroke(),t.setLineDash([]),t.save(),t.beginPath(),t.rect(l.rect.x,l.rect.y,l.rect.width,l.rect.height),t.clip(),e.forEach((h,u)=>{const d=l.band(u),f=Math.min(l.bandWidth*.36,90),g=Df(h.values),_=h.values[0]-1.5*g,p=h.values[h.values.length-1]+1.5*g,m=48,M=[];let v=0;for(let R=0;R<=m;R+=1){const F=_+(p-_)*R/m,w=nw(h.values,F,g);M.push(w),v=Math.max(v,w)}const b=v>0?1/v:0,N=R=>l.rect.y+l.rect.height*(1-R/l.yMax);t.beginPath(),M.forEach((R,F)=>{const w=_+(p-_)*F/m,y=d+R*b*f,P=N(w);F===0?t.moveTo(y,P):t.lineTo(y,P)});for(let R=M.length-1;R>=0;R-=1){const F=_+(p-_)*R/m,w=d-M[R]*b*f;t.lineTo(w,N(F))}t.closePath(),t.fillStyle=`${h.color}33`,t.fill(),t.strokeStyle=h.color,t.lineWidth=1.5,t.stroke(),h.values.forEach((R,F)=>{const w=(F-(h.values.length-1)/2)*7;t.fillStyle=h.color,t.beginPath(),t.arc(d+w,N(R),3,0,Math.PI*2),t.fill()});const A=h.values.reduce((R,F)=>R+F,0)/h.values.length;t.strokeStyle=z.text_primary,t.lineWidth=1.5,t.beginPath(),t.moveTo(d-f,N(A)),t.lineTo(d+f,N(A)),t.stroke()}),t.restore(),e.forEach((h,u)=>{const d=Math.max(0,r-h.values.length);t.font="11px 'JetBrains Mono', monospace",t.textAlign="center",t.textBaseline="top",t.fillStyle=z.text_secondary,t.fillText(`${h.values.length} of ${r} seeds`,l.band(u),l.rect.y+l.rect.height+46),d>0&&(t.fillStyle=z.warn,t.fillText(`${d} short`,l.band(u),l.rect.y+l.rect.height+62))}),Fn(t,n,`the white line is each arm's mean · a claim needs ${r} seeds per group`),this.drawn=!0}}const Ec=3.4,Ur=1.15,sw=new V(.34,.4,.85);class rw{constructor(){I(this,"id","terrain");I(this,"name","Terrain");I(this,"caption","The space as a heightfield: accuracy is the height, the gaps are flat, the refusals are craters.");I(this,"group",new Ti);I(this,"visible",!1);I(this,"drawn",!1);I(this,"framed",!1)}enter(){this.visible=!0;const e=xs();e&&e.scene.add(this.group),this.draw(!0)}exit(){var e;this.visible=!1,(e=this.group.parent)==null||e.remove(this.group),ea(this.group),this.group=new Ti,this.drawn=!1,this.framed=!1}refresh(){this.visible&&this.draw(!1)}ready(){return this.drawn}columns(){const e=Ee.space;if(!e)return{columns:[],xValues:[],yValues:[]};const t=Ee.axes,n=e.values[t.x]??[],s=e.values[t.y]??[],r=e.values[t.z]??[],a=[];return n.forEach((o,l)=>{s.forEach((c,h)=>{let u=0,d=0,f=-1/0,g="";r.forEach(p=>{const m=js(o,c,p),M=Ee.spaceCells.get(m);if((M==null?void 0:M.status)==="void"){u+=1;return}d+=1;const v=Ee.aggregates.get(m);if(!v||v.acc.length===0)return;const b=ms(v.acc);b>f&&(f=b,g=v.coordinate.credit??"")});const _=u>0&&d===0?"void":f>-1/0?"measured":"gap";a.push({status:_,accuracy:f>-1/0?f:0,arm:g,x:(l-(n.length-1)/2)*Ur,y:(h-(s.length-1)/2)*Ur})})}),{columns:a,xValues:n,yValues:s}}draw(e){const{columns:t,xValues:n,yValues:s}=this.columns();if(t.length===0){this.drawn=!1;return}this.clear();const r=Math.max(...t.map(f=>f.accuracy),1e-4),a=[],o=[],l=[];t.forEach(f=>{const g=f.status==="measured"?f.accuracy/r*Ec:f.status==="void"?-1.1:0;a.push(f.x,g,f.y);const _=new nt(f.status==="measured"?Xt[f.arm]||z.gradient:f.status==="void"?z.void:z.border_bright);if(f.status==="measured"){const p=.6+.4*(f.accuracy/r);_.multiplyScalar(p)}else f.status==="void"&&_.multiplyScalar(.55);o.push(_.r,_.g,_.b)});const c=n.length,h=s.length;for(let f=0;f<c-1;f+=1)for(let g=0;g<h-1;g+=1){const _=f*h+g,p=(f+1)*h+g,m=(f+1)*h+g+1,M=f*h+g+1;l.push(_,M,p,p,M,m)}const u=new Gt;u.setAttribute("position",new zt(a,3)),u.setAttribute("color",new zt(o,3)),u.setIndex(l),u.computeVertexNormals();const d=new Qt(u,new Ia({vertexColors:!0,roughness:.7,metalness:.1,side:In}));this.group.add(d),this.addVoidMarkers(t),this.addLabels(n,s),this.drawn=t.some(f=>f.status==="measured"),(e||!this.framed)&&(this.frame(t,n,s),this.framed=!0)}clear(){[...this.group.children].forEach(e=>{this.group.remove(e),ea(e)})}addVoidMarkers(e){const t=[];if(e.forEach(r=>{r.status==="void"&&t.push(r.x-.22,-1.1+.02,r.y-.22,r.x+.22,-1.1+.02,r.y+.22,r.x+.22,-1.1+.02,r.y-.22,r.x-.22,-1.1+.02,r.y+.22)}),t.length===0)return;const s=new Gt;s.setAttribute("position",new zt(t,3)),this.group.add(new Ws(s,new Ai({color:z.void,transparent:!0,opacity:.75})))}addLabels(e,t){const n=new ji({color:13227232,sizeAttenuation:!0}),s=(e.length-1)*Ur/2,r=(t.length-1)*Ur/2,a=Un(Ee.axes.x,.22,n);a.position.set(s+1,-.2,r+.9),this.group.add(a);const o=Un(Ee.axes.y,.22,n);o.position.set(-s-1,.2,-r),this.group.add(o)}frame(e,t,n){const s=xs();if(!s||e.length===0)return;const r=(t.length-1)*Ur/2,a=(n.length-1)*Ur/2;ul(s,new V(-r-1.2,-1.1-.3,-a),new V(r+1.2,Ec,a+1.4),new V(0,Ec/3,0),sw)}}class aw{constructor(){I(this,"id","timeline");I(this,"name","The timeline");I(this,"caption","The run's stages, in the order it reached them, and the time each held it.");I(this,"key","t");I(this,"visible",!1);I(this,"drawn",!1)}enter(){this.visible=!0,Xe.show(),this.draw()}exit(){this.visible=!1,Xe.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}draw(){const e=Ee.timeline,t=(e==null?void 0:e.stages)??[];if(!e||t.length===0){this.drawn=!1;return}const n=Xe.begin(),s=Xe.area(),r=Math.max(e.seconds,.001),a=Sl(n,s,{xMin:0,xMax:r,rows:t.map(d=>d.action),title:"The timeline",subtitle:"the run's stages, and the time each of them held it",xLabel:"seconds"}),o=d=>a.rect.x+d/r*a.rect.width,l=new Map;e.events.forEach(d=>{const f=l.get(d.stage)??[];f.push(d.at-e.start),l.set(d.stage,f)});const c=t.slice(0,-1).map((d,f)=>{const g=t[f+1],_=(l.get(d.stage)??[]).filter(m=>m<=g.offset),p=_.length>0?_[_.length-1]:d.offset;return{index:f,from:p,to:g.offset,seconds:g.offset-p}}),h=c.reduce((d,f)=>f.seconds>d.seconds?f:d,{index:-1,from:0,to:0,seconds:0}),u=h.seconds>.5?h:null;if(u){const d=o(u.from),f=o(u.to);n.fillStyle=`${z.warn}18`,n.fillRect(d,a.rect.y,Math.max(2,f-d),a.rect.height)}c.forEach(d=>{const f=d.index===h.index;n.strokeStyle=f?z.warn:z.border,n.lineWidth=f?2:1,n.beginPath(),n.moveTo(o(d.from),a.rowY(d.index)),n.lineTo(o(d.to),a.rowY(d.index+1)),n.stroke()}),t.forEach((d,f)=>{const g=a.rowY(f);n.fillStyle=z.gradient,(l.get(d.stage)??[]).forEach(_=>{const p=o(_);n.fillRect(p-1.5,g-9,3,18)}),n.font="12px 'JetBrains Mono', monospace",n.textAlign="left",n.textBaseline="middle",n.fillStyle=z.text_secondary,n.fillText(`${d.events}`,a.rect.x+a.rect.width+12,g)}),u&&(n.font="13px 'JetBrains Mono', monospace",n.textAlign="center",n.textBaseline="alphabetic",n.fillStyle=z.warn,n.fillText(`${u.seconds.toFixed(1)} s of silence`,(o(u.from)+o(u.to))/2,a.rect.y+22)),Fn(n,s,`${t.length} stages · ${e.events.length} events · ${r.toFixed(1)} s from the first word to the last`),this.drawn=!0}}class ow{constructor(){I(this,"id","uncertainty");I(this,"name","The uncertainty");I(this,"caption","Each cell's mean and the margin the gate asks for, against the chance level.");I(this,"visible",!1);I(this,"drawn",!1)}enter(){this.visible=!0,Xe.show(),this.draw()}exit(){this.visible=!1,Xe.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}sigma(){const e=Ee.gate;return e&&typeof e.superiority_margin_sigma=="number"?e.superiority_margin_sigma:2}intervals(){const e=Ee.axes,t=Ee.chance,n=this.sigma(),s=zh(Ee.aggregates,e),r=dl(s,e);return s.filter(a=>a.acc.length>0).map(a=>{const o=a.acc.length,l=a.acc.reduce((d,f)=>d+f,0)/o,c=a.acc.reduce((d,f)=>d+(f-l)**2,0)/Math.max(1,o-1),h=o>1?Math.sqrt(c/o):0,u=n*h;return{cell:a,label:za(a,e,r),color:Xt[a.coordinate.credit]??z.gradient,mean:l,margin:u,lower:l-u,upper:l+u,threshold:t+u}}).sort((a,o)=>o.mean-a.mean)}draw(){const e=this.intervals();if(e.length===0){this.drawn=!1;return}const t=Xe.begin(),n=Xe.area(),s=Ee.chance,r=this.sigma(),a=Math.max(s,...e.map(h=>Math.max(h.upper,h.threshold))),o=Sl(t,n,{xMin:0,xMax:a*1.12,rows:e.map(h=>h.label),title:"The uncertainty",subtitle:"each cell's mean, and the margin the gate asks for",xLabel:"accuracy"}),l=h=>o.rect.x+h/(o.xMax||1)*o.rect.width,c=l(s);t.strokeStyle=z.chance_line,t.lineWidth=1.5,t.setLineDash([6,5]),t.beginPath(),t.moveTo(c,o.rect.y),t.lineTo(c,o.rect.y+o.rect.height),t.stroke(),t.setLineDash([]),t.font="11px 'JetBrains Mono', monospace",t.textAlign="left",t.textBaseline="alphabetic",t.fillStyle=z.chance_line,t.fillText("chance",c+6,o.rect.y+14),e.forEach((h,u)=>{const d=o.rowY(u),f=h.lower>s;t.strokeStyle=h.color,t.lineWidth=3,t.beginPath(),t.moveTo(l(h.lower),d),t.lineTo(l(h.upper),d),t.stroke(),t.strokeStyle=f?z.ok:z.warn,t.lineWidth=2,t.beginPath(),t.moveTo(l(h.threshold),d-11),t.lineTo(l(h.threshold),d+11),t.stroke(),t.fillStyle=h.color,t.beginPath(),t.arc(l(h.mean),d,5,0,Math.PI*2),t.fill(),t.textAlign="left",t.textBaseline="middle",t.font="12px 'JetBrains Mono', monospace",t.fillStyle=f?z.ok:z.warn,t.fillText(f?"clears chance":"not yet separable",o.rect.x+o.rect.width+12,d)}),Fn(t,n,`the bar is ±${r}·SE · the tick is the threshold each cell has to clear · a claim needs ${Ee.requiredSeeds} seeds per cell`),this.drawn=!0}}class lw{constructor(){I(this,"id","space");I(this,"name","Space");I(this,"caption","The declared space: the gaps as cages, the measured cells as pillars, the refusals as crosses.")}enter(){Vs.show()}exit(){Vs.hide()}refresh(e){Vs.refreshView(e)}ready(){return Vs.hasMeasured()}}class cw{constructor(){I(this,"name","ViewSwitcher");I(this,"views",[]);I(this,"active",null);I(this,"selector",null);I(this,"captionElement",null);I(this,"section",null);I(this,"keys",new Map);I(this,"keyOf",new Map);I(this,"onKeyDown",e=>{if(e.metaKey||e.ctrlKey||e.altKey)return;const t=e.target;if(t&&["INPUT","SELECT","TEXTAREA"].includes(t.tagName))return;const n=e.key.toLowerCase();if(n===lm){this.cycle();return}const s=this.keys.get(n);s&&this.show(s.id)});this.views=[new lw,new rw,new jb,new Qb,new Ob,new tw,new iw,new Nb,new ow,new aw,new Jb,new Fb,new Yb,new Xb,new Zb,new Hb,new Vb,new Gb,new Wb]}async init(){window.addEventListener("keydown",this.onKeyDown),Ee.onChange(e=>{var t;return(t=this.active)==null?void 0:t.refresh(e)}),this.buildKeys(),this.buildSection(),this.attachSection(),this.show(this.views[0].id),console.log("[ViewSwitcher] Initialized")}async destroy(){var e,t;window.removeEventListener("keydown",this.onKeyDown),(e=this.active)==null||e.exit(),this.active=null,(t=this.section)==null||t.remove(),this.section=null}get activeId(){var e;return((e=this.active)==null?void 0:e.id)??null}isReady(e){const t=this.views.find(n=>n.id===e);return t?t.ready():!1}show(e){var n;const t=this.views.find(s=>s.id===e);!t||t===this.active||((n=this.active)==null||n.exit(),this.active=t,t.enter(),this.updateSelector(),this.updateLegend())}cycle(){if(this.views.length===0)return;const e=this.views.findIndex(n=>n===this.active),t=this.views[(e+1)%this.views.length];this.show(t.id)}buildKeys(){this.keys.clear(),this.keyOf.clear(),this.views.forEach((e,t)=>{const n=t<9?String(t+1):"";n&&(this.keys.set(n,e),this.keyOf.set(e.id,n)),e.key&&!Ef.has(e.key)&&(this.keys.set(e.key,e),this.keyOf.set(e.id,e.key))})}optionLabel(e){const t=this.keyOf.get(e.id);return t?`${t.toUpperCase()} · ${e.name}`:e.name}keyHint(){const e=[],t=[];this.views.forEach((s,r)=>{if(r<9){e.push(String(r+1));return}s.key&&!Ef.has(s.key)&&t.push(s.key.toUpperCase())});const n=["V cycles"];return e.length>0&&n.push(`${e[0]}–${e[e.length-1]} pick`),t.length>0&&n.push(`${t.join(" ")} pick`),n.join(" · ")}buildSection(){const e=document.createElement("div");e.id="legend-view-section",e.style.cssText="margin-bottom: 12px;";const t=document.createElement("div");t.textContent="View",t.style.cssText="font-weight: 600; margin-bottom: 8px;",e.appendChild(t);const n=document.createElement("select");n.id="view-picker",n.style.cssText=`
      width: 100%;
      background: var(--bg-tertiary);
      color: var(--text-primary);
      border: 1px solid var(--border);
      border-radius: 4px;
      font-size: 11px;
      padding: 2px 4px;
    `,this.views.forEach(a=>{const o=document.createElement("option");o.value=a.id,o.textContent=this.optionLabel(a),n.appendChild(o)}),n.addEventListener("change",()=>this.show(n.value)),e.appendChild(n),this.selector=n;const s=document.createElement("div");s.id="view-caption",s.style.cssText="font-size: 11px; color: var(--text-secondary); margin-top: 8px;",e.appendChild(s),this.captionElement=s;const r=document.createElement("div");r.textContent=this.keyHint(),r.style.cssText="font-size: 10px; color: var(--text-muted); margin-top: 6px;",e.appendChild(r),this.section=e}attachSection(e=0){const t=document.getElementById("legend-view");if(!t){e<50&&window.setTimeout(()=>this.attachSection(e+1),100);return}this.section&&this.section.parentElement!==t&&t.appendChild(this.section),this.updateSelector(),this.updateLegend()}updateSelector(){!this.selector||!this.active||(this.selector.value=this.active.id)}updateLegend(){if(!this.active)return;const e=document.getElementById("legend-title");e&&(e.textContent=this.active.name);const t=document.getElementById("legend-marks");t&&(t.style.display=this.active.id==="space"?"":"none"),this.captionElement&&(this.captionElement.textContent=this.active.caption)}}const hm=new cw;Ki.register(hm);const hw=/swiftshader|llvmpipe|software|basic render/i;function uw(){const i=dw();return{software:i,fps:i?12:60,shadows:!i,antialias:!i}}function dw(){try{const i=document.createElement("canvas"),e=i.getContext("webgl2")??i.getContext("webgl");if(!e)return!0;const t=e.getExtension("WEBGL_debug_renderer_info"),n=String(t?e.getParameter(t.UNMASKED_RENDERER_WEBGL):e.getParameter(e.RENDERER));return hw.test(n)}catch{return!0}}window.addEventListener("error",i=>{var e;console.error("[Global Error]",i.error),dm(((e=i.error)==null?void 0:e.message)||"Unknown error")});window.addEventListener("unhandledrejection",i=>{var e;console.error("[Unhandled Rejection]",i.reason),dm(((e=i.reason)==null?void 0:e.message)||"Unhandled promise rejection")});let Vi=null,ls=null;function um(i="Initializing dashboard..."){const e=document.getElementById("ui-overlay");e&&(Vi=document.createElement("div"),Vi.id="global-loading",Vi.style.cssText=`
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
  `,Vi.innerHTML=`
    <div style="
      width: 48px;
      height: 48px;
      border: 3px solid var(--border);
      border-top-color: ${z.gradient};
      border-radius: 50%;
      animation: spin 1s linear infinite;
    "></div>
    <div style="font-size: 14px; color: var(--text-primary);">${i}</div>
    <style>
      @keyframes spin { to { transform: rotate(360deg); } }
    </style>
  `,e.appendChild(Vi))}function If(){Vi==null||Vi.remove(),Vi=null}function dm(i){const e=document.getElementById("ui-overlay");e&&(ls=document.createElement("div"),ls.id="global-error",ls.style.cssText=`
    position: fixed;
    top: 20px;
    right: 20px;
    background: ${z.error}22;
    border: 1px solid ${z.error}88;
    border-radius: 8px;
    padding: 16px 24px;
    color: ${z.error};
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    z-index: 1000;
    max-width: 400px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    display: flex;
    align-items: center;
    gap: 12px;
  `,ls.innerHTML=`
    <span>✗</span>
    <span>${i}</span>
    <button onclick="this.parentElement.remove()" style="
      background: none;
      border: none;
      color: ${z.error};
      font-size: 18px;
      cursor: pointer;
      line-height: 1;
      padding: 0 4px;
    ">&times;</button>
  `,e.appendChild(ls),setTimeout(()=>ls==null?void 0:ls.remove(),1e4))}jr.connect();um("Connecting to dashboard...");jr.waitForConnection(15e3).then(i=>{i?If():(um("Connection timeout — retrying..."),jr.onStateChange(e=>{e==="connected"&&If()}))});const fw=new Map(Object.entries(om).map(([i,e])=>[e,i]));window.addEventListener("keydown",i=>{if(i.metaKey||i.ctrlKey||i.altKey)return;const e=i.key.toLowerCase(),t=fw.get(e);if(t){eu.showTab(t);return}e===$o.hud&&Ml.toggle(),e===$o.rail&&tu.toggle(),e===$o.caption&&nu.toggle()});const pw=document.getElementById("dashboard-canvas"),oa=uw(),ti=new dp({canvas:pw,antialias:oa.antialias,alpha:!0,powerPreference:"high-performance"});ti.setSize(window.innerWidth,window.innerHeight);ti.setPixelRatio(oa.software?1:Math.min(window.devicePixelRatio,2));ti.shadowMap.enabled=oa.shadows;ti.shadowMap.type=Nf;ti.toneMapping=Of;ti.toneMappingExposure=1.2;const Zi=new Uh;Zi.background=new nt(658964);Zi.fog=new Ih(658964,.015);const ys=new bn(60,window.innerWidth/window.innerHeight,.1,200);ys.position.set(3.3,4.4,8.8);ys.lookAt(0,1,.1);const Pi=new mM(ys,ti.domElement);Pi.target.set(0,1,.1);Pi.enableDamping=!0;Pi.dampingFactor=.05;Pi.enablePan=!0;Pi.minDistance=5;Pi.maxDistance=80;Pi.maxPolarAngle=Math.PI/2-.05;xM({scene:Zi,camera:ys,renderer:ti,controls:Pi});const mw=new rM(4473958,.6);Zi.add(mw);const mi=new sM(16777215,1.2);mi.position.set(10,20,10);mi.castShadow=oa.shadows;mi.shadow.mapSize.width=2048;mi.shadow.mapSize.height=2048;mi.shadow.camera.near=1;mi.shadow.camera.far=50;mi.shadow.camera.left=-20;mi.shadow.camera.right=20;mi.shadow.camera.top=20;mi.shadow.camera.bottom=-20;Zi.add(mi);const gw=new tM(8956671,2236979,.5);Zi.add(gw);const su=new oM(8,8,2371648,1449256);su.position.y=-.01;const fm=su.material;fm.transparent=!0;fm.opacity=.35;Zi.add(su);function _w(){ys.aspect=window.innerWidth/window.innerHeight,ys.updateProjectionMatrix(),ti.setSize(window.innerWidth,window.innerHeight),ti.setPixelRatio(oa.software?1:Math.min(window.devicePixelRatio,2))}window.addEventListener("resize",_w);const xw=1e3/oa.fps;let Tc=0;function pm(i){if(requestAnimationFrame(pm),i-Tc<xw)return;const e=(i-Tc)/1e3;Tc=i,Pi.update(),Vs.update(e),Ml.update(e),ti.render(Zi,ys)}requestAnimationFrame(pm);window.__DASHBOARD__={scene:Zi,camera:ys,renderer:ti,controls:Pi,discoveryMap:Vs,cellDrawer:yp,plotter:eu,liveRail:tu,caption:nu,hud:Ml,viewSwitcher:hm,wsClient:jr,router:jt};console.log("🚀 Computronium Dashboard initialized");
//# sourceMappingURL=dashboard.js.map
