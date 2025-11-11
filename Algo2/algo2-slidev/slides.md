---
title: R-Tree実装発表 — Team B
theme: seriph
colorSchema: auto
fonts:
  sans: 'Inter'
transition: slide-left
mdc: true
---

<!-- ===== Cover ===== -->
<style>
.cover {
  height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  gap: 2rem;
  background: #000;
  color: #fff;
}
.big   { 
  font-size: 16vh; 
  font-weight: 900; 
  letter-spacing: 0.05em;
  line-height: 1.1;
  margin-bottom: 1rem;
}
.team  { 
  font-size: 4vh; 
  font-weight: 600; 
  margin-top: 2rem;
  margin-bottom: 1rem;
}
.names { 
  font-size: 2.8vh; 
  line-height: 1.8;
}
</style>

<div class="cover">
  <div class="big" style="font-size: 5vh; font-weight: 900; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 1.5rem;">R-Tree実装発表</div>
  <div class="team">チームB</div>
  <div class="names">
    筒井夏輝<br/>
    佐々木悠介<br/>
    小俣俊輔<br/>
    Teuku Zikri Fatahillah<br/>
    Rawich Piboonsin<br/>
    河野拓斗
  </div>
</div>

---

# R-Treeについて

- 空間データを効率的に管理する**ツリー構造**
- 各ノードが**最小外接矩形（MBR）**で表される
- 主に**範囲検索**、**交差判定**、**最近傍探索**に利用される

<br>

## 【メリット】
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

## Linear-Cost Algorithm（線形コスト分割アルゴリズム）

- 軸方向でもっとも**離れた矩形ペア**を選択
- シンプルで高速

<br>

## パラメータ設定
|     |                                                              |
|-----|--------------------------------------------------------------|
| M=6 | 各ノードが保持できる最大エントリ数。7件目を挿入すると分割が発生 |
| m=3 | 各ノードが保持できる最小エントリ数。各ノードは最低3件を保持 |

---

## 追加、線形コスト分割アルゴリズムの可視化

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: start;">

<div>

### 動作の流れ

1. 30個のランダム矩形を作成  
2. 各矩形を1つずつ挿入  
3. R-tree構造を更新

### 特徴

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

## 実装概要

- **Flickr** から投稿データの取得  
- 地図平面上で投稿を**クラスタリング**  
- **R-tree** の作成  
- **Webアプリ** の作成

---

# Flickrから投稿データの取得

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: start;">

<div>

pythonのライブラリ flickrapi を用いて取得

- タイトル
- タグ
- 緯度経度
- 画像url など

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

デモは録画じゃなく実際に動かしたほうが面白そう

---

# 評価

線形探索と比べてどれくらい早いのか検証

そもそもクラスタ数がそんなに多くないのでそこまで早くなるのかは怪しい

（全探索モードとR-treeモードで分けて実装して検索時間とかをどこかに表示してもいい）

全世界的に行ったら目に見えて早いかも（めんどくさいのでやりたくない）

---

# まとめ

個人の実装

<br>
<br>

チームの実装

---

# Thank you
質問はありますか？
