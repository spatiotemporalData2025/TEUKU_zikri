import{d as p,$ as u,y as f,f as n,o as r,g as e,t as a,F as h,Z as g,i as v,e as x,a0 as b}from"../modules/vue-BZkwjUey.js";import{u as N,j as y,c as _,b as k}from"../index-BYZQy7fX.js";import{N as T}from"./NoteDisplay-iHge2AXw.js";import"../modules/shiki-h7FM_dfv.js";const w=p({__name:"print",setup(m,{expose:i}){i();const{slides:l,total:o}=N();u(`
@page {
  size: A4;
  margin-top: 1.5cm;
  margin-bottom: 1cm;
}
* {
  -webkit-print-color-adjust: exact;
}
html,
html body,
html #app,
html #page-root {
  height: auto;
  overflow: auto !important;
}
`),y({title:`Notes - ${_.title}`});const d=f(()=>l.value.map(t=>{var s;return(s=t.meta)==null?void 0:s.slide}).filter(t=>t!==void 0&&t.noteHTML!=="")),c={slides:l,total:o,slidesWithNote:d,get configs(){return _},NoteDisplay:T};return Object.defineProperty(c,"__isScriptSetup",{enumerable:!1,value:!0}),c}}),S={id:"page-root"},D={class:"m-4"},L={class:"mb-10"},U={class:"text-4xl font-bold mt-2"},V={class:"opacity-50"},j={class:"text-lg"},z={class:"font-bold flex gap-2"},B={class:"opacity-50"},E={key:0,class:"border-main mb-8"};function H(m,i,l,o,d,c){return r(),n("div",S,[e("div",D,[e("div",L,[e("h1",U,a(o.configs.title),1),e("div",V,a(new Date().toLocaleString()),1)]),(r(!0),n(h,null,g(o.slidesWithNote,(t,s)=>(r(),n("div",{key:s,class:"flex flex-col gap-4 break-inside-avoid-page"},[e("div",null,[e("h2",j,[e("div",z,[e("div",B,a(t==null?void 0:t.no)+"/"+a(o.total),1),b(" "+a(t==null?void 0:t.title)+" ",1),i[0]||(i[0]=e("div",{class:"flex-auto"},null,-1))])]),x(o.NoteDisplay,{"note-html":t.noteHTML,class:"max-w-full"},null,8,["note-html"])]),s<o.slidesWithNote.length-1?(r(),n("hr",E)):v("v-if",!0)]))),128))])])}const K=k(w,[["render",H],["__file","/home/runner/work/TEUKU_zikri/TEUKU_zikri/Algo2/algo2-slidev/node_modules/@slidev/client/pages/presenter/print.vue"]]);export{K as default};
