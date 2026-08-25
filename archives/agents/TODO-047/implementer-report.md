# TODO-047 implementer 報告

Bootstrap をやめて、素の CSS にした。**テンプレートの `class="..."` は
1 文字も変えていない。**

## 変更したファイル

| ファイル | 内容 |
|---------|------|
| `src/ytsched/webroot/static/css/my.css` | reboot とユーティリティを追加（398 → 679 行、14KB）。`!important` を 5 → 1 か所に減らした |
| `src/ytsched/webroot/templates/base.html` | `bootstrap.min.css` の `<link>` を削除（Font Awesome は残した） |
| `README.md` | 「同梱しているライブラリ」から Bootstrap の行を外し、写した旨を追記 |
| `src/ytsched/webroot/static/vendor/bootstrap/` | `git rm -r` で削除（232KB + LICENSE） |

`my.css` は 3 段構えにした。並び順そのものが仕組みなので、コメントに
書いてある。

1. `:root` の変数（`--my-body-font-family`・`--my-gutter-x`）
2. 土台（reboot）
3. ユーティリティ（`container-fluid` / `row` / `col-*` / `alert` →
   `p-*` `m-*` → `text-*` `fw-bold` → `align-*` → `d-none` `border`
   `fixed-bottom`）
4. `my-*` などアプリ固有のクラス

## `!important`

**5 か所のうち 4 か所を外した。残したのは `.d-none` の 1 か所。**

| 外した | 確かめ方 |
|--------|---------|
| `.my-btn:active` | `:active` は擬似クラスぶんで詳細度が (0,2,0) になり、`.my-wday-N` (0,1,0) に元から勝っている。CDP の `CSS.forcePseudoState` で `:active` を強制し、背景が `rgb(255,255,0)` になることを実測 |
| `.my-date-block` / `.my-date-block-today` | `.border` をユーティリティの側（前）に置いたので、後ろの `my-*` が勝つ。計算値が `2px solid rgb(136,136,136)` / `4px solid rgb(34,136,255)` のままであることを実測 |
| `.my-canceled` / `.my-canceled-items > *` | もともと競合する指定が無かった。取り消し線の付く 5 要素すべてで `text-decoration-line` が変わらないことを実測 |

`.d-none` は残した。**要素を隠す指定なので、後ろの `my-*` に負けると
困る**（依頼書の判断に従った）。`#menu-sw` の `display` が `none` の
ままであることも実測した。

## テンプレートを触ったか → 触っていない

`align-middle` / `align-bottom` は、`<i>` `<input>` `<select>` といった
inline 要素に付いていて、どれも Grid の子ではない。`vertical-align` の
ままで意味が変わらないので、CSS 側だけで済んだ。

## 変更前と見比べた結果 → 違いは無し

キャプチャ同士の画素比較は、日付ブロックの `blink`
（`.5s × 10 回`）の位相が撮るたびに違うため、**同じコードで 2 回撮っても
14,643 画素ずれる**。画素数だけでは判断できないので、**DOM の実測値を
突き合わせた**。

playwright で全要素（`body, body *`）の `getBoundingClientRect` と、
`padding` `margin` `border` `font` `color` `background-color`
`text-align` `vertical-align` `display` `z-index` `position` `overflow`
`white-space` `text-overflow` `text-decoration-line` `border-radius`
`min-width` を吐かせ、変更の前後で 1 要素ずつ比べた（スクリプトは
scratchpad の `geom.py` / `cmp2.py`）。

- 対象は 5 通り × 幅 412px・800px（一覧・一覧の詳細を開いた状態・
  編集画面・alert・検索）
- 意図した差以外は **0 件**。意図した差は次の 3 つだけ

| 差 | 中身 |
|----|------|
| `display: flex → grid` | `.row` を Grid にしたため（狙いどおり） |
| `min-width: auto → 0px` | `.row > *` にまとめてかけたため（TODO-045） |
| 位置・寸法の 0.08px 以下のずれ | 百分率の幅（`91.66666667%`）と Grid の `1fr` の丸めの違い。最大 0.08px |

画素比較の残りも、この 0.08px ぶんのアンチエイリアスだった。編集画面の
27 画素の差を 6 倍に拡大して見たが、`(Tue)` の文字のふちだけで、
目では区別できない。

**キャプチャは撮り直しになった。** `search_str` は `conf.json` に
**サーバ側で残る**ので、main が撮った `todo047-before-menu_*` と
`todo047-before-search_*` は「会議」で検索した状態のまま撮れている
（`before-menu_closed` と `before-search_closed` は画素まで同一）。
撮る前に `conf.json` を `{}` に戻す必要がある。

`~/tmp/playwright-mcp/` に置いたもの:

- `todo047-impl-{main,menu,edit,alert,search}_*` — 変更後。5 通りとも
  `conf.json` を `{}` に戻してから撮った
- `todo047-cmpbefore-*` / `todo047-cmpafter-*` — menu と edit について、
  同じ手順で撮った前後の対。画素比較用
- `todo047-before-*`（main が撮ったもの）はそのまま残してある

## そのほか、自分で確かめたこと

- `mise run lint`（ruff format / ruff check / basedpyright / mypy）→ すべて通る
- `uv run pytest tests` → **418 passed**。ゴールデンマスターテストは
  落ちていない（HTML の中身を持っているテストは無く、`base.html` の
  `<link>` を減らしても影響しなかった）
- `grep -rn -i bootstrap src docs tests README.md tools` → 残っているのは
  `my.css` のコメント（出どころの告知）、`README.md` の追記、
  `main.html:86` のコメント（決まっていること 2 でそのまま残す）、
  Font Awesome の `.fa-bootstrap`（アイコン名）だけ

## 単独で決めたこと

1. **`col-7` `col-8` `col-12` も定義した。** テンプレートで使っている
   のは 1〜6・9〜11 だけだが、12 列のグリッドで番号が飛んでいるほうが
   後から読んで分かりにくい。3 行ぶんなので揃えた
2. **`--bs-body-font-family` は `--my-body-font-family` に改名した。**
   `--bs-` は Bootstrap の名前空間なので、無くなった以上まぎらわしい。
   値と TODO-040 の理由はコメントごと残してある
3. **ガターは `--my-gutter-x: 1.5rem` という変数にした。** Bootstrap の
   `--bs-gutter-x` と同じ値で、`.row` の負のマージンと `.row > *` ・
   `.container-fluid` のパディングの 3 か所から参照する
4. **`.row` のトラックを `repeat(12, minmax(0, 1fr))` にした。**
   `1fr` は `minmax(auto, 1fr)` の略で、中身に押し広げられる。
   `.row > *` の `min-width: 0` と両方そろえないと、TODO-045 と同じ
   ことが列の側で起きる
5. **reboot は、テンプレートに出てくる要素にかかるものだけ写した。**
   `<button>` は使っていないので、ボタン向けの 4 つ
   （`button{border-radius:0}`、`-webkit-appearance:button`、
   `::-moz-focus-inner`、`button:focus:not(:focus-visible)`）は
   写していない。`<a>` `<table>` `<hr>` `<ul>` `<p>` `<h1>`〜`<h6>` も
   テンプレートに無いので写していない。その旨は `my.css` のコメントに
   書いた
6. **`scroll-behavior: smooth` が無くなっても動きは変わらない**ことを
   確かめた。`my.js` の `scrollToId()` / `scrollToDate()` /
   `moveToMonday()` は `behavior` を引数で必ず渡していて（既定は
   `"smooth"`）、CSS 側の `scroll-behavior` を見る `"auto"` は
   どこからも渡していない

## main の判断が要ること

**`vendor/bootstrap/` の削除が、TODO-052 の docs コミットに紛れ込んで
いる。**

```
9c4e329 docs(todo): TODO 項目を足す作業を自動化できないか検討する件を TODO-052 として立てる
 TODO.md                                            | 22 +++++++-
 archives/agents/TODO-052/wording-report.md         | 65 ++++++++++++++++++++++
 .../webroot/static/vendor/bootstrap/LICENSE        | 21 -------
 .../static/vendor/bootstrap/bootstrap.min.css      |  6 --
```

こちらが `git rm -r` した直後（09:11 ごろ）に、main が `git commit` を
実行したため、staging に載っていた削除が一緒に入ってしまった。
**コミットを分け直すか、このままにするかは main が決めること。**
いまの作業ツリーは「bootstrap は無い」状態で正しく、`git status` は
`README.md` ・ `my.css` ・ `base.html` の 3 つが modified になっている。

## 気づいたが直さなかったもの

- **`tools/screenshot.py` は `DISPLAY` があると撮れない**（依頼書にある
  とおり `env -u DISPLAY` で回避した）。TODO-051 の範囲
- **`tools/screenshot.py` は `conf.json` に残る `search_str` を考えない。**
  上に書いたとおり、撮る前に状態を戻さないと前後で条件がそろわない。
  TODO-046（キャプチャの道具）か TODO-050（週を URL に持たせる）の
  どちらかの範囲に見えるが、今回の項目ではないので触っていない
- **`edit.html` には `m-*` の付いていない `row` が 7 つある**（依頼書は
  4 つと書いてあった。`p-1 my-edit-row` が 2 つ、`my-edit-row` が 3 つ、
  `div_detail`、`div_id`）。負のマージンはそのまま残してあるので、
  見た目は変わっていない
