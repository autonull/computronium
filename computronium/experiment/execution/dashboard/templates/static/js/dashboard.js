var ng=Object.defineProperty;var ig=(i,e,t)=>e in i?ng(i,e,{enumerable:!0,configurable:!0,writable:!0,value:t}):i[e]=t;var M=(i,e,t)=>ig(i,typeof e!="symbol"?e+"":e,t);/**
 * @license
 * Copyright 2010-2024 Three.js Authors
 * SPDX-License-Identifier: MIT
 */const Vh="168",gr={ROTATE:0,DOLLY:1,PAN:2},vr={ROTATE:0,PAN:1,DOLLY_PAN:2,DOLLY_ROTATE:3},sg=0,Vu=1,rg=2,Qf=1,ep=2,ji=3,Ms=0,Vn=1,Fn=2,ys=0,$r=1,Gu=2,Wu=3,$u=4,ag=5,$s=100,og=101,lg=102,cg=103,hg=104,ug=200,dg=201,fg=202,pg=203,qc=204,Xc=205,mg=206,gg=207,vg=208,xg=209,_g=210,yg=211,Sg=212,bg=213,Mg=214,wg=0,Eg=1,Tg=2,cl=3,Ag=4,Cg=5,Rg=6,Pg=7,tp=0,Lg=1,Dg=2,Ss=0,Ig=1,Ug=2,Ng=3,np=4,Og=5,Fg=6,kg=7,ip=300,Qr=301,ea=302,Yc=303,jc=304,bl=306,Kc=1e3,Ys=1001,Jc=1002,ai=1003,Bg=1004,_o=1005,vi=1006,tc=1007,js=1008,ss=1009,sp=1010,rp=1011,Za=1012,Gh=1013,Zs=1014,Ji=1015,so=1016,Wh=1017,$h=1018,ta=1020,ap=35902,op=1021,lp=1022,yi=1023,cp=1024,hp=1025,qr=1026,na=1027,up=1028,qh=1029,dp=1030,Xh=1031,Yh=1033,nl=33776,il=33777,sl=33778,rl=33779,Zc=35840,Qc=35841,eh=35842,th=35843,nh=36196,ih=37492,sh=37496,rh=37808,ah=37809,oh=37810,lh=37811,ch=37812,hh=37813,uh=37814,dh=37815,fh=37816,ph=37817,mh=37818,gh=37819,vh=37820,xh=37821,al=36492,_h=36494,yh=36495,fp=36283,Sh=36284,bh=36285,Mh=36286,zg=3200,Hg=3201,pp=0,Vg=1,_s="",Ui="srgb",Cs="srgb-linear",jh="display-p3",Ml="display-p3-linear",hl="linear",Bt="srgb",ul="rec709",dl="p3",xr=7680,qu=519,Gg=512,Wg=513,$g=514,mp=515,qg=516,Xg=517,Yg=518,jg=519,wh=35044,Xu="300 es",Zi=2e3,fl=2001;let pa=class{addEventListener(e,t){this._listeners===void 0&&(this._listeners={});const n=this._listeners;n[e]===void 0&&(n[e]=[]),n[e].indexOf(t)===-1&&n[e].push(t)}hasEventListener(e,t){if(this._listeners===void 0)return!1;const n=this._listeners;return n[e]!==void 0&&n[e].indexOf(t)!==-1}removeEventListener(e,t){if(this._listeners===void 0)return;const s=this._listeners[e];if(s!==void 0){const r=s.indexOf(t);r!==-1&&s.splice(r,1)}}dispatchEvent(e){if(this._listeners===void 0)return;const n=this._listeners[e.type];if(n!==void 0){e.target=this;const s=n.slice(0);for(let r=0,a=s.length;r<a;r++)s[r].call(this,e);e.target=null}}};const Tn=["00","01","02","03","04","05","06","07","08","09","0a","0b","0c","0d","0e","0f","10","11","12","13","14","15","16","17","18","19","1a","1b","1c","1d","1e","1f","20","21","22","23","24","25","26","27","28","29","2a","2b","2c","2d","2e","2f","30","31","32","33","34","35","36","37","38","39","3a","3b","3c","3d","3e","3f","40","41","42","43","44","45","46","47","48","49","4a","4b","4c","4d","4e","4f","50","51","52","53","54","55","56","57","58","59","5a","5b","5c","5d","5e","5f","60","61","62","63","64","65","66","67","68","69","6a","6b","6c","6d","6e","6f","70","71","72","73","74","75","76","77","78","79","7a","7b","7c","7d","7e","7f","80","81","82","83","84","85","86","87","88","89","8a","8b","8c","8d","8e","8f","90","91","92","93","94","95","96","97","98","99","9a","9b","9c","9d","9e","9f","a0","a1","a2","a3","a4","a5","a6","a7","a8","a9","aa","ab","ac","ad","ae","af","b0","b1","b2","b3","b4","b5","b6","b7","b8","b9","ba","bb","bc","bd","be","bf","c0","c1","c2","c3","c4","c5","c6","c7","c8","c9","ca","cb","cc","cd","ce","cf","d0","d1","d2","d3","d4","d5","d6","d7","d8","d9","da","db","dc","dd","de","df","e0","e1","e2","e3","e4","e5","e6","e7","e8","e9","ea","eb","ec","ed","ee","ef","f0","f1","f2","f3","f4","f5","f6","f7","f8","f9","fa","fb","fc","fd","fe","ff"];let Yu=1234567;const Xr=Math.PI/180,Qa=180/Math.PI;function Qi(){const i=Math.random()*4294967295|0,e=Math.random()*4294967295|0,t=Math.random()*4294967295|0,n=Math.random()*4294967295|0;return(Tn[i&255]+Tn[i>>8&255]+Tn[i>>16&255]+Tn[i>>24&255]+"-"+Tn[e&255]+Tn[e>>8&255]+"-"+Tn[e>>16&15|64]+Tn[e>>24&255]+"-"+Tn[t&63|128]+Tn[t>>8&255]+"-"+Tn[t>>16&255]+Tn[t>>24&255]+Tn[n&255]+Tn[n>>8&255]+Tn[n>>16&255]+Tn[n>>24&255]).toLowerCase()}function Cn(i,e,t){return Math.max(e,Math.min(t,i))}function Kh(i,e){return(i%e+e)%e}function Kg(i,e,t,n,s){return n+(i-e)*(s-n)/(t-e)}function Jg(i,e,t){return i!==e?(t-i)/(e-i):0}function qa(i,e,t){return(1-t)*i+t*e}function Zg(i,e,t,n){return qa(i,e,1-Math.exp(-t*n))}function Qg(i,e=1){return e-Math.abs(Kh(i,e*2)-e)}function ev(i,e,t){return i<=e?0:i>=t?1:(i=(i-e)/(t-e),i*i*(3-2*i))}function tv(i,e,t){return i<=e?0:i>=t?1:(i=(i-e)/(t-e),i*i*i*(i*(i*6-15)+10))}function nv(i,e){return i+Math.floor(Math.random()*(e-i+1))}function iv(i,e){return i+Math.random()*(e-i)}function sv(i){return i*(.5-Math.random())}function rv(i){i!==void 0&&(Yu=i);let e=Yu+=1831565813;return e=Math.imul(e^e>>>15,e|1),e^=e+Math.imul(e^e>>>7,e|61),((e^e>>>14)>>>0)/4294967296}function av(i){return i*Xr}function ov(i){return i*Qa}function lv(i){return(i&i-1)===0&&i!==0}function cv(i){return Math.pow(2,Math.ceil(Math.log(i)/Math.LN2))}function hv(i){return Math.pow(2,Math.floor(Math.log(i)/Math.LN2))}function uv(i,e,t,n,s){const r=Math.cos,a=Math.sin,o=r(t/2),l=a(t/2),c=r((e+n)/2),h=a((e+n)/2),u=r((e-n)/2),d=a((e-n)/2),f=r((n-e)/2),g=a((n-e)/2);switch(s){case"XYX":i.set(o*h,l*u,l*d,o*c);break;case"YZY":i.set(l*d,o*h,l*u,o*c);break;case"ZXZ":i.set(l*u,l*d,o*h,o*c);break;case"XZX":i.set(o*h,l*g,l*f,o*c);break;case"YXY":i.set(l*f,o*h,l*g,o*c);break;case"ZYZ":i.set(l*g,l*f,o*h,o*c);break;default:console.warn("THREE.MathUtils: .setQuaternionFromProperEuler() encountered an unknown order: "+s)}}function xi(i,e){switch(e.constructor){case Float32Array:return i;case Uint32Array:return i/4294967295;case Uint16Array:return i/65535;case Uint8Array:return i/255;case Int32Array:return Math.max(i/2147483647,-1);case Int16Array:return Math.max(i/32767,-1);case Int8Array:return Math.max(i/127,-1);default:throw new Error("Invalid component type.")}}function At(i,e){switch(e.constructor){case Float32Array:return i;case Uint32Array:return Math.round(i*4294967295);case Uint16Array:return Math.round(i*65535);case Uint8Array:return Math.round(i*255);case Int32Array:return Math.round(i*2147483647);case Int16Array:return Math.round(i*32767);case Int8Array:return Math.round(i*127);default:throw new Error("Invalid component type.")}}const dv={DEG2RAD:Xr,RAD2DEG:Qa,generateUUID:Qi,clamp:Cn,euclideanModulo:Kh,mapLinear:Kg,inverseLerp:Jg,lerp:qa,damp:Zg,pingpong:Qg,smoothstep:ev,smootherstep:tv,randInt:nv,randFloat:iv,randFloatSpread:sv,seededRandom:rv,degToRad:av,radToDeg:ov,isPowerOfTwo:lv,ceilPowerOfTwo:cv,floorPowerOfTwo:hv,setQuaternionFromProperEuler:uv,normalize:At,denormalize:xi};class Xe{constructor(e=0,t=0){Xe.prototype.isVector2=!0,this.x=e,this.y=t}get width(){return this.x}set width(e){this.x=e}get height(){return this.y}set height(e){this.y=e}set(e,t){return this.x=e,this.y=t,this}setScalar(e){return this.x=e,this.y=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y)}copy(e){return this.x=e.x,this.y=e.y,this}add(e){return this.x+=e.x,this.y+=e.y,this}addScalar(e){return this.x+=e,this.y+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this}subScalar(e){return this.x-=e,this.y-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this}multiply(e){return this.x*=e.x,this.y*=e.y,this}multiplyScalar(e){return this.x*=e,this.y*=e,this}divide(e){return this.x/=e.x,this.y/=e.y,this}divideScalar(e){return this.multiplyScalar(1/e)}applyMatrix3(e){const t=this.x,n=this.y,s=e.elements;return this.x=s[0]*t+s[3]*n+s[6],this.y=s[1]*t+s[4]*n+s[7],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this}negate(){return this.x=-this.x,this.y=-this.y,this}dot(e){return this.x*e.x+this.y*e.y}cross(e){return this.x*e.y-this.y*e.x}lengthSq(){return this.x*this.x+this.y*this.y}length(){return Math.sqrt(this.x*this.x+this.y*this.y)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)}normalize(){return this.divideScalar(this.length()||1)}angle(){return Math.atan2(-this.y,-this.x)+Math.PI}angleTo(e){const t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;const n=this.dot(e)/t;return Math.acos(Cn(n,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){const t=this.x-e.x,n=this.y-e.y;return t*t+n*n}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this}equals(e){return e.x===this.x&&e.y===this.y}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this}rotateAround(e,t){const n=Math.cos(t),s=Math.sin(t),r=this.x-e.x,a=this.y-e.y;return this.x=r*n-a*s+e.x,this.y=r*s+a*n+e.y,this}random(){return this.x=Math.random(),this.y=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y}}class ot{constructor(e,t,n,s,r,a,o,l,c){ot.prototype.isMatrix3=!0,this.elements=[1,0,0,0,1,0,0,0,1],e!==void 0&&this.set(e,t,n,s,r,a,o,l,c)}set(e,t,n,s,r,a,o,l,c){const h=this.elements;return h[0]=e,h[1]=s,h[2]=o,h[3]=t,h[4]=r,h[5]=l,h[6]=n,h[7]=a,h[8]=c,this}identity(){return this.set(1,0,0,0,1,0,0,0,1),this}copy(e){const t=this.elements,n=e.elements;return t[0]=n[0],t[1]=n[1],t[2]=n[2],t[3]=n[3],t[4]=n[4],t[5]=n[5],t[6]=n[6],t[7]=n[7],t[8]=n[8],this}extractBasis(e,t,n){return e.setFromMatrix3Column(this,0),t.setFromMatrix3Column(this,1),n.setFromMatrix3Column(this,2),this}setFromMatrix4(e){const t=e.elements;return this.set(t[0],t[4],t[8],t[1],t[5],t[9],t[2],t[6],t[10]),this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){const n=e.elements,s=t.elements,r=this.elements,a=n[0],o=n[3],l=n[6],c=n[1],h=n[4],u=n[7],d=n[2],f=n[5],g=n[8],v=s[0],p=s[3],m=s[6],S=s[1],_=s[4],b=s[7],I=s[2],A=s[5],R=s[8];return r[0]=a*v+o*S+l*I,r[3]=a*p+o*_+l*A,r[6]=a*m+o*b+l*R,r[1]=c*v+h*S+u*I,r[4]=c*p+h*_+u*A,r[7]=c*m+h*b+u*R,r[2]=d*v+f*S+g*I,r[5]=d*p+f*_+g*A,r[8]=d*m+f*b+g*R,this}multiplyScalar(e){const t=this.elements;return t[0]*=e,t[3]*=e,t[6]*=e,t[1]*=e,t[4]*=e,t[7]*=e,t[2]*=e,t[5]*=e,t[8]*=e,this}determinant(){const e=this.elements,t=e[0],n=e[1],s=e[2],r=e[3],a=e[4],o=e[5],l=e[6],c=e[7],h=e[8];return t*a*h-t*o*c-n*r*h+n*o*l+s*r*c-s*a*l}invert(){const e=this.elements,t=e[0],n=e[1],s=e[2],r=e[3],a=e[4],o=e[5],l=e[6],c=e[7],h=e[8],u=h*a-o*c,d=o*l-h*r,f=c*r-a*l,g=t*u+n*d+s*f;if(g===0)return this.set(0,0,0,0,0,0,0,0,0);const v=1/g;return e[0]=u*v,e[1]=(s*c-h*n)*v,e[2]=(o*n-s*a)*v,e[3]=d*v,e[4]=(h*t-s*l)*v,e[5]=(s*r-o*t)*v,e[6]=f*v,e[7]=(n*l-c*t)*v,e[8]=(a*t-n*r)*v,this}transpose(){let e;const t=this.elements;return e=t[1],t[1]=t[3],t[3]=e,e=t[2],t[2]=t[6],t[6]=e,e=t[5],t[5]=t[7],t[7]=e,this}getNormalMatrix(e){return this.setFromMatrix4(e).invert().transpose()}transposeIntoArray(e){const t=this.elements;return e[0]=t[0],e[1]=t[3],e[2]=t[6],e[3]=t[1],e[4]=t[4],e[5]=t[7],e[6]=t[2],e[7]=t[5],e[8]=t[8],this}setUvTransform(e,t,n,s,r,a,o){const l=Math.cos(r),c=Math.sin(r);return this.set(n*l,n*c,-n*(l*a+c*o)+a+e,-s*c,s*l,-s*(-c*a+l*o)+o+t,0,0,1),this}scale(e,t){return this.premultiply(nc.makeScale(e,t)),this}rotate(e){return this.premultiply(nc.makeRotation(-e)),this}translate(e,t){return this.premultiply(nc.makeTranslation(e,t)),this}makeTranslation(e,t){return e.isVector2?this.set(1,0,e.x,0,1,e.y,0,0,1):this.set(1,0,e,0,1,t,0,0,1),this}makeRotation(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,-n,0,n,t,0,0,0,1),this}makeScale(e,t){return this.set(e,0,0,0,t,0,0,0,1),this}equals(e){const t=this.elements,n=e.elements;for(let s=0;s<9;s++)if(t[s]!==n[s])return!1;return!0}fromArray(e,t=0){for(let n=0;n<9;n++)this.elements[n]=e[n+t];return this}toArray(e=[],t=0){const n=this.elements;return e[t]=n[0],e[t+1]=n[1],e[t+2]=n[2],e[t+3]=n[3],e[t+4]=n[4],e[t+5]=n[5],e[t+6]=n[6],e[t+7]=n[7],e[t+8]=n[8],e}clone(){return new this.constructor().fromArray(this.elements)}}const nc=new ot;function gp(i){for(let e=i.length-1;e>=0;--e)if(i[e]>=65535)return!0;return!1}function pl(i){return document.createElementNS("http://www.w3.org/1999/xhtml",i)}function fv(){const i=pl("canvas");return i.style.display="block",i}const ju={};function Yr(i){i in ju||(ju[i]=!0,console.warn(i))}function pv(i,e,t){return new Promise(function(n,s){function r(){switch(i.clientWaitSync(e,i.SYNC_FLUSH_COMMANDS_BIT,0)){case i.WAIT_FAILED:s();break;case i.TIMEOUT_EXPIRED:setTimeout(r,t);break;default:n()}}setTimeout(r,t)})}const Ku=new ot().set(.8224621,.177538,0,.0331941,.9668058,0,.0170827,.0723974,.9105199),Ju=new ot().set(1.2249401,-.2249404,0,-.0420569,1.0420571,0,-.0196376,-.0786361,1.0982735),Ca={[Cs]:{transfer:hl,primaries:ul,luminanceCoefficients:[.2126,.7152,.0722],toReference:i=>i,fromReference:i=>i},[Ui]:{transfer:Bt,primaries:ul,luminanceCoefficients:[.2126,.7152,.0722],toReference:i=>i.convertSRGBToLinear(),fromReference:i=>i.convertLinearToSRGB()},[Ml]:{transfer:hl,primaries:dl,luminanceCoefficients:[.2289,.6917,.0793],toReference:i=>i.applyMatrix3(Ju),fromReference:i=>i.applyMatrix3(Ku)},[jh]:{transfer:Bt,primaries:dl,luminanceCoefficients:[.2289,.6917,.0793],toReference:i=>i.convertSRGBToLinear().applyMatrix3(Ju),fromReference:i=>i.applyMatrix3(Ku).convertLinearToSRGB()}},mv=new Set([Cs,Ml]),wt={enabled:!0,_workingColorSpace:Cs,get workingColorSpace(){return this._workingColorSpace},set workingColorSpace(i){if(!mv.has(i))throw new Error(`Unsupported working color space, "${i}".`);this._workingColorSpace=i},convert:function(i,e,t){if(this.enabled===!1||e===t||!e||!t)return i;const n=Ca[e].toReference,s=Ca[t].fromReference;return s(n(i))},fromWorkingColorSpace:function(i,e){return this.convert(i,this._workingColorSpace,e)},toWorkingColorSpace:function(i,e){return this.convert(i,e,this._workingColorSpace)},getPrimaries:function(i){return Ca[i].primaries},getTransfer:function(i){return i===_s?hl:Ca[i].transfer},getLuminanceCoefficients:function(i,e=this._workingColorSpace){return i.fromArray(Ca[e].luminanceCoefficients)}};function jr(i){return i<.04045?i*.0773993808:Math.pow(i*.9478672986+.0521327014,2.4)}function ic(i){return i<.0031308?i*12.92:1.055*Math.pow(i,.41666)-.055}let _r;class gv{static getDataURL(e){if(/^data:/i.test(e.src)||typeof HTMLCanvasElement>"u")return e.src;let t;if(e instanceof HTMLCanvasElement)t=e;else{_r===void 0&&(_r=pl("canvas")),_r.width=e.width,_r.height=e.height;const n=_r.getContext("2d");e instanceof ImageData?n.putImageData(e,0,0):n.drawImage(e,0,0,e.width,e.height),t=_r}return t.width>2048||t.height>2048?(console.warn("THREE.ImageUtils.getDataURL: Image converted to jpg for performance reasons",e),t.toDataURL("image/jpeg",.6)):t.toDataURL("image/png")}static sRGBToLinear(e){if(typeof HTMLImageElement<"u"&&e instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&e instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&e instanceof ImageBitmap){const t=pl("canvas");t.width=e.width,t.height=e.height;const n=t.getContext("2d");n.drawImage(e,0,0,e.width,e.height);const s=n.getImageData(0,0,e.width,e.height),r=s.data;for(let a=0;a<r.length;a++)r[a]=jr(r[a]/255)*255;return n.putImageData(s,0,0),t}else if(e.data){const t=e.data.slice(0);for(let n=0;n<t.length;n++)t instanceof Uint8Array||t instanceof Uint8ClampedArray?t[n]=Math.floor(jr(t[n]/255)*255):t[n]=jr(t[n]);return{data:t,width:e.width,height:e.height}}else return console.warn("THREE.ImageUtils.sRGBToLinear(): Unsupported image type. No color space conversion applied."),e}}let vv=0;class vp{constructor(e=null){this.isSource=!0,Object.defineProperty(this,"id",{value:vv++}),this.uuid=Qi(),this.data=e,this.dataReady=!0,this.version=0}set needsUpdate(e){e===!0&&this.version++}toJSON(e){const t=e===void 0||typeof e=="string";if(!t&&e.images[this.uuid]!==void 0)return e.images[this.uuid];const n={uuid:this.uuid,url:""},s=this.data;if(s!==null){let r;if(Array.isArray(s)){r=[];for(let a=0,o=s.length;a<o;a++)s[a].isDataTexture?r.push(sc(s[a].image)):r.push(sc(s[a]))}else r=sc(s);n.url=r}return t||(e.images[this.uuid]=n),n}}function sc(i){return typeof HTMLImageElement<"u"&&i instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&i instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&i instanceof ImageBitmap?gv.getDataURL(i):i.data?{data:Array.from(i.data),width:i.width,height:i.height,type:i.data.constructor.name}:(console.warn("THREE.Texture: Unable to serialize Texture."),{})}let xv=0;class Bn extends pa{constructor(e=Bn.DEFAULT_IMAGE,t=Bn.DEFAULT_MAPPING,n=Ys,s=Ys,r=vi,a=js,o=yi,l=ss,c=Bn.DEFAULT_ANISOTROPY,h=_s){super(),this.isTexture=!0,Object.defineProperty(this,"id",{value:xv++}),this.uuid=Qi(),this.name="",this.source=new vp(e),this.mipmaps=[],this.mapping=t,this.channel=0,this.wrapS=n,this.wrapT=s,this.magFilter=r,this.minFilter=a,this.anisotropy=c,this.format=o,this.internalFormat=null,this.type=l,this.offset=new Xe(0,0),this.repeat=new Xe(1,1),this.center=new Xe(0,0),this.rotation=0,this.matrixAutoUpdate=!0,this.matrix=new ot,this.generateMipmaps=!0,this.premultiplyAlpha=!1,this.flipY=!0,this.unpackAlignment=4,this.colorSpace=h,this.userData={},this.version=0,this.onUpdate=null,this.isRenderTargetTexture=!1,this.pmremVersion=0}get image(){return this.source.data}set image(e=null){this.source.data=e}updateMatrix(){this.matrix.setUvTransform(this.offset.x,this.offset.y,this.repeat.x,this.repeat.y,this.rotation,this.center.x,this.center.y)}clone(){return new this.constructor().copy(this)}copy(e){return this.name=e.name,this.source=e.source,this.mipmaps=e.mipmaps.slice(0),this.mapping=e.mapping,this.channel=e.channel,this.wrapS=e.wrapS,this.wrapT=e.wrapT,this.magFilter=e.magFilter,this.minFilter=e.minFilter,this.anisotropy=e.anisotropy,this.format=e.format,this.internalFormat=e.internalFormat,this.type=e.type,this.offset.copy(e.offset),this.repeat.copy(e.repeat),this.center.copy(e.center),this.rotation=e.rotation,this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrix.copy(e.matrix),this.generateMipmaps=e.generateMipmaps,this.premultiplyAlpha=e.premultiplyAlpha,this.flipY=e.flipY,this.unpackAlignment=e.unpackAlignment,this.colorSpace=e.colorSpace,this.userData=JSON.parse(JSON.stringify(e.userData)),this.needsUpdate=!0,this}toJSON(e){const t=e===void 0||typeof e=="string";if(!t&&e.textures[this.uuid]!==void 0)return e.textures[this.uuid];const n={metadata:{version:4.6,type:"Texture",generator:"Texture.toJSON"},uuid:this.uuid,name:this.name,image:this.source.toJSON(e).uuid,mapping:this.mapping,channel:this.channel,repeat:[this.repeat.x,this.repeat.y],offset:[this.offset.x,this.offset.y],center:[this.center.x,this.center.y],rotation:this.rotation,wrap:[this.wrapS,this.wrapT],format:this.format,internalFormat:this.internalFormat,type:this.type,colorSpace:this.colorSpace,minFilter:this.minFilter,magFilter:this.magFilter,anisotropy:this.anisotropy,flipY:this.flipY,generateMipmaps:this.generateMipmaps,premultiplyAlpha:this.premultiplyAlpha,unpackAlignment:this.unpackAlignment};return Object.keys(this.userData).length>0&&(n.userData=this.userData),t||(e.textures[this.uuid]=n),n}dispose(){this.dispatchEvent({type:"dispose"})}transformUv(e){if(this.mapping!==ip)return e;if(e.applyMatrix3(this.matrix),e.x<0||e.x>1)switch(this.wrapS){case Kc:e.x=e.x-Math.floor(e.x);break;case Ys:e.x=e.x<0?0:1;break;case Jc:Math.abs(Math.floor(e.x)%2)===1?e.x=Math.ceil(e.x)-e.x:e.x=e.x-Math.floor(e.x);break}if(e.y<0||e.y>1)switch(this.wrapT){case Kc:e.y=e.y-Math.floor(e.y);break;case Ys:e.y=e.y<0?0:1;break;case Jc:Math.abs(Math.floor(e.y)%2)===1?e.y=Math.ceil(e.y)-e.y:e.y=e.y-Math.floor(e.y);break}return this.flipY&&(e.y=1-e.y),e}set needsUpdate(e){e===!0&&(this.version++,this.source.needsUpdate=!0)}set needsPMREMUpdate(e){e===!0&&this.pmremVersion++}}Bn.DEFAULT_IMAGE=null;Bn.DEFAULT_MAPPING=ip;Bn.DEFAULT_ANISOTROPY=1;class on{constructor(e=0,t=0,n=0,s=1){on.prototype.isVector4=!0,this.x=e,this.y=t,this.z=n,this.w=s}get width(){return this.z}set width(e){this.z=e}get height(){return this.w}set height(e){this.w=e}set(e,t,n,s){return this.x=e,this.y=t,this.z=n,this.w=s,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this.w=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setW(e){return this.w=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;case 3:this.w=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;case 3:return this.w;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z,this.w)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this.w=e.w!==void 0?e.w:1,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this.w+=e.w,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this.w+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this.w=e.w+t.w,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this.w+=e.w*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this.w-=e.w,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this.w-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this.w=e.w-t.w,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this.w*=e.w,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this.w*=e,this}applyMatrix4(e){const t=this.x,n=this.y,s=this.z,r=this.w,a=e.elements;return this.x=a[0]*t+a[4]*n+a[8]*s+a[12]*r,this.y=a[1]*t+a[5]*n+a[9]*s+a[13]*r,this.z=a[2]*t+a[6]*n+a[10]*s+a[14]*r,this.w=a[3]*t+a[7]*n+a[11]*s+a[15]*r,this}divideScalar(e){return this.multiplyScalar(1/e)}setAxisAngleFromQuaternion(e){this.w=2*Math.acos(e.w);const t=Math.sqrt(1-e.w*e.w);return t<1e-4?(this.x=1,this.y=0,this.z=0):(this.x=e.x/t,this.y=e.y/t,this.z=e.z/t),this}setAxisAngleFromRotationMatrix(e){let t,n,s,r;const l=e.elements,c=l[0],h=l[4],u=l[8],d=l[1],f=l[5],g=l[9],v=l[2],p=l[6],m=l[10];if(Math.abs(h-d)<.01&&Math.abs(u-v)<.01&&Math.abs(g-p)<.01){if(Math.abs(h+d)<.1&&Math.abs(u+v)<.1&&Math.abs(g+p)<.1&&Math.abs(c+f+m-3)<.1)return this.set(1,0,0,0),this;t=Math.PI;const _=(c+1)/2,b=(f+1)/2,I=(m+1)/2,A=(h+d)/4,R=(u+v)/4,N=(g+p)/4;return _>b&&_>I?_<.01?(n=0,s=.707106781,r=.707106781):(n=Math.sqrt(_),s=A/n,r=R/n):b>I?b<.01?(n=.707106781,s=0,r=.707106781):(s=Math.sqrt(b),n=A/s,r=N/s):I<.01?(n=.707106781,s=.707106781,r=0):(r=Math.sqrt(I),n=R/r,s=N/r),this.set(n,s,r,t),this}let S=Math.sqrt((p-g)*(p-g)+(u-v)*(u-v)+(d-h)*(d-h));return Math.abs(S)<.001&&(S=1),this.x=(p-g)/S,this.y=(u-v)/S,this.z=(d-h)/S,this.w=Math.acos((c+f+m-1)/2),this}setFromMatrixPosition(e){const t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this.w=t[15],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this.w=Math.min(this.w,e.w),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this.w=Math.max(this.w,e.w),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this.z=Math.max(e.z,Math.min(t.z,this.z)),this.w=Math.max(e.w,Math.min(t.w,this.w)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this.z=Math.max(e,Math.min(t,this.z)),this.w=Math.max(e,Math.min(t,this.w)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this.w=Math.floor(this.w),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this.w=Math.ceil(this.w),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this.w=Math.round(this.w),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this.w=Math.trunc(this.w),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this.w=-this.w,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z+this.w*e.w}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)+Math.abs(this.w)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this.w+=(e.w-this.w)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this.z=e.z+(t.z-e.z)*n,this.w=e.w+(t.w-e.w)*n,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z&&e.w===this.w}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this.w=e[t+3],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e[t+3]=this.w,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this.w=e.getW(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this.w=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z,yield this.w}}class _v extends pa{constructor(e=1,t=1,n={}){super(),this.isRenderTarget=!0,this.width=e,this.height=t,this.depth=1,this.scissor=new on(0,0,e,t),this.scissorTest=!1,this.viewport=new on(0,0,e,t);const s={width:e,height:t,depth:1};n=Object.assign({generateMipmaps:!1,internalFormat:null,minFilter:vi,depthBuffer:!0,stencilBuffer:!1,resolveDepthBuffer:!0,resolveStencilBuffer:!0,depthTexture:null,samples:0,count:1},n);const r=new Bn(s,n.mapping,n.wrapS,n.wrapT,n.magFilter,n.minFilter,n.format,n.type,n.anisotropy,n.colorSpace);r.flipY=!1,r.generateMipmaps=n.generateMipmaps,r.internalFormat=n.internalFormat,this.textures=[];const a=n.count;for(let o=0;o<a;o++)this.textures[o]=r.clone(),this.textures[o].isRenderTargetTexture=!0;this.depthBuffer=n.depthBuffer,this.stencilBuffer=n.stencilBuffer,this.resolveDepthBuffer=n.resolveDepthBuffer,this.resolveStencilBuffer=n.resolveStencilBuffer,this.depthTexture=n.depthTexture,this.samples=n.samples}get texture(){return this.textures[0]}set texture(e){this.textures[0]=e}setSize(e,t,n=1){if(this.width!==e||this.height!==t||this.depth!==n){this.width=e,this.height=t,this.depth=n;for(let s=0,r=this.textures.length;s<r;s++)this.textures[s].image.width=e,this.textures[s].image.height=t,this.textures[s].image.depth=n;this.dispose()}this.viewport.set(0,0,e,t),this.scissor.set(0,0,e,t)}clone(){return new this.constructor().copy(this)}copy(e){this.width=e.width,this.height=e.height,this.depth=e.depth,this.scissor.copy(e.scissor),this.scissorTest=e.scissorTest,this.viewport.copy(e.viewport),this.textures.length=0;for(let n=0,s=e.textures.length;n<s;n++)this.textures[n]=e.textures[n].clone(),this.textures[n].isRenderTargetTexture=!0;const t=Object.assign({},e.texture.image);return this.texture.source=new vp(t),this.depthBuffer=e.depthBuffer,this.stencilBuffer=e.stencilBuffer,this.resolveDepthBuffer=e.resolveDepthBuffer,this.resolveStencilBuffer=e.resolveStencilBuffer,e.depthTexture!==null&&(this.depthTexture=e.depthTexture.clone()),this.samples=e.samples,this}dispose(){this.dispatchEvent({type:"dispose"})}}class Qs extends _v{constructor(e=1,t=1,n={}){super(e,t,n),this.isWebGLRenderTarget=!0}}class xp extends Bn{constructor(e=null,t=1,n=1,s=1){super(null),this.isDataArrayTexture=!0,this.image={data:e,width:t,height:n,depth:s},this.magFilter=ai,this.minFilter=ai,this.wrapR=Ys,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1,this.layerUpdates=new Set}addLayerUpdate(e){this.layerUpdates.add(e)}clearLayerUpdates(){this.layerUpdates.clear()}}class yv extends Bn{constructor(e=null,t=1,n=1,s=1){super(null),this.isData3DTexture=!0,this.image={data:e,width:t,height:n,depth:s},this.magFilter=ai,this.minFilter=ai,this.wrapR=Ys,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}}class er{constructor(e=0,t=0,n=0,s=1){this.isQuaternion=!0,this._x=e,this._y=t,this._z=n,this._w=s}static slerpFlat(e,t,n,s,r,a,o){let l=n[s+0],c=n[s+1],h=n[s+2],u=n[s+3];const d=r[a+0],f=r[a+1],g=r[a+2],v=r[a+3];if(o===0){e[t+0]=l,e[t+1]=c,e[t+2]=h,e[t+3]=u;return}if(o===1){e[t+0]=d,e[t+1]=f,e[t+2]=g,e[t+3]=v;return}if(u!==v||l!==d||c!==f||h!==g){let p=1-o;const m=l*d+c*f+h*g+u*v,S=m>=0?1:-1,_=1-m*m;if(_>Number.EPSILON){const I=Math.sqrt(_),A=Math.atan2(I,m*S);p=Math.sin(p*A)/I,o=Math.sin(o*A)/I}const b=o*S;if(l=l*p+d*b,c=c*p+f*b,h=h*p+g*b,u=u*p+v*b,p===1-o){const I=1/Math.sqrt(l*l+c*c+h*h+u*u);l*=I,c*=I,h*=I,u*=I}}e[t]=l,e[t+1]=c,e[t+2]=h,e[t+3]=u}static multiplyQuaternionsFlat(e,t,n,s,r,a){const o=n[s],l=n[s+1],c=n[s+2],h=n[s+3],u=r[a],d=r[a+1],f=r[a+2],g=r[a+3];return e[t]=o*g+h*u+l*f-c*d,e[t+1]=l*g+h*d+c*u-o*f,e[t+2]=c*g+h*f+o*d-l*u,e[t+3]=h*g-o*u-l*d-c*f,e}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get w(){return this._w}set w(e){this._w=e,this._onChangeCallback()}set(e,t,n,s){return this._x=e,this._y=t,this._z=n,this._w=s,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._w)}copy(e){return this._x=e.x,this._y=e.y,this._z=e.z,this._w=e.w,this._onChangeCallback(),this}setFromEuler(e,t=!0){const n=e._x,s=e._y,r=e._z,a=e._order,o=Math.cos,l=Math.sin,c=o(n/2),h=o(s/2),u=o(r/2),d=l(n/2),f=l(s/2),g=l(r/2);switch(a){case"XYZ":this._x=d*h*u+c*f*g,this._y=c*f*u-d*h*g,this._z=c*h*g+d*f*u,this._w=c*h*u-d*f*g;break;case"YXZ":this._x=d*h*u+c*f*g,this._y=c*f*u-d*h*g,this._z=c*h*g-d*f*u,this._w=c*h*u+d*f*g;break;case"ZXY":this._x=d*h*u-c*f*g,this._y=c*f*u+d*h*g,this._z=c*h*g+d*f*u,this._w=c*h*u-d*f*g;break;case"ZYX":this._x=d*h*u-c*f*g,this._y=c*f*u+d*h*g,this._z=c*h*g-d*f*u,this._w=c*h*u+d*f*g;break;case"YZX":this._x=d*h*u+c*f*g,this._y=c*f*u+d*h*g,this._z=c*h*g-d*f*u,this._w=c*h*u-d*f*g;break;case"XZY":this._x=d*h*u-c*f*g,this._y=c*f*u-d*h*g,this._z=c*h*g+d*f*u,this._w=c*h*u+d*f*g;break;default:console.warn("THREE.Quaternion: .setFromEuler() encountered an unknown order: "+a)}return t===!0&&this._onChangeCallback(),this}setFromAxisAngle(e,t){const n=t/2,s=Math.sin(n);return this._x=e.x*s,this._y=e.y*s,this._z=e.z*s,this._w=Math.cos(n),this._onChangeCallback(),this}setFromRotationMatrix(e){const t=e.elements,n=t[0],s=t[4],r=t[8],a=t[1],o=t[5],l=t[9],c=t[2],h=t[6],u=t[10],d=n+o+u;if(d>0){const f=.5/Math.sqrt(d+1);this._w=.25/f,this._x=(h-l)*f,this._y=(r-c)*f,this._z=(a-s)*f}else if(n>o&&n>u){const f=2*Math.sqrt(1+n-o-u);this._w=(h-l)/f,this._x=.25*f,this._y=(s+a)/f,this._z=(r+c)/f}else if(o>u){const f=2*Math.sqrt(1+o-n-u);this._w=(r-c)/f,this._x=(s+a)/f,this._y=.25*f,this._z=(l+h)/f}else{const f=2*Math.sqrt(1+u-n-o);this._w=(a-s)/f,this._x=(r+c)/f,this._y=(l+h)/f,this._z=.25*f}return this._onChangeCallback(),this}setFromUnitVectors(e,t){let n=e.dot(t)+1;return n<Number.EPSILON?(n=0,Math.abs(e.x)>Math.abs(e.z)?(this._x=-e.y,this._y=e.x,this._z=0,this._w=n):(this._x=0,this._y=-e.z,this._z=e.y,this._w=n)):(this._x=e.y*t.z-e.z*t.y,this._y=e.z*t.x-e.x*t.z,this._z=e.x*t.y-e.y*t.x,this._w=n),this.normalize()}angleTo(e){return 2*Math.acos(Math.abs(Cn(this.dot(e),-1,1)))}rotateTowards(e,t){const n=this.angleTo(e);if(n===0)return this;const s=Math.min(1,t/n);return this.slerp(e,s),this}identity(){return this.set(0,0,0,1)}invert(){return this.conjugate()}conjugate(){return this._x*=-1,this._y*=-1,this._z*=-1,this._onChangeCallback(),this}dot(e){return this._x*e._x+this._y*e._y+this._z*e._z+this._w*e._w}lengthSq(){return this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w}length(){return Math.sqrt(this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w)}normalize(){let e=this.length();return e===0?(this._x=0,this._y=0,this._z=0,this._w=1):(e=1/e,this._x=this._x*e,this._y=this._y*e,this._z=this._z*e,this._w=this._w*e),this._onChangeCallback(),this}multiply(e){return this.multiplyQuaternions(this,e)}premultiply(e){return this.multiplyQuaternions(e,this)}multiplyQuaternions(e,t){const n=e._x,s=e._y,r=e._z,a=e._w,o=t._x,l=t._y,c=t._z,h=t._w;return this._x=n*h+a*o+s*c-r*l,this._y=s*h+a*l+r*o-n*c,this._z=r*h+a*c+n*l-s*o,this._w=a*h-n*o-s*l-r*c,this._onChangeCallback(),this}slerp(e,t){if(t===0)return this;if(t===1)return this.copy(e);const n=this._x,s=this._y,r=this._z,a=this._w;let o=a*e._w+n*e._x+s*e._y+r*e._z;if(o<0?(this._w=-e._w,this._x=-e._x,this._y=-e._y,this._z=-e._z,o=-o):this.copy(e),o>=1)return this._w=a,this._x=n,this._y=s,this._z=r,this;const l=1-o*o;if(l<=Number.EPSILON){const f=1-t;return this._w=f*a+t*this._w,this._x=f*n+t*this._x,this._y=f*s+t*this._y,this._z=f*r+t*this._z,this.normalize(),this}const c=Math.sqrt(l),h=Math.atan2(c,o),u=Math.sin((1-t)*h)/c,d=Math.sin(t*h)/c;return this._w=a*u+this._w*d,this._x=n*u+this._x*d,this._y=s*u+this._y*d,this._z=r*u+this._z*d,this._onChangeCallback(),this}slerpQuaternions(e,t,n){return this.copy(e).slerp(t,n)}random(){const e=2*Math.PI*Math.random(),t=2*Math.PI*Math.random(),n=Math.random(),s=Math.sqrt(1-n),r=Math.sqrt(n);return this.set(s*Math.sin(e),s*Math.cos(e),r*Math.sin(t),r*Math.cos(t))}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._w===this._w}fromArray(e,t=0){return this._x=e[t],this._y=e[t+1],this._z=e[t+2],this._w=e[t+3],this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._w,e}fromBufferAttribute(e,t){return this._x=e.getX(t),this._y=e.getY(t),this._z=e.getZ(t),this._w=e.getW(t),this._onChangeCallback(),this}toJSON(){return this.toArray()}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._w}}class V{constructor(e=0,t=0,n=0){V.prototype.isVector3=!0,this.x=e,this.y=t,this.z=n}set(e,t,n){return n===void 0&&(n=this.z),this.x=e,this.y=t,this.z=n,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this}multiplyVectors(e,t){return this.x=e.x*t.x,this.y=e.y*t.y,this.z=e.z*t.z,this}applyEuler(e){return this.applyQuaternion(Zu.setFromEuler(e))}applyAxisAngle(e,t){return this.applyQuaternion(Zu.setFromAxisAngle(e,t))}applyMatrix3(e){const t=this.x,n=this.y,s=this.z,r=e.elements;return this.x=r[0]*t+r[3]*n+r[6]*s,this.y=r[1]*t+r[4]*n+r[7]*s,this.z=r[2]*t+r[5]*n+r[8]*s,this}applyNormalMatrix(e){return this.applyMatrix3(e).normalize()}applyMatrix4(e){const t=this.x,n=this.y,s=this.z,r=e.elements,a=1/(r[3]*t+r[7]*n+r[11]*s+r[15]);return this.x=(r[0]*t+r[4]*n+r[8]*s+r[12])*a,this.y=(r[1]*t+r[5]*n+r[9]*s+r[13])*a,this.z=(r[2]*t+r[6]*n+r[10]*s+r[14])*a,this}applyQuaternion(e){const t=this.x,n=this.y,s=this.z,r=e.x,a=e.y,o=e.z,l=e.w,c=2*(a*s-o*n),h=2*(o*t-r*s),u=2*(r*n-a*t);return this.x=t+l*c+a*u-o*h,this.y=n+l*h+o*c-r*u,this.z=s+l*u+r*h-a*c,this}project(e){return this.applyMatrix4(e.matrixWorldInverse).applyMatrix4(e.projectionMatrix)}unproject(e){return this.applyMatrix4(e.projectionMatrixInverse).applyMatrix4(e.matrixWorld)}transformDirection(e){const t=this.x,n=this.y,s=this.z,r=e.elements;return this.x=r[0]*t+r[4]*n+r[8]*s,this.y=r[1]*t+r[5]*n+r[9]*s,this.z=r[2]*t+r[6]*n+r[10]*s,this.normalize()}divide(e){return this.x/=e.x,this.y/=e.y,this.z/=e.z,this}divideScalar(e){return this.multiplyScalar(1/e)}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this.z=Math.max(e.z,Math.min(t.z,this.z)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this.z=Math.max(e,Math.min(t,this.z)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this.z=e.z+(t.z-e.z)*n,this}cross(e){return this.crossVectors(this,e)}crossVectors(e,t){const n=e.x,s=e.y,r=e.z,a=t.x,o=t.y,l=t.z;return this.x=s*l-r*o,this.y=r*a-n*l,this.z=n*o-s*a,this}projectOnVector(e){const t=e.lengthSq();if(t===0)return this.set(0,0,0);const n=e.dot(this)/t;return this.copy(e).multiplyScalar(n)}projectOnPlane(e){return rc.copy(this).projectOnVector(e),this.sub(rc)}reflect(e){return this.sub(rc.copy(e).multiplyScalar(2*this.dot(e)))}angleTo(e){const t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;const n=this.dot(e)/t;return Math.acos(Cn(n,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){const t=this.x-e.x,n=this.y-e.y,s=this.z-e.z;return t*t+n*n+s*s}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)+Math.abs(this.z-e.z)}setFromSpherical(e){return this.setFromSphericalCoords(e.radius,e.phi,e.theta)}setFromSphericalCoords(e,t,n){const s=Math.sin(t)*e;return this.x=s*Math.sin(n),this.y=Math.cos(t)*e,this.z=s*Math.cos(n),this}setFromCylindrical(e){return this.setFromCylindricalCoords(e.radius,e.theta,e.y)}setFromCylindricalCoords(e,t,n){return this.x=e*Math.sin(t),this.y=n,this.z=e*Math.cos(t),this}setFromMatrixPosition(e){const t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this}setFromMatrixScale(e){const t=this.setFromMatrixColumn(e,0).length(),n=this.setFromMatrixColumn(e,1).length(),s=this.setFromMatrixColumn(e,2).length();return this.x=t,this.y=n,this.z=s,this}setFromMatrixColumn(e,t){return this.fromArray(e.elements,t*4)}setFromMatrix3Column(e,t){return this.fromArray(e.elements,t*3)}setFromEuler(e){return this.x=e._x,this.y=e._y,this.z=e._z,this}setFromColor(e){return this.x=e.r,this.y=e.g,this.z=e.b,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this}randomDirection(){const e=Math.random()*Math.PI*2,t=Math.random()*2-1,n=Math.sqrt(1-t*t);return this.x=n*Math.cos(e),this.y=t,this.z=n*Math.sin(e),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z}}const rc=new V,Zu=new er;class ro{constructor(e=new V(1/0,1/0,1/0),t=new V(-1/0,-1/0,-1/0)){this.isBox3=!0,this.min=e,this.max=t}set(e,t){return this.min.copy(e),this.max.copy(t),this}setFromArray(e){this.makeEmpty();for(let t=0,n=e.length;t<n;t+=3)this.expandByPoint(di.fromArray(e,t));return this}setFromBufferAttribute(e){this.makeEmpty();for(let t=0,n=e.count;t<n;t++)this.expandByPoint(di.fromBufferAttribute(e,t));return this}setFromPoints(e){this.makeEmpty();for(let t=0,n=e.length;t<n;t++)this.expandByPoint(e[t]);return this}setFromCenterAndSize(e,t){const n=di.copy(t).multiplyScalar(.5);return this.min.copy(e).sub(n),this.max.copy(e).add(n),this}setFromObject(e,t=!1){return this.makeEmpty(),this.expandByObject(e,t)}clone(){return new this.constructor().copy(this)}copy(e){return this.min.copy(e.min),this.max.copy(e.max),this}makeEmpty(){return this.min.x=this.min.y=this.min.z=1/0,this.max.x=this.max.y=this.max.z=-1/0,this}isEmpty(){return this.max.x<this.min.x||this.max.y<this.min.y||this.max.z<this.min.z}getCenter(e){return this.isEmpty()?e.set(0,0,0):e.addVectors(this.min,this.max).multiplyScalar(.5)}getSize(e){return this.isEmpty()?e.set(0,0,0):e.subVectors(this.max,this.min)}expandByPoint(e){return this.min.min(e),this.max.max(e),this}expandByVector(e){return this.min.sub(e),this.max.add(e),this}expandByScalar(e){return this.min.addScalar(-e),this.max.addScalar(e),this}expandByObject(e,t=!1){e.updateWorldMatrix(!1,!1);const n=e.geometry;if(n!==void 0){const r=n.getAttribute("position");if(t===!0&&r!==void 0&&e.isInstancedMesh!==!0)for(let a=0,o=r.count;a<o;a++)e.isMesh===!0?e.getVertexPosition(a,di):di.fromBufferAttribute(r,a),di.applyMatrix4(e.matrixWorld),this.expandByPoint(di);else e.boundingBox!==void 0?(e.boundingBox===null&&e.computeBoundingBox(),yo.copy(e.boundingBox)):(n.boundingBox===null&&n.computeBoundingBox(),yo.copy(n.boundingBox)),yo.applyMatrix4(e.matrixWorld),this.union(yo)}const s=e.children;for(let r=0,a=s.length;r<a;r++)this.expandByObject(s[r],t);return this}containsPoint(e){return e.x>=this.min.x&&e.x<=this.max.x&&e.y>=this.min.y&&e.y<=this.max.y&&e.z>=this.min.z&&e.z<=this.max.z}containsBox(e){return this.min.x<=e.min.x&&e.max.x<=this.max.x&&this.min.y<=e.min.y&&e.max.y<=this.max.y&&this.min.z<=e.min.z&&e.max.z<=this.max.z}getParameter(e,t){return t.set((e.x-this.min.x)/(this.max.x-this.min.x),(e.y-this.min.y)/(this.max.y-this.min.y),(e.z-this.min.z)/(this.max.z-this.min.z))}intersectsBox(e){return e.max.x>=this.min.x&&e.min.x<=this.max.x&&e.max.y>=this.min.y&&e.min.y<=this.max.y&&e.max.z>=this.min.z&&e.min.z<=this.max.z}intersectsSphere(e){return this.clampPoint(e.center,di),di.distanceToSquared(e.center)<=e.radius*e.radius}intersectsPlane(e){let t,n;return e.normal.x>0?(t=e.normal.x*this.min.x,n=e.normal.x*this.max.x):(t=e.normal.x*this.max.x,n=e.normal.x*this.min.x),e.normal.y>0?(t+=e.normal.y*this.min.y,n+=e.normal.y*this.max.y):(t+=e.normal.y*this.max.y,n+=e.normal.y*this.min.y),e.normal.z>0?(t+=e.normal.z*this.min.z,n+=e.normal.z*this.max.z):(t+=e.normal.z*this.max.z,n+=e.normal.z*this.min.z),t<=-e.constant&&n>=-e.constant}intersectsTriangle(e){if(this.isEmpty())return!1;this.getCenter(Ra),So.subVectors(this.max,Ra),yr.subVectors(e.a,Ra),Sr.subVectors(e.b,Ra),br.subVectors(e.c,Ra),us.subVectors(Sr,yr),ds.subVectors(br,Sr),Os.subVectors(yr,br);let t=[0,-us.z,us.y,0,-ds.z,ds.y,0,-Os.z,Os.y,us.z,0,-us.x,ds.z,0,-ds.x,Os.z,0,-Os.x,-us.y,us.x,0,-ds.y,ds.x,0,-Os.y,Os.x,0];return!ac(t,yr,Sr,br,So)||(t=[1,0,0,0,1,0,0,0,1],!ac(t,yr,Sr,br,So))?!1:(bo.crossVectors(us,ds),t=[bo.x,bo.y,bo.z],ac(t,yr,Sr,br,So))}clampPoint(e,t){return t.copy(e).clamp(this.min,this.max)}distanceToPoint(e){return this.clampPoint(e,di).distanceTo(e)}getBoundingSphere(e){return this.isEmpty()?e.makeEmpty():(this.getCenter(e.center),e.radius=this.getSize(di).length()*.5),e}intersect(e){return this.min.max(e.min),this.max.min(e.max),this.isEmpty()&&this.makeEmpty(),this}union(e){return this.min.min(e.min),this.max.max(e.max),this}applyMatrix4(e){return this.isEmpty()?this:(Wi[0].set(this.min.x,this.min.y,this.min.z).applyMatrix4(e),Wi[1].set(this.min.x,this.min.y,this.max.z).applyMatrix4(e),Wi[2].set(this.min.x,this.max.y,this.min.z).applyMatrix4(e),Wi[3].set(this.min.x,this.max.y,this.max.z).applyMatrix4(e),Wi[4].set(this.max.x,this.min.y,this.min.z).applyMatrix4(e),Wi[5].set(this.max.x,this.min.y,this.max.z).applyMatrix4(e),Wi[6].set(this.max.x,this.max.y,this.min.z).applyMatrix4(e),Wi[7].set(this.max.x,this.max.y,this.max.z).applyMatrix4(e),this.setFromPoints(Wi),this)}translate(e){return this.min.add(e),this.max.add(e),this}equals(e){return e.min.equals(this.min)&&e.max.equals(this.max)}}const Wi=[new V,new V,new V,new V,new V,new V,new V,new V],di=new V,yo=new ro,yr=new V,Sr=new V,br=new V,us=new V,ds=new V,Os=new V,Ra=new V,So=new V,bo=new V,Fs=new V;function ac(i,e,t,n,s){for(let r=0,a=i.length-3;r<=a;r+=3){Fs.fromArray(i,r);const o=s.x*Math.abs(Fs.x)+s.y*Math.abs(Fs.y)+s.z*Math.abs(Fs.z),l=e.dot(Fs),c=t.dot(Fs),h=n.dot(Fs);if(Math.max(-Math.max(l,c,h),Math.min(l,c,h))>o)return!1}return!0}const Sv=new ro,Pa=new V,oc=new V;class ao{constructor(e=new V,t=-1){this.isSphere=!0,this.center=e,this.radius=t}set(e,t){return this.center.copy(e),this.radius=t,this}setFromPoints(e,t){const n=this.center;t!==void 0?n.copy(t):Sv.setFromPoints(e).getCenter(n);let s=0;for(let r=0,a=e.length;r<a;r++)s=Math.max(s,n.distanceToSquared(e[r]));return this.radius=Math.sqrt(s),this}copy(e){return this.center.copy(e.center),this.radius=e.radius,this}isEmpty(){return this.radius<0}makeEmpty(){return this.center.set(0,0,0),this.radius=-1,this}containsPoint(e){return e.distanceToSquared(this.center)<=this.radius*this.radius}distanceToPoint(e){return e.distanceTo(this.center)-this.radius}intersectsSphere(e){const t=this.radius+e.radius;return e.center.distanceToSquared(this.center)<=t*t}intersectsBox(e){return e.intersectsSphere(this)}intersectsPlane(e){return Math.abs(e.distanceToPoint(this.center))<=this.radius}clampPoint(e,t){const n=this.center.distanceToSquared(e);return t.copy(e),n>this.radius*this.radius&&(t.sub(this.center).normalize(),t.multiplyScalar(this.radius).add(this.center)),t}getBoundingBox(e){return this.isEmpty()?(e.makeEmpty(),e):(e.set(this.center,this.center),e.expandByScalar(this.radius),e)}applyMatrix4(e){return this.center.applyMatrix4(e),this.radius=this.radius*e.getMaxScaleOnAxis(),this}translate(e){return this.center.add(e),this}expandByPoint(e){if(this.isEmpty())return this.center.copy(e),this.radius=0,this;Pa.subVectors(e,this.center);const t=Pa.lengthSq();if(t>this.radius*this.radius){const n=Math.sqrt(t),s=(n-this.radius)*.5;this.center.addScaledVector(Pa,s/n),this.radius+=s}return this}union(e){return e.isEmpty()?this:this.isEmpty()?(this.copy(e),this):(this.center.equals(e.center)===!0?this.radius=Math.max(this.radius,e.radius):(oc.subVectors(e.center,this.center).setLength(e.radius),this.expandByPoint(Pa.copy(e.center).add(oc)),this.expandByPoint(Pa.copy(e.center).sub(oc))),this)}equals(e){return e.center.equals(this.center)&&e.radius===this.radius}clone(){return new this.constructor().copy(this)}}const $i=new V,lc=new V,Mo=new V,fs=new V,cc=new V,wo=new V,hc=new V;class oo{constructor(e=new V,t=new V(0,0,-1)){this.origin=e,this.direction=t}set(e,t){return this.origin.copy(e),this.direction.copy(t),this}copy(e){return this.origin.copy(e.origin),this.direction.copy(e.direction),this}at(e,t){return t.copy(this.origin).addScaledVector(this.direction,e)}lookAt(e){return this.direction.copy(e).sub(this.origin).normalize(),this}recast(e){return this.origin.copy(this.at(e,$i)),this}closestPointToPoint(e,t){t.subVectors(e,this.origin);const n=t.dot(this.direction);return n<0?t.copy(this.origin):t.copy(this.origin).addScaledVector(this.direction,n)}distanceToPoint(e){return Math.sqrt(this.distanceSqToPoint(e))}distanceSqToPoint(e){const t=$i.subVectors(e,this.origin).dot(this.direction);return t<0?this.origin.distanceToSquared(e):($i.copy(this.origin).addScaledVector(this.direction,t),$i.distanceToSquared(e))}distanceSqToSegment(e,t,n,s){lc.copy(e).add(t).multiplyScalar(.5),Mo.copy(t).sub(e).normalize(),fs.copy(this.origin).sub(lc);const r=e.distanceTo(t)*.5,a=-this.direction.dot(Mo),o=fs.dot(this.direction),l=-fs.dot(Mo),c=fs.lengthSq(),h=Math.abs(1-a*a);let u,d,f,g;if(h>0)if(u=a*l-o,d=a*o-l,g=r*h,u>=0)if(d>=-g)if(d<=g){const v=1/h;u*=v,d*=v,f=u*(u+a*d+2*o)+d*(a*u+d+2*l)+c}else d=r,u=Math.max(0,-(a*d+o)),f=-u*u+d*(d+2*l)+c;else d=-r,u=Math.max(0,-(a*d+o)),f=-u*u+d*(d+2*l)+c;else d<=-g?(u=Math.max(0,-(-a*r+o)),d=u>0?-r:Math.min(Math.max(-r,-l),r),f=-u*u+d*(d+2*l)+c):d<=g?(u=0,d=Math.min(Math.max(-r,-l),r),f=d*(d+2*l)+c):(u=Math.max(0,-(a*r+o)),d=u>0?r:Math.min(Math.max(-r,-l),r),f=-u*u+d*(d+2*l)+c);else d=a>0?-r:r,u=Math.max(0,-(a*d+o)),f=-u*u+d*(d+2*l)+c;return n&&n.copy(this.origin).addScaledVector(this.direction,u),s&&s.copy(lc).addScaledVector(Mo,d),f}intersectSphere(e,t){$i.subVectors(e.center,this.origin);const n=$i.dot(this.direction),s=$i.dot($i)-n*n,r=e.radius*e.radius;if(s>r)return null;const a=Math.sqrt(r-s),o=n-a,l=n+a;return l<0?null:o<0?this.at(l,t):this.at(o,t)}intersectsSphere(e){return this.distanceSqToPoint(e.center)<=e.radius*e.radius}distanceToPlane(e){const t=e.normal.dot(this.direction);if(t===0)return e.distanceToPoint(this.origin)===0?0:null;const n=-(this.origin.dot(e.normal)+e.constant)/t;return n>=0?n:null}intersectPlane(e,t){const n=this.distanceToPlane(e);return n===null?null:this.at(n,t)}intersectsPlane(e){const t=e.distanceToPoint(this.origin);return t===0||e.normal.dot(this.direction)*t<0}intersectBox(e,t){let n,s,r,a,o,l;const c=1/this.direction.x,h=1/this.direction.y,u=1/this.direction.z,d=this.origin;return c>=0?(n=(e.min.x-d.x)*c,s=(e.max.x-d.x)*c):(n=(e.max.x-d.x)*c,s=(e.min.x-d.x)*c),h>=0?(r=(e.min.y-d.y)*h,a=(e.max.y-d.y)*h):(r=(e.max.y-d.y)*h,a=(e.min.y-d.y)*h),n>a||r>s||((r>n||isNaN(n))&&(n=r),(a<s||isNaN(s))&&(s=a),u>=0?(o=(e.min.z-d.z)*u,l=(e.max.z-d.z)*u):(o=(e.max.z-d.z)*u,l=(e.min.z-d.z)*u),n>l||o>s)||((o>n||n!==n)&&(n=o),(l<s||s!==s)&&(s=l),s<0)?null:this.at(n>=0?n:s,t)}intersectsBox(e){return this.intersectBox(e,$i)!==null}intersectTriangle(e,t,n,s,r){cc.subVectors(t,e),wo.subVectors(n,e),hc.crossVectors(cc,wo);let a=this.direction.dot(hc),o;if(a>0){if(s)return null;o=1}else if(a<0)o=-1,a=-a;else return null;fs.subVectors(this.origin,e);const l=o*this.direction.dot(wo.crossVectors(fs,wo));if(l<0)return null;const c=o*this.direction.dot(cc.cross(fs));if(c<0||l+c>a)return null;const h=-o*fs.dot(hc);return h<0?null:this.at(h/a,r)}applyMatrix4(e){return this.origin.applyMatrix4(e),this.direction.transformDirection(e),this}equals(e){return e.origin.equals(this.origin)&&e.direction.equals(this.direction)}clone(){return new this.constructor().copy(this)}}class zt{constructor(e,t,n,s,r,a,o,l,c,h,u,d,f,g,v,p){zt.prototype.isMatrix4=!0,this.elements=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],e!==void 0&&this.set(e,t,n,s,r,a,o,l,c,h,u,d,f,g,v,p)}set(e,t,n,s,r,a,o,l,c,h,u,d,f,g,v,p){const m=this.elements;return m[0]=e,m[4]=t,m[8]=n,m[12]=s,m[1]=r,m[5]=a,m[9]=o,m[13]=l,m[2]=c,m[6]=h,m[10]=u,m[14]=d,m[3]=f,m[7]=g,m[11]=v,m[15]=p,this}identity(){return this.set(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1),this}clone(){return new zt().fromArray(this.elements)}copy(e){const t=this.elements,n=e.elements;return t[0]=n[0],t[1]=n[1],t[2]=n[2],t[3]=n[3],t[4]=n[4],t[5]=n[5],t[6]=n[6],t[7]=n[7],t[8]=n[8],t[9]=n[9],t[10]=n[10],t[11]=n[11],t[12]=n[12],t[13]=n[13],t[14]=n[14],t[15]=n[15],this}copyPosition(e){const t=this.elements,n=e.elements;return t[12]=n[12],t[13]=n[13],t[14]=n[14],this}setFromMatrix3(e){const t=e.elements;return this.set(t[0],t[3],t[6],0,t[1],t[4],t[7],0,t[2],t[5],t[8],0,0,0,0,1),this}extractBasis(e,t,n){return e.setFromMatrixColumn(this,0),t.setFromMatrixColumn(this,1),n.setFromMatrixColumn(this,2),this}makeBasis(e,t,n){return this.set(e.x,t.x,n.x,0,e.y,t.y,n.y,0,e.z,t.z,n.z,0,0,0,0,1),this}extractRotation(e){const t=this.elements,n=e.elements,s=1/Mr.setFromMatrixColumn(e,0).length(),r=1/Mr.setFromMatrixColumn(e,1).length(),a=1/Mr.setFromMatrixColumn(e,2).length();return t[0]=n[0]*s,t[1]=n[1]*s,t[2]=n[2]*s,t[3]=0,t[4]=n[4]*r,t[5]=n[5]*r,t[6]=n[6]*r,t[7]=0,t[8]=n[8]*a,t[9]=n[9]*a,t[10]=n[10]*a,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromEuler(e){const t=this.elements,n=e.x,s=e.y,r=e.z,a=Math.cos(n),o=Math.sin(n),l=Math.cos(s),c=Math.sin(s),h=Math.cos(r),u=Math.sin(r);if(e.order==="XYZ"){const d=a*h,f=a*u,g=o*h,v=o*u;t[0]=l*h,t[4]=-l*u,t[8]=c,t[1]=f+g*c,t[5]=d-v*c,t[9]=-o*l,t[2]=v-d*c,t[6]=g+f*c,t[10]=a*l}else if(e.order==="YXZ"){const d=l*h,f=l*u,g=c*h,v=c*u;t[0]=d+v*o,t[4]=g*o-f,t[8]=a*c,t[1]=a*u,t[5]=a*h,t[9]=-o,t[2]=f*o-g,t[6]=v+d*o,t[10]=a*l}else if(e.order==="ZXY"){const d=l*h,f=l*u,g=c*h,v=c*u;t[0]=d-v*o,t[4]=-a*u,t[8]=g+f*o,t[1]=f+g*o,t[5]=a*h,t[9]=v-d*o,t[2]=-a*c,t[6]=o,t[10]=a*l}else if(e.order==="ZYX"){const d=a*h,f=a*u,g=o*h,v=o*u;t[0]=l*h,t[4]=g*c-f,t[8]=d*c+v,t[1]=l*u,t[5]=v*c+d,t[9]=f*c-g,t[2]=-c,t[6]=o*l,t[10]=a*l}else if(e.order==="YZX"){const d=a*l,f=a*c,g=o*l,v=o*c;t[0]=l*h,t[4]=v-d*u,t[8]=g*u+f,t[1]=u,t[5]=a*h,t[9]=-o*h,t[2]=-c*h,t[6]=f*u+g,t[10]=d-v*u}else if(e.order==="XZY"){const d=a*l,f=a*c,g=o*l,v=o*c;t[0]=l*h,t[4]=-u,t[8]=c*h,t[1]=d*u+v,t[5]=a*h,t[9]=f*u-g,t[2]=g*u-f,t[6]=o*h,t[10]=v*u+d}return t[3]=0,t[7]=0,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromQuaternion(e){return this.compose(bv,e,Mv)}lookAt(e,t,n){const s=this.elements;return qn.subVectors(e,t),qn.lengthSq()===0&&(qn.z=1),qn.normalize(),ps.crossVectors(n,qn),ps.lengthSq()===0&&(Math.abs(n.z)===1?qn.x+=1e-4:qn.z+=1e-4,qn.normalize(),ps.crossVectors(n,qn)),ps.normalize(),Eo.crossVectors(qn,ps),s[0]=ps.x,s[4]=Eo.x,s[8]=qn.x,s[1]=ps.y,s[5]=Eo.y,s[9]=qn.y,s[2]=ps.z,s[6]=Eo.z,s[10]=qn.z,this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){const n=e.elements,s=t.elements,r=this.elements,a=n[0],o=n[4],l=n[8],c=n[12],h=n[1],u=n[5],d=n[9],f=n[13],g=n[2],v=n[6],p=n[10],m=n[14],S=n[3],_=n[7],b=n[11],I=n[15],A=s[0],R=s[4],N=s[8],w=s[12],y=s[1],P=s[5],X=s[9],H=s[13],J=s[2],q=s[6],ee=s[10],j=s[14],ne=s[3],ge=s[7],de=s[11],ye=s[15];return r[0]=a*A+o*y+l*J+c*ne,r[4]=a*R+o*P+l*q+c*ge,r[8]=a*N+o*X+l*ee+c*de,r[12]=a*w+o*H+l*j+c*ye,r[1]=h*A+u*y+d*J+f*ne,r[5]=h*R+u*P+d*q+f*ge,r[9]=h*N+u*X+d*ee+f*de,r[13]=h*w+u*H+d*j+f*ye,r[2]=g*A+v*y+p*J+m*ne,r[6]=g*R+v*P+p*q+m*ge,r[10]=g*N+v*X+p*ee+m*de,r[14]=g*w+v*H+p*j+m*ye,r[3]=S*A+_*y+b*J+I*ne,r[7]=S*R+_*P+b*q+I*ge,r[11]=S*N+_*X+b*ee+I*de,r[15]=S*w+_*H+b*j+I*ye,this}multiplyScalar(e){const t=this.elements;return t[0]*=e,t[4]*=e,t[8]*=e,t[12]*=e,t[1]*=e,t[5]*=e,t[9]*=e,t[13]*=e,t[2]*=e,t[6]*=e,t[10]*=e,t[14]*=e,t[3]*=e,t[7]*=e,t[11]*=e,t[15]*=e,this}determinant(){const e=this.elements,t=e[0],n=e[4],s=e[8],r=e[12],a=e[1],o=e[5],l=e[9],c=e[13],h=e[2],u=e[6],d=e[10],f=e[14],g=e[3],v=e[7],p=e[11],m=e[15];return g*(+r*l*u-s*c*u-r*o*d+n*c*d+s*o*f-n*l*f)+v*(+t*l*f-t*c*d+r*a*d-s*a*f+s*c*h-r*l*h)+p*(+t*c*u-t*o*f-r*a*u+n*a*f+r*o*h-n*c*h)+m*(-s*o*h-t*l*u+t*o*d+s*a*u-n*a*d+n*l*h)}transpose(){const e=this.elements;let t;return t=e[1],e[1]=e[4],e[4]=t,t=e[2],e[2]=e[8],e[8]=t,t=e[6],e[6]=e[9],e[9]=t,t=e[3],e[3]=e[12],e[12]=t,t=e[7],e[7]=e[13],e[13]=t,t=e[11],e[11]=e[14],e[14]=t,this}setPosition(e,t,n){const s=this.elements;return e.isVector3?(s[12]=e.x,s[13]=e.y,s[14]=e.z):(s[12]=e,s[13]=t,s[14]=n),this}invert(){const e=this.elements,t=e[0],n=e[1],s=e[2],r=e[3],a=e[4],o=e[5],l=e[6],c=e[7],h=e[8],u=e[9],d=e[10],f=e[11],g=e[12],v=e[13],p=e[14],m=e[15],S=u*p*c-v*d*c+v*l*f-o*p*f-u*l*m+o*d*m,_=g*d*c-h*p*c-g*l*f+a*p*f+h*l*m-a*d*m,b=h*v*c-g*u*c+g*o*f-a*v*f-h*o*m+a*u*m,I=g*u*l-h*v*l-g*o*d+a*v*d+h*o*p-a*u*p,A=t*S+n*_+s*b+r*I;if(A===0)return this.set(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);const R=1/A;return e[0]=S*R,e[1]=(v*d*r-u*p*r-v*s*f+n*p*f+u*s*m-n*d*m)*R,e[2]=(o*p*r-v*l*r+v*s*c-n*p*c-o*s*m+n*l*m)*R,e[3]=(u*l*r-o*d*r-u*s*c+n*d*c+o*s*f-n*l*f)*R,e[4]=_*R,e[5]=(h*p*r-g*d*r+g*s*f-t*p*f-h*s*m+t*d*m)*R,e[6]=(g*l*r-a*p*r-g*s*c+t*p*c+a*s*m-t*l*m)*R,e[7]=(a*d*r-h*l*r+h*s*c-t*d*c-a*s*f+t*l*f)*R,e[8]=b*R,e[9]=(g*u*r-h*v*r-g*n*f+t*v*f+h*n*m-t*u*m)*R,e[10]=(a*v*r-g*o*r+g*n*c-t*v*c-a*n*m+t*o*m)*R,e[11]=(h*o*r-a*u*r-h*n*c+t*u*c+a*n*f-t*o*f)*R,e[12]=I*R,e[13]=(h*v*s-g*u*s+g*n*d-t*v*d-h*n*p+t*u*p)*R,e[14]=(g*o*s-a*v*s-g*n*l+t*v*l+a*n*p-t*o*p)*R,e[15]=(a*u*s-h*o*s+h*n*l-t*u*l-a*n*d+t*o*d)*R,this}scale(e){const t=this.elements,n=e.x,s=e.y,r=e.z;return t[0]*=n,t[4]*=s,t[8]*=r,t[1]*=n,t[5]*=s,t[9]*=r,t[2]*=n,t[6]*=s,t[10]*=r,t[3]*=n,t[7]*=s,t[11]*=r,this}getMaxScaleOnAxis(){const e=this.elements,t=e[0]*e[0]+e[1]*e[1]+e[2]*e[2],n=e[4]*e[4]+e[5]*e[5]+e[6]*e[6],s=e[8]*e[8]+e[9]*e[9]+e[10]*e[10];return Math.sqrt(Math.max(t,n,s))}makeTranslation(e,t,n){return e.isVector3?this.set(1,0,0,e.x,0,1,0,e.y,0,0,1,e.z,0,0,0,1):this.set(1,0,0,e,0,1,0,t,0,0,1,n,0,0,0,1),this}makeRotationX(e){const t=Math.cos(e),n=Math.sin(e);return this.set(1,0,0,0,0,t,-n,0,0,n,t,0,0,0,0,1),this}makeRotationY(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,0,n,0,0,1,0,0,-n,0,t,0,0,0,0,1),this}makeRotationZ(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,-n,0,0,n,t,0,0,0,0,1,0,0,0,0,1),this}makeRotationAxis(e,t){const n=Math.cos(t),s=Math.sin(t),r=1-n,a=e.x,o=e.y,l=e.z,c=r*a,h=r*o;return this.set(c*a+n,c*o-s*l,c*l+s*o,0,c*o+s*l,h*o+n,h*l-s*a,0,c*l-s*o,h*l+s*a,r*l*l+n,0,0,0,0,1),this}makeScale(e,t,n){return this.set(e,0,0,0,0,t,0,0,0,0,n,0,0,0,0,1),this}makeShear(e,t,n,s,r,a){return this.set(1,n,r,0,e,1,a,0,t,s,1,0,0,0,0,1),this}compose(e,t,n){const s=this.elements,r=t._x,a=t._y,o=t._z,l=t._w,c=r+r,h=a+a,u=o+o,d=r*c,f=r*h,g=r*u,v=a*h,p=a*u,m=o*u,S=l*c,_=l*h,b=l*u,I=n.x,A=n.y,R=n.z;return s[0]=(1-(v+m))*I,s[1]=(f+b)*I,s[2]=(g-_)*I,s[3]=0,s[4]=(f-b)*A,s[5]=(1-(d+m))*A,s[6]=(p+S)*A,s[7]=0,s[8]=(g+_)*R,s[9]=(p-S)*R,s[10]=(1-(d+v))*R,s[11]=0,s[12]=e.x,s[13]=e.y,s[14]=e.z,s[15]=1,this}decompose(e,t,n){const s=this.elements;let r=Mr.set(s[0],s[1],s[2]).length();const a=Mr.set(s[4],s[5],s[6]).length(),o=Mr.set(s[8],s[9],s[10]).length();this.determinant()<0&&(r=-r),e.x=s[12],e.y=s[13],e.z=s[14],fi.copy(this);const c=1/r,h=1/a,u=1/o;return fi.elements[0]*=c,fi.elements[1]*=c,fi.elements[2]*=c,fi.elements[4]*=h,fi.elements[5]*=h,fi.elements[6]*=h,fi.elements[8]*=u,fi.elements[9]*=u,fi.elements[10]*=u,t.setFromRotationMatrix(fi),n.x=r,n.y=a,n.z=o,this}makePerspective(e,t,n,s,r,a,o=Zi){const l=this.elements,c=2*r/(t-e),h=2*r/(n-s),u=(t+e)/(t-e),d=(n+s)/(n-s);let f,g;if(o===Zi)f=-(a+r)/(a-r),g=-2*a*r/(a-r);else if(o===fl)f=-a/(a-r),g=-a*r/(a-r);else throw new Error("THREE.Matrix4.makePerspective(): Invalid coordinate system: "+o);return l[0]=c,l[4]=0,l[8]=u,l[12]=0,l[1]=0,l[5]=h,l[9]=d,l[13]=0,l[2]=0,l[6]=0,l[10]=f,l[14]=g,l[3]=0,l[7]=0,l[11]=-1,l[15]=0,this}makeOrthographic(e,t,n,s,r,a,o=Zi){const l=this.elements,c=1/(t-e),h=1/(n-s),u=1/(a-r),d=(t+e)*c,f=(n+s)*h;let g,v;if(o===Zi)g=(a+r)*u,v=-2*u;else if(o===fl)g=r*u,v=-1*u;else throw new Error("THREE.Matrix4.makeOrthographic(): Invalid coordinate system: "+o);return l[0]=2*c,l[4]=0,l[8]=0,l[12]=-d,l[1]=0,l[5]=2*h,l[9]=0,l[13]=-f,l[2]=0,l[6]=0,l[10]=v,l[14]=-g,l[3]=0,l[7]=0,l[11]=0,l[15]=1,this}equals(e){const t=this.elements,n=e.elements;for(let s=0;s<16;s++)if(t[s]!==n[s])return!1;return!0}fromArray(e,t=0){for(let n=0;n<16;n++)this.elements[n]=e[n+t];return this}toArray(e=[],t=0){const n=this.elements;return e[t]=n[0],e[t+1]=n[1],e[t+2]=n[2],e[t+3]=n[3],e[t+4]=n[4],e[t+5]=n[5],e[t+6]=n[6],e[t+7]=n[7],e[t+8]=n[8],e[t+9]=n[9],e[t+10]=n[10],e[t+11]=n[11],e[t+12]=n[12],e[t+13]=n[13],e[t+14]=n[14],e[t+15]=n[15],e}}const Mr=new V,fi=new zt,bv=new V(0,0,0),Mv=new V(1,1,1),ps=new V,Eo=new V,qn=new V,Qu=new zt,ed=new er;class Oi{constructor(e=0,t=0,n=0,s=Oi.DEFAULT_ORDER){this.isEuler=!0,this._x=e,this._y=t,this._z=n,this._order=s}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get order(){return this._order}set order(e){this._order=e,this._onChangeCallback()}set(e,t,n,s=this._order){return this._x=e,this._y=t,this._z=n,this._order=s,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._order)}copy(e){return this._x=e._x,this._y=e._y,this._z=e._z,this._order=e._order,this._onChangeCallback(),this}setFromRotationMatrix(e,t=this._order,n=!0){const s=e.elements,r=s[0],a=s[4],o=s[8],l=s[1],c=s[5],h=s[9],u=s[2],d=s[6],f=s[10];switch(t){case"XYZ":this._y=Math.asin(Cn(o,-1,1)),Math.abs(o)<.9999999?(this._x=Math.atan2(-h,f),this._z=Math.atan2(-a,r)):(this._x=Math.atan2(d,c),this._z=0);break;case"YXZ":this._x=Math.asin(-Cn(h,-1,1)),Math.abs(h)<.9999999?(this._y=Math.atan2(o,f),this._z=Math.atan2(l,c)):(this._y=Math.atan2(-u,r),this._z=0);break;case"ZXY":this._x=Math.asin(Cn(d,-1,1)),Math.abs(d)<.9999999?(this._y=Math.atan2(-u,f),this._z=Math.atan2(-a,c)):(this._y=0,this._z=Math.atan2(l,r));break;case"ZYX":this._y=Math.asin(-Cn(u,-1,1)),Math.abs(u)<.9999999?(this._x=Math.atan2(d,f),this._z=Math.atan2(l,r)):(this._x=0,this._z=Math.atan2(-a,c));break;case"YZX":this._z=Math.asin(Cn(l,-1,1)),Math.abs(l)<.9999999?(this._x=Math.atan2(-h,c),this._y=Math.atan2(-u,r)):(this._x=0,this._y=Math.atan2(o,f));break;case"XZY":this._z=Math.asin(-Cn(a,-1,1)),Math.abs(a)<.9999999?(this._x=Math.atan2(d,c),this._y=Math.atan2(o,r)):(this._x=Math.atan2(-h,f),this._y=0);break;default:console.warn("THREE.Euler: .setFromRotationMatrix() encountered an unknown order: "+t)}return this._order=t,n===!0&&this._onChangeCallback(),this}setFromQuaternion(e,t,n){return Qu.makeRotationFromQuaternion(e),this.setFromRotationMatrix(Qu,t,n)}setFromVector3(e,t=this._order){return this.set(e.x,e.y,e.z,t)}reorder(e){return ed.setFromEuler(this),this.setFromQuaternion(ed,e)}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._order===this._order}fromArray(e){return this._x=e[0],this._y=e[1],this._z=e[2],e[3]!==void 0&&(this._order=e[3]),this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._order,e}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._order}}Oi.DEFAULT_ORDER="XYZ";class Jh{constructor(){this.mask=1}set(e){this.mask=(1<<e|0)>>>0}enable(e){this.mask|=1<<e|0}enableAll(){this.mask=-1}toggle(e){this.mask^=1<<e|0}disable(e){this.mask&=~(1<<e|0)}disableAll(){this.mask=0}test(e){return(this.mask&e.mask)!==0}isEnabled(e){return(this.mask&(1<<e|0))!==0}}let wv=0;const td=new V,wr=new er,qi=new zt,To=new V,La=new V,Ev=new V,Tv=new er,nd=new V(1,0,0),id=new V(0,1,0),sd=new V(0,0,1),rd={type:"added"},Av={type:"removed"},Er={type:"childadded",child:null},uc={type:"childremoved",child:null};class sn extends pa{constructor(){super(),this.isObject3D=!0,Object.defineProperty(this,"id",{value:wv++}),this.uuid=Qi(),this.name="",this.type="Object3D",this.parent=null,this.children=[],this.up=sn.DEFAULT_UP.clone();const e=new V,t=new Oi,n=new er,s=new V(1,1,1);function r(){n.setFromEuler(t,!1)}function a(){t.setFromQuaternion(n,void 0,!1)}t._onChange(r),n._onChange(a),Object.defineProperties(this,{position:{configurable:!0,enumerable:!0,value:e},rotation:{configurable:!0,enumerable:!0,value:t},quaternion:{configurable:!0,enumerable:!0,value:n},scale:{configurable:!0,enumerable:!0,value:s},modelViewMatrix:{value:new zt},normalMatrix:{value:new ot}}),this.matrix=new zt,this.matrixWorld=new zt,this.matrixAutoUpdate=sn.DEFAULT_MATRIX_AUTO_UPDATE,this.matrixWorldAutoUpdate=sn.DEFAULT_MATRIX_WORLD_AUTO_UPDATE,this.matrixWorldNeedsUpdate=!1,this.layers=new Jh,this.visible=!0,this.castShadow=!1,this.receiveShadow=!1,this.frustumCulled=!0,this.renderOrder=0,this.animations=[],this.userData={}}onBeforeShadow(){}onAfterShadow(){}onBeforeRender(){}onAfterRender(){}applyMatrix4(e){this.matrixAutoUpdate&&this.updateMatrix(),this.matrix.premultiply(e),this.matrix.decompose(this.position,this.quaternion,this.scale)}applyQuaternion(e){return this.quaternion.premultiply(e),this}setRotationFromAxisAngle(e,t){this.quaternion.setFromAxisAngle(e,t)}setRotationFromEuler(e){this.quaternion.setFromEuler(e,!0)}setRotationFromMatrix(e){this.quaternion.setFromRotationMatrix(e)}setRotationFromQuaternion(e){this.quaternion.copy(e)}rotateOnAxis(e,t){return wr.setFromAxisAngle(e,t),this.quaternion.multiply(wr),this}rotateOnWorldAxis(e,t){return wr.setFromAxisAngle(e,t),this.quaternion.premultiply(wr),this}rotateX(e){return this.rotateOnAxis(nd,e)}rotateY(e){return this.rotateOnAxis(id,e)}rotateZ(e){return this.rotateOnAxis(sd,e)}translateOnAxis(e,t){return td.copy(e).applyQuaternion(this.quaternion),this.position.add(td.multiplyScalar(t)),this}translateX(e){return this.translateOnAxis(nd,e)}translateY(e){return this.translateOnAxis(id,e)}translateZ(e){return this.translateOnAxis(sd,e)}localToWorld(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(this.matrixWorld)}worldToLocal(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(qi.copy(this.matrixWorld).invert())}lookAt(e,t,n){e.isVector3?To.copy(e):To.set(e,t,n);const s=this.parent;this.updateWorldMatrix(!0,!1),La.setFromMatrixPosition(this.matrixWorld),this.isCamera||this.isLight?qi.lookAt(La,To,this.up):qi.lookAt(To,La,this.up),this.quaternion.setFromRotationMatrix(qi),s&&(qi.extractRotation(s.matrixWorld),wr.setFromRotationMatrix(qi),this.quaternion.premultiply(wr.invert()))}add(e){if(arguments.length>1){for(let t=0;t<arguments.length;t++)this.add(arguments[t]);return this}return e===this?(console.error("THREE.Object3D.add: object can't be added as a child of itself.",e),this):(e&&e.isObject3D?(e.removeFromParent(),e.parent=this,this.children.push(e),e.dispatchEvent(rd),Er.child=e,this.dispatchEvent(Er),Er.child=null):console.error("THREE.Object3D.add: object not an instance of THREE.Object3D.",e),this)}remove(e){if(arguments.length>1){for(let n=0;n<arguments.length;n++)this.remove(arguments[n]);return this}const t=this.children.indexOf(e);return t!==-1&&(e.parent=null,this.children.splice(t,1),e.dispatchEvent(Av),uc.child=e,this.dispatchEvent(uc),uc.child=null),this}removeFromParent(){const e=this.parent;return e!==null&&e.remove(this),this}clear(){return this.remove(...this.children)}attach(e){return this.updateWorldMatrix(!0,!1),qi.copy(this.matrixWorld).invert(),e.parent!==null&&(e.parent.updateWorldMatrix(!0,!1),qi.multiply(e.parent.matrixWorld)),e.applyMatrix4(qi),e.removeFromParent(),e.parent=this,this.children.push(e),e.updateWorldMatrix(!1,!0),e.dispatchEvent(rd),Er.child=e,this.dispatchEvent(Er),Er.child=null,this}getObjectById(e){return this.getObjectByProperty("id",e)}getObjectByName(e){return this.getObjectByProperty("name",e)}getObjectByProperty(e,t){if(this[e]===t)return this;for(let n=0,s=this.children.length;n<s;n++){const a=this.children[n].getObjectByProperty(e,t);if(a!==void 0)return a}}getObjectsByProperty(e,t,n=[]){this[e]===t&&n.push(this);const s=this.children;for(let r=0,a=s.length;r<a;r++)s[r].getObjectsByProperty(e,t,n);return n}getWorldPosition(e){return this.updateWorldMatrix(!0,!1),e.setFromMatrixPosition(this.matrixWorld)}getWorldQuaternion(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(La,e,Ev),e}getWorldScale(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(La,Tv,e),e}getWorldDirection(e){this.updateWorldMatrix(!0,!1);const t=this.matrixWorld.elements;return e.set(t[8],t[9],t[10]).normalize()}raycast(){}traverse(e){e(this);const t=this.children;for(let n=0,s=t.length;n<s;n++)t[n].traverse(e)}traverseVisible(e){if(this.visible===!1)return;e(this);const t=this.children;for(let n=0,s=t.length;n<s;n++)t[n].traverseVisible(e)}traverseAncestors(e){const t=this.parent;t!==null&&(e(t),t.traverseAncestors(e))}updateMatrix(){this.matrix.compose(this.position,this.quaternion,this.scale),this.matrixWorldNeedsUpdate=!0}updateMatrixWorld(e){this.matrixAutoUpdate&&this.updateMatrix(),(this.matrixWorldNeedsUpdate||e)&&(this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),this.matrixWorldNeedsUpdate=!1,e=!0);const t=this.children;for(let n=0,s=t.length;n<s;n++)t[n].updateMatrixWorld(e)}updateWorldMatrix(e,t){const n=this.parent;if(e===!0&&n!==null&&n.updateWorldMatrix(!0,!1),this.matrixAutoUpdate&&this.updateMatrix(),this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),t===!0){const s=this.children;for(let r=0,a=s.length;r<a;r++)s[r].updateWorldMatrix(!1,!0)}}toJSON(e){const t=e===void 0||typeof e=="string",n={};t&&(e={geometries:{},materials:{},textures:{},images:{},shapes:{},skeletons:{},animations:{},nodes:{}},n.metadata={version:4.6,type:"Object",generator:"Object3D.toJSON"});const s={};s.uuid=this.uuid,s.type=this.type,this.name!==""&&(s.name=this.name),this.castShadow===!0&&(s.castShadow=!0),this.receiveShadow===!0&&(s.receiveShadow=!0),this.visible===!1&&(s.visible=!1),this.frustumCulled===!1&&(s.frustumCulled=!1),this.renderOrder!==0&&(s.renderOrder=this.renderOrder),Object.keys(this.userData).length>0&&(s.userData=this.userData),s.layers=this.layers.mask,s.matrix=this.matrix.toArray(),s.up=this.up.toArray(),this.matrixAutoUpdate===!1&&(s.matrixAutoUpdate=!1),this.isInstancedMesh&&(s.type="InstancedMesh",s.count=this.count,s.instanceMatrix=this.instanceMatrix.toJSON(),this.instanceColor!==null&&(s.instanceColor=this.instanceColor.toJSON())),this.isBatchedMesh&&(s.type="BatchedMesh",s.perObjectFrustumCulled=this.perObjectFrustumCulled,s.sortObjects=this.sortObjects,s.drawRanges=this._drawRanges,s.reservedRanges=this._reservedRanges,s.visibility=this._visibility,s.active=this._active,s.bounds=this._bounds.map(o=>({boxInitialized:o.boxInitialized,boxMin:o.box.min.toArray(),boxMax:o.box.max.toArray(),sphereInitialized:o.sphereInitialized,sphereRadius:o.sphere.radius,sphereCenter:o.sphere.center.toArray()})),s.maxInstanceCount=this._maxInstanceCount,s.maxVertexCount=this._maxVertexCount,s.maxIndexCount=this._maxIndexCount,s.geometryInitialized=this._geometryInitialized,s.geometryCount=this._geometryCount,s.matricesTexture=this._matricesTexture.toJSON(e),this._colorsTexture!==null&&(s.colorsTexture=this._colorsTexture.toJSON(e)),this.boundingSphere!==null&&(s.boundingSphere={center:s.boundingSphere.center.toArray(),radius:s.boundingSphere.radius}),this.boundingBox!==null&&(s.boundingBox={min:s.boundingBox.min.toArray(),max:s.boundingBox.max.toArray()}));function r(o,l){return o[l.uuid]===void 0&&(o[l.uuid]=l.toJSON(e)),l.uuid}if(this.isScene)this.background&&(this.background.isColor?s.background=this.background.toJSON():this.background.isTexture&&(s.background=this.background.toJSON(e).uuid)),this.environment&&this.environment.isTexture&&this.environment.isRenderTargetTexture!==!0&&(s.environment=this.environment.toJSON(e).uuid);else if(this.isMesh||this.isLine||this.isPoints){s.geometry=r(e.geometries,this.geometry);const o=this.geometry.parameters;if(o!==void 0&&o.shapes!==void 0){const l=o.shapes;if(Array.isArray(l))for(let c=0,h=l.length;c<h;c++){const u=l[c];r(e.shapes,u)}else r(e.shapes,l)}}if(this.isSkinnedMesh&&(s.bindMode=this.bindMode,s.bindMatrix=this.bindMatrix.toArray(),this.skeleton!==void 0&&(r(e.skeletons,this.skeleton),s.skeleton=this.skeleton.uuid)),this.material!==void 0)if(Array.isArray(this.material)){const o=[];for(let l=0,c=this.material.length;l<c;l++)o.push(r(e.materials,this.material[l]));s.material=o}else s.material=r(e.materials,this.material);if(this.children.length>0){s.children=[];for(let o=0;o<this.children.length;o++)s.children.push(this.children[o].toJSON(e).object)}if(this.animations.length>0){s.animations=[];for(let o=0;o<this.animations.length;o++){const l=this.animations[o];s.animations.push(r(e.animations,l))}}if(t){const o=a(e.geometries),l=a(e.materials),c=a(e.textures),h=a(e.images),u=a(e.shapes),d=a(e.skeletons),f=a(e.animations),g=a(e.nodes);o.length>0&&(n.geometries=o),l.length>0&&(n.materials=l),c.length>0&&(n.textures=c),h.length>0&&(n.images=h),u.length>0&&(n.shapes=u),d.length>0&&(n.skeletons=d),f.length>0&&(n.animations=f),g.length>0&&(n.nodes=g)}return n.object=s,n;function a(o){const l=[];for(const c in o){const h=o[c];delete h.metadata,l.push(h)}return l}}clone(e){return new this.constructor().copy(this,e)}copy(e,t=!0){if(this.name=e.name,this.up.copy(e.up),this.position.copy(e.position),this.rotation.order=e.rotation.order,this.quaternion.copy(e.quaternion),this.scale.copy(e.scale),this.matrix.copy(e.matrix),this.matrixWorld.copy(e.matrixWorld),this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrixWorldAutoUpdate=e.matrixWorldAutoUpdate,this.matrixWorldNeedsUpdate=e.matrixWorldNeedsUpdate,this.layers.mask=e.layers.mask,this.visible=e.visible,this.castShadow=e.castShadow,this.receiveShadow=e.receiveShadow,this.frustumCulled=e.frustumCulled,this.renderOrder=e.renderOrder,this.animations=e.animations.slice(),this.userData=JSON.parse(JSON.stringify(e.userData)),t===!0)for(let n=0;n<e.children.length;n++){const s=e.children[n];this.add(s.clone())}return this}}sn.DEFAULT_UP=new V(0,1,0);sn.DEFAULT_MATRIX_AUTO_UPDATE=!0;sn.DEFAULT_MATRIX_WORLD_AUTO_UPDATE=!0;const pi=new V,Xi=new V,dc=new V,Yi=new V,Tr=new V,Ar=new V,ad=new V,fc=new V,pc=new V,mc=new V;class ri{constructor(e=new V,t=new V,n=new V){this.a=e,this.b=t,this.c=n}static getNormal(e,t,n,s){s.subVectors(n,t),pi.subVectors(e,t),s.cross(pi);const r=s.lengthSq();return r>0?s.multiplyScalar(1/Math.sqrt(r)):s.set(0,0,0)}static getBarycoord(e,t,n,s,r){pi.subVectors(s,t),Xi.subVectors(n,t),dc.subVectors(e,t);const a=pi.dot(pi),o=pi.dot(Xi),l=pi.dot(dc),c=Xi.dot(Xi),h=Xi.dot(dc),u=a*c-o*o;if(u===0)return r.set(0,0,0),null;const d=1/u,f=(c*l-o*h)*d,g=(a*h-o*l)*d;return r.set(1-f-g,g,f)}static containsPoint(e,t,n,s){return this.getBarycoord(e,t,n,s,Yi)===null?!1:Yi.x>=0&&Yi.y>=0&&Yi.x+Yi.y<=1}static getInterpolation(e,t,n,s,r,a,o,l){return this.getBarycoord(e,t,n,s,Yi)===null?(l.x=0,l.y=0,"z"in l&&(l.z=0),"w"in l&&(l.w=0),null):(l.setScalar(0),l.addScaledVector(r,Yi.x),l.addScaledVector(a,Yi.y),l.addScaledVector(o,Yi.z),l)}static isFrontFacing(e,t,n,s){return pi.subVectors(n,t),Xi.subVectors(e,t),pi.cross(Xi).dot(s)<0}set(e,t,n){return this.a.copy(e),this.b.copy(t),this.c.copy(n),this}setFromPointsAndIndices(e,t,n,s){return this.a.copy(e[t]),this.b.copy(e[n]),this.c.copy(e[s]),this}setFromAttributeAndIndices(e,t,n,s){return this.a.fromBufferAttribute(e,t),this.b.fromBufferAttribute(e,n),this.c.fromBufferAttribute(e,s),this}clone(){return new this.constructor().copy(this)}copy(e){return this.a.copy(e.a),this.b.copy(e.b),this.c.copy(e.c),this}getArea(){return pi.subVectors(this.c,this.b),Xi.subVectors(this.a,this.b),pi.cross(Xi).length()*.5}getMidpoint(e){return e.addVectors(this.a,this.b).add(this.c).multiplyScalar(1/3)}getNormal(e){return ri.getNormal(this.a,this.b,this.c,e)}getPlane(e){return e.setFromCoplanarPoints(this.a,this.b,this.c)}getBarycoord(e,t){return ri.getBarycoord(e,this.a,this.b,this.c,t)}getInterpolation(e,t,n,s,r){return ri.getInterpolation(e,this.a,this.b,this.c,t,n,s,r)}containsPoint(e){return ri.containsPoint(e,this.a,this.b,this.c)}isFrontFacing(e){return ri.isFrontFacing(this.a,this.b,this.c,e)}intersectsBox(e){return e.intersectsTriangle(this)}closestPointToPoint(e,t){const n=this.a,s=this.b,r=this.c;let a,o;Tr.subVectors(s,n),Ar.subVectors(r,n),fc.subVectors(e,n);const l=Tr.dot(fc),c=Ar.dot(fc);if(l<=0&&c<=0)return t.copy(n);pc.subVectors(e,s);const h=Tr.dot(pc),u=Ar.dot(pc);if(h>=0&&u<=h)return t.copy(s);const d=l*u-h*c;if(d<=0&&l>=0&&h<=0)return a=l/(l-h),t.copy(n).addScaledVector(Tr,a);mc.subVectors(e,r);const f=Tr.dot(mc),g=Ar.dot(mc);if(g>=0&&f<=g)return t.copy(r);const v=f*c-l*g;if(v<=0&&c>=0&&g<=0)return o=c/(c-g),t.copy(n).addScaledVector(Ar,o);const p=h*g-f*u;if(p<=0&&u-h>=0&&f-g>=0)return ad.subVectors(r,s),o=(u-h)/(u-h+(f-g)),t.copy(s).addScaledVector(ad,o);const m=1/(p+v+d);return a=v*m,o=d*m,t.copy(n).addScaledVector(Tr,a).addScaledVector(Ar,o)}equals(e){return e.a.equals(this.a)&&e.b.equals(this.b)&&e.c.equals(this.c)}}const _p={aliceblue:15792383,antiquewhite:16444375,aqua:65535,aquamarine:8388564,azure:15794175,beige:16119260,bisque:16770244,black:0,blanchedalmond:16772045,blue:255,blueviolet:9055202,brown:10824234,burlywood:14596231,cadetblue:6266528,chartreuse:8388352,chocolate:13789470,coral:16744272,cornflowerblue:6591981,cornsilk:16775388,crimson:14423100,cyan:65535,darkblue:139,darkcyan:35723,darkgoldenrod:12092939,darkgray:11119017,darkgreen:25600,darkgrey:11119017,darkkhaki:12433259,darkmagenta:9109643,darkolivegreen:5597999,darkorange:16747520,darkorchid:10040012,darkred:9109504,darksalmon:15308410,darkseagreen:9419919,darkslateblue:4734347,darkslategray:3100495,darkslategrey:3100495,darkturquoise:52945,darkviolet:9699539,deeppink:16716947,deepskyblue:49151,dimgray:6908265,dimgrey:6908265,dodgerblue:2003199,firebrick:11674146,floralwhite:16775920,forestgreen:2263842,fuchsia:16711935,gainsboro:14474460,ghostwhite:16316671,gold:16766720,goldenrod:14329120,gray:8421504,green:32768,greenyellow:11403055,grey:8421504,honeydew:15794160,hotpink:16738740,indianred:13458524,indigo:4915330,ivory:16777200,khaki:15787660,lavender:15132410,lavenderblush:16773365,lawngreen:8190976,lemonchiffon:16775885,lightblue:11393254,lightcoral:15761536,lightcyan:14745599,lightgoldenrodyellow:16448210,lightgray:13882323,lightgreen:9498256,lightgrey:13882323,lightpink:16758465,lightsalmon:16752762,lightseagreen:2142890,lightskyblue:8900346,lightslategray:7833753,lightslategrey:7833753,lightsteelblue:11584734,lightyellow:16777184,lime:65280,limegreen:3329330,linen:16445670,magenta:16711935,maroon:8388608,mediumaquamarine:6737322,mediumblue:205,mediumorchid:12211667,mediumpurple:9662683,mediumseagreen:3978097,mediumslateblue:8087790,mediumspringgreen:64154,mediumturquoise:4772300,mediumvioletred:13047173,midnightblue:1644912,mintcream:16121850,mistyrose:16770273,moccasin:16770229,navajowhite:16768685,navy:128,oldlace:16643558,olive:8421376,olivedrab:7048739,orange:16753920,orangered:16729344,orchid:14315734,palegoldenrod:15657130,palegreen:10025880,paleturquoise:11529966,palevioletred:14381203,papayawhip:16773077,peachpuff:16767673,peru:13468991,pink:16761035,plum:14524637,powderblue:11591910,purple:8388736,rebeccapurple:6697881,red:16711680,rosybrown:12357519,royalblue:4286945,saddlebrown:9127187,salmon:16416882,sandybrown:16032864,seagreen:3050327,seashell:16774638,sienna:10506797,silver:12632256,skyblue:8900331,slateblue:6970061,slategray:7372944,slategrey:7372944,snow:16775930,springgreen:65407,steelblue:4620980,tan:13808780,teal:32896,thistle:14204888,tomato:16737095,turquoise:4251856,violet:15631086,wheat:16113331,white:16777215,whitesmoke:16119285,yellow:16776960,yellowgreen:10145074},ms={h:0,s:0,l:0},Ao={h:0,s:0,l:0};function gc(i,e,t){return t<0&&(t+=1),t>1&&(t-=1),t<1/6?i+(e-i)*6*t:t<1/2?e:t<2/3?i+(e-i)*6*(2/3-t):i}class it{constructor(e,t,n){return this.isColor=!0,this.r=1,this.g=1,this.b=1,this.set(e,t,n)}set(e,t,n){if(t===void 0&&n===void 0){const s=e;s&&s.isColor?this.copy(s):typeof s=="number"?this.setHex(s):typeof s=="string"&&this.setStyle(s)}else this.setRGB(e,t,n);return this}setScalar(e){return this.r=e,this.g=e,this.b=e,this}setHex(e,t=Ui){return e=Math.floor(e),this.r=(e>>16&255)/255,this.g=(e>>8&255)/255,this.b=(e&255)/255,wt.toWorkingColorSpace(this,t),this}setRGB(e,t,n,s=wt.workingColorSpace){return this.r=e,this.g=t,this.b=n,wt.toWorkingColorSpace(this,s),this}setHSL(e,t,n,s=wt.workingColorSpace){if(e=Kh(e,1),t=Cn(t,0,1),n=Cn(n,0,1),t===0)this.r=this.g=this.b=n;else{const r=n<=.5?n*(1+t):n+t-n*t,a=2*n-r;this.r=gc(a,r,e+1/3),this.g=gc(a,r,e),this.b=gc(a,r,e-1/3)}return wt.toWorkingColorSpace(this,s),this}setStyle(e,t=Ui){function n(r){r!==void 0&&parseFloat(r)<1&&console.warn("THREE.Color: Alpha component of "+e+" will be ignored.")}let s;if(s=/^(\w+)\(([^\)]*)\)/.exec(e)){let r;const a=s[1],o=s[2];switch(a){case"rgb":case"rgba":if(r=/^\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(o))return n(r[4]),this.setRGB(Math.min(255,parseInt(r[1],10))/255,Math.min(255,parseInt(r[2],10))/255,Math.min(255,parseInt(r[3],10))/255,t);if(r=/^\s*(\d+)\%\s*,\s*(\d+)\%\s*,\s*(\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(o))return n(r[4]),this.setRGB(Math.min(100,parseInt(r[1],10))/100,Math.min(100,parseInt(r[2],10))/100,Math.min(100,parseInt(r[3],10))/100,t);break;case"hsl":case"hsla":if(r=/^\s*(\d*\.?\d+)\s*,\s*(\d*\.?\d+)\%\s*,\s*(\d*\.?\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(o))return n(r[4]),this.setHSL(parseFloat(r[1])/360,parseFloat(r[2])/100,parseFloat(r[3])/100,t);break;default:console.warn("THREE.Color: Unknown color model "+e)}}else if(s=/^\#([A-Fa-f\d]+)$/.exec(e)){const r=s[1],a=r.length;if(a===3)return this.setRGB(parseInt(r.charAt(0),16)/15,parseInt(r.charAt(1),16)/15,parseInt(r.charAt(2),16)/15,t);if(a===6)return this.setHex(parseInt(r,16),t);console.warn("THREE.Color: Invalid hex color "+e)}else if(e&&e.length>0)return this.setColorName(e,t);return this}setColorName(e,t=Ui){const n=_p[e.toLowerCase()];return n!==void 0?this.setHex(n,t):console.warn("THREE.Color: Unknown color "+e),this}clone(){return new this.constructor(this.r,this.g,this.b)}copy(e){return this.r=e.r,this.g=e.g,this.b=e.b,this}copySRGBToLinear(e){return this.r=jr(e.r),this.g=jr(e.g),this.b=jr(e.b),this}copyLinearToSRGB(e){return this.r=ic(e.r),this.g=ic(e.g),this.b=ic(e.b),this}convertSRGBToLinear(){return this.copySRGBToLinear(this),this}convertLinearToSRGB(){return this.copyLinearToSRGB(this),this}getHex(e=Ui){return wt.fromWorkingColorSpace(An.copy(this),e),Math.round(Cn(An.r*255,0,255))*65536+Math.round(Cn(An.g*255,0,255))*256+Math.round(Cn(An.b*255,0,255))}getHexString(e=Ui){return("000000"+this.getHex(e).toString(16)).slice(-6)}getHSL(e,t=wt.workingColorSpace){wt.fromWorkingColorSpace(An.copy(this),t);const n=An.r,s=An.g,r=An.b,a=Math.max(n,s,r),o=Math.min(n,s,r);let l,c;const h=(o+a)/2;if(o===a)l=0,c=0;else{const u=a-o;switch(c=h<=.5?u/(a+o):u/(2-a-o),a){case n:l=(s-r)/u+(s<r?6:0);break;case s:l=(r-n)/u+2;break;case r:l=(n-s)/u+4;break}l/=6}return e.h=l,e.s=c,e.l=h,e}getRGB(e,t=wt.workingColorSpace){return wt.fromWorkingColorSpace(An.copy(this),t),e.r=An.r,e.g=An.g,e.b=An.b,e}getStyle(e=Ui){wt.fromWorkingColorSpace(An.copy(this),e);const t=An.r,n=An.g,s=An.b;return e!==Ui?`color(${e} ${t.toFixed(3)} ${n.toFixed(3)} ${s.toFixed(3)})`:`rgb(${Math.round(t*255)},${Math.round(n*255)},${Math.round(s*255)})`}offsetHSL(e,t,n){return this.getHSL(ms),this.setHSL(ms.h+e,ms.s+t,ms.l+n)}add(e){return this.r+=e.r,this.g+=e.g,this.b+=e.b,this}addColors(e,t){return this.r=e.r+t.r,this.g=e.g+t.g,this.b=e.b+t.b,this}addScalar(e){return this.r+=e,this.g+=e,this.b+=e,this}sub(e){return this.r=Math.max(0,this.r-e.r),this.g=Math.max(0,this.g-e.g),this.b=Math.max(0,this.b-e.b),this}multiply(e){return this.r*=e.r,this.g*=e.g,this.b*=e.b,this}multiplyScalar(e){return this.r*=e,this.g*=e,this.b*=e,this}lerp(e,t){return this.r+=(e.r-this.r)*t,this.g+=(e.g-this.g)*t,this.b+=(e.b-this.b)*t,this}lerpColors(e,t,n){return this.r=e.r+(t.r-e.r)*n,this.g=e.g+(t.g-e.g)*n,this.b=e.b+(t.b-e.b)*n,this}lerpHSL(e,t){this.getHSL(ms),e.getHSL(Ao);const n=qa(ms.h,Ao.h,t),s=qa(ms.s,Ao.s,t),r=qa(ms.l,Ao.l,t);return this.setHSL(n,s,r),this}setFromVector3(e){return this.r=e.x,this.g=e.y,this.b=e.z,this}applyMatrix3(e){const t=this.r,n=this.g,s=this.b,r=e.elements;return this.r=r[0]*t+r[3]*n+r[6]*s,this.g=r[1]*t+r[4]*n+r[7]*s,this.b=r[2]*t+r[5]*n+r[8]*s,this}equals(e){return e.r===this.r&&e.g===this.g&&e.b===this.b}fromArray(e,t=0){return this.r=e[t],this.g=e[t+1],this.b=e[t+2],this}toArray(e=[],t=0){return e[t]=this.r,e[t+1]=this.g,e[t+2]=this.b,e}fromBufferAttribute(e,t){return this.r=e.getX(t),this.g=e.getY(t),this.b=e.getZ(t),this}toJSON(){return this.getHex()}*[Symbol.iterator](){yield this.r,yield this.g,yield this.b}}const An=new it;it.NAMES=_p;let Cv=0;class Rs extends pa{constructor(){super(),this.isMaterial=!0,Object.defineProperty(this,"id",{value:Cv++}),this.uuid=Qi(),this.name="",this.type="Material",this.blending=$r,this.side=Ms,this.vertexColors=!1,this.opacity=1,this.transparent=!1,this.alphaHash=!1,this.blendSrc=qc,this.blendDst=Xc,this.blendEquation=$s,this.blendSrcAlpha=null,this.blendDstAlpha=null,this.blendEquationAlpha=null,this.blendColor=new it(0,0,0),this.blendAlpha=0,this.depthFunc=cl,this.depthTest=!0,this.depthWrite=!0,this.stencilWriteMask=255,this.stencilFunc=qu,this.stencilRef=0,this.stencilFuncMask=255,this.stencilFail=xr,this.stencilZFail=xr,this.stencilZPass=xr,this.stencilWrite=!1,this.clippingPlanes=null,this.clipIntersection=!1,this.clipShadows=!1,this.shadowSide=null,this.colorWrite=!0,this.precision=null,this.polygonOffset=!1,this.polygonOffsetFactor=0,this.polygonOffsetUnits=0,this.dithering=!1,this.alphaToCoverage=!1,this.premultipliedAlpha=!1,this.forceSinglePass=!1,this.visible=!0,this.toneMapped=!0,this.userData={},this.version=0,this._alphaTest=0}get alphaTest(){return this._alphaTest}set alphaTest(e){this._alphaTest>0!=e>0&&this.version++,this._alphaTest=e}onBeforeRender(){}onBeforeCompile(){}customProgramCacheKey(){return this.onBeforeCompile.toString()}setValues(e){if(e!==void 0)for(const t in e){const n=e[t];if(n===void 0){console.warn(`THREE.Material: parameter '${t}' has value of undefined.`);continue}const s=this[t];if(s===void 0){console.warn(`THREE.Material: '${t}' is not a property of THREE.${this.type}.`);continue}s&&s.isColor?s.set(n):s&&s.isVector3&&n&&n.isVector3?s.copy(n):this[t]=n}}toJSON(e){const t=e===void 0||typeof e=="string";t&&(e={textures:{},images:{}});const n={metadata:{version:4.6,type:"Material",generator:"Material.toJSON"}};n.uuid=this.uuid,n.type=this.type,this.name!==""&&(n.name=this.name),this.color&&this.color.isColor&&(n.color=this.color.getHex()),this.roughness!==void 0&&(n.roughness=this.roughness),this.metalness!==void 0&&(n.metalness=this.metalness),this.sheen!==void 0&&(n.sheen=this.sheen),this.sheenColor&&this.sheenColor.isColor&&(n.sheenColor=this.sheenColor.getHex()),this.sheenRoughness!==void 0&&(n.sheenRoughness=this.sheenRoughness),this.emissive&&this.emissive.isColor&&(n.emissive=this.emissive.getHex()),this.emissiveIntensity!==void 0&&this.emissiveIntensity!==1&&(n.emissiveIntensity=this.emissiveIntensity),this.specular&&this.specular.isColor&&(n.specular=this.specular.getHex()),this.specularIntensity!==void 0&&(n.specularIntensity=this.specularIntensity),this.specularColor&&this.specularColor.isColor&&(n.specularColor=this.specularColor.getHex()),this.shininess!==void 0&&(n.shininess=this.shininess),this.clearcoat!==void 0&&(n.clearcoat=this.clearcoat),this.clearcoatRoughness!==void 0&&(n.clearcoatRoughness=this.clearcoatRoughness),this.clearcoatMap&&this.clearcoatMap.isTexture&&(n.clearcoatMap=this.clearcoatMap.toJSON(e).uuid),this.clearcoatRoughnessMap&&this.clearcoatRoughnessMap.isTexture&&(n.clearcoatRoughnessMap=this.clearcoatRoughnessMap.toJSON(e).uuid),this.clearcoatNormalMap&&this.clearcoatNormalMap.isTexture&&(n.clearcoatNormalMap=this.clearcoatNormalMap.toJSON(e).uuid,n.clearcoatNormalScale=this.clearcoatNormalScale.toArray()),this.dispersion!==void 0&&(n.dispersion=this.dispersion),this.iridescence!==void 0&&(n.iridescence=this.iridescence),this.iridescenceIOR!==void 0&&(n.iridescenceIOR=this.iridescenceIOR),this.iridescenceThicknessRange!==void 0&&(n.iridescenceThicknessRange=this.iridescenceThicknessRange),this.iridescenceMap&&this.iridescenceMap.isTexture&&(n.iridescenceMap=this.iridescenceMap.toJSON(e).uuid),this.iridescenceThicknessMap&&this.iridescenceThicknessMap.isTexture&&(n.iridescenceThicknessMap=this.iridescenceThicknessMap.toJSON(e).uuid),this.anisotropy!==void 0&&(n.anisotropy=this.anisotropy),this.anisotropyRotation!==void 0&&(n.anisotropyRotation=this.anisotropyRotation),this.anisotropyMap&&this.anisotropyMap.isTexture&&(n.anisotropyMap=this.anisotropyMap.toJSON(e).uuid),this.map&&this.map.isTexture&&(n.map=this.map.toJSON(e).uuid),this.matcap&&this.matcap.isTexture&&(n.matcap=this.matcap.toJSON(e).uuid),this.alphaMap&&this.alphaMap.isTexture&&(n.alphaMap=this.alphaMap.toJSON(e).uuid),this.lightMap&&this.lightMap.isTexture&&(n.lightMap=this.lightMap.toJSON(e).uuid,n.lightMapIntensity=this.lightMapIntensity),this.aoMap&&this.aoMap.isTexture&&(n.aoMap=this.aoMap.toJSON(e).uuid,n.aoMapIntensity=this.aoMapIntensity),this.bumpMap&&this.bumpMap.isTexture&&(n.bumpMap=this.bumpMap.toJSON(e).uuid,n.bumpScale=this.bumpScale),this.normalMap&&this.normalMap.isTexture&&(n.normalMap=this.normalMap.toJSON(e).uuid,n.normalMapType=this.normalMapType,n.normalScale=this.normalScale.toArray()),this.displacementMap&&this.displacementMap.isTexture&&(n.displacementMap=this.displacementMap.toJSON(e).uuid,n.displacementScale=this.displacementScale,n.displacementBias=this.displacementBias),this.roughnessMap&&this.roughnessMap.isTexture&&(n.roughnessMap=this.roughnessMap.toJSON(e).uuid),this.metalnessMap&&this.metalnessMap.isTexture&&(n.metalnessMap=this.metalnessMap.toJSON(e).uuid),this.emissiveMap&&this.emissiveMap.isTexture&&(n.emissiveMap=this.emissiveMap.toJSON(e).uuid),this.specularMap&&this.specularMap.isTexture&&(n.specularMap=this.specularMap.toJSON(e).uuid),this.specularIntensityMap&&this.specularIntensityMap.isTexture&&(n.specularIntensityMap=this.specularIntensityMap.toJSON(e).uuid),this.specularColorMap&&this.specularColorMap.isTexture&&(n.specularColorMap=this.specularColorMap.toJSON(e).uuid),this.envMap&&this.envMap.isTexture&&(n.envMap=this.envMap.toJSON(e).uuid,this.combine!==void 0&&(n.combine=this.combine)),this.envMapRotation!==void 0&&(n.envMapRotation=this.envMapRotation.toArray()),this.envMapIntensity!==void 0&&(n.envMapIntensity=this.envMapIntensity),this.reflectivity!==void 0&&(n.reflectivity=this.reflectivity),this.refractionRatio!==void 0&&(n.refractionRatio=this.refractionRatio),this.gradientMap&&this.gradientMap.isTexture&&(n.gradientMap=this.gradientMap.toJSON(e).uuid),this.transmission!==void 0&&(n.transmission=this.transmission),this.transmissionMap&&this.transmissionMap.isTexture&&(n.transmissionMap=this.transmissionMap.toJSON(e).uuid),this.thickness!==void 0&&(n.thickness=this.thickness),this.thicknessMap&&this.thicknessMap.isTexture&&(n.thicknessMap=this.thicknessMap.toJSON(e).uuid),this.attenuationDistance!==void 0&&this.attenuationDistance!==1/0&&(n.attenuationDistance=this.attenuationDistance),this.attenuationColor!==void 0&&(n.attenuationColor=this.attenuationColor.getHex()),this.size!==void 0&&(n.size=this.size),this.shadowSide!==null&&(n.shadowSide=this.shadowSide),this.sizeAttenuation!==void 0&&(n.sizeAttenuation=this.sizeAttenuation),this.blending!==$r&&(n.blending=this.blending),this.side!==Ms&&(n.side=this.side),this.vertexColors===!0&&(n.vertexColors=!0),this.opacity<1&&(n.opacity=this.opacity),this.transparent===!0&&(n.transparent=!0),this.blendSrc!==qc&&(n.blendSrc=this.blendSrc),this.blendDst!==Xc&&(n.blendDst=this.blendDst),this.blendEquation!==$s&&(n.blendEquation=this.blendEquation),this.blendSrcAlpha!==null&&(n.blendSrcAlpha=this.blendSrcAlpha),this.blendDstAlpha!==null&&(n.blendDstAlpha=this.blendDstAlpha),this.blendEquationAlpha!==null&&(n.blendEquationAlpha=this.blendEquationAlpha),this.blendColor&&this.blendColor.isColor&&(n.blendColor=this.blendColor.getHex()),this.blendAlpha!==0&&(n.blendAlpha=this.blendAlpha),this.depthFunc!==cl&&(n.depthFunc=this.depthFunc),this.depthTest===!1&&(n.depthTest=this.depthTest),this.depthWrite===!1&&(n.depthWrite=this.depthWrite),this.colorWrite===!1&&(n.colorWrite=this.colorWrite),this.stencilWriteMask!==255&&(n.stencilWriteMask=this.stencilWriteMask),this.stencilFunc!==qu&&(n.stencilFunc=this.stencilFunc),this.stencilRef!==0&&(n.stencilRef=this.stencilRef),this.stencilFuncMask!==255&&(n.stencilFuncMask=this.stencilFuncMask),this.stencilFail!==xr&&(n.stencilFail=this.stencilFail),this.stencilZFail!==xr&&(n.stencilZFail=this.stencilZFail),this.stencilZPass!==xr&&(n.stencilZPass=this.stencilZPass),this.stencilWrite===!0&&(n.stencilWrite=this.stencilWrite),this.rotation!==void 0&&this.rotation!==0&&(n.rotation=this.rotation),this.polygonOffset===!0&&(n.polygonOffset=!0),this.polygonOffsetFactor!==0&&(n.polygonOffsetFactor=this.polygonOffsetFactor),this.polygonOffsetUnits!==0&&(n.polygonOffsetUnits=this.polygonOffsetUnits),this.linewidth!==void 0&&this.linewidth!==1&&(n.linewidth=this.linewidth),this.dashSize!==void 0&&(n.dashSize=this.dashSize),this.gapSize!==void 0&&(n.gapSize=this.gapSize),this.scale!==void 0&&(n.scale=this.scale),this.dithering===!0&&(n.dithering=!0),this.alphaTest>0&&(n.alphaTest=this.alphaTest),this.alphaHash===!0&&(n.alphaHash=!0),this.alphaToCoverage===!0&&(n.alphaToCoverage=!0),this.premultipliedAlpha===!0&&(n.premultipliedAlpha=!0),this.forceSinglePass===!0&&(n.forceSinglePass=!0),this.wireframe===!0&&(n.wireframe=!0),this.wireframeLinewidth>1&&(n.wireframeLinewidth=this.wireframeLinewidth),this.wireframeLinecap!=="round"&&(n.wireframeLinecap=this.wireframeLinecap),this.wireframeLinejoin!=="round"&&(n.wireframeLinejoin=this.wireframeLinejoin),this.flatShading===!0&&(n.flatShading=!0),this.visible===!1&&(n.visible=!1),this.toneMapped===!1&&(n.toneMapped=!1),this.fog===!1&&(n.fog=!1),Object.keys(this.userData).length>0&&(n.userData=this.userData);function s(r){const a=[];for(const o in r){const l=r[o];delete l.metadata,a.push(l)}return a}if(t){const r=s(e.textures),a=s(e.images);r.length>0&&(n.textures=r),a.length>0&&(n.images=a)}return n}clone(){return new this.constructor().copy(this)}copy(e){this.name=e.name,this.blending=e.blending,this.side=e.side,this.vertexColors=e.vertexColors,this.opacity=e.opacity,this.transparent=e.transparent,this.blendSrc=e.blendSrc,this.blendDst=e.blendDst,this.blendEquation=e.blendEquation,this.blendSrcAlpha=e.blendSrcAlpha,this.blendDstAlpha=e.blendDstAlpha,this.blendEquationAlpha=e.blendEquationAlpha,this.blendColor.copy(e.blendColor),this.blendAlpha=e.blendAlpha,this.depthFunc=e.depthFunc,this.depthTest=e.depthTest,this.depthWrite=e.depthWrite,this.stencilWriteMask=e.stencilWriteMask,this.stencilFunc=e.stencilFunc,this.stencilRef=e.stencilRef,this.stencilFuncMask=e.stencilFuncMask,this.stencilFail=e.stencilFail,this.stencilZFail=e.stencilZFail,this.stencilZPass=e.stencilZPass,this.stencilWrite=e.stencilWrite;const t=e.clippingPlanes;let n=null;if(t!==null){const s=t.length;n=new Array(s);for(let r=0;r!==s;++r)n[r]=t[r].clone()}return this.clippingPlanes=n,this.clipIntersection=e.clipIntersection,this.clipShadows=e.clipShadows,this.shadowSide=e.shadowSide,this.colorWrite=e.colorWrite,this.precision=e.precision,this.polygonOffset=e.polygonOffset,this.polygonOffsetFactor=e.polygonOffsetFactor,this.polygonOffsetUnits=e.polygonOffsetUnits,this.dithering=e.dithering,this.alphaTest=e.alphaTest,this.alphaHash=e.alphaHash,this.alphaToCoverage=e.alphaToCoverage,this.premultipliedAlpha=e.premultipliedAlpha,this.forceSinglePass=e.forceSinglePass,this.visible=e.visible,this.toneMapped=e.toneMapped,this.userData=JSON.parse(JSON.stringify(e.userData)),this}dispose(){this.dispatchEvent({type:"dispose"})}set needsUpdate(e){e===!0&&this.version++}onBuild(){console.warn("Material: onBuild() has been removed.")}}class es extends Rs{constructor(e){super(),this.isMeshBasicMaterial=!0,this.type="MeshBasicMaterial",this.color=new it(16777215),this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.specularMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new Oi,this.combine=tp,this.reflectivity=1,this.refractionRatio=.98,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.lightMap=e.lightMap,this.lightMapIntensity=e.lightMapIntensity,this.aoMap=e.aoMap,this.aoMapIntensity=e.aoMapIntensity,this.specularMap=e.specularMap,this.alphaMap=e.alphaMap,this.envMap=e.envMap,this.envMapRotation.copy(e.envMapRotation),this.combine=e.combine,this.reflectivity=e.reflectivity,this.refractionRatio=e.refractionRatio,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.wireframeLinecap=e.wireframeLinecap,this.wireframeLinejoin=e.wireframeLinejoin,this.fog=e.fog,this}}const tn=new V,Co=new Xe;class Mi{constructor(e,t,n=!1){if(Array.isArray(e))throw new TypeError("THREE.BufferAttribute: array should be a Typed Array.");this.isBufferAttribute=!0,this.name="",this.array=e,this.itemSize=t,this.count=e!==void 0?e.length/t:0,this.normalized=n,this.usage=wh,this._updateRange={offset:0,count:-1},this.updateRanges=[],this.gpuType=Ji,this.version=0}onUploadCallback(){}set needsUpdate(e){e===!0&&this.version++}get updateRange(){return Yr("THREE.BufferAttribute: updateRange() is deprecated and will be removed in r169. Use addUpdateRange() instead."),this._updateRange}setUsage(e){return this.usage=e,this}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}copy(e){return this.name=e.name,this.array=new e.array.constructor(e.array),this.itemSize=e.itemSize,this.count=e.count,this.normalized=e.normalized,this.usage=e.usage,this.gpuType=e.gpuType,this}copyAt(e,t,n){e*=this.itemSize,n*=t.itemSize;for(let s=0,r=this.itemSize;s<r;s++)this.array[e+s]=t.array[n+s];return this}copyArray(e){return this.array.set(e),this}applyMatrix3(e){if(this.itemSize===2)for(let t=0,n=this.count;t<n;t++)Co.fromBufferAttribute(this,t),Co.applyMatrix3(e),this.setXY(t,Co.x,Co.y);else if(this.itemSize===3)for(let t=0,n=this.count;t<n;t++)tn.fromBufferAttribute(this,t),tn.applyMatrix3(e),this.setXYZ(t,tn.x,tn.y,tn.z);return this}applyMatrix4(e){for(let t=0,n=this.count;t<n;t++)tn.fromBufferAttribute(this,t),tn.applyMatrix4(e),this.setXYZ(t,tn.x,tn.y,tn.z);return this}applyNormalMatrix(e){for(let t=0,n=this.count;t<n;t++)tn.fromBufferAttribute(this,t),tn.applyNormalMatrix(e),this.setXYZ(t,tn.x,tn.y,tn.z);return this}transformDirection(e){for(let t=0,n=this.count;t<n;t++)tn.fromBufferAttribute(this,t),tn.transformDirection(e),this.setXYZ(t,tn.x,tn.y,tn.z);return this}set(e,t=0){return this.array.set(e,t),this}getComponent(e,t){let n=this.array[e*this.itemSize+t];return this.normalized&&(n=xi(n,this.array)),n}setComponent(e,t,n){return this.normalized&&(n=At(n,this.array)),this.array[e*this.itemSize+t]=n,this}getX(e){let t=this.array[e*this.itemSize];return this.normalized&&(t=xi(t,this.array)),t}setX(e,t){return this.normalized&&(t=At(t,this.array)),this.array[e*this.itemSize]=t,this}getY(e){let t=this.array[e*this.itemSize+1];return this.normalized&&(t=xi(t,this.array)),t}setY(e,t){return this.normalized&&(t=At(t,this.array)),this.array[e*this.itemSize+1]=t,this}getZ(e){let t=this.array[e*this.itemSize+2];return this.normalized&&(t=xi(t,this.array)),t}setZ(e,t){return this.normalized&&(t=At(t,this.array)),this.array[e*this.itemSize+2]=t,this}getW(e){let t=this.array[e*this.itemSize+3];return this.normalized&&(t=xi(t,this.array)),t}setW(e,t){return this.normalized&&(t=At(t,this.array)),this.array[e*this.itemSize+3]=t,this}setXY(e,t,n){return e*=this.itemSize,this.normalized&&(t=At(t,this.array),n=At(n,this.array)),this.array[e+0]=t,this.array[e+1]=n,this}setXYZ(e,t,n,s){return e*=this.itemSize,this.normalized&&(t=At(t,this.array),n=At(n,this.array),s=At(s,this.array)),this.array[e+0]=t,this.array[e+1]=n,this.array[e+2]=s,this}setXYZW(e,t,n,s,r){return e*=this.itemSize,this.normalized&&(t=At(t,this.array),n=At(n,this.array),s=At(s,this.array),r=At(r,this.array)),this.array[e+0]=t,this.array[e+1]=n,this.array[e+2]=s,this.array[e+3]=r,this}onUpload(e){return this.onUploadCallback=e,this}clone(){return new this.constructor(this.array,this.itemSize).copy(this)}toJSON(){const e={itemSize:this.itemSize,type:this.array.constructor.name,array:Array.from(this.array),normalized:this.normalized};return this.name!==""&&(e.name=this.name),this.usage!==wh&&(e.usage=this.usage),e}}class yp extends Mi{constructor(e,t,n){super(new Uint16Array(e),t,n)}}class Sp extends Mi{constructor(e,t,n){super(new Uint32Array(e),t,n)}}class Ut extends Mi{constructor(e,t,n){super(new Float32Array(e),t,n)}}let Rv=0;const ni=new zt,vc=new sn,Cr=new V,Xn=new ro,Da=new ro,gn=new V;class Qt extends pa{constructor(){super(),this.isBufferGeometry=!0,Object.defineProperty(this,"id",{value:Rv++}),this.uuid=Qi(),this.name="",this.type="BufferGeometry",this.index=null,this.attributes={},this.morphAttributes={},this.morphTargetsRelative=!1,this.groups=[],this.boundingBox=null,this.boundingSphere=null,this.drawRange={start:0,count:1/0},this.userData={}}getIndex(){return this.index}setIndex(e){return Array.isArray(e)?this.index=new(gp(e)?Sp:yp)(e,1):this.index=e,this}getAttribute(e){return this.attributes[e]}setAttribute(e,t){return this.attributes[e]=t,this}deleteAttribute(e){return delete this.attributes[e],this}hasAttribute(e){return this.attributes[e]!==void 0}addGroup(e,t,n=0){this.groups.push({start:e,count:t,materialIndex:n})}clearGroups(){this.groups=[]}setDrawRange(e,t){this.drawRange.start=e,this.drawRange.count=t}applyMatrix4(e){const t=this.attributes.position;t!==void 0&&(t.applyMatrix4(e),t.needsUpdate=!0);const n=this.attributes.normal;if(n!==void 0){const r=new ot().getNormalMatrix(e);n.applyNormalMatrix(r),n.needsUpdate=!0}const s=this.attributes.tangent;return s!==void 0&&(s.transformDirection(e),s.needsUpdate=!0),this.boundingBox!==null&&this.computeBoundingBox(),this.boundingSphere!==null&&this.computeBoundingSphere(),this}applyQuaternion(e){return ni.makeRotationFromQuaternion(e),this.applyMatrix4(ni),this}rotateX(e){return ni.makeRotationX(e),this.applyMatrix4(ni),this}rotateY(e){return ni.makeRotationY(e),this.applyMatrix4(ni),this}rotateZ(e){return ni.makeRotationZ(e),this.applyMatrix4(ni),this}translate(e,t,n){return ni.makeTranslation(e,t,n),this.applyMatrix4(ni),this}scale(e,t,n){return ni.makeScale(e,t,n),this.applyMatrix4(ni),this}lookAt(e){return vc.lookAt(e),vc.updateMatrix(),this.applyMatrix4(vc.matrix),this}center(){return this.computeBoundingBox(),this.boundingBox.getCenter(Cr).negate(),this.translate(Cr.x,Cr.y,Cr.z),this}setFromPoints(e){const t=[];for(let n=0,s=e.length;n<s;n++){const r=e[n];t.push(r.x,r.y,r.z||0)}return this.setAttribute("position",new Ut(t,3)),this}computeBoundingBox(){this.boundingBox===null&&(this.boundingBox=new ro);const e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingBox(): GLBufferAttribute requires a manual bounding box.",this),this.boundingBox.set(new V(-1/0,-1/0,-1/0),new V(1/0,1/0,1/0));return}if(e!==void 0){if(this.boundingBox.setFromBufferAttribute(e),t)for(let n=0,s=t.length;n<s;n++){const r=t[n];Xn.setFromBufferAttribute(r),this.morphTargetsRelative?(gn.addVectors(this.boundingBox.min,Xn.min),this.boundingBox.expandByPoint(gn),gn.addVectors(this.boundingBox.max,Xn.max),this.boundingBox.expandByPoint(gn)):(this.boundingBox.expandByPoint(Xn.min),this.boundingBox.expandByPoint(Xn.max))}}else this.boundingBox.makeEmpty();(isNaN(this.boundingBox.min.x)||isNaN(this.boundingBox.min.y)||isNaN(this.boundingBox.min.z))&&console.error('THREE.BufferGeometry.computeBoundingBox(): Computed min/max have NaN values. The "position" attribute is likely to have NaN values.',this)}computeBoundingSphere(){this.boundingSphere===null&&(this.boundingSphere=new ao);const e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingSphere(): GLBufferAttribute requires a manual bounding sphere.",this),this.boundingSphere.set(new V,1/0);return}if(e){const n=this.boundingSphere.center;if(Xn.setFromBufferAttribute(e),t)for(let r=0,a=t.length;r<a;r++){const o=t[r];Da.setFromBufferAttribute(o),this.morphTargetsRelative?(gn.addVectors(Xn.min,Da.min),Xn.expandByPoint(gn),gn.addVectors(Xn.max,Da.max),Xn.expandByPoint(gn)):(Xn.expandByPoint(Da.min),Xn.expandByPoint(Da.max))}Xn.getCenter(n);let s=0;for(let r=0,a=e.count;r<a;r++)gn.fromBufferAttribute(e,r),s=Math.max(s,n.distanceToSquared(gn));if(t)for(let r=0,a=t.length;r<a;r++){const o=t[r],l=this.morphTargetsRelative;for(let c=0,h=o.count;c<h;c++)gn.fromBufferAttribute(o,c),l&&(Cr.fromBufferAttribute(e,c),gn.add(Cr)),s=Math.max(s,n.distanceToSquared(gn))}this.boundingSphere.radius=Math.sqrt(s),isNaN(this.boundingSphere.radius)&&console.error('THREE.BufferGeometry.computeBoundingSphere(): Computed radius is NaN. The "position" attribute is likely to have NaN values.',this)}}computeTangents(){const e=this.index,t=this.attributes;if(e===null||t.position===void 0||t.normal===void 0||t.uv===void 0){console.error("THREE.BufferGeometry: .computeTangents() failed. Missing required attributes (index, position, normal or uv)");return}const n=t.position,s=t.normal,r=t.uv;this.hasAttribute("tangent")===!1&&this.setAttribute("tangent",new Mi(new Float32Array(4*n.count),4));const a=this.getAttribute("tangent"),o=[],l=[];for(let N=0;N<n.count;N++)o[N]=new V,l[N]=new V;const c=new V,h=new V,u=new V,d=new Xe,f=new Xe,g=new Xe,v=new V,p=new V;function m(N,w,y){c.fromBufferAttribute(n,N),h.fromBufferAttribute(n,w),u.fromBufferAttribute(n,y),d.fromBufferAttribute(r,N),f.fromBufferAttribute(r,w),g.fromBufferAttribute(r,y),h.sub(c),u.sub(c),f.sub(d),g.sub(d);const P=1/(f.x*g.y-g.x*f.y);isFinite(P)&&(v.copy(h).multiplyScalar(g.y).addScaledVector(u,-f.y).multiplyScalar(P),p.copy(u).multiplyScalar(f.x).addScaledVector(h,-g.x).multiplyScalar(P),o[N].add(v),o[w].add(v),o[y].add(v),l[N].add(p),l[w].add(p),l[y].add(p))}let S=this.groups;S.length===0&&(S=[{start:0,count:e.count}]);for(let N=0,w=S.length;N<w;++N){const y=S[N],P=y.start,X=y.count;for(let H=P,J=P+X;H<J;H+=3)m(e.getX(H+0),e.getX(H+1),e.getX(H+2))}const _=new V,b=new V,I=new V,A=new V;function R(N){I.fromBufferAttribute(s,N),A.copy(I);const w=o[N];_.copy(w),_.sub(I.multiplyScalar(I.dot(w))).normalize(),b.crossVectors(A,w);const P=b.dot(l[N])<0?-1:1;a.setXYZW(N,_.x,_.y,_.z,P)}for(let N=0,w=S.length;N<w;++N){const y=S[N],P=y.start,X=y.count;for(let H=P,J=P+X;H<J;H+=3)R(e.getX(H+0)),R(e.getX(H+1)),R(e.getX(H+2))}}computeVertexNormals(){const e=this.index,t=this.getAttribute("position");if(t!==void 0){let n=this.getAttribute("normal");if(n===void 0)n=new Mi(new Float32Array(t.count*3),3),this.setAttribute("normal",n);else for(let d=0,f=n.count;d<f;d++)n.setXYZ(d,0,0,0);const s=new V,r=new V,a=new V,o=new V,l=new V,c=new V,h=new V,u=new V;if(e)for(let d=0,f=e.count;d<f;d+=3){const g=e.getX(d+0),v=e.getX(d+1),p=e.getX(d+2);s.fromBufferAttribute(t,g),r.fromBufferAttribute(t,v),a.fromBufferAttribute(t,p),h.subVectors(a,r),u.subVectors(s,r),h.cross(u),o.fromBufferAttribute(n,g),l.fromBufferAttribute(n,v),c.fromBufferAttribute(n,p),o.add(h),l.add(h),c.add(h),n.setXYZ(g,o.x,o.y,o.z),n.setXYZ(v,l.x,l.y,l.z),n.setXYZ(p,c.x,c.y,c.z)}else for(let d=0,f=t.count;d<f;d+=3)s.fromBufferAttribute(t,d+0),r.fromBufferAttribute(t,d+1),a.fromBufferAttribute(t,d+2),h.subVectors(a,r),u.subVectors(s,r),h.cross(u),n.setXYZ(d+0,h.x,h.y,h.z),n.setXYZ(d+1,h.x,h.y,h.z),n.setXYZ(d+2,h.x,h.y,h.z);this.normalizeNormals(),n.needsUpdate=!0}}normalizeNormals(){const e=this.attributes.normal;for(let t=0,n=e.count;t<n;t++)gn.fromBufferAttribute(e,t),gn.normalize(),e.setXYZ(t,gn.x,gn.y,gn.z)}toNonIndexed(){function e(o,l){const c=o.array,h=o.itemSize,u=o.normalized,d=new c.constructor(l.length*h);let f=0,g=0;for(let v=0,p=l.length;v<p;v++){o.isInterleavedBufferAttribute?f=l[v]*o.data.stride+o.offset:f=l[v]*h;for(let m=0;m<h;m++)d[g++]=c[f++]}return new Mi(d,h,u)}if(this.index===null)return console.warn("THREE.BufferGeometry.toNonIndexed(): BufferGeometry is already non-indexed."),this;const t=new Qt,n=this.index.array,s=this.attributes;for(const o in s){const l=s[o],c=e(l,n);t.setAttribute(o,c)}const r=this.morphAttributes;for(const o in r){const l=[],c=r[o];for(let h=0,u=c.length;h<u;h++){const d=c[h],f=e(d,n);l.push(f)}t.morphAttributes[o]=l}t.morphTargetsRelative=this.morphTargetsRelative;const a=this.groups;for(let o=0,l=a.length;o<l;o++){const c=a[o];t.addGroup(c.start,c.count,c.materialIndex)}return t}toJSON(){const e={metadata:{version:4.6,type:"BufferGeometry",generator:"BufferGeometry.toJSON"}};if(e.uuid=this.uuid,e.type=this.type,this.name!==""&&(e.name=this.name),Object.keys(this.userData).length>0&&(e.userData=this.userData),this.parameters!==void 0){const l=this.parameters;for(const c in l)l[c]!==void 0&&(e[c]=l[c]);return e}e.data={attributes:{}};const t=this.index;t!==null&&(e.data.index={type:t.array.constructor.name,array:Array.prototype.slice.call(t.array)});const n=this.attributes;for(const l in n){const c=n[l];e.data.attributes[l]=c.toJSON(e.data)}const s={};let r=!1;for(const l in this.morphAttributes){const c=this.morphAttributes[l],h=[];for(let u=0,d=c.length;u<d;u++){const f=c[u];h.push(f.toJSON(e.data))}h.length>0&&(s[l]=h,r=!0)}r&&(e.data.morphAttributes=s,e.data.morphTargetsRelative=this.morphTargetsRelative);const a=this.groups;a.length>0&&(e.data.groups=JSON.parse(JSON.stringify(a)));const o=this.boundingSphere;return o!==null&&(e.data.boundingSphere={center:o.center.toArray(),radius:o.radius}),e}clone(){return new this.constructor().copy(this)}copy(e){this.index=null,this.attributes={},this.morphAttributes={},this.groups=[],this.boundingBox=null,this.boundingSphere=null;const t={};this.name=e.name;const n=e.index;n!==null&&this.setIndex(n.clone(t));const s=e.attributes;for(const c in s){const h=s[c];this.setAttribute(c,h.clone(t))}const r=e.morphAttributes;for(const c in r){const h=[],u=r[c];for(let d=0,f=u.length;d<f;d++)h.push(u[d].clone(t));this.morphAttributes[c]=h}this.morphTargetsRelative=e.morphTargetsRelative;const a=e.groups;for(let c=0,h=a.length;c<h;c++){const u=a[c];this.addGroup(u.start,u.count,u.materialIndex)}const o=e.boundingBox;o!==null&&(this.boundingBox=o.clone());const l=e.boundingSphere;return l!==null&&(this.boundingSphere=l.clone()),this.drawRange.start=e.drawRange.start,this.drawRange.count=e.drawRange.count,this.userData=e.userData,this}dispose(){this.dispatchEvent({type:"dispose"})}}const od=new zt,ks=new oo,Ro=new ao,ld=new V,Rr=new V,Pr=new V,Lr=new V,xc=new V,Po=new V,Lo=new Xe,Do=new Xe,Io=new Xe,cd=new V,hd=new V,ud=new V,Uo=new V,No=new V;class jt extends sn{constructor(e=new Qt,t=new es){super(),this.isMesh=!0,this.type="Mesh",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),e.morphTargetInfluences!==void 0&&(this.morphTargetInfluences=e.morphTargetInfluences.slice()),e.morphTargetDictionary!==void 0&&(this.morphTargetDictionary=Object.assign({},e.morphTargetDictionary)),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const s=t[n[0]];if(s!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let r=0,a=s.length;r<a;r++){const o=s[r].name||String(r);this.morphTargetInfluences.push(0),this.morphTargetDictionary[o]=r}}}}getVertexPosition(e,t){const n=this.geometry,s=n.attributes.position,r=n.morphAttributes.position,a=n.morphTargetsRelative;t.fromBufferAttribute(s,e);const o=this.morphTargetInfluences;if(r&&o){Po.set(0,0,0);for(let l=0,c=r.length;l<c;l++){const h=o[l],u=r[l];h!==0&&(xc.fromBufferAttribute(u,e),a?Po.addScaledVector(xc,h):Po.addScaledVector(xc.sub(t),h))}t.add(Po)}return t}raycast(e,t){const n=this.geometry,s=this.material,r=this.matrixWorld;s!==void 0&&(n.boundingSphere===null&&n.computeBoundingSphere(),Ro.copy(n.boundingSphere),Ro.applyMatrix4(r),ks.copy(e.ray).recast(e.near),!(Ro.containsPoint(ks.origin)===!1&&(ks.intersectSphere(Ro,ld)===null||ks.origin.distanceToSquared(ld)>(e.far-e.near)**2))&&(od.copy(r).invert(),ks.copy(e.ray).applyMatrix4(od),!(n.boundingBox!==null&&ks.intersectsBox(n.boundingBox)===!1)&&this._computeIntersections(e,t,ks)))}_computeIntersections(e,t,n){let s;const r=this.geometry,a=this.material,o=r.index,l=r.attributes.position,c=r.attributes.uv,h=r.attributes.uv1,u=r.attributes.normal,d=r.groups,f=r.drawRange;if(o!==null)if(Array.isArray(a))for(let g=0,v=d.length;g<v;g++){const p=d[g],m=a[p.materialIndex],S=Math.max(p.start,f.start),_=Math.min(o.count,Math.min(p.start+p.count,f.start+f.count));for(let b=S,I=_;b<I;b+=3){const A=o.getX(b),R=o.getX(b+1),N=o.getX(b+2);s=Oo(this,m,e,n,c,h,u,A,R,N),s&&(s.faceIndex=Math.floor(b/3),s.face.materialIndex=p.materialIndex,t.push(s))}}else{const g=Math.max(0,f.start),v=Math.min(o.count,f.start+f.count);for(let p=g,m=v;p<m;p+=3){const S=o.getX(p),_=o.getX(p+1),b=o.getX(p+2);s=Oo(this,a,e,n,c,h,u,S,_,b),s&&(s.faceIndex=Math.floor(p/3),t.push(s))}}else if(l!==void 0)if(Array.isArray(a))for(let g=0,v=d.length;g<v;g++){const p=d[g],m=a[p.materialIndex],S=Math.max(p.start,f.start),_=Math.min(l.count,Math.min(p.start+p.count,f.start+f.count));for(let b=S,I=_;b<I;b+=3){const A=b,R=b+1,N=b+2;s=Oo(this,m,e,n,c,h,u,A,R,N),s&&(s.faceIndex=Math.floor(b/3),s.face.materialIndex=p.materialIndex,t.push(s))}}else{const g=Math.max(0,f.start),v=Math.min(l.count,f.start+f.count);for(let p=g,m=v;p<m;p+=3){const S=p,_=p+1,b=p+2;s=Oo(this,a,e,n,c,h,u,S,_,b),s&&(s.faceIndex=Math.floor(p/3),t.push(s))}}}}function Pv(i,e,t,n,s,r,a,o){let l;if(e.side===Vn?l=n.intersectTriangle(a,r,s,!0,o):l=n.intersectTriangle(s,r,a,e.side===Ms,o),l===null)return null;No.copy(o),No.applyMatrix4(i.matrixWorld);const c=t.ray.origin.distanceTo(No);return c<t.near||c>t.far?null:{distance:c,point:No.clone(),object:i}}function Oo(i,e,t,n,s,r,a,o,l,c){i.getVertexPosition(o,Rr),i.getVertexPosition(l,Pr),i.getVertexPosition(c,Lr);const h=Pv(i,e,t,n,Rr,Pr,Lr,Uo);if(h){s&&(Lo.fromBufferAttribute(s,o),Do.fromBufferAttribute(s,l),Io.fromBufferAttribute(s,c),h.uv=ri.getInterpolation(Uo,Rr,Pr,Lr,Lo,Do,Io,new Xe)),r&&(Lo.fromBufferAttribute(r,o),Do.fromBufferAttribute(r,l),Io.fromBufferAttribute(r,c),h.uv1=ri.getInterpolation(Uo,Rr,Pr,Lr,Lo,Do,Io,new Xe)),a&&(cd.fromBufferAttribute(a,o),hd.fromBufferAttribute(a,l),ud.fromBufferAttribute(a,c),h.normal=ri.getInterpolation(Uo,Rr,Pr,Lr,cd,hd,ud,new V),h.normal.dot(n.direction)>0&&h.normal.multiplyScalar(-1));const u={a:o,b:l,c,normal:new V,materialIndex:0};ri.getNormal(Rr,Pr,Lr,u.normal),h.face=u}return h}class Si extends Qt{constructor(e=1,t=1,n=1,s=1,r=1,a=1){super(),this.type="BoxGeometry",this.parameters={width:e,height:t,depth:n,widthSegments:s,heightSegments:r,depthSegments:a};const o=this;s=Math.floor(s),r=Math.floor(r),a=Math.floor(a);const l=[],c=[],h=[],u=[];let d=0,f=0;g("z","y","x",-1,-1,n,t,e,a,r,0),g("z","y","x",1,-1,n,t,-e,a,r,1),g("x","z","y",1,1,e,n,t,s,a,2),g("x","z","y",1,-1,e,n,-t,s,a,3),g("x","y","z",1,-1,e,t,n,s,r,4),g("x","y","z",-1,-1,e,t,-n,s,r,5),this.setIndex(l),this.setAttribute("position",new Ut(c,3)),this.setAttribute("normal",new Ut(h,3)),this.setAttribute("uv",new Ut(u,2));function g(v,p,m,S,_,b,I,A,R,N,w){const y=b/R,P=I/N,X=b/2,H=I/2,J=A/2,q=R+1,ee=N+1;let j=0,ne=0;const ge=new V;for(let de=0;de<ee;de++){const ye=de*P-H;for(let Te=0;Te<q;Te++){const Se=Te*y-X;ge[v]=Se*S,ge[p]=ye*_,ge[m]=J,c.push(ge.x,ge.y,ge.z),ge[v]=0,ge[p]=0,ge[m]=A>0?1:-1,h.push(ge.x,ge.y,ge.z),u.push(Te/R),u.push(1-de/N),j+=1}}for(let de=0;de<N;de++)for(let ye=0;ye<R;ye++){const Te=d+ye+q*de,Se=d+ye+q*(de+1),ie=d+(ye+1)+q*(de+1),he=d+(ye+1)+q*de;l.push(Te,Se,he),l.push(Se,ie,he),ne+=6}o.addGroup(f,ne,w),f+=ne,d+=j}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Si(e.width,e.height,e.depth,e.widthSegments,e.heightSegments,e.depthSegments)}}function ia(i){const e={};for(const t in i){e[t]={};for(const n in i[t]){const s=i[t][n];s&&(s.isColor||s.isMatrix3||s.isMatrix4||s.isVector2||s.isVector3||s.isVector4||s.isTexture||s.isQuaternion)?s.isRenderTargetTexture?(console.warn("UniformsUtils: Textures of render targets cannot be cloned via cloneUniforms() or mergeUniforms()."),e[t][n]=null):e[t][n]=s.clone():Array.isArray(s)?e[t][n]=s.slice():e[t][n]=s}}return e}function On(i){const e={};for(let t=0;t<i.length;t++){const n=ia(i[t]);for(const s in n)e[s]=n[s]}return e}function Lv(i){const e=[];for(let t=0;t<i.length;t++)e.push(i[t].clone());return e}function bp(i){const e=i.getRenderTarget();return e===null?i.outputColorSpace:e.isXRRenderTarget===!0?e.texture.colorSpace:wt.workingColorSpace}const Dv={clone:ia,merge:On};var Iv=`void main() {
	gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
}`,Uv=`void main() {
	gl_FragColor = vec4( 1.0, 0.0, 0.0, 1.0 );
}`;class ws extends Rs{constructor(e){super(),this.isShaderMaterial=!0,this.type="ShaderMaterial",this.defines={},this.uniforms={},this.uniformsGroups=[],this.vertexShader=Iv,this.fragmentShader=Uv,this.linewidth=1,this.wireframe=!1,this.wireframeLinewidth=1,this.fog=!1,this.lights=!1,this.clipping=!1,this.forceSinglePass=!0,this.extensions={clipCullDistance:!1,multiDraw:!1},this.defaultAttributeValues={color:[1,1,1],uv:[0,0],uv1:[0,0]},this.index0AttributeName=void 0,this.uniformsNeedUpdate=!1,this.glslVersion=null,e!==void 0&&this.setValues(e)}copy(e){return super.copy(e),this.fragmentShader=e.fragmentShader,this.vertexShader=e.vertexShader,this.uniforms=ia(e.uniforms),this.uniformsGroups=Lv(e.uniformsGroups),this.defines=Object.assign({},e.defines),this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.fog=e.fog,this.lights=e.lights,this.clipping=e.clipping,this.extensions=Object.assign({},e.extensions),this.glslVersion=e.glslVersion,this}toJSON(e){const t=super.toJSON(e);t.glslVersion=this.glslVersion,t.uniforms={};for(const s in this.uniforms){const a=this.uniforms[s].value;a&&a.isTexture?t.uniforms[s]={type:"t",value:a.toJSON(e).uuid}:a&&a.isColor?t.uniforms[s]={type:"c",value:a.getHex()}:a&&a.isVector2?t.uniforms[s]={type:"v2",value:a.toArray()}:a&&a.isVector3?t.uniforms[s]={type:"v3",value:a.toArray()}:a&&a.isVector4?t.uniforms[s]={type:"v4",value:a.toArray()}:a&&a.isMatrix3?t.uniforms[s]={type:"m3",value:a.toArray()}:a&&a.isMatrix4?t.uniforms[s]={type:"m4",value:a.toArray()}:t.uniforms[s]={value:a}}Object.keys(this.defines).length>0&&(t.defines=this.defines),t.vertexShader=this.vertexShader,t.fragmentShader=this.fragmentShader,t.lights=this.lights,t.clipping=this.clipping;const n={};for(const s in this.extensions)this.extensions[s]===!0&&(n[s]=!0);return Object.keys(n).length>0&&(t.extensions=n),t}}class Mp extends sn{constructor(){super(),this.isCamera=!0,this.type="Camera",this.matrixWorldInverse=new zt,this.projectionMatrix=new zt,this.projectionMatrixInverse=new zt,this.coordinateSystem=Zi}copy(e,t){return super.copy(e,t),this.matrixWorldInverse.copy(e.matrixWorldInverse),this.projectionMatrix.copy(e.projectionMatrix),this.projectionMatrixInverse.copy(e.projectionMatrixInverse),this.coordinateSystem=e.coordinateSystem,this}getWorldDirection(e){return super.getWorldDirection(e).negate()}updateMatrixWorld(e){super.updateMatrixWorld(e),this.matrixWorldInverse.copy(this.matrixWorld).invert()}updateWorldMatrix(e,t){super.updateWorldMatrix(e,t),this.matrixWorldInverse.copy(this.matrixWorld).invert()}clone(){return new this.constructor().copy(this)}}const gs=new V,dd=new Xe,fd=new Xe;class Rn extends Mp{constructor(e=50,t=1,n=.1,s=2e3){super(),this.isPerspectiveCamera=!0,this.type="PerspectiveCamera",this.fov=e,this.zoom=1,this.near=n,this.far=s,this.focus=10,this.aspect=t,this.view=null,this.filmGauge=35,this.filmOffset=0,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.fov=e.fov,this.zoom=e.zoom,this.near=e.near,this.far=e.far,this.focus=e.focus,this.aspect=e.aspect,this.view=e.view===null?null:Object.assign({},e.view),this.filmGauge=e.filmGauge,this.filmOffset=e.filmOffset,this}setFocalLength(e){const t=.5*this.getFilmHeight()/e;this.fov=Qa*2*Math.atan(t),this.updateProjectionMatrix()}getFocalLength(){const e=Math.tan(Xr*.5*this.fov);return .5*this.getFilmHeight()/e}getEffectiveFOV(){return Qa*2*Math.atan(Math.tan(Xr*.5*this.fov)/this.zoom)}getFilmWidth(){return this.filmGauge*Math.min(this.aspect,1)}getFilmHeight(){return this.filmGauge/Math.max(this.aspect,1)}getViewBounds(e,t,n){gs.set(-1,-1,.5).applyMatrix4(this.projectionMatrixInverse),t.set(gs.x,gs.y).multiplyScalar(-e/gs.z),gs.set(1,1,.5).applyMatrix4(this.projectionMatrixInverse),n.set(gs.x,gs.y).multiplyScalar(-e/gs.z)}getViewSize(e,t){return this.getViewBounds(e,dd,fd),t.subVectors(fd,dd)}setViewOffset(e,t,n,s,r,a){this.aspect=e/t,this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=n,this.view.offsetY=s,this.view.width=r,this.view.height=a,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const e=this.near;let t=e*Math.tan(Xr*.5*this.fov)/this.zoom,n=2*t,s=this.aspect*n,r=-.5*s;const a=this.view;if(this.view!==null&&this.view.enabled){const l=a.fullWidth,c=a.fullHeight;r+=a.offsetX*s/l,t-=a.offsetY*n/c,s*=a.width/l,n*=a.height/c}const o=this.filmOffset;o!==0&&(r+=e*o/this.getFilmWidth()),this.projectionMatrix.makePerspective(r,r+s,t,t-n,e,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){const t=super.toJSON(e);return t.object.fov=this.fov,t.object.zoom=this.zoom,t.object.near=this.near,t.object.far=this.far,t.object.focus=this.focus,t.object.aspect=this.aspect,this.view!==null&&(t.object.view=Object.assign({},this.view)),t.object.filmGauge=this.filmGauge,t.object.filmOffset=this.filmOffset,t}}const Dr=-90,Ir=1;class Nv extends sn{constructor(e,t,n){super(),this.type="CubeCamera",this.renderTarget=n,this.coordinateSystem=null,this.activeMipmapLevel=0;const s=new Rn(Dr,Ir,e,t);s.layers=this.layers,this.add(s);const r=new Rn(Dr,Ir,e,t);r.layers=this.layers,this.add(r);const a=new Rn(Dr,Ir,e,t);a.layers=this.layers,this.add(a);const o=new Rn(Dr,Ir,e,t);o.layers=this.layers,this.add(o);const l=new Rn(Dr,Ir,e,t);l.layers=this.layers,this.add(l);const c=new Rn(Dr,Ir,e,t);c.layers=this.layers,this.add(c)}updateCoordinateSystem(){const e=this.coordinateSystem,t=this.children.concat(),[n,s,r,a,o,l]=t;for(const c of t)this.remove(c);if(e===Zi)n.up.set(0,1,0),n.lookAt(1,0,0),s.up.set(0,1,0),s.lookAt(-1,0,0),r.up.set(0,0,-1),r.lookAt(0,1,0),a.up.set(0,0,1),a.lookAt(0,-1,0),o.up.set(0,1,0),o.lookAt(0,0,1),l.up.set(0,1,0),l.lookAt(0,0,-1);else if(e===fl)n.up.set(0,-1,0),n.lookAt(-1,0,0),s.up.set(0,-1,0),s.lookAt(1,0,0),r.up.set(0,0,1),r.lookAt(0,1,0),a.up.set(0,0,-1),a.lookAt(0,-1,0),o.up.set(0,-1,0),o.lookAt(0,0,1),l.up.set(0,-1,0),l.lookAt(0,0,-1);else throw new Error("THREE.CubeCamera.updateCoordinateSystem(): Invalid coordinate system: "+e);for(const c of t)this.add(c),c.updateMatrixWorld()}update(e,t){this.parent===null&&this.updateMatrixWorld();const{renderTarget:n,activeMipmapLevel:s}=this;this.coordinateSystem!==e.coordinateSystem&&(this.coordinateSystem=e.coordinateSystem,this.updateCoordinateSystem());const[r,a,o,l,c,h]=this.children,u=e.getRenderTarget(),d=e.getActiveCubeFace(),f=e.getActiveMipmapLevel(),g=e.xr.enabled;e.xr.enabled=!1;const v=n.texture.generateMipmaps;n.texture.generateMipmaps=!1,e.setRenderTarget(n,0,s),e.render(t,r),e.setRenderTarget(n,1,s),e.render(t,a),e.setRenderTarget(n,2,s),e.render(t,o),e.setRenderTarget(n,3,s),e.render(t,l),e.setRenderTarget(n,4,s),e.render(t,c),n.texture.generateMipmaps=v,e.setRenderTarget(n,5,s),e.render(t,h),e.setRenderTarget(u,d,f),e.xr.enabled=g,n.texture.needsPMREMUpdate=!0}}class wp extends Bn{constructor(e,t,n,s,r,a,o,l,c,h){e=e!==void 0?e:[],t=t!==void 0?t:Qr,super(e,t,n,s,r,a,o,l,c,h),this.isCubeTexture=!0,this.flipY=!1}get images(){return this.image}set images(e){this.image=e}}class Ov extends Qs{constructor(e=1,t={}){super(e,e,t),this.isWebGLCubeRenderTarget=!0;const n={width:e,height:e,depth:1},s=[n,n,n,n,n,n];this.texture=new wp(s,t.mapping,t.wrapS,t.wrapT,t.magFilter,t.minFilter,t.format,t.type,t.anisotropy,t.colorSpace),this.texture.isRenderTargetTexture=!0,this.texture.generateMipmaps=t.generateMipmaps!==void 0?t.generateMipmaps:!1,this.texture.minFilter=t.minFilter!==void 0?t.minFilter:vi}fromEquirectangularTexture(e,t){this.texture.type=t.type,this.texture.colorSpace=t.colorSpace,this.texture.generateMipmaps=t.generateMipmaps,this.texture.minFilter=t.minFilter,this.texture.magFilter=t.magFilter;const n={uniforms:{tEquirect:{value:null}},vertexShader:`

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
			`},s=new Si(5,5,5),r=new ws({name:"CubemapFromEquirect",uniforms:ia(n.uniforms),vertexShader:n.vertexShader,fragmentShader:n.fragmentShader,side:Vn,blending:ys});r.uniforms.tEquirect.value=t;const a=new jt(s,r),o=t.minFilter;return t.minFilter===js&&(t.minFilter=vi),new Nv(1,10,this).update(e,a),t.minFilter=o,a.geometry.dispose(),a.material.dispose(),this}clear(e,t,n,s){const r=e.getRenderTarget();for(let a=0;a<6;a++)e.setRenderTarget(this,a),e.clear(t,n,s);e.setRenderTarget(r)}}const _c=new V,Fv=new V,kv=new ot;class vs{constructor(e=new V(1,0,0),t=0){this.isPlane=!0,this.normal=e,this.constant=t}set(e,t){return this.normal.copy(e),this.constant=t,this}setComponents(e,t,n,s){return this.normal.set(e,t,n),this.constant=s,this}setFromNormalAndCoplanarPoint(e,t){return this.normal.copy(e),this.constant=-t.dot(this.normal),this}setFromCoplanarPoints(e,t,n){const s=_c.subVectors(n,t).cross(Fv.subVectors(e,t)).normalize();return this.setFromNormalAndCoplanarPoint(s,e),this}copy(e){return this.normal.copy(e.normal),this.constant=e.constant,this}normalize(){const e=1/this.normal.length();return this.normal.multiplyScalar(e),this.constant*=e,this}negate(){return this.constant*=-1,this.normal.negate(),this}distanceToPoint(e){return this.normal.dot(e)+this.constant}distanceToSphere(e){return this.distanceToPoint(e.center)-e.radius}projectPoint(e,t){return t.copy(e).addScaledVector(this.normal,-this.distanceToPoint(e))}intersectLine(e,t){const n=e.delta(_c),s=this.normal.dot(n);if(s===0)return this.distanceToPoint(e.start)===0?t.copy(e.start):null;const r=-(e.start.dot(this.normal)+this.constant)/s;return r<0||r>1?null:t.copy(e.start).addScaledVector(n,r)}intersectsLine(e){const t=this.distanceToPoint(e.start),n=this.distanceToPoint(e.end);return t<0&&n>0||n<0&&t>0}intersectsBox(e){return e.intersectsPlane(this)}intersectsSphere(e){return e.intersectsPlane(this)}coplanarPoint(e){return e.copy(this.normal).multiplyScalar(-this.constant)}applyMatrix4(e,t){const n=t||kv.getNormalMatrix(e),s=this.coplanarPoint(_c).applyMatrix4(e),r=this.normal.applyMatrix3(n).normalize();return this.constant=-s.dot(r),this}translate(e){return this.constant-=e.dot(this.normal),this}equals(e){return e.normal.equals(this.normal)&&e.constant===this.constant}clone(){return new this.constructor().copy(this)}}const Bs=new ao,Fo=new V;class Zh{constructor(e=new vs,t=new vs,n=new vs,s=new vs,r=new vs,a=new vs){this.planes=[e,t,n,s,r,a]}set(e,t,n,s,r,a){const o=this.planes;return o[0].copy(e),o[1].copy(t),o[2].copy(n),o[3].copy(s),o[4].copy(r),o[5].copy(a),this}copy(e){const t=this.planes;for(let n=0;n<6;n++)t[n].copy(e.planes[n]);return this}setFromProjectionMatrix(e,t=Zi){const n=this.planes,s=e.elements,r=s[0],a=s[1],o=s[2],l=s[3],c=s[4],h=s[5],u=s[6],d=s[7],f=s[8],g=s[9],v=s[10],p=s[11],m=s[12],S=s[13],_=s[14],b=s[15];if(n[0].setComponents(l-r,d-c,p-f,b-m).normalize(),n[1].setComponents(l+r,d+c,p+f,b+m).normalize(),n[2].setComponents(l+a,d+h,p+g,b+S).normalize(),n[3].setComponents(l-a,d-h,p-g,b-S).normalize(),n[4].setComponents(l-o,d-u,p-v,b-_).normalize(),t===Zi)n[5].setComponents(l+o,d+u,p+v,b+_).normalize();else if(t===fl)n[5].setComponents(o,u,v,_).normalize();else throw new Error("THREE.Frustum.setFromProjectionMatrix(): Invalid coordinate system: "+t);return this}intersectsObject(e){if(e.boundingSphere!==void 0)e.boundingSphere===null&&e.computeBoundingSphere(),Bs.copy(e.boundingSphere).applyMatrix4(e.matrixWorld);else{const t=e.geometry;t.boundingSphere===null&&t.computeBoundingSphere(),Bs.copy(t.boundingSphere).applyMatrix4(e.matrixWorld)}return this.intersectsSphere(Bs)}intersectsSprite(e){return Bs.center.set(0,0,0),Bs.radius=.7071067811865476,Bs.applyMatrix4(e.matrixWorld),this.intersectsSphere(Bs)}intersectsSphere(e){const t=this.planes,n=e.center,s=-e.radius;for(let r=0;r<6;r++)if(t[r].distanceToPoint(n)<s)return!1;return!0}intersectsBox(e){const t=this.planes;for(let n=0;n<6;n++){const s=t[n];if(Fo.x=s.normal.x>0?e.max.x:e.min.x,Fo.y=s.normal.y>0?e.max.y:e.min.y,Fo.z=s.normal.z>0?e.max.z:e.min.z,s.distanceToPoint(Fo)<0)return!1}return!0}containsPoint(e){const t=this.planes;for(let n=0;n<6;n++)if(t[n].distanceToPoint(e)<0)return!1;return!0}clone(){return new this.constructor().copy(this)}}function Ep(){let i=null,e=!1,t=null,n=null;function s(r,a){t(r,a),n=i.requestAnimationFrame(s)}return{start:function(){e!==!0&&t!==null&&(n=i.requestAnimationFrame(s),e=!0)},stop:function(){i.cancelAnimationFrame(n),e=!1},setAnimationLoop:function(r){t=r},setContext:function(r){i=r}}}function Bv(i){const e=new WeakMap;function t(o,l){const c=o.array,h=o.usage,u=c.byteLength,d=i.createBuffer();i.bindBuffer(l,d),i.bufferData(l,c,h),o.onUploadCallback();let f;if(c instanceof Float32Array)f=i.FLOAT;else if(c instanceof Uint16Array)o.isFloat16BufferAttribute?f=i.HALF_FLOAT:f=i.UNSIGNED_SHORT;else if(c instanceof Int16Array)f=i.SHORT;else if(c instanceof Uint32Array)f=i.UNSIGNED_INT;else if(c instanceof Int32Array)f=i.INT;else if(c instanceof Int8Array)f=i.BYTE;else if(c instanceof Uint8Array)f=i.UNSIGNED_BYTE;else if(c instanceof Uint8ClampedArray)f=i.UNSIGNED_BYTE;else throw new Error("THREE.WebGLAttributes: Unsupported buffer data format: "+c);return{buffer:d,type:f,bytesPerElement:c.BYTES_PER_ELEMENT,version:o.version,size:u}}function n(o,l,c){const h=l.array,u=l._updateRange,d=l.updateRanges;if(i.bindBuffer(c,o),u.count===-1&&d.length===0&&i.bufferSubData(c,0,h),d.length!==0){for(let f=0,g=d.length;f<g;f++){const v=d[f];i.bufferSubData(c,v.start*h.BYTES_PER_ELEMENT,h,v.start,v.count)}l.clearUpdateRanges()}u.count!==-1&&(i.bufferSubData(c,u.offset*h.BYTES_PER_ELEMENT,h,u.offset,u.count),u.count=-1),l.onUploadCallback()}function s(o){return o.isInterleavedBufferAttribute&&(o=o.data),e.get(o)}function r(o){o.isInterleavedBufferAttribute&&(o=o.data);const l=e.get(o);l&&(i.deleteBuffer(l.buffer),e.delete(o))}function a(o,l){if(o.isInterleavedBufferAttribute&&(o=o.data),o.isGLBufferAttribute){const h=e.get(o);(!h||h.version<o.version)&&e.set(o,{buffer:o.buffer,type:o.type,bytesPerElement:o.elementSize,version:o.version});return}const c=e.get(o);if(c===void 0)e.set(o,t(o,l));else if(c.version<o.version){if(c.size!==o.array.byteLength)throw new Error("THREE.WebGLAttributes: The size of the buffer attribute's array buffer does not match the original size. Resizing buffer attributes is not supported.");n(c.buffer,o,l),c.version=o.version}}return{get:s,remove:r,update:a}}class lo extends Qt{constructor(e=1,t=1,n=1,s=1){super(),this.type="PlaneGeometry",this.parameters={width:e,height:t,widthSegments:n,heightSegments:s};const r=e/2,a=t/2,o=Math.floor(n),l=Math.floor(s),c=o+1,h=l+1,u=e/o,d=t/l,f=[],g=[],v=[],p=[];for(let m=0;m<h;m++){const S=m*d-a;for(let _=0;_<c;_++){const b=_*u-r;g.push(b,-S,0),v.push(0,0,1),p.push(_/o),p.push(1-m/l)}}for(let m=0;m<l;m++)for(let S=0;S<o;S++){const _=S+c*m,b=S+c*(m+1),I=S+1+c*(m+1),A=S+1+c*m;f.push(_,b,A),f.push(b,I,A)}this.setIndex(f),this.setAttribute("position",new Ut(g,3)),this.setAttribute("normal",new Ut(v,3)),this.setAttribute("uv",new Ut(p,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new lo(e.width,e.height,e.widthSegments,e.heightSegments)}}var zv=`#ifdef USE_ALPHAHASH
	if ( diffuseColor.a < getAlphaHashThreshold( vPosition ) ) discard;
#endif`,Hv=`#ifdef USE_ALPHAHASH
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
#endif`,Vv=`#ifdef USE_ALPHAMAP
	diffuseColor.a *= texture2D( alphaMap, vAlphaMapUv ).g;
#endif`,Gv=`#ifdef USE_ALPHAMAP
	uniform sampler2D alphaMap;
#endif`,Wv=`#ifdef USE_ALPHATEST
	#ifdef ALPHA_TO_COVERAGE
	diffuseColor.a = smoothstep( alphaTest, alphaTest + fwidth( diffuseColor.a ), diffuseColor.a );
	if ( diffuseColor.a == 0.0 ) discard;
	#else
	if ( diffuseColor.a < alphaTest ) discard;
	#endif
#endif`,$v=`#ifdef USE_ALPHATEST
	uniform float alphaTest;
#endif`,qv=`#ifdef USE_AOMAP
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
#endif`,Xv=`#ifdef USE_AOMAP
	uniform sampler2D aoMap;
	uniform float aoMapIntensity;
#endif`,Yv=`#ifdef USE_BATCHING
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
#endif`,jv=`#ifdef USE_BATCHING
	mat4 batchingMatrix = getBatchingMatrix( getIndirectIndex( gl_DrawID ) );
#endif`,Kv=`vec3 transformed = vec3( position );
#ifdef USE_ALPHAHASH
	vPosition = vec3( position );
#endif`,Jv=`vec3 objectNormal = vec3( normal );
#ifdef USE_TANGENT
	vec3 objectTangent = vec3( tangent.xyz );
#endif`,Zv=`float G_BlinnPhong_Implicit( ) {
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
} // validated`,Qv=`#ifdef USE_IRIDESCENCE
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
#endif`,ex=`#ifdef USE_BUMPMAP
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
#endif`,tx=`#if NUM_CLIPPING_PLANES > 0
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
#endif`,nx=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
	uniform vec4 clippingPlanes[ NUM_CLIPPING_PLANES ];
#endif`,ix=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
#endif`,sx=`#if NUM_CLIPPING_PLANES > 0
	vClipPosition = - mvPosition.xyz;
#endif`,rx=`#if defined( USE_COLOR_ALPHA )
	diffuseColor *= vColor;
#elif defined( USE_COLOR )
	diffuseColor.rgb *= vColor;
#endif`,ax=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR )
	varying vec3 vColor;
#endif`,ox=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR ) || defined( USE_INSTANCING_COLOR ) || defined( USE_BATCHING_COLOR )
	varying vec3 vColor;
#endif`,lx=`#if defined( USE_COLOR_ALPHA )
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
#endif`,cx=`#define PI 3.141592653589793
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
} // validated`,hx=`#ifdef ENVMAP_TYPE_CUBE_UV
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
#endif`,ux=`vec3 transformedNormal = objectNormal;
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
#endif`,dx=`#ifdef USE_DISPLACEMENTMAP
	uniform sampler2D displacementMap;
	uniform float displacementScale;
	uniform float displacementBias;
#endif`,fx=`#ifdef USE_DISPLACEMENTMAP
	transformed += normalize( objectNormal ) * ( texture2D( displacementMap, vDisplacementMapUv ).x * displacementScale + displacementBias );
#endif`,px=`#ifdef USE_EMISSIVEMAP
	vec4 emissiveColor = texture2D( emissiveMap, vEmissiveMapUv );
	totalEmissiveRadiance *= emissiveColor.rgb;
#endif`,mx=`#ifdef USE_EMISSIVEMAP
	uniform sampler2D emissiveMap;
#endif`,gx="gl_FragColor = linearToOutputTexel( gl_FragColor );",vx=`
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
}`,xx=`#ifdef USE_ENVMAP
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
#endif`,_x=`#ifdef USE_ENVMAP
	uniform float envMapIntensity;
	uniform float flipEnvMap;
	uniform mat3 envMapRotation;
	#ifdef ENVMAP_TYPE_CUBE
		uniform samplerCube envMap;
	#else
		uniform sampler2D envMap;
	#endif
	
#endif`,yx=`#ifdef USE_ENVMAP
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
#endif`,Sx=`#ifdef USE_ENVMAP
	#if defined( USE_BUMPMAP ) || defined( USE_NORMALMAP ) || defined( PHONG ) || defined( LAMBERT )
		#define ENV_WORLDPOS
	#endif
	#ifdef ENV_WORLDPOS
		
		varying vec3 vWorldPosition;
	#else
		varying vec3 vReflect;
		uniform float refractionRatio;
	#endif
#endif`,bx=`#ifdef USE_ENVMAP
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
#endif`,Mx=`#ifdef USE_FOG
	vFogDepth = - mvPosition.z;
#endif`,wx=`#ifdef USE_FOG
	varying float vFogDepth;
#endif`,Ex=`#ifdef USE_FOG
	#ifdef FOG_EXP2
		float fogFactor = 1.0 - exp( - fogDensity * fogDensity * vFogDepth * vFogDepth );
	#else
		float fogFactor = smoothstep( fogNear, fogFar, vFogDepth );
	#endif
	gl_FragColor.rgb = mix( gl_FragColor.rgb, fogColor, fogFactor );
#endif`,Tx=`#ifdef USE_FOG
	uniform vec3 fogColor;
	varying float vFogDepth;
	#ifdef FOG_EXP2
		uniform float fogDensity;
	#else
		uniform float fogNear;
		uniform float fogFar;
	#endif
#endif`,Ax=`#ifdef USE_GRADIENTMAP
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
}`,Cx=`#ifdef USE_LIGHTMAP
	uniform sampler2D lightMap;
	uniform float lightMapIntensity;
#endif`,Rx=`LambertMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularStrength = specularStrength;`,Px=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Lambert`,Lx=`uniform bool receiveShadow;
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
#endif`,Dx=`#ifdef USE_ENVMAP
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
#endif`,Ix=`ToonMaterial material;
material.diffuseColor = diffuseColor.rgb;`,Ux=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Toon`,Nx=`BlinnPhongMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularColor = specular;
material.specularShininess = shininess;
material.specularStrength = specularStrength;`,Ox=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_BlinnPhong`,Fx=`PhysicalMaterial material;
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
#endif`,kx=`struct PhysicalMaterial {
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
}`,Bx=`
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
#endif`,zx=`#if defined( RE_IndirectDiffuse )
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
#endif`,Hx=`#if defined( RE_IndirectDiffuse )
	RE_IndirectDiffuse( irradiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif
#if defined( RE_IndirectSpecular )
	RE_IndirectSpecular( radiance, iblIrradiance, clearcoatRadiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif`,Vx=`#if defined( USE_LOGDEPTHBUF )
	gl_FragDepth = vIsPerspective == 0.0 ? gl_FragCoord.z : log2( vFragDepth ) * logDepthBufFC * 0.5;
#endif`,Gx=`#if defined( USE_LOGDEPTHBUF )
	uniform float logDepthBufFC;
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,Wx=`#ifdef USE_LOGDEPTHBUF
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,$x=`#ifdef USE_LOGDEPTHBUF
	vFragDepth = 1.0 + gl_Position.w;
	vIsPerspective = float( isPerspectiveMatrix( projectionMatrix ) );
#endif`,qx=`#ifdef USE_MAP
	vec4 sampledDiffuseColor = texture2D( map, vMapUv );
	#ifdef DECODE_VIDEO_TEXTURE
		sampledDiffuseColor = vec4( mix( pow( sampledDiffuseColor.rgb * 0.9478672986 + vec3( 0.0521327014 ), vec3( 2.4 ) ), sampledDiffuseColor.rgb * 0.0773993808, vec3( lessThanEqual( sampledDiffuseColor.rgb, vec3( 0.04045 ) ) ) ), sampledDiffuseColor.w );
	
	#endif
	diffuseColor *= sampledDiffuseColor;
#endif`,Xx=`#ifdef USE_MAP
	uniform sampler2D map;
#endif`,Yx=`#if defined( USE_MAP ) || defined( USE_ALPHAMAP )
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
#endif`,jx=`#if defined( USE_POINTS_UV )
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
#endif`,Kx=`float metalnessFactor = metalness;
#ifdef USE_METALNESSMAP
	vec4 texelMetalness = texture2D( metalnessMap, vMetalnessMapUv );
	metalnessFactor *= texelMetalness.b;
#endif`,Jx=`#ifdef USE_METALNESSMAP
	uniform sampler2D metalnessMap;
#endif`,Zx=`#ifdef USE_INSTANCING_MORPH
	float morphTargetInfluences[ MORPHTARGETS_COUNT ];
	float morphTargetBaseInfluence = texelFetch( morphTexture, ivec2( 0, gl_InstanceID ), 0 ).r;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		morphTargetInfluences[i] =  texelFetch( morphTexture, ivec2( i + 1, gl_InstanceID ), 0 ).r;
	}
#endif`,Qx=`#if defined( USE_MORPHCOLORS )
	vColor *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		#if defined( USE_COLOR_ALPHA )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ) * morphTargetInfluences[ i ];
		#elif defined( USE_COLOR )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ).rgb * morphTargetInfluences[ i ];
		#endif
	}
#endif`,e0=`#ifdef USE_MORPHNORMALS
	objectNormal *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) objectNormal += getMorph( gl_VertexID, i, 1 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,t0=`#ifdef USE_MORPHTARGETS
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
#endif`,n0=`#ifdef USE_MORPHTARGETS
	transformed *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) transformed += getMorph( gl_VertexID, i, 0 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,i0=`float faceDirection = gl_FrontFacing ? 1.0 : - 1.0;
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
vec3 nonPerturbedNormal = normal;`,s0=`#ifdef USE_NORMALMAP_OBJECTSPACE
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
#endif`,r0=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,a0=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,o0=`#ifndef FLAT_SHADED
	vNormal = normalize( transformedNormal );
	#ifdef USE_TANGENT
		vTangent = normalize( transformedTangent );
		vBitangent = normalize( cross( vNormal, vTangent ) * tangent.w );
	#endif
#endif`,l0=`#ifdef USE_NORMALMAP
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
#endif`,c0=`#ifdef USE_CLEARCOAT
	vec3 clearcoatNormal = nonPerturbedNormal;
#endif`,h0=`#ifdef USE_CLEARCOAT_NORMALMAP
	vec3 clearcoatMapN = texture2D( clearcoatNormalMap, vClearcoatNormalMapUv ).xyz * 2.0 - 1.0;
	clearcoatMapN.xy *= clearcoatNormalScale;
	clearcoatNormal = normalize( tbn2 * clearcoatMapN );
#endif`,u0=`#ifdef USE_CLEARCOATMAP
	uniform sampler2D clearcoatMap;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	uniform sampler2D clearcoatNormalMap;
	uniform vec2 clearcoatNormalScale;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	uniform sampler2D clearcoatRoughnessMap;
#endif`,d0=`#ifdef USE_IRIDESCENCEMAP
	uniform sampler2D iridescenceMap;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	uniform sampler2D iridescenceThicknessMap;
#endif`,f0=`#ifdef OPAQUE
diffuseColor.a = 1.0;
#endif
#ifdef USE_TRANSMISSION
diffuseColor.a *= material.transmissionAlpha;
#endif
gl_FragColor = vec4( outgoingLight, diffuseColor.a );`,p0=`vec3 packNormalToRGB( const in vec3 normal ) {
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
}`,m0=`#ifdef PREMULTIPLIED_ALPHA
	gl_FragColor.rgb *= gl_FragColor.a;
#endif`,g0=`vec4 mvPosition = vec4( transformed, 1.0 );
#ifdef USE_BATCHING
	mvPosition = batchingMatrix * mvPosition;
#endif
#ifdef USE_INSTANCING
	mvPosition = instanceMatrix * mvPosition;
#endif
mvPosition = modelViewMatrix * mvPosition;
gl_Position = projectionMatrix * mvPosition;`,v0=`#ifdef DITHERING
	gl_FragColor.rgb = dithering( gl_FragColor.rgb );
#endif`,x0=`#ifdef DITHERING
	vec3 dithering( vec3 color ) {
		float grid_position = rand( gl_FragCoord.xy );
		vec3 dither_shift_RGB = vec3( 0.25 / 255.0, -0.25 / 255.0, 0.25 / 255.0 );
		dither_shift_RGB = mix( 2.0 * dither_shift_RGB, -2.0 * dither_shift_RGB, grid_position );
		return color + dither_shift_RGB;
	}
#endif`,_0=`float roughnessFactor = roughness;
#ifdef USE_ROUGHNESSMAP
	vec4 texelRoughness = texture2D( roughnessMap, vRoughnessMapUv );
	roughnessFactor *= texelRoughness.g;
#endif`,y0=`#ifdef USE_ROUGHNESSMAP
	uniform sampler2D roughnessMap;
#endif`,S0=`#if NUM_SPOT_LIGHT_COORDS > 0
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
#endif`,b0=`#if NUM_SPOT_LIGHT_COORDS > 0
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
#endif`,M0=`#if ( defined( USE_SHADOWMAP ) && ( NUM_DIR_LIGHT_SHADOWS > 0 || NUM_POINT_LIGHT_SHADOWS > 0 ) ) || ( NUM_SPOT_LIGHT_COORDS > 0 )
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
#endif`,w0=`float getShadowMask() {
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
}`,E0=`#ifdef USE_SKINNING
	mat4 boneMatX = getBoneMatrix( skinIndex.x );
	mat4 boneMatY = getBoneMatrix( skinIndex.y );
	mat4 boneMatZ = getBoneMatrix( skinIndex.z );
	mat4 boneMatW = getBoneMatrix( skinIndex.w );
#endif`,T0=`#ifdef USE_SKINNING
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
#endif`,A0=`#ifdef USE_SKINNING
	vec4 skinVertex = bindMatrix * vec4( transformed, 1.0 );
	vec4 skinned = vec4( 0.0 );
	skinned += boneMatX * skinVertex * skinWeight.x;
	skinned += boneMatY * skinVertex * skinWeight.y;
	skinned += boneMatZ * skinVertex * skinWeight.z;
	skinned += boneMatW * skinVertex * skinWeight.w;
	transformed = ( bindMatrixInverse * skinned ).xyz;
#endif`,C0=`#ifdef USE_SKINNING
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
#endif`,R0=`float specularStrength;
#ifdef USE_SPECULARMAP
	vec4 texelSpecular = texture2D( specularMap, vSpecularMapUv );
	specularStrength = texelSpecular.r;
#else
	specularStrength = 1.0;
#endif`,P0=`#ifdef USE_SPECULARMAP
	uniform sampler2D specularMap;
#endif`,L0=`#if defined( TONE_MAPPING )
	gl_FragColor.rgb = toneMapping( gl_FragColor.rgb );
#endif`,D0=`#ifndef saturate
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
vec3 CustomToneMapping( vec3 color ) { return color; }`,I0=`#ifdef USE_TRANSMISSION
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
#endif`,U0=`#ifdef USE_TRANSMISSION
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
#endif`,N0=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
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
#endif`,O0=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
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
#endif`,F0=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
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
#endif`,k0=`#if defined( USE_ENVMAP ) || defined( DISTANCE ) || defined ( USE_SHADOWMAP ) || defined ( USE_TRANSMISSION ) || NUM_SPOT_LIGHT_COORDS > 0
	vec4 worldPosition = vec4( transformed, 1.0 );
	#ifdef USE_BATCHING
		worldPosition = batchingMatrix * worldPosition;
	#endif
	#ifdef USE_INSTANCING
		worldPosition = instanceMatrix * worldPosition;
	#endif
	worldPosition = modelMatrix * worldPosition;
#endif`;const B0=`varying vec2 vUv;
uniform mat3 uvTransform;
void main() {
	vUv = ( uvTransform * vec3( uv, 1 ) ).xy;
	gl_Position = vec4( position.xy, 1.0, 1.0 );
}`,z0=`uniform sampler2D t2D;
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
}`,H0=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,V0=`#ifdef ENVMAP_TYPE_CUBE
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
}`,G0=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,W0=`uniform samplerCube tCube;
uniform float tFlip;
uniform float opacity;
varying vec3 vWorldDirection;
void main() {
	vec4 texColor = textureCube( tCube, vec3( tFlip * vWorldDirection.x, vWorldDirection.yz ) );
	gl_FragColor = texColor;
	gl_FragColor.a *= opacity;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,$0=`#include <common>
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
}`,q0=`#if DEPTH_PACKING == 3200
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
}`,X0=`#define DISTANCE
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
}`,Y0=`#define DISTANCE
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
}`,j0=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
}`,K0=`uniform sampler2D tEquirect;
varying vec3 vWorldDirection;
#include <common>
void main() {
	vec3 direction = normalize( vWorldDirection );
	vec2 sampleUV = equirectUv( direction );
	gl_FragColor = texture2D( tEquirect, sampleUV );
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,J0=`uniform float scale;
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
}`,Z0=`uniform vec3 diffuse;
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
}`,Q0=`#include <common>
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
}`,e_=`uniform vec3 diffuse;
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
}`,t_=`#define LAMBERT
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
}`,n_=`#define LAMBERT
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
}`,i_=`#define MATCAP
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
}`,s_=`#define MATCAP
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
}`,r_=`#define NORMAL
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
}`,a_=`#define NORMAL
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
}`,o_=`#define PHONG
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
}`,l_=`#define PHONG
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
}`,c_=`#define STANDARD
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
}`,h_=`#define STANDARD
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
}`,u_=`#define TOON
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
}`,d_=`#define TOON
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
}`,f_=`uniform float size;
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
}`,p_=`uniform vec3 diffuse;
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
}`,m_=`#include <common>
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
}`,g_=`uniform vec3 color;
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
}`,v_=`uniform float rotation;
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
}`,x_=`uniform vec3 diffuse;
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
}`,at={alphahash_fragment:zv,alphahash_pars_fragment:Hv,alphamap_fragment:Vv,alphamap_pars_fragment:Gv,alphatest_fragment:Wv,alphatest_pars_fragment:$v,aomap_fragment:qv,aomap_pars_fragment:Xv,batching_pars_vertex:Yv,batching_vertex:jv,begin_vertex:Kv,beginnormal_vertex:Jv,bsdfs:Zv,iridescence_fragment:Qv,bumpmap_pars_fragment:ex,clipping_planes_fragment:tx,clipping_planes_pars_fragment:nx,clipping_planes_pars_vertex:ix,clipping_planes_vertex:sx,color_fragment:rx,color_pars_fragment:ax,color_pars_vertex:ox,color_vertex:lx,common:cx,cube_uv_reflection_fragment:hx,defaultnormal_vertex:ux,displacementmap_pars_vertex:dx,displacementmap_vertex:fx,emissivemap_fragment:px,emissivemap_pars_fragment:mx,colorspace_fragment:gx,colorspace_pars_fragment:vx,envmap_fragment:xx,envmap_common_pars_fragment:_x,envmap_pars_fragment:yx,envmap_pars_vertex:Sx,envmap_physical_pars_fragment:Dx,envmap_vertex:bx,fog_vertex:Mx,fog_pars_vertex:wx,fog_fragment:Ex,fog_pars_fragment:Tx,gradientmap_pars_fragment:Ax,lightmap_pars_fragment:Cx,lights_lambert_fragment:Rx,lights_lambert_pars_fragment:Px,lights_pars_begin:Lx,lights_toon_fragment:Ix,lights_toon_pars_fragment:Ux,lights_phong_fragment:Nx,lights_phong_pars_fragment:Ox,lights_physical_fragment:Fx,lights_physical_pars_fragment:kx,lights_fragment_begin:Bx,lights_fragment_maps:zx,lights_fragment_end:Hx,logdepthbuf_fragment:Vx,logdepthbuf_pars_fragment:Gx,logdepthbuf_pars_vertex:Wx,logdepthbuf_vertex:$x,map_fragment:qx,map_pars_fragment:Xx,map_particle_fragment:Yx,map_particle_pars_fragment:jx,metalnessmap_fragment:Kx,metalnessmap_pars_fragment:Jx,morphinstance_vertex:Zx,morphcolor_vertex:Qx,morphnormal_vertex:e0,morphtarget_pars_vertex:t0,morphtarget_vertex:n0,normal_fragment_begin:i0,normal_fragment_maps:s0,normal_pars_fragment:r0,normal_pars_vertex:a0,normal_vertex:o0,normalmap_pars_fragment:l0,clearcoat_normal_fragment_begin:c0,clearcoat_normal_fragment_maps:h0,clearcoat_pars_fragment:u0,iridescence_pars_fragment:d0,opaque_fragment:f0,packing:p0,premultiplied_alpha_fragment:m0,project_vertex:g0,dithering_fragment:v0,dithering_pars_fragment:x0,roughnessmap_fragment:_0,roughnessmap_pars_fragment:y0,shadowmap_pars_fragment:S0,shadowmap_pars_vertex:b0,shadowmap_vertex:M0,shadowmask_pars_fragment:w0,skinbase_vertex:E0,skinning_pars_vertex:T0,skinning_vertex:A0,skinnormal_vertex:C0,specularmap_fragment:R0,specularmap_pars_fragment:P0,tonemapping_fragment:L0,tonemapping_pars_fragment:D0,transmission_fragment:I0,transmission_pars_fragment:U0,uv_pars_fragment:N0,uv_pars_vertex:O0,uv_vertex:F0,worldpos_vertex:k0,background_vert:B0,background_frag:z0,backgroundCube_vert:H0,backgroundCube_frag:V0,cube_vert:G0,cube_frag:W0,depth_vert:$0,depth_frag:q0,distanceRGBA_vert:X0,distanceRGBA_frag:Y0,equirect_vert:j0,equirect_frag:K0,linedashed_vert:J0,linedashed_frag:Z0,meshbasic_vert:Q0,meshbasic_frag:e_,meshlambert_vert:t_,meshlambert_frag:n_,meshmatcap_vert:i_,meshmatcap_frag:s_,meshnormal_vert:r_,meshnormal_frag:a_,meshphong_vert:o_,meshphong_frag:l_,meshphysical_vert:c_,meshphysical_frag:h_,meshtoon_vert:u_,meshtoon_frag:d_,points_vert:f_,points_frag:p_,shadow_vert:m_,shadow_frag:g_,sprite_vert:v_,sprite_frag:x_},Re={common:{diffuse:{value:new it(16777215)},opacity:{value:1},map:{value:null},mapTransform:{value:new ot},alphaMap:{value:null},alphaMapTransform:{value:new ot},alphaTest:{value:0}},specularmap:{specularMap:{value:null},specularMapTransform:{value:new ot}},envmap:{envMap:{value:null},envMapRotation:{value:new ot},flipEnvMap:{value:-1},reflectivity:{value:1},ior:{value:1.5},refractionRatio:{value:.98}},aomap:{aoMap:{value:null},aoMapIntensity:{value:1},aoMapTransform:{value:new ot}},lightmap:{lightMap:{value:null},lightMapIntensity:{value:1},lightMapTransform:{value:new ot}},bumpmap:{bumpMap:{value:null},bumpMapTransform:{value:new ot},bumpScale:{value:1}},normalmap:{normalMap:{value:null},normalMapTransform:{value:new ot},normalScale:{value:new Xe(1,1)}},displacementmap:{displacementMap:{value:null},displacementMapTransform:{value:new ot},displacementScale:{value:1},displacementBias:{value:0}},emissivemap:{emissiveMap:{value:null},emissiveMapTransform:{value:new ot}},metalnessmap:{metalnessMap:{value:null},metalnessMapTransform:{value:new ot}},roughnessmap:{roughnessMap:{value:null},roughnessMapTransform:{value:new ot}},gradientmap:{gradientMap:{value:null}},fog:{fogDensity:{value:25e-5},fogNear:{value:1},fogFar:{value:2e3},fogColor:{value:new it(16777215)}},lights:{ambientLightColor:{value:[]},lightProbe:{value:[]},directionalLights:{value:[],properties:{direction:{},color:{}}},directionalLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},directionalShadowMap:{value:[]},directionalShadowMatrix:{value:[]},spotLights:{value:[],properties:{color:{},position:{},direction:{},distance:{},coneCos:{},penumbraCos:{},decay:{}}},spotLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},spotLightMap:{value:[]},spotShadowMap:{value:[]},spotLightMatrix:{value:[]},pointLights:{value:[],properties:{color:{},position:{},decay:{},distance:{}}},pointLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{},shadowCameraNear:{},shadowCameraFar:{}}},pointShadowMap:{value:[]},pointShadowMatrix:{value:[]},hemisphereLights:{value:[],properties:{direction:{},skyColor:{},groundColor:{}}},rectAreaLights:{value:[],properties:{color:{},position:{},width:{},height:{}}},ltc_1:{value:null},ltc_2:{value:null}},points:{diffuse:{value:new it(16777215)},opacity:{value:1},size:{value:1},scale:{value:1},map:{value:null},alphaMap:{value:null},alphaMapTransform:{value:new ot},alphaTest:{value:0},uvTransform:{value:new ot}},sprite:{diffuse:{value:new it(16777215)},opacity:{value:1},center:{value:new Xe(.5,.5)},rotation:{value:0},map:{value:null},mapTransform:{value:new ot},alphaMap:{value:null},alphaMapTransform:{value:new ot},alphaTest:{value:0}}},Ni={basic:{uniforms:On([Re.common,Re.specularmap,Re.envmap,Re.aomap,Re.lightmap,Re.fog]),vertexShader:at.meshbasic_vert,fragmentShader:at.meshbasic_frag},lambert:{uniforms:On([Re.common,Re.specularmap,Re.envmap,Re.aomap,Re.lightmap,Re.emissivemap,Re.bumpmap,Re.normalmap,Re.displacementmap,Re.fog,Re.lights,{emissive:{value:new it(0)}}]),vertexShader:at.meshlambert_vert,fragmentShader:at.meshlambert_frag},phong:{uniforms:On([Re.common,Re.specularmap,Re.envmap,Re.aomap,Re.lightmap,Re.emissivemap,Re.bumpmap,Re.normalmap,Re.displacementmap,Re.fog,Re.lights,{emissive:{value:new it(0)},specular:{value:new it(1118481)},shininess:{value:30}}]),vertexShader:at.meshphong_vert,fragmentShader:at.meshphong_frag},standard:{uniforms:On([Re.common,Re.envmap,Re.aomap,Re.lightmap,Re.emissivemap,Re.bumpmap,Re.normalmap,Re.displacementmap,Re.roughnessmap,Re.metalnessmap,Re.fog,Re.lights,{emissive:{value:new it(0)},roughness:{value:1},metalness:{value:0},envMapIntensity:{value:1}}]),vertexShader:at.meshphysical_vert,fragmentShader:at.meshphysical_frag},toon:{uniforms:On([Re.common,Re.aomap,Re.lightmap,Re.emissivemap,Re.bumpmap,Re.normalmap,Re.displacementmap,Re.gradientmap,Re.fog,Re.lights,{emissive:{value:new it(0)}}]),vertexShader:at.meshtoon_vert,fragmentShader:at.meshtoon_frag},matcap:{uniforms:On([Re.common,Re.bumpmap,Re.normalmap,Re.displacementmap,Re.fog,{matcap:{value:null}}]),vertexShader:at.meshmatcap_vert,fragmentShader:at.meshmatcap_frag},points:{uniforms:On([Re.points,Re.fog]),vertexShader:at.points_vert,fragmentShader:at.points_frag},dashed:{uniforms:On([Re.common,Re.fog,{scale:{value:1},dashSize:{value:1},totalSize:{value:2}}]),vertexShader:at.linedashed_vert,fragmentShader:at.linedashed_frag},depth:{uniforms:On([Re.common,Re.displacementmap]),vertexShader:at.depth_vert,fragmentShader:at.depth_frag},normal:{uniforms:On([Re.common,Re.bumpmap,Re.normalmap,Re.displacementmap,{opacity:{value:1}}]),vertexShader:at.meshnormal_vert,fragmentShader:at.meshnormal_frag},sprite:{uniforms:On([Re.sprite,Re.fog]),vertexShader:at.sprite_vert,fragmentShader:at.sprite_frag},background:{uniforms:{uvTransform:{value:new ot},t2D:{value:null},backgroundIntensity:{value:1}},vertexShader:at.background_vert,fragmentShader:at.background_frag},backgroundCube:{uniforms:{envMap:{value:null},flipEnvMap:{value:-1},backgroundBlurriness:{value:0},backgroundIntensity:{value:1},backgroundRotation:{value:new ot}},vertexShader:at.backgroundCube_vert,fragmentShader:at.backgroundCube_frag},cube:{uniforms:{tCube:{value:null},tFlip:{value:-1},opacity:{value:1}},vertexShader:at.cube_vert,fragmentShader:at.cube_frag},equirect:{uniforms:{tEquirect:{value:null}},vertexShader:at.equirect_vert,fragmentShader:at.equirect_frag},distanceRGBA:{uniforms:On([Re.common,Re.displacementmap,{referencePosition:{value:new V},nearDistance:{value:1},farDistance:{value:1e3}}]),vertexShader:at.distanceRGBA_vert,fragmentShader:at.distanceRGBA_frag},shadow:{uniforms:On([Re.lights,Re.fog,{color:{value:new it(0)},opacity:{value:1}}]),vertexShader:at.shadow_vert,fragmentShader:at.shadow_frag}};Ni.physical={uniforms:On([Ni.standard.uniforms,{clearcoat:{value:0},clearcoatMap:{value:null},clearcoatMapTransform:{value:new ot},clearcoatNormalMap:{value:null},clearcoatNormalMapTransform:{value:new ot},clearcoatNormalScale:{value:new Xe(1,1)},clearcoatRoughness:{value:0},clearcoatRoughnessMap:{value:null},clearcoatRoughnessMapTransform:{value:new ot},dispersion:{value:0},iridescence:{value:0},iridescenceMap:{value:null},iridescenceMapTransform:{value:new ot},iridescenceIOR:{value:1.3},iridescenceThicknessMinimum:{value:100},iridescenceThicknessMaximum:{value:400},iridescenceThicknessMap:{value:null},iridescenceThicknessMapTransform:{value:new ot},sheen:{value:0},sheenColor:{value:new it(0)},sheenColorMap:{value:null},sheenColorMapTransform:{value:new ot},sheenRoughness:{value:1},sheenRoughnessMap:{value:null},sheenRoughnessMapTransform:{value:new ot},transmission:{value:0},transmissionMap:{value:null},transmissionMapTransform:{value:new ot},transmissionSamplerSize:{value:new Xe},transmissionSamplerMap:{value:null},thickness:{value:0},thicknessMap:{value:null},thicknessMapTransform:{value:new ot},attenuationDistance:{value:0},attenuationColor:{value:new it(0)},specularColor:{value:new it(1,1,1)},specularColorMap:{value:null},specularColorMapTransform:{value:new ot},specularIntensity:{value:1},specularIntensityMap:{value:null},specularIntensityMapTransform:{value:new ot},anisotropyVector:{value:new Xe},anisotropyMap:{value:null},anisotropyMapTransform:{value:new ot}}]),vertexShader:at.meshphysical_vert,fragmentShader:at.meshphysical_frag};const ko={r:0,b:0,g:0},zs=new Oi,__=new zt;function y_(i,e,t,n,s,r,a){const o=new it(0);let l=r===!0?0:1,c,h,u=null,d=0,f=null;function g(S){let _=S.isScene===!0?S.background:null;return _&&_.isTexture&&(_=(S.backgroundBlurriness>0?t:e).get(_)),_}function v(S){let _=!1;const b=g(S);b===null?m(o,l):b&&b.isColor&&(m(b,1),_=!0);const I=i.xr.getEnvironmentBlendMode();I==="additive"?n.buffers.color.setClear(0,0,0,1,a):I==="alpha-blend"&&n.buffers.color.setClear(0,0,0,0,a),(i.autoClear||_)&&(n.buffers.depth.setTest(!0),n.buffers.depth.setMask(!0),n.buffers.color.setMask(!0),i.clear(i.autoClearColor,i.autoClearDepth,i.autoClearStencil))}function p(S,_){const b=g(_);b&&(b.isCubeTexture||b.mapping===bl)?(h===void 0&&(h=new jt(new Si(1,1,1),new ws({name:"BackgroundCubeMaterial",uniforms:ia(Ni.backgroundCube.uniforms),vertexShader:Ni.backgroundCube.vertexShader,fragmentShader:Ni.backgroundCube.fragmentShader,side:Vn,depthTest:!1,depthWrite:!1,fog:!1})),h.geometry.deleteAttribute("normal"),h.geometry.deleteAttribute("uv"),h.onBeforeRender=function(I,A,R){this.matrixWorld.copyPosition(R.matrixWorld)},Object.defineProperty(h.material,"envMap",{get:function(){return this.uniforms.envMap.value}}),s.update(h)),zs.copy(_.backgroundRotation),zs.x*=-1,zs.y*=-1,zs.z*=-1,b.isCubeTexture&&b.isRenderTargetTexture===!1&&(zs.y*=-1,zs.z*=-1),h.material.uniforms.envMap.value=b,h.material.uniforms.flipEnvMap.value=b.isCubeTexture&&b.isRenderTargetTexture===!1?-1:1,h.material.uniforms.backgroundBlurriness.value=_.backgroundBlurriness,h.material.uniforms.backgroundIntensity.value=_.backgroundIntensity,h.material.uniforms.backgroundRotation.value.setFromMatrix4(__.makeRotationFromEuler(zs)),h.material.toneMapped=wt.getTransfer(b.colorSpace)!==Bt,(u!==b||d!==b.version||f!==i.toneMapping)&&(h.material.needsUpdate=!0,u=b,d=b.version,f=i.toneMapping),h.layers.enableAll(),S.unshift(h,h.geometry,h.material,0,0,null)):b&&b.isTexture&&(c===void 0&&(c=new jt(new lo(2,2),new ws({name:"BackgroundMaterial",uniforms:ia(Ni.background.uniforms),vertexShader:Ni.background.vertexShader,fragmentShader:Ni.background.fragmentShader,side:Ms,depthTest:!1,depthWrite:!1,fog:!1})),c.geometry.deleteAttribute("normal"),Object.defineProperty(c.material,"map",{get:function(){return this.uniforms.t2D.value}}),s.update(c)),c.material.uniforms.t2D.value=b,c.material.uniforms.backgroundIntensity.value=_.backgroundIntensity,c.material.toneMapped=wt.getTransfer(b.colorSpace)!==Bt,b.matrixAutoUpdate===!0&&b.updateMatrix(),c.material.uniforms.uvTransform.value.copy(b.matrix),(u!==b||d!==b.version||f!==i.toneMapping)&&(c.material.needsUpdate=!0,u=b,d=b.version,f=i.toneMapping),c.layers.enableAll(),S.unshift(c,c.geometry,c.material,0,0,null))}function m(S,_){S.getRGB(ko,bp(i)),n.buffers.color.setClear(ko.r,ko.g,ko.b,_,a)}return{getClearColor:function(){return o},setClearColor:function(S,_=1){o.set(S),l=_,m(o,l)},getClearAlpha:function(){return l},setClearAlpha:function(S){l=S,m(o,l)},render:v,addToRenderList:p}}function S_(i,e){const t=i.getParameter(i.MAX_VERTEX_ATTRIBS),n={},s=d(null);let r=s,a=!1;function o(y,P,X,H,J){let q=!1;const ee=u(H,X,P);r!==ee&&(r=ee,c(r.object)),q=f(y,H,X,J),q&&g(y,H,X,J),J!==null&&e.update(J,i.ELEMENT_ARRAY_BUFFER),(q||a)&&(a=!1,b(y,P,X,H),J!==null&&i.bindBuffer(i.ELEMENT_ARRAY_BUFFER,e.get(J).buffer))}function l(){return i.createVertexArray()}function c(y){return i.bindVertexArray(y)}function h(y){return i.deleteVertexArray(y)}function u(y,P,X){const H=X.wireframe===!0;let J=n[y.id];J===void 0&&(J={},n[y.id]=J);let q=J[P.id];q===void 0&&(q={},J[P.id]=q);let ee=q[H];return ee===void 0&&(ee=d(l()),q[H]=ee),ee}function d(y){const P=[],X=[],H=[];for(let J=0;J<t;J++)P[J]=0,X[J]=0,H[J]=0;return{geometry:null,program:null,wireframe:!1,newAttributes:P,enabledAttributes:X,attributeDivisors:H,object:y,attributes:{},index:null}}function f(y,P,X,H){const J=r.attributes,q=P.attributes;let ee=0;const j=X.getAttributes();for(const ne in j)if(j[ne].location>=0){const de=J[ne];let ye=q[ne];if(ye===void 0&&(ne==="instanceMatrix"&&y.instanceMatrix&&(ye=y.instanceMatrix),ne==="instanceColor"&&y.instanceColor&&(ye=y.instanceColor)),de===void 0||de.attribute!==ye||ye&&de.data!==ye.data)return!0;ee++}return r.attributesNum!==ee||r.index!==H}function g(y,P,X,H){const J={},q=P.attributes;let ee=0;const j=X.getAttributes();for(const ne in j)if(j[ne].location>=0){let de=q[ne];de===void 0&&(ne==="instanceMatrix"&&y.instanceMatrix&&(de=y.instanceMatrix),ne==="instanceColor"&&y.instanceColor&&(de=y.instanceColor));const ye={};ye.attribute=de,de&&de.data&&(ye.data=de.data),J[ne]=ye,ee++}r.attributes=J,r.attributesNum=ee,r.index=H}function v(){const y=r.newAttributes;for(let P=0,X=y.length;P<X;P++)y[P]=0}function p(y){m(y,0)}function m(y,P){const X=r.newAttributes,H=r.enabledAttributes,J=r.attributeDivisors;X[y]=1,H[y]===0&&(i.enableVertexAttribArray(y),H[y]=1),J[y]!==P&&(i.vertexAttribDivisor(y,P),J[y]=P)}function S(){const y=r.newAttributes,P=r.enabledAttributes;for(let X=0,H=P.length;X<H;X++)P[X]!==y[X]&&(i.disableVertexAttribArray(X),P[X]=0)}function _(y,P,X,H,J,q,ee){ee===!0?i.vertexAttribIPointer(y,P,X,J,q):i.vertexAttribPointer(y,P,X,H,J,q)}function b(y,P,X,H){v();const J=H.attributes,q=X.getAttributes(),ee=P.defaultAttributeValues;for(const j in q){const ne=q[j];if(ne.location>=0){let ge=J[j];if(ge===void 0&&(j==="instanceMatrix"&&y.instanceMatrix&&(ge=y.instanceMatrix),j==="instanceColor"&&y.instanceColor&&(ge=y.instanceColor)),ge!==void 0){const de=ge.normalized,ye=ge.itemSize,Te=e.get(ge);if(Te===void 0)continue;const Se=Te.buffer,ie=Te.type,he=Te.bytesPerElement,be=ie===i.INT||ie===i.UNSIGNED_INT||ge.gpuType===Gh;if(ge.isInterleavedBufferAttribute){const fe=ge.data,ze=fe.stride,We=ge.offset;if(fe.isInstancedInterleavedBuffer){for(let Fe=0;Fe<ne.locationSize;Fe++)m(ne.location+Fe,fe.meshPerAttribute);y.isInstancedMesh!==!0&&H._maxInstanceCount===void 0&&(H._maxInstanceCount=fe.meshPerAttribute*fe.count)}else for(let Fe=0;Fe<ne.locationSize;Fe++)p(ne.location+Fe);i.bindBuffer(i.ARRAY_BUFFER,Se);for(let Fe=0;Fe<ne.locationSize;Fe++)_(ne.location+Fe,ye/ne.locationSize,ie,de,ze*he,(We+ye/ne.locationSize*Fe)*he,be)}else{if(ge.isInstancedBufferAttribute){for(let fe=0;fe<ne.locationSize;fe++)m(ne.location+fe,ge.meshPerAttribute);y.isInstancedMesh!==!0&&H._maxInstanceCount===void 0&&(H._maxInstanceCount=ge.meshPerAttribute*ge.count)}else for(let fe=0;fe<ne.locationSize;fe++)p(ne.location+fe);i.bindBuffer(i.ARRAY_BUFFER,Se);for(let fe=0;fe<ne.locationSize;fe++)_(ne.location+fe,ye/ne.locationSize,ie,de,ye*he,ye/ne.locationSize*fe*he,be)}}else if(ee!==void 0){const de=ee[j];if(de!==void 0)switch(de.length){case 2:i.vertexAttrib2fv(ne.location,de);break;case 3:i.vertexAttrib3fv(ne.location,de);break;case 4:i.vertexAttrib4fv(ne.location,de);break;default:i.vertexAttrib1fv(ne.location,de)}}}}S()}function I(){N();for(const y in n){const P=n[y];for(const X in P){const H=P[X];for(const J in H)h(H[J].object),delete H[J];delete P[X]}delete n[y]}}function A(y){if(n[y.id]===void 0)return;const P=n[y.id];for(const X in P){const H=P[X];for(const J in H)h(H[J].object),delete H[J];delete P[X]}delete n[y.id]}function R(y){for(const P in n){const X=n[P];if(X[y.id]===void 0)continue;const H=X[y.id];for(const J in H)h(H[J].object),delete H[J];delete X[y.id]}}function N(){w(),a=!0,r!==s&&(r=s,c(r.object))}function w(){s.geometry=null,s.program=null,s.wireframe=!1}return{setup:o,reset:N,resetDefaultState:w,dispose:I,releaseStatesOfGeometry:A,releaseStatesOfProgram:R,initAttributes:v,enableAttribute:p,disableUnusedAttributes:S}}function b_(i,e,t){let n;function s(c){n=c}function r(c,h){i.drawArrays(n,c,h),t.update(h,n,1)}function a(c,h,u){u!==0&&(i.drawArraysInstanced(n,c,h,u),t.update(h,n,u))}function o(c,h,u){if(u===0)return;e.get("WEBGL_multi_draw").multiDrawArraysWEBGL(n,c,0,h,0,u);let f=0;for(let g=0;g<u;g++)f+=h[g];t.update(f,n,1)}function l(c,h,u,d){if(u===0)return;const f=e.get("WEBGL_multi_draw");if(f===null)for(let g=0;g<c.length;g++)a(c[g],h[g],d[g]);else{f.multiDrawArraysInstancedWEBGL(n,c,0,h,0,d,0,u);let g=0;for(let v=0;v<u;v++)g+=h[v];for(let v=0;v<d.length;v++)t.update(g,n,d[v])}}this.setMode=s,this.render=r,this.renderInstances=a,this.renderMultiDraw=o,this.renderMultiDrawInstances=l}function M_(i,e,t,n){let s;function r(){if(s!==void 0)return s;if(e.has("EXT_texture_filter_anisotropic")===!0){const A=e.get("EXT_texture_filter_anisotropic");s=i.getParameter(A.MAX_TEXTURE_MAX_ANISOTROPY_EXT)}else s=0;return s}function a(A){return!(A!==yi&&n.convert(A)!==i.getParameter(i.IMPLEMENTATION_COLOR_READ_FORMAT))}function o(A){const R=A===so&&(e.has("EXT_color_buffer_half_float")||e.has("EXT_color_buffer_float"));return!(A!==ss&&n.convert(A)!==i.getParameter(i.IMPLEMENTATION_COLOR_READ_TYPE)&&A!==Ji&&!R)}function l(A){if(A==="highp"){if(i.getShaderPrecisionFormat(i.VERTEX_SHADER,i.HIGH_FLOAT).precision>0&&i.getShaderPrecisionFormat(i.FRAGMENT_SHADER,i.HIGH_FLOAT).precision>0)return"highp";A="mediump"}return A==="mediump"&&i.getShaderPrecisionFormat(i.VERTEX_SHADER,i.MEDIUM_FLOAT).precision>0&&i.getShaderPrecisionFormat(i.FRAGMENT_SHADER,i.MEDIUM_FLOAT).precision>0?"mediump":"lowp"}let c=t.precision!==void 0?t.precision:"highp";const h=l(c);h!==c&&(console.warn("THREE.WebGLRenderer:",c,"not supported, using",h,"instead."),c=h);const u=t.logarithmicDepthBuffer===!0,d=i.getParameter(i.MAX_TEXTURE_IMAGE_UNITS),f=i.getParameter(i.MAX_VERTEX_TEXTURE_IMAGE_UNITS),g=i.getParameter(i.MAX_TEXTURE_SIZE),v=i.getParameter(i.MAX_CUBE_MAP_TEXTURE_SIZE),p=i.getParameter(i.MAX_VERTEX_ATTRIBS),m=i.getParameter(i.MAX_VERTEX_UNIFORM_VECTORS),S=i.getParameter(i.MAX_VARYING_VECTORS),_=i.getParameter(i.MAX_FRAGMENT_UNIFORM_VECTORS),b=f>0,I=i.getParameter(i.MAX_SAMPLES);return{isWebGL2:!0,getMaxAnisotropy:r,getMaxPrecision:l,textureFormatReadable:a,textureTypeReadable:o,precision:c,logarithmicDepthBuffer:u,maxTextures:d,maxVertexTextures:f,maxTextureSize:g,maxCubemapSize:v,maxAttributes:p,maxVertexUniforms:m,maxVaryings:S,maxFragmentUniforms:_,vertexTextures:b,maxSamples:I}}function w_(i){const e=this;let t=null,n=0,s=!1,r=!1;const a=new vs,o=new ot,l={value:null,needsUpdate:!1};this.uniform=l,this.numPlanes=0,this.numIntersection=0,this.init=function(u,d){const f=u.length!==0||d||n!==0||s;return s=d,n=u.length,f},this.beginShadows=function(){r=!0,h(null)},this.endShadows=function(){r=!1},this.setGlobalState=function(u,d){t=h(u,d,0)},this.setState=function(u,d,f){const g=u.clippingPlanes,v=u.clipIntersection,p=u.clipShadows,m=i.get(u);if(!s||g===null||g.length===0||r&&!p)r?h(null):c();else{const S=r?0:n,_=S*4;let b=m.clippingState||null;l.value=b,b=h(g,d,_,f);for(let I=0;I!==_;++I)b[I]=t[I];m.clippingState=b,this.numIntersection=v?this.numPlanes:0,this.numPlanes+=S}};function c(){l.value!==t&&(l.value=t,l.needsUpdate=n>0),e.numPlanes=n,e.numIntersection=0}function h(u,d,f,g){const v=u!==null?u.length:0;let p=null;if(v!==0){if(p=l.value,g!==!0||p===null){const m=f+v*4,S=d.matrixWorldInverse;o.getNormalMatrix(S),(p===null||p.length<m)&&(p=new Float32Array(m));for(let _=0,b=f;_!==v;++_,b+=4)a.copy(u[_]).applyMatrix4(S,o),a.normal.toArray(p,b),p[b+3]=a.constant}l.value=p,l.needsUpdate=!0}return e.numPlanes=v,e.numIntersection=0,p}}function E_(i){let e=new WeakMap;function t(a,o){return o===Yc?a.mapping=Qr:o===jc&&(a.mapping=ea),a}function n(a){if(a&&a.isTexture){const o=a.mapping;if(o===Yc||o===jc)if(e.has(a)){const l=e.get(a).texture;return t(l,a.mapping)}else{const l=a.image;if(l&&l.height>0){const c=new Ov(l.height);return c.fromEquirectangularTexture(i,a),e.set(a,c),a.addEventListener("dispose",s),t(c.texture,a.mapping)}else return null}}return a}function s(a){const o=a.target;o.removeEventListener("dispose",s);const l=e.get(o);l!==void 0&&(e.delete(o),l.dispose())}function r(){e=new WeakMap}return{get:n,dispose:r}}class Xa extends Mp{constructor(e=-1,t=1,n=1,s=-1,r=.1,a=2e3){super(),this.isOrthographicCamera=!0,this.type="OrthographicCamera",this.zoom=1,this.view=null,this.left=e,this.right=t,this.top=n,this.bottom=s,this.near=r,this.far=a,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.left=e.left,this.right=e.right,this.top=e.top,this.bottom=e.bottom,this.near=e.near,this.far=e.far,this.zoom=e.zoom,this.view=e.view===null?null:Object.assign({},e.view),this}setViewOffset(e,t,n,s,r,a){this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=n,this.view.offsetY=s,this.view.width=r,this.view.height=a,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const e=(this.right-this.left)/(2*this.zoom),t=(this.top-this.bottom)/(2*this.zoom),n=(this.right+this.left)/2,s=(this.top+this.bottom)/2;let r=n-e,a=n+e,o=s+t,l=s-t;if(this.view!==null&&this.view.enabled){const c=(this.right-this.left)/this.view.fullWidth/this.zoom,h=(this.top-this.bottom)/this.view.fullHeight/this.zoom;r+=c*this.view.offsetX,a=r+c*this.view.width,o-=h*this.view.offsetY,l=o-h*this.view.height}this.projectionMatrix.makeOrthographic(r,a,o,l,this.near,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){const t=super.toJSON(e);return t.object.zoom=this.zoom,t.object.left=this.left,t.object.right=this.right,t.object.top=this.top,t.object.bottom=this.bottom,t.object.near=this.near,t.object.far=this.far,this.view!==null&&(t.object.view=Object.assign({},this.view)),t}}const Wr=4,pd=[.125,.215,.35,.446,.526,.582],qs=20,yc=new Xa,md=new it;let Sc=null,bc=0,Mc=0,wc=!1;const Vs=(1+Math.sqrt(5))/2,Ur=1/Vs,gd=[new V(-Vs,Ur,0),new V(Vs,Ur,0),new V(-Ur,0,Vs),new V(Ur,0,Vs),new V(0,Vs,-Ur),new V(0,Vs,Ur),new V(-1,1,-1),new V(1,1,-1),new V(-1,1,1),new V(1,1,1)];class vd{constructor(e){this._renderer=e,this._pingPongRenderTarget=null,this._lodMax=0,this._cubeSize=0,this._lodPlanes=[],this._sizeLods=[],this._sigmas=[],this._blurMaterial=null,this._cubemapMaterial=null,this._equirectMaterial=null,this._compileMaterial(this._blurMaterial)}fromScene(e,t=0,n=.1,s=100){Sc=this._renderer.getRenderTarget(),bc=this._renderer.getActiveCubeFace(),Mc=this._renderer.getActiveMipmapLevel(),wc=this._renderer.xr.enabled,this._renderer.xr.enabled=!1,this._setSize(256);const r=this._allocateTargets();return r.depthBuffer=!0,this._sceneToCubeUV(e,n,s,r),t>0&&this._blur(r,0,0,t),this._applyPMREM(r),this._cleanup(r),r}fromEquirectangular(e,t=null){return this._fromTexture(e,t)}fromCubemap(e,t=null){return this._fromTexture(e,t)}compileCubemapShader(){this._cubemapMaterial===null&&(this._cubemapMaterial=yd(),this._compileMaterial(this._cubemapMaterial))}compileEquirectangularShader(){this._equirectMaterial===null&&(this._equirectMaterial=_d(),this._compileMaterial(this._equirectMaterial))}dispose(){this._dispose(),this._cubemapMaterial!==null&&this._cubemapMaterial.dispose(),this._equirectMaterial!==null&&this._equirectMaterial.dispose()}_setSize(e){this._lodMax=Math.floor(Math.log2(e)),this._cubeSize=Math.pow(2,this._lodMax)}_dispose(){this._blurMaterial!==null&&this._blurMaterial.dispose(),this._pingPongRenderTarget!==null&&this._pingPongRenderTarget.dispose();for(let e=0;e<this._lodPlanes.length;e++)this._lodPlanes[e].dispose()}_cleanup(e){this._renderer.setRenderTarget(Sc,bc,Mc),this._renderer.xr.enabled=wc,e.scissorTest=!1,Bo(e,0,0,e.width,e.height)}_fromTexture(e,t){e.mapping===Qr||e.mapping===ea?this._setSize(e.image.length===0?16:e.image[0].width||e.image[0].image.width):this._setSize(e.image.width/4),Sc=this._renderer.getRenderTarget(),bc=this._renderer.getActiveCubeFace(),Mc=this._renderer.getActiveMipmapLevel(),wc=this._renderer.xr.enabled,this._renderer.xr.enabled=!1;const n=t||this._allocateTargets();return this._textureToCubeUV(e,n),this._applyPMREM(n),this._cleanup(n),n}_allocateTargets(){const e=3*Math.max(this._cubeSize,112),t=4*this._cubeSize,n={magFilter:vi,minFilter:vi,generateMipmaps:!1,type:so,format:yi,colorSpace:Cs,depthBuffer:!1},s=xd(e,t,n);if(this._pingPongRenderTarget===null||this._pingPongRenderTarget.width!==e||this._pingPongRenderTarget.height!==t){this._pingPongRenderTarget!==null&&this._dispose(),this._pingPongRenderTarget=xd(e,t,n);const{_lodMax:r}=this;({sizeLods:this._sizeLods,lodPlanes:this._lodPlanes,sigmas:this._sigmas}=T_(r)),this._blurMaterial=A_(r,e,t)}return s}_compileMaterial(e){const t=new jt(this._lodPlanes[0],e);this._renderer.compile(t,yc)}_sceneToCubeUV(e,t,n,s){const o=new Rn(90,1,t,n),l=[1,-1,1,1,1,1],c=[1,1,1,-1,-1,-1],h=this._renderer,u=h.autoClear,d=h.toneMapping;h.getClearColor(md),h.toneMapping=Ss,h.autoClear=!1;const f=new es({name:"PMREM.Background",side:Vn,depthWrite:!1,depthTest:!1}),g=new jt(new Si,f);let v=!1;const p=e.background;p?p.isColor&&(f.color.copy(p),e.background=null,v=!0):(f.color.copy(md),v=!0);for(let m=0;m<6;m++){const S=m%3;S===0?(o.up.set(0,l[m],0),o.lookAt(c[m],0,0)):S===1?(o.up.set(0,0,l[m]),o.lookAt(0,c[m],0)):(o.up.set(0,l[m],0),o.lookAt(0,0,c[m]));const _=this._cubeSize;Bo(s,S*_,m>2?_:0,_,_),h.setRenderTarget(s),v&&h.render(g,o),h.render(e,o)}g.geometry.dispose(),g.material.dispose(),h.toneMapping=d,h.autoClear=u,e.background=p}_textureToCubeUV(e,t){const n=this._renderer,s=e.mapping===Qr||e.mapping===ea;s?(this._cubemapMaterial===null&&(this._cubemapMaterial=yd()),this._cubemapMaterial.uniforms.flipEnvMap.value=e.isRenderTargetTexture===!1?-1:1):this._equirectMaterial===null&&(this._equirectMaterial=_d());const r=s?this._cubemapMaterial:this._equirectMaterial,a=new jt(this._lodPlanes[0],r),o=r.uniforms;o.envMap.value=e;const l=this._cubeSize;Bo(t,0,0,3*l,2*l),n.setRenderTarget(t),n.render(a,yc)}_applyPMREM(e){const t=this._renderer,n=t.autoClear;t.autoClear=!1;const s=this._lodPlanes.length;for(let r=1;r<s;r++){const a=Math.sqrt(this._sigmas[r]*this._sigmas[r]-this._sigmas[r-1]*this._sigmas[r-1]),o=gd[(s-r-1)%gd.length];this._blur(e,r-1,r,a,o)}t.autoClear=n}_blur(e,t,n,s,r){const a=this._pingPongRenderTarget;this._halfBlur(e,a,t,n,s,"latitudinal",r),this._halfBlur(a,e,n,n,s,"longitudinal",r)}_halfBlur(e,t,n,s,r,a,o){const l=this._renderer,c=this._blurMaterial;a!=="latitudinal"&&a!=="longitudinal"&&console.error("blur direction must be either latitudinal or longitudinal!");const h=3,u=new jt(this._lodPlanes[s],c),d=c.uniforms,f=this._sizeLods[n]-1,g=isFinite(r)?Math.PI/(2*f):2*Math.PI/(2*qs-1),v=r/g,p=isFinite(r)?1+Math.floor(h*v):qs;p>qs&&console.warn(`sigmaRadians, ${r}, is too large and will clip, as it requested ${p} samples when the maximum is set to ${qs}`);const m=[];let S=0;for(let R=0;R<qs;++R){const N=R/v,w=Math.exp(-N*N/2);m.push(w),R===0?S+=w:R<p&&(S+=2*w)}for(let R=0;R<m.length;R++)m[R]=m[R]/S;d.envMap.value=e.texture,d.samples.value=p,d.weights.value=m,d.latitudinal.value=a==="latitudinal",o&&(d.poleAxis.value=o);const{_lodMax:_}=this;d.dTheta.value=g,d.mipInt.value=_-n;const b=this._sizeLods[s],I=3*b*(s>_-Wr?s-_+Wr:0),A=4*(this._cubeSize-b);Bo(t,I,A,3*b,2*b),l.setRenderTarget(t),l.render(u,yc)}}function T_(i){const e=[],t=[],n=[];let s=i;const r=i-Wr+1+pd.length;for(let a=0;a<r;a++){const o=Math.pow(2,s);t.push(o);let l=1/o;a>i-Wr?l=pd[a-i+Wr-1]:a===0&&(l=0),n.push(l);const c=1/(o-2),h=-c,u=1+c,d=[h,h,u,h,u,u,h,h,u,u,h,u],f=6,g=6,v=3,p=2,m=1,S=new Float32Array(v*g*f),_=new Float32Array(p*g*f),b=new Float32Array(m*g*f);for(let A=0;A<f;A++){const R=A%3*2/3-1,N=A>2?0:-1,w=[R,N,0,R+2/3,N,0,R+2/3,N+1,0,R,N,0,R+2/3,N+1,0,R,N+1,0];S.set(w,v*g*A),_.set(d,p*g*A);const y=[A,A,A,A,A,A];b.set(y,m*g*A)}const I=new Qt;I.setAttribute("position",new Mi(S,v)),I.setAttribute("uv",new Mi(_,p)),I.setAttribute("faceIndex",new Mi(b,m)),e.push(I),s>Wr&&s--}return{lodPlanes:e,sizeLods:t,sigmas:n}}function xd(i,e,t){const n=new Qs(i,e,t);return n.texture.mapping=bl,n.texture.name="PMREM.cubeUv",n.scissorTest=!0,n}function Bo(i,e,t,n,s){i.viewport.set(e,t,n,s),i.scissor.set(e,t,n,s)}function A_(i,e,t){const n=new Float32Array(qs),s=new V(0,1,0);return new ws({name:"SphericalGaussianBlur",defines:{n:qs,CUBEUV_TEXEL_WIDTH:1/e,CUBEUV_TEXEL_HEIGHT:1/t,CUBEUV_MAX_MIP:`${i}.0`},uniforms:{envMap:{value:null},samples:{value:1},weights:{value:n},latitudinal:{value:!1},dTheta:{value:0},mipInt:{value:0},poleAxis:{value:s}},vertexShader:Qh(),fragmentShader:`

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
		`,blending:ys,depthTest:!1,depthWrite:!1})}function _d(){return new ws({name:"EquirectangularToCubeUV",uniforms:{envMap:{value:null}},vertexShader:Qh(),fragmentShader:`

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
		`,blending:ys,depthTest:!1,depthWrite:!1})}function yd(){return new ws({name:"CubemapToCubeUV",uniforms:{envMap:{value:null},flipEnvMap:{value:-1}},vertexShader:Qh(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			uniform float flipEnvMap;

			varying vec3 vOutputDirection;

			uniform samplerCube envMap;

			void main() {

				gl_FragColor = textureCube( envMap, vec3( flipEnvMap * vOutputDirection.x, vOutputDirection.yz ) );

			}
		`,blending:ys,depthTest:!1,depthWrite:!1})}function Qh(){return`

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
	`}function C_(i){let e=new WeakMap,t=null;function n(o){if(o&&o.isTexture){const l=o.mapping,c=l===Yc||l===jc,h=l===Qr||l===ea;if(c||h){let u=e.get(o);const d=u!==void 0?u.texture.pmremVersion:0;if(o.isRenderTargetTexture&&o.pmremVersion!==d)return t===null&&(t=new vd(i)),u=c?t.fromEquirectangular(o,u):t.fromCubemap(o,u),u.texture.pmremVersion=o.pmremVersion,e.set(o,u),u.texture;if(u!==void 0)return u.texture;{const f=o.image;return c&&f&&f.height>0||h&&f&&s(f)?(t===null&&(t=new vd(i)),u=c?t.fromEquirectangular(o):t.fromCubemap(o),u.texture.pmremVersion=o.pmremVersion,e.set(o,u),o.addEventListener("dispose",r),u.texture):null}}}return o}function s(o){let l=0;const c=6;for(let h=0;h<c;h++)o[h]!==void 0&&l++;return l===c}function r(o){const l=o.target;l.removeEventListener("dispose",r);const c=e.get(l);c!==void 0&&(e.delete(l),c.dispose())}function a(){e=new WeakMap,t!==null&&(t.dispose(),t=null)}return{get:n,dispose:a}}function R_(i){const e={};function t(n){if(e[n]!==void 0)return e[n];let s;switch(n){case"WEBGL_depth_texture":s=i.getExtension("WEBGL_depth_texture")||i.getExtension("MOZ_WEBGL_depth_texture")||i.getExtension("WEBKIT_WEBGL_depth_texture");break;case"EXT_texture_filter_anisotropic":s=i.getExtension("EXT_texture_filter_anisotropic")||i.getExtension("MOZ_EXT_texture_filter_anisotropic")||i.getExtension("WEBKIT_EXT_texture_filter_anisotropic");break;case"WEBGL_compressed_texture_s3tc":s=i.getExtension("WEBGL_compressed_texture_s3tc")||i.getExtension("MOZ_WEBGL_compressed_texture_s3tc")||i.getExtension("WEBKIT_WEBGL_compressed_texture_s3tc");break;case"WEBGL_compressed_texture_pvrtc":s=i.getExtension("WEBGL_compressed_texture_pvrtc")||i.getExtension("WEBKIT_WEBGL_compressed_texture_pvrtc");break;default:s=i.getExtension(n)}return e[n]=s,s}return{has:function(n){return t(n)!==null},init:function(){t("EXT_color_buffer_float"),t("WEBGL_clip_cull_distance"),t("OES_texture_float_linear"),t("EXT_color_buffer_half_float"),t("WEBGL_multisampled_render_to_texture"),t("WEBGL_render_shared_exponent")},get:function(n){const s=t(n);return s===null&&Yr("THREE.WebGLRenderer: "+n+" extension not supported."),s}}}function P_(i,e,t,n){const s={},r=new WeakMap;function a(u){const d=u.target;d.index!==null&&e.remove(d.index);for(const g in d.attributes)e.remove(d.attributes[g]);for(const g in d.morphAttributes){const v=d.morphAttributes[g];for(let p=0,m=v.length;p<m;p++)e.remove(v[p])}d.removeEventListener("dispose",a),delete s[d.id];const f=r.get(d);f&&(e.remove(f),r.delete(d)),n.releaseStatesOfGeometry(d),d.isInstancedBufferGeometry===!0&&delete d._maxInstanceCount,t.memory.geometries--}function o(u,d){return s[d.id]===!0||(d.addEventListener("dispose",a),s[d.id]=!0,t.memory.geometries++),d}function l(u){const d=u.attributes;for(const g in d)e.update(d[g],i.ARRAY_BUFFER);const f=u.morphAttributes;for(const g in f){const v=f[g];for(let p=0,m=v.length;p<m;p++)e.update(v[p],i.ARRAY_BUFFER)}}function c(u){const d=[],f=u.index,g=u.attributes.position;let v=0;if(f!==null){const S=f.array;v=f.version;for(let _=0,b=S.length;_<b;_+=3){const I=S[_+0],A=S[_+1],R=S[_+2];d.push(I,A,A,R,R,I)}}else if(g!==void 0){const S=g.array;v=g.version;for(let _=0,b=S.length/3-1;_<b;_+=3){const I=_+0,A=_+1,R=_+2;d.push(I,A,A,R,R,I)}}else return;const p=new(gp(d)?Sp:yp)(d,1);p.version=v;const m=r.get(u);m&&e.remove(m),r.set(u,p)}function h(u){const d=r.get(u);if(d){const f=u.index;f!==null&&d.version<f.version&&c(u)}else c(u);return r.get(u)}return{get:o,update:l,getWireframeAttribute:h}}function L_(i,e,t){let n;function s(d){n=d}let r,a;function o(d){r=d.type,a=d.bytesPerElement}function l(d,f){i.drawElements(n,f,r,d*a),t.update(f,n,1)}function c(d,f,g){g!==0&&(i.drawElementsInstanced(n,f,r,d*a,g),t.update(f,n,g))}function h(d,f,g){if(g===0)return;e.get("WEBGL_multi_draw").multiDrawElementsWEBGL(n,f,0,r,d,0,g);let p=0;for(let m=0;m<g;m++)p+=f[m];t.update(p,n,1)}function u(d,f,g,v){if(g===0)return;const p=e.get("WEBGL_multi_draw");if(p===null)for(let m=0;m<d.length;m++)c(d[m]/a,f[m],v[m]);else{p.multiDrawElementsInstancedWEBGL(n,f,0,r,d,0,v,0,g);let m=0;for(let S=0;S<g;S++)m+=f[S];for(let S=0;S<v.length;S++)t.update(m,n,v[S])}}this.setMode=s,this.setIndex=o,this.render=l,this.renderInstances=c,this.renderMultiDraw=h,this.renderMultiDrawInstances=u}function D_(i){const e={geometries:0,textures:0},t={frame:0,calls:0,triangles:0,points:0,lines:0};function n(r,a,o){switch(t.calls++,a){case i.TRIANGLES:t.triangles+=o*(r/3);break;case i.LINES:t.lines+=o*(r/2);break;case i.LINE_STRIP:t.lines+=o*(r-1);break;case i.LINE_LOOP:t.lines+=o*r;break;case i.POINTS:t.points+=o*r;break;default:console.error("THREE.WebGLInfo: Unknown draw mode:",a);break}}function s(){t.calls=0,t.triangles=0,t.points=0,t.lines=0}return{memory:e,render:t,programs:null,autoReset:!0,reset:s,update:n}}function I_(i,e,t){const n=new WeakMap,s=new on;function r(a,o,l){const c=a.morphTargetInfluences,h=o.morphAttributes.position||o.morphAttributes.normal||o.morphAttributes.color,u=h!==void 0?h.length:0;let d=n.get(o);if(d===void 0||d.count!==u){let y=function(){N.dispose(),n.delete(o),o.removeEventListener("dispose",y)};var f=y;d!==void 0&&d.texture.dispose();const g=o.morphAttributes.position!==void 0,v=o.morphAttributes.normal!==void 0,p=o.morphAttributes.color!==void 0,m=o.morphAttributes.position||[],S=o.morphAttributes.normal||[],_=o.morphAttributes.color||[];let b=0;g===!0&&(b=1),v===!0&&(b=2),p===!0&&(b=3);let I=o.attributes.position.count*b,A=1;I>e.maxTextureSize&&(A=Math.ceil(I/e.maxTextureSize),I=e.maxTextureSize);const R=new Float32Array(I*A*4*u),N=new xp(R,I,A,u);N.type=Ji,N.needsUpdate=!0;const w=b*4;for(let P=0;P<u;P++){const X=m[P],H=S[P],J=_[P],q=I*A*4*P;for(let ee=0;ee<X.count;ee++){const j=ee*w;g===!0&&(s.fromBufferAttribute(X,ee),R[q+j+0]=s.x,R[q+j+1]=s.y,R[q+j+2]=s.z,R[q+j+3]=0),v===!0&&(s.fromBufferAttribute(H,ee),R[q+j+4]=s.x,R[q+j+5]=s.y,R[q+j+6]=s.z,R[q+j+7]=0),p===!0&&(s.fromBufferAttribute(J,ee),R[q+j+8]=s.x,R[q+j+9]=s.y,R[q+j+10]=s.z,R[q+j+11]=J.itemSize===4?s.w:1)}}d={count:u,texture:N,size:new Xe(I,A)},n.set(o,d),o.addEventListener("dispose",y)}if(a.isInstancedMesh===!0&&a.morphTexture!==null)l.getUniforms().setValue(i,"morphTexture",a.morphTexture,t);else{let g=0;for(let p=0;p<c.length;p++)g+=c[p];const v=o.morphTargetsRelative?1:1-g;l.getUniforms().setValue(i,"morphTargetBaseInfluence",v),l.getUniforms().setValue(i,"morphTargetInfluences",c)}l.getUniforms().setValue(i,"morphTargetsTexture",d.texture,t),l.getUniforms().setValue(i,"morphTargetsTextureSize",d.size)}return{update:r}}function U_(i,e,t,n){let s=new WeakMap;function r(l){const c=n.render.frame,h=l.geometry,u=e.get(l,h);if(s.get(u)!==c&&(e.update(u),s.set(u,c)),l.isInstancedMesh&&(l.hasEventListener("dispose",o)===!1&&l.addEventListener("dispose",o),s.get(l)!==c&&(t.update(l.instanceMatrix,i.ARRAY_BUFFER),l.instanceColor!==null&&t.update(l.instanceColor,i.ARRAY_BUFFER),s.set(l,c))),l.isSkinnedMesh){const d=l.skeleton;s.get(d)!==c&&(d.update(),s.set(d,c))}return u}function a(){s=new WeakMap}function o(l){const c=l.target;c.removeEventListener("dispose",o),t.remove(c.instanceMatrix),c.instanceColor!==null&&t.remove(c.instanceColor)}return{update:r,dispose:a}}class Tp extends Bn{constructor(e,t,n,s,r,a,o,l,c,h=qr){if(h!==qr&&h!==na)throw new Error("DepthTexture format must be either THREE.DepthFormat or THREE.DepthStencilFormat");n===void 0&&h===qr&&(n=Zs),n===void 0&&h===na&&(n=ta),super(null,s,r,a,o,l,h,n,c),this.isDepthTexture=!0,this.image={width:e,height:t},this.magFilter=o!==void 0?o:ai,this.minFilter=l!==void 0?l:ai,this.flipY=!1,this.generateMipmaps=!1,this.compareFunction=null}copy(e){return super.copy(e),this.compareFunction=e.compareFunction,this}toJSON(e){const t=super.toJSON(e);return this.compareFunction!==null&&(t.compareFunction=this.compareFunction),t}}const Ap=new Bn,Sd=new Tp(1,1),Cp=new xp,Rp=new yv,Pp=new wp,bd=[],Md=[],wd=new Float32Array(16),Ed=new Float32Array(9),Td=new Float32Array(4);function ma(i,e,t){const n=i[0];if(n<=0||n>0)return i;const s=e*t;let r=bd[s];if(r===void 0&&(r=new Float32Array(s),bd[s]=r),e!==0){n.toArray(r,0);for(let a=1,o=0;a!==e;++a)o+=t,i[a].toArray(r,o)}return r}function ln(i,e){if(i.length!==e.length)return!1;for(let t=0,n=i.length;t<n;t++)if(i[t]!==e[t])return!1;return!0}function cn(i,e){for(let t=0,n=e.length;t<n;t++)i[t]=e[t]}function wl(i,e){let t=Md[e];t===void 0&&(t=new Int32Array(e),Md[e]=t);for(let n=0;n!==e;++n)t[n]=i.allocateTextureUnit();return t}function N_(i,e){const t=this.cache;t[0]!==e&&(i.uniform1f(this.addr,e),t[0]=e)}function O_(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(i.uniform2f(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(ln(t,e))return;i.uniform2fv(this.addr,e),cn(t,e)}}function F_(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(i.uniform3f(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else if(e.r!==void 0)(t[0]!==e.r||t[1]!==e.g||t[2]!==e.b)&&(i.uniform3f(this.addr,e.r,e.g,e.b),t[0]=e.r,t[1]=e.g,t[2]=e.b);else{if(ln(t,e))return;i.uniform3fv(this.addr,e),cn(t,e)}}function k_(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(i.uniform4f(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(ln(t,e))return;i.uniform4fv(this.addr,e),cn(t,e)}}function B_(i,e){const t=this.cache,n=e.elements;if(n===void 0){if(ln(t,e))return;i.uniformMatrix2fv(this.addr,!1,e),cn(t,e)}else{if(ln(t,n))return;Td.set(n),i.uniformMatrix2fv(this.addr,!1,Td),cn(t,n)}}function z_(i,e){const t=this.cache,n=e.elements;if(n===void 0){if(ln(t,e))return;i.uniformMatrix3fv(this.addr,!1,e),cn(t,e)}else{if(ln(t,n))return;Ed.set(n),i.uniformMatrix3fv(this.addr,!1,Ed),cn(t,n)}}function H_(i,e){const t=this.cache,n=e.elements;if(n===void 0){if(ln(t,e))return;i.uniformMatrix4fv(this.addr,!1,e),cn(t,e)}else{if(ln(t,n))return;wd.set(n),i.uniformMatrix4fv(this.addr,!1,wd),cn(t,n)}}function V_(i,e){const t=this.cache;t[0]!==e&&(i.uniform1i(this.addr,e),t[0]=e)}function G_(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(i.uniform2i(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(ln(t,e))return;i.uniform2iv(this.addr,e),cn(t,e)}}function W_(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(i.uniform3i(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(ln(t,e))return;i.uniform3iv(this.addr,e),cn(t,e)}}function $_(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(i.uniform4i(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(ln(t,e))return;i.uniform4iv(this.addr,e),cn(t,e)}}function q_(i,e){const t=this.cache;t[0]!==e&&(i.uniform1ui(this.addr,e),t[0]=e)}function X_(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(i.uniform2ui(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(ln(t,e))return;i.uniform2uiv(this.addr,e),cn(t,e)}}function Y_(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(i.uniform3ui(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(ln(t,e))return;i.uniform3uiv(this.addr,e),cn(t,e)}}function j_(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(i.uniform4ui(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(ln(t,e))return;i.uniform4uiv(this.addr,e),cn(t,e)}}function K_(i,e,t){const n=this.cache,s=t.allocateTextureUnit();n[0]!==s&&(i.uniform1i(this.addr,s),n[0]=s);let r;this.type===i.SAMPLER_2D_SHADOW?(Sd.compareFunction=mp,r=Sd):r=Ap,t.setTexture2D(e||r,s)}function J_(i,e,t){const n=this.cache,s=t.allocateTextureUnit();n[0]!==s&&(i.uniform1i(this.addr,s),n[0]=s),t.setTexture3D(e||Rp,s)}function Z_(i,e,t){const n=this.cache,s=t.allocateTextureUnit();n[0]!==s&&(i.uniform1i(this.addr,s),n[0]=s),t.setTextureCube(e||Pp,s)}function Q_(i,e,t){const n=this.cache,s=t.allocateTextureUnit();n[0]!==s&&(i.uniform1i(this.addr,s),n[0]=s),t.setTexture2DArray(e||Cp,s)}function ey(i){switch(i){case 5126:return N_;case 35664:return O_;case 35665:return F_;case 35666:return k_;case 35674:return B_;case 35675:return z_;case 35676:return H_;case 5124:case 35670:return V_;case 35667:case 35671:return G_;case 35668:case 35672:return W_;case 35669:case 35673:return $_;case 5125:return q_;case 36294:return X_;case 36295:return Y_;case 36296:return j_;case 35678:case 36198:case 36298:case 36306:case 35682:return K_;case 35679:case 36299:case 36307:return J_;case 35680:case 36300:case 36308:case 36293:return Z_;case 36289:case 36303:case 36311:case 36292:return Q_}}function ty(i,e){i.uniform1fv(this.addr,e)}function ny(i,e){const t=ma(e,this.size,2);i.uniform2fv(this.addr,t)}function iy(i,e){const t=ma(e,this.size,3);i.uniform3fv(this.addr,t)}function sy(i,e){const t=ma(e,this.size,4);i.uniform4fv(this.addr,t)}function ry(i,e){const t=ma(e,this.size,4);i.uniformMatrix2fv(this.addr,!1,t)}function ay(i,e){const t=ma(e,this.size,9);i.uniformMatrix3fv(this.addr,!1,t)}function oy(i,e){const t=ma(e,this.size,16);i.uniformMatrix4fv(this.addr,!1,t)}function ly(i,e){i.uniform1iv(this.addr,e)}function cy(i,e){i.uniform2iv(this.addr,e)}function hy(i,e){i.uniform3iv(this.addr,e)}function uy(i,e){i.uniform4iv(this.addr,e)}function dy(i,e){i.uniform1uiv(this.addr,e)}function fy(i,e){i.uniform2uiv(this.addr,e)}function py(i,e){i.uniform3uiv(this.addr,e)}function my(i,e){i.uniform4uiv(this.addr,e)}function gy(i,e,t){const n=this.cache,s=e.length,r=wl(t,s);ln(n,r)||(i.uniform1iv(this.addr,r),cn(n,r));for(let a=0;a!==s;++a)t.setTexture2D(e[a]||Ap,r[a])}function vy(i,e,t){const n=this.cache,s=e.length,r=wl(t,s);ln(n,r)||(i.uniform1iv(this.addr,r),cn(n,r));for(let a=0;a!==s;++a)t.setTexture3D(e[a]||Rp,r[a])}function xy(i,e,t){const n=this.cache,s=e.length,r=wl(t,s);ln(n,r)||(i.uniform1iv(this.addr,r),cn(n,r));for(let a=0;a!==s;++a)t.setTextureCube(e[a]||Pp,r[a])}function _y(i,e,t){const n=this.cache,s=e.length,r=wl(t,s);ln(n,r)||(i.uniform1iv(this.addr,r),cn(n,r));for(let a=0;a!==s;++a)t.setTexture2DArray(e[a]||Cp,r[a])}function yy(i){switch(i){case 5126:return ty;case 35664:return ny;case 35665:return iy;case 35666:return sy;case 35674:return ry;case 35675:return ay;case 35676:return oy;case 5124:case 35670:return ly;case 35667:case 35671:return cy;case 35668:case 35672:return hy;case 35669:case 35673:return uy;case 5125:return dy;case 36294:return fy;case 36295:return py;case 36296:return my;case 35678:case 36198:case 36298:case 36306:case 35682:return gy;case 35679:case 36299:case 36307:return vy;case 35680:case 36300:case 36308:case 36293:return xy;case 36289:case 36303:case 36311:case 36292:return _y}}class Sy{constructor(e,t,n){this.id=e,this.addr=n,this.cache=[],this.type=t.type,this.setValue=ey(t.type)}}class by{constructor(e,t,n){this.id=e,this.addr=n,this.cache=[],this.type=t.type,this.size=t.size,this.setValue=yy(t.type)}}class My{constructor(e){this.id=e,this.seq=[],this.map={}}setValue(e,t,n){const s=this.seq;for(let r=0,a=s.length;r!==a;++r){const o=s[r];o.setValue(e,t[o.id],n)}}}const Ec=/(\w+)(\])?(\[|\.)?/g;function Ad(i,e){i.seq.push(e),i.map[e.id]=e}function wy(i,e,t){const n=i.name,s=n.length;for(Ec.lastIndex=0;;){const r=Ec.exec(n),a=Ec.lastIndex;let o=r[1];const l=r[2]==="]",c=r[3];if(l&&(o=o|0),c===void 0||c==="["&&a+2===s){Ad(t,c===void 0?new Sy(o,i,e):new by(o,i,e));break}else{let u=t.map[o];u===void 0&&(u=new My(o),Ad(t,u)),t=u}}}class ol{constructor(e,t){this.seq=[],this.map={};const n=e.getProgramParameter(t,e.ACTIVE_UNIFORMS);for(let s=0;s<n;++s){const r=e.getActiveUniform(t,s),a=e.getUniformLocation(t,r.name);wy(r,a,this)}}setValue(e,t,n,s){const r=this.map[t];r!==void 0&&r.setValue(e,n,s)}setOptional(e,t,n){const s=t[n];s!==void 0&&this.setValue(e,n,s)}static upload(e,t,n,s){for(let r=0,a=t.length;r!==a;++r){const o=t[r],l=n[o.id];l.needsUpdate!==!1&&o.setValue(e,l.value,s)}}static seqWithValue(e,t){const n=[];for(let s=0,r=e.length;s!==r;++s){const a=e[s];a.id in t&&n.push(a)}return n}}function Cd(i,e,t){const n=i.createShader(e);return i.shaderSource(n,t),i.compileShader(n),n}const Ey=37297;let Ty=0;function Ay(i,e){const t=i.split(`
`),n=[],s=Math.max(e-6,0),r=Math.min(e+6,t.length);for(let a=s;a<r;a++){const o=a+1;n.push(`${o===e?">":" "} ${o}: ${t[a]}`)}return n.join(`
`)}function Cy(i){const e=wt.getPrimaries(wt.workingColorSpace),t=wt.getPrimaries(i);let n;switch(e===t?n="":e===dl&&t===ul?n="LinearDisplayP3ToLinearSRGB":e===ul&&t===dl&&(n="LinearSRGBToLinearDisplayP3"),i){case Cs:case Ml:return[n,"LinearTransferOETF"];case Ui:case jh:return[n,"sRGBTransferOETF"];default:return console.warn("THREE.WebGLProgram: Unsupported color space:",i),[n,"LinearTransferOETF"]}}function Rd(i,e,t){const n=i.getShaderParameter(e,i.COMPILE_STATUS),s=i.getShaderInfoLog(e).trim();if(n&&s==="")return"";const r=/ERROR: 0:(\d+)/.exec(s);if(r){const a=parseInt(r[1]);return t.toUpperCase()+`

`+s+`

`+Ay(i.getShaderSource(e),a)}else return s}function Ry(i,e){const t=Cy(e);return`vec4 ${i}( vec4 value ) { return ${t[0]}( ${t[1]}( value ) ); }`}function Py(i,e){let t;switch(e){case Ig:t="Linear";break;case Ug:t="Reinhard";break;case Ng:t="Cineon";break;case np:t="ACESFilmic";break;case Fg:t="AgX";break;case kg:t="Neutral";break;case Og:t="Custom";break;default:console.warn("THREE.WebGLProgram: Unsupported toneMapping:",e),t="Linear"}return"vec3 "+i+"( vec3 color ) { return "+t+"ToneMapping( color ); }"}const zo=new V;function Ly(){wt.getLuminanceCoefficients(zo);const i=zo.x.toFixed(4),e=zo.y.toFixed(4),t=zo.z.toFixed(4);return["float luminance( const in vec3 rgb ) {",`	const vec3 weights = vec3( ${i}, ${e}, ${t} );`,"	return dot( weights, rgb );","}"].join(`
`)}function Dy(i){return[i.extensionClipCullDistance?"#extension GL_ANGLE_clip_cull_distance : require":"",i.extensionMultiDraw?"#extension GL_ANGLE_multi_draw : require":""].filter(Va).join(`
`)}function Iy(i){const e=[];for(const t in i){const n=i[t];n!==!1&&e.push("#define "+t+" "+n)}return e.join(`
`)}function Uy(i,e){const t={},n=i.getProgramParameter(e,i.ACTIVE_ATTRIBUTES);for(let s=0;s<n;s++){const r=i.getActiveAttrib(e,s),a=r.name;let o=1;r.type===i.FLOAT_MAT2&&(o=2),r.type===i.FLOAT_MAT3&&(o=3),r.type===i.FLOAT_MAT4&&(o=4),t[a]={type:r.type,location:i.getAttribLocation(e,a),locationSize:o}}return t}function Va(i){return i!==""}function Pd(i,e){const t=e.numSpotLightShadows+e.numSpotLightMaps-e.numSpotLightShadowsWithMaps;return i.replace(/NUM_DIR_LIGHTS/g,e.numDirLights).replace(/NUM_SPOT_LIGHTS/g,e.numSpotLights).replace(/NUM_SPOT_LIGHT_MAPS/g,e.numSpotLightMaps).replace(/NUM_SPOT_LIGHT_COORDS/g,t).replace(/NUM_RECT_AREA_LIGHTS/g,e.numRectAreaLights).replace(/NUM_POINT_LIGHTS/g,e.numPointLights).replace(/NUM_HEMI_LIGHTS/g,e.numHemiLights).replace(/NUM_DIR_LIGHT_SHADOWS/g,e.numDirLightShadows).replace(/NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS/g,e.numSpotLightShadowsWithMaps).replace(/NUM_SPOT_LIGHT_SHADOWS/g,e.numSpotLightShadows).replace(/NUM_POINT_LIGHT_SHADOWS/g,e.numPointLightShadows)}function Ld(i,e){return i.replace(/NUM_CLIPPING_PLANES/g,e.numClippingPlanes).replace(/UNION_CLIPPING_PLANES/g,e.numClippingPlanes-e.numClipIntersection)}const Ny=/^[ \t]*#include +<([\w\d./]+)>/gm;function Eh(i){return i.replace(Ny,Fy)}const Oy=new Map;function Fy(i,e){let t=at[e];if(t===void 0){const n=Oy.get(e);if(n!==void 0)t=at[n],console.warn('THREE.WebGLRenderer: Shader chunk "%s" has been deprecated. Use "%s" instead.',e,n);else throw new Error("Can not resolve #include <"+e+">")}return Eh(t)}const ky=/#pragma unroll_loop_start\s+for\s*\(\s*int\s+i\s*=\s*(\d+)\s*;\s*i\s*<\s*(\d+)\s*;\s*i\s*\+\+\s*\)\s*{([\s\S]+?)}\s+#pragma unroll_loop_end/g;function Dd(i){return i.replace(ky,By)}function By(i,e,t,n){let s="";for(let r=parseInt(e);r<parseInt(t);r++)s+=n.replace(/\[\s*i\s*\]/g,"[ "+r+" ]").replace(/UNROLLED_LOOP_INDEX/g,r);return s}function Id(i){let e=`precision ${i.precision} float;
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
#define LOW_PRECISION`),e}function zy(i){let e="SHADOWMAP_TYPE_BASIC";return i.shadowMapType===Qf?e="SHADOWMAP_TYPE_PCF":i.shadowMapType===ep?e="SHADOWMAP_TYPE_PCF_SOFT":i.shadowMapType===ji&&(e="SHADOWMAP_TYPE_VSM"),e}function Hy(i){let e="ENVMAP_TYPE_CUBE";if(i.envMap)switch(i.envMapMode){case Qr:case ea:e="ENVMAP_TYPE_CUBE";break;case bl:e="ENVMAP_TYPE_CUBE_UV";break}return e}function Vy(i){let e="ENVMAP_MODE_REFLECTION";if(i.envMap)switch(i.envMapMode){case ea:e="ENVMAP_MODE_REFRACTION";break}return e}function Gy(i){let e="ENVMAP_BLENDING_NONE";if(i.envMap)switch(i.combine){case tp:e="ENVMAP_BLENDING_MULTIPLY";break;case Lg:e="ENVMAP_BLENDING_MIX";break;case Dg:e="ENVMAP_BLENDING_ADD";break}return e}function Wy(i){const e=i.envMapCubeUVHeight;if(e===null)return null;const t=Math.log2(e)-2,n=1/e;return{texelWidth:1/(3*Math.max(Math.pow(2,t),7*16)),texelHeight:n,maxMip:t}}function $y(i,e,t,n){const s=i.getContext(),r=t.defines;let a=t.vertexShader,o=t.fragmentShader;const l=zy(t),c=Hy(t),h=Vy(t),u=Gy(t),d=Wy(t),f=Dy(t),g=Iy(r),v=s.createProgram();let p,m,S=t.glslVersion?"#version "+t.glslVersion+`
`:"";t.isRawShaderMaterial?(p=["#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,g].filter(Va).join(`
`),p.length>0&&(p+=`
`),m=["#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,g].filter(Va).join(`
`),m.length>0&&(m+=`
`)):(p=[Id(t),"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,g,t.extensionClipCullDistance?"#define USE_CLIP_DISTANCE":"",t.batching?"#define USE_BATCHING":"",t.batchingColor?"#define USE_BATCHING_COLOR":"",t.instancing?"#define USE_INSTANCING":"",t.instancingColor?"#define USE_INSTANCING_COLOR":"",t.instancingMorph?"#define USE_INSTANCING_MORPH":"",t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.map?"#define USE_MAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+h:"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",t.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",t.displacementMap?"#define USE_DISPLACEMENTMAP":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.anisotropy?"#define USE_ANISOTROPY":"",t.anisotropyMap?"#define USE_ANISOTROPYMAP":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",t.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaHash?"#define USE_ALPHAHASH":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",t.mapUv?"#define MAP_UV "+t.mapUv:"",t.alphaMapUv?"#define ALPHAMAP_UV "+t.alphaMapUv:"",t.lightMapUv?"#define LIGHTMAP_UV "+t.lightMapUv:"",t.aoMapUv?"#define AOMAP_UV "+t.aoMapUv:"",t.emissiveMapUv?"#define EMISSIVEMAP_UV "+t.emissiveMapUv:"",t.bumpMapUv?"#define BUMPMAP_UV "+t.bumpMapUv:"",t.normalMapUv?"#define NORMALMAP_UV "+t.normalMapUv:"",t.displacementMapUv?"#define DISPLACEMENTMAP_UV "+t.displacementMapUv:"",t.metalnessMapUv?"#define METALNESSMAP_UV "+t.metalnessMapUv:"",t.roughnessMapUv?"#define ROUGHNESSMAP_UV "+t.roughnessMapUv:"",t.anisotropyMapUv?"#define ANISOTROPYMAP_UV "+t.anisotropyMapUv:"",t.clearcoatMapUv?"#define CLEARCOATMAP_UV "+t.clearcoatMapUv:"",t.clearcoatNormalMapUv?"#define CLEARCOAT_NORMALMAP_UV "+t.clearcoatNormalMapUv:"",t.clearcoatRoughnessMapUv?"#define CLEARCOAT_ROUGHNESSMAP_UV "+t.clearcoatRoughnessMapUv:"",t.iridescenceMapUv?"#define IRIDESCENCEMAP_UV "+t.iridescenceMapUv:"",t.iridescenceThicknessMapUv?"#define IRIDESCENCE_THICKNESSMAP_UV "+t.iridescenceThicknessMapUv:"",t.sheenColorMapUv?"#define SHEEN_COLORMAP_UV "+t.sheenColorMapUv:"",t.sheenRoughnessMapUv?"#define SHEEN_ROUGHNESSMAP_UV "+t.sheenRoughnessMapUv:"",t.specularMapUv?"#define SPECULARMAP_UV "+t.specularMapUv:"",t.specularColorMapUv?"#define SPECULAR_COLORMAP_UV "+t.specularColorMapUv:"",t.specularIntensityMapUv?"#define SPECULAR_INTENSITYMAP_UV "+t.specularIntensityMapUv:"",t.transmissionMapUv?"#define TRANSMISSIONMAP_UV "+t.transmissionMapUv:"",t.thicknessMapUv?"#define THICKNESSMAP_UV "+t.thicknessMapUv:"",t.vertexTangents&&t.flatShading===!1?"#define USE_TANGENT":"",t.vertexColors?"#define USE_COLOR":"",t.vertexAlphas?"#define USE_COLOR_ALPHA":"",t.vertexUv1s?"#define USE_UV1":"",t.vertexUv2s?"#define USE_UV2":"",t.vertexUv3s?"#define USE_UV3":"",t.pointsUvs?"#define USE_POINTS_UV":"",t.flatShading?"#define FLAT_SHADED":"",t.skinning?"#define USE_SKINNING":"",t.morphTargets?"#define USE_MORPHTARGETS":"",t.morphNormals&&t.flatShading===!1?"#define USE_MORPHNORMALS":"",t.morphColors?"#define USE_MORPHCOLORS":"",t.morphTargetsCount>0?"#define MORPHTARGETS_TEXTURE_STRIDE "+t.morphTextureStride:"",t.morphTargetsCount>0?"#define MORPHTARGETS_COUNT "+t.morphTargetsCount:"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+l:"",t.sizeAttenuation?"#define USE_SIZEATTENUATION":"",t.numLightProbes>0?"#define USE_LIGHT_PROBES":"",t.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"","uniform mat4 modelMatrix;","uniform mat4 modelViewMatrix;","uniform mat4 projectionMatrix;","uniform mat4 viewMatrix;","uniform mat3 normalMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;","#ifdef USE_INSTANCING","	attribute mat4 instanceMatrix;","#endif","#ifdef USE_INSTANCING_COLOR","	attribute vec3 instanceColor;","#endif","#ifdef USE_INSTANCING_MORPH","	uniform sampler2D morphTexture;","#endif","attribute vec3 position;","attribute vec3 normal;","attribute vec2 uv;","#ifdef USE_UV1","	attribute vec2 uv1;","#endif","#ifdef USE_UV2","	attribute vec2 uv2;","#endif","#ifdef USE_UV3","	attribute vec2 uv3;","#endif","#ifdef USE_TANGENT","	attribute vec4 tangent;","#endif","#if defined( USE_COLOR_ALPHA )","	attribute vec4 color;","#elif defined( USE_COLOR )","	attribute vec3 color;","#endif","#ifdef USE_SKINNING","	attribute vec4 skinIndex;","	attribute vec4 skinWeight;","#endif",`
`].filter(Va).join(`
`),m=[Id(t),"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,g,t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.alphaToCoverage?"#define ALPHA_TO_COVERAGE":"",t.map?"#define USE_MAP":"",t.matcap?"#define USE_MATCAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+c:"",t.envMap?"#define "+h:"",t.envMap?"#define "+u:"",d?"#define CUBEUV_TEXEL_WIDTH "+d.texelWidth:"",d?"#define CUBEUV_TEXEL_HEIGHT "+d.texelHeight:"",d?"#define CUBEUV_MAX_MIP "+d.maxMip+".0":"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",t.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.anisotropy?"#define USE_ANISOTROPY":"",t.anisotropyMap?"#define USE_ANISOTROPYMAP":"",t.clearcoat?"#define USE_CLEARCOAT":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.dispersion?"#define USE_DISPERSION":"",t.iridescence?"#define USE_IRIDESCENCE":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",t.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaTest?"#define USE_ALPHATEST":"",t.alphaHash?"#define USE_ALPHAHASH":"",t.sheen?"#define USE_SHEEN":"",t.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.vertexTangents&&t.flatShading===!1?"#define USE_TANGENT":"",t.vertexColors||t.instancingColor||t.batchingColor?"#define USE_COLOR":"",t.vertexAlphas?"#define USE_COLOR_ALPHA":"",t.vertexUv1s?"#define USE_UV1":"",t.vertexUv2s?"#define USE_UV2":"",t.vertexUv3s?"#define USE_UV3":"",t.pointsUvs?"#define USE_POINTS_UV":"",t.gradientMap?"#define USE_GRADIENTMAP":"",t.flatShading?"#define FLAT_SHADED":"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+l:"",t.premultipliedAlpha?"#define PREMULTIPLIED_ALPHA":"",t.numLightProbes>0?"#define USE_LIGHT_PROBES":"",t.decodeVideoTexture?"#define DECODE_VIDEO_TEXTURE":"",t.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"","uniform mat4 viewMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;",t.toneMapping!==Ss?"#define TONE_MAPPING":"",t.toneMapping!==Ss?at.tonemapping_pars_fragment:"",t.toneMapping!==Ss?Py("toneMapping",t.toneMapping):"",t.dithering?"#define DITHERING":"",t.opaque?"#define OPAQUE":"",at.colorspace_pars_fragment,Ry("linearToOutputTexel",t.outputColorSpace),Ly(),t.useDepthPacking?"#define DEPTH_PACKING "+t.depthPacking:"",`
`].filter(Va).join(`
`)),a=Eh(a),a=Pd(a,t),a=Ld(a,t),o=Eh(o),o=Pd(o,t),o=Ld(o,t),a=Dd(a),o=Dd(o),t.isRawShaderMaterial!==!0&&(S=`#version 300 es
`,p=[f,"#define attribute in","#define varying out","#define texture2D texture"].join(`
`)+`
`+p,m=["#define varying in",t.glslVersion===Xu?"":"layout(location = 0) out highp vec4 pc_fragColor;",t.glslVersion===Xu?"":"#define gl_FragColor pc_fragColor","#define gl_FragDepthEXT gl_FragDepth","#define texture2D texture","#define textureCube texture","#define texture2DProj textureProj","#define texture2DLodEXT textureLod","#define texture2DProjLodEXT textureProjLod","#define textureCubeLodEXT textureLod","#define texture2DGradEXT textureGrad","#define texture2DProjGradEXT textureProjGrad","#define textureCubeGradEXT textureGrad"].join(`
`)+`
`+m);const _=S+p+a,b=S+m+o,I=Cd(s,s.VERTEX_SHADER,_),A=Cd(s,s.FRAGMENT_SHADER,b);s.attachShader(v,I),s.attachShader(v,A),t.index0AttributeName!==void 0?s.bindAttribLocation(v,0,t.index0AttributeName):t.morphTargets===!0&&s.bindAttribLocation(v,0,"position"),s.linkProgram(v);function R(P){if(i.debug.checkShaderErrors){const X=s.getProgramInfoLog(v).trim(),H=s.getShaderInfoLog(I).trim(),J=s.getShaderInfoLog(A).trim();let q=!0,ee=!0;if(s.getProgramParameter(v,s.LINK_STATUS)===!1)if(q=!1,typeof i.debug.onShaderError=="function")i.debug.onShaderError(s,v,I,A);else{const j=Rd(s,I,"vertex"),ne=Rd(s,A,"fragment");console.error("THREE.WebGLProgram: Shader Error "+s.getError()+" - VALIDATE_STATUS "+s.getProgramParameter(v,s.VALIDATE_STATUS)+`

Material Name: `+P.name+`
Material Type: `+P.type+`

Program Info Log: `+X+`
`+j+`
`+ne)}else X!==""?console.warn("THREE.WebGLProgram: Program Info Log:",X):(H===""||J==="")&&(ee=!1);ee&&(P.diagnostics={runnable:q,programLog:X,vertexShader:{log:H,prefix:p},fragmentShader:{log:J,prefix:m}})}s.deleteShader(I),s.deleteShader(A),N=new ol(s,v),w=Uy(s,v)}let N;this.getUniforms=function(){return N===void 0&&R(this),N};let w;this.getAttributes=function(){return w===void 0&&R(this),w};let y=t.rendererExtensionParallelShaderCompile===!1;return this.isReady=function(){return y===!1&&(y=s.getProgramParameter(v,Ey)),y},this.destroy=function(){n.releaseStatesOfProgram(this),s.deleteProgram(v),this.program=void 0},this.type=t.shaderType,this.name=t.shaderName,this.id=Ty++,this.cacheKey=e,this.usedTimes=1,this.program=v,this.vertexShader=I,this.fragmentShader=A,this}let qy=0;class Xy{constructor(){this.shaderCache=new Map,this.materialCache=new Map}update(e){const t=e.vertexShader,n=e.fragmentShader,s=this._getShaderStage(t),r=this._getShaderStage(n),a=this._getShaderCacheForMaterial(e);return a.has(s)===!1&&(a.add(s),s.usedTimes++),a.has(r)===!1&&(a.add(r),r.usedTimes++),this}remove(e){const t=this.materialCache.get(e);for(const n of t)n.usedTimes--,n.usedTimes===0&&this.shaderCache.delete(n.code);return this.materialCache.delete(e),this}getVertexShaderID(e){return this._getShaderStage(e.vertexShader).id}getFragmentShaderID(e){return this._getShaderStage(e.fragmentShader).id}dispose(){this.shaderCache.clear(),this.materialCache.clear()}_getShaderCacheForMaterial(e){const t=this.materialCache;let n=t.get(e);return n===void 0&&(n=new Set,t.set(e,n)),n}_getShaderStage(e){const t=this.shaderCache;let n=t.get(e);return n===void 0&&(n=new Yy(e),t.set(e,n)),n}}class Yy{constructor(e){this.id=qy++,this.code=e,this.usedTimes=0}}function jy(i,e,t,n,s,r,a){const o=new Jh,l=new Xy,c=new Set,h=[],u=s.logarithmicDepthBuffer,d=s.vertexTextures;let f=s.precision;const g={MeshDepthMaterial:"depth",MeshDistanceMaterial:"distanceRGBA",MeshNormalMaterial:"normal",MeshBasicMaterial:"basic",MeshLambertMaterial:"lambert",MeshPhongMaterial:"phong",MeshToonMaterial:"toon",MeshStandardMaterial:"physical",MeshPhysicalMaterial:"physical",MeshMatcapMaterial:"matcap",LineBasicMaterial:"basic",LineDashedMaterial:"dashed",PointsMaterial:"points",ShadowMaterial:"shadow",SpriteMaterial:"sprite"};function v(w){return c.add(w),w===0?"uv":`uv${w}`}function p(w,y,P,X,H){const J=X.fog,q=H.geometry,ee=w.isMeshStandardMaterial?X.environment:null,j=(w.isMeshStandardMaterial?t:e).get(w.envMap||ee),ne=j&&j.mapping===bl?j.image.height:null,ge=g[w.type];w.precision!==null&&(f=s.getMaxPrecision(w.precision),f!==w.precision&&console.warn("THREE.WebGLProgram.getParameters:",w.precision,"not supported, using",f,"instead."));const de=q.morphAttributes.position||q.morphAttributes.normal||q.morphAttributes.color,ye=de!==void 0?de.length:0;let Te=0;q.morphAttributes.position!==void 0&&(Te=1),q.morphAttributes.normal!==void 0&&(Te=2),q.morphAttributes.color!==void 0&&(Te=3);let Se,ie,he,be;if(ge){const ct=Ni[ge];Se=ct.vertexShader,ie=ct.fragmentShader}else Se=w.vertexShader,ie=w.fragmentShader,l.update(w),he=l.getVertexShaderID(w),be=l.getFragmentShaderID(w);const fe=i.getRenderTarget(),ze=H.isInstancedMesh===!0,We=H.isBatchedMesh===!0,Fe=!!w.map,mt=!!w.matcap,F=!!j,ft=!!w.aoMap,rt=!!w.lightMap,ht=!!w.bumpMap,ke=!!w.normalMap,Et=!!w.displacementMap,Ye=!!w.emissiveMap,qe=!!w.metalnessMap,U=!!w.roughnessMap,T=w.anisotropy>0,Q=w.clearcoat>0,le=w.dispersion>0,te=w.iridescence>0,$=w.sheen>0,Ee=w.transmission>0,ve=T&&!!w.anisotropyMap,Ce=Q&&!!w.clearcoatMap,Ze=Q&&!!w.clearcoatNormalMap,me=Q&&!!w.clearcoatRoughnessMap,Ae=te&&!!w.iridescenceMap,Qe=te&&!!w.iridescenceThicknessMap,He=$&&!!w.sheenColorMap,we=$&&!!w.sheenRoughnessMap,Ve=!!w.specularMap,B=!!w.specularColorMap,ce=!!w.specularIntensityMap,O=Ee&&!!w.transmissionMap,ae=Ee&&!!w.thicknessMap,se=!!w.gradientMap,re=!!w.alphaMap,_e=w.alphaTest>0,Je=!!w.alphaHash,lt=!!w.extensions;let xt=Ss;w.toneMapped&&(fe===null||fe.isXRRenderTarget===!0)&&(xt=i.toneMapping);const Tt={shaderID:ge,shaderType:w.type,shaderName:w.name,vertexShader:Se,fragmentShader:ie,defines:w.defines,customVertexShaderID:he,customFragmentShaderID:be,isRawShaderMaterial:w.isRawShaderMaterial===!0,glslVersion:w.glslVersion,precision:f,batching:We,batchingColor:We&&H._colorsTexture!==null,instancing:ze,instancingColor:ze&&H.instanceColor!==null,instancingMorph:ze&&H.morphTexture!==null,supportsVertexTextures:d,outputColorSpace:fe===null?i.outputColorSpace:fe.isXRRenderTarget===!0?fe.texture.colorSpace:Cs,alphaToCoverage:!!w.alphaToCoverage,map:Fe,matcap:mt,envMap:F,envMapMode:F&&j.mapping,envMapCubeUVHeight:ne,aoMap:ft,lightMap:rt,bumpMap:ht,normalMap:ke,displacementMap:d&&Et,emissiveMap:Ye,normalMapObjectSpace:ke&&w.normalMapType===Vg,normalMapTangentSpace:ke&&w.normalMapType===pp,metalnessMap:qe,roughnessMap:U,anisotropy:T,anisotropyMap:ve,clearcoat:Q,clearcoatMap:Ce,clearcoatNormalMap:Ze,clearcoatRoughnessMap:me,dispersion:le,iridescence:te,iridescenceMap:Ae,iridescenceThicknessMap:Qe,sheen:$,sheenColorMap:He,sheenRoughnessMap:we,specularMap:Ve,specularColorMap:B,specularIntensityMap:ce,transmission:Ee,transmissionMap:O,thicknessMap:ae,gradientMap:se,opaque:w.transparent===!1&&w.blending===$r&&w.alphaToCoverage===!1,alphaMap:re,alphaTest:_e,alphaHash:Je,combine:w.combine,mapUv:Fe&&v(w.map.channel),aoMapUv:ft&&v(w.aoMap.channel),lightMapUv:rt&&v(w.lightMap.channel),bumpMapUv:ht&&v(w.bumpMap.channel),normalMapUv:ke&&v(w.normalMap.channel),displacementMapUv:Et&&v(w.displacementMap.channel),emissiveMapUv:Ye&&v(w.emissiveMap.channel),metalnessMapUv:qe&&v(w.metalnessMap.channel),roughnessMapUv:U&&v(w.roughnessMap.channel),anisotropyMapUv:ve&&v(w.anisotropyMap.channel),clearcoatMapUv:Ce&&v(w.clearcoatMap.channel),clearcoatNormalMapUv:Ze&&v(w.clearcoatNormalMap.channel),clearcoatRoughnessMapUv:me&&v(w.clearcoatRoughnessMap.channel),iridescenceMapUv:Ae&&v(w.iridescenceMap.channel),iridescenceThicknessMapUv:Qe&&v(w.iridescenceThicknessMap.channel),sheenColorMapUv:He&&v(w.sheenColorMap.channel),sheenRoughnessMapUv:we&&v(w.sheenRoughnessMap.channel),specularMapUv:Ve&&v(w.specularMap.channel),specularColorMapUv:B&&v(w.specularColorMap.channel),specularIntensityMapUv:ce&&v(w.specularIntensityMap.channel),transmissionMapUv:O&&v(w.transmissionMap.channel),thicknessMapUv:ae&&v(w.thicknessMap.channel),alphaMapUv:re&&v(w.alphaMap.channel),vertexTangents:!!q.attributes.tangent&&(ke||T),vertexColors:w.vertexColors,vertexAlphas:w.vertexColors===!0&&!!q.attributes.color&&q.attributes.color.itemSize===4,pointsUvs:H.isPoints===!0&&!!q.attributes.uv&&(Fe||re),fog:!!J,useFog:w.fog===!0,fogExp2:!!J&&J.isFogExp2,flatShading:w.flatShading===!0,sizeAttenuation:w.sizeAttenuation===!0,logarithmicDepthBuffer:u,skinning:H.isSkinnedMesh===!0,morphTargets:q.morphAttributes.position!==void 0,morphNormals:q.morphAttributes.normal!==void 0,morphColors:q.morphAttributes.color!==void 0,morphTargetsCount:ye,morphTextureStride:Te,numDirLights:y.directional.length,numPointLights:y.point.length,numSpotLights:y.spot.length,numSpotLightMaps:y.spotLightMap.length,numRectAreaLights:y.rectArea.length,numHemiLights:y.hemi.length,numDirLightShadows:y.directionalShadowMap.length,numPointLightShadows:y.pointShadowMap.length,numSpotLightShadows:y.spotShadowMap.length,numSpotLightShadowsWithMaps:y.numSpotLightShadowsWithMaps,numLightProbes:y.numLightProbes,numClippingPlanes:a.numPlanes,numClipIntersection:a.numIntersection,dithering:w.dithering,shadowMapEnabled:i.shadowMap.enabled&&P.length>0,shadowMapType:i.shadowMap.type,toneMapping:xt,decodeVideoTexture:Fe&&w.map.isVideoTexture===!0&&wt.getTransfer(w.map.colorSpace)===Bt,premultipliedAlpha:w.premultipliedAlpha,doubleSided:w.side===Fn,flipSided:w.side===Vn,useDepthPacking:w.depthPacking>=0,depthPacking:w.depthPacking||0,index0AttributeName:w.index0AttributeName,extensionClipCullDistance:lt&&w.extensions.clipCullDistance===!0&&n.has("WEBGL_clip_cull_distance"),extensionMultiDraw:(lt&&w.extensions.multiDraw===!0||We)&&n.has("WEBGL_multi_draw"),rendererExtensionParallelShaderCompile:n.has("KHR_parallel_shader_compile"),customProgramCacheKey:w.customProgramCacheKey()};return Tt.vertexUv1s=c.has(1),Tt.vertexUv2s=c.has(2),Tt.vertexUv3s=c.has(3),c.clear(),Tt}function m(w){const y=[];if(w.shaderID?y.push(w.shaderID):(y.push(w.customVertexShaderID),y.push(w.customFragmentShaderID)),w.defines!==void 0)for(const P in w.defines)y.push(P),y.push(w.defines[P]);return w.isRawShaderMaterial===!1&&(S(y,w),_(y,w),y.push(i.outputColorSpace)),y.push(w.customProgramCacheKey),y.join()}function S(w,y){w.push(y.precision),w.push(y.outputColorSpace),w.push(y.envMapMode),w.push(y.envMapCubeUVHeight),w.push(y.mapUv),w.push(y.alphaMapUv),w.push(y.lightMapUv),w.push(y.aoMapUv),w.push(y.bumpMapUv),w.push(y.normalMapUv),w.push(y.displacementMapUv),w.push(y.emissiveMapUv),w.push(y.metalnessMapUv),w.push(y.roughnessMapUv),w.push(y.anisotropyMapUv),w.push(y.clearcoatMapUv),w.push(y.clearcoatNormalMapUv),w.push(y.clearcoatRoughnessMapUv),w.push(y.iridescenceMapUv),w.push(y.iridescenceThicknessMapUv),w.push(y.sheenColorMapUv),w.push(y.sheenRoughnessMapUv),w.push(y.specularMapUv),w.push(y.specularColorMapUv),w.push(y.specularIntensityMapUv),w.push(y.transmissionMapUv),w.push(y.thicknessMapUv),w.push(y.combine),w.push(y.fogExp2),w.push(y.sizeAttenuation),w.push(y.morphTargetsCount),w.push(y.morphAttributeCount),w.push(y.numDirLights),w.push(y.numPointLights),w.push(y.numSpotLights),w.push(y.numSpotLightMaps),w.push(y.numHemiLights),w.push(y.numRectAreaLights),w.push(y.numDirLightShadows),w.push(y.numPointLightShadows),w.push(y.numSpotLightShadows),w.push(y.numSpotLightShadowsWithMaps),w.push(y.numLightProbes),w.push(y.shadowMapType),w.push(y.toneMapping),w.push(y.numClippingPlanes),w.push(y.numClipIntersection),w.push(y.depthPacking)}function _(w,y){o.disableAll(),y.supportsVertexTextures&&o.enable(0),y.instancing&&o.enable(1),y.instancingColor&&o.enable(2),y.instancingMorph&&o.enable(3),y.matcap&&o.enable(4),y.envMap&&o.enable(5),y.normalMapObjectSpace&&o.enable(6),y.normalMapTangentSpace&&o.enable(7),y.clearcoat&&o.enable(8),y.iridescence&&o.enable(9),y.alphaTest&&o.enable(10),y.vertexColors&&o.enable(11),y.vertexAlphas&&o.enable(12),y.vertexUv1s&&o.enable(13),y.vertexUv2s&&o.enable(14),y.vertexUv3s&&o.enable(15),y.vertexTangents&&o.enable(16),y.anisotropy&&o.enable(17),y.alphaHash&&o.enable(18),y.batching&&o.enable(19),y.dispersion&&o.enable(20),y.batchingColor&&o.enable(21),w.push(o.mask),o.disableAll(),y.fog&&o.enable(0),y.useFog&&o.enable(1),y.flatShading&&o.enable(2),y.logarithmicDepthBuffer&&o.enable(3),y.skinning&&o.enable(4),y.morphTargets&&o.enable(5),y.morphNormals&&o.enable(6),y.morphColors&&o.enable(7),y.premultipliedAlpha&&o.enable(8),y.shadowMapEnabled&&o.enable(9),y.doubleSided&&o.enable(10),y.flipSided&&o.enable(11),y.useDepthPacking&&o.enable(12),y.dithering&&o.enable(13),y.transmission&&o.enable(14),y.sheen&&o.enable(15),y.opaque&&o.enable(16),y.pointsUvs&&o.enable(17),y.decodeVideoTexture&&o.enable(18),y.alphaToCoverage&&o.enable(19),w.push(o.mask)}function b(w){const y=g[w.type];let P;if(y){const X=Ni[y];P=Dv.clone(X.uniforms)}else P=w.uniforms;return P}function I(w,y){let P;for(let X=0,H=h.length;X<H;X++){const J=h[X];if(J.cacheKey===y){P=J,++P.usedTimes;break}}return P===void 0&&(P=new $y(i,y,w,r),h.push(P)),P}function A(w){if(--w.usedTimes===0){const y=h.indexOf(w);h[y]=h[h.length-1],h.pop(),w.destroy()}}function R(w){l.remove(w)}function N(){l.dispose()}return{getParameters:p,getProgramCacheKey:m,getUniforms:b,acquireProgram:I,releaseProgram:A,releaseShaderCache:R,programs:h,dispose:N}}function Ky(){let i=new WeakMap;function e(a){return i.has(a)}function t(a){let o=i.get(a);return o===void 0&&(o={},i.set(a,o)),o}function n(a){i.delete(a)}function s(a,o,l){i.get(a)[o]=l}function r(){i=new WeakMap}return{has:e,get:t,remove:n,update:s,dispose:r}}function Jy(i,e){return i.groupOrder!==e.groupOrder?i.groupOrder-e.groupOrder:i.renderOrder!==e.renderOrder?i.renderOrder-e.renderOrder:i.material.id!==e.material.id?i.material.id-e.material.id:i.z!==e.z?i.z-e.z:i.id-e.id}function Ud(i,e){return i.groupOrder!==e.groupOrder?i.groupOrder-e.groupOrder:i.renderOrder!==e.renderOrder?i.renderOrder-e.renderOrder:i.z!==e.z?e.z-i.z:i.id-e.id}function Nd(){const i=[];let e=0;const t=[],n=[],s=[];function r(){e=0,t.length=0,n.length=0,s.length=0}function a(u,d,f,g,v,p){let m=i[e];return m===void 0?(m={id:u.id,object:u,geometry:d,material:f,groupOrder:g,renderOrder:u.renderOrder,z:v,group:p},i[e]=m):(m.id=u.id,m.object=u,m.geometry=d,m.material=f,m.groupOrder=g,m.renderOrder=u.renderOrder,m.z=v,m.group=p),e++,m}function o(u,d,f,g,v,p){const m=a(u,d,f,g,v,p);f.transmission>0?n.push(m):f.transparent===!0?s.push(m):t.push(m)}function l(u,d,f,g,v,p){const m=a(u,d,f,g,v,p);f.transmission>0?n.unshift(m):f.transparent===!0?s.unshift(m):t.unshift(m)}function c(u,d){t.length>1&&t.sort(u||Jy),n.length>1&&n.sort(d||Ud),s.length>1&&s.sort(d||Ud)}function h(){for(let u=e,d=i.length;u<d;u++){const f=i[u];if(f.id===null)break;f.id=null,f.object=null,f.geometry=null,f.material=null,f.group=null}}return{opaque:t,transmissive:n,transparent:s,init:r,push:o,unshift:l,finish:h,sort:c}}function Zy(){let i=new WeakMap;function e(n,s){const r=i.get(n);let a;return r===void 0?(a=new Nd,i.set(n,[a])):s>=r.length?(a=new Nd,r.push(a)):a=r[s],a}function t(){i=new WeakMap}return{get:e,dispose:t}}function Qy(){const i={};return{get:function(e){if(i[e.id]!==void 0)return i[e.id];let t;switch(e.type){case"DirectionalLight":t={direction:new V,color:new it};break;case"SpotLight":t={position:new V,direction:new V,color:new it,distance:0,coneCos:0,penumbraCos:0,decay:0};break;case"PointLight":t={position:new V,color:new it,distance:0,decay:0};break;case"HemisphereLight":t={direction:new V,skyColor:new it,groundColor:new it};break;case"RectAreaLight":t={color:new it,position:new V,halfWidth:new V,halfHeight:new V};break}return i[e.id]=t,t}}}function eS(){const i={};return{get:function(e){if(i[e.id]!==void 0)return i[e.id];let t;switch(e.type){case"DirectionalLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new Xe};break;case"SpotLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new Xe};break;case"PointLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new Xe,shadowCameraNear:1,shadowCameraFar:1e3};break}return i[e.id]=t,t}}}let tS=0;function nS(i,e){return(e.castShadow?2:0)-(i.castShadow?2:0)+(e.map?1:0)-(i.map?1:0)}function iS(i){const e=new Qy,t=eS(),n={version:0,hash:{directionalLength:-1,pointLength:-1,spotLength:-1,rectAreaLength:-1,hemiLength:-1,numDirectionalShadows:-1,numPointShadows:-1,numSpotShadows:-1,numSpotMaps:-1,numLightProbes:-1},ambient:[0,0,0],probe:[],directional:[],directionalShadow:[],directionalShadowMap:[],directionalShadowMatrix:[],spot:[],spotLightMap:[],spotShadow:[],spotShadowMap:[],spotLightMatrix:[],rectArea:[],rectAreaLTC1:null,rectAreaLTC2:null,point:[],pointShadow:[],pointShadowMap:[],pointShadowMatrix:[],hemi:[],numSpotLightShadowsWithMaps:0,numLightProbes:0};for(let c=0;c<9;c++)n.probe.push(new V);const s=new V,r=new zt,a=new zt;function o(c){let h=0,u=0,d=0;for(let w=0;w<9;w++)n.probe[w].set(0,0,0);let f=0,g=0,v=0,p=0,m=0,S=0,_=0,b=0,I=0,A=0,R=0;c.sort(nS);for(let w=0,y=c.length;w<y;w++){const P=c[w],X=P.color,H=P.intensity,J=P.distance,q=P.shadow&&P.shadow.map?P.shadow.map.texture:null;if(P.isAmbientLight)h+=X.r*H,u+=X.g*H,d+=X.b*H;else if(P.isLightProbe){for(let ee=0;ee<9;ee++)n.probe[ee].addScaledVector(P.sh.coefficients[ee],H);R++}else if(P.isDirectionalLight){const ee=e.get(P);if(ee.color.copy(P.color).multiplyScalar(P.intensity),P.castShadow){const j=P.shadow,ne=t.get(P);ne.shadowIntensity=j.intensity,ne.shadowBias=j.bias,ne.shadowNormalBias=j.normalBias,ne.shadowRadius=j.radius,ne.shadowMapSize=j.mapSize,n.directionalShadow[f]=ne,n.directionalShadowMap[f]=q,n.directionalShadowMatrix[f]=P.shadow.matrix,S++}n.directional[f]=ee,f++}else if(P.isSpotLight){const ee=e.get(P);ee.position.setFromMatrixPosition(P.matrixWorld),ee.color.copy(X).multiplyScalar(H),ee.distance=J,ee.coneCos=Math.cos(P.angle),ee.penumbraCos=Math.cos(P.angle*(1-P.penumbra)),ee.decay=P.decay,n.spot[v]=ee;const j=P.shadow;if(P.map&&(n.spotLightMap[I]=P.map,I++,j.updateMatrices(P),P.castShadow&&A++),n.spotLightMatrix[v]=j.matrix,P.castShadow){const ne=t.get(P);ne.shadowIntensity=j.intensity,ne.shadowBias=j.bias,ne.shadowNormalBias=j.normalBias,ne.shadowRadius=j.radius,ne.shadowMapSize=j.mapSize,n.spotShadow[v]=ne,n.spotShadowMap[v]=q,b++}v++}else if(P.isRectAreaLight){const ee=e.get(P);ee.color.copy(X).multiplyScalar(H),ee.halfWidth.set(P.width*.5,0,0),ee.halfHeight.set(0,P.height*.5,0),n.rectArea[p]=ee,p++}else if(P.isPointLight){const ee=e.get(P);if(ee.color.copy(P.color).multiplyScalar(P.intensity),ee.distance=P.distance,ee.decay=P.decay,P.castShadow){const j=P.shadow,ne=t.get(P);ne.shadowIntensity=j.intensity,ne.shadowBias=j.bias,ne.shadowNormalBias=j.normalBias,ne.shadowRadius=j.radius,ne.shadowMapSize=j.mapSize,ne.shadowCameraNear=j.camera.near,ne.shadowCameraFar=j.camera.far,n.pointShadow[g]=ne,n.pointShadowMap[g]=q,n.pointShadowMatrix[g]=P.shadow.matrix,_++}n.point[g]=ee,g++}else if(P.isHemisphereLight){const ee=e.get(P);ee.skyColor.copy(P.color).multiplyScalar(H),ee.groundColor.copy(P.groundColor).multiplyScalar(H),n.hemi[m]=ee,m++}}p>0&&(i.has("OES_texture_float_linear")===!0?(n.rectAreaLTC1=Re.LTC_FLOAT_1,n.rectAreaLTC2=Re.LTC_FLOAT_2):(n.rectAreaLTC1=Re.LTC_HALF_1,n.rectAreaLTC2=Re.LTC_HALF_2)),n.ambient[0]=h,n.ambient[1]=u,n.ambient[2]=d;const N=n.hash;(N.directionalLength!==f||N.pointLength!==g||N.spotLength!==v||N.rectAreaLength!==p||N.hemiLength!==m||N.numDirectionalShadows!==S||N.numPointShadows!==_||N.numSpotShadows!==b||N.numSpotMaps!==I||N.numLightProbes!==R)&&(n.directional.length=f,n.spot.length=v,n.rectArea.length=p,n.point.length=g,n.hemi.length=m,n.directionalShadow.length=S,n.directionalShadowMap.length=S,n.pointShadow.length=_,n.pointShadowMap.length=_,n.spotShadow.length=b,n.spotShadowMap.length=b,n.directionalShadowMatrix.length=S,n.pointShadowMatrix.length=_,n.spotLightMatrix.length=b+I-A,n.spotLightMap.length=I,n.numSpotLightShadowsWithMaps=A,n.numLightProbes=R,N.directionalLength=f,N.pointLength=g,N.spotLength=v,N.rectAreaLength=p,N.hemiLength=m,N.numDirectionalShadows=S,N.numPointShadows=_,N.numSpotShadows=b,N.numSpotMaps=I,N.numLightProbes=R,n.version=tS++)}function l(c,h){let u=0,d=0,f=0,g=0,v=0;const p=h.matrixWorldInverse;for(let m=0,S=c.length;m<S;m++){const _=c[m];if(_.isDirectionalLight){const b=n.directional[u];b.direction.setFromMatrixPosition(_.matrixWorld),s.setFromMatrixPosition(_.target.matrixWorld),b.direction.sub(s),b.direction.transformDirection(p),u++}else if(_.isSpotLight){const b=n.spot[f];b.position.setFromMatrixPosition(_.matrixWorld),b.position.applyMatrix4(p),b.direction.setFromMatrixPosition(_.matrixWorld),s.setFromMatrixPosition(_.target.matrixWorld),b.direction.sub(s),b.direction.transformDirection(p),f++}else if(_.isRectAreaLight){const b=n.rectArea[g];b.position.setFromMatrixPosition(_.matrixWorld),b.position.applyMatrix4(p),a.identity(),r.copy(_.matrixWorld),r.premultiply(p),a.extractRotation(r),b.halfWidth.set(_.width*.5,0,0),b.halfHeight.set(0,_.height*.5,0),b.halfWidth.applyMatrix4(a),b.halfHeight.applyMatrix4(a),g++}else if(_.isPointLight){const b=n.point[d];b.position.setFromMatrixPosition(_.matrixWorld),b.position.applyMatrix4(p),d++}else if(_.isHemisphereLight){const b=n.hemi[v];b.direction.setFromMatrixPosition(_.matrixWorld),b.direction.transformDirection(p),v++}}}return{setup:o,setupView:l,state:n}}function Od(i){const e=new iS(i),t=[],n=[];function s(h){c.camera=h,t.length=0,n.length=0}function r(h){t.push(h)}function a(h){n.push(h)}function o(){e.setup(t)}function l(h){e.setupView(t,h)}const c={lightsArray:t,shadowsArray:n,camera:null,lights:e,transmissionRenderTarget:{}};return{init:s,state:c,setupLights:o,setupLightsView:l,pushLight:r,pushShadow:a}}function sS(i){let e=new WeakMap;function t(s,r=0){const a=e.get(s);let o;return a===void 0?(o=new Od(i),e.set(s,[o])):r>=a.length?(o=new Od(i),a.push(o)):o=a[r],o}function n(){e=new WeakMap}return{get:t,dispose:n}}class rS extends Rs{constructor(e){super(),this.isMeshDepthMaterial=!0,this.type="MeshDepthMaterial",this.depthPacking=zg,this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.wireframe=!1,this.wireframeLinewidth=1,this.setValues(e)}copy(e){return super.copy(e),this.depthPacking=e.depthPacking,this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this}}class aS extends Rs{constructor(e){super(),this.isMeshDistanceMaterial=!0,this.type="MeshDistanceMaterial",this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.setValues(e)}copy(e){return super.copy(e),this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this}}const oS=`void main() {
	gl_Position = vec4( position, 1.0 );
}`,lS=`uniform sampler2D shadow_pass;
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
}`;function cS(i,e,t){let n=new Zh;const s=new Xe,r=new Xe,a=new on,o=new rS({depthPacking:Hg}),l=new aS,c={},h=t.maxTextureSize,u={[Ms]:Vn,[Vn]:Ms,[Fn]:Fn},d=new ws({defines:{VSM_SAMPLES:8},uniforms:{shadow_pass:{value:null},resolution:{value:new Xe},radius:{value:4}},vertexShader:oS,fragmentShader:lS}),f=d.clone();f.defines.HORIZONTAL_PASS=1;const g=new Qt;g.setAttribute("position",new Mi(new Float32Array([-1,-1,.5,3,-1,.5,-1,3,.5]),3));const v=new jt(g,d),p=this;this.enabled=!1,this.autoUpdate=!0,this.needsUpdate=!1,this.type=Qf;let m=this.type;this.render=function(A,R,N){if(p.enabled===!1||p.autoUpdate===!1&&p.needsUpdate===!1||A.length===0)return;const w=i.getRenderTarget(),y=i.getActiveCubeFace(),P=i.getActiveMipmapLevel(),X=i.state;X.setBlending(ys),X.buffers.color.setClear(1,1,1,1),X.buffers.depth.setTest(!0),X.setScissorTest(!1);const H=m!==ji&&this.type===ji,J=m===ji&&this.type!==ji;for(let q=0,ee=A.length;q<ee;q++){const j=A[q],ne=j.shadow;if(ne===void 0){console.warn("THREE.WebGLShadowMap:",j,"has no shadow.");continue}if(ne.autoUpdate===!1&&ne.needsUpdate===!1)continue;s.copy(ne.mapSize);const ge=ne.getFrameExtents();if(s.multiply(ge),r.copy(ne.mapSize),(s.x>h||s.y>h)&&(s.x>h&&(r.x=Math.floor(h/ge.x),s.x=r.x*ge.x,ne.mapSize.x=r.x),s.y>h&&(r.y=Math.floor(h/ge.y),s.y=r.y*ge.y,ne.mapSize.y=r.y)),ne.map===null||H===!0||J===!0){const ye=this.type!==ji?{minFilter:ai,magFilter:ai}:{};ne.map!==null&&ne.map.dispose(),ne.map=new Qs(s.x,s.y,ye),ne.map.texture.name=j.name+".shadowMap",ne.camera.updateProjectionMatrix()}i.setRenderTarget(ne.map),i.clear();const de=ne.getViewportCount();for(let ye=0;ye<de;ye++){const Te=ne.getViewport(ye);a.set(r.x*Te.x,r.y*Te.y,r.x*Te.z,r.y*Te.w),X.viewport(a),ne.updateMatrices(j,ye),n=ne.getFrustum(),b(R,N,ne.camera,j,this.type)}ne.isPointLightShadow!==!0&&this.type===ji&&S(ne,N),ne.needsUpdate=!1}m=this.type,p.needsUpdate=!1,i.setRenderTarget(w,y,P)};function S(A,R){const N=e.update(v);d.defines.VSM_SAMPLES!==A.blurSamples&&(d.defines.VSM_SAMPLES=A.blurSamples,f.defines.VSM_SAMPLES=A.blurSamples,d.needsUpdate=!0,f.needsUpdate=!0),A.mapPass===null&&(A.mapPass=new Qs(s.x,s.y)),d.uniforms.shadow_pass.value=A.map.texture,d.uniforms.resolution.value=A.mapSize,d.uniforms.radius.value=A.radius,i.setRenderTarget(A.mapPass),i.clear(),i.renderBufferDirect(R,null,N,d,v,null),f.uniforms.shadow_pass.value=A.mapPass.texture,f.uniforms.resolution.value=A.mapSize,f.uniforms.radius.value=A.radius,i.setRenderTarget(A.map),i.clear(),i.renderBufferDirect(R,null,N,f,v,null)}function _(A,R,N,w){let y=null;const P=N.isPointLight===!0?A.customDistanceMaterial:A.customDepthMaterial;if(P!==void 0)y=P;else if(y=N.isPointLight===!0?l:o,i.localClippingEnabled&&R.clipShadows===!0&&Array.isArray(R.clippingPlanes)&&R.clippingPlanes.length!==0||R.displacementMap&&R.displacementScale!==0||R.alphaMap&&R.alphaTest>0||R.map&&R.alphaTest>0){const X=y.uuid,H=R.uuid;let J=c[X];J===void 0&&(J={},c[X]=J);let q=J[H];q===void 0&&(q=y.clone(),J[H]=q,R.addEventListener("dispose",I)),y=q}if(y.visible=R.visible,y.wireframe=R.wireframe,w===ji?y.side=R.shadowSide!==null?R.shadowSide:R.side:y.side=R.shadowSide!==null?R.shadowSide:u[R.side],y.alphaMap=R.alphaMap,y.alphaTest=R.alphaTest,y.map=R.map,y.clipShadows=R.clipShadows,y.clippingPlanes=R.clippingPlanes,y.clipIntersection=R.clipIntersection,y.displacementMap=R.displacementMap,y.displacementScale=R.displacementScale,y.displacementBias=R.displacementBias,y.wireframeLinewidth=R.wireframeLinewidth,y.linewidth=R.linewidth,N.isPointLight===!0&&y.isMeshDistanceMaterial===!0){const X=i.properties.get(y);X.light=N}return y}function b(A,R,N,w,y){if(A.visible===!1)return;if(A.layers.test(R.layers)&&(A.isMesh||A.isLine||A.isPoints)&&(A.castShadow||A.receiveShadow&&y===ji)&&(!A.frustumCulled||n.intersectsObject(A))){A.modelViewMatrix.multiplyMatrices(N.matrixWorldInverse,A.matrixWorld);const H=e.update(A),J=A.material;if(Array.isArray(J)){const q=H.groups;for(let ee=0,j=q.length;ee<j;ee++){const ne=q[ee],ge=J[ne.materialIndex];if(ge&&ge.visible){const de=_(A,ge,w,y);A.onBeforeShadow(i,A,R,N,H,de,ne),i.renderBufferDirect(N,null,H,de,A,ne),A.onAfterShadow(i,A,R,N,H,de,ne)}}}else if(J.visible){const q=_(A,J,w,y);A.onBeforeShadow(i,A,R,N,H,q,null),i.renderBufferDirect(N,null,H,q,A,null),A.onAfterShadow(i,A,R,N,H,q,null)}}const X=A.children;for(let H=0,J=X.length;H<J;H++)b(X[H],R,N,w,y)}function I(A){A.target.removeEventListener("dispose",I);for(const N in c){const w=c[N],y=A.target.uuid;y in w&&(w[y].dispose(),delete w[y])}}}function hS(i){function e(){let O=!1;const ae=new on;let se=null;const re=new on(0,0,0,0);return{setMask:function(_e){se!==_e&&!O&&(i.colorMask(_e,_e,_e,_e),se=_e)},setLocked:function(_e){O=_e},setClear:function(_e,Je,lt,xt,Tt){Tt===!0&&(_e*=xt,Je*=xt,lt*=xt),ae.set(_e,Je,lt,xt),re.equals(ae)===!1&&(i.clearColor(_e,Je,lt,xt),re.copy(ae))},reset:function(){O=!1,se=null,re.set(-1,0,0,0)}}}function t(){let O=!1,ae=null,se=null,re=null;return{setTest:function(_e){_e?be(i.DEPTH_TEST):fe(i.DEPTH_TEST)},setMask:function(_e){ae!==_e&&!O&&(i.depthMask(_e),ae=_e)},setFunc:function(_e){if(se!==_e){switch(_e){case wg:i.depthFunc(i.NEVER);break;case Eg:i.depthFunc(i.ALWAYS);break;case Tg:i.depthFunc(i.LESS);break;case cl:i.depthFunc(i.LEQUAL);break;case Ag:i.depthFunc(i.EQUAL);break;case Cg:i.depthFunc(i.GEQUAL);break;case Rg:i.depthFunc(i.GREATER);break;case Pg:i.depthFunc(i.NOTEQUAL);break;default:i.depthFunc(i.LEQUAL)}se=_e}},setLocked:function(_e){O=_e},setClear:function(_e){re!==_e&&(i.clearDepth(_e),re=_e)},reset:function(){O=!1,ae=null,se=null,re=null}}}function n(){let O=!1,ae=null,se=null,re=null,_e=null,Je=null,lt=null,xt=null,Tt=null;return{setTest:function(ct){O||(ct?be(i.STENCIL_TEST):fe(i.STENCIL_TEST))},setMask:function(ct){ae!==ct&&!O&&(i.stencilMask(ct),ae=ct)},setFunc:function(ct,yn,Ht){(se!==ct||re!==yn||_e!==Ht)&&(i.stencilFunc(ct,yn,Ht),se=ct,re=yn,_e=Ht)},setOp:function(ct,yn,Ht){(Je!==ct||lt!==yn||xt!==Ht)&&(i.stencilOp(ct,yn,Ht),Je=ct,lt=yn,xt=Ht)},setLocked:function(ct){O=ct},setClear:function(ct){Tt!==ct&&(i.clearStencil(ct),Tt=ct)},reset:function(){O=!1,ae=null,se=null,re=null,_e=null,Je=null,lt=null,xt=null,Tt=null}}}const s=new e,r=new t,a=new n,o=new WeakMap,l=new WeakMap;let c={},h={},u=new WeakMap,d=[],f=null,g=!1,v=null,p=null,m=null,S=null,_=null,b=null,I=null,A=new it(0,0,0),R=0,N=!1,w=null,y=null,P=null,X=null,H=null;const J=i.getParameter(i.MAX_COMBINED_TEXTURE_IMAGE_UNITS);let q=!1,ee=0;const j=i.getParameter(i.VERSION);j.indexOf("WebGL")!==-1?(ee=parseFloat(/^WebGL (\d)/.exec(j)[1]),q=ee>=1):j.indexOf("OpenGL ES")!==-1&&(ee=parseFloat(/^OpenGL ES (\d)/.exec(j)[1]),q=ee>=2);let ne=null,ge={};const de=i.getParameter(i.SCISSOR_BOX),ye=i.getParameter(i.VIEWPORT),Te=new on().fromArray(de),Se=new on().fromArray(ye);function ie(O,ae,se,re){const _e=new Uint8Array(4),Je=i.createTexture();i.bindTexture(O,Je),i.texParameteri(O,i.TEXTURE_MIN_FILTER,i.NEAREST),i.texParameteri(O,i.TEXTURE_MAG_FILTER,i.NEAREST);for(let lt=0;lt<se;lt++)O===i.TEXTURE_3D||O===i.TEXTURE_2D_ARRAY?i.texImage3D(ae,0,i.RGBA,1,1,re,0,i.RGBA,i.UNSIGNED_BYTE,_e):i.texImage2D(ae+lt,0,i.RGBA,1,1,0,i.RGBA,i.UNSIGNED_BYTE,_e);return Je}const he={};he[i.TEXTURE_2D]=ie(i.TEXTURE_2D,i.TEXTURE_2D,1),he[i.TEXTURE_CUBE_MAP]=ie(i.TEXTURE_CUBE_MAP,i.TEXTURE_CUBE_MAP_POSITIVE_X,6),he[i.TEXTURE_2D_ARRAY]=ie(i.TEXTURE_2D_ARRAY,i.TEXTURE_2D_ARRAY,1,1),he[i.TEXTURE_3D]=ie(i.TEXTURE_3D,i.TEXTURE_3D,1,1),s.setClear(0,0,0,1),r.setClear(1),a.setClear(0),be(i.DEPTH_TEST),r.setFunc(cl),ht(!1),ke(Vu),be(i.CULL_FACE),ft(ys);function be(O){c[O]!==!0&&(i.enable(O),c[O]=!0)}function fe(O){c[O]!==!1&&(i.disable(O),c[O]=!1)}function ze(O,ae){return h[O]!==ae?(i.bindFramebuffer(O,ae),h[O]=ae,O===i.DRAW_FRAMEBUFFER&&(h[i.FRAMEBUFFER]=ae),O===i.FRAMEBUFFER&&(h[i.DRAW_FRAMEBUFFER]=ae),!0):!1}function We(O,ae){let se=d,re=!1;if(O){se=u.get(ae),se===void 0&&(se=[],u.set(ae,se));const _e=O.textures;if(se.length!==_e.length||se[0]!==i.COLOR_ATTACHMENT0){for(let Je=0,lt=_e.length;Je<lt;Je++)se[Je]=i.COLOR_ATTACHMENT0+Je;se.length=_e.length,re=!0}}else se[0]!==i.BACK&&(se[0]=i.BACK,re=!0);re&&i.drawBuffers(se)}function Fe(O){return f!==O?(i.useProgram(O),f=O,!0):!1}const mt={[$s]:i.FUNC_ADD,[og]:i.FUNC_SUBTRACT,[lg]:i.FUNC_REVERSE_SUBTRACT};mt[cg]=i.MIN,mt[hg]=i.MAX;const F={[ug]:i.ZERO,[dg]:i.ONE,[fg]:i.SRC_COLOR,[qc]:i.SRC_ALPHA,[_g]:i.SRC_ALPHA_SATURATE,[vg]:i.DST_COLOR,[mg]:i.DST_ALPHA,[pg]:i.ONE_MINUS_SRC_COLOR,[Xc]:i.ONE_MINUS_SRC_ALPHA,[xg]:i.ONE_MINUS_DST_COLOR,[gg]:i.ONE_MINUS_DST_ALPHA,[yg]:i.CONSTANT_COLOR,[Sg]:i.ONE_MINUS_CONSTANT_COLOR,[bg]:i.CONSTANT_ALPHA,[Mg]:i.ONE_MINUS_CONSTANT_ALPHA};function ft(O,ae,se,re,_e,Je,lt,xt,Tt,ct){if(O===ys){g===!0&&(fe(i.BLEND),g=!1);return}if(g===!1&&(be(i.BLEND),g=!0),O!==ag){if(O!==v||ct!==N){if((p!==$s||_!==$s)&&(i.blendEquation(i.FUNC_ADD),p=$s,_=$s),ct)switch(O){case $r:i.blendFuncSeparate(i.ONE,i.ONE_MINUS_SRC_ALPHA,i.ONE,i.ONE_MINUS_SRC_ALPHA);break;case Gu:i.blendFunc(i.ONE,i.ONE);break;case Wu:i.blendFuncSeparate(i.ZERO,i.ONE_MINUS_SRC_COLOR,i.ZERO,i.ONE);break;case $u:i.blendFuncSeparate(i.ZERO,i.SRC_COLOR,i.ZERO,i.SRC_ALPHA);break;default:console.error("THREE.WebGLState: Invalid blending: ",O);break}else switch(O){case $r:i.blendFuncSeparate(i.SRC_ALPHA,i.ONE_MINUS_SRC_ALPHA,i.ONE,i.ONE_MINUS_SRC_ALPHA);break;case Gu:i.blendFunc(i.SRC_ALPHA,i.ONE);break;case Wu:i.blendFuncSeparate(i.ZERO,i.ONE_MINUS_SRC_COLOR,i.ZERO,i.ONE);break;case $u:i.blendFunc(i.ZERO,i.SRC_COLOR);break;default:console.error("THREE.WebGLState: Invalid blending: ",O);break}m=null,S=null,b=null,I=null,A.set(0,0,0),R=0,v=O,N=ct}return}_e=_e||ae,Je=Je||se,lt=lt||re,(ae!==p||_e!==_)&&(i.blendEquationSeparate(mt[ae],mt[_e]),p=ae,_=_e),(se!==m||re!==S||Je!==b||lt!==I)&&(i.blendFuncSeparate(F[se],F[re],F[Je],F[lt]),m=se,S=re,b=Je,I=lt),(xt.equals(A)===!1||Tt!==R)&&(i.blendColor(xt.r,xt.g,xt.b,Tt),A.copy(xt),R=Tt),v=O,N=!1}function rt(O,ae){O.side===Fn?fe(i.CULL_FACE):be(i.CULL_FACE);let se=O.side===Vn;ae&&(se=!se),ht(se),O.blending===$r&&O.transparent===!1?ft(ys):ft(O.blending,O.blendEquation,O.blendSrc,O.blendDst,O.blendEquationAlpha,O.blendSrcAlpha,O.blendDstAlpha,O.blendColor,O.blendAlpha,O.premultipliedAlpha),r.setFunc(O.depthFunc),r.setTest(O.depthTest),r.setMask(O.depthWrite),s.setMask(O.colorWrite);const re=O.stencilWrite;a.setTest(re),re&&(a.setMask(O.stencilWriteMask),a.setFunc(O.stencilFunc,O.stencilRef,O.stencilFuncMask),a.setOp(O.stencilFail,O.stencilZFail,O.stencilZPass)),Ye(O.polygonOffset,O.polygonOffsetFactor,O.polygonOffsetUnits),O.alphaToCoverage===!0?be(i.SAMPLE_ALPHA_TO_COVERAGE):fe(i.SAMPLE_ALPHA_TO_COVERAGE)}function ht(O){w!==O&&(O?i.frontFace(i.CW):i.frontFace(i.CCW),w=O)}function ke(O){O!==sg?(be(i.CULL_FACE),O!==y&&(O===Vu?i.cullFace(i.BACK):O===rg?i.cullFace(i.FRONT):i.cullFace(i.FRONT_AND_BACK))):fe(i.CULL_FACE),y=O}function Et(O){O!==P&&(q&&i.lineWidth(O),P=O)}function Ye(O,ae,se){O?(be(i.POLYGON_OFFSET_FILL),(X!==ae||H!==se)&&(i.polygonOffset(ae,se),X=ae,H=se)):fe(i.POLYGON_OFFSET_FILL)}function qe(O){O?be(i.SCISSOR_TEST):fe(i.SCISSOR_TEST)}function U(O){O===void 0&&(O=i.TEXTURE0+J-1),ne!==O&&(i.activeTexture(O),ne=O)}function T(O,ae,se){se===void 0&&(ne===null?se=i.TEXTURE0+J-1:se=ne);let re=ge[se];re===void 0&&(re={type:void 0,texture:void 0},ge[se]=re),(re.type!==O||re.texture!==ae)&&(ne!==se&&(i.activeTexture(se),ne=se),i.bindTexture(O,ae||he[O]),re.type=O,re.texture=ae)}function Q(){const O=ge[ne];O!==void 0&&O.type!==void 0&&(i.bindTexture(O.type,null),O.type=void 0,O.texture=void 0)}function le(){try{i.compressedTexImage2D.apply(i,arguments)}catch(O){console.error("THREE.WebGLState:",O)}}function te(){try{i.compressedTexImage3D.apply(i,arguments)}catch(O){console.error("THREE.WebGLState:",O)}}function $(){try{i.texSubImage2D.apply(i,arguments)}catch(O){console.error("THREE.WebGLState:",O)}}function Ee(){try{i.texSubImage3D.apply(i,arguments)}catch(O){console.error("THREE.WebGLState:",O)}}function ve(){try{i.compressedTexSubImage2D.apply(i,arguments)}catch(O){console.error("THREE.WebGLState:",O)}}function Ce(){try{i.compressedTexSubImage3D.apply(i,arguments)}catch(O){console.error("THREE.WebGLState:",O)}}function Ze(){try{i.texStorage2D.apply(i,arguments)}catch(O){console.error("THREE.WebGLState:",O)}}function me(){try{i.texStorage3D.apply(i,arguments)}catch(O){console.error("THREE.WebGLState:",O)}}function Ae(){try{i.texImage2D.apply(i,arguments)}catch(O){console.error("THREE.WebGLState:",O)}}function Qe(){try{i.texImage3D.apply(i,arguments)}catch(O){console.error("THREE.WebGLState:",O)}}function He(O){Te.equals(O)===!1&&(i.scissor(O.x,O.y,O.z,O.w),Te.copy(O))}function we(O){Se.equals(O)===!1&&(i.viewport(O.x,O.y,O.z,O.w),Se.copy(O))}function Ve(O,ae){let se=l.get(ae);se===void 0&&(se=new WeakMap,l.set(ae,se));let re=se.get(O);re===void 0&&(re=i.getUniformBlockIndex(ae,O.name),se.set(O,re))}function B(O,ae){const re=l.get(ae).get(O);o.get(ae)!==re&&(i.uniformBlockBinding(ae,re,O.__bindingPointIndex),o.set(ae,re))}function ce(){i.disable(i.BLEND),i.disable(i.CULL_FACE),i.disable(i.DEPTH_TEST),i.disable(i.POLYGON_OFFSET_FILL),i.disable(i.SCISSOR_TEST),i.disable(i.STENCIL_TEST),i.disable(i.SAMPLE_ALPHA_TO_COVERAGE),i.blendEquation(i.FUNC_ADD),i.blendFunc(i.ONE,i.ZERO),i.blendFuncSeparate(i.ONE,i.ZERO,i.ONE,i.ZERO),i.blendColor(0,0,0,0),i.colorMask(!0,!0,!0,!0),i.clearColor(0,0,0,0),i.depthMask(!0),i.depthFunc(i.LESS),i.clearDepth(1),i.stencilMask(4294967295),i.stencilFunc(i.ALWAYS,0,4294967295),i.stencilOp(i.KEEP,i.KEEP,i.KEEP),i.clearStencil(0),i.cullFace(i.BACK),i.frontFace(i.CCW),i.polygonOffset(0,0),i.activeTexture(i.TEXTURE0),i.bindFramebuffer(i.FRAMEBUFFER,null),i.bindFramebuffer(i.DRAW_FRAMEBUFFER,null),i.bindFramebuffer(i.READ_FRAMEBUFFER,null),i.useProgram(null),i.lineWidth(1),i.scissor(0,0,i.canvas.width,i.canvas.height),i.viewport(0,0,i.canvas.width,i.canvas.height),c={},ne=null,ge={},h={},u=new WeakMap,d=[],f=null,g=!1,v=null,p=null,m=null,S=null,_=null,b=null,I=null,A=new it(0,0,0),R=0,N=!1,w=null,y=null,P=null,X=null,H=null,Te.set(0,0,i.canvas.width,i.canvas.height),Se.set(0,0,i.canvas.width,i.canvas.height),s.reset(),r.reset(),a.reset()}return{buffers:{color:s,depth:r,stencil:a},enable:be,disable:fe,bindFramebuffer:ze,drawBuffers:We,useProgram:Fe,setBlending:ft,setMaterial:rt,setFlipSided:ht,setCullFace:ke,setLineWidth:Et,setPolygonOffset:Ye,setScissorTest:qe,activeTexture:U,bindTexture:T,unbindTexture:Q,compressedTexImage2D:le,compressedTexImage3D:te,texImage2D:Ae,texImage3D:Qe,updateUBOMapping:Ve,uniformBlockBinding:B,texStorage2D:Ze,texStorage3D:me,texSubImage2D:$,texSubImage3D:Ee,compressedTexSubImage2D:ve,compressedTexSubImage3D:Ce,scissor:He,viewport:we,reset:ce}}function Fd(i,e,t,n){const s=uS(n);switch(t){case op:return i*e;case cp:return i*e;case hp:return i*e*2;case up:return i*e/s.components*s.byteLength;case qh:return i*e/s.components*s.byteLength;case dp:return i*e*2/s.components*s.byteLength;case Xh:return i*e*2/s.components*s.byteLength;case lp:return i*e*3/s.components*s.byteLength;case yi:return i*e*4/s.components*s.byteLength;case Yh:return i*e*4/s.components*s.byteLength;case nl:case il:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*8;case sl:case rl:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*16;case Qc:case th:return Math.max(i,16)*Math.max(e,8)/4;case Zc:case eh:return Math.max(i,8)*Math.max(e,8)/2;case nh:case ih:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*8;case sh:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*16;case rh:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*16;case ah:return Math.floor((i+4)/5)*Math.floor((e+3)/4)*16;case oh:return Math.floor((i+4)/5)*Math.floor((e+4)/5)*16;case lh:return Math.floor((i+5)/6)*Math.floor((e+4)/5)*16;case ch:return Math.floor((i+5)/6)*Math.floor((e+5)/6)*16;case hh:return Math.floor((i+7)/8)*Math.floor((e+4)/5)*16;case uh:return Math.floor((i+7)/8)*Math.floor((e+5)/6)*16;case dh:return Math.floor((i+7)/8)*Math.floor((e+7)/8)*16;case fh:return Math.floor((i+9)/10)*Math.floor((e+4)/5)*16;case ph:return Math.floor((i+9)/10)*Math.floor((e+5)/6)*16;case mh:return Math.floor((i+9)/10)*Math.floor((e+7)/8)*16;case gh:return Math.floor((i+9)/10)*Math.floor((e+9)/10)*16;case vh:return Math.floor((i+11)/12)*Math.floor((e+9)/10)*16;case xh:return Math.floor((i+11)/12)*Math.floor((e+11)/12)*16;case al:case _h:case yh:return Math.ceil(i/4)*Math.ceil(e/4)*16;case fp:case Sh:return Math.ceil(i/4)*Math.ceil(e/4)*8;case bh:case Mh:return Math.ceil(i/4)*Math.ceil(e/4)*16}throw new Error(`Unable to determine texture byte length for ${t} format.`)}function uS(i){switch(i){case ss:case sp:return{byteLength:1,components:1};case Za:case rp:case so:return{byteLength:2,components:1};case Wh:case $h:return{byteLength:2,components:4};case Zs:case Gh:case Ji:return{byteLength:4,components:1};case ap:return{byteLength:4,components:3}}throw new Error(`Unknown texture type ${i}.`)}function dS(i,e,t,n,s,r,a){const o=e.has("WEBGL_multisampled_render_to_texture")?e.get("WEBGL_multisampled_render_to_texture"):null,l=typeof navigator>"u"?!1:/OculusBrowser/g.test(navigator.userAgent),c=new Xe,h=new WeakMap;let u;const d=new WeakMap;let f=!1;try{f=typeof OffscreenCanvas<"u"&&new OffscreenCanvas(1,1).getContext("2d")!==null}catch{}function g(U,T){return f?new OffscreenCanvas(U,T):pl("canvas")}function v(U,T,Q){let le=1;const te=qe(U);if((te.width>Q||te.height>Q)&&(le=Q/Math.max(te.width,te.height)),le<1)if(typeof HTMLImageElement<"u"&&U instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&U instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&U instanceof ImageBitmap||typeof VideoFrame<"u"&&U instanceof VideoFrame){const $=Math.floor(le*te.width),Ee=Math.floor(le*te.height);u===void 0&&(u=g($,Ee));const ve=T?g($,Ee):u;return ve.width=$,ve.height=Ee,ve.getContext("2d").drawImage(U,0,0,$,Ee),console.warn("THREE.WebGLRenderer: Texture has been resized from ("+te.width+"x"+te.height+") to ("+$+"x"+Ee+")."),ve}else return"data"in U&&console.warn("THREE.WebGLRenderer: Image in DataTexture is too big ("+te.width+"x"+te.height+")."),U;return U}function p(U){return U.generateMipmaps&&U.minFilter!==ai&&U.minFilter!==vi}function m(U){i.generateMipmap(U)}function S(U,T,Q,le,te=!1){if(U!==null){if(i[U]!==void 0)return i[U];console.warn("THREE.WebGLRenderer: Attempt to use non-existing WebGL internal format '"+U+"'")}let $=T;if(T===i.RED&&(Q===i.FLOAT&&($=i.R32F),Q===i.HALF_FLOAT&&($=i.R16F),Q===i.UNSIGNED_BYTE&&($=i.R8)),T===i.RED_INTEGER&&(Q===i.UNSIGNED_BYTE&&($=i.R8UI),Q===i.UNSIGNED_SHORT&&($=i.R16UI),Q===i.UNSIGNED_INT&&($=i.R32UI),Q===i.BYTE&&($=i.R8I),Q===i.SHORT&&($=i.R16I),Q===i.INT&&($=i.R32I)),T===i.RG&&(Q===i.FLOAT&&($=i.RG32F),Q===i.HALF_FLOAT&&($=i.RG16F),Q===i.UNSIGNED_BYTE&&($=i.RG8)),T===i.RG_INTEGER&&(Q===i.UNSIGNED_BYTE&&($=i.RG8UI),Q===i.UNSIGNED_SHORT&&($=i.RG16UI),Q===i.UNSIGNED_INT&&($=i.RG32UI),Q===i.BYTE&&($=i.RG8I),Q===i.SHORT&&($=i.RG16I),Q===i.INT&&($=i.RG32I)),T===i.RGB&&Q===i.UNSIGNED_INT_5_9_9_9_REV&&($=i.RGB9_E5),T===i.RGBA){const Ee=te?hl:wt.getTransfer(le);Q===i.FLOAT&&($=i.RGBA32F),Q===i.HALF_FLOAT&&($=i.RGBA16F),Q===i.UNSIGNED_BYTE&&($=Ee===Bt?i.SRGB8_ALPHA8:i.RGBA8),Q===i.UNSIGNED_SHORT_4_4_4_4&&($=i.RGBA4),Q===i.UNSIGNED_SHORT_5_5_5_1&&($=i.RGB5_A1)}return($===i.R16F||$===i.R32F||$===i.RG16F||$===i.RG32F||$===i.RGBA16F||$===i.RGBA32F)&&e.get("EXT_color_buffer_float"),$}function _(U,T){let Q;return U?T===null||T===Zs||T===ta?Q=i.DEPTH24_STENCIL8:T===Ji?Q=i.DEPTH32F_STENCIL8:T===Za&&(Q=i.DEPTH24_STENCIL8,console.warn("DepthTexture: 16 bit depth attachment is not supported with stencil. Using 24-bit attachment.")):T===null||T===Zs||T===ta?Q=i.DEPTH_COMPONENT24:T===Ji?Q=i.DEPTH_COMPONENT32F:T===Za&&(Q=i.DEPTH_COMPONENT16),Q}function b(U,T){return p(U)===!0||U.isFramebufferTexture&&U.minFilter!==ai&&U.minFilter!==vi?Math.log2(Math.max(T.width,T.height))+1:U.mipmaps!==void 0&&U.mipmaps.length>0?U.mipmaps.length:U.isCompressedTexture&&Array.isArray(U.image)?T.mipmaps.length:1}function I(U){const T=U.target;T.removeEventListener("dispose",I),R(T),T.isVideoTexture&&h.delete(T)}function A(U){const T=U.target;T.removeEventListener("dispose",A),w(T)}function R(U){const T=n.get(U);if(T.__webglInit===void 0)return;const Q=U.source,le=d.get(Q);if(le){const te=le[T.__cacheKey];te.usedTimes--,te.usedTimes===0&&N(U),Object.keys(le).length===0&&d.delete(Q)}n.remove(U)}function N(U){const T=n.get(U);i.deleteTexture(T.__webglTexture);const Q=U.source,le=d.get(Q);delete le[T.__cacheKey],a.memory.textures--}function w(U){const T=n.get(U);if(U.depthTexture&&U.depthTexture.dispose(),U.isWebGLCubeRenderTarget)for(let le=0;le<6;le++){if(Array.isArray(T.__webglFramebuffer[le]))for(let te=0;te<T.__webglFramebuffer[le].length;te++)i.deleteFramebuffer(T.__webglFramebuffer[le][te]);else i.deleteFramebuffer(T.__webglFramebuffer[le]);T.__webglDepthbuffer&&i.deleteRenderbuffer(T.__webglDepthbuffer[le])}else{if(Array.isArray(T.__webglFramebuffer))for(let le=0;le<T.__webglFramebuffer.length;le++)i.deleteFramebuffer(T.__webglFramebuffer[le]);else i.deleteFramebuffer(T.__webglFramebuffer);if(T.__webglDepthbuffer&&i.deleteRenderbuffer(T.__webglDepthbuffer),T.__webglMultisampledFramebuffer&&i.deleteFramebuffer(T.__webglMultisampledFramebuffer),T.__webglColorRenderbuffer)for(let le=0;le<T.__webglColorRenderbuffer.length;le++)T.__webglColorRenderbuffer[le]&&i.deleteRenderbuffer(T.__webglColorRenderbuffer[le]);T.__webglDepthRenderbuffer&&i.deleteRenderbuffer(T.__webglDepthRenderbuffer)}const Q=U.textures;for(let le=0,te=Q.length;le<te;le++){const $=n.get(Q[le]);$.__webglTexture&&(i.deleteTexture($.__webglTexture),a.memory.textures--),n.remove(Q[le])}n.remove(U)}let y=0;function P(){y=0}function X(){const U=y;return U>=s.maxTextures&&console.warn("THREE.WebGLTextures: Trying to use "+U+" texture units while this GPU supports only "+s.maxTextures),y+=1,U}function H(U){const T=[];return T.push(U.wrapS),T.push(U.wrapT),T.push(U.wrapR||0),T.push(U.magFilter),T.push(U.minFilter),T.push(U.anisotropy),T.push(U.internalFormat),T.push(U.format),T.push(U.type),T.push(U.generateMipmaps),T.push(U.premultiplyAlpha),T.push(U.flipY),T.push(U.unpackAlignment),T.push(U.colorSpace),T.join()}function J(U,T){const Q=n.get(U);if(U.isVideoTexture&&Et(U),U.isRenderTargetTexture===!1&&U.version>0&&Q.__version!==U.version){const le=U.image;if(le===null)console.warn("THREE.WebGLRenderer: Texture marked for update but no image data found.");else if(le.complete===!1)console.warn("THREE.WebGLRenderer: Texture marked for update but image is incomplete");else{Se(Q,U,T);return}}t.bindTexture(i.TEXTURE_2D,Q.__webglTexture,i.TEXTURE0+T)}function q(U,T){const Q=n.get(U);if(U.version>0&&Q.__version!==U.version){Se(Q,U,T);return}t.bindTexture(i.TEXTURE_2D_ARRAY,Q.__webglTexture,i.TEXTURE0+T)}function ee(U,T){const Q=n.get(U);if(U.version>0&&Q.__version!==U.version){Se(Q,U,T);return}t.bindTexture(i.TEXTURE_3D,Q.__webglTexture,i.TEXTURE0+T)}function j(U,T){const Q=n.get(U);if(U.version>0&&Q.__version!==U.version){ie(Q,U,T);return}t.bindTexture(i.TEXTURE_CUBE_MAP,Q.__webglTexture,i.TEXTURE0+T)}const ne={[Kc]:i.REPEAT,[Ys]:i.CLAMP_TO_EDGE,[Jc]:i.MIRRORED_REPEAT},ge={[ai]:i.NEAREST,[Bg]:i.NEAREST_MIPMAP_NEAREST,[_o]:i.NEAREST_MIPMAP_LINEAR,[vi]:i.LINEAR,[tc]:i.LINEAR_MIPMAP_NEAREST,[js]:i.LINEAR_MIPMAP_LINEAR},de={[Gg]:i.NEVER,[jg]:i.ALWAYS,[Wg]:i.LESS,[mp]:i.LEQUAL,[$g]:i.EQUAL,[Yg]:i.GEQUAL,[qg]:i.GREATER,[Xg]:i.NOTEQUAL};function ye(U,T){if(T.type===Ji&&e.has("OES_texture_float_linear")===!1&&(T.magFilter===vi||T.magFilter===tc||T.magFilter===_o||T.magFilter===js||T.minFilter===vi||T.minFilter===tc||T.minFilter===_o||T.minFilter===js)&&console.warn("THREE.WebGLRenderer: Unable to use linear filtering with floating point textures. OES_texture_float_linear not supported on this device."),i.texParameteri(U,i.TEXTURE_WRAP_S,ne[T.wrapS]),i.texParameteri(U,i.TEXTURE_WRAP_T,ne[T.wrapT]),(U===i.TEXTURE_3D||U===i.TEXTURE_2D_ARRAY)&&i.texParameteri(U,i.TEXTURE_WRAP_R,ne[T.wrapR]),i.texParameteri(U,i.TEXTURE_MAG_FILTER,ge[T.magFilter]),i.texParameteri(U,i.TEXTURE_MIN_FILTER,ge[T.minFilter]),T.compareFunction&&(i.texParameteri(U,i.TEXTURE_COMPARE_MODE,i.COMPARE_REF_TO_TEXTURE),i.texParameteri(U,i.TEXTURE_COMPARE_FUNC,de[T.compareFunction])),e.has("EXT_texture_filter_anisotropic")===!0){if(T.magFilter===ai||T.minFilter!==_o&&T.minFilter!==js||T.type===Ji&&e.has("OES_texture_float_linear")===!1)return;if(T.anisotropy>1||n.get(T).__currentAnisotropy){const Q=e.get("EXT_texture_filter_anisotropic");i.texParameterf(U,Q.TEXTURE_MAX_ANISOTROPY_EXT,Math.min(T.anisotropy,s.getMaxAnisotropy())),n.get(T).__currentAnisotropy=T.anisotropy}}}function Te(U,T){let Q=!1;U.__webglInit===void 0&&(U.__webglInit=!0,T.addEventListener("dispose",I));const le=T.source;let te=d.get(le);te===void 0&&(te={},d.set(le,te));const $=H(T);if($!==U.__cacheKey){te[$]===void 0&&(te[$]={texture:i.createTexture(),usedTimes:0},a.memory.textures++,Q=!0),te[$].usedTimes++;const Ee=te[U.__cacheKey];Ee!==void 0&&(te[U.__cacheKey].usedTimes--,Ee.usedTimes===0&&N(T)),U.__cacheKey=$,U.__webglTexture=te[$].texture}return Q}function Se(U,T,Q){let le=i.TEXTURE_2D;(T.isDataArrayTexture||T.isCompressedArrayTexture)&&(le=i.TEXTURE_2D_ARRAY),T.isData3DTexture&&(le=i.TEXTURE_3D);const te=Te(U,T),$=T.source;t.bindTexture(le,U.__webglTexture,i.TEXTURE0+Q);const Ee=n.get($);if($.version!==Ee.__version||te===!0){t.activeTexture(i.TEXTURE0+Q);const ve=wt.getPrimaries(wt.workingColorSpace),Ce=T.colorSpace===_s?null:wt.getPrimaries(T.colorSpace),Ze=T.colorSpace===_s||ve===Ce?i.NONE:i.BROWSER_DEFAULT_WEBGL;i.pixelStorei(i.UNPACK_FLIP_Y_WEBGL,T.flipY),i.pixelStorei(i.UNPACK_PREMULTIPLY_ALPHA_WEBGL,T.premultiplyAlpha),i.pixelStorei(i.UNPACK_ALIGNMENT,T.unpackAlignment),i.pixelStorei(i.UNPACK_COLORSPACE_CONVERSION_WEBGL,Ze);let me=v(T.image,!1,s.maxTextureSize);me=Ye(T,me);const Ae=r.convert(T.format,T.colorSpace),Qe=r.convert(T.type);let He=S(T.internalFormat,Ae,Qe,T.colorSpace,T.isVideoTexture);ye(le,T);let we;const Ve=T.mipmaps,B=T.isVideoTexture!==!0,ce=Ee.__version===void 0||te===!0,O=$.dataReady,ae=b(T,me);if(T.isDepthTexture)He=_(T.format===na,T.type),ce&&(B?t.texStorage2D(i.TEXTURE_2D,1,He,me.width,me.height):t.texImage2D(i.TEXTURE_2D,0,He,me.width,me.height,0,Ae,Qe,null));else if(T.isDataTexture)if(Ve.length>0){B&&ce&&t.texStorage2D(i.TEXTURE_2D,ae,He,Ve[0].width,Ve[0].height);for(let se=0,re=Ve.length;se<re;se++)we=Ve[se],B?O&&t.texSubImage2D(i.TEXTURE_2D,se,0,0,we.width,we.height,Ae,Qe,we.data):t.texImage2D(i.TEXTURE_2D,se,He,we.width,we.height,0,Ae,Qe,we.data);T.generateMipmaps=!1}else B?(ce&&t.texStorage2D(i.TEXTURE_2D,ae,He,me.width,me.height),O&&t.texSubImage2D(i.TEXTURE_2D,0,0,0,me.width,me.height,Ae,Qe,me.data)):t.texImage2D(i.TEXTURE_2D,0,He,me.width,me.height,0,Ae,Qe,me.data);else if(T.isCompressedTexture)if(T.isCompressedArrayTexture){B&&ce&&t.texStorage3D(i.TEXTURE_2D_ARRAY,ae,He,Ve[0].width,Ve[0].height,me.depth);for(let se=0,re=Ve.length;se<re;se++)if(we=Ve[se],T.format!==yi)if(Ae!==null)if(B){if(O)if(T.layerUpdates.size>0){const _e=Fd(we.width,we.height,T.format,T.type);for(const Je of T.layerUpdates){const lt=we.data.subarray(Je*_e/we.data.BYTES_PER_ELEMENT,(Je+1)*_e/we.data.BYTES_PER_ELEMENT);t.compressedTexSubImage3D(i.TEXTURE_2D_ARRAY,se,0,0,Je,we.width,we.height,1,Ae,lt,0,0)}T.clearLayerUpdates()}else t.compressedTexSubImage3D(i.TEXTURE_2D_ARRAY,se,0,0,0,we.width,we.height,me.depth,Ae,we.data,0,0)}else t.compressedTexImage3D(i.TEXTURE_2D_ARRAY,se,He,we.width,we.height,me.depth,0,we.data,0,0);else console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()");else B?O&&t.texSubImage3D(i.TEXTURE_2D_ARRAY,se,0,0,0,we.width,we.height,me.depth,Ae,Qe,we.data):t.texImage3D(i.TEXTURE_2D_ARRAY,se,He,we.width,we.height,me.depth,0,Ae,Qe,we.data)}else{B&&ce&&t.texStorage2D(i.TEXTURE_2D,ae,He,Ve[0].width,Ve[0].height);for(let se=0,re=Ve.length;se<re;se++)we=Ve[se],T.format!==yi?Ae!==null?B?O&&t.compressedTexSubImage2D(i.TEXTURE_2D,se,0,0,we.width,we.height,Ae,we.data):t.compressedTexImage2D(i.TEXTURE_2D,se,He,we.width,we.height,0,we.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()"):B?O&&t.texSubImage2D(i.TEXTURE_2D,se,0,0,we.width,we.height,Ae,Qe,we.data):t.texImage2D(i.TEXTURE_2D,se,He,we.width,we.height,0,Ae,Qe,we.data)}else if(T.isDataArrayTexture)if(B){if(ce&&t.texStorage3D(i.TEXTURE_2D_ARRAY,ae,He,me.width,me.height,me.depth),O)if(T.layerUpdates.size>0){const se=Fd(me.width,me.height,T.format,T.type);for(const re of T.layerUpdates){const _e=me.data.subarray(re*se/me.data.BYTES_PER_ELEMENT,(re+1)*se/me.data.BYTES_PER_ELEMENT);t.texSubImage3D(i.TEXTURE_2D_ARRAY,0,0,0,re,me.width,me.height,1,Ae,Qe,_e)}T.clearLayerUpdates()}else t.texSubImage3D(i.TEXTURE_2D_ARRAY,0,0,0,0,me.width,me.height,me.depth,Ae,Qe,me.data)}else t.texImage3D(i.TEXTURE_2D_ARRAY,0,He,me.width,me.height,me.depth,0,Ae,Qe,me.data);else if(T.isData3DTexture)B?(ce&&t.texStorage3D(i.TEXTURE_3D,ae,He,me.width,me.height,me.depth),O&&t.texSubImage3D(i.TEXTURE_3D,0,0,0,0,me.width,me.height,me.depth,Ae,Qe,me.data)):t.texImage3D(i.TEXTURE_3D,0,He,me.width,me.height,me.depth,0,Ae,Qe,me.data);else if(T.isFramebufferTexture){if(ce)if(B)t.texStorage2D(i.TEXTURE_2D,ae,He,me.width,me.height);else{let se=me.width,re=me.height;for(let _e=0;_e<ae;_e++)t.texImage2D(i.TEXTURE_2D,_e,He,se,re,0,Ae,Qe,null),se>>=1,re>>=1}}else if(Ve.length>0){if(B&&ce){const se=qe(Ve[0]);t.texStorage2D(i.TEXTURE_2D,ae,He,se.width,se.height)}for(let se=0,re=Ve.length;se<re;se++)we=Ve[se],B?O&&t.texSubImage2D(i.TEXTURE_2D,se,0,0,Ae,Qe,we):t.texImage2D(i.TEXTURE_2D,se,He,Ae,Qe,we);T.generateMipmaps=!1}else if(B){if(ce){const se=qe(me);t.texStorage2D(i.TEXTURE_2D,ae,He,se.width,se.height)}O&&t.texSubImage2D(i.TEXTURE_2D,0,0,0,Ae,Qe,me)}else t.texImage2D(i.TEXTURE_2D,0,He,Ae,Qe,me);p(T)&&m(le),Ee.__version=$.version,T.onUpdate&&T.onUpdate(T)}U.__version=T.version}function ie(U,T,Q){if(T.image.length!==6)return;const le=Te(U,T),te=T.source;t.bindTexture(i.TEXTURE_CUBE_MAP,U.__webglTexture,i.TEXTURE0+Q);const $=n.get(te);if(te.version!==$.__version||le===!0){t.activeTexture(i.TEXTURE0+Q);const Ee=wt.getPrimaries(wt.workingColorSpace),ve=T.colorSpace===_s?null:wt.getPrimaries(T.colorSpace),Ce=T.colorSpace===_s||Ee===ve?i.NONE:i.BROWSER_DEFAULT_WEBGL;i.pixelStorei(i.UNPACK_FLIP_Y_WEBGL,T.flipY),i.pixelStorei(i.UNPACK_PREMULTIPLY_ALPHA_WEBGL,T.premultiplyAlpha),i.pixelStorei(i.UNPACK_ALIGNMENT,T.unpackAlignment),i.pixelStorei(i.UNPACK_COLORSPACE_CONVERSION_WEBGL,Ce);const Ze=T.isCompressedTexture||T.image[0].isCompressedTexture,me=T.image[0]&&T.image[0].isDataTexture,Ae=[];for(let re=0;re<6;re++)!Ze&&!me?Ae[re]=v(T.image[re],!0,s.maxCubemapSize):Ae[re]=me?T.image[re].image:T.image[re],Ae[re]=Ye(T,Ae[re]);const Qe=Ae[0],He=r.convert(T.format,T.colorSpace),we=r.convert(T.type),Ve=S(T.internalFormat,He,we,T.colorSpace),B=T.isVideoTexture!==!0,ce=$.__version===void 0||le===!0,O=te.dataReady;let ae=b(T,Qe);ye(i.TEXTURE_CUBE_MAP,T);let se;if(Ze){B&&ce&&t.texStorage2D(i.TEXTURE_CUBE_MAP,ae,Ve,Qe.width,Qe.height);for(let re=0;re<6;re++){se=Ae[re].mipmaps;for(let _e=0;_e<se.length;_e++){const Je=se[_e];T.format!==yi?He!==null?B?O&&t.compressedTexSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,_e,0,0,Je.width,Je.height,He,Je.data):t.compressedTexImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,_e,Ve,Je.width,Je.height,0,Je.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .setTextureCube()"):B?O&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,_e,0,0,Je.width,Je.height,He,we,Je.data):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,_e,Ve,Je.width,Je.height,0,He,we,Je.data)}}}else{if(se=T.mipmaps,B&&ce){se.length>0&&ae++;const re=qe(Ae[0]);t.texStorage2D(i.TEXTURE_CUBE_MAP,ae,Ve,re.width,re.height)}for(let re=0;re<6;re++)if(me){B?O&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,0,0,0,Ae[re].width,Ae[re].height,He,we,Ae[re].data):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,0,Ve,Ae[re].width,Ae[re].height,0,He,we,Ae[re].data);for(let _e=0;_e<se.length;_e++){const lt=se[_e].image[re].image;B?O&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,_e+1,0,0,lt.width,lt.height,He,we,lt.data):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,_e+1,Ve,lt.width,lt.height,0,He,we,lt.data)}}else{B?O&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,0,0,0,He,we,Ae[re]):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,0,Ve,He,we,Ae[re]);for(let _e=0;_e<se.length;_e++){const Je=se[_e];B?O&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,_e+1,0,0,He,we,Je.image[re]):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+re,_e+1,Ve,He,we,Je.image[re])}}}p(T)&&m(i.TEXTURE_CUBE_MAP),$.__version=te.version,T.onUpdate&&T.onUpdate(T)}U.__version=T.version}function he(U,T,Q,le,te,$){const Ee=r.convert(Q.format,Q.colorSpace),ve=r.convert(Q.type),Ce=S(Q.internalFormat,Ee,ve,Q.colorSpace);if(!n.get(T).__hasExternalTextures){const me=Math.max(1,T.width>>$),Ae=Math.max(1,T.height>>$);te===i.TEXTURE_3D||te===i.TEXTURE_2D_ARRAY?t.texImage3D(te,$,Ce,me,Ae,T.depth,0,Ee,ve,null):t.texImage2D(te,$,Ce,me,Ae,0,Ee,ve,null)}t.bindFramebuffer(i.FRAMEBUFFER,U),ke(T)?o.framebufferTexture2DMultisampleEXT(i.FRAMEBUFFER,le,te,n.get(Q).__webglTexture,0,ht(T)):(te===i.TEXTURE_2D||te>=i.TEXTURE_CUBE_MAP_POSITIVE_X&&te<=i.TEXTURE_CUBE_MAP_NEGATIVE_Z)&&i.framebufferTexture2D(i.FRAMEBUFFER,le,te,n.get(Q).__webglTexture,$),t.bindFramebuffer(i.FRAMEBUFFER,null)}function be(U,T,Q){if(i.bindRenderbuffer(i.RENDERBUFFER,U),T.depthBuffer){const le=T.depthTexture,te=le&&le.isDepthTexture?le.type:null,$=_(T.stencilBuffer,te),Ee=T.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,ve=ht(T);ke(T)?o.renderbufferStorageMultisampleEXT(i.RENDERBUFFER,ve,$,T.width,T.height):Q?i.renderbufferStorageMultisample(i.RENDERBUFFER,ve,$,T.width,T.height):i.renderbufferStorage(i.RENDERBUFFER,$,T.width,T.height),i.framebufferRenderbuffer(i.FRAMEBUFFER,Ee,i.RENDERBUFFER,U)}else{const le=T.textures;for(let te=0;te<le.length;te++){const $=le[te],Ee=r.convert($.format,$.colorSpace),ve=r.convert($.type),Ce=S($.internalFormat,Ee,ve,$.colorSpace),Ze=ht(T);Q&&ke(T)===!1?i.renderbufferStorageMultisample(i.RENDERBUFFER,Ze,Ce,T.width,T.height):ke(T)?o.renderbufferStorageMultisampleEXT(i.RENDERBUFFER,Ze,Ce,T.width,T.height):i.renderbufferStorage(i.RENDERBUFFER,Ce,T.width,T.height)}}i.bindRenderbuffer(i.RENDERBUFFER,null)}function fe(U,T){if(T&&T.isWebGLCubeRenderTarget)throw new Error("Depth Texture with cube render targets is not supported");if(t.bindFramebuffer(i.FRAMEBUFFER,U),!(T.depthTexture&&T.depthTexture.isDepthTexture))throw new Error("renderTarget.depthTexture must be an instance of THREE.DepthTexture");(!n.get(T.depthTexture).__webglTexture||T.depthTexture.image.width!==T.width||T.depthTexture.image.height!==T.height)&&(T.depthTexture.image.width=T.width,T.depthTexture.image.height=T.height,T.depthTexture.needsUpdate=!0),J(T.depthTexture,0);const le=n.get(T.depthTexture).__webglTexture,te=ht(T);if(T.depthTexture.format===qr)ke(T)?o.framebufferTexture2DMultisampleEXT(i.FRAMEBUFFER,i.DEPTH_ATTACHMENT,i.TEXTURE_2D,le,0,te):i.framebufferTexture2D(i.FRAMEBUFFER,i.DEPTH_ATTACHMENT,i.TEXTURE_2D,le,0);else if(T.depthTexture.format===na)ke(T)?o.framebufferTexture2DMultisampleEXT(i.FRAMEBUFFER,i.DEPTH_STENCIL_ATTACHMENT,i.TEXTURE_2D,le,0,te):i.framebufferTexture2D(i.FRAMEBUFFER,i.DEPTH_STENCIL_ATTACHMENT,i.TEXTURE_2D,le,0);else throw new Error("Unknown depthTexture format")}function ze(U){const T=n.get(U),Q=U.isWebGLCubeRenderTarget===!0;if(T.__boundDepthTexture!==U.depthTexture){const le=U.depthTexture;if(T.__depthDisposeCallback&&T.__depthDisposeCallback(),le){const te=()=>{delete T.__boundDepthTexture,delete T.__depthDisposeCallback,le.removeEventListener("dispose",te)};le.addEventListener("dispose",te),T.__depthDisposeCallback=te}T.__boundDepthTexture=le}if(U.depthTexture&&!T.__autoAllocateDepthBuffer){if(Q)throw new Error("target.depthTexture not supported in Cube render targets");fe(T.__webglFramebuffer,U)}else if(Q){T.__webglDepthbuffer=[];for(let le=0;le<6;le++)if(t.bindFramebuffer(i.FRAMEBUFFER,T.__webglFramebuffer[le]),T.__webglDepthbuffer[le]===void 0)T.__webglDepthbuffer[le]=i.createRenderbuffer(),be(T.__webglDepthbuffer[le],U,!1);else{const te=U.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,$=T.__webglDepthbuffer[le];i.bindRenderbuffer(i.RENDERBUFFER,$),i.framebufferRenderbuffer(i.FRAMEBUFFER,te,i.RENDERBUFFER,$)}}else if(t.bindFramebuffer(i.FRAMEBUFFER,T.__webglFramebuffer),T.__webglDepthbuffer===void 0)T.__webglDepthbuffer=i.createRenderbuffer(),be(T.__webglDepthbuffer,U,!1);else{const le=U.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,te=T.__webglDepthbuffer;i.bindRenderbuffer(i.RENDERBUFFER,te),i.framebufferRenderbuffer(i.FRAMEBUFFER,le,i.RENDERBUFFER,te)}t.bindFramebuffer(i.FRAMEBUFFER,null)}function We(U,T,Q){const le=n.get(U);T!==void 0&&he(le.__webglFramebuffer,U,U.texture,i.COLOR_ATTACHMENT0,i.TEXTURE_2D,0),Q!==void 0&&ze(U)}function Fe(U){const T=U.texture,Q=n.get(U),le=n.get(T);U.addEventListener("dispose",A);const te=U.textures,$=U.isWebGLCubeRenderTarget===!0,Ee=te.length>1;if(Ee||(le.__webglTexture===void 0&&(le.__webglTexture=i.createTexture()),le.__version=T.version,a.memory.textures++),$){Q.__webglFramebuffer=[];for(let ve=0;ve<6;ve++)if(T.mipmaps&&T.mipmaps.length>0){Q.__webglFramebuffer[ve]=[];for(let Ce=0;Ce<T.mipmaps.length;Ce++)Q.__webglFramebuffer[ve][Ce]=i.createFramebuffer()}else Q.__webglFramebuffer[ve]=i.createFramebuffer()}else{if(T.mipmaps&&T.mipmaps.length>0){Q.__webglFramebuffer=[];for(let ve=0;ve<T.mipmaps.length;ve++)Q.__webglFramebuffer[ve]=i.createFramebuffer()}else Q.__webglFramebuffer=i.createFramebuffer();if(Ee)for(let ve=0,Ce=te.length;ve<Ce;ve++){const Ze=n.get(te[ve]);Ze.__webglTexture===void 0&&(Ze.__webglTexture=i.createTexture(),a.memory.textures++)}if(U.samples>0&&ke(U)===!1){Q.__webglMultisampledFramebuffer=i.createFramebuffer(),Q.__webglColorRenderbuffer=[],t.bindFramebuffer(i.FRAMEBUFFER,Q.__webglMultisampledFramebuffer);for(let ve=0;ve<te.length;ve++){const Ce=te[ve];Q.__webglColorRenderbuffer[ve]=i.createRenderbuffer(),i.bindRenderbuffer(i.RENDERBUFFER,Q.__webglColorRenderbuffer[ve]);const Ze=r.convert(Ce.format,Ce.colorSpace),me=r.convert(Ce.type),Ae=S(Ce.internalFormat,Ze,me,Ce.colorSpace,U.isXRRenderTarget===!0),Qe=ht(U);i.renderbufferStorageMultisample(i.RENDERBUFFER,Qe,Ae,U.width,U.height),i.framebufferRenderbuffer(i.FRAMEBUFFER,i.COLOR_ATTACHMENT0+ve,i.RENDERBUFFER,Q.__webglColorRenderbuffer[ve])}i.bindRenderbuffer(i.RENDERBUFFER,null),U.depthBuffer&&(Q.__webglDepthRenderbuffer=i.createRenderbuffer(),be(Q.__webglDepthRenderbuffer,U,!0)),t.bindFramebuffer(i.FRAMEBUFFER,null)}}if($){t.bindTexture(i.TEXTURE_CUBE_MAP,le.__webglTexture),ye(i.TEXTURE_CUBE_MAP,T);for(let ve=0;ve<6;ve++)if(T.mipmaps&&T.mipmaps.length>0)for(let Ce=0;Ce<T.mipmaps.length;Ce++)he(Q.__webglFramebuffer[ve][Ce],U,T,i.COLOR_ATTACHMENT0,i.TEXTURE_CUBE_MAP_POSITIVE_X+ve,Ce);else he(Q.__webglFramebuffer[ve],U,T,i.COLOR_ATTACHMENT0,i.TEXTURE_CUBE_MAP_POSITIVE_X+ve,0);p(T)&&m(i.TEXTURE_CUBE_MAP),t.unbindTexture()}else if(Ee){for(let ve=0,Ce=te.length;ve<Ce;ve++){const Ze=te[ve],me=n.get(Ze);t.bindTexture(i.TEXTURE_2D,me.__webglTexture),ye(i.TEXTURE_2D,Ze),he(Q.__webglFramebuffer,U,Ze,i.COLOR_ATTACHMENT0+ve,i.TEXTURE_2D,0),p(Ze)&&m(i.TEXTURE_2D)}t.unbindTexture()}else{let ve=i.TEXTURE_2D;if((U.isWebGL3DRenderTarget||U.isWebGLArrayRenderTarget)&&(ve=U.isWebGL3DRenderTarget?i.TEXTURE_3D:i.TEXTURE_2D_ARRAY),t.bindTexture(ve,le.__webglTexture),ye(ve,T),T.mipmaps&&T.mipmaps.length>0)for(let Ce=0;Ce<T.mipmaps.length;Ce++)he(Q.__webglFramebuffer[Ce],U,T,i.COLOR_ATTACHMENT0,ve,Ce);else he(Q.__webglFramebuffer,U,T,i.COLOR_ATTACHMENT0,ve,0);p(T)&&m(ve),t.unbindTexture()}U.depthBuffer&&ze(U)}function mt(U){const T=U.textures;for(let Q=0,le=T.length;Q<le;Q++){const te=T[Q];if(p(te)){const $=U.isWebGLCubeRenderTarget?i.TEXTURE_CUBE_MAP:i.TEXTURE_2D,Ee=n.get(te).__webglTexture;t.bindTexture($,Ee),m($),t.unbindTexture()}}}const F=[],ft=[];function rt(U){if(U.samples>0){if(ke(U)===!1){const T=U.textures,Q=U.width,le=U.height;let te=i.COLOR_BUFFER_BIT;const $=U.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,Ee=n.get(U),ve=T.length>1;if(ve)for(let Ce=0;Ce<T.length;Ce++)t.bindFramebuffer(i.FRAMEBUFFER,Ee.__webglMultisampledFramebuffer),i.framebufferRenderbuffer(i.FRAMEBUFFER,i.COLOR_ATTACHMENT0+Ce,i.RENDERBUFFER,null),t.bindFramebuffer(i.FRAMEBUFFER,Ee.__webglFramebuffer),i.framebufferTexture2D(i.DRAW_FRAMEBUFFER,i.COLOR_ATTACHMENT0+Ce,i.TEXTURE_2D,null,0);t.bindFramebuffer(i.READ_FRAMEBUFFER,Ee.__webglMultisampledFramebuffer),t.bindFramebuffer(i.DRAW_FRAMEBUFFER,Ee.__webglFramebuffer);for(let Ce=0;Ce<T.length;Ce++){if(U.resolveDepthBuffer&&(U.depthBuffer&&(te|=i.DEPTH_BUFFER_BIT),U.stencilBuffer&&U.resolveStencilBuffer&&(te|=i.STENCIL_BUFFER_BIT)),ve){i.framebufferRenderbuffer(i.READ_FRAMEBUFFER,i.COLOR_ATTACHMENT0,i.RENDERBUFFER,Ee.__webglColorRenderbuffer[Ce]);const Ze=n.get(T[Ce]).__webglTexture;i.framebufferTexture2D(i.DRAW_FRAMEBUFFER,i.COLOR_ATTACHMENT0,i.TEXTURE_2D,Ze,0)}i.blitFramebuffer(0,0,Q,le,0,0,Q,le,te,i.NEAREST),l===!0&&(F.length=0,ft.length=0,F.push(i.COLOR_ATTACHMENT0+Ce),U.depthBuffer&&U.resolveDepthBuffer===!1&&(F.push($),ft.push($),i.invalidateFramebuffer(i.DRAW_FRAMEBUFFER,ft)),i.invalidateFramebuffer(i.READ_FRAMEBUFFER,F))}if(t.bindFramebuffer(i.READ_FRAMEBUFFER,null),t.bindFramebuffer(i.DRAW_FRAMEBUFFER,null),ve)for(let Ce=0;Ce<T.length;Ce++){t.bindFramebuffer(i.FRAMEBUFFER,Ee.__webglMultisampledFramebuffer),i.framebufferRenderbuffer(i.FRAMEBUFFER,i.COLOR_ATTACHMENT0+Ce,i.RENDERBUFFER,Ee.__webglColorRenderbuffer[Ce]);const Ze=n.get(T[Ce]).__webglTexture;t.bindFramebuffer(i.FRAMEBUFFER,Ee.__webglFramebuffer),i.framebufferTexture2D(i.DRAW_FRAMEBUFFER,i.COLOR_ATTACHMENT0+Ce,i.TEXTURE_2D,Ze,0)}t.bindFramebuffer(i.DRAW_FRAMEBUFFER,Ee.__webglMultisampledFramebuffer)}else if(U.depthBuffer&&U.resolveDepthBuffer===!1&&l){const T=U.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT;i.invalidateFramebuffer(i.DRAW_FRAMEBUFFER,[T])}}}function ht(U){return Math.min(s.maxSamples,U.samples)}function ke(U){const T=n.get(U);return U.samples>0&&e.has("WEBGL_multisampled_render_to_texture")===!0&&T.__useRenderToTexture!==!1}function Et(U){const T=a.render.frame;h.get(U)!==T&&(h.set(U,T),U.update())}function Ye(U,T){const Q=U.colorSpace,le=U.format,te=U.type;return U.isCompressedTexture===!0||U.isVideoTexture===!0||Q!==Cs&&Q!==_s&&(wt.getTransfer(Q)===Bt?(le!==yi||te!==ss)&&console.warn("THREE.WebGLTextures: sRGB encoded textures have to use RGBAFormat and UnsignedByteType."):console.error("THREE.WebGLTextures: Unsupported texture color space:",Q)),T}function qe(U){return typeof HTMLImageElement<"u"&&U instanceof HTMLImageElement?(c.width=U.naturalWidth||U.width,c.height=U.naturalHeight||U.height):typeof VideoFrame<"u"&&U instanceof VideoFrame?(c.width=U.displayWidth,c.height=U.displayHeight):(c.width=U.width,c.height=U.height),c}this.allocateTextureUnit=X,this.resetTextureUnits=P,this.setTexture2D=J,this.setTexture2DArray=q,this.setTexture3D=ee,this.setTextureCube=j,this.rebindTextures=We,this.setupRenderTarget=Fe,this.updateRenderTargetMipmap=mt,this.updateMultisampleRenderTarget=rt,this.setupDepthRenderbuffer=ze,this.setupFrameBufferTexture=he,this.useMultisampledRTT=ke}function fS(i,e){function t(n,s=_s){let r;const a=wt.getTransfer(s);if(n===ss)return i.UNSIGNED_BYTE;if(n===Wh)return i.UNSIGNED_SHORT_4_4_4_4;if(n===$h)return i.UNSIGNED_SHORT_5_5_5_1;if(n===ap)return i.UNSIGNED_INT_5_9_9_9_REV;if(n===sp)return i.BYTE;if(n===rp)return i.SHORT;if(n===Za)return i.UNSIGNED_SHORT;if(n===Gh)return i.INT;if(n===Zs)return i.UNSIGNED_INT;if(n===Ji)return i.FLOAT;if(n===so)return i.HALF_FLOAT;if(n===op)return i.ALPHA;if(n===lp)return i.RGB;if(n===yi)return i.RGBA;if(n===cp)return i.LUMINANCE;if(n===hp)return i.LUMINANCE_ALPHA;if(n===qr)return i.DEPTH_COMPONENT;if(n===na)return i.DEPTH_STENCIL;if(n===up)return i.RED;if(n===qh)return i.RED_INTEGER;if(n===dp)return i.RG;if(n===Xh)return i.RG_INTEGER;if(n===Yh)return i.RGBA_INTEGER;if(n===nl||n===il||n===sl||n===rl)if(a===Bt)if(r=e.get("WEBGL_compressed_texture_s3tc_srgb"),r!==null){if(n===nl)return r.COMPRESSED_SRGB_S3TC_DXT1_EXT;if(n===il)return r.COMPRESSED_SRGB_ALPHA_S3TC_DXT1_EXT;if(n===sl)return r.COMPRESSED_SRGB_ALPHA_S3TC_DXT3_EXT;if(n===rl)return r.COMPRESSED_SRGB_ALPHA_S3TC_DXT5_EXT}else return null;else if(r=e.get("WEBGL_compressed_texture_s3tc"),r!==null){if(n===nl)return r.COMPRESSED_RGB_S3TC_DXT1_EXT;if(n===il)return r.COMPRESSED_RGBA_S3TC_DXT1_EXT;if(n===sl)return r.COMPRESSED_RGBA_S3TC_DXT3_EXT;if(n===rl)return r.COMPRESSED_RGBA_S3TC_DXT5_EXT}else return null;if(n===Zc||n===Qc||n===eh||n===th)if(r=e.get("WEBGL_compressed_texture_pvrtc"),r!==null){if(n===Zc)return r.COMPRESSED_RGB_PVRTC_4BPPV1_IMG;if(n===Qc)return r.COMPRESSED_RGB_PVRTC_2BPPV1_IMG;if(n===eh)return r.COMPRESSED_RGBA_PVRTC_4BPPV1_IMG;if(n===th)return r.COMPRESSED_RGBA_PVRTC_2BPPV1_IMG}else return null;if(n===nh||n===ih||n===sh)if(r=e.get("WEBGL_compressed_texture_etc"),r!==null){if(n===nh||n===ih)return a===Bt?r.COMPRESSED_SRGB8_ETC2:r.COMPRESSED_RGB8_ETC2;if(n===sh)return a===Bt?r.COMPRESSED_SRGB8_ALPHA8_ETC2_EAC:r.COMPRESSED_RGBA8_ETC2_EAC}else return null;if(n===rh||n===ah||n===oh||n===lh||n===ch||n===hh||n===uh||n===dh||n===fh||n===ph||n===mh||n===gh||n===vh||n===xh)if(r=e.get("WEBGL_compressed_texture_astc"),r!==null){if(n===rh)return a===Bt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_4x4_KHR:r.COMPRESSED_RGBA_ASTC_4x4_KHR;if(n===ah)return a===Bt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_5x4_KHR:r.COMPRESSED_RGBA_ASTC_5x4_KHR;if(n===oh)return a===Bt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_5x5_KHR:r.COMPRESSED_RGBA_ASTC_5x5_KHR;if(n===lh)return a===Bt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_6x5_KHR:r.COMPRESSED_RGBA_ASTC_6x5_KHR;if(n===ch)return a===Bt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_6x6_KHR:r.COMPRESSED_RGBA_ASTC_6x6_KHR;if(n===hh)return a===Bt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_8x5_KHR:r.COMPRESSED_RGBA_ASTC_8x5_KHR;if(n===uh)return a===Bt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_8x6_KHR:r.COMPRESSED_RGBA_ASTC_8x6_KHR;if(n===dh)return a===Bt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_8x8_KHR:r.COMPRESSED_RGBA_ASTC_8x8_KHR;if(n===fh)return a===Bt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_10x5_KHR:r.COMPRESSED_RGBA_ASTC_10x5_KHR;if(n===ph)return a===Bt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_10x6_KHR:r.COMPRESSED_RGBA_ASTC_10x6_KHR;if(n===mh)return a===Bt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_10x8_KHR:r.COMPRESSED_RGBA_ASTC_10x8_KHR;if(n===gh)return a===Bt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_10x10_KHR:r.COMPRESSED_RGBA_ASTC_10x10_KHR;if(n===vh)return a===Bt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_12x10_KHR:r.COMPRESSED_RGBA_ASTC_12x10_KHR;if(n===xh)return a===Bt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_12x12_KHR:r.COMPRESSED_RGBA_ASTC_12x12_KHR}else return null;if(n===al||n===_h||n===yh)if(r=e.get("EXT_texture_compression_bptc"),r!==null){if(n===al)return a===Bt?r.COMPRESSED_SRGB_ALPHA_BPTC_UNORM_EXT:r.COMPRESSED_RGBA_BPTC_UNORM_EXT;if(n===_h)return r.COMPRESSED_RGB_BPTC_SIGNED_FLOAT_EXT;if(n===yh)return r.COMPRESSED_RGB_BPTC_UNSIGNED_FLOAT_EXT}else return null;if(n===fp||n===Sh||n===bh||n===Mh)if(r=e.get("EXT_texture_compression_rgtc"),r!==null){if(n===al)return r.COMPRESSED_RED_RGTC1_EXT;if(n===Sh)return r.COMPRESSED_SIGNED_RED_RGTC1_EXT;if(n===bh)return r.COMPRESSED_RED_GREEN_RGTC2_EXT;if(n===Mh)return r.COMPRESSED_SIGNED_RED_GREEN_RGTC2_EXT}else return null;return n===ta?i.UNSIGNED_INT_24_8:i[n]!==void 0?i[n]:null}return{convert:t}}class pS extends Rn{constructor(e=[]){super(),this.isArrayCamera=!0,this.cameras=e}}class oi extends sn{constructor(){super(),this.isGroup=!0,this.type="Group"}}const mS={type:"move"};class Tc{constructor(){this._targetRay=null,this._grip=null,this._hand=null}getHandSpace(){return this._hand===null&&(this._hand=new oi,this._hand.matrixAutoUpdate=!1,this._hand.visible=!1,this._hand.joints={},this._hand.inputState={pinching:!1}),this._hand}getTargetRaySpace(){return this._targetRay===null&&(this._targetRay=new oi,this._targetRay.matrixAutoUpdate=!1,this._targetRay.visible=!1,this._targetRay.hasLinearVelocity=!1,this._targetRay.linearVelocity=new V,this._targetRay.hasAngularVelocity=!1,this._targetRay.angularVelocity=new V),this._targetRay}getGripSpace(){return this._grip===null&&(this._grip=new oi,this._grip.matrixAutoUpdate=!1,this._grip.visible=!1,this._grip.hasLinearVelocity=!1,this._grip.linearVelocity=new V,this._grip.hasAngularVelocity=!1,this._grip.angularVelocity=new V),this._grip}dispatchEvent(e){return this._targetRay!==null&&this._targetRay.dispatchEvent(e),this._grip!==null&&this._grip.dispatchEvent(e),this._hand!==null&&this._hand.dispatchEvent(e),this}connect(e){if(e&&e.hand){const t=this._hand;if(t)for(const n of e.hand.values())this._getHandJoint(t,n)}return this.dispatchEvent({type:"connected",data:e}),this}disconnect(e){return this.dispatchEvent({type:"disconnected",data:e}),this._targetRay!==null&&(this._targetRay.visible=!1),this._grip!==null&&(this._grip.visible=!1),this._hand!==null&&(this._hand.visible=!1),this}update(e,t,n){let s=null,r=null,a=null;const o=this._targetRay,l=this._grip,c=this._hand;if(e&&t.session.visibilityState!=="visible-blurred"){if(c&&e.hand){a=!0;for(const v of e.hand.values()){const p=t.getJointPose(v,n),m=this._getHandJoint(c,v);p!==null&&(m.matrix.fromArray(p.transform.matrix),m.matrix.decompose(m.position,m.rotation,m.scale),m.matrixWorldNeedsUpdate=!0,m.jointRadius=p.radius),m.visible=p!==null}const h=c.joints["index-finger-tip"],u=c.joints["thumb-tip"],d=h.position.distanceTo(u.position),f=.02,g=.005;c.inputState.pinching&&d>f+g?(c.inputState.pinching=!1,this.dispatchEvent({type:"pinchend",handedness:e.handedness,target:this})):!c.inputState.pinching&&d<=f-g&&(c.inputState.pinching=!0,this.dispatchEvent({type:"pinchstart",handedness:e.handedness,target:this}))}else l!==null&&e.gripSpace&&(r=t.getPose(e.gripSpace,n),r!==null&&(l.matrix.fromArray(r.transform.matrix),l.matrix.decompose(l.position,l.rotation,l.scale),l.matrixWorldNeedsUpdate=!0,r.linearVelocity?(l.hasLinearVelocity=!0,l.linearVelocity.copy(r.linearVelocity)):l.hasLinearVelocity=!1,r.angularVelocity?(l.hasAngularVelocity=!0,l.angularVelocity.copy(r.angularVelocity)):l.hasAngularVelocity=!1));o!==null&&(s=t.getPose(e.targetRaySpace,n),s===null&&r!==null&&(s=r),s!==null&&(o.matrix.fromArray(s.transform.matrix),o.matrix.decompose(o.position,o.rotation,o.scale),o.matrixWorldNeedsUpdate=!0,s.linearVelocity?(o.hasLinearVelocity=!0,o.linearVelocity.copy(s.linearVelocity)):o.hasLinearVelocity=!1,s.angularVelocity?(o.hasAngularVelocity=!0,o.angularVelocity.copy(s.angularVelocity)):o.hasAngularVelocity=!1,this.dispatchEvent(mS)))}return o!==null&&(o.visible=s!==null),l!==null&&(l.visible=r!==null),c!==null&&(c.visible=a!==null),this}_getHandJoint(e,t){if(e.joints[t.jointName]===void 0){const n=new oi;n.matrixAutoUpdate=!1,n.visible=!1,e.joints[t.jointName]=n,e.add(n)}return e.joints[t.jointName]}}const gS=`
void main() {

	gl_Position = vec4( position, 1.0 );

}`,vS=`
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

}`;class xS{constructor(){this.texture=null,this.mesh=null,this.depthNear=0,this.depthFar=0}init(e,t,n){if(this.texture===null){const s=new Bn,r=e.properties.get(s);r.__webglTexture=t.texture,(t.depthNear!=n.depthNear||t.depthFar!=n.depthFar)&&(this.depthNear=t.depthNear,this.depthFar=t.depthFar),this.texture=s}}getMesh(e){if(this.texture!==null&&this.mesh===null){const t=e.cameras[0].viewport,n=new ws({vertexShader:gS,fragmentShader:vS,uniforms:{depthColor:{value:this.texture},depthWidth:{value:t.z},depthHeight:{value:t.w}}});this.mesh=new jt(new lo(20,20),n)}return this.mesh}reset(){this.texture=null,this.mesh=null}getDepthTexture(){return this.texture}}class _S extends pa{constructor(e,t){super();const n=this;let s=null,r=1,a=null,o="local-floor",l=1,c=null,h=null,u=null,d=null,f=null,g=null;const v=new xS,p=t.getContextAttributes();let m=null,S=null;const _=[],b=[],I=new Xe;let A=null;const R=new Rn;R.layers.enable(1),R.viewport=new on;const N=new Rn;N.layers.enable(2),N.viewport=new on;const w=[R,N],y=new pS;y.layers.enable(1),y.layers.enable(2);let P=null,X=null;this.cameraAutoUpdate=!0,this.enabled=!1,this.isPresenting=!1,this.getController=function(ie){let he=_[ie];return he===void 0&&(he=new Tc,_[ie]=he),he.getTargetRaySpace()},this.getControllerGrip=function(ie){let he=_[ie];return he===void 0&&(he=new Tc,_[ie]=he),he.getGripSpace()},this.getHand=function(ie){let he=_[ie];return he===void 0&&(he=new Tc,_[ie]=he),he.getHandSpace()};function H(ie){const he=b.indexOf(ie.inputSource);if(he===-1)return;const be=_[he];be!==void 0&&(be.update(ie.inputSource,ie.frame,c||a),be.dispatchEvent({type:ie.type,data:ie.inputSource}))}function J(){s.removeEventListener("select",H),s.removeEventListener("selectstart",H),s.removeEventListener("selectend",H),s.removeEventListener("squeeze",H),s.removeEventListener("squeezestart",H),s.removeEventListener("squeezeend",H),s.removeEventListener("end",J),s.removeEventListener("inputsourceschange",q);for(let ie=0;ie<_.length;ie++){const he=b[ie];he!==null&&(b[ie]=null,_[ie].disconnect(he))}P=null,X=null,v.reset(),e.setRenderTarget(m),f=null,d=null,u=null,s=null,S=null,Se.stop(),n.isPresenting=!1,e.setPixelRatio(A),e.setSize(I.width,I.height,!1),n.dispatchEvent({type:"sessionend"})}this.setFramebufferScaleFactor=function(ie){r=ie,n.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change framebuffer scale while presenting.")},this.setReferenceSpaceType=function(ie){o=ie,n.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change reference space type while presenting.")},this.getReferenceSpace=function(){return c||a},this.setReferenceSpace=function(ie){c=ie},this.getBaseLayer=function(){return d!==null?d:f},this.getBinding=function(){return u},this.getFrame=function(){return g},this.getSession=function(){return s},this.setSession=async function(ie){if(s=ie,s!==null){if(m=e.getRenderTarget(),s.addEventListener("select",H),s.addEventListener("selectstart",H),s.addEventListener("selectend",H),s.addEventListener("squeeze",H),s.addEventListener("squeezestart",H),s.addEventListener("squeezeend",H),s.addEventListener("end",J),s.addEventListener("inputsourceschange",q),p.xrCompatible!==!0&&await t.makeXRCompatible(),A=e.getPixelRatio(),e.getSize(I),s.renderState.layers===void 0){const he={antialias:p.antialias,alpha:!0,depth:p.depth,stencil:p.stencil,framebufferScaleFactor:r};f=new XRWebGLLayer(s,t,he),s.updateRenderState({baseLayer:f}),e.setPixelRatio(1),e.setSize(f.framebufferWidth,f.framebufferHeight,!1),S=new Qs(f.framebufferWidth,f.framebufferHeight,{format:yi,type:ss,colorSpace:e.outputColorSpace,stencilBuffer:p.stencil})}else{let he=null,be=null,fe=null;p.depth&&(fe=p.stencil?t.DEPTH24_STENCIL8:t.DEPTH_COMPONENT24,he=p.stencil?na:qr,be=p.stencil?ta:Zs);const ze={colorFormat:t.RGBA8,depthFormat:fe,scaleFactor:r};u=new XRWebGLBinding(s,t),d=u.createProjectionLayer(ze),s.updateRenderState({layers:[d]}),e.setPixelRatio(1),e.setSize(d.textureWidth,d.textureHeight,!1),S=new Qs(d.textureWidth,d.textureHeight,{format:yi,type:ss,depthTexture:new Tp(d.textureWidth,d.textureHeight,be,void 0,void 0,void 0,void 0,void 0,void 0,he),stencilBuffer:p.stencil,colorSpace:e.outputColorSpace,samples:p.antialias?4:0,resolveDepthBuffer:d.ignoreDepthValues===!1})}S.isXRRenderTarget=!0,this.setFoveation(l),c=null,a=await s.requestReferenceSpace(o),Se.setContext(s),Se.start(),n.isPresenting=!0,n.dispatchEvent({type:"sessionstart"})}},this.getEnvironmentBlendMode=function(){if(s!==null)return s.environmentBlendMode},this.getDepthTexture=function(){return v.getDepthTexture()};function q(ie){for(let he=0;he<ie.removed.length;he++){const be=ie.removed[he],fe=b.indexOf(be);fe>=0&&(b[fe]=null,_[fe].disconnect(be))}for(let he=0;he<ie.added.length;he++){const be=ie.added[he];let fe=b.indexOf(be);if(fe===-1){for(let We=0;We<_.length;We++)if(We>=b.length){b.push(be),fe=We;break}else if(b[We]===null){b[We]=be,fe=We;break}if(fe===-1)break}const ze=_[fe];ze&&ze.connect(be)}}const ee=new V,j=new V;function ne(ie,he,be){ee.setFromMatrixPosition(he.matrixWorld),j.setFromMatrixPosition(be.matrixWorld);const fe=ee.distanceTo(j),ze=he.projectionMatrix.elements,We=be.projectionMatrix.elements,Fe=ze[14]/(ze[10]-1),mt=ze[14]/(ze[10]+1),F=(ze[9]+1)/ze[5],ft=(ze[9]-1)/ze[5],rt=(ze[8]-1)/ze[0],ht=(We[8]+1)/We[0],ke=Fe*rt,Et=Fe*ht,Ye=fe/(-rt+ht),qe=Ye*-rt;if(he.matrixWorld.decompose(ie.position,ie.quaternion,ie.scale),ie.translateX(qe),ie.translateZ(Ye),ie.matrixWorld.compose(ie.position,ie.quaternion,ie.scale),ie.matrixWorldInverse.copy(ie.matrixWorld).invert(),ze[10]===-1)ie.projectionMatrix.copy(he.projectionMatrix),ie.projectionMatrixInverse.copy(he.projectionMatrixInverse);else{const U=Fe+Ye,T=mt+Ye,Q=ke-qe,le=Et+(fe-qe),te=F*mt/T*U,$=ft*mt/T*U;ie.projectionMatrix.makePerspective(Q,le,te,$,U,T),ie.projectionMatrixInverse.copy(ie.projectionMatrix).invert()}}function ge(ie,he){he===null?ie.matrixWorld.copy(ie.matrix):ie.matrixWorld.multiplyMatrices(he.matrixWorld,ie.matrix),ie.matrixWorldInverse.copy(ie.matrixWorld).invert()}this.updateCamera=function(ie){if(s===null)return;let he=ie.near,be=ie.far;v.texture!==null&&(v.depthNear>0&&(he=v.depthNear),v.depthFar>0&&(be=v.depthFar)),y.near=N.near=R.near=he,y.far=N.far=R.far=be,(P!==y.near||X!==y.far)&&(s.updateRenderState({depthNear:y.near,depthFar:y.far}),P=y.near,X=y.far);const fe=ie.parent,ze=y.cameras;ge(y,fe);for(let We=0;We<ze.length;We++)ge(ze[We],fe);ze.length===2?ne(y,R,N):y.projectionMatrix.copy(R.projectionMatrix),de(ie,y,fe)};function de(ie,he,be){be===null?ie.matrix.copy(he.matrixWorld):(ie.matrix.copy(be.matrixWorld),ie.matrix.invert(),ie.matrix.multiply(he.matrixWorld)),ie.matrix.decompose(ie.position,ie.quaternion,ie.scale),ie.updateMatrixWorld(!0),ie.projectionMatrix.copy(he.projectionMatrix),ie.projectionMatrixInverse.copy(he.projectionMatrixInverse),ie.isPerspectiveCamera&&(ie.fov=Qa*2*Math.atan(1/ie.projectionMatrix.elements[5]),ie.zoom=1)}this.getCamera=function(){return y},this.getFoveation=function(){if(!(d===null&&f===null))return l},this.setFoveation=function(ie){l=ie,d!==null&&(d.fixedFoveation=ie),f!==null&&f.fixedFoveation!==void 0&&(f.fixedFoveation=ie)},this.hasDepthSensing=function(){return v.texture!==null},this.getDepthSensingMesh=function(){return v.getMesh(y)};let ye=null;function Te(ie,he){if(h=he.getViewerPose(c||a),g=he,h!==null){const be=h.views;f!==null&&(e.setRenderTargetFramebuffer(S,f.framebuffer),e.setRenderTarget(S));let fe=!1;be.length!==y.cameras.length&&(y.cameras.length=0,fe=!0);for(let We=0;We<be.length;We++){const Fe=be[We];let mt=null;if(f!==null)mt=f.getViewport(Fe);else{const ft=u.getViewSubImage(d,Fe);mt=ft.viewport,We===0&&(e.setRenderTargetTextures(S,ft.colorTexture,d.ignoreDepthValues?void 0:ft.depthStencilTexture),e.setRenderTarget(S))}let F=w[We];F===void 0&&(F=new Rn,F.layers.enable(We),F.viewport=new on,w[We]=F),F.matrix.fromArray(Fe.transform.matrix),F.matrix.decompose(F.position,F.quaternion,F.scale),F.projectionMatrix.fromArray(Fe.projectionMatrix),F.projectionMatrixInverse.copy(F.projectionMatrix).invert(),F.viewport.set(mt.x,mt.y,mt.width,mt.height),We===0&&(y.matrix.copy(F.matrix),y.matrix.decompose(y.position,y.quaternion,y.scale)),fe===!0&&y.cameras.push(F)}const ze=s.enabledFeatures;if(ze&&ze.includes("depth-sensing")){const We=u.getDepthInformation(be[0]);We&&We.isValid&&We.texture&&v.init(e,We,s.renderState)}}for(let be=0;be<_.length;be++){const fe=b[be],ze=_[be];fe!==null&&ze!==void 0&&ze.update(fe,he,c||a)}ye&&ye(ie,he),he.detectedPlanes&&n.dispatchEvent({type:"planesdetected",data:he}),g=null}const Se=new Ep;Se.setAnimationLoop(Te),this.setAnimationLoop=function(ie){ye=ie},this.dispose=function(){}}}const Hs=new Oi,yS=new zt;function SS(i,e){function t(p,m){p.matrixAutoUpdate===!0&&p.updateMatrix(),m.value.copy(p.matrix)}function n(p,m){m.color.getRGB(p.fogColor.value,bp(i)),m.isFog?(p.fogNear.value=m.near,p.fogFar.value=m.far):m.isFogExp2&&(p.fogDensity.value=m.density)}function s(p,m,S,_,b){m.isMeshBasicMaterial||m.isMeshLambertMaterial?r(p,m):m.isMeshToonMaterial?(r(p,m),u(p,m)):m.isMeshPhongMaterial?(r(p,m),h(p,m)):m.isMeshStandardMaterial?(r(p,m),d(p,m),m.isMeshPhysicalMaterial&&f(p,m,b)):m.isMeshMatcapMaterial?(r(p,m),g(p,m)):m.isMeshDepthMaterial?r(p,m):m.isMeshDistanceMaterial?(r(p,m),v(p,m)):m.isMeshNormalMaterial?r(p,m):m.isLineBasicMaterial?(a(p,m),m.isLineDashedMaterial&&o(p,m)):m.isPointsMaterial?l(p,m,S,_):m.isSpriteMaterial?c(p,m):m.isShadowMaterial?(p.color.value.copy(m.color),p.opacity.value=m.opacity):m.isShaderMaterial&&(m.uniformsNeedUpdate=!1)}function r(p,m){p.opacity.value=m.opacity,m.color&&p.diffuse.value.copy(m.color),m.emissive&&p.emissive.value.copy(m.emissive).multiplyScalar(m.emissiveIntensity),m.map&&(p.map.value=m.map,t(m.map,p.mapTransform)),m.alphaMap&&(p.alphaMap.value=m.alphaMap,t(m.alphaMap,p.alphaMapTransform)),m.bumpMap&&(p.bumpMap.value=m.bumpMap,t(m.bumpMap,p.bumpMapTransform),p.bumpScale.value=m.bumpScale,m.side===Vn&&(p.bumpScale.value*=-1)),m.normalMap&&(p.normalMap.value=m.normalMap,t(m.normalMap,p.normalMapTransform),p.normalScale.value.copy(m.normalScale),m.side===Vn&&p.normalScale.value.negate()),m.displacementMap&&(p.displacementMap.value=m.displacementMap,t(m.displacementMap,p.displacementMapTransform),p.displacementScale.value=m.displacementScale,p.displacementBias.value=m.displacementBias),m.emissiveMap&&(p.emissiveMap.value=m.emissiveMap,t(m.emissiveMap,p.emissiveMapTransform)),m.specularMap&&(p.specularMap.value=m.specularMap,t(m.specularMap,p.specularMapTransform)),m.alphaTest>0&&(p.alphaTest.value=m.alphaTest);const S=e.get(m),_=S.envMap,b=S.envMapRotation;_&&(p.envMap.value=_,Hs.copy(b),Hs.x*=-1,Hs.y*=-1,Hs.z*=-1,_.isCubeTexture&&_.isRenderTargetTexture===!1&&(Hs.y*=-1,Hs.z*=-1),p.envMapRotation.value.setFromMatrix4(yS.makeRotationFromEuler(Hs)),p.flipEnvMap.value=_.isCubeTexture&&_.isRenderTargetTexture===!1?-1:1,p.reflectivity.value=m.reflectivity,p.ior.value=m.ior,p.refractionRatio.value=m.refractionRatio),m.lightMap&&(p.lightMap.value=m.lightMap,p.lightMapIntensity.value=m.lightMapIntensity,t(m.lightMap,p.lightMapTransform)),m.aoMap&&(p.aoMap.value=m.aoMap,p.aoMapIntensity.value=m.aoMapIntensity,t(m.aoMap,p.aoMapTransform))}function a(p,m){p.diffuse.value.copy(m.color),p.opacity.value=m.opacity,m.map&&(p.map.value=m.map,t(m.map,p.mapTransform))}function o(p,m){p.dashSize.value=m.dashSize,p.totalSize.value=m.dashSize+m.gapSize,p.scale.value=m.scale}function l(p,m,S,_){p.diffuse.value.copy(m.color),p.opacity.value=m.opacity,p.size.value=m.size*S,p.scale.value=_*.5,m.map&&(p.map.value=m.map,t(m.map,p.uvTransform)),m.alphaMap&&(p.alphaMap.value=m.alphaMap,t(m.alphaMap,p.alphaMapTransform)),m.alphaTest>0&&(p.alphaTest.value=m.alphaTest)}function c(p,m){p.diffuse.value.copy(m.color),p.opacity.value=m.opacity,p.rotation.value=m.rotation,m.map&&(p.map.value=m.map,t(m.map,p.mapTransform)),m.alphaMap&&(p.alphaMap.value=m.alphaMap,t(m.alphaMap,p.alphaMapTransform)),m.alphaTest>0&&(p.alphaTest.value=m.alphaTest)}function h(p,m){p.specular.value.copy(m.specular),p.shininess.value=Math.max(m.shininess,1e-4)}function u(p,m){m.gradientMap&&(p.gradientMap.value=m.gradientMap)}function d(p,m){p.metalness.value=m.metalness,m.metalnessMap&&(p.metalnessMap.value=m.metalnessMap,t(m.metalnessMap,p.metalnessMapTransform)),p.roughness.value=m.roughness,m.roughnessMap&&(p.roughnessMap.value=m.roughnessMap,t(m.roughnessMap,p.roughnessMapTransform)),m.envMap&&(p.envMapIntensity.value=m.envMapIntensity)}function f(p,m,S){p.ior.value=m.ior,m.sheen>0&&(p.sheenColor.value.copy(m.sheenColor).multiplyScalar(m.sheen),p.sheenRoughness.value=m.sheenRoughness,m.sheenColorMap&&(p.sheenColorMap.value=m.sheenColorMap,t(m.sheenColorMap,p.sheenColorMapTransform)),m.sheenRoughnessMap&&(p.sheenRoughnessMap.value=m.sheenRoughnessMap,t(m.sheenRoughnessMap,p.sheenRoughnessMapTransform))),m.clearcoat>0&&(p.clearcoat.value=m.clearcoat,p.clearcoatRoughness.value=m.clearcoatRoughness,m.clearcoatMap&&(p.clearcoatMap.value=m.clearcoatMap,t(m.clearcoatMap,p.clearcoatMapTransform)),m.clearcoatRoughnessMap&&(p.clearcoatRoughnessMap.value=m.clearcoatRoughnessMap,t(m.clearcoatRoughnessMap,p.clearcoatRoughnessMapTransform)),m.clearcoatNormalMap&&(p.clearcoatNormalMap.value=m.clearcoatNormalMap,t(m.clearcoatNormalMap,p.clearcoatNormalMapTransform),p.clearcoatNormalScale.value.copy(m.clearcoatNormalScale),m.side===Vn&&p.clearcoatNormalScale.value.negate())),m.dispersion>0&&(p.dispersion.value=m.dispersion),m.iridescence>0&&(p.iridescence.value=m.iridescence,p.iridescenceIOR.value=m.iridescenceIOR,p.iridescenceThicknessMinimum.value=m.iridescenceThicknessRange[0],p.iridescenceThicknessMaximum.value=m.iridescenceThicknessRange[1],m.iridescenceMap&&(p.iridescenceMap.value=m.iridescenceMap,t(m.iridescenceMap,p.iridescenceMapTransform)),m.iridescenceThicknessMap&&(p.iridescenceThicknessMap.value=m.iridescenceThicknessMap,t(m.iridescenceThicknessMap,p.iridescenceThicknessMapTransform))),m.transmission>0&&(p.transmission.value=m.transmission,p.transmissionSamplerMap.value=S.texture,p.transmissionSamplerSize.value.set(S.width,S.height),m.transmissionMap&&(p.transmissionMap.value=m.transmissionMap,t(m.transmissionMap,p.transmissionMapTransform)),p.thickness.value=m.thickness,m.thicknessMap&&(p.thicknessMap.value=m.thicknessMap,t(m.thicknessMap,p.thicknessMapTransform)),p.attenuationDistance.value=m.attenuationDistance,p.attenuationColor.value.copy(m.attenuationColor)),m.anisotropy>0&&(p.anisotropyVector.value.set(m.anisotropy*Math.cos(m.anisotropyRotation),m.anisotropy*Math.sin(m.anisotropyRotation)),m.anisotropyMap&&(p.anisotropyMap.value=m.anisotropyMap,t(m.anisotropyMap,p.anisotropyMapTransform))),p.specularIntensity.value=m.specularIntensity,p.specularColor.value.copy(m.specularColor),m.specularColorMap&&(p.specularColorMap.value=m.specularColorMap,t(m.specularColorMap,p.specularColorMapTransform)),m.specularIntensityMap&&(p.specularIntensityMap.value=m.specularIntensityMap,t(m.specularIntensityMap,p.specularIntensityMapTransform))}function g(p,m){m.matcap&&(p.matcap.value=m.matcap)}function v(p,m){const S=e.get(m).light;p.referencePosition.value.setFromMatrixPosition(S.matrixWorld),p.nearDistance.value=S.shadow.camera.near,p.farDistance.value=S.shadow.camera.far}return{refreshFogUniforms:n,refreshMaterialUniforms:s}}function bS(i,e,t,n){let s={},r={},a=[];const o=i.getParameter(i.MAX_UNIFORM_BUFFER_BINDINGS);function l(S,_){const b=_.program;n.uniformBlockBinding(S,b)}function c(S,_){let b=s[S.id];b===void 0&&(g(S),b=h(S),s[S.id]=b,S.addEventListener("dispose",p));const I=_.program;n.updateUBOMapping(S,I);const A=e.render.frame;r[S.id]!==A&&(d(S),r[S.id]=A)}function h(S){const _=u();S.__bindingPointIndex=_;const b=i.createBuffer(),I=S.__size,A=S.usage;return i.bindBuffer(i.UNIFORM_BUFFER,b),i.bufferData(i.UNIFORM_BUFFER,I,A),i.bindBuffer(i.UNIFORM_BUFFER,null),i.bindBufferBase(i.UNIFORM_BUFFER,_,b),b}function u(){for(let S=0;S<o;S++)if(a.indexOf(S)===-1)return a.push(S),S;return console.error("THREE.WebGLRenderer: Maximum number of simultaneously usable uniforms groups reached."),0}function d(S){const _=s[S.id],b=S.uniforms,I=S.__cache;i.bindBuffer(i.UNIFORM_BUFFER,_);for(let A=0,R=b.length;A<R;A++){const N=Array.isArray(b[A])?b[A]:[b[A]];for(let w=0,y=N.length;w<y;w++){const P=N[w];if(f(P,A,w,I)===!0){const X=P.__offset,H=Array.isArray(P.value)?P.value:[P.value];let J=0;for(let q=0;q<H.length;q++){const ee=H[q],j=v(ee);typeof ee=="number"||typeof ee=="boolean"?(P.__data[0]=ee,i.bufferSubData(i.UNIFORM_BUFFER,X+J,P.__data)):ee.isMatrix3?(P.__data[0]=ee.elements[0],P.__data[1]=ee.elements[1],P.__data[2]=ee.elements[2],P.__data[3]=0,P.__data[4]=ee.elements[3],P.__data[5]=ee.elements[4],P.__data[6]=ee.elements[5],P.__data[7]=0,P.__data[8]=ee.elements[6],P.__data[9]=ee.elements[7],P.__data[10]=ee.elements[8],P.__data[11]=0):(ee.toArray(P.__data,J),J+=j.storage/Float32Array.BYTES_PER_ELEMENT)}i.bufferSubData(i.UNIFORM_BUFFER,X,P.__data)}}}i.bindBuffer(i.UNIFORM_BUFFER,null)}function f(S,_,b,I){const A=S.value,R=_+"_"+b;if(I[R]===void 0)return typeof A=="number"||typeof A=="boolean"?I[R]=A:I[R]=A.clone(),!0;{const N=I[R];if(typeof A=="number"||typeof A=="boolean"){if(N!==A)return I[R]=A,!0}else if(N.equals(A)===!1)return N.copy(A),!0}return!1}function g(S){const _=S.uniforms;let b=0;const I=16;for(let R=0,N=_.length;R<N;R++){const w=Array.isArray(_[R])?_[R]:[_[R]];for(let y=0,P=w.length;y<P;y++){const X=w[y],H=Array.isArray(X.value)?X.value:[X.value];for(let J=0,q=H.length;J<q;J++){const ee=H[J],j=v(ee),ne=b%I,ge=ne%j.boundary,de=ne+ge;b+=ge,de!==0&&I-de<j.storage&&(b+=I-de),X.__data=new Float32Array(j.storage/Float32Array.BYTES_PER_ELEMENT),X.__offset=b,b+=j.storage}}}const A=b%I;return A>0&&(b+=I-A),S.__size=b,S.__cache={},this}function v(S){const _={boundary:0,storage:0};return typeof S=="number"||typeof S=="boolean"?(_.boundary=4,_.storage=4):S.isVector2?(_.boundary=8,_.storage=8):S.isVector3||S.isColor?(_.boundary=16,_.storage=12):S.isVector4?(_.boundary=16,_.storage=16):S.isMatrix3?(_.boundary=48,_.storage=48):S.isMatrix4?(_.boundary=64,_.storage=64):S.isTexture?console.warn("THREE.WebGLRenderer: Texture samplers can not be part of an uniforms group."):console.warn("THREE.WebGLRenderer: Unsupported uniform value type.",S),_}function p(S){const _=S.target;_.removeEventListener("dispose",p);const b=a.indexOf(_.__bindingPointIndex);a.splice(b,1),i.deleteBuffer(s[_.id]),delete s[_.id],delete r[_.id]}function m(){for(const S in s)i.deleteBuffer(s[S]);a=[],s={},r={}}return{bind:l,update:c,dispose:m}}class MS{constructor(e={}){const{canvas:t=fv(),context:n=null,depth:s=!0,stencil:r=!1,alpha:a=!1,antialias:o=!1,premultipliedAlpha:l=!0,preserveDrawingBuffer:c=!1,powerPreference:h="default",failIfMajorPerformanceCaveat:u=!1}=e;this.isWebGLRenderer=!0;let d;if(n!==null){if(typeof WebGLRenderingContext<"u"&&n instanceof WebGLRenderingContext)throw new Error("THREE.WebGLRenderer: WebGL 1 is not supported since r163.");d=n.getContextAttributes().alpha}else d=a;const f=new Uint32Array(4),g=new Int32Array(4);let v=null,p=null;const m=[],S=[];this.domElement=t,this.debug={checkShaderErrors:!0,onShaderError:null},this.autoClear=!0,this.autoClearColor=!0,this.autoClearDepth=!0,this.autoClearStencil=!0,this.sortObjects=!0,this.clippingPlanes=[],this.localClippingEnabled=!1,this._outputColorSpace=Ui,this.toneMapping=Ss,this.toneMappingExposure=1;const _=this;let b=!1,I=0,A=0,R=null,N=-1,w=null;const y=new on,P=new on;let X=null;const H=new it(0);let J=0,q=t.width,ee=t.height,j=1,ne=null,ge=null;const de=new on(0,0,q,ee),ye=new on(0,0,q,ee);let Te=!1;const Se=new Zh;let ie=!1,he=!1;const be=new zt,fe=new V,ze=new on,We={background:null,fog:null,environment:null,overrideMaterial:null,isScene:!0};let Fe=!1;function mt(){return R===null?j:1}let F=n;function ft(C,W){return t.getContext(C,W)}try{const C={alpha:!0,depth:s,stencil:r,antialias:o,premultipliedAlpha:l,preserveDrawingBuffer:c,powerPreference:h,failIfMajorPerformanceCaveat:u};if("setAttribute"in t&&t.setAttribute("data-engine",`three.js r${Vh}`),t.addEventListener("webglcontextlost",se,!1),t.addEventListener("webglcontextrestored",re,!1),t.addEventListener("webglcontextcreationerror",_e,!1),F===null){const W="webgl2";if(F=ft(W,C),F===null)throw ft(W)?new Error("Error creating WebGL context with your selected attributes."):new Error("Error creating WebGL context.")}}catch(C){throw console.error("THREE.WebGLRenderer: "+C.message),C}let rt,ht,ke,Et,Ye,qe,U,T,Q,le,te,$,Ee,ve,Ce,Ze,me,Ae,Qe,He,we,Ve,B,ce;function O(){rt=new R_(F),rt.init(),Ve=new fS(F,rt),ht=new M_(F,rt,e,Ve),ke=new hS(F),Et=new D_(F),Ye=new Ky,qe=new dS(F,rt,ke,Ye,ht,Ve,Et),U=new E_(_),T=new C_(_),Q=new Bv(F),B=new S_(F,Q),le=new P_(F,Q,Et,B),te=new U_(F,le,Q,Et),Qe=new I_(F,ht,qe),Ze=new w_(Ye),$=new jy(_,U,T,rt,ht,B,Ze),Ee=new SS(_,Ye),ve=new Zy,Ce=new sS(rt),Ae=new y_(_,U,T,ke,te,d,l),me=new cS(_,te,ht),ce=new bS(F,Et,ht,ke),He=new b_(F,rt,Et),we=new L_(F,rt,Et),Et.programs=$.programs,_.capabilities=ht,_.extensions=rt,_.properties=Ye,_.renderLists=ve,_.shadowMap=me,_.state=ke,_.info=Et}O();const ae=new _S(_,F);this.xr=ae,this.getContext=function(){return F},this.getContextAttributes=function(){return F.getContextAttributes()},this.forceContextLoss=function(){const C=rt.get("WEBGL_lose_context");C&&C.loseContext()},this.forceContextRestore=function(){const C=rt.get("WEBGL_lose_context");C&&C.restoreContext()},this.getPixelRatio=function(){return j},this.setPixelRatio=function(C){C!==void 0&&(j=C,this.setSize(q,ee,!1))},this.getSize=function(C){return C.set(q,ee)},this.setSize=function(C,W,Z=!0){if(ae.isPresenting){console.warn("THREE.WebGLRenderer: Can't change size while VR device is presenting.");return}q=C,ee=W,t.width=Math.floor(C*j),t.height=Math.floor(W*j),Z===!0&&(t.style.width=C+"px",t.style.height=W+"px"),this.setViewport(0,0,C,W)},this.getDrawingBufferSize=function(C){return C.set(q*j,ee*j).floor()},this.setDrawingBufferSize=function(C,W,Z){q=C,ee=W,j=Z,t.width=Math.floor(C*Z),t.height=Math.floor(W*Z),this.setViewport(0,0,C,W)},this.getCurrentViewport=function(C){return C.copy(y)},this.getViewport=function(C){return C.copy(de)},this.setViewport=function(C,W,Z,Y){C.isVector4?de.set(C.x,C.y,C.z,C.w):de.set(C,W,Z,Y),ke.viewport(y.copy(de).multiplyScalar(j).round())},this.getScissor=function(C){return C.copy(ye)},this.setScissor=function(C,W,Z,Y){C.isVector4?ye.set(C.x,C.y,C.z,C.w):ye.set(C,W,Z,Y),ke.scissor(P.copy(ye).multiplyScalar(j).round())},this.getScissorTest=function(){return Te},this.setScissorTest=function(C){ke.setScissorTest(Te=C)},this.setOpaqueSort=function(C){ne=C},this.setTransparentSort=function(C){ge=C},this.getClearColor=function(C){return C.copy(Ae.getClearColor())},this.setClearColor=function(){Ae.setClearColor.apply(Ae,arguments)},this.getClearAlpha=function(){return Ae.getClearAlpha()},this.setClearAlpha=function(){Ae.setClearAlpha.apply(Ae,arguments)},this.clear=function(C=!0,W=!0,Z=!0){let Y=0;if(C){let G=!1;if(R!==null){const ue=R.texture.format;G=ue===Yh||ue===Xh||ue===qh}if(G){const ue=R.texture.type,Pe=ue===ss||ue===Zs||ue===Za||ue===ta||ue===Wh||ue===$h,Le=Ae.getClearColor(),Ne=Ae.getClearAlpha(),et=Le.r,tt=Le.g,Be=Le.b;Pe?(f[0]=et,f[1]=tt,f[2]=Be,f[3]=Ne,F.clearBufferuiv(F.COLOR,0,f)):(g[0]=et,g[1]=tt,g[2]=Be,g[3]=Ne,F.clearBufferiv(F.COLOR,0,g))}else Y|=F.COLOR_BUFFER_BIT}W&&(Y|=F.DEPTH_BUFFER_BIT),Z&&(Y|=F.STENCIL_BUFFER_BIT,this.state.buffers.stencil.setMask(4294967295)),F.clear(Y)},this.clearColor=function(){this.clear(!0,!1,!1)},this.clearDepth=function(){this.clear(!1,!0,!1)},this.clearStencil=function(){this.clear(!1,!1,!0)},this.dispose=function(){t.removeEventListener("webglcontextlost",se,!1),t.removeEventListener("webglcontextrestored",re,!1),t.removeEventListener("webglcontextcreationerror",_e,!1),ve.dispose(),Ce.dispose(),Ye.dispose(),U.dispose(),T.dispose(),te.dispose(),B.dispose(),ce.dispose(),$.dispose(),ae.dispose(),ae.removeEventListener("sessionstart",Ht),ae.removeEventListener("sessionend",Vt),un.stop()};function se(C){C.preventDefault(),console.log("THREE.WebGLRenderer: Context Lost."),b=!0}function re(){console.log("THREE.WebGLRenderer: Context Restored."),b=!1;const C=Et.autoReset,W=me.enabled,Z=me.autoUpdate,Y=me.needsUpdate,G=me.type;O(),Et.autoReset=C,me.enabled=W,me.autoUpdate=Z,me.needsUpdate=Y,me.type=G}function _e(C){console.error("THREE.WebGLRenderer: A WebGL context could not be created. Reason: ",C.statusMessage)}function Je(C){const W=C.target;W.removeEventListener("dispose",Je),lt(W)}function lt(C){xt(C),Ye.remove(C)}function xt(C){const W=Ye.get(C).programs;W!==void 0&&(W.forEach(function(Z){$.releaseProgram(Z)}),C.isShaderMaterial&&$.releaseShaderCache(C))}this.renderBufferDirect=function(C,W,Z,Y,G,ue){W===null&&(W=We);const Pe=G.isMesh&&G.matrixWorld.determinant()<0,Le=Hl(C,W,Z,Y,G);ke.setMaterial(Y,Pe);let Ne=Z.index,et=1;if(Y.wireframe===!0){if(Ne=le.getWireframeAttribute(Z),Ne===void 0)return;et=2}const tt=Z.drawRange,Be=Z.attributes.position;let ut=tt.start*et,Lt=(tt.start+tt.count)*et;ue!==null&&(ut=Math.max(ut,ue.start*et),Lt=Math.min(Lt,(ue.start+ue.count)*et)),Ne!==null?(ut=Math.max(ut,0),Lt=Math.min(Lt,Ne.count)):Be!=null&&(ut=Math.max(ut,0),Lt=Math.min(Lt,Be.count));const Dt=Lt-ut;if(Dt<0||Dt===1/0)return;B.setup(G,Y,Le,Z,Ne);let Sn,gt=He;if(Ne!==null&&(Sn=Q.get(Ne),gt=we,gt.setIndex(Sn)),G.isMesh)Y.wireframe===!0?(ke.setLineWidth(Y.wireframeLinewidth*mt()),gt.setMode(F.LINES)):gt.setMode(F.TRIANGLES);else if(G.isLine){let Ge=Y.linewidth;Ge===void 0&&(Ge=1),ke.setLineWidth(Ge*mt()),G.isLineSegments?gt.setMode(F.LINES):G.isLineLoop?gt.setMode(F.LINE_LOOP):gt.setMode(F.LINE_STRIP)}else G.isPoints?gt.setMode(F.POINTS):G.isSprite&&gt.setMode(F.TRIANGLES);if(G.isBatchedMesh)if(G._multiDrawInstances!==null)gt.renderMultiDrawInstances(G._multiDrawStarts,G._multiDrawCounts,G._multiDrawCount,G._multiDrawInstances);else if(rt.get("WEBGL_multi_draw"))gt.renderMultiDraw(G._multiDrawStarts,G._multiDrawCounts,G._multiDrawCount);else{const Ge=G._multiDrawStarts,Kt=G._multiDrawCounts,vt=G._multiDrawCount,It=Ne?Q.get(Ne).bytesPerElement:1,Vi=Ye.get(Y).currentProgram.getUniforms();for(let En=0;En<vt;En++)Vi.setValue(F,"_gl_DrawID",En),gt.render(Ge[En]/It,Kt[En])}else if(G.isInstancedMesh)gt.renderInstances(ut,Dt,G.count);else if(Z.isInstancedBufferGeometry){const Ge=Z._maxInstanceCount!==void 0?Z._maxInstanceCount:1/0,Kt=Math.min(Z.instanceCount,Ge);gt.renderInstances(ut,Dt,Kt)}else gt.render(ut,Dt)};function Tt(C,W,Z){C.transparent===!0&&C.side===Fn&&C.forceSinglePass===!1?(C.side=Vn,C.needsUpdate=!0,Ls(C,W,Z),C.side=Ms,C.needsUpdate=!0,Ls(C,W,Z),C.side=Fn):Ls(C,W,Z)}this.compile=function(C,W,Z=null){Z===null&&(Z=C),p=Ce.get(Z),p.init(W),S.push(p),Z.traverseVisible(function(G){G.isLight&&G.layers.test(W.layers)&&(p.pushLight(G),G.castShadow&&p.pushShadow(G))}),C!==Z&&C.traverseVisible(function(G){G.isLight&&G.layers.test(W.layers)&&(p.pushLight(G),G.castShadow&&p.pushShadow(G))}),p.setupLights();const Y=new Set;return C.traverse(function(G){const ue=G.material;if(ue)if(Array.isArray(ue))for(let Pe=0;Pe<ue.length;Pe++){const Le=ue[Pe];Tt(Le,Z,G),Y.add(Le)}else Tt(ue,Z,G),Y.add(ue)}),S.pop(),p=null,Y},this.compileAsync=function(C,W,Z=null){const Y=this.compile(C,W,Z);return new Promise(G=>{function ue(){if(Y.forEach(function(Pe){Ye.get(Pe).currentProgram.isReady()&&Y.delete(Pe)}),Y.size===0){G(C);return}setTimeout(ue,10)}rt.get("KHR_parallel_shader_compile")!==null?ue():setTimeout(ue,10)})};let ct=null;function yn(C){ct&&ct(C)}function Ht(){un.stop()}function Vt(){un.start()}const un=new Ep;un.setAnimationLoop(yn),typeof self<"u"&&un.setContext(self),this.setAnimationLoop=function(C){ct=C,ae.setAnimationLoop(C),C===null?un.stop():un.start()},ae.addEventListener("sessionstart",Ht),ae.addEventListener("sessionend",Vt),this.render=function(C,W){if(W!==void 0&&W.isCamera!==!0){console.error("THREE.WebGLRenderer.render: camera is not an instance of THREE.Camera.");return}if(b===!0)return;if(C.matrixWorldAutoUpdate===!0&&C.updateMatrixWorld(),W.parent===null&&W.matrixWorldAutoUpdate===!0&&W.updateMatrixWorld(),ae.enabled===!0&&ae.isPresenting===!0&&(ae.cameraAutoUpdate===!0&&ae.updateCamera(W),W=ae.getCamera()),C.isScene===!0&&C.onBeforeRender(_,C,W,R),p=Ce.get(C,S.length),p.init(W),S.push(p),be.multiplyMatrices(W.projectionMatrix,W.matrixWorldInverse),Se.setFromProjectionMatrix(be),he=this.localClippingEnabled,ie=Ze.init(this.clippingPlanes,he),v=ve.get(C,m.length),v.init(),m.push(v),ae.enabled===!0&&ae.isPresenting===!0){const ue=_.xr.getDepthSensingMesh();ue!==null&&Ai(ue,W,-1/0,_.sortObjects)}Ai(C,W,0,_.sortObjects),v.finish(),_.sortObjects===!0&&v.sort(ne,ge),Fe=ae.enabled===!1||ae.isPresenting===!1||ae.hasDepthSensing()===!1,Fe&&Ae.addToRenderList(v,C),this.info.render.frame++,ie===!0&&Ze.beginShadows();const Z=p.state.shadowsArray;me.render(Z,C,W),ie===!0&&Ze.endShadows(),this.info.autoReset===!0&&this.info.reset();const Y=v.opaque,G=v.transmissive;if(p.setupLights(),W.isArrayCamera){const ue=W.cameras;if(G.length>0)for(let Pe=0,Le=ue.length;Pe<Le;Pe++){const Ne=ue[Pe];Ln(Y,G,C,Ne)}Fe&&Ae.render(C);for(let Pe=0,Le=ue.length;Pe<Le;Pe++){const Ne=ue[Pe];Bi(v,C,Ne,Ne.viewport)}}else G.length>0&&Ln(Y,G,C,W),Fe&&Ae.render(C),Bi(v,C,W);R!==null&&(qe.updateMultisampleRenderTarget(R),qe.updateRenderTargetMipmap(R)),C.isScene===!0&&C.onAfterRender(_,C,W),B.resetDefaultState(),N=-1,w=null,S.pop(),S.length>0?(p=S[S.length-1],ie===!0&&Ze.setGlobalState(_.clippingPlanes,p.state.camera)):p=null,m.pop(),m.length>0?v=m[m.length-1]:v=null};function Ai(C,W,Z,Y){if(C.visible===!1)return;if(C.layers.test(W.layers)){if(C.isGroup)Z=C.renderOrder;else if(C.isLOD)C.autoUpdate===!0&&C.update(W);else if(C.isLight)p.pushLight(C),C.castShadow&&p.pushShadow(C);else if(C.isSprite){if(!C.frustumCulled||Se.intersectsSprite(C)){Y&&ze.setFromMatrixPosition(C.matrixWorld).applyMatrix4(be);const Pe=te.update(C),Le=C.material;Le.visible&&v.push(C,Pe,Le,Z,ze.z,null)}}else if((C.isMesh||C.isLine||C.isPoints)&&(!C.frustumCulled||Se.intersectsObject(C))){const Pe=te.update(C),Le=C.material;if(Y&&(C.boundingSphere!==void 0?(C.boundingSphere===null&&C.computeBoundingSphere(),ze.copy(C.boundingSphere.center)):(Pe.boundingSphere===null&&Pe.computeBoundingSphere(),ze.copy(Pe.boundingSphere.center)),ze.applyMatrix4(C.matrixWorld).applyMatrix4(be)),Array.isArray(Le)){const Ne=Pe.groups;for(let et=0,tt=Ne.length;et<tt;et++){const Be=Ne[et],ut=Le[Be.materialIndex];ut&&ut.visible&&v.push(C,Pe,ut,Z,ze.z,Be)}}else Le.visible&&v.push(C,Pe,Le,Z,ze.z,null)}}const ue=C.children;for(let Pe=0,Le=ue.length;Pe<Le;Pe++)Ai(ue[Pe],W,Z,Y)}function Bi(C,W,Z,Y){const G=C.opaque,ue=C.transmissive,Pe=C.transparent;p.setupLightsView(Z),ie===!0&&Ze.setGlobalState(_.clippingPlanes,Z),Y&&ke.viewport(y.copy(Y)),G.length>0&&ci(G,W,Z),ue.length>0&&ci(ue,W,Z),Pe.length>0&&ci(Pe,W,Z),ke.buffers.depth.setTest(!0),ke.buffers.depth.setMask(!0),ke.buffers.color.setMask(!0),ke.setPolygonOffset(!1)}function Ln(C,W,Z,Y){if((Z.isScene===!0?Z.overrideMaterial:null)!==null)return;p.state.transmissionRenderTarget[Y.id]===void 0&&(p.state.transmissionRenderTarget[Y.id]=new Qs(1,1,{generateMipmaps:!0,type:rt.has("EXT_color_buffer_half_float")||rt.has("EXT_color_buffer_float")?so:ss,minFilter:js,samples:4,stencilBuffer:r,resolveDepthBuffer:!1,resolveStencilBuffer:!1,colorSpace:wt.workingColorSpace}));const ue=p.state.transmissionRenderTarget[Y.id],Pe=Y.viewport||y;ue.setSize(Pe.z,Pe.w);const Le=_.getRenderTarget();_.setRenderTarget(ue),_.getClearColor(H),J=_.getClearAlpha(),J<1&&_.setClearColor(16777215,.5),_.clear(),Fe&&Ae.render(Z);const Ne=_.toneMapping;_.toneMapping=Ss;const et=Y.viewport;if(Y.viewport!==void 0&&(Y.viewport=void 0),p.setupLightsView(Y),ie===!0&&Ze.setGlobalState(_.clippingPlanes,Y),ci(C,Z,Y),qe.updateMultisampleRenderTarget(ue),qe.updateRenderTargetMipmap(ue),rt.has("WEBGL_multisampled_render_to_texture")===!1){let tt=!1;for(let Be=0,ut=W.length;Be<ut;Be++){const Lt=W[Be],Dt=Lt.object,Sn=Lt.geometry,gt=Lt.material,Ge=Lt.group;if(gt.side===Fn&&Dt.layers.test(Y.layers)){const Kt=gt.side;gt.side=Vn,gt.needsUpdate=!0,zi(Dt,Z,Y,Sn,gt,Ge),gt.side=Kt,gt.needsUpdate=!0,tt=!0}}tt===!0&&(qe.updateMultisampleRenderTarget(ue),qe.updateRenderTargetMipmap(ue))}_.setRenderTarget(Le),_.setClearColor(H,J),et!==void 0&&(Y.viewport=et),_.toneMapping=Ne}function ci(C,W,Z){const Y=W.isScene===!0?W.overrideMaterial:null;for(let G=0,ue=C.length;G<ue;G++){const Pe=C[G],Le=Pe.object,Ne=Pe.geometry,et=Y===null?Pe.material:Y,tt=Pe.group;Le.layers.test(Z.layers)&&zi(Le,W,Z,Ne,et,tt)}}function zi(C,W,Z,Y,G,ue){C.onBeforeRender(_,W,Z,Y,G,ue),C.modelViewMatrix.multiplyMatrices(Z.matrixWorldInverse,C.matrixWorld),C.normalMatrix.getNormalMatrix(C.modelViewMatrix),G.onBeforeRender(_,W,Z,Y,C,ue),G.transparent===!0&&G.side===Fn&&G.forceSinglePass===!1?(G.side=Vn,G.needsUpdate=!0,_.renderBufferDirect(Z,W,Y,G,C,ue),G.side=Ms,G.needsUpdate=!0,_.renderBufferDirect(Z,W,Y,G,C,ue),G.side=Fn):_.renderBufferDirect(Z,W,Y,G,C,ue),C.onAfterRender(_,W,Z,Y,G,ue)}function Ls(C,W,Z){W.isScene!==!0&&(W=We);const Y=Ye.get(C),G=p.state.lights,ue=p.state.shadowsArray,Pe=G.state.version,Le=$.getParameters(C,G.state,ue,W,Z),Ne=$.getProgramCacheKey(Le);let et=Y.programs;Y.environment=C.isMeshStandardMaterial?W.environment:null,Y.fog=W.fog,Y.envMap=(C.isMeshStandardMaterial?T:U).get(C.envMap||Y.environment),Y.envMapRotation=Y.environment!==null&&C.envMap===null?W.environmentRotation:C.envMapRotation,et===void 0&&(C.addEventListener("dispose",Je),et=new Map,Y.programs=et);let tt=et.get(Ne);if(tt!==void 0){if(Y.currentProgram===tt&&Y.lightsStateVersion===Pe)return ho(C,Le),tt}else Le.uniforms=$.getUniforms(C),C.onBeforeCompile(Le,_),tt=$.acquireProgram(Le,Ne),et.set(Ne,tt),Y.uniforms=Le.uniforms;const Be=Y.uniforms;return(!C.isShaderMaterial&&!C.isRawShaderMaterial||C.clipping===!0)&&(Be.clippingPlanes=Ze.uniform),ho(C,Le),Y.needsLights=Vl(C),Y.lightsStateVersion=Pe,Y.needsLights&&(Be.ambientLightColor.value=G.state.ambient,Be.lightProbe.value=G.state.probe,Be.directionalLights.value=G.state.directional,Be.directionalLightShadows.value=G.state.directionalShadow,Be.spotLights.value=G.state.spot,Be.spotLightShadows.value=G.state.spotShadow,Be.rectAreaLights.value=G.state.rectArea,Be.ltc_1.value=G.state.rectAreaLTC1,Be.ltc_2.value=G.state.rectAreaLTC2,Be.pointLights.value=G.state.point,Be.pointLightShadows.value=G.state.pointShadow,Be.hemisphereLights.value=G.state.hemi,Be.directionalShadowMap.value=G.state.directionalShadowMap,Be.directionalShadowMatrix.value=G.state.directionalShadowMatrix,Be.spotShadowMap.value=G.state.spotShadowMap,Be.spotLightMatrix.value=G.state.spotLightMatrix,Be.spotLightMap.value=G.state.spotLightMap,Be.pointShadowMap.value=G.state.pointShadowMap,Be.pointShadowMatrix.value=G.state.pointShadowMatrix),Y.currentProgram=tt,Y.uniformsList=null,tt}function Sa(C){if(C.uniformsList===null){const W=C.currentProgram.getUniforms();C.uniformsList=ol.seqWithValue(W.seq,C.uniforms)}return C.uniformsList}function ho(C,W){const Z=Ye.get(C);Z.outputColorSpace=W.outputColorSpace,Z.batching=W.batching,Z.batchingColor=W.batchingColor,Z.instancing=W.instancing,Z.instancingColor=W.instancingColor,Z.instancingMorph=W.instancingMorph,Z.skinning=W.skinning,Z.morphTargets=W.morphTargets,Z.morphNormals=W.morphNormals,Z.morphColors=W.morphColors,Z.morphTargetsCount=W.morphTargetsCount,Z.numClippingPlanes=W.numClippingPlanes,Z.numIntersection=W.numClipIntersection,Z.vertexAlphas=W.vertexAlphas,Z.vertexTangents=W.vertexTangents,Z.toneMapping=W.toneMapping}function Hl(C,W,Z,Y,G){W.isScene!==!0&&(W=We),qe.resetTextureUnits();const ue=W.fog,Pe=Y.isMeshStandardMaterial?W.environment:null,Le=R===null?_.outputColorSpace:R.isXRRenderTarget===!0?R.texture.colorSpace:Cs,Ne=(Y.isMeshStandardMaterial?T:U).get(Y.envMap||Pe),et=Y.vertexColors===!0&&!!Z.attributes.color&&Z.attributes.color.itemSize===4,tt=!!Z.attributes.tangent&&(!!Y.normalMap||Y.anisotropy>0),Be=!!Z.morphAttributes.position,ut=!!Z.morphAttributes.normal,Lt=!!Z.morphAttributes.color;let Dt=Ss;Y.toneMapped&&(R===null||R.isXRRenderTarget===!0)&&(Dt=_.toneMapping);const Sn=Z.morphAttributes.position||Z.morphAttributes.normal||Z.morphAttributes.color,gt=Sn!==void 0?Sn.length:0,Ge=Ye.get(Y),Kt=p.state.lights;if(ie===!0&&(he===!0||C!==w)){const zn=C===w&&Y.id===N;Ze.setState(Y,C,zn)}let vt=!1;Y.version===Ge.__version?(Ge.needsLights&&Ge.lightsStateVersion!==Kt.state.version||Ge.outputColorSpace!==Le||G.isBatchedMesh&&Ge.batching===!1||!G.isBatchedMesh&&Ge.batching===!0||G.isBatchedMesh&&Ge.batchingColor===!0&&G.colorTexture===null||G.isBatchedMesh&&Ge.batchingColor===!1&&G.colorTexture!==null||G.isInstancedMesh&&Ge.instancing===!1||!G.isInstancedMesh&&Ge.instancing===!0||G.isSkinnedMesh&&Ge.skinning===!1||!G.isSkinnedMesh&&Ge.skinning===!0||G.isInstancedMesh&&Ge.instancingColor===!0&&G.instanceColor===null||G.isInstancedMesh&&Ge.instancingColor===!1&&G.instanceColor!==null||G.isInstancedMesh&&Ge.instancingMorph===!0&&G.morphTexture===null||G.isInstancedMesh&&Ge.instancingMorph===!1&&G.morphTexture!==null||Ge.envMap!==Ne||Y.fog===!0&&Ge.fog!==ue||Ge.numClippingPlanes!==void 0&&(Ge.numClippingPlanes!==Ze.numPlanes||Ge.numIntersection!==Ze.numIntersection)||Ge.vertexAlphas!==et||Ge.vertexTangents!==tt||Ge.morphTargets!==Be||Ge.morphNormals!==ut||Ge.morphColors!==Lt||Ge.toneMapping!==Dt||Ge.morphTargetsCount!==gt)&&(vt=!0):(vt=!0,Ge.__version=Y.version);let It=Ge.currentProgram;vt===!0&&(It=Ls(Y,W,G));let Vi=!1,En=!1,Ds=!1;const Wt=It.getUniforms(),Ci=Ge.uniforms;if(ke.useProgram(It.program)&&(Vi=!0,En=!0,Ds=!0),Y.id!==N&&(N=Y.id,En=!0),Vi||w!==C){Wt.setValue(F,"projectionMatrix",C.projectionMatrix),Wt.setValue(F,"viewMatrix",C.matrixWorldInverse);const zn=Wt.map.cameraPosition;zn!==void 0&&zn.setValue(F,fe.setFromMatrixPosition(C.matrixWorld)),ht.logarithmicDepthBuffer&&Wt.setValue(F,"logDepthBufFC",2/(Math.log(C.far+1)/Math.LN2)),(Y.isMeshPhongMaterial||Y.isMeshToonMaterial||Y.isMeshLambertMaterial||Y.isMeshBasicMaterial||Y.isMeshStandardMaterial||Y.isShaderMaterial)&&Wt.setValue(F,"isOrthographic",C.isOrthographicCamera===!0),w!==C&&(w=C,En=!0,Ds=!0)}if(G.isSkinnedMesh){Wt.setOptional(F,G,"bindMatrix"),Wt.setOptional(F,G,"bindMatrixInverse");const zn=G.skeleton;zn&&(zn.boneTexture===null&&zn.computeBoneTexture(),Wt.setValue(F,"boneTexture",zn.boneTexture,qe))}G.isBatchedMesh&&(Wt.setOptional(F,G,"batchingTexture"),Wt.setValue(F,"batchingTexture",G._matricesTexture,qe),Wt.setOptional(F,G,"batchingIdTexture"),Wt.setValue(F,"batchingIdTexture",G._indirectTexture,qe),Wt.setOptional(F,G,"batchingColorTexture"),G._colorsTexture!==null&&Wt.setValue(F,"batchingColorTexture",G._colorsTexture,qe));const ba=Z.morphAttributes;if((ba.position!==void 0||ba.normal!==void 0||ba.color!==void 0)&&Qe.update(G,Z,It),(En||Ge.receiveShadow!==G.receiveShadow)&&(Ge.receiveShadow=G.receiveShadow,Wt.setValue(F,"receiveShadow",G.receiveShadow)),Y.isMeshGouraudMaterial&&Y.envMap!==null&&(Ci.envMap.value=Ne,Ci.flipEnvMap.value=Ne.isCubeTexture&&Ne.isRenderTargetTexture===!1?-1:1),Y.isMeshStandardMaterial&&Y.envMap===null&&W.environment!==null&&(Ci.envMapIntensity.value=W.environmentIntensity),En&&(Wt.setValue(F,"toneMappingExposure",_.toneMappingExposure),Ge.needsLights&&Hi(Ci,Ds),ue&&Y.fog===!0&&Ee.refreshFogUniforms(Ci,ue),Ee.refreshMaterialUniforms(Ci,Y,j,ee,p.state.transmissionRenderTarget[C.id]),ol.upload(F,Sa(Ge),Ci,qe)),Y.isShaderMaterial&&Y.uniformsNeedUpdate===!0&&(ol.upload(F,Sa(Ge),Ci,qe),Y.uniformsNeedUpdate=!1),Y.isSpriteMaterial&&Wt.setValue(F,"center",G.center),Wt.setValue(F,"modelViewMatrix",G.modelViewMatrix),Wt.setValue(F,"normalMatrix",G.normalMatrix),Wt.setValue(F,"modelMatrix",G.matrixWorld),Y.isShaderMaterial||Y.isRawShaderMaterial){const zn=Y.uniformsGroups;for(let ar=0,uo=zn.length;ar<uo;ar++){const fo=zn[ar];ce.update(fo,It),ce.bind(fo,It)}}return It}function Hi(C,W){C.ambientLightColor.needsUpdate=W,C.lightProbe.needsUpdate=W,C.directionalLights.needsUpdate=W,C.directionalLightShadows.needsUpdate=W,C.pointLights.needsUpdate=W,C.pointLightShadows.needsUpdate=W,C.spotLights.needsUpdate=W,C.spotLightShadows.needsUpdate=W,C.rectAreaLights.needsUpdate=W,C.hemisphereLights.needsUpdate=W}function Vl(C){return C.isMeshLambertMaterial||C.isMeshToonMaterial||C.isMeshPhongMaterial||C.isMeshStandardMaterial||C.isShadowMaterial||C.isShaderMaterial&&C.lights===!0}this.getActiveCubeFace=function(){return I},this.getActiveMipmapLevel=function(){return A},this.getRenderTarget=function(){return R},this.setRenderTargetTextures=function(C,W,Z){Ye.get(C.texture).__webglTexture=W,Ye.get(C.depthTexture).__webglTexture=Z;const Y=Ye.get(C);Y.__hasExternalTextures=!0,Y.__autoAllocateDepthBuffer=Z===void 0,Y.__autoAllocateDepthBuffer||rt.has("WEBGL_multisampled_render_to_texture")===!0&&(console.warn("THREE.WebGLRenderer: Render-to-texture extension was disabled because an external texture was provided"),Y.__useRenderToTexture=!1)},this.setRenderTargetFramebuffer=function(C,W){const Z=Ye.get(C);Z.__webglFramebuffer=W,Z.__useDefaultFramebuffer=W===void 0},this.setRenderTarget=function(C,W=0,Z=0){R=C,I=W,A=Z;let Y=!0,G=null,ue=!1,Pe=!1;if(C){const Ne=Ye.get(C);if(Ne.__useDefaultFramebuffer!==void 0)ke.bindFramebuffer(F.FRAMEBUFFER,null),Y=!1;else if(Ne.__webglFramebuffer===void 0)qe.setupRenderTarget(C);else if(Ne.__hasExternalTextures)qe.rebindTextures(C,Ye.get(C.texture).__webglTexture,Ye.get(C.depthTexture).__webglTexture);else if(C.depthBuffer){const Be=C.depthTexture;if(Ne.__boundDepthTexture!==Be){if(Be!==null&&Ye.has(Be)&&(C.width!==Be.image.width||C.height!==Be.image.height))throw new Error("WebGLRenderTarget: Attached DepthTexture is initialized to the incorrect size.");qe.setupDepthRenderbuffer(C)}}const et=C.texture;(et.isData3DTexture||et.isDataArrayTexture||et.isCompressedArrayTexture)&&(Pe=!0);const tt=Ye.get(C).__webglFramebuffer;C.isWebGLCubeRenderTarget?(Array.isArray(tt[W])?G=tt[W][Z]:G=tt[W],ue=!0):C.samples>0&&qe.useMultisampledRTT(C)===!1?G=Ye.get(C).__webglMultisampledFramebuffer:Array.isArray(tt)?G=tt[Z]:G=tt,y.copy(C.viewport),P.copy(C.scissor),X=C.scissorTest}else y.copy(de).multiplyScalar(j).floor(),P.copy(ye).multiplyScalar(j).floor(),X=Te;if(ke.bindFramebuffer(F.FRAMEBUFFER,G)&&Y&&ke.drawBuffers(C,G),ke.viewport(y),ke.scissor(P),ke.setScissorTest(X),ue){const Ne=Ye.get(C.texture);F.framebufferTexture2D(F.FRAMEBUFFER,F.COLOR_ATTACHMENT0,F.TEXTURE_CUBE_MAP_POSITIVE_X+W,Ne.__webglTexture,Z)}else if(Pe){const Ne=Ye.get(C.texture),et=W||0;F.framebufferTextureLayer(F.FRAMEBUFFER,F.COLOR_ATTACHMENT0,Ne.__webglTexture,Z||0,et)}N=-1},this.readRenderTargetPixels=function(C,W,Z,Y,G,ue,Pe){if(!(C&&C.isWebGLRenderTarget)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");return}let Le=Ye.get(C).__webglFramebuffer;if(C.isWebGLCubeRenderTarget&&Pe!==void 0&&(Le=Le[Pe]),Le){ke.bindFramebuffer(F.FRAMEBUFFER,Le);try{const Ne=C.texture,et=Ne.format,tt=Ne.type;if(!ht.textureFormatReadable(et)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in RGBA or implementation defined format.");return}if(!ht.textureTypeReadable(tt)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in UnsignedByteType or implementation defined type.");return}W>=0&&W<=C.width-Y&&Z>=0&&Z<=C.height-G&&F.readPixels(W,Z,Y,G,Ve.convert(et),Ve.convert(tt),ue)}finally{const Ne=R!==null?Ye.get(R).__webglFramebuffer:null;ke.bindFramebuffer(F.FRAMEBUFFER,Ne)}}},this.readRenderTargetPixelsAsync=async function(C,W,Z,Y,G,ue,Pe){if(!(C&&C.isWebGLRenderTarget))throw new Error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");let Le=Ye.get(C).__webglFramebuffer;if(C.isWebGLCubeRenderTarget&&Pe!==void 0&&(Le=Le[Pe]),Le){ke.bindFramebuffer(F.FRAMEBUFFER,Le);try{const Ne=C.texture,et=Ne.format,tt=Ne.type;if(!ht.textureFormatReadable(et))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in RGBA or implementation defined format.");if(!ht.textureTypeReadable(tt))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in UnsignedByteType or implementation defined type.");if(W>=0&&W<=C.width-Y&&Z>=0&&Z<=C.height-G){const Be=F.createBuffer();F.bindBuffer(F.PIXEL_PACK_BUFFER,Be),F.bufferData(F.PIXEL_PACK_BUFFER,ue.byteLength,F.STREAM_READ),F.readPixels(W,Z,Y,G,Ve.convert(et),Ve.convert(tt),0),F.flush();const ut=F.fenceSync(F.SYNC_GPU_COMMANDS_COMPLETE,0);await pv(F,ut,4);try{F.bindBuffer(F.PIXEL_PACK_BUFFER,Be),F.getBufferSubData(F.PIXEL_PACK_BUFFER,0,ue)}finally{F.deleteBuffer(Be),F.deleteSync(ut)}return ue}}finally{const Ne=R!==null?Ye.get(R).__webglFramebuffer:null;ke.bindFramebuffer(F.FRAMEBUFFER,Ne)}}},this.copyFramebufferToTexture=function(C,W=null,Z=0){C.isTexture!==!0&&(Yr("WebGLRenderer: copyFramebufferToTexture function signature has changed."),W=arguments[0]||null,C=arguments[1]);const Y=Math.pow(2,-Z),G=Math.floor(C.image.width*Y),ue=Math.floor(C.image.height*Y),Pe=W!==null?W.x:0,Le=W!==null?W.y:0;qe.setTexture2D(C,0),F.copyTexSubImage2D(F.TEXTURE_2D,Z,0,0,Pe,Le,G,ue),ke.unbindTexture()},this.copyTextureToTexture=function(C,W,Z=null,Y=null,G=0){C.isTexture!==!0&&(Yr("WebGLRenderer: copyTextureToTexture function signature has changed."),Y=arguments[0]||null,C=arguments[1],W=arguments[2],G=arguments[3]||0,Z=null);let ue,Pe,Le,Ne,et,tt;Z!==null?(ue=Z.max.x-Z.min.x,Pe=Z.max.y-Z.min.y,Le=Z.min.x,Ne=Z.min.y):(ue=C.image.width,Pe=C.image.height,Le=0,Ne=0),Y!==null?(et=Y.x,tt=Y.y):(et=0,tt=0);const Be=Ve.convert(W.format),ut=Ve.convert(W.type);qe.setTexture2D(W,0),F.pixelStorei(F.UNPACK_FLIP_Y_WEBGL,W.flipY),F.pixelStorei(F.UNPACK_PREMULTIPLY_ALPHA_WEBGL,W.premultiplyAlpha),F.pixelStorei(F.UNPACK_ALIGNMENT,W.unpackAlignment);const Lt=F.getParameter(F.UNPACK_ROW_LENGTH),Dt=F.getParameter(F.UNPACK_IMAGE_HEIGHT),Sn=F.getParameter(F.UNPACK_SKIP_PIXELS),gt=F.getParameter(F.UNPACK_SKIP_ROWS),Ge=F.getParameter(F.UNPACK_SKIP_IMAGES),Kt=C.isCompressedTexture?C.mipmaps[G]:C.image;F.pixelStorei(F.UNPACK_ROW_LENGTH,Kt.width),F.pixelStorei(F.UNPACK_IMAGE_HEIGHT,Kt.height),F.pixelStorei(F.UNPACK_SKIP_PIXELS,Le),F.pixelStorei(F.UNPACK_SKIP_ROWS,Ne),C.isDataTexture?F.texSubImage2D(F.TEXTURE_2D,G,et,tt,ue,Pe,Be,ut,Kt.data):C.isCompressedTexture?F.compressedTexSubImage2D(F.TEXTURE_2D,G,et,tt,Kt.width,Kt.height,Be,Kt.data):F.texSubImage2D(F.TEXTURE_2D,G,et,tt,ue,Pe,Be,ut,Kt),F.pixelStorei(F.UNPACK_ROW_LENGTH,Lt),F.pixelStorei(F.UNPACK_IMAGE_HEIGHT,Dt),F.pixelStorei(F.UNPACK_SKIP_PIXELS,Sn),F.pixelStorei(F.UNPACK_SKIP_ROWS,gt),F.pixelStorei(F.UNPACK_SKIP_IMAGES,Ge),G===0&&W.generateMipmaps&&F.generateMipmap(F.TEXTURE_2D),ke.unbindTexture()},this.copyTextureToTexture3D=function(C,W,Z=null,Y=null,G=0){C.isTexture!==!0&&(Yr("WebGLRenderer: copyTextureToTexture3D function signature has changed."),Z=arguments[0]||null,Y=arguments[1]||null,C=arguments[2],W=arguments[3],G=arguments[4]||0);let ue,Pe,Le,Ne,et,tt,Be,ut,Lt;const Dt=C.isCompressedTexture?C.mipmaps[G]:C.image;Z!==null?(ue=Z.max.x-Z.min.x,Pe=Z.max.y-Z.min.y,Le=Z.max.z-Z.min.z,Ne=Z.min.x,et=Z.min.y,tt=Z.min.z):(ue=Dt.width,Pe=Dt.height,Le=Dt.depth,Ne=0,et=0,tt=0),Y!==null?(Be=Y.x,ut=Y.y,Lt=Y.z):(Be=0,ut=0,Lt=0);const Sn=Ve.convert(W.format),gt=Ve.convert(W.type);let Ge;if(W.isData3DTexture)qe.setTexture3D(W,0),Ge=F.TEXTURE_3D;else if(W.isDataArrayTexture||W.isCompressedArrayTexture)qe.setTexture2DArray(W,0),Ge=F.TEXTURE_2D_ARRAY;else{console.warn("THREE.WebGLRenderer.copyTextureToTexture3D: only supports THREE.DataTexture3D and THREE.DataTexture2DArray.");return}F.pixelStorei(F.UNPACK_FLIP_Y_WEBGL,W.flipY),F.pixelStorei(F.UNPACK_PREMULTIPLY_ALPHA_WEBGL,W.premultiplyAlpha),F.pixelStorei(F.UNPACK_ALIGNMENT,W.unpackAlignment);const Kt=F.getParameter(F.UNPACK_ROW_LENGTH),vt=F.getParameter(F.UNPACK_IMAGE_HEIGHT),It=F.getParameter(F.UNPACK_SKIP_PIXELS),Vi=F.getParameter(F.UNPACK_SKIP_ROWS),En=F.getParameter(F.UNPACK_SKIP_IMAGES);F.pixelStorei(F.UNPACK_ROW_LENGTH,Dt.width),F.pixelStorei(F.UNPACK_IMAGE_HEIGHT,Dt.height),F.pixelStorei(F.UNPACK_SKIP_PIXELS,Ne),F.pixelStorei(F.UNPACK_SKIP_ROWS,et),F.pixelStorei(F.UNPACK_SKIP_IMAGES,tt),C.isDataTexture||C.isData3DTexture?F.texSubImage3D(Ge,G,Be,ut,Lt,ue,Pe,Le,Sn,gt,Dt.data):W.isCompressedArrayTexture?F.compressedTexSubImage3D(Ge,G,Be,ut,Lt,ue,Pe,Le,Sn,Dt.data):F.texSubImage3D(Ge,G,Be,ut,Lt,ue,Pe,Le,Sn,gt,Dt),F.pixelStorei(F.UNPACK_ROW_LENGTH,Kt),F.pixelStorei(F.UNPACK_IMAGE_HEIGHT,vt),F.pixelStorei(F.UNPACK_SKIP_PIXELS,It),F.pixelStorei(F.UNPACK_SKIP_ROWS,Vi),F.pixelStorei(F.UNPACK_SKIP_IMAGES,En),G===0&&W.generateMipmaps&&F.generateMipmap(Ge),ke.unbindTexture()},this.initRenderTarget=function(C){Ye.get(C).__webglFramebuffer===void 0&&qe.setupRenderTarget(C)},this.initTexture=function(C){C.isCubeTexture?qe.setTextureCube(C,0):C.isData3DTexture?qe.setTexture3D(C,0):C.isDataArrayTexture||C.isCompressedArrayTexture?qe.setTexture2DArray(C,0):qe.setTexture2D(C,0),ke.unbindTexture()},this.resetState=function(){I=0,A=0,R=null,ke.reset(),B.reset()},typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}get coordinateSystem(){return Zi}get outputColorSpace(){return this._outputColorSpace}set outputColorSpace(e){this._outputColorSpace=e;const t=this.getContext();t.drawingBufferColorSpace=e===jh?"display-p3":"srgb",t.unpackColorSpace=wt.workingColorSpace===Ml?"display-p3":"srgb"}}class eu{constructor(e,t=25e-5){this.isFogExp2=!0,this.name="",this.color=new it(e),this.density=t}clone(){return new eu(this.color,this.density)}toJSON(){return{type:"FogExp2",name:this.name,color:this.color.getHex(),density:this.density}}}class Lp extends sn{constructor(){super(),this.isScene=!0,this.type="Scene",this.background=null,this.environment=null,this.fog=null,this.backgroundBlurriness=0,this.backgroundIntensity=1,this.backgroundRotation=new Oi,this.environmentIntensity=1,this.environmentRotation=new Oi,this.overrideMaterial=null,typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}copy(e,t){return super.copy(e,t),e.background!==null&&(this.background=e.background.clone()),e.environment!==null&&(this.environment=e.environment.clone()),e.fog!==null&&(this.fog=e.fog.clone()),this.backgroundBlurriness=e.backgroundBlurriness,this.backgroundIntensity=e.backgroundIntensity,this.backgroundRotation.copy(e.backgroundRotation),this.environmentIntensity=e.environmentIntensity,this.environmentRotation.copy(e.environmentRotation),e.overrideMaterial!==null&&(this.overrideMaterial=e.overrideMaterial.clone()),this.matrixAutoUpdate=e.matrixAutoUpdate,this}toJSON(e){const t=super.toJSON(e);return this.fog!==null&&(t.object.fog=this.fog.toJSON()),this.backgroundBlurriness>0&&(t.object.backgroundBlurriness=this.backgroundBlurriness),this.backgroundIntensity!==1&&(t.object.backgroundIntensity=this.backgroundIntensity),t.object.backgroundRotation=this.backgroundRotation.toArray(),this.environmentIntensity!==1&&(t.object.environmentIntensity=this.environmentIntensity),t.object.environmentRotation=this.environmentRotation.toArray(),t}}class wS{constructor(e,t){this.isInterleavedBuffer=!0,this.array=e,this.stride=t,this.count=e!==void 0?e.length/t:0,this.usage=wh,this._updateRange={offset:0,count:-1},this.updateRanges=[],this.version=0,this.uuid=Qi()}onUploadCallback(){}set needsUpdate(e){e===!0&&this.version++}get updateRange(){return Yr("THREE.InterleavedBuffer: updateRange() is deprecated and will be removed in r169. Use addUpdateRange() instead."),this._updateRange}setUsage(e){return this.usage=e,this}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}copy(e){return this.array=new e.array.constructor(e.array),this.count=e.count,this.stride=e.stride,this.usage=e.usage,this}copyAt(e,t,n){e*=this.stride,n*=t.stride;for(let s=0,r=this.stride;s<r;s++)this.array[e+s]=t.array[n+s];return this}set(e,t=0){return this.array.set(e,t),this}clone(e){e.arrayBuffers===void 0&&(e.arrayBuffers={}),this.array.buffer._uuid===void 0&&(this.array.buffer._uuid=Qi()),e.arrayBuffers[this.array.buffer._uuid]===void 0&&(e.arrayBuffers[this.array.buffer._uuid]=this.array.slice(0).buffer);const t=new this.array.constructor(e.arrayBuffers[this.array.buffer._uuid]),n=new this.constructor(t,this.stride);return n.setUsage(this.usage),n}onUpload(e){return this.onUploadCallback=e,this}toJSON(e){return e.arrayBuffers===void 0&&(e.arrayBuffers={}),this.array.buffer._uuid===void 0&&(this.array.buffer._uuid=Qi()),e.arrayBuffers[this.array.buffer._uuid]===void 0&&(e.arrayBuffers[this.array.buffer._uuid]=Array.from(new Uint32Array(this.array.buffer))),{uuid:this.uuid,buffer:this.array.buffer._uuid,type:this.array.constructor.name,stride:this.stride}}}const Nn=new V;class ml{constructor(e,t,n,s=!1){this.isInterleavedBufferAttribute=!0,this.name="",this.data=e,this.itemSize=t,this.offset=n,this.normalized=s}get count(){return this.data.count}get array(){return this.data.array}set needsUpdate(e){this.data.needsUpdate=e}applyMatrix4(e){for(let t=0,n=this.data.count;t<n;t++)Nn.fromBufferAttribute(this,t),Nn.applyMatrix4(e),this.setXYZ(t,Nn.x,Nn.y,Nn.z);return this}applyNormalMatrix(e){for(let t=0,n=this.count;t<n;t++)Nn.fromBufferAttribute(this,t),Nn.applyNormalMatrix(e),this.setXYZ(t,Nn.x,Nn.y,Nn.z);return this}transformDirection(e){for(let t=0,n=this.count;t<n;t++)Nn.fromBufferAttribute(this,t),Nn.transformDirection(e),this.setXYZ(t,Nn.x,Nn.y,Nn.z);return this}getComponent(e,t){let n=this.array[e*this.data.stride+this.offset+t];return this.normalized&&(n=xi(n,this.array)),n}setComponent(e,t,n){return this.normalized&&(n=At(n,this.array)),this.data.array[e*this.data.stride+this.offset+t]=n,this}setX(e,t){return this.normalized&&(t=At(t,this.array)),this.data.array[e*this.data.stride+this.offset]=t,this}setY(e,t){return this.normalized&&(t=At(t,this.array)),this.data.array[e*this.data.stride+this.offset+1]=t,this}setZ(e,t){return this.normalized&&(t=At(t,this.array)),this.data.array[e*this.data.stride+this.offset+2]=t,this}setW(e,t){return this.normalized&&(t=At(t,this.array)),this.data.array[e*this.data.stride+this.offset+3]=t,this}getX(e){let t=this.data.array[e*this.data.stride+this.offset];return this.normalized&&(t=xi(t,this.array)),t}getY(e){let t=this.data.array[e*this.data.stride+this.offset+1];return this.normalized&&(t=xi(t,this.array)),t}getZ(e){let t=this.data.array[e*this.data.stride+this.offset+2];return this.normalized&&(t=xi(t,this.array)),t}getW(e){let t=this.data.array[e*this.data.stride+this.offset+3];return this.normalized&&(t=xi(t,this.array)),t}setXY(e,t,n){return e=e*this.data.stride+this.offset,this.normalized&&(t=At(t,this.array),n=At(n,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this}setXYZ(e,t,n,s){return e=e*this.data.stride+this.offset,this.normalized&&(t=At(t,this.array),n=At(n,this.array),s=At(s,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this.data.array[e+2]=s,this}setXYZW(e,t,n,s,r){return e=e*this.data.stride+this.offset,this.normalized&&(t=At(t,this.array),n=At(n,this.array),s=At(s,this.array),r=At(r,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this.data.array[e+2]=s,this.data.array[e+3]=r,this}clone(e){if(e===void 0){console.log("THREE.InterleavedBufferAttribute.clone(): Cloning an interleaved buffer attribute will de-interleave buffer data.");const t=[];for(let n=0;n<this.count;n++){const s=n*this.data.stride+this.offset;for(let r=0;r<this.itemSize;r++)t.push(this.data.array[s+r])}return new Mi(new this.array.constructor(t),this.itemSize,this.normalized)}else return e.interleavedBuffers===void 0&&(e.interleavedBuffers={}),e.interleavedBuffers[this.data.uuid]===void 0&&(e.interleavedBuffers[this.data.uuid]=this.data.clone(e)),new ml(e.interleavedBuffers[this.data.uuid],this.itemSize,this.offset,this.normalized)}toJSON(e){if(e===void 0){console.log("THREE.InterleavedBufferAttribute.toJSON(): Serializing an interleaved buffer attribute will de-interleave buffer data.");const t=[];for(let n=0;n<this.count;n++){const s=n*this.data.stride+this.offset;for(let r=0;r<this.itemSize;r++)t.push(this.data.array[s+r])}return{itemSize:this.itemSize,type:this.array.constructor.name,array:t,normalized:this.normalized}}else return e.interleavedBuffers===void 0&&(e.interleavedBuffers={}),e.interleavedBuffers[this.data.uuid]===void 0&&(e.interleavedBuffers[this.data.uuid]=this.data.toJSON(e)),{isInterleavedBufferAttribute:!0,itemSize:this.itemSize,data:this.data.uuid,offset:this.offset,normalized:this.normalized}}}class Ei extends Rs{constructor(e){super(),this.isSpriteMaterial=!0,this.type="SpriteMaterial",this.color=new it(16777215),this.map=null,this.alphaMap=null,this.rotation=0,this.sizeAttenuation=!0,this.transparent=!0,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.alphaMap=e.alphaMap,this.rotation=e.rotation,this.sizeAttenuation=e.sizeAttenuation,this.fog=e.fog,this}}let Nr;const Ia=new V,Or=new V,Fr=new V,kr=new Xe,Ua=new Xe,Dp=new zt,Ho=new V,Na=new V,Vo=new V,kd=new Xe,Ac=new Xe,Bd=new Xe;class Ip extends sn{constructor(e=new Ei){if(super(),this.isSprite=!0,this.type="Sprite",Nr===void 0){Nr=new Qt;const t=new Float32Array([-.5,-.5,0,0,0,.5,-.5,0,1,0,.5,.5,0,1,1,-.5,.5,0,0,1]),n=new wS(t,5);Nr.setIndex([0,1,2,0,2,3]),Nr.setAttribute("position",new ml(n,3,0,!1)),Nr.setAttribute("uv",new ml(n,2,3,!1))}this.geometry=Nr,this.material=e,this.center=new Xe(.5,.5)}raycast(e,t){e.camera===null&&console.error('THREE.Sprite: "Raycaster.camera" needs to be set in order to raycast against sprites.'),Or.setFromMatrixScale(this.matrixWorld),Dp.copy(e.camera.matrixWorld),this.modelViewMatrix.multiplyMatrices(e.camera.matrixWorldInverse,this.matrixWorld),Fr.setFromMatrixPosition(this.modelViewMatrix),e.camera.isPerspectiveCamera&&this.material.sizeAttenuation===!1&&Or.multiplyScalar(-Fr.z);const n=this.material.rotation;let s,r;n!==0&&(r=Math.cos(n),s=Math.sin(n));const a=this.center;Go(Ho.set(-.5,-.5,0),Fr,a,Or,s,r),Go(Na.set(.5,-.5,0),Fr,a,Or,s,r),Go(Vo.set(.5,.5,0),Fr,a,Or,s,r),kd.set(0,0),Ac.set(1,0),Bd.set(1,1);let o=e.ray.intersectTriangle(Ho,Na,Vo,!1,Ia);if(o===null&&(Go(Na.set(-.5,.5,0),Fr,a,Or,s,r),Ac.set(0,1),o=e.ray.intersectTriangle(Ho,Vo,Na,!1,Ia),o===null))return;const l=e.ray.origin.distanceTo(Ia);l<e.near||l>e.far||t.push({distance:l,point:Ia.clone(),uv:ri.getInterpolation(Ia,Ho,Na,Vo,kd,Ac,Bd,new Xe),face:null,object:this})}copy(e,t){return super.copy(e,t),e.center!==void 0&&this.center.copy(e.center),this.material=e.material,this}}function Go(i,e,t,n,s,r){kr.subVectors(i,t).addScalar(.5).multiply(n),s!==void 0?(Ua.x=r*kr.x-s*kr.y,Ua.y=s*kr.x+r*kr.y):Ua.copy(kr),i.copy(e),i.x+=Ua.x,i.y+=Ua.y,i.applyMatrix4(Dp)}class bs extends Rs{constructor(e){super(),this.isLineBasicMaterial=!0,this.type="LineBasicMaterial",this.color=new it(16777215),this.map=null,this.linewidth=1,this.linecap="round",this.linejoin="round",this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.linewidth=e.linewidth,this.linecap=e.linecap,this.linejoin=e.linejoin,this.fog=e.fog,this}}const gl=new V,vl=new V,zd=new zt,Oa=new oo,Wo=new ao,Cc=new V,Hd=new V;class Up extends sn{constructor(e=new Qt,t=new bs){super(),this.isLine=!0,this.type="Line",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}computeLineDistances(){const e=this.geometry;if(e.index===null){const t=e.attributes.position,n=[0];for(let s=1,r=t.count;s<r;s++)gl.fromBufferAttribute(t,s-1),vl.fromBufferAttribute(t,s),n[s]=n[s-1],n[s]+=gl.distanceTo(vl);e.setAttribute("lineDistance",new Ut(n,1))}else console.warn("THREE.Line.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.");return this}raycast(e,t){const n=this.geometry,s=this.matrixWorld,r=e.params.Line.threshold,a=n.drawRange;if(n.boundingSphere===null&&n.computeBoundingSphere(),Wo.copy(n.boundingSphere),Wo.applyMatrix4(s),Wo.radius+=r,e.ray.intersectsSphere(Wo)===!1)return;zd.copy(s).invert(),Oa.copy(e.ray).applyMatrix4(zd);const o=r/((this.scale.x+this.scale.y+this.scale.z)/3),l=o*o,c=this.isLineSegments?2:1,h=n.index,d=n.attributes.position;if(h!==null){const f=Math.max(0,a.start),g=Math.min(h.count,a.start+a.count);for(let v=f,p=g-1;v<p;v+=c){const m=h.getX(v),S=h.getX(v+1),_=$o(this,e,Oa,l,m,S);_&&t.push(_)}if(this.isLineLoop){const v=h.getX(g-1),p=h.getX(f),m=$o(this,e,Oa,l,v,p);m&&t.push(m)}}else{const f=Math.max(0,a.start),g=Math.min(d.count,a.start+a.count);for(let v=f,p=g-1;v<p;v+=c){const m=$o(this,e,Oa,l,v,v+1);m&&t.push(m)}if(this.isLineLoop){const v=$o(this,e,Oa,l,g-1,f);v&&t.push(v)}}}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const s=t[n[0]];if(s!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let r=0,a=s.length;r<a;r++){const o=s[r].name||String(r);this.morphTargetInfluences.push(0),this.morphTargetDictionary[o]=r}}}}}function $o(i,e,t,n,s,r){const a=i.geometry.attributes.position;if(gl.fromBufferAttribute(a,s),vl.fromBufferAttribute(a,r),t.distanceSqToSegment(gl,vl,Cc,Hd)>n)return;Cc.applyMatrix4(i.matrixWorld);const l=e.ray.origin.distanceTo(Cc);if(!(l<e.near||l>e.far))return{distance:l,point:Hd.clone().applyMatrix4(i.matrixWorld),index:s,face:null,faceIndex:null,object:i}}const Vd=new V,Gd=new V;class Kr extends Up{constructor(e,t){super(e,t),this.isLineSegments=!0,this.type="LineSegments"}computeLineDistances(){const e=this.geometry;if(e.index===null){const t=e.attributes.position,n=[];for(let s=0,r=t.count;s<r;s+=2)Vd.fromBufferAttribute(t,s),Gd.fromBufferAttribute(t,s+1),n[s]=s===0?0:n[s-1],n[s+1]=n[s]+Vd.distanceTo(Gd);e.setAttribute("lineDistance",new Ut(n,1))}else console.warn("THREE.LineSegments.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.");return this}}class Np extends Rs{constructor(e){super(),this.isPointsMaterial=!0,this.type="PointsMaterial",this.color=new it(16777215),this.map=null,this.alphaMap=null,this.size=1,this.sizeAttenuation=!0,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.alphaMap=e.alphaMap,this.size=e.size,this.sizeAttenuation=e.sizeAttenuation,this.fog=e.fog,this}}const Wd=new zt,Th=new oo,qo=new ao,Xo=new V;class ES extends sn{constructor(e=new Qt,t=new Np){super(),this.isPoints=!0,this.type="Points",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}raycast(e,t){const n=this.geometry,s=this.matrixWorld,r=e.params.Points.threshold,a=n.drawRange;if(n.boundingSphere===null&&n.computeBoundingSphere(),qo.copy(n.boundingSphere),qo.applyMatrix4(s),qo.radius+=r,e.ray.intersectsSphere(qo)===!1)return;Wd.copy(s).invert(),Th.copy(e.ray).applyMatrix4(Wd);const o=r/((this.scale.x+this.scale.y+this.scale.z)/3),l=o*o,c=n.index,u=n.attributes.position;if(c!==null){const d=Math.max(0,a.start),f=Math.min(c.count,a.start+a.count);for(let g=d,v=f;g<v;g++){const p=c.getX(g);Xo.fromBufferAttribute(u,p),$d(Xo,p,l,s,e,t,this)}}else{const d=Math.max(0,a.start),f=Math.min(u.count,a.start+a.count);for(let g=d,v=f;g<v;g++)Xo.fromBufferAttribute(u,g),$d(Xo,g,l,s,e,t,this)}}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const s=t[n[0]];if(s!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let r=0,a=s.length;r<a;r++){const o=s[r].name||String(r);this.morphTargetInfluences.push(0),this.morphTargetDictionary[o]=r}}}}}function $d(i,e,t,n,s,r,a){const o=Th.distanceSqToPoint(i);if(o<t){const l=new V;Th.closestPointToPoint(i,l),l.applyMatrix4(n);const c=s.ray.origin.distanceTo(l);if(c<s.near||c>s.far)return;r.push({distance:c,distanceToRay:Math.sqrt(o),point:l,index:e,face:null,object:a})}}class tu extends Bn{constructor(e,t,n,s,r,a,o,l,c){super(e,t,n,s,r,a,o,l,c),this.isCanvasTexture=!0,this.needsUpdate=!0}}const Yo=new V,jo=new V,Rc=new V,Ko=new ri;class TS extends Qt{constructor(e=null,t=1){if(super(),this.type="EdgesGeometry",this.parameters={geometry:e,thresholdAngle:t},e!==null){const s=Math.pow(10,4),r=Math.cos(Xr*t),a=e.getIndex(),o=e.getAttribute("position"),l=a?a.count:o.count,c=[0,0,0],h=["a","b","c"],u=new Array(3),d={},f=[];for(let g=0;g<l;g+=3){a?(c[0]=a.getX(g),c[1]=a.getX(g+1),c[2]=a.getX(g+2)):(c[0]=g,c[1]=g+1,c[2]=g+2);const{a:v,b:p,c:m}=Ko;if(v.fromBufferAttribute(o,c[0]),p.fromBufferAttribute(o,c[1]),m.fromBufferAttribute(o,c[2]),Ko.getNormal(Rc),u[0]=`${Math.round(v.x*s)},${Math.round(v.y*s)},${Math.round(v.z*s)}`,u[1]=`${Math.round(p.x*s)},${Math.round(p.y*s)},${Math.round(p.z*s)}`,u[2]=`${Math.round(m.x*s)},${Math.round(m.y*s)},${Math.round(m.z*s)}`,!(u[0]===u[1]||u[1]===u[2]||u[2]===u[0]))for(let S=0;S<3;S++){const _=(S+1)%3,b=u[S],I=u[_],A=Ko[h[S]],R=Ko[h[_]],N=`${b}_${I}`,w=`${I}_${b}`;w in d&&d[w]?(Rc.dot(d[w].normal)<=r&&(f.push(A.x,A.y,A.z),f.push(R.x,R.y,R.z)),d[w]=null):N in d||(d[N]={index0:c[S],index1:c[_],normal:Rc.clone()})}}for(const g in d)if(d[g]){const{index0:v,index1:p}=d[g];Yo.fromBufferAttribute(o,v),jo.fromBufferAttribute(o,p),f.push(Yo.x,Yo.y,Yo.z),f.push(jo.x,jo.y,jo.z)}this.setAttribute("position",new Ut(f,3))}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}}class nu extends Qt{constructor(e=.5,t=1,n=32,s=1,r=0,a=Math.PI*2){super(),this.type="RingGeometry",this.parameters={innerRadius:e,outerRadius:t,thetaSegments:n,phiSegments:s,thetaStart:r,thetaLength:a},n=Math.max(3,n),s=Math.max(1,s);const o=[],l=[],c=[],h=[];let u=e;const d=(t-e)/s,f=new V,g=new Xe;for(let v=0;v<=s;v++){for(let p=0;p<=n;p++){const m=r+p/n*a;f.x=u*Math.cos(m),f.y=u*Math.sin(m),l.push(f.x,f.y,f.z),c.push(0,0,1),g.x=(f.x/t+1)/2,g.y=(f.y/t+1)/2,h.push(g.x,g.y)}u+=d}for(let v=0;v<s;v++){const p=v*(n+1);for(let m=0;m<n;m++){const S=m+p,_=S,b=S+n+1,I=S+n+2,A=S+1;o.push(_,b,A),o.push(b,I,A)}}this.setIndex(o),this.setAttribute("position",new Ut(l,3)),this.setAttribute("normal",new Ut(c,3)),this.setAttribute("uv",new Ut(h,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new nu(e.innerRadius,e.outerRadius,e.thetaSegments,e.phiSegments,e.thetaStart,e.thetaLength)}}class Jr extends Rs{constructor(e){super(),this.isMeshStandardMaterial=!0,this.defines={STANDARD:""},this.type="MeshStandardMaterial",this.color=new it(16777215),this.roughness=1,this.metalness=0,this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.emissive=new it(0),this.emissiveIntensity=1,this.emissiveMap=null,this.bumpMap=null,this.bumpScale=1,this.normalMap=null,this.normalMapType=pp,this.normalScale=new Xe(1,1),this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.roughnessMap=null,this.metalnessMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new Oi,this.envMapIntensity=1,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.flatShading=!1,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.defines={STANDARD:""},this.color.copy(e.color),this.roughness=e.roughness,this.metalness=e.metalness,this.map=e.map,this.lightMap=e.lightMap,this.lightMapIntensity=e.lightMapIntensity,this.aoMap=e.aoMap,this.aoMapIntensity=e.aoMapIntensity,this.emissive.copy(e.emissive),this.emissiveMap=e.emissiveMap,this.emissiveIntensity=e.emissiveIntensity,this.bumpMap=e.bumpMap,this.bumpScale=e.bumpScale,this.normalMap=e.normalMap,this.normalMapType=e.normalMapType,this.normalScale.copy(e.normalScale),this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this.roughnessMap=e.roughnessMap,this.metalnessMap=e.metalnessMap,this.alphaMap=e.alphaMap,this.envMap=e.envMap,this.envMapRotation.copy(e.envMapRotation),this.envMapIntensity=e.envMapIntensity,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.wireframeLinecap=e.wireframeLinecap,this.wireframeLinejoin=e.wireframeLinejoin,this.flatShading=e.flatShading,this.fog=e.fog,this}}class AS extends bs{constructor(e){super(),this.isLineDashedMaterial=!0,this.type="LineDashedMaterial",this.scale=1,this.dashSize=3,this.gapSize=1,this.setValues(e)}copy(e){return super.copy(e),this.scale=e.scale,this.dashSize=e.dashSize,this.gapSize=e.gapSize,this}}class iu extends sn{constructor(e,t=1){super(),this.isLight=!0,this.type="Light",this.color=new it(e),this.intensity=t}dispose(){}copy(e,t){return super.copy(e,t),this.color.copy(e.color),this.intensity=e.intensity,this}toJSON(e){const t=super.toJSON(e);return t.object.color=this.color.getHex(),t.object.intensity=this.intensity,this.groundColor!==void 0&&(t.object.groundColor=this.groundColor.getHex()),this.distance!==void 0&&(t.object.distance=this.distance),this.angle!==void 0&&(t.object.angle=this.angle),this.decay!==void 0&&(t.object.decay=this.decay),this.penumbra!==void 0&&(t.object.penumbra=this.penumbra),this.shadow!==void 0&&(t.object.shadow=this.shadow.toJSON()),this.target!==void 0&&(t.object.target=this.target.uuid),t}}class CS extends iu{constructor(e,t,n){super(e,n),this.isHemisphereLight=!0,this.type="HemisphereLight",this.position.copy(sn.DEFAULT_UP),this.updateMatrix(),this.groundColor=new it(t)}copy(e,t){return super.copy(e,t),this.groundColor.copy(e.groundColor),this}}const Pc=new zt,qd=new V,Xd=new V;class RS{constructor(e){this.camera=e,this.intensity=1,this.bias=0,this.normalBias=0,this.radius=1,this.blurSamples=8,this.mapSize=new Xe(512,512),this.map=null,this.mapPass=null,this.matrix=new zt,this.autoUpdate=!0,this.needsUpdate=!1,this._frustum=new Zh,this._frameExtents=new Xe(1,1),this._viewportCount=1,this._viewports=[new on(0,0,1,1)]}getViewportCount(){return this._viewportCount}getFrustum(){return this._frustum}updateMatrices(e){const t=this.camera,n=this.matrix;qd.setFromMatrixPosition(e.matrixWorld),t.position.copy(qd),Xd.setFromMatrixPosition(e.target.matrixWorld),t.lookAt(Xd),t.updateMatrixWorld(),Pc.multiplyMatrices(t.projectionMatrix,t.matrixWorldInverse),this._frustum.setFromProjectionMatrix(Pc),n.set(.5,0,0,.5,0,.5,0,.5,0,0,.5,.5,0,0,0,1),n.multiply(Pc)}getViewport(e){return this._viewports[e]}getFrameExtents(){return this._frameExtents}dispose(){this.map&&this.map.dispose(),this.mapPass&&this.mapPass.dispose()}copy(e){return this.camera=e.camera.clone(),this.intensity=e.intensity,this.bias=e.bias,this.radius=e.radius,this.mapSize.copy(e.mapSize),this}clone(){return new this.constructor().copy(this)}toJSON(){const e={};return this.intensity!==1&&(e.intensity=this.intensity),this.bias!==0&&(e.bias=this.bias),this.normalBias!==0&&(e.normalBias=this.normalBias),this.radius!==1&&(e.radius=this.radius),(this.mapSize.x!==512||this.mapSize.y!==512)&&(e.mapSize=this.mapSize.toArray()),e.camera=this.camera.toJSON(!1).object,delete e.camera.matrix,e}}class PS extends RS{constructor(){super(new Xa(-5,5,5,-5,.5,500)),this.isDirectionalLightShadow=!0}}class LS extends iu{constructor(e,t){super(e,t),this.isDirectionalLight=!0,this.type="DirectionalLight",this.position.copy(sn.DEFAULT_UP),this.updateMatrix(),this.target=new sn,this.shadow=new PS}dispose(){this.shadow.dispose()}copy(e){return super.copy(e),this.target=e.target.clone(),this.shadow=e.shadow.clone(),this}}class DS extends iu{constructor(e,t){super(e,t),this.isAmbientLight=!0,this.type="AmbientLight"}}const Yd=new zt;class IS{constructor(e,t,n=0,s=1/0){this.ray=new oo(e,t),this.near=n,this.far=s,this.camera=null,this.layers=new Jh,this.params={Mesh:{},Line:{threshold:1},LOD:{},Points:{threshold:1},Sprite:{}}}set(e,t){this.ray.set(e,t)}setFromCamera(e,t){t.isPerspectiveCamera?(this.ray.origin.setFromMatrixPosition(t.matrixWorld),this.ray.direction.set(e.x,e.y,.5).unproject(t).sub(this.ray.origin).normalize(),this.camera=t):t.isOrthographicCamera?(this.ray.origin.set(e.x,e.y,(t.near+t.far)/(t.near-t.far)).unproject(t),this.ray.direction.set(0,0,-1).transformDirection(t.matrixWorld),this.camera=t):console.error("THREE.Raycaster: Unsupported camera type: "+t.type)}setFromXRController(e){return Yd.identity().extractRotation(e.matrixWorld),this.ray.origin.setFromMatrixPosition(e.matrixWorld),this.ray.direction.set(0,0,-1).applyMatrix4(Yd),this}intersectObject(e,t=!0,n=[]){return Ah(e,this,n,t),n.sort(jd),n}intersectObjects(e,t=!0,n=[]){for(let s=0,r=e.length;s<r;s++)Ah(e[s],this,n,t);return n.sort(jd),n}}function jd(i,e){return i.distance-e.distance}function Ah(i,e,t,n){let s=!0;if(i.layers.test(e.layers)&&i.raycast(e,t)===!1&&(s=!1),s===!0&&n===!0){const r=i.children;for(let a=0,o=r.length;a<o;a++)Ah(r[a],e,t,!0)}}class Kd{constructor(e=1,t=0,n=0){return this.radius=e,this.phi=t,this.theta=n,this}set(e,t,n){return this.radius=e,this.phi=t,this.theta=n,this}copy(e){return this.radius=e.radius,this.phi=e.phi,this.theta=e.theta,this}makeSafe(){return this.phi=Math.max(1e-6,Math.min(Math.PI-1e-6,this.phi)),this}setFromVector3(e){return this.setFromCartesianCoords(e.x,e.y,e.z)}setFromCartesianCoords(e,t,n){return this.radius=Math.sqrt(e*e+t*t+n*n),this.radius===0?(this.theta=0,this.phi=0):(this.theta=Math.atan2(e,n),this.phi=Math.acos(Cn(t/this.radius,-1,1))),this}clone(){return new this.constructor().copy(this)}}class US extends Kr{constructor(e=10,t=10,n=4473924,s=8947848){n=new it(n),s=new it(s);const r=t/2,a=e/t,o=e/2,l=[],c=[];for(let d=0,f=0,g=-o;d<=t;d++,g+=a){l.push(-o,0,g,o,0,g),l.push(g,0,-o,g,0,o);const v=d===r?n:s;v.toArray(c,f),f+=3,v.toArray(c,f),f+=3,v.toArray(c,f),f+=3,v.toArray(c,f),f+=3}const h=new Qt;h.setAttribute("position",new Ut(l,3)),h.setAttribute("color",new Ut(c,3));const u=new bs({vertexColors:!0,toneMapped:!1});super(h,u),this.type="GridHelper"}dispose(){this.geometry.dispose(),this.material.dispose()}}typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("register",{detail:{revision:Vh}}));typeof window<"u"&&(window.__THREE__?console.warn("WARNING: Multiple instances of Three.js being imported."):window.__THREE__=Vh);var NS=Object.defineProperty,OS=(i,e,t)=>e in i?NS(i,e,{enumerable:!0,configurable:!0,writable:!0,value:t}):i[e]=t,FS=(i,e,t)=>(OS(i,e+"",t),t);class kS{constructor(){FS(this,"_listeners")}addEventListener(e,t){this._listeners===void 0&&(this._listeners={});const n=this._listeners;n[e]===void 0&&(n[e]=[]),n[e].indexOf(t)===-1&&n[e].push(t)}hasEventListener(e,t){if(this._listeners===void 0)return!1;const n=this._listeners;return n[e]!==void 0&&n[e].indexOf(t)!==-1}removeEventListener(e,t){if(this._listeners===void 0)return;const s=this._listeners[e];if(s!==void 0){const r=s.indexOf(t);r!==-1&&s.splice(r,1)}}dispatchEvent(e){if(this._listeners===void 0)return;const n=this._listeners[e.type];if(n!==void 0){e.target=this;const s=n.slice(0);for(let r=0,a=s.length;r<a;r++)s[r].call(this,e);e.target=null}}}var BS=Object.defineProperty,zS=(i,e,t)=>e in i?BS(i,e,{enumerable:!0,configurable:!0,writable:!0,value:t}):i[e]=t,je=(i,e,t)=>(zS(i,typeof e!="symbol"?e+"":e,t),t);const Jo=new oo,Jd=new vs,HS=Math.cos(70*(Math.PI/180)),Zd=(i,e)=>(i%e+e)%e;class VS extends kS{constructor(e,t){super(),je(this,"object"),je(this,"domElement"),je(this,"enabled",!0),je(this,"target",new V),je(this,"minDistance",0),je(this,"maxDistance",1/0),je(this,"minZoom",0),je(this,"maxZoom",1/0),je(this,"minPolarAngle",0),je(this,"maxPolarAngle",Math.PI),je(this,"minAzimuthAngle",-1/0),je(this,"maxAzimuthAngle",1/0),je(this,"enableDamping",!1),je(this,"dampingFactor",.05),je(this,"enableZoom",!0),je(this,"zoomSpeed",1),je(this,"enableRotate",!0),je(this,"rotateSpeed",1),je(this,"enablePan",!0),je(this,"panSpeed",1),je(this,"screenSpacePanning",!0),je(this,"keyPanSpeed",7),je(this,"zoomToCursor",!1),je(this,"autoRotate",!1),je(this,"autoRotateSpeed",2),je(this,"reverseOrbit",!1),je(this,"reverseHorizontalOrbit",!1),je(this,"reverseVerticalOrbit",!1),je(this,"keys",{LEFT:"ArrowLeft",UP:"ArrowUp",RIGHT:"ArrowRight",BOTTOM:"ArrowDown"}),je(this,"mouseButtons",{LEFT:gr.ROTATE,MIDDLE:gr.DOLLY,RIGHT:gr.PAN}),je(this,"touches",{ONE:vr.ROTATE,TWO:vr.DOLLY_PAN}),je(this,"target0"),je(this,"position0"),je(this,"zoom0"),je(this,"_domElementKeyEvents",null),je(this,"getPolarAngle"),je(this,"getAzimuthalAngle"),je(this,"setPolarAngle"),je(this,"setAzimuthalAngle"),je(this,"getDistance"),je(this,"getZoomScale"),je(this,"listenToKeyEvents"),je(this,"stopListenToKeyEvents"),je(this,"saveState"),je(this,"reset"),je(this,"update"),je(this,"connect"),je(this,"dispose"),je(this,"dollyIn"),je(this,"dollyOut"),je(this,"getScale"),je(this,"setScale"),this.object=e,this.domElement=t,this.target0=this.target.clone(),this.position0=this.object.position.clone(),this.zoom0=this.object.zoom,this.getPolarAngle=()=>h.phi,this.getAzimuthalAngle=()=>h.theta,this.setPolarAngle=B=>{let ce=Zd(B,2*Math.PI),O=h.phi;O<0&&(O+=2*Math.PI),ce<0&&(ce+=2*Math.PI);let ae=Math.abs(ce-O);2*Math.PI-ae<ae&&(ce<O?ce+=2*Math.PI:O+=2*Math.PI),u.phi=ce-O,n.update()},this.setAzimuthalAngle=B=>{let ce=Zd(B,2*Math.PI),O=h.theta;O<0&&(O+=2*Math.PI),ce<0&&(ce+=2*Math.PI);let ae=Math.abs(ce-O);2*Math.PI-ae<ae&&(ce<O?ce+=2*Math.PI:O+=2*Math.PI),u.theta=ce-O,n.update()},this.getDistance=()=>n.object.position.distanceTo(n.target),this.listenToKeyEvents=B=>{B.addEventListener("keydown",Ce),this._domElementKeyEvents=B},this.stopListenToKeyEvents=()=>{this._domElementKeyEvents.removeEventListener("keydown",Ce),this._domElementKeyEvents=null},this.saveState=()=>{n.target0.copy(n.target),n.position0.copy(n.object.position),n.zoom0=n.object.zoom},this.reset=()=>{n.target.copy(n.target0),n.object.position.copy(n.position0),n.object.zoom=n.zoom0,n.object.updateProjectionMatrix(),n.dispatchEvent(s),n.update(),l=o.NONE},this.update=(()=>{const B=new V,ce=new V(0,1,0),O=new er().setFromUnitVectors(e.up,ce),ae=O.clone().invert(),se=new V,re=new er,_e=2*Math.PI;return function(){const lt=n.object.position;O.setFromUnitVectors(e.up,ce),ae.copy(O).invert(),B.copy(lt).sub(n.target),B.applyQuaternion(O),h.setFromVector3(B),n.autoRotate&&l===o.NONE&&J(X()),n.enableDamping?(h.theta+=u.theta*n.dampingFactor,h.phi+=u.phi*n.dampingFactor):(h.theta+=u.theta,h.phi+=u.phi);let xt=n.minAzimuthAngle,Tt=n.maxAzimuthAngle;isFinite(xt)&&isFinite(Tt)&&(xt<-Math.PI?xt+=_e:xt>Math.PI&&(xt-=_e),Tt<-Math.PI?Tt+=_e:Tt>Math.PI&&(Tt-=_e),xt<=Tt?h.theta=Math.max(xt,Math.min(Tt,h.theta)):h.theta=h.theta>(xt+Tt)/2?Math.max(xt,h.theta):Math.min(Tt,h.theta)),h.phi=Math.max(n.minPolarAngle,Math.min(n.maxPolarAngle,h.phi)),h.makeSafe(),n.enableDamping===!0?n.target.addScaledVector(f,n.dampingFactor):n.target.add(f),n.zoomToCursor&&w||n.object.isOrthographicCamera?h.radius=Se(h.radius):h.radius=Se(h.radius*d),B.setFromSpherical(h),B.applyQuaternion(ae),lt.copy(n.target).add(B),n.object.matrixAutoUpdate||n.object.updateMatrix(),n.object.lookAt(n.target),n.enableDamping===!0?(u.theta*=1-n.dampingFactor,u.phi*=1-n.dampingFactor,f.multiplyScalar(1-n.dampingFactor)):(u.set(0,0,0),f.set(0,0,0));let ct=!1;if(n.zoomToCursor&&w){let yn=null;if(n.object instanceof Rn&&n.object.isPerspectiveCamera){const Ht=B.length();yn=Se(Ht*d);const Vt=Ht-yn;n.object.position.addScaledVector(R,Vt),n.object.updateMatrixWorld()}else if(n.object.isOrthographicCamera){const Ht=new V(N.x,N.y,0);Ht.unproject(n.object),n.object.zoom=Math.max(n.minZoom,Math.min(n.maxZoom,n.object.zoom/d)),n.object.updateProjectionMatrix(),ct=!0;const Vt=new V(N.x,N.y,0);Vt.unproject(n.object),n.object.position.sub(Vt).add(Ht),n.object.updateMatrixWorld(),yn=B.length()}else console.warn("WARNING: OrbitControls.js encountered an unknown camera type - zoom to cursor disabled."),n.zoomToCursor=!1;yn!==null&&(n.screenSpacePanning?n.target.set(0,0,-1).transformDirection(n.object.matrix).multiplyScalar(yn).add(n.object.position):(Jo.origin.copy(n.object.position),Jo.direction.set(0,0,-1).transformDirection(n.object.matrix),Math.abs(n.object.up.dot(Jo.direction))<HS?e.lookAt(n.target):(Jd.setFromNormalAndCoplanarPoint(n.object.up,n.target),Jo.intersectPlane(Jd,n.target))))}else n.object instanceof Xa&&n.object.isOrthographicCamera&&(ct=d!==1,ct&&(n.object.zoom=Math.max(n.minZoom,Math.min(n.maxZoom,n.object.zoom/d)),n.object.updateProjectionMatrix()));return d=1,w=!1,ct||se.distanceToSquared(n.object.position)>c||8*(1-re.dot(n.object.quaternion))>c?(n.dispatchEvent(s),se.copy(n.object.position),re.copy(n.object.quaternion),ct=!1,!0):!1}})(),this.connect=B=>{n.domElement=B,n.domElement.style.touchAction="none",n.domElement.addEventListener("contextmenu",Ae),n.domElement.addEventListener("pointerdown",Q),n.domElement.addEventListener("pointercancel",te),n.domElement.addEventListener("wheel",ve)},this.dispose=()=>{var B,ce,O,ae,se,re;n.domElement&&(n.domElement.style.touchAction="auto"),(B=n.domElement)==null||B.removeEventListener("contextmenu",Ae),(ce=n.domElement)==null||ce.removeEventListener("pointerdown",Q),(O=n.domElement)==null||O.removeEventListener("pointercancel",te),(ae=n.domElement)==null||ae.removeEventListener("wheel",ve),(se=n.domElement)==null||se.ownerDocument.removeEventListener("pointermove",le),(re=n.domElement)==null||re.ownerDocument.removeEventListener("pointerup",te),n._domElementKeyEvents!==null&&n._domElementKeyEvents.removeEventListener("keydown",Ce)};const n=this,s={type:"change"},r={type:"start"},a={type:"end"},o={NONE:-1,ROTATE:0,DOLLY:1,PAN:2,TOUCH_ROTATE:3,TOUCH_PAN:4,TOUCH_DOLLY_PAN:5,TOUCH_DOLLY_ROTATE:6};let l=o.NONE;const c=1e-6,h=new Kd,u=new Kd;let d=1;const f=new V,g=new Xe,v=new Xe,p=new Xe,m=new Xe,S=new Xe,_=new Xe,b=new Xe,I=new Xe,A=new Xe,R=new V,N=new Xe;let w=!1;const y=[],P={};function X(){return 2*Math.PI/60/60*n.autoRotateSpeed}function H(){return Math.pow(.95,n.zoomSpeed)}function J(B){n.reverseOrbit||n.reverseHorizontalOrbit?u.theta+=B:u.theta-=B}function q(B){n.reverseOrbit||n.reverseVerticalOrbit?u.phi+=B:u.phi-=B}const ee=(()=>{const B=new V;return function(O,ae){B.setFromMatrixColumn(ae,0),B.multiplyScalar(-O),f.add(B)}})(),j=(()=>{const B=new V;return function(O,ae){n.screenSpacePanning===!0?B.setFromMatrixColumn(ae,1):(B.setFromMatrixColumn(ae,0),B.crossVectors(n.object.up,B)),B.multiplyScalar(O),f.add(B)}})(),ne=(()=>{const B=new V;return function(O,ae){const se=n.domElement;if(se&&n.object instanceof Rn&&n.object.isPerspectiveCamera){const re=n.object.position;B.copy(re).sub(n.target);let _e=B.length();_e*=Math.tan(n.object.fov/2*Math.PI/180),ee(2*O*_e/se.clientHeight,n.object.matrix),j(2*ae*_e/se.clientHeight,n.object.matrix)}else se&&n.object instanceof Xa&&n.object.isOrthographicCamera?(ee(O*(n.object.right-n.object.left)/n.object.zoom/se.clientWidth,n.object.matrix),j(ae*(n.object.top-n.object.bottom)/n.object.zoom/se.clientHeight,n.object.matrix)):(console.warn("WARNING: OrbitControls.js encountered an unknown camera type - pan disabled."),n.enablePan=!1)}})();function ge(B){n.object instanceof Rn&&n.object.isPerspectiveCamera||n.object instanceof Xa&&n.object.isOrthographicCamera?d=B:(console.warn("WARNING: OrbitControls.js encountered an unknown camera type - dolly/zoom disabled."),n.enableZoom=!1)}function de(B){ge(d/B)}function ye(B){ge(d*B)}function Te(B){if(!n.zoomToCursor||!n.domElement)return;w=!0;const ce=n.domElement.getBoundingClientRect(),O=B.clientX-ce.left,ae=B.clientY-ce.top,se=ce.width,re=ce.height;N.x=O/se*2-1,N.y=-(ae/re)*2+1,R.set(N.x,N.y,1).unproject(n.object).sub(n.object.position).normalize()}function Se(B){return Math.max(n.minDistance,Math.min(n.maxDistance,B))}function ie(B){g.set(B.clientX,B.clientY)}function he(B){Te(B),b.set(B.clientX,B.clientY)}function be(B){m.set(B.clientX,B.clientY)}function fe(B){v.set(B.clientX,B.clientY),p.subVectors(v,g).multiplyScalar(n.rotateSpeed);const ce=n.domElement;ce&&(J(2*Math.PI*p.x/ce.clientHeight),q(2*Math.PI*p.y/ce.clientHeight)),g.copy(v),n.update()}function ze(B){I.set(B.clientX,B.clientY),A.subVectors(I,b),A.y>0?de(H()):A.y<0&&ye(H()),b.copy(I),n.update()}function We(B){S.set(B.clientX,B.clientY),_.subVectors(S,m).multiplyScalar(n.panSpeed),ne(_.x,_.y),m.copy(S),n.update()}function Fe(B){Te(B),B.deltaY<0?ye(H()):B.deltaY>0&&de(H()),n.update()}function mt(B){let ce=!1;switch(B.code){case n.keys.UP:ne(0,n.keyPanSpeed),ce=!0;break;case n.keys.BOTTOM:ne(0,-n.keyPanSpeed),ce=!0;break;case n.keys.LEFT:ne(n.keyPanSpeed,0),ce=!0;break;case n.keys.RIGHT:ne(-n.keyPanSpeed,0),ce=!0;break}ce&&(B.preventDefault(),n.update())}function F(){if(y.length==1)g.set(y[0].pageX,y[0].pageY);else{const B=.5*(y[0].pageX+y[1].pageX),ce=.5*(y[0].pageY+y[1].pageY);g.set(B,ce)}}function ft(){if(y.length==1)m.set(y[0].pageX,y[0].pageY);else{const B=.5*(y[0].pageX+y[1].pageX),ce=.5*(y[0].pageY+y[1].pageY);m.set(B,ce)}}function rt(){const B=y[0].pageX-y[1].pageX,ce=y[0].pageY-y[1].pageY,O=Math.sqrt(B*B+ce*ce);b.set(0,O)}function ht(){n.enableZoom&&rt(),n.enablePan&&ft()}function ke(){n.enableZoom&&rt(),n.enableRotate&&F()}function Et(B){if(y.length==1)v.set(B.pageX,B.pageY);else{const O=Ve(B),ae=.5*(B.pageX+O.x),se=.5*(B.pageY+O.y);v.set(ae,se)}p.subVectors(v,g).multiplyScalar(n.rotateSpeed);const ce=n.domElement;ce&&(J(2*Math.PI*p.x/ce.clientHeight),q(2*Math.PI*p.y/ce.clientHeight)),g.copy(v)}function Ye(B){if(y.length==1)S.set(B.pageX,B.pageY);else{const ce=Ve(B),O=.5*(B.pageX+ce.x),ae=.5*(B.pageY+ce.y);S.set(O,ae)}_.subVectors(S,m).multiplyScalar(n.panSpeed),ne(_.x,_.y),m.copy(S)}function qe(B){const ce=Ve(B),O=B.pageX-ce.x,ae=B.pageY-ce.y,se=Math.sqrt(O*O+ae*ae);I.set(0,se),A.set(0,Math.pow(I.y/b.y,n.zoomSpeed)),de(A.y),b.copy(I)}function U(B){n.enableZoom&&qe(B),n.enablePan&&Ye(B)}function T(B){n.enableZoom&&qe(B),n.enableRotate&&Et(B)}function Q(B){var ce,O;n.enabled!==!1&&(y.length===0&&((ce=n.domElement)==null||ce.ownerDocument.addEventListener("pointermove",le),(O=n.domElement)==null||O.ownerDocument.addEventListener("pointerup",te)),Qe(B),B.pointerType==="touch"?Ze(B):$(B))}function le(B){n.enabled!==!1&&(B.pointerType==="touch"?me(B):Ee(B))}function te(B){var ce,O,ae;He(B),y.length===0&&((ce=n.domElement)==null||ce.releasePointerCapture(B.pointerId),(O=n.domElement)==null||O.ownerDocument.removeEventListener("pointermove",le),(ae=n.domElement)==null||ae.ownerDocument.removeEventListener("pointerup",te)),n.dispatchEvent(a),l=o.NONE}function $(B){let ce;switch(B.button){case 0:ce=n.mouseButtons.LEFT;break;case 1:ce=n.mouseButtons.MIDDLE;break;case 2:ce=n.mouseButtons.RIGHT;break;default:ce=-1}switch(ce){case gr.DOLLY:if(n.enableZoom===!1)return;he(B),l=o.DOLLY;break;case gr.ROTATE:if(B.ctrlKey||B.metaKey||B.shiftKey){if(n.enablePan===!1)return;be(B),l=o.PAN}else{if(n.enableRotate===!1)return;ie(B),l=o.ROTATE}break;case gr.PAN:if(B.ctrlKey||B.metaKey||B.shiftKey){if(n.enableRotate===!1)return;ie(B),l=o.ROTATE}else{if(n.enablePan===!1)return;be(B),l=o.PAN}break;default:l=o.NONE}l!==o.NONE&&n.dispatchEvent(r)}function Ee(B){if(n.enabled!==!1)switch(l){case o.ROTATE:if(n.enableRotate===!1)return;fe(B);break;case o.DOLLY:if(n.enableZoom===!1)return;ze(B);break;case o.PAN:if(n.enablePan===!1)return;We(B);break}}function ve(B){n.enabled===!1||n.enableZoom===!1||l!==o.NONE&&l!==o.ROTATE||(B.preventDefault(),n.dispatchEvent(r),Fe(B),n.dispatchEvent(a))}function Ce(B){n.enabled===!1||n.enablePan===!1||mt(B)}function Ze(B){switch(we(B),y.length){case 1:switch(n.touches.ONE){case vr.ROTATE:if(n.enableRotate===!1)return;F(),l=o.TOUCH_ROTATE;break;case vr.PAN:if(n.enablePan===!1)return;ft(),l=o.TOUCH_PAN;break;default:l=o.NONE}break;case 2:switch(n.touches.TWO){case vr.DOLLY_PAN:if(n.enableZoom===!1&&n.enablePan===!1)return;ht(),l=o.TOUCH_DOLLY_PAN;break;case vr.DOLLY_ROTATE:if(n.enableZoom===!1&&n.enableRotate===!1)return;ke(),l=o.TOUCH_DOLLY_ROTATE;break;default:l=o.NONE}break;default:l=o.NONE}l!==o.NONE&&n.dispatchEvent(r)}function me(B){switch(we(B),l){case o.TOUCH_ROTATE:if(n.enableRotate===!1)return;Et(B),n.update();break;case o.TOUCH_PAN:if(n.enablePan===!1)return;Ye(B),n.update();break;case o.TOUCH_DOLLY_PAN:if(n.enableZoom===!1&&n.enablePan===!1)return;U(B),n.update();break;case o.TOUCH_DOLLY_ROTATE:if(n.enableZoom===!1&&n.enableRotate===!1)return;T(B),n.update();break;default:l=o.NONE}}function Ae(B){n.enabled!==!1&&B.preventDefault()}function Qe(B){y.push(B)}function He(B){delete P[B.pointerId];for(let ce=0;ce<y.length;ce++)if(y[ce].pointerId==B.pointerId){y.splice(ce,1);return}}function we(B){let ce=P[B.pointerId];ce===void 0&&(ce=new Xe,P[B.pointerId]=ce),ce.set(B.pageX,B.pageY)}function Ve(B){const ce=B.pointerId===y[0].pointerId?y[1]:y[0];return P[ce.pointerId]}this.dollyIn=(B=H())=>{ye(B),n.update()},this.dollyOut=(B=H())=>{de(B),n.update()},this.getScale=()=>d,this.setScale=B=>{ge(B),n.update()},this.getZoomScale=()=>H(),t!==void 0&&this.connect(t),this.update()}}class GS{constructor(){M(this,"handlers",new Map);M(this,"onceHandlers",new Map);M(this,"messageBuffer",new Map)}register(e,t){if(!this.handlers.has(e)){this.handlers.set(e,new Set);const n=this.messageBuffer.get(e);n&&(n.forEach(s=>Promise.resolve(t(s))),this.messageBuffer.delete(e))}return this.handlers.get(e).add(t),()=>this.unregister(e,t)}once(e,t){return this.onceHandlers.has(e)||this.onceHandlers.set(e,new Set),this.onceHandlers.get(e).add(t),()=>this.unregisterOnce(e,t)}unregister(e,t){var n;(n=this.handlers.get(e))==null||n.delete(t)}unregisterOnce(e,t){var n;(n=this.onceHandlers.get(e))==null||n.delete(t)}buffer(e){const{type:t}=e;this.messageBuffer.has(t)||this.messageBuffer.set(t,[]),this.messageBuffer.get(t).push(e)}async dispatch(e){const{type:t,...n}=e,s=this.handlers.get(t);if(s&&s.size>0){await Promise.all(Array.from(s).map(a=>Promise.resolve(a(n))));return}const r=this.onceHandlers.get(t);if(r&&r.size>0){await Promise.all(Array.from(r).map(a=>Promise.resolve(a(n)))),this.onceHandlers.delete(t);return}this.buffer(e)}clear(){this.handlers.clear(),this.onceHandlers.clear(),this.messageBuffer.clear()}getBuffered(e){return this.messageBuffer.get(e)??[]}hasHandlers(e){var t;return(((t=this.handlers.get(e))==null?void 0:t.size)??0)>0}}class WS{constructor(e,t){M(this,"ws",null);M(this,"url");M(this,"router");M(this,"reconnectDelay",1e3);M(this,"maxReconnectDelay",3e4);M(this,"reconnectAttempts",0);M(this,"shouldReconnect",!0);M(this,"state","disconnected");M(this,"stateListeners",new Set);M(this,"messageQueue",[]);M(this,"heartbeatInterval",null);M(this,"lastPong",0);M(this,"missedPongs",0);M(this,"maxMissedPongs",3);M(this,"heartbeatIntervalMs",15e3);this.url=e,this.router=t}get connectionState(){return this.state}onStateChange(e){return this.stateListeners.add(e),e(this.state),()=>this.stateListeners.delete(e)}setState(e){if(this.state===e)return;const t=this.state;this.state=e,console.log(`[WS] State: ${t} → ${e}`),this.stateListeners.forEach(n=>n(e))}connect(){var n;if(((n=this.ws)==null?void 0:n.readyState)===WebSocket.OPEN||this.state==="connecting")return;this.setState("connecting");const t=`${window.location.protocol==="https:"?"wss:":"ws:"}//${window.location.host}${this.url}`;this.ws=new WebSocket(t),this.ws.binaryType="arraybuffer",this.ws.onopen=()=>{console.log("[WS] Connected"),this.reconnectAttempts=0,this.reconnectDelay=1e3,this.missedPongs=0,this.lastPong=Date.now(),this.setState("connected"),this.startHeartbeat(),this.flushQueue()},this.ws.onmessage=async s=>{try{const r=JSON.parse(s.data);if(r.type==="pong"){this.lastPong=Date.now(),this.missedPongs=0;return}await this.router.dispatch(r)}catch(r){console.error("[WS] Failed to parse message:",r)}},this.ws.onclose=s=>{console.log("[WS] Disconnected:",s.code,s.reason),this.stopHeartbeat(),this.setState("disconnected"),this.shouldReconnect&&this.scheduleReconnect()},this.ws.onerror=s=>{console.error("[WS] Error:",s)}}startHeartbeat(){this.stopHeartbeat(),this.heartbeatInterval=window.setInterval(()=>{var e;if(((e=this.ws)==null?void 0:e.readyState)===WebSocket.OPEN){if(this.missedPongs++,this.missedPongs>this.maxMissedPongs){console.warn("[WS] Heartbeat failed - closing connection"),this.ws.close(1e3,"Heartbeat timeout");return}this.ws.send(JSON.stringify({type:"ping"}))}},this.heartbeatIntervalMs)}stopHeartbeat(){this.heartbeatInterval!==null&&(clearInterval(this.heartbeatInterval),this.heartbeatInterval=null)}scheduleReconnect(){if(this.state==="reconnecting")return;this.setState("reconnecting");const e=Math.min(this.reconnectDelay*Math.pow(1.5,this.reconnectAttempts),this.maxReconnectDelay),t=e*.25*(Math.random()*2-1),n=Math.max(100,e+t);this.reconnectAttempts++,console.log(`[WS] Reconnecting in ${Math.round(n)}ms (attempt ${this.reconnectAttempts})`),setTimeout(()=>this.connect(),n)}send(e){var t;((t=this.ws)==null?void 0:t.readyState)===WebSocket.OPEN?this.ws.send(JSON.stringify(e)):this.messageQueue.push(e)}flushQueue(){var e;for(;this.messageQueue.length>0&&((e=this.ws)==null?void 0:e.readyState)===WebSocket.OPEN;){const t=this.messageQueue.shift();this.ws.send(JSON.stringify(t))}}async request(e,t=5e3){return new Promise((n,s)=>{const r=`${e.type}_${Date.now()}_${Math.random().toString(36).slice(2,9)}`,a={...e,request_id:r},o=this.router.once(r,c=>{clearTimeout(l),c.error?s(new Error(c.error)):n(c.data)}),l=setTimeout(()=>{o(),s(new Error(`Request timeout: ${e.type}`))},t);this.send(a)})}disconnect(){var e;this.shouldReconnect=!1,this.stopHeartbeat(),(e=this.ws)==null||e.close(1e3,"Client disconnect"),this.ws=null,this.setState("disconnected")}async waitForConnection(e=1e4){return this.state==="connected"?!0:new Promise(t=>{const n=setTimeout(()=>{s(),t(!1)},e),s=this.onStateChange(r=>{r==="connected"&&(clearTimeout(n),s(),t(!0))})})}get isConnected(){var e;return((e=this.ws)==null?void 0:e.readyState)===WebSocket.OPEN}getConnectionQuality(){return{state:this.state,latency:this.lastPong?Date.now()-this.lastPong:-1,missedPongs:this.missedPongs}}}const Jt=new GS,sa=new WS("/ws",Jt);let Op=null;function $S(i){Op=i}function Fi(){return Op}class qS{constructor(){M(this,"components",new Map);M(this,"initialized",!1);M(this,"initOrder",[])}register(e){const t=e.name||e.constructor.name;this.components.has(t)&&console.warn(`[ComponentRegistry] Component "${t}" already registered, replacing`),this.components.set(t,e),this.initialized&&e.init().catch(console.error)}unregister(e){const t=this.components.get(e);t&&(t.destroy().catch(console.error),this.components.delete(e))}computeInitOrder(){const e=new Set,t=new Set,n=[],s=r=>{if(e.has(r))return;if(t.has(r)){console.warn(`[ComponentRegistry] Circular dependency detected: ${r}`);return}t.add(r);const a=this.components.get(r);if(a!=null&&a.dependencies)for(const o of a.dependencies)this.components.has(o)&&s(o);t.delete(r),e.add(r),n.push(r)};for(const r of this.components.keys())s(r);return n}async initAll(){if(!this.initialized){this.initOrder=this.computeInitOrder(),this.initialized=!0;for(const e of this.initOrder){const t=this.components.get(e);if(t)try{await t.init(),console.log(`[ComponentRegistry] Initialized: ${e}`)}catch(n){console.error(`[ComponentRegistry] Failed to initialize ${e}:`,n)}}}}async destroyAll(){for(const e of[...this.initOrder].reverse()){const t=this.components.get(e);if(t)try{await t.destroy(),console.log(`[ComponentRegistry] Destroyed: ${e}`)}catch(n){console.error(`[ComponentRegistry] Failed to destroy ${e}:`,n)}}this.components.clear(),this.initialized=!1,this.initOrder=[]}get(e){return this.components.get(e)}list(){return this.initOrder.length>0?this.initOrder:Array.from(this.components.keys())}async healthCheck(){const e={};for(const[t,n]of this.components)if(n.healthCheck)try{e[t]=await Promise.resolve(n.healthCheck())}catch{e[t]=!1}else e[t]=!0;return e}async isHealthy(){const e=await this.healthCheck();return Object.values(e).every(t=>t)}}const Zn=new qS;typeof window<"u"&&(document.addEventListener("DOMContentLoaded",()=>{Zn.initAll().catch(console.error)}),window.addEventListener("beforeunload",()=>{Zn.destroyAll().catch(console.error)}));const Ke={};function Mn(i,e){Ke[i]=e}const ir=[{id:"chart-pareto",label:"Pareto frontier",group:"Charts",key:"p",run:()=>{var i;return(i=Ke["chart-pareto"])==null?void 0:i.call(Ke)}},{id:"chart-ablation",label:"Ablation chart",group:"Charts",key:"a",run:()=>{var i;return(i=Ke["chart-ablation"])==null?void 0:i.call(Ke)}},{id:"chart-variability",label:"Variability chart",group:"Charts",key:"s",run:()=>{var i;return(i=Ke["chart-variability"])==null?void 0:i.call(Ke)}},{id:"control-play",label:"Play / Pause",group:"Run Control",key:" ",run:()=>{var i;return(i=Ke["control-play"])==null?void 0:i.call(Ke)}},{id:"control-step",label:"Step one batch",group:"Run Control",key:"w",run:()=>{var i;return(i=Ke["control-step"])==null?void 0:i.call(Ke)}},{id:"control-stop",label:"Stop run",group:"Run Control",key:"x",run:()=>{var i;return(i=Ke["control-stop"])==null?void 0:i.call(Ke)}},{id:"control-panel",label:"Control panel",group:"Run Control",key:"z",run:()=>{var i;return(i=Ke["control-panel"])==null?void 0:i.call(Ke)}},{id:"panel-hud",label:"Mission Control (HUD)",group:"Panels",key:"h",run:()=>{var i;return(i=Ke["panel-hud"])==null?void 0:i.call(Ke)}},{id:"panel-rail",label:"Live Rail",group:"Panels",key:"r",run:()=>{var i;return(i=Ke["panel-rail"])==null?void 0:i.call(Ke)}},{id:"panel-caption",label:"Caption",group:"Panels",key:"c",run:()=>{var i;return(i=Ke["panel-caption"])==null?void 0:i.call(Ke)}},{id:"panel-legend",label:"Legend",group:"Panels",key:"q",run:()=>{var i;return(i=Ke["panel-legend"])==null?void 0:i.call(Ke)}},{id:"view-cycle",label:"Cycle stage views",group:"Stage",key:"v",run:()=>{var i;return(i=Ke["view-cycle"])==null?void 0:i.call(Ke)}},{id:"cell-replicate",label:"Replicate (queue remaining seeds)",group:"Cell Actions",chord:"shift+r",when:"cell-selected",run:()=>{var i;return(i=Ke["cell-replicate"])==null?void 0:i.call(Ke)}},{id:"cell-preregister",label:"Preregister (confirm protocol)",group:"Cell Actions",chord:"shift+p",when:"cell-selected",run:()=>{var i;return(i=Ke["cell-preregister"])==null?void 0:i.call(Ke)}},{id:"cell-quest",label:"Adopt as Quest (new run)",group:"Cell Actions",chord:"shift+q",when:"cell-selected",run:()=>{var i;return(i=Ke["cell-quest"])==null?void 0:i.call(Ke)}},{id:"help",label:"Show help",group:"General",chord:"shift+/",run:()=>{var i;return(i=Ke.help)==null?void 0:i.call(Ke)}},{id:"escape",label:"Close drawer / dismiss",group:"General",key:"escape",run:()=>{var i;return(i=Ke.escape)==null?void 0:i.call(Ke)}}];function Fp(){return ir}function XS(){const i=new Set;for(const e of ir)if(e.key&&i.add(e.key.toLowerCase()),e.chord){const t=e.chord.match(/shift\+(.+)/);t&&i.add(t[1].toLowerCase())}return i}function YS(){const i={};for(const e of ir)if(e.group==="Panels"&&e.key){const t=e.id.replace("panel-","");i[t]=e.key}return i}function jS(){const i={};for(const e of ir)if(e.group==="Charts"&&e.key){const t=e.id.replace("chart-","");i[t]=e.key}return i}function KS(){const i={};for(const e of ir)if(e.group==="Run Control"&&e.key){const t=e.id.replace("control-","");i[t]=e.key}return i}function JS(){const i=ir.find(e=>e.id==="view-cycle");return(i==null?void 0:i.key)??"v"}const tr=YS(),Lc=jS(),Qd=KS(),ZS=JS(),Ch=XS();new Set("abcdefghijklmnopqrstuvwxyz".split("").filter(i=>!Ch.has(i)));function Ps(i){const{id:e,title:t,glyph:n,key:s,body:r,className:a="",dock:o,defaultOpen:l=!1,onToggle:c}=i,h=document.getElementById("ui-overlay");if(!h)throw new Error("ui-overlay not found — panels must init after DOM ready");const u=document.createElement("div");u.id=e,u.className=`panel ${a}`.trim(),u.dataset.dock=o??"floating",u.setAttribute("role","dialog"),u.setAttribute("aria-label",t),u.setAttribute("aria-modal","false"),u.innerHTML=`
    <header class="panel-header">
      <span class="panel-title">${t}</span>
      ${s?`<kbd class="panel-key-hint">${s.toUpperCase()}</kbd>`:'<span class="panel-key-hint"></span>'}
    </header>
    <div class="panel-body">${r}</div>
  `;const d=u.querySelector(".panel-header"),f=Hp(()=>{$t.toggle(e)});f.style.position="absolute",f.style.top="8px",f.style.right="8px",d.appendChild(f),h.appendChild(u),Lh(u,!l),o&&la.registerPanel(e,{dock:o,defaultOpen:l});const g=$t.onChange(()=>{const p=$t.get(e);if(p){const m=!p.isOpen(),S=u.classList.contains("panel-hidden");m!==S&&(Lh(u,m),la.setPanelOpen(e,!m),c==null||c(!m))}});u.__panelShellUnsubscribe=g;const v=new MutationObserver(()=>{u.classList.contains("panel-hidden")||d.focus()});return v.observe(u,{attributes:!0,attributeFilter:["class"]}),u.__panelShellObserver=v,u}const qt={gradient:"#58a6ff",pepita:"#d4a843",random_projections:"#f78166",local_goodness:"#a371f7",thermodynamic_contrast:"#3fb950",contrastive:"#ff7b72",hebbian:"#79c0ff",predictive:"#d2a8ff"},k={bg:"#0a0e14",bg_tertiary:"#1a2330",border:"#2a3a4a",border_bright:"#3a4a5a",text_primary:"#e8ecf0",text_secondary:"#8b98a8",text_muted:"#5a6a7a",gradient:"#58a6ff",thermodynamic_contrast:"#3fb950",measured:"#d4a843",legal_unmeasured:"#58a6ff",void:"#f85149",pareto:"#e8ecf0",chance_line:"#f85149",ok:"#3fb950",warn:"#d29922",error:"#f85149",passed:"#3fb950",insufficient:"#d29922",rejected:"#f85149",ramp_low:"#1f3a5f",ramp_mid:"#58a6ff",ramp_high:"#d4a843"};class QS{constructor(){M(this,"metricsByRun",new Map);M(this,"selectedRunId",null);M(this,"chosenByReader",!1);M(this,"listeners",[])}observe(e,t){this.metricsByRun.set(e,t),this.chosenByReader||(this.selectedRunId=this.newestRunId()),this.notify()}select(e){this.chosenByReader=!0,this.selectedRunId=e,this.notify()}get selectedId(){return this.selectedRunId}get selected(){return this.selectedRunId?this.metricsByRun.get(this.selectedRunId)??null:null}get runs(){return Array.from(this.metricsByRun.entries())}onChange(e){this.listeners.push(e)}notify(){this.listeners.forEach(e=>e(this.selectedRunId,this.selected))}newestRunId(){let e=null,t=-1/0;if(this.metricsByRun.forEach((s,r)=>{var l;const a=(l=s.run)==null?void 0:l.started_at,o=a?Date.parse(a):Number.NaN;Number.isNaN(o)||o>=t&&(t=o,e=r)}),e)return e;const n=this.metricsByRun.keys().next();return n.done?null:n.value}}const Kn=new QS,eb={substrate:{display_name:"Substrate",description:"Physical or computational substrate",primitives:[{name:"digital",summary:"Digital substrate: exact arithmetic, full precision",available:!0},{name:"analog",summary:"Analog substrate: continuous-valued physical state",available:!0},{name:"memristive",summary:"Memristive substrate: conductance, IR-drop, noise",available:!0},{name:"neuromorphic",summary:"Neuromorphic substrate: asynchronous spike events",available:!0},{name:"optical",summary:"Photonic substrate: phase/amplitude modulation",available:!0},{name:"quantum",summary:"Quantum substrate: unitary gate simulation",available:!0},{name:"complex",summary:"Complex-valued substrate",available:!0},{name:"sparse",summary:"Sparse substrate: sparsity-masked state",available:!0},{name:"ternary",summary:"Ternary substrate: weights in {-alpha, 0, +alpha}",available:!0}]},geometry:{display_name:"Geometry",description:"Network architecture and connectivity",primitives:[{name:"feedforward",summary:"Feedforward DAG (MLP/CNN)",available:!0},{name:"recurrent",summary:"Recurrent attractor (Hopfield/EqProp)",available:!0},{name:"causal_transformer",summary:"Causal transformer with KV cache",available:!0},{name:"tile",summary:"TileNet modular tile mesh",available:!0},{name:"tile_mesh",summary:"TileNet mesh topology",available:!0},{name:"conv",summary:"Convolutional geometry",available:!0},{name:"graph",summary:"Arbitrary node-edge fabric (FabricPC)",available:!0},{name:"attention",summary:"Attention geometry",available:!0},{name:"spatial_lattice",summary:"3-D spatial lattice (neural_cube)",available:!0},{name:"nca",summary:"Neural cellular automaton fabric",available:!0},{name:"ntm",summary:"Neural Turing Machine tape",available:!0}]},dynamics:{display_name:"Dynamics",description:"State evolution and settling",primitives:[{name:"energy_minimization",summary:"Equilibrium propagation energy minimization",available:!0},{name:"predictive_settling",summary:"Predictive coding settling",available:!0},{name:"error_predictive_coding",summary:"Error predictive coding",available:!0},{name:"spike_integration",summary:"LIF/Izhikevich spike integration",available:!0},{name:"instantaneous",summary:"Instantaneous pass (FF/Backprop)",available:!0},{name:"diffusion",summary:"Continuous-time diffusion settling",available:!0},{name:"lazy",summary:"Lazy/on-demand state dynamics",available:!0},{name:"pc_alm",summary:"Augmented Lagrangian predictive coding",available:!0}]},plasticity:{display_name:"Plasticity",description:"Local learning and adaptation",primitives:[{name:"null",summary:"Null plasticity (5-D slice)",available:!0},{name:"routing",summary:"Routing plasticity: state-dependent gating",available:!0},{name:"fast_weights",summary:"Fast-weight episode-local memory",available:!0},{name:"substrate_coupled",summary:"Physical substrate-coupled plasticity",available:!0},{name:"rule_state",summary:"Rule-state plasticity (Z3)",available:!0},{name:"temporal_psi",summary:"Trace-decayed supervised psi",available:!0},{name:"conflict_adaptive",summary:"Conflict-adaptive psi",available:!0}]},credit:{display_name:"Credit Assignment",description:"How learning signals reach parameters",primitives:[{name:"thermodynamic_contrast",summary:"EqProp free/nudged contrast (Scellier-Bengio)",available:!0},{name:"random_projections",summary:"Fixed random feedback (FA/DFA)",available:!0},{name:"local_goodness",summary:"Forward-Forward / PEPITA goodness",available:!0},{name:"local_contrastive",summary:"Local contrastive credit",available:!0},{name:"temporal_trace",summary:"Hebbian/STDP temporal trace",available:!0},{name:"target_inversion",summary:"Target propagation inversion",available:!0},{name:"homeostatic",summary:"Autonomous Lipschitz scaling",available:!0},{name:"pepita",summary:"PEPITA input-modulation credit",available:!0},{name:"gradient",summary:"Backprop gradient credit (ruler reference)",available:!0},{name:"pc_alm",summary:"PC-ALM primal-dual credit",available:!0}]},update:{display_name:"Update Rule",description:"How parameters are updated",primitives:[{name:"euclidean",summary:"SGD/Adam Euclidean update",available:!0},{name:"adam",summary:"Adam adaptive moment",available:!0},{name:"local_adam",summary:"Local Adam",available:!0},{name:"ortho_adam",summary:"Orthogonal Adam",available:!0},{name:"riemannian_orthogonal",summary:"Riemannian orthogonal update (Muon-family)",available:!0},{name:"muon",summary:"Muon update",available:!0},{name:"lion",summary:"Lion optimizer",available:!0},{name:"spectral_constrained",summary:"Spectral-norm constrained update",available:!0},{name:"mean_norm",summary:"Mean-norm update",available:!0},{name:"elastic_consolidation",summary:"EWC elastic consolidation",available:!0},{name:"natural_gradient",summary:"Natural gradient (Fisher)",available:!0},{name:"role_split",summary:"Role-split update",available:!0}]}},tb={axes:eb},kp=.72,Bp=.86;function co(i,e,t,n,s){const{camera:r,controls:a}=i,o=(s==null?void 0:s.clone())??r.position.clone().sub(a.target);o.lengthSq()===0&&o.set(.4,.5,.8),o.normalize();const l=o.clone().negate(),c=new V().crossVectors(l,new V(0,1,0)).normalize(),h=new V().crossVectors(c,l).normalize(),u=Math.tan((r.fov??60)*Math.PI/360),d=u*(r.aspect||1),f=u*Bp,g=d*kp;let v=0;[e.x,t.x].forEach(p=>{[e.y,t.y].forEach(m=>{[e.z,t.z].forEach(S=>{const _=new V(p,m,S),b=Math.max(Math.abs(_.dot(c))/g,Math.abs(_.dot(h))/f)+_.dot(o);v=Math.max(v,b)})})}),v*=1.06,n.add(c.clone().multiplyScalar(.28*d*v)).add(h.clone().multiplyScalar(-.14*u*v)),a.target.copy(n),r.position.copy(n).add(o.clone().multiplyScalar(v)),a.update()}const eo=["credit","geometry","dynamics","substrate","plasticity","update"];function wi(i,e,t){return`${i}|${e}|${t}`}function ts(i){return i.length===0?0:i.reduce((e,t)=>e+t,0)/i.length}function nb(i){if(i.length<2)return 0;const e=ts(i),t=i.reduce((n,s)=>n+(s-e)**2,0)/(i.length-1);return Math.sqrt(t)}function ib(i){const e=new Map;for(const t of i)for(const n of t){const s=e.get(n.epoch)??[];s.push(n.val_acc),e.set(n.epoch,s)}return Array.from(e.entries()).sort((t,n)=>t[0]-n[0]).map(([t,n])=>({epoch:t,val_acc:ts(n)}))}function sb(i,e){const t=new Map;return i.cells.forEach(n=>{t.set(wi(n.coordinate[e.x],n.coordinate[e.y],n.coordinate[e.z]),n)}),t}function rb(i,e){const t=new Map;return((i==null?void 0:i.records)??[]).forEach((s,r)=>{var h;const a=s==null?void 0:s.coordinate;if(!a)return;const o=wi(a[e.x],a[e.y],a[e.z]);let l=t.get(o);l||(l={acc:[],walltime:[],params:[],curves:[],pareto:!1,coordinate:{...a},seeds:0},t.set(o,l)),l.seeds+=1;const c=s.payload??{};if(typeof c.val_acc=="number"&&l.acc.push(c.val_acc),typeof c.walltime_s=="number"&&l.walltime.push(c.walltime_s),typeof c.param_count=="number"&&l.params.push(c.param_count),Array.isArray(c.convergence_curve)){const u=c.convergence_curve.filter(d=>typeof(d==null?void 0:d.epoch)=="number"&&typeof(d==null?void 0:d.val_acc)=="number").map(d=>({epoch:d.epoch,val_acc:d.val_acc}));u.length>0&&l.curves.push(u)}(h=i==null?void 0:i.pareto)!=null&&h[r]&&(l.pareto=!0)}),t}function su(i,e){const t=Array.from(i.values()),n=El(t,e);return t.sort((s,r)=>to(s,e,n).localeCompare(to(r,e,n)))}function El(i,e){return[e.x,e.y,e.z].filter(n=>new Set(i.map(r=>r.coordinate[n])).size>1)}function to(i,e,t){return(t.length>0?t:[e.x,e.y,e.z]).map(s=>i.coordinate[s]??"").join(" · ")}function ef(i){const e={credit:new Set,geometry:new Set,dynamics:new Set,substrate:new Set,plasticity:new Set,update:new Set};i.forEach(n=>{const s=n==null?void 0:n.coordinate;s&&eo.forEach(r=>{const a=s[r];typeof a=="string"&&a.length>0&&e[r].add(a)})});const t={};return eo.forEach(n=>{t[n]=Array.from(e[n]).sort()}),t}class ab{constructor(){M(this,"runId",null);M(this,"metrics",null);M(this,"axes",{x:"credit",y:"geometry",z:"dynamics"});M(this,"space",null);M(this,"spaceCells",new Map);M(this,"aggregates",new Map);M(this,"values",ef([]));M(this,"chance",.1);M(this,"requiredSeeds",0);M(this,"gate",null);M(this,"timeline",null);M(this,"account",null);M(this,"flow",null);M(this,"attribution",null);M(this,"dynamics",null);M(this,"multirun",null);M(this,"trainedDynamics",null);M(this,"spaceRequest","");M(this,"accountRequest","");M(this,"attributionRequest","");M(this,"flowRequest","");M(this,"dynamicsRun","");M(this,"dynamicsAsking",!1);M(this,"trainedDynamicsRun","");M(this,"trainedDynamicsAsking",!1);M(this,"multirunRequest","");M(this,"multirunAsking",!1);M(this,"timelineRun","");M(this,"timelineStale",!0);M(this,"timelineTimer",null);M(this,"listeners",[]);Kn.onChange((e,t)=>{this.absorb(e,t)}),Jt.register("pipeline_event",()=>this.scheduleTimeline())}onChange(e){this.listeners.push(e)}notify(e){this.listeners.forEach(t=>t(e))}async absorb(e,t){this.runId=e,this.metrics=t,t&&(typeof t.chance=="number"&&(this.chance=t.chance),typeof t.required_seeds=="number"&&(this.requiredSeeds=t.required_seeds),t.gate&&(this.gate=t.gate,typeof t.gate.required_seeds_per_group=="number"&&(this.requiredSeeds=t.gate.required_seeds_per_group)),this.values=ef(t.records??[])),this.recomputeEvidence(),await this.syncSpace(),this.syncAccount(),this.syncAttribution(),this.syncTimeline(),this.syncDynamics(),this.syncTrainedDynamics()}setAxes(e){this.axes=e,this.notify("axes"),this.recomputeEvidence(),this.syncSpace()}recomputeEvidence(){this.aggregates=rb(this.metrics,this.axes),this.notify("evidence")}async syncSpace(){if(!this.runId)return;const e=[this.runId,this.axes.x,this.axes.y,this.axes.z,...eo.map(n=>this.values[n].join(","))].join("|");if(e===this.spaceRequest)return;const t=await this.fetchSpace();t&&(this.spaceRequest=e,this.space=t,this.spaceCells=sb(t,this.axes),this.notify("space"))}async fetchSpace(){try{const e=await fetch(`/api/cells/${this.runId}/space`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({axes:[this.axes.x,this.axes.y,this.axes.z]})});return e.ok?await e.json():(console.warn("[StageState] The space was refused",e.status),null)}catch(e){return console.warn("[StageState] The space could not be read",e),null}}async syncAccount(){var n,s;if(!this.runId){this.account=null,this.accountRequest="";return}const e=((s=(n=this.metrics)==null?void 0:n.records)==null?void 0:s.length)??0,t=`${this.runId}|${e}`;if(t!==this.accountRequest)try{const r=await fetch(`/api/runs/${encodeURIComponent(this.runId)}/account`);if(!r.ok){console.warn("[StageState] The account was refused",r.status);return}this.account=await r.json(),this.accountRequest=t,this.notify("evidence")}catch(r){console.warn("[StageState] The account could not be read",r)}}async syncTimeline(){if(!this.runId){this.timeline=null,this.timelineRun="";return}if(!(!this.timelineStale&&this.timelineRun===this.runId))try{const e=await fetch(`/api/events?run_id=${encodeURIComponent(this.runId)}`);if(!e.ok){console.warn("[StageState] The timeline was refused",e.status);return}this.timeline=await e.json(),this.timelineRun=this.runId,this.timelineStale=!1,this.notify("events"),this.syncFlow()}catch(e){console.warn("[StageState] The timeline could not be read",e)}}async syncFlow(){var n;if(!this.runId){this.flow=null,this.flowRequest="";return}const e=((n=this.timeline)==null?void 0:n.events.length)??0,t=`${this.runId}|${e}`;if(t!==this.flowRequest)try{const s=await fetch(`/api/runs/${encodeURIComponent(this.runId)}/flow`);if(!s.ok){console.warn("[StageState] The flow was refused",s.status);return}this.flow=await s.json(),this.flowRequest=t,this.notify("events")}catch(s){console.warn("[StageState] The flow could not be read",s)}}async syncAttribution(){var n,s;if(!this.runId){this.attribution=null,this.attributionRequest="";return}const e=((s=(n=this.metrics)==null?void 0:n.records)==null?void 0:s.length)??0,t=`${this.runId}|${e}`;if(t!==this.attributionRequest)try{const r=await fetch(`/api/runs/${encodeURIComponent(this.runId)}/attribution`);if(!r.ok){console.warn("[StageState] The attribution was refused",r.status);return}this.attribution=await r.json(),this.attributionRequest=t,this.notify("evidence")}catch(r){console.warn("[StageState] The attribution could not be read",r)}}async syncDynamics(){if(!this.runId){this.dynamics=null,this.dynamicsRun="";return}if(!(this.dynamicsRun===this.runId||this.dynamicsAsking)){this.dynamicsAsking=!0;try{const e=await fetch(`/api/runs/${encodeURIComponent(this.runId)}/dynamics`);if(!e.ok){console.warn("[StageState] The dynamics were refused",e.status);return}const t=await e.json();this.dynamics=t,t.cell&&(this.dynamicsRun=this.runId),this.notify("evidence")}catch(e){console.warn("[StageState] The dynamics could not be read",e)}finally{this.dynamicsAsking=!1}}}async syncTrainedDynamics(){if(!this.runId){this.trainedDynamics=null,this.trainedDynamicsRun="";return}if(!(this.trainedDynamicsRun===this.runId||this.trainedDynamicsAsking)){this.trainedDynamicsAsking=!0;try{const e=await fetch(`/api/runs/${encodeURIComponent(this.runId)}/dynamics/trained`);if(!e.ok){console.warn("[StageState] The trained dynamics were refused",e.status);return}const t=await e.json();this.trainedDynamics=t,t.cell&&(this.trainedDynamicsRun=this.runId),this.notify("evidence")}catch(e){console.warn("[StageState] The trained dynamics could not be read",e)}finally{this.trainedDynamicsAsking=!1}}}scheduleTimeline(){this.timelineStale=!0,this.timelineTimer===null&&(this.timelineTimer=window.setTimeout(()=>{this.timelineTimer=null,this.syncTimeline()},300))}async syncMultirun(e=!1){const t=[this.axes.x,this.axes.y,this.axes.z].join("|");if(!(!e&&(t===this.multirunRequest||this.multirunAsking))){this.multirunAsking=!0;try{const n=await fetch("/api/spaces",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({axes:[this.axes.x,this.axes.y,this.axes.z]})});if(!n.ok){console.warn("[StageState] The runs' space was refused",n.status);return}this.multirun=await n.json(),this.multirunRequest=t,this.notify("evidence")}catch(n){console.warn("[StageState] The runs' space could not be read",n)}finally{this.multirunAsking=!1}}}}const xe=new ab;function ra(i,e=10){if(i.length<=e)return[i];const t=[];let n="";for(const s of i.split("_")){const r=n?`${n}_${s}`:s;r.length>e&&n?(t.push(n),n=s):n=r}return n&&t.push(n),t}function vn(i,e,t,n){const s=ra(i),r=document.createElement("canvas"),a=r.getContext("2d"),o=64,l=72;a.font=`bold ${o}px "JetBrains Mono", monospace`;const c=Math.max(...s.map(v=>a.measureText(v).width))+16;r.width=Math.max(64,Math.ceil(c)),r.height=s.length*l+16,a.font=`bold ${o}px "JetBrains Mono", monospace`,a.fillStyle="#ffffff",a.textAlign="center",a.textBaseline="middle",s.forEach((v,p)=>{a.fillText(v,r.width/2,l*p+l/2+8)});const h=new tu(r);h.needsUpdate=!0;const u=t.clone();u.map=h,u.transparent=!0;const d=new Ip(u),f=r.width/r.height;let g=e*s.length;return n!==void 0&&(g=Math.min(g,n/f)),d.scale.set(g*f,g,1),d}function ob(){const e=document.createElement("canvas");e.width=64,e.height=64;const t=e.getContext("2d");t.fillStyle="#ffffff",t.beginPath(),t.arc(64/2,64/2,64/2-2,0,Math.PI*2),t.fill();const n=new tu(e);return n.needsUpdate=!0,n}function lb(i,e,t=.14){const s=document.createElement("canvas");s.width=128,s.height=128;const r=s.getContext("2d");r.strokeStyle=i,r.lineWidth=128*t,r.beginPath(),r.arc(128/2,128/2,128/2-r.lineWidth,0,Math.PI*2),r.stroke();const a=new tu(s);a.needsUpdate=!0;const o=new Ei({map:a,transparent:!0,depthWrite:!1}),l=new Ip(o);return l.scale.set(e*2,e*2,1),l}const tf=tb.axes,cb={measured:"Measured — the run has evidence here",legal:"Legal — a gap nobody has measured",void:"Void — the system refuses this cell"};class hb{constructor(){M(this,"name","DiscoveryMap");M(this,"scene",new Lp);M(this,"camera",new Rn);M(this,"renderer",null);M(this,"cells",new Map);M(this,"cellDataMap",new Map);M(this,"cellHeights",new Map);M(this,"xValues",[]);M(this,"yValues",[]);M(this,"zValues",[]);M(this,"cellSize",.8);M(this,"spacing",1.1);M(this,"raycaster",new IS);M(this,"mouse",new Xe);M(this,"selectedCell",null);M(this,"hoveredCell",null);M(this,"legendElement",null);M(this,"readoutElement",null);M(this,"pointerX",0);M(this,"pointerY",0);M(this,"axisLabelMeshes",[]);M(this,"voidMesh",null);M(this,"visible",!1);M(this,"onQueueUpdate",e=>{});M(this,"onCampaignMetrics",e=>{const t=e==null?void 0:e.data;if(!(t!=null&&t.run))return;const n=typeof(e==null?void 0:e.campaign_id)=="string"?e.campaign_id:null;n&&Kn.observe(n,t)});Jt.register("queue_update",this.onQueueUpdate),Jt.register("campaign_metrics",this.onCampaignMetrics)}async init(){const e=Fi();e&&(this.scene=e.scene,this.camera=e.camera,this.renderer=e.renderer),this.setupInteraction(),this.createLegend(),this.createReadout(),xe.onChange(()=>this.updateLegend()),Kn.onChange(()=>this.updateRunPicker()),console.log("[DiscoveryMap] Initialized")}async destroy(){var e,t;Jt.unregister("queue_update",this.onQueueUpdate),Jt.unregister("campaign_metrics",this.onCampaignMetrics),this.clearGrid(),(e=this.legendElement)==null||e.remove(),(t=this.readoutElement)==null||t.remove()}show(){this.visible=!0,this.applyAxes()}hide(){this.visible=!1,this.clearGrid()}refreshView(e){if(this.visible){if(e==="space"){this.applyAxes();return}e==="evidence"&&this.applyAggregates()}}hasMeasured(){return this.cellDataMap.size>0&&this.cellHeights.size>0}updateLegend(){var h,u,d,f,g;const e=xe.space,t=!!e,s=xe.values.credit.length>0,r=(h=this.legendElement)==null?void 0:h.querySelector("#legend-empty-state"),a=(u=this.legendElement)==null?void 0:u.querySelector("#legend-view"),o=(d=this.legendElement)==null?void 0:d.querySelector("#legend-arms-block"),l=(f=this.legendElement)==null?void 0:f.querySelector("#legend-axes-block");r&&(r.style.display=t?"none":"flex"),a&&(a.style.display=t?"block":"none"),o&&(o.style.display=s?"block":"none"),l&&(l.style.display=t?"block":"none");const c=(g=this.legendElement)==null?void 0:g.querySelector("#legend-cell-count");if(c&&e){const v={measured:Array.from(xe.aggregates.keys()).filter(p=>xe.spaceCells.has(p)).length,legal:e.counts.legal,void:e.counts.void};c.textContent=`${v.measured+v.legal+v.void} cells`}this.refreshAxisOptions(),this.updateLegendArms(),this.updateLegendAxes()}setupInteraction(){var t;const e=(t=this.renderer)==null?void 0:t.domElement;e&&(this.raycaster.params.Line.threshold=this.cellSize*.2,e.addEventListener("mousemove",n=>{const s=e.getBoundingClientRect();this.mouse.x=(n.clientX-s.left)/s.width*2-1,this.mouse.y=-((n.clientY-s.top)/s.height)*2+1,this.pointerX=n.clientX,this.pointerY=n.clientY}),e.addEventListener("mouseleave",()=>{this.hideReadout()}),e.addEventListener("click",()=>{this.hoveredCell&&this.selectCell(this.hoveredCell)}))}createReadout(){const e=document.getElementById("ui-overlay");e&&(this.readoutElement=document.createElement("div"),this.readoutElement.id="cell-readout",this.readoutElement.style.cssText=`
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
    `,e.appendChild(this.readoutElement))}showReadout(e){const t=this.readoutElement;if(!t)return;t.innerHTML="";const n=document.createElement("div");n.style.cssText="display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 8px;",Object.entries(e.coordinate).filter(([,d])=>d).forEach(([d,f])=>{const g=d==="credit",v=g?qt[f]||k.gradient:"var(--text-secondary)",p=document.createElement("span");p.style.cssText=`
          padding: 2px 8px;
          background: ${g?v+"22":"var(--bg-tertiary)"};
          border: 1px solid ${g?v+"88":"var(--border)"};
          border-radius: 10px;
          font-size: 10px;
          color: ${v};
          font-weight: ${g?"600":"400"};
        `,p.textContent=`${d}=${f}`,n.appendChild(p)}),t.appendChild(n);const s=document.createElement("div");s.style.cssText="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;";const r={measured:k.measured,legal:k.legal_unmeasured,void:k.void},a={measured:"●",legal:"○",void:"✕"},o=document.createElement("span");o.style.cssText=`font-size: 14px; color: ${r[e.status]};`,o.textContent=a[e.status],s.appendChild(o);const l=document.createElement("span");if(l.style.cssText=`font-weight: 600; color: ${r[e.status]}; font-size: 12px;`,l.textContent=cb[e.status],s.appendChild(l),t.appendChild(s),e.status==="measured"&&e.metrics){const d=e.metrics,f=document.createElement("div");f.style.cssText="display: flex; gap: 16px; font-size: 11px; color: var(--text-secondary);";const g=d.val_acc??0,v=d.val_acc_std??0,p=d.n_seeds??0,m=d.walltime_s;f.innerHTML=`
        <span>acc <strong style="color: var(--text-primary);">${g.toFixed(3)}</strong> ± ${v.toFixed(3)}</span>
        <span>n=<strong style="color: var(--text-primary);">${p}</strong></span>
        <span>${m!==void 0?`${m.toFixed(1)}s`:""}</span>
        ${e.pareto?'<span style="color: var(--pareto);">● PARETO</span>':""}
      `,t.appendChild(f)}if(e.status==="legal"){const d=document.createElement("div");d.style.cssText="margin-top: 6px; padding: 6px 8px; background: var(--bg-tertiary); border-radius: 4px; font-size: 10px; color: var(--text-muted);";const f=e.requiredSeeds??0;d.textContent=`Click to queue ${f} seeds →`,t.appendChild(d)}if(e.voidReason){const d=document.createElement("div");d.style.cssText="margin-top: 6px; padding: 6px 8px; background: var(--void)11; border: 1px solid var(--void)44; border-radius: 4px; font-size: 10px; color: var(--void);",d.textContent=e.voidReason,t.appendChild(d)}t.style.display="block";const c=t.getBoundingClientRect(),h=Math.min(this.pointerX+16,window.innerWidth-c.width-8),u=Math.min(this.pointerY+16,window.innerHeight-c.height-8);t.style.left=`${Math.max(8,h)}px`,t.style.top=`${Math.max(8,u)}px`}hideReadout(){this.readoutElement&&(this.readoutElement.style.display="none")}createLegend(){this.legendElement=Ps({id:"discovery-legend",title:"Discovery Map",glyph:"▦",key:tr.legend,body:this.legendBody(),dock:"bottom",defaultOpen:!0}),this.createRunPicker(),this.createAxisPicker(),this.updateLegendArms(),this.updateLegendAxes()}legendBody(){return`
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
    `}createRunPicker(){var t;const e=(t=this.legendElement)==null?void 0:t.querySelector("#legend-run-picker");e&&e.addEventListener("change",()=>{Kn.select(e.value||null)})}updateRunPicker(){var a,o,l;const e=(a=this.legendElement)==null?void 0:a.querySelector("#legend-run-picker"),t=(o=this.legendElement)==null?void 0:o.querySelector("#legend-run");if(!e)return;const n=Kn.runs;if(e.innerHTML="",n.forEach(([c,h])=>{var g,v;const u=document.createElement("option"),d=((g=h==null?void 0:h.run)==null?void 0:g.profile)??"run",f=((v=h==null?void 0:h.records)==null?void 0:v.length)??0;u.value=c,u.textContent=`${c.slice(0,8)} · ${d} · ${f}`,u.selected=c===Kn.selectedId,e.appendChild(u)}),n.length===0){e.disabled=!0,t&&(t.textContent="No run has reported yet.");return}e.disabled=!1;const s=Kn.selected;if(!t)return;if(!s){t.textContent="";return}const r=s.run??{};t.textContent=[`run ${(Kn.selectedId??"").slice(0,8)}`,r.mode,`${((l=s.records)==null?void 0:l.length)??0} records`].filter(Boolean).join(" · ")}createAxisPicker(){var n;const e=(n=this.legendElement)==null?void 0:n.querySelector("#legend-axis-picker");if(!e)return;["x","y","z"].forEach(s=>{const r=document.createElement("div");r.className="axis-row",r.dataset.dimension=s,r.style.cssText=`
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 3px;
        font-size: 11px;
        margin-bottom: 3px;
      `;const a=document.createElement("span");a.textContent=s.toUpperCase(),a.style.cssText="color: var(--text-secondary); width: 12px;",r.appendChild(a),e.appendChild(r)}),this.refreshAxisOptions()}refreshAxisOptions(){var t;const e=(t=this.legendElement)==null?void 0:t.querySelectorAll("#legend-axis-picker .axis-row");e&&e.forEach(n=>{const s=n.dataset.dimension,r=new Set(["x","y","z"].filter(o=>o!==s).map(o=>xe.axes[o]));n.innerHTML="";const a=document.createElement("span");a.textContent=s.toUpperCase(),a.style.cssText="color: var(--text-secondary); width: 12px;",n.appendChild(a),eo.forEach(o=>{var h;const l=xe.axes[s]===o,c=document.createElement("button");c.className="axis-button",c.dataset.axis=o,c.textContent=((h=tf[o])==null?void 0:h.display_name)??o,c.disabled=r.has(o),c.style.cssText=`
          flex: 0 0 auto;
          padding: 1px 5px;
          background: ${l?"var(--bg-primary)":"var(--bg-tertiary)"};
          border: 1px solid ${l?"var(--border-bright)":"var(--border)"};
          border-radius: 4px;
          color: ${l?"var(--text-primary)":"var(--text-secondary)"};
          font-size: 10px;
          cursor: pointer;
          opacity: ${r.has(o)?.4:1};
        `,c.addEventListener("click",()=>{xe.setAxes({...xe.axes,[s]:o})}),n.appendChild(c)})})}updateLegendArms(){var n;const e=(n=this.legendElement)==null?void 0:n.querySelector("#legend-arms");if(!e)return;const t=xe.values.credit;if(t.length===0){e.innerHTML='<span style="color: var(--text-muted); font-size: 11px;">No arm measured yet.</span>';return}e.innerHTML=t.map(s=>{const r=qt[s]||k.gradient;return`<span style="display: inline-flex; align-items: center; gap: 4px; padding: 2px 8px; background: ${r}22; border: 1px solid ${r}88; border-radius: 12px; color: ${r}; font-size: 11px;">${s}</span>`}).join("")}updateLegendAxes(){var l;const e=(l=this.legendElement)==null?void 0:l.querySelector("#legend-axes");if(!e)return;const t=xe.space;if(!t){e.textContent="Waiting for the run's declared space — the axes come from the ontology.";return}const n=(c,h)=>{var g;const u=t.available[c]??h.length,d=u>h.length?` (${h.length} of ${u})`:"";return`${((g=tf[c])==null?void 0:g.display_name)??c}${d}`},s=Object.entries(t.held).map(([c,h])=>`${c}=${h}`),r={measured:Array.from(xe.aggregates.keys()).filter(c=>xe.spaceCells.has(c)).length,legal:t.counts.legal,void:t.counts.void},a=t.cells.length,o=Object.entries(t.void_rules??{}).sort((c,h)=>h[1]-c[1]).slice(0,2).map(([c,h])=>`${c.replace(/_/g," ")} (${h})`);e.innerHTML=[`<div>X: ${n(xe.axes.x,t.values[xe.axes.x]??[])}</div>`,`<div>Y: ${n(xe.axes.y,t.values[xe.axes.y]??[])}</div>`,`<div>Z: ${n(xe.axes.z,t.values[xe.axes.z]??[])}</div>`,`<div style="margin-top: 6px;">held: ${s.join(" · ")||"—"}</div>`,`<div style="margin-top: 6px;">${r.measured} measured · ${r.legal} legal · ${r.void} void (of ${a})</div>`,o.length>0?`<div style="margin-top: 6px;">refused by: ${o.join(", ")}</div>`:""].join("")}applyAxes(){const e=xe.space,t=xe.axes;this.xValues=(e==null?void 0:e.values[t.x])??[],this.yValues=(e==null?void 0:e.values[t.y])??[],this.zValues=(e==null?void 0:e.values[t.z])??[],this.buildGrid(),this.updateLegend()}buildGrid(){if(this.clearGrid(),!this.visible)return;this.createAxisLabels();const e=[];this.yValues.forEach((t,n)=>{this.zValues.forEach((s,r)=>{this.xValues.forEach((a,o)=>{const l=wi(a,t,s),c=xe.spaceCells.get(l),h=(c==null?void 0:c.status)??"legal",u={coordinate:this.coordinateFor(a,t,s),status:h,chance:xe.chance,requiredSeeds:xe.requiredSeeds,runId:xe.runId??void 0,voidReason:c==null?void 0:c.reason,inDeclaration:c==null?void 0:c.in_declaration};if(this.cellDataMap.set(l,u),h==="void"){e.push(...this.voidMarkerPositions(o,n,r));return}this.createCell(l,u,o,n,r)})})}),e.length>0&&this.createVoidMarkers(e),this.frameGrid()}coordinateFor(e,t,n){const s={credit:"",geometry:"",dynamics:"",substrate:"",plasticity:"",update:""};return s[xe.axes.x]=e,s[xe.axes.y]=t,s[xe.axes.z]=n,eo.forEach(r=>{var o,l;if(s[r])return;const a=(l=(o=xe.space)==null?void 0:o.held)==null?void 0:l[r];a&&(s[r]=a)}),s}createAxisLabels(){this.axisLabelMeshes.forEach(h=>this.scene.remove(h)),this.axisLabelMeshes=[];const e=new Ei({color:9148584,sizeAttenuation:!0}),t=new Ei({color:13227232,sizeAttenuation:!0}),n=(this.xValues.length-1)*this.spacing,r=(this.zValues.length-1)*this.spacing/2+1.2,a=-.45;this.xValues.forEach((h,u)=>{const d=(u-(this.xValues.length-1)/2)*this.spacing,f=vn(h,.3,e,this.spacing*.95);f.position.set(d,a,r),this.scene.add(f),this.axisLabelMeshes.push(f)});const o=vn(xe.axes.x,.3,t);o.position.set(n/2+1.15,a,r),this.scene.add(o),this.axisLabelMeshes.push(o);const l=vn(xe.axes.z,.3,t);l.position.set(0,a,r+1.1),this.scene.add(l),this.axisLabelMeshes.push(l);const c=vn(xe.axes.y,.3,t);c.position.set(-(n/2)-1.5,1.3,0),this.scene.add(c),this.axisLabelMeshes.push(c)}createCell(e,t,n,s,r){const a=(n-(this.xValues.length-1)/2)*this.spacing,o=s*this.spacing,l=(r-(this.zValues.length-1)/2)*this.spacing,c=t.status==="measured"?this.createMeasuredCell(t):this.createLegalCell();c.position.set(a,o,l),c.userData={...c.userData,cellKey:e},this.scene.add(c),this.cells.set(e,c)}createMeasuredCell(e){const t=this.pillarHeight(e),n=qt[e.coordinate.credit]||k.gradient,s=new Si(this.cellSize,t,this.cellSize);s.translate(0,t/2,0);const r=new Jr({color:new it(n),emissive:new it(n),emissiveIntensity:.5,transparent:!0,opacity:.9,metalness:.3,roughness:.4}),a=new jt(s,r);a.castShadow=!0,a.receiveShadow=!0;const o=new Si(this.cellSize*1.1,t*1.1,this.cellSize*1.1);o.translate(0,t/2,0);const l=new es({color:new it(n),transparent:!0,opacity:.15,depthWrite:!1}),c=new jt(o,l);return a.add(c),a.userData.glow=c,a}createLegalCell(){const e=new Si(this.cellSize,this.cellSize,this.cellSize),t=new TS(e);t.translate(0,this.cellSize/2,0);const n=new bs({color:k.legal_unmeasured,transparent:!0,opacity:.55}),s=new Kr(t,n),r=new jt(new Si(this.cellSize,this.cellSize,this.cellSize),new es);return r.position.y=this.cellSize/2,r.visible=!1,s.add(r),s}disposeMesh(e){e.traverse(t=>{const n=t.geometry;n&&n.dispose();const s=t.material;Array.isArray(s)?s.forEach(r=>r.dispose()):s&&s.dispose()})}voidMarkerPositions(e,t,n){const s=(e-(this.xValues.length-1)/2)*this.spacing,r=t*this.spacing,a=(n-(this.zValues.length-1)/2)*this.spacing,o=this.cellSize*.6,l=.1;return[s-o,r+l,a-o,s+o,r+l,a+o,s+o,r+l,a-o,s-o,r+l,a+o]}createVoidMarkers(e){const t=new Qt;t.setAttribute("position",new Ut(e,3));const n=new bs({color:k.void,transparent:!0,opacity:.32});this.voidMesh=new Kr(t,n),this.scene.add(this.voidMesh)}frameGrid(){const e=Fi();if(!(e!=null&&e.controls)||this.xValues.length===0||this.zValues.length===0)return;const t=(this.xValues.length-1)*this.spacing/2+this.cellSize,n=(this.zValues.length-1)*this.spacing/2+this.cellSize,s=(this.yValues.length-1)*this.spacing+this.cellSize,r=n+1.8,a=-.8;co(e,new V(-t,a,-n),new V(t,s,r),new V(0,s/2,0))}clearGrid(){this.cells.forEach(e=>{this.scene.remove(e),this.disposeMesh(e)}),this.cells.clear(),this.cellDataMap.clear(),this.cellHeights.clear(),this.axisLabelMeshes.forEach(e=>{this.scene.remove(e),this.disposeMesh(e)}),this.axisLabelMeshes=[],this.voidMesh&&(this.scene.remove(this.voidMesh),this.voidMesh.geometry.dispose(),Array.isArray(this.voidMesh.material)?this.voidMesh.material.forEach(e=>e.dispose()):this.voidMesh.material.dispose(),this.voidMesh=null)}applyAggregates(){this.visible&&(xe.aggregates.forEach((e,t)=>{const n=this.cellDataMap.get(t);n&&(n.status="measured",n.coordinate={...e.coordinate},n.metrics={val_acc:ts(e.acc),val_acc_std:nb(e.acc),walltime_s:ts(e.walltime),param_count:ts(e.params),n_seeds:e.acc.length},n.curve=ib(e.curves),n.pareto=e.pareto,n.chance=xe.chance,n.requiredSeeds=xe.requiredSeeds,n.runId=xe.runId??void 0,this.updateCellVisual(t,n,e.pareto))}),this.updateLegendAxes())}pillarHeight(e){var t;return dv.lerp(.4,3.4,((t=e.metrics)==null?void 0:t.val_acc)??0)}updateCellVisual(e,t,n){const s=this.cells.get(e);if(!s)return;const r=s.position.clone(),a=s.userData.glow;a&&s.remove(a),this.scene.remove(s),this.disposeMesh(s);const o=this.createMeasuredCell(t);o.position.copy(r),o.userData.cellKey=e;const l=this.pillarHeight(t),c=this.cellHeights.get(e)??0;if(this.cellHeights.set(e,l),o.scale.y=l>0?Math.min(1,Math.max(c/l,.001)):1,n){const h=new nu(this.cellSize*.6,this.cellSize*.8,32),u=new es({color:k.pareto,side:Fn,transparent:!0,opacity:.6}),d=new jt(h,u);d.rotation.x=-Math.PI/2,d.position.y=.05,o.add(d),o.userData.paretoRing=d}this.scene.add(o),this.cells.set(e,o)}selectCell(e){this.selectedCell=e;const t=this.cellDataMap.get(e);t&&window.dispatchEvent(new CustomEvent("cell-selected",{detail:t}))}update(e){if(!this.visible){this.hideReadout();return}const t=1-Math.exp(-e*8);this.cells.forEach((a,o)=>{const l=this.cellDataMap.get(o);if((l==null?void 0:l.status)==="measured"&&a instanceof jt&&a.material instanceof Jr){a.scale.y<1&&(a.scale.y=Math.min(1,a.scale.y+(1-a.scale.y)*t));const c=a.userData.glow;c&&(c.material.opacity=.1+.1*Math.sin(Date.now()*.003));const h=a.userData.paretoRing;h&&(h.material.opacity=.4+.2*Math.sin(Date.now()*.005))}}),this.raycaster.setFromCamera(this.mouse,this.camera);const n=this.raycaster.intersectObjects(Array.from(this.cells.values()),!0);let s=null;n.length>0&&(s=this.pickCell(n)),s||(s=this.voidCellUnderCursor()),s!==this.hoveredCell&&(this.hoveredCell&&this.highlightCell(this.hoveredCell,!1),this.hoveredCell=s,s&&this.highlightCell(s,!0));const r=s?this.cellDataMap.get(s):void 0;r?this.showReadout(r):this.hideReadout()}pickCell(e){var n,s;let t=null;for(const r of e){const a=r.object.userData.cellKey||((n=r.object.parent)==null?void 0:n.userData.cellKey);if(a&&(t??(t=a),((s=this.cellDataMap.get(a))==null?void 0:s.status)==="measured"))return a}return t}voidCellUnderCursor(){if(!this.voidMesh)return null;const e=this.raycaster.params.Line.threshold;this.raycaster.params.Line.threshold=this.cellSize*.3;try{const t=this.raycaster.intersectObject(this.voidMesh,!1);return t.length===0?null:this.cellAt(t[0].point)}finally{this.raycaster.params.Line.threshold=e}}cellAt(e){const t=Math.round(e.x/this.spacing+(this.xValues.length-1)/2),n=Math.round(e.y/this.spacing),s=Math.round(e.z/this.spacing+(this.zValues.length-1)/2);return t<0||t>=this.xValues.length||n<0||n>=this.yValues.length||s<0||s>=this.zValues.length?null:wi(this.xValues[t],this.yValues[n],this.zValues[s])}highlightCell(e,t){var r;const n=this.cells.get(e);if(!n)return;const s=(r=this.renderer)==null?void 0:r.domElement;if(s&&(s.style.cursor=t&&this.isCellActionable(e)?"pointer":"grab"),n instanceof jt&&n.material instanceof Jr){t?(n.userData.originalEmissive=n.material.emissiveIntensity,n.userData.originalScale=n.scale.y,n.material.emissiveIntensity=(n.userData.originalEmissive||.5)+.5,n.scale.y=Math.min(1.05,n.scale.y*1.08)):(n.userData.originalEmissive!==void 0&&(n.material.emissiveIntensity=n.userData.originalEmissive),n.userData.originalScale!==void 0&&(n.scale.y=n.userData.originalScale));return}n instanceof Kr&&n.material instanceof bs&&(t?(n.userData.originalOpacity=n.material.opacity,n.material.opacity=.95,n.material.linewidth=2):n.userData.originalOpacity!==void 0&&(n.material.opacity=n.userData.originalOpacity,n.material.linewidth=1))}isCellActionable(e){const t=this.cellDataMap.get(e);return t?t.status==="legal"||t.status==="measured":!1}}const Ks=new hb;Zn.register(Ks);const ub={space:{glyph:"▦",kind:"solid"},terrain:{glyph:"▲",kind:"solid"},frontier:{glyph:"◭",kind:"solid"},layers:{glyph:"▤",kind:"solid"},multirun:{glyph:"▣",kind:"solid"},matrix:{glyph:"▩",kind:"mark"},multiples:{glyph:"⊞",kind:"mark"},uncertainty:{glyph:"◌",kind:"mark"},ledger:{glyph:"☰",kind:"mark"},contrast:{glyph:"◐",kind:"mark"},basin:{glyph:"◡",kind:"mark"},"trained-basin":{glyph:"◠",kind:"mark"},cost:{glyph:"▮",kind:"bar"},flow:{glyph:"⇉",kind:"bar"},effect:{glyph:"▯",kind:"bar"},spread:{glyph:"▬",kind:"bar"},convergence:{glyph:"∿",kind:"curve"},timeline:{glyph:"↦",kind:"curve"},trajectory:{glyph:"⟿",kind:"curve"},spectrum:{glyph:"〜",kind:"curve"},landscape:{glyph:"∿",kind:"curve"},"trained-trajectory":{glyph:"⟿",kind:"curve"},"trained-spectrum":{glyph:"〜",kind:"curve"},"trained-landscape":{glyph:"∿",kind:"curve"},slices:{glyph:"⁙",kind:"mark"}};function db(i){return ub[i]??{glyph:"•",kind:"mark"}}class fb{constructor(e){M(this,"canvas");M(this,"context");M(this,"visible",!1);this.canvas=document.createElement("canvas"),this.canvas.id=e,this.canvas.style.cssText=`
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      z-index: 50;
      display: none;
      background: var(--bg);
      pointer-events: none;
    `,document.body.appendChild(this.canvas),this.context=this.canvas.getContext("2d"),this.resize(),window.addEventListener("resize",()=>{this.resize()})}show(){this.visible=!0,this.canvas.style.display="block",this.resize(),this.begin()}hide(){this.visible=!1,this.canvas.style.display="none"}resize(){const e=Math.min(window.devicePixelRatio||1,2);this.canvas.width=Math.floor(window.innerWidth*e),this.canvas.height=Math.floor(window.innerHeight*e),this.context.setTransform(e,0,0,e,0,0)}begin(){const e=this.context;return e.clearRect(0,0,window.innerWidth,window.innerHeight),e.fillStyle="#0a0e14",e.fillRect(0,0,window.innerWidth,window.innerHeight),e}area(){const e=document.getElementById("discovery-legend"),t=e?e.getBoundingClientRect().right:0,n=Math.max(40,t+24),s=Math.max(200,window.innerWidth*kp-n);return{x:n,y:70,width:s,height:Math.max(200,window.innerHeight*Bp-70)}}}const Ue=new fb("stage-2d"),wn={top:64,right:36,bottom:62,left:78};function ga(i,e,t,n){i.fillStyle=k.text_primary,i.font="600 22px 'JetBrains Mono', monospace",i.textAlign="left",i.textBaseline="alphabetic",i.fillText(t,e.x,e.y+14),n&&(i.fillStyle=k.text_secondary,i.font="13px 'JetBrains Mono', monospace",i.fillText(n,e.x,e.y+40))}function aa(i,e,t=5){if(!Number.isFinite(i)||!Number.isFinite(e))return[i];if(i===e)return[i];const s=(e-i)/Math.max(1,t),r=10**Math.floor(Math.log10(s)),a=s/r,o=(a>=5?10:a>=2?5:a>=1?2:1)*r,l=Math.ceil(i/o)*o,c=[];for(let h=l;h<=e+o*1e-6;h+=o)c.push(Number(h.toFixed(10)));return c}function oa(i){const e=Math.abs(i);return e===0?"0":e>=1e3||e>=10?i.toFixed(0):e>=1?i.toFixed(1):e>=.01?i.toFixed(2):i.toExponential(1)}function Pn(i,e){const t=e.xMax-e.xMin;return t===0?e.rect.x:e.rect.x+(i-e.xMin)/t*e.rect.width}function Zt(i,e){const t=e.yMax-e.yMin;return t===0?e.rect.y+e.rect.height:e.rect.y+e.rect.height-(i-e.yMin)/t*e.rect.height}function rs(i,e,t){const n={x:e.x+wn.left,y:e.y+wn.top,width:Math.max(40,e.width-wn.left-wn.right),height:Math.max(40,e.height-wn.top-wn.bottom)},s={rect:n,xMin:t.xMin,xMax:t.xMax,yMin:t.yMin,yMax:t.yMax};ga(i,e,t.title,t.subtitle);const r=t.xTicks??aa(t.xMin,t.xMax,6),a=t.yTicks??aa(t.yMin,t.yMax,5);return i.strokeStyle=k.border,i.lineWidth=1,i.beginPath(),i.rect(n.x,n.y,n.width,n.height),i.stroke(),i.font="12px 'JetBrains Mono', monospace",i.fillStyle=k.text_secondary,r.forEach(o=>{const l=Pn(o,s);l<n.x-1||l>n.x+n.width+1||(i.strokeStyle=k.border,i.beginPath(),i.moveTo(l,n.y),i.lineTo(l,n.y+n.height),i.stroke(),i.textAlign="center",i.fillText(oa(o),l,n.y+n.height+20))}),a.forEach(o=>{const l=Zt(o,s);l<n.y-1||l>n.y+n.height+1||(i.strokeStyle=k.border,i.beginPath(),i.moveTo(n.x,l),i.lineTo(n.x+n.width,l),i.stroke(),i.textAlign="right",i.fillText(oa(o),n.x-10,l+4))}),i.fillStyle=k.text_secondary,i.font="13px 'JetBrains Mono', monospace",i.textAlign="center",i.fillText(t.xLabel,n.x+n.width/2,n.y+n.height+46),i.save(),i.translate(n.x-56,n.y+n.height/2),i.rotate(-Math.PI/2),i.textAlign="center",i.fillText(t.yLabel,0,0),i.restore(),s}function Rh(i,e,t){const n=e.split(/\s+/).filter(a=>a.length>0),s=[];let r="";return n.forEach(a=>{const o=r?`${r} ${a}`:a;if(r&&i.measureText(o).width>t){s.push(r),r=a;return}r=o}),r&&s.push(r),s}function _n(i,e,t){i.fillStyle=k.text_secondary,i.font="12px 'JetBrains Mono', monospace",i.textAlign="left",i.textBaseline="alphabetic",i.fillText(t,e.x,e.y+e.height+40)}function zp(i,e,t){const n={x:e.x+wn.left,y:e.y+wn.top,width:Math.max(40,e.width-wn.left-wn.right),height:Math.max(40,e.height-wn.top-wn.bottom)},s=n.width/Math.max(1,t.categories.length),r={rect:n,yMin:t.yMin,yMax:t.yMax,categories:t.categories,bandWidth:s,band:l=>n.x+s*(l+.5)},a={rect:n,yMin:t.yMin,yMax:t.yMax};return ga(i,e,t.title,t.subtitle),i.strokeStyle=k.border,i.lineWidth=1,i.strokeRect(n.x+.5,n.y+.5,n.width-1,n.height-1),i.font="12px 'JetBrains Mono', monospace",i.fillStyle=k.text_secondary,(t.yTicks??aa(t.yMin,t.yMax,5)).forEach(l=>{const c=Zt(l,a);c<n.y-1||c>n.y+n.height+1||(i.strokeStyle=k.border,i.beginPath(),i.moveTo(n.x,c),i.lineTo(n.x+n.width,c),i.stroke(),i.textAlign="right",i.fillText(oa(l),n.x-10,c+4))}),i.textAlign="center",i.textBaseline="top",t.categories.forEach((l,c)=>{ra(l,14).forEach((h,u)=>{i.fillText(h,r.band(c),n.y+n.height+12+u*16)})}),i.fillStyle=k.text_secondary,i.font="13px 'JetBrains Mono', monospace",i.save(),i.translate(n.x-56,n.y+n.height/2),i.rotate(-Math.PI/2),i.textAlign="center",i.textBaseline="alphabetic",i.fillText(t.yLabel,0,0),i.restore(),r}function Tl(i,e,t){i.font="12px 'JetBrains Mono', monospace";const n=t.rows.reduce((h,u)=>Math.max(h,i.measureText(u).width),0),s=Math.min(e.width*.45,Math.max(wn.left,n+24)),r={x:e.x+s,y:e.y+wn.top,width:Math.max(40,e.width-s-wn.right),height:Math.max(40,e.height-wn.top-wn.bottom)},a=r.height/Math.max(1,t.rows.length),o={rect:r,xMin:t.xMin,xMax:t.xMax,rows:t.rows,rowHeight:a,rowY:h=>r.y+a*(h+.5)},l={rect:r,xMin:t.xMin,xMax:t.xMax};return ga(i,e,t.title,t.subtitle),i.strokeStyle=k.border,i.lineWidth=1,i.strokeRect(r.x+.5,r.y+.5,r.width-1,r.height-1),i.font="12px 'JetBrains Mono', monospace",i.fillStyle=k.text_secondary,(t.xTicks??aa(t.xMin,t.xMax,6)).forEach(h=>{const u=Pn(h,l);u<r.x-1||u>r.x+r.width+1||(i.strokeStyle=k.border,i.beginPath(),i.moveTo(u,r.y),i.lineTo(u,r.y+r.height),i.stroke(),i.textAlign="center",i.textBaseline="alphabetic",i.fillText(oa(h),u,r.y+r.height+20))}),i.textAlign="right",i.textBaseline="middle",t.rows.forEach((h,u)=>{i.fillText(h,r.x-12,o.rowY(u))}),i.fillStyle=k.text_secondary,i.font="13px 'JetBrains Mono', monospace",i.textAlign="center",i.textBaseline="alphabetic",i.fillText(t.xLabel,r.x+r.width/2,r.y+r.height+46),o}class pb{constructor(){M(this,"id","cost");M(this,"name","The claim's cost");M(this,"group","process");M(this,"caption","The seeds each cell measured, against the seeds a claim is measured against.");M(this,"visible",!1);M(this,"drawn",!1)}enter(){this.visible=!0,Ue.show(),this.draw()}exit(){this.visible=!1,Ue.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}costs(){const e=xe.axes,t=xe.requiredSeeds,n=su(xe.aggregates,e),s=El(n,e);return n.map(r=>({cell:r,label:to(r,e,s),color:qt[r.coordinate.credit]??k.gradient,measured:r.seeds,required:t})).sort((r,a)=>a.required-a.measured-(r.required-r.measured))}draw(){const e=this.costs();if(e.length===0){this.drawn=!1;return}const t=Ue.begin(),n=Ue.area(),s=Math.max(xe.requiredSeeds,...e.map(c=>c.measured)),r=Tl(t,n,{xMin:0,xMax:s,rows:e.map(c=>c.label),title:"The claim's cost",subtitle:"the seeds measured, and the seeds a claim still needs",xLabel:"seeds"}),a=c=>r.rect.x+c/(r.xMax||1)*r.rect.width;e.forEach((c,h)=>{const u=r.rowY(h),d=Math.min(26,r.rowHeight*.5);t.fillStyle=k.bg_tertiary,t.fillRect(r.rect.x,u-d/2,a(c.required)-r.rect.x,d);const f=a(c.measured)-r.rect.x;t.fillStyle=c.color,t.fillRect(r.rect.x,u-d/2,f,d);const g=Math.max(0,c.required-c.measured);g>0&&(t.strokeStyle=k.warn,t.lineWidth=2,t.setLineDash([5,4]),t.beginPath(),t.moveTo(a(c.measured)+4,u),t.lineTo(a(c.required)-4,u),t.stroke(),t.setLineDash([])),t.strokeStyle=k.border,t.lineWidth=1,t.strokeRect(r.rect.x+.5,u-d/2,a(c.required)-r.rect.x-1,d-1),t.font="12px 'JetBrains Mono', monospace",t.textAlign="left",t.textBaseline="middle",t.fillStyle=k.text_secondary,t.fillText(`${c.measured} of ${c.required}`,r.rect.x+r.rect.width+12,u-8),g>0&&(t.fillStyle=k.warn,t.fillText(`${g} short`,r.rect.x+r.rect.width+12,u+9))});const o=a(xe.requiredSeeds);o>r.rect.x&&o<r.rect.x+r.rect.width&&(t.strokeStyle=k.text_secondary,t.lineWidth=1,t.setLineDash([3,4]),t.beginPath(),t.moveTo(o,r.rect.y),t.lineTo(o,r.rect.y+r.rect.height),t.stroke(),t.setLineDash([]));const l=e.reduce((c,h)=>c+Math.max(0,h.required-h.measured),0);_n(t,n,`the claim is ${l} seeds short over ${e.length} cells`),this.drawn=!0}}class mb{constructor(){M(this,"id","contrast");M(this,"name","The contrast");M(this,"group","analysis");M(this,"caption","The run's arms against one another, and whether the test could be run.");M(this,"key","d");M(this,"visible",!1);M(this,"drawn",!1)}enter(){this.visible=!0,Ue.show(),this.draw()}exit(){this.visible=!1,Ue.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}draw(){var h,u,d;const e=(h=xe.account)==null?void 0:h.contrast;if(!e||e.pairs.length===0){this.drawn=!1;return}const t=new Map,n=new Map;e.arms.forEach(f=>{t.set(f.value,f.mean),n.set(f.value,f.sd)});const s=Math.max(...e.arms.map(f=>f.mean),.001),r=Ue.begin(),a=Ue.area(),o=Tl(r,a,{xMin:0,xMax:s*1.15,rows:e.pairs.map(f=>`${f.a} vs ${f.b}`),title:"The contrast",subtitle:`the ${e.axis} arms on ${e.metric}, and what separates them`,xLabel:e.metric}),l=f=>o.rect.x+f/(o.xMax||1)*o.rect.width;e.pairs.forEach((f,g)=>{const v=o.rowY(g),p=l(t.get(f.a)??0),m=l(t.get(f.b)??0);r.fillStyle=`${k.gradient}33`,r.fillRect(Math.min(p,m),v-11,Math.abs(m-p),22),r.strokeStyle=k.border_bright,r.lineWidth=2,r.beginPath(),r.moveTo(p,v),r.lineTo(m,v),r.stroke(),[f.a,f.b].forEach(_=>{const b=l(t.get(_)??0);n.get(_),r.strokeStyle=qt[_]??k.gradient,r.lineWidth=1,r.beginPath(),r.moveTo(b,v-16),r.lineTo(b,v+16),r.stroke(),r.fillStyle=qt[_]??k.gradient,r.beginPath(),r.arc(b,v,6,0,Math.PI*2),r.fill(),r.font="11px 'JetBrains Mono', monospace",r.textAlign="center",r.textBaseline="bottom",r.fillStyle=qt[_]??k.gradient,r.fillText(_,b,v-18)}),r.font="12px 'JetBrains Mono', monospace",r.textAlign="left",r.textBaseline="middle",r.fillStyle=k.text_primary;const S=f.difference??0;r.fillText(`${S>=0?"+":"−"}${Math.abs(S).toFixed(3)}`,o.rect.x+o.rect.width+12,v-9),r.fillStyle=k.text_secondary,r.fillText(`${f.shared_cells} shared cell${f.shared_cells===1?"":"s"}`,o.rect.x+o.rect.width+12,v+9)});const c=e.test;_n(r,a,c.tested?`the test ran: p=${(u=c.p_value)==null?void 0:u.toFixed(4)} (alpha=${c.alpha}) · dz=${(d=c.cohens_dz)==null?void 0:d.toFixed(2)} · ${c.shared_cells} shared cells`:`no test ran: ${c.shared_cells} shared cell${c.shared_cells===1?"":"s"}, ${c.required_cells} required`),this.drawn=!0}}class gb{constructor(){M(this,"id","convergence");M(this,"name","Convergence");M(this,"group","process");M(this,"caption","Accuracy against epoch, one curve per arm, with the chance level under them.");M(this,"visible",!1);M(this,"drawn",!1)}enter(){this.visible=!0,Ue.show(),this.draw()}exit(){this.visible=!1,Ue.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}curves(){var n;const e=((n=xe.metrics)==null?void 0:n.records)??[],t=new Map;return e.forEach(s=>{var l,c;const r=(l=s==null?void 0:s.payload)==null?void 0:l.convergence_curve;if(!Array.isArray(r)||r.length===0)return;const a=((c=s==null?void 0:s.coordinate)==null?void 0:c.credit)??"",o=t.get(a)??new Map;r.forEach(h=>{if(typeof(h==null?void 0:h.epoch)!="number"||typeof(h==null?void 0:h.val_acc)!="number")return;const u=o.get(h.epoch)??[];u.push(h.val_acc),o.set(h.epoch,u)}),t.set(a,o)}),Array.from(t.entries()).map(([s,r])=>({arm:s,points:Array.from(r.entries()).sort((a,o)=>a[0]-o[0]).map(([a,o])=>({epoch:a,val_acc:o.reduce((l,c)=>l+c,0)/o.length}))}))}draw(){const e=this.curves();if(e.length===0){this.drawn=!1;return}const t=Ue.begin(),n=Ue.area(),s=xe.chance,r=Math.max(...e.flatMap(h=>h.points.map(u=>u.epoch))),a=Math.max(s,...e.flatMap(h=>h.points.map(u=>u.val_acc))),o=rs(t,n,{xMin:0,xMax:r,yMin:0,yMax:a,xLabel:"epoch",yLabel:"accuracy",title:"Convergence",subtitle:"the mean accuracy of each arm, epoch by epoch",xTicks:void 0,yTicks:void 0}),l=Zt(s,o);t.strokeStyle=k.chance_line,t.lineWidth=1.5,t.setLineDash([6,5]),t.beginPath(),t.moveTo(o.rect.x,l),t.lineTo(o.rect.x+o.rect.width,l),t.stroke(),t.setLineDash([]),e.forEach(h=>{const u=qt[h.arm]||k.gradient;t.strokeStyle=u,t.lineWidth=2.5,t.beginPath(),h.points.forEach((d,f)=>{const g=Pn(d.epoch,o),v=Zt(d.val_acc,o);f===0?t.moveTo(g,v):t.lineTo(g,v)}),t.stroke(),h.points.forEach(d=>{t.fillStyle=u,t.beginPath(),t.arc(Pn(d.epoch,o),Zt(d.val_acc,o),3,0,Math.PI*2),t.fill()})}),t.font="12px 'JetBrains Mono', monospace",t.textAlign="left",t.textBaseline="middle";let c=o.rect.y+10;e.forEach(h=>{const u=qt[h.arm]||k.gradient;t.fillStyle=u,t.fillRect(o.rect.x+o.rect.width+18,c-5,10,10),t.fillStyle=k.text_secondary,t.fillText(h.arm,o.rect.x+o.rect.width+34,c),c+=20}),_n(t,n,`${e.length} arms · the dashed line is the chance level (${s.toFixed(2)})`),this.drawn=!0}}function ru(i){const e=i.replace("#","");return[parseInt(e.slice(0,2),16),parseInt(e.slice(2,4),16),parseInt(e.slice(4,6),16)]}function nf(i){return`#${i.map(e=>Math.round(Math.max(0,Math.min(255,e))).toString(16).padStart(2,"0")).join("")}`}function sf(i,e,t){return[i[0]+(e[0]-i[0])*t,i[1]+(e[1]-i[1])*t,i[2]+(e[2]-i[2])*t]}const vb=ru(k.ramp_low),rf=ru(k.ramp_mid),xb=ru(k.ramp_high);function bi(i){const e=Math.max(0,Math.min(1,i));return e<=.5?nf(sf(vb,rf,e*2)):nf(sf(rf,xb,(e-.5)*2))}function Al(){const i=xe.dynamics;return!i||!i.stateful?null:i}function _b(i){var t;const e=((t=i.cell)==null?void 0:t.coordinate)??{};return[e.geometry,e.dynamics,e.credit].filter(n=>typeof n=="string"&&n.length>0).join(" · ")}function Cl(i){var n;const e=[],t=_b(i);return t&&e.push(t),((n=i.cell)==null?void 0:n.measured_by_run)===!1&&e.push("a cell of the space, not one the run measured"),i.trained===!1&&e.push("the weights are untrained"),e.join(" · ")}class Rl{constructor(){M(this,"key");M(this,"visible",!1);M(this,"drawn",!1)}enter(){this.visible=!0,Ue.show(),this.draw()}exit(){this.visible=!1,Ue.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}}class yb extends Rl{constructor(){super(...arguments);M(this,"id","trajectory");M(this,"name","The trajectory");M(this,"group","dynamics");M(this,"caption","Where the cell's own state went, step by step: the path it took through the space it moves in.");M(this,"key","j")}draw(){const t=Al(),n=t==null?void 0:t.trajectory;if(!t||!n||n.path.length<2){this.drawn=!1;return}const s=Ue.begin(),r=Ue.area(),a=n.path,o=a.map(_=>_[0]),l=a.map(_=>_[1]),c=.08,h=Math.min(...o),u=Math.max(...o),d=Math.min(...l),f=Math.max(...l),g=u-h||1,v=f-d||1,p=rs(s,r,{xMin:h-g*c,xMax:u+g*c,yMin:d-v*c,yMax:f+v*c,xLabel:n.axes[0]??"the direction the state moved",yLabel:n.axes[1]??"the direction across it",title:"The trajectory",subtitle:Cl(t)});for(let _=1;_<a.length;_+=1){const b=_/(a.length-1);s.strokeStyle=bi(b),s.lineWidth=2.5,s.beginPath(),s.moveTo(Pn(a[_-1][0],p),Zt(a[_-1][1],p)),s.lineTo(Pn(a[_][0],p),Zt(a[_][1],p)),s.stroke()}const m=(_,b,I)=>{const A=Pn(_[0],p),R=Zt(_[1],p);s.fillStyle=b,s.beginPath(),s.arc(A,R,5,0,Math.PI*2),s.fill(),s.font="12px 'JetBrains Mono', monospace",s.textAlign="left",s.textBaseline="middle",s.fillText(I,A+10,R)};m(a[0],k.text_primary,"where it started"),m(a[a.length-1],k.warn,"where it stopped");const S=n.error??[];if(S.length>1){const _=Math.min(...S),b=Math.max(...S),I=p.rect.height*.16,A=p.rect.y+p.rect.height-I*.5,R=N=>A-(N-_)/(b-_||1)*I*.5;s.strokeStyle=k.thermodynamic_contrast,s.lineWidth=1.5,s.beginPath(),S.forEach((N,w)=>{const y=p.rect.x+w/(S.length-1)*p.rect.width;w===0?s.moveTo(y,R(N)):s.lineTo(y,R(N))}),s.stroke(),s.font="11px 'JetBrains Mono', monospace",s.fillStyle=k.thermodynamic_contrast,s.textAlign="right",s.textBaseline="bottom",s.fillText("the prediction error",p.rect.x+p.rect.width,A-I*.6)}_n(s,r,t.verdict??""),this.drawn=!0}}class Sb extends Rl{constructor(){super(...arguments);M(this,"id","spectrum");M(this,"name","The spectrum");M(this,"group","dynamics");M(this,"caption","How fast a nudge grows along each direction: the exponents that say whether this dynamics settles.");M(this,"key","m")}draw(){const t=Al(),n=t==null?void 0:t.spectrum;if(!t||!n||n.length===0){this.drawn=!1;return}const s=Ue.begin(),r=Ue.area(),o=Math.max(...n.map(u=>Math.abs(u)),1e-6)*1.25,l=rs(s,r,{xMin:0,xMax:n.length,yMin:-o,yMax:o,xLabel:"direction",yLabel:"growth per step",title:"The spectrum",subtitle:Cl(t),xTicks:aa(0,n.length,6).filter(u=>Number.isInteger(u))}),c=Zt(0,l);s.strokeStyle=k.text_muted,s.lineWidth=1.5,s.beginPath(),s.moveTo(l.rect.x,c),s.lineTo(l.rect.x+l.rect.width,c),s.stroke();const h=l.rect.width/n.length;n.forEach((u,d)=>{const f=l.rect.x+h*(d+.5),g=Math.min(46,h*.5),v=Zt(u,l),p=u>0;s.fillStyle=p?k.warn:k.ok,s.fillRect(f-g/2,Math.min(v,c),g,Math.abs(v-c)),s.font="11px 'JetBrains Mono', monospace",s.fillStyle=p?k.warn:k.ok,s.textAlign="center",s.textBaseline=p?"bottom":"top",s.fillText(oa(u),f,p?v-5:v+5)}),_n(s,r,t.verdict??""),this.drawn=!0}}class bb extends Rl{constructor(){super(...arguments);M(this,"id","basin");M(this,"name","The basin");M(this,"group","dynamics");M(this,"caption","The states near the cell's own: how many come back, and how far the ones that do not stray.");M(this,"key","b")}draw(){const t=Al(),n=t==null?void 0:t.basin;if(!t||!n||n.paths.length===0){this.drawn=!1;return}const s=Ue.begin(),r=Ue.area(),a=n.paths,o=Math.max(...a.flatMap(h=>h.distances),1e-6),l=rs(s,r,{xMin:0,xMax:a[0].distances.length,yMin:0,yMax:o*1.1,xLabel:"steps after the nudge",yLabel:"distance from the attractor",title:"The basin",subtitle:Cl(t)}),c=n.radii;a.forEach(h=>{const u=c.indexOf(h.radius),d=c.length>1?u/(c.length-1):.5;s.strokeStyle=h.returned?k.ok:bi(d),s.lineWidth=2,s.beginPath(),h.distances.forEach((f,g)=>{const v=Pn(g,l),p=Zt(f,l);g===0?s.moveTo(v,p):s.lineTo(v,p)}),s.stroke()}),s.font="12px 'JetBrains Mono', monospace",s.textAlign="center",s.textBaseline="top",n.stability.forEach((h,u)=>{const d=l.rect.x+l.rect.width/c.length*(u+.5);s.fillStyle=h>0?k.ok:k.warn,s.fillText(`${Math.round(h*100)}% back`,d,l.rect.y+12),s.fillStyle=k.text_secondary,s.fillText(`nudge ${c[u]}`,d,l.rect.y+28)}),_n(s,r,t.verdict??""),this.drawn=!0}}class Mb extends Rl{constructor(){super(...arguments);M(this,"id","landscape");M(this,"name","The landscape");M(this,"group","dynamics");M(this,"caption","The cell's own energy over the ground its trajectory crossed, and the path it took across it.");M(this,"key","n")}draw(){const t=Al(),n=t==null?void 0:t.landscape,s=t==null?void 0:t.trajectory;if(!t||!n||n.grid.length===0){this.drawn=!1;return}const r=Ue.begin(),a=Ue.area(),o=n.grid,l=o.flat(),c=Math.min(...l),h=Math.max(...l),u=rs(r,a,{xMin:n.x[0],xMax:n.x[n.x.length-1],yMin:n.y[0],yMax:n.y[n.y.length-1],xLabel:"along the trajectory",yLabel:"across it",title:"The landscape",subtitle:Cl(t)}),d=u.rect.width/(n.x.length-1||1),f=u.rect.height/(n.y.length-1||1);r.save(),r.beginPath(),r.rect(u.rect.x,u.rect.y,u.rect.width,u.rect.height),r.clip(),o.forEach((_,b)=>{_.forEach((I,A)=>{const R=(I-c)/(h-c||1);r.fillStyle=bi(1-R);const N=u.rect.x+d*b,w=u.rect.y+u.rect.height-f*(A+1);r.fillRect(N,w,d+1,f+1)})}),r.restore(),s&&s.path.length>1&&(r.strokeStyle=k.text_primary,r.lineWidth=2,r.beginPath(),s.path.forEach((_,b)=>{const I=Pn(_[0],u),A=Zt(_[1],u);b===0?r.moveTo(I,A):r.lineTo(I,A)}),r.stroke());let g=0,v=0,p=Number.POSITIVE_INFINITY;o.forEach((_,b)=>_.forEach((I,A)=>{I<p&&(p=I,g=b,v=A)}));const m=Pn(n.x[g],u),S=Zt(n.y[v],u);r.strokeStyle=k.ok,r.lineWidth=2,r.beginPath(),r.arc(m,S,7,0,Math.PI*2),r.stroke(),r.font="12px 'JetBrains Mono', monospace",r.fillStyle=k.ok,r.textAlign="left",r.textBaseline="bottom",r.fillText("the lowest ground",m+11,S-6),_n(r,a,t.verdict??""),this.drawn=!0}}function Pl(){const i=xe.trainedDynamics;return!i||!i.stateful?null:i}function wb(i){var t;const e=((t=i.cell)==null?void 0:t.coordinate)??{};return[e.geometry,e.dynamics,e.credit].filter(n=>typeof n=="string"&&n.length>0).join(" · ")}function Ll(i){var n;const e=[],t=wb(i);return t&&e.push(t),((n=i.cell)==null?void 0:n.measured_by_run)===!1&&e.push("a cell of the space, not one the run measured"),i.trained===!0&&e.push("the weights were trained first"),e.join(" · ")}class Dl{constructor(){M(this,"key");M(this,"visible",!1);M(this,"drawn",!1)}enter(){this.visible=!0,Ue.show(),this.draw()}exit(){this.visible=!1,Ue.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}}class Eb extends Dl{constructor(){super(...arguments);M(this,"id","trained-trajectory");M(this,"name","The trained trajectory");M(this,"group","trained");M(this,"caption","Where the trained cell's state went, step by step: the path it took through the space it moves in.");M(this,"key","g")}draw(){const t=Pl(),n=t==null?void 0:t.trajectory;if(!t||!n||n.path.length<2){this.drawn=!1;return}const s=Ue.begin(),r=Ue.area(),a=n.path,o=a.map(_=>_[0]),l=a.map(_=>_[1]),c=.08,h=Math.min(...o),u=Math.max(...o),d=Math.min(...l),f=Math.max(...l),g=u-h||1,v=f-d||1,p=rs(s,r,{xMin:h-g*c,xMax:u+g*c,yMin:d-v*c,yMax:f+v*c,xLabel:n.axes[0]??"the direction the state moved",yLabel:n.axes[1]??"the direction across it",title:"The trained trajectory",subtitle:Ll(t)});for(let _=1;_<a.length;_+=1){const b=_/(a.length-1);s.strokeStyle=bi(b),s.lineWidth=2.5,s.beginPath(),s.moveTo(Pn(a[_-1][0],p),Zt(a[_-1][1],p)),s.lineTo(Pn(a[_][0],p),Zt(a[_][1],p)),s.stroke()}const m=(_,b,I)=>{const A=Pn(_[0],p),R=Zt(_[1],p);s.fillStyle=b,s.beginPath(),s.arc(A,R,5,0,Math.PI*2),s.fill(),s.font="12px 'JetBrains Mono', monospace",s.textAlign="left",s.textBaseline="middle",s.fillText(I,A+10,R)};m(a[0],k.text_primary,"where it started"),m(a[a.length-1],k.warn,"where it stopped");const S=n.error??[];if(S.length>1){const _=Math.min(...S),b=Math.max(...S),I=p.rect.height*.16,A=p.rect.y+p.rect.height-I*.5,R=N=>A-(N-_)/(b-_||1)*I*.5;s.strokeStyle=k.thermodynamic_contrast,s.lineWidth=1.5,s.beginPath(),S.forEach((N,w)=>{const y=p.rect.x+w/(S.length-1)*p.rect.width;w===0?s.moveTo(y,R(N)):s.lineTo(y,R(N))}),s.stroke(),s.font="11px 'JetBrains Mono', monospace",s.fillStyle=k.thermodynamic_contrast,s.textAlign="right",s.textBaseline="bottom",s.fillText("the prediction error",p.rect.x+p.rect.width,A-I*.6)}_n(s,r,t.verdict??""),this.drawn=!0}}class Tb extends Dl{constructor(){super(...arguments);M(this,"id","trained-spectrum");M(this,"name","The trained spectrum");M(this,"group","trained");M(this,"caption","How fast a nudge grows along each direction after training: the exponents that say whether this dynamics settles.");M(this,"key","i")}draw(){const t=Pl(),n=t==null?void 0:t.spectrum;if(!t||!n||n.length===0){this.drawn=!1;return}const s=Ue.begin(),r=Ue.area(),o=Math.max(...n.map(u=>Math.abs(u)),1e-6)*1.25,l=rs(s,r,{xMin:0,xMax:n.length,yMin:-o,yMax:o,xLabel:"direction",yLabel:"growth per step",title:"The trained spectrum",subtitle:Ll(t),xTicks:aa(0,n.length,6).filter(u=>Number.isInteger(u))}),c=Zt(0,l);s.strokeStyle=k.text_muted,s.lineWidth=1.5,s.beginPath(),s.moveTo(l.rect.x,c),s.lineTo(l.rect.x+l.rect.width,c),s.stroke();const h=l.rect.width/n.length;n.forEach((u,d)=>{const f=l.rect.x+h*(d+.5),g=Math.min(46,h*.5),v=Zt(u,l),p=u>0;s.fillStyle=p?k.warn:k.ok,s.fillRect(f-g/2,Math.min(v,c),g,Math.abs(v-c)),s.font="11px 'JetBrains Mono', monospace",s.fillStyle=p?k.warn:k.ok,s.textAlign="center",s.textBaseline=p?"bottom":"top",s.fillText(oa(u),f,p?v-5:v+5)}),_n(s,r,t.verdict??""),this.drawn=!0}}class Ab extends Dl{constructor(){super(...arguments);M(this,"id","trained-basin");M(this,"name","The trained basin");M(this,"group","trained");M(this,"caption","The states near the trained cell's own: how many come back, and how far the ones that do not stray.");M(this,"key","k")}draw(){const t=Pl(),n=t==null?void 0:t.basin;if(!t||!n||n.paths.length===0){this.drawn=!1;return}const s=Ue.begin(),r=Ue.area(),a=n.paths,o=Math.max(...a.flatMap(h=>h.distances),1e-6),l=rs(s,r,{xMin:0,xMax:a[0].distances.length,yMin:0,yMax:o*1.1,xLabel:"steps after the nudge",yLabel:"distance from the attractor",title:"The trained basin",subtitle:Ll(t)}),c=n.radii;a.forEach(h=>{const u=c.indexOf(h.radius),d=c.length>1?u/(c.length-1):.5;s.strokeStyle=h.returned?k.ok:bi(d),s.lineWidth=2,s.beginPath(),h.distances.forEach((f,g)=>{const v=Pn(g,l),p=Zt(f,l);g===0?s.moveTo(v,p):s.lineTo(v,p)}),s.stroke()}),s.font="12px 'JetBrains Mono', monospace",s.textAlign="center",s.textBaseline="top",n.stability.forEach((h,u)=>{const d=l.rect.x+l.rect.width/c.length*(u+.5);s.fillStyle=h>0?k.ok:k.warn,s.fillText(`${Math.round(h*100)}% back`,d,l.rect.y+12),s.fillStyle=k.text_secondary,s.fillText(`nudge ${c[u]}`,d,l.rect.y+28)}),_n(s,r,t.verdict??""),this.drawn=!0}}class Cb extends Dl{constructor(){super(...arguments);M(this,"id","trained-landscape");M(this,"name","The trained landscape");M(this,"group","trained");M(this,"caption","The trained cell's own energy over the ground its trajectory crossed, and the path it took across it.");M(this,"key","o")}draw(){const t=Pl(),n=t==null?void 0:t.landscape,s=t==null?void 0:t.trajectory;if(!t||!n||n.grid.length===0){this.drawn=!1;return}const r=Ue.begin(),a=Ue.area(),o=n.grid,l=o.flat(),c=Math.min(...l),h=Math.max(...l),u=rs(r,a,{xMin:n.x[0],xMax:n.x[n.x.length-1],yMin:n.y[0],yMax:n.y[n.y.length-1],xLabel:"along the trajectory",yLabel:"across it",title:"The trained landscape",subtitle:Ll(t)}),d=u.rect.width/(n.x.length-1||1),f=u.rect.height/(n.y.length-1||1);r.save(),r.beginPath(),r.rect(u.rect.x,u.rect.y,u.rect.width,u.rect.height),r.clip(),o.forEach((_,b)=>{_.forEach((I,A)=>{const R=(I-c)/(h-c||1);r.fillStyle=bi(1-R);const N=u.rect.x+d*b,w=u.rect.y+u.rect.height-f*(A+1);r.fillRect(N,w,d+1,f+1)})}),r.restore(),s&&s.path.length>1&&(r.strokeStyle=k.text_primary,r.lineWidth=2,r.beginPath(),s.path.forEach((_,b)=>{const I=Pn(_[0],u),A=Zt(_[1],u);b===0?r.moveTo(I,A):r.lineTo(I,A)}),r.stroke());let g=0,v=0,p=Number.POSITIVE_INFINITY;o.forEach((_,b)=>_.forEach((I,A)=>{I<p&&(p=I,g=b,v=A)}));const m=Pn(n.x[g],u),S=Zt(n.y[v],u);r.strokeStyle=k.ok,r.lineWidth=2,r.beginPath(),r.arc(m,S,7,0,Math.PI*2),r.stroke(),r.font="12px 'JetBrains Mono', monospace",r.fillStyle=k.ok,r.textAlign="left",r.textBaseline="bottom",r.fillText("the lowest ground",m+11,S-6),_n(r,a,t.verdict??""),this.drawn=!0}}class Rb{constructor(){M(this,"id","effect");M(this,"name","The effect");M(this,"group","analysis");M(this,"caption","Which axis moved the objective, and which the run held fixed: the run's attribution, and its limits.");M(this,"key","e");M(this,"visible",!1);M(this,"drawn",!1)}enter(){this.visible=!0,Ue.show(),this.draw()}exit(){this.visible=!1,Ue.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}draw(){const e=xe.attribution,t=(e==null?void 0:e.axes)??[];if(!e||t.length===0){this.drawn=!1;return}const n=Ue.begin(),s=Ue.area(),r=t.flatMap(c=>c.values.map(h=>h.mean)),a=Math.max(...r,.1),o=zp(n,s,{yMin:0,yMax:a*1.15,categories:t.map(c=>c.axis),title:"The effect",subtitle:e.summary,yLabel:e.metric||"the objective"}),l=c=>o.rect.y+o.rect.height-c/(o.yMax||1)*o.rect.height;t.forEach((c,h)=>{const u=o.band(h),d=Math.min(46,o.bandWidth*.4);if(c.varied&&c.values.length>1){const v=Math.min(...c.values.map(b=>b.mean)),p=Math.max(...c.values.map(b=>b.mean)),m=l(p),S=l(v);n.fillStyle=`${k.gradient}33`,n.fillRect(u-d/2,m,d,S-m),n.strokeStyle=k.gradient,n.lineWidth=1,n.strokeRect(u-d/2,m,d,S-m);const _=[];c.values.forEach(b=>{const I=l(b.mean),A=qt[b.value]??k.gradient;n.fillStyle=A,n.beginPath(),n.arc(u,I,5,0,Math.PI*2),n.fill();let R=I;for(;_.some(N=>Math.abs(N-R)<14);)R+=14;_.push(R),n.font="12px 'JetBrains Mono', monospace",n.textAlign="left",n.textBaseline="middle",n.fillStyle=A,n.fillText(b.value,u+d/2+10,R)});return}const f=c.values[0];if(!f)return;const g=l(f.mean);n.strokeStyle=k.text_muted,n.lineWidth=2,n.beginPath(),n.moveTo(u-7,g),n.lineTo(u+7,g),n.stroke(),n.font="12px 'JetBrains Mono', monospace",n.textAlign="center",n.textBaseline="top",n.fillStyle=k.text_muted,n.fillText(f.value,u,g+10)}),_n(n,s,e.reason),this.drawn=!0}}const Pb=84,Lb=92;class Db{constructor(){M(this,"id","flow");M(this,"name","The flow");M(this,"group","process");M(this,"caption","The run's cells, stage by stage: what each one handled, and what the gate refused.");M(this,"key","f");M(this,"visible",!1);M(this,"drawn",!1)}enter(){this.visible=!0,Ue.show(),this.draw()}exit(){this.visible=!1,Ue.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}draw(){const e=xe.flow,t=(e==null?void 0:e.stages)??[];if(!e||t.length===0){this.drawn=!1;return}const n=Ue.begin(),s=Ue.area();ga(n,s,"The flow","the run's cells, from the space to the evidence");const r=s.y+s.height-Lb,a=Math.max(120,r-(s.y+Pb)),o=Math.max(1,...t.map(c=>c.count+c.refused)),l=s.width/t.length;n.strokeStyle=k.border,n.lineWidth=1,n.beginPath(),n.moveTo(s.x,r+.5),n.lineTo(s.x+s.width,r+.5),n.stroke(),t.forEach((c,h)=>{const u=s.x+l*(h+.5),d=l*.56,f=p=>p/o*a,g=f(c.count),v=r-g;if(n.fillStyle=c.kind==="records"?k.measured:k.gradient,n.fillRect(u-d/2,v,d,Math.max(g,2)),c.refused>0){const p=f(c.refused);n.fillStyle=k.void,n.fillRect(u-d/2,v-p,d,p),n.font="12px 'JetBrains Mono', monospace",n.textAlign="center",n.textBaseline="bottom",n.fillStyle=k.void,n.fillText(`${c.refused} refused`,u,v-p-6)}c.count>0&&(n.font="600 15px 'JetBrains Mono', monospace",n.textAlign="center",n.textBaseline="bottom",n.fillStyle=k.text_primary,n.fillText(`${c.count}`,u,v-6)),n.font="12px 'JetBrains Mono', monospace",n.textAlign="center",n.textBaseline="top",n.fillStyle=c.count>0?k.text_secondary:k.text_muted,Rh(n,c.action,l-8).slice(0,2).forEach((p,m)=>{n.fillText(p,u,r+10+m*16)})}),this.drawRefusals(n,s),_n(n,s,e.summary),this.drawn=!0}drawRefusals(e,t){const n=xe.space,s=(n==null?void 0:n.void_rules)??{},r=Object.keys(s),a=t.x;if(e.textAlign="left",e.textBaseline="alphabetic",e.font="600 13px 'JetBrains Mono', monospace",e.fillStyle=k.text_secondary,e.fillText("the rules that refuse",a,t.y+80),r.length===0){e.font="12px 'JetBrains Mono', monospace",e.fillStyle=k.text_muted,e.fillText("no cell of this slice is refused",a,t.y+102);return}e.font="12px 'JetBrains Mono', monospace",r.slice(0,6).forEach((o,l)=>{const c=t.y+102+l*18;e.fillStyle=k.void,e.fillText(o,a,c),e.fillStyle=k.text_secondary,e.textAlign="right",e.fillText(`${s[o]} cells`,a+280,c),e.textAlign="left"})}}function Es(i){i.traverse(e=>{var s;const t=e;(s=t.geometry)==null||s.dispose();const n=t.material;Array.isArray(n)?n.forEach(r=>r.dispose()):n==null||n.dispose()})}const Br=6.4,Fa=4,zr=5;class Ib{constructor(){M(this,"id","frontier");M(this,"name","Frontier");M(this,"group","space");M(this,"caption","Every measured cell in accuracy, speed and parameters; the frontier is the line nothing beat.");M(this,"sceneGroup",new oi);M(this,"visible",!1);M(this,"drawn",!1);M(this,"framed",!1);M(this,"accuracy",{min:0,max:0,span:0})}enter(){this.visible=!0;const e=Fi();e&&e.scene.add(this.sceneGroup),this.draw(!0)}exit(){var e;this.visible=!1,(e=this.sceneGroup.parent)==null||e.remove(this.sceneGroup),Es(this.sceneGroup),this.sceneGroup=new oi,this.drawn=!1,this.framed=!1}refresh(){this.visible&&this.draw(!1)}ready(){return this.drawn}points(){var u,d;const e=((u=xe.metrics)==null?void 0:u.records)??[],t=((d=xe.metrics)==null?void 0:d.pareto)??[],n=xe.chance,s=[],r=[],a=[];e.forEach(f=>{const g=(f==null?void 0:f.payload)??{};typeof g.val_acc=="number"&&s.push(g.val_acc),typeof g.walltime_s=="number"&&g.walltime_s>0&&r.push(1/g.walltime_s),typeof g.param_count=="number"&&g.param_count>0&&a.push(Math.log10(g.param_count))});const o=Dc([...s,n]);this.accuracy=o;const l=Dc(r),c=Dc(a),h=[];return e.forEach((f,g)=>{var S;const v=(f==null?void 0:f.payload)??{};if(typeof v.val_acc!="number")return;const p=typeof v.walltime_s=="number"&&v.walltime_s>0?1/v.walltime_s:null,m=typeof v.param_count=="number"&&v.param_count>0?Math.log10(v.param_count):null;h.push({x:p===null||l.span===0?0:((p-l.min)/l.span-.5)*Br,y:o.span===0?0:(v.val_acc-o.min)/o.span*Fa,z:m===null||c.span===0?0:((m-c.min)/c.span-.5)*zr,arm:((S=f==null?void 0:f.coordinate)==null?void 0:S.credit)??"",pareto:t[g]===!0})}),h}draw(e){const t=this.points();if(t.length===0){this.drawn=!1;return}this.clear(),this.addPoints(t),this.addFront(t),this.addChanceFloor(),this.addLabels(),this.drawn=!0,(e||!this.framed)&&(this.frame(),this.framed=!0)}clear(){[...this.sceneGroup.children].forEach(e=>{this.sceneGroup.remove(e),Es(e)})}addPoints(e){const t=[],n=[];e.forEach(o=>{t.push(o.x,o.y,o.z);const l=new it(qt[o.arm]||k.gradient);n.push(l.r,l.g,l.b)});const s=new Qt;s.setAttribute("position",new Ut(t,3)),s.setAttribute("color",new Ut(n,3));const r=new Np({size:.26,sizeAttenuation:!0,vertexColors:!0,map:ob(),alphaTest:.4,transparent:!0,opacity:.95});this.sceneGroup.add(new ES(s,r));const a=e.filter(o=>o.pareto);a.length!==0&&a.forEach(o=>{const l=lb(k.pareto,.26);l.position.set(o.x,o.y,o.z),this.sceneGroup.add(l)})}addFront(e){const t=e.filter(a=>a.pareto).sort((a,o)=>a.y-o.y);if(t.length<2)return;const n=[];t.forEach(a=>n.push(a.x,a.y,a.z));const s=new Qt;s.setAttribute("position",new Ut(n,3));const r=new Up(s,new AS({color:k.pareto,dashSize:.22,gapSize:.16,transparent:!0,opacity:.85}));r.computeLineDistances(),this.sceneGroup.add(r)}addChanceFloor(){const e=xe.chance,t=this.accuracy;if(t.span===0)return;const n=(e-t.min)/t.span*Fa,s=new lo(Br*1.02,zr*1.02);s.rotateX(-Math.PI/2);const r=new jt(s,new es({color:k.chance_line,transparent:!0,opacity:.07,side:Fn,depthWrite:!1}));r.position.y=n,this.sceneGroup.add(r);const a=vn("chance",.24,new Ei({color:k.chance_line,sizeAttenuation:!0}));a.position.set(Br/2+.3,n,zr/2+.3),this.sceneGroup.add(a)}addLabels(){const e=new Ei({color:13227232,sizeAttenuation:!0}),t=vn("speed 1/s",.26,e);t.position.set(Br/2+.6,.1,0),this.sceneGroup.add(t);const n=vn("accuracy",.26,e);n.position.set(0,Fa+.4,0),this.sceneGroup.add(n);const s=vn("parameters",.26,e);s.position.set(0,.1,zr/2+.7),this.sceneGroup.add(s)}frame(){const e=Fi();e&&co(e,new V(-Br/2-.6,-.2,-zr/2-.6),new V(Br/2+.6,Fa+.6,zr/2+.6),new V(0,Fa/2,0))}}function Dc(i){const e=i.filter(s=>Number.isFinite(s));if(e.length===0)return{min:0,max:0,span:0};const t=Math.min(...e),n=Math.max(...e);return{min:t,max:n,span:n-t}}const ka=1.7,Yn=1,af=.9,Ub=new V(.72,.24,.65);class Nb{constructor(){M(this,"id","layers");M(this,"name","Layers");M(this,"group","space");M(this,"key","y");M(this,"caption","The space cut into sheets: the lit ones are the cells the run measured.");M(this,"sceneGroup",new oi);M(this,"visible",!1);M(this,"drawn",!1);M(this,"framed",!1)}enter(){this.visible=!0;const e=Fi();e&&e.scene.add(this.sceneGroup),this.draw(!0)}exit(){var e;this.visible=!1,(e=this.sceneGroup.parent)==null||e.remove(this.sceneGroup),Es(this.sceneGroup),this.sceneGroup=new oi,this.drawn=!1,this.framed=!1}refresh(){this.visible&&this.draw(!1)}ready(){return this.drawn}sheets(){const e=xe.space;if(!e)return{sheets:[],nx:0,ny:0};const t=xe.axes,n=e.values[t.x]??[],s=e.values[t.y]??[],r=e.values[t.z]??[];return{sheets:r.map((o,l)=>{const c=[];let h=0;return n.forEach((u,d)=>{s.forEach((f,g)=>{const v=wi(u,f,o),p=xe.spaceCells.get(v),m=xe.aggregates.get(v),S=m&&m.acc.length>0?ts(m.acc):0;if((p==null?void 0:p.status)==="void"){c.push({status:"void",accuracy:0,arm:"",x:(d-(n.length-1)/2)*Yn,y:(g-(s.length-1)/2)*Yn});return}if(S>0){h+=1,c.push({status:"measured",accuracy:S,arm:(m==null?void 0:m.coordinate.credit)??"",x:(d-(n.length-1)/2)*Yn,y:(g-(s.length-1)/2)*Yn});return}c.push({status:"gap",accuracy:0,arm:"",x:(d-(n.length-1)/2)*Yn,y:(g-(s.length-1)/2)*Yn})})}),{value:o,height:(l-(r.length-1)/2)*ka,cells:c,measured:h}}),nx:n.length,ny:s.length}}draw(e){const{sheets:t,nx:n,ny:s}=this.sheets();if(t.length===0){this.drawn=!1;return}this.clear();const r=[],a=[],o=[],l=[];let c=0;t.forEach(u=>{u.cells.forEach(d=>{d.status==="measured"&&(c=Math.max(c,d.accuracy))})});const h=c>0?c:1;t.forEach(u=>{u.cells.forEach(d=>{const f=new it(d.status==="measured"?qt[d.arm]||k.gradient:d.status==="void"?k.void:k.border_bright);d.status==="measured"?f.multiplyScalar(.65+.35*(d.accuracy/h)):f.multiplyScalar(.3);const g=d.status==="measured"?o:r,v=d.status==="measured"?l:a,p=Yn/2;g.push(d.x-p,u.height,d.y-p,d.x+p,u.height,d.y-p,d.x+p,u.height,d.y+p,d.x-p,u.height,d.y+p);for(let m=0;m<4;m+=1)v.push(f.r,f.g,f.b)})}),r.length>0&&this.sceneGroup.add(new jt(of(r,a),new es({vertexColors:!0,transparent:!0,opacity:.11,side:Fn,depthWrite:!1}))),o.length>0&&this.sceneGroup.add(new jt(of(o,l),new es({vertexColors:!0,side:Fn}))),this.addPins(t),this.addSheetEdges(t,n,s),this.addLabels(t,n,s),this.drawn=t.some(u=>u.measured>0),(e||!this.framed)&&(this.frame(t,n,s),this.framed=!0)}addPins(e){e.forEach(t=>{t.cells.forEach(n=>{if(n.status!=="measured")return;const s=new it(qt[n.arm]||k.gradient),r=new Si(.22,af,.22);r.translate(0,af/2,0);const a=new Jr({color:s,emissive:s,emissiveIntensity:.55,roughness:.4,metalness:.2}),o=new jt(r,a);o.position.set(n.x,t.height,n.y),this.sceneGroup.add(o)})})}addSheetEdges(e,t,n){const s=[],r=t*Yn/2,a=n*Yn/2;if(e.forEach(l=>{const c=[[-r,-a],[r,-a],[r,a],[-r,a]];c.forEach((h,u)=>{const d=c[(u+1)%c.length];s.push(h[0],l.height,h[1],d[0],l.height,d[1])})}),s.length===0)return;const o=new Qt;o.setAttribute("position",new Ut(s,3)),this.sceneGroup.add(new Kr(o,new bs({color:k.border_bright,transparent:!0,opacity:.65})))}addLabels(e,t,n){const s=xe.axes,r=new Ei({color:13227232,sizeAttenuation:!0}),a=new Ei({color:9148584,sizeAttenuation:!0}),o=t*Yn/2,l=n*Yn/2;e.forEach(d=>{const f=vn(d.value,.26,a);f.position.set(-o-.85,d.height,l),this.sceneGroup.add(f)});const c=vn(s.z,.28,r);c.position.set(-o-.85,e.length*ka*.5,-l),this.sceneGroup.add(c);const h=vn(s.x,.28,r);h.position.set(o+.9,-ka,l),this.sceneGroup.add(h);const u=vn(s.y,.28,r);u.position.set(o+.9,-ka,-l-.6),this.sceneGroup.add(u)}frame(e,t,n){const s=Fi();if(!s||e.length===0)return;const r=t*Yn/2,a=n*Yn/2,o=e.length*ka/2;co(s,new V(-r-1.4,-o-.4,-a-.6),new V(r+1.4,o+.4,a+.6),new V(0,0,0),Ub)}clear(){[...this.sceneGroup.children].forEach(e=>{this.sceneGroup.remove(e),Es(e)})}}function of(i,e){const t=new Qt;return t.setAttribute("position",new Ut(i,3)),t.setAttribute("color",new Ut(e,3)),t}const lf={PASSED:k.passed,INSUFFICIENT:k.insufficient,REJECTED:k.rejected};class Ob{constructor(){M(this,"id","ledger");M(this,"name","The ledger");M(this,"group","process");M(this,"caption","Every arm the run measured, its evidence, and the gate's standing on it.");M(this,"key","l");M(this,"visible",!1);M(this,"drawn",!1)}enter(){this.visible=!0,Ue.show(),this.draw()}exit(){this.visible=!1,Ue.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}chip(e,t,n,s){const r=lf[s]??k.text_secondary;e.font="11px 'JetBrains Mono', monospace";const a=e.measureText(s).width+18;e.fillStyle=`${r}22`,e.strokeStyle=`${r}88`,e.lineWidth=1,e.beginPath(),e.roundRect(t,n-9,a,18,9),e.fill(),e.stroke(),e.fillStyle=r,e.textAlign="center",e.textBaseline="middle",e.fillText(s,t+a/2,n)}standingBar(e,t,n,s,r,a){const o=Object.values(r).reduce((h,u)=>h+u,0);if(o===0)return;const l=18;let c=t;Object.entries(r).forEach(([h,u])=>{if(u<=0)return;const d=u/o*s;e.fillStyle=lf[h]??k.text_secondary,e.fillRect(c,n,Math.max(2,d-2),l),d>52&&(e.fillStyle=k.bg,e.font="11px 'JetBrains Mono', monospace",e.textAlign="center",e.textBaseline="middle",e.fillText(`${u}`,c+(d-2)/2,n+l/2)),c+=d}),e.font="12px 'JetBrains Mono', monospace",e.textAlign="left",e.textBaseline="alphabetic",e.fillStyle=k.text_secondary,e.fillText(`${a} arm${a===1?"":"s"}, and where each one stands`,t,n-10)}draw(){var r;const e=(r=xe.account)==null?void 0:r.ledger;if(!e||e.claims.length===0){this.drawn=!1;return}const t=Ue.begin(),n=Ue.area();ga(t,n,"The ledger","every arm the run measured, its evidence, and the gate's standing on it");let s=n.y+96;this.standingBar(t,n.x,s,Math.min(560,n.width*.55),e.standings,e.claims.length),s+=66,e.claims.forEach(a=>{const o=qt[a.value]??k.gradient;t.font="14px 'JetBrains Mono', monospace",t.textAlign="left",t.textBaseline="middle",t.fillStyle=o,t.fillText(`${a.axis} = ${a.value}`,n.x,s),t.font="13px 'JetBrains Mono', monospace",t.fillStyle=k.text_primary,t.fillText(`${a.mean.toFixed(3)} ± ${a.sd.toFixed(3)}`,n.x+300,s),t.font="12px 'JetBrains Mono', monospace",t.fillStyle=k.text_secondary,t.fillText(`${a.n} seeds · ${a.cells} cell${a.cells===1?"":"s"}`,n.x+460,s),this.chip(t,n.x+640,s,a.verdict),s+=42}),e.fixed.length>0&&(s+=22,t.font="600 14px 'JetBrains Mono', monospace",t.textAlign="left",t.textBaseline="alphabetic",t.fillStyle=k.text_primary,t.fillText("What was held fixed",n.x,s),s+=24,t.font="12px 'JetBrains Mono', monospace",e.fixed.forEach(a=>{t.textAlign="left",t.textBaseline="middle",t.fillStyle=k.text_secondary,t.fillText(`${a.axis} = ${a.value}`,n.x,s),t.fillText(`${a.mean.toFixed(3)}`,n.x+300,s),t.fillText(`${a.n} measurements · ${a.cells} cells`,n.x+460,s),s+=26})),s+=22,t.font="600 14px 'JetBrains Mono', monospace",t.textAlign="left",t.textBaseline="alphabetic",t.fillStyle=k.text_primary,t.fillText("What holds it back",n.x,s),s+=24,t.font="13px 'JetBrains Mono', monospace",e.limitations.forEach(a=>{Rh(t,`· ${a.detail}`,n.width).forEach(o=>{t.fillStyle=k.text_secondary,t.fillText(o,n.x,s),s+=20})}),e.significance&&(s+=14,Rh(t,`the report's test — ${e.significance}`,n.width).forEach(a=>{t.fillStyle=k.text_secondary,t.fillText(a,n.x,s),s+=20})),_n(t,n,`a claim needs ${e.min_seeds} seeds per cell`+(e.chance!==null?` · the chance level is ${e.chance.toFixed(3)}`:"")),this.drawn=!0}}class Fb{constructor(){M(this,"id","matrix");M(this,"name","Evidence matrix");M(this,"group","analysis");M(this,"caption","The space seen from above: one axis against another, every column a number, the refusals in the void colour.");M(this,"visible",!1);M(this,"drawn",!1)}enter(){this.visible=!0,Ue.show(),this.draw()}exit(){this.visible=!1,Ue.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}columns(){const e=xe.space;if(!e)return{columns:[],xValues:[],yValues:[]};const t=xe.axes,n=e.values[t.x]??[],s=e.values[t.y]??[],r=e.values[t.z]??[],a=[];return n.forEach(o=>{s.forEach(l=>{let c=0,h=0,u=-1/0,d="";r.forEach(g=>{const v=wi(o,l,g),p=xe.spaceCells.get(v);if((p==null?void 0:p.status)==="void"){c+=1;return}h+=1;const m=xe.aggregates.get(v);if(!m||m.acc.length===0)return;const S=ts(m.acc);S>u&&(u=S,d=m.coordinate.credit??"")});const f=c>0&&h===0?"void":u>-1/0?"measured":"gap";a.push({status:f,accuracy:u>-1/0?u:0,arm:d})})}),{columns:a,xValues:n,yValues:s}}draw(){const{columns:e,xValues:t,yValues:n}=this.columns();if(e.length===0){this.drawn=!1;return}const s=Ue.begin(),r=Ue.area(),a=xe.axes,o=t.length,l=n.length,c=150,u={x:r.x+c,y:r.y+70,width:Math.max(80,r.width-c-40),height:Math.max(80,r.height-70-96)},d=u.width/o,f=u.height/l,g=Math.max(...e.map(A=>A.accuracy),1e-4);s.fillStyle=k.text_primary,s.font="600 22px 'JetBrains Mono', monospace",s.textAlign="left",s.textBaseline="alphabetic",s.fillText("Evidence matrix",r.x,r.y+14),s.fillStyle=k.text_secondary,s.font="13px 'JetBrains Mono', monospace",s.fillText(`${a.x} against ${a.y} — the best cell of each column`,r.x,r.y+40);let v=0,p=0,m=0;e.forEach((A,R)=>{const N=Math.floor(R/l),w=R%l,y=u.x+N*d,P=u.y+w*f;A.status==="void"?(m+=1,s.fillStyle=`${k.void}22`,s.fillRect(y,P,d,f),this.drawCross(s,y,P,d,f)):A.status==="gap"?(p+=1,s.fillStyle=k.bg_tertiary,s.fillRect(y,P,d,f)):(v+=1,s.fillStyle=bi(A.accuracy/g),s.fillRect(y,P,d,f),d>44&&f>26&&(s.fillStyle=kb(A.accuracy/g),s.font="600 15px 'JetBrains Mono', monospace",s.textAlign="center",s.textBaseline="middle",s.fillText(A.accuracy.toFixed(2),y+d/2,P+f/2))),s.strokeStyle=k.bg,s.lineWidth=1,s.strokeRect(y+.5,P+.5,d-1,f-1)}),s.fillStyle=k.text_secondary,s.font="12px 'JetBrains Mono', monospace",t.forEach((A,R)=>{const N=ra(A,14);s.textAlign="center",s.textBaseline="top",N.forEach((w,y)=>{s.fillText(w,u.x+R*d+d/2,u.y+u.height+12+y*16)})}),n.forEach((A,R)=>{const N=ra(A,16);s.textAlign="right",s.textBaseline="middle",N.forEach((w,y)=>{s.fillText(w,u.x-12,u.y+R*f+f/2-(N.length-1)*8+y*16)})});const S=180,_=u.x+u.width-S,b=r.y+16,I=s.createLinearGradient(_,0,_+S,0);I.addColorStop(0,bi(0)),I.addColorStop(.5,bi(.5)),I.addColorStop(1,bi(1)),s.fillStyle=I,s.fillRect(_,b,S,12),s.strokeStyle=k.border,s.strokeRect(_+.5,b+.5,S-1,11),s.fillStyle=k.text_secondary,s.font="11px 'JetBrains Mono', monospace",s.textAlign="left",s.textBaseline="top",s.fillText("0",_,b+18),s.textAlign="right",s.fillText(g.toFixed(2),_+S,b+18),s.textAlign="left",s.fillText(`${v} measured · ${p} gaps · ${m} refused`,r.x,r.y+r.height+30),this.drawn=v>0}drawCross(e,t,n,s,r){const a=Math.min(s,r)*.28,o=t+s/2,l=n+r/2;e.strokeStyle=k.void,e.lineWidth=2,e.beginPath(),e.moveTo(o-a,l-a),e.lineTo(o+a,l+a),e.moveTo(o+a,l-a),e.lineTo(o-a,l+a),e.stroke()}}function kb(i){return i>.62?k.bg:k.text_primary}const Zo=["#58a6ff","#d4a843","#3fb950","#f78166"],Hn=1.15,Ba=1,Bb=1.5,zb=new V(.34,.4,.85);class Hb{constructor(){M(this,"id","multirun");M(this,"name","The multi-run space");M(this,"group","multi");M(this,"key","u");M(this,"caption","Several runs' evidence in one space: each run's cells stand in the run's own colour.");M(this,"sceneGroup",new oi);M(this,"visible",!1);M(this,"drawn",!1);M(this,"framed",!1);M(this,"legend",null)}enter(){this.visible=!0;const e=Fi();e&&e.scene.add(this.sceneGroup),this.load()}exit(){var t,n;this.visible=!1,(t=this.sceneGroup.parent)==null||t.remove(this.sceneGroup),Es(this.sceneGroup),this.sceneGroup=new oi,this.drawn=!1,this.framed=!1,(n=this.legend)==null||n.remove(),this.legend=null;const e=document.getElementById("legend-arms-block");e&&(e.style.display="")}refresh(e){if(this.visible){if(e==="axes"){this.load();return}this.draw(!1)}}ready(){return this.drawn}async load(){await xe.syncMultirun(!0),this.visible&&this.draw(!0)}cells(e){const[t,n,s]=e.axes,r=e.values[t]??[],a=e.values[n]??[],o=e.values[s]??[],l=[],c=new Set;let h=1e-4;e.runs.forEach((p,m)=>{Object.entries(p.measured).forEach(([S,_])=>{const[b,I,A]=S.split("|"),R=r.indexOf(b),N=a.indexOf(I),w=o.indexOf(A);R<0||N<0||w<0||(l.push({xi:R,yi:N,zi:w,runIndex:m,accuracy:_.accuracy}),c.add(b),_.accuracy>h&&(h=_.accuracy))})});const u=new Map;l.forEach(p=>{const m=`${p.xi}|${p.yi}|${p.zi}`;u.set(m,(u.get(m)??0)+1)});const d=new Map,f=l.map(p=>{const m=`${p.xi}|${p.yi}|${p.zi}`,S=d.get(m)??0;d.set(m,S+1);const _=u.get(m)??1,b=(S-(_-1)/2)*(Ba*.5);return{x:(p.xi-(r.length-1)/2)*Hn+b,y:p.yi*Hn,z:(p.zi-(o.length-1)/2)*Hn,color:Zo[p.runIndex%Zo.length],height:p.accuracy/h*Bb}}),g=new Set;e.runs.forEach(p=>{const m=[t,n,s].map(_=>p.values[_]??[]),S=new Set(p.refused);r.forEach(_=>{m[0].includes(_)&&m[1].forEach(b=>{m[2].forEach(I=>{S.has(wi(_,b,I))||g.add(wi(_,b,I))})})})});const v=[];return r.forEach((p,m)=>{a.forEach((S,_)=>{o.forEach((b,I)=>{g.has(wi(p,S,b))&&v.push({x:(m-(r.length-1)/2)*Hn,y:_*Hn,z:(I-(o.length-1)/2)*Hn})})})}),{tiles:v,blocks:f,xValues:r,yValues:a,zValues:o,labelled:c}}draw(e){var c;const t=xe.multirun;if(!t||t.runs.length===0){this.drawn=!1,(c=this.legend)==null||c.remove(),this.legend=null;return}this.clear();const{tiles:n,blocks:s,xValues:r,yValues:a,zValues:o,labelled:l}=this.cells(t);this.addGround(n),this.addBlocks(s),this.addLabels(r,a.length,o.length,l),this.drawn=s.length>0,this.buildLegend(t),(e||!this.framed)&&(this.frame(r.length,a.length,o.length),this.framed=!0)}clear(){[...this.sceneGroup.children].forEach(e=>{this.sceneGroup.remove(e),Es(e)})}addGround(e){if(e.length===0)return;const t=Ba/2,n=[],s=[];e.forEach((a,o)=>{n.push(a.x-t,a.y,a.z-t,a.x+t,a.y,a.z-t,a.x+t,a.y,a.z+t,a.x-t,a.y,a.z+t);const l=o*4;s.push(l,l+2,l+1,l,l+3,l+2)});const r=new Qt;r.setAttribute("position",new Ut(n,3)),r.setIndex(s),r.computeVertexNormals(),this.sceneGroup.add(new jt(r,new es({color:new it(k.border),side:Fn})))}addBlocks(e){const t=new Map;e.forEach(n=>{const s=`${n.x}|${n.y}|${n.z}`,r=t.get(s)??0;t.set(s,r+1);const a=(r-(t.size-1)/2)*(Ba*.5),o=Math.max(n.height,.12),l=new Si(Ba*.45,o,Ba*.45);l.translate(0,o/2,0);const c=new Jr({color:new it(n.color),emissive:new it(n.color),emissiveIntensity:.45,transparent:!0,opacity:.95,metalness:.2,roughness:.4}),h=new jt(l,c);h.position.set(n.x+a,n.y,n.z),this.sceneGroup.add(h)})}addLabels(e,t,n,s){const r=new Ei({color:13227232,sizeAttenuation:!0}),a=new Ei({color:9148584,sizeAttenuation:!0}),o=(e.length-1)*Hn/2,l=(n-1)*Hn/2;e.forEach((p,m)=>{if(!s.has(p))return;const S=vn(p,.26,a,Hn*.9);S.position.set((m-(e.length-1)/2)*Hn,-.45,l+1.1),this.sceneGroup.add(S)});const c=xe.multirun,[h,u,d]=(c==null?void 0:c.axes)??["","",""],f=vn(h,.24,r);f.position.set(o+1,-.4,l+1.1),this.sceneGroup.add(f);const g=vn(d,.24,r);g.position.set(0,-.4,l+2),this.sceneGroup.add(g);const v=vn(u,.24,r);v.position.set(-o-1.3,(t-1)*Hn*.5,0),this.sceneGroup.add(v)}buildLegend(e){var o;const t=document.getElementById("discovery-legend");if(!t)return;(o=this.legend)==null||o.remove();const n=document.getElementById("legend-arms-block");n&&(n.style.display="none");const s=document.createElement("div");s.id="legend-runs",s.style.cssText="margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--border);";const r=document.createElement("div");r.textContent="Runs",r.style.cssText="font-weight: 600; margin-bottom: 8px;",s.appendChild(r),e.runs.forEach((l,c)=>{const h=Zo[c%Zo.length],u=Object.keys(l.measured).length,d=document.createElement("div");d.style.cssText="display: flex; align-items: center; gap: 8px; margin-bottom: 6px; font-size: 11px;";const f=document.createElement("span");f.style.cssText=`width: 14px; height: 14px; background: ${h}; border-radius: 3px;`;const g=document.createElement("span");g.style.color="var(--text-secondary)",g.textContent=`${l.profile??l.run_id.slice(0,8)} · ${u} cells · ${l.records} records`,d.appendChild(f),d.appendChild(g),s.appendChild(d)});const a=document.createElement("div");a.textContent=e.summary,a.style.cssText="font-size: 11px; color: var(--text-muted); margin-top: 6px;",s.appendChild(a),t.appendChild(s),this.legend=s}frame(e,t,n){const s=Fi();if(!s||e===0)return;const r=(e-1)*Hn/2+.6,a=(n-1)*Hn/2+.6,o=(t-1)*Hn+.8;co(s,new V(-r,-.8,-a),new V(r,o,a+1.8),new V(0,o/3,0),zb)}}const Vb=[{across:"x",down:"y",held:"z"},{across:"x",down:"z",held:"y"},{across:"y",down:"z",held:"x"}];class Gb{constructor(){M(this,"id","slices");M(this,"name","The slices");M(this,"group","analysis");M(this,"key",",");M(this,"caption","The same space, cut three ways: three pairs of axes, side by side, so the space is not one picture.");M(this,"visible",!1);M(this,"drawn",!1)}enter(){this.visible=!0,Ue.show(),this.draw()}exit(){this.visible=!1,Ue.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}cut(e){const t=xe.space;if(!t)return{cells:[],across:[],down:[]};const n=xe.axes,s=t.values[n[e.across]]??[],r=t.values[n[e.down]]??[],a=t.values[n[e.held]]??[],o=[];return s.forEach(l=>{r.forEach(c=>{let h=0,u=0,d=-1/0;a.forEach(f=>{const g=this.keyOf(n,e,l,c,f),v=xe.spaceCells.get(g);if((v==null?void 0:v.status)==="void"){h+=1;return}u+=1;const p=xe.aggregates.get(g);!p||p.acc.length===0||(d=Math.max(d,ts(p.acc)))}),o.push({status:h>0&&u===0?"void":d>-1/0?"measured":"gap",accuracy:d>-1/0?d:0})})}),{cells:o,across:s,down:r}}keyOf(e,t,n,s,r){const a={x:"",y:"",z:""};return a[t.across]=n,a[t.down]=s,a[t.held]=r,wi(a.x,a.y,a.z)}draw(){if(!xe.space){this.drawn=!1;return}const t=Ue.begin(),n=Ue.area(),s=xe.axes;t.fillStyle=k.text_primary,t.font="600 22px 'JetBrains Mono', monospace",t.textAlign="left",t.textBaseline="alphabetic",t.fillText("The slices",n.x,n.y+14),t.fillStyle=k.text_secondary,t.font="13px 'JetBrains Mono', monospace",t.fillText("One space, three cuts: the axes a reader sees are a choice, and every choice hides an axis.",n.x,n.y+40);const r=28,a=(n.width-r*2)/3;let o=0,l=0,c=0;Vb.forEach((h,u)=>{const{cells:d,across:f,down:g}=this.cut(h),v=n.x+u*(a+r),p=n.y+70,m=96,_={x:v+m,y:p,width:Math.max(60,a-m-12),height:Math.max(60,n.height-70-54)},b=f.length?_.width/f.length:0,I=g.length?_.height/g.length:0,A=Math.max(...d.map(R=>R.accuracy),1e-4);t.fillStyle=k.text_primary,t.font="600 13px 'JetBrains Mono', monospace",t.textAlign="left",t.textBaseline="alphabetic",t.fillText(`${s[h.across]} × ${s[h.down]}`,v,p-12),t.fillStyle=k.text_muted,t.font="11px 'JetBrains Mono', monospace",t.fillText(`${s[h.held]} collapsed`,v,p-30),d.forEach((R,N)=>{const w=Math.floor(N/g.length),y=N%g.length,P=_.x+w*b,X=_.y+y*I;R.status==="void"?(c+=1,t.fillStyle=`${k.void}22`,t.fillRect(P,X,b,I)):R.status==="gap"?(l+=1,t.fillStyle=k.bg_tertiary,t.fillRect(P,X,b,I)):(o+=1,t.fillStyle=bi(R.accuracy/A),t.fillRect(P,X,b,I)),t.strokeStyle=k.bg,t.lineWidth=1,t.strokeRect(P+.5,X+.5,b-1,I-1)}),t.fillStyle=k.text_secondary,t.font="11px 'JetBrains Mono', monospace",f.forEach((R,N)=>{const w=ra(R,12);t.textAlign="center",t.textBaseline="top",w.forEach((y,P)=>{t.fillText(y,_.x+N*b+b/2,_.y+_.height+8+P*14)})}),g.forEach((R,N)=>{const w=ra(R,14);t.textAlign="right",t.textBaseline="middle",w.forEach((y,P)=>{t.fillText(y,_.x-8,_.y+N*I+I/2-(w.length-1)*7+P*14)})})}),t.fillStyle=k.text_secondary,t.font="12px 'JetBrains Mono', monospace",t.textAlign="left",t.textBaseline="alphabetic",t.fillText(`${o} measured · ${l} gaps · ${c} refused`,n.x,n.y+n.height+24),this.drawn=o>0}}class Wb{constructor(){M(this,"id","multiples");M(this,"name","Small multiples");M(this,"group","analysis");M(this,"caption","One panel per cell: every seed's own curve, on the same accuracy scale.");M(this,"visible",!1);M(this,"drawn",!1)}enter(){this.visible=!0,Ue.show(),this.draw()}exit(){this.visible=!1,Ue.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}panels(){const e=xe.axes,t=su(xe.aggregates,e),n=El(t,e);return t.filter(s=>s.curves.length>0).map(s=>({cell:s,label:to(s,e,n),color:qt[s.coordinate.credit]??k.gradient,curves:s.curves}))}draw(){const e=this.panels();if(e.length===0){this.drawn=!1;return}const t=Ue.begin(),n=Ue.area(),s=xe.chance,r=e.flatMap(_=>_.curves.flatMap(b=>b.map(I=>I.val_acc))),a=e.flatMap(_=>_.curves.flatMap(b=>b.map(I=>I.epoch)));let o=Math.min(s,...r),l=Math.max(s,...r);l-o<1e-6&&(o-=.05,l+=.05);const c=(l-o)*.14;o-=c,l+=c;const h=Math.max(1,...a),u=Math.ceil(Math.sqrt(e.length)),d=Math.ceil(e.length/u),f=18,g=n.width-f*(u-1),v=n.height-64-44-f*(d-1),p=g/u,m=v/d;ga(t,n,"Small multiples","every seed of every cell, on one accuracy scale"),e.forEach((_,b)=>{const I=b%u,A=Math.floor(b/u),R=n.x+I*(p+f),N=n.y+64+A*(m+f);t.fillStyle=_.color,t.font="600 13px 'JetBrains Mono', monospace",t.textAlign="left",t.textBaseline="alphabetic",t.fillText(_.label,R,N+12);const w={x:R+(I===0?44:10),y:N+30,width:p-(I===0?54:20),height:m-56};t.strokeStyle=k.border,t.lineWidth=1,t.strokeRect(w.x+.5,w.y+.5,w.width-1,w.height-1);const y=w.y+w.height*(1-(s-o)/(l-o));t.strokeStyle=k.chance_line,t.lineWidth=1,t.setLineDash([4,4]),t.beginPath(),t.moveTo(w.x,y),t.lineTo(w.x+w.width,y),t.stroke(),t.setLineDash([]),_.curves.forEach(P=>{t.strokeStyle=_.color,t.lineWidth=1.8,t.beginPath(),P.forEach((X,H)=>{const J=w.x+X.epoch/h*w.width,q=w.y+w.height*(1-(X.val_acc-o)/(l-o));H===0?t.moveTo(J,q):t.lineTo(J,q)}),t.stroke()}),t.fillStyle=k.text_muted,t.font="9px 'JetBrains Mono', monospace",I===0&&(t.textAlign="right",t.textBaseline="middle",[l,(l+o)/2,o].forEach(P=>{const X=w.y+w.height*(1-(P-o)/(l-o));t.fillText(P.toFixed(2),w.x-6,X)})),A===d-1&&(t.textAlign="left",t.textBaseline="top",t.fillText("epoch 0",w.x,w.y+w.height+6),t.textAlign="right",t.fillText(`epoch ${h}`,w.x+w.width,w.y+w.height+6))});const S=e.reduce((_,b)=>_+b.curves.length,0);_n(t,n,`${e.length} cells · ${S} seeds · the dashed line is the chance level (${s.toFixed(2)})`),this.drawn=!0}}function $b(i,e,t){let n=0;return i.forEach(s=>{const r=(e-s)/t;n+=Math.exp(-.5*r*r)}),n/(i.length*t*Math.sqrt(2*Math.PI))}function cf(i){if(i.length<2)return .02;const e=i.reduce((r,a)=>r+a,0)/i.length,t=i.reduce((r,a)=>r+(a-e)**2,0)/(i.length-1),s=1.06*Math.sqrt(t)*i.length**-.2;return Math.max(s,.01)}class qb{constructor(){M(this,"id","spread");M(this,"name","The spread");M(this,"group","analysis");M(this,"caption","One violin per arm, across its seeds: the width is the spread, not the mean.");M(this,"visible",!1);M(this,"drawn",!1)}enter(){this.visible=!0,Ue.show(),this.draw()}exit(){this.visible=!1,Ue.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}arms(){var n;const e=((n=xe.metrics)==null?void 0:n.records)??[],t=new Map;return e.forEach(s=>{var l,c;const r=(l=s==null?void 0:s.payload)==null?void 0:l.val_acc,a=(c=s==null?void 0:s.coordinate)==null?void 0:c.credit;if(typeof r!="number"||!a)return;const o=t.get(a)??[];o.push(r),t.set(a,o)}),Array.from(t.entries()).map(([s,r])=>({name:s,values:r.slice().sort((a,o)=>a-o),color:qt[s]??k.gradient})).sort((s,r)=>s.name.localeCompare(r.name))}draw(){const e=this.arms();if(e.length===0){this.drawn=!1;return}const t=Ue.begin(),n=Ue.area(),s=xe.chance,r=xe.requiredSeeds,a=e.map(h=>{const u=cf(h.values);return{high:h.values[h.values.length-1]+1.5*u,low:h.values[0]-1.5*u}}),o=Math.max(s,...a.map(h=>h.high))*1.03,l=zp(t,n,{yMin:0,yMax:o,categories:e.map(h=>h.name),title:"The spread",subtitle:"every seed of every arm, as a distribution",yLabel:"accuracy"}),c=l.rect.y+l.rect.height*(1-s/l.yMax);t.strokeStyle=k.chance_line,t.lineWidth=1.5,t.setLineDash([6,5]),t.beginPath(),t.moveTo(l.rect.x,c),t.lineTo(l.rect.x+l.rect.width,c),t.stroke(),t.setLineDash([]),t.save(),t.beginPath(),t.rect(l.rect.x,l.rect.y,l.rect.width,l.rect.height),t.clip(),e.forEach((h,u)=>{const d=l.band(u),f=Math.min(l.bandWidth*.36,90),g=cf(h.values),v=h.values[0]-1.5*g,p=h.values[h.values.length-1]+1.5*g,m=48,S=[];let _=0;for(let R=0;R<=m;R+=1){const N=v+(p-v)*R/m,w=$b(h.values,N,g);S.push(w),_=Math.max(_,w)}const b=_>0?1/_:0,I=R=>l.rect.y+l.rect.height*(1-R/l.yMax);t.beginPath(),S.forEach((R,N)=>{const w=v+(p-v)*N/m,y=d+R*b*f,P=I(w);N===0?t.moveTo(y,P):t.lineTo(y,P)});for(let R=S.length-1;R>=0;R-=1){const N=v+(p-v)*R/m,w=d-S[R]*b*f;t.lineTo(w,I(N))}t.closePath(),t.fillStyle=`${h.color}33`,t.fill(),t.strokeStyle=h.color,t.lineWidth=1.5,t.stroke(),h.values.forEach((R,N)=>{const w=(N-(h.values.length-1)/2)*7;t.fillStyle=h.color,t.beginPath(),t.arc(d+w,I(R),3,0,Math.PI*2),t.fill()});const A=h.values.reduce((R,N)=>R+N,0)/h.values.length;t.strokeStyle=k.text_primary,t.lineWidth=1.5,t.beginPath(),t.moveTo(d-f,I(A)),t.lineTo(d+f,I(A)),t.stroke()}),t.restore(),e.forEach((h,u)=>{const d=Math.max(0,r-h.values.length);t.font="11px 'JetBrains Mono', monospace",t.textAlign="center",t.textBaseline="top",t.fillStyle=k.text_secondary,t.fillText(`${h.values.length} of ${r} seeds`,l.band(u),l.rect.y+l.rect.height+46),d>0&&(t.fillStyle=k.warn,t.fillText(`${d} short`,l.band(u),l.rect.y+l.rect.height+62))}),_n(t,n,`the white line is each arm's mean · a claim needs ${r} seeds per group`),this.drawn=!0}}const Ic=3.4,Hr=1.15,Xb=new V(.34,.4,.85);class Yb{constructor(){M(this,"id","terrain");M(this,"name","Terrain");M(this,"group","space");M(this,"caption","The space as a heightfield: accuracy is the height, the gaps are flat, the refusals are craters.");M(this,"sceneGroup",new oi);M(this,"visible",!1);M(this,"drawn",!1);M(this,"framed",!1)}enter(){this.visible=!0;const e=Fi();e&&e.scene.add(this.sceneGroup),this.draw(!0)}exit(){var e;this.visible=!1,(e=this.sceneGroup.parent)==null||e.remove(this.sceneGroup),Es(this.sceneGroup),this.sceneGroup=new oi,this.drawn=!1,this.framed=!1}refresh(){this.visible&&this.draw(!1)}ready(){return this.drawn}columns(){const e=xe.space;if(!e)return{columns:[],xValues:[],yValues:[]};const t=xe.axes,n=e.values[t.x]??[],s=e.values[t.y]??[],r=e.values[t.z]??[],a=[];return n.forEach((o,l)=>{s.forEach((c,h)=>{let u=0,d=0,f=-1/0,g="";r.forEach(p=>{const m=wi(o,c,p),S=xe.spaceCells.get(m);if((S==null?void 0:S.status)==="void"){u+=1;return}d+=1;const _=xe.aggregates.get(m);if(!_||_.acc.length===0)return;const b=ts(_.acc);b>f&&(f=b,g=_.coordinate.credit??"")});const v=u>0&&d===0?"void":f>-1/0?"measured":"gap";a.push({status:v,accuracy:f>-1/0?f:0,arm:g,x:(l-(n.length-1)/2)*Hr,y:(h-(s.length-1)/2)*Hr})})}),{columns:a,xValues:n,yValues:s}}draw(e){const{columns:t,xValues:n,yValues:s}=this.columns();if(t.length===0){this.drawn=!1;return}this.clear();const r=Math.max(...t.map(f=>f.accuracy),1e-4),a=[],o=[],l=[];t.forEach(f=>{const g=f.status==="measured"?f.accuracy/r*Ic:f.status==="void"?-1.1:0;a.push(f.x,g,f.y);const v=new it(f.status==="measured"?qt[f.arm]||k.gradient:f.status==="void"?k.void:k.border_bright);if(f.status==="measured"){const p=.6+.4*(f.accuracy/r);v.multiplyScalar(p)}else f.status==="void"&&v.multiplyScalar(.55);o.push(v.r,v.g,v.b)});const c=n.length,h=s.length;for(let f=0;f<c-1;f+=1)for(let g=0;g<h-1;g+=1){const v=f*h+g,p=(f+1)*h+g,m=(f+1)*h+g+1,S=f*h+g+1;l.push(v,S,p,p,S,m)}const u=new Qt;u.setAttribute("position",new Ut(a,3)),u.setAttribute("color",new Ut(o,3)),u.setIndex(l),u.computeVertexNormals();const d=new jt(u,new Jr({vertexColors:!0,roughness:.7,metalness:.1,side:Fn}));this.sceneGroup.add(d),this.addVoidMarkers(t),this.addLabels(n,s),this.drawn=t.some(f=>f.status==="measured"),(e||!this.framed)&&(this.frame(t,n,s),this.framed=!0)}clear(){[...this.sceneGroup.children].forEach(e=>{this.sceneGroup.remove(e),Es(e)})}addVoidMarkers(e){const t=[];if(e.forEach(r=>{r.status==="void"&&t.push(r.x-.22,-1.1+.02,r.y-.22,r.x+.22,-1.1+.02,r.y+.22,r.x+.22,-1.1+.02,r.y-.22,r.x-.22,-1.1+.02,r.y+.22)}),t.length===0)return;const s=new Qt;s.setAttribute("position",new Ut(t,3)),this.sceneGroup.add(new Kr(s,new bs({color:k.void,transparent:!0,opacity:.75})))}addLabels(e,t){const n=new Ei({color:13227232,sizeAttenuation:!0}),s=(e.length-1)*Hr/2,r=(t.length-1)*Hr/2,a=vn(xe.axes.x,.22,n);a.position.set(s+1,-.2,r+.9),this.sceneGroup.add(a);const o=vn(xe.axes.y,.22,n);o.position.set(-s-1,.2,-r),this.sceneGroup.add(o)}frame(e,t,n){const s=Fi();if(!s||e.length===0)return;const r=(t.length-1)*Hr/2,a=(n.length-1)*Hr/2;co(s,new V(-r-1.2,-1.1-.3,-a),new V(r+1.2,Ic,a+1.4),new V(0,Ic/3,0),Xb)}}class jb{constructor(){M(this,"id","timeline");M(this,"name","The timeline");M(this,"group","process");M(this,"caption","The run's stages, in the order it reached them, and the time each held it.");M(this,"key","t");M(this,"visible",!1);M(this,"drawn",!1)}enter(){this.visible=!0,Ue.show(),this.draw()}exit(){this.visible=!1,Ue.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}draw(){const e=xe.timeline,t=(e==null?void 0:e.stages)??[];if(!e||t.length===0){this.drawn=!1;return}const n=Ue.begin(),s=Ue.area(),r=Math.max(e.seconds,.001),a=Tl(n,s,{xMin:0,xMax:r,rows:t.map(d=>d.action),title:"The timeline",subtitle:"the run's stages, and the time each of them held it",xLabel:"seconds"}),o=d=>a.rect.x+d/r*a.rect.width,l=new Map;e.events.forEach(d=>{const f=l.get(d.stage)??[];f.push(d.at-e.start),l.set(d.stage,f)});const c=t.slice(0,-1).map((d,f)=>{const g=t[f+1],v=(l.get(d.stage)??[]).filter(m=>m<=g.offset),p=v.length>0?v[v.length-1]:d.offset;return{index:f,from:p,to:g.offset,seconds:g.offset-p}}),h=c.reduce((d,f)=>f.seconds>d.seconds?f:d,{index:-1,from:0,to:0,seconds:0}),u=h.seconds>.5?h:null;if(u){const d=o(u.from),f=o(u.to);n.fillStyle=`${k.warn}18`,n.fillRect(d,a.rect.y,Math.max(2,f-d),a.rect.height)}c.forEach(d=>{const f=d.index===h.index;n.strokeStyle=f?k.warn:k.border,n.lineWidth=f?2:1,n.beginPath(),n.moveTo(o(d.from),a.rowY(d.index)),n.lineTo(o(d.to),a.rowY(d.index+1)),n.stroke()}),t.forEach((d,f)=>{const g=a.rowY(f);n.fillStyle=k.gradient,(l.get(d.stage)??[]).forEach(v=>{const p=o(v);n.fillRect(p-1.5,g-9,3,18)}),n.font="12px 'JetBrains Mono', monospace",n.textAlign="left",n.textBaseline="middle",n.fillStyle=k.text_secondary,n.fillText(`${d.events}`,a.rect.x+a.rect.width+12,g)}),u&&(n.font="13px 'JetBrains Mono', monospace",n.textAlign="center",n.textBaseline="alphabetic",n.fillStyle=k.warn,n.fillText(`${u.seconds.toFixed(1)} s of silence`,(o(u.from)+o(u.to))/2,a.rect.y+22)),_n(n,s,`${t.length} stages · ${e.events.length} events · ${r.toFixed(1)} s from the first word to the last`),this.drawn=!0}}class Kb{constructor(){M(this,"id","uncertainty");M(this,"name","The uncertainty");M(this,"group","analysis");M(this,"caption","Each cell's mean and the margin the gate asks for, against the chance level.");M(this,"visible",!1);M(this,"drawn",!1)}enter(){this.visible=!0,Ue.show(),this.draw()}exit(){this.visible=!1,Ue.hide(),this.drawn=!1}refresh(){this.visible&&this.draw()}ready(){return this.drawn}sigma(){const e=xe.gate;return e&&typeof e.superiority_margin_sigma=="number"?e.superiority_margin_sigma:2}intervals(){const e=xe.axes,t=xe.chance,n=this.sigma(),s=su(xe.aggregates,e),r=El(s,e);return s.filter(a=>a.acc.length>0).map(a=>{const o=a.acc.length,l=a.acc.reduce((d,f)=>d+f,0)/o,c=a.acc.reduce((d,f)=>d+(f-l)**2,0)/Math.max(1,o-1),h=o>1?Math.sqrt(c/o):0,u=n*h;return{cell:a,label:to(a,e,r),color:qt[a.coordinate.credit]??k.gradient,mean:l,margin:u,lower:l-u,upper:l+u,threshold:t+u}}).sort((a,o)=>o.mean-a.mean)}draw(){const e=this.intervals();if(e.length===0){this.drawn=!1;return}const t=Ue.begin(),n=Ue.area(),s=xe.chance,r=this.sigma(),a=Math.max(s,...e.map(h=>Math.max(h.upper,h.threshold))),o=Tl(t,n,{xMin:0,xMax:a*1.12,rows:e.map(h=>h.label),title:"The uncertainty",subtitle:"each cell's mean, and the margin the gate asks for",xLabel:"accuracy"}),l=h=>o.rect.x+h/(o.xMax||1)*o.rect.width,c=l(s);t.strokeStyle=k.chance_line,t.lineWidth=1.5,t.setLineDash([6,5]),t.beginPath(),t.moveTo(c,o.rect.y),t.lineTo(c,o.rect.y+o.rect.height),t.stroke(),t.setLineDash([]),t.font="11px 'JetBrains Mono', monospace",t.textAlign="left",t.textBaseline="alphabetic",t.fillStyle=k.chance_line,t.fillText("chance",c+6,o.rect.y+14),e.forEach((h,u)=>{const d=o.rowY(u),f=h.lower>s;t.strokeStyle=h.color,t.lineWidth=3,t.beginPath(),t.moveTo(l(h.lower),d),t.lineTo(l(h.upper),d),t.stroke(),t.strokeStyle=f?k.ok:k.warn,t.lineWidth=2,t.beginPath(),t.moveTo(l(h.threshold),d-11),t.lineTo(l(h.threshold),d+11),t.stroke(),t.fillStyle=h.color,t.beginPath(),t.arc(l(h.mean),d,5,0,Math.PI*2),t.fill(),t.textAlign="left",t.textBaseline="middle",t.font="12px 'JetBrains Mono', monospace",t.fillStyle=f?k.ok:k.warn,t.fillText(f?"clears chance":"not yet separable",o.rect.x+o.rect.width+12,d)}),_n(t,n,`the bar is ±${r}·SE · the tick is the threshold each cell has to clear · a claim needs ${xe.requiredSeeds} seeds per cell`),this.drawn=!0}}class Jb{constructor(){M(this,"id","space");M(this,"name","Space");M(this,"group","space");M(this,"caption","The declared space: the gaps as cages, the measured cells as pillars, the refusals as crosses.")}enter(){Ks.show()}exit(){Ks.hide()}refresh(e){Ks.refreshView(e)}ready(){return Ks.hasMeasured()}}class Zb{constructor(){M(this,"name","ViewSwitcher");M(this,"views",[]);M(this,"active",null);M(this,"track",null);M(this,"viewButtons",new Map);M(this,"captionElement",null);M(this,"section",null);M(this,"keys",new Map);M(this,"keyOf",new Map);M(this,"onKeyDown",e=>{if(e.metaKey||e.ctrlKey||e.altKey)return;const t=e.target;if(t&&["INPUT","SELECT","TEXTAREA"].includes(t.tagName))return;const n=e.key.toLowerCase();if(n===ZS){this.cycle();return}const s=this.keys.get(n);s&&this.show(s.id)});this.views=[new Jb,new Yb,new Ib,new Fb,new gb,new Wb,new qb,new pb,new Kb,new jb,new Ob,new mb,new Db,new Rb,new Nb,new yb,new Sb,new bb,new Mb,new Eb,new Tb,new Ab,new Cb,new Hb,new Gb]}async init(){window.addEventListener("keydown",this.onKeyDown),xe.onChange(e=>{var t;return(t=this.active)==null?void 0:t.refresh(e)}),this.buildKeys(),this.buildSection(),this.attachSection(),this.show(this.views[0].id),console.log("[ViewSwitcher] Initialized")}async destroy(){var e,t;window.removeEventListener("keydown",this.onKeyDown),(e=this.active)==null||e.exit(),this.active=null,(t=this.section)==null||t.remove(),this.section=null}get activeId(){var e;return((e=this.active)==null?void 0:e.id)??null}isReady(e){const t=this.views.find(n=>n.id===e);return t?t.ready():!1}show(e){var n;const t=this.views.find(s=>s.id===e);!t||t===this.active||((n=this.active)==null||n.exit(),this.active=t,t.enter(),this.updateSelector(),this.updateLegend())}cycle(){if(this.views.length===0)return;const e=this.views.findIndex(n=>n===this.active),t=this.views[(e+1)%this.views.length];this.show(t.id)}buildKeys(){this.keys.clear(),this.keyOf.clear(),this.views.forEach((e,t)=>{const n=t<9?String(t+1):"";n&&(this.keys.set(n,e),this.keyOf.set(e.id,n)),e.key&&!Ch.has(e.key)&&(this.keys.set(e.key,e),this.keyOf.set(e.id,e.key))})}optionLabel(e){const t=this.keyOf.get(e.id);return t?`${t.toUpperCase()} · ${e.name}`:e.name}keyHint(){const e=[],t=[],n=[];this.views.forEach((r,a)=>{if(a<9){e.push(String(a+1));return}if(!(!r.key||Ch.has(r.key))){if(/^[a-z]$/.test(r.key)){t.push(r.key.toUpperCase());return}n.push(r.key)}});const s=["V cycles"];return e.length>0&&s.push(`${e[0]}–${e[e.length-1]} pick`),t.length>0&&s.push(`${t.join(" ")} pick`),n.length>0&&s.push(`${n.join(" ")} pick`),s.join(" · ")}buildSection(){const e=document.createElement("div");e.id="legend-view-section",e.style.cssText="margin-bottom: 12px;";const t=document.createElement("div");t.textContent="View",t.style.cssText="font-weight: 600; margin-bottom: 8px;",e.appendChild(t);const n=document.createElement("div");n.id="view-strip",n.style.cssText=`
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
    `;const r=[{group:"space",label:"Space",views:[]},{group:"analysis",label:"Analysis",views:[]},{group:"process",label:"Process",views:[]},{group:"dynamics",label:"Dynamics",views:[]},{group:"trained",label:"Trained",views:[]},{group:"multi",label:"Multi",views:[]}];for(const l of this.views){const c=r.find(h=>h.group===l.group);c&&c.views.push(l)}r.forEach((l,c)=>{if(l.views.length===0)return;if(c>0){const u=document.createElement("div");u.style.cssText=`
          width: 1px;
          height: 16px;
          background: var(--border);
          margin: 0 4px;
        `,s.appendChild(u)}const h=document.createElement("span");h.textContent=l.label,h.style.cssText=`
        font-size: 9px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--text-muted);
        margin-right: 4px;
        flex-shrink: 0;
      `,s.appendChild(h);for(const u of l.views)s.appendChild(this.viewButton(u))}),n.appendChild(s),n.appendChild(this.stepButton("›","the next view",1)),e.appendChild(n),this.track=s;const a=document.createElement("div");a.id="view-caption",a.style.cssText="font-size: 11px; color: var(--text-secondary); margin-top: 8px;",e.appendChild(a),this.captionElement=a;const o=document.createElement("div");o.textContent=this.keyHint(),o.style.cssText="font-size: 10px; color: var(--text-muted); margin-top: 6px;",e.appendChild(o),this.section=e}viewButton(e){const t=db(e.id),n=this.keyOf.get(e.id),s=document.createElement("button");s.className="view-button",s.dataset.view=e.id,s.textContent=t.glyph,s.title=n?`${n.toUpperCase()} · ${e.name}`:e.name,s.style.cssText=`
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
    `,s.addEventListener("click",()=>this.step(n)),s}step(e){if(this.views.length===0)return;const t=this.views.findIndex(r=>{var a;return r.id===((a=this.active)==null?void 0:a.id)}),s=((t<0?0:t)+e+this.views.length)%this.views.length;this.show(this.views[s].id)}attachSection(e=0){const t=document.getElementById("legend-view");if(!t){e<50&&window.setTimeout(()=>this.attachSection(e+1),100);return}this.section&&this.section.parentElement!==t&&t.appendChild(this.section),this.updateSelector(),this.updateLegend()}updateSelector(){if(this.active){for(const[e,t]of this.viewButtons){const n=e===this.active.id;t.classList.toggle("active",n),n&&(t.style.color="var(--text-primary)",t.style.borderColor="var(--border-bright)",t.style.background="var(--bg-primary)")}this.scrollToActive()}}scrollToActive(){const e=this.active?this.viewButtons.get(this.active.id):null;!e||!this.track||e.scrollIntoView({block:"nearest",inline:"nearest"})}updateLegend(){if(!this.active)return;const e=document.getElementById("legend-title");e&&(e.textContent=this.active.name);const t=document.getElementById("legend-marks");t&&(t.style.display=this.active.id==="space"?"":"none"),this.captionElement&&(this.captionElement.textContent=this.active.caption)}}const no=new Zb;Zn.register(no);const Qb={watch:{id:"watch",viewId:"space",placements:[{id:"control-bar",dock:"bottom",order:0,isOpen:!0},{id:"live-rail",dock:"right",order:0,isOpen:!0},{id:"caption",dock:"bottom",order:1,isOpen:!0},{id:"legend",dock:"bottom",order:2,isOpen:!0},{id:"hud",dock:"top",order:0,isOpen:!1},{id:"plotter-pareto",dock:"right",order:1,isOpen:!0},{id:"plotter-ablation",dock:"right",order:2,isOpen:!1},{id:"plotter-variability",dock:"right",order:3,isOpen:!1},{id:"cell-drawer",dock:"floating",order:0,isOpen:!1},{id:"control-panel",dock:"floating",order:1,isOpen:!1},{id:"help-overlay",dock:"floating",order:2,isOpen:!1}]},audit:{id:"audit",viewId:"ledger",placements:[{id:"control-bar",dock:"bottom",order:0,isOpen:!0},{id:"live-rail",dock:"right",order:0,isOpen:!0},{id:"caption",dock:"bottom",order:1,isOpen:!0},{id:"legend",dock:"bottom",order:2,isOpen:!0},{id:"hud",dock:"top",order:0,isOpen:!1},{id:"plotter-pareto",dock:"right",order:1,isOpen:!0},{id:"plotter-ablation",dock:"right",order:2,isOpen:!0},{id:"plotter-variability",dock:"right",order:3,isOpen:!0},{id:"cell-drawer",dock:"floating",order:0,isOpen:!1},{id:"control-panel",dock:"floating",order:1,isOpen:!1},{id:"help-overlay",dock:"floating",order:2,isOpen:!1}]},drive:{id:"drive",viewId:"flow",placements:[{id:"control-bar",dock:"bottom",order:0,isOpen:!0},{id:"live-rail",dock:"right",order:0,isOpen:!0},{id:"caption",dock:"bottom",order:1,isOpen:!0},{id:"legend",dock:"bottom",order:2,isOpen:!0},{id:"hud",dock:"top",order:0,isOpen:!1},{id:"plotter-pareto",dock:"right",order:1,isOpen:!1},{id:"plotter-ablation",dock:"right",order:2,isOpen:!1},{id:"plotter-variability",dock:"right",order:3,isOpen:!1},{id:"cell-drawer",dock:"floating",order:0,isOpen:!1},{id:"control-panel",dock:"floating",order:1,isOpen:!0},{id:"help-overlay",dock:"floating",order:2,isOpen:!1}]},free:{id:"free",viewId:"space",placements:[]}},Uc="computronium.layout.v1";class eM{constructor(){M(this,"dockElements",new Map);M(this,"panelPlacements",new Map);M(this,"currentWorkspace","watch");M(this,"isManualOverride",!1);M(this,"listeners",new Set);M(this,"initialized",!1)}async init(){if(this.initialized)return;const e=document.getElementById("ui-overlay");if(!e)throw new Error("ui-overlay not found — layout must init after DOM ready");for(const t of["top","bottom","left","right","floating"]){const n=document.createElement("div");n.id=`dock-${t}`,n.className=`dock dock-${t}`,n.dataset.dock=t,n.style.cssText=this.dockStyles(t),e.appendChild(n),this.dockElements.set(t,n)}this.restoreOrDefault(),this.initialized=!0,console.log("[LayoutManager] Initialized")}dockStyles(e){const t=`
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
        `}}registerPanel(e,t){const n=$t.get(e);if(!n)return;const s=this.panelPlacements.get(e),r={id:e,dock:t.dock,order:(s==null?void 0:s.order)??0,isOpen:(s==null?void 0:s.isOpen)??t.defaultOpen??!1};this.panelPlacements.set(e,r),this.movePanelToDock(e,t.dock),r.isOpen&&n.toggle(),this.notify()}movePanelToDock(e,t){const n=document.getElementById(e),s=this.dockElements.get(t);if(!n||!s)return;n.style.pointerEvents="auto",n.parentElement&&n.parentElement.removeChild(n);const a=this.getPlacementsInDock(t).findIndex(c=>c.order>this.panelPlacements.get(e).order),o=Array.from(s.children),l=a>=0&&a<o.length?o[a]:null;s.insertBefore(n,l)}getPlacementsInDock(e){return Array.from(this.panelPlacements.values()).filter(t=>t.dock===e).sort((t,n)=>t.order-n.order)}setPanelOpen(e,t){const n=this.panelPlacements.get(e);n&&n.isOpen!==t&&(n.isOpen=t,this.isManualOverride=!0,this.currentWorkspace!=="free"&&(this.currentWorkspace="free"),this.persist(),this.notify())}setPanelOrder(e,t){const n=this.panelPlacements.get(e);n&&(n.order=t,this.isManualOverride=!0,this.currentWorkspace!=="free"&&(this.currentWorkspace="free"),this.movePanelToDock(e,n.dock),this.persist(),this.notify())}setPanelDock(e,t){const n=this.panelPlacements.get(e);n&&n.dock!==t&&(n.dock=t,n.order=this.getPlacementsInDock(t).length,this.isManualOverride=!0,this.currentWorkspace!=="free"&&(this.currentWorkspace="free"),this.movePanelToDock(e,t),this.persist(),this.notify())}applyWorkspace(e){const t=Qb[e];if(t){this.currentWorkspace=e,this.isManualOverride=!1,no.show(t.viewId);for(const n of t.placements){const s=$t.get(n.id);if(!s)continue;this.panelPlacements.get(n.id);const r={id:n.id,dock:n.dock,order:n.order,isOpen:n.isOpen};this.panelPlacements.set(n.id,r),this.movePanelToDock(n.id,n.dock),s.isOpen()!==n.isOpen&&s.toggle()}for(const[n,s]of $t.list().map(r=>[r.id,r]))t.placements.some(r=>r.id===n)||s.isOpen()&&!["cell-drawer","help-overlay"].includes(n)&&s.toggle();this.persist(),this.notify()}}reset(){this.applyWorkspace("watch"),this.clearPersisted()}getCurrentWorkspace(){return this.currentWorkspace}isFree(){return this.currentWorkspace==="free"||this.isManualOverride}getPlacements(){return Array.from(this.panelPlacements.values())}getPlacement(e){return this.panelPlacements.get(e)}onChange(e){return this.listeners.add(e),()=>this.listeners.delete(e)}notify(){for(const e of this.listeners)e()}persist(){try{const e={id:this.currentWorkspace,viewId:no.activeId??"space",placements:this.getPlacements(),updatedAt:Date.now()};localStorage.setItem(Uc,JSON.stringify(e))}catch{}}restoreOrDefault(){try{const e=localStorage.getItem(Uc);if(e){const t=JSON.parse(e);if(t.placements&&Array.isArray(t.placements)){this.applyWorkspace(t.id);return}}}catch{}this.applyWorkspace("watch")}clearPersisted(){try{localStorage.removeItem(Uc)}catch{}}buildWorkspaceSwitcher(){const e=document.createElement("div");e.className="workspace-switcher",e.style.cssText=`
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
    `,n.addEventListener("click",()=>this.reset()),n.addEventListener("mouseenter",()=>n.style.color="var(--text-primary)"),n.addEventListener("mouseleave",()=>n.style.color="var(--text-muted)"),e.appendChild(n),e}refreshSwitcher(e){for(const t of e.querySelectorAll("button[data-workspace]")){const n=t.dataset.workspace,s=this.currentWorkspace===n;t.style.background=s?"var(--bg-primary)":"transparent",t.style.color=s?"var(--text-primary)":"var(--text-secondary)",t.style.border=s?"1px solid var(--border-bright)":"none"}}}const la=new eM;function Nc(){return la}class tM{constructor(){M(this,"panels",new Map);M(this,"listeners",new Set)}register(e){this.panels.set(e.id,e),this.notify()}get(e){return this.panels.get(e)}list(){return[...this.panels.values()]}toggle(e){const t=this.panels.get(e);t&&(t.toggle(),la.setPanelOpen(e,t.isOpen()),this.notify())}isOpen(e){const t=this.panels.get(e);return t?t.isOpen():!1}openIds(){return this.list().filter(e=>e.isOpen()).map(e=>e.id)}byKey(e){return this.list().find(t=>t.key===e)}onChange(e){return this.listeners.add(e),()=>{this.listeners.delete(e)}}notify(){for(const e of this.listeners)e()}}const $t=new tM,Ph="panel-hidden";function Lh(i,e){i&&i.classList.toggle(Ph,e)}function Hp(i){const e=document.createElement("button");return e.className="panel-close",e.setAttribute("aria-label","close"),e.textContent="×",e.style.cssText=`
    background: none;
    border: none;
    color: var(--text-secondary);
    font-size: 16px;
    line-height: 1;
    cursor: pointer;
    padding: 2px 4px;
    flex: 0 0 auto;
    pointer-events: auto;
  `,e.addEventListener("click",t=>{t.stopPropagation(),i()}),e}class nM{constructor(){M(this,"name","PanelRail");M(this,"container",null);M(this,"buttons",new Map);M(this,"unsubscribe",null)}async init(){const e=document.getElementById("ui-overlay");e&&(this.container=document.createElement("div"),this.container.id="panel-rail",this.container.style.cssText=`
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
    `,e.appendChild(this.container),this.build(),this.unsubscribe=$t.onChange(()=>this.refresh()))}async destroy(){var e,t;(e=this.unsubscribe)==null||e.call(this),this.unsubscribe=null,(t=this.container)==null||t.remove(),this.container=null,this.buttons.clear()}build(){if(this.container){this.container.innerHTML="",this.buttons.clear();for(const e of $t.list()){const t=document.createElement("button");t.className="panel-rail-button",t.textContent=e.glyph,t.title=e.key?`${e.label} (${e.key.toUpperCase()})`:e.label,t.style.cssText=`
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
      `,t.addEventListener("click",()=>$t.toggle(e.id)),this.container.appendChild(t),this.buttons.set(e.id,t)}this.light()}}refresh(){if(!this.container)return;const e=$t.list().map(s=>s.id),t=[...this.buttons.keys()];if(e.length!==t.length||e.some((s,r)=>s!==t[r])){this.build();return}this.light()}light(){for(const e of $t.list()){const t=this.buttons.get(e.id);if(!t)continue;const n=e.isOpen();t.style.color=n?"var(--text-primary)":"var(--text-muted)",t.style.borderColor=n?"var(--border-bright)":"var(--border)",t.style.background=n?"var(--bg-primary)":"var(--bg-tertiary)"}}}const iM=new nM;Zn.register(iM);function Vp(i,e,t,n,s,r){$t.register({id:i,label:e,glyph:t,key:r,toggle:n,isOpen:s})}function sr(i,e,t,n,s){Vp(i,e,t,()=>{const r=n();r&&Lh(r,!r.classList.contains(Ph))},()=>{const r=n();return r?!r.classList.contains(Ph):!1},s)}const sM=500,hf=60;function rM(){return`
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
  `}class aM{constructor(){M(this,"name","ControlBar");M(this,"container",null);M(this,"playButton",null);M(this,"stepButton",null);M(this,"stopButton",null);M(this,"slider",null);M(this,"ceilingValue",null);M(this,"levelFill",null);M(this,"levelText",null);M(this,"cpuFill",null);M(this,"cpuText",null);M(this,"trace",null);M(this,"statusText",null);M(this,"timer",null);M(this,"payload",null);M(this,"samples",[]);M(this,"layoutUnsubscribe",null);M(this,"workspaceSwitcherContainer",null)}async init(){this.container=Ps({id:"control-bar",title:"Control Bar",glyph:"⏯",body:rM(),dock:"bottom",defaultOpen:!0,className:"control-bar-panel"}),this.bindElements(),this.bindEvents(),sr("control-bar","control bar","⏯",()=>this.container),this.layoutUnsubscribe=Nc().onChange(()=>this.refreshWorkspaceSwitcher()),this.timer=window.setInterval(()=>{this.poll()},sM),this.poll()}async destroy(){var e,t;this.timer!==null&&window.clearInterval(this.timer),this.timer=null,(e=this.layoutUnsubscribe)==null||e.call(this),this.layoutUnsubscribe=null,(t=this.container)==null||t.remove()}refreshWorkspaceSwitcher(){if(!this.workspaceSwitcherContainer)return;const e=this.workspaceSwitcherContainer.querySelector(".workspace-switcher");e&&Nc().refreshSwitcher(e)}bindElements(){if(!this.container)return;const e=this.container.querySelectorAll(".verb");if(this.playButton=e[0],this.stepButton=e[1],this.stopButton=e[2],this.slider=this.container.querySelector(".ceiling-slider"),this.ceilingValue=this.container.querySelector(".ceiling-value"),this.levelFill=this.container.querySelector(".level-fill"),this.levelText=this.container.querySelector(".level-text"),this.cpuFill=this.container.querySelector(".cpu-fill"),this.cpuText=this.container.querySelector(".cpu-text"),this.trace=this.container.querySelector("canvas.trace-canvas"),this.statusText=this.container.querySelector(".status-text"),this.workspaceSwitcherContainer=this.container.querySelector(".workspace-switcher"),this.workspaceSwitcherContainer){const t=Nc().buildWorkspaceSwitcher();this.workspaceSwitcherContainer.appendChild(t)}}bindEvents(){var e,t,n,s,r;this.container&&((e=this.playButton)==null||e.addEventListener("click",()=>this.togglePlay()),(t=this.stepButton)==null||t.addEventListener("click",()=>this.step()),(n=this.stopButton)==null||n.addEventListener("click",()=>this.stop()),(s=this.slider)==null||s.addEventListener("input",a=>{const o=a.target,l=Number(o.value);this.ceilingValue&&(this.ceilingValue.textContent=String(l))}),(r=this.slider)==null||r.addEventListener("change",()=>{var o;const a=Number(((o=this.slider)==null?void 0:o.value)??1);this.command({max_workers:a})}),this.container.querySelector(".door-btn").addEventListener("click",()=>$t.toggle("control-panel")))}togglePlay(){var e;this.command({paused:!((e=this.payload)!=null&&e.control.paused)})}step(){this.command({step:!0})}stop(){window.confirm("Stop the run? The run ends at its next boundary.")&&this.command({cancel:!0})}async poll(){var e,t;try{const n=await fetch("/api/control");if(!n.ok)return;const s=await n.json();for(this.payload=s,this.samples.push({level:((e=s.status)==null?void 0:e.in_flight)??0,cpu:((t=s.machine)==null?void 0:t.cpu_percent)??0});this.samples.length>hf;)this.samples.shift();this.render()}catch{}}async command(e){var n;const t=(n=this.payload)==null?void 0:n.control.revision;try{const s=await fetch("/api/control",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({...e,revision:t})});if(!s.ok){const r=await s.json().catch(()=>({}));this.setStatus(r.error??"the control plane refused the command");return}await this.poll()}catch{this.setStatus("the dashboard could not reach the server")}}render(){var l,c;const e=this.payload;if(!e)return;const t=e.control,n=e.status,s=(n==null?void 0:n.in_flight)??0,r=t.max_workers??(n==null?void 0:n.ceiling)??0,a=((l=e.machine)==null?void 0:l.cpu_percent)??0;if(this.playButton){const h=t.paused;this.playButton.textContent=h?"▶":"⏸",this.playButton.classList.toggle("verb-primary",h),this.playButton.classList.toggle("verb-danger",!h),this.playButton.title=h?"Play — release the run":"Pause — hold the run at its next boundary",this.playButton.setAttribute("aria-label",h?"play":"pause")}if(this.stepButton){const h=t.paused&&e.readable;this.stepButton.disabled=!h,this.stepButton.title=h?"Step — release exactly one more batch":t.paused?"Step — control plane not readable":"Step — the run is not paused"}this.stopButton&&(this.stopButton.disabled=!e.readable,this.stopButton.title="Stop — end the run at its next boundary");const o=e.readable?"":e.error??"the control plane could not be read";if(this.playButton&&(this.playButton.disabled=!e.readable),this.playButton&&o&&(this.playButton.title=o),this.slider){const h=Math.max(1,((c=e.machine)==null?void 0:c.cpu_count)??1,r||1);this.slider.max=String(h),this.slider.value=String(Math.max(1,r||1)),this.slider.disabled=!e.readable,this.slider.title=o||`The ceiling on cells in flight — ${r||"the run's own"}`}if(this.ceilingValue&&(this.ceilingValue.textContent=r?String(r):"—"),this.levelFill){const h=r?Math.min(1,s/r):0;this.levelFill.style.width=`${h*100}%`,h===0?this.levelFill.style.background="var(--promoted)":h<.5?this.levelFill.style.background="var(--promoted)":h<.85?this.levelFill.style.background="var(--warn)":this.levelFill.style.background="var(--error)"}if(this.levelText&&(this.levelText.textContent=`${s}${r?` / ${r}`:""}`),this.cpuFill){const h=Math.min(100,Math.max(0,a));this.cpuFill.style.width=`${h}%`,h<30?this.cpuFill.style.background="var(--cpu)":h<70?this.cpuFill.style.background="var(--warn)":this.cpuFill.style.background="var(--error)"}if(this.cpuText&&(this.cpuText.textContent=`${a.toFixed(0)}%`),this.drawTrace(),this.statusText&&!o){const h=n!=null&&n.stage?n.stage.replace("s","S"):"";this.statusText.textContent=n?`${h} · ${n.cells_done} cells`:"no run is reporting"}}drawTrace(){var c,h,u;const e=this.trace;if(!e)return;const t=e.getContext("2d");if(!t)return;const n=e.width,s=e.height;t.clearRect(0,0,n,s);const r=Math.max(1,((c=this.payload)==null?void 0:c.control.max_workers)??((u=(h=this.payload)==null?void 0:h.status)==null?void 0:u.ceiling)??1),a=n/Math.max(1,hf-1),o=n-(this.samples.length-1)*a;t.strokeStyle="var(--border)",t.lineWidth=.5,[.25,.5,.75].forEach(d=>{const f=s*d;t.beginPath(),t.moveTo(0,f),t.lineTo(n,f),t.stroke()}),t.beginPath(),t.strokeStyle="var(--cpu)",t.globalAlpha=.7,t.lineWidth=1,this.samples.forEach((d,f)=>{const g=o+f*a,v=s-Math.min(100,d.cpu)/100*s;f===0?t.moveTo(g,v):t.lineTo(g,v)}),t.stroke(),t.globalAlpha=1;const l=t.createLinearGradient(0,s,0,0);if(l.addColorStop(0,"var(--promoted)"),l.addColorStop(.5,"var(--warn)"),l.addColorStop(1,"var(--error)"),t.strokeStyle=l,t.lineWidth=1.5,t.lineCap="round",t.lineJoin="round",this.samples.forEach((d,f)=>{const g=o+f*a,v=s-Math.min(1,d.level/r)*s;f===0?t.moveTo(g,v):t.lineTo(g,v)}),t.stroke(),this.samples.length>0){const d=this.samples[this.samples.length-1],f=n-2,g=s-Math.min(100,d.cpu)/100*s;t.fillStyle="var(--cpu)",t.beginPath(),t.arc(f,g,2.5,0,Math.PI*2),t.fill();const v=s-Math.min(1,d.level/r)*s,p=d.level/r;t.fillStyle=p<.5?"var(--promoted)":p<.85?"var(--warn)":"var(--error)",t.beginPath(),t.arc(f-6,v,2.5,0,Math.PI*2),t.fill()}}setStatus(e){this.statusText&&(this.statusText.textContent=e)}}const Ya=new aM;Zn.register(Ya);const Oc=["substrate","geometry","dynamics","plasticity","credit","update"];function oM(){return`
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
  `}class lM{constructor(){M(this,"name","ControlPanel");M(this,"container",null);M(this,"profiles",[]);M(this,"axes",[]);M(this,"newRunSection",null);M(this,"runSection",null);M(this,"queueSection",null);M(this,"cellSection",null);M(this,"exportSection",null);M(this,"profileSelect",null);M(this,"seedsInput",null);M(this,"epochsInput",null);M(this,"budgetInput",null);M(this,"deviceSelect",null);M(this,"fidelitySelect",null);M(this,"profileNote",null);M(this,"newRunNote",null);M(this,"cellSelects",new Map);M(this,"cellNote",null);M(this,"exportNote",null)}async init(){this.container=Ps({id:"control-panel",title:"Control Panel",glyph:"⚙",key:Qd.panel,body:oM(),dock:"floating",defaultOpen:!1}),this.bindElements(),this.bindEvents(),sr("control-panel","control panel","⚙",()=>this.container,Qd.panel),await this.loadCatalogue(),this.refresh()}async destroy(){var e;(e=this.container)==null||e.remove()}bindElements(){if(!this.container)return;this.newRunSection=this.container.querySelector(".new-run-note"),this.runSection=this.container.querySelector(".run-section"),this.queueSection=this.container.querySelector(".queue-section"),this.cellSection=this.container.querySelector(".cell-section"),this.exportSection=this.container.querySelector(".export-note"),this.profileSelect=this.container.querySelector(".profile"),this.profileNote=this.container.querySelector(".profile-note"),this.newRunNote=this.container.querySelector(".new-run-note"),this.cellNote=this.container.querySelector(".cell-note"),this.exportNote=this.container.querySelector(".export-note"),this.seedsInput=this.container.querySelector(".seeds"),this.epochsInput=this.container.querySelector(".epochs"),this.budgetInput=this.container.querySelector(".budget"),this.deviceSelect=this.container.querySelector(".device"),this.fidelitySelect=this.container.querySelector(".fidelity");const e=this.container.querySelector(".cell-row");for(const t of Oc){const n=document.createElement("label");n.textContent=t;const s=document.createElement("select");s.className=`cell-${t}`,n.appendChild(s),e.appendChild(n),this.cellSelects.set(t,s)}this.container.querySelector("#control-panel-header").appendChild(Hp(()=>$t.toggle("control-panel")))}bindEvents(){var e;this.container&&((e=this.profileSelect)==null||e.addEventListener("change",()=>this.renderProfileNote()),this.container.querySelector(".start").addEventListener("click",()=>void this.startRun()),this.container.querySelector(".replicate").addEventListener("click",()=>void this.cellAction("replicate")),this.container.querySelector(".preregister").addEventListener("click",()=>void this.cellAction("preregister")),this.container.querySelector(".quest").addEventListener("click",()=>void this.cellAction("quest")),this.container.querySelector(".export-script").addEventListener("click",()=>void this.export("script")),this.container.querySelector(".export-report").addEventListener("click",()=>void this.export("report")),this.container.querySelector(".export-records").addEventListener("click",()=>void this.export("records")))}async loadCatalogue(){try{const[e,t]=await Promise.all([fetch("/api/profiles").then(n=>n.json()),fetch("/api/axes").then(n=>n.json())]);this.profiles=e.profiles??[],this.axes=t.axes??[]}catch{this.profiles=[],this.axes=[]}this.renderProfileOptions(),this.renderCellOptions()}async refresh(){await Promise.all([this.refreshRuns(),this.refreshQueue(),this.refreshStatus()])}async refreshRuns(){if(this.runSection)try{const t=await(await fetch("/api/runs")).json(),n=this.currentRunId(),s=(t.runs??[]).find(r=>r.run_id===n);this.runSection.innerHTML=this.renderRun(s)}catch{this.runSection.innerHTML='<div class="note">the store did not answer</div>'}}async refreshQueue(){if(this.queueSection)try{const[e,t]=await Promise.all([fetch("/api/campaigns").then(n=>n.json()),fetch("/api/queue").then(n=>n.json())]);this.queueSection.innerHTML=this.renderQueue(e.campaigns??[],t),this.queueSection.querySelectorAll("[data-cancel]").forEach(n=>n.addEventListener("click",()=>{this.cancelCampaign(n.dataset.cancel??"")})),this.queueSection.querySelectorAll("[data-preempt]").forEach(n=>n.addEventListener("click",()=>{this.preemptCampaign(n.dataset.preempt??"")}))}catch{this.queueSection.innerHTML='<div class="note">the queue did not answer</div>'}}async refreshStatus(){if(this.newRunSection)try{const t=await(await fetch("/api/control")).json();if(!t.readable){this.newRunNote.textContent=t.error??"the control plane could not be read";return}const n=t.status;this.newRunNote.textContent=n?`The run is in ${n.stage} with ${n.cells_done} cells measured.`:"No run is reporting. The panel can still start one."}catch{this.newRunNote.textContent="the server did not answer"}}currentRunId(){return Kn.selectedId??null}renderProfileOptions(){if(this.profileSelect){this.profileSelect.innerHTML="";for(const e of this.profiles){const t=document.createElement("option");t.value=e.name,t.textContent=e.name,this.profileSelect.appendChild(t)}this.renderProfileNote()}}renderProfileNote(){if(!this.profileNote||!this.profileSelect)return;const e=this.profiles.find(t=>t.name===this.profileSelect.value);if(!e){this.profileNote.textContent="";return}this.profileNote.textContent=[e.description,`fidelity ${e.fidelity} · ${e.n_seeds} seeds · ${e.epochs} epochs`,e.budget_seconds?`budget ${e.budget_seconds}s`:"no budget",`policy ${e.policy}`,`axes ${e.axes.map(t=>t.axis).join(", ")||"all"}`].join(" · "),this.seedsInput&&(this.seedsInput.value=String(e.n_seeds)),this.epochsInput&&(this.epochsInput.value=String(e.epochs)),this.budgetInput&&(this.budgetInput.value=e.budget_seconds?String(e.budget_seconds):""),this.fidelitySelect&&(this.fidelitySelect.value=e.fidelity)}renderCellOptions(){for(const e of Oc){const t=this.cellSelects.get(e);if(!t)continue;const n=this.axes.find(r=>r.axis===e);t.innerHTML="";for(const r of(n==null?void 0:n.primitives)??[]){const a=document.createElement("option");a.value=r.name,a.textContent=r.available?r.name:`${r.name} (unavailable)`,a.disabled=!r.available,t.appendChild(a)}const s=t.querySelector("option:not([disabled])");s&&(t.value=s.value)}}renderRun(e){if(!e)return'<div class="note">no run is selected</div>';const t=e.declaration??{};return[`<div class="note">A run's declaration is frozen once it has begun; the panel shows it rather than offering an editor that would lie.</div>`,`<table class="kv">${[["run",e.run_id],["status",String(e.status)],["profile",String(t.profile??"—")],["tasks",(t.tasks??[]).join(", ")||"—"],["fidelity",String(t.fidelity??"—")],["objectives",(t.objectives??[]).join(", ")||"—"],["mode",String(t.mode??"—")],["declared cells",String(t.declared_cells??"—")],["records",String(e.records)],["seeds still owed",String(e.seeds_owed??"—")]].map(([s,r])=>`<tr><th>${s}</th><td>${r}</td></tr>`).join("")}</table>`].join("")}renderQueue(e,t){const n=e.map(r=>`<tr>
          <td>${r.campaign_id}</td>
          <td>${r.name}</td>
          <td>${r.status}</td>
          <td>
            <button data-cancel="${r.campaign_id}" class="mini">cancel</button>
            <button data-preempt="${r.campaign_id}" class="mini">preempt</button>
          </td>
        </tr>`).join("");return[`<table class="kv">${[["max concurrent",String(t.max_concurrent??"—")],["max cpus",String(t.max_cpus??"—")],["max gpus",String(t.max_gpus??"—")]].map(([r,a])=>`<tr><th>${r}</th><td>${a}</td></tr>`).join("")}</table>`,n?`<table class="list"><tr><th>id</th><th>name</th><th>status</th><th></th></tr>${n}</table>`:'<div class="note">the queue is empty</div>'].join("")}async startRun(){var t,n,s,r,a;if(!this.profileSelect)return;const e={};(t=this.seedsInput)!=null&&t.value&&(e.n_seeds=Number(this.seedsInput.value)),(n=this.epochsInput)!=null&&n.value&&(e.epochs=Number(this.epochsInput.value)),(s=this.budgetInput)!=null&&s.value&&(e.budget_seconds=Number(this.budgetInput.value)),(r=this.fidelitySelect)!=null&&r.value&&(e.fidelity=this.fidelitySelect.value);try{const l=await(await fetch("/api/runs",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({profile:this.profileSelect.value,overrides:e,device:((a=this.deviceSelect)==null?void 0:a.value)??void 0})})).json();l.started?this.newRunNote.textContent=`The run is queued as ${l.campaign_id}.`:this.newRunNote.textContent=`${l.error??"the run was refused"}. ${l.command??""}`}catch{this.newRunNote.textContent="the dashboard could not reach the server"}}cellCoordinate(){var t;const e={};for(const n of Oc)e[n]=((t=this.cellSelects.get(n))==null?void 0:t.value)??"";return e}async cellAction(e){const t=this.currentRunId();if(!t){this.cellNote.textContent="no run is selected";return}try{const s=await(await fetch(`/api/cells/${t}/${e}`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({coordinate:this.cellCoordinate()})})).json();this.cellNote.textContent=s.error??s.message??`${e} was refused`}catch{this.cellNote.textContent="the dashboard could not reach the server"}}async cancelCampaign(e){await fetch(`/api/campaigns/${e}/cancel`,{method:"POST"}),await this.refreshQueue()}async preemptCampaign(e){await fetch(`/api/campaigns/${e}/preempt`,{method:"POST"}),await this.refreshQueue()}async export(e){const t=this.currentRunId();if(!t){this.exportNote.textContent="no run is selected";return}try{if(e==="script"){const a=await fetch("/api/narration").then(o=>o.json());this.download("narration.txt",a.script??""),this.exportNote.textContent="the narration script was taken";return}const n=e==="report"?"report":"records",s=await fetch(`/api/runs/${t}/${n}`).then(a=>a.json());if(s.error){this.exportNote.textContent=s.error;return}const r=e==="report"?s.report??"":JSON.stringify(s.records??[],null,2);this.download(`${t}-${n}.${e==="report"?"txt":"json"}`,r),this.exportNote.textContent=`the ${e} was taken`}catch{this.exportNote.textContent="the dashboard could not reach the server"}}download(e,t){const n=new Blob([t],{type:"text/plain"}),s=document.createElement("a");s.download=e,s.href=URL.createObjectURL(n),s.click(),URL.revokeObjectURL(s.href)}}const Gp=new lM;Zn.register(Gp);function cM(){return`
    <div id="drawer-content"></div>
  `}class hM{constructor(){M(this,"name","CellDrawer");M(this,"panel",null);M(this,"content",null);M(this,"sparklineCanvas",null);M(this,"currentData",null);M(this,"onKeyDown",e=>{e.key==="Escape"&&this.currentData&&this.hide()});M(this,"onCellSelected",e=>{this.show(e.detail)})}async init(){this.panel=Ps({id:"cell-drawer",title:"Cell Details",glyph:"◧",body:cM(),dock:"floating",defaultOpen:!1}),this.content=this.panel.querySelector("#drawer-content"),Vp("cell-drawer","cell drawer","◧",()=>this.hide(),()=>this.isOpen()),console.log("[CellDrawer] Initialized")}async destroy(){var e;this.stopSparkline(),(e=this.panel)==null||e.remove(),window.removeEventListener("cell-selected",this.onCellSelected),window.removeEventListener("keydown",this.onKeyDown)}setupEvents(){window.addEventListener("cell-selected",this.onCellSelected),window.addEventListener("keydown",this.onKeyDown)}isOpen(){return this.panel?!this.panel.classList.contains("panel-hidden"):!1}hasCellSelected(){return this.currentData!==null}show(e){this.currentData=e,this.renderContent(e),$t.toggle("cell-drawer"),this.startSparkline(e)}hide(){$t.toggle("cell-drawer"),this.stopSparkline(),this.currentData=null}renderContent(e){if(!this.content)return;const{coordinate:t,metrics:n,status:s}=e,r=qt[t.credit]||k.gradient,a=(n==null?void 0:n.val_acc)??0,o=(n==null?void 0:n.n_seeds)??0,l=e.chance??.1,c=e.requiredSeeds??0;let h="UNMEASURED",u=k.legal_unmeasured;s==="void"&&(h="VOID",u=k.void),s==="measured"&&(a<=l?(h="REJECTED",u=k.rejected):c>0&&o<c?(h="INSUFFICIENT",u=k.insufficient):a>l+.1?(h="PASSED",u=k.passed):(h="INSUFFICIENT",u=k.insufficient));const d=s==="measured"&&c>0?Math.max(0,c-o):"N/A";this.content.innerHTML=`
      <div style="margin-bottom: 20px;">
        <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px;">
          ${Object.entries(t).filter(([,f])=>f).map(([f,g])=>`
              <span class="coord-chip" data-axis="${f}" style="
                background: ${f==="credit"?r+"22":"var(--bg-tertiary)"};
                border: 1px solid ${f==="credit"?r+"88":"var(--border)"};
                border-radius: 12px;
                font-size: 11px;
                color: ${f==="credit"?r:"var(--text-primary)"};
              ">
                ${f}=${g}
              </span>
            `).join("")}
        </div>
      </div>

      ${n?`
        <div style="margin-bottom: 20px;">
          <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 4px;">VALIDATION ACCURACY</div>
          <div class="drawer-metric-value">${a.toFixed(3)}</div>
          <div style="font-size: 11px; color: var(--text-secondary); margin-top: 4px;">
            ± ${(n.val_acc_std??0).toFixed(3)} (n=${o})
          </div>
        </div>
      `:""}

      <div style="margin-bottom: 20px; padding: 12px; background: var(--bg-tertiary); border-radius: 6px;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
          <span class="verdict-badge" style="
            background: ${u}22;
            border: 1px solid ${u}88;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            color: ${u};
            text-transform: uppercase;
            padding: 4px 10px;
          ">${h}</span>
          <span style="font-size: 12px; color: var(--text-secondary);">Chance level: ${l}</span>
        </div>
        ${e.voidReason?`<div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 8px;">${e.voidReason}</div>`:""}
        <div class="progress-bar" style="height: 4px; background: var(--bg); border-radius: 2px; overflow: hidden;">
          <div class="progress-fill" style="
            width: ${Math.min(100,a/(l*2)*100)}%;
            height: 100%;
            background: linear-gradient(90deg, ${k.rejected}, ${k.insufficient}, ${k.passed});
            border-radius: 2px;
          "></div>
        </div>
      </div>

      ${s==="measured"?`
        <div style="margin-bottom: 20px;">
          <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 8px;">SEEDS TO CLAIM</div>
          <div class="drawer-metric-value" style="color: ${k.insufficient};">
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
    `,this.wireActions(e)}actionStates(e){var a;if(e.status==="void")return{replicate:!1,preregister:!1,quest:!1};const t=e.status==="measured",n=((a=e.metrics)==null?void 0:a.n_seeds)??0,s=e.requiredSeeds??0;return{replicate:(s>0?Math.max(0,s-n):0)>0||!t,preregister:t,quest:!t}}wireActions(e){const t=this.content;if(!t)return;const n=this.actionStates(e);t.querySelectorAll(".drawer-btn[data-action]").forEach(o=>{const l=o.dataset.action??"",c=n[l]===!0;o.disabled=!c,o.addEventListener("click",()=>{this.runAction(l,e)})});const r=t.querySelector('.drawer-btn[data-action="replicate"]');r&&(r.textContent=e.status==="measured"?"Queue Rest":"Queue");const a=t.querySelector("#drawer-action-note");a&&(a.textContent=this.actionNote(e))}actionNote(e){var s;if(!e.runId)return"This cell belongs to no run yet — nothing to queue or register.";if(e.status==="void")return`The system refuses this cell.${e.voidReason?` ${e.voidReason}`:""}`;if(e.status==="measured"){const r=((s=e.metrics)==null?void 0:s.n_seeds)??0,a=e.requiredSeeds??0,o=Math.max(0,a-r);return o>0?`Queue Rest adds ${o} more seeds to reach the claim threshold (${a} needed). Preregister locks in this cell's protocol for a confirmatory run.`:"This cell has enough seeds for a claim. Preregister locks in the protocol for a confirmatory run."}const t=e.inDeclaration===!1?" (outside this run's declaration)":"";return`Queue measures this cell (${e.requiredSeeds??0} seeds). Adopt as Quest writes the question first, then queues a new confirming run.${t}`}setStatus(e,t=!1){var s;const n=(s=this.content)==null?void 0:s.querySelector("#drawer-status");n&&(n.textContent=e,n.style.color=t?k.rejected:k.text_secondary)}async runAction(e,t){var o,l;if(!t.runId){this.setStatus("This cell belongs to no run yet.",!0);return}const n=Array.from(((o=this.content)==null?void 0:o.querySelectorAll(".drawer-btn"))??[]);n.forEach(c=>{c.disabled=!0}),this.setStatus("Working…");const s=(l=this.content)==null?void 0:l.querySelector("#drawer-threshold"),r=s!=null&&s.value?Number(s.value):null,a={coordinate:t.coordinate};r!==null&&Number.isFinite(r)&&(a.threshold=r);try{const c=await fetch(`/api/cells/${t.runId}/${e}`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(a)}),h=await c.json();if(!c.ok){this.setStatus((h==null?void 0:h.error)??"The action failed.",!0);return}this.setStatus(this.actionSummary(e,h))}catch(c){this.setStatus(`The action failed: ${String(c)}`,!0)}finally{n.forEach(c=>{c.disabled=!1})}}actionSummary(e,t){if(e==="replicate")return`Queued campaign ${t.campaign_id}: ${t.measurements} measurements in a plan of ${t.plan}.`;const s=`${t.written?"Registered":"Already registered"} ${t.path} — commit it; the run that follows it can be confirmatory.`;return e!=="quest"?s:t.campaign_id?`${s} Queued campaign ${t.campaign_id}: ${t.measurements} measurements in a plan of ${t.plan}, in a new run.`:`${s} No campaign queue is attached, so nothing is scheduled.`}startSparkline(e){const t=document.getElementById("sparkline-container");if(!t)return;this.stopSparkline();const n=e.curve??[];if(n.length===0){t.innerHTML=`
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
      `;return}const s=document.createElement("canvas");s.style.width="100%",s.style.height="100%",t.appendChild(s);const r=s.getContext("2d"),a=Math.min(window.devicePixelRatio,2),o=t.getBoundingClientRect();s.width=o.width*a,s.height=o.height*a,r.scale(a,a);const l=o.width,c=o.height,h=e.chance??.1,u=n.map(A=>A.val_acc),d=Math.min(h,...u),f=Math.max(...u,h),v=(f-d||1)*.1,p=d-v,m=f+v,S=A=>A/(n.length-1||1)*(l-20)+10,_=A=>c-10-(A-p)/(m-p)*(c-20);r.fillStyle=getComputedStyle(document.documentElement).getPropertyValue("--bg").trim()||"#0a0e14",r.fillRect(0,0,l,c);const b=_(h);r.strokeStyle=k.chance_line,r.lineWidth=1,r.setLineDash([4,4]),r.beginPath(),r.moveTo(10,b),r.lineTo(l-10,b),r.stroke(),r.setLineDash([]),r.fillStyle=k.chance_line,r.font="9px 'JetBrains Mono', monospace",r.textAlign="left",r.fillText("chance",12,b-4);const I=qt[e.coordinate.credit]||k.gradient;r.strokeStyle=I,r.lineWidth=2,r.lineCap="round",r.lineJoin="round",r.beginPath(),n.forEach((A,R)=>{const N=S(R),w=_(A.val_acc);R===0?r.moveTo(N,w):r.lineTo(N,w)}),r.stroke(),r.fillStyle=I,n.forEach((A,R)=>{const N=S(R),w=_(A.val_acc);r.beginPath(),r.arc(N,w,3,0,Math.PI*2),r.fill()}),r.fillStyle=k.text_muted,r.font="9px 'JetBrains Mono', monospace",r.textAlign="right",r.fillText(m.toFixed(2),8,14),r.fillText(p.toFixed(2),8,c-6),this.sparklineCanvas=s}stopSparkline(){this.sparklineCanvas&&(this.sparklineCanvas.remove(),this.sparklineCanvas=null)}}const ca=new hM;Zn.register(ca);const uM=!0,hn="u-",dM="uplot",fM=hn+"hz",pM=hn+"vt",mM=hn+"title",gM=hn+"wrap",vM=hn+"under",xM=hn+"over",_M=hn+"axis",Xs=hn+"off",yM=hn+"select",SM=hn+"cursor-x",bM=hn+"cursor-y",MM=hn+"cursor-pt",wM=hn+"legend",EM=hn+"live",TM=hn+"inline",AM=hn+"series",CM=hn+"marker",uf=hn+"label",RM=hn+"value",Ga="width",Wa="height",za="top",df="bottom",Vr="left",Fc="right",au="#000",ff=au+"0",kc="mousemove",pf="mousedown",Bc="mouseup",mf="mouseenter",gf="mouseleave",vf="dblclick",PM="resize",LM="scroll",xf="change",xl="dppxchange",ou="--",va=typeof window<"u",Dh=va?document:null,Zr=va?window:null,DM=va?navigator:null;let bt,Qo;function Ih(){let i=devicePixelRatio;bt!=i&&(bt=i,Qo&&Nh(xf,Qo,Ih),Qo=matchMedia(`(min-resolution: ${bt-.001}dppx) and (max-resolution: ${bt+.001}dppx)`),Js(xf,Qo,Ih),Zr.dispatchEvent(new CustomEvent(xl)))}function jn(i,e){if(e!=null){let t=i.classList;!t.contains(e)&&t.add(e)}}function Uh(i,e){let t=i.classList;t.contains(e)&&t.remove(e)}function kt(i,e,t){i.style[e]=t+"px"}function mi(i,e,t,n){let s=Dh.createElement(i);return e!=null&&jn(s,e),t!=null&&t.insertBefore(s,n),s}function ii(i,e){return mi("div",i,e)}const _f=new WeakMap;function Ii(i,e,t,n,s){let r="translate("+e+"px,"+t+"px)",a=_f.get(i);r!=a&&(i.style.transform=r,_f.set(i,r),e<0||t<0||e>n||t>s?jn(i,Xs):Uh(i,Xs))}const yf=new WeakMap;function Sf(i,e,t){let n=e+t,s=yf.get(i);n!=s&&(yf.set(i,n),i.style.background=e,i.style.borderColor=t)}const bf=new WeakMap;function Mf(i,e,t,n){let s=e+""+t,r=bf.get(i);s!=r&&(bf.set(i,s),i.style.height=t+"px",i.style.width=e+"px",i.style.marginLeft=n?-e/2+"px":0,i.style.marginTop=n?-t/2+"px":0)}const lu={passive:!0},IM={...lu,capture:!0};function Js(i,e,t,n){e.addEventListener(i,t,n?IM:lu)}function Nh(i,e,t,n){e.removeEventListener(i,t,lu)}va&&Ih();function gi(i,e,t,n){let s;t=t||0,n=n||e.length-1;let r=n<=2147483647;for(;n-t>1;)s=r?t+n>>1:Jn((t+n)/2),e[s]<i?t=s:n=s;return i-e[t]<=e[n]-i?t:n}function Wp(i){return(t,n,s)=>{let r=-1,a=-1;for(let o=n;o<=s;o++)if(i(t[o])){r=o;break}for(let o=s;o>=n;o--)if(i(t[o])){a=o;break}return[r,a]}}const $p=i=>i!=null,qp=i=>i!=null&&i>0,Il=Wp($p),UM=Wp(qp);function NM(i,e,t,n=0,s=!1){let r=s?UM:Il,a=s?qp:$p;[e,t]=r(i,e,t);let o=i[e],l=i[e];if(e>-1)if(n==1)o=i[e],l=i[t];else if(n==-1)o=i[t],l=i[e];else for(let c=e;c<=t;c++){let h=i[c];a(h)&&(h<o?o=h:h>l&&(l=h))}return[o??Rt,l??-Rt]}function Ul(i,e,t,n){let s=Tf(i),r=Tf(e);i==e&&(s==-1?(i*=t,e/=t):(i/=t,e*=t));let a=t==10?ns:Xp,o=s==1?Jn:si,l=r==1?si:Jn,c=o(a(an(i))),h=l(a(an(e))),u=ha(t,c),d=ha(t,h);return t==10&&(c<0&&(u=Pt(u,-c)),h<0&&(d=Pt(d,-h))),n||t==2?(i=u*s,e=d*r):(i=Jp(i,u),e=Nl(e,d)),[i,e]}function cu(i,e,t,n){let s=Ul(i,e,t,n);return i==0&&(s[0]=0),e==0&&(s[1]=0),s}const hu=.1,wf={mode:3,pad:hu},ja={pad:0,soft:null,mode:0},OM={min:ja,max:ja};function _l(i,e,t,n){return Ol(t)?Ef(i,e,t):(ja.pad=t,ja.soft=n?0:null,ja.mode=n?3:0,Ef(i,e,OM))}function yt(i,e){return i??e}function FM(i,e,t){for(e=yt(e,0),t=yt(t,i.length-1);e<=t;){if(i[e]!=null)return!0;e++}return!1}function Ef(i,e,t){let n=t.min,s=t.max,r=yt(n.pad,0),a=yt(s.pad,0),o=yt(n.hard,-Rt),l=yt(s.hard,Rt),c=yt(n.soft,Rt),h=yt(s.soft,-Rt),u=yt(n.mode,0),d=yt(s.mode,0),f=e-i,g=ns(f),v=kn(an(i),an(e)),p=ns(v),m=an(p-g);(f<1e-24||m>10)&&(f=0,(i==0||e==0)&&(f=1e-24,u==2&&c!=Rt&&(r=0),d==2&&h!=-Rt&&(a=0)));let S=f||v||1e3,_=ns(S),b=ha(10,Jn(_)),I=S*(f==0?i==0?.1:1:r),A=Pt(Jp(i-I,b/10),24),R=i>=c&&(u==1||u==3&&A<=c||u==2&&A>=c)?c:Rt,N=kn(o,A<R&&i>=R?R:_i(R,A)),w=S*(f==0?e==0?.1:1:a),y=Pt(Nl(e+w,b/10),24),P=e<=h&&(d==1||d==3&&y>=h||d==2&&y<=h)?h:-Rt,X=_i(l,y>P&&e<=P?P:kn(P,y));return N==X&&N==0&&(X=100),[N,X]}const kM=new Intl.NumberFormat(va?DM.language:"en-US"),uu=i=>kM.format(i),Qn=Math,ll=Qn.PI,an=Qn.abs,Jn=Qn.floor,rn=Qn.round,si=Qn.ceil,_i=Qn.min,kn=Qn.max,ha=Qn.pow,Tf=Qn.sign,ns=Qn.log10,Xp=Qn.log2,BM=(i,e=1)=>Qn.sinh(i)*e,zc=(i,e=1)=>Qn.asinh(i/e),Rt=1/0;function Af(i){return(ns((i^i>>31)-(i>>31))|0)+1}function Oh(i,e,t){return _i(kn(i,e),t)}function Yp(i){return typeof i=="function"}function pt(i){return Yp(i)?i:()=>i}const zM=()=>{},jp=i=>i,Kp=(i,e)=>e,HM=i=>null,Cf=i=>!0,Rf=(i,e)=>i==e,VM=/\.\d*?(?=9{6,}|0{6,})/gm,nr=i=>{if(Qp(i)||Ts.has(i))return i;const e=`${i}`,t=e.match(VM);if(t==null)return i;let n=t[0].length-1;if(e.indexOf("e-")!=-1){let[s,r]=e.split("e");return+`${nr(s)}e${r}`}return Pt(i,n)};function Gs(i,e){return nr(Pt(nr(i/e))*e)}function Nl(i,e){return nr(si(nr(i/e))*e)}function Jp(i,e){return nr(Jn(nr(i/e))*e)}function Pt(i,e=0){if(Qp(i))return i;let t=10**e,n=i*t*(1+Number.EPSILON);return rn(n)/t}const Ts=new Map;function Zp(i){return((""+i).split(".")[1]||"").length}function io(i,e,t,n){let s=[],r=n.map(Zp);for(let a=e;a<t;a++){let o=an(a),l=Pt(ha(i,a),o);for(let c=0;c<n.length;c++){let h=i==10?+`${n[c]}e${a}`:n[c]*l,u=(a>=0?0:o)+(a>=r[c]?0:r[c]),d=i==10?h:Pt(h,u);s.push(d),Ts.set(d,u)}}return s}const Ka={},du=[],ua=[null,null],xs=Array.isArray,Qp=Number.isInteger,GM=i=>i===void 0;function Pf(i){return typeof i=="string"}function Ol(i){let e=!1;if(i!=null){let t=i.constructor;e=t==null||t==Object}return e}function WM(i){return i!=null&&typeof i=="object"}const $M=Object.getPrototypeOf(Uint8Array),em="__proto__";function da(i,e=Ol){let t;if(xs(i)){let n=i.find(s=>s!=null);if(xs(n)||e(n)){t=Array(i.length);for(let s=0;s<i.length;s++)t[s]=da(i[s],e)}else t=i.slice()}else if(i instanceof $M)t=i.slice();else if(e(i)){t={};for(let n in i)n!=em&&(t[n]=da(i[n],e))}else t=i;return t}function nn(i){let e=arguments;for(let t=1;t<e.length;t++){let n=e[t];for(let s in n)s!=em&&(Ol(i[s])?nn(i[s],da(n[s])):i[s]=da(n[s]))}return i}const qM=0,XM=1,YM=2;function jM(i,e,t){for(let n=0,s,r=-1;n<e.length;n++){let a=e[n];if(a>r){for(s=a-1;s>=0&&i[s]==null;)i[s--]=null;for(s=a+1;s<t&&i[s]==null;)i[r=s++]=null}}}function KM(i,e){if(QM(i)){let a=i[0].slice();for(let o=1;o<i.length;o++)a.push(...i[o].slice(1));return ew(a[0])||(a=ZM(a)),a}let t=new Set;for(let a=0;a<i.length;a++){let l=i[a][0],c=l.length;for(let h=0;h<c;h++)t.add(l[h])}let n=[Array.from(t).sort((a,o)=>a-o)],s=n[0].length,r=new Map;for(let a=0;a<s;a++)r.set(n[0][a],a);for(let a=0;a<i.length;a++){let o=i[a],l=o[0];for(let c=1;c<o.length;c++){let h=o[c],u=Array(s).fill(void 0),d=e?e[a][c]:XM,f=[];for(let g=0;g<h.length;g++){let v=h[g],p=r.get(l[g]);v===null?d!=qM&&(u[p]=v,d==YM&&f.push(p)):u[p]=v}jM(u,f,s),n.push(u)}}return n}const JM=typeof queueMicrotask>"u"?i=>Promise.resolve().then(i):queueMicrotask;function ZM(i){let e=i[0],t=e.length,n=Array(t);for(let r=0;r<n.length;r++)n[r]=r;n.sort((r,a)=>e[r]-e[a]);let s=[];for(let r=0;r<i.length;r++){let a=i[r],o=Array(t);for(let l=0;l<t;l++)o[l]=a[n[l]];s.push(o)}return s}function QM(i){let e=i[0][0],t=e.length;for(let n=1;n<i.length;n++){let s=i[n][0];if(s.length!=t)return!1;if(s!=e){for(let r=0;r<t;r++)if(s[r]!=e[r])return!1}}return!0}function ew(i,e=100){const t=i.length;if(t<=1)return!0;let n=0,s=t-1;for(;n<=s&&i[n]==null;)n++;for(;s>=n&&i[s]==null;)s--;if(s<=n)return!0;const r=kn(1,Jn((s-n+1)/e));for(let a=i[n],o=n+r;o<=s;o+=r){const l=i[o];if(l!=null){if(l<=a)return!1;a=l}}return!0}const tm=["January","February","March","April","May","June","July","August","September","October","November","December"],nm=["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];function im(i){return i.slice(0,3)}const tw=nm.map(im),nw=tm.map(im),iw={MMMM:tm,MMM:nw,WWWW:nm,WWW:tw};function Ha(i){return(i<10?"0":"")+i}function sw(i){return(i<10?"00":i<100?"0":"")+i}const rw={YYYY:i=>i.getFullYear(),YY:i=>(i.getFullYear()+"").slice(2),MMMM:(i,e)=>e.MMMM[i.getMonth()],MMM:(i,e)=>e.MMM[i.getMonth()],MM:i=>Ha(i.getMonth()+1),M:i=>i.getMonth()+1,DD:i=>Ha(i.getDate()),D:i=>i.getDate(),WWWW:(i,e)=>e.WWWW[i.getDay()],WWW:(i,e)=>e.WWW[i.getDay()],HH:i=>Ha(i.getHours()),H:i=>i.getHours(),h:i=>{let e=i.getHours();return e==0?12:e>12?e-12:e},AA:i=>i.getHours()>=12?"PM":"AM",aa:i=>i.getHours()>=12?"pm":"am",a:i=>i.getHours()>=12?"p":"a",mm:i=>Ha(i.getMinutes()),m:i=>i.getMinutes(),ss:i=>Ha(i.getSeconds()),s:i=>i.getSeconds(),fff:i=>sw(i.getMilliseconds())};function fu(i,e){e=e||iw;let t=[],n=/\{([a-z]+)\}|[^{]+/gi,s;for(;s=n.exec(i);)t.push(s[0][0]=="{"?rw[s[1]]:s[0]);return r=>{let a="";for(let o=0;o<t.length;o++)a+=typeof t[o]=="string"?t[o]:t[o](r,e);return a}}const aw=new Intl.DateTimeFormat().resolvedOptions().timeZone;function ow(i,e){let t;return e=="UTC"||e=="Etc/UTC"?t=new Date(+i+i.getTimezoneOffset()*6e4):e==aw?t=i:(t=new Date(i.toLocaleString("en-US",{timeZone:e})),t.setMilliseconds(i.getMilliseconds())),t}const sm=i=>i%1==0,yl=[1,2,2.5,5],lw=io(10,-32,0,yl),rm=io(10,0,32,yl),cw=rm.filter(sm),Ws=lw.concat(rm),pu=`
`,am="{YYYY}",Lf=pu+am,om="{M}/{D}",$a=pu+om,el=$a+"/{YY}",lm="{aa}",hw="{h}:{mm}",Gr=hw+lm,Df=pu+Gr,If=":{ss}",Mt=null;function cm(i){let e=i*1e3,t=e*60,n=t*60,s=n*24,r=s*30,a=s*365,l=(i==1?io(10,0,3,yl).filter(sm):io(10,-3,0,yl)).concat([e,e*5,e*10,e*15,e*30,t,t*5,t*10,t*15,t*30,n,n*2,n*3,n*4,n*6,n*8,n*12,s,s*2,s*3,s*4,s*5,s*6,s*7,s*8,s*9,s*10,s*15,r,r*2,r*3,r*4,r*6,a,a*2,a*5,a*10,a*25,a*50,a*100]);const c=[[a,am,Mt,Mt,Mt,Mt,Mt,Mt,1],[s*28,"{MMM}",Lf,Mt,Mt,Mt,Mt,Mt,1],[s,om,Lf,Mt,Mt,Mt,Mt,Mt,1],[n,"{h}"+lm,el,Mt,$a,Mt,Mt,Mt,1],[t,Gr,el,Mt,$a,Mt,Mt,Mt,1],[e,If,el+" "+Gr,Mt,$a+" "+Gr,Mt,Df,Mt,1],[i,If+".{fff}",el+" "+Gr,Mt,$a+" "+Gr,Mt,Df,Mt,1]];function h(u){return(d,f,g,v,p,m)=>{let S=[],_=p>=a,b=p>=r&&p<a,I=u(g),A=Pt(I*i,3),R=Hc(I.getFullYear(),_?0:I.getMonth(),b||_?1:I.getDate()),N=Pt(R*i,3);if(b||_){let w=b?p/r:0,y=_?p/a:0,P=A==N?A:Pt(Hc(R.getFullYear()+y,R.getMonth()+w,1)*i,3),X=new Date(rn(P/i)),H=X.getFullYear(),J=X.getMonth();for(let q=0;P<=v;q++){let ee=Hc(H+y*q,J+w*q,1),j=ee-u(Pt(ee*i,3));P=Pt((+ee+j)*i,3),P<=v&&S.push(P)}}else{let w=p>=s?s:p,y=Jn(g)-Jn(A),P=N+y+Nl(A-N,w);S.push(P);let X=u(P),H=X.getHours()+X.getMinutes()/t+X.getSeconds()/n,J=p/n,q=d.axes[f]._space,ee=m/q;for(;P=Pt(P+p,i==1?0:3),!(P>v);)if(J>1){let j=Jn(Pt(H+J,6))%24,de=u(P).getHours()-j;de>1&&(de=-1),P-=de*n,H=(H+J)%24;let ye=S[S.length-1];Pt((P-ye)/p,3)*ee>=.7&&S.push(P)}else S.push(P)}return S}}return[l,c,h]}const[uw,dw,fw]=cm(1),[pw,mw,gw]=cm(.001);io(2,-53,53,[1]);function Uf(i,e){return i.map(t=>t.map((n,s)=>s==0||s==8||n==null?n:e(s==1||t[8]==0?n:t[1]+n)))}function Nf(i,e){return(t,n,s,r,a)=>{let o=e.find(g=>a>=g[0])||e[e.length-1],l,c,h,u,d,f;return n.map(g=>{let v=i(g),p=v.getFullYear(),m=v.getMonth(),S=v.getDate(),_=v.getHours(),b=v.getMinutes(),I=v.getSeconds(),A=p!=l&&o[2]||m!=c&&o[3]||S!=h&&o[4]||_!=u&&o[5]||b!=d&&o[6]||I!=f&&o[7]||o[1];return l=p,c=m,h=S,u=_,d=b,f=I,A(v)})}}function vw(i,e){let t=fu(e);return(n,s,r,a,o)=>s.map(l=>t(i(l)))}function Hc(i,e,t){return new Date(i,e,t)}function Of(i,e){return e(i)}const xw="{YYYY}-{MM}-{DD} {h}:{mm}{aa}";function Ff(i,e){return(t,n,s,r)=>r==null?ou:e(i(n))}function _w(i,e){let t=i.series[e];return t.width?t.stroke(i,e):t.points.width?t.points.stroke(i,e):null}function yw(i,e){return i.series[e].fill(i,e)}const Sw={show:!0,live:!0,isolate:!1,mount:zM,markers:{show:!0,width:2,stroke:_w,fill:yw,dash:"solid"},idx:null,idxs:null,values:[]};function bw(i,e){let t=i.cursor.points,n=ii(),s=t.size(i,e);kt(n,Ga,s),kt(n,Wa,s);let r=s/-2;kt(n,"marginLeft",r),kt(n,"marginTop",r);let a=t.width(i,e,s);return a&&kt(n,"borderWidth",a),n}function Mw(i,e){let t=i.series[e].points;return t._fill||t._stroke}function ww(i,e){let t=i.series[e].points;return t._stroke||t._fill}function Ew(i,e){return i.series[e].points.size}const Vc=[0,0];function Tw(i,e,t){return Vc[0]=e,Vc[1]=t,Vc}function tl(i,e,t,n=!0){return s=>{s.button==0&&(!n||s.target==e)&&t(s)}}function Gc(i,e,t,n=!0){return s=>{(!n||s.target==e)&&t(s)}}const Aw={show:!0,x:!0,y:!0,lock:!1,move:Tw,points:{one:!1,show:bw,size:Ew,width:0,stroke:ww,fill:Mw},bind:{mousedown:tl,mouseup:tl,click:tl,dblclick:tl,mousemove:Gc,mouseleave:Gc,mouseenter:Gc},drag:{setScale:!0,x:!0,y:!1,dist:0,uni:null,click:(i,e)=>{e.stopPropagation(),e.stopImmediatePropagation()},_x:!1,_y:!1},focus:{dist:(i,e,t,n,s)=>n-s,prox:-1,bias:0},hover:{skip:[void 0],prox:null,bias:0},left:-10,top:-10,idx:null,dataIdx:null,idxs:null,event:null},hm={show:!0,stroke:"rgba(0,0,0,0.07)",width:2},mu=nn({},hm,{filter:Kp}),um=nn({},mu,{size:10}),dm=nn({},hm,{show:!1}),gu='12px system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji"',fm="bold "+gu,pm=1.5,kf={show:!0,scale:"x",stroke:au,space:50,gap:5,alignTo:1,size:50,labelGap:0,labelSize:30,labelFont:fm,side:2,grid:mu,ticks:um,border:dm,font:gu,lineGap:pm,rotate:0},Cw="Value",Rw="Time",Bf={show:!0,scale:"x",auto:!1,sorted:1,min:Rt,max:-Rt,idxs:[]};function Pw(i,e,t,n,s){return e.map(r=>r==null?"":uu(r))}function Lw(i,e,t,n,s,r,a){let o=[],l=Ts.get(s)||0;t=a?t:Pt(Nl(t,s),l);for(let c=t;c<=n;c=Pt(c+s,l))o.push(Object.is(c,-0)?0:c);return o}function Fh(i,e,t,n,s,r,a){const o=[],l=i.scales[i.axes[e].scale].log,c=l==10?ns:Xp,h=Jn(c(t));s=ha(l,h),l==10&&(s=Ws[gi(s,Ws)]);let u=t,d=s*l;l==10&&(d=Ws[gi(d,Ws)]);do o.push(u),u=u+s,l==10&&!Ts.has(u)&&(u=Pt(u,Ts.get(s))),u>=d&&(s=u,d=s*l,l==10&&(d=Ws[gi(d,Ws)]));while(u<=n);return o}function Dw(i,e,t,n,s,r,a){let l=i.scales[i.axes[e].scale].asinh,c=n>l?Fh(i,e,kn(l,t),n,s):[l],h=n>=0&&t<=0?[0]:[];return(t<-l?Fh(i,e,kn(l,-n),-t,s):[l]).reverse().map(d=>-d).concat(h,c)}const mm=/./,Iw=/[12357]/,Uw=/[125]/,zf=/1/,kh=(i,e,t,n)=>i.map((s,r)=>e==4&&s==0||r%n==0&&t.test(s.toExponential()[s<0?1:0])?s:null);function Nw(i,e,t,n,s){let r=i.axes[t],a=r.scale,o=i.scales[a],l=i.valToPos,c=r._space,h=l(10,a),u=l(9,a)-h>=c?mm:l(7,a)-h>=c?Iw:l(5,a)-h>=c?Uw:zf;if(u==zf){let d=an(l(1,a)-h);if(d<c)return kh(e.slice().reverse(),o.distr,u,si(c/d)).reverse()}return kh(e,o.distr,u,1)}function Ow(i,e,t,n,s){let r=i.axes[t],a=r.scale,o=r._space,l=i.valToPos,c=an(l(1,a)-l(2,a));return c<o?kh(e.slice().reverse(),3,mm,si(o/c)).reverse():e}function Fw(i,e,t,n){return n==null?ou:e==null?"":uu(e)}const Hf={show:!0,scale:"y",stroke:au,space:30,gap:5,alignTo:1,size:50,labelGap:0,labelSize:30,labelFont:fm,side:3,grid:mu,ticks:um,border:dm,font:gu,lineGap:pm,rotate:0};function kw(i,e){let t=3+(i||1)*2;return Pt(t*e,3)}function Bw(i,e){let{scale:t,idxs:n}=i.series[0],s=i._data[0],r=i.valToPos(s[n[0]],t,!0),a=i.valToPos(s[n[1]],t,!0),o=an(a-r),l=i.series[e],c=o/(l.points.space*bt);return n[1]-n[0]<=c}const Vf={scale:null,auto:!0,sorted:0,min:Rt,max:-Rt},gm=(i,e,t,n,s)=>s,Gf={show:!0,auto:!0,sorted:0,gaps:gm,alpha:1,facets:[nn({},Vf,{scale:"x"}),nn({},Vf,{scale:"y"})]},Wf={scale:"y",auto:!0,sorted:0,show:!0,spanGaps:!1,gaps:gm,alpha:1,points:{show:Bw,filter:null},values:null,min:Rt,max:-Rt,idxs:[],path:null,clip:null};function zw(i,e,t,n,s){return t/10}const vm={time:uM,auto:!0,distr:1,log:10,asinh:1,min:null,max:null,dir:1,ori:0},Hw=nn({},vm,{time:!1,ori:1}),$f={};function xm(i,e){let t=$f[i];return t||(t={key:i,plots:[],sub(n){t.plots.push(n)},unsub(n){t.plots=t.plots.filter(s=>s!=n)},pub(n,s,r,a,o,l,c){for(let h=0;h<t.plots.length;h++)t.plots[h]!=s&&t.plots[h].pub(n,s,r,a,o,l,c)}},i!=null&&($f[i]=t)),t}const fa=1,Bh=2;function rr(i,e,t){const n=i.mode,s=i.series[e],r=n==2?i._data[e]:i._data,a=i.scales,o=i.bbox;let l=r[0],c=n==2?r[1]:r[e],h=n==2?a[s.facets[0].scale]:a[i.series[0].scale],u=n==2?a[s.facets[1].scale]:a[s.scale],d=o.left,f=o.top,g=o.width,v=o.height,p=i.valToPosH,m=i.valToPosV;return h.ori==0?t(s,l,c,h,u,p,m,d,f,g,v,kl,xa,zl,ym,bm):t(s,l,c,h,u,m,p,f,d,v,g,Bl,_a,_u,Sm,Mm)}function vu(i,e){let t=0,n=0,s=yt(i.bands,du);for(let r=0;r<s.length;r++){let a=s[r];a.series[0]==e?t=a.dir:a.series[1]==e&&(a.dir==1?n|=1:n|=2)}return[t,n==1?-1:n==2?1:n==3?2:0]}function Vw(i,e,t,n,s){let r=i.mode,a=i.series[e],o=r==2?a.facets[1].scale:a.scale,l=i.scales[o];return s==-1?l.min:s==1?l.max:l.distr==3?l.dir==1?l.min:l.max:0}function is(i,e,t,n,s,r){return rr(i,e,(a,o,l,c,h,u,d,f,g,v,p)=>{let m=a.pxRound;const S=c.dir*(c.ori==0?1:-1),_=c.ori==0?xa:_a;let b,I;S==1?(b=t,I=n):(b=n,I=t);let A=m(u(o[b],c,v,f)),R=m(d(l[b],h,p,g)),N=m(u(o[I],c,v,f)),w=m(d(r==1?h.max:h.min,h,p,g)),y=new Path2D(s);return _(y,N,w),_(y,A,w),_(y,A,R),y})}function Fl(i,e,t,n,s,r){let a=null;if(i.length>0){a=new Path2D;const o=e==0?zl:_u;let l=t;for(let u=0;u<i.length;u++){let d=i[u];if(d[1]>d[0]){let f=d[0]-l;f>0&&o(a,l,n,f,n+r),l=d[1]}}let c=t+s-l,h=10;c>0&&o(a,l,n-h/2,c,n+r+h)}return a}function Gw(i,e,t){let n=i[i.length-1];n&&n[0]==e?n[1]=t:i.push([e,t])}function xu(i,e,t,n,s,r,a){let o=[],l=i.length;for(let c=s==1?t:n;c>=t&&c<=n;c+=s)if(e[c]===null){let u=c,d=c;if(s==1)for(;++c<=n&&e[c]===null;)d=c;else for(;--c>=t&&e[c]===null;)d=c;let f=r(i[u]),g=d==u?f:r(i[d]),v=u-s;f=a<=0&&v>=0&&v<l?r(i[v]):f;let m=d+s;g=a>=0&&m>=0&&m<l?r(i[m]):g,g>=f&&o.push([f,g])}return o}function qf(i){return i==0?jp:i==1?rn:e=>Gs(e,i)}function _m(i){let e=i==0?kl:Bl,t=i==0?(s,r,a,o,l,c)=>{s.arcTo(r,a,o,l,c)}:(s,r,a,o,l,c)=>{s.arcTo(a,r,l,o,c)},n=i==0?(s,r,a,o,l)=>{s.rect(r,a,o,l)}:(s,r,a,o,l)=>{s.rect(a,r,l,o)};return(s,r,a,o,l,c=0,h=0)=>{c==0&&h==0?n(s,r,a,o,l):(c=_i(c,o/2,l/2),h=_i(h,o/2,l/2),e(s,r+c,a),t(s,r+o,a,r+o,a+l,c),t(s,r+o,a+l,r,a+l,h),t(s,r,a+l,r,a,h),t(s,r,a,r+o,a,c),s.closePath())}}const kl=(i,e,t)=>{i.moveTo(e,t)},Bl=(i,e,t)=>{i.moveTo(t,e)},xa=(i,e,t)=>{i.lineTo(e,t)},_a=(i,e,t)=>{i.lineTo(t,e)},zl=_m(0),_u=_m(1),ym=(i,e,t,n,s,r)=>{i.arc(e,t,n,s,r)},Sm=(i,e,t,n,s,r)=>{i.arc(t,e,n,s,r)},bm=(i,e,t,n,s,r,a)=>{i.bezierCurveTo(e,t,n,s,r,a)},Mm=(i,e,t,n,s,r,a)=>{i.bezierCurveTo(t,e,s,n,a,r)};function wm(i){return(e,t,n,s,r)=>rr(e,t,(a,o,l,c,h,u,d,f,g,v,p)=>{let{pxRound:m,points:S}=a,_,b;c.ori==0?(_=kl,b=ym):(_=Bl,b=Sm);const I=Pt(S.width*bt,3);let A=(S.size-S.width)/2*bt,R=Pt(A*2,3),N=new Path2D,w=new Path2D,{left:y,top:P,width:X,height:H}=e.bbox;zl(w,y-R,P-R,X+R*2,H+R*2);const J=q=>{if(l[q]!=null){let ee=m(u(o[q],c,v,f)),j=m(d(l[q],h,p,g));_(N,ee+A,j),b(N,ee,j,A,0,ll*2)}};if(r)r.forEach(J);else for(let q=n;q<=s;q++)J(q);return{stroke:I>0?N:null,fill:N,clip:w,flags:fa|Bh}})}function Em(i){return(e,t,n,s,r,a)=>{n!=s&&(r!=n&&a!=n&&i(e,t,n),r!=s&&a!=s&&i(e,t,s),i(e,t,a))}}const Ww=Em(xa),$w=Em(_a);function Tm(i){const e=yt(i==null?void 0:i.alignGaps,0);return(t,n,s,r)=>rr(t,n,(a,o,l,c,h,u,d,f,g,v,p)=>{[s,r]=Il(l,s,r);let m=a.pxRound,S=H=>m(u(H,c,v,f)),_=H=>m(d(H,h,p,g)),b,I;c.ori==0?(b=xa,I=Ww):(b=_a,I=$w);const A=c.dir*(c.ori==0?1:-1),R={stroke:new Path2D,fill:null,clip:null,band:null,gaps:null,flags:fa},N=R.stroke;let w=!1;if(r-s>=v*4){let H=Se=>t.posToVal(Se,c.key,!0),J=null,q=null,ee,j,ne,ge=S(o[A==1?s:r]),de=S(o[s]),ye=S(o[r]),Te=H(A==1?de+1:ye-1);for(let Se=A==1?s:r;Se>=s&&Se<=r;Se+=A){let ie=o[Se],be=(A==1?ie<Te:ie>Te)?ge:S(ie),fe=l[Se];be==ge?fe!=null?(j=fe,J==null?(b(N,be,_(j)),ee=J=q=j):j<J?J=j:j>q&&(q=j)):fe===null&&(w=!0):(J!=null&&I(N,ge,_(J),_(q),_(ee),_(j)),fe!=null?(j=fe,b(N,be,_(j)),J=q=ee=j):(J=q=null,fe===null&&(w=!0)),ge=be,Te=H(ge+A))}J!=null&&J!=q&&ne!=ge&&I(N,ge,_(J),_(q),_(ee),_(j))}else for(let H=A==1?s:r;H>=s&&H<=r;H+=A){let J=l[H];J===null?w=!0:J!=null&&b(N,S(o[H]),_(J))}let[P,X]=vu(t,n);if(a.fill!=null||P!=0){let H=R.fill=new Path2D(N),J=a.fillTo(t,n,a.min,a.max,P),q=_(J),ee=S(o[s]),j=S(o[r]);A==-1&&([j,ee]=[ee,j]),b(H,j,q),b(H,ee,q)}if(!a.spanGaps){let H=[];w&&H.push(...xu(o,l,s,r,A,S,e)),R.gaps=H=a.gaps(t,n,s,r,H),R.clip=Fl(H,c.ori,f,g,v,p)}return X!=0&&(R.band=X==2?[is(t,n,s,r,N,-1),is(t,n,s,r,N,1)]:is(t,n,s,r,N,X)),R})}function qw(i){const e=yt(i.align,1),t=yt(i.ascDesc,!1),n=yt(i.alignGaps,0),s=yt(i.extend,!1);return(r,a,o,l)=>rr(r,a,(c,h,u,d,f,g,v,p,m,S,_)=>{[o,l]=Il(u,o,l);let b=c.pxRound,{left:I,width:A}=r.bbox,R=de=>b(g(de,d,S,p)),N=de=>b(v(de,f,_,m)),w=d.ori==0?xa:_a;const y={stroke:new Path2D,fill:null,clip:null,band:null,gaps:null,flags:fa},P=y.stroke,X=d.dir*(d.ori==0?1:-1);let H=N(u[X==1?o:l]),J=R(h[X==1?o:l]),q=J,ee=J;s&&e==-1&&(ee=I,w(P,ee,H)),w(P,J,H);for(let de=X==1?o:l;de>=o&&de<=l;de+=X){let ye=u[de];if(ye==null)continue;let Te=R(h[de]),Se=N(ye);e==1?w(P,Te,H):w(P,q,Se),w(P,Te,Se),H=Se,q=Te}let j=q;s&&e==1&&(j=I+A,w(P,j,H));let[ne,ge]=vu(r,a);if(c.fill!=null||ne!=0){let de=y.fill=new Path2D(P),ye=c.fillTo(r,a,c.min,c.max,ne),Te=N(ye);w(de,j,Te),w(de,ee,Te)}if(!c.spanGaps){let de=[];de.push(...xu(h,u,o,l,X,R,n));let ye=c.width*bt/2,Te=t||e==1?ye:-ye,Se=t||e==-1?-ye:ye;de.forEach(ie=>{ie[0]+=Te,ie[1]+=Se}),y.gaps=de=c.gaps(r,a,o,l,de),y.clip=Fl(de,d.ori,p,m,S,_)}return ge!=0&&(y.band=ge==2?[is(r,a,o,l,P,-1),is(r,a,o,l,P,1)]:is(r,a,o,l,P,ge)),y})}function Xf(i,e,t,n,s,r,a=Rt){if(i.length>1){let o=null;for(let l=0,c=1/0;l<i.length;l++)if(e[l]!==void 0){if(o!=null){let h=an(i[l]-i[o]);h<c&&(c=h,a=an(t(i[l],n,s,r)-t(i[o],n,s,r)))}o=l}}return a}function Xw(i){i=i||Ka;const e=yt(i.size,[.6,Rt,1]),t=i.align||0,n=i.gap||0;let s=i.radius;s=s==null?[0,0]:typeof s=="number"?[s,0]:s;const r=pt(s),a=1-e[0],o=yt(e[1],Rt),l=yt(e[2],1),c=yt(i.disp,Ka),h=yt(i.each,f=>{}),{fill:u,stroke:d}=c;return(f,g,v,p)=>rr(f,g,(m,S,_,b,I,A,R,N,w,y,P)=>{let X=m.pxRound,H=t,J=n*bt,q=o*bt,ee=l*bt,j,ne;b.ori==0?[j,ne]=r(f,g):[ne,j]=r(f,g);const ge=b.dir*(b.ori==0?1:-1);let de=b.ori==0?zl:_u,ye=b.ori==0?h:($,Ee,ve,Ce,Ze,me,Ae)=>{h($,Ee,ve,Ze,Ce,Ae,me)},Te=yt(f.bands,du).find($=>$.series[0]==g),Se=Te!=null?Te.dir:0,ie=m.fillTo(f,g,m.min,m.max,Se),he=X(R(ie,I,P,w)),be,fe,ze,We=y,Fe=X(m.width*bt),mt=!1,F=null,ft=null,rt=null,ht=null;u!=null&&(Fe==0||d!=null)&&(mt=!0,F=u.values(f,g,v,p),ft=new Map,new Set(F).forEach($=>{$!=null&&ft.set($,new Path2D)}),Fe>0&&(rt=d.values(f,g,v,p),ht=new Map,new Set(rt).forEach($=>{$!=null&&ht.set($,new Path2D)})));let{x0:ke,size:Et}=c;if(ke!=null&&Et!=null){H=1,S=ke.values(f,g,v,p),ke.unit==2&&(S=S.map(ve=>f.posToVal(N+ve*y,b.key,!0)));let $=Et.values(f,g,v,p);Et.unit==2?fe=$[0]*y:fe=A($[0],b,y,N)-A(0,b,y,N),We=Xf(S,_,A,b,y,N,We),ze=We-fe+J}else We=Xf(S,_,A,b,y,N,We),ze=We*a+J,fe=We-ze;ze<1&&(ze=0),Fe>=fe/2&&(Fe=0),ze<5&&(X=jp);let Ye=ze>0,qe=We-ze-(Ye?Fe:0);fe=X(Oh(qe,ee,q)),be=(H==0?fe/2:H==ge?0:fe)-H*ge*((H==0?J/2:0)+(Ye?Fe/2:0));const U={stroke:null,fill:null,clip:null,band:null,gaps:null,flags:0},T=mt?null:new Path2D;let Q=null;if(Te!=null)Q=f.data[Te.series[1]];else{let{y0:$,y1:Ee}=c;$!=null&&Ee!=null&&(_=Ee.values(f,g,v,p),Q=$.values(f,g,v,p))}let le=j*fe,te=ne*fe;for(let $=ge==1?v:p;$>=v&&$<=p;$+=ge){let Ee=_[$];if(Ee==null)continue;if(Q!=null){let we=Q[$]??0;if(Ee-we==0)continue;he=R(we,I,P,w)}let ve=b.distr!=2||c!=null?S[$]:$,Ce=A(ve,b,y,N),Ze=R(yt(Ee,ie),I,P,w),me=X(Ce-be),Ae=X(kn(Ze,he)),Qe=X(_i(Ze,he)),He=Ae-Qe;if(Ee!=null){let we=Ee<0?te:le,Ve=Ee<0?le:te;mt?(Fe>0&&rt[$]!=null&&de(ht.get(rt[$]),me,Qe+Jn(Fe/2),fe,kn(0,He-Fe),we,Ve),F[$]!=null&&de(ft.get(F[$]),me,Qe+Jn(Fe/2),fe,kn(0,He-Fe),we,Ve)):de(T,me,Qe+Jn(Fe/2),fe,kn(0,He-Fe),we,Ve),ye(f,g,$,me-Fe/2,Qe,fe+Fe,He)}}return Fe>0?U.stroke=mt?ht:T:mt||(U._fill=m.width==0?m._fill:m._stroke??m._fill,U.width=0),U.fill=mt?ft:T,U})}function Yw(i,e){const t=yt(e==null?void 0:e.alignGaps,0);return(n,s,r,a)=>rr(n,s,(o,l,c,h,u,d,f,g,v,p,m)=>{[r,a]=Il(c,r,a);let S=o.pxRound,_=j=>S(d(j,h,p,g)),b=j=>S(f(j,u,m,v)),I,A,R;h.ori==0?(I=kl,R=xa,A=bm):(I=Bl,R=_a,A=Mm);const N=h.dir*(h.ori==0?1:-1);let w=_(l[N==1?r:a]),y=w,P=[],X=[];for(let j=N==1?r:a;j>=r&&j<=a;j+=N)if(c[j]!=null){let ge=l[j],de=_(ge);P.push(y=de),X.push(b(c[j]))}const H={stroke:i(P,X,I,R,A,S),fill:null,clip:null,band:null,gaps:null,flags:fa},J=H.stroke;let[q,ee]=vu(n,s);if(o.fill!=null||q!=0){let j=H.fill=new Path2D(J),ne=o.fillTo(n,s,o.min,o.max,q),ge=b(ne);R(j,y,ge),R(j,w,ge)}if(!o.spanGaps){let j=[];j.push(...xu(l,c,r,a,N,_,t)),H.gaps=j=o.gaps(n,s,r,a,j),H.clip=Fl(j,h.ori,g,v,p,m)}return ee!=0&&(H.band=ee==2?[is(n,s,r,a,J,-1),is(n,s,r,a,J,1)]:is(n,s,r,a,J,ee)),H})}function jw(i){return Yw(Kw,i)}function Kw(i,e,t,n,s,r){const a=i.length;if(a<2)return null;const o=new Path2D;if(t(o,i[0],e[0]),a==2)n(o,i[1],e[1]);else{let l=Array(a),c=Array(a-1),h=Array(a-1),u=Array(a-1);for(let d=0;d<a-1;d++)h[d]=e[d+1]-e[d],u[d]=i[d+1]-i[d],c[d]=h[d]/u[d];l[0]=c[0];for(let d=1;d<a-1;d++)c[d]===0||c[d-1]===0||c[d-1]>0!=c[d]>0?l[d]=0:(l[d]=3*(u[d-1]+u[d])/((2*u[d]+u[d-1])/c[d-1]+(u[d]+2*u[d-1])/c[d]),isFinite(l[d])||(l[d]=0));l[a-1]=c[a-2];for(let d=0;d<a-1;d++)s(o,i[d]+u[d]/3,e[d]+l[d]*u[d]/3,i[d+1]-u[d]/3,e[d+1]-l[d+1]*u[d]/3,i[d+1],e[d+1])}return o}const zh=new Set;function Yf(){for(let i of zh)i.syncRect(!0)}va&&(Js(PM,Zr,Yf),Js(LM,Zr,Yf,!0),Js(xl,Zr,()=>{xn.pxRatio=bt}));const Jw=Tm(),Zw=wm();function jf(i,e,t,n){return(n?[i[0],i[1]].concat(i.slice(2)):[i[0]].concat(i.slice(1))).map((r,a)=>Hh(r,a,e,t))}function Qw(i,e){return i.map((t,n)=>n==0?{}:nn({},e,t))}function Hh(i,e,t,n){return nn({},e==0?t:n,i)}function Am(i,e,t){return e==null?ua:[e,t]}const eE=Am;function tE(i,e,t){return e==null?ua:_l(e,t,hu,!0)}function Cm(i,e,t,n){return e==null?ua:Ul(e,t,i.scales[n].log,!1)}const nE=Cm;function Rm(i,e,t,n){return e==null?ua:cu(e,t,i.scales[n].log,!1)}const iE=Rm;function sE(i,e,t,n,s){let r=kn(Af(i),Af(e)),a=e-i,o=gi(s/n*a,t);do{let l=t[o],c=n*l/a;if(c>=s&&r+(l<5?Ts.get(l):0)<=17)return[l,c]}while(++o<t.length);return[0,0]}function Kf(i){let e,t;return i=i.replace(/(\d+)px/,(n,s)=>(e=rn((t=+s)*bt))+"px"),[i,e,t]}function rE(i){i.show&&[i.font,i.labelFont].forEach(e=>{let t=Pt(e[2]*bt,1);e[0]=e[0].replace(/[0-9.]+px/,t+"px"),e[1]=t})}function xn(i,e,t){const n={mode:yt(i.mode,1)},s=n.mode;function r(x,E,L,D){let z=E.valToPct(x);return D+L*(E.dir==-1?1-z:z)}function a(x,E,L,D){let z=E.valToPct(x);return D+L*(E.dir==-1?z:1-z)}function o(x,E,L,D){return E.ori==0?r(x,E,L,D):a(x,E,L,D)}n.valToPosH=r,n.valToPosV=a;let l=!1;n.status=0;const c=n.root=ii(dM);if(i.id!=null&&(c.id=i.id),jn(c,i.class),i.title){let x=ii(mM,c);x.textContent=i.title}const h=mi("canvas"),u=n.ctx=h.getContext("2d"),d=ii(gM,c);Js("click",d,x=>{x.target===g&&(Nt!=ur||Gt!=dr)&&bn.click(n,x)},!0);const f=n.under=ii(vM,d);d.appendChild(h);const g=n.over=ii(xM,d);i=da(i);const v=+yt(i.pxAlign,1),p=qf(v);(i.plugins||[]).forEach(x=>{x.opts&&(i=x.opts(n,i)||i)});const m=i.ms||.001,S=n.series=s==1?jf(i.series||[],Bf,Wf,!1):Qw(i.series||[null],Gf),_=n.axes=jf(i.axes||[],kf,Hf,!0),b=n.scales={},I=n.bands=i.bands||[];I.forEach(x=>{x.fill=pt(x.fill||null),x.dir=yt(x.dir,-1)});const A=s==2?S[1].facets[0].scale:S[0].scale,R={axes:Hm,series:zn},N=(i.drawOrder||["axes","series"]).map(x=>R[x]);function w(x){const E=x.distr==3?L=>ns(L>0?L:x.clamp(n,L,x.min,x.max,x.key)):x.distr==4?L=>zc(L,x.asinh):x.distr==100?L=>x.fwd(L):L=>L;return L=>{let D=E(L),{_min:z,_max:K}=x,oe=K-z;return(D-z)/oe}}function y(x){let E=b[x];if(E==null){let L=(i.scales||Ka)[x]||Ka;if(L.from!=null){y(L.from);let D=nn({},b[L.from],L,{key:x});D.valToPct=w(D),b[x]=D}else{E=b[x]=nn({},x==A?vm:Hw,L),E.key=x;let D=E.time,z=E.range,K=xs(z);if((x!=A||s==2&&!D)&&(K&&(z[0]==null||z[1]==null)&&(z={min:z[0]==null?wf:{mode:1,hard:z[0],soft:z[0]},max:z[1]==null?wf:{mode:1,hard:z[1],soft:z[1]}},K=!1),!K&&Ol(z))){let oe=z;z=(pe,Me,De)=>Me==null?ua:_l(Me,De,oe)}E.range=pt(z||(D?eE:x==A?E.distr==3?nE:E.distr==4?iE:Am:E.distr==3?Cm:E.distr==4?Rm:tE)),E.auto=pt(K?!1:E.auto),E.clamp=pt(E.clamp||zw),E._min=E._max=null,E.valToPct=w(E)}}}y("x"),y("y"),s==1&&S.forEach(x=>{y(x.scale)}),_.forEach(x=>{y(x.scale)});for(let x in i.scales)y(x);const P=b[A],X=P.distr;let H,J;P.ori==0?(jn(c,fM),H=r,J=a):(jn(c,pM),H=a,J=r);const q={};for(let x in b){let E=b[x];(E.min!=null||E.max!=null)&&(q[x]={min:E.min,max:E.max},E.min=E.max=null)}const ee=i.tzDate||(x=>new Date(rn(x/m))),j=i.fmtDate||fu,ne=m==1?fw(ee):gw(ee),ge=Nf(ee,Uf(m==1?dw:mw,j)),de=Ff(ee,Of(xw,j)),ye=[],Te=n.legend=nn({},Sw,i.legend),Se=n.cursor=nn({},Aw,{drag:{y:s==2}},i.cursor),ie=Te.show,he=Se.show,be=Te.markers;Te.idxs=ye,be.width=pt(be.width),be.dash=pt(be.dash),be.stroke=pt(be.stroke),be.fill=pt(be.fill);let fe,ze,We,Fe=[],mt=[],F,ft=!1,rt={};if(Te.live){const x=S[1]?S[1].values:null;ft=x!=null,F=ft?x(n,1,0):{_:0};for(let E in F)rt[E]=ou}if(ie)if(fe=mi("table",wM,c),We=mi("tbody",null,fe),Te.mount(n,fe),ft){ze=mi("thead",null,fe,We);let x=mi("tr",null,ze);mi("th",null,x);for(var ht in F)mi("th",uf,x).textContent=ht}else jn(fe,TM),Te.live&&jn(fe,EM);const ke={show:!0},Et={show:!1};function Ye(x,E){if(E==0&&(ft||!Te.live||s==2))return ua;let L=[],D=mi("tr",AM,We,We.childNodes[E]);jn(D,x.class),x.show||jn(D,Xs);let z=mi("th",null,D);if(be.show){let pe=ii(CM,z);if(E>0){let Me=be.width(n,E);Me&&(pe.style.border=Me+"px "+be.dash(n,E)+" "+be.stroke(n,E)),pe.style.background=be.fill(n,E)}}let K=ii(uf,z);x.label instanceof HTMLElement?K.appendChild(x.label):K.textContent=x.label,E>0&&(be.show||(K.style.color=x.width>0?be.stroke(n,E):be.fill(n,E)),U("click",z,pe=>{if(Se._lock)return;Ht(pe);let Me=S.indexOf(x);if((pe.ctrlKey||pe.metaKey)!=Te.isolate){let De=S.some((Ie,Oe)=>Oe>0&&Oe!=Me&&Ie.show);S.forEach((Ie,Oe)=>{Oe>0&&Ri(Oe,De?Oe==Me?ke:Et:ke,!0,en.setSeries)})}else Ri(Me,{show:!x.show},!0,en.setSeries)},!1),Ai&&U(mf,z,pe=>{Se._lock||(Ht(pe),Ri(S.indexOf(x),pr,!0,en.setSeries))},!1));for(var oe in F){let pe=mi("td",RM,D);pe.textContent="--",L.push(pe)}return[D,L]}const qe=new Map;function U(x,E,L,D=!0){const z=qe.get(E)||{},K=Se.bind[x](n,E,L,D);K&&(Js(x,E,z[x]=K),qe.set(E,z))}function T(x,E,L){const D=qe.get(E)||{};for(let z in D)(x==null||z==x)&&(Nh(z,E,D[z]),delete D[z]);x==null&&qe.delete(E)}let Q=0,le=0,te=0,$=0,Ee=0,ve=0,Ce=Ee,Ze=ve,me=te,Ae=$,Qe=0,He=0,we=0,Ve=0;n.bbox={};let B=!1,ce=!1,O=!1,ae=!1,se=!1,re=!1;function _e(x,E,L){(L||x!=n.width||E!=n.height)&&Je(x,E),or(!1),O=!0,ce=!0,lr()}function Je(x,E){n.width=Q=te=x,n.height=le=$=E,Ee=ve=0,ct(),yn();let L=n.bbox;Qe=L.left=Gs(Ee*bt,.5),He=L.top=Gs(ve*bt,.5),we=L.width=Gs(te*bt,.5),Ve=L.height=Gs($*bt,.5)}const lt=3;function xt(){let x=!1,E=0;for(;!x;){E++;let L=Bm(E),D=zm(E);x=E==lt||L&&D,x||(Je(n.width,n.height),ce=!0)}}function Tt({width:x,height:E}){_e(x,E)}n.setSize=Tt;function ct(){let x=!1,E=!1,L=!1,D=!1;_.forEach((z,K)=>{if(z.show&&z._show){let{side:oe,_size:pe}=z,Me=oe%2,De=z.label!=null?z.labelSize:0,Ie=pe+De;Ie>0&&(Me?(te-=Ie,oe==3?(Ee+=Ie,D=!0):L=!0):($-=Ie,oe==0?(ve+=Ie,x=!0):E=!0))}}),Hi[0]=x,Hi[1]=L,Hi[2]=E,Hi[3]=D,te-=Z[1]+Z[3],Ee+=Z[3],$-=Z[2]+Z[0],ve+=Z[0]}function yn(){let x=Ee+te,E=ve+$,L=Ee,D=ve;function z(K,oe){switch(K){case 1:return x+=oe,x-oe;case 2:return E+=oe,E-oe;case 3:return L-=oe,L+oe;case 0:return D-=oe,D+oe}}_.forEach((K,oe)=>{if(K.show&&K._show){let pe=K.side;K._pos=z(pe,K._size),K.label!=null&&(K._lpos=z(pe,K.labelSize))}})}if(Se.dataIdx==null){let x=Se.hover,E=x.skip=new Set(x.skip??[]);E.add(void 0);let L=x.prox=pt(x.prox),D=x.bias??(x.bias=0);Se.dataIdx=(z,K,oe,pe)=>{if(K==0)return oe;let Me=oe,De=L(z,K,oe,pe)??Rt,Ie=De>=0&&De<Rt,Oe=P.ori==0?te:$,st=Se.left,St=e[0],_t=e[K];if(E.has(_t[oe])){Me=null;let dt=null,nt=null,$e;if(D==0||D==-1)for($e=oe;dt==null&&$e-- >0;)E.has(_t[$e])||(dt=$e);if(D==0||D==1)for($e=oe;nt==null&&$e++<_t.length;)E.has(_t[$e])||(nt=$e);if(dt!=null||nt!=null)if(Ie){let Ft=dt==null?-1/0:H(St[dt],P,Oe,0),Xt=nt==null?1/0:H(St[nt],P,Oe,0),mn=st-Ft,Ct=Xt-st;mn<=Ct?mn<=De&&(Me=dt):Ct<=De&&(Me=nt)}else Me=nt==null?dt:dt==null?nt:oe-dt<=nt-oe?dt:nt}else Ie&&an(st-H(St[oe],P,Oe,0))>De&&(Me=null);return Me}}const Ht=x=>{Se.event=x};Se.idxs=ye,Se._lock=!1;let Vt=Se.points;Vt.show=pt(Vt.show),Vt.size=pt(Vt.size),Vt.stroke=pt(Vt.stroke),Vt.width=pt(Vt.width),Vt.fill=pt(Vt.fill);const un=n.focus=nn({},i.focus||{alpha:.3},Se.focus),Ai=un.prox>=0,Bi=Ai&&Vt.one;let Ln=[],ci=[],zi=[];function Ls(x,E){let L=Vt.show(n,E);if(L instanceof HTMLElement)return jn(L,MM),jn(L,x.class),Ii(L,-10,-10,te,$),g.insertBefore(L,Ln[E]),L}function Sa(x,E){if(s==1||E>0){let L=s==1&&b[x.scale].time,D=x.value;x.value=L?Pf(D)?Ff(ee,Of(D,j)):D||de:D||Fw,x.label=x.label||(L?Rw:Cw)}if(Bi||E>0){x.width=x.width==null?1:x.width,x.paths=x.paths||Jw||HM,x.fillTo=pt(x.fillTo||Vw),x.pxAlign=+yt(x.pxAlign,v),x.pxRound=qf(x.pxAlign),x.stroke=pt(x.stroke||null),x.fill=pt(x.fill||null),x._stroke=x._fill=x._paths=x._focus=null;let L=kw(kn(1,x.width),1),D=x.points=nn({},{size:L,width:kn(1,L*.2),stroke:x.stroke,space:L*2,paths:Zw,_stroke:null,_fill:null},x.points);D.show=pt(D.show),D.filter=pt(D.filter),D.fill=pt(D.fill),D.stroke=pt(D.stroke),D.paths=pt(D.paths),D.pxAlign=x.pxAlign}if(ie){let L=Ye(x,E);Fe.splice(E,0,L[0]),mt.splice(E,0,L[1]),Te.values.push(null)}if(he){ye.splice(E,0,null);let L=null;Bi?E==0&&(L=Ls(x,E)):E>0&&(L=Ls(x,E)),Ln.splice(E,0,L),ci.splice(E,0,0),zi.splice(E,0,0)}pn("addSeries",E)}function ho(x,E){E=E??S.length,x=s==1?Hh(x,E,Bf,Wf):Hh(x,E,{},Gf),S.splice(E,0,x),Sa(S[E],E)}n.addSeries=ho;function Hl(x){if(S.splice(x,1),ie){Te.values.splice(x,1),mt.splice(x,1);let E=Fe.splice(x,1)[0];T(null,E.firstChild),E.remove()}he&&(ye.splice(x,1),Ln.splice(x,1)[0].remove(),ci.splice(x,1),zi.splice(x,1)),pn("delSeries",x)}n.delSeries=Hl;const Hi=[!1,!1,!1,!1];function Vl(x,E){if(x._show=x.show,x.show){let L=x.side%2,D=b[x.scale];D==null&&(x.scale=L?S[1].scale:A,D=b[x.scale]);let z=D.time;x.size=pt(x.size),x.space=pt(x.space),x.rotate=pt(x.rotate),xs(x.incrs)&&x.incrs.forEach(oe=>{!Ts.has(oe)&&Ts.set(oe,Zp(oe))}),x.incrs=pt(x.incrs||(D.distr==2?cw:z?m==1?uw:pw:Ws)),x.splits=pt(x.splits||(z&&D.distr==1?ne:D.distr==3?Fh:D.distr==4?Dw:Lw)),x.stroke=pt(x.stroke),x.grid.stroke=pt(x.grid.stroke),x.ticks.stroke=pt(x.ticks.stroke),x.border.stroke=pt(x.border.stroke);let K=x.values;x.values=xs(K)&&!xs(K[0])?pt(K):z?xs(K)?Nf(ee,Uf(K,j)):Pf(K)?vw(ee,K):K||ge:K||Pw,x.filter=pt(x.filter||(D.distr>=3&&D.log==10?Nw:D.distr==3&&D.log==2?Ow:Kp)),x.font=Kf(x.font),x.labelFont=Kf(x.labelFont),x._size=x.size(n,null,E,0),x._space=x._rotate=x._incrs=x._found=x._splits=x._values=null,x._size>0&&(Hi[E]=!0,x._el=ii(_M,d))}}function C(x,E,L,D){let[z,K,oe,pe]=L,Me=E%2,De=0;return Me==0&&(pe||K)&&(De=E==0&&!z||E==2&&!oe?rn(kf.size/3):0),Me==1&&(z||oe)&&(De=E==1&&!K||E==3&&!pe?rn(Hf.size/2):0),De}const W=n.padding=(i.padding||[C,C,C,C]).map(x=>pt(yt(x,C))),Z=n._padding=W.map((x,E)=>x(n,E,Hi,0));let Y,G=null,ue=null;const Pe=s==1?S[0].idxs:null;let Le=null,Ne=!1;function et(x,E){if(e=x??[],n.data=n._data=e,s==2){Y=0;for(let L=1;L<S.length;L++)Y+=e[L][0].length}else{e.length==0&&(n.data=n._data=e=[[]]),Le=e[0],Y=Le.length;let L=e;if(X==2){L=e.slice();let D=L[0]=Array(Y);for(let z=0;z<Y;z++)D[z]=z}n._data=e=L}if(or(!0),pn("setData"),X==2&&(O=!0),E!==!1){let L=P;L.auto(n,Ne)?tt():ls(A,L.min,L.max),ae=ae||Se.left>=0,re=!0,lr()}}n.setData=et;function tt(){Ne=!0;let x,E;s==1&&(Y>0?(G=Pe[0]=0,ue=Pe[1]=Y-1,x=e[0][G],E=e[0][ue],X==2?(x=G,E=ue):x==E&&(X==3?[x,E]=Ul(x,x,P.log,!1):X==4?[x,E]=cu(x,x,P.log,!1):P.time?E=x+rn(86400/m):[x,E]=_l(x,E,hu,!0))):(G=Pe[0]=x=null,ue=Pe[1]=E=null)),ls(A,x,E)}let Be,ut,Lt,Dt,Sn,gt,Ge,Kt,vt,It;function Vi(x,E,L,D,z,K){x??(x=ff),L??(L=du),D??(D="butt"),z??(z=ff),K??(K="round"),x!=Be&&(u.strokeStyle=Be=x),z!=ut&&(u.fillStyle=ut=z),E!=Lt&&(u.lineWidth=Lt=E),K!=Sn&&(u.lineJoin=Sn=K),D!=gt&&(u.lineCap=gt=D),L!=Dt&&u.setLineDash(Dt=L)}function En(x,E,L,D){E!=ut&&(u.fillStyle=ut=E),x!=Ge&&(u.font=Ge=x),L!=Kt&&(u.textAlign=Kt=L),D!=vt&&(u.textBaseline=vt=D)}function Ds(x,E,L,D,z=0){if(D.length>0&&x.auto(n,Ne)&&(E==null||E.min==null)){let K=yt(G,0),oe=yt(ue,D.length-1),pe=L.min==null?NM(D,K,oe,z,x.distr==3):[L.min,L.max];x.min=_i(x.min,L.min=pe[0]),x.max=kn(x.max,L.max=pe[1])}}const Wt={min:null,max:null};function Ci(){for(let D in b){let z=b[D];q[D]==null&&(z.min==null||q[A]!=null&&z.auto(n,Ne))&&(q[D]=Wt)}for(let D in b){let z=b[D];q[D]==null&&z.from!=null&&q[z.from]!=null&&(q[D]=Wt)}q[A]!=null&&or(!0);let x={};for(let D in q){let z=q[D];if(z!=null){let K=x[D]=da(b[D],WM);if(z.min!=null)nn(K,z);else if(D!=A||s==2)if(Y==0&&K.from==null){let oe=K.range(n,null,null,D);K.min=oe[0],K.max=oe[1]}else K.min=Rt,K.max=-Rt}}if(Y>0){S.forEach((D,z)=>{if(s==1){let K=D.scale,oe=q[K];if(oe==null)return;let pe=x[K];if(z==0){let Me=pe.range(n,pe.min,pe.max,K);pe.min=Me[0],pe.max=Me[1],G=gi(pe.min,e[0]),ue=gi(pe.max,e[0]),ue-G>1&&(e[0][G]<pe.min&&G++,e[0][ue]>pe.max&&ue--),D.min=Le[G],D.max=Le[ue]}else D.show&&D.auto&&Ds(pe,oe,D,e[z],D.sorted);D.idxs[0]=G,D.idxs[1]=ue}else if(z>0&&D.show&&D.auto){let[K,oe]=D.facets,pe=K.scale,Me=oe.scale,[De,Ie]=e[z],Oe=x[pe],st=x[Me];Oe!=null&&Ds(Oe,q[pe],K,De,K.sorted),st!=null&&Ds(st,q[Me],oe,Ie,oe.sorted),D.min=oe.min,D.max=oe.max}});for(let D in x){let z=x[D],K=q[D];if(z.from==null&&(K==null||K.min==null)){let oe=z.range(n,z.min==Rt?null:z.min,z.max==-Rt?null:z.max,D);z.min=oe[0],z.max=oe[1]}}}for(let D in x){let z=x[D];if(z.from!=null){let K=x[z.from];if(K.min==null)z.min=z.max=null;else{let oe=z.range(n,K.min,K.max,D);z.min=oe[0],z.max=oe[1]}}}let E={},L=!1;for(let D in x){let z=x[D],K=b[D];if(K.min!=z.min||K.max!=z.max){K.min=z.min,K.max=z.max;let oe=K.distr;K._min=oe==3?ns(K.min):oe==4?zc(K.min,K.asinh):oe==100?K.fwd(K.min):K.min,K._max=oe==3?ns(K.max):oe==4?zc(K.max,K.asinh):oe==100?K.fwd(K.max):K.max,E[D]=L=!0}}if(L){S.forEach((D,z)=>{s==2?z>0&&E.y&&(D._paths=null):E[D.scale]&&(D._paths=null)});for(let D in E)O=!0,pn("setScale",D);he&&Se.left>=0&&(ae=re=!0)}for(let D in q)q[D]=null}function ba(x){let E=Oh(G-1,0,Y-1),L=Oh(ue+1,0,Y-1);for(;x[E]==null&&E>0;)E--;for(;x[L]==null&&L<Y-1;)L++;return[E,L]}function zn(){if(Y>0){let x=S.some(E=>E._focus)&&It!=un.alpha;x&&(u.globalAlpha=It=un.alpha),S.forEach((E,L)=>{if(L>0&&E.show&&(ar(L,!1),ar(L,!0),E._paths==null)){let D=It;It!=E.alpha&&(u.globalAlpha=It=E.alpha);let z=s==2?[0,e[L][0].length-1]:ba(e[L]);E._paths=E.paths(n,L,z[0],z[1]),It!=D&&(u.globalAlpha=It=D)}}),S.forEach((E,L)=>{if(L>0&&E.show){let D=It;It!=E.alpha&&(u.globalAlpha=It=E.alpha),E._paths!=null&&uo(L,!1);{let z=E._paths!=null?E._paths.gaps:null,K=E.points.show(n,L,G,ue,z),oe=E.points.filter(n,L,K,z);(K||oe)&&(E.points._paths=E.points.paths(n,L,G,ue,oe),uo(L,!0))}It!=D&&(u.globalAlpha=It=D),pn("drawSeries",L)}}),x&&(u.globalAlpha=It=1)}}function ar(x,E){let L=E?S[x].points:S[x];L._stroke=L.stroke(n,x),L._fill=L.fill(n,x)}function uo(x,E){let L=E?S[x].points:S[x],{stroke:D,fill:z,clip:K,flags:oe,_stroke:pe=L._stroke,_fill:Me=L._fill,_width:De=L.width}=L._paths;De=Pt(De*bt,3);let Ie=null,Oe=De%2/2;E&&Me==null&&(Me=De>0?"#fff":pe);let st=L.pxAlign==1&&Oe>0;if(st&&u.translate(Oe,Oe),!E){let St=Qe-De/2,_t=He-De/2,dt=we+De,nt=Ve+De;Ie=new Path2D,Ie.rect(St,_t,dt,nt)}E?Gl(pe,De,L.dash,L.cap,Me,D,z,oe,K):fo(x,pe,De,L.dash,L.cap,Me,D,z,oe,Ie,K),st&&u.translate(-Oe,-Oe)}function fo(x,E,L,D,z,K,oe,pe,Me,De,Ie){let Oe=!1;Me!=0&&I.forEach((st,St)=>{if(st.series[0]==x){let _t=S[st.series[1]],dt=e[st.series[1]],nt=(_t._paths||Ka).band;xs(nt)&&(nt=st.dir==1?nt[0]:nt[1]);let $e,Ft=null;_t.show&&nt&&FM(dt,G,ue)?(Ft=st.fill(n,St)||K,$e=_t._paths.clip):nt=null,Gl(E,L,D,z,Ft,oe,pe,Me,De,Ie,$e,nt),Oe=!0}}),Oe||Gl(E,L,D,z,K,oe,pe,Me,De,Ie)}const bu=fa|Bh;function Gl(x,E,L,D,z,K,oe,pe,Me,De,Ie,Oe){Vi(x,E,L,D,z),(Me||De||Oe)&&(u.save(),Me&&u.clip(Me),De&&u.clip(De)),Oe?(pe&bu)==bu?(u.clip(Oe),Ie&&u.clip(Ie),mo(z,oe),po(x,K,E)):pe&Bh?(mo(z,oe),u.clip(Oe),po(x,K,E)):pe&fa&&(u.save(),u.clip(Oe),Ie&&u.clip(Ie),mo(z,oe),u.restore(),po(x,K,E)):(mo(z,oe),po(x,K,E)),(Me||De||Oe)&&u.restore()}function po(x,E,L){L>0&&(E instanceof Map?E.forEach((D,z)=>{u.strokeStyle=Be=z,u.stroke(D)}):E!=null&&x&&u.stroke(E))}function mo(x,E){E instanceof Map?E.forEach((L,D)=>{u.fillStyle=ut=D,u.fill(L)}):E!=null&&x&&u.fill(E)}function km(x,E,L,D){let z=_[x],K;if(D<=0)K=[0,0];else{let oe=z._space=z.space(n,x,E,L,D),pe=z._incrs=z.incrs(n,x,E,L,D,oe);K=sE(E,L,pe,D,oe)}return z._found=K}function Wl(x,E,L,D,z,K,oe,pe,Me,De){let Ie=oe%2/2;v==1&&u.translate(Ie,Ie),Vi(pe,oe,Me,De,pe),u.beginPath();let Oe,st,St,_t,dt=z+(D==0||D==3?-K:K);L==0?(st=z,_t=dt):(Oe=z,St=dt);for(let nt=0;nt<x.length;nt++)E[nt]!=null&&(L==0?Oe=St=x[nt]:st=_t=x[nt],u.moveTo(Oe,st),u.lineTo(St,_t));u.stroke(),v==1&&u.translate(-Ie,-Ie)}function Bm(x){let E=!0;return _.forEach((L,D)=>{if(!L.show)return;let z=b[L.scale];if(z.min==null){L._show&&(E=!1,L._show=!1,or(!1));return}else L._show||(E=!1,L._show=!0,or(!1));let K=L.side,oe=K%2,{min:pe,max:Me}=z,[De,Ie]=km(D,pe,Me,oe==0?te:$);if(Ie==0)return;let Oe=z.distr==2,st=L._splits=L.splits(n,D,pe,Me,De,Ie,Oe),St=z.distr==2?st.map($e=>Le[$e]):st,_t=z.distr==2?Le[st[1]]-Le[st[0]]:De,dt=L._values=L.values(n,L.filter(n,St,D,Ie,_t),D,Ie,_t);L._rotate=K==2?L.rotate(n,dt,D,Ie):0;let nt=L._size;L._size=si(L.size(n,dt,D,x)),nt!=null&&L._size!=nt&&(E=!1)}),E}function zm(x){let E=!0;return W.forEach((L,D)=>{let z=L(n,D,Hi,x);z!=Z[D]&&(E=!1),Z[D]=z}),E}function Hm(){for(let x=0;x<_.length;x++){let E=_[x];if(!E.show||!E._show)continue;let L=E.side,D=L%2,z,K,oe=E.stroke(n,x),pe=L==0||L==3?-1:1,[Me,De]=E._found;if(E.label!=null){let In=E.labelGap*pe,$n=rn((E._lpos+In)*bt);En(E.labelFont[0],oe,"center",L==2?za:df),u.save(),D==1?(z=K=0,u.translate($n,rn(He+Ve/2)),u.rotate((L==3?-ll:ll)/2)):(z=rn(Qe+we/2),K=$n);let Ns=Yp(E.label)?E.label(n,x,Me,De):E.label;u.fillText(Ns,z,K),u.restore()}if(De==0)continue;let Ie=b[E.scale],Oe=D==0?we:Ve,st=D==0?Qe:He,St=E._splits,_t=Ie.distr==2?St.map(In=>Le[In]):St,dt=Ie.distr==2?Le[St[1]]-Le[St[0]]:Me,nt=E.ticks,$e=E.border,Ft=nt.show?nt.size:0,Xt=rn(Ft*bt),mn=rn((E.alignTo==2?E._size-Ft-E.gap:E.gap)*bt),Ct=E._rotate*-ll/180,Yt=p(E._pos*bt),Gn=(Xt+mn)*pe,Dn=Yt+Gn;K=D==0?Dn:0,z=D==1?Dn:0;let ei=E.font[0],hi=E.align==1?Vr:E.align==2?Fc:Ct>0?Vr:Ct<0?Fc:D==0?"center":L==3?Fc:Vr,Li=Ct||D==1?"middle":L==2?za:df;En(ei,oe,hi,Li);let Wn=E.font[1]*E.lineGap,ti=St.map(In=>p(o(In,Ie,Oe,st))),ui=E._values;for(let In=0;In<ui.length;In++){let $n=ui[In];if($n!=null){D==0?z=ti[In]:K=ti[In],$n=""+$n;let Ns=$n.indexOf(`
`)==-1?[$n]:$n.split(/\n/gm);for(let Un=0;Un<Ns.length;Un++){let Hu=Ns[Un];Ct?(u.save(),u.translate(z,K+Un*Wn),u.rotate(Ct),u.fillText(Hu,0,0),u.restore()):u.fillText(Hu,z,K+Un*Wn)}}}nt.show&&Wl(ti,nt.filter(n,_t,x,De,dt),D,L,Yt,Xt,Pt(nt.width*bt,3),nt.stroke(n,x),nt.dash,nt.cap);let Di=E.grid;Di.show&&Wl(ti,Di.filter(n,_t,x,De,dt),D,D==0?2:1,D==0?He:Qe,D==0?Ve:we,Pt(Di.width*bt,3),Di.stroke(n,x),Di.dash,Di.cap),$e.show&&Wl([Yt],[1],D==0?1:0,D==0?1:2,D==1?He:Qe,D==1?Ve:we,Pt($e.width*bt,3),$e.stroke(n,x),$e.dash,$e.cap)}pn("drawAxes")}function or(x){S.forEach((E,L)=>{L>0&&(E._paths=null,x&&(s==1?(E.min=null,E.max=null):E.facets.forEach(D=>{D.min=null,D.max=null})))})}let go=!1,$l=!1,Ma=[];function Vm(){$l=!1;for(let x=0;x<Ma.length;x++)pn(...Ma[x]);Ma.length=0}function lr(){go||(JM(Mu),go=!0)}function Gm(x,E=!1){go=!0,$l=E,x(n),Mu(),E&&Ma.length>0&&queueMicrotask(Vm)}n.batch=Gm;function Mu(){if(B&&(Ci(),B=!1),O&&(xt(),O=!1),ce){if(kt(f,Vr,Ee),kt(f,za,ve),kt(f,Ga,te),kt(f,Wa,$),kt(g,Vr,Ee),kt(g,za,ve),kt(g,Ga,te),kt(g,Wa,$),kt(d,Ga,Q),kt(d,Wa,le),h.width=rn(Q*bt),h.height=rn(le*bt),_.forEach(({_el:x,_show:E,_size:L,_pos:D,side:z})=>{if(x!=null)if(E){let K=z===3||z===0?L:0,oe=z%2==1;kt(x,oe?"left":"top",D-K),kt(x,oe?"width":"height",L),kt(x,oe?"top":"left",oe?ve:Ee),kt(x,oe?"height":"width",oe?$:te),Uh(x,Xs)}else jn(x,Xs)}),Be=ut=Lt=Sn=gt=Ge=Kt=vt=Dt=null,It=1,Ta(!0),Ee!=Ce||ve!=Ze||te!=me||$!=Ae){or(!1);let x=te/me,E=$/Ae;if(he&&!ae&&Se.left>=0){Se.left*=x,Se.top*=E,cr&&Ii(cr,rn(Se.left),0,te,$),hr&&Ii(hr,0,rn(Se.top),te,$);for(let L=0;L<Ln.length;L++){let D=Ln[L];D!=null&&(ci[L]*=x,zi[L]*=E,Ii(D,si(ci[L]),si(zi[L]),te,$))}}if(Ot.show&&!se&&Ot.left>=0&&Ot.width>0){Ot.left*=x,Ot.width*=x,Ot.top*=E,Ot.height*=E;for(let L in Jl)kt(fr,L,Ot[L])}Ce=Ee,Ze=ve,me=te,Ae=$}pn("setSize"),ce=!1}Q>0&&le>0&&(u.clearRect(0,0,h.width,h.height),pn("drawClear"),N.forEach(x=>x()),pn("draw")),Ot.show&&se&&(vo(Ot),se=!1),he&&ae&&(Us(null,!0,!1),ae=!1),Te.show&&Te.live&&re&&(jl(),re=!1),l||(l=!0,n.status=1,pn("ready")),Ne=!1,go=!1}n.redraw=(x,E)=>{O=E||!1,x!==!1?ls(A,P.min,P.max):lr()};function ql(x,E){let L=b[x];if(L.from==null){if(Y==0){let D=L.range(n,E.min,E.max,x);E.min=D[0],E.max=D[1]}if(E.min>E.max){let D=E.min;E.min=E.max,E.max=D}if(Y>1&&E.min!=null&&E.max!=null&&E.max-E.min<1e-16)return;x==A&&L.distr==2&&Y>0&&(E.min=gi(E.min,e[0]),E.max=gi(E.max,e[0]),E.min==E.max&&E.max++),q[x]=E,B=!0,lr()}}n.setScale=ql;let Xl,Yl,cr,hr,wu,Eu,ur,dr,Tu,Au,Nt,Gt,os=!1;const bn=Se.drag;let dn=bn.x,fn=bn.y;he&&(Se.x&&(Xl=ii(SM,g)),Se.y&&(Yl=ii(bM,g)),P.ori==0?(cr=Xl,hr=Yl):(cr=Yl,hr=Xl),Nt=Se.left,Gt=Se.top);const Ot=n.select=nn({show:!0,over:!0,left:0,width:0,top:0,height:0},i.select),fr=Ot.show?ii(yM,Ot.over?g:f):null;function vo(x,E){if(Ot.show){for(let L in x)Ot[L]=x[L],L in Jl&&kt(fr,L,x[L]);E!==!1&&pn("setSelect")}}n.setSelect=vo;function Wm(x){if(S[x].show)ie&&Uh(Fe[x],Xs);else if(ie&&jn(Fe[x],Xs),he){let L=Bi?Ln[0]:Ln[x];L!=null&&Ii(L,-10,-10,te,$)}}function ls(x,E,L){ql(x,{min:E,max:L})}function Ri(x,E,L,D){E.focus!=null&&jm(x),E.show!=null&&S.forEach((z,K)=>{K>0&&(x==K||x==null)&&(z.show=E.show,Wm(K),s==2?(ls(z.facets[0].scale,null,null),ls(z.facets[1].scale,null,null)):ls(z.scale,null,null),lr())}),L!==!1&&pn("setSeries",x,E),D&&Aa("setSeries",n,x,E)}n.setSeries=Ri;function $m(x,E){nn(I[x],E)}function qm(x,E){x.fill=pt(x.fill||null),x.dir=yt(x.dir,-1),E=E??I.length,I.splice(E,0,x)}function Xm(x){x==null?I.length=0:I.splice(x,1)}n.addBand=qm,n.setBand=$m,n.delBand=Xm;function Ym(x,E){S[x].alpha=E,he&&Ln[x]!=null&&(Ln[x].style.opacity=E),ie&&Fe[x]&&(Fe[x].style.opacity=E)}let Gi,cs,Is;const pr={focus:!0};function jm(x){if(x!=Is){let E=x==null,L=un.alpha!=1;S.forEach((D,z)=>{if(s==1||z>0){let K=E||z==0||z==x;D._focus=E?null:K,L&&Ym(z,K?1:un.alpha)}}),Is=x,L&&lr()}}ie&&Ai&&U(gf,fe,x=>{Se._lock||(Ht(x),Is!=null&&Ri(null,pr,!0,en.setSeries))});function Pi(x,E,L){let D=b[E];L&&(x=x/bt-(D.ori==1?ve:Ee));let z=te;D.ori==1&&(z=$,x=z-x),D.dir==-1&&(x=z-x);let K=D._min,oe=D._max,pe=x/z,Me=K+(oe-K)*pe,De=D.distr;return De==3?ha(10,Me):De==4?BM(Me,D.asinh):De==100?D.bwd(Me):Me}function Km(x,E){let L=Pi(x,A,E);return gi(L,e[0],G,ue)}n.valToIdx=x=>gi(x,e[0]),n.posToIdx=Km,n.posToVal=Pi,n.valToPos=(x,E,L)=>b[E].ori==0?r(x,b[E],L?we:te,L?Qe:0):a(x,b[E],L?Ve:$,L?He:0),n.setCursor=(x,E,L)=>{Nt=x.left,Gt=x.top,Us(null,E,L)};function Cu(x,E){kt(fr,Vr,Ot.left=x),kt(fr,Ga,Ot.width=E)}function Ru(x,E){kt(fr,za,Ot.top=x),kt(fr,Wa,Ot.height=E)}let wa=P.ori==0?Cu:Ru,Ea=P.ori==1?Cu:Ru;function Jm(){if(ie&&Te.live)for(let x=s==2?1:0;x<S.length;x++){if(x==0&&ft)continue;let E=Te.values[x],L=0;for(let D in E)mt[x][L++].firstChild.nodeValue=E[D]}}function jl(x,E){if(x!=null&&(x.idxs?x.idxs.forEach((L,D)=>{ye[D]=L}):GM(x.idx)||ye.fill(x.idx),Te.idx=ye[0]),ie&&Te.live){for(let L=0;L<S.length;L++)(L>0||s==1&&!ft)&&Zm(L,ye[L]);Jm()}re=!1,E!==!1&&pn("setLegend")}n.setLegend=jl;function Zm(x,E){let L=S[x],D=x==0&&X==2?Le:e[x],z;ft?z=L.values(n,x,E)??rt:(z=L.value(n,E==null?null:D[E],x,E),z=z==null?rt:{_:z}),Te.values[x]=z}function Us(x,E,L){Tu=Nt,Au=Gt,[Nt,Gt]=Se.move(n,Nt,Gt),Se.left=Nt,Se.top=Gt,he&&(cr&&Ii(cr,rn(Nt),0,te,$),hr&&Ii(hr,0,rn(Gt),te,$));let D,z=G>ue;Gi=Rt,cs=null;let K=P.ori==0?te:$,oe=P.ori==1?te:$;if(Nt<0||Y==0||z){D=Se.idx=null;for(let pe=0;pe<S.length;pe++){let Me=Ln[pe];Me!=null&&Ii(Me,-10,-10,te,$)}Ai&&Ri(null,pr,!0,x==null&&en.setSeries),Te.live&&(ye.fill(D),re=!0)}else{let pe,Me,De;s==1&&(pe=P.ori==0?Nt:Gt,Me=Pi(pe,A),D=Se.idx=gi(Me,e[0],G,ue),De=H(e[0][D],P,K,0));let Ie=-10,Oe=-10,st=0,St=0,_t=!0,dt="",nt="";for(let $e=s==2?1:0;$e<S.length;$e++){let Ft=S[$e],Xt=ye[$e],mn=Xt==null?null:s==1?e[$e][Xt]:e[$e][1][Xt],Ct=Se.dataIdx(n,$e,D,Me),Yt=Ct==null?null:s==1?e[$e][Ct]:e[$e][1][Ct];if(re=re||Yt!=mn||Ct!=Xt,ye[$e]=Ct,$e>0&&Ft.show){let Gn=Ct==null?-10:Ct==D?De:H(s==1?e[0][Ct]:e[$e][0][Ct],P,K,0),Dn=Yt==null?-10:J(Yt,s==1?b[Ft.scale]:b[Ft.facets[1].scale],oe,0);if(Ai&&Yt!=null){let ei=P.ori==1?Nt:Gt,hi=an(un.dist(n,$e,Ct,Dn,ei));if(hi<Gi){let Li=un.bias;if(Li!=0){let Wn=Pi(ei,Ft.scale),ti=Yt>=0?1:-1,ui=Wn>=0?1:-1;ui==ti&&(ui==1?Li==1?Yt>=Wn:Yt<=Wn:Li==1?Yt<=Wn:Yt>=Wn)&&(Gi=hi,cs=$e)}else Gi=hi,cs=$e}}if(re||Bi){let ei,hi;P.ori==0?(ei=Gn,hi=Dn):(ei=Dn,hi=Gn);let Li,Wn,ti,ui,Di,In,$n=!0,Ns=Vt.bbox;if(Ns!=null){$n=!1;let Un=Ns(n,$e);ti=Un.left,ui=Un.top,Li=Un.width,Wn=Un.height}else ti=ei,ui=hi,Li=Wn=Vt.size(n,$e);if(In=Vt.fill(n,$e),Di=Vt.stroke(n,$e),Bi)$e==cs&&Gi<=un.prox&&(Ie=ti,Oe=ui,st=Li,St=Wn,_t=$n,dt=In,nt=Di);else{let Un=Ln[$e];Un!=null&&(ci[$e]=ti,zi[$e]=ui,Mf(Un,Li,Wn,$n),Sf(Un,In,Di),Ii(Un,si(ti),si(ui),te,$))}}}}if(Bi){let $e=un.prox,Ft=Is==null?Gi<=$e:Gi>$e||cs!=Is;if(re||Ft){let Xt=Ln[0];Xt!=null&&(ci[0]=Ie,zi[0]=Oe,Mf(Xt,st,St,_t),Sf(Xt,dt,nt),Ii(Xt,si(Ie),si(Oe),te,$))}}}if(Ot.show&&os)if(x!=null){let[pe,Me]=en.scales,[De,Ie]=en.match,[Oe,st]=x.cursor.sync.scales,St=x.cursor.drag;if(dn=St._x,fn=St._y,dn||fn){let{left:_t,top:dt,width:nt,height:$e}=x.select,Ft=x.scales[Oe].ori,Xt=x.posToVal,mn,Ct,Yt,Gn,Dn,ei=pe!=null&&De(pe,Oe),hi=Me!=null&&Ie(Me,st);ei&&dn?(Ft==0?(mn=_t,Ct=nt):(mn=dt,Ct=$e),Yt=b[pe],Gn=H(Xt(mn,Oe),Yt,K,0),Dn=H(Xt(mn+Ct,Oe),Yt,K,0),wa(_i(Gn,Dn),an(Dn-Gn))):wa(0,K),hi&&fn?(Ft==1?(mn=_t,Ct=nt):(mn=dt,Ct=$e),Yt=b[Me],Gn=J(Xt(mn,st),Yt,oe,0),Dn=J(Xt(mn+Ct,st),Yt,oe,0),Ea(_i(Gn,Dn),an(Dn-Gn))):Ea(0,oe)}else Zl()}else{let pe=an(Tu-wu),Me=an(Au-Eu);if(P.ori==1){let st=pe;pe=Me,Me=st}dn=bn.x&&pe>=bn.dist,fn=bn.y&&Me>=bn.dist;let De=bn.uni;De!=null?dn&&fn&&(dn=pe>=De,fn=Me>=De,!dn&&!fn&&(Me>pe?fn=!0:dn=!0)):bn.x&&bn.y&&(dn||fn)&&(dn=fn=!0);let Ie,Oe;dn&&(P.ori==0?(Ie=ur,Oe=Nt):(Ie=dr,Oe=Gt),wa(_i(Ie,Oe),an(Oe-Ie)),fn||Ea(0,oe)),fn&&(P.ori==1?(Ie=ur,Oe=Nt):(Ie=dr,Oe=Gt),Ea(_i(Ie,Oe),an(Oe-Ie)),dn||wa(0,K)),!dn&&!fn&&(wa(0,0),Ea(0,0))}if(bn._x=dn,bn._y=fn,x==null){if(L){if(zu!=null){let[pe,Me]=en.scales;en.values[0]=pe!=null?Pi(P.ori==0?Nt:Gt,pe):null,en.values[1]=Me!=null?Pi(P.ori==1?Nt:Gt,Me):null}Aa(kc,n,Nt,Gt,te,$,D)}if(Ai){let pe=L&&en.setSeries,Me=un.prox;Is==null?Gi<=Me&&Ri(cs,pr,!0,pe):Gi>Me?Ri(null,pr,!0,pe):cs!=Is&&Ri(cs,pr,!0,pe)}}re&&(Te.idx=D,jl()),E!==!1&&pn("setCursor")}let hs=null;Object.defineProperty(n,"rect",{get(){return hs==null&&Ta(!1),hs}});function Ta(x=!1){x?hs=null:(hs=g.getBoundingClientRect(),pn("syncRect",hs))}function Pu(x,E,L,D,z,K,oe){Se._lock||os&&x!=null&&x.movementX==0&&x.movementY==0||(Kl(x,E,L,D,z,K,oe,!1,x!=null),x!=null?Us(null,!0,!0):Us(E,!0,!1))}function Kl(x,E,L,D,z,K,oe,pe,Me){if(hs==null&&Ta(!1),Ht(x),x!=null)L=x.clientX-hs.left,D=x.clientY-hs.top;else{if(L<0||D<0){Nt=-10,Gt=-10;return}let[De,Ie]=en.scales,Oe=E.cursor.sync,[st,St]=Oe.values,[_t,dt]=Oe.scales,[nt,$e]=en.match,Ft=E.axes[0].side%2==1,Xt=P.ori==0?te:$,mn=P.ori==1?te:$,Ct=Ft?K:z,Yt=Ft?z:K,Gn=Ft?D:L,Dn=Ft?L:D;if(_t!=null?L=nt(De,_t)?o(st,b[De],Xt,0):-10:L=Xt*(Gn/Ct),dt!=null?D=$e(Ie,dt)?o(St,b[Ie],mn,0):-10:D=mn*(Dn/Yt),P.ori==1){let ei=L;L=D,D=ei}}Me&&(E==null||E.cursor.event.type==kc)&&((L<=1||L>=te-1)&&(L=Gs(L,te)),(D<=1||D>=$-1)&&(D=Gs(D,$))),pe?(wu=L,Eu=D,[ur,dr]=Se.move(n,L,D)):(Nt=L,Gt=D)}const Jl={width:0,height:0,left:0,top:0};function Zl(){vo(Jl,!1)}let Lu,Du,Iu,Uu;function Nu(x,E,L,D,z,K,oe){os=!0,dn=fn=bn._x=bn._y=!1,Kl(x,E,L,D,z,K,oe,!0,!1),x!=null&&(U(Bc,Dh,Ou,!1),Aa(pf,n,ur,dr,te,$,null));let{left:pe,top:Me,width:De,height:Ie}=Ot;Lu=pe,Du=Me,Iu=De,Uu=Ie}function Ou(x,E,L,D,z,K,oe){os=bn._x=bn._y=!1,Kl(x,E,L,D,z,K,oe,!1,!0);let{left:pe,top:Me,width:De,height:Ie}=Ot,Oe=De>0||Ie>0,st=Lu!=pe||Du!=Me||Iu!=De||Uu!=Ie;if(Oe&&st&&vo(Ot),bn.setScale&&Oe&&st){let St=pe,_t=De,dt=Me,nt=Ie;if(P.ori==1&&(St=Me,_t=Ie,dt=pe,nt=De),dn&&ls(A,Pi(St,A),Pi(St+_t,A)),fn)for(let $e in b){let Ft=b[$e];$e!=A&&Ft.from==null&&Ft.min!=Rt&&ls($e,Pi(dt+nt,$e),Pi(dt,$e))}Zl()}else Se.lock&&(Se._lock=!Se._lock,Us(E,!0,x!=null));x!=null&&(T(Bc,Dh),Aa(Bc,n,Nt,Gt,te,$,null))}function Qm(x,E,L,D,z,K,oe){if(Se._lock)return;Ht(x);let pe=os;if(os){let Me=!0,De=!0,Ie=10,Oe,st;P.ori==0?(Oe=dn,st=fn):(Oe=fn,st=dn),Oe&&st&&(Me=Nt<=Ie||Nt>=te-Ie,De=Gt<=Ie||Gt>=$-Ie),Oe&&Me&&(Nt=Nt<ur?0:te),st&&De&&(Gt=Gt<dr?0:$),Us(null,!0,!0),os=!1}Nt=-10,Gt=-10,ye.fill(null),Us(null,!0,!0),pe&&(os=pe)}function Fu(x,E,L,D,z,K,oe){Se._lock||(Ht(x),tt(),Zl(),x!=null&&Aa(vf,n,Nt,Gt,te,$,null))}function ku(){_.forEach(rE),_e(n.width,n.height,!0)}Js(xl,Zr,ku);const mr={};mr.mousedown=Nu,mr.mousemove=Pu,mr.mouseup=Ou,mr.dblclick=Fu,mr.setSeries=(x,E,L,D)=>{let z=en.match[2];L=z(n,E,L),L!=-1&&Ri(L,D,!0,!1)},he&&(U(pf,g,Nu),U(kc,g,Pu),U(mf,g,x=>{Ht(x),Ta(!1)}),U(gf,g,Qm),U(vf,g,Fu),zh.add(n),n.syncRect=Ta);const xo=n.hooks=i.hooks||{};function pn(x,E,L){$l?Ma.push([x,E,L]):x in xo&&xo[x].forEach(D=>{D.call(null,n,E,L)})}(i.plugins||[]).forEach(x=>{for(let E in x.hooks)xo[E]=(xo[E]||[]).concat(x.hooks[E])});const Bu=(x,E,L)=>L,en=nn({key:null,setSeries:!1,filters:{pub:Cf,sub:Cf},scales:[A,S[1]?S[1].scale:null],match:[Rf,Rf,Bu],values:[null,null]},Se.sync);en.match.length==2&&en.match.push(Bu),Se.sync=en;const zu=en.key,Ql=xm(zu);function Aa(x,E,L,D,z,K,oe){en.filters.pub(x,E,L,D,z,K,oe)&&Ql.pub(x,E,L,D,z,K,oe)}Ql.sub(n);function eg(x,E,L,D,z,K,oe){en.filters.sub(x,E,L,D,z,K,oe)&&mr[x](null,E,L,D,z,K,oe)}n.pub=eg;function tg(){Ql.unsub(n),zh.delete(n),qe.clear(),Nh(xl,Zr,ku),c.remove(),fe==null||fe.remove(),pn("destroy")}n.destroy=tg;function ec(){pn("init",i,e),et(e||i.data,!1),q[A]?ql(A,q[A]):tt(),se=Ot.show&&(Ot.width>0||Ot.height>0),ae=re=!0,_e(i.width,i.height)}return S.forEach(Sa),_.forEach(Vl),t?t instanceof HTMLElement?(t.appendChild(c),ec()):t(n,ec):ec(),n}xn.assign=nn;xn.fmtNum=uu;xn.rangeNum=_l;xn.rangeLog=Ul;xn.rangeAsinh=cu;xn.orient=rr;xn.pxRatio=bt;xn.join=KM;xn.fmtDate=fu,xn.tzDate=ow;xn.sync=xm;{xn.addGap=Gw,xn.clipGaps=Fl;let i=xn.paths={points:wm};i.linear=Tm,i.stepped=qw,i.bars=Xw,i.spline=jw}function Wc(i){return Math.max(120,i.clientHeight-30)}const Jf=[{id:"pareto",panelId:"plotter-pareto",hostId:"plotter-pareto-chart",title:"Pareto frontier",glyph:"◭",key:Lc.pareto},{id:"ablation",panelId:"plotter-ablation",hostId:"plotter-ablation-chart",title:"Ablation",glyph:"▥",key:Lc.ablation},{id:"variability",panelId:"plotter-variability",hostId:"plotter-variability-chart",title:"Variability",glyph:"◇",key:Lc.variability}];function aE(i){return`
    <div id="${i.hostId}" style="flex: 1; position: relative; overflow: hidden;"></div>
    <div class="chart-empty-state">
      <div class="empty-icon">${i.glyph}</div>
      <div style="font-size: 13px; font-weight: 600; color: var(--text-primary);">${i.title}</div>
      <div style="font-size: 11px; color: var(--text-secondary); max-width: 280px; line-height: 1.5;">${oE(i.id)}</div>
    </div>
    <div class="chart-toolbar">
      <span class="chart-status">No data</span>
    </div>
  `}function oE(i){switch(i){case"pareto":return"Shows validation accuracy vs. speed for each measured cell. Pareto frontier cells are not dominated on both axes.";case"ablation":return"Shows how each credit arm performs when other axes are held fixed. Error bars = ±1 std dev. Dashed line = chance level.";case"variability":return"Shows seed-to-seed spread per credit arm. Box = IQR, line = median, whiskers = 1.5×IQR, dots = outliers. Dashed line = chance level.";default:return"Select a run from the legend to populate this chart."}}class lE{constructor(){M(this,"name","Plotter");M(this,"container",null);M(this,"chartPanels",new Map);M(this,"tooltip",null);M(this,"paretoPlot",null);M(this,"ablationPlot",null);M(this,"variabilityPlot",null);M(this,"records",[]);M(this,"ablationGroups",[]);M(this,"paretoFlags",[]);M(this,"chance",.1);M(this,"paretoRecordIndices",[]);M(this,"paretoXData",[]);M(this,"paretoYData",[]);M(this,"categoryLabels",[]);M(this,"ablationFixedAxes","");M(this,"onCampaignMetrics",e=>{const{data:t}=e;t!=null&&t.records&&Kn.observe(e==null?void 0:e.campaign_id,t)});M(this,"onRunChanged",(e,t)=>{t&&(this.records=t.records??[],this.paretoFlags=t.pareto??[],this.ablationGroups=t.ablation_groups??[],typeof t.chance=="number"&&(this.chance=t.chance),this.updatePlots(),this.updateStatus())});Jt.register("campaign_metrics",this.onCampaignMetrics),Kn.onChange(this.onRunChanged)}async init(){this.createUI(),console.log("[Plotter] Initialized")}async destroy(){var e,t,n,s;Jt.unregister("campaign_metrics",this.onCampaignMetrics),(e=this.paretoPlot)==null||e.destroy(),(t=this.ablationPlot)==null||t.destroy(),(n=this.variabilityPlot)==null||n.destroy(),(s=this.tooltip)==null||s.remove(),this.tooltip=null}createUI(){const e=document.getElementById("ui-overlay");if(!e)return;for(const n of Jf){const s=Ps({id:n.panelId,title:n.title,glyph:n.glyph,key:n.key,body:aE(n),dock:"right",defaultOpen:n.id==="pareto",className:"chart-panel",onToggle:r=>{r&&this.initPlot(n.id)}});this.chartPanels.set(n.id,s),s.querySelector(".chart-download").addEventListener("click",()=>this.download(n.id)),s.querySelector(".chart-empty-hint"),sr(n.panelId,n.title.toLowerCase(),n.glyph,()=>this.chartPanels.get(n.id)??null,n.key)}const t=this.chartPanels.get("pareto")??this.chartPanels.values().next().value;this.tooltip=document.createElement("div"),this.tooltip.id="plotter-tooltip",this.tooltip.style.cssText=`
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
    `,t?t.appendChild(this.tooltip):e.appendChild(this.tooltip)}showTab(e){var n;const t=Jf.find(s=>s.id===e);t&&($t.toggle(t.panelId),(n=this.chartPanels.get(t.id))==null||n.scrollIntoView({block:"nearest"}))}initPlot(e){e==="pareto"&&!this.paretoPlot&&this.initParetoPlot(),e==="ablation"&&!this.ablationPlot&&this.initAblationPlot(),e==="variability"&&!this.variabilityPlot&&this.initVariabilityPlot(),this.updatePlots()}updateStatus(){const e=this.records.length>0,t=`${this.records.length} records | ${this.paretoFlags.filter(s=>s).length} Pareto`,n=this.ablationFixedAxes?` | fixed: ${this.ablationFixedAxes}`:"";for(const s of this.chartPanels.values()){const r=s.querySelector(".chart-status"),a=s.querySelector(".chart-empty-state"),o=s.querySelector(".chart-empty-hint");r&&(r.textContent=e?t+n:"No run selected",r.title=r.textContent),a&&(a.style.display=e?"none":"flex"),o&&(o.style.display=e?"none":"flex")}}updatePlots(){const e=this.records.length>0;for(const t of this.chartPanels.values()){const n=t.querySelector(".chart-empty-state"),s=t.querySelector(".chart-empty-hint");n&&(n.style.display=e?"none":"flex"),s&&(s.style.display=e?"none":"flex")}this.paretoPlot&&this.updateParetoPlot(),this.ablationPlot&&this.updateAblationPlot(),this.variabilityPlot&&this.updateVariabilityPlot()}initParetoPlot(){const e=document.getElementById("plotter-pareto-chart");if(!e)return;const t={width:e.clientWidth,height:Wc(e),title:"Pareto Frontier: validation accuracy vs speed",axes:[{label:"1 / walltime_s   (faster →)",grid:{stroke:k.border}},{label:"accuracy",grid:{stroke:k.border},side:1}],scales:{x:{time:!1},y:{time:!1}},series:[{},{label:"val_acc",stroke:k.gradient,width:0,points:{show:!0,size:8,stroke:"white",width:1,fill:(n,s)=>{var o;const r=this.paretoRecordIndices[s],a=r===void 0?void 0:this.records[r];return a&&qt[(o=a.coordinate)==null?void 0:o.credit]||k.gradient}}}],hooks:{draw:[n=>{const s=n.ctx;if(this.paretoFlags.some(a=>a)){const a=[];this.records.forEach((o,l)=>{this.paretoFlags[l]&&o.payload.walltime_s&&o.payload.val_acc&&a.push([1/o.payload.walltime_s,o.payload.val_acc])}),a.sort((o,l)=>o[0]-l[0]),a.length>1&&(s.beginPath(),s.strokeStyle=k.pareto,s.lineWidth=2,s.setLineDash([5,5]),a.forEach((o,l)=>{const c=n.valToPos(o[0],"x"),h=n.valToPos(o[1],"y");l===0?s.moveTo(c,h):s.lineTo(c,h)}),s.stroke(),s.setLineDash([])),a.forEach(o=>{const l=n.valToPos(o[0],"x"),c=n.valToPos(o[1],"y");s.beginPath(),s.arc(l,c,7,0,Math.PI*2),s.strokeStyle=k.pareto,s.lineWidth=1.5,s.stroke()})}const r=n.valToPos(this.chance,"y");s.strokeStyle=k.chance_line,s.lineWidth=1.5,s.setLineDash([4,4]),s.beginPath(),s.moveTo(n.bbox.left,r),s.lineTo(n.bbox.width,r),s.stroke(),s.setLineDash([])}],setCursor:[n=>{this.showScatterTooltip(n)}]},cursor:{show:!0,drag:{setScale:!0},focus:{prox:16}}};this.paretoPlot=new xn(t,[[],[]],e)}recordAt(e){const t=this.paretoRecordIndices[e];return t===void 0?void 0:this.records[t]}updateParetoPlot(){if(!this.paretoPlot||this.records.length===0)return;const e=[],t=[];this.paretoRecordIndices=[],this.records.forEach((r,a)=>{const o=r.payload.walltime_s,l=r.payload.val_acc;this.paretoRecordIndices.push(a),o&&l?(e.push(1/o),t.push(l)):(e.push(NaN),t.push(NaN))}),this.paretoPlot.setData([e,t]),this.paretoXData=e,this.paretoYData=t;const n=e.filter(Number.isFinite),s=t.filter(Number.isFinite);n.length>0&&this.fitScale(this.paretoPlot,"x",Math.min(...n),Math.max(...n)),s.length>0&&this.fitScale(this.paretoPlot,"y",Math.min(Math.min(...s),this.chance),Math.max(...s))}fitScale(e,t,n,s){if(!Number.isFinite(n)||!Number.isFinite(s))return;n===s&&(n-=.01,s+=.01);const r=(s-n)*.05;e.setScale(t,{min:n-r,max:s+r})}initAblationPlot(){const e=document.getElementById("plotter-ablation-chart");if(!e)return;const t={width:e.clientWidth,height:Wc(e),title:"Ablation: credit arm → validation accuracy",axes:[{label:"credit arm",splits:()=>this.categoryIndices(),values:(n,s)=>s.map(r=>this.categoryLabels[r]??String(r)),grid:{stroke:k.border}},{label:"accuracy",grid:{stroke:k.border},side:1}],scales:{x:{time:!1},y:{time:!1}},series:[{},{label:"val_acc",width:0,points:{show:!1}}],hooks:{draw:[n=>{if(!this.ablationGroups.length)return;const s=n.ctx,r=this.ablationGroups.find(h=>h.axis==="credit");if(!r)return;const a=r.metrics.find(h=>h.metric==="val_acc");if(!a)return;const o=a.arms,l=n.bbox.width/(o.length*1.5);n.bbox.left,o.forEach((h,u)=>{const d=n.valToPos(u,"x"),f=n.valToPos(0,"y"),g=n.valToPos(h.mean,"y"),v=f-g;if(s.fillStyle=qt[h.value]||k.gradient,s.fillRect(d-l/2,g,l,v),h.std>0){const p=n.valToPos(h.mean+h.std,"y");s.strokeStyle=k.text_muted,s.lineWidth=1,s.beginPath(),s.moveTo(d,p),s.lineTo(d,f),s.stroke(),s.moveTo(d-3,p),s.lineTo(d+3,p),s.stroke()}});const c=n.valToPos(this.chance,"y");s.strokeStyle=k.chance_line,s.lineWidth=2,s.setLineDash([5,5]),s.beginPath(),s.moveTo(n.bbox.left,c),s.lineTo(n.bbox.width,c),s.stroke(),s.setLineDash([])}],setCursor:[n=>{this.showCategoryTooltip(n,"ablation")}]},cursor:{show:!0,drag:{setScale:!0}}};this.ablationPlot=new xn(t,[[],[]],e)}updateAblationPlot(){if(!this.ablationPlot||!this.ablationGroups.length)return;const e=this.ablationGroups.find(o=>o.axis==="credit");if(!e)return;const t=e.metrics.find(o=>o.metric==="val_acc");if(!t)return;const n=t.arms.map((o,l)=>l),s=t.arms.map(o=>o.mean);this.categoryLabels=t.arms.map(o=>o.value),this.ablationFixedAxes=e.fixed_axes.split(",").map(o=>o.split("=").pop()??o).join(", "),this.ablationPlot.setData([n,s]),this.fitScale(this.ablationPlot,"x",-.5,Math.max(n.length-.5,.5));const r=t.arms.flatMap(o=>[o.mean-o.std,o.mean+o.std]);r.length>0&&this.fitScale(this.ablationPlot,"y",Math.min(Math.min(...r),this.chance),Math.max(...r));const a=this.ablationPlot.root.querySelector(".u-title");a&&(a.textContent=`Ablation: ${e.axis} vs val_acc`)}initVariabilityPlot(){const e=document.getElementById("plotter-variability-chart");if(!e)return;const t={width:e.clientWidth,height:Wc(e),title:"Seed variability: validation accuracy per arm",axes:[{label:"credit arm",splits:()=>this.categoryIndices(),values:(n,s)=>s.map(r=>this.categoryLabels[r]??String(r)),grid:{stroke:k.border}},{label:"accuracy",grid:{stroke:k.border},side:1}],scales:{x:{time:!1},y:{time:!1}},series:[{},{label:"val_acc",width:0,points:{show:!1}}],hooks:{draw:[n=>{if(!this.records.length)return;const s=n.ctx,r={};this.records.forEach(c=>{const h=c.coordinate.credit,u=c.payload.val_acc;u!==void 0&&(r[h]||(r[h]=[])).push(u)});const a=Object.keys(r).sort(),o=n.bbox.width/(a.length*2);a.forEach((c,h)=>{const u=r[c].sort((y,P)=>y-P),d=u.length;if(d===0)return;const f=u[Math.floor(d*.25)],g=u[Math.floor(d*.5)],v=u[Math.floor(d*.75)],p=v-f,m=Math.max(u[0],f-1.5*p),S=Math.min(u[d-1],v+1.5*p),_=n.valToPos(h,"x"),b=n.valToPos(m,"y"),I=n.valToPos(f,"y"),A=n.valToPos(g,"y"),R=n.valToPos(v,"y"),N=n.valToPos(S,"y"),w=qt[c]||k.gradient;s.strokeStyle=w,s.lineWidth=1.5,s.beginPath(),s.moveTo(_,b),s.lineTo(_,I),s.moveTo(_,R),s.lineTo(_,N),s.stroke(),s.fillStyle=w+"44",s.strokeStyle=w,s.lineWidth=1.5,s.fillRect(_-o/2,R,o,I-R),s.strokeRect(_-o/2,R,o,I-R),s.strokeStyle="white",s.lineWidth=2,s.beginPath(),s.moveTo(_-o/2,A),s.lineTo(_+o/2,A),s.stroke(),u.forEach(y=>{if(y<m||y>S){const P=n.valToPos(y,"y");s.fillStyle=w,s.beginPath(),s.arc(_,P,2,0,Math.PI*2),s.fill()}})});const l=n.valToPos(this.chance,"y");s.strokeStyle=k.chance_line,s.lineWidth=2,s.setLineDash([5,5]),s.beginPath(),s.moveTo(n.bbox.left,l),s.lineTo(n.bbox.width,l),s.stroke(),s.setLineDash([])}],setCursor:[n=>{this.showCategoryTooltip(n,"variability")}]},cursor:{show:!0,drag:{setScale:!0}}};this.variabilityPlot=new xn(t,[[],[]],e)}updateVariabilityPlot(){if(!this.variabilityPlot||!this.records.length)return;const e=Array.from(new Set(this.records.map(r=>r.coordinate.credit))).sort(),t=e.map((r,a)=>a),n=e.map(()=>0);this.categoryLabels=e,this.variabilityPlot.setData([t,n]),this.fitScale(this.variabilityPlot,"x",-.5,Math.max(e.length-.5,.5));const s=this.records.map(r=>r.payload.val_acc).filter(r=>typeof r=="number");s.length>0&&this.fitScale(this.variabilityPlot,"y",Math.min(Math.min(...s),this.chance),Math.max(...s))}categoryIndices(){return this.categoryLabels.map((e,t)=>t)}showTooltip(e,t){if(!this.tooltip)return;const n=e.cursor;if(!n||n.left==null||n.top==null){this.hideTooltip();return}const s=e.ctx.canvas.getBoundingClientRect(),r=this.chartPanels.get("pareto")??this.chartPanels.values().next().value,a=r==null?void 0:r.getBoundingClientRect();if(!a){this.hideTooltip();return}this.tooltip.innerHTML=t,this.tooltip.style.display="block",this.tooltip.style.left=`${s.left-a.left+e.bbox.left+n.left+14}px`,this.tooltip.style.top=`${s.top-a.top+e.bbox.top+n.top+14}px`}hideTooltip(){this.tooltip&&(this.tooltip.style.display="none")}showScatterTooltip(e){var d,f;const t=e.cursor;if(!t||t.left==null||t.top==null){this.hideTooltip();return}let n=-1,s=1/0;if(this.paretoXData.forEach((g,v)=>{const p=this.paretoYData[v];if(!Number.isFinite(g)||!Number.isFinite(p))return;const m=e.valToPos(g,"x"),S=e.valToPos(p,"y");if(!Number.isFinite(m)||!Number.isFinite(S))return;const _=(m-t.left)**2+(S-t.top)**2;_<s&&(s=_,n=v)}),n<0||s>400){this.hideTooltip();return}const r=this.recordAt(n);if(!r){this.hideTooltip();return}const a=this.paretoRecordIndices[n],o=((d=r.coordinate)==null?void 0:d.credit)??"?",l=r.payload.val_acc??0,c=r.payload.walltime_s??0,h=((f=r.schedule)==null?void 0:f.seed)??"?",u=this.paretoFlags[a]?" · PARETO":"";this.showTooltip(e,`${o} · val_acc ${l.toFixed(3)} · ${c.toFixed(1)}s · seed ${h}${u}`)}showCategoryTooltip(e,t){const n=e.cursor;if(!n||n.left==null||n.top==null){this.hideTooltip();return}const s=Math.round(e.posToVal(n.left,"x"));if(s<0||s>=this.categoryLabels.length){this.hideTooltip();return}const r=this.categoryLabels[s];if(t==="ablation"){const h=this.ablationGroups.find(f=>f.axis==="credit"),u=h==null?void 0:h.metrics.find(f=>f.metric==="val_acc"),d=u==null?void 0:u.arms[s];if(!d){this.hideTooltip();return}this.showTooltip(e,`${r} · ${d.mean.toFixed(3)} ± ${d.std.toFixed(3)} (n=${d.count})${d.at_chance?" · at chance":""}`);return}const a=this.records.filter(h=>h.coordinate.credit===r).map(h=>h.payload.val_acc).filter(h=>typeof h=="number").sort((h,u)=>h-u);if(a.length===0){this.hideTooltip();return}const o=a[Math.floor(a.length*.5)],l=a[Math.floor(a.length*.25)],c=a[Math.floor(a.length*.75)];this.showTooltip(e,`${r} · median ${o.toFixed(3)} · IQR ${(c-l).toFixed(3)} · n=${a.length}`)}download(e){const n={pareto:this.paretoPlot,ablation:this.ablationPlot,variability:this.variabilityPlot}[e];if(!n)return;const s=document.createElement("a");s.download=`computronium-${e}-${Date.now()}.png`,s.href=this.exportImage(n),s.click()}exportImage(e){const t=Array.from(e.root.querySelectorAll("canvas")),n=e.root.getBoundingClientRect(),s=Math.max(...t.map(l=>l.width),1),r=Math.max(...t.map(l=>l.height),1),a=document.createElement("canvas");a.width=s,a.height=r;const o=a.getContext("2d");return o?(o.fillStyle=k.bg,o.fillRect(0,0,s,r),t.forEach(l=>{const c=l.getBoundingClientRect();if(c.width===0||c.height===0)return;const h=l.width/c.width;o.drawImage(l,(c.left-n.left)*h,(c.top-n.top)*h,l.width,l.height)}),a.toDataURL("image/png")):e.ctx.canvas.toDataURL("image/png")}}const Ja=new lE;Zn.register(Ja);function cE(){return`
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
  `}class hE{constructor(){M(this,"name","LiveRail");M(this,"container",null);M(this,"logContainer",null);M(this,"scrollHint",null);M(this,"events",[]);M(this,"maxEvents",50);M(this,"onPipelineEvent",e=>{this.events.unshift(e),this.events.length>this.maxEvents&&this.events.pop(),this.render()});M(this,"onStatusUpdate",e=>{var r,a,o;const t=((r=e==null?void 0:e.data)==null?void 0:r.running_campaigns)??0,n=((a=e==null?void 0:e.data)==null?void 0:a.queued_campaigns)??0,s=(o=this.container)==null?void 0:o.querySelector("#rail-queue");s&&(s.textContent=`${t} running · ${n} queued`)});Jt.register("pipeline_event",this.onPipelineEvent),Jt.register("status_update",this.onStatusUpdate)}async init(){this.container=Ps({id:"live-rail",title:"LIVE RAIL",glyph:"≡",key:tr.rail,body:cE(),dock:"bottom",defaultOpen:!0,className:"live-rail-panel"}),this.logContainer=this.container.querySelector("#rail-log"),this.scrollHint=this.container.querySelector("#rail-scroll-hint"),sr("live-rail","live rail","≡",()=>this.container,tr.rail),sa.onStateChange(e=>this.setConnected(e==="connected")),console.log("[LiveRail] Initialized")}async destroy(){var e;Jt.unregister("pipeline_event",this.onPipelineEvent),Jt.unregister("status_update",this.onStatusUpdate),(e=this.container)==null||e.remove()}setConnected(e){var a;const t=(a=this.container)==null?void 0:a.querySelector("#rail-connection");if(!t)return;const n=t.querySelector(".dot"),s=t.querySelector(".rail-label");if(!n||!s)return;const r=e?k.ok:k.error;n.style.background=r,t.style.background=r+"22",t.style.borderColor=r+"88",t.style.color=r,s.textContent=e?"Connected":"Disconnected"}render(){var t;if(!this.logContainer)return;this.logContainer.innerHTML=this.events.map((n,s)=>{const r=new Date(n.timestamp).toLocaleTimeString(),o={ok:k.ok,warn:k.warn,error:k.error}[n.level]||k.text_secondary;return`
          <span class="rail-event ${s===0?"latest":""}">
            <span class="rail-time">${r}</span>
            <span class="rail-icon" style="color: ${o};">${{ok:"✓",warn:"⚠",error:"✗"}[n.level]??"•"}</span>
            <span class="rail-stage">${n.stage}</span>
            <span class="rail-message">${n.message}</span>
          </span>
        `}).join("");const e=(t=this.container)==null?void 0:t.querySelector("#rail-count");if(e&&(e.textContent=`${this.events.length} events`),this.logContainer.scrollLeft=0,this.scrollHint){const n=this.logContainer.scrollWidth>this.logContainer.clientWidth;this.scrollHint.style.opacity=n?"1":"0"}}}const Pm=new hE;Zn.register(Pm);const uE=4e3,dE={ok:k.text_primary,warn:k.warn,error:k.error};function fE(){return`
    <div id="caption-headline">The dashboard is starting.</div>
    <div id="caption-context"></div>
  `}class pE{constructor(){M(this,"name","Caption");M(this,"container",null);M(this,"headline",null);M(this,"context",null);M(this,"state",[]);M(this,"spoken",null);M(this,"last",null);M(this,"holdTimer",null);M(this,"onNarration",e=>{this.state=(e==null?void 0:e.state)??[],this.render()});M(this,"onEvent",e=>{e!=null&&e.sentence&&this.say(e.sentence,e.level??"ok")});Jt.register("narration",this.onNarration),Jt.register("pipeline_event",this.onEvent)}async init(){this.container=Ps({id:"caption",title:"Caption",glyph:"▤",key:tr.caption,body:fE(),dock:"bottom",defaultOpen:!0,className:"caption-panel"}),this.headline=this.container.querySelector("#caption-headline"),this.context=this.container.querySelector("#caption-context"),sr("caption","caption","▤",()=>this.container,tr.caption),this.render()}async destroy(){var e;Jt.unregister("narration",this.onNarration),Jt.unregister("pipeline_event",this.onEvent),this.holdTimer!==null&&window.clearTimeout(this.holdTimer),(e=this.container)==null||e.remove()}say(e,t="ok"){e&&(this.spoken={text:e,level:t},this.last={text:e,level:t},this.render(),this.holdTimer!==null&&window.clearTimeout(this.holdTimer),this.holdTimer=window.setTimeout(()=>{this.spoken=null,this.holdTimer=null,this.render()},uE))}render(){if(!(!this.headline||!this.context)){if(this.spoken){this.headline.textContent=this.spoken.text,this.headline.style.color=this.colorOf(this.spoken.level),this.context.textContent=this.state.join(" · ");return}if(this.state.length>0){this.headline.textContent=this.state[0],this.headline.style.color=k.text_primary,this.context.textContent=this.state.slice(1).join(" · ");return}if(this.last){this.headline.textContent=this.last.text,this.headline.style.color=this.colorOf(this.last.level),this.context.textContent="";return}this.headline.textContent="The dashboard is starting.",this.headline.style.color=k.text_primary,this.context.textContent=""}}colorOf(e){return dE[e]??k.text_primary}}const Lm=new pE;Zn.register(Lm);function mE(){return`
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
  `}class gE{constructor(){M(this,"name","HUD");M(this,"panel",null);M(this,"modeChip",null);M(this,"connectionPill",null);M(this,"rows",new Map);M(this,"rowElements",new Map);M(this,"claimValue",null);M(this,"claimFill",null);M(this,"sourceValue",null);M(this,"statusData",{});M(this,"resources",{});M(this,"requiredSeeds",0);M(this,"measuredSeeds",0);M(this,"connected",!1);M(this,"animationTime",0);M(this,"onStatusUpdate",e=>{const t=(e==null?void 0:e.data)??e;t&&(this.statusData=t,this.updateQueueRows())});M(this,"onCampaignMetrics",e=>{const t=e==null?void 0:e.data;t&&Kn.observe(e==null?void 0:e.campaign_id,t)});M(this,"onRunChanged",(e,t)=>{var n;t&&(this.resources=t.resources??{},typeof t.required_seeds=="number"&&(this.requiredSeeds=t.required_seeds),this.measuredSeeds=this.resources.seeds_per_arm??((n=t.records)==null?void 0:n.length)??0,this.updateModeChip(t.run),this.updateSource(t.store),this.updateResourceRows(),this.updateClaim())});Jt.register("status_update",this.onStatusUpdate),Jt.register("campaign_metrics",this.onCampaignMetrics),Kn.onChange(this.onRunChanged)}async init(){this.panel=Ps({id:"hud",title:"MISSION CONTROL",glyph:"◱",key:tr.hud,body:mE(),dock:"top",defaultOpen:!0}),this.createModeChip(),this.setupMeters(),sr("hud","mission control","◱",()=>this.panel,tr.hud),sa.onStateChange(e=>{this.connected=e==="connected",this.updateConnection()}),console.log("[HUD] Initialized")}async destroy(){var e,t;Jt.unregister("status_update",this.onStatusUpdate),Jt.unregister("campaign_metrics",this.onCampaignMetrics),(e=this.panel)==null||e.remove(),(t=this.modeChip)==null||t.remove()}setupMeters(){if(!this.panel)return;const e=this.panel.querySelector("#hud-meters");this.addMeter(e,"device","DEVICE","var(--gradient)"),this.addMeter(e,"memory","MEMORY","var(--memory)"),this.addMeter(e,"walltime","WALLTIME","var(--cpu)"),this.addMeter(e,"gpu","GPU","var(--gpu)"),this.addMeter(e,"cpu","CPU","var(--cpu)"),this.addMeter(e,"records","RECORDS","var(--promoted)"),this.claimValue=this.panel.querySelector("#hud-claim"),this.claimFill=this.panel.querySelector("#hud-claim-fill"),this.connectionPill=this.panel.querySelector("#hud-connection"),this.sourceValue=this.panel.querySelector("#hud-source")}addMeter(e,t,n,s){const r=document.createElement("div");r.className="meter-row",r.innerHTML=`
      <div class="meter-label-row">
        <span class="meter-label">${n}</span>
        <span class="meter-value hud-value">—</span>
      </div>
      <div class="meter-bar"><div class="meter-fill hud-fill" style="background: ${s};"></div></div>
    `,e.appendChild(r),this.rows.set(t,{key:t,label:n,value:"",fraction:0,color:s}),this.rowElements.set(t,{fill:r.querySelector(".hud-fill"),value:r.querySelector(".hud-value")})}createModeChip(){const e=document.getElementById("ui-overlay");e&&(this.modeChip=document.createElement("div"),this.modeChip.id="mode-chip",this.modeChip.className="mode-chip",this.modeChip.innerHTML=`
      <div class="mode-label">NO RUN</div>
      <div class="mode-detail"></div>
    `,e.appendChild(this.modeChip))}updateModeChip(e){if(!this.modeChip)return;const t=(e==null?void 0:e.mode)??"NO RUN",n=t==="PREREGISTERED"?k.passed:t==="EXPLORATORY"?k.insufficient:k.text_muted;this.modeChip.style.background=`${n}22`,this.modeChip.style.borderColor=`${n}88`,this.modeChip.style.color=n;const s=this.modeChip.querySelector(".mode-label");s&&(s.textContent=t);const r=this.modeChip.querySelector(".mode-detail");r&&(r.textContent=[e==null?void 0:e.profile,((e==null?void 0:e.tasks)??[]).join(", "),e==null?void 0:e.fidelity].filter(Boolean).join(" · ")),this.modeChip.title=e?`run ${e.run_id??"?"} · objectives: ${(e.objectives??[]).join(", ")||"none"}`:"No run has reported yet"}setMeter(e,t,n){const s=this.rows.get(e),r=this.rowElements.get(e);!s||!r||(s.value=t,s.fraction=Math.max(0,Math.min(1,n)),r.value.textContent=t,r.fill.style.width=`${(s.fraction*100).toFixed(1)}%`)}updateSource(e){if(!this.sourceValue)return;const t=e==null?void 0:e.source;if(!t){this.sourceValue.textContent="—",this.sourceValue.style.color="var(--text-secondary)";return}if(t==="snapshot"){const n=e!=null&&e.published_at?new Date(e.published_at).toLocaleTimeString():"";this.sourceValue.textContent=n?`snapshot ${n}`:"snapshot",this.sourceValue.style.color="var(--insufficient)",this.sourceValue.title="The writer published this copy; it is as fresh as its last publish.";return}this.sourceValue.textContent="live",this.sourceValue.style.color="var(--passed)",this.sourceValue.title="The store itself, read as it is written."}updateQueueRows(){const e=this.statusData;this.setMeter("gpu",e.max_gpus?`${e.used_gpus??0} / ${e.max_gpus}`:"—",e.max_gpus?(e.used_gpus??0)/e.max_gpus:0),this.setMeter("cpu",e.max_cpus?`${e.used_cpus??0} / ${e.max_cpus}`:"—",e.max_cpus?(e.used_cpus??0)/e.max_cpus:0)}updateResourceRows(){const e=this.resources;this.setMeter("device",e.device??"—",e.device?1:0),this.setMeter("memory",e.memory_mb!==void 0?`${e.memory_mb.toFixed(1)} MB`:"—",e.memory_mb!==void 0?Math.min(1,e.memory_mb/2048):0),this.setMeter("walltime",e.walltime_s!==void 0?`${e.walltime_s.toFixed(1)} s`:"—",e.walltime_s!==void 0?Math.min(1,e.walltime_s/120):0),this.setMeter("records",e.records!==void 0?`${e.records}`:"—",e.records!==void 0?Math.min(1,e.records/20):0)}updateClaim(){if(!this.claimValue||!this.claimFill)return;if(this.requiredSeeds<=0){this.claimValue.textContent="—",this.claimFill.style.width="0%";return}const e=Math.max(0,this.requiredSeeds-this.measuredSeeds),t=this.requiredSeeds>0?this.measuredSeeds/this.requiredSeeds:0;this.claimValue.textContent=e>0?`${e} more (${this.requiredSeeds} needed)`:`Ready (${this.requiredSeeds} met)`,this.claimValue.style.color=e>0?"var(--insufficient)":"var(--passed)",this.claimFill.style.width=`${Math.min(100,t*100)}%`,this.claimFill.style.background=e>0?"var(--insufficient)":"var(--passed)"}updateConnection(){if(!this.connectionPill)return;const e=this.connectionPill.querySelector(".dot"),t=this.connectionPill.querySelector("span:last-child"),n=this.connected?"var(--ok)":"var(--error)";e.style.background=n,this.connectionPill.style.background=`${n}22`,this.connectionPill.style.borderColor=`${n}88`,this.connectionPill.style.color=n,t.textContent=this.connected?"live":"offline"}update(e){var n;this.animationTime+=e;const t=.5+.5*Math.sin(this.animationTime*2);(n=this.connectionPill)==null||n.style.setProperty("opacity",`${.75+.25*t}`)}}const yu=new gE;Zn.register(yu);function vE(){const i=Fp(),e=new Map;for(const n of i){const s=n.chord?n.chord.replace("shift+","Shift + ").toUpperCase():n.key?n.key.toUpperCase():"";if(!s)continue;const r=n.group;e.has(r)||e.set(r,[]),e.get(r).push({key:s,description:n.label})}return["Navigation","Panels","Charts","Run Control","Cell Actions","Stage","General"].map(n=>({title:n,items:e.get(n)??[]})).filter(n=>n.items.length>0)}const xE=vE();class _E{constructor(){M(this,"name","HelpOverlay");M(this,"container",null);M(this,"dialog",null);M(this,"isOpen",!1);M(this,"lastFocused",null);M(this,"onKeyDown",e=>{const t=e.target;t&&["INPUT","SELECT","TEXTAREA"].includes(t.tagName)||(e.key==="?"&&!e.shiftKey&&!e.ctrlKey&&!e.metaKey&&!e.altKey&&(e.preventDefault(),this.toggle()),e.key==="Escape"&&this.isOpen&&this.hide())});window.addEventListener("keydown",this.onKeyDown)}async init(){this.createOverlay(),sr("help-overlay","help","?",()=>this.container),console.log("[HelpOverlay] Initialized")}async destroy(){var e;window.removeEventListener("keydown",this.onKeyDown),(e=this.container)==null||e.remove()}createOverlay(){if(!document.getElementById("ui-overlay"))return;this.container=document.createElement("div"),this.container.id="help-overlay",this.container.setAttribute("role","dialog"),this.container.setAttribute("aria-modal","true"),this.container.setAttribute("aria-labelledby","help-title"),this.container.style.cssText=`
      position: fixed;
      inset: 0;
      background: rgba(10, 14, 20, 0.92);
      z-index: 1000;
      display: none;
      align-items: center;
      justify-content: center;
      opacity: 0;
      transition: opacity 0.2s ease;
    `;const t=xE.map(n=>`
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
    `,this.dialog=this.container.querySelector("div"),this.container.addEventListener("click",n=>{n.target===this.container&&this.hide()})}toggle(){this.isOpen?this.hide():this.show()}show(){!this.container||!this.dialog||(this.lastFocused=document.activeElement,this.container.style.display="flex",this.trapFocus(),requestAnimationFrame(()=>{this.container.style.opacity="1",this.dialog&&(this.dialog.style.transform="scale(1)")}),this.isOpen=!0,document.body.style.overflow="hidden")}hide(){!this.container||!this.dialog||(this.container.style.opacity="0",this.dialog.style.transform="scale(0.95)",setTimeout(()=>{this.container&&(this.container.style.display="none")},200),this.isOpen=!1,document.body.style.overflow="",this.lastFocused&&this.lastFocused.focus())}trapFocus(){var a;if(!this.dialog)return;const e=this.dialog.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');if(e.length===0)return;const t=e[0],n=e[e.length-1],s=o=>{o.key==="Tab"&&(o.shiftKey?document.activeElement===t&&(o.preventDefault(),n.focus()):document.activeElement===n&&(o.preventDefault(),t.focus()))};this.dialog.addEventListener("keydown",s);const r=()=>{var o;(o=this.dialog)==null||o.removeEventListener("keydown",s)};(a=this.container)==null||a.addEventListener("transitionend",r,{once:!0}),t.focus()}}const Sl=new _E;Zn.register(Sl);const yE=/swiftshader|llvmpipe|software|basic render/i;function SE(){const i=bE();return{software:i,fps:i?12:60,shadows:!i,antialias:!i}}function bE(){try{const i=document.createElement("canvas"),e=i.getContext("webgl2")??i.getContext("webgl");if(!e)return!0;const t=e.getExtension("WEBGL_debug_renderer_info"),n=String(t?e.getParameter(t.UNMASKED_RENDERER_WEBGL):e.getParameter(e.RENDERER));return yE.test(n)}catch{return!0}}window.addEventListener("error",i=>{var e;console.error("[Global Error]",i.error),Im(((e=i.error)==null?void 0:e.message)||"Unknown error")});window.addEventListener("unhandledrejection",i=>{var e;console.error("[Unhandled Rejection]",i.reason),Im(((e=i.reason)==null?void 0:e.message)||"Unhandled promise rejection")});let Ki=null;function Dm(i="Initializing dashboard..."){const e=document.getElementById("ui-overlay");e&&(Ki=document.createElement("div"),Ki.id="global-loading",Ki.className="global-loading",Ki.innerHTML=`
    <div class="global-loading-spinner"></div>
    <div class="global-loading-text">${i}</div>
  `,e.appendChild(Ki))}function Zf(){Ki==null||Ki.remove(),Ki=null}function Im(i){var n;const e=document.getElementById("ui-overlay");if(!e)return;const t=document.createElement("div");t.id="global-error",t.className="global-error",t.innerHTML=`
    <span>✗</span>
    <span>${i}</span>
    <button class="global-error-close">&times;</button>
  `,(n=t.querySelector(".global-error-close"))==null||n.addEventListener("click",()=>{t.remove()}),e.appendChild(t),setTimeout(()=>t==null?void 0:t.remove(),1e4)}sa.connect();Dm("Connecting to dashboard...");sa.waitForConnection(15e3).then(i=>{i?Zf():(Dm("Connection timeout — retrying..."),sa.onStateChange(e=>{e==="connected"&&Zf()}))});document.addEventListener("DOMContentLoaded",async()=>{await la.init(),Mn("chart-pareto",()=>Ja.showTab("pareto")),Mn("chart-ablation",()=>Ja.showTab("ablation")),Mn("chart-variability",()=>Ja.showTab("variability")),Mn("control-play",()=>Ya.togglePlay()),Mn("control-step",()=>Ya.step()),Mn("control-stop",()=>Ya.stop()),Mn("control-panel",()=>$t.toggle("control-panel")),Mn("panel-hud",()=>$t.toggle("hud")),Mn("panel-rail",()=>$t.toggle("live-rail")),Mn("panel-caption",()=>$t.toggle("caption")),Mn("panel-legend",()=>$t.toggle("legend")),Mn("view-cycle",()=>no.cycle()),Mn("cell-replicate",()=>window.dispatchEvent(new CustomEvent("cell-action-replicate"))),Mn("cell-preregister",()=>window.dispatchEvent(new CustomEvent("cell-action-preregister"))),Mn("cell-quest",()=>window.dispatchEvent(new CustomEvent("cell-action-quest"))),Mn("help",()=>Sl.toggle()),Mn("escape",()=>{ca.hasCellSelected()?ca.hide():Sl.hide()})});const Um=new Map,Nm=new Map;for(const i of ir)i.key&&Um.set(i.key.toLowerCase(),i),i.chord&&Nm.set(i.chord.toLowerCase(),i);window.addEventListener("keydown",i=>{if(i.metaKey||i.ctrlKey||i.altKey)return;const e=i.target;if(e&&["INPUT","SELECT","TEXTAREA"].includes(e.tagName))return;const t=i.key.toLowerCase();if(i.shiftKey){const s=`shift+${t}`,r=Nm.get(s);if(r){if(r.when==="cell-selected"&&!ca.hasCellSelected())return;r.run();return}}const n=Um.get(t);if(n){if(n.when==="cell-selected"&&!ca.hasCellSelected())return;n.run();return}});const ME=document.getElementById("dashboard-canvas"),ya=SE(),li=new MS({canvas:ME,antialias:ya.antialias,alpha:!0,powerPreference:"high-performance"});li.setSize(window.innerWidth,window.innerHeight);li.setPixelRatio(ya.software?1:Math.min(window.devicePixelRatio,2));li.shadowMap.enabled=ya.shadows;li.shadowMap.type=ep;li.toneMapping=np;li.toneMappingExposure=1.2;const as=new Lp;as.background=new it(658964);as.fog=new eu(658964,.015);const As=new Rn(60,window.innerWidth/window.innerHeight,.1,200);As.position.set(3.3,4.4,8.8);As.lookAt(0,1,.1);const ki=new VS(As,li.domElement);ki.target.set(0,1,.1);ki.enableDamping=!0;ki.dampingFactor=.05;ki.enablePan=!0;ki.minDistance=5;ki.maxDistance=80;ki.maxPolarAngle=Math.PI/2-.05;$S({scene:as,camera:As,renderer:li,controls:ki});const wE=new DS(4473958,.6);as.add(wE);const Ti=new LS(16777215,1.2);Ti.position.set(10,20,10);Ti.castShadow=ya.shadows;Ti.shadow.mapSize.width=2048;Ti.shadow.mapSize.height=2048;Ti.shadow.camera.near=1;Ti.shadow.camera.far=50;Ti.shadow.camera.left=-20;Ti.shadow.camera.right=20;Ti.shadow.camera.top=20;Ti.shadow.camera.bottom=-20;as.add(Ti);const EE=new CS(8956671,2236979,.5);as.add(EE);const Su=new US(8,8,2371648,1449256);Su.position.y=-.01;const Om=Su.material;Om.transparent=!0;Om.opacity=.35;as.add(Su);function TE(){As.aspect=window.innerWidth/window.innerHeight,As.updateProjectionMatrix(),li.setSize(window.innerWidth,window.innerHeight),li.setPixelRatio(ya.software?1:Math.min(window.devicePixelRatio,2))}window.addEventListener("resize",TE);const AE=1e3/ya.fps;let $c=0;function Fm(i){if(requestAnimationFrame(Fm),i-$c<AE)return;const e=(i-$c)/1e3;$c=i,ki.update(),Ks.update(e),yu.update(e),li.render(as,As)}requestAnimationFrame(Fm);window.__DASHBOARD__={scene:as,camera:As,renderer:li,controls:ki,discoveryMap:Ks,cellDrawer:ca,plotter:Ja,liveRail:Pm,caption:Lm,hud:yu,helpOverlay:Sl,viewSwitcher:no,controlBar:Ya,controlPanel:Gp,panels:$t,layout:la,wsClient:sa,router:Jt,bindings:{list:()=>Fp().map(i=>({id:i.id,label:i.label,group:i.group,key:i.key}))}};console.log("🚀 Computronium Dashboard initialized");
//# sourceMappingURL=dashboard.js.map
