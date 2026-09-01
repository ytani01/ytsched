# TODO-146. CSS のクラス名を、Bootstrap 由来のものからアプリの役割の名前へ変える

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier + reviewer |
| 実施 | Opus 5 / effort high | implementer + verifier + reviewer |
| 消費 | output 59,924 / cache_creation 521,818 / 概算 $10.2 |
|      | implementer 57% + main 25% + verifier 10% + reviewer 8%（料金の割合） |

依頼と報告は `archives/agents/TODO-146/` にある。

## きっかけ

Bootstrap そのものは TODO-047 でやめたが、そのときクラス名は変えな
かった。テンプレートを全部書き換えることになり、見た目が変わる危険が
増えるためで、「名前を変えるのは、必要なら別の項目にできる」と書いて
あった。その別の項目。

`container-fluid` `row` `col-N` `p-0` `text-center` のような名前が
テンプレートに 169 か所あり、どれもアプリの中では意味を持っていな
かった。

## やったこと

### 1 要素 1 クラスにした

**名前を差し替えたのではない。** `p-0`（29 か所）`text-center`
（18 か所）のようなユーティリティは、1 クラスが 1 つの役割に対応して
いないので、名前を置き換えるだけでは意味のある名前にならない。
テンプレートの要素ごとに重ね掛けを 1 つの役割クラスへまとめ、その
要素の役割で名前を付けた。

```
container-fluid p-1 fixed-top my-bar                → my-week-bar
container-fluid p-2 fixed-bottom my-bar my-menu-bar → my-menu-bar
alert alert-danger p-1 m-0 text-center              → my-error-box
container-fluid p-0 fixed-bottom my-bar             → my-edit-bar
container-fluid p-2 fixed-top my-bar                → my-trash-header
```

`col-N` の幅は役割クラスの中へ `grid-column: span N` として畳み込んだ。
`.row > *` が全部の列に掛けていた `min-width: 0` とガター由来の
パディングは、列ごとの役割クラスへ 1 つずつ配った。
`longtext` `longtext-sw` `longtext-sw-label` にも `my-` を付け、
定義の無かった `px-1` `mt-1` `text-truncate` はテンプレートから消した。

`.my-bar`（帯の色・背景）は、6 か所の帯の役割クラスへ個別に焼き込んだ。

### 畳み込めなかった修飾クラス

| クラス | 理由 |
|--------|------|
| `my-align-middle` / `my-align-bottom` | 同じ `my-icon-xl` でも付く箇所と付かない箇所があり、アイコンの役割クラスへ常時焼き込むと他の箇所の見た目が変わる |
| `my-fw-bold` | 「今日のとき」「重要なとき」だけ、別々の役割クラスに条件付きで付く |
| `my-row-end` | `.my-row-middle > .text-end` として効いていた位置指定。`.my-row-middle` の flex 化とセットで、3 つの異なる役割クラスに共通して要る |

### 並び順の決まりが要らなくなった

TODO-047 で作った「Bootstrap 由来のクラスを前に、`my-` のクラスを
後ろに置いて詳細度で勝たせる」という並び順の決まりは、重ね掛けを
やめたので成立させる必要が無くなった。**`!important` は全廃**
（TODO-047 で 5 か所 → 1 か所にして残していた `.d-none` も、要素ごとの
`my-menu-sw-hidden` / `my-longtext-sw` に分かれて単独セレクタになった）。

`.my-longtext` の `min-width: 0` も自分のクラスが持つ形になり、
「`.row` の直接の子であること」への依存（TODO-045・TODO-047）が消えた。

### ライセンス表記は消せない

**クラス名を変えても、Bootstrap の MIT 表記は外せない。** 写している
のはクラス名ではなく値のほうで、しかも大半は要素セレクタに付いている。

- 土台（reboot）の `body` `b, strong` `img, svg` `label` `select`
  `textarea` `::-webkit-datetime-edit-*` — 要素セレクタなので、
  クラス名を変えても何も変わらない
- `--my-body-font-family` のフォント指定一式
- `.my-error-box` の配色、`.my-sde` の枠線の色 `#dee2e6`、
  `border-radius: .375rem`、`z-index: 1030`、ガター `1.5rem`

`docs/licenses/bootstrap-LICENSE` と、`my.css` 先頭・`docs/Developer.md`
からの参照はそのまま残し、「写したのは reboot とこれらの値」という
書き方に直した。

### やらなかったこと

**写した値そのものの置き換えはしない。** 表記を外すにはそこまで要るが、
見た目が変わる。フォント指定は、値を変えると日付ブロックが 1 個あたり
2px 高くなり一覧が 176px 伸びる（TODO-040）。

## テスト

見た目を変えないための項目なので、テストでは確かめられない。TODO-047 と
同じやり方で見た。

### 計算値の突き合わせ（implementer）

playwright で `body, body *` の `getBoundingClientRect` と、`padding`
`margin` `border` `font` `color` `background-color` `text-align`
`vertical-align` `display` `z-index` `position` `overflow` `white-space`
`text-overflow` `text-decoration-line` `border-radius` `min-width` を
JSON に吐き、変更の前後で 1 要素ずつ比べた。**クラス名が変わるので、
要素の対応付けは DOM 順（深さ優先の通し番号）で取る。**

対象は 7 通り（一覧・一覧の詳細を開いた状態・編集画面・alert・検索・
ゴミ箱・月間表示）× 幅 412px・800px の 14 通り。要素数は前後で完全に
一致し、**差は 4 件だけ**。それもフッターのバージョン表示の中の
`({{ cache_size }})` の幅で、リクエストのたびに増えるキャッシュ件数が
撮影時刻で違っていただけだった（座標と他のスタイルは一致）。

TODO-047 の「引っかかったこと」は今回も全部そのまま起きる。
`conf.json` を `{}` に戻してから撮ること、`DISPLAY` を外すこと、
画素比較は使えないこと（`blink` の位相が撮るたびに違う）。

### そのほか

- `mise run test` … 589 件通過（`test_browser.py` を含む）
- verifier が独立に確かめた（`archives/agents/TODO-146/verifier-report.md`）。
  テンプレートに Bootstrap 由来の名前が残っていないこと（`{% set %}` で
  組み立てる `class_bg` などの中身も含む）、`my.css` とテンプレートの
  対応が両方向で取れていること、実際に画面を操作して
  **メニューの開閉・詳細の開閉**が壊れていないこと、ログに例外が
  無いこと。**発見は無し**
- reviewer が、変更前の `class="..."` をショートハンド込みで展開して
  役割クラスの計算値と 1 要素ずつ突き合わせた
  （`archives/agents/TODO-146/reviewer-report.md`）。写し漏れは無し。
  指摘は 2 件で、どちらも main が直した
  - `my.css` 先頭の「写した値」の列挙から、`.my-sde` に残る `#dee2e6`
    が抜けていた
  - 書き直す前のコメントが 3 か所に消し残っていた

### main が直したこと

- `main.html` `edit.html` の終わりの HTML コメントが `<!-- container -->`
  のまま残っていた。`tests/test_web.py` の `week_bar()` がその文字列を
  正規表現で探しており、implementer は**テストを触らない方針を守って
  コメントを二重に残していた**（`<!-- container --><!-- my-week-bar -->`）。
  これは要素を指すための目印なので、役割名に直してテスト側の正規表現も
  合わせた
- `tools/screenshot.py` の `DEF_TOGGLE` が `input.longtext-sw` のまま
  だった。`input.my-longtext-sw` に直し、`docs/Developer.md` の記述も
  合わせた
