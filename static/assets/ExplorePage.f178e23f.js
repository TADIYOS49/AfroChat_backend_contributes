import{Q as B,a as z}from"./QInfiniteScroll.827f07ef.js";import{Q as M}from"./QPage.c5d7c714.js";import{bY as F,r as g,d as R,bT as N,cb as w,o as L,w as D,aN as d,ab as p,aT as S,M as f,F as I,ac as t,f as m,bg as y,ca as V,b$ as j,U as v,bE as q,aQ as A,aO as O,a9 as U,P as Y}from"./index.9318a740.js";import{u as k}from"./chat-store.775f2457.js";import{a as $,t as Z,b as G}from"./explore.4cd00191.js";import{_ as C}from"./plugin-vue_export-helper.21dcd24c.js";const h=F("exploreStore",()=>{const r=g([]),l=g([]),i=g("Recommended"),a=g({total:0,offset:0,limit:5,returned:0});return{explore_tags:r,explore_list:l,selected_tag:i,meta_data:a,paginateExplores:async()=>{a.value.offset=a.value.offset+a.value.limit,await $(i.value,a.value.limit,a.value.offset).then(e=>{var s,_;(s=e.data)==null||s.data.forEach(b=>{l.value.push(b)}),a.value=(_=e.data)==null?void 0:_.meta_data}).catch(e=>{console.log(e)})},get_explore_lists:async()=>{await $(i.value,a.value.limit,a.value.offset).then(e=>{var s,_;l.value=(s=e.data)==null?void 0:s.data,a.value=(_=e.data)==null?void 0:_.meta_data}).catch(e=>{console.log(e)})}}});const Q=r=>(A("data-v-61f25609"),r=r(),O(),r),H=["onClick"],J={class:"persona-image"},K=["src","alt"],W={class:"message-count"},X={class:"text-info"},T={class:"card-section"},ee={class:"text-info"},te={class:"text-warning"},ae=["onClick"],se={key:0,xmlns:"http://www.w3.org/2000/svg",viewBox:"0 0 24 24",width:"2em",height:"2em",fill:"yellow",style:{cursor:"pointer"}},oe=Q(()=>t("path",{d:"M17.562 21.56a1 1 0 0 1-.465-.116L12 18.764l-5.097 2.68a1 1 0 0 1-1.45-1.053l.973-5.676l-4.124-4.02a1 1 0 0 1 .554-1.705l5.699-.828l2.549-5.164a1.04 1.04 0 0 1 1.793 0l2.548 5.164l5.699.828a1 1 0 0 1 .554 1.705l-4.124 4.02l.974 5.676a1 1 0 0 1-.985 1.169Z"},null,-1)),le=[oe],ie={key:1,xmlns:"http://www.w3.org/2000/svg",viewBox:"0 0 24 24",width:"2em",height:"2em",style:{cursor:"pointer"}},ne=Q(()=>t("path",{d:"M21.919 10.127a1 1 0 0 0-.845-1.136l-5.651-.826l-2.526-5.147a1.037 1.037 0 0 0-1.795.001L8.577 8.165l-5.651.826a1 1 0 0 0-.556 1.704l4.093 4.013l-.966 5.664a1.002 1.002 0 0 0 1.453 1.052l5.05-2.67l5.049 2.669a1 1 0 0 0 1.454-1.05l-.966-5.665l4.094-4.014a1 1 0 0 0 .288-.567m-5.269 4.05a.502.502 0 0 0-.143.441l1.01 5.921l-5.284-2.793a.505.505 0 0 0-.466 0L6.483 20.54l1.01-5.922a.502.502 0 0 0-.143-.441L3.07 9.98l5.912-.864a.503.503 0 0 0 .377-.275L12 3.46l2.64 5.382a.503.503 0 0 0 .378.275l5.913.863z"},null,-1)),ce=[ne],re=R({__name:"ExploreCard",setup(r){const l=N(),{explore_list:i,selected_tag:a,meta_data:u}=w(h()),{get_explore_lists:n}=h(),{ResetChat:e}=k(),{persona_id:s,sub_tool_id:_}=w(k());L(async()=>{await n()}),D(a,async(c,x)=>{u.value.offset=0,c!==x&&await n()});async function b(c){console.log("this is first explore type",c.type),await Z(c.id,c.type).then(()=>c.is_preferable_entity=!c.is_preferable_entity)}const P=(c,x,o,E)=>{e(),E==="Persona"?s.value=c:_.value=c,l.push({name:"chat",params:{id:c},query:{name:x,image:o}})};return(c,x)=>(d(!0),p(I,null,S(f(i),o=>(d(),p("div",{class:"persona-card bg-primary",key:o.id,onClick:E=>P(o.id,o.name,o.image,o.type)},[t("div",J,[m(V,{size:"64px",style:{margin:"0.6rem"}},{default:y(()=>[t("img",{src:o.image,alt:o.name,style:{"object-fit":"cover"}},null,8,K)]),_:2},1024),t("div",W,[m(j,{name:"forum",class:"forum-message text-info",size:"sm"}),t("p",X,v(o.total_messages),1)])]),t("div",T,[t("div",ee,[t("h6",null,v(o.name),1)]),t("div",te,[t("p",null,v(o.description),1)])]),t("div",{class:"svg-image",onClick:q(E=>b(o),["stop"])},[o.is_preferable_entity?(d(),p("svg",se,le)):(d(),p("svg",ie,ce))],8,ae)],8,H))),128))}});var _e=C(re,[["__scopeId","data-v-61f25609"]]);const de={class:"loader-container"},ue={__name:"ExploreLists",setup(r){const{meta_data:l,explore_list:i}=w(h()),{paginateExplores:a}=h(),u=g(!1);async function n(e,s){if(i.value.length>0){await a().then(()=>{s(),l.value.offset+2*l.value.limit>=l.value.total&&(u.value=!0)});return}}return(e,s)=>(d(),U(M,{class:"explore-wrapper"},{default:y(()=>[m(z,{class:"persona-card-container",onLoad:n,offset:10,debounce:"500",disable:u.value},{loading:y(()=>[t("div",de,[m(B,{class:"loader",color:"accent",size:"40px"})])]),default:y(()=>[m(_e)]),_:1},8,["disable"])]),_:1}))}};var pe=C(ue,[["__scopeId","data-v-4e6c6e48"]]);const ge={class:"page-container"},me={class:"category-chip-container text-info"},ve=["aria-current","onClick"],fe={class:"tag-description bg-primary"},he={class:"tag-title text-info"},xe={class:"text-warning"},ye={__name:"ExplorePage",setup(r){const{explore_tags:l,selected_tag:i}=w(h()),a=g(""),u=(n,e)=>{i.value=n,a.value=e};return L(async()=>{await G().then(n=>{var e;l.value=(e=n.data)==null?void 0:e.categories,console.log(l.value)}).catch(n=>{console.log(n)})}),(n,e)=>(d(),p("div",ge,[t("div",me,[(d(!0),p(I,null,S(f(l),s=>(d(),p("div",{class:Y(["category-chip text-weight-medium",s.title===f(i)?"bg-primary text-info":"bg-primary text-warning"]),key:s.title,"aria-current":s.title===f(i),onClick:_=>u(s.title,s.description)},[t("span",null,v(s.title),1)],10,ve))),128))]),t("div",fe,[t("p",he,v(f(i)),1),t("p",xe,v(a.value),1)]),m(pe)]))}};var Le=C(ye,[["__scopeId","data-v-22e85b54"]]);export{Le as default};
