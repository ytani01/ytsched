# TODO-016. `date` が空の POST と、存在しない `sde_id` の扱い

見込み: main = Opus 5 / effort medium、担当 = implementer + verifier
実施: main = Opus 5 / effort medium、担当 = implementer + verifier

分担の理由と各担当の報告は
[archives/agents/TODO-016/](../agents/TODO-016/README.md) にある。

## きっかけ

TODO-006（型ヒントの整備）の reviewer の指摘 1-1 と 2-2 から。
どちらも TODO-006 より前からある挙動。

- `date` を空にして、ToDo ではない予定を `cmd=add` で POST すると、
  `cmd_add()` が `add_sde(None, sde)` を呼ぶため、**予定が `ToDo.cgi` に
  書かれる**。`edit.html` の日付欄は必ず埋まるが、`type="date"` の入力は
  手で空にできるので到達する
- `edit_handler.py` の `sdf.get_sde(sde_id)` は、存在しない `sde_id` を
  渡されると `None` を返し、`edit.html` の `sde.date` で落ちる

TODO-006 で `get_sde()` の戻り値が `SchedDataEnt | None` になった際、
`main_handler.py` の guard で失敗が黙って 200 で返るようになったため、
暫定で `warning` を 1 行足してあった。

## やったこと

- **`date` が空の非 ToDo は、今日の予定として保存する。**
  `main_handler.py` の `cmd_add()` で、非 ToDo の書き込み先を引数の
  `date` から `new_sde.date` へ変えた。`SchedDataEnt.__init__` が
  `date=None` を今日に補正しているので、書き込み先もそれに合わせる形
- **存在しない `sde_id` には 404 を返す。** `edit_handler.py` と
  `main_handler.py` の両方で、`get_sde()` が `None` なら
  `tornado.web.HTTPError(404)` を投げる。それまでは編集画面が 500、
  更新経路は黙って 200 と、ばらついていた
- **TODO-006 の暫定の `warning` を削除し、404 のメッセージにまとめた。**
  あわせて `todo_flag` の初期化と分岐をガード節の形に直した

`HTTPError` のメッセージだけは f-string をやめ、
`"sde not found: sde_id=%s", sde_id` と tornado の流儀にした。
tornado は `log_message % args` を `__str__()` で評価するため、
入力に `%` が混ざると f-string ではログ出力時に `ValueError` になる。

### 今回やらなかったこと

**`cmd=del` で存在しない `sde_id` を渡したときは、今も黙って 200 を返す。**
404 にするには `SchedData.del_sde()` に削除の成否を返させる必要があり、
データモデル側の API 変更になる。TODO-016 が指していたのは
`cmd not in ["del"]` のブロックなので、範囲を広げなかった。

`main_handler.py` 側の 404 は、1 つ目の修正を入れると
`add`/`fix`/`update` が必ず自分の書いた `sde` を読み直すことになるため、
実リクエストでは到達しない防御的なガードになっている。

## テスト

`tests/test_web.py` に 4 件足した（いずれも修正前のコードでは失敗する
ことを確かめてある）。

- `TestUpdate.test_add_without_date` — `date=""` の非 ToDo を `cmd=add` で
  POST し、`ToDo.cgi` が作られず今日のファイルに入ること
- `TestUpdate.test_update_sde_not_found` — 更新後に見つからない場合 404。
  上記のとおり実リクエストでは到達しないため、`SchedDataFile.get_sde` を
  mock している
- `TestEditHandler.test_get_unknown_sde_id` /
  `test_get_unknown_sde_id_todo` — 存在しない `sde_id` で 404

`mise run lint`（ruff / basedpyright / mypy）と `uv run pytest tests`
（178 passed）が通る。verifier が一時ディレクトリでアプリを起動し、
`date` 空の追加が当日のファイルに入ること、ToDo の追加が `ToDo.cgi` に
入ること（退行なし）、存在しない `sde_id` の編集画面が 404 になること、
一覧・追加・修正・削除が退行していないことを curl で確かめた。
