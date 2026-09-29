# TODO-206 reviewer への依頼

## 対象
`git diff`（未コミット）。仕様は `TODO.md` の TODO-206 の節。実装の報告は
`archives/agents/TODO-206/implementer-report.md`。

## 見てほしいこと（コードは直さない。境界線上の判断は報告だけ）
1. **漏れ**: POST になる経路にトークンが載っているか。
   `rg -n '<form|doPost|doSubmit|\.submit\(|fetch\(|method' src/ytsched/webroot`
   を全部辿り、POST するのに `_xsrf` が付かない経路が無いか。`doSubmit()` が
   送るフォームが、どのテンプレートのどのフォームか、そこに hidden があるか
2. `nav.js` の cookie 読み取りの正しさ（cookie 名、`url_prefix` があるときの
   path、値の decode、cookie が無いときの動き）
3. `handler.py` の 403 の文言・`write_error()` が xsrf 以外の 403 に対して不適切に
   ならないか。403 のとき `write_error` の `self._app_info` などが使えるか
   （xsrf 検査は `prepare` 前後のどこで走るか。`initialize()` は済んでいるか）
4. `tests/helpers.py` の `make_app()` と `webapp.py` の設定が食い違う余地
   （設定が 2 か所にある問題）。
5. テストの強さ: `WebTestBase.fetch()` の上書きが、トークン検査そのものを
   素通りさせていないか（cookie と本文の両方を本当に送っているか）。
   `TestXsrf` は、本番の設定を外したら落ちるか（コードを読んで判断。
   実際に壊す確認は verifier が行う）
6. `expires_days=365` が実際に cookie に付くか（tornado の該当版のソースで確認）

## 報告
`archives/agents/TODO-206/reviewer-report.md` に 60 行以内。指摘は
重大度順、「実害は未確認」と添える。返事は「終わったか・報告ファイル・判断が
要る点」だけ。コミットしない。
