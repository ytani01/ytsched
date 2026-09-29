# TODO-206. POST に CSRF 対策を入れる（xsrf_cookies）

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | implementer（Sonnet 5.5 / medium）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |
| 実施 | Sonnet 5.5 / 記載なし | implementer（Sonnet 5.5 / medium）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |

| 担当 | モデル | effort | input | output | cache_creation | cache_read | 割合 |
|------|--------|--------|-------|--------|----------------|------------|------|
| main | Sonnet 5.5 | 記載なし | 52 | 9,993 | 69,732 | 1,638,749 | 56% |
| implementer | Sonnet 5.5 | medium | 28 | 278 | 42,671 | 433,665 | 16% |
| reviewer | Opus 5.5 | high | 30 | 2,296 | 52,650 | 494,223 | 18% |
| verifier | Sonnet 5.5 | medium | 24 | 206 | 53,325 | 244,121 | 10% |
| 合計 |  |  | 134 | 12,773 | 218,378 | 2,810,758 | 計 3,042,043 |

- main は利用者が `/model` で Sonnet 5.5 に切り替えていた（見込みは Opus 5.5）。
  effort は記録に残らないので「記載なし」
- 集計は `--since '2026-09-30 04:49:00'`（`/clear` 直後）。決着の作業（この
  ファイルの作成など）の分は含まない。サブエージェントの分は少なめに出る

## きっかけ

POST にトークンが無く、リバースプロキシが Basic 認証だと、ブラウザは他の
サイトから送らせた POST にも認証情報を付ける。外のページから予定の削除や
ゴミ箱の全消去ができた。

## やったこと

- `webapp.py`: `xsrf_cookies=True`、`xsrf_cookie_kwargs={"expires_days": 365}`
- テンプレートの POST フォーム 6 つ（`main.html` 3、`edit.html` 1、
  `trash.html` 2）に `{% module xsrf_form_html() %}`
- `nav.js` の `doPost()` が `_xsrf` cookie を読んで hidden に足す
  （`doSubmit()` は既存フォームを送るだけなので、フォーム側の hidden で足りる）
- `handler.py` の `ERROR_MESSAGES` に 403 を足し、TODO-204 の 409 と同じ画面で
  出す。`src` で 403 を出すのは xsrf の検査だけ
- テスト: `WebTestBase.fetch()` が POST のときだけ GET で cookie を取り、
  cookie と本文に付ける（テスト専用に切る設定は作っていない）。
  `TestXsrf`（トークン無しが 403、hidden の数）と、本番の `WebServer` の設定を
  見る `test_xsrf_settings` を足した
- `src/README.md` に 403 と xsrf を追記

**403 の文言を、決めていたものから変えた。** 決めていたのは「読み込み直して
ください」だが、403 の画面は POST の応答なので、F5 で読み込み直すと古い
トークンが再送されてまた 403 になる（reviewer の指摘）。「画面が古くなって
います。一覧へ戻って、もう一度操作してください。」にした。利用者に事後で
確認し、了承を得た（2026-09-30）。

## 確かめたこと

- `mise run fmt` / `typecheck` / `lint` / `test`: 706 件通過（ブラウザテスト含む）
- 壊すと落ちるか（verifier が 1 回ずつ壊して戻した）:
  `xsrf_cookies` を消す、`expires_days` を 30 にする → `test_xsrf_settings`。
  `todo_days_form` の hidden を消す → `test_forms_have_xsrf_hidden`。
  `nav.js` の `_xsrf` を足す処理を消す → `test_browser.py`
- 実起動: cookie の期限が 365 日先、トークン付き POST が 302、トークン無しが
  403 で上の文言が出る
- reviewer: POST の経路の漏れは無し（`fetch(`・XHR も無い）。cookie の path は
  `/` なので `url_prefix` によらず読める

## 残ること

- `_xsrf` cookie の期限は初回発行から 365 日で、延びない（tornado は cookie が
  あると出し直さない）。1 年後に古いタブから送ると 403 になる。想定内と読んだ
- 実起動の確認で implementer が起動したサーバ（port 10197）が残っていた。
  kill が権限で止められたため、利用者が止める

## 分担の振り返り

- **implementer**: 実装は 1 回で通り、reviewer の指摘は設定の重複、403 の文言、
  テストの穴だけで、実装の作り直しは無かった。`make_app()` が本番と別に
  `Application` を作っていることに気づいて同じ設定を足したが、本番側を
  外して落ちるテストまでは考えていなかった（reviewer が見つけた）
- **reviewer**: テストが本番の設定を見ていないこと、403 の文言が実際の動きと
  合わないことを見つけた。どちらも動かして確かめるだけでは出ない指摘
- **verifier**: 壊す確認 4 つがすべて落ちることを確かめた。見つけた食い違いは無い
- **見込みとの差**: main が Opus 5.5 でなく Sonnet 5.5 だった。指摘の内容は
  分担どおりの reviewer（Opus）で出ており、main を下げても品質は落ちなかった
- **次に同じ規模なら**: 同じ組み方でよい。implementer への依頼に「設定が
  テスト用と本番の 2 か所にあるなら、本番を外して落ちるテストも足す」と
  「エラー画面の文言は、その画面で利用者が取れる操作で成り立つか確かめる」を
  書いておくと、reviewer の指摘 2 件を先に潰せる
