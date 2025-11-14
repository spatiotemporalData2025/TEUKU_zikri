import{_ as r}from"./slidev/CodeBlockWrapper.vue_vue_type_script_setup_true_lang-BQhNASZI.js";import{b as p,o as u,w as a,g as n,ad as l,e as d,m as f,v as m,x as c,T as e}from"./modules/vue-C-lq0ZUA.js";import{_ as g}from"./slidev/two-cols.vue_vue_type_script_setup_true_lang-D0cFr0wC.js";import{u as k,f as _}from"./slidev/context-d14xt2mk.js";import"./modules/unplugin-icons-CrrNop7o.js";import"./index-Cw6_qtq9.js";import"./modules/shiki-CUeUv8pe.js";const x={class:"ml-4"},$={__name:"slides.md__slidev_6",setup(E){const{$clicksContext:t,$frontmatter:i}=k();return t.setup(),(h,s)=>{const o=r;return u(),p(g,m(c(e(_)(e(i),5))),{right:a(v=>[n("div",x,[s[1]||(s[1]=n("div",{style:{"border-top":"1px solid #333","border-bottom":"1px solid #333",padding:"0.3rem 0","margin-bottom":"0.8rem","text-align":"left"}},[n("strong",null,"Algorithm 1"),l(" R-tree Search ")],-1)),d(o,f({},{title:"",ranges:[]}),{default:a(()=>[...s[0]||(s[0]=[n("pre",{class:"shiki shiki-themes vitesse-dark vitesse-light slidev-code",style:{"--shiki-dark":"#dbd7caee","--shiki-light":"#393a34","--shiki-dark-bg":"#121212","--shiki-light-bg":"#ffffff"}},[n("code",{class:"language-text"},[n("span",{class:"line"},[n("span",null,"1: function SEARCH(T,S)")]),l(`
`),n("span",{class:"line"},[n("span",null,"2:   if T is not leaf then")]),l(`
`),n("span",{class:"line"},[n("span",null,"3:     for all E ∈ T do")]),l(`
`),n("span",{class:"line"},[n("span",null,"4:       if E.I overlaps S then")]),l(`
`),n("span",{class:"line"},[n("span",null,"5:         SEARCH(E.p, S)")]),l(`
`),n("span",{class:"line"},[n("span",null,"6:       end if")]),l(`
`),n("span",{class:"line"},[n("span",null,"7:     end for")]),l(`
`),n("span",{class:"line"},[n("span",null,"8:   else")]),l(`
`),n("span",{class:"line"},[n("span",null,"9:     for all E ∈ T do")]),l(`
`),n("span",{class:"line"},[n("span",null,"10:      if E.I overlaps S then")]),l(`
`),n("span",{class:"line"},[n("span",null,"11:        Output E")]),l(`
`),n("span",{class:"line"},[n("span",null,"12:      end if")]),l(`
`),n("span",{class:"line"},[n("span",null,"13:    end for")]),l(`
`),n("span",{class:"line"},[n("span",null,"14:  end if")]),l(`
`),n("span",{class:"line"},[n("span",null,"15: end function")])])],-1)])]),_:1},16)])]),default:a(()=>[s[2]||(s[2]=n("h1",null,"探索アルゴリズムの疑似コード",-1)),s[3]||(s[3]=n("p",null,[n("strong",null,"用語:")],-1)),s[4]||(s[4]=n("ul",null,[n("li",null,[n("strong",null,"T"),l(": 現在のノード")]),n("li",null,[n("strong",null,"S"),l(": 探索矩形")]),n("li",null,[n("strong",null,"E"),l(": 要素（ポインタ，矩形）")]),n("li",null,[n("strong",null,"E.I"),l(": 要素の矩形部分")]),n("li",null,[n("strong",null,"E.p"),l(": 要素の子ノードへのポインタ")])],-1))]),_:1},16)}}};export{$ as default};
