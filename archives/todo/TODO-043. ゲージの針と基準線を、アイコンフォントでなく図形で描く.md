# TODO-043. ゲージの針と基準線を、アイコンフォントでなく図形で描く

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort medium | main のみ + verifier + wording |
| 実施 | Opus 5 / effort high | main のみ + verifier + wording + runner |
| 消費 | output 31,209 / cache_creation 286,990（全体） | verifier 61% + main 24% + wording 10% + runner 5% |

## きっかけ

TODO-042 を済ませたあと、利用者から「`centerY - 9` について、他にもっと
いい方法はあるのか」と聞かれた。**針と基準線を図形として描き直せば、
TODO-042 で入れた補正が 3 つとも要らなくなる**と答えたのが、この項目。

## 何が問題だったか

針と基準線は図形なのに、Font Awesome のアイコン（`fa-caret-right` /
`fa-grip-lines`）で描いていた。TODO-040 で FA を 5.6.1 から 7.3.1 へ
上げたときに既定値が変わって位置がずれ、TODO-042 で 3 つの補正を入れて
直した。

- `.my-gage-text { --fa-width: auto; }` — FA 7 が付ける 1.25em の箱を戻す
- `.my-gage-r .my-gage-text { transform: translate(-0.127em, 50%); }` —
  字面の左余白を戻す
- `main.html` の `centerY - 9` — 針と基準線の縦位置を合わせる

**3 つともフォント側の都合を打ち消すためのもの**で、次に FA を上げれば
また合わせ直しになる。

## やったこと

分担と、その理由は
[archives/agents/TODO-043/README.md](../agents/TODO-043/README.md)。

### 1. グリフの実寸をフォントから測った

「見た目を変えない」の拠り所が要るので、同梱している
`fa-solid-900.woff2` から fontTools で輪郭を取り出した
（`unitsPerEm = 512`）。

| | 字面（units） | 実寸 | SVG にした値 |
|---|---|---|---|
| `fa-caret-right`（`fa-2x` = 36px） | 194 x 298 | 13.6 x 21.0px | 14 x 21 |
| `fa-grip-lines`（`fa-xs` = 13.5px） | 448 x 192 | 11.8 x 5.1px | 12 x 5 |

基準線の棒は 64 units（1.7px）、隙間も 64 units、角丸は 32 units
（0.85px）。`fa-caret-right` の左余白が 65 units＝`0.127em` で、
TODO-042 で `transform` に書いた値の出どころもこれだと確かめられた。

fontTools は `uv run --no-project --with fonttools --with brotli` で
一時的に使った。**プロジェクトの依存は増えていない**（TODO-041 で
Playwright をこう使ったのと同じ）。

### 2. SVG に置き換えた（`main.html`）

```html
<svg id="gage_r" class="my-osd-base my-gage-r"
  viewBox="0 0 14 21">
  <polygon points="0,0 14,10.5 0,21" />
</svg>

<svg id="gage_r_base" class="my-osd-base my-gage-base"
  viewBox="0 0 12 5">
  <rect x="0" y="0" width="12" height="1.7" rx="0.85" />
  <rect x="0" y="3.3" width="12" height="1.7" rx="0.85" />
</svg>
```

`viewBox` の値と CSS の `width` / `height` を同じにしてあるので、
**SVG の中の座標がそのまま画面のピクセルになる**。

### 3. CSS を整理した（`my.css`）

TODO-042 の補正 2 つを消し、大きさと位置の指定に置き換えた。

```css
.my-gage-r {
    left: 0px;
    width: 14px;
    height: 21px;
    fill: #000;
    opacity: 0.2;
    transform: translateY(50%);
}
```

`.my-gage` は針と基準線から外れ、**目盛りのラベルだけが使うクラスに
なった**ので、その旨のコメントを置いた。

### 4. `centerY` に戻した（`main.html`）

```
-     elGageRBase.style.bottom = `${centerY - 9}px`;
+     elGageRBase.style.bottom = `${centerY}px`;
```

**位置合わせの考え方が変わったので、9 の補正が不要になった。**
前は、大きさの違う 2 つのアイコンの `<i>` に同じ
`transform: translate(0%, 50%)` をかけていたため、下へずれる量が
それぞれ違った（ずれる量は要素の高さの半分）。その差を吸収していたのが
`9` だった。

いまは `<svg>` 自身に `translateY(50%)` をかけている。SVG は
`width` / `height` が確定した箱で、**その箱＝図形そのもの**なので、
針も基準線も「図形の中心が `bottom` の値に来る」で揃う。

### 角の丸みは再現しなかった

`fa-caret-right` は 3 つの角が丸められている（グリフに `curveTo` が
入っている）。今回の `<polygon>` は鋭角なので、**10 倍に拡大すると
分かる差がある**。

グリフの輪郭をそのまま SVG の `path` に写せば見た目は完全に一致するが、
**鋭角のままにした。** FA の丸みはアイコンとしてのデザインであって、
このゲージが必要とした形ではない。`points` が 1 行で読め、形をあとから
変えるのも楽なほうを採った。`stroke-linejoin: round` で近似する案も
比べたうえで見送っている。

## テスト

**テストは足していない。** 変えたのはテンプレートの HTML と CSS で、
Python 側のテストからは触れない。

verifier に確かめさせた
（[verifier-report.md](../agents/TODO-043/verifier-report.md)）。
`HEAD`（FA 版）と作業ツリー（SVG 版）を別ポートで起動し、`--datadir` に
一時ディレクトリを指定して、同じテストデータでスクリーンショットを撮って
比べている。

- **針の左端** — 三角形の bbox は old / new とも `x: 0〜14`。TODO-042 で
  x = 0 に合わせたところから動いていない
- **重なり方** — 三角形の bbox は `y: 2021〜2041` → `2022〜2041`
  （1px の差はアンチエイリアスの閾値程度）、基準線は `y: 2030〜2033` で
  **1 ピクセルも動いていない**
- **画面全体** — `compare -metric AE` の差分は 412 幅・740 幅とも
  **134 画素**で、bbox は `x: 0〜14, y: 2020〜2043`（ゲージの領域そのもの）。
  それ以外は 1 画素も変わっていない
- **目盛りのラベル** — `top` / `left` / `width` とも完全一致

runner の結果（[runner-report.md](../agents/TODO-043/runner-report.md)）。
`ruff format` / `ruff check` / `basedpyright` / `mypy` とも通り、テストは
**418 件 pass**。

## 次に同じことをするときの申し送り

- **`getBoundingClientRect()` は「見た目」の指標として万能ではない。**
  箱の大きさが図形の実寸と違うとき（フォントアイコンのように
  `font-size` 由来の余白があるとき）、箱の中心で比べると、実際には
  動いていないものが動いたように見える。今回も箱で比べると old / new で
  18.5px ずれて見えたが、画素を直接読むと変わっていなかった。
  **最終的な判断は画素で行う**
- **woff2 からグリフの実寸を測れる。** `fontTools` で輪郭を取り出せば、
  アイコンを図形に置き換えるときの寸法の拠り所になる。
  `uv run --no-project --with fonttools --with brotli` で、依存を増やさずに
  使える
- **`chromium --headless` の `--window-size` と
  `document.documentElement.clientHeight` は一致しない**（`4000` 指定に
  対して実測 3857、差は約 143px）。2 つの版を同じ条件で比べる分には
  影響しないが、`getBoundingClientRect()` の値からスクリーンショットの
  画素位置を逆算するときはずれる

## 文書の語（wording の指摘と、どう決めたか）

`wording` が前例の無い語を 8 挙げた（前例が少ないものを含めると 14）。
[wording-report.md](../agents/TODO-043/wording-report.md) の
「済ませるコミット」の節。**どれも直していない。**

- **フォント・SVG・DOM の識別子はそのまま。** `unitsPerEm`・`curveTo`・
  `stroke-linejoin`・`clientHeight`・`documentElement`・`fontTools` は、
  仕様やライブラリにその名前で存在するもの。訳したり言い換えたりすると、
  かえって元をたどれなくなる
- **「鋭角」「逆算」「拠り所」「近似する」「アンチエイリアスの閾値」は
  普通の日本語**、または一般的な用語の組み合わせ
- **verifier の報告に出てくる「罠」「差分画素」「再帰的に発火」も
  そのまま。** 報告ファイルは、そのとき何を書いたかの記録なので直さない
  （TODO-041・TODO-042 と同じ）
