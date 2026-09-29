# TODO-206 reviewer 報告

対象は未コミットの `git diff`。tornado は 6.5.10（`.venv` のソースで確認）。
どれも実害は未確認。

## 指摘（重大度順）

1. **本番の設定を外しても、落ちるテストが無い**（`src/ytsched/webapp.py:114-115`、
   `tests/helpers.py:80-81`）。`TestXsrf` は `make_app()` の設定しか見ない。
   ブラウザテストは実サーバーを起動するが、`xsrf_cookies` が無くても
   `xsrf_form_html()` は hidden を出し、POST は通るので落ちない。
   `webapp.py` から 2 行を消す・`expires_days` を変える、のどちらも
   テストでは捕まらない。ルートの一覧が 2 か所にあるのは前からだが、
   今回は安全のための設定が片方だけで効いている形になる。設定を
   `webapp.py` の定数に出して `make_app()` から使う、または `WebServer` の
   `_app.settings` を見るテストを足す、のどちらかが要るか（main の判断）
2. **403 の画面で「読み込み直す」と、直らない**（`handler.py:96`、
   `error.html`）。403 の画面は POST の応答なので、F5 は同じ本文（古い
   `_xsrf`）を再送して、また 403 になる。`check_xsrf_cookie()` は
   `_get_raw_xsrf_token()` しか呼ばず、`error.html` も `xsrf_token` に
   触れないので、403 の応答は cookie を出し直さない。直るのは「一覧へ戻る」
   を押したとき（GET の `main.html` が cookie を出す）だけ。文言は利用者が
   決めたもの（TODO.md）なので、「一覧から開き直して」の 409 と揃えるかは
   利用者に聞く点
3. **`main.html` の 3 つのフォームの hidden を見るテストが無い**
   （`test_web.py` `test_forms_have_xsrf_hidden`）。docstring どおり edit・
   trash だけ。ブラウザテストが `form_search` を直接 submit するので検索は
   間接に守られるが、`todo_days_form`・`form_filter` から hidden を消しても
   落ちるテストは見当たらない（`rg` で探した範囲）

## 確かめて問題が無かったもの（1 行ずつ）

- POST の経路: `<form method=POST>` 6 個すべてに hidden あり。`doSubmit()` が
  送るのは `main.html` の `form_search`・`todo_days_form`・`form_filter`、
  `edit-page.js` の `submitCmd()` は `input_form`。`doPost()` 5 か所は cookie から
  付く。`fetch(`・XHR は無い
- `nav.js`: 正規表現は `document.cookie` の `a=b; c=d` 形式に合う。v2 トークン
  （`2|hex|hex|数字`）は Morsel の許可文字だけなので引用符で囲まれない。
  `decodeURIComponent` は恒等で害なし。cookie の path は `set_cookie()` の既定
  `/` なので `url_prefix` によらず読める。cookie が無いと付けずに送り 403
- xsrf 検査は `_execute()` の中で `prepare()` の直前。`initialize()` は
  `__init__` で済んでいるので `write_error()` の `self._app_info` は使える。
  `src/` に 403 を出す所は他に無く、`StaticFileHandler` は `HandlerBase`
  を継がないので影響なし
- `expires_days=365`: `xsrf_token` が `set_cookie(..., **cookie_kwargs)` に
  渡し、`set_cookie()` が `expires` に直す。ただし cookie が既にあると
  出し直さない（`if version is None`）ので、期限は初回発行から 365 日で
  延びない。1 年後に古いタブから送ると 403 になるが、TODO の想定内と読んだ
- `WebTestBase.fetch()`: cookie ヘッダーと本文の両方に同じトークンを付けて
  いる。本文はどれも `urlencode()` の文字列なので連結で壊れない

## 確信度の低いもの

- テストの `fetch()` は POST のたびに一覧を GET する。GET は今日の週を
  `SchedData` のキャッシュへ読み、`conf.json` を書くので、POST だけの
  テストの前提が少し変わる。tornado の v1 形式は任意の文字列を受ける
  （`_decode_xsrf_token()` の else 側）ので、cookie と本文に固定の値
  （例 `_xsrf=x`）を送れば GET は要らない
- `TestXsrf` の 403 は「トークン無し」の分岐だけで、古いタブで起きる
  「cookie と本文が合わない」分岐は見ていない（tornado の中なので必須ではない）
- 同じホストの `/` に `_xsrf` cookie を使う別の tornado アプリがあると、
  cookie を上書きし合って 403 になる。配置しだいなので確かめていない
