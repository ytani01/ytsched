# TODO-206 implementer への依頼

## 目的
POST に CSRF 対策（tornado の `xsrf_cookies`）を入れる。`TODO.md` の TODO-206 の
節が仕様。先にそこを読むこと。

## 変更すること
1. `src/ytsched/webapp.py` の `tornado.web.Application(...)` に
   `xsrf_cookies=True` と `xsrf_cookie_kwargs={"expires_days": 365}` を渡す
2. フォーム（`rg -n '<form' src/ytsched/webroot/templates`）のうち
   **`method="POST"` になるもの**に `{% module xsrf_form_html() %}` を入れる。
   `main.html` の検索・フィルタ・ToDo 日数のフォームは、メソッドと JS の
   送り方を読んで、POST になるものだけ入れる
3. `src/ytsched/webroot/static/js/nav.js` の `doPost()`、および `doSubmit()` など
   フォームを POST する JS に、`_xsrf` を hidden で足す。トークンの取り方は
   `_xsrf` cookie を読む（または base.html に meta で出す）のうち小さい方
4. トークンが合わず 403 になったときは、`src/ytsched/handler.py` の
   `ERROR_MESSAGES`（TODO-204 の 409 と同じ作り）に 403 を足し、
   「画面が古くなっています。読み込み直してください。」の趣旨の文を出す。
   **この文は 403 全般に出るので、文言は xsrf に限らない言い方にするか、
   `rg -n '403' src` で xsrf 以外に 403 を出す所が無いことを確かめる**
5. テスト: `tests/test_web.py` の `WebTestBase` に、POST のときだけ GET で
   `_xsrf` cookie を取って cookie とフォーム本文の両方へ付ける仕組みを 1 か所
   作り、既存の POST テスト（`rg -n 'method="POST"' tests`）を通す。
   **テスト専用に xsrf を切る設定は作らない。**
   足すテスト: (a) トークン無しの POST が 403 で、応答に「読み込み直して」の
   文が出る (b) 正しいトークンの POST が通る（既存テストで足りる）
   (c) `edit.html`・`trash.html` の 3 つのフォームに `_xsrf` の hidden が出る
6. `tests/test_browser.py`（Playwright）は実サーバに対して操作するので、
   フォームや JS が正しければそのまま通るはず。通らなければ原因を報告する
7. 文書: `rg -n 'POST' src/README.md docs/*.md README.md` で CSRF に触れる
   ところがあれば揃える。無ければ `src/README.md` に 2〜3 行足す

## 保つもの・変えないもの
- データ形式、URL、`_xsrf` 以外のパラメータ名は変えない
- `mise run upgradeproject` は走らせない

## 完了条件・確かめ方
- `mise run fmt` / `typecheck` / `lint` / `test` が通る（ブラウザテスト含む）
- 実際に起動して確かめる: `--datadir` に一時ディレクトリを指定して起動し、
  `curl -X POST` でトークン無しが 403、cookie とトークン付きが通ることを
  出力つきで報告する

## 報告
`archives/agents/TODO-206/implementer-report.md` に 60 行以内。変更点、
確かめた結果（実際の出力）、判断した点、残る懸念。返事は
「終わったか・報告ファイルのパス・判断が要る点」だけ。コミットしない。
