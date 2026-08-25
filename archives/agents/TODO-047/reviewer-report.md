# TODO-047 reviewer 報告

`my.css` / `base.html` / `README.md` の変更と、`static/vendor/bootstrap/`
の削除を見た。**動くかどうかは見ていない**（verifier の担当）。

結論から書くと、**写し漏れ・値の写し間違い・`!important` を外したことに
よる意図しない打ち消しは、いずれも見つからなかった**。指摘は「いま壊れて
いる」ものではなく、**あとから黙って壊れる書き方**が 2 つと、`README.md`
とライセンス告知の話が 2 つ。

---

## 確信度の高い指摘

### 1. `align-middle` / `align-bottom` が、`base.html` の `<link>` の並び順に依存するようになった

`my.css:268-274`、`base.html:25-28`。

Font Awesome の `all.css:111-115` は `.fa-lg` に
`vertical-align: calc((6 / 20 - 0.375) * 1em)`（= `-0.075em`）を
入れている。詳細度は `(0,1,0)` で `.align-middle` と**同じ**。

これまでは Bootstrap の `.align-middle{vertical-align:middle!important}`
が並び順に関係なく勝っていた。今回 `!important` を外したので、
**`my.css` が `all.css` より後に読み込まれていることだけが根拠**になった。
いまの `base.html` は
`all.css`（25 行目）→ `my.css`（28 行目）の順なので**正しく効いている**
（implementer の DOM 実測で `vertical-align` に差が出ていないことと
一致する）。

問題は、この依存がどこにも書かれていないこと。`<link>` を並べ替える、
`my.css` を分割して先に読ませる、といった変更で**アイコンの縦位置だけが
静かにずれる**。CSS なので例外も警告も出ない。

効く箇所は `fa-lg` と `align-*` が同居している 10 個:

- `main.html:183, 184, 313, 343, 351, 357, 397`（`fa-lg align-middle`）
- `edit.html:200, 204, 208`（`fa-lg align-bottom`）

`base.html` の `<link>` のところか `my.css` の `.align-middle` の
ところに、一行「Font Awesome より後に読むこと」と書いておけば済む。
なお TODO-048 で Font Awesome が無くなればこの依存も消える。

### 2. `.longtext` の `min-width: 0` を `.row > *` に移したので、直接の子でなくなると黙って効かなくなる

`my.css:149-154`、`my.css:354-366`。

`min-width: 0` を `.longtext` 自身から `.row > *` に移したのは依頼書の
指示どおりで、いまは `sde.html:152` の `.longtext` が `.row` の直接の子
なので効いている。

ただし `.row > *` は**直接の子にしか当たらない**。TODO-049（1 画面
1 週間）・TODO-050（週を URL に持たせる）で `main.html` / `sde.html` の
入れ子を変えて `.longtext` が `.row` の孫になると、
`text-overflow: ellipsis` が静かに効かなくなり、**閉じているのに 2 行に
なる**という TODO-045 とまったく同じ症状に戻る。テストでは落ちない。

`.longtext` のコメントは「`.row > *` にまとめてかけてある」と書いて
あるので手掛かりは残っているが、**テンプレートの構造に依存している**
ことまでは書かれていない。TODO-049/050 に着手するときの注意として
どこかに残しておくのが安全（直すかどうかは main の判断）。

---

## 判断が要ること（main へ）

### 3. Bootstrap の MIT ライセンスの告知が、`LICENSE` を消したぶん薄くなっている

`my.css:1-13` に「Bootstrap 5.3.8 (MIT License, Copyright (c) 2011-2025
The Bootstrap Authors) から写した」とあるが、**MIT が要求している
permission notice の本文**（"The above copyright notice and this
permission notice shall be included in all copies or substantial portions
of the Software"）は、`vendor/bootstrap/LICENSE` ごと消えている。

写したのが「値だけ」で substantial portion に当たらないという整理も
成り立つ（実際、写っているのは 30 行ほどのプロパティ値）。ただ、
`README.md:206` は「ライセンス文書はそれぞれのディレクトリにあります」
と書いており、Bootstrap についてだけそれが成り立たなくなっている。

判断は main に委ねるが、**`LICENSE` の本文をどこかに残す**
（`docs/licenses/bootstrap-LICENSE` に置く、あるいは `my.css` の先頭
コメントに全文を入れる）のがいちばん安上がりで、あとで悩まずに済む。

### 4. `README.md` の追記が、実際に写した範囲より狭く読める

`README.md:216-219`。

> 使っていたのはグリッドと余白まわりのクラスだけだったので、その値を
> Bootstrap 5.3.8（MIT License）から写して…

実際に写したのはそれだけではなく、**reboot（土台）が含まれる**。
`body` のフォント・文字色 `#212529`・`line-height: 1.5`、
`*{box-sizing:border-box}`、`button,input,select,textarea` の
`font-family: inherit` など、見た目の土台になっている値がそっくり
入っている（`my.css:38-112`）。`my.css` のコメントのほうは
「土台の指定 (reboot) と…ユーティリティのクラス」と正しく書いてある
ので、README だけが狭い。

3 の判断とも関わる（「値を少し写しただけ」なのか「reboot ごと写した」
のかで、告知の重さの見え方が変わる）ので、そろえておくとよい。

---

## 確信度の低いもの

### 5. `.col` の意味が Bootstrap と変わっている

`my.css:159-161`。Bootstrap の `.col` は `flex: 1 0 0` で「**余った幅を
分け合う**」だが、今回の `.col` は `grid-column: span 12` で「**12 列
ぶん**」。

いまは `edit.html` で 1 行に 1 つだけ使っているので結果は同じで、
コメントにもそう書いてある。ただ、あとで `.col` と `.col-N` を同じ
`row` に混ぜると、Bootstrap なら 1 行に収まるところが**黙って 2 行に
折り返す**。`.col-12` と完全に同じ定義になっているので、
`.col` を使わず `.col-12` に寄せるという手もあるが、
「クラス名は変えない」という決めごとに触るので提案にとどめる。

### 6. `.row > *` の `min-width: 0` は Bootstrap より広い

Bootstrap の `.row > *` は `min-width: auto`（既定）のままなので、
中身が 1/12 幅に収まらないときは列が**広がって**いた。今回は
`minmax(0, 1fr)` ＋ `min-width: 0` なので、収まらないときは
**はみ出す / 切れる**。

412px・800px では implementer が実測して差が無いことを確かめており、
そもそも TODO-045 の狙いがこれなので指摘ではない。ただし
**もっと狭い画面（320px 程度）では挙動が分かれうる**。気になるなら
一度その幅でも見ておくとよい、という程度。

### 7. `main.html:86` のコメントが実態と合わなくなった

「"auto" は CSS の scroll-behavior に従うので、**Bootstrap 5 の :root の
指定で**アニメーションになってしまう (TODO-041)」とあるが、
Bootstrap が無くなったいま `scroll-behavior: smooth` はどこにも無い。
**利用者が「今回は触らない」と決めた範囲**なので指摘ではなく、
TODO-041 を蒸し返すときの覚書として書いておく。

---

## 確かめて、問題が無かったこと

依頼書の 1〜6 に対して、自分で確かめた結果。

### 写し漏れ（依頼 1）

テンプレート 4 つの `class="..."` を**複数行にまたがるものも含めて**
機械的に集め（`main.html:305` のように改行を挟むものがある）、
`my.css` と `all.css` の定義と突き合わせた。**未定義のクラスは無し。**

テンプレート変数から入るものも追った:
`class_bg`→`my-sde-{normal,holiday,todo,todo-near,todo-over}`、
`class_blink`→`blink`、`class_canceled`→`my-canceled`、
`class_canceled_items`→`my-canceled-items`、
`class_date_block`→`my-date-block` / `my-date-block-today`、
`class_today` / `class_important`→`fw-bold`、
`my-wday-{{ weekday }}`→`my-wday-0`〜`6`。**すべて定義済み。**

`my.js` は `classList` / `className` を一切触っていないので、
JavaScript から後づけされるクラスは無い。

### reboot の写し漏れ（依頼 2）

テンプレートに出てくる要素を機械的に集めた:
`html head title meta link script body header main footer div span i br
input select option textarea form label svg rect polygon strong`。
**`<button>` `<a>` `<table>` `<hr>` `<ul>` `<p>` `<h1>`〜`<h6>` は本当に
無い**（implementer の申告どおり）。

`bootstrap.min.css` の reboot 部分（`*{box-sizing}` から
`[hidden]{display:none!important}` まで）を全部書き出して、上の要素に
かかるものを 1 つずつ照合した。**写されていないのは、対象の要素・属性が
テンプレートに存在しないものだけ**だった:

- `[type=button] / [type=submit] / [type=reset] / button` 向けの
  `-webkit-appearance` ・ `cursor` ・ `::-moz-focus-inner` →
  テンプレートの `<input>` は `checkbox` `hidden` `date` `time` `text`
  の 5 種類だけで、該当なし
- `select:disabled` → `disabled` 属性なし
- `[list]…::-webkit-calendar-picker-indicator` → `list` 属性なし
- `[type=search]` 関連、`::-webkit-color-swatch-wrapper`、
  `::file-selector-button` → 該当する `type` なし
- `[hidden]{display:none!important}` → `hidden` 属性なし
  （`type="hidden"` は別物）

写した値も原本と 1 文字ずつ突き合わせた。`body` の `#212529` / `1rem` /
`400` / `1.5` / `#fff`、`.border` の `1px solid #dee2e6`
（`--bs-border-width` `--bs-border-style` `--bs-border-color` の展開）、
`.alert` の `1rem 1rem` / `margin-bottom:1rem` / `border-radius:.375rem`、
`.alert-danger` の `#58151c` / `#f8d7da` / `#f1aeb5`
（`--bs-danger-{text-emphasis,bg-subtle,border-subtle}`）、
`.fixed-bottom` の `z-index:1030`、`.p-*` `.m-*` `.text-*` `.fw-bold`。
**すべて一致。**

Font Awesome の `all.css` に要素だけのセレクタ（`svg{...}` のような）が
無いことも確かめた。`my.css` の reboot が FA に打ち消される心配は無い。

### Grid への置き換え（依頼 3）

**`.row` は 15 個あり、どれも子の合計がちょうど 12 列**だった。

| 場所 | 子 |
|------|-----|
| `sde.html:66` | 1 + 11 |
| `sde.html:138` | （`d-none` の input）+ 1 + 11 |
| `main.html:176` | 2 + 10 |
| `main.html:244` | 1 + 11 |
| `main.html:307` | 2 + 1 + 1 + 3 + 5 |
| `main.html:372` | 6 + 6 |
| `main.html:383` | 5 + 3 + 4 |
| `edit.html:120` | 2 + 2 + 2 + 4 + 2（`new_flag` のどちらの枝でも 12） |
| `edit.html:198` | 1 + 1 + 1 + 9 |
| `edit.html:232,245,256,264,273,282` | `col` 1 つ（= 12） |

**`col-*` の付いていない `.row` の直接の子**は `sde.html:139` の
`<input class="longtext-sw d-none">` だけで、`display:none` なので
grid item にならない。それ以外に `.row > *` の `span 12` が効いてしまう
子は無い。

ガターは原本と完全に一致している:

- Bootstrap `.row{margin-right/left: calc(-.5 * var(--bs-gutter-x))}`
  → `my.css:145-146` 同じ
- Bootstrap `.row>*{padding-right/left: calc(var(--bs-gutter-x) * .5)}`
  → `my.css:152-153` 同じ
- Bootstrap `.container-fluid{width:100%; padding …; margin: auto}`
  → `my.css:122-128` 同じ
- `--bs-gutter-y: 0` に対応する `.row{margin-top:0}` /
  `.row>*{margin-top:0}` も、値が 0 なので `.row{margin-top:0}` だけで
  等価

`--my-gutter-x` を `.row` / `.container-fluid` ではなく `:root` に
置いた点は、この 4 テンプレートの範囲では値が同じなので差は出ない。

### `!important` を外した判断（依頼 4）

**外して問題ない。** 並び順で解けていることを、次のように確かめた。

- `.my-btn:active` … 詳細度 `(0,2,0)`。同じ要素で `background-color` を
  争う相手は `.my-wday-N` `(0,1,0)` だけで、`!important` 抜きでも勝つ
- `.my-date-block` / `.my-date-block-today` … `.border`（`my.css:282`）
  より後ろ（454・461 行）なので勝つ。両者の前後関係も正しい
- `.my-canceled` / `.my-canceled-items > *` … 同じ要素で
  `text-decoration` を書いている規則が、`my.css` にも `all.css` にも
  無い。もともと争っていない

**「ユーティリティより後ろの `my-*` が意図せず打ち消していないか」は、
機械的に総当たりした**（テンプレート中の各 `class="..."` について、
含まれるユーティリティと `my-*` のプロパティの重なりを、
`padding` / `margin` / `border` のショートハンド展開込みで照合）。
出てきたのは次の 3 つで、**いずれも意図したもの**（Bootstrap でも
`.fixed-bottom` `.container-fluid` に `!important` は無く、`my.css` が
後に読まれていたので、以前とまったく同じ関係）:

- `.my-menu-bar` が `.fixed-bottom` の `z-index` を上書き
- `.my-bar-content` が `.container-fluid` の `width` を上書き
- `.my-bar-content` が `.fixed-bottom` の `position` / `bottom` /
  `z-index` を上書き（`my.css:324-326` のコメントどおり）

`.d-none` に `!important` を残した判断も妥当。`#menu-sw` は
`:checked` でメニュー開閉を担っているので、見えてしまうと機能が壊れる。

**`!important` を外したことで inline style に負けるようになる**という
経路も見た。テンプレートの `style="..."` は `main.html:110` の
`<main>` 1 か所だけで、ユーティリティのクラスは付いていない。
`my.js` が触る `style.display` / `.bottom` / `.transform` /
`.visibility` の対象（`.my-spinner` `#gage_r0` `.my-follow-keyboard`
と動的生成の form）も、同じプロパティを持つユーティリティとは同居して
いない。**問題なし。**

### 黙って壊れる書き方（依頼 5）

上の 1・2・5 のとおり。それ以外では、`my.css` が
「変数 → 土台 → ユーティリティ → `my-*`」の順に並んでいること自体が
仕組みになっているが、**その旨がファイル先頭・各節の見出し・
`.my-date-block-today` の直前と、3 か所に書いてある**ので、
これは黙って壊れる書き方には当たらないと判断した。

`scroll-behavior: smooth` が無くなった件も追った。`my.js` の
`scrollTo()` は 2 か所とも `behavior` を明示的に渡しており、
`scrollToId()` / `scrollToDate()` の既定値も `"smooth"` なので、
CSS 側の `scroll-behavior` を見る `"auto"` はどこからも渡らない。
implementer の申告どおり。

### そのほか

- CSS の波括弧の対応は 112 対 112 で釣り合っている。セミコロンの
  抜けも無し
- `grep -rn -i 'bootstrap\|bs-'`（`archives/` を除く）で残るのは
  `README.md` の追記、`my.css` のコメント、`main.html:86` のコメント
  （上の 7）、`TODO.md` だけ。`docs/` `src/README.md` `tests/` には
  Bootstrap への言及は無い
- `pyproject.toml` は静的ファイルを明示列挙していないので、
  `vendor/bootstrap/` を消したことによる packaging 側の直し漏れは無い
- `manifest.json` にアセットの一覧は無く、Service Worker も無いので、
  消したファイルを参照し続ける経路は無い

---

## 範囲外だが気づいたこと

- **`.col-7` `.col-8` `.col-12` は使われていない。** implementer が
  「番号が飛ぶと読みにくい」という理由で足したと報告しており、
  コメントにも書いてある。妥当な判断だと思う（指摘ではない）
- `.my-follow-keyboard {}` が空の規則のまま残っている（`my.css:678`）。
  今回の変更で入ったものではなく、`my.js` が
  `getElementsByClassName()` で拾うための目印なので動作に影響は無い
