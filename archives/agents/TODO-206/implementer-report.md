# TODO-206 implementer 報告

終わった。fmt / typecheck / lint / test（705 件、ブラウザテスト含む）すべて通過。

## 変更
- `src/ytsched/webapp.py`: `xsrf_cookies=True`、`xsrf_cookie_kwargs={"expires_days": 365}`
- `src/ytsched/handler.py`: `ERROR_MESSAGES` に 403「画面が古くなっています。読み込み直してください。」
  （`rg -n 403 src` で xsrf 以外に 403 を出す所が無いことを確認。文言は 403 全般でも成り立つ）
- テンプレート: `main.html` の 3 フォーム（検索・ToDo 日数・フィルタ。すべて POST）、
  `edit.html` 1、`trash.html` 2 に `{% module xsrf_form_html() %}`
- `nav.js` `doPost()`: `_xsrf` cookie を読んで hidden に足す。`doSubmit()` は
  既存フォームを送るだけなので、フォーム側の hidden で足りる
- `tests/helpers.py` `make_app()`: 本番と同じ `xsrf_cookies` 設定を足した
  （テスト用の Application は `WebServer` と別に作られているため。切る設定ではない）
- `tests/test_web.py`: `WebTestBase.fetch()` を上書き。POST のときだけ GET で
  cookie を取り、cookie と本文へ付ける（`xsrf=False` で付けない）。
  `TestXsrf` を追加（トークン無し 403 と文言、edit 1 個・trash 2 個の hidden）。
  既存の POST テストは無修正で通る
- `src/README.md`: 403 と xsrf の 2〜3 行を追記。他の文書に CSRF に触れる所は無かった

## 実起動での確認（`--datadir` は一時ディレクトリ、port 10197）
```
GET 200                          (cookie 保存)
<p>画面が古くなっています。読み込み直してください。</p>
no-token POST 403
with-token POST 302              (cookie + _xsrf=... 付き。PRG のリダイレクト)
```

## 判断
- `fetch` の上書きは basedpyright の署名検査に合わせ `(path, raise_error=False, **kwargs)`
  にして、`xsrf` は kwargs から pop した。`.group(1)` に `# type: ignore[union-attr]` を付けた
  （mypy 用。basedpyright は通る）
- トークンは meta でなく cookie 読み取り（JS 6 行）

## 残る懸念
- `test_forms_have_xsrf_hidden` は、ゴミ箱に 1 件入れて trash の 2 フォームを見る
  （削除・復活）。壊すと落ちるかの確認（テンプレートから `xsrf_form_html` を消す）は
  してない。verifier に頼みたい
- 実ブラウザで doPost() 経由（検索語つき POST）が通るかは、test_browser.py の
  既存テストが通ったことのみ。個別には見ていない
