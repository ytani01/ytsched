# TODO-084 writer 報告

## 直したファイル

- `src/README.md`
  - `HandlerBase` の項:「`LoadMonths` を除いて」を「`LoadMonths` と
    `AutoTurnMsec` を除いて」に直した
  - `MainHandler` の項に `AutoTurnMsec`（既定 700、範囲 300〜10000）を
    足し、`get_load_months()`/`get_auto_turn_msec()` が共通の
    `get_conf_int()` を使うことに触れた
  - 「週の移動（ブラウザ側）」に「フッターの ◀▶ とダブルタップ
    （TODO-084）」の節を新設。`window` への委譲の理由、ダブルタップの
    窓（350msec）、止まる 4 条件、ボタン上のスワイプを拾わない仕組みを
    書いた。Mermaid の図・`static/js/` 8 本の記述は変えていない
- `tests/README.md`
  - `test_web.py` の項に `AutoTurnMsec` のテストを 1 行足した
  - `test_browser.py` の項に、足した 3 本（ダブルタップで自動送り開始・
    次のタップで停止・ボタン上の横払いでは動かない）を 1 行足した
- `archives/todo/TODO-084. フッターの ◀▶ をダブルタップして自動ページ送り.md`
  （新規）。骨格は「きっかけ / やったこと / テスト」＋
  reviewer の確認結果。見込みの行はそのまま残し、実施の行を足した。
  消費の行は空欄のまま残した（main が後で書く前提）
- `TODO.md`
  - TODO-084 の節を削除
  - 「残っている項目」から TODO-084 を外し、85 件→86 件に直した
  - 「完了済み」の目次の先頭に TODO-084 を足した

## 実物を確かめた方法

`git diff --stat` と `git diff` で 6 ファイルの変更を全部読んだ
（`main_handler.py`・`main-page.js`・`swipe.js`・`main.html`）。
`implementer-report.md`・`verifier-report.md`・`reviewer-report.md`・
`wording-report.md`・`request-implementer.md` を読んだ。`src/README.md`・
`tests/README.md` は既存の記述を `grep`/`Read` で確認してから編集した。
コード・テンプレート・テストは触っていない。

## 判断が要る点

- 消費の行の数字（`archives/todo/TODO-084…md` の表）は集計していない。
  main が `tools/token-usage.py` で埋める前提
- リンクの日本語ファイル名（◀▶ を含む）は、既存の `archives/todo/` の
  リンクに倣ってスペースだけ `%20` にし、他の文字はそのまま書いた
  （このリポジトリに ◀▶ を含むファイル名の前例が無いため、既存の
  日本語ファイル名リンクの書き方に揃えた）
