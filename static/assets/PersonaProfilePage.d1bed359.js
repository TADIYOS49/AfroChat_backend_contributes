import{Q as b,a as g,b as h}from"./QCard.9bf82158.js";import{d as y,bT as x,cb as u,cn as P,r as c,o as k,aN as l,a9 as w,bg as t,f as n,ac as s,U as i,ab as p,cc as Q,b$ as B}from"./index.9318a740.js";import{u as f,a as C}from"./persona-store.0e6e4fc8.js";import{u as E}from"./tool-store.90c99ec5.js";import"./use-dark.bbec077c.js";const N={class:"absolute-bottom text-h6"},R={class:"about-section text-info"},S=s("h6",null,"About",-1),T={key:0},I={key:1,class:"description"},V=s("br",null,null,-1),j={class:"row justify-center"},F=y({__name:"PersonaProfilePage",setup(z){x(),u(E()),u(f());const m=P().params.id;f();const e=c(null),o=c(!1);c("");function v(){o.value=!o.value}return k(async()=>{const r=await C(m.toString());r.data&&(e.value=r.data)}),(r,A)=>(l(),w(b,{class:"my-card bg-secondary"},{default:t(()=>{var _;return[n(g,{src:(_=e.value)==null?void 0:_.persona_image,alt:"Person",class:"height-img"},{default:t(()=>{var a;return[s("div",N,i((a=e.value)==null?void 0:a.full_name),1)]}),_:1},8,["src"]),n(h,null,{default:t(()=>{var a,d;return[s("div",R,[S,o.value?(l(),p("div",I,i((d=e.value)==null?void 0:d.long_description),1)):(l(),p("div",T,i((a=e.value)==null?void 0:a.description),1)),V,s("div",j,[n(Q,{round:"",dense:"",class:"bg-accent",onClick:v},{default:t(()=>[n(B,{color:"white",name:o.value?"keyboard_arrow_up":"keyboard_arrow_down",size:"24px"},null,8,["name"])]),_:1})])])]}),_:1})]}),_:1}))}});export{F as default};
