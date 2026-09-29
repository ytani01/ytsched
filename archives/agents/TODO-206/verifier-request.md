# TODO-206 verifier への依頼

対象は未コミットの `git diff`。仕様は `TODO.md` の TODO-206 の節。
コードは直さない。境界線上の判断は報告だけ（「実害は未確認」と添える）。

## 確かめること
1. `mise run fmt` / `typecheck` / `lint` / `test` が通る（ブラウザテスト含む）。
   件数を報告する
2. **壊すと落ちるか**（各 1 回。壊したら必ず元に戻し、`git diff --stat` が
   壊す前と同じことを確かめる）:
   a. `src/ytsched/webapp.py` の `xsrf_cookies=True` を消す → 落ちるテストの名前
   b. `xsrf_cookie_kwargs` の `expires_days` を 30 にする → 同上
   c. `main.html` の `todo_days_form` から `xsrf_form_html` を消す → 同上
   d. `nav.js` の `doPost()` の `_xsrf` を足す 6 行を消す → 同上
      （落ちるのはブラウザテストのはず。落ちなければ報告）
3. 実起動（`--datadir` は一時ディレクトリ、空きポート）で、curl の cookie jar
   を使って: 一覧 GET → cookie の `Expires` が約 1 年先 → トークン付き POST が
   302 → トークン無し POST が 403 でメッセージが出る。出力を貼る

## 報告
`archives/agents/TODO-206/verifier-report.md` に 60 行以内。一致したものは
1 行、食い違いだけ詳しく。返事は「終わったか・報告ファイル・判断が要る点」だけ。
コミットしない。
