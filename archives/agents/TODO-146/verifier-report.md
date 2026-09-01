# TODO-146 verifier 報告

## 1. `mise run test`

```
mise run test
```

`fmt`（1 file reformatted — `my.css` の整形のみ、内容変更なし）
`typecheck` `lint` `test` すべて通過。`test` は 589 件全通過
（154.74s）。`test_browser.py` を含む。

## 2. テンプレート 7 枚の Bootstrap 由来クラス

`class="..."` を grep して `container-fluid` `row` `col-*` `p-*` `m-*`
`text-*` `fw-bold` `align-*` `border` `d-none` `fixed-*` `alert*` を
検索したところ、`my-align-middle` / `my-align-bottom`（意図して残した
修飾クラス。TODO.md・implementer 報告に理由が書いてある）以外に
一致無し。`{% set %}` で組み立てる `class_bg` `class_canceled`
`class_important` `class_today` `class_date_block` `tr_class`
`td_class` の中身も grep して確認、すべて `my-` 接頭辞。○

## 3. `my.css` とテンプレートの突き合わせ

`my.css` の `.my-*` セレクタ 167 個と、テンプレート側で使っている
クラス（静的な `class="..."`、`{% set %}` で組み立てる値、JS からの
参照）を突き合わせた。差分に見えたものは以下、すべて実際には対応が
取れている（抽出スクリプトの誤検出）。

- `my-wday-0`〜`6`：`main.html:192` で `my-wday-{{ weekday }}` として
  動的生成。○
- `my-sde-todo-near` / `-over`：`sde.html` で `'my-sde-todo-' + _urgency`
  として動的生成。○
- `my-edit-row`：`my.css:1182` のコメント中の言及のみで、実クラスでは
  ない（意図通り、行ごとに個別クラスへ分けたので存在しない）。○
- 他（`my-btn-disabled` `my-mini-cal-*` `my-week-cur` 等）は
  grep の対象を templates/*.html + static/js まで広げたら見つかった
  （最初の抽出漏れ）。○

両方向で不整合は無し。

## 4. アプリの起動と画面操作

`--datadir` に一時ディレクトリを指定して起動（実データ未使用）。
テストデータ（通常予定・重要・キャンセル・ToDo 近い/超過・ゴミ箱 2 件）
を書き込み、playwright で以下を確認（幅 412px・800px 両方）。

- 週間表示: 上の週バー・ゲージ・下のメニューバー、位置とも正常。○
- ハンバーガーメニュー開閉: `label[for='menu-sw']` クリックで開閉。
  バージョン表示・ゴミ箱件数・フィルタ列が正しく現れ、`d-none` の
  `!important` を外した影響で崩れる様子は無い。○
- 予定の詳細開閉（`my-longtext-sw`）: 開くと本文が折り返され、
  閉じると 1 行省略表示に戻る。矢印アイコンの向きも連動。○
- 編集画面（新規 `edit?date=...`、既存 `data-action="edit-sde"` 経由）:
  下のボタン帯が中央に並ぶ。既存編集では複製アイコンも表示。○
- ゴミ箱（2 件）: ヘッダー・チェックボックス・復元/削除アイコン、
  レイアウト正常。○（0 件は今回のデータでは未確認。TODO-145 で
  別途確認済みのはず）
- 月間表示・ミニカレンダー切り替え: ミニカレンダーの見出しクリックで
  6 か月分の月間表示に切り替わる。○
- 検索、不正な正規表現: `(` を入れて Enter → 旧 `alert-danger` 相当の
  `my-error-box`（赤背景・中央寄せ）が表示される。○

## 5. 画面の目視

`mise run shot -p todo146`、`--open`（`DEF_TOGGLE` が
`input.my-longtext-sw` に直っていることも確認）で撮影。
上記の操作を playwright で個別に撮った画像も含め、見た目のおかしい点は
無し。チャットに添付、`~/tmp/playwright-mcp/todo146_*.png` に保存。

## 6. ログ

サーバログに例外・トレースバックは無し。出ているのは想定通りの
`PatternError`（不正な正規表現。`WARNING` で処理済み）のみ。
検証中に自分が誤ったパス（`/ytsched/edit/2026-09-10`）へ curl した分の
404 が数件あるが、アプリ側の不具合ではない（正しい経路は
`/ytsched/edit?date=...`）。

## 見つけたこと

無し。

## 残る懸念

- implementer 報告にある「命名の一貫性は reviewer 的な視点でもう一段
  確認する価値があるかもしれない」は、今回の依頼（見た目・挙動を
  変えていないかの確認）の範囲外なので確認していない。判断は main へ。
- ゴミ箱 0 件の状態（TODO-145 の対象）は今回作ったデータでは再現して
  いない。TODO-145 側で確認済みであれば問題無し。
