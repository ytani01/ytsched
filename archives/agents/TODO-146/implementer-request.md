# TODO-146 implementer への依頼

## 目的

CSS のクラス名を、Bootstrap 由来のユーティリティ名から、アプリの役割を
表す名前へ変える。**見た目は 1px も変えない。**

まず `TODO.md` の「## TODO-146.」の節を最後まで読むこと。やること・
役割クラスへの畳み込み方・ライセンス表記を消せない理由・やらないこと・
検証の方法が、そこに全部書いてある。この依頼はそれを前提にした補足。

## 対象範囲

- `src/ytsched/webroot/static/css/my.css`
- `src/ytsched/webroot/templates/` の 7 枚
  （`base.html` `main.html` `edit.html` `sde.html` `trash.html`
  `mini_cal.html` `month.html`）
- `src/ytsched/webroot/static/css/my.css` 先頭コメント、`docs/Developer.md`
  の「外部のライブラリ」節（Bootstrap の記述を実態に合わせる）

**JavaScript・Python・テストは触らない。** `my-*` しか参照していないこと
は確認済みだが、もし `col-*` などを参照している箇所を見つけたら、直さずに
報告すること。

## やること

`TODO.md` のチェックリスト 6 項目すべて。特に:

1. テンプレートの要素ごとに 1 つの役割クラスへまとめる。既にある `my-*`
   がユーティリティを吸収する形にする（`container-fluid p-1 fixed-top
   my-bar` → `my-week-bar` など）
2. `col-N` の幅は役割クラスの中へ `grid-column: span N` として畳み込む
3. `px-1` `mt-1` `text-truncate` は `my.css` に定義が無い。テンプレート
   から消す（消しても計算値が変わらないことを確かめてから）
4. `longtext` `longtext-sw` `longtext-sw-label` に `my-` を付ける。
   JavaScript がこの名前を見ていないか grep で確かめること
5. 畳み込めなかった修飾クラス（`align-middle` `align-bottom` など）は
   `my-` を付けて残し、**なぜ畳み込めなかったかを一覧にして報告に書く**
6. `my.css` の並び順の意味（ユーティリティを前・`my-*` を後ろに置いて
   詳細度で勝たせる）は、ユーティリティが無くなると成立しなくなる。
   `!important` を増やさずに済む構成にし、先頭コメントを書き直すこと

## 完了条件

- テンプレート 7 枚に Bootstrap 由来の名前が残っていない
  （`container-fluid` `row` `col*` `p-*` `m-*` `text-*` `fw-bold`
  `align-*` `border` `d-none` `fixed-*` `alert*`）。
  `my-` 接頭辞に統一されている
- `my.css` が役割クラス中心の構成になっている
- 前後の計算値の突き合わせで、意図した差以外が 0 件
- `mise run test` が通る（`test_browser.py` を含む）

## 検証方法

**編集を始める前に、変更前の計算値を必ず先に採ること。** 採り忘れると
やり直しになる。

1. 一時ディレクトリを `--datadir` に指定してアプリを起動する
   （実データ `~/ytsched/data` は絶対に使わない）。データが要るので、
   `tests/make_test_data.py` か `tests/helpers.py` を見て、5 通り＋ゴミ箱＋
   月間表示を出せるだけの予定を用意する。ゴミ箱に入った項目、詳細のある
   項目、ToDo、キャンセル済みの項目を含めること
2. playwright で `body, body *` の `getBoundingClientRect` と、
   `padding` `margin` `border` `font` `color` `background-color`
   `text-align` `vertical-align` `display` `z-index` `position`
   `overflow` `white-space` `text-overflow` `text-decoration-line`
   `border-radius` `min-width` を JSON に吐く。要素の対応付けは DOM 順
   （深さ優先の通し番号）で取る。**クラス名が変わるのでクラスでは
   対応付けられない**
3. 採る画面は 7 通り × 幅 412px・800px:
   一覧 / 一覧の詳細を開いた状態 / 編集画面 / alert（不正な正規表現）/
   検索 / ゴミ箱 / 月間表示
4. 変更後に同じ手順で採り、1 要素ずつ差分を取る。**意図した差以外は
   0 件**にする。残った差は 1 つずつ理由を書く
5. `mise run test`

引っかかりどころ（TODO-047 で実測済み）:

- **画素比較は使えない。** 日付ブロックの `blink` の位相が撮るたびに
  違い、同じコードで 2 回撮っても 14,643 画素ずれる
- **`DISPLAY` が設定されていると chromium がフレームを返さない。**
  `env -u DISPLAY` を通すこと
- **`search_str` は `conf.json` にサーバ側で残る。** 前後で条件を
  そろえるため、採る前に `conf.json` を `{}` に戻す
- ブラウザは `/usr/bin/chromium` を使う（`tools/screenshot.py` 参照）
- `.d-none` の `!important` は、後ろの `my-*` に負けるとメニューの開閉が
  壊れるためのもの。畳み込むときはここが壊れないか実際に開閉して確かめる
- `.align-middle` は `base.html` の読み込み順に依存していた
  （Font Awesome は TODO-048 で無くなったので、いまも要るかを確かめる）
- `.longtext` の `min-width: 0` は `.row` の直接の子であることに依存
  している。入れ子を変えると `text-overflow: ellipsis` が黙って効かなくなる

## 報告

`archives/agents/TODO-146/implementer-report.md` に書く。含めるもの:

- 変更点（クラスの対応表: 変更前のクラス列 → 変更後の役割クラス）
- 残した修飾クラスの一覧と、畳み込まなかった理由
- `my.css` の構成をどう組み替えたか、詳細度の勝たせ方をどうしたか
- 計算値の突き合わせの結果（画面ごとの差分件数と、残った差の理由）
- `mise run test` の結果
- 残る懸念

返事は「終わったか・報告ファイルのパス・判断が要る点」の 5 行以内。
