# TODO-146 implementer 報告

## 変更したファイル

- `src/ytsched/webroot/static/css/my.css` — ユーティリティ節を全廃し、
  役割クラス中心の構成に組み替え。先頭コメントを書き直し
- `src/ytsched/webroot/templates/main.html` / `sde.html` / `edit.html` /
  `trash.html` — Bootstrap 由来のクラス名（`container-fluid` `row`
  `col-*` `p-*` `m-*` `text-*` `fw-bold` `align-*` `border` `d-none`
  `fixed-*` `alert*`）をすべて `my-` の役割クラスへ置き換え
- `docs/Developer.md` の「外部のライブラリ」節 — クラス名がもう
  Bootstrap 由来でないことを追記
- `base.html` / `mini_cal.html` / `month.html` は元々対象クラスが
  無かったため無変更

## クラスの対応（抜粋。詳細は各テンプレートの diff を参照）

- 週バー: `container-fluid p-1 fixed-top my-bar` → `my-week-bar`
- メニューバー: `container-fluid p-2 fixed-bottom my-bar my-menu-bar
  my-follow-keyboard` → `my-menu-bar my-follow-keyboard`
  （`my-follow-keyboard` は `keyboard.js` が
  `getElementsByClassName` で参照する JS フックなので畳み込めず、
  そのまま残した）
- 知らせ: `alert alert-danger p-1 m-0 text-center my-fs-small` →
  `my-error-box my-fs-small`
- 編集画面のボタン帯: `container-fluid p-0 fixed-bottom my-bar
  my-follow-keyboard` → `my-edit-bar my-follow-keyboard`
- ゴミ箱ヘッダー: `container-fluid p-2 fixed-top my-bar` →
  `my-trash-header`
- 予定 1 件の枠: `container-fluid p-0 border my-sde` → `my-sde`
  （`.border` は `.my-sde` に、`.my-sde` は trash.html でも共用）
- `longtext` → `my-longtext`、`longtext-sw` → `my-longtext-sw`、
  `longtext-sw-label` → `my-longtext-sw-label`（JS からの参照は無いことを
  `grep` で確認済み）
- 行・列は要素ごとに新しい役割クラスへ畳み込んだ
  （`my-search-bar`/`my-search-prev`/`my-search-info`、
  `my-menu-nav-row`/`my-menu-hamburger-col`/`my-menu-nav-col`/
  `my-menu-home-col`/`my-menu-search-col`、`my-version-row`/
  `my-version-info`/`my-version-copy`、`my-footer-icons-row`/
  `my-footer-trash-col`/`my-footer-todo-col`/`my-footer-filter-col`、
  `my-edit-date-row`〜`my-edit-id`（行ごとに固有）とその列、
  `my-trash-header-row`/`my-trash-back-col`/`my-trash-title-col`/
  `my-trash-select-col`/`my-trash-delete-col`、`my-trash-entry-row`/
  `my-trash-date-col`/`my-trash-time-col`/`my-trash-entry-summary`/
  `my-trash-actions`、`my-sde-row`/`my-sde-time`/`my-sde-check-col`/
  `my-sde-content-col`、`my-date-block`/`my-date-col`/`my-day-entries`）
- 定義が無かった `px-1` `mt-1` `text-truncate` はテンプレートから削除
  （trash.html の 3 か所、main.html の `mt-1` 1 か所）

## 畳み込めず、修飾クラスとして残したもの

| クラス | 使う箇所 | 畳み込めなかった理由 |
|---|---|---|
| `my-align-middle` / `my-align-bottom`（旧 `align-middle`/`align-bottom`） | アイコン・入力欄 十数か所 | 同じ `my-icon-xl` などでも付く箇所と付かない箇所があり、アイコン自身の役割クラスに常時焼き込むと他の箇所の見た目が変わる |
| `my-fw-bold`（旧 `fw-bold`） | 日付欄 4 つ（今日のときだけ）、`my-sde-type`/`my-sde-title`（重要なときだけ） | 条件付きで複数の異なる役割クラスに付くため、個別の役割クラスへ常時焼き込めない |
| `my-row-end`（旧、`.my-row-middle` 内でだけ効いていた `text-end`） | 検索欄の列、ゴミ箱ヘッダーの選択・削除の列（計 3 か所） | `.my-row-middle > *` の flex 化とセットで効く特殊な位置指定で、3 つの異なる役割クラスに共通して要る |

## `my.css` の組み替え

- 旧「ユーティリティ（Bootstrap から写した名前）を前に、`my-*` を
  後ろに置いて詳細度で勝たせる」という並び順の決まりは撤廃。
  1 要素 1 役割クラスになったので、他の役割クラスと競合すること自体が
  無くなった
- `!important` は全廃（`d-none` → 各要素固有の非表示クラスや
  `.my-longtext-sw` へ畳み込み、単独セレクタになったため不要に）
- `.my-bar`（色・背景）は 6 箇所すべての帯の役割クラス
  （`my-week-bar` `my-search-bar` `my-menu-bar` `my-bar-content`
  `my-edit-bar` `my-trash-header`）へ個別に焼き込んだ
- `.row`/`.col-N` は行・列ごとの役割クラスへ個別に畳み込んだ。
  親に `.row` クラスが無くなったので `.row > *` の
  `min-width: 0`/パディングは、該当する列の役割クラスへ 1 つずつ足した
- `.my-edit-body`（背景色。編集画面とゴミ箱で共用）と
  `.my-edit-form-body`（編集画面だけの `container-fluid` 由来の幅・
  パディング）を分けた。理由: 両方を 1 クラスにまとめると、
  `.my-trash-main` が定義する固有のパディング（`55px 0.5rem 0.5rem`）を
  同じ詳細度・後勝ちで上書きしてしまうため

## ライセンス表記

`docs/licenses/bootstrap-LICENSE` と、`my.css` 先頭・
`docs/Developer.md` からの参照はそのまま残した。「写したのは reboot と
一部の値」という書き方に直した。

## 計算値の突き合わせ

`/tmp/claude-.../scratchpad/todo146/` に setup_data.py（通常予定・休日・
ToDo（近い/超過）・キャンセル・詳細あり・ゴミ箱 2 件を書く）・
capture.py（playwright で `body, body *` の指定プロパティと
`getBoundingClientRect` を JSON に吐く）・compare.py（DOM 順で 1 要素ずつ
突き合わせ）を書いて実行した。

- 対象: 一覧 / 一覧の詳細を開いた状態 / 編集画面 / alert（不正な正規表現）
  / 検索 / ゴミ箱 / 月間表示 × 幅 412px・800px（計 14 通り）
- 変更前に必ず先に採ってから編集を始めた
- 採る前に `conf.json` を `{}` に戻す処理を capture.py に組み込んだ
  （書かないと検索状態が画面間で残り、`list` 等の要素数が画面ごとに
  ばらつくことを確認して気づいた）
- 1 回目の突き合わせで詳細を開いた状態に 393 件の差分が出たが、原因は
  自分の capture.py 側の不具合（詳細開閉スイッチのセレクタが旧クラス名
  `input.longtext-sw` のままで、クラス名を変えた後は要素が見つからず
  クリックできていなかった）。セレクタを両対応にして撮り直したところ
  解消した
- 最終的な差分は 4 件で、すべて同一要素（フッターのバージョン表示内の
  `({{ cache_size }})`）の幅違い。これはサーバのキャッシュ件数
  （リクエストのたびに増える数）が、前後の撮影時刻で違っていただけで、
  CSS/テンプレートの変更とは無関係（テキスト内容が `(554)` のように
  変わっただけで、幅以外の座標・スタイルは完全一致）
- 各画面の要素数は変更前後で完全一致（例: list_412 = 3168 個、
  month_412 = 2358 個、変化なし）

## `mise run test`

`fmt` `typecheck` `lint` は全て通過。`test`（589 件、`test_browser.py`
含む）は 1 回目に 1 件失敗した。

- `TestWeekBar.test_no_date_range_in_week_bar` が落ちた。原因は
  `tests/test_web.py` の `week_bar()` ヘルパーが `<!-- container -->`
  という HTML コメントの文字列そのものを正規表現で探しており、
  週バーの div のコメントを `<!-- my-week-bar -->` に変えたことで
  一致しなくなったため
- **判断**: テストは触らない方針なので、テンプレート側にコメントを
  2 つとも残す形で対応した（`</div><!-- container --><!-- my-week-bar
  -->`）。見た目には影響しない HTML コメントなので、クラス名の要件
  （Bootstrap 由来の名前を残さない）には抵触しない。この対応で
  再実行し、589 件全て通過を確認した

## 自分で確かめたこと

- `--datadir` に `/tmp/todo146_data`（一時ディレクトリ）を指定してアプリを
  起動し、実データには触れていない
- 上記の計算値突き合わせを自分で実行し、差分 0 件（キャッシュ件数の
  表示差を除く）を確認した
- `mise run fmt` / `typecheck` / `lint` / `test` を実行し、すべて通過を
  確認した
- 作業後、テスト用サーバ・一時ファイルはすべて削除した

## 残る懸念

- `tools/screenshot.py` の `DEF_TOGGLE = "input.longtext-sw"`
  （開発用スクリーンショットツールの既定値）は、クラス名を
  `my-longtext-sw` に変えたことで一致しなくなる。依頼の対象範囲が
  Python ファイルを含まないため直していない。次に使うときは
  `--toggle` オプションで明示的に指定するか、別途直す必要がある
- `my.css` の役割クラスの命名は、既存の `my-*` 命名（`my-sde-*` /
  `my-date-*` / `my-menu-*` など）に合わせて付けたが、命名の一貫性は
  reviewer 的な視点でもう一段確認する価値があるかもしれない
  （今回の依頼には reviewer が付いていないため、この点は verifier の
  確認に委ねる）
