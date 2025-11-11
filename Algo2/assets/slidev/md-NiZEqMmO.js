import{_ as f}from"./CodeBlockWrapper.vue_vue_type_script_setup_true_lang-BFgMBclS.js";import{d as m,f as g,o as u,g as s,j as r,n as t,b as h,w as o,ad as l,e as k,m as v,v as _,x as E,T as p}from"../modules/vue-C-lq0ZUA.js";import{u as S,f as x}from"./context-Czws2hmU.js";import"../modules/unplugin-icons-CrrNop7o.js";import"../index-DjfUCRN_.js";import"../modules/shiki-CUeUv8pe.js";const C=m({__name:"two-cols",props:{class:{type:String},layoutClass:{type:String}},setup(i){const a=i;return(e,d)=>(u(),g("div",{class:t(["slidev-layout two-columns w-full h-full grid grid-cols-2",a.layoutClass])},[s("div",{class:t(["col-left",a.class])},[r(e.$slots,"default")],2),s("div",{class:t(["col-right",a.class])},[r(e.$slots,"right")],2)],2))}}),b={class:"ml-4"},A={__name:"slides.md__slidev_5",setup(i){const{$clicksContext:a,$frontmatter:e}=S();return a.setup(),(d,n)=>{const c=f;return u(),h(C,_(E(p(x)(p(e),4))),{right:o(T=>[s("div",b,[n[1]||(n[1]=s("div",{style:{"border-top":"1px solid #333","border-bottom":"1px solid #333",padding:"0.3rem 0","margin-bottom":"0.8rem","text-align":"left"}},[s("strong",null,"Algorithm 1"),l(" R-tree Search ")],-1)),k(c,v({},{title:"",ranges:[]}),{default:o(()=>[...n[0]||(n[0]=[s("pre",{class:"shiki shiki-themes vitesse-dark vitesse-light slidev-code",style:{"--shiki-dark":"#dbd7caee","--shiki-light":"#393a34","--shiki-dark-bg":"#121212","--shiki-light-bg":"#ffffff"}},[s("code",{class:"language-text"},[s("span",{class:"line"},[s("span",null,"1: function SEARCH(T,S)")]),l(`
`),s("span",{class:"line"},[s("span",null,"2:   if T is not leaf then")]),l(`
`),s("span",{class:"line"},[s("span",null,"3:     for all E ∈ T do")]),l(`
`),s("span",{class:"line"},[s("span",null,"4:       if E.I overlaps S then")]),l(`
`),s("span",{class:"line"},[s("span",null,"5:         SEARCH(E.p, S)")]),l(`
`),s("span",{class:"line"},[s("span",null,"6:       end if")]),l(`
`),s("span",{class:"line"},[s("span",null,"7:     end for")]),l(`
`),s("span",{class:"line"},[s("span",null,"8:   else")]),l(`
`),s("span",{class:"line"},[s("span",null,"9:     for all E ∈ T do")]),l(`
`),s("span",{class:"line"},[s("span",null,"10:      if E.I overlaps S then")]),l(`
`),s("span",{class:"line"},[s("span",null,"11:        Output E")]),l(`
`),s("span",{class:"line"},[s("span",null,"12:      end if")]),l(`
`),s("span",{class:"line"},[s("span",null,"13:    end for")]),l(`
`),s("span",{class:"line"},[s("span",null,"14:  end if")]),l(`
`),s("span",{class:"line"},[s("span",null,"15: end function")])])],-1)])]),_:1},16)])]),default:o(()=>[n[2]||(n[2]=s("h2",null,"探索アルゴリズムの疑似コード",-1)),n[3]||(n[3]=s("p",null,[s("strong",null,"用語:")],-1)),n[4]||(n[4]=s("ul",null,[s("li",null,[s("strong",null,"T"),l(": 現在のノード")]),s("li",null,[s("strong",null,"S"),l(": 探索矩形")]),s("li",null,[s("strong",null,"E"),l(": 要素（ポインタ，矩形）")]),s("li",null,[s("strong",null,"E.I"),l(": 要素の矩形部分")]),s("li",null,[s("strong",null,"E.p"),l(": 要素の子ノードへのポインタ")])],-1))]),_:1},16)}}};export{A as default};
