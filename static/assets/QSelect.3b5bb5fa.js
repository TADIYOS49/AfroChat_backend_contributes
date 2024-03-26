import{u as Je,b as At,e as Et,d as Tt,g as Xt,a as Yt,c as Gt,f as mt,h as Jt}from"./use-key-composition.a30091f4.js";import{bF as Ze,r as L,co as zt,c7 as He,aC as ue,cp as ht,w as Y,o as Zt,aF as qe,g as De,cq as el,bM as Ye,c9 as tl,bQ as ll,c as V,cr as nl,bL as ul,h as M,bH as ol,bl as il,cs as al,c6 as me,bK as rl,c5 as sl,aE as cl,aH as dl,aD as fl,aG as vl,aM as ml,b$ as hl,ct as Te,c2 as pe,c0 as gl,bR as Sl}from"./index.9318a740.js";import{p as gt,u as yl,a as bl,b as wl,c as xl,d as Cl,e as pl,f as Vl,g as kl,h as Ml,r as Al,i as St,j as El,k as Tl,Q as zl,l as Hl}from"./QDialog.05df106c.js";import{Q as ql}from"./QItem.19d95841.js";import{c as Fl,Q as Il}from"./selection.938e0258.js";import{Q as Ol}from"./QItemLabel.f5ebb189.js";import{u as Ll,a as Bl}from"./use-dark.bbec077c.js";import{n as yt}from"./chat-store.775f2457.js";var Pl=Ze({name:"QField",inheritAttrs:!1,props:Je,emits:At,setup(){return Et(Tt())}});const Rl={target:{default:!0},noParentEvent:Boolean,contextMenu:Boolean};function _l({showing:e,avoidEmit:n,configureAnchorEl:u}){const{props:o,proxy:v,emit:i}=De(),m=L(null);let h=null;function g(s){return m.value===null?!1:s===void 0||s.touches===void 0||s.touches.length<=1}const y={};u===void 0&&(Object.assign(y,{hide(s){v.hide(s)},toggle(s){v.toggle(s),s.qAnchorHandled=!0},toggleKey(s){zt(s,13)===!0&&y.toggle(s)},contextClick(s){v.hide(s),He(s),ue(()=>{v.show(s),s.qAnchorHandled=!0})},prevent:He,mobileTouch(s){if(y.mobileCleanup(s),g(s)!==!0)return;v.hide(s),m.value.classList.add("non-selectable");const S=s.target;ht(y,"anchor",[[S,"touchmove","mobileCleanup","passive"],[S,"touchend","mobileCleanup","passive"],[S,"touchcancel","mobileCleanup","passive"],[m.value,"contextmenu","prevent","notPassive"]]),h=setTimeout(()=>{h=null,v.show(s),s.qAnchorHandled=!0},300)},mobileCleanup(s){m.value.classList.remove("non-selectable"),h!==null&&(clearTimeout(h),h=null),e.value===!0&&s!==void 0&&Fl()}}),u=function(s=o.contextMenu){if(o.noParentEvent===!0||m.value===null)return;let S;s===!0?v.$q.platform.is.mobile===!0?S=[[m.value,"touchstart","mobileTouch","passive"]]:S=[[m.value,"mousedown","hide","passive"],[m.value,"contextmenu","contextClick","notPassive"]]:S=[[m.value,"click","toggle","passive"],[m.value,"keyup","toggleKey","passive"]],ht(y,"anchor",S)});function f(){el(y,"anchor")}function w(s){for(m.value=s;m.value.classList.contains("q-anchor--skip");)m.value=m.value.parentNode;u()}function C(){if(o.target===!1||o.target===""||v.$el.parentNode===null)m.value=null;else if(o.target===!0)w(v.$el.parentNode);else{let s=o.target;if(typeof o.target=="string")try{s=document.querySelector(o.target)}catch{s=void 0}s!=null?(m.value=s.$el||s,u()):(m.value=null,console.error(`Anchor: target "${o.target}" not found`))}}return Y(()=>o.contextMenu,s=>{m.value!==null&&(f(),u(s))}),Y(()=>o.target,()=>{m.value!==null&&f(),C()}),Y(()=>o.noParentEvent,s=>{m.value!==null&&(s===!0?f():u())}),Zt(()=>{C(),n!==!0&&o.modelValue===!0&&m.value===null&&i("update:modelValue",!1)}),qe(()=>{h!==null&&clearTimeout(h),f()}),{anchorEl:m,canShow:g,anchorEvents:y}}function Dl(e,n){const u=L(null);let o;function v(h,g){const y=`${g!==void 0?"add":"remove"}EventListener`,f=g!==void 0?g:o;h!==window&&h[y]("scroll",f,Ye.passive),window[y]("scroll",f,Ye.passive),o=g}function i(){u.value!==null&&(v(u.value),u.value=null)}const m=Y(()=>e.noParentEvent,()=>{u.value!==null&&(i(),n())});return qe(m),{localScrollTarget:u,unconfigureScrollTarget:i,changeScrollEvent:v}}const{notPassiveCapture:Pe}=Ye,he=[];function Re(e){const n=e.target;if(n===void 0||n.nodeType===8||n.classList.contains("no-pointer-events")===!0)return;let u=gt.length-1;for(;u>=0;){const o=gt[u].$;if(o.type.name==="QTooltip"){u--;continue}if(o.type.name!=="QDialog")break;if(o.props.seamless!==!0)return;u--}for(let o=he.length-1;o>=0;o--){const v=he[o];if((v.anchorEl.value===null||v.anchorEl.value.contains(n)===!1)&&(n===document.body||v.innerRef.value!==null&&v.innerRef.value.contains(n)===!1))e.qClickOutside=!0,v.onClickOutside(e);else return}}function Wl(e){he.push(e),he.length===1&&(document.addEventListener("mousedown",Re,Pe),document.addEventListener("touchstart",Re,Pe))}function bt(e){const n=he.findIndex(u=>u===e);n>-1&&(he.splice(n,1),he.length===0&&(document.removeEventListener("mousedown",Re,Pe),document.removeEventListener("touchstart",Re,Pe)))}let wt,xt;function Ct(e){const n=e.split(" ");return n.length!==2?!1:["top","center","bottom"].includes(n[0])!==!0?(console.error("Anchor/Self position must start with one of top/center/bottom"),!1):["left","middle","right","start","end"].includes(n[1])!==!0?(console.error("Anchor/Self position must end with one of left/middle/right/start/end"),!1):!0}function $l(e){return e?!(e.length!==2||typeof e[0]!="number"||typeof e[1]!="number"):!0}const Ge={"start#ltr":"left","start#rtl":"right","end#ltr":"right","end#rtl":"left"};["left","middle","right"].forEach(e=>{Ge[`${e}#ltr`]=e,Ge[`${e}#rtl`]=e});function pt(e,n){const u=e.split(" ");return{vertical:u[0],horizontal:Ge[`${u[1]}#${n===!0?"rtl":"ltr"}`]}}function Kl(e,n){let{top:u,left:o,right:v,bottom:i,width:m,height:h}=e.getBoundingClientRect();return n!==void 0&&(u-=n[1],o-=n[0],i+=n[1],v+=n[0],m+=n[0],h+=n[1]),{top:u,bottom:i,height:h,left:o,right:v,width:m,middle:o+(v-o)/2,center:u+(i-u)/2}}function jl(e,n,u){let{top:o,left:v}=e.getBoundingClientRect();return o+=n.top,v+=n.left,u!==void 0&&(o+=u[1],v+=u[0]),{top:o,bottom:o+1,height:1,left:v,right:v+1,width:1,middle:v,center:o}}function Nl(e,n){return{top:0,center:n/2,bottom:n,left:0,middle:e/2,right:e}}function Vt(e,n,u,o){return{top:e[u.vertical]-n[o.vertical],left:e[u.horizontal]-n[o.horizontal]}}function Ht(e,n=0){if(e.targetEl===null||e.anchorEl===null||n>5)return;if(e.targetEl.offsetHeight===0||e.targetEl.offsetWidth===0){setTimeout(()=>{Ht(e,n+1)},10);return}const{targetEl:u,offset:o,anchorEl:v,anchorOrigin:i,selfOrigin:m,absoluteOffset:h,fit:g,cover:y,maxHeight:f,maxWidth:w}=e;if(tl.is.ios===!0&&window.visualViewport!==void 0){const z=document.body.style,{offsetLeft:R,offsetTop:_}=window.visualViewport;R!==wt&&(z.setProperty("--q-pe-left",R+"px"),wt=R),_!==xt&&(z.setProperty("--q-pe-top",_+"px"),xt=_)}const{scrollLeft:C,scrollTop:s}=u,S=h===void 0?Kl(v,y===!0?[0,0]:o):jl(v,h,o);Object.assign(u.style,{top:0,left:0,minWidth:null,minHeight:null,maxWidth:w||"100vw",maxHeight:f||"100vh",visibility:"visible"});const{offsetWidth:W,offsetHeight:F}=u,{elWidth:j,elHeight:U}=g===!0||y===!0?{elWidth:Math.max(S.width,W),elHeight:y===!0?Math.max(S.height,F):F}:{elWidth:W,elHeight:F};let A={maxWidth:w,maxHeight:f};(g===!0||y===!0)&&(A.minWidth=S.width+"px",y===!0&&(A.minHeight=S.height+"px")),Object.assign(u.style,A);const E=Nl(j,U);let I=Vt(S,E,i,m);if(h===void 0||o===void 0)Ue(I,S,E,i,m);else{const{top:z,left:R}=I;Ue(I,S,E,i,m);let _=!1;if(I.top!==z){_=!0;const N=2*o[1];S.center=S.top-=N,S.bottom-=N+2}if(I.left!==R){_=!0;const N=2*o[0];S.middle=S.left-=N,S.right-=N+2}_===!0&&(I=Vt(S,E,i,m),Ue(I,S,E,i,m))}A={top:I.top+"px",left:I.left+"px"},I.maxHeight!==void 0&&(A.maxHeight=I.maxHeight+"px",S.height>I.maxHeight&&(A.minHeight=A.maxHeight)),I.maxWidth!==void 0&&(A.maxWidth=I.maxWidth+"px",S.width>I.maxWidth&&(A.minWidth=A.maxWidth)),Object.assign(u.style,A),u.scrollTop!==s&&(u.scrollTop=s),u.scrollLeft!==C&&(u.scrollLeft=C)}function Ue(e,n,u,o,v){const i=u.bottom,m=u.right,h=ll(),g=window.innerHeight-h,y=document.body.clientWidth;if(e.top<0||e.top+i>g)if(v.vertical==="center")e.top=n[o.vertical]>g/2?Math.max(0,g-i):0,e.maxHeight=Math.min(i,g);else if(n[o.vertical]>g/2){const f=Math.min(g,o.vertical==="center"?n.center:o.vertical===v.vertical?n.bottom:n.top);e.maxHeight=Math.min(i,f),e.top=Math.max(0,f-i)}else e.top=Math.max(0,o.vertical==="center"?n.center:o.vertical===v.vertical?n.top:n.bottom),e.maxHeight=Math.min(i,g-e.top);if(e.left<0||e.left+m>y)if(e.maxWidth=Math.min(m,y),v.horizontal==="middle")e.left=n[o.horizontal]>y/2?Math.max(0,y-m):0;else if(n[o.horizontal]>y/2){const f=Math.min(y,o.horizontal==="middle"?n.middle:o.horizontal===v.horizontal?n.right:n.left);e.maxWidth=Math.min(m,f),e.left=Math.max(0,f-e.maxWidth)}else e.left=Math.max(0,o.horizontal==="middle"?n.middle:o.horizontal===v.horizontal?n.left:n.right),e.maxWidth=Math.min(m,y-e.left)}var Ql=Ze({name:"QMenu",inheritAttrs:!1,props:{...Rl,...yl,...Ll,...bl,persistent:Boolean,autoClose:Boolean,separateClosePopup:Boolean,noRouteDismiss:Boolean,noRefocus:Boolean,noFocus:Boolean,fit:Boolean,cover:Boolean,square:Boolean,anchor:{type:String,validator:Ct},self:{type:String,validator:Ct},offset:{type:Array,validator:$l},scrollTarget:{default:void 0},touchPosition:Boolean,maxHeight:{type:String,default:null},maxWidth:{type:String,default:null}},emits:[...wl,"click","escapeKey"],setup(e,{slots:n,emit:u,attrs:o}){let v=null,i,m,h;const g=De(),{proxy:y}=g,{$q:f}=y,w=L(null),C=L(!1),s=V(()=>e.persistent!==!0&&e.noRouteDismiss!==!0),S=Bl(e,f),{registerTick:W,removeTick:F}=xl(),{registerTimeout:j}=Cl(),{transitionProps:U,transitionStyle:A}=pl(e),{localScrollTarget:E,changeScrollEvent:I,unconfigureScrollTarget:z}=Dl(e,p),{anchorEl:R,canShow:_}=_l({showing:C}),{hide:N}=Vl({showing:C,canShow:_,handleShow:se,handleHide:l,hideOnRouteChange:s,processOnMount:!0}),{showPortal:J,hidePortal:ae,renderPortal:$}=kl(g,w,B,"menu"),ne={anchorEl:R,innerRef:w,onClickOutside(a){if(e.persistent!==!0&&C.value===!0)return N(a),(a.type==="touchstart"||a.target.classList.contains("q-dialog__backdrop"))&&me(a),!0}},re=V(()=>pt(e.anchor||(e.cover===!0?"center middle":"bottom start"),f.lang.rtl)),oe=V(()=>e.cover===!0?re.value:pt(e.self||"top start",f.lang.rtl)),X=V(()=>(e.square===!0?" q-menu--square":"")+(S.value===!0?" q-menu--dark q-dark":"")),ke=V(()=>e.autoClose===!0?{onClick:H}:{}),ie=V(()=>C.value===!0&&e.persistent!==!0);Y(ie,a=>{a===!0?(Tl(k),Wl(ne)):(St(k),bt(ne))});function Z(){Xt(()=>{let a=w.value;a&&a.contains(document.activeElement)!==!0&&(a=a.querySelector("[autofocus][tabindex], [data-autofocus][tabindex]")||a.querySelector("[autofocus] [tabindex], [data-autofocus] [tabindex]")||a.querySelector("[autofocus], [data-autofocus]")||a,a.focus({preventScroll:!0}))})}function se(a){if(v=e.noRefocus===!1?document.activeElement:null,Ml(O),J(),p(),i=void 0,a!==void 0&&(e.touchPosition||e.contextMenu)){const D=nl(a);if(D.left!==void 0){const{top:ee,left:ge}=R.value.getBoundingClientRect();i={left:D.left-ge,top:D.top-ee}}}m===void 0&&(m=Y(()=>f.screen.width+"|"+f.screen.height+"|"+e.self+"|"+e.anchor+"|"+f.lang.rtl,x)),e.noFocus!==!0&&document.activeElement.blur(),W(()=>{x(),e.noFocus!==!0&&Z()}),j(()=>{f.platform.is.ios===!0&&(h=e.autoClose,w.value.click()),x(),J(!0),u("show",a)},e.transitionDuration)}function l(a){F(),ae(),c(!0),v!==null&&(a===void 0||a.qClickOutside!==!0)&&(((a&&a.type.indexOf("key")===0?v.closest('[tabindex]:not([tabindex^="-"])'):void 0)||v).focus(),v=null),j(()=>{ae(!0),u("hide",a)},e.transitionDuration)}function c(a){i=void 0,m!==void 0&&(m(),m=void 0),(a===!0||C.value===!0)&&(Al(O),z(),bt(ne),St(k)),a!==!0&&(v=null)}function p(){(R.value!==null||e.scrollTarget!==void 0)&&(E.value=ul(R.value,e.scrollTarget),I(E.value,x))}function H(a){h!==!0?(El(y,a),u("click",a)):h=!1}function O(a){ie.value===!0&&e.noFocus!==!0&&al(w.value,a.target)!==!0&&Z()}function k(a){u("escapeKey"),N(a)}function x(){Ht({targetEl:w.value,offset:e.offset,anchorEl:R.value,anchorOrigin:re.value,selfOrigin:oe.value,absoluteOffset:i,fit:e.fit,cover:e.cover,maxHeight:e.maxHeight,maxWidth:e.maxWidth})}function B(){return M(il,U.value,()=>C.value===!0?M("div",{role:"menu",...o,ref:w,tabindex:-1,class:["q-menu q-position-engine scroll"+X.value,o.class],style:[o.style,A.value],...ke.value},ol(n.default)):null)}return qe(c),Object.assign(y,{focus:Z,updatePosition:x}),$}});let _e=!1;{const e=document.createElement("div");e.setAttribute("dir","rtl"),Object.assign(e.style,{width:"1px",height:"1px",overflow:"auto"});const n=document.createElement("div");Object.assign(n.style,{width:"1000px",height:"1px"}),document.body.appendChild(e),e.appendChild(n),e.scrollLeft=-1e3,_e=e.scrollLeft>=0,e.remove()}const G=1e3,Ul=["start","center","end","start-force","center-force","end-force"],qt=Array.prototype.filter,Xl=window.getComputedStyle(document.body).overflowAnchor===void 0?rl:function(e,n){e!==null&&(e._qOverflowAnimationFrame!==void 0&&cancelAnimationFrame(e._qOverflowAnimationFrame),e._qOverflowAnimationFrame=requestAnimationFrame(()=>{if(e===null)return;e._qOverflowAnimationFrame=void 0;const u=e.children||[];qt.call(u,v=>v.dataset&&v.dataset.qVsAnchor!==void 0).forEach(v=>{delete v.dataset.qVsAnchor});const o=u[n];o&&o.dataset&&(o.dataset.qVsAnchor="")}))};function Ve(e,n){return e+n}function Xe(e,n,u,o,v,i,m,h){const g=e===window?document.scrollingElement||document.documentElement:e,y=v===!0?"offsetWidth":"offsetHeight",f={scrollStart:0,scrollViewSize:-m-h,scrollMaxSize:0,offsetStart:-m,offsetEnd:-h};if(v===!0?(e===window?(f.scrollStart=window.pageXOffset||window.scrollX||document.body.scrollLeft||0,f.scrollViewSize+=document.documentElement.clientWidth):(f.scrollStart=g.scrollLeft,f.scrollViewSize+=g.clientWidth),f.scrollMaxSize=g.scrollWidth,i===!0&&(f.scrollStart=(_e===!0?f.scrollMaxSize-f.scrollViewSize:0)-f.scrollStart)):(e===window?(f.scrollStart=window.pageYOffset||window.scrollY||document.body.scrollTop||0,f.scrollViewSize+=document.documentElement.clientHeight):(f.scrollStart=g.scrollTop,f.scrollViewSize+=g.clientHeight),f.scrollMaxSize=g.scrollHeight),u!==null)for(let w=u.previousElementSibling;w!==null;w=w.previousElementSibling)w.classList.contains("q-virtual-scroll--skip")===!1&&(f.offsetStart+=w[y]);if(o!==null)for(let w=o.nextElementSibling;w!==null;w=w.nextElementSibling)w.classList.contains("q-virtual-scroll--skip")===!1&&(f.offsetEnd+=w[y]);if(n!==e){const w=g.getBoundingClientRect(),C=n.getBoundingClientRect();v===!0?(f.offsetStart+=C.left-w.left,f.offsetEnd-=C.width):(f.offsetStart+=C.top-w.top,f.offsetEnd-=C.height),e!==window&&(f.offsetStart+=f.scrollStart),f.offsetEnd+=f.scrollMaxSize-f.offsetStart}return f}function kt(e,n,u,o){n==="end"&&(n=(e===window?document.body:e)[u===!0?"scrollWidth":"scrollHeight"]),e===window?u===!0?(o===!0&&(n=(_e===!0?document.body.scrollWidth-document.documentElement.clientWidth:0)-n),window.scrollTo(n,window.pageYOffset||window.scrollY||document.body.scrollTop||0)):window.scrollTo(window.pageXOffset||window.scrollX||document.body.scrollLeft||0,n):u===!0?(o===!0&&(n=(_e===!0?e.scrollWidth-e.offsetWidth:0)-n),e.scrollLeft=n):e.scrollTop=n}function ze(e,n,u,o){if(u>=o)return 0;const v=n.length,i=Math.floor(u/G),m=Math.floor((o-1)/G)+1;let h=e.slice(i,m).reduce(Ve,0);return u%G!==0&&(h-=n.slice(i*G,u).reduce(Ve,0)),o%G!==0&&o!==v&&(h-=n.slice(o,m*G).reduce(Ve,0)),h}const Yl={virtualScrollSliceSize:{type:[Number,String],default:null},virtualScrollSliceRatioBefore:{type:[Number,String],default:1},virtualScrollSliceRatioAfter:{type:[Number,String],default:1},virtualScrollItemSize:{type:[Number,String],default:24},virtualScrollStickySizeStart:{type:[Number,String],default:0},virtualScrollStickySizeEnd:{type:[Number,String],default:0},tableColspan:[Number,String]},Gl={virtualScrollHorizontal:Boolean,onVirtualScroll:Function,...Yl};function Jl({virtualScrollLength:e,getVirtualScrollTarget:n,getVirtualScrollEl:u,virtualScrollItemSizeComputed:o}){const v=De(),{props:i,emit:m,proxy:h}=v,{$q:g}=h;let y,f,w,C=[],s;const S=L(0),W=L(0),F=L({}),j=L(null),U=L(null),A=L(null),E=L({from:0,to:0}),I=V(()=>i.tableColspan!==void 0?i.tableColspan:100);o===void 0&&(o=V(()=>i.virtualScrollItemSize));const z=V(()=>o.value+";"+i.virtualScrollHorizontal),R=V(()=>z.value+";"+i.virtualScrollSliceRatioBefore+";"+i.virtualScrollSliceRatioAfter);Y(R,()=>{X()}),Y(z,_);function _(){oe(f,!0)}function N(l){oe(l===void 0?f:l)}function J(l,c){const p=n();if(p==null||p.nodeType===8)return;const H=Xe(p,u(),j.value,U.value,i.virtualScrollHorizontal,g.lang.rtl,i.virtualScrollStickySizeStart,i.virtualScrollStickySizeEnd);w!==H.scrollViewSize&&X(H.scrollViewSize),$(p,H,Math.min(e.value-1,Math.max(0,parseInt(l,10)||0)),0,Ul.indexOf(c)>-1?c:f>-1&&l>f?"end":"start")}function ae(){const l=n();if(l==null||l.nodeType===8)return;const c=Xe(l,u(),j.value,U.value,i.virtualScrollHorizontal,g.lang.rtl,i.virtualScrollStickySizeStart,i.virtualScrollStickySizeEnd),p=e.value-1,H=c.scrollMaxSize-c.offsetStart-c.offsetEnd-W.value;if(y===c.scrollStart)return;if(c.scrollMaxSize<=0){$(l,c,0,0);return}w!==c.scrollViewSize&&X(c.scrollViewSize),ne(E.value.from);const O=Math.floor(c.scrollMaxSize-Math.max(c.scrollViewSize,c.offsetEnd)-Math.min(s[p],c.scrollViewSize/2));if(O>0&&Math.ceil(c.scrollStart)>=O){$(l,c,p,c.scrollMaxSize-c.offsetEnd-C.reduce(Ve,0));return}let k=0,x=c.scrollStart-c.offsetStart,B=x;if(x<=H&&x+c.scrollViewSize>=S.value)x-=S.value,k=E.value.from,B=x;else for(let a=0;x>=C[a]&&k<p;a++)x-=C[a],k+=G;for(;x>0&&k<p;)x-=s[k],x>-c.scrollViewSize?(k++,B=x):B=s[k]+x;$(l,c,k,B)}function $(l,c,p,H,O){const k=typeof O=="string"&&O.indexOf("-force")>-1,x=k===!0?O.replace("-force",""):O,B=x!==void 0?x:"start";let a=Math.max(0,p-F.value[B]),D=a+F.value.total;D>e.value&&(D=e.value,a=Math.max(0,D-F.value.total)),y=c.scrollStart;const ee=a!==E.value.from||D!==E.value.to;if(ee===!1&&x===void 0){ie(p);return}const{activeElement:ge}=document,te=A.value;ee===!0&&te!==null&&te!==ge&&te.contains(ge)===!0&&(te.addEventListener("focusout",re),setTimeout(()=>{te!==null&&te.removeEventListener("focusout",re)})),Xl(te,p-a);const Fe=x!==void 0?s.slice(a,p).reduce(Ve,0):0;if(ee===!0){const ce=D>=E.value.from&&a<=E.value.to?E.value.to:D;E.value={from:a,to:ce},S.value=ze(C,s,0,a),W.value=ze(C,s,D,e.value),requestAnimationFrame(()=>{E.value.to!==D&&y===c.scrollStart&&(E.value={from:E.value.from,to:D},W.value=ze(C,s,D,e.value))})}requestAnimationFrame(()=>{if(y!==c.scrollStart)return;ee===!0&&ne(a);const ce=s.slice(a,p).reduce(Ve,0),de=ce+c.offsetStart+S.value,Ie=de+s[p];let Me=de+H;if(x!==void 0){const We=ce-Fe,Ae=c.scrollStart+We;Me=k!==!0&&Ae<de&&Ie<Ae+c.scrollViewSize?Ae:x==="end"?Ie-c.scrollViewSize:de-(x==="start"?0:Math.round((c.scrollViewSize-s[p])/2))}y=Me,kt(l,Me,i.virtualScrollHorizontal,g.lang.rtl),ie(p)})}function ne(l){const c=A.value;if(c){const p=qt.call(c.children,a=>a.classList&&a.classList.contains("q-virtual-scroll--skip")===!1),H=p.length,O=i.virtualScrollHorizontal===!0?a=>a.getBoundingClientRect().width:a=>a.offsetHeight;let k=l,x,B;for(let a=0;a<H;){for(x=O(p[a]),a++;a<H&&p[a].classList.contains("q-virtual-scroll--with-prev")===!0;)x+=O(p[a]),a++;B=x-s[k],B!==0&&(s[k]+=B,C[Math.floor(k/G)]+=B),k++}}}function re(){A.value!==null&&A.value!==void 0&&A.value.focus()}function oe(l,c){const p=1*o.value;(c===!0||Array.isArray(s)===!1)&&(s=[]);const H=s.length;s.length=e.value;for(let k=e.value-1;k>=H;k--)s[k]=p;const O=Math.floor((e.value-1)/G);C=[];for(let k=0;k<=O;k++){let x=0;const B=Math.min((k+1)*G,e.value);for(let a=k*G;a<B;a++)x+=s[a];C.push(x)}f=-1,y=void 0,S.value=ze(C,s,0,E.value.from),W.value=ze(C,s,E.value.to,e.value),l>=0?(ne(E.value.from),ue(()=>{J(l)})):Z()}function X(l){if(l===void 0&&typeof window!="undefined"){const x=n();x!=null&&x.nodeType!==8&&(l=Xe(x,u(),j.value,U.value,i.virtualScrollHorizontal,g.lang.rtl,i.virtualScrollStickySizeStart,i.virtualScrollStickySizeEnd).scrollViewSize)}w=l;const c=parseFloat(i.virtualScrollSliceRatioBefore)||0,p=parseFloat(i.virtualScrollSliceRatioAfter)||0,H=1+c+p,O=l===void 0||l<=0?1:Math.ceil(l/o.value),k=Math.max(1,O,Math.ceil((i.virtualScrollSliceSize>0?i.virtualScrollSliceSize:10)/H));F.value={total:Math.ceil(k*H),start:Math.ceil(k*c),center:Math.ceil(k*(.5+c)),end:Math.ceil(k*(1+c)),view:O}}function ke(l,c){const p=i.virtualScrollHorizontal===!0?"width":"height",H={["--q-virtual-scroll-item-"+p]:o.value+"px"};return[l==="tbody"?M(l,{class:"q-virtual-scroll__padding",key:"before",ref:j},[M("tr",[M("td",{style:{[p]:`${S.value}px`,...H},colspan:I.value})])]):M(l,{class:"q-virtual-scroll__padding",key:"before",ref:j,style:{[p]:`${S.value}px`,...H}}),M(l,{class:"q-virtual-scroll__content",key:"content",ref:A,tabindex:-1},c.flat()),l==="tbody"?M(l,{class:"q-virtual-scroll__padding",key:"after",ref:U},[M("tr",[M("td",{style:{[p]:`${W.value}px`,...H},colspan:I.value})])]):M(l,{class:"q-virtual-scroll__padding",key:"after",ref:U,style:{[p]:`${W.value}px`,...H}})]}function ie(l){f!==l&&(i.onVirtualScroll!==void 0&&m("virtualScroll",{index:l,from:E.value.from,to:E.value.to-1,direction:l<f?"decrease":"increase",ref:h}),f=l)}X();const Z=sl(ae,g.platform.is.ios===!0?120:35);cl(()=>{X()});let se=!1;return dl(()=>{se=!0}),fl(()=>{if(se!==!0)return;const l=n();y!==void 0&&l!==void 0&&l!==null&&l.nodeType!==8?kt(l,y,i.virtualScrollHorizontal,g.lang.rtl):J(f)}),qe(()=>{Z.cancel()}),Object.assign(h,{scrollTo:J,reset:_,refresh:N}),{virtualScrollSliceRange:E,virtualScrollSliceSizeComputed:F,setVirtualScrollSize:X,onVirtualScrollEvt:Z,localResetVirtualScroll:oe,padVirtualScroll:ke,scrollTo:J,reset:_,refresh:N}}const Mt=e=>["add","add-unique","toggle"].includes(e),Zl=".*+?^${}()|[]\\",en=Object.keys(Je);var cn=Ze({name:"QSelect",inheritAttrs:!1,props:{...Gl,...Yt,...Je,modelValue:{required:!0},multiple:Boolean,displayValue:[String,Number],displayValueHtml:Boolean,dropdownIcon:String,options:{type:Array,default:()=>[]},optionValue:[Function,String],optionLabel:[Function,String],optionDisable:[Function,String],hideSelected:Boolean,hideDropdownIcon:Boolean,fillInput:Boolean,maxValues:[Number,String],optionsDense:Boolean,optionsDark:{type:Boolean,default:null},optionsSelectedClass:String,optionsHtml:Boolean,optionsCover:Boolean,menuShrink:Boolean,menuAnchor:String,menuSelf:String,menuOffset:Array,popupContentClass:String,popupContentStyle:[String,Array,Object],useInput:Boolean,useChips:Boolean,newValueMode:{type:String,validator:Mt},mapOptions:Boolean,emitValue:Boolean,inputDebounce:{type:[Number,String],default:500},inputClass:[Array,String,Object],inputStyle:[Array,String,Object],tabindex:{type:[String,Number],default:0},autocomplete:String,transitionShow:String,transitionHide:String,transitionDuration:[String,Number],behavior:{type:String,validator:e=>["default","menu","dialog"].includes(e),default:"default"},virtualScrollItemSize:{type:[Number,String],default:void 0},onNewValue:Function,onFilter:Function},emits:[...At,"add","remove","inputValue","newValue","keyup","keypress","keydown","filterAbort"],setup(e,{slots:n,emit:u}){const{proxy:o}=De(),{$q:v}=o,i=L(!1),m=L(!1),h=L(-1),g=L(""),y=L(!1),f=L(!1);let w=null,C=null,s,S,W,F=null,j,U,A,E;const I=L(null),z=L(null),R=L(null),_=L(null),N=L(null),J=Gt(e),ae=Jt(st),$=V(()=>Array.isArray(e.options)?e.options.length:0),ne=V(()=>e.virtualScrollItemSize===void 0?e.optionsDense===!0?24:48:e.virtualScrollItemSize),{virtualScrollSliceRange:re,virtualScrollSliceSizeComputed:oe,localResetVirtualScroll:X,padVirtualScroll:ke,onVirtualScrollEvt:ie,scrollTo:Z,setVirtualScrollSize:se}=Jl({virtualScrollLength:$,getVirtualScrollTarget:Lt,getVirtualScrollEl:at,virtualScrollItemSizeComputed:ne}),l=Tt(),c=V(()=>{const t=e.mapOptions===!0&&e.multiple!==!0,d=e.modelValue!==void 0&&(e.modelValue!==null||t===!0)?e.multiple===!0&&Array.isArray(e.modelValue)?e.modelValue:[e.modelValue]:[];if(e.mapOptions===!0&&Array.isArray(e.options)===!0){const r=e.mapOptions===!0&&s!==void 0?s:[],b=d.map(q=>Ot(q,r));return e.modelValue===null&&t===!0?b.filter(q=>q!==null):b}return d}),p=V(()=>{const t={};return en.forEach(d=>{const r=e[d];r!==void 0&&(t[d]=r)}),t}),H=V(()=>e.optionsDark===null?l.isDark.value:e.optionsDark),O=V(()=>mt(c.value)),k=V(()=>{let t="q-field__input q-placeholder col";return e.hideSelected===!0||c.value.length===0?[t,e.inputClass]:(t+=" q-field__input--padding",e.inputClass===void 0?t:[t,e.inputClass])}),x=V(()=>(e.virtualScrollHorizontal===!0?"q-virtual-scroll--horizontal":"")+(e.popupContentClass?" "+e.popupContentClass:"")),B=V(()=>$.value===0),a=V(()=>c.value.map(t=>Q.value(t)).join(", ")),D=V(()=>e.displayValue!==void 0?e.displayValue:a.value),ee=V(()=>e.optionsHtml===!0?()=>!0:t=>t!=null&&t.html===!0),ge=V(()=>e.displayValueHtml===!0||e.displayValue===void 0&&(e.optionsHtml===!0||c.value.some(ee.value))),te=V(()=>l.focused.value===!0?e.tabindex:-1),Fe=V(()=>{const t={tabindex:e.tabindex,role:"combobox","aria-label":e.label,"aria-readonly":e.readonly===!0?"true":"false","aria-autocomplete":e.useInput===!0?"list":"none","aria-expanded":i.value===!0?"true":"false","aria-controls":`${l.targetUid.value}_lb`};return h.value>=0&&(t["aria-activedescendant"]=`${l.targetUid.value}_${h.value}`),t}),ce=V(()=>({id:`${l.targetUid.value}_lb`,role:"listbox","aria-multiselectable":e.multiple===!0?"true":"false"})),de=V(()=>c.value.map((t,d)=>({index:d,opt:t,html:ee.value(t),selected:!0,removeAtIndex:It,toggleOption:fe,tabindex:te.value}))),Ie=V(()=>{if($.value===0)return[];const{from:t,to:d}=re.value;return e.options.slice(t,d).map((r,b)=>{const q=Se.value(r)===!0,T=t+b,P={clickable:!0,active:!1,activeClass:Ae.value,manualFocus:!0,focused:!1,disable:q,tabindex:-1,dense:e.optionsDense,dark:H.value,role:"option",id:`${l.targetUid.value}_${T}`,onClick:()=>{fe(r)}};return q!==!0&&(je(r)===!0&&(P.active=!0),h.value===T&&(P.focused=!0),P["aria-selected"]=P.active===!0?"true":"false",v.platform.is.desktop===!0&&(P.onMousemove=()=>{i.value===!0&&ye(T)})),{index:T,opt:r,html:ee.value(r),label:Q.value(r),selected:P.active,focused:P.focused,toggleOption:fe,setOptionIndex:ye,itemProps:P}})}),Me=V(()=>e.dropdownIcon!==void 0?e.dropdownIcon:v.iconSet.arrow.dropdown),We=V(()=>e.optionsCover===!1&&e.outlined!==!0&&e.standout!==!0&&e.borderless!==!0&&e.rounded!==!0),Ae=V(()=>e.optionsSelectedClass!==void 0?e.optionsSelectedClass:e.color!==void 0?`text-${e.color}`:""),le=V(()=>Ke(e.optionValue,"value")),Q=V(()=>Ke(e.optionLabel,"label")),Se=V(()=>Ke(e.optionDisable,"disable")),Oe=V(()=>c.value.map(t=>le.value(t))),Ft=V(()=>{const t={onInput:st,onChange:ae,onKeydown:it,onKeyup:ut,onKeypress:ot,onFocus:lt,onClick(d){S===!0&&pe(d)}};return t.onCompositionstart=t.onCompositionupdate=t.onCompositionend=ae,t});Y(c,t=>{s=t,e.useInput===!0&&e.fillInput===!0&&e.multiple!==!0&&l.innerLoading.value!==!0&&(m.value!==!0&&i.value!==!0||O.value!==!0)&&(W!==!0&&Ce(),(m.value===!0||i.value===!0)&&be(""))},{immediate:!0}),Y(()=>e.fillInput,Ce),Y(i,Ne),Y($,Ut);function et(t){return e.emitValue===!0?le.value(t):t}function $e(t){if(t>-1&&t<c.value.length)if(e.multiple===!0){const d=e.modelValue.slice();u("remove",{index:t,value:d.splice(t,1)[0]}),u("update:modelValue",d)}else u("update:modelValue",null)}function It(t){$e(t),l.focus()}function tt(t,d){const r=et(t);if(e.multiple!==!0){e.fillInput===!0&&Ee(Q.value(t),!0,!0),u("update:modelValue",r);return}if(c.value.length===0){u("add",{index:0,value:r}),u("update:modelValue",e.multiple===!0?[r]:r);return}if(d===!0&&je(t)===!0||e.maxValues!==void 0&&e.modelValue.length>=e.maxValues)return;const b=e.modelValue.slice();u("add",{index:b.length,value:r}),b.push(r),u("update:modelValue",b)}function fe(t,d){if(l.editable.value!==!0||t===void 0||Se.value(t)===!0)return;const r=le.value(t);if(e.multiple!==!0){d!==!0&&(Ee(e.fillInput===!0?Q.value(t):"",!0,!0),ve()),z.value!==null&&z.value.focus(),(c.value.length===0||Te(le.value(c.value[0]),r)!==!0)&&u("update:modelValue",e.emitValue===!0?r:t);return}if((S!==!0||y.value===!0)&&l.focus(),lt(),c.value.length===0){const T=e.emitValue===!0?r:t;u("add",{index:0,value:T}),u("update:modelValue",e.multiple===!0?[T]:T);return}const b=e.modelValue.slice(),q=Oe.value.findIndex(T=>Te(T,r));if(q>-1)u("remove",{index:q,value:b.splice(q,1)[0]});else{if(e.maxValues!==void 0&&b.length>=e.maxValues)return;const T=e.emitValue===!0?r:t;u("add",{index:b.length,value:T}),b.push(T)}u("update:modelValue",b)}function ye(t){if(v.platform.is.desktop!==!0)return;const d=t>-1&&t<$.value?t:-1;h.value!==d&&(h.value=d)}function Le(t=1,d){if(i.value===!0){let r=h.value;do r=yt(r+t,-1,$.value-1);while(r!==-1&&r!==h.value&&Se.value(e.options[r])===!0);h.value!==r&&(ye(r),Z(r),d!==!0&&e.useInput===!0&&e.fillInput===!0&&Be(r>=0?Q.value(e.options[r]):j,!0))}}function Ot(t,d){const r=b=>Te(le.value(b),t);return e.options.find(r)||d.find(r)||t}function Ke(t,d){const r=t!==void 0?t:d;return typeof r=="function"?r:b=>b!==null&&typeof b=="object"&&r in b?b[r]:b}function je(t){const d=le.value(t);return Oe.value.find(r=>Te(r,d))!==void 0}function lt(t){e.useInput===!0&&z.value!==null&&(t===void 0||z.value===t.target&&t.target.value===a.value)&&z.value.select()}function nt(t){zt(t,27)===!0&&i.value===!0&&(pe(t),ve(),Ce()),u("keyup",t)}function ut(t){const{value:d}=t.target;if(t.keyCode!==void 0){nt(t);return}if(t.target.value="",w!==null&&(clearTimeout(w),w=null),C!==null&&(clearTimeout(C),C=null),Ce(),typeof d=="string"&&d.length!==0){const r=d.toLocaleLowerCase(),b=T=>{const P=e.options.find(K=>T.value(K).toLocaleLowerCase()===r);return P===void 0?!1:(c.value.indexOf(P)===-1?fe(P):ve(),!0)},q=T=>{b(le)!==!0&&(b(Q)===!0||T===!0||be(d,!0,()=>q(!0)))};q()}else l.clearValue(t)}function ot(t){u("keypress",t)}function it(t){if(u("keydown",t),gl(t)===!0)return;const d=g.value.length!==0&&(e.newValueMode!==void 0||e.onNewValue!==void 0),r=t.shiftKey!==!0&&e.multiple!==!0&&(h.value>-1||d===!0);if(t.keyCode===27){He(t);return}if(t.keyCode===9&&r===!1){we();return}if(t.target===void 0||t.target.id!==l.targetUid.value||l.editable.value!==!0)return;if(t.keyCode===40&&l.innerLoading.value!==!0&&i.value===!1){me(t),xe();return}if(t.keyCode===8&&(e.useChips===!0||e.clearable===!0)&&e.hideSelected!==!0&&g.value.length===0){e.multiple===!0&&Array.isArray(e.modelValue)===!0?$e(e.modelValue.length-1):e.multiple!==!0&&e.modelValue!==null&&u("update:modelValue",null);return}(t.keyCode===35||t.keyCode===36)&&(typeof g.value!="string"||g.value.length===0)&&(me(t),h.value=-1,Le(t.keyCode===36?1:-1,e.multiple)),(t.keyCode===33||t.keyCode===34)&&oe.value!==void 0&&(me(t),h.value=Math.max(-1,Math.min($.value,h.value+(t.keyCode===33?-1:1)*oe.value.view)),Le(t.keyCode===33?1:-1,e.multiple)),(t.keyCode===38||t.keyCode===40)&&(me(t),Le(t.keyCode===38?-1:1,e.multiple));const b=$.value;if((A===void 0||E<Date.now())&&(A=""),b>0&&e.useInput!==!0&&t.key!==void 0&&t.key.length===1&&t.altKey===!1&&t.ctrlKey===!1&&t.metaKey===!1&&(t.keyCode!==32||A.length!==0)){i.value!==!0&&xe(t);const q=t.key.toLocaleLowerCase(),T=A.length===1&&A[0]===q;E=Date.now()+1500,T===!1&&(me(t),A+=q);const P=new RegExp("^"+A.split("").map(Qe=>Zl.indexOf(Qe)>-1?"\\"+Qe:Qe).join(".*"),"i");let K=h.value;if(T===!0||K<0||P.test(Q.value(e.options[K]))!==!0)do K=yt(K+1,-1,b-1);while(K!==h.value&&(Se.value(e.options[K])===!0||P.test(Q.value(e.options[K]))!==!0));h.value!==K&&ue(()=>{ye(K),Z(K),K>=0&&e.useInput===!0&&e.fillInput===!0&&Be(Q.value(e.options[K]),!0)});return}if(!(t.keyCode!==13&&(t.keyCode!==32||e.useInput===!0||A!=="")&&(t.keyCode!==9||r===!1))){if(t.keyCode!==9&&me(t),h.value>-1&&h.value<b){fe(e.options[h.value]);return}if(d===!0){const q=(T,P)=>{if(P){if(Mt(P)!==!0)return}else P=e.newValueMode;if(Ee("",e.multiple!==!0,!0),T==null)return;(P==="toggle"?fe:tt)(T,P==="add-unique"),e.multiple!==!0&&(z.value!==null&&z.value.focus(),ve())};if(e.onNewValue!==void 0?u("newValue",g.value,q):q(g.value),e.multiple!==!0)return}i.value===!0?we():l.innerLoading.value!==!0&&xe()}}function at(){return S===!0?N.value:R.value!==null&&R.value.contentEl!==null?R.value.contentEl:void 0}function Lt(){return at()}function Bt(){return e.hideSelected===!0?[]:n["selected-item"]!==void 0?de.value.map(t=>n["selected-item"](t)).slice():n.selected!==void 0?[].concat(n.selected()):e.useChips===!0?de.value.map((t,d)=>M(zl,{key:"option-"+d,removable:l.editable.value===!0&&Se.value(t.opt)!==!0,dense:!0,textColor:e.color,tabindex:te.value,onRemove(){t.removeAtIndex(d)}},()=>M("span",{class:"ellipsis",[t.html===!0?"innerHTML":"textContent"]:Q.value(t.opt)}))):[M("span",{[ge.value===!0?"innerHTML":"textContent"]:D.value})]}function rt(){if(B.value===!0)return n["no-option"]!==void 0?n["no-option"]({inputValue:g.value}):void 0;const t=n.option!==void 0?n.option:r=>M(ql,{key:r.index,...r.itemProps},()=>M(Il,()=>M(Ol,()=>M("span",{[r.html===!0?"innerHTML":"textContent"]:r.label}))));let d=ke("div",Ie.value.map(t));return n["before-options"]!==void 0&&(d=n["before-options"]().concat(d)),Sl(n["after-options"],d)}function Pt(t,d){const r=d===!0?{...Fe.value,...l.splitAttrs.attributes.value}:void 0,b={ref:d===!0?z:void 0,key:"i_t",class:k.value,style:e.inputStyle,value:g.value!==void 0?g.value:"",type:"search",...r,id:d===!0?l.targetUid.value:void 0,maxlength:e.maxlength,autocomplete:e.autocomplete,"data-autofocus":t===!0||e.autofocus===!0||void 0,disabled:e.disable===!0,readonly:e.readonly===!0,...Ft.value};return t!==!0&&S===!0&&(Array.isArray(b.class)===!0?b.class=[...b.class,"no-pointer-events"]:b.class+=" no-pointer-events"),M("input",b)}function st(t){w!==null&&(clearTimeout(w),w=null),C!==null&&(clearTimeout(C),C=null),!(t&&t.target&&t.target.qComposing===!0)&&(Be(t.target.value||""),W=!0,j=g.value,l.focused.value!==!0&&(S!==!0||y.value===!0)&&l.focus(),e.onFilter!==void 0&&(w=setTimeout(()=>{w=null,be(g.value)},e.inputDebounce)))}function Be(t,d){g.value!==t&&(g.value=t,d===!0||e.inputDebounce===0||e.inputDebounce==="0"?u("inputValue",t):C=setTimeout(()=>{C=null,u("inputValue",t)},e.inputDebounce))}function Ee(t,d,r){W=r!==!0,e.useInput===!0&&(Be(t,!0),(d===!0||r!==!0)&&(j=t),d!==!0&&be(t))}function be(t,d,r){if(e.onFilter===void 0||d!==!0&&l.focused.value!==!0)return;l.innerLoading.value===!0?u("filterAbort"):(l.innerLoading.value=!0,f.value=!0),t!==""&&e.multiple!==!0&&c.value.length!==0&&W!==!0&&t===Q.value(c.value[0])&&(t="");const b=setTimeout(()=>{i.value===!0&&(i.value=!1)},10);F!==null&&clearTimeout(F),F=b,u("filter",t,(q,T)=>{(d===!0||l.focused.value===!0)&&F===b&&(clearTimeout(F),typeof q=="function"&&q(),f.value=!1,ue(()=>{l.innerLoading.value=!1,l.editable.value===!0&&(d===!0?i.value===!0&&ve():i.value===!0?Ne(!0):i.value=!0),typeof T=="function"&&ue(()=>{T(o)}),typeof r=="function"&&ue(()=>{r(o)})}))},()=>{l.focused.value===!0&&F===b&&(clearTimeout(F),l.innerLoading.value=!1,f.value=!1),i.value===!0&&(i.value=!1)})}function Rt(){return M(Ql,{ref:R,class:x.value,style:e.popupContentStyle,modelValue:i.value,fit:e.menuShrink!==!0,cover:e.optionsCover===!0&&B.value!==!0&&e.useInput!==!0,anchor:e.menuAnchor,self:e.menuSelf,offset:e.menuOffset,dark:H.value,noParentEvent:!0,noRefocus:!0,noFocus:!0,square:We.value,transitionShow:e.transitionShow,transitionHide:e.transitionHide,transitionDuration:e.transitionDuration,separateClosePopup:!0,...ce.value,onScrollPassive:ie,onBeforeShow:dt,onBeforeHide:_t,onShow:Dt},rt)}function _t(t){ft(t),we()}function Dt(){se()}function Wt(t){pe(t),z.value!==null&&z.value.focus(),y.value=!0,window.scrollTo(window.pageXOffset||window.scrollX||document.body.scrollLeft||0,0)}function $t(t){pe(t),ue(()=>{y.value=!1})}function Kt(){const t=[M(Pl,{class:`col-auto ${l.fieldClass.value}`,...p.value,for:l.targetUid.value,dark:H.value,square:!0,loading:f.value,itemAligned:!1,filled:!0,stackLabel:g.value.length!==0,...l.splitAttrs.listeners.value,onFocus:Wt,onBlur:$t},{...n,rawControl:()=>l.getControl(!0),before:void 0,after:void 0})];return i.value===!0&&t.push(M("div",{ref:N,class:x.value+" scroll",style:e.popupContentStyle,...ce.value,onClick:He,onScrollPassive:ie},rt())),M(Hl,{ref:_,modelValue:m.value,position:e.useInput===!0?"top":void 0,transitionShow:U,transitionHide:e.transitionHide,transitionDuration:e.transitionDuration,onBeforeShow:dt,onBeforeHide:jt,onHide:Nt,onShow:Qt},()=>M("div",{class:"q-select__dialog"+(H.value===!0?" q-select__dialog--dark q-dark":"")+(y.value===!0?" q-select__dialog--focused":"")},t))}function jt(t){ft(t),_.value!==null&&_.value.__updateRefocusTarget(l.rootRef.value.querySelector(".q-field__native > [tabindex]:last-child")),l.focused.value=!1}function Nt(t){ve(),l.focused.value===!1&&u("blur",t),Ce()}function Qt(){const t=document.activeElement;(t===null||t.id!==l.targetUid.value)&&z.value!==null&&z.value!==t&&z.value.focus(),se()}function we(){m.value!==!0&&(h.value=-1,i.value===!0&&(i.value=!1),l.focused.value===!1&&(F!==null&&(clearTimeout(F),F=null),l.innerLoading.value===!0&&(u("filterAbort"),l.innerLoading.value=!1,f.value=!1)))}function xe(t){l.editable.value===!0&&(S===!0?(l.onControlFocusin(t),m.value=!0,ue(()=>{l.focus()})):l.focus(),e.onFilter!==void 0?be(g.value):(B.value!==!0||n["no-option"]!==void 0)&&(i.value=!0))}function ve(){m.value=!1,we()}function Ce(){e.useInput===!0&&Ee(e.multiple!==!0&&e.fillInput===!0&&c.value.length!==0&&Q.value(c.value[0])||"",!0,!0)}function Ne(t){let d=-1;if(t===!0){if(c.value.length!==0){const r=le.value(c.value[0]);d=e.options.findIndex(b=>Te(le.value(b),r))}X(d)}ye(d)}function Ut(t,d){i.value===!0&&l.innerLoading.value===!1&&(X(-1,!0),ue(()=>{i.value===!0&&l.innerLoading.value===!1&&(t>d?X():Ne(!0))}))}function ct(){m.value===!1&&R.value!==null&&R.value.updatePosition()}function dt(t){t!==void 0&&pe(t),u("popupShow",t),l.hasPopupOpen=!0,l.onControlFocusin(t)}function ft(t){t!==void 0&&pe(t),u("popupHide",t),l.hasPopupOpen=!1,l.onControlFocusout(t)}function vt(){S=v.platform.is.mobile!==!0&&e.behavior!=="dialog"?!1:e.behavior!=="menu"&&(e.useInput===!0?n["no-option"]!==void 0||e.onFilter!==void 0||B.value===!1:!0),U=v.platform.is.ios===!0&&S===!0&&e.useInput===!0?"fade":e.transitionShow}return vl(vt),ml(ct),vt(),qe(()=>{w!==null&&clearTimeout(w),C!==null&&clearTimeout(C)}),Object.assign(o,{showPopup:xe,hidePopup:ve,removeAtIndex:$e,add:tt,toggleOption:fe,getOptionIndex:()=>h.value,setOptionIndex:ye,moveOptionSelection:Le,filter:be,updateMenuPosition:ct,updateInputValue:Ee,isOptionSelected:je,getEmittingOptionValue:et,isOptionDisabled:(...t)=>Se.value.apply(null,t)===!0,getOptionValue:(...t)=>le.value.apply(null,t),getOptionLabel:(...t)=>Q.value.apply(null,t)}),Object.assign(l,{innerValue:c,fieldClass:V(()=>`q-select q-field--auto-height q-select--with${e.useInput!==!0?"out":""}-input q-select--with${e.useChips!==!0?"out":""}-chips q-select--${e.multiple===!0?"multiple":"single"}`),inputRef:I,targetRef:z,hasValue:O,showPopup:xe,floatingLabel:V(()=>e.hideSelected!==!0&&O.value===!0||typeof g.value=="number"||g.value.length!==0||mt(e.displayValue)),getControlChild:()=>{if(l.editable.value!==!1&&(m.value===!0||B.value!==!0||n["no-option"]!==void 0))return S===!0?Kt():Rt();l.hasPopupOpen===!0&&(l.hasPopupOpen=!1)},controlEvents:{onFocusin(t){l.onControlFocusin(t)},onFocusout(t){l.onControlFocusout(t,()=>{Ce(),we()})},onClick(t){if(He(t),S!==!0&&i.value===!0){we(),z.value!==null&&z.value.focus();return}xe(t)}},getControl:t=>{const d=Bt(),r=t===!0||m.value!==!0||S!==!0;if(e.useInput===!0)d.push(Pt(t,r));else if(l.editable.value===!0){const q=r===!0?Fe.value:void 0;d.push(M("input",{ref:r===!0?z:void 0,key:"d_t",class:"q-select__focus-target",id:r===!0?l.targetUid.value:void 0,value:D.value,readonly:!0,"data-autofocus":t===!0||e.autofocus===!0||void 0,...q,onKeydown:it,onKeyup:nt,onKeypress:ot})),r===!0&&typeof e.autocomplete=="string"&&e.autocomplete.length!==0&&d.push(M("input",{class:"q-select__autocomplete-input",autocomplete:e.autocomplete,tabindex:-1,onKeyup:ut}))}if(J.value!==void 0&&e.disable!==!0&&Oe.value.length!==0){const q=Oe.value.map(T=>M("option",{value:T,selected:!0}));d.push(M("select",{class:"hidden",name:J.value,multiple:e.multiple},q))}const b=e.useInput===!0||r!==!0?void 0:l.splitAttrs.attributes.value;return M("div",{class:"q-field__native row items-center",...b,...l.splitAttrs.listeners.value},d)},getInnerAppend:()=>e.loading!==!0&&f.value!==!0&&e.hideDropdownIcon!==!0?[M(hl,{class:"q-select__dropdown-icon"+(i.value===!0?" rotate-180":""),name:Me.value})]:null}),Et(l)}});export{cn as Q,Ql as a};