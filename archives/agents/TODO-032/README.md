# TODO-032 の分担

- 実装: `implementer` — 依頼書 `implementer-request.md`。
  **報告ファイルは無い**（下記）
- 確認: `verifier` — 依頼書 `verifier-request.md`、報告
  `verifier-report.md`
- レビュー: `reviewer` — 依頼書 `reviewer-request.md`、報告
  `reviewer-report.md`
- 実行: `runner` — 報告 `runner-report.md`
- 文書: `wording` — 報告 `wording-report.md`
  （項目を立てたときの分もこのディレクトリにある）

## この分担にした理由

**implementer を立てたのは、コード 2 本（`handler.py`・`migrate.py`）と
テスト 4 本、文書 3 本にまたがる規模だったから。**

**reviewer を入れたのは、設定の読み書きの分岐が変わるから**（壊れた
JSON をどう扱うか、旧形式のどこまでを引き継ぐか）。挙動や分岐が変わる
項目には入れる、という基準（TODO-017）に当たる。

**verifier を立てたのは、試せる手順があるから。** 移行ツールを実際に
走らせ、変換後のデータでアプリを起動して設定が効くかまで見られる。
テストでは見ていないところが主眼になる。

`.md` が複数入るコミットなので `wording` を立てた（TODO-025・TODO-026）。

## implementer が途中で終わった

`implementer` は **セッションの上限に当たって途中で終わった**
（「アプリを起動して確かめる」の直前）。コード・テスト・文書の変更は
一通り入っていたが、`implementer-report.md` は書かれていない。

main が作業ツリーの差分を読んで引き継ぎ、テスト・lint・型チェックが
通ることを確かめたうえで、確認とレビューを `verifier` と `reviewer` に
回した。**この 2 つは、実装者が止まったことを依頼書に書いたうえで
依頼している**（やり残しがある前提で見てもらうため）。

reviewer の指摘を受けた修正は、implementer を立て直さず **main が直した**
（docstring と文書が中心で、コードの変更は警告条件 1 か所と
`str()` の削除だけだったため）。修正後の lint とテストは `runner` に
走らせた。

## reviewer の指摘の採否

`reviewer-report.md` の 10 件について、main の判断。

直したもの:

- **1.** `docs/data-format.md` の「移行ツールの使い方」節が `Conf.cgi` の
  追加に追随していない → 直した（TODO-032 の「文書を直す」の範囲内）
- **2.** `conv_conf()` だけタブの無い行を `--error-file` に出さない →
  **出さない方針のまま、docstring と文書に明記した**。設定はアプリが
  書いたもので行数も数行なので、予定データと同じ扱いにする必要が薄い
- **3.** `load_conf()` の docstring が実装より広い →
  文言を狭めた（`PermissionError` などは捕まえない、と書いた）。
  TODO-032 は形式の変更だけなので、`except` は広げない
- **4.** `UnicodeDecodeError` の分岐にテストが無い → 足した
- **5.** `str(param)` が要らない → 消した。`isinstance` を通ったあとの
  型を変数で明示する形にした
- **6.** `Conf.cgi` しか無いディレクトリで「no target file」が出る →
  警告の条件に `Conf.cgi` の有無を足した
- **7.** 移行前にアプリを起動すると旧設定を取り込めなくなる →
  `docs/data-format.md` に「アプリを起動する前に移行する」を足した

直さなかったもの:

- **8.** 書き出しの書式（`ensure_ascii=False` / `indent=2` / 末尾の改行）が
  `handler.save_conf()` と `Migrator.migrate_conf()` の 2 か所にある →
  **そのままにした。** 両方に書式まで見るテストがある。「2 つが同じ
  書式であること」を見るテストを足しても、片方を意図的に変えたときに
  落ちるだけで、拾いたい間違いが増えるわけではない
- **9.** 壊れた JSON では設定が全部消える（旧形式は 1 行だけ飛ばせた）→
  **指摘ではないと判断した。** JSON にすると決めた時点で避けられず、
  設定は 4 つで画面から入れ直せる
- **10.** `migrate.py` のモジュール docstring が矛盾して見える →
  1 と同じ話なので、そちらと合わせて直した（「予定データの対象は」に
  限定した）
