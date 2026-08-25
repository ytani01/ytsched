# TODO-047. Bootstrap をやめて、素の CSS にする

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier + reviewer |
| 実施 | Opus 5 / effort high | implementer + verifier + reviewer + wording |
| 消費 | output 95,988 / cache_creation 534,403 / 概算 $19.7 |
|      | main 60% + implementer 25% + reviewer 12% + verifier 1% + wording 1%（料金の割合） |

消費の数字には、**同じ時間帯に挟まった TODO-051・TODO-052 を立てる作業も
入っている**（`--since '2026-08-25 08:40:00'` で切ったが、着手中に別の
項目を立てたため分けられない）。`wording` の行は、その 2 件のもの。

依頼と報告は `archives/agents/TODO-047/` にある。

## きっかけ

236KB の `bootstrap.min.css` を同梱していたが、テンプレートで使って
いたのはグリッド・余白・配置の 3 種類だけだった。JavaScript は使って
いない。

- フレームワーク側の変更に振り回される。既定のフォントが変わって行の
  高さがずれた件（TODO-040）のせいで、`--bs-body-font-family` を
  固定していた
- `my.css` にあった 5 か所の `!important` は、Bootstrap の詳細度に
  勝つためのものだった

## やったこと

### クラスの名前は変えなかった

`row` `col-N` `p-0` `text-center` のような名前を、そのまま `my.css` に
定義した。**テンプレート 4 つの `class="..."` は 1 文字も変えていない。**

`my-` を付けて名前を揃える案もあったが、テンプレートを全部書き換える
ことになり、見た目が変わる危険が増える。名前を変えるのは、必要なら
別の項目にできる。

### `my.css` の並び順そのものが仕組み

398 → 679 行。4 段構えで、**この順番に意味がある**。

1. `:root` の変数（`--my-body-font-family`・`--my-gutter-x`）
2. 土台（Bootstrap の reboot から写したもの）
3. ユーティリティ（Bootstrap から写したもの）
4. `my-` で始まるアプリ固有のクラス

**ユーティリティを前に、`my-*` を後ろに置くと、詳細度が同じなので
後ろが勝つ。** これで `!important` を書かずに済む。

### `!important` は 5 か所 → 1 か所

`.d-none` だけ残した。要素を隠す指定なので、後ろの `my-*` に負けると
メニューの開閉が壊れる。

外した 4 つ（`.my-btn:active` `.my-date-block` `.my-date-block-today`
`.my-canceled` / `.my-canceled-items > *`）は、外しても計算値が変わら
ないことを DOM で実測した。reviewer が、テンプレート中の各
`class="..."` について「ユーティリティと `my-*` のプロパティの重なり」を
ショートハンドの展開込みで総当たりし、意図しない打ち消しが無いことを
確かめている。

### `row` / `col-N` は CSS Grid にした

`.row { display: grid; grid-template-columns: repeat(12, minmax(0, 1fr)) }`
と `.col-N { grid-column: span N }`。**`.row` は 15 個あり、どれも子の
合計がちょうど 12 列**だったので、折り返しの挙動を移す必要は無かった。

ガター（溝）は Bootstrap と同じ `1.5rem` を `--my-gutter-x` に持たせ、
`.row` の負のマージンと `.row > *` ・ `.container-fluid` のパディングの
3 か所から参照する。**`edit.html` には `m-*` の付いていない `row` が
7 つあり**、そこでは負のマージンが効いているので、落とすと横幅が変わる。

`min-width: 0` は `.row > *` にまとめてかけた（TODO-045 で `.longtext`
だけに入れていたもの）。**Grid の子も flex と同じで既定が
`min-width: auto`** なので、`minmax(0, 1fr)` と両方そろえないと、列の
側で同じことが起きる。

### 土台（reboot）を写した

**ここがいちばん抜けやすいところ。** `bootstrap.min.css` は
normalize / reboot を含んでいて、これが無くなると、クラスをそろえても
見た目が変わる。

`body` の文字色 `#212529`（黒ではない）・`font-size: 1rem`・
`line-height: 1.5`、`*{box-sizing: border-box}`、
`button,input,optgroup,select,textarea{font-family: inherit …}`（日付・
時刻の入力欄と `<select>` の見え方が変わる）、
`::-webkit-datetime-edit-*{padding: 0}`、`img,svg{vertical-align: middle}`
（ゲージの SVG に効く）、`label{display: inline-block}` など。

**テンプレートに出てこない要素の分は写していない。** `<button>` `<a>`
`<table>` `<hr>` `<ul>` `<p>` `<h1>`〜`<h6>` は使っていない。reviewer が
reboot 全体を書き出して 1 つずつ照合し、写されていないのは対象の要素・
属性がテンプレートに無いものだけであることを確かめている。

### 読み込む順への依存を書き残した

`!important` を外したことで、**`.align-middle` は `base.html` で
`all.css` より後に `my.css` を読むことだけが根拠**になった。Font Awesome
の `.fa-lg` が `vertical-align: -0.075em` を同じ詳細度で持っているため。
並べ替えると、`fa-lg align-middle` を付けた 10 か所のアイコンの縦位置が
黙ってずれる。`base.html` と `my.css` の両方にその旨を書いた。
TODO-048 で Font Awesome が無くなれば、この依存も消える。

`.longtext` の `min-width: 0` が **`.row` の直接の子であることに依存**
していることも書いた。入れ子を深くすると `text-overflow: ellipsis` が
黙って効かなくなり、TODO-045 と同じ症状に戻る。TODO-049・TODO-050 の
「気をつけること」にも同じ注意を足した。

### ライセンス

`static/vendor/bootstrap/` はディレクトリごと消したので、MIT の
permission notice がリポジトリから無くなっていた。`LICENSE` の本文を
`docs/licenses/bootstrap-LICENSE` に残し、`README.md` と `my.css` の
先頭コメントから参照するようにした。

### 今回やらなかったこと

- **`scroll-behavior: smooth` の件。** Bootstrap の `:root` の指定は
  無くなったが、TODO-041 の回避（`my.js` に `"instant"` を渡している）は
  そのまま残した。`main.html:86` の「Bootstrap 5 の :root の指定で」と
  いうコメントも残してある。蒸し返すときは TODO-041 を見ること
- **Font Awesome。** 288KB あり、使っているのは 22 個だけだが、
  TODO-048 の範囲

## テスト

見た目を変えないための項目なので、テストでは確かめられない。

### DOM の計算値の突き合わせ（implementer）

**キャプチャの画素比較では判断できない。** 日付ブロックの `blink`
（`.5s × 10 回`）の位相が撮るたびに違うので、**同じコードで 2 回撮っても
14,643 画素ずれる**。

そこで playwright で全要素（`body, body *`）の `getBoundingClientRect`
と、`padding` `margin` `border` `font` `color` `background-color`
`text-align` `vertical-align` `display` `z-index` `position` `overflow`
`white-space` `text-overflow` `text-decoration-line` `border-radius`
`min-width` を吐かせ、変更の前後で 1 要素ずつ比べた。

対象は 5 通り（一覧・一覧の詳細を開いた状態・編集画面・alert・検索）
× 幅 412px・800px。**意図した差以外は 0 件。** 意図した差は
`display: flex → grid`、`min-width: auto → 0px`、百分率と `1fr` の
丸めによる 0.08px 以下のずれ、の 3 つだけ。

### そのほか

- `mise run lint`（ruff format / ruff check / basedpyright / mypy）… 問題なし
- `uv run pytest tests` … 418 件通過。HTML の中身を持っているテストは
  無いので、ゴールデンマスターテストは落ちなかった
- verifier が独立に確かめた（`archives/agents/TODO-047/verifier-report.md`）。
  起動 200、`bootstrap.min.css` の `<link>` が消えていること、その
  パスが 404 になること、Font Awesome の `<link>` は残っていること、
  ログに例外が無いこと。キャプチャも自分で撮り直して見比べている
- reviewer が写し漏れと値の写し間違いを照合した
  （`archives/agents/TODO-047/reviewer-report.md`）
- **`alert` はキャプチャに写らない。** 一覧のいちばん上にあり、画面は
  今日の日付まで自動で送られるため。要素だけ撮って確かめ、値も消える前の
  `bootstrap.min.css` と突き合わせた（`#58151c` / `#f8d7da` / `#f1aeb5` /
  `.375rem`、すべて一致）
- **320px 幅でも撮り比べた。** `min-width: 0` を広げたぶん、狭い画面で
  挙動が分かれる可能性を reviewer が挙げたため。レイアウトの差は無し

### 撮るときに引っかかったこと

- **`DISPLAY` が設定されていると chromium がフレームを返さず、
  `Page.screenshot` が必ずタイムアウトする。** `env -u DISPLAY` で回避
  した。TODO-051 として別に立てた
- **`search_str` は `conf.json` にサーバ側で残る。** 撮る前に
  `conf.json` を `{}` に戻さないと、前後で条件がそろわない
  （最初に撮った変更前のうち 2 通りが、これで撮り直しになった）
