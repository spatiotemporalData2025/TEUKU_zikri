---
title: R-Tree実装発表 — Team B
theme: seriph
colorSchema: auto
fonts:
  sans: 'Inter'
transition: slide-left
mdc: true
---

<style>
/* Noragami inspired divine theme */
:root {
  --noragami-blue: #4169E1;
  --noragami-purple: #7B68EE;
  --noragami-white: #F0F8FF;
  --noragami-gold: #FFD700;
}
.dark {
  --bg-primary: linear-gradient(135deg, #1a1f3a 0%, #2d1b4e 100%);
  --text-glow: rgba(65, 105, 225, 0.6);
}
.light {
  --bg-primary: linear-gradient(135deg, #e6f2ff 0%, #f0f0ff 100%);
  --text-glow: rgba(65, 105, 225, 0.3);
}
.cover {
  height: 50vh;
  padding: 0 !important;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  gap: 2rem;
  position: relative;
  overflow: visible;   /* penting untuk neon shadow */
  padding-bottom: 50vh;
}
.dark .cover {
  color: #F0F8FF;

  background:
    radial-gradient(circle at 50% 25%, rgba(120,160,255,0.28), transparent 70%),
    radial-gradient(circle at 85% 70%, rgba(255,200,40,0.22), transparent 75%),
    radial-gradient(circle at 15% 80%, rgba(140,80,255,0.25), transparent 70%),
    linear-gradient(135deg, #05060c 0%, #0b0e18 45%, #06070d 100%);
}

.light .cover {
  color: #1a1f3a;

  background:
    radial-gradient(circle at 50% 25%, rgba(120,150,255,0.35), transparent 70%),
    radial-gradient(circle at 85% 70%, rgba(255,210,60,0.28), transparent 75%),
    radial-gradient(circle at 15% 80%, rgba(160,120,255,0.32), transparent 70%),
    linear-gradient(135deg, #e8ecff 0%, #d8dcff 45%, #eef0ff 100%);
}


/* Floating divine particles effect */
.cover::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image: 
    radial-gradient(circle at 20% 20%, rgba(65, 105, 225, 0.15) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(123, 104, 238, 0.15) 0%, transparent 50%),
    radial-gradient(circle at 50% 50%, rgba(255, 215, 0, 0.1) 0%, transparent 60%);
  animation: divineFloat 12s ease-in-out infinite;
}
@keyframes divineFloat {
  0%, 100% { transform: translateY(0) scale(1); opacity: 0.5; }
  50% { transform: translateY(-20px) scale(1.05); opacity: 0.8; }
}

.cover::after {
  content: "";
  position: absolute;
  inset: 0;
  z-index: -1;

  border-radius: 20px;

  background:
    radial-gradient(closest-side, rgba(120,150,255,0.6), transparent 80%) top left,
    radial-gradient(closest-side, rgba(255,220,80,0.45), transparent 80%) top right,
    radial-gradient(closest-side, rgba(150,80,255,0.45), transparent 80%) bottom left,
    radial-gradient(closest-side, rgba(100,120,255,0.55), transparent 80%) bottom right;

  background-size: 50% 50%;
  background-repeat: no-repeat;

  filter: blur(40px);
  opacity: 1;
}
.big {
  font-size: 7vh;
  font-weight: 900;
  background: linear-gradient(135deg, #4169E1 0%, #7B68EE 50%, #FFD700 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0;
  position: relative;
  z-index: 1;
  letter-spacing: 0.05em;
  filter: drop-shadow(0 0 30px rgba(65, 105, 225, 0.5));
  animation: titleGlow 3s ease-in-out infinite;
  text-align: center;
  line-height: 1.1;
}
@keyframes titleGlow {
  0%, 100% { filter: drop-shadow(0 0 20px rgba(65, 105, 225, 0.4)); }
  50% { filter: drop-shadow(0 0 40px rgba(65, 105, 225, 0.7)); }
}

.cover::after {
  content: "";
  position: absolute;
  inset: 0;
  z-index: -1;

  background: inherit; /* pakai background cover */
  border-radius: 20px;

  filter: blur(40px) brightness(0.4);
  transform: scale(1.06);
  opacity: 0.9;
}
.team {
  font-size: 4vh;
  font-weight: 700;
  margin-top: 0;
  margin-bottom: 0;
  position: relative;
  z-index: 1;
  background: linear-gradient(90deg, #4169E1, #7B68EE);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 0.2em;
}
.names {
  font-size: 2.2vh;
  line-height: 1.8;
  position: relative;
  z-index: 1;
  opacity: 0.9;
  font-weight: 400;
  max-width: 90%;
}
/* Divine gradient headings */
h1, h2, h3 {
  background: linear-gradient(135deg, #4169E1 0%, #7B68EE 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 800;
  position: relative;
}
h1::after, h2::after {
  content: '';
  position: absolute;
  bottom: -8px;
  left: 0;
  width: 60px;
  height: 3px;
  background: linear-gradient(90deg, #4169E1, #7B68EE, transparent);
  border-radius: 2px;
}
.slidev-code-wrapper {
  border-radius: 8px !important;
  border: 2px solid rgba(65, 105, 225, 0.3) !important;
  background: rgba(240, 248, 255, 0.05) !important;
  box-shadow: 
    0 4px 16px rgba(65, 105, 225, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}
img {
  border-radius: 12px;
  border: 2px solid rgba(140, 170, 255, 0.4);

  box-shadow:
    /* 0 0 7px rgba(140, 170, 255, 0.9),
    0 0 10px rgba(160, 190, 255, 0.6), */
    0 0 7px rgba(180, 210, 255, 0),
    0 4px 12px rgba(70, 110, 255, 0.4);
}


ul li::marker {
  color: #4169E1;
  font-weight: bold;
}
table {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(65, 105, 225, 0.15);
}
table th {
  background: linear-gradient(135deg, #4169E1, #7B68EE);
  color: white;
  font-weight: 700;
  padding: 0.75rem;
}
table td {
  border-bottom: 1px solid rgba(65, 105, 225, 0.1);
  padding: 0.75rem;
}
* {
  transition: all 0.3s ease;
}
</style>

<div class="cover">
  <div class="big">R-Tree実装発表</div>
  <div class="team">TEAM B</div>
</div>

---
layout: center
class: text-center
---

# TEAM B メンバー

<div style="font-size: 1.8rem; line-height: 2.5; margin-top: 2rem;">

筒井夏輝

佐々木悠介

小俣俊輔

Teuku Zikri Fatahillah

Rawich Piboonsin

河野拓斗

</div>

---
layout: two-cols
---
# R-Treeについて

- 空間データを効率的に管理する**ツリー構造**
- 各ノードが**最小外接矩形（MBR）**で表される
- 主に**範囲検索**、**交差判定**、**最近傍探索**に利用される

<div style="margin-top: 1rem; margin-bottom: 0.5rem;">

## 【メリット】

</div>

- 大量の空間データを**階層的に整理**可能
- **範囲・交差検索**を効率的に処理できる

---
layout: center
class: text-center
---

# 個人実装

---

# Rtreeの探索アルゴリズム

- 探索はB-treeのように根から降下

- ただし重なりがあるため、複数の部分木を探索する必要がある

- 目的：検索矩形Sと重なるデータ矩形を全て見つける

- 更新アルゴリズムが構造を保つので、無駄な領域は除外できる

---
layout: two-cols
---

## 探索アルゴリズムの疑似コード

**用語:**  
- **T**: 現在のノード  
- **S**: 探索矩形  
- **E**: 要素（ポインタ，矩形）
- **E.I**: 要素の矩形部分
- **E.p**: 要素の子ノードへのポインタ

::right::

<div class="ml-4">

<div style="border-top: 1px solid #333; border-bottom: 1px solid #333; padding: 0.3rem 0; margin-bottom: 0.8rem; text-align: left;">
<strong>Algorithm 1</strong> R-tree Search
</div>

```text
1: function SEARCH(T,S)
2:   if T is not leaf then
3:     for all E ∈ T do
4:       if E.I overlaps S then
5:         SEARCH(E.p, S)
6:       end if
7:     end for
8:   else
9:     for all E ∈ T do
10:      if E.I overlaps S then
11:        Output E
12:      end if
13:    end for
14:  end if
15: end function
```

</div>

---

## 探索アルゴリズムのコード

```python
def search(node: Node, query: Rect):
    for rect, child, obj_id in node.entries:
        steps.append((rect, "visited"))
        if not rect.intersects(query):
            steps.append((rect, "skipped"))
            continue
        if node.is_leaf:
            steps.append((rect, "leaf"))
        else:
            search(child, query)
```

---

# 探索アルゴリズムの可視化

<div style="border: 2px dashed #999; padding: 1.5rem; display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: center;">

<div>
<img src="/gifs/gif1.gif" alt="R-tree search visualization" style="width: 100%; height: auto;" />
</div>

<div>
<img src="/gifs/gif2.gif" alt="R-tree structure" style="width: 100%; height: auto;" />
</div>

</div>

---

# ノードの分割・追加処理
<br>
<div style="margin-top: 1rem; margin-bottom: 0.5rem;">

## Linear-Cost Algorithm（線形コスト分割アルゴリズム）

</div>


- 軸方向でもっとも**離れた矩形ペア**を選択
- シンプルで高速

<div style="margin-top: 1.5rem; margin-bottom: 1.0rem;">

## パラメータ設定

</div>

<table style="width: 100%; border-collapse: collapse;">
  <tr>
    <td style="border: 1px solid rgba(65, 105, 225, 0.3); padding: 0.75rem; font-weight: 900; color: #4169E1; width: 15%;">M=6</td>
    <td style="border: 1px solid rgba(65, 105, 225, 0.3); padding: 0.75rem;">各ノードが保持できる最大エントリ数。7件目を挿入すると分割が発生</td>
  </tr>
  <tr>
    <td style="border: 1px solid rgba(65, 105, 225, 0.3); padding: 0.75rem; font-weight: 900; color: #4169E1;">m=3</td>
    <td style="border: 1px solid rgba(65, 105, 225, 0.3); padding: 0.75rem;">各ノードが保持できる最小エントリ数。各ノードは最低3件を保持</td>
  </tr>
</table>

---

# 追加、線形コスト分割アルゴリズムの可視化

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: start;">

<div>

- 動作の流れ
  1. 30個のランダム矩形を作成  
  2. 各矩形を1つずつ挿入  
  3. R-tree構造を更新
- 特徴
  - M=&にすることで、分割を頻繁化
  - 計算量が少なく、リアルタイム描写に最適

</div>

<div>
<img src="/gifs/gif3.gif" alt="Linear-cost split visualization" style="width: 100%; height: auto;" />
</div>

</div>

---
layout: center
class: text-center
---

# チーム実装

---

# 目的

- SNSには位置情報付きの投稿が多い
- Flickrの投稿の中にはユーザの未知の写真スポットが存在
- 効率的な検索と可視化によって写真スポットを発見する
  - 地図上の投稿をクラスタリング
  - R-Treeを用いて位置情報検索を高速化

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 2rem;">
<img src="/images/image1.png" alt="Flickr posts map" style="width: 100%; height: auto;" />
<img src="/images/image2.png" alt="Clustered map" style="width: 100%; height: auto;" />
</div>

---

# 実装概要

- **Flickr** から投稿データの取得 
  - flickrapi 
- 地図平面上で投稿を**クラスタリング**
  - sklearn
- **R-tree** の作成
  - rtree
- **Webアプリ** の作成
  - fastapi, leaflet(js)

---

# Flickrから投稿データの取得

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: start;">

<div>

flickrapiから取得できる項目

- タイトル
- タグ
- 緯度経度
- 画像url など

取得内容

- ヨーロッパ全域
- 2024年1月1日から1年分
- 505,946投稿

</div>

<div style="display: grid; grid-template-rows: auto auto; gap: 1rem;">
<img src="/images/image3.png" alt="Flickr interface" style="width: 100%; height: auto;" />
<img src="/images/image4.png" alt="Map with posts" style="width: 100%; height: auto;" />
</div>

</div>

---

# 地図平面上で投稿をクラスタリング

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: start;">

<div>

- DBSCANでクラスタリング
- クラスタリングから漏れた投稿は削除
- パラメータ（適当）
  - eps = 30 [m]
  - min_samples = 8
- クラスタ数は8306

</div>

<div>
<img src="/images/image5.png" alt="Clustering map" style="width: 100%; height: auto;" />
</div>

</div>

---

# R-treeでの実装

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: start;">

<div>

- クラスタを包含する最小の矩形
- それぞれを葉としてR-Treeに追加

</div>

<div>
<img src="/images/image6.png" alt="R-tree implementation" style="width: 100%; height: auto;" />
</div>

</div>

---

# webアプリの作成

<img src="/images/image7.png" alt="Web application map" style="width: 100%; height: auto;" />

---

# 評価
<br>
R-Treeのほうが圧倒的に早い

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-top: 2rem;">
<img src="/images/image8.png" alt="R-Tree mode evaluation" style="width: 100%; height: auto;" />
<img src="/images/image9.png" alt="Linear search mode evaluation" style="width: 100%; height: auto;" />
</div>

---

<style>
.thanks-wrapper {
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  text-align: center;
  position: relative;
  overflow: hidden;
}

/* AUTO BACKGROUND */
.dark .thanks-wrapper {
  background: radial-gradient(circle at center,
    rgba(0,0,0,1) 0%,
    rgba(10,15,35,1) 45%,
    rgba(20,25,55,1) 100%);
}
.light .thanks-wrapper {
  background: radial-gradient(circle at center,
    rgba(64, 99, 255, 1) 10%,
    rgba(83, 114, 253, 1) 55%,
    rgba(136, 158, 255, 1) 100%);
}

/* AURA GLOW (auto color) */
.dark .thanks-wrapper::before,
.light .thanks-wrapper::before {
  content: "";
  position: absolute;
  inset: 0;
  z-index: -1;
  background:
    radial-gradient(circle at 50% 20%, rgba(120,150,255,0.4), transparent 70%),
    radial-gradient(circle at 85% 80%, rgba(255,200,80,0.35), transparent 75%),
    radial-gradient(circle at 15% 80%, rgba(150,80,255,0.35), transparent 75%);
  filter: blur(55px);
  opacity: 0.9;
}

/* MAIN TEXT */
.thanks-title {
  font-size: 9vh;
  font-weight: 900;
  letter-spacing: 0.06em;
  margin: 0;

  background: linear-gradient(135deg,
    #e2ceceff,
    #d5ddff 30%,
    #88aaff 60%,
    #ffd86b);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;

  text-shadow:
    0 0 18px rgba(255,255,255,0.6),
    0 0 30px rgba(140,160,255,0.4);
}

/* DARK MODE TEXT BOOSTER */
.dark .thanks-title {
  text-shadow:
    0 0 22px rgba(255,255,255,0.45),
    0 0 35px rgba(120,160,255,0.4),
    0 0 55px rgba(255,200,80,0.25);
}

/* SUBTEXT */
.thanks-sub {
  margin-top: 1.5vh;
  font-size: 2.8vh;
  letter-spacing: 0.25em;
  opacity: 0.85;
}

/* COLOR ADAPTATION */
.dark .thanks-sub {
  color: #dfe3ff;
}
.light .thanks-sub {
  color: #26264a;
}
</style>

<div class="thanks-wrapper">
  <div>
    <div class="thanks-title">Thank You</div>
    <div class="thanks-sub">質問はありますか？</div>
  </div>
</div>
