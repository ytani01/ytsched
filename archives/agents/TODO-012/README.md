# TODO-012 の分担

不正な正規表現を入れられたときの扱い。

- `implementer` — `main_handler.py` の正規表現の扱いを変え、`main.html` に
  知らせを出し、`tests/test_web.py` にテストを足す
  （[報告](implementer-report.md)）
- `verifier` — `mise run lint` / `mise run test` と、実際の画面での確認
  （[報告](verifier-report.md)）

## この分担にした理由

`main_handler.py`・`main.html`・テストの 3 つにまたがり、検索モードの判定を
「文字列が空でないか」から「正規表現として使えるか」へ変えるため、
分岐の見落としが出やすい。実装を `implementer` に任せ、確認は別に `verifier`
へ分けた。`reviewer` は付けていない（変更の範囲が 1 ファイルの中の
決まった書き換えで、設計の判断は main が先に決めているため）。

## main が先に決めた設計

- `re.compile()` を `get()` の中で 1 回だけ行い、ループの中の `try` /
  `except re.error` は無くす
- 不正なら、その条件は**無視して全件を出す**（今の `continue` は捨てる）
- 入力欄には元の文字列を残す（直せなくなるため）。`Conf.cgi` への保存も
  今までどおり。マッチに使うかどうかだけを分ける
- `search_str` が不正なときは、検索モード（日付範囲の変更・年の見出し）にも
  入らない。テンプレートの `{% if search_str %}` のうち、**検索モードの
  判定に使っているところ**を別の変数に変える
