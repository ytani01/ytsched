# TODO-038 implementer 報告（2 段目・style 属性を CSS へ）

依頼書: `archives/agents/TODO-038/implementer-request-2.md`

`style` 属性を `static/css/my.css` のクラスへ寄せた。あわせて
`sde.html` の `{% if sde.is_canceled() %}` の繰り返し 7 か所を 3 か所に
減らした（依頼書は「6 か所」と書いているが、数えると 7 か所あった）。

**見た目は、下の「見た目が変わったところ」1 件を除いて画素単位で同じ。**
自分でも旧版と新版のサーバを 2 つ立てて `compare -metric AE` で比べた。

## 変更したファイル

| ファイル | 要点 |
|---|---|
| `src/ytsched/webroot/static/css/my.css` | クラスを 40 個ほど追加（75 → 307 行）。`.my-bar-content` に `z-index: 100` を追加 |
| `src/ytsched/webroot/templates/main.html` | `style` 属性 39 → 1（残したのは `#main` の 1 つだけ） |
| `src/ytsched/webroot/templates/sde.html` | `style` 属性 18 → 0。取り消し線の `{% if %}` を 7 → 3 |
| `src/ytsched/webroot/templates/edit.html` | `style` 属性 23 → 0 |

`style="` の数は **80 → 1**。

## 残した `style` 属性

`main.html` の `<main id="main">` の 1 つだけ。

```html
<main id="main" style="background-color:#FFF; visibility: hidden;
          padding-left:22px">
```

`visibility` を JavaScript（`my.js` の `scrollToId()` と `main.html` の
`onloadHdr()`）が書き換えるので、この属性はどのみち残る。同じ属性に
入っている `padding-left: 22px` は依頼書が「動かさない」としているので、
まとめて元のままにした。

JavaScript が触る他のものも、インラインには**置いていない**が、CSS へも
移していない（初期値を持っていなかったので、書くところが無い）。

- `#loadingSpinner` の `display` — `.my-spinner` には入れていない
- ゲージの `bottom` / `display` — `.my-gage-r` には入れていない

## 追加したクラス

`my-` を付けた（`.longtext` には揃えていない。依頼書のとおり）。

- 文字の大きさ: `.my-fs-xx-small` `.my-fs-x-small` `.my-fs-small`
  `.my-fs-medium` `.my-fs-large` `.my-fs-x-large`
- 行の高さ: `.my-lh-10` `.my-lh-12` `.my-lh-14` `.my-lh-16`
- その他: `.my-fw-bold` `.my-va-middle` `.my-va-bottom` `.my-hidden`
- 部品ごと: `.my-spinner` `.my-gage-r` `.my-gage-base` `.my-gage-label`
  `.my-date-block` `.my-date-block-today` `.my-date-col` `.my-wday-0`〜`6`
  `.my-add-btn` `.my-menu-bar` `.my-home-date` `.my-sde`
  `.my-sde-normal` `.my-sde-holiday` `.my-sde-todo` `.my-sde-todo-near`
  `.my-sde-todo-over` `.my-sde-sub` `.my-canceled` `.my-canceled-items`
  `.my-edit-main` `.my-edit-body` `.my-input-time` `.my-input-type`
  `.my-input-place` `.my-input-full`

`text-align` は Bootstrap の `.text-left` `.text-center` `.text-right` を
そのまま使った（`!important` 付きで、計算後の値は元と同じ）。

## 自分で決めたこと

### 1. `border-radius` と `font-size: 0` も CSS へ移した

依頼書は「そのまま残すもの（消さない・動かさない）」に
`border-radius` の値と `sde.html` の `font-size: 0` を挙げている。
**値は 1 文字も変えていないが、置き場所は CSS へ移した。**

そうしないと、依頼書が「クラスにする」と指示している 3 か所
（日付ブロックの枠・曜日の背景色・`sde.html` の背景色）で `style` 属性が
そのまま残ってしまい、指示どうしが噛み合わないため。「動かさない」は
「値を変えたり消したりしない」の意味だと読んだ。画素単位で同じであることは
下の比較で確かめた。

### 2. 取り消し線は 2 つのクラスに分けた

依頼書は「時刻の欄・本文の欄・詳細の欄の 3 か所」と指示しているが、
1 つのクラスでは同じ見え方にならなかったので、2 つに分けた。

```css
.my-canceled { text-decoration: line-through !important; }
.my-canceled-items > * { text-decoration: line-through !important; }
```

- 時刻の欄（`col-1`）と詳細の欄は、中身が文字だけなので `.my-canceled`
- 本文の欄（`col-11`）は `.my-canceled-items`。理由は 2 つ
  - `col-11` に直接引くと、`<span>` どうしの**間の空白にも線が入る**
    （いまは入っていない）。子要素ごとに引けば入らない
  - ToDo の日付・時刻の欄は `display: inline-flex` で、CSS の仕様上、
    **親からの取り消し線は inline-flex の中へ伝わらない**。子要素ごとに
    指定すればその要素自身に引かれる

`!important` は外していない。外すと Bootstrap に負ける可能性があると
依頼書にあり、確かめるより残すほうが安全なので、そのままにした。

### 3. `sde.html` の詳細に `{{ '\n' + detail + '\n' }}` を使った

開いたときの `.longtext` は `white-space: pre-wrap` なので、**テンプレート
の中の改行がそのまま見える。** `{% if %}` を減らすとテンプレートの
テキストの塊が減り、Tornado の空白の扱いが変わって、詳細の前後の空行が
減ってしまう。そこで式の中で `\n` を足して、元の見え方に合わせた。
理由はテンプレートにコメントで書いた。

### 4. 効かない宣言を 2 種類、そのまま落とした

どちらも**元から効いていない**ので、見た目は変わらない
（画素単位の比較でも差は出ていない）。

- `main.html` の `<select id="search_n_in" style="vertical-align; middle;">`
  — `:` ではなく `;` なので宣言として成立していない。
  `.my-va-middle` に**置き換えると見た目が変わってしまう**ので、消した
- `edit.html` の `font-width: bold`（2 か所）— `font-width` という CSS
  プロパティは無い。`.my-fs-x-large` だけにした

### 5. `.my-bar-content` に `z-index: 100` を足した

`main.html` から `style="z-index: 100;"` を外したら、閉じているはずの
メニューがメニューバーの上に出てしまった。この要素は Bootstrap の
`.fixed-bottom`（`z-index: 1030`）も付いていて、インラインの 100 が
それを打ち消していた。`.my-bar-content` に移して直した。
**画素単位の比較で見つけた。**

## 見た目が変わったところ（1 件）

**取り消し済みの予定の「詳細」を開いたとき、上下の空行が 2 行ずつ減る。**
普通の予定と同じ見え方になる。1 行の詳細で、欄の高さが 122px → 62px。
普通の予定（取り消しでないもの）の詳細は、開いても閉じても**元のまま**。

元は、取り消し線の `<span>` が入れ子になっていたぶんだけテキストの塊が
増え、`white-space: pre-wrap` で上下に 2 行ずつ余分な空行が出ていた。
入れ子をやめるのがこの項目の眼目なので、ここだけは合わせられなかった
（合わせるには `is_canceled()` で改行の数を変える必要があり、消したはずの
条件分岐が戻ってくる）。**元の空行は、意図した余白ではなく、テンプレートの
書き方から出ていたものだと判断した。**

## 確かめたこと

### 画素単位の比較

`git archive HEAD` で取り出した webroot（＝変更前）を別ポートで動かし、
同じデータ・同じ画面サイズで撮って `compare -metric AE` で数えた。
データは一時ディレクトリに作った
（`~/ytsched/data` は使っていない。ポート 12345 にも触れていない）。

| 画面 | 大きさ | 違う画素 |
|---|---|---|
| 一覧 | 412x2400 | **0** |
| 一覧（横長） | 740x1400 | **0** |
| 一覧（検索） | 412x2400 | **0** |
| 編集（普通の予定） | 412x2400 | **0** |
| 編集（取り消しの予定） | 412x2400 | **0** |
| 一覧（メニューを開き、詳細を全部開く） | 412x2400 | **0**（※） |

※ 取り消し済みの予定に詳細が付いていないデータでの結果。付いていると、
上に書いた空行のぶんだけ差が出る。

テストに使ったデータには、普通の予定・重要（★）・取り消し（`x` と
`(欠`）・祝日・ToDo（期限が過去 / 1 週間以内 / 先）・場所あり・詳細が
複数行、を入れて、`sde.html` の分岐を全部通した。今日・平日・土日の
日付ブロックも入っている。

### そのほか

- `mise run lint` — ruff format `23 files left unchanged`、ruff check
  `All checks passed!`、basedpyright `0 errors, 0 warnings`、
  mypy `Success: no issues found in 20 source files`
- `mise run test` — `412 passed`
- 起動確認（ポート 10096、`--datadir` は一時ディレクトリ）
  - `/ytsched/` 200、`/ytsched/edit/` 200、
    `/ytsched/edit/?date=…&sde_id=…` 200、
    `/ytsched/?search_str=予定` 200、`/ytsched/static/css/my.css` 200
  - POST で予定を 1 件追加 → 一覧に出て、`my-sde my-sde-normal blink` が
    付くこと、`my-wday-0`〜`my-wday-6` が 7 種類とも出ること、
    `my-date-block my-date-block-today` が 1 つだけ出ることを確認
- ブラウザの JavaScript の例外（chromium `--dump-dom --enable-logging`）
  — 一覧 412x915 / 740x360、編集 412x915 / 740x360 の 4 通りで
  `Uncaught` / `TypeError` は 0 件
- クラス名の突き合わせ — テンプレートに出てくる `my-*` が全部 `my.css` に
  あること、`my.css` の `.my-*` が全部使われていること（`.my-wday-N` は
  `my-wday-{{ weekday }}` で組み立てているので、名前そのものでは出ない）
- 使わなくなったテンプレート変数（`bg_color` `bg_color_wday`
  `date_border` `font_size` `font_weight` `type_font` `title_font`）が
  残っていないことを grep で確認

## 気づいたが直さなかったもの

- **`main.html` の `<script>` の中が、HEAD から 1 桁ぶんインデントが変わって
  いる。** これは 1 段目の変更で、私は触っていない
  （`git diff` が大きく見えるのはこのため）。`{# -*- engine: tornado -*- #}`
  の 1 行が増えているのも 1 段目
- `my.css` の `.my-gage` にある `/* background-color: #FFF; */` は
  コメントアウトされたまま（**1 段目の依頼にも 2 段目の依頼にも無い**）
- `edit.html` のコメントアウトされた `window.addEventListener('resize', …)`
  も残っている（同上）
- `.longtext` `.longtext-sw` `.longtext-sw-label` `.blink` は `my-` が
  付いていないが、依頼書のとおり揃えていない
- `sde.html` の外側 `<!-- … -->` の中で `{% set %}` を書く書き方は元の
  ままにした（Tornado はコメントの中でも `{% %}` を実行する）

## うまくいかなかったところ

- ヘッドレスの chromium で一覧の画面を撮ると、`--days` が大きいときに
  スクロールしてしまって白い画像になった。`--days 4` にして 1 画面に
  収めることで撮れるようにした
- チェックボックス（メニューの開閉、詳細の開閉）は URL では指定できないので、
  取得した HTML に「読み込み後に全部チェックする」`<script>` を足したものを
  `static/` に置いて、同じ生成元から読ませて撮った

## 動かしたもの（後片付け済み）

比較のために立てたサーバ（ポート 10092〜10096）は全部止めた。
`pgrep` で残っているのは、利用者の 12345 と別の担当の 10099 だけ。
一時ファイルは `/tmp` の作業ディレクトリの中だけで、リポジトリには
置いていない。
