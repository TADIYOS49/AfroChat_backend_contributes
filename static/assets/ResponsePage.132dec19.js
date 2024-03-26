import{Q as D}from"./QDialog.05df106c.js";import{d as b,aN as n,a9 as q,bg as S,ac as e,M as t,ab as r,U as f,aa as _,f as p,ai as N,cc as F,F as T,aT as x,aQ as w,aO as I,c as B,P as U,S as V,o as Q,cb as j,bU as Y,aF as z}from"./index.9318a740.js";import{Q as P}from"./QPage.c5d7c714.js";import{_ as R}from"./plugin-vue_export-helper.21dcd24c.js";import{u as L,S as G}from"./SearchBar.3b521b1d.js";import"./use-dark.bbec077c.js";import"./use-key-composition.a30091f4.js";import"./ImageModal.bac71592.js";import"./QCard.9bf82158.js";import"./QItemLabel.f5ebb189.js";import"./QInput.3b735948.js";import"./chat-store.775f2457.js";import"./explore.4cd00191.js";import"./ReCaptchaVuePlugin.836d4bc4.js";const k=a=>(w("data-v-2b567f1e"),a=a(),I(),a),M=["id"],A={key:0,class:"question"},E={class:"summary-container"},O=k(()=>e("div",{class:"icon-container"},[e("i",{class:"material-icons"},"description"),e("h6",null,"Summary")],-1)),H={class:"chip_container"},J={key:0},K={key:1,class:"sources-container bg-secondary shadow-2 rounded-borders"},W=k(()=>e("div",{class:"icon-container"},[e("i",{class:"material-icons"},"link"),e("h6",null,"Sources")],-1)),X={key:0,class:"source-list"},Z=["onClick"],ee={class:"source-title text-info"},oe={key:2,class:"icon-container"},te=k(()=>e("i",{class:"material-icons"},"recommend",-1)),se=k(()=>e("h6",null,"Related Questions",-1)),ae=[te,se],ne={key:3},re=["onClick"],ie=b({__name:"ResponseComponent",props:{ask_response:{},fetchSearchData:{type:Function}},setup(a){const c={"GPT 3.5":"green","Gemini Pro":"blue",Mistral:"orange",Llama:"purple",Gemma:"yellow"};function i(l){return c[l]}const d=a,{ask_response:o}=d,s=async l=>{d.fetchSearchData(l)},v=l=>{window.open(l,"_blank")},y=()=>{const l=o.question,h=o.summary;let m="";o.sources&&(m=o.sources.map(u=>`${u.title}: ${u.URL}`).join(`
`));const g=`${l}

Summary:
${h}

Sources:
${m}`;navigator.clipboard.writeText(g).then(()=>{console.log("Summary, sources, and question copied to clipboard")}).catch(u=>{console.error("Failed to copy summary, sources, and question: ",u)})};return(l,h)=>(n(),q(P,{class:"main-page bg-secondary text-info"},{default:S(()=>[e("div",{id:t(o).id},null,8,M),e("div",null,[t(o).question?(n(),r("h1",A,f(t(o).question),1)):_("",!0)]),e("div",E,[O,e("div",H,[p(D,{color:i(t(o).llm_model),class:"text-info"},{default:S(()=>[N(f(t(o).llm_model),1)]),_:1},8,["color"])]),p(F,{onClick:y,icon:"content_copy",class:"copy-button",flat:"",round:"",dense:""})]),t(o).summary?(n(),r("p",J,f(t(o).summary),1)):_("",!0),t(o).sources.length>0?(n(),r("div",K,[W,t(o).sources.length>0?(n(),r("div",X,[(n(!0),r(T,null,x(t(o).sources,(m,g)=>(n(),r("div",{key:g,class:"source-item bg-primary shadow-1",onClick:u=>v(m.URL)},[e("h6",ee,f(m.title),1)],8,Z))),128))])):_("",!0)])):_("",!0),t(o).recommendations.length>0?(n(),r("div",oe,ae)):_("",!0),t(o).recommendations&&t(o).recommendations.length>0?(n(),r("ul",ne,[(n(!0),r(T,null,x(t(o).recommendations,(m,g)=>(n(),r("li",{key:g},[e("button",{onClick:u=>s(m),class:"recommendation-button bg-warning text-info"},f(m),9,re)]))),128))])):_("",!0)]),_:1}))}});var ce=R(ie,[["__scopeId","data-v-2b567f1e"]]);(function(){try{if(typeof document<"u"){var a=document.createElement("style");a.appendChild(document.createTextNode('*[data-v-295a14e8]{box-sizing:border-box;padding:0;margin:0}.vue3-loading-shimmer[data-v-295a14e8]{position:relative;overflow:hidden;background-color:var(--vue3-loading-shimmer-bg)}.vue3-loading-shimmer[data-v-295a14e8]:before{content:"";position:absolute;top:0;left:0;right:0;bottom:0;background-image:var(--vue3-loading-shimmer-shimmerBg);animation-duration:var(--vue3-loading-shimmer-duration);animation-iteration-count:infinite;animation-timing-function:ease-in-out}.vue3-loading-shimmer__left-to-right[data-v-295a14e8]:before{transform:translate(-100%);animation-name:shimmerLeftToRight-295a14e8}.vue3-loading-shimmer__right-to-left[data-v-295a14e8]:before{transform:translate(100%);animation-name:shimmerRightToLeft-295a14e8}.vue3-loading-shimmer__top-to-bottom[data-v-295a14e8]:before{transform:translateY(-100%);animation-name:shimmerTopToBottom-295a14e8}.vue3-loading-shimmer__bottom-to-top[data-v-295a14e8]:before{transform:translateY(100%);animation-name:shimmerBottomToTop-295a14e8}@keyframes shimmerLeftToRight-295a14e8{to{transform:translate(100%)}}@keyframes shimmerRightToLeft-295a14e8{to{transform:translate(-100%)}}@keyframes shimmerTopToBottom-295a14e8{to{transform:translateY(100%)}}@keyframes shimmerBottomToTop-295a14e8{to{transform:translateY(-100%)}}')),document.head.appendChild(a)}}catch(c){console.error("vite-plugin-css-injected-by-js",c)}})();const le=b({__name:"Vue3LoadingShimmer",props:{bgColor:{default:"#d3d3d3"},shimmerColor:{default:"#ffffff"},duration:{default:1400},direction:{default:"left-to-right"}},setup(a){const c=a;function i(s){s=s.split("#")[1],s.length===3&&(s=s.split("").map(u=>`${u}${u}`).join(""));const v=s.slice(0,2),y=s.slice(2,4),l=s.slice(4,6),h=parseInt(v,16),m=parseInt(y,16),g=parseInt(l,16);return`${h},${m},${g}`}const d=B(()=>{const s=i(c.shimmerColor);return`linear-gradient(90deg,
            rgba(${s}, 0) 0%,
            rgba(${s}, 0.1) 20%,
            rgba(${s}, 0.3) 40%,
            rgba(${s}, 0.5) 60%,
            rgba(${s}, 0.3) 80%,
            rgba(${s}, 0.1) 100%)`}),o=B(()=>`${c.duration}ms`);return(s,v)=>(n(),r("div",{class:U(["vue3-loading-shimmer",`vue3-loading-shimmer__${s.direction}`]),style:V({"--vue3-loading-shimmer-bg":s.bgColor,"--vue3-loading-shimmer-shimmerBg":d.value,"--vue3-loading-shimmer-duration":o.value})},null,6))}}),me=(a,c)=>{const i=a.__vccOpts||a;for(const[d,o]of c)i[d]=o;return i},C=me(le,[["__scopeId","data-v-295a14e8"]]);const $=a=>(w("data-v-9a575b96"),a=a(),I(),a),de=$(()=>e("div",{id:"placeholder"},null,-1)),ue={class:"question"},_e=$(()=>e("div",{class:"summary-container"},[e("div",{class:"icon-container"},[e("i",{class:"material-icons"},"description"),e("h6",null,"Summary")])],-1)),pe={class:"sources-container bg-secondary shadow-2 rounded-borders"},he=$(()=>e("div",{class:"icon-container"},[e("i",{class:"material-icons"},"link"),e("h6",null,"Sources")],-1)),ge=$(()=>e("div",{class:"icon-container"},[e("i",{class:"material-icons"},"recommend"),e("h6",null,"Related Questions")],-1)),fe=b({__name:"LoadingComponent",props:{question:{}},setup(a){const c=a,{question:i}=c;return Q(()=>{console.log(i),console.log("LoadingComponent mounted")}),(d,o)=>(n(),q(P,{class:"main-page bg-secondary text-info"},{default:S(()=>[de,e("h1",ue,f(t(i)),1),_e,p(t(C),{class:"shimmer-container","bg-color":"secondary"}),e("div",pe,[he,p(t(C),{class:"shimmer-container","bg-color":"secondary"})]),ge,p(t(C),{class:"shimmer-container","bg-color":"secondary"})]),_:1}))}});var ve=R(fe,[["__scopeId","data-v-9a575b96"]]);const ye={class:"response bg-secondary text-info"},be={class:"chat-response-container"},ke={key:0,class:"line"},$e={key:0},Ce=b({__name:"ResponsePage",setup(a){const{fetchSearchData:c}=L(),{ask_responses:i,loading_response:d,last_question:o}=j(L()),{showBack:s}=Y();return z(()=>{i.value=[]}),Q(()=>{s()}),(v,y)=>(n(),r("div",ye,[e("div",be,[(n(!0),r(T,null,x(t(i),(l,h)=>(n(),r("div",{key:h},[p(ce,{ask_response:l,fetchSearchData:t(c)},null,8,["ask_response","fetchSearchData"]),h!==t(i).length-1?(n(),r("hr",ke)):_("",!0)]))),128)),t(d)?(n(),r("div",$e,[p(ve,{question:t(o)},null,8,["question"])])):_("",!0)]),p(G)]))}});var Ue=R(Ce,[["__scopeId","data-v-7a69dcb8"]]);export{Ue as default};